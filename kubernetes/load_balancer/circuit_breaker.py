"""Circuit Breaker for Load Balancer

Advanced circuit breaker implementation for the IA Influencer Agent platform,
providing service resilience, failure detection, and automatic recovery
capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""
import time
import asyncio
import logging
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Circuit is open, blocking requests
    HALF_OPEN = "half_open" # Testing if service is recovered


class FailureType(Enum):
    """Types of failures that can trigger circuit breaker"""    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    SERVICE_ERROR = "service_error"
    CUSTOM_ERROR = "custom_error"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""    name: str
    failure_threshold: int = 5          # Number of failures to open circuit
    recovery_timeout: int = 60          # Seconds to wait before half-open
    success_threshold: int = 3          # Successful requests to close circuit
    timeout_seconds: float = 30.0       # Request timeout
    window_size: int = 100              # Rolling window size for failure rate
    minimum_requests: int = 10          # Minimum requests before opening
    failure_rate_threshold: float = 0.5 # Failure rate to open circuit (0.0-1.0)
    slow_call_duration: float = 5.0     # Slow call threshold in seconds
    slow_call_rate_threshold: float = 0.5 # Slow call rate to open circuit
    enabled: bool = True


@dataclass
class CircuitBreakerRequest:
    """Circuit breaker request tracking"""    timestamp: datetime
    duration: float
    success: bool
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    slow_requests: int = 0
    blocked_requests: int = 0
    failure_rate: float = 0.0
    slow_call_rate: float = 0.0
    average_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    state_change_time: datetime = field(default_factory=datetime.now)


class CircuitBreakerInstance:
    """Individual circuit breaker instance"""    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state_change_time = datetime.now()
        self.request_history = deque(maxlen=config.window_size)
        self.metrics = CircuitBreakerMetrics()
        self.lock = threading.RLock()
        
        # Callbacks for state changes
        self.state_change_callbacks: List[Callable] = []
    
    def add_state_change_callback(self, callback: Callable[[str, CircuitState, CircuitState], None]) -> None:
        """Add callback for state changes"""        self.state_change_callbacks.append(callback)
    
    def _notify_state_change(self, old_state: CircuitState, new_state: CircuitState) -> None:
        """Notify all callbacks of state change"""        for callback in self.state_change_callbacks:
            try:
                callback(self.config.name, old_state, new_state)
            except Exception as e:
                logger.error(f"State change callback failed: {e}")
    
    def _change_state(self, new_state: CircuitState) -> None:
        """Change circuit breaker state"""        old_state = self.state
        self.state = new_state
        self.state_change_time = datetime.now()
        
        if old_state != new_state:
            logger.info(f"Circuit breaker {self.config.name} state changed: {old_state.value} -> {new_state.value}")
            self._notify_state_change(old_state, new_state)
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened based on failure rate"""        if len(self.request_history) < self.config.minimum_requests:
            return False
        
        # Calculate failure rate
        recent_requests = list(self.request_history)
        failed_requests = sum(1 for req in recent_requests if not req.success)
        failure_rate = failed_requests / len(recent_requests)
        
        # Calculate slow call rate
        slow_requests = sum(1 for req in recent_requests if req.duration >= self.config.slow_call_duration)
        slow_call_rate = slow_requests / len(recent_requests)
        
        # Update metrics
        self.metrics.failure_rate = failure_rate
        self.metrics.slow_call_rate = slow_call_rate
        
        # Check thresholds
        failure_threshold_exceeded = failure_rate >= self.config.failure_rate_threshold
        slow_call_threshold_exceeded = slow_call_rate >= self.config.slow_call_rate_threshold
        
        return failure_threshold_exceeded or slow_call_threshold_exceeded
    
    def _can_attempt_reset(self) -> bool:
        """Check if circuit can attempt reset to half-open"""        if self.state != CircuitState.OPEN:
            return False
        
        if not self.last_failure_time:
            return True
        
        time_since_last_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_last_failure >= self.config.recovery_timeout
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function call through circuit breaker"""        with self.lock:
            # Check if request should be blocked
            if self.state == CircuitState.OPEN:
                if self._can_attempt_reset():
                    self._change_state(CircuitState.HALF_OPEN)
                    self.success_count = 0
                else:
                    self.metrics.blocked_requests += 1
                    raise CircuitBreakerOpenException(f"Circuit breaker {self.config.name} is open")
            
            # Track request start time
            start_time = time.time()
            request = CircuitBreakerRequest(
                timestamp=datetime.now(),
                duration=0.0,
                success=False
            )
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                request.duration = duration
                request.success = True
                
                # Handle successful request
                self._handle_success(request)
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time
                request.duration = duration
                request.success = False
                
                # Determine failure type
                if "timeout" in str(e).lower():
                    request.failure_type = FailureType.TIMEOUT
                elif "connection" in str(e).lower():
                    request.failure_type = FailureType.CONNECTION_ERROR
                elif hasattr(e, 'status_code'):
                    request.failure_type = FailureType.HTTP_ERROR
                else:
                    request.failure_type = FailureType.SERVICE_ERROR
                
                request.error_message = str(e)
                
                # Handle failed request
                self._handle_failure(request)
                
                # Re-raise the exception
                raise
    
    async def async_call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function call through circuit breaker"""        with self.lock:
            # Check if request should be blocked
            if self.state == CircuitState.OPEN:
                if self._can_attempt_reset():
                    self._change_state(CircuitState.HALF_OPEN)
                    self.success_count = 0
                else:
                    self.metrics.blocked_requests += 1
                    raise CircuitBreakerOpenException(f"Circuit breaker {self.config.name} is open")
            
            # Track request start time
            start_time = time.time()
            request = CircuitBreakerRequest(
                timestamp=datetime.now(),
                duration=0.0,
                success=False
            )
            
            try:
                # Execute the async function with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout_seconds
                )
                
                # Calculate duration
                duration = time.time() - start_time
                request.duration = duration
                request.success = True
                
                # Handle successful request
                self._handle_success(request)
                
                return result
                
            except asyncio.TimeoutError:
                # Handle timeout
                duration = time.time() - start_time
                request.duration = duration
                request.success = False
                request.failure_type = FailureType.TIMEOUT
                request.error_message = f"Request timed out after {self.config.timeout_seconds}s"
                
                self._handle_failure(request)
                raise
                
            except Exception as e:
                # Calculate duration
                duration = time.time() - start_time
                request.duration = duration
                request.success = False
                
                # Determine failure type
                if "connection" in str(e).lower():
                    request.failure_type = FailureType.CONNECTION_ERROR
                elif hasattr(e, 'status_code'):
                    request.failure_type = FailureType.HTTP_ERROR
                else:
                    request.failure_type = FailureType.SERVICE_ERROR
                
                request.error_message = str(e)
                
                # Handle failed request
                self._handle_failure(request)
                
                # Re-raise the exception
                raise
    
    def _handle_success(self, request: CircuitBreakerRequest) -> None:
        """Handle successful request"""        # Add to history
        self.request_history.append(request)
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        
        # Update average response time
        if self.metrics.total_requests > 0:
            total_duration = sum(req.duration for req in self.request_history)
            self.metrics.average_response_time = total_duration / len(self.request_history)
        
        # Handle state transitions
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._change_state(CircuitState.CLOSED)
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on successful request
            self.failure_count = 0
    
    def _handle_failure(self, request: CircuitBreakerRequest) -> None:
        """Handle failed request"""        # Add to history
        self.request_history.append(request)
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.metrics.last_failure_time = request.timestamp
        
        if request.duration >= self.config.slow_call_duration:
            self.metrics.slow_requests += 1
        
        # Update average response time
        if self.metrics.total_requests > 0:
            total_duration = sum(req.duration for req in self.request_history)
            self.metrics.average_response_time = total_duration / len(self.request_history)
        
        # Handle state transitions
        self.failure_count += 1
        self.last_failure_time = request.timestamp
        
        if self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens the circuit
            self._change_state(CircuitState.OPEN)
        elif self.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            if self._should_open_circuit():
                self._change_state(CircuitState.OPEN)
    
    def force_open(self) -> None:
        """Force circuit breaker to open state"""        with self.lock:
            self._change_state(CircuitState.OPEN)
            self.last_failure_time = datetime.now()
    
    def force_close(self) -> None:
        """Force circuit breaker to closed state"""        with self.lock:
            self._change_state(CircuitState.CLOSED)
            self.failure_count = 0
            self.success_count = 0
    
    def reset(self) -> None:
        """Reset circuit breaker to initial state"""        with self.lock:
            self._change_state(CircuitState.CLOSED)
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.request_history.clear()
            self.metrics = CircuitBreakerMetrics()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""        with self.lock:
            return {
                "name": self.config.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "state_change_time": self.state_change_time.isoformat(),
                "can_attempt_reset": self._can_attempt_reset(),
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout,
                    "success_threshold": self.config.success_threshold,
                    "timeout_seconds": self.config.timeout_seconds,
                    "failure_rate_threshold": self.config.failure_rate_threshold,
                    "slow_call_rate_threshold": self.config.slow_call_rate_threshold,
                    "enabled": self.config.enabled
                },
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "slow_requests": self.metrics.slow_requests,
                    "blocked_requests": self.metrics.blocked_requests,
                    "failure_rate": round(self.metrics.failure_rate, 3),
                    "slow_call_rate": round(self.metrics.slow_call_rate, 3),
                    "average_response_time": round(self.metrics.average_response_time, 3),
                    "last_failure_time": self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None
                }
            }


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""    pass


class CircuitBreaker:
    """Enterprise Circuit Breaker Manager for Load Balancer"""    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreakerInstance] = {}
        self.global_callbacks: List[Callable] = []
        self.lock = threading.RLock()
        self.stats = defaultdict(int)
    
    def create_circuit_breaker(self, config: CircuitBreakerConfig) -> bool:
        """Create a new circuit breaker"""        try:
            if not config.enabled:
                logger.info(f"Circuit breaker {config.name} is disabled")
                return True
            
            with self.lock:
                circuit_breaker = CircuitBreakerInstance(config)
                
                # Add global callbacks
                for callback in self.global_callbacks:
                    circuit_breaker.add_state_change_callback(callback)
                
                self.circuit_breakers[config.name] = circuit_breaker
            
            logger.info(f"Circuit breaker {config.name} created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create circuit breaker {config.name}: {e}")
            return False
    
    def remove_circuit_breaker(self, name: str) -> bool:
        """Remove circuit breaker"""        try:
            with self.lock:
                if name in self.circuit_breakers:
                    del self.circuit_breakers[name]
                    logger.info(f"Circuit breaker {name} removed")
                    return True
                else:
                    logger.warning(f"Circuit breaker {name} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to remove circuit breaker {name}: {e}")
            return False
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreakerInstance]:
        """Get circuit breaker instance"""        with self.lock:
            return self.circuit_breakers.get(name)
    
    def add_global_state_change_callback(self, callback: Callable[[str, CircuitState, CircuitState], None]) -> None:
        """Add global state change callback"""        self.global_callbacks.append(callback)
        
        # Add to existing circuit breakers
        with self.lock:
            for cb in self.circuit_breakers.values():
                cb.add_state_change_callback(callback)
    
    def call_with_circuit_breaker(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function call with circuit breaker protection"""        circuit_breaker = self.get_circuit_breaker(name)
        if not circuit_breaker:
            raise ValueError(f"Circuit breaker {name} not found")
        
        return circuit_breaker.call(func, *args, **kwargs)
    
    async def async_call_with_circuit_breaker(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute async function call with circuit breaker protection"""        circuit_breaker = self.get_circuit_breaker(name)
        if not circuit_breaker:
            raise ValueError(f"Circuit breaker {name} not found")
        
        return await circuit_breaker.async_call(func, *args, **kwargs)
    
    def force_open_all(self) -> None:
        """Force all circuit breakers to open state"""        with self.lock:
            for cb in self.circuit_breakers.values():
                cb.force_open()
    
    def force_close_all(self) -> None:
        """Force all circuit breakers to closed state"""        with self.lock:
            for cb in self.circuit_breakers.values():
                cb.force_close()
    
    def reset_all(self) -> None:
        """Reset all circuit breakers"""        with self.lock:
            for cb in self.circuit_breakers.values():
                cb.reset()
    
    def configure_platform_circuit_breakers(self) -> bool:
        """Configure circuit breakers for platform services"""        try:
            circuit_breaker_configs = [
                # Fingerprinting service circuit breakers
                CircuitBreakerConfig(
                    name="fingerprinting_service",
                    failure_threshold=5,
                    recovery_timeout=60,
                    success_threshold=3,
                    timeout_seconds=30.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.5,
                    slow_call_duration=15.0,  # Fingerprinting can be slow
                    slow_call_rate_threshold=0.3
                ),
                CircuitBreakerConfig(
                    name="audio_fingerprinting",
                    failure_threshold=3,
                    recovery_timeout=45,
                    success_threshold=2,
                    timeout_seconds=60.0,  # Audio processing takes longer
                    window_size=50,
                    minimum_requests=5,
                    failure_rate_threshold=0.4,
                    slow_call_duration=30.0,
                    slow_call_rate_threshold=0.4
                ),
                CircuitBreakerConfig(
                    name="video_fingerprinting",
                    failure_threshold=3,
                    recovery_timeout=90,
                    success_threshold=2,
                    timeout_seconds=120.0,  # Video processing takes much longer
                    window_size=30,
                    minimum_requests=3,
                    failure_rate_threshold=0.4,
                    slow_call_duration=60.0,
                    slow_call_rate_threshold=0.5
                ),
                
                # Protection service circuit breakers
                CircuitBreakerConfig(
                    name="protection_service",
                    failure_threshold=5,
                    recovery_timeout=30,
                    success_threshold=3,
                    timeout_seconds=10.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.3,
                    slow_call_duration=5.0,
                    slow_call_rate_threshold=0.2
                ),
                CircuitBreakerConfig(
                    name="content_monitoring",
                    failure_threshold=8,
                    recovery_timeout=60,
                    success_threshold=3,
                    timeout_seconds=15.0,
                    window_size=200,
                    minimum_requests=20,
                    failure_rate_threshold=0.4,
                    slow_call_duration=8.0,
                    slow_call_rate_threshold=0.3
                ),
                
                # Monetization service circuit breakers
                CircuitBreakerConfig(
                    name="monetization_service",
                    failure_threshold=3,
                    recovery_timeout=120,
                    success_threshold=5,
                    timeout_seconds=20.0,
                    window_size=50,
                    minimum_requests=5,
                    failure_rate_threshold=0.2,  # Strict for payment processing
                    slow_call_duration=10.0,
                    slow_call_rate_threshold=0.2
                ),
                CircuitBreakerConfig(
                    name="payment_processing",
                    failure_threshold=2,
                    recovery_timeout=300,  # 5 minutes for payment recovery
                    success_threshold=5,
                    timeout_seconds=30.0,
                    window_size=20,
                    minimum_requests=2,
                    failure_rate_threshold=0.1,  # Very strict for payments
                    slow_call_duration=15.0,
                    slow_call_rate_threshold=0.2
                ),
                
                # AI Agent service circuit breakers
                CircuitBreakerConfig(
                    name="ai_agent_service",
                    failure_threshold=5,
                    recovery_timeout=60,
                    success_threshold=3,
                    timeout_seconds=30.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.4,
                    slow_call_duration=20.0,
                    slow_call_rate_threshold=0.3
                ),
                CircuitBreakerConfig(
                    name="ai_music_generation",
                    failure_threshold=3,
                    recovery_timeout=120,
                    success_threshold=2,
                    timeout_seconds=180.0,  # AI generation can be very slow
                    window_size=30,
                    minimum_requests=3,
                    failure_rate_threshold=0.3,
                    slow_call_duration=90.0,
                    slow_call_rate_threshold=0.5
                ),
                
                # Crawler service circuit breakers
                CircuitBreakerConfig(
                    name="crawler_service",
                    failure_threshold=8,
                    recovery_timeout=45,
                    success_threshold=3,
                    timeout_seconds=30.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.6,  # Crawlers can be unreliable
                    slow_call_duration=20.0,
                    slow_call_rate_threshold=0.4
                ),
                CircuitBreakerConfig(
                    name="web_crawling",
                    failure_threshold=10,
                    recovery_timeout=30,
                    success_threshold=2,
                    timeout_seconds=60.0,
                    window_size=200,
                    minimum_requests=20,
                    failure_rate_threshold=0.7,  # Web crawling is often unreliable
                    slow_call_duration=30.0,
                    slow_call_rate_threshold=0.5
                ),
                
                # Database circuit breakers
                CircuitBreakerConfig(
                    name="primary_database",
                    failure_threshold=3,
                    recovery_timeout=60,
                    success_threshold=5,
                    timeout_seconds=10.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.2,
                    slow_call_duration=3.0,
                    slow_call_rate_threshold=0.1
                ),
                CircuitBreakerConfig(
                    name="redis_cache",
                    failure_threshold=5,
                    recovery_timeout=30,
                    success_threshold=3,
                    timeout_seconds=5.0,
                    window_size=200,
                    minimum_requests=20,
                    failure_rate_threshold=0.3,
                    slow_call_duration=2.0,
                    slow_call_rate_threshold=0.2
                ),
                
                # External API circuit breakers
                CircuitBreakerConfig(
                    name="spotify_api",
                    failure_threshold=5,
                    recovery_timeout=120,
                    success_threshold=3,
                    timeout_seconds=15.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.4,
                    slow_call_duration=8.0,
                    slow_call_rate_threshold=0.3
                ),
                CircuitBreakerConfig(
                    name="youtube_api",
                    failure_threshold=8,
                    recovery_timeout=90,
                    success_threshold=3,
                    timeout_seconds=20.0,
                    window_size=150,
                    minimum_requests=15,
                    failure_rate_threshold=0.5,
                    slow_call_duration=12.0,
                    slow_call_rate_threshold=0.4
                ),
                CircuitBreakerConfig(
                    name="instagram_api",
                    failure_threshold=6,
                    recovery_timeout=90,
                    success_threshold=3,
                    timeout_seconds=15.0,
                    window_size=100,
                    minimum_requests=10,
                    failure_rate_threshold=0.4,
                    slow_call_duration=8.0,
                    slow_call_rate_threshold=0.3
                )
            ]
            
            # Create all circuit breakers
            for config in circuit_breaker_configs:
                self.create_circuit_breaker(config)
            
            logger.info(f"Platform circuit breakers configured: {len(circuit_breaker_configs)} breakers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform circuit breakers: {e}")
            return False
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""        with self.lock:
            statuses = {}
            for name, cb in self.circuit_breakers.items():
                statuses[name] = cb.get_status()
            
            # Calculate summary statistics
            total_breakers = len(self.circuit_breakers)
            open_breakers = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN)
            half_open_breakers = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.HALF_OPEN)
            closed_breakers = total_breakers - open_breakers - half_open_breakers
            
            summary = {
                "total_circuit_breakers": total_breakers,
                "open_circuit_breakers": open_breakers,
                "half_open_circuit_breakers": half_open_breakers,
                "closed_circuit_breakers": closed_breakers,
                "health_percentage": round((closed_breakers / total_breakers) * 100, 1) if total_breakers > 0 else 100.0
            }
            
            return {
                "summary": summary,
                "circuit_breakers": statuses,
                "timestamp": datetime.now().isoformat()
            }
