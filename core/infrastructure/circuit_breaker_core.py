"""Ainflue Core Infrastructure - Circuit Breaker Core
==================================================

Enterprise-grade circuit breaker implementation providing fault tolerance,
automatic failure detection, service protection, and graceful degradation
for distributed systems in the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import threading

# Setup logger
logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Circuit is open, failing fast
    HALF_OPEN = "half_open" # Testing if service is recovered

class FailureType(str, Enum):
    """Types of failures"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    HTTP_ERROR = "http_error"
    CUSTOM = "custom"

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Number of failures before opening
    recovery_timeout: float = 60.0      # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 10.0               # Request timeout seconds
    failure_rate_threshold: float = 0.5 # Failure rate threshold (0.0-1.0)
    min_request_threshold: int = 10     # Minimum requests before checking failure rate
    reset_timeout: float = 30.0         # Time to reset stats in closed state
    max_retries: int = 3                # Maximum retry attempts
    backoff_multiplier: float = 2.0     # Exponential backoff multiplier
    enable_metrics: bool = True         # Enable metrics collection

@dataclass
class CircuitMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    rejected_requests: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    current_failure_rate: float = 0.0
    avg_response_time: float = 0.0
    total_response_time: float = 0.0
    state_changes: int = 0
    last_state_change: Optional[datetime] = None

@dataclass
class CallResult(Generic[T]):
    """Result of a circuit breaker call"""
    success: bool
    result: Optional[T] = None
    exception: Optional[Exception] = None
    execution_time: float = 0.0
    state: CircuitState = CircuitState.CLOSED
    rejected: bool = False
    failure_type: Optional[FailureType] = None

class CircuitBreakerException(Exception):
    """Circuit breaker specific exception"""
    def __init__(self, message -> None: str, state -> None: CircuitState) -> None:
        super().__init__(message)
        self.state = state

class CircuitOpenException(CircuitBreakerException):
    """Exception when circuit is open"""
    def __init__(self) -> None:
        super().__init__("Circuit breaker is OPEN", CircuitState.OPEN)

class FallbackHandler(ABC, Generic[T]):
    """Abstract fallback handler"""
    
    @abstractmethod
    async def handle_fallback(self, exception: Exception, *args, **kwargs) -> T:
        """Handle fallback when circuit is open or call fails"""
        pass

class DefaultFallbackHandler(FallbackHandler[T]):
    """Default fallback handler that raises the original exception"""
    
    async def handle_fallback(self, exception: Exception, *args, **kwargs) -> T:
        raise exception

class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, name -> None: str, config -> None: Optional[CircuitBreakerConfig] = None) -> None:
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitMetrics()
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.state_changed_at = time.time()
        self.lock = threading.Lock()
        self.fallback_handler: Optional[FallbackHandler] = None
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    def set_fallback_handler(self, handler -> None: FallbackHandler) -> None:
        """Set fallback handler"""
        self.fallback_handler = handler
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> CallResult[T]:
        """Execute function with circuit breaker protection"""
        start_time = time.time()
        
        with self.lock:
            self.metrics.total_requests += 1
            
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                self.metrics.rejected_requests += 1
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    # Circuit is open, reject call
                    result = CallResult[T](
                        success=False,
                        exception=CircuitOpenException(),
                        state=self.state,
                        rejected=True
                    )
                    await self._handle_rejected_call(result, *args, **kwargs)
                    return result
            
            # Check if we should open the circuit
            if self.state == CircuitState.CLOSED and self._should_open_circuit():
                self._transition_to_open()
                result = CallResult[T](
                    success=False,
                    exception=CircuitOpenException(),
                    state=self.state,
                    rejected=True
                )
                await self._handle_rejected_call(result, *args, **kwargs)
                return result
        
        # Execute the function
        try:
            if asyncio.iscoroutinefunction(func):
                result_value = await asyncio.wait_for(
                    func(*args, **kwargs), 
                    timeout=self.config.timeout
                )
            else:
                result_value = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Record success
            with self.lock:
                self._record_success(execution_time)
                
                # If half-open and enough successes, close circuit
                if (self.state == CircuitState.HALF_OPEN and 
                    self.metrics.consecutive_successes >= self.config.success_threshold):
                    self._transition_to_closed()
            
            return CallResult[T](
                success=True,
                result=result_value,
                execution_time=execution_time,
                state=self.state
            )
            
        except asyncio.TimeoutError as e:
            execution_time = time.time() - start_time
            with self.lock:
                self._record_failure(FailureType.TIMEOUT)
            
            result = CallResult[T](
                success=False,
                exception=e,
                execution_time=execution_time,
                state=self.state,
                failure_type=FailureType.TIMEOUT
            )
            
            return await self._handle_failed_call(result, e, *args, **kwargs)
            
        except Exception as e:
            execution_time = time.time() - start_time
            failure_type = self._classify_exception(e)
            
            with self.lock:
                self._record_failure(failure_type)
            
            result = CallResult[T](
                success=False,
                exception=e,
                execution_time=execution_time,
                state=self.state,
                failure_type=failure_type
            )
            
            return await self._handle_failed_call(result, e, *args, **kwargs)
    
    async def _handle_failed_call(self, result: CallResult[T], exception: Exception, 
                                 *args, **kwargs) -> CallResult[T]:
        """Handle failed call with fallback"""
        if self.fallback_handler:
            try:
                fallback_result = await self.fallback_handler.handle_fallback(exception, *args, **kwargs)
                result.result = fallback_result
                result.success = True
            except Exception as fallback_exception:
                result.exception = fallback_exception
        
        return result
    
    async def _handle_rejected_call(self, result: CallResult[T], *args, **kwargs) -> CallResult[T]:
        """Handle rejected call with fallback"""
        if self.fallback_handler:
            try:
                fallback_result = await self.fallback_handler.handle_fallback(
                    result.exception, *args, **kwargs
                )
                result.result = fallback_result
                result.success = True
                result.rejected = False
            except Exception as fallback_exception:
                result.exception = fallback_exception
        
        return result
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened"""
        # Check consecutive failures
        if self.metrics.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Check failure rate
        if (self.metrics.total_requests >= self.config.min_request_threshold and
            self.metrics.current_failure_rate >= self.config.failure_rate_threshold):
            return True
        
        return False
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset circuit"""
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _transition_to_open(self) -> None:
        """Transition circuit to open state"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.state_changed_at = time.time()
        self.metrics.state_changes += 1
        self.metrics.last_state_change = datetime.utcnow()
        
        logger.warning(f"Circuit breaker '{self.name}' opened - {old_state} -> {self.state}")
    
    def _transition_to_half_open(self) -> None:
        """Transition circuit to half-open state"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.state_changed_at = time.time()
        self.metrics.consecutive_successes = 0
        self.metrics.state_changes += 1
        self.metrics.last_state_change = datetime.utcnow()
        
        logger.info(f"Circuit breaker '{self.name}' half-opened - {old_state} -> {self.state}")
    
    def _transition_to_closed(self) -> None:
        """Transition circuit to closed state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.state_changed_at = time.time()
        self.metrics.consecutive_failures = 0
        self.metrics.state_changes += 1
        self.metrics.last_state_change = datetime.utcnow()
        
        logger.info(f"Circuit breaker '{self.name}' closed - {old_state} -> {self.state}")
    
    def _record_success(self, execution_time -> None: float) -> None:
        """Record successful execution"""
        self.metrics.successful_requests += 1
        self.metrics.consecutive_successes += 1
        self.metrics.consecutive_failures = 0
        self.metrics.last_success_time = datetime.utcnow()
        self.last_success_time = time.time()
        
        # Update response time metrics
        self.metrics.total_response_time += execution_time
        self.metrics.avg_response_time = (
            self.metrics.total_response_time / self.metrics.successful_requests
        )
        
        # Update failure rate
        self._update_failure_rate()
    
    def _record_failure(self, failure_type -> None: FailureType) -> None:
        """Record failed execution"""
        self.metrics.failed_requests += 1
        self.metrics.consecutive_failures += 1
        self.metrics.consecutive_successes = 0
        self.metrics.last_failure_time = datetime.utcnow()
        self.last_failure_time = time.time()
        
        if failure_type == FailureType.TIMEOUT:
            self.metrics.timeout_requests += 1
        
        # Update failure rate
        self._update_failure_rate()
    
    def _update_failure_rate(self) -> None:
        """Update current failure rate"""
        if self.metrics.total_requests > 0:
            self.metrics.current_failure_rate = (
                self.metrics.failed_requests / self.metrics.total_requests
            )
    
    def _classify_exception(self, exception: Exception) -> FailureType:
        """Classify exception type"""
        if isinstance(exception, asyncio.TimeoutError):
            return FailureType.TIMEOUT
        elif hasattr(exception, 'status_code'):
            return FailureType.HTTP_ERROR
        else:
            return FailureType.EXCEPTION
    
    def reset(self) -> None:
        """Reset circuit breaker state"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.metrics = CircuitMetrics()
            self.last_failure_time = 0.0
            self.last_success_time = 0.0
            self.state_changed_at = time.time()
        
        logger.info(f"Circuit breaker '{self.name}' reset")
    
    def force_open(self) -> None:
        """Force circuit to open state"""
        with self.lock:
            self._transition_to_open()
    
    def force_close(self) -> None:
        """Force circuit to closed state"""
        with self.lock:
            self._transition_to_closed()
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state
    
    def get_metrics(self) -> CircuitMetrics:
        """Get circuit metrics"""
        return self.metrics
    
    def is_call_permitted(self) -> bool:
        """Check if call is permitted"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                return self._should_attempt_reset()
            return True

class CircuitBreakerCore:
    """Core circuit breaker management system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.level = level
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.global_config = CircuitBreakerConfig()
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        self.metrics = {
            'total_circuits': 0,
            'open_circuits': 0,
            'half_open_circuits': 0,
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rejected_calls': 0
        }
        
        logger.info(f"Circuit Breaker Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize circuit breaker system"""
        try:
            logger.info("Circuit Breaker Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Circuit Breaker Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start circuit breaker system"""
        try:
            self.is_running = True
            
            # Start monitoring task
            self.monitoring_task = asyncio.create_task(self._monitor_circuits())
            
            logger.info("Circuit Breaker Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Circuit Breaker Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop circuit breaker system"""
        try:
            self.is_running = False
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Circuit Breaker Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Circuit Breaker Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if monitoring is running
            if self.is_running and (not self.monitoring_task or self.monitoring_task.done()):
                logger.warning("Circuit breaker monitoring is not running")
                return False
            
            # Check for too many open circuits
            open_circuits = len([cb for cb in self.circuit_breakers.values() 
                               if cb.get_state() == CircuitState.OPEN])
            if open_circuits > len(self.circuit_breakers) * 0.5:  # More than 50% open
                logger.warning(f"Too many open circuits: {open_circuits}/{len(self.circuit_breakers)}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def _monitor_circuits(self) -> None:
        """Monitor circuit breaker states"""
        while self.is_running:
            try:
                await self._update_global_metrics()
                await asyncio.sleep(10)  # Monitor every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Circuit monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _update_global_metrics(self) -> None:
        """Update global metrics"""
        total_calls = 0
        successful_calls = 0
        failed_calls = 0
        rejected_calls = 0
        open_circuits = 0
        half_open_circuits = 0
        
        for circuit in self.circuit_breakers.values():
            metrics = circuit.get_metrics()
            total_calls += metrics.total_requests
            successful_calls += metrics.successful_requests
            failed_calls += metrics.failed_requests
            rejected_calls += metrics.rejected_requests
            
            state = circuit.get_state()
            if state == CircuitState.OPEN:
                open_circuits += 1
            elif state == CircuitState.HALF_OPEN:
                half_open_circuits += 1
        
        self.metrics.update({
            'total_circuits': len(self.circuit_breakers),
            'open_circuits': open_circuits,
            'half_open_circuits': half_open_circuits,
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'rejected_calls': rejected_calls
        })
    
    def create_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Create new circuit breaker"""
        if name in self.circuit_breakers:
            logger.warning(f"Circuit breaker '{name}' already exists")
            return self.circuit_breakers[name]
        
        circuit_config = config or self.global_config
        circuit = CircuitBreaker(name, circuit_config)
        self.circuit_breakers[name] = circuit
        
        logger.info(f"Created circuit breaker: {name}")
        return circuit
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name"""
        return self.circuit_breakers.get(name)
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker"""
        if name in self.circuit_breakers:
            del self.circuit_breakers[name]
            logger.info(f"Removed circuit breaker: {name}")
            return True
        return False
    
    async def call_with_circuit_breaker(self, circuit_name: str, func: Callable[..., T], 
                                       *args, **kwargs) -> CallResult[T]:
        """Execute function with circuit breaker protection"""
        circuit = self.get_circuit_breaker(circuit_name)
        if not circuit:
            # Create circuit breaker on demand
            circuit = self.create_circuit_breaker(circuit_name)
        
        return await circuit.call(func, *args, **kwargs)
    
    def reset_circuit_breaker(self, name: str) -> bool:
        """Reset specific circuit breaker"""
        circuit = self.get_circuit_breaker(name)
        if circuit:
            circuit.reset()
            return True
        return False
    
    def reset_all_circuit_breakers(self) -> None:
        """Reset all circuit breakers"""
        for circuit in self.circuit_breakers.values():
            circuit.reset()
        logger.info("Reset all circuit breakers")
    
    def get_circuit_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get circuit breaker status"""
        circuit = self.get_circuit_breaker(name)
        if not circuit:
            return None
        
        metrics = circuit.get_metrics()
        return {
            'name': name,
            'state': circuit.get_state().value,
            'is_call_permitted': circuit.is_call_permitted(),
            'metrics': {
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'rejected_requests': metrics.rejected_requests,
                'consecutive_failures': metrics.consecutive_failures,
                'consecutive_successes': metrics.consecutive_successes,
                'current_failure_rate': metrics.current_failure_rate,
                'avg_response_time': metrics.avg_response_time,
                'state_changes': metrics.state_changes,
                'last_failure_time': metrics.last_failure_time.isoformat() if metrics.last_failure_time else None,
                'last_success_time': metrics.last_success_time.isoformat() if metrics.last_success_time else None
            },
            'config': {
                'failure_threshold': circuit.config.failure_threshold,
                'recovery_timeout': circuit.config.recovery_timeout,
                'success_threshold': circuit.config.success_threshold,
                'timeout': circuit.config.timeout
            }
        }
    
    def get_all_circuit_status(self) -> List[Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return [
            self.get_circuit_status(name) 
            for name in self.circuit_breakers.keys()
        ]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        success_rate = (
            self.metrics['successful_calls'] / self.metrics['total_calls']
            if self.metrics['total_calls'] > 0 else 1.0
        )
        
        failure_rate = (
            self.metrics['failed_calls'] / self.metrics['total_calls']
            if self.metrics['total_calls'] > 0 else 0.0
        )
        
        rejection_rate = (
            self.metrics['rejected_calls'] / self.metrics['total_calls']
            if self.metrics['total_calls'] > 0 else 0.0
        )
        
        return {
            'level': self.level,
            'total_circuits': self.metrics['total_circuits'],
            'open_circuits': self.metrics['open_circuits'],
            'half_open_circuits': self.metrics['half_open_circuits'],
            'closed_circuits': self.metrics['total_circuits'] - self.metrics['open_circuits'] - self.metrics['half_open_circuits'],
            'total_calls': self.metrics['total_calls'],
            'successful_calls': self.metrics['successful_calls'],
            'failed_calls': self.metrics['failed_calls'],
            'rejected_calls': self.metrics['rejected_calls'],
            'success_rate': success_rate,
            'failure_rate': failure_rate,
            'rejection_rate': rejection_rate,
            'circuit_health': (
                (self.metrics['total_circuits'] - self.metrics['open_circuits']) / self.metrics['total_circuits']
                if self.metrics['total_circuits'] > 0 else 1.0
            ),
            'is_running': self.is_running
        }

# Global instance
circuit_breaker_core = CircuitBreakerCore()

# Convenience functions
def create_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Create circuit breaker"""
    return circuit_breaker_core.create_circuit_breaker(name, config)

async def call_with_circuit_breaker(circuit_name: str, func: Callable[..., T], *args, **kwargs) -> CallResult[T]:
    """Call function with circuit breaker protection"""
    return await circuit_breaker_core.call_with_circuit_breaker(circuit_name, func, *args, **kwargs)

def get_circuit_status(name: str) -> Optional[Dict[str, Any]]:
    """Get circuit breaker status"""
    return circuit_breaker_core.get_circuit_status(name)

def reset_circuit_breaker(name: str) -> bool:
    """Reset circuit breaker"""
    return circuit_breaker_core.reset_circuit_breaker(name)

# Module exports
__all__ = [
    "CircuitBreakerCore", "CircuitBreaker", "CircuitBreakerConfig", "CircuitMetrics",
    "CallResult", "FallbackHandler", "DefaultFallbackHandler", "CircuitState",
    "FailureType", "CircuitBreakerException", "CircuitOpenException",
    "circuit_breaker_core", "create_circuit_breaker", "call_with_circuit_breaker",
    "get_circuit_status", "reset_circuit_breaker"
]

logger.info("Circuit Breaker Core module loaded")