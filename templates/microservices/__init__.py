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

# All other template categories are TODO - commenting out for now
# Discovery Templates
# from .discovery import (...)

# Monitoring Templates  
# from .monitoring import (...)

# Security Templates
# from .security import (...)

# Data Templates
# from .data import (...)

# Performance Templates
# from .performance import (...)

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
]