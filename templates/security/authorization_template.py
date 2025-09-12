"""{{auth_name}} Authorization Template for Ainflue Platform
{{auth_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Set
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json
import hashlib

from pydantic import BaseModel, Field, validator
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext

from core.config import get_settings
from core.database import get_db_session
from utils.exceptions import AuthorizationException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()


class PermissionType(Enum):
    """Permission types"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    CREATE = "create"
    UPDATE = "update"
    EXECUTE = "execute"
    MANAGE = "manage"


class ResourceType(Enum):
    """Resource types"""
    USER = "user"
    CONTENT = "content"
    COMMENT = "comment"
    MEDIA = "media"
    ANALYTICS = "analytics"
    SETTINGS = "settings"
    BILLING = "billing"
    API = "api"


class AccessLevel(Enum):
    """Access levels"""
    NONE = 0
    BASIC = 1
    STANDARD = 2
    PREMIUM = 3
    ADMIN = 4
    SUPER_ADMIN = 5


class PolicyEffect(Enum):
    """Policy effects"""
    ALLOW = "allow"
    DENY = "deny"


class ContextType(Enum):
    """Context types for authorization"""
    IP_ADDRESS = "ip_address"
    TIME_RANGE = "time_range"
    DEVICE_TYPE = "device_type"
    LOCATION = "location"
    USER_AGENT = "user_agent"


class Permission(BaseModel):
    """Permission model"""
    id: str = Field(..., description="Permission identifier")
    name: str = Field(..., description="Permission name")
    resource: ResourceType = Field(..., description="Resource type")
    action: PermissionType = Field(..., description="Permission type")
    description: Optional[str] = Field(None, description="Permission description")
    is_active: bool = Field(default=True, description="Whether permission is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Role(BaseModel):
    """Role model"""
    id: str = Field(..., description="Role identifier")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: List[Permission] = Field(default_factory=list, description="Role permissions")
    access_level: AccessLevel = Field(default=AccessLevel.BASIC, description="Access level")
    is_system_role: bool = Field(default=False, description="Whether it's a system role")
    is_active: bool = Field(default=True, description="Whether role is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    """User model for authorization"""
    id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    roles: List[Role] = Field(default_factory=list, description="User roles")
    direct_permissions: List[Permission] = Field(default_factory=list, description="Direct permissions")
    access_level: AccessLevel = Field(default=AccessLevel.BASIC, description="User access level")
    is_active: bool = Field(default=True, description="Whether user is active")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuthorizationContext(BaseModel):
    """Authorization context"""
    user: User = Field(..., description="User making the request")
    resource: str = Field(..., description="Resource being accessed")
    action: str = Field(..., description="Action being performed")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PolicyCondition(BaseModel):
    """Policy condition"""
    type: ContextType = Field(..., description="Condition type")
    operator: str = Field(..., description="Operator (eq, ne, in, not_in, gt, lt, etc.)")
    value: Any = Field(..., description="Condition value")
    description: Optional[str] = Field(None, description="Condition description")


class Policy(BaseModel):
    """Authorization policy"""
    id: str = Field(..., description="Policy identifier")
    name: str = Field(..., description="Policy name")
    description: Optional[str] = Field(None, description="Policy description")
    effect: PolicyEffect = Field(..., description="Policy effect")
    resources: List[str] = Field(..., description="Resources this policy applies to")
    actions: List[str] = Field(..., description="Actions this policy applies to")
    principals: List[str] = Field(default_factory=list, description="Users/roles this policy applies to")
    conditions: List[PolicyCondition] = Field(default_factory=list, description="Policy conditions")
    priority: int = Field(default=100, description="Policy priority (higher = more important)")
    is_active: bool = Field(default=True, description="Whether policy is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuthorizationDecision(BaseModel):
    """Authorization decision"""
    allowed: bool = Field(..., description="Whether access is allowed")
    reason: str = Field(..., description="Reason for the decision")
    applied_policies: List[str] = Field(default_factory=list, description="Policies that were applied")
    missing_permissions: List[str] = Field(default_factory=list, description="Missing permissions")
    context: Optional[Dict[str, Any]] = Field(None, description="Decision context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class {{auth_name}}Authorizer:
    """{{auth_description}} with comprehensive authorization capabilities"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        token_expire_hours: int = 24,
        cache_ttl: int = 300,
        enable_policy_caching: bool = True,
        metrics_collector: Optional[SecurityMetricsCollector] = None
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_hours = token_expire_hours
        self.cache_ttl = cache_ttl
        self.enable_policy_caching = enable_policy_caching
        self.metrics_collector = metrics_collector or SecurityMetricsCollector()
        
        # Initialize storage
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.policies: Dict[str, Policy] = {}
        
        # Initialize caches
        self.permission_cache: Dict[str, bool] = {}
        self.policy_cache: Dict[str, List[Policy]] = {}
        
        # Load default permissions and roles
        self._initialize_default_permissions()
        self._initialize_default_roles()
        
        logger.info("Authorization system initialized")
    
    def _initialize_default_permissions(self):
        """Initialize default permissions"""
        default_permissions = [
            # User permissions
            Permission(id="user:read", name="Read User", resource=ResourceType.USER, action=PermissionType.READ),
            Permission(id="user:write", name="Write User", resource=ResourceType.USER, action=PermissionType.WRITE),
            Permission(id="user:delete", name="Delete User", resource=ResourceType.USER, action=PermissionType.DELETE),
            Permission(id="user:manage", name="Manage Users", resource=ResourceType.USER, action=PermissionType.MANAGE),
            
            # Content permissions
            Permission(id="content:read", name="Read Content", resource=ResourceType.CONTENT, action=PermissionType.READ),
            Permission(id="content:create", name="Create Content", resource=ResourceType.CONTENT, action=PermissionType.CREATE),
            Permission(id="content:update", name="Update Content", resource=ResourceType.CONTENT, action=PermissionType.UPDATE),
            Permission(id="content:delete", name="Delete Content", resource=ResourceType.CONTENT, action=PermissionType.DELETE),
            Permission(id="content:manage", name="Manage Content", resource=ResourceType.CONTENT, action=PermissionType.MANAGE),
            
            # Analytics permissions
            Permission(id="analytics:read", name="Read Analytics", resource=ResourceType.ANALYTICS, action=PermissionType.READ),
            Permission(id="analytics:manage", name="Manage Analytics", resource=ResourceType.ANALYTICS, action=PermissionType.MANAGE),
            
            # Settings permissions
            Permission(id="settings:read", name="Read Settings", resource=ResourceType.SETTINGS, action=PermissionType.READ),
            Permission(id="settings:write", name="Write Settings", resource=ResourceType.SETTINGS, action=PermissionType.WRITE),
            Permission(id="settings:manage", name="Manage Settings", resource=ResourceType.SETTINGS, action=PermissionType.MANAGE),
            
            # API permissions
            Permission(id="api:read", name="API Read", resource=ResourceType.API, action=PermissionType.READ),
            Permission(id="api:write", name="API Write", resource=ResourceType.API, action=PermissionType.WRITE),
            Permission(id="api:admin", name="API Admin", resource=ResourceType.API, action=PermissionType.ADMIN),
        ]
        
        for permission in default_permissions:
            self.permissions[permission.id] = permission
    
    def _initialize_default_roles(self):
        """Initialize default roles"""
        # Basic User Role
        basic_permissions = [
            self.permissions["user:read"],
            self.permissions["content:read"],
            self.permissions["content:create"],
            self.permissions["api:read"]
        ]
        basic_role = Role(
            id="basic_user",
            name="Basic User",
            description="Basic user with minimal permissions",
            permissions=basic_permissions,
            access_level=AccessLevel.BASIC
        )
        
        # Premium User Role
        premium_permissions = basic_permissions + [
            self.permissions["content:update"],
            self.permissions["analytics:read"],
            self.permissions["api:write"]
        ]
        premium_role = Role(
            id="premium_user",
            name="Premium User",
            description="Premium user with enhanced permissions",
            permissions=premium_permissions,
            access_level=AccessLevel.PREMIUM
        )
        
        # Admin Role
        admin_permissions = list(self.permissions.values())
        admin_role = Role(
            id="admin",
            name="Administrator",
            description="Administrator with full permissions",
            permissions=admin_permissions,
            access_level=AccessLevel.ADMIN,
            is_system_role=True
        )
        
        self.roles["basic_user"] = basic_role
        self.roles["premium_user"] = premium_role
        self.roles["admin"] = admin_role
    
    async def authorize(self, context: AuthorizationContext) -> AuthorizationDecision:
        """Authorize a user action"""
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(context)
            
            # Check cache first
            if self.enable_policy_caching and cache_key in self.permission_cache:
                decision = AuthorizationDecision(
                    allowed=self.permission_cache[cache_key],
                    reason="Cached decision",
                    context={"cached": True}
                )
                return decision
            
            # Perform authorization
            decision = await self._perform_authorization(context)
            
            # Cache the decision
            if self.enable_policy_caching:
                self.permission_cache[cache_key] = decision.allowed
            
            # Record metrics
            await self.metrics_collector.record_authorization_check(
                user_id=context.user.id,
                resource=context.resource,
                action=context.action,
                allowed=decision.allowed,
                response_time=0  # Calculate if needed
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Authorization error: {e}")
            # Default to deny on error
            return AuthorizationDecision(
                allowed=False,
                reason=f"Authorization error: {str(e)}",
                context={"error": True}
            )
    
    async def _perform_authorization(self, context: AuthorizationContext) -> AuthorizationDecision:
        """Perform the actual authorization logic"""
        
        # Check if user is active
        if not context.user.is_active:
            return AuthorizationDecision(
                allowed=False,
                reason="User account is inactive"
            )
        
        # Get applicable policies
        applicable_policies = await self._get_applicable_policies(context)
        
        # Apply policies in priority order
        policy_results = []
        for policy in sorted(applicable_policies, key=lambda p: p.priority, reverse=True):
            result = await self._evaluate_policy(policy, context)
            policy_results.append((policy, result))
            
            # If we find an explicit deny, stop processing
            if policy.effect == PolicyEffect.DENY and result:
                return AuthorizationDecision(
                    allowed=False,
                    reason=f"Denied by policy: {policy.name}",
                    applied_policies=[policy.id]
                )
        
        # Check role-based permissions
        role_permissions = self._get_user_permissions(context.user)
        permission_key = f"{context.resource}:{context.action}"
        
        has_permission = any(
            perm.id == permission_key or 
            (perm.resource.value == context.resource.split(':')[0] and perm.action.value == context.action) or
            perm.action == PermissionType.ADMIN
            for perm in role_permissions
        )
        
        # Apply allow policies
        allow_policies = [p for p, result in policy_results if p.effect == PolicyEffect.ALLOW and result]
        
        if has_permission or allow_policies:
            return AuthorizationDecision(
                allowed=True,
                reason="Granted by role permissions" if has_permission else "Granted by policy",
                applied_policies=[p.id for p, _ in policy_results if _]
            )
        
        # Check for missing permissions
        missing_permissions = [permission_key] if not has_permission else []
        
        return AuthorizationDecision(
            allowed=False,
            reason="Insufficient permissions",
            missing_permissions=missing_permissions
        )
    
    async def _get_applicable_policies(self, context: AuthorizationContext) -> List[Policy]:
        """Get policies applicable to the authorization context"""
        applicable_policies = []
        
        for policy in self.policies.values():
            if not policy.is_active:
                continue
            
            # Check if policy applies to this resource
            if not any(resource in context.resource for resource in policy.resources):
                continue
            
            # Check if policy applies to this action
            if not any(action in context.action for action in policy.actions):
                continue
            
            # Check if policy applies to this user
            if policy.principals:
                user_matches = (
                    context.user.id in policy.principals or
                    context.user.username in policy.principals or
                    any(role.id in policy.principals for role in context.user.roles)
                )
                if not user_matches:
                    continue
            
            applicable_policies.append(policy)
        
        return applicable_policies
    
    async def _evaluate_policy(self, policy: Policy, context: AuthorizationContext) -> bool:
        """Evaluate if a policy applies to the context"""
        if not policy.conditions:
            return True
        
        for condition in policy.conditions:
            if not await self._evaluate_condition(condition, context):
                return False
        
        return True
    
    async def _evaluate_condition(self, condition: PolicyCondition, context: AuthorizationContext) -> bool:
        """Evaluate a single policy condition"""
        
        if condition.type == ContextType.IP_ADDRESS:
            client_ip = context.ip_address
            if condition.operator == "eq":
                return client_ip == condition.value
            elif condition.operator == "in":
                return client_ip in condition.value
            # Add more IP-based conditions as needed
        
        elif condition.type == ContextType.TIME_RANGE:
            current_time = context.timestamp.time()
            if condition.operator == "between":
                start_time, end_time = condition.value
                return start_time <= current_time <= end_time
        
        elif condition.type == ContextType.USER_AGENT:
            user_agent = context.user_agent
            if condition.operator == "contains":
                return condition.value in (user_agent or "")
        
        elif condition.type == ContextType.LOCATION:
            # Placeholder for location-based conditions
            return True
        
        # Default to true if condition type not recognized
        return True
    
    def _get_user_permissions(self, user: User) -> List[Permission]:
        """Get all permissions for a user"""
        permissions = list(user.direct_permissions)
        
        # Add permissions from roles
        for role in user.roles:
            if role.is_active:
                permissions.extend(role.permissions)
        
        # Remove duplicates
        unique_permissions = {}
        for perm in permissions:
            unique_permissions[perm.id] = perm
        
        return list(unique_permissions.values())
    
    def _generate_cache_key(self, context: AuthorizationContext) -> str:
        """Generate cache key for authorization context"""
        key_data = {
            "user_id": context.user.id,
            "resource": context.resource,
            "action": context.action,
            "timestamp": context.timestamp.strftime("%Y-%m-%d-%H")  # Hour-level caching
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def create_permission(self, permission: Permission) -> Permission:
        """Create a new permission"""
        if permission.id in self.permissions:
            raise AuthorizationException(f"Permission {permission.id} already exists")
        
        self.permissions[permission.id] = permission
        self._clear_cache()
        
        logger.info(f"Created permission: {permission.id}")
        return permission
    
    async def create_role(self, role: Role) -> Role:
        """Create a new role"""
        if role.id in self.roles:
            raise AuthorizationException(f"Role {role.id} already exists")
        
        self.roles[role.id] = role
        self._clear_cache()
        
        logger.info(f"Created role: {role.id}")
        return role
    
    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign a role to a user"""
        if user_id not in self.users:
            raise AuthorizationException(f"User {user_id} not found")
        
        if role_id not in self.roles:
            raise AuthorizationException(f"Role {role_id} not found")
        
        user = self.users[user_id]
        role = self.roles[role_id]
        
        # Check if user already has this role
        if not any(r.id == role_id for r in user.roles):
            user.roles.append(role)
            user.updated_at = datetime.utcnow()
            self._clear_cache()
            
            logger.info(f"Assigned role {role_id} to user {user_id}")
            return True
        
        return False
    
    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user"""
        if user_id not in self.users:
            raise AuthorizationException(f"User {user_id} not found")
        
        user = self.users[user_id]
        original_count = len(user.roles)
        user.roles = [r for r in user.roles if r.id != role_id]
        
        if len(user.roles) < original_count:
            user.updated_at = datetime.utcnow()
            self._clear_cache()
            
            logger.info(f"Removed role {role_id} from user {user_id}")
            return True
        
        return False
    
    async def create_policy(self, policy: Policy) -> Policy:
        """Create a new authorization policy"""
        if policy.id in self.policies:
            raise AuthorizationException(f"Policy {policy.id} already exists")
        
        self.policies[policy.id] = policy
        self._clear_cache()
        
        logger.info(f"Created policy: {policy.id}")
        return policy
    
    async def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> Optional[Policy]:
        """Update an existing policy"""
        if policy_id not in self.policies:
            return None
        
        policy = self.policies[policy_id]
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        policy.updated_at = datetime.utcnow()
        self._clear_cache()
        
        logger.info(f"Updated policy: {policy_id}")
        return policy
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Delete a policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            self._clear_cache()
            
            logger.info(f"Deleted policy: {policy_id}")
            return True
        
        return False
    
    async def check_permission(self, user_id: str, resource: str, action: str, **context_data) -> bool:
        """Simple permission check"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        auth_context = AuthorizationContext(
            user=user,
            resource=resource,
            action=action,
            context_data=context_data
        )
        
        decision = await self.authorize(auth_context)
        return decision.allowed
    
    def _clear_cache(self):
        """Clear authorization caches"""
        self.permission_cache.clear()
        self.policy_cache.clear()
    
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user"""
        if user_id not in self.users:
            return []
        
        return self._get_user_permissions(self.users[user_id])
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user"""
        if user_id not in self.users:
            return []
        
        return self.users[user_id].roles
    
    async def register_user(self, user: User) -> User:
        """Register a new user in the authorization system"""
        if user.id in self.users:
            raise AuthorizationException(f"User {user.id} already exists")
        
        # Assign default role if no roles specified
        if not user.roles:
            default_role = self.roles.get("basic_user")
            if default_role:
                user.roles = [default_role]
        
        self.users[user.id] = user
        self._clear_cache()
        
        logger.info(f"Registered user: {user.id}")
        return user
    
    async def get_authorization_stats(self) -> Dict[str, Any]:
        """Get authorization system statistics"""
        return {
            "users_count": len(self.users),
            "roles_count": len(self.roles),
            "permissions_count": len(self.permissions),
            "policies_count": len(self.policies),
            "cache_size": len(self.permission_cache),
            "active_users": len([u for u in self.users.values() if u.is_active]),
            "active_roles": len([r for r in self.roles.values() if r.is_active]),
            "active_policies": len([p for p in self.policies.values() if p.is_active])
        }


# Dependency for FastAPI
async def get_authorization_service() -> {{auth_name}}Authorizer:
    """Get authorization service instance"""
    return {{auth_name}}Authorizer(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        token_expire_hours=settings.ACCESS_TOKEN_EXPIRE_HOURS
    )


# Template usage example
def create_authorization_system_example():
    """Example of how to create and use the authorization system"""
    
    # Create authorizer
    authorizer = {{auth_name}}Authorizer(
        secret_key="your-secret-key",
        algorithm="HS256",
        token_expire_hours=24
    )
    
    return authorizer


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "authorization_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive authorization system with RBAC and policy-based access control",
    "required_parameters": [
        "auth_name",
        "auth_description",
        "author_name",
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_permissions",
        "custom_roles",
        "custom_policies",
        "custom_conditions"
    ],
    "dependencies": [
        "pydantic>=2.5.0",
        "fastapi>=0.104.1",
        "PyJWT>=2.8.0",
        "passlib[bcrypt]>=1.7.4"
    ],
    "features": [
        "Role-based access control (RBAC)",
        "Policy-based authorization",
        "Context-aware permissions",
        "Permission caching",
        "User management",
        "Role management",
        "Policy management",
        "Conditional access",
        "Audit logging",
        "Performance monitoring"
    ]
}