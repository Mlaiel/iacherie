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
    HealthStatus,
    BaseMicroserviceTemplate
)

# Core infrastructure components (existing)
from .base_microservice import BaseMicroservice
from .service_factory import ServiceFactory
from .communication_manager import CommunicationManager
from .circuit_breaker import CircuitBreaker
from .metrics_collector import MetricsCollector

# Service templates modules
from . import core_services
from . import communication
from . import creator_economy
from . import discovery_registry
from . import monitoring

# Core Service Templates (existing)
from .core_services import (
    RestApiTemplate,
    GraphqlApiTemplate,
    GrpcServiceTemplate,
    WebsocketServiceTemplate,
    BackgroundWorkerTemplate,
    # CronJobTemplate,  # TODO: Implement
    # EventProcessorTemplate,  # TODO: Implement
    # DataPipelineTemplate  # TODO: Implement
)

# Communication Templates (partially implemented)
from .communication import (
    MessageQueueTemplate,
    EventBusTemplate,
    # SagaOrchestratorTemplate,  # TODO: Complete implementation
    # CircuitBreakerTemplate,  # TODO: Complete implementation
    ApiGatewayTemplate,
    # ServiceMeshTemplate,  # TODO: Complete implementation
    # LoadBalancerTemplate,  # TODO: Complete implementation
    # RateLimiterTemplate  # TODO: Complete implementation
)

# Creator Economy Templates (partially implemented)
from .creator_economy import (
    CreatorServiceTemplate,
    # ContentProcessingTemplate,  # TODO: Implement
    # CollaborationServiceTemplate,  # TODO: Implement
    # MonetizationServiceTemplate,  # TODO: Implement
    # AnalyticsServiceTemplate,  # TODO: Implement
    # DistributionServiceTemplate,  # TODO: Implement
    # SeoServiceTemplate,  # TODO: Implement
    # GamificationServiceTemplate  # TODO: Implement
)

# Performance Templates (newly implemented)
from . import performance
from .performance import (
    CachingStrategyTemplate,
    ConnectionPoolTemplate,
    AsyncProcessorTemplate,
    BatchProcessorTemplate,
    StreamProcessorTemplate,
    MemoryOptimizerTemplate,
    CPUOptimizerTemplate,
    IOOptimizerTemplate
)

# Deployment Templates (newly implemented)
from . import deployment
from .deployment import (
    KubernetesDeploymentTemplate,
    DockerComposeTemplate,
    HelmChartTemplate,
    TerraformTemplate,
    AnsiblePlaybookTemplate,
    CICDPipelineTemplate,
    BlueGreenDeploymentTemplate,
    CanaryDeploymentTemplate
)

# Testing Templates (newly implemented)
from . import testing
from .testing import (
    UnitTestTemplate,
    IntegrationTestTemplate,
    ContractTestTemplate,
    LoadTestTemplate,
    ChaosTestTemplate,
    SecurityTestTemplate,
    PerformanceTestTemplate,
    E2ETestTemplate
)

# Configuration Templates (newly implemented)
from . import configuration
from .configuration import (
    EnvironmentConfigTemplate,
    FeatureFlagTemplate,
    SecretsManagerTemplate,
    ConfigServerTemplate,
    VaultIntegrationTemplate,
    ConsulConfigTemplate,
    K8sConfigMapTemplate,
    HelmValuesTemplate
)

# Scaling Templates (newly implemented)
from . import scaling
from .scaling import (
    HorizontalScalerTemplate,
    VerticalScalerTemplate,
    AutoScalerTemplate,
    LoadBalancerTemplate,
    ClusterManagerTemplate,
    ResourceManagerTemplate,
    CapacityPlannerTemplate,
    CostOptimizerTemplate
)

# Resilience Templates (newly implemented)
from . import resilience
from .resilience import (
    RetryPolicyTemplate,
    TimeoutHandlerTemplate,
    BulkheadPatternTemplate,
    FallbackHandlerTemplate,
    HealthCircuitTemplate,
    GracefulShutdownTemplate,
    DisasterRecoveryTemplate,
    FailoverTemplate
)

# Documentation Templates (newly implemented)
from . import documentation
from .documentation import (
    APIDocumentationTemplate,
    SwaggerGeneratorTemplate,
    OpenAPISpecTemplate,
    ServiceCatalogTemplate,
    ArchitectureDiagramTemplate,
    RunbookTemplate,
    TroubleshootingGuideTemplate,
    DeploymentGuideTemplate
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
    "BaseMicroserviceTemplate",
    
    # Infrastructure Components (existing)
    "BaseMicroservice",
    "ServiceFactory",
    "CommunicationManager",
    "CircuitBreaker",
    "MetricsCollector",
    
    # Core Service Templates (existing)
    "RestApiTemplate",
    "GraphqlApiTemplate", 
    "GrpcServiceTemplate",
    "WebsocketServiceTemplate",
    "BackgroundWorkerTemplate",
    
    # Communication Templates (partially implemented)
    "MessageQueueTemplate",
    "EventBusTemplate",
    "ApiGatewayTemplate",
    
    # Creator Economy Templates (partially implemented)
    "CreatorServiceTemplate",
    
    # Performance Templates (newly implemented)
    "CachingStrategyTemplate",
    "ConnectionPoolTemplate", 
    "AsyncProcessorTemplate",
    "BatchProcessorTemplate",
    "StreamProcessorTemplate",
    "MemoryOptimizerTemplate",
    "CPUOptimizerTemplate",
    "IOOptimizerTemplate",
    
    # Deployment Templates (newly implemented)
    "KubernetesDeploymentTemplate",
    "DockerComposeTemplate",
    "HelmChartTemplate",
    "TerraformTemplate",
    "AnsiblePlaybookTemplate", 
    "CICDPipelineTemplate",
    "BlueGreenDeploymentTemplate",
    "CanaryDeploymentTemplate",
    
    # Testing Templates (newly implemented)
    "UnitTestTemplate",
    "IntegrationTestTemplate",
    "ContractTestTemplate",
    "LoadTestTemplate",
    "ChaosTestTemplate",
    "SecurityTestTemplate",
    "PerformanceTestTemplate",
    "E2ETestTemplate",
    
    # Configuration Templates (newly implemented)
    "EnvironmentConfigTemplate",
    "FeatureFlagTemplate",
    "SecretsManagerTemplate",
    "ConfigServerTemplate",
    "VaultIntegrationTemplate",
    "ConsulConfigTemplate",
    "K8sConfigMapTemplate",
    "HelmValuesTemplate",
    
    # Scaling Templates (newly implemented)
    "HorizontalScalerTemplate",
    "VerticalScalerTemplate",
    "AutoScalerTemplate",
    "LoadBalancerTemplate",
    "ClusterManagerTemplate",
    "ResourceManagerTemplate",
    "CapacityPlannerTemplate",
    "CostOptimizerTemplate",
    
    # Resilience Templates (newly implemented)
    "RetryPolicyTemplate",
    "TimeoutHandlerTemplate",
    "BulkheadPatternTemplate",
    "FallbackHandlerTemplate",
    "HealthCircuitTemplate",
    "GracefulShutdownTemplate",
    "DisasterRecoveryTemplate",
    "FailoverTemplate",
    
    # Documentation Templates (newly implemented)
    "APIDocumentationTemplate",
    "SwaggerGeneratorTemplate",
    "OpenAPISpecTemplate",
    "ServiceCatalogTemplate",
    "ArchitectureDiagramTemplate",
    "RunbookTemplate",
    "TroubleshootingGuideTemplate",
    "DeploymentGuideTemplate",
]