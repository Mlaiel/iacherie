"""Service Mesh Module - Enterprise Microservices Communication
=============================================================
Istio/Linkerd service mesh for microservices orchestration

Author: Fahed Mlaiel <mlaiel@live.de>
Project: Ainflue Infrastructure Enterprise
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by copyright.
Any unauthorized use, reproduction, or distribution without written 
permission from Fahed Mlaiel is strictly prohibited.

Service Mesh Components: Istio + Linkerd + Circuit Breakers + Load Balancing
"""

# Import core service mesh components
try:
    from .istio_integration import (
        IstioServiceMesh, IstioConfiguration, IstioGateway,
        IstioVirtualService, IstioDestinationRule, istio_mesh
    )
except ImportError:
    IstioServiceMesh = IstioConfiguration = IstioGateway = None
    IstioVirtualService = IstioDestinationRule = istio_mesh = None

try:
    from .linkerd_integration import (
        LinkerdServiceMesh, LinkerdConfiguration, LinkerdProfile,
        LinkerdTrafficSplit, linkerd_mesh
    )
except ImportError:
    LinkerdServiceMesh = LinkerdConfiguration = LinkerdProfile = None
    LinkerdTrafficSplit = linkerd_mesh = None

try:
    from .service_mesh_security import (
        ServiceMeshSecurity, MutualTLS, ServiceMeshRBAC,
        SecurityPolicy, mesh_security
    )
except ImportError:
    ServiceMeshSecurity = MutualTLS = ServiceMeshRBAC = None
    SecurityPolicy = mesh_security = None

try:
    from .load_balancing import (
        ServiceMeshLoadBalancer, LoadBalancingStrategy, HealthChecker,
        TrafficDistributor, load_balancer
    )
except ImportError:
    ServiceMeshLoadBalancer = LoadBalancingStrategy = HealthChecker = None
    TrafficDistributor = load_balancer = None

try:
    from .circuit_breaker import (
        CircuitBreaker, CircuitBreakerConfig, FailureDetector,
        RecoveryManager, circuit_breaker
    )
except ImportError:
    CircuitBreaker = CircuitBreakerConfig = FailureDetector = None
    RecoveryManager = circuit_breaker = None

try:
    from .service_discovery import (
        ServiceDiscovery, ServiceRegistry, ServiceEndpoint,
        DiscoveryAgent, service_discovery
    )
except ImportError:
    ServiceDiscovery = ServiceRegistry = ServiceEndpoint = None
    DiscoveryAgent = service_discovery = None

try:
    from .traffic_management import (
        TrafficManager, RoutingRule, TrafficPolicy,
        CanaryDeployment, traffic_manager
    )
except ImportError:
    TrafficManager = RoutingRule = TrafficPolicy = None
    CanaryDeployment = traffic_manager = None

try:
    from .observability_mesh import (
        MeshObservability, DistributedTracing, MetricsCollector,
        LoggingAggregator, mesh_observability
    )
except ImportError:
    MeshObservability = DistributedTracing = MetricsCollector = None
    LoggingAggregator = mesh_observability = None

try:
    from .policy_management import (
        PolicyManager, AccessPolicy, RateLimitPolicy,
        SecurityPolicy, policy_manager
    )
except ImportError:
    PolicyManager = AccessPolicy = RateLimitPolicy = None
    SecurityPolicy = policy_manager = None

# Service Mesh Global Configuration
SERVICE_MESH_CONFIG = {
    'default_mesh': 'istio',
    'fallback_mesh': 'linkerd',
    'security_enabled': True,
    'mtls_enabled': True,
    'observability_enabled': True,
    'load_balancing_strategy': 'round_robin',
    'circuit_breaker_enabled': True,
    'service_discovery_enabled': True,
    'traffic_management_enabled': True
}

# Ainflue Microservices Registry
AINFLUE_SERVICES = {
    'ai_optimization': {
        'port': 8001,
        'health_endpoint': '/health',
        'dependencies': ['external_integrations', 'storage_modules']
    },
    'external_integrations': {
        'port': 8002,
        'health_endpoint': '/health',
        'dependencies': ['security_modules', 'storage_modules']
    },
    'content_protection': {
        'port': 8003,
        'health_endpoint': '/health',
        'dependencies': ['ai_optimization', 'external_integrations']
    },
    'monetization_engine': {
        'port': 8004,
        'health_endpoint': '/health',
        'dependencies': ['ai_optimization', 'external_integrations']
    },
    'collaboration_platform': {
        'port': 8005,
        'health_endpoint': '/health',
        'dependencies': ['ai_optimization', 'gamification_engine']
    },
    'gamification_engine': {
        'port': 8006,
        'health_endpoint': '/health',
        'dependencies': ['collaboration_platform', 'storage_modules']
    },
    'api_gateway': {
        'port': 8000,
        'health_endpoint': '/health',
        'dependencies': []  # Gateway has no dependencies
    }
}

__all__ = [
    # Istio Integration
    'IstioServiceMesh',
    'IstioConfiguration', 
    'IstioGateway',
    'IstioVirtualService',
    'IstioDestinationRule',
    'istio_mesh',
    
    # Linkerd Integration
    'LinkerdServiceMesh',
    'LinkerdConfiguration',
    'LinkerdProfile', 
    'LinkerdTrafficSplit',
    'linkerd_mesh',
    
    # Security
    'ServiceMeshSecurity',
    'MutualTLS',
    'ServiceMeshRBAC',
    'SecurityPolicy',
    'mesh_security',
    
    # Load Balancing
    'ServiceMeshLoadBalancer',
    'LoadBalancingStrategy',
    'HealthChecker',
    'TrafficDistributor',
    'load_balancer',
    
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerConfig',
    'FailureDetector',
    'RecoveryManager',
    'circuit_breaker',
    
    # Service Discovery
    'ServiceDiscovery',
    'ServiceRegistry',
    'ServiceEndpoint',
    'DiscoveryAgent',
    'service_discovery',
    
    # Traffic Management
    'TrafficManager',
    'RoutingRule',
    'TrafficPolicy',
    'CanaryDeployment',
    'traffic_manager',
    
    # Observability
    'MeshObservability',
    'DistributedTracing',
    'MetricsCollector',
    'LoggingAggregator',
    'mesh_observability',
    
    # Policy Management
    'PolicyManager',
    'AccessPolicy',
    'RateLimitPolicy',
    'policy_manager',
    
    # Configuration
    'SERVICE_MESH_CONFIG',
    'AINFLUE_SERVICES'
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Service Mesh Infrastructure for Ainflue Microservices"