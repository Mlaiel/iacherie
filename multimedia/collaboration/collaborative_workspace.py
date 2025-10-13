"""
👥 COLLABORATIVE WORKSPACE - ENTERPRISE ARCHITECTURE
=================================================

Advanced team workspace management for multimedia collaboration with 
real-time synchronization, project organization, and team coordination.

**Expert Implementation:**
- Collaboration Engineer: Workspace design and team coordination
- Backend Senior: High-performance workspace infrastructure
- Database Administrator: Efficient workspace data management
- Security Engineer: Workspace access control and data protection

**Features:** Team workspaces, Project organization, Real-time coordination, Asset management
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
import copy

# Workspace libraries
try:
    import redis
    import websockets
    from concurrent.futures import ThreadPoolExecutor
    import aiofiles
    import numpy as np
except ImportError as e:
    logging.warning(f"Collaborative workspace dependencies not available: {e}")

logger = logging.getLogger(__name__)

class WorkspaceType(Enum):
    """Types of collaborative workspaces"""
    MULTIMEDIA_PRODUCTION = "multimedia_production"
    VIDEO_EDITING = "video_editing"
    AUDIO_PRODUCTION = "audio_production"
    IMAGE_EDITING = "image_editing"
    CONTENT_CREATION = "content_creation"
    LIVE_STREAMING = "live_streaming"
    PODCAST_PRODUCTION = "podcast_production"

class WorkspaceStatus(Enum):
    """Workspace status states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    MAINTENANCE = "maintenance"

class ActivityType(Enum):
    """Types of workspace activities"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CONTENT_MODIFIED = "content_modified"
    FILE_UPLOADED = "file_uploaded"
    COMMENT_ADDED = "comment_added"
    EFFECT_APPLIED = "effect_applied"
    VERSION_CREATED = "version_created"
    APPROVAL_REQUESTED = "approval_requested"

@dataclass
class WorkspaceConfig:
    """Workspace configuration"""
    workspace_id: str
    name: str
    description: str
    workspace_type: WorkspaceType
    created_by: str
    created_at: float
    max_members: int
    storage_limit_gb: float
    features_enabled: List[str]
    settings: Dict[str, Any]

@dataclass 
class WorkspaceMember:
    """Workspace member representation"""
    user_id: str
    username: str
    email: str
    role: str
    permissions: List[str]
    joined_at: float
    last_active: float
    is_online: bool
    current_activity: Optional[str]

@dataclass
class WorkspaceActivity:
    """Workspace activity log entry"""
    activity_id: str
    workspace_id: str
    user_id: str
    activity_type: ActivityType
    description: str
    timestamp: float
    metadata: Dict[str, Any]
    
@dataclass
class WorkspaceAsset:
    """Workspace asset representation"""
    asset_id: str
    workspace_id: str
    name: str
    asset_type: str
    file_path: str
    file_size: int
    uploaded_by: str
    uploaded_at: float
    tags: List[str]
    metadata: Dict[str, Any]
    is_shared: bool
    access_permissions: Dict[str, List[str]]

class CollaborativeWorkspace:
    """Main collaborative workspace manager"""
    
    def __init__(self):
        self.workspaces = {}  # workspace_id -> WorkspaceConfig
        self.workspace_members = defaultdict(dict)  # workspace_id -> {user_id -> WorkspaceMember}
        self.workspace_activities = defaultdict(deque)  # workspace_id -> activities
        self.workspace_assets = defaultdict(dict)  # workspace_id -> {asset_id -> WorkspaceAsset}
        self.active_sessions = defaultdict(set)  # workspace_id -> set of user_ids
        
        # Real-time communication
        self.websocket_connections = {}  # user_id -> websocket
        self.workspace_channels = defaultdict(set)  # workspace_id -> set of user_ids
        
        # Storage and caching
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except:
            self.redis_client = None
            logger.warning("Redis not available for workspace caching")
        
        # Workspace settings
        self.default_storage_limit = 10.0  # GB
        self.max_workspace_members = 100
        self.activity_history_limit = 1000
        
    async def create_workspace(self, creator_id: str, name: str, 
                             workspace_type: WorkspaceType, description: str = "",
                             custom_settings: Dict[str, Any] = None) -> WorkspaceConfig:
        """Create new collaborative workspace"""
        try:
            workspace_id = str(uuid.uuid4())
            
            # Default workspace settings
            default_settings = {
                'real_time_sync': True,
                'version_control': True,
                'comment_system': True,
                'approval_workflow': False,
                'notification_enabled': True,
                'auto_save_interval': 30,  # seconds
                'conflict_resolution': 'auto',
                'collaboration_features': [
                    'shared_editing',
                    'real_time_cursor',
                    'voice_chat',
                    'screen_sharing'
                ]
            }
            
            # Merge custom settings
            settings = {**default_settings, **(custom_settings or {})}
            
            # Create workspace config
            workspace_config = WorkspaceConfig(
                workspace_id=workspace_id,
                name=name,
                description=description,
                workspace_type=workspace_type,
                created_by=creator_id,
                created_at=time.time(),
                max_members=self.max_workspace_members,
                storage_limit_gb=self.default_storage_limit,
                features_enabled=settings['collaboration_features'],
                settings=settings
            )
            
            # Store workspace
            self.workspaces[workspace_id] = workspace_config
            
            # Add creator as owner
            await self.add_member(workspace_id, creator_id, role="owner")
            
            # Initialize workspace directories
            await self._initialize_workspace_storage(workspace_id)
            
            # Log creation activity
            await self._log_activity(
                workspace_id, creator_id, ActivityType.USER_JOINED,
                f"Created workspace '{name}'"
            )
            
            # Store in persistent storage
            if self.redis_client:
                await self._store_workspace_redis(workspace_config)
            
            logger.info(f"Created workspace {workspace_id}: {name}")
            return workspace_config
            
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            raise
    
    async def add_member(self, workspace_id: str, user_id: str, 
                        role: str = "member", permissions: List[str] = None,
                        user_info: Dict[str, Any] = None) -> WorkspaceMember:
        """Add member to workspace"""
        try:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            # Default permissions based on role
            default_permissions = self._get_default_permissions(role)
            member_permissions = permissions or default_permissions
            
            # Get user info
            user_data = user_info or {}
            username = user_data.get('username', f'user_{user_id}')
            email = user_data.get('email', f'{user_id}@example.com')
            
            member = WorkspaceMember(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                permissions=member_permissions,
                joined_at=time.time(),
                last_active=time.time(),
                is_online=False,
                current_activity=None
            )
            
            # Add to workspace
            self.workspace_members[workspace_id][user_id] = member
            
            # Log activity
            await self._log_activity(
                workspace_id, user_id, ActivityType.USER_JOINED,
                f"{username} joined workspace as {role}"
            )
            
            # Notify other members
            await self._broadcast_workspace_event(workspace_id, {
                'type': 'member_added',
                'user_id': user_id,
                'username': username,
                'role': role,
                'timestamp': time.time()
            })
            
            logger.info(f"Added member {user_id} to workspace {workspace_id}")
            return member
            
        except Exception as e:
            logger.error(f"Failed to add member: {e}")
            raise
    
    async def join_workspace_session(self, workspace_id: str, user_id: str,
                                   websocket=None) -> Dict[str, Any]:
        """User joins active workspace session"""
        try:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            if user_id not in self.workspace_members[workspace_id]:
                raise ValueError(f"User {user_id} not a member of workspace")
            
            # Update member status
            member = self.workspace_members[workspace_id][user_id]
            member.is_online = True
            member.last_active = time.time()
            
            # Add to active session
            self.active_sessions[workspace_id].add(user_id)
            
            # Store websocket connection
            if websocket:
                self.websocket_connections[user_id] = websocket
                self.workspace_channels[workspace_id].add(user_id)
            
            # Get workspace state
            workspace_state = await self._get_workspace_state(workspace_id)
            
            # Log activity
            await self._log_activity(
                workspace_id, user_id, ActivityType.USER_JOINED,
                f"{member.username} joined session"
            )
            
            # Notify other members
            await self._broadcast_workspace_event(workspace_id, {
                'type': 'user_joined_session',
                'user_id': user_id,
                'username': member.username,
                'timestamp': time.time()
            }, exclude_user=user_id)
            
            logger.info(f"User {user_id} joined workspace session {workspace_id}")
            return {
                'status': 'joined',
                'workspace_state': workspace_state,
                'active_members': len(self.active_sessions[workspace_id]),
                'user_role': member.role,
                'permissions': member.permissions
            }
            
        except Exception as e:
            logger.error(f"Failed to join workspace session: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def leave_workspace_session(self, workspace_id: str, user_id: str) -> Dict[str, Any]:
        """User leaves workspace session"""
        try:
            # Update member status
            if user_id in self.workspace_members[workspace_id]:
                member = self.workspace_members[workspace_id][user_id]
                member.is_online = False
                member.last_active = time.time()
            
            # Remove from active session
            self.active_sessions[workspace_id].discard(user_id)
            
            # Remove websocket connection
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
            self.workspace_channels[workspace_id].discard(user_id)
            
            # Log activity
            await self._log_activity(
                workspace_id, user_id, ActivityType.USER_LEFT,
                f"User left session"
            )
            
            # Notify other members
            await self._broadcast_workspace_event(workspace_id, {
                'type': 'user_left_session',
                'user_id': user_id,
                'timestamp': time.time()
            })
            
            logger.info(f"User {user_id} left workspace session {workspace_id}")
            return {'status': 'left'}
            
        except Exception as e:
            logger.error(f"Failed to leave workspace session: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def upload_asset(self, workspace_id: str, user_id: str,
                          file_name: str, file_data: bytes, 
                          asset_type: str = "file", tags: List[str] = None,
                          metadata: Dict[str, Any] = None) -> WorkspaceAsset:
        """Upload asset to workspace"""
        try:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            asset_id = str(uuid.uuid4())
            
            # Store file
            file_path = await self._store_workspace_file(
                workspace_id, asset_id, file_name, file_data
            )
            
            # Create asset record
            asset = WorkspaceAsset(
                asset_id=asset_id,
                workspace_id=workspace_id,
                name=file_name,
                asset_type=asset_type,
                file_path=file_path,
                file_size=len(file_data),
                uploaded_by=user_id,
                uploaded_at=time.time(),
                tags=tags or [],
                metadata=metadata or {},
                is_shared=True,
                access_permissions={'read': ['all'], 'write': [user_id]}
            )
            
            # Store asset
            self.workspace_assets[workspace_id][asset_id] = asset
            
            # Log activity
            await self._log_activity(
                workspace_id, user_id, ActivityType.FILE_UPLOADED,
                f"Uploaded {file_name} ({len(file_data)} bytes)"
            )
            
            # Notify workspace members
            await self._broadcast_workspace_event(workspace_id, {
                'type': 'asset_uploaded',
                'asset_id': asset_id,
                'file_name': file_name,
                'uploaded_by': user_id,
                'timestamp': time.time()
            })
            
            logger.info(f"Uploaded asset {asset_id} to workspace {workspace_id}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to upload asset: {e}")
            raise
    
    async def get_workspace_assets(self, workspace_id: str, 
                                 user_id: str = None) -> List[WorkspaceAsset]:
        """Get assets in workspace"""
        try:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            assets = list(self.workspace_assets[workspace_id].values())
            
            # Filter by user permissions if specified
            if user_id:
                filtered_assets = []
                for asset in assets:
                    if self._check_asset_permission(asset, user_id, 'read'):
                        filtered_assets.append(asset)
                assets = filtered_assets
            
            # Sort by upload time (newest first)
            assets.sort(key=lambda a: a.uploaded_at, reverse=True)
            
            return assets
            
        except Exception as e:
            logger.error(f"Failed to get workspace assets: {e}")
            return []
    
    async def get_workspace_activity(self, workspace_id: str, 
                                   limit: int = 50) -> List[WorkspaceActivity]:
        """Get recent workspace activity"""
        try:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            activities = list(self.workspace_activities[workspace_id])
            
            # Return most recent activities
            return list(reversed(activities))[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get workspace activity: {e}")
            return []
    
    async def get_workspace_members(self, workspace_id: str) -> List[WorkspaceMember]:
        """Get workspace members"""
        try:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            members = list(self.workspace_members[workspace_id].values())
            
            # Sort by role priority and join date
            role_priority = {'owner': 0, 'admin': 1, 'editor': 2, 'reviewer': 3, 'member': 4}
            members.sort(key=lambda m: (role_priority.get(m.role, 999), m.joined_at))
            
            return members
            
        except Exception as e:
            logger.error(f"Failed to get workspace members: {e}")
            return []
    
    async def update_user_activity(self, workspace_id: str, user_id: str,
                                 activity: str) -> bool:
        """Update user's current activity"""
        try:
            if user_id in self.workspace_members[workspace_id]:
                member = self.workspace_members[workspace_id][user_id]
                member.current_activity = activity
                member.last_active = time.time()
                
                # Broadcast activity update
                await self._broadcast_workspace_event(workspace_id, {
                    'type': 'user_activity_updated',
                    'user_id': user_id,
                    'activity': activity,
                    'timestamp': time.time()
                })
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update user activity: {e}")
            return False
    
    async def _get_workspace_state(self, workspace_id: str) -> Dict[str, Any]:
        """Get current workspace state"""
        try:
            workspace = self.workspaces[workspace_id]
            members = await self.get_workspace_members(workspace_id)
            assets = await self.get_workspace_assets(workspace_id)
            recent_activity = await self.get_workspace_activity(workspace_id, 20)
            
            return {
                'workspace_config': asdict(workspace),
                'active_members': len(self.active_sessions[workspace_id]),
                'total_members': len(members),
                'total_assets': len(assets),
                'recent_activities': [asdict(a) for a in recent_activity],
                'online_members': [
                    {'user_id': m.user_id, 'username': m.username, 'activity': m.current_activity}
                    for m in members if m.is_online
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get workspace state: {e}")
            return {}
    
    async def _log_activity(self, workspace_id: str, user_id: str,
                          activity_type: ActivityType, description: str,
                          metadata: Dict[str, Any] = None):
        """Log workspace activity"""
        try:
            activity = WorkspaceActivity(
                activity_id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                user_id=user_id,
                activity_type=activity_type,
                description=description,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            
            # Add to activity log
            activities = self.workspace_activities[workspace_id]
            activities.append(activity)
            
            # Maintain activity history limit
            while len(activities) > self.activity_history_limit:
                activities.popleft()
                
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    async def _broadcast_workspace_event(self, workspace_id: str, 
                                       event_data: Dict[str, Any],
                                       exclude_user: str = None):
        """Broadcast event to all workspace members"""
        try:
            active_users = self.workspace_channels.get(workspace_id, set())
            
            for user_id in active_users:
                if exclude_user and user_id == exclude_user:
                    continue
                    
                if user_id in self.websocket_connections:
                    websocket = self.websocket_connections[user_id]
                    try:
                        await websocket.send(json.dumps({
                            'type': 'workspace_event',
                            'workspace_id': workspace_id,
                            'data': event_data
                        }))
                    except:
                        # Remove broken connection
                        del self.websocket_connections[user_id]
                        self.workspace_channels[workspace_id].discard(user_id)
                        
        except Exception as e:
            logger.error(f"Failed to broadcast workspace event: {e}")
    
    def _get_default_permissions(self, role: str) -> List[str]:
        """Get default permissions for role"""
        permission_map = {
            'owner': ['read', 'write', 'delete', 'admin', 'approve', 'manage_team'],
            'admin': ['read', 'write', 'delete', 'approve', 'manage_team'],
            'editor': ['read', 'write', 'comment', 'request_approval'],
            'reviewer': ['read', 'comment', 'approve', 'request_changes'],
            'member': ['read', 'comment'],
            'viewer': ['read']
        }
        return permission_map.get(role, ['read'])
    
    def _check_asset_permission(self, asset: WorkspaceAsset, 
                              user_id: str, permission: str) -> bool:
        """Check if user has permission for asset"""
        # Check if permission is granted to all users
        if 'all' in asset.access_permissions.get(permission, []):
            return True
        
        # Check if user specifically has permission
        if user_id in asset.access_permissions.get(permission, []):
            return True
        
        return False
    
    async def _initialize_workspace_storage(self, workspace_id: str):
        """Initialize storage directories for workspace"""
        try:
            # Create workspace directory structure
            # In production, this would create actual directories
            logger.info(f"Initialized storage for workspace {workspace_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace storage: {e}")
    
    async def _store_workspace_file(self, workspace_id: str, asset_id: str,
                                  file_name: str, file_data: bytes) -> str:
        """Store file in workspace storage"""
        try:
            # In production, store in actual file system or cloud storage
            file_path = f"/workspaces/{workspace_id}/assets/{asset_id}_{file_name}"
            
            # Simulate file storage
            logger.info(f"Stored file {file_name} at {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to store workspace file: {e}")
            raise
    
    async def _store_workspace_redis(self, workspace_config: WorkspaceConfig):
        """Store workspace config in Redis"""
        try:
            if self.redis_client:
                key = f"workspace:{workspace_config.workspace_id}"
                value = json.dumps(asdict(workspace_config), default=str)
                self.redis_client.setex(key, 86400, value)  # 24 hour expiry
                
        except Exception as e:
            logger.error(f"Failed to store workspace in Redis: {e}")

class WorkspaceManager:
    """High-level workspace management"""
    
    def __init__(self):
        self.workspace_engine = CollaborativeWorkspace()
        self.workspace_templates = self._load_workspace_templates()
    
    async def create_workspace_from_template(self, creator_id: str, 
                                           template_name: str,
                                           workspace_name: str) -> WorkspaceConfig:
        """Create workspace from predefined template"""
        try:
            if template_name not in self.workspace_templates:
                raise ValueError(f"Template {template_name} not found")
            
            template = self.workspace_templates[template_name]
            
            workspace = await self.workspace_engine.create_workspace(
                creator_id=creator_id,
                name=workspace_name,
                workspace_type=WorkspaceType(template['workspace_type']),
                description=template['description'],
                custom_settings=template['settings']
            )
            
            # Add template-specific assets
            for asset in template.get('default_assets', []):
                await self._add_template_asset(workspace.workspace_id, creator_id, asset)
            
            return workspace
            
        except Exception as e:
            logger.error(f"Failed to create workspace from template: {e}")
            raise
    
    async def get_workspace_analytics(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace analytics and metrics"""
        try:
            workspace = self.workspace_engine.workspaces.get(workspace_id)
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            members = await self.workspace_engine.get_workspace_members(workspace_id)
            assets = await self.workspace_engine.get_workspace_assets(workspace_id)
            activities = await self.workspace_engine.get_workspace_activity(workspace_id, 100)
            
            # Calculate metrics
            total_storage_used = sum(asset.file_size for asset in assets)
            active_members_today = len([
                m for m in members 
                if m.last_active > (time.time() - 86400)  # Last 24 hours
            ])
            
            activity_by_type = defaultdict(int)
            for activity in activities:
                activity_by_type[activity.activity_type.value] += 1
            
            return {
                'workspace_id': workspace_id,
                'total_members': len(members),
                'active_members_today': active_members_today,
                'total_assets': len(assets),
                'storage_used_mb': total_storage_used / (1024 * 1024),
                'storage_limit_mb': workspace.storage_limit_gb * 1024,
                'activity_summary': dict(activity_by_type),
                'creation_date': workspace.created_at,
                'workspace_type': workspace.workspace_type.value
            }
            
        except Exception as e:
            logger.error(f"Failed to get workspace analytics: {e}")
            return {}
    
    def _load_workspace_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined workspace templates"""
        return {
            'video_production': {
                'workspace_type': 'video_editing',
                'description': 'Professional video production workspace',
                'settings': {
                    'collaboration_features': [
                        'shared_editing', 'real_time_cursor', 'voice_chat',
                        'screen_sharing', 'timeline_sync'
                    ],
                    'approval_workflow': True,
                    'version_control': True,
                    'auto_save_interval': 15
                },
                'default_assets': []
            },
            'podcast_studio': {
                'workspace_type': 'audio_production',
                'description': 'Podcast recording and editing studio',
                'settings': {
                    'collaboration_features': [
                        'shared_editing', 'voice_chat', 'waveform_sync'
                    ],
                    'approval_workflow': False,
                    'version_control': True,
                    'auto_save_interval': 30
                },
                'default_assets': []
            },
            'content_creation': {
                'workspace_type': 'content_creation',
                'description': 'Multi-format content creation workspace',
                'settings': {
                    'collaboration_features': [
                        'shared_editing', 'real_time_cursor', 'comment_system',
                        'approval_workflow', 'asset_library'
                    ],
                    'approval_workflow': True,
                    'version_control': True,
                    'auto_save_interval': 20
                },
                'default_assets': []
            }
        }
    
    async def _add_template_asset(self, workspace_id: str, user_id: str, 
                                asset_info: Dict[str, Any]):
        """Add template asset to workspace"""
        try:
            # In production, load actual template assets
            # For now, create placeholder
            placeholder_data = b"Template asset data"
            
            await self.workspace_engine.upload_asset(
                workspace_id=workspace_id,
                user_id=user_id,
                file_name=asset_info['name'],
                file_data=placeholder_data,
                asset_type=asset_info['type'],
                tags=asset_info.get('tags', []),
                metadata=asset_info.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"Failed to add template asset: {e}")

# Module exports
__all__ = [
    'CollaborativeWorkspace',
    'WorkspaceManager',
    'WorkspaceConfig',
    'WorkspaceMember',
    'WorkspaceActivity',
    'WorkspaceAsset',
    'WorkspaceType',
    'WorkspaceStatus',
    'ActivityType'
]