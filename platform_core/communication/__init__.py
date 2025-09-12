"""🚀 Platform Core Communication System - IA Influencer Agent Platform Enterprise
==============================================================================
Module: backend/platform_core/communication/
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME DE COMMUNICATION INTER-SERVICES
Communication WebSocket et REST API pour coordination des microservices
- WebSocket real-time pour notifications instantanées
- REST API pour communication synchrone
- Message queue pour communication asynchrone
- Load balancing et failover automatique
"""

# Import existing modules with error handling
__all__ = []

try:
    from .websocket_manager import WebSocketManager, ConnectionManager
    __all__.extend(["WebSocketManager", "ConnectionManager"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: WebSocket manager not available: {e}")

try:
    from .rest_client import RestClient, ServiceRegistry
    __all__.extend(["RestClient", "ServiceRegistry"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: REST client not available: {e}")

try:
    from .message_queue import MessageQueue, QueueManager
    __all__.extend(["MessageQueue", "QueueManager"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Message queue not available: {e}")

try:
    from .load_balancer import LoadBalancer, HealthChecker
    __all__.extend(["LoadBalancer", "HealthChecker"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Load balancer not available: {e}")

try:
    from .event_bus import EventBus, EventHandler
    __all__.extend(["EventBus", "EventHandler"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Event bus not available: {e}")

try:
    from .service_mesh import ServiceMesh, ServiceDiscovery
    __all__.extend(["ServiceMesh", "ServiceDiscovery"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Service mesh not available: {e}")

# Import new modules
try:
    from .message_broker_orchestrator import message_broker_orchestrator, MessageBrokerOrchestrator
    __all__.extend(["message_broker_orchestrator", "MessageBrokerOrchestrator"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Message broker orchestrator not available: {e}")

try:
    from .communication_protocol_manager import communication_protocol_manager, CommunicationProtocolManager
    __all__.extend(["communication_protocol_manager", "CommunicationProtocolManager"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Communication protocol manager not available: {e}")

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
