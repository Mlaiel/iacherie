# Rate Limiting Strategies - Enterprise Integration Guide
======================================================

## Table of Contents
- [Rate Limiting Overview](#rate-limiting-overview)
- [Adaptive Rate Limiting](#adaptive-rate-limiting)
- [Circuit Breaker Implementation](#circuit-breaker-implementation)
- [Queue Management](#queue-management)
- [Provider-Specific Limits](#provider-specific-limits)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Best Practices](#best-practices)

## Rate Limiting Overview

### Purpose and Benefits

Rate limiting in the Ainflue platform serves multiple critical functions:

- **API Protection**: Prevent overwhelming external service providers
- **Cost Control**: Manage usage-based billing from third-party services
- **Reliability**: Ensure consistent service availability
- **Compliance**: Meet provider terms of service requirements
- **Performance**: Optimize resource utilization and response times

### Rate Limiting Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│ Rate Limiter    │───▶│ External API    │
│   Request       │    │ Component       │    │ Provider        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Queue Manager & │
                       │ Circuit Breaker │
                       └─────────────────┘
```

### Rate Limiting Strategies

#### 1. Token Bucket Algorithm

```python
import time
import asyncio
from typing import Dict, Optional

class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens"""
        async with self._lock:
            now = time.time()
            
            # Add tokens based on time elapsed
            elapsed = now - self.last_refill
            self.tokens = min(
                self.capacity,
                self.tokens + (elapsed * self.refill_rate)
            )
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> float:
        """Calculate wait time for tokens"""
        async with self._lock:
            if self.tokens >= tokens:
                return 0.0
            
            needed_tokens = tokens - self.tokens
            wait_time = needed_tokens / self.refill_rate
            return wait_time
```

#### 2. Sliding Window Rate Limiter

```python
import time
from collections import deque
from typing import Deque

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: Deque[float] = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] <= now - self.window_seconds:
                self.requests.popleft()
            
            # Check if we're under limit
            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True
            
            return False
    
    def get_reset_time(self) -> float:
        """Get time until rate limit resets"""
        if not self.requests:
            return 0.0
        
        oldest_request = self.requests[0]
        reset_time = oldest_request + self.window_seconds
        return max(0.0, reset_time - time.time())
```

## Adaptive Rate Limiting

### Dynamic Rate Adjustment

```python
class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on success rates"""
    
    def __init__(self, initial_rate: float, min_rate: float, max_rate: float):
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.success_count = 0
        self.total_count = 0
        self.adjustment_threshold = 100
        
    async def record_result(self, success: bool):
        """Record request result for adaptive adjustment"""
        self.total_count += 1
        if success:
            self.success_count += 1
        
        # Adjust rate based on success ratio
        if self.total_count >= self.adjustment_threshold:
            success_rate = self.success_count / self.total_count
            
            if success_rate > 0.95:
                # High success rate, increase limit
                self.current_rate = min(
                    self.max_rate,
                    self.current_rate * 1.1
                )
            elif success_rate < 0.8:
                # Low success rate, decrease limit
                self.current_rate = max(
                    self.min_rate,
                    self.current_rate * 0.9
                )
            
            # Reset counters
            self.success_count = 0
            self.total_count = 0
```

### Provider Health Monitoring

```python
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

class ProviderHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ProviderMetrics:
    """Provider health metrics"""
    provider_name: str
    health_status: ProviderHealth = ProviderHealth.HEALTHY
    success_rate: float = 100.0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    last_error: Optional[str] = None
    last_check: datetime = field(default_factory=datetime.utcnow)
    
    def update_health(self):
        """Update health status based on metrics"""
        if self.error_rate > 10 or self.success_rate < 90:
            self.health_status = ProviderHealth.UNHEALTHY
        elif self.error_rate > 5 or self.success_rate < 95:
            self.health_status = ProviderHealth.DEGRADED
        else:
            self.health_status = ProviderHealth.HEALTHY

class HealthAwareRateLimiter:
    """Rate limiter that adjusts based on provider health"""
    
    def __init__(self):
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        self.base_rates: Dict[str, float] = {}
    
    def get_adjusted_rate(self, provider: str) -> float:
        """Get rate adjusted for provider health"""
        base_rate = self.base_rates.get(provider, 10.0)
        metrics = self.provider_metrics.get(provider)
        
        if not metrics:
            return base_rate
        
        # Adjust rate based on health
        if metrics.health_status == ProviderHealth.UNHEALTHY:
            return base_rate * 0.5  # Reduce by 50%
        elif metrics.health_status == ProviderHealth.DEGRADED:
            return base_rate * 0.75  # Reduce by 25%
        else:
            return base_rate
```

## Circuit Breaker Implementation

### Basic Circuit Breaker

```python
import asyncio
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for API protection"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise self.expected_exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.expected_exception as e:
            await self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        if self.last_failure_time is None:
            return False
        
        return (
            datetime.utcnow() - self.last_failure_time
        ).total_seconds() >= self.recovery_timeout
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
```

## Queue Management

### Priority Queue System

```python
import heapq
import asyncio
from dataclasses import dataclass, field
from typing import Any, List, Optional

@dataclass
class QueuedRequest:
    """Queued request with priority"""
    priority: int
    timestamp: float
    request_data: Any
    callback: Optional[callable] = None
    
    def __lt__(self, other):
        """Compare for priority queue"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp

class PriorityQueueManager:
    """Priority-based queue manager"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue: List[QueuedRequest] = []
        self.queue_lock = asyncio.Lock()
        self.not_empty = asyncio.Condition(self.queue_lock)
        self.not_full = asyncio.Condition(self.queue_lock)
    
    async def enqueue(self, request: QueuedRequest) -> bool:
        """Add request to queue"""
        async with self.not_full:
            if len(self.queue) >= self.max_size:
                return False
            
            heapq.heappush(self.queue, request)
            self.not_empty.notify()
            return True
    
    async def dequeue(self, timeout: Optional[float] = None) -> Optional[QueuedRequest]:
        """Remove and return highest priority request"""
        async with self.not_empty:
            while not self.queue:
                await asyncio.wait_for(
                    self.not_empty.wait(), 
                    timeout=timeout
                )
            
            request = heapq.heappop(self.queue)
            self.not_full.notify()
            return request
    
    async def size(self) -> int:
        """Get current queue size"""
        async with self.queue_lock:
            return len(self.queue)
```

### Batch Processing Queue

```python
class BatchQueue:
    """Queue that processes items in batches"""
    
    def __init__(self, batch_size: int = 10, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue = asyncio.Queue()
        self.current_batch = []
        self.last_flush = time.time()
        self.processing_task = None
    
    async def start_processing(self, processor_func):
        """Start batch processing"""
        self.processing_task = asyncio.create_task(
            self._process_batches(processor_func)
        )
    
    async def stop_processing(self):
        """Stop batch processing"""
        if self.processing_task:
            self.processing_task.cancel()
            await self.processing_task
    
    async def add_item(self, item: Any):
        """Add item to queue"""
        await self.queue.put(item)
    
    async def _process_batches(self, processor_func):
        """Process items in batches"""
        while True:
            try:
                # Collect items for batch
                while (
                    len(self.current_batch) < self.batch_size and
                    time.time() - self.last_flush < self.flush_interval
                ):
                    try:
                        item = await asyncio.wait_for(
                            self.queue.get(), 
                            timeout=0.1
                        )
                        self.current_batch.append(item)
                    except asyncio.TimeoutError:
                        break
                
                # Process batch if we have items
                if self.current_batch:
                    await processor_func(self.current_batch.copy())
                    self.current_batch.clear()
                    self.last_flush = time.time()
                
                await asyncio.sleep(0.01)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Batch processing error: {e}")
```

## Provider-Specific Limits

### Configuration Management

```yaml
# rate_limits.yaml
providers:
  twilio:
    requests_per_second: 10
    requests_per_minute: 100
    concurrent_requests: 5
    burst_allowance: 20
    
  sendgrid:
    requests_per_second: 25
    requests_per_minute: 1000
    concurrent_requests: 10
    daily_limit: 100000
    
  google_analytics:
    requests_per_second: 10
    requests_per_100_seconds: 1000
    concurrent_requests: 10
    quota_user_limits: true
    
  stripe:
    requests_per_second: 25
    requests_per_minute: 1000
    concurrent_requests: 25
    read_requests_per_second: 100
```

### Provider Rate Limiter

```python
import yaml
from typing import Dict, Any

class ProviderRateLimiter:
    """Provider-specific rate limiting"""
    
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.limiters: Dict[str, Dict[str, Any]] = {}
        self._initialize_limiters()
    
    def _initialize_limiters(self):
        """Initialize rate limiters for each provider"""
        for provider, limits in self.config['providers'].items():
            self.limiters[provider] = {
                'per_second': TokenBucket(
                    capacity=limits.get('requests_per_second', 10),
                    refill_rate=limits.get('requests_per_second', 10)
                ),
                'per_minute': SlidingWindowRateLimiter(
                    limit=limits.get('requests_per_minute', 100),
                    window_seconds=60
                ),
                'concurrent': asyncio.Semaphore(
                    limits.get('concurrent_requests', 5)
                )
            }
    
    async def acquire(self, provider: str) -> bool:
        """Acquire rate limit permissions"""
        if provider not in self.limiters:
            return True
        
        limiters = self.limiters[provider]
        
        # Check per-second limit
        if not await limiters['per_second'].consume():
            return False
        
        # Check per-minute limit
        if not await limiters['per_minute'].is_allowed():
            return False
        
        # Acquire semaphore for concurrent requests
        await limiters['concurrent'].acquire()
        return True
    
    def release(self, provider: str):
        """Release concurrent request semaphore"""
        if provider in self.limiters:
            self.limiters[provider]['concurrent'].release()
```

## Monitoring and Alerting

### Rate Limit Metrics

```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    requests_allowed: int = 0
    requests_rejected: int = 0
    average_wait_time: float = 0.0
    max_wait_time: float = 0.0
    queue_size: int = 0
    circuit_breaker_trips: int = 0
    
    @property
    def rejection_rate(self) -> float:
        total = self.requests_allowed + self.requests_rejected
        return (self.requests_rejected / total * 100) if total > 0 else 0.0

class RateLimitMonitor:
    """Monitor rate limiting performance"""
    
    def __init__(self):
        self.metrics_by_provider: Dict[str, RateLimitMetrics] = {}
        self.start_time = time.time()
    
    def record_request(self, provider: str, allowed: bool, wait_time: float = 0.0):
        """Record rate limit decision"""
        if provider not in self.metrics_by_provider:
            self.metrics_by_provider[provider] = RateLimitMetrics()
        
        metrics = self.metrics_by_provider[provider]
        
        if allowed:
            metrics.requests_allowed += 1
        else:
            metrics.requests_rejected += 1
        
        if wait_time > 0:
            # Update average wait time
            total_requests = metrics.requests_allowed + metrics.requests_rejected
            metrics.average_wait_time = (
                (metrics.average_wait_time * (total_requests - 1) + wait_time) / 
                total_requests
            )
            metrics.max_wait_time = max(metrics.max_wait_time, wait_time)
    
    def get_provider_metrics(self, provider: str) -> RateLimitMetrics:
        """Get metrics for specific provider"""
        return self.metrics_by_provider.get(provider, RateLimitMetrics())
    
    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall rate limiting metrics"""
        total_allowed = sum(m.requests_allowed for m in self.metrics_by_provider.values())
        total_rejected = sum(m.requests_rejected for m in self.metrics_by_provider.values())
        total_requests = total_allowed + total_rejected
        
        return {
            'total_requests': total_requests,
            'total_allowed': total_allowed,
            'total_rejected': total_rejected,
            'overall_rejection_rate': (total_rejected / total_requests * 100) if total_requests > 0 else 0.0,
            'uptime_seconds': time.time() - self.start_time,
            'providers': list(self.metrics_by_provider.keys())
        }
```

### Alerting Configuration

```yaml
# alerts.yaml
rate_limit_alerts:
  high_rejection_rate:
    threshold: 10  # percent
    window: 300    # 5 minutes
    severity: warning
    
  queue_backlog:
    threshold: 100  # items
    severity: warning
    
  circuit_breaker_open:
    threshold: 1
    severity: critical
    
  provider_unavailable:
    threshold: 5  # consecutive failures
    severity: critical
```

## Best Practices

### Implementation Guidelines

1. **Layered Rate Limiting**
   - Implement multiple rate limiting strategies
   - Use different limits for different request types
   - Apply both local and distributed rate limiting

2. **Graceful Degradation**
   - Queue requests when possible
   - Provide meaningful error messages
   - Implement fallback providers

3. **Monitoring and Observability**
   - Track rate limit metrics continuously
   - Set up alerts for threshold breaches
   - Log rate limiting decisions for analysis

4. **Configuration Management**
   - Make rate limits configurable
   - Allow runtime adjustment of limits
   - Use feature flags for rate limiting strategies

### Performance Considerations

```python
# Efficient rate limiting patterns
class EfficientRateLimiter:
    """High-performance rate limiter optimizations"""
    
    def __init__(self):
        # Use local cache for frequent checks
        self.local_cache = {}
        self.cache_ttl = 60  # 1 minute
        
        # Batch rate limit checks
        self.pending_checks = []
        self.batch_timer = None
    
    async def check_rate_limit_batch(self, requests: List[str]) -> Dict[str, bool]:
        """Check multiple rate limits in one operation"""
        # Implement batch checking logic
        results = {}
        
        # Group by provider for efficient checking
        provider_groups = self._group_by_provider(requests)
        
        for provider, provider_requests in provider_groups.items():
            provider_results = await self._check_provider_batch(provider, provider_requests)
            results.update(provider_results)
        
        return results
    
    def _group_by_provider(self, requests: List[str]) -> Dict[str, List[str]]:
        """Group requests by provider for batch processing"""
        groups = {}
        for request in requests:
            provider = self._extract_provider(request)
            if provider not in groups:
                groups[provider] = []
            groups[provider].append(request)
        return groups
```

### Error Handling

```python
class RateLimitError(Exception):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after

async def rate_limited_request(func, *args, **kwargs):
    """Execute function with rate limiting and retry logic"""
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            # Calculate delay with exponential backoff
            delay = e.retry_after or (base_delay * (2 ** attempt))
            await asyncio.sleep(delay)
```

---

## Integration Examples

### Flask/FastAPI Integration

```python
from functools import wraps
from flask import request, jsonify

def rate_limit(provider: str):
    """Decorator for rate limiting Flask routes"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            if not await rate_limiter.acquire(provider):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': await rate_limiter.get_retry_after(provider)
                }), 429
            
            try:
                result = await f(*args, **kwargs)
                rate_limiter.release(provider)
                return result
            except Exception as e:
                rate_limiter.release(provider)
                raise
        
        return decorated_function
    return decorator

@app.route('/api/send-email')
@rate_limit('sendgrid')
async def send_email():
    # Email sending logic
    pass
```

---

**© 2025 Fahed Mlaiel. All rights reserved.**  
**Contact**: mlaiel@live.de  
**Legal**: This documentation is part of the Ainflue platform and is protected by international copyright law.