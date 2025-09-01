"""Project Management Engine - Advanced Processing Core

Core engine for project management operations including task management,
resource allocation, timeline tracking, and workflow optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ProjectManagementJob:
    """Project management operation job"""
    job_id: str
    operation_type: str
    project_id: Optional[str] = None
    task_data: Optional[Dict[str, Any]] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None
    assigned_to: Optional[str] = None
    created_at: datetime = None

@dataclass
class ProjectManagementResult:
    """Project management operation result"""
    job_id: str
    success: bool
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    completed_at: datetime = None

class ProjectManagementEngine:
    """Core project management processing engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_running = False
        self.active_projects = {}
        self.task_queue = asyncio.Queue()
        
        logger.info("ProjectManagementEngine initialized")

    async def start(self) -> None:
        """Start the project management engine"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Project Management Engine started")

    async def shutdown(self) -> None:
        """Shutdown the project management engine"""
        self.is_running = False
        logger.info("Project Management Engine shut down")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process project management operation"""
        operation = data.get("operation", "status")
        
        if operation == "create_project":
            return await self._create_project(data)
        elif operation == "add_task":
            return await self._add_task(data)
        elif operation == "update_status":
            return await self._update_status(data)
        elif operation == "get_timeline":
            return await self._get_timeline(data)
        else:
            return await self._get_status(data)

    async def _create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        project_id = data.get("project_id", f"proj_{datetime.now().timestamp()}")
        project_name = data.get("name", "Untitled Project")
        
        project = {
            "id": project_id,
            "name": project_name,
            "status": ProjectStatus.PLANNING.value,
            "created_at": datetime.now().isoformat(),
            "tasks": [],
            "milestones": [],
            "team_members": data.get("team_members", [])
        }
        
        self.active_projects[project_id] = project
        
        return {
            "project_id": project_id,
            "status": "created",
            "project": project
        }

    async def _add_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add task to project"""
        project_id = data.get("project_id")
        task_data = data.get("task", {})
        
        if project_id not in self.active_projects:
            return {"error": "Project not found"}
        
        task = {
            "id": f"task_{len(self.active_projects[project_id]['tasks']) + 1}",
            "title": task_data.get("title", "New Task"),
            "description": task_data.get("description", ""),
            "priority": task_data.get("priority", TaskPriority.MEDIUM.value),
            "status": "pending",
            "assigned_to": task_data.get("assigned_to"),
            "created_at": datetime.now().isoformat(),
            "due_date": task_data.get("due_date")
        }
        
        self.active_projects[project_id]["tasks"].append(task)
        
        return {
            "task_id": task["id"],
            "status": "added",
            "task": task
        }

    async def _update_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update project or task status"""
        project_id = data.get("project_id")
        new_status = data.get("status")
        task_id = data.get("task_id")
        
        if project_id not in self.active_projects:
            return {"error": "Project not found"}
        
        if task_id:
            # Update task status
            for task in self.active_projects[project_id]["tasks"]:
                if task["id"] == task_id:
                    task["status"] = new_status
                    task["updated_at"] = datetime.now().isoformat()
                    return {"status": "updated", "task": task}
            return {"error": "Task not found"}
        else:
            # Update project status
            self.active_projects[project_id]["status"] = new_status
            self.active_projects[project_id]["updated_at"] = datetime.now().isoformat()
            return {"status": "updated", "project": self.active_projects[project_id]}

    async def _get_timeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get project timeline and milestones"""
        project_id = data.get("project_id")
        
        if project_id not in self.active_projects:
            return {"error": "Project not found"}
        
        project = self.active_projects[project_id]
        
        # Generate timeline from tasks
        timeline = []
        for task in project["tasks"]:
            timeline.append({
                "type": "task",
                "id": task["id"],
                "title": task["title"],
                "start_date": task.get("created_at"),
                "due_date": task.get("due_date"),
                "status": task["status"],
                "priority": task["priority"]
            })
        
        return {
            "project_id": project_id,
            "timeline": sorted(timeline, key=lambda x: x.get("start_date", "")),
            "total_tasks": len(project["tasks"]),
            "completed_tasks": len([t for t in project["tasks"] if t["status"] == "completed"])
        }

    async def _get_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get overall status"""
        return {
            "engine_status": "running" if self.is_running else "stopped",
            "active_projects": len(self.active_projects),
            "total_tasks": sum(len(p["tasks"]) for p in self.active_projects.values())
        }