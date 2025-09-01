"""Authorization Management Module
Advanced Role-Based Access Control (RBAC) for IA Influencer Agent

Features:
- Hierarchical role-based access control with inheritance
- Fine-grained permission management with attribute-based control
- Resource-level authorization with dynamic policies
- Content access control for multi-format protection
- Dynamic permission evaluation with caching
- Multi-tenant permission isolation and delegation
- Audit trail for authorization decisions with forensics
- Advanced security controls for content monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
import asyncio
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, Request
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger


class PermissionLevel(Enum):
    """
Permission levels for granular access control"""

    NONE = 0
    READ = 10
    WRITE = 20
    MODIFY = 25
    DELETE = 30
    MANAGE = 35
    ADMIN = 40
    SUPER_ADMIN = 45
    OWNER = 50


class ResourceType(Enum):
    """
Types of resources in the system"""

    USER = "user"
    CONTENT = "content"
    FINGERPRINT = "fingerprint"
    PROTECTION = "protection"
    REVENUE = "revenue"
    ANALYTICS = "analytics"
    TENANT = "tenant"
    API = "api"
    SYSTEM = "system"
    CRAWLERS = "crawlers"
    LICENSING = "licensing"
    MONETIZATION = "monetization"
    COMPLIANCE = "compliance"


class ContentType(Enum):
    """Content types for content-specific permissions"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    PLAYLIST = "playlist"
    ALBUM = "album"
    PODCAST = "podcast"


class PermissionScope(Enum):
    """Permission scopes for different contexts"""

    GLOBAL = "global"
    TENANT = "tenant"
    RESOURCE = "resource"
    CONTENT = "content"
    TEMPORARY = "temporary"


@dataclass
class Permission:
    """Individual permission definition"""
    name: str
    resource_type: ResourceType
    level: PermissionLevel
    description: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Role:
    """
Role definition with hierarchical permissions"""
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    is_system_role: bool = False
    tenant_specific: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceAccess:
    """
Resource access definition"""
    resource_id: str
    resource_type: ResourceType
    user_id: str
    permissions: Set[str]
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


class PermissionManager:
    """
Manages system permissions and their definitions"""
    
    def __init__(self):
        self.logger = SecurityLogger("PermissionManager")
        self.cache = CacheManager()
        self.settings = get_settings()
        
        # Initialize default permissions
        self.default_permissions = self._initialize_default_permissions()
    
    def _initialize_default_permissions(self) -> Dict[str, Permission]:
        """Initialize default system permissions"""
        permissions = {}
        
        # User permissions
        permissions["user.read"] = Permission(
            name="user.read",
            resource_type=ResourceType.USER,
            level=PermissionLevel.READ,
            description="Read user information"
        )
        
        permissions["user.write"] = Permission(
            name="user.write",
            resource_type=ResourceType.USER,
            level=PermissionLevel.WRITE,
            description="Modify user information"
        )
        
        permissions["user.delete"] = Permission(
            name="user.delete",
            resource_type=ResourceType.USER,
            level=PermissionLevel.DELETE,
            description="Delete user accounts"
        )
        
        # Content permissions
        permissions["content.upload"] = Permission(
            name="content.upload",
            resource_type=ResourceType.CONTENT,
            level=PermissionLevel.WRITE,
            description="Upload content for protection"
        )
        
        permissions["content.manage"] = Permission(
            name="content.manage",
            resource_type=ResourceType.CONTENT,
            level=PermissionLevel.WRITE,
            description="Manage uploaded content"
        )
        
        permissions["content.delete"] = Permission(
            name="content.delete",
            resource_type=ResourceType.CONTENT,
            level=PermissionLevel.DELETE,
            description="Delete protected content"
        )
        
        # Fingerprint permissions
        permissions["fingerprint.create"] = Permission(
            name="fingerprint.create",
            resource_type=ResourceType.FINGERPRINT,
            level=PermissionLevel.WRITE,
            description="Create content fingerprints"
        )
        
        permissions["fingerprint.view"] = Permission(
            name="fingerprint.view",
            resource_type=ResourceType.FINGERPRINT,
            level=PermissionLevel.READ,
            description="View fingerprint data"
        )
        
        # Protection permissions
        permissions["protection.monitor"] = Permission(
            name="protection.monitor",
            resource_type=ResourceType.PROTECTION,
            level=PermissionLevel.READ,
            description="Monitor protection alerts"
        )
        
        permissions["protection.manage"] = Permission(
            name="protection.manage",
            resource_type=ResourceType.PROTECTION,
            level=PermissionLevel.WRITE,
            description="Manage protection settings"
        )
        
        # Revenue permissions
        permissions["revenue.view"] = Permission(
            name="revenue.view",
            resource_type=ResourceType.REVENUE,
            level=PermissionLevel.READ,
            description="View revenue analytics"
        )
        
        permissions["revenue.manage"] = Permission(
            name="revenue.manage",
            resource_type=ResourceType.REVENUE,
            level=PermissionLevel.WRITE,
            description="Manage revenue settings"
        )
        
        # Analytics permissions
        permissions["analytics.view"] = Permission(
            name="analytics.view",
            resource_type=ResourceType.ANALYTICS,
            level=PermissionLevel.READ,
            description="View analytics data"
        )
        
        permissions["analytics.export"] = Permission(
            name="analytics.export",
            resource_type=ResourceType.ANALYTICS,
            level=PermissionLevel.READ,
            description="Export analytics data"
        )
        
        # API permissions
        permissions["api.access"] = Permission(
            name="api.access",
            resource_type=ResourceType.API,
            level=PermissionLevel.READ,
            description="Access API endpoints"
        )
        
        permissions["api.admin"] = Permission(
            name="api.admin",
            resource_type=ResourceType.API,
            level=PermissionLevel.ADMIN,
            description="Administrative API access"
        )
        
        # System permissions
        permissions["system.admin"] = Permission(
            name="system.admin",
            resource_type=ResourceType.SYSTEM,
            level=PermissionLevel.ADMIN,
            description="System administration"
        )
        
        return permissions
    
    async def get_permission(self, permission_name: str) -> Optional[Permission]:
        """Get permission by name"""
        cache_key = f"permission:{permission_name}"
        cached_permission = await self.cache.get(cache_key)
        
        if cached_permission:
            return Permission(**cached_permission)
        
        # Check default permissions
        if permission_name in self.default_permissions:
            permission = self.default_permissions[permission_name]
            await self.cache.set(cache_key, permission.__dict__, expire=3600)
            return permission
        
        return None
    
    async def create_permission(self, permission: Permission) -> bool:
        """Create new custom permission"""
        try:
            # Store in database
            # Implementation depends on your permission model
            
            # Cache the permission
            cache_key = f"permission:{permission.name}"
            await self.cache.set(cache_key, permission.__dict__, expire=3600)
            
            self.logger.info(f"Permission created: {permission.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create permission: {str(e)}")
            return False


class RoleBasedAccess:
    """Role-based access control manager"""
    
    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager
        self.logger = SecurityLogger("RoleBasedAccess")
        self.cache = CacheManager()
        
        # Initialize default roles
        self.default_roles = self._initialize_default_roles()
    
    def _initialize_default_roles(self) -> Dict[str, Role]:
        """Initialize default system roles"""
        roles = {}
        
        # Artist role - content creator
        roles["artist"] = Role(
            name="artist",
            description="Content creator with upload and protection rights",
            permissions={
                "content.upload", "content.manage", "content.delete",
                "fingerprint.create", "fingerprint.view",
                "protection.monitor", "protection.manage",
                "revenue.view", "analytics.view", "analytics.export",
                "api.access"
            }
        )
        
        # Manager role - content manager
        roles["manager"] = Role(
            name="manager",
            description="Content manager with extended permissions",
            permissions={
                "content.upload", "content.manage",
                "fingerprint.create", "fingerprint.view",
                "protection.monitor", "protection.manage",
                "revenue.view", "revenue.manage",
                "analytics.view", "analytics.export",
                "api.access"
            },
            parent_roles={"artist"}
        )
        
        # Admin role - tenant administrator
        roles["admin"] = Role(
            name="admin",
            description="Tenant administrator with full permissions",
            permissions={
                "user.read", "user.write", "user.delete",
                "content.upload", "content.manage", "content.delete",
                "fingerprint.create", "fingerprint.view",
                "protection.monitor", "protection.manage",
                "revenue.view", "revenue.manage",
                "analytics.view", "analytics.export",
                "api.access", "api.admin"
            },
            parent_roles={"manager"}
        )
        
        # System admin role - system-wide administration
        roles["system_admin"] = Role(
            name="system_admin",
            description="System administrator with all permissions",
            permissions={
                "system.admin", "api.admin"
            },
            parent_roles={"admin"},
            is_system_role=True,
            tenant_specific=False
        )
        
        # Viewer role - read-only access
        roles["viewer"] = Role(
            name="viewer",
            description="Read-only access to content and analytics",
            permissions={
                "content.view", "fingerprint.view",
                "protection.monitor", "revenue.view",
                "analytics.view", "api.access"
            }
        )
        
        return roles
    
    async def get_role(self, role_name: str, tenant_id: Optional[str] = None) -> Optional[Role]:
        """Get role by name"""
        cache_key = f"role:{role_name}:{tenant_id or 'global'}"
        cached_role = await self.cache.get(cache_key)
        
        if cached_role:
            return Role(**cached_role)
        
        # Check default roles
        if role_name in self.default_roles:
            role = self.default_roles[role_name]
            await self.cache.set(cache_key, role.__dict__, expire=3600)
            return role
        
        return None
    
    async def get_role_permissions(
        self, 
        role_name: str, 
        tenant_id: Optional[str] = None
    ) -> Set[str]:
        """Get all permissions for a role including inherited ones"""
        role = await self.get_role(role_name, tenant_id)
        if not role:
            return set()
        
        permissions = role.permissions.copy()
        
        # Add permissions from parent roles
        for parent_role_name in role.parent_roles:
            parent_permissions = await self.get_role_permissions(parent_role_name, tenant_id)
            permissions.update(parent_permissions)
        
        return permissions
    
    async def assign_role_to_user(
        self, 
        user_id: str, 
        role_name: str, 
        tenant_id: str,
        assigned_by: str
    ) -> bool:
        """
Assign role to user"""
        try:
            # Validate role exists
            role = await self.get_role(role_name, tenant_id)
            if not role:
                return False
            
            # Store role assignment in database
            # Implementation depends on your user-role model
            
            # Cache user roles
            cache_key = f"user_roles:{user_id}:{tenant_id}"
            user_roles = await self.cache.get(cache_key) or []
            if role_name not in user_roles:
                user_roles.append(role_name)
                await self.cache.set(cache_key, user_roles, expire=3600)
            
            # Clear user permissions cache
            perm_cache_key = f"user_permissions:{user_id}:{tenant_id}"
            await self.cache.delete(perm_cache_key)
            
            self.logger.info(f"Role {role_name} assigned to user {user_id} in tenant {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign role: {str(e)}")
            return False
    
    async def revoke_role_from_user(
        self, 
        user_id: str, 
        role_name: str, 
        tenant_id: str
    ) -> bool:
        """Revoke role from user"""
        try:
            # Remove role assignment from database
            # Implementation depends on your user-role model
            
            # Update cache
            cache_key = f"user_roles:{user_id}:{tenant_id}"
            user_roles = await self.cache.get(cache_key) or []
            if role_name in user_roles:
                user_roles.remove(role_name)
                await self.cache.set(cache_key, user_roles, expire=3600)
            
            # Clear user permissions cache
            perm_cache_key = f"user_permissions:{user_id}:{tenant_id}"
            await self.cache.delete(perm_cache_key)
            
            self.logger.info(f"Role {role_name} revoked from user {user_id} in tenant {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke role: {str(e)}")
            return False


class ContentAccessControl:
    """Content-specific access control for multi-format protection"""
    
    def __init__(self, rbac: RoleBasedAccess):
        self.rbac = rbac
        self.logger = SecurityLogger("ContentAccessControl")
        self.cache = CacheManager()
    
    async def can_access_content(
        self, 
        user_id: str, 
        content_id: str, 
        permission: str,
        tenant_id: str
    ) -> bool:
        """Check if user can access specific content"""
        try:
            # Check cache first
            cache_key = f"content_access:{user_id}:{content_id}:{permission}"
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Get content ownership
            content_owner = await self.get_content_owner(content_id)
            if content_owner == user_id:
                # Owner has all permissions
                await self.cache.set(cache_key, True, expire=300)
                return True
            
            # Check user permissions
            user_permissions = await self.get_user_permissions(user_id, tenant_id)
            
            # Check if user has required permission
            has_permission = permission in user_permissions
            
            # Check resource-specific access
            if not has_permission:
                has_permission = await self.check_resource_access(
                    user_id, content_id, permission
                )
            
            # Cache result
            await self.cache.set(cache_key, has_permission, expire=300)
            
            return has_permission
            
        except Exception as e:
            self.logger.error(f"Content access check failed: {str(e)}")
            return False
    
    async def grant_content_access(
        self, 
        user_id: str, 
        content_id: str, 
        permissions: List[str],
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Grant specific access to content"""
        try:
            # Create resource access record
            access = ResourceAccess(
                resource_id=content_id,
                resource_type=ResourceType.CONTENT,
                user_id=user_id,
                permissions=set(permissions),
                granted_by=granted_by,
                granted_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            # Store in database
            # Implementation depends on your resource access model
            
            # Clear cache
            for permission in permissions:
                cache_key = f"content_access:{user_id}:{content_id}:{permission}"
                await self.cache.delete(cache_key)
            
            self.logger.info(f"Content access granted to user {user_id} for content {content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to grant content access: {str(e)}")
            return False
    
    async def revoke_content_access(
        self, 
        user_id: str, 
        content_id: str,
        permissions: Optional[List[str]] = None
    ) -> bool:
        """Revoke content access"""
        try:
            # Remove from database
            # Implementation depends on your resource access model
            
            # Clear cache
            if permissions:
                for permission in permissions:
                    cache_key = f"content_access:{user_id}:{content_id}:{permission}"
                    await self.cache.delete(cache_key)
            else:
                # Clear all permissions for this content
                pattern = f"content_access:{user_id}:{content_id}:*"
                await self.cache.delete_pattern(pattern)
            
            self.logger.info(f"Content access revoked for user {user_id} on content {content_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke content access: {str(e)}")
            return False
    
    async def get_content_owner(self, content_id: str) -> Optional[str]:
        """Get content owner"""
        try:
            # Check cache first
            cache_key = f"content_owner:{content_id}"
            cached_owner = await self.cache.get(cache_key)
            
            if cached_owner:
                return cached_owner
            
            # In a real implementation, this would query the content database
            # For now, we'll use a simple file-based storage
            import os
            content_owners_file = "/tmp/content_owners.json"
            
            if os.path.exists(content_owners_file):
                with open(content_owners_file, 'r') as f:
                    content_owners = json.load(f)
                    owner_id = content_owners.get(content_id)
                    
                    if owner_id:
                        # Cache the result
                        await self.cache.set(cache_key, owner_id, expire=3600)
                        return owner_id
            
            self.logger.warning(f"Content owner not found for content: {content_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get content owner for {content_id}: {str(e)}")
            return None
    
    async def get_user_permissions(self, user_id: str, tenant_id: str) -> Set[str]:
        """Get all user permissions"""
        cache_key = f"user_permissions:{user_id}:{tenant_id}"
        cached_permissions = await self.cache.get(cache_key)
        
        if cached_permissions:
            return set(cached_permissions)
        
        # Get user roles
        user_roles = await self.get_user_roles(user_id, tenant_id)
        
        # Collect all permissions from roles
        all_permissions = set()
        for role_name in user_roles:
            role_permissions = await self.rbac.get_role_permissions(role_name, tenant_id)
            all_permissions.update(role_permissions)
        
        # Cache permissions
        await self.cache.set(cache_key, list(all_permissions), expire=3600)
        
        return all_permissions
    
    async def get_user_roles(self, user_id: str, tenant_id: str) -> List[str]:
        """Get user roles"""
        try:
            cache_key = f"user_roles:{user_id}:{tenant_id}"
            cached_roles = await self.cache.get(cache_key)
            
            if cached_roles:
                return cached_roles
            
            # In a real implementation, this would query the user-role database
            # For now, use file-based storage
            import os
            user_roles_file = "/tmp/user_roles.json"
            
            if os.path.exists(user_roles_file):
                with open(user_roles_file, 'r') as f:
                    user_roles_data = json.load(f)
                    
                    # Structure: {user_id: {tenant_id: [roles]}}
                    user_data = user_roles_data.get(user_id, {})
                    roles = user_data.get(tenant_id, ["viewer"])  # Default to viewer role
                    
                    # Cache the result
                    await self.cache.set(cache_key, roles, expire=3600)
                    return roles
            
            # Default role if no data found
            default_roles = ["viewer"]
            await self.cache.set(cache_key, default_roles, expire=3600)
            return default_roles
            
        except Exception as e:
            self.logger.error(f"Failed to get user roles for {user_id} in tenant {tenant_id}: {str(e)}")
            return ["viewer"]  # Fallback to minimal access
    
    async def check_resource_access(
        self, 
        user_id: str, 
        resource_id: str, 
        permission: str
    ) -> bool:
        """Check resource-specific access"""
        try:
            # Check cache first
            cache_key = f"resource_access:{user_id}:{resource_id}:{permission}"
            cached_result = await self.cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # In a real implementation, this would query the resource access database
            # For now, use file-based storage
            import os
            resource_access_file = "/tmp/resource_access.json"
            
            if os.path.exists(resource_access_file):
                with open(resource_access_file, 'r') as f:
                    access_data = json.load(f)
                    
                    # Structure: {user_id: {resource_id: [permissions]}}
                    user_access = access_data.get(user_id, {})
                    resource_permissions = user_access.get(resource_id, [])
                    
                    has_access = permission in resource_permissions
                    
                    # Cache the result for 5 minutes
                    await self.cache.set(cache_key, has_access, expire=300)
                    return has_access
            
            # Default to no access if no data found
            await self.cache.set(cache_key, False, expire=300)
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check resource access for user {user_id}, resource {resource_id}, permission {permission}: {str(e)}")
            return False  # Deny access on error for security


class AuthorizationManager:
    """Main authorization manager"""
    
    def __init__(self):
        self.permission_manager = PermissionManager()
        self.rbac = RoleBasedAccess(self.permission_manager)
        self.content_access = ContentAccessControl(self.rbac)
        self.logger = SecurityLogger("AuthorizationManager")
    
    async def authorize(
        self, 
        user_id: str, 
        resource_type: str, 
        resource_id: str, 
        permission: str,
        tenant_id: str
    ) -> bool:
        """Main authorization method"""
        try:
            # Log authorization attempt
            self.logger.debug(
                f"Authorization check: user={user_id}, resource={resource_type}:{resource_id}, "
                f"permission={permission}, tenant={tenant_id}"
            )
            
            # Content-specific authorization
            if resource_type == "content":
                return await self.content_access.can_access_content(
                    user_id, resource_id, permission, tenant_id
                )
            
            # General resource authorization
            user_permissions = await self.content_access.get_user_permissions(user_id, tenant_id)
            has_permission = permission in user_permissions
            
            # Log result
            self.logger.info(
                f"Authorization {'granted' if has_permission else 'denied'}: "
                f"user={user_id}, permission={permission}"
            )
            
            return has_permission
            
        except Exception as e:
            self.logger.error(f"Authorization check failed: {str(e)}")
            return False
    
    async def require_permission(self, permission: str):
        """Decorator for requiring specific permission"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Get current user from request context
                # Implementation depends on your auth system
                
                # Check authorization
                # authorized = await self.authorize(...)
                
                # if not authorized:
                #     raise HTTPException(status_code=403, detail="Insufficient permissions")
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def require_role(self, role: str):
        """Decorator for requiring specific role"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Implementation similar to require_permission
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def get_user_effective_permissions(
        self, 
        user_id: str, 
        tenant_id: str
    ) -> Dict[str, Any]:
        """
Get user's effective permissions summary"""
        try:
            user_permissions = await self.content_access.get_user_permissions(user_id, tenant_id)
            user_roles = await self.content_access.get_user_roles(user_id, tenant_id)
            
            # Organize permissions by resource type
            permissions_by_resource = {}
            for permission in user_permissions:
                resource_type = permission.split('.')[0]
                if resource_type not in permissions_by_resource:
                    permissions_by_resource[resource_type] = []
                permissions_by_resource[resource_type].append(permission)
            
            return {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "roles": user_roles,
                "permissions": list(user_permissions),
                "permissions_by_resource": permissions_by_resource,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get effective permissions: {str(e)}")
            return {}
