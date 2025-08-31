"""
User Roles and Permissions Configuration Module
===============================================

Enterprise user role-based access control (RBAC) and permissions management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Union
from dataclasses import dataclass
from datetime import datetime, timedelta


class UserRole(str, Enum):
    """User roles in the platform hierarchy."""
    PLATFORM_ADMIN = "platform_admin"
    TENANT_ADMIN = "tenant_admin"
    CONTENT_MANAGER = "content_manager"
    CREATOR_PROFESSIONAL = "creator_professional"
    CREATOR_STANDARD = "creator_standard"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"
    API_CLIENT = "api_client"
    SUPPORT_AGENT = "support_agent"
    AUDITOR = "auditor"


class Permission(str, Enum):
    """Granular permissions for system operations."""
    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE_ROLES = "user:manage_roles"
    
    # Content permissions
    CONTENT_CREATE = "content:create"
    CONTENT_READ = "content:read"
    CONTENT_UPDATE = "content:update"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"
    CONTENT_MODERATE = "content:moderate"
    
    # Protection permissions
    PROTECTION_CONFIGURE = "protection:configure"
    PROTECTION_VIEW_ALERTS = "protection:view_alerts"
    PROTECTION_MANAGE_ALERTS = "protection:manage_alerts"
    PROTECTION_VIEW_REPORTS = "protection:view_reports"
    
    # Analytics permissions
    ANALYTICS_VIEW_BASIC = "analytics:view_basic"
    ANALYTICS_VIEW_ADVANCED = "analytics:view_advanced"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_CONFIGURE = "analytics:configure"
    
    # Financial permissions
    FINANCE_VIEW_REVENUE = "finance:view_revenue"
    FINANCE_MANAGE_PAYOUTS = "finance:manage_payouts"
    FINANCE_VIEW_BILLING = "finance:view_billing"
    FINANCE_MANAGE_BILLING = "finance:manage_billing"
    
    # Collaboration permissions
    COLLABORATION_INVITE = "collaboration:invite"
    COLLABORATION_ACCEPT = "collaboration:accept"
    COLLABORATION_MANAGE = "collaboration:manage"
    COLLABORATION_VIEW = "collaboration:view"
    
    # System administration permissions
    SYSTEM_CONFIGURE = "system:configure"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_AUDIT = "system:audit"
    SYSTEM_BACKUP = "system:backup"
    
    # API permissions
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"
    
    # Tenant management permissions
    TENANT_CONFIGURE = "tenant:configure"
    TENANT_MANAGE_USERS = "tenant:manage_users"
    TENANT_VIEW_ANALYTICS = "tenant:view_analytics"
    TENANT_MANAGE_BILLING = "tenant:manage_billing"


class ResourceType(str, Enum):
    """Resource types for permission scoping."""
    USER = "user"
    CONTENT = "content"
    TENANT = "tenant"
    ANALYTICS = "analytics"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    SYSTEM = "system"
    API = "api"
    FINANCE = "finance"


@dataclass
class PermissionScope:
    """Permission scope definition."""
    resource_type: ResourceType
    resource_ids: Optional[List[str]] = None  # None means all resources
    conditions: Optional[Dict[str, str]] = None
    time_bound: Optional[datetime] = None
    ip_restrictions: Optional[List[str]] = None


@dataclass
class RoleDefinition:
    """Complete role definition with permissions and constraints."""
    name: str
    description: str
    permissions: Set[Permission]
    inherits_from: Optional[List[UserRole]] = None
    max_concurrent_sessions: int = 5
    session_timeout_minutes: int = 30
    ip_whitelist: Optional[List[str]] = None
    time_restrictions: Optional[Dict[str, str]] = None
    mfa_required: bool = False


class UserRolesConfig:
    """Enterprise user roles and permissions configuration."""

    # Role hierarchy and inheritance
    ROLE_HIERARCHY = {
        UserRole.PLATFORM_ADMIN: {
            "level": 10,
            "inherits_from": [],
            "can_assign_roles": [
                UserRole.TENANT_ADMIN,
                UserRole.SUPPORT_AGENT,
                UserRole.AUDITOR
            ]
        },
        UserRole.TENANT_ADMIN: {
            "level": 8,
            "inherits_from": [UserRole.CONTENT_MANAGER],
            "can_assign_roles": [
                UserRole.CONTENT_MANAGER,
                UserRole.CREATOR_PROFESSIONAL,
                UserRole.CREATOR_STANDARD,
                UserRole.COLLABORATOR,
                UserRole.VIEWER
            ]
        },
        UserRole.CONTENT_MANAGER: {
            "level": 6,
            "inherits_from": [UserRole.CREATOR_PROFESSIONAL],
            "can_assign_roles": [
                UserRole.CREATOR_STANDARD,
                UserRole.COLLABORATOR,
                UserRole.VIEWER
            ]
        },
        UserRole.CREATOR_PROFESSIONAL: {
            "level": 5,
            "inherits_from": [UserRole.CREATOR_STANDARD],
            "can_assign_roles": [
                UserRole.COLLABORATOR,
                UserRole.VIEWER
            ]
        },
        UserRole.CREATOR_STANDARD: {
            "level": 4,
            "inherits_from": [UserRole.COLLABORATOR],
            "can_assign_roles": [
                UserRole.COLLABORATOR
            ]
        },
        UserRole.COLLABORATOR: {
            "level": 3,
            "inherits_from": [UserRole.VIEWER],
            "can_assign_roles": []
        },
        UserRole.VIEWER: {
            "level": 2,
            "inherits_from": [],
            "can_assign_roles": []
        },
        UserRole.API_CLIENT: {
            "level": 3,
            "inherits_from": [],
            "can_assign_roles": []
        },
        UserRole.SUPPORT_AGENT: {
            "level": 7,
            "inherits_from": [UserRole.VIEWER],
            "can_assign_roles": []
        },
        UserRole.AUDITOR: {
            "level": 6,
            "inherits_from": [UserRole.VIEWER],
            "can_assign_roles": []
        }
    }

    # Detailed role definitions
    ROLE_DEFINITIONS = {
        UserRole.PLATFORM_ADMIN: RoleDefinition(
            name="Platform Administrator",
            description="Full system administration access across all tenants",
            permissions={
                Permission.SYSTEM_CONFIGURE,
                Permission.SYSTEM_MONITOR,
                Permission.SYSTEM_AUDIT,
                Permission.SYSTEM_BACKUP,
                Permission.TENANT_CONFIGURE,
                Permission.TENANT_MANAGE_USERS,
                Permission.TENANT_VIEW_ANALYTICS,
                Permission.USER_CREATE,
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.USER_DELETE,
                Permission.USER_MANAGE_ROLES,
                Permission.API_ADMIN
            },
            mfa_required=True,
            max_concurrent_sessions=3,
            session_timeout_minutes=60
        ),
        
        UserRole.TENANT_ADMIN: RoleDefinition(
            name="Tenant Administrator",
            description="Full administration within tenant scope",
            permissions={
                Permission.TENANT_CONFIGURE,
                Permission.TENANT_MANAGE_USERS,
                Permission.TENANT_VIEW_ANALYTICS,
                Permission.TENANT_MANAGE_BILLING,
                Permission.USER_CREATE,
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.USER_DELETE,
                Permission.USER_MANAGE_ROLES,
                Permission.CONTENT_CREATE,
                Permission.CONTENT_READ,
                Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE,
                Permission.CONTENT_PUBLISH,
                Permission.CONTENT_MODERATE,
                Permission.PROTECTION_CONFIGURE,
                Permission.PROTECTION_VIEW_ALERTS,
                Permission.PROTECTION_MANAGE_ALERTS,
                Permission.PROTECTION_VIEW_REPORTS,
                Permission.ANALYTICS_VIEW_ADVANCED,
                Permission.ANALYTICS_EXPORT,
                Permission.ANALYTICS_CONFIGURE,
                Permission.FINANCE_VIEW_REVENUE,
                Permission.FINANCE_MANAGE_PAYOUTS,
                Permission.FINANCE_VIEW_BILLING,
                Permission.FINANCE_MANAGE_BILLING,
                Permission.COLLABORATION_MANAGE,
                Permission.API_READ,
                Permission.API_WRITE
            },
            mfa_required=True,
            max_concurrent_sessions=5,
            session_timeout_minutes=45
        ),
        
        UserRole.CONTENT_MANAGER: RoleDefinition(
            name="Content Manager",
            description="Manages content and user permissions within tenant",
            permissions={
                Permission.USER_READ,
                Permission.USER_UPDATE,
                Permission.CONTENT_CREATE,
                Permission.CONTENT_READ,
                Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE,
                Permission.CONTENT_PUBLISH,
                Permission.CONTENT_MODERATE,
                Permission.PROTECTION_CONFIGURE,
                Permission.PROTECTION_VIEW_ALERTS,
                Permission.PROTECTION_MANAGE_ALERTS,
                Permission.PROTECTION_VIEW_REPORTS,
                Permission.ANALYTICS_VIEW_ADVANCED,
                Permission.ANALYTICS_EXPORT,
                Permission.FINANCE_VIEW_REVENUE,
                Permission.COLLABORATION_MANAGE,
                Permission.COLLABORATION_INVITE,
                Permission.API_READ,
                Permission.API_WRITE
            },
            max_concurrent_sessions=5,
            session_timeout_minutes=30
        ),
        
        UserRole.CREATOR_PROFESSIONAL: RoleDefinition(
            name="Professional Creator",
            description="Advanced creator with enhanced features and analytics",
            permissions={
                Permission.CONTENT_CREATE,
                Permission.CONTENT_READ,
                Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE,
                Permission.CONTENT_PUBLISH,
                Permission.PROTECTION_CONFIGURE,
                Permission.PROTECTION_VIEW_ALERTS,
                Permission.PROTECTION_VIEW_REPORTS,
                Permission.ANALYTICS_VIEW_ADVANCED,
                Permission.ANALYTICS_EXPORT,
                Permission.FINANCE_VIEW_REVENUE,
                Permission.COLLABORATION_INVITE,
                Permission.COLLABORATION_ACCEPT,
                Permission.COLLABORATION_MANAGE,
                Permission.COLLABORATION_VIEW,
                Permission.API_READ,
                Permission.API_WRITE
            },
            max_concurrent_sessions=5,
            session_timeout_minutes=30
        ),
        
        UserRole.CREATOR_STANDARD: RoleDefinition(
            name="Standard Creator",
            description="Basic creator with essential content management features",
            permissions={
                Permission.CONTENT_CREATE,
                Permission.CONTENT_READ,
                Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE,
                Permission.CONTENT_PUBLISH,
                Permission.PROTECTION_VIEW_ALERTS,
                Permission.ANALYTICS_VIEW_BASIC,
                Permission.FINANCE_VIEW_REVENUE,
                Permission.COLLABORATION_ACCEPT,
                Permission.COLLABORATION_VIEW,
                Permission.API_READ
            },
            max_concurrent_sessions=3,
            session_timeout_minutes=30
        ),
        
        UserRole.COLLABORATOR: RoleDefinition(
            name="Collaborator",
            description="Can collaborate on content and view shared resources",
            permissions={
                Permission.CONTENT_READ,
                Permission.CONTENT_UPDATE,
                Permission.COLLABORATION_ACCEPT,
                Permission.COLLABORATION_VIEW,
                Permission.ANALYTICS_VIEW_BASIC,
                Permission.API_READ
            },
            max_concurrent_sessions=3,
            session_timeout_minutes=30
        ),
        
        UserRole.VIEWER: RoleDefinition(
            name="Viewer",
            description="Read-only access to shared content and basic information",
            permissions={
                Permission.CONTENT_READ,
                Permission.COLLABORATION_VIEW,
                Permission.ANALYTICS_VIEW_BASIC
            },
            max_concurrent_sessions=2,
            session_timeout_minutes=30
        ),
        
        UserRole.API_CLIENT: RoleDefinition(
            name="API Client",
            description="Programmatic access for external integrations",
            permissions={
                Permission.API_READ,
                Permission.API_WRITE,
                Permission.CONTENT_READ,
                Permission.CONTENT_CREATE,
                Permission.ANALYTICS_VIEW_BASIC
            },
            max_concurrent_sessions=10,
            session_timeout_minutes=120
        ),
        
        UserRole.SUPPORT_AGENT: RoleDefinition(
            name="Support Agent",
            description="Customer support with limited system access",
            permissions={
                Permission.USER_READ,
                Permission.CONTENT_READ,
                Permission.PROTECTION_VIEW_ALERTS,
                Permission.PROTECTION_VIEW_REPORTS,
                Permission.ANALYTICS_VIEW_BASIC,
                Permission.COLLABORATION_VIEW,
                Permission.SYSTEM_MONITOR
            },
            max_concurrent_sessions=3,
            session_timeout_minutes=60
        ),
        
        UserRole.AUDITOR: RoleDefinition(
            name="Auditor",
            description="Audit and compliance monitoring access",
            permissions={
                Permission.SYSTEM_AUDIT,
                Permission.USER_READ,
                Permission.CONTENT_READ,
                Permission.PROTECTION_VIEW_REPORTS,
                Permission.ANALYTICS_VIEW_ADVANCED,
                Permission.ANALYTICS_EXPORT,
                Permission.FINANCE_VIEW_REVENUE,
                Permission.FINANCE_VIEW_BILLING
            },
            max_concurrent_sessions=2,
            session_timeout_minutes=120
        )
    }

    # Permission groups for easier management
    PERMISSION_GROUPS = {
        "user_management": [
            Permission.USER_CREATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.USER_DELETE,
            Permission.USER_MANAGE_ROLES
        ],
        "content_management": [
            Permission.CONTENT_CREATE,
            Permission.CONTENT_READ,
            Permission.CONTENT_UPDATE,
            Permission.CONTENT_DELETE,
            Permission.CONTENT_PUBLISH,
            Permission.CONTENT_MODERATE
        ],
        "protection_management": [
            Permission.PROTECTION_CONFIGURE,
            Permission.PROTECTION_VIEW_ALERTS,
            Permission.PROTECTION_MANAGE_ALERTS,
            Permission.PROTECTION_VIEW_REPORTS
        ],
        "analytics_access": [
            Permission.ANALYTICS_VIEW_BASIC,
            Permission.ANALYTICS_VIEW_ADVANCED,
            Permission.ANALYTICS_EXPORT,
            Permission.ANALYTICS_CONFIGURE
        ],
        "financial_access": [
            Permission.FINANCE_VIEW_REVENUE,
            Permission.FINANCE_MANAGE_PAYOUTS,
            Permission.FINANCE_VIEW_BILLING,
            Permission.FINANCE_MANAGE_BILLING
        ],
        "collaboration_features": [
            Permission.COLLABORATION_INVITE,
            Permission.COLLABORATION_ACCEPT,
            Permission.COLLABORATION_MANAGE,
            Permission.COLLABORATION_VIEW
        ],
        "system_administration": [
            Permission.SYSTEM_CONFIGURE,
            Permission.SYSTEM_MONITOR,
            Permission.SYSTEM_AUDIT,
            Permission.SYSTEM_BACKUP
        ],
        "api_access": [
            Permission.API_READ,
            Permission.API_WRITE,
            Permission.API_ADMIN
        ]
    }

    # Role-based feature access
    ROLE_FEATURES = {
        UserRole.PLATFORM_ADMIN: {
            "all_features": True
        },
        UserRole.TENANT_ADMIN: {
            "advanced_analytics": True,
            "custom_branding": True,
            "api_access": True,
            "bulk_operations": True,
            "user_management": True,
            "billing_management": True
        },
        UserRole.CONTENT_MANAGER: {
            "advanced_analytics": True,
            "bulk_operations": True,
            "user_management": True,
            "content_moderation": True
        },
        UserRole.CREATOR_PROFESSIONAL: {
            "advanced_analytics": True,
            "collaboration_matching": True,
            "priority_processing": True,
            "custom_integrations": True
        },
        UserRole.CREATOR_STANDARD: {
            "basic_analytics": True,
            "collaboration_basic": True,
            "standard_processing": True
        },
        UserRole.COLLABORATOR: {
            "collaboration_basic": True,
            "content_contribution": True
        },
        UserRole.VIEWER: {
            "read_only_access": True
        }
    }

    @classmethod
    def get_role_permissions(cls, role: UserRole) -> Set[Permission]:
        """Get all permissions for a role including inherited permissions."""
        role_def = cls.ROLE_DEFINITIONS.get(role)
        if not role_def:
            return set()
        
        permissions = role_def.permissions.copy()
        
        # Add inherited permissions
        hierarchy = cls.ROLE_HIERARCHY.get(role, {})
        for parent_role in hierarchy.get("inherits_from", []):
            parent_permissions = cls.get_role_permissions(parent_role)
            permissions.update(parent_permissions)
        
        return permissions

    @classmethod
    def has_permission(cls, user_role: UserRole, permission: Permission, resource_type: Optional[ResourceType] = None) -> bool:
        """Check if a role has a specific permission."""
        role_permissions = cls.get_role_permissions(user_role)
        return permission in role_permissions

    @classmethod
    def can_assign_role(cls, assigner_role: UserRole, target_role: UserRole) -> bool:
        """Check if a role can assign another role."""
        hierarchy = cls.ROLE_HIERARCHY.get(assigner_role, {})
        assignable_roles = hierarchy.get("can_assign_roles", [])
        return target_role in assignable_roles

    @classmethod
    def get_role_level(cls, role: UserRole) -> int:
        """Get hierarchical level of a role."""
        hierarchy = cls.ROLE_HIERARCHY.get(role, {})
        return hierarchy.get("level", 0)

    @classmethod
    def is_higher_role(cls, role1: UserRole, role2: UserRole) -> bool:
        """Check if role1 has higher privileges than role2."""



        return cls.get_role_level(role1) > cls.get_role_level(role2)

    @classmethod
    def get_role_features(cls, role: UserRole) -> Dict[str, bool]:
        """Get feature access for a role."""



        return cls.ROLE_FEATURES.get(role, {})

    @classmethod
    def validate_role_assignment(cls, assigner: UserRole, assignee: UserRole, tenant_context: bool = True) -> Dict[str, Union[bool, str]]:
        """Validate if a role assignment is permitted."""
        validation = {
            "valid": True,
            "reason": ""
        }
        
        # Check if assigner can assign the target role
        if not cls.can_assign_role(assigner, assignee):
            validation["valid"] = False
            validation["reason"] = f"Role {assigner} cannot assign role {assignee}"
            return validation
        
        # Check hierarchical constraints
        if cls.get_role_level(assignee) >= cls.get_role_level(assigner):
            validation["valid"] = False
            validation["reason"] = "Cannot assign role with equal or higher privileges"
            return validation
        
        return validation

    @classmethod
    def get_permission_groups(cls) -> Dict[str, List[Permission]]:
        """Get all permission groups."""



        return cls.PERMISSION_GROUPS

    @classmethod
    def get_permissions_in_group(cls, group_name: str) -> List[Permission]:
        """Get permissions in a specific group."""



        return cls.PERMISSION_GROUPS.get(group_name, [])
