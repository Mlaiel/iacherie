"""{{handler_name}} WebSocket Handler Template for Ainflue Platform
{{handler_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Set, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import uuid

from fastapi import WebSocket, WebSocketDisconnect, status, Depends
from fastapi.websockets import WebSocketState
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis

from core.config import get_settings
from core.auth import get_current_user_websocket, verify_websocket_permissions
from core.rate_limiting import WebSocketRateLimiter
from utils.exceptions import WebSocketException
from monitoring.websocket_metrics import WebSocketMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class MessageType(Enum):
    """WebSocket message types"""
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    SUBSCRIPTION = "subscription"
    UNSUBSCRIPTION = "unsubscription"
    DATA = "data"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"
    PRIVATE_MESSAGE = "private_message"
    STATUS_UPDATE = "status_update"
    COMMAND = "command"
    RESPONSE = "response"


class ConnectionState(Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    SUBSCRIBED = "subscribed"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class ChannelType(Enum):
    """Channel types for subscriptions"""
    PUBLIC = "public"
    PRIVATE = "private"
    SYSTEM = "system"
    USER_SPECIFIC = "user_specific"
    ROOM = "room"
    BROADCAST = "broadcast"


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    type: MessageType = Field(..., description="Message type")
    channel: Optional[str] = Field(None, description="Target channel")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    user_id: Optional[str] = Field(None, description="Sender user ID")
    target_user_id: Optional[str] = Field(None, description="Target user ID for private messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    expires_at: Optional[datetime] = Field(None, description="Message expiration time")
    require_auth: bool = Field(default=True, description="Whether authentication is required")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "id": "msg_123",
                "type": "data",
                "channel": "notifications",
                "data": {"content": "Hello, World!"},
                "user_id": "user_123",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class ConnectionInfo(BaseModel):
    """WebSocket connection information"""
    connection_id: str = Field(..., description="Unique connection identifier")
    user_id: Optional[str] = Field(None, description="Authenticated user ID")
    websocket: WebSocket = Field(..., description="WebSocket instance")
    state: ConnectionState = Field(default=ConnectionState.CONNECTING, description="Connection state")
    subscriptions: Set[str] = Field(default_factory=set, description="Subscribed channels")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Connection metadata")
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    
    class Config:
        arbitrary_types_allowed = True


class ChannelInfo(BaseModel):
    """Channel information"""
    channel_id: str = Field(..., description="Channel identifier")
    channel_type: ChannelType = Field(..., description="Channel type")
    name: str = Field(..., description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    max_connections: Optional[int] = Field(None, description="Maximum connections allowed")
    require_auth: bool = Field(default=True, description="Whether authentication is required")
    permissions: List[str] = Field(default_factory=list, description="Required permissions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Channel creation time")


class {{handler_name}}Manager:
    """{{handler_description}} with comprehensive WebSocket management"""
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        enable_persistence: bool = True,
        heartbeat_interval: int = 30,
        max_connections_per_user: int = 10,
        message_retention_hours: int = 24,
        metrics_collector: Optional[WebSocketMetricsCollector] = None
    ):
        self.redis_client = redis_client
        self.enable_persistence = enable_persistence
        self.heartbeat_interval = heartbeat_interval
        self.max_connections_per_user = max_connections_per_user
        self.message_retention_hours = message_retention_hours
        self.metrics_collector = metrics_collector or WebSocketMetricsCollector()
        
        # Connection management
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.channel_subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids
        
        # Channel management
        self.channels: Dict[str, ChannelInfo] = {}
        
        # Rate limiting
        self.rate_limiter = WebSocketRateLimiter()
        
        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {}
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Initialize default channels and handlers
        self._initialize_default_channels()
        self._initialize_message_handlers()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("WebSocket manager initialized")
    
    def _initialize_default_channels(self):
        """Initialize default channels"""
        default_channels = [
            ChannelInfo(
                channel_id="notifications",
                channel_type=ChannelType.USER_SPECIFIC,
                name="Notifications",
                description="User notifications channel",
                require_auth=True
            ),
            ChannelInfo(
                channel_id="system",
                channel_type=ChannelType.SYSTEM,
                name="System",
                description="System announcements",
                require_auth=False
            ),
            ChannelInfo(
                channel_id="chat",
                channel_type=ChannelType.PUBLIC,
                name="Public Chat",
                description="Public chat room",
                require_auth=True
            )
        ]
        
        for channel in default_channels:
            self.channels[channel.channel_id] = channel
    
    def _initialize_message_handlers(self):
        """Initialize message handlers"""
        self.message_handlers = {
            MessageType.CONNECTION: self._handle_connection,
            MessageType.AUTHENTICATION: self._handle_authentication,
            MessageType.SUBSCRIPTION: self._handle_subscription,
            MessageType.UNSUBSCRIPTION: self._handle_unsubscription,
            MessageType.DATA: self._handle_data_message,
            MessageType.HEARTBEAT: self._handle_heartbeat,
            MessageType.PRIVATE_MESSAGE: self._handle_private_message,
            MessageType.COMMAND: self._handle_command
        }
    
    def _start_background_tasks(self):
        """Start background tasks"""
        # Heartbeat task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.background_tasks.add(heartbeat_task)
        heartbeat_task.add_done_callback(self.background_tasks.discard)
        
        # Cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self.background_tasks.discard)
    
    async def connect_websocket(
        self, 
        websocket: WebSocket, 
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Connect a new WebSocket"""
        
        try:
            # Accept WebSocket connection
            await websocket.accept()
            
            # Generate connection ID
            connection_id = str(uuid.uuid4())
            
            # Check connection limits
            if user_id and user_id in self.user_connections:
                if len(self.user_connections[user_id]) >= self.max_connections_per_user:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    raise WebSocketException("Maximum connections per user exceeded")
            
            # Create connection info
            connection_info = ConnectionInfo(
                connection_id=connection_id,
                user_id=user_id,
                websocket=websocket,
                state=ConnectionState.CONNECTED,
                metadata=metadata or {}
            )
            
            # Store connection
            self.active_connections[connection_id] = connection_info
            
            # Update user connections
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
                connection_info.state = ConnectionState.AUTHENTICATED
            
            # Send connection confirmation
            await self._send_message_to_connection(
                connection_id,
                WebSocketMessage(
                    type=MessageType.CONNECTION,
                    data={
                        "status": "connected",
                        "connection_id": connection_id,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    require_auth=False
                )
            )
            
            # Record metrics
            await self.metrics_collector.record_connection(
                connection_id=connection_id,
                user_id=user_id,
                success=True
            )
            
            logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")
            return connection_id
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            await self.metrics_collector.record_connection(
                connection_id="unknown",
                user_id=user_id,
                success=False
            )
            raise WebSocketException(f"Connection failed: {e}")
    
    async def disconnect_websocket(self, connection_id: str, code: int = status.WS_1000_NORMAL_CLOSURE):
        """Disconnect a WebSocket"""
        
        if connection_id not in self.active_connections:
            return
        
        connection_info = self.active_connections[connection_id]
        
        try:
            # Update connection state
            connection_info.state = ConnectionState.DISCONNECTING
            
            # Remove from subscriptions
            for channel_id in list(connection_info.subscriptions):
                await self._unsubscribe_from_channel(connection_id, channel_id)
            
            # Close WebSocket
            if connection_info.websocket.client_state == WebSocketState.CONNECTED:
                await connection_info.websocket.close(code=code)
            
            # Remove from user connections
            if connection_info.user_id and connection_info.user_id in self.user_connections:
                self.user_connections[connection_info.user_id].discard(connection_id)
                if not self.user_connections[connection_info.user_id]:
                    del self.user_connections[connection_info.user_id]
            
            # Remove connection
            del self.active_connections[connection_id]
            
            # Record metrics
            await self.metrics_collector.record_disconnection(
                connection_id=connection_id,
                user_id=connection_info.user_id,
                duration=(datetime.utcnow() - connection_info.connected_at).total_seconds()
            )
            
            logger.info(f"WebSocket disconnected: {connection_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket {connection_id}: {e}")
    
    async def handle_message(self, connection_id: str, message_data: str):
        """Handle incoming WebSocket message"""
        
        if connection_id not in self.active_connections:
            logger.warning(f"Message from unknown connection: {connection_id}")
            return
        
        connection_info = self.active_connections[connection_id]
        
        try:
            # Parse message
            message_dict = json.loads(message_data)
            message = WebSocketMessage(**message_dict)
            
            # Update last activity
            connection_info.last_activity = datetime.utcnow()
            
            # Check rate limits
            if not await self.rate_limiter.check_rate_limit(connection_id, message.type):
                await self._send_error_message(connection_id, "Rate limit exceeded")
                return
            
            # Check authentication if required
            if message.require_auth and connection_info.state != ConnectionState.AUTHENTICATED:
                await self._send_error_message(connection_id, "Authentication required")
                return
            
            # Handle message
            handler = self.message_handlers.get(message.type)
            if handler:
                await handler(connection_id, message)
            else:
                await self._send_error_message(connection_id, f"Unknown message type: {message.type}")
            
            # Record metrics
            await self.metrics_collector.record_message_received(
                connection_id=connection_id,
                message_type=message.type.value,
                success=True
            )
            
        except json.JSONDecodeError:
            await self._send_error_message(connection_id, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
            await self._send_error_message(connection_id, "Message processing error")
            await self.metrics_collector.record_message_received(
                connection_id=connection_id,
                message_type="unknown",
                success=False
            )
    
    # Message handlers
    async def _handle_connection(self, connection_id: str, message: WebSocketMessage):
        """Handle connection message"""
        # Connection already handled in connect_websocket
        pass
    
    async def _handle_authentication(self, connection_id: str, message: WebSocketMessage):
        """Handle authentication message"""
        connection_info = self.active_connections[connection_id]
        
        # Extract authentication data
        auth_data = message.data
        token = auth_data.get("token")
        
        if not token:
            await self._send_error_message(connection_id, "Authentication token required")
            return
        
        try:
            # Verify token (implement your authentication logic)
            user_id = await self._verify_auth_token(token)
            
            if user_id:
                # Update connection info
                connection_info.user_id = user_id
                connection_info.state = ConnectionState.AUTHENTICATED
                
                # Update user connections
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
                
                # Send success response
                await self._send_message_to_connection(
                    connection_id,
                    WebSocketMessage(
                        type=MessageType.RESPONSE,
                        data={
                            "status": "authenticated",
                            "user_id": user_id
                        },
                        require_auth=False
                    )
                )
            else:
                await self._send_error_message(connection_id, "Invalid authentication token")
                
        except Exception as e:
            logger.error(f"Authentication error for {connection_id}: {e}")
            await self._send_error_message(connection_id, "Authentication failed")
    
    async def _handle_subscription(self, connection_id: str, message: WebSocketMessage):
        """Handle channel subscription"""
        channel_id = message.data.get("channel")
        
        if not channel_id:
            await self._send_error_message(connection_id, "Channel ID required")
            return
        
        await self._subscribe_to_channel(connection_id, channel_id)
    
    async def _handle_unsubscription(self, connection_id: str, message: WebSocketMessage):
        """Handle channel unsubscription"""
        channel_id = message.data.get("channel")
        
        if not channel_id:
            await self._send_error_message(connection_id, "Channel ID required")
            return
        
        await self._unsubscribe_from_channel(connection_id, channel_id)
    
    async def _handle_data_message(self, connection_id: str, message: WebSocketMessage):
        """Handle data message"""
        connection_info = self.active_connections[connection_id]
        
        # Add user ID to message
        message.user_id = connection_info.user_id
        
        # Broadcast to channel if specified
        if message.channel:
            await self._broadcast_to_channel(message.channel, message, exclude_connection=connection_id)
        
        # Store message if persistence is enabled
        if self.enable_persistence:
            await self._store_message(message)
    
    async def _handle_heartbeat(self, connection_id: str, message: WebSocketMessage):
        """Handle heartbeat message"""
        connection_info = self.active_connections[connection_id]
        connection_info.last_activity = datetime.utcnow()
        
        # Send heartbeat response
        await self._send_message_to_connection(
            connection_id,
            WebSocketMessage(
                type=MessageType.HEARTBEAT,
                data={"timestamp": datetime.utcnow().isoformat()},
                require_auth=False
            )
        )
    
    async def _handle_private_message(self, connection_id: str, message: WebSocketMessage):
        """Handle private message"""
        target_user_id = message.target_user_id
        
        if not target_user_id:
            await self._send_error_message(connection_id, "Target user ID required")
            return
        
        # Send to target user's connections
        if target_user_id in self.user_connections:
            for target_connection_id in self.user_connections[target_user_id]:
                await self._send_message_to_connection(target_connection_id, message)
    
    async def _handle_command(self, connection_id: str, message: WebSocketMessage):
        """Handle command message"""
        command = message.data.get("command")
        
        if command == "list_channels":
            channels_info = [
                {
                    "id": channel.channel_id,
                    "name": channel.name,
                    "type": channel.channel_type.value,
                    "description": channel.description
                }
                for channel in self.channels.values()
            ]
            
            await self._send_message_to_connection(
                connection_id,
                WebSocketMessage(
                    type=MessageType.RESPONSE,
                    data={"channels": channels_info},
                    require_auth=False
                )
            )
        
        elif command == "list_subscriptions":
            connection_info = self.active_connections[connection_id]
            
            await self._send_message_to_connection(
                connection_id,
                WebSocketMessage(
                    type=MessageType.RESPONSE,
                    data={"subscriptions": list(connection_info.subscriptions)},
                    require_auth=False
                )
            )
        
        else:
            await self._send_error_message(connection_id, f"Unknown command: {command}")
    
    # Channel management
    async def _subscribe_to_channel(self, connection_id: str, channel_id: str):
        """Subscribe connection to channel"""
        connection_info = self.active_connections[connection_id]
        
        # Check if channel exists
        if channel_id not in self.channels:
            await self._send_error_message(connection_id, f"Channel not found: {channel_id}")
            return
        
        channel_info = self.channels[channel_id]
        
        # Check permissions
        if channel_info.require_auth and connection_info.state != ConnectionState.AUTHENTICATED:
            await self._send_error_message(connection_id, "Authentication required for this channel")
            return
        
        # Check channel permissions
        if channel_info.permissions and connection_info.user_id:
            has_permission = await verify_websocket_permissions(
                connection_info.user_id, 
                channel_info.permissions
            )
            if not has_permission:
                await self._send_error_message(connection_id, "Insufficient permissions for this channel")
                return
        
        # Check connection limits
        if channel_info.max_connections:
            current_connections = len(self.channel_subscriptions.get(channel_id, set()))
            if current_connections >= channel_info.max_connections:
                await self._send_error_message(connection_id, "Channel is full")
                return
        
        # Add to subscriptions
        connection_info.subscriptions.add(channel_id)
        
        if channel_id not in self.channel_subscriptions:
            self.channel_subscriptions[channel_id] = set()
        self.channel_subscriptions[channel_id].add(connection_id)
        
        # Send confirmation
        await self._send_message_to_connection(
            connection_id,
            WebSocketMessage(
                type=MessageType.RESPONSE,
                data={
                    "status": "subscribed",
                    "channel": channel_id
                },
                require_auth=False
            )
        )
        
        logger.info(f"Connection {connection_id} subscribed to channel {channel_id}")
    
    async def _unsubscribe_from_channel(self, connection_id: str, channel_id: str):
        """Unsubscribe connection from channel"""
        connection_info = self.active_connections.get(connection_id)
        
        if not connection_info:
            return
        
        # Remove from subscriptions
        connection_info.subscriptions.discard(channel_id)
        
        if channel_id in self.channel_subscriptions:
            self.channel_subscriptions[channel_id].discard(connection_id)
            if not self.channel_subscriptions[channel_id]:
                del self.channel_subscriptions[channel_id]
        
        # Send confirmation
        await self._send_message_to_connection(
            connection_id,
            WebSocketMessage(
                type=MessageType.RESPONSE,
                data={
                    "status": "unsubscribed",
                    "channel": channel_id
                },
                require_auth=False
            )
        )
        
        logger.info(f"Connection {connection_id} unsubscribed from channel {channel_id}")
    
    # Message sending
    async def _send_message_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        connection_info = self.active_connections.get(connection_id)
        
        if not connection_info or connection_info.websocket.client_state != WebSocketState.CONNECTED:
            return False
        
        try:
            message_data = message.dict(exclude_none=True)
            await connection_info.websocket.send_text(json.dumps(message_data))
            
            # Record metrics
            await self.metrics_collector.record_message_sent(
                connection_id=connection_id,
                message_type=message.type.value,
                success=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            await self.disconnect_websocket(connection_id)
            return False
    
    async def _broadcast_to_channel(
        self, 
        channel_id: str, 
        message: WebSocketMessage, 
        exclude_connection: Optional[str] = None
    ):
        """Broadcast message to all connections in channel"""
        
        if channel_id not in self.channel_subscriptions:
            return
        
        connection_ids = self.channel_subscriptions[channel_id].copy()
        
        if exclude_connection:
            connection_ids.discard(exclude_connection)
        
        # Send to all connections
        tasks = []
        for connection_id in connection_ids:
            task = self._send_message_to_connection(connection_id, message)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_error_message(self, connection_id: str, error_message: str):
        """Send error message to connection"""
        await self._send_message_to_connection(
            connection_id,
            WebSocketMessage(
                type=MessageType.ERROR,
                data={"error": error_message},
                require_auth=False
            )
        )
    
    # Utility methods
    async def _verify_auth_token(self, token: str) -> Optional[str]:
        """Verify authentication token and return user ID"""
        # Implement your token verification logic here
        # This is a placeholder implementation
        try:
            # Use your authentication service
            user = await get_current_user_websocket(token)
            return user.id if user else None
        except Exception:
            return None
    
    async def _store_message(self, message: WebSocketMessage):
        """Store message for persistence"""
        if self.redis_client:
            try:
                key = f"ws_message:{message.channel}:{message.id}"
                data = message.dict()
                await self.redis_client.setex(
                    key, 
                    self.message_retention_hours * 3600, 
                    json.dumps(data, default=str)
                )
            except Exception as e:
                logger.error(f"Failed to store message: {e}")
    
    # Background tasks
    async def _heartbeat_loop(self):
        """Send periodic heartbeats"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                # Send heartbeat to all connections
                current_time = datetime.utcnow()
                for connection_id, connection_info in list(self.active_connections.items()):
                    # Check if connection is stale
                    if (current_time - connection_info.last_activity).seconds > self.heartbeat_interval * 2:
                        logger.info(f"Disconnecting stale connection: {connection_id}")
                        await self.disconnect_websocket(connection_id)
                        continue
                    
                    # Send heartbeat
                    await self._send_message_to_connection(
                        connection_id,
                        WebSocketMessage(
                            type=MessageType.HEARTBEAT,
                            data={"timestamp": current_time.isoformat()},
                            require_auth=False
                        )
                    )
                    
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of resources"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up disconnected connections
                disconnected_connections = []
                for connection_id, connection_info in self.active_connections.items():
                    if connection_info.websocket.client_state == WebSocketState.DISCONNECTED:
                        disconnected_connections.append(connection_id)
                
                for connection_id in disconnected_connections:
                    await self.disconnect_websocket(connection_id)
                
                logger.info(f"Cleaned up {len(disconnected_connections)} disconnected connections")
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    # Public API methods
    async def broadcast_to_all(self, message: WebSocketMessage):
        """Broadcast message to all connected users"""
        tasks = []
        for connection_id in list(self.active_connections.keys()):
            task = self._send_message_to_connection(connection_id, message)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to specific user"""
        if user_id in self.user_connections:
            tasks = []
            for connection_id in self.user_connections[user_id]:
                task = self._send_message_to_connection(connection_id, message)
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def create_channel(self, channel_info: ChannelInfo):
        """Create a new channel"""
        self.channels[channel_info.channel_id] = channel_info
        logger.info(f"Created channel: {channel_info.channel_id}")
    
    async def delete_channel(self, channel_id: str):
        """Delete a channel"""
        if channel_id in self.channels:
            # Disconnect all subscribers
            if channel_id in self.channel_subscriptions:
                for connection_id in list(self.channel_subscriptions[channel_id]):
                    await self._unsubscribe_from_channel(connection_id, channel_id)
            
            del self.channels[channel_id]
            logger.info(f"Deleted channel: {channel_id}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            "active_connections": len(self.active_connections),
            "authenticated_connections": len([
                c for c in self.active_connections.values() 
                if c.state == ConnectionState.AUTHENTICATED
            ]),
            "total_users": len(self.user_connections),
            "total_channels": len(self.channels),
            "channel_subscriptions": {
                channel_id: len(connections) 
                for channel_id, connections in self.channel_subscriptions.items()
            }
        }


# FastAPI WebSocket endpoint
class {{handler_name}}Endpoint:
    """WebSocket endpoint handler"""
    
    def __init__(self, manager: {{handler_name}}Manager):
        self.manager = manager
    
    async def websocket_endpoint(
        self, 
        websocket: WebSocket,
        user_id: Optional[str] = None,
        channel: Optional[str] = None
    ):
        """Main WebSocket endpoint"""
        connection_id = None
        
        try:
            # Connect WebSocket
            connection_id = await self.manager.connect_websocket(
                websocket, 
                user_id=user_id,
                metadata={"initial_channel": channel}
            )
            
            # Auto-subscribe to initial channel if provided
            if channel and user_id:
                await self.manager._subscribe_to_channel(connection_id, channel)
            
            # Message handling loop
            while True:
                try:
                    data = await websocket.receive_text()
                    await self.manager.handle_message(connection_id, data)
                    
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected normally: {connection_id}")
                    break
                except Exception as e:
                    logger.error(f"Error in message loop for {connection_id}: {e}")
                    break
        
        except Exception as e:
            logger.error(f"WebSocket endpoint error: {e}")
        
        finally:
            if connection_id:
                await self.manager.disconnect_websocket(connection_id)


# Template usage example
def create_websocket_handler_example():
    """Example of how to create and use the WebSocket handler"""
    
    # Create manager
    manager = {{handler_name}}Manager(
        heartbeat_interval=30,
        max_connections_per_user=5
    )
    
    # Create endpoint
    endpoint = {{handler_name}}Endpoint(manager)
    
    return manager, endpoint


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "websocket_handler_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive WebSocket handler with real-time communication features",
    "required_parameters": [
        "handler_name",
        "handler_description",
        "author_name",
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_message_types",
        "custom_channels",
        "authentication_method",
        "persistence_backend"
    ],
    "dependencies": [
        "fastapi>=0.104.1",
        "pydantic>=2.5.0",
        "redis>=5.0.0",
        "websockets>=12.0"
    ],
    "features": [
        "Real-time bidirectional communication",
        "Channel-based messaging",
        "User authentication",
        "Rate limiting",
        "Message persistence",
        "Private messaging",
        "Broadcast messaging",
        "Connection management",
        "Heartbeat monitoring",
        "Metrics collection",
        "Error handling",
        "Auto-reconnection support"
    ]
}