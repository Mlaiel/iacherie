"""Real-Time Communication Database Module

Enterprise real-time communication infrastructure for creator collaboration,
live streaming coordination, and instant messaging with WebSocket management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""from .websocket_manager import WebSocketManager, ConnectionPool
from .message_broker import MessageBroker, MessageQueue, get_message_broker
from .notification_engine import NotificationEngine, NotificationChannel
from .live_collaboration import LiveCollaboration, CollaborationRoom, get_live_collaboration
from .streaming_coordinator import StreamingCoordinator, StreamSession, get_streaming_coordinator
from .realtime_sync import RealtimeSyncManager, get_realtime_sync_manager
from .cross_platform_bridge import CrossPlatformBridge, get_cross_platform_bridge
from .communication_analytics import CommunicationAnalyticsEngine, get_communication_analytics_engine
from .index import (
    CommunicationService,
    get_communication_service,
    create_websocket_manager,
    create_message_broker,
    create_notification_engine,
    create_live_collaboration,
    create_streaming_coordinator,
    create_realtime_sync_manager,
    create_cross_platform_bridge,
    create_communication_analytics_engine,
    send_notification_to_creators,
    create_collaboration_room_for_creators,
    start_multi_platform_stream,
    sync_content_across_platforms,
    track_communication_analytics
)

__all__ = [
    # Core service
    "CommunicationService",
    "get_communication_service",
    
    # Individual components
    "WebSocketManager",
    "ConnectionPool",
    "MessageBroker", 
    "MessageQueue",
    "NotificationEngine",
    "NotificationChannel",
    "LiveCollaboration",
    "CollaborationRoom",
    "StreamingCoordinator",
    "StreamSession",
    "RealtimeSyncManager",
    "CrossPlatformBridge",
    "CommunicationAnalyticsEngine",
    
    # Context managers
    "get_message_broker",
    "get_live_collaboration",
    "get_streaming_coordinator",
    "get_realtime_sync_manager",
    "get_cross_platform_bridge", 
    "get_communication_analytics_engine",
    
    # Factory functions
    "create_websocket_manager",
    "create_message_broker",
    "create_notification_engine",
    "create_live_collaboration",
    "create_streaming_coordinator",
    "create_realtime_sync_manager",
    "create_cross_platform_bridge",
    "create_communication_analytics_engine",
    
    # Business functions
    "send_notification_to_creators",
    "create_collaboration_room_for_creators",
    "start_multi_platform_stream",
    "sync_content_across_platforms",
    "track_communication_analytics"
]
    "create_streaming_coordinator",
    
    # Utility functions
    "send_notification_to_creators",
    "create_collaboration_room_for_creators",
    "start_multi_platform_stream"
]
