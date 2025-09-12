"""
Enterprise Rate Limiter for ML Services
Security + Backend Senior implementation with adaptive rate limiting
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import time
from collections import defaultdict, deque
import hashlib
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class CreatorTier(Enum):
    """Creator subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    VIP = "vip"


class RateLimitScope(Enum):
    """Rate limit scopes"""
    GLOBAL = "global"
    USER = "user"
    IP = "ip"
    API_KEY = "api_key"
    CREATOR_TYPE = "creator_type"
    SERVICE = "service"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    scope: RateLimitScope
    strategy: RateLimitStrategy
    requests_per_window: int
    window_size: timedelta
    burst_capacity: Optional[int] = None
    creator_tier_multiplier: Dict[CreatorTier, float] = field(default_factory=dict)
    priority_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class RateLimitViolation:
    """Rate limit violation record"""
    violation_id: str
    identifier: str
    scope: RateLimitScope
    requested_count: int
    allowed_count: int
    timestamp: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    creator_type: Optional[str] = None
    severity: str = "medium"


@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    total_requests: int = 0
    allowed_requests: int = 0
    blocked_requests: int = 0
    violations: int = 0
    avg_response_time: float = 0.0
    peak_requests_per_second: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class RateLimiter:
    """Enterprise adaptive rate limiter for ML services"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rate_limits: Dict[str, RateLimit] = {}
        self.request_counters: Dict[str, deque] = defaultdict(deque)
        self.token_buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.violations: List[RateLimitViolation] = []
        self.metrics = RateLimitMetrics()
        
        # Creator-specific rate limits
        self.creator_limits = {
            'musicians': {
                'audio_processing': 100,  # requests per minute
                'model_inference': 500,
                'data_upload': 50,
                'collaboration_requests': 20
            },
            'photographers': {
                'image_processing': 200,
                'storage_operations': 1000,
                'portfolio_updates': 10,
                'gallery_views': 5000
            },
            'bloggers': {
                'content_generation': 50,
                'seo_analysis': 100,
                'publishing': 20,
                'analytics_queries': 200
            },
            'influencers': {
                'multi_platform_sync': 30,
                'analytics_queries': 300,
                'content_scheduling': 100,
                'engagement_tracking': 1000
            },
            'comedians': {
                'video_processing': 20,
                'timing_analysis': 50,
                'performance_metrics': 100,
                'venue_matching': 10
            }
        }
        
        # Tier multipliers
        self.tier_multipliers = {
            CreatorTier.FREE: 1.0,
            CreatorTier.BASIC: 2.0,
            CreatorTier.PREMIUM: 5.0,
            CreatorTier.ENTERPRISE: 10.0,
            CreatorTier.VIP: 20.0
        }
        
    async def initialize(self) -> bool:
        """Initialize rate limiter"""
        try:
            logger.info("Initializing Rate Limiter...")
            
            # Setup default rate limits
            await self._setup_default_limits()
            
            # Initialize monitoring
            await self._setup_monitoring()
            
            # Start cleanup tasks
            asyncio.create_task(self._cleanup_expired_entries())
            
            logger.info("Rate Limiter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Rate Limiter: {e}")
            return False
    
    async def check_rate_limit(self, 
                             identifier: str,
                             scope: RateLimitScope,
                             creator_type: Optional[str] = None,
                             creator_tier: Optional[CreatorTier] = None,
                             service_type: Optional[str] = None) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        try:
            # Get applicable rate limit
            limit_key = f"{scope.value}_{service_type or 'default'}"
            rate_limit = self.rate_limits.get(limit_key)
            
            if not rate_limit:
                # No rate limit configured, allow request
                return {
                    'allowed': True,
                    'remaining': float('inf'),
                    'reset_time': None,
                    'retry_after': None
                }
            
            # Apply creator-specific adjustments
            adjusted_limit = await self._get_adjusted_limit(
                rate_limit, creator_type, creator_tier, service_type
            )
            
            # Check based on strategy
            result = await self._check_strategy(
                identifier, adjusted_limit, scope
            )
            
            # Update metrics
            await self._update_metrics(result)
            
            # Log violation if blocked
            if not result['allowed']:
                await self._log_violation(identifier, scope, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request on error
            return {'allowed': True, 'error': str(e)}
    
    async def add_rate_limit(self, 
                           service_type: str,
                           scope: RateLimitScope,
                           strategy: RateLimitStrategy,
                           requests_per_window: int,
                           window_size: timedelta) -> bool:
        """Add new rate limit configuration"""
        try:
            limit_key = f"{scope.value}_{service_type}"
            
            rate_limit = RateLimit(
                scope=scope,
                strategy=strategy,
                requests_per_window=requests_per_window,
                window_size=window_size,
                creator_tier_multiplier=self.tier_multipliers.copy()
            )
            
            self.rate_limits[limit_key] = rate_limit
            
            logger.info(f"Added rate limit for {service_type}: {requests_per_window} requests per {window_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add rate limit: {e}")
            return False
    
    async def update_creator_limits(self, 
                                  creator_type: str,
                                  service_limits: Dict[str, int]) -> bool:
        """Update rate limits for specific creator type"""
        try:
            if creator_type not in self.creator_limits:
                self.creator_limits[creator_type] = {}
            
            self.creator_limits[creator_type].update(service_limits)
            
            logger.info(f"Updated rate limits for {creator_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update creator limits: {e}")
            return False
    
    async def get_violations(self, 
                           time_period: Optional[timedelta] = None,
                           severity_filter: Optional[str] = None) -> List[RateLimitViolation]:
        """Get rate limit violations"""
        try:
            violations = self.violations.copy()
            
            # Filter by time period
            if time_period:
                cutoff_time = datetime.utcnow() - time_period
                violations = [v for v in violations if v.timestamp >= cutoff_time]
            
            # Filter by severity
            if severity_filter:
                violations = [v for v in violations if v.severity == severity_filter]
            
            return violations
            
        except Exception as e:
            logger.error(f"Failed to get violations: {e}")
            return []
    
    async def get_metrics(self) -> RateLimitMetrics:
        """Get rate limiting metrics"""
        try:
            # Update current metrics
            await self._calculate_current_metrics()
            return self.metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return RateLimitMetrics()
    
    async def reset_limits(self, identifier: str, scope: RateLimitScope) -> bool:
        """Reset rate limits for specific identifier"""
        try:
            key = f"{scope.value}_{identifier}"
            
            # Clear request counters
            if key in self.request_counters:
                self.request_counters[key].clear()
            
            # Reset token buckets
            if key in self.token_buckets:
                self.token_buckets[key] = {}
            
            logger.info(f"Reset rate limits for {identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset limits: {e}")
            return False
    
    async def _setup_default_limits(self):
        """Setup default rate limits"""
        # Global API limits
        await self.add_rate_limit(
            "api_general", 
            RateLimitScope.GLOBAL, 
            RateLimitStrategy.SLIDING_WINDOW,
            10000,  # 10k requests
            timedelta(minutes=1)
        )
        
        # User-specific limits
        await self.add_rate_limit(
            "user_general",
            RateLimitScope.USER,
            RateLimitStrategy.TOKEN_BUCKET,
            1000,  # 1k requests
            timedelta(minutes=1)
        )
        
        # Service-specific limits for each creator type
        for creator_type, services in self.creator_limits.items():
            for service, limit in services.items():
                await self.add_rate_limit(
                    f"{creator_type}_{service}",
                    RateLimitScope.CREATOR_TYPE,
                    RateLimitStrategy.ADAPTIVE,
                    limit,
                    timedelta(minutes=1)
                )
    
    async def _setup_monitoring(self):
        """Setup rate limit monitoring"""
        # Initialize metrics collection
        self.metrics = RateLimitMetrics()
    
    async def _get_adjusted_limit(self, 
                                rate_limit: RateLimit,
                                creator_type: Optional[str],
                                creator_tier: Optional[CreatorTier],
                                service_type: Optional[str]) -> RateLimit:
        """Get rate limit adjusted for creator type and tier"""
        adjusted_limit = rate_limit
        
        # Apply tier multiplier
        if creator_tier and creator_tier in rate_limit.creator_tier_multiplier:
            multiplier = rate_limit.creator_tier_multiplier[creator_tier]
            adjusted_limit.requests_per_window = int(
                adjusted_limit.requests_per_window * multiplier
            )
        
        # Apply creator-specific adjustments
        if creator_type and service_type:
            creator_service_key = f"{creator_type}_{service_type}"
            if creator_service_key in self.creator_limits.get(creator_type, {}):
                adjusted_limit.requests_per_window = self.creator_limits[creator_type][creator_service_key]
        
        return adjusted_limit
    
    async def _check_strategy(self, 
                            identifier: str,
                            rate_limit: RateLimit,
                            scope: RateLimitScope) -> Dict[str, Any]:
        """Check rate limit based on strategy"""
        key = f"{scope.value}_{identifier}"
        current_time = time.time()
        
        if rate_limit.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(key, rate_limit, current_time)
        elif rate_limit.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(key, rate_limit, current_time)
        elif rate_limit.strategy == RateLimitStrategy.ADAPTIVE:
            return await self._check_adaptive(key, rate_limit, current_time)
        else:
            # Default to fixed window
            return await self._check_fixed_window(key, rate_limit, current_time)
    
    async def _check_sliding_window(self, 
                                  key: str,
                                  rate_limit: RateLimit,
                                  current_time: float) -> Dict[str, Any]:
        """Check sliding window rate limit"""
        window_start = current_time - rate_limit.window_size.total_seconds()
        
        # Remove expired entries
        counter = self.request_counters[key]
        while counter and counter[0] < window_start:
            counter.popleft()
        
        # Check if within limit
        allowed = len(counter) < rate_limit.requests_per_window
        
        if allowed:
            counter.append(current_time)
        
        remaining = max(0, rate_limit.requests_per_window - len(counter))
        reset_time = window_start + rate_limit.window_size.total_seconds()
        
        return {
            'allowed': allowed,
            'remaining': remaining,
            'reset_time': datetime.fromtimestamp(reset_time),
            'retry_after': None if allowed else int(reset_time - current_time)
        }
    
    async def _check_token_bucket(self, 
                                key: str,
                                rate_limit: RateLimit,
                                current_time: float) -> Dict[str, Any]:
        """Check token bucket rate limit"""
        bucket = self.token_buckets[key]
        
        if 'tokens' not in bucket:
            bucket['tokens'] = rate_limit.requests_per_window
            bucket['last_refill'] = current_time
        
        # Refill tokens
        time_passed = current_time - bucket['last_refill']
        refill_rate = rate_limit.requests_per_window / rate_limit.window_size.total_seconds()
        tokens_to_add = time_passed * refill_rate
        
        bucket['tokens'] = min(
            rate_limit.requests_per_window,
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = current_time
        
        # Check if token available
        allowed = bucket['tokens'] >= 1
        
        if allowed:
            bucket['tokens'] -= 1
        
        return {
            'allowed': allowed,
            'remaining': int(bucket['tokens']),
            'reset_time': None,
            'retry_after': None if allowed else int(1 / refill_rate)
        }
    
    async def _check_adaptive(self, 
                            key: str,
                            rate_limit: RateLimit,
                            current_time: float) -> Dict[str, Any]:
        """Check adaptive rate limit (ML-based)"""
        # For now, use sliding window with dynamic adjustment
        base_result = await self._check_sliding_window(key, rate_limit, current_time)
        
        # TODO: Implement ML-based adaptive adjustment
        # This could analyze patterns and adjust limits dynamically
        
        return base_result
    
    async def _check_fixed_window(self, 
                                key: str,
                                rate_limit: RateLimit,
                                current_time: float) -> Dict[str, Any]:
        """Check fixed window rate limit"""
        window_start = int(current_time // rate_limit.window_size.total_seconds())
        window_key = f"{key}_{window_start}"
        
        counter = self.request_counters[window_key]
        allowed = len(counter) < rate_limit.requests_per_window
        
        if allowed:
            counter.append(current_time)
        
        remaining = max(0, rate_limit.requests_per_window - len(counter))
        reset_time = (window_start + 1) * rate_limit.window_size.total_seconds()
        
        return {
            'allowed': allowed,
            'remaining': remaining,
            'reset_time': datetime.fromtimestamp(reset_time),
            'retry_after': None if allowed else int(reset_time - current_time)
        }
    
    async def _update_metrics(self, result: Dict[str, Any]):
        """Update rate limiting metrics"""
        self.metrics.total_requests += 1
        
        if result['allowed']:
            self.metrics.allowed_requests += 1
        else:
            self.metrics.blocked_requests += 1
            self.metrics.violations += 1
    
    async def _log_violation(self, 
                           identifier: str,
                           scope: RateLimitScope,
                           result: Dict[str, Any]):
        """Log rate limit violation"""
        violation = RateLimitViolation(
            violation_id=str(uuid.uuid4()),
            identifier=identifier,
            scope=scope,
            requested_count=1,
            allowed_count=result.get('remaining', 0),
            timestamp=datetime.utcnow()
        )
        
        self.violations.append(violation)
        
        # Keep only recent violations (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.violations = [v for v in self.violations if v.timestamp >= cutoff]
    
    async def _calculate_current_metrics(self):
        """Calculate current metrics"""
        # Update timestamp
        self.metrics.timestamp = datetime.utcnow()
        
        # Calculate averages and peaks
        if self.metrics.total_requests > 0:
            self.metrics.avg_response_time = 0.5  # Simulated
        
        # Calculate peak requests per second
        # This would be calculated from actual request timestamps
        self.metrics.peak_requests_per_second = 100.0  # Simulated
    
    async def _cleanup_expired_entries(self):
        """Cleanup expired rate limit entries"""
        while True:
            try:
                current_time = time.time()
                cutoff_time = current_time - 3600  # 1 hour cleanup window
                
                # Cleanup request counters
                for key, counter in list(self.request_counters.items()):
                    # Remove old entries
                    while counter and counter[0] < cutoff_time:
                        counter.popleft()
                    
                    # Remove empty counters
                    if not counter:
                        del self.request_counters[key]
                
                # Sleep for 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")
                await asyncio.sleep(60)


# Creator-specific rate limiting strategies
class CreatorRateLimitManager:
    """Creator-specific rate limiting management"""
    
    @staticmethod
    async def setup_musician_limits(rate_limiter: RateLimiter) -> bool:
        """Setup rate limits optimized for musicians"""
        limits = {
            'audio_upload': 50,  # per hour
            'audio_processing': 200,  # per hour
            'collaboration_requests': 20,  # per hour
            'streaming_requests': 1000  # per hour
        }
        
        return await rate_limiter.update_creator_limits('musicians', limits)
    
    @staticmethod
    async def setup_photographer_limits(rate_limiter: RateLimiter) -> bool:
        """Setup rate limits optimized for photographers"""
        limits = {
            'image_upload': 100,  # per hour
            'image_processing': 500,  # per hour
            'portfolio_updates': 10,  # per hour
            'gallery_requests': 2000  # per hour
        }
        
        return await rate_limiter.update_creator_limits('photographers', limits)


# Example usage and testing
async def main():
    """Example usage of Rate Limiter"""
    limiter = RateLimiter()
    
    # Initialize
    await limiter.initialize()
    
    # Test rate limiting
    for i in range(5):
        result = await limiter.check_rate_limit(
            identifier="user123",
            scope=RateLimitScope.USER,
            creator_type="musicians",
            creator_tier=CreatorTier.PREMIUM,
            service_type="audio_processing"
        )
        print(f"Request {i+1}: {result}")
    
    # Get metrics
    metrics = await limiter.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())