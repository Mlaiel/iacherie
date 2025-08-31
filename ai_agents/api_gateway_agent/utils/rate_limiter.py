"""Rate Limiter - Advanced Rate Limiting System

Enterprise rate limiting with multiple strategies, distributed rate limiting,
user-based quotas, and intelligent throttling mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib

import redis.asyncio as aioredis
from fastapi import Request

from .config import RateLimitStrategy

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""    identifier: str  # user_id, ip_address, api_key, etc.
    limit: int      # requests per window
    window: int     # time window in seconds
    burst: int      # burst allowance
    strategy: RateLimitStrategy


@dataclass
class RateLimitStatus:
    """Current rate limit status"""    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None


class RateLimiter:
    """    Enterprise Rate Limiter
    
    Features:
    - Multiple rate limiting algorithms
    - Distributed rate limiting via Redis
    - User-specific and global limits
    - Burst handling
    - Quota management
    - Dynamic rule updates
    """    
    def __init__(
        self,
        redis_url: str,
        strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW,
        default_limit: int = 1000,
        window: int = 60
    ):
        """Initialize rate limiter"""        self.redis_url = redis_url
        self.strategy = strategy
        self.default_limit = default_limit
        self.window = window
        
        # Redis connection
        self.redis: Optional[aioredis.Redis] = None
        
        # Rate limit rules
        self.rules: Dict[str, RateLimitRule] = {}
        
        # Local cache for performance
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 60  # seconds
        
        logger.info(f"Rate limiter initialized with strategy: {strategy.value}")
    
    async def initialize(self):
        """Initialize Redis connection"""        try:
            self.redis = aioredis.from_url(self.redis_url)
            
            # Test connection
            await self.redis.ping()
            
            logger.info("Rate limiter Redis connection established")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            raise
    
    async def allow_request(
        self, 
        request: Request,
        identifier: Optional[str] = None
    ) -> bool:
        """        Check if request is allowed based on rate limits
        
        Args:
            request: FastAPI request object
            identifier: Custom identifier (overrides auto-detection)
            
        Returns:
            True if request is allowed, False otherwise
        """        try:
            # Get rate limit identifier
            rate_limit_id = identifier or await self._get_rate_limit_identifier(request)
            
            # Get applicable rule
            rule = await self._get_applicable_rule(rate_limit_id, request)
            
            # Check rate limit
            status = await self._check_rate_limit(rate_limit_id, rule)
            
            # Add headers to response
            if hasattr(request, 'state'):
                request.state.rate_limit_status = status
            
            return status.allowed
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request on error
            return True
    
    async def _get_rate_limit_identifier(self, request: Request) -> str:
        """Extract rate limit identifier from request"""        try:
            # Priority order: User ID > API Key > IP Address
            
            # Try to get user ID from JWT token
            if hasattr(request.state, 'user_id'):
                return f"user:{request.state.user_id}"
            
            # Try to get API key
            api_key = request.headers.get("X-API-Key")
            if api_key:
                # Hash API key for privacy
                hashed_key = hashlib.sha256(api_key.encode()).hexdigest()[:16]
                return f"api_key:{hashed_key}"
            
            # Fall back to IP address
            client_ip = self._get_client_ip(request)
            return f"ip:{client_ip}"
            
        except Exception as e:
            logger.error(f"Error getting rate limit identifier: {e}")
            return "unknown"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""        try:
            # Check forwarded headers first
            forwarded_ips = request.headers.get("X-Forwarded-For")
            if forwarded_ips:
                return forwarded_ips.split(",")[0].strip()
            
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
            
            # Fall back to direct connection IP
            if hasattr(request.client, 'host'):
                return request.client.host
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error extracting client IP: {e}")
            return "unknown"
    
    async def _get_applicable_rule(self, identifier: str, request: Request) -> RateLimitRule:
        """Get applicable rate limiting rule for identifier"""        try:
            # Check for specific rule
            if identifier in self.rules:
                return self.rules[identifier]
            
            # Check for pattern-based rules
            for rule_key, rule in self.rules.items():
                if self._matches_pattern(identifier, rule_key):
                    return rule
            
            # Check for endpoint-specific rules
            endpoint = f"{request.method}:{request.url.path}"
            endpoint_rule_key = f"endpoint:{endpoint}"
            if endpoint_rule_key in self.rules:
                return self.rules[endpoint_rule_key]
            
            # Fall back to default rule
            return RateLimitRule(
                identifier=identifier,
                limit=self.default_limit,
                window=self.window,
                burst=self.default_limit // 10,  # 10% burst allowance
                strategy=self.strategy
            )
            
        except Exception as e:
            logger.error(f"Error getting applicable rule: {e}")
            # Return permissive default
            return RateLimitRule(
                identifier=identifier,
                limit=10000,
                window=self.window,
                burst=1000,
                strategy=self.strategy
            )
    
    def _matches_pattern(self, identifier: str, pattern: str) -> bool:
        """Check if identifier matches pattern"""        try:
            # Support wildcard patterns
            if "*" in pattern:
                import fnmatch
                return fnmatch.fnmatch(identifier, pattern)
            
            # Support prefix matching
            if pattern.endswith(":*"):
                prefix = pattern[:-1]
                return identifier.startswith(prefix)
            
            return False
            
        except Exception as e:
            logger.error(f"Error matching pattern: {e}")
            return False
    
    async def _check_rate_limit(self, identifier: str, rule: RateLimitRule) -> RateLimitStatus:
        """Check rate limit using configured strategy"""        
        if rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._token_bucket_check(identifier, rule)
        elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._sliding_window_check(identifier, rule)
        elif rule.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._fixed_window_check(identifier, rule)
        elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return await self._leaky_bucket_check(identifier, rule)
        else:
            # Default to sliding window
            return await self._sliding_window_check(identifier, rule)
    
    async def _token_bucket_check(self, identifier: str, rule: RateLimitRule) -> RateLimitStatus:
        """Token bucket rate limiting algorithm"""        try:
            current_time = time.time()
            bucket_key = f"rate_limit:token_bucket:{identifier}"
            
            # Get current bucket state
            bucket_data = await self.redis.hgetall(bucket_key)
            
            if bucket_data:
                tokens = float(bucket_data.get(b'tokens', rule.limit))
                last_refill = float(bucket_data.get(b'last_refill', current_time))
            else:
                tokens = rule.limit
                last_refill = current_time
            
            # Refill tokens based on elapsed time
            elapsed = current_time - last_refill
            refill_rate = rule.limit / rule.window  # tokens per second
            tokens = min(rule.limit, tokens + elapsed * refill_rate)
            
            # Check if request can be allowed
            if tokens >= 1:
                tokens -= 1
                allowed = True
                remaining = int(tokens)
            else:
                allowed = False
                remaining = 0
            
            # Update bucket state
            pipe = self.redis.pipeline()
            pipe.hset(bucket_key, mapping={
                'tokens': tokens,
                'last_refill': current_time
            })
            pipe.expire(bucket_key, rule.window * 2)
            await pipe.execute()
            
            # Calculate reset time
            if remaining == 0:
                reset_time = datetime.fromtimestamp(current_time + (1 / refill_rate))
                retry_after = int(1 / refill_rate) + 1
            else:
                reset_time = datetime.fromtimestamp(current_time + rule.window)
                retry_after = None
            
            return RateLimitStatus(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
            
        except Exception as e:
            logger.error(f"Token bucket check error: {e}")
            return RateLimitStatus(True, rule.limit, datetime.utcnow())
    
    async def _sliding_window_check(self, identifier: str, rule: RateLimitRule) -> RateLimitStatus:
        """Sliding window rate limiting algorithm"""        try:
            current_time = time.time()
            window_key = f"rate_limit:sliding:{identifier}"
            
            # Use Redis sorted set to track requests in time window
            pipe = self.redis.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(window_key, 0, current_time - rule.window)
            
            # Count requests in current window
            pipe.zcard(window_key)
            
            # Add current request
            request_id = f"{current_time}:{id(self)}"
            pipe.zadd(window_key, {request_id: current_time})
            
            # Set expiration
            pipe.expire(window_key, rule.window * 2)
            
            results = await pipe.execute()
            request_count = results[1]
            
            # Check if request is allowed
            if request_count <= rule.limit:
                allowed = True
                remaining = rule.limit - request_count
            else:
                # Remove the request we just added since it's not allowed
                await self.redis.zrem(window_key, request_id)
                allowed = False
                remaining = 0
            
            # Calculate reset time (when oldest request expires)
            if request_count > 0:
                oldest_requests = await self.redis.zrange(window_key, 0, 0, withscores=True)
                if oldest_requests:
                    oldest_time = oldest_requests[0][1]
                    reset_time = datetime.fromtimestamp(oldest_time + rule.window)
                else:
                    reset_time = datetime.fromtimestamp(current_time + rule.window)
            else:
                reset_time = datetime.fromtimestamp(current_time + rule.window)
            
            retry_after = None
            if not allowed and request_count > 0:
                retry_after = int((reset_time - datetime.fromtimestamp(current_time)).total_seconds()) + 1
            
            return RateLimitStatus(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
            
        except Exception as e:
            logger.error(f"Sliding window check error: {e}")
            return RateLimitStatus(True, rule.limit, datetime.utcnow())
    
    async def _fixed_window_check(self, identifier: str, rule: RateLimitRule) -> RateLimitStatus:
        """Fixed window rate limiting algorithm"""        try:
            current_time = time.time()
            window_start = int(current_time // rule.window) * rule.window
            window_key = f"rate_limit:fixed:{identifier}:{window_start}"
            
            # Increment counter
            pipe = self.redis.pipeline()
            pipe.incr(window_key)
            pipe.expire(window_key, rule.window)
            results = await pipe.execute()
            
            request_count = results[0]
            
            # Check if request is allowed
            allowed = request_count <= rule.limit
            remaining = max(0, rule.limit - request_count)
            
            # Calculate reset time (start of next window)
            next_window_start = window_start + rule.window
            reset_time = datetime.fromtimestamp(next_window_start)
            
            retry_after = None
            if not allowed:
                retry_after = int(next_window_start - current_time) + 1
            
            return RateLimitStatus(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
            
        except Exception as e:
            logger.error(f"Fixed window check error: {e}")
            return RateLimitStatus(True, rule.limit, datetime.utcnow())
    
    async def _leaky_bucket_check(self, identifier: str, rule: RateLimitRule) -> RateLimitStatus:
        """Leaky bucket rate limiting algorithm"""        try:
            current_time = time.time()
            bucket_key = f"rate_limit:leaky:{identifier}"
            
            # Get current bucket state
            bucket_data = await self.redis.hgetall(bucket_key)
            
            if bucket_data:
                volume = float(bucket_data.get(b'volume', 0))
                last_leak = float(bucket_data.get(b'last_leak', current_time))
            else:
                volume = 0
                last_leak = current_time
            
            # Leak from bucket based on elapsed time
            elapsed = current_time - last_leak
            leak_rate = rule.limit / rule.window  # requests per second
            volume = max(0, volume - elapsed * leak_rate)
            
            # Check if request can be added to bucket
            if volume < rule.limit:
                volume += 1
                allowed = True
                remaining = int(rule.limit - volume)
            else:
                allowed = False
                remaining = 0
            
            # Update bucket state
            pipe = self.redis.pipeline()
            pipe.hset(bucket_key, mapping={
                'volume': volume,
                'last_leak': current_time
            })
            pipe.expire(bucket_key, rule.window * 2)
            await pipe.execute()
            
            # Calculate reset time
            if volume >= rule.limit:
                time_to_leak_one = 1 / leak_rate
                reset_time = datetime.fromtimestamp(current_time + time_to_leak_one)
                retry_after = int(time_to_leak_one) + 1
            else:
                reset_time = datetime.fromtimestamp(current_time + rule.window)
                retry_after = None
            
            return RateLimitStatus(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after
            )
            
        except Exception as e:
            logger.error(f"Leaky bucket check error: {e}")
            return RateLimitStatus(True, rule.limit, datetime.utcnow())
    
    async def add_rate_limit_rule(self, rule: RateLimitRule) -> bool:
        """Add or update rate limiting rule"""        try:
            self.rules[rule.identifier] = rule
            
            # Persist rule to Redis for distributed access
            rule_key = f"rate_limit:rules:{rule.identifier}"
            rule_data = {
                'limit': rule.limit,
                'window': rule.window,
                'burst': rule.burst,
                'strategy': rule.strategy.value
            }
            
            await self.redis.hset(rule_key, mapping=rule_data)
            await self.redis.expire(rule_key, 86400)  # Expire after 1 day
            
            logger.info(f"Added rate limit rule: {rule.identifier} -> {rule.limit}/{rule.window}s")
            return True
            
        except Exception as e:
            logger.error(f"Error adding rate limit rule: {e}")
            return False
    
    async def remove_rate_limit_rule(self, identifier: str) -> bool:
        """Remove rate limiting rule"""        try:
            # Remove from memory
            self.rules.pop(identifier, None)
            
            # Remove from Redis
            rule_key = f"rate_limit:rules:{identifier}"
            await self.redis.delete(rule_key)
            
            logger.info(f"Removed rate limit rule: {identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing rate limit rule: {e}")
            return False
    
    async def get_rate_limit_stats(self, identifier: str) -> Dict[str, Any]:
        """Get rate limit statistics for identifier"""        try:
            stats = {
                "identifier": identifier,
                "current_usage": {},
                "rules": {}
            }
            
            # Get applicable rule
            rule = self.rules.get(identifier)
            if rule:
                stats["rules"] = {
                    "limit": rule.limit,
                    "window": rule.window,
                    "burst": rule.burst,
                    "strategy": rule.strategy.value
                }
            
            # Get current usage based on strategy
            for strategy in RateLimitStrategy:
                usage = await self._get_current_usage(identifier, strategy)
                stats["current_usage"][strategy.value] = usage
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting rate limit stats: {e}")
            return {}
    
    async def _get_current_usage(self, identifier: str, strategy: RateLimitStrategy) -> Dict[str, Any]:
        """Get current usage for specific strategy"""        try:
            current_time = time.time()
            
            if strategy == RateLimitStrategy.TOKEN_BUCKET:
                bucket_key = f"rate_limit:token_bucket:{identifier}"
                bucket_data = await self.redis.hgetall(bucket_key)
                if bucket_data:
                    return {
                        "tokens_remaining": float(bucket_data.get(b'tokens', 0)),
                        "last_refill": float(bucket_data.get(b'last_refill', current_time))
                    }
            
            elif strategy == RateLimitStrategy.SLIDING_WINDOW:
                window_key = f"rate_limit:sliding:{identifier}"
                count = await self.redis.zcard(window_key)
                return {"requests_in_window": count}
            
            elif strategy == RateLimitStrategy.FIXED_WINDOW:
                window_start = int(current_time // self.window) * self.window
                window_key = f"rate_limit:fixed:{identifier}:{window_start}"
                count = await self.redis.get(window_key)
                return {"requests_in_window": int(count) if count else 0}
            
            elif strategy == RateLimitStrategy.LEAKY_BUCKET:
                bucket_key = f"rate_limit:leaky:{identifier}"
                bucket_data = await self.redis.hgetall(bucket_key)
                if bucket_data:
                    return {
                        "bucket_volume": float(bucket_data.get(b'volume', 0)),
                        "last_leak": float(bucket_data.get(b'last_leak', current_time))
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting current usage: {e}")
            return {}
    
    async def reset_rate_limit(self, identifier: str) -> bool:
        """Reset rate limits for identifier"""        try:
            # Reset all strategy-specific keys
            keys_to_delete = []
            
            for strategy in RateLimitStrategy:
                if strategy == RateLimitStrategy.TOKEN_BUCKET:
                    keys_to_delete.append(f"rate_limit:token_bucket:{identifier}")
                elif strategy == RateLimitStrategy.SLIDING_WINDOW:
                    keys_to_delete.append(f"rate_limit:sliding:{identifier}")
                elif strategy == RateLimitStrategy.LEAKY_BUCKET:
                    keys_to_delete.append(f"rate_limit:leaky:{identifier}")
                elif strategy == RateLimitStrategy.FIXED_WINDOW:
                    # Find all fixed window keys for this identifier
                    pattern = f"rate_limit:fixed:{identifier}:*"
                    fixed_keys = await self.redis.keys(pattern)
                    keys_to_delete.extend([key.decode() for key in fixed_keys])
            
            if keys_to_delete:
                await self.redis.delete(*keys_to_delete)
            
            logger.info(f"Reset rate limits for identifier: {identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting rate limits: {e}")
            return False
    
    async def close(self):
        """Close Redis connection"""        if self.redis:
            await self.redis.close()
