"""
Identity and Access Manager
Enterprise identity and access management for ML systems

Features:
- Role-based access control (RBAC)
- Multi-factor authentication
- Single sign-on (SSO) integration
- User lifecycle management
- Access auditing and compliance
- Dynamic access policies

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
import hashlib
import secrets
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import uuid


class AccessLevel(Enum):
    """Access levels for resources"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    OWNER = "owner"


class AuthenticationMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    MFA = "mfa"
    SSO = "sso"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"


@dataclass
class User:
    """User entity"""
    user_id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    groups: List[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    authentication_methods: List[AuthenticationMethod]
    metadata: Dict[str, Any]


@dataclass
class Role:
    """Role definition"""
    role_id: str
    name: str
    description: str
    permissions: List[str]
    is_system_role: bool
    created_at: datetime
    created_by: str


@dataclass
class Permission:
    """Permission definition"""
    permission_id: str
    name: str
    resource_type: str
    access_level: AccessLevel
    description: str
    is_system_permission: bool


@dataclass
class AccessPolicy:
    """Dynamic access policy"""
    policy_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[str]
    effect: str  # allow, deny
    priority: int
    is_active: bool


@dataclass
class AccessRequest:
    """Access request for audit trail"""
    request_id: str
    user_id: str
    resource_id: str
    resource_type: str
    requested_access: AccessLevel
    timestamp: datetime
    source_ip: Optional[str]
    user_agent: Optional[str]
    decision: str  # granted, denied
    reason: str
    policy_applied: Optional[str]


class IdentityAccessManager:
    """
    Enterprise Identity and Access Manager
    Comprehensive IAM for ML systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.access_requests: List[AccessRequest] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default roles and permissions
        self._initialize_default_permissions()
        self._initialize_default_roles()
    
    def _initialize_default_permissions(self):
        """Initialize default system permissions"""
        default_permissions = [
            Permission(
                permission_id="perm_model_read",
                name="Model Read",
                resource_type="model",
                access_level=AccessLevel.READ,
                description="Read access to ML models",
                is_system_permission=True
            ),
            Permission(
                permission_id="perm_model_write",
                name="Model Write",
                resource_type="model",
                access_level=AccessLevel.WRITE,
                description="Write access to ML models",
                is_system_permission=True
            ),
            Permission(
                permission_id="perm_model_execute",
                name="Model Execute",
                resource_type="model",
                access_level=AccessLevel.EXECUTE,
                description="Execute ML model inference",
                is_system_permission=True
            ),
            Permission(
                permission_id="perm_data_read",
                name="Data Read",
                resource_type="data",
                access_level=AccessLevel.READ,
                description="Read access to datasets",
                is_system_permission=True
            ),
            Permission(
                permission_id="perm_data_write",
                name="Data Write", 
                resource_type="data",
                access_level=AccessLevel.WRITE,
                description="Write access to datasets",
                is_system_permission=True
            ),
            Permission(
                permission_id="perm_system_admin",
                name="System Admin",
                resource_type="system",
                access_level=AccessLevel.ADMIN,
                description="Full system administration",
                is_system_permission=True
            )
        ]
        
        for perm in default_permissions:
            self.permissions[perm.permission_id] = perm
    
    def _initialize_default_roles(self):
        """Initialize default system roles"""
        default_roles = [
            Role(
                role_id="role_ml_engineer",
                name="ML Engineer",
                description="Machine Learning Engineer with model development access",
                permissions=["perm_model_read", "perm_model_write", "perm_model_execute", "perm_data_read"],
                is_system_role=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            Role(
                role_id="role_data_scientist",
                name="Data Scientist",
                description="Data Scientist with data and model access",
                permissions=["perm_model_read", "perm_model_execute", "perm_data_read", "perm_data_write"],
                is_system_role=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            Role(
                role_id="role_ml_ops",
                name="MLOps Engineer",
                description="MLOps Engineer with deployment and monitoring access",
                permissions=["perm_model_read", "perm_model_write", "perm_model_execute"],
                is_system_role=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            Role(
                role_id="role_system_admin",
                name="System Administrator",
                description="Full system administrator",
                permissions=["perm_system_admin"],
                is_system_role=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            Role(
                role_id="role_viewer",
                name="Viewer",
                description="Read-only access to models and data",
                permissions=["perm_model_read", "perm_data_read"],
                is_system_role=True,
                created_at=datetime.now(),
                created_by="system"
            )
        ]
        
        for role in default_roles:
            self.roles[role.role_id] = role
    
    async def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        roles: List[str],
        authentication_methods: List[AuthenticationMethod],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new user"""
        try:
            user_id = str(uuid.uuid4())
            
            # Validate roles exist
            for role_id in roles:
                if role_id not in self.roles:
                    raise ValueError(f"Role {role_id} does not exist")
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                roles=roles,
                groups=[],
                is_active=True,
                created_at=datetime.now(),
                last_login=None,
                authentication_methods=authentication_methods,
                metadata=metadata or {}
            )
            
            self.users[user_id] = user
            
            self.logger.info(f"User created: {username} ({user_id})")
            return user_id
            
        except Exception as e:
            self.logger.error(f"Failed to create user: {str(e)}")
            raise
    
    async def authenticate_user(
        self,
        username: str,
        credentials: Dict[str, Any],
        source_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Authenticate user and create session"""
        try:
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                await self._log_access_request(
                    user_id="unknown",
                    resource_id="authentication",
                    resource_type="system",
                    requested_access=AccessLevel.READ,
                    source_ip=source_ip,
                    decision="denied",
                    reason="user_not_found"
                )
                return {"authenticated": False, "reason": "invalid_credentials"}
            
            if not user.is_active:
                return {"authenticated": False, "reason": "account_disabled"}
            
            # Validate credentials based on authentication method
            auth_method = credentials.get("method")
            if not auth_method or AuthenticationMethod(auth_method) not in user.authentication_methods:
                return {"authenticated": False, "reason": "invalid_auth_method"}
            
            # Simplified credential validation
            if auth_method == "password":
                if not self._validate_password(credentials.get("password", "")):
                    await self._log_access_request(
                        user_id=user.user_id,
                        resource_id="authentication",
                        resource_type="system",
                        requested_access=AccessLevel.READ,
                        source_ip=source_ip,
                        decision="denied",
                        reason="invalid_password"
                    )
                    return {"authenticated": False, "reason": "invalid_credentials"}
            
            # Create session
            session_id = self._create_session(user, source_ip)
            
            # Update last login
            user.last_login = datetime.now()
            self.users[user.user_id] = user
            
            await self._log_access_request(
                user_id=user.user_id,
                resource_id="authentication",
                resource_type="system",
                requested_access=AccessLevel.READ,
                source_ip=source_ip,
                decision="granted",
                reason="authentication_successful"
            )
            
            return {
                "authenticated": True,
                "user_id": user.user_id,
                "session_id": session_id,
                "roles": user.roles,
                "permissions": await self._get_user_permissions(user.user_id)
            }
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return {"authenticated": False, "reason": "system_error"}
    
    async def check_access(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        requested_access: AccessLevel,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check if user has access to resource"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"access_granted": False, "reason": "user_not_found"}
            
            if not user.is_active:
                return {"access_granted": False, "reason": "user_inactive"}
            
            # Check role-based permissions
            user_permissions = await self._get_user_permissions(user_id)
            required_permission = self._get_required_permission(resource_type, requested_access)
            
            if required_permission in user_permissions:
                rbac_access = True
            else:
                rbac_access = False
            
            # Apply dynamic access policies
            policy_decision = await self._evaluate_access_policies(
                user, resource_id, resource_type, requested_access, context or {}
            )
            
            # Final decision (RBAC + Policies)
            final_decision = rbac_access and policy_decision["allowed"]
            decision_reason = policy_decision.get("reason", "rbac_check")
            
            # Log access request
            await self._log_access_request(
                user_id=user_id,
                resource_id=resource_id,
                resource_type=resource_type,
                requested_access=requested_access,
                source_ip=context.get("source_ip") if context else None,
                decision="granted" if final_decision else "denied",
                reason=decision_reason,
                policy_applied=policy_decision.get("policy_id")
            )
            
            return {
                "access_granted": final_decision,
                "reason": decision_reason,
                "rbac_decision": rbac_access,
                "policy_decision": policy_decision["allowed"],
                "applied_policy": policy_decision.get("policy_id"),
                "user_permissions": user_permissions
            }
            
        except Exception as e:
            self.logger.error(f"Access check failed: {str(e)}")
            return {"access_granted": False, "reason": "system_error"}
    
    async def create_role(
        self,
        name: str,
        description: str,
        permissions: List[str],
        created_by: str
    ) -> str:
        """Create new role"""
        try:
            role_id = str(uuid.uuid4())
            
            # Validate permissions exist
            for perm_id in permissions:
                if perm_id not in self.permissions:
                    raise ValueError(f"Permission {perm_id} does not exist")
            
            role = Role(
                role_id=role_id,
                name=name,
                description=description,
                permissions=permissions,
                is_system_role=False,
                created_at=datetime.now(),
                created_by=created_by
            )
            
            self.roles[role_id] = role
            
            self.logger.info(f"Role created: {name} ({role_id})")
            return role_id
            
        except Exception as e:
            self.logger.error(f"Failed to create role: {str(e)}")
            raise
    
    async def create_permission(
        self,
        name: str,
        resource_type: str,
        access_level: AccessLevel,
        description: str
    ) -> str:
        """Create new permission"""
        try:
            permission_id = str(uuid.uuid4())
            
            permission = Permission(
                permission_id=permission_id,
                name=name,
                resource_type=resource_type,
                access_level=access_level,
                description=description,
                is_system_permission=False
            )
            
            self.permissions[permission_id] = permission
            
            self.logger.info(f"Permission created: {name} ({permission_id})")
            return permission_id
            
        except Exception as e:
            self.logger.error(f"Failed to create permission: {str(e)}")
            raise
    
    async def create_access_policy(
        self,
        name: str,
        description: str,
        conditions: Dict[str, Any],
        actions: List[str],
        effect: str,
        priority: int = 1000
    ) -> str:
        """Create dynamic access policy"""
        try:
            policy_id = str(uuid.uuid4())
            
            policy = AccessPolicy(
                policy_id=policy_id,
                name=name,
                description=description,
                conditions=conditions,
                actions=actions,
                effect=effect,
                priority=priority,
                is_active=True
            )
            
            self.access_policies[policy_id] = policy
            
            self.logger.info(f"Access policy created: {name} ({policy_id})")
            return policy_id
            
        except Exception as e:
            self.logger.error(f"Failed to create access policy: {str(e)}")
            raise
    
    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign role to user"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False
            
            if role_id not in self.roles:
                return False
            
            if role_id not in user.roles:
                user.roles.append(role_id)
                self.users[user_id] = user
                
                self.logger.info(f"Role {role_id} assigned to user {user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign role: {str(e)}")
            return False
    
    async def revoke_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Revoke role from user"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False
            
            if role_id in user.roles:
                user.roles.remove(role_id)
                self.users[user_id] = user
                
                self.logger.info(f"Role {role_id} revoked from user {user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke role: {str(e)}")
            return False
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            user = self.users.get(user_id)
            if not user:
                return False
            
            user.is_active = False
            self.users[user_id] = user
            
            # Terminate active sessions
            sessions_to_remove = []
            for session_id, session_data in self.active_sessions.items():
                if session_data["user_id"] == user_id:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.active_sessions[session_id]
            
            self.logger.info(f"User {user_id} deactivated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate user: {str(e)}")
            return False
    
    async def get_user_access_history(
        self,
        user_id: str,
        time_period: timedelta = timedelta(days=30)
    ) -> List[Dict[str, Any]]:
        """Get user access history for audit"""
        try:
            cutoff_time = datetime.now() - time_period
            
            user_requests = [
                asdict(req) for req in self.access_requests
                if req.user_id == user_id and req.timestamp >= cutoff_time
            ]
            
            # Convert datetime objects to ISO strings
            for req in user_requests:
                req["timestamp"] = req["timestamp"].isoformat()
            
            return user_requests
            
        except Exception as e:
            self.logger.error(f"Failed to get user access history: {str(e)}")
            return []
    
    async def get_iam_metrics(self) -> Dict[str, Any]:
        """Get IAM metrics and statistics"""
        try:
            # Calculate metrics
            total_users = len(self.users)
            active_users = len([u for u in self.users.values() if u.is_active])
            total_roles = len(self.roles)
            total_permissions = len(self.permissions)
            active_sessions = len(self.active_sessions)
            
            # Recent access requests (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_requests = [r for r in self.access_requests if r.timestamp >= cutoff_time]
            granted_requests = [r for r in recent_requests if r.decision == "granted"]
            denied_requests = [r for r in recent_requests if r.decision == "denied"]
            
            return {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users
                },
                "roles": {
                    "total": total_roles,
                    "system_roles": len([r for r in self.roles.values() if r.is_system_role]),
                    "custom_roles": len([r for r in self.roles.values() if not r.is_system_role])
                },
                "permissions": {
                    "total": total_permissions,
                    "system_permissions": len([p for p in self.permissions.values() if p.is_system_permission]),
                    "custom_permissions": len([p for p in self.permissions.values() if not p.is_system_permission])
                },
                "access_activity": {
                    "active_sessions": active_sessions,
                    "requests_24h": len(recent_requests),
                    "granted_24h": len(granted_requests),
                    "denied_24h": len(denied_requests),
                    "success_rate": len(granted_requests) / max(len(recent_requests), 1) * 100
                },
                "policies": {
                    "total": len(self.access_policies),
                    "active": len([p for p in self.access_policies.values() if p.is_active])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get IAM metrics: {str(e)}")
            return {}
    
    # Private methods
    
    def _validate_password(self, password: str) -> bool:
        """Validate password (simplified)"""
        # In production, would validate against stored hash
        return len(password) >= 8
    
    def _create_session(self, user: User, source_ip: Optional[str]) -> str:
        """Create user session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "session_id": session_id,
            "user_id": user.user_id,
            "username": user.username,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "source_ip": source_ip,
            "is_active": True
        }
        
        self.active_sessions[session_id] = session_data
        return session_id
    
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for user based on roles"""
        user = self.users.get(user_id)
        if not user:
            return []
        
        permissions = set()
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role:
                permissions.update(role.permissions)
        
        return list(permissions)
    
    def _get_required_permission(self, resource_type: str, access_level: AccessLevel) -> str:
        """Get required permission for resource and access level"""
        # Map resource types and access levels to permission IDs
        permission_map = {
            ("model", AccessLevel.READ): "perm_model_read",
            ("model", AccessLevel.WRITE): "perm_model_write", 
            ("model", AccessLevel.EXECUTE): "perm_model_execute",
            ("data", AccessLevel.READ): "perm_data_read",
            ("data", AccessLevel.WRITE): "perm_data_write",
            ("system", AccessLevel.ADMIN): "perm_system_admin"
        }
        
        return permission_map.get((resource_type, access_level), "")
    
    async def _evaluate_access_policies(
        self,
        user: User,
        resource_id: str,
        resource_type: str,
        requested_access: AccessLevel,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate dynamic access policies"""
        try:
            # Get applicable policies sorted by priority
            applicable_policies = [
                p for p in self.access_policies.values()
                if p.is_active and self._policy_applies(p, user, resource_type, context)
            ]
            applicable_policies.sort(key=lambda x: x.priority)
            
            # Default allow if no policies
            if not applicable_policies:
                return {"allowed": True, "reason": "no_applicable_policies"}
            
            # Evaluate policies in priority order
            for policy in applicable_policies:
                if self._evaluate_policy_conditions(policy, user, resource_id, context):
                    if policy.effect == "deny":
                        return {
                            "allowed": False,
                            "reason": f"denied_by_policy_{policy.name}",
                            "policy_id": policy.policy_id
                        }
                    elif policy.effect == "allow":
                        return {
                            "allowed": True,
                            "reason": f"allowed_by_policy_{policy.name}",
                            "policy_id": policy.policy_id
                        }
            
            # Default deny if no explicit allow
            return {"allowed": False, "reason": "no_explicit_allow_policy"}
            
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {str(e)}")
            return {"allowed": False, "reason": "policy_evaluation_error"}
    
    def _policy_applies(
        self,
        policy: AccessPolicy,
        user: User,
        resource_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """Check if policy applies to the access request"""
        conditions = policy.conditions
        
        # Check resource type
        if "resource_types" in conditions:
            if resource_type not in conditions["resource_types"]:
                return False
        
        # Check user roles
        if "roles" in conditions:
            if not any(role in user.roles for role in conditions["roles"]):
                return False
        
        # Check time-based conditions
        if "time_restrictions" in conditions:
            current_hour = datetime.now().hour
            allowed_hours = conditions["time_restrictions"].get("allowed_hours", [])
            if allowed_hours and current_hour not in allowed_hours:
                return False
        
        return True
    
    def _evaluate_policy_conditions(
        self,
        policy: AccessPolicy,
        user: User,
        resource_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate policy conditions against current context"""
        conditions = policy.conditions
        
        # Check IP restrictions
        if "ip_restrictions" in conditions:
            source_ip = context.get("source_ip")
            allowed_ips = conditions["ip_restrictions"].get("allowed_ips", [])
            if allowed_ips and source_ip not in allowed_ips:
                return False
        
        # Check session age
        if "max_session_age_hours" in conditions:
            max_age = conditions["max_session_age_hours"]
            # Simplified check - in practice would check actual session age
            if max_age < 8:  # Example condition
                return False
        
        # Check resource-specific conditions
        if "resource_conditions" in conditions:
            resource_conditions = conditions["resource_conditions"]
            # Apply resource-specific logic here
            pass
        
        return True
    
    async def _log_access_request(
        self,
        user_id: str,
        resource_id: str,
        resource_type: str,
        requested_access: AccessLevel,
        source_ip: Optional[str],
        decision: str,
        reason: str,
        policy_applied: Optional[str] = None
    ):
        """Log access request for audit trail"""
        request = AccessRequest(
            request_id=str(uuid.uuid4()),
            user_id=user_id,
            resource_id=resource_id,
            resource_type=resource_type,
            requested_access=requested_access,
            timestamp=datetime.now(),
            source_ip=source_ip,
            user_agent=None,  # Could be passed in context
            decision=decision,
            reason=reason,
            policy_applied=policy_applied
        )
        
        self.access_requests.append(request)
        
        # Keep only recent requests (last 10000)
        if len(self.access_requests) > 10000:
            self.access_requests = self.access_requests[-10000:]


# Global instance
identity_access_manager = IdentityAccessManager()