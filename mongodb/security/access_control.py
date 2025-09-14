"""Role-Based Access Control (RBAC) for MongoDB
============================================

Enterprise-grade access control system with role-based permissions,
user management, and fine-grained authorization policies.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTED:
- Security Engineer: Zero-trust security model
- DBA: Database access control and permissions
- Backend Senior: Enterprise authorization patterns
"""

import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Database permission levels."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    CREATE_INDEX = "create_index"
    DROP_INDEX = "drop_index"
    CREATE_COLLECTION = "create_collection"
    DROP_COLLECTION = "drop_collection"
    BACKUP = "backup"
    RESTORE = "restore"
    MONITOR = "monitor"
    AUDIT = "audit"

class ResourceType(Enum):
    """Resource types for access control."""
    DATABASE = "database"
    COLLECTION = "collection"
    DOCUMENT = "document"
    INDEX = "index"
    SYSTEM = "system"

@dataclass
class AccessRule:
    """Individual access rule."""
    resource_type: ResourceType
    resource_name: str
    permissions: Set[Permission]
    conditions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Role:
    """User role with permissions."""
    role_id: str
    name: str
    description: str
    access_rules: List[AccessRule] = field(default_factory=list)
    inherits_from: List[str] = field(default_factory=list)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class User:
    """User with roles and permissions."""
    user_id: str
    username: str
    email: str
    roles: List[str] = field(default_factory=list)
    direct_permissions: List[AccessRule] = field(default_factory=list)
    is_active: bool = True
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    session_token: Optional[str] = None
    session_expires: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

class AccessControlManager:
    """MongoDB Role-Based Access Control manager."""
    
    def __init__(self) -> None:
        """Initialize access control manager."""
        self._roles: Dict[str, Role] = {}
        self._users: Dict[str, User] = {}
        self._active_sessions: Dict[str, User] = {}
        self._permission_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Initialize system roles
        self._initialize_system_roles()
    
    def _initialize_system_roles(self) -> None:
        """Create default system roles."""
        # Super Admin role
        super_admin = Role(
            role_id="super_admin",
            name="Super Administrator",
            description="Full system access with all permissions",
            access_rules=[
                AccessRule(
                    resource_type=ResourceType.SYSTEM,
                    resource_name="*",
                    permissions={Permission.ADMIN, Permission.READ, Permission.WRITE, 
                               Permission.DELETE, Permission.BACKUP, Permission.RESTORE,
                               Permission.MONITOR, Permission.AUDIT}
                )
            ],
            is_system_role=True
        )
        
        # Database Admin role
        db_admin = Role(
            role_id="db_admin",
            name="Database Administrator",
            description="Database administration with index and collection management",
            access_rules=[
                AccessRule(
                    resource_type=ResourceType.DATABASE,
                    resource_name="*",
                    permissions={Permission.READ, Permission.WRITE, Permission.DELETE,
                               Permission.CREATE_INDEX, Permission.DROP_INDEX,
                               Permission.CREATE_COLLECTION, Permission.DROP_COLLECTION,
                               Permission.BACKUP, Permission.MONITOR}
                )
            ],
            is_system_role=True
        )
        
        # Read-Write role
        read_write = Role(
            role_id="read_write",
            name="Read Write User",
            description="Standard user with read and write access",
            access_rules=[
                AccessRule(
                    resource_type=ResourceType.COLLECTION,
                    resource_name="*",
                    permissions={Permission.READ, Permission.WRITE}
                )
            ],
            is_system_role=True
        )
        
        # Read-Only role
        read_only = Role(
            role_id="read_only",
            name="Read Only User",
            description="Read-only access to collections",
            access_rules=[
                AccessRule(
                    resource_type=ResourceType.COLLECTION,
                    resource_name="*",
                    permissions={Permission.READ}
                )
            ],
            is_system_role=True
        )
        
        # Monitor role
        monitor = Role(
            role_id="monitor",
            name="Monitor User",
            description="Monitoring and audit access",
            access_rules=[
                AccessRule(
                    resource_type=ResourceType.SYSTEM,
                    resource_name="*",
                    permissions={Permission.MONITOR, Permission.AUDIT, Permission.READ}
                )
            ],
            is_system_role=True
        )
        
        # Store system roles
        for role in [super_admin, db_admin, read_write, read_only, monitor]:
            self._roles[role.role_id] = role
        
        logger.info("Initialized system roles")
    
    def create_role(self, role_id: str, name: str, description: str,
                   access_rules: List[AccessRule] = None,
                   inherits_from: List[str] = None) -> bool:
        """Create a new role."""
        try:
            if role_id in self._roles:
                logger.warning(f"Role already exists: {role_id}")
                return False
            
            # Validate inherited roles exist
            if inherits_from:
                for parent_role in inherits_from:
                    if parent_role not in self._roles:
                        raise ValueError(f"Parent role not found: {parent_role}")
            
            role = Role(
                role_id=role_id,
                name=name,
                description=description,
                access_rules=access_rules or [],
                inherits_from=inherits_from or []
            )
            
            self._roles[role_id] = role
            logger.info(f"Created role: {role_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create role {role_id}: {e}")
            return False
    
    def create_user(self, user_id: str, username: str, email: str,
                   password: str = None, roles: List[str] = None) -> bool:
        """Create a new user."""
        try:
            if user_id in self._users:
                logger.warning(f"User already exists: {user_id}")
                return False
            
            # Validate roles exist
            if roles:
                for role_id in roles:
                    if role_id not in self._roles:
                        raise ValueError(f"Role not found: {role_id}")
            
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = self._hash_password(password)
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                roles=roles or [],
                password_hash=password_hash
            )
            
            self._users[user_id] = user
            logger.info(f"Created user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create user {user_id}: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token."""
        try:
            # Find user by username
            user = None
            for u in self._users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                logger.warning(f"User not found: {username}")
                return None
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                logger.warning(f"Account locked: {username}")
                return None
            
            if not user.is_active:
                logger.warning(f"Account disabled: {username}")
                return None
            
            # Verify password
            if not user.password_hash or not self._verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                    logger.warning(f"Account locked due to failed attempts: {username}")
                
                return None
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            user.session_token = session_token
            user.session_expires = datetime.utcnow() + timedelta(hours=8)
            
            # Store active session
            self._active_sessions[session_token] = user
            
            logger.info(f"User authenticated: {username}")
            return session_token
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            return None
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate session token and return user."""
        if session_token not in self._active_sessions:
            return None
        
        user = self._active_sessions[session_token]
        
        # Check if session expired
        if user.session_expires and user.session_expires < datetime.utcnow():
            del self._active_sessions[session_token]
            user.session_token = None
            user.session_expires = None
            return None
        
        return user
    
    def check_permission(self, user_id: str, resource_type: ResourceType,
                        resource_name: str, permission: Permission,
                        context: Dict[str, Any] = None) -> bool:
        """Check if user has permission for resource."""
        try:
            # Get user
            if user_id not in self._users:
                return False
            
            user = self._users[user_id]
            
            if not user.is_active:
                return False
            
            # Check cache first
            cache_key = f"{user_id}:{resource_type.value}:{resource_name}:{permission.value}"
            if cache_key in self._permission_cache:
                cache_entry = self._permission_cache[cache_key]
                if cache_entry["expires"] > datetime.utcnow():
                    return cache_entry["allowed"]
            
            # Check direct permissions
            allowed = self._check_direct_permissions(user, resource_type, resource_name, permission, context)
            
            if not allowed:
                # Check role-based permissions
                allowed = self._check_role_permissions(user, resource_type, resource_name, permission, context)
            
            # Cache result
            self._permission_cache[cache_key] = {
                "allowed": allowed,
                "expires": datetime.utcnow() + timedelta(seconds=self._cache_ttl)
            }
            
            return allowed
            
        except Exception as e:
            logger.error(f"Permission check failed for user {user_id}: {e}")
            return False
    
    def _check_direct_permissions(self, user: User, resource_type: ResourceType,
                                 resource_name: str, permission: Permission,
                                 context: Dict[str, Any] = None) -> bool:
        """Check user's direct permissions."""
        for rule in user.direct_permissions:
            if self._rule_matches(rule, resource_type, resource_name, permission, context):
                return True
        return False
    
    def _check_role_permissions(self, user: User, resource_type: ResourceType,
                               resource_name: str, permission: Permission,
                               context: Dict[str, Any] = None) -> bool:
        """Check permissions from user's roles."""
        # Get all roles (including inherited)
        all_roles = self._get_user_roles_recursive(user.roles)
        
        for role_id in all_roles:
            if role_id not in self._roles:
                continue
            
            role = self._roles[role_id]
            for rule in role.access_rules:
                if self._rule_matches(rule, resource_type, resource_name, permission, context):
                    return True
        
        return False
    
    def _get_user_roles_recursive(self, role_ids: List[str]) -> Set[str]:
        """Get all roles including inherited ones."""
        all_roles = set(role_ids)
        
        for role_id in role_ids:
            if role_id in self._roles:
                role = self._roles[role_id]
                inherited = self._get_user_roles_recursive(role.inherits_from)
                all_roles.update(inherited)
        
        return all_roles
    
    def _rule_matches(self, rule: AccessRule, resource_type: ResourceType,
                     resource_name: str, permission: Permission,
                     context: Dict[str, Any] = None) -> bool:
        """Check if access rule matches the request."""
        # Check if rule has expired
        if rule.expires_at and rule.expires_at < datetime.utcnow():
            return False
        
        # Check resource type
        if rule.resource_type != resource_type:
            return False
        
        # Check resource name (support wildcards)
        if rule.resource_name != "*" and rule.resource_name != resource_name:
            return False
        
        # Check permission
        if permission not in rule.permissions and Permission.ADMIN not in rule.permissions:
            return False
        
        # Check conditions if specified
        if rule.conditions and context:
            for condition_key, condition_value in rule.conditions.items():
                if context.get(condition_key) != condition_value:
                    return False
        
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    def _verify_password(self, password: str, hash_str: str) -> bool:
        """Verify password against hash."""
        try:
            salt, pwd_hash = hash_str.split('$')
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == pwd_hash
        except:
            return False
    
    def add_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Add role to user."""
        if user_id not in self._users or role_id not in self._roles:
            return False
        
        user = self._users[user_id]
        if role_id not in user.roles:
            user.roles.append(role_id)
            user.updated_at = datetime.utcnow()
            # Clear permission cache for user
            self._clear_user_cache(user_id)
            logger.info(f"Added role {role_id} to user {user_id}")
        
        return True
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove role from user."""
        if user_id not in self._users:
            return False
        
        user = self._users[user_id]
        if role_id in user.roles:
            user.roles.remove(role_id)
            user.updated_at = datetime.utcnow()
            # Clear permission cache for user
            self._clear_user_cache(user_id)
            logger.info(f"Removed role {role_id} from user {user_id}")
        
        return True
    
    def _clear_user_cache(self, user_id -> None: str) -> None:
        """Clear permission cache for user."""
        keys_to_remove = [key for key in self._permission_cache if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self._permission_cache[key]
    
    def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive permissions for user."""
        if user_id not in self._users:
            return {"error": "User not found"}
        
        user = self._users[user_id]
        all_roles = self._get_user_roles_recursive(user.roles)
        
        permissions = {
            "user_id": user_id,
            "username": user.username,
            "roles": list(all_roles),
            "direct_permissions": len(user.direct_permissions),
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        return permissions
    
    def list_roles(self) -> List[Dict[str, Any]]:
        """List all roles."""
        return [
            {
                "role_id": role.role_id,
                "name": role.name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "access_rules_count": len(role.access_rules),
                "inherits_from": role.inherits_from
            }
            for role in self._roles.values()
        ]
    
    def list_users(self) -> List[Dict[str, Any]]:
        """List all users."""
        return [
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles,
                "is_active": user.is_active,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "mfa_enabled": user.mfa_enabled
            }
            for user in self._users.values()
        ]

# Global access control manager instance
_default_manager: Optional[AccessControlManager] = None

def get_access_control() -> AccessControlManager:
    """Get or create default access control manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = AccessControlManager()
    return _default_manager

# Export main classes and functions
__all__ = [
    'Permission',
    'ResourceType',
    'AccessRule',
    'Role',
    'User',
    'AccessControlManager',
    'get_access_control'
]