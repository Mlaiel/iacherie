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

Communication Templates Module for Ainflue Microservices
======================================================

Enterprise-grade communication patterns for microservices:
- Message Queue Templates
- Event Bus Templates  
- Saga Orchestrator Templates
- Circuit Breaker Templates
- API Gateway Templates
- Service Mesh Templates
- Load Balancer Templates
- Rate Limiter Templates

Author: Fahed Mlaiel (mlaiel@live.de)
Microservices Communication Expert
"""

from .message_queue_template import MessageQueueTemplate
from .event_bus_template import EventBusTemplate
from .saga_orchestrator_template import SagaOrchestratorTemplate
from .circuit_breaker_template import CircuitBreakerTemplate
from .api_gateway_template import ApiGatewayTemplate
from .service_mesh_template import ServiceMeshTemplate
from .load_balancer_template import LoadBalancerTemplate
from .rate_limiter_template import RateLimiterTemplate

__all__ = [
    "MessageQueueTemplate",
    "EventBusTemplate",
    "SagaOrchestratorTemplate", 
    "CircuitBreakerTemplate",
    "ApiGatewayTemplate",
    "ServiceMeshTemplate",
    "LoadBalancerTemplate",
    "RateLimiterTemplate"
]