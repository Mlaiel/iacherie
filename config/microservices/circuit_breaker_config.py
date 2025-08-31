"""Circuit Breaker Configuration for IA-Influencer Agent Platform
=============================================================

Professional circuit breaker configuration for microservices resilience.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseSettings, Field, validator
import asyncio
from collections import deque
import statistics


class CircuitState(str, Enum):
    """Circuit breaker states."""    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Circuit is open, requests fail fast
    HALF_OPEN = "half_open" # Testing if service is back


class FailureType(str, Enum):
    """Types of failures that can trigger circuit breaker."""    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CUSTOM = "custom"


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    rejected_requests: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    failure_rate: float = 0.0
    average_response_time: float = 0.0
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def update_success(self, response_time: float):
        """Update metrics for successful request."""        self.total_requests += 1
        self.successful_requests += 1
        self.last_success_time = time.time()
        self.recent_response_times.append(response_time)
        self._update_derived_metrics()
    
    def update_failure(self, failure_type: FailureType):
        """Update metrics for failed request."""        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure_time = time.time()
        if failure_type == FailureType.TIMEOUT:
            self.timeout_requests += 1
        self._update_derived_metrics()
    
    def update_rejection(self):
        """Update metrics for rejected request (circuit open)."""        self.rejected_requests += 1
    
    def _update_derived_metrics(self):
        """Update derived metrics."""        if self.total_requests > 0:
            self.failure_rate = self.failed_requests / self.total_requests
        
        if self.recent_response_times:
            self.average_response_time = statistics.mean(self.recent_response_times)
    
    def reset(self):
        """Reset all metrics."""        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeout_requests = 0
        self.rejected_requests = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.failure_rate = 0.0
        self.average_response_time = 0.0
        self.recent_response_times.clear()


@dataclass
class CircuitBreakerRule:
    """Circuit breaker rule configuration."""    name: str
    failure_threshold: int = 5           # Number of failures to open circuit
    success_threshold: int = 3           # Number of successes to close circuit
    timeout_threshold: float = 30.0      # Timeout threshold in seconds
    failure_rate_threshold: float = 0.5  # Failure rate threshold (0.0-1.0)
    time_window: int = 60                # Time window for failure counting (seconds)
    recovery_timeout: int = 60           # Time to wait before half-open (seconds)
    minimum_requests: int = 10           # Minimum requests before evaluating
    slow_call_threshold: float = 5.0     # Slow call threshold in seconds
    slow_call_rate_threshold: float = 0.5 # Slow call rate threshold
    enabled: bool = True
    fallback_enabled: bool = True


class CircuitBreakerConfig(BaseSettings):
    """    Centralized circuit breaker configuration for microservices resilience.
    Implements multiple circuit breaker patterns and failure detection strategies.
    """    
    # Global circuit breaker settings
    enabled: bool = Field(True, env="CIRCUIT_BREAKER_ENABLED")
    default_failure_threshold: int = Field(5, env="CB_DEFAULT_FAILURE_THRESHOLD")
    default_success_threshold: int = Field(3, env="CB_DEFAULT_SUCCESS_THRESHOLD")
    default_timeout_threshold: float = Field(30.0, env="CB_DEFAULT_TIMEOUT_THRESHOLD")
    default_failure_rate_threshold: float = Field(0.5, env="CB_DEFAULT_FAILURE_RATE_THRESHOLD")
    default_time_window: int = Field(60, env="CB_DEFAULT_TIME_WINDOW")
    default_recovery_timeout: int = Field(60, env="CB_DEFAULT_RECOVERY_TIMEOUT")
    default_minimum_requests: int = Field(10, env="CB_DEFAULT_MINIMUM_REQUESTS")
    
    # Slow call detection
    slow_call_detection_enabled: bool = Field(True, env="CB_SLOW_CALL_DETECTION_ENABLED")
    default_slow_call_threshold: float = Field(5.0, env="CB_DEFAULT_SLOW_CALL_THRESHOLD")
    default_slow_call_rate_threshold: float = Field(0.5, env="CB_DEFAULT_SLOW_CALL_RATE_THRESHOLD")
    
    # Fallback settings
    fallback_enabled: bool = Field(True, env="CB_FALLBACK_ENABLED")
    fallback_timeout: float = Field(1.0, env="CB_FALLBACK_TIMEOUT")
    
    # Monitoring settings
    metrics_enabled: bool = Field(True, env="CB_METRICS_ENABLED")
    metrics_retention_period: int = Field(3600, env="CB_METRICS_RETENTION_PERIOD")  # 1 hour
    health_check_enabled: bool = Field(True, env="CB_HEALTH_CHECK_ENABLED")
    health_check_interval: int = Field(30, env="CB_HEALTH_CHECK_INTERVAL")
    
    # Notification settings
    notifications_enabled: bool = Field(True, env="CB_NOTIFICATIONS_ENABLED")
    notify_on_state_change: bool = Field(True, env="CB_NOTIFY_ON_STATE_CHANGE")
    notify_on_failure_threshold: bool = Field(True, env="CB_NOTIFY_ON_FAILURE_THRESHOLD")
    
    # Advanced settings
    jitter_enabled: bool = Field(True, env="CB_JITTER_ENABLED")
    jitter_max_delay: float = Field(1.0, env="CB_JITTER_MAX_DELAY")
    bulkhead_enabled: bool = Field(True, env="CB_BULKHEAD_ENABLED")
    bulkhead_max_concurrent_calls: int = Field(100, env="CB_BULKHEAD_MAX_CONCURRENT_CALLS")
    
    class Config:
        env_prefix = "CIRCUIT_BREAKER_"
        case_sensitive = False


class CircuitBreaker:
    """    Production-ready circuit breaker implementation with advanced features.
    """    
    def __init__(self, name: str, rule: CircuitBreakerRule, config: CircuitBreakerConfig):
        self.name = name
        self.rule = rule
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.last_state_change = time.time()
        self.concurrent_calls = 0
        self.max_concurrent_calls = config.bulkhead_max_concurrent_calls
        self._lock = threading.Lock()
        self.fallback_function: Optional[Callable] = None
        self.state_change_listeners: List[Callable] = []
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""        if not self.rule.enabled:
            return func(*args, **kwargs)
        
        # Check bulkhead limit
        if self.config.bulkhead_enabled:
            with self._lock:
                if self.concurrent_calls >= self.max_concurrent_calls:
                    raise Exception(f"Bulkhead limit exceeded for {self.name}")
                self.concurrent_calls += 1
        
        try:
            # Check circuit state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.metrics.update_rejection()
                    return self._execute_fallback(*args, **kwargs)
            
            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                # Update metrics for success
                self.metrics.update_success(response_time)
                
                # Check if we should close circuit (from half-open)
                if self.state == CircuitState.HALF_OPEN:
                    if self._should_close_circuit():
                        self._transition_to_closed()
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                failure_type = self._classify_failure(e)
                
                # Update metrics for failure
                self.metrics.update_failure(failure_type)
                
                # Check if we should open circuit
                if self.state == CircuitState.CLOSED:
                    if self._should_open_circuit():
                        self._transition_to_open()
                elif self.state == CircuitState.HALF_OPEN:
                    self._transition_to_open()
                
                # Try fallback or re-raise
                if self.rule.fallback_enabled and self.fallback_function:
                    return self._execute_fallback(*args, **kwargs)
                else:
                    raise
        
        finally:
            if self.config.bulkhead_enabled:
                with self._lock:
                    self.concurrent_calls = max(0, self.concurrent_calls - 1)
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection."""        if not self.rule.enabled:
            return await func(*args, **kwargs)
        
        # Similar implementation to sync version but with async/await
        if self.config.bulkhead_enabled:
            with self._lock:
                if self.concurrent_calls >= self.max_concurrent_calls:
                    raise Exception(f"Bulkhead limit exceeded for {self.name}")
                self.concurrent_calls += 1
        
        try:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.metrics.update_rejection()
                    return await self._execute_fallback_async(*args, **kwargs)
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                
                self.metrics.update_success(response_time)
                
                if self.state == CircuitState.HALF_OPEN:
                    if self._should_close_circuit():
                        self._transition_to_closed()
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                failure_type = self._classify_failure(e)
                
                self.metrics.update_failure(failure_type)
                
                if self.state == CircuitState.CLOSED:
                    if self._should_open_circuit():
                        self._transition_to_open()
                elif self.state == CircuitState.HALF_OPEN:
                    self._transition_to_open()
                
                if self.rule.fallback_enabled and self.fallback_function:
                    return await self._execute_fallback_async(*args, **kwargs)
                else:
                    raise
        
        finally:
            if self.config.bulkhead_enabled:
                with self._lock:
                    self.concurrent_calls = max(0, self.concurrent_calls - 1)
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened."""        # Check minimum requests threshold
        if self.metrics.total_requests < self.rule.minimum_requests:
            return False
        
        # Check failure threshold
        if self.metrics.failed_requests >= self.rule.failure_threshold:
            return True
        
        # Check failure rate threshold
        if self.metrics.failure_rate >= self.rule.failure_rate_threshold:
            return True
        
        # Check slow call rate
        if self.config.slow_call_detection_enabled:
            slow_calls = sum(1 for rt in self.metrics.recent_response_times 
                           if rt >= self.rule.slow_call_threshold)
            if len(self.metrics.recent_response_times) > 0:
                slow_call_rate = slow_calls / len(self.metrics.recent_response_times)
                if slow_call_rate >= self.rule.slow_call_rate_threshold:
                    return True
        
        return False
    
    def _should_close_circuit(self) -> bool:
        """Check if circuit should be closed (from half-open state)."""        return self.metrics.successful_requests >= self.rule.success_threshold
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset circuit (from open to half-open)."""        return (time.time() - self.last_state_change) >= self.rule.recovery_timeout
    
    def _transition_to_open(self):
        """Transition circuit to open state."""        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
            self._notify_state_change(CircuitState.OPEN)
    
    def _transition_to_half_open(self):
        """Transition circuit to half-open state."""        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.last_state_change = time.time()
            self.metrics.reset()  # Reset metrics for fresh evaluation
            self._notify_state_change(CircuitState.HALF_OPEN)
    
    def _transition_to_closed(self):
        """Transition circuit to closed state."""        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.last_state_change = time.time()
            self._notify_state_change(CircuitState.CLOSED)
    
    def _classify_failure(self, exception: Exception) -> FailureType:
        """Classify the type of failure."""        if isinstance(exception, TimeoutError):
            return FailureType.TIMEOUT
        elif isinstance(exception, ConnectionError):
            return FailureType.CONNECTION_ERROR
        elif hasattr(exception, 'status_code'):
            if exception.status_code >= 500:
                return FailureType.SERVICE_UNAVAILABLE
            elif exception.status_code == 429:
                return FailureType.RATE_LIMIT_EXCEEDED
            else:
                return FailureType.HTTP_ERROR
        else:
            return FailureType.CUSTOM
    
    def _execute_fallback(self, *args, **kwargs):
        """Execute fallback function."""        if self.fallback_function:
            try:
                return self.fallback_function(*args, **kwargs)
            except Exception as e:
                raise Exception(f"Fallback failed for {self.name}: {str(e)}")
        else:
            raise Exception(f"Circuit breaker {self.name} is open and no fallback provided")
    
    async def _execute_fallback_async(self, *args, **kwargs):
        """Execute async fallback function."""        if self.fallback_function:
            try:
                if asyncio.iscoroutinefunction(self.fallback_function):
                    return await self.fallback_function(*args, **kwargs)
                else:
                    return self.fallback_function(*args, **kwargs)
            except Exception as e:
                raise Exception(f"Async fallback failed for {self.name}: {str(e)}")
        else:
            raise Exception(f"Circuit breaker {self.name} is open and no fallback provided")
    
    def _notify_state_change(self, new_state: CircuitState):
        """Notify listeners of state change."""        if self.config.notifications_enabled and self.config.notify_on_state_change:
            for listener in self.state_change_listeners:
                try:
                    listener(self.name, new_state, self.metrics)
                except Exception:
                    pass  # Don't let notification failures affect circuit breaker
    
    def set_fallback(self, fallback_function: Callable):
        """Set fallback function."""        self.fallback_function = fallback_function
    
    def add_state_change_listener(self, listener: Callable):
        """Add state change listener."""        self.state_change_listeners.append(listener)
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics."""        return self.metrics
    
    def reset(self):
        """Reset circuit breaker to closed state."""        with self._lock:
            self.state = CircuitState.CLOSED
            self.metrics.reset()
            self.last_state_change = time.time()
            self.concurrent_calls = 0


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()
    
    def get_or_create(self, name: str, rule: Optional[CircuitBreakerRule] = None) -> CircuitBreaker:
        """Get existing circuit breaker or create new one."""        with self._lock:
            if name not in self.circuit_breakers:
                if rule is None:
                    rule = CircuitBreakerRule(name=name)
                self.circuit_breakers[name] = CircuitBreaker(name, rule, self.config)
            return self.circuit_breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""        return self.circuit_breakers.get(name)
    
    def remove(self, name: str):
        """Remove circuit breaker."""        with self._lock:
            if name in self.circuit_breakers:
                del self.circuit_breakers[name]
    
    def list_all(self) -> Dict[str, CircuitBreaker]:
        """List all circuit breakers."""        return self.circuit_breakers.copy()
    
    def get_metrics_summary(self) -> Dict[str, Dict]:
        """Get metrics summary for all circuit breakers."""        summary = {}
        for name, cb in self.circuit_breakers.items():
            metrics = cb.get_metrics()
            summary[name] = {
                "state": cb.state,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "rejected_requests": metrics.rejected_requests,
                "failure_rate": metrics.failure_rate,
                "average_response_time": metrics.average_response_time,
                "last_failure_time": metrics.last_failure_time,
                "last_success_time": metrics.last_success_time
            }
        return summary


# Pre-configured circuit breaker rules for IA-Influencer Agent microservices
MICROSERVICE_CIRCUIT_BREAKER_RULES = {
    "api-gateway": CircuitBreakerRule(
        name="api-gateway",
        failure_threshold=5,
        success_threshold=3,
        timeout_threshold=10.0,
        failure_rate_threshold=0.3,
        time_window=60,
        recovery_timeout=30,
        minimum_requests=20,
        slow_call_threshold=2.0,
        slow_call_rate_threshold=0.4
    ),
    "spotify-agent": CircuitBreakerRule(
        name="spotify-agent",
        failure_threshold=3,
        success_threshold=2,
        timeout_threshold=30.0,
        failure_rate_threshold=0.5,
        time_window=120,
        recovery_timeout=60,
        minimum_requests=10,
        slow_call_threshold=5.0,
        slow_call_rate_threshold=0.3
    ),
    "content-protection": CircuitBreakerRule(
        name="content-protection",
        failure_threshold=8,
        success_threshold=5,
        timeout_threshold=60.0,
        failure_rate_threshold=0.4,
        time_window=180,
        recovery_timeout=120,
        minimum_requests=15,
        slow_call_threshold=10.0,
        slow_call_rate_threshold=0.5
    ),
    "fingerprinting-engine": CircuitBreakerRule(
        name="fingerprinting-engine",
        failure_threshold=10,
        success_threshold=3,
        timeout_threshold=120.0,
        failure_rate_threshold=0.6,
        time_window=300,
        recovery_timeout=180,
        minimum_requests=5,
        slow_call_threshold=30.0,
        slow_call_rate_threshold=0.7
    ),
    "web-crawler": CircuitBreakerRule(
        name="web-crawler",
        failure_threshold=15,
        success_threshold=5,
        timeout_threshold=180.0,
        failure_rate_threshold=0.7,
        time_window=600,
        recovery_timeout=300,
        minimum_requests=8,
        slow_call_threshold=60.0,
        slow_call_rate_threshold=0.8
    ),
    "monetization-engine": CircuitBreakerRule(
        name="monetization-engine",
        failure_threshold=3,
        success_threshold=2,
        timeout_threshold=45.0,
        failure_rate_threshold=0.2,
        time_window=300,
        recovery_timeout=120,
        minimum_requests=5,
        slow_call_threshold=15.0,
        slow_call_rate_threshold=0.3
    ),
    "notification-service": CircuitBreakerRule(
        name="notification-service",
        failure_threshold=5,
        success_threshold=3,
        timeout_threshold=15.0,
        failure_rate_threshold=0.4,
        time_window=60,
        recovery_timeout=30,
        minimum_requests=10,
        slow_call_threshold=3.0,
        slow_call_rate_threshold=0.5
    ),
    "analytics-engine": CircuitBreakerRule(
        name="analytics-engine",
        failure_threshold=5,
        success_threshold=3,
        timeout_threshold=90.0,
        failure_rate_threshold=0.5,
        time_window=240,
        recovery_timeout=90,
        minimum_requests=12,
        slow_call_threshold=20.0,
        slow_call_rate_threshold=0.6
    ),
    "database": CircuitBreakerRule(
        name="database",
        failure_threshold=3,
        success_threshold=2,
        timeout_threshold=20.0,
        failure_rate_threshold=0.3,
        time_window=60,
        recovery_timeout=45,
        minimum_requests=15,
        slow_call_threshold=5.0,
        slow_call_rate_threshold=0.4
    ),
    "redis-cache": CircuitBreakerRule(
        name="redis-cache",
        failure_threshold=5,
        success_threshold=3,
        timeout_threshold=5.0,
        failure_rate_threshold=0.5,
        time_window=30,
        recovery_timeout=20,
        minimum_requests=20,
        slow_call_threshold=1.0,
        slow_call_rate_threshold=0.6
    ),
    "external-apis": CircuitBreakerRule(
        name="external-apis",
        failure_threshold=10,
        success_threshold=5,
        timeout_threshold=60.0,
        failure_rate_threshold=0.6,
        time_window=300,
        recovery_timeout=180,
        minimum_requests=8,
        slow_call_threshold=20.0,
        slow_call_rate_threshold=0.7
    )
}


# Export configuration instance
circuit_breaker_config = CircuitBreakerConfig()
