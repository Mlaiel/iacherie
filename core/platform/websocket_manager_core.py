"""Ainflue Core WebSocket Manager - Real-time Communication Hub
==========================================================

Advanced WebSocket management providing real-time messaging, connection pooling,
room management, authentication, broadcasting, and scalable real-time features
for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
from datetime import datetime, timedelta
import weakref

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    from websockets.exceptions import ConnectionClosed, WebSocketException
except ImportError:
    websockets = None
    WebSocketServerProtocol = None
    ConnectionClosed = None
    WebSocketException = None

logger = logging.getLogger(__name__)

class ConnectionStatus(str, Enum):
    """WebSocket connection status"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class MessageType(str, Enum):
    """Message types"""
    AUTH = "auth"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    BROADCAST = "broadcast"
    PRIVATE_MESSAGE = "private_message"
    SYSTEM = "system"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    NOTIFICATION = "notification"

class RoomType(str, Enum):
    """Room types"""
    PUBLIC = "public"
    PRIVATE = "private"
    CREATOR = "creator"
    ADMIN = "admin"
    TEMPORARY = "temporary"

@dataclass
class WebSocketConnection:
    """WebSocket connection wrapper"""
    connection_id: str
    websocket: Any  # WebSocketServerProtocol
    user_id: Optional[str] = None
    status: ConnectionStatus = ConnectionStatus.CONNECTING
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)
    rooms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    permissions: Set[str] = field(default_factory=set)

@dataclass
class Room:
    """WebSocket room"""
    room_id: str
    name: str
    room_type: RoomType
    max_members: int = 1000
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    members: Set[str] = field(default_factory=set)  # connection_ids
    admins: Set[str] = field(default_factory=set)  # user_ids
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

@dataclass
class Message:
    """WebSocket message"""
    message_id: str
    message_type: MessageType
    sender_id: str
    room_id: Optional[str] = None
    recipient_id: Optional[str] = None
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WebSocketMetrics:
    """WebSocket manager metrics"""
    total_connections: int = 0
    active_connections: int = 0
    authenticated_connections: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    broadcasts_sent: int = 0
    rooms_created: int = 0
    active_rooms: int = 0
    connection_errors: int = 0
    authentication_failures: int = 0
    avg_message_processing_time: float = 0.0
    uptime_seconds: int = 0
    last_health_check: float = field(default_factory=time.time)

class WebSocketManagerCore:
    """Enterprise WebSocket manager core system"""
    
    def __init__(self, host: str = "localhost", port: int = 8765, level: str = "enterprise"):
        """Initialize WebSocket manager"""
        self.host = host
        self.port = port
        self.level = level
        self.metrics = WebSocketMetrics()
        self.start_time = time.time()
        
        # Connection management
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        
        # Room management
        self.rooms: Dict[str, Room] = {}
        
        # Message handling
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.message_history: Dict[str, List[Message]] = {}  # room_id -> messages
        self.max_history_per_room = 1000
        
        # Authentication
        self.auth_handler: Optional[Callable] = None
        self.authenticated_connections: Set[str] = set()
        
        # Server
        self.server: Optional[Any] = None
        self.is_running = False
        
        # Background tasks
        self._ping_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info(f"🌐 WebSocket Manager Core initialized - {host}:{port}")
    
    async def initialize(self) -> bool:
        """Initialize WebSocket manager"""
        try:
            logger.info("🚀 Initializing WebSocket manager core")
            
            if not websockets:
                logger.warning("⚠️ websockets library not available, using mock WebSocket manager")
                return True
            
            # Setup message handlers
            self._setup_message_handlers()
            
            # Create default rooms
            await self._create_default_rooms()
            
            logger.info("✅ WebSocket manager core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket manager initialization failed: {str(e)}")
            return False
    
    def _setup_message_handlers(self):
        """Setup default message handlers"""
        self.message_handlers = {
            MessageType.AUTH: self._handle_auth_message,
            MessageType.JOIN_ROOM: self._handle_join_room_message,
            MessageType.LEAVE_ROOM: self._handle_leave_room_message,
            MessageType.BROADCAST: self._handle_broadcast_message,
            MessageType.PRIVATE_MESSAGE: self._handle_private_message,
            MessageType.PING: self._handle_ping_message,
            MessageType.NOTIFICATION: self._handle_notification_message
        }
    
    async def _create_default_rooms(self):
        """Create default rooms"""
        default_rooms = [
            Room(
                room_id="general",
                name="General",
                room_type=RoomType.PUBLIC,
                max_members=10000
            ),
            Room(
                room_id="announcements",
                name="Announcements",
                room_type=RoomType.PUBLIC,
                max_members=50000
            ),
            Room(
                room_id="creators",
                name="Creators Only",
                room_type=RoomType.CREATOR,
                max_members=5000
            ),
            Room(
                room_id="support",
                name="Support",
                room_type=RoomType.PUBLIC,
                max_members=1000
            )
        ]
        
        for room in default_rooms:
            self.rooms[room.room_id] = room
            self.message_history[room.room_id] = []
            self.metrics.rooms_created += 1
            self.metrics.active_rooms += 1
    
    async def start(self) -> bool:
        """Start WebSocket server"""
        try:
            if not hasattr(self, '_initialized'):
                await self.initialize()
                self._initialized = True
            
            if websockets:
                # Start WebSocket server
                self.server = await websockets.serve(
                    self._handle_connection,
                    self.host,
                    self.port,
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=10
                )
                
                logger.info(f"🚀 WebSocket server started on {self.host}:{self.port}")
            
            self.is_running = True
            
            # Start background tasks
            self._ping_task = asyncio.create_task(self._ping_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            logger.info("✅ WebSocket manager core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket manager start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop WebSocket server"""
        try:
            logger.info("🛑 Stopping WebSocket manager core")
            
            self.is_running = False
            self._shutdown_event.set()
            
            # Close all connections
            for connection in list(self.connections.values()):
                try:
                    await connection.websocket.close()
                except:
                    pass
            
            # Stop server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            # Cancel background tasks
            for task in [self._ping_task, self._cleanup_task, self._health_monitor_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("✅ WebSocket manager core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket manager stop failed: {str(e)}")
            return False
    
    async def _handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        connection_id = str(uuid.uuid4())
        
        try:
            # Create connection object
            connection = WebSocketConnection(
                connection_id=connection_id,
                websocket=websocket,
                status=ConnectionStatus.CONNECTED
            )
            
            self.connections[connection_id] = connection
            self.metrics.total_connections += 1
            self.metrics.active_connections += 1
            
            logger.info(f"🔗 New WebSocket connection: {connection_id}")
            
            # Send welcome message
            await self._send_to_connection(connection_id, {
                "type": "system",
                "message": "Connected to Ainflue WebSocket",
                "connection_id": connection_id
            })
            
            # Handle messages
            async for message in websocket:
                await self._handle_message(connection_id, message)
                
        except ConnectionClosed:
            logger.info(f"🔌 Connection closed: {connection_id}")
        except WebSocketException as e:
            logger.error(f"WebSocket error for {connection_id}: {str(e)}")
            self.metrics.connection_errors += 1
        except Exception as e:
            logger.error(f"Connection handler error for {connection_id}: {str(e)}")
            self.metrics.connection_errors += 1
        finally:
            await self._cleanup_connection(connection_id)
    
    async def _handle_message(self, connection_id: str, raw_message: str):
        """Handle incoming message"""
        start_time = time.time()
        
        try:
            # Parse message
            try:
                message_data = json.loads(raw_message)
            except json.JSONDecodeError:
                await self._send_error(connection_id, "Invalid JSON format")
                return
            
            # Validate message format
            if "type" not in message_data:
                await self._send_error(connection_id, "Missing message type")
                return
            
            message_type = MessageType(message_data["type"])
            
            # Create message object
            message = Message(
                message_id=str(uuid.uuid4()),
                message_type=message_type,
                sender_id=connection_id,
                content=message_data,
                room_id=message_data.get("room_id"),
                recipient_id=message_data.get("recipient_id")
            )
            
            # Handle message
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(connection_id, message)
            else:
                await self._send_error(connection_id, f"Unknown message type: {message_type}")
            
            self.metrics.messages_received += 1
            
            # Update processing time
            processing_time = time.time() - start_time
            total_messages = self.metrics.messages_received
            self.metrics.avg_message_processing_time = (
                (self.metrics.avg_message_processing_time * (total_messages - 1) + processing_time) /
                total_messages
            )
            
        except Exception as e:
            logger.error(f"Message handling error for {connection_id}: {str(e)}")
            await self._send_error(connection_id, "Internal server error")
    
    async def _handle_auth_message(self, connection_id: str, message: Message):
        """Handle authentication message"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            # Extract auth data
            auth_data = message.content.get("auth", {})
            token = auth_data.get("token")
            user_id = auth_data.get("user_id")
            
            # Authenticate (simplified)
            if self.auth_handler:
                is_authenticated = await self.auth_handler(token, user_id)
            else:
                # Simple authentication for demo
                is_authenticated = bool(token and user_id)
            
            if is_authenticated:
                connection.status = ConnectionStatus.AUTHENTICATED
                connection.user_id = user_id
                self.authenticated_connections.add(connection_id)
                self.metrics.authenticated_connections += 1
                
                # Add to user connections
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
                
                await self._send_to_connection(connection_id, {
                    "type": "auth_success",
                    "user_id": user_id,
                    "permissions": list(connection.permissions)
                })
                
                logger.info(f"🔐 User {user_id} authenticated on connection {connection_id}")
            else:
                self.metrics.authentication_failures += 1
                await self._send_error(connection_id, "Authentication failed")
                
        except Exception as e:
            logger.error(f"Auth message handling error: {str(e)}")
            await self._send_error(connection_id, "Authentication error")
    
    async def _handle_join_room_message(self, connection_id: str, message: Message):
        """Handle join room message"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            room_id = message.content.get("room_id")
            if not room_id:
                await self._send_error(connection_id, "Missing room_id")
                return
            
            # Check if room exists
            if room_id not in self.rooms:
                await self._send_error(connection_id, f"Room '{room_id}' not found")
                return
            
            room = self.rooms[room_id]
            
            # Check permissions
            if not await self._can_join_room(connection, room):
                await self._send_error(connection_id, "Insufficient permissions")
                return
            
            # Check room capacity
            if len(room.members) >= room.max_members:
                await self._send_error(connection_id, "Room is full")
                return
            
            # Join room
            room.members.add(connection_id)
            connection.rooms.add(room_id)
            
            await self._send_to_connection(connection_id, {
                "type": "room_joined",
                "room_id": room_id,
                "room_name": room.name,
                "member_count": len(room.members)
            })
            
            # Notify other room members
            await self._broadcast_to_room(room_id, {
                "type": "user_joined",
                "user_id": connection.user_id,
                "room_id": room_id
            }, exclude_connection=connection_id)
            
            logger.info(f"👥 User {connection.user_id} joined room {room_id}")
            
        except Exception as e:
            logger.error(f"Join room message handling error: {str(e)}")
            await self._send_error(connection_id, "Join room error")
    
    async def _handle_leave_room_message(self, connection_id: str, message: Message):
        """Handle leave room message"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            room_id = message.content.get("room_id")
            if not room_id or room_id not in connection.rooms:
                await self._send_error(connection_id, "Not in room")
                return
            
            await self._remove_from_room(connection_id, room_id)
            
            await self._send_to_connection(connection_id, {
                "type": "room_left",
                "room_id": room_id
            })
            
        except Exception as e:
            logger.error(f"Leave room message handling error: {str(e)}")
    
    async def _handle_broadcast_message(self, connection_id: str, message: Message):
        """Handle broadcast message"""
        try:
            connection = self.connections.get(connection_id)
            if not connection or connection.status != ConnectionStatus.AUTHENTICATED:
                await self._send_error(connection_id, "Authentication required")
                return
            
            room_id = message.content.get("room_id")
            if not room_id:
                await self._send_error(connection_id, "Missing room_id")
                return
            
            if room_id not in connection.rooms:
                await self._send_error(connection_id, "Not in room")
                return
            
            # Broadcast message
            broadcast_data = {
                "type": "broadcast",
                "room_id": room_id,
                "sender_id": connection.user_id,
                "content": message.content.get("content", ""),
                "timestamp": message.timestamp.isoformat()
            }
            
            await self._broadcast_to_room(room_id, broadcast_data, exclude_connection=connection_id)
            
            # Store in message history
            if room_id in self.message_history:
                self.message_history[room_id].append(message)
                # Limit history size
                if len(self.message_history[room_id]) > self.max_history_per_room:
                    self.message_history[room_id] = self.message_history[room_id][-self.max_history_per_room:]
            
            self.metrics.broadcasts_sent += 1
            
        except Exception as e:
            logger.error(f"Broadcast message handling error: {str(e)}")
    
    async def _handle_private_message(self, connection_id: str, message: Message):
        """Handle private message"""
        try:
            connection = self.connections.get(connection_id)
            if not connection or connection.status != ConnectionStatus.AUTHENTICATED:
                await self._send_error(connection_id, "Authentication required")
                return
            
            recipient_id = message.content.get("recipient_id")
            if not recipient_id:
                await self._send_error(connection_id, "Missing recipient_id")
                return
            
            # Find recipient connections
            recipient_connections = self.user_connections.get(recipient_id, set())
            if not recipient_connections:
                await self._send_error(connection_id, "Recipient not online")
                return
            
            # Send to all recipient connections
            private_data = {
                "type": "private_message",
                "sender_id": connection.user_id,
                "content": message.content.get("content", ""),
                "timestamp": message.timestamp.isoformat()
            }
            
            for recipient_conn_id in recipient_connections:
                await self._send_to_connection(recipient_conn_id, private_data)
            
        except Exception as e:
            logger.error(f"Private message handling error: {str(e)}")
    
    async def _handle_ping_message(self, connection_id: str, message: Message):
        """Handle ping message"""
        connection = self.connections.get(connection_id)
        if connection:
            connection.last_ping = datetime.utcnow()
            await self._send_to_connection(connection_id, {"type": "pong"})
    
    async def _handle_notification_message(self, connection_id: str, message: Message):
        """Handle notification message"""
        try:
            connection = self.connections.get(connection_id)
            if not connection or connection.status != ConnectionStatus.AUTHENTICATED:
                return
            
            # Check if user has permission to send notifications
            if "send_notifications" not in connection.permissions:
                await self._send_error(connection_id, "Insufficient permissions")
                return
            
            # Send notification to specified users or broadcast
            target_users = message.content.get("target_users", [])
            notification_data = {
                "type": "notification",
                "title": message.content.get("title", ""),
                "message": message.content.get("message", ""),
                "timestamp": message.timestamp.isoformat()
            }
            
            if target_users:
                for user_id in target_users:
                    await self._send_to_user(user_id, notification_data)
            else:
                # Broadcast to all authenticated users
                await self._broadcast_to_authenticated(notification_data)
            
        except Exception as e:
            logger.error(f"Notification message handling error: {str(e)}")
    
    async def _can_join_room(self, connection: WebSocketConnection, room: Room) -> bool:
        """Check if connection can join room"""
        if room.room_type == RoomType.PUBLIC:
            return True
        elif room.room_type == RoomType.PRIVATE:
            return connection.user_id in room.admins
        elif room.room_type == RoomType.CREATOR:
            return "creator" in connection.permissions
        elif room.room_type == RoomType.ADMIN:
            return "admin" in connection.permissions
        else:
            return True
    
    async def _send_to_connection(self, connection_id: str, data: Dict[str, Any]) -> bool:
        """Send data to specific connection"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return False
            
            message_json = json.dumps(data)
            await connection.websocket.send(message_json)
            self.metrics.messages_sent += 1
            return True
            
        except Exception as e:
            logger.error(f"Send to connection error: {str(e)}")
            return False
    
    async def _send_to_user(self, user_id: str, data: Dict[str, Any]) -> int:
        """Send data to all connections for a user"""
        sent_count = 0
        user_connections = self.user_connections.get(user_id, set())
        
        for connection_id in user_connections.copy():
            if await self._send_to_connection(connection_id, data):
                sent_count += 1
        
        return sent_count
    
    async def _broadcast_to_room(self, room_id: str, data: Dict[str, Any], 
                               exclude_connection: Optional[str] = None) -> int:
        """Broadcast data to all members of a room"""
        if room_id not in self.rooms:
            return 0
        
        room = self.rooms[room_id]
        sent_count = 0
        
        for connection_id in room.members.copy():
            if connection_id != exclude_connection:
                if await self._send_to_connection(connection_id, data):
                    sent_count += 1
        
        return sent_count
    
    async def _broadcast_to_authenticated(self, data: Dict[str, Any]) -> int:
        """Broadcast data to all authenticated connections"""
        sent_count = 0
        
        for connection_id in self.authenticated_connections.copy():
            if await self._send_to_connection(connection_id, data):
                sent_count += 1
        
        return sent_count
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to connection"""
        await self._send_to_connection(connection_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _remove_from_room(self, connection_id: str, room_id: str):
        """Remove connection from room"""
        connection = self.connections.get(connection_id)
        if not connection:
            return
        
        if room_id in self.rooms:
            room = self.rooms[room_id]
            room.members.discard(connection_id)
            
            # Notify other members
            await self._broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": connection.user_id,
                "room_id": room_id
            }, exclude_connection=connection_id)
        
        connection.rooms.discard(room_id)
    
    async def _cleanup_connection(self, connection_id: str):
        """Clean up connection"""
        try:
            connection = self.connections.get(connection_id)
            if not connection:
                return
            
            # Remove from all rooms
            for room_id in connection.rooms.copy():
                await self._remove_from_room(connection_id, room_id)
            
            # Remove from user connections
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
            
            # Remove from authenticated connections
            self.authenticated_connections.discard(connection_id)
            
            # Remove connection
            del self.connections[connection_id]
            
            self.metrics.active_connections -= 1
            if connection.status == ConnectionStatus.AUTHENTICATED:
                self.metrics.authenticated_connections -= 1
            
            logger.info(f"🧹 Cleaned up connection: {connection_id}")
            
        except Exception as e:
            logger.error(f"Connection cleanup error: {str(e)}")
    
    async def _ping_loop(self):
        """Send periodic pings to connections"""
        while not self._shutdown_event.is_set() and self.is_running:
            try:
                current_time = datetime.utcnow()
                stale_connections = []
                
                for connection_id, connection in self.connections.items():
                    # Check for stale connections (no ping in 2 minutes)
                    if (current_time - connection.last_ping).total_seconds() > 120:
                        stale_connections.append(connection_id)
                    else:
                        # Send ping
                        await self._send_to_connection(connection_id, {"type": "ping"})
                
                # Clean up stale connections
                for connection_id in stale_connections:
                    try:
                        connection = self.connections.get(connection_id)
                        if connection:
                            await connection.websocket.close()
                    except:
                        pass
                
                await asyncio.sleep(30)  # Ping every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ping loop error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Periodic cleanup of inactive rooms and old messages"""
        while not self._shutdown_event.is_set() and self.is_running:
            try:
                # Clean up empty temporary rooms
                rooms_to_remove = []
                for room_id, room in self.rooms.items():
                    if (room.room_type == RoomType.TEMPORARY and 
                        len(room.members) == 0 and
                        (datetime.utcnow() - room.created_at).total_seconds() > 3600):  # 1 hour
                        rooms_to_remove.append(room_id)
                
                for room_id in rooms_to_remove:
                    del self.rooms[room_id]
                    if room_id in self.message_history:
                        del self.message_history[room_id]
                    self.metrics.active_rooms -= 1
                
                # Clean up old message history
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                for room_id, messages in self.message_history.items():
                    self.message_history[room_id] = [
                        msg for msg in messages
                        if msg.timestamp > cutoff_time
                    ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {str(e)}")
                await asyncio.sleep(3600)
    
    async def create_room(self, room_id: str, name: str, room_type: RoomType = RoomType.PUBLIC,
                         max_members: int = 1000, created_by: Optional[str] = None) -> bool:
        """Create new room"""
        try:
            if room_id in self.rooms:
                return False
            
            room = Room(
                room_id=room_id,
                name=name,
                room_type=room_type,
                max_members=max_members,
                created_by=created_by
            )
            
            if created_by:
                room.admins.add(created_by)
            
            self.rooms[room_id] = room
            self.message_history[room_id] = []
            self.metrics.rooms_created += 1
            self.metrics.active_rooms += 1
            
            logger.info(f"🏠 Created room '{room_id}' ({room_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Room creation error: {str(e)}")
            return False
    
    async def send_notification(self, title: str, message: str, target_users: Optional[List[str]] = None) -> int:
        """Send notification to users"""
        notification_data = {
            "type": "notification",
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if target_users:
            sent_count = 0
            for user_id in target_users:
                sent_count += await self._send_to_user(user_id, notification_data)
            return sent_count
        else:
            return await self._broadcast_to_authenticated(notification_data)
    
    async def health_check(self) -> bool:
        """Perform WebSocket manager health check"""
        try:
            # Check if server is running
            if not self.is_running:
                return False
            
            # Check connection health
            healthy_connections = 0
            for connection in self.connections.values():
                if (datetime.utcnow() - connection.last_ping).total_seconds() < 300:  # 5 minutes
                    healthy_connections += 1
            
            # Update metrics
            self.metrics.uptime_seconds = int(time.time() - self.start_time)
            self.metrics.last_health_check = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"WebSocket health monitor error: {str(e)}")
                await asyncio.sleep(600)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get WebSocket manager metrics"""
        return {
            "total_connections": self.metrics.total_connections,
            "active_connections": self.metrics.active_connections,
            "authenticated_connections": self.metrics.authenticated_connections,
            "messages_sent": self.metrics.messages_sent,
            "messages_received": self.metrics.messages_received,
            "broadcasts_sent": self.metrics.broadcasts_sent,
            "rooms_created": self.metrics.rooms_created,
            "active_rooms": self.metrics.active_rooms,
            "connection_errors": self.metrics.connection_errors,
            "authentication_failures": self.metrics.authentication_failures,
            "avg_message_processing_time_ms": round(self.metrics.avg_message_processing_time * 1000, 2),
            "uptime_seconds": int(time.time() - self.start_time),
            "is_running": self.is_running
        }
    
    def get_room_info(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get room information"""
        room = self.rooms.get(room_id)
        if not room:
            return None
        
        return {
            "room_id": room.room_id,
            "name": room.name,
            "room_type": room.room_type.value,
            "member_count": len(room.members),
            "max_members": room.max_members,
            "created_at": room.created_at.isoformat(),
            "created_by": room.created_by,
            "is_active": room.is_active
        }

# Module exports
__all__ = [
    "WebSocketManagerCore", "WebSocketConnection", "Room", "Message",
    "ConnectionStatus", "MessageType", "RoomType", "WebSocketMetrics"
]