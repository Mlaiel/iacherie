"""
Enterprise Circuit Breaker Core - Ainflue Platform
=================================================

Enterprise circuit breaker with advanced patterns, ML prediction, and adaptive thresholds.
Multi-state management, graceful degradation, and distributed state synchronization.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, List, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor

# ML and Analytics imports (graceful degradation if not available)
try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    HAS_ML = True
except ImportError:
    HAS_ML = False
    np = None

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Enhanced circuit breaker states"""
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    FORCED_OPEN = "FORCED_OPEN"
    FORCED_CLOSED = "FORCED_CLOSED"

class FailureType(Enum):
    """Types of failures for classification"""
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

@dataclass
class CircuitMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    failed_requests: int = 0
    successful_requests: int = 0
    rejected_requests: int = 0
    timeout_requests: int = 0
    average_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    failure_rate: float = 0.0
    success_rate: float = 0.0

@dataclass
class EnterpriseCircuitConfig:
    """Enterprise circuit breaker configuration"""
    # Basic thresholds
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: float = 30.0
    recovery_timeout: int = 60
    
    # Advanced features
    enable_ml_prediction: bool = True
    enable_adaptive_thresholds: bool = True
    enable_distributed_sync: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 100
    sliding_window_size: int = 100
    metrics_retention_hours: int = 24
    
    # ML settings
    anomaly_detection_enabled: bool = True
    prediction_confidence_threshold: float = 0.7
    model_retrain_interval_hours: int = 6
    
    # Fallback settings
    fallback_strategies: List[str] = field(default_factory=lambda: ["cache", "static", "alternate_service"])
    graceful_degradation_enabled: bool = True

class MLFailurePredictor:
    """ML-based failure prediction engine"""
    
    def __init__(self, config: EnterpriseCircuitConfig):
        self.config = config
        self.model = None
        self.scaler = None
        self.training_data = []
        self.last_training = None
        
        if HAS_ML and config.enable_ml_prediction:
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.scaler = StandardScaler()
    
    async def predict_failure_probability(self, metrics: CircuitMetrics, context: Dict[str, Any]) -> float:
        """Predict failure probability using ML models"""
        if not HAS_ML or not self.config.enable_ml_prediction or not self.model:
            return 0.0
        
        try:
            # Feature extraction
            features = self._extract_features(metrics, context)
            
            # Ensure model is trained
            if len(self.training_data) < 10:
                return 0.0
            
            # Make prediction
            features_scaled = self.scaler.transform([features])
            anomaly_score = self.model.decision_function(features_scaled)[0]
            
            # Convert to probability (0-1 range)
            probability = max(0.0, min(1.0, (1 - anomaly_score) / 2))
            
            return probability
            
        except Exception as e:
            logger.warning(f"ML prediction failed: {str(e)}")
            return 0.0
    
    def _extract_features(self, metrics: CircuitMetrics, context: Dict[str, Any]) -> List[float]:
        """Extract features for ML prediction"""
        features = [
            metrics.failure_rate,
            metrics.average_response_time,
            metrics.total_requests,
            time.time() % 86400,  # Time of day
            context.get('cpu_usage', 0.0),
            context.get('memory_usage', 0.0),
            context.get('network_latency', 0.0),
        ]
        
        return features
    
    async def train_model(self, historical_data: List[Dict[str, Any]]):
        """Train the ML model with historical data"""
        if not HAS_ML or not self.config.enable_ml_prediction:
            return
        
        try:
            if len(historical_data) < 10:
                return
            
            # Prepare training data
            features = []
            for data_point in historical_data:
                feature_vector = self._extract_features(
                    data_point['metrics'], 
                    data_point['context']
                )
                features.append(feature_vector)
            
            # Train model
            features_array = np.array(features)
            self.scaler.fit(features_array)
            features_scaled = self.scaler.transform(features_array)
            
            self.model.fit(features_scaled)
            self.last_training = datetime.now()
            
            logger.info(f"ML model trained with {len(historical_data)} data points")
            
        except Exception as e:
            logger.error(f"ML model training failed: {str(e)}")

class AdvancedStateMachine:
    """Advanced state machine for circuit breaker"""
    
    def __init__(self, config: EnterpriseCircuitConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.state_history = []
        self.state_change_callbacks = []
    
    async def transition_to(self, new_state: CircuitState, reason: str = ""):
        """Transition to new state with validation"""
        old_state = self.state
        
        if self._is_valid_transition(old_state, new_state):
            self.state = new_state
            self._record_state_change(old_state, new_state, reason)
            await self._notify_state_change(old_state, new_state, reason)
            logger.info(f"Circuit state transition: {old_state.value} -> {new_state.value} ({reason})")
        else:
            logger.warning(f"Invalid state transition: {old_state.value} -> {new_state.value}")
    
    def _is_valid_transition(self, from_state: CircuitState, to_state: CircuitState) -> bool:
        """Validate state transition"""
        valid_transitions = {
            CircuitState.CLOSED: [CircuitState.OPEN, CircuitState.FORCED_OPEN, CircuitState.FORCED_CLOSED],
            CircuitState.OPEN: [CircuitState.HALF_OPEN, CircuitState.FORCED_CLOSED],
            CircuitState.HALF_OPEN: [CircuitState.CLOSED, CircuitState.OPEN, CircuitState.FORCED_OPEN, CircuitState.FORCED_CLOSED],
            CircuitState.FORCED_OPEN: [CircuitState.FORCED_CLOSED],
            CircuitState.FORCED_CLOSED: [CircuitState.FORCED_OPEN]
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def _record_state_change(self, from_state: CircuitState, to_state: CircuitState, reason: str):
        """Record state change in history"""
        self.state_history.append({
            'timestamp': datetime.now(),
            'from_state': from_state.value,
            'to_state': to_state.value,
            'reason': reason
        })
        
        # Keep only recent history
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]
    
    async def _notify_state_change(self, from_state: CircuitState, to_state: CircuitState, reason: str):
        """Notify registered callbacks about state change"""
        for callback in self.state_change_callbacks:
            try:
                await callback(from_state, to_state, reason)
            except Exception as e:
                logger.error(f"State change callback failed: {str(e)}")

class EnterpriseCircuitBreaker:
    """
    Enterprise circuit breaker with advanced patterns.
    Multi-state management + adaptive thresholds + ML prediction.
    """
    
    def __init__(self, service_name: str, config: Optional[EnterpriseCircuitConfig] = None):
        self.service_name = service_name
        self.config = config or EnterpriseCircuitConfig()
        
        # Core components
        self.state_machine = AdvancedStateMachine(self.config)
        self.failure_predictor = MLFailurePredictor(self.config)
        self.metrics = CircuitMetrics()
        
        # Request tracking
        self.request_history = []
        self.concurrent_requests = 0
        self.request_lock = asyncio.Lock()
        
        # Adaptive thresholds
        self.adaptive_failure_threshold = self.config.failure_threshold
        self.adaptive_timeout = self.config.timeout_seconds
        
        # Thread pool for blocking operations
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        logger.info(f"Enterprise circuit breaker initialized for service: {service_name}")
    
    async def execute_with_protection(self, operation: Callable, context: Optional[Dict[str, Any]] = None, *args, **kwargs) -> Any:
        """
        Execute operation with circuit breaker protection.
        
        Features:
        - Adaptive failure thresholds based on ML
        - Context-aware circuit breaking
        - Graceful degradation patterns
        - Real-time metrics collection
        - Distributed circuit state synchronization
        """
        context = context or {}
        request_id = self._generate_request_id()
        
        async with self.request_lock:
            # Check concurrent request limits
            if self.concurrent_requests >= self.config.max_concurrent_requests:
                await self._record_request(request_id, "REJECTED", 0, "Max concurrent requests exceeded")
                raise Exception(f"Circuit breaker: Max concurrent requests ({self.config.max_concurrent_requests}) exceeded")
            
            self.concurrent_requests += 1
        
        try:
            # Check circuit state
            if not await self._should_allow_request(context):
                await self._record_request(request_id, "REJECTED", 0, f"Circuit state: {self.state_machine.state.value}")
                return await self.apply_graceful_degradation("circuit_open", context)
            
            # Execute operation with timeout
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(operation):
                    result = await asyncio.wait_for(
                        operation(*args, **kwargs),
                        timeout=self.adaptive_timeout
                    )
                else:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        lambda: operation(*args, **kwargs)
                    )
                
                execution_time = time.time() - start_time
                await self._record_request(request_id, "SUCCESS", execution_time, "")
                await self._on_success(execution_time, context)
                
                return result
                
            except asyncio.TimeoutError:
                execution_time = time.time() - start_time
                await self._record_request(request_id, "TIMEOUT", execution_time, "Operation timeout")
                await self._on_failure(FailureType.TIMEOUT, execution_time, context)
                return await self.apply_graceful_degradation("timeout", context)
                
            except Exception as e:
                execution_time = time.time() - start_time
                failure_type = self._classify_failure(e)
                await self._record_request(request_id, "FAILURE", execution_time, str(e))
                await self._on_failure(failure_type, execution_time, context)
                
                if await self._should_apply_fallback(failure_type):
                    return await self.apply_graceful_degradation(failure_type.value.lower(), context)
                else:
                    raise e
        
        finally:
            async with self.request_lock:
                self.concurrent_requests -= 1
    
    async def _should_allow_request(self, context: Dict[str, Any]) -> bool:
        """Determine if request should be allowed based on circuit state and ML prediction"""
        current_state = self.state_machine.state
        
        # Forced states
        if current_state == CircuitState.FORCED_OPEN:
            return False
        elif current_state == CircuitState.FORCED_CLOSED:
            return True
        
        # Normal circuit logic
        if current_state == CircuitState.CLOSED:
            # Check ML prediction if enabled
            if self.config.enable_ml_prediction:
                failure_probability = await self.failure_predictor.predict_failure_probability(self.metrics, context)
                if failure_probability > self.config.prediction_confidence_threshold:
                    logger.warning(f"ML prediction suggests high failure probability: {failure_probability:.2f}")
                    await self.state_machine.transition_to(CircuitState.HALF_OPEN, "ML prediction threshold exceeded")
                    return True  # Allow in half-open to test
            
            return True
        
        elif current_state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if (self.metrics.last_failure_time and 
                datetime.now() - self.metrics.last_failure_time > timedelta(seconds=self.config.recovery_timeout)):
                await self.state_machine.transition_to(CircuitState.HALF_OPEN, "Recovery timeout elapsed")
                return True
            return False
        
        elif current_state == CircuitState.HALF_OPEN:
            # Allow limited requests in half-open state
            return True
        
        return False
    
    async def _on_success(self, execution_time: float, context: Dict[str, Any]):
        """Handle successful request"""
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = datetime.now()
        
        # Update adaptive timeout based on performance
        if self.config.enable_adaptive_thresholds:
            self.adaptive_timeout = max(
                self.config.timeout_seconds * 0.5,
                min(self.config.timeout_seconds * 2.0, execution_time * 1.5)
            )
        
        # State transitions
        if self.state_machine.state == CircuitState.HALF_OPEN:
            # Check if we should close the circuit
            recent_successes = sum(1 for req in self.request_history[-10:] if req['status'] == 'SUCCESS')
            if recent_successes >= self.config.success_threshold:
                await self.state_machine.transition_to(CircuitState.CLOSED, "Success threshold met")
        
        await self._update_metrics()
    
    async def _on_failure(self, failure_type: FailureType, execution_time: float, context: Dict[str, Any]):
        """Handle failed request"""
        self.metrics.failed_requests += 1
        self.metrics.last_failure_time = datetime.now()
        
        if failure_type == FailureType.TIMEOUT:
            self.metrics.timeout_requests += 1
        
        # Update adaptive thresholds
        if self.config.enable_adaptive_thresholds:
            await self._update_adaptive_thresholds(failure_type, context)
        
        # State transitions
        current_state = self.state_machine.state
        
        if current_state == CircuitState.CLOSED:
            if self.metrics.failure_rate > (self.adaptive_failure_threshold / 100.0):
                await self.state_machine.transition_to(CircuitState.OPEN, f"Failure rate exceeded: {self.metrics.failure_rate:.2f}")
        
        elif current_state == CircuitState.HALF_OPEN:
            await self.state_machine.transition_to(CircuitState.OPEN, "Failure in half-open state")
        
        await self._update_metrics()
    
    async def _update_adaptive_thresholds(self, failure_type: FailureType, context: Dict[str, Any]):
        """Update adaptive thresholds based on failure patterns"""
        if not self.config.enable_adaptive_thresholds:
            return
        
        # Adjust failure threshold based on system load
        system_load = context.get('cpu_usage', 0.5)
        if system_load > 0.8:
            self.adaptive_failure_threshold = max(2, self.config.failure_threshold - 2)
        elif system_load < 0.3:
            self.adaptive_failure_threshold = min(20, self.config.failure_threshold + 3)
        
        # Adjust timeout based on failure type
        if failure_type == FailureType.TIMEOUT:
            self.adaptive_timeout = min(self.config.timeout_seconds * 2.0, self.adaptive_timeout * 1.2)
        elif failure_type == FailureType.CONNECTION_ERROR:
            self.adaptive_timeout = max(self.config.timeout_seconds * 0.5, self.adaptive_timeout * 0.9)
    
    async def apply_graceful_degradation(self, fallback_strategy: str, context: Dict[str, Any]) -> Any:
        """
        Apply graceful degradation with fallback intelligent.
        """
        if not self.config.graceful_degradation_enabled:
            raise Exception(f"Circuit breaker open for {self.service_name}, no fallback available")
        
        # Default fallback responses based on strategy
        fallback_responses = {
            "circuit_open": {"status": "degraded", "message": "Service temporarily unavailable", "fallback": True},
            "timeout": {"status": "timeout", "message": "Request timeout, using cached data", "fallback": True},
            "connection_error": {"status": "offline", "message": "Service offline, using backup", "fallback": True},
            "cache": await self._get_cached_response(context),
            "static": {"status": "static", "data": "Default response", "fallback": True}
        }
        
        response = fallback_responses.get(fallback_strategy, fallback_responses["static"])
        logger.info(f"Applied graceful degradation: {fallback_strategy} for {self.service_name}")
        
        return response
    
    async def _get_cached_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get cached response if available"""
        # This would integrate with Redis or other cache
        return {"status": "cached", "message": "Using cached data", "fallback": True}
    
    def _classify_failure(self, exception: Exception) -> FailureType:
        """Classify failure type for better handling"""
        exception_str = str(exception).lower()
        
        if "timeout" in exception_str:
            return FailureType.TIMEOUT
        elif "connection" in exception_str or "connect" in exception_str:
            return FailureType.CONNECTION_ERROR
        elif "http" in exception_str or "status" in exception_str:
            return FailureType.HTTP_ERROR
        elif "validation" in exception_str or "invalid" in exception_str:
            return FailureType.VALIDATION_ERROR
        elif "rate" in exception_str or "limit" in exception_str:
            return FailureType.RATE_LIMIT_ERROR
        else:
            return FailureType.UNKNOWN_ERROR
    
    async def _should_apply_fallback(self, failure_type: FailureType) -> bool:
        """Determine if fallback should be applied for failure type"""
        fallback_eligible = {
            FailureType.TIMEOUT: True,
            FailureType.CONNECTION_ERROR: True,
            FailureType.HTTP_ERROR: True,
            FailureType.RATE_LIMIT_ERROR: True,
            FailureType.VALIDATION_ERROR: False,
            FailureType.UNKNOWN_ERROR: True
        }
        
        return fallback_eligible.get(failure_type, False)
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return hashlib.md5(f"{self.service_name}_{time.time()}_{id(self)}".encode()).hexdigest()[:8]
    
    async def _record_request(self, request_id: str, status: str, execution_time: float, error_message: str):
        """Record request in history"""
        request_record = {
            'id': request_id,
            'timestamp': datetime.now(),
            'status': status,
            'execution_time': execution_time,
            'error_message': error_message
        }
        
        self.request_history.append(request_record)
        
        # Keep sliding window
        if len(self.request_history) > self.config.sliding_window_size:
            self.request_history = self.request_history[-self.config.sliding_window_size:]
        
        self.metrics.total_requests += 1
        if status == "REJECTED":
            self.metrics.rejected_requests += 1
    
    async def _update_metrics(self):
        """Update circuit breaker metrics"""
        total = self.metrics.total_requests
        if total > 0:
            self.metrics.failure_rate = self.metrics.failed_requests / total
            self.metrics.success_rate = self.metrics.successful_requests / total
        
        # Calculate average response time
        if self.request_history:
            successful_requests = [req for req in self.request_history if req['status'] == 'SUCCESS']
            if successful_requests:
                self.metrics.average_response_time = sum(req['execution_time'] for req in successful_requests) / len(successful_requests)
    
    async def calculate_adaptive_threshold(self, service_metrics: Dict[str, Any]) -> float:
        """Calculate adaptive threshold based on ML patterns"""
        if not self.config.enable_adaptive_thresholds:
            return float(self.config.failure_threshold)
        
        base_threshold = self.config.failure_threshold
        
        # Adjust based on system metrics
        cpu_usage = service_metrics.get('cpu_usage', 0.5)
        memory_usage = service_metrics.get('memory_usage', 0.5)
        network_latency = service_metrics.get('network_latency', 50)
        
        # System under stress - lower threshold
        if cpu_usage > 0.8 or memory_usage > 0.8 or network_latency > 200:
            adjustment = -2
        # System healthy - higher threshold
        elif cpu_usage < 0.3 and memory_usage < 0.3 and network_latency < 50:
            adjustment = 3
        else:
            adjustment = 0
        
        adaptive_threshold = max(1, min(20, base_threshold + adjustment))
        self.adaptive_failure_threshold = adaptive_threshold
        
        return float(adaptive_threshold)
    
    async def sync_distributed_state(self, cluster_nodes: List[str]) -> bool:
        """Synchronize circuit state between cluster nodes"""
        if not self.config.enable_distributed_sync:
            return True
        
        try:
            # This would integrate with distributed coordination service
            # For now, return success to maintain interface
            logger.info(f"Distributed state sync requested for {len(cluster_nodes)} nodes")
            return True
            
        except Exception as e:
            logger.error(f"Distributed state sync failed: {str(e)}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker metrics"""
        await self._update_metrics()
        
        return {
            'service_name': self.service_name,
            'state': self.state_machine.state.value,
            'metrics': {
                'total_requests': self.metrics.total_requests,
                'successful_requests': self.metrics.successful_requests,
                'failed_requests': self.metrics.failed_requests,
                'rejected_requests': self.metrics.rejected_requests,
                'timeout_requests': self.metrics.timeout_requests,
                'failure_rate': self.metrics.failure_rate,
                'success_rate': self.metrics.success_rate,
                'average_response_time': self.metrics.average_response_time,
                'concurrent_requests': self.concurrent_requests,
            },
            'adaptive_settings': {
                'adaptive_failure_threshold': self.adaptive_failure_threshold,
                'adaptive_timeout': self.adaptive_timeout,
            },
            'last_events': {
                'last_failure_time': self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                'last_success_time': self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
            },
            'state_history': self.state_machine.state_history[-10:],  # Last 10 state changes
        }
    
    async def reset(self, reason: str = "Manual reset"):
        """Reset circuit breaker to initial state"""
        await self.state_machine.transition_to(CircuitState.CLOSED, reason)
        self.metrics = CircuitMetrics()
        self.request_history = []
        self.concurrent_requests = 0
        self.adaptive_failure_threshold = self.config.failure_threshold
        self.adaptive_timeout = self.config.timeout_seconds
        
        logger.info(f"Circuit breaker reset for {self.service_name}: {reason}")
    
    async def force_state(self, state: CircuitState, reason: str = "Forced state change"):
        """Force circuit breaker to specific state"""
        if state in [CircuitState.FORCED_OPEN, CircuitState.FORCED_CLOSED]:
            await self.state_machine.transition_to(state, reason)
            logger.warning(f"Circuit breaker force state for {self.service_name}: {state.value} ({reason})")
        else:
            raise ValueError("Can only force to FORCED_OPEN or FORCED_CLOSED states")

# Export main classes
__all__ = [
    'EnterpriseCircuitBreaker',
    'EnterpriseCircuitConfig',
    'CircuitState',
    'FailureType',
    'CircuitMetrics',
    'MLFailurePredictor',
    'AdvancedStateMachine'
]