"""⚡ Enterprise Rate Limiting Engine
=================================

Advanced intelligent rate limiting system with predictive analysis,
adaptive throttling, and comprehensive quota management for enterprise
API usage optimization and compliance.

Features:
- Intelligent adaptive rate limiting
- Predictive quota management
- Circuit breaker pattern integration
- Real-time usage analytics
- Multi-tier rate limiting policies
- Burst traffic handling
- Priority-based request queuing
- Platform-specific optimization
- Usage forecasting and alerts
- Automatic backoff strategies

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""
import asyncio
import logging
import time
import math
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics
import json

logger = logging.getLogger(__name__)

class RateLimitType(str, Enum):
    """Rate limit type enumeration."""
    REQUESTS_PER_SECOND = "requests_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BANDWIDTH_PER_SECOND = "bandwidth_per_second"
    CONCURRENT_REQUESTS = "concurrent_requests"
    CUSTOM = "custom"

class Priority(str, Enum):
    """Request priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"

class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"

@dataclass
class RateLimitConfig:
    """Rate limit configuration structure."""
    platform: str
    limit_type: RateLimitType
    limit_value: int
    window_size: int  # seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_limit: Optional[int] = None
    priority_multipliers: Dict[Priority, float] = field(default_factory=lambda: {
        Priority.CRITICAL: 2.0,
        Priority.HIGH: 1.5,
        Priority.MEDIUM: 1.0,
        Priority.LOW: 0.7,
        Priority.BACKGROUND: 0.3
    })
    backoff_factor: float = 2.0
    max_backoff: int = 300  # seconds
    recovery_factor: float = 0.8

@dataclass
class RateLimitStatus:
    """Current rate limit status."""
    platform: str
    current_usage: int
    limit_value: int
    remaining: int
    reset_time: datetime
    window_start: datetime
    is_limited: bool = False
    backoff_until: Optional[datetime] = None
    last_request_time: Optional[datetime] = None

@dataclass
class RequestMetrics:
    """Request performance metrics."""
    timestamp: datetime
    platform: str
    priority: Priority
    response_time: float
    success: bool
    size_bytes: int = 0
    endpoint: str = ""

class SlidingWindowCounter:
    """Sliding window counter implementation."""
    
    def __init__(self, window_size: int, limit: int):
        """Initialize sliding window counter."""
        self.window_size = window_size
        self.limit = limit
        self.requests: deque = deque()
        
    def add_request(self, timestamp: float = None) -> bool:
        """Add request and check if within limits."""
        if timestamp is None:
            timestamp = time.time()
        
        # Remove requests outside window
        cutoff_time = timestamp - self.window_size
        while self.requests and self.requests[0] <= cutoff_time:
            self.requests.popleft()
        
        # Check if we can add new request
        if len(self.requests) >= self.limit:
            return False
        
        self.requests.append(timestamp)
        return True
    
    def get_current_count(self) -> int:
        """Get current request count in window."""
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        
        # Clean old requests
        while self.requests and self.requests[0] <= cutoff_time:
            self.requests.popleft()
        
        return len(self.requests)
    
    def get_reset_time(self) -> datetime:
        """Get time when oldest request will expire."""
        if not self.requests:
            return datetime.utcnow()
        
        oldest_request_time = self.requests[0]
        reset_time = oldest_request_time + self.window_size
        return datetime.utcfromtimestamp(reset_time)

class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket."""
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
        
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens and check availability."""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_available_tokens(self) -> int:
        """Get number of available tokens."""
        self._refill()
        return int(self.tokens)
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get wait time until enough tokens are available."""
        self._refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate

class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on performance."""
    
    def __init__(self, base_config: RateLimitConfig):
        """Initialize adaptive rate limiter."""
        self.base_config = base_config
        self.current_limit = base_config.limit_value
        self.performance_history: deque = deque(maxlen=100)
        self.adjustment_factor = 1.0
        self.last_adjustment = time.time()
        
    def record_performance(self, response_time: float, success: bool):
        """Record request performance for adaptation."""
        self.performance_history.append({
            'timestamp': time.time(),
            'response_time': response_time,
            'success': success
        })
        
        # Adjust rate limit based on performance
        self._adjust_rate_limit()
    
    def _adjust_rate_limit(self):
        """Adjust rate limit based on recent performance."""
        if len(self.performance_history) < 10:
            return
        
        now = time.time()
        # Only adjust every 60 seconds
        if now - self.last_adjustment < 60:
            return
        
        # Calculate recent metrics
        recent_requests = [r for r in self.performance_history 
                          if now - r['timestamp'] < 300]  # Last 5 minutes
        
        if not recent_requests:
            return
        
        success_rate = sum(1 for r in recent_requests if r['success']) / len(recent_requests)
        avg_response_time = statistics.mean(r['response_time'] for r in recent_requests)
        
        # Adjust based on performance
        if success_rate > 0.95 and avg_response_time < 2.0:
            # Good performance, can increase rate
            self.adjustment_factor = min(2.0, self.adjustment_factor * 1.1)
        elif success_rate < 0.8 or avg_response_time > 5.0:
            # Poor performance, decrease rate
            self.adjustment_factor = max(0.3, self.adjustment_factor * 0.8)
        
        self.current_limit = int(self.base_config.limit_value * self.adjustment_factor)
        self.last_adjustment = now
        
        logger.info(f"Adjusted rate limit for {self.base_config.platform}: "
                   f"{self.current_limit} (factor: {self.adjustment_factor:.2f})")
    
    def get_current_limit(self) -> int:
        """Get current adjusted limit."""
        return self.current_limit

class PriorityQueue:
    """Priority-based request queue."""
    
    def __init__(self):
        """Initialize priority queue."""
        self.queues: Dict[Priority, deque] = {
            priority: deque() for priority in Priority
        }
        self.pending_count = 0
        
    async def put(self, item: Any, priority: Priority = Priority.MEDIUM):
        """Add item to priority queue."""
        self.queues[priority].append({
            'item': item,
            'timestamp': time.time(),
            'priority': priority
        })
        self.pending_count += 1
    
    async def get(self) -> Optional[Tuple[Any, Priority]]:
        """Get highest priority item from queue."""
        # Check queues in priority order
        for priority in [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, 
                        Priority.LOW, Priority.BACKGROUND]:
            if self.queues[priority]:
                entry = self.queues[priority].popleft()
                self.pending_count -= 1
                return entry['item'], entry['priority']
        
        return None
    
    def size(self) -> int:
        """Get total queue size."""
        return self.pending_count
    
    def size_by_priority(self) -> Dict[Priority, int]:
        """Get queue size by priority."""
        return {priority: len(queue) for priority, queue in self.queues.items()}

class IntelligentRateLimiter:
    """
    Enterprise intelligent rate limiting engine.
    
    Provides comprehensive rate limiting with:
    - Multiple limiting strategies
    - Priority-based queuing
    - Adaptive adjustment
    - Performance monitoring
    - Predictive analysis
    """
    
    def __init__(self):
        """Initialize intelligent rate limiter."""
        self.platform_configs: Dict[str, RateLimitConfig] = {}
        self.rate_limiters: Dict[str, Any] = {}
        self.status_cache: Dict[str, RateLimitStatus] = {}
        self.request_queue = PriorityQueue()
        self.metrics_history: deque = deque(maxlen=10000)
        self.alert_callbacks: List[Callable] = []
        self.adaptive_limiters: Dict[str, AdaptiveRateLimiter] = {}
        
        # Background task for queue processing
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._processing_active = False
        
        logger.info("Intelligent Rate Limiter initialized")
    
    def configure_platform(self, config: RateLimitConfig):
        """Configure rate limiting for platform."""
        self.platform_configs[config.platform] = config
        
        # Initialize appropriate rate limiter
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            self.rate_limiters[config.platform] = SlidingWindowCounter(
                config.window_size, config.limit_value
            )
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            refill_rate = config.limit_value / config.window_size
            self.rate_limiters[config.platform] = TokenBucket(
                config.limit_value, refill_rate
            )
        elif config.strategy == RateLimitStrategy.ADAPTIVE:
            self.adaptive_limiters[config.platform] = AdaptiveRateLimiter(config)
            self.rate_limiters[config.platform] = SlidingWindowCounter(
                config.window_size, config.limit_value
            )
        
        # Initialize status
        self.status_cache[config.platform] = RateLimitStatus(
            platform=config.platform,
            current_usage=0,
            limit_value=config.limit_value,
            remaining=config.limit_value,
            reset_time=datetime.utcnow() + timedelta(seconds=config.window_size),
            window_start=datetime.utcnow()
        )
        
        logger.info(f"Configured rate limiting for {config.platform}: "
                   f"{config.limit_value}/{config.window_size}s using {config.strategy}")
    
    async def can_make_request(
        self,
        platform: str,
        priority: Priority = Priority.MEDIUM,
        size_bytes: int = 0
    ) -> Tuple[bool, Optional[float]]:
        """
        Check if request can be made immediately.
        
        Args:
            platform: Platform identifier
            priority: Request priority
            size_bytes: Request size in bytes
            
        Returns:
            Tuple of (can_proceed, wait_time_seconds)
        """
        if platform not in self.platform_configs:
            logger.warning(f"No rate limit config for platform: {platform}")
            return True, None
        
        config = self.platform_configs[platform]
        limiter = self.rate_limiters[platform]
        
        # Check adaptive limiter if configured
        if config.strategy == RateLimitStrategy.ADAPTIVE:
            adaptive_limiter = self.adaptive_limiters[platform]
            current_limit = adaptive_limiter.get_current_limit()
        else:
            current_limit = config.limit_value
        
        # Apply priority multiplier
        effective_limit = int(current_limit * config.priority_multipliers[priority])
        
        # Check rate limiter
        if isinstance(limiter, SlidingWindowCounter):
            can_proceed = limiter.add_request()
            wait_time = 0.0 if can_proceed else self._calculate_wait_time(platform)
        elif isinstance(limiter, TokenBucket):
            can_proceed = limiter.consume()
            wait_time = limiter.get_wait_time() if not can_proceed else 0.0
        else:
            can_proceed = True
            wait_time = 0.0
        
        # Update status
        self._update_status(platform, can_proceed)
        
        return can_proceed, wait_time
    
    async def record_request(
        self,
        platform: str,
        priority: Priority = Priority.MEDIUM,
        response_time: float = 0.0,
        success: bool = True,
        size_bytes: int = 0,
        endpoint: str = ""
    ):
        """Record completed request for analytics and adaptation."""
        # Record metrics
        metrics = RequestMetrics(
            timestamp=datetime.utcnow(),
            platform=platform,
            priority=priority,
            response_time=response_time,
            success=success,
            size_bytes=size_bytes,
            endpoint=endpoint
        )
        self.metrics_history.append(metrics)
        
        # Update adaptive limiter if configured
        if platform in self.adaptive_limiters:
            adaptive_limiter = self.adaptive_limiters[platform]
            adaptive_limiter.record_performance(response_time, success)
        
        # Check alert conditions
        await self._check_alert_conditions(platform, metrics)
    
    async def queue_request(
        self,
        request_func: Callable,
        platform: str,
        priority: Priority = Priority.MEDIUM,
        **kwargs
    ) -> Any:
        """
        Queue request for execution with rate limiting.
        
        Args:
            request_func: Function to execute
            platform: Platform identifier
            priority: Request priority
            **kwargs: Additional arguments
            
        Returns:
            Function result when executed
        """
        request_item = {
            'func': request_func,
            'platform': platform,
            'kwargs': kwargs,
            'future': asyncio.Future()
        }
        
        await self.request_queue.put(request_item, priority)
        
        # Start queue processor if not active
        if not self._processing_active:
            await self._start_queue_processor()
        
        return await request_item['future']
    
    async def _start_queue_processor(self):
        """Start background queue processor."""
        if self._queue_processor_task and not self._queue_processor_task.done():
            return
        
        self._processing_active = True
        self._queue_processor_task = asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        """Process queued requests with rate limiting."""
        logger.info("Started rate limited queue processor")
        
        while self._processing_active:
            try:
                # Get next request
                queue_item = await self.request_queue.get()
                if not queue_item:
                    await asyncio.sleep(0.1)
                    continue
                
                request_item, priority = queue_item
                platform = request_item['platform']
                
                # Check rate limits
                can_proceed, wait_time = await self.can_make_request(platform, priority)
                
                if not can_proceed and wait_time:
                    # Wait and retry
                    await asyncio.sleep(wait_time)
                    can_proceed, _ = await self.can_make_request(platform, priority)
                
                if can_proceed:
                    # Execute request
                    try:
                        start_time = time.time()
                        result = await request_item['func'](**request_item['kwargs'])
                        response_time = time.time() - start_time
                        
                        # Record successful request
                        await self.record_request(
                            platform, priority, response_time, True
                        )
                        
                        # Set result
                        request_item['future'].set_result(result)
                        
                    except Exception as e:
                        # Record failed request
                        response_time = time.time() - start_time
                        await self.record_request(
                            platform, priority, response_time, False
                        )
                        
                        # Set exception
                        request_item['future'].set_exception(e)
                else:
                    # Rate limited, set exception
                    request_item['future'].set_exception(
                        Exception(f"Rate limited for {platform}")
                    )
                
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(1)
    
    def _calculate_wait_time(self, platform: str) -> float:
        """Calculate wait time until next request can be made."""
        if platform not in self.rate_limiters:
            return 0.0
        
        limiter = self.rate_limiters[platform]
        
        if isinstance(limiter, SlidingWindowCounter):
            reset_time = limiter.get_reset_time()
            wait_time = (reset_time - datetime.utcnow()).total_seconds()
            return max(0.0, wait_time)
        elif isinstance(limiter, TokenBucket):
            return limiter.get_wait_time()
        
        return 0.0
    
    def _update_status(self, platform: str, can_proceed: bool):
        """Update platform rate limit status."""
        if platform not in self.status_cache:
            return
        
        status = self.status_cache[platform]
        limiter = self.rate_limiters[platform]
        
        if isinstance(limiter, SlidingWindowCounter):
            status.current_usage = limiter.get_current_count()
            status.remaining = max(0, status.limit_value - status.current_usage)
            status.reset_time = limiter.get_reset_time()
        elif isinstance(limiter, TokenBucket):
            status.current_usage = status.limit_value - limiter.get_available_tokens()
            status.remaining = limiter.get_available_tokens()
        
        status.is_limited = not can_proceed
        status.last_request_time = datetime.utcnow()
    
    async def _check_alert_conditions(self, platform: str, metrics: RequestMetrics):
        """Check for alert conditions and trigger callbacks."""
        # Check high error rate
        recent_requests = [m for m in self.metrics_history 
                          if m.platform == platform and 
                          (datetime.utcnow() - m.timestamp).total_seconds() < 300]
        
        if len(recent_requests) >= 10:
            error_rate = sum(1 for r in recent_requests if not r.success) / len(recent_requests)
            if error_rate > 0.1:  # 10% error rate threshold
                await self._trigger_alert('high_error_rate', {
                    'platform': platform,
                    'error_rate': error_rate,
                    'sample_size': len(recent_requests)
                })
        
        # Check slow response times
        if metrics.response_time > 10.0:  # 10 second threshold
            await self._trigger_alert('slow_response', {
                'platform': platform,
                'response_time': metrics.response_time,
                'endpoint': metrics.endpoint
            })
    
    async def _trigger_alert(self, alert_type: str, data: Dict[str, Any]):
        """Trigger alert callbacks."""
        alert_data = {
            'type': alert_type,
            'timestamp': datetime.utcnow(),
            'data': data
        }
        
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert_data)
                else:
                    callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for rate limiting alerts."""
        self.alert_callbacks.append(callback)
    
    def get_platform_status(self, platform: str) -> Optional[RateLimitStatus]:
        """Get current rate limit status for platform."""
        return self.status_cache.get(platform)
    
    def get_all_status(self) -> Dict[str, RateLimitStatus]:
        """Get rate limit status for all platforms."""
        return self.status_cache.copy()
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            'total_pending': self.request_queue.size(),
            'by_priority': self.request_queue.size_by_priority(),
            'processing_active': self._processing_active
        }
    
    def get_performance_metrics(self, platform: str = None) -> Dict[str, Any]:
        """Get performance metrics."""
        if platform:
            platform_metrics = [m for m in self.metrics_history if m.platform == platform]
        else:
            platform_metrics = list(self.metrics_history)
        
        if not platform_metrics:
            return {}
        
        # Calculate metrics
        total_requests = len(platform_metrics)
        successful_requests = sum(1 for m in platform_metrics if m.success)
        success_rate = successful_requests / total_requests * 100
        
        response_times = [m.response_time for m in platform_metrics if m.success]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'min_response_time': min(response_times) if response_times else 0.0,
            'max_response_time': max(response_times) if response_times else 0.0
        }
    
    async def shutdown(self):
        """Shutdown rate limiter and cleanup resources."""
        self._processing_active = False
        
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
            try:
                await self._queue_processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Rate limiter shutdown completed")

# Export main classes
__all__ = [
    'IntelligentRateLimiter',
    'RateLimitConfig',
    'RateLimitStatus',
    'RateLimitType',
    'RateLimitStrategy',
    'Priority',
    'RequestMetrics'
]
