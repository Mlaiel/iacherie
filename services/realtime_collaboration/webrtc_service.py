"""WebRTC Collaboration Service
Professional WebRTC implementation for audio/video collaboration.

Provides:
- P2P and relay WebRTC connections
- Screen sharing capabilities
- Recording and transcription
- Multi-participant sessions
- Quality adaptation
- Connection monitoring

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """WebRTC connection types"""
    PEER_TO_PEER = "peer_to_peer"
    RELAY_SERVER = "relay_server"
    MESH_NETWORK = "mesh_network"
    SFU_SERVER = "sfu_server"


class StreamType(Enum):
    """Media stream types"""
    AUDIO_ONLY = "audio_only"
    VIDEO_ONLY = "video_only"
    AUDIO_VIDEO = "audio_video"
    SCREEN_SHARE = "screen_share"
    DATA_CHANNEL = "data_channel"


class SessionStatus(Enum):
    """Collaboration session status"""
    WAITING = "waiting"
    CONNECTING = "connecting"
    ACTIVE = "active"
    PAUSED = "paused"
    RECORDING = "recording"
    ENDED = "ended"
    ERROR = "error"


@dataclass
class Participant:
    """Participant in collaboration session"""
    user_id: str
    username: str
    role: str
    permissions: List[str]
    joined_at: datetime
    last_activity: datetime
    connection_quality: float = 1.0
    audio_enabled: bool = True
    video_enabled: bool = True
    screen_sharing: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationSession:
    """WebRTC collaboration session"""
    session_id: str
    project_id: str
    title: str
    description: str
    creator_id: str
    max_participants: int
    participants: Dict[str, Participant] = field(default_factory=dict)
    status: SessionStatus = SessionStatus.WAITING
    connection_type: ConnectionType = ConnectionType.SFU_SERVER
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    recording_enabled: bool = False
    transcription_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebRTCOffer:
    """WebRTC offer/answer exchange"""
    session_id: str
    from_user: str
    to_user: str
    offer_type: str  # offer, answer, ice_candidate
    sdp_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class WebRTCCollaborationService:
    """
    Professional WebRTC collaboration service for real-time audio/video
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.signaling_handlers: Dict[str, Callable] = {}
        self.recording_storage = {}
        self.quality_monitor = {}
        
        # Initialize signaling handlers
        self._setup_signaling_handlers()
    
    def _setup_signaling_handlers(self):
        """Setup WebRTC signaling message handlers"""
        self.signaling_handlers = {
            "create_session": self._handle_create_session,
            "join_session": self._handle_join_session,
            "leave_session": self._handle_leave_session,
            "webrtc_offer": self._handle_webrtc_offer,
            "webrtc_answer": self._handle_webrtc_answer,
            "ice_candidate": self._handle_ice_candidate,
            "toggle_audio": self._handle_toggle_audio,
            "toggle_video": self._handle_toggle_video,
            "start_screen_share": self._handle_start_screen_share,
            "stop_screen_share": self._handle_stop_screen_share,
            "start_recording": self._handle_start_recording,
            "stop_recording": self._handle_stop_recording,
            "connection_quality": self._handle_connection_quality
        }
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle new WebSocket connection for WebRTC signaling"""
        try:
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"WebRTC signaling connection established for user {user_id}")
            
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
                    await self._handle_signaling_message(user_id, message)
                    
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await self._send_error(user_id, "Invalid JSON message")
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
                    await self._send_error(user_id, str(e))
        
        except Exception as e:
            logger.error(f"WebSocket connection error for {user_id}: {e}")
        
        finally:
            await self._cleanup_user_connection(user_id)
    
    async def _handle_signaling_message(self, user_id: str, message: Dict[str, Any]):
        """Route signaling messages to appropriate handlers"""
        message_type = message.get("type")
        handler = self.signaling_handlers.get(message_type)
        
        if handler:
            await handler(user_id, message)
        else:
            await self._send_error(user_id, f"Unknown message type: {message_type}")
    
    async def _handle_create_session(self, user_id: str, message: Dict[str, Any]):
        """Create new collaboration session"""
        try:
            session_id = f"session_{uuid.uuid4().hex[:12]}"
            
            session = CollaborationSession(
                session_id=session_id,
                project_id=message.get("project_id", ""),
                title=message.get("title", "Untitled Session"),
                description=message.get("description", ""),
                creator_id=user_id,
                max_participants=message.get("max_participants", 10),
                connection_type=ConnectionType(message.get("connection_type", "sfu_server")),
                recording_enabled=message.get("recording_enabled", False),
                transcription_enabled=message.get("transcription_enabled", False)
            )
            
            # Add creator as first participant
            creator = Participant(
                user_id=user_id,
                username=message.get("username", f"User_{user_id}"),
                role="creator",
                permissions=["admin", "moderate", "record", "invite"],
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            session.participants[user_id] = creator
            self.active_sessions[session_id] = session
            
            # Store in Redis for persistence
            if self.redis:
                await self.redis.setex(
                    f"collaboration_session:{session_id}",
                    3600,  # 1 hour expiry
                    json.dumps({
                        "session_id": session_id,
                        "project_id": session.project_id,
                        "creator_id": user_id,
                        "created_at": session.created_at.isoformat(),
                        "status": session.status.value
                    })
                )
            
            await self._send_to_user(user_id, {
                "type": "session_created",
                "session": {
                    "session_id": session_id,
                    "project_id": session.project_id,
                    "title": session.title,
                    "creator_id": user_id,
                    "max_participants": session.max_participants,
                    "connection_type": session.connection_type.value,
                    "recording_enabled": session.recording_enabled,
                    "created_at": session.created_at.isoformat()
                }
            })
            
            logger.info(f"Collaboration session {session_id} created by {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            await self._send_error(user_id, f"Failed to create session: {e}")
    
    async def _handle_join_session(self, user_id: str, message: Dict[str, Any]):
        """Join existing collaboration session"""
        try:
            session_id = message.get("session_id")
            session = self.active_sessions.get(session_id)
            
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            if len(session.participants) >= session.max_participants:
                await self._send_error(user_id, "Session is full")
                return
            
            # Add participant
            participant = Participant(
                user_id=user_id,
                username=message.get("username", f"User_{user_id}"),
                role="participant",
                permissions=["communicate"],
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            session.participants[user_id] = participant
            
            # Notify participant
            await self._send_to_user(user_id, {
                "type": "session_joined",
                "session": {
                    "session_id": session_id,
                    "title": session.title,
                    "participants": len(session.participants),
                    "status": session.status.value
                },
                "participants": [
                    {
                        "user_id": p.user_id,
                        "username": p.username,
                        "role": p.role,
                        "audio_enabled": p.audio_enabled,
                        "video_enabled": p.video_enabled,
                        "screen_sharing": p.screen_sharing
                    }
                    for p in session.participants.values()
                ]
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "participant_joined",
                "participant": {
                    "user_id": user_id,
                    "username": participant.username,
                    "role": participant.role,
                    "joined_at": participant.joined_at.isoformat()
                }
            }, exclude_user=user_id)
            
            logger.info(f"User {user_id} joined session {session_id}")
            
        except Exception as e:
            logger.error(f"Error joining session: {e}")
            await self._send_error(user_id, f"Failed to join session: {e}")
    
    async def _handle_leave_session(self, user_id: str, message: Dict[str, Any]):
        """Leave collaboration session"""
        try:
            session_id = message.get("session_id")
            session = self.active_sessions.get(session_id)
            
            if not session or user_id not in session.participants:
                await self._send_error(user_id, "Not in session")
                return
            
            # Remove participant
            participant = session.participants.pop(user_id)
            
            # Notify participant
            await self._send_to_user(user_id, {
                "type": "session_left",
                "session_id": session_id
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "participant_left",
                "user_id": user_id,
                "username": participant.username,
                "left_at": datetime.utcnow().isoformat()
            }, exclude_user=user_id)
            
            # End session if creator leaves or no participants left
            if user_id == session.creator_id or len(session.participants) == 0:
                await self._end_session(session_id)
            
            logger.info(f"User {user_id} left session {session_id}")
            
        except Exception as e:
            logger.error(f"Error leaving session: {e}")
            await self._send_error(user_id, f"Failed to leave session: {e}")
    
    async def _handle_webrtc_offer(self, user_id: str, message: Dict[str, Any]):
        """Forward WebRTC offer to target peer"""
        try:
            session_id = message.get("session_id")
            target_user = message.get("target_user")
            sdp_offer = message.get("sdp_offer")
            
            session = self.active_sessions.get(session_id)
            if not session or user_id not in session.participants:
                await self._send_error(user_id, "Not authorized for session")
                return
            
            # Forward offer to target user
            await self._send_to_user(target_user, {
                "type": "webrtc_offer_received",
                "session_id": session_id,
                "from_user": user_id,
                "sdp_offer": sdp_offer,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.debug(f"WebRTC offer forwarded from {user_id} to {target_user}")
            
        except Exception as e:
            logger.error(f"Error handling WebRTC offer: {e}")
            await self._send_error(user_id, f"Failed to send offer: {e}")
    
    async def _handle_webrtc_answer(self, user_id: str, message: Dict[str, Any]):
        """Forward WebRTC answer to target peer"""
        try:
            session_id = message.get("session_id")
            target_user = message.get("target_user")
            sdp_answer = message.get("sdp_answer")
            
            # Forward answer to target user
            await self._send_to_user(target_user, {
                "type": "webrtc_answer_received",
                "session_id": session_id,
                "from_user": user_id,
                "sdp_answer": sdp_answer,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.debug(f"WebRTC answer forwarded from {user_id} to {target_user}")
            
        except Exception as e:
            logger.error(f"Error handling WebRTC answer: {e}")
            await self._send_error(user_id, f"Failed to send answer: {e}")
    
    async def _handle_ice_candidate(self, user_id: str, message: Dict[str, Any]):
        """Forward ICE candidate to target peer"""
        try:
            session_id = message.get("session_id")
            target_user = message.get("target_user")
            ice_candidate = message.get("ice_candidate")
            
            # Forward ICE candidate to target user
            await self._send_to_user(target_user, {
                "type": "ice_candidate_received",
                "session_id": session_id,
                "from_user": user_id,
                "ice_candidate": ice_candidate,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling ICE candidate: {e}")
    
    async def _handle_toggle_audio(self, user_id: str, message: Dict[str, Any]):
        """Toggle audio for participant"""
        try:
            session_id = message.get("session_id")
            enabled = message.get("enabled", True)
            
            session = self.active_sessions.get(session_id)
            if session and user_id in session.participants:
                session.participants[user_id].audio_enabled = enabled
                session.participants[user_id].last_activity = datetime.utcnow()
                
                # Broadcast audio status change
                await self._broadcast_to_session(session_id, {
                    "type": "audio_toggled",
                    "user_id": user_id,
                    "enabled": enabled
                }, exclude_user=user_id)
                
        except Exception as e:
            logger.error(f"Error toggling audio: {e}")
    
    async def _handle_toggle_video(self, user_id: str, message: Dict[str, Any]):
        """Toggle video for participant"""
        try:
            session_id = message.get("session_id")
            enabled = message.get("enabled", True)
            
            session = self.active_sessions.get(session_id)
            if session and user_id in session.participants:
                session.participants[user_id].video_enabled = enabled
                session.participants[user_id].last_activity = datetime.utcnow()
                
                # Broadcast video status change
                await self._broadcast_to_session(session_id, {
                    "type": "video_toggled",
                    "user_id": user_id,
                    "enabled": enabled
                }, exclude_user=user_id)
                
        except Exception as e:
            logger.error(f"Error toggling video: {e}")
    
    async def _handle_start_screen_share(self, user_id: str, message: Dict[str, Any]):
        """Start screen sharing"""
        try:
            session_id = message.get("session_id")
            
            session = self.active_sessions.get(session_id)
            if session and user_id in session.participants:
                session.participants[user_id].screen_sharing = True
                session.participants[user_id].last_activity = datetime.utcnow()
                
                # Broadcast screen share start
                await self._broadcast_to_session(session_id, {
                    "type": "screen_share_started",
                    "user_id": user_id,
                    "username": session.participants[user_id].username
                }, exclude_user=user_id)
                
        except Exception as e:
            logger.error(f"Error starting screen share: {e}")
    
    async def _handle_stop_screen_share(self, user_id: str, message: Dict[str, Any]):
        """Stop screen sharing"""
        try:
            session_id = message.get("session_id")
            
            session = self.active_sessions.get(session_id)
            if session and user_id in session.participants:
                session.participants[user_id].screen_sharing = False
                session.participants[user_id].last_activity = datetime.utcnow()
                
                # Broadcast screen share stop
                await self._broadcast_to_session(session_id, {
                    "type": "screen_share_stopped",
                    "user_id": user_id
                }, exclude_user=user_id)
                
        except Exception as e:
            logger.error(f"Error stopping screen share: {e}")
    
    async def _handle_start_recording(self, user_id: str, message: Dict[str, Any]):
        """Start session recording"""
        try:
            session_id = message.get("session_id")
            
            session = self.active_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            participant = session.participants.get(user_id)
            if not participant or "record" not in participant.permissions:
                await self._send_error(user_id, "No recording permission")
                return
            
            if session.status == SessionStatus.RECORDING:
                await self._send_error(user_id, "Recording already in progress")
                return
            
            # Start recording
            session.status = SessionStatus.RECORDING
            recording_id = f"rec_{session_id}_{int(time.time())}"
            
            # Initialize recording metadata
            self.recording_storage[recording_id] = {
                "session_id": session_id,
                "started_by": user_id,
                "started_at": datetime.utcnow().isoformat(),
                "participants": list(session.participants.keys()),
                "format": message.get("format", "webm"),
                "quality": message.get("quality", "high")
            }
            
            # Broadcast recording start
            await self._broadcast_to_session(session_id, {
                "type": "recording_started",
                "recording_id": recording_id,
                "started_by": user_id,
                "started_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"Recording {recording_id} started for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            await self._send_error(user_id, f"Failed to start recording: {e}")
    
    async def _handle_stop_recording(self, user_id: str, message: Dict[str, Any]):
        """Stop session recording"""
        try:
            session_id = message.get("session_id")
            
            session = self.active_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            if session.status != SessionStatus.RECORDING:
                await self._send_error(user_id, "No recording in progress")
                return
            
            # Stop recording
            session.status = SessionStatus.ACTIVE
            
            # Find recording
            recording_id = None
            for rec_id, rec_data in self.recording_storage.items():
                if rec_data["session_id"] == session_id and "ended_at" not in rec_data:
                    recording_id = rec_id
                    break
            
            if recording_id:
                self.recording_storage[recording_id]["ended_at"] = datetime.utcnow().isoformat()
                self.recording_storage[recording_id]["ended_by"] = user_id
                
                # Broadcast recording stop
                await self._broadcast_to_session(session_id, {
                    "type": "recording_stopped",
                    "recording_id": recording_id,
                    "ended_by": user_id,
                    "ended_at": datetime.utcnow().isoformat()
                })
                
                logger.info(f"Recording {recording_id} stopped for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            await self._send_error(user_id, f"Failed to stop recording: {e}")
    
    async def _handle_connection_quality(self, user_id: str, message: Dict[str, Any]):
        """Update connection quality metrics"""
        try:
            session_id = message.get("session_id")
            quality = message.get("quality", 1.0)
            
            session = self.active_sessions.get(session_id)
            if session and user_id in session.participants:
                session.participants[user_id].connection_quality = quality
                session.participants[user_id].last_activity = datetime.utcnow()
                
                # Store quality metrics
                if session_id not in self.quality_monitor:
                    self.quality_monitor[session_id] = {}
                
                self.quality_monitor[session_id][user_id] = {
                    "quality": quality,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": message.get("metrics", {})
                }
                
        except Exception as e:
            logger.error(f"Error updating connection quality: {e}")
    
    async def _end_session(self, session_id: str):
        """End collaboration session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
            
            session.status = SessionStatus.ENDED
            session.ended_at = datetime.utcnow()
            
            # Notify all participants
            await self._broadcast_to_session(session_id, {
                "type": "session_ended",
                "session_id": session_id,
                "ended_at": session.ended_at.isoformat()
            })
            
            # Cleanup
            del self.active_sessions[session_id]
            
            # Remove from Redis
            if self.redis:
                await self.redis.delete(f"collaboration_session:{session_id}")
            
            logger.info(f"Session {session_id} ended")
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
    
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
        """Broadcast message to all session participants"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        for user_id in session.participants:
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
            for session_id, session in list(self.active_sessions.items()):
                if user_id in session.participants:
                    await self._handle_leave_session(user_id, {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"Error cleaning up user connection: {e}")
    
    async def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active collaboration sessions"""
        return [
            {
                "session_id": session.session_id,
                "project_id": session.project_id,
                "title": session.title,
                "creator_id": session.creator_id,
                "participants": len(session.participants),
                "max_participants": session.max_participants,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "recording_enabled": session.recording_enabled
            }
            for session in self.active_sessions.values()
        ]
    
    async def get_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session information"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "project_id": session.project_id,
            "title": session.title,
            "description": session.description,
            "creator_id": session.creator_id,
            "status": session.status.value,
            "connection_type": session.connection_type.value,
            "participants": [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "role": p.role,
                    "permissions": p.permissions,
                    "joined_at": p.joined_at.isoformat(),
                    "last_activity": p.last_activity.isoformat(),
                    "connection_quality": p.connection_quality,
                    "audio_enabled": p.audio_enabled,
                    "video_enabled": p.video_enabled,
                    "screen_sharing": p.screen_sharing
                }
                for p in session.participants.values()
            ],
            "created_at": session.created_at.isoformat(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "recording_enabled": session.recording_enabled,
            "transcription_enabled": session.transcription_enabled
        }
    
    async def get_recording_info(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Get recording information"""
        return self.recording_storage.get(recording_id)
    
    async def get_session_quality_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get session quality metrics"""
        return self.quality_monitor.get(session_id, {})


# Export the service
__all__ = ['WebRTCCollaborationService', 'ConnectionType', 'StreamType', 
           'SessionStatus', 'Participant', 'CollaborationSession']