"""Real-Time Collaboration API Endpoints
FastAPI endpoints for real-time collaboration features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import uuid
import asyncio
import logging

from ...services.realtime_collaboration_service import (
    RealtimeCollaborationService, 
    SessionType, 
    AnnotationType,
    ConflictType
)
from ...services.virtual_daw_service import VirtualDAWService, TrackType, PluginType
from ...services.realtime_websocket_server import RealtimeWebSocketServer
from ...backend.collaboration.realtime_integration import RealtimeCollaborationIntegration

logger = logging.getLogger(__name__)

# Initialize services
realtime_integration = RealtimeCollaborationIntegration()
security = HTTPBearer()

router = APIRouter(prefix="/api/realtime", tags=["Real-Time Collaboration"])


# Pydantic models for request/response
class SessionCreateRequest(BaseModel):
    session_type: str = Field(..., description="Type of collaboration session")
    project_name: str = Field(..., description="Name of the project")
    project_type: str = Field(default="general", description="Type of project")
    max_participants: int = Field(default=10, description="Maximum number of participants")
    collaboration_type: str = Field(default="real_time", description="Collaboration type")
    daw_template: Optional[Dict[str, Any]] = Field(None, description="DAW template configuration")
    session_config: Optional[Dict[str, Any]] = Field(None, description="Additional session configuration")


class SessionResponse(BaseModel):
    session_id: str
    project_id: str
    session_type: str
    webrtc_config: Dict[str, Any]
    collaboration_url: str
    daw_session_id: Optional[str] = None
    created_at: str
    status: str = "active"


class SessionJoinRequest(BaseModel):
    session_id: str = Field(..., description="Session to join")
    role: str = Field(default="participant", description="User role in session")


class InviteCollaboratorRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    invitee_email: str = Field(..., description="Email of user to invite")
    role: str = Field(default="collaborator", description="Role for invited user")
    permissions: Optional[List[str]] = Field(None, description="Specific permissions")
    message: Optional[str] = Field(None, description="Invitation message")


class AnnotationCreateRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    annotation_type: str = Field(..., description="Type of annotation")
    media_timestamp: float = Field(..., description="Timestamp in media")
    content: str = Field(..., description="Annotation content")
    position: Optional[Dict[str, float]] = Field(None, description="Position coordinates")


class VersionCommitRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    changes: Dict[str, Any] = Field(..., description="Changes to commit")
    commit_message: str = Field(..., description="Commit message")
    create_branch: bool = Field(default=False, description="Create new branch")
    branch_name: Optional[str] = Field(None, description="Branch name if creating")


class DAWTrackCreateRequest(BaseModel):
    session_id: str = Field(..., description="DAW session ID")
    name: str = Field(..., description="Track name")
    track_type: str = Field(..., description="Track type")
    volume: float = Field(default=1.0, description="Track volume")
    pan: float = Field(default=0.0, description="Track pan")
    color: Optional[str] = Field(None, description="Track color")


class DAWParameterUpdateRequest(BaseModel):
    session_id: str = Field(..., description="DAW session ID")
    track_id: str = Field(..., description="Track ID")
    parameter: str = Field(..., description="Parameter name")
    value: Union[float, bool, str] = Field(..., description="Parameter value")


class ConflictResolutionRequest(BaseModel):
    conflict_id: str = Field(..., description="Conflict ID")
    resolution_strategy: str = Field(..., description="Resolution strategy")
    resolution_data: Dict[str, Any] = Field(..., description="Resolution data")


# Session Management Endpoints
@router.post("/sessions", response_model=SessionResponse)
async def create_collaboration_session(
    request: SessionCreateRequest
):
    """Create new real-time collaboration session"""
    try:
        # Mock user for now - in production this would come from authentication
        current_user_id = "user_" + str(uuid.uuid4())[:8]
        
        project_data = {
            "name": request.project_name,
            "type": request.project_type,
            "max_participants": request.max_participants,
            "daw_template": request.daw_template
        }
        
        result = await realtime_integration.create_collaborative_project(
            current_user_id, project_data, request.collaboration_type
        )
        
        return SessionResponse(
            session_id=result["realtime_session_id"],
            project_id=result["project_id"],
            session_type=result["session_type"],
            webrtc_config=result["webrtc_config"],
            collaboration_url=result["collaboration_url"],
            daw_session_id=result.get("daw_session_id"),
            created_at=datetime.now().isoformat(),
            status="active"
        )
        
    except Exception as e:
        logger.error(f"Error creating collaboration session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session_details(session_id: str):
    """Get collaboration session details"""
    try:
        session_state = await realtime_integration.realtime_service.get_session_analytics(session_id)
        
        if not session_state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_state
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/join")
async def join_collaboration_session(
    session_id: str,
    request: SessionJoinRequest
):
    """Join existing collaboration session"""
    try:
        # Mock user for now
        current_user_id = "user_" + str(uuid.uuid4())[:8]
        
        # Mock websocket for API endpoint (real joining happens via WebSocket)
        from unittest.mock import Mock, AsyncMock
        mock_websocket = Mock()
        mock_websocket.send = AsyncMock()
        
        success = await realtime_integration.realtime_service.join_session(
            session_id, current_user_id, mock_websocket
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to join session")
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": current_user_id,
            "role": request.role,
            "websocket_url": f"/ws/realtime/{session_id}",
            "joined_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error joining session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/annotations")
async def create_media_annotation(request: AnnotationCreateRequest):
    """Create media annotation"""
    try:
        # Mock user for now
        current_user_id = "user_" + str(uuid.uuid4())[:8]
        
        annotation = await realtime_integration.realtime_service.create_media_annotation(
            request.session_id,
            current_user_id,
            AnnotationType(request.annotation_type),
            request.media_timestamp,
            request.content,
            request.position
        )
        
        return {
            "annotation_id": annotation.annotation_id,
            "session_id": annotation.session_id,
            "user_id": annotation.user_id,
            "annotation_type": annotation.annotation_type.value,
            "media_timestamp": annotation.media_timestamp,
            "content": annotation.content,
            "position": annotation.position,
            "created_at": annotation.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating annotation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/annotations/{session_id}")
async def get_session_annotations(session_id: str):
    """Get all annotations for session"""
    try:
        annotations = realtime_integration.realtime_service.media_annotations.get(session_id, [])
        
        return {
            "session_id": session_id,
            "annotations": [
                {
                    "annotation_id": ann.annotation_id,
                    "user_id": ann.user_id,
                    "annotation_type": ann.annotation_type.value,
                    "media_timestamp": ann.media_timestamp,
                    "content": ann.content,
                    "position": ann.position,
                    "created_at": ann.created_at.isoformat(),
                    "resolved": ann.resolved
                }
                for ann in annotations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting annotations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/versions/commit")
async def commit_version(request: VersionCommitRequest):
    """Commit new version"""
    try:
        # Mock user for now
        current_user_id = "user_" + str(uuid.uuid4())[:8]
        
        version = await realtime_integration.realtime_service.create_version_snapshot(
            request.session_id,
            current_user_id,
            request.changes,
            request.commit_message,
            request.create_branch,
            request.branch_name
        )
        
        return {
            "version_id": version.version_id,
            "session_id": version.session_id,
            "author_id": version.author_id,
            "parent_version": version.parent_version,
            "commit_message": version.commit_message,
            "is_branch": version.is_branch,
            "branch_name": version.branch_name,
            "timestamp": version.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error committing version: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daw/tracks")
async def create_daw_track(request: DAWTrackCreateRequest):
    """Create DAW track"""
    try:
        # Mock user for now
        current_user_id = "user_" + str(uuid.uuid4())[:8]
        
        track_config = {
            "name": request.name,
            "type": request.track_type,
            "volume": request.volume,
            "pan": request.pan,
            "color": request.color
        }
        
        track = await realtime_integration.daw_service.create_track(
            request.session_id, current_user_id, track_config
        )
        
        return {
            "track_id": track.track_id,
            "session_id": request.session_id,
            "name": track.name,
            "track_type": track.track_type.value,
            "volume": track.volume,
            "pan": track.pan,
            "color": track.color
        }
        
    except Exception as e:
        logger.error(f"Error creating DAW track: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/daw/tracks/parameters")
async def update_daw_parameter(request: DAWParameterUpdateRequest):
    """Update DAW track parameter"""
    try:
        # Mock user for now
        current_user_id = "user_" + str(uuid.uuid4())[:8]
        
        success = await realtime_integration.daw_service.update_track_parameter(
            request.session_id,
            current_user_id,
            request.track_id,
            request.parameter,
            request.value
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update parameter")
        
        return {
            "success": True,
            "session_id": request.session_id,
            "track_id": request.track_id,
            "parameter": request.parameter,
            "value": request.value,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating DAW parameter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{session_id}")
async def get_session_analytics(session_id: str):
    """Get real-time session analytics"""
    try:
        analytics = await realtime_integration.realtime_service.get_session_analytics(session_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for real-time collaboration service"""
    try:
        active_sessions = len(realtime_integration.realtime_service.active_sessions)
        daw_sessions = len(realtime_integration.daw_service.active_sessions)
        
        return {
            "status": "healthy",
            "active_realtime_sessions": active_sessions,
            "active_daw_sessions": daw_sessions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# WebSocket endpoint for real-time communication
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket.accept()
    
    try:
        # Handle WebSocket authentication and session joining
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        # Authenticate user (simplified)
        user_id = auth_data.get("user_id")
        if not user_id:
            await websocket.send_text(json.dumps({"error": "Authentication required"}))
            return
        
        # Join session
        success = await realtime_integration.realtime_service.join_session(
            session_id, user_id, websocket
        )
        
        if not success:
            await websocket.send_text(json.dumps({"error": "Failed to join session"}))
            return
        
        # Handle messages
        try:
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                await realtime_integration.realtime_service.handle_realtime_message(
                    session_id, user_id, data
                )
        except WebSocketDisconnect:
            await realtime_integration.realtime_service.leave_session(session_id, user_id)
            
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


# Initialize integration on startup
@router.on_event("startup")
async def startup_event():
    """Initialize real-time collaboration integration"""
    try:
        await realtime_integration.initialize()
        logger.info("Real-time collaboration API initialized")
    except Exception as e:
        logger.error(f"Failed to initialize real-time collaboration API: {str(e)}")


def get_router():
    """Get router for inclusion in main app"""
    return router