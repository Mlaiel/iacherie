"""
Circuit Breaker Implementation for Inter-Service Resilience
Provides fault tolerance and graceful degradation for service calls

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Any, Optional, Dict, Callable, Union, List
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import aiohttp
import statistics
from functools import wraps


logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5  # Number of failures to open circuit
    recovery_timeout: float = 60.0  # Seconds to wait before trying again
    success_threshold: int = 3  # Successes needed to close circuit in half-open
    timeout: float = 30.0  # Request timeout in seconds
    slow_call_duration_threshold: float = 5.0  # Threshold for slow calls
    slow_call_rate_threshold: float = 0.5  # Percentage of slow calls to trigger
    minimum_number_of_calls: int = 10  # Minimum calls before evaluating
    sliding_window_size: int = 100  # Size of sliding window for metrics
    
    # Exponential backoff configuration
    max_backoff_seconds: float = 300.0
    backoff_multiplier: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changes: List[Dict[str, Any]] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)


class CircuitBreakerError(Exception):
    """Circuit breaker specific exception"""
    pass


class CircuitBreakerOpenError(CircuitBreakerError):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Professional circuit breaker implementation with advanced features
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.lock = asyncio.Lock()
        self.next_attempt_time = 0.0
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_state_change = time.time()
        
        # Sliding window for call tracking
        self.call_window: List[Dict[str, Any]] = []
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {config}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._check_state()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if exc_type is None:
            await self._record_success()
        else:
            await self._record_failure(exc_val)
        return False
    
    def __call__(self, func):
        """Decorator for protecting functions"""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with self:
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # For sync functions, we need to handle this differently
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                async def async_call():
                    async with self:
                        return func(*args, **kwargs)
                
                return loop.run_until_complete(async_call())
            return sync_wrapper
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function call with circuit breaker protection"""
        async with self:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
    
    async def _check_state(self):
        """Check circuit breaker state and decide if call should proceed"""
        async with self.lock:
            current_time = time.time()
            
            if self.state == CircuitBreakerState.OPEN:
                if current_time >= self.next_attempt_time:
                    # Transition to half-open
                    await self._transition_to_half_open()
                else:
                    # Still in open state, reject call
                    self.metrics.rejected_calls += 1
                    remaining_time = self.next_attempt_time - current_time
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Retry in {remaining_time:.1f} seconds"
                    )
            
            # Update metrics
            self.metrics.total_calls += 1
            
            # Clean up old entries from sliding window
            self._cleanup_call_window(current_time)
    
    async def _record_success(self):
        """Record a successful call"""
        async with self.lock:
            current_time = time.time()
            
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = current_time
            self.consecutive_failures = 0
            self.consecutive_successes += 1
            
            # Add to call window
            self.call_window.append({
                'timestamp': current_time,
                'success': True,
                'duration': 0  # Will be updated if timing info available
            })
            
            # Check if we should close the circuit from half-open
            if (self.state == CircuitBreakerState.HALF_OPEN and
                self.consecutive_successes >= self.config.success_threshold):
                await self._transition_to_closed()
            
            logger.debug(f"Circuit breaker '{self.name}' recorded success")
    
    async def _record_failure(self, exception: Optional[Exception] = None):
        """Record a failed call"""
        async with self.lock:
            current_time = time.time()
            
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = current_time
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            
            # Add to call window
            self.call_window.append({
                'timestamp': current_time,
                'success': False,
                'exception': str(exception) if exception else None
            })
            
            # Check if we should open the circuit
            if (self.state != CircuitBreakerState.OPEN and
                self._should_open_circuit()):
                await self._transition_to_open()
            
            logger.warning(
                f"Circuit breaker '{self.name}' recorded failure: {exception}"
            )
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened based on current metrics"""
        # Simple threshold check
        if self.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Advanced sliding window analysis
        if len(self.call_window) < self.config.minimum_number_of_calls:
            return False
        
        recent_calls = self.call_window[-self.config.sliding_window_size:]
        
        # Calculate failure rate
        failures = sum(1 for call in recent_calls if not call['success'])
        failure_rate = failures / len(recent_calls)
        
        # Calculate slow call rate (if timing info available)
        slow_calls = sum(
            1 for call in recent_calls 
            if call.get('duration', 0) > self.config.slow_call_duration_threshold
        )
        slow_call_rate = slow_calls / len(recent_calls)
        
        # Open circuit if thresholds exceeded
        return (failure_rate > 0.5 or  # 50% failure rate
                slow_call_rate > self.config.slow_call_rate_threshold)
    
    async def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        old_state = self.state
        self.state = CircuitBreakerState.OPEN
        self.last_state_change = time.time()
        
        # Calculate next attempt time with exponential backoff
        backoff_seconds = min(
            self.config.recovery_timeout * 
            (self.config.backoff_multiplier ** min(self.consecutive_failures - 1, 10)),
            self.config.max_backoff_seconds
        )
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            import random
            backoff_seconds *= (0.5 + random.random() * 0.5)
        
        self.next_attempt_time = time.time() + backoff_seconds
        
        # Record state change
        self.metrics.state_changes.append({
            'timestamp': time.time(),
            'from_state': old_state.value,
            'to_state': self.state.value,
            'reason': 'failure_threshold_exceeded',
            'consecutive_failures': self.consecutive_failures,
            'next_attempt_time': self.next_attempt_time
        })
        
        logger.warning(
            f"Circuit breaker '{self.name}' opened due to {self.consecutive_failures} "
            f"consecutive failures. Next attempt in {backoff_seconds:.1f} seconds"
        )
    
    async def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        old_state = self.state
        self.state = CircuitBreakerState.HALF_OPEN
        self.last_state_change = time.time()
        self.consecutive_successes = 0
        
        # Record state change
        self.metrics.state_changes.append({
            'timestamp': time.time(),
            'from_state': old_state.value,
            'to_state': self.state.value,
            'reason': 'recovery_timeout_elapsed'
        })
        
        logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")
    
    async def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        old_state = self.state
        self.state = CircuitBreakerState.CLOSED
        self.last_state_change = time.time()
        self.consecutive_failures = 0
        
        # Record state change
        self.metrics.state_changes.append({
            'timestamp': time.time(),
            'from_state': old_state.value,
            'to_state': self.state.value,
            'reason': 'recovery_success',
            'consecutive_successes': self.consecutive_successes
        })
        
        logger.info(
            f"Circuit breaker '{self.name}' closed after {self.consecutive_successes} "
            "consecutive successes"
        )
    
    def _cleanup_call_window(self, current_time: float):
        """Remove old entries from call window"""
        cutoff_time = current_time - 300  # Keep last 5 minutes
        self.call_window = [
            call for call in self.call_window 
            if call['timestamp'] > cutoff_time
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current circuit breaker metrics"""
        current_time = time.time()
        self._cleanup_call_window(current_time)
        
        # Calculate rates and percentiles
        recent_calls = self.call_window[-self.config.sliding_window_size:]
        
        failure_rate = 0.0
        success_rate = 0.0
        avg_response_time = 0.0
        p95_response_time = 0.0
        
        if recent_calls:
            failures = sum(1 for call in recent_calls if not call['success'])
            failure_rate = failures / len(recent_calls)
            success_rate = 1.0 - failure_rate
            
            # Response time statistics (if available)
            response_times = [
                call['duration'] for call in recent_calls 
                if 'duration' in call and call['duration'] > 0
            ]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]
        
        return {
            'name': self.name,
            'state': self.state.value,
            'last_state_change': self.last_state_change,
            'total_calls': self.metrics.total_calls,
            'successful_calls': self.metrics.successful_calls,
            'failed_calls': self.metrics.failed_calls,
            'rejected_calls': self.metrics.rejected_calls,
            'consecutive_failures': self.consecutive_failures,
            'consecutive_successes': self.consecutive_successes,
            'failure_rate': failure_rate,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'p95_response_time': p95_response_time,
            'next_attempt_time': self.next_attempt_time,
            'time_until_next_attempt': max(0, self.next_attempt_time - current_time),
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold,
                'timeout': self.config.timeout
            }
        }
    
    async def reset(self):
        """Reset circuit breaker to initial state"""
        async with self.lock:
            self.state = CircuitBreakerState.CLOSED
            self.metrics = CircuitBreakerMetrics()
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            self.next_attempt_time = 0.0
            self.call_window.clear()
            self.last_state_change = time.time()
            
            logger.info(f"Circuit breaker '{self.name}' reset to initial state")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()
    
    def get_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self.breakers:
            effective_config = config or self.default_config
            self.breakers[name] = CircuitBreaker(name, effective_config)
        return self.breakers[name]
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all registered circuit breakers"""
        return {
            name: breaker.get_metrics() 
            for name, breaker in self.breakers.items()
        }
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            await breaker.reset()
    
    def remove_breaker(self, name: str):
        """Remove a circuit breaker from registry"""
        if name in self.breakers:
            del self.breakers[name]


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator to add circuit breaker protection to functions"""
    breaker = circuit_breaker_registry.get_breaker(name, config)
    return breaker


@asynccontextmanager
async def protected_call(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Context manager for circuit breaker protection"""
    breaker = circuit_breaker_registry.get_breaker(name, config)
    async with breaker:
        yield