"""Rate Limiting Middleware Module
==============================

Enterprise-grade rate limiting middleware for crawler pipeline.
Implements distributed rate limiting, burst protection, and intelligent throttling.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Business Logic Integration:
- Multi-format creators get priority rate limits based on subscription
- Premium content processing gets higher rate limits
- AI protection services have dedicated rate limit pools
- Cross-platform distribution respects platform-specific limits
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
import redis
from pydantic import BaseModel, Field
import logging
import hashlib
import statistics

from ...config.settings import get_settings
from ...utils.cache import CacheManager

settings = get_settings()
logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"
    PRIORITY_QUEUE = "priority_queue"
    GEOLOCATION_BASED = "geolocation_based"


class RateLimitLevel(str, Enum):
    """Rate limit severity levels"""    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    BLOCKED = "blocked"


class UserTier(str, Enum):
    """User subscription tiers affecting rate limits"""    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    VIP = "vip"


class RateLimitRequest(BaseModel):
    """Rate limit request model"""    user_id: str = Field(description="User identifier")
    api_key: Optional[str] = Field(None, description="API key")
    endpoint: str = Field(description="Endpoint being accessed")
    content_type: Optional[str] = Field(None, description="Content type")
    priority: int = Field(default=5, description="Request priority (1-10)")
    user_tier: UserTier = Field(default=UserTier.FREE, description="User subscription tier")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RateLimitResult(BaseModel):
    """Rate limit result model"""    allowed: bool = Field(description="Whether request is allowed")
    current_usage: int = Field(description="Current usage count")
    limit: int = Field(description="Rate limit threshold")
    reset_time: datetime = Field(description="When limit resets")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retry")
    strategy_used: RateLimitStrategy = Field(description="Strategy used for limiting")
    level: RateLimitLevel = Field(description="Current rate limit level")
    queue_position: Optional[int] = Field(None, description="Position in priority queue")
    estimated_wait: Optional[int] = Field(None, description="Estimated wait time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional info")


class RateLimitConfig(BaseModel):
    """Rate limit configuration"""    requests_per_minute: int = Field(default=100, description="Requests per minute")
    requests_per_hour: int = Field(default=1000, description="Requests per hour")
    requests_per_day: int = Field(default=10000, description="Requests per day")
    burst_limit: int = Field(default=10, description="Burst request limit")
    concurrent_limit: int = Field(default=5, description="Concurrent request limit")
    strategy: RateLimitStrategy = Field(default=RateLimitStrategy.SLIDING_WINDOW)
    priority_multiplier: float = Field(default=1.0, description="Priority-based multiplier")
    tier_multipliers: Dict[UserTier, float] = Field(
        default_factory=lambda: {
            UserTier.FREE: 1.0,
            UserTier.BASIC: 2.0,
            UserTier.PREMIUM: 5.0,
            UserTier.ENTERPRISE: 10.0,
            UserTier.VIP: 20.0
        },
        description="Multipliers for different user tiers"
    )


class SlidingWindowLimiter:
    """Advanced sliding window rate limiter implementation"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
    async def check_limit(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int, datetime]:
        """Check rate limit using sliding window algorithm"""        now = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window_seconds)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request timestamp
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window_seconds)
        
        results = await pipeline.execute()
        current_count = results[1]
        
        # Calculate reset time
        reset_time = datetime.fromtimestamp(now + window_seconds)
        
        return current_count < limit, current_count, reset_time


class TokenBucketLimiter:
    """Token bucket rate limiter implementation"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
    async def check_limit(self, key: str, capacity: int, refill_rate: float) -> Tuple[bool, int, datetime]:
        """Check rate limit using token bucket algorithm"""        now = time.time()
        bucket_key = f"bucket:{key}"
        
        # Get current bucket state
        bucket_data = await self.redis_client.hmget(bucket_key, "tokens", "last_refill")
        
        tokens = float(bucket_data[0] or capacity)
        last_refill = float(bucket_data[1] or now)
        
        # Calculate new tokens
        time_passed = now - last_refill
        new_tokens = min(capacity, tokens + (time_passed * refill_rate))
        
        if new_tokens >= 1.0:
            # Consume token
            new_tokens -= 1.0
            allowed = True
        else:
            allowed = False
        
        # Update bucket state
        await self.redis_client.hmset(bucket_key, {
            "tokens": new_tokens,
            "last_refill": now
        })
        await self.redis_client.expire(bucket_key, 3600)  # 1 hour expiry
        
        # Calculate reset time
        tokens_needed = 1.0 - new_tokens
        seconds_to_wait = tokens_needed / refill_rate if refill_rate > 0 else 0
        reset_time = datetime.fromtimestamp(now + seconds_to_wait)
        
        return allowed, int(capacity - new_tokens), reset_time


class AdaptiveLimiter:
    """Adaptive rate limiter that adjusts based on system load"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.sliding_window = SlidingWindowLimiter(redis_client)
        
    async def check_limit(self, key: str, base_limit: int, window_seconds: int) -> Tuple[bool, int, datetime]:
        """Check rate limit with adaptive adjustment"""        # Get system load metrics
        load_factor = await self.get_system_load_factor()
        
        # Adjust limit based on load
        adjusted_limit = int(base_limit * load_factor)
        
        return await self.sliding_window.check_limit(key, adjusted_limit, window_seconds)
    
    async def get_system_load_factor(self) -> float:
        """Get system load factor for adaptive limiting"""        try:
            # Get system metrics from Redis
            metrics_key = "system_metrics"
            metrics = await self.redis_client.hmget(metrics_key, 
                                                  "cpu_usage", "memory_usage", "active_connections")
            
            cpu_usage = float(metrics[0] or 50.0)
            memory_usage = float(metrics[1] or 50.0)
            active_connections = int(metrics[2] or 100)
            
            # Calculate load factor (0.1 to 2.0)
            cpu_factor = 2.0 - (cpu_usage / 50.0)  # Higher CPU = lower limit
            memory_factor = 2.0 - (memory_usage / 50.0)  # Higher memory = lower limit
            connection_factor = max(0.1, min(2.0, 100.0 / active_connections))  # More connections = lower limit
            
            # Weighted average
            load_factor = (cpu_factor * 0.4 + memory_factor * 0.3 + connection_factor * 0.3)
            
            return max(0.1, min(2.0, load_factor))
            
        except Exception as e:
            logger.warning(f"Could not get system load factor: {e}")
            return 1.0  # Default to no adjustment


class PriorityQueue:
    """Priority-based request queue for rate limiting"""    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        
    async def enqueue_request(self, request_id: str, priority: int, user_id: str):
        """Add request to priority queue"""        queue_key = "priority_queue"
        score = priority * 1000 + time.time()  # Higher priority first, then FIFO
        
        request_data = {
            "user_id": user_id,
            "timestamp": time.time(),
            "priority": priority
        }
        
        await self.redis_client.zadd(queue_key, {f"{request_id}:{json.dumps(request_data)}": score})
    
    async def dequeue_request(self) -> Optional[Dict[str, Any]]:
        """Get next request from priority queue"""        queue_key = "priority_queue"
        
        # Get highest priority request
        result = await self.redis_client.zpopmax(queue_key)
        if not result:
            return None
        
        request_data, score = result[0]
        request_id, data_json = request_data.split(":", 1)
        data = json.loads(data_json)
        
        return {
            "request_id": request_id,
            "user_id": data["user_id"],
            "timestamp": data["timestamp"],
            "priority": data["priority"]
        }


class RateLimitingMiddleware:
    """Main rate limiting middleware orchestrator"""    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.cache = CacheManager()
        self.sliding_window = SlidingWindowLimiter(self.redis_client)
        self.token_bucket = TokenBucketLimiter(self.redis_client)
        self.adaptive_limiter = AdaptiveLimiter(self.redis_client)
        self.priority_queue = PriorityQueue(self.redis_client)
        
        # Default configurations
        self.default_configs = {
            "free": RateLimitConfig(
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=1000,
                burst_limit=5
            ),
            "premium": RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_limit=20
            ),
            "enterprise": RateLimitConfig(
                requests_per_minute=1000,
                requests_per_hour=10000,
                requests_per_day=100000,
                burst_limit=100
            )
        }
    
    async def check_rate_limit(self, request: RateLimitRequest) -> RateLimitResult:
        """Main rate limiting check"""        try:
            start_time = time.time()
            
            # Get user's rate limit configuration
            config = await self.get_user_rate_limit_config(request.user_id)
            
            # Generate rate limit key
            limit_key = self.generate_rate_limit_key(request)
            
            # Check concurrent requests
            concurrent_allowed = await self.check_concurrent_limit(request.user_id, config.concurrent_limit)
            if not concurrent_allowed:
                return RateLimitResult(
                    allowed=False,
                    current_usage=config.concurrent_limit,
                    limit=config.concurrent_limit,
                    reset_time=datetime.utcnow() + timedelta(seconds=60),
                    retry_after=60,
                    strategy_used=RateLimitStrategy.FIXED_WINDOW,
                    level=RateLimitLevel.CRITICAL,
                    metadata={"reason": "concurrent_limit_exceeded"}
                )
            
            # Apply priority-based adjustment
            adjusted_config = self.adjust_config_for_priority(config, request.priority)
            
            # Check rate limit based on strategy
            if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                result = await self.check_sliding_window_limit(limit_key, adjusted_config)
            elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                result = await self.check_token_bucket_limit(limit_key, adjusted_config)
            elif config.strategy == RateLimitStrategy.ADAPTIVE:
                result = await self.check_adaptive_limit(limit_key, adjusted_config)
            else:
                result = await self.check_fixed_window_limit(limit_key, adjusted_config)
            
            # Log rate limit event
            await self.log_rate_limit_event(request, result, time.time() - start_time)
            
            # Handle priority queuing if limit exceeded
            if not result.allowed and request.priority > 7:
                await self.priority_queue.enqueue_request(
                    f"{request.user_id}_{int(time.time())}",
                    request.priority,
                    request.user_id
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open - allow request if rate limiting fails
            return RateLimitResult(
                allowed=True,
                current_usage=0,
                limit=1000,
                reset_time=datetime.utcnow() + timedelta(hours=1),
                strategy_used=RateLimitStrategy.FIXED_WINDOW,
                level=RateLimitLevel.NORMAL,
                metadata={"error": str(e), "fail_open": True}
            )
    
    async def check_sliding_window_limit(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Check sliding window rate limit"""        # Check minute limit
        allowed, current, reset_time = await self.sliding_window.check_limit(
            f"{key}:minute", config.requests_per_minute, 60
        )
        
        if not allowed:
            return RateLimitResult(
                allowed=False,
                current_usage=current,
                limit=config.requests_per_minute,
                reset_time=reset_time,
                retry_after=60,
                strategy_used=RateLimitStrategy.SLIDING_WINDOW,
                level=self.calculate_rate_limit_level(current, config.requests_per_minute)
            )
        
        # Check hour limit
        allowed, current, reset_time = await self.sliding_window.check_limit(
            f"{key}:hour", config.requests_per_hour, 3600
        )
        
        if not allowed:
            return RateLimitResult(
                allowed=False,
                current_usage=current,
                limit=config.requests_per_hour,
                reset_time=reset_time,
                retry_after=3600,
                strategy_used=RateLimitStrategy.SLIDING_WINDOW,
                level=self.calculate_rate_limit_level(current, config.requests_per_hour)
            )
        
        return RateLimitResult(
            allowed=True,
            current_usage=current,
            limit=config.requests_per_minute,
            reset_time=reset_time,
            strategy_used=RateLimitStrategy.SLIDING_WINDOW,
            level=self.calculate_rate_limit_level(current, config.requests_per_minute)
        )
    
    async def check_token_bucket_limit(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Check token bucket rate limit"""        refill_rate = config.requests_per_minute / 60.0  # Tokens per second
        
        allowed, tokens_used, reset_time = await self.token_bucket.check_limit(
            key, config.burst_limit, refill_rate
        )
        
        level = RateLimitLevel.CRITICAL if not allowed else RateLimitLevel.NORMAL
        retry_after = None
        if not allowed:
            retry_after = int((reset_time - datetime.utcnow()).total_seconds())
        
        return RateLimitResult(
            allowed=allowed,
            current_usage=tokens_used,
            limit=config.burst_limit,
            reset_time=reset_time,
            retry_after=retry_after,
            strategy_used=RateLimitStrategy.TOKEN_BUCKET,
            level=level
        )
    
    async def check_adaptive_limit(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Check adaptive rate limit"""        allowed, current, reset_time = await self.adaptive_limiter.check_limit(
            f"{key}:adaptive", config.requests_per_minute, 60
        )
        
        level = RateLimitLevel.CRITICAL if not allowed else RateLimitLevel.NORMAL
        
        return RateLimitResult(
            allowed=allowed,
            current_usage=current,
            limit=config.requests_per_minute,
            reset_time=reset_time,
            retry_after=60 if not allowed else None,
            strategy_used=RateLimitStrategy.ADAPTIVE,
            level=level
        )
    
    async def check_fixed_window_limit(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Check fixed window rate limit"""        now = time.time()
        window_start = int(now // 60) * 60  # Minute window
        window_key = f"{key}:fixed:{window_start}"
        
        current_count = await self.redis_client.incr(window_key)
        await self.redis_client.expire(window_key, 60)
        
        allowed = current_count <= config.requests_per_minute
        reset_time = datetime.fromtimestamp(window_start + 60)
        
        return RateLimitResult(
            allowed=allowed,
            current_usage=current_count,
            limit=config.requests_per_minute,
            reset_time=reset_time,
            retry_after=60 if not allowed else None,
            strategy_used=RateLimitStrategy.FIXED_WINDOW,
            level=self.calculate_rate_limit_level(current_count, config.requests_per_minute)
        )
    
    async def check_concurrent_limit(self, user_id: str, limit: int) -> bool:
        """Check concurrent request limit"""        concurrent_key = f"concurrent:{user_id}"
        current_concurrent = await self.redis_client.incr(concurrent_key)
        await self.redis_client.expire(concurrent_key, 300)  # 5 minute expiry
        
        return current_concurrent <= limit
    
    async def release_concurrent_slot(self, user_id: str):
        """Release a concurrent request slot"""        concurrent_key = f"concurrent:{user_id}"
        await self.redis_client.decr(concurrent_key)
    
    def generate_rate_limit_key(self, request: RateLimitRequest) -> str:
        """Generate unique rate limit key"""        key_components = [
            "rate_limit",
            request.user_id,
            request.endpoint.replace("/", "_")
        ]
        
        if request.content_type:
            key_components.append(request.content_type)
        
        return ":".join(key_components)
    
    async def get_user_rate_limit_config(self, user_id: str) -> RateLimitConfig:
        """Get user's rate limit configuration"""        cache_key = f"rate_limit_config:{user_id}"
        
        # Try cache first
        cached_config = await self.cache.get(cache_key)
        if cached_config:
            return RateLimitConfig.parse_raw(cached_config)
        
        # Get user tier from database (mock implementation)
        user_tier = await self.get_user_tier(user_id)
        config = self.default_configs.get(user_tier, self.default_configs["free"])
        
        # Cache for 10 minutes
        await self.cache.set(cache_key, config.json(), expire=600)
        
        return config
    
    async def get_user_tier(self, user_id: str) -> str:
        """Get user's subscription tier"""        # Mock implementation - would query actual database
        return "premium"  # Default to premium for demo
    
    def adjust_config_for_priority(self, config: RateLimitConfig, priority: int) -> RateLimitConfig:
        """Adjust rate limit config based on request priority"""        if priority >= 8:  # High priority requests
            multiplier = 1.5
        elif priority >= 6:  # Medium priority requests
            multiplier = 1.2
        else:  # Low priority requests
            multiplier = 0.8
        
        return RateLimitConfig(
            requests_per_minute=int(config.requests_per_minute * multiplier),
            requests_per_hour=int(config.requests_per_hour * multiplier),
            requests_per_day=int(config.requests_per_day * multiplier),
            burst_limit=int(config.burst_limit * multiplier),
            concurrent_limit=config.concurrent_limit,
            strategy=config.strategy,
            priority_multiplier=multiplier
        )
    
    def calculate_rate_limit_level(self, current: int, limit: int) -> RateLimitLevel:
        """Calculate rate limit severity level"""        usage_percentage = (current / limit) * 100
        
        if usage_percentage >= 95:
            return RateLimitLevel.CRITICAL
        elif usage_percentage >= 80:
            return RateLimitLevel.WARNING
        else:
            return RateLimitLevel.NORMAL
    
    async def log_rate_limit_event(self, request: RateLimitRequest, result: RateLimitResult, 
                                  duration: float):
        """Log rate limiting events for monitoring"""        event = {
            "user_id": request.user_id,
            "endpoint": request.endpoint,
            "allowed": result.allowed,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "strategy": result.strategy_used.value,
            "level": result.level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "duration": duration,
            "priority": request.priority
        }
        
        # Log to Redis for real-time monitoring
        await self.redis_client.lpush("rate_limit_events", json.dumps(event))
        await self.redis_client.ltrim("rate_limit_events", 0, 10000)  # Keep last 10k events


# Factory function for dependency injection
def get_rate_limiting_middleware() -> RateLimitingMiddleware:
    """Get rate limiting middleware instance"""    return RateLimitingMiddleware()


# Decorator for automatic rate limiting
def rate_limit(requests_per_minute: int = 60, strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW):
    """Decorator for automatic rate limiting"""    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from function arguments
            user_id = kwargs.get("user_id") or getattr(args[0], "user_id", "anonymous")
            
            middleware = get_rate_limiting_middleware()
            request = RateLimitRequest(
                user_id=user_id,
                endpoint=func.__name__,
                priority=5
            )
            
            result = await middleware.check_rate_limit(request)
            
            if not result.allowed:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": result.retry_after,
                        "limit": result.limit,
                        "current_usage": result.current_usage
                    }
                )
            
            try:
                return await func(*args, **kwargs)
            finally:
                # Release concurrent slot
                await middleware.release_concurrent_slot(user_id)
        
        return wrapper
    return decorator
