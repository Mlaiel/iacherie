"""Advanced Authorization and Access Control System
Enterprise-grade role-based access control with fine-grained permissions

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Security Expert + Backend Senior + Database Administrator
"""

import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from collections import defaultdict
import asyncio
import aioredis
from functools import wraps
import inspect

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """
Custom authorization exception"""
    pass


class AccessDecision(Enum):
    """
Access control decision enumeration"""

    ALLOW = "allow"
    DENY = "deny"
    ABSTAIN = "abstain"
    CONDITIONAL = "conditional"


class PermissionType(Enum):
    """Permission type enumeration"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    CREATE = "create"
    UPDATE = "update"
    MANAGE = "manage"
    SHARE = "share"
    EXPORT = "export"


class ResourceType(Enum):
    """Resource type enumeration"""

    CONTENT = "content"
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    SYSTEM = "system"
    API = "api"
    DASHBOARD = "dashboard"
    ANALYTICS = "analytics"
    BILLING = "billing"
    INTEGRATION = "integration"


class PermissionScope(Enum):
    """Permission scope enumeration"""

    GLOBAL = "global"
    ORGANIZATION = "organization"
    PROJECT = "project"
    RESOURCE = "resource"
    OWNER = "owner"


@dataclass
class Permission:
    """Permission data structure"""
    name: str
    resource_type: ResourceType
    permission_type: PermissionType
    scope: PermissionScope
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_expired(self) -> bool:
        """
Check if permission has expired"""
        return self.expires_at is not None and datetime.now(timezone.utc) > self.expires_at
    
    def matches_request(self, resource_type: ResourceType, permission_type: PermissionType,
                       scope: PermissionScope = None) -> bool:
        """
Check if permission matches the request"""
        if self.is_expired():
            return False
        
        type_match = (self.resource_type == resource_type or 
                     self.resource_type == ResourceType.SYSTEM)
        permission_match = (self.permission_type == permission_type or 
                           self.permission_type == PermissionType.ADMIN)
        scope_match = (scope is None or self.scope == scope or 
                      self.scope == PermissionScope.GLOBAL)
        
        return type_match and permission_match and scope_match


@dataclass
class Role:
    """
Role data structure"""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def add_permission(self, permission: Permission):
        """
Add permission to role"""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission):
        """
Remove permission from role"""
        self.permissions.discard(permission)
    
    def has_permission(self, resource_type: ResourceType, permission_type: PermissionType,
                      scope: PermissionScope = None) -> bool:
        """
Check if role has specific permission"""
        return any(p.matches_request(resource_type, permission_type, scope) 
                  for p in self.permissions if not p.is_expired())


@dataclass
class AccessRequest:
    """
Access request data structure"""
    user_id: str
    resource_type: ResourceType
    resource_id: Optional[str]
    permission_type: PermissionType
    scope: PermissionScope = PermissionScope.RESOURCE
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AccessDecisionResult:
    """
Access decision result"""
    decision: AccessDecision
    reason: str
    user_id: str
    resource_type: ResourceType
    permission_type: PermissionType
    conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AccessControlPolicy(ABC):
    """
Abstract base class for access control policies"""
    
    @abstractmethod
    def evaluate(self, request: AccessRequest, user_roles: List[Role], 
                context: Dict[str, Any]) -> AccessDecisionResult:
        """
Evaluate access request against policy"""
        pass
    
    @abstractmethod
    def get_policy_name(self) -> str:
        """
Get policy name"""
        pass


class RoleBasedAccessPolicy(AccessControlPolicy):
    """
Role-based access control policy"""
    
    def get_policy_name(self) -> str:
        return "RBAC"
    
    def evaluate(self, request: AccessRequest, user_roles: List[Role], 
                context: Dict[str, Any]) -> AccessDecisionResult:
        """Evaluate RBAC access request"""
        
        # Check if user has required permission through any role
        for role in user_roles:
            if not role.is_active:
                continue
                
            if role.has_permission(request.resource_type, request.permission_type, request.scope):
                return AccessDecisionResult(
                    decision=AccessDecision.ALLOW,
                    reason=f"User has required permission through role '{role.name}'",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type,
                    metadata={'role': role.name}
                )
        
        return AccessDecisionResult(
            decision=AccessDecision.DENY,
            reason="User does not have required permission",
            user_id=request.user_id,
            resource_type=request.resource_type,
            permission_type=request.permission_type
        )


class AttributeBasedAccessPolicy(AccessControlPolicy):
    """Attribute-based access control policy"""
    
    def get_policy_name(self) -> str:
        return "ABAC"
    
    def evaluate(self, request: AccessRequest, user_roles: List[Role], 
                context: Dict[str, Any]) -> AccessDecisionResult:
        """Evaluate ABAC access request"""
        
        # Check user attributes
        user_attributes = context.get('user_attributes', {})
        resource_attributes = context.get('resource_attributes', {})
        environment_attributes = context.get('environment_attributes', {})
        
        # Example ABAC rules
        conditions = []
        
        # Time-based access control
        current_hour = datetime.now().hour
        if 'working_hours_only' in user_attributes:
            if not (9 <= current_hour <= 17):
                return AccessDecisionResult(
                    decision=AccessDecision.DENY,
                    reason="Access denied outside working hours",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type
                )
            conditions.append("working_hours_check")
        
        # Location-based access control
        user_location = environment_attributes.get('location')
        allowed_locations = user_attributes.get('allowed_locations', [])
        if allowed_locations and user_location not in allowed_locations:
            return AccessDecisionResult(
                decision=AccessDecision.DENY,
                reason=f"Access denied from location: {user_location}",
                user_id=request.user_id,
                resource_type=request.resource_type,
                permission_type=request.permission_type
            )
        
        # Content owner access
        if (request.resource_type == ResourceType.CONTENT and 
            resource_attributes.get('owner_id') == request.user_id):
            return AccessDecisionResult(
                decision=AccessDecision.ALLOW,
                reason="Content owner has full access",
                user_id=request.user_id,
                resource_type=request.resource_type,
                permission_type=request.permission_type,
                conditions=conditions,
                metadata={'owner_access': True}
            )
        
        # Fallback to RBAC
        rbac_policy = RoleBasedAccessPolicy()
        return rbac_policy.evaluate(request, user_roles, context)


class ContentProtectionPolicy(AccessControlPolicy):
    """Content protection specific access policy"""
    
    def get_policy_name(self) -> str:
        return "ContentProtection"
    
    def evaluate(self, request: AccessRequest, user_roles: List[Role], 
                context: Dict[str, Any]) -> AccessDecisionResult:
        """Evaluate content protection access"""
        
        if request.resource_type != ResourceType.CONTENT:
            return AccessDecisionResult(
                decision=AccessDecision.ABSTAIN,
                reason="Policy only applies to content resources",
                user_id=request.user_id,
                resource_type=request.resource_type,
                permission_type=request.permission_type
            )
        
        resource_attributes = context.get('resource_attributes', {})
        
        # Check content protection level
        protection_level = resource_attributes.get('protection_level', 'public')
        
        if protection_level == 'private':
            # Only owner and authorized users can access
            owner_id = resource_attributes.get('owner_id')
            authorized_users = resource_attributes.get('authorized_users', [])
            
            if request.user_id == owner_id or request.user_id in authorized_users:
                return AccessDecisionResult(
                    decision=AccessDecision.ALLOW,
                    reason="Access granted to authorized user",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type,
                    metadata={'protection_level': protection_level}
                )
            else:
                return AccessDecisionResult(
                    decision=AccessDecision.DENY,
                    reason="Access denied to protected content",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type
                )
        
        elif protection_level == 'premium':
            # Check if user has premium subscription
            user_attributes = context.get('user_attributes', {})
            if user_attributes.get('subscription_type') == 'premium':
                return AccessDecisionResult(
                    decision=AccessDecision.ALLOW,
                    reason="Premium content access granted",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type,
                    metadata={'premium_access': True}
                )
            else:
                return AccessDecisionResult(
                    decision=AccessDecision.DENY,
                    reason="Premium subscription required",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type
                )
        
        # Public content - allow access
        return AccessDecisionResult(
            decision=AccessDecision.ALLOW,
            reason="Public content access",
            user_id=request.user_id,
            resource_type=request.resource_type,
            permission_type=request.permission_type,
            metadata={'protection_level': protection_level}
        )


class PolicyEngine:
    """Policy engine for combining multiple access control policies"""
    
    def __init__(self):
        self.policies: List[AccessControlPolicy] = []
        self.policy_weights: Dict[str, float] = {}
        self.combination_algorithm = "unanimous_consent"  # or "majority_vote", "first_applicable"
    
    def add_policy(self, policy: AccessControlPolicy, weight: float = 1.0):
        """Add access control policy"""
        self.policies.append(policy)
        self.policy_weights[policy.get_policy_name()] = weight
    
    def remove_policy(self, policy_name: str):
        """
Remove access control policy"""
        self.policies = [p for p in self.policies if p.get_policy_name() != policy_name]
        self.policy_weights.pop(policy_name, None)
    
    def evaluate_access(self, request: AccessRequest, user_roles: List[Role], 
                       context: Dict[str, Any]) -> AccessDecisionResult:
        """
Evaluate access request using all policies"""
        
        if not self.policies:
            return AccessDecisionResult(
                decision=AccessDecision.DENY,
                reason="No policies configured",
                user_id=request.user_id,
                resource_type=request.resource_type,
                permission_type=request.permission_type
            )
        
        policy_results = []
        
        for policy in self.policies:
            try:
                result = policy.evaluate(request, user_roles, context)
                policy_results.append((policy.get_policy_name(), result))
            except Exception as e:
                logger.error(f"Policy {policy.get_policy_name()} evaluation error: {e}")
                continue
        
        return self._combine_decisions(policy_results, request)
    
    def _combine_decisions(self, policy_results: List[Tuple[str, AccessDecisionResult]], 
                          request: AccessRequest) -> AccessDecisionResult:
        """Combine multiple policy decisions"""
        
        if not policy_results:
            return AccessDecisionResult(
                decision=AccessDecision.DENY,
                reason="No valid policy results",
                user_id=request.user_id,
                resource_type=request.resource_type,
                permission_type=request.permission_type
            )
        
        if self.combination_algorithm == "unanimous_consent":
            # All non-abstaining policies must agree
            allow_count = 0
            deny_count = 0
            abstain_count = 0
            reasons = []
            
            for policy_name, result in policy_results:
                if result.decision == AccessDecision.ALLOW:
                    allow_count += 1
                elif result.decision == AccessDecision.DENY:
                    deny_count += 1
                    reasons.append(f"{policy_name}: {result.reason}")
                else:  # ABSTAIN
                    abstain_count += 1
            
            if deny_count > 0:
                return AccessDecisionResult(
                    decision=AccessDecision.DENY,
                    reason=f"Denied by policies: {'; '.join(reasons)}",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type
                )
            elif allow_count > 0:
                return AccessDecisionResult(
                    decision=AccessDecision.ALLOW,
                    reason=f"Approved by {allow_count} policies",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type
                )
            else:
                return AccessDecisionResult(
                    decision=AccessDecision.DENY,
                    reason="All policies abstained",
                    user_id=request.user_id,
                    resource_type=request.resource_type,
                    permission_type=request.permission_type
                )
        
        elif self.combination_algorithm == "first_applicable":
            # Return first non-abstaining decision
            for policy_name, result in policy_results:
                if result.decision != AccessDecision.ABSTAIN:
                    return result
            
            return AccessDecisionResult(
                decision=AccessDecision.DENY,
                reason="All policies abstained",
                user_id=request.user_id,
                resource_type=request.resource_type,
                permission_type=request.permission_type
            )
        
        # Default to deny
        return AccessDecisionResult(
            decision=AccessDecision.DENY,
            reason="Unknown combination algorithm",
            user_id=request.user_id,
            resource_type=request.resource_type,
            permission_type=request.permission_type
        )
    
    def create_policy(self, user_role: str, resource_type: str) -> Dict[str, Any]:
        """Create security policy configuration"""
        
        # Default policies by role
        role_policies = {
            'admin': {
                'permissions': ['read', 'write', 'delete', 'admin', 'manage'],
                'resources': ['*'],
                'conditions': {},
                'time_restrictions': None
            },
            'creator': {
                'permissions': ['read', 'write', 'create', 'update', 'share'],
                'resources': ['content', 'dashboard', 'analytics'],
                'conditions': {'content_owner': True},
                'time_restrictions': None
            },
            'viewer': {
                'permissions': ['read'],
                'resources': ['content', 'dashboard'],
                'conditions': {'public_only': True},
                'time_restrictions': {'working_hours': True}
            },
            'collaborator': {
                'permissions': ['read', 'write', 'update'],
                'resources': ['content'],
                'conditions': {'invited_only': True},
                'time_restrictions': None
            }
        }
        
        base_policy = role_policies.get(user_role, role_policies['viewer'])
        
        # Customize based on resource type
        resource_customizations = {
            'content': {
                'additional_conditions': ['content_protection_check'],
                'rate_limits': {'read': 1000, 'write': 100}
            },
            'analytics': {
                'additional_conditions': ['data_privacy_check'],
                'encryption_required': True
            },
            'billing': {
                'additional_conditions': ['financial_access_check'],
                'audit_required': True
            }
        }
        
        if resource_type in resource_customizations:
            customization = resource_customizations[resource_type]
            base_policy['conditions'].update(customization.get('additional_conditions', []))
            base_policy.update({k: v for k, v in customization.items() 
                               if k != 'additional_conditions'})
        
        return base_policy


class PermissionManager:
    """
Permission management system"""
    
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.permission_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def create_permission(self, name: str, resource_type: ResourceType, 
                         permission_type: PermissionType, scope: PermissionScope,
                         conditions: Dict[str, Any] = None, 
                         expires_at: datetime = None) -> Permission:
        """
Create new permission"""
        
        permission = Permission(
            name=name,
            resource_type=resource_type,
            permission_type=permission_type,
            scope=scope,
            conditions=conditions or {},
            expires_at=expires_at
        )
        
        self.permissions[name] = permission
        return permission
    
    def get_permission(self, name: str) -> Optional[Permission]:
        """
Get permission by name"""
        return self.permissions.get(name)
    
    def list_permissions(self, resource_type: ResourceType = None, 
                        permission_type: PermissionType = None) -> List[Permission]:
        """
List permissions with optional filtering"""
        
        permissions = list(self.permissions.values())
        
        if resource_type:
            permissions = [p for p in permissions if p.resource_type == resource_type]
        
        if permission_type:
            permissions = [p for p in permissions if p.permission_type == permission_type]
        
        return permissions
    
    def delete_permission(self, name: str) -> bool:
        """
Delete permission"""
        return self.permissions.pop(name, None) is not None
    
    def create_default_permissions(self):
        """
Create default system permissions"""
        
        default_permissions = [
            # Content permissions
            ("content.read", ResourceType.CONTENT, PermissionType.READ, PermissionScope.RESOURCE),
            ("content.write", ResourceType.CONTENT, PermissionType.WRITE, PermissionScope.RESOURCE),
            ("content.create", ResourceType.CONTENT, PermissionType.CREATE, PermissionScope.PROJECT),
            ("content.delete", ResourceType.CONTENT, PermissionType.DELETE, PermissionScope.OWNER),
            ("content.share", ResourceType.CONTENT, PermissionType.SHARE, PermissionScope.RESOURCE),
            
            # User permissions
            ("user.read", ResourceType.USER, PermissionType.READ, PermissionScope.RESOURCE),
            ("user.manage", ResourceType.USER, PermissionType.MANAGE, PermissionScope.ORGANIZATION),
            ("user.admin", ResourceType.USER, PermissionType.ADMIN, PermissionScope.GLOBAL),
            
            # System permissions
            ("system.admin", ResourceType.SYSTEM, PermissionType.ADMIN, PermissionScope.GLOBAL),
            ("system.monitor", ResourceType.SYSTEM, PermissionType.READ, PermissionScope.GLOBAL),
            
            # API permissions
            ("api.read", ResourceType.API, PermissionType.READ, PermissionScope.RESOURCE),
            ("api.write", ResourceType.API, PermissionType.WRITE, PermissionScope.RESOURCE),
            ("api.admin", ResourceType.API, PermissionType.ADMIN, PermissionScope.GLOBAL),
            
            # Analytics permissions
            ("analytics.view", ResourceType.ANALYTICS, PermissionType.READ, PermissionScope.PROJECT),
            ("analytics.export", ResourceType.ANALYTICS, PermissionType.EXPORT, PermissionScope.PROJECT),
            
            # Billing permissions
            ("billing.view", ResourceType.BILLING, PermissionType.READ, PermissionScope.ORGANIZATION),
            ("billing.manage", ResourceType.BILLING, PermissionType.MANAGE, PermissionScope.ORGANIZATION),
        ]
        
        for name, resource_type, permission_type, scope in default_permissions:
            self.create_permission(name, resource_type, permission_type, scope)


class RoleBasedAccessControl:
    """Role-Based Access Control (RBAC) system"""
    
    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = defaultdict(set)
        self.role_hierarchy: Dict[str, Set[str]] = defaultdict(set)  # parent -> children
    
    def create_role(self, name: str, description: str, 
                   parent_roles: List[str] = None) -> Role:
        """
Create new role"""
        
        role = Role(
            name=name,
            description=description,
            parent_roles=set(parent_roles or [])
        )
        
        self.roles[name] = role
        
        # Update role hierarchy
        for parent_role in parent_roles or []:
            self.role_hierarchy[parent_role].add(name)
        
        return role
    
    def get_role(self, name: str) -> Optional[Role]:
        """
Get role by name"""
        return self.roles.get(name)
    
    def assign_permission_to_role(self, role_name: str, permission_name: str) -> bool:
        """
Assign permission to role"""
        role = self.roles.get(role_name)
        permission = self.permission_manager.get_permission(permission_name)
        
        if role and permission:
            role.add_permission(permission)
            return True
        
        return False
    
    def remove_permission_from_role(self, role_name: str, permission_name: str) -> bool:
        """
Remove permission from role"""
        role = self.roles.get(role_name)
        permission = self.permission_manager.get_permission(permission_name)
        
        if role and permission:
            role.remove_permission(permission)
            return True
        
        return False
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """
Assign role to user"""
        if role_name in self.roles:
            self.user_roles[user_id].add(role_name)
            return True
        
        return False
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """
Remove role from user"""
        if role_name in self.user_roles.get(user_id, set()):
            self.user_roles[user_id].remove(role_name)
            return True
        
        return False
    
    def get_user_roles(self, user_id: str, include_inherited: bool = True) -> List[Role]:
        """
Get user roles with optional inheritance"""
        direct_roles = self.user_roles.get(user_id, set())
        
        if not include_inherited:
            return [self.roles[role_name] for role_name in direct_roles if role_name in self.roles]
        
        # Include inherited roles
        all_roles = set(direct_roles)
        
        for role_name in direct_roles:
            all_roles.update(self._get_inherited_roles(role_name))
        
        return [self.roles[role_name] for role_name in all_roles if role_name in self.roles]
    
    def user_has_permission(self, user_id: str, resource_type: ResourceType,
                           permission_type: PermissionType, scope: PermissionScope = None) -> bool:
        """
Check if user has specific permission"""
        user_roles = self.get_user_roles(user_id, include_inherited=True)
        
        return any(role.has_permission(resource_type, permission_type, scope) 
                  for role in user_roles)
    
    def _get_inherited_roles(self, role_name: str) -> Set[str]:
        """
Get all inherited roles recursively"""
        inherited = set()
        
        if role_name in self.roles:
            role = self.roles[role_name]
            for parent_role in role.parent_roles:
                inherited.add(parent_role)
                inherited.update(self._get_inherited_roles(parent_role))
        
        return inherited
    
    def create_default_roles(self):
        """
Create default system roles"""
        
        # Create base roles
        self.create_role("admin", "System Administrator with full access")
        self.create_role("creator", "Content creator with content management permissions")
        self.create_role("collaborator", "Collaborator with limited content access")
        self.create_role("viewer", "Read-only access to public content")
        self.create_role("premium_user", "Premium subscriber with enhanced access", ["viewer"])
        self.create_role("content_manager", "Content management role", ["creator"])
        self.create_role("analytics_viewer", "Analytics view access", ["viewer"])
        
        # Assign permissions to roles
        
        # Admin role - all permissions
        admin_permissions = [p.name for p in self.permission_manager.permissions.values()]
        for perm in admin_permissions:
            self.assign_permission_to_role("admin", perm)
        
        # Creator role
        creator_permissions = [
            "content.read", "content.write", "content.create", "content.delete", "content.share",
            "analytics.view", "api.read", "api.write"
        ]
        for perm in creator_permissions:
            self.assign_permission_to_role("creator", perm)
        
        # Collaborator role
        collaborator_permissions = [
            "content.read", "content.write", "content.share"
        ]
        for perm in collaborator_permissions:
            self.assign_permission_to_role("collaborator", perm)
        
        # Viewer role
        viewer_permissions = ["content.read", "api.read"]
        for perm in viewer_permissions:
            self.assign_permission_to_role("viewer", perm)
        
        # Premium user role
        premium_permissions = ["analytics.view"]
        for perm in premium_permissions:
            self.assign_permission_to_role("premium_user", perm)


class ResourceAccessManager:
    """Resource-specific access management"""
    
    def __init__(self):
        self.resource_owners: Dict[str, str] = {}  # resource_id -> user_id
        self.resource_permissions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        self.resource_attributes: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def set_resource_owner(self, resource_id: str, owner_id: str):
        """
Set resource owner"""
        self.resource_owners[resource_id] = owner_id
    
    def get_resource_owner(self, resource_id: str) -> Optional[str]:
        """
Get resource owner"""
        return self.resource_owners.get(resource_id)
    
    def grant_resource_access(self, resource_id: str, user_id: str, 
                             permissions: List[str]):
        """
Grant specific permissions to user for resource"""
        self.resource_permissions[resource_id][user_id].update(permissions)
    
    def revoke_resource_access(self, resource_id: str, user_id: str, 
                              permissions: List[str] = None):
        """
Revoke permissions from user for resource"""
        if permissions is None:
            # Revoke all permissions
            self.resource_permissions[resource_id].pop(user_id, None)
        else:
            self.resource_permissions[resource_id][user_id].difference_update(permissions)
    
    def check_resource_access(self, resource_id: str, user_id: str, 
                             permission: str) -> bool:
        """
Check if user has specific permission for resource"""
        
        # Owner has all permissions
        if self.resource_owners.get(resource_id) == user_id:
            return True
        
        # Check explicit permissions
        user_permissions = self.resource_permissions[resource_id].get(user_id, set())
        return permission in user_permissions
    
    def set_resource_attributes(self, resource_id: str, attributes: Dict[str, Any]):
        """
Set resource attributes for policy evaluation"""
        self.resource_attributes[resource_id].update(attributes)
    
    def get_resource_attributes(self, resource_id: str) -> Dict[str, Any]:
        """
Get resource attributes"""
        return self.resource_attributes.get(resource_id, {})


class AuthorizationManager:
    """
Main authorization manager"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.permission_manager = PermissionManager()
        self.rbac = RoleBasedAccessControl(self.permission_manager)
        self.resource_manager = ResourceAccessManager()
        self.policy_engine = PolicyEngine()
        
        # Initialize default permissions and roles
        self.permission_manager.create_default_permissions()
        self.rbac.create_default_roles()
        
        # Add default policies
        self.policy_engine.add_policy(RoleBasedAccessPolicy(), 1.0)
        self.policy_engine.add_policy(AttributeBasedAccessPolicy(), 0.8)
        self.policy_engine.add_policy(ContentProtectionPolicy(), 1.2)
        
        # Access decision cache
        self.decision_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def authorize(self, user_id: str, resource_type: ResourceType,
                       resource_id: str, permission_type: PermissionType,
                       context: Dict[str, Any] = None) -> AccessDecisionResult:
        """Authorize access request"""
        
        # Create access request
        request = AccessRequest(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_type=permission_type,
            context=context or {}
        )
        
        # Check cache first
        cache_key = self._get_cache_key(request)
        if cache_key in self.decision_cache:
            cached_result, timestamp = self.decision_cache[cache_key]
            if (datetime.now(timezone.utc) - timestamp).seconds < self.cache_ttl:
                return cached_result
        
        # Get user roles
        user_roles = self.rbac.get_user_roles(user_id)
        
        # Enhance context with resource attributes
        enhanced_context = dict(context or {})
        if resource_id:
            enhanced_context['resource_attributes'] = self.resource_manager.get_resource_attributes(resource_id)
            enhanced_context['resource_attributes']['owner_id'] = self.resource_manager.get_resource_owner(resource_id)
        
        # Evaluate with policy engine
        decision_result = self.policy_engine.evaluate_access(request, user_roles, enhanced_context)
        
        # Cache the result
        self.decision_cache[cache_key] = (decision_result, datetime.now(timezone.utc))
        
        # Log the decision
        await self._log_access_decision(request, decision_result)
        
        return decision_result
    
    async def bulk_authorize(self, requests: List[Tuple[str, ResourceType, str, PermissionType]],
                           context: Dict[str, Any] = None) -> List[AccessDecisionResult]:
        """
Authorize multiple access requests efficiently"""
        
        results = []
        for user_id, resource_type, resource_id, permission_type in requests:
            result = await self.authorize(user_id, resource_type, resource_id, 
                                        permission_type, context)
            results.append(result)
        
        return results
    
    def grant_permission(self, user_id: str, role_name: str) -> bool:
        """
Grant role to user"""
        return self.rbac.assign_role_to_user(user_id, role_name)
    
    def revoke_permission(self, user_id: str, role_name: str) -> bool:
        """
Revoke role from user"""
        return self.rbac.remove_role_from_user(user_id, role_name)
    
    def create_resource_policy(self, resource_id: str, owner_id: str, 
                              protection_level: str = "public",
                              authorized_users: List[str] = None) -> bool:
        """Create access policy for specific resource"""
        
        # Set resource owner
        self.resource_manager.set_resource_owner(resource_id, owner_id)
        
        # Set resource attributes
        attributes = {
            'protection_level': protection_level,
            'authorized_users': authorized_users or [],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.resource_manager.set_resource_attributes(resource_id, attributes)
        
        return True
    
    def _get_cache_key(self, request: AccessRequest) -> str:
        """
Generate cache key for access request"""
        return f"{request.user_id}:{request.resource_type.value}:{request.resource_id}:{request.permission_type.value}"
    
    async def _log_access_decision(self, request: AccessRequest, 
                                  decision: AccessDecisionResult):
        """Log access decision for audit purposes"""
        try:
            redis_client = await aioredis.from_url(self.redis_url)
            
            log_entry = {
                'user_id': request.user_id,
                'resource_type': request.resource_type.value,
                'resource_id': request.resource_id,
                'permission_type': request.permission_type.value,
                'decision': decision.decision.value,
                'reason': decision.reason,
                'timestamp': decision.timestamp.isoformat(),
                'metadata': decision.metadata
            }
            
            # Store in Redis with expiration (30 days)
            await redis_client.setex(
                f"access_log:{datetime.now().strftime('%Y-%m-%d')}:{secrets.token_hex(8)}",
                30 * 24 * 3600,  # 30 days
                json.dumps(log_entry)
            )
            
            await redis_client.close()
            
        except Exception as e:
            logger.error(f"Failed to log access decision: {e}")


def require_permission(resource_type: ResourceType, permission_type: PermissionType):
    """Decorator for enforcing permissions on functions"""
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get user_id from function arguments or context
            user_id = kwargs.get('user_id') or getattr(args[0] if args else None, 'user_id', None)
            resource_id = kwargs.get('resource_id', 'default')
            
            if not user_id:
                raise AuthorizationError("User ID required for authorization")
            
            # Get authorization manager (should be injected or available in context)
            auth_manager = kwargs.get('auth_manager')
            if not auth_manager:
                raise AuthorizationError("Authorization manager not available")
            
            # Check authorization
            decision = await auth_manager.authorize(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                permission_type=permission_type
            )
            
            if decision.decision != AccessDecision.ALLOW:
                raise AuthorizationError(f"Access denied: {decision.reason}")
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


__all__ = [
    'AuthorizationManager',
    'RoleBasedAccessControl',
    'PermissionManager',
    'ResourceAccessManager',
    'PolicyEngine',
    'Permission',
    'Role',
    'AccessRequest',
    'AccessDecisionResult',
    'RoleBasedAccessPolicy',
    'AttributeBasedAccessPolicy',
    'ContentProtectionPolicy',
    'AuthorizationError',
    'AccessDecision',
    'PermissionType',
    'ResourceType',
    'PermissionScope',
    'require_permission'
]
