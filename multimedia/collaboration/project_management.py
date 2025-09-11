"""
📋 PROJECT MANAGEMENT ENGINE - ENTERPRISE ARCHITECTURE
===================================================

Comprehensive project management system for multimedia collaboration with
task tracking, milestone management, resource allocation, and team coordination.

**Expert Implementation:**
- Project Manager: Advanced project planning and execution workflows
- Backend Senior: High-performance project data management
- Database Administrator: Efficient project tracking and reporting
- Business Analyst: Workflow optimization and metrics tracking

**Features:** Project planning, Task management, Resource allocation, Timeline tracking, Team collaboration
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, List, Optional, Union, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import copy

# Project management libraries
try:
    import redis
    import asyncpg
    from datetime import datetime, timedelta
    import pandas as pd
    import numpy as np
except ImportError as e:
    logging.warning(f"Project management dependencies not available: {e}")

logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    """Project status states"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class TaskStatus(Enum):
    """Task status states"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Priority(Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class ResourceType(Enum):
    """Types of project resources"""
    TEAM_MEMBER = "team_member"
    EQUIPMENT = "equipment"
    BUDGET = "budget"
    SOFTWARE_LICENSE = "software_license"
    STORAGE_SPACE = "storage_space"
    RENDER_TIME = "render_time"

@dataclass
class Project:
    """Project representation"""
    project_id: str
    name: str
    description: str
    status: ProjectStatus
    priority: Priority
    created_by: str
    created_at: float
    start_date: Optional[float]
    end_date: Optional[float]
    deadline: Optional[float]
    budget: Optional[float]
    currency: str
    tags: List[str]
    metadata: Dict[str, Any]
    settings: Dict[str, Any]

@dataclass
class Task:
    """Task representation"""
    task_id: str
    project_id: str
    name: str
    description: str
    status: TaskStatus
    priority: Priority
    assigned_to: Optional[str]
    created_by: str
    created_at: float
    start_date: Optional[float]
    due_date: Optional[float]
    completed_at: Optional[float]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    parent_task_id: Optional[str]
    dependencies: List[str]  # Task IDs this task depends on
    tags: List[str]
    attachments: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class Milestone:
    """Milestone representation"""
    milestone_id: str
    project_id: str
    name: str
    description: str
    due_date: float
    completed_at: Optional[float]
    is_completed: bool
    tasks: List[str]  # Task IDs associated with milestone
    completion_criteria: List[str]
    created_by: str
    created_at: float

@dataclass
class Resource:
    """Resource representation"""
    resource_id: str
    name: str
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    unit: str  # hours, GB, licenses, etc.
    cost_per_unit: Optional[float]
    allocated_to: Dict[str, float]  # project_id -> allocated_amount
    metadata: Dict[str, Any]

@dataclass
class TimeEntry:
    """Time tracking entry"""
    entry_id: str
    user_id: str
    project_id: str
    task_id: Optional[str]
    start_time: float
    end_time: Optional[float]
    duration: float  # minutes
    description: str
    is_billable: bool
    hourly_rate: Optional[float]

class ProjectManagementEngine:
    """Core project management engine"""
    
    def __init__(self):
        self.projects = {}  # project_id -> Project
        self.tasks = {}  # task_id -> Task
        self.milestones = {}  # milestone_id -> Milestone
        self.resources = {}  # resource_id -> Resource
        self.time_entries = defaultdict(list)  # project_id -> [TimeEntry]
        
        self.project_teams = defaultdict(set)  # project_id -> set of user_ids
        self.user_tasks = defaultdict(list)  # user_id -> [task_ids]
        self.project_tasks = defaultdict(list)  # project_id -> [task_ids]
        
        # Database connections
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except:
            self.redis_client = None
            logger.warning("Redis not available for project caching")
        
        # Project settings
        self.default_currency = "USD"
        self.working_hours_per_day = 8
        self.working_days_per_week = 5
        
        # Notification callbacks
        self.notification_callbacks = []
    
    async def create_project(self, name: str, description: str, creator_id: str,
                           priority: Priority = Priority.MEDIUM,
                           start_date: Optional[float] = None,
                           end_date: Optional[float] = None,
                           budget: Optional[float] = None,
                           tags: List[str] = None,
                           settings: Dict[str, Any] = None) -> Project:
        """Create new project"""
        try:
            project_id = str(uuid.uuid4())
            
            project = Project(
                project_id=project_id,
                name=name,
                description=description,
                status=ProjectStatus.PLANNING,
                priority=priority,
                created_by=creator_id,
                created_at=time.time(),
                start_date=start_date,
                end_date=end_date,
                deadline=end_date,
                budget=budget,
                currency=self.default_currency,
                tags=tags or [],
                metadata={},
                settings=settings or {}
            )
            
            self.projects[project_id] = project
            self.project_teams[project_id].add(creator_id)
            
            # Store in persistent storage
            if self.redis_client:
                await self._store_project_redis(project)
            
            # Send notification
            await self._notify_project_created(project)
            
            logger.info(f"Created project {project_id}: {name}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    async def create_task(self, project_id: str, name: str, description: str,
                        creator_id: str, assigned_to: Optional[str] = None,
                        priority: Priority = Priority.MEDIUM,
                        due_date: Optional[float] = None,
                        estimated_hours: Optional[float] = None,
                        parent_task_id: Optional[str] = None,
                        dependencies: List[str] = None,
                        tags: List[str] = None) -> Task:
        """Create new task"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            task_id = str(uuid.uuid4())
            
            task = Task(
                task_id=task_id,
                project_id=project_id,
                name=name,
                description=description,
                status=TaskStatus.TODO,
                priority=priority,
                assigned_to=assigned_to,
                created_by=creator_id,
                created_at=time.time(),
                start_date=None,
                due_date=due_date,
                completed_at=None,
                estimated_hours=estimated_hours,
                actual_hours=None,
                parent_task_id=parent_task_id,
                dependencies=dependencies or [],
                tags=tags or [],
                attachments=[],
                metadata={}
            )
            
            self.tasks[task_id] = task
            self.project_tasks[project_id].append(task_id)
            
            if assigned_to:
                self.user_tasks[assigned_to].append(task_id)
            
            # Store in persistent storage
            if self.redis_client:
                await self._store_task_redis(task)
            
            # Send notification
            await self._notify_task_created(task)
            
            logger.info(f"Created task {task_id}: {name}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    async def update_task_status(self, task_id: str, new_status: TaskStatus,
                               user_id: str, notes: str = "") -> bool:
        """Update task status"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            old_status = task.status
            task.status = new_status
            
            # Handle status-specific updates
            if new_status == TaskStatus.IN_PROGRESS and not task.start_date:
                task.start_date = time.time()
            elif new_status == TaskStatus.COMPLETED:
                task.completed_at = time.time()
                await self._calculate_actual_hours(task)
            
            # Update in storage
            if self.redis_client:
                await self._store_task_redis(task)
            
            # Send notification
            await self._notify_task_status_changed(task, old_status, user_id, notes)
            
            # Check for project completion
            await self._check_project_completion(task.project_id)
            
            logger.info(f"Updated task {task_id} status to {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return False
    
    async def assign_task(self, task_id: str, assignee_id: str, assigner_id: str) -> bool:
        """Assign task to user"""
        try:
            task = self.tasks.get(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Remove from previous assignee
            if task.assigned_to:
                self.user_tasks[task.assigned_to].remove(task_id)
            
            # Assign to new user
            task.assigned_to = assignee_id
            self.user_tasks[assignee_id].append(task_id)
            
            # Update in storage
            if self.redis_client:
                await self._store_task_redis(task)
            
            # Send notification
            await self._notify_task_assigned(task, assignee_id, assigner_id)
            
            logger.info(f"Assigned task {task_id} to user {assignee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign task: {e}")
            return False
    
    async def create_milestone(self, project_id: str, name: str, description: str,
                             due_date: float, creator_id: str,
                             completion_criteria: List[str] = None) -> Milestone:
        """Create project milestone"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            milestone_id = str(uuid.uuid4())
            
            milestone = Milestone(
                milestone_id=milestone_id,
                project_id=project_id,
                name=name,
                description=description,
                due_date=due_date,
                completed_at=None,
                is_completed=False,
                tasks=[],
                completion_criteria=completion_criteria or [],
                created_by=creator_id,
                created_at=time.time()
            )
            
            self.milestones[milestone_id] = milestone
            
            # Send notification
            await self._notify_milestone_created(milestone)
            
            logger.info(f"Created milestone {milestone_id}: {name}")
            return milestone
            
        except Exception as e:
            logger.error(f"Failed to create milestone: {e}")
            raise
    
    async def add_team_member(self, project_id: str, user_id: str, role: str = "member") -> bool:
        """Add team member to project"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            self.project_teams[project_id].add(user_id)
            
            # Send notification
            await self._notify_team_member_added(project_id, user_id, role)
            
            logger.info(f"Added user {user_id} to project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add team member: {e}")
            return False
    
    async def log_time(self, user_id: str, project_id: str, duration: float,
                     description: str, task_id: Optional[str] = None,
                     is_billable: bool = True, hourly_rate: Optional[float] = None) -> TimeEntry:
        """Log time entry"""
        try:
            entry_id = str(uuid.uuid4())
            
            entry = TimeEntry(
                entry_id=entry_id,
                user_id=user_id,
                project_id=project_id,
                task_id=task_id,
                start_time=time.time() - (duration * 60),  # Calculate start time
                end_time=time.time(),
                duration=duration,
                description=description,
                is_billable=is_billable,
                hourly_rate=hourly_rate
            )
            
            self.time_entries[project_id].append(entry)
            
            # Update task actual hours if applicable
            if task_id and task_id in self.tasks:
                task = self.tasks[task_id]
                if task.actual_hours is None:
                    task.actual_hours = 0
                task.actual_hours += duration / 60  # Convert minutes to hours
            
            logger.info(f"Logged {duration} minutes for project {project_id}")
            return entry
            
        except Exception as e:
            logger.error(f"Failed to log time: {e}")
            raise
    
    async def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project progress"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Get all project tasks
            project_task_ids = self.project_tasks.get(project_id, [])
            project_tasks = [self.tasks[tid] for tid in project_task_ids if tid in self.tasks]
            
            # Calculate task statistics
            total_tasks = len(project_tasks)
            completed_tasks = len([t for t in project_tasks if t.status == TaskStatus.COMPLETED])
            in_progress_tasks = len([t for t in project_tasks if t.status == TaskStatus.IN_PROGRESS])
            blocked_tasks = len([t for t in project_tasks if t.status == TaskStatus.BLOCKED])
            
            # Calculate progress percentage
            progress_percentage = (completed_tasks / max(total_tasks, 1)) * 100
            
            # Calculate time statistics
            estimated_hours = sum(t.estimated_hours or 0 for t in project_tasks)
            actual_hours = sum(t.actual_hours or 0 for t in project_tasks)
            
            # Calculate budget utilization
            time_entries = self.time_entries.get(project_id, [])
            billable_hours = sum(e.duration / 60 for e in time_entries if e.is_billable)
            
            # Get milestones
            project_milestones = [m for m in self.milestones.values() if m.project_id == project_id]
            completed_milestones = len([m for m in project_milestones if m.is_completed])
            
            # Timeline analysis
            timeline_status = await self._analyze_project_timeline(project, project_tasks)
            
            return {
                'project_id': project_id,
                'project_name': project.name,
                'status': project.status.value,
                'progress_percentage': round(progress_percentage, 2),
                'tasks': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'in_progress': in_progress_tasks,
                    'blocked': blocked_tasks,
                    'todo': total_tasks - completed_tasks - in_progress_tasks - blocked_tasks
                },
                'time': {
                    'estimated_hours': estimated_hours,
                    'actual_hours': actual_hours,
                    'billable_hours': billable_hours,
                    'efficiency': (estimated_hours / max(actual_hours, 1)) * 100 if actual_hours > 0 else 0
                },
                'milestones': {
                    'total': len(project_milestones),
                    'completed': completed_milestones
                },
                'timeline': timeline_status,
                'team_size': len(self.project_teams.get(project_id, set()))
            }
            
        except Exception as e:
            logger.error(f"Failed to get project progress: {e}")
            return {}
    
    async def get_user_workload(self, user_id: str) -> Dict[str, Any]:
        """Get user workload analysis"""
        try:
            user_task_ids = self.user_tasks.get(user_id, [])
            user_tasks = [self.tasks[tid] for tid in user_task_ids if tid in self.tasks]
            
            # Filter active tasks
            active_tasks = [t for t in user_tasks if t.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]]
            
            # Calculate workload
            total_estimated_hours = sum(t.estimated_hours or 0 for t in active_tasks)
            high_priority_tasks = len([t for t in active_tasks if t.priority in [Priority.HIGH, Priority.CRITICAL, Priority.URGENT]])
            overdue_tasks = len([t for t in active_tasks if t.due_date and t.due_date < time.time()])
            
            # Get projects user is involved in
            user_projects = set()
            for task in user_tasks:
                user_projects.add(task.project_id)
            
            # Recent time entries
            recent_entries = []
            cutoff = time.time() - (7 * 24 * 3600)  # Last 7 days
            for project_id in user_projects:
                entries = self.time_entries.get(project_id, [])
                user_entries = [e for e in entries if e.user_id == user_id and e.start_time > cutoff]
                recent_entries.extend(user_entries)
            
            weekly_hours = sum(e.duration / 60 for e in recent_entries)
            
            return {
                'user_id': user_id,
                'active_tasks': len(active_tasks),
                'high_priority_tasks': high_priority_tasks,
                'overdue_tasks': overdue_tasks,
                'estimated_workload_hours': total_estimated_hours,
                'weekly_hours_logged': weekly_hours,
                'projects_involved': len(user_projects),
                'workload_status': self._calculate_workload_status(total_estimated_hours, weekly_hours)
            }
            
        except Exception as e:
            logger.error(f"Failed to get user workload: {e}")
            return {}
    
    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project analytics"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Get project data
            project_tasks = [self.tasks[tid] for tid in self.project_tasks.get(project_id, []) if tid in self.tasks]
            time_entries = self.time_entries.get(project_id, [])
            team_members = self.project_teams.get(project_id, set())
            
            # Task analytics
            task_analytics = self._analyze_tasks(project_tasks)
            
            # Time analytics
            time_analytics = self._analyze_time_entries(time_entries)
            
            # Team analytics
            team_analytics = self._analyze_team_performance(team_members, project_tasks, time_entries)
            
            # Risk assessment
            risk_assessment = await self._assess_project_risks(project, project_tasks)
            
            # Predictions
            predictions = await self._predict_project_completion(project, project_tasks)
            
            return {
                'project_id': project_id,
                'generated_at': time.time(),
                'task_analytics': task_analytics,
                'time_analytics': time_analytics,
                'team_analytics': team_analytics,
                'risk_assessment': risk_assessment,
                'predictions': predictions
            }
            
        except Exception as e:
            logger.error(f"Failed to get project analytics: {e}")
            return {}
    
    async def _calculate_actual_hours(self, task: Task):
        """Calculate actual hours from time entries"""
        try:
            task_entries = []
            for project_entries in self.time_entries.values():
                task_entries.extend([e for e in project_entries if e.task_id == task.task_id])
            
            if task_entries:
                total_minutes = sum(e.duration for e in task_entries)
                task.actual_hours = total_minutes / 60
            
        except Exception as e:
            logger.error(f"Failed to calculate actual hours: {e}")
    
    async def _check_project_completion(self, project_id: str):
        """Check if project should be marked as completed"""
        try:
            project_task_ids = self.project_tasks.get(project_id, [])
            project_tasks = [self.tasks[tid] for tid in project_task_ids if tid in self.tasks]
            
            if project_tasks:
                completed_tasks = [t for t in project_tasks if t.status == TaskStatus.COMPLETED]
                if len(completed_tasks) == len(project_tasks):
                    project = self.projects[project_id]
                    project.status = ProjectStatus.COMPLETED
                    await self._notify_project_completed(project)
            
        except Exception as e:
            logger.error(f"Failed to check project completion: {e}")
    
    async def _analyze_project_timeline(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze project timeline status"""
        try:
            current_time = time.time()
            
            # Check if project has started
            if project.start_date and current_time < project.start_date:
                status = "not_started"
            elif project.end_date and current_time > project.end_date:
                status = "overdue"
            elif project.deadline and current_time > project.deadline:
                status = "past_deadline"
            else:
                status = "on_track"
            
            # Calculate timeline progress
            if project.start_date and project.end_date:
                total_duration = project.end_date - project.start_date
                elapsed_duration = current_time - project.start_date
                timeline_progress = min(max(elapsed_duration / total_duration, 0), 1) * 100
            else:
                timeline_progress = 0
            
            # Check for delayed tasks
            overdue_tasks = [t for t in tasks if t.due_date and t.due_date < current_time and t.status != TaskStatus.COMPLETED]
            
            return {
                'status': status,
                'timeline_progress': round(timeline_progress, 2),
                'overdue_tasks': len(overdue_tasks),
                'days_remaining': (project.end_date - current_time) / 86400 if project.end_date else None
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze project timeline: {e}")
            return {}
    
    def _calculate_workload_status(self, estimated_hours: float, weekly_hours: float) -> str:
        """Calculate workload status"""
        try:
            weekly_capacity = self.working_hours_per_day * self.working_days_per_week
            utilization = weekly_hours / weekly_capacity if weekly_capacity > 0 else 0
            
            if utilization < 0.5:
                return "underutilized"
            elif utilization < 0.8:
                return "normal"
            elif utilization < 1.2:
                return "high"
            else:
                return "overloaded"
                
        except Exception as e:
            logger.error(f"Failed to calculate workload status: {e}")
            return "unknown"
    
    def _analyze_tasks(self, tasks: List[Task]) -> Dict[str, Any]:
        """Analyze task patterns and metrics"""
        try:
            total_tasks = len(tasks)
            if total_tasks == 0:
                return {}
            
            # Status distribution
            status_counts = defaultdict(int)
            for task in tasks:
                status_counts[task.status.value] += 1
            
            # Priority distribution
            priority_counts = defaultdict(int)
            for task in tasks:
                priority_counts[task.priority.value] += 1
            
            # Time analysis
            estimated_total = sum(t.estimated_hours or 0 for t in tasks)
            actual_total = sum(t.actual_hours or 0 for t in tasks if t.actual_hours)
            
            return {
                'total_tasks': total_tasks,
                'status_distribution': dict(status_counts),
                'priority_distribution': dict(priority_counts),
                'time_estimation_accuracy': (estimated_total / max(actual_total, 1)) * 100 if actual_total > 0 else 0,
                'average_task_completion_time': actual_total / len([t for t in tasks if t.actual_hours]) if any(t.actual_hours for t in tasks) else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze tasks: {e}")
            return {}
    
    def _analyze_time_entries(self, time_entries: List[TimeEntry]) -> Dict[str, Any]:
        """Analyze time entry patterns"""
        try:
            if not time_entries:
                return {}
            
            total_time = sum(e.duration for e in time_entries) / 60  # Convert to hours
            billable_time = sum(e.duration for e in time_entries if e.is_billable) / 60
            
            # Daily averages
            days_with_entries = len(set(datetime.fromtimestamp(e.start_time).date() for e in time_entries))
            daily_average = total_time / max(days_with_entries, 1)
            
            return {
                'total_hours': round(total_time, 2),
                'billable_hours': round(billable_time, 2),
                'billable_percentage': round((billable_time / max(total_time, 1)) * 100, 2),
                'daily_average_hours': round(daily_average, 2),
                'total_entries': len(time_entries)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze time entries: {e}")
            return {}
    
    def _analyze_team_performance(self, team_members: Set[str], 
                                tasks: List[Task], time_entries: List[TimeEntry]) -> Dict[str, Any]:
        """Analyze team performance metrics"""
        try:
            if not team_members:
                return {}
            
            # Task assignments
            assigned_tasks = defaultdict(int)
            completed_tasks = defaultdict(int)
            
            for task in tasks:
                if task.assigned_to:
                    assigned_tasks[task.assigned_to] += 1
                    if task.status == TaskStatus.COMPLETED:
                        completed_tasks[task.assigned_to] += 1
            
            # Time contributions
            time_contributions = defaultdict(float)
            for entry in time_entries:
                time_contributions[entry.user_id] += entry.duration / 60
            
            # Calculate team metrics
            team_size = len(team_members)
            avg_tasks_per_member = sum(assigned_tasks.values()) / max(team_size, 1)
            avg_completion_rate = sum(completed_tasks[uid] / max(assigned_tasks[uid], 1) for uid in team_members) / max(team_size, 1)
            
            return {
                'team_size': team_size,
                'average_tasks_per_member': round(avg_tasks_per_member, 2),
                'average_completion_rate': round(avg_completion_rate * 100, 2),
                'total_team_hours': round(sum(time_contributions.values()), 2),
                'most_active_members': sorted(time_contributions.items(), key=lambda x: x[1], reverse=True)[:3]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze team performance: {e}")
            return {}
    
    async def _assess_project_risks(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Assess project risks"""
        try:
            risks = []
            risk_score = 0
            
            # Timeline risks
            current_time = time.time()
            if project.deadline and current_time > project.deadline:
                risks.append("Project is past deadline")
                risk_score += 30
            
            # Task completion risks
            overdue_tasks = [t for t in tasks if t.due_date and t.due_date < current_time and t.status != TaskStatus.COMPLETED]
            if len(overdue_tasks) > len(tasks) * 0.2:  # More than 20% overdue
                risks.append("High number of overdue tasks")
                risk_score += 25
            
            # Blocked tasks
            blocked_tasks = [t for t in tasks if t.status == TaskStatus.BLOCKED]
            if len(blocked_tasks) > 0:
                risks.append(f"{len(blocked_tasks)} tasks are blocked")
                risk_score += len(blocked_tasks) * 5
            
            # Resource risks
            unassigned_tasks = [t for t in tasks if not t.assigned_to and t.status == TaskStatus.TODO]
            if len(unassigned_tasks) > 0:
                risks.append(f"{len(unassigned_tasks)} tasks are unassigned")
                risk_score += len(unassigned_tasks) * 2
            
            # Determine risk level
            if risk_score < 20:
                risk_level = "low"
            elif risk_score < 50:
                risk_level = "medium"
            elif risk_score < 80:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            return {
                'risk_level': risk_level,
                'risk_score': min(risk_score, 100),
                'identified_risks': risks,
                'mitigation_suggestions': self._get_risk_mitigation_suggestions(risks)
            }
            
        except Exception as e:
            logger.error(f"Failed to assess project risks: {e}")
            return {}
    
    async def _predict_project_completion(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Predict project completion"""
        try:
            if not tasks:
                return {}
            
            # Calculate velocity based on completed tasks
            completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED and t.completed_at]
            
            if len(completed_tasks) < 2:
                return {'prediction_available': False, 'reason': 'Insufficient completed tasks for prediction'}
            
            # Calculate average completion time
            completion_times = []
            for task in completed_tasks:
                if task.start_date and task.completed_at:
                    completion_times.append(task.completed_at - task.start_date)
            
            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)
                remaining_tasks = len([t for t in tasks if t.status != TaskStatus.COMPLETED])
                
                predicted_completion_time = time.time() + (remaining_tasks * avg_completion_time)
                
                # Compare with deadline
                on_schedule = True
                if project.deadline and predicted_completion_time > project.deadline:
                    on_schedule = False
                
                return {
                    'prediction_available': True,
                    'predicted_completion_date': predicted_completion_time,
                    'remaining_tasks': remaining_tasks,
                    'on_schedule': on_schedule,
                    'confidence': min(len(completed_tasks) / 10, 1.0)  # Higher confidence with more data
                }
            
            return {'prediction_available': False, 'reason': 'Unable to calculate completion velocity'}
            
        except Exception as e:
            logger.error(f"Failed to predict project completion: {e}")
            return {}
    
    def _get_risk_mitigation_suggestions(self, risks: List[str]) -> List[str]:
        """Get suggestions for risk mitigation"""
        suggestions = []
        
        for risk in risks:
            if "overdue" in risk.lower():
                suggestions.append("Reassign or break down overdue tasks")
            elif "blocked" in risk.lower():
                suggestions.append("Identify and resolve task blockers")
            elif "unassigned" in risk.lower():
                suggestions.append("Assign tasks to available team members")
            elif "deadline" in risk.lower():
                suggestions.append("Consider deadline extension or scope reduction")
        
        return suggestions
    
    # Notification methods
    async def _notify_project_created(self, project: Project):
        """Notify about project creation"""
        # Implementation for project creation notification
        pass
    
    async def _notify_task_created(self, task: Task):
        """Notify about task creation"""
        # Implementation for task creation notification
        pass
    
    async def _notify_task_status_changed(self, task: Task, old_status: TaskStatus, user_id: str, notes: str):
        """Notify about task status change"""
        # Implementation for task status change notification
        pass
    
    async def _notify_task_assigned(self, task: Task, assignee_id: str, assigner_id: str):
        """Notify about task assignment"""
        # Implementation for task assignment notification
        pass
    
    async def _notify_milestone_created(self, milestone: Milestone):
        """Notify about milestone creation"""
        # Implementation for milestone creation notification
        pass
    
    async def _notify_team_member_added(self, project_id: str, user_id: str, role: str):
        """Notify about team member addition"""
        # Implementation for team member addition notification
        pass
    
    async def _notify_project_completed(self, project: Project):
        """Notify about project completion"""
        # Implementation for project completion notification
        pass
    
    # Storage methods
    async def _store_project_redis(self, project: Project):
        """Store project in Redis"""
        try:
            if self.redis_client:
                key = f"project:{project.project_id}"
                value = json.dumps(asdict(project), default=str)
                self.redis_client.setex(key, 86400, value)
                
        except Exception as e:
            logger.error(f"Failed to store project in Redis: {e}")
    
    async def _store_task_redis(self, task: Task):
        """Store task in Redis"""
        try:
            if self.redis_client:
                key = f"task:{task.task_id}"
                value = json.dumps(asdict(task), default=str)
                self.redis_client.setex(key, 86400, value)
                
        except Exception as e:
            logger.error(f"Failed to store task in Redis: {e}")

class CollaborativeProjectManager:
    """High-level collaborative project management"""
    
    def __init__(self):
        self.project_engine = ProjectManagementEngine()
        self.project_templates = self._load_project_templates()
    
    async def create_multimedia_project(self, name: str, project_type: str,
                                      creator_id: str, team_members: List[str] = None) -> Project:
        """Create multimedia project from template"""
        try:
            template = self.project_templates.get(project_type)
            if not template:
                raise ValueError(f"Project template {project_type} not found")
            
            # Create project
            project = await self.project_engine.create_project(
                name=name,
                description=template['description'],
                creator_id=creator_id,
                priority=Priority(template['priority']),
                settings=template['settings']
            )
            
            # Add team members
            if team_members:
                for member_id in team_members:
                    await self.project_engine.add_team_member(project.project_id, member_id)
            
            # Create template tasks
            for task_template in template['tasks']:
                await self.project_engine.create_task(
                    project_id=project.project_id,
                    name=task_template['name'],
                    description=task_template['description'],
                    creator_id=creator_id,
                    priority=Priority(task_template['priority']),
                    estimated_hours=task_template.get('estimated_hours')
                )
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to create multimedia project: {e}")
            raise
    
    def _load_project_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined project templates"""
        return {
            'video_production': {
                'description': 'Professional video production project',
                'priority': 'high',
                'settings': {
                    'workflow_type': 'video_production',
                    'approval_stages': ['rough_cut', 'fine_cut', 'final'],
                    'deliverables': ['raw_footage', 'edited_video', 'final_export']
                },
                'tasks': [
                    {
                        'name': 'Pre-production Planning',
                        'description': 'Script, storyboard, and production planning',
                        'priority': 'high',
                        'estimated_hours': 16
                    },
                    {
                        'name': 'Video Shooting',
                        'description': 'Capture video footage',
                        'priority': 'high',
                        'estimated_hours': 24
                    },
                    {
                        'name': 'Video Editing',
                        'description': 'Edit and assemble video content',
                        'priority': 'high',
                        'estimated_hours': 32
                    },
                    {
                        'name': 'Color Correction',
                        'description': 'Color grading and correction',
                        'priority': 'medium',
                        'estimated_hours': 8
                    },
                    {
                        'name': 'Audio Post-production',
                        'description': 'Audio editing and mixing',
                        'priority': 'medium',
                        'estimated_hours': 12
                    },
                    {
                        'name': 'Final Review',
                        'description': 'Final review and approval',
                        'priority': 'high',
                        'estimated_hours': 4
                    }
                ]
            },
            'podcast_production': {
                'description': 'Podcast recording and production project',
                'priority': 'medium',
                'settings': {
                    'workflow_type': 'audio_production',
                    'approval_stages': ['rough_edit', 'final_edit'],
                    'deliverables': ['raw_audio', 'edited_podcast', 'transcript']
                },
                'tasks': [
                    {
                        'name': 'Episode Planning',
                        'description': 'Plan episode content and structure',
                        'priority': 'high',
                        'estimated_hours': 4
                    },
                    {
                        'name': 'Recording Session',
                        'description': 'Record podcast episode',
                        'priority': 'high',
                        'estimated_hours': 3
                    },
                    {
                        'name': 'Audio Editing',
                        'description': 'Edit and clean audio',
                        'priority': 'high',
                        'estimated_hours': 6
                    },
                    {
                        'name': 'Show Notes Creation',
                        'description': 'Create episode description and notes',
                        'priority': 'medium',
                        'estimated_hours': 2
                    },
                    {
                        'name': 'Publishing',
                        'description': 'Upload and publish episode',
                        'priority': 'medium',
                        'estimated_hours': 1
                    }
                ]
            }
        }

# Module exports
__all__ = [
    'ProjectManagementEngine',
    'CollaborativeProjectManager',
    'Project',
    'Task',
    'Milestone',
    'Resource',
    'TimeEntry',
    'ProjectStatus',
    'TaskStatus',
    'Priority',
    'ResourceType'
]