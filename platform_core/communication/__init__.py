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

from .websocket_manager import WebSocketManager, ConnectionManager
from .rest_client import RestClient, ServiceRegistry
from .message_queue import MessageQueue, QueueManager
from .load_balancer import LoadBalancer, HealthChecker
from .event_bus import EventBus, EventHandler
from .service_mesh import ServiceMesh, ServiceDiscovery

__all__ = [
    "WebSocketManager",
    "ConnectionManager", 
    "RestClient",
    "ServiceRegistry",
    "MessageQueue",
    "QueueManager",
    "LoadBalancer",
    "HealthChecker",
    "EventBus",
    "EventHandler",
    "ServiceMesh",
    "ServiceDiscovery"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
