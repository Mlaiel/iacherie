"""
Working Collaboration Engine for Ainflue Platform
Simplified implementation to ensure functionality
"""

import asyncio
import time
import hashlib
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ProjectStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"

class CollaborationType(Enum):
    MUSIC_PRODUCTION = "music_production"
    CONTENT_CREATION = "content_creation"
    AUDIO_ENGINEERING = "audio_engineering"
    VOICE_ACTING = "voice_acting"
    PODCAST = "podcast"

class User:
    """User model for collaboration"""
    
    def __init__(self, user_id: str, name: str, skills: List[str], 
                 experience_level: str = "intermediate"):
        self.user_id = user_id
        self.name = name
        self.skills = skills
        self.experience_level = experience_level
        self.availability = "available"
        self.rating = 4.5  # Default rating

class Project:
    """Project model for collaboration"""
    
    def __init__(self, project_id: str, title: str, description: str, 
                 creator_id: str, collaboration_type: CollaborationType):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.collaboration_type = collaboration_type
        self.status = ProjectStatus.DRAFT
        self.collaborators: Set[str] = {creator_id}
        self.tasks: List[Dict] = []
        self.created_at = datetime.utcnow()
        self.deadline = None
        self.budget = 0.0
        self.metadata = {}

class CollaborationMatcher:
    """AI-powered collaboration matching system"""
    
    def __init__(self):
        self.logger = logger
        self.users = {}  # In-memory user storage
        
    async def add_user(self, user: User) -> Dict[str, Any]:
        """Add user to the system"""
        try:
            self.users[user.user_id] = user
            return {
                "status": "success",
                "user_id": user.user_id,
                "message": "User added successfully"
            }
        except Exception as e:
            self.logger.error(f"Adding user failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def find_collaborators(self, project: Project, required_skills: List[str],
                               max_results: int = 10) -> Dict[str, Any]:
        """Find potential collaborators for a project"""
        try:
            matches = []
            
            for user_id, user in self.users.items():
                if user_id == project.creator_id:
                    continue  # Skip project creator
                
                # Calculate compatibility score
                skill_match = len(set(user.skills) & set(required_skills))
                skill_score = skill_match / len(required_skills) if required_skills else 0
                
                # Experience level bonus
                experience_bonus = {
                    "beginner": 0.1,
                    "intermediate": 0.2,
                    "advanced": 0.3,
                    "expert": 0.4
                }.get(user.experience_level, 0.2)
                
                # Availability bonus
                availability_bonus = 0.2 if user.availability == "available" else 0
                
                # Calculate total score
                compatibility_score = (skill_score * 0.6) + experience_bonus + availability_bonus
                
                if compatibility_score > 0.3:  # Minimum threshold
                    matches.append({
                        "user_id": user.user_id,
                        "name": user.name,
                        "skills": user.skills,
                        "experience_level": user.experience_level,
                        "rating": user.rating,
                        "compatibility_score": round(compatibility_score, 2),
                        "matching_skills": list(set(user.skills) & set(required_skills))
                    })
            
            # Sort by compatibility score
            matches = sorted(matches, key=lambda x: x["compatibility_score"], reverse=True)
            matches = matches[:max_results]
            
            return {
                "status": "success",
                "matches": matches,
                "count": len(matches),
                "message": f"Found {len(matches)} potential collaborators"
            }
            
        except Exception as e:
            self.logger.error(f"Finding collaborators failed: {e}")
            return {"status": "error", "message": str(e)}

class ProjectManager:
    """Project management system"""
    
    def __init__(self):
        self.logger = logger
        self.projects = {}  # In-memory project storage
        
    async def create_project(self, title: str, description: str, creator_id: str,
                           collaboration_type: str, deadline: str = None,
                           budget: float = 0.0) -> Dict[str, Any]:
        """Create a new collaboration project"""
        try:
            project_id = f"proj_{int(time.time())}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
            
            project = Project(
                project_id=project_id,
                title=title,
                description=description,
                creator_id=creator_id,
                collaboration_type=CollaborationType(collaboration_type)
            )
            
            if deadline:
                project.deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            
            project.budget = budget
            project.status = ProjectStatus.ACTIVE
            
            # Store project
            self.projects[project_id] = project
            
            return {
                "status": "success",
                "project": {
                    "project_id": project.project_id,
                    "title": project.title,
                    "description": project.description,
                    "creator_id": project.creator_id,
                    "collaboration_type": project.collaboration_type.value,
                    "status": project.status.value,
                    "created_at": project.created_at.isoformat(),
                    "deadline": project.deadline.isoformat() if project.deadline else None,
                    "budget": project.budget
                },
                "message": "Project created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Project creation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def add_collaborator(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Add collaborator to project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            project.collaborators.add(user_id)
            
            return {
                "status": "success",
                "project_id": project_id,
                "collaborator_id": user_id,
                "total_collaborators": len(project.collaborators),
                "message": "Collaborator added successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Adding collaborator failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def create_task(self, project_id: str, title: str, description: str,
                         assigned_to: str = None, priority: str = "medium") -> Dict[str, Any]:
        """Create a task in a project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            task_id = f"task_{int(time.time())}_{len(project.tasks)}"
            
            task = {
                "task_id": task_id,
                "title": title,
                "description": description,
                "assigned_to": assigned_to,
                "priority": priority,
                "status": TaskStatus.TODO.value,
                "created_at": datetime.utcnow().isoformat(),
                "due_date": None,
                "completed_at": None
            }
            
            project.tasks.append(task)
            
            return {
                "status": "success",
                "task": task,
                "message": "Task created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Task creation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def update_task_status(self, project_id: str, task_id: str, 
                               new_status: str) -> Dict[str, Any]:
        """Update task status"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            task = next((t for t in project.tasks if t["task_id"] == task_id), None)
            if not task:
                return {"status": "error", "message": "Task not found"}
            
            task["status"] = new_status
            if new_status == TaskStatus.COMPLETED.value:
                task["completed_at"] = datetime.utcnow().isoformat()
            
            return {
                "status": "success",
                "task": task,
                "message": f"Task status updated to {new_status}"
            }
            
        except Exception as e:
            self.logger.error(f"Task status update failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {"status": "error", "message": "Project not found"}
            
            return {
                "status": "success",
                "project": {
                    "project_id": project.project_id,
                    "title": project.title,
                    "description": project.description,
                    "creator_id": project.creator_id,
                    "collaboration_type": project.collaboration_type.value,
                    "status": project.status.value,
                    "collaborators": list(project.collaborators),
                    "tasks": project.tasks,
                    "created_at": project.created_at.isoformat(),
                    "deadline": project.deadline.isoformat() if project.deadline else None,
                    "budget": project.budget,
                    "task_count": len(project.tasks),
                    "completed_tasks": len([t for t in project.tasks if t["status"] == TaskStatus.COMPLETED.value])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Getting project failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def list_user_projects(self, user_id: str) -> Dict[str, Any]:
        """List projects for a user"""
        try:
            user_projects = []
            
            for project in self.projects.values():
                if user_id in project.collaborators:
                    user_projects.append({
                        "project_id": project.project_id,
                        "title": project.title,
                        "collaboration_type": project.collaboration_type.value,
                        "status": project.status.value,
                        "role": "creator" if project.creator_id == user_id else "collaborator",
                        "created_at": project.created_at.isoformat(),
                        "task_count": len(project.tasks),
                        "collaborator_count": len(project.collaborators)
                    })
            
            # Sort by creation date (newest first)
            user_projects = sorted(user_projects, key=lambda x: x["created_at"], reverse=True)
            
            return {
                "status": "success",
                "projects": user_projects,
                "count": len(user_projects)
            }
            
        except Exception as e:
            self.logger.error(f"Listing user projects failed: {e}")
            return {"status": "error", "message": str(e)}

class CollaborationEngine:
    """Main collaboration engine orchestrator"""
    
    def __init__(self):
        self.logger = logger
        self.matcher = CollaborationMatcher()
        self.project_manager = ProjectManager()
        
    async def initialize_demo_data(self):
        """Initialize with demo users for testing"""
        demo_users = [
            User("user1", "Alice Producer", ["music_production", "mixing", "mastering"], "advanced"),
            User("user2", "Bob Vocalist", ["vocals", "songwriting", "performance"], "intermediate"),
            User("user3", "Carol Engineer", ["audio_engineering", "sound_design", "editing"], "expert"),
            User("user4", "David Composer", ["composition", "orchestration", "music_theory"], "advanced"),
            User("user5", "Eve Voice Actor", ["voice_acting", "narration", "character_voices"], "intermediate")
        ]
        
        for user in demo_users:
            await self.matcher.add_user(user)
        
        return {
            "status": "success",
            "message": f"Initialized with {len(demo_users)} demo users"
        }

# Service instances
collaboration_engine = CollaborationEngine()

# API functions
async def create_project(title: str, description: str, creator_id: str,
                        collaboration_type: str, deadline: str = None,
                        budget: float = 0.0) -> Dict[str, Any]:
    """Create a collaboration project"""
    return await collaboration_engine.project_manager.create_project(
        title, description, creator_id, collaboration_type, deadline, budget
    )

async def find_collaborators(project_id: str, required_skills: List[str],
                           max_results: int = 10) -> Dict[str, Any]:
    """Find collaborators for a project"""
    project = collaboration_engine.project_manager.projects.get(project_id)
    if not project:
        return {"status": "error", "message": "Project not found"}
    
    return await collaboration_engine.matcher.find_collaborators(
        project, required_skills, max_results
    )

async def add_collaborator(project_id: str, user_id: str) -> Dict[str, Any]:
    """Add collaborator to project"""
    return await collaboration_engine.project_manager.add_collaborator(project_id, user_id)

async def create_task(project_id: str, title: str, description: str,
                     assigned_to: str = None, priority: str = "medium") -> Dict[str, Any]:
    """Create a task in a project"""
    return await collaboration_engine.project_manager.create_task(
        project_id, title, description, assigned_to, priority
    )

async def update_task_status(project_id: str, task_id: str, new_status: str) -> Dict[str, Any]:
    """Update task status"""
    return await collaboration_engine.project_manager.update_task_status(
        project_id, task_id, new_status
    )

async def get_project_details(project_id: str) -> Dict[str, Any]:
    """Get project details"""
    return await collaboration_engine.project_manager.get_project(project_id)

async def list_user_projects(user_id: str) -> Dict[str, Any]:
    """List projects for a user"""
    return await collaboration_engine.project_manager.list_user_projects(user_id)

async def add_user(user_id: str, name: str, skills: List[str], 
                  experience_level: str = "intermediate") -> Dict[str, Any]:
    """Add user to collaboration system"""
    user = User(user_id, name, skills, experience_level)
    return await collaboration_engine.matcher.add_user(user)

# Export main functions
__all__ = ['create_project', 'find_collaborators', 'add_collaborator', 'create_task',
           'update_task_status', 'get_project_details', 'list_user_projects', 'add_user',
           'CollaborationEngine', 'ProjectStatus', 'TaskStatus', 'CollaborationType']