"""Access Control Management for Deployment Security

Provides comprehensive access control, permission management, and role-based
security for the IA Influencer Agent platform deployment infrastructure.

Author: Fahed Mlaiel <mlaiel@live.de>
Company: IA Influencer Agent Platform
License: Proprietary - All rights reserved

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and
will result in legal action.
"""
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
from pathlib import Path
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access levels for resources"""    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class ResourceType(Enum):
    """Types of resources that can be secured"""    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    CERTIFICATE = "certificate"
    SECRET = "secret"
    LOG = "log"
    MONITORING = "monitoring"
    BACKUP = "backup"
    INFRASTRUCTURE = "infrastructure"


class ActionType(Enum):
    """Types of actions that can be performed"""    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    CONFIGURE = "configure"
    DEPLOY = "deploy"
    MONITOR = "monitor"
    AUDIT = "audit"


@dataclass
class Permission:
    """Permission definition"""    id: str
    name: str
    description: str
    resource_type: ResourceType
    actions: List[ActionType]
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Role:
    """Role definition with permissions"""    id: str
    name: str
    description: str
    permissions: List[Permission]
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class User:
    """User definition for access control"""    id: str
    username: str
    email: str
    roles: List[Role]
    is_active: bool = True
    is_system_user: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessRequest:
    """Access request for authorization"""    user_id: str
    resource_type: ResourceType
    resource_id: str
    action: ActionType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessSession:
    """User access session"""    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    mfa_verified: bool = False
    permissions_cache: Dict[str, bool] = field(default_factory=dict)


class PermissionManager:
    """    Advanced permission management system
    """    
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self._setup_default_permissions()
        logger.info("Permission manager initialized")
    
    def _setup_default_permissions(self):
        """Setup default system permissions"""        default_permissions = [
            # Deployment permissions
            Permission(
                id="deploy_read",
                name="Deployment Read",
                description="Read deployment configurations and status",
                resource_type=ResourceType.DEPLOYMENT,
                actions=[ActionType.READ]
            ),
            Permission(
                id="deploy_write",
                name="Deployment Write",
                description="Create and update deployment configurations",
                resource_type=ResourceType.DEPLOYMENT,
                actions=[ActionType.CREATE, ActionType.UPDATE]
            ),
            Permission(
                id="deploy_execute",
                name="Deployment Execute",
                description="Execute deployments and rollbacks",
                resource_type=ResourceType.DEPLOYMENT,
                actions=[ActionType.EXECUTE, ActionType.DEPLOY]
            ),
            Permission(
                id="deploy_admin",
                name="Deployment Admin",
                description="Full deployment management access",
                resource_type=ResourceType.DEPLOYMENT,
                actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.EXECUTE, ActionType.DEPLOY]
            ),
            
            # Configuration permissions
            Permission(
                id="config_read",
                name="Configuration Read",
                description="Read configuration files and settings",
                resource_type=ResourceType.CONFIGURATION,
                actions=[ActionType.READ]
            ),
            Permission(
                id="config_write",
                name="Configuration Write",
                description="Create and update configurations",
                resource_type=ResourceType.CONFIGURATION,
                actions=[ActionType.CREATE, ActionType.UPDATE, ActionType.CONFIGURE]
            ),
            Permission(
                id="config_admin",
                name="Configuration Admin",
                description="Full configuration management access",
                resource_type=ResourceType.CONFIGURATION,
                actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.CONFIGURE]
            ),
            
            # Certificate permissions
            Permission(
                id="cert_read",
                name="Certificate Read",
                description="Read certificate information",
                resource_type=ResourceType.CERTIFICATE,
                actions=[ActionType.READ]
            ),
            Permission(
                id="cert_manage",
                name="Certificate Manage",
                description="Create and manage certificates",
                resource_type=ResourceType.CERTIFICATE,
                actions=[ActionType.CREATE, ActionType.UPDATE, ActionType.DELETE]
            ),
            
            # Secret permissions
            Permission(
                id="secret_read",
                name="Secret Read",
                description="Read secret values",
                resource_type=ResourceType.SECRET,
                actions=[ActionType.READ]
            ),
            Permission(
                id="secret_write",
                name="Secret Write",
                description="Create and update secrets",
                resource_type=ResourceType.SECRET,
                actions=[ActionType.CREATE, ActionType.UPDATE]
            ),
            Permission(
                id="secret_admin",
                name="Secret Admin",
                description="Full secret management access",
                resource_type=ResourceType.SECRET,
                actions=[ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE]
            ),
            
            # Monitoring permissions
            Permission(
                id="monitor_read",
                name="Monitoring Read",
                description="Read monitoring data and metrics",
                resource_type=ResourceType.MONITORING,
                actions=[ActionType.READ, ActionType.MONITOR]
            ),
            Permission(
                id="monitor_admin",
                name="Monitoring Admin",
                description="Configure monitoring and alerting",
                resource_type=ResourceType.MONITORING,
                actions=[ActionType.READ, ActionType.UPDATE, ActionType.CONFIGURE, ActionType.MONITOR]
            ),
            
            # Audit permissions
            Permission(
                id="audit_read",
                name="Audit Read",
                description="Read audit logs and reports",
                resource_type=ResourceType.LOG,
                actions=[ActionType.READ, ActionType.AUDIT]
            ),
            Permission(
                id="audit_admin",
                name="Audit Admin",
                description="Configure audit settings and export logs",
                resource_type=ResourceType.LOG,
                actions=[ActionType.READ, ActionType.CONFIGURE, ActionType.AUDIT]
            )
        ]
        
        for permission in default_permissions:
            self.permissions[permission.id] = permission
    
    def create_permission(
        self,
        permission_id: str,
        name: str,
        description: str,
        resource_type: ResourceType,
        actions: List[ActionType],
        conditions: Dict[str, Any] = None
    ) -> Permission:
        """        Create new permission
        
        Args:
            permission_id: Unique permission identifier
            name: Permission name
            description: Permission description
            resource_type: Type of resource
            actions: List of allowed actions
            conditions: Optional conditions for the permission
            
        Returns:
            Created permission
        """        try:
            if permission_id in self.permissions:
                raise ValueError(f"Permission already exists: {permission_id}")
            
            permission = Permission(
                id=permission_id,
                name=name,
                description=description,
                resource_type=resource_type,
                actions=actions,
                conditions=conditions or {}
            )
            
            self.permissions[permission_id] = permission
            logger.info(f"Created permission: {permission_id}")
            return permission
            
        except Exception as e:
            logger.error(f"Failed to create permission: {e}")
            raise
    
    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID"""        return self.permissions.get(permission_id)
    
    def list_permissions(
        self,
        resource_type: Optional[ResourceType] = None,
        action: Optional[ActionType] = None
    ) -> List[Permission]:
        """        List permissions with optional filters
        
        Args:
            resource_type: Filter by resource type
            action: Filter by action type
            
        Returns:
            List of matching permissions
        """        permissions = list(self.permissions.values())
        
        if resource_type:
            permissions = [p for p in permissions if p.resource_type == resource_type]
        
        if action:
            permissions = [p for p in permissions if action in p.actions]
        
        return permissions
    
    def update_permission(self, permission_id: str, **kwargs) -> Optional[Permission]:
        """        Update permission properties
        
        Args:
            permission_id: Permission ID to update
            **kwargs: Properties to update
            
        Returns:
            Updated permission or None
        """        try:
            if permission_id not in self.permissions:
                logger.warning(f"Permission not found: {permission_id}")
                return None
            
            permission = self.permissions[permission_id]
            
            # Update allowed properties
            allowed_updates = ['name', 'description', 'actions', 'conditions']
            for key, value in kwargs.items():
                if key in allowed_updates:
                    setattr(permission, key, value)
            
            logger.info(f"Updated permission: {permission_id}")
            return permission
            
        except Exception as e:
            logger.error(f"Failed to update permission: {e}")
            return None
    
    def delete_permission(self, permission_id: str) -> bool:
        """        Delete permission
        
        Args:
            permission_id: Permission ID to delete
            
        Returns:
            True if deleted successfully
        """        try:
            if permission_id not in self.permissions:
                logger.warning(f"Permission not found: {permission_id}")
                return False
            
            del self.permissions[permission_id]
            logger.info(f"Deleted permission: {permission_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete permission: {e}")
            return False


class RoleBasedSecurity:
    """    Role-based access control (RBAC) system
    """    
    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self._setup_default_roles()
        logger.info("Role-based security system initialized")
    
    def _setup_default_roles(self):
        """Setup default system roles"""        # Get default permissions
        permissions = self.permission_manager.permissions
        
        # System Administrator role
        admin_permissions = [
            permissions["deploy_admin"],
            permissions["config_admin"],
            permissions["cert_manage"],
            permissions["secret_admin"],
            permissions["monitor_admin"],
            permissions["audit_admin"]
        ]
        
        admin_role = Role(
            id="system_admin",
            name="System Administrator",
            description="Full system access for administrators",
            permissions=admin_permissions,
            is_system_role=True
        )
        
        # DevOps Engineer role
        devops_permissions = [
            permissions["deploy_admin"],
            permissions["config_write"],
            permissions["cert_manage"],
            permissions["secret_write"],
            permissions["monitor_admin"],
            permissions["audit_read"]
        ]
        
        devops_role = Role(
            id="devops_engineer",
            name="DevOps Engineer",
            description="Deployment and infrastructure management access",
            permissions=devops_permissions,
            is_system_role=True
        )
        
        # Security Analyst role
        security_permissions = [
            permissions["deploy_read"],
            permissions["config_read"],
            permissions["cert_read"],
            permissions["secret_read"],
            permissions["monitor_read"],
            permissions["audit_admin"]
        ]
        
        security_role = Role(
            id="security_analyst",
            name="Security Analyst",
            description="Security monitoring and audit access",
            permissions=security_permissions,
            is_system_role=True
        )
        
        # Developer role
        developer_permissions = [
            permissions["deploy_read"],
            permissions["config_read"],
            permissions["monitor_read"]
        ]
        
        developer_role = Role(
            id="developer",
            name="Developer",
            description="Basic read access for developers",
            permissions=developer_permissions,
            is_system_role=True
        )
        
        # Auditor role (read-only)
        auditor_permissions = [
            permissions["audit_read"],
            permissions["monitor_read"],
            permissions["deploy_read"],
            permissions["config_read"]
        ]
        
        auditor_role = Role(
            id="auditor",
            name="Auditor",
            description="Read-only access for compliance auditing",
            permissions=auditor_permissions,
            is_system_role=True
        )
        
        # Store default roles
        self.roles = {
            "system_admin": admin_role,
            "devops_engineer": devops_role,
            "security_analyst": security_role,
            "developer": developer_role,
            "auditor": auditor_role
        }
    
    def create_role(
        self,
        role_id: str,
        name: str,
        description: str,
        permission_ids: List[str]
    ) -> Role:
        """        Create new role
        
        Args:
            role_id: Unique role identifier
            name: Role name
            description: Role description
            permission_ids: List of permission IDs to assign
            
        Returns:
            Created role
        """        try:
            if role_id in self.roles:
                raise ValueError(f"Role already exists: {role_id}")
            
            # Validate permissions
            permissions = []
            for perm_id in permission_ids:
                permission = self.permission_manager.get_permission(perm_id)
                if not permission:
                    raise ValueError(f"Permission not found: {perm_id}")
                permissions.append(permission)
            
            role = Role(
                id=role_id,
                name=name,
                description=description,
                permissions=permissions
            )
            
            self.roles[role_id] = role
            logger.info(f"Created role: {role_id}")
            return role
            
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            raise
    
    def assign_permissions_to_role(self, role_id: str, permission_ids: List[str]) -> bool:
        """        Assign permissions to role
        
        Args:
            role_id: Role ID
            permission_ids: List of permission IDs to assign
            
        Returns:
            True if successful
        """        try:
            if role_id not in self.roles:
                raise ValueError(f"Role not found: {role_id}")
            
            role = self.roles[role_id]
            
            # Check if system role
            if role.is_system_role:
                raise ValueError("Cannot modify system role permissions")
            
            # Validate and add permissions
            for perm_id in permission_ids:
                permission = self.permission_manager.get_permission(perm_id)
                if not permission:
                    raise ValueError(f"Permission not found: {perm_id}")
                
                # Check if permission already assigned
                if permission not in role.permissions:
                    role.permissions.append(permission)
            
            role.updated_at = datetime.utcnow()
            logger.info(f"Assigned permissions to role: {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign permissions to role: {e}")
            return False
    
    def remove_permissions_from_role(self, role_id: str, permission_ids: List[str]) -> bool:
        """        Remove permissions from role
        
        Args:
            role_id: Role ID
            permission_ids: List of permission IDs to remove
            
        Returns:
            True if successful
        """        try:
            if role_id not in self.roles:
                raise ValueError(f"Role not found: {role_id}")
            
            role = self.roles[role_id]
            
            # Check if system role
            if role.is_system_role:
                raise ValueError("Cannot modify system role permissions")
            
            # Remove permissions
            for perm_id in permission_ids:
                role.permissions = [p for p in role.permissions if p.id != perm_id]
            
            role.updated_at = datetime.utcnow()
            logger.info(f"Removed permissions from role: {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove permissions from role: {e}")
            return False
    
    def create_user(
        self,
        user_id: str,
        username: str,
        email: str,
        role_ids: List[str]
    ) -> User:
        """        Create new user
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: User email
            role_ids: List of role IDs to assign
            
        Returns:
            Created user
        """        try:
            if user_id in self.users:
                raise ValueError(f"User already exists: {user_id}")
            
            # Validate roles
            roles = []
            for role_id in role_ids:
                if role_id not in self.roles:
                    raise ValueError(f"Role not found: {role_id}")
                roles.append(self.roles[role_id])
            
            user = User(
                id=user_id,
                username=username,
                email=email,
                roles=roles
            )
            
            self.users[user_id] = user
            logger.info(f"Created user: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def assign_roles_to_user(self, user_id: str, role_ids: List[str]) -> bool:
        """        Assign roles to user
        
        Args:
            user_id: User ID
            role_ids: List of role IDs to assign
            
        Returns:
            True if successful
        """        try:
            if user_id not in self.users:
                raise ValueError(f"User not found: {user_id}")
            
            user = self.users[user_id]
            
            # Validate and add roles
            for role_id in role_ids:
                if role_id not in self.roles:
                    raise ValueError(f"Role not found: {role_id}")
                
                role = self.roles[role_id]
                
                # Check if role already assigned
                if role not in user.roles:
                    user.roles.append(role)
            
            user.updated_at = datetime.utcnow()
            logger.info(f"Assigned roles to user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign roles to user: {e}")
            return False
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """        Get all permissions for user (aggregated from roles)
        
        Args:
            user_id: User ID
            
        Returns:
            Set of user permissions
        """        try:
            if user_id not in self.users:
                return set()
            
            user = self.users[user_id]
            permissions = set()
            
            for role in user.roles:
                permissions.update(role.permissions)
            
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return set()
    
    def check_user_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        action: ActionType,
        resource_id: Optional[str] = None
    ) -> bool:
        """        Check if user has specific permission
        
        Args:
            user_id: User ID
            resource_type: Resource type
            action: Action type
            resource_id: Optional specific resource ID
            
        Returns:
            True if user has permission
        """        try:
            permissions = self.get_user_permissions(user_id)
            
            for permission in permissions:
                if (permission.resource_type == resource_type and 
                    action in permission.actions):
                    
                    # Check additional conditions if any
                    if permission.conditions:
                        # Implement condition checking logic here
                        # For now, assume conditions pass
                        pass
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check user permission: {e}")
            return False


class DeploymentAccessControl:
    """    Comprehensive access control system for deployment security
    """    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        jwt_secret: str = "your-secret-key",
        session_timeout: int = 3600
    ):
        self.permission_manager = PermissionManager()
        self.rbac = RoleBasedSecurity(self.permission_manager)
        
        self.redis_url = redis_url
        self.jwt_secret = jwt_secret
        self.session_timeout = session_timeout
        
        # Session storage
        self.sessions: Dict[str, AccessSession] = {}
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Connection pools
        self._redis_pool = None
        
        logger.info("Deployment access control initialized")
    
    async def initialize_redis_pool(self):
        """Initialize Redis connection pool"""        try:
            self._redis_pool = aioredis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis connection pool initialized for access control")
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_jwt_token(self, user_id: str, session_id: str, expires_in: int = None) -> str:
        """        Generate JWT token for user session
        
        Args:
            user_id: User ID
            session_id: Session ID
            expires_in: Token expiration time in seconds
            
        Returns:
            JWT token
        """        try:
            expires_in = expires_in or self.session_timeout
            
            payload = {
                'user_id': user_id,
                'session_id': session_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """        Verify JWT token and extract payload
        
        Args:
            token: JWT token
            
        Returns:
            Token payload or None if invalid
        """        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Failed to verify JWT token: {e}")
            return None
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str
    ) -> Optional[str]:
        """        Authenticate user and create session
        
        Args:
            username: Username
            password: Password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            JWT token if authentication successful
        """        try:
            # Find user by username
            user = None
            for user_obj in self.rbac.users.values():
                if user_obj.username == username:
                    user = user_obj
                    break
            
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            # For this example, we'll use a simple password check
            # In production, retrieve hashed password from database
            expected_password_hash = self.hash_password("default_password")
            
            if not self.verify_password(password, expected_password_hash):
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            # Create session
            session_id = hashlib.sha256(
                f"{user.id}:{datetime.utcnow().isoformat()}:{ip_address}".encode()
            ).hexdigest()
            
            session = AccessSession(
                session_id=session_id,
                user_id=user.id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.sessions[session_id] = session
            
            # Update user last login
            user.last_login = datetime.utcnow()
            
            # Generate JWT token
            token = self.generate_jwt_token(user.id, session_id)
            
            logger.info(f"User authenticated: {username}")
            return token
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    async def authorize_request(self, request: AccessRequest, token: str) -> bool:
        """        Authorize access request
        
        Args:
            request: Access request
            token: JWT token
            
        Returns:
            True if authorized
        """        try:
            # Verify token
            payload = self.verify_jwt_token(token)
            if not payload:
                return False
            
            session_id = payload.get('session_id')
            user_id = payload.get('user_id')
            
            # Check session
            if session_id not in self.sessions:
                logger.warning(f"Session not found: {session_id}")
                return False
            
            session = self.sessions[session_id]
            
            # Verify user ID matches
            if session.user_id != user_id or session.user_id != request.user_id:
                logger.warning("User ID mismatch in authorization")
                return False
            
            # Check session activity
            if not session.is_active:
                logger.warning(f"Inactive session: {session_id}")
                return False
            
            # Update session activity
            session.last_activity = datetime.utcnow()
            
            # Check permission
            has_permission = self.rbac.check_user_permission(
                user_id=request.user_id,
                resource_type=request.resource_type,
                action=request.action,
                resource_id=request.resource_id
            )
            
            if has_permission:
                logger.info(f"Access authorized: {request.user_id} -> {request.resource_type.value}:{request.action.value}")
            else:
                logger.warning(f"Access denied: {request.user_id} -> {request.resource_type.value}:{request.action.value}")
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            return False
    
    async def logout_session(self, session_id: str) -> bool:
        """        Logout user session
        
        Args:
            session_id: Session ID to logout
            
        Returns:
            True if successful
        """        try:
            if session_id in self.sessions:
                self.sessions[session_id].is_active = False
                del self.sessions[session_id]
                logger.info(f"Session logged out: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to logout session: {e}")
            return False
    
    async def cleanup_expired_sessions(self):
        """Cleanup expired sessions"""        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                # Check if session has expired
                if (current_time - session.last_activity).total_seconds() > self.session_timeout:
                    expired_sessions.append(session_id)
            
            # Remove expired sessions
            for session_id in expired_sessions:
                del self.sessions[session_id]
                logger.info(f"Removed expired session: {session_id}")
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    def get_access_summary(self, user_id: str) -> Dict[str, Any]:
        """        Get access summary for user
        
        Args:
            user_id: User ID
            
        Returns:
            Access summary
        """        try:
            if user_id not in self.rbac.users:
                return {'error': 'User not found'}
            
            user = self.rbac.users[user_id]
            permissions = self.rbac.get_user_permissions(user_id)
            
            # Get active sessions
            active_sessions = [
                s for s in self.sessions.values()
                if s.user_id == user_id and s.is_active
            ]
            
            summary = {
                'user_id': user_id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'roles': [{'id': r.id, 'name': r.name} for r in user.roles],
                'permissions': [
                    {
                        'id': p.id,
                        'name': p.name,
                        'resource_type': p.resource_type.value,
                        'actions': [a.value for a in p.actions]
                    }
                    for p in permissions
                ],
                'active_sessions': len(active_sessions),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get access summary: {e}")
            return {'error': str(e)}
