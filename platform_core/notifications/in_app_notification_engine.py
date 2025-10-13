"""🚀 In-App Notification Engine - Real-Time Enterprise System
=============================================================
Module: platform_core/notifications/in_app_notification_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

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

🎯 IN-APP NOTIFICATION ENGINE - REAL-TIME ENTERPRISE
- WebSocket temps réel pour notifications instantanées
- State management avec persistence Redis
- Rich UI notifications avec actions interactives
- Analytics engagement et interaction tracking
- Segmentation intelligente et targeting avancé
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import websockets
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
import jwt

logger = logging.getLogger(__name__)


class NotificationStyle(Enum):
    """In-app notification styles."""
    TOAST = "toast"
    BANNER = "banner"
    MODAL = "modal"
    BADGE = "badge"
    SLIDE_IN = "slide_in"
    OVERLAY = "overlay"


class NotificationPosition(Enum):
    """Notification display position."""
    TOP_RIGHT = "top_right"
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    CENTER = "center"


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class NotificationStatus(Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    CLICKED = "clicked"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class ActionType(Enum):
    """Notification action types."""
    BUTTON = "button"
    LINK = "link"
    DISMISS = "dismiss"
    NAVIGATE = "navigate"
    API_CALL = "api_call"


@dataclass
class NotificationAction:
    """Notification action configuration."""
    id: str
    type: ActionType
    label: str
    icon: Optional[str] = None
    url: Optional[str] = None
    api_endpoint: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    style: Optional[str] = None
    confirm_message: Optional[str] = None


@dataclass
class NotificationMedia:
    """Notification media content."""
    type: str  # image, video, audio, gif
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class InAppNotification:
    """In-app notification data structure."""
    id: str
    user_id: str
    title: str
    message: str
    style: NotificationStyle = NotificationStyle.TOAST
    position: NotificationPosition = NotificationPosition.TOP_RIGHT
    priority: NotificationPriority = NotificationPriority.NORMAL
    icon: Optional[str] = None
    image: Optional[str] = None
    media: Optional[NotificationMedia] = None
    actions: List[NotificationAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    auto_dismiss_seconds: Optional[int] = None
    persist_after_read: bool = False
    require_interaction: bool = False
    sound_url: Optional[str] = None
    vibration_pattern: Optional[List[int]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: NotificationStatus = NotificationStatus.PENDING
    read_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None


@dataclass
class UserConnection:
    """WebSocket user connection information."""
    user_id: str
    websocket: WebSocket
    connected_at: datetime
    last_activity: datetime
    session_id: str
    device_info: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationTemplate:
    """In-app notification template."""
    id: str
    name: str
    title_template: str
    message_template: str
    style: NotificationStyle
    position: NotificationPosition
    icon: Optional[str] = None
    image_template: Optional[str] = None
    actions_template: List[Dict[str, Any]] = field(default_factory=list)
    category: Optional[str] = None
    auto_dismiss_seconds: Optional[int] = None
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ConnectionManager:
    """WebSocket connection manager for real-time notifications."""
    
    def __init__(self):
        self.active_connections: Dict[str, UserConnection] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> session_ids
        
    async def connect(self, websocket: WebSocket, user_id: str, session_id: str = None) -> str:
        """Connect user to WebSocket."""
        try:
            await websocket.accept()
            
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Create connection
            connection = UserConnection(
                user_id=user_id,
                websocket=websocket,
                connected_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                session_id=session_id
            )
            
            # Store connection
            self.active_connections[session_id] = connection
            
            # Track user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            logger.info(f"User {user_id} connected with session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            raise
    
    async def disconnect(self, session_id: str):
        """Disconnect user session."""
        try:
            if session_id in self.active_connections:
                connection = self.active_connections[session_id]
                user_id = connection.user_id
                
                # Remove connection
                del self.active_connections[session_id]
                
                # Update user sessions
                if user_id in self.user_sessions:
                    self.user_sessions[user_id] = [
                        sid for sid in self.user_sessions[user_id] 
                        if sid != session_id
                    ]
                    
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]
                
                logger.info(f"Session {session_id} disconnected")
                
        except Exception as e:
            logger.error(f"WebSocket disconnection error: {e}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """Send message to all user sessions."""
        sent_count = 0
        
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id].copy():
                try:
                    connection = self.active_connections.get(session_id)
                    if connection:
                        await connection.websocket.send_text(json.dumps(message))
                        connection.last_activity = datetime.utcnow()
                        sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send to session {session_id}: {e}")
                    await self.disconnect(session_id)
        
        return sent_count
    
    async def send_to_session(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific session."""
        try:
            connection = self.active_connections.get(session_id)
            if connection:
                await connection.websocket.send_text(json.dumps(message))
                connection.last_activity = datetime.utcnow()
                return True
        except Exception as e:
            logger.error(f"Failed to send to session {session_id}: {e}")
            await self.disconnect(session_id)
        
        return False
    
    async def broadcast(self, message: Dict[str, Any], exclude_users: List[str] = None) -> int:
        """Broadcast message to all connected users."""
        exclude_users = exclude_users or []
        sent_count = 0
        
        for session_id, connection in self.active_connections.copy().items():
            if connection.user_id not in exclude_users:
                try:
                    await connection.websocket.send_text(json.dumps(message))
                    connection.last_activity = datetime.utcnow()
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Broadcast failed for session {session_id}: {e}")
                    await self.disconnect(session_id)
        
        return sent_count
    
    def get_user_connections(self, user_id: str) -> List[UserConnection]:
        """Get all connections for a user."""
        connections = []
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                connection = self.active_connections.get(session_id)
                if connection:
                    connections.append(connection)
        return connections
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online."""
        return user_id in self.user_sessions and len(self.user_sessions[user_id]) > 0
    
    def get_online_users(self) -> List[str]:
        """Get list of online user IDs."""
        return list(self.user_sessions.keys())
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """Clean up inactive connections."""
        timeout_threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        inactive_sessions = []
        for session_id, connection in self.active_connections.items():
            if connection.last_activity < timeout_threshold:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            await self.disconnect(session_id)
        
        if inactive_sessions:
            logger.info(f"Cleaned up {len(inactive_sessions)} inactive connections")


class InAppNotificationEngine:
    """Enterprise in-app notification engine with real-time delivery."""
    
    def __init__(self, redis_client: redis.Redis, connection_manager: ConnectionManager):
        self.redis = redis_client
        self.connection_manager = connection_manager
        self.templates: Dict[str, NotificationTemplate] = {}
        self.analytics_data: Dict[str, Any] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        self.middleware_stack: List[Callable] = []
        
        # Start background tasks
        asyncio.create_task(self._background_cleanup())
        asyncio.create_task(self._process_scheduled_notifications())
    
    async def send_notification(self, notification: InAppNotification) -> bool:
        """Send in-app notification to user."""
        try:
            # Apply middleware
            for middleware in self.middleware_stack:
                notification = await middleware(notification)
                if not notification:
                    return False
            
            # Store notification
            await self._store_notification(notification)
            
            # Check if user is online
            if self.connection_manager.is_user_online(notification.user_id):
                # Send real-time notification
                message = {
                    "type": "notification",
                    "data": self._serialize_notification(notification)
                }
                
                sent_count = await self.connection_manager.send_to_user(
                    notification.user_id, message
                )
                
                if sent_count > 0:
                    notification.status = NotificationStatus.DELIVERED
                    await self._update_notification_status(notification)
                    
                    # Track analytics
                    await self._track_notification_sent(notification)
                    
                    logger.info(f"Notification {notification.id} sent to {sent_count} sessions")
                    return True
            else:
                # User offline - notification will be delivered when they reconnect
                logger.info(f"Notification {notification.id} queued for offline user {notification.user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send notification {notification.id}: {e}")
            return False
    
    async def send_template_notification(self, template_id: str, user_id: str, 
                                       template_data: Dict[str, Any], 
                                       overrides: Dict[str, Any] = None) -> bool:
        """Send notification using template."""
        try:
            # Load template
            template = await self._load_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Render template
            title = self._render_template_string(template.title_template, template_data)
            message = self._render_template_string(template.message_template, template_data)
            
            # Create notification
            notification_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "title": title,
                "message": message,
                "style": template.style,
                "position": template.position,
                "icon": template.icon,
                "category": template.category,
                "auto_dismiss_seconds": template.auto_dismiss_seconds
            }
            
            # Apply overrides
            if overrides:
                notification_data.update(overrides)
            
            # Render image template if available
            if template.image_template:
                notification_data["image"] = self._render_template_string(
                    template.image_template, template_data
                )
            
            # Render actions
            if template.actions_template:
                actions = []
                for action_template in template.actions_template:
                    action = NotificationAction(
                        id=action_template["id"],
                        type=ActionType(action_template["type"]),
                        label=self._render_template_string(action_template["label"], template_data),
                        icon=action_template.get("icon"),
                        url=self._render_template_string(action_template.get("url", ""), template_data) if action_template.get("url") else None,
                        payload=action_template.get("payload", {})
                    )
                    actions.append(action)
                notification_data["actions"] = actions
            
            notification = InAppNotification(**notification_data)
            return await self.send_notification(notification)
            
        except Exception as e:
            logger.error(f"Template notification failed: {e}")
            return False
    
    async def get_user_notifications(self, user_id: str, limit: int = 50, 
                                   include_read: bool = True) -> List[InAppNotification]:
        """Get notifications for user."""
        try:
            # Get notifications from Redis
            key = f"notifications:{user_id}"
            notification_ids = await self.redis.lrange(key, 0, limit - 1)
            
            notifications = []
            for notification_id in notification_ids:
                notification_data = await self.redis.hgetall(f"notification:{notification_id}")
                if notification_data:
                    notification = self._deserialize_notification(notification_data)
                    
                    if include_read or notification.status != NotificationStatus.READ:
                        notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read."""
        try:
            # Get notification
            notification_data = await self.redis.hgetall(f"notification:{notification_id}")
            if not notification_data:
                return False
            
            notification = self._deserialize_notification(notification_data)
            
            # Verify ownership
            if notification.user_id != user_id:
                return False
            
            # Update status
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            
            await self._update_notification_status(notification)
            await self._track_notification_interaction(notification, "read")
            
            logger.info(f"Notification {notification_id} marked as read")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification read: {e}")
            return False
    
    async def mark_notification_clicked(self, notification_id: str, user_id: str, 
                                      action_id: str = None) -> bool:
        """Mark notification as clicked."""
        try:
            # Get notification
            notification_data = await self.redis.hgetall(f"notification:{notification_id}")
            if not notification_data:
                return False
            
            notification = self._deserialize_notification(notification_data)
            
            # Verify ownership
            if notification.user_id != user_id:
                return False
            
            # Update status
            notification.status = NotificationStatus.CLICKED
            notification.clicked_at = datetime.utcnow()
            
            await self._update_notification_status(notification)
            await self._track_notification_interaction(notification, "clicked", {"action_id": action_id})
            
            logger.info(f"Notification {notification_id} clicked")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark notification clicked: {e}")
            return False
    
    async def dismiss_notification(self, notification_id: str, user_id: str) -> bool:
        """Dismiss notification."""
        try:
            # Get notification
            notification_data = await self.redis.hgetall(f"notification:{notification_id}")
            if not notification_data:
                return False
            
            notification = self._deserialize_notification(notification_data)
            
            # Verify ownership
            if notification.user_id != user_id:
                return False
            
            # Update status
            notification.status = NotificationStatus.DISMISSED
            notification.dismissed_at = datetime.utcnow()
            
            await self._update_notification_status(notification)
            await self._track_notification_interaction(notification, "dismissed")
            
            # Send dismiss event to user sessions
            message = {
                "type": "notification_dismissed",
                "data": {"notification_id": notification_id}
            }
            await self.connection_manager.send_to_user(user_id, message)
            
            logger.info(f"Notification {notification_id} dismissed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to dismiss notification: {e}")
            return False
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count for user."""
        try:
            key = f"notifications:{user_id}"
            notification_ids = await self.redis.lrange(key, 0, -1)
            
            unread_count = 0
            for notification_id in notification_ids:
                notification_data = await self.redis.hgetall(f"notification:{notification_id}")
                if notification_data:
                    notification = self._deserialize_notification(notification_data)
                    if notification.status not in [NotificationStatus.READ, NotificationStatus.DISMISSED]:
                        unread_count += 1
            
            return unread_count
            
        except Exception as e:
            logger.error(f"Failed to get unread count: {e}")
            return 0
    
    async def schedule_notification(self, notification: InAppNotification, 
                                  send_at: datetime) -> bool:
        """Schedule notification for future delivery."""
        try:
            # Store notification with scheduled status
            notification.status = NotificationStatus.PENDING
            await self._store_notification(notification)
            
            # Add to scheduled queue
            timestamp = int(send_at.timestamp())
            await self.redis.zadd("scheduled_notifications", {notification.id: timestamp})
            
            logger.info(f"Notification {notification.id} scheduled for {send_at}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule notification: {e}")
            return False
    
    async def send_to_segment(self, segment: str, notification_template: InAppNotification) -> int:
        """Send notification to user segment."""
        try:
            # Get users in segment
            user_ids = await self._get_segment_users(segment)
            
            sent_count = 0
            for user_id in user_ids:
                # Create personalized notification
                notification = InAppNotification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    **{k: v for k, v in asdict(notification_template).items() 
                       if k not in ['id', 'user_id', 'created_at', 'status']}
                )
                
                if await self.send_notification(notification):
                    sent_count += 1
            
            logger.info(f"Sent notifications to {sent_count} users in segment '{segment}'")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to send to segment: {e}")
            return 0
    
    async def add_middleware(self, middleware: Callable) -> None:
        """Add middleware to notification processing pipeline."""
        self.middleware_stack.append(middleware)
    
    async def register_notification_handler(self, event_type: str, handler: Callable) -> None:
        """Register handler for notification events."""
        self.notification_handlers[event_type] = handler
    
    async def handle_websocket_message(self, session_id: str, message: Dict[str, Any]) -> None:
        """Handle incoming WebSocket message."""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            connection = self.connection_manager.active_connections.get(session_id)
            if not connection:
                return
            
            user_id = connection.user_id
            
            if message_type == "mark_read":
                await self.mark_notification_read(data.get("notification_id"), user_id)
            
            elif message_type == "mark_clicked":
                await self.mark_notification_clicked(
                    data.get("notification_id"), 
                    user_id, 
                    data.get("action_id")
                )
            
            elif message_type == "dismiss":
                await self.dismiss_notification(data.get("notification_id"), user_id)
            
            elif message_type == "get_notifications":
                notifications = await self.get_user_notifications(
                    user_id, 
                    data.get("limit", 50),
                    data.get("include_read", True)
                )
                
                response = {
                    "type": "notifications_list",
                    "data": [self._serialize_notification(n) for n in notifications]
                }
                await self.connection_manager.send_to_session(session_id, response)
            
            elif message_type == "get_unread_count":
                count = await self.get_unread_count(user_id)
                response = {
                    "type": "unread_count",
                    "data": {"count": count}
                }
                await self.connection_manager.send_to_session(session_id, response)
            
            # Custom handlers
            elif message_type in self.notification_handlers:
                await self.notification_handlers[message_type](session_id, data)
            
        except Exception as e:
            logger.error(f"WebSocket message handling failed: {e}")
    
    async def _store_notification(self, notification: InAppNotification) -> None:
        """Store notification in Redis."""
        try:
            # Store notification data
            notification_data = self._serialize_notification(notification)
            await self.redis.hset(f"notification:{notification.id}", mapping=notification_data)
            
            # Add to user's notification list
            await self.redis.lpush(f"notifications:{notification.user_id}", notification.id)
            
            # Set expiration if specified
            if notification.expires_at:
                expire_seconds = int((notification.expires_at - datetime.utcnow()).total_seconds())
                if expire_seconds > 0:
                    await self.redis.expire(f"notification:{notification.id}", expire_seconds)
            
        except Exception as e:
            logger.error(f"Failed to store notification: {e}")
            raise
    
    async def _update_notification_status(self, notification: InAppNotification) -> None:
        """Update notification status in storage."""
        try:
            notification_data = self._serialize_notification(notification)
            await self.redis.hset(f"notification:{notification.id}", mapping=notification_data)
        except Exception as e:
            logger.error(f"Failed to update notification status: {e}")
    
    def _serialize_notification(self, notification: InAppNotification) -> Dict[str, str]:
        """Serialize notification for storage."""
        try:
            data = asdict(notification)
            
            # Handle datetime fields
            for field in ['created_at', 'expires_at', 'read_at', 'clicked_at', 'dismissed_at']:
                if data.get(field):
                    data[field] = data[field].isoformat()
            
            # Handle enum fields
            data['style'] = data['style'].value if data.get('style') else None
            data['position'] = data['position'].value if data.get('position') else None
            data['priority'] = data['priority'].value if data.get('priority') else None
            data['status'] = data['status'].value if data.get('status') else None
            
            # Serialize complex fields
            data['actions'] = json.dumps([asdict(action) for action in notification.actions])
            data['metadata'] = json.dumps(data.get('metadata', {}))
            data['tags'] = json.dumps(data.get('tags', []))
            
            if data.get('media'):
                data['media'] = json.dumps(asdict(notification.media))
            
            if data.get('vibration_pattern'):
                data['vibration_pattern'] = json.dumps(data['vibration_pattern'])
            
            # Convert all values to strings
            return {k: str(v) if v is not None else '' for k, v in data.items()}
            
        except Exception as e:
            logger.error(f"Failed to serialize notification: {e}")
            return {}
    
    def _deserialize_notification(self, data: Dict[str, str]) -> InAppNotification:
        """Deserialize notification from storage."""
        try:
            # Handle datetime fields
            for field in ['created_at', 'expires_at', 'read_at', 'clicked_at', 'dismissed_at']:
                if data.get(field):
                    data[field] = datetime.fromisoformat(data[field])
                else:
                    data[field] = None
            
            # Handle enum fields
            if data.get('style'):
                data['style'] = NotificationStyle(data['style'])
            if data.get('position'):
                data['position'] = NotificationPosition(data['position'])
            if data.get('priority'):
                data['priority'] = NotificationPriority(int(data['priority']))
            if data.get('status'):
                data['status'] = NotificationStatus(data['status'])
            
            # Deserialize complex fields
            if data.get('actions'):
                actions_data = json.loads(data['actions'])
                data['actions'] = [
                    NotificationAction(
                        id=action['id'],
                        type=ActionType(action['type']),
                        label=action['label'],
                        icon=action.get('icon'),
                        url=action.get('url'),
                        api_endpoint=action.get('api_endpoint'),
                        payload=action.get('payload', {}),
                        style=action.get('style'),
                        confirm_message=action.get('confirm_message')
                    ) for action in actions_data
                ]
            
            if data.get('metadata'):
                data['metadata'] = json.loads(data['metadata'])
            
            if data.get('tags'):
                data['tags'] = json.loads(data['tags'])
            
            if data.get('media'):
                media_data = json.loads(data['media'])
                data['media'] = NotificationMedia(**media_data)
            
            if data.get('vibration_pattern'):
                data['vibration_pattern'] = json.loads(data['vibration_pattern'])
            
            # Handle optional integer fields
            for field in ['auto_dismiss_seconds']:
                if data.get(field):
                    data[field] = int(data[field])
                else:
                    data[field] = None
            
            # Handle boolean fields
            for field in ['persist_after_read', 'require_interaction']:
                data[field] = data.get(field, '').lower() == 'true'
            
            return InAppNotification(**data)
            
        except Exception as e:
            logger.error(f"Failed to deserialize notification: {e}")
            raise
    
    def _render_template_string(self, template: str, data: Dict[str, Any]) -> str:
        """Render template string with data."""
        try:
            result = template
            for key, value in data.items():
                result = result.replace(f"{{{{{key}}}}}", str(value))
            return result
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template
    
    async def _load_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Load notification template."""
        try:
            # For now, return a sample template
            return NotificationTemplate(
                id=template_id,
                name=f"Template {template_id}",
                title_template="Welcome {{user_name}}!",
                message_template="Thank you for joining {{platform_name}}. You have {{credits}} credits available.",
                style=NotificationStyle.TOAST,
                position=NotificationPosition.TOP_RIGHT,
                icon="welcome-icon",
                category="welcome",
                auto_dismiss_seconds=5,
                variables=["user_name", "platform_name", "credits"]
            )
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return None
    
    async def _get_segment_users(self, segment: str) -> List[str]:
        """Get users in segment."""
        try:
            # Implementation would query user database
            # For now, return sample users
            return ["user_1", "user_2", "user_3"]
        except Exception as e:
            logger.error(f"Failed to get segment users: {e}")
            return []
    
    async def _track_notification_sent(self, notification: InAppNotification) -> None:
        """Track notification analytics."""
        try:
            analytics_key = f"notification_analytics_{datetime.utcnow().strftime('%Y-%m-%d')}"
            
            if analytics_key not in self.analytics_data:
                self.analytics_data[analytics_key] = {
                    'total_sent': 0,
                    'by_style': {},
                    'by_category': {},
                    'by_priority': {}
                }
            
            analytics = self.analytics_data[analytics_key]
            analytics['total_sent'] += 1
            
            # Track by style
            style_key = notification.style.value
            analytics['by_style'][style_key] = analytics['by_style'].get(style_key, 0) + 1
            
            # Track by category
            if notification.category:
                analytics['by_category'][notification.category] = analytics['by_category'].get(notification.category, 0) + 1
            
            # Track by priority
            priority_key = notification.priority.name
            analytics['by_priority'][priority_key] = analytics['by_priority'].get(priority_key, 0) + 1
            
        except Exception as e:
            logger.error(f"Failed to track notification analytics: {e}")
    
    async def _track_notification_interaction(self, notification: InAppNotification, 
                                           interaction_type: str, metadata: Dict[str, Any] = None) -> None:
        """Track notification interaction."""
        try:
            interaction_key = f"notification_interactions_{datetime.utcnow().strftime('%Y-%m-%d')}"
            
            interaction_data = {
                'notification_id': notification.id,
                'user_id': notification.user_id,
                'interaction_type': interaction_type,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
            await self.redis.lpush(interaction_key, json.dumps(interaction_data))
            
        except Exception as e:
            logger.error(f"Failed to track interaction: {e}")
    
    async def _process_scheduled_notifications(self) -> None:
        """Background task to process scheduled notifications."""
        while True:
            try:
                # Get notifications to send
                current_timestamp = int(datetime.utcnow().timestamp())
                
                # Get notifications due for sending
                scheduled = await self.redis.zrangebyscore(
                    "scheduled_notifications", 
                    0, 
                    current_timestamp,
                    withscores=True
                )
                
                for notification_id, timestamp in scheduled:
                    # Get notification data
                    notification_data = await self.redis.hgetall(f"notification:{notification_id}")
                    if notification_data:
                        notification = self._deserialize_notification(notification_data)
                        
                        # Send notification
                        await self.send_notification(notification)
                        
                        # Remove from scheduled queue
                        await self.redis.zrem("scheduled_notifications", notification_id)
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Scheduled notifications processing error: {e}")
                await asyncio.sleep(60)
    
    async def _background_cleanup(self) -> None:
        """Background task for cleanup operations."""
        while True:
            try:
                # Clean up expired notifications
                await self._cleanup_expired_notifications()
                
                # Clean up inactive connections
                await self.connection_manager.cleanup_inactive_connections()
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
                await asyncio.sleep(300)
    
    async def _cleanup_expired_notifications(self) -> None:
        """Clean up expired notifications."""
        try:
            # This would be more sophisticated in production
            # For now, just log that cleanup is running
            logger.debug("Running notification cleanup")
        except Exception as e:
            logger.error(f"Notification cleanup failed: {e}")


# Factory function for creating service instance
def create_in_app_notification_engine(redis_client: redis.Redis) -> InAppNotificationEngine:
    """Create and configure in-app notification engine."""
    connection_manager = ConnectionManager()
    return InAppNotificationEngine(redis_client, connection_manager)


# Export main classes and functions
__all__ = [
    'InAppNotificationEngine',
    'ConnectionManager',
    'InAppNotification',
    'NotificationTemplate',
    'NotificationAction',
    'NotificationMedia',
    'UserConnection',
    'NotificationStyle',
    'NotificationPosition',
    'NotificationPriority',
    'NotificationStatus',
    'ActionType',
    'create_in_app_notification_engine'
]