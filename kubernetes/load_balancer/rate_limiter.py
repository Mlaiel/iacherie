"""Rate Limiter for Load Balancer

Advanced rate limiting and traffic throttling system for the IA Influencer
Agent platform, providing DoS protection, API quota management, and
traffic shaping capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import time
import asyncio
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
from collections import defaultdict, deque
import redis
import json

logger = logging.getLogger(__name__)


class LimitType(Enum):
    """
Rate limit types"""

    REQUESTS_PER_SECOND = "requests_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BANDWIDTH_PER_SECOND = "bandwidth_per_second"
    CONCURRENT_CONNECTIONS = "concurrent_connections"


class LimitScope(Enum):
    """Rate limit scope"""

    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_API_KEY = "per_api_key"
    PER_ENDPOINT = "per_endpoint"
    PER_SERVICE = "per_service"


class ActionType(Enum):
    """Action to take when limit is exceeded"""

    DENY = "deny"
    DELAY = "delay"
    THROTTLE = "throttle"
    QUEUE = "queue"
    LOG_ONLY = "log_only"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    name: str
    limit_type: LimitType
    scope: LimitScope
    limit: int
    window_seconds: int
    action: ActionType = ActionType.DENY
    burst_limit: Optional[int] = None
    delay_seconds: float = 1.0
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)
    enabled: bool = True
    priority: int = 0


@dataclass
class RateLimitRequest:
    """
Rate limit request information"""
    client_ip: str
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    service: Optional[str] = None
    request_size: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LimitStatus:
    """
Rate limit status"""
    limit_name: str
    current_count: int
    limit_value: int
    window_start: datetime
    window_end: datetime
    remaining: int
    reset_time: datetime
    is_exceeded: bool


class TokenBucket:
    """
Token bucket algorithm implementation"""
    
    def __init__(self, capacity -> None: int, refill_rate -> None: float) -> None:
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
Consume tokens from bucket"""
        with self.lock:
            now = time.time()
            
            # Add tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
Get bucket status"""
        with self.lock:
            return {
                "capacity": self.capacity,
                "current_tokens": self.tokens,
                "refill_rate": self.refill_rate,
                "last_refill": self.last_refill
            }


class SlidingWindowCounter:
    """Sliding window counter implementation"""
    
    def __init__(self, window_seconds -> None: int, limit -> None: int) -> None:
        self.window_seconds = window_seconds
        self.limit = limit
        self.requests = deque()
        self.lock = threading.Lock()
    
    def add_request(self, timestamp: Optional[datetime] = None) -> bool:
        """
Add request and check if within limit"""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            # Remove old requests outside window
            cutoff_time = timestamp - timedelta(seconds=self.window_seconds)
            while self.requests and self.requests[0] < cutoff_time:
                self.requests.popleft()
            
            # Check if adding this request would exceed limit
            if len(self.requests) >= self.limit:
                return False
            
            # Add request
            self.requests.append(timestamp)
            return True
    
    def get_count(self) -> int:
        """
Get current count in window"""
        with self.lock:
            now = datetime.now()
            cutoff_time = now - timedelta(seconds=self.window_seconds)
            
            # Clean old requests
            while self.requests and self.requests[0] < cutoff_time:
                self.requests.popleft()
            
            return len(self.requests)
    
    def get_status(self) -> Dict[str, Any]:
        """
Get counter status"""
        count = self.get_count()
        now = datetime.now()
        
        return {
            "current_count": count,
            "limit": self.limit,
            "window_seconds": self.window_seconds,
            "remaining": max(0, self.limit - count),
            "window_start": now - timedelta(seconds=self.window_seconds),
            "window_end": now,
            "is_exceeded": count >= self.limit
        }


class DistributedRateLimiter:
    """Distributed rate limiter using Redis"""
    
    def __init__(self, redis_client -> None: redis.Redis) -> None:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def check_limit(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """
Check rate limit using Redis sliding window"""
        try:
            now = time.time()
            pipeline = self.redis.pipeline()
            
            # Remove old entries
            pipeline.zremrangebyscore(key, 0, now - window_seconds)
            
            # Count current entries
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(now): now})
            
            # Set expiration
            pipeline.expire(key, window_seconds + 1)
            
            results = pipeline.execute()
            current_count = results[1]
            
            # Check if limit exceeded
            is_exceeded = current_count >= limit
            
            # Remove the request we just added if limit exceeded
            if is_exceeded:
                self.redis.zrem(key, str(now))
                current_count -= 1
            
            status = {
                "current_count": current_count,
                "limit": limit,
                "remaining": max(0, limit - current_count),
                "reset_time": now + window_seconds,
                "is_exceeded": is_exceeded
            }
            
            return not is_exceeded, status
            
        except Exception as e:
            logger.error(f"Redis rate limiter error: {e}")
            # Fail open - allow request if Redis is unavailable
            return True, {"error": str(e)}


class InMemoryRateLimiter:
    """In-memory rate limiter"""
    
    def __init__(self) -> None:
        self.counters: Dict[str, SlidingWindowCounter] = {}
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = threading.Lock()
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self) -> None:
        """
Cleanup old counters and buckets"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        with self.lock:
            # Remove old counters with no recent activity
            keys_to_remove = []
            for key, counter in self.counters.items():
                if counter.get_count() == 0:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.counters[key]
            
            self.last_cleanup = now
    
    def check_sliding_window_limit(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """
Check sliding window rate limit"""
        self._cleanup_old_entries()
        
        with self.lock:
            if key not in self.counters:
                self.counters[key] = SlidingWindowCounter(window_seconds, limit)
            
            counter = self.counters[key]
        
        allowed = counter.add_request()
        status = counter.get_status()
        
        return allowed, status
    
    def check_token_bucket_limit(self, key: str, capacity: int, refill_rate: float, tokens: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """
Check token bucket rate limit"""
        self._cleanup_old_entries()
        
        with self.lock:
            if key not in self.buckets:
                self.buckets[key] = TokenBucket(capacity, refill_rate)
            
            bucket = self.buckets[key]
        
        allowed = bucket.consume(tokens)
        status = bucket.get_status()
        
        return allowed, status


class RateLimiter:
    """
Enterprise Rate Limiter for Load Balancer"""
    
    def __init__(self, redis_client -> None: Optional[redis.Redis] = None) -> None:
        self.rate_limits: Dict[str, RateLimit] = {}
        self.redis_client = redis_client
        
        if redis_client:
            self.distributed_limiter = DistributedRateLimiter(redis_client)
        else:
            self.distributed_limiter = None
        
        self.memory_limiter = InMemoryRateLimiter()
        self.request_queue = asyncio.Queue()
        self.stats = defaultdict(int)
        self.lock = threading.RLock()
    
    def add_rate_limit(self, rate_limit: RateLimit) -> bool:
        """
Add rate limit configuration"""
        try:
            with self.lock:
                self.rate_limits[rate_limit.name] = rate_limit
            
            logger.info(f"Rate limit {rate_limit.name} added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add rate limit {rate_limit.name}: {e}")
            return False
    
    def remove_rate_limit(self, name: str) -> bool:
        """Remove rate limit configuration"""
        try:
            with self.lock:
                if name in self.rate_limits:
                    del self.rate_limits[name]
                    logger.info(f"Rate limit {name} removed")
                    return True
                else:
                    logger.warning(f"Rate limit {name} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to remove rate limit {name}: {e}")
            return False
    
    def _generate_limit_key(self, rate_limit: RateLimit, request: RateLimitRequest) -> str:
        """Generate unique key for rate limit"""
        key_parts = [rate_limit.name]
        
        if rate_limit.scope == LimitScope.PER_IP:
            key_parts.append(request.client_ip)
        elif rate_limit.scope == LimitScope.PER_USER and request.user_id:
            key_parts.append(f"user:{request.user_id}")
        elif rate_limit.scope == LimitScope.PER_API_KEY and request.api_key:
            key_parts.append(f"api_key:{request.api_key}")
        elif rate_limit.scope == LimitScope.PER_ENDPOINT and request.endpoint:
            key_parts.append(f"endpoint:{request.endpoint}")
        elif rate_limit.scope == LimitScope.PER_SERVICE and request.service:
            key_parts.append(f"service:{request.service}")
        
        return ":".join(key_parts)
    
    def _is_whitelisted(self, rate_limit: RateLimit, request: RateLimitRequest) -> bool:
        """Check if request is whitelisted"""
        if not rate_limit.whitelist:
            return False
        
        # Check IP whitelist
        if request.client_ip in rate_limit.whitelist:
            return True
        
        # Check user whitelist
        if request.user_id and f"user:{request.user_id}" in rate_limit.whitelist:
            return True
        
        # Check API key whitelist
        if request.api_key and f"api_key:{request.api_key}" in rate_limit.whitelist:
            return True
        
        return False
    
    def _is_blacklisted(self, rate_limit: RateLimit, request: RateLimitRequest) -> bool:
        """Check if request is blacklisted"""
        if not rate_limit.blacklist:
            return False
        
        # Check IP blacklist
        if request.client_ip in rate_limit.blacklist:
            return True
        
        # Check user blacklist
        if request.user_id and f"user:{request.user_id}" in rate_limit.blacklist:
            return True
        
        # Check API key blacklist
        if request.api_key and f"api_key:{request.api_key}" in rate_limit.blacklist:
            return True
        
        return False
    
    def check_rate_limits(self, request: RateLimitRequest) -> Tuple[bool, List[LimitStatus], Optional[str]]:
        """Check all applicable rate limits for request"""
        try:
            limit_statuses = []
            blocked_by = None
            
            # Get applicable rate limits sorted by priority
            applicable_limits = [
                limit for limit in self.rate_limits.values()
                if limit.enabled
            ]
            applicable_limits.sort(key=lambda x: x.priority, reverse=True)
            
            for rate_limit in applicable_limits:
                # Check whitelist first
                if self._is_whitelisted(rate_limit, request):
                    continue
                
                # Check blacklist
                if self._is_blacklisted(rate_limit, request):
                    limit_status = LimitStatus(
                        limit_name=rate_limit.name,
                        current_count=0,
                        limit_value=0,
                        window_start=datetime.now(),
                        window_end=datetime.now(),
                        remaining=0,
                        reset_time=datetime.now(),
                        is_exceeded=True
                    )
                    limit_statuses.append(limit_status)
                    blocked_by = rate_limit.name
                    break
                
                # Generate key for this limit
                key = self._generate_limit_key(rate_limit, request)
                
                # Check the specific limit type
                allowed, status_dict = self._check_specific_limit(rate_limit, key, request)
                
                # Convert to LimitStatus
                limit_status = LimitStatus(
                    limit_name=rate_limit.name,
                    current_count=status_dict.get("current_count", 0),
                    limit_value=rate_limit.limit,
                    window_start=status_dict.get("window_start", datetime.now()),
                    window_end=status_dict.get("window_end", datetime.now()),
                    remaining=status_dict.get("remaining", 0),
                    reset_time=datetime.fromtimestamp(status_dict.get("reset_time", time.time())),
                    is_exceeded=not allowed
                )
                
                limit_statuses.append(limit_status)
                
                # If this limit is exceeded, check action
                if not allowed:
                    if rate_limit.action in [ActionType.DENY, ActionType.DELAY, ActionType.THROTTLE]:
                        blocked_by = rate_limit.name
                        break
                    elif rate_limit.action == ActionType.LOG_ONLY:
                        logger.warning(f"Rate limit {rate_limit.name} exceeded for key {key} (log only)")
            
            # Update stats
            self.stats["total_requests"] += 1
            if blocked_by:
                self.stats["blocked_requests"] += 1
                self.stats[f"blocked_by_{blocked_by}"] += 1
            else:
                self.stats["allowed_requests"] += 1
            
            return blocked_by is None, limit_statuses, blocked_by
            
        except Exception as e:
            logger.error(f"Failed to check rate limits: {e}")
            # Fail open - allow request if rate limiting fails
            return True, [], None
    
    def _check_specific_limit(self, rate_limit: RateLimit, key: str, request: RateLimitRequest) -> Tuple[bool, Dict[str, Any]]:
        """Check specific rate limit type"""
        if rate_limit.limit_type == LimitType.REQUESTS_PER_SECOND:
            return self._check_request_limit(key, rate_limit.limit, 1)
        elif rate_limit.limit_type == LimitType.REQUESTS_PER_MINUTE:
            return self._check_request_limit(key, rate_limit.limit, 60)
        elif rate_limit.limit_type == LimitType.REQUESTS_PER_HOUR:
            return self._check_request_limit(key, rate_limit.limit, 3600)
        elif rate_limit.limit_type == LimitType.REQUESTS_PER_DAY:
            return self._check_request_limit(key, rate_limit.limit, 86400)
        elif rate_limit.limit_type == LimitType.BANDWIDTH_PER_SECOND:
            return self._check_bandwidth_limit(key, rate_limit.limit, 1, request.request_size)
        elif rate_limit.limit_type == LimitType.CONCURRENT_CONNECTIONS:
            return self._check_concurrent_limit(key, rate_limit.limit)
        else:
            return True, {"error": f"Unsupported limit type: {rate_limit.limit_type}"}
    
    def _check_request_limit(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, Dict[str, Any]]:
        """Check request-based rate limit"""
        if self.distributed_limiter:
            return self.distributed_limiter.check_limit(key, limit, window_seconds)
        else:
            return self.memory_limiter.check_sliding_window_limit(key, limit, window_seconds)
    
    def _check_bandwidth_limit(self, key: str, limit: int, window_seconds: int, request_size: int) -> Tuple[bool, Dict[str, Any]]:
        """
Check bandwidth-based rate limit"""
        # Use token bucket for bandwidth limiting
        tokens_needed = max(1, request_size // 1024)  # Convert to KB
        refill_rate = limit / window_seconds  # tokens per second
        
        return self.memory_limiter.check_token_bucket_limit(key, limit, refill_rate, tokens_needed)
    
    def _check_concurrent_limit(self, key: str, limit: int) -> Tuple[bool, Dict[str, Any]]:
        """
Check concurrent connections limit"""
        # This would typically be implemented with connection tracking
        # For now, return a simple implementation
        return True, {"current_count": 0, "limit": limit, "remaining": limit}
    
    async def apply_rate_limit_action(self, action: ActionType, delay_seconds: float = 1.0) -> None:
        """Apply rate limiting action"""
        if action == ActionType.DELAY:
            await asyncio.sleep(delay_seconds)
        elif action == ActionType.THROTTLE:
            # Implement throttling by adding to queue
            await self.request_queue.put(time.time())
        elif action == ActionType.QUEUE:
            # Queue the request for later processing
            await self.request_queue.put(time.time())
    
    def configure_platform_rate_limits(self) -> bool:
        """
Configure rate limits for platform services"""
        try:
            rate_limits = [
                # Global API limits
                RateLimit(
                    name="global_api_requests",
                    limit_type=LimitType.REQUESTS_PER_SECOND,
                    scope=LimitScope.GLOBAL,
                    limit=1000,
                    window_seconds=1,
                    action=ActionType.DENY,
                    priority=100
                ),
                
                # Per-IP limits
                RateLimit(
                    name="per_ip_requests",
                    limit_type=LimitType.REQUESTS_PER_MINUTE,
                    scope=LimitScope.PER_IP,
                    limit=100,
                    window_seconds=60,
                    action=ActionType.DELAY,
                    delay_seconds=1.0,
                    priority=90
                ),
                RateLimit(
                    name="per_ip_heavy_requests",
                    limit_type=LimitType.REQUESTS_PER_HOUR,
                    scope=LimitScope.PER_IP,
                    limit=500,
                    window_seconds=3600,
                    action=ActionType.THROTTLE,
                    priority=85
                ),
                
                # Authentication limits
                RateLimit(
                    name="auth_attempts",
                    limit_type=LimitType.REQUESTS_PER_MINUTE,
                    scope=LimitScope.PER_IP,
                    limit=5,
                    window_seconds=60,
                    action=ActionType.DENY,
                    priority=95
                ),
                
                # Upload limits
                RateLimit(
                    name="file_upload_requests",
                    limit_type=LimitType.REQUESTS_PER_MINUTE,
                    scope=LimitScope.PER_USER,
                    limit=10,
                    window_seconds=60,
                    action=ActionType.DELAY,
                    delay_seconds=2.0,
                    priority=80
                ),
                RateLimit(
                    name="file_upload_bandwidth",
                    limit_type=LimitType.BANDWIDTH_PER_SECOND,
                    scope=LimitScope.PER_USER,
                    limit=10240,  # 10MB per second
                    window_seconds=1,
                    action=ActionType.THROTTLE,
                    priority=80
                ),
                
                # Fingerprinting service limits
                RateLimit(
                    name="fingerprinting_requests",
                    limit_type=LimitType.REQUESTS_PER_MINUTE,
                    scope=LimitScope.PER_USER,
                    limit=20,
                    window_seconds=60,
                    action=ActionType.QUEUE,
                    priority=75
                ),
                
                # Protection service limits
                RateLimit(
                    name="protection_alerts",
                    limit_type=LimitType.REQUESTS_PER_SECOND,
                    scope=LimitScope.PER_SERVICE,
                    limit=50,
                    window_seconds=1,
                    action=ActionType.LOG_ONLY,
                    priority=70
                ),
                
                # AI Agent limits
                RateLimit(
                    name="ai_generation_requests",
                    limit_type=LimitType.REQUESTS_PER_HOUR,
                    scope=LimitScope.PER_USER,
                    limit=50,
                    window_seconds=3600,
                    action=ActionType.DELAY,
                    delay_seconds=5.0,
                    priority=75
                ),
                
                # Crawler limits
                RateLimit(
                    name="crawler_requests",
                    limit_type=LimitType.REQUESTS_PER_MINUTE,
                    scope=LimitScope.PER_SERVICE,
                    limit=30,
                    window_seconds=60,
                    action=ActionType.THROTTLE,
                    priority=65
                ),
                
                # Monetization limits
                RateLimit(
                    name="payment_requests",
                    limit_type=LimitType.REQUESTS_PER_HOUR,
                    scope=LimitScope.PER_USER,
                    limit=20,
                    window_seconds=3600,
                    action=ActionType.DENY,
                    priority=85
                ),
                
                # Admin/monitoring exceptions
                RateLimit(
                    name="admin_whitelist",
                    limit_type=LimitType.REQUESTS_PER_SECOND,
                    scope=LimitScope.PER_IP,
                    limit=1000,
                    window_seconds=1,
                    action=ActionType.LOG_ONLY,
                    whitelist=["127.0.0.1", "10.0.0.0/8", "admin"],
                    priority=100
                )
            ]
            
            # Add all rate limits
            for rate_limit in rate_limits:
                self.add_rate_limit(rate_limit)
            
            logger.info(f"Platform rate limits configured: {len(rate_limits)} limits")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform rate limits: {e}")
            return False
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        with self.lock:
            stats = dict(self.stats)
            
            # Add rate limit configurations
            rate_limit_configs = {}
            for name, rate_limit in self.rate_limits.items():
                rate_limit_configs[name] = {
                    "limit_type": rate_limit.limit_type.value,
                    "scope": rate_limit.scope.value,
                    "limit": rate_limit.limit,
                    "window_seconds": rate_limit.window_seconds,
                    "action": rate_limit.action.value,
                    "enabled": rate_limit.enabled,
                    "priority": rate_limit.priority
                }
            
            return {
                "stats": stats,
                "rate_limits": rate_limit_configs,
                "distributed_limiter_enabled": self.distributed_limiter is not None,
                "timestamp": datetime.now().isoformat()
            }
