"""
Circuit Breaker & Resilience Patterns - Enterprise Microservices
================================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: Microservices Architect + Backend Senior
**Module**: Enterprise Resilience & Fault Tolerance
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Advanced circuit breaker implementation with bulkhead isolation,
retry policies, fallback mechanisms, and intelligent failure detection.
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from dataclasses import dataclass, field
from enum import Enum
import functools
import random


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = 0      # Normal operation
    OPEN = 1        # Blocking requests
    HALF_OPEN = 2   # Testing recovery


class FailureType(Enum):
    """Types of failures"""
    TIMEOUT = "timeout"
    ERROR = "error"
    RATE_LIMIT = "rate_limit"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"


class RetryStrategy(Enum):
    """Retry strategies"""
    NONE = "none"
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    JITTERED_BACKOFF = "jittered_backoff"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5              # Failures to open circuit
    success_threshold: int = 3              # Successes to close circuit  
    timeout_duration: float = 60.0          # Timeout before half-open (seconds)
    call_timeout: float = 10.0              # Individual call timeout
    sliding_window_size: int = 100          # Size of failure tracking window
    minimum_throughput: int = 10            # Minimum calls before opening
    failure_rate_threshold: float = 0.5     # Failure rate to open (0-1)
    slow_call_duration: float = 5.0         # Duration considered slow
    slow_call_rate_threshold: float = 0.5   # Slow call rate to open


@dataclass
class RetryConfig:
    """Retry policy configuration"""
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[type] = field(default_factory=list)


@dataclass
class BulkheadConfig:
    """Bulkhead isolation configuration"""
    max_concurrent_calls: int = 10
    max_wait_duration: float = 30.0
    queue_size: int = 50


@dataclass
class FailureRecord:
    """Record of a failure"""
    timestamp: datetime
    failure_type: FailureType
    duration: float
    exception: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreakerMetrics:
    """Circuit breaker metrics collector"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.call_records: List[Dict[str, Any]] = []
        self.failure_records: List[FailureRecord] = []
        
        # Metrics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0
        self.slow_calls = 0
        
        # Timing
        self.total_duration = 0.0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None

    def record_call(self, success: bool, duration: float, failure_type: Optional[FailureType] = None):
        """Record a call result"""
        
        now = datetime.utcnow()
        
        # Update totals
        self.total_calls += 1
        self.total_duration += duration
        
        if success:
            self.successful_calls += 1
            self.last_success_time = now
        else:
            self.failed_calls += 1
            self.last_failure_time = now
            
            if failure_type:
                self.failure_records.append(FailureRecord(
                    timestamp=now,
                    failure_type=failure_type,
                    duration=duration
                ))
        
        # Add to sliding window
        self.call_records.append({
            "timestamp": now,
            "success": success,
            "duration": duration,
            "failure_type": failure_type.value if failure_type else None
        })
        
        # Maintain window size
        if len(self.call_records) > self.window_size:
            self.call_records.pop(0)
        
        if len(self.failure_records) > self.window_size:
            self.failure_records.pop(0)

    def record_rejection(self):
        """Record a rejected call"""
        self.rejected_calls += 1

    def record_slow_call(self):
        """Record a slow call"""
        self.slow_calls += 1

    def get_failure_rate(self, window_minutes: int = 5) -> float:
        """Get failure rate within time window"""
        
        if not self.call_records:
            return 0.0
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_calls = [
            record for record in self.call_records
            if record["timestamp"] > cutoff_time
        ]
        
        if not recent_calls:
            return 0.0
        
        failed_calls = sum(1 for record in recent_calls if not record["success"])
        return failed_calls / len(recent_calls)

    def get_slow_call_rate(self, window_minutes: int = 5, slow_threshold: float = 5.0) -> float:
        """Get slow call rate within time window"""
        
        if not self.call_records:
            return 0.0
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_calls = [
            record for record in self.call_records
            if record["timestamp"] > cutoff_time
        ]
        
        if not recent_calls:
            return 0.0
        
        slow_calls = sum(1 for record in recent_calls if record["duration"] > slow_threshold)
        return slow_calls / len(recent_calls)

    def get_average_response_time(self, window_minutes: int = 5) -> float:
        """Get average response time"""
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_calls = [
            record for record in self.call_records
            if record["timestamp"] > cutoff_time
        ]
        
        if not recent_calls:
            return 0.0
        
        return statistics.mean(record["duration"] for record in recent_calls)


class CircuitBreaker:
    """Enterprise Circuit Breaker with advanced patterns"""
    
    def __init__(self, 
                 name: str,
                 config: CircuitBreakerConfig = None,
                 fallback_function: Optional[Callable] = None):
        """Initialize circuit breaker"""
        
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback_function = fallback_function
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.next_attempt_time: Optional[datetime] = None
        
        # Metrics
        self.metrics = CircuitBreakerMetrics(self.config.sliding_window_size)
        
        # Concurrency control
        self.active_calls = 0
        self.max_concurrent_calls = 100
        
        # Logger
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
        
        self.logger.info(f"Circuit breaker '{name}' initialized")

    async def call(self, func: Callable[..., Awaitable], *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if call is allowed
        if not await self._can_execute():
            self.metrics.record_rejection()
            if self.fallback_function:
                self.logger.debug(f"Circuit breaker '{self.name}' executing fallback")
                return await self.fallback_function(*args, **kwargs)
            else:
                raise CircuitBreakerOpenException(f"Circuit breaker '{self.name}' is open")
        
        # Execute call with metrics
        start_time = time.time()
        self.active_calls += 1
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.call_timeout
            )
            
            # Record success
            duration = time.time() - start_time
            await self._on_success(duration)
            
            return result
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            await self._on_failure(duration, FailureType.TIMEOUT)
            raise
            
        except Exception as e:
            duration = time.time() - start_time
            await self._on_failure(duration, FailureType.ERROR, e)
            raise
            
        finally:
            self.active_calls -= 1

    async def _can_execute(self) -> bool:
        """Check if call can be executed"""
        
        if self.state == CircuitState.CLOSED:
            return True
        
        elif self.state == CircuitState.OPEN:
            # Check if timeout period has passed
            if (self.next_attempt_time and 
                datetime.utcnow() >= self.next_attempt_time):
                
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' moved to HALF_OPEN")
                return True
            
            return False
        
        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited calls to test recovery
            return self.success_count < self.config.success_threshold
        
        return False

    async def _on_success(self, duration: float):
        """Handle successful call"""
        
        # Record metrics
        self.metrics.record_call(True, duration)
        
        # Track slow calls
        if duration > self.config.slow_call_duration:
            self.metrics.record_slow_call()
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            
            # Check if we can close the circuit
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info(f"Circuit breaker '{self.name}' moved to CLOSED")
        
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)

    async def _on_failure(self, duration: float, failure_type: FailureType, exception: Exception = None):
        """Handle failed call"""
        
        # Record metrics
        self.metrics.record_call(False, duration, failure_type)
        
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        # Check if we should open the circuit
        should_open = await self._should_open_circuit()
        
        if should_open and self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.next_attempt_time = datetime.utcnow() + timedelta(seconds=self.config.timeout_duration)
            self.logger.warning(f"Circuit breaker '{self.name}' moved to OPEN")
        
        elif self.state == CircuitState.HALF_OPEN:
            # Failed during testing, go back to open
            self.state = CircuitState.OPEN
            self.next_attempt_time = datetime.utcnow() + timedelta(seconds=self.config.timeout_duration)
            self.logger.warning(f"Circuit breaker '{self.name}' moved back to OPEN")

    async def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        
        # Check failure count threshold
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # Check minimum throughput requirement
        if self.metrics.total_calls < self.config.minimum_throughput:
            return False
        
        # Check failure rate
        failure_rate = self.metrics.get_failure_rate()
        if failure_rate >= self.config.failure_rate_threshold:
            return True
        
        # Check slow call rate
        slow_call_rate = self.metrics.get_slow_call_rate(
            slow_threshold=self.config.slow_call_duration
        )
        if slow_call_rate >= self.config.slow_call_rate_threshold:
            return True
        
        return False

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        
        return {
            "name": self.name,
            "state": self.state.name,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.metrics.total_calls,
            "successful_calls": self.metrics.successful_calls,
            "failed_calls": self.metrics.failed_calls,
            "rejected_calls": self.metrics.rejected_calls,
            "failure_rate": self.metrics.get_failure_rate(),
            "slow_call_rate": self.metrics.get_slow_call_rate(),
            "average_response_time": self.metrics.get_average_response_time(),
            "active_calls": self.active_calls,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "next_attempt_time": self.next_attempt_time.isoformat() if self.next_attempt_time else None
        }


class RetryPolicy:
    """Advanced retry policy with multiple strategies"""
    
    def __init__(self, config: RetryConfig = None):
        """Initialize retry policy"""
        
        self.config = config or RetryConfig()
        self.logger = logging.getLogger("retry_policy")

    async def execute(self, func: Callable[..., Awaitable], *args, **kwargs) -> Any:
        """Execute function with retry policy"""
        
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable(e):
                    raise
                
                # Check if this is the last attempt
                if attempt == self.config.max_attempts - 1:
                    raise
                
                # Calculate delay
                delay = self._calculate_delay(attempt)
                
                self.logger.debug(
                    f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}"
                )
                
                await asyncio.sleep(delay)
        
        # Should not reach here, but just in case
        raise last_exception

    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable"""
        
        # Default retryable exceptions
        retryable_types = [
            asyncio.TimeoutError,
            ConnectionError,
            TimeoutError,
        ]
        
        # Add configured retryable exceptions
        retryable_types.extend(self.config.retryable_exceptions)
        
        return any(isinstance(exception, exc_type) for exc_type in retryable_types)

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on retry strategy"""
        
        if self.config.strategy == RetryStrategy.NONE:
            return 0.0
        
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * (attempt + 1)
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.multiplier ** attempt)
        
        elif self.config.strategy == RetryStrategy.JITTERED_BACKOFF:
            base_delay = self.config.base_delay * (self.config.multiplier ** attempt)
            jitter = random.uniform(0, base_delay * 0.1)  # 10% jitter
            delay = base_delay + jitter
        
        else:
            delay = self.config.base_delay
        
        # Apply jitter if enabled
        if self.config.jitter and self.config.strategy != RetryStrategy.JITTERED_BACKOFF:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        # Ensure delay doesn't exceed maximum
        return min(delay, self.config.max_delay)


class BulkheadIsolator:
    """Bulkhead pattern for resource isolation"""
    
    def __init__(self, name: str, config: BulkheadConfig = None):
        """Initialize bulkhead isolator"""
        
        self.name = name
        self.config = config or BulkheadConfig()
        
        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_calls)
        
        # Queue for waiting requests
        self.waiting_queue = asyncio.Queue(maxsize=self.config.queue_size)
        
        # Metrics
        self.active_calls = 0
        self.total_calls = 0
        self.rejected_calls = 0
        self.queued_calls = 0
        
        self.logger = logging.getLogger(f"bulkhead.{name}")

    async def execute(self, func: Callable[..., Awaitable], *args, **kwargs) -> Any:
        """Execute function with bulkhead isolation"""
        
        self.total_calls += 1
        
        try:
            # Try to acquire semaphore with timeout
            await asyncio.wait_for(
                self.semaphore.acquire(),
                timeout=self.config.max_wait_duration
            )
            
            self.active_calls += 1
            
            try:
                return await func(*args, **kwargs)
            finally:
                self.active_calls -= 1
                self.semaphore.release()
                
        except asyncio.TimeoutError:
            self.rejected_calls += 1
            raise BulkheadRejectedException(
                f"Bulkhead '{self.name}' rejected call due to resource exhaustion"
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get bulkhead metrics"""
        
        return {
            "name": self.name,
            "active_calls": self.active_calls,
            "total_calls": self.total_calls,
            "rejected_calls": self.rejected_calls,
            "queued_calls": self.queued_calls,
            "available_permits": self.semaphore._value,
            "max_concurrent_calls": self.config.max_concurrent_calls,
            "queue_size": self.config.queue_size,
            "rejection_rate": self.rejected_calls / max(self.total_calls, 1)
        }


class ResilienceManager:
    """Comprehensive resilience manager combining all patterns"""
    
    def __init__(self):
        """Initialize resilience manager"""
        
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self.bulkheads: Dict[str, BulkheadIsolator] = {}
        
        self.logger = logging.getLogger("resilience_manager")
        self.logger.info("Resilience Manager initialized")

    def create_circuit_breaker(self, 
                             name: str, 
                             config: CircuitBreakerConfig = None,
                             fallback_function: Optional[Callable] = None) -> CircuitBreaker:
        """Create and register circuit breaker"""
        
        circuit_breaker = CircuitBreaker(name, config, fallback_function)
        self.circuit_breakers[name] = circuit_breaker
        
        self.logger.info(f"Created circuit breaker: {name}")
        return circuit_breaker

    def create_retry_policy(self, name: str, config: RetryConfig = None) -> RetryPolicy:
        """Create and register retry policy"""
        
        retry_policy = RetryPolicy(config)
        self.retry_policies[name] = retry_policy
        
        self.logger.info(f"Created retry policy: {name}")
        return retry_policy

    def create_bulkhead(self, name: str, config: BulkheadConfig = None) -> BulkheadIsolator:
        """Create and register bulkhead isolator"""
        
        bulkhead = BulkheadIsolator(name, config)
        self.bulkheads[name] = bulkhead
        
        self.logger.info(f"Created bulkhead: {name}")
        return bulkhead

    async def execute_with_resilience(self,
                                    func: Callable[..., Awaitable],
                                    circuit_breaker_name: Optional[str] = None,
                                    retry_policy_name: Optional[str] = None,
                                    bulkhead_name: Optional[str] = None,
                                    *args, **kwargs) -> Any:
        """Execute function with full resilience patterns"""
        
        # Wrap function with selected patterns
        execution_func = func
        
        # Apply bulkhead isolation first (outermost)
        if bulkhead_name and bulkhead_name in self.bulkheads:
            bulkhead = self.bulkheads[bulkhead_name]
            execution_func = functools.partial(bulkhead.execute, execution_func)
        
        # Apply retry policy
        if retry_policy_name and retry_policy_name in self.retry_policies:
            retry_policy = self.retry_policies[retry_policy_name]
            execution_func = functools.partial(retry_policy.execute, execution_func)
        
        # Apply circuit breaker (innermost)
        if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[circuit_breaker_name]
            return await circuit_breaker.call(execution_func, *args, **kwargs)
        
        # Execute without circuit breaker
        return await execution_func(*args, **kwargs)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics from all resilience components"""
        
        return {
            "circuit_breakers": {
                name: cb.get_state() 
                for name, cb in self.circuit_breakers.items()
            },
            "bulkheads": {
                name: bh.get_metrics() 
                for name, bh in self.bulkheads.items()
            },
            "summary": {
                "total_circuit_breakers": len(self.circuit_breakers),
                "total_retry_policies": len(self.retry_policies),
                "total_bulkheads": len(self.bulkheads),
                "open_circuit_breakers": sum(
                    1 for cb in self.circuit_breakers.values() 
                    if cb.state == CircuitState.OPEN
                )
            }
        }


# Custom exceptions
class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is open"""
    pass


class BulkheadRejectedException(Exception):
    """Raised when bulkhead rejects a call"""
    pass


# Decorator for easy usage
def circuit_breaker(name: str, 
                   config: CircuitBreakerConfig = None,
                   fallback_function: Optional[Callable] = None):
    """Decorator to apply circuit breaker to a function"""
    
    def decorator(func):
        cb = CircuitBreaker(name, config, fallback_function)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        
        return wrapper
    return decorator


def retry_on_failure(config: RetryConfig = None):
    """Decorator to apply retry policy to a function"""
    
    def decorator(func):
        retry_policy = RetryPolicy(config)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_policy.execute(func, *args, **kwargs)
        
        return wrapper
    return decorator


def bulkhead_isolation(name: str, config: BulkheadConfig = None):
    """Decorator to apply bulkhead isolation to a function"""
    
    def decorator(func):
        bulkhead = BulkheadIsolator(name, config)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await bulkhead.execute(func, *args, **kwargs)
        
        return wrapper
    return decorator


# Example usage
async def main():
    """Example usage of resilience patterns"""
    
    # Create resilience manager
    manager = ResilienceManager()
    
    # Configure circuit breaker
    cb_config = CircuitBreakerConfig(
        failure_threshold=3,
        timeout_duration=30.0,
        call_timeout=5.0
    )
    
    # Configure retry policy
    retry_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        max_attempts=3,
        base_delay=1.0
    )
    
    # Configure bulkhead
    bulkhead_config = BulkheadConfig(
        max_concurrent_calls=5,
        max_wait_duration=10.0
    )
    
    # Create components
    manager.create_circuit_breaker("external_api", cb_config)
    manager.create_retry_policy("external_api", retry_config)
    manager.create_bulkhead("external_api", bulkhead_config)
    
    # Example function that might fail
    async def external_api_call():
        await asyncio.sleep(0.1)
        if random.random() < 0.3:  # 30% failure rate
            raise Exception("API call failed")
        return "Success"
    
    # Execute with full resilience
    try:
        result = await manager.execute_with_resilience(
            external_api_call,
            circuit_breaker_name="external_api",
            retry_policy_name="external_api",
            bulkhead_name="external_api"
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Failed: {e}")
    
    # Get metrics
    metrics = manager.get_all_metrics()
    print(f"Resilience metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())