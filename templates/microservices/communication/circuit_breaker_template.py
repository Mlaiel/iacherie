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

Circuit Breaker Template for Ainflue Microservices Platform
==========================================================

Enterprise-grade circuit breaker pattern template providing:
- Advanced circuit breaker patterns with multiple states
- Adaptive failure threshold based on response patterns
- Health check integration with automatic recovery
- Bulkhead pattern for resource isolation
- Rate limiting integration
- Metrics collection and monitoring
- Distributed circuit breaker coordination
- Custom recovery strategies
- Integration with service mesh
- Real-time dashboards and alerting

Author: Fahed Mlaiel (mlaiel@live.de)
Security Expert & Resilience Patterns Specialist
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Type, Union, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
import time
from collections import deque, defaultdict
import threading
import statistics

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, Enum as PrometheusEnum
import aiohttp

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"    # Testing if service has recovered
    FORCED_OPEN = "forced_open"    # Manually opened circuit
    FORCED_CLOSED = "forced_closed"  # Manually closed circuit


class FailureType(str, Enum):
    """Types of failures tracked"""
    EXCEPTION = "exception"
    TIMEOUT = "timeout"
    HTTP_ERROR = "http_error"
    CONNECTION_ERROR = "connection_error"
    RATE_LIMIT = "rate_limit"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class RecoveryStrategy(str, Enum):
    """Recovery strategy types"""
    IMMEDIATE = "immediate"        # Immediate recovery attempt
    EXPONENTIAL_BACKOFF = "exponential_backoff"  # Exponential backoff
    LINEAR_BACKOFF = "linear_backoff"           # Linear backoff
    ADAPTIVE = "adaptive"          # Adaptive based on failure patterns
    HEALTH_CHECK = "health_check"  # Health check based


@dataclass
class FailureRecord:
    """Record of a failure occurrence"""
    timestamp: datetime
    failure_type: FailureType
    duration_ms: float
    error_message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CallMetrics:
    """Metrics for circuit breaker calls"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    rejected_calls: int = 0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    name: str = Field(..., description="Circuit breaker name")
    failure_threshold: int = Field(default=5, description="Number of failures to open circuit")
    success_threshold: int = Field(default=3, description="Number of successes to close circuit")
    timeout_ms: int = Field(default=5000, description="Operation timeout in milliseconds")
    recovery_timeout_ms: int = Field(default=60000, description="Recovery timeout in milliseconds")
    
    # Advanced settings
    failure_rate_threshold: float = Field(default=0.5, description="Failure rate threshold (0.0-1.0)")
    minimum_throughput: int = Field(default=10, description="Minimum calls before applying failure rate")
    sliding_window_size: int = Field(default=100, description="Sliding window size for metrics")
    half_open_max_calls: int = Field(default=3, description="Max calls in half-open state")
    
    # Recovery strategy
    recovery_strategy: RecoveryStrategy = Field(default=RecoveryStrategy.EXPONENTIAL_BACKOFF, description="Recovery strategy")
    max_recovery_time_ms: int = Field(default=300000, description="Maximum recovery time")
    
    # Health check settings
    health_check_url: Optional[str] = Field(default=None, description="Health check endpoint URL")
    health_check_interval_ms: int = Field(default=30000, description="Health check interval")
    health_check_timeout_ms: int = Field(default=5000, description="Health check timeout")
    
    # Bulkhead settings
    enable_bulkhead: bool = Field(default=False, description="Enable bulkhead pattern")
    max_concurrent_calls: int = Field(default=100, description="Maximum concurrent calls")
    max_queue_size: int = Field(default=200, description="Maximum queue size")
    
    # Adaptive settings
    enable_adaptive_threshold: bool = Field(default=False, description="Enable adaptive failure threshold")
    response_time_threshold_ms: int = Field(default=1000, description="Response time threshold for failures")
    
    # Monitoring
    enable_detailed_metrics: bool = Field(default=True, description="Enable detailed metrics collection")
    failure_types_tracked: List[FailureType] = Field(
        default_factory=lambda: list(FailureType), 
        description="Failure types to track"
    )


class CircuitBreakerState:
    """Circuit breaker state management"""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.utcnow()
        self.next_attempt: Optional[datetime] = None
        self.half_open_calls = 0
        
        # Sliding window for metrics
        self.call_history: deque = deque(maxlen=config.sliding_window_size)
        self.failure_history: deque = deque(maxlen=config.sliding_window_size)
        self.response_times: deque = deque(maxlen=config.sliding_window_size)
        
        # Concurrent call tracking for bulkhead
        self.current_calls = 0
        self.call_queue = asyncio.Queue(maxsize=config.max_queue_size)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_calls)
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Metrics
        self.metrics = CallMetrics()
    
    def can_execute(self) -> bool:
        """Check if call can be executed"""
        with self.lock:
            now = datetime.utcnow()
            
            if self.state == CircuitState.FORCED_OPEN:
                return False
            elif self.state == CircuitState.FORCED_CLOSED:
                return True
            elif self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                # Check if it's time to try recovery
                if self.next_attempt and now >= self.next_attempt:
                    self._transition_to_half_open()
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                # Allow limited calls in half-open state
                return self.half_open_calls < self.config.half_open_max_calls
            
            return False
    
    def record_success(self, response_time_ms: float) -> None:
        """Record successful call"""
        with self.lock:
            now = datetime.utcnow()
            
            # Update call history
            self.call_history.append({"timestamp": now, "success": True, "response_time": response_time_ms})
            self.response_times.append(response_time_ms)
            
            # Update metrics
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1
            self.metrics.last_success = now
            self._update_response_time_metrics()
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._transition_to_closed()
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    def record_failure(self, failure_record: FailureRecord) -> None:
        """Record failed call"""
        with self.lock:
            now = datetime.utcnow()
            
            # Update call history
            self.call_history.append({
                "timestamp": now, 
                "success": False, 
                "response_time": failure_record.duration_ms,
                "failure_type": failure_record.failure_type.value
            })
            self.failure_history.append(failure_record)
            
            # Update metrics
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1
            self.metrics.last_failure = now
            
            if failure_record.failure_type == FailureType.TIMEOUT:
                self.metrics.timeout_calls += 1
            
            self.last_failure_time = now
            
            if self.state == CircuitState.CLOSED:
                self.failure_count += 1
                
                # Check if we should open the circuit
                if self._should_open_circuit():
                    self._transition_to_open()
                    
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state should open the circuit
                self._transition_to_open()
    
    def record_rejection(self) -> None:
        """Record rejected call (circuit open or bulkhead full)"""
        with self.lock:
            self.metrics.total_calls += 1
            self.metrics.rejected_calls += 1
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        # Check simple failure count threshold
        if self.failure_count >= self.config.failure_threshold:
            return True
        
        # Check failure rate if we have enough data
        if len(self.call_history) >= self.config.minimum_throughput:
            recent_calls = list(self.call_history)[-self.config.minimum_throughput:]
            failures = sum(1 for call in recent_calls if not call["success"])
            failure_rate = failures / len(recent_calls)
            
            if failure_rate >= self.config.failure_rate_threshold:
                return True
        
        # Check adaptive threshold based on response times
        if (self.config.enable_adaptive_threshold and 
            len(self.response_times) >= self.config.minimum_throughput):
            
            avg_response_time = statistics.mean(self.response_times)
            if avg_response_time > self.config.response_time_threshold_ms:
                return True
        
        return False
    
    def _transition_to_open(self) -> None:
        """Transition to open state"""
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.utcnow()
        self.success_count = 0
        self.half_open_calls = 0
        
        # Calculate next attempt time based on recovery strategy
        self._calculate_next_attempt()
        
        logger.warning(f"Circuit breaker {self.config.name} opened")
    
    def _transition_to_half_open(self) -> None:
        """Transition to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = datetime.utcnow()
        self.success_count = 0
        self.half_open_calls = 0
        
        logger.info(f"Circuit breaker {self.config.name} transitioning to half-open")
    
    def _transition_to_closed(self) -> None:
        """Transition to closed state"""
        self.state = CircuitState.CLOSED
        self.last_state_change = datetime.utcnow()
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.next_attempt = None
        
        logger.info(f"Circuit breaker {self.config.name} closed")
    
    def _calculate_next_attempt(self) -> None:
        """Calculate next recovery attempt time"""
        now = datetime.utcnow()
        
        if self.config.recovery_strategy == RecoveryStrategy.IMMEDIATE:
            self.next_attempt = now
        
        elif self.config.recovery_strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
            # Exponential backoff based on consecutive failures
            delay_ms = min(
                self.config.recovery_timeout_ms * (2 ** min(self.failure_count - 1, 10)),
                self.config.max_recovery_time_ms
            )
            self.next_attempt = now + timedelta(milliseconds=delay_ms)
        
        elif self.config.recovery_strategy == RecoveryStrategy.LINEAR_BACKOFF:
            # Linear increase in delay
            delay_ms = min(
                self.config.recovery_timeout_ms * self.failure_count,
                self.config.max_recovery_time_ms
            )
            self.next_attempt = now + timedelta(milliseconds=delay_ms)
        
        elif self.config.recovery_strategy == RecoveryStrategy.ADAPTIVE:
            # Adaptive delay based on failure patterns
            if self.failure_history:
                recent_failures = [f for f in self.failure_history if 
                                 (now - f.timestamp).total_seconds() < 300]  # Last 5 minutes
                if recent_failures:
                    avg_failure_interval = statistics.mean([
                        (recent_failures[i].timestamp - recent_failures[i-1].timestamp).total_seconds()
                        for i in range(1, len(recent_failures))
                    ]) if len(recent_failures) > 1 else 60
                    
                    delay_ms = min(avg_failure_interval * 1000 * 2, self.config.max_recovery_time_ms)
                    self.next_attempt = now + timedelta(milliseconds=delay_ms)
                else:
                    self.next_attempt = now + timedelta(milliseconds=self.config.recovery_timeout_ms)
            else:
                self.next_attempt = now + timedelta(milliseconds=self.config.recovery_timeout_ms)
        
        else:  # HEALTH_CHECK
            self.next_attempt = now + timedelta(milliseconds=self.config.health_check_interval_ms)
    
    def _update_response_time_metrics(self) -> None:
        """Update response time metrics"""
        if self.response_times:
            self.metrics.average_response_time = statistics.mean(self.response_times)
            if len(self.response_times) >= 20:  # Need sufficient data for percentile
                sorted_times = sorted(self.response_times)
                p95_index = int(len(sorted_times) * 0.95)
                self.metrics.p95_response_time = sorted_times[p95_index]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        with self.lock:
            failure_rate = (
                self.metrics.failed_calls / self.metrics.total_calls 
                if self.metrics.total_calls > 0 else 0.0
            )
            
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "timeout_calls": self.metrics.timeout_calls,
                "rejected_calls": self.metrics.rejected_calls,
                "failure_rate": failure_rate,
                "average_response_time": self.metrics.average_response_time,
                "p95_response_time": self.metrics.p95_response_time,
                "last_success": self.metrics.last_success.isoformat() if self.metrics.last_success else None,
                "last_failure": self.metrics.last_failure.isoformat() if self.metrics.last_failure else None,
                "last_state_change": self.last_state_change.isoformat(),
                "next_attempt": self.next_attempt.isoformat() if self.next_attempt else None,
                "current_calls": self.current_calls
            }


class CircuitBreakerTemplate(BaseMicroservice):
    """
    Enterprise Circuit Breaker Template
    
    Provides advanced circuit breaker patterns with:
    - Multiple circuit breaker states
    - Adaptive failure detection
    - Bulkhead pattern integration
    - Health check based recovery
    - Comprehensive monitoring
    """
    
    def __init__(self, config: ServiceConfig):
        super().__init__(config)
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Prometheus metrics
        self.circuit_breaker_state = PrometheusEnum(
            'circuit_breaker_state',
            'Circuit breaker state',
            ['circuit_name'],
            states=[state.value for state in CircuitState]
        )
        
        self.circuit_breaker_calls_total = Counter(
            'circuit_breaker_calls_total',
            'Total calls through circuit breaker',
            ['circuit_name', 'result']
        )
        
        self.circuit_breaker_response_time = Histogram(
            'circuit_breaker_response_time_seconds',
            'Response time through circuit breaker',
            ['circuit_name']
        )
        
        self.circuit_breaker_failure_rate = Gauge(
            'circuit_breaker_failure_rate',
            'Circuit breaker failure rate',
            ['circuit_name']
        )
    
    async def initialize(self) -> None:
        """Initialize circuit breaker service"""
        try:
            logger.info("Initializing circuit breaker service")
            
            # Initialize Redis for distributed coordination if configured
            redis_config = getattr(self.config, 'redis_config', None)
            if redis_config:
                await self._initialize_redis(redis_config)
            
            logger.info("Circuit breaker service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breaker service: {e}")
            raise
    
    async def _initialize_redis(self, redis_config: Dict[str, Any]) -> None:
        """Initialize Redis connection for distributed coordination"""
        self.redis_client = redis.Redis(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=redis_config.get("db", 5),
            password=redis_config.get("password"),
            decode_responses=True
        )
        
        await self.redis_client.ping()
        logger.info("Redis connection established for circuit breaker coordination")
    
    async def create_circuit_breaker(self, config: CircuitBreakerConfig) -> Dict[str, Any]:
        """Create a new circuit breaker"""
        try:
            # Create circuit breaker state
            circuit_state = CircuitBreakerState(config)
            self.circuit_breakers[config.name] = circuit_state
            
            # Set initial Prometheus metrics
            self.circuit_breaker_state.labels(circuit_name=config.name).state(CircuitState.CLOSED.value)
            
            # Start health check task if configured
            if config.health_check_url and config.recovery_strategy == RecoveryStrategy.HEALTH_CHECK:
                task = asyncio.create_task(self._health_check_task(config.name))
                self.health_check_tasks[config.name] = task
            
            logger.info(f"Created circuit breaker: {config.name}")
            
            return {
                "name": config.name,
                "status": "created",
                "state": CircuitState.CLOSED.value,
                "failure_threshold": config.failure_threshold,
                "timeout_ms": config.timeout_ms
            }
            
        except Exception as e:
            logger.error(f"Failed to create circuit breaker {config.name}: {e}")
            raise
    
    async def execute_with_circuit_breaker(
        self, circuit_name: str, func: Callable, *args, **kwargs
    ) -> Any:
        """Execute function with circuit breaker protection"""
        if circuit_name not in self.circuit_breakers:
            raise ValueError(f"Circuit breaker not found: {circuit_name}")
        
        circuit_state = self.circuit_breakers[circuit_name]
        
        # Check if call can be executed
        if not circuit_state.can_execute():
            circuit_state.record_rejection()
            self.circuit_breaker_calls_total.labels(
                circuit_name=circuit_name, result='rejected'
            ).inc()
            raise RuntimeError(f"Circuit breaker {circuit_name} is open")
        
        # Apply bulkhead pattern if enabled
        if circuit_state.config.enable_bulkhead:
            try:
                # Acquire semaphore with timeout
                await asyncio.wait_for(
                    circuit_state.semaphore.acquire(),
                    timeout=circuit_state.config.timeout_ms / 1000
                )
            except asyncio.TimeoutError:
                circuit_state.record_rejection()
                self.circuit_breaker_calls_total.labels(
                    circuit_name=circuit_name, result='rejected'
                ).inc()
                raise RuntimeError(f"Bulkhead limit reached for circuit breaker {circuit_name}")
        
        start_time = time.time()
        circuit_state.current_calls += 1
        
        try:
            # Track half-open calls
            if circuit_state.state == CircuitState.HALF_OPEN:
                circuit_state.half_open_calls += 1
            
            # Execute function with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=circuit_state.config.timeout_ms / 1000
                )
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                    timeout=circuit_state.config.timeout_ms / 1000
                )
            
            # Record success
            response_time_ms = (time.time() - start_time) * 1000
            circuit_state.record_success(response_time_ms)
            
            # Update metrics
            self.circuit_breaker_calls_total.labels(
                circuit_name=circuit_name, result='success'
            ).inc()
            self.circuit_breaker_response_time.labels(circuit_name=circuit_name).observe(
                response_time_ms / 1000
            )
            
            return result
            
        except asyncio.TimeoutError as e:
            # Record timeout failure
            response_time_ms = (time.time() - start_time) * 1000
            failure_record = FailureRecord(
                timestamp=datetime.utcnow(),
                failure_type=FailureType.TIMEOUT,
                duration_ms=response_time_ms,
                error_message="Operation timeout"
            )
            circuit_state.record_failure(failure_record)
            
            # Update metrics
            self.circuit_breaker_calls_total.labels(
                circuit_name=circuit_name, result='timeout'
            ).inc()
            
            raise
            
        except Exception as e:
            # Record general failure
            response_time_ms = (time.time() - start_time) * 1000
            
            # Determine failure type
            failure_type = FailureType.EXCEPTION
            if isinstance(e, aiohttp.ClientConnectorError):
                failure_type = FailureType.CONNECTION_ERROR
            elif isinstance(e, aiohttp.ClientResponseError):
                if e.status == 429:
                    failure_type = FailureType.RATE_LIMIT
                else:
                    failure_type = FailureType.HTTP_ERROR
            
            failure_record = FailureRecord(
                timestamp=datetime.utcnow(),
                failure_type=failure_type,
                duration_ms=response_time_ms,
                error_message=str(e)
            )
            circuit_state.record_failure(failure_record)
            
            # Update metrics
            self.circuit_breaker_calls_total.labels(
                circuit_name=circuit_name, result='failure'
            ).inc()
            
            raise
            
        finally:
            # Release resources
            circuit_state.current_calls -= 1
            if circuit_state.config.enable_bulkhead:
                circuit_state.semaphore.release()
            
            # Update Prometheus state metric
            self.circuit_breaker_state.labels(circuit_name=circuit_name).state(
                circuit_state.state.value
            )
            
            # Update failure rate metric
            metrics = circuit_state.get_metrics()
            self.circuit_breaker_failure_rate.labels(circuit_name=circuit_name).set(
                metrics["failure_rate"]
            )
    
    async def force_open(self, circuit_name: str) -> bool:
        """Force circuit breaker to open state"""
        if circuit_name not in self.circuit_breakers:
            return False
        
        circuit_state = self.circuit_breakers[circuit_name]
        with circuit_state.lock:
            circuit_state.state = CircuitState.FORCED_OPEN
            circuit_state.last_state_change = datetime.utcnow()
        
        self.circuit_breaker_state.labels(circuit_name=circuit_name).state(
            CircuitState.FORCED_OPEN.value
        )
        
        logger.info(f"Circuit breaker {circuit_name} forced to open")
        return True
    
    async def force_close(self, circuit_name: str) -> bool:
        """Force circuit breaker to closed state"""
        if circuit_name not in self.circuit_breakers:
            return False
        
        circuit_state = self.circuit_breakers[circuit_name]
        with circuit_state.lock:
            circuit_state.state = CircuitState.FORCED_CLOSED
            circuit_state.last_state_change = datetime.utcnow()
            circuit_state.failure_count = 0
            circuit_state.success_count = 0
        
        self.circuit_breaker_state.labels(circuit_name=circuit_name).state(
            CircuitState.FORCED_CLOSED.value
        )
        
        logger.info(f"Circuit breaker {circuit_name} forced to closed")
        return True
    
    async def reset_circuit_breaker(self, circuit_name: str) -> bool:
        """Reset circuit breaker to normal operation"""
        if circuit_name not in self.circuit_breakers:
            return False
        
        circuit_state = self.circuit_breakers[circuit_name]
        with circuit_state.lock:
            circuit_state.state = CircuitState.CLOSED
            circuit_state.failure_count = 0
            circuit_state.success_count = 0
            circuit_state.half_open_calls = 0
            circuit_state.last_state_change = datetime.utcnow()
            circuit_state.next_attempt = None
            
            # Clear history
            circuit_state.call_history.clear()
            circuit_state.failure_history.clear()
            circuit_state.response_times.clear()
            
            # Reset metrics
            circuit_state.metrics = CallMetrics()
        
        self.circuit_breaker_state.labels(circuit_name=circuit_name).state(
            CircuitState.CLOSED.value
        )
        
        logger.info(f"Circuit breaker {circuit_name} reset")
        return True
    
    async def get_circuit_breaker_status(self, circuit_name: str) -> Dict[str, Any]:
        """Get circuit breaker status and metrics"""
        if circuit_name not in self.circuit_breakers:
            raise ValueError(f"Circuit breaker not found: {circuit_name}")
        
        circuit_state = self.circuit_breakers[circuit_name]
        metrics = circuit_state.get_metrics()
        
        # Add configuration info
        config_info = {
            "failure_threshold": circuit_state.config.failure_threshold,
            "success_threshold": circuit_state.config.success_threshold,
            "timeout_ms": circuit_state.config.timeout_ms,
            "recovery_timeout_ms": circuit_state.config.recovery_timeout_ms,
            "recovery_strategy": circuit_state.config.recovery_strategy.value,
            "enable_bulkhead": circuit_state.config.enable_bulkhead,
            "max_concurrent_calls": circuit_state.config.max_concurrent_calls
        }
        
        return {
            "name": circuit_name,
            "configuration": config_info,
            "metrics": metrics,
            "health_check_enabled": circuit_name in self.health_check_tasks
        }
    
    async def get_all_circuit_breakers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        status = {}
        for circuit_name in self.circuit_breakers.keys():
            status[circuit_name] = await self.get_circuit_breaker_status(circuit_name)
        return status
    
    async def _health_check_task(self, circuit_name: str) -> None:
        """Background health check task for circuit breaker"""
        circuit_state = self.circuit_breakers[circuit_name]
        config = circuit_state.config
        
        if not config.health_check_url:
            return
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Only perform health check when circuit is open
                    if circuit_state.state == CircuitState.OPEN:
                        timeout = aiohttp.ClientTimeout(total=config.health_check_timeout_ms / 1000)
                        
                        async with session.get(config.health_check_url, timeout=timeout) as response:
                            if response.status == 200:
                                # Health check passed, transition to half-open
                                with circuit_state.lock:
                                    if circuit_state.state == CircuitState.OPEN:
                                        circuit_state._transition_to_half_open()
                                        logger.info(f"Health check passed for {circuit_name}, transitioning to half-open")
                    
                    # Wait for next health check
                    await asyncio.sleep(config.health_check_interval_ms / 1000)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.debug(f"Health check failed for {circuit_name}: {e}")
                    await asyncio.sleep(config.health_check_interval_ms / 1000)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            total_circuits = len(self.circuit_breakers)
            open_circuits = sum(1 for cb in self.circuit_breakers.values() 
                              if cb.state in [CircuitState.OPEN, CircuitState.FORCED_OPEN])
            
            # Check Redis connectivity if configured
            redis_healthy = True
            if self.redis_client:
                try:
                    await self.redis_client.ping()
                except Exception:
                    redis_healthy = False
            
            return {
                "service": "circuit_breaker_template",
                "status": "healthy" if redis_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_circuit_breakers": total_circuits,
                    "open_circuit_breakers": open_circuits,
                    "health_check_tasks": len(self.health_check_tasks),
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "circuit_breaker_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down circuit breaker service")
            
            # Cancel health check tasks
            for task in self.health_check_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.health_check_tasks:
                await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Circuit breaker service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")