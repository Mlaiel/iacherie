"""Circuit Breaker Protection Module

Advanced circuit breaker patterns with intelligent failure detection and recovery
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Circuit Breaker Protection architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from collections import defaultdict, deque
import statistics

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Blocking requests
    HALF_OPEN = "half_open" # Testing recovery


class FailureType(Enum):
    """Types of failures detected"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    SLOW_RESPONSE = "slow_response"
    HIGH_ERROR_RATE = "high_error_rate"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"


class RecoveryStrategy(Enum):
    """Recovery strategies for circuit breakers"""
    TIME_BASED = "time_based"
    GRADUAL = "gradual"
    LOAD_BASED = "load_based"
    HEALTH_CHECK = "health_check"
    ADAPTIVE = "adaptive"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    breaker_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    service_name: str = ""
    
    # Failure detection
    failure_threshold: int = 5
    failure_rate_threshold: float = 0.5  # 50%
    slow_call_threshold: float = 2.0     # 2 seconds
    slow_call_rate_threshold: float = 0.5  # 50%
    
    # Time windows
    sliding_window_size: int = 100       # requests
    minimum_requests: int = 10           # minimum calls before evaluation
    
    # Recovery settings
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.TIME_BASED
    wait_duration_seconds: float = 60.0
    permitted_calls_in_half_open: int = 3
    max_wait_duration_seconds: float = 300.0
    
    # Health check settings
    health_check_interval: float = 30.0
    health_check_timeout: float = 5.0
    
    # Business context
    critical_service: bool = False
    auto_recovery_enabled: bool = True
    notifications_enabled: bool = True
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class CircuitBreakerState:
    """Current state of a circuit breaker"""
    breaker_id: str
    current_state: CircuitState = CircuitState.CLOSED
    
    # Failure tracking
    failure_count: int = 0
    success_count: int = 0
    total_calls: int = 0
    
    # Call tracking (sliding window)
    call_results: deque = field(default_factory=lambda: deque(maxlen=100))
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # State transitions
    last_state_change: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_change_reason: str = ""
    
    # Half-open state tracking
    half_open_calls: int = 0
    half_open_successes: int = 0
    
    # Recovery tracking
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    
    # Health check
    last_health_check: Optional[datetime] = None
    health_check_status: bool = True
    
    # Metrics
    total_blocked_calls: int = 0
    total_successful_calls: int = 0
    total_failed_calls: int = 0


@dataclass
class CallResult:
    """Result of a protected call"""
    call_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = False
    duration_ms: float = 0.0
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    blocked: bool = False


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker system metrics"""
    total_breakers: int = 0
    breakers_closed: int = 0
    breakers_open: int = 0
    breakers_half_open: int = 0
    total_protected_calls: int = 0
    total_blocked_calls: int = 0
    total_successful_calls: int = 0
    total_failed_calls: int = 0
    avg_response_time: float = 0.0


class AinflueBusiness:
    """Ainflue Business Circuit Breaker Configuration"""
    
    # Circuit breaker configurations by service
    CIRCUIT_BREAKER_CONFIGS = {
        # Payment processing (most critical)
        "payment_gateway": CircuitBreakerConfig(
            breaker_id="payment_gateway_cb",
            name="Payment Gateway Circuit Breaker",
            service_name="payment_gateway",
            failure_threshold=3,
            failure_rate_threshold=0.3,  # 30%
            slow_call_threshold=5.0,     # 5 seconds
            wait_duration_seconds=30.0,
            recovery_strategy=RecoveryStrategy.HEALTH_CHECK,
            critical_service=True,
            health_check_interval=15.0
        ),
        
        # AI processing services
        "ai_content_analysis": CircuitBreakerConfig(
            breaker_id="ai_analysis_cb",
            name="AI Content Analysis Circuit Breaker",
            service_name="ai_content_analysis",
            failure_threshold=5,
            failure_rate_threshold=0.4,  # 40%
            slow_call_threshold=30.0,    # 30 seconds
            wait_duration_seconds=60.0,
            recovery_strategy=RecoveryStrategy.GRADUAL,
            critical_service=False,
            health_check_interval=45.0
        ),
        
        "ai_generation": CircuitBreakerConfig(
            breaker_id="ai_generation_cb",
            name="AI Generation Circuit Breaker",
            service_name="ai_generation",
            failure_threshold=8,
            failure_rate_threshold=0.5,  # 50%
            slow_call_threshold=60.0,    # 60 seconds
            wait_duration_seconds=120.0,
            recovery_strategy=RecoveryStrategy.ADAPTIVE,
            critical_service=False
        ),
        
        # Content processing services
        "content_upload": CircuitBreakerConfig(
            breaker_id="content_upload_cb",
            name="Content Upload Circuit Breaker",
            service_name="content_upload",
            failure_threshold=10,
            failure_rate_threshold=0.4,  # 40%
            slow_call_threshold=15.0,    # 15 seconds
            wait_duration_seconds=45.0,
            recovery_strategy=RecoveryStrategy.TIME_BASED,
            critical_service=True
        ),
        
        "content_storage": CircuitBreakerConfig(
            breaker_id="content_storage_cb",
            name="Content Storage Circuit Breaker", 
            service_name="content_storage",
            failure_threshold=15,
            failure_rate_threshold=0.6,  # 60%
            slow_call_threshold=10.0,    # 10 seconds
            wait_duration_seconds=30.0,
            recovery_strategy=RecoveryStrategy.LOAD_BASED,
            critical_service=True
        ),
        
        # External API services
        "external_social_api": CircuitBreakerConfig(
            breaker_id="social_api_cb",
            name="Social Media API Circuit Breaker",
            service_name="external_social_api",
            failure_threshold=20,
            failure_rate_threshold=0.7,  # 70%
            slow_call_threshold=5.0,     # 5 seconds
            wait_duration_seconds=180.0,
            recovery_strategy=RecoveryStrategy.TIME_BASED,
            critical_service=False
        ),
        
        # Database services
        "database_primary": CircuitBreakerConfig(
            breaker_id="db_primary_cb",
            name="Primary Database Circuit Breaker",
            service_name="database_primary",
            failure_threshold=3,
            failure_rate_threshold=0.2,  # 20%
            slow_call_threshold=2.0,     # 2 seconds
            wait_duration_seconds=15.0,
            recovery_strategy=RecoveryStrategy.HEALTH_CHECK,
            critical_service=True,
            health_check_interval=10.0
        ),
        
        # Analytics services
        "analytics_processor": CircuitBreakerConfig(
            breaker_id="analytics_cb",
            name="Analytics Processor Circuit Breaker",
            service_name="analytics_processor",
            failure_threshold=25,
            failure_rate_threshold=0.8,  # 80%
            slow_call_threshold=20.0,    # 20 seconds
            wait_duration_seconds=240.0,
            recovery_strategy=RecoveryStrategy.GRADUAL,
            critical_service=False
        )
    }
    
    # Failure classification rules
    FAILURE_CLASSIFICATION = {
        "timeout_errors": [
            "TimeoutError", "ConnectionTimeout", "ReadTimeout",
            "AsyncioTimeoutError", "RequestTimeout"
        ],
        "connection_errors": [
            "ConnectionError", "ConnectionRefused", "NetworkError",
            "SocketError", "DNSLookupError"
        ],
        "server_errors": [
            "HTTPError", "InternalServerError", "BadGateway",
            "ServiceUnavailable", "GatewayTimeout"
        ],
        "resource_errors": [
            "MemoryError", "OutOfMemoryError", "DiskSpaceError",
            "ResourceExhausted", "QuotaExceeded"
        ],
        "dependency_errors": [
            "DatabaseError", "RedisError", "ExternalServiceError",
            "UpstreamError", "DependencyFailure"
        ]
    }
    
    # Recovery configurations
    RECOVERY_CONFIGS = {
        RecoveryStrategy.TIME_BASED: {
            "base_wait_time": 60.0,
            "max_wait_time": 300.0,
            "backoff_multiplier": 2.0
        },
        RecoveryStrategy.GRADUAL: {
            "initial_test_calls": 1,
            "success_threshold": 3,
            "increment_rate": 2
        },
        RecoveryStrategy.LOAD_BASED: {
            "load_threshold": 0.7,
            "check_interval": 30.0
        },
        RecoveryStrategy.HEALTH_CHECK: {
            "check_interval": 30.0,
            "timeout": 5.0,
            "success_threshold": 2
        },
        RecoveryStrategy.ADAPTIVE: {
            "learning_window": 100,
            "adaptation_factor": 0.1
        }
    }
    
    # Notification settings
    NOTIFICATION_SETTINGS = {
        "critical_services": {
            "state_change": True,
            "failure_threshold": True,
            "recovery": True,
            "channels": ["email", "slack", "pagerduty"]
        },
        "standard_services": {
            "state_change": True,
            "failure_threshold": False,
            "recovery": True,
            "channels": ["email", "slack"]
        }
    }


class CircuitBreakerProtection:
    """
    Advanced circuit breaker patterns with intelligent failure detection and recovery
    Provides comprehensive protection for Ainflue business operations
    """
    
    def __init__(self,
                 metrics_collector -> None: Optional[MetricsCollector] = None,
                 encryption_manager -> None: Optional[EncryptionManager] = None) -> None:
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Circuit breaker management
        self.circuit_breakers = {}  # breaker_id -> CircuitBreakerConfig
        self.breaker_states = {}    # breaker_id -> CircuitBreakerState
        self.health_check_functions = {}  # service_name -> health_check_function
        
        # Monitoring tasks
        self.monitoring_tasks = {}  # breaker_id -> asyncio.Task
        self.recovery_tasks = {}    # breaker_id -> asyncio.Task
        
        # Global metrics
        self.global_metrics = CircuitBreakerMetrics()
        
        # Notification callbacks
        self.notification_callbacks = {}  # event_type -> List[callback]
        
        # Adaptive learning
        self.failure_patterns = defaultdict(list)
        self.recovery_patterns = defaultdict(list)
        
        logger.info("Initialized Circuit Breaker Protection")
    
    async def start(self) -> bool:
        """Start the circuit breaker protection system"""
        try:
            # Load business circuit breaker configurations
            await self._load_business_configurations()
            
            # Start monitoring tasks
            await self._start_monitoring_tasks()
            
            logger.info("Circuit Breaker Protection started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start circuit breaker protection: {str(e)}")
            raise MessageQueueError(f"Circuit breaker startup failed: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the circuit breaker protection system"""
        try:
            # Stop all monitoring tasks
            for task in self.monitoring_tasks.values():
                task.cancel()
            
            for task in self.recovery_tasks.values():
                task.cancel()
            
            logger.info("Circuit Breaker Protection stopped")
            
        except Exception as e:
            logger.error(f"Error stopping circuit breaker protection: {str(e)}")
    
    async def execute_protected_call(self,
                                   breaker_id: str,
                                   operation: Callable,
                                   *args,
                                   timeout: Optional[float] = None,
                                   **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Execute a protected call through circuit breaker"""
        try:
            # Check if circuit breaker allows the call
            allowed = await self._check_call_allowed(breaker_id)
            
            if not allowed:
                # Call blocked by circuit breaker
                await self._record_blocked_call(breaker_id)
                return False, None, "circuit_breaker_open"
            
            # Execute the protected call
            start_time = time.time()
            success = False
            result = None
            error_message = None
            failure_type = None
            
            try:
                # Execute with timeout if specified
                if timeout:
                    result = await asyncio.wait_for(operation(*args, **kwargs), timeout=timeout)
                else:
                    result = await operation(*args, **kwargs)
                
                success = True
                
            except asyncio.TimeoutError:
                failure_type = FailureType.TIMEOUT
                error_message = "Operation timed out"
                
            except Exception as e:
                failure_type = await self._classify_failure(str(e))
                error_message = str(e)
            
            # Record call result
            duration_ms = (time.time() - start_time) * 1000
            call_result = CallResult(
                success=success,
                duration_ms=duration_ms,
                failure_type=failure_type,
                error_message=error_message
            )
            
            await self._record_call_result(breaker_id, call_result)
            
            return success, result, error_message
            
        except Exception as e:
            logger.error(f"Error in protected call execution: {str(e)}")
            return False, None, str(e)
    
    async def register_circuit_breaker(self, config: CircuitBreakerConfig) -> str:
        """Register a new circuit breaker"""
        try:
            self.circuit_breakers[config.breaker_id] = config
            
            # Initialize state
            state = CircuitBreakerState(breaker_id=config.breaker_id)
            self.breaker_states[config.breaker_id] = state
            
            # Start monitoring if active
            if config.is_active:
                await self._start_breaker_monitoring(config.breaker_id)
            
            logger.info(f"Registered circuit breaker: {config.name}")
            return config.breaker_id
            
        except Exception as e:
            logger.error(f"Error registering circuit breaker: {str(e)}")
            raise MessageQueueError(f"Failed to register circuit breaker: {str(e)}")
    
    async def register_health_check(self, service_name: str, health_check_func: Callable) -> bool:
        """Register a health check function for a service"""
        try:
            self.health_check_functions[service_name] = health_check_func
            logger.info(f"Registered health check for service: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering health check: {str(e)}")
            return False
    
    async def get_circuit_breaker_status(self, breaker_id: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker status"""
        try:
            if breaker_id:
                # Specific circuit breaker status
                if breaker_id not in self.breaker_states:
                    return {"error": "Circuit breaker not found"}
                
                config = self.circuit_breakers[breaker_id]
                state = self.breaker_states[breaker_id]
                
                # Calculate metrics
                failure_rate = 0.0
                if state.total_calls > 0:
                    failure_rate = (state.total_failed_calls / state.total_calls) * 100
                
                slow_call_rate = 0.0
                if state.response_times:
                    slow_calls = sum(1 for t in state.response_times if t > config.slow_call_threshold * 1000)
                    slow_call_rate = (slow_calls / len(state.response_times)) * 100
                
                return {
                    "breaker_id": breaker_id,
                    "name": config.name,
                    "service_name": config.service_name,
                    "current_state": state.current_state.value,
                    "failure_count": state.failure_count,
                    "success_count": state.success_count,
                    "total_calls": state.total_calls,
                    "failure_rate": round(failure_rate, 2),
                    "slow_call_rate": round(slow_call_rate, 2),
                    "consecutive_failures": state.consecutive_failures,
                    "last_state_change": state.last_state_change.isoformat(),
                    "state_change_reason": state.state_change_reason,
                    "last_failure": state.last_failure_time.isoformat() if state.last_failure_time else None,
                    "last_success": state.last_success_time.isoformat() if state.last_success_time else None,
                    "total_blocked_calls": state.total_blocked_calls,
                    "is_critical": config.critical_service
                }
            else:
                # All circuit breakers status
                all_status = {}
                for breaker_id in self.circuit_breakers.keys():
                    status = await self.get_circuit_breaker_status(breaker_id)
                    if "error" not in status:
                        all_status[breaker_id] = status
                
                return {"circuit_breakers": all_status}
                
        except Exception as e:
            logger.error(f"Error getting circuit breaker status: {str(e)}")
            return {"error": str(e)}
    
    async def get_protection_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker protection metrics"""
        try:
            # Update global metrics
            await self._update_global_metrics()
            
            # Calculate state distribution
            state_distribution = defaultdict(int)
            for state in self.breaker_states.values():
                state_distribution[state.current_state.value] += 1
            
            # Calculate protection effectiveness
            total_calls = self.global_metrics.total_protected_calls
            protection_rate = 0.0
            if total_calls > 0:
                protection_rate = (self.global_metrics.total_blocked_calls / total_calls) * 100
            
            success_rate = 0.0
            if total_calls > 0:
                success_rate = (self.global_metrics.total_successful_calls / total_calls) * 100
            
            return {
                "global_metrics": {
                    "total_breakers": self.global_metrics.total_breakers,
                    "total_protected_calls": total_calls,
                    "total_blocked_calls": self.global_metrics.total_blocked_calls,
                    "total_successful_calls": self.global_metrics.total_successful_calls,
                    "total_failed_calls": self.global_metrics.total_failed_calls,
                    "protection_rate": round(protection_rate, 2),
                    "success_rate": round(success_rate, 2),
                    "avg_response_time": round(self.global_metrics.avg_response_time, 3)
                },
                "state_distribution": dict(state_distribution),
                "critical_services": {
                    breaker_id: state.current_state.value
                    for breaker_id, config in self.circuit_breakers.items()
                    if config.critical_service
                    for state in [self.breaker_states[breaker_id]]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting protection metrics: {str(e)}")
            return {"error": str(e)}
    
    async def force_circuit_breaker_state(self, breaker_id: str, new_state: CircuitState, reason: str = "") -> bool:
        """Force circuit breaker to specific state (for testing/maintenance)"""
        try:
            if breaker_id not in self.breaker_states:
                return False
            
            old_state = self.breaker_states[breaker_id].current_state
            await self._transition_circuit_breaker(breaker_id, new_state, reason or "manual_override")
            
            logger.info(f"Manually transitioned circuit breaker {breaker_id} from {old_state.value} to {new_state.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error forcing circuit breaker state: {str(e)}")
            return False
    
    async def reset_circuit_breaker(self, breaker_id: str) -> bool:
        """Reset circuit breaker to initial state"""
        try:
            if breaker_id not in self.breaker_states:
                return False
            
            state = self.breaker_states[breaker_id]
            
            # Reset state
            state.current_state = CircuitState.CLOSED
            state.failure_count = 0
            state.success_count = 0
            state.consecutive_failures = 0
            state.consecutive_successes = 0
            state.half_open_calls = 0
            state.half_open_successes = 0
            state.call_results.clear()
            state.response_times.clear()
            state.state_change_reason = "manual_reset"
            state.last_state_change = datetime.now(timezone.utc)
            
            logger.info(f"Reset circuit breaker: {breaker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting circuit breaker: {str(e)}")
            return False
    
    # Core circuit breaker logic
    
    async def _check_call_allowed(self, breaker_id: str) -> bool:
        """Check if call is allowed by circuit breaker"""
        if breaker_id not in self.breaker_states:
            return True  # No circuit breaker = allow
        
        state = self.breaker_states[breaker_id]
        config = self.circuit_breakers[breaker_id]
        
        if state.current_state == CircuitState.CLOSED:
            return True
        
        elif state.current_state == CircuitState.OPEN:
            # Check if enough time has passed to try half-open
            current_time = datetime.now(timezone.utc)
            time_since_open = (current_time - state.last_state_change).total_seconds()
            
            if time_since_open >= config.wait_duration_seconds:
                await self._transition_circuit_breaker(breaker_id, CircuitState.HALF_OPEN, "timeout_recovery")
                return True
            
            return False
        
        elif state.current_state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open state
            return state.half_open_calls < config.permitted_calls_in_half_open
        
        return False
    
    async def _record_call_result(self, breaker_id -> None: str, call_result -> None: CallResult) -> None:
        """Record the result of a protected call"""
        if breaker_id not in self.breaker_states:
            return
        
        state = self.breaker_states[breaker_id]
        config = self.circuit_breakers[breaker_id]
        
        # Update state counters
        state.total_calls += 1
        
        if call_result.success:
            state.success_count += 1
            state.consecutive_successes += 1
            state.consecutive_failures = 0
            state.last_success_time = call_result.timestamp
            state.total_successful_calls += 1
            
            # Handle half-open state
            if state.current_state == CircuitState.HALF_OPEN:
                state.half_open_successes += 1
                
                # Check if we should close the circuit
                if state.half_open_successes >= config.permitted_calls_in_half_open:
                    await self._transition_circuit_breaker(breaker_id, CircuitState.CLOSED, "recovery_successful")
        else:
            state.failure_count += 1
            state.consecutive_failures += 1
            state.consecutive_successes = 0
            state.last_failure_time = call_result.timestamp
            state.total_failed_calls += 1
            
            # Handle half-open state
            if state.current_state == CircuitState.HALF_OPEN:
                await self._transition_circuit_breaker(breaker_id, CircuitState.OPEN, "half_open_failure")
        
        # Update sliding window
        state.call_results.append(call_result)
        state.response_times.append(call_result.duration_ms)
        
        # Handle half-open call tracking
        if state.current_state == CircuitState.HALF_OPEN:
            state.half_open_calls += 1
        
        # Check if circuit should be opened (only if currently closed)
        if state.current_state == CircuitState.CLOSED:
            await self._evaluate_circuit_opening(breaker_id)
        
        # Update global metrics
        self.global_metrics.total_protected_calls += 1
        if call_result.success:
            self.global_metrics.total_successful_calls += 1
        else:
            self.global_metrics.total_failed_calls += 1
    
    async def _record_blocked_call(self, breaker_id -> None: str) -> None:
        """Record a call that was blocked by circuit breaker"""
        if breaker_id in self.breaker_states:
            self.breaker_states[breaker_id].total_blocked_calls += 1
        
        self.global_metrics.total_blocked_calls += 1
    
    async def _evaluate_circuit_opening(self, breaker_id -> None: str) -> None:
        """Evaluate whether circuit should be opened"""
        state = self.breaker_states[breaker_id]
        config = self.circuit_breakers[breaker_id]
        
        # Need minimum number of calls for evaluation
        if len(state.call_results) < config.minimum_requests:
            return
        
        recent_calls = list(state.call_results)
        
        # Check failure count threshold
        recent_failures = sum(1 for call in recent_calls if not call.success)
        if recent_failures >= config.failure_threshold:
            await self._transition_circuit_breaker(breaker_id, CircuitState.OPEN, f"failure_threshold_exceeded_{recent_failures}")
            return
        
        # Check failure rate threshold
        failure_rate = recent_failures / len(recent_calls)
        if failure_rate >= config.failure_rate_threshold:
            await self._transition_circuit_breaker(breaker_id, CircuitState.OPEN, f"failure_rate_exceeded_{failure_rate:.2f}")
            return
        
        # Check slow call rate threshold
        slow_calls = sum(1 for call in recent_calls if call.duration_ms > config.slow_call_threshold * 1000)
        slow_call_rate = slow_calls / len(recent_calls)
        if slow_call_rate >= config.slow_call_rate_threshold:
            await self._transition_circuit_breaker(breaker_id, CircuitState.OPEN, f"slow_call_rate_exceeded_{slow_call_rate:.2f}")
            return
    
    async def _transition_circuit_breaker(self, breaker_id -> None: str, new_state -> None: CircuitState, reason -> None: str) -> None:
        """Transition circuit breaker to new state"""
        if breaker_id not in self.breaker_states:
            return
        
        state = self.breaker_states[breaker_id]
        config = self.circuit_breakers[breaker_id]
        old_state = state.current_state
        
        if old_state == new_state:
            return  # No change
        
        # Update state
        state.current_state = new_state
        state.last_state_change = datetime.now(timezone.utc)
        state.state_change_reason = reason
        
        # Reset half-open tracking when entering half-open
        if new_state == CircuitState.HALF_OPEN:
            state.half_open_calls = 0
            state.half_open_successes = 0
        
        # Start recovery task if opening
        if new_state == CircuitState.OPEN:
            await self._start_recovery_task(breaker_id)
        
        # Stop recovery task if closing
        elif new_state == CircuitState.CLOSED and breaker_id in self.recovery_tasks:
            self.recovery_tasks[breaker_id].cancel()
            del self.recovery_tasks[breaker_id]
        
        logger.info(f"Circuit breaker {config.name} transitioned from {old_state.value} to {new_state.value}: {reason}")
        
        # Send notifications
        await self._send_state_change_notification(breaker_id, old_state, new_state, reason)
    
    # Helper methods
    
    async def _load_business_configurations(self) -> None:
        """Load Ainflue business circuit breaker configurations"""
        for service_name, config in AinflueBusiness.CIRCUIT_BREAKER_CONFIGS.items():
            await self.register_circuit_breaker(config)
        
        logger.info(f"Loaded {len(AinflueBusiness.CIRCUIT_BREAKER_CONFIGS)} business circuit breaker configurations")
    
    async def _classify_failure(self, error_message: str) -> FailureType:
        """Classify failure type based on error message"""
        error_lower = error_message.lower()
        
        # Check timeout errors
        for timeout_error in AinflueBusiness.FAILURE_CLASSIFICATION["timeout_errors"]:
            if timeout_error.lower() in error_lower:
                return FailureType.TIMEOUT
        
        # Check connection errors
        for conn_error in AinflueBusiness.FAILURE_CLASSIFICATION["connection_errors"]:
            if conn_error.lower() in error_lower:
                return FailureType.DEPENDENCY_FAILURE
        
        # Check server errors
        for server_error in AinflueBusiness.FAILURE_CLASSIFICATION["server_errors"]:
            if server_error.lower() in error_lower:
                return FailureType.HIGH_ERROR_RATE
        
        # Check resource errors
        for resource_error in AinflueBusiness.FAILURE_CLASSIFICATION["resource_errors"]:
            if resource_error.lower() in error_lower:
                return FailureType.RESOURCE_EXHAUSTION
        
        # Check dependency errors
        for dep_error in AinflueBusiness.FAILURE_CLASSIFICATION["dependency_errors"]:
            if dep_error.lower() in error_lower:
                return FailureType.DEPENDENCY_FAILURE
        
        # Default to exception
        return FailureType.EXCEPTION
    
    async def _start_monitoring_tasks(self) -> None:
        """Start monitoring tasks for all circuit breakers"""
        for breaker_id in self.circuit_breakers.keys():
            await self._start_breaker_monitoring(breaker_id)
    
    async def _start_breaker_monitoring(self, breaker_id -> None: str) -> None:
        """Start monitoring task for a circuit breaker"""
        if breaker_id in self.monitoring_tasks:
            return  # Already monitoring
        
        task = asyncio.create_task(self._monitoring_loop(breaker_id))
        self.monitoring_tasks[breaker_id] = task
    
    async def _monitoring_loop(self, breaker_id -> None: str) -> None:
        """Monitoring loop for a circuit breaker"""
        config = self.circuit_breakers[breaker_id]
        
        while breaker_id in self.circuit_breakers:
            try:
                # Perform health check if applicable
                if config.service_name in self.health_check_functions:
                    await self._perform_health_check(breaker_id)
                
                # Clean old call results
                await self._cleanup_old_call_results(breaker_id)
                
                await asyncio.sleep(config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop for {breaker_id}: {str(e)}")
                await asyncio.sleep(60)  # Back off on error
    
    async def _perform_health_check(self, breaker_id -> None: str) -> None:
        """Perform health check for circuit breaker service"""
        config = self.circuit_breakers[breaker_id]
        state = self.breaker_states[breaker_id]
        
        if config.service_name not in self.health_check_functions:
            return
        
        health_check_func = self.health_check_functions[config.service_name]
        
        try:
            # Perform health check with timeout
            health_status = await asyncio.wait_for(
                health_check_func(),
                timeout=config.health_check_timeout
            )
            
            state.health_check_status = health_status
            state.last_health_check = datetime.now(timezone.utc)
            
            # If circuit is open and health check passes, consider recovery
            if (state.current_state == CircuitState.OPEN and 
                health_status and 
                config.recovery_strategy == RecoveryStrategy.HEALTH_CHECK):
                
                await self._transition_circuit_breaker(breaker_id, CircuitState.HALF_OPEN, "health_check_recovery")
            
        except Exception as e:
            logger.warning(f"Health check failed for {config.service_name}: {str(e)}")
            state.health_check_status = False
    
    async def _start_recovery_task(self, breaker_id -> None: str) -> None:
        """Start recovery task for opened circuit breaker"""
        if breaker_id in self.recovery_tasks:
            return  # Already has recovery task
        
        task = asyncio.create_task(self._recovery_loop(breaker_id))
        self.recovery_tasks[breaker_id] = task
    
    async def _recovery_loop(self, breaker_id -> None: str) -> None:
        """Recovery loop for opened circuit breaker"""
        config = self.circuit_breakers[breaker_id]
        state = self.breaker_states[breaker_id]
        
        recovery_config = AinflueBusiness.RECOVERY_CONFIGS.get(config.recovery_strategy, {})
        
        while state.current_state == CircuitState.OPEN:
            try:
                if config.recovery_strategy == RecoveryStrategy.TIME_BASED:
                    # Simple time-based recovery (handled in _check_call_allowed)
                    await asyncio.sleep(config.wait_duration_seconds)
                
                elif config.recovery_strategy == RecoveryStrategy.LOAD_BASED:
                    # Check system load before allowing recovery
                    system_load = await self._get_system_load()
                    load_threshold = recovery_config.get("load_threshold", 0.7)
                    
                    if system_load < load_threshold:
                        await self._transition_circuit_breaker(breaker_id, CircuitState.HALF_OPEN, "load_based_recovery")
                    
                    await asyncio.sleep(recovery_config.get("check_interval", 30.0))
                
                elif config.recovery_strategy == RecoveryStrategy.ADAPTIVE:
                    # Adaptive recovery based on historical patterns
                    wait_time = await self._calculate_adaptive_wait_time(breaker_id)
                    await asyncio.sleep(wait_time)
                    
                    await self._transition_circuit_breaker(breaker_id, CircuitState.HALF_OPEN, "adaptive_recovery")
                
                else:
                    # Default to time-based
                    await asyncio.sleep(config.wait_duration_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in recovery loop for {breaker_id}: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_call_results(self, breaker_id -> None: str) -> None:
        """Clean up old call results to prevent memory growth"""
        state = self.breaker_states[breaker_id]
        
        # Results are automatically cleaned by deque maxlen
        # But we can add additional cleanup logic here if needed
        
        # Clean results older than 1 hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        
        while (state.call_results and 
               state.call_results[0].timestamp < one_hour_ago):
            state.call_results.popleft()
    
    async def _update_global_metrics(self) -> None:
        """Update global circuit breaker metrics"""
        self.global_metrics.total_breakers = len(self.circuit_breakers)
        
        # Count breakers by state
        self.global_metrics.breakers_closed = 0
        self.global_metrics.breakers_open = 0
        self.global_metrics.breakers_half_open = 0
        
        total_response_time = 0
        total_responses = 0
        
        for state in self.breaker_states.values():
            if state.current_state == CircuitState.CLOSED:
                self.global_metrics.breakers_closed += 1
            elif state.current_state == CircuitState.OPEN:
                self.global_metrics.breakers_open += 1
            elif state.current_state == CircuitState.HALF_OPEN:
                self.global_metrics.breakers_half_open += 1
            
            # Aggregate response times
            if state.response_times:
                total_response_time += sum(state.response_times)
                total_responses += len(state.response_times)
        
        # Calculate average response time
        if total_responses > 0:
            self.global_metrics.avg_response_time = total_response_time / total_responses
    
    async def _send_state_change_notification(self, 
                                            breaker_id -> None: str,
                                            old_state -> None: CircuitState,
                                            new_state -> None: CircuitState,
                                            reason -> None: str) -> None:
        """Send notification for circuit breaker state change"""
        config = self.circuit_breakers[breaker_id]
        
        if not config.notifications_enabled:
            return
        
        # Determine notification settings
        if config.critical_service:
            notification_config = AinflueBusiness.NOTIFICATION_SETTINGS["critical_services"]
        else:
            notification_config = AinflueBusiness.NOTIFICATION_SETTINGS["standard_services"]
        
        if not notification_config.get("state_change", False):
            return
        
        # Create notification message
        message = {
            "event_type": "circuit_breaker_state_change",
            "breaker_id": breaker_id,
            "service_name": config.service_name,
            "old_state": old_state.value,
            "new_state": new_state.value,
            "reason": reason,
            "critical_service": config.critical_service,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send to notification callbacks
        callbacks = self.notification_callbacks.get("state_change", [])
        for callback in callbacks:
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Error sending notification: {str(e)}")
    
    async def _get_system_load(self) -> float:
        """Get current system load (simplified)"""
        # In a real implementation, this would check:
        # - CPU usage
        # - Memory usage
        # - Network load
        # - Queue depths
        # For now, return a mock value
        return 0.5  # 50% load
    
    async def _calculate_adaptive_wait_time(self, breaker_id: str) -> float:
        """Calculate adaptive wait time based on historical patterns"""
        config = self.circuit_breakers[breaker_id]
        
        # Use historical recovery patterns to adjust wait time
        base_wait = config.wait_duration_seconds
        
        # Simple adaptive logic - could be more sophisticated
        failure_patterns = self.failure_patterns.get(breaker_id, [])
        
        if len(failure_patterns) > 5:
            # Increase wait time if frequent failures
            recent_failures = sum(1 for f in failure_patterns[-10:] if f)
            if recent_failures > 7:
                return min(base_wait * 2, config.max_wait_duration_seconds)
            elif recent_failures < 3:
                return max(base_wait * 0.5, 10.0)
        
        return base_wait
    
    def register_notification_callback(self, event_type -> None: str, callback -> None: Callable) -> None:
        """Register notification callback for circuit breaker events"""
        if event_type not in self.notification_callbacks:
            self.notification_callbacks[event_type] = []
        
        self.notification_callbacks[event_type].append(callback)
        logger.info(f"Registered notification callback for {event_type}")


# Export for public API
__all__ = [
    "CircuitBreakerProtection",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CallResult",
    "CircuitBreakerMetrics",
    "CircuitState",
    "FailureType",
    "RecoveryStrategy",
    "AinflueBusiness"
]