"""Project Management Engine - Enterprise Media Project Coordination System
========================================================================

Consolidated project management system providing comprehensive project coordination,
resource management, timeline tracking, and version control for media projects.

Consolidates:
- Media project management and coordination (media_project_manager.py)
- Version control system for media assets (version_control_system.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary project management system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or project management logic appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import json
import logging
import hashlib
import uuid
import shutil
import os
import mimetypes
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from pathlib import Path
from collections import defaultdict

# External dependencies with graceful fallbacks
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory storage")

try:
    import git
    HAS_GIT = True
except ImportError:
    HAS_GIT = False
    logging.warning("GitPython not available - using basic version control")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not available - image comparison limited")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logging.warning("Librosa not available - audio analysis limited")

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
    """Project types"""
    CONTENT_CREATION = "content_creation"
    CAMPAIGN = "campaign"
    COLLABORATION = "collaboration"
    PRODUCTION = "production"
    MARKETING = "marketing"
    RESEARCH = "research"
    TEMPLATE = "template"


class TaskStatus(Enum):
    """Task status types"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class VersionType(Enum):
    """Version types"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    DRAFT = "draft"
    RELEASE = "release"
    HOTFIX = "hotfix"


class ChangeType(Enum):
    """Change types for version control"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MOVE = "move"
    RENAME = "rename"
    RESTORE = "restore"


@dataclass
class ProjectConfig:
    """Project management configuration"""
    auto_versioning: bool = True
    backup_enabled: bool = True
    collaboration_enabled: bool = True
    deadline_alerts: bool = True
    resource_tracking: bool = True
    quality_gates: bool = True
    analytics_enabled: bool = True


@dataclass
class Resource:
    """Project resource representation"""
    resource_id: str
    name: str
    type: str  # file, person, tool, budget
    location: Optional[str] = None
    availability: float = 1.0  # 0-1 scale
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Project task representation"""
    task_id: str
    project_id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to: List[str] = field(default_factory=list)  # User IDs
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    resources: List[str] = field(default_factory=list)  # Resource IDs
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    due_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class Milestone:
    """Project milestone representation"""
    milestone_id: str
    project_id: str
    name: str
    description: str
    target_date: datetime
    completion_criteria: List[str]
    tasks: List[str] = field(default_factory=list)  # Task IDs
    status: str = "pending"  # pending, achieved, missed
    achieved_at: Optional[datetime] = None


@dataclass
class Project:
    """Project representation"""
    project_id: str
    name: str
    description: str
    project_type: ProjectType
    status: ProjectStatus = ProjectStatus.PLANNING
    owner_id: str = ""
    team_members: List[str] = field(default_factory=list)  # User IDs
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: float = 0.0
    spent_budget: float = 0.0
    tasks: List[Task] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    resources: List[Resource] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Version:
    """Version representation for assets"""
    version_id: str
    asset_id: str
    version_number: str
    version_type: VersionType
    file_path: str
    file_hash: str
    file_size: int
    created_by: str
    created_at: datetime
    message: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_version: Optional[str] = None
    is_current: bool = False


@dataclass
class Asset:
    """Asset representation with version control"""
    asset_id: str
    name: str
    asset_type: str  # image, video, audio, document, etc.
    project_id: str
    current_version: str
    versions: List[Version] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeLog:
    """Change log entry for version control"""
    change_id: str
    asset_id: str
    version_id: str
    change_type: ChangeType
    changed_by: str
    change_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)


class MediaProjectManager:
    """Advanced media project coordination and management"""
    
    def __init__(self, config -> None: ProjectConfig) -> None:
        self.config = config
        self.projects: Dict[str, Project] = {}
        self.project_cache = {}
        
        if HAS_REDIS:
            self.redis_client = redis.Redis(decode_responses=True)
        else:
            self.redis_client = None
        
        logger.info("📋 Media Project Manager initialized")
    
    async def create_project(
        self,
        name: str,
        description: str,
        project_type: ProjectType,
        owner_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        budget: float = 0.0,
        team_members: Optional[List[str]] = None
    ) -> Project:
        """Create new media project"""
        try:
            project_id = str(uuid.uuid4())
            
            project = Project(
                project_id=project_id,
                name=name,
                description=description,
                project_type=project_type,
                owner_id=owner_id,
                team_members=team_members or [],
                start_date=start_date,
                end_date=end_date,
                budget=budget
            )
            
            self.projects[project_id] = project
            
            # Cache project for quick access
            await self._cache_project(project)
            
            logger.info(f"Created project {project_id}: {name}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    async def add_task(
        self,
        project_id: str,
        name: str,
        description: str,
        assigned_to: Optional[List[str]] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        estimated_hours: float = 0.0,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """Add task to project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            task_id = str(uuid.uuid4())
            
            task = Task(
                task_id=task_id,
                project_id=project_id,
                name=name,
                description=description,
                assigned_to=assigned_to or [],
                priority=priority,
                due_date=due_date,
                estimated_hours=estimated_hours,
                dependencies=dependencies or []
            )
            
            project.tasks.append(task)
            project.updated_at = datetime.now(timezone.utc)
            
            # Update cache
            await self._cache_project(project)
            
            logger.info(f"Added task {task_id} to project {project_id}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            raise
    
    async def update_task_status(
        self,
        project_id: str,
        task_id: str,
        new_status: TaskStatus,
        updated_by: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update task status"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return False
            
            task = next((t for t in project.tasks if t.task_id == task_id), None)
            if not task:
                return False
            
            old_status = task.status
            task.status = new_status
            task.updated_at = datetime.now(timezone.utc)
            
            if new_status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now(timezone.utc)
            
            project.updated_at = datetime.now(timezone.utc)
            
            # Update project status if needed
            await self._update_project_status(project)
            
            # Cache updates
            await self._cache_project(project)
            
            logger.info(f"Task {task_id} status updated: {old_status.value} -> {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return False
    
    async def add_milestone(
        self,
        project_id: str,
        name: str,
        description: str,
        target_date: datetime,
        completion_criteria: List[str]
    ) -> Milestone:
        """Add milestone to project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            milestone_id = str(uuid.uuid4())
            
            milestone = Milestone(
                milestone_id=milestone_id,
                project_id=project_id,
                name=name,
                description=description,
                target_date=target_date,
                completion_criteria=completion_criteria
            )
            
            project.milestones.append(milestone)
            project.updated_at = datetime.now(timezone.utc)
            
            await self._cache_project(project)
            
            logger.info(f"Added milestone {milestone_id} to project {project_id}")
            return milestone
            
        except Exception as e:
            logger.error(f"Failed to add milestone: {e}")
            raise
    
    async def add_resource(
        self,
        project_id: str,
        name: str,
        resource_type: str,
        location: Optional[str] = None,
        cost: float = 0.0,
        availability: float = 1.0
    ) -> Resource:
        """Add resource to project"""
        try:
            project = self.projects.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            resource_id = str(uuid.uuid4())
            
            resource = Resource(
                resource_id=resource_id,
                name=name,
                type=resource_type,
                location=location,
                cost=cost,
                availability=availability
            )
            
            project.resources.append(resource)
            project.updated_at = datetime.now(timezone.utc)
            
            await self._cache_project(project)
            
            logger.info(f"Added resource {resource_id} to project {project_id}")
            return resource
            
        except Exception as e:
            logger.error(f"Failed to add resource: {e}")
            raise
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project status"""
        try:
            project = self.projects.get(project_id)
            if not project:
                return {}
            
            # Calculate task statistics
            total_tasks = len(project.tasks)
            completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
            in_progress_tasks = len([t for t in project.tasks if t.status == TaskStatus.IN_PROGRESS])
            blocked_tasks = len([t for t in project.tasks if t.status == TaskStatus.BLOCKED])
            
            # Calculate progress
            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate budget usage
            budget_used_percent = (project.spent_budget / project.budget * 100) if project.budget > 0 else 0
            
            # Check milestone status
            upcoming_milestones = [
                m for m in project.milestones 
                if m.status == "pending" and m.target_date > datetime.now(timezone.utc)
            ]
            overdue_milestones = [
                m for m in project.milestones 
                if m.status == "pending" and m.target_date <= datetime.now(timezone.utc)
            ]
            
            # Calculate estimated completion
            remaining_hours = sum(t.estimated_hours - t.actual_hours for t in project.tasks if t.status != TaskStatus.COMPLETED)
            
            return {
                'project_id': project_id,
                'name': project.name,
                'status': project.status.value,
                'progress': {
                    'completion_percentage': progress,
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'in_progress_tasks': in_progress_tasks,
                    'blocked_tasks': blocked_tasks
                },
                'budget': {
                    'total_budget': project.budget,
                    'spent_budget': project.spent_budget,
                    'budget_used_percent': budget_used_percent,
                    'remaining_budget': project.budget - project.spent_budget
                },
                'timeline': {
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'end_date': project.end_date.isoformat() if project.end_date else None,
                    'days_elapsed': (datetime.now(timezone.utc) - project.created_at).days,
                    'estimated_remaining_hours': remaining_hours
                },
                'milestones': {
                    'total_milestones': len(project.milestones),
                    'upcoming_milestones': len(upcoming_milestones),
                    'overdue_milestones': len(overdue_milestones)
                },
                'team': {
                    'owner_id': project.owner_id,
                    'team_size': len(project.team_members),
                    'total_resources': len(project.resources)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get project status: {e}")
            return {}
    
    async def get_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """Get projects for specific user"""
        try:
            user_projects = []
            
            for project in self.projects.values():
                # Check if user is owner or team member
                if project.owner_id == user_id or user_id in project.team_members:
                    # Check if user has assigned tasks
                    user_tasks = [t for t in project.tasks if user_id in t.assigned_to]
                    
                    project_info = {
                        'project_id': project.project_id,
                        'name': project.name,
                        'status': project.status.value,
                        'role': 'owner' if project.owner_id == user_id else 'member',
                        'assigned_tasks': len(user_tasks),
                        'pending_tasks': len([t for t in user_tasks if t.status != TaskStatus.COMPLETED]),
                        'updated_at': project.updated_at.isoformat()
                    }
                    user_projects.append(project_info)
            
            # Sort by most recently updated
            user_projects.sort(key=lambda p: p['updated_at'], reverse=True)
            
            return user_projects
            
        except Exception as e:
            logger.error(f"Failed to get user projects: {e}")
            return []
    
    async def _update_project_status(self, project -> None: Project) -> None:
        """Update project status based on task completion"""
        if not project.tasks:
            return
        
        completed_tasks = len([t for t in project.tasks if t.status == TaskStatus.COMPLETED])
        total_tasks = len(project.tasks)
        
        if completed_tasks == total_tasks:
            project.status = ProjectStatus.COMPLETED
        elif completed_tasks > 0:
            project.status = ProjectStatus.IN_PROGRESS
        else:
            if project.status == ProjectStatus.PLANNING:
                project.status = ProjectStatus.ACTIVE
    
    async def _cache_project(self, project -> None: Project) -> None:
        """Cache project for quick access"""
        if self.redis_client:
            try:
                # Store basic project info in cache
                cache_data = {
                    'name': project.name,
                    'status': project.status.value,
                    'owner_id': project.owner_id,
                    'updated_at': project.updated_at.isoformat()
                }
                self.redis_client.setex(
                    f"project:{project.project_id}",
                    3600,  # 1 hour cache
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"Failed to cache project: {e}")


class VersionControlSystem:
    """Advanced version control system for media assets"""
    
    def __init__(self, storage_path -> None: str) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.assets: Dict[str, Asset] = {}
        self.versions: Dict[str, Version] = {}
        self.change_logs: List[ChangeLog] = []
        
        # Initialize Git repository if available
        self.git_repo = None
        if HAS_GIT:
            try:
                self.git_repo = git.Repo.init(str(self.storage_path))
            except Exception as e:
                logger.warning(f"Failed to initialize Git repository: {e}")
        
        logger.info("📁 Version Control System initialized")
    
    async def create_asset(
        self,
        name: str,
        asset_type: str,
        project_id: str,
        file_path: str,
        created_by: str,
        initial_message: str = "Initial version"
    ) -> Asset:
        """Create new asset with initial version"""
        try:
            asset_id = str(uuid.uuid4())
            version_id = str(uuid.uuid4())
            
            # Copy file to version storage
            file_hash = await self._calculate_file_hash(file_path)
            stored_path = await self._store_file_version(file_path, asset_id, version_id)
            
            # Create initial version
            initial_version = Version(
                version_id=version_id,
                asset_id=asset_id,
                version_number="1.0.0",
                version_type=VersionType.MAJOR,
                file_path=str(stored_path),
                file_hash=file_hash,
                file_size=Path(file_path).stat().st_size,
                created_by=created_by,
                created_at=datetime.now(timezone.utc),
                message=initial_message,
                is_current=True
            )
            
            # Create asset
            asset = Asset(
                asset_id=asset_id,
                name=name,
                asset_type=asset_type,
                project_id=project_id,
                current_version=version_id,
                versions=[initial_version]
            )
            
            self.assets[asset_id] = asset
            self.versions[version_id] = initial_version
            
            # Log change
            await self._log_change(
                asset_id, version_id, ChangeType.CREATE, created_by, initial_message
            )
            
            # Git commit if available
            if self.git_repo:
                try:
                    self.git_repo.index.add([str(stored_path)])
                    self.git_repo.index.commit(f"Add {name} - {initial_message}")
                except Exception as e:
                    logger.warning(f"Git commit failed: {e}")
            
            logger.info(f"Created asset {asset_id}: {name}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to create asset: {e}")
            raise
    
    async def create_version(
        self,
        asset_id: str,
        file_path: str,
        created_by: str,
        message: str,
        version_type: VersionType = VersionType.MINOR,
        tags: Optional[List[str]] = None
    ) -> Version:
        """Create new version of existing asset"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            version_id = str(uuid.uuid4())
            
            # Calculate file hash
            file_hash = await self._calculate_file_hash(file_path)
            
            # Check if content actually changed
            current_version = self.versions.get(asset.current_version)
            if current_version and current_version.file_hash == file_hash:
                logger.info(f"No changes detected for asset {asset_id}")
                return current_version
            
            # Store new version
            stored_path = await self._store_file_version(file_path, asset_id, version_id)
            
            # Generate version number
            version_number = await self._generate_version_number(asset, version_type)
            
            # Create new version
            new_version = Version(
                version_id=version_id,
                asset_id=asset_id,
                version_number=version_number,
                version_type=version_type,
                file_path=str(stored_path),
                file_hash=file_hash,
                file_size=Path(file_path).stat().st_size,
                created_by=created_by,
                created_at=datetime.now(timezone.utc),
                message=message,
                tags=tags or [],
                parent_version=asset.current_version,
                is_current=True
            )
            
            # Update current version flag
            if current_version:
                current_version.is_current = False
            
            # Add to asset
            asset.versions.append(new_version)
            asset.current_version = version_id
            asset.updated_at = datetime.now(timezone.utc)
            
            self.versions[version_id] = new_version
            
            # Log change
            await self._log_change(
                asset_id, version_id, ChangeType.UPDATE, created_by, message
            )
            
            # Git commit if available
            if self.git_repo:
                try:
                    self.git_repo.index.add([str(stored_path)])
                    self.git_repo.index.commit(f"Update {asset.name} v{version_number} - {message}")
                except Exception as e:
                    logger.warning(f"Git commit failed: {e}")
            
            logger.info(f"Created version {version_number} for asset {asset_id}")
            return new_version
            
        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            raise
    
    async def get_version_history(self, asset_id: str) -> List[Dict[str, Any]]:
        """Get version history for asset"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return []
            
            # Sort versions by creation date (newest first)
            sorted_versions = sorted(asset.versions, key=lambda v: v.created_at, reverse=True)
            
            history = []
            for version in sorted_versions:
                version_info = {
                    'version_id': version.version_id,
                    'version_number': version.version_number,
                    'version_type': version.version_type.value,
                    'created_by': version.created_by,
                    'created_at': version.created_at.isoformat(),
                    'message': version.message,
                    'file_size': version.file_size,
                    'is_current': version.is_current,
                    'tags': version.tags
                }
                history.append(version_info)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return []
    
    async def restore_version(
        self,
        asset_id: str,
        version_id: str,
        restored_by: str,
        message: str = "Restored previous version"
    ) -> Version:
        """Restore asset to previous version"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            target_version = self.versions.get(version_id)
            if not target_version or target_version.asset_id != asset_id:
                raise ValueError(f"Version {version_id} not found for asset {asset_id}")
            
            # Create new version based on target version
            new_version_id = str(uuid.uuid4())
            
            # Copy file from target version
            source_path = Path(target_version.file_path)
            stored_path = await self._store_file_version(str(source_path), asset_id, new_version_id)
            
            # Generate new version number
            new_version_number = await self._generate_version_number(asset, VersionType.MINOR)
            
            # Create restore version
            restore_version = Version(
                version_id=new_version_id,
                asset_id=asset_id,
                version_number=new_version_number,
                version_type=VersionType.MINOR,
                file_path=str(stored_path),
                file_hash=target_version.file_hash,
                file_size=target_version.file_size,
                created_by=restored_by,
                created_at=datetime.now(timezone.utc),
                message=f"{message} (restored from v{target_version.version_number})",
                parent_version=asset.current_version,
                is_current=True
            )
            
            # Update current version
            current_version = self.versions.get(asset.current_version)
            if current_version:
                current_version.is_current = False
            
            asset.versions.append(restore_version)
            asset.current_version = new_version_id
            asset.updated_at = datetime.now(timezone.utc)
            
            self.versions[new_version_id] = restore_version
            
            # Log change
            await self._log_change(
                asset_id, new_version_id, ChangeType.RESTORE, restored_by, 
                f"Restored to version {target_version.version_number}"
            )
            
            logger.info(f"Restored asset {asset_id} to version {target_version.version_number}")
            return restore_version
            
        except Exception as e:
            logger.error(f"Failed to restore version: {e}")
            raise
    
    async def compare_versions(
        self,
        asset_id: str,
        version1_id: str,
        version2_id: str
    ) -> Dict[str, Any]:
        """Compare two versions of an asset"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            version1 = self.versions.get(version1_id)
            version2 = self.versions.get(version2_id)
            
            if not version1 or not version2:
                raise ValueError("One or both versions not found")
            
            comparison = {
                'asset_id': asset_id,
                'version1': {
                    'version_id': version1_id,
                    'version_number': version1.version_number,
                    'created_at': version1.created_at.isoformat(),
                    'created_by': version1.created_by,
                    'file_size': version1.file_size,
                    'message': version1.message
                },
                'version2': {
                    'version_id': version2_id,
                    'version_number': version2.version_number,
                    'created_at': version2.created_at.isoformat(),
                    'created_by': version2.created_by,
                    'file_size': version2.file_size,
                    'message': version2.message
                },
                'differences': {
                    'file_hash_changed': version1.file_hash != version2.file_hash,
                    'size_difference': version2.file_size - version1.file_size,
                    'time_difference': (version2.created_at - version1.created_at).total_seconds()
                }
            }
            
            # Add content-specific comparison if possible
            if asset.asset_type == 'image' and HAS_PIL:
                comparison['differences'].update(
                    await self._compare_images(version1.file_path, version2.file_path)
                )
            elif asset.asset_type == 'audio' and HAS_LIBROSA:
                comparison['differences'].update(
                    await self._compare_audio(version1.file_path, version2.file_path)
                )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare versions: {e}")
            return {}
    
    async def get_change_log(
        self,
        asset_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get change log for asset or all assets"""
        try:
            relevant_logs = self.change_logs
            
            if asset_id:
                relevant_logs = [log for log in self.change_logs if log.asset_id == asset_id]
            
            # Sort by timestamp (newest first)
            sorted_logs = sorted(relevant_logs, key=lambda l: l.timestamp, reverse=True)
            
            return [
                {
                    'change_id': log.change_id,
                    'asset_id': log.asset_id,
                    'version_id': log.version_id,
                    'change_type': log.change_type.value,
                    'changed_by': log.changed_by,
                    'message': log.change_message,
                    'timestamp': log.timestamp.isoformat(),
                    'details': log.details
                }
                for log in sorted_logs[:limit]
            ]
            
        except Exception as e:
            logger.error(f"Failed to get change log: {e}")
            return []
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""
    
    async def _store_file_version(self, source_path: str, asset_id: str, version_id: str) -> Path:
        """Store file version in version control storage"""
        try:
            # Create asset directory
            asset_dir = self.storage_path / asset_id
            asset_dir.mkdir(exist_ok=True)
            
            # Get file extension
            source_file = Path(source_path)
            extension = source_file.suffix
            
            # Create version file path
            version_file = asset_dir / f"{version_id}{extension}"
            
            # Copy file
            shutil.copy2(source_path, version_file)
            
            return version_file
            
        except Exception as e:
            logger.error(f"Failed to store file version: {e}")
            raise
    
    async def _generate_version_number(self, asset: Asset, version_type: VersionType) -> str:
        """Generate next version number"""
        try:
            if not asset.versions:
                return "1.0.0"
            
            # Get current version number
            current_version = max(asset.versions, key=lambda v: v.created_at)
            current_number = current_version.version_number
            
            # Parse version number (assuming semantic versioning)
            try:
                parts = current_number.split('.')
                major = int(parts[0]) if len(parts) > 0 else 1
                minor = int(parts[1]) if len(parts) > 1 else 0
                patch = int(parts[2]) if len(parts) > 2 else 0
            except (ValueError, IndexError):
                # Fallback for non-standard version numbers
                return f"{len(asset.versions) + 1}.0.0"
            
            # Increment based on version type
            if version_type == VersionType.MAJOR:
                major += 1
                minor = 0
                patch = 0
            elif version_type == VersionType.MINOR:
                minor += 1
                patch = 0
            elif version_type == VersionType.PATCH:
                patch += 1
            
            return f"{major}.{minor}.{patch}"
            
        except Exception as e:
            logger.error(f"Failed to generate version number: {e}")
            return f"{len(asset.versions) + 1}.0.0"
    
    async def _log_change(
        self,
        asset_id -> None: str,
        version_id -> None: str,
        change_type -> None: ChangeType,
        changed_by -> None: str,
        message -> None: str,
        details -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log change to change log"""
        try:
            change_log = ChangeLog(
                change_id=str(uuid.uuid4()),
                asset_id=asset_id,
                version_id=version_id,
                change_type=change_type,
                changed_by=changed_by,
                change_message=message,
                details=details or {}
            )
            
            self.change_logs.append(change_log)
            
            # Keep change log size manageable
            if len(self.change_logs) > 10000:
                self.change_logs = self.change_logs[-5000:]  # Keep last 5000 entries
            
        except Exception as e:
            logger.error(f"Failed to log change: {e}")
    
    async def _compare_images(self, image1_path: str, image2_path: str) -> Dict[str, Any]:
        """Compare two images"""
        try:
            with Image.open(image1_path) as img1, Image.open(image2_path) as img2:
                comparison = {
                    'dimensions_changed': img1.size != img2.size,
                    'mode_changed': img1.mode != img2.mode,
                    'size_1': img1.size,
                    'size_2': img2.size,
                    'mode_1': img1.mode,
                    'mode_2': img2.mode
                }
                
                # Basic similarity check (if same dimensions)
                if img1.size == img2.size and img1.mode == img2.mode:
                    # This is a simplified similarity check
                    # In production, would use more sophisticated image comparison
                    comparison['identical_dimensions'] = True
                
                return comparison
        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            return {'comparison_failed': True, 'error': str(e)}
    
    async def _compare_audio(self, audio1_path: str, audio2_path: str) -> Dict[str, Any]:
        """Compare two audio files"""
        try:
            y1, sr1 = librosa.load(audio1_path)
            y2, sr2 = librosa.load(audio2_path)
            
            duration1 = librosa.get_duration(y=y1, sr=sr1)
            duration2 = librosa.get_duration(y=y2, sr=sr2)
            
            comparison = {
                'duration_changed': abs(duration1 - duration2) > 0.1,
                'sample_rate_changed': sr1 != sr2,
                'duration_1': duration1,
                'duration_2': duration2,
                'sample_rate_1': sr1,
                'sample_rate_2': sr2,
                'duration_difference': duration2 - duration1
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Audio comparison failed: {e}")
            return {'comparison_failed': True, 'error': str(e)}


class ProjectManagementEngine:
    """Main project management engine orchestrating all project management components"""
    
    def __init__(
        self, 
        config -> None: Optional[ProjectConfig] = None,
        storage_path -> None: str = "./project_storage"
    ) -> None:
        """Initialize project management engine"""
        self.config = config or ProjectConfig()
        
        # Initialize component managers
        self.project_manager = MediaProjectManager(self.config)
        self.version_control = VersionControlSystem(storage_path)
        
        # Integration state
        self.project_assets: Dict[str, List[str]] = defaultdict(list)  # project_id -> asset_ids
        
        logger.info("🏗️ Project Management Engine initialized")
    
    async def create_project_with_assets(
        self,
        project_name: str,
        project_description: str,
        project_type: ProjectType,
        owner_id: str,
        initial_assets: Optional[List[Dict[str, Any]]] = None,
        **project_kwargs
    ) -> Dict[str, Any]:
        """Create project with initial assets"""
        try:
            # Create project
            project = await self.project_manager.create_project(
                name=project_name,
                description=project_description,
                project_type=project_type,
                owner_id=owner_id,
                **project_kwargs
            )
            
            # Add initial assets if provided
            assets_created = []
            if initial_assets:
                for asset_info in initial_assets:
                    try:
                        asset = await self.version_control.create_asset(
                            name=asset_info['name'],
                            asset_type=asset_info['type'],
                            project_id=project.project_id,
                            file_path=asset_info['file_path'],
                            created_by=owner_id,
                            initial_message=asset_info.get('message', 'Initial version')
                        )
                        
                        assets_created.append(asset)
                        self.project_assets[project.project_id].append(asset.asset_id)
                        
                    except Exception as e:
                        logger.error(f"Failed to create asset {asset_info.get('name')}: {e}")
            
            return {
                'project': {
                    'project_id': project.project_id,
                    'name': project.name,
                    'status': project.status.value,
                    'created_at': project.created_at.isoformat()
                },
                'assets_created': [
                    {
                        'asset_id': asset.asset_id,
                        'name': asset.name,
                        'type': asset.asset_type,
                        'current_version': asset.current_version
                    }
                    for asset in assets_created
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to create project with assets: {e}")
            raise
    
    async def add_asset_to_project(
        self,
        project_id: str,
        asset_name: str,
        asset_type: str,
        file_path: str,
        created_by: str,
        message: str = "Added to project"
    ) -> Asset:
        """Add new asset to existing project"""
        try:
            # Verify project exists
            project_status = await self.project_manager.get_project_status(project_id)
            if not project_status:
                raise ValueError(f"Project {project_id} not found")
            
            # Create asset
            asset = await self.version_control.create_asset(
                name=asset_name,
                asset_type=asset_type,
                project_id=project_id,
                file_path=file_path,
                created_by=created_by,
                initial_message=message
            )
            
            # Link asset to project
            self.project_assets[project_id].append(asset.asset_id)
            
            # Create task for asset integration if auto-tasking enabled
            if self.config.auto_versioning:
                await self.project_manager.add_task(
                    project_id=project_id,
                    name=f"Integrate {asset_name}",
                    description=f"Review and integrate {asset_name} into project",
                    assigned_to=[created_by],
                    priority=TaskPriority.MEDIUM
                )
            
            logger.info(f"Added asset {asset.asset_id} to project {project_id}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to add asset to project: {e}")
            raise
    
    async def update_project_asset(
        self,
        project_id: str,
        asset_id: str,
        file_path: str,
        updated_by: str,
        message: str,
        version_type: VersionType = VersionType.MINOR
    ) -> Version:
        """Update asset in project with new version"""
        try:
            # Verify asset belongs to project
            if asset_id not in self.project_assets.get(project_id, []):
                raise ValueError(f"Asset {asset_id} not found in project {project_id}")
            
            # Create new version
            version = await self.version_control.create_version(
                asset_id=asset_id,
                file_path=file_path,
                created_by=updated_by,
                message=message,
                version_type=version_type
            )
            
            # Create task for version review if quality gates enabled
            if self.config.quality_gates:
                await self.project_manager.add_task(
                    project_id=project_id,
                    name=f"Review asset update - v{version.version_number}",
                    description=f"Review changes in {message}",
                    assigned_to=[updated_by],
                    priority=TaskPriority.HIGH
                )
            
            logger.info(f"Updated asset {asset_id} in project {project_id} to version {version.version_number}")
            return version
            
        except Exception as e:
            logger.error(f"Failed to update project asset: {e}")
            raise
    
    async def get_project_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project dashboard"""
        try:
            # Get project status
            project_status = await self.project_manager.get_project_status(project_id)
            if not project_status:
                return {'error': f'Project {project_id} not found'}
            
            # Get project assets
            asset_ids = self.project_assets.get(project_id, [])
            assets_info = []
            
            for asset_id in asset_ids:
                asset = self.version_control.assets.get(asset_id)
                if asset:
                    current_version = self.version_control.versions.get(asset.current_version)
                    asset_info = {
                        'asset_id': asset_id,
                        'name': asset.name,
                        'type': asset.asset_type,
                        'current_version': current_version.version_number if current_version else 'unknown',
                        'total_versions': len(asset.versions),
                        'last_updated': asset.updated_at.isoformat()
                    }
                    assets_info.append(asset_info)
            
            # Get recent changes
            recent_changes = await self.version_control.get_change_log(limit=10)
            project_changes = [
                change for change in recent_changes
                if change['asset_id'] in asset_ids
            ]
            
            return {
                'project_status': project_status,
                'assets': {
                    'total_assets': len(assets_info),
                    'assets_list': assets_info
                },
                'recent_activity': {
                    'recent_changes': project_changes[:5],
                    'total_changes': len(project_changes)
                },
                'dashboard_generated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get project dashboard: {e}")
            return {'error': str(e)}
    
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user's project management dashboard"""
        try:
            # Get user's projects
            user_projects = await self.project_manager.get_user_projects(user_id)
            
            # Get user's recent asset changes
            all_changes = await self.version_control.get_change_log(limit=50)
            user_changes = [
                change for change in all_changes
                if change['changed_by'] == user_id
            ]
            
            # Calculate user statistics
            total_projects = len(user_projects)
            active_projects = len([p for p in user_projects if p['status'] in ['active', 'in_progress']])
            total_pending_tasks = sum(p['pending_tasks'] for p in user_projects)
            
            return {
                'user_id': user_id,
                'projects': {
                    'total_projects': total_projects,
                    'active_projects': active_projects,
                    'projects_list': user_projects[:10]  # Most recent 10
                },
                'tasks': {
                    'total_pending_tasks': total_pending_tasks,
                    'high_priority_projects': [
                        p for p in user_projects 
                        if p['pending_tasks'] > 5
                    ]
                },
                'recent_activity': {
                    'recent_changes': user_changes[:10],
                    'total_changes': len(user_changes)
                },
                'dashboard_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user dashboard: {e}")
            return {'error': str(e)}


# Backward compatibility classes for existing imports
class MediaProjectManager_Legacy:
    """Legacy wrapper for media project manager"""
    def __init__(self, *args, **kwargs) -> None:
        config = ProjectConfig()
        self.manager = MediaProjectManager(config)


class VersionControlSystem_Legacy:
    """Legacy wrapper for version control system"""
    def __init__(self, *args, **kwargs) -> None:
        storage_path = kwargs.get('storage_path', './version_storage')
        self.system = VersionControlSystem(storage_path)


# Export all classes for consolidated import
__all__ = [
    'ProjectManagementEngine',
    'MediaProjectManager',
    'VersionControlSystem',
    'ProjectConfig',
    'Project',
    'Task',
    'Milestone',
    'Resource',
    'Asset',
    'Version',
    'ChangeLog',
    'ProjectStatus',
    'ProjectType',
    'TaskStatus',
    'TaskPriority',
    'VersionType',
    'ChangeType',
    # Legacy compatibility
    'MediaProjectManager_Legacy',
    'VersionControlSystem_Legacy'
]