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

try:
    from .communication_security_manager import CommunicationSecurityManager, SecurityPolicy
    __all__.extend(["CommunicationSecurityManager", "SecurityPolicy"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Communication security manager not available: {e}")

try:
    from .communication_analytics import CommunicationAnalytics, AnalyticsMetrics
    __all__.extend(["CommunicationAnalytics", "AnalyticsMetrics"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Communication analytics not available: {e}")

try:
    from .real_time_streaming_engine import RealTimeStreamingEngine, StreamProcessor
    __all__.extend(["RealTimeStreamingEngine", "StreamProcessor"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Real time streaming engine not available: {e}")

try:
    from .event_sourcing_manager import EventSourcingManager, EventStore
    __all__.extend(["EventSourcingManager", "EventStore"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Event sourcing manager not available: {e}")

# New enterprise modules
try:
    from .push_notification_manager import PushNotificationManager, NotificationTarget, NotificationTemplate
    __all__.extend(["PushNotificationManager", "NotificationTarget", "NotificationTemplate"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Push notification manager not available: {e}")

try:
    from .voice_communication_engine import VoiceCommunicationEngine, CallSession, CallParticipant
    __all__.extend(["VoiceCommunicationEngine", "CallSession", "CallParticipant"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Voice communication engine not available: {e}")

try:
    from .chat_moderation_system import ChatModerationSystem, ModerationResult, UserReputation
    __all__.extend(["ChatModerationSystem", "ModerationResult", "UserReputation"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Chat moderation system not available: {e}")

try:
    from .collaboration_communication_hub import CollaborationCommunicationHub, CollaborationProject, CommunicationChannel
    __all__.extend(["CollaborationCommunicationHub", "CollaborationProject", "CommunicationChannel"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Collaboration communication hub not available: {e}")

try:
    from .communication_rate_limiter import CommunicationRateLimiter, RateLimitRequest, RateLimitResponse
    __all__.extend(["CommunicationRateLimiter", "RateLimitRequest", "RateLimitResponse"])
except (ImportError, SyntaxError) as e:
    print(f"Warning: Communication rate limiter not available: {e}")

__version__ = "3.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
