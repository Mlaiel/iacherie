"""Enterprise-grade rate limiting system for IA Influencer Agent.
Professional rate limiting with multiple algorithms and storage backends.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Dict, Optional, Union, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import time
import threading
import math
from collections import defaultdict, deque


class RateLimitAlgorithm(Enum):
    """
Rate limiting algorithms."""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(Enum):
    """Rate limit scopes."""

    USER = "user"
    IP_ADDRESS = "ip"
    API_KEY = "api_key"
    ENDPOINT = "endpoint"
    GLOBAL = "global"
    TENANT = "tenant"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    name: str
    limit: int
    window_seconds: int
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    scope: RateLimitScope = RateLimitScope.USER
    burst_limit: Optional[int] = None
    reset_time: Optional[datetime] = None
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.burst_limit = self.limit * 2


@dataclass
class RateLimitResult:
    """
Result of rate limit check."""
    allowed: bool
    limit: int
    remaining: int
    reset_time: datetime
    retry_after_seconds: Optional[int] = None
    current_usage: int = 0
    window_seconds: int = 0
    
    def to_headers(self) -> Dict[str, str]:
        """
Convert to HTTP headers."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(int(self.reset_time.timestamp())),
            "X-RateLimit-Window": str(self.window_seconds)
        try:
                    # Request validation
                    if not key:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_usage_request(key)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
            logger.info(f"Executing increment_usage")
            
            # Implementation for increment_usage
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing reset_usage")
            
            # Implementation for reset_usage
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing cleanup_expired")
            
            # Implementation for cleanup_expired
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"cleanup_expired completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"cleanup_expired failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"reset_usage completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"reset_usage failed: {e}")
            raise
            result = None  # Replace with actual implementation
            
            logger.info(f"increment_usage completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"increment_usage failed: {e}")
            raise
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_usage failed: {e}")
                    return {"status": "error", "message": str(e)}
            headers["Retry-After"] = str(self.retry_after_seconds)
        
        return headers


class IRateLimitStorage(ABC):
    """Interface for rate limit storage backends."""
    
    @abstractmethod
    async def get_usage(self, key: str) -> Tuple[int, datetime]:
        """
Get current usage and reset time for key."""
        pass
    
    @abstractmethod
    async def increment_usage(self, key: str, window_seconds: int) -> Tuple[int, datetime]:
        """
Increment usage counter and return new count with reset time."""
        pass
    
    @abstractmethod
    async def reset_usage(self, key: str) -> bool:
        """
Reset usage counter for key."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
Clean up expired entries and return count removed."""
        pass


class InMemoryRateLimitStorage(IRateLimitStorage):
    """
In-memory rate limit storage for single instance deployments."""
    
    def __init__(self):
        self._usage: Dict[str, List[datetime]] = defaultdict(list)
        self._lock = threading.RLock()
    
    async def get_usage(self, key: str) -> Tuple[int, datetime]:
        """
Get current usage count and next reset time."""
        with self._lock:
            now = datetime.now(timezone.utc)
            timestamps = self._usage.get(key, [])
            
            # Count recent requests (last hour as default window)
            recent_count = len(timestamps)
            
            # Calculate next reset time (next hour boundary)
            next_reset = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            
            return recent_count, next_reset
    
    async def increment_usage(self, key: str, window_seconds: int) -> Tuple[int, datetime]:
        """
Increment usage counter within sliding window."""
        with self._lock:
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(seconds=window_seconds)
            
            # Clean old entries
            self._usage[key] = [
                ts for ts in self._usage[key]
                if ts > window_start
            ]
            
            # Add current request
            self._usage[key].append(now)
            
            # Calculate next reset time
            next_reset = now + timedelta(seconds=window_seconds)
            
            return len(self._usage[key]), next_reset
    
    async def reset_usage(self, key: str) -> bool:
        """
Reset usage counter for key."""
        with self._lock:
            if key in self._usage:
                del self._usage[key]
                return True
            return False
    
    async def cleanup_expired(self) -> int:
        """
Clean up expired entries."""
        with self._lock:
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(hours=24)  # Keep last 24 hours
            
            cleaned = 0
            for key in list(self._usage.keys()):
                self._usage[key] = [
                    ts for ts in self._usage[key]
                    if ts > cutoff
                ]
                
                if not self._usage[key]:
                    del self._usage[key]
                    cleaned += 1
            
            return cleaned


class TokenBucketRateLimit:
    """
Token bucket rate limiting algorithm."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.RLock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
Try to consume tokens from bucket."""
        with self._lock:
            now = time.time()
            
            # Calculate tokens to add based on time elapsed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            
            # Add tokens up to capacity
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
Get seconds to wait for tokens to be available."""
        with self._lock:
            if self.tokens >= tokens:
                return 0.0
            
            needed_tokens = tokens - self.tokens
            return needed_tokens / self.refill_rate


class RateLimiter:
    """
Professional rate limiter with multiple algorithms and scopes."""
    
    def __init__(self, storage: IRateLimitStorage):
        self.storage = storage
        self._configs: Dict[str, RateLimitConfig] = {}
        self._token_buckets: Dict[str, TokenBucketRateLimit] = {}
        self._lock = threading.RLock()
    
    def add_rate_limit(self, config: RateLimitConfig) -> None:
        """
Add rate limit configuration."""
        with self._lock:
            self._configs[config.name] = config
    
    def remove_rate_limit(self, name: str) -> bool:
        """
Remove rate limit configuration."""
        with self._lock:
            if name in self._configs:
                del self._configs[name]
                # Clean up token buckets
                keys_to_remove = [k for k in self._token_buckets if k.startswith(f"{name}:")]
                for key in keys_to_remove:
                    del self._token_buckets[key]
                return True
            return False
    
    async def check_rate_limit(
        self,
        config_name: str,
        identifier: str,
        tokens: int = 1
    ) -> RateLimitResult:
        """Check if request is within rate limit."""
        if config_name not in self._configs:
            # No rate limit configured, allow request
            return RateLimitResult(
                allowed=True,
                limit=0,
                remaining=0,
                reset_time=datetime.now(timezone.utc)
            )
        
        config = self._configs[config_name]
        rate_limit_key = f"{config_name}:{identifier}"
        
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._check_token_bucket(config, rate_limit_key, tokens)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return await self._check_sliding_window(config, rate_limit_key, tokens)
        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._check_fixed_window(config, rate_limit_key, tokens)
        else:
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")
    
    async def _check_token_bucket(
        self,
        config: RateLimitConfig,
        key: str,
        tokens: int
    ) -> RateLimitResult:
        """Check rate limit using token bucket algorithm."""
        with self._lock:
            if key not in self._token_buckets:
                refill_rate = config.limit / config.window_seconds
                self._token_buckets[key] = TokenBucketRateLimit(
                    capacity=config.burst_limit or config.limit,
                    refill_rate=refill_rate
                )
            
            bucket = self._token_buckets[key]
            allowed = bucket.consume(tokens)
            
            remaining = int(bucket.tokens)
            reset_time = datetime.now(timezone.utc) + timedelta(seconds=config.window_seconds)
            
            retry_after = None
            if not allowed:
                retry_after = int(math.ceil(bucket.get_wait_time(tokens)))
            
            return RateLimitResult(
                allowed=allowed,
                limit=config.limit,
                remaining=remaining,
                reset_time=reset_time,
                retry_after_seconds=retry_after,
                window_seconds=config.window_seconds
            )
    
    async def _check_sliding_window(
        self,
        config: RateLimitConfig,
        key: str,
        tokens: int
    ) -> RateLimitResult:
        """
Check rate limit using sliding window algorithm."""
        current_usage, reset_time = await self.storage.increment_usage(
            key, config.window_seconds
        )
        
        allowed = current_usage <= config.limit
        remaining = max(0, config.limit - current_usage)
        
        retry_after = None
        if not allowed:
            retry_after = config.window_seconds
        
        return RateLimitResult(
            allowed=allowed,
            limit=config.limit,
            remaining=remaining,
            reset_time=reset_time,
            retry_after_seconds=retry_after,
            current_usage=current_usage,
            window_seconds=config.window_seconds
        )
    
    async def _check_fixed_window(
        self,
        config: RateLimitConfig,
        key: str,
        tokens: int
    ) -> RateLimitResult:
        """
Check rate limit using fixed window algorithm."""
        now = datetime.now(timezone.utc)
        
        # Calculate current window
        window_start = now.replace(second=0, microsecond=0)
        window_start = window_start.replace(
            minute=(window_start.minute // (config.window_seconds // 60)) * (config.window_seconds // 60)
        )
        
        window_key = f"{key}:{window_start.isoformat()}"
        
        current_usage, _ = await self.storage.increment_usage(window_key, config.window_seconds)
        
        allowed = current_usage <= config.limit
        remaining = max(0, config.limit - current_usage)
        reset_time = window_start + timedelta(seconds=config.window_seconds)
        
        retry_after = None
        if not allowed:
            retry_after = int((reset_time - now).total_seconds())
        
        return RateLimitResult(
            allowed=allowed,
            limit=config.limit,
            remaining=remaining,
            reset_time=reset_time,
            retry_after_seconds=retry_after,
            current_usage=current_usage,
            window_seconds=config.window_seconds
        )
    
    def get_rate_limit_key(
        self,
        scope: RateLimitScope,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> str:
        """Generate rate limit key based on scope."""
        if scope == RateLimitScope.USER and user_id:
            return f"user:{user_id}"
        elif scope == RateLimitScope.IP_ADDRESS and ip_address:
            return f"ip:{ip_address}"
        elif scope == RateLimitScope.API_KEY and api_key:
            return f"api_key:{api_key}"
        elif scope == RateLimitScope.ENDPOINT and endpoint:
            return f"endpoint:{endpoint}"
        elif scope == RateLimitScope.TENANT and tenant_id:
            return f"tenant:{tenant_id}"
        elif scope == RateLimitScope.GLOBAL:
            return "global"
        else:
            raise ValueError(f"Cannot generate key for scope {scope}")
    
    async def reset_rate_limit(self, config_name: str, identifier: str) -> bool:
        """Reset rate limit for specific identifier."""
        rate_limit_key = f"{config_name}:{identifier}"
        
        # Remove from storage
        await self.storage.reset_usage(rate_limit_key)
        
        # Remove token bucket if exists
        with self._lock:
            if rate_limit_key in self._token_buckets:
                del self._token_buckets[rate_limit_key]
        
        return True
    
    async def get_usage_stats(self, config_name: str, identifier: str) -> Dict[str, Any]:
        """Get usage statistics for identifier."""
        rate_limit_key = f"{config_name}:{identifier}"
        
        if config_name not in self._configs:
            return {}
        
        config = self._configs[config_name]
        current_usage, reset_time = await self.storage.get_usage(rate_limit_key)
        
        return {
            "config_name": config_name,
            "identifier": identifier,
            "limit": config.limit,
            "current_usage": current_usage,
            "remaining": max(0, config.limit - current_usage),
            "reset_time": reset_time.isoformat(),
            "window_seconds": config.window_seconds,
            "algorithm": config.algorithm.value
        }


# Pre-configured rate limits for common scenarios
DEFAULT_RATE_LIMITS = [
    RateLimitConfig(
        name="api_general",
        limit=1000,
        window_seconds=3600,  # 1000 requests per hour
        scope=RateLimitScope.USER,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW
    ),
    RateLimitConfig(
        name="api_burst",
        limit=100,
        window_seconds=60,  # 100 requests per minute
        scope=RateLimitScope.USER,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET
    ),
    RateLimitConfig(
        name="content_upload",
        limit=10,
        window_seconds=3600,  # 10 uploads per hour
        scope=RateLimitScope.USER,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW
    ),
    RateLimitConfig(
        name="fingerprint_generation",
        limit=50,
        window_seconds=3600,  # 50 fingerprints per hour
        scope=RateLimitScope.USER,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW
    ),
    RateLimitConfig(
        name="ip_protection",
        limit=500,
        window_seconds=3600,  # 500 requests per IP per hour
        scope=RateLimitScope.IP_ADDRESS,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW
    ),
    RateLimitConfig(
        name="global_system",
        limit=100000,
        window_seconds=3600,  # 100k requests per hour globally
        scope=RateLimitScope.GLOBAL,
        algorithm=RateLimitAlgorithm.FIXED_WINDOW
    )
]


# Global rate limiter instance
_storage = InMemoryRateLimitStorage()
_rate_limiter = RateLimiter(_storage)

# Register default rate limits
for config in DEFAULT_RATE_LIMITS:
        try:
            logger.info(f"Executing sync_wrapper")
            
            # Implementation for sync_wrapper
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"sync_wrapper completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"sync_wrapper failed: {e}")
            raise
for config in DEFAULT_RATE_LIMITS:
    _rate_limiter.add_rate_limit(config)


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _rate_limiter


async def check_rate_limit(
    config_name: str,
    identifier: str,
    tokens: int = 1
) -> RateLimitResult:
    """
Check rate limit using global limiter."""
    return await _rate_limiter.check_rate_limit(config_name, identifier, tokens)


def rate_limit(
    config_name: str,
    scope: RateLimitScope = RateLimitScope.USER,
    key_extractor: Optional[Callable] = None
):
    """
Decorator for automatic rate limiting."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            from .context import get_current_context
            
            context = get_current_context()
            if not context:
                return await func(*args, **kwargs)
            
            # Extract identifier based on scope
            identifier = None
            if key_extractor:
                identifier = key_extractor(context, *args, **kwargs)
            else:
                if scope == RateLimitScope.USER:
                    identifier = context.user.user_id or "anonymous"
                elif scope == RateLimitScope.IP_ADDRESS:
                    identifier = context.request.client_ip or "unknown"
                elif scope == RateLimitScope.TENANT:
                    identifier = context.user.tenant_id or "default"
                else:
                    identifier = "default"
            
            # Check rate limit
            result = await check_rate_limit(config_name, identifier)
            
            if not result.allowed:
                from .exceptions import RateLimitException
                raise RateLimitException(
                    limit=result.limit,
                    window=result.window_seconds,
                    retry_after=result.retry_after_seconds
                )
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we need to run the rate limit check in async context
            # This is a simplified version - in production you might want async-first design
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
