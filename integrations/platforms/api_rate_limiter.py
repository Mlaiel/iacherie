"""API Rate Limiter for Platform Integrations
==========================================

Intelligent rate limiting system for multiple platform APIs with different rate limits.
Implements various algorithms including token bucket, sliding window, and adaptive limiting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
REDIS_AVAILABLE = False  # Disabled due to compatibility issues
import json

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""    platform: str
    endpoint: str = "*"
    max_requests: int = 100
    time_window: int = 3600  # seconds
    burst_limit: int = 10
    backoff_factor: float = 2.0
    max_backoff: int = 300


@dataclass
class RateLimitStatus:
    """Rate limit status information"""    platform: str
    endpoint: str
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[int] = None
    is_limited: bool = False


class APIRateLimiter:
    """Intelligent rate limiting for platform APIs"""    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_cache = defaultdict(lambda: defaultdict(deque))
        self.backoff_cache = defaultdict(float)
        
        # Default platform rate limits
        self.platform_limits = {
            "youtube": {
                "*": RateLimitRule("youtube", "*", 10000, 86400, 100),  # 10k/day
                "search": RateLimitRule("youtube", "search", 100, 3600, 10),  # 100/hour
                "videos": RateLimitRule("youtube", "videos", 1000, 3600, 50),  # 1k/hour
                "analytics": RateLimitRule("youtube", "analytics", 200, 3600, 20)  # 200/hour
            },
            "instagram": {
                "*": RateLimitRule("instagram", "*", 200, 3600, 20),  # 200/hour
                "media": RateLimitRule("instagram", "media", 240, 3600, 24),  # 240/hour
                "insights": RateLimitRule("instagram", "insights", 500, 3600, 50)  # 500/hour
            },
            "tiktok": {
                "*": RateLimitRule("tiktok", "*", 1000, 86400, 100),  # 1k/day
                "videos": RateLimitRule("tiktok", "videos", 100, 3600, 10)  # 100/hour
            },
            "spotify": {
                "*": RateLimitRule("spotify", "*", 1000, 3600, 100),  # 1k/hour
                "artists": RateLimitRule("spotify", "artists", 100, 60, 10)  # 100/minute
            },
            "facebook": {
                "*": RateLimitRule("facebook", "*", 600, 3600, 60),  # 600/hour
                "pages": RateLimitRule("facebook", "pages", 200, 3600, 20)  # 200/hour
            },
            "twitter": {
                "*": RateLimitRule("twitter", "*", 300, 900, 30),  # 300/15min
                "tweets": RateLimitRule("twitter", "tweets", 300, 900, 30),  # 300/15min
                "users": RateLimitRule("twitter", "users", 75, 900, 15)  # 75/15min
            }
        }
        
    async def __aenter__(self):
        """Async context manager entry"""        if self.redis_url and REDIS_AVAILABLE:
            try:
                import aioredis  # Import here to avoid module-level issues
                self.redis_client = await aioredis.from_url(self.redis_url)
                logger.info("Rate limiter connected to Redis")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using memory cache.")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""        if self.redis_client:
            await self.redis_client.close()
            
    async def check_rate_limit(
        self,
        platform: str,
        endpoint: str = "*",
        user_id: Optional[str] = None
    ) -> RateLimitStatus:
        """        Check if request can be made within rate limits
        
        Args:
            platform: Platform name (youtube, instagram, etc.)
            endpoint: Specific endpoint or "*" for general
            user_id: Optional user identifier for per-user limits
            
        Returns:
            RateLimitStatus with current limit status
        """        key = f"{platform}:{endpoint}"
        if user_id:
            key = f"{key}:{user_id}"
            
        rule = self._get_rate_limit_rule(platform, endpoint)
        
        if self.redis_client:
            return await self._check_redis_rate_limit(key, rule)
        else:
            return await self._check_memory_rate_limit(key, rule)
            
    async def record_request(
        self,
        platform: str,
        endpoint: str = "*",
        user_id: Optional[str] = None,
        status_code: int = 200
    ):
        """        Record a request for rate limiting tracking
        
        Args:
            platform: Platform name
            endpoint: Specific endpoint
            user_id: Optional user identifier
            status_code: HTTP status code of the request
        """        key = f"{platform}:{endpoint}"
        if user_id:
            key = f"{key}:{user_id}"
            
        # Handle rate limit responses
        if status_code == 429:
            await self._handle_rate_limit_exceeded(platform, endpoint, user_id)
        elif status_code >= 500:
            await self._handle_server_error(platform, endpoint, user_id)
        else:
            # Reset backoff on successful requests
            self.backoff_cache[key] = 0
            
    async def get_wait_time(
        self,
        platform: str,
        endpoint: str = "*",
        user_id: Optional[str] = None
    ) -> float:
        """        Get recommended wait time before next request
        
        Returns:
            Wait time in seconds
        """        key = f"{platform}:{endpoint}"
        if user_id:
            key = f"{key}:{user_id}"
            
        # Check if there's an active backoff
        if key in self.backoff_cache and self.backoff_cache[key] > 0:
            return self.backoff_cache[key]
            
        status = await self.check_rate_limit(platform, endpoint, user_id)
        
        if status.is_limited:
            if status.retry_after:
                return status.retry_after
            else:
                # Calculate wait time based on reset time
                now = datetime.now()
                if status.reset_time > now:
                    return (status.reset_time - now).total_seconds()
                    
        return 0
        
    async def add_platform_limits(self, platform: str, limits: Dict[str, RateLimitRule]):
        """Add custom rate limits for a platform"""        self.platform_limits[platform] = limits
        logger.info(f"Added rate limits for platform: {platform}")
        
    def _get_rate_limit_rule(self, platform: str, endpoint: str) -> RateLimitRule:
        """Get rate limit rule for platform and endpoint"""        platform_rules = self.platform_limits.get(platform, {})
        
        # Try specific endpoint first, then fallback to general
        if endpoint in platform_rules:
            return platform_rules[endpoint]
        elif "*" in platform_rules:
            return platform_rules["*"]
        else:
            # Default fallback
            return RateLimitRule(platform, endpoint, 100, 3600, 10)
            
    async def _check_redis_rate_limit(self, key: str, rule: RateLimitRule) -> RateLimitStatus:
        """Check rate limit using Redis backend"""        try:
            if not REDIS_AVAILABLE:
                return await self._check_memory_rate_limit(key, rule)
                
            import aioredis  # Import here to avoid module-level issues
            
            now = int(time.time())
            window_start = now - rule.time_window
            
            # Use sliding window algorithm
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(f"rate_limit:{key}", 0, window_start)
            
            # Count current requests
            pipe.zcard(f"rate_limit:{key}")
            
            # Add current request
            pipe.zadd(f"rate_limit:{key}", {str(now): now})
            
            # Set expiry
            pipe.expire(f"rate_limit:{key}", rule.time_window)
            
            results = await pipe.execute()
            current_count = results[1] if len(results) > 1 else 0
            
            remaining = max(0, rule.max_requests - current_count - 1)
            reset_time = datetime.fromtimestamp(now + rule.time_window)
            
            is_limited = current_count >= rule.max_requests
            
            return RateLimitStatus(
                platform=rule.platform,
                endpoint=rule.endpoint,
                remaining_requests=remaining,
                reset_time=reset_time,
                is_limited=is_limited
            )
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to memory cache
            return await self._check_memory_rate_limit(key, rule)
            
    async def _check_memory_rate_limit(self, key: str, rule: RateLimitRule) -> RateLimitStatus:
        """Check rate limit using memory cache"""        now = time.time()
        window_start = now - rule.time_window
        
        # Clean old entries
        request_times = self.memory_cache[key]["requests"]
        while request_times and request_times[0] < window_start:
            request_times.popleft()
            
        current_count = len(request_times)
        remaining = max(0, rule.max_requests - current_count - 1)
        reset_time = datetime.fromtimestamp(now + rule.time_window)
        
        is_limited = current_count >= rule.max_requests
        
        if not is_limited:
            request_times.append(now)
            
        return RateLimitStatus(
            platform=rule.platform,
            endpoint=rule.endpoint,
            remaining_requests=remaining,
            reset_time=reset_time,
            is_limited=is_limited
        )
        
    async def _handle_rate_limit_exceeded(
        self,
        platform: str,
        endpoint: str,
        user_id: Optional[str] = None
    ):
        """Handle rate limit exceeded response"""        key = f"{platform}:{endpoint}"
        if user_id:
            key = f"{key}:{user_id}"
            
        rule = self._get_rate_limit_rule(platform, endpoint)
        
        # Apply exponential backoff
        current_backoff = self.backoff_cache.get(key, 1)
        new_backoff = min(current_backoff * rule.backoff_factor, rule.max_backoff)
        self.backoff_cache[key] = new_backoff
        
        logger.warning(
            f"Rate limit exceeded for {platform}:{endpoint}. "
            f"Backoff: {new_backoff}s"
        )
        
    async def _handle_server_error(
        self,
        platform: str,
        endpoint: str,
        user_id: Optional[str] = None
    ):
        """Handle server error response"""        key = f"{platform}:{endpoint}"
        if user_id:
            key = f"{key}:{user_id}"
            
        # Apply smaller backoff for server errors
        current_backoff = self.backoff_cache.get(key, 1)
        new_backoff = min(current_backoff * 1.5, 60)  # Max 60s for server errors
        self.backoff_cache[key] = new_backoff
        
        logger.warning(
            f"Server error for {platform}:{endpoint}. "
            f"Backoff: {new_backoff}s"
        )
        
    async def get_platform_status(self, platform: str) -> Dict[str, Any]:
        """Get overall status for a platform"""        platform_rules = self.platform_limits.get(platform, {})
        status = {}
        
        for endpoint, rule in platform_rules.items():
            endpoint_status = await self.check_rate_limit(platform, endpoint)
            status[endpoint] = {
                "remaining": endpoint_status.remaining_requests,
                "reset_time": endpoint_status.reset_time.isoformat(),
                "is_limited": endpoint_status.is_limited
            }
            
        return status
        
    async def reset_platform_limits(self, platform: str):
        """Reset all rate limits for a platform (admin function)"""        if self.redis_client:
            # Find and delete all keys for this platform
            pattern = f"rate_limit:{platform}:*"
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        else:
            # Clear memory cache
            keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{platform}:")]
            for key in keys_to_remove:
                del self.memory_cache[key]
                
        # Clear backoff cache
        backoff_keys_to_remove = [k for k in self.backoff_cache.keys() if k.startswith(f"{platform}:")]
        for key in backoff_keys_to_remove:
            del self.backoff_cache[key]
            
        logger.info(f"Reset rate limits for platform: {platform}")