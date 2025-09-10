"""
Security Module - Access Controller
Advanced granular access control system for Ainflue Distribution Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Set, Union, Any
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import hashlib
import jwt
import redis.asyncio as redis

class Permission(Enum):
    """System permissions"""
    # Content permissions
    CONTENT_CREATE = "content:create"
    CONTENT_READ = "content:read"
    CONTENT_UPDATE = "content:update"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"
    
    # Distribution permissions
    DISTRIBUTION_SCHEDULE = "distribution:schedule"
    DISTRIBUTION_EXECUTE = "distribution:execute"
    DISTRIBUTION_MONITOR = "distribution:monitor"
    DISTRIBUTION_CANCEL = "distribution:cancel"
    
    # Platform permissions
    PLATFORM_CONNECT = "platform:connect"
    PLATFORM_CONFIGURE = "platform:configure"
    PLATFORM_DISCONNECT = "platform:disconnect"
    
    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_ADVANCED = "analytics:advanced"
    
    # User management permissions
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_IMPERSONATE = "user:impersonate"
    
    # Administrative permissions
    ADMIN_SYSTEM = "admin:system"
    ADMIN_SECURITY = "admin:security"
    ADMIN_BILLING = "admin:billing"
    ADMIN_SUPPORT = "admin:support"

class Role(Enum):
    """System roles with hierarchical permissions"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    CREATOR_PRO = "creator_pro"
    CREATOR_STANDARD = "creator_standard"
    CREATOR_BASIC = "creator_basic"
    VIEWER = "viewer"
    GUEST = "guest"

@dataclass
class AccessContext:
    """Access control context"""
    user_id: str
    roles: List[Role]
    permissions: Set[Permission]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    session_id: Optional[str] = None
    mfa_verified: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class AccessRequest:
    """Access request structure"""
    resource: str
    action: Permission
    context: AccessContext
    resource_owner_id: Optional[str] = None
    additional_checks: Optional[Dict[str, Any]] = None

@dataclass
class AccessResult:
    """Access control decision result"""
    granted: bool
    reason: str
    required_permissions: Set[Permission]
    missing_permissions: Set[Permission]
    additional_requirements: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

class AccessController:
    """
    Advanced granular access control system
    Supports RBAC, ABAC, and custom access policies
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.role_permissions = self._initialize_role_permissions()
        self.access_cache = {}
        self.policy_cache = {}
        
    def _initialize_role_permissions(self) -> Dict[Role, Set[Permission]]:
        """Initialize role-based permissions mapping"""
        return {
            Role.SUPER_ADMIN: set(Permission),  # All permissions
            Role.ADMIN: {
                Permission.CONTENT_CREATE, Permission.CONTENT_READ, Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE, Permission.CONTENT_PUBLISH,
                Permission.DISTRIBUTION_SCHEDULE, Permission.DISTRIBUTION_EXECUTE,
                Permission.DISTRIBUTION_MONITOR, Permission.DISTRIBUTION_CANCEL,
                Permission.PLATFORM_CONNECT, Permission.PLATFORM_CONFIGURE,
                Permission.PLATFORM_DISCONNECT, Permission.ANALYTICS_VIEW,
                Permission.ANALYTICS_EXPORT, Permission.ANALYTICS_ADVANCED,
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.USER_DELETE, Permission.ADMIN_SYSTEM, Permission.ADMIN_BILLING
            },
            Role.MANAGER: {
                Permission.CONTENT_CREATE, Permission.CONTENT_READ, Permission.CONTENT_UPDATE,
                Permission.CONTENT_PUBLISH, Permission.DISTRIBUTION_SCHEDULE,
                Permission.DISTRIBUTION_EXECUTE, Permission.DISTRIBUTION_MONITOR,
                Permission.PLATFORM_CONNECT, Permission.PLATFORM_CONFIGURE,
                Permission.ANALYTICS_VIEW, Permission.ANALYTICS_EXPORT,
                Permission.USER_READ, Permission.USER_UPDATE
            },
            Role.CREATOR_PRO: {
                Permission.CONTENT_CREATE, Permission.CONTENT_READ, Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE, Permission.CONTENT_PUBLISH,
                Permission.DISTRIBUTION_SCHEDULE, Permission.DISTRIBUTION_EXECUTE,
                Permission.DISTRIBUTION_MONITOR, Permission.PLATFORM_CONNECT,
                Permission.PLATFORM_CONFIGURE, Permission.ANALYTICS_VIEW,
                Permission.ANALYTICS_EXPORT, Permission.ANALYTICS_ADVANCED
            },
            Role.CREATOR_STANDARD: {
                Permission.CONTENT_CREATE, Permission.CONTENT_READ, Permission.CONTENT_UPDATE,
                Permission.CONTENT_DELETE, Permission.CONTENT_PUBLISH,
                Permission.DISTRIBUTION_SCHEDULE, Permission.DISTRIBUTION_EXECUTE,
                Permission.DISTRIBUTION_MONITOR, Permission.PLATFORM_CONNECT,
                Permission.ANALYTICS_VIEW, Permission.ANALYTICS_EXPORT
            },
            Role.CREATOR_BASIC: {
                Permission.CONTENT_CREATE, Permission.CONTENT_READ, Permission.CONTENT_UPDATE,
                Permission.CONTENT_PUBLISH, Permission.DISTRIBUTION_SCHEDULE,
                Permission.DISTRIBUTION_EXECUTE, Permission.PLATFORM_CONNECT,
                Permission.ANALYTICS_VIEW
            },
            Role.VIEWER: {
                Permission.CONTENT_READ, Permission.ANALYTICS_VIEW
            },
            Role.GUEST: {
                Permission.CONTENT_READ
            }
        }
    
    async def check_access(self, request: AccessRequest) -> AccessResult:
        """
        Check access permissions for a request
        
        Args:
            request: Access request with context and resource information
            
        Returns:
            AccessResult with permission decision
        """
        # Check cache first
        cache_key = self._generate_cache_key(request)
        cached_result = await self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        # Get user permissions
        user_permissions = await self._get_user_permissions(request.context)
        
        # Check basic permission
        if request.action not in user_permissions:
            result = AccessResult(
                granted=False,
                reason=f"Missing required permission: {request.action.value}",
                required_permissions={request.action},
                missing_permissions={request.action}
            )
            await self._cache_result(cache_key, result, 300)  # Cache for 5 minutes
            return result
        
        # Check resource ownership
        if request.resource_owner_id:
            ownership_check = await self._check_resource_ownership(request)
            if not ownership_check.granted:
                await self._cache_result(cache_key, ownership_check, 600)
                return ownership_check
        
        # Check attribute-based policies
        policy_check = await self._check_policies(request)
        if not policy_check.granted:
            await self._cache_result(cache_key, policy_check, 300)
            return policy_check
        
        # Check time-based restrictions
        time_check = await self._check_time_restrictions(request)
        if not time_check.granted:
            await self._cache_result(cache_key, time_check, 60)
            return time_check
        
        # Check rate limits
        rate_limit_check = await self._check_access_rate_limits(request)
        if not rate_limit_check.granted:
            await self._cache_result(cache_key, rate_limit_check, 60)
            return rate_limit_check
        
        # Check MFA requirements
        mfa_check = await self._check_mfa_requirements(request)
        if not mfa_check.granted:
            await self._cache_result(cache_key, mfa_check, 60)
            return mfa_check
        
        # Access granted
        result = AccessResult(
            granted=True,
            reason="Access granted",
            required_permissions={request.action},
            missing_permissions=set()
        )
        
        await self._cache_result(cache_key, result, 600)
        await self._log_access_event(request, result)
        
        return result
    
    async def _get_user_permissions(self, context: AccessContext) -> Set[Permission]:
        """Get all permissions for user based on roles"""
        all_permissions = set()
        
        # Add role-based permissions
        for role in context.roles:
            if role in self.role_permissions:
                all_permissions.update(self.role_permissions[role])
        
        # Add explicit permissions from context
        all_permissions.update(context.permissions)
        
        # Add custom permissions from database
        custom_permissions = await self._get_custom_permissions(context.user_id)
        all_permissions.update(custom_permissions)
        
        return all_permissions
    
    async def _get_custom_permissions(self, user_id: str) -> Set[Permission]:
        """Get custom permissions assigned to user"""
        permissions_key = f"user_permissions:{user_id}"
        permission_data = await self.redis.smembers(permissions_key)
        
        permissions = set()
        for perm_str in permission_data:
            try:
                permission = Permission(perm_str.decode())
                permissions.add(permission)
            except ValueError:
                # Skip invalid permissions
                continue
        
        return permissions
    
    async def _check_resource_ownership(self, request: AccessRequest) -> AccessResult:
        """Check if user owns or has access to resource"""
        # Direct ownership check
        if request.resource_owner_id == request.context.user_id:
            return AccessResult(
                granted=True,
                reason="Resource owner",
                required_permissions={request.action},
                missing_permissions=set()
            )
        
        # Check shared access
        shared_access = await self._check_shared_access(request)
        if shared_access:
            return AccessResult(
                granted=True,
                reason="Shared access granted",
                required_permissions={request.action},
                missing_permissions=set()
            )
        
        # Check if user has admin privileges
        if Role.ADMIN in request.context.roles or Role.SUPER_ADMIN in request.context.roles:
            return AccessResult(
                granted=True,
                reason="Administrative access",
                required_permissions={request.action},
                missing_permissions=set()
            )
        
        return AccessResult(
            granted=False,
            reason="Resource access denied - not owner or shared access",
            required_permissions={request.action},
            missing_permissions={request.action}
        )
    
    async def _check_shared_access(self, request: AccessRequest) -> bool:
        """Check if resource has been shared with user"""
        share_key = f"shared_access:{request.resource}:{request.context.user_id}"
        return await self.redis.exists(share_key)
    
    async def _check_policies(self, request: AccessRequest) -> AccessResult:
        """Check attribute-based access control policies"""
        # Get applicable policies
        policies = await self._get_applicable_policies(request)
        
        for policy in policies:
            policy_result = await self._evaluate_policy(policy, request)
            if not policy_result.granted:
                return policy_result
        
        return AccessResult(
            granted=True,
            reason="Policy checks passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    async def _get_applicable_policies(self, request: AccessRequest) -> List[Dict]:
        """Get policies applicable to the request"""
        # This would fetch from a policy store
        # For now, return basic policies
        basic_policies = [
            {
                "id": "ip_restriction",
                "name": "IP Address Restriction",
                "conditions": {
                    "allowed_ips": ["192.168.1.0/24", "10.0.0.0/8"],
                    "blocked_ips": ["1.2.3.4"]
                }
            },
            {
                "id": "platform_restriction",
                "name": "Platform Access Restriction",
                "conditions": {
                    "allowed_platforms": ["web", "mobile", "api"],
                    "restricted_actions": [Permission.USER_DELETE.value, Permission.ADMIN_SYSTEM.value]
                }
            }
        ]
        
        return basic_policies
    
    async def _evaluate_policy(self, policy: Dict, request: AccessRequest) -> AccessResult:
        """Evaluate a single policy against the request"""
        policy_id = policy.get("id")
        conditions = policy.get("conditions", {})
        
        if policy_id == "ip_restriction":
            return await self._evaluate_ip_policy(conditions, request)
        elif policy_id == "platform_restriction":
            return await self._evaluate_platform_policy(conditions, request)
        
        # Default allow if policy not recognized
        return AccessResult(
            granted=True,
            reason="Policy evaluation passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    async def _evaluate_ip_policy(self, conditions: Dict, request: AccessRequest) -> AccessResult:
        """Evaluate IP address policy"""
        if not request.context.ip_address:
            return AccessResult(
                granted=True,
                reason="No IP address to check",
                required_permissions={request.action},
                missing_permissions=set()
            )
        
        blocked_ips = conditions.get("blocked_ips", [])
        if request.context.ip_address in blocked_ips:
            return AccessResult(
                granted=False,
                reason=f"IP address {request.context.ip_address} is blocked",
                required_permissions={request.action},
                missing_permissions={request.action}
            )
        
        return AccessResult(
            granted=True,
            reason="IP policy check passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    async def _evaluate_platform_policy(self, conditions: Dict, request: AccessRequest) -> AccessResult:
        """Evaluate platform access policy"""
        restricted_actions = conditions.get("restricted_actions", [])
        
        if request.action.value in restricted_actions:
            if request.context.platform not in conditions.get("allowed_platforms", []):
                return AccessResult(
                    granted=False,
                    reason=f"Action {request.action.value} not allowed from platform {request.context.platform}",
                    required_permissions={request.action},
                    missing_permissions={request.action}
                )
        
        return AccessResult(
            granted=True,
            reason="Platform policy check passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    async def _check_time_restrictions(self, request: AccessRequest) -> AccessResult:
        """Check time-based access restrictions"""
        # Check if user has time-based restrictions
        restrictions_key = f"time_restrictions:{request.context.user_id}"
        restrictions_data = await self.redis.get(restrictions_key)
        
        if not restrictions_data:
            return AccessResult(
                granted=True,
                reason="No time restrictions",
                required_permissions={request.action},
                missing_permissions=set()
            )
        
        restrictions = json.loads(restrictions_data)
        current_time = datetime.now()
        
        # Check valid time windows
        for restriction in restrictions:
            if restriction["type"] == "allowed_hours":
                current_hour = current_time.hour
                allowed_hours = restriction["hours"]
                if current_hour not in allowed_hours:
                    return AccessResult(
                        granted=False,
                        reason=f"Access not allowed at hour {current_hour}",
                        required_permissions={request.action},
                        missing_permissions={request.action}
                    )
            
            elif restriction["type"] == "blocked_dates":
                current_date = current_time.date().isoformat()
                blocked_dates = restriction["dates"]
                if current_date in blocked_dates:
                    return AccessResult(
                        granted=False,
                        reason=f"Access blocked on date {current_date}",
                        required_permissions={request.action},
                        missing_permissions={request.action}
                    )
        
        return AccessResult(
            granted=True,
            reason="Time restriction checks passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    async def _check_access_rate_limits(self, request: AccessRequest) -> AccessResult:
        """Check access-specific rate limits"""
        # Different from general rate limits - these are for access attempts
        rate_limit_key = f"access_rate_limit:{request.context.user_id}:{request.action.value}"
        current_time = int(time.time() // 60)  # Per minute
        
        pipe = self.redis.pipeline()
        pipe.incr(f"{rate_limit_key}:{current_time}")
        pipe.expire(f"{rate_limit_key}:{current_time}", 60)
        results = await pipe.execute()
        
        current_count = results[0]
        
        # Dynamic limits based on action sensitivity
        sensitive_actions = {
            Permission.USER_DELETE, Permission.ADMIN_SYSTEM, Permission.USER_IMPERSONATE
        }
        
        limit = 5 if request.action in sensitive_actions else 100
        
        if current_count > limit:
            return AccessResult(
                granted=False,
                reason=f"Access rate limit exceeded: {current_count}/{limit}",
                required_permissions={request.action},
                missing_permissions={request.action}
            )
        
        return AccessResult(
            granted=True,
            reason="Access rate limit check passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    async def _check_mfa_requirements(self, request: AccessRequest) -> AccessResult:
        """Check multi-factor authentication requirements"""
        # Actions requiring MFA
        mfa_required_actions = {
            Permission.USER_DELETE,
            Permission.ADMIN_SYSTEM,
            Permission.ADMIN_SECURITY,
            Permission.USER_IMPERSONATE,
            Permission.CONTENT_DELETE  # If it's not the user's own content
        }
        
        if request.action in mfa_required_actions:
            if not request.context.mfa_verified:
                return AccessResult(
                    granted=False,
                    reason="Multi-factor authentication required",
                    required_permissions={request.action},
                    missing_permissions={request.action},
                    additional_requirements={"mfa_required": True}
                )
        
        return AccessResult(
            granted=True,
            reason="MFA requirement check passed",
            required_permissions={request.action},
            missing_permissions=set()
        )
    
    def _generate_cache_key(self, request: AccessRequest) -> str:
        """Generate cache key for access request"""
        key_parts = [
            request.context.user_id,
            "|".join(role.value for role in request.context.roles),
            request.resource,
            request.action.value,
            request.resource_owner_id or "no_owner"
        ]
        
        key_string = ":".join(key_parts)
        return f"access_cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[AccessResult]:
        """Get cached access result"""
        cached_data = await self.redis.get(cache_key)
        if not cached_data:
            return None
        
        try:
            data = json.loads(cached_data)
            return AccessResult(
                granted=data["granted"],
                reason=data["reason"],
                required_permissions={Permission(p) for p in data["required_permissions"]},
                missing_permissions={Permission(p) for p in data["missing_permissions"]},
                additional_requirements=data.get("additional_requirements"),
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            return None
    
    async def _cache_result(self, cache_key: str, result: AccessResult, ttl: int):
        """Cache access result"""
        cache_data = {
            "granted": result.granted,
            "reason": result.reason,
            "required_permissions": [p.value for p in result.required_permissions],
            "missing_permissions": [p.value for p in result.missing_permissions],
            "additional_requirements": result.additional_requirements,
            "expires_at": result.expires_at.isoformat() if result.expires_at else None
        }
        
        await self.redis.setex(cache_key, ttl, json.dumps(cache_data))
    
    async def _log_access_event(self, request: AccessRequest, result: AccessResult):
        """Log access control event for auditing"""
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": request.context.user_id,
            "action": request.action.value,
            "resource": request.resource,
            "granted": result.granted,
            "reason": result.reason,
            "ip_address": request.context.ip_address,
            "user_agent": request.context.user_agent,
            "platform": request.context.platform
        }
        
        # Log to daily audit log
        audit_key = f"access_audit:{datetime.now().strftime('%Y-%m-%d')}"
        await self.redis.lpush(audit_key, json.dumps(event_data))
        await self.redis.expire(audit_key, 86400 * 90)  # Keep for 90 days
    
    # Admin methods for permission management
    
    async def grant_permission(self, user_id: str, permission: Permission, ttl: Optional[int] = None):
        """Grant specific permission to user"""
        permissions_key = f"user_permissions:{user_id}"
        await self.redis.sadd(permissions_key, permission.value)
        
        if ttl:
            await self.redis.expire(permissions_key, ttl)
    
    async def revoke_permission(self, user_id: str, permission: Permission):
        """Revoke specific permission from user"""
        permissions_key = f"user_permissions:{user_id}"
        await self.redis.srem(permissions_key, permission.value)
    
    async def grant_shared_access(self, resource: str, user_id: str, ttl: int = 86400):
        """Grant shared access to resource"""
        share_key = f"shared_access:{resource}:{user_id}"
        await self.redis.setex(share_key, ttl, "1")
    
    async def revoke_shared_access(self, resource: str, user_id: str):
        """Revoke shared access to resource"""
        share_key = f"shared_access:{resource}:{user_id}"
        await self.redis.delete(share_key)
    
    async def set_time_restrictions(self, user_id: str, restrictions: List[Dict]):
        """Set time-based restrictions for user"""
        restrictions_key = f"time_restrictions:{user_id}"
        await self.redis.set(restrictions_key, json.dumps(restrictions))
    
    async def get_user_permissions_summary(self, user_id: str, roles: List[Role]) -> Dict:
        """Get comprehensive permissions summary for user"""
        # Role-based permissions
        role_permissions = set()
        for role in roles:
            if role in self.role_permissions:
                role_permissions.update(self.role_permissions[role])
        
        # Custom permissions
        custom_permissions = await self._get_custom_permissions(user_id)
        
        # All permissions
        all_permissions = role_permissions.union(custom_permissions)
        
        return {
            "user_id": user_id,
            "roles": [role.value for role in roles],
            "role_permissions": [p.value for p in role_permissions],
            "custom_permissions": [p.value for p in custom_permissions],
            "all_permissions": [p.value for p in all_permissions],
            "total_permissions": len(all_permissions)
        }