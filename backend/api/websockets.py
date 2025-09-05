"""WebSockets - WebSocket Handlers and Events
Consolidated WebSocket functionality for real-time communication.

This module consolidates WebSocket functionality from:
- Real-time content protection alerts
- Live collaboration events
- Analytics dashboard updates
- Content upload progress tracking
- System notifications and status updates
- Chat and messaging features

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Set, Callable, Union
from datetime import datetime
from enum import Enum
from collections import defaultdict
import json
import asyncio
import uuid
from dataclasses import dataclass, asdict

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import redis.asyncio as redis

# ========================================
# WEBSOCKET ENUMS
# ========================================

class EventType(str, Enum):
    """WebSocket event types"""
    # Connection events
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    
    # Content events
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_PROTECTED = "content.protected"
    CONTENT_VIOLATION = "content.violation"
    
    # Collaboration events
    COLLABORATION_REQUEST = "collaboration.request"
    COLLABORATION_ACCEPTED = "collaboration.accepted"
    COLLABORATION_DECLINED = "collaboration.declined"
    COLLABORATION_MESSAGE = "collaboration.message"
    
    # Analytics events
    ANALYTICS_UPDATE = "analytics.update"
    PERFORMANCE_ALERT = "performance.alert"
    
    # System events
    SYSTEM_NOTIFICATION = "system.notification"
    SYSTEM_MAINTENANCE = "system.maintenance"
    
    # Real-time updates
    LIVE_VIEW_COUNT = "live.view_count"
    LIVE_ENGAGEMENT = "live.engagement"
    LIVE_REVENUE = "live.revenue"

class ConnectionStatus(str, Enum):
    """WebSocket connection status"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"

# ========================================
# WEBSOCKET MODELS
# ========================================

class WebSocketMessage(BaseModel):
    """Standard WebSocket message format"""
    event_type: EventType = Field(..., description="Type of event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    sender_id: Optional[str] = Field(None, description="Sender user ID")
    target_id: Optional[str] = Field(None, description="Target user ID or channel")

class ConnectionInfo(BaseModel):
    """WebSocket connection information"""
    connection_id: str = Field(..., description="Unique connection ID")
    user_id: str = Field(..., description="Connected user ID")
    channels: Set[str] = Field(default_factory=set, description="Subscribed channels")
    connected_at: datetime = Field(default_factory=datetime.utcnow, description="Connection timestamp")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: str = Field(..., description="Client user agent")

# ========================================
# WEBSOCKET CONNECTION MANAGER
# ========================================

class WebSocketManager:
    """Manages WebSocket connections and message routing"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.channel_subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids
        self.redis = redis_client
        self.heartbeat_interval = 30  # seconds
        
    async def connect(self, websocket: WebSocket, user_id: str, client_info: Dict[str, Any]) -> str:
        """Accept WebSocket connection and register client"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        
        # Store connection
        self.active_connections[connection_id] = websocket
        
        # Store connection info
        self.connection_info[connection_id] = ConnectionInfo(
            connection_id=connection_id,
            user_id=user_id,
            ip_address=client_info.get("ip_address", "unknown"),
            user_agent=client_info.get("user_agent", "unknown")
        )
        
        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Send welcome message
        await self.send_to_connection(connection_id, WebSocketMessage(
            event_type=EventType.CONNECT,
            data={
                "connection_id": connection_id,
                "user_id": user_id,
                "status": "connected",
                "server_time": datetime.utcnow().isoformat()
            }
        ))
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect WebSocket client"""
        if connection_id not in self.active_connections:
            return
        
        connection_info = self.connection_info.get(connection_id)
        
        # Remove from channels
        if connection_info:
            for channel in connection_info.channels:
                if channel in self.channel_subscriptions:
                    self.channel_subscriptions[channel].discard(connection_id)
            
            # Remove from user connections
            user_id = connection_info.user_id
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
        
        # Clean up
        del self.active_connections[connection_id]
        if connection_id in self.connection_info:
            del self.connection_info[connection_id]
    
    async def send_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(message.json())
                
                # Update last activity
                if connection_id in self.connection_info:
                    self.connection_info[connection_id].last_activity = datetime.utcnow()
                    
            except WebSocketDisconnect:
                await self.disconnect(connection_id)
            except Exception as e:
                print(f"Error sending message to {connection_id}: {e}")
                await self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a user"""
        if user_id in self.user_connections:
            connections = self.user_connections[user_id].copy()
            for connection_id in connections:
                await self.send_to_connection(connection_id, message)
    
    async def send_to_channel(self, channel: str, message: WebSocketMessage):
        """Send message to all subscribers of a channel"""
        if channel in self.channel_subscriptions:
            connections = self.channel_subscriptions[channel].copy()
            for connection_id in connections:
                await self.send_to_connection(connection_id, message)
    
    async def broadcast(self, message: WebSocketMessage, exclude_connections: Set[str] = None):
        """Broadcast message to all connected clients"""
        exclude_connections = exclude_connections or set()
        
        for connection_id in list(self.active_connections.keys()):
            if connection_id not in exclude_connections:
                await self.send_to_connection(connection_id, message)
    
    async def subscribe_to_channel(self, connection_id: str, channel: str) -> bool:
        """Subscribe connection to a channel"""
        if connection_id not in self.connection_info:
            return False
        
        # Add to channel subscriptions
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(connection_id)
        
        # Update connection info
        self.connection_info[connection_id].channels.add(channel)
        
        # Confirm subscription
        await self.send_to_connection(connection_id, WebSocketMessage(
            event_type=EventType.SYSTEM_NOTIFICATION,
            data={
                "type": "channel_subscribed",
                "channel": channel,
                "status": "subscribed"
            }
        ))
        
        return True
    
    async def unsubscribe_from_channel(self, connection_id: str, channel: str) -> bool:
        """Unsubscribe connection from a channel"""
        if connection_id not in self.connection_info:
            return False
        
        # Remove from channel subscriptions
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(connection_id)
        
        # Update connection info
        self.connection_info[connection_id].channels.discard(channel)
        
        # Confirm unsubscription
        await self.send_to_connection(connection_id, WebSocketMessage(
            event_type=EventType.SYSTEM_NOTIFICATION,
            data={
                "type": "channel_unsubscribed",
                "channel": channel,
                "status": "unsubscribed"
            }
        ))
        
        return True
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "unique_users": len(self.user_connections),
            "active_channels": len(self.channel_subscriptions),
            "total_subscriptions": sum(len(subs) for subs in self.channel_subscriptions.values())
        }

# ========================================
# EVENT HANDLERS
# ========================================

class ContentEventHandler:
    """Handle content-related WebSocket events"""
    
    def __init__(self, manager: WebSocketManager):
        self.manager = manager
    
    async def handle_content_upload_progress(self, user_id: str, content_id: str, progress: float):
        """Handle content upload progress updates"""
        message = WebSocketMessage(
            event_type=EventType.CONTENT_UPLOADED,
            data={
                "content_id": content_id,
                "progress": progress,
                "status": "uploading" if progress < 100 else "completed"
            },
            sender_id="system",
            target_id=user_id
        )
        
        await self.manager.send_to_user(user_id, message)
    
    async def handle_content_protection_alert(self, user_id: str, content_id: str, violation_type: str):
        """Handle content protection violation alerts"""
        message = WebSocketMessage(
            event_type=EventType.CONTENT_VIOLATION,
            data={
                "content_id": content_id,
                "violation_type": violation_type,
                "severity": "high",
                "action_required": True
            },
            sender_id="system",
            target_id=user_id
        )
        
        await self.manager.send_to_user(user_id, message)
        
        # Also send to content protection channel
        await self.manager.send_to_channel("content_protection", message)

class CollaborationEventHandler:
    """Handle collaboration-related WebSocket events"""
    
    def __init__(self, manager: WebSocketManager):
        self.manager = manager
    
    async def handle_collaboration_request(self, from_user_id: str, to_user_id: str, collaboration_data: Dict[str, Any]):
        """Handle new collaboration request"""
        message = WebSocketMessage(
            event_type=EventType.COLLABORATION_REQUEST,
            data=collaboration_data,
            sender_id=from_user_id,
            target_id=to_user_id
        )
        
        await self.manager.send_to_user(to_user_id, message)
    
    async def handle_collaboration_response(self, from_user_id: str, to_user_id: str, response: str, collaboration_id: str):
        """Handle collaboration request response"""
        event_type = EventType.COLLABORATION_ACCEPTED if response == "accepted" else EventType.COLLABORATION_DECLINED
        
        message = WebSocketMessage(
            event_type=event_type,
            data={
                "collaboration_id": collaboration_id,
                "response": response,
                "message": f"Collaboration request {response}"
            },
            sender_id=from_user_id,
            target_id=to_user_id
        )
        
        await self.manager.send_to_user(to_user_id, message)

class AnalyticsEventHandler:
    """Handle analytics-related WebSocket events"""
    
    def __init__(self, manager: WebSocketManager):
        self.manager = manager
    
    async def handle_real_time_analytics(self, user_id: str, analytics_data: Dict[str, Any]):
        """Handle real-time analytics updates"""
        message = WebSocketMessage(
            event_type=EventType.ANALYTICS_UPDATE,
            data=analytics_data,
            sender_id="system",
            target_id=user_id
        )
        
        await self.manager.send_to_user(user_id, message)
    
    async def handle_performance_alert(self, user_id: str, alert_data: Dict[str, Any]):
        """Handle performance alerts"""
        message = WebSocketMessage(
            event_type=EventType.PERFORMANCE_ALERT,
            data=alert_data,
            sender_id="system",
            target_id=user_id
        )
        
        await self.manager.send_to_user(user_id, message)

# ========================================
# WEBSOCKET ROUTE HANDLERS
# ========================================

class WebSocketHandler:
    """Main WebSocket handler consolidating all functionality"""
    
    def __init__(self):
        self.manager = WebSocketManager()
        self.content_handler = ContentEventHandler(self.manager)
        self.collaboration_handler = CollaborationEventHandler(self.manager)
        self.analytics_handler = AnalyticsEventHandler(self.manager)
    
    async def handle_connection(self, websocket: WebSocket, user_id: str, client_info: Dict[str, Any]):
        """Handle new WebSocket connection"""
        connection_id = await self.manager.connect(websocket, user_id, client_info)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Update last activity
                if connection_id in self.manager.connection_info:
                    self.manager.connection_info[connection_id].last_activity = datetime.utcnow()
                
                # Handle different message types
                await self.handle_message(connection_id, message_data)
                
        except WebSocketDisconnect:
            await self.manager.disconnect(connection_id)
        except Exception as e:
            print(f"WebSocket error for connection {connection_id}: {e}")
            await self.manager.disconnect(connection_id)
    
    async def handle_message(self, connection_id: str, message_data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = message_data.get("type")
        
        if message_type == "subscribe":
            channel = message_data.get("channel")
            if channel:
                await self.manager.subscribe_to_channel(connection_id, channel)
        
        elif message_type == "unsubscribe":
            channel = message_data.get("channel")
            if channel:
                await self.manager.unsubscribe_from_channel(connection_id, channel)
        
        elif message_type == "ping":
            # Respond with pong for heartbeat
            pong_message = WebSocketMessage(
                event_type=EventType.SYSTEM_NOTIFICATION,
                data={"type": "pong", "timestamp": datetime.utcnow().isoformat()}
            )
            await self.manager.send_to_connection(connection_id, pong_message)
        
        elif message_type == "get_stats":
            # Send connection statistics
            stats = self.manager.get_connection_stats()
            stats_message = WebSocketMessage(
                event_type=EventType.SYSTEM_NOTIFICATION,
                data={"type": "stats", "stats": stats}
            )
            await self.manager.send_to_connection(connection_id, stats_message)

# ========================================
# WEBSOCKET DEPENDENCY
# ========================================

async def get_websocket_user(websocket: WebSocket, token: str = None) -> str:
    """Extract user ID from WebSocket connection (simplified)"""
    # In a real implementation, this would validate the token
    # For now, returning a mock user ID
    return "user_123"

# ========================================
# CHANNEL DEFINITIONS
# ========================================

class ChannelNames:
    """Predefined channel names for different types of events"""
    
    # Content channels
    CONTENT_UPLOADS = "content.uploads"
    CONTENT_PROTECTION = "content.protection"
    CONTENT_VIOLATIONS = "content.violations"
    
    # Collaboration channels
    COLLABORATION_REQUESTS = "collaboration.requests"
    COLLABORATION_MESSAGES = "collaboration.messages"
    
    # Analytics channels
    ANALYTICS_DASHBOARD = "analytics.dashboard"
    PERFORMANCE_ALERTS = "performance.alerts"
    LIVE_METRICS = "live.metrics"
    
    # System channels
    SYSTEM_NOTIFICATIONS = "system.notifications"
    SYSTEM_MAINTENANCE = "system.maintenance"
    
    # User-specific channels (format: user.{user_id})
    @staticmethod
    def user_channel(user_id: str) -> str:
        return f"user.{user_id}"
    
    # Content-specific channels (format: content.{content_id})
    @staticmethod
    def content_channel(content_id: str) -> str:
        return f"content.{content_id}"


# ========================================
# REAL-TIME COLLABORATION FEATURES
# ========================================

class CollaborationType(str, Enum):
    """Types of collaboration"""
    CONTENT_CREATION = "content_creation"
    LIVE_EDITING = "live_editing"
    REVIEW_SESSION = "review_session"
    BRAINSTORMING = "brainstorming"
    PROJECT_PLANNING = "project_planning"
    FEEDBACK_SESSION = "feedback_session"

class CollaborationPermission(str, Enum):
    """Collaboration permissions"""
    VIEW_ONLY = "view_only"
    COMMENT = "comment"
    EDIT = "edit"
    ADMIN = "admin"

class RealTimeCollaborationManager:
    """Real-time collaboration manager for creators"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.active_sessions = {}
        self.collaboration_state = defaultdict(dict)
        self.cursor_positions = defaultdict(dict)
        self.version_control = {}
        
    async def create_collaboration_session(
        self, 
        session_id: str, 
        creator_id: str, 
        collaboration_type: CollaborationType,
        content_id: str = None
    ) -> Dict[str, Any]:
        """Create new collaboration session"""
        try:
            session_data = {
                "session_id": session_id,
                "creator_id": creator_id,
                "collaboration_type": collaboration_type,
                "content_id": content_id,
                "participants": [creator_id],
                "permissions": {creator_id: CollaborationPermission.ADMIN},
                "created_at": datetime.utcnow(),
                "is_active": True,
                "state": {},
                "version": 1
            }
            
            self.active_sessions[session_id] = session_data
            self.collaboration_state[session_id] = {"content": "", "changes": []}
            
            # Notify all relevant channels
            await self.websocket_manager.broadcast_to_channel(
                f"creator.{creator_id}",
                {
                    "type": "collaboration_session_created",
                    "session_id": session_id,
                    "collaboration_type": collaboration_type.value,
                    "content_id": content_id
                }
            )
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to create collaboration session: {str(e)}")
            raise
    
    async def join_collaboration_session(
        self, 
        session_id: str, 
        user_id: str, 
        permission: CollaborationPermission = CollaborationPermission.EDIT
    ) -> Dict[str, Any]:
        """Join existing collaboration session"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError("Collaboration session not found")
            
            session = self.active_sessions[session_id]
            
            # Add participant
            if user_id not in session["participants"]:
                session["participants"].append(user_id)
                session["permissions"][user_id] = permission
            
            # Initialize user state
            self.cursor_positions[session_id][user_id] = {"line": 0, "column": 0}
            
            # Notify all participants
            await self.websocket_manager.broadcast_to_channel(
                f"collaboration.{session_id}",
                {
                    "type": "user_joined",
                    "user_id": user_id,
                    "permission": permission.value,
                    "participants": session["participants"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Send current state to new participant
            await self.websocket_manager.send_to_user(
                user_id,
                {
                    "type": "collaboration_state",
                    "session_id": session_id,
                    "state": self.collaboration_state[session_id],
                    "version": session["version"],
                    "participants": session["participants"]
                }
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to join collaboration session: {str(e)}")
            raise
    
    async def handle_live_edit(
        self, 
        session_id: str, 
        user_id: str, 
        edit_operation: Dict[str, Any]
    ) -> None:
        """Handle live editing operations"""
        try:
            if session_id not in self.active_sessions:
                return
            
            session = self.active_sessions[session_id]
            
            # Check permissions
            user_permission = session["permissions"].get(user_id)
            if user_permission not in [CollaborationPermission.EDIT, CollaborationPermission.ADMIN]:
                return
            
            # Apply edit operation
            await self._apply_edit_operation(session_id, user_id, edit_operation)
            
            # Increment version
            session["version"] += 1
            
            # Broadcast to all participants except sender
            participants = [p for p in session["participants"] if p != user_id]
            for participant in participants:
                await self.websocket_manager.send_to_user(
                    participant,
                    {
                        "type": "live_edit",
                        "session_id": session_id,
                        "user_id": user_id,
                        "operation": edit_operation,
                        "version": session["version"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to handle live edit: {str(e)}")
    
    async def handle_cursor_movement(
        self, 
        session_id: str, 
        user_id: str, 
        cursor_position: Dict[str, int]
    ) -> None:
        """Handle cursor position updates"""
        try:
            if session_id not in self.cursor_positions:
                return
            
            # Update cursor position
            self.cursor_positions[session_id][user_id] = cursor_position
            
            # Broadcast to all other participants
            session = self.active_sessions.get(session_id, {})
            participants = [p for p in session.get("participants", []) if p != user_id]
            
            for participant in participants:
                await self.websocket_manager.send_to_user(
                    participant,
                    {
                        "type": "cursor_movement",
                        "session_id": session_id,
                        "user_id": user_id,
                        "position": cursor_position,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
        except Exception as e:
            logger.error(f"Failed to handle cursor movement: {str(e)}")
    
    async def add_comment(
        self, 
        session_id: str, 
        user_id: str, 
        comment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add comment to collaboration session"""
        try:
            comment_id = str(uuid.uuid4())
            comment = {
                "comment_id": comment_id,
                "user_id": user_id,
                "content": comment_data["content"],
                "position": comment_data.get("position"),
                "timestamp": datetime.utcnow().isoformat(),
                "resolved": False
            }
            
            # Store comment
            if session_id not in self.collaboration_state:
                self.collaboration_state[session_id] = {"comments": []}
            
            if "comments" not in self.collaboration_state[session_id]:
                self.collaboration_state[session_id]["comments"] = []
            
            self.collaboration_state[session_id]["comments"].append(comment)
            
            # Broadcast to all participants
            session = self.active_sessions.get(session_id, {})
            for participant in session.get("participants", []):
                await self.websocket_manager.send_to_user(
                    participant,
                    {
                        "type": "comment_added",
                        "session_id": session_id,
                        "comment": comment
                    }
                )
            
            return comment
            
        except Exception as e:
            logger.error(f"Failed to add comment: {str(e)}")
            raise
    
    async def save_collaboration_state(self, session_id: str) -> Dict[str, Any]:
        """Save current collaboration state"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError("Session not found")
            
            session = self.active_sessions[session_id]
            state = self.collaboration_state[session_id]
            
            # Create save checkpoint
            checkpoint = {
                "checkpoint_id": str(uuid.uuid4()),
                "session_id": session_id,
                "state": state.copy(),
                "version": session["version"],
                "saved_by": session["creator_id"],
                "saved_at": datetime.utcnow().isoformat()
            }
            
            # Store checkpoint (in production, save to database)
            if session_id not in self.version_control:
                self.version_control[session_id] = []
            
            self.version_control[session_id].append(checkpoint)
            
            # Notify participants
            for participant in session["participants"]:
                await self.websocket_manager.send_to_user(
                    participant,
                    {
                        "type": "state_saved",
                        "session_id": session_id,
                        "checkpoint_id": checkpoint["checkpoint_id"],
                        "timestamp": checkpoint["saved_at"]
                    }
                )
            
            return checkpoint
            
        except Exception as e:
            logger.error(f"Failed to save collaboration state: {str(e)}")
            raise
    
    async def _apply_edit_operation(
        self, 
        session_id: str, 
        user_id: str, 
        operation: Dict[str, Any]
    ) -> None:
        """Apply edit operation to collaboration state"""
        try:
            state = self.collaboration_state[session_id]
            
            operation_type = operation.get("type")
            
            if operation_type == "insert":
                # Insert text at position
                position = operation.get("position", 0)
                text = operation.get("text", "")
                current_content = state.get("content", "")
                
                new_content = current_content[:position] + text + current_content[position:]
                state["content"] = new_content
                
            elif operation_type == "delete":
                # Delete text range
                start = operation.get("start", 0)
                end = operation.get("end", 0)
                current_content = state.get("content", "")
                
                new_content = current_content[:start] + current_content[end:]
                state["content"] = new_content
                
            elif operation_type == "replace":
                # Replace text range
                start = operation.get("start", 0)
                end = operation.get("end", 0)
                text = operation.get("text", "")
                current_content = state.get("content", "")
                
                new_content = current_content[:start] + text + current_content[end:]
                state["content"] = new_content
            
            # Record change
            if "changes" not in state:
                state["changes"] = []
            
            change_record = {
                "change_id": str(uuid.uuid4()),
                "user_id": user_id,
                "operation": operation,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            state["changes"].append(change_record)
            
        except Exception as e:
            logger.error(f"Failed to apply edit operation: {str(e)}")

class LiveStreamManager:
    """Manager for live streaming and real-time content"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.websocket_manager = websocket_manager
        self.active_streams = {}
        self.stream_viewers = defaultdict(set)
        
    async def start_live_stream(
        self, 
        stream_id: str, 
        creator_id: str, 
        stream_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start live streaming session"""
        try:
            stream_data = {
                "stream_id": stream_id,
                "creator_id": creator_id,
                "title": stream_config.get("title", "Live Stream"),
                "description": stream_config.get("description", ""),
                "category": stream_config.get("category", "general"),
                "started_at": datetime.utcnow(),
                "is_live": True,
                "viewer_count": 0,
                "chat_enabled": stream_config.get("chat_enabled", True),
                "quality": stream_config.get("quality", "720p")
            }
            
            self.active_streams[stream_id] = stream_data
            
            # Notify followers
            await self.websocket_manager.broadcast_to_channel(
                f"creator.{creator_id}.followers",
                {
                    "type": "stream_started",
                    "stream_id": stream_id,
                    "creator_id": creator_id,
                    "title": stream_data["title"],
                    "started_at": stream_data["started_at"].isoformat()
                }
            )
            
            return stream_data
            
        except Exception as e:
            logger.error(f"Failed to start live stream: {str(e)}")
            raise
    
    async def join_stream(self, stream_id: str, viewer_id: str) -> Dict[str, Any]:
        """Join live stream as viewer"""
        try:
            if stream_id not in self.active_streams:
                raise ValueError("Stream not found")
            
            stream = self.active_streams[stream_id]
            
            # Add viewer
            self.stream_viewers[stream_id].add(viewer_id)
            stream["viewer_count"] = len(self.stream_viewers[stream_id])
            
            # Notify stream
            await self.websocket_manager.broadcast_to_channel(
                f"stream.{stream_id}",
                {
                    "type": "viewer_joined",
                    "viewer_id": viewer_id,
                    "viewer_count": stream["viewer_count"]
                }
            )
            
            return stream
            
        except Exception as e:
            logger.error(f"Failed to join stream: {str(e)}")
            raise
    
    async def send_chat_message(
        self, 
        stream_id: str, 
        user_id: str, 
        message: str
    ) -> None:
        """Send chat message to live stream"""
        try:
            if stream_id not in self.active_streams:
                return
            
            stream = self.active_streams[stream_id]
            if not stream.get("chat_enabled", True):
                return
            
            chat_message = {
                "type": "chat_message",
                "stream_id": stream_id,
                "user_id": user_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Broadcast to all stream viewers
            await self.websocket_manager.broadcast_to_channel(
                f"stream.{stream_id}",
                chat_message
            )
            
        except Exception as e:
            logger.error(f"Failed to send chat message: {str(e)}")


# Initialize real-time collaboration
collaboration_manager = RealTimeCollaborationManager(WebSocketManager())
live_stream_manager = LiveStreamManager(WebSocketManager())


# ========================================
# ENHANCED WEBSOCKET HANDLER
# ========================================

class EnhancedWebSocketHandler(WebSocketHandler):
    """Enhanced WebSocket handler with collaboration features"""
    
    def __init__(self):
        super().__init__()
        self.collaboration_manager = collaboration_manager
        self.live_stream_manager = live_stream_manager
    
    async def handle_collaboration_message(self, websocket, message: Dict[str, Any]):
        """Handle collaboration-specific messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "join_collaboration":
                session_id = message.get("session_id")
                user_id = message.get("user_id")
                permission = CollaborationPermission(message.get("permission", "edit"))
                
                await self.collaboration_manager.join_collaboration_session(
                    session_id, user_id, permission
                )
                
            elif message_type == "live_edit":
                session_id = message.get("session_id")
                user_id = message.get("user_id")
                operation = message.get("operation")
                
                await self.collaboration_manager.handle_live_edit(
                    session_id, user_id, operation
                )
                
            elif message_type == "cursor_movement":
                session_id = message.get("session_id")
                user_id = message.get("user_id")
                position = message.get("position")
                
                await self.collaboration_manager.handle_cursor_movement(
                    session_id, user_id, position
                )
                
            elif message_type == "add_comment":
                session_id = message.get("session_id")
                user_id = message.get("user_id")
                comment_data = message.get("comment_data")
                
                await self.collaboration_manager.add_comment(
                    session_id, user_id, comment_data
                )
                
        except Exception as e:
            logger.error(f"Failed to handle collaboration message: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": "Failed to process collaboration message"
            })


# ========================================
# UPDATED GLOBAL INSTANCE
# ========================================

# Enhanced WebSocket handler instance
enhanced_websocket_handler = EnhancedWebSocketHandler()

def get_enhanced_websocket_handler() -> EnhancedWebSocketHandler:
    """Get enhanced WebSocket handler instance"""
    return enhanced_websocket_handler

# Keep backward compatibility
websocket_handler = WebSocketHandler()

def get_websocket_handler() -> WebSocketHandler:
    """Get WebSocket handler instance (backward compatibility)"""
    return websocket_handler


# ========================================
# UPDATED EXPORTS
# ========================================

__all__ = [
    "EventType",
    "ConnectionStatus", 
    "CollaborationType",
    "CollaborationPermission",
    "WebSocketMessage",
    "ConnectionInfo",
    "WebSocketManager",
    "ContentEventHandler",
    "CollaborationEventHandler", 
    "AnalyticsEventHandler",
    "WebSocketHandler",
    "EnhancedWebSocketHandler",
    "RealTimeCollaborationManager",
    "LiveStreamManager",
    "ChannelNames",
    "get_websocket_handler",
    "get_enhanced_websocket_handler",
    "get_websocket_user",
    "collaboration_manager",
    "live_stream_manager"
]