"""Real-time Collaboration Engine
Main orchestrator for all real-time collaboration services.

Integrates:
- WebRTC audio/video collaboration
- Project versioning and branching
- Collaborative media annotations
- Translation chat service
- Virtual DAW session sharing  
- Conflict resolution system

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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from pydantic import BaseModel, Field

from .webrtc_service import WebRTCCollaborationService
from .project_versioning import ProjectVersioningSystem
from .media_annotations import CollaborativeAnnotationEngine
from .translation_chat import TranslationChatService
from .daw_sharing import VirtualDAWSessionManager
from .conflict_resolution import CollaborationConflictResolver

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of collaboration services"""
    WEBRTC = "webrtc"
    VERSIONING = "versioning"
    ANNOTATIONS = "annotations"
    CHAT = "chat"
    DAW_SHARING = "daw_sharing"
    CONFLICT_RESOLUTION = "conflict_resolution"


class SessionType(Enum):
    """Types of collaboration sessions"""
    GENERAL = "general"
    AUDIO_VIDEO = "audio_video"
    TEXT_EDITING = "text_editing"
    MEDIA_ANNOTATION = "media_annotation"
    MUSIC_PRODUCTION = "music_production"
    CHAT_ONLY = "chat_only"


@dataclass
class CollaborationMetrics:
    """Real-time collaboration metrics"""
    active_sessions: int = 0
    total_participants: int = 0
    messages_per_second: float = 0.0
    conflicts_resolved: int = 0
    average_latency_ms: float = 0.0
    bandwidth_usage_mbps: float = 0.0
    uptime_seconds: int = 0


@dataclass
class UnifiedSession:
    """Unified collaboration session"""
    session_id: str
    project_id: str
    title: str
    description: str
    session_type: SessionType
    creator_id: str
    participants: Set[str] = field(default_factory=set)
    active_services: Set[ServiceType] = field(default_factory=set)
    service_sessions: Dict[ServiceType, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RealtimeCollaborationEngine:
    """
    Main real-time collaboration engine orchestrating all services
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        
        # Initialize all collaboration services
        self.webrtc_service = WebRTCCollaborationService(redis_client)
        self.versioning_system = ProjectVersioningSystem()
        self.annotation_engine = CollaborativeAnnotationEngine()
        self.chat_service = TranslationChatService()
        self.daw_manager = VirtualDAWSessionManager()
        self.conflict_resolver = CollaborationConflictResolver()
        
        # Session management
        self.unified_sessions: Dict[str, UnifiedSession] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
        self.service_routing: Dict[str, ServiceType] = {}
        
        # Metrics and monitoring
        self.metrics = CollaborationMetrics()
        self.start_time = datetime.utcnow()
        
        # Initialize FastAPI app
        self.app = self._create_app()
        
        self._setup_message_handlers()
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="Real-time Collaboration Engine",
            description="Professional real-time collaboration platform",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add routes
        self._setup_routes(app)
        
        return app
    
    def _setup_routes(self, app: FastAPI):
        """Setup API routes"""
        
        @app.websocket("/ws/collaboration/{user_id}")
        async def collaboration_websocket(websocket: WebSocket, user_id: str):
            """Main collaboration WebSocket endpoint"""
            await self.handle_websocket_connection(websocket, user_id)
        
        @app.websocket("/ws/webrtc/{user_id}")
        async def webrtc_websocket(websocket: WebSocket, user_id: str):
            """WebRTC-specific WebSocket endpoint"""
            await self.webrtc_service.handle_websocket_connection(websocket, user_id)
        
        @app.websocket("/ws/annotations/{user_id}")
        async def annotations_websocket(websocket: WebSocket, user_id: str):
            """Annotations-specific WebSocket endpoint"""
            await self.annotation_engine.handle_websocket_connection(websocket, user_id)
        
        @app.websocket("/ws/chat/{user_id}")
        async def chat_websocket(websocket: WebSocket, user_id: str):
            """Chat-specific WebSocket endpoint"""
            await self.chat_service.handle_websocket_connection(websocket, user_id)
        
        @app.websocket("/ws/daw/{user_id}")
        async def daw_websocket(websocket: WebSocket, user_id: str):
            """DAW-specific WebSocket endpoint"""
            await self.daw_manager.handle_websocket_connection(websocket, user_id)
        
        @app.websocket("/ws/conflicts/{user_id}")
        async def conflicts_websocket(websocket: WebSocket, user_id: str):
            """Conflict resolution WebSocket endpoint"""
            await self.conflict_resolver.handle_websocket_connection(websocket, user_id)
        
        @app.post("/api/sessions")
        async def create_session(session_request: dict):
            """Create new collaboration session"""
            return await self.create_unified_session(
                project_id=session_request.get("project_id"),
                title=session_request.get("title"),
                description=session_request.get("description", ""),
                session_type=session_request.get("session_type", "general"),
                creator_id=session_request.get("creator_id"),
                services=session_request.get("services", [])
            )
        
        @app.get("/api/sessions/{session_id}")
        async def get_session(session_id: str):
            """Get session details"""
            return await self.get_session_details(session_id)
        
        @app.delete("/api/sessions/{session_id}")
        async def delete_session(session_id: str):
            """Delete session"""
            return await self.end_session(session_id)
        
        @app.get("/api/sessions")
        async def list_sessions():
            """List all active sessions"""
            return await self.list_active_sessions()
        
        @app.get("/api/metrics")
        async def get_metrics():
            """Get collaboration metrics"""
            return await self.get_collaboration_metrics()
        
        @app.get("/api/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "active_sessions": len(self.unified_sessions)
            }
    
    def _setup_message_handlers(self):
        """Setup unified message handlers"""
        self.message_handlers = {
            "create_session": self._handle_create_session,
            "join_session": self._handle_join_session,
            "leave_session": self._handle_leave_session,
            "enable_service": self._handle_enable_service,
            "disable_service": self._handle_disable_service,
            "route_message": self._handle_route_message,
            "get_session_status": self._handle_get_session_status,
            "sync_all": self._handle_sync_all
        }
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: str):
        """Handle main collaboration WebSocket connection"""
        try:
            await websocket.accept()
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"Main collaboration connection established for user {user_id}")
            
            # Send connection confirmation
            await self._send_to_user(user_id, {
                "type": "connection_established",
                "user_id": user_id,
                "available_services": [service.value for service in ServiceType],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_unified_message(user_id, message)
                    
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
    
    async def _handle_unified_message(self, user_id: str, message: Dict[str, Any]):
        """Handle unified collaboration messages"""
        message_type = message.get("type")
        handler = self.message_handlers.get(message_type)
        
        if handler:
            await handler(user_id, message)
        else:
            await self._send_error(user_id, f"Unknown message type: {message_type}")
    
    async def create_unified_session(self, project_id: str, title: str, description: str,
                                   session_type: str, creator_id: str,
                                   services: List[str] = None) -> Dict[str, Any]:
        """Create unified collaboration session"""
        try:
            session_id = f"unified_{uuid.uuid4().hex[:12]}"
            
            if services is None:
                services = ["chat", "conflict_resolution"]  # Default services
            
            # Create unified session
            session = UnifiedSession(
                session_id=session_id,
                project_id=project_id,
                title=title,
                description=description,
                session_type=SessionType(session_type),
                creator_id=creator_id
            )
            
            session.participants.add(creator_id)
            
            # Initialize requested services
            for service_name in services:
                try:
                    service_type = ServiceType(service_name)
                    service_session_id = await self._initialize_service(
                        service_type, session_id, project_id, creator_id, title, description
                    )
                    
                    if service_session_id:
                        session.active_services.add(service_type)
                        session.service_sessions[service_type] = service_session_id
                        
                except ValueError:
                    logger.warning(f"Unknown service type: {service_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize service {service_name}: {e}")
            
            # Initialize project versioning
            versioning_result = await self.versioning_system.initialize_project(
                project_id, creator_id, title
            )
            
            # Initialize conflict resolution session
            conflict_result = await self.conflict_resolver.create_collaboration_session(
                session_id, project_id, [creator_id]
            )
            
            self.unified_sessions[session_id] = session
            
            # Update metrics
            self.metrics.active_sessions = len(self.unified_sessions)
            
            logger.info(f"Unified session {session_id} created with services: {services}")
            
            return {
                "status": "success",
                "session_id": session_id,
                "project_id": project_id,
                "session_type": session_type,
                "active_services": [s.value for s in session.active_services],
                "service_sessions": {s.value: sid for s, sid in session.service_sessions.items()},
                "versioning_initialized": versioning_result.get("status") == "success",
                "message": "Unified collaboration session created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating unified session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _initialize_service(self, service_type: ServiceType, session_id: str,
                                project_id: str, creator_id: str, title: str,
                                description: str) -> Optional[str]:
        """Initialize individual service"""
        try:
            if service_type == ServiceType.WEBRTC:
                # WebRTC sessions are created on-demand
                return f"webrtc_{session_id}"
            
            elif service_type == ServiceType.ANNOTATIONS:
                result = await self.annotation_engine.create_annotation_session(
                    media_id=project_id,
                    media_type="video",  # Default
                    media_url="",
                    title=title,
                    creator_id=creator_id
                )
                return result.get("session_id") if result.get("status") == "success" else None
            
            elif service_type == ServiceType.CHAT:
                result = await self.chat_service.create_chat_session(
                    project_id=project_id,
                    title=title,
                    description=description,
                    creator_id=creator_id
                )
                return result.get("session_id") if result.get("status") == "success" else None
            
            elif service_type == ServiceType.DAW_SHARING:
                result = await self.daw_manager.create_daw_session(
                    project_id=project_id,
                    project_name=title,
                    host_id=creator_id,
                    daw_type="reaper"  # Default
                )
                return result.get("session_id") if result.get("status") == "success" else None
            
            elif service_type == ServiceType.CONFLICT_RESOLUTION:
                result = await self.conflict_resolver.create_collaboration_session(
                    session_id, project_id, [creator_id]
                )
                return session_id if result.get("status") == "success" else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error initializing service {service_type.value}: {e}")
            return None
    
    async def _handle_create_session(self, user_id: str, message: Dict[str, Any]):
        """Handle create session message"""
        result = await self.create_unified_session(
            project_id=message.get("project_id"),
            title=message.get("title"),
            description=message.get("description", ""),
            session_type=message.get("session_type", "general"),
            creator_id=user_id,
            services=message.get("services", [])
        )
        
        await self._send_to_user(user_id, {
            "type": "session_created",
            "result": result
        })
    
    async def _handle_join_session(self, user_id: str, message: Dict[str, Any]):
        """Handle join session message"""
        try:
            session_id = message.get("session_id")
            username = message.get("username", f"User_{user_id}")
            
            session = self.unified_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Add participant to unified session
            session.participants.add(user_id)
            session.last_activity = datetime.utcnow()
            
            # Join active services
            join_results = {}
            for service_type in session.active_services:
                try:
                    service_session_id = session.service_sessions.get(service_type)
                    if service_session_id:
                        result = await self._join_service_session(
                            service_type, service_session_id, user_id, username
                        )
                        join_results[service_type.value] = result
                except Exception as e:
                    logger.error(f"Error joining service {service_type.value}: {e}")
                    join_results[service_type.value] = {"status": "error", "message": str(e)}
            
            # Update metrics
            self.metrics.total_participants = sum(len(s.participants) for s in self.unified_sessions.values())
            
            # Send confirmation
            await self._send_to_user(user_id, {
                "type": "session_joined",
                "session_id": session_id,
                "active_services": [s.value for s in session.active_services],
                "service_results": join_results,
                "participants": list(session.participants)
            })
            
            # Notify other participants
            await self._broadcast_to_session(session_id, {
                "type": "participant_joined",
                "user_id": user_id,
                "username": username,
                "participant_count": len(session.participants)
            }, exclude_user=user_id)
            
            logger.info(f"User {user_id} joined unified session {session_id}")
            
        except Exception as e:
            logger.error(f"Error joining session: {e}")
            await self._send_error(user_id, str(e))
    
    async def _join_service_session(self, service_type: ServiceType, service_session_id: str,
                                  user_id: str, username: str) -> Dict[str, Any]:
        """Join specific service session"""
        try:
            if service_type == ServiceType.WEBRTC:
                # WebRTC joining is handled separately
                return {"status": "success", "message": "WebRTC available"}
            
            elif service_type == ServiceType.ANNOTATIONS:
                # Annotations joining is handled via WebSocket
                return {"status": "success", "message": "Annotations available"}
            
            elif service_type == ServiceType.CHAT:
                # Chat joining is handled via WebSocket
                return {"status": "success", "message": "Chat available"}
            
            elif service_type == ServiceType.DAW_SHARING:
                # DAW joining is handled via WebSocket
                return {"status": "success", "message": "DAW sharing available"}
            
            elif service_type == ServiceType.CONFLICT_RESOLUTION:
                # Conflict resolution is automatically available
                return {"status": "success", "message": "Conflict resolution available"}
            
            return {"status": "success", "message": "Service available"}
            
        except Exception as e:
            logger.error(f"Error joining service session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_leave_session(self, user_id: str, message: Dict[str, Any]):
        """Handle leave session message"""
        try:
            session_id = message.get("session_id")
            session = self.unified_sessions.get(session_id)
            
            if session and user_id in session.participants:
                session.participants.remove(user_id)
                session.last_activity = datetime.utcnow()
                
                # Update metrics
                self.metrics.total_participants = sum(len(s.participants) for s in self.unified_sessions.values())
                
                # Notify other participants
                await self._broadcast_to_session(session_id, {
                    "type": "participant_left",
                    "user_id": user_id,
                    "participant_count": len(session.participants)
                }, exclude_user=user_id)
                
                # End session if no participants left
                if len(session.participants) == 0:
                    await self.end_session(session_id)
                
                logger.info(f"User {user_id} left unified session {session_id}")
            
        except Exception as e:
            logger.error(f"Error leaving session: {e}")
    
    async def _handle_enable_service(self, user_id: str, message: Dict[str, Any]):
        """Handle enable service message"""
        try:
            session_id = message.get("session_id")
            service_name = message.get("service")
            
            session = self.unified_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            if user_id != session.creator_id:
                await self._send_error(user_id, "Only session creator can enable services")
                return
            
            service_type = ServiceType(service_name)
            
            if service_type in session.active_services:
                await self._send_error(user_id, "Service already enabled")
                return
            
            # Initialize service
            service_session_id = await self._initialize_service(
                service_type, session_id, session.project_id,
                session.creator_id, session.title, session.description
            )
            
            if service_session_id:
                session.active_services.add(service_type)
                session.service_sessions[service_type] = service_session_id
                
                # Notify all participants
                await self._broadcast_to_session(session_id, {
                    "type": "service_enabled",
                    "service": service_name,
                    "service_session_id": service_session_id
                })
                
                logger.info(f"Service {service_name} enabled in session {session_id}")
            else:
                await self._send_error(user_id, f"Failed to initialize service {service_name}")
            
        except ValueError:
            await self._send_error(user_id, f"Unknown service: {service_name}")
        except Exception as e:
            logger.error(f"Error enabling service: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_disable_service(self, user_id: str, message: Dict[str, Any]):
        """Handle disable service message"""
        try:
            session_id = message.get("session_id")
            service_name = message.get("service")
            
            session = self.unified_sessions.get(session_id)
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            if user_id != session.creator_id:
                await self._send_error(user_id, "Only session creator can disable services")
                return
            
            service_type = ServiceType(service_name)
            
            if service_type not in session.active_services:
                await self._send_error(user_id, "Service not enabled")
                return
            
            # Remove service
            session.active_services.remove(service_type)
            if service_type in session.service_sessions:
                del session.service_sessions[service_type]
            
            # Notify all participants
            await self._broadcast_to_session(session_id, {
                "type": "service_disabled",
                "service": service_name
            })
            
            logger.info(f"Service {service_name} disabled in session {session_id}")
            
        except ValueError:
            await self._send_error(user_id, f"Unknown service: {service_name}")
        except Exception as e:
            logger.error(f"Error disabling service: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_route_message(self, user_id: str, message: Dict[str, Any]):
        """Handle message routing to specific service"""
        try:
            service_name = message.get("service")
            service_message = message.get("message")
            
            if not service_name or not service_message:
                await self._send_error(user_id, "Service and message required")
                return
            
            service_type = ServiceType(service_name)
            
            # Route to appropriate service
            if service_type == ServiceType.WEBRTC:
                await self.webrtc_service._handle_signaling_message(user_id, service_message)
            elif service_type == ServiceType.ANNOTATIONS:
                await self.annotation_engine._handle_annotation_message(user_id, service_message)
            elif service_type == ServiceType.CHAT:
                await self.chat_service._handle_chat_message(user_id, service_message)
            elif service_type == ServiceType.DAW_SHARING:
                await self.daw_manager._handle_daw_message(user_id, service_message)
            elif service_type == ServiceType.CONFLICT_RESOLUTION:
                await self.conflict_resolver._handle_message(user_id, service_message)
            else:
                await self._send_error(user_id, f"Unknown service: {service_name}")
            
        except ValueError:
            await self._send_error(user_id, f"Unknown service: {service_name}")
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_get_session_status(self, user_id: str, message: Dict[str, Any]):
        """Handle get session status message"""
        try:
            session_id = message.get("session_id")
            session = self.unified_sessions.get(session_id)
            
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            status = {
                "session_id": session_id,
                "project_id": session.project_id,
                "title": session.title,
                "session_type": session.session_type.value,
                "creator_id": session.creator_id,
                "participants": list(session.participants),
                "participant_count": len(session.participants),
                "active_services": [s.value for s in session.active_services],
                "service_sessions": {s.value: sid for s, sid in session.service_sessions.items()},
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
            
            await self._send_to_user(user_id, {
                "type": "session_status",
                "status": status
            })
            
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            await self._send_error(user_id, str(e))
    
    async def _handle_sync_all(self, user_id: str, message: Dict[str, Any]):
        """Handle sync all services message"""
        try:
            session_id = message.get("session_id")
            session = self.unified_sessions.get(session_id)
            
            if not session:
                await self._send_error(user_id, "Session not found")
                return
            
            # Sync all active services
            sync_results = {}
            
            for service_type in session.active_services:
                try:
                    if service_type == ServiceType.WEBRTC:
                        # Get WebRTC session details
                        webrtc_sessions = await self.webrtc_service.get_active_sessions()
                        sync_results["webrtc"] = {"sessions": webrtc_sessions}
                    
                    elif service_type == ServiceType.ANNOTATIONS:
                        service_session_id = session.service_sessions.get(service_type)
                        if service_session_id:
                            annotations = await self.annotation_engine.get_session_annotations(service_session_id)
                            sync_results["annotations"] = {"annotations": annotations}
                    
                    elif service_type == ServiceType.VERSIONING:
                        history = await self.versioning_system.get_project_history(session.project_id)
                        sync_results["versioning"] = history
                    
                    elif service_type == ServiceType.DAW_SHARING:
                        service_session_id = session.service_sessions.get(service_type)
                        if service_session_id:
                            daw_info = await self.daw_manager.get_session_info(service_session_id)
                            sync_results["daw_sharing"] = daw_info
                    
                except Exception as e:
                    logger.error(f"Error syncing service {service_type.value}: {e}")
                    sync_results[service_type.value] = {"error": str(e)}
            
            await self._send_to_user(user_id, {
                "type": "sync_complete",
                "session_id": session_id,
                "sync_results": sync_results,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error syncing all services: {e}")
            await self._send_error(user_id, str(e))
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End unified collaboration session"""
        try:
            session = self.unified_sessions.get(session_id)
            if not session:
                return {"status": "error", "message": "Session not found"}
            
            # Notify all participants
            await self._broadcast_to_session(session_id, {
                "type": "session_ended",
                "session_id": session_id,
                "ended_at": datetime.utcnow().isoformat()
            })
            
            # End all service sessions
            for service_type, service_session_id in session.service_sessions.items():
                try:
                    if service_type == ServiceType.WEBRTC:
                        # WebRTC sessions end automatically when participants leave
                        pass
                    # Other services would be cleaned up here
                except Exception as e:
                    logger.error(f"Error ending service session {service_type.value}: {e}")
            
            # Remove from active sessions
            del self.unified_sessions[session_id]
            
            # Update metrics
            self.metrics.active_sessions = len(self.unified_sessions)
            self.metrics.total_participants = sum(len(s.participants) for s in self.unified_sessions.values())
            
            logger.info(f"Unified session {session_id} ended")
            
            return {"status": "success", "message": "Session ended"}
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session information"""
        session = self.unified_sessions.get(session_id)
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        return {
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "project_id": session.project_id,
                "title": session.title,
                "description": session.description,
                "session_type": session.session_type.value,
                "creator_id": session.creator_id,
                "participants": list(session.participants),
                "participant_count": len(session.participants),
                "active_services": [s.value for s in session.active_services],
                "service_sessions": {s.value: sid for s, sid in session.service_sessions.items()},
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "metadata": session.metadata
            }
        }
    
    async def list_active_sessions(self) -> Dict[str, Any]:
        """List all active collaboration sessions"""
        sessions = []
        
        for session in self.unified_sessions.values():
            sessions.append({
                "session_id": session.session_id,
                "project_id": session.project_id,
                "title": session.title,
                "session_type": session.session_type.value,
                "creator_id": session.creator_id,
                "participant_count": len(session.participants),
                "active_services": [s.value for s in session.active_services],
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            })
        
        return {
            "status": "success",
            "sessions": sessions,
            "total_count": len(sessions)
        }
    
    async def get_collaboration_metrics(self) -> Dict[str, Any]:
        """Get real-time collaboration metrics"""
        # Update uptime
        self.metrics.uptime_seconds = int((datetime.utcnow() - self.start_time).total_seconds())
        
        # Calculate metrics
        total_operations = 0
        total_conflicts = 0
        
        for session in self.unified_sessions.values():
            if ServiceType.CONFLICT_RESOLUTION in session.active_services:
                conflict_session = self.conflict_resolver.sessions.get(session.session_id)
                if conflict_session:
                    total_operations += len(conflict_session.operation_log)
                    total_conflicts += len(conflict_session.conflict_history)
        
        self.metrics.conflicts_resolved = total_conflicts
        
        return {
            "status": "success",
            "metrics": {
                "active_sessions": self.metrics.active_sessions,
                "total_participants": self.metrics.total_participants,
                "messages_per_second": self.metrics.messages_per_second,
                "conflicts_resolved": self.metrics.conflicts_resolved,
                "average_latency_ms": self.metrics.average_latency_ms,
                "bandwidth_usage_mbps": self.metrics.bandwidth_usage_mbps,
                "uptime_seconds": self.metrics.uptime_seconds,
                "total_operations": total_operations
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _broadcast_to_session(self, session_id: str, message: Dict[str, Any],
                                   exclude_user: Optional[str] = None):
        """Broadcast message to all users in session"""
        session = self.unified_sessions.get(session_id)
        if not session:
            return
        
        for user_id in session.participants:
            if user_id != exclude_user:
                await self._send_to_user(user_id, message)
    
    async def _send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to specific user"""
        websocket = self.websocket_connections.get(user_id)
        if websocket:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")
                await self._cleanup_user_connection(user_id)
    
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
            for session_id, session in list(self.unified_sessions.items()):
                if user_id in session.participants:
                    await self._handle_leave_session(user_id, {"session_id": session_id})
            
        except Exception as e:
            logger.error(f"Error cleaning up user connection: {e}")


# Export the engine
__all__ = ['RealtimeCollaborationEngine', 'ServiceType', 'SessionType',
           'CollaborationMetrics', 'UnifiedSession']