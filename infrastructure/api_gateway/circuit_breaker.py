"""
Circuit Breaker Pattern - Service Failure Protection
© 2025 Fahed Mlaiel. All rights reserved.

Enterprise circuit breaker providing service failure protection, automatic
fallback mechanisms, recovery detection, and circuit state management.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import time
import threading
from collections import deque
import statistics

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"           # Normal operation
    OPEN = "open"              # Failure detected, blocking requests
    HALF_OPEN = "half_open"    # Testing if service recovered


class FailureType(Enum):
    """Types of failures"""
    TIMEOUT = "timeout"
    ERROR = "error"
    EXCEPTION = "exception"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"


class FallbackStrategy(Enum):
    """Fallback strategies"""
    RETURN_NONE = "return_none"
    RETURN_DEFAULT = "return_default"
    RETURN_CACHED = "return_cached"
    REDIRECT_TO_BACKUP = "redirect_to_backup"
    GRACEFUL_DEGRADATION = "graceful_degradation"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    name: str
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    reset_timeout_seconds: float = 60.0
    half_open_max_calls: int = 3
    sliding_window_size: int = 100
    minimum_throughput: int = 10
    error_rate_threshold: float = 0.5
    slow_call_duration_threshold: float = 10.0
    slow_call_rate_threshold: float = 0.5
    enabled: bool = True


@dataclass
class ServiceCall:
    """Service call record"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_seconds: float = 0.0
    success: bool = False
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_transitions: int = 0
    current_state: CircuitState = CircuitState.CLOSED
    last_state_change: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    avg_call_duration: float = 0.0
    error_rate: float = 0.0
    slow_call_rate: float = 0.0


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation
    
    Protects services from cascading failures by:
    - Monitoring service health
    - Opening circuit on failures
    - Testing recovery periodically
    - Providing fallback mechanisms
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics(current_state=self.state)
        
        # Call history
        self.call_history: deque = deque(maxlen=config.sliding_window_size)
        
        # State management
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change_time: datetime = datetime.utcnow()
        self.consecutive_failures: int = 0
        self.consecutive_successes: int = 0
        self.half_open_calls: int = 0
        
        # Fallback configuration
        self.fallback_function: Optional[Callable] = None
        self.fallback_strategy: FallbackStrategy = FallbackStrategy.RETURN_NONE
        self.cached_response: Optional[Any] = None
        self.default_response: Optional[Any] = None
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info(f"Circuit breaker '{config.name}' initialized")
    
    def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Execute function through circuit breaker
        
        Args:
            func: Function to execute
            *args: Function arguments
            fallback: Optional fallback function
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback result
            
        Raises:
            Exception: If circuit is open and no fallback is provided
        """
        if not self.config.enabled:
            return func(*args, **kwargs)
        
        with self.lock:
            # Check if circuit allows the call
            if not self._can_attempt_call():
                self.metrics.rejected_calls += 1
                logger.warning(
                    f"Circuit breaker '{self.config.name}' is {self.state.value}, "
                    "rejecting call"
                )
                return self._execute_fallback(fallback, *args, **kwargs)
            
            # Execute the call
            start_time = time.time()
            call_record = ServiceCall()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success
                call_record.duration_seconds = duration
                call_record.success = True
                self._record_success(call_record)
                
                # Cache successful response
                self.cached_response = result
                
                return result
                
            except asyncio.TimeoutError as e:
                duration = time.time() - start_time
                call_record.duration_seconds = duration
                call_record.failure_type = FailureType.TIMEOUT
                call_record.error_message = str(e)
                self._record_failure(call_record)
                
                logger.error(
                    f"Timeout in circuit breaker '{self.config.name}': {e}"
                )
                return self._execute_fallback(fallback, *args, **kwargs)
                
            except Exception as e:
                duration = time.time() - start_time
                call_record.duration_seconds = duration
                call_record.failure_type = FailureType.EXCEPTION
                call_record.error_message = str(e)
                self._record_failure(call_record)
                
                logger.error(
                    f"Exception in circuit breaker '{self.config.name}': {e}"
                )
                return self._execute_fallback(fallback, *args, **kwargs)
    
    async def call_async(
        self,
        func: Coroutine,
        fallback: Optional[Callable] = None,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Execute async function through circuit breaker
        
        Args:
            func: Async function to execute
            fallback: Optional fallback function
            timeout: Optional timeout override
            
        Returns:
            Function result or fallback result
        """
        if not self.config.enabled:
            return await func
        
        with self.lock:
            # Check if circuit allows the call
            if not self._can_attempt_call():
                self.metrics.rejected_calls += 1
                logger.warning(
                    f"Circuit breaker '{self.config.name}' is {self.state.value}, "
                    "rejecting async call"
                )
                if fallback:
                    return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
                return None
        
        # Execute the call
        start_time = time.time()
        call_record = ServiceCall()
        timeout_value = timeout or self.config.timeout_seconds
        
        try:
            result = await asyncio.wait_for(func, timeout=timeout_value)
            duration = time.time() - start_time
            
            # Record success
            call_record.duration_seconds = duration
            call_record.success = True
            self._record_success(call_record)
            
            # Cache successful response
            self.cached_response = result
            
            return result
            
        except asyncio.TimeoutError as e:
            duration = time.time() - start_time
            call_record.duration_seconds = duration
            call_record.failure_type = FailureType.TIMEOUT
            call_record.error_message = str(e)
            self._record_failure(call_record)
            
            logger.error(
                f"Timeout in async circuit breaker '{self.config.name}': {e}"
            )
            if fallback:
                return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
            return None
            
        except Exception as e:
            duration = time.time() - start_time
            call_record.duration_seconds = duration
            call_record.failure_type = FailureType.EXCEPTION
            call_record.error_message = str(e)
            self._record_failure(call_record)
            
            logger.error(
                f"Exception in async circuit breaker '{self.config.name}': {e}"
            )
            if fallback:
                return await fallback() if asyncio.iscoroutinefunction(fallback) else fallback()
            return None
    
    def _can_attempt_call(self) -> bool:
        """
        Check if circuit allows attempting a call
        
        Returns:
            True if call is allowed, False otherwise
        """
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if reset timeout has elapsed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.config.reset_timeout_seconds:
                    self._transition_to_half_open()
                    return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def _record_success(self, call_record: ServiceCall) -> None:
        """
        Record successful call
        
        Args:
            call_record: Service call record
        """
        with self.lock:
            self.call_history.append(call_record)
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
                
                # Check if service has recovered
                if self.consecutive_successes >= self.config.success_threshold:
                    self._transition_to_closed()
            
            self._update_metrics()
    
    def _record_failure(self, call_record: ServiceCall) -> None:
        """
        Record failed call
        
        Args:
            call_record: Service call record
        """
        with self.lock:
            self.call_history.append(call_record)
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.last_failure = call_record.timestamp
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_failure_time = datetime.utcnow()
            
            if self.state == CircuitState.HALF_OPEN:
                # Service still unhealthy, reopen circuit
                self._transition_to_open()
            elif self.state == CircuitState.CLOSED:
                # Check if threshold exceeded
                if self._should_open_circuit():
                    self._transition_to_open()
            
            self._update_metrics()
    
    def _should_open_circuit(self) -> bool:
        """
        Determine if circuit should be opened
        
        Returns:
            True if circuit should open, False otherwise
        """
        # Check consecutive failures
        if self.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Check error rate
        recent_calls = list(self.call_history)[-self.config.minimum_throughput:]
        if len(recent_calls) >= self.config.minimum_throughput:
            failed_calls = sum(1 for c in recent_calls if not c.success)
            error_rate = failed_calls / len(recent_calls)
            if error_rate >= self.config.error_rate_threshold:
                return True
        
        # Check slow call rate
        if len(recent_calls) >= self.config.minimum_throughput:
            slow_calls = sum(
                1 for c in recent_calls
                if c.duration_seconds >= self.config.slow_call_duration_threshold
            )
            slow_call_rate = slow_calls / len(recent_calls)
            if slow_call_rate >= self.config.slow_call_rate_threshold:
                return True
        
        return False
    
    def _transition_to_open(self) -> None:
        """Transition circuit to OPEN state"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change_time = datetime.utcnow()
            self.metrics.current_state = self.state
            self.metrics.last_state_change = self.last_state_change_time
            self.metrics.state_transitions += 1
            self.half_open_calls = 0
            
            logger.warning(
                f"Circuit breaker '{self.config.name}' transitioned to OPEN "
                f"(consecutive failures: {self.consecutive_failures})"
            )
    
    def _transition_to_half_open(self) -> None:
        """Transition circuit to HALF_OPEN state"""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.last_state_change_time = datetime.utcnow()
            self.metrics.current_state = self.state
            self.metrics.last_state_change = self.last_state_change_time
            self.metrics.state_transitions += 1
            self.half_open_calls = 0
            
            logger.info(
                f"Circuit breaker '{self.config.name}' transitioned to HALF_OPEN, "
                "testing service recovery"
            )
    
    def _transition_to_closed(self) -> None:
        """Transition circuit to CLOSED state"""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.last_state_change_time = datetime.utcnow()
            self.metrics.current_state = self.state
            self.metrics.last_state_change = self.last_state_change_time
            self.metrics.state_transitions += 1
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            self.half_open_calls = 0
            
            logger.info(
                f"Circuit breaker '{self.config.name}' transitioned to CLOSED, "
                "service recovered"
            )
    
    def _update_metrics(self) -> None:
        """Update circuit breaker metrics"""
        recent_calls = list(self.call_history)
        
        if recent_calls:
            # Calculate error rate
            failed = sum(1 for c in recent_calls if not c.success)
            self.metrics.error_rate = failed / len(recent_calls)
            
            # Calculate slow call rate
            slow = sum(
                1 for c in recent_calls
                if c.duration_seconds >= self.config.slow_call_duration_threshold
            )
            self.metrics.slow_call_rate = slow / len(recent_calls)
            
            # Calculate average call duration
            durations = [c.duration_seconds for c in recent_calls]
            self.metrics.avg_call_duration = statistics.mean(durations)
        
        self.metrics.consecutive_failures = self.consecutive_failures
        self.metrics.consecutive_successes = self.consecutive_successes
    
    def _execute_fallback(
        self,
        fallback: Optional[Callable],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute fallback function
        
        Args:
            fallback: Fallback function
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Fallback result
        """
        if fallback:
            try:
                return fallback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fallback function failed: {e}")
        
        # Execute configured fallback strategy
        if self.fallback_strategy == FallbackStrategy.RETURN_DEFAULT:
            return self.default_response
        elif self.fallback_strategy == FallbackStrategy.RETURN_CACHED:
            return self.cached_response
        elif self.fallback_strategy == FallbackStrategy.GRACEFUL_DEGRADATION:
            return self._graceful_degradation()
        
        return None
    
    def _graceful_degradation(self) -> Dict[str, Any]:
        """
        Provide gracefully degraded response
        
        Returns:
            Degraded response
        """
        return {
            'status': 'degraded',
            'message': 'Service temporarily unavailable',
            'circuit_breaker': self.config.name,
            'retry_after': self.config.reset_timeout_seconds
        }
    
    def set_fallback(
        self,
        strategy: FallbackStrategy,
        fallback_func: Optional[Callable] = None,
        default_response: Optional[Any] = None
    ) -> None:
        """
        Configure fallback behavior
        
        Args:
            strategy: Fallback strategy
            fallback_func: Optional fallback function
            default_response: Optional default response
        """
        self.fallback_strategy = strategy
        self.fallback_function = fallback_func
        self.default_response = default_response
        
        logger.info(
            f"Configured fallback for '{self.config.name}': {strategy.value}"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics
        
        Returns:
            Circuit breaker metrics
        """
        return {
            'name': self.config.name,
            'state': self.state.value,
            'total_calls': self.metrics.total_calls,
            'successful_calls': self.metrics.successful_calls,
            'failed_calls': self.metrics.failed_calls,
            'rejected_calls': self.metrics.rejected_calls,
            'error_rate': round(self.metrics.error_rate, 4),
            'slow_call_rate': round(self.metrics.slow_call_rate, 4),
            'avg_call_duration_ms': round(self.metrics.avg_call_duration * 1000, 2),
            'consecutive_failures': self.metrics.consecutive_failures,
            'consecutive_successes': self.metrics.consecutive_successes,
            'state_transitions': self.metrics.state_transitions,
            'last_state_change': self.metrics.last_state_change.isoformat() if self.metrics.last_state_change else None,
            'last_failure': self.metrics.last_failure.isoformat() if self.metrics.last_failure else None
        }
    
    def reset(self) -> None:
        """Reset circuit breaker to initial state"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.metrics = CircuitBreakerMetrics(current_state=self.state)
            self.call_history.clear()
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            self.half_open_calls = 0
            self.last_failure_time = None
            
            logger.info(f"Circuit breaker '{self.config.name}' reset")


class CircuitBreakerRegistry:
    """
    Circuit Breaker Registry
    
    Manages multiple circuit breakers for different services
    """
    
    def __init__(self):
        """Initialize circuit breaker registry"""
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.RLock()
        
        logger.info("Circuit breaker registry initialized")
    
    def register(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """
        Register a new circuit breaker
        
        Args:
            name: Circuit breaker name
            config: Optional configuration (uses defaults if not provided)
            
        Returns:
            Circuit breaker instance
        """
        with self.lock:
            if name in self.breakers:
                logger.warning(f"Circuit breaker '{name}' already registered")
                return self.breakers[name]
            
            if not config:
                config = CircuitBreakerConfig(name=name)
            
            breaker = CircuitBreaker(config)
            self.breakers[name] = breaker
            
            logger.info(f"Registered circuit breaker: {name}")
            return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """
        Get circuit breaker by name
        
        Args:
            name: Circuit breaker name
            
        Returns:
            Circuit breaker instance or None
        """
        return self.breakers.get(name)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all circuit breakers
        
        Returns:
            Dictionary of circuit breaker metrics
        """
        return {
            name: breaker.get_metrics()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self) -> None:
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
        
        logger.info("Reset all circuit breakers")


# Creator platform circuit breaker configuration
IACHERIE_CIRCUIT_BREAKER_CONFIG = {
    'services': {
        'ai_processing': {
            'failure_threshold': 5,
            'timeout_seconds': 30.0,
            'reset_timeout_seconds': 60.0,
            'error_rate_threshold': 0.5
        },
        'content_upload': {
            'failure_threshold': 3,
            'timeout_seconds': 60.0,
            'reset_timeout_seconds': 30.0,
            'error_rate_threshold': 0.3
        },
        'distribution': {
            'failure_threshold': 10,
            'timeout_seconds': 15.0,
            'reset_timeout_seconds': 45.0,
            'error_rate_threshold': 0.4
        },
        'monetization': {
            'failure_threshold': 2,
            'timeout_seconds': 10.0,
            'reset_timeout_seconds': 120.0,
            'error_rate_threshold': 0.1
        },
        'analytics': {
            'failure_threshold': 7,
            'timeout_seconds': 20.0,
            'reset_timeout_seconds': 30.0,
            'error_rate_threshold': 0.6
        }
    },
    'global_defaults': {
        'success_threshold': 2,
        'half_open_max_calls': 3,
        'sliding_window_size': 100,
        'minimum_throughput': 10,
        'slow_call_duration_threshold': 10.0,
        'slow_call_rate_threshold': 0.5
    },
    'fallback_strategies': {
        'ai_processing': 'graceful_degradation',
        'content_upload': 'return_default',
        'distribution': 'return_cached',
        'monetization': 'return_none',
        'analytics': 'return_cached'
    }
}
