"""
🚀 Project Management Service - Collaboration Project Lifecycle Management
==========================================================================

**Module**: Project Management Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: Backend Senior + Microservices Architect + DevOps Engineer

Advanced project management service for collaboration project lifecycle 
management with real-time collaboration, resource allocation, and analytics.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ProjectManagementService")

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ProjectMetrics:
    """Project metrics and KPIs"""
    completion_percentage: float
    tasks_completed: int
    tasks_total: int
    days_remaining: int
    budget_used: float
    budget_total: float
    team_productivity: float
    risk_score: float

class TaskModel(BaseModel):
    """Task model for project management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class ProjectModel(BaseModel):
    """Project model for collaboration management"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    creator_id: str
    team_members: List[str] = Field(default_factory=list)
    tasks: List[TaskModel] = Field(default_factory=list)
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    budget: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProjectManagementService:
    """
    🏗️ Enterprise Project Management Service
    
    **Expertise Applied:**
    - **Backend Senior**: Enterprise project lifecycle management
    - **Microservices**: Distributed project coordination
    - **DevOps**: Automated project monitoring and analytics
    """
    
    def __init__(self):
        self.projects: Dict[str, ProjectModel] = {}
        self.templates: Dict[str, Dict] = self._initialize_templates()
        self.active_projects: List[str] = []
        self.metrics_cache: Dict[str, ProjectMetrics] = {}
        
        logger.info("🚀 Project Management Service initialized")
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize project templates for different types"""
        return {
            "content_creation": {
                "name": "Content Creation Project",
                "default_tasks": [
                    {"title": "Content Planning", "estimated_hours": 8.0},
                    {"title": "Content Creation", "estimated_hours": 24.0},
                    {"title": "Review & Editing", "estimated_hours": 8.0},
                    {"title": "Final Approval", "estimated_hours": 2.0},
                    {"title": "Publishing", "estimated_hours": 2.0}
                ]
            },
            "collaboration": {
                "name": "Creator Collaboration Project", 
                "default_tasks": [
                    {"title": "Partnership Agreement", "estimated_hours": 4.0},
                    {"title": "Content Strategy", "estimated_hours": 6.0},
                    {"title": "Production Phase", "estimated_hours": 32.0},
                    {"title": "Quality Review", "estimated_hours": 8.0},
                    {"title": "Distribution Setup", "estimated_hours": 4.0}
                ]
            },
            "marketing_campaign": {
                "name": "Marketing Campaign Project",
                "default_tasks": [
                    {"title": "Campaign Strategy", "estimated_hours": 12.0},
                    {"title": "Content Preparation", "estimated_hours": 20.0},
                    {"title": "Platform Setup", "estimated_hours": 8.0},
                    {"title": "Campaign Launch", "estimated_hours": 4.0},
                    {"title": "Performance Monitoring", "estimated_hours": 16.0}
                ]
            },
            "product_launch": {
                "name": "Product Launch Project",
                "default_tasks": [
                    {"title": "Market Research", "estimated_hours": 16.0},
                    {"title": "Product Development", "estimated_hours": 80.0},
                    {"title": "Testing & QA", "estimated_hours": 24.0},
                    {"title": "Marketing Preparation", "estimated_hours": 32.0},
                    {"title": "Launch Execution", "estimated_hours": 16.0}
                ]
            }
        }
    
    async def create_project(self, project_data: ProjectModel) -> Dict[str, Any]:
        """Create new project with validation and setup"""
        try:
            # Validate project data
            if not project_data.name or not project_data.creator_id:
                raise ValueError("Project name and creator ID required")
            
            # Store project
            self.projects[project_data.id] = project_data
            
            if project_data.status == ProjectStatus.ACTIVE:
                self.active_projects.append(project_data.id)
            
            # Initialize metrics
            await self._calculate_project_metrics(project_data.id)
            
            logger.info(f"✅ Project created: {project_data.name} (ID: {project_data.id})")
            
            return {
                "success": True,
                "project_id": project_data.id,
                "project": project_data.dict(),
                "metrics": asdict(self.metrics_cache.get(project_data.id)),
                "message": "Project created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Project creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")
    
    async def create_from_template(self, template_name: str, project_name: str, 
                                 creator_id: str, customization: Dict = None) -> Dict[str, Any]:
        """Create project from template with customization"""
        try:
            if template_name not in self.templates:
                raise ValueError(f"Template '{template_name}' not found")
            
            template = self.templates[template_name]
            
            # Create project from template
            project = ProjectModel(
                name=project_name,
                description=f"Project created from {template_name} template",
                creator_id=creator_id,
                metadata={"template": template_name}
            )
            
            # Add default tasks from template
            for task_data in template["default_tasks"]:
                task = TaskModel(
                    title=task_data["title"],
                    estimated_hours=task_data["estimated_hours"],
                    description=f"Auto-generated from {template_name} template"
                )
                project.tasks.append(task)
            
            # Apply customization
            if customization:
                if "budget" in customization:
                    project.budget = customization["budget"]
                if "end_date" in customization:
                    project.end_date = customization["end_date"]
                if "team_members" in customization:
                    project.team_members = customization["team_members"]
            
            return await self.create_project(project)
            
        except Exception as e:
            logger.error(f"❌ Template project creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")
    
    async def update_project_status(self, project_id: str, status: ProjectStatus) -> Dict[str, Any]:
        """Update project status with validation"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.projects[project_id]
            old_status = project.status
            project.status = status
            project.updated_at = datetime.utcnow()
            
            # Update active projects list
            if status == ProjectStatus.ACTIVE and project_id not in self.active_projects:
                self.active_projects.append(project_id)
            elif status != ProjectStatus.ACTIVE and project_id in self.active_projects:
                self.active_projects.remove(project_id)
            
            # Recalculate metrics
            await self._calculate_project_metrics(project_id)
            
            logger.info(f"📊 Project {project_id} status: {old_status} → {status}")
            
            return {
                "success": True,
                "project_id": project_id,
                "old_status": old_status.value,
                "new_status": status.value,
                "metrics": asdict(self.metrics_cache.get(project_id)),
                "message": "Project status updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Project status update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")
    
    async def add_task(self, project_id: str, task: TaskModel) -> Dict[str, Any]:
        """Add task to project with validation"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.projects[project_id]
            
            # Validate task dependencies
            for dep_id in task.dependencies:
                if not any(t.id == dep_id for t in project.tasks):
                    raise ValueError(f"Dependency task {dep_id} not found")
            
            project.tasks.append(task)
            project.updated_at = datetime.utcnow()
            
            # Recalculate metrics
            await self._calculate_project_metrics(project_id)
            
            logger.info(f"✅ Task added to project {project_id}: {task.title}")
            
            return {
                "success": True,
                "project_id": project_id,
                "task_id": task.id,
                "task": task.dict(),
                "metrics": asdict(self.metrics_cache.get(project_id)),
                "message": "Task added successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Task addition failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Task addition failed: {str(e)}")
    
    async def update_task_status(self, project_id: str, task_id: str, 
                               status: TaskStatus) -> Dict[str, Any]:
        """Update task status with dependency validation"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.projects[project_id]
            task = next((t for t in project.tasks if t.id == task_id), None)
            
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Validate dependencies for status change
            if status == TaskStatus.DONE:
                for dep_id in task.dependencies:
                    dep_task = next((t for t in project.tasks if t.id == dep_id), None)
                    if dep_task and dep_task.status != TaskStatus.DONE:
                        raise ValueError(f"Cannot complete task: dependency {dep_id} not completed")
            
            old_status = task.status
            task.status = status
            task.updated_at = datetime.utcnow()
            project.updated_at = datetime.utcnow()
            
            # Recalculate metrics
            await self._calculate_project_metrics(project_id)
            
            logger.info(f"📊 Task {task_id} status: {old_status} → {status}")
            
            return {
                "success": True,
                "project_id": project_id,
                "task_id": task_id,
                "old_status": old_status.value,
                "new_status": status.value,
                "metrics": asdict(self.metrics_cache.get(project_id)),
                "message": "Task status updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Task status update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Task status update failed: {str(e)}")
    
    async def get_project_analytics(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project analytics"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.projects[project_id]
            metrics = await self._calculate_project_metrics(project_id)
            
            # Calculate additional analytics
            task_distribution = {}
            for status in TaskStatus:
                task_distribution[status.value] = len([t for t in project.tasks if t.status == status])
            
            team_workload = {}
            for task in project.tasks:
                if task.assignee_id:
                    if task.assignee_id not in team_workload:
                        team_workload[task.assignee_id] = {"assigned": 0, "completed": 0, "hours": 0.0}
                    team_workload[task.assignee_id]["assigned"] += 1
                    team_workload[task.assignee_id]["hours"] += task.estimated_hours
                    if task.status == TaskStatus.DONE:
                        team_workload[task.assignee_id]["completed"] += 1
            
            return {
                "success": True,
                "project_id": project_id,
                "project_name": project.name,
                "metrics": asdict(metrics),
                "task_distribution": task_distribution,
                "team_workload": team_workload,
                "timeline": {
                    "start_date": project.start_date.isoformat(),
                    "end_date": project.end_date.isoformat() if project.end_date else None,
                    "duration_days": (datetime.utcnow() - project.start_date).days,
                    "status": project.status.value
                },
                "message": "Project analytics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Project analytics failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")
    
    async def _calculate_project_metrics(self, project_id: str) -> ProjectMetrics:
        """Calculate comprehensive project metrics"""
        try:
            project = self.projects[project_id]
            
            # Task completion metrics
            total_tasks = len(project.tasks)
            completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.DONE])
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Time metrics
            days_remaining = 0
            if project.end_date:
                days_remaining = max(0, (project.end_date - datetime.utcnow()).days)
            
            # Budget metrics (simplified)
            total_estimated_hours = sum(t.estimated_hours for t in project.tasks)
            completed_hours = sum(t.estimated_hours for t in project.tasks if t.status == TaskStatus.DONE)
            budget_used = (completed_hours / total_estimated_hours * project.budget) if total_estimated_hours > 0 else 0
            
            # Productivity metrics
            total_actual_hours = sum(t.actual_hours for t in project.tasks if t.actual_hours > 0)
            productivity = (completed_hours / total_actual_hours * 100) if total_actual_hours > 0 else 100
            
            # Risk assessment (simplified)
            overdue_tasks = len([t for t in project.tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != TaskStatus.DONE])
            blocked_tasks = len([t for t in project.tasks if t.status == TaskStatus.BLOCKED])
            risk_score = min(100, (overdue_tasks + blocked_tasks) / total_tasks * 100) if total_tasks > 0 else 0
            
            metrics = ProjectMetrics(
                completion_percentage=completion_percentage,
                tasks_completed=completed_tasks,
                tasks_total=total_tasks,
                days_remaining=days_remaining,
                budget_used=budget_used,
                budget_total=project.budget,
                team_productivity=productivity,
                risk_score=risk_score
            )
            
            self.metrics_cache[project_id] = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Metrics calculation failed: {str(e)}")
            # Return default metrics on error
            return ProjectMetrics(0, 0, 0, 0, 0, 0, 0, 0)
    
    async def get_portfolio_overview(self) -> Dict[str, Any]:
        """Get overview of all projects portfolio"""
        try:
            active_count = len(self.active_projects)
            total_count = len(self.projects)
            
            status_distribution = {}
            for status in ProjectStatus:
                status_distribution[status.value] = len([p for p in self.projects.values() if p.status == status])
            
            # Calculate portfolio metrics
            total_budget = sum(p.budget for p in self.projects.values())
            total_tasks = sum(len(p.tasks) for p in self.projects.values())
            completed_tasks = sum(len([t for t in p.tasks if t.status == TaskStatus.DONE]) for p in self.projects.values())
            
            portfolio_completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                "success": True,
                "portfolio_stats": {
                    "total_projects": total_count,
                    "active_projects": active_count,
                    "portfolio_completion": portfolio_completion,
                    "total_budget": total_budget,
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks
                },
                "status_distribution": status_distribution,
                "templates_available": list(self.templates.keys()),
                "message": "Portfolio overview retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Portfolio overview failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Portfolio overview failed: {str(e)}")

# FastAPI Application
app = FastAPI(title="Project Management Service", version="1.0.0")
service = ProjectManagementService()

@app.post("/projects/create")
async def create_project(project: ProjectModel):
    """Create new collaboration project"""
    return await service.create_project(project)

@app.post("/projects/create-from-template")
async def create_from_template(template_name: str, project_name: str, 
                             creator_id: str, customization: Dict = None):
    """Create project from template"""
    return await service.create_from_template(template_name, project_name, creator_id, customization)

@app.put("/projects/{project_id}/status")
async def update_project_status(project_id: str, status: ProjectStatus):
    """Update project status"""
    return await service.update_project_status(project_id, status)

@app.post("/projects/{project_id}/tasks")
async def add_task(project_id: str, task: TaskModel):
    """Add task to project"""
    return await service.add_task(project_id, task)

@app.put("/projects/{project_id}/tasks/{task_id}/status")
async def update_task_status(project_id: str, task_id: str, status: TaskStatus):
    """Update task status"""
    return await service.update_task_status(project_id, task_id, status)

@app.get("/projects/{project_id}/analytics")
async def get_project_analytics(project_id: str):
    """Get project analytics and insights"""
    return await service.get_project_analytics(project_id)

@app.get("/portfolio/overview")
async def get_portfolio_overview():
    """Get portfolio overview and metrics"""
    return await service.get_portfolio_overview()

@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "service": "ProjectManagementService",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Project Management Service...")
    print("📊 Enterprise project lifecycle management")
    print("👥 Advanced collaboration and team coordination")
    print("📈 Real-time analytics and performance monitoring")
    
    uvicorn.run(app, host="0.0.0.0", port=8086)