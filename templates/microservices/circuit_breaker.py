"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Circuit Breaker for IA Chérie Microservices Platform
=================================================

Enterprise-grade circuit breaker pattern providing:
- Failure detection and automatic failover
- Configurable thresholds and timeouts
- Exponential backoff and retry logic
- Health monitoring and recovery
- Metrics collection and monitoring
- Multiple failure detection strategies
- Custom fallback mechanisms
- State persistence and recovery

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Resilience Expert
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Type, Union
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import time

from pydantic import BaseModel, Field
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""
    CLOSED = "closed"           # Normal operation
    OPEN = "open"               # Failing, blocking requests
    HALF_OPEN = "half_open"     # Testing if service recovered


class FailureType(Enum):
    """Failure type enumeration"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    HTTP_ERROR = "http_error"
    VALIDATION_ERROR = "validation_error"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    failure_threshold: int = Field(default=5, description="Number of failures to trigger opening")
    success_threshold: int = Field(default=3, description="Number of successes to close from half-open")
    timeout: int = Field(default=60, description="Timeout before trying half-open in seconds")
    reset_timeout: int = Field(default=300, description="Time to reset failure count in seconds")
    expected_exceptions: List[Type[Exception]] = Field(default_factory=list, description="Expected exception types")
    monitor_window: int = Field(default=60, description="Monitoring window in seconds")
    max_failures_per_window: int = Field(default=10, description="Max failures per monitoring window")
    enable_exponential_backoff: bool = Field(default=True, description="Enable exponential backoff")
    max_backoff_time: int = Field(default=300, description="Maximum backoff time in seconds")
    enable_jitter: bool = Field(default=True, description="Enable jitter in backoff")
    enable_persistence: bool = Field(default=False, description="Enable state persistence")
    persistence_key_prefix: str = Field(default="circuit_breaker", description="Persistence key prefix")


class CircuitBreakerMetrics(BaseModel):
    """Circuit breaker metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    blocked_requests: int = 0
    state_changes: int = 0
    average_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    current_failure_streak: int = 0
    current_success_streak: int = 0


class CircuitBreakerError(Exception):
    """Circuit breaker error"""
    pass


class CircuitBreakerOpenError(CircuitBreakerError):
    """Circuit breaker is open error"""
    pass


class FailureDetector(ABC):
    """Abstract failure detector"""
    
    @abstractmethod
    async def is_failure(self, exception: Optional[Exception], result: Any, execution_time: float) -> bool:
        """Determine if execution result is a failure"""
        pass


class ExceptionBasedFailureDetector(FailureDetector):
    """Exception-based failure detector"""
    
    def __init__(self, expected_exceptions: List[Type[Exception]]):
        self.expected_exceptions = expected_exceptions
    
    async def is_failure(self, exception: Optional[Exception], result: Any, execution_time: float) -> bool:
        """Check if exception indicates failure"""
        if exception is None:
            return False
        
        if not self.expected_exceptions:
            return True
        
        return any(isinstance(exception, exc_type) for exc_type in self.expected_exceptions)


class TimeoutBasedFailureDetector(FailureDetector):
    """Timeout-based failure detector"""
    
    def __init__(self, timeout_threshold: float):
        self.timeout_threshold = timeout_threshold
    
    async def is_failure(self, exception: Optional[Exception], result: Any, execution_time: float) -> bool:
        """Check if execution time exceeds threshold"""
        return execution_time > self.timeout_threshold


class HttpResponseFailureDetector(FailureDetector):
    """HTTP response-based failure detector"""
    
    def __init__(self, failure_status_codes: List[int]):
        self.failure_status_codes = failure_status_codes
    
    async def is_failure(self, exception: Optional[Exception], result: Any, execution_time: float) -> bool:
        """Check if HTTP response indicates failure"""
        if hasattr(result, 'status_code'):
            return result.status_code in self.failure_status_codes
        return False


class CircuitBreaker:
    """
    Enterprise circuit breaker implementation
    
    Provides comprehensive failure handling including:
    - Configurable failure thresholds and timeouts
    - Multiple state management (closed, open, half-open)
    - Exponential backoff with jitter
    - Multiple failure detection strategies
    - Metrics collection and monitoring
    - State persistence for reliability
    - Custom fallback mechanisms
    - Health monitoring and automatic recovery
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        failure_detectors: Optional[List[FailureDetector]] = None,
        fallback_function: Optional[Callable] = None,
        redis_client: Optional[redis.Redis] = None
    ):
        """Initialize circuit breaker"""
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.failure_detectors = failure_detectors or [
            ExceptionBasedFailureDetector(self.config.expected_exceptions)
        ]
        self.fallback_function = fallback_function
        self.redis_client = redis_client
        
        # State management
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self.state_change_time = datetime.utcnow()
        
        # Metrics
        self.metrics = CircuitBreakerMetrics()
        
        # Timing windows
        self.failure_times: List[datetime] = []
        
        # Backoff calculation
        self.consecutive_failures = 0
        
        logger.info(f"Circuit breaker '{name}' initialized with config: {config}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        # Check if circuit breaker allows execution
        if not await self.can_execute():
            self.metrics.blocked_requests += 1
            await self._record_state_persistence()
            
            if self.fallback_function:
                logger.info(f"Circuit breaker '{self.name}' open, using fallback")
                return await self.fallback_function(*args, **kwargs)
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is open")
        
        # Execute function with monitoring
        start_time = time.time()
        exception = None
        result = None
        
        try:
            self.metrics.total_requests += 1
            
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Update metrics
            self._update_response_time(execution_time)
            
            # Check if result indicates failure
            is_failure = await self._detect_failure(exception, result, execution_time)
            
            if is_failure:
                await self.record_failure()
            else:
                await self.record_success()
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            exception = e
            
            # Update metrics
            self._update_response_time(execution_time)
            
            # Check if exception indicates failure
            is_failure = await self._detect_failure(exception, result, execution_time)
            
            if is_failure:
                await self.record_failure()
            else:
                await self.record_success()
            
            raise e
    
    async def can_execute(self) -> bool:
        """Check if circuit breaker allows execution"""
        current_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        elif self.state == CircuitBreakerState.OPEN:
            # Check if timeout period has passed
            if self.last_failure_time:
                time_since_failure = (current_time - self.last_failure_time).total_seconds()
                
                # Calculate backoff time
                backoff_time = self._calculate_backoff_time()
                
                if time_since_failure >= backoff_time:
                    await self._transition_to_half_open()
                    return True
            
            return False
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        
        return False
    
    async def record_failure(self):
        """Record a failure"""
        current_time = datetime.utcnow()
        
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_time = current_time
        self.metrics.failed_requests += 1
        self.metrics.current_failure_streak += 1
        self.metrics.current_success_streak = 0
        self.metrics.last_failure_time = current_time
        
        # Add to failure window
        self.failure_times.append(current_time)
        self._cleanup_old_failures()
        
        # Check state transitions
        await self._check_state_transition_on_failure()
        
        # Persist state if enabled
        await self._record_state_persistence()
        
        logger.warning(f"Circuit breaker '{self.name}' recorded failure (count: {self.failure_count})")
    
    async def record_success(self):
        """Record a success"""
        current_time = datetime.utcnow()
        
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_success_time = current_time
        self.metrics.successful_requests += 1
        self.metrics.current_success_streak += 1
        self.metrics.current_failure_streak = 0
        self.metrics.last_success_time = current_time
        
        # Check state transitions
        await self._check_state_transition_on_success()
        
        # Persist state if enabled
        await self._record_state_persistence()
        
        logger.debug(f"Circuit breaker '{self.name}' recorded success (count: {self.success_count})")
    
    async def _detect_failure(self, exception: Optional[Exception], result: Any, execution_time: float) -> bool:
        """Detect if execution result is a failure"""
        for detector in self.failure_detectors:
            if await detector.is_failure(exception, result, execution_time):
                return True
        return False
    
    async def _check_state_transition_on_failure(self):
        """Check state transition on failure"""
        if self.state == CircuitBreakerState.CLOSED:
            # Check if we should open the circuit
            if self._should_open_circuit():
                await self._transition_to_open()
        
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Any failure in half-open state should open the circuit
            await self._transition_to_open()
    
    async def _check_state_transition_on_success(self):
        """Check state transition on success"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Check if we have enough successes to close
            if self.success_count >= self.config.success_threshold:
                await self._transition_to_closed()
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Check failure threshold
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # Check failure rate in monitoring window
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=self.config.monitor_window)
        
        recent_failures = [
            failure_time for failure_time in self.failure_times
            if failure_time >= window_start
        ]
        
        if len(recent_failures) >= self.config.max_failures_per_window:
            return True
        
        return False
    
    async def _transition_to_open(self):
        """Transition to open state"""
        if self.state != CircuitBreakerState.OPEN:
            logger.warning(f"Circuit breaker '{self.name}' opening")
            self.state = CircuitBreakerState.OPEN
            self.state_change_time = datetime.utcnow()
            self.success_count = 0
            self.metrics.state_changes += 1
    
    async def _transition_to_half_open(self):
        """Transition to half-open state"""
        if self.state != CircuitBreakerState.HALF_OPEN:
            logger.info(f"Circuit breaker '{self.name}' transitioning to half-open")
            self.state = CircuitBreakerState.HALF_OPEN
            self.state_change_time = datetime.utcnow()
            self.success_count = 0
            self.metrics.state_changes += 1
    
    async def _transition_to_closed(self):
        """Transition to closed state"""
        if self.state != CircuitBreakerState.CLOSED:
            logger.info(f"Circuit breaker '{self.name}' closing")
            self.state = CircuitBreakerState.CLOSED
            self.state_change_time = datetime.utcnow()
            self.failure_count = 0
            self.success_count = 0
            self.metrics.state_changes += 1
    
    def _calculate_backoff_time(self) -> float:
        """Calculate backoff time with exponential backoff and jitter"""
        if not self.config.enable_exponential_backoff:
            return self.config.timeout
        
        # Exponential backoff: 2^failures * base_timeout
        backoff_time = min(
            self.config.timeout * (2 ** self.consecutive_failures),
            self.config.max_backoff_time
        )
        
        # Add jitter to prevent thundering herd
        if self.config.enable_jitter:
            import random
            jitter = random.uniform(0.1, 0.5)
            backoff_time *= (1 + jitter)
        
        return backoff_time
    
    def _cleanup_old_failures(self):
        """Cleanup old failure times outside monitoring window"""
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=self.config.monitor_window)
        
        self.failure_times = [
            failure_time for failure_time in self.failure_times
            if failure_time >= window_start
        ]
    
    def _update_response_time(self, execution_time: float):
        """Update response time metrics"""
        current_avg = self.metrics.average_response_time
        total_requests = self.metrics.total_requests
        
        if total_requests > 1:
            self.metrics.average_response_time = (
                (current_avg * (total_requests - 1) + execution_time) / total_requests
            )
        else:
            self.metrics.average_response_time = execution_time
    
    async def _record_state_persistence(self):
        """Record state to persistent storage"""
        if not self.config.enable_persistence or not self.redis_client:
            return
        
        try:
            state_data = {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
                "consecutive_failures": self.consecutive_failures,
                "metrics": self.metrics.dict()
            }
            
            key = f"{self.config.persistence_key_prefix}:{self.name}"
            await self.redis_client.setex(key, 3600, json.dumps(state_data))
            
        except Exception as e:
            logger.error(f"Failed to persist circuit breaker state: {str(e)}")
    
    async def load_state_from_persistence(self):
        """Load state from persistent storage"""
        if not self.config.enable_persistence or not self.redis_client:
            return
        
        try:
            key = f"{self.config.persistence_key_prefix}:{self.name}"
            state_data = await self.redis_client.get(key)
            
            if state_data:
                data = json.loads(state_data)
                
                self.state = CircuitBreakerState(data["state"])
                self.failure_count = data["failure_count"]
                self.success_count = data["success_count"]
                self.consecutive_failures = data["consecutive_failures"]
                
                if data["last_failure_time"]:
                    self.last_failure_time = datetime.fromisoformat(data["last_failure_time"])
                
                if data["last_success_time"]:
                    self.last_success_time = datetime.fromisoformat(data["last_success_time"])
                
                self.metrics = CircuitBreakerMetrics(**data["metrics"])
                
                logger.info(f"Circuit breaker '{self.name}' state loaded from persistence")
        
        except Exception as e:
            logger.error(f"Failed to load circuit breaker state: {str(e)}")
    
    async def reset(self):
        """Reset circuit breaker to initial state"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.consecutive_failures = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.state_change_time = datetime.utcnow()
        self.failure_times.clear()
        self.metrics = CircuitBreakerMetrics()
        
        await self._record_state_persistence()
        logger.info(f"Circuit breaker '{self.name}' reset")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "consecutive_failures": self.consecutive_failures,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "state_change_time": self.state_change_time.isoformat(),
            "metrics": self.metrics.dict(),
            "config": self.config.dict()
        }


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        failure_detectors: Optional[List[FailureDetector]] = None,
        fallback_function: Optional[Callable] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name=name,
                config=config,
                failure_detectors=failure_detectors,
                fallback_function=fallback_function,
                redis_client=self.redis_client
            )
        
        return self.circuit_breakers[name]
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        for cb in self.circuit_breakers.values():
            await cb.reset()
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all circuit breakers"""
        return {
            name: cb.get_state()
            for name, cb in self.circuit_breakers.items()
        }


# Example usage and factory functions

def create_default_circuit_breaker(name: str) -> CircuitBreaker:
    """Create circuit breaker with default configuration"""
    config = CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=3,
        timeout=60,
        enable_exponential_backoff=True,
        enable_jitter=True
    )
    
    return CircuitBreaker(name=name, config=config)


def create_http_circuit_breaker(name: str, timeout_seconds: float = 5.0) -> CircuitBreaker:
    """Create circuit breaker for HTTP services"""
    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=30,
        enable_exponential_backoff=True
    )
    
    failure_detectors = [
        ExceptionBasedFailureDetector([ConnectionError, TimeoutError]),
        TimeoutBasedFailureDetector(timeout_seconds),
        HttpResponseFailureDetector([500, 502, 503, 504])
    ]
    
    return CircuitBreaker(
        name=name,
        config=config,
        failure_detectors=failure_detectors
    )