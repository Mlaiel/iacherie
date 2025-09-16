"""
Circuit Breaker Pattern - Advanced Service Protection & Resilience
© 2025 Fahed Mlaiel. All rights reserved.

Circuit breaker implementation providing service failure protection,
automatic fallback mechanisms, recovery detection, and resilience patterns.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
import time
import statistics
from collections import defaultdict, deque
import threading
import functools
import inspect

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


class FailureType(Enum):
    """Types of failures that can trigger circuit breaker"""
    TIMEOUT = "timeout"
    ERROR_RESPONSE = "error_response"
    EXCEPTION = "exception"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class RecoveryStrategy(Enum):
    """Recovery detection strategies"""
    TIME_BASED = "time_based"
    SUCCESS_THRESHOLD = "success_threshold"
    GRADUAL_RECOVERY = "gradual_recovery"
    HEALTH_CHECK = "health_check"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    name: str
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    timeout: float = 30.0  # seconds
    expected_exception: Optional[type] = None
    failure_threshold_percentage: float = 50.0
    minimum_requests: int = 10
    rolling_window_size: int = 100
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.TIME_BASED
    success_threshold: int = 3
    health_check_interval: int = 30
    enable_fallback: bool = True
    enable_monitoring: bool = True


@dataclass
class CircuitBreakerStats:
    """Circuit breaker statistics"""
    name: str
    state: CircuitState
    failure_count: int = 0
    success_count: int = 0
    timeout_count: int = 0
    total_requests: int = 0
    last_failure_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.utcnow)
    recovery_attempts: int = 0
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    average_response_time: float = 0.0
    failure_rate: float = 0.0


@dataclass
class FailureRecord:
    """Record of a service failure"""
    failure_type: FailureType
    timestamp: datetime
    exception: Optional[Exception] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    def __init__(self, circuit_name: str, message: str = None):
        self.circuit_name = circuit_name
        self.message = message or f"Circuit breaker '{circuit_name}' is open"
        super().__init__(self.message)


class CircuitBreaker:
    """
    Circuit Breaker Implementation
    
    Provides protection against cascade failures by:
    - Monitoring service call failures
    - Opening circuit when failure threshold is reached
    - Providing fallback mechanisms
    - Automatically attempting recovery
    - Collecting comprehensive metrics
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        """Initialize circuit breaker"""
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{config.name}")
        
        # Circuit state
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats(name=config.name, state=self.state)
        
        # Failure tracking
        self.failure_history: deque = deque(maxlen=config.rolling_window_size)
        self.recent_responses: deque = deque(maxlen=config.rolling_window_size)
        
        # Timing
        self.last_attempt_time: Optional[datetime] = None
        self.state_change_time = datetime.utcnow()
        
        # Fallback and recovery
        self.fallback_func: Optional[Callable] = None
        self.health_check_func: Optional[Callable] = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring
        self.state_change_callbacks: List[Callable] = []
        
        self.logger.info(f"Circuit breaker '{config.name}' initialized in {self.state.value} state")
    
    def __call__(self, func: Callable = None, *, fallback: Callable = None):
        """Decorator for protecting functions with circuit breaker"""
        if func is None:
            return functools.partial(self.__call__, fallback=fallback)
        
        if fallback:
            self.fallback_func = fallback
        
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return self.call(func, *args, **kwargs)
            return sync_wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection (sync)"""
        start_time = time.time()
        
        try:
            with self._lock:
                self._check_state()
                
                if self.state == CircuitState.OPEN:
                    self._record_request()
                    if self.fallback_func:
                        self.logger.debug(f"Circuit open, using fallback for {self.config.name}")
                        return self.fallback_func(*args, **kwargs)
                    else:
                        raise CircuitBreakerOpenException(self.config.name)
                
                # Record attempt
                self._record_request()
                self.last_attempt_time = datetime.utcnow()
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Record success
            response_time = time.time() - start_time
            with self._lock:
                self._record_success(response_time)
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            with self._lock:
                failure_type = self._classify_failure(e)
                self._record_failure(failure_type, e, response_time)
            
            # If circuit is now open and we have fallback, use it
            if self.state == CircuitState.OPEN and self.fallback_func:
                self.logger.warning(f"Function failed, circuit opened, using fallback for {self.config.name}")
                return self.fallback_func(*args, **kwargs)
            
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        start_time = time.time()
        
        try:
            with self._lock:
                self._check_state()
                
                if self.state == CircuitState.OPEN:
                    self._record_request()
                    if self.fallback_func:
                        self.logger.debug(f"Circuit open, using fallback for {self.config.name}")
                        if inspect.iscoroutinefunction(self.fallback_func):
                            return await self.fallback_func(*args, **kwargs)
                        else:
                            return self.fallback_func(*args, **kwargs)
                    else:
                        raise CircuitBreakerOpenException(self.config.name)
                
                # Record attempt
                self._record_request()
                self.last_attempt_time = datetime.utcnow()
            
            # Execute the async function with timeout
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            except asyncio.TimeoutError:
                response_time = time.time() - start_time
                with self._lock:
                    self._record_failure(FailureType.TIMEOUT, None, response_time)
                raise
            
            # Record success
            response_time = time.time() - start_time
            with self._lock:
                self._record_success(response_time)
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            with self._lock:
                failure_type = self._classify_failure(e)
                self._record_failure(failure_type, e, response_time)
            
            # If circuit is now open and we have fallback, use it
            if self.state == CircuitState.OPEN and self.fallback_func:
                self.logger.warning(f"Async function failed, circuit opened, using fallback for {self.config.name}")
                if inspect.iscoroutinefunction(self.fallback_func):
                    return await self.fallback_func(*args, **kwargs)
                else:
                    return self.fallback_func(*args, **kwargs)
            
            raise
    
    def set_fallback(self, fallback_func: Callable):
        """Set fallback function"""
        self.fallback_func = fallback_func
        self.logger.info(f"Fallback function set for circuit breaker '{self.config.name}'")
    
    def set_health_check(self, health_check_func: Callable):
        """Set health check function"""
        self.health_check_func = health_check_func
        self.logger.info(f"Health check function set for circuit breaker '{self.config.name}'")
    
    def add_state_change_callback(self, callback: Callable):
        """Add callback for state changes"""
        self.state_change_callbacks.append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        with self._lock:
            return {
                "name": self.stats.name,
                "state": self.state.value,
                "failure_count": self.stats.failure_count,
                "success_count": self.stats.success_count,
                "timeout_count": self.stats.timeout_count,
                "total_requests": self.stats.total_requests,
                "failure_rate": self.stats.failure_rate,
                "average_response_time": self.stats.average_response_time,
                "consecutive_failures": self.stats.consecutive_failures,
                "consecutive_successes": self.stats.consecutive_successes,
                "recovery_attempts": self.stats.recovery_attempts,
                "last_failure_time": self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
                "state_changed_at": self.stats.state_changed_at.isoformat(),
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "timeout": self.config.timeout,
                    "failure_threshold_percentage": self.config.failure_threshold_percentage,
                    "minimum_requests": self.config.minimum_requests
                }
            }
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        with self._lock:
            self._change_state(CircuitState.CLOSED)
            self.stats.failure_count = 0
            self.stats.success_count = 0
            self.stats.consecutive_failures = 0
            self.stats.consecutive_successes = 0
            self.stats.recovery_attempts = 0
            self.failure_history.clear()
            self.recent_responses.clear()
            
        self.logger.info(f"Circuit breaker '{self.config.name}' reset to closed state")
    
    def force_open(self):
        """Force circuit breaker to open state"""
        with self._lock:
            self._change_state(CircuitState.OPEN)
        
        self.logger.warning(f"Circuit breaker '{self.config.name}' forced to open state")
    
    def _check_state(self):
        """Check and update circuit breaker state"""
        current_time = datetime.utcnow()
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            time_since_open = (current_time - self.state_change_time).total_seconds()
            
            if time_since_open >= self.config.recovery_timeout:
                if self.config.recovery_strategy == RecoveryStrategy.HEALTH_CHECK and self.health_check_func:
                    try:
                        if inspect.iscoroutinefunction(self.health_check_func):
                            # For async health checks, we can't await here in sync context
                            # Move to half-open and let the next call handle it
                            self._change_state(CircuitState.HALF_OPEN)
                        else:
                            if self.health_check_func():
                                self._change_state(CircuitState.HALF_OPEN)
                            else:
                                # Reset timer for next health check
                                self.state_change_time = current_time
                    except Exception as e:
                        self.logger.warning(f"Health check failed for {self.config.name}: {e}")
                        self.state_change_time = current_time
                else:
                    self._change_state(CircuitState.HALF_OPEN)
        
        elif self.state == CircuitState.HALF_OPEN:
            # Check if we have enough successes to close the circuit
            if self.stats.consecutive_successes >= self.config.success_threshold:
                self._change_state(CircuitState.CLOSED)
        
        elif self.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            if self._should_open_circuit():
                self._change_state(CircuitState.OPEN)
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Need minimum number of requests
        if self.stats.total_requests < self.config.minimum_requests:
            return False
        
        # Check consecutive failures threshold
        if self.stats.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Check failure rate over rolling window
        if len(self.recent_responses) >= self.config.minimum_requests:
            failures_in_window = sum(1 for success in self.recent_responses if not success)
            failure_rate = (failures_in_window / len(self.recent_responses)) * 100
            
            if failure_rate >= self.config.failure_threshold_percentage:
                return True
        
        return False
    
    def _record_request(self):
        """Record a request attempt"""
        self.stats.total_requests += 1
    
    def _record_success(self, response_time: float):
        """Record a successful request"""
        self.stats.success_count += 1
        self.stats.consecutive_successes += 1
        self.stats.consecutive_failures = 0
        
        # Update response time
        if self.stats.average_response_time == 0:
            self.stats.average_response_time = response_time
        else:
            self.stats.average_response_time = (
                self.stats.average_response_time + response_time
            ) / 2
        
        # Record in rolling window
        self.recent_responses.append(True)
        
        # Update failure rate
        self._update_failure_rate()
        
        self.logger.debug(f"Success recorded for {self.config.name}, response time: {response_time:.3f}s")
    
    def _record_failure(self, failure_type: FailureType, exception: Optional[Exception], response_time: float):
        """Record a failed request"""
        self.stats.failure_count += 1
        self.stats.consecutive_failures += 1
        self.stats.consecutive_successes = 0
        self.stats.last_failure_time = datetime.utcnow()
        
        if failure_type == FailureType.TIMEOUT:
            self.stats.timeout_count += 1
        
        # Record failure details
        failure_record = FailureRecord(
            failure_type=failure_type,
            timestamp=datetime.utcnow(),
            exception=exception,
            response_time=response_time,
            error_message=str(exception) if exception else None
        )
        
        self.failure_history.append(failure_record)
        
        # Record in rolling window
        self.recent_responses.append(False)
        
        # Update failure rate
        self._update_failure_rate()
        
        self.logger.warning(
            f"Failure recorded for {self.config.name}: {failure_type.value}, "
            f"consecutive failures: {self.stats.consecutive_failures}"
        )
    
    def _update_failure_rate(self):
        """Update failure rate calculation"""
        if self.stats.total_requests > 0:
            self.stats.failure_rate = (self.stats.failure_count / self.stats.total_requests) * 100
    
    def _classify_failure(self, exception: Exception) -> FailureType:
        """Classify the type of failure"""
        if isinstance(exception, asyncio.TimeoutError):
            return FailureType.TIMEOUT
        elif isinstance(exception, ConnectionError):
            return FailureType.DEPENDENCY_FAILURE
        elif isinstance(exception, MemoryError):
            return FailureType.RESOURCE_EXHAUSTION
        elif self.config.expected_exception and isinstance(exception, self.config.expected_exception):
            return FailureType.ERROR_RESPONSE
        else:
            return FailureType.EXCEPTION
    
    def _change_state(self, new_state: CircuitState):
        """Change circuit breaker state"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.stats.state = new_state
            self.state_change_time = datetime.utcnow()
            self.stats.state_changed_at = self.state_change_time
            
            if new_state == CircuitState.HALF_OPEN:
                self.stats.recovery_attempts += 1
            
            self.logger.info(f"Circuit breaker '{self.config.name}' state changed: {old_state.value} -> {new_state.value}")
            
            # Notify callbacks
            for callback in self.state_change_callbacks:
                try:
                    callback(self.config.name, old_state, new_state, self.get_stats())
                except Exception as e:
                    self.logger.error(f"State change callback failed: {e}")


class CircuitBreakerManager:
    """
    Circuit Breaker Manager
    
    Manages multiple circuit breakers and provides:
    - Centralized configuration
    - Monitoring and metrics collection
    - Bulk operations
    - Health checking coordination
    """
    
    def __init__(self):
        """Initialize circuit breaker manager"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.global_stats = {
            "total_circuits": 0,
            "open_circuits": 0,
            "half_open_circuits": 0,
            "closed_circuits": 0,
            "total_requests": 0,
            "total_failures": 0,
            "global_failure_rate": 0.0
        }
        
        # Monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_interval = 30  # seconds
        self._running = False
        
        self.logger.info("Circuit Breaker Manager initialized")
    
    def create_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        **kwargs
    ) -> CircuitBreaker:
        """Create and register a new circuit breaker"""
        if name in self.circuit_breakers:
            raise ValueError(f"Circuit breaker '{name}' already exists")
        
        if config is None:
            config = CircuitBreakerConfig(name=name, **kwargs)
        
        circuit_breaker = CircuitBreaker(config)
        circuit_breaker.add_state_change_callback(self._on_state_change)
        
        self.circuit_breakers[name] = circuit_breaker
        self.global_stats["total_circuits"] += 1
        self.global_stats["closed_circuits"] += 1
        
        self.logger.info(f"Created circuit breaker '{name}'")
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker"""
        if name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[name]
            del self.circuit_breakers[name]
            
            self.global_stats["total_circuits"] -= 1
            state = circuit_breaker.state
            
            if state == CircuitState.OPEN:
                self.global_stats["open_circuits"] -= 1
            elif state == CircuitState.HALF_OPEN:
                self.global_stats["half_open_circuits"] -= 1
            else:
                self.global_stats["closed_circuits"] -= 1
            
            self.logger.info(f"Removed circuit breaker '{name}'")
            return True
        
        return False
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all circuit breakers"""
        circuit_stats = {}
        total_requests = 0
        total_failures = 0
        
        for name, circuit_breaker in self.circuit_breakers.items():
            stats = circuit_breaker.get_stats()
            circuit_stats[name] = stats
            total_requests += stats["total_requests"]
            total_failures += stats["failure_count"]
        
        # Update global stats
        self.global_stats["total_requests"] = total_requests
        self.global_stats["total_failures"] = total_failures
        self.global_stats["global_failure_rate"] = (
            (total_failures / total_requests * 100) if total_requests > 0 else 0.0
        )
        
        return {
            "global_stats": self.global_stats,
            "circuit_breakers": circuit_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for circuit_breaker in self.circuit_breakers.values():
            circuit_breaker.reset()
        
        self.logger.info("Reset all circuit breakers")
    
    def get_open_circuits(self) -> List[str]:
        """Get list of circuit breakers in open state"""
        return [
            name for name, cb in self.circuit_breakers.items()
            if cb.state == CircuitState.OPEN
        ]
    
    def get_degraded_circuits(self) -> List[str]:
        """Get list of circuit breakers in degraded state (open or half-open)"""
        return [
            name for name, cb in self.circuit_breakers.items()
            if cb.state in [CircuitState.OPEN, CircuitState.HALF_OPEN]
        ]
    
    async def start_monitoring(self):
        """Start monitoring circuit breakers"""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_worker())
        self.logger.info("Started circuit breaker monitoring")
    
    async def stop_monitoring(self):
        """Stop monitoring circuit breakers"""
        if not self._running:
            return
        
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped circuit breaker monitoring")
    
    def _on_state_change(self, name: str, old_state: CircuitState, new_state: CircuitState, stats: Dict[str, Any]):
        """Handle circuit breaker state changes"""
        # Update global counters
        if old_state == CircuitState.OPEN:
            self.global_stats["open_circuits"] -= 1
        elif old_state == CircuitState.HALF_OPEN:
            self.global_stats["half_open_circuits"] -= 1
        else:
            self.global_stats["closed_circuits"] -= 1
        
        if new_state == CircuitState.OPEN:
            self.global_stats["open_circuits"] += 1
        elif new_state == CircuitState.HALF_OPEN:
            self.global_stats["half_open_circuits"] += 1
        else:
            self.global_stats["closed_circuits"] += 1
        
        self.logger.info(f"Circuit '{name}' state changed: {old_state.value} -> {new_state.value}")
    
    async def _monitoring_worker(self):
        """Background monitoring worker"""
        while self._running:
            try:
                await self._check_circuit_health()
                await asyncio.sleep(self._monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring worker error: {e}")
                await asyncio.sleep(10)
    
    async def _check_circuit_health(self):
        """Check health of all circuit breakers"""
        open_circuits = self.get_open_circuits()
        
        if open_circuits:
            self.logger.warning(f"Open circuits detected: {', '.join(open_circuits)}")
        
        # Check for circuits with high failure rates
        high_failure_circuits = []
        for name, cb in self.circuit_breakers.items():
            stats = cb.get_stats()
            if stats["failure_rate"] > 25.0 and stats["total_requests"] > 10:
                high_failure_circuits.append(name)
        
        if high_failure_circuits:
            self.logger.warning(f"High failure rate circuits: {', '.join(high_failure_circuits)}")


# Global circuit breaker manager instance
_global_manager = CircuitBreakerManager()


def circuit_breaker(
    name: str = None,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    timeout: float = 30.0,
    fallback: Callable = None,
    **kwargs
) -> Callable:
    """
    Decorator for creating circuit breakers
    
    Args:
        name: Circuit breaker name (defaults to function name)
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before attempting recovery
        timeout: Request timeout in seconds
        fallback: Fallback function to call when circuit is open
        **kwargs: Additional configuration options
    """
    def decorator(func: Callable):
        circuit_name = name or func.__name__
        
        # Create circuit breaker if it doesn't exist
        if not _global_manager.get_circuit_breaker(circuit_name):
            config = CircuitBreakerConfig(
                name=circuit_name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                timeout=timeout,
                **kwargs
            )
            cb = _global_manager.create_circuit_breaker(circuit_name, config)
            
            if fallback:
                cb.set_fallback(fallback)
        else:
            cb = _global_manager.get_circuit_breaker(circuit_name)
        
        return cb(func, fallback=fallback)
    
    return decorator


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get the global circuit breaker manager"""
    return _global_manager


# Example usage
if __name__ == "__main__":
    async def main():
        # Create circuit breaker manager
        manager = CircuitBreakerManager()
        await manager.start_monitoring()
        
        # Create a circuit breaker
        config = CircuitBreakerConfig(
            name="test_service",
            failure_threshold=3,
            recovery_timeout=10,
            timeout=5.0
        )
        
        cb = manager.create_circuit_breaker("test_service", config)
        
        # Fallback function
        def fallback_response():
            return {"error": "Service unavailable", "fallback": True}
        
        cb.set_fallback(fallback_response)
        
        # Protected function
        @cb
        async def unreliable_service():
            import random
            if random.random() < 0.7:  # 70% failure rate
                raise Exception("Service failed")
            return {"success": True, "data": "Hello World"}
        
        # Test the circuit breaker
        for i in range(20):
            try:
                result = await unreliable_service()
                print(f"Call {i+1}: {result}")
            except Exception as e:
                print(f"Call {i+1}: Error - {e}")
            
            await asyncio.sleep(0.5)
        
        # Print stats
        stats = manager.get_all_stats()
        print(json.dumps(stats, indent=2, default=str))
        
        await manager.stop_monitoring()
    
    asyncio.run(main())