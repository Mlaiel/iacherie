"""Team Media Workspace - Collaborative Media Management Hub

Comprehensive team workspace for managing shared media assets, coordinating projects,
facilitating collaboration, and organizing creative workflows across teams.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Set
import uuid
from collections import defaultdict
from pathlib import Path

# External dependencies with graceful fallbacks
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    logging.warning("SQLAlchemy async not available - using in-memory storage")

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory state")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkspaceRole(Enum):
    """Workspace member roles"""
    MEMBER = "member"
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


class AssetStatus(Enum):
    """Asset status in workspace"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class ProjectStatus(Enum):
    """Project status types"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityType(Enum):
    """Activity types for feed"""
    ASSET_UPLOADED = "asset_uploaded"
    ASSET_UPDATED = "asset_updated"
    ASSET_COMMENTED = "asset_commented"
    ASSET_APPROVED = "asset_approved"
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    MEMBER_JOINED = "member_joined"
    MEMBER_LEFT = "member_left"
    COLLABORATION_STARTED = "collaboration_started"
    MILESTONE_REACHED = "milestone_reached"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class WorkspaceMember:
    """Workspace team member"""
    user_id: str
    username: str
    email: str
    role: WorkspaceRole
    joined_at: datetime
    
    # Profile information
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    
    # Activity tracking
    last_activity: Optional[datetime] = None
    total_contributions: int = 0
    
    # Preferences
    notification_settings: Dict[str, bool] = field(default_factory=dict)
    workspace_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    active: bool = True
    invited_by: Optional[str] = None


@dataclass
class MediaAssetInfo:
    """Simplified media asset information for workspace"""
    id: str
    name: str
    type: str
    file_path: str
    created_by: str
    created_at: datetime
    
    # Status and metadata
    status: AssetStatus = AssetStatus.DRAFT
    file_size: int = 0
    mime_type: str = ""
    thumbnail_url: Optional[str] = None
    
    # Collaboration
    tags: List[str] = field(default_factory=list)
    description: str = ""
    comments_count: int = 0
    likes_count: int = 0
    
    # Organization
    folder_id: Optional[str] = None
    project_ids: List[str] = field(default_factory=list)
    
    # Versioning
    version: str = "1.0"
    is_latest: bool = True
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkspaceProject:
    """Workspace project"""
    id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    
    # Project details
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    
    # Team
    members: List[str] = field(default_factory=list)
    lead: Optional[str] = None
    
    # Organization
    folder_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Progress
    progress_percentage: float = 0.0
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Assets
    asset_ids: List[str] = field(default_factory=list)
    
    # Metadata
    budget: Optional[float] = None
    client: Optional[str] = None
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkspaceFolder:
    """Workspace folder for organization"""
    id: str
    name: str
    created_by: str
    created_at: datetime
    
    # Hierarchy
    parent_id: Optional[str] = None
    path: str = "/"
    
    # Contents
    asset_ids: Set[str] = field(default_factory=set)
    subfolder_ids: Set[str] = field(default_factory=set)
    
    # Permissions
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Metadata
    description: str = ""
    color: Optional[str] = None
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkspaceActivity:
    """Activity feed item"""
    id: str
    type: ActivityType
    actor_id: str
    actor_name: str
    timestamp: datetime
    
    # Activity data
    target_id: str
    target_name: str
    target_type: str
    
    # Context
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Visibility
    visible_to: List[str] = field(default_factory=list)  # Empty = visible to all


@dataclass
class WorkspaceNotification:
    """Workspace notification"""
    id: str
    recipient_id: str
    title: str
    message: str
    created_at: datetime
    
    # Classification
    type: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    
    # Context
    related_id: Optional[str] = None
    related_type: Optional[str] = None
    action_url: Optional[str] = None
    
    # Status
    read: bool = False
    read_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamMediaWorkspace:
    """Main workspace entity"""
    id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    
    # Members and permissions
    members: Dict[str, WorkspaceMember] = field(default_factory=dict)
    pending_invitations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Organization
    folders: Dict[str, WorkspaceFolder] = field(default_factory=dict)
    projects: Dict[str, WorkspaceProject] = field(default_factory=dict)
    assets: Dict[str, MediaAssetInfo] = field(default_factory=dict)
    
    # Activity and notifications
    activities: List[WorkspaceActivity] = field(default_factory=list)
    notifications: Dict[str, List[WorkspaceNotification]] = field(default_factory=dict)
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    active: bool = True
    storage_quota: int = 10 * 1024 * 1024 * 1024  # 10GB default
    storage_used: int = 0
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TeamMediaWorkspaceManager:
    """Team media workspace management system"""
    
    def __init__(self, storage_root: str = "./workspace_storage", redis_url: Optional[str] = None):
        """Initialize workspace manager
        
        Args:
            storage_root: Root directory for workspace storage
            redis_url: Optional Redis connection URL
        """
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        self.workspaces: Dict[str, TeamMediaWorkspace] = {}
        self.user_workspaces: Dict[str, Set[str]] = defaultdict(set)
        
        # Redis for distributed state
        self.redis_client = None
        if HAS_REDIS and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info("Connected to Redis for workspace state")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
        
        logger.info(f"TeamMediaWorkspaceManager initialized at {self.storage_root}")
    
    async def create_workspace(self, workspace_data: Dict[str, Any]) -> str:
        """Create a new team workspace
        
        Args:
            workspace_data: Workspace configuration
            
        Returns:
            Workspace ID
        """
        try:
            workspace_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Create workspace
            workspace = TeamMediaWorkspace(
                id=workspace_id,
                name=workspace_data["name"],
                description=workspace_data.get("description", ""),
                created_by=workspace_data["created_by"],
                created_at=now
            )
            
            # Add creator as owner
            creator_member = WorkspaceMember(
                user_id=workspace_data["created_by"],
                username=workspace_data.get("creator_username", workspace_data["created_by"]),
                email=workspace_data.get("creator_email", ""),
                role=WorkspaceRole.OWNER,
                joined_at=now,
                display_name=workspace_data.get("creator_name"),
                avatar_url=workspace_data.get("creator_avatar")
            )
            workspace.members[workspace_data["created_by"]] = creator_member
            
            # Set default settings
            workspace.settings = {
                "auto_notifications": workspace_data.get("auto_notifications", True),
                "public_sharing": workspace_data.get("public_sharing", False),
                "require_approval": workspace_data.get("require_approval", True),
                "max_file_size": workspace_data.get("max_file_size", 100 * 1024 * 1024),  # 100MB
                "allowed_file_types": workspace_data.get("allowed_file_types", [
                    "video/*", "audio/*", "image/*", "text/*"
                ]),
                "collaboration_features": workspace_data.get("collaboration_features", {
                    "real_time_editing": True,
                    "comments": True,
                    "annotations": True,
                    "version_control": True
                })
            }
            
            # Create root folder
            root_folder = WorkspaceFolder(
                id="root",
                name="Root",
                created_by=workspace_data["created_by"],
                created_at=now,
                path="/"
            )
            workspace.folders["root"] = root_folder
            
            # Store workspace
            self.workspaces[workspace_id] = workspace
            self.user_workspaces[workspace_data["created_by"]].add(workspace_id)
            
            # Create workspace directory
            workspace_dir = self.storage_root / workspace_id
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # Log activity
            await self._log_activity(workspace, ActivityType.MEMBER_JOINED, {
                "actor_id": workspace_data["created_by"],
                "actor_name": creator_member.display_name or creator_member.username,
                "target_id": workspace_id,
                "target_name": workspace.name,
                "target_type": "workspace",
                "description": f"Created workspace '{workspace.name}'"
            })
            
            logger.info(f"Created workspace {workspace_id}: {workspace.name}")
            return workspace_id
            
        except Exception as e:
            logger.error(f"Error creating workspace: {e}")
            raise
    
    async def invite_member(self, workspace_id: str, inviter_id: str, 
                          invitation_data: Dict[str, Any]) -> str:
        """Invite a member to workspace
        
        Args:
            workspace_id: Workspace identifier
            inviter_id: User sending invitation
            invitation_data: Invitation details
            
        Returns:
            Invitation ID
        """
        try:
            workspace = await self._get_workspace(workspace_id)
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            # Check permissions
            if not self._check_admin_permission(workspace, inviter_id):
                raise PermissionError(f"User {inviter_id} lacks admin permission")
            
            invitation_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            invitation = {
                "id": invitation_id,
                "workspace_id": workspace_id,
                "invited_user": invitation_data["user_id"],
                "invited_email": invitation_data.get("email", ""),
                "invited_by": inviter_id,
                "role": invitation_data.get("role", "member"),
                "message": invitation_data.get("message", ""),
                "created_at": now.isoformat(),
                "expires_at": (now + timedelta(days=7)).isoformat(),
                "accepted": False
            }
            
            workspace.pending_invitations[invitation_id] = invitation
            
            # Send notification to invited user (if they're already in the system)
            await self._send_notification(
                invitation_data["user_id"],
                "Workspace Invitation",
                f"You've been invited to join '{workspace.name}' workspace",
                "invitation",
                NotificationPriority.MEDIUM,
                {
                    "workspace_id": workspace_id,
                    "invitation_id": invitation_id,
                    "inviter": workspace.members[inviter_id].display_name or workspace.members[inviter_id].username
                }
            )
            
            logger.info(f"Invited user {invitation_data['user_id']} to workspace {workspace_id}")
            return invitation_id
            
        except Exception as e:
            logger.error(f"Error inviting member: {e}")
            raise
    
    async def accept_invitation(self, invitation_id: str, user_data: Dict[str, Any]) -> bool:
        """Accept workspace invitation
        
        Args:
            invitation_id: Invitation identifier
            user_data: User information
            
        Returns:
            Success status
        """
        try:
            # Find invitation across all workspaces
            workspace = None
            invitation = None
            
            for ws in self.workspaces.values():
                if invitation_id in ws.pending_invitations:
                    workspace = ws
                    invitation = ws.pending_invitations[invitation_id]
                    break
            
            if not workspace or not invitation:
                return False
            
            # Check if invitation is valid
            if invitation["accepted"]:
                return False
            
            expires_at = datetime.fromisoformat(invitation["expires_at"])
            if datetime.now(timezone.utc) > expires_at:
                return False
            
            # Check if user matches invitation
            if invitation["invited_user"] != user_data["user_id"]:
                return False
            
            # Add user to workspace
            now = datetime.now(timezone.utc)
            member = WorkspaceMember(
                user_id=user_data["user_id"],
                username=user_data.get("username", user_data["user_id"]),
                email=user_data.get("email", invitation["invited_email"]),
                role=WorkspaceRole(invitation["role"]),
                joined_at=now,
                display_name=user_data.get("display_name"),
                avatar_url=user_data.get("avatar_url"),
                invited_by=invitation["invited_by"]
            )
            
            workspace.members[user_data["user_id"]] = member
            self.user_workspaces[user_data["user_id"]].add(workspace.id)
            
            # Mark invitation as accepted
            invitation["accepted"] = True
            invitation["accepted_at"] = now.isoformat()
            
            # Log activity
            await self._log_activity(workspace, ActivityType.MEMBER_JOINED, {
                "actor_id": user_data["user_id"],
                "actor_name": member.display_name or member.username,
                "target_id": workspace.id,
                "target_name": workspace.name,
                "target_type": "workspace",
                "description": f"Joined the workspace"
            })
            
            # Send welcome notification
            await self._send_notification(
                user_data["user_id"],
                f"Welcome to {workspace.name}",
                f"You've successfully joined the '{workspace.name}' workspace",
                "welcome",
                NotificationPriority.MEDIUM,
                {"workspace_id": workspace.id}
            )
            
            logger.info(f"User {user_data['user_id']} joined workspace {workspace.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            return False
    
    async def upload_asset(self, workspace_id: str, user_id: str, 
                         asset_data: Dict[str, Any], file_path: str) -> Optional[str]:
        """Upload media asset to workspace
        
        Args:
            workspace_id: Workspace identifier
            user_id: User uploading asset
            asset_data: Asset metadata
            file_path: Path to asset file
            
        Returns:
            Asset ID or None
        """
        try:
            workspace = await self._get_workspace(workspace_id)
            if not workspace:
                return None
            
            # Check membership
            if user_id not in workspace.members:
                logger.warning(f"User {user_id} not a member of workspace {workspace_id}")
                return None
            
            # Check file size limits
            file_size = Path(file_path).stat().st_size
            max_size = workspace.settings.get("max_file_size", 100 * 1024 * 1024)
            
            if file_size > max_size:
                logger.warning(f"File too large: {file_size} > {max_size}")
                return None
            
            # Check storage quota
            if workspace.storage_used + file_size > workspace.storage_quota:
                logger.warning(f"Storage quota exceeded")
                return None
            
            asset_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Copy file to workspace storage
            workspace_dir = self.storage_root / workspace_id / "assets"
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            file_extension = Path(file_path).suffix
            stored_path = workspace_dir / f"{asset_id}{file_extension}"
            
            import shutil
            shutil.copy2(file_path, stored_path)
            
            # Create asset info
            asset = MediaAssetInfo(
                id=asset_id,
                name=asset_data.get("name", Path(file_path).name),
                type=asset_data.get("type", "unknown"),
                file_path=str(stored_path),
                created_by=user_id,
                created_at=now,
                file_size=file_size,
                mime_type=asset_data.get("mime_type", ""),
                description=asset_data.get("description", ""),
                tags=asset_data.get("tags", []),
                folder_id=asset_data.get("folder_id", "root")
            )
            
            # Add to workspace
            workspace.assets[asset_id] = asset
            workspace.storage_used += file_size
            
            # Add to folder
            if asset.folder_id and asset.folder_id in workspace.folders:
                workspace.folders[asset.folder_id].asset_ids.add(asset_id)
            
            # Log activity
            await self._log_activity(workspace, ActivityType.ASSET_UPLOADED, {
                "actor_id": user_id,
                "actor_name": workspace.members[user_id].display_name or workspace.members[user_id].username,
                "target_id": asset_id,
                "target_name": asset.name,
                "target_type": "asset",
                "description": f"Uploaded asset '{asset.name}'"
            })
            
            # Send notifications to team members
            if workspace.settings.get("auto_notifications", True):
                for member_id in workspace.members:
                    if member_id != user_id:
                        await self._send_notification(
                            member_id,
                            "New Asset Uploaded",
                            f"{workspace.members[user_id].display_name or workspace.members[user_id].username} uploaded '{asset.name}'",
                            "asset_upload",
                            NotificationPriority.LOW,
                            {
                                "workspace_id": workspace_id,
                                "asset_id": asset_id,
                                "uploader": user_id
                            }
                        )
            
            logger.info(f"Uploaded asset {asset_id} to workspace {workspace_id}")
            return asset_id
            
        except Exception as e:
            logger.error(f"Error uploading asset: {e}")
            return None
    
    async def create_project(self, workspace_id: str, user_id: str, 
                           project_data: Dict[str, Any]) -> Optional[str]:
        """Create a new project in workspace
        
        Args:
            workspace_id: Workspace identifier
            user_id: User creating project
            project_data: Project information
            
        Returns:
            Project ID or None
        """
        try:
            workspace = await self._get_workspace(workspace_id)
            if not workspace:
                return None
            
            # Check membership and permissions
            if user_id not in workspace.members:
                return None
            
            member = workspace.members[user_id]
            if member.role not in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER, WorkspaceRole.MODERATOR]:
                logger.warning(f"User {user_id} lacks permission to create projects")
                return None
            
            project_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            project = WorkspaceProject(
                id=project_id,
                name=project_data["name"],
                description=project_data.get("description", ""),
                created_by=user_id,
                created_at=now,
                status=ProjectStatus(project_data.get("status", "planning")),
                start_date=datetime.fromisoformat(project_data["start_date"]) if project_data.get("start_date") else None,
                due_date=datetime.fromisoformat(project_data["due_date"]) if project_data.get("due_date") else None,
                members=project_data.get("members", [user_id]),
                lead=project_data.get("lead", user_id),
                tags=project_data.get("tags", []),
                budget=project_data.get("budget"),
                client=project_data.get("client")
            )
            
            # Add milestones if provided
            if "milestones" in project_data:
                project.milestones = project_data["milestones"]
            
            workspace.projects[project_id] = project
            
            # Log activity
            await self._log_activity(workspace, ActivityType.PROJECT_CREATED, {
                "actor_id": user_id,
                "actor_name": member.display_name or member.username,
                "target_id": project_id,
                "target_name": project.name,
                "target_type": "project",
                "description": f"Created project '{project.name}'"
            })
            
            # Notify project members
            for member_id in project.members:
                if member_id != user_id and member_id in workspace.members:
                    await self._send_notification(
                        member_id,
                        "Added to Project",
                        f"You've been added to project '{project.name}'",
                        "project_assignment",
                        NotificationPriority.MEDIUM,
                        {
                            "workspace_id": workspace_id,
                            "project_id": project_id,
                            "creator": user_id
                        }
                    )
            
            logger.info(f"Created project {project_id} in workspace {workspace_id}")
            return project_id
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    async def create_folder(self, workspace_id: str, user_id: str, 
                          folder_data: Dict[str, Any]) -> Optional[str]:
        """Create a new folder in workspace
        
        Args:
            workspace_id: Workspace identifier
            user_id: User creating folder
            folder_data: Folder information
            
        Returns:
            Folder ID or None
        """
        try:
            workspace = await self._get_workspace(workspace_id)
            if not workspace:
                return None
            
            # Check membership
            if user_id not in workspace.members:
                return None
            
            folder_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            parent_id = folder_data.get("parent_id", "root")
            parent_folder = workspace.folders.get(parent_id)
            
            if not parent_folder:
                parent_id = "root"
                parent_folder = workspace.folders["root"]
            
            # Build path
            path = parent_folder.path
            if not path.endswith("/"):
                path += "/"
            path += folder_data["name"]
            
            folder = WorkspaceFolder(
                id=folder_id,
                name=folder_data["name"],
                created_by=user_id,
                created_at=now,
                parent_id=parent_id,
                path=path,
                description=folder_data.get("description", ""),
                color=folder_data.get("color")
            )
            
            workspace.folders[folder_id] = folder
            
            # Add to parent folder
            parent_folder.subfolder_ids.add(folder_id)
            
            logger.info(f"Created folder {folder_id} in workspace {workspace_id}")
            return folder_id
            
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return None
    
    async def get_workspace_dashboard(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """Get workspace dashboard data
        
        Args:
            workspace_id: Workspace identifier
            user_id: User requesting dashboard
            
        Returns:
            Dashboard data
        """
        try:
            workspace = await self._get_workspace(workspace_id)
            if not workspace or user_id not in workspace.members:
                return {}
            
            now = datetime.now(timezone.utc)
            week_ago = now - timedelta(days=7)
            
            # Recent activities
            recent_activities = [
                {
                    "id": activity.id,
                    "type": activity.type.value,
                    "actor_name": activity.actor_name,
                    "description": activity.description,
                    "timestamp": activity.timestamp.isoformat(),
                    "target_type": activity.target_type,
                    "target_name": activity.target_name
                }
                for activity in workspace.activities[-20:]  # Last 20 activities
            ]
            recent_activities.reverse()  # Most recent first
            
            # Asset statistics
            total_assets = len(workspace.assets)
            assets_this_week = len([a for a in workspace.assets.values() if a.created_at >= week_ago])
            
            # Project statistics
            active_projects = len([p for p in workspace.projects.values() if p.status == ProjectStatus.ACTIVE])
            total_projects = len(workspace.projects)
            
            # Storage information
            storage_used_mb = workspace.storage_used / (1024 * 1024)
            storage_quota_mb = workspace.storage_quota / (1024 * 1024)
            storage_percentage = (workspace.storage_used / workspace.storage_quota) * 100
            
            # Member activity
            active_members = len([m for m in workspace.members.values() 
                                if m.last_activity and m.last_activity >= week_ago])
            
            dashboard = {
                "workspace": {
                    "id": workspace.id,
                    "name": workspace.name,
                    "description": workspace.description,
                    "created_at": workspace.created_at.isoformat(),
                    "member_count": len(workspace.members),
                    "active_members": active_members
                },
                "statistics": {
                    "assets": {
                        "total": total_assets,
                        "this_week": assets_this_week,
                        "by_type": self._get_asset_type_distribution(workspace)
                    },
                    "projects": {
                        "total": total_projects,
                        "active": active_projects,
                        "by_status": self._get_project_status_distribution(workspace)
                    },
                    "storage": {
                        "used_mb": round(storage_used_mb, 2),
                        "quota_mb": round(storage_quota_mb, 2),
                        "percentage": round(storage_percentage, 1)
                    }
                },
                "recent_activities": recent_activities,
                "user_notifications": len(workspace.notifications.get(user_id, [])),
                "quick_actions": self._get_quick_actions(workspace, user_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting workspace dashboard: {e}")
            return {}
    
    async def get_user_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
        """Get workspaces for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user's workspaces
        """
        try:
            user_workspace_ids = self.user_workspaces.get(user_id, set())
            workspaces = []
            
            for workspace_id in user_workspace_ids:
                workspace = await self._get_workspace(workspace_id)
                if workspace and user_id in workspace.members:
                    member = workspace.members[user_id]
                    
                    workspaces.append({
                        "id": workspace.id,
                        "name": workspace.name,
                        "description": workspace.description,
                        "role": member.role.value,
                        "member_count": len(workspace.members),
                        "asset_count": len(workspace.assets),
                        "project_count": len(workspace.projects),
                        "last_activity": workspace.updated_at.isoformat(),
                        "unread_notifications": len([n for n in workspace.notifications.get(user_id, []) if not n.read])
                    })
            
            # Sort by last activity
            workspaces.sort(key=lambda w: w["last_activity"], reverse=True)
            return workspaces
            
        except Exception as e:
            logger.error(f"Error getting user workspaces: {e}")
            return []
    
    async def _get_workspace(self, workspace_id: str) -> Optional[TeamMediaWorkspace]:
        """Get workspace by ID"""
        if workspace_id in self.workspaces:
            return self.workspaces[workspace_id]
        
        # Try loading from storage (simplified)
        return None
    
    async def _log_activity(self, workspace: TeamMediaWorkspace, activity_type: ActivityType, 
                          data: Dict[str, Any]):
        """Log activity to workspace feed"""
        activity = WorkspaceActivity(
            id=str(uuid.uuid4()),
            type=activity_type,
            actor_id=data["actor_id"],
            actor_name=data["actor_name"],
            timestamp=datetime.now(timezone.utc),
            target_id=data["target_id"],
            target_name=data["target_name"],
            target_type=data["target_type"],
            description=data["description"],
            metadata=data.get("metadata", {})
        )
        
        workspace.activities.append(activity)
        
        # Keep only last 1000 activities
        if len(workspace.activities) > 1000:
            workspace.activities = workspace.activities[-1000:]
    
    async def _send_notification(self, user_id: str, title: str, message: str, 
                               notification_type: str, priority: NotificationPriority,
                               metadata: Dict[str, Any] = None):
        """Send notification to user"""
        notification = WorkspaceNotification(
            id=str(uuid.uuid4()),
            recipient_id=user_id,
            title=title,
            message=message,
            created_at=datetime.now(timezone.utc),
            type=notification_type,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Find workspace to add notification
        workspace_id = metadata.get("workspace_id") if metadata else None
        if workspace_id and workspace_id in self.workspaces:
            workspace = self.workspaces[workspace_id]
            if user_id not in workspace.notifications:
                workspace.notifications[user_id] = []
            
            workspace.notifications[user_id].append(notification)
            
            # Keep only last 100 notifications per user
            if len(workspace.notifications[user_id]) > 100:
                workspace.notifications[user_id] = workspace.notifications[user_id][-100:]
    
    def _check_admin_permission(self, workspace: TeamMediaWorkspace, user_id: str) -> bool:
        """Check if user has admin permissions"""
        if user_id not in workspace.members:
            return False
        
        role = workspace.members[user_id].role
        return role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER]
    
    def _get_asset_type_distribution(self, workspace: TeamMediaWorkspace) -> Dict[str, int]:
        """Get distribution of asset types"""
        distribution = defaultdict(int)
        for asset in workspace.assets.values():
            distribution[asset.type] += 1
        return dict(distribution)
    
    def _get_project_status_distribution(self, workspace: TeamMediaWorkspace) -> Dict[str, int]:
        """Get distribution of project statuses"""
        distribution = defaultdict(int)
        for project in workspace.projects.values():
            distribution[project.status.value] += 1
        return dict(distribution)
    
    def _get_quick_actions(self, workspace: TeamMediaWorkspace, user_id: str) -> List[Dict[str, str]]:
        """Get quick actions for user"""
        member = workspace.members[user_id]
        actions = [
            {"name": "Upload Asset", "action": "upload_asset"},
            {"name": "Browse Assets", "action": "browse_assets"}
        ]
        
        if member.role in [WorkspaceRole.ADMIN, WorkspaceRole.OWNER, WorkspaceRole.MODERATOR]:
            actions.extend([
                {"name": "Create Project", "action": "create_project"},
                {"name": "Invite Member", "action": "invite_member"},
                {"name": "Manage Workspace", "action": "manage_workspace"}
            ])
        
        return actions


# Convenience functions for easy usage
async def create_team_workspace(name: str, description: str, created_by: str,
                              creator_data: Dict[str, Any] = None) -> str:
    """Create a new team workspace
    
    Args:
        name: Workspace name
        description: Workspace description
        created_by: Creator user ID
        creator_data: Additional creator information
        
    Returns:
        Workspace ID
    """
    manager = TeamMediaWorkspaceManager()
    
    workspace_data = {
        "name": name,
        "description": description,
        "created_by": created_by,
        **(creator_data or {})
    }
    
    return await manager.create_workspace(workspace_data)


async def join_workspace(invitation_id: str, user_id: str, username: str,
                       email: str, display_name: Optional[str] = None) -> bool:
    """Join a workspace using invitation
    
    Args:
        invitation_id: Invitation identifier
        user_id: User identifier
        username: Username
        email: User email
        display_name: Optional display name
        
    Returns:
        Success status
    """
    manager = TeamMediaWorkspaceManager()
    
    user_data = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "display_name": display_name
    }
    
    return await manager.accept_invitation(invitation_id, user_data)


async def upload_workspace_asset(workspace_id: str, user_id: str, file_path: str,
                                name: str, asset_type: str, description: str = "",
                                tags: List[str] = None) -> Optional[str]:
    """Upload asset to workspace
    
    Args:
        workspace_id: Workspace identifier
        user_id: User uploading
        file_path: Path to file
        name: Asset name
        asset_type: Asset type
        description: Asset description
        tags: Asset tags
        
    Returns:
        Asset ID or None
    """
    manager = TeamMediaWorkspaceManager()
    
    asset_data = {
        "name": name,
        "type": asset_type,
        "description": description,
        "tags": tags or []
    }
    
    return await manager.upload_asset(workspace_id, user_id, asset_data, file_path)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create workspace manager
        manager = TeamMediaWorkspaceManager()
        
        # Create workspace
        workspace_data = {
            "name": "Creative Team Workspace",
            "description": "Collaborative space for our creative projects",
            "created_by": "creator_1",
            "creator_username": "john_creator",
            "creator_email": "john@example.com",
            "creator_name": "John Creator"
        }
        
        workspace_id = await manager.create_workspace(workspace_data)
        print(f"Created workspace: {workspace_id}")
        
        # Invite member
        invitation_data = {
            "user_id": "editor_1",
            "email": "editor@example.com",
            "role": "editor",
            "message": "Welcome to our creative team!"
        }
        
        invitation_id = await manager.invite_member(workspace_id, "creator_1", invitation_data)
        print(f"Sent invitation: {invitation_id}")
        
        # Accept invitation
        user_data = {
            "user_id": "editor_1",
            "username": "jane_editor",
            "email": "editor@example.com",
            "display_name": "Jane Editor"
        }
        
        accepted = await manager.accept_invitation(invitation_id, user_data)
        print(f"Invitation accepted: {accepted}")
        
        # Get dashboard
        dashboard = await manager.get_workspace_dashboard(workspace_id, "creator_1")
        print(f"Dashboard: {json.dumps(dashboard, indent=2, default=str)}")
    
    asyncio.run(main())