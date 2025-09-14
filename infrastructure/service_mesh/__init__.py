"""
Service Mesh Module - Enterprise Microservices Communication Infrastructure
================================================================================

Expert Team: Microservices + Backend Senior + Security + DevOps
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🔗 Microservices: Service mesh architecture, inter-service communication
🏗️ Backend Senior: Load balancing, circuit breakers, service discovery
🔒 Security: mTLS, zero-trust networking, policy management
⚙️ DevOps: Observability, traffic management, deployment strategies

Production service mesh for Ainflue microservices architecture supporting:
- Istio and Linkerd service mesh integration
- Advanced traffic management and load balancing
- Circuit breakers and fault tolerance
- Service discovery and registration
- Mutual TLS and zero-trust security
- Comprehensive observability and monitoring
- Policy management and access control
"""

from .istio_integration import IstioIntegration
from .linkerd_integration import LinkerdIntegration
from .service_mesh_security import ServiceMeshSecurity
from .service_mesh_monitoring import ServiceMeshMonitoring
from .load_balancing import LoadBalancing
from .circuit_breaker import CircuitBreaker
from .service_discovery import ServiceDiscovery
from .traffic_management import TrafficManagement
from .mutual_tls import MutualTLS
from .observability_mesh import ObservabilityMesh
from .policy_management import PolicyManagement

__all__ = [
    'IstioIntegration',
    'LinkerdIntegration',
    'ServiceMeshSecurity',
    'ServiceMeshMonitoring',
    'LoadBalancing',
    'CircuitBreaker',
    'ServiceDiscovery',
    'TrafficManagement',
    'MutualTLS',
    'ObservabilityMesh',
    'PolicyManagement'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise service mesh infrastructure for microservices communication"