"""Project Management Database Module

Enterprise project management system for collaborative content creation.
Handles project lifecycle, task management, milestones, and team coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices
"""

from typing import List, Dict, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

Base = declarative_base()

class TaskStatus(Enum):
    """
Task status enumeration"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class MilestoneType(Enum):
    """Milestone type enumeration"""

    PROJECT_START = "project_start"
    DESIGN_COMPLETE = "design_complete"
    CONTENT_DRAFT = "content_draft"
    REVIEW_COMPLETE = "review_complete"
    APPROVAL_RECEIVED = "approval_received"
    PRODUCTION_COMPLETE = "production_complete"
    QUALITY_CHECK = "quality_check"
    PROJECT_DELIVERY = "project_delivery"
    PROJECT_COMPLETION = "project_completion"

class ResourceType(Enum):
    """Resource type enumeration"""

    HUMAN = "human"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    LOCATION = "location"
    BUDGET = "budget"
    EXTERNAL_SERVICE = "external_service"

class ProjectTask(Base):
    """
    Comprehensive task management for collaborative projects.
    Supports hierarchical tasks, dependencies, and resource allocation.
    """
    __tablename__ = 'project_tasks'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Project and hierarchy
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey('project_tasks.id'))
    task_order = Column(Integer, default=0)
    task_level = Column(Integer, default=1)  # Hierarchy level
    
    # Assignment and ownership
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    assigned_team = Column(ARRAY(UUID(as_uuid=True)))
    task_owner = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Status and priority
    status = Column(ENUM(TaskStatus), default=TaskStatus.NOT_STARTED)
    priority = Column(ENUM(TaskPriority), default=TaskPriority.MEDIUM)
    completion_percentage = Column(Float, default=0.0)
    
    # Timeline and scheduling
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    estimated_hours = Column(Float)
    actual_hours = Column(Float, default=0.0)
    
    # Dependencies and blocking
    depends_on_tasks = Column(ARRAY(UUID(as_uuid=True)))
    blocks_tasks = Column(ARRAY(UUID(as_uuid=True)))
    dependency_type = Column(String(20), default='finish_to_start')  # finish_to_start, start_to_start, etc.
    
    # Resource requirements
    required_skills = Column(ARRAY(String))
    required_resources = Column(JSONB)
    budget_allocated = Column(DECIMAL(12, 2))
    budget_spent = Column(DECIMAL(12, 2), default=0)
    
    # Task categorization
    task_category = Column(String(50))  # design, content, review, technical, etc.
    content_type = Column(String(20))   # audio, video, image, text
    deliverables = Column(JSONB)
    acceptance_criteria = Column(JSONB)
    
    # Collaboration features
    comments_count = Column(Integer, default=0)
    attachments = Column(JSONB)
    related_content = Column(ARRAY(UUID(as_uuid=True)))
    external_links = Column(JSONB)
    
    # Progress tracking
    work_log = Column(JSONB)
    status_history = Column(JSONB)
    quality_score = Column(Float)
    review_notes = Column(Text)
    
    # Automation and AI
    auto_assigned = Column(Boolean, default=False)
    ai_recommended = Column(Boolean, default=False)
    automation_rules = Column(JSONB)
    ai_insights = Column(JSONB)
    
    # Metadata and tracking
    tags = Column(ARRAY(String))
    custom_fields = Column(JSONB)
    recurrence_pattern = Column(JSONB)  # For recurring tasks
    template_id = Column(UUID(as_uuid=True))
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_task_project_status', 'project_id', 'status'),
        Index('idx_task_assigned_priority', 'assigned_to', 'priority'),
        Index('idx_task_timeline', 'planned_start_date', 'planned_end_date'),
        Index('idx_task_dependencies', 'depends_on_tasks'),
        Index('idx_task_parent_level', 'parent_task_id', 'task_level'),
    )

class ProjectMilestone(Base):
    """
    Project milestones and key deliverables tracking.
    Provides structured project progress monitoring.
    """
    __tablename__ = 'project_milestones'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    milestone_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Project association
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    milestone_type = Column(ENUM(MilestoneType), nullable=False)
    milestone_order = Column(Integer, default=0)
    
    # Timeline and targets
    target_date = Column(DateTime, nullable=False)
    actual_date = Column(DateTime)
    buffer_days = Column(Integer, default=0)
    is_critical_path = Column(Boolean, default=False)
    
    # Status and completion
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    completed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Dependencies and requirements
    depends_on_milestones = Column(ARRAY(UUID(as_uuid=True)))
    required_tasks = Column(ARRAY(UUID(as_uuid=True)))
    required_deliverables = Column(JSONB)
    success_criteria = Column(JSONB)
    
    # Quality and approval
    quality_gates = Column(JSONB)
    approval_required = Column(Boolean, default=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approval_date = Column(DateTime)
    approval_notes = Column(Text)
    
    # Impact and metrics
    business_value = Column(DECIMAL(10, 2))
    risk_level = Column(String(10), default='medium')
    impact_assessment = Column(JSONB)
    kpi_targets = Column(JSONB)
    
    # Notification and communication
    stakeholders = Column(ARRAY(UUID(as_uuid=True)))
    notification_settings = Column(JSONB)
    communication_plan = Column(JSONB)
    
    # Metadata
    tags = Column(ARRAY(String))
    custom_fields = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_milestone_project_type', 'project_id', 'milestone_type'),
        Index('idx_milestone_target_date', 'target_date'),
        Index('idx_milestone_critical_path', 'is_critical_path'),
    )

class ResourceAllocation(Base):
    """
    Resource allocation and management for projects and tasks.
    Tracks utilization, availability, and costs.
    """
    __tablename__ = 'resource_allocations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    allocation_id = Column(String(100), unique=True, nullable=False)
    
    # Resource identification
    resource_id = Column(UUID(as_uuid=True), ForeignKey('resources.id'), nullable=False)
    resource_type = Column(ENUM(ResourceType), nullable=False)
    resource_name = Column(String(255))
    
    # Allocation target
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'))
    task_id = Column(UUID(as_uuid=True), ForeignKey('project_tasks.id'))
    allocated_to = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Allocation details
    allocation_percentage = Column(Float, default=100.0)
    allocated_hours = Column(Float)
    hourly_rate = Column(DECIMAL(8, 2))
    total_cost = Column(DECIMAL(12, 2))
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    
    # Status and tracking
    status = Column(String(20), default='allocated')  # allocated, active, completed, cancelled
    utilization_rate = Column(Float, default=0.0)
    efficiency_score = Column(Float)
    
    # Constraints and requirements
    availability_constraints = Column(JSONB)
    skill_requirements = Column(JSONB)
    location_requirements = Column(JSONB)
    
    # Cost tracking
    budget_allocation = Column(DECIMAL(12, 2))
    actual_cost = Column(DECIMAL(12, 2), default=0)
    cost_variance = Column(DECIMAL(12, 2), default=0)
    
    # Metadata
    notes = Column(Text)
    custom_fields = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_allocation_resource_date', 'resource_id', 'start_date', 'end_date'),
        Index('idx_allocation_project_task', 'project_id', 'task_id'),
        Index('idx_allocation_user_period', 'allocated_to', 'start_date'),
    )

class WorkLog(Base):
    """
    Detailed work logging for time tracking and progress monitoring.
    Captures actual work performed on tasks and projects.
    """
    __tablename__ = 'work_logs'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_id = Column(String(100), unique=True, nullable=False)
    
    # Work context
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey('project_tasks.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Time tracking
    work_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    hours_logged = Column(Float, nullable=False)
    break_time_minutes = Column(Integer, default=0)
    
    # Work description
    description = Column(Text, nullable=False)
    work_category = Column(String(50))  # development, design, review, meeting, etc.
    activity_type = Column(String(50))   # coding, writing, editing, etc.
    
    # Progress and output
    progress_made = Column(Text)
    deliverables_completed = Column(JSONB)
    issues_encountered = Column(Text)
    solutions_implemented = Column(Text)
    
    # Quality and review
    quality_notes = Column(Text)
    review_required = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    review_status = Column(String(20), default='pending')
    
    # Billing and cost
    billable_hours = Column(Float)
    hourly_rate = Column(DECIMAL(8, 2))
    total_cost = Column(DECIMAL(10, 2))
    billing_status = Column(String(20), default='pending')
    
    # Location and context
    work_location = Column(String(100))
    remote_work = Column(Boolean, default=True)
    collaboration_details = Column(JSONB)
    
    # Attachments and evidence
    screenshots = Column(ARRAY(String))
    documents = Column(ARRAY(String))
    code_commits = Column(ARRAY(String))
    external_references = Column(JSONB)
    
    # Metadata
    tags = Column(ARRAY(String))
    mood_rating = Column(Integer)  # 1-5 scale for productivity tracking
    energy_level = Column(Integer)  # 1-5 scale
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_worklog_user_date', 'user_id', 'work_date'),
        Index('idx_worklog_project_task', 'project_id', 'task_id'),
        Index('idx_worklog_billing_status', 'billing_status'),
    )

@dataclass
class TaskCreationRequest:
    """
Data class for task creation requests"""
    title: str
    project_id: str
    created_by: str
    description: str = None
    assigned_to: str = None
    priority: TaskPriority = TaskPriority.MEDIUM
    planned_start_date: datetime = None
    planned_end_date: datetime = None
    estimated_hours: float = None
    parent_task_id: str = None
    required_skills: List[str] = None
    task_category: str = None
    deliverables: Dict[str, Any] = None

@dataclass
class MilestoneCreationRequest:
    """
Data class for milestone creation requests"""
    title: str
    project_id: str
    milestone_type: MilestoneType
    target_date: datetime
    description: str = None
    required_tasks: List[str] = None
    success_criteria: Dict[str, Any] = None
    approval_required: bool = True
    stakeholders: List[str] = None

class ProjectManagementEngine:
    """
    Enterprise project management engine with advanced features.
    Handles task management, milestone tracking, and resource allocation.
    """
    
    def __init__(self, db_session, redis_client: aioredis.Redis = None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.cache_ttl = 1800  # 30 minutes cache
    
    async def create_task(self, request: TaskCreationRequest) -> Optional[ProjectTask]:
        """
        Create a new project task with enterprise features.
        
        Args:
            request: Task creation request
            
        Returns:
            Created task instance
        """
        try:
            # Generate task ID
            task_id = await self._generate_task_id(request.project_id)
            
            # Calculate task level for hierarchy
            task_level = 1
            if request.parent_task_id:
                parent_task = await self.db_session.query(ProjectTask)\
                    .filter(ProjectTask.id == uuid.UUID(request.parent_task_id))\
                    .first()
                if parent_task:
                    task_level = parent_task.task_level + 1
            
            # Create task instance
            task = ProjectTask(
                task_id=task_id,
                title=request.title,
                description=request.description,
                project_id=uuid.UUID(request.project_id),
                created_by=uuid.UUID(request.created_by),
                assigned_to=uuid.UUID(request.assigned_to) if request.assigned_to else None,
                parent_task_id=uuid.UUID(request.parent_task_id) if request.parent_task_id else None,
                priority=request.priority,
                planned_start_date=request.planned_start_date,
                planned_end_date=request.planned_end_date,
                estimated_hours=request.estimated_hours,
                task_level=task_level,
                required_skills=request.required_skills or [],
                task_category=request.task_category,
                deliverables=request.deliverables or {},
                status_history=[{
                    'status': TaskStatus.NOT_STARTED.value,
                    'timestamp': datetime.utcnow().isoformat(),
                    'changed_by': request.created_by
                }],
                work_log=[],
                ai_insights=await self._generate_task_ai_insights(request)
            )
            
            # Save task
            self.db_session.add(task)
            await self.db_session.commit()
            await self.db_session.refresh(task)
            
            # Update project task counts
            await self._update_project_task_stats(request.project_id)
            
            # Cache task
            if self.redis_client:
                await self._cache_task(task)
            
            logger.info(f"Task created: {task_id}")
            
            return task
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create task: {str(e)}")
            raise
    
    async def update_task_status(
        self, 
        task_id: str, 
        new_status: TaskStatus, 
        user_id: str,
        completion_percentage: float = None,
        notes: str = None
    ) -> Optional[ProjectTask]:
        """
        Update task status with progress tracking.
        
        Args:
            task_id: Task identifier
            new_status: New task status
            user_id: User making the update
            completion_percentage: Task completion percentage
            notes: Status change notes
            
        Returns:
            Updated task instance
        """
        try:
            task = await self._get_task(task_id)
            if not task:
                return None
            
            # Store previous status for history
            previous_status = task.status
            
            # Update status
            task.status = new_status
            task.last_activity_at = datetime.utcnow()
            
            # Update completion percentage
            if completion_percentage is not None:
                task.completion_percentage = min(100.0, max(0.0, completion_percentage))
            elif new_status == TaskStatus.COMPLETED:
                task.completion_percentage = 100.0
            elif new_status == TaskStatus.NOT_STARTED:
                task.completion_percentage = 0.0
            
            # Update actual dates
            if new_status == TaskStatus.IN_PROGRESS and not task.actual_start_date:
                task.actual_start_date = datetime.utcnow()
            elif new_status == TaskStatus.COMPLETED and not task.actual_end_date:
                task.actual_end_date = datetime.utcnow()
            
            # Update status history
            status_history = task.status_history or []
            status_entry = {
                'status': new_status.value,
                'previous_status': previous_status.value,
                'timestamp': datetime.utcnow().isoformat(),
                'changed_by': user_id,
                'completion_percentage': task.completion_percentage,
                'notes': notes
            }
            status_history.append(status_entry)
            task.status_history = status_history
            
            # Auto-update dependent tasks
            await self._check_and_update_dependent_tasks(task)
            
            # Save changes
            await self.db_session.commit()
            
            # Update cache
            if self.redis_client:
                await self._cache_task(task)
            
            # Trigger notifications
            asyncio.create_task(self._notify_task_status_change(task, previous_status))
            
            logger.info(f"Task status updated: {task_id} -> {new_status.value}")
            
            return task
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update task status {task_id}: {str(e)}")
            raise
    
    async def create_milestone(self, request: MilestoneCreationRequest) -> Optional[ProjectMilestone]:
        """
        Create project milestone with tracking features.
        
        Args:
            request: Milestone creation request
            
        Returns:
            Created milestone instance
        """
        try:
            # Generate milestone ID
            milestone_id = await self._generate_milestone_id(request.project_id, request.milestone_type)
            
            # Create milestone
            milestone = ProjectMilestone(
                milestone_id=milestone_id,
                title=request.title,
                description=request.description,
                project_id=uuid.UUID(request.project_id),
                milestone_type=request.milestone_type,
                target_date=request.target_date,
                required_tasks=[uuid.UUID(tid) for tid in (request.required_tasks or [])],
                success_criteria=request.success_criteria or {},
                approval_required=request.approval_required,
                stakeholders=[uuid.UUID(sid) for sid in (request.stakeholders or [])],
                notification_settings=self._default_milestone_notifications(),
                quality_gates=self._default_quality_gates(request.milestone_type)
            )
            
            # Save milestone
            self.db_session.add(milestone)
            await self.db_session.commit()
            await self.db_session.refresh(milestone)
            
            # Update project milestone tracking
            await self._update_project_milestone_stats(request.project_id)
            
            logger.info(f"Milestone created: {milestone_id}")
            
            return milestone
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create milestone: {str(e)}")
            raise
    
    async def log_work(
        self,
        project_id: str,
        user_id: str,
        hours_logged: float,
        description: str,
        task_id: str = None,
        work_category: str = None,
        billable_hours: float = None
    ) -> Optional[WorkLog]:
        """
        Log work performed on project or task.
        
        Args:
            project_id: Project identifier
            user_id: User performing work
            hours_logged: Hours of work logged
            description: Work description
            task_id: Associated task (optional)
            work_category: Category of work
            billable_hours: Billable hours (if different from logged)
            
        Returns:
            Created work log instance
        """
        try:
            # Generate log ID
            log_id = await self._generate_work_log_id(project_id, user_id)
            
            # Create work log
            work_log = WorkLog(
                log_id=log_id,
                project_id=uuid.UUID(project_id),
                task_id=uuid.UUID(task_id) if task_id else None,
                user_id=uuid.UUID(user_id),
                work_date=datetime.utcnow().date(),
                hours_logged=hours_logged,
                billable_hours=billable_hours or hours_logged,
                description=description,
                work_category=work_category or 'general',
                start_time=datetime.utcnow() - timedelta(hours=hours_logged),
                end_time=datetime.utcnow()
            )
            
            # Save work log
            self.db_session.add(work_log)
            await self.db_session.commit()
            await self.db_session.refresh(work_log)
            
            # Update task actual hours if task specified
            if task_id:
                await self._update_task_actual_hours(task_id, hours_logged)
            
            # Update project hour tracking
            await self._update_project_hour_tracking(project_id, hours_logged)
            
            logger.info(f"Work logged: {log_id} - {hours_logged} hours")
            
            return work_log
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to log work: {str(e)}")
            raise
    
    async def get_project_dashboard(self, project_id: str) -> Dict[str, Any]:
        """
        Get comprehensive project dashboard data.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dashboard data dictionary
        """
        try:
            # Get project tasks summary
            tasks_summary = await self._get_tasks_summary(project_id)
            
            # Get milestones progress
            milestones_progress = await self._get_milestones_progress(project_id)
            
            # Get team performance
            team_performance = await self._get_team_performance(project_id)
            
            # Get resource utilization
            resource_utilization = await self._get_resource_utilization(project_id)
            
            # Get timeline analysis
            timeline_analysis = await self._get_timeline_analysis(project_id)
            
            # Get budget tracking
            budget_tracking = await self._get_budget_tracking(project_id)
            
            dashboard = {
                'project_id': project_id,
                'generated_at': datetime.utcnow().isoformat(),
                'tasks_summary': tasks_summary,
                'milestones_progress': milestones_progress,
                'team_performance': team_performance,
                'resource_utilization': resource_utilization,
                'timeline_analysis': timeline_analysis,
                'budget_tracking': budget_tracking,
                'risk_indicators': await self._get_risk_indicators(project_id),
                'ai_insights': await self._get_project_ai_insights(project_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get project dashboard for {project_id}: {str(e)}")
            return {}
    
    async def get_gantt_chart_data(self, project_id: str) -> Dict[str, Any]:
        """
        Generate Gantt chart data for project visualization.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Gantt chart data structure
        """
        try:
            # Get all project tasks with timeline
            tasks = await self.db_session.query(ProjectTask)\
                .filter(ProjectTask.project_id == uuid.UUID(project_id))\
                .order_by(ProjectTask.task_level, ProjectTask.planned_start_date)\
                .all()
            
            # Get project milestones
            milestones = await self.db_session.query(ProjectMilestone)\
                .filter(ProjectMilestone.project_id == uuid.UUID(project_id))\
                .order_by(ProjectMilestone.target_date)\
                .all()
            
            # Format tasks for Gantt chart
            gantt_tasks = []
            for task in tasks:
                gantt_task = {
                    'id': str(task.id),
                    'task_id': task.task_id,
                    'title': task.title,
                    'start_date': task.planned_start_date.isoformat() if task.planned_start_date else None,
                    'end_date': task.planned_end_date.isoformat() if task.planned_end_date else None,
                    'actual_start': task.actual_start_date.isoformat() if task.actual_start_date else None,
                    'actual_end': task.actual_end_date.isoformat() if task.actual_end_date else None,
                    'duration_days': self._calculate_task_duration(task),
                    'completion_percentage': task.completion_percentage,
                    'status': task.status.value,
                    'priority': task.priority.value,
                    'assigned_to': str(task.assigned_to) if task.assigned_to else None,
                    'parent_task': str(task.parent_task_id) if task.parent_task_id else None,
                    'dependencies': [str(dep) for dep in (task.depends_on_tasks or [])],
                    'task_level': task.task_level,
                    'critical_path': await self._is_task_on_critical_path(task)
                }
                gantt_tasks.append(gantt_task)
            
            # Format milestones
            gantt_milestones = []
            for milestone in milestones:
                gantt_milestone = {
                    'id': str(milestone.id),
                    'milestone_id': milestone.milestone_id,
                    'title': milestone.title,
                    'target_date': milestone.target_date.isoformat(),
                    'actual_date': milestone.actual_date.isoformat() if milestone.actual_date else None,
                    'type': milestone.milestone_type.value,
                    'is_completed': milestone.is_completed,
                    'completion_percentage': milestone.completion_percentage,
                    'is_critical_path': milestone.is_critical_path,
                    'dependencies': [str(dep) for dep in (milestone.depends_on_milestones or [])]
                }
                gantt_milestones.append(gantt_milestone)
            
            # Calculate project timeline
            project_start = min([t['start_date'] for t in gantt_tasks if t['start_date']], default=None)
            project_end = max([t['end_date'] for t in gantt_tasks if t['end_date']], default=None)
            
            gantt_data = {
                'project_id': project_id,
                'project_timeline': {
                    'start_date': project_start,
                    'end_date': project_end,
                    'total_duration_days': self._calculate_date_difference(project_start, project_end) if project_start and project_end else 0
                },
                'tasks': gantt_tasks,
                'milestones': gantt_milestones,
                'critical_path': await self._get_critical_path(project_id),
                'resource_allocation': await self._get_gantt_resource_data(project_id),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return gantt_data
            
        except Exception as e:
            logger.error(f"Failed to generate Gantt chart data for {project_id}: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _generate_task_id(self, project_id: str) -> str:
        """Generate unique task identifier"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        task_count = await self.db_session.query(ProjectTask)\
            .filter(ProjectTask.project_id == uuid.UUID(project_id))\
            .count()
        
        return f"TASK-{timestamp}-{task_count + 1:04d}"
    
    async def _generate_milestone_id(self, project_id: str, milestone_type: MilestoneType) -> str:
        """Generate unique milestone identifier"""
        type_code = milestone_type.value.upper()[:3]
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        
        return f"MILE-{type_code}-{timestamp}-{str(uuid.uuid4())[:8]}"
    
    async def _generate_work_log_id(self, project_id: str, user_id: str) -> str:
        """Generate unique work log identifier"""
        date_str = datetime.utcnow().strftime('%Y%m%d')
        user_short = str(user_id)[:8]
        
        return f"WORK-{date_str}-{user_short}-{str(uuid.uuid4())[:8]}"
    
    async def _get_task(self, task_id: str) -> Optional[ProjectTask]:
        """Get task by ID with caching"""
        try:
            # Check cache first
            if self.redis_client:
                cached_data = await self.redis_client.get(f"task:{task_id}")
                if cached_data:
                    return self._deserialize_task(json.loads(cached_data))
            
            # Query database
            task = await self.db_session.query(ProjectTask)\
                .filter(ProjectTask.task_id == task_id)\
                .first()
            
            # Cache result
            if task and self.redis_client:
                await self._cache_task(task)
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {str(e)}")
            return None
    
    async def _generate_task_ai_insights(self, request: TaskCreationRequest) -> Dict[str, Any]:
        """Generate AI insights for new task"""
        insights = {
            'complexity_score': self._estimate_task_complexity(request),
            'recommended_assignee': await self._suggest_task_assignee(request),
            'estimated_duration': self._calculate_duration_estimate(request),
            'risk_factors': self._identify_task_risks(request),
            'optimization_suggestions': self._generate_optimization_suggestions(request)
        }
        
        return insights
    
    def _estimate_task_complexity(self, request: TaskCreationRequest) -> float:
        """
Estimate task complexity based on various factors"""
        complexity = 1.0  # Base complexity
        
        # Adjust based on description length
        if request.description and len(request.description) > 500:
            complexity += 0.5
        
        # Adjust based on required skills
        if request.required_skills and len(request.required_skills) > 3:
            complexity += 0.3
        
        # Adjust based on estimated hours
        if request.estimated_hours:
            if request.estimated_hours > 40:
                complexity += 1.0
            elif request.estimated_hours > 16:
                complexity += 0.5
        
        return min(5.0, complexity)  # Cap at 5.0
    
    def _calculate_task_duration(self, task: ProjectTask) -> int:
        """
Calculate task duration in days"""
        if task.planned_start_date and task.planned_end_date:
            return (task.planned_end_date - task.planned_start_date).days
        elif task.estimated_hours:
            return max(1, int(task.estimated_hours / 8))  # Assume 8 hours per day
        return 1
    
    def _calculate_date_difference(self, start_date: str, end_date: str) -> int:
        """
Calculate difference between two date strings"""
        if not start_date or not end_date:
            return 0
        
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        return (end - start).days
    
    async def _cache_task(self, task: ProjectTask):
        """
Cache task data in Redis"""
        try:
            task_data = {
                'id': str(task.id),
                'task_id': task.task_id,
                'title': task.title,
                'status': task.status.value,
                'priority': task.priority.value,
                'completion_percentage': task.completion_percentage,
                'updated_at': task.updated_at.isoformat()
            }
            
            await self.redis_client.setex(
                f"task:{task.task_id}",
                self.cache_ttl,
                json.dumps(task_data)
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache task {task.task_id}: {str(e)}")
    
    # Additional helper methods would be implemented here for:
    # - Critical path calculation
    # - Resource utilization analysis
    # - Team performance metrics
    # - Risk assessment
    # - AI-powered insights
    # - Notification systems

# Export main classes
__all__ = [
    'ProjectTask',
    'ProjectMilestone',
    'ResourceAllocation',
    'WorkLog',
    'TaskStatus',
    'TaskPriority',
    'MilestoneType',
    'ResourceType',
    'TaskCreationRequest',
    'MilestoneCreationRequest',
    'ProjectManagementEngine'
]
