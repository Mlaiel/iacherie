"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Collaboration Service Template for Ainflue Platform
==================================================

Production-ready real-time collaboration service with:
- Creator matching and discovery
- Project collaboration management
- Real-time communication and workspace
- Revenue sharing and contract management
- Collaboration workflow automation
- Multi-format content collaboration
- Version control and change tracking
- Collaboration analytics and insights

Author: Fahed Mlaiel (mlaiel@live.de)
Collaboration Expert & Backend Senior
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker
from ..communication_manager import CommunicationManager

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of collaborations"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_CREATION = "video_creation"
    PODCAST_SERIES = "podcast_series"
    CONTENT_CAMPAIGN = "content_campaign"
    CROSS_PROMOTION = "cross_promotion"
    BRAND_PARTNERSHIP = "brand_partnership"
    EDUCATIONAL_SERIES = "educational_series"
    JOINT_LIVESTREAM = "joint_livestream"


class CollaborationStatus(Enum):
    """Collaboration project status"""
    PROPOSAL = "proposal"
    NEGOTIATING = "negotiating"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class ParticipantRole(Enum):
    """Participant roles in collaboration"""
    INITIATOR = "initiator"
    COLLABORATOR = "collaborator"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"
    MANAGER = "manager"
    OBSERVER = "observer"


class CollaborationPhase(Enum):
    """Collaboration project phases"""
    PLANNING = "planning"
    PRE_PRODUCTION = "pre_production"
    PRODUCTION = "production"
    POST_PRODUCTION = "post_production"
    REVIEW = "review"
    FINALIZATION = "finalization"
    DISTRIBUTION = "distribution"


@dataclass
class CollaborationProject:
    """Collaboration project data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    collaboration_type: CollaborationType = CollaborationType.CONTENT_CAMPAIGN
    status: CollaborationStatus = CollaborationStatus.PROPOSAL
    phase: CollaborationPhase = CollaborationPhase.PLANNING
    
    # Participants
    initiator_id: str = ""
    participants: Dict[str, ParticipantRole] = field(default_factory=dict)
    max_participants: int = 5
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.utcnow)
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Requirements
    required_skills: List[str] = field(default_factory=list)
    required_equipment: List[str] = field(default_factory=list)
    minimum_followers: int = 0
    minimum_rating: float = 0.0
    
    # Content and deliverables
    deliverables: List[str] = field(default_factory=list)
    content_guidelines: Dict[str, Any] = field(default_factory=dict)
    quality_standards: Dict[str, Any] = field(default_factory=dict)
    
    # Financial
    budget: float = 0.0
    revenue_sharing: Dict[str, float] = field(default_factory=dict)
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    
    # Workspace
    workspace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    shared_resources: List[str] = field(default_factory=list)
    communication_channels: List[str] = field(default_factory=list)
    
    # Progress tracking
    progress_percentage: float = 0.0
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Analytics
    views_count: int = 0
    applications_count: int = 0
    completion_rate: float = 0.0


@dataclass
class CollaborationWorkspace:
    """Real-time collaboration workspace"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    name: str = ""
    
    # Real-time features
    active_users: Set[str] = field(default_factory=set)
    chat_history: List[Dict[str, Any]] = field(default_factory=list)
    shared_files: List[Dict[str, Any]] = field(default_factory=list)
    
    # Version control
    versions: List[Dict[str, Any]] = field(default_factory=list)
    current_version: str = "1.0"
    
    # Collaboration tools
    whiteboard_data: Dict[str, Any] = field(default_factory=dict)
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Settings
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    notification_settings: Dict[str, Any] = field(default_factory=dict)


class CollaborationConfig:
    """Collaboration service configuration"""
    
    def __init__(self):
        # Matching algorithm settings
        self.enable_ai_matching = True
        self.matching_threshold = 0.7
        self.max_recommendations = 20
        
        # Real-time collaboration
        self.max_workspace_users = 10
        self.message_history_limit = 1000
        self.file_size_limit = 100 * 1024 * 1024  # 100MB
        
        # Project settings
        self.max_project_duration = 365  # days
        self.auto_archive_delay = 30  # days after completion
        self.reminder_intervals = [7, 3, 1]  # days before deadline
        
        # Revenue sharing
        self.platform_fee_percentage = 5.0
        self.minimum_payout = 50.0
        self.payout_schedule = "monthly"
        
        # Communication
        self.enable_video_calls = True
        self.enable_screen_sharing = True
        self.enable_file_sharing = True
        self.max_call_duration = 240  # minutes


# Pydantic models for API
class CollaborationProjectRequest(BaseModel):
    """Collaboration project creation request"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    collaboration_type: CollaborationType
    required_skills: List[str] = Field(default_factory=list)
    required_equipment: List[str] = Field(default_factory=list)
    minimum_followers: int = Field(0, ge=0)
    minimum_rating: float = Field(0.0, ge=0.0, le=5.0)
    budget: float = Field(0.0, ge=0.0)
    deadline: Optional[datetime] = None
    max_participants: int = Field(5, ge=2, le=20)


class CollaborationApplicationRequest(BaseModel):
    """Collaboration application request"""
    project_id: str
    message: str = Field(..., min_length=10, max_length=1000)
    portfolio_links: List[str] = Field(default_factory=list)
    proposed_role: ParticipantRole = ParticipantRole.COLLABORATOR
    availability: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceMessageRequest(BaseModel):
    """Workspace message request"""
    workspace_id: str
    message: str = Field(..., min_length=1, max_length=1000)
    message_type: str = Field("text", regex="^(text|file|image|audio|video)$")
    reply_to: Optional[str] = None


class CollaborationProjectResponse(BaseModel):
    """Collaboration project response"""
    id: str
    title: str
    description: str
    collaboration_type: CollaborationType
    status: CollaborationStatus
    phase: CollaborationPhase
    initiator_id: str
    participants_count: int
    created_at: datetime
    deadline: Optional[datetime] = None
    budget: float
    progress_percentage: float


class CreatorMatchResponse(BaseModel):
    """Creator matching response"""
    creator_id: str
    username: str
    match_score: float
    compatibility_reasons: List[str]
    skills: List[str]
    rating: float
    follower_count: int


class CollaborationService(BaseMicroservice):
    """
    Enterprise Collaboration Service for Ainflue Platform
    
    Provides real-time collaboration features, creator matching,
    project management, and workspace tools for content creators.
    """
    
    def __init__(self, config: Optional[CollaborationConfig] = None):
        super().__init__("collaboration-service")
        
        self.config = config or CollaborationConfig()
        self.projects: Dict[str, CollaborationProject] = {}
        self.workspaces: Dict[str, CollaborationWorkspace] = {}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # Metrics
        self.projects_counter = Counter('collaboration_projects_total', 'Total collaboration projects created')
        self.applications_counter = Counter('collaboration_applications_total', 'Total collaboration applications')
        self.messages_counter = Counter('collaboration_messages_total', 'Total workspace messages')
        self.project_duration = Histogram('collaboration_project_duration_days', 'Project completion duration')
        self.active_projects_gauge = Gauge('collaboration_active_projects', 'Active collaboration projects')
        self.active_workspaces_gauge = Gauge('collaboration_active_workspaces', 'Active collaboration workspaces')
        
        # Circuit breakers
        self.matching_circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=Exception
        )
        
        self.notification_circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            expected_exception=Exception
        )
        
        # Communication manager
        self.communication_manager = CommunicationManager()
        
        # Redis client for real-time features
        self.redis_client: Optional[redis.Redis] = None
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        logger.info("Collaboration Service initialized")
    
    async def startup(self):
        """Service startup tasks"""
        await super().startup()
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
        
        # Start background tasks
        await self._start_background_tasks()
        
        logger.info("Collaboration Service started")
    
    async def shutdown(self):
        """Service shutdown tasks"""
        logger.info("Shutting down Collaboration Service...")
        
        # Close all WebSocket connections
        for connections in self.active_connections.values():
            for websocket in connections.copy():
                try:
                    await websocket.close()
                except:
                    pass
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        await super().shutdown()
        logger.info("Collaboration Service shut down")
    
    async def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks"""
        # Project monitoring
        monitoring_task = asyncio.create_task(self._monitor_projects())
        self.background_tasks.add(monitoring_task)
        
        # Deadline reminders
        reminder_task = asyncio.create_task(self._send_deadline_reminders())
        self.background_tasks.add(reminder_task)
        
        # Metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics())
        self.background_tasks.add(metrics_task)
        
        # Cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_expired_data())
        self.background_tasks.add(cleanup_task)
        
        logger.info("Started background tasks")
    
    async def create_project(
        self,
        creator_id: str,
        request: CollaborationProjectRequest
    ) -> Dict[str, Any]:
        """Create a new collaboration project"""
        start_time = time.time()
        
        try:
            # Create project
            project = CollaborationProject(
                title=request.title,
                description=request.description,
                collaboration_type=request.collaboration_type,
                initiator_id=creator_id,
                required_skills=request.required_skills,
                required_equipment=request.required_equipment,
                minimum_followers=request.minimum_followers,
                minimum_rating=request.minimum_rating,
                budget=request.budget,
                deadline=request.deadline,
                max_participants=request.max_participants
            )
            
            # Add initiator as participant
            project.participants[creator_id] = ParticipantRole.INITIATOR
            
            # Initialize revenue sharing (initiator gets 60% by default)
            project.revenue_sharing[creator_id] = 60.0
            
            # Create workspace
            workspace = CollaborationWorkspace(
                project_id=project.id,
                name=f"{project.title} Workspace"
            )
            
            # Set workspace permissions
            workspace.permissions[creator_id] = ["admin", "read", "write", "invite", "manage"]
            
            # Store project and workspace
            self.projects[project.id] = project
            self.workspaces[workspace.id] = workspace
            project.workspace_id = workspace.id
            
            # Cache in Redis
            await self._cache_project(project)
            await self._cache_workspace(workspace)
            
            # Update metrics
            self.projects_counter.inc()
            
            # Send notifications to potential collaborators
            await self._notify_potential_collaborators(project)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "project_id": project.id,
                "workspace_id": workspace.id,
                "status": project.status.value,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def apply_to_project(
        self,
        creator_id: str,
        request: CollaborationApplicationRequest
    ) -> Dict[str, Any]:
        """Apply to join a collaboration project"""
        try:
            project = self.projects.get(request.project_id)
            if not project:
                # Try to load from cache
                project = await self._load_project_from_cache(request.project_id)
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Check if already a participant
            if creator_id in project.participants:
                raise HTTPException(status_code=400, detail="Already a participant")
            
            # Check if project is accepting applications
            if project.status != CollaborationStatus.PROPOSAL:
                raise HTTPException(status_code=400, detail="Project not accepting applications")
            
            # Check participant limit
            if len(project.participants) >= project.max_participants:
                raise HTTPException(status_code=400, detail="Project is full")
            
            # Check creator eligibility
            eligibility = await self._check_creator_eligibility(creator_id, project)
            if not eligibility["eligible"]:
                raise HTTPException(status_code=400, detail=eligibility["reason"])
            
            # Create application
            application = {
                "id": str(uuid.uuid4()),
                "project_id": request.project_id,
                "creator_id": creator_id,
                "message": request.message,
                "portfolio_links": request.portfolio_links,
                "proposed_role": request.proposed_role.value,
                "availability": request.availability,
                "created_at": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            # Store application
            await self._store_application(application)
            
            # Update project metrics
            project.applications_count += 1
            await self._cache_project(project)
            
            # Notify project initiator
            await self._notify_application_received(project, application)
            
            # Update metrics
            self.applications_counter.inc()
            
            return {
                "success": True,
                "application_id": application["id"],
                "status": "pending",
                "message": "Application submitted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Project application failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def accept_application(
        self,
        project_id: str,
        application_id: str,
        creator_id: str,
        revenue_share: float = 20.0
    ) -> Dict[str, Any]:
        """Accept a collaboration application"""
        try:
            project = self.projects.get(project_id)
            if not project:
                project = await self._load_project_from_cache(project_id)
            
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Check if user is the initiator
            if project.initiator_id != creator_id:
                raise HTTPException(status_code=403, detail="Only project initiator can accept applications")
            
            # Load application
            application = await self._load_application(application_id)
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            
            if application["status"] != "pending":
                raise HTTPException(status_code=400, detail="Application already processed")
            
            # Add participant to project
            applicant_id = application["creator_id"]
            proposed_role = ParticipantRole(application["proposed_role"])
            
            project.participants[applicant_id] = proposed_role
            project.revenue_sharing[applicant_id] = revenue_share
            
            # Update workspace permissions
            workspace = self.workspaces.get(project.workspace_id)
            if workspace:
                workspace.permissions[applicant_id] = ["read", "write", "comment"]
                await self._cache_workspace(workspace)
            
            # Update application status
            application["status"] = "accepted"
            application["accepted_at"] = datetime.utcnow().isoformat()
            application["revenue_share"] = revenue_share
            await self._store_application(application)
            
            # Update project status if needed
            if project.status == CollaborationStatus.PROPOSAL and len(project.participants) >= 2:
                project.status = CollaborationStatus.ACTIVE
                project.start_date = datetime.utcnow()
            
            await self._cache_project(project)
            
            # Send notifications
            await self._notify_application_accepted(project, application)
            await self._notify_project_participants(project, "new_participant_joined", {
                "participant_id": applicant_id,
                "role": proposed_role.value
            })
            
            return {
                "success": True,
                "message": "Application accepted",
                "participant_added": applicant_id,
                "project_status": project.status.value
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Application acceptance failed: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @CircuitBreaker.circuit_breaker
    async def find_collaborators(
        self,
        creator_id: str,
        project_id: Optional[str] = None,
        skills: Optional[List[str]] = None,
        collaboration_type: Optional[CollaborationType] = None,
        limit: int = 10
    ) -> List[CreatorMatchResponse]:
        """Find potential collaborators using AI matching"""
        try:
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            if not creator_profile:
                raise HTTPException(status_code=404, detail="Creator profile not found")
            
            # Get project requirements if specified
            project_requirements = {}
            if project_id:
                project = self.projects.get(project_id) or await self._load_project_from_cache(project_id)
                if project:
                    project_requirements = {
                        "skills": project.required_skills,
                        "equipment": project.required_equipment,
                        "collaboration_type": project.collaboration_type.value,
                        "minimum_followers": project.minimum_followers,
                        "minimum_rating": project.minimum_rating
                    }
            
            # Build search criteria
            search_criteria = {
                "creator_id": creator_id,
                "skills": skills or project_requirements.get("skills", []),
                "collaboration_type": collaboration_type.value if collaboration_type else project_requirements.get("collaboration_type"),
                "minimum_followers": project_requirements.get("minimum_followers", 0),
                "minimum_rating": project_requirements.get("minimum_rating", 0.0),
                "exclude_ids": [creator_id]  # Exclude self
            }
            
            # Find matching creators
            potential_matches = await self._find_matching_creators(search_criteria, limit * 2)
            
            # Calculate compatibility scores
            matches = []
            for candidate in potential_matches:
                compatibility = await self._calculate_compatibility(
                    creator_profile,
                    candidate,
                    search_criteria
                )
                
                if compatibility["score"] >= self.config.matching_threshold:
                    matches.append(CreatorMatchResponse(
                        creator_id=candidate["id"],
                        username=candidate["username"],
                        match_score=compatibility["score"],
                        compatibility_reasons=compatibility["reasons"],
                        skills=candidate.get("skills", []),
                        rating=candidate.get("rating", 0.0),
                        follower_count=candidate.get("follower_count", 0)
                    ))
            
            # Sort by match score and limit results
            matches.sort(key=lambda x: x.match_score, reverse=True)
            return matches[:limit]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Collaborator matching failed: {e}")
            raise HTTPException(status_code=500, detail="Matching service unavailable")
    
    async def websocket_connect(self, websocket: WebSocket, workspace_id: str, creator_id: str):
        """Handle WebSocket connection for real-time collaboration"""
        try:
            await websocket.accept()
            
            # Verify workspace access
            workspace = self.workspaces.get(workspace_id)
            if not workspace:
                await websocket.close(code=4004, reason="Workspace not found")
                return
            
            # Check permissions
            if creator_id not in workspace.permissions:
                await websocket.close(code=4003, reason="Access denied")
                return
            
            # Add to active connections
            if workspace_id not in self.active_connections:
                self.active_connections[workspace_id] = set()
            
            self.active_connections[workspace_id].add(websocket)
            workspace.active_users.add(creator_id)
            
            # Notify other users
            await self._broadcast_to_workspace(workspace_id, {
                "type": "user_joined",
                "user_id": creator_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_websocket=websocket)
            
            # Send workspace state
            await websocket.send_json({
                "type": "workspace_state",
                "workspace": {
                    "id": workspace.id,
                    "name": workspace.name,
                    "active_users": list(workspace.active_users),
                    "chat_history": workspace.chat_history[-50:],  # Last 50 messages
                    "shared_files": workspace.shared_files,
                    "permissions": workspace.permissions.get(creator_id, [])
                }
            })
            
            # Handle messages
            await self._handle_websocket_messages(websocket, workspace_id, creator_id)
            
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            # Clean up connection
            if workspace_id in self.active_connections:
                self.active_connections[workspace_id].discard(websocket)
                if not self.active_connections[workspace_id]:
                    del self.active_connections[workspace_id]
            
            # Remove from active users
            workspace = self.workspaces.get(workspace_id)
            if workspace:
                workspace.active_users.discard(creator_id)
                
                # Notify other users
                await self._broadcast_to_workspace(workspace_id, {
                    "type": "user_left",
                    "user_id": creator_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    async def _handle_websocket_messages(self, websocket: WebSocket, workspace_id: str, creator_id: str):
        """Handle incoming WebSocket messages"""
        try:
            while True:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "chat_message":
                    await self._handle_chat_message(workspace_id, creator_id, data)
                elif message_type == "file_share":
                    await self._handle_file_share(workspace_id, creator_id, data)
                elif message_type == "cursor_position":
                    await self._handle_cursor_position(workspace_id, creator_id, data)
                elif message_type == "annotation":
                    await self._handle_annotation(workspace_id, creator_id, data)
                elif message_type == "typing_indicator":
                    await self._handle_typing_indicator(workspace_id, creator_id, data)
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket message handling error: {e}")
    
    async def _handle_chat_message(self, workspace_id: str, creator_id: str, data: Dict[str, Any]):
        """Handle chat message"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return
        
        message = {
            "id": str(uuid.uuid4()),
            "user_id": creator_id,
            "content": data.get("content", ""),
            "message_type": data.get("message_type", "text"),
            "timestamp": datetime.utcnow().isoformat(),
            "reply_to": data.get("reply_to")
        }
        
        # Add to chat history
        workspace.chat_history.append(message)
        
        # Limit chat history
        if len(workspace.chat_history) > self.config.message_history_limit:
            workspace.chat_history = workspace.chat_history[-self.config.message_history_limit:]
        
        # Cache workspace
        await self._cache_workspace(workspace)
        
        # Broadcast message
        await self._broadcast_to_workspace(workspace_id, {
            "type": "chat_message",
            "message": message
        })
        
        # Update metrics
        self.messages_counter.inc()
    
    async def _handle_file_share(self, workspace_id: str, creator_id: str, data: Dict[str, Any]):
        """Handle file sharing"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return
        
        file_info = {
            "id": str(uuid.uuid4()),
            "name": data.get("filename", ""),
            "size": data.get("filesize", 0),
            "type": data.get("filetype", ""),
            "url": data.get("file_url", ""),
            "uploaded_by": creator_id,
            "uploaded_at": datetime.utcnow().isoformat(),
            "description": data.get("description", "")
        }
        
        # Add to shared files
        workspace.shared_files.append(file_info)
        
        # Cache workspace
        await self._cache_workspace(workspace)
        
        # Broadcast file share
        await self._broadcast_to_workspace(workspace_id, {
            "type": "file_shared",
            "file": file_info
        })
    
    async def _handle_cursor_position(self, workspace_id: str, creator_id: str, data: Dict[str, Any]):
        """Handle cursor position for real-time collaboration"""
        # Broadcast cursor position to other users
        await self._broadcast_to_workspace(workspace_id, {
            "type": "cursor_position",
            "user_id": creator_id,
            "position": data.get("position", {}),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_annotation(self, workspace_id: str, creator_id: str, data: Dict[str, Any]):
        """Handle content annotation"""
        workspace = self.workspaces.get(workspace_id)
        if not workspace:
            return
        
        annotation = {
            "id": str(uuid.uuid4()),
            "user_id": creator_id,
            "content": data.get("content", ""),
            "position": data.get("position", {}),
            "type": data.get("annotation_type", "comment"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add annotation
        workspace.annotations.append(annotation)
        
        # Cache workspace
        await self._cache_workspace(workspace)
        
        # Broadcast annotation
        await self._broadcast_to_workspace(workspace_id, {
            "type": "annotation_added",
            "annotation": annotation
        })
    
    async def _handle_typing_indicator(self, workspace_id: str, creator_id: str, data: Dict[str, Any]):
        """Handle typing indicator"""
        # Broadcast typing indicator to other users
        await self._broadcast_to_workspace(workspace_id, {
            "type": "typing_indicator",
            "user_id": creator_id,
            "is_typing": data.get("is_typing", False),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _broadcast_to_workspace(
        self,
        workspace_id: str,
        message: Dict[str, Any],
        exclude_websocket: Optional[WebSocket] = None
    ):
        """Broadcast message to all connected users in workspace"""
        if workspace_id not in self.active_connections:
            return
        
        connections = self.active_connections[workspace_id].copy()
        for websocket in connections:
            if websocket == exclude_websocket:
                continue
            
            try:
                await websocket.send_json(message)
            except:
                # Remove broken connections
                self.active_connections[workspace_id].discard(websocket)
    
    # Helper methods
    async def _check_creator_eligibility(self, creator_id: str, project: CollaborationProject) -> Dict[str, Any]:
        """Check if creator is eligible for project"""
        try:
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            if not creator_profile:
                return {"eligible": False, "reason": "Creator profile not found"}
            
            # Check minimum followers
            if creator_profile.get("follower_count", 0) < project.minimum_followers:
                return {"eligible": False, "reason": "Insufficient followers"}
            
            # Check minimum rating
            if creator_profile.get("rating", 0.0) < project.minimum_rating:
                return {"eligible": False, "reason": "Rating below minimum requirement"}
            
            # Check required skills (at least 50% match)
            creator_skills = set(creator_profile.get("skills", []))
            required_skills = set(project.required_skills)
            
            if required_skills and len(creator_skills.intersection(required_skills)) / len(required_skills) < 0.5:
                return {"eligible": False, "reason": "Insufficient skill match"}
            
            return {"eligible": True}
            
        except Exception as e:
            logger.error(f"Eligibility check failed: {e}")
            return {"eligible": False, "reason": "Unable to verify eligibility"}
    
    async def _find_matching_creators(self, criteria: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Find creators matching the search criteria"""
        # This would integrate with the creator service to find matching creators
        # For now, return mock data
        return [
            {
                "id": f"creator_{i}",
                "username": f"creator_{i}",
                "skills": ["video_editing", "music_production", "content_creation"],
                "rating": 4.5,
                "follower_count": 10000,
                "collaboration_history": 5
            }
            for i in range(limit)
        ]
    
    async def _calculate_compatibility(
        self,
        creator_profile: Dict[str, Any],
        candidate: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate compatibility score between creators"""
        score = 0.0
        reasons = []
        
        # Skill match (40% weight)
        creator_skills = set(creator_profile.get("skills", []))
        candidate_skills = set(candidate.get("skills", []))
        skill_overlap = creator_skills.intersection(candidate_skills)
        
        if creator_skills and candidate_skills:
            skill_score = len(skill_overlap) / max(len(creator_skills), len(candidate_skills))
            score += skill_score * 0.4
            
            if skill_overlap:
                reasons.append(f"Shared skills: {', '.join(list(skill_overlap)[:3])}")
        
        # Rating compatibility (20% weight)
        creator_rating = creator_profile.get("rating", 0.0)
        candidate_rating = candidate.get("rating", 0.0)
        
        if abs(creator_rating - candidate_rating) <= 1.0:
            rating_score = 1.0 - (abs(creator_rating - candidate_rating) / 5.0)
            score += rating_score * 0.2
            reasons.append("Similar quality standards")
        
        # Collaboration history (20% weight)
        candidate_history = candidate.get("collaboration_history", 0)
        if candidate_history > 0:
            history_score = min(candidate_history / 10, 1.0)  # Max score at 10+ collaborations
            score += history_score * 0.2
            reasons.append(f"Experienced collaborator ({candidate_history} projects)")
        
        # Follower compatibility (20% weight)
        creator_followers = creator_profile.get("follower_count", 0)
        candidate_followers = candidate.get("follower_count", 0)
        
        # Similar audience size is beneficial
        if creator_followers > 0 and candidate_followers > 0:
            ratio = min(creator_followers, candidate_followers) / max(creator_followers, candidate_followers)
            follower_score = ratio
            score += follower_score * 0.2
            
            if ratio > 0.5:
                reasons.append("Similar audience size")
        
        return {
            "score": min(score, 1.0),
            "reasons": reasons
        }
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator profile from creator service"""
        try:
            # This would integrate with the creator service
            # For now, return mock data
            return {
                "id": creator_id,
                "username": f"creator_{creator_id}",
                "skills": ["content_creation", "video_editing"],
                "rating": 4.2,
                "follower_count": 5000,
                "collaboration_history": 3
            }
        except Exception as e:
            logger.error(f"Failed to get creator profile: {e}")
            return None
    
    async def _cache_project(self, project: CollaborationProject):
        """Cache project in Redis"""
        if not self.redis_client:
            return
        
        try:
            project_data = {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "collaboration_type": project.collaboration_type.value,
                "status": project.status.value,
                "phase": project.phase.value,
                "initiator_id": project.initiator_id,
                "participants": {k: v.value for k, v in project.participants.items()},
                "workspace_id": project.workspace_id,
                "created_at": project.created_at.isoformat(),
                "deadline": project.deadline.isoformat() if project.deadline else None,
                "budget": project.budget,
                "progress_percentage": project.progress_percentage
            }
            
            await self.redis_client.setex(
                f"collaboration:project:{project.id}",
                3600,  # 1 hour TTL
                json.dumps(project_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache project: {e}")
    
    async def _cache_workspace(self, workspace: CollaborationWorkspace):
        """Cache workspace in Redis"""
        if not self.redis_client:
            return
        
        try:
            workspace_data = {
                "id": workspace.id,
                "project_id": workspace.project_id,
                "name": workspace.name,
                "active_users": list(workspace.active_users),
                "chat_history": workspace.chat_history[-100:],  # Last 100 messages
                "shared_files": workspace.shared_files,
                "permissions": workspace.permissions
            }
            
            await self.redis_client.setex(
                f"collaboration:workspace:{workspace.id}",
                1800,  # 30 minutes TTL
                json.dumps(workspace_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache workspace: {e}")
    
    async def _load_project_from_cache(self, project_id: str) -> Optional[CollaborationProject]:
        """Load project from Redis cache"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(f"collaboration:project:{project_id}")
            if not data:
                return None
            
            project_data = json.loads(data)
            
            # Reconstruct project object (simplified)
            project = CollaborationProject(
                id=project_data["id"],
                title=project_data["title"],
                description=project_data["description"],
                collaboration_type=CollaborationType(project_data["collaboration_type"]),
                status=CollaborationStatus(project_data["status"]),
                phase=CollaborationPhase(project_data["phase"]),
                initiator_id=project_data["initiator_id"],
                workspace_id=project_data["workspace_id"],
                budget=project_data["budget"],
                progress_percentage=project_data["progress_percentage"]
            )
            
            # Add to memory cache
            self.projects[project_id] = project
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to load project from cache: {e}")
            return None
    
    async def _store_application(self, application: Dict[str, Any]):
        """Store collaboration application"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                f"collaboration:application:{application['id']}",
                7200,  # 2 hours TTL
                json.dumps(application)
            )
        except Exception as e:
            logger.error(f"Failed to store application: {e}")
    
    async def _load_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Load collaboration application"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(f"collaboration:application:{application_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to load application: {e}")
        
        return None
    
    async def _notify_potential_collaborators(self, project: CollaborationProject):
        """Notify potential collaborators about new project"""
        # This would integrate with the notification service
        pass
    
    async def _notify_application_received(self, project: CollaborationProject, application: Dict[str, Any]):
        """Notify project initiator about new application"""
        # This would send notification to the project initiator
        pass
    
    async def _notify_application_accepted(self, project: CollaborationProject, application: Dict[str, Any]):
        """Notify applicant that their application was accepted"""
        # This would send notification to the applicant
        pass
    
    async def _notify_project_participants(self, project: CollaborationProject, event_type: str, data: Dict[str, Any]):
        """Notify all project participants about events"""
        # This would send notifications to all participants
        pass
    
    async def _monitor_projects(self):
        """Monitor project progress and deadlines"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                now = datetime.utcnow()
                
                for project in self.projects.values():
                    # Check for overdue projects
                    if project.deadline and project.deadline < now and project.status == CollaborationStatus.ACTIVE:
                        logger.warning(f"Project {project.id} is overdue")
                        # Could update status or send notifications
                
            except Exception as e:
                logger.error(f"Project monitoring failed: {e}")
    
    async def _send_deadline_reminders(self):
        """Send deadline reminders to project participants"""
        while True:
            try:
                await asyncio.sleep(86400)  # Check daily
                
                now = datetime.utcnow()
                
                for project in self.projects.values():
                    if not project.deadline or project.status != CollaborationStatus.ACTIVE:
                        continue
                    
                    days_until_deadline = (project.deadline - now).days
                    
                    if days_until_deadline in self.config.reminder_intervals:
                        await self._send_deadline_reminder(project, days_until_deadline)
                
            except Exception as e:
                logger.error(f"Deadline reminder failed: {e}")
    
    async def _send_deadline_reminder(self, project: CollaborationProject, days_remaining: int):
        """Send deadline reminder for specific project"""
        # This would send reminder notifications to all participants
        logger.info(f"Sending deadline reminder for project {project.id}: {days_remaining} days remaining")
    
    async def _collect_metrics(self):
        """Collect and update metrics periodically"""
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Update active projects gauge
                active_count = sum(1 for p in self.projects.values() 
                                 if p.status == CollaborationStatus.ACTIVE)
                self.active_projects_gauge.set(active_count)
                
                # Update active workspaces gauge
                active_workspaces = len(self.active_connections)
                self.active_workspaces_gauge.set(active_workspaces)
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
    
    async def _cleanup_expired_data(self):
        """Clean up expired projects and workspaces"""
        while True:
            try:
                await asyncio.sleep(3600)  # Clean up every hour
                
                # Clean up completed projects older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                to_remove = []
                for project_id, project in self.projects.items():
                    if (project.status in [CollaborationStatus.COMPLETED, CollaborationStatus.CANCELLED] and
                        project.completed_at and project.completed_at < cutoff_date):
                        to_remove.append(project_id)
                
                for project_id in to_remove:
                    del self.projects[project_id]
                    # Also remove associated workspace
                    workspace_id = self.projects.get(project_id, {}).get("workspace_id")
                    if workspace_id and workspace_id in self.workspaces:
                        del self.workspaces[workspace_id]
                
                logger.info(f"Cleaned up {len(to_remove)} expired projects")
                
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Collaboration service health check"""
        try:
            # Test Redis connection
            redis_healthy = False
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    redis_healthy = True
            except Exception:
                pass
            
            # Check active connections
            total_connections = sum(len(connections) for connections in self.active_connections.values())
            
            status = "healthy" if redis_healthy else "degraded"
            
            return {
                'status': status,
                'redis_connected': redis_healthy,
                'total_projects': len(self.projects),
                'active_projects': sum(1 for p in self.projects.values() 
                                     if p.status == CollaborationStatus.ACTIVE),
                'total_workspaces': len(self.workspaces),
                'active_connections': total_connections,
                'background_tasks': len(self.background_tasks),
                'circuit_breakers': {
                    'matching_service': self.matching_circuit_breaker.state.name,
                    'notification_service': self.notification_circuit_breaker.state.name
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# FastAPI app setup
def create_collaboration_app() -> FastAPI:
    """Create FastAPI application for collaboration service"""
    
    app = FastAPI(
        title="Ainflue Collaboration Service",
        description="Real-time collaboration and creator matching service",
        version="1.0.0"
    )
    
    # Initialize service
    service = CollaborationService()
    
    @app.on_event("startup")
    async def startup():
        await service.startup()
    
    @app.on_event("shutdown")
    async def shutdown():
        await service.shutdown()
    
    @app.post("/projects")
    async def create_project(
        creator_id: str,
        request: CollaborationProjectRequest
    ):
        """Create a new collaboration project"""
        return await service.create_project(creator_id, request)
    
    @app.post("/projects/{project_id}/apply")
    async def apply_to_project(
        project_id: str,
        creator_id: str,
        request: CollaborationApplicationRequest
    ):
        """Apply to join a collaboration project"""
        request.project_id = project_id
        return await service.apply_to_project(creator_id, request)
    
    @app.post("/projects/{project_id}/applications/{application_id}/accept")
    async def accept_application(
        project_id: str,
        application_id: str,
        creator_id: str,
        revenue_share: float = 20.0
    ):
        """Accept a collaboration application"""
        return await service.accept_application(project_id, application_id, creator_id, revenue_share)
    
    @app.get("/creators/{creator_id}/matches")
    async def find_collaborators(
        creator_id: str,
        project_id: Optional[str] = None,
        skills: Optional[str] = None,
        collaboration_type: Optional[CollaborationType] = None,
        limit: int = 10
    ):
        """Find potential collaborators"""
        skill_list = skills.split(",") if skills else None
        return await service.find_collaborators(
            creator_id, project_id, skill_list, collaboration_type, limit
        )
    
    @app.websocket("/workspace/{workspace_id}")
    async def websocket_endpoint(websocket: WebSocket, workspace_id: str, creator_id: str):
        """WebSocket endpoint for real-time collaboration"""
        await service.websocket_connect(websocket, workspace_id, creator_id)
    
    @app.get("/health")
    async def health_check():
        """Service health check"""
        return await service.health_check()
    
    return app


# Export classes for use in other modules
__all__ = [
    'CollaborationService',
    'CollaborationConfig',
    'CollaborationType',
    'CollaborationStatus',
    'ParticipantRole',
    'CollaborationPhase',
    'CollaborationProject',
    'CollaborationWorkspace',
    'CollaborationProjectRequest',
    'CollaborationApplicationRequest',
    'WorkspaceMessageRequest',
    'CollaborationProjectResponse',
    'CreatorMatchResponse',
    'create_collaboration_app'
]