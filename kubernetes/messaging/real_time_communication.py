"""
IA Influencer Agent - Real-time Communication Manager
Enterprise real-time messaging for live notifications and WebSocket communication

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

STRICT WARNING: This code is proprietary and confidential.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Legal action will be taken against violators.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + DevOps 
- Audio Processing + Security + Microservices + IA Prompt Engineering
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Union

import aioredis
import socketio
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...core.logging import get_logger
from ...security.auth import verify_websocket_token

logger = get_logger(__name__)
settings = get_settings()


class WebSocketConnection(BaseModel):
    """WebSocket connection information"""
    id: str = Field(..., description="Connection ID")
    user_id: str = Field(..., description="User ID")
    websocket: Any = Field(..., description="WebSocket instance")
    connected_at: float = Field(default_factory=time.time, description="Connection timestamp")
    last_heartbeat: float = Field(default_factory=time.time, description="Last heartbeat")
    subscriptions: Set[str] = Field(default_factory=set, description="Channel subscriptions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Connection metadata")


class NotificationChannel(str, Enum):
    """Notification channel types"""
    CONTENT_ALERTS = "content.alerts"
    PROTECTION_VIOLATIONS = "protection.violations"
    AI_PROCESSING = "ai.processing"
    REVENUE_UPDATES = "revenue.updates"
    SYSTEM_NOTIFICATIONS = "system.notifications"
    CRAWLING_ALERTS = "crawling.alerts"
    COLLABORATION_INVITES = "collaboration.invites"
    PAYMENT_NOTIFICATIONS = "payment.notifications"


class RealTimeMessage(BaseModel):
    """Real-time message format"""
    id: str = Field(..., description="Message ID")
    channel: NotificationChannel = Field(..., description="Notification channel")
    type: str = Field(..., description="Message type")
    title: str = Field(..., description="Message title")
    content: str = Field(..., description="Message content")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Additional data")
    priority: str = Field(default="medium", description="Message priority")
    timestamp: float = Field(default_factory=time.time, description="Message timestamp")
    expires_at: Optional[float] = Field(None, description="Message expiration")
    read_receipt: bool = Field(default=False, description="Require read receipt")


class RealTimeCommunicationManager:
    """
    Enterprise real-time communication manager
    Handles WebSocket connections, notifications, and live updates
    """

    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> connection_ids
        self.channel_subscribers: Dict[str, Set[str]] = {}  # channel -> connection_ids
        
        # Redis for distributed messaging
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Socket.IO server for advanced features
        self.sio_server = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=logger,
            engineio_logger=logger
        )
        
        # Setup Socket.IO event handlers
        self._setup_socketio_handlers()
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []

    async def initialize(self) -> None:
        """Initialize real-time communication manager"""



        try:
            # Setup Redis connection
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("Real-time communication manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize real-time communication: {e}")
            raise

    def _setup_socketio_handlers(self) -> None:
        """Setup Socket.IO event handlers"""
        
        @self.sio_server.event
        async def connect(sid: str, environ: Dict[str, Any], auth: Dict[str, Any]):
            """Handle Socket.IO connection"""



            try:
                # Verify authentication
                token = auth.get("token")
                if not token:
                    await self.sio_server.disconnect(sid)
                    return False
                    
                user_data = verify_websocket_token(token)
                if not user_data:
                    await self.sio_server.disconnect(sid)
                    return False
                
                # Store connection info
                await self.sio_server.save_session(sid, {
                    "user_id": user_data["user_id"],
                    "username": user_data.get("username"),
                    "connected_at": time.time()
                })
                
                # Join user-specific room
                await self.sio_server.enter_room(sid, f"user_{user_data['user_id']}")
                
                # Send welcome message
                await self.sio_server.emit("connected", {
                    "message": "Connected to IA Influencer Agent real-time notifications",
                    "timestamp": time.time()
                }, room=sid)
                
                logger.info(f"Socket.IO client {sid} connected for user {user_data['user_id']}")
                return True
                
            except Exception as e:
                logger.error(f"Socket.IO connection error: {e}")
                await self.sio_server.disconnect(sid)
                return False

        @self.sio_server.event
        async def disconnect(sid: str):
            """Handle Socket.IO disconnection"""



            try:
                session = await self.sio_server.get_session(sid)
                user_id = session.get("user_id")
                
                logger.info(f"Socket.IO client {sid} disconnected for user {user_id}")
                
            except Exception as e:
                logger.error(f"Socket.IO disconnection error: {e}")

        @self.sio_server.event
        async def subscribe_channel(sid: str, data: Dict[str, Any]):
            """Subscribe to notification channel"""



            try:
                channel = data.get("channel")
                if not channel or channel not in NotificationChannel:
                    await self.sio_server.emit("error", {
                        "message": "Invalid channel"
                    }, room=sid)
                    return
                
                # Join channel room
                await self.sio_server.enter_room(sid, f"channel_{channel}")
                
                await self.sio_server.emit("subscribed", {
                    "channel": channel,
                    "timestamp": time.time()
                }, room=sid)
                
                logger.debug(f"Client {sid} subscribed to channel {channel}")
                
            except Exception as e:
                logger.error(f"Channel subscription error: {e}")

        @self.sio_server.event
        async def unsubscribe_channel(sid: str, data: Dict[str, Any]):
            """Unsubscribe from notification channel"""



            try:
                channel = data.get("channel")
                if not channel:
                    return
                
                # Leave channel room
                await self.sio_server.leave_room(sid, f"channel_{channel}")
                
                await self.sio_server.emit("unsubscribed", {
                    "channel": channel,
                    "timestamp": time.time()
                }, room=sid)
                
                logger.debug(f"Client {sid} unsubscribed from channel {channel}")
                
            except Exception as e:
                logger.error(f"Channel unsubscription error: {e}")

        @self.sio_server.event
        async def heartbeat(sid: str):
            """Handle heartbeat ping"""
            await self.sio_server.emit("heartbeat_ack", {"timestamp": time.time()}, room=sid)

    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str) -> None:
        """Handle raw WebSocket connection"""



        try:
            await websocket.accept()
            
            connection_id = f"ws_{user_id}_{int(time.time())}"
            connection = WebSocketConnection(
                id=connection_id,
                user_id=user_id,
                websocket=websocket,
                metadata={"type": "websocket"}
            )
            
            # Store connection
            self.connections[connection_id] = connection
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(connection_id)
            
            # Send welcome message
            await self.send_to_connection(connection_id, {
                "type": "welcome",
                "message": "Connected to IA Influencer Agent",
                "timestamp": time.time()
            })
            
            # Handle messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_websocket_message(connection_id, message)
                    
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"WebSocket message error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            await self._cleanup_websocket_connection(connection_id)

    async def _handle_websocket_message(self, connection_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming WebSocket message"""



        try:
            message_type = message.get("type")
            
            if message_type == "subscribe":
                channel = message.get("channel")
                await self._subscribe_connection_to_channel(connection_id, channel)
                
            elif message_type == "unsubscribe":
                channel = message.get("channel")
                await self._unsubscribe_connection_from_channel(connection_id, channel)
                
            elif message_type == "heartbeat":
                connection = self.connections.get(connection_id)
                if connection:
                    connection.last_heartbeat = time.time()
                    await self.send_to_connection(connection_id, {
                        "type": "heartbeat_ack",
                        "timestamp": time.time()
                    })
                    
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def _subscribe_connection_to_channel(self, connection_id: str, channel: str) -> None:
        """Subscribe connection to notification channel"""



        try:
            if channel not in NotificationChannel:
                await self.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Invalid channel"
                })
                return
            
            # Add to channel subscribers
            if channel not in self.channel_subscribers:
                self.channel_subscribers[channel] = set()
            self.channel_subscribers[channel].add(connection_id)
            
            # Update connection subscriptions
            connection = self.connections.get(connection_id)
            if connection:
                connection.subscriptions.add(channel)
            
            await self.send_to_connection(connection_id, {
                "type": "subscribed",
                "channel": channel,
                "timestamp": time.time()
            })
            
            logger.debug(f"Connection {connection_id} subscribed to {channel}")
            
        except Exception as e:
            logger.error(f"Subscription error: {e}")

    async def _unsubscribe_connection_from_channel(self, connection_id: str, channel: str) -> None:
        """Unsubscribe connection from notification channel"""



        try:
            # Remove from channel subscribers
            if channel in self.channel_subscribers:
                self.channel_subscribers[channel].discard(connection_id)
            
            # Update connection subscriptions
            connection = self.connections.get(connection_id)
            if connection:
                connection.subscriptions.discard(channel)
            
            await self.send_to_connection(connection_id, {
                "type": "unsubscribed",
                "channel": channel,
                "timestamp": time.time()
            })
            
            logger.debug(f"Connection {connection_id} unsubscribed from {channel}")
            
        except Exception as e:
            logger.error(f"Unsubscription error: {e}")

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific connection"""



        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return False
            
            # WebSocket connection
            if hasattr(connection.websocket, 'send_text'):
                await connection.websocket.send_text(json.dumps(message))
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending to connection {connection_id}: {e}")
            # Connection likely broken, clean up
            await self._cleanup_websocket_connection(connection_id)
            return False

    async def send_to_user(self, user_id: str, message: RealTimeMessage) -> int:
        """Send message to all connections of a user"""



        try:
            connections = self.user_connections.get(user_id, [])
            sent_count = 0
            
            # Send to WebSocket connections
            for connection_id in connections:
                if await self.send_to_connection(connection_id, message.dict()):
                    sent_count += 1
            
            # Send via Socket.IO
            await self.sio_server.emit(
                "notification",
                message.dict(),
                room=f"user_{user_id}"
            )
            
            # Store in Redis for offline delivery
            if self.redis_client:
                await self.redis_client.lpush(
                    f"notifications:{user_id}",
                    json.dumps(message.dict())
                )
                await self.redis_client.expire(f"notifications:{user_id}", 604800)  # 7 days
            
            logger.debug(f"Sent message to user {user_id} via {sent_count} connections")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending to user {user_id}: {e}")
            return 0

    async def broadcast_to_channel(self, channel: NotificationChannel, message: RealTimeMessage) -> int:
        """Broadcast message to all subscribers of a channel"""



        try:
            subscribers = self.channel_subscribers.get(channel, set())
            sent_count = 0
            
            # Send to WebSocket subscribers
            for connection_id in subscribers:
                if await self.send_to_connection(connection_id, message.dict()):
                    sent_count += 1
            
            # Broadcast via Socket.IO
            await self.sio_server.emit(
                "channel_notification",
                message.dict(),
                room=f"channel_{channel}"
            )
            
            logger.info(f"Broadcasted to channel {channel}, reached {sent_count} WebSocket connections")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error broadcasting to channel {channel}: {e}")
            return 0

    async def send_content_protection_alert(self, user_id: str, violation_data: Dict[str, Any]) -> None:
        """Send content protection violation alert"""



        try:
            message = RealTimeMessage(
                id=f"protection_alert_{int(time.time())}",
                channel=NotificationChannel.PROTECTION_VIOLATIONS,
                type="violation_detected",
                title="Content Protection Alert",
                content=f"Potential violation detected on {violation_data.get('platform', 'unknown platform')}",
                payload=violation_data,
                priority="high"
            )
            
            await self.send_to_user(user_id, message)
            await self.broadcast_to_channel(NotificationChannel.PROTECTION_VIOLATIONS, message)
            
        except Exception as e:
            logger.error(f"Error sending protection alert: {e}")

    async def send_ai_processing_update(self, user_id: str, processing_data: Dict[str, Any]) -> None:
        """Send AI processing status update"""



        try:
            message = RealTimeMessage(
                id=f"ai_update_{int(time.time())}",
                channel=NotificationChannel.AI_PROCESSING,
                type="processing_update",
                title="AI Processing Update",
                content=f"Content analysis {processing_data.get('status', 'in progress')}",
                payload=processing_data,
                priority="medium"
            )
            
            await self.send_to_user(user_id, message)
            
        except Exception as e:
            logger.error(f"Error sending AI processing update: {e}")

    async def send_revenue_notification(self, user_id: str, revenue_data: Dict[str, Any]) -> None:
        """Send revenue update notification"""



        try:
            message = RealTimeMessage(
                id=f"revenue_update_{int(time.time())}",
                channel=NotificationChannel.REVENUE_UPDATES,
                type="revenue_update",
                title="Revenue Update",
                content=f"New revenue: {revenue_data.get('amount', 0)} {revenue_data.get('currency', 'EUR')}",
                payload=revenue_data,
                priority="medium"
            )
            
            await self.send_to_user(user_id, message)
            
        except Exception as e:
            logger.error(f"Error sending revenue notification: {e}")

    async def get_offline_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get offline notifications for user"""



        try:
            if not self.redis_client:
                return []
            
            # Get all notifications
            notifications = await self.redis_client.lrange(f"notifications:{user_id}", 0, -1)
            
            # Clear the list
            await self.redis_client.delete(f"notifications:{user_id}")
            
            # Parse notifications
            parsed_notifications = []
            for notification in notifications:
                try:
                    parsed_notifications.append(json.loads(notification))
                except json.JSONDecodeError:
                    continue
            
            return parsed_notifications
            
        except Exception as e:
            logger.error(f"Error getting offline notifications: {e}")
            return []

    async def _cleanup_websocket_connection(self, connection_id: str) -> None:
        """Clean up WebSocket connection"""



        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            # Remove from user connections
            user_id = connection.user_id
            if user_id in self.user_connections:
                self.user_connections[user_id] = [
                    cid for cid in self.user_connections[user_id] if cid != connection_id
                ]
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from channel subscriptions
            for channel in connection.subscriptions:
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(connection_id)
            
            # Remove connection
            del self.connections[connection_id]
            
            logger.debug(f"Cleaned up connection {connection_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up connection {connection_id}: {e}")

    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""



        try:
            # Connection health checker
            health_task = asyncio.create_task(self._connection_health_checker())
            self.background_tasks.append(health_task)
            
            # Notification cleanup
            cleanup_task = asyncio.create_task(self._notification_cleanup())
            self.background_tasks.append(cleanup_task)
            
            logger.info("Started real-time communication background tasks")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")

    async def _connection_health_checker(self) -> None:
        """Check connection health and clean up stale connections"""
        while True:
            try:
                current_time = time.time()
                stale_connections = []
                
                for connection_id, connection in self.connections.items():
                    # Check if connection is stale (no heartbeat for 60 seconds)
                    if current_time - connection.last_heartbeat > 60:
                        stale_connections.append(connection_id)
                
                # Clean up stale connections
                for connection_id in stale_connections:
                    await self._cleanup_websocket_connection(connection_id)
                
                if stale_connections:
                    logger.info(f"Cleaned up {len(stale_connections)} stale connections")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in connection health checker: {e}")
                await asyncio.sleep(60)

    async def _notification_cleanup(self) -> None:
        """Clean up expired notifications"""
        while True:
            try:
                if self.redis_client:
                    # Clean up expired notifications
                    current_time = time.time()
                    
                    # This would iterate through stored notifications and remove expired ones
                    # Implementation depends on notification storage strategy
                    pass
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")
                await asyncio.sleep(3600)

    async def get_connection_stats(self) -> Dict[str, Union[int, Dict]]:
        """Get real-time connection statistics"""



        try:
            channel_stats = {}
            for channel, subscribers in self.channel_subscribers.items():
                channel_stats[channel] = len(subscribers)
            
            return {
                "total_connections": len(self.connections),
                "total_users": len(self.user_connections),
                "socketio_connections": len(self.sio_server.manager.rooms.get("/", {})),
                "channel_subscriptions": channel_stats,
                "active_channels": len(self.channel_subscribers)
            }
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {}

    async def shutdown(self) -> None:
        """Shutdown real-time communication manager"""



        try:
            logger.info("Shutting down real-time communication manager")
            
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Close all WebSocket connections
            for connection_id in list(self.connections.keys()):
                await self._cleanup_websocket_connection(connection_id)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Real-time communication manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
