"""Collaboration Tools - Real-time Creative Collaboration System

Advanced real-time collaboration tools for media creation, including live editing,
comments, annotations, version synchronization, and team coordination features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
import uuid
from collections import defaultdict

# External dependencies with graceful fallbacks
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    logging.warning("Websockets not available - using polling for real-time features")

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory state management")

try:
    from socketio import AsyncServer
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False
    logging.warning("Socket.IO not available - using basic WebSocket implementation")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CollaborationEventType(Enum):
    """Types of collaboration events"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CURSOR_MOVE = "cursor_move"
    SELECTION_CHANGE = "selection_change"
    CONTENT_EDIT = "content_edit"
    COMMENT_ADD = "comment_add"
    COMMENT_REPLY = "comment_reply"
    COMMENT_RESOLVE = "comment_resolve"
    ANNOTATION_ADD = "annotation_add"
    ANNOTATION_UPDATE = "annotation_update"
    VERSION_SYNC = "version_sync"
    PERMISSION_CHANGE = "permission_change"
    STATUS_UPDATE = "status_update"


class PermissionLevel(Enum):
    """Permission levels for collaboration"""
    VIEWER = "viewer"
    COMMENTER = "commenter"
    EDITOR = "editor"
    ADMIN = "admin"
    OWNER = "owner"


class AnnotationType(Enum):
    """Types of annotations"""
    TEXT = "text"
    HIGHLIGHT = "highlight"
    SHAPE = "shape"
    AUDIO_MARKER = "audio_marker"
    VIDEO_TIMESTAMP = "video_timestamp"
    IMAGE_REGION = "image_region"
    REVISION_MARK = "revision_mark"


class CollaborationStatus(Enum):
    """Collaboration session status"""
    ACTIVE = "active"
    PAUSED = "paused"
    OFFLINE = "offline"
    IDLE = "idle"
    TYPING = "typing"
    EDITING = "editing"
    REVIEWING = "reviewing"


@dataclass
class UserPresence:
    """User presence information"""
    user_id: str
    username: str
    avatar_url: Optional[str]
    status: CollaborationStatus
    last_activity: datetime
    cursor_position: Optional[Dict[str, Any]] = None
    current_selection: Optional[Dict[str, Any]] = None
    active_tool: Optional[str] = None
    permission_level: PermissionLevel = PermissionLevel.VIEWER
    color: str = "#4A90E2"  # Default collaboration color


@dataclass
class Comment:
    """Collaboration comment"""
    id: str
    author_id: str
    author_name: str
    content: str
    timestamp: datetime
    
    # Position and context
    position: Dict[str, Any]  # Depends on media type
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Thread management
    parent_id: Optional[str] = None
    replies: List[str] = field(default_factory=list)
    
    # Status
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Metadata
    mentions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Annotation:
    """Media annotation"""
    id: str
    type: AnnotationType
    author_id: str
    author_name: str
    created_at: datetime
    
    # Content
    content: str
    data: Dict[str, Any]  # Type-specific annotation data
    
    # Position and styling
    position: Dict[str, Any]
    style: Dict[str, str] = field(default_factory=dict)
    
    # Collaboration
    visible_to: List[str] = field(default_factory=list)  # Empty = visible to all
    linked_comments: List[str] = field(default_factory=list)
    
    # Status
    active: bool = True
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CollaborationEvent:
    """Real-time collaboration event"""
    id: str
    type: CollaborationEventType
    user_id: str
    session_id: str
    timestamp: datetime
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Targeting
    target_users: Optional[List[str]] = None  # None = broadcast to all
    exclude_users: List[str] = field(default_factory=list)
    
    # Metadata
    priority: int = 0  # Higher numbers = higher priority
    persistent: bool = False  # Whether to store for offline users


@dataclass
class OperationalTransform:
    """Operational Transform for concurrent editing"""
    id: str
    operation_type: str
    position: int
    length: int
    content: Optional[str] = None
    author_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    applied: bool = False
    
    # Transform metadata
    original_position: int = 0
    transformed_position: int = 0
    conflicts: List[str] = field(default_factory=list)


@dataclass
class CollaborationSession:
    """Active collaboration session"""
    id: str
    content_id: str
    content_type: str
    name: str
    created_by: str
    created_at: datetime
    
    # Participants
    active_users: Dict[str, UserPresence] = field(default_factory=dict)
    permissions: Dict[str, PermissionLevel] = field(default_factory=dict)
    
    # Collaboration data
    comments: Dict[str, Comment] = field(default_factory=dict)
    annotations: Dict[str, Annotation] = field(default_factory=dict)
    
    # Real-time state
    current_version: str = "1.0"
    pending_operations: List[OperationalTransform] = field(default_factory=list)
    sync_state: Dict[str, Any] = field(default_factory=dict)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    active: bool = True
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CollaborationEngine:
    """Real-time collaboration engine"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize collaboration engine
        
        Args:
            redis_url: Optional Redis connection URL
        """
        self.sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
        self.event_handlers: Dict[CollaborationEventType, List[Callable]] = defaultdict(list)
        self.websocket_connections: Dict[str, Any] = {}
        
        # Redis for distributed state
        self.redis_client = None
        if HAS_REDIS and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info("Connected to Redis for collaboration state")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
        
        # Socket.IO server if available
        self.socketio = None
        if HAS_SOCKETIO:
            self.socketio = AsyncServer(cors_allowed_origins="*")
            self._setup_socketio_handlers()
        
        logger.info("CollaborationEngine initialized successfully")
    
    def _setup_socketio_handlers(self):
        """Setup Socket.IO event handlers"""
        if not self.socketio:
            return
        
        @self.socketio.event
        async def connect(sid, environ):
            logger.info(f"User connected: {sid}")
        
        @self.socketio.event
        async def disconnect(sid):
            logger.info(f"User disconnected: {sid}")
            await self._handle_user_disconnect(sid)
        
        @self.socketio.event
        async def join_session(sid, data):
            await self._handle_join_session(sid, data)
        
        @self.socketio.event
        async def leave_session(sid, data):
            await self._handle_leave_session(sid, data)
        
        @self.socketio.event
        async def collaboration_event(sid, data):
            await self._handle_collaboration_event(sid, data)
    
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new collaboration session
        
        Args:
            session_data: Session configuration
            
        Returns:
            Session ID
        """
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            session = CollaborationSession(
                id=session_id,
                content_id=session_data["content_id"],
                content_type=session_data["content_type"],
                name=session_data.get("name", f"Collaboration on {session_data['content_id']}"),
                created_by=session_data["created_by"],
                created_at=now
            )
            
            # Set initial permissions
            session.permissions[session_data["created_by"]] = PermissionLevel.OWNER
            
            # Add initial settings
            session.settings = {
                "auto_save": session_data.get("auto_save", True),
                "real_time_sync": session_data.get("real_time_sync", True),
                "comment_notifications": session_data.get("comment_notifications", True),
                "cursor_sharing": session_data.get("cursor_sharing", True),
                "max_participants": session_data.get("max_participants", 50)
            }
            
            self.sessions[session_id] = session
            
            # Store in Redis if available
            if self.redis_client:
                await self._save_session_to_redis(session)
            
            logger.info(f"Created collaboration session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating collaboration session: {e}")
            raise
    
    async def join_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Join a collaboration session
        
        Args:
            session_id: Session identifier
            user_data: User information
            
        Returns:
            Success status
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            user_id = user_data["user_id"]
            
            # Check if user has permission to join
            if not self._check_join_permission(session, user_id):
                logger.warning(f"User {user_id} lacks permission to join session {session_id}")
                return False
            
            # Check participant limit
            if len(session.active_users) >= session.settings.get("max_participants", 50):
                logger.warning(f"Session {session_id} is at participant limit")
                return False
            
            # Create user presence
            presence = UserPresence(
                user_id=user_id,
                username=user_data.get("username", user_id),
                avatar_url=user_data.get("avatar_url"),
                status=CollaborationStatus.ACTIVE,
                last_activity=datetime.now(timezone.utc),
                permission_level=session.permissions.get(user_id, PermissionLevel.VIEWER),
                color=user_data.get("color", self._generate_user_color(user_id))
            )
            
            # Add to session
            session.active_users[user_id] = presence
            self.user_sessions[user_id].add(session_id)
            session.last_activity = datetime.now(timezone.utc)
            
            # Broadcast join event
            await self._broadcast_event(session, CollaborationEventType.USER_JOINED, {
                "user_id": user_id,
                "username": presence.username,
                "avatar_url": presence.avatar_url,
                "permission_level": presence.permission_level.value,
                "color": presence.color
            }, exclude_users=[user_id])
            
            # Send current state to new user
            await self._send_current_state(session_id, user_id)
            
            logger.info(f"User {user_id} joined session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining session: {e}")
            return False
    
    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Leave a collaboration session
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Success status
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            if user_id not in session.active_users:
                return False
            
            # Remove user from session
            presence = session.active_users.pop(user_id)
            self.user_sessions[user_id].discard(session_id)
            session.last_activity = datetime.now(timezone.utc)
            
            # Broadcast leave event
            await self._broadcast_event(session, CollaborationEventType.USER_LEFT, {
                "user_id": user_id,
                "username": presence.username
            })
            
            # Clean up user's pending operations
            session.pending_operations = [
                op for op in session.pending_operations if op.author_id != user_id
            ]
            
            logger.info(f"User {user_id} left session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving session: {e}")
            return False
    
    async def add_comment(self, session_id: str, comment_data: Dict[str, Any]) -> Optional[str]:
        """Add a comment to the collaboration
        
        Args:
            session_id: Session identifier
            comment_data: Comment information
            
        Returns:
            Comment ID or None
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return None
            
            user_id = comment_data["author_id"]
            
            # Check permissions
            if not self._check_comment_permission(session, user_id):
                return None
            
            comment_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            comment = Comment(
                id=comment_id,
                author_id=user_id,
                author_name=comment_data.get("author_name", user_id),
                content=comment_data["content"],
                timestamp=now,
                position=comment_data["position"],
                context=comment_data.get("context", {}),
                parent_id=comment_data.get("parent_id"),
                mentions=comment_data.get("mentions", []),
                tags=comment_data.get("tags", [])
            )
            
            # Add to session
            session.comments[comment_id] = comment
            session.last_activity = now
            
            # Handle replies
            if comment.parent_id and comment.parent_id in session.comments:
                session.comments[comment.parent_id].replies.append(comment_id)
            
            # Broadcast comment event
            await self._broadcast_event(session, CollaborationEventType.COMMENT_ADD, {
                "comment_id": comment_id,
                "author_id": comment.author_id,
                "author_name": comment.author_name,
                "content": comment.content,
                "position": comment.position,
                "parent_id": comment.parent_id,
                "mentions": comment.mentions
            })
            
            # Send notifications for mentions
            await self._send_mention_notifications(session, comment)
            
            logger.info(f"Added comment {comment_id} to session {session_id}")
            return comment_id
            
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return None
    
    async def add_annotation(self, session_id: str, annotation_data: Dict[str, Any]) -> Optional[str]:
        """Add an annotation to the collaboration
        
        Args:
            session_id: Session identifier
            annotation_data: Annotation information
            
        Returns:
            Annotation ID or None
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return None
            
            user_id = annotation_data["author_id"]
            
            # Check permissions
            if not self._check_edit_permission(session, user_id):
                return None
            
            annotation_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            annotation = Annotation(
                id=annotation_id,
                type=AnnotationType(annotation_data["type"]),
                author_id=user_id,
                author_name=annotation_data.get("author_name", user_id),
                created_at=now,
                content=annotation_data["content"],
                data=annotation_data["data"],
                position=annotation_data["position"],
                style=annotation_data.get("style", {}),
                visible_to=annotation_data.get("visible_to", [])
            )
            
            # Add to session
            session.annotations[annotation_id] = annotation
            session.last_activity = now
            
            # Broadcast annotation event
            await self._broadcast_event(session, CollaborationEventType.ANNOTATION_ADD, {
                "annotation_id": annotation_id,
                "type": annotation.type.value,
                "author_id": annotation.author_id,
                "author_name": annotation.author_name,
                "content": annotation.content,
                "position": annotation.position,
                "style": annotation.style,
                "visible_to": annotation.visible_to
            })
            
            logger.info(f"Added annotation {annotation_id} to session {session_id}")
            return annotation_id
            
        except Exception as e:
            logger.error(f"Error adding annotation: {e}")
            return None
    
    async def update_cursor_position(self, session_id: str, user_id: str, 
                                   position: Dict[str, Any]) -> bool:
        """Update user's cursor position
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            position: Cursor position data
            
        Returns:
            Success status
        """
        try:
            session = await self._get_session(session_id)
            if not session or user_id not in session.active_users:
                return False
            
            # Update user presence
            presence = session.active_users[user_id]
            presence.cursor_position = position
            presence.last_activity = datetime.now(timezone.utc)
            
            # Broadcast cursor movement if enabled
            if session.settings.get("cursor_sharing", True):
                await self._broadcast_event(session, CollaborationEventType.CURSOR_MOVE, {
                    "user_id": user_id,
                    "position": position,
                    "color": presence.color
                }, exclude_users=[user_id])
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating cursor position: {e}")
            return False
    
    async def apply_operation(self, session_id: str, operation: Dict[str, Any]) -> bool:
        """Apply operational transform operation
        
        Args:
            session_id: Session identifier
            operation: Operation to apply
            
        Returns:
            Success status
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            user_id = operation["author_id"]
            
            # Check edit permissions
            if not self._check_edit_permission(session, user_id):
                return False
            
            # Create operational transform
            ot = OperationalTransform(
                id=str(uuid.uuid4()),
                operation_type=operation["type"],
                position=operation["position"],
                length=operation.get("length", 0),
                content=operation.get("content"),
                author_id=user_id,
                original_position=operation["position"]
            )
            
            # Transform against pending operations
            await self._transform_operation(session, ot)
            
            # Add to pending operations
            session.pending_operations.append(ot)
            session.last_activity = datetime.now(timezone.utc)
            
            # Broadcast operation
            await self._broadcast_event(session, CollaborationEventType.CONTENT_EDIT, {
                "operation_id": ot.id,
                "type": ot.operation_type,
                "position": ot.transformed_position,
                "length": ot.length,
                "content": ot.content,
                "author_id": ot.author_id
            }, exclude_users=[user_id])
            
            # Apply operation locally
            ot.applied = True
            
            logger.info(f"Applied operation {ot.id} in session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying operation: {e}")
            return False
    
    async def sync_version(self, session_id: str, version: str, user_id: str) -> bool:
        """Synchronize version across session
        
        Args:
            session_id: Session identifier
            version: Version identifier
            user_id: User requesting sync
            
        Returns:
            Success status
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            # Check permissions
            if not self._check_edit_permission(session, user_id):
                return False
            
            # Update session version
            old_version = session.current_version
            session.current_version = version
            session.last_activity = datetime.now(timezone.utc)
            
            # Clear pending operations for new version
            session.pending_operations.clear()
            
            # Broadcast version sync
            await self._broadcast_event(session, CollaborationEventType.VERSION_SYNC, {
                "old_version": old_version,
                "new_version": version,
                "synced_by": user_id
            })
            
            logger.info(f"Synced session {session_id} to version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing version: {e}")
            return False
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get complete session state
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session state
        """
        try:
            session = await self._get_session(session_id)
            if not session:
                return {}
            
            return {
                "session": {
                    "id": session.id,
                    "content_id": session.content_id,
                    "content_type": session.content_type,
                    "name": session.name,
                    "created_by": session.created_by,
                    "created_at": session.created_at.isoformat(),
                    "current_version": session.current_version,
                    "settings": session.settings,
                    "last_activity": session.last_activity.isoformat()
                },
                "participants": {
                    user_id: {
                        "username": presence.username,
                        "avatar_url": presence.avatar_url,
                        "status": presence.status.value,
                        "permission_level": presence.permission_level.value,
                        "color": presence.color,
                        "last_activity": presence.last_activity.isoformat(),
                        "cursor_position": presence.cursor_position,
                        "current_selection": presence.current_selection
                    }
                    for user_id, presence in session.active_users.items()
                },
                "comments": {
                    comment_id: {
                        "id": comment.id,
                        "author_id": comment.author_id,
                        "author_name": comment.author_name,
                        "content": comment.content,
                        "timestamp": comment.timestamp.isoformat(),
                        "position": comment.position,
                        "parent_id": comment.parent_id,
                        "replies": comment.replies,
                        "resolved": comment.resolved,
                        "mentions": comment.mentions,
                        "tags": comment.tags
                    }
                    for comment_id, comment in session.comments.items()
                },
                "annotations": {
                    annotation_id: {
                        "id": annotation.id,
                        "type": annotation.type.value,
                        "author_id": annotation.author_id,
                        "author_name": annotation.author_name,
                        "content": annotation.content,
                        "position": annotation.position,
                        "style": annotation.style,
                        "created_at": annotation.created_at.isoformat(),
                        "visible_to": annotation.visible_to,
                        "active": annotation.active
                    }
                    for annotation_id, annotation in session.annotations.items()
                    if annotation.active
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return {}
    
    async def _get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get session by ID"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try loading from Redis
        if self.redis_client:
            session = await self._load_session_from_redis(session_id)
            if session:
                self.sessions[session_id] = session
                return session
        
        return None
    
    async def _broadcast_event(self, session: CollaborationSession, event_type: CollaborationEventType,
                             data: Dict[str, Any], target_users: Optional[List[str]] = None,
                             exclude_users: List[str] = None):
        """Broadcast event to session participants"""
        event = CollaborationEvent(
            id=str(uuid.uuid4()),
            type=event_type,
            user_id="system",
            session_id=session.id,
            timestamp=datetime.now(timezone.utc),
            data=data,
            target_users=target_users,
            exclude_users=exclude_users or []
        )
        
        # Determine recipients
        if target_users:
            recipients = [uid for uid in target_users if uid in session.active_users]
        else:
            recipients = list(session.active_users.keys())
        
        # Exclude specified users
        recipients = [uid for uid in recipients if uid not in event.exclude_users]
        
        # Send via Socket.IO if available
        if self.socketio:
            for user_id in recipients:
                try:
                    await self.socketio.emit('collaboration_event', {
                        'type': event_type.value,
                        'data': data,
                        'session_id': session.id,
                        'timestamp': event.timestamp.isoformat()
                    }, room=user_id)
                except Exception as e:
                    logger.warning(f"Failed to send event to {user_id}: {e}")
        
        # Call event handlers
        for handler in self.event_handlers[event_type]:
            try:
                await handler(event)
            except Exception as e:
                logger.warning(f"Event handler failed: {e}")
    
    async def _send_current_state(self, session_id: str, user_id: str):
        """Send current session state to user"""
        state = await self.get_session_state(session_id)
        
        if self.socketio:
            try:
                await self.socketio.emit('session_state', state, room=user_id)
            except Exception as e:
                logger.warning(f"Failed to send state to {user_id}: {e}")
    
    async def _transform_operation(self, session: CollaborationSession, operation: OperationalTransform):
        """Apply operational transform to operation"""
        # Simplified OT implementation
        for pending_op in session.pending_operations:
            if not pending_op.applied:
                continue
            
            # Transform position based on pending operations
            if pending_op.position <= operation.position:
                if pending_op.operation_type == "insert":
                    operation.transformed_position = operation.position + pending_op.length
                elif pending_op.operation_type == "delete":
                    operation.transformed_position = max(0, operation.position - pending_op.length)
            else:
                operation.transformed_position = operation.position
    
    async def _send_mention_notifications(self, session: CollaborationSession, comment: Comment):
        """Send notifications for comment mentions"""
        for mentioned_user in comment.mentions:
            if mentioned_user in session.active_users:
                await self._broadcast_event(session, CollaborationEventType.COMMENT_ADD, {
                    "comment_id": comment.id,
                    "mention": True,
                    "author_name": comment.author_name,
                    "content": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content
                }, target_users=[mentioned_user])
    
    def _check_join_permission(self, session: CollaborationSession, user_id: str) -> bool:
        """Check if user can join session"""
        # Allow if user has explicit permission or session is public
        return user_id in session.permissions or not session.permissions
    
    def _check_comment_permission(self, session: CollaborationSession, user_id: str) -> bool:
        """Check if user can add comments"""
        if user_id not in session.active_users:
            return False
        
        permission = session.active_users[user_id].permission_level
        return permission in [PermissionLevel.COMMENTER, PermissionLevel.EDITOR, PermissionLevel.ADMIN, PermissionLevel.OWNER]
    
    def _check_edit_permission(self, session: CollaborationSession, user_id: str) -> bool:
        """Check if user can edit content"""
        if user_id not in session.active_users:
            return False
        
        permission = session.active_users[user_id].permission_level
        return permission in [PermissionLevel.EDITOR, PermissionLevel.ADMIN, PermissionLevel.OWNER]
    
    def _generate_user_color(self, user_id: str) -> str:
        """Generate consistent color for user"""
        colors = [
            "#4A90E2", "#7ED321", "#F5A623", "#D0021B", "#9013FE",
            "#50E3C2", "#B8E986", "#FF6B6B", "#4ECDC4", "#45B7D1"
        ]
        return colors[hash(user_id) % len(colors)]
    
    async def _save_session_to_redis(self, session: CollaborationSession):
        """Save session to Redis"""
        if not self.redis_client:
            return
        
        try:
            session_data = {
                "id": session.id,
                "content_id": session.content_id,
                "content_type": session.content_type,
                "name": session.name,
                "created_by": session.created_by,
                "created_at": session.created_at.isoformat(),
                "current_version": session.current_version,
                "settings": session.settings,
                "active": session.active
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.set, 
                f"session:{session.id}", json.dumps(session_data)
            )
        except Exception as e:
            logger.warning(f"Failed to save session to Redis: {e}")
    
    async def _load_session_from_redis(self, session_id: str) -> Optional[CollaborationSession]:
        """Load session from Redis"""
        if not self.redis_client:
            return None
        
        try:
            data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, f"session:{session_id}"
            )
            
            if data:
                session_data = json.loads(data)
                # Note: This is simplified - full implementation would restore complete state
                session = CollaborationSession(
                    id=session_data["id"],
                    content_id=session_data["content_id"],
                    content_type=session_data["content_type"],
                    name=session_data["name"],
                    created_by=session_data["created_by"],
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    current_version=session_data["current_version"],
                    settings=session_data["settings"],
                    active=session_data["active"]
                )
                return session
        except Exception as e:
            logger.warning(f"Failed to load session from Redis: {e}")
        
        return None
    
    async def _handle_user_disconnect(self, connection_id: str):
        """Handle user disconnection"""
        # Find user sessions and remove them
        for user_id, session_ids in self.user_sessions.items():
            for session_id in list(session_ids):
                await self.leave_session(session_id, user_id)
    
    async def _handle_join_session(self, connection_id: str, data: Dict[str, Any]):
        """Handle join session request"""
        await self.join_session(data["session_id"], data["user_data"])
    
    async def _handle_leave_session(self, connection_id: str, data: Dict[str, Any]):
        """Handle leave session request"""
        await self.leave_session(data["session_id"], data["user_id"])
    
    async def _handle_collaboration_event(self, connection_id: str, data: Dict[str, Any]):
        """Handle collaboration event from client"""
        event_type = data.get("type")
        session_id = data.get("session_id")
        
        if not event_type or not session_id:
            return
        
        try:
            event_type_enum = CollaborationEventType(event_type)
            
            if event_type_enum == CollaborationEventType.CURSOR_MOVE:
                await self.update_cursor_position(session_id, data["user_id"], data["position"])
            elif event_type_enum == CollaborationEventType.CONTENT_EDIT:
                await self.apply_operation(session_id, data["operation"])
            elif event_type_enum == CollaborationEventType.COMMENT_ADD:
                await self.add_comment(session_id, data["comment"])
            elif event_type_enum == CollaborationEventType.ANNOTATION_ADD:
                await self.add_annotation(session_id, data["annotation"])
            
        except ValueError:
            logger.warning(f"Unknown event type: {event_type}")
    
    def add_event_handler(self, event_type: CollaborationEventType, handler: Callable):
        """Add event handler for collaboration events"""
        self.event_handlers[event_type].append(handler)


# Convenience functions for easy usage
async def start_collaboration_session(content_id: str, content_type: str, created_by: str,
                                    name: Optional[str] = None) -> str:
    """Start a new collaboration session
    
    Args:
        content_id: Content identifier
        content_type: Type of content
        created_by: User creating session
        name: Optional session name
        
    Returns:
        Session ID
    """
    engine = CollaborationEngine()
    
    session_data = {
        "content_id": content_id,
        "content_type": content_type,
        "created_by": created_by,
        "name": name or f"Collaboration on {content_id}"
    }
    
    return await engine.create_session(session_data)


async def join_collaboration(session_id: str, user_id: str, username: str,
                           avatar_url: Optional[str] = None) -> bool:
    """Join a collaboration session
    
    Args:
        session_id: Session identifier
        user_id: User identifier
        username: User display name
        avatar_url: Optional avatar URL
        
    Returns:
        Success status
    """
    engine = CollaborationEngine()
    
    user_data = {
        "user_id": user_id,
        "username": username,
        "avatar_url": avatar_url
    }
    
    return await engine.join_session(session_id, user_data)


async def add_collaboration_comment(session_id: str, author_id: str, content: str,
                                  position: Dict[str, Any], author_name: Optional[str] = None) -> Optional[str]:
    """Add a comment to collaboration
    
    Args:
        session_id: Session identifier
        author_id: Comment author
        content: Comment content
        position: Position information
        author_name: Optional author display name
        
    Returns:
        Comment ID or None
    """
    engine = CollaborationEngine()
    
    comment_data = {
        "author_id": author_id,
        "author_name": author_name or author_id,
        "content": content,
        "position": position
    }
    
    return await engine.add_comment(session_id, comment_data)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create collaboration engine
        engine = CollaborationEngine()
        
        # Create session
        session_data = {
            "content_id": "video_123",
            "content_type": "video",
            "created_by": "creator_1",
            "name": "Marketing Video Collaboration"
        }
        
        session_id = await engine.create_session(session_data)
        print(f"Created collaboration session: {session_id}")
        
        # Join session
        user_data = {
            "user_id": "editor_1",
            "username": "Jane Editor",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        
        joined = await engine.join_session(session_id, user_data)
        print(f"Joined session: {joined}")
        
        # Add comment
        comment_data = {
            "author_id": "editor_1",
            "author_name": "Jane Editor",
            "content": "This transition needs work",
            "position": {"timestamp": 45.5, "track": "video"}
        }
        
        comment_id = await engine.add_comment(session_id, comment_data)
        print(f"Added comment: {comment_id}")
        
        # Get session state
        state = await engine.get_session_state(session_id)
        print(f"Session state: {json.dumps(state, indent=2, default=str)}")
    
    asyncio.run(main())