# -*- coding: utf-8 -*-
"""
IA Chérie Platform - Enterprise Permission Handler
Advanced permission management system with role-based access control
Author: IA Chérie Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import time
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class PermissionLevel(Enum):
    """Permission levels"""
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3
    SUPER_ADMIN = 4

class ResourceType(Enum):
    """Resource types"""
    USER = "user"
    CONTENT = "content"
    API = "api"
    SYSTEM = "system"
    ANALYTICS = "analytics"
    PAYMENTS = "payments"
    INTEGRATIONS = "integrations"

@dataclass
class Permission:
    """Permission definition"""
    id: str
    name: str
    resource_type: ResourceType
    level: PermissionLevel
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    
@dataclass
class Role:
    """Role definition with permissions"""
    id: str
    name: str
    permissions: Set[str] = field(default_factory=set)
    description: str = ""
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserPermissions:
    """User permission cache"""
    user_id: str
    roles: Set[str] = field(default_factory=set)
    direct_permissions: Set[str] = field(default_factory=set)
    effective_permissions: Set[str] = field(default_factory=set)
    last_updated: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

class PermissionHandler:
    """Enterprise Permission Handler"""
    
    def __init__(self):
        """Initialize permission handler"""
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.user_permissions: Dict[str, UserPermissions] = {}
        self.permission_cache_ttl = timedelta(hours=1)
        self._lock = threading.RLock()
        
        # Initialize default permissions and roles
        self._initialize_default_permissions()
        self._initialize_default_roles()
        
        logger.info("🔐 Permission Handler initialized successfully")
    
    def _initialize_default_permissions(self):
        """Initialize default permissions"""
        default_permissions = [
            # User permissions
            Permission("user.read", "Read Users", ResourceType.USER, PermissionLevel.READ, "View user information"),
            Permission("user.write", "Write Users", ResourceType.USER, PermissionLevel.WRITE, "Create/update users"),
            Permission("user.admin", "Admin Users", ResourceType.USER, PermissionLevel.ADMIN, "Full user management"),
            
            # Content permissions
            Permission("content.read", "Read Content", ResourceType.CONTENT, PermissionLevel.READ, "View content"),
            Permission("content.write", "Write Content", ResourceType.CONTENT, PermissionLevel.WRITE, "Create/edit content"),
            Permission("content.admin", "Admin Content", ResourceType.CONTENT, PermissionLevel.ADMIN, "Full content management"),
            
            # API permissions
            Permission("api.read", "API Read", ResourceType.API, PermissionLevel.READ, "Read API access"),
            Permission("api.write", "API Write", ResourceType.API, PermissionLevel.WRITE, "Write API access"),
            Permission("api.admin", "API Admin", ResourceType.API, PermissionLevel.ADMIN, "Full API management"),
            
            # System permissions
            Permission("system.read", "System Read", ResourceType.SYSTEM, PermissionLevel.READ, "View system info"),
            Permission("system.admin", "System Admin", ResourceType.SYSTEM, PermissionLevel.ADMIN, "System administration"),
            Permission("system.super_admin", "Super Admin", ResourceType.SYSTEM, PermissionLevel.SUPER_ADMIN, "Full system control")
        ]
        
        for perm in default_permissions:
            self.permissions[perm.id] = perm
        
        logger.info(f"🎭 Initialized {len(default_permissions)} default permissions")
    
    def _initialize_default_roles(self):
        """Initialize default roles"""
        default_roles = [
            Role("viewer", "Viewer", {"user.read", "content.read", "api.read"}, "Basic read access", True),
            Role("creator", "Creator", {"user.read", "content.read", "content.write", "api.read"}, "Content creation access", True),
            Role("moderator", "Moderator", {"user.read", "user.write", "content.read", "content.write", "content.admin", "api.read"}, "Content moderation access", True),
            Role("admin", "Administrator", {"user.read", "user.write", "user.admin", "content.read", "content.write", "content.admin", "api.read", "api.write", "api.admin", "system.read"}, "Administrative access", True),
            Role("super_admin", "Super Administrator", set(self.permissions.keys()), "Full system access", True)
        ]
        
        for role in default_roles:
            self.roles[role.id] = role
        
        logger.info(f"👑 Initialized {len(default_roles)} default roles")
    
    def create_permission(self, permission_id: str, name: str, resource_type: ResourceType, 
                         level: PermissionLevel, description: str = "") -> bool:
        """Create a new permission"""
        try:
            with self._lock:
                if permission_id in self.permissions:
                    logger.warning(f"⚠️ Permission {permission_id} already exists")
                    return False
                
                permission = Permission(
                    id=permission_id,
                    name=name,
                    resource_type=resource_type,
                    level=level,
                    description=description
                )
                
                self.permissions[permission_id] = permission
                logger.info(f"✅ Created permission: {permission_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error creating permission {permission_id}: {str(e)}")
            return False
    
    def create_role(self, role_id: str, name: str, permissions: Set[str], 
                   description: str = "", is_system_role: bool = False) -> bool:
        """Create a new role"""
        try:
            with self._lock:
                if role_id in self.roles:
                    logger.warning(f"⚠️ Role {role_id} already exists")
                    return False
                
                # Validate permissions exist
                invalid_perms = permissions - set(self.permissions.keys())
                if invalid_perms:
                    logger.error(f"❌ Invalid permissions: {invalid_perms}")
                    return False
                
                role = Role(
                    id=role_id,
                    name=name,
                    permissions=permissions.copy(),
                    description=description,
                    is_system_role=is_system_role
                )
                
                self.roles[role_id] = role
                logger.info(f"✅ Created role: {role_id} with {len(permissions)} permissions")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error creating role {role_id}: {str(e)}")
            return False
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign role to user"""
        try:
            with self._lock:
                if role_id not in self.roles:
                    logger.error(f"❌ Role {role_id} does not exist")
                    return False
                
                if user_id not in self.user_permissions:
                    self.user_permissions[user_id] = UserPermissions(user_id=user_id)
                
                self.user_permissions[user_id].roles.add(role_id)
                self._refresh_user_permissions(user_id)
                
                logger.info(f"✅ Assigned role {role_id} to user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error assigning role {role_id} to user {user_id}: {str(e)}")
            return False
    
    def grant_permission_to_user(self, user_id: str, permission_id: str) -> bool:
        """Grant direct permission to user"""
        try:
            with self._lock:
                if permission_id not in self.permissions:
                    logger.error(f"❌ Permission {permission_id} does not exist")
                    return False
                
                if user_id not in self.user_permissions:
                    self.user_permissions[user_id] = UserPermissions(user_id=user_id)
                
                self.user_permissions[user_id].direct_permissions.add(permission_id)
                self._refresh_user_permissions(user_id)
                
                logger.info(f"✅ Granted permission {permission_id} to user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error granting permission {permission_id} to user {user_id}: {str(e)}")
            return False
    
    def _refresh_user_permissions(self, user_id: str):
        """Refresh user's effective permissions"""
        if user_id not in self.user_permissions:
            return
        
        user_perms = self.user_permissions[user_id]
        effective_permissions = set()
        
        # Add permissions from roles
        for role_id in user_perms.roles:
            if role_id in self.roles:
                effective_permissions.update(self.roles[role_id].permissions)
        
        # Add direct permissions
        effective_permissions.update(user_perms.direct_permissions)
        
        user_perms.effective_permissions = effective_permissions
        user_perms.last_updated = datetime.now()
        user_perms.expires_at = datetime.now() + self.permission_cache_ttl
    
    def has_permission(self, user_id: str, permission_id: str) -> bool:
        """Check if user has specific permission"""
        try:
            with self._lock:
                if user_id not in self.user_permissions:
                    return False
                
                user_perms = self.user_permissions[user_id]
                
                # Check if cache is expired
                if user_perms.expires_at and datetime.now() > user_perms.expires_at:
                    self._refresh_user_permissions(user_id)
                
                return permission_id in user_perms.effective_permissions
                
        except Exception as e:
            logger.error(f"❌ Error checking permission {permission_id} for user {user_id}: {str(e)}")
            return False
    
    def has_role(self, user_id: str, role_id: str) -> bool:
        """Check if user has specific role"""
        try:
            with self._lock:
                if user_id not in self.user_permissions:
                    return False
                
                return role_id in self.user_permissions[user_id].roles
                
        except Exception as e:
            logger.error(f"❌ Error checking role {role_id} for user {user_id}: {str(e)}")
            return False
    
    def has_resource_access(self, user_id: str, resource_type: ResourceType, 
                           required_level: PermissionLevel = PermissionLevel.READ) -> bool:
        """Check if user has access to resource type with minimum level"""
        try:
            with self._lock:
                if user_id not in self.user_permissions:
                    return False
                
                user_perms = self.user_permissions[user_id]
                
                for perm_id in user_perms.effective_permissions:
                    if perm_id in self.permissions:
                        perm = self.permissions[perm_id]
                        if (perm.resource_type == resource_type and 
                            perm.level.value >= required_level.value):
                            return True
                
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking resource access for user {user_id}: {str(e)}")
            return False
    
    def get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions"""
        try:
            with self._lock:
                if user_id in self.user_permissions:
                    # Refresh if expired
                    user_perms = self.user_permissions[user_id]
                    if user_perms.expires_at and datetime.now() > user_perms.expires_at:
                        self._refresh_user_permissions(user_id)
                    return user_perms
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting permissions for user {user_id}: {str(e)}")
            return None
    
    def revoke_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Revoke role from user"""
        try:
            with self._lock:
                if user_id not in self.user_permissions:
                    return False
                
                self.user_permissions[user_id].roles.discard(role_id)
                self._refresh_user_permissions(user_id)
                
                logger.info(f"✅ Revoked role {role_id} from user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error revoking role {role_id} from user {user_id}: {str(e)}")
            return False
    
    def revoke_permission_from_user(self, user_id: str, permission_id: str) -> bool:
        """Revoke direct permission from user"""
        try:
            with self._lock:
                if user_id not in self.user_permissions:
                    return False
                
                self.user_permissions[user_id].direct_permissions.discard(permission_id)
                self._refresh_user_permissions(user_id)
                
                logger.info(f"✅ Revoked permission {permission_id} from user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error revoking permission {permission_id} from user {user_id}: {str(e)}")
            return False
    
    def get_all_permissions(self) -> Dict[str, Permission]:
        """Get all permissions"""
        return self.permissions.copy()
    
    def get_all_roles(self) -> Dict[str, Role]:
        """Get all roles"""
        return self.roles.copy()
    
    def cleanup_expired_permissions(self):
        """Clean up expired permission caches"""
        try:
            with self._lock:
                now = datetime.now()
                expired_users = []
                
                for user_id, user_perms in self.user_permissions.items():
                    if user_perms.expires_at and now > user_perms.expires_at:
                        expired_users.append(user_id)
                
                for user_id in expired_users:
                    self._refresh_user_permissions(user_id)
                
                if expired_users:
                    logger.info(f"🧹 Refreshed permissions for {len(expired_users)} users")
                    
        except Exception as e:
            logger.error(f"❌ Error cleaning up expired permissions: {str(e)}")

# Create global instance
permission_handler = PermissionHandler()

# Export main classes and instance
__all__ = [
    'PermissionHandler',
    'Permission',
    'Role', 
    'UserPermissions',
    'PermissionLevel',
    'ResourceType',
    'permission_handler'
]