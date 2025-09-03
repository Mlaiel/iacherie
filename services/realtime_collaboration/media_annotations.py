"""Collaborative Media Annotation Engine
Real-time collaborative annotation system for multimedia content.

Provides:
- Real-time collaborative annotations on audio, video, and images
- Time-based annotations for media timelines
- Rich annotation types (text, shapes, arrows, highlights)
- Permission-based annotation editing
- Annotation history and versioning
- AI-powered annotation suggestions

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from fastapi import WebSocket
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AnnotationType(Enum):
    """Types of annotations"""
    TEXT = "text"
    HIGHLIGHT = "highlight"
    SHAPE = "shape"
    ARROW = "arrow"
    COMMENT = "comment"
    TIMESTAMP = "timestamp"
    REGION = "region"
    MARKER = "marker"


class MediaType(Enum):
    """Supported media types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


class AnnotationStatus(Enum):
    """Annotation status"""
    ACTIVE = "active"
    DELETED = "deleted"
    ARCHIVED = "archived"
    PENDING = "pending"


class PermissionLevel(Enum):
    """Permission levels for annotations"""
    READ_ONLY = "read_only"
    COMMENT = "comment"
    ANNOTATE = "annotate"
    MODERATE = "moderate"
    ADMIN = "admin"


@dataclass
class AnnotationPosition:
    """Position data for annotations"""
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None
    start_time: Optional[float] = None  # For time-based media
    end_time: Optional[float] = None
    z_index: int = 0


@dataclass
class AnnotationStyle:
    """Visual styling for annotations"""
    color: str = "#ff0000"
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: int = 1
    font_size: int = 14
    font_family: str = "Arial"
    opacity: float = 1.0
    line_style: str = "solid"


@dataclass
class Annotation:
    """Individual annotation object"""
    annotation_id: str
    media_id: str
    annotation_type: AnnotationType
    content: str
    position: AnnotationPosition
    style: AnnotationStyle
    author_id: str
    created_at: datetime
    modified_at: datetime
    status: AnnotationStatus = AnnotationStatus.ACTIVE
    replies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaSession:
    """Collaborative annotation session for media"""
    session_id: str
    media_id: str
    media_type: MediaType
    media_url: str
    title: str
    creator_id: str
    participants: Dict[str, PermissionLevel] = field(default_factory=dict)
    annotations: Dict[str, Annotation] = field(default_factory=dict)
    active_users: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserCursor:
    """Real-time user cursor position"""
    user_id: str
    username: str
    x: float
    y: float
    timestamp: datetime
    current_time: Optional[float] = None  # For time-based media


class CollaborativeAnnotationEngine:
    """
    Real-time collaborative annotation system for multimedia content
    """
    
    def __init__(self):
        self.sessions: Dict[str, MediaSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.user_cursors: Dict[str, Dict[str, UserCursor]] = {}  # session_id -> user_id -> cursor
        self.annotation_handlers: Dict[str, callable] = {}
        
        self._setup_annotation_handlers()
    
    def _setup_annotation_handlers(self):
        """Setup annotation message handlers"""
        self.annotation_handlers = {
            "create_annotation": self._handle_create_annotation,
            "update_annotation": self._handle_update_annotation,
            "delete_annotation": self._handle_delete_annotation,
            "add_reply": self._handle_add_reply,
            "update_cursor": self._handle_update_cursor,
            "join_session": self._handle_join_session,
            "leave_session": self._handle_leave_session,
            "seek_media": self._handle_seek_media,
            "play_pause": self._handle_play_pause,
            "request_suggestions": self._handle_request_suggestions
        }
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle WebSocket connection for annotation collaboration"""
        try:
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"Annotation collaboration connection established for user {user_id}")
            
            # Send connection confirmation
            await self._send_to_user(user_id, {
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_annotation_message(user_id, message)
                    
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
                    await self._send_error(user_id, str(e))
        
        except Exception as e:
            logger.error(f"WebSocket connection error for {user_id}: {e}")
        
        finally:
            await self._cleanup_user_connection(user_id)
    
    async def _handle_annotation_message(self, user_id: str, message: Dict[str, Any]):
        """Route annotation messages to appropriate handlers"""
        message_type = message.get("type")
        handler = self.annotation_handlers.get(message_type)
        
        if handler:
            await handler(user_id, message)
        else:
            await self._send_error(user_id, f"Unknown message type: {message_type}")
    
    async def create_annotation_session(self, media_id: str, media_type: str,
                                      media_url: str, title: str, creator_id: str,
                                      settings: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Create new collaborative annotation session"""
        try:
            session_id = f"annotation_{uuid.uuid4().hex[:12]}"
            
            session = MediaSession(
                session_id=session_id,
                media_id=media_id,
                media_type=MediaType(media_type),
                media_url=media_url,
                title=title,
                creator_id=creator_id,
                settings=settings
            )
            
            # Add creator as admin
            session.participants[creator_id] = PermissionLevel.ADMIN
            
            self.sessions[session_id] = session
            self.user_cursors[session_id] = {}
            
            logger.info(f"Annotation session {session_id} created for media {media_id}")
            
            return {
                "status": "success",
                "session_id": session_id,
                "media_id": media_id,
                "media_type": media_type,
                "message": "Annotation session created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating annotation session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_join_session(self, user_id: str, message: Dict[str, Any]):
        """Join annotation session"""
        try:
            session_id = message.get("session_id")
            session = self.sessions.get(session_id)
            
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Check permissions
            if user_id not in session.participants:
                # Default permission for new users
                session.participants[user_id] = PermissionLevel.COMMENT
            
            session.active_users.add(user_id)
            session.last_activity = datetime.utcnow()
            
            # Send session data to user
            await self._send_to_user(user_id, {
                "type": "session_joined",
                "session": {
                    "session_id": session_id,
                    "media_id": session.media_id,
                    "media_type": session.media_type.value,
                    "media_url": session.media_url,
                    "title": session.title,
                    "permission": session.participants[user_id].value
                },
                "annotations": [
                    self._serialize_annotation(annotation)
                    for annotation in session.annotations.values()
                    if annotation.status == AnnotationStatus.ACTIVE
                ],
                "active_users": list(session.active_users)
            })
            
            # Notify other users
            await self._broadcast_to_session(session_id, {
                "type": "user_joined",
                "user_id": user_id,
                "active_users": list(session.active_users)
            }, exclude_user=user_id)
            
            logger.info(f"User {user_id} joined annotation session {session_id}")
            
        except Exception as e:
            logger.error(f"Error joining annotation session: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_leave_session(self, user_id: str, message: Dict[str, Any]):
        """Leave annotation session"""
        try:
            session_id = message.get("session_id")
            session = self.sessions.get(session_id)
            
            if session and user_id in session.active_users:
                session.active_users.remove(user_id)
                
                # Remove user cursor
                if session_id in self.user_cursors and user_id in self.user_cursors[session_id]:
                    del self.user_cursors[session_id][user_id]
                
                # Notify other users
                await self._broadcast_to_session(session_id, {
                    "type": "user_left",
                    "user_id": user_id,
                    "active_users": list(session.active_users)
                }, exclude_user=user_id)
                
                logger.info(f"User {user_id} left annotation session {session_id}")
            
        except Exception as e:
            logger.error(f"Error leaving annotation session: {e}")
    
    async def _handle_create_annotation(self, user_id: str, message: Dict[str, Any]):
        """Create new annotation"""
        try:
            session_id = message.get("session_id")
            session = self.sessions.get(session_id)
            
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Check permissions
            user_permission = session.participants.get(user_id, PermissionLevel.READ_ONLY)
            if user_permission in [PermissionLevel.READ_ONLY]:
                await self._send_error(user_id, "Insufficient permissions")
                return
            
            # Create annotation
            annotation_id = f"annotation_{uuid.uuid4().hex[:12]}"
            
            position_data = message.get("position", {})
            position = AnnotationPosition(
                x=position_data.get("x", 0),
                y=position_data.get("y", 0),
                width=position_data.get("width"),
                height=position_data.get("height"),
                start_time=position_data.get("start_time"),
                end_time=position_data.get("end_time"),
                z_index=position_data.get("z_index", 0)
            )
            
            style_data = message.get("style", {})
            style = AnnotationStyle(
                color=style_data.get("color", "#ff0000"),
                background_color=style_data.get("background_color"),
                border_color=style_data.get("border_color"),
                border_width=style_data.get("border_width", 1),
                font_size=style_data.get("font_size", 14),
                font_family=style_data.get("font_family", "Arial"),
                opacity=style_data.get("opacity", 1.0),
                line_style=style_data.get("line_style", "solid")
            )
            
            annotation = Annotation(
                annotation_id=annotation_id,
                media_id=session.media_id,
                annotation_type=AnnotationType(message.get("annotation_type")),
                content=message.get("content", ""),
                position=position,
                style=style,
                author_id=user_id,
                created_at=datetime.utcnow(),
                modified_at=datetime.utcnow(),
                tags=message.get("tags", []),
                metadata=message.get("metadata", {})
            )
            
            session.annotations[annotation_id] = annotation
            session.last_activity = datetime.utcnow()
            
            # Broadcast annotation to all users in session
            await self._broadcast_to_session(session_id, {
                "type": "annotation_created",
                "annotation": self._serialize_annotation(annotation)
            })
            
            logger.info(f"Annotation {annotation_id} created in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error creating annotation: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_update_annotation(self, user_id: str, message: Dict[str, Any]):
        """Update existing annotation"""
        try:
            session_id = message.get("session_id")
            annotation_id = message.get("annotation_id")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            annotation = session.annotations.get(annotation_id)
            if not annotation:
                await self._send_error(user_id, "Annotation not found")
                return
            
            # Check permissions
            user_permission = session.participants.get(user_id, PermissionLevel.READ_ONLY)
            if annotation.author_id != user_id and user_permission not in [PermissionLevel.MODERATE, PermissionLevel.ADMIN]:
                await self._send_error(user_id, "Insufficient permissions")
                return
            
            # Update annotation fields
            if "content" in message:
                annotation.content = message["content"]
            
            if "position" in message:
                position_data = message["position"]
                if "x" in position_data:
                    annotation.position.x = position_data["x"]
                if "y" in position_data:
                    annotation.position.y = position_data["y"]
                if "width" in position_data:
                    annotation.position.width = position_data["width"]
                if "height" in position_data:
                    annotation.position.height = position_data["height"]
                if "start_time" in position_data:
                    annotation.position.start_time = position_data["start_time"]
                if "end_time" in position_data:
                    annotation.position.end_time = position_data["end_time"]
            
            if "style" in message:
                style_data = message["style"]
                for key, value in style_data.items():
                    if hasattr(annotation.style, key):
                        setattr(annotation.style, key, value)
            
            if "tags" in message:
                annotation.tags = message["tags"]
            
            annotation.modified_at = datetime.utcnow()
            session.last_activity = datetime.utcnow()
            
            # Broadcast update to all users in session
            await self._broadcast_to_session(session_id, {
                "type": "annotation_updated",
                "annotation": self._serialize_annotation(annotation)
            })
            
            logger.info(f"Annotation {annotation_id} updated in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error updating annotation: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_delete_annotation(self, user_id: str, message: Dict[str, Any]):
        """Delete annotation"""
        try:
            session_id = message.get("session_id")
            annotation_id = message.get("annotation_id")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            annotation = session.annotations.get(annotation_id)
            if not annotation:
                await self._send_error(user_id, "Annotation not found")
                return
            
            # Check permissions
            user_permission = session.participants.get(user_id, PermissionLevel.READ_ONLY)
            if annotation.author_id != user_id and user_permission not in [PermissionLevel.MODERATE, PermissionLevel.ADMIN]:
                await self._send_error(user_id, "Insufficient permissions")
                return
            
            # Mark as deleted
            annotation.status = AnnotationStatus.DELETED
            annotation.modified_at = datetime.utcnow()
            session.last_activity = datetime.utcnow()
            
            # Broadcast deletion to all users in session
            await self._broadcast_to_session(session_id, {
                "type": "annotation_deleted",
                "annotation_id": annotation_id
            })
            
            logger.info(f"Annotation {annotation_id} deleted in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error deleting annotation: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_add_reply(self, user_id: str, message: Dict[str, Any]):
        """Add reply to annotation"""
        try:
            session_id = message.get("session_id")
            annotation_id = message.get("annotation_id")
            reply_content = message.get("content", "")
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            annotation = session.annotations.get(annotation_id)
            if not annotation:
                await self._send_error(user_id, "Annotation not found")
                return
            
            # Check permissions
            user_permission = session.participants.get(user_id, PermissionLevel.READ_ONLY)
            if user_permission == PermissionLevel.READ_ONLY:
                await self._send_error(user_id, "Insufficient permissions")
                return
            
            # Create reply
            reply_id = f"reply_{uuid.uuid4().hex[:12]}"
            reply = {
                "reply_id": reply_id,
                "content": reply_content,
                "author_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            annotation.replies.append(reply_id)
            annotation.modified_at = datetime.utcnow()
            session.last_activity = datetime.utcnow()
            
            # Store reply separately (in real implementation, would use proper storage)
            if not hasattr(annotation, '_replies_data'):
                annotation._replies_data = {}
            annotation._replies_data[reply_id] = reply
            
            # Broadcast reply to all users in session
            await self._broadcast_to_session(session_id, {
                "type": "annotation_reply_added",
                "annotation_id": annotation_id,
                "reply": reply
            })
            
            logger.info(f"Reply {reply_id} added to annotation {annotation_id}")
            
        except Exception as e:
            logger.error(f"Error adding reply: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_update_cursor(self, user_id: str, message: Dict[str, Any]):
        """Update user cursor position"""
        try:
            session_id = message.get("session_id")
            x = message.get("x", 0)
            y = message.get("y", 0)
            current_time = message.get("current_time")
            
            session = self.sessions.get(session_id)
            if not session or user_id not in session.active_users:
                return
            
            # Update cursor position
            if session_id not in self.user_cursors:
                self.user_cursors[session_id] = {}
            
            self.user_cursors[session_id][user_id] = UserCursor(
                user_id=user_id,
                username=message.get("username", f"User_{user_id}"),
                x=x,
                y=y,
                timestamp=datetime.utcnow(),
                current_time=current_time
            )
            
            # Broadcast cursor update to other users
            await self._broadcast_to_session(session_id, {
                "type": "cursor_updated",
                "user_id": user_id,
                "x": x,
                "y": y,
                "current_time": current_time
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error updating cursor: {e}")
    
    async def _handle_seek_media(self, user_id: str, message: Dict[str, Any]):
        """Handle media seek event"""
        try:
            session_id = message.get("session_id")
            time_position = message.get("time", 0)
            
            session = self.sessions.get(session_id)
            if not session or user_id not in session.active_users:
                return
            
            # Broadcast seek event to other users
            await self._broadcast_to_session(session_id, {
                "type": "media_seek",
                "user_id": user_id,
                "time": time_position,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling media seek: {e}")
    
    async def _handle_play_pause(self, user_id: str, message: Dict[str, Any]):
        """Handle play/pause event"""
        try:
            session_id = message.get("session_id")
            is_playing = message.get("playing", False)
            time_position = message.get("time", 0)
            
            session = self.sessions.get(session_id)
            if not session or user_id not in session.active_users:
                return
            
            # Broadcast play/pause event to other users
            await self._broadcast_to_session(session_id, {
                "type": "media_play_pause",
                "user_id": user_id,
                "playing": is_playing,
                "time": time_position,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
        except Exception as e:
            logger.error(f"Error handling play/pause: {e}")
    
    async def _handle_request_suggestions(self, user_id: str, message: Dict[str, Any]):
        """Handle AI annotation suggestions request"""
        try:
            session_id = message.get("session_id")
            media_segment = message.get("segment", {})
            
            session = self.sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Generate AI suggestions (simplified implementation)
            suggestions = await self._generate_annotation_suggestions(session, media_segment)
            
            await self._send_to_user(user_id, {
                "type": "annotation_suggestions",
                "session_id": session_id,
                "suggestions": suggestions
            })
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            await self._send_error(user_id, str(e))
    
    async def _generate_annotation_suggestions(self, session: MediaSession, 
                                             segment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered annotation suggestions"""
        # This is a simplified implementation
        # In production, this would use ML models for content analysis
        
        suggestions = []
        
        if session.media_type == MediaType.AUDIO:
            # Audio-specific suggestions
            suggestions.extend([
                {
                    "type": "timestamp",
                    "content": "Beat marker",
                    "confidence": 0.8,
                    "position": {"start_time": segment.get("start", 0)}
                },
                {
                    "type": "region",
                    "content": "Vocal section",
                    "confidence": 0.7,
                    "position": {
                        "start_time": segment.get("start", 0),
                        "end_time": segment.get("end", 10)
                    }
                }
            ])
        
        elif session.media_type == MediaType.VIDEO:
            # Video-specific suggestions
            suggestions.extend([
                {
                    "type": "comment",
                    "content": "Scene transition",
                    "confidence": 0.9,
                    "position": {"start_time": segment.get("start", 0)}
                },
                {
                    "type": "highlight",
                    "content": "Key moment",
                    "confidence": 0.6,
                    "position": {
                        "x": segment.get("x", 100),
                        "y": segment.get("y", 100),
                        "width": 200,
                        "height": 100
                    }
                }
            ])
        
        return suggestions
    
    def _serialize_annotation(self, annotation: Annotation) -> Dict[str, Any]:
        """Serialize annotation for transmission"""
        return {
            "annotation_id": annotation.annotation_id,
            "media_id": annotation.media_id,
            "annotation_type": annotation.annotation_type.value,
            "content": annotation.content,
            "position": {
                "x": annotation.position.x,
                "y": annotation.position.y,
                "width": annotation.position.width,
                "height": annotation.position.height,
                "start_time": annotation.position.start_time,
                "end_time": annotation.position.end_time,
                "z_index": annotation.position.z_index
            },
            "style": {
                "color": annotation.style.color,
                "background_color": annotation.style.background_color,
                "border_color": annotation.style.border_color,
                "border_width": annotation.style.border_width,
                "font_size": annotation.style.font_size,
                "font_family": annotation.style.font_family,
                "opacity": annotation.style.opacity,
                "line_style": annotation.style.line_style
            },
            "author_id": annotation.author_id,
            "created_at": annotation.created_at.isoformat(),
            "modified_at": annotation.modified_at.isoformat(),
            "status": annotation.status.value,
            "replies": annotation.replies,
            "tags": annotation.tags,
            "metadata": annotation.metadata
        }
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        websocket = self.websocket_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                await self._cleanup_user_connection(user_id)
    
    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any],
                                   exclude_user: Optional[str] = None):
        """Broadcast message to all users in session"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        for user_id in session.active_users:
            if user_id != exclude_user:
                await self._send_to_user(user_id, message)
    
    async def _send_error(self, user_id: str, error_message: str):
        """Send error message to user"""
        await self._send_to_user(user_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _cleanup_user_connection(self, user_id: str):
        """Cleanup user connection and session participation"""
        try:
            # Remove WebSocket connection
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
            
            # Remove from all sessions
            for session_id, session in self.sessions.items():
                if user_id in session.active_users:
                    await self._handle_leave_session(user_id, {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"Error cleaning up user connection: {e}")
    
    async def get_session_annotations(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all annotations for a session"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return [
            self._serialize_annotation(annotation)
            for annotation in session.annotations.values()
            if annotation.status == AnnotationStatus.ACTIVE
        ]
    
    async def export_annotations(self, session_id: str, format_type: str = "json") -> Dict[str, Any]:
        """Export annotations in specified format"""
        session = self.sessions.get(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        annotations = await self.get_session_annotations(session_id)
        
        export_data = {
            "session_id": session_id,
            "media_id": session.media_id,
            "media_type": session.media_type.value,
            "title": session.title,
            "exported_at": datetime.utcnow().isoformat(),
            "annotations": annotations,
            "total_count": len(annotations)
        }
        
        if format_type == "json":
            return {
                "status": "success",
                "format": "json",
                "data": export_data
            }
        
        # Additional formats could be implemented (XML, CSV, etc.)
        return {"status": "error", "message": f"Unsupported format: {format_type}"}


# Export the engine
__all__ = ['CollaborativeAnnotationEngine', 'AnnotationType', 'MediaType',
           'AnnotationStatus', 'PermissionLevel', 'Annotation', 'MediaSession',
           'AnnotationPosition', 'AnnotationStyle', 'UserCursor']