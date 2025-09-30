"""💳 Gateway Rate Limiter
========================

Enterprise-grade rate limiting and throttling system for payment gateway
with DDoS protection, fair usage enforcement, and provider quota management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import redis.asyncio as redis
from collections import defaultdict, deque
import hashlib
import json

logger = logging.getLogger(__name__)


class RateLimitType(Enum):
    """Rate limit types"""
    PER_SECOND = "per_second"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"
    BURST = "burst"
    SLIDING_WINDOW = "sliding_window"


class LimitScope(Enum):
    """Rate limiting scope"""
    GLOBAL = "global"
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    PROVIDER = "provider"


class ThrottleAction(Enum):
    """Actions when rate limit is exceeded"""
    REJECT = "reject"
    DELAY = "delay"
    QUEUE = "queue"
    REDIRECT = "redirect"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit: int
    window_seconds: int
    limit_type: RateLimitType
    scope: LimitScope
    action: ThrottleAction = ThrottleAction.REJECT
    burst_allowance: int = 0
    reset_on_success: bool = False


@dataclass
class RateLimitState:
    """Current rate limit state"""
    key: str
    count: int
    window_start: float
    last_request: float
    burst_used: int = 0
    violations: int = 0
    blocked_until: Optional[float] = None


@dataclass
class RateLimitResult:
    """Rate limiting result"""
    allowed: bool
    limit: RateLimit
    current_count: int
    remaining: int
    reset_time: float
    retry_after: Optional[int] = None
    reason: Optional[str] = None


class GatewayRateLimiter:
    """Enterprise gateway rate limiting system"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Default rate limits
        self.default_limits = {
            LimitScope.GLOBAL: [
                RateLimit(1000, 60, RateLimitType.PER_MINUTE, LimitScope.GLOBAL),
                RateLimit(50, 1, RateLimitType.PER_SECOND, LimitScope.GLOBAL),
                RateLimit(10000, 3600, RateLimitType.PER_HOUR, LimitScope.GLOBAL)
            ],
            LimitScope.CUSTOMER: [
                RateLimit(100, 60, RateLimitType.PER_MINUTE, LimitScope.CUSTOMER),
                RateLimit(5, 1, RateLimitType.PER_SECOND, LimitScope.CUSTOMER),
                RateLimit(1000, 3600, RateLimitType.PER_HOUR, LimitScope.CUSTOMER)
            ],
            LimitScope.IP_ADDRESS: [
                RateLimit(50, 60, RateLimitType.PER_MINUTE, LimitScope.IP_ADDRESS),
                RateLimit(2, 1, RateLimitType.PER_SECOND, LimitScope.IP_ADDRESS),
                RateLimit(500, 3600, RateLimitType.PER_HOUR, LimitScope.IP_ADDRESS)
            ],
            LimitScope.PROVIDER: [
                RateLimit(500, 60, RateLimitType.PER_MINUTE, LimitScope.PROVIDER),
                RateLimit(10, 1, RateLimitType.PER_SECOND, LimitScope.PROVIDER)
            ]
        }
        
        # Custom limits per identifier
        self.custom_limits: Dict[str, List[RateLimit]] = {}
        
        # In-memory fallback for when Redis is unavailable
        self.memory_store: Dict[str, RateLimitState] = {}
        self.memory_cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        # DDoS detection
        self.ddos_threshold = 1000  # requests per minute from single IP
        self.ddos_block_duration = 3600  # 1 hour block
        
        # Provider quotas
        self.provider_quotas = {
            'stripe': {'daily': 100000, 'hourly': 5000},
            'paypal': {'daily': 50000, 'hourly': 2500},
            'wise': {'daily': 10000, 'hourly': 500},
            'crypto': {'daily': 1000, 'hourly': 100}
        }

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Rate limiter Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed, using memory store: {e}")
            self.redis_client = None

    async def check_rate_limit(self, 
                             identifier: str, 
                             scope: LimitScope,
                             ip_address: Optional[str] = None,
                             provider: Optional[str] = None) -> RateLimitResult:
        """Check if request is within rate limits"""
        
        # Get applicable rate limits
        limits = self._get_applicable_limits(identifier, scope)
        
        # Check each limit
        for limit in limits:
            result = await self._check_single_limit(identifier, limit, ip_address, provider)
            if not result.allowed:
                return result
        
        # Check DDoS protection if IP provided
        if ip_address:
            ddos_result = await self._check_ddos_protection(ip_address)
            if not ddos_result.allowed:
                return ddos_result
        
        # Check provider quotas if provider specified
        if provider:
            quota_result = await self._check_provider_quota(provider)
            if not quota_result.allowed:
                return quota_result
        
        # All checks passed
        return RateLimitResult(
            allowed=True,
            limit=limits[0] if limits else None,
            current_count=0,
            remaining=limits[0].limit if limits else 0,
            reset_time=time.time() + (limits[0].window_seconds if limits else 60)
        )

    async def _check_single_limit(self, 
                                identifier: str, 
                                limit: RateLimit,
                                ip_address: Optional[str] = None,
                                provider: Optional[str] = None) -> RateLimitResult:
        """Check a single rate limit"""
        
        # Generate unique key for this limit
        key = self._generate_limit_key(identifier, limit, ip_address, provider)
        
        # Get current state
        state = await self._get_rate_limit_state(key)
        current_time = time.time()
        
        # Check if window has reset
        if current_time >= state.window_start + limit.window_seconds:
            state.window_start = current_time
            state.count = 0
            state.burst_used = 0
        
        # Check if blocked
        if state.blocked_until and current_time < state.blocked_until:
            return RateLimitResult(
                allowed=False,
                limit=limit,
                current_count=state.count,
                remaining=0,
                reset_time=state.blocked_until,
                retry_after=int(state.blocked_until - current_time),
                reason="Temporarily blocked due to rate limit violations"
            )
        
        # Check burst allowance
        if limit.burst_allowance > 0 and state.burst_used < limit.burst_allowance:
            # Allow burst request
            state.burst_used += 1
            state.count += 1
            state.last_request = current_time
            await self._save_rate_limit_state(key, state)
            
            return RateLimitResult(
                allowed=True,
                limit=limit,
                current_count=state.count,
                remaining=max(0, limit.limit - state.count),
                reset_time=state.window_start + limit.window_seconds
            )
        
        # Check main limit
        if state.count >= limit.limit:
            # Rate limit exceeded
            state.violations += 1
            
            # Apply throttle action
            if limit.action == ThrottleAction.REJECT:
                await self._save_rate_limit_state(key, state)
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    current_count=state.count,
                    remaining=0,
                    reset_time=state.window_start + limit.window_seconds,
                    retry_after=int(state.window_start + limit.window_seconds - current_time),
                    reason="Rate limit exceeded"
                )
            
            elif limit.action == ThrottleAction.DELAY:
                # Implement delay (in real system, this would queue the request)
                delay_seconds = min(60, state.violations * 2)  # Progressive delay
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    current_count=state.count,
                    remaining=0,
                    reset_time=state.window_start + limit.window_seconds,
                    retry_after=delay_seconds,
                    reason=f"Rate limit exceeded - retry after {delay_seconds}s delay"
                )
        
        # Request allowed
        state.count += 1
        state.last_request = current_time
        await self._save_rate_limit_state(key, state)
        
        return RateLimitResult(
            allowed=True,
            limit=limit,
            current_count=state.count,
            remaining=max(0, limit.limit - state.count),
            reset_time=state.window_start + limit.window_seconds
        )

    async def _check_ddos_protection(self, ip_address: str) -> RateLimitResult:
        """Check DDoS protection for IP address"""
        ddos_key = f"ddos:{ip_address}"
        
        # Check if IP is currently blocked
        if self.redis_client:
            blocked_until = await self.redis_client.get(f"{ddos_key}:blocked")
            if blocked_until:
                block_time = float(blocked_until)
                if time.time() < block_time:
                    return RateLimitResult(
                        allowed=False,
                        limit=None,
                        current_count=0,
                        remaining=0,
                        reset_time=block_time,
                        retry_after=int(block_time - time.time()),
                        reason="IP address blocked due to DDoS protection"
                    )
        
        # Check request rate for DDoS detection
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        if self.redis_client:
            # Use Redis for accurate tracking
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(ddos_key, 0, window_start)
            pipe.zadd(ddos_key, {str(current_time): current_time})
            pipe.zcard(ddos_key)
            pipe.expire(ddos_key, 120)
            results = await pipe.execute()
            
            request_count = results[2]
        else:
            # Fallback to memory store
            if ddos_key not in self.memory_store:
                self.memory_store[ddos_key] = RateLimitState(
                    key=ddos_key,
                    count=0,
                    window_start=current_time,
                    last_request=current_time
                )
            
            state = self.memory_store[ddos_key]
            if current_time >= state.window_start + 60:
                state.window_start = current_time
                state.count = 0
            
            state.count += 1
            request_count = state.count
        
        # Check if DDoS threshold exceeded
        if request_count > self.ddos_threshold:
            # Block IP
            block_until = current_time + self.ddos_block_duration
            
            if self.redis_client:
                await self.redis_client.setex(f"{ddos_key}:blocked", 
                                            self.ddos_block_duration, 
                                            str(block_until))
            
            logger.warning(f"DDoS protection triggered for IP {ip_address}")
            
            return RateLimitResult(
                allowed=False,
                limit=None,
                current_count=request_count,
                remaining=0,
                reset_time=block_until,
                retry_after=self.ddos_block_duration,
                reason="DDoS protection activated - IP blocked"
            )
        
        return RateLimitResult(
            allowed=True,
            limit=None,
            current_count=request_count,
            remaining=max(0, self.ddos_threshold - request_count),
            reset_time=window_start + 60
        )

    async def _check_provider_quota(self, provider: str) -> RateLimitResult:
        """Check provider-specific quotas"""
        if provider not in self.provider_quotas:
            return RateLimitResult(
                allowed=True,
                limit=None,
                current_count=0,
                remaining=1000,
                reset_time=time.time() + 3600
            )
        
        quotas = self.provider_quotas[provider]
        current_time = time.time()
        
        # Check hourly quota
        hourly_key = f"provider:{provider}:hourly"
        hourly_state = await self._get_rate_limit_state(hourly_key)
        
        if current_time >= hourly_state.window_start + 3600:
            hourly_state.window_start = current_time
            hourly_state.count = 0
        
        if hourly_state.count >= quotas['hourly']:
            return RateLimitResult(
                allowed=False,
                limit=None,
                current_count=hourly_state.count,
                remaining=0,
                reset_time=hourly_state.window_start + 3600,
                retry_after=int(hourly_state.window_start + 3600 - current_time),
                reason=f"Provider {provider} hourly quota exceeded"
            )
        
        # Check daily quota
        daily_key = f"provider:{provider}:daily"
        daily_state = await self._get_rate_limit_state(daily_key)
        
        if current_time >= daily_state.window_start + 86400:
            daily_state.window_start = current_time
            daily_state.count = 0
        
        if daily_state.count >= quotas['daily']:
            return RateLimitResult(
                allowed=False,
                limit=None,
                current_count=daily_state.count,
                remaining=0,
                reset_time=daily_state.window_start + 86400,
                retry_after=int(daily_state.window_start + 86400 - current_time),
                reason=f"Provider {provider} daily quota exceeded"
            )
        
        # Update quotas
        hourly_state.count += 1
        daily_state.count += 1
        await self._save_rate_limit_state(hourly_key, hourly_state)
        await self._save_rate_limit_state(daily_key, daily_state)
        
        return RateLimitResult(
            allowed=True,
            limit=None,
            current_count=hourly_state.count,
            remaining=min(quotas['hourly'] - hourly_state.count,
                         quotas['daily'] - daily_state.count),
            reset_time=min(hourly_state.window_start + 3600,
                          daily_state.window_start + 86400)
        )

    def _get_applicable_limits(self, identifier: str, scope: LimitScope) -> List[RateLimit]:
        """Get applicable rate limits for identifier and scope"""
        # Check for custom limits first
        if identifier in self.custom_limits:
            return self.custom_limits[identifier]
        
        # Return default limits for scope
        return self.default_limits.get(scope, [])

    def _generate_limit_key(self, 
                          identifier: str, 
                          limit: RateLimit,
                          ip_address: Optional[str] = None,
                          provider: Optional[str] = None) -> str:
        """Generate unique key for rate limit"""
        key_parts = [
            f"ratelimit",
            limit.scope.value,
            limit.limit_type.value,
            str(limit.window_seconds)
        ]
        
        if limit.scope == LimitScope.IP_ADDRESS and ip_address:
            key_parts.append(ip_address)
        elif limit.scope == LimitScope.PROVIDER and provider:
            key_parts.append(provider)
        else:
            key_parts.append(identifier)
        
        return ":".join(key_parts)

    async def _get_rate_limit_state(self, key: str) -> RateLimitState:
        """Get rate limit state from storage"""
        current_time = time.time()
        
        if self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    state_data = json.loads(data)
                    return RateLimitState(
                        key=key,
                        count=state_data.get('count', 0),
                        window_start=state_data.get('window_start', current_time),
                        last_request=state_data.get('last_request', current_time),
                        burst_used=state_data.get('burst_used', 0),
                        violations=state_data.get('violations', 0),
                        blocked_until=state_data.get('blocked_until')
                    )
            except Exception as e:
                logger.warning(f"Failed to get state from Redis: {e}")
        
        # Return default state
        return RateLimitState(
            key=key,
            count=0,
            window_start=current_time,
            last_request=current_time
        )

    async def _save_rate_limit_state(self, key: str, state: RateLimitState):
        """Save rate limit state to storage"""
        state_data = {
            'count': state.count,
            'window_start': state.window_start,
            'last_request': state.last_request,
            'burst_used': state.burst_used,
            'violations': state.violations,
            'blocked_until': state.blocked_until
        }
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    key, 
                    3600,  # 1 hour expiry
                    json.dumps(state_data)
                )
            except Exception as e:
                logger.warning(f"Failed to save state to Redis: {e}")
                self.memory_store[key] = state
        else:
            self.memory_store[key] = state
            
        # Cleanup memory store periodically
        current_time = time.time()
        if current_time - self.last_cleanup > self.memory_cleanup_interval:
            await self._cleanup_memory_store()
            self.last_cleanup = current_time

    async def _cleanup_memory_store(self):
        """Clean up expired entries from memory store"""
        current_time = time.time()
        expired_keys = []
        
        for key, state in self.memory_store.items():
            # Remove entries older than 2 hours
            if current_time - state.last_request > 7200:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_store[key]
        
        logger.debug(f"Cleaned up {len(expired_keys)} expired rate limit entries")

    async def set_custom_limits(self, identifier: str, limits: List[RateLimit]):
        """Set custom rate limits for specific identifier"""
        self.custom_limits[identifier] = limits

    async def remove_custom_limits(self, identifier: str):
        """Remove custom rate limits for identifier"""
        if identifier in self.custom_limits:
            del self.custom_limits[identifier]

    async def get_rate_limit_status(self, identifier: str, scope: LimitScope) -> Dict[str, Any]:
        """Get current rate limit status for identifier"""
        limits = self._get_applicable_limits(identifier, scope)
        status = []
        
        for limit in limits:
            key = self._generate_limit_key(identifier, limit)
            state = await self._get_rate_limit_state(key)
            
            status.append({
                'limit_type': limit.limit_type.value,
                'scope': limit.scope.value,
                'limit': limit.limit,
                'window_seconds': limit.window_seconds,
                'current_count': state.count,
                'remaining': max(0, limit.limit - state.count),
                'reset_time': state.window_start + limit.window_seconds,
                'violations': state.violations
            })
        
        return {
            'identifier': identifier,
            'scope': scope.value,
            'limits': status,
            'timestamp': time.time()
        }

    async def reset_rate_limit(self, identifier: str, scope: LimitScope):
        """Reset rate limits for identifier"""
        limits = self._get_applicable_limits(identifier, scope)
        
        for limit in limits:
            key = self._generate_limit_key(identifier, limit)
            
            if self.redis_client:
                await self.redis_client.delete(key)
            
            if key in self.memory_store:
                del self.memory_store[key]

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics"""
        stats = {
            'total_memory_entries': len(self.memory_store),
            'custom_limits_count': len(self.custom_limits),
            'redis_connected': self.redis_client is not None
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats['redis_used_memory'] = info.get('used_memory_human', 'N/A')
                stats['redis_connected_clients'] = info.get('connected_clients', 0)
            except Exception as e:
                logger.warning(f"Failed to get Redis stats: {e}")
        
        return stats