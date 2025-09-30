"""
🤝 Collaboration Service Template - Enterprise Creator Collaboration Framework
=============================================================================

🛡️ BACKEND SENIOR - Advanced Collaboration Service Template
- Creator-to-creator collaboration management
- Real-time collaboration workflows and approval processes
- Project sharing and co-creation features
- Revenue sharing and collaboration agreements
- Collaborative content editing and review systems
- Team workspace and permission management

Author: Backend Senior Expert
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import uuid
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborationStatus(Enum):
    """Collaboration status types"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class CollaborationType(Enum):
    """Types of collaboration"""
    CO_CREATION = "co_creation"
    GUEST_APPEARANCE = "guest_appearance"
    CONTENT_EXCHANGE = "content_exchange"
    JOINT_CAMPAIGN = "joint_campaign"
    SKILL_SHARING = "skill_sharing"
    CROSS_PROMOTION = "cross_promotion"
    MENTORSHIP = "mentorship"

class ParticipantRole(Enum):
    """Participant roles in collaboration"""
    INITIATOR = "initiator"
    COLLABORATOR = "collaborator"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    OBSERVER = "observer"

class TaskStatus(Enum):
    """Task status in collaboration"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class Permission(Enum):
    """Collaboration permissions"""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    MANAGE = "manage"
    APPROVE = "approve"
    DELETE = "delete"

@dataclass
class CollaborationParticipant:
    """Collaboration participant details"""
    user_id: str
    username: str
    role: ParticipantRole
    permissions: List[Permission]
    joined_at: datetime = field(default_factory=datetime.now)
    contribution_percentage: float = 0.0
    revenue_share_percentage: float = 0.0
    skills: List[str] = field(default_factory=list)
    contact_info: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    last_activity: datetime = field(default_factory=datetime.now)

@dataclass
class CollaborationTask:
    """Individual task within collaboration"""
    task_id: str
    title: str
    description: str
    assigned_to: str
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: str = "medium"  # low, medium, high, critical
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)  # task_ids
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None

@dataclass
class CollaborationProject:
    """Main collaboration project"""
    project_id: str
    title: str
    description: str
    collaboration_type: CollaborationType
    initiator_id: str
    participants: List[CollaborationParticipant] = field(default_factory=list)
    tasks: List[CollaborationTask] = field(default_factory=list)
    status: CollaborationStatus = CollaborationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    budget: Optional[float] = None
    revenue_sharing_agreement: Dict[str, Any] = field(default_factory=dict)
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    communication_channels: List[Dict[str, str]] = field(default_factory=list)
    approval_workflow: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_public: bool = False

@dataclass
class CollaborationInvitation:
    """Collaboration invitation"""
    invitation_id: str
    project_id: str
    inviter_id: str
    invitee_id: str
    proposed_role: ParticipantRole
    proposed_permissions: List[Permission]
    proposed_revenue_share: float
    message: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    status: str = "pending"  # pending, accepted, rejected, expired
    response_message: Optional[str] = None
    responded_at: Optional[datetime] = None

@dataclass
class ContentVersion:
    """Version control for collaborative content"""
    version_id: str
    project_id: str
    task_id: Optional[str] = None
    created_by: str = ""
    version_number: str = "1.0"
    content_data: Dict[str, Any] = field(default_factory=dict)
    changes_description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    comments: List[Dict[str, Any]] = field(default_factory=list)

class CollaborationNotificationService:
    """Notification service for collaboration events"""
    
    def __init__(self):
        self.notification_handlers = []
    
    def add_handler(self, handler: Callable):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    async def send_notification(self, notification_type: str, 
                              recipients: List[str], 
                              data: Dict[str, Any]):
        """Send notification to recipients"""
        notification = {
            "type": notification_type,
            "recipients": recipients,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        for handler in self.notification_handlers:
            try:
                await handler(notification)
            except Exception as e:
                logger.error(f"Notification handler error: {str(e)}")

class WorkflowEngine:
    """Workflow engine for collaboration processes"""
    
    def __init__(self):
        self.workflow_definitions = {}
        self.active_workflows = {}
    
    def register_workflow(self, workflow_name: str, workflow_definition: Dict[str, Any]):
        """Register a workflow definition"""
        self.workflow_definitions[workflow_name] = workflow_definition
    
    async def start_workflow(self, workflow_name: str, project_id: str, 
                           initial_data: Dict[str, Any]) -> str:
        """Start a workflow instance"""
        workflow_id = str(uuid.uuid4())
        
        workflow_instance = {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "project_id": project_id,
            "current_step": 0,
            "data": initial_data,
            "started_at": datetime.now(),
            "status": "running"
        }
        
        self.active_workflows[workflow_id] = workflow_instance
        
        # Execute first step
        await self._execute_workflow_step(workflow_id)
        
        return workflow_id
    
    async def _execute_workflow_step(self, workflow_id: str):
        """Execute current workflow step"""
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            return
        
        workflow_def = self.workflow_definitions.get(workflow["workflow_name"])
        if not workflow_def:
            return
        
        steps = workflow_def.get("steps", [])
        current_step = workflow["current_step"]
        
        if current_step < len(steps):
            step = steps[current_step]
            
            # Simulate step execution
            logger.info(f"Executing workflow step: {step.get('name', 'Unknown')}")
            
            # Move to next step
            workflow["current_step"] += 1
            
            if workflow["current_step"] >= len(steps):
                workflow["status"] = "completed"
                workflow["completed_at"] = datetime.now()

class CollaborationService:
    """🤝 Advanced Collaboration Service for Creator Partnerships"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Collaboration Service"""
        self.config = config or {}
        self.service_id = f"collaboration_service_{int(time.time())}"
        
        # Storage
        self.projects = {}
        self.invitations = {}
        self.content_versions = {}
        
        # Services
        self.notification_service = CollaborationNotificationService()
        self.workflow_engine = WorkflowEngine()
        
        # Setup default workflows
        self._setup_default_workflows()
        
        # Statistics
        self.stats = {
            "projects_created": 0,
            "collaborations_completed": 0,
            "invitations_sent": 0,
            "invitations_accepted": 0,
            "tasks_completed": 0,
            "revenue_shared": 0.0
        }
        
        logger.info(f"🤝 Collaboration Service initialized: {self.service_id}")
    
    def _setup_default_workflows(self):
        """Setup default collaboration workflows"""
        
        # Content creation workflow
        content_workflow = {
            "name": "Content Creation Collaboration",
            "steps": [
                {"name": "Project Planning", "type": "planning", "required_roles": ["initiator"]},
                {"name": "Content Creation", "type": "creation", "required_roles": ["collaborator"]},
                {"name": "Review & Feedback", "type": "review", "required_roles": ["reviewer"]},
                {"name": "Final Approval", "type": "approval", "required_roles": ["approver"]},
                {"name": "Publishing", "type": "publishing", "required_roles": ["initiator"]}
            ]
        }
        
        # Revenue sharing workflow
        revenue_workflow = {
            "name": "Revenue Sharing Process",
            "steps": [
                {"name": "Calculate Earnings", "type": "calculation", "automated": True},
                {"name": "Distribute Payments", "type": "payment", "automated": True},
                {"name": "Send Notifications", "type": "notification", "automated": True}
            ]
        }
        
        self.workflow_engine.register_workflow("content_creation", content_workflow)
        self.workflow_engine.register_workflow("revenue_sharing", revenue_workflow)
    
    async def create_project(self, title: str, description: str,
                           collaboration_type: CollaborationType,
                           initiator_id: str,
                           requirements: Dict[str, Any] = None) -> CollaborationProject:
        """Create a new collaboration project"""
        
        project_id = str(uuid.uuid4())
        
        # Create initiator participant
        initiator = CollaborationParticipant(
            user_id=initiator_id,
            username=f"user_{initiator_id}",  # Would fetch from user service
            role=ParticipantRole.INITIATOR,
            permissions=[Permission.MANAGE, Permission.EDIT, Permission.APPROVE, Permission.DELETE],
            contribution_percentage=0.0,  # Will be set later
            revenue_share_percentage=0.0   # Will be set later
        )
        
        project = CollaborationProject(
            project_id=project_id,
            title=title,
            description=description,
            collaboration_type=collaboration_type,
            initiator_id=initiator_id,
            participants=[initiator],
            requirements=requirements or {}
        )
        
        self.projects[project_id] = project
        self.stats["projects_created"] += 1
        
        # Start project workflow
        await self.workflow_engine.start_workflow(
            "content_creation",
            project_id,
            {"project_id": project_id, "initiator_id": initiator_id}
        )
        
        logger.info(f"Collaboration project created: {project_id}")
        return project
    
    async def send_invitation(self, project_id: str, invitee_id: str,
                            proposed_role: ParticipantRole,
                            proposed_permissions: List[Permission],
                            proposed_revenue_share: float,
                            message: str) -> CollaborationInvitation:
        """Send collaboration invitation"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        invitation_id = str(uuid.uuid4())
        
        invitation = CollaborationInvitation(
            invitation_id=invitation_id,
            project_id=project_id,
            inviter_id=project.initiator_id,
            invitee_id=invitee_id,
            proposed_role=proposed_role,
            proposed_permissions=proposed_permissions,
            proposed_revenue_share=proposed_revenue_share,
            message=message
        )
        
        self.invitations[invitation_id] = invitation
        self.stats["invitations_sent"] += 1
        
        # Send notification
        await self.notification_service.send_notification(
            "collaboration_invitation",
            [invitee_id],
            {
                "invitation_id": invitation_id,
                "project_title": project.title,
                "inviter_id": project.initiator_id,
                "message": message,
                "proposed_role": proposed_role.value,
                "revenue_share": proposed_revenue_share
            }
        )
        
        logger.info(f"Collaboration invitation sent: {invitation_id}")
        return invitation
    
    async def respond_to_invitation(self, invitation_id: str, 
                                  accept: bool, 
                                  response_message: str = "") -> bool:
        """Respond to collaboration invitation"""
        
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            raise ValueError(f"Invitation {invitation_id} not found")
        
        if invitation.status != "pending":
            raise ValueError(f"Invitation {invitation_id} is not pending")
        
        invitation.status = "accepted" if accept else "rejected"
        invitation.response_message = response_message
        invitation.responded_at = datetime.now()
        
        if accept:
            # Add participant to project
            project = self.projects[invitation.project_id]
            
            participant = CollaborationParticipant(
                user_id=invitation.invitee_id,
                username=f"user_{invitation.invitee_id}",
                role=invitation.proposed_role,
                permissions=invitation.proposed_permissions,
                revenue_share_percentage=invitation.proposed_revenue_share
            )
            
            project.participants.append(participant)
            project.updated_at = datetime.now()
            
            # Activate project if it was pending
            if project.status == CollaborationStatus.PENDING:
                project.status = CollaborationStatus.ACTIVE
                project.start_date = datetime.now()
            
            self.stats["invitations_accepted"] += 1
            
            # Send notification to all participants
            participant_ids = [p.user_id for p in project.participants]
            await self.notification_service.send_notification(
                "participant_joined",
                participant_ids,
                {
                    "project_id": invitation.project_id,
                    "new_participant": invitation.invitee_id,
                    "role": invitation.proposed_role.value
                }
            )
        
        logger.info(f"Invitation {invitation_id} {'accepted' if accept else 'rejected'}")
        return True
    
    async def create_task(self, project_id: str, title: str, description: str,
                        assigned_to: str, priority: str = "medium",
                        due_date: Optional[datetime] = None,
                        dependencies: List[str] = None) -> CollaborationTask:
        """Create a task within collaboration project"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Verify assigned user is participant
        participant_ids = [p.user_id for p in project.participants]
        if assigned_to not in participant_ids:
            raise ValueError(f"User {assigned_to} is not a project participant")
        
        task_id = str(uuid.uuid4())
        
        task = CollaborationTask(
            task_id=task_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            due_date=due_date,
            dependencies=dependencies or []
        )
        
        project.tasks.append(task)
        project.updated_at = datetime.now()
        
        # Send notification to assigned user
        await self.notification_service.send_notification(
            "task_assigned",
            [assigned_to],
            {
                "task_id": task_id,
                "project_id": project_id,
                "title": title,
                "priority": priority,
                "due_date": due_date.isoformat() if due_date else None
            }
        )
        
        logger.info(f"Task created: {task_id} in project {project_id}")
        return task
    
    async def update_task_status(self, project_id: str, task_id: str, 
                               new_status: TaskStatus,
                               comment: str = "") -> bool:
        """Update task status"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        task = next((t for t in project.tasks if t.task_id == task_id), None)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        old_status = task.status
        task.status = new_status
        task.updated_at = datetime.now()
        
        if new_status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now()
            self.stats["tasks_completed"] += 1
        
        # Add comment if provided
        if comment:
            task.comments.append({
                "comment_id": str(uuid.uuid4()),
                "author": "system",  # Would be actual user in real implementation
                "content": comment,
                "timestamp": datetime.now().isoformat()
            })
        
        # Send notification to project participants
        participant_ids = [p.user_id for p in project.participants]
        await self.notification_service.send_notification(
            "task_status_updated",
            participant_ids,
            {
                "task_id": task_id,
                "project_id": project_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "task_title": task.title
            }
        )
        
        logger.info(f"Task {task_id} status updated: {old_status.value} -> {new_status.value}")
        return True
    
    async def create_content_version(self, project_id: str, 
                                   created_by: str,
                                   content_data: Dict[str, Any],
                                   changes_description: str,
                                   task_id: Optional[str] = None) -> ContentVersion:
        """Create new content version"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        version_id = str(uuid.uuid4())
        
        # Calculate version number
        existing_versions = [v for v in self.content_versions.values() 
                           if v.project_id == project_id and v.task_id == task_id]
        version_number = f"{len(existing_versions) + 1}.0"
        
        version = ContentVersion(
            version_id=version_id,
            project_id=project_id,
            task_id=task_id,
            created_by=created_by,
            version_number=version_number,
            content_data=content_data,
            changes_description=changes_description
        )
        
        self.content_versions[version_id] = version
        
        # Send notification to project participants
        participant_ids = [p.user_id for p in project.participants]
        await self.notification_service.send_notification(
            "content_version_created",
            participant_ids,
            {
                "version_id": version_id,
                "project_id": project_id,
                "version_number": version_number,
                "created_by": created_by,
                "changes_description": changes_description
            }
        )
        
        logger.info(f"Content version created: {version_id} v{version_number}")
        return version
    
    async def approve_content_version(self, version_id: str, 
                                    approved_by: str) -> bool:
        """Approve content version"""
        
        version = self.content_versions.get(version_id)
        if not version:
            raise ValueError(f"Content version {version_id} not found")
        
        project = self.projects.get(version.project_id)
        if not project:
            raise ValueError(f"Project {version.project_id} not found")
        
        # Check if approver has permission
        approver = next((p for p in project.participants if p.user_id == approved_by), None)
        if not approver or Permission.APPROVE not in approver.permissions:
            raise ValueError(f"User {approved_by} does not have approval permission")
        
        version.is_approved = True
        version.approved_by = approved_by
        version.approved_at = datetime.now()
        
        # Send notification
        participant_ids = [p.user_id for p in project.participants]
        await self.notification_service.send_notification(
            "content_version_approved",
            participant_ids,
            {
                "version_id": version_id,
                "project_id": version.project_id,
                "version_number": version.version_number,
                "approved_by": approved_by
            }
        )
        
        logger.info(f"Content version {version_id} approved by {approved_by}")
        return True
    
    async def calculate_revenue_sharing(self, project_id: str, 
                                      total_revenue: float) -> Dict[str, float]:
        """Calculate revenue sharing for project participants"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        revenue_distribution = {}
        
        for participant in project.participants:
            if participant.revenue_share_percentage > 0:
                participant_revenue = total_revenue * (participant.revenue_share_percentage / 100)
                revenue_distribution[participant.user_id] = participant_revenue
        
        # Update statistics
        self.stats["revenue_shared"] += total_revenue
        
        # Start revenue sharing workflow
        await self.workflow_engine.start_workflow(
            "revenue_sharing",
            project_id,
            {
                "project_id": project_id,
                "total_revenue": total_revenue,
                "distribution": revenue_distribution
            }
        )
        
        # Send notifications
        for participant in project.participants:
            if participant.user_id in revenue_distribution:
                await self.notification_service.send_notification(
                    "revenue_share_calculated",
                    [participant.user_id],
                    {
                        "project_id": project_id,
                        "amount": revenue_distribution[participant.user_id],
                        "total_revenue": total_revenue,
                        "share_percentage": participant.revenue_share_percentage
                    }
                )
        
        logger.info(f"Revenue sharing calculated for project {project_id}: ${total_revenue}")
        return revenue_distribution
    
    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get project analytics and insights"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Calculate task statistics
        total_tasks = len(project.tasks)
        completed_tasks = sum(1 for task in project.tasks if task.status == TaskStatus.COMPLETED)
        in_progress_tasks = sum(1 for task in project.tasks if task.status == TaskStatus.IN_PROGRESS)
        
        completion_rate = (completed_tasks / max(1, total_tasks)) * 100
        
        # Calculate collaboration metrics
        total_participants = len(project.participants)
        active_participants = sum(1 for p in project.participants if p.is_active)
        
        # Calculate timeline metrics
        project_duration = None
        if project.start_date:
            if project.status == CollaborationStatus.COMPLETED and project.end_date:
                project_duration = (project.end_date - project.start_date).days
            else:
                project_duration = (datetime.now() - project.start_date).days
        
        # Content version statistics
        project_versions = [v for v in self.content_versions.values() 
                          if v.project_id == project_id]
        approved_versions = sum(1 for v in project_versions if v.is_approved)
        
        analytics = {
            "project_id": project_id,
            "project_title": project.title,
            "collaboration_type": project.collaboration_type.value,
            "status": project.status.value,
            "task_metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "completion_rate": completion_rate
            },
            "participant_metrics": {
                "total_participants": total_participants,
                "active_participants": active_participants,
                "participant_roles": [p.role.value for p in project.participants]
            },
            "timeline_metrics": {
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "deadline": project.deadline.isoformat() if project.deadline else None,
                "project_duration_days": project_duration
            },
            "content_metrics": {
                "total_versions": len(project_versions),
                "approved_versions": approved_versions,
                "approval_rate": (approved_versions / max(1, len(project_versions))) * 100
            },
            "revenue_metrics": {
                "budget": project.budget,
                "revenue_sharing_setup": len(project.revenue_sharing_agreement) > 0
            }
        }
        
        return analytics
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        
        active_projects = sum(1 for p in self.projects.values() 
                            if p.status == CollaborationStatus.ACTIVE)
        
        total_participants = sum(len(p.participants) for p in self.projects.values())
        
        pending_invitations = sum(1 for i in self.invitations.values() 
                                if i.status == "pending")
        
        return {
            **self.stats,
            "service_id": self.service_id,
            "total_projects": len(self.projects),
            "active_projects": active_projects,
            "total_participants": total_participants,
            "pending_invitations": pending_invitations,
            "total_content_versions": len(self.content_versions),
            "active_workflows": len(self.workflow_engine.active_workflows)
        }

# Usage Example and Template Testing
async def main():
    """Example usage of Collaboration Service Template"""
    
    # Initialize the service
    service = CollaborationService()
    
    # Add notification handler
    async def notification_handler(notification):
        print(f"📧 Notification [{notification['type']}]: {notification['data']}")
    
    service.notification_service.add_handler(notification_handler)
    
    try:
        # Create a collaboration project
        project = await service.create_project(
            title="AI-Powered Music Video Creation",
            description="Collaborative project to create an AI-assisted music video",
            collaboration_type=CollaborationType.CO_CREATION,
            initiator_id="creator_123",
            requirements={
                "skills_needed": ["video_editing", "music_production", "ai_tools"],
                "timeline": "4 weeks",
                "budget": 5000.0
            }
        )
        print(f"✅ Project created: {project.project_id}")
        
        # Send invitation to collaborator
        invitation = await service.send_invitation(
            project_id=project.project_id,
            invitee_id="creator_456",
            proposed_role=ParticipantRole.COLLABORATOR,
            proposed_permissions=[Permission.VIEW, Permission.COMMENT, Permission.EDIT],
            proposed_revenue_share=40.0,
            message="Would you like to collaborate on this AI music video project?"
        )
        print(f"✅ Invitation sent: {invitation.invitation_id}")
        
        # Accept invitation
        await service.respond_to_invitation(
            invitation_id=invitation.invitation_id,
            accept=True,
            response_message="Excited to work on this project!"
        )
        print(f"✅ Invitation accepted")
        
        # Create tasks
        task1 = await service.create_task(
            project_id=project.project_id,
            title="Concept Development",
            description="Develop the creative concept and storyboard",
            assigned_to="creator_123",
            priority="high",
            due_date=datetime.now() + timedelta(days=7)
        )
        
        task2 = await service.create_task(
            project_id=project.project_id,
            title="Music Production",
            description="Create and produce the background music",
            assigned_to="creator_456",
            priority="high",
            due_date=datetime.now() + timedelta(days=14)
        )
        
        print(f"✅ Tasks created: {task1.task_id}, {task2.task_id}")
        
        # Update task status
        await service.update_task_status(
            project_id=project.project_id,
            task_id=task1.task_id,
            new_status=TaskStatus.IN_PROGRESS,
            comment="Started working on initial concept sketches"
        )
        print(f"✅ Task status updated")
        
        # Create content version
        content_version = await service.create_content_version(
            project_id=project.project_id,
            created_by="creator_123",
            content_data={
                "type": "storyboard",
                "file_url": "https://example.com/storyboard_v1.pdf",
                "description": "Initial storyboard concepts",
                "scenes": 12
            },
            changes_description="Initial storyboard draft with 12 scenes",
            task_id=task1.task_id
        )
        print(f"✅ Content version created: {content_version.version_id}")
        
        # Approve content version
        await service.approve_content_version(
            version_id=content_version.version_id,
            approved_by="creator_456"  # Collaborator has approval permission
        )
        print(f"✅ Content version approved")
        
        # Calculate revenue sharing
        revenue_distribution = await service.calculate_revenue_sharing(
            project_id=project.project_id,
            total_revenue=10000.0
        )
        print(f"✅ Revenue sharing calculated: {revenue_distribution}")
        
        # Get project analytics
        analytics = await service.get_project_analytics(project.project_id)
        print(f"\n📊 Project Analytics:")
        print(f"  Task Completion Rate: {analytics['task_metrics']['completion_rate']:.1f}%")
        print(f"  Total Participants: {analytics['participant_metrics']['total_participants']}")
        print(f"  Content Versions: {analytics['content_metrics']['total_versions']}")
        print(f"  Approval Rate: {analytics['content_metrics']['approval_rate']:.1f}%")
        
        # Get service statistics
        stats = service.get_service_stats()
        print(f"\n📈 Service Statistics:")
        print(f"  Total Projects: {stats['total_projects']}")
        print(f"  Active Projects: {stats['active_projects']}")
        print(f"  Invitations Sent: {stats['invitations_sent']}")
        print(f"  Invitations Accepted: {stats['invitations_accepted']}")
        print(f"  Tasks Completed: {stats['tasks_completed']}")
        print(f"  Revenue Shared: ${stats['revenue_shared']:,.2f}")
        
        print(f"\n✅ Collaboration Service demonstration completed!")
        
    except Exception as e:
        logger.error(f"Error in collaboration service demo: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("🤝 Collaboration Service Template demonstration completed!")