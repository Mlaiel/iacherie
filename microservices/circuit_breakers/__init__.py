"""
Circuit Breakers Module for Ainflue Microservices
Implements circuit breaker pattern for resilient microservices communication.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import time
import threading
from typing import Callable, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

__all__ = ['CircuitBreaker', 'CircuitBreakerState', 'CircuitBreakerOpenException']

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """Circuit breaker implementation for microservices"""
    
    def __init__(self, failure_threshold -> None: int = 5, timeout -> None: int = 60, 
                 expected_exception -> None: type = Exception) -> None:
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker moved to HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
                
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.timeout
        
    def _on_success(self) -> None:
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker moved to CLOSED state")
            
    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker moved to OPEN state after {self.failure_count} failures")
            
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self.state
        
    def reset(self) -> None:
        """Manually reset circuit breaker"""
        with self._lock:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED
            self.last_failure_time = None
            logger.info("Circuit breaker manually reset to CLOSED state")
