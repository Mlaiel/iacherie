"""
Circuit Breaker - Performance Utilities Level 3
===============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade circuit breaker pattern consolidating circuit_breaker.py + error_handler.py
Enhanced with intelligent failure detection and recovery mechanisms.

Performance: < 1ms per circuit breaker operation
Standards: Fail-fast patterns, intelligent recovery, enterprise resilience
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerResult:
    """Result container for circuit breaker operations."""
    success: bool
    result: Optional[Any] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

class CircuitBreaker:
    """Enterprise circuit breaker with intelligent failure detection."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout_seconds: int = 60,
                 expected_exception: type = Exception):
        """Initialize circuit breaker."""
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = CircuitState.CLOSED
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            time_since_failure = datetime.now(timezone.utc) - self._last_failure_time
            return time_since_failure.total_seconds() >= self.timeout_seconds
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> CircuitBreakerResult:
        """Execute function with circuit breaker protection."""
        start_time = time.perf_counter()
        
        try:
            # Check if circuit is open
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    exec_time = (time.perf_counter() - start_time) * 1000
                    return CircuitBreakerResult(
                        success=False,
                        circuit_state=self._state,
                        errors=["Circuit breaker is OPEN"],
                        execution_time_ms=exec_time
                    )
            
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset failure count and close circuit
            self._failure_count = 0
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                logger.info("Circuit breaker reset to CLOSED")
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return CircuitBreakerResult(
                success=True,
                result=result,
                circuit_state=self._state,
                execution_time_ms=exec_time
            )
            
        except self.expected_exception as e:
            # Handle expected failures
            self._failure_count += 1
            self._last_failure_time = datetime.now(timezone.utc)
            
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return CircuitBreakerResult(
                success=False,
                circuit_state=self._state,
                errors=[str(e)],
                execution_time_ms=exec_time
            )
        
        except Exception as e:
            # Handle unexpected exceptions
            exec_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Unexpected error in circuit breaker: {e}")
            
            return CircuitBreakerResult(
                success=False,
                circuit_state=self._state,
                errors=[f"Unexpected error: {str(e)}"],
                execution_time_ms=exec_time
            )
    
    def reset(self) -> None:
        """Manually reset circuit breaker."""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset")

class CircuitBreakerFactory:
    """Factory for creating circuit breaker instances."""
    
    @staticmethod
    def create_breaker(
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: type = Exception
    ) -> CircuitBreaker:
        return CircuitBreaker(failure_threshold, timeout_seconds, expected_exception)