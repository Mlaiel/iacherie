"""Real-Time Collaboration - Live Collaboration Engine

Real-time collaboration system for creator partnerships with live editing,
communication, and synchronization capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import websockets
import time

logger = logging.getLogger(__name__)


class CollabSessionType(Enum):
    """Types of collaboration sessions"""
    DOCUMENT_EDITING = "document_editing"
    VIDEO_EDITING = "video_editing"
    AUDIO_PRODUCTION = "audio_production"
    DESIGN_REVIEW = "design_review"
    BRAINSTORMING = "brainstorming"
    LIVE_STREAM = "live_stream"
    CODE_COLLABORATION = "code_collaboration"
    PROJECT_PLANNING = "project_planning"


class ParticipantRole(Enum):
    """Participant roles in collaboration"""
    HOST = "host"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    GUEST = "guest"


class CollabEventType(Enum):
    """Types of collaboration events"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CURSOR_MOVED = "cursor_moved"
    CONTENT_CHANGED = "content_changed"
    COMMENT_ADDED = "comment_added"
    FILE_UPLOADED = "file_uploaded"
    STATUS_CHANGED = "status_changed"
    VOICE_STARTED = "voice_started"
    VOICE_STOPPED = "voice_stopped"
    SCREEN_SHARED = "screen_shared"
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"


@dataclass
class CollabParticipant:
    """Collaboration session participant"""
    user_id: str
    username: str
    role: ParticipantRole
    is_online: bool = True
    last_seen: datetime = field(default_factory=datetime.now)
    cursor_position: Optional[Dict[str, Any]] = None
    permissions: List[str] = field(default_factory=list)
    session_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollabEvent:
    """Real-time collaboration event"""
    event_id: str
    event_type: CollabEventType
    session_id: str
    user_id: str
    timestamp: datetime
    data: Dict[str, Any]
    requires_sync: bool = True


@dataclass
class CollabState:
    """Current collaboration state"""
    session_id: str
    content: Dict[str, Any]
    version: int
    last_modified: datetime
    locked_sections: Dict[str, str]  # section_id -> user_id
    active_users: Dict[str, str]  # user_id -> cursor_position
    change_history: List[Dict[str, Any]]


@dataclass
class CollabSession:
    """Real-time collaboration session"""
    session_id: str
    title: str
    session_type: CollabSessionType
    host_id: str
    participants: Dict[str, CollabParticipant]
    current_state: CollabState
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    recording_enabled: bool = False
    voice_enabled: bool = False
    screen_sharing_enabled: bool = False


@dataclass
class SyncMessage:
    """Synchronization message for real-time updates"""
    message_id: str
    session_id: str
    operation: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    sender_id: Optional[str] = None


class RealTimeCollab:
    """Real-time collaboration engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Active collaboration sessions
        self.sessions: Dict[str, CollabSession] = {}
        
        # WebSocket connections for real-time communication
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        
        # Event handlers
        self.event_handlers: Dict[CollabEventType, List[Callable]] = {}
        
        # Sync queue for operations
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        
        # Configuration
        self.max_participants = self.config.get('max_participants', 10)
        self.session_timeout = self.config.get('session_timeout', 3600)  # 1 hour
        self.auto_save_interval = self.config.get('auto_save_interval', 30)  # 30 seconds
        
        # Performance monitoring
        self.metrics = {
            'active_sessions': 0,
            'total_events': 0,
            'sync_latency': [],
            'connection_count': 0
        }
        
        logger.info("RealTimeCollab engine initialized")
    
    async def initialize(self):
        """Initialize the real-time collaboration engine"""
        logger.info("Initializing Real-Time Collaboration...")
        
        # Start background tasks
        asyncio.create_task(self._sync_processor())
        asyncio.create_task(self._session_cleanup())
        asyncio.create_task(self._auto_save_sessions())
        asyncio.create_task(self._metrics_collector())
        
        # Initialize event handlers
        self._setup_default_event_handlers()
        
        logger.info("Real-Time Collaboration initialized successfully")
    
    async def shutdown(self):
        """Shutdown the real-time collaboration engine"""
        logger.info("Shutting down Real-Time Collaboration...")
        
        # Close all sessions
        for session_id in list(self.sessions.keys()):
            await self.end_session(session_id)
        
        # Close all connections
        for connections in self.connections.values():
            for conn in connections:
                await conn.close()
        
        logger.info("Real-Time Collaboration shutdown complete")
    
    async def create_session(
        self,
        title: str,
        session_type: CollabSessionType,
        host_id: str,
        settings: Dict[str, Any] = None
    ) -> CollabSession:
        """Create a new collaboration session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create host participant
            host_participant = CollabParticipant(
                user_id=host_id,
                username=settings.get('host_username', f'User_{host_id}'),
                role=ParticipantRole.HOST,
                permissions=['edit', 'invite', 'kick', 'manage']
            )
            
            # Initialize collaboration state
            initial_state = CollabState(
                session_id=session_id,
                content={},
                version=1,
                last_modified=datetime.now(),
                locked_sections={},
                active_users={},
                change_history=[]
            )
            
            # Create session
            session = CollabSession(
                session_id=session_id,
                title=title,
                session_type=session_type,
                host_id=host_id,
                participants={host_id: host_participant},
                current_state=initial_state,
                settings=settings or {},
                expires_at=datetime.now().timestamp() + self.session_timeout if self.session_timeout else None
            )
            
            # Store session
            self.sessions[session_id] = session
            self.metrics['active_sessions'] += 1
            
            # Initialize connection pool for session
            self.connections[session_id] = set()
            
            logger.info(f"Created collaboration session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating collaboration session: {str(e)}")
            raise
    
    async def join_session(
        self,
        session_id: str,
        user_id: str,
        username: str,
        role: ParticipantRole = ParticipantRole.EDITOR
    ) -> CollabParticipant:
        """Join an existing collaboration session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            if not session.is_active:
                raise ValueError(f"Session {session_id} is not active")
            
            if len(session.participants) >= self.max_participants:
                raise ValueError("Session is at maximum capacity")
            
            # Create participant
            participant = CollabParticipant(
                user_id=user_id,
                username=username,
                role=role,
                permissions=self._get_role_permissions(role)
            )
            
            # Add to session
            session.participants[user_id] = participant
            
            # Broadcast join event
            join_event = CollabEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollabEventType.USER_JOINED,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                data={'username': username, 'role': role.value}
            )
            
            await self._broadcast_event(session_id, join_event)
            
            logger.info(f"User {user_id} joined session {session_id}")
            return participant
            
        except Exception as e:
            logger.error(f"Error joining session: {str(e)}")
            raise
    
    async def leave_session(self, session_id: str, user_id: str):
        """Leave a collaboration session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return
            
            if user_id in session.participants:
                # Remove participant
                del session.participants[user_id]
                
                # Clear any locks held by this user
                session.current_state.locked_sections = {
                    section: uid for section, uid in session.current_state.locked_sections.items()
                    if uid != user_id
                }
                
                # Remove from active users
                session.current_state.active_users.pop(user_id, None)
                
                # Broadcast leave event
                leave_event = CollabEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=CollabEventType.USER_LEFT,
                    session_id=session_id,
                    user_id=user_id,
                    timestamp=datetime.now(),
                    data={}
                )
                
                await self._broadcast_event(session_id, leave_event)
                
                # If host left and there are other participants, transfer host
                if user_id == session.host_id and session.participants:
                    new_host_id = next(iter(session.participants.keys()))
                    session.host_id = new_host_id
                    session.participants[new_host_id].role = ParticipantRole.HOST
                    session.participants[new_host_id].permissions = self._get_role_permissions(ParticipantRole.HOST)
                
                # If no participants left, mark session for cleanup
                if not session.participants:
                    session.is_active = False
                
                logger.info(f"User {user_id} left session {session_id}")
            
        except Exception as e:
            logger.error(f"Error leaving session: {str(e)}")
            raise
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        try:
            session_id = None
            user_id = None
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'join':
                        session_id = data.get('session_id')
                        user_id = data.get('user_id')
                        
                        if session_id in self.sessions:
                            self.connections[session_id].add(websocket)
                            self.metrics['connection_count'] += 1
                            
                            # Send current state to new connection
                            await self._send_current_state(websocket, session_id)
                    
                    elif msg_type == 'event':
                        if session_id and user_id:
                            await self._handle_collaboration_event(data, session_id, user_id)
                    
                    elif msg_type == 'sync':
                        if session_id:
                            await self._handle_sync_operation(data, session_id, user_id)
                
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received from WebSocket")
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {str(e)}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Cleanup connection
            if session_id and session_id in self.connections:
                self.connections[session_id].discard(websocket)
                self.metrics['connection_count'] -= 1
                
            if session_id and user_id:
                await self.leave_session(session_id, user_id)
    
    async def update_content(
        self,
        session_id: str,
        user_id: str,
        operation: str,
        data: Dict[str, Any]
    ):
        """Update collaboration content with operational transformation"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            participant = session.participants.get(user_id)
            if not participant or 'edit' not in participant.permissions:
                raise ValueError("User does not have edit permissions")
            
            # Apply operational transformation
            transformed_op = await self._apply_operational_transform(session, operation, data)
            
            # Update session state
            session.current_state.version += 1
            session.current_state.last_modified = datetime.now()
            
            # Add to change history
            change = {
                'version': session.current_state.version,
                'operation': operation,
                'data': transformed_op,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
            session.current_state.change_history.append(change)
            
            # Create sync message
            sync_msg = SyncMessage(
                message_id=str(uuid.uuid4()),
                session_id=session_id,
                operation=operation,
                data=transformed_op,
                sender_id=user_id
            )
            
            # Add to sync queue
            await self.sync_queue.put(sync_msg)
            
            logger.info(f"Content updated in session {session_id} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating content: {str(e)}")
            raise
    
    async def lock_section(self, session_id: str, user_id: str, section_id: str) -> bool:
        """Lock a section for exclusive editing"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            # Check if section is already locked
            if section_id in session.current_state.locked_sections:
                current_owner = session.current_state.locked_sections[section_id]
                if current_owner != user_id:
                    return False
            
            # Lock section
            session.current_state.locked_sections[section_id] = user_id
            
            # Broadcast lock event
            lock_event = CollabEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollabEventType.STATUS_CHANGED,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                data={'action': 'section_locked', 'section_id': section_id}
            )
            
            await self._broadcast_event(session_id, lock_event)
            return True
            
        except Exception as e:
            logger.error(f"Error locking section: {str(e)}")
            return False
    
    async def unlock_section(self, session_id: str, user_id: str, section_id: str) -> bool:
        """Unlock a section"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            # Check if user owns the lock
            if session.current_state.locked_sections.get(section_id) != user_id:
                # Allow host to unlock any section
                participant = session.participants.get(user_id)
                if not participant or participant.role != ParticipantRole.HOST:
                    return False
            
            # Unlock section
            if section_id in session.current_state.locked_sections:
                del session.current_state.locked_sections[section_id]
            
            # Broadcast unlock event
            unlock_event = CollabEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollabEventType.STATUS_CHANGED,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                data={'action': 'section_unlocked', 'section_id': section_id}
            )
            
            await self._broadcast_event(session_id, unlock_event)
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking section: {str(e)}")
            return False
    
    async def add_comment(
        self,
        session_id: str,
        user_id: str,
        text: str,
        position: Dict[str, Any] = None
    ):
        """Add a comment to the collaboration"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            comment_id = str(uuid.uuid4())
            
            # Create comment event
            comment_event = CollabEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollabEventType.COMMENT_ADDED,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                data={
                    'comment_id': comment_id,
                    'text': text,
                    'position': position,
                    'username': session.participants[user_id].username
                }
            )
            
            await self._broadcast_event(session_id, comment_event)
            
            logger.info(f"Comment added to session {session_id} by user {user_id}")
            
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            raise
    
    async def start_voice_session(self, session_id: str, user_id: str):
        """Start voice communication for a user"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            if not session.voice_enabled:
                raise ValueError("Voice is not enabled for this session")
            
            # Broadcast voice start event
            voice_event = CollabEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollabEventType.VOICE_STARTED,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                data={'username': session.participants[user_id].username}
            )
            
            await self._broadcast_event(session_id, voice_event)
            
            logger.info(f"Voice started for user {user_id} in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error starting voice session: {str(e)}")
            raise
    
    async def start_screen_sharing(self, session_id: str, user_id: str):
        """Start screen sharing for a user"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            if not session.screen_sharing_enabled:
                raise ValueError("Screen sharing is not enabled for this session")
            
            # Check permissions
            participant = session.participants.get(user_id)
            if not participant or 'screen_share' not in participant.permissions:
                raise ValueError("User does not have screen sharing permissions")
            
            # Broadcast screen sharing event
            screen_event = CollabEvent(
                event_id=str(uuid.uuid4()),
                event_type=CollabEventType.SCREEN_SHARED,
                session_id=session_id,
                user_id=user_id,
                timestamp=datetime.now(),
                data={'username': participant.username}
            )
            
            await self._broadcast_event(session_id, screen_event)
            
            logger.info(f"Screen sharing started for user {user_id} in session {session_id}")
            
        except Exception as e:
            logger.error(f"Error starting screen sharing: {str(e)}")
            raise
    
    async def end_session(self, session_id: str):
        """End a collaboration session"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                return
            
            # Mark session as inactive
            session.is_active = False
            
            # Close all connections
            if session_id in self.connections:
                connections = list(self.connections[session_id])
                for conn in connections:
                    try:
                        await conn.close()
                    except:
                        pass
                del self.connections[session_id]
            
            # Save final state if needed
            await self._save_session_state(session)
            
            # Remove from active sessions
            del self.sessions[session_id]
            self.metrics['active_sessions'] -= 1
            
            logger.info(f"Session {session_id} ended")
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            raise
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.session_id,
            'title': session.title,
            'session_type': session.session_type.value,
            'host_id': session.host_id,
            'participant_count': len(session.participants),
            'participants': [
                {
                    'user_id': p.user_id,
                    'username': p.username,
                    'role': p.role.value,
                    'is_online': p.is_online
                }
                for p in session.participants.values()
            ],
            'created_at': session.created_at.isoformat(),
            'is_active': session.is_active,
            'version': session.current_state.version
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collaboration metrics"""
        avg_latency = sum(self.metrics['sync_latency']) / len(self.metrics['sync_latency']) if self.metrics['sync_latency'] else 0
        
        return {
            'active_sessions': self.metrics['active_sessions'],
            'total_events': self.metrics['total_events'],
            'connection_count': self.metrics['connection_count'],
            'average_sync_latency': avg_latency,
            'sync_queue_size': self.sync_queue.qsize()
        }
    
    # Private helper methods
    
    def _get_role_permissions(self, role: ParticipantRole) -> List[str]:
        """Get permissions for a role"""
        permissions = {
            ParticipantRole.HOST: ['edit', 'invite', 'kick', 'manage', 'screen_share', 'record'],
            ParticipantRole.EDITOR: ['edit', 'comment', 'voice'],
            ParticipantRole.REVIEWER: ['comment', 'voice'],
            ParticipantRole.VIEWER: ['view'],
            ParticipantRole.GUEST: ['view', 'comment']
        }
        return permissions.get(role, ['view'])
    
    def _setup_default_event_handlers(self):
        """Setup default event handlers"""
        self.event_handlers[CollabEventType.USER_JOINED] = [self._handle_user_joined]
        self.event_handlers[CollabEventType.USER_LEFT] = [self._handle_user_left]
        self.event_handlers[CollabEventType.CONTENT_CHANGED] = [self._handle_content_changed]
    
    async def _handle_user_joined(self, event: CollabEvent):
        """Handle user joined event"""
        logger.info(f"User {event.user_id} joined session {event.session_id}")
    
    async def _handle_user_left(self, event: CollabEvent):
        """Handle user left event"""
        logger.info(f"User {event.user_id} left session {event.session_id}")
    
    async def _handle_content_changed(self, event: CollabEvent):
        """Handle content changed event"""
        logger.info(f"Content changed in session {event.session_id} by user {event.user_id}")
    
    async def _broadcast_event(self, session_id: str, event: CollabEvent):
        """Broadcast event to all session participants"""
        if session_id not in self.connections:
            return
        
        message = json.dumps({
            'type': 'event',
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'user_id': event.user_id,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data
        })
        
        connections = list(self.connections[session_id])
        for conn in connections:
            try:
                await conn.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.connections[session_id].discard(conn)
        
        self.metrics['total_events'] += 1
        
        # Call event handlers
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {str(e)}")
    
    async def _send_current_state(self, websocket, session_id: str):
        """Send current session state to a WebSocket connection"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        state_message = json.dumps({
            'type': 'state',
            'session_id': session_id,
            'version': session.current_state.version,
            'content': session.current_state.content,
            'locked_sections': session.current_state.locked_sections,
            'active_users': session.current_state.active_users
        })
        
        try:
            await websocket.send(state_message)
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def _handle_collaboration_event(self, data: Dict[str, Any], session_id: str, user_id: str):
        """Handle incoming collaboration event"""
        event_type = CollabEventType(data.get('event_type'))
        
        event = CollabEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            session_id=session_id,
            user_id=user_id,
            timestamp=datetime.now(),
            data=data.get('data', {})
        )
        
        await self._broadcast_event(session_id, event)
    
    async def _handle_sync_operation(self, data: Dict[str, Any], session_id: str, user_id: str):
        """Handle synchronization operation"""
        sync_msg = SyncMessage(
            message_id=str(uuid.uuid4()),
            session_id=session_id,
            operation=data.get('operation'),
            data=data.get('data', {}),
            sender_id=user_id
        )
        
        await self.sync_queue.put(sync_msg)
    
    async def _apply_operational_transform(self, session: CollabSession, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply operational transformation to resolve conflicts"""
        # Simplified operational transformation
        # In a real implementation, this would be much more sophisticated
        
        # For now, just return the data as-is
        # Actual OT would transform operations based on concurrent changes
        return data
    
    async def _sync_processor(self):
        """Process synchronization queue"""
        while True:
            try:
                sync_msg = await self.sync_queue.get()
                start_time = time.time()
                
                # Process sync operation
                await self._process_sync_message(sync_msg)
                
                # Track latency
                latency = time.time() - start_time
                self.metrics['sync_latency'].append(latency)
                
                # Keep only recent latency measurements
                if len(self.metrics['sync_latency']) > 100:
                    self.metrics['sync_latency'] = self.metrics['sync_latency'][-100:]
                
                self.sync_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing sync message: {str(e)}")
    
    async def _process_sync_message(self, sync_msg: SyncMessage):
        """Process a synchronization message"""
        session = self.sessions.get(sync_msg.session_id)
        if not session:
            return
        
        # Apply operation to session state
        if sync_msg.operation == 'content_update':
            session.current_state.content.update(sync_msg.data)
        
        # Broadcast to other participants
        if sync_msg.session_id in self.connections:
            message = json.dumps({
                'type': 'sync',
                'operation': sync_msg.operation,
                'data': sync_msg.data,
                'sender_id': sync_msg.sender_id,
                'timestamp': sync_msg.timestamp.isoformat()
            })
            
            connections = list(self.connections[sync_msg.session_id])
            for conn in connections:
                try:
                    await conn.send(message)
                except websockets.exceptions.ConnectionClosed:
                    self.connections[sync_msg.session_id].discard(conn)
    
    async def _session_cleanup(self):
        """Cleanup inactive sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    # Check if session has expired
                    if session.expires_at and current_time.timestamp() > session.expires_at:
                        expired_sessions.append(session_id)
                    
                    # Check if session has no participants
                    elif not session.participants and not session.is_active:
                        expired_sessions.append(session_id)
                
                # End expired sessions
                for session_id in expired_sessions:
                    await self.end_session(session_id)
                
                # Sleep for cleanup interval
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {str(e)}")
                await asyncio.sleep(60)
    
    async def _auto_save_sessions(self):
        """Auto-save session states"""
        while True:
            try:
                for session in self.sessions.values():
                    if session.is_active and session.current_state.change_history:
                        await self._save_session_state(session)
                
                await asyncio.sleep(self.auto_save_interval)
                
            except Exception as e:
                logger.error(f"Error in auto-save: {str(e)}")
                await asyncio.sleep(60)
    
    async def _save_session_state(self, session: CollabSession):
        """Save session state to persistent storage"""
        # In real implementation, save to database
        logger.debug(f"Saving state for session {session.session_id}")
    
    async def _metrics_collector(self):
        """Collect and log metrics"""
        while True:
            try:
                metrics = self.get_metrics()
                logger.info(f"Collaboration metrics: {metrics}")
                
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {str(e)}")
                await asyncio.sleep(60)


# Export main classes
__all__ = [
    'RealTimeCollab', 'CollabSession', 'CollabParticipant', 'CollabEvent', 'CollabState',
    'CollabSessionType', 'ParticipantRole', 'CollabEventType', 'SyncMessage'
]