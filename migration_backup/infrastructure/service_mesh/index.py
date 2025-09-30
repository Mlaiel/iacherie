"""
Service Mesh Module - Ainflue Infrastructure
===========================================
Enterprise service mesh management for microservices orchestration

This module provides comprehensive service mesh capabilities including:
- Istio integration and management
- Linkerd integration and management
- Service discovery and load balancing
- Traffic management and circuit breakers
- mTLS security and policy management

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure Enterprise
Version: 1.0 Production
"""

from .istio_integration import (
    IstioServiceMesh,
    IstioConfiguration,
    IstioGateway,
    IstioVirtualService,
    IstioDestinationRule,
    LoadBalancingAlgorithm,
    TrafficPolicyType
)

# Additional imports that would be available when fully implemented
# from .linkerd_integration import LinkerdIntegration
# from .service_mesh_security import ServiceMeshSecurity
# from .service_mesh_monitoring import ServiceMeshMonitoring
# from .load_balancing import LoadBalancing
# from .circuit_breaker import CircuitBreaker
# from .service_discovery import ServiceDiscovery
# from .traffic_management import TrafficManagement
# from .mutual_tls import MutualTLS
# from .observability_mesh import ObservabilityMesh
# from .policy_management import PolicyManagement

# Exports publics
__all__ = [
    'IstioServiceMesh',
    'IstioConfiguration', 
    'IstioGateway',
    'IstioVirtualService',
    'IstioDestinationRule',
    'LoadBalancingAlgorithm',
    'TrafficPolicyType',
    # Additional exports when implemented
    # 'LinkerdIntegration',
    # 'ServiceMeshSecurity',
    # 'ServiceMeshMonitoring',
    # 'LoadBalancing',
    # 'CircuitBreaker',
    # 'ServiceDiscovery',
    # 'TrafficManagement',
    # 'MutualTLS',
    # 'ObservabilityMesh',
    # 'PolicyManagement'
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise service mesh infrastructure"

# Configuration logique métier Ainflue
AINFLUE_SERVICE_MESH_CONFIG = {
    'upload': 'Service routing for multi-format content upload services',
    'ai_processing': 'Load balancing for 53 AI agents across mesh', 
    'protection': 'Secure service communication for rights protection',
    'monetization': 'Traffic management for revenue optimization services',
    'collaboration': 'Service discovery for creator matching services',
    'seo': 'Circuit breakers for SEO optimization services',
    'distribution': 'Mesh orchestration for 65+ platform distribution'
}

# Service mesh performance targets
SERVICE_MESH_TARGETS = {
    'latency_p99_ms': 100,
    'throughput_rps': 50000,
    'availability_percent': 99.99,
    'mtls_enabled': True,
    'circuit_breaker_threshold': 80
}