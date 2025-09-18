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

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Microservices Templates Module for Ainflue Platform
==================================================

Enterprise-grade microservices templates providing comprehensive patterns for:
- Service architecture templates
- Communication patterns
- Event-driven architecture
- Circuit breaker patterns
- Service discovery
- Monitoring and observability
- Security and authentication
- Data management
- Performance optimization
- Deployment automation

Author: Fahed Mlaiel (mlaiel@live.de)
Technical Lead & Microservices Architect
"""

from .microservice_template import (
    ServiceStatus,
    MessageType,
    ServiceMessage,
    ServiceConfig,
    HealthStatus
)

from .base_microservice import BaseMicroservice
from .service_factory import ServiceFactory
from .communication_manager import CommunicationManager
from .discovery_client import DiscoveryClient
from .circuit_breaker import CircuitBreaker
from .metrics_collector import MetricsCollector
from .health_checker import HealthChecker
from .config_manager import ConfigManager
from .security_manager import SecurityManager
from .message_broker import MessageBroker
from .event_dispatcher import EventDispatcher
from .saga_coordinator import SagaCoordinator
from .service_registry import ServiceRegistry
from .load_balancer import LoadBalancer
from .performance_monitor import PerformanceMonitor
from .deployment_manager import DeploymentManager
from .testing_framework import TestingFramework

# Core Service Templates
from .core_services import (
    RestApiTemplate,
    GraphqlApiTemplate,
    GrpcServiceTemplate,
    WebsocketServiceTemplate,
    BackgroundWorkerTemplate,
    CronJobTemplate,
    EventProcessorTemplate,
    DataPipelineTemplate
)

# Communication Templates
from .communication import (
    MessageQueueTemplate,
    EventBusTemplate,
    SagaOrchestratorTemplate,
    CircuitBreakerTemplate,
    ApiGatewayTemplate,
    ServiceMeshTemplate,
    LoadBalancerTemplate,
    RateLimiterTemplate
)

# Discovery Templates
from .discovery import (
    ServiceRegistryTemplate,
    ServiceDiscoveryTemplate,
    ConsulIntegrationTemplate,
    EtcdIntegrationTemplate,
    EurekaIntegrationTemplate,
    KubernetesDiscoveryTemplate,
    DnsDiscoveryTemplate,
    HealthCheckTemplate
)

# Monitoring Templates
from .monitoring import (
    MetricsCollectorTemplate,
    TracingInterceptorTemplate,
    LoggingHandlerTemplate,
    AlertManagerTemplate,
    DashboardExporterTemplate,
    PerformanceProfilerTemplate,
    ErrorTrackerTemplate,
    AuditLoggerTemplate
)

# Security Templates
from .security import (
    JwtAuthTemplate,
    Oauth2ServiceTemplate,
    RbacMiddlewareTemplate,
    EncryptionServiceTemplate,
    KeyManagementTemplate,
    SecurityGatewayTemplate,
    AuditServiceTemplate,
    ComplianceCheckerTemplate
)

# Data Templates
from .data import (
    DatabaseServiceTemplate,
    CacheServiceTemplate,
    SearchServiceTemplate,
    FileStorageTemplate,
    BackupServiceTemplate,
    DataSyncTemplate,
    MigrationServiceTemplate,
    ReplicationTemplate
)

# Creator Economy Templates
from .creator_economy import (
    CreatorServiceTemplate,
    ContentProcessingTemplate,
    CollaborationServiceTemplate,
    MonetizationServiceTemplate,
    AnalyticsServiceTemplate,
    DistributionServiceTemplate,
    SeoServiceTemplate,
    GamificationServiceTemplate
)

# Performance Templates
from .performance import (
    CachingStrategyTemplate,
    ConnectionPoolTemplate,
    AsyncProcessorTemplate,
    BatchProcessorTemplate,
    StreamProcessorTemplate,
    MemoryOptimizerTemplate,
    CpuOptimizerTemplate,
    IoOptimizerTemplate
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core Classes
    "ServiceStatus",
    "MessageType", 
    "ServiceMessage",
    "ServiceConfig",
    "HealthStatus",
    
    # Infrastructure Components
    "BaseMicroservice",
    "ServiceFactory",
    "CommunicationManager",
    "DiscoveryClient",
    "CircuitBreaker",
    "MetricsCollector",
    "HealthChecker",
    "ConfigManager",
    "SecurityManager",
    "MessageBroker",
    "EventDispatcher",
    "SagaCoordinator",
    "ServiceRegistry",
    "LoadBalancer",
    "PerformanceMonitor",
    "DeploymentManager",
    "TestingFramework",
    
    # Core Service Templates
    "RestApiTemplate",
    "GraphqlApiTemplate", 
    "GrpcServiceTemplate",
    "WebsocketServiceTemplate",
    "BackgroundWorkerTemplate",
    "CronJobTemplate",
    "EventProcessorTemplate",
    "DataPipelineTemplate",
    
    # Communication Templates
    "MessageQueueTemplate",
    "EventBusTemplate",
    "SagaOrchestratorTemplate",
    "CircuitBreakerTemplate",
    "ApiGatewayTemplate",
    "ServiceMeshTemplate",
    "LoadBalancerTemplate",
    "RateLimiterTemplate",
    
    # Discovery Templates
    "ServiceRegistryTemplate",
    "ServiceDiscoveryTemplate",
    "ConsulIntegrationTemplate",
    "EtcdIntegrationTemplate",
    "EurekaIntegrationTemplate",
    "KubernetesDiscoveryTemplate",
    "DnsDiscoveryTemplate",
    "HealthCheckTemplate",
    
    # Monitoring Templates
    "MetricsCollectorTemplate",
    "TracingInterceptorTemplate",
    "LoggingHandlerTemplate",
    "AlertManagerTemplate",
    "DashboardExporterTemplate",
    "PerformanceProfilerTemplate",
    "ErrorTrackerTemplate",
    "AuditLoggerTemplate",
    
    # Security Templates
    "JwtAuthTemplate",
    "Oauth2ServiceTemplate",
    "RbacMiddlewareTemplate",
    "EncryptionServiceTemplate",
    "KeyManagementTemplate",
    "SecurityGatewayTemplate",
    "AuditServiceTemplate",
    "ComplianceCheckerTemplate",
    
    # Data Templates
    "DatabaseServiceTemplate",
    "CacheServiceTemplate", 
    "SearchServiceTemplate",
    "FileStorageTemplate",
    "BackupServiceTemplate",
    "DataSyncTemplate",
    "MigrationServiceTemplate",
    "ReplicationTemplate",
    
    # Creator Economy Templates
    "CreatorServiceTemplate",
    "ContentProcessingTemplate",
    "CollaborationServiceTemplate",
    "MonetizationServiceTemplate",
    "AnalyticsServiceTemplate",
    "DistributionServiceTemplate",
    "SeoServiceTemplate",
    "GamificationServiceTemplate",
    
    # Performance Templates
    "CachingStrategyTemplate",
    "ConnectionPoolTemplate",
    "AsyncProcessorTemplate",
    "BatchProcessorTemplate",
    "StreamProcessorTemplate",
    "MemoryOptimizerTemplate",
    "CpuOptimizerTemplate",
    "IoOptimizerTemplate"
]