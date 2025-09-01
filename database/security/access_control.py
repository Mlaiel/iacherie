"""Database Access Control Manager

Enterprise-grade database access control system with role-based permissions,
fine-grained access policies, and advanced security monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced access control architecture
- ML Engineer: AI-driven access pattern analysis
- DBA: Database permission optimization
- Security Expert: Enterprise access policies
- Microservices: Distributed access control
- Audio Engineer: Audio data access protection
- DevOps: Secure access deployment
- IA Prompt Engineer: AI access control prompts

Contact: mlaiel@live.de
⚠️ LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""

import asyncio
import logging
import time
import json
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid
import secrets

# Configure logging
logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """
Database access levels"""

    NONE = 0
    READ = 1
    WRITE = 2
    UPDATE = 3
    DELETE = 4
    ADMIN = 5
    SUPER_ADMIN = 99


class PermissionType(Enum):
    """
Permission types"""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    EXECUTE = "EXECUTE"
    CONNECT = "CONNECT"


class ResourceType(Enum):
    """Database resource types"""

    DATABASE = "database"
    SCHEMA = "schema"
    TABLE = "table"
    COLUMN = "column"
    ROW = "row"
    VIEW = "view"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    TRIGGER = "trigger"


class PolicyEffect(Enum):
    """Access policy effects"""

    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"


class AuthenticationMethod(Enum):
    """Authentication methods"""

    PASSWORD = "password"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"
    MFA = "mfa"


@dataclass
class Principal:
    """Access control principal (user, role, service)"""
    principal_id: str
    principal_type: str  # user, role, service, group
    name: str
    authentication_method: AuthenticationMethod
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_access: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Permission:
    """
Database permission definition"""
    permission_id: str
    permission_type: PermissionType
    resource_type: ResourceType
    resource_name: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    granted_at: datetime = field(default_factory=datetime.now)
    granted_by: str = ""
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessPolicy:
    """Access control policy"""
    policy_id: str
    name: str
    description: str
    effect: PolicyEffect
    principals: List[str]  # Principal IDs
    resources: List[str]  # Resource patterns
    actions: List[PermissionType]
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    """
Access request context"""
    request_id: str
    principal_id: str
    resource_type: ResourceType
    resource_name: str
    action: PermissionType
    timestamp: datetime = field(default_factory=datetime.now)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessDecision:
    """
Access control decision"""
    request_id: str
    decision: PolicyEffect
    reason: str
    applicable_policies: List[str]
    evaluation_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AccessMetrics:
    """
Access control metrics and monitoring"""
    
    def __init__(self):
        self.total_requests: int = 0
        self.allowed_requests: int = 0
        self.denied_requests: int = 0
        self.policy_evaluations: int = 0
        self.average_evaluation_time: float = 0.0
        self.failed_authentications: int = 0
        self.access_violations: List[Dict[str, Any]] = []
        self.principal_activity: Dict[str, int] = {}
        
    def record_access_decision(self, decision: AccessDecision):
        """
Record access control decision"""
        self.total_requests += 1
        
        if decision.decision == PolicyEffect.ALLOW:
            self.allowed_requests += 1
        else:
            self.denied_requests += 1
        
        # Update average evaluation time
        self.average_evaluation_time = (
            (self.average_evaluation_time * (self.total_requests - 1) + decision.evaluation_time)
            / self.total_requests
        )
        
        self.policy_evaluations += len(decision.applicable_policies)


class DatabaseAccessControl:
    """
    Enterprise-grade database access control manager
    
    Provides comprehensive access control capabilities including:
    - Role-based access control (RBAC)
    - Attribute-based access control (ABAC)
    - Policy-based access control
    - Dynamic permission evaluation
    - Access monitoring and auditing
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize access control manager"""
        self.config = config or {}
        self.principals: Dict[str, Principal] = {}
        self.permissions: Dict[str, Permission] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.role_hierarchy: Dict[str, Set[str]] = {}
        self.metrics = AccessMetrics()
        
        # Configuration
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        self.max_policy_evaluation_time = self.config.get("max_evaluation_time", 1.0)
        self.enable_policy_caching = self.config.get("enable_caching", True)
        self.require_mfa_for_admin = self.config.get("require_mfa_admin", True)
        
        # Initialize default roles and policies
        self._initialize_default_setup()
        
        logger.info("Database access control manager initialized successfully")
    
    def _initialize_default_setup(self):
        """Initialize default roles, permissions, and policies"""
        try:
            # Create default roles
            default_roles = [
                ("guest", "Guest user with read-only access"),
                ("user", "Regular user with basic access"),
                ("creator", "Content creator with upload permissions"),
                ("moderator", "Content moderator with review permissions"),
                ("admin", "Administrator with elevated privileges"),
                ("super_admin", "Super administrator with full access")
            ]
            
            for role_id, description in default_roles:
                if role_id not in self.principals:
                    role = Principal(
                        principal_id=role_id,
                        principal_type="role",
                        name=role_id.title(),
                        authentication_method=AuthenticationMethod.JWT_TOKEN,
                        attributes={"description": description}
                    )
                    self.principals[role_id] = role
            
            # Create role hierarchy
            self.role_hierarchy = {
                "super_admin": {"admin", "moderator", "creator", "user", "guest"},
                "admin": {"moderator", "creator", "user", "guest"},
                "moderator": {"creator", "user", "guest"},
                "creator": {"user", "guest"},
                "user": {"guest"},
                "guest": set()
            }
            
            # Create default policies
            self._create_default_policies()
            
            logger.info("Default access control setup completed")
            
        except Exception as e:
            logger.error(f"Default setup initialization error: {e}")
            raise
    
    def _create_default_policies(self):
        """Create default access control policies"""
        # Guest policy - read-only access to public data
        guest_policy = AccessPolicy(
            policy_id="policy_guest_read",
            name="Guest Read Access",
            description="Allow guests to read public content",
            effect=PolicyEffect.ALLOW,
            principals=["guest"],
            resources=["public_*", "content.public_*"],
            actions=[PermissionType.SELECT, PermissionType.CONNECT],
            conditions={"resource_visibility": "public"}
        )
        self.policies[guest_policy.policy_id] = guest_policy
        
        # User policy - basic user access
        user_policy = AccessPolicy(
            policy_id="policy_user_basic",
            name="User Basic Access",
            description="Allow users basic access to their own data",
            effect=PolicyEffect.ALLOW,
            principals=["user"],
            resources=["user_data.*", "content.user_*"],
            actions=[PermissionType.SELECT, PermissionType.INSERT, PermissionType.UPDATE],
            conditions={"owner_match": True}
        )
        self.policies[user_policy.policy_id] = user_policy
        
        # Creator policy - content creation and management
        creator_policy = AccessPolicy(
            policy_id="policy_creator_content",
            name="Creator Content Access",
            description="Allow creators to manage their content",
            effect=PolicyEffect.ALLOW,
            principals=["creator"],
            resources=["content.*", "fingerprints.*", "protection.*"],
            actions=[PermissionType.SELECT, PermissionType.INSERT, 
                    PermissionType.UPDATE, PermissionType.DELETE],
            conditions={"creator_owned": True}
        )
        self.policies[creator_policy.policy_id] = creator_policy
        
        # Admin policy - administrative access
        admin_policy = AccessPolicy(
            policy_id="policy_admin_manage",
            name="Admin Management Access",
            description="Allow admins to manage system resources",
            effect=PolicyEffect.ALLOW,
            principals=["admin"],
            resources=["system.*", "users.*", "analytics.*"],
            actions=[PermissionType.SELECT, PermissionType.INSERT, 
                    PermissionType.UPDATE, PermissionType.DELETE, PermissionType.ALTER],
            conditions={"admin_scope": True}
        )
        self.policies[admin_policy.policy_id] = admin_policy
        
        # Security policy - deny sensitive operations without MFA
        security_policy = AccessPolicy(
            policy_id="policy_security_mfa",
            name="MFA Required for Sensitive Operations",
            description="Require MFA for sensitive administrative operations",
            effect=PolicyEffect.DENY,
            principals=["admin", "super_admin"],
            resources=["security.*", "encryption.*", "backup.*"],
            actions=[PermissionType.DELETE, PermissionType.DROP, PermissionType.ALTER],
            conditions={"mfa_verified": False},
            priority=10  # High priority
        )
        self.policies[security_policy.policy_id] = security_policy
    
    async def authenticate_principal(
        self,
        principal_id: str,
        credentials: Dict[str, Any],
        authentication_method: AuthenticationMethod
    ) -> bool:
        """
        Authenticate principal with provided credentials
        
        Args:
            principal_id: Principal identifier
            credentials: Authentication credentials
            authentication_method: Authentication method to use
            
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Check if principal exists
            if principal_id not in self.principals:
                logger.warning(f"Authentication attempt for unknown principal: {principal_id}")
                self.metrics.failed_authentications += 1
                return False
            
            principal = self.principals[principal_id]
            
            # Check if principal is active
            if not principal.is_active:
                logger.warning(f"Authentication attempt for inactive principal: {principal_id}")
                self.metrics.failed_authentications += 1
                return False
            
            # Perform authentication based on method
            if authentication_method == AuthenticationMethod.PASSWORD:
                return await self._authenticate_password(principal, credentials)
            elif authentication_method == AuthenticationMethod.API_KEY:
                return await self._authenticate_api_key(principal, credentials)
            elif authentication_method == AuthenticationMethod.JWT_TOKEN:
                return await self._authenticate_jwt(principal, credentials)
            elif authentication_method == AuthenticationMethod.OAUTH2:
                return await self._authenticate_oauth2(principal, credentials)
            elif authentication_method == AuthenticationMethod.MFA:
                return await self._authenticate_mfa(principal, credentials)
            else:
                logger.error(f"Unsupported authentication method: {authentication_method}")
                self.metrics.failed_authentications += 1
                return False
                
        except Exception as e:
            logger.error(f"Authentication error for principal {principal_id}: {e}")
            self.metrics.failed_authentications += 1
            return False
    
    async def _authenticate_password(self, principal: Principal, credentials: Dict[str, Any]) -> bool:
        """Authenticate using password"""
        password = credentials.get("password")
        stored_hash = principal.attributes.get("password_hash")
        
        if not password or not stored_hash:
            return False
        
        # In production, use proper password hashing (bcrypt, scrypt, etc.)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(password_hash, stored_hash)
    
    async def _authenticate_api_key(self, principal: Principal, credentials: Dict[str, Any]) -> bool:
        """Authenticate using API key"""
        api_key = credentials.get("api_key")
        stored_key = principal.attributes.get("api_key")
        
        if not api_key or not stored_key:
            return False
        
        return hmac.compare_digest(api_key, stored_key)
    
    async def _authenticate_jwt(self, principal: Principal, credentials: Dict[str, Any]) -> bool:
        """Authenticate using JWT token"""
        # JWT validation would be implemented here
        # For now, just check if token is present
        token = credentials.get("jwt_token")
        return token is not None
    
    async def _authenticate_oauth2(self, principal: Principal, credentials: Dict[str, Any]) -> bool:
        """Authenticate using OAuth2"""
        # OAuth2 validation would be implemented here
        access_token = credentials.get("access_token")
        return access_token is not None
    
    async def _authenticate_mfa(self, principal: Principal, credentials: Dict[str, Any]) -> bool:
        """Authenticate using MFA"""
        # MFA validation would be implemented here
        mfa_token = credentials.get("mfa_token")
        base_auth = credentials.get("base_authenticated", False)
        return mfa_token is not None and base_auth
    
    async def check_access(self, request: AccessRequest) -> AccessDecision:
        """
        Check access permissions for a request
        
        Args:
            request: Access request to evaluate
            
        Returns:
            AccessDecision with allow/deny result and reasoning
        """
        start_time = time.time()
        
        try:
            # Check if principal exists and is active
            if request.principal_id not in self.principals:
                decision = AccessDecision(
                    request_id=request.request_id,
                    decision=PolicyEffect.DENY,
                    reason="Unknown principal",
                    applicable_policies=[],
                    evaluation_time=time.time() - start_time
                )
                self.metrics.record_access_decision(decision)
                return decision
            
            principal = self.principals[request.principal_id]
            if not principal.is_active:
                decision = AccessDecision(
                    request_id=request.request_id,
                    decision=PolicyEffect.DENY,
                    reason="Inactive principal",
                    applicable_policies=[],
                    evaluation_time=time.time() - start_time
                )
                self.metrics.record_access_decision(decision)
                return decision
            
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(request, principal)
            
            # Evaluate policies in priority order
            decision_result = await self._evaluate_policies(request, applicable_policies)
            
            # Create access decision
            decision = AccessDecision(
                request_id=request.request_id,
                decision=decision_result["effect"],
                reason=decision_result["reason"],
                applicable_policies=[p.policy_id for p in applicable_policies],
                evaluation_time=time.time() - start_time
            )
            
            # Update principal activity
            self.metrics.principal_activity[request.principal_id] = (
                self.metrics.principal_activity.get(request.principal_id, 0) + 1
            )
            
            # Record metrics
            self.metrics.record_access_decision(decision)
            
            # Log access decision
            await self._log_access_decision(request, decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Access check error for request {request.request_id}: {e}")
            
            # Return deny decision on error
            decision = AccessDecision(
                request_id=request.request_id,
                decision=PolicyEffect.DENY,
                reason=f"Evaluation error: {str(e)}",
                applicable_policies=[],
                evaluation_time=time.time() - start_time
            )
            self.metrics.record_access_decision(decision)
            return decision
    
    async def _get_applicable_policies(
        self, 
        request: AccessRequest, 
        principal: Principal
    ) -> List[AccessPolicy]:
        """Get policies applicable to the access request"""
        applicable_policies = []
        
        # Get principal roles (including inherited roles)
        principal_roles = await self._get_principal_roles(principal.principal_id)
        
        for policy in self.policies.values():
            if not policy.is_active:
                continue
            
            # Check if policy applies to principal or their roles
            if (principal.principal_id in policy.principals or 
                any(role in policy.principals for role in principal_roles)):
                
                # Check if policy applies to the resource
                if await self._resource_matches_policy(request.resource_name, policy.resources):
                    
                    # Check if policy applies to the action
                    if request.action in policy.actions:
                        applicable_policies.append(policy)
        
        # Sort by priority (lower number = higher priority)
        applicable_policies.sort(key=lambda p: p.priority)
        
        return applicable_policies
    
    async def _get_principal_roles(self, principal_id: str) -> Set[str]:
        """
Get all roles for a principal including inherited roles"""
        roles = set()
        
        principal = self.principals.get(principal_id)
        if not principal:
            return roles
        
        # If principal is a role, get inherited roles
        if principal.principal_type == "role":
            roles.add(principal_id)
            roles.update(self.role_hierarchy.get(principal_id, set()))
        else:
            # For users, get assigned roles
            assigned_roles = principal.attributes.get("roles", [])
            for role in assigned_roles:
                roles.add(role)
                roles.update(self.role_hierarchy.get(role, set()))
        
        return roles
    
    async def _resource_matches_policy(self, resource_name: str, policy_resources: List[str]) -> bool:
        """Check if resource matches any policy resource pattern"""
        for pattern in policy_resources:
            if await self._match_resource_pattern(resource_name, pattern):
                return True
        return False
    
    async def _match_resource_pattern(self, resource_name: str, pattern: str) -> bool:
        """
Match resource name against pattern (supports wildcards)"""
        if pattern == "*":
            return True
        
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return resource_name.startswith(prefix)
        
        if pattern.startswith("*"):
            suffix = pattern[1:]
            return resource_name.endswith(suffix)
        
        return resource_name == pattern
    
    async def _evaluate_policies(
        self, 
        request: AccessRequest, 
        policies: List[AccessPolicy]
    ) -> Dict[str, Any]:
        """Evaluate policies and return decision"""
        
        # Default to deny
        final_decision = PolicyEffect.DENY
        final_reason = "No applicable allow policies"
        
        # Check for explicit deny policies first (higher priority)
        for policy in policies:
            if policy.effect == PolicyEffect.DENY:
                # Check conditions
                if await self._evaluate_policy_conditions(request, policy):
                    return {
                        "effect": PolicyEffect.DENY,
                        "reason": f"Denied by policy: {policy.name}"
                    }
        
        # Check for allow policies
        for policy in policies:
            if policy.effect == PolicyEffect.ALLOW:
                # Check conditions
                if await self._evaluate_policy_conditions(request, policy):
                    final_decision = PolicyEffect.ALLOW
                    final_reason = f"Allowed by policy: {policy.name}"
                    break
        
        return {
            "effect": final_decision,
            "reason": final_reason
        }
    
    async def _evaluate_policy_conditions(
        self, 
        request: AccessRequest, 
        policy: AccessPolicy
    ) -> bool:
        """Evaluate policy conditions"""
        if not policy.conditions:
            return True
        
        # Evaluate each condition
        for condition_key, condition_value in policy.conditions.items():
            
            if condition_key == "owner_match":
                # Check if user owns the resource
                if not await self._check_resource_ownership(request):
                    return False
            
            elif condition_key == "resource_visibility":
                # Check resource visibility level
                if not await self._check_resource_visibility(request, condition_value):
                    return False
            
            elif condition_key == "creator_owned":
                # Check if creator owns the content
                if not await self._check_creator_ownership(request):
                    return False
            
            elif condition_key == "admin_scope":
                # Check if operation is within admin scope
                if not await self._check_admin_scope(request):
                    return False
            
            elif condition_key == "mfa_verified":
                # Check if MFA is verified
                if not await self._check_mfa_verification(request, condition_value):
                    return False
            
            elif condition_key == "time_restriction":
                # Check time-based restrictions
                if not await self._check_time_restriction(request, condition_value):
                    return False
            
            elif condition_key == "ip_restriction":
                # Check IP-based restrictions
                if not await self._check_ip_restriction(request, condition_value):
                    return False
        
        return True
    
    async def _check_resource_ownership(self, request: AccessRequest) -> bool:
        """Check if principal owns the requested resource"""
        # This would query the database to check ownership
        # For now, return True as placeholder
        return True
    
    async def _check_resource_visibility(self, request: AccessRequest, required_visibility: str) -> bool:
        """
Check resource visibility level"""
        # This would check resource metadata for visibility
        return True
    
    async def _check_creator_ownership(self, request: AccessRequest) -> bool:
        """
Check if creator owns the content"""
        # This would verify creator ownership in content tables
        return True
    
    async def _check_admin_scope(self, request: AccessRequest) -> bool:
        """
Check if operation is within admin scope"""
        # This would verify admin permissions for the operation
        return True
    
    async def _check_mfa_verification(self, request: AccessRequest, required: bool) -> bool:
        """
Check MFA verification status"""
        mfa_verified = request.attributes.get("mfa_verified", False)
        return not required or mfa_verified
    
    async def _check_time_restriction(self, request: AccessRequest, restriction: Dict[str, Any]) -> bool:
        """Check time-based access restrictions"""
        # Implement time-based access control
        return True
    
    async def _check_ip_restriction(self, request: AccessRequest, restriction: Dict[str, Any]) -> bool:
        """
Check IP-based access restrictions"""
        # Implement IP-based access control
        return True
    
    async def _log_access_decision(self, request: AccessRequest, decision: AccessDecision):
        """
Log access control decision for audit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request.request_id,
            "principal_id": request.principal_id,
            "resource": f"{request.resource_type.value}:{request.resource_name}",
            "action": request.action.value,
            "decision": decision.decision.value,
            "reason": decision.reason,
            "source_ip": request.source_ip,
            "user_agent": request.user_agent,
            "evaluation_time": decision.evaluation_time,
            "applicable_policies": decision.applicable_policies
        }
        
        # In production, this would write to audit log system
        if decision.decision == PolicyEffect.DENY:
            logger.warning(f"Access denied: {log_entry}")
        else:
            logger.info(f"Access granted: {log_entry}")
    
    async def grant_permission(
        self,
        principal_id: str,
        permission: Permission,
        granted_by: str
    ) -> bool:
        """Grant permission to principal"""
        try:
            if principal_id not in self.principals:
                raise ValueError(f"Unknown principal: {principal_id}")
            
            permission.granted_by = granted_by
            permission_key = f"{principal_id}:{permission.permission_id}"
            self.permissions[permission_key] = permission
            
            logger.info(f"Permission granted: {permission.permission_type.value} on "
                       f"{permission.resource_type.value}:{permission.resource_name} "
                       f"to {principal_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Grant permission error: {e}")
            return False
    
    async def revoke_permission(
        self,
        principal_id: str,
        permission_id: str,
        revoked_by: str
    ) -> bool:
        """Revoke permission from principal"""
        try:
            permission_key = f"{principal_id}:{permission_id}"
            
            if permission_key not in self.permissions:
                logger.warning(f"Permission not found: {permission_key}")
                return False
            
            permission = self.permissions[permission_key]
            del self.permissions[permission_key]
            
            logger.info(f"Permission revoked: {permission.permission_type.value} on "
                       f"{permission.resource_type.value}:{permission.resource_name} "
                       f"from {principal_id} by {revoked_by}")
            
            return True
            
        except Exception as e:
            logger.error(f"Revoke permission error: {e}")
            return False
    
    async def add_principal_to_role(self, principal_id: str, role_id: str) -> bool:
        """Add principal to role"""
        try:
            if principal_id not in self.principals:
                raise ValueError(f"Unknown principal: {principal_id}")
            
            if role_id not in self.principals:
                raise ValueError(f"Unknown role: {role_id}")
            
            principal = self.principals[principal_id]
            roles = principal.attributes.get("roles", [])
            
            if role_id not in roles:
                roles.append(role_id)
                principal.attributes["roles"] = roles
                
                logger.info(f"Principal {principal_id} added to role {role_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Add principal to role error: {e}")
            return False
    
    async def remove_principal_from_role(self, principal_id: str, role_id: str) -> bool:
        """Remove principal from role"""
        try:
            if principal_id not in self.principals:
                raise ValueError(f"Unknown principal: {principal_id}")
            
            principal = self.principals[principal_id]
            roles = principal.attributes.get("roles", [])
            
            if role_id in roles:
                roles.remove(role_id)
                principal.attributes["roles"] = roles
                
                logger.info(f"Principal {principal_id} removed from role {role_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Remove principal from role error: {e}")
            return False
    
    def get_principal_permissions(self, principal_id: str) -> List[Permission]:
        """Get all permissions for a principal"""
        permissions = []
        
        for key, permission in self.permissions.items():
            if key.startswith(f"{principal_id}:"):
                permissions.append(permission)
        
        return permissions
    
    def get_access_metrics(self) -> Dict[str, Any]:
        """Get access control metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "allowed_requests": self.metrics.allowed_requests,
            "denied_requests": self.metrics.denied_requests,
            "success_rate": (
                self.metrics.allowed_requests / max(self.metrics.total_requests, 1) * 100
            ),
            "average_evaluation_time": self.metrics.average_evaluation_time,
            "failed_authentications": self.metrics.failed_authentications,
            "policy_evaluations": self.metrics.policy_evaluations,
            "active_principals": len([p for p in self.principals.values() if p.is_active]),
            "active_policies": len([p for p in self.policies.values() if p.is_active]),
            "principal_activity": dict(self.metrics.principal_activity)
        }


# Module initialization
logger.info("Database access control module loaded successfully")
