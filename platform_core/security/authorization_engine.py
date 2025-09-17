#!/usr/bin/env python3
"""
Authorization Engine - Enterprise Granular Access Control System
Advanced RBAC/ABAC authorization with dynamic policy enforcement

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive authorization management including:
- Role-Based Access Control (RBAC) with hierarchical roles
- Attribute-Based Access Control (ABAC) with dynamic policies
- Fine-grained permission management with resource-level control
- Dynamic policy evaluation with context-aware decisions
- Creator economy specific authorization patterns
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import fnmatch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PermissionType(Enum):
    """Permission type enumeration"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    CREATE = "create"
    UPDATE = "update"
    SHARE = "share"
    DOWNLOAD = "download"
    PUBLISH = "publish"


class ResourceType(Enum):
    """Resource type enumeration"""
    USER = "user"
    CONTENT = "content"
    PROJECT = "project"
    WORKSPACE = "workspace"
    ANALYTICS = "analytics"
    BILLING = "billing"
    SETTINGS = "settings"
    API = "api"
    SYSTEM = "system"
    TENANT = "tenant"


class PolicyEffect(Enum):
    """Policy effect enumeration"""
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"


class AuthorizationContext(Enum):
    """Authorization context enumeration"""
    WEB_UI = "web_ui"
    API_CALL = "api_call"
    BACKGROUND_JOB = "background_job"
    WEBHOOK = "webhook"
    SYSTEM_INTERNAL = "system_internal"


@dataclass
class Permission:
    """Permission definition"""
    permission_id: str
    name: str
    description: str
    permission_type: PermissionType
    resource_type: ResourceType
    resource_pattern: str = "*"  # Wildcard pattern for resources
    conditions: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Role:
    """Role definition with hierarchical support"""
    role_id: str
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    child_roles: Set[str] = field(default_factory=set)
    is_system_role: bool = False
    is_active: bool = True
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserRoleAssignment:
    """User role assignment"""
    assignment_id: str
    user_id: str
    role_id: str
    tenant_id: Optional[str] = None
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    assigned_by: str = ""
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizationPolicy:
    """ABAC authorization policy"""
    policy_id: str
    name: str
    description: str
    effect: PolicyEffect
    subjects: Dict[str, Any] = field(default_factory=dict)  # User attributes
    resources: Dict[str, Any] = field(default_factory=dict)  # Resource attributes
    actions: List[str] = field(default_factory=list)  # Action patterns
    conditions: Dict[str, Any] = field(default_factory=dict)  # Context conditions
    priority: int = 100
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuthorizationRequest:
    """Authorization request context"""
    request_id: str
    user_id: str
    action: str
    resource_type: ResourceType
    resource_id: str
    tenant_id: Optional[str] = None
    context: AuthorizationContext = AuthorizationContext.API_CALL
    request_attributes: Dict[str, Any] = field(default_factory=dict)
    resource_attributes: Dict[str, Any] = field(default_factory=dict)
    environment_attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuthorizationDecision:
    """Authorization decision result"""
    decision_id: str
    request: AuthorizationRequest
    decision: str  # "allow", "deny", "indeterminate"
    reasons: List[str] = field(default_factory=list)
    applicable_policies: List[str] = field(default_factory=list)
    applicable_roles: List[str] = field(default_factory=list)
    applicable_permissions: List[str] = field(default_factory=list)
    evaluation_time_ms: float = 0.0
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AuthorizationEngine:
    """
    Enterprise Authorization Engine
    
    Provides comprehensive authorization management with RBAC and ABAC support,
    hierarchical roles, dynamic policy evaluation, and creator economy specific
    access patterns for multi-tenant platform security.
    """

    def __init__(self):
        # Core authorization data
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.user_role_assignments: Dict[str, List[UserRoleAssignment]] = defaultdict(list)
        self.authorization_policies: Dict[str, AuthorizationPolicy] = {}
        
        # Decision cache for performance
        self.decision_cache: Dict[str, AuthorizationDecision] = {}
        self.cache_ttl = timedelta(minutes=5)
        
        # Audit trail
        self.authorization_decisions: List[AuthorizationDecision] = []
        
        # Role hierarchy cache
        self.role_hierarchy_cache: Dict[str, Set[str]] = {}
        
        # Initialize default permissions and roles
        self._initialize_default_permissions()
        self._initialize_default_roles()
        self._initialize_default_policies()
        
        logger.info("Authorization Engine initialized with enterprise security")

    def _initialize_default_permissions(self) -> None:
        """Initialize default system permissions"""
        try:
            default_permissions = [
                # User management permissions
                Permission("user_read", "Read User", "View user information", 
                         PermissionType.READ, ResourceType.USER),
                Permission("user_write", "Write User", "Modify user information", 
                         PermissionType.WRITE, ResourceType.USER),
                Permission("user_delete", "Delete User", "Delete user account", 
                         PermissionType.DELETE, ResourceType.USER),
                
                # Content management permissions
                Permission("content_read", "Read Content", "View content", 
                         PermissionType.READ, ResourceType.CONTENT),
                Permission("content_create", "Create Content", "Create new content", 
                         PermissionType.CREATE, ResourceType.CONTENT),
                Permission("content_edit", "Edit Content", "Modify content", 
                         PermissionType.UPDATE, ResourceType.CONTENT),
                Permission("content_delete", "Delete Content", "Delete content", 
                         PermissionType.DELETE, ResourceType.CONTENT),
                Permission("content_publish", "Publish Content", "Publish content", 
                         PermissionType.PUBLISH, ResourceType.CONTENT),
                Permission("content_share", "Share Content", "Share content with others", 
                         PermissionType.SHARE, ResourceType.CONTENT),
                
                # Project management permissions
                Permission("project_read", "Read Project", "View project information", 
                         PermissionType.READ, ResourceType.PROJECT),
                Permission("project_create", "Create Project", "Create new project", 
                         PermissionType.CREATE, ResourceType.PROJECT),
                Permission("project_edit", "Edit Project", "Modify project", 
                         PermissionType.UPDATE, ResourceType.PROJECT),
                Permission("project_delete", "Delete Project", "Delete project", 
                         PermissionType.DELETE, ResourceType.PROJECT),
                Permission("project_admin", "Admin Project", "Full project administration", 
                         PermissionType.ADMIN, ResourceType.PROJECT),
                
                # Analytics permissions
                Permission("analytics_read", "Read Analytics", "View analytics data", 
                         PermissionType.READ, ResourceType.ANALYTICS),
                Permission("analytics_export", "Export Analytics", "Export analytics data", 
                         PermissionType.DOWNLOAD, ResourceType.ANALYTICS),
                
                # Billing permissions
                Permission("billing_read", "Read Billing", "View billing information", 
                         PermissionType.READ, ResourceType.BILLING),
                Permission("billing_admin", "Admin Billing", "Manage billing settings", 
                         PermissionType.ADMIN, ResourceType.BILLING),
                
                # System permissions
                Permission("system_admin", "System Admin", "Full system administration", 
                         PermissionType.ADMIN, ResourceType.SYSTEM),
                Permission("tenant_admin", "Tenant Admin", "Tenant administration", 
                         PermissionType.ADMIN, ResourceType.TENANT),
                
                # API permissions
                Permission("api_read", "API Read", "Read access via API", 
                         PermissionType.READ, ResourceType.API),
                Permission("api_write", "API Write", "Write access via API", 
                         PermissionType.WRITE, ResourceType.API),
            ]
            
            for permission in default_permissions:
                self.permissions[permission.permission_id] = permission
            
            logger.info(f"Initialized {len(default_permissions)} default permissions")
            
        except Exception as e:
            logger.error(f"Failed to initialize default permissions: {e}")

    def _initialize_default_roles(self) -> None:
        """Initialize default system roles with hierarchical structure"""
        try:
            # Define role hierarchy: super_admin -> tenant_admin -> creator -> user
            
            # Super Admin Role
            super_admin_role = Role(
                role_id="super_admin",
                name="Super Administrator",
                description="Full system access across all tenants",
                permissions={
                    "system_admin", "tenant_admin", "user_read", "user_write", "user_delete",
                    "content_read", "content_create", "content_edit", "content_delete", 
                    "content_publish", "content_share", "project_read", "project_create",
                    "project_edit", "project_delete", "project_admin", "analytics_read",
                    "analytics_export", "billing_read", "billing_admin", "api_read", "api_write"
                },
                is_system_role=True
            )
            
            # Tenant Admin Role
            tenant_admin_role = Role(
                role_id="tenant_admin",
                name="Tenant Administrator",
                description="Full access within tenant scope",
                permissions={
                    "tenant_admin", "user_read", "user_write", "content_read", "content_create",
                    "content_edit", "content_delete", "content_publish", "content_share",
                    "project_read", "project_create", "project_edit", "project_delete",
                    "project_admin", "analytics_read", "analytics_export", "billing_read",
                    "api_read", "api_write"
                },
                parent_roles={"super_admin"},
                is_system_role=True
            )
            
            # Creator Role
            creator_role = Role(
                role_id="creator",
                name="Content Creator",
                description="Creator with content management capabilities",
                permissions={
                    "user_read", "content_read", "content_create", "content_edit",
                    "content_delete", "content_publish", "content_share", "project_read",
                    "project_create", "project_edit", "project_delete", "analytics_read",
                    "api_read", "api_write"
                },
                parent_roles={"tenant_admin"},
                is_system_role=True
            )
            
            # Collaborator Role
            collaborator_role = Role(
                role_id="collaborator",
                name="Collaborator",
                description="Can collaborate on shared projects",
                permissions={
                    "user_read", "content_read", "content_create", "content_edit",
                    "content_share", "project_read", "project_edit", "analytics_read",
                    "api_read"
                },
                parent_roles={"creator"},
                is_system_role=True
            )
            
            # Viewer Role
            viewer_role = Role(
                role_id="viewer",
                name="Viewer",
                description="Read-only access to shared content",
                permissions={
                    "content_read", "project_read", "analytics_read"
                },
                parent_roles={"collaborator"},
                is_system_role=True
            )
            
            # User Role (Basic)
            user_role = Role(
                role_id="user",
                name="Basic User",
                description="Basic user with minimal permissions",
                permissions={
                    "user_read", "content_read"
                },
                parent_roles={"viewer"},
                is_system_role=True
            )
            
            roles = [super_admin_role, tenant_admin_role, creator_role, 
                    collaborator_role, viewer_role, user_role]
            
            for role in roles:
                self.roles[role.role_id] = role
                # Update child relationships
                for parent_role_id in role.parent_roles:
                    if parent_role_id in self.roles:
                        self.roles[parent_role_id].child_roles.add(role.role_id)
            
            # Build role hierarchy cache
            self._build_role_hierarchy_cache()
            
            logger.info(f"Initialized {len(roles)} default roles with hierarchy")
            
        except Exception as e:
            logger.error(f"Failed to initialize default roles: {e}")

    def _initialize_default_policies(self) -> None:
        """Initialize default ABAC policies"""
        try:
            # Creator Content Ownership Policy
            content_ownership_policy = AuthorizationPolicy(
                policy_id="creator_content_ownership",
                name="Creator Content Ownership",
                description="Creators have full access to their own content",
                effect=PolicyEffect.ALLOW,
                subjects={"role": ["creator"]},
                resources={"type": "content", "owner": "${user.id}"},
                actions=["content_*"],
                conditions={"ownership": "self"}
            )
            
            # Project Collaboration Policy
            project_collaboration_policy = AuthorizationPolicy(
                policy_id="project_collaboration",
                name="Project Collaboration Access",
                description="Collaborators can access shared projects",
                effect=PolicyEffect.ALLOW,
                subjects={"role": ["collaborator", "creator"]},
                resources={"type": "project", "collaborators": "${user.id}"},
                actions=["project_read", "project_edit", "content_read", "content_edit"],
                conditions={"collaboration": "member"}
            )
            
            # Tenant Isolation Policy
            tenant_isolation_policy = AuthorizationPolicy(
                policy_id="tenant_isolation",
                name="Tenant Data Isolation",
                description="Users can only access data within their tenant",
                effect=PolicyEffect.DENY,
                subjects={"tenant_id": "${user.tenant_id}"},
                resources={"tenant_id": "!${user.tenant_id}"},
                actions=["*"],
                conditions={"tenant_isolation": True},
                priority=200  # High priority
            )
            
            # Time-based Access Policy
            business_hours_policy = AuthorizationPolicy(
                policy_id="business_hours_access",
                name="Business Hours Access",
                description="Restrict admin actions to business hours",
                effect=PolicyEffect.CONDITIONAL,
                subjects={"role": ["tenant_admin"]},
                resources={"type": ["billing", "system"]},
                actions=["*_admin"],
                conditions={
                    "time_range": {"start": "09:00", "end": "18:00"},
                    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                }
            )
            
            policies = [content_ownership_policy, project_collaboration_policy,
                       tenant_isolation_policy, business_hours_policy]
            
            for policy in policies:
                self.authorization_policies[policy.policy_id] = policy
            
            logger.info(f"Initialized {len(policies)} default authorization policies")
            
        except Exception as e:
            logger.error(f"Failed to initialize default policies: {e}")

    async def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        """Main authorization method - evaluate request against all policies"""
        try:
            start_time = datetime.utcnow()
            
            # Check cache first
            cache_key = self._generate_cache_key(request)
            if cache_key in self.decision_cache:
                cached_decision = self.decision_cache[cache_key]
                if datetime.utcnow() - cached_decision.timestamp < self.cache_ttl:
                    cached_decision.cached = True
                    return cached_decision
            
            # Create decision object
            decision = AuthorizationDecision(
                decision_id=hashlib.md5(cache_key.encode()).hexdigest(),
                request=request,
                decision="deny"  # Default deny
            )
            
            # Evaluate RBAC permissions
            rbac_result = await self._evaluate_rbac(request, decision)
            
            # Evaluate ABAC policies
            abac_result = await self._evaluate_abac(request, decision)
            
            # Combine results (RBAC OR ABAC allows access)
            if rbac_result or abac_result:
                decision.decision = "allow"
            else:
                decision.decision = "deny"
            
            # Calculate evaluation time
            end_time = datetime.utcnow()
            decision.evaluation_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Cache decision
            self.decision_cache[cache_key] = decision
            
            # Add to audit trail
            self.authorization_decisions.append(decision)
            
            # Clean up old decisions (keep last 10000)
            if len(self.authorization_decisions) > 10000:
                self.authorization_decisions = self.authorization_decisions[-10000:]
            
            logger.debug(f"Authorization decision: {decision.decision} for user {request.user_id} "
                        f"on {request.resource_type.value}:{request.resource_id}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Authorization evaluation failed: {e}")
            # Return deny decision on error
            return AuthorizationDecision(
                decision_id="error",
                request=request,
                decision="deny",
                reasons=[f"Authorization error: {str(e)}"]
            )

    async def _evaluate_rbac(self, request: AuthorizationRequest, 
                           decision: AuthorizationDecision) -> bool:
        """Evaluate Role-Based Access Control"""
        try:
            user_roles = await self._get_user_roles(request.user_id, request.tenant_id)
            decision.applicable_roles = user_roles
            
            # Get all permissions for user roles (including inherited)
            user_permissions = set()
            for role_id in user_roles:
                role_permissions = await self._get_role_permissions(role_id)
                user_permissions.update(role_permissions)
            
            decision.applicable_permissions = list(user_permissions)
            
            # Check if user has required permission
            required_permission = f"{request.resource_type.value}_{request.action}"
            
            # Check exact permission match
            if required_permission in user_permissions:
                decision.reasons.append(f"RBAC: User has permission {required_permission}")
                return True
            
            # Check wildcard permissions
            wildcard_permission = f"{request.resource_type.value}_*"
            if wildcard_permission in user_permissions:
                decision.reasons.append(f"RBAC: User has wildcard permission {wildcard_permission}")
                return True
            
            # Check admin permissions
            if "system_admin" in user_permissions:
                decision.reasons.append("RBAC: User has system admin permission")
                return True
            
            if f"{request.resource_type.value}_admin" in user_permissions:
                decision.reasons.append(f"RBAC: User has {request.resource_type.value} admin permission")
                return True
            
            decision.reasons.append(f"RBAC: User lacks required permission {required_permission}")
            return False
            
        except Exception as e:
            logger.error(f"RBAC evaluation failed: {e}")
            decision.reasons.append(f"RBAC evaluation error: {str(e)}")
            return False

    async def _evaluate_abac(self, request: AuthorizationRequest,
                           decision: AuthorizationDecision) -> bool:
        """Evaluate Attribute-Based Access Control"""
        try:
            # Sort policies by priority (highest first)
            sorted_policies = sorted(
                [p for p in self.authorization_policies.values() if p.is_active],
                key=lambda x: x.priority,
                reverse=True
            )
            
            for policy in sorted_policies:
                if await self._policy_applies(policy, request):
                    decision.applicable_policies.append(policy.policy_id)
                    
                    if policy.effect == PolicyEffect.ALLOW:
                        decision.reasons.append(f"ABAC: Policy {policy.name} grants access")
                        return True
                    elif policy.effect == PolicyEffect.DENY:
                        decision.reasons.append(f"ABAC: Policy {policy.name} denies access")
                        return False
                    elif policy.effect == PolicyEffect.CONDITIONAL:
                        # Evaluate conditions
                        if await self._evaluate_policy_conditions(policy, request):
                            decision.reasons.append(f"ABAC: Conditional policy {policy.name} grants access")
                            return True
                        else:
                            decision.reasons.append(f"ABAC: Conditional policy {policy.name} conditions not met")
            
            decision.reasons.append("ABAC: No applicable policies found")
            return False
            
        except Exception as e:
            logger.error(f"ABAC evaluation failed: {e}")
            decision.reasons.append(f"ABAC evaluation error: {str(e)}")
            return False

    async def _policy_applies(self, policy: AuthorizationPolicy, 
                            request: AuthorizationRequest) -> bool:
        """Check if policy applies to the request"""
        try:
            # Check subject attributes
            if policy.subjects:
                user_roles = await self._get_user_roles(request.user_id, request.tenant_id)
                if "role" in policy.subjects:
                    required_roles = policy.subjects["role"]
                    if not any(role in user_roles for role in required_roles):
                        return False
                
                if "tenant_id" in policy.subjects:
                    tenant_pattern = policy.subjects["tenant_id"]
                    if not self._match_attribute(request.tenant_id, tenant_pattern, request):
                        return False
            
            # Check resource attributes
            if policy.resources:
                if "type" in policy.resources:
                    resource_types = policy.resources["type"]
                    if isinstance(resource_types, str):
                        resource_types = [resource_types]
                    if request.resource_type.value not in resource_types:
                        return False
                
                if "owner" in policy.resources:
                    owner_pattern = policy.resources["owner"]
                    resource_owner = request.resource_attributes.get("owner")
                    if not self._match_attribute(resource_owner, owner_pattern, request):
                        return False
                
                if "collaborators" in policy.resources:
                    collaborators_pattern = policy.resources["collaborators"]
                    collaborators = request.resource_attributes.get("collaborators", [])
                    if not self._match_attribute(request.user_id, collaborators_pattern, request, collaborators):
                        return False
            
            # Check action patterns
            if policy.actions:
                action_match = False
                for action_pattern in policy.actions:
                    if fnmatch.fnmatch(f"{request.resource_type.value}_{request.action}", action_pattern):
                        action_match = True
                        break
                if not action_match:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check policy applicability: {e}")
            return False

    async def _evaluate_policy_conditions(self, policy: AuthorizationPolicy,
                                        request: AuthorizationRequest) -> bool:
        """Evaluate policy conditions"""
        try:
            if not policy.conditions:
                return True
            
            # Time-based conditions
            if "time_range" in policy.conditions:
                time_condition = policy.conditions["time_range"]
                current_time = datetime.utcnow().time()
                start_time = datetime.strptime(time_condition["start"], "%H:%M").time()
                end_time = datetime.strptime(time_condition["end"], "%H:%M").time()
                
                if not (start_time <= current_time <= end_time):
                    return False
            
            if "days" in policy.conditions:
                allowed_days = policy.conditions["days"]
                current_day = datetime.utcnow().strftime("%A").lower()
                if current_day not in allowed_days:
                    return False
            
            # Ownership conditions
            if "ownership" in policy.conditions:
                if policy.conditions["ownership"] == "self":
                    resource_owner = request.resource_attributes.get("owner")
                    if resource_owner != request.user_id:
                        return False
            
            # Collaboration conditions
            if "collaboration" in policy.conditions:
                if policy.conditions["collaboration"] == "member":
                    collaborators = request.resource_attributes.get("collaborators", [])
                    if request.user_id not in collaborators:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to evaluate policy conditions: {e}")
            return False

    async def assign_role_to_user(self, user_id: str, role_id: str, 
                                tenant_id: str = None, assigned_by: str = "",
                                valid_until: datetime = None) -> bool:
        """Assign role to user"""
        try:
            if role_id not in self.roles:
                logger.warning(f"Role {role_id} not found")
                return False
            
            # Check if assignment already exists
            existing_assignments = self.user_role_assignments.get(user_id, [])
            for assignment in existing_assignments:
                if (assignment.role_id == role_id and 
                    assignment.tenant_id == tenant_id and 
                    assignment.is_active):
                    logger.warning(f"User {user_id} already has role {role_id}")
                    return False
            
            # Create new assignment
            assignment = UserRoleAssignment(
                assignment_id=f"{user_id}_{role_id}_{int(datetime.utcnow().timestamp())}",
                user_id=user_id,
                role_id=role_id,
                tenant_id=tenant_id,
                valid_until=valid_until,
                assigned_by=assigned_by
            )
            
            self.user_role_assignments[user_id].append(assignment)
            
            # Clear role hierarchy cache for this user
            if user_id in self.role_hierarchy_cache:
                del self.role_hierarchy_cache[user_id]
            
            logger.info(f"Role {role_id} assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign role {role_id} to user {user_id}: {e}")
            return False

    async def _get_user_roles(self, user_id: str, tenant_id: str = None) -> List[str]:
        """Get all roles for user including inherited roles"""
        try:
            cache_key = f"{user_id}_{tenant_id}"
            if cache_key in self.role_hierarchy_cache:
                return list(self.role_hierarchy_cache[cache_key])
            
            direct_roles = set()
            current_time = datetime.utcnow()
            
            # Get direct role assignments
            for assignment in self.user_role_assignments.get(user_id, []):
                if (assignment.is_active and
                    (assignment.tenant_id == tenant_id or tenant_id is None) and
                    assignment.valid_from <= current_time and
                    (assignment.valid_until is None or assignment.valid_until > current_time)):
                    direct_roles.add(assignment.role_id)
            
            # Get inherited roles through hierarchy
            all_roles = set(direct_roles)
            for role_id in direct_roles:
                inherited_roles = await self._get_inherited_roles(role_id)
                all_roles.update(inherited_roles)
            
            # Cache result
            self.role_hierarchy_cache[cache_key] = all_roles
            
            return list(all_roles)
            
        except Exception as e:
            logger.error(f"Failed to get user roles for {user_id}: {e}")
            return []

    async def _get_inherited_roles(self, role_id: str) -> Set[str]:
        """Get all inherited roles through parent hierarchy"""
        try:
            inherited_roles = set()
            
            if role_id in self.roles:
                role = self.roles[role_id]
                for parent_role_id in role.parent_roles:
                    inherited_roles.add(parent_role_id)
                    # Recursively get parent's parents
                    parent_inherited = await self._get_inherited_roles(parent_role_id)
                    inherited_roles.update(parent_inherited)
            
            return inherited_roles
            
        except Exception as e:
            logger.error(f"Failed to get inherited roles for {role_id}: {e}")
            return set()

    async def _get_role_permissions(self, role_id: str) -> Set[str]:
        """Get all permissions for role including inherited permissions"""
        try:
            if role_id not in self.roles:
                return set()
            
            role = self.roles[role_id]
            all_permissions = set(role.permissions)
            
            # Get permissions from parent roles
            for parent_role_id in role.parent_roles:
                parent_permissions = await self._get_role_permissions(parent_role_id)
                all_permissions.update(parent_permissions)
            
            return all_permissions
            
        except Exception as e:
            logger.error(f"Failed to get role permissions for {role_id}: {e}")
            return set()

    def _match_attribute(self, value: Any, pattern: str, request: AuthorizationRequest,
                        collection: List[Any] = None) -> bool:
        """Match attribute value against pattern with variable substitution"""
        try:
            # Variable substitution
            if pattern.startswith("${"):
                if pattern == "${user.id}":
                    return value == request.user_id
                elif pattern == "${user.tenant_id}":
                    return value == request.tenant_id
                elif pattern.startswith("!${"):
                    # Negation
                    positive_pattern = pattern[1:]  # Remove '!'
                    return not self._match_attribute(value, positive_pattern, request, collection)
            
            # Collection membership check
            if collection is not None:
                if pattern == "${user.id}":
                    return request.user_id in collection
            
            # Direct match
            return value == pattern
            
        except Exception as e:
            logger.error(f"Failed to match attribute: {e}")
            return False

    def _generate_cache_key(self, request: AuthorizationRequest) -> str:
        """Generate cache key for authorization request"""
        return f"{request.user_id}:{request.action}:{request.resource_type.value}:{request.resource_id}:{request.tenant_id}"

    def _build_role_hierarchy_cache(self) -> None:
        """Build role hierarchy cache for performance"""
        try:
            self.role_hierarchy_cache.clear()
            # Cache will be built on-demand in _get_user_roles
            logger.info("Role hierarchy cache cleared for rebuild")
            
        except Exception as e:
            logger.error(f"Failed to build role hierarchy cache: {e}")

    async def get_authorization_statistics(self) -> Dict[str, Any]:
        """Get authorization engine statistics"""
        try:
            return {
                "total_permissions": len(self.permissions),
                "total_roles": len(self.roles),
                "system_roles": len([r for r in self.roles.values() if r.is_system_role]),
                "custom_roles": len([r for r in self.roles.values() if not r.is_system_role]),
                "total_policies": len(self.authorization_policies),
                "active_policies": len([p for p in self.authorization_policies.values() if p.is_active]),
                "total_user_assignments": sum(len(assignments) for assignments in self.user_role_assignments.values()),
                "active_user_assignments": sum(
                    len([a for a in assignments if a.is_active])
                    for assignments in self.user_role_assignments.values()
                ),
                "cache_entries": len(self.decision_cache),
                "decisions_24h": len([
                    d for d in self.authorization_decisions
                    if d.timestamp > datetime.utcnow() - timedelta(days=1)
                ]),
                "allow_decisions_24h": len([
                    d for d in self.authorization_decisions
                    if (d.timestamp > datetime.utcnow() - timedelta(days=1) and d.decision == "allow")
                ]),
                "deny_decisions_24h": len([
                    d for d in self.authorization_decisions
                    if (d.timestamp > datetime.utcnow() - timedelta(days=1) and d.decision == "deny")
                ]),
                "average_evaluation_time_ms": sum(
                    d.evaluation_time_ms for d in self.authorization_decisions[-1000:]
                ) / min(len(self.authorization_decisions), 1000) if self.authorization_decisions else 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get authorization statistics: {e}")
            return {"error": str(e)}


# Factory function for easier instantiation
def create_authorization_engine() -> AuthorizationEngine:
    """Factory function to create an Authorization Engine"""
    return AuthorizationEngine()


# Example usage and testing
async def main():
    """Example usage of Authorization Engine"""
    auth_engine = create_authorization_engine()
    
    # Assign role to test user
    await auth_engine.assign_role_to_user(
        user_id="creator_001",
        role_id="creator",
        tenant_id="tenant_001",
        assigned_by="system"
    )
    
    # Test authorization request
    request = AuthorizationRequest(
        request_id="test_001",
        user_id="creator_001",
        action="read",
        resource_type=ResourceType.CONTENT,
        resource_id="content_123",
        tenant_id="tenant_001",
        resource_attributes={"owner": "creator_001"}
    )
    
    decision = await auth_engine.authorize(request)
    print(f"Authorization Decision: {decision.decision}")
    print(f"Reasons: {decision.reasons}")
    
    # Get statistics
    stats = await auth_engine.get_authorization_statistics()
    print(f"Authorization Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())