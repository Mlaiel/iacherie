"""
Rate Limiting Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Enterprise Rate Limiting Engine Service
Advanced rate limiting and throttling for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import hashlib
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
import aioredis
import json
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)

class RateLimitAlgorithm(Enum):
    """Rate limiting algorithm enumeration"""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW_LOG = "sliding_window_log"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"
    ADAPTIVE = "adaptive"
    DISTRIBUTED = "distributed"

class LimitType(Enum):
    """Rate limit type enumeration"""
    REQUESTS_PER_SECOND = "requests_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BANDWIDTH_PER_SECOND = "bandwidth_per_second"
    CONCURRENT_REQUESTS = "concurrent_requests"

class ThrottleAction(Enum):
    """Throttle action enumeration"""
    ALLOW = "allow"
    DENY = "deny"
    DELAY = "delay"
    QUEUE = "queue"

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    name: str
    key_pattern: str  # Pattern for generating keys (e.g., "user:{user_id}", "ip:{ip_address}")
    limit: int
    window_size: int  # Window size in seconds
    limit_type: LimitType = LimitType.REQUESTS_PER_MINUTE
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    burst_size: Optional[int] = None  # For token bucket
    replenish_rate: Optional[float] = None  # For token bucket
    skip_successful_requests: bool = False
    skip_failed_requests: bool = False
    headers_enabled: bool = True
    cost_function: Optional[Callable[[Dict[str, Any]], int]] = None
    conditions: List[Callable[[Dict[str, Any]], bool]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    remaining: int
    reset_time: float
    retry_after: Optional[float] = None
    total_hits: int = 0
    rule_name: str = ""
    cost: int = 1
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class TokenBucket:
    """Token bucket state"""
    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float

@dataclass
class SlidingWindow:
    """Sliding window state"""
    requests: deque
    total_count: int
    window_size: int

@dataclass
class RequestContext:
    """Request context for rate limiting"""
    key: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    request_size: int = 0
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

class RateLimitingEngine:
    """
    Enterprise Rate Limiting Engine
    
    Provides comprehensive rate limiting with:
    - Multiple algorithms (token bucket, sliding window, etc.)
    - Distributed rate limiting with Redis
    - Adaptive rate limiting based on system load
    - Cost-based rate limiting
    - Custom conditions and rules
    - Queue management for delayed requests
    """
    
    def __init__(self, redis_url -> None: Optional[str] = None) -> None:
        """Initialize rate limiting engine"""
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Local state for non-distributed mode
        self.token_buckets: Dict[str, TokenBucket] = {}
        self.sliding_windows: Dict[str, SlidingWindow] = {}
        self.fixed_windows: Dict[str, Dict[int, int]] = defaultdict(dict)
        self.request_queues: Dict[str, deque] = defaultdict(deque)
        self.concurrent_counts: Dict[str, int] = defaultdict(int)
        
        # Rules and configuration
        self.rules: Dict[str, RateLimitRule] = {}
        self.global_settings = {
            "enabled": True,
            "default_algorithm": RateLimitAlgorithm.TOKEN_BUCKET,
            "cleanup_interval": 60.0,
            "adaptive_enabled": False,
            "adaptive_threshold": 0.8,
            "queue_timeout": 30.0
        }
        
        # Performance tracking
        self.performance_metrics: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            "avg_response_time": 0.0,
            "error_rate": 0.0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0
        })
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.queue_processor_task: Optional[asyncio.Task] = None
        
        logger.info("RateLimitingEngine initialized")
    
    async def start(self) -> None:
        """Start the rate limiting engine"""
        try:
            # Connect to Redis if URL provided
            if self.redis_url:
                self.redis_client = aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("Connected to Redis for distributed rate limiting")
            
            # Start background tasks
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.queue_processor_task = asyncio.create_task(self._queue_processor_loop())
            
            logger.info("RateLimitingEngine started successfully")
        except Exception as e:
            logger.error("Failed to start RateLimitingEngine: %s", e)
            raise
    
    async def stop(self) -> None:
        """Stop the rate limiting engine"""
        try:
            self.shutdown_event.set()
            
            # Stop background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            if self.queue_processor_task:
                self.queue_processor_task.cancel()
                try:
                    await self.queue_processor_task
                except asyncio.CancelledError:
                    pass
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                self.redis_client = None
            
            logger.info("RateLimitingEngine stopped successfully")
        except Exception as e:
            logger.error("Error stopping RateLimitingEngine: %s", e)
    
    async def add_rule(self, rule -> None: RateLimitRule) -> None:
        """Add a rate limiting rule"""
        async with self._lock:
            self.rules[rule.name] = rule
        
        logger.info("Added rate limiting rule: %s", rule.name)
    
    async def remove_rule(self, rule_name -> None: str) -> None:
        """Remove a rate limiting rule"""
        async with self._lock:
            self.rules.pop(rule_name, None)
        
        logger.info("Removed rate limiting rule: %s", rule_name)
    
    async def check_rate_limit(self, context: RequestContext) -> RateLimitResult:
        """Check if request is allowed by rate limits"""
        if not self.global_settings["enabled"]:
            return RateLimitResult(
                allowed=True,
                remaining=float('inf'),
                reset_time=0
            )
        
        # Find applicable rules
        applicable_rules = await self._find_applicable_rules(context)
        
        if not applicable_rules:
            return RateLimitResult(
                allowed=True,
                remaining=float('inf'),
                reset_time=0
            )
        
        # Check each rule (all must pass)
        results = []
        for rule in applicable_rules:
            result = await self._check_rule(rule, context)
            results.append(result)
            
            if not result.allowed:
                return result  # Return first failing rule
        
        # All rules passed - return most restrictive result
        most_restrictive = min(results, key=lambda r: r.remaining)
        return most_restrictive
    
    async def consume_quota(self, context -> None: RequestContext, cost -> None: int = 1) -> None:
        """Consume quota for a request"""
        applicable_rules = await self._find_applicable_rules(context)
        
        for rule in applicable_rules:
            key = await self._generate_key(rule, context)
            await self._consume_tokens(rule, key, cost)
    
    async def increment_concurrent(self, context -> None: RequestContext) -> None:
        """Increment concurrent request count"""
        async with self._lock:
            self.concurrent_counts[context.key] += 1
    
    async def decrement_concurrent(self, context -> None: RequestContext) -> None:
        """Decrement concurrent request count"""
        async with self._lock:
            self.concurrent_counts[context.key] = max(0, self.concurrent_counts[context.key] - 1)
    
    async def get_status(self, key: str) -> Dict[str, Any]:
        """Get rate limit status for a key"""
        async with self._lock:
            status = {
                "key": key,
                "token_buckets": {},
                "sliding_windows": {},
                "fixed_windows": {},
                "concurrent_requests": self.concurrent_counts.get(key, 0),
                "queued_requests": len(self.request_queues.get(key, deque()))
            }
            
            # Token bucket status
            if key in self.token_buckets:
                bucket = self.token_buckets[key]
                status["token_buckets"][key] = {
                    "capacity": bucket.capacity,
                    "tokens": bucket.tokens,
                    "last_refill": bucket.last_refill,
                    "refill_rate": bucket.refill_rate
                }
            
            # Sliding window status
            if key in self.sliding_windows:
                window = self.sliding_windows[key]
                status["sliding_windows"][key] = {
                    "total_count": window.total_count,
                    "window_size": window.window_size,
                    "current_requests": len(window.requests)
                }
            
            # Fixed window status
            if key in self.fixed_windows:
                status["fixed_windows"][key] = dict(self.fixed_windows[key])
            
            return status
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics"""
        async with self._lock:
            return {
                "total_rules": len(self.rules),
                "active_buckets": len(self.token_buckets),
                "active_windows": len(self.sliding_windows),
                "total_concurrent": sum(self.concurrent_counts.values()),
                "total_queued": sum(len(queue) for queue in self.request_queues.values()),
                "redis_connected": self.redis_client is not None,
                "settings": dict(self.global_settings),
                "performance": dict(self.performance_metrics)
            }
    
    async def _find_applicable_rules(self, context: RequestContext) -> List[RateLimitRule]:
        """Find rules applicable to the request context"""
        applicable_rules = []
        
        for rule in self.rules.values():
            # Check conditions
            if all(condition(context.metadata) for condition in rule.conditions):
                applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _check_rule(self, rule: RateLimitRule, context: RequestContext) -> RateLimitResult:
        """Check a specific rate limiting rule"""
        key = await self._generate_key(rule, context)
        cost = 1
        
        # Calculate cost if function provided
        if rule.cost_function:
            cost = rule.cost_function(context.metadata)
        
        # Check based on algorithm
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._check_token_bucket(rule, key, cost)
        
        elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_LOG:
            return await self._check_sliding_window_log(rule, key, cost)
        
        elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_COUNTER:
            return await self._check_sliding_window_counter(rule, key, cost)
        
        elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._check_fixed_window(rule, key, cost)
        
        elif rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
            return await self._check_adaptive(rule, key, cost)
        
        elif rule.algorithm == RateLimitAlgorithm.DISTRIBUTED:
            return await self._check_distributed(rule, key, cost)
        
        else:
            # Default to token bucket
            return await self._check_token_bucket(rule, key, cost)
    
    async def _generate_key(self, rule: RateLimitRule, context: RequestContext) -> str:
        """Generate cache key for a rule and context"""
        key_data = {
            "user_id": context.user_id,
            "ip_address": context.ip_address,
            "endpoint": context.endpoint,
            "method": context.method,
            "key": context.key
        }
        
        # Replace placeholders in pattern
        key = rule.key_pattern
        for placeholder, value in key_data.items():
            if value is not None:
                key = key.replace(f"{{{placeholder}}}", str(value))
        
        return f"rate_limit:{rule.name}:{key}"
    
    async def _check_token_bucket(self, rule: RateLimitRule, key: str, cost: int) -> RateLimitResult:
        """Check token bucket rate limit"""
        async with self._lock:
            current_time = time.time()
            
            if key not in self.token_buckets:
                # Initialize bucket
                self.token_buckets[key] = TokenBucket(
                    capacity=rule.burst_size or rule.limit,
                    tokens=rule.burst_size or rule.limit,
                    last_refill=current_time,
                    refill_rate=rule.replenish_rate or (rule.limit / rule.window_size)
                )
            
            bucket = self.token_buckets[key]
            
            # Refill tokens
            time_passed = current_time - bucket.last_refill
            tokens_to_add = time_passed * bucket.refill_rate
            bucket.tokens = min(bucket.capacity, bucket.tokens + tokens_to_add)
            bucket.last_refill = current_time
            
            # Check if enough tokens
            if bucket.tokens >= cost:
                bucket.tokens -= cost
                
                headers = {}
                if rule.headers_enabled:
                    headers = {
                        "X-RateLimit-Limit": str(rule.limit),
                        "X-RateLimit-Remaining": str(int(bucket.tokens)),
                        "X-RateLimit-Reset": str(int(current_time + rule.window_size))
                    }
                
                return RateLimitResult(
                    allowed=True,
                    remaining=int(bucket.tokens),
                    reset_time=current_time + rule.window_size,
                    rule_name=rule.name,
                    cost=cost,
                    headers=headers
                )
            
            else:
                # Calculate retry after
                tokens_needed = cost - bucket.tokens
                retry_after = tokens_needed / bucket.refill_rate
                
                headers = {}
                if rule.headers_enabled:
                    headers = {
                        "X-RateLimit-Limit": str(rule.limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(current_time + rule.window_size)),
                        "Retry-After": str(int(retry_after))
                    }
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + rule.window_size,
                    retry_after=retry_after,
                    rule_name=rule.name,
                    cost=cost,
                    headers=headers
                )
    
    async def _check_sliding_window_log(self, rule: RateLimitRule, key: str, cost: int) -> RateLimitResult:
        """Check sliding window log rate limit"""
        async with self._lock:
            current_time = time.time()
            
            if key not in self.sliding_windows:
                self.sliding_windows[key] = SlidingWindow(
                    requests=deque(),
                    total_count=0,
                    window_size=rule.window_size
                )
            
            window = self.sliding_windows[key]
            
            # Remove old requests
            cutoff_time = current_time - rule.window_size
            while window.requests and window.requests[0] <= cutoff_time:
                window.requests.popleft()
                window.total_count = max(0, window.total_count - 1)
            
            # Check if we can add new request
            if window.total_count + cost <= rule.limit:
                # Add request(s)
                for _ in range(cost):
                    window.requests.append(current_time)
                window.total_count += cost
                
                headers = {}
                if rule.headers_enabled:
                    headers = {
                        "X-RateLimit-Limit": str(rule.limit),
                        "X-RateLimit-Remaining": str(rule.limit - window.total_count),
                        "X-RateLimit-Reset": str(int(current_time + rule.window_size))
                    }
                
                return RateLimitResult(
                    allowed=True,
                    remaining=rule.limit - window.total_count,
                    reset_time=current_time + rule.window_size,
                    total_hits=window.total_count,
                    rule_name=rule.name,
                    cost=cost,
                    headers=headers
                )
            
            else:
                # Calculate when oldest request will expire
                reset_time = window.requests[0] + rule.window_size if window.requests else current_time
                
                headers = {}
                if rule.headers_enabled:
                    headers = {
                        "X-RateLimit-Limit": str(rule.limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time)),
                        "Retry-After": str(int(reset_time - current_time))
                    }
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=reset_time - current_time,
                    total_hits=window.total_count,
                    rule_name=rule.name,
                    cost=cost,
                    headers=headers
                )
    
    async def _check_fixed_window(self, rule: RateLimitRule, key: str, cost: int) -> RateLimitResult:
        """Check fixed window rate limit"""
        async with self._lock:
            current_time = time.time()
            window_start = int(current_time // rule.window_size) * rule.window_size
            
            if key not in self.fixed_windows:
                self.fixed_windows[key] = {}
            
            window_count = self.fixed_windows[key].get(window_start, 0)
            
            if window_count + cost <= rule.limit:
                self.fixed_windows[key][window_start] = window_count + cost
                
                headers = {}
                if rule.headers_enabled:
                    headers = {
                        "X-RateLimit-Limit": str(rule.limit),
                        "X-RateLimit-Remaining": str(rule.limit - window_count - cost),
                        "X-RateLimit-Reset": str(int(window_start + rule.window_size))
                    }
                
                return RateLimitResult(
                    allowed=True,
                    remaining=rule.limit - window_count - cost,
                    reset_time=window_start + rule.window_size,
                    total_hits=window_count + cost,
                    rule_name=rule.name,
                    cost=cost,
                    headers=headers
                )
            
            else:
                reset_time = window_start + rule.window_size
                
                headers = {}
                if rule.headers_enabled:
                    headers = {
                        "X-RateLimit-Limit": str(rule.limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(reset_time)),
                        "Retry-After": str(int(reset_time - current_time))
                    }
                
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=reset_time - current_time,
                    total_hits=window_count,
                    rule_name=rule.name,
                    cost=cost,
                    headers=headers
                )
    
    async def _check_adaptive(self, rule: RateLimitRule, key: str, cost: int) -> RateLimitResult:
        """Check adaptive rate limit based on system performance"""
        # Get current performance metrics
        metrics = self.performance_metrics.get(key, {})
        
        # Adjust limit based on performance
        adaptive_factor = 1.0
        if self.global_settings["adaptive_enabled"]:
            error_rate = metrics.get("error_rate", 0.0)
            cpu_usage = metrics.get("cpu_usage", 0.0)
            
            if error_rate > 0.1 or cpu_usage > self.global_settings["adaptive_threshold"]:
                adaptive_factor = 0.5  # Reduce limit by 50%
            elif error_rate < 0.01 and cpu_usage < 0.5:
                adaptive_factor = 1.5  # Increase limit by 50%
        
        # Create adjusted rule
        adjusted_rule = RateLimitRule(
            name=rule.name,
            key_pattern=rule.key_pattern,
            limit=int(rule.limit * adaptive_factor),
            window_size=rule.window_size,
            limit_type=rule.limit_type,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET  # Use token bucket for adaptive
        )
        
        return await self._check_token_bucket(adjusted_rule, key, cost)
    
    async def _check_distributed(self, rule: RateLimitRule, key: str, cost: int) -> RateLimitResult:
        """Check distributed rate limit using Redis"""
        if not self.redis_client:
            # Fall back to local checking
            return await self._check_token_bucket(rule, key, cost)
        
        try:
            # Use Redis Lua script for atomic rate limiting
            lua_script = """
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local cost = tonumber(ARGV[3])
            local current_time = tonumber(ARGV[4])
            
            local current = redis.call('GET', key)
            if current == false then
                current = 0
            else
                current = tonumber(current)
            end
            
            if current + cost <= limit then
                local new_value = current + cost
                redis.call('SET', key, new_value)
                redis.call('EXPIRE', key, window)
                return {1, limit - new_value, current_time + window}
            else
                local ttl = redis.call('TTL', key)
                if ttl == -1 then
                    ttl = window
                end
                return {0, 0, current_time + ttl}
            end
            """
            
            current_time = time.time()
            result = await self.redis_client.eval(
                lua_script,
                1,
                key,
                rule.limit,
                rule.window_size,
                cost,
                current_time
            )
            
            allowed = bool(result[0])
            remaining = int(result[1])
            reset_time = float(result[2])
            
            headers = {}
            if rule.headers_enabled:
                headers = {
                    "X-RateLimit-Limit": str(rule.limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(int(reset_time))
                }
                
                if not allowed:
                    headers["Retry-After"] = str(int(reset_time - current_time))
            
            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=reset_time - current_time if not allowed else None,
                rule_name=rule.name,
                cost=cost,
                headers=headers
            )
            
        except Exception as e:
            logger.error("Error in distributed rate limiting: %s", e)
            # Fall back to local checking
            return await self._check_token_bucket(rule, key, cost)
    
    async def _consume_tokens(self, rule -> None: RateLimitRule, key -> None: str, cost -> None: int) -> None:
        """Consume tokens without checking (for post-request cleanup)"""
        # This is called after a successful request to ensure accurate counting
        pass
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.global_settings["cleanup_interval"])
                await self._cleanup_expired_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup loop: %s", e)
    
    async def _cleanup_expired_data(self) -> None:
        """Clean up expired rate limiting data"""
        current_time = time.time()
        
        async with self._lock:
            # Cleanup sliding windows
            expired_windows = []
            for key, window in self.sliding_windows.items():
                cutoff_time = current_time - window.window_size
                # Remove old requests
                while window.requests and window.requests[0] <= cutoff_time:
                    window.requests.popleft()
                    window.total_count = max(0, window.total_count - 1)
                
                # Remove empty windows
                if not window.requests:
                    expired_windows.append(key)
            
            for key in expired_windows:
                del self.sliding_windows[key]
            
            # Cleanup fixed windows
            for key, windows in list(self.fixed_windows.items()):
                expired_window_starts = [
                    window_start for window_start in windows.keys()
                    if current_time > window_start + 3600  # Keep windows for 1 hour
                ]
                for window_start in expired_window_starts:
                    del windows[window_start]
                
                if not windows:
                    del self.fixed_windows[key]
    
    async def _queue_processor_loop(self) -> None:
        """Process queued requests"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(1.0)  # Process every second
                await self._process_queued_requests()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in queue processor: %s", e)
    
    async def _process_queued_requests(self) -> None:
        """Process requests in queue"""
        # This is a placeholder for queue processing logic
        # In a full implementation, this would handle delayed requests
        pass

# Global rate limiting engine instance
_rate_limiter: Optional[RateLimitingEngine] = None

async def get_rate_limiter(redis_url: Optional[str] = None) -> RateLimitingEngine:
    """Get global rate limiting engine instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimitingEngine(redis_url)
        await _rate_limiter.start()
    return _rate_limiter

async def shutdown_rate_limiter() -> None:
    """Shutdown global rate limiting engine"""
    global _rate_limiter
    if _rate_limiter:
        await _rate_limiter.stop()
        _rate_limiter = None

if __name__ == "__main__":
    async def test_rate_limiter() -> None:
        """Test rate limiting engine functionality"""
        engine = RateLimitingEngine()
        await engine.start()
        
        try:
            # Add test rule
            rule = RateLimitRule(
                name="api_limit",
                key_pattern="api:{ip_address}",
                limit=10,
                window_size=60,
                algorithm=RateLimitAlgorithm.TOKEN_BUCKET
            )
            
            await engine.add_rule(rule)
            
            # Test requests
            context = RequestContext(
                key="test_key",
                ip_address="192.168.1.100"
            )
            
            # Make several requests
            for i in range(15):
                result = await engine.check_rate_limit(context)
                print(f"Request {i+1}: allowed={result.allowed}, remaining={result.remaining}")
                
                if result.allowed:
                    await engine.consume_quota(context)
                
                await asyncio.sleep(0.1)
            
            # Get status
            status = await engine.get_status("rate_limit:api_limit:api:192.168.1.100")
            print(f"Status: {status}")
            
            # Get metrics
            metrics = await engine.get_metrics()
            print(f"Metrics: {metrics}")
            
        finally:
            await engine.stop()
    
    # Run test
    asyncio.run(test_rate_limiter())