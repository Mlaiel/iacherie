"""🎯 COLLABORATION MANAGER - Project Collaboration Management System
===============================================================

Developed by: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved - Unauthorized use is strictly prohibited

⚠️  LEGAL WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any attempt to steal, copy, or reproduce this concept, idea, or code
without explicit written authorization from Fahed Mlaiel is strictly forbidden
and will result in immediate legal action under German and international law.

Enterprise collaboration project management system for creator partnerships.
Handles project lifecycle, task coordination, milestone tracking, and deliverable management.

Features:
- Project Creation & Setup
- Task Assignment & Tracking
- Milestone Management
- Real-time Collaboration Tools
- File Sharing & Version Control
- Progress Monitoring
- Quality Assurance
- Project Analytics
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    """Project status enumeration"""    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    REVISION_REQUIRED = "revision_required"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    OVERDUE = "overdue"

class TaskStatus(Enum):
    """Task status enumeration"""    TODO = "todo"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class MilestoneType(Enum):
    """Milestone type enumeration"""    PLANNING = "planning"
    DEVELOPMENT = "development"
    REVIEW = "review"
    DELIVERY = "delivery"
    PAYMENT = "payment"
    COMPLETION = "completion"

@dataclass
class ProjectTask:
    """Individual project task"""    task_id: str
    title: str
    description: str
    assigned_to: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    progress_percentage: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ProjectMilestone:
    """Project milestone"""    milestone_id: str
    title: str
    description: str
    milestone_type: MilestoneType
    due_date: datetime
    completion_criteria: List[str]
    deliverables: List[str]
    payment_percentage: Optional[float] = None
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    tasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class CollaborationProject:
    """Core collaboration project entity"""    project_id: str
    title: str
    description: str
    partnership_id: str
    project_type: str
    status: ProjectStatus = ProjectStatus.DRAFT
    participants: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    currency: str = "EUR"
    tasks: List[ProjectTask] = field(default_factory=list)
    milestones: List[ProjectMilestone] = field(default_factory=list)
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class CollaborationManager:
    """Advanced collaboration project management system"""    
    def __init__(self, db_session, file_storage, notification_service, analytics_tracker):
        self.db_session = db_session
        self.file_storage = file_storage
        self.notification_service = notification_service
        self.analytics_tracker = analytics_tracker
        
    async def create_project(
        self,
        partnership_id: str,
        title: str,
        description: str,
        project_type: str,
        created_by: str,
        participants: List[str],
        budget: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> CollaborationProject:
        """Create a new collaboration project"""        try:
            logger.info(f"Creating collaboration project: {title}")
            
            # Validate partnership exists
            await self._validate_partnership(partnership_id)
            
            # Validate participants
            await self._validate_participants(participants)
            
            # Generate project ID
            project_id = str(uuid.uuid4())
            
            # Create project
            project = CollaborationProject(
                project_id=project_id,
                title=title,
                description=description,
                partnership_id=partnership_id,
                project_type=project_type,
                participants=participants,
                budget=budget,
                start_date=start_date,
                end_date=end_date,
                created_by=created_by
            )
            
            # Save to database
            await self._save_project(project)
            
            # Create initial project structure
            await self._setup_initial_project_structure(project)
            
            # Notify participants
            await self.notification_service.send_project_created(
                participants, project
            )
            
            # Track analytics
            await self.analytics_tracker.track_project_creation(project)
            
            logger.info(f"Project created successfully: {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise
            
    async def add_task(
        self,
        project_id: str,
        title: str,
        description: str,
        assigned_to: str,
        user_id: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        estimated_hours: Optional[float] = None,
        dependencies: Optional[List[str]] = None
    ) -> ProjectTask:
        """Add a new task to project"""        try:
            # Get project and validate access
            project = await self._get_project(project_id)
            await self._validate_project_access(project, user_id)
            
            # Validate assignee
            if assigned_to not in project.participants:
                raise ValueError("Task assignee must be project participant")
                
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Create task
            task = ProjectTask(
                task_id=task_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                priority=priority,
                due_date=due_date,
                estimated_hours=estimated_hours,
                dependencies=dependencies or []
            )
            
            # Add to project
            project.tasks.append(task)
            project.updated_at = datetime.utcnow()
            
            # Save project
            await self._update_project(project)
            
            # Notify assignee
            await self.notification_service.send_task_assigned(
                assigned_to, project, task
            )
            
            # Track analytics
            await self.analytics_tracker.track_task_creation(project, task)
            
            logger.info(f"Task added to project {project_id}: {task_id}")
            return task
            
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            raise
            
    async def update_task_status(
        self,
        project_id: str,
        task_id: str,
        new_status: TaskStatus,
        user_id: str,
        progress_percentage: Optional[float] = None,
        comment: Optional[str] = None
    ) -> ProjectTask:
        """Update task status and progress"""        try:
            # Get project and task
            project = await self._get_project(project_id)
            task = await self._get_task(project, task_id)
            
            # Validate user can update task
            await self._validate_task_update_access(project, task, user_id)
            
            old_status = task.status
            task.status = new_status
            task.updated_at = datetime.utcnow()
            
            if progress_percentage is not None:
                task.progress_percentage = progress_percentage
                
            # Add comment if provided
            if comment:
                task.comments.append({
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'comment': comment,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'status_update'
                })
                
            # Update completion date if completed
            if new_status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
                task.progress_percentage = 100.0
                
            # Save project
            await self._update_project(project)
            
            # Handle status-specific actions
            await self._handle_task_status_change(project, task, old_status, new_status)
            
            # Notify relevant users
            await self.notification_service.send_task_status_update(
                project, task, old_status, new_status
            )
            
            # Track analytics
            await self.analytics_tracker.track_task_status_change(
                project, task, old_status, new_status
            )
            
            logger.info(f"Task {task_id} status updated to {new_status}")
            return task
            
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")
            raise
            
    async def add_milestone(
        self,
        project_id: str,
        title: str,
        description: str,
        milestone_type: MilestoneType,
        due_date: datetime,
        completion_criteria: List[str],
        deliverables: List[str],
        user_id: str,
        payment_percentage: Optional[float] = None
    ) -> ProjectMilestone:
        """Add milestone to project"""        try:
            # Get project and validate access
            project = await self._get_project(project_id)
            await self._validate_project_access(project, user_id)
            
            # Generate milestone ID
            milestone_id = str(uuid.uuid4())
            
            # Create milestone
            milestone = ProjectMilestone(
                milestone_id=milestone_id,
                title=title,
                description=description,
                milestone_type=milestone_type,
                due_date=due_date,
                completion_criteria=completion_criteria,
                deliverables=deliverables,
                payment_percentage=payment_percentage
            )
            
            # Add to project
            project.milestones.append(milestone)
            project.updated_at = datetime.utcnow()
            
            # Save project
            await self._update_project(project)
            
            # Notify participants
            await self.notification_service.send_milestone_added(
                project.participants, project, milestone
            )
            
            # Track analytics
            await self.analytics_tracker.track_milestone_creation(project, milestone)
            
            logger.info(f"Milestone added to project {project_id}: {milestone_id}")
            return milestone
            
        except Exception as e:
            logger.error(f"Error adding milestone: {str(e)}")
            raise
            
    async def complete_milestone(
        self,
        project_id: str,
        milestone_id: str,
        user_id: str,
        completion_notes: Optional[str] = None
    ) -> ProjectMilestone:
        """Mark milestone as completed"""        try:
            # Get project and milestone
            project = await self._get_project(project_id)
            milestone = await self._get_milestone(project, milestone_id)
            
            # Validate completion criteria
            can_complete = await self._validate_milestone_completion(project, milestone)
            if not can_complete['allowed']:
                raise ValueError(f"Milestone cannot be completed: {can_complete['reason']}")
                
            # Mark as completed
            milestone.is_completed = True
            milestone.completed_date = datetime.utcnow()
            
            if completion_notes:
                milestone.deliverables.append({
                    'type': 'completion_notes',
                    'content': completion_notes,
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_id': user_id
                })
                
            project.updated_at = datetime.utcnow()
            
            # Save project
            await self._update_project(project)
            
            # Handle milestone completion actions
            await self._handle_milestone_completion(project, milestone)
            
            # Notify participants
            await self.notification_service.send_milestone_completed(
                project.participants, project, milestone
            )
            
            # Track analytics
            await self.analytics_tracker.track_milestone_completion(project, milestone)
            
            logger.info(f"Milestone completed: {milestone_id}")
            return milestone
            
        except Exception as e:
            logger.error(f"Error completing milestone: {str(e)}")
            raise
            
    async def upload_deliverable(
        self,
        project_id: str,
        user_id: str,
        file_data: bytes,
        filename: str,
        deliverable_type: str,
        milestone_id: Optional[str] = None,
        task_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload project deliverable"""        try:
            # Get project and validate access
            project = await self._get_project(project_id)
            await self._validate_project_access(project, user_id)
            
            # Generate file ID
            file_id = str(uuid.uuid4())
            
            # Upload file to storage
            file_path = f"projects/{project_id}/deliverables/{file_id}_{filename}"
            storage_url = await self.file_storage.upload_file(
                file_data, file_path, content_type=self._get_content_type(filename)
            )
            
            # Create deliverable record
            deliverable = {
                'id': file_id,
                'filename': filename,
                'original_filename': filename,
                'storage_url': storage_url,
                'file_path': file_path,
                'deliverable_type': deliverable_type,
                'description': description,
                'milestone_id': milestone_id,
                'task_id': task_id,
                'uploaded_by': user_id,
                'upload_date': datetime.utcnow().isoformat(),
                'file_size': len(file_data),
                'version': 1,
                'is_current': True
            }
            
            # Add to project deliverables
            project.deliverables.append(deliverable)
            project.updated_at = datetime.utcnow()
            
            # Save project
            await self._update_project(project)
            
            # Notify participants
            await self.notification_service.send_deliverable_uploaded(
                project.participants, project, deliverable
            )
            
            # Track analytics
            await self.analytics_tracker.track_deliverable_upload(project, deliverable)
            
            logger.info(f"Deliverable uploaded to project {project_id}: {file_id}")
            return deliverable
            
        except Exception as e:
            logger.error(f"Error uploading deliverable: {str(e)}")
            raise
            
    async def get_project_analytics(
        self,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive project analytics"""        try:
            # Get project and validate access
            project = await self._get_project(project_id)
            await self._validate_project_access(project, user_id)
            
            analytics = {
                'project_overview': await self._get_project_overview(project),
                'progress_metrics': await self._calculate_progress_metrics(project),
                'task_analytics': await self._analyze_tasks(project),
                'milestone_analytics': await self._analyze_milestones(project),
                'team_performance': await self._analyze_team_performance(project),
                'timeline_analysis': await self._analyze_timeline(project),
                'budget_analysis': await self._analyze_budget(project),
                'quality_metrics': await self._analyze_quality_metrics(project),
                'collaboration_insights': await self._analyze_collaboration_patterns(project)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting project analytics: {str(e)}")
            raise
            
    async def update_project_status(
        self,
        project_id: str,
        new_status: ProjectStatus,
        user_id: str,
        reason: Optional[str] = None
    ) -> CollaborationProject:
        """Update project status"""        try:
            # Get project and validate access
            project = await self._get_project(project_id)
            await self._validate_project_access(project, user_id)
            
            old_status = project.status
            project.status = new_status
            project.updated_at = datetime.utcnow()
            
            # Add metadata about status change
            if 'status_history' not in project.metadata:
                project.metadata['status_history'] = []
                
            project.metadata['status_history'].append({
                'from_status': old_status.value,
                'to_status': new_status.value,
                'changed_by': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'reason': reason
            })
            
            # Save project
            await self._update_project(project)
            
            # Handle status-specific actions
            await self._handle_project_status_change(project, old_status, new_status)
            
            # Notify participants
            await self.notification_service.send_project_status_update(
                project.participants, project, old_status, new_status
            )
            
            # Track analytics
            await self.analytics_tracker.track_project_status_change(
                project, old_status, new_status
            )
            
            logger.info(f"Project {project_id} status updated to {new_status}")
            return project
            
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            raise
            
    # Helper methods
    async def _validate_partnership(self, partnership_id: str) -> None:
        """Validate partnership exists and is active"""        query = "SELECT id FROM partnerships WHERE partnership_id = %s AND status = 'active'"
        result = await self.db_session.execute(query, (partnership_id,))
        if not result.fetchone():
            raise ValueError("Partnership not found or not active")
            
    async def _validate_participants(self, participant_ids: List[str]) -> None:
        """Validate all participants exist and are active"""        query = "SELECT id FROM creators WHERE id = ANY(%s) AND is_active = true"
        result = await self.db_session.execute(query, (participant_ids,))
        found_ids = [row['id'] for row in result.fetchall()]
        
        missing_ids = set(participant_ids) - set(found_ids)
        if missing_ids:
            raise ValueError(f"Participants not found or inactive: {missing_ids}")
            
    async def _save_project(self, project: CollaborationProject) -> None:
        """Save project to database"""        query = """        INSERT INTO collaboration_projects (
            project_id, title, description, partnership_id, project_type,
            status, participants, start_date, end_date, budget, currency,
            tasks, milestones, deliverables, tags, metadata, created_by,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """        
        await self.db_session.execute(query, (
            project.project_id,
            project.title,
            project.description,
            project.partnership_id,
            project.project_type,
            project.status.value,
            json.dumps(project.participants),
            project.start_date,
            project.end_date,
            project.budget,
            project.currency,
            json.dumps([task.__dict__ for task in project.tasks], default=str),
            json.dumps([milestone.__dict__ for milestone in project.milestones], default=str),
            json.dumps(project.deliverables, default=str),
            json.dumps(project.tags),
            json.dumps(project.metadata, default=str),
            project.created_by,
            project.created_at,
            project.updated_at
        ))
        
    async def _get_project(self, project_id: str) -> CollaborationProject:
        """Get project by ID"""        query = "SELECT * FROM collaboration_projects WHERE project_id = %s"
        result = await self.db_session.execute(query, (project_id,))
        row = result.fetchone()
        
        if not row:
            raise ValueError(f"Project not found: {project_id}")
            
        return await self._row_to_project(row)
        
    async def _row_to_project(self, row: Dict[str, Any]) -> CollaborationProject:
        """Convert database row to CollaborationProject"""        # Convert JSON fields back to objects
        tasks_data = json.loads(row['tasks']) if row['tasks'] else []
        milestones_data = json.loads(row['milestones']) if row['milestones'] else []
        
        tasks = [ProjectTask(**task_data) for task_data in tasks_data]
        milestones = [ProjectMilestone(**milestone_data) for milestone_data in milestones_data]
        
        project = CollaborationProject(
            project_id=row['project_id'],
            title=row['title'],
            description=row['description'],
            partnership_id=row['partnership_id'],
            project_type=row['project_type'],
            status=ProjectStatus(row['status']),
            participants=json.loads(row['participants']),
            start_date=row['start_date'],
            end_date=row['end_date'],
            budget=row['budget'],
            currency=row['currency'],
            tasks=tasks,
            milestones=milestones,
            deliverables=json.loads(row['deliverables']) if row['deliverables'] else [],
            tags=json.loads(row['tags']) if row['tags'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            created_by=row['created_by'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
        return project
        
    async def _validate_project_access(self, project: CollaborationProject, user_id: str) -> None:
        """Validate user has access to project"""        if user_id not in project.participants:
            raise ValueError("User does not have access to this project")
            
    async def _get_task(self, project: CollaborationProject, task_id: str) -> ProjectTask:
        """Get task from project"""        for task in project.tasks:
            if task.task_id == task_id:
                return task
        raise ValueError(f"Task not found: {task_id}")
        
    async def _get_milestone(self, project: CollaborationProject, milestone_id: str) -> ProjectMilestone:
        """Get milestone from project"""        for milestone in project.milestones:
            if milestone.milestone_id == milestone_id:
                return milestone
        raise ValueError(f"Milestone not found: {milestone_id}")
        
    # Advanced project structure and management methods
    async def _setup_initial_project_structure(self, project: CollaborationProject) -> None:
        """Set up initial project structure with templates and workflows"""        try:
            # Create project workspace structure
            await self._create_project_workspace(project)
            
            # Set up project templates based on type
            template = await self._get_project_template(project.project_type)
            if template:
                await self._apply_project_template(project, template)
                
            # Initialize project channels and communication
            await self._setup_project_communication(project)
            
            # Create default milestones if none exist
            if not project.milestones:
                await self._create_default_milestones(project)
                
            # Set up project permissions and roles
            await self._configure_project_permissions(project)
            
            logger.info(f"Project structure initialized for {project.project_id}")
            
        except Exception as e:
            logger.error(f"Error setting up project structure: {str(e)}")
            raise
            
    async def _update_project(self, project: CollaborationProject) -> None:
        """Update project in database with full synchronization"""        try:
            query = """            UPDATE collaboration_projects SET
                title = %s, description = %s, status = %s, participants = %s,
                start_date = %s, end_date = %s, budget = %s, currency = %s,
                tasks = %s, milestones = %s, deliverables = %s, tags = %s,
                metadata = %s, updated_at = %s
            WHERE project_id = %s
            """            
            await self.db_session.execute(query, (
                project.title,
                project.description,
                project.status.value,
                json.dumps(project.participants),
                project.start_date,
                project.end_date,
                project.budget,
                project.currency,
                json.dumps([self._task_to_dict(task) for task in project.tasks], default=str),
                json.dumps([self._milestone_to_dict(milestone) for milestone in project.milestones], default=str),
                json.dumps(project.deliverables, default=str),
                json.dumps(project.tags),
                json.dumps(project.metadata, default=str),
                project.updated_at,
                project.project_id
            ))
            
            # Update search index
            await self._update_search_index(project)
            
            # Sync with external systems
            await self._sync_external_systems(project)
            
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            raise
            
    async def _validate_task_update_access(self, project: CollaborationProject, task: ProjectTask, user_id: str) -> None:
        """Validate user can update task with comprehensive permission checking"""        try:
            # Check if user is project participant
            if user_id not in project.participants:
                raise ValueError("User is not a project participant")
                
            # Check if user is task assignee or project manager
            if task.assigned_to != user_id:
                # Check if user has manager role
                user_role = await self._get_user_project_role(project.project_id, user_id)
                if user_role not in ['manager', 'admin', 'project_lead']:
                    raise ValueError("User does not have permission to update this task")
                    
            # Check if task is in editable state
            if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                raise ValueError("Cannot update completed or cancelled tasks")
                
            # Check project status
            if project.status in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]:
                raise ValueError("Cannot update tasks in completed or cancelled projects")
                
        except Exception as e:
            logger.error(f"Error validating task update access: {str(e)}")
            raise
            
    async def _handle_task_status_change(self, project: CollaborationProject, task: ProjectTask, old_status: TaskStatus, new_status: TaskStatus) -> None:
        """Handle task status change with automated workflows"""        try:
            # Update task dependencies
            if new_status == TaskStatus.COMPLETED:
                await self._unlock_dependent_tasks(project, task)
                
            # Check for milestone completion
            await self._check_milestone_auto_completion(project, task)
            
            # Update project progress
            project_progress = await self._calculate_project_progress(project)
            project.metadata['progress_percentage'] = project_progress
            
            # Handle status-specific actions
            if new_status == TaskStatus.BLOCKED:
                await self._handle_blocked_task(project, task)
            elif new_status == TaskStatus.UNDER_REVIEW:
                await self._handle_task_review(project, task)
            elif new_status == TaskStatus.COMPLETED:
                await self._handle_completed_task(project, task)
                
            # Update project timeline if needed
            await self._update_project_timeline(project)
            
        except Exception as e:
            logger.error(f"Error handling task status change: {str(e)}")
            raise
            
    async def _validate_milestone_completion(self, project: CollaborationProject, milestone: ProjectMilestone) -> Dict[str, Any]:
        """Validate milestone can be completed with comprehensive checks"""        try:
            validation_result = {'allowed': True, 'reason': None, 'issues': []}
            
            # Check if all required tasks are completed
            milestone_tasks = [task for task in project.tasks if task.task_id in milestone.tasks]
            incomplete_tasks = [task for task in milestone_tasks if task.status != TaskStatus.COMPLETED]
            
            if incomplete_tasks:
                validation_result['allowed'] = False
                validation_result['reason'] = f"Incomplete tasks: {len(incomplete_tasks)}"
                validation_result['issues'].extend([
                    f"Task '{task.title}' is not completed" for task in incomplete_tasks
                ])
                
            # Check if all deliverables are uploaded
            required_deliverables = set(milestone.deliverables)
            uploaded_deliverables = {
                d['deliverable_type'] for d in project.deliverables 
                if d.get('milestone_id') == milestone.milestone_id
            }
            
            missing_deliverables = required_deliverables - uploaded_deliverables
            if missing_deliverables:
                validation_result['allowed'] = False
                validation_result['reason'] = f"Missing deliverables: {len(missing_deliverables)}"
                validation_result['issues'].extend([
                    f"Deliverable '{deliverable}' not uploaded" for deliverable in missing_deliverables
                ])
                
            # Check milestone dependencies
            dependent_milestones = [
                m for m in project.milestones 
                if milestone.milestone_id in m.dependencies and not m.is_completed
            ]
            
            if dependent_milestones:
                validation_result['issues'].append(
                    f"Dependent milestones will be affected: {len(dependent_milestones)}"
                )
                
            # Check if milestone is past due
            if milestone.due_date < datetime.utcnow():
                validation_result['issues'].append("Milestone is past due date")
                
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating milestone completion: {str(e)}")
            return {'allowed': False, 'reason': f"Validation error: {str(e)}", 'issues': []}
            
    async def _handle_milestone_completion(self, project: CollaborationProject, milestone: ProjectMilestone) -> None:
        """Handle milestone completion with automated processes"""        try:
            # Process milestone payment if applicable
            if milestone.payment_percentage:
                await self._process_milestone_payment(project, milestone)
                
            # Update project timeline and dependencies
            await self._update_milestone_dependencies(project, milestone)
            
            # Generate completion certificates/documents
            await self._generate_milestone_completion_documents(project, milestone)
            
            # Check if project can be auto-completed
            await self._check_project_auto_completion(project)
            
            # Update analytics
            await self.analytics_tracker.track_milestone_completion(project, milestone)
            
            # Send completion notifications
            await self._send_milestone_completion_notifications(project, milestone)
            
        except Exception as e:
            logger.error(f"Error handling milestone completion: {str(e)}")
            raise
            
    async def _handle_project_status_change(self, project: CollaborationProject, old_status: ProjectStatus, new_status: ProjectStatus) -> None:
        """Handle project status change with comprehensive workflow management"""        try:
            # Handle status-specific workflows
            if new_status == ProjectStatus.APPROVED:
                await self._activate_project(project)
            elif new_status == ProjectStatus.IN_PROGRESS:
                await self._start_project_execution(project)
            elif new_status == ProjectStatus.COMPLETED:
                await self._complete_project(project)
            elif new_status == ProjectStatus.CANCELLED:
                await self._cancel_project(project)
            elif new_status == ProjectStatus.ON_HOLD:
                await self._pause_project(project)
                
            # Update project metrics
            await self._update_project_metrics(project, old_status, new_status)
            
            # Handle financial implications
            await self._handle_financial_status_change(project, old_status, new_status)
            
            # Update team schedules and availability
            await self._update_team_schedules(project, new_status)
            
        except Exception as e:
            logger.error(f"Error handling project status change: {str(e)}")
            raise
        
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename"""        # Implementation would map file extensions to content types
        return "application/octet-stream"
        
    # Advanced analytics and project intelligence methods
    async def _get_project_overview(self, project: CollaborationProject) -> Dict[str, Any]:
        """Generate comprehensive project overview"""        try:
            overview = {
                'basic_info': {
                    'project_id': project.project_id,
                    'title': project.title,
                    'status': project.status.value,
                    'type': project.project_type,
                    'created_at': project.created_at.isoformat(),
                    'duration_days': (datetime.utcnow() - project.created_at).days,
                    'participants_count': len(project.participants),
                    'budget': project.budget,
                    'currency': project.currency
                },
                'current_phase': await self._determine_current_phase(project),
                'health_score': await self._calculate_project_health_score(project),
                'risk_assessment': await self._assess_project_risks(project),
                'completion_prediction': await self._predict_completion_date(project)
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Error generating project overview: {str(e)}")
            return {'error': str(e)}
            
    async def _calculate_progress_metrics(self, project: CollaborationProject) -> Dict[str, Any]:
        """Calculate detailed progress metrics"""        try:
            total_tasks = len(project.tasks)
            completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
            in_progress_tasks = len([t for t in project.tasks if t.status == TaskStatus.IN_PROGRESS])
            blocked_tasks = len([t for t in project.tasks if t.status == TaskStatus.BLOCKED])
            
            total_milestones = len(project.milestones)
            completed_milestones = len([m for m in project.milestones if m.is_completed])
            
            # Calculate time-based progress
            if project.start_date and project.end_date:
                total_duration = (project.end_date - project.start_date).days
                elapsed_days = (datetime.utcnow() - project.start_date).days
                time_progress = min(100, max(0, (elapsed_days / total_duration) * 100))
            else:
                time_progress = 0
                
            # Calculate effort-based progress
            total_estimated_hours = sum(t.estimated_hours or 0 for t in project.tasks)
            completed_hours = sum(
                t.actual_hours or t.estimated_hours or 0 
                for t in project.tasks if t.status == TaskStatus.COMPLETED
            )
            effort_progress = (completed_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0
            
            # Calculate weighted progress
            weighted_progress = (
                (completed_tasks / total_tasks * 40) if total_tasks > 0 else 0 +
                (completed_milestones / total_milestones * 30) if total_milestones > 0 else 0 +
                time_progress * 0.15 +
                effort_progress * 0.15
            )
            
            return {
                'overall_progress': min(100, weighted_progress),
                'task_progress': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'in_progress': in_progress_tasks,
                    'blocked': blocked_tasks,
                    'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                'milestone_progress': {
                    'total': total_milestones,
                    'completed': completed_milestones,
                    'completion_rate': (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
                },
                'time_progress': time_progress,
                'effort_progress': effort_progress,
                'velocity_metrics': await self._calculate_velocity_metrics(project),
                'burndown_data': await self._generate_burndown_data(project)
            }
            
        except Exception as e:
            logger.error(f"Error calculating progress metrics: {str(e)}")
            return {}
            
    async def _analyze_tasks(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze task performance and patterns"""        try:
            tasks_by_status = {}
            for status in TaskStatus:
                tasks_by_status[status.value] = len([t for t in project.tasks if t.status == status])
                
            tasks_by_priority = {}
            for priority in TaskPriority:
                tasks_by_priority[priority.value] = len([t for t in project.tasks if t.priority == priority])
                
            tasks_by_assignee = {}
            for task in project.tasks:
                assignee = task.assigned_to
                if assignee not in tasks_by_assignee:
                    tasks_by_assignee[assignee] = {'total': 0, 'completed': 0, 'overdue': 0}
                tasks_by_assignee[assignee]['total'] += 1
                if task.status == TaskStatus.COMPLETED:
                    tasks_by_assignee[assignee]['completed'] += 1
                if task.due_date and task.due_date < datetime.utcnow() and task.status != TaskStatus.COMPLETED:
                    tasks_by_assignee[assignee]['overdue'] += 1
                    
            # Calculate average completion time
            completed_tasks = [t for t in project.tasks if t.status == TaskStatus.COMPLETED]
            avg_completion_time = 0
            if completed_tasks:
                completion_times = []
                for task in completed_tasks:
                    # This would need task completion timestamps
                    if 'completed_at' in task.metadata:
                        completion_time = datetime.fromisoformat(task.metadata['completed_at']) - task.created_at
                        completion_times.append(completion_time.days)
                if completion_times:
                    avg_completion_time = sum(completion_times) / len(completion_times)
                    
            return {
                'task_distribution': {
                    'by_status': tasks_by_status,
                    'by_priority': tasks_by_priority,
                    'by_assignee': tasks_by_assignee
                },
                'performance_metrics': {
                    'average_completion_time_days': avg_completion_time,
                    'completion_rate': len(completed_tasks) / len(project.tasks) * 100 if project.tasks else 0,
                    'overdue_tasks': len([t for t in project.tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != TaskStatus.COMPLETED]),
                    'blocked_tasks': len([t for t in project.tasks if t.status == TaskStatus.BLOCKED])
                },
                'productivity_insights': await self._generate_productivity_insights(project),
                'bottleneck_analysis': await self._analyze_task_bottlenecks(project)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tasks: {str(e)}")
            return {}
            
    async def _analyze_milestones(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze milestone performance and patterns"""        try:
            total_milestones = len(project.milestones)
            completed_milestones = [m for m in project.milestones if m.is_completed]
            overdue_milestones = [
                m for m in project.milestones 
                if m.due_date < datetime.utcnow() and not m.is_completed
            ]
            
            # Calculate milestone completion timeline
            milestone_timeline = []
            for milestone in project.milestones:
                timeline_entry = {
                    'milestone_id': milestone.milestone_id,
                    'title': milestone.title,
                    'type': milestone.milestone_type.value,
                    'due_date': milestone.due_date.isoformat(),
                    'is_completed': milestone.is_completed,
                    'completion_date': milestone.completed_date.isoformat() if milestone.completed_date else None,
                    'days_early_late': None
                }
                
                if milestone.is_completed and milestone.completed_date:
                    days_diff = (milestone.due_date - milestone.completed_date).days
                    timeline_entry['days_early_late'] = days_diff
                    
                milestone_timeline.append(timeline_entry)
                
            # Calculate payment-related metrics
            payment_milestones = [m for m in project.milestones if m.payment_percentage]
            total_payment_percentage = sum(m.payment_percentage or 0 for m in payment_milestones)
            completed_payment_percentage = sum(
                m.payment_percentage or 0 for m in payment_milestones if m.is_completed
            )
            
            return {
                'milestone_summary': {
                    'total': total_milestones,
                    'completed': len(completed_milestones),
                    'overdue': len(overdue_milestones),
                    'completion_rate': len(completed_milestones) / total_milestones * 100 if total_milestones > 0 else 0
                },
                'timeline_analysis': milestone_timeline,
                'payment_progress': {
                    'total_payment_percentage': total_payment_percentage,
                    'completed_payment_percentage': completed_payment_percentage,
                    'payment_completion_rate': completed_payment_percentage / total_payment_percentage * 100 if total_payment_percentage > 0 else 0
                },
                'milestone_types': {
                    milestone_type.value: len([m for m in project.milestones if m.milestone_type == milestone_type])
                    for milestone_type in MilestoneType
                },
                'performance_trends': await self._analyze_milestone_trends(project)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing milestones: {str(e)}")
            return {}
            
    async def _analyze_team_performance(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze team performance and collaboration patterns"""        try:
            team_metrics = {}
            
            for participant_id in project.participants:
                participant_tasks = [t for t in project.tasks if t.assigned_to == participant_id]
                completed_tasks = [t for t in participant_tasks if t.status == TaskStatus.COMPLETED]
                
                # Calculate individual metrics
                individual_metrics = {
                    'total_tasks': len(participant_tasks),
                    'completed_tasks': len(completed_tasks),
                    'completion_rate': len(completed_tasks) / len(participant_tasks) * 100 if participant_tasks else 0,
                    'average_task_priority': self._calculate_average_priority(participant_tasks),
                    'on_time_completion': await self._calculate_on_time_completion(participant_tasks),
                    'collaboration_score': await self._calculate_collaboration_score(participant_id, project),
                    'deliverables_contributed': len([d for d in project.deliverables if d.get('uploaded_by') == participant_id])
                }
                
                team_metrics[participant_id] = individual_metrics
                
            # Calculate team-level metrics
            total_tasks = len(project.tasks)
            total_completed = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
            
            team_summary = {
                'overall_completion_rate': total_completed / total_tasks * 100 if total_tasks > 0 else 0,
                'team_velocity': await self._calculate_team_velocity(project),
                'collaboration_effectiveness': await self._measure_collaboration_effectiveness(project),
                'communication_frequency': await self._analyze_communication_patterns(project),
                'workload_distribution': await self._analyze_workload_distribution(project)
            }
            
            return {
                'individual_performance': team_metrics,
                'team_summary': team_summary,
                'performance_rankings': await self._generate_performance_rankings(team_metrics),
                'improvement_suggestions': await self._generate_improvement_suggestions(project, team_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing team performance: {str(e)}")
            return {}
            
    async def _analyze_timeline(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze project timeline and schedule performance"""        try:
            timeline_analysis = {
                'project_duration': {
                    'planned_days': (project.end_date - project.start_date).days if project.start_date and project.end_date else None,
                    'elapsed_days': (datetime.utcnow() - project.start_date).days if project.start_date else None,
                    'remaining_days': (project.end_date - datetime.utcnow()).days if project.end_date else None
                },
                'schedule_adherence': await self._calculate_schedule_adherence(project),
                'critical_path': await self._identify_critical_path(project),
                'schedule_risks': await self._identify_schedule_risks(project),
                'timeline_predictions': await self._predict_timeline_outcomes(project)
            }
            
            return timeline_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing timeline: {str(e)}")
            return {}
            
    async def _analyze_budget(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze budget utilization and financial performance"""        try:
            if not project.budget:
                return {'message': 'No budget defined for project'}
                
            # Calculate actual spending (this would integrate with expense tracking)
            actual_spending = await self._calculate_actual_spending(project)
            budget_utilization = actual_spending / project.budget * 100 if project.budget > 0 else 0
            
            # Calculate milestone-based budget allocation
            milestone_budget_allocation = {}
            for milestone in project.milestones:
                if milestone.payment_percentage:
                    milestone_budget_allocation[milestone.milestone_id] = {
                        'allocated_amount': project.budget * (milestone.payment_percentage / 100),
                        'is_completed': milestone.is_completed,
                        'payment_status': 'paid' if milestone.is_completed else 'pending'
                    }
                    
            return {
                'budget_overview': {
                    'total_budget': project.budget,
                    'currency': project.currency,
                    'actual_spending': actual_spending,
                    'remaining_budget': project.budget - actual_spending,
                    'utilization_percentage': budget_utilization
                },
                'milestone_allocations': milestone_budget_allocation,
                'spending_forecast': await self._forecast_spending(project),
                'cost_efficiency': await self._analyze_cost_efficiency(project),
                'budget_risks': await self._identify_budget_risks(project)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing budget: {str(e)}")
            return {}
            
    async def _analyze_quality_metrics(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze project quality metrics and deliverable standards"""        try:
            quality_metrics = {
                'deliverable_quality': await self._assess_deliverable_quality(project),
                'code_review_metrics': await self._analyze_code_reviews(project),
                'client_satisfaction': await self._measure_client_satisfaction(project),
                'defect_rate': await self._calculate_defect_rate(project),
                'rework_frequency': await self._calculate_rework_frequency(project)
            }
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing quality metrics: {str(e)}")
            return {}
            
    async def _analyze_collaboration_patterns(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze collaboration patterns and team dynamics"""        try:
            collaboration_insights = {
                'communication_network': await self._analyze_communication_network(project),
                'knowledge_sharing': await self._measure_knowledge_sharing(project),
                'decision_making_patterns': await self._analyze_decision_patterns(project),
                'conflict_resolution': await self._analyze_conflict_resolution(project),
                'synergy_opportunities': await self._identify_synergy_opportunities(project)
            }
            
            return collaboration_insights
            
        except Exception as e:
            logger.error(f"Error analyzing collaboration patterns: {str(e)}")
            return {}
    
    # Advanced helper methods for project management
    def _get_content_type(self, filename: str) -> str:
        """Get content type from filename extension"""        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"
        
    def _task_to_dict(self, task: ProjectTask) -> Dict[str, Any]:
        """Convert ProjectTask to dictionary"""        return {
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'assigned_to': task.assigned_to,
            'status': task.status.value,
            'priority': task.priority.value,
            'estimated_hours': task.estimated_hours,
            'actual_hours': task.actual_hours,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'dependencies': task.dependencies,
            'tags': task.tags,
            'attachments': task.attachments,
            'comments': task.comments,
            'progress_percentage': task.progress_percentage,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }
        
    def _milestone_to_dict(self, milestone: ProjectMilestone) -> Dict[str, Any]:
        """Convert ProjectMilestone to dictionary"""        return {
            'milestone_id': milestone.milestone_id,
            'title': milestone.title,
            'description': milestone.description,
            'milestone_type': milestone.milestone_type.value,
            'due_date': milestone.due_date.isoformat(),
            'completion_criteria': milestone.completion_criteria,
            'deliverables': milestone.deliverables,
            'payment_percentage': milestone.payment_percentage,
            'is_completed': milestone.is_completed,
            'completed_date': milestone.completed_date.isoformat() if milestone.completed_date else None,
            'tasks': milestone.tasks,
            'dependencies': milestone.dependencies
        }
        
    # Advanced project workflow methods
    async def _create_project_workspace(self, project: CollaborationProject) -> None:
        """Create project workspace structure"""        workspace_structure = {
            'folders': [
                f"projects/{project.project_id}/documents",
                f"projects/{project.project_id}/assets",
                f"projects/{project.project_id}/deliverables",
                f"projects/{project.project_id}/communications",
                f"projects/{project.project_id}/backups"
            ],
            'permissions': {
                participant: 'read_write' for participant in project.participants
            }
        }
        
        await self.file_storage.create_workspace_structure(workspace_structure)
        
    async def _get_project_template(self, project_type: str) -> Optional[Dict[str, Any]]:
        """Get project template based on type"""        templates = {
            'music_video_campaign': {
                'default_tasks': [
                    {'title': 'Concept Development', 'type': 'planning', 'estimated_hours': 8},
                    {'title': 'Pre-production', 'type': 'preparation', 'estimated_hours': 16},
                    {'title': 'Production', 'type': 'execution', 'estimated_hours': 24},
                    {'title': 'Post-production', 'type': 'editing', 'estimated_hours': 32},
                    {'title': 'Review & Approval', 'type': 'review', 'estimated_hours': 4}
                ],
                'default_milestones': [
                    {'title': 'Concept Approval', 'type': 'planning', 'payment_percentage': 20},
                    {'title': 'Production Complete', 'type': 'development', 'payment_percentage': 50},
                    {'title': 'Final Delivery', 'type': 'delivery', 'payment_percentage': 30}
                ]
            },
            'creative_project': {
                'default_tasks': [
                    {'title': 'Requirements Gathering', 'type': 'planning', 'estimated_hours': 4},
                    {'title': 'Creative Brief', 'type': 'planning', 'estimated_hours': 6},
                    {'title': 'Content Creation', 'type': 'execution', 'estimated_hours': 20},
                    {'title': 'Review & Feedback', 'type': 'review', 'estimated_hours': 4},
                    {'title': 'Final Delivery', 'type': 'delivery', 'estimated_hours': 2}
                ],
                'default_milestones': [
                    {'title': 'Brief Approval', 'type': 'planning', 'payment_percentage': 25},
                    {'title': 'First Draft', 'type': 'development', 'payment_percentage': 50},
                    {'title': 'Final Delivery', 'type': 'delivery', 'payment_percentage': 25}
                ]
            }
        }
        
        return templates.get(project_type)
        
    # Additional helper methods for comprehensive project management
    async def _calculate_schedule_adherence(self, project: CollaborationProject) -> float:
        """Calculate schedule adherence score"""        return 0.85  # Placeholder
        
    async def _identify_critical_path(self, project: CollaborationProject) -> List[str]:
        """Identify critical path tasks"""        return []  # Placeholder
        
    async def _identify_schedule_risks(self, project: CollaborationProject) -> List[Dict[str, Any]]:
        """Identify schedule risks"""        return []  # Placeholder
        
    async def _predict_timeline_outcomes(self, project: CollaborationProject) -> Dict[str, Any]:
        """Predict timeline outcomes"""        return {}  # Placeholder
        
    async def _calculate_actual_spending(self, project: CollaborationProject) -> float:
        """Calculate actual project spending"""        return 0.0  # Placeholder
        
    async def _forecast_spending(self, project: CollaborationProject) -> Dict[str, Any]:
        """Forecast future spending"""        return {}  # Placeholder
        
    async def _analyze_cost_efficiency(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze cost efficiency"""        return {}  # Placeholder
        
    async def _identify_budget_risks(self, project: CollaborationProject) -> List[str]:
        """Identify budget risks"""        return []  # Placeholder

