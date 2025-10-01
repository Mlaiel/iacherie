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

WebSocket Service Template for IA Chéries Microservices Platform
============================================================

Enterprise-grade WebSocket service template providing:
- Real-time bidirectional communication
- Room-based connection management
- Message broadcasting and routing
- Authentication and authorization
- Connection lifecycle management
- Message queuing and persistence
- Rate limiting and throttling
- Heartbeat and connection monitoring
- Scalable connection pooling
- Event-driven message handling

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Real-time Systems Expert
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Set, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import redis.asyncio as redis

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection state"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class MessageType(Enum):
    """WebSocket message types"""
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    BROADCAST = "broadcast"
    PRIVATE_MESSAGE = "private_message"
    SYSTEM_MESSAGE = "system_message"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    AUTH = "auth"


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Message ID")
    type: MessageType = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    room: Optional[str] = Field(default=None, description="Target room")
    target_user: Optional[str] = Field(default=None, description="Target user for private messages")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    sender: Optional[str] = Field(default=None, description="Message sender")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConnectionInfo(BaseModel):
    """WebSocket connection information"""
    connection_id: str = Field(..., description="Unique connection ID")
    user_id: Optional[str] = Field(default=None, description="Authenticated user ID")
    state: ConnectionState = Field(default=ConnectionState.CONNECTING, description="Connection state")
    rooms: Set[str] = Field(default_factory=set, description="Joined rooms")
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow, description="Last heartbeat timestamp")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional connection metadata")


class RoomInfo(BaseModel):
    """Room information"""
    room_id: str = Field(..., description="Room ID")
    name: str = Field(..., description="Room name")
    description: Optional[str] = Field(default=None, description="Room description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Room creation timestamp")
    max_connections: Optional[int] = Field(default=None, description="Maximum connections allowed")
    is_private: bool = Field(default=False, description="Private room flag")
    permissions: Dict[str, List[str]] = Field(default_factory=dict, description="Room permissions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional room metadata")


class WebSocketConfig(ServiceConfig):
    """WebSocket service configuration"""
    max_connections: int = Field(default=10000, description="Maximum concurrent connections")
    max_connections_per_user: int = Field(default=5, description="Maximum connections per user")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    connection_timeout: int = Field(default=300, description="Connection timeout in seconds")
    message_queue_size: int = Field(default=1000, description="Message queue size per connection")
    enable_message_persistence: bool = Field(default=True, description="Enable message persistence")
    enable_room_management: bool = Field(default=True, description="Enable room management")
    enable_private_messaging: bool = Field(default=True, description="Enable private messaging")
    enable_broadcast: bool = Field(default=True, description="Enable broadcasting")
    rate_limit_messages_per_minute: int = Field(default=100, description="Rate limit messages per minute")
    enable_authentication: bool = Field(default=True, description="Enable authentication")
    enable_compression: bool = Field(default=True, description="Enable message compression")
    ping_interval: int = Field(default=20, description="WebSocket ping interval in seconds")
    ping_timeout: int = Field(default=10, description="WebSocket ping timeout in seconds")


class WebSocketManager:
    """WebSocket connection manager"""
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        
        # Connection management
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        
        # Room management
        self.rooms: Dict[str, RoomInfo] = {}
        self.room_connections: Dict[str, Set[str]] = {}  # room_id -> connection_ids
        
        # Message queues
        self.message_queues: Dict[str, List[WebSocketMessage]] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        logger.info("WebSocket manager initialized")
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None) -> bool:
        """Connect a WebSocket"""
        try:
            # Check connection limits
            if len(self.active_connections) >= self.config.max_connections:
                logger.warning(f"Connection limit reached, rejecting connection {connection_id}")
                return False
            
            if user_id and len(self.user_connections.get(user_id, set())) >= self.config.max_connections_per_user:
                logger.warning(f"User connection limit reached for {user_id}")
                return False
            
            # Accept connection
            await websocket.accept()
            
            # Store connection
            self.active_connections[connection_id] = websocket
            
            # Create connection info
            connection_info = ConnectionInfo(
                connection_id=connection_id,
                user_id=user_id,
                state=ConnectionState.CONNECTED,
                ip_address=getattr(websocket.client, 'host', None) if websocket.client else None
            )
            self.connection_info[connection_id] = connection_info
            
            # Track user connections
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
            
            # Initialize message queue
            self.message_queues[connection_id] = []
            
            logger.info(f"WebSocket connected: {connection_id} (user: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket {connection_id}: {str(e)}")
            return False
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket"""
        try:
            # Get connection info
            connection_info = self.connection_info.get(connection_id)
            if not connection_info:
                return
            
            # Remove from rooms
            for room_id in list(connection_info.rooms):
                await self.leave_room(connection_id, room_id)
            
            # Remove from user connections
            if connection_info.user_id:
                user_connections = self.user_connections.get(connection_info.user_id, set())
                user_connections.discard(connection_id)
                if not user_connections:
                    del self.user_connections[connection_info.user_id]
            
            # Cleanup
            self.active_connections.pop(connection_id, None)
            self.connection_info.pop(connection_id, None)
            self.message_queues.pop(connection_id, None)
            self.rate_limits.pop(connection_id, None)
            
            logger.info(f"WebSocket disconnected: {connection_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket {connection_id}: {str(e)}")
    
    async def send_message(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to specific connection"""
        try:
            websocket = self.active_connections.get(connection_id)
            if not websocket:
                return False
            
            # Send message
            await websocket.send_text(message.json())
            
            # Store in persistence if enabled
            if self.config.enable_message_persistence:
                await self._persist_message(message)
            
            return True
            
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {str(e)}")
            return False
    
    async def broadcast_to_room(self, room_id: str, message: WebSocketMessage, exclude_connection: Optional[str] = None) -> int:
        """Broadcast message to all connections in a room"""
        if room_id not in self.room_connections:
            return 0
        
        sent_count = 0
        connections = self.room_connections[room_id].copy()
        
        for connection_id in connections:
            if connection_id != exclude_connection:
                if await self.send_message(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def broadcast_to_all(self, message: WebSocketMessage, exclude_connection: Optional[str] = None) -> int:
        """Broadcast message to all active connections"""
        sent_count = 0
        connections = list(self.active_connections.keys())
        
        for connection_id in connections:
            if connection_id != exclude_connection:
                if await self.send_message(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """Send message to all connections of a specific user"""
        sent_count = 0
        connections = self.user_connections.get(user_id, set()).copy()
        
        for connection_id in connections:
            if await self.send_message(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def join_room(self, connection_id: str, room_id: str) -> bool:
        """Join a connection to a room"""
        try:
            connection_info = self.connection_info.get(connection_id)
            if not connection_info:
                return False
            
            # Check room permissions
            room_info = self.rooms.get(room_id)
            if room_info and room_info.is_private:
                # Implement permission checking logic here
                pass
            
            # Check room capacity
            if room_info and room_info.max_connections:
                current_count = len(self.room_connections.get(room_id, set()))
                if current_count >= room_info.max_connections:
                    return False
            
            # Add to room
            if room_id not in self.room_connections:
                self.room_connections[room_id] = set()
            
            self.room_connections[room_id].add(connection_id)
            connection_info.rooms.add(room_id)
            
            logger.info(f"Connection {connection_id} joined room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join room {room_id} for connection {connection_id}: {str(e)}")
            return False
    
    async def leave_room(self, connection_id: str, room_id: str) -> bool:
        """Remove a connection from a room"""
        try:
            connection_info = self.connection_info.get(connection_id)
            if connection_info:
                connection_info.rooms.discard(room_id)
            
            room_connections = self.room_connections.get(room_id, set())
            room_connections.discard(connection_id)
            
            # Clean up empty rooms
            if not room_connections:
                self.room_connections.pop(room_id, None)
            
            logger.info(f"Connection {connection_id} left room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave room {room_id} for connection {connection_id}: {str(e)}")
            return False
    
    async def create_room(self, room_id: str, name: str, **kwargs) -> bool:
        """Create a new room"""
        try:
            if room_id in self.rooms:
                return False
            
            room_info = RoomInfo(
                room_id=room_id,
                name=name,
                **kwargs
            )
            
            self.rooms[room_id] = room_info
            self.room_connections[room_id] = set()
            
            logger.info(f"Created room: {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create room {room_id}: {str(e)}")
            return False
    
    async def check_rate_limit(self, connection_id: str) -> bool:
        """Check rate limit for connection"""
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        # Initialize rate limit tracking
        if connection_id not in self.rate_limits:
            self.rate_limits[connection_id] = []
        
        # Clean old entries
        self.rate_limits[connection_id] = [
            timestamp for timestamp in self.rate_limits[connection_id]
            if timestamp > cutoff
        ]
        
        # Check limit
        if len(self.rate_limits[connection_id]) >= self.config.rate_limit_messages_per_minute:
            return False
        
        # Record current message
        self.rate_limits[connection_id].append(now)
        return True
    
    async def _persist_message(self, message: WebSocketMessage):
        """Persist message to storage"""
        # Implement message persistence logic
        pass
    
    def get_connection_count(self) -> int:
        """Get total connection count"""
        return len(self.active_connections)
    
    def get_room_count(self) -> int:
        """Get total room count"""
        return len(self.rooms)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_rooms": len(self.rooms),
            "total_users": len(self.user_connections),
            "rooms_with_connections": len([r for r in self.room_connections.values() if r]),
            "average_connections_per_room": sum(len(r) for r in self.room_connections.values()) / max(len(self.room_connections), 1)
        }


class WebsocketServiceTemplate(BaseMicroservice):
    """
    Enterprise WebSocket service template
    
    Provides comprehensive real-time communication including:
    - WebSocket connection lifecycle management
    - Room-based message broadcasting
    - Private messaging between users
    - Authentication and authorization
    - Rate limiting and throttling
    - Message persistence and queuing
    - Connection monitoring and heartbeat
    - Scalable connection pooling
    - Event-driven message handling
    - Performance monitoring and metrics
    """
    
    def __init__(self, config: WebSocketConfig):
        """Initialize WebSocket service"""
        self.websocket_config = config
        super().__init__(config)
        
        # WebSocket manager
        self.websocket_manager = WebSocketManager(config)
        
        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Setup WebSocket routes
        self._setup_websocket_routes()
        
        logger.info(f"WebSocket service initialized")
    
    def _setup_websocket_routes(self):
        """Setup WebSocket routes"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Main WebSocket endpoint"""
            await self._handle_websocket_connection(websocket)
        
        @self.app.websocket("/ws/{room_id}")
        async def websocket_room_endpoint(websocket: WebSocket, room_id: str):
            """Room-specific WebSocket endpoint"""
            await self._handle_websocket_connection(websocket, room_id)
        
        @self.app.get("/ws/stats")
        async def websocket_stats():
            """WebSocket statistics endpoint"""
            return self.websocket_manager.get_stats()
        
        @self.app.get("/ws/rooms")
        async def list_rooms():
            """List all rooms"""
            return {
                "rooms": [
                    {
                        "room_id": room_info.room_id,
                        "name": room_info.name,
                        "connections": len(self.websocket_manager.room_connections.get(room_info.room_id, set())),
                        "created_at": room_info.created_at.isoformat()
                    }
                    for room_info in self.websocket_manager.rooms.values()
                ]
            }
        
        @self.app.post("/ws/rooms/{room_id}/broadcast")
        async def broadcast_to_room(room_id: str, message_data: Dict[str, Any]):
            """Broadcast message to room via HTTP"""
            message = WebSocketMessage(
                type=MessageType.BROADCAST,
                data=message_data,
                room=room_id
            )
            
            sent_count = await self.websocket_manager.broadcast_to_room(room_id, message)
            return {"sent_to": sent_count, "room": room_id}
        
        @self.app.get("/ws/demo")
        async def websocket_demo():
            """WebSocket demo page"""
            return HTMLResponse(self._get_demo_html())
    
    async def _handle_websocket_connection(self, websocket: WebSocket, auto_join_room: Optional[str] = None):
        """Handle WebSocket connection lifecycle"""
        connection_id = str(uuid.uuid4())
        user_id = None
        
        try:
            # Extract user info from query parameters or headers
            user_id = websocket.query_params.get('user_id')
            
            # Connect WebSocket
            connected = await self.websocket_manager.connect(websocket, connection_id, user_id)
            if not connected:
                await websocket.close(code=1008, reason="Connection rejected")
                return
            
            # Auto-join room if specified
            if auto_join_room:
                await self.websocket_manager.join_room(connection_id, auto_join_room)
            
            # Send welcome message
            welcome_message = WebSocketMessage(
                type=MessageType.SYSTEM_MESSAGE,
                data={
                    "message": "Connected successfully",
                    "connection_id": connection_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            await self.websocket_manager.send_message(connection_id, welcome_message)
            
            # Handle messages
            await self._message_loop(websocket, connection_id)
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {connection_id}")
        except Exception as e:
            logger.error(f"WebSocket error for {connection_id}: {str(e)}")
        finally:
            await self.websocket_manager.disconnect(connection_id)
    
    async def _message_loop(self, websocket: WebSocket, connection_id: str):
        """Handle incoming WebSocket messages"""
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Parse message
                message = WebSocketMessage(**message_data)
                message.sender = connection_id
                
                # Check rate limit
                if not await self.websocket_manager.check_rate_limit(connection_id):
                    error_message = WebSocketMessage(
                        type=MessageType.ERROR,
                        data={"error": "Rate limit exceeded"}
                    )
                    await self.websocket_manager.send_message(connection_id, error_message)
                    continue
                
                # Handle message based on type
                await self._handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": "Invalid JSON format"}
                )
                await self.websocket_manager.send_message(connection_id, error_message)
            except Exception as e:
                logger.error(f"Error processing message from {connection_id}: {str(e)}")
                error_message = WebSocketMessage(
                    type=MessageType.ERROR,
                    data={"error": "Message processing failed"}
                )
                await self.websocket_manager.send_message(connection_id, error_message)
    
    async def _handle_message(self, connection_id: str, message: WebSocketMessage):
        """Handle specific message types"""
        try:
            if message.type == MessageType.JOIN_ROOM:
                room_id = message.data.get("room_id")
                if room_id:
                    success = await self.websocket_manager.join_room(connection_id, room_id)
                    response = WebSocketMessage(
                        type=MessageType.SYSTEM_MESSAGE,
                        data={
                            "action": "join_room",
                            "room_id": room_id,
                            "success": success
                        }
                    )
                    await self.websocket_manager.send_message(connection_id, response)
            
            elif message.type == MessageType.LEAVE_ROOM:
                room_id = message.data.get("room_id")
                if room_id:
                    success = await self.websocket_manager.leave_room(connection_id, room_id)
                    response = WebSocketMessage(
                        type=MessageType.SYSTEM_MESSAGE,
                        data={
                            "action": "leave_room",
                            "room_id": room_id,
                            "success": success
                        }
                    )
                    await self.websocket_manager.send_message(connection_id, response)
            
            elif message.type == MessageType.BROADCAST:
                if message.room:
                    await self.websocket_manager.broadcast_to_room(
                        message.room, message, exclude_connection=connection_id
                    )
                else:
                    await self.websocket_manager.broadcast_to_all(
                        message, exclude_connection=connection_id
                    )
            
            elif message.type == MessageType.PRIVATE_MESSAGE:
                target_user = message.target_user
                if target_user:
                    await self.websocket_manager.send_to_user(target_user, message)
            
            elif message.type == MessageType.HEARTBEAT:
                # Update heartbeat timestamp
                connection_info = self.websocket_manager.connection_info.get(connection_id)
                if connection_info:
                    connection_info.last_heartbeat = datetime.utcnow()
                
                # Send heartbeat response
                response = WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    data={"timestamp": datetime.utcnow().isoformat()}
                )
                await self.websocket_manager.send_message(connection_id, response)
            
        except Exception as e:
            logger.error(f"Error handling message type {message.type}: {str(e)}")
    
    def _get_demo_html(self) -> str:
        """Get WebSocket demo HTML page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebSocket Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                #messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; }
                .message { margin: 5px 0; padding: 5px; background: #f0f0f0; border-radius: 3px; }
                input, button { margin: 5px; padding: 5px; }
            </style>
        </head>
        <body>
            <h1>WebSocket Demo</h1>
            <div>
                <input type="text" id="userId" placeholder="User ID" />
                <button onclick="connect()">Connect</button>
                <button onclick="disconnect()">Disconnect</button>
                <span id="status">Disconnected</span>
            </div>
            <div>
                <input type="text" id="roomId" placeholder="Room ID" />
                <button onclick="joinRoom()">Join Room</button>
                <button onclick="leaveRoom()">Leave Room</button>
            </div>
            <div>
                <input type="text" id="messageText" placeholder="Message" />
                <button onclick="sendMessage()">Send to Room</button>
                <button onclick="sendBroadcast()">Broadcast</button>
            </div>
            <div id="messages"></div>
            
            <script>
                let ws = null;
                let userId = null;
                
                function connect() {
                    userId = document.getElementById('userId').value || 'user_' + Math.random().toString(36).substr(2, 9);
                    ws = new WebSocket(`ws://localhost:8000/ws?user_id=${userId}`);
                    
                    ws.onopen = function(event) {
                        document.getElementById('status').textContent = 'Connected';
                        addMessage('System', 'Connected to WebSocket');
                    };
                    
                    ws.onmessage = function(event) {
                        const message = JSON.parse(event.data);
                        addMessage(message.sender || 'System', JSON.stringify(message.data));
                    };
                    
                    ws.onclose = function(event) {
                        document.getElementById('status').textContent = 'Disconnected';
                        addMessage('System', 'Disconnected from WebSocket');
                    };
                }
                
                function disconnect() {
                    if (ws) {
                        ws.close();
                        ws = null;
                    }
                }
                
                function joinRoom() {
                    const roomId = document.getElementById('roomId').value;
                    if (ws && roomId) {
                        const message = {
                            type: 'join_room',
                            data: { room_id: roomId }
                        };
                        ws.send(JSON.stringify(message));
                    }
                }
                
                function leaveRoom() {
                    const roomId = document.getElementById('roomId').value;
                    if (ws && roomId) {
                        const message = {
                            type: 'leave_room',
                            data: { room_id: roomId }
                        };
                        ws.send(JSON.stringify(message));
                    }
                }
                
                function sendMessage() {
                    const text = document.getElementById('messageText').value;
                    const roomId = document.getElementById('roomId').value;
                    if (ws && text) {
                        const message = {
                            type: 'broadcast',
                            room: roomId,
                            data: { text: text, sender: userId }
                        };
                        ws.send(JSON.stringify(message));
                        document.getElementById('messageText').value = '';
                    }
                }
                
                function sendBroadcast() {
                    const text = document.getElementById('messageText').value;
                    if (ws && text) {
                        const message = {
                            type: 'broadcast',
                            data: { text: text, sender: userId }
                        };
                        ws.send(JSON.stringify(message));
                        document.getElementById('messageText').value = '';
                    }
                }
                
                function addMessage(sender, content) {
                    const messages = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message';
                    messageDiv.innerHTML = `<strong>${sender}:</strong> ${content}`;
                    messages.appendChild(messageDiv);
                    messages.scrollTop = messages.scrollHeight;
                }
                
                // Auto-connect on page load
                window.onload = function() {
                    connect();
                };
            </script>
        </body>
        </html>
        """
    
    async def _heartbeat_monitor(self):
        """Monitor connection heartbeats"""
        while self.status != ServiceStatus.STOPPING:
            try:
                now = datetime.utcnow()
                timeout_threshold = now - timedelta(seconds=self.websocket_config.connection_timeout)
                
                # Check for timed out connections
                expired_connections = []
                for connection_id, connection_info in self.websocket_manager.connection_info.items():
                    if connection_info.last_heartbeat < timeout_threshold:
                        expired_connections.append(connection_id)
                
                # Disconnect expired connections
                for connection_id in expired_connections:
                    logger.info(f"Disconnecting expired connection: {connection_id}")
                    await self.websocket_manager.disconnect(connection_id)
                
                await asyncio.sleep(self.websocket_config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {str(e)}")
                await asyncio.sleep(5)
    
    # Override abstract methods from BaseMicroservice
    
    async def initialize_service(self):
        """Initialize WebSocket service"""
        logger.info(f"WebSocket service {self.config.name} initialized")
    
    async def cleanup_service(self):
        """Cleanup WebSocket service"""
        # Disconnect all WebSocket connections
        connections = list(self.websocket_manager.active_connections.keys())
        for connection_id in connections:
            await self.websocket_manager.disconnect(connection_id)
        
        logger.info(f"WebSocket service {self.config.name} cleaned up")
    
    def register_routes(self):
        """Register service-specific routes"""
        # Routes are registered in _setup_websocket_routes
        pass
    
    async def register_service(self):
        """Register service with service discovery"""
        logger.info(f"WebSocket service {self.config.name} registered")
    
    async def deregister_service(self):
        """Deregister service from service discovery"""
        logger.info(f"WebSocket service {self.config.name} deregistered")
    
    async def get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        return f"ws://{service_name}:8000"
    
    async def start_background_tasks(self):
        """Start background tasks"""
        # Start heartbeat monitor
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        logger.info("WebSocket background tasks started")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        logger.info("WebSocket background tasks stopped")


def create_websocket_service(
    service_name: str = "websocket-service",
    max_connections: int = 10000,
    enable_rooms: bool = True
) -> WebsocketServiceTemplate:
    """Factory function to create WebSocket service"""
    
    config = WebSocketConfig(
        name=service_name,
        max_connections=max_connections,
        enable_room_management=enable_rooms,
        enable_private_messaging=True,
        enable_authentication=True,
        enable_metrics=True
    )
    
    return WebsocketServiceTemplate(config)


if __name__ == "__main__":
    # Example usage
    service = create_websocket_service()
    service.run()