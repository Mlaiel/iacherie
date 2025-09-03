"""Real-Time WebSocket Server
WebSocket server for real-time collaboration features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Set, Optional, Any
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
import ssl
import jwt

from .realtime_collaboration_service import RealtimeCollaborationService, SessionType
from .virtual_daw_service import VirtualDAWService

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """Manages WebSocket connections for real-time collaboration"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self.session_connections: Dict[str, Set[str]] = {}  # session_id -> user_ids
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect_user(
        self, 
        websocket: WebSocketServerProtocol, 
        user_id: str,
        connection_metadata: Optional[Dict] = None
    ):
        """Register new WebSocket connection"""
        try:
            connection_id = f"{user_id}_{str(uuid.uuid4())[:8]}"
            
            self.active_connections[connection_id] = websocket
            
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "connected_at": datetime.now().isoformat(),
                "metadata": connection_metadata or {}
            }
            
            # Send connection acknowledgment
            await websocket.send(json.dumps({
                "type": "connection_established",
                "connection_id": connection_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            logger.info(f"User {user_id} connected with connection {connection_id}")
            return connection_id
            
        except Exception as e:
            logger.error(f"Error connecting user: {str(e)}")
            raise

    async def disconnect_user(self, connection_id: str):
        """Disconnect user and cleanup"""
        try:
            if connection_id not in self.active_connections:
                return
            
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            # Remove from active connections
            del self.active_connections[connection_id]
            del self.connection_metadata[connection_id]
            
            # Clean up session connections
            if user_id:
                for session_id in self.user_sessions.get(user_id, set()).copy():
                    if session_id in self.session_connections:
                        self.session_connections[session_id].discard(user_id)
                        if not self.session_connections[session_id]:
                            del self.session_connections[session_id]
                
                # Clean up user sessions if no active connections
                remaining_connections = [
                    conn_id for conn_id, conn_meta in self.connection_metadata.items()
                    if conn_meta.get("user_id") == user_id
                ]
                
                if not remaining_connections:
                    self.user_sessions.pop(user_id, None)
            
            logger.info(f"Disconnected connection {connection_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting user: {str(e)}")

    async def join_session(self, connection_id: str, session_id: str):
        """Add connection to session"""
        try:
            if connection_id not in self.active_connections:
                return False
            
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            if not user_id:
                return False
            
            # Add to session connections
            if session_id not in self.session_connections:
                self.session_connections[session_id] = set()
            self.session_connections[session_id].add(user_id)
            
            # Add to user sessions
            self.user_sessions[user_id].add(session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error joining session: {str(e)}")
            return False

    async def leave_session(self, connection_id: str, session_id: str):
        """Remove connection from session"""
        try:
            metadata = self.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            if not user_id:
                return
            
            # Remove from session connections
            if session_id in self.session_connections:
                self.session_connections[session_id].discard(user_id)
                if not self.session_connections[session_id]:
                    del self.session_connections[session_id]
            
            # Remove from user sessions
            if user_id in self.user_sessions:
                self.user_sessions[user_id].discard(session_id)
                
        except Exception as e:
            logger.error(f"Error leaving session: {str(e)}")

    async def broadcast_to_session(
        self, 
        session_id: str, 
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all users in session"""
        try:
            if session_id not in self.session_connections:
                return
            
            message_json = json.dumps(message)
            
            for user_id in self.session_connections[session_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                
                # Send to all connections for this user
                user_connections = [
                    conn_id for conn_id, metadata in self.connection_metadata.items()
                    if metadata.get("user_id") == user_id
                ]
                
                for conn_id in user_connections:
                    websocket = self.active_connections.get(conn_id)
                    if websocket:
                        try:
                            await websocket.send(message_json)
                        except Exception as e:
                            logger.warning(f"Failed to send to connection {conn_id}: {str(e)}")
                            await self.disconnect_user(conn_id)
                            
        except Exception as e:
            logger.error(f"Error broadcasting to session: {str(e)}")

    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        try:
            message_json = json.dumps(message)
            
            # Send to all connections for this user
            user_connections = [
                conn_id for conn_id, metadata in self.connection_metadata.items()
                if metadata.get("user_id") == user_id
            ]
            
            for conn_id in user_connections:
                websocket = self.active_connections.get(conn_id)
                if websocket:
                    try:
                        await websocket.send(message_json)
                    except Exception as e:
                        logger.warning(f"Failed to send to user {user_id}: {str(e)}")
                        await self.disconnect_user(conn_id)
                        
        except Exception as e:
            logger.error(f"Error sending to user: {str(e)}")


class RealtimeWebSocketServer:
    """WebSocket server for real-time collaboration"""
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8765,
        ssl_context: Optional[ssl.SSLContext] = None
    ):
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.connection_manager = WebSocketConnectionManager()
        self.collaboration_service = RealtimeCollaborationService()
        self.daw_service = VirtualDAWService()
        self.jwt_secret = "your-jwt-secret-key"  # In production, use environment variable
        
    async def start_server(self):
        """Start WebSocket server"""
        try:
            # Initialize services
            await self.collaboration_service.initialize()
            
            # Start WebSocket server
            async def handle_client(websocket, path):
                await self.handle_connection(websocket, path)
            
            server = await websockets.serve(
                handle_client,
                self.host,
                self.port,
                ssl=self.ssl_context
            )
            
            logger.info(f"Real-time WebSocket server started on {self.host}:{self.port}")
            
            # Keep server running
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {str(e)}")
            raise

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        connection_id = None
        try:
            # Wait for authentication message
            auth_message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            auth_data = json.loads(auth_message)
            
            # Authenticate user
            user_id = await self.authenticate_user(auth_data)
            if not user_id:
                await websocket.send(json.dumps({
                    "type": "auth_failed",
                    "message": "Authentication failed"
                }))
                return
            
            # Register connection
            connection_id = await self.connection_manager.connect_user(
                websocket, user_id, auth_data.get("metadata")
            )
            
            # Handle messages
            async for message in websocket:
                try:
                    await self.handle_message(connection_id, message)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received from {connection_id}")
                except Exception as e:
                    logger.error(f"Error handling message from {connection_id}: {str(e)}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection {connection_id} closed")
        except asyncio.TimeoutError:
            logger.warning("Authentication timeout")
        except Exception as e:
            logger.error(f"Error in connection handler: {str(e)}")
        finally:
            if connection_id:
                await self.connection_manager.disconnect_user(connection_id)

    async def authenticate_user(self, auth_data: Dict[str, Any]) -> Optional[str]:
        """Authenticate user connection"""
        try:
            auth_type = auth_data.get("type")
            
            if auth_type == "jwt":
                token = auth_data.get("token")
                if token:
                    try:
                        payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                        return payload.get("user_id")
                    except jwt.InvalidTokenError:
                        return None
            
            elif auth_type == "api_key":
                api_key = auth_data.get("api_key")
                user_id = auth_data.get("user_id")
                # Validate API key (implement your validation logic)
                if api_key and user_id:
                    return user_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None

    async def handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            metadata = self.connection_manager.connection_metadata.get(connection_id, {})
            user_id = metadata.get("user_id")
            
            if not user_id:
                return
            
            # Route message based on type
            if message_type == "join_session":
                await self.handle_join_session(connection_id, user_id, data)
                
            elif message_type == "leave_session":
                await self.handle_leave_session(connection_id, user_id, data)
                
            elif message_type == "create_session":
                await self.handle_create_session(connection_id, user_id, data)
                
            elif message_type == "realtime_update":
                await self.handle_realtime_update(connection_id, user_id, data)
                
            elif message_type == "daw_command":
                await self.handle_daw_command(connection_id, user_id, data)
                
            elif message_type == "annotation":
                await self.handle_annotation(connection_id, user_id, data)
                
            elif message_type == "chat_message":
                await self.handle_chat_message(connection_id, user_id, data)
                
            elif message_type == "version_control":
                await self.handle_version_control(connection_id, user_id, data)
                
            elif message_type == "webrtc_signal":
                await self.handle_webrtc_signal(connection_id, user_id, data)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")

    async def handle_join_session(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle session join request"""
        try:
            session_id = data.get("session_id")
            session_type = data.get("session_type", "live_annotation")
            
            if not session_id:
                return
            
            # Join collaboration session
            websocket = self.connection_manager.active_connections[connection_id]
            success = await self.collaboration_service.join_session(
                session_id, user_id, websocket
            )
            
            if success:
                # Update connection manager
                await self.connection_manager.join_session(connection_id, session_id)
                
                # Join DAW session if it's audio production
                if session_type == "audio_production":
                    await self.daw_service.join_daw_session(session_id, user_id)
                
                logger.info(f"User {user_id} joined session {session_id}")
            else:
                await websocket.send(json.dumps({
                    "type": "join_failed",
                    "session_id": session_id,
                    "message": "Failed to join session"
                }))
                
        except Exception as e:
            logger.error(f"Error handling join session: {str(e)}")

    async def handle_leave_session(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle session leave request"""
        try:
            session_id = data.get("session_id")
            
            if not session_id:
                return
            
            # Leave collaboration session
            await self.collaboration_service.leave_session(session_id, user_id)
            
            # Update connection manager
            await self.connection_manager.leave_session(connection_id, session_id)
            
            logger.info(f"User {user_id} left session {session_id}")
            
        except Exception as e:
            logger.error(f"Error handling leave session: {str(e)}")

    async def handle_create_session(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle session creation request"""
        try:
            session_type = SessionType(data.get("session_type", "live_annotation"))
            project_id = data.get("project_id", str(uuid.uuid4()))
            session_config = data.get("config", {})
            
            # Create collaboration session
            session = await self.collaboration_service.create_realtime_session(
                user_id, session_type, project_id, session_config
            )
            
            # Create DAW session if needed
            if session_type == SessionType.AUDIO_PRODUCTION:
                daw_session = await self.daw_service.create_daw_session(
                    user_id, data.get("daw_template")
                )
                session.session_state["daw_session_id"] = daw_session.session_id
            
            # Send response
            websocket = self.connection_manager.active_connections[connection_id]
            await websocket.send(json.dumps({
                "type": "session_created",
                "session": {
                    "session_id": session.session_id,
                    "session_type": session.session_type.value,
                    "project_id": session.project_id,
                    "webrtc_config": session.webrtc_config,
                    "session_state": session.session_state
                }
            }))
            
            logger.info(f"Created session {session.session_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")

    async def handle_realtime_update(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle real-time collaboration update"""
        try:
            session_id = data.get("session_id")
            update_data = data.get("data", {})
            
            if not session_id:
                return
            
            # Handle real-time message
            await self.collaboration_service.handle_realtime_message(
                session_id, user_id, {
                    "type": "state_update",
                    "data": update_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling realtime update: {str(e)}")

    async def handle_daw_command(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle DAW-specific command"""
        try:
            session_id = data.get("session_id")
            command = data.get("command")
            command_data = data.get("data", {})
            
            if not session_id or not command:
                return
            
            websocket = self.connection_manager.active_connections[connection_id]
            
            # Route DAW commands
            if command == "create_track":
                track = await self.daw_service.create_track(
                    session_id, user_id, command_data
                )
                await websocket.send(json.dumps({
                    "type": "track_created",
                    "track": asdict(track) if track else None
                }))
                
            elif command == "update_track_parameter":
                success = await self.daw_service.update_track_parameter(
                    session_id, user_id,
                    command_data.get("track_id"),
                    command_data.get("parameter"),
                    command_data.get("value")
                )
                await websocket.send(json.dumps({
                    "type": "parameter_updated",
                    "success": success
                }))
                
            elif command == "start_playback":
                success = await self.daw_service.start_playback(
                    session_id, user_id, command_data.get("position", 0.0)
                )
                await websocket.send(json.dumps({
                    "type": "playback_started",
                    "success": success
                }))
                
            elif command == "stop_playback":
                success = await self.daw_service.stop_playback(session_id, user_id)
                await websocket.send(json.dumps({
                    "type": "playback_stopped",
                    "success": success
                }))
                
            elif command == "start_recording":
                success = await self.daw_service.start_recording(
                    session_id, user_id,
                    command_data.get("track_id"),
                    command_data.get("input_source", "default")
                )
                await websocket.send(json.dumps({
                    "type": "recording_started",
                    "success": success
                }))
                
            elif command == "get_session_state":
                state = await self.daw_service.get_session_state(session_id)
                await websocket.send(json.dumps({
                    "type": "session_state",
                    "state": state
                }))
                
        except Exception as e:
            logger.error(f"Error handling DAW command: {str(e)}")

    async def handle_annotation(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle annotation creation/update"""
        try:
            session_id = data.get("session_id")
            annotation_data = data.get("data", {})
            
            if not session_id:
                return
            
            await self.collaboration_service.handle_realtime_message(
                session_id, user_id, {
                    "type": "annotation",
                    "data": annotation_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling annotation: {str(e)}")

    async def handle_chat_message(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle chat message with translation"""
        try:
            session_id = data.get("session_id")
            chat_data = data.get("data", {})
            
            if not session_id:
                return
            
            await self.collaboration_service.handle_realtime_message(
                session_id, user_id, {
                    "type": "chat_message",
                    "data": chat_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")

    async def handle_version_control(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle version control operations"""
        try:
            session_id = data.get("session_id")
            vc_command = data.get("command")
            vc_data = data.get("data", {})
            
            if not session_id or not vc_command:
                return
            
            websocket = self.connection_manager.active_connections[connection_id]
            
            if vc_command == "commit":
                version = await self.collaboration_service.create_version_snapshot(
                    session_id, user_id,
                    vc_data.get("changes", {}),
                    vc_data.get("message", ""),
                    vc_data.get("create_branch", False),
                    vc_data.get("branch_name")
                )
                
                await websocket.send(json.dumps({
                    "type": "version_committed",
                    "version": asdict(version) if version else None
                }))
                
        except Exception as e:
            logger.error(f"Error handling version control: {str(e)}")

    async def handle_webrtc_signal(
        self, 
        connection_id: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Handle WebRTC signaling"""
        try:
            session_id = data.get("session_id")
            signal_data = data.get("data", {})
            
            if not session_id:
                return
            
            await self.collaboration_service.handle_realtime_message(
                session_id, user_id, {
                    "type": "webrtc_signal",
                    "data": signal_data
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling WebRTC signal: {str(e)}")


# Helper function to start server
async def start_realtime_server(
    host: str = "localhost",
    port: int = 8765,
    ssl_cert_path: Optional[str] = None,
    ssl_key_path: Optional[str] = None
):
    """Start real-time WebSocket server"""
    ssl_context = None
    
    if ssl_cert_path and ssl_key_path:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(ssl_cert_path, ssl_key_path)
    
    server = RealtimeWebSocketServer(host, port, ssl_context)
    await server.start_server()


if __name__ == "__main__":
    asyncio.run(start_realtime_server())