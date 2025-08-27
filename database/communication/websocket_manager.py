"""
WebSocket Connection Management Database

Enterprise WebSocket connection management with real-time message routing,
connection pooling, and collaboration coordination for multi-format creators.

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
"""

import uuid
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from websockets import WebSocketServerProtocol
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """WebSocket connection status"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"
    IDLE = "idle"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class MessageType(Enum):
    """Real-time message types"""
    CHAT = "chat"
    COLLABORATION = "collaboration"
    NOTIFICATION = "notification"
    SYSTEM = "system"
    STREAMING = "streaming"
    FILE_SHARE = "file_share"
    VOICE_CALL = "voice_call"
    VIDEO_CALL = "video_call"
    SCREEN_SHARE = "screen_share"
    WORKFLOW = "workflow"


class RoomType(Enum):
    """Collaboration room types"""
    PROJECT = "project"
    MUSIC_SESSION = "music_session"
    LIVE_STREAM = "live_stream"
    EDITORIAL = "editorial"
    PHOTO_REVIEW = "photo_review"
    COMEDY_WORKSHOP = "comedy_workshop"
    BRAND_MEETING = "brand_meeting"
    PRIVATE_CHAT = "private_chat"


@dataclass
class ConnectionInfo:
    """WebSocket connection information"""
    connection_id: str
    user_id: str
    creator_type: str
    device_info: Dict[str, Any]
    location: Dict[str, Any]
    connected_at: datetime
    last_activity: datetime
    status: ConnectionStatus
    rooms: Set[str]
    metadata: Dict[str, Any]


class WebSocketConnection(Base):
    """
    Database model for WebSocket connection tracking
    """
    __tablename__ = "websocket_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(String(128), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_type = Column(String(50), nullable=False)
    
    # Connection details
    device_type = Column(String(20))
    browser_info = Column(JSON)
    ip_address = Column(String(45))
    location_data = Column(JSON)
    
    # Connection lifecycle
    connected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    disconnected_at = Column(DateTime(timezone=True))
    connection_duration = Column(Integer)  # seconds
    
    # Status and performance
    status = Column(String(20), default="connecting", nullable=False)
    message_count = Column(Integer, default=0)
    bytes_transferred = Column(BigInteger, default=0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Collaboration context
    active_rooms = Column(JSON, default=list)
    collaboration_sessions = Column(JSON, default=list)
    current_activity = Column(String(100))
    
    # Quality metrics
    latency_ms = Column(Integer)
    packet_loss_rate = Column(Integer, default=0)
    reconnection_count = Column(Integer, default=0)
    
    # Metadata
    connection_metadata = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_websocket_user_status', 'user_id', 'status'),
        Index('idx_websocket_connected_at', 'connected_at'),
        Index('idx_websocket_last_activity', 'last_activity'),
        Index('idx_websocket_creator_type', 'creator_type'),
    )


class MessageHistory(Base):
    """
    Database model for real-time message history
    """
    __tablename__ = "message_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(128), unique=True, nullable=False, index=True)
    connection_id = Column(String(128), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Message content
    message_type = Column(String(50), nullable=False)
    room_id = Column(String(128), index=True)
    target_user_id = Column(UUID(as_uuid=True), index=True)
    message_content = Column(JSON, nullable=False)
    
    # Delivery tracking
    sent_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    delivery_status = Column(String(20), default="sent")
    
    # Message metadata
    content_type = Column(String(50))  # text, image, audio, video, file
    file_attachments = Column(JSON)
    encryption_key = Column(String(128))
    priority_level = Column(Integer, default=1)
    
    # Collaboration context
    collaboration_id = Column(UUID(as_uuid=True))
    thread_id = Column(String(128))
    reply_to_message_id = Column(String(128))
    
    # Performance tracking
    message_size_bytes = Column(Integer)
    processing_time_ms = Column(Integer)
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_message_room_sent', 'room_id', 'sent_at'),
        Index('idx_message_user_sent', 'user_id', 'sent_at'),
        Index('idx_message_type_sent', 'message_type', 'sent_at'),
        Index('idx_message_collaboration', 'collaboration_id'),
    )


class CollaborationRoom(Base):
    """
    Database model for real-time collaboration rooms
    """
    __tablename__ = "collaboration_rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(String(128), unique=True, nullable=False, index=True)
    room_name = Column(String(200), nullable=False)
    room_type = Column(String(50), nullable=False)
    creator_user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Room configuration
    max_participants = Column(Integer, default=50)
    current_participants = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    
    # Content and context
    project_id = Column(UUID(as_uuid=True), index=True)
    room_description = Column(Text)
    room_tags = Column(JSON)
    active_document_id = Column(String(128))
    
    # Room lifecycle
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime(timezone=True))
    
    # Participants and permissions
    participants = Column(JSON, default=list)
    moderators = Column(JSON, default=list)
    permissions = Column(JSON)
    
    # Activity metrics
    total_messages = Column(Integer, default=0)
    total_files_shared = Column(Integer, default=0)
    session_duration = Column(Integer, default=0)  # seconds
    
    # Room settings
    settings = Column(JSON)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_room_creator_type', 'creator_user_id', 'room_type'),
        Index('idx_room_project', 'project_id'),
        Index('idx_room_last_activity', 'last_activity'),
        Index('idx_room_public', 'is_public'),
    )


class ConnectionPool:
    """
    WebSocket connection pool management
    """
    
    def __init__(self):
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.room_connections: Dict[str, Set[str]] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self._cleanup_task = None
    
    async def add_connection(
        self,
        connection_id: str,
        websocket: WebSocketServerProtocol,
        user_id: str,
        creator_type: str,
        device_info: Dict[str, Any],
        location: Dict[str, Any]
    ):
        """Add new WebSocket connection to pool"""
        self.connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        connection_info = ConnectionInfo(
            connection_id=connection_id,
            user_id=user_id,
            creator_type=creator_type,
            device_info=device_info,
            location=location,
            connected_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            status=ConnectionStatus.CONNECTED,
            rooms=set(),
            metadata={}
        )
        self.connection_info[connection_id] = connection_info
        
        logger.info(f"Added WebSocket connection: {connection_id} for user: {user_id}")
    
    async def remove_connection(self, connection_id: str):
        """Remove connection from pool"""
        if connection_id in self.connections:
            connection_info = self.connection_info.get(connection_id)
            if connection_info:
                # Remove from user connections
                user_id = connection_info.user_id
                if user_id in self.user_connections:
                    self.user_connections[user_id].discard(connection_id)
                    if not self.user_connections[user_id]:
                        del self.user_connections[user_id]
                
                # Remove from rooms
                for room_id in connection_info.rooms:
                    if room_id in self.room_connections:
                        self.room_connections[room_id].discard(connection_id)
                        if not self.room_connections[room_id]:
                            del self.room_connections[room_id]
            
            del self.connections[connection_id]
            if connection_id in self.connection_info:
                del self.connection_info[connection_id]
            
            logger.info(f"Removed WebSocket connection: {connection_id}")
    
    def get_connection(self, connection_id: str) -> Optional[WebSocketServerProtocol]:
        """Get WebSocket connection by ID"""
        return self.connections.get(connection_id)
    
    def get_user_connections(self, user_id: str) -> List[str]:
        """Get all connection IDs for a user"""
        return list(self.user_connections.get(user_id, set()))
    
    def get_room_connections(self, room_id: str) -> List[str]:
        """Get all connection IDs in a room"""
        return list(self.room_connections.get(room_id, set()))
    
    async def join_room(self, connection_id: str, room_id: str):
        """Add connection to a collaboration room"""
        if connection_id in self.connection_info:
            self.connection_info[connection_id].rooms.add(room_id)
            
            if room_id not in self.room_connections:
                self.room_connections[room_id] = set()
            self.room_connections[room_id].add(connection_id)
    
    async def leave_room(self, connection_id: str, room_id: str):
        """Remove connection from a collaboration room"""
        if connection_id in self.connection_info:
            self.connection_info[connection_id].rooms.discard(room_id)
            
            if room_id in self.room_connections:
                self.room_connections[room_id].discard(connection_id)
                if not self.room_connections[room_id]:
                    del self.room_connections[room_id]
    
    def update_activity(self, connection_id: str):
        """Update last activity timestamp"""
        if connection_id in self.connection_info:
            self.connection_info[connection_id].last_activity = datetime.now(timezone.utc)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.connections)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        creator_types = {}
        for info in self.connection_info.values():
            creator_type = info.creator_type
            creator_types[creator_type] = creator_types.get(creator_type, 0) + 1
        
        return {
            'total_connections': len(self.connections),
            'total_users': len(self.user_connections),
            'total_rooms': len(self.room_connections),
            'creator_type_distribution': creator_types,
            'avg_connections_per_user': len(self.connections) / max(len(self.user_connections), 1)
        }


class WebSocketManager:
    """
    Enterprise WebSocket connection manager with database persistence
    """
    
    def __init__(
        self,
        db_session: Session,
        redis_client: redis.Redis,
        connection_pool: ConnectionPool
    ):
        self.db_session = db_session
        self.redis_client = redis_client
        self.connection_pool = connection_pool
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.room_handlers: Dict[str, List[Callable]] = {}
    
    async def register_connection(
        self,
        websocket: WebSocketServerProtocol,
        user_id: str,
        creator_type: str,
        device_info: Dict[str, Any],
        auth_context: Dict[str, Any]
    ) -> str:
        """
        Register new WebSocket connection with full tracking
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
            creator_type: Type of creator
            device_info: Device and location information
            auth_context: Authentication context
            
        Returns:
            Connection ID
        """
        connection_id = str(uuid.uuid4())
        
        # Add to connection pool
        await self.connection_pool.add_connection(
            connection_id=connection_id,
            websocket=websocket,
            user_id=user_id,
            creator_type=creator_type,
            device_info=device_info,
            location=device_info.get('location', {})
        )
        
        # Store in database
        connection_record = WebSocketConnection(
            connection_id=connection_id,
            user_id=user_id,
            creator_type=creator_type,
            device_type=device_info.get('type'),
            browser_info=device_info.get('browser'),
            ip_address=device_info.get('ip_address'),
            location_data=device_info.get('location'),
            status="connected",
            connection_metadata=auth_context
        )
        
        self.db_session.add(connection_record)
        self.db_session.commit()
        
        # Cache in Redis
        await self._cache_connection_in_redis(connection_id, user_id, creator_type)
        
        logger.info(f"Registered WebSocket connection: {connection_id} for user: {user_id}")
        return connection_id
    
    async def unregister_connection(self, connection_id: str, reason: str = "normal"):
        """
        Unregister WebSocket connection with cleanup
        
        Args:
            connection_id: Connection to unregister
            reason: Disconnection reason
        """
        # Update database
        connection_record = self.db_session.query(WebSocketConnection).filter(
            WebSocketConnection.connection_id == connection_id
        ).first()
        
        if connection_record:
            now = datetime.now(timezone.utc)
            connection_record.disconnected_at = now
            connection_record.status = "disconnected"
            connection_record.connection_duration = int(
                (now - connection_record.connected_at).total_seconds()
            )
            connection_record.is_active = False
            
            self.db_session.commit()
        
        # Remove from pool
        await self.connection_pool.remove_connection(connection_id)
        
        # Remove from Redis cache
        await self.redis_client.delete(f"ws_connection:{connection_id}")
        
        logger.info(f"Unregistered WebSocket connection: {connection_id}, reason: {reason}")
    
    async def send_message(
        self,
        connection_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        room_id: Optional[str] = None
    ) -> bool:
        """
        Send message to specific connection
        
        Args:
            connection_id: Target connection
            message_type: Type of message
            content: Message content
            room_id: Optional room context
            
        Returns:
            Success status
        """
        websocket = self.connection_pool.get_connection(connection_id)
        if not websocket:
            return False
        
        message_id = str(uuid.uuid4())
        message_data = {
            'message_id': message_id,
            'type': message_type.value,
            'content': content,
            'room_id': room_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            await websocket.send(json.dumps(message_data))
            
            # Log message in database
            await self._log_message(
                message_id=message_id,
                connection_id=connection_id,
                message_type=message_type,
                content=content,
                room_id=room_id
            )
            
            # Update connection activity
            self.connection_pool.update_activity(connection_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {str(e)}")
            return False
    
    async def broadcast_to_room(
        self,
        room_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ):
        """
        Broadcast message to all connections in a room
        
        Args:
            room_id: Target room
            message_type: Type of message
            content: Message content
            exclude_connection: Connection to exclude from broadcast
        """
        room_connections = self.connection_pool.get_room_connections(room_id)
        
        for connection_id in room_connections:
            if connection_id != exclude_connection:
                await self.send_message(connection_id, message_type, content, room_id)
    
    async def broadcast_to_user(
        self,
        user_id: str,
        message_type: MessageType,
        content: Dict[str, Any]
    ):
        """
        Broadcast message to all user connections
        
        Args:
            user_id: Target user
            message_type: Type of message
            content: Message content
        """
        user_connections = self.connection_pool.get_user_connections(user_id)
        
        for connection_id in user_connections:
            await self.send_message(connection_id, message_type, content)
    
    async def create_collaboration_room(
        self,
        room_name: str,
        room_type: RoomType,
        creator_user_id: str,
        config: Dict[str, Any]
    ) -> str:
        """
        Create new collaboration room
        
        Args:
            room_name: Name of the room
            room_type: Type of collaboration room
            creator_user_id: Room creator
            config: Room configuration
            
        Returns:
            Room ID
        """
        room_id = str(uuid.uuid4())
        
        room_record = CollaborationRoom(
            room_id=room_id,
            room_name=room_name,
            room_type=room_type.value,
            creator_user_id=creator_user_id,
            max_participants=config.get('max_participants', 50),
            is_public=config.get('is_public', False),
            requires_approval=config.get('requires_approval', True),
            project_id=config.get('project_id'),
            room_description=config.get('description'),
            room_tags=config.get('tags', []),
            permissions=config.get('permissions', {}),
            settings=config
        )
        
        self.db_session.add(room_record)
        self.db_session.commit()
        
        # Cache room in Redis
        await self._cache_room_in_redis(room_id, room_record)
        
        logger.info(f"Created collaboration room: {room_id} ({room_type.value}) by user: {creator_user_id}")
        return room_id
    
    async def join_collaboration_room(
        self,
        connection_id: str,
        room_id: str,
        user_id: str
    ) -> bool:
        """
        Join user connection to collaboration room
        
        Args:
            connection_id: Connection to add
            room_id: Room to join
            user_id: User identifier
            
        Returns:
            Success status
        """
        # Check room exists and permissions
        room_record = self.db_session.query(CollaborationRoom).filter(
            CollaborationRoom.room_id == room_id,
            CollaborationRoom.is_active == True
        ).first()
        
        if not room_record:
            return False
        
        # Check capacity
        if room_record.current_participants >= room_record.max_participants:
            return False
        
        # Add to connection pool
        await self.connection_pool.join_room(connection_id, room_id)
        
        # Update room participants
        participants = room_record.participants or []
        if user_id not in participants:
            participants.append(user_id)
            room_record.participants = participants
            room_record.current_participants = len(participants)
            room_record.last_activity = datetime.now(timezone.utc)
            
            self.db_session.commit()
        
        # Notify other room members
        await self.broadcast_to_room(
            room_id=room_id,
            message_type=MessageType.SYSTEM,
            content={
                'event': 'user_joined',
                'user_id': user_id,
                'room_id': room_id
            },
            exclude_connection=connection_id
        )
        
        return True
    
    async def leave_collaboration_room(
        self,
        connection_id: str,
        room_id: str,
        user_id: str
    ):
        """
        Remove user connection from collaboration room
        
        Args:
            connection_id: Connection to remove
            room_id: Room to leave
            user_id: User identifier
        """
        # Remove from connection pool
        await self.connection_pool.leave_room(connection_id, room_id)
        
        # Update room participants if no other connections from same user
        user_connections = self.connection_pool.get_user_connections(user_id)
        room_connections = self.connection_pool.get_room_connections(room_id)
        
        user_still_in_room = any(
            conn_id in room_connections for conn_id in user_connections
        )
        
        if not user_still_in_room:
            room_record = self.db_session.query(CollaborationRoom).filter(
                CollaborationRoom.room_id == room_id
            ).first()
            
            if room_record and room_record.participants:
                participants = room_record.participants
                if user_id in participants:
                    participants.remove(user_id)
                    room_record.participants = participants
                    room_record.current_participants = len(participants)
                    room_record.last_activity = datetime.now(timezone.utc)
                    
                    self.db_session.commit()
            
            # Notify other room members
            await self.broadcast_to_room(
                room_id=room_id,
                message_type=MessageType.SYSTEM,
                content={
                    'event': 'user_left',
                    'user_id': user_id,
                    'room_id': room_id
                }
            )
    
    async def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """Get list of room participants with status"""
        room_record = self.db_session.query(CollaborationRoom).filter(
            CollaborationRoom.room_id == room_id
        ).first()
        
        if not room_record:
            return []
        
        participants = []
        room_connections = self.connection_pool.get_room_connections(room_id)
        
        for user_id in room_record.participants or []:
            user_connections = self.connection_pool.get_user_connections(user_id)
            is_online = any(conn_id in room_connections for conn_id in user_connections)
            
            participant_info = {
                'user_id': user_id,
                'is_online': is_online,
                'connection_count': len([c for c in user_connections if c in room_connections])
            }
            participants.append(participant_info)
        
        return participants
    
    async def _cache_connection_in_redis(
        self,
        connection_id: str,
        user_id: str,
        creator_type: str
    ):
        """Cache connection info in Redis"""
        connection_data = {
            'user_id': user_id,
            'creator_type': creator_type,
            'connected_at': datetime.now(timezone.utc).isoformat()
        }
        
        await self.redis_client.setex(
            f"ws_connection:{connection_id}",
            3600,  # 1 hour TTL
            json.dumps(connection_data)
        )
    
    async def _cache_room_in_redis(self, room_id: str, room_record: CollaborationRoom):
        """Cache room info in Redis"""
        room_data = {
            'room_name': room_record.room_name,
            'room_type': room_record.room_type,
            'creator_user_id': str(room_record.creator_user_id),
            'max_participants': room_record.max_participants,
            'current_participants': room_record.current_participants,
            'is_public': room_record.is_public
        }
        
        await self.redis_client.setex(
            f"collaboration_room:{room_id}",
            3600,  # 1 hour TTL
            json.dumps(room_data)
        )
    
    async def _log_message(
        self,
        message_id: str,
        connection_id: str,
        message_type: MessageType,
        content: Dict[str, Any],
        room_id: Optional[str]
    ):
        """Log message to database"""
        connection_info = self.connection_pool.connection_info.get(connection_id)
        if not connection_info:
            return
        
        message_record = MessageHistory(
            message_id=message_id,
            connection_id=connection_id,
            user_id=connection_info.user_id,
            message_type=message_type.value,
            room_id=room_id,
            message_content=content,
            content_type=content.get('type', 'text'),
            message_size_bytes=len(json.dumps(content))
        )
        
        self.db_session.add(message_record)
        self.db_session.commit()
    
    def register_message_handler(
        self,
        message_type: MessageType,
        handler: Callable
    ):
        """Register message handler for specific message type"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def handle_incoming_message(
        self,
        connection_id: str,
        raw_message: str
    ):
        """Process incoming WebSocket message"""
        try:
            message_data = json.loads(raw_message)
            message_type = MessageType(message_data.get('type'))
            
            # Update connection activity
            self.connection_pool.update_activity(connection_id)
            
            # Call registered handlers
            handlers = self.message_handlers.get(message_type, [])
            for handler in handlers:
                await handler(connection_id, message_data)
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Invalid message from {connection_id}: {str(e)}")
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """Clean up inactive connections"""
        timeout = timedelta(minutes=timeout_minutes)
        cutoff_time = datetime.now(timezone.utc) - timeout
        
        inactive_connections = []
        for connection_id, info in self.connection_pool.connection_info.items():
            if info.last_activity < cutoff_time:
                inactive_connections.append(connection_id)
        
        for connection_id in inactive_connections:
            await self.unregister_connection(connection_id, "timeout")
        
        return len(inactive_connections)
