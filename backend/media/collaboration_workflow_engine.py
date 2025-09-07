"""Collaboration Workflow Engine - Creator Collaboration System

Enterprise-grade collaboration workflow system for managing creator partnerships,
project coordination, and collaborative content creation workflows.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
import hashlib
import uuid

# Workflow and task management imports with graceful fallbacks
try:
    from celery import Celery
    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False
    logging.warning("Celery not available - using basic task management")

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory state management")


class WorkflowStatus(Enum):
    """Workflow status types"""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PAUSED = "paused"


class TaskStatus(Enum):
    """Individual task status types"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class CollaboratorRole(Enum):
    """Collaborator role types"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class WorkflowType(Enum):
    """Types of collaboration workflows"""
    CONTENT_CREATION = "content_creation"
    CAMPAIGN = "campaign"
    BRAND_PARTNERSHIP = "brand_partnership"
    CHALLENGE = "challenge"
    COLLABORATION = "collaboration"
    REVIEW_CYCLE = "review_cycle"
    PRODUCTION = "production"


@dataclass
class Collaborator:
    """Collaborator information"""
    user_id: str
    username: str
    email: str
    role: CollaboratorRole
    permissions: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    availability: Dict[str, Any] = field(default_factory=dict)
    rating: float = 0.0
    joined_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    contribution_score: float = 0.0


@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    task_id: str
    title: str
    description: str
    assignee_id: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = 5  # 1-10 scale
    estimated_hours: float = 1.0
    actual_hours: float = 0.0
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    
    # Timeline
    due_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Deliverables
    deliverables: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    
    # Feedback and review
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    approval_required: bool = False
    approved_by: Optional[str] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowTemplate:
    """Template for creating workflows"""
    template_id: str
    name: str
    description: str
    workflow_type: WorkflowType
    estimated_duration: int  # days
    
    # Template tasks
    task_templates: List[Dict[str, Any]] = field(default_factory=list)
    role_requirements: List[CollaboratorRole] = field(default_factory=list)
    
    # Configuration
    default_permissions: Dict[CollaboratorRole, List[str]] = field(default_factory=dict)
    milestone_templates: List[Dict[str, Any]] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    usage_count: int = 0


@dataclass
class WorkflowMilestone:
    """Milestone within a workflow"""
    milestone_id: str
    title: str
    description: str
    due_date: datetime
    completion_criteria: List[str] = field(default_factory=list)
    related_tasks: List[str] = field(default_factory=list)
    is_critical: bool = False
    completed: bool = False
    completed_at: Optional[datetime] = None


@dataclass
class CollaborationWorkflow:
    """Main collaboration workflow"""
    workflow_id: str
    title: str
    description: str
    workflow_type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.DRAFT
    
    # Participants
    owner_id: str
    collaborators: List[Collaborator] = field(default_factory=list)
    
    # Structure
    tasks: List[WorkflowTask] = field(default_factory=list)
    milestones: List[WorkflowMilestone] = field(default_factory=list)
    
    # Timeline
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_duration: int = 7  # days
    
    # Progress tracking
    progress_percentage: float = 0.0
    completed_tasks: int = 0
    total_tasks: int = 0
    
    # Content and deliverables
    deliverables: List[str] = field(default_factory=list)
    shared_assets: List[str] = field(default_factory=list)
    
    # Configuration
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    notification_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Analytics
    analytics: Dict[str, Any] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowEvent:
    """Event in workflow history"""
    event_id: str
    workflow_id: str
    event_type: str
    user_id: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CollaborationWorkflowEngine:
    """Enterprise collaboration workflow management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.workflows: Dict[str, CollaborationWorkflow] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.events: List[WorkflowEvent] = []
        
        # Task scheduling
        self.task_scheduler = None
        if HAS_CELERY:
            self._initialize_celery()
        
        # Real-time state management
        self.redis_client = None
        if HAS_REDIS and self.config.get("redis_url"):
            self._initialize_redis()
        
        # Workflow statistics
        self.workflow_stats = {
            "total_workflows": 0,
            "active_workflows": 0,
            "completed_workflows": 0,
            "total_collaborators": 0,
            "average_completion_time": 0.0,
            "success_rate": 0.0
        }
        
        # Initialize default templates
        self._initialize_default_templates()
        
        # Start background workers
        self._start_background_workers()
        
        self.logger.info("Collaboration Workflow Engine initialized")
    
    def _initialize_celery(self) -> None:
        """Initialize Celery for task scheduling"""
        try:
            self.task_scheduler = Celery(
                'collaboration_workflows',
                broker=self.config.get('celery_broker', 'redis://localhost:6379/0'),
                backend=self.config.get('celery_backend', 'redis://localhost:6379/0')
            )
            self.logger.info("Celery task scheduler initialized")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Celery: {e}")
    
    def _initialize_redis(self) -> None:
        """Initialize Redis for real-time state management"""
        try:
            import redis
            self.redis_client = redis.from_url(self.config["redis_url"])
            self.redis_client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}")
    
    def _initialize_default_templates(self) -> None:
        """Initialize default workflow templates"""
        
        # Content Creation Template
        content_template = WorkflowTemplate(
            template_id="content_creation_basic",
            name="Basic Content Creation",
            description="Standard workflow for collaborative content creation",
            workflow_type=WorkflowType.CONTENT_CREATION,
            estimated_duration=7,
            task_templates=[
                {
                    "title": "Content Planning",
                    "description": "Plan content theme, style, and requirements",
                    "estimated_hours": 2.0,
                    "required_role": CollaboratorRole.ADMIN
                },
                {
                    "title": "Content Creation",
                    "description": "Create initial content draft",
                    "estimated_hours": 8.0,
                    "required_role": CollaboratorRole.CONTRIBUTOR
                },
                {
                    "title": "Review & Feedback",
                    "description": "Review content and provide feedback",
                    "estimated_hours": 2.0,
                    "required_role": CollaboratorRole.REVIEWER
                },
                {
                    "title": "Content Revision",
                    "description": "Revise content based on feedback",
                    "estimated_hours": 4.0,
                    "required_role": CollaboratorRole.EDITOR
                },
                {
                    "title": "Final Approval",
                    "description": "Final approval for publication",
                    "estimated_hours": 1.0,
                    "required_role": CollaboratorRole.ADMIN
                }
            ],
            role_requirements=[
                CollaboratorRole.ADMIN,
                CollaboratorRole.CONTRIBUTOR,
                CollaboratorRole.REVIEWER,
                CollaboratorRole.EDITOR
            ]
        )
        
        # Campaign Template
        campaign_template = WorkflowTemplate(
            template_id="campaign_standard",
            name="Marketing Campaign",
            description="Standard marketing campaign workflow",
            workflow_type=WorkflowType.CAMPAIGN,
            estimated_duration=14,
            task_templates=[
                {
                    "title": "Campaign Strategy",
                    "description": "Define campaign goals and strategy",
                    "estimated_hours": 4.0,
                    "required_role": CollaboratorRole.ADMIN
                },
                {
                    "title": "Content Planning",
                    "description": "Plan all campaign content",
                    "estimated_hours": 6.0,
                    "required_role": CollaboratorRole.EDITOR
                },
                {
                    "title": "Asset Creation",
                    "description": "Create campaign assets",
                    "estimated_hours": 20.0,
                    "required_role": CollaboratorRole.CONTRIBUTOR
                },
                {
                    "title": "Review Cycle",
                    "description": "Review and refine campaign materials",
                    "estimated_hours": 8.0,
                    "required_role": CollaboratorRole.REVIEWER
                },
                {
                    "title": "Campaign Launch",
                    "description": "Execute campaign launch",
                    "estimated_hours": 4.0,
                    "required_role": CollaboratorRole.ADMIN
                }
            ]
        )
        
        # Brand Partnership Template
        partnership_template = WorkflowTemplate(
            template_id="brand_partnership",
            name="Brand Partnership",
            description="Workflow for brand collaboration projects",
            workflow_type=WorkflowType.BRAND_PARTNERSHIP,
            estimated_duration=21,
            task_templates=[
                {
                    "title": "Partnership Negotiation",
                    "description": "Negotiate partnership terms",
                    "estimated_hours": 6.0,
                    "required_role": CollaboratorRole.ADMIN
                },
                {
                    "title": "Content Brief",
                    "description": "Create detailed content brief",
                    "estimated_hours": 3.0,
                    "required_role": CollaboratorRole.ADMIN
                },
                {
                    "title": "Content Creation",
                    "description": "Create partnership content",
                    "estimated_hours": 16.0,
                    "required_role": CollaboratorRole.CONTRIBUTOR
                },
                {
                    "title": "Brand Review",
                    "description": "Brand approval process",
                    "estimated_hours": 4.0,
                    "required_role": CollaboratorRole.REVIEWER
                },
                {
                    "title": "Content Publication",
                    "description": "Publish approved content",
                    "estimated_hours": 2.0,
                    "required_role": CollaboratorRole.ADMIN
                },
                {
                    "title": "Performance Tracking",
                    "description": "Track and report performance",
                    "estimated_hours": 4.0,
                    "required_role": CollaboratorRole.ADMIN
                }
            ]
        )
        
        self.templates = {
            content_template.template_id: content_template,
            campaign_template.template_id: campaign_template,
            partnership_template.template_id: partnership_template
        }
    
    def _start_background_workers(self) -> None:
        """Start background worker tasks"""
        
        # Workflow monitoring worker
        asyncio.create_task(self._workflow_monitoring_worker())
        
        # Deadline checking worker
        asyncio.create_task(self._deadline_monitoring_worker())
        
        # Analytics update worker
        asyncio.create_task(self._analytics_update_worker())
    
    async def _workflow_monitoring_worker(self) -> None:
        """Background worker for monitoring workflow progress"""
        
        while True:
            try:
                # Update workflow progress
                for workflow in self.workflows.values():
                    if workflow.status == WorkflowStatus.ACTIVE:
                        await self._update_workflow_progress(workflow)
                
                # Check for completed workflows
                await self._check_workflow_completion()
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in workflow monitoring worker: {str(e)}")
                await asyncio.sleep(60)
    
    async def _deadline_monitoring_worker(self) -> None:
        """Background worker for monitoring deadlines"""
        
        while True:
            try:
                current_time = datetime.now()
                
                # Check for approaching deadlines
                for workflow in self.workflows.values():
                    if workflow.status == WorkflowStatus.ACTIVE:
                        # Check workflow deadline
                        if (workflow.end_date and 
                            workflow.end_date - current_time <= timedelta(days=1)):
                            await self._send_deadline_notification(workflow)
                        
                        # Check task deadlines
                        for task in workflow.tasks:
                            if (task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED] and
                                task.due_date and 
                                task.due_date - current_time <= timedelta(hours=24)):
                                await self._send_task_deadline_notification(workflow, task)
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Error in deadline monitoring worker: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _analytics_update_worker(self) -> None:
        """Background worker for updating analytics"""
        
        while True:
            try:
                # Update workflow analytics
                for workflow in self.workflows.values():
                    await self._update_workflow_analytics(workflow)
                
                # Update global statistics
                await self._update_global_statistics()
                
                # Sleep for 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                self.logger.error(f"Error in analytics update worker: {str(e)}")
                await asyncio.sleep(1800)
    
    async def create_workflow(
        self,
        title: str,
        description: str,
        workflow_type: WorkflowType,
        owner_id: str,
        template_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Create a new collaboration workflow"""
        
        workflow_id = str(uuid.uuid4())
        
        workflow = CollaborationWorkflow(
            workflow_id=workflow_id,
            title=title,
            description=description,
            workflow_type=workflow_type,
            owner_id=owner_id,
            start_date=kwargs.get("start_date"),
            end_date=kwargs.get("end_date"),
            estimated_duration=kwargs.get("estimated_duration", 7)
        )
        
        # Apply template if specified
        if template_id and template_id in self.templates:
            await self._apply_template(workflow, self.templates[template_id])
        
        # Add owner as admin collaborator
        owner_collaborator = Collaborator(
            user_id=owner_id,
            username=kwargs.get("owner_username", f"user_{owner_id}"),
            email=kwargs.get("owner_email", f"{owner_id}@example.com"),
            role=CollaboratorRole.OWNER
        )
        workflow.collaborators.append(owner_collaborator)
        
        # Store workflow
        self.workflows[workflow_id] = workflow
        
        # Log event
        await self._log_workflow_event(
            workflow_id, "workflow_created", owner_id,
            f"Workflow '{title}' created", {"template_id": template_id}
        )
        
        # Update statistics
        self.workflow_stats["total_workflows"] += 1
        
        self.logger.info(f"Created workflow {workflow_id}: {title}")
        
        return workflow_id
    
    async def _apply_template(self, workflow: CollaborationWorkflow, template: WorkflowTemplate) -> None:
        """Apply a workflow template to a workflow"""
        
        workflow.estimated_duration = template.estimated_duration
        
        # Create tasks from template
        for i, task_template in enumerate(template.task_templates):
            task = WorkflowTask(
                task_id=str(uuid.uuid4()),
                title=task_template["title"],
                description=task_template["description"],
                estimated_hours=task_template.get("estimated_hours", 1.0),
                priority=task_template.get("priority", 5)
            )
            
            # Set due date based on position and estimated duration
            if workflow.start_date:
                days_offset = (i + 1) * (workflow.estimated_duration / len(template.task_templates))
                task.due_date = workflow.start_date + timedelta(days=days_offset)
            
            workflow.tasks.append(task)
        
        workflow.total_tasks = len(workflow.tasks)
        
        # Update template usage
        template.usage_count += 1
    
    async def add_collaborator(
        self,
        workflow_id: str,
        user_id: str,
        username: str,
        email: str,
        role: CollaboratorRole,
        added_by: str,
        **kwargs
    ) -> bool:
        """Add a collaborator to a workflow"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        # Check if user is already a collaborator
        for collaborator in workflow.collaborators:
            if collaborator.user_id == user_id:
                return False
        
        collaborator = Collaborator(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=kwargs.get("permissions", []),
            skills=kwargs.get("skills", []),
            availability=kwargs.get("availability", {}),
            rating=kwargs.get("rating", 0.0)
        )
        
        workflow.collaborators.append(collaborator)
        workflow.updated_at = datetime.now()
        
        # Log event
        await self._log_workflow_event(
            workflow_id, "collaborator_added", added_by,
            f"Added {username} as {role.value}", {"user_id": user_id, "role": role.value}
        )
        
        # Update statistics
        self.workflow_stats["total_collaborators"] += 1
        
        self.logger.info(f"Added collaborator {username} to workflow {workflow_id}")
        
        return True
    
    async def create_task(
        self,
        workflow_id: str,
        title: str,
        description: str,
        created_by: str,
        **kwargs
    ) -> Optional[str]:
        """Create a new task in a workflow"""
        
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        task = WorkflowTask(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            assignee_id=kwargs.get("assignee_id"),
            priority=kwargs.get("priority", 5),
            estimated_hours=kwargs.get("estimated_hours", 1.0),
            due_date=kwargs.get("due_date"),
            dependencies=kwargs.get("dependencies", []),
            approval_required=kwargs.get("approval_required", False)
        )
        
        workflow.tasks.append(task)
        workflow.total_tasks = len(workflow.tasks)
        workflow.updated_at = datetime.now()
        
        # Log event
        await self._log_workflow_event(
            workflow_id, "task_created", created_by,
            f"Created task '{title}'", {"task_id": task.task_id}
        )
        
        self.logger.info(f"Created task {task.task_id} in workflow {workflow_id}")
        
        return task.task_id
    
    async def update_task_status(
        self,
        workflow_id: str,
        task_id: str,
        new_status: TaskStatus,
        updated_by: str,
        **kwargs
    ) -> bool:
        """Update the status of a task"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        task = None
        
        for t in workflow.tasks:
            if t.task_id == task_id:
                task = t
                break
        
        if not task:
            return False
        
        old_status = task.status
        task.status = new_status
        task.updated_at = datetime.now()
        
        # Update timestamps
        if new_status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.now()
        elif new_status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.now()
        
        # Add feedback if provided
        if kwargs.get("feedback"):
            task.feedback.append({
                "user_id": updated_by,
                "message": kwargs["feedback"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Update workflow progress
        await self._update_workflow_progress(workflow)
        
        # Log event
        await self._log_workflow_event(
            workflow_id, "task_status_updated", updated_by,
            f"Updated task '{task.title}' from {old_status.value} to {new_status.value}",
            {"task_id": task_id, "old_status": old_status.value, "new_status": new_status.value}
        )
        
        self.logger.info(f"Updated task {task_id} status to {new_status.value}")
        
        return True
    
    async def assign_task(
        self,
        workflow_id: str,
        task_id: str,
        assignee_id: str,
        assigned_by: str
    ) -> bool:
        """Assign a task to a collaborator"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        # Check if assignee is a collaborator
        assignee = None
        for collaborator in workflow.collaborators:
            if collaborator.user_id == assignee_id:
                assignee = collaborator
                break
        
        if not assignee:
            return False
        
        # Find and update task
        for task in workflow.tasks:
            if task.task_id == task_id:
                task.assignee_id = assignee_id
                task.updated_at = datetime.now()
                
                # Log event
                await self._log_workflow_event(
                    workflow_id, "task_assigned", assigned_by,
                    f"Assigned task '{task.title}' to {assignee.username}",
                    {"task_id": task_id, "assignee_id": assignee_id}
                )
                
                self.logger.info(f"Assigned task {task_id} to {assignee.username}")
                return True
        
        return False
    
    async def start_workflow(self, workflow_id: str, started_by: str) -> bool:
        """Start a workflow"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.DRAFT:
            return False
        
        workflow.status = WorkflowStatus.ACTIVE
        workflow.start_date = datetime.now()
        workflow.updated_at = datetime.now()
        
        # Update statistics
        self.workflow_stats["active_workflows"] += 1
        
        # Log event
        await self._log_workflow_event(
            workflow_id, "workflow_started", started_by,
            f"Workflow '{workflow.title}' started"
        )
        
        self.logger.info(f"Started workflow {workflow_id}")
        
        return True
    
    async def complete_workflow(self, workflow_id: str, completed_by: str) -> bool:
        """Complete a workflow"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.ACTIVE:
            return False
        
        # Check if all critical tasks are completed
        critical_tasks_completed = all(
            task.status == TaskStatus.COMPLETED
            for task in workflow.tasks
            if task.priority >= 8  # High priority tasks
        )
        
        if not critical_tasks_completed:
            return False
        
        workflow.status = WorkflowStatus.COMPLETED
        workflow.end_date = datetime.now()
        workflow.updated_at = datetime.now()
        workflow.progress_percentage = 100.0
        
        # Update statistics
        self.workflow_stats["active_workflows"] -= 1
        self.workflow_stats["completed_workflows"] += 1
        
        # Calculate completion time
        if workflow.start_date:
            completion_time = (workflow.end_date - workflow.start_date).days
            self._update_average_completion_time(completion_time)
        
        # Log event
        await self._log_workflow_event(
            workflow_id, "workflow_completed", completed_by,
            f"Workflow '{workflow.title}' completed"
        )
        
        self.logger.info(f"Completed workflow {workflow_id}")
        
        return True
    
    async def _update_workflow_progress(self, workflow: CollaborationWorkflow) -> None:
        """Update workflow progress based on task completion"""
        
        if not workflow.tasks:
            workflow.progress_percentage = 0.0
            return
        
        completed_tasks = sum(1 for task in workflow.tasks if task.status == TaskStatus.COMPLETED)
        workflow.completed_tasks = completed_tasks
        workflow.progress_percentage = (completed_tasks / len(workflow.tasks)) * 100
        
        # Check if workflow should be automatically completed
        if workflow.progress_percentage == 100.0 and workflow.status == WorkflowStatus.ACTIVE:
            workflow.status = WorkflowStatus.REVIEW
    
    async def _check_workflow_completion(self) -> None:
        """Check for workflows that should be completed"""
        
        for workflow in self.workflows.values():
            if workflow.status == WorkflowStatus.REVIEW:
                # Auto-complete if all tasks are done
                if workflow.progress_percentage == 100.0:
                    await self.complete_workflow(workflow.workflow_id, workflow.owner_id)
    
    async def _send_deadline_notification(self, workflow: CollaborationWorkflow) -> None:
        """Send notification for approaching workflow deadline"""
        
        # This would integrate with notification system
        self.logger.info(f"Deadline approaching for workflow {workflow.workflow_id}: {workflow.title}")
    
    async def _send_task_deadline_notification(
        self,
        workflow: CollaborationWorkflow,
        task: WorkflowTask
    ) -> None:
        """Send notification for approaching task deadline"""
        
        # This would integrate with notification system
        self.logger.info(f"Task deadline approaching: {task.title} in workflow {workflow.workflow_id}")
    
    async def _update_workflow_analytics(self, workflow: CollaborationWorkflow) -> None:
        """Update analytics for a workflow"""
        
        analytics = {
            "task_completion_rate": workflow.progress_percentage / 100,
            "collaborator_count": len(workflow.collaborators),
            "average_task_duration": 0.0,
            "on_time_completion_rate": 0.0,
            "total_hours_logged": 0.0
        }
        
        # Calculate task metrics
        completed_tasks = [task for task in workflow.tasks if task.status == TaskStatus.COMPLETED]
        
        if completed_tasks:
            total_duration = sum(
                (task.completed_at - task.started_at).total_seconds() / 3600
                for task in completed_tasks
                if task.started_at and task.completed_at
            )
            analytics["average_task_duration"] = total_duration / len(completed_tasks)
            
            on_time_tasks = sum(
                1 for task in completed_tasks
                if task.due_date and task.completed_at and task.completed_at <= task.due_date
            )
            analytics["on_time_completion_rate"] = on_time_tasks / len(completed_tasks)
        
        # Calculate total hours
        analytics["total_hours_logged"] = sum(task.actual_hours for task in workflow.tasks)
        
        workflow.analytics = analytics
    
    async def _update_global_statistics(self) -> None:
        """Update global workflow statistics"""
        
        total_workflows = len(self.workflows)
        active_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE)
        completed_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.COMPLETED)
        
        self.workflow_stats.update({
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "completed_workflows": completed_workflows,
            "success_rate": completed_workflows / max(1, total_workflows)
        })
    
    def _update_average_completion_time(self, completion_time: int) -> None:
        """Update average completion time"""
        
        current_avg = self.workflow_stats["average_completion_time"]
        completed_count = self.workflow_stats["completed_workflows"]
        
        if completed_count <= 1:
            self.workflow_stats["average_completion_time"] = completion_time
        else:
            self.workflow_stats["average_completion_time"] = (
                (current_avg * (completed_count - 1) + completion_time) / completed_count
            )
    
    async def _log_workflow_event(
        self,
        workflow_id: str,
        event_type: str,
        user_id: str,
        description: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a workflow event"""
        
        event = WorkflowEvent(
            event_id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            event_type=event_type,
            user_id=user_id,
            description=description,
            data=data or {}
        )
        
        self.events.append(event)
        
        # Publish to Redis if available
        if self.redis_client:
            try:
                event_data = {
                    "workflow_id": workflow_id,
                    "event_type": event_type,
                    "user_id": user_id,
                    "description": description,
                    "timestamp": event.timestamp.isoformat(),
                    "data": data or {}
                }
                self.redis_client.publish(f"workflow_events:{workflow_id}", json.dumps(event_data))
            except Exception as e:
                self.logger.error(f"Failed to publish event to Redis: {e}")
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow details"""
        
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            "workflow_id": workflow.workflow_id,
            "title": workflow.title,
            "description": workflow.description,
            "workflow_type": workflow.workflow_type.value,
            "status": workflow.status.value,
            "owner_id": workflow.owner_id,
            "collaborators": [
                {
                    "user_id": c.user_id,
                    "username": c.username,
                    "role": c.role.value,
                    "contribution_score": c.contribution_score,
                    "last_active": c.last_active.isoformat() if c.last_active else None
                } for c in workflow.collaborators
            ],
            "tasks": [
                {
                    "task_id": t.task_id,
                    "title": t.title,
                    "status": t.status.value,
                    "assignee_id": t.assignee_id,
                    "priority": t.priority,
                    "estimated_hours": t.estimated_hours,
                    "actual_hours": t.actual_hours,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None
                } for t in workflow.tasks
            ],
            "progress_percentage": workflow.progress_percentage,
            "start_date": workflow.start_date.isoformat() if workflow.start_date else None,
            "end_date": workflow.end_date.isoformat() if workflow.end_date else None,
            "analytics": workflow.analytics,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }
    
    def get_user_workflows(self, user_id: str) -> List[Dict[str, Any]]:
        """Get workflows for a specific user"""
        
        user_workflows = []
        
        for workflow in self.workflows.values():
            # Check if user is a collaborator
            is_collaborator = any(c.user_id == user_id for c in workflow.collaborators)
            
            if is_collaborator:
                user_workflows.append({
                    "workflow_id": workflow.workflow_id,
                    "title": workflow.title,
                    "status": workflow.status.value,
                    "progress_percentage": workflow.progress_percentage,
                    "role": next(
                        c.role.value for c in workflow.collaborators 
                        if c.user_id == user_id
                    ),
                    "updated_at": workflow.updated_at.isoformat()
                })
        
        return user_workflows
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates"""
        
        return [
            {
                "template_id": t.template_id,
                "name": t.name,
                "description": t.description,
                "workflow_type": t.workflow_type.value,
                "estimated_duration": t.estimated_duration,
                "task_count": len(t.task_templates),
                "usage_count": t.usage_count
            } for t in self.templates.values()
        ]
    
    def get_workflow_events(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events for a workflow"""
        
        workflow_events = [
            event for event in self.events
            if event.workflow_id == workflow_id
        ]
        
        # Sort by timestamp descending
        workflow_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "user_id": e.user_id,
                "description": e.description,
                "data": e.data,
                "timestamp": e.timestamp.isoformat()
            } for e in workflow_events[:limit]
        ]
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get workflow system statistics"""
        
        return {
            **self.workflow_stats,
            "templates_available": len(self.templates),
            "events_logged": len(self.events),
            "has_celery": HAS_CELERY,
            "has_redis": self.redis_client is not None
        }


# Global instance for easy access
_collaboration_workflow_engine = None

def get_collaboration_workflow_engine(config: Optional[Dict[str, Any]] = None) -> CollaborationWorkflowEngine:
    """Get or create global collaboration workflow engine instance"""
    global _collaboration_workflow_engine
    
    if _collaboration_workflow_engine is None:
        _collaboration_workflow_engine = CollaborationWorkflowEngine(config)
    
    return _collaboration_workflow_engine


# Example usage and testing
if __name__ == "__main__":
    async def example_usage():
        """Example usage of the Collaboration Workflow Engine"""
        
        # Initialize the system
        engine = get_collaboration_workflow_engine()
        
        # Create a new workflow
        workflow_id = await engine.create_workflow(
            title="Summer Campaign 2025",
            description="Collaborative campaign for summer products",
            workflow_type=WorkflowType.CAMPAIGN,
            owner_id="user_123",
            template_id="campaign_standard",
            owner_username="alice",
            owner_email="alice@example.com"
        )
        
        print(f"Created workflow: {workflow_id}")
        
        # Add collaborators
        await engine.add_collaborator(
            workflow_id=workflow_id,
            user_id="user_456",
            username="bob",
            email="bob@example.com",
            role=CollaboratorRole.CONTRIBUTOR,
            added_by="user_123"
        )
        
        await engine.add_collaborator(
            workflow_id=workflow_id,
            user_id="user_789",
            username="charlie",
            email="charlie@example.com",
            role=CollaboratorRole.REVIEWER,
            added_by="user_123"
        )
        
        # Start the workflow
        await engine.start_workflow(workflow_id, "user_123")
        
        # Create a custom task
        task_id = await engine.create_task(
            workflow_id=workflow_id,
            title="Create promotional video",
            description="Create a 30-second promotional video for the campaign",
            created_by="user_123",
            assignee_id="user_456",
            estimated_hours=8.0,
            priority=8
        )
        
        print(f"Created task: {task_id}")
        
        # Update task status
        await engine.update_task_status(
            workflow_id=workflow_id,
            task_id=task_id,
            new_status=TaskStatus.IN_PROGRESS,
            updated_by="user_456"
        )
        
        # Get workflow details
        workflow_details = engine.get_workflow(workflow_id)
        if workflow_details:
            print(f"\nWorkflow Progress: {workflow_details['progress_percentage']:.1f}%")
            print(f"Collaborators: {len(workflow_details['collaborators'])}")
            print(f"Tasks: {len(workflow_details['tasks'])}")
        
        # Get workflow events
        events = engine.get_workflow_events(workflow_id, limit=10)
        print(f"\nRecent Events:")
        for event in events[:3]:
            print(f"- {event['description']} by {event['user_id']}")
        
        # Get statistics
        stats = engine.get_workflow_statistics()
        print(f"\nSystem Statistics:")
        print(f"- Total Workflows: {stats['total_workflows']}")
        print(f"- Active Workflows: {stats['active_workflows']}")
        print(f"- Success Rate: {stats['success_rate']:.2%}")
    
    # Run example if this file is executed directly
    asyncio.run(example_usage())