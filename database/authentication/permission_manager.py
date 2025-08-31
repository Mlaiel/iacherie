"""🔐 Permission Manager - Enterprise Role-Based Access Control System
===================================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Type: Production-Ready RBAC Permission Management
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING: Unauthorized use strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Business Logic: Role Definition → Permission Assignment → Access Control → 
Resource Protection → Audit Logging → Dynamic Permissions
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from uuid import UUID, uuid4
import json

from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()

class ResourceType(Enum):
    """Resource types for permission management"""    CONTENT = "content"
    PROFILE = "profile"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    PLATFORM = "platform"
    ADMIN = "admin"
    API = "api"
    FINGERPRINT = "fingerprint"
    PROTECTION = "protection"

class ActionType(Enum):
    """Action types for permissions"""    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    APPROVE = "approve"
    PUBLISH = "publish"
    SHARE = "share"
    DOWNLOAD = "download"

class RoleType(Enum):
    """Predefined role types"""    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CREATOR = "creator"
    PREMIUM_CREATOR = "premium_creator"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"
    API_USER = "api_user"
    GUEST = "guest"

class PermissionScope(Enum):
    """Permission scope levels"""    GLOBAL = "global"
    TENANT = "tenant"
    PROJECT = "project"
    PERSONAL = "personal"
    SHARED = "shared"

@dataclass
class Permission:
    """Permission structure"""    resource: ResourceType
    action: ActionType
    scope: PermissionScope = PermissionScope.PERSONAL
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    def to_string(self) -> str:
        """Convert permission to string format"""        return f"{self.resource.value}:{self.action.value}:{self.scope.value}"

@dataclass
class AccessContext:
    """Access context for permission evaluation"""    user_id: str
    resource_id: Optional[str] = None
    resource_owner_id: Optional[str] = None
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Roles(Base):
    """Database model for roles"""    __tablename__ = 'roles'
    
    role_id = Column(String, primary_key=True)
    role_name = Column(String, nullable=False, unique=True)
    role_type = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String, nullable=True)
    role_metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_roles_type', 'role_type'),
        Index('idx_roles_active', 'is_active'),
    )

class Permissions(Base):
    """Database model for permissions"""    __tablename__ = 'permissions'
    
    permission_id = Column(String, primary_key=True)
    permission_name = Column(String, nullable=False, unique=True)
    resource_type = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    scope_type = Column(String, nullable=False, default=PermissionScope.PERSONAL.value)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_system_permission = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    conditions = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    permission_metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_permissions_resource_action', 'resource_type', 'action_type'),
        Index('idx_permissions_scope', 'scope_type'),
    )

class RolePermissions(Base):
    """Database model for role-permission assignments"""    __tablename__ = 'role_permissions'
    
    assignment_id = Column(String, primary_key=True)
    role_id = Column(String, nullable=False, index=True)
    permission_id = Column(String, nullable=False, index=True)
    granted_by = Column(String, nullable=True)
    granted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    conditions = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index('idx_role_permissions_role', 'role_id', 'is_active'),
        Index('idx_role_permissions_expires', 'expires_at'),
    )

class UserRoles(Base):
    """Database model for user-role assignments"""    __tablename__ = 'user_roles'
    
    assignment_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    role_id = Column(String, nullable=False, index=True)
    tenant_id = Column(String, nullable=True, index=True)
    project_id = Column(String, nullable=True, index=True)
    assigned_by = Column(String, nullable=True)
    assigned_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    assignment_metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_user_roles_user', 'user_id', 'is_active'),
        Index('idx_user_roles_tenant', 'tenant_id', 'user_id'),
        Index('idx_user_roles_expires', 'expires_at'),
    )

class UserPermissions(Base):
    """Database model for direct user permissions"""    __tablename__ = 'user_permissions'
    
    assignment_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    permission_id = Column(String, nullable=False, index=True)
    resource_id = Column(String, nullable=True, index=True)
    tenant_id = Column(String, nullable=True, index=True)
    granted_by = Column(String, nullable=True)
    granted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    conditions = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    __table_args__ = (
        Index('idx_user_permissions_user', 'user_id', 'is_active'),
        Index('idx_user_permissions_resource', 'resource_id', 'user_id'),
        Index('idx_user_permissions_expires', 'expires_at'),
    )

class PermissionAuditLog(Base):
    """Database model for permission audit logging"""    __tablename__ = 'permission_audit_log'
    
    audit_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # check, grant, revoke, etc.
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    permission_checked = Column(String, nullable=True)
    access_granted = Column(Boolean, nullable=True)
    reason = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    request_context = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_permission_audit_user_date', 'user_id', 'created_at'),
        Index('idx_permission_audit_resource', 'resource_type', 'resource_id'),
    )

class PermissionManager:
    """    Enterprise-grade permission management system with RBAC support.
    
    Features:
    - Role-based access control (RBAC)
    - Fine-grained permissions
    - Resource-level access control
    - Dynamic permission evaluation
    - Tenant and project isolation
    - Comprehensive audit logging
    - Conditional permissions
    """    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        # Default system permissions
        self.system_permissions = [
            # Content permissions
            Permission(ResourceType.CONTENT, ActionType.CREATE, PermissionScope.PERSONAL),
            Permission(ResourceType.CONTENT, ActionType.READ, PermissionScope.PERSONAL),
            Permission(ResourceType.CONTENT, ActionType.UPDATE, PermissionScope.PERSONAL),
            Permission(ResourceType.CONTENT, ActionType.DELETE, PermissionScope.PERSONAL),
            Permission(ResourceType.CONTENT, ActionType.PUBLISH, PermissionScope.PERSONAL),
            Permission(ResourceType.CONTENT, ActionType.SHARE, PermissionScope.PERSONAL),
            
            # Profile permissions
            Permission(ResourceType.PROFILE, ActionType.READ, PermissionScope.PERSONAL),
            Permission(ResourceType.PROFILE, ActionType.UPDATE, PermissionScope.PERSONAL),
            
            # Analytics permissions
            Permission(ResourceType.ANALYTICS, ActionType.READ, PermissionScope.PERSONAL),
            
            # Monetization permissions
            Permission(ResourceType.MONETIZATION, ActionType.READ, PermissionScope.PERSONAL),
            Permission(ResourceType.MONETIZATION, ActionType.MANAGE, PermissionScope.PERSONAL),
            
            # Protection permissions
            Permission(ResourceType.PROTECTION, ActionType.READ, PermissionScope.PERSONAL),
            Permission(ResourceType.PROTECTION, ActionType.CREATE, PermissionScope.PERSONAL),
            Permission(ResourceType.PROTECTION, ActionType.MANAGE, PermissionScope.PERSONAL),
            
            # API permissions
            Permission(ResourceType.API, ActionType.READ, PermissionScope.TENANT),
            Permission(ResourceType.API, ActionType.EXECUTE, PermissionScope.TENANT),
            
            # Admin permissions
            Permission(ResourceType.ADMIN, ActionType.MANAGE, PermissionScope.GLOBAL),
            Permission(ResourceType.PLATFORM, ActionType.MANAGE, PermissionScope.GLOBAL),
        ]
        
        # Default system roles
        self.system_roles = {
            RoleType.SUPER_ADMIN: {
                'display_name': 'Super Administrator',
                'description': 'Full system access with all permissions',
                'permissions': ['*:*:*']  # All permissions
            },
            RoleType.ADMIN: {
                'display_name': 'Administrator',
                'description': 'Administrative access with most permissions',
                'permissions': [
                    'platform:manage:global',
                    'content:*:tenant',
                    'analytics:read:tenant',
                    'monetization:manage:tenant'
                ]
            },
            RoleType.CREATOR: {
                'display_name': 'Content Creator',
                'description': 'Standard creator with personal content management',
                'permissions': [
                    'content:*:personal',
                    'profile:*:personal',
                    'analytics:read:personal',
                    'monetization:read:personal',
                    'protection:*:personal',
                    'api:read:tenant'
                ]
            },
            RoleType.PREMIUM_CREATOR: {
                'display_name': 'Premium Creator',
                'description': 'Premium creator with advanced features',
                'permissions': [
                    'content:*:personal',
                    'content:*:shared',
                    'profile:*:personal',
                    'analytics:read:personal',
                    'monetization:*:personal',
                    'protection:*:personal',
                    'collaboration:*:personal',
                    'api:*:tenant'
                ]
            },
            RoleType.COLLABORATOR: {
                'display_name': 'Collaborator',
                'description': 'Collaborative access to shared resources',
                'permissions': [
                    'content:read:shared',
                    'content:update:shared',
                    'collaboration:*:shared',
                    'api:read:tenant'
                ]
            },
            RoleType.VIEWER: {
                'display_name': 'Viewer',
                'description': 'Read-only access to shared resources',
                'permissions': [
                    'content:read:shared',
                    'analytics:read:shared',
                    'api:read:tenant'
                ]
            },
            RoleType.API_USER: {
                'display_name': 'API User',
                'description': 'API access for integrations',
                'permissions': [
                    'api:*:tenant',
                    'content:read:tenant',
                    'analytics:read:tenant'
                ]
            },
            RoleType.GUEST: {
                'display_name': 'Guest',
                'description': 'Limited guest access',
                'permissions': [
                    'content:read:shared'
                ]
            }
        }
    
    async def initialize_system_permissions(self):
        """Initialize system permissions and roles"""        try:
            # Create system permissions
            for perm in self.system_permissions:
                await self._create_permission_if_not_exists(perm)
            
            # Create system roles
            for role_type, role_config in self.system_roles.items():
                await self._create_role_if_not_exists(role_type, role_config)
            
            await self.session.commit()
            logger.info("System permissions and roles initialized successfully")
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to initialize system permissions: {e}")
            raise
    
    async def check_permission(
        self,
        user_id: str,
        permission: Union[Permission, str],
        context: Optional[AccessContext] = None
    ) -> bool:
        """Check if user has specific permission"""        try:
            context = context or AccessContext(user_id=user_id)
            
            # Convert string permission to Permission object
            if isinstance(permission, str):
                permission = self._parse_permission_string(permission)
            
            # Check direct user permissions first
            if await self._check_direct_user_permission(user_id, permission, context):
                await self._log_permission_check(user_id, permission, True, "Direct permission", context)
                return True
            
            # Check role-based permissions
            if await self._check_role_based_permission(user_id, permission, context):
                await self._log_permission_check(user_id, permission, True, "Role-based permission", context)
                return True
            
            # Check if user is resource owner (automatic permissions)
            if await self._check_resource_ownership(user_id, permission, context):
                await self._log_permission_check(user_id, permission, True, "Resource ownership", context)
                return True
            
            await self._log_permission_check(user_id, permission, False, "Permission denied", context)
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed for user {user_id}: {e}")
            await self._log_permission_check(user_id, permission, False, f"Error: {e}", context)
            return False
    
    async def assign_role_to_user(
        self,
        user_id: str,
        role_id: str,
        assigned_by: str,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Assign role to user"""        try:
            # Verify role exists
            role = await self._get_role(role_id)
            if not role:
                raise ValueError(f"Role {role_id} not found")
            
            # Check if assignment already exists
            existing = await self._get_user_role_assignment(user_id, role_id, tenant_id, project_id)
            if existing and existing.is_active:
                raise ValueError("Role assignment already exists")
            
            assignment_id = str(uuid4())
            
            user_role = UserRoles(
                assignment_id=assignment_id,
                user_id=user_id,
                role_id=role_id,
                tenant_id=tenant_id,
                project_id=project_id,
                assigned_by=assigned_by,
                expires_at=expires_at
            )
            
            self.session.add(user_role)
            await self.session.commit()
            
            logger.info(f"Role {role_id} assigned to user {user_id}")
            return assignment_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to assign role to user: {e}")
            raise
    
    async def grant_permission_to_user(
        self,
        user_id: str,
        permission: Union[Permission, str],
        granted_by: str,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Grant specific permission to user"""        try:
            # Convert string permission to Permission object
            if isinstance(permission, str):
                permission = self._parse_permission_string(permission)
            
            # Get or create permission
            permission_record = await self._get_or_create_permission(permission)
            
            assignment_id = str(uuid4())
            
            user_permission = UserPermissions(
                assignment_id=assignment_id,
                user_id=user_id,
                permission_id=permission_record.permission_id,
                resource_id=resource_id,
                tenant_id=tenant_id,
                granted_by=granted_by,
                expires_at=expires_at,
                conditions=conditions
            )
            
            self.session.add(user_permission)
            await self.session.commit()
            
            logger.info(f"Permission {permission.to_string()} granted to user {user_id}")
            return assignment_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to grant permission to user: {e}")
            raise
    
    async def revoke_user_role(
        self,
        user_id: str,
        role_id: str,
        revoked_by: str,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> bool:
        """Revoke role from user"""        try:
            assignment = await self._get_user_role_assignment(user_id, role_id, tenant_id, project_id)
            if not assignment or not assignment.is_active:
                raise ValueError("Role assignment not found")
            
            assignment.is_active = False
            await self.session.commit()
            
            logger.info(f"Role {role_id} revoked from user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to revoke role from user: {e}")
            raise
    
    async def get_user_permissions(self, user_id: str, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all permissions for a user"""        try:
            permissions = set()
            
            # Get direct permissions
            direct_perms = await self._get_direct_user_permissions(user_id, tenant_id)
            permissions.update(direct_perms)
            
            # Get role-based permissions
            role_perms = await self._get_role_based_permissions(user_id, tenant_id)
            permissions.update(role_perms)
            
            # Convert to list of dictionaries
            permission_list = []
            for perm in permissions:
                permission_list.append({
                    'resource': perm.resource.value,
                    'action': perm.action.value,
                    'scope': perm.scope.value,
                    'permission_string': perm.to_string()
                })
            
            return permission_list
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            raise
    
    async def get_user_roles(self, user_id: str, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all roles for a user"""        try:
            query = select(UserRoles, Roles).join(
                Roles, UserRoles.role_id == Roles.role_id
            ).where(
                UserRoles.user_id == user_id,
                UserRoles.is_active == True
            )
            
            if tenant_id:
                query = query.where(UserRoles.tenant_id == tenant_id)
            
            result = await self.session.execute(query)
            assignments = result.all()
            
            role_list = []
            for assignment, role in assignments:
                role_info = {
                    'assignment_id': assignment.assignment_id,
                    'role_id': role.role_id,
                    'role_name': role.role_name,
                    'display_name': role.display_name,
                    'role_type': role.role_type,
                    'tenant_id': assignment.tenant_id,
                    'project_id': assignment.project_id,
                    'assigned_at': assignment.assigned_at,
                    'expires_at': assignment.expires_at,
                    'is_expired': (
                        assignment.expires_at and 
                        assignment.expires_at < datetime.now(timezone.utc)
                    ) if assignment.expires_at else False
                }
                role_list.append(role_info)
            
            return role_list
            
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            raise
    
    async def create_custom_role(
        self,
        role_name: str,
        display_name: str,
        description: str,
        permissions: List[Union[Permission, str]],
        created_by: str
    ) -> str:
        """Create custom role"""        try:
            role_id = str(uuid4())
            
            # Create role
            role = Roles(
                role_id=role_id,
                role_name=role_name,
                role_type=RoleType.CREATOR.value,  # Custom roles are creator type
                display_name=display_name,
                description=description,
                is_system_role=False,
                created_by=created_by
            )
            
            self.session.add(role)
            
            # Assign permissions to role
            for perm in permissions:
                if isinstance(perm, str):
                    perm = self._parse_permission_string(perm)
                
                permission_record = await self._get_or_create_permission(perm)
                
                role_permission = RolePermissions(
                    assignment_id=str(uuid4()),
                    role_id=role_id,
                    permission_id=permission_record.permission_id,
                    granted_by=created_by
                )
                
                self.session.add(role_permission)
            
            await self.session.commit()
            
            logger.info(f"Custom role {role_name} created with ID {role_id}")
            return role_id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create custom role: {e}")
            raise
    
    # Private helper methods
    
    async def _check_direct_user_permission(
        self,
        user_id: str,
        permission: Permission,
        context: AccessContext
    ) -> bool:
        """Check direct user permissions"""        try:
            query = select(UserPermissions, Permissions).join(
                Permissions, UserPermissions.permission_id == Permissions.permission_id
            ).where(
                UserPermissions.user_id == user_id,
                UserPermissions.is_active == True,
                Permissions.resource_type == permission.resource.value,
                Permissions.action_type == permission.action.value,
                Permissions.scope_type == permission.scope.value
            )
            
            # Add resource and tenant filters
            if context.resource_id:
                query = query.where(UserPermissions.resource_id == context.resource_id)
            if context.tenant_id:
                query = query.where(UserPermissions.tenant_id == context.tenant_id)
            
            # Check expiration
            query = query.where(
                (UserPermissions.expires_at.is_(None)) | 
                (UserPermissions.expires_at > datetime.now(timezone.utc))
            )
            
            result = await self.session.execute(query)
            user_perm = result.first()
            
            if user_perm:
                # Evaluate conditions if present
                user_permission, permission_record = user_perm
                if user_permission.conditions:
                    return self._evaluate_conditions(user_permission.conditions, context)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Direct permission check failed: {e}")
            return False
    
    async def _check_role_based_permission(
        self,
        user_id: str,
        permission: Permission,
        context: AccessContext
    ) -> bool:
        """Check role-based permissions"""        try:
            # Get user roles
            user_roles_query = select(UserRoles).where(
                UserRoles.user_id == user_id,
                UserRoles.is_active == True,
                (UserRoles.expires_at.is_(None)) | 
                (UserRoles.expires_at > datetime.now(timezone.utc))
            )
            
            if context.tenant_id:
                user_roles_query = user_roles_query.where(
                    (UserRoles.tenant_id == context.tenant_id) |
                    (UserRoles.tenant_id.is_(None))
                )
            
            result = await self.session.execute(user_roles_query)
            user_roles = result.scalars().all()
            
            # Check permissions for each role
            for user_role in user_roles:
                role_perms_query = select(RolePermissions, Permissions).join(
                    Permissions, RolePermissions.permission_id == Permissions.permission_id
                ).where(
                    RolePermissions.role_id == user_role.role_id,
                    RolePermissions.is_active == True,
                    (RolePermissions.expires_at.is_(None)) | 
                    (RolePermissions.expires_at > datetime.now(timezone.utc))
                )
                
                result = await self.session.execute(role_perms_query)
                role_permissions = result.all()
                
                for role_perm, perm_record in role_permissions:
                    # Check wildcard permissions
                    if (perm_record.resource_type == '*' or 
                        perm_record.resource_type == permission.resource.value):
                        if (perm_record.action_type == '*' or 
                            perm_record.action_type == permission.action.value):
                            if (perm_record.scope_type == '*' or 
                                perm_record.scope_type == permission.scope.value):
                                
                                # Evaluate conditions if present
                                if role_perm.conditions:
                                    if self._evaluate_conditions(role_perm.conditions, context):
                                        return True
                                else:
                                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Role-based permission check failed: {e}")
            return False
    
    async def _check_resource_ownership(
        self,
        user_id: str,
        permission: Permission,
        context: AccessContext
    ) -> bool:
        """Check if user owns the resource"""        try:
            # For personal scope, check if user is the resource owner
            if (permission.scope == PermissionScope.PERSONAL and 
                context.resource_owner_id == user_id):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Resource ownership check failed: {e}")
            return False
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: AccessContext) -> bool:
        """Evaluate permission conditions"""        try:
            for condition_type, condition_value in conditions.items():
                if condition_type == 'time_range':
                    # Check if current time is within allowed range
                    current_time = datetime.now(timezone.utc).time()
                    start_time = datetime.strptime(condition_value['start'], '%H:%M').time()
                    end_time = datetime.strptime(condition_value['end'], '%H:%M').time()
                    
                    if not (start_time <= current_time <= end_time):
                        return False
                
                elif condition_type == 'ip_range':
                    # Check if IP is in allowed range (simplified)
                    allowed_ips = condition_value.get('allowed_ips', [])
                    client_ip = context.metadata.get('ip_address')
                    
                    if client_ip and client_ip not in allowed_ips:
                        return False
                
                elif condition_type == 'resource_limit':
                    # Check resource limits (placeholder)
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _parse_permission_string(self, permission_str: str) -> Permission:
        """Parse permission string to Permission object"""        try:
            parts = permission_str.split(':')
            if len(parts) != 3:
                raise ValueError(f"Invalid permission string format: {permission_str}")
            
            resource_str, action_str, scope_str = parts
            
            # Handle wildcards
            if resource_str == '*':
                resource = ResourceType.PLATFORM  # Default for wildcard
            else:
                resource = ResourceType(resource_str)
            
            if action_str == '*':
                action = ActionType.MANAGE  # Default for wildcard
            else:
                action = ActionType(action_str)
            
            if scope_str == '*':
                scope = PermissionScope.GLOBAL  # Default for wildcard
            else:
                scope = PermissionScope(scope_str)
            
            return Permission(resource=resource, action=action, scope=scope)
            
        except Exception as e:
            logger.error(f"Failed to parse permission string: {e}")
            raise ValueError(f"Invalid permission string: {permission_str}")
    
    async def _get_or_create_permission(self, permission: Permission) -> Permissions:
        """Get or create permission record"""        try:
            permission_name = permission.to_string()
            
            # Try to get existing permission
            stmt = select(Permissions).where(Permissions.permission_name == permission_name)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                return existing
            
            # Create new permission
            permission_record = Permissions(
                permission_id=str(uuid4()),
                permission_name=permission_name,
                resource_type=permission.resource.value,
                action_type=permission.action.value,
                scope_type=permission.scope.value,
                display_name=f"{permission.resource.value.title()} {permission.action.value.title()}",
                description=f"Permission to {permission.action.value} {permission.resource.value} resources",
                is_system_permission=True
            )
            
            self.session.add(permission_record)
            await self.session.flush()  # Get the ID without committing
            
            return permission_record
            
        except Exception as e:
            logger.error(f"Failed to get or create permission: {e}")
            raise
    
    async def _create_permission_if_not_exists(self, permission: Permission):
        """Create permission if it doesn't exist"""        await self._get_or_create_permission(permission)
    
    async def _create_role_if_not_exists(self, role_type: RoleType, role_config: Dict[str, Any]):
        """Create role if it doesn't exist"""        try:
            # Check if role exists
            stmt = select(Roles).where(Roles.role_name == role_type.value)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                return
            
            # Create role
            role_id = str(uuid4())
            role = Roles(
                role_id=role_id,
                role_name=role_type.value,
                role_type=role_type.value,
                display_name=role_config['display_name'],
                description=role_config['description'],
                is_system_role=True
            )
            
            self.session.add(role)
            await self.session.flush()
            
            # Assign permissions to role
            for perm_str in role_config['permissions']:
                if perm_str == '*:*:*':
                    # Grant all permissions
                    for sys_perm in self.system_permissions:
                        perm_record = await self._get_or_create_permission(sys_perm)
                        role_perm = RolePermissions(
                            assignment_id=str(uuid4()),
                            role_id=role_id,
                            permission_id=perm_record.permission_id,
                            granted_by='system'
                        )
                        self.session.add(role_perm)
                else:
                    # Parse and assign specific permission
                    permission = self._parse_permission_string(perm_str)
                    perm_record = await self._get_or_create_permission(permission)
                    
                    role_perm = RolePermissions(
                        assignment_id=str(uuid4()),
                        role_id=role_id,
                        permission_id=perm_record.permission_id,
                        granted_by='system'
                    )
                    self.session.add(role_perm)
            
        except Exception as e:
            logger.error(f"Failed to create role {role_type.value}: {e}")
            raise
    
    async def _get_role(self, role_id: str) -> Optional[Roles]:
        """Get role by ID"""        stmt = select(Roles).where(Roles.role_id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_user_role_assignment(
        self,
        user_id: str,
        role_id: str,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Optional[UserRoles]:
        """Get user role assignment"""        query = select(UserRoles).where(
            UserRoles.user_id == user_id,
            UserRoles.role_id == role_id
        )
        
        if tenant_id:
            query = query.where(UserRoles.tenant_id == tenant_id)
        if project_id:
            query = query.where(UserRoles.project_id == project_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_direct_user_permissions(self, user_id: str, tenant_id: Optional[str] = None) -> Set[Permission]:
        """Get direct user permissions"""        query = select(UserPermissions, Permissions).join(
            Permissions, UserPermissions.permission_id == Permissions.permission_id
        ).where(
            UserPermissions.user_id == user_id,
            UserPermissions.is_active == True,
            (UserPermissions.expires_at.is_(None)) | 
            (UserPermissions.expires_at > datetime.now(timezone.utc))
        )
        
        if tenant_id:
            query = query.where(UserPermissions.tenant_id == tenant_id)
        
        result = await self.session.execute(query)
        permissions = result.all()
        
        perm_set = set()
        for user_perm, perm_record in permissions:
            permission = Permission(
                resource=ResourceType(perm_record.resource_type),
                action=ActionType(perm_record.action_type),
                scope=PermissionScope(perm_record.scope_type)
            )
            perm_set.add(permission)
        
        return perm_set
    
    async def _get_role_based_permissions(self, user_id: str, tenant_id: Optional[str] = None) -> Set[Permission]:
        """Get role-based permissions"""        # This is a simplified version - you would implement the full logic here
        return set()
    
    async def _log_permission_check(
        self,
        user_id: str,
        permission: Permission,
        access_granted: bool,
        reason: str,
        context: AccessContext
    ):
        """Log permission check for audit purposes"""        try:
            audit_log = PermissionAuditLog(
                audit_id=str(uuid4()),
                user_id=user_id,
                action="check",
                resource_type=permission.resource.value,
                resource_id=context.resource_id,
                permission_checked=permission.to_string(),
                access_granted=access_granted,
                reason=reason,
                ip_address=context.metadata.get('ip_address'),
                user_agent=context.metadata.get('user_agent'),
                request_context=context.metadata
            )
            
            self.session.add(audit_log)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log permission check: {e}")

# Export the main classes
__all__ = [
    'PermissionManager',
    'Roles',
    'Permissions',
    'RolePermissions',
    'UserRoles',
    'UserPermissions',
    'PermissionAuditLog',
    'ResourceType',
    'ActionType',
    'RoleType',
    'PermissionScope',
    'Permission',
    'AccessContext'
]
