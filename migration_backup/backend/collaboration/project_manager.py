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
    allocated_budget: Dict[str, float]  # creator_id -> allocated amount
    spent_budget: Dict[str, float]  # creator_id -> spent amount
    expense_categories: Dict[str, float]  # category -> amount
    payment_schedule: List[Dict[str, Any]] = field(default_factory=list)
    currency: str = "USD"


@dataclass
class CollaborationProject:
    """Comprehensive collaboration project"""
    project_id: str
    title: str
    description: str
    project_type: str
    status: ProjectStatus
    participants: List[str]  # creator IDs
    project_lead: str  # creator ID
    start_date: datetime
    target_end_date: datetime
    actual_end_date: Optional[datetime] = None
    tasks: List[Task] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    budget: Optional[ProjectBudget] = None
    deliverables: List[str] = field(default_factory=list)
    communication_channels: Dict[str, str] = field(default_factory=dict)
    project_settings: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: float = 0.0
    health_score: float = 1.0  # 0-1 scale
    risk_factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ProjectAnalytics:
    """Project performance analytics"""
    project_id: str
    completion_rate: float
    schedule_performance: float  # Planned vs actual timeline
    budget_performance: float  # Budget utilization
    quality_score: float
    team_satisfaction: float
    collaboration_efficiency: float
    key_metrics: Dict[str, Any] = field(default_factory=dict)
    performance_trends: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class ProjectManager:
    """AI-powered collaborative project management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Project storage (in real implementation, use database)
        self.projects = {}
        self.project_templates = {}
        
        # AI optimization settings
        self.optimization_enabled = self.config.get('ai_optimization', True)
        self.auto_scheduling = self.config.get('auto_scheduling', True)
        self.risk_monitoring = self.config.get('risk_monitoring', True)
        
        # Performance thresholds
        self.health_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'concerning': 0.5,
            'critical': 0.3
        }
        
        logger.info("ProjectManager initialized with AI-powered collaboration features")
    
    async def create_project(
        self,
        project_data: Dict[str, Any],
        participants: List[str],
        project_lead: str,
        template_id: Optional[str] = None
    ) -> CollaborationProject:
        """Create a new collaboration project"""
        try:
            project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Apply template if specified
            if template_id and template_id in self.project_templates:
                template = self.project_templates[template_id]
                project_data = {**template, **project_data}
            
            # Create project instance
            project = CollaborationProject(
                project_id=project_id,
                title=project_data['title'],
                description=project_data['description'],
                project_type=project_data.get('type', 'collaboration'),
                status=ProjectStatus.PLANNING,
                participants=participants,
                project_lead=project_lead,
                start_date=datetime.fromisoformat(project_data['start_date']),
                target_end_date=datetime.fromisoformat(project_data['target_end_date']),
                deliverables=project_data.get('deliverables', []),
                project_settings=project_data.get('settings', {})
            )
            
            # Initialize budget if provided
            if 'budget' in project_data:
                project.budget = ProjectBudget(
                    total_budget=project_data['budget']['total'],
                    allocated_budget={},
                    spent_budget={},
                    expense_categories={},
                    currency=project_data['budget'].get('currency', 'USD')
                )
            
            # Generate initial tasks and milestones using AI
            if self.optimization_enabled:
                await self._generate_initial_project_structure(project, project_data)
            
            # Set up communication channels
            await self._setup_communication_channels(project)
            
            # Store project
            self.projects[project_id] = project
            
            logger.info(f"Created project {project_id}: {project.title}")
            return project
            
        except Exception as e:
            logger.error(f"Project creation failed: {e}")
            raise
    
    async def add_task(
        self,
        project_id: str,
        task_data: Dict[str, Any],
        auto_schedule: bool = True
    ) -> Task:
        """Add a new task to the project"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        
        task_id = f"task_{len(project.tasks) + 1}_{datetime.now().strftime('%Y%m%d%H%M')}"
        
        task = Task(
            task_id=task_id,
            title=task_data['title'],
            description=task_data['description'],
            assigned_to=task_data['assigned_to'],
            status=TaskStatus(task_data.get('status', 'not_started')),
            priority=TaskPriority(task_data.get('priority', 'medium')),
            estimated_hours=task_data.get('estimated_hours', 1.0),
            dependencies=task_data.get('dependencies', []),
            deliverables=task_data.get('deliverables', [])
        )
        
        # Auto-schedule if enabled
        if auto_schedule and self.auto_scheduling:
            await self._auto_schedule_task(task, project)
        
        project.tasks.append(task)
        project.updated_at = datetime.now()
        
        # Update project health
        await self._update_project_health(project)
        
        logger.info(f"Added task {task_id} to project {project_id}")
        return task
    
    async def update_task_status(
        self,
        project_id: str,
        task_id: str,
        new_status: TaskStatus,
        progress_percentage: Optional[float] = None,
        actual_hours: Optional[float] = None
    ) -> Task:
        """Update task status and progress"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        task = next((t for t in project.tasks if t.task_id == task_id), None)
        
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status
        old_status = task.status
        task.status = new_status
        task.updated_at = datetime.now()
        
        if progress_percentage is not None:
            task.progress_percentage = min(100.0, max(0.0, progress_percentage))
        
        if actual_hours is not None:
            task.actual_hours = actual_hours
        
        # Handle status-specific updates
        if new_status == TaskStatus.IN_PROGRESS and not task.start_date:
            task.start_date = datetime.now()
        elif new_status == TaskStatus.COMPLETED:
            task.completion_date = datetime.now()
            task.progress_percentage = 100.0
        
        # Check milestone completion
        await self._check_milestone_completion(project)
        
        # Update project progress
        await self._update_project_progress(project)
        
        # Update project health
        await self._update_project_health(project)
        
        # AI-powered task optimization
        if self.optimization_enabled:
            await self._optimize_task_dependencies(project, task)
        
        logger.info(f"Updated task {task_id} status from {old_status.value} to {new_status.value}")
        return task
    
    async def add_milestone(
        self,
        project_id: str,
        milestone_data: Dict[str, Any]
    ) -> Milestone:
        """Add a milestone to the project"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        
        milestone_id = f"milestone_{len(project.milestones) + 1}"
        
        milestone = Milestone(
            milestone_id=milestone_id,
            title=milestone_data['title'],
            description=milestone_data['description'],
            milestone_type=MilestoneType(milestone_data.get('type', 'planning_complete')),
            target_date=datetime.fromisoformat(milestone_data['target_date']),
            associated_tasks=milestone_data.get('associated_tasks', []),
            success_criteria=milestone_data.get('success_criteria', []),
            deliverables=milestone_data.get('deliverables', [])
        )
        
        project.milestones.append(milestone)
        project.updated_at = datetime.now()
        
        logger.info(f"Added milestone {milestone_id} to project {project_id}")
        return milestone
    
    async def get_project_analytics(self, project_id: str) -> ProjectAnalytics:
        """Generate comprehensive project analytics"""
        if project_id not in self.projects:
            raise ValueError(f"Project {project_id} not found")
        
        project = self.projects[project_id]
        
        # Calculate completion rate
        completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
        total_tasks = len(project.tasks)
        completion_rate = completed_tasks / max(total_tasks, 1)
        
        # Calculate schedule performance
        schedule_performance = await self._calculate_schedule_performance(project)
        
        # Calculate budget performance
        budget_performance = await self._calculate_budget_performance(project)
        
        # Calculate quality score
        quality_score = await self._calculate_quality_score(project)
        
        # Calculate team satisfaction (simulated)
        team_satisfaction = await self._calculate_team_satisfaction(project)
        
        # Calculate collaboration efficiency
        collaboration_efficiency = await self._calculate_collaboration_efficiency(project)
        
        # Generate key metrics
        key_metrics = await self._generate_key_metrics(project)
        
        # Generate performance trends
        performance_trends = await self._generate_performance_trends(project)
        
        # Generate AI recommendations
        recommendations = await self._generate_project_recommendations(project)
        
        analytics = ProjectAnalytics(
            project_id=project_id,
            completion_rate=completion_rate,
            schedule_performance=schedule_performance,
            budget_performance=budget_performance,
            quality_score=quality_score,
            team_satisfaction=team_satisfaction,
            collaboration_efficiency=collaboration_efficiency,
            key_metrics=key_metrics,
            performance_trends=performance_trends,
            recommendations=recommendations
        )
        
        return analytics
    
    async def _generate_initial_project_structure(
        self,
        project: CollaborationProject,
        project_data: Dict[str, Any]
    ):
        """Generate initial project structure using AI"""
        project_type = project.project_type
        
        # Generate standard milestones
        milestones_templates = {
            'content_creation': [
                {'title': 'Project Kickoff', 'type': 'kickoff', 'days_offset': 0},
                {'title': 'Planning Complete', 'type': 'planning_complete', 'days_offset': 7},
                {'title': 'First Draft Ready', 'type': 'first_draft', 'days_offset': 21},
                {'title': 'Review Complete', 'type': 'review_complete', 'days_offset': 28},
                {'title': 'Final Delivery', 'type': 'final_delivery', 'days_offset': 35}
            ],
            'collaboration': [
                {'title': 'Project Kickoff', 'type': 'kickoff', 'days_offset': 0},
                {'title': 'Planning Phase Done', 'type': 'planning_complete', 'days_offset': 5},
                {'title': 'Mid-point Check', 'type': 'review_complete', 'days_offset': 15},
                {'title': 'Project Complete', 'type': 'project_complete', 'days_offset': 30}
            ]
        }
        
        milestone_template = milestones_templates.get(project_type, milestones_templates['collaboration'])
        
        for i, milestone_data in enumerate(milestone_template):
            milestone = Milestone(
                milestone_id=f"milestone_{i+1}",
                title=milestone_data['title'],
                description=f"Auto-generated milestone: {milestone_data['title']}",
                milestone_type=MilestoneType(milestone_data['type']),
                target_date=project.start_date + timedelta(days=milestone_data['days_offset'])
            )
            project.milestones.append(milestone)
        
        # Generate standard tasks
        task_templates = {
            'content_creation': [
                {'title': 'Define Content Strategy', 'estimated_hours': 4, 'priority': 'high'},
                {'title': 'Create Content Outline', 'estimated_hours': 2, 'priority': 'high'},
                {'title': 'Develop Initial Content', 'estimated_hours': 16, 'priority': 'medium'},
                {'title': 'Review and Feedback', 'estimated_hours': 4, 'priority': 'medium'},
                {'title': 'Final Content Production', 'estimated_hours': 8, 'priority': 'high'},
                {'title': 'Quality Assurance', 'estimated_hours': 2, 'priority': 'medium'}
            ],
            'collaboration': [
                {'title': 'Collaboration Planning', 'estimated_hours': 3, 'priority': 'high'},
                {'title': 'Role Definition', 'estimated_hours': 2, 'priority': 'high'},
                {'title': 'Content Development', 'estimated_hours': 20, 'priority': 'medium'},
                {'title': 'Integration and Review', 'estimated_hours': 6, 'priority': 'medium'},
                {'title': 'Final Production', 'estimated_hours': 8, 'priority': 'high'}
            ]
        }
        
        task_template = task_templates.get(project_type, task_templates['collaboration'])
        
        for i, task_data in enumerate(task_template):
            task = Task(
                task_id=f"task_{i+1}",
                title=task_data['title'],
                description=f"Auto-generated task: {task_data['title']}",
                assigned_to=[project.project_lead],  # Initially assign to project lead
                status=TaskStatus.NOT_STARTED,
                priority=TaskPriority(task_data['priority']),
                estimated_hours=task_data['estimated_hours']
            )
            project.tasks.append(task)
    
    async def _auto_schedule_task(self, task: Task, project: CollaborationProject):
        """Automatically schedule task based on dependencies and resource availability"""
        # Simple scheduling logic - in real implementation, use more sophisticated algorithms
        
        if not task.dependencies:
            # No dependencies - can start immediately
            task.start_date = max(datetime.now(), project.start_date)
        else:
            # Find latest completion date of dependencies
            latest_dependency_date = project.start_date
            
            for dep_task_id in task.dependencies:
                dep_task = next((t for t in project.tasks if t.task_id == dep_task_id), None)
                if dep_task and dep_task.due_date:
                    latest_dependency_date = max(latest_dependency_date, dep_task.due_date)
            
            task.start_date = latest_dependency_date + timedelta(days=1)
        
        # Set due date based on estimated hours (assuming 8 hours per day)
        working_days = max(1, int(task.estimated_hours / 8))
        task.due_date = task.start_date + timedelta(days=working_days)
    
    async def _setup_communication_channels(self, project: CollaborationProject):
        """Set up communication channels for the project"""
        project.communication_channels = {
            'main_chat': f"project_{project.project_id}_main",
            'updates': f"project_{project.project_id}_updates",
            'files': f"project_{project.project_id}_files",
            'feedback': f"project_{project.project_id}_feedback"
        }
    
    async def _check_milestone_completion(self, project: CollaborationProject):
        """Check if any milestones should be marked as completed"""
        for milestone in project.milestones:
            if milestone.is_completed:
                continue
            
            # Check if all associated tasks are completed
            if milestone.associated_tasks:
                associated_task_statuses = [
                    t.status for t in project.tasks 
                    if t.task_id in milestone.associated_tasks
                ]
                
                if associated_task_statuses and all(status == TaskStatus.COMPLETED for status in associated_task_statuses):
                    milestone.is_completed = True
                    milestone.completion_date = datetime.now()
                    
                    logger.info(f"Milestone {milestone.milestone_id} completed")
    
    async def _update_project_progress(self, project: CollaborationProject):
        """Update overall project progress based on task completion"""
        if not project.tasks:
            project.progress_percentage = 0.0
            return
        
        # Weight tasks by estimated hours
        total_estimated_hours = sum(task.estimated_hours for task in project.tasks)
        completed_hours = sum(
            task.estimated_hours for task in project.tasks 
            if task.status == TaskStatus.COMPLETED
        )
        
        in_progress_hours = sum(
            task.estimated_hours * (task.progress_percentage / 100) 
            for task in project.tasks 
            if task.status == TaskStatus.IN_PROGRESS
        )
        
        if total_estimated_hours > 0:
            project.progress_percentage = ((completed_hours + in_progress_hours) / total_estimated_hours) * 100
        else:
            project.progress_percentage = 0.0
        
        project.updated_at = datetime.now()
    
    async def _update_project_health(self, project: CollaborationProject):
        """Update project health score based on various factors"""
        health_factors = []
        
        # Schedule adherence factor
        schedule_factor = await self._calculate_schedule_adherence(project)
        health_factors.append(schedule_factor * 0.3)
        
        # Task progress factor
        progress_factor = project.progress_percentage / 100
        health_factors.append(progress_factor * 0.25)
        
        # Risk factor
        risk_factor = max(0, 1.0 - len(project.risk_factors) * 0.1)
        health_factors.append(risk_factor * 0.2)
        
        # Milestone achievement factor
        milestone_factor = await self._calculate_milestone_achievement(project)
        health_factors.append(milestone_factor * 0.15)
        
        # Team activity factor (simulated)
        activity_factor = 0.8  # Placeholder
        health_factors.append(activity_factor * 0.1)
        
        project.health_score = sum(health_factors)
        
        # Update risk factors based on health score
        await self._update_risk_factors(project)
    
    async def _calculate_schedule_adherence(self, project: CollaborationProject) -> float:
        """Calculate how well the project is adhering to schedule"""
        current_date = datetime.now()
        
        # Check overdue tasks
        overdue_tasks = [
            task for task in project.tasks 
            if task.due_date and task.due_date < current_date and task.status != TaskStatus.COMPLETED
        ]
        
        total_tasks = len(project.tasks)
        if total_tasks == 0:
            return 1.0
        
        overdue_ratio = len(overdue_tasks) / total_tasks
        
        # Return inverted ratio (fewer overdue tasks = better adherence)
        return max(0.0, 1.0 - overdue_ratio * 2)  # Heavily penalize overdue tasks
    
    async def _calculate_milestone_achievement(self, project: CollaborationProject) -> float:
        """Calculate milestone achievement rate"""
        if not project.milestones:
            return 1.0
        
        completed_milestones = len([m for m in project.milestones if m.is_completed])
        total_milestones = len(project.milestones)
        
        return completed_milestones / total_milestones
    
    async def _update_risk_factors(self, project: CollaborationProject):
        """Update project risk factors based on current state"""
        risk_factors = []
        
        # Schedule risks
        if project.health_score < 0.6:
            risk_factors.append("Project health below acceptable threshold")
        
        # Overdue task risks
        current_date = datetime.now()
        overdue_tasks = [
            task for task in project.tasks 
            if task.due_date and task.due_date < current_date and task.status != TaskStatus.COMPLETED
        ]
        
        if len(overdue_tasks) > 0:
            risk_factors.append(f"{len(overdue_tasks)} tasks are overdue")
        
        # Budget risks (if budget exists)
        if project.budget:
            spent_total = sum(project.budget.spent_budget.values())
            if spent_total > project.budget.total_budget * 0.8:
                risk_factors.append("Budget utilization above 80%")
        
        # Timeline risks
        if project.target_end_date < current_date + timedelta(days=7):
            if project.progress_percentage < 90:
                risk_factors.append("Project may not meet deadline")
        
        project.risk_factors = risk_factors
    
    async def _optimize_task_dependencies(self, project: CollaborationProject, updated_task: Task):
        """Optimize task dependencies based on AI analysis"""
        if not self.optimization_enabled:
            return
        
        # If a blocking task is completed, check for dependent tasks that can now start
        if updated_task.status == TaskStatus.COMPLETED:
            dependent_tasks = [
                task for task in project.tasks 
                if updated_task.task_id in task.dependencies and task.status == TaskStatus.NOT_STARTED
            ]
            
            for task in dependent_tasks:
                # Check if all dependencies are now completed
                all_deps_completed = all(
                    any(t.task_id == dep_id and t.status == TaskStatus.COMPLETED 
                        for t in project.tasks)
                    for dep_id in task.dependencies
                )
                
                if all_deps_completed:
                    # Auto-schedule the task
                    await self._auto_schedule_task(task, project)
                    
                    logger.info(f"Auto-scheduled task {task.task_id} after dependency completion")
    
    async def _calculate_schedule_performance(self, project: CollaborationProject) -> float:
        """Calculate schedule performance index"""
        current_date = datetime.now()
        project_duration = (project.target_end_date - project.start_date).days
        elapsed_days = (current_date - project.start_date).days
        
        if project_duration <= 0:
            return 1.0
        
        planned_progress = min(100, (elapsed_days / project_duration) * 100)
        actual_progress = project.progress_percentage
        
        if planned_progress <= 0:
            return 1.0
        
        # Schedule Performance Index = Actual Progress / Planned Progress
        spi = actual_progress / planned_progress
        
        return min(2.0, max(0.0, spi))  # Cap between 0 and 2
    
    async def _calculate_budget_performance(self, project: CollaborationProject) -> float:
        """Calculate budget performance index"""
        if not project.budget:
            return 1.0
        
        total_spent = sum(project.budget.spent_budget.values())
        
        if project.budget.total_budget <= 0:
            return 1.0
        
        # Simple budget utilization metric
        budget_utilization = total_spent / project.budget.total_budget
        progress_ratio = project.progress_percentage / 100
        
        if progress_ratio <= 0:
            return 1.0 if budget_utilization == 0 else 0.0
        
        # Budget Performance Index = Progress / Budget Utilization
        bpi = progress_ratio / max(budget_utilization, 0.01)
        
        return min(2.0, max(0.0, bpi))
    
    async def _calculate_quality_score(self, project: CollaborationProject) -> float:
        """Calculate overall quality score"""
        # Simplified quality calculation based on:
        # - Task completion quality
        # - Milestone achievement
        # - Rework rate
        
        quality_factors = []
        
        # Milestone achievement factor
        milestone_factor = await self._calculate_milestone_achievement(project)
        quality_factors.append(milestone_factor)
        
        # Task completion factor (assuming completed tasks indicate quality)
        if project.tasks:
            completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
            completion_factor = completed_tasks / len(project.tasks)
            quality_factors.append(completion_factor)
        
        # Health score factor
        quality_factors.append(project.health_score)
        
        return sum(quality_factors) / len(quality_factors)
    
    async def _calculate_team_satisfaction(self, project: CollaborationProject) -> float:
        """Calculate team satisfaction score (simulated)"""
        # In real implementation, this would come from surveys or feedback
        # For now, base it on project health and progress
        
        satisfaction_factors = []
        
        # Project health contributes to satisfaction
        satisfaction_factors.append(project.health_score)
        
        # Progress contributes to satisfaction
        progress_factor = min(1.0, project.progress_percentage / 100)
        satisfaction_factors.append(progress_factor)
        
        # Low risk contributes to satisfaction
        risk_factor = max(0.0, 1.0 - len(project.risk_factors) * 0.15)
        satisfaction_factors.append(risk_factor)
        
        return sum(satisfaction_factors) / len(satisfaction_factors)
    
    async def _calculate_collaboration_efficiency(self, project: CollaborationProject) -> float:
        """Calculate collaboration efficiency score"""
        efficiency_factors = []
        
        # Task distribution efficiency
        if project.tasks and len(project.participants) > 1:
            task_assignments = {}
            for task in project.tasks:
                for assignee in task.assigned_to:
                    task_assignments[assignee] = task_assignments.get(assignee, 0) + 1
            
            # Calculate distribution balance
            max_tasks = max(task_assignments.values()) if task_assignments else 0
            min_tasks = min(task_assignments.values()) if task_assignments else 0
            
            if max_tasks > 0:
                distribution_balance = 1.0 - ((max_tasks - min_tasks) / max_tasks)
                efficiency_factors.append(distribution_balance)
        
        # Communication efficiency (simulated)
        comm_efficiency = 0.8  # Placeholder
        efficiency_factors.append(comm_efficiency)
        
        # Schedule efficiency
        schedule_performance = await self._calculate_schedule_performance(project)
        efficiency_factors.append(min(1.0, schedule_performance))
        
        return sum(efficiency_factors) / len(efficiency_factors) if efficiency_factors else 0.8
    
    async def _generate_key_metrics(self, project: CollaborationProject) -> Dict[str, Any]:
        """Generate key project metrics"""
        metrics = {}
        
        # Basic metrics
        metrics['total_tasks'] = len(project.tasks)
        metrics['completed_tasks'] = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
        metrics['total_milestones'] = len(project.milestones)
        metrics['completed_milestones'] = len([m for m in project.milestones if m.is_completed])
        
        # Time metrics
        metrics['project_duration_days'] = (project.target_end_date - project.start_date).days
        metrics['elapsed_days'] = (datetime.now() - project.start_date).days
        metrics['remaining_days'] = (project.target_end_date - datetime.now()).days
        
        # Effort metrics
        metrics['total_estimated_hours'] = sum(task.estimated_hours for task in project.tasks)
        metrics['total_actual_hours'] = sum(task.actual_hours for task in project.tasks)
        
        # Budget metrics
        if project.budget:
            metrics['total_budget'] = project.budget.total_budget
            metrics['spent_budget'] = sum(project.budget.spent_budget.values())
            metrics['budget_utilization'] = (metrics['spent_budget'] / metrics['total_budget']) * 100
        
        # Risk metrics
        metrics['active_risks'] = len(project.risk_factors)
        metrics['health_score'] = project.health_score
        
        return metrics
    
    async def _generate_performance_trends(self, project: CollaborationProject) -> List[Dict[str, Any]]:
        """Generate performance trend data"""
        # In real implementation, this would track historical data
        # For now, generate simulated trend data
        
        trends = []
        current_date = datetime.now()
        
        for i in range(7):  # Last 7 days
            date = current_date - timedelta(days=6-i)
            trend_point = {
                'date': date.isoformat(),
                'progress': max(0, project.progress_percentage - (6-i) * 5),
                'health_score': max(0.3, project.health_score - (6-i) * 0.05),
                'task_completion_rate': max(0, min(100, (i + 1) * 10))
            }
            trends.append(trend_point)
        
        return trends
    
    async def _generate_project_recommendations(self, project: CollaborationProject) -> List[str]:
        """Generate AI-powered project recommendations"""
        recommendations = []
        
        # Health-based recommendations
        if project.health_score < 0.5:
            recommendations.append("Critical: Project health is below 50% - immediate action required")
        elif project.health_score < 0.7:
            recommendations.append("Warning: Monitor project closely and address risk factors")
        
        # Progress-based recommendations
        schedule_performance = await self._calculate_schedule_performance(project)
        if schedule_performance < 0.8:
            recommendations.append("Consider redistributing tasks or extending timeline")
        
        # Risk-based recommendations
        if len(project.risk_factors) > 2:
            recommendations.append("Address high number of risk factors to improve project stability")
        
        # Resource-based recommendations
        if project.budget:
            budget_performance = await self._calculate_budget_performance(project)
            if budget_performance < 0.8:
                recommendations.append("Budget utilization is high - monitor spending carefully")
        
        # Task-based recommendations
        overdue_tasks = [
            task for task in project.tasks 
            if task.due_date and task.due_date < datetime.now() and task.status != TaskStatus.COMPLETED
        ]
        
        if overdue_tasks:
            recommendations.append(f"Address {len(overdue_tasks)} overdue tasks to improve schedule performance")
        
        # Team-based recommendations
        if len(project.participants) > 1:
            recommendations.append("Schedule regular team sync meetings to maintain collaboration")
        
        return recommendations[:8]  # Limit to 8 recommendations


# Export main class
__all__ = ['ProjectManager', 'CollaborationProject', 'Task', 'Milestone', 'ProjectAnalytics', 
           'ProjectStatus', 'TaskStatus', 'TaskPriority', 'MilestoneType']