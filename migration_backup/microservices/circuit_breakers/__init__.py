"""
Circuit Breakers Module for IA Chéries Microservices - Enterprise Edition
=====================================================================

Implements enterprise circuit breaker patterns with advanced features:
- ML-powered failure prediction and adaptive thresholds
- Distributed coordination with Raft consensus
- Multi-framework middleware integration
- Multi-tier fallback strategies with intelligent caching
- Comprehensive metrics and observability

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import threading
from typing import Callable, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Legacy circuit breaker for backward compatibility
class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class CircuitBreaker:
    """Legacy circuit breaker implementation for microservices (backward compatibility)"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60, 
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker moved to HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
                
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.timeout
        
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            logger.info("Circuit breaker moved to CLOSED state")
            
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker moved to OPEN state after {self.failure_count} failures")
            
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self.state
        
    def reset(self):
        """Manually reset circuit breaker"""
        with self._lock:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED
            self.last_failure_time = None
            logger.info("Circuit breaker manually reset to CLOSED state")

# Import enterprise components
try:
    from .enterprise_circuit_breaker import (
        EnterpriseCircuitBreaker,
        EnterpriseCircuitConfig,
        CircuitState as EnterpriseCircuitState,
        FailureType,
        CircuitMetrics,
        MLFailurePredictor,
        AdvancedStateMachine
    )
    HAS_ENTERPRISE_CIRCUIT_BREAKER = True
except ImportError:
    HAS_ENTERPRISE_CIRCUIT_BREAKER = False

try:
    from .distributed_circuit_coordinator import (
        DistributedCircuitCoordinator,
        ClusterConfig,
        ClusterNode,
        CircuitEventData,
        CircuitEvent,
        NodeState,
        RaftConsensus,
        StateReplicator,
        ClusterHealthMonitor
    )
    HAS_DISTRIBUTED_COORDINATOR = True
except ImportError:
    HAS_DISTRIBUTED_COORDINATOR = False

try:
    from .adaptive_threshold_manager import (
        AdaptiveThresholdManager,
        MLConfig,
        ThresholdMetric,
        AnomalyType,
        Anomaly,
        ThresholdRecommendation,
        LSTMModel,
        ProphetModel
    )
    HAS_ADAPTIVE_THRESHOLD_MANAGER = True
except ImportError:
    HAS_ADAPTIVE_THRESHOLD_MANAGER = False

try:
    from .circuit_breaker_middleware import (
        CircuitBreakerMiddleware,
        FrameworkConfig,
        EndpointConfig,
        FrameworkType,
        RequestCriticality,
        RequestClassifier,
        ResponseAnalyzer,
        CircuitRegistry,
        create_fastapi_middleware,
        create_flask_middleware,
        create_grpc_interceptor
    )
    HAS_CIRCUIT_BREAKER_MIDDLEWARE = True
except ImportError:
    HAS_CIRCUIT_BREAKER_MIDDLEWARE = False

try:
    from .fallback_strategy_engine import (
        FallbackStrategyEngine,
        FallbackConfig,
        FallbackStrategy,
        FallbackStrategyType,
        FallbackQuality,
        MultiTierCacheManager,
        ServiceMeshConnector,
        FallbackRegistry,
        CacheType,
        ServiceMeshType
    )
    HAS_FALLBACK_STRATEGY_ENGINE = True
except ImportError:
    HAS_FALLBACK_STRATEGY_ENGINE = False

try:
    from .circuit_breaker_metrics import (
        CircuitBreakerMetrics,
        MetricsConfig,
        AlertRule,
        AlertSeverity,
        DashboardType,
        PrometheusClient,
        GrafanaClient,
        AlertManagerClient,
        CustomMetricsRegistry
    )
    HAS_CIRCUIT_BREAKER_METRICS = True
except ImportError:
    HAS_CIRCUIT_BREAKER_METRICS = False

# Export all components
__all__ = [
    # Legacy components (backward compatibility)
    'CircuitBreaker', 
    'CircuitBreakerState', 
    'CircuitBreakerOpenException',
]

# Add enterprise components if available
if HAS_ENTERPRISE_CIRCUIT_BREAKER:
    __all__.extend([
        'EnterpriseCircuitBreaker',
        'EnterpriseCircuitConfig',
        'EnterpriseCircuitState',
        'FailureType',
        'CircuitMetrics',
        'MLFailurePredictor',
        'AdvancedStateMachine'
    ])

if HAS_DISTRIBUTED_COORDINATOR:
    __all__.extend([
        'DistributedCircuitCoordinator',
        'ClusterConfig',
        'ClusterNode',
        'CircuitEventData',
        'CircuitEvent',
        'NodeState',
        'RaftConsensus',
        'StateReplicator',
        'ClusterHealthMonitor'
    ])

if HAS_ADAPTIVE_THRESHOLD_MANAGER:
    __all__.extend([
        'AdaptiveThresholdManager',
        'MLConfig',
        'ThresholdMetric',
        'AnomalyType',
        'Anomaly',
        'ThresholdRecommendation',
        'LSTMModel',
        'ProphetModel'
    ])

if HAS_CIRCUIT_BREAKER_MIDDLEWARE:
    __all__.extend([
        'CircuitBreakerMiddleware',
        'FrameworkConfig',
        'EndpointConfig',
        'FrameworkType',
        'RequestCriticality',
        'RequestClassifier',
        'ResponseAnalyzer',
        'CircuitRegistry',
        'create_fastapi_middleware',
        'create_flask_middleware',
        'create_grpc_interceptor'
    ])

if HAS_FALLBACK_STRATEGY_ENGINE:
    __all__.extend([
        'FallbackStrategyEngine',
        'FallbackConfig',
        'FallbackStrategy',
        'FallbackStrategyType',
        'FallbackQuality',
        'MultiTierCacheManager',
        'ServiceMeshConnector',
        'FallbackRegistry',
        'CacheType',
        'ServiceMeshType'
    ])

if HAS_CIRCUIT_BREAKER_METRICS:
    __all__.extend([
        'CircuitBreakerMetrics',
        'MetricsConfig',
        'AlertRule',
        'AlertSeverity',
        'DashboardType',
        'PrometheusClient',
        'GrafanaClient',
        'AlertManagerClient',
        'CustomMetricsRegistry'
    ])

# Module info
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Circuit Breakers with ML, Distributed Coordination, and Observability"

# Feature flags for runtime detection
FEATURES = {
    'enterprise_circuit_breaker': HAS_ENTERPRISE_CIRCUIT_BREAKER,
    'distributed_coordinator': HAS_DISTRIBUTED_COORDINATOR,
    'adaptive_threshold_manager': HAS_ADAPTIVE_THRESHOLD_MANAGER,
    'circuit_breaker_middleware': HAS_CIRCUIT_BREAKER_MIDDLEWARE,
    'fallback_strategy_engine': HAS_FALLBACK_STRATEGY_ENGINE,
    'circuit_breaker_metrics': HAS_CIRCUIT_BREAKER_METRICS,
}
