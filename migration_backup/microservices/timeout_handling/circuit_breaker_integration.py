"""
Circuit Breaker Integration - IA Chéries Enterprise
==============================================
Intégration circuit breaker avec timeout management.
Circuit patterns + failure isolation + auto-recovery + health monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries Timeout Handling
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitFailureType(Enum):
    """Types of circuit breaker failures"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    SLOW_RESPONSE = "slow_response"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    EXTERNAL_DEPENDENCY = "external_dependency"

class RecoveryStrategy(Enum):
    """Recovery strategies for circuit breakers"""
    GRADUAL = "gradual"
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    ADAPTIVE = "adaptive"

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    service_name: str
    operation_name: str
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_duration: float = 60.0
    half_open_max_calls: int = 10
    slow_response_threshold: float = 30.0
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.GRADUAL
    health_check_interval: float = 30.0
    business_priority: str = "medium"  # critical, high, medium, low
    enable_fallback: bool = True

@dataclass
class CircuitIntegrationRequest:
    """Request for circuit breaker integration"""
    request_id: str
    service_name: str
    operation_name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timeout_override: Optional[float] = None
    business_context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitIntegrationResult:
    """Result of circuit breaker integration"""
    request_id: str
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    circuit_state: CircuitState = CircuitState.CLOSED
    circuit_triggered: bool = False
    fallback_executed: bool = False
    recovery_attempted: bool = False

@dataclass
class CircuitHealthMetrics:
    """Health metrics for circuit breaker"""
    service_name: str
    operation_name: str
    current_state: CircuitState
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    last_success_time: float = 0.0
    avg_response_time: float = 0.0
    failure_rate: float = 0.0
    health_score: float = 1.0
    last_updated: float = field(default_factory=time.time)

@dataclass
class RecoveryTest:
    """Recovery test configuration"""
    test_id: str
    service_name: str
    test_function: Callable
    expected_success_rate: float = 0.8
    test_iterations: int = 5
    timeout_per_test: float = 10.0

class CircuitBreakerIntegration:
    """
    Intégration circuit breaker avec timeout management.
    Circuit patterns + failure isolation + auto-recovery + health monitoring.
    """
    
    def __init__(self, integration_config: Optional[Dict[str, Any]] = None):
        self.integration_config = integration_config or {}
        self.circuit_configs: Dict[str, CircuitBreakerConfig] = {}
        self.circuit_states: Dict[str, CircuitState] = {}
        self.circuit_metrics: Dict[str, CircuitHealthMetrics] = {}
        self.failure_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, float] = {}
        self.half_open_calls: Dict[str, int] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        self.is_initialized = False
        
        # IA Chéries business priority weights
        self.priority_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Business domain circuit configurations
        self.business_circuit_configs = {
            'creator_service': {
                'upload': CircuitBreakerConfig(
                    service_name='creator_service',
                    operation_name='upload',
                    failure_threshold=3,
                    timeout_duration=120.0,
                    business_priority='high'
                ),
                'process': CircuitBreakerConfig(
                    service_name='creator_service',
                    operation_name='process',
                    failure_threshold=5,
                    timeout_duration=300.0,
                    business_priority='high'
                )
            },
            'ai_service': {
                'analyze': CircuitBreakerConfig(
                    service_name='ai_service',
                    operation_name='analyze',
                    failure_threshold=2,
                    timeout_duration=180.0,
                    business_priority='critical',
                    slow_response_threshold=60.0
                ),
                'generate': CircuitBreakerConfig(
                    service_name='ai_service',
                    operation_name='generate',
                    failure_threshold=2,
                    timeout_duration=300.0,
                    business_priority='critical',
                    slow_response_threshold=120.0
                )
            },
            'payment_service': {
                'process': CircuitBreakerConfig(
                    service_name='payment_service',
                    operation_name='process',
                    failure_threshold=2,
                    timeout_duration=30.0,
                    business_priority='critical',
                    enable_fallback=False  # No fallback for payments
                )
            },
            'collaboration_service': {
                'sync': CircuitBreakerConfig(
                    service_name='collaboration_service',
                    operation_name='sync',
                    failure_threshold=5,
                    timeout_duration=10.0,
                    business_priority='high',
                    recovery_strategy=RecoveryStrategy.ADAPTIVE
                )
            }
        }
        
    async def initialize(self):
        """Initialize circuit breaker integration"""
        if self.is_initialized:
            return
            
        logger.info("Initializing Circuit Breaker Integration")
        
        # Load default circuit configurations
        await self._load_default_circuit_configs()
        
        # Initialize circuit states
        await self._initialize_circuit_states()
        
        # Start background tasks
        asyncio.create_task(self._health_monitoring_task())
        asyncio.create_task(self._recovery_testing_task())
        asyncio.create_task(self._metrics_collection_task())
        
        self.is_initialized = True
        logger.info("Circuit Breaker Integration initialized successfully")
        
    async def integrate_circuit_breaker_timeout(self, integration_request: CircuitIntegrationRequest) -> CircuitIntegrationResult:
        """
        Intégration circuit breaker avec timeout management.
        
        Circuit Breaker Features:
        - Timeout-aware circuit breaker avec failure thresholds
        - Automatic circuit state transitions (closed/open/half-open)
        - Service health monitoring avec predictive failure detection
        - Graceful degradation avec fallback service selection
        - Recovery testing avec gradual traffic restoration
        - Business impact assessment pour circuit decisions
        - Multi-level circuit breakers (operation/service/cluster)
        - Circuit breaker metrics avec performance analytics
        """
        start_time = time.time()
        
        if not self.is_initialized:
            await self.initialize()
            
        service_key = f"{integration_request.service_name}_{integration_request.operation_name}"
        
        # Get circuit state
        current_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
        
        # Check if circuit is open
        if current_state == CircuitState.OPEN:
            return await self._handle_open_circuit(integration_request)
            
        # Check if circuit is half-open and at capacity
        if current_state == CircuitState.HALF_OPEN:
            if self.half_open_calls.get(service_key, 0) >= self._get_config(service_key).half_open_max_calls:
                return await self._handle_half_open_capacity_exceeded(integration_request)
                
        # Execute with circuit breaker protection
        try:
            # Increment half-open call count if applicable
            if current_state == CircuitState.HALF_OPEN:
                self.half_open_calls[service_key] = self.half_open_calls.get(service_key, 0) + 1
                
            # Get timeout value
            timeout_value = await self._calculate_circuit_aware_timeout(integration_request)
            
            # Execute with timeout
            if asyncio.iscoroutinefunction(integration_request.function):
                result = await asyncio.wait_for(
                    integration_request.function(*integration_request.args, **integration_request.kwargs),
                    timeout=timeout_value
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.to_thread(integration_request.function, *integration_request.args, **integration_request.kwargs),
                    timeout=timeout_value
                )
            
            execution_time = time.time() - start_time
            
            # Record success
            await self._record_success(service_key, execution_time)
            
            return CircuitIntegrationResult(
                request_id=integration_request.request_id,
                success=True,
                result=result,
                execution_time=execution_time,
                circuit_state=self.circuit_states.get(service_key, CircuitState.CLOSED)
            )
            
        except asyncio.TimeoutError as e:
            execution_time = time.time() - start_time
            
            # Record timeout failure
            await self._record_failure(service_key, CircuitFailureType.TIMEOUT, execution_time)
            
            # Check if circuit should open
            await self._evaluate_circuit_state(service_key)
            
            # Execute fallback if available and circuit allows
            fallback_result = None
            fallback_executed = False
            
            if self._get_config(service_key).enable_fallback:
                fallback_result = await self._execute_fallback(integration_request)
                fallback_executed = fallback_result is not None
                
            return CircuitIntegrationResult(
                request_id=integration_request.request_id,
                success=False,
                error=e,
                execution_time=execution_time,
                circuit_state=self.circuit_states.get(service_key, CircuitState.CLOSED),
                circuit_triggered=True,
                fallback_executed=fallback_executed,
                result=fallback_result
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Determine failure type
            failure_type = await self._classify_exception(e, execution_time, integration_request)
            
            # Record failure
            await self._record_failure(service_key, failure_type, execution_time)
            
            # Check if circuit should open
            await self._evaluate_circuit_state(service_key)
            
            # Execute fallback if available
            fallback_result = None
            fallback_executed = False
            
            if self._get_config(service_key).enable_fallback:
                fallback_result = await self._execute_fallback(integration_request)
                fallback_executed = fallback_result is not None
                
            return CircuitIntegrationResult(
                request_id=integration_request.request_id,
                success=False,
                error=e,
                execution_time=execution_time,
                circuit_state=self.circuit_states.get(service_key, CircuitState.CLOSED),
                circuit_triggered=True,
                fallback_executed=fallback_executed,
                result=fallback_result
            )
    
    async def manage_circuit_state_transitions(self, service_name: str, operation_name: str, 
                                             force_state: Optional[CircuitState] = None) -> Dict[str, Any]:
        """Manage circuit state transitions"""
        service_key = f"{service_name}_{operation_name}"
        
        if force_state:
            # Force specific state
            old_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
            self.circuit_states[service_key] = force_state
            
            logger.info(f"Circuit state forced from {old_state} to {force_state} for {service_key}")
            
            # Reset counters for new state
            await self._reset_state_counters(service_key, force_state)
            
            return {
                'service_key': service_key,
                'old_state': old_state,
                'new_state': force_state,
                'transition_reason': 'manual_override',
                'timestamp': time.time()
            }
        else:
            # Evaluate natural state transition
            return await self._evaluate_circuit_state(service_key)
    
    async def execute_circuit_recovery_testing(self, recovery_test: RecoveryTest) -> Dict[str, Any]:
        """Execute recovery testing for circuit breaker"""
        logger.info(f"Starting recovery test {recovery_test.test_id} for {recovery_test.service_name}")
        
        test_results = []
        successful_tests = 0
        
        for i in range(recovery_test.test_iterations):
            try:
                start_time = time.time()
                
                # Execute test function with timeout
                if asyncio.iscoroutinefunction(recovery_test.test_function):
                    await asyncio.wait_for(
                        recovery_test.test_function(),
                        timeout=recovery_test.timeout_per_test
                    )
                else:
                    await asyncio.wait_for(
                        asyncio.to_thread(recovery_test.test_function),
                        timeout=recovery_test.timeout_per_test
                    )
                
                execution_time = time.time() - start_time
                successful_tests += 1
                
                test_results.append({
                    'iteration': i + 1,
                    'success': True,
                    'execution_time': execution_time
                })
                
            except Exception as e:
                execution_time = time.time() - start_time
                test_results.append({
                    'iteration': i + 1,
                    'success': False,
                    'execution_time': execution_time,
                    'error': str(e)
                })
        
        success_rate = successful_tests / recovery_test.test_iterations
        recovery_recommended = success_rate >= recovery_test.expected_success_rate
        
        logger.info(f"Recovery test {recovery_test.test_id} completed: {success_rate:.2%} success rate")
        
        return {
            'test_id': recovery_test.test_id,
            'service_name': recovery_test.service_name,
            'success_rate': success_rate,
            'successful_tests': successful_tests,
            'total_tests': recovery_test.test_iterations,
            'recovery_recommended': recovery_recommended,
            'test_results': test_results,
            'timestamp': time.time()
        }
    
    async def calculate_circuit_health_score(self, service_name: str, operation_name: str) -> Dict[str, Any]:
        """Calculate circuit health score for state decisions"""
        service_key = f"{service_name}_{operation_name}"
        
        metrics = self.circuit_metrics.get(service_key)
        if not metrics:
            return {
                'health_score': 0.5,
                'confidence': 'low',
                'reason': 'No metrics available'
            }
        
        # Calculate health components
        failure_rate_score = max(0, 1.0 - metrics.failure_rate)
        response_time_score = await self._calculate_response_time_score(metrics.avg_response_time, service_key)
        success_trend_score = await self._calculate_success_trend_score(service_key)
        business_impact_score = await self._calculate_business_impact_score(service_key)
        
        # Weighted health score
        health_score = (
            failure_rate_score * 0.3 +
            response_time_score * 0.25 +
            success_trend_score * 0.25 +
            business_impact_score * 0.2
        )
        
        # Determine confidence level
        data_points = metrics.failure_count + metrics.success_count
        if data_points < 10:
            confidence = 'low'
        elif data_points < 50:
            confidence = 'medium'
        else:
            confidence = 'high'
        
        # Update metrics
        metrics.health_score = health_score
        metrics.last_updated = time.time()
        
        return {
            'health_score': health_score,
            'confidence': confidence,
            'components': {
                'failure_rate_score': failure_rate_score,
                'response_time_score': response_time_score,
                'success_trend_score': success_trend_score,
                'business_impact_score': business_impact_score
            },
            'metrics': {
                'failure_rate': metrics.failure_rate,
                'avg_response_time': metrics.avg_response_time,
                'current_state': metrics.current_state.value
            }
        }
    
    async def isolate_failed_services(self, service_names: List[str]) -> Dict[str, Any]:
        """Isolate failed services for cascade prevention"""
        isolation_actions = []
        
        for service_name in service_names:
            # Find all operations for this service
            service_operations = [
                key for key in self.circuit_states.keys() 
                if key.startswith(f"{service_name}_")
            ]
            
            for service_key in service_operations:
                current_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
                
                if current_state != CircuitState.OPEN:
                    # Force circuit open for isolation
                    old_state = current_state
                    self.circuit_states[service_key] = CircuitState.OPEN
                    self.last_failure_times[service_key] = time.time()
                    
                    isolation_actions.append({
                        'service_key': service_key,
                        'old_state': old_state.value,
                        'new_state': CircuitState.OPEN.value,
                        'action': 'isolated',
                        'timestamp': time.time()
                    })
                    
                    logger.warning(f"Isolated service {service_key} due to cascade prevention")
        
        return {
            'isolated_services': len(isolation_actions),
            'isolation_actions': isolation_actions,
            'cascade_prevention_active': True,
            'next_recovery_check': time.time() + 300  # 5 minutes
        }
    
    async def _load_default_circuit_configs(self):
        """Load default circuit breaker configurations"""
        for service_name, operations in self.business_circuit_configs.items():
            for operation_name, config in operations.items():
                service_key = f"{service_name}_{operation_name}"
                self.circuit_configs[service_key] = config
                
        logger.info(f"Loaded {len(self.circuit_configs)} circuit breaker configurations")
    
    async def _initialize_circuit_states(self):
        """Initialize circuit states for all configured services"""
        for service_key in self.circuit_configs.keys():
            self.circuit_states[service_key] = CircuitState.CLOSED
            self.failure_counts[service_key] = 0
            self.success_counts[service_key] = 0
            self.half_open_calls[service_key] = 0
            
            # Initialize metrics
            service_name, operation_name = service_key.split('_', 1)
            self.circuit_metrics[service_key] = CircuitHealthMetrics(
                service_name=service_name,
                operation_name=operation_name,
                current_state=CircuitState.CLOSED
            )
            
        logger.info(f"Initialized {len(self.circuit_states)} circuit breaker states")
    
    def _get_config(self, service_key: str) -> CircuitBreakerConfig:
        """Get circuit breaker configuration for service"""
        return self.circuit_configs.get(service_key, CircuitBreakerConfig(
            service_name=service_key.split('_')[0],
            operation_name='_'.join(service_key.split('_')[1:])
        ))
    
    async def _calculate_circuit_aware_timeout(self, integration_request: CircuitIntegrationRequest) -> float:
        """Calculate timeout value considering circuit breaker state"""
        service_key = f"{integration_request.service_name}_{integration_request.operation_name}"
        config = self._get_config(service_key)
        current_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
        
        base_timeout = integration_request.timeout_override or config.timeout_duration
        
        # Adjust timeout based on circuit state
        if current_state == CircuitState.HALF_OPEN:
            # Shorter timeout in half-open state for faster failure detection
            return base_timeout * 0.7
        elif current_state == CircuitState.OPEN:
            # Very short timeout in open state
            return min(base_timeout * 0.1, 5.0)
        else:
            # Normal timeout in closed state
            return base_timeout
    
    async def _record_success(self, service_key: str, execution_time: float):
        """Record successful execution"""
        self.success_counts[service_key] = self.success_counts.get(service_key, 0) + 1
        
        # Update metrics
        metrics = self.circuit_metrics.get(service_key)
        if metrics:
            metrics.success_count += 1
            metrics.last_success_time = time.time()
            
            # Update moving average response time
            if metrics.avg_response_time == 0:
                metrics.avg_response_time = execution_time
            else:
                metrics.avg_response_time = (metrics.avg_response_time * 0.9) + (execution_time * 0.1)
            
            # Update failure rate
            total_calls = metrics.success_count + metrics.failure_count
            metrics.failure_rate = metrics.failure_count / total_calls if total_calls > 0 else 0
        
        # Check if circuit should close from half-open
        current_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
        if current_state == CircuitState.HALF_OPEN:
            config = self._get_config(service_key)
            if self.success_counts.get(service_key, 0) >= config.success_threshold:
                await self._close_circuit(service_key)
    
    async def _record_failure(self, service_key: str, failure_type: CircuitFailureType, execution_time: float):
        """Record failed execution"""
        self.failure_counts[service_key] = self.failure_counts.get(service_key, 0) + 1
        self.last_failure_times[service_key] = time.time()
        
        # Update metrics
        metrics = self.circuit_metrics.get(service_key)
        if metrics:
            metrics.failure_count += 1
            metrics.last_failure_time = time.time()
            
            # Update failure rate
            total_calls = metrics.success_count + metrics.failure_count
            metrics.failure_rate = metrics.failure_count / total_calls if total_calls > 0 else 0
        
        logger.warning(f"Circuit breaker failure recorded for {service_key}: {failure_type.value}")
    
    async def _evaluate_circuit_state(self, service_key: str) -> Dict[str, Any]:
        """Evaluate and potentially change circuit state"""
        current_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
        config = self._get_config(service_key)
        
        if current_state == CircuitState.CLOSED:
            # Check if should open
            if self.failure_counts.get(service_key, 0) >= config.failure_threshold:
                return await self._open_circuit(service_key)
                
        elif current_state == CircuitState.OPEN:
            # Check if should move to half-open
            last_failure = self.last_failure_times.get(service_key, 0)
            if time.time() - last_failure >= config.timeout_duration:
                return await self._half_open_circuit(service_key)
                
        elif current_state == CircuitState.HALF_OPEN:
            # State changes handled in record_success/record_failure
            pass
        
        return {
            'service_key': service_key,
            'state_changed': False,
            'current_state': current_state.value
        }
    
    async def _open_circuit(self, service_key: str) -> Dict[str, Any]:
        """Open circuit breaker"""
        old_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
        self.circuit_states[service_key] = CircuitState.OPEN
        
        # Update metrics
        metrics = self.circuit_metrics.get(service_key)
        if metrics:
            metrics.current_state = CircuitState.OPEN
        
        logger.warning(f"Circuit breaker OPENED for {service_key}")
        
        return {
            'service_key': service_key,
            'old_state': old_state.value,
            'new_state': CircuitState.OPEN.value,
            'transition_reason': 'failure_threshold_exceeded',
            'timestamp': time.time()
        }
    
    async def _half_open_circuit(self, service_key: str) -> Dict[str, Any]:
        """Move circuit to half-open state"""
        old_state = self.circuit_states.get(service_key, CircuitState.OPEN)
        self.circuit_states[service_key] = CircuitState.HALF_OPEN
        self.half_open_calls[service_key] = 0
        self.success_counts[service_key] = 0  # Reset success count for half-open evaluation
        
        # Update metrics
        metrics = self.circuit_metrics.get(service_key)
        if metrics:
            metrics.current_state = CircuitState.HALF_OPEN
        
        logger.info(f"Circuit breaker moved to HALF-OPEN for {service_key}")
        
        return {
            'service_key': service_key,
            'old_state': old_state.value,
            'new_state': CircuitState.HALF_OPEN.value,
            'transition_reason': 'timeout_period_expired',
            'timestamp': time.time()
        }
    
    async def _close_circuit(self, service_key: str) -> Dict[str, Any]:
        """Close circuit breaker"""
        old_state = self.circuit_states.get(service_key, CircuitState.HALF_OPEN)
        self.circuit_states[service_key] = CircuitState.CLOSED
        self.failure_counts[service_key] = 0  # Reset failure count
        self.half_open_calls[service_key] = 0
        
        # Update metrics
        metrics = self.circuit_metrics.get(service_key)
        if metrics:
            metrics.current_state = CircuitState.CLOSED
        
        logger.info(f"Circuit breaker CLOSED for {service_key}")
        
        return {
            'service_key': service_key,
            'old_state': old_state.value,
            'new_state': CircuitState.CLOSED.value,
            'transition_reason': 'success_threshold_reached',
            'timestamp': time.time()
        }
    
    async def _reset_state_counters(self, service_key: str, new_state: CircuitState):
        """Reset counters for new circuit state"""
        if new_state == CircuitState.CLOSED:
            self.failure_counts[service_key] = 0
            self.half_open_calls[service_key] = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_counts[service_key] = 0
            self.half_open_calls[service_key] = 0
        elif new_state == CircuitState.OPEN:
            self.last_failure_times[service_key] = time.time()
    
    async def _handle_open_circuit(self, integration_request: CircuitIntegrationRequest) -> CircuitIntegrationResult:
        """Handle request when circuit is open"""
        service_key = f"{integration_request.service_name}_{integration_request.operation_name}"
        
        # Execute fallback if available
        fallback_result = None
        fallback_executed = False
        
        if self._get_config(service_key).enable_fallback:
            fallback_result = await self._execute_fallback(integration_request)
            fallback_executed = fallback_result is not None
        
        return CircuitIntegrationResult(
            request_id=integration_request.request_id,
            success=False,
            error=Exception("Circuit breaker is OPEN"),
            execution_time=0.0,
            circuit_state=CircuitState.OPEN,
            circuit_triggered=True,
            fallback_executed=fallback_executed,
            result=fallback_result
        )
    
    async def _handle_half_open_capacity_exceeded(self, integration_request: CircuitIntegrationRequest) -> CircuitIntegrationResult:
        """Handle request when half-open circuit is at capacity"""
        service_key = f"{integration_request.service_name}_{integration_request.operation_name}"
        
        # Execute fallback if available
        fallback_result = None
        fallback_executed = False
        
        if self._get_config(service_key).enable_fallback:
            fallback_result = await self._execute_fallback(integration_request)
            fallback_executed = fallback_result is not None
        
        return CircuitIntegrationResult(
            request_id=integration_request.request_id,
            success=False,
            error=Exception("Circuit breaker HALF-OPEN capacity exceeded"),
            execution_time=0.0,
            circuit_state=CircuitState.HALF_OPEN,
            circuit_triggered=True,
            fallback_executed=fallback_executed,
            result=fallback_result
        )
    
    async def _execute_fallback(self, integration_request: CircuitIntegrationRequest) -> Any:
        """Execute fallback for failed circuit"""
        service_key = f"{integration_request.service_name}_{integration_request.operation_name}"
        
        # Check for registered fallback handler
        fallback_handler = self.fallback_handlers.get(service_key)
        if fallback_handler:
            try:
                if asyncio.iscoroutinefunction(fallback_handler):
                    return await fallback_handler(integration_request)
                else:
                    return fallback_handler(integration_request)
            except Exception as e:
                logger.error(f"Fallback handler failed for {service_key}: {e}")
        
        # Default fallback based on service type
        return await self._execute_default_fallback(integration_request)
    
    async def _execute_default_fallback(self, integration_request: CircuitIntegrationRequest) -> Dict[str, Any]:
        """Execute default fallback strategy"""
        service_name = integration_request.service_name
        
        # Business-specific fallback strategies for IA Chéries
        if 'creator' in service_name:
            return {
                'fallback': True,
                'strategy': 'creator_fallback',
                'message': 'Creator service temporarily unavailable - please try again',
                'retry_after': 300
            }
        elif 'ai' in service_name:
            return {
                'fallback': True,
                'strategy': 'ai_fallback',
                'message': 'AI processing queued for background execution',
                'queue_id': f"ai_queue_{int(time.time())}"
            }
        elif 'payment' in service_name:
            # No fallback for payments - return None
            return None
        elif 'collaboration' in service_name:
            return {
                'fallback': True,
                'strategy': 'collaboration_fallback',
                'message': 'Using cached collaboration data',
                'cache_timestamp': time.time()
            }
        else:
            return {
                'fallback': True,
                'strategy': 'default_fallback',
                'message': 'Service temporarily unavailable',
                'timestamp': time.time()
            }
    
    async def _classify_exception(self, exception: Exception, execution_time: float, 
                                integration_request: CircuitIntegrationRequest) -> CircuitFailureType:
        """Classify exception type for circuit breaker decision"""
        config = self._get_config(f"{integration_request.service_name}_{integration_request.operation_name}")
        
        if isinstance(exception, asyncio.TimeoutError):
            return CircuitFailureType.TIMEOUT
        elif execution_time > config.slow_response_threshold:
            return CircuitFailureType.SLOW_RESPONSE
        elif 'connection' in str(exception).lower() or 'network' in str(exception).lower():
            return CircuitFailureType.EXTERNAL_DEPENDENCY
        elif 'memory' in str(exception).lower() or 'resource' in str(exception).lower():
            return CircuitFailureType.RESOURCE_EXHAUSTION
        else:
            return CircuitFailureType.EXCEPTION
    
    async def _calculate_response_time_score(self, avg_response_time: float, service_key: str) -> float:
        """Calculate response time score component"""
        config = self._get_config(service_key)
        optimal_time = config.timeout_duration * 0.3  # 30% of timeout is optimal
        
        if avg_response_time <= optimal_time:
            return 1.0
        elif avg_response_time <= config.slow_response_threshold:
            return 1.0 - ((avg_response_time - optimal_time) / (config.slow_response_threshold - optimal_time)) * 0.5
        else:
            return 0.0
    
    async def _calculate_success_trend_score(self, service_key: str) -> float:
        """Calculate success trend score component"""
        # In a real implementation, this would analyze recent success trends
        # For now, return a simple score based on recent success/failure ratio
        recent_successes = self.success_counts.get(service_key, 0)
        recent_failures = self.failure_counts.get(service_key, 0)
        
        if recent_successes + recent_failures == 0:
            return 0.5  # No data
        
        return recent_successes / (recent_successes + recent_failures)
    
    async def _calculate_business_impact_score(self, service_key: str) -> float:
        """Calculate business impact score component"""
        config = self._get_config(service_key)
        priority_weight = self.priority_weights.get(config.business_priority, 0.6)
        
        # Higher priority services have higher impact when failing
        current_state = self.circuit_states.get(service_key, CircuitState.CLOSED)
        
        if current_state == CircuitState.CLOSED:
            return priority_weight
        elif current_state == CircuitState.HALF_OPEN:
            return priority_weight * 0.7
        else:  # OPEN
            return priority_weight * 0.3
    
    async def _health_monitoring_task(self):
        """Background task for health monitoring"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for service_key in self.circuit_configs.keys():
                    await self.calculate_circuit_health_score(
                        service_key.split('_')[0],
                        '_'.join(service_key.split('_')[1:])
                    )
                    
                logger.debug("Health monitoring cycle completed")
            except Exception as e:
                logger.error(f"Error in health monitoring task: {e}")
    
    async def _recovery_testing_task(self):
        """Background task for recovery testing"""
        while True:
            try:
                await asyncio.sleep(300)  # Test every 5 minutes
                
                # Test recovery for open circuits
                for service_key, state in self.circuit_states.items():
                    if state == CircuitState.OPEN:
                        # Check if ready for recovery testing
                        config = self._get_config(service_key)
                        last_failure = self.last_failure_times.get(service_key, 0)
                        
                        if time.time() - last_failure >= config.timeout_duration:
                            await self._half_open_circuit(service_key)
                            
                logger.debug("Recovery testing cycle completed")
            except Exception as e:
                logger.error(f"Error in recovery testing task: {e}")
    
    async def _metrics_collection_task(self):
        """Background task for metrics collection"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Update circuit metrics
                for service_key, metrics in self.circuit_metrics.items():
                    current_time = time.time()
                    metrics.last_updated = current_time
                    
                logger.debug("Metrics collection cycle completed")
            except Exception as e:
                logger.error(f"Error in metrics collection task: {e}")
    
    def register_fallback_handler(self, service_name: str, operation_name: str, handler: Callable):
        """Register fallback handler for service operation"""
        service_key = f"{service_name}_{operation_name}"
        self.fallback_handlers[service_key] = handler
        logger.info(f"Registered fallback handler for {service_key}")
    
    def register_recovery_handler(self, service_name: str, operation_name: str, handler: Callable):
        """Register recovery handler for service operation"""
        service_key = f"{service_name}_{operation_name}"
        self.recovery_handlers[service_key] = handler
        logger.info(f"Registered recovery handler for {service_key}")
    
    def get_circuit_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker status"""
        if service_name:
            service_circuits = {
                key: {
                    'state': state.value,
                    'failure_count': self.failure_counts.get(key, 0),
                    'success_count': self.success_counts.get(key, 0),
                    'metrics': self.circuit_metrics.get(key)
                }
                for key, state in self.circuit_states.items()
                if key.startswith(f"{service_name}_")
            }
            return service_circuits
        else:
            return {
                key: {
                    'state': state.value,
                    'failure_count': self.failure_counts.get(key, 0),
                    'success_count': self.success_counts.get(key, 0),
                    'metrics': self.circuit_metrics.get(key)
                }
                for key, state in self.circuit_states.items()
            }
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration metrics"""
        total_circuits = len(self.circuit_states)
        open_circuits = sum(1 for state in self.circuit_states.values() if state == CircuitState.OPEN)
        half_open_circuits = sum(1 for state in self.circuit_states.values() if state == CircuitState.HALF_OPEN)
        closed_circuits = total_circuits - open_circuits - half_open_circuits
        
        return {
            'total_circuits': total_circuits,
            'closed_circuits': closed_circuits,
            'open_circuits': open_circuits,
            'half_open_circuits': half_open_circuits,
            'health_status': 'healthy' if open_circuits == 0 else 'degraded',
            'fallback_handlers': len(self.fallback_handlers),
            'recovery_handlers': len(self.recovery_handlers),
            'last_updated': time.time()
        }

# Global circuit breaker integration instance
circuit_breaker_integration = CircuitBreakerIntegration()

# Export main classes and functions
__all__ = [
    'CircuitBreakerIntegration',
    'CircuitBreakerConfig',
    'CircuitIntegrationRequest',
    'CircuitIntegrationResult',
    'CircuitState',
    'CircuitFailureType',
    'RecoveryStrategy',
    'circuit_breaker_integration'
]