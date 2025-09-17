"""
Error Handling Module - Ainflue Integrations
===========================================
Enterprise error handling module providing comprehensive error management,
logging, recovery automation, and exception handling.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Error Handling Core Components
from .error_handler import ErrorHandler

# Phase 1: Resilience Patterns Enterprise
from .circuit_breaker_manager import CircuitBreakerManager, CircuitBreaker
from .retry_policy_engine import RetryPolicyEngine
from .bulkhead_isolation_manager import BulkheadIsolationManager, Bulkhead
from .timeout_management_system import TimeoutManagementSystem

# Phase 2: Distributed Error Management
from .distributed_error_orchestrator import DistributedErrorOrchestrator
from .error_propagation_controller import ErrorPropagationController
from .distributed_tracing_integration import DistributedTracingIntegration
from .compensation_transaction_manager import CompensationTransactionManager

# Public exports
__all__ = [
    # Core Error Handling
    'ErrorHandler',
    
    # Phase 1: Resilience Patterns Enterprise
    'CircuitBreakerManager',
    'CircuitBreaker', 
    'RetryPolicyEngine',
    'BulkheadIsolationManager',
    'Bulkhead',
    'TimeoutManagementSystem',
    
    # Phase 2: Distributed Error Management
    'DistributedErrorOrchestrator',
    'ErrorPropagationController',
    'DistributedTracingIntegration',
    'CompensationTransactionManager',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise error handling and recovery for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_ERROR_HANDLING = {
    'platforms': 65,
    'error_features': [
        'intelligent_recovery', 
        'automated_logging', 
        'escalation_management',
        'circuit_breaker_patterns',
        'adaptive_retry_policies',
        'bulkhead_isolation',
        'timeout_management',
        'distributed_orchestration',
        'error_propagation_control',
        'distributed_tracing',
        'saga_compensation'
    ],
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'phase_1_complete': True,
    'phase_2_complete': True,
    'implementation_coverage': '61.1%'  # 11/18 files implemented
}