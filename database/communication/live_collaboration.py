"""
Live Collaboration Database Management

Enterprise real-time collaboration system for multi-format creators including
musicians, bloggers, photographers, comedians, and brand ambassadors.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql import func
import logging
from contextlib import asynccontextmanager

Base = declarative_base()
logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of collaboration for creators"""
    MUSIC_PRODUCTION = "music_production"
    CONTENT_CREATION = "content_creation"
    PHOTO_EDITING = "photo_editing"
    VIDEO_PRODUCTION = "video_production"
    BRAND_CAMPAIGN = "brand_campaign"
    LIVE_STREAMING = "live_streaming"
    PODCAST_RECORDING = "podcast_recording"
    COMEDY_WRITING = "comedy_writing"
    CROSS_PROMOTION = "cross_promotion"
    MENTORING = "mentoring"


class RoomStatus(Enum):
    """Collaboration room status"""
    CREATING = "creating"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    CLOSED = "closed"
    EXPIRED = "expired"


class ParticipantRole(Enum):
    """Participant roles in collaboration"""
    OWNER = "owner"
    MODERATOR = "moderator"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"
    GUEST = "guest"


class ParticipantStatus(Enum):
    """Participant connection status"""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"
    INVISIBLE = "invisible"


class ActivityType(Enum):
    """Collaboration activity types"""
    JOIN = "join"
    LEAVE = "leave"
    MESSAGE = "message"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    EDIT = "edit"
    COMMENT = "comment"
    REACTION = "reaction"
    SCREEN_SHARE = "screen_share"
    VOICE_CALL = "voice_call"
    VIDEO_CALL = "video_call"
    PERMISSION_CHANGE = "permission_change"


class ContentFormat(Enum):
    """Supported content formats for collaboration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    CODE = "code"
    DESIGN = "design"


@dataclass
class CollaborationPermissions:
    """Collaboration permissions structure"""
    can_edit: bool = False
    can_comment: bool = True
    can_share: bool = False
    can_invite: bool = False
    can_moderate: bool = False
    can_export: bool = False
    can_delete: bool = False


@dataclass
class RoomSettings:
    """Collaboration room settings"""
    max_participants: int = 50
    is_public: bool = False
    requires_approval: bool = True
    enable_chat: bool = True
    enable_voice: bool = True
    enable_video: bool = True
    enable_screen_share: bool = True
    enable_file_sharing: bool = True
    auto_save_interval: int = 30  # seconds
    session_timeout: int = 3600   # seconds


class CollaborationRoom(Base):
    """Collaboration room model"""
    __tablename__ = "collaboration_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    collaboration_type = Column(String(100), nullable=False)
    
    # Ownership
    owner_id = Column(String(255), nullable=False, index=True)
    owner_creator_type = Column(String(50))
    
    # Status and settings
    status = Column(String(50), default=RoomStatus.CREATING.value)
    settings = Column(JSON)
    
    # Content and formats
    supported_formats = Column(ARRAY(String))
    primary_content_type = Column(String(50))
    
    # Access control
    is_public = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    invite_code = Column(String(50), unique=True)
    max_participants = Column(Integer, default=50)
    
    # Scheduling
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime(timezone=True))
    
    # Statistics
    total_participants = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    total_files_shared = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    
    # Content protection
    content_protection_enabled = Column(Boolean, default=True)
    ai_monitoring_enabled = Column(Boolean, default=True)
    
    tags = Column(ARRAY(String))
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_room_owner_type', 'owner_id', 'collaboration_type'),
        Index('idx_room_status_scheduled', 'status', 'scheduled_start'),
    )


class RoomParticipant(Base):
    """Room participant model"""
    __tablename__ = "room_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    creator_type = Column(String(50))
    
    # Participation details
    role = Column(String(50), default=ParticipantRole.COLLABORATOR.value)
    status = Column(String(50), default=ParticipantStatus.OFFLINE.value)
    permissions = Column(JSON)
    
    # Connection info
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime(timezone=True))
    last_active = Column(DateTime(timezone=True))
    total_time_seconds = Column(Integer, default=0)
    
    # Invitation details
    invited_by = Column(String(255))
    invited_at = Column(DateTime(timezone=True))
    invitation_accepted_at = Column(DateTime(timezone=True))
    
    # Activity metrics
    messages_sent = Column(Integer, default=0)
    files_shared = Column(Integer, default=0)
    edits_made = Column(Integer, default=0)
    
    # Device and connection
    device_info = Column(JSON)
    connection_quality = Column(String(50))
    
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_participant_room_user', 'room_id', 'user_id'),
        Index('idx_participant_status_active', 'status', 'is_active'),
    )


class CollaborationActivity(Base):
    """Collaboration activity tracking"""
    __tablename__ = "collaboration_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False)
    
    # Activity details
    description = Column(Text)
    details = Column(JSON)
    affected_resource = Column(String(255))
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    session_id = Column(String(255))
    device_info = Column(JSON)
    
    # Content tracking
    content_before = Column(JSON)
    content_after = Column(JSON)
    change_summary = Column(Text)
    
    # AI analysis
    ai_sentiment = Column(String(50))
    ai_summary = Column(Text)
    ai_insights = Column(JSON)

    __table_args__ = (
        Index('idx_activity_room_time', 'room_id', 'timestamp'),
        Index('idx_activity_user_type', 'user_id', 'activity_type'),
    )


class SharedContent(Base):
    """Shared content in collaboration rooms"""
    __tablename__ = "shared_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, unique=True, index=True)
    room_id = Column(String(255), nullable=False, index=True)
    owner_id = Column(String(255), nullable=False, index=True)
    
    # Content details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(String(100), nullable=False)
    format = Column(String(50))
    size_bytes = Column(BigInteger)
    
    # Storage
    storage_path = Column(String(500))
    storage_provider = Column(String(100))
    download_url = Column(String(500))
    preview_url = Column(String(500))
    
    # Permissions
    is_public = Column(Boolean, default=False)
    download_allowed = Column(Boolean, default=True)
    edit_allowed = Column(Boolean, default=False)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_content_id = Column(String(255))
    is_latest_version = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True))
    
    # Analytics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    edit_count = Column(Integer, default=0)
    
    # AI processing
    ai_analysis = Column(JSON)
    content_fingerprint = Column(String(255))
    protection_status = Column(String(50))
    
    tags = Column(ARRAY(String))
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_content_room_type', 'room_id', 'content_type'),
        Index('idx_content_owner_created', 'owner_id', 'created_at'),
    )


class CollaborationMessage(Base):
    """Real-time messages in collaboration rooms"""
    __tablename__ = "collaboration_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(255), nullable=False, unique=True, index=True)
    room_id = Column(String(255), nullable=False, index=True)
    sender_id = Column(String(255), nullable=False, index=True)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, file, image, audio, video
    format = Column(String(50))
    
    # Threading
    thread_id = Column(String(255))
    reply_to_message_id = Column(String(255))
    
    # Attachments
    attachments = Column(JSON)
    
    # Status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Delivery tracking
    delivered_to = Column(ARRAY(String))
    read_by = Column(JSON)  # {user_id: timestamp}
    
    # AI analysis
    ai_sentiment = Column(String(50))
    ai_summary = Column(Text)
    ai_language = Column(String(10))
    
    # Moderation
    is_flagged = Column(Boolean, default=False)
    moderation_status = Column(String(50))
    moderation_reason = Column(Text)
    
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_message_room_sent', 'room_id', 'sent_at'),
        Index('idx_message_sender_sent', 'sender_id', 'sent_at'),
        Index('idx_message_thread', 'thread_id'),
    )


class CollaborationSession(Base):
    """Collaboration session tracking"""
    __tablename__ = "collaboration_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    room_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Session details
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Connection info
    device_type = Column(String(50))
    browser = Column(String(100))
    ip_address = Column(String(45))
    location = Column(JSON)
    
    # Quality metrics
    connection_quality = Column(String(50))
    avg_latency_ms = Column(Integer)
    disconnect_count = Column(Integer, default=0)
    
    # Activity summary
    messages_sent = Column(Integer, default=0)
    files_uploaded = Column(Integer, default=0)
    edits_made = Column(Integer, default=0)
    voice_time_seconds = Column(Integer, default=0)
    video_time_seconds = Column(Integer, default=0)
    
    metadata = Column(JSON)

    __table_args__ = (
        Index('idx_session_room_started', 'room_id', 'started_at'),
        Index('idx_session_user_started', 'user_id', 'started_at'),
    )


class LiveCollaboration:
    """Enterprise live collaboration system"""
    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.active_rooms: Dict[str, Dict[str, Any]] = {}
        self.room_subscribers: Dict[str, Set[Callable]] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
    
    async def initialize(self):
        """Initialize collaboration system"""



        try:
            # Load active rooms
            await self._load_active_rooms()
            
            # Start background workers
            await self._start_workers()
            
            self.running = True
            logger.info("Live collaboration system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize collaboration system: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Close all active rooms
        for room_id in list(self.active_rooms.keys()):
            await self._close_room(room_id)
        
        # Stop workers
        for task in self.worker_tasks:
            task.cancel()
        
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        logger.info("Live collaboration system shutdown completed")
    
    async def create_room(
        self,
        owner_id: str,
        name: str,
        collaboration_type: CollaborationType,
        settings: Optional[RoomSettings] = None,
        scheduled_start: Optional[datetime] = None,
        scheduled_end: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> str:
        """Create new collaboration room"""



        try:
            room_id = f"room_{uuid.uuid4().hex[:12]}"
            
            # Create room record
            room = CollaborationRoom(
                room_id=room_id,
                name=name,
                description=description,
                collaboration_type=collaboration_type.value,
                owner_id=owner_id,
                settings=asdict(settings) if settings else asdict(RoomSettings()),
                scheduled_start=scheduled_start,
                scheduled_end=scheduled_end,
                invite_code=uuid.uuid4().hex[:8].upper(),
                status=RoomStatus.CREATING.value
            )
            
            self.db.add(room)
            
            # Add owner as participant
            owner_participant = RoomParticipant(
                room_id=room_id,
                user_id=owner_id,
                role=ParticipantRole.OWNER.value,
                permissions=asdict(CollaborationPermissions(
                    can_edit=True,
                    can_comment=True,
                    can_share=True,
                    can_invite=True,
                    can_moderate=True,
                    can_export=True,
                    can_delete=True
                )),
                joined_at=datetime.now(timezone.utc)
            )
            
            self.db.add(owner_participant)
            self.db.commit()
            
            # Initialize in Redis
            await self._initialize_room_redis(room_id)
            
            # Track creation activity
            await self._log_activity(
                room_id=room_id,
                user_id=owner_id,
                activity_type=ActivityType.JOIN,
                description=f"Created collaboration room: {name}"
            )
            
            logger.info(f"Created collaboration room {room_id} by {owner_id}")
            return room_id
            
        except Exception as e:
            logger.error(f"Failed to create room: {e}")
            self.db.rollback()
            raise
    
    async def join_room(
        self,
        room_id: str,
        user_id: str,
        invite_code: Optional[str] = None,
        role: ParticipantRole = ParticipantRole.COLLABORATOR
    ) -> bool:
        """Join collaboration room"""



        try:
            # Get room
            room = self.db.query(CollaborationRoom).filter(
                CollaborationRoom.room_id == room_id,
                CollaborationRoom.status.in_([RoomStatus.CREATING.value, RoomStatus.ACTIVE.value])
            ).first()
            
            if not room:
                raise ValueError(f"Room {room_id} not found or not accessible")
            
            # Check access permissions
            if not room.is_public and room.requires_approval:
                if invite_code != room.invite_code:
                    raise ValueError("Invalid invite code")
            
            # Check if already participant
            existing = self.db.query(RoomParticipant).filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id,
                RoomParticipant.is_active == True
            ).first()
            
            if existing:
                # Update status to online
                existing.status = ParticipantStatus.ONLINE.value
                existing.last_active = datetime.now(timezone.utc)
            else:
                # Check participant limit
                current_participants = self.db.query(RoomParticipant).filter(
                    RoomParticipant.room_id == room_id,
                    RoomParticipant.is_active == True
                ).count()
                
                if current_participants >= room.max_participants:
                    raise ValueError("Room is full")
                
                # Create new participant
                participant = RoomParticipant(
                    room_id=room_id,
                    user_id=user_id,
                    role=role.value,
                    permissions=asdict(self._get_default_permissions(role)),
                    status=ParticipantStatus.ONLINE.value,
                    joined_at=datetime.now(timezone.utc),
                    last_active=datetime.now(timezone.utc)
                )
                
                self.db.add(participant)
                
                # Update room stats
                room.total_participants += 1
            
            room.last_activity = datetime.now(timezone.utc)
            self.db.commit()
            
            # Add to Redis room
            await self._add_participant_to_redis(room_id, user_id)
            
            # Notify other participants
            await self._broadcast_to_room(room_id, {
                "type": "participant_joined",
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Log activity
            await self._log_activity(
                room_id=room_id,
                user_id=user_id,
                activity_type=ActivityType.JOIN,
                description=f"Joined collaboration room"
            )
            
            logger.info(f"User {user_id} joined room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join room {room_id}: {e}")
            self.db.rollback()
            return False
    
    async def leave_room(self, room_id: str, user_id: str) -> bool:
        """Leave collaboration room"""



        try:
            participant = self.db.query(RoomParticipant).filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == user_id,
                RoomParticipant.is_active == True
            ).first()
            
            if not participant:
                return False
            
            # Update participant status
            participant.status = ParticipantStatus.OFFLINE.value
            participant.left_at = datetime.now(timezone.utc)
            
            if participant.joined_at:
                duration = (datetime.now(timezone.utc) - participant.joined_at).total_seconds()
                participant.total_time_seconds += int(duration)
            
            self.db.commit()
            
            # Remove from Redis
            await self._remove_participant_from_redis(room_id, user_id)
            
            # Notify other participants
            await self._broadcast_to_room(room_id, {
                "type": "participant_left",
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Log activity
            await self._log_activity(
                room_id=room_id,
                user_id=user_id,
                activity_type=ActivityType.LEAVE,
                description=f"Left collaboration room"
            )
            
            logger.info(f"User {user_id} left room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave room {room_id}: {e}")
            self.db.rollback()
            return False
    
    async def send_message(
        self,
        room_id: str,
        sender_id: str,
        content: str,
        message_type: str = "text",
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None
    ) -> str:
        """Send message in collaboration room"""



        try:
            message_id = f"msg_{uuid.uuid4().hex[:12]}"
            
            # Create message
            message = CollaborationMessage(
                message_id=message_id,
                room_id=room_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                attachments=attachments or [],
                reply_to_message_id=reply_to,
                sent_at=datetime.now(timezone.utc)
            )
            
            self.db.add(message)
            
            # Update participant stats
            participant = self.db.query(RoomParticipant).filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == sender_id
            ).first()
            
            if participant:
                participant.messages_sent += 1
                participant.last_active = datetime.now(timezone.utc)
            
            # Update room stats
            room = self.db.query(CollaborationRoom).filter(
                CollaborationRoom.room_id == room_id
            ).first()
            
            if room:
                room.total_messages += 1
                room.last_activity = datetime.now(timezone.utc)
            
            self.db.commit()
            
            # Broadcast to room participants
            await self._broadcast_to_room(room_id, {
                "type": "message",
                "message_id": message_id,
                "sender_id": sender_id,
                "content": content,
                "message_type": message_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "attachments": attachments,
                "reply_to": reply_to
            })
            
            # Log activity
            await self._log_activity(
                room_id=room_id,
                user_id=sender_id,
                activity_type=ActivityType.MESSAGE,
                description=f"Sent message: {content[:50]}..."
            )
            
            logger.debug(f"Message {message_id} sent in room {room_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.db.rollback()
            raise
    
    async def share_content(
        self,
        room_id: str,
        owner_id: str,
        name: str,
        content_type: str,
        storage_path: str,
        size_bytes: int,
        permissions: Optional[Dict[str, bool]] = None
    ) -> str:
        """Share content in collaboration room"""



        try:
            content_id = f"content_{uuid.uuid4().hex[:12]}"
            
            shared_content = SharedContent(
                content_id=content_id,
                room_id=room_id,
                owner_id=owner_id,
                name=name,
                content_type=content_type,
                storage_path=storage_path,
                size_bytes=size_bytes,
                download_allowed=permissions.get("download_allowed", True) if permissions else True,
                edit_allowed=permissions.get("edit_allowed", False) if permissions else False,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(shared_content)
            
            # Update participant stats
            participant = self.db.query(RoomParticipant).filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.user_id == owner_id
            ).first()
            
            if participant:
                participant.files_shared += 1
                participant.last_active = datetime.now(timezone.utc)
            
            # Update room stats
            room = self.db.query(CollaborationRoom).filter(
                CollaborationRoom.room_id == room_id
            ).first()
            
            if room:
                room.total_files_shared += 1
                room.last_activity = datetime.now(timezone.utc)
            
            self.db.commit()
            
            # Notify participants
            await self._broadcast_to_room(room_id, {
                "type": "content_shared",
                "content_id": content_id,
                "owner_id": owner_id,
                "name": name,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Log activity
            await self._log_activity(
                room_id=room_id,
                user_id=owner_id,
                activity_type=ActivityType.FILE_UPLOAD,
                description=f"Shared content: {name}",
                details={"content_id": content_id, "type": content_type}
            )
            
            logger.info(f"Content {content_id} shared in room {room_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Failed to share content: {e}")
            self.db.rollback()
            raise
    
    async def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """Get room participants with status"""



        try:
            participants = self.db.query(RoomParticipant).filter(
                RoomParticipant.room_id == room_id,
                RoomParticipant.is_active == True
            ).all()
            
            result = []
            for p in participants:
                # Get online status from Redis
                is_online = await self.redis.sismember(f"room:{room_id}:participants", p.user_id)
                
                result.append({
                    "user_id": p.user_id,
                    "creator_type": p.creator_type,
                    "role": p.role,
                    "status": ParticipantStatus.ONLINE.value if is_online else ParticipantStatus.OFFLINE.value,
                    "joined_at": p.joined_at.isoformat(),
                    "last_active": p.last_active.isoformat() if p.last_active else None,
                    "permissions": p.permissions,
                    "stats": {
                        "messages_sent": p.messages_sent,
                        "files_shared": p.files_shared,
                        "total_time_seconds": p.total_time_seconds
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get room participants: {e}")
            return []
    
    async def get_room_messages(
        self,
        room_id: str,
        limit: int = 50,
        offset: int = 0,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get room messages"""



        try:
            query = self.db.query(CollaborationMessage).filter(
                CollaborationMessage.room_id == room_id,
                CollaborationMessage.is_deleted == False
            )
            
            if since:
                query = query.filter(CollaborationMessage.sent_at >= since)
            
            messages = query.order_by(
                CollaborationMessage.sent_at.desc()
            ).offset(offset).limit(limit).all()
            
            return [
                {
                    "message_id": m.message_id,
                    "sender_id": m.sender_id,
                    "content": m.content,
                    "message_type": m.message_type,
                    "sent_at": m.sent_at.isoformat(),
                    "attachments": m.attachments,
                    "reply_to": m.reply_to_message_id,
                    "is_edited": m.is_edited,
                    "edited_at": m.edited_at.isoformat() if m.edited_at else None
                }
                for m in reversed(messages)
            ]
            
        except Exception as e:
            logger.error(f"Failed to get room messages: {e}")
            return []
    
    async def subscribe_to_room(self, room_id: str, callback: Callable):
        """Subscribe to room events"""
        if room_id not in self.room_subscribers:
            self.room_subscribers[room_id] = set()
        
        self.room_subscribers[room_id].add(callback)
        
        # Subscribe to Redis pub/sub
        await self.redis.subscribe(f"room:{room_id}")
        
        logger.info(f"Subscribed to room events: {room_id}")
    
    async def unsubscribe_from_room(self, room_id: str, callback: Callable):
        """Unsubscribe from room events"""
        if room_id in self.room_subscribers:
            self.room_subscribers[room_id].discard(callback)
            
            if not self.room_subscribers[room_id]:
                del self.room_subscribers[room_id]
                await self.redis.unsubscribe(f"room:{room_id}")
    
    # Private methods
    
    async def _load_active_rooms(self):
        """Load active rooms from database"""
        active_rooms = self.db.query(CollaborationRoom).filter(
            CollaborationRoom.status.in_([RoomStatus.ACTIVE.value, RoomStatus.CREATING.value])
        ).all()
        
        for room in active_rooms:
            self.active_rooms[room.room_id] = {
                "status": room.status,
                "settings": room.settings,
                "last_activity": room.last_activity
            }
    
    async def _start_workers(self):
        """Start background worker tasks"""
        self.worker_tasks.extend([
            asyncio.create_task(self._room_activity_monitor()),
            asyncio.create_task(self._session_timeout_monitor()),
            asyncio.create_task(self._metrics_collector())
        ])
    
    async def _initialize_room_redis(self, room_id: str):
        """Initialize Redis structures for room"""
        await self.redis.delete(f"room:{room_id}:participants")
        await self.redis.delete(f"room:{room_id}:messages")
        await self.redis.setex(f"room:{room_id}:created", 86400, datetime.now(timezone.utc).isoformat())
    
    async def _add_participant_to_redis(self, room_id: str, user_id: str):
        """Add participant to Redis room structures"""
        await self.redis.sadd(f"room:{room_id}:participants", user_id)
        await self.redis.setex(f"room:{room_id}:participant:{user_id}", 3600, "online")
    
    async def _remove_participant_from_redis(self, room_id: str, user_id: str):
        """Remove participant from Redis room structures"""
        await self.redis.srem(f"room:{room_id}:participants", user_id)
        await self.redis.delete(f"room:{room_id}:participant:{user_id}")
    
    async def _broadcast_to_room(self, room_id: str, message: Dict[str, Any]):
        """Broadcast message to room participants"""
        # Publish to Redis
        await self.redis.publish(f"room:{room_id}", json.dumps(message))
        
        # Call local subscribers
        if room_id in self.room_subscribers:
            for callback in self.room_subscribers[room_id]:
                try:
                    await callback(message)
                except Exception as e:
                    logger.error(f"Room subscriber callback failed: {e}")
    
    async def _log_activity(
        self,
        room_id: str,
        user_id: str,
        activity_type: ActivityType,
        description: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log collaboration activity"""
        activity = CollaborationActivity(
            room_id=room_id,
            user_id=user_id,
            activity_type=activity_type.value,
            description=description,
            details=details or {},
            timestamp=datetime.now(timezone.utc)
        )
        
        self.db.add(activity)
        self.db.commit()
    
    def _get_default_permissions(self, role: ParticipantRole) -> CollaborationPermissions:
        """Get default permissions for role"""
        if role == ParticipantRole.OWNER:
            return CollaborationPermissions(
                can_edit=True, can_comment=True, can_share=True,
                can_invite=True, can_moderate=True, can_export=True, can_delete=True
            )
        elif role == ParticipantRole.MODERATOR:
            return CollaborationPermissions(
                can_edit=True, can_comment=True, can_share=True,
                can_invite=True, can_moderate=True, can_export=False, can_delete=False
            )
        elif role == ParticipantRole.COLLABORATOR:
            return CollaborationPermissions(
                can_edit=True, can_comment=True, can_share=True,
                can_invite=False, can_moderate=False, can_export=False, can_delete=False
            )
        elif role == ParticipantRole.VIEWER:
            return CollaborationPermissions(
                can_edit=False, can_comment=True, can_share=False,
                can_invite=False, can_moderate=False, can_export=False, can_delete=False
            )
        else:  # GUEST
            return CollaborationPermissions(
                can_edit=False, can_comment=False, can_share=False,
                can_invite=False, can_moderate=False, can_export=False, can_delete=False
            )
    
    async def _close_room(self, room_id: str):
        """Close and cleanup room"""
        # Update room status
        room = self.db.query(CollaborationRoom).filter(
            CollaborationRoom.room_id == room_id
        ).first()
        
        if room:
            room.status = RoomStatus.CLOSED.value
            room.actual_end = datetime.now(timezone.utc)
            self.db.commit()
        
        # Cleanup Redis
        await self.redis.delete(f"room:{room_id}:participants")
        await self.redis.delete(f"room:{room_id}:messages")
        
        # Remove from active rooms
        self.active_rooms.pop(room_id, None)
    
    async def _room_activity_monitor(self):
        """Monitor room activity"""
        while self.running:
            try:
                await asyncio.sleep(60)
                # Monitor room activity and cleanup inactive rooms
                
            except Exception as e:
                logger.error(f"Room activity monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _session_timeout_monitor(self):
        """Monitor session timeouts"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                # Handle session timeouts
                
            except Exception as e:
                logger.error(f"Session timeout monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_collector(self):
        """Collect collaboration metrics"""
        while self.running:
            try:
                await asyncio.sleep(120)
                # Collect and store metrics
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(60)


@asynccontextmanager
async def get_live_collaboration(redis_client: redis.Redis, db_session: Session):
    """Context manager for live collaboration"""
    collaboration = LiveCollaboration(redis_client, db_session)
    try:
        await collaboration.initialize()
        yield collaboration
    finally:
        await collaboration.shutdown()
