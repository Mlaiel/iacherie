"""
🔥 CIRCUIT BREAKER - ENTERPRISE FAULT TOLERANCE PATTERNS
Ultra-fast circuit breaker implementation for system resilience
Performance Target: < 1ms circuit breaker operations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - TOUS DROITS RÉSERVÉS
Commercial use forbidden without written authorization
Reverse engineering strictly prohibited
"""

import asyncio
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

import logging


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    max_requests_half_open: int = 3
    
    # Creator Economy specific
    content_type_specific: bool = True
    revenue_protection: bool = True


class CircuitBreaker:
    """
    🔥 ENTERPRISE CIRCUIT BREAKER - CREATOR ECONOMY OPTIMIZED
    Ultra-fast circuit breaker with <1ms operations
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        self.failure_detector = FailureDetector()
        self.recovery_monitor = RecoveryMonitor()
        self.circuit_state = CircuitStateManager()
        
        # Performance metrics
        self.metrics = {
            'requests_total': 0,
            'requests_failed': 0,
            'requests_blocked': 0,
            'state_changes': 0,
            'total_operation_time': 0.0
        }
        
        self._lock = threading.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        start_time = time.perf_counter()
        
        with self._lock:
            self.metrics['requests_total'] += 1
        
        # Check circuit state
        current_state = await self.circuit_state.get_state()
        
        if current_state == CircuitState.OPEN:
            with self._lock:
                self.metrics['requests_blocked'] += 1
            raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        if current_state == CircuitState.HALF_OPEN:
            if not await self.circuit_state.can_make_request():
                with self._lock:
                    self.metrics['requests_blocked'] += 1
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is HALF_OPEN - max requests reached")
        
        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record success
            await self.failure_detector.record_success()
            await self.recovery_monitor.record_success()
            
            # Check if we can close circuit from half-open
            if current_state == CircuitState.HALF_OPEN:
                if await self.recovery_monitor.should_close_circuit():
                    await self.circuit_state.close_circuit()
                    with self._lock:
                        self.metrics['state_changes'] += 1
            
            operation_time = time.perf_counter() - start_time
            with self._lock:
                self.metrics['total_operation_time'] += operation_time
            
            return result
            
        except Exception as e:
            # Record failure
            await self.failure_detector.record_failure()
            
            with self._lock:
                self.metrics['requests_failed'] += 1
            
            # Check if we should open circuit
            if current_state == CircuitState.CLOSED:
                if await self.failure_detector.should_open_circuit():
                    await self.circuit_state.open_circuit()
                    with self._lock:
                        self.metrics['state_changes'] += 1
            
            # If half-open and failure, go back to open
            elif current_state == CircuitState.HALF_OPEN:
                await self.circuit_state.open_circuit()
                with self._lock:
                    self.metrics['state_changes'] += 1
            
            raise
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        with self._lock:
            total_requests = self.metrics['requests_total']
            avg_operation_time = (
                self.metrics['total_operation_time'] / max(1, total_requests)
            ) * 1000  # Convert to ms
            
            return {
                **self.metrics,
                'failure_rate': self.metrics['requests_failed'] / max(1, total_requests),
                'success_rate': 1 - (self.metrics['requests_failed'] / max(1, total_requests)),
                'block_rate': self.metrics['requests_blocked'] / max(1, total_requests),
                'average_operation_time_ms': avg_operation_time,
                'current_state': (await self.circuit_state.get_state()).value
            }


class FailureDetector:
    """Detect service failures for circuit breaker decisions."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.recent_results = deque(maxlen=window_size)
        self.failure_threshold = 0.5  # 50% failure rate
        
    async def record_success(self):
        """Record successful operation."""
        self.recent_results.append(True)
    
    async def record_failure(self):
        """Record failed operation."""
        self.recent_results.append(False)
    
    async def should_open_circuit(self) -> bool:
        """Determine if circuit should be opened."""
        if len(self.recent_results) < 10:  # Need minimum data
            return False
        
        failure_count = sum(1 for result in self.recent_results if not result)
        failure_rate = failure_count / len(self.recent_results)
        
        return failure_rate >= self.failure_threshold


class RecoveryMonitor:
    """Monitor service recovery for circuit breaker decisions."""
    
    def __init__(self, success_threshold: int = 3):
        self.success_threshold = success_threshold
        self.consecutive_successes = 0
    
    async def record_success(self):
        """Record successful operation during recovery."""
        self.consecutive_successes += 1
    
    async def record_failure(self):
        """Record failed operation during recovery."""
        self.consecutive_successes = 0
    
    async def should_close_circuit(self) -> bool:
        """Determine if circuit should be closed."""
        return self.consecutive_successes >= self.success_threshold


class CircuitStateManager:
    """Manage circuit breaker state transitions."""
    
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.state_changed_at = datetime.now()
        self.half_open_requests = 0
        self.max_half_open_requests = 3
        self.open_timeout = timedelta(seconds=60)
        
    async def get_state(self) -> CircuitState:
        """Get current circuit state."""
        # Check if we should transition from OPEN to HALF_OPEN
        if (self.state == CircuitState.OPEN and 
            datetime.now() - self.state_changed_at > self.open_timeout):
            await self.half_open_circuit()
        
        return self.state
    
    async def open_circuit(self):
        """Open the circuit breaker."""
        self.state = CircuitState.OPEN
        self.state_changed_at = datetime.now()
        self.half_open_requests = 0
        logging.warning(f"Circuit breaker opened at {self.state_changed_at}")
    
    async def close_circuit(self):
        """Close the circuit breaker."""
        self.state = CircuitState.CLOSED
        self.state_changed_at = datetime.now()
        self.half_open_requests = 0
        logging.info(f"Circuit breaker closed at {self.state_changed_at}")
    
    async def half_open_circuit(self):
        """Set circuit to half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.state_changed_at = datetime.now()
        self.half_open_requests = 0
        logging.info(f"Circuit breaker half-opened at {self.state_changed_at}")
    
    async def can_make_request(self) -> bool:
        """Check if request can be made in half-open state."""
        if self.state != CircuitState.HALF_OPEN:
            return True
        
        if self.half_open_requests < self.max_half_open_requests:
            self.half_open_requests += 1
            return True
        
        return False


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Enterprise factory function
async def create_enterprise_circuit_breaker(
    name: str,
    config: CircuitBreakerConfig = None
) -> CircuitBreaker:
    """Factory function for enterprise circuit breaker."""
    return CircuitBreaker(name, config)