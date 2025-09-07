"""Media Project Manager - Advanced Project Coordination System

Enterprise-grade project management system for coordinating complex media projects,
managing timelines, resources, and deliverables across multiple creators and teams.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path
import uuid
from collections import defaultdict

# External dependencies with graceful fallbacks
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory storage")

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    logging.warning("SQLAlchemy async not available - using basic storage")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project status types"""
    PLANNING = "planning"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class ProjectType(Enum):
    """Project types for media creation"""
    VIDEO_PRODUCTION = "video_production"
    AUDIO_PRODUCTION = "audio_production" 
    PODCAST_SERIES = "podcast_series"
    IMAGE_CAMPAIGN = "image_campaign"
    CONTENT_SERIES = "content_series"
    COLLABORATION = "collaboration"
    REMIX_PROJECT = "remix_project"
    MULTI_CREATOR = "multi_creator"
    BRANDED_CONTENT = "branded_content"
    LIVE_EVENT = "live_event"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class ResourceType(Enum):
    """Resource types for project management"""
    HUMAN = "human"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    STUDIO = "studio"
    BUDGET = "budget"
    EXTERNAL = "external"


@dataclass
class ProjectMilestone:
    """Project milestone definition"""
    id: str
    name: str
    description: str
    due_date: datetime
    dependencies: List[str] = field(default_factory=list)
    completion_criteria: Dict[str, Any] = field(default_factory=dict)
    assigned_to: List[str] = field(default_factory=list)
    status: str = "pending"
    completion_date: Optional[datetime] = None
    deliverables: List[str] = field(default_factory=list)


@dataclass
class ProjectTask:
    """Individual project task"""
    id: str
    name: str
    description: str
    assignee: str
    due_date: datetime
    priority: TaskPriority
    estimated_hours: float
    actual_hours: float = 0.0
    status: str = "todo"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ProjectResource:
    """Project resource allocation"""
    id: str
    name: str
    type: ResourceType
    availability: Dict[str, Any]
    cost_per_hour: float = 0.0
    allocated_hours: float = 0.0
    used_hours: float = 0.0
    booking_schedule: Dict[str, List[Tuple[datetime, datetime]]] = field(default_factory=dict)


@dataclass
class MediaProject:
    """Comprehensive media project definition"""
    id: str
    name: str
    description: str
    type: ProjectType
    status: ProjectStatus
    created_by: str
    created_at: datetime
    
    # Timeline and scheduling
    start_date: datetime
    target_end_date: datetime
    actual_end_date: Optional[datetime] = None
    
    # Team and collaboration
    team_members: List[str] = field(default_factory=list)
    collaborators: List[str] = field(default_factory=list)
    project_manager: Optional[str] = None
    
    # Project structure
    milestones: List[ProjectMilestone] = field(default_factory=list)
    tasks: List[ProjectTask] = field(default_factory=list)
    resources: List[ProjectResource] = field(default_factory=list)
    
    # Budget and finances
    budget: float = 0.0
    actual_cost: float = 0.0
    revenue_target: float = 0.0
    
    # Content and deliverables
    content_assets: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    
    # Metadata and tracking
    tags: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    progress_percentage: float = 0.0
    
    # Communication and updates
    communication_channel: Optional[str] = None
    update_frequency: str = "weekly"
    last_update: Optional[datetime] = None
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MediaProjectManager:
    """Advanced media project management system"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize project manager
        
        Args:
            redis_url: Optional Redis connection URL for distributed storage
        """
        self.projects: Dict[str, MediaProject] = {}
        self.project_templates: Dict[str, Dict[str, Any]] = {}
        self.notification_handlers: List[Callable] = []
        
        # Initialize Redis if available
        self.redis_client = None
        if HAS_REDIS and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info("Connected to Redis for project storage")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
        
        # Load default project templates
        self._load_default_templates()
        
        logger.info("MediaProjectManager initialized successfully")
    
    def _load_default_templates(self):
        """Load default project templates"""
        self.project_templates = {
            "video_production": {
                "name": "Video Production Project",
                "milestones": [
                    {"name": "Pre-production", "duration_days": 7},
                    {"name": "Production", "duration_days": 14}, 
                    {"name": "Post-production", "duration_days": 21},
                    {"name": "Review & Approval", "duration_days": 5},
                    {"name": "Final Delivery", "duration_days": 2}
                ],
                "required_resources": ["video_editor", "sound_engineer", "equipment"],
                "estimated_hours": 120
            },
            "podcast_series": {
                "name": "Podcast Series Project",
                "milestones": [
                    {"name": "Content Planning", "duration_days": 5},
                    {"name": "Recording", "duration_days": 10},
                    {"name": "Editing", "duration_days": 15},
                    {"name": "Publishing", "duration_days": 3}
                ],
                "required_resources": ["podcast_host", "audio_editor", "studio"],
                "estimated_hours": 80
            },
            "collaboration": {
                "name": "Creator Collaboration",
                "milestones": [
                    {"name": "Partnership Setup", "duration_days": 3},
                    {"name": "Content Creation", "duration_days": 14},
                    {"name": "Review & Integration", "duration_days": 7},
                    {"name": "Launch Campaign", "duration_days": 5}
                ],
                "required_resources": ["collaboration_manager", "creators"],
                "estimated_hours": 60
            }
        }
    
    async def create_project(self, project_data: Dict[str, Any], template: Optional[str] = None) -> str:
        """Create a new media project
        
        Args:
            project_data: Project information
            template: Optional template to use
            
        Returns:
            Project ID
        """
        try:
            project_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Apply template if specified
            if template and template in self.project_templates:
                template_data = self.project_templates[template].copy()
                project_data = {**template_data, **project_data}
            
            # Create project
            project = MediaProject(
                id=project_id,
                name=project_data.get("name", f"Project {project_id[:8]}"),
                description=project_data.get("description", ""),
                type=ProjectType(project_data.get("type", "content_series")),
                status=ProjectStatus.PLANNING,
                created_by=project_data.get("created_by", "system"),
                created_at=now,
                start_date=project_data.get("start_date", now),
                target_end_date=project_data.get("target_end_date", now + timedelta(days=30)),
                budget=project_data.get("budget", 0.0),
                revenue_target=project_data.get("revenue_target", 0.0)
            )
            
            # Add team members
            if "team_members" in project_data:
                project.team_members = project_data["team_members"]
            
            # Create milestones from template
            if "milestones" in project_data:
                for milestone_data in project_data["milestones"]:
                    milestone = ProjectMilestone(
                        id=str(uuid.uuid4()),
                        name=milestone_data["name"],
                        description=milestone_data.get("description", ""),
                        due_date=project.start_date + timedelta(days=milestone_data.get("duration_days", 7))
                    )
                    project.milestones.append(milestone)
            
            # Store project
            self.projects[project_id] = project
            await self._save_project(project)
            
            # Send notification
            await self._notify_project_created(project)
            
            logger.info(f"Created project {project_id}: {project.name}")
            return project_id
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def get_project(self, project_id: str) -> Optional[MediaProject]:
        """Get project by ID
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project object or None
        """
        try:
            if project_id in self.projects:
                return self.projects[project_id]
            
            # Try loading from Redis
            project = await self._load_project(project_id)
            if project:
                self.projects[project_id] = project
                return project
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            return None
    
    async def update_project_status(self, project_id: str, status: ProjectStatus) -> bool:
        """Update project status
        
        Args:
            project_id: Project identifier
            status: New project status
            
        Returns:
            Success status
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return False
            
            old_status = project.status
            project.status = status
            project.updated_at = datetime.now(timezone.utc)
            
            if status == ProjectStatus.COMPLETED:
                project.actual_end_date = datetime.now(timezone.utc)
                project.progress_percentage = 100.0
            
            await self._save_project(project)
            await self._notify_status_change(project, old_status, status)
            
            logger.info(f"Updated project {project_id} status: {old_status} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating project status: {e}")
            return False
    
    async def add_task(self, project_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Add task to project
        
        Args:
            project_id: Project identifier
            task_data: Task information
            
        Returns:
            Task ID or None
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return None
            
            task_id = str(uuid.uuid4())
            task = ProjectTask(
                id=task_id,
                name=task_data["name"],
                description=task_data.get("description", ""),
                assignee=task_data["assignee"],
                due_date=datetime.fromisoformat(task_data["due_date"]) if isinstance(task_data["due_date"], str) else task_data["due_date"],
                priority=TaskPriority(task_data.get("priority", "medium")),
                estimated_hours=task_data.get("estimated_hours", 8.0)
            )
            
            project.tasks.append(task)
            project.updated_at = datetime.now(timezone.utc)
            
            await self._save_project(project)
            await self._notify_task_assigned(project, task)
            
            logger.info(f"Added task {task_id} to project {project_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return None
    
    async def update_task_status(self, project_id: str, task_id: str, status: str, 
                               actual_hours: Optional[float] = None) -> bool:
        """Update task status and progress
        
        Args:
            project_id: Project identifier
            task_id: Task identifier
            status: New task status
            actual_hours: Actual hours spent
            
        Returns:
            Success status
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return False
            
            task = next((t for t in project.tasks if t.id == task_id), None)
            if not task:
                return False
            
            old_status = task.status
            task.status = status
            task.updated_at = datetime.now(timezone.utc)
            
            if actual_hours is not None:
                task.actual_hours = actual_hours
            
            # Update project progress
            await self._update_project_progress(project)
            await self._save_project(project)
            
            if status == "completed":
                await self._notify_task_completed(project, task)
            
            logger.info(f"Updated task {task_id} status: {old_status} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    async def get_project_timeline(self, project_id: str) -> Dict[str, Any]:
        """Get project timeline and critical path
        
        Args:
            project_id: Project identifier
            
        Returns:
            Timeline information
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return {}
            
            timeline = {
                "project_id": project_id,
                "start_date": project.start_date.isoformat(),
                "target_end_date": project.target_end_date.isoformat(),
                "actual_end_date": project.actual_end_date.isoformat() if project.actual_end_date else None,
                "milestones": [],
                "tasks": [],
                "critical_path": [],
                "progress": project.progress_percentage
            }
            
            # Add milestones
            for milestone in project.milestones:
                timeline["milestones"].append({
                    "id": milestone.id,
                    "name": milestone.name,
                    "due_date": milestone.due_date.isoformat(),
                    "status": milestone.status,
                    "completion_date": milestone.completion_date.isoformat() if milestone.completion_date else None
                })
            
            # Add tasks
            for task in project.tasks:
                timeline["tasks"].append({
                    "id": task.id,
                    "name": task.name,
                    "assignee": task.assignee,
                    "due_date": task.due_date.isoformat(),
                    "status": task.status,
                    "priority": task.priority.value,
                    "estimated_hours": task.estimated_hours,
                    "actual_hours": task.actual_hours
                })
            
            # Calculate critical path (simplified)
            critical_tasks = [task for task in project.tasks if task.priority in [TaskPriority.CRITICAL, TaskPriority.URGENT]]
            timeline["critical_path"] = [{"id": task.id, "name": task.name} for task in critical_tasks]
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting project timeline: {e}")
            return {}
    
    async def get_resource_allocation(self, project_id: str) -> Dict[str, Any]:
        """Get resource allocation and availability
        
        Args:
            project_id: Project identifier
            
        Returns:
            Resource allocation information
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return {}
            
            allocation = {
                "project_id": project_id,
                "total_budget": project.budget,
                "actual_cost": project.actual_cost,
                "budget_remaining": project.budget - project.actual_cost,
                "resources": [],
                "utilization": {}
            }
            
            # Add resource details
            for resource in project.resources:
                allocation["resources"].append({
                    "id": resource.id,
                    "name": resource.name,
                    "type": resource.type.value,
                    "allocated_hours": resource.allocated_hours,
                    "used_hours": resource.used_hours,
                    "cost_per_hour": resource.cost_per_hour,
                    "total_cost": resource.used_hours * resource.cost_per_hour,
                    "utilization": (resource.used_hours / resource.allocated_hours * 100) if resource.allocated_hours > 0 else 0
                })
            
            # Calculate overall utilization
            total_allocated = sum(r.allocated_hours for r in project.resources)
            total_used = sum(r.used_hours for r in project.resources)
            allocation["utilization"]["overall"] = (total_used / total_allocated * 100) if total_allocated > 0 else 0
            
            return allocation
            
        except Exception as e:
            logger.error(f"Error getting resource allocation: {e}")
            return {}
    
    async def get_team_workload(self, team_member: str) -> Dict[str, Any]:
        """Get workload analysis for team member
        
        Args:
            team_member: Team member identifier
            
        Returns:
            Workload information
        """
        try:
            workload = {
                "team_member": team_member,
                "active_projects": [],
                "total_tasks": 0,
                "pending_tasks": 0,
                "completed_tasks": 0,
                "overdue_tasks": 0,
                "estimated_hours": 0.0,
                "actual_hours": 0.0,
                "workload_score": 0.0
            }
            
            now = datetime.now(timezone.utc)
            
            # Analyze all projects
            for project in self.projects.values():
                if team_member in project.team_members or team_member in project.collaborators:
                    workload["active_projects"].append({
                        "id": project.id,
                        "name": project.name,
                        "status": project.status.value,
                        "role": "manager" if project.project_manager == team_member else "member"
                    })
                
                # Analyze tasks assigned to team member
                member_tasks = [task for task in project.tasks if task.assignee == team_member]
                for task in member_tasks:
                    workload["total_tasks"] += 1
                    workload["estimated_hours"] += task.estimated_hours
                    workload["actual_hours"] += task.actual_hours
                    
                    if task.status == "completed":
                        workload["completed_tasks"] += 1
                    elif task.status in ["todo", "in_progress"]:
                        workload["pending_tasks"] += 1
                        
                        if task.due_date < now:
                            workload["overdue_tasks"] += 1
            
            # Calculate workload score (0-100, where 100 is overloaded)
            if workload["total_tasks"] > 0:
                completion_rate = workload["completed_tasks"] / workload["total_tasks"]
                overdue_rate = workload["overdue_tasks"] / workload["total_tasks"]
                
                workload["workload_score"] = min(100, 
                    (workload["pending_tasks"] * 10) + 
                    (workload["overdue_tasks"] * 20) + 
                    ((1 - completion_rate) * 30)
                )
            
            return workload
            
        except Exception as e:
            logger.error(f"Error getting team workload: {e}")
            return {}
    
    async def generate_project_report(self, project_id: str) -> Dict[str, Any]:
        """Generate comprehensive project report
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project report
        """
        try:
            project = await self.get_project(project_id)
            if not project:
                return {}
            
            now = datetime.now(timezone.utc)
            
            # Basic project information
            report = {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "type": project.type.value,
                    "status": project.status.value,
                    "created_by": project.created_by,
                    "created_at": project.created_at.isoformat(),
                    "start_date": project.start_date.isoformat(),
                    "target_end_date": project.target_end_date.isoformat(),
                    "progress": project.progress_percentage
                },
                "timeline": await self.get_project_timeline(project_id),
                "resources": await self.get_resource_allocation(project_id),
                "team": {
                    "members": project.team_members,
                    "collaborators": project.collaborators,
                    "project_manager": project.project_manager
                },
                "financials": {
                    "budget": project.budget,
                    "actual_cost": project.actual_cost,
                    "revenue_target": project.revenue_target,
                    "budget_variance": project.budget - project.actual_cost,
                    "roi_projection": ((project.revenue_target - project.actual_cost) / project.actual_cost * 100) if project.actual_cost > 0 else 0
                },
                "performance": {
                    "total_tasks": len(project.tasks),
                    "completed_tasks": len([t for t in project.tasks if t.status == "completed"]),
                    "overdue_tasks": len([t for t in project.tasks if t.due_date < now and t.status != "completed"]),
                    "on_schedule": project.target_end_date > now if project.status != ProjectStatus.COMPLETED else True
                },
                "generated_at": now.isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating project report: {e}")
            return {}
    
    async def _update_project_progress(self, project: MediaProject):
        """Update project progress based on task completion"""
        if not project.tasks:
            return
        
        completed_tasks = len([task for task in project.tasks if task.status == "completed"])
        project.progress_percentage = (completed_tasks / len(project.tasks)) * 100
    
    async def _save_project(self, project: MediaProject):
        """Save project to storage"""
        if self.redis_client:
            try:
                project_data = json.dumps(project, default=str, ensure_ascii=False)
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.set, f"project:{project.id}", project_data
                )
            except Exception as e:
                logger.warning(f"Failed to save project to Redis: {e}")
    
    async def _load_project(self, project_id: str) -> Optional[MediaProject]:
        """Load project from storage"""
        if self.redis_client:
            try:
                project_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.get, f"project:{project_id}"
                )
                if project_data:
                    # Note: In a real implementation, you'd properly deserialize the project
                    # This is a simplified version
                    return None
            except Exception as e:
                logger.warning(f"Failed to load project from Redis: {e}")
        
        return None
    
    async def _notify_project_created(self, project: MediaProject):
        """Send project creation notification"""
        for handler in self.notification_handlers:
            try:
                await handler("project_created", {
                    "project_id": project.id,
                    "project_name": project.name,
                    "created_by": project.created_by
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_status_change(self, project: MediaProject, old_status: ProjectStatus, new_status: ProjectStatus):
        """Send status change notification"""
        for handler in self.notification_handlers:
            try:
                await handler("status_change", {
                    "project_id": project.id,
                    "project_name": project.name,
                    "old_status": old_status.value,
                    "new_status": new_status.value
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_task_assigned(self, project: MediaProject, task: ProjectTask):
        """Send task assignment notification"""
        for handler in self.notification_handlers:
            try:
                await handler("task_assigned", {
                    "project_id": project.id,
                    "task_id": task.id,
                    "task_name": task.name,
                    "assignee": task.assignee,
                    "due_date": task.due_date.isoformat()
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_task_completed(self, project: MediaProject, task: ProjectTask):
        """Send task completion notification"""
        for handler in self.notification_handlers:
            try:
                await handler("task_completed", {
                    "project_id": project.id,
                    "task_id": task.id,
                    "task_name": task.name,
                    "assignee": task.assignee,
                    "actual_hours": task.actual_hours
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    def add_notification_handler(self, handler: Callable):
        """Add notification handler"""
        self.notification_handlers.append(handler)


# Convenience functions for easy usage
async def create_media_project(project_data: Dict[str, Any], template: Optional[str] = None, 
                             redis_url: Optional[str] = None) -> str:
    """Create a new media project
    
    Args:
        project_data: Project information
        template: Optional template to use
        redis_url: Optional Redis URL
        
    Returns:
        Project ID
    """
    manager = MediaProjectManager(redis_url)
    return await manager.create_project(project_data, template)


async def get_project_status(project_id: str, redis_url: Optional[str] = None) -> Dict[str, Any]:
    """Get project status and information
    
    Args:
        project_id: Project identifier
        redis_url: Optional Redis URL
        
    Returns:
        Project status information
    """
    manager = MediaProjectManager(redis_url)
    project = await manager.get_project(project_id)
    
    if not project:
        return {}
    
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status.value,
        "progress": project.progress_percentage,
        "team_size": len(project.team_members),
        "task_count": len(project.tasks),
        "budget_status": {
            "budget": project.budget,
            "spent": project.actual_cost,
            "remaining": project.budget - project.actual_cost
        }
    }


async def update_project_progress(project_id: str, task_updates: List[Dict[str, Any]], 
                                redis_url: Optional[str] = None) -> bool:
    """Update multiple task statuses and project progress
    
    Args:
        project_id: Project identifier
        task_updates: List of task updates
        redis_url: Optional Redis URL
        
    Returns:
        Success status
    """
    manager = MediaProjectManager(redis_url)
    
    success = True
    for update in task_updates:
        result = await manager.update_task_status(
            project_id,
            update["task_id"],
            update["status"],
            update.get("actual_hours")
        )
        success = success and result
    
    return success


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create project manager
        manager = MediaProjectManager()
        
        # Create a video production project
        project_data = {
            "name": "Summer Campaign Video",
            "description": "Promotional video for summer campaign",
            "type": "video_production",
            "created_by": "creator_123",
            "team_members": ["editor_1", "sound_engineer_1"],
            "budget": 5000.0,
            "revenue_target": 15000.0
        }
        
        project_id = await manager.create_project(project_data, template="video_production")
        print(f"Created project: {project_id}")
        
        # Add a task
        task_data = {
            "name": "Script Writing",
            "description": "Write video script and storyboard",
            "assignee": "writer_1",
            "due_date": datetime.now(timezone.utc) + timedelta(days=5),
            "priority": "high",
            "estimated_hours": 16.0
        }
        
        task_id = await manager.add_task(project_id, task_data)
        print(f"Added task: {task_id}")
        
        # Generate project report
        report = await manager.generate_project_report(project_id)
        print(f"Project report: {json.dumps(report, indent=2, default=str)}")
    
    asyncio.run(main())