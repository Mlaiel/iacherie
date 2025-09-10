"""Intelligent Rate Limiting System
==================================

Global rate limiting system for all API integrations with intelligent algorithms,
burst handling, and provider-specific limits.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import redis.asyncio as redis
from collections import defaultdict, deque


class RateLimitType(Enum):
    """Rate limit types"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    name: str
    limit: int  # Number of requests
    window: int  # Time window in seconds
    type: RateLimitType = RateLimitType.SLIDING_WINDOW
    burst_limit: Optional[int] = None  # Allow burst requests
    priority: int = 1  # Higher priority = checked first
    enabled: bool = True


@dataclass
class RateLimitStatus:
    """Current rate limit status"""
    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    current_usage: int = 0


class RateLimiter:
    """Intelligent rate limiting system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None, 
                 use_memory_fallback: bool = True):
        """Initialize rate limiter
        
        Args:
            redis_client: Redis client for distributed rate limiting
            use_memory_fallback: Use in-memory storage if Redis unavailable
        """
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis_client
        self.use_memory_fallback = use_memory_fallback
        
        # In-memory storage for fallback
        self.memory_storage = defaultdict(deque)
        self.token_buckets = {}  # For token bucket algorithm
        
        # Rate limit rules
        self.rules: Dict[str, List[RateLimitRule]] = defaultdict(list)
        self.global_rules: List[RateLimitRule] = []
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "denied_requests": 0,
            "provider_stats": defaultdict(lambda: {"requests": 0, "denied": 0})
        }
        
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default rate limiting rules for common providers"""
        
        # Twitter API v2 rate limits
        twitter_rules = [
            RateLimitRule("tweets_per_user", 300, 900),  # 300 per 15 min
            RateLimitRule("tweets_per_app", 300, 900),   # 300 per 15 min
            RateLimitRule("media_upload", 25, 900),      # 25 per 15 min
        ]
        self.rules["twitter"] = twitter_rules
        
        # Instagram API rate limits
        instagram_rules = [
            RateLimitRule("basic_display", 200, 3600),   # 200 per hour
            RateLimitRule("graph_api", 200, 3600),       # 200 per hour
            RateLimitRule("media_publish", 25, 3600),    # 25 per hour
        ]
        self.rules["instagram"] = instagram_rules
        
        # YouTube API rate limits
        youtube_rules = [
            RateLimitRule("quota_units", 10000, 86400),  # 10,000 units per day
            RateLimitRule("uploads", 6, 86400),          # 6 uploads per day
            RateLimitRule("comments", 100, 86400),       # 100 comments per day
        ]
        self.rules["youtube"] = youtube_rules
        
        # TikTok API rate limits
        tiktok_rules = [
            RateLimitRule("user_info", 100, 86400),      # 100 per day
            RateLimitRule("video_list", 1000, 86400),    # 1,000 per day
            RateLimitRule("video_upload", 10, 86400),    # 10 per day
        ]
        self.rules["tiktok"] = tiktok_rules
        
        # Facebook Graph API rate limits
        facebook_rules = [
            RateLimitRule("app_rate_limit", 200, 3600),  # 200 per hour
            RateLimitRule("page_rate_limit", 600, 3600), # 600 per hour
            RateLimitRule("ad_api", 100, 3600),          # 100 per hour
        ]
        self.rules["facebook"] = facebook_rules
        
        # Spotify API rate limits
        spotify_rules = [
            RateLimitRule("web_api", 100, 60),           # 100 per minute
            RateLimitRule("playlist_modify", 1, 1),      # 1 per second
        ]
        self.rules["spotify"] = spotify_rules
        
        # LinkedIn API rate limits
        linkedin_rules = [
            RateLimitRule("profile_api", 500, 86400),    # 500 per day
            RateLimitRule("share_api", 100, 86400),      # 100 per day
        ]
        self.rules["linkedin"] = linkedin_rules
        
        # OpenAI API rate limits (example tiers)
        openai_rules = [
            RateLimitRule("gpt4_tokens", 10000, 60),     # 10k tokens per minute
            RateLimitRule("gpt4_requests", 500, 60),     # 500 requests per minute
            RateLimitRule("dalle_requests", 50, 60),     # 50 images per minute
        ]
        self.rules["openai"] = openai_rules
        
        # Anthropic Claude API rate limits
        anthropic_rules = [
            RateLimitRule("claude_requests", 1000, 60),  # 1k requests per minute
            RateLimitRule("claude_tokens", 100000, 60),  # 100k tokens per minute
        ]
        self.rules["anthropic"] = anthropic_rules
        
        # Global rate limits
        self.global_rules = [
            RateLimitRule("global_burst", 1000, 60),     # 1000 requests per minute globally
            RateLimitRule("global_daily", 100000, 86400) # 100k requests per day globally
        ]
    
    def add_rule(self, provider: str, rule: RateLimitRule):
        """Add rate limiting rule for provider
        
        Args:
            provider: Provider name
            rule: Rate limit rule
        """
        self.rules[provider].append(rule)
        # Sort by priority (higher first)
        self.rules[provider].sort(key=lambda r: r.priority, reverse=True)
        
        self.logger.info(f"Added rate limit rule for {provider}: {rule.name}")
    
    def add_global_rule(self, rule: RateLimitRule):
        """Add global rate limiting rule
        
        Args:
            rule: Rate limit rule
        """
        self.global_rules.append(rule)
        self.global_rules.sort(key=lambda r: r.priority, reverse=True)
        
        self.logger.info(f"Added global rate limit rule: {rule.name}")
    
    async def allow_request(self, provider: str, user_id: Optional[str] = None, 
                          rule_name: Optional[str] = None, cost: int = 1) -> bool:
        """Check if request is allowed under rate limits
        
        Args:
            provider: Provider name
            user_id: User identifier
            rule_name: Specific rule to check
            cost: Request cost (for token bucket)
            
        Returns:
            bool: Whether request is allowed
        """
        try:
            # Update statistics
            self.stats["total_requests"] += 1
            self.stats["provider_stats"][provider]["requests"] += 1
            
            # Check global rules first
            for rule in self.global_rules:
                if not rule.enabled:
                    continue
                    
                key = f"global:{rule.name}"
                if not await self._check_rule(key, rule, cost):
                    self.stats["denied_requests"] += 1
                    self.stats["provider_stats"][provider]["denied"] += 1
                    self.logger.warning(f"Request denied by global rule: {rule.name}")
                    return False
            
            # Check provider-specific rules
            provider_rules = self.rules.get(provider, [])
            for rule in provider_rules:
                if not rule.enabled:
                    continue
                    
                # If specific rule requested, only check that one
                if rule_name and rule.name != rule_name:
                    continue
                
                # Build rate limit key
                key_parts = [provider, rule.name]
                if user_id:
                    key_parts.append(user_id)
                key = ":".join(key_parts)
                
                if not await self._check_rule(key, rule, cost):
                    self.stats["denied_requests"] += 1
                    self.stats["provider_stats"][provider]["denied"] += 1
                    self.logger.warning(f"Request denied by rule: {provider}:{rule.name}")
                    return False
            
            # All checks passed
            self.stats["allowed_requests"] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check error: {e}")
            # Fail open - allow request on error
            return True
    
    async def _check_rule(self, key: str, rule: RateLimitRule, cost: int = 1) -> bool:
        """Check specific rate limit rule
        
        Args:
            key: Rate limit key
            rule: Rate limit rule
            cost: Request cost
            
        Returns:
            bool: Whether request is allowed
        """
        if rule.type == RateLimitType.SLIDING_WINDOW:
            return await self._check_sliding_window(key, rule)
        elif rule.type == RateLimitType.FIXED_WINDOW:
            return await self._check_fixed_window(key, rule)
        elif rule.type == RateLimitType.TOKEN_BUCKET:
            return await self._check_token_bucket(key, rule, cost)
        elif rule.type == RateLimitType.LEAKY_BUCKET:
            return await self._check_leaky_bucket(key, rule, cost)
        else:
            return True
    
    async def _check_sliding_window(self, key: str, rule: RateLimitRule) -> bool:
        """Check sliding window rate limit
        
        Args:
            key: Rate limit key
            rule: Rate limit rule
            
        Returns:
            bool: Whether request is allowed
        """
        now = time.time()
        window_start = now - rule.window
        
        if self.redis_client and not self.redis_client.connection_pool.connection_kwargs.get('host') == 'localhost':
            try:
                # Use Redis for distributed rate limiting
                pipe = self.redis_client.pipeline()
                
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Count current entries
                pipe.zcard(key)
                
                # Add current request
                pipe.zadd(key, {str(now): now})
                
                # Set expiration
                pipe.expire(key, rule.window + 1)
                
                results = await pipe.execute()
                current_count = results[1]
                
                return current_count < rule.limit
                
            except Exception as e:
                self.logger.warning(f"Redis error, falling back to memory: {e}")
                if not self.use_memory_fallback:
                    return True
        
        # Memory fallback
        if key not in self.memory_storage:
            self.memory_storage[key] = deque()
        
        # Remove old entries
        timestamps = self.memory_storage[key]
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()
        
        # Check limit
        if len(timestamps) >= rule.limit:
            return False
        
        # Add current request
        timestamps.append(now)
        return True
    
    async def _check_fixed_window(self, key: str, rule: RateLimitRule) -> bool:
        """Check fixed window rate limit
        
        Args:
            key: Rate limit key
            rule: Rate limit rule
            
        Returns:
            bool: Whether request is allowed
        """
        now = time.time()
        window_start = int(now // rule.window) * rule.window
        window_key = f"{key}:{window_start}"
        
        if self.redis_client:
            try:
                # Get current count
                current = await self.redis_client.get(window_key)
                current_count = int(current) if current else 0
                
                if current_count >= rule.limit:
                    return False
                
                # Increment count
                pipe = self.redis_client.pipeline()
                pipe.incr(window_key)
                pipe.expire(window_key, rule.window + 1)
                await pipe.execute()
                
                return True
                
            except Exception as e:
                self.logger.warning(f"Redis error, falling back to memory: {e}")
                if not self.use_memory_fallback:
                    return True
        
        # Memory fallback
        if window_key not in self.memory_storage:
            self.memory_storage[window_key] = deque([0])
        
        current_count = self.memory_storage[window_key][0]
        if current_count >= rule.limit:
            return False
        
        self.memory_storage[window_key][0] = current_count + 1
        return True
    
    async def _check_token_bucket(self, key: str, rule: RateLimitRule, cost: int = 1) -> bool:
        """Check token bucket rate limit
        
        Args:
            key: Rate limit key
            rule: Rate limit rule
            cost: Token cost
            
        Returns:
            bool: Whether request is allowed
        """
        now = time.time()
        
        if key not in self.token_buckets:
            self.token_buckets[key] = {
                "tokens": rule.limit,
                "last_refill": now
            }
        
        bucket = self.token_buckets[key]
        
        # Calculate tokens to add based on time passed
        time_passed = now - bucket["last_refill"]
        tokens_to_add = (time_passed / rule.window) * rule.limit
        
        # Update bucket
        bucket["tokens"] = min(rule.limit, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if enough tokens
        if bucket["tokens"] >= cost:
            bucket["tokens"] -= cost
            return True
        
        return False
    
    async def _check_leaky_bucket(self, key: str, rule: RateLimitRule, cost: int = 1) -> bool:
        """Check leaky bucket rate limit
        
        Args:
            key: Rate limit key
            rule: Rate limit rule
            cost: Request cost
            
        Returns:
            bool: Whether request is allowed
        """
        now = time.time()
        
        if key not in self.memory_storage:
            self.memory_storage[key] = deque()
        
        bucket = self.memory_storage[key]
        
        # Leak requests (remove old ones)
        leak_rate = rule.limit / rule.window  # requests per second
        if bucket:
            last_leak = getattr(bucket, 'last_leak', now)
            time_passed = now - last_leak
            requests_to_leak = int(time_passed * leak_rate)
            
            for _ in range(min(requests_to_leak, len(bucket))):
                bucket.popleft()
            
            bucket.last_leak = now
        
        # Check capacity
        if len(bucket) + cost <= rule.limit:
            bucket.extend([now] * cost)
            return True
        
        return False
    
    async def get_rate_limit_status(self, provider: str, user_id: Optional[str] = None, 
                                  rule_name: Optional[str] = None) -> List[RateLimitStatus]:
        """Get current rate limit status
        
        Args:
            provider: Provider name
            user_id: User identifier
            rule_name: Specific rule name
            
        Returns:
            List[RateLimitStatus]: Rate limit statuses
        """
        statuses = []
        
        # Check provider rules
        provider_rules = self.rules.get(provider, [])
        for rule in provider_rules:
            if rule_name and rule.name != rule_name:
                continue
                
            key_parts = [provider, rule.name]
            if user_id:
                key_parts.append(user_id)
            key = ":".join(key_parts)
            
            status = await self._get_rule_status(key, rule)
            statuses.append(status)
        
        return statuses
    
    async def _get_rule_status(self, key: str, rule: RateLimitRule) -> RateLimitStatus:
        """Get status for specific rule
        
        Args:
            key: Rate limit key
            rule: Rate limit rule
            
        Returns:
            RateLimitStatus: Current status
        """
        now = time.time()
        
        if rule.type == RateLimitType.SLIDING_WINDOW:
            window_start = now - rule.window
            
            if self.redis_client:
                try:
                    count = await self.redis_client.zcount(key, window_start, now)
                    remaining = max(0, rule.limit - count)
                    reset_time = datetime.fromtimestamp(now + rule.window)
                    
                    return RateLimitStatus(
                        allowed=remaining > 0,
                        remaining=remaining,
                        reset_time=reset_time,
                        current_usage=count
                    )
                except Exception:
                    pass
            
            # Memory fallback
            if key in self.memory_storage:
                timestamps = self.memory_storage[key]
                # Count valid timestamps
                valid_count = sum(1 for t in timestamps if t >= window_start)
                remaining = max(0, rule.limit - valid_count)
                reset_time = datetime.fromtimestamp(now + rule.window)
                
                return RateLimitStatus(
                    allowed=remaining > 0,
                    remaining=remaining,
                    reset_time=reset_time,
                    current_usage=valid_count
                )
        
        elif rule.type == RateLimitType.TOKEN_BUCKET:
            if key in self.token_buckets:
                bucket = self.token_buckets[key]
                return RateLimitStatus(
                    allowed=bucket["tokens"] >= 1,
                    remaining=int(bucket["tokens"]),
                    reset_time=datetime.fromtimestamp(now + rule.window),
                    current_usage=rule.limit - int(bucket["tokens"])
                )
        
        # Default status
        return RateLimitStatus(
            allowed=True,
            remaining=rule.limit,
            reset_time=datetime.fromtimestamp(now + rule.window),
            current_usage=0
        )
    
    async def reset_rate_limit(self, provider: str, user_id: Optional[str] = None, 
                             rule_name: Optional[str] = None):
        """Reset rate limits for provider/user
        
        Args:
            provider: Provider name
            user_id: User identifier
            rule_name: Specific rule name
        """
        provider_rules = self.rules.get(provider, [])
        
        for rule in provider_rules:
            if rule_name and rule.name != rule_name:
                continue
                
            key_parts = [provider, rule.name]
            if user_id:
                key_parts.append(user_id)
            key = ":".join(key_parts)
            
            # Clear from storage
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except Exception:
                    pass
            
            if key in self.memory_storage:
                del self.memory_storage[key]
            
            if key in self.token_buckets:
                del self.token_buckets[key]
        
        self.logger.info(f"Reset rate limits for {provider}" + (f":{user_id}" if user_id else ""))
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics
        
        Returns:
            Dict[str, Any]: Statistics
        """
        stats = self.stats.copy()
        
        # Calculate success rate
        total = stats["total_requests"]
        if total > 0:
            stats["success_rate"] = stats["allowed_requests"] / total
            stats["denial_rate"] = stats["denied_requests"] / total
        else:
            stats["success_rate"] = 1.0
            stats["denial_rate"] = 0.0
        
        # Provider statistics
        for provider, provider_stats in stats["provider_stats"].items():
            requests = provider_stats["requests"]
            if requests > 0:
                provider_stats["denial_rate"] = provider_stats["denied"] / requests
            else:
                provider_stats["denial_rate"] = 0.0
        
        return stats
    
    async def get_current_usage(self, provider: str) -> Dict[str, Any]:
        """Get current usage for provider
        
        Args:
            provider: Provider name
            
        Returns:
            Dict[str, Any]: Current usage information
        """
        usage = {
            "provider": provider,
            "rules": []
        }
        
        provider_rules = self.rules.get(provider, [])
        for rule in provider_rules:
            key = f"{provider}:{rule.name}"
            status = await self._get_rule_status(key, rule)
            
            usage["rules"].append({
                "name": rule.name,
                "limit": rule.limit,
                "window": rule.window,
                "current_usage": status.current_usage,
                "remaining": status.remaining,
                "utilization": status.current_usage / rule.limit if rule.limit > 0 else 0
            })
        
        return usage
    
    async def optimize_rate_limits(self, provider: str):
        """Optimize rate limits based on usage patterns
        
        Args:
            provider: Provider name
        """
        usage = await self.get_current_usage(provider)
        
        for rule_usage in usage["rules"]:
            utilization = rule_usage["utilization"]
            
            # If consistently low usage, could increase burst limit
            if utilization < 0.3:
                rule_name = rule_usage["name"]
                for rule in self.rules[provider]:
                    if rule.name == rule_name and not rule.burst_limit:
                        rule.burst_limit = int(rule.limit * 1.5)
                        self.logger.info(f"Added burst limit to {provider}:{rule_name}")
            
            # If consistently high usage, log warning
            elif utilization > 0.9:
                self.logger.warning(f"High utilization for {provider}:{rule_usage['name']}")
    
    async def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old rate limiting data
        
        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff_time = time.time() - (max_age_hours * 3600)
        
        # Clean memory storage
        keys_to_remove = []
        for key, data in self.memory_storage.items():
            if isinstance(data, deque):
                # Remove old timestamps
                while data and data[0] < cutoff_time:
                    data.popleft()
                
                # Remove empty deques
                if not data:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_storage[key]
        
        # Clean token buckets
        bucket_keys_to_remove = []
        for key, bucket in self.token_buckets.items():
            if bucket.get("last_refill", 0) < cutoff_time:
                bucket_keys_to_remove.append(key)
        
        for key in bucket_keys_to_remove:
            del self.token_buckets[key]
        
        self.logger.info(f"Cleaned up {len(keys_to_remove)} old rate limit entries")


# Global rate limiter instance
rate_limiter = RateLimiter()


async def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance
    
    Returns:
        RateLimiter: Global instance
    """
    return rate_limiter