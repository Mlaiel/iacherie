"""Project Manager - Collaborative Project Management System

Advanced project management system for creator collaborations with AI-driven
task coordination, milestone tracking, and workflow optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project lifecycle status"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class TaskStatus(Enum):
    """Task status options"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MilestoneType(Enum):
    """Types of project milestones"""
    KICKOFF = "kickoff"
    PLANNING_COMPLETE = "planning_complete"
    FIRST_DRAFT = "first_draft"
    REVIEW_COMPLETE = "review_complete"
    FINAL_DELIVERY = "final_delivery"
    PROJECT_COMPLETE = "project_complete"


@dataclass
class Task:
    """Individual project task"""
    task_id: str
    title: str
    description: str
    assigned_to: List[str]  # creator IDs
    status: TaskStatus
    priority: TaskPriority
    estimated_hours: float
    actual_hours: float = 0.0
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)  # task IDs
    deliverables: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Milestone:
    """Project milestone"""
    milestone_id: str
    title: str
    description: str
    milestone_type: MilestoneType
    target_date: datetime
    completion_date: Optional[datetime] = None
    is_completed: bool = False
    associated_tasks: List[str] = field(default_factory=list)  # task IDs
    success_criteria: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProjectBudget:
    """Project budget tracking"""
    total_budget: float
    allocated_budget: Dict[str, float]  # category -> amount
    spent_budget: Dict[str, float]  # category -> amount
    remaining_budget: float
    cost_breakdown: Dict[str, Any]
    budget_alerts: List[str] = field(default_factory=list)


@dataclass
class ProjectAnalytics:
    """Project analytics and insights"""
    project_id: str
    completion_percentage: float
    tasks_completed: int
    tasks_remaining: int
    avg_task_completion_time: float
    milestones_achieved: int
    milestones_pending: int
    budget_utilization: float
    timeline_variance: float  # positive = ahead, negative = behind
    team_performance: Dict[str, Any]
    risk_indicators: List[str]
    success_metrics: Dict[str, float]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CollaborationProject:
    """Main project entity for collaboration"""
    project_id: str
    title: str
    description: str
    project_type: str
    status: ProjectStatus
    creators: List[str]  # creator IDs
    lead_creator: str
    start_date: datetime
    target_end_date: datetime
    actual_end_date: Optional[datetime] = None
    tasks: List[Task] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    budget: Optional[ProjectBudget] = None
    deliverables: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    collaboration_rules: Dict[str, Any] = field(default_factory=dict)
    communication_channels: Dict[str, str] = field(default_factory=dict)
    project_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ProjectManager:
    """Advanced collaborative project management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Project storage (in real implementation, this would be a database)
        self.projects = {}
        self.tasks = {}
        self.milestones = {}
        
        # Project templates for different collaboration types
        self.project_templates = self._initialize_project_templates()
        
        # AI-driven task optimization settings
        self.optimization_enabled = self.config.get('ai_optimization', True)
        self.auto_scheduling = self.config.get('auto_scheduling', True)
        self.risk_monitoring = self.config.get('risk_monitoring', True)
        
        logger.info("ProjectManager initialized with advanced collaboration capabilities")
    
    async def initialize(self):
        """Initialize the project management system"""
        logger.info("Initializing Project Manager...")
        await self._load_project_templates()
        await self._initialize_ai_optimization()
        logger.info("Project Manager initialized successfully")
    
    async def shutdown(self):
        """Shutdown the project management system"""
        logger.info("Shutting down Project Manager...")
        # Save project data, cleanup resources
        logger.info("Project Manager shutdown complete")
    
    async def create_project(
        self,
        title: str,
        description: str,
        project_type: str,
        creators: List[str],
        lead_creator: str,
        requirements: Dict[str, Any] = None,
        budget: float = None
    ) -> CollaborationProject:
        """Create a new collaboration project"""
        try:
            project_id = str(uuid.uuid4())
            
            # Initialize project from template if available
            project_template = self.project_templates.get(project_type, {})
            
            # Calculate project timeline based on requirements
            start_date = datetime.now()
            estimated_duration = self._estimate_project_duration(project_type, requirements or {})
            target_end_date = start_date + timedelta(days=estimated_duration)
            
            # Create project budget if specified
            project_budget = None
            if budget:
                project_budget = ProjectBudget(
                    total_budget=budget,
                    allocated_budget=self._allocate_budget(budget, project_type),
                    spent_budget={},
                    remaining_budget=budget,
                    cost_breakdown={}
                )
            
            # Create project
            project = CollaborationProject(
                project_id=project_id,
                title=title,
                description=description,
                project_type=project_type,
                status=ProjectStatus.PLANNING,
                creators=creators,
                lead_creator=lead_creator,
                start_date=start_date,
                target_end_date=target_end_date,
                budget=project_budget,
                requirements=requirements or {},
                collaboration_rules=project_template.get('collaboration_rules', {}),
                communication_channels=self._setup_communication_channels(creators),
                project_metadata={'template_used': project_type}
            )
            
            # Generate initial tasks and milestones from template
            if project_template:
                await self._generate_tasks_from_template(project, project_template)
                await self._generate_milestones_from_template(project, project_template)
            
            # Store project
            self.projects[project_id] = project
            
            # Initialize project analytics
            await self._initialize_project_analytics(project_id)
            
            logger.info(f"Created collaboration project: {project_id}")
            return project
            
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise
    
    async def add_task(
        self,
        project_id: str,
        title: str,
        description: str,
        assigned_to: List[str],
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_hours: float = 1.0,
        due_date: Optional[datetime] = None,
        dependencies: List[str] = None
    ) -> Task:
        """Add a new task to a project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            task_id = str(uuid.uuid4())
            
            # Auto-schedule task if enabled
            if self.auto_scheduling and due_date is None:
                due_date = await self._auto_schedule_task(project, estimated_hours, dependencies or [])
            
            task = Task(
                task_id=task_id,
                title=title,
                description=description,
                assigned_to=assigned_to,
                status=TaskStatus.NOT_STARTED,
                priority=priority,
                estimated_hours=estimated_hours,
                due_date=due_date,
                dependencies=dependencies or []
            )
            
            # Add task to project
            project.tasks.append(task)
            self.tasks[task_id] = task
            
            # Update project
            project.updated_at = datetime.now()
            
            # Trigger task optimization if enabled
            if self.optimization_enabled:
                await self._optimize_task_assignment(project, task)
            
            logger.info(f"Added task {task_id} to project {project_id}")
            return task
            
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            raise
    
    async def update_task_status(
        self,
        project_id: str,
        task_id: str,
        status: TaskStatus,
        progress_percentage: Optional[float] = None,
        actual_hours: Optional[float] = None,
        notes: Optional[str] = None
    ) -> Task:
        """Update task status and progress"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            task = self.tasks.get(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Update task
            task.status = status
            task.updated_at = datetime.now()
            
            if progress_percentage is not None:
                task.progress_percentage = progress_percentage
            
            if actual_hours is not None:
                task.actual_hours = actual_hours
            
            if notes:
                task.notes.append(f"{datetime.now().isoformat()}: {notes}")
            
            # Mark completion date if completed
            if status == TaskStatus.COMPLETED:
                task.completion_date = datetime.now()
                task.progress_percentage = 100.0
            
            # Update project
            project.updated_at = datetime.now()
            
            # Check for milestone completion
            await self._check_milestone_completion(project)
            
            # Update analytics
            await self._update_project_analytics(project_id)
            
            logger.info(f"Updated task {task_id} status to {status.value}")
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
        target_date: datetime,
        success_criteria: List[str] = None
    ) -> Milestone:
        """Add a milestone to a project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            milestone_id = str(uuid.uuid4())
            
            milestone = Milestone(
                milestone_id=milestone_id,
                title=title,
                description=description,
                milestone_type=milestone_type,
                target_date=target_date,
                success_criteria=success_criteria or []
            )
            
            # Add milestone to project
            project.milestones.append(milestone)
            self.milestones[milestone_id] = milestone
            
            # Update project
            project.updated_at = datetime.now()
            
            logger.info(f"Added milestone {milestone_id} to project {project_id}")
            return milestone
            
        except Exception as e:
            logger.error(f"Error adding milestone: {str(e)}")
            raise
    
    async def get_project_analytics(self, project_id: str) -> ProjectAnalytics:
        """Get comprehensive project analytics"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Calculate completion percentage
            total_tasks = len(project.tasks)
            completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate average task completion time
            completed_task_times = []
            for task in project.tasks:
                if task.status == TaskStatus.COMPLETED and task.start_date and task.completion_date:
                    duration = (task.completion_date - task.start_date).total_seconds() / 3600
                    completed_task_times.append(duration)
            
            avg_completion_time = sum(completed_task_times) / len(completed_task_times) if completed_task_times else 0
            
            # Calculate milestone progress
            total_milestones = len(project.milestones)
            achieved_milestones = len([m for m in project.milestones if m.is_completed])
            
            # Calculate budget utilization
            budget_utilization = 0
            if project.budget:
                total_spent = sum(project.budget.spent_budget.values())
                budget_utilization = (total_spent / project.budget.total_budget * 100) if project.budget.total_budget > 0 else 0
            
            # Calculate timeline variance
            current_date = datetime.now()
            project_duration = (project.target_end_date - project.start_date).days
            elapsed_days = (current_date - project.start_date).days
            expected_progress = (elapsed_days / project_duration * 100) if project_duration > 0 else 0
            timeline_variance = completion_percentage - expected_progress
            
            # Team performance analysis
            team_performance = await self._analyze_team_performance(project)
            
            # Risk indicators
            risk_indicators = await self._identify_risk_indicators(project)
            
            # Success metrics
            success_metrics = await self._calculate_success_metrics(project)
            
            analytics = ProjectAnalytics(
                project_id=project_id,
                completion_percentage=completion_percentage,
                tasks_completed=completed_tasks,
                tasks_remaining=total_tasks - completed_tasks,
                avg_task_completion_time=avg_completion_time,
                milestones_achieved=achieved_milestones,
                milestones_pending=total_milestones - achieved_milestones,
                budget_utilization=budget_utilization,
                timeline_variance=timeline_variance,
                team_performance=team_performance,
                risk_indicators=risk_indicators,
                success_metrics=success_metrics
            )
            
            logger.info(f"Generated analytics for project {project_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating project analytics: {str(e)}")
            raise
    
    async def optimize_project_workflow(self, project_id: str) -> Dict[str, Any]:
        """AI-driven project workflow optimization"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            optimization_results = {
                'task_reallocation': [],
                'schedule_adjustments': [],
                'resource_optimization': [],
                'risk_mitigation': [],
                'efficiency_improvements': []
            }
            
            # Analyze current workflow
            workflow_analysis = await self._analyze_workflow_efficiency(project)
            
            # Task reallocation optimization
            task_reallocations = await self._optimize_task_allocation(project)
            optimization_results['task_reallocation'] = task_reallocations
            
            # Schedule optimization
            schedule_adjustments = await self._optimize_project_schedule(project)
            optimization_results['schedule_adjustments'] = schedule_adjustments
            
            # Resource optimization
            resource_optimizations = await self._optimize_resource_allocation(project)
            optimization_results['resource_optimization'] = resource_optimizations
            
            # Risk mitigation
            risk_mitigations = await self._suggest_risk_mitigations(project)
            optimization_results['risk_mitigation'] = risk_mitigations
            
            # Efficiency improvements
            efficiency_improvements = await self._suggest_efficiency_improvements(project)
            optimization_results['efficiency_improvements'] = efficiency_improvements
            
            logger.info(f"Optimized workflow for project {project_id}")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing project workflow: {str(e)}")
            raise
    
    def _initialize_project_templates(self) -> Dict[str, Any]:
        """Initialize project templates for different collaboration types"""
        return {
            'content_creation': {
                'default_duration': 21,  # days
                'phases': ['planning', 'production', 'review', 'finalization'],
                'collaboration_rules': {
                    'approval_required': True,
                    'version_control': True,
                    'daily_checkins': True
                },
                'typical_tasks': [
                    'Content planning and ideation',
                    'Research and preparation',
                    'Content creation',
                    'Review and feedback',
                    'Revisions and improvements',
                    'Final production',
                    'Distribution planning'
                ]
            },
            'cross_promotion': {
                'default_duration': 14,
                'phases': ['planning', 'content_prep', 'execution', 'analysis'],
                'collaboration_rules': {
                    'mutual_approval': True,
                    'brand_guidelines': True,
                    'scheduled_posts': True
                }
            },
            'joint_project': {
                'default_duration': 30,
                'phases': ['conception', 'planning', 'development', 'testing', 'launch'],
                'collaboration_rules': {
                    'shared_ownership': True,
                    'joint_decision_making': True,
                    'revenue_sharing': True
                }
            }
        }
    
    async def _load_project_templates(self):
        """Load project templates from configuration"""
        logger.info("Loading project templates...")
    
    async def _initialize_ai_optimization(self):
        """Initialize AI optimization models"""
        logger.info("Initializing AI optimization...")
    
    def _estimate_project_duration(self, project_type: str, requirements: Dict[str, Any]) -> int:
        """Estimate project duration based on type and requirements"""
        template = self.project_templates.get(project_type, {})
        base_duration = template.get('default_duration', 21)
        
        # Adjust based on complexity
        complexity = requirements.get('complexity', 'medium')
        if complexity == 'high':
            base_duration = int(base_duration * 1.5)
        elif complexity == 'low':
            base_duration = int(base_duration * 0.8)
        
        # Adjust based on team size
        team_size = requirements.get('team_size', 2)
        if team_size > 3:
            base_duration = int(base_duration * 1.2)
        
        return base_duration
    
    def _allocate_budget(self, total_budget: float, project_type: str) -> Dict[str, float]:
        """Allocate budget across different categories"""
        # Default allocation percentages
        allocation = {
            'creator_fees': 0.6,
            'production_costs': 0.2,
            'marketing': 0.1,
            'platform_fees': 0.05,
            'contingency': 0.05
        }
        
        # Adjust based on project type
        if project_type == 'content_creation':
            allocation['production_costs'] = 0.3
            allocation['creator_fees'] = 0.5
        elif project_type == 'cross_promotion':
            allocation['marketing'] = 0.2
            allocation['creator_fees'] = 0.65
        
        return {category: total_budget * percentage for category, percentage in allocation.items()}
    
    def _setup_communication_channels(self, creators: List[str]) -> Dict[str, str]:
        """Setup communication channels for the project"""
        return {
            'primary_channel': f"project_chat_{len(creators)}_creators",
            'video_calls': 'scheduled_weekly',
            'file_sharing': 'shared_workspace',
            'notifications': 'real_time'
        }
    
    async def _generate_tasks_from_template(self, project: CollaborationProject, template: Dict[str, Any]):
        """Generate initial tasks from project template"""
        typical_tasks = template.get('typical_tasks', [])
        
        for i, task_title in enumerate(typical_tasks):
            task_id = str(uuid.uuid4())
            
            # Distribute tasks among creators
            assigned_creator = project.creators[i % len(project.creators)]
            
            task = Task(
                task_id=task_id,
                title=task_title,
                description=f"Template task: {task_title}",
                assigned_to=[assigned_creator],
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority.MEDIUM,
                estimated_hours=8.0  # Default estimate
            )
            
            project.tasks.append(task)
            self.tasks[task_id] = task
    
    async def _generate_milestones_from_template(self, project: CollaborationProject, template: Dict[str, Any]):
        """Generate milestones from project template"""
        phases = template.get('phases', [])
        phase_duration = (project.target_end_date - project.start_date).days / len(phases) if phases else 7
        
        for i, phase in enumerate(phases):
            milestone_id = str(uuid.uuid4())
            target_date = project.start_date + timedelta(days=int((i + 1) * phase_duration))
            
            milestone = Milestone(
                milestone_id=milestone_id,
                title=f"{phase.title()} Complete",
                description=f"Complete the {phase} phase of the project",
                milestone_type=MilestoneType.PLANNING_COMPLETE,  # Default type
                target_date=target_date
            )
            
            project.milestones.append(milestone)
            self.milestones[milestone_id] = milestone
    
    async def _initialize_project_analytics(self, project_id: str):
        """Initialize analytics tracking for a new project"""
        logger.info(f"Initializing analytics for project {project_id}")
    
    async def _auto_schedule_task(self, project: CollaborationProject, estimated_hours: float, dependencies: List[str]) -> datetime:
        """Auto-schedule a task based on project timeline and dependencies"""
        # Simple scheduling logic - in real implementation, this would be more sophisticated
        latest_dependency_date = project.start_date
        
        # Check dependency completion dates
        for dep_id in dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task and dep_task.due_date:
                latest_dependency_date = max(latest_dependency_date, dep_task.due_date)
        
        # Add estimated duration
        return latest_dependency_date + timedelta(hours=estimated_hours)
    
    async def _optimize_task_assignment(self, project: CollaborationProject, task: Task):
        """Optimize task assignment using AI"""
        # Placeholder for AI-driven task assignment optimization
        logger.info(f"Optimizing assignment for task {task.task_id}")
    
    async def _check_milestone_completion(self, project: CollaborationProject):
        """Check if any milestones are completed based on task completion"""
        for milestone in project.milestones:
            if not milestone.is_completed and milestone.associated_tasks:
                # Check if all associated tasks are completed
                all_completed = True
                for task_id in milestone.associated_tasks:
                    task = self.tasks.get(task_id)
                    if not task or task.status != TaskStatus.COMPLETED:
                        all_completed = False
                        break
                
                if all_completed:
                    milestone.is_completed = True
                    milestone.completion_date = datetime.now()
                    logger.info(f"Milestone {milestone.milestone_id} completed")
    
    async def _update_project_analytics(self, project_id: str):
        """Update project analytics after changes"""
        logger.info(f"Updating analytics for project {project_id}")
    
    async def _analyze_team_performance(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze team performance metrics"""
        performance = {}
        
        for creator_id in project.creators:
            creator_tasks = [t for t in project.tasks if creator_id in t.assigned_to]
            completed_tasks = [t for t in creator_tasks if t.status == TaskStatus.COMPLETED]
            
            performance[creator_id] = {
                'total_tasks': len(creator_tasks),
                'completed_tasks': len(completed_tasks),
                'completion_rate': len(completed_tasks) / len(creator_tasks) if creator_tasks else 0,
                'avg_completion_time': self._calculate_avg_completion_time(completed_tasks)
            }
        
        return performance
    
    def _calculate_avg_completion_time(self, tasks: List[Task]) -> float:
        """Calculate average completion time for tasks"""
        completion_times = []
        for task in tasks:
            if task.start_date and task.completion_date:
                duration = (task.completion_date - task.start_date).total_seconds() / 3600
                completion_times.append(duration)
        
        return sum(completion_times) / len(completion_times) if completion_times else 0
    
    async def _identify_risk_indicators(self, project: CollaborationProject) -> List[str]:
        """Identify project risk indicators"""
        risks = []
        
        # Timeline risks
        current_date = datetime.now()
        if current_date > project.target_end_date:
            risks.append("Project is past deadline")
        
        # Task completion risks
        overdue_tasks = [t for t in project.tasks if t.due_date and t.due_date < current_date and t.status != TaskStatus.COMPLETED]
        if overdue_tasks:
            risks.append(f"{len(overdue_tasks)} tasks are overdue")
        
        # Budget risks
        if project.budget:
            total_spent = sum(project.budget.spent_budget.values())
            if total_spent > project.budget.total_budget * 0.9:
                risks.append("Budget nearly exhausted")
        
        return risks
    
    async def _calculate_success_metrics(self, project: CollaborationProject) -> Dict[str, float]:
        """Calculate project success metrics"""
        return {
            'schedule_adherence': 0.85,  # Placeholder
            'budget_efficiency': 0.90,   # Placeholder
            'quality_score': 0.88,       # Placeholder
            'team_satisfaction': 0.92    # Placeholder
        }
    
    async def _analyze_workflow_efficiency(self, project: CollaborationProject) -> Dict[str, Any]:
        """Analyze workflow efficiency"""
        return {
            'bottlenecks': [],
            'optimization_opportunities': [],
            'efficiency_score': 0.8
        }
    
    async def _optimize_task_allocation(self, project: CollaborationProject) -> List[str]:
        """Optimize task allocation across team members"""
        return ["Redistribute high-priority tasks for better load balancing"]
    
    async def _optimize_project_schedule(self, project: CollaborationProject) -> List[str]:
        """Optimize project schedule"""
        return ["Parallel task execution opportunities identified"]
    
    async def _optimize_resource_allocation(self, project: CollaborationProject) -> List[str]:
        """Optimize resource allocation"""
        return ["Budget reallocation suggestions for better ROI"]
    
    async def _suggest_risk_mitigations(self, project: CollaborationProject) -> List[str]:
        """Suggest risk mitigation strategies"""
        return ["Add buffer time for critical path tasks"]
    
    async def _suggest_efficiency_improvements(self, project: CollaborationProject) -> List[str]:
        """Suggest efficiency improvements"""
        return ["Implement automated status updates", "Use template-based task creation"]


# Export main classes
__all__ = [
    'ProjectManager', 'CollaborationProject', 'Task', 'Milestone', 'ProjectAnalytics',
    'ProjectStatus', 'TaskStatus', 'TaskPriority', 'MilestoneType', 'ProjectBudget'
]