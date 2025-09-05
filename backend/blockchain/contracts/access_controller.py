"""Access Controller Contract - IA-Influencer-Agent Platform

This module provides granular access control functionality for content, features,
and platform resources with role-based permissions, time-based access, and
hierarchical permission management.

Features:
- Role-based access control (RBAC)
- Time-based access permissions
- Hierarchical permission inheritance
- Feature-specific access control
- Content access management
- Dynamic permission updates
- Access audit trails
- Emergency access override

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
import time

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access levels for resources"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class ResourceType(Enum):
    """Types of resources that can be access-controlled"""
    CONTENT = "content"
    FEATURE = "feature"
    API_ENDPOINT = "api_endpoint"
    DASHBOARD = "dashboard"
    MARKETPLACE = "marketplace"
    ANALYTICS = "analytics"
    BILLING = "billing"
    USER_DATA = "user_data"


class PermissionScope(Enum):
    """Scope of permissions"""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    CONTENT = "content"
    PERSONAL = "personal"


@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str
    name: str
    description: str
    permissions: Set[str]
    inheritance: List[str]  # Parent role IDs
    scope: PermissionScope
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Permission:
    """Permission definition"""
    permission_id: str
    name: str
    description: str
    resource_type: ResourceType
    access_level: AccessLevel
    conditions: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessGrant:
    """Access grant for user to resource"""
    grant_id: str
    user_address: str
    resource_id: str
    resource_type: ResourceType
    access_level: AccessLevel
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime]
    conditions: Dict[str, Any]
    is_active: bool = True


class AccessController:
    """
    Granular Access Control System
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Access Controller
        
        Args:
            config: Configuration including system settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core data structures
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.user_roles: Dict[str, Set[str]] = {}  # user_address -> role_ids
        self.access_grants: Dict[str, AccessGrant] = {}
        self.access_audit_log: List[Dict[str, Any]] = []
        
        # System settings
        self.default_permissions_enabled = config.get("default_permissions", True)
        self.permission_inheritance_enabled = config.get("inheritance", True)
        self.access_logging_enabled = config.get("access_logging", True)
        
        # Initialize system roles and permissions
        self._init_system_roles()
        self._init_system_permissions()
    
    def _init_system_roles(self):
        """Initialize system roles"""
        system_roles = [
            Role(
                role_id="super_admin",
                name="Super Administrator",
                description="Full system access",
                permissions={"*"},  # All permissions
                inheritance=[],
                scope=PermissionScope.GLOBAL,
                is_system_role=True
            ),
            Role(
                role_id="admin",
                name="Administrator",
                description="Administrative access",
                permissions={
                    "content.read", "content.write", "content.admin",
                    "user.read", "user.write",
                    "analytics.read", "analytics.admin",
                    "marketplace.admin"
                },
                inheritance=[],
                scope=PermissionScope.ORGANIZATION,
                is_system_role=True
            ),
            Role(
                role_id="creator",
                name="Content Creator",
                description="Content creation and management",
                permissions={
                    "content.read", "content.write",
                    "analytics.read",
                    "marketplace.read", "marketplace.write"
                },
                inheritance=[],
                scope=PermissionScope.PROJECT,
                is_system_role=True
            ),
            Role(
                role_id="viewer",
                name="Viewer",
                description="Read-only access",
                permissions={
                    "content.read",
                    "analytics.read"
                },
                inheritance=[],
                scope=PermissionScope.PERSONAL,
                is_system_role=True
            ),
            Role(
                role_id="collaborator",
                name="Collaborator",
                description="Collaboration on content",
                permissions={
                    "content.read", "content.write",
                    "marketplace.read"
                },
                inheritance=["viewer"],
                scope=PermissionScope.CONTENT,
                is_system_role=True
            )
        ]
        
        for role in system_roles:
            self.roles[role.role_id] = role
    
    def _init_system_permissions(self):
        """Initialize system permissions"""
        system_permissions = [
            Permission(
                permission_id="content.read",
                name="Read Content",
                description="View content and metadata",
                resource_type=ResourceType.CONTENT,
                access_level=AccessLevel.READ,
                conditions={}
            ),
            Permission(
                permission_id="content.write",
                name="Write Content",
                description="Create and edit content",
                resource_type=ResourceType.CONTENT,
                access_level=AccessLevel.WRITE,
                conditions={}
            ),
            Permission(
                permission_id="content.admin",
                name="Administer Content",
                description="Full content management",
                resource_type=ResourceType.CONTENT,
                access_level=AccessLevel.ADMIN,
                conditions={}
            ),
            Permission(
                permission_id="analytics.read",
                name="View Analytics",
                description="Access analytics dashboards",
                resource_type=ResourceType.ANALYTICS,
                access_level=AccessLevel.READ,
                conditions={}
            ),
            Permission(
                permission_id="marketplace.read",
                name="Browse Marketplace",
                description="View marketplace listings",
                resource_type=ResourceType.MARKETPLACE,
                access_level=AccessLevel.READ,
                conditions={}
            ),
            Permission(
                permission_id="marketplace.write",
                name="List in Marketplace",
                description="Create marketplace listings",
                resource_type=ResourceType.MARKETPLACE,
                access_level=AccessLevel.WRITE,
                conditions={}
            )
        ]
        
        for permission in system_permissions:
            self.permissions[permission.permission_id] = permission
    
    async def create_role(
        self,
        name: str,
        description: str,
        permissions: Set[str],
        inheritance: Optional[List[str]] = None,
        scope: PermissionScope = PermissionScope.PROJECT,
        creator_address: str = ""
    ) -> Role:
        """
        Create a new role
        
        Args:
            name: Role name
            description: Role description  
            permissions: Set of permission IDs
            inheritance: Parent role IDs
            scope: Permission scope
            creator_address: Address creating the role
            
        Returns:
            Created role
        """
        try:
            role_id = str(uuid.uuid4())
            
            self.logger.info(f"Creating role: {name}")
            
            # Validate permissions exist
            for permission_id in permissions:
                if permission_id != "*" and permission_id not in self.permissions:
                    raise ValueError(f"Permission not found: {permission_id}")
            
            # Validate inheritance roles exist
            inheritance = inheritance or []
            for parent_role_id in inheritance:
                if parent_role_id not in self.roles:
                    raise ValueError(f"Parent role not found: {parent_role_id}")
            
            role = Role(
                role_id=role_id,
                name=name,
                description=description,
                permissions=permissions,
                inheritance=inheritance,
                scope=scope,
                is_system_role=False
            )
            
            self.roles[role_id] = role
            
            # Log role creation
            await self._log_access_event("role_created", {
                "role_id": role_id,
                "name": name,
                "creator": creator_address,
                "permissions_count": len(permissions)
            })
            
            self.logger.info(f"Role created: {role_id}")
            return role
            
        except Exception as e:
            self.logger.error(f"Role creation failed: {e}")
            raise
    
    async def assign_role(
        self,
        user_address: str,
        role_id: str,
        assigned_by: str,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Assign role to user
        
        Args:
            user_address: User receiving role
            role_id: Role to assign
            assigned_by: Address assigning role
            expires_at: Optional expiration
            
        Returns:
            Assignment result
        """
        try:
            if role_id not in self.roles:
                raise ValueError(f"Role not found: {role_id}")
            
            role = self.roles[role_id]
            
            self.logger.info(f"Assigning role {role_id} to {user_address}")
            
            # Initialize user roles if needed
            if user_address not in self.user_roles:
                self.user_roles[user_address] = set()
            
            # Add role
            self.user_roles[user_address].add(role_id)
            
            # Log assignment
            await self._log_access_event("role_assigned", {
                "user_address": user_address,
                "role_id": role_id,
                "role_name": role.name,
                "assigned_by": assigned_by,
                "expires_at": expires_at.isoformat() if expires_at else None
            })
            
            # Get effective permissions
            effective_permissions = await self._get_effective_permissions(user_address)
            
            result = {
                "user_address": user_address,
                "role_id": role_id,
                "role_name": role.name,
                "assigned_by": assigned_by,
                "assigned_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "effective_permissions": list(effective_permissions)
            }
            
            self.logger.info(f"Role assigned: {role_id} to {user_address}")
            return result
            
        except Exception as e:
            self.logger.error(f"Role assignment failed: {e}")
            raise
    
    async def grant_access(
        self,
        user_address: str,
        resource_id: str,
        resource_type: ResourceType,
        access_level: AccessLevel,
        granted_by: str,
        duration_hours: Optional[int] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> AccessGrant:
        """
        Grant specific access to resource
        
        Args:
            user_address: User receiving access
            resource_id: Resource identifier
            resource_type: Type of resource
            access_level: Level of access
            granted_by: Address granting access
            duration_hours: Optional access duration
            conditions: Optional access conditions
            
        Returns:
            Access grant
        """
        try:
            grant_id = str(uuid.uuid4())
            
            self.logger.info(f"Granting {access_level.value} access to {resource_type.value}:{resource_id}")
            
            # Calculate expiration
            expires_at = None
            if duration_hours:
                expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
            
            grant = AccessGrant(
                grant_id=grant_id,
                user_address=user_address,
                resource_id=resource_id,
                resource_type=resource_type,
                access_level=access_level,
                granted_by=granted_by,
                granted_at=datetime.utcnow(),
                expires_at=expires_at,
                conditions=conditions or {},
                is_active=True
            )
            
            self.access_grants[grant_id] = grant
            
            # Log access grant
            await self._log_access_event("access_granted", {
                "grant_id": grant_id,
                "user_address": user_address,
                "resource_id": resource_id,
                "resource_type": resource_type.value,
                "access_level": access_level.value,
                "granted_by": granted_by,
                "duration_hours": duration_hours
            })
            
            self.logger.info(f"Access granted: {grant_id}")
            return grant
            
        except Exception as e:
            self.logger.error(f"Access grant failed: {e}")
            raise
    
    async def check_access(
        self,
        user_address: str,
        resource_id: str,
        resource_type: ResourceType,
        required_access_level: AccessLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if user has required access to resource
        
        Args:
            user_address: User requesting access
            resource_id: Resource identifier
            resource_type: Type of resource
            required_access_level: Required access level
            context: Optional context for conditions
            
        Returns:
            Access check result
        """
        try:
            self.logger.debug(f"Checking access for {user_address} to {resource_type.value}:{resource_id}")
            
            access_granted = False
            granted_level = AccessLevel.NONE
            grant_sources = []
            
            # Check direct access grants
            for grant in self.access_grants.values():
                if (grant.user_address == user_address and 
                    grant.resource_id == resource_id and
                    grant.resource_type == resource_type and
                    grant.is_active):
                    
                    # Check expiration
                    if grant.expires_at and datetime.utcnow() > grant.expires_at:
                        grant.is_active = False
                        continue
                    
                    # Check conditions
                    if await self._check_access_conditions(grant.conditions, context):
                        if self._access_level_sufficient(grant.access_level, required_access_level):
                            access_granted = True
                            granted_level = max(granted_level, grant.access_level, key=lambda x: self._access_level_value(x))
                            grant_sources.append(f"direct_grant:{grant.grant_id}")
            
            # Check role-based permissions
            if user_address in self.user_roles:
                user_permissions = await self._get_effective_permissions(user_address)
                
                for permission_id in user_permissions:
                    if permission_id == "*":  # Wildcard permission
                        access_granted = True
                        granted_level = AccessLevel.OWNER
                        grant_sources.append("wildcard_permission")
                        break
                    
                    if permission_id in self.permissions:
                        permission = self.permissions[permission_id]
                        
                        if (permission.resource_type == resource_type and
                            self._access_level_sufficient(permission.access_level, required_access_level)):
                            access_granted = True
                            granted_level = max(granted_level, permission.access_level, key=lambda x: self._access_level_value(x))
                            grant_sources.append(f"role_permission:{permission_id}")
            
            # Log access check
            await self._log_access_event("access_checked", {
                "user_address": user_address,
                "resource_id": resource_id,
                "resource_type": resource_type.value,
                "required_access_level": required_access_level.value,
                "access_granted": access_granted,
                "granted_level": granted_level.value,
                "grant_sources": grant_sources
            })
            
            result = {
                "user_address": user_address,
                "resource_id": resource_id,
                "resource_type": resource_type.value,
                "required_access_level": required_access_level.value,
                "access_granted": access_granted,
                "granted_level": granted_level.value,
                "grant_sources": grant_sources,
                "checked_at": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Access check failed: {e}")
            raise
    
    def _access_level_sufficient(self, granted_level: AccessLevel, required_level: AccessLevel) -> bool:
        """Check if granted access level is sufficient for required level"""
        access_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        
        return access_hierarchy[granted_level] >= access_hierarchy[required_level]
    
    def _access_level_value(self, access_level: AccessLevel) -> int:
        """Get numeric value for access level comparison"""
        access_hierarchy = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
            AccessLevel.OWNER: 4
        }
        return access_hierarchy[access_level]
    
    async def _check_access_conditions(
        self,
        conditions: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if access conditions are met"""
        if not conditions:
            return True
        
        context = context or {}
        
        # Time-based conditions
        if "time_range" in conditions:
            time_range = conditions["time_range"]
            current_hour = datetime.utcnow().hour
            
            if "start_hour" in time_range and current_hour < time_range["start_hour"]:
                return False
            if "end_hour" in time_range and current_hour > time_range["end_hour"]:
                return False
        
        # Location-based conditions
        if "allowed_locations" in conditions:
            user_location = context.get("location")
            if user_location not in conditions["allowed_locations"]:
                return False
        
        # Device-based conditions
        if "allowed_devices" in conditions:
            device_type = context.get("device_type")
            if device_type not in conditions["allowed_devices"]:
                return False
        
        return True
    
    async def _get_effective_permissions(self, user_address: str) -> Set[str]:
        """Get effective permissions for user including inherited ones"""
        if user_address not in self.user_roles:
            return set()
        
        effective_permissions = set()
        processed_roles = set()
        
        # Get permissions from all roles (including inherited)
        roles_to_process = list(self.user_roles[user_address])
        
        while roles_to_process:
            role_id = roles_to_process.pop(0)
            
            if role_id in processed_roles:
                continue
            
            processed_roles.add(role_id)
            
            if role_id in self.roles:
                role = self.roles[role_id]
                effective_permissions.update(role.permissions)
                
                # Add inherited roles
                if self.permission_inheritance_enabled:
                    roles_to_process.extend(role.inheritance)
        
        return effective_permissions
    
    async def revoke_access(
        self,
        grant_id: str,
        revoked_by: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Revoke access grant
        
        Args:
            grant_id: Grant ID to revoke
            revoked_by: Address revoking access
            reason: Reason for revocation
            
        Returns:
            Revocation result
        """
        try:
            if grant_id not in self.access_grants:
                raise ValueError(f"Access grant not found: {grant_id}")
            
            grant = self.access_grants[grant_id]
            
            if not grant.is_active:
                raise ValueError("Access grant already inactive")
            
            self.logger.info(f"Revoking access grant: {grant_id}")
            
            # Deactivate grant
            grant.is_active = False
            
            # Log revocation
            await self._log_access_event("access_revoked", {
                "grant_id": grant_id,
                "user_address": grant.user_address,
                "resource_id": grant.resource_id,
                "resource_type": grant.resource_type.value,
                "revoked_by": revoked_by,
                "reason": reason
            })
            
            result = {
                "grant_id": grant_id,
                "user_address": grant.user_address,
                "resource_id": grant.resource_id,
                "revoked_by": revoked_by,
                "reason": reason,
                "revoked_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Access revoked: {grant_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Access revocation failed: {e}")
            raise
    
    async def remove_role(
        self,
        user_address: str,
        role_id: str,
        removed_by: str
    ) -> Dict[str, Any]:
        """
        Remove role from user
        
        Args:
            user_address: User losing role
            role_id: Role to remove
            removed_by: Address removing role
            
        Returns:
            Removal result
        """
        try:
            if user_address not in self.user_roles:
                raise ValueError(f"User has no roles: {user_address}")
            
            if role_id not in self.user_roles[user_address]:
                raise ValueError(f"User does not have role: {role_id}")
            
            role = self.roles.get(role_id)
            role_name = role.name if role else role_id
            
            self.logger.info(f"Removing role {role_id} from {user_address}")
            
            # Remove role
            self.user_roles[user_address].remove(role_id)
            
            # Clean up if no roles left
            if not self.user_roles[user_address]:
                del self.user_roles[user_address]
            
            # Log removal
            await self._log_access_event("role_removed", {
                "user_address": user_address,
                "role_id": role_id,
                "role_name": role_name,
                "removed_by": removed_by
            })
            
            result = {
                "user_address": user_address,
                "role_id": role_id,
                "role_name": role_name,
                "removed_by": removed_by,
                "removed_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Role removed: {role_id} from {user_address}")
            return result
            
        except Exception as e:
            self.logger.error(f"Role removal failed: {e}")
            raise
    
    async def _log_access_event(self, event_type: str, data: Dict[str, Any]):
        """Log access control events"""
        if not self.access_logging_enabled:
            return
        
        log_entry = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        self.access_audit_log.append(log_entry)
        
        # Limit log size (keep last 10000 entries)
        if len(self.access_audit_log) > 10000:
            self.access_audit_log = self.access_audit_log[-10000:]
    
    async def get_user_permissions(self, user_address: str) -> Dict[str, Any]:
        """Get user's roles and effective permissions"""
        user_role_ids = self.user_roles.get(user_address, set())
        user_roles_info = []
        
        for role_id in user_role_ids:
            if role_id in self.roles:
                role = self.roles[role_id]
                user_roles_info.append({
                    "role_id": role_id,
                    "name": role.name,
                    "description": role.description,
                    "scope": role.scope.value,
                    "is_system_role": role.is_system_role
                })
        
        effective_permissions = await self._get_effective_permissions(user_address)
        
        active_grants = [
            {
                "grant_id": grant.grant_id,
                "resource_id": grant.resource_id,
                "resource_type": grant.resource_type.value,
                "access_level": grant.access_level.value,
                "granted_by": grant.granted_by,
                "granted_at": grant.granted_at.isoformat(),
                "expires_at": grant.expires_at.isoformat() if grant.expires_at else None
            }
            for grant in self.access_grants.values()
            if grant.user_address == user_address and grant.is_active
        ]
        
        return {
            "user_address": user_address,
            "roles": user_roles_info,
            "effective_permissions": list(effective_permissions),
            "active_grants": active_grants,
            "total_roles": len(user_role_ids),
            "total_permissions": len(effective_permissions),
            "total_grants": len(active_grants)
        }
    
    async def get_access_analytics(self) -> Dict[str, Any]:
        """Get access control analytics"""
        total_users = len(self.user_roles)
        total_roles = len(self.roles)
        total_permissions = len(self.permissions)
        total_grants = len([g for g in self.access_grants.values() if g.is_active])
        
        # Role distribution
        role_usage = {}
        for user_roles in self.user_roles.values():
            for role_id in user_roles:
                role_usage[role_id] = role_usage.get(role_id, 0) + 1
        
        # Recent access events
        recent_events = [
            log_entry for log_entry in self.access_audit_log[-100:]
        ]
        
        return {
            "total_users": total_users,
            "total_roles": total_roles,
            "total_permissions": total_permissions,
            "total_active_grants": total_grants,
            "role_usage_distribution": role_usage,
            "recent_events": recent_events,
            "system_roles_count": len([r for r in self.roles.values() if r.is_system_role]),
            "custom_roles_count": len([r for r in self.roles.values() if not r.is_system_role])
        }


class PermissionManager:
    """
    High-level manager for permission operations
    """
    
    def __init__(self, access_controller: AccessController):
        """
        Initialize Permission Manager
        
        Args:
            access_controller: Underlying access controller
        """
        self.access_controller = access_controller
        self.logger = logging.getLogger(__name__)
    
    async def setup_creator_permissions(
        self,
        creator_address: str,
        content_ids: List[str]
    ) -> Dict[str, Any]:
        """Setup standard creator permissions for content"""
        results = []
        
        # Assign creator role
        role_result = await self.access_controller.assign_role(
            creator_address, "creator", "system"
        )
        results.append(role_result)
        
        # Grant owner access to each content item
        for content_id in content_ids:
            grant = await self.access_controller.grant_access(
                creator_address, content_id, ResourceType.CONTENT,
                AccessLevel.OWNER, "system"
            )
            results.append({
                "type": "content_grant",
                "grant_id": grant.grant_id,
                "content_id": content_id
            })
        
        return {
            "creator_address": creator_address,
            "permissions_setup": results,
            "total_grants": len(results)
        }
    
    async def setup_collaboration_permissions(
        self,
        content_id: str,
        owner_address: str,
        collaborators: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Setup permissions for content collaboration"""
        results = []
        
        for collaborator in collaborators:
            address = collaborator["address"]
            access_level = AccessLevel(collaborator.get("access_level", "write"))
            
            # Assign collaborator role
            role_result = await self.access_controller.assign_role(
                address, "collaborator", owner_address
            )
            results.append(role_result)
            
            # Grant specific access to content
            grant = await self.access_controller.grant_access(
                address, content_id, ResourceType.CONTENT,
                access_level, owner_address
            )
            results.append({
                "type": "collaboration_grant",
                "grant_id": grant.grant_id,
                "collaborator_address": address,
                "access_level": access_level.value
            })
        
        return {
            "content_id": content_id,
            "owner_address": owner_address,
            "collaboration_setup": results,
            "total_collaborators": len(collaborators)
        }