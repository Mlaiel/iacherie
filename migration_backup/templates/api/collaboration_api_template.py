"""Collaboration API Template for IA Chéries Platform

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
import uuid
import asyncio
import logging
import json
from dataclasses import dataclass
import redis
from collections import defaultdict

logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()

class CollaborationType(str, Enum):
    """Types of collaboration"""
    CONTENT_CREATION = "content_creation"
    LIVE_STREAMING = "live_streaming"
    JOINT_PROJECT = "joint_project"
    MENTORSHIP = "mentorship"
    CROSS_PROMOTION = "cross_promotion"
    REVENUE_SHARING = "revenue_sharing"
    GUEST_APPEARANCE = "guest_appearance"
    SKILL_EXCHANGE = "skill_exchange"

class CollaborationStatus(str, Enum):
    """Collaboration status"""
    PROPOSED = "proposed"
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class InvitationStatus(str, Enum):
    """Invitation status"""
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"

class MessageType(str, Enum):
    """Message types in collaboration"""
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LINK = "link"
    SYSTEM = "system"

class Collaboration(Base):
    """Collaboration projects between creators"""
    __tablename__ = "collaborations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    collaboration_type = Column(SQLEnum(CollaborationType), nullable=False)
    status = Column(SQLEnum(CollaborationStatus), default=CollaborationStatus.PROPOSED)
    
    # Creator relationships
    initiator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Project details
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    deadline = Column(DateTime)
    
    # Financial terms
    revenue_split = Column(JSON)  # {"creator1": 60, "creator2": 40}
    budget = Column(Float)
    payment_terms = Column(Text)
    
    # Project requirements
    skills_required = Column(JSON)  # ["video_editing", "graphic_design"]
    tools_required = Column(JSON)  # ["Adobe Premiere", "Photoshop"]
    deliverables = Column(JSON)  # [{"name": "Video", "format": "MP4", "duration": "10min"}]
    
    # Metadata
    tags = Column(JSON)
    is_public = Column(Boolean, default=False)
    max_collaborators = Column(Integer, default=2)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participants = relationship("CollaborationParticipant", back_populates="collaboration")
    messages = relationship("CollaborationMessage", back_populates="collaboration")
    tasks = relationship("CollaborationTask", back_populates="collaboration")

class CollaborationParticipant(Base):
    """Participants in a collaboration"""
    __tablename__ = "collaboration_participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String, ForeignKey("collaborations.id"), nullable=False)
    creator_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Participation details
    role = Column(String(100))  # "Lead Creator", "Video Editor", "Designer"
    permissions = Column(JSON)  # ["edit", "invite", "manage_tasks"]
    revenue_percentage = Column(Float, default=0.0)
    
    # Status
    invitation_status = Column(SQLEnum(InvitationStatus), default=InvitationStatus.SENT)
    joined_at = Column(DateTime)
    
    # Contribution tracking
    contribution_hours = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collaboration = relationship("Collaboration", back_populates="participants")

class CollaborationMessage(Base):
    """Messages in collaboration workspace"""
    __tablename__ = "collaboration_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String, ForeignKey("collaborations.id"), nullable=False)
    sender_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Message content
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    content = Column(Text)
    file_url = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    
    # Message metadata
    reply_to_id = Column(String, ForeignKey("collaboration_messages.id"))
    is_pinned = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # Read status tracking
    read_by = Column(JSON)  # {"creator1": "2025-01-18T10:30:00Z"}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collaboration = relationship("Collaboration", back_populates="messages")

class CollaborationTask(Base):
    """Tasks within a collaboration"""
    __tablename__ = "collaboration_tasks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String, ForeignKey("collaborations.id"), nullable=False)
    
    # Task details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Assignment
    assigned_to_id = Column(String, ForeignKey("creators.id"))
    created_by_id = Column(String, ForeignKey("creators.id"), nullable=False)
    
    # Status and timing
    status = Column(String(20), default="pending")  # pending, in_progress, review, completed
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Task metadata
    tags = Column(JSON)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    dependencies = Column(JSON)  # Task IDs that must be completed first
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    collaboration = relationship("Collaboration", back_populates="tasks")

class LiveCollaborationSession(Base):
    """Live collaboration sessions (real-time editing, streaming)"""
    __tablename__ = "live_collaboration_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String, ForeignKey("collaborations.id"), nullable=False)
    
    # Session details
    session_type = Column(String(50))  # "video_call", "screen_share", "live_edit"
    title = Column(String(200))
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Participants
    host_id = Column(String, ForeignKey("creators.id"), nullable=False)
    participants = Column(JSON)  # List of participant IDs
    
    # Session data
    recording_url = Column(String(500))
    session_notes = Column(Text)
    shared_files = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class CollaborationCreate(BaseModel):
    """Create collaboration request"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    collaboration_type: CollaborationType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    revenue_split: Optional[Dict[str, float]] = None
    budget: Optional[float] = Field(None, ge=0)
    skills_required: List[str] = Field(default=[])
    tools_required: List[str] = Field(default=[])
    deliverables: List[Dict[str, Any]] = Field(default=[])
    tags: List[str] = Field(default=[])
    is_public: bool = False
    max_collaborators: int = Field(default=2, ge=2, le=10)

class CollaborationInvite(BaseModel):
    """Invite to collaboration"""
    creator_id: str
    role: Optional[str] = None
    revenue_percentage: Optional[float] = Field(None, ge=0, le=100)
    message: Optional[str] = None

class CollaborationResponse(BaseModel):
    """Collaboration response"""
    id: str
    title: str
    description: Optional[str]
    collaboration_type: CollaborationType
    status: CollaborationStatus
    initiator_id: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    deadline: Optional[datetime]
    revenue_split: Optional[Dict[str, float]]
    budget: Optional[float]
    skills_required: List[str]
    tools_required: List[str]
    deliverables: List[Dict[str, Any]]
    tags: List[str]
    is_public: bool
    max_collaborators: int
    participant_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    """Create message request"""
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.TEXT
    reply_to_id: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None

class MessageResponse(BaseModel):
    """Message response"""
    id: str
    collaboration_id: str
    sender_id: str
    message_type: MessageType
    content: str
    file_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    reply_to_id: Optional[str]
    is_pinned: bool
    is_edited: bool
    read_by: Dict[str, str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    """Create task request"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    assigned_to_id: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    tags: List[str] = Field(default=[])
    dependencies: List[str] = Field(default=[])

class TaskResponse(BaseModel):
    """Task response"""
    id: str
    collaboration_id: str
    title: str
    description: Optional[str]
    priority: str
    assigned_to_id: Optional[str]
    created_by_id: str
    status: str
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    tags: List[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CollaborationWorkspace(BaseModel):
    """Collaboration workspace view"""
    collaboration: CollaborationResponse
    participants: List[Dict[str, Any]]
    recent_messages: List[MessageResponse]
    active_tasks: List[TaskResponse]
    upcoming_deadlines: List[Dict[str, Any]]
    project_progress: Dict[str, Any]

class CollaborationService:
    """Service for handling collaboration operations"""
    
    def __init__(self, db_session: AsyncSession, redis_client: Optional[redis.Redis] = None):
        self.db = db_session
        self.redis = redis_client
        
        # WebSocket connections for real-time collaboration
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
        logger.info("Collaboration service initialized")
    
    async def create_collaboration(
        self,
        creator_id: str,
        collaboration_data: CollaborationCreate
    ) -> CollaborationResponse:
        """Create a new collaboration"""
        
        # Create collaboration
        collaboration = Collaboration(
            title=collaboration_data.title,
            description=collaboration_data.description,
            collaboration_type=collaboration_data.collaboration_type,
            initiator_id=creator_id,
            start_date=collaboration_data.start_date,
            end_date=collaboration_data.end_date,
            deadline=collaboration_data.deadline,
            revenue_split=collaboration_data.revenue_split,
            budget=collaboration_data.budget,
            skills_required=collaboration_data.skills_required,
            tools_required=collaboration_data.tools_required,
            deliverables=collaboration_data.deliverables,
            tags=collaboration_data.tags,
            is_public=collaboration_data.is_public,
            max_collaborators=collaboration_data.max_collaborators
        )
        
        self.db.add(collaboration)
        await self.db.commit()
        await self.db.refresh(collaboration)
        
        # Add initiator as participant
        participant = CollaborationParticipant(
            collaboration_id=collaboration.id,
            creator_id=creator_id,
            role="Project Lead",
            permissions=["edit", "invite", "manage_tasks", "manage_finances"],
            invitation_status=InvitationStatus.ACCEPTED,
            joined_at=datetime.utcnow()
        )
        
        self.db.add(participant)
        await self.db.commit()
        
        return CollaborationResponse(
            **collaboration.__dict__,
            participant_count=1
        )
    
    async def invite_collaborator(
        self,
        collaboration_id: str,
        inviter_id: str,
        invite_data: CollaborationInvite
    ) -> Dict[str, str]:
        """Invite a creator to collaborate"""
        
        # Check if collaboration exists and inviter has permission
        collaboration = await self.db.get(Collaboration, collaboration_id)
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        # Check if inviter is a participant with invite permissions
        inviter_participant = await self._get_participant(collaboration_id, inviter_id)
        if not inviter_participant or "invite" not in inviter_participant.permissions:
            raise HTTPException(status_code=403, detail="No permission to invite")
        
        # Check if creator is already a participant
        existing_participant = await self._get_participant(collaboration_id, invite_data.creator_id)
        if existing_participant:
            raise HTTPException(status_code=400, detail="Creator is already a participant")
        
        # Check max collaborators limit
        current_count = await self._get_participant_count(collaboration_id)
        if current_count >= collaboration.max_collaborators:
            raise HTTPException(status_code=400, detail="Maximum collaborators reached")
        
        # Create participant invitation
        participant = CollaborationParticipant(
            collaboration_id=collaboration_id,
            creator_id=invite_data.creator_id,
            role=invite_data.role or "Collaborator",
            revenue_percentage=invite_data.revenue_percentage or 0.0,
            invitation_status=InvitationStatus.SENT
        )
        
        self.db.add(participant)
        await self.db.commit()
        
        # Send notification (would integrate with notification service)
        await self._send_collaboration_notification(
            invite_data.creator_id,
            "collaboration_invite",
            {
                "collaboration_id": collaboration_id,
                "collaboration_title": collaboration.title,
                "inviter_id": inviter_id,
                "message": invite_data.message
            }
        )
        
        return {"status": "invited", "participant_id": participant.id}
    
    async def respond_to_invitation(
        self,
        collaboration_id: str,
        creator_id: str,
        accept: bool
    ) -> Dict[str, str]:
        """Respond to collaboration invitation"""
        
        participant = await self._get_participant(collaboration_id, creator_id)
        if not participant:
            raise HTTPException(status_code=404, detail="Invitation not found")
        
        if participant.invitation_status != InvitationStatus.SENT:
            raise HTTPException(status_code=400, detail="Invitation already responded to")
        
        if accept:
            participant.invitation_status = InvitationStatus.ACCEPTED
            participant.joined_at = datetime.utcnow()
            status = "accepted"
        else:
            participant.invitation_status = InvitationStatus.DECLINED
            status = "declined"
        
        await self.db.commit()
        
        # Notify other participants
        await self._notify_participants(
            collaboration_id,
            f"invitation_{status}",
            {"creator_id": creator_id}
        )
        
        return {"status": status}
    
    async def send_message(
        self,
        collaboration_id: str,
        sender_id: str,
        message_data: MessageCreate
    ) -> MessageResponse:
        """Send message in collaboration"""
        
        # Verify sender is participant
        participant = await self._get_participant(collaboration_id, sender_id)
        if not participant or participant.invitation_status != InvitationStatus.ACCEPTED:
            raise HTTPException(status_code=403, detail="Not a collaboration participant")
        
        # Create message
        message = CollaborationMessage(
            collaboration_id=collaboration_id,
            sender_id=sender_id,
            message_type=message_data.message_type,
            content=message_data.content,
            file_url=message_data.file_url,
            file_name=message_data.file_name,
            reply_to_id=message_data.reply_to_id,
            read_by={sender_id: datetime.utcnow().isoformat()}
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        # Broadcast to active WebSocket connections
        await self._broadcast_message(collaboration_id, message)
        
        # Send push notifications to offline participants
        await self._notify_offline_participants(collaboration_id, message)
        
        return MessageResponse(**message.__dict__)
    
    async def create_task(
        self,
        collaboration_id: str,
        creator_id: str,
        task_data: TaskCreate
    ) -> TaskResponse:
        """Create task in collaboration"""
        
        # Verify creator is participant with task management permission
        participant = await self._get_participant(collaboration_id, creator_id)
        if not participant or "manage_tasks" not in participant.permissions:
            raise HTTPException(status_code=403, detail="No permission to create tasks")
        
        # Create task
        task = CollaborationTask(
            collaboration_id=collaboration_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            assigned_to_id=task_data.assigned_to_id,
            created_by_id=creator_id,
            due_date=task_data.due_date,
            estimated_hours=task_data.estimated_hours,
            tags=task_data.tags,
            dependencies=task_data.dependencies
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        # Notify assigned user
        if task_data.assigned_to_id:
            await self._send_collaboration_notification(
                task_data.assigned_to_id,
                "task_assigned",
                {
                    "task_id": task.id,
                    "task_title": task.title,
                    "collaboration_id": collaboration_id
                }
            )
        
        return TaskResponse(**task.__dict__)
    
    async def get_collaboration_workspace(
        self,
        collaboration_id: str,
        creator_id: str
    ) -> CollaborationWorkspace:
        """Get collaboration workspace view"""
        
        # Verify participant access
        participant = await self._get_participant(collaboration_id, creator_id)
        if not participant or participant.invitation_status != InvitationStatus.ACCEPTED:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get collaboration details
        collaboration = await self.db.get(Collaboration, collaboration_id)
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        # Get participants
        participants = await self._get_collaboration_participants(collaboration_id)
        
        # Get recent messages
        recent_messages = await self._get_recent_messages(collaboration_id, limit=20)
        
        # Get active tasks
        active_tasks = await self._get_active_tasks(collaboration_id)
        
        # Get upcoming deadlines
        upcoming_deadlines = await self._get_upcoming_deadlines(collaboration_id)
        
        # Calculate project progress
        project_progress = await self._calculate_project_progress(collaboration_id)
        
        return CollaborationWorkspace(
            collaboration=CollaborationResponse(
                **collaboration.__dict__,
                participant_count=len(participants)
            ),
            participants=participants,
            recent_messages=recent_messages,
            active_tasks=active_tasks,
            upcoming_deadlines=upcoming_deadlines,
            project_progress=project_progress
        )
    
    async def start_live_session(
        self,
        collaboration_id: str,
        host_id: str,
        session_type: str,
        title: str
    ) -> Dict[str, Any]:
        """Start live collaboration session"""
        
        # Verify host is participant
        participant = await self._get_participant(collaboration_id, host_id)
        if not participant or participant.invitation_status != InvitationStatus.ACCEPTED:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create live session
        session = LiveCollaborationSession(
            collaboration_id=collaboration_id,
            session_type=session_type,
            title=title,
            host_id=host_id,
            participants=[host_id]
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        # Notify participants
        await self._notify_participants(
            collaboration_id,
            "live_session_started",
            {
                "session_id": session.id,
                "session_type": session_type,
                "title": title,
                "host_id": host_id
            }
        )
        
        return {
            "session_id": session.id,
            "join_url": f"/collaborate/{collaboration_id}/live/{session.id}",
            "session_type": session_type
        }
    
    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        collaboration_id: str,
        creator_id: str
    ):
        """Handle WebSocket connection for real-time collaboration"""
        
        # Verify participant
        participant = await self._get_participant(collaboration_id, creator_id)
        if not participant or participant.invitation_status != InvitationStatus.ACCEPTED:
            await websocket.close(code=4003, reason="Access denied")
            return
        
        # Accept connection
        await websocket.accept()
        self.active_connections[collaboration_id].add(websocket)
        
        # Notify other participants that user joined
        await self._broadcast_user_status(collaboration_id, creator_id, "online")
        
        try:
            while True:
                # Receive messages from WebSocket
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle different message types
                if message_data["type"] == "typing":
                    await self._broadcast_typing_status(collaboration_id, creator_id, message_data["typing"])
                elif message_data["type"] == "cursor_position":
                    await self._broadcast_cursor_position(collaboration_id, creator_id, message_data["position"])
                elif message_data["type"] == "document_edit":
                    await self._handle_document_edit(collaboration_id, creator_id, message_data["edit"])
                
        except WebSocketDisconnect:
            # Remove connection
            self.active_connections[collaboration_id].discard(websocket)
            
            # Notify other participants that user left
            await self._broadcast_user_status(collaboration_id, creator_id, "offline")
    
    async def _get_participant(self, collaboration_id: str, creator_id: str) -> Optional[CollaborationParticipant]:
        """Get collaboration participant"""
        # Mock implementation - would query database
        return None
    
    async def _get_participant_count(self, collaboration_id: str) -> int:
        """Get number of participants"""
        # Mock implementation
        return 1
    
    async def _send_collaboration_notification(self, creator_id: str, notification_type: str, data: Dict[str, Any]):
        """Send collaboration notification"""
        # Mock implementation - would integrate with notification service
        logger.info(f"Sending {notification_type} notification to {creator_id}: {data}")
    
    async def _notify_participants(self, collaboration_id: str, event_type: str, data: Dict[str, Any]):
        """Notify all collaboration participants"""
        # Mock implementation
        pass
    
    async def _broadcast_message(self, collaboration_id: str, message: CollaborationMessage):
        """Broadcast message to active WebSocket connections"""
        if collaboration_id in self.active_connections:
            message_data = {
                "type": "new_message",
                "message": MessageResponse(**message.__dict__).dict()
            }
            
            disconnected = set()
            for websocket in self.active_connections[collaboration_id]:
                try:
                    await websocket.send_text(json.dumps(message_data))
                except:
                    disconnected.add(websocket)
            
            # Remove disconnected WebSockets
            self.active_connections[collaboration_id] -= disconnected
    
    async def _notify_offline_participants(self, collaboration_id: str, message: CollaborationMessage):
        """Send push notifications to offline participants"""
        # Mock implementation
        pass
    
    async def _get_collaboration_participants(self, collaboration_id: str) -> List[Dict[str, Any]]:
        """Get collaboration participants"""
        # Mock implementation
        return [
            {
                "id": "participant_1",
                "creator_id": "creator_123",
                "role": "Project Lead",
                "permissions": ["edit", "invite", "manage_tasks"],
                "revenue_percentage": 60.0,
                "contribution_hours": 25.5,
                "tasks_completed": 8,
                "status": "online"
            }
        ]
    
    async def _get_recent_messages(self, collaboration_id: str, limit: int) -> List[MessageResponse]:
        """Get recent messages"""
        # Mock implementation
        return []
    
    async def _get_active_tasks(self, collaboration_id: str) -> List[TaskResponse]:
        """Get active tasks"""
        # Mock implementation
        return []
    
    async def _get_upcoming_deadlines(self, collaboration_id: str) -> List[Dict[str, Any]]:
        """Get upcoming deadlines"""
        # Mock implementation
        return [
            {
                "task_id": "task_1",
                "title": "Video Editing",
                "due_date": datetime.utcnow() + timedelta(days=3),
                "assigned_to": "creator_456",
                "priority": "high"
            }
        ]
    
    async def _calculate_project_progress(self, collaboration_id: str) -> Dict[str, Any]:
        """Calculate project progress"""
        # Mock implementation
        return {
            "overall_progress": 65.5,
            "tasks_completed": 8,
            "tasks_total": 12,
            "milestones_completed": 2,
            "milestones_total": 4,
            "estimated_completion": (datetime.utcnow() + timedelta(days=15)).isoformat()
        }
    
    async def _broadcast_user_status(self, collaboration_id: str, creator_id: str, status: str):
        """Broadcast user online/offline status"""
        if collaboration_id in self.active_connections:
            status_data = {
                "type": "user_status",
                "creator_id": creator_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for websocket in self.active_connections[collaboration_id]:
                try:
                    await websocket.send_text(json.dumps(status_data))
                except:
                    pass
    
    async def _broadcast_typing_status(self, collaboration_id: str, creator_id: str, typing: bool):
        """Broadcast typing status"""
        if collaboration_id in self.active_connections:
            typing_data = {
                "type": "typing_status",
                "creator_id": creator_id,
                "typing": typing
            }
            
            for websocket in self.active_connections[collaboration_id]:
                try:
                    await websocket.send_text(json.dumps(typing_data))
                except:
                    pass
    
    async def _broadcast_cursor_position(self, collaboration_id: str, creator_id: str, position: Dict[str, Any]):
        """Broadcast cursor position for collaborative editing"""
        if collaboration_id in self.active_connections:
            cursor_data = {
                "type": "cursor_position",
                "creator_id": creator_id,
                "position": position
            }
            
            for websocket in self.active_connections[collaboration_id]:
                try:
                    await websocket.send_text(json.dumps(cursor_data))
                except:
                    pass
    
    async def _handle_document_edit(self, collaboration_id: str, creator_id: str, edit: Dict[str, Any]):
        """Handle collaborative document editing"""
        # Implement operational transformation for conflict resolution
        # This is a complex topic that would require a proper OT library
        
        if collaboration_id in self.active_connections:
            edit_data = {
                "type": "document_edit",
                "creator_id": creator_id,
                "edit": edit,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for websocket in self.active_connections[collaboration_id]:
                try:
                    await websocket.send_text(json.dumps(edit_data))
                except:
                    pass

# FastAPI Router
from fastapi import APIRouter

def create_collaboration_router(db_session_dependency) -> APIRouter:
    """Create collaboration API router"""
    
    router = APIRouter(prefix="/collaboration", tags=["Collaboration"])
    security = HTTPBearer()
    
    @router.post("/projects", response_model=CollaborationResponse)
    async def create_collaboration(
        collaboration_data: CollaborationCreate,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Create a new collaboration project"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.create_collaboration(creator_id, collaboration_data)
    
    @router.post("/projects/{collaboration_id}/invite")
    async def invite_collaborator(
        collaboration_id: str,
        invite_data: CollaborationInvite,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Invite a creator to collaborate"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.invite_collaborator(collaboration_id, creator_id, invite_data)
    
    @router.post("/projects/{collaboration_id}/respond")
    async def respond_to_invitation(
        collaboration_id: str,
        accept: bool,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Respond to collaboration invitation"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.respond_to_invitation(collaboration_id, creator_id, accept)
    
    @router.get("/projects/{collaboration_id}/workspace")
    async def get_workspace(
        collaboration_id: str,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Get collaboration workspace"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.get_collaboration_workspace(collaboration_id, creator_id)
    
    @router.post("/projects/{collaboration_id}/messages", response_model=MessageResponse)
    async def send_message(
        collaboration_id: str,
        message_data: MessageCreate,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Send message in collaboration"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.send_message(collaboration_id, creator_id, message_data)
    
    @router.post("/projects/{collaboration_id}/tasks", response_model=TaskResponse)
    async def create_task(
        collaboration_id: str,
        task_data: TaskCreate,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Create task in collaboration"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.create_task(collaboration_id, creator_id, task_data)
    
    @router.post("/projects/{collaboration_id}/live")
    async def start_live_session(
        collaboration_id: str,
        session_type: str,
        title: str,
        db: AsyncSession = Depends(db_session_dependency),
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Start live collaboration session"""
        # Extract creator_id from JWT token
        creator_id = "creator_123"  # Mock - extract from JWT
        
        service = CollaborationService(db)
        return await service.start_live_session(collaboration_id, creator_id, session_type, title)
    
    @router.websocket("/projects/{collaboration_id}/ws")
    async def websocket_endpoint(
        websocket: WebSocket,
        collaboration_id: str,
        creator_id: str,  # Would be extracted from token in real implementation
        db: AsyncSession = Depends(db_session_dependency)
    ):
        """WebSocket endpoint for real-time collaboration"""
        service = CollaborationService(db)
        await service.handle_websocket_connection(websocket, collaboration_id, creator_id)
    
    return router

# Configuration template
COLLABORATION_CONFIG = {
    "projects": {
        "max_participants": 10,
        "default_revenue_split": "equal",
        "auto_archive_after_days": 90
    },
    "messaging": {
        "max_message_length": 2000,
        "file_upload_max_size": 10485760,  # 10MB
        "allowed_file_types": ["image", "document", "video", "audio"]
    },
    "tasks": {
        "max_tasks_per_project": 100,
        "default_priority": "medium",
        "auto_assign_creator": True
    },
    "live_sessions": {
        "max_duration_hours": 8,
        "recording_enabled": True,
        "screen_sharing_enabled": True
    },
    "notifications": {
        "email_enabled": True,
        "push_enabled": True,
        "digest_frequency": "daily"
    }
}

if __name__ == "__main__":
    # Example usage
    print("Collaboration API Template loaded successfully")
    print("Collaboration Types:", [col_type.value for col_type in CollaborationType])
    print("Message Types:", [msg_type.value for msg_type in MessageType])