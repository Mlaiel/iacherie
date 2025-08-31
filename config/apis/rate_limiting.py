"""API Rate Limiting - Advanced Rate Limiting & Traffic Management
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides advanced rate limiting capabilities for API requests
including sliding window, token bucket, and adaptive rate limiting algorithms.
"""import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis
import json

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"

class RateLimitScope(Enum):
    """Rate limit scope"""    GLOBAL = "global"
    PER_USER = "per_user"
    PER_API = "per_api"
    PER_ENDPOINT = "per_endpoint"
    PER_IP = "per_ip"

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""    api_name: str
    strategy: RateLimitStrategy
    scope: RateLimitScope
    
    # Limits
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    requests_per_day: int = 86400
    burst_limit: int = 10
    
    # Token bucket settings
    bucket_size: int = 100
    refill_rate: float = 1.0  # tokens per second
    
    # Sliding window settings
    window_size_seconds: int = 60
    
    # Adaptive settings
    min_requests_per_minute: int = 10
    max_requests_per_minute: int = 1000
    adaptation_factor: float = 1.1
    
    # Backoff settings
    enable_backoff: bool = True
    backoff_factor: float = 2.0
    max_backoff_seconds: int = 300
    
    # Redis settings
    use_redis: bool = True
    redis_key_prefix: str = "rate_limit"
    
    # Environment overrides
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> 'RateLimitConfig':
        """Get configuration for specific environment"""        if environment in self.environments:
            env_overrides = self.environments[environment]
            # Create a copy with environment-specific overrides
            config_dict = self.__dict__.copy()
            config_dict.update(env_overrides)
            return RateLimitConfig(**config_dict)
        return self

@dataclass
class RateLimitResult:
    """Rate limit check result"""    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after_seconds: Optional[int] = None
    current_usage: int = 0
    limit: int = 0

class RateLimiter:
    """Base rate limiter class"""    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.redis_client = None
        
        if config.use_redis:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    password=os.getenv("REDIS_PASSWORD"),
                    decode_responses=True
                )
            except Exception as e:
                logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
                self.redis_client = None
        
        self.local_storage = {}
    
    async def check_rate_limit(self, identifier: str) -> RateLimitResult:
        """Check if request is within rate limits"""        # Base implementation provides a simple fixed window rate limiter
        current_time = int(time.time())
        window_start = current_time - (current_time % 60)  # 1-minute windows
        
        key = self._get_key(identifier, str(window_start))
        
        # Use local storage as fallback
        current_count = self.local_storage.get(key, 0) + 1
        self.local_storage[key] = current_count
        
        allowed = current_count <= self.config.requests_per_minute
        remaining = max(0, self.config.requests_per_minute - current_count)
        reset_time = datetime.fromtimestamp(window_start + 60)
        
        retry_after = None if allowed else (window_start + 60 - current_time)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            retry_after_seconds=retry_after,
            current_usage=current_count,
            limit=self.config.requests_per_minute
        )
    
    def _get_key(self, identifier: str, window: str = "") -> str:
        """Generate Redis key for rate limiting"""        key_parts = [self.config.redis_key_prefix, self.config.api_name, identifier]
        if window:
            key_parts.append(window)
        return ":".join(key_parts)

class FixedWindowRateLimiter(RateLimiter):
    """Fixed window rate limiter"""    
    async def check_rate_limit(self, identifier: str) -> RateLimitResult:
        """Check rate limit using fixed window strategy"""        current_time = int(time.time())
        window_start = current_time - (current_time % 60)  # 1-minute windows
        
        key = self._get_key(identifier, str(window_start))
        
        if self.redis_client:
            try:
                # Atomic increment with expiration
                pipe = self.redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, 60)
                results = pipe.execute()
                current_count = results[0]
            except Exception as e:
                logger.error(f"Redis error in fixed window rate limiter: {e}")
                # Fall back to local storage
                current_count = self.local_storage.get(key, 0) + 1
                self.local_storage[key] = current_count
        else:
            current_count = self.local_storage.get(key, 0) + 1
            self.local_storage[key] = current_count
        
        allowed = current_count <= self.config.requests_per_minute
        remaining = max(0, self.config.requests_per_minute - current_count)
        reset_time = datetime.fromtimestamp(window_start + 60)
        
        retry_after = None if allowed else (window_start + 60 - current_time)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            retry_after_seconds=retry_after,
            current_usage=current_count,
            limit=self.config.requests_per_minute
        )

class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window rate limiter"""    
    async def check_rate_limit(self, identifier: str) -> RateLimitResult:
        """Check rate limit using sliding window strategy"""        current_time = time.time()
        window_start = current_time - self.config.window_size_seconds
        
        key = self._get_key(identifier, "sliding")
        
        if self.redis_client:
            try:
                # Use sorted set to track requests with timestamps
                pipe = self.redis_client.pipeline()
                # Remove old requests
                pipe.zremrangebyscore(key, 0, window_start)
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                # Count requests in window
                pipe.zcard(key)
                # Set expiration
                pipe.expire(key, self.config.window_size_seconds)
                results = pipe.execute()
                current_count = results[2]
            except Exception as e:
                logger.error(f"Redis error in sliding window rate limiter: {e}")
                # Simplified fallback
                current_count = self.local_storage.get(key, 0) + 1
                self.local_storage[key] = current_count
        else:
            # Simple in-memory implementation
            if key not in self.local_storage:
                self.local_storage[key] = []
            
            # Remove old timestamps
            self.local_storage[key] = [
                ts for ts in self.local_storage[key] 
                if ts > window_start
            ]
            # Add current timestamp
            self.local_storage[key].append(current_time)
            current_count = len(self.local_storage[key])
        
        allowed = current_count <= self.config.requests_per_minute
        remaining = max(0, self.config.requests_per_minute - current_count)
        
        # Calculate when the oldest request will expire
        reset_time = datetime.fromtimestamp(current_time + self.config.window_size_seconds)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            current_usage=current_count,
            limit=self.config.requests_per_minute
        )

class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter"""    
    async def check_rate_limit(self, identifier: str) -> RateLimitResult:
        """Check rate limit using token bucket strategy"""        current_time = time.time()
        key = self._get_key(identifier, "bucket")
        
        if self.redis_client:
            try:
                # Get bucket state
                bucket_data = self.redis_client.get(key)
                if bucket_data:
                    bucket = json.loads(bucket_data)
                    tokens = bucket['tokens']
                    last_refill = bucket['last_refill']
                else:
                    tokens = self.config.bucket_size
                    last_refill = current_time
                
                # Refill tokens based on time elapsed
                time_elapsed = current_time - last_refill
                tokens_to_add = time_elapsed * self.config.refill_rate
                tokens = min(self.config.bucket_size, tokens + tokens_to_add)
                
                # Check if we can consume a token
                if tokens >= 1:
                    tokens -= 1
                    allowed = True
                else:
                    allowed = False
                
                # Update bucket state
                bucket_data = {
                    'tokens': tokens,
                    'last_refill': current_time
                }
                self.redis_client.setex(key, 3600, json.dumps(bucket_data))
                
            except Exception as e:
                logger.error(f"Redis error in token bucket rate limiter: {e}")
                # Fallback to allow request
                allowed = True
                tokens = self.config.bucket_size - 1
        else:
            # In-memory implementation
            if key not in self.local_storage:
                self.local_storage[key] = {
                    'tokens': self.config.bucket_size,
                    'last_refill': current_time
                }
            
            bucket = self.local_storage[key]
            time_elapsed = current_time - bucket['last_refill']
            tokens_to_add = time_elapsed * self.config.refill_rate
            bucket['tokens'] = min(self.config.bucket_size, bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = current_time
            
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                allowed = True
                tokens = bucket['tokens']
            else:
                allowed = False
                tokens = 0
        
        remaining = int(tokens)
        reset_time = datetime.fromtimestamp(
            current_time + (self.config.bucket_size - tokens) / self.config.refill_rate
        )
        
        retry_after = None if allowed else int(1 / self.config.refill_rate)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            retry_after_seconds=retry_after,
            current_usage=self.config.bucket_size - remaining,
            limit=self.config.bucket_size
        )

class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts limits based on system performance"""    
    def __init__(self, config: RateLimitConfig):
        super().__init__(config)
        self.current_limit = config.requests_per_minute
        self.last_adjustment = time.time()
        self.error_rate = 0.0
        self.response_times = []
    
    async def check_rate_limit(self, identifier: str) -> RateLimitResult:
        """Check rate limit with adaptive adjustment"""        # First check with current limit using sliding window
        temp_config = RateLimitConfig(
            api_name=self.config.api_name,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            scope=self.config.scope,
            requests_per_minute=self.current_limit,
            window_size_seconds=self.config.window_size_seconds
        )
        
        sliding_limiter = SlidingWindowRateLimiter(temp_config)
        result = await sliding_limiter.check_rate_limit(identifier)
        
        # Adjust limits based on system performance
        self._adjust_limits()
        
        return result
    
    def _adjust_limits(self):
        """Adjust rate limits based on system performance"""        current_time = time.time()
        
        # Only adjust every 60 seconds
        if current_time - self.last_adjustment < 60:
            return
        
        self.last_adjustment = current_time
        
        # Calculate average response time
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            self.response_times = self.response_times[-100:]  # Keep last 100
        else:
            avg_response_time = 0
        
        # Adjust based on error rate and response time
        if self.error_rate > 0.1 or avg_response_time > 2.0:
            # High error rate or slow responses - decrease limit
            self.current_limit = max(
                self.config.min_requests_per_minute,
                int(self.current_limit / self.config.adaptation_factor)
            )
            logger.info(f"Decreased rate limit to {self.current_limit} due to performance issues")
        elif self.error_rate < 0.01 and avg_response_time < 0.5:
            # Low error rate and fast responses - increase limit
            self.current_limit = min(
                self.config.max_requests_per_minute,
                int(self.current_limit * self.config.adaptation_factor)
            )
            logger.info(f"Increased rate limit to {self.current_limit} due to good performance")
    
    def record_response(self, success: bool, response_time: float):
        """Record response for adaptive adjustment"""        if not success:
            self.error_rate = min(1.0, self.error_rate + 0.01)
        else:
            self.error_rate = max(0.0, self.error_rate - 0.001)
        
        self.response_times.append(response_time)

class APIRateLimiter:
    """Main API rate limiter coordinator"""    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
        self.configs: Dict[str, RateLimitConfig] = {}
    
    def register_rate_limit(self, api_name: str, config: RateLimitConfig):
        """Register rate limit configuration for an API"""        self.configs[api_name] = config
        
        # Create appropriate limiter based on strategy
        if config.strategy == RateLimitStrategy.FIXED_WINDOW:
            limiter = FixedWindowRateLimiter(config)
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            limiter = SlidingWindowRateLimiter(config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            limiter = TokenBucketRateLimiter(config)
        elif config.strategy == RateLimitStrategy.ADAPTIVE:
            limiter = AdaptiveRateLimiter(config)
        else:
            # Default to sliding window
            limiter = SlidingWindowRateLimiter(config)
        
        self.limiters[api_name] = limiter
        logger.info(f"Registered rate limiter for {api_name} with strategy {config.strategy.value}")
    
    async def check_rate_limit(self, api_name: str, identifier: str) -> RateLimitResult:
        """Check rate limit for API and identifier"""        if api_name not in self.limiters:
            # No rate limiting configured - allow request
            return RateLimitResult(
                allowed=True,
                remaining_requests=999999,
                reset_time=datetime.utcnow() + timedelta(hours=1)
            )
        
        limiter = self.limiters[api_name]
        return await limiter.check_rate_limit(identifier)
    
    def record_api_response(self, api_name: str, success: bool, response_time: float):
        """Record API response for adaptive rate limiting"""        if api_name in self.limiters:
            limiter = self.limiters[api_name]
            if isinstance(limiter, AdaptiveRateLimiter):
                limiter.record_response(success, response_time)
    
    def get_rate_limit_config(self, api_name: str) -> Optional[RateLimitConfig]:
        """Get rate limit configuration for API"""        return self.configs.get(api_name)
    
    def update_rate_limit_config(self, api_name: str, config: RateLimitConfig):
        """Update rate limit configuration"""        self.register_rate_limit(api_name, config)
    
    def get_all_configs(self) -> Dict[str, RateLimitConfig]:
        """Get all rate limit configurations"""        return self.configs.copy()
    
    def remove_rate_limit(self, api_name: str):
        """Remove rate limiting for API"""        if api_name in self.limiters:
            del self.limiters[api_name]
        if api_name in self.configs:
            del self.configs[api_name]
        logger.info(f"Removed rate limiting for {api_name}")

# Default rate limit configurations for different API types
DEFAULT_RATE_LIMITS = {
    "platform_apis": RateLimitConfig(
        api_name="platform_default",
        strategy=RateLimitStrategy.SLIDING_WINDOW,
        scope=RateLimitScope.PER_API,
        requests_per_minute=100,
        requests_per_hour=6000,
        burst_limit=20
    ),
    "payment_apis": RateLimitConfig(
        api_name="payment_default",
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        scope=RateLimitScope.PER_USER,
        requests_per_minute=50,
        requests_per_hour=3000,
        bucket_size=10,
        refill_rate=0.8
    ),
    "protection_apis": RateLimitConfig(
        api_name="protection_default",
        strategy=RateLimitStrategy.ADAPTIVE,
        scope=RateLimitScope.PER_API,
        requests_per_minute=200,
        min_requests_per_minute=50,
        max_requests_per_minute=500
    )
}
