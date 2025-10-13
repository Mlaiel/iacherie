"""🔗 Microservices Orchestration Module - Enterprise Service Management
======================================================================

Module __init__.py pour centraliser l'orchestration des microservices enterprise.

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

from .enterprise_service_orchestrator import (
    EnterpriseServiceOrchestrator,
    ServiceInstance,
    ServiceStatus,
    ServiceType,
    LoadBalancingStrategy,
    CircuitBreaker,
    CircuitBreakerState,
    ServiceCall,
    initialize_service_orchestrator
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "EnterpriseServiceOrchestrator",
    "ServiceInstance",
    "ServiceStatus", 
    "ServiceType",
    "LoadBalancingStrategy",
    "CircuitBreaker",
    "CircuitBreakerState",
    "ServiceCall",
    "initialize_service_orchestrator"
]