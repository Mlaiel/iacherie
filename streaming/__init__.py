"""
Real-time Streaming Infrastructure
=================================

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue - AI-Powered Content Protection and Monetization Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides WebSocket-based real-time streaming for collaboration and live content.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.routing import APIRouter
import websockets

logger = logging.getLogger(__name__)

class StreamType(Enum):
    """Types of real-time streams"""
    COLLABORATION = "collaboration"
    LIVE_CONTENT = "live_content"
    ANALYTICS = "analytics"
    NOTIFICATIONS = "notifications"
    AUDIO_STREAM = "audio_stream"
    VIDEO_STREAM = "video_stream"

class MessageType(Enum):
    """WebSocket message types"""
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    BROADCAST = "broadcast"
    DIRECT_MESSAGE = "direct_message"
    CONTENT_UPDATE = "content_update"
    COLLABORATION_EVENT = "collaboration_event"
    STATUS_UPDATE = "status_update"
    ANALYTICS_EVENT = "analytics_event"

@dataclass
class StreamMessage:
    """Real-time stream message"""
    message_type: str
    stream_type: str
    room_id: str
    user_id: str
    data: Dict[str, Any]
    timestamp: str = None
    message_id: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.message_id:
            self.message_id = str(uuid.uuid4())

class ConnectionManager:
    """Manages WebSocket connections for real-time streaming"""
    
    def __init__(self):
        # Active connections grouped by room and stream type
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
        # User to connection mapping
        self.user_connections: Dict[str, WebSocket] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        logger.info("ConnectionManager initialized")
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, stream_type: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Initialize room if it doesn't exist
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        
        # Initialize stream type if it doesn't exist
        if stream_type not in self.active_connections[room_id]:
            self.active_connections[room_id][stream_type] = set()
        
        # Add connection
        self.active_connections[room_id][stream_type].add(websocket)
        self.user_connections[user_id] = websocket
        
        # Store metadata
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'room_id': room_id,
            'stream_type': stream_type,
            'connected_at': datetime.now().isoformat()
        }
        
        logger.info(f"User {user_id} connected to room {room_id} for {stream_type}")
        
        # Notify room about new connection
        await self.broadcast_to_room(room_id, stream_type, {
            'type': 'user_joined',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }, exclude_user=user_id)
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket not in self.connection_metadata:
            return
        
        metadata = self.connection_metadata[websocket]
        user_id = metadata['user_id']
        room_id = metadata['room_id']
        stream_type = metadata['stream_type']
        
        # Remove from active connections
        if (room_id in self.active_connections and 
            stream_type in self.active_connections[room_id]):
            self.active_connections[room_id][stream_type].discard(websocket)
            
            # Clean up empty structures
            if not self.active_connections[room_id][stream_type]:
                del self.active_connections[room_id][stream_type]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        
        # Remove metadata
        del self.connection_metadata[websocket]
        
        logger.info(f"User {user_id} disconnected from room {room_id}")
        
        # Notify room about disconnection
        if room_id in self.active_connections and stream_type in self.active_connections[room_id]:
            await self.broadcast_to_room(room_id, stream_type, {
                'type': 'user_left',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            })
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            try:
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Sent personal message to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending personal message to {user_id}: {e}")
                await self.disconnect(websocket)
    
    async def broadcast_to_room(self, room_id: str, stream_type: str, message: Dict[str, Any], exclude_user: str = None):
        """Broadcast message to all users in a room/stream"""
        if (room_id not in self.active_connections or 
            stream_type not in self.active_connections[room_id]):
            return
        
        connections = self.active_connections[room_id][stream_type].copy()
        
        for websocket in connections:
            metadata = self.connection_metadata.get(websocket, {})
            user_id = metadata.get('user_id')
            
            # Skip excluded user
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to room {room_id}: {e}")
                await self.disconnect(websocket)
    
    def get_room_users(self, room_id: str, stream_type: str) -> List[str]:
        """Get list of users in a room/stream"""
        if (room_id not in self.active_connections or 
            stream_type not in self.active_connections[room_id]):
            return []
        
        users = []
        for websocket in self.active_connections[room_id][stream_type]:
            metadata = self.connection_metadata.get(websocket, {})
            user_id = metadata.get('user_id')
            if user_id:
                users.append(user_id)
        
        return users
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_connections = sum(
            len(stream_connections)
            for room in self.active_connections.values()
            for stream_connections in room.values()
        )
        
        return {
            'total_connections': total_connections,
            'active_rooms': len(self.active_connections),
            'connected_users': len(self.user_connections),
            'rooms_by_stream': {
                room_id: list(streams.keys())
                for room_id, streams in self.active_connections.items()
            }
        }

class RealTimeStreamingService:
    """Real-time streaming service for live collaboration and content"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.stream_processors = {
            StreamType.COLLABORATION.value: self._process_collaboration_stream,
            StreamType.LIVE_CONTENT.value: self._process_live_content_stream,
            StreamType.ANALYTICS.value: self._process_analytics_stream,
            StreamType.NOTIFICATIONS.value: self._process_notifications_stream,
            StreamType.AUDIO_STREAM.value: self._process_audio_stream,
            StreamType.VIDEO_STREAM.value: self._process_video_stream,
        }
        
        logger.info("RealTimeStreamingService initialized")
    
    async def handle_websocket(self, websocket: WebSocket, room_id: str, user_id: str, stream_type: str):
        """Handle WebSocket connection lifecycle"""
        await self.connection_manager.connect(websocket, room_id, user_id, stream_type)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Create stream message
                stream_message = StreamMessage(
                    message_type=message_data.get('type', MessageType.BROADCAST.value),
                    stream_type=stream_type,
                    room_id=room_id,
                    user_id=user_id,
                    data=message_data.get('data', {})
                )
                
                # Process message based on stream type
                await self._process_stream_message(stream_message)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except Exception as e:
            logger.error(f"Error in WebSocket handler: {e}")
        finally:
            await self.connection_manager.disconnect(websocket)
    
    async def _process_stream_message(self, message: StreamMessage):
        """Process incoming stream message"""
        processor = self.stream_processors.get(message.stream_type)
        if processor:
            await processor(message)
        else:
            logger.warning(f"No processor for stream type: {message.stream_type}")
    
    async def _process_collaboration_stream(self, message: StreamMessage):
        """Process collaboration stream messages"""
        if message.message_type == MessageType.COLLABORATION_EVENT.value:
            # Handle real-time collaboration events
            collaboration_data = {
                'type': 'collaboration_update',
                'event': message.data.get('event'),
                'user_id': message.user_id,
                'timestamp': message.timestamp,
                'data': message.data
            }
            
            await self.connection_manager.broadcast_to_room(
                message.room_id, 
                message.stream_type, 
                collaboration_data,
                exclude_user=message.user_id
            )
            
        elif message.message_type == MessageType.CONTENT_UPDATE.value:
            # Handle content updates in real-time
            content_update = {
                'type': 'content_updated',
                'content_id': message.data.get('content_id'),
                'changes': message.data.get('changes'),
                'user_id': message.user_id,
                'timestamp': message.timestamp
            }
            
            await self.connection_manager.broadcast_to_room(
                message.room_id,
                message.stream_type,
                content_update,
                exclude_user=message.user_id
            )
    
    async def _process_live_content_stream(self, message: StreamMessage):
        """Process live content stream messages"""
        if message.message_type == MessageType.BROADCAST.value:
            # Handle live content broadcasting
            live_data = {
                'type': 'live_content',
                'content_type': message.data.get('content_type'),
                'content_data': message.data.get('content_data'),
                'creator_id': message.user_id,
                'timestamp': message.timestamp
            }
            
            await self.connection_manager.broadcast_to_room(
                message.room_id,
                message.stream_type,
                live_data
            )
    
    async def _process_analytics_stream(self, message: StreamMessage):
        """Process analytics stream messages"""
        # Handle real-time analytics updates
        analytics_data = {
            'type': 'analytics_update',
            'metrics': message.data.get('metrics'),
            'user_id': message.user_id,
            'timestamp': message.timestamp
        }
        
        await self.connection_manager.broadcast_to_room(
            message.room_id,
            message.stream_type,
            analytics_data
        )
    
    async def _process_notifications_stream(self, message: StreamMessage):
        """Process notifications stream messages"""
        # Handle real-time notifications
        notification_data = {
            'type': 'notification',
            'notification_type': message.data.get('notification_type'),
            'title': message.data.get('title'),
            'message': message.data.get('message'),
            'timestamp': message.timestamp
        }
        
        target_user = message.data.get('target_user')
        if target_user:
            await self.connection_manager.send_personal_message(target_user, notification_data)
        else:
            await self.connection_manager.broadcast_to_room(
                message.room_id,
                message.stream_type,
                notification_data
            )
    
    async def _process_audio_stream(self, message: StreamMessage):
        """Process audio stream messages"""
        # Handle real-time audio streaming
        audio_data = {
            'type': 'audio_data',
            'audio_chunk': message.data.get('audio_chunk'),
            'sample_rate': message.data.get('sample_rate', 44100),
            'format': message.data.get('format', 'wav'),
            'creator_id': message.user_id,
            'timestamp': message.timestamp
        }
        
        await self.connection_manager.broadcast_to_room(
            message.room_id,
            message.stream_type,
            audio_data,
            exclude_user=message.user_id
        )
    
    async def _process_video_stream(self, message: StreamMessage):
        """Process video stream messages"""
        # Handle real-time video streaming
        video_data = {
            'type': 'video_data',
            'video_chunk': message.data.get('video_chunk'),
            'resolution': message.data.get('resolution', '1080p'),
            'format': message.data.get('format', 'mp4'),
            'creator_id': message.user_id,
            'timestamp': message.timestamp
        }
        
        await self.connection_manager.broadcast_to_room(
            message.room_id,
            message.stream_type,
            video_data,
            exclude_user=message.user_id
        )

# Global streaming service instance
streaming_service = RealTimeStreamingService()

# FastAPI router for WebSocket endpoints
streaming_router = APIRouter(prefix="/streaming", tags=["streaming"])

@streaming_router.websocket("/collaborate/{room_id}")
async def websocket_collaboration(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await streaming_service.handle_websocket(websocket, room_id, user_id, StreamType.COLLABORATION.value)

@streaming_router.websocket("/live/{room_id}")
async def websocket_live_content(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for live content streaming"""
    await streaming_service.handle_websocket(websocket, room_id, user_id, StreamType.LIVE_CONTENT.value)

@streaming_router.websocket("/analytics/{room_id}")
async def websocket_analytics(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time analytics"""
    await streaming_service.handle_websocket(websocket, room_id, user_id, StreamType.ANALYTICS.value)

@streaming_router.websocket("/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for personal notifications"""
    room_id = f"user_{user_id}_notifications"
    await streaming_service.handle_websocket(websocket, room_id, user_id, StreamType.NOTIFICATIONS.value)

@streaming_router.websocket("/audio/{room_id}")
async def websocket_audio_stream(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time audio streaming"""
    await streaming_service.handle_websocket(websocket, room_id, user_id, StreamType.AUDIO_STREAM.value)

@streaming_router.websocket("/video/{room_id}")
async def websocket_video_stream(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time video streaming"""
    await streaming_service.handle_websocket(websocket, room_id, user_id, StreamType.VIDEO_STREAM.value)

# REST endpoints for streaming management
@streaming_router.get("/stats")
async def get_streaming_stats():
    """Get real-time streaming statistics"""
    return streaming_service.connection_manager.get_connection_stats()

@streaming_router.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str, stream_type: str = StreamType.COLLABORATION.value):
    """Get users currently in a room"""
    users = streaming_service.connection_manager.get_room_users(room_id, stream_type)
    return {
        'room_id': room_id,
        'stream_type': stream_type,
        'users': users,
        'user_count': len(users)
    }

# Export main components
__all__ = [
    'StreamType',
    'MessageType',
    'StreamMessage',
    'ConnectionManager',
    'RealTimeStreamingService',
    'streaming_service',
    'streaming_router'
]