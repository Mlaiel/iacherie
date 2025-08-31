"""
 Access Controller - IA Influencer Agent Platform Enterprise
=============================================================
Module: backend/data_management/storage/access_controller.py
Author: Fahed Mlaiel (mlaiel@live.de)
=============================================================

Enterprise access control system with permission management,
audit logging, and role-based security for storage resources.

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- Security: Fahed Mlaiel
- DevOps: Fahed Mlaiel
"""

from typing import Dict, List, Optional, Any, Union, Set, Tuple, Callable
import logging
import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import aiofiles
import aiofiles.os
import jwt
import secrets
import bcrypt
from functools import wraps

logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """Access levels for resources"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"

class ResourceType(Enum):
    """Types of storage resources"""
    FILE = "file"
    DIRECTORY = "directory"
    BACKUP = "backup"
    ARCHIVE = "archive"
    TEMP = "temp"
    SYSTEM = "system"

class PermissionType(Enum):
    """Types of permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    MODIFY_PERMISSIONS = "modify_permissions"
    SHARE = "share"
    DOWNLOAD = "download"
    UPLOAD = "upload"

class UserRole(Enum):
    """User roles in the system"""
    GUEST = "guest"
    USER = "user"
    EDITOR = "editor"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SYSTEM = "system"

class AuditAction(Enum):
    """Actions that can be audited"""
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    FILE_ACCESSED = "file_accessed"
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    ROLE_CHANGED = "role_changed"
    POLICY_CREATED = "policy_created"
    POLICY_MODIFIED = "policy_modified"

@dataclass
class User:
    """Represents a user in the system"""
    user_id: str
    username: str
    email: str
    password_hash: str
    
    # User information
    full_name: str = ""
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_verified: bool = False
    
    # Security
    api_key: Optional[str] = None
    two_factor_enabled: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Additional attributes
    groups: List[str] = field(default_factory=list)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessPolicy:
    """Defines access policies for resources"""
    policy_id: str
    name: str
    description: str
    
    # Policy rules
    resource_patterns: List[str]  # File/directory patterns
    allowed_users: List[str] = field(default_factory=list)
    allowed_roles: List[UserRole] = field(default_factory=list)
    allowed_groups: List[str] = field(default_factory=list)
    denied_users: List[str] = field(default_factory=list)
    
    # Permissions
    permissions: List[PermissionType] = field(default_factory=list)
    
    # Conditions
    time_restrictions: Dict[str, Any] = field(default_factory=dict)  # time windows
    ip_restrictions: List[str] = field(default_factory=list)  # IP ranges
    location_restrictions: List[str] = field(default_factory=list)  # geographic
    
    # Settings
    priority: int = 50  # 1-100, higher = more priority
    is_active: bool = True
    expires_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    updated_at: Optional[datetime] = None

@dataclass
class AccessRequest:
    """Represents an access request"""
    request_id: str
    user_id: str
    resource_path: str
    resource_type: ResourceType
    requested_permissions: List[PermissionType]
    
    # Request context
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    
    # Security context
    authentication_method: str = "password"
    security_level: str = "standard"
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessDecision:
    """Result of access control decision"""
    request_id: str
    granted: bool
    granted_permissions: List[PermissionType] = field(default_factory=list)
    denied_permissions: List[PermissionType] = field(default_factory=list)
    
    # Decision details
    decision_reason: str = ""
    applied_policies: List[str] = field(default_factory=list)
    security_warnings: List[str] = field(default_factory=list)
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    
    # Audit information
    decided_at: datetime = field(default_factory=datetime.now)
    decision_time_ms: float = 0.0

@dataclass
class AuditEntry:
    """Audit log entry"""
    entry_id: str
    user_id: str
    action: AuditAction
    resource_path: str
    
    # Details
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    ip_address: str = ""
    user_agent: str = ""
    session_id: str = ""
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: Optional[float] = None
    
    # Security
    risk_score: float = 0.0
    anomaly_detected: bool = False

@dataclass
class AccessConfig:
    """Configuration for access controller"""
    storage_root_path: str
    users_directory: str
    policies_directory: str
    audit_directory: str
    
    # Security settings
    jwt_secret_key: str
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    max_failed_login_attempts: int = 5
    account_lockout_duration_minutes: int = 30
    
    # Session settings
    session_timeout_hours: int = 8
    require_2fa_for_admin: bool = True
    allow_concurrent_sessions: bool = True
    
    # Audit settings
    audit_enabled: bool = True
    audit_retention_days: int = 365
    detailed_audit_logging: bool = True
    real_time_audit_alerts: bool = True
    
    # Performance settings
    cache_permissions: bool = True
    cache_timeout_minutes: int = 15
    max_concurrent_requests: int = 1000
    
    # Default policies
    default_user_role: UserRole = UserRole.USER
    allow_guest_access: bool = False
    require_email_verification: bool = True

class AccessController:
    """
    Enterprise access control system for storage resources.
    
    Features:
    - Role-based access control (RBAC)
    - Policy-based permissions
    - Comprehensive audit logging
    - Session management
    - Security monitoring
    - Multi-factor authentication support
    """
    
    def __init__(self, config: AccessConfig):
        """Initialize access controller"""
        self.config = config
        self.users: Dict[str, User] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.audit_entries: List[AuditEntry] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Managers
        self.authentication_manager = AuthenticationManager(self)
        self.authorization_manager = AuthorizationManager(self)
        self.audit_manager = AuditManager(self)
        self.session_manager = SessionManager(self)
        
        # Caching
        self.permission_cache: Dict[str, Dict[str, Any]] = {}
        self.policy_cache: Dict[str, List[AccessPolicy]] = {}
        
        # Performance tracking
        self.metrics = {
            'total_requests': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'access_granted': 0,
            'access_denied': 0,
            'security_violations': 0,
            'average_decision_time': 0.0,
            'active_users': 0,
            'active_sessions': 0
        }
        
        # Initialize directories and load data
        self._initialize_access_directories()
        asyncio.create_task(self._load_initial_data())
        
        # Start background tasks
        asyncio.create_task(self._start_background_tasks())
        
        logger.info("AccessController initialized successfully")
    
    def _initialize_access_directories(self) -> None:
        """Initialize access control directories"""



        try:
            directories = [
                self.config.storage_root_path,
                self.config.users_directory,
                self.config.policies_directory,
                self.config.audit_directory
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            audit_dir = Path(self.config.audit_directory)
            (audit_dir / "security").mkdir(exist_ok=True)
            (audit_dir / "access").mkdir(exist_ok=True)
            (audit_dir / "authentication").mkdir(exist_ok=True)
            
            policies_dir = Path(self.config.policies_directory)
            (policies_dir / "active").mkdir(exist_ok=True)
            (policies_dir / "archived").mkdir(exist_ok=True)
            
            logger.info("Access control directories initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize access directories: {str(e)}")
            raise
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user account"""



        try:
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in user_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Check if user already exists
            username = user_data['username']
            email = user_data['email']
            
            if any(user.username == username for user in self.users.values()):
                return {
                    'success': False,
                    'error': f'Username already exists: {username}'
                }
            
            if any(user.email == email for user in self.users.values()):
                return {
                    'success': False,
                    'error': f'Email already exists: {email}'
                }
            
            # Validate password strength
            password_validation = self._validate_password(user_data['password'])
            if not password_validation['valid']:
                return {
                    'success': False,
                    'error': f'Password validation failed: {password_validation["error"]}'
                }
            
            # Generate user ID
            user_id = f"user_{int(time.time())}_{hash(username) & 0xFFFF:04x}"
            
            # Hash password
            password_hash = bcrypt.hashpw(
                user_data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Create user
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=user_data.get('full_name', ''),
                role=UserRole(user_data.get('role', self.config.default_user_role.value)),
                is_active=user_data.get('is_active', True),
                is_verified=not self.config.require_email_verification,
                api_key=secrets.token_urlsafe(32),
                groups=user_data.get('groups', []),
                metadata=user_data.get('metadata', {})
            )
            
            # Store user
            self.users[user_id] = user
            
            # Save user to disk
            await self._save_user(user)
            
            # Create audit entry
            await self.audit_manager.log_action(
                user_id=user_id,
                action=AuditAction.LOGIN,  # User creation
                resource_path="system",
                success=True,
                details={
                    'action': 'user_created',
                    'username': username,
                    'role': user.role.value
                }
            )
            
            logger.info(f"User created: {user_id} - {username}")
            
            return {
                'success': True,
                'user_id': user_id,
                'user_config': {
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value,
                    'api_key': user.api_key,
                    'requires_verification': not user.is_verified
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str = "",
        user_agent: str = ""
    ) -> Dict[str, Any]:
        """Authenticate user credentials"""



        try:
            start_time = time.time()
            
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                # Log failed authentication
                await self.audit_manager.log_action(
                    user_id="unknown",
                    action=AuditAction.LOGIN,
                    resource_path="system",
                    success=False,
                    details={'username': username, 'reason': 'user_not_found'},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                self.metrics['failed_authentications'] += 1
                
                return {
                    'success': False,
                    'error': 'Invalid credentials',
                    'authenticated': False
                }
            
            # Check if account is locked
            if user.locked_until and datetime.now() < user.locked_until:
                await self.audit_manager.log_action(
                    user_id=user.user_id,
                    action=AuditAction.LOGIN,
                    resource_path="system",
                    success=False,
                    details={'reason': 'account_locked'},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                return {
                    'success': False,
                    'error': 'Account is locked',
                    'authenticated': False,
                    'locked_until': user.locked_until.isoformat()
                }
            
            # Check if account is active
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Account is deactivated',
                    'authenticated': False
                }
            
            # Verify password
            password_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            )
            
            if not password_valid:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.config.max_failed_login_attempts:
                    user.locked_until = datetime.now() + timedelta(
                        minutes=self.config.account_lockout_duration_minutes
                    )
                
                await self._save_user(user)
                
                await self.audit_manager.log_action(
                    user_id=user.user_id,
                    action=AuditAction.LOGIN,
                    resource_path="system",
                    success=False,
                    details={'reason': 'invalid_password'},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                self.metrics['failed_authentications'] += 1
                
                return {
                    'success': False,
                    'error': 'Invalid credentials',
                    'authenticated': False
                }
            
            # Authentication successful
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            
            await self._save_user(user)
            
            # Generate JWT token
            token = await self.authentication_manager.generate_token(user)
            
            # Create session
            session_id = await self.session_manager.create_session(
                user, ip_address, user_agent
            )
            
            # Log successful authentication
            await self.audit_manager.log_action(
                user_id=user.user_id,
                action=AuditAction.LOGIN,
                resource_path="system",
                success=True,
                details={'session_id': session_id},
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )
            
            auth_time = (time.time() - start_time) * 1000
            self.metrics['successful_authentications'] += 1
            
            return {
                'success': True,
                'authenticated': True,
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role.value,
                'token': token,
                'session_id': session_id,
                'expires_at': (datetime.now() + timedelta(hours=self.config.jwt_expiration_hours)).isoformat(),
                'authentication_time_ms': auth_time,
                'requires_2fa': user.two_factor_enabled and self.config.require_2fa_for_admin and user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
            }
            
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'authenticated': False
            }
    
    async def check_access(
        self,
        user_id: str,
        resource_path: str,
        permissions: List[PermissionType],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check if user has access to resource with specified permissions"""



        try:
            start_time = time.time()
            
            # Get user
            if user_id not in self.users:
                return {
                    'success': False,
                    'error': f'User not found: {user_id}',
                    'access_granted': False
                }
            
            user = self.users[user_id]
            context = context or {}
            
            # Create access request
            request = AccessRequest(
                request_id=f"req_{int(time.time())}_{secrets.token_hex(4)}",
                user_id=user_id,
                resource_path=resource_path,
                resource_type=self._determine_resource_type(resource_path),
                requested_permissions=permissions,
                ip_address=context.get('ip_address', ''),
                user_agent=context.get('user_agent', ''),
                session_id=context.get('session_id', ''),
                authentication_method=context.get('auth_method', 'jwt'),
                metadata=context
            )
            
            # Check authorization
            decision = await self.authorization_manager.make_decision(request, user)
            
            decision_time = (time.time() - start_time) * 1000
            decision.decision_time_ms = decision_time
            
            # Update metrics
            self.metrics['total_requests'] += 1
            if decision.granted:
                self.metrics['access_granted'] += 1
            else:
                self.metrics['access_denied'] += 1
            
            # Update average decision time
            old_avg = self.metrics['average_decision_time']
            total_requests = self.metrics['total_requests']
            self.metrics['average_decision_time'] = (
                (old_avg * (total_requests - 1) + decision_time) / total_requests
            )
            
            # Log access attempt
            await self.audit_manager.log_action(
                user_id=user_id,
                action=AuditAction.ACCESS_GRANTED if decision.granted else AuditAction.ACCESS_DENIED,
                resource_path=resource_path,
                success=decision.granted,
                details={
                    'requested_permissions': [p.value for p in permissions],
                    'granted_permissions': [p.value for p in decision.granted_permissions],
                    'decision_reason': decision.decision_reason,
                    'applied_policies': decision.applied_policies
                },
                ip_address=context.get('ip_address', ''),
                user_agent=context.get('user_agent', ''),
                session_id=context.get('session_id', ''),
                duration_ms=decision_time
            )
            
            return {
                'success': True,
                'access_granted': decision.granted,
                'granted_permissions': [p.value for p in decision.granted_permissions],
                'denied_permissions': [p.value for p in decision.denied_permissions],
                'decision_reason': decision.decision_reason,
                'security_warnings': decision.security_warnings,
                'decision_time_ms': decision_time,
                'expires_at': decision.expires_at.isoformat() if decision.expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Access check failed for user {user_id} on {resource_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'access_granted': False
            }
    
    async def create_access_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new access policy"""



        try:
            # Validate required fields
            required_fields = ['name', 'resource_patterns']
            for field in required_fields:
                if field not in policy_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate policy ID
            policy_id = f"policy_{int(time.time())}_{hash(policy_data['name']) & 0xFFFF:04x}"
            
            # Create policy
            policy = AccessPolicy(
                policy_id=policy_id,
                name=policy_data['name'],
                description=policy_data.get('description', ''),
                resource_patterns=policy_data['resource_patterns'],
                allowed_users=policy_data.get('allowed_users', []),
                allowed_roles=[UserRole(role) for role in policy_data.get('allowed_roles', [])],
                allowed_groups=policy_data.get('allowed_groups', []),
                denied_users=policy_data.get('denied_users', []),
                permissions=[PermissionType(perm) for perm in policy_data.get('permissions', [])],
                time_restrictions=policy_data.get('time_restrictions', {}),
                ip_restrictions=policy_data.get('ip_restrictions', []),
                location_restrictions=policy_data.get('location_restrictions', []),
                priority=policy_data.get('priority', 50),
                is_active=policy_data.get('is_active', True),
                expires_at=datetime.fromisoformat(policy_data['expires_at']) if policy_data.get('expires_at') else None,
                created_by=policy_data.get('created_by', 'system')
            )
            
            # Store policy
            self.policies[policy_id] = policy
            
            # Clear policy cache
            self.policy_cache.clear()
            
            # Save policy to disk
            await self._save_policy(policy)
            
            # Create audit entry
            await self.audit_manager.log_action(
                user_id=policy.created_by,
                action=AuditAction.POLICY_CREATED,
                resource_path="system",
                success=True,
                details={
                    'policy_id': policy_id,
                    'policy_name': policy.name,
                    'resource_patterns': policy.resource_patterns
                }
            )
            
            logger.info(f"Access policy created: {policy_id} - {policy.name}")
            
            return {
                'success': True,
                'policy_id': policy_id,
                'policy_config': {
                    'name': policy.name,
                    'resource_patterns': policy.resource_patterns,
                    'permissions': [p.value for p in policy.permissions],
                    'priority': policy.priority,
                    'is_active': policy.is_active
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create access policy: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_permissions(self, user_id: str, resource_path: str) -> Dict[str, Any]:
        """Get effective permissions for user on resource"""



        try:
            if user_id not in self.users:
                return {
                    'success': False,
                    'error': f'User not found: {user_id}'
                }
            
            user = self.users[user_id]
            
            # Check cache first
            cache_key = f"{user_id}:{resource_path}"
            if self.config.cache_permissions and cache_key in self.permission_cache:
                cached_entry = self.permission_cache[cache_key]
                
                # Check if cache is still valid
                if datetime.now() < cached_entry['expires_at']:
                    return {
                        'success': True,
                        'permissions': cached_entry['permissions'],
                        'source': 'cache'
                    }
            
            # Calculate effective permissions
            effective_permissions = await self.authorization_manager.calculate_effective_permissions(
                user, resource_path
            )
            
            # Cache result
            if self.config.cache_permissions:
                self.permission_cache[cache_key] = {
                    'permissions': effective_permissions,
                    'expires_at': datetime.now() + timedelta(minutes=self.config.cache_timeout_minutes)
                }
            
            return {
                'success': True,
                'permissions': effective_permissions,
                'source': 'calculated'
            }
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_audit_log(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get audit log entries with filtering"""



        try:
            return await self.audit_manager.get_audit_entries(filters, limit)
            
        except Exception as e:
            logger.error(f"Failed to get audit log: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_access_statistics(self) -> Dict[str, Any]:
        """Get comprehensive access control statistics"""



        try:
            # User statistics
            total_users = len(self.users)
            active_users = len([u for u in self.users.values() if u.is_active])
            
            # Role distribution
            role_distribution = {}
            for role in UserRole:
                role_distribution[role.value] = len([
                    u for u in self.users.values() if u.role == role
                ])
            
            # Policy statistics
            total_policies = len(self.policies)
            active_policies = len([p for p in self.policies.values() if p.is_active])
            
            # Recent activity
            last_24h = datetime.now() - timedelta(hours=24)
            recent_logins = len([
                u for u in self.users.values()
                if u.last_login and u.last_login >= last_24h
            ])
            
            return {
                'users': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'recent_logins_24h': recent_logins,
                    'role_distribution': role_distribution
                },
                'policies': {
                    'total_policies': total_policies,
                    'active_policies': active_policies
                },
                'sessions': {
                    'active_sessions': len(self.active_sessions)
                },
                'performance': self.metrics,
                'security': {
                    'authentication_success_rate': (
                        self.metrics['successful_authentications'] / 
                        max(self.metrics['successful_authentications'] + self.metrics['failed_authentications'], 1)
                    ) * 100,
                    'access_success_rate': (
                        self.metrics['access_granted'] / 
                        max(self.metrics['total_requests'], 1)
                    ) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get access statistics: {str(e)}")
            return {'error': str(e)}
    
    # Private implementation methods
    
    def _validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        if len(password) < self.config.password_min_length:
            return {
                'valid': False,
                'error': f'Password must be at least {self.config.password_min_length} characters'
            }
        
        # Add more password strength checks here
        # (uppercase, lowercase, digits, special characters, etc.)
        
        return {'valid': True}
    
    def _determine_resource_type(self, resource_path: str) -> ResourceType:
        """Determine resource type from path"""
        path = Path(resource_path)
        
        if 'backup' in str(path):
            return ResourceType.BACKUP
        elif 'archive' in str(path):
            return ResourceType.ARCHIVE
        elif 'temp' in str(path):
            return ResourceType.TEMP
        elif path.is_dir():
            return ResourceType.DIRECTORY
        else:
            return ResourceType.FILE
    
    async def _load_initial_data(self) -> None:
        """Load initial data from disk"""



        try:
            # Load users
            users_dir = Path(self.config.users_directory)
            if users_dir.exists():
                for user_file in users_dir.glob("*.json"):
                    try:
                        async with aiofiles.open(user_file, 'r') as f:
                            user_data = json.loads(await f.read())
                            
                        # Reconstruct user object
                        user = User(
                            user_id=user_data['user_id'],
                            username=user_data['username'],
                            email=user_data['email'],
                            password_hash=user_data['password_hash'],
                            full_name=user_data.get('full_name', ''),
                            role=UserRole(user_data.get('role', 'user')),
                            is_active=user_data.get('is_active', True),
                            is_verified=user_data.get('is_verified', False),
                            api_key=user_data.get('api_key'),
                            two_factor_enabled=user_data.get('two_factor_enabled', False),
                            last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
                            failed_login_attempts=user_data.get('failed_login_attempts', 0),
                            locked_until=datetime.fromisoformat(user_data['locked_until']) if user_data.get('locked_until') else None,
                            created_at=datetime.fromisoformat(user_data.get('created_at', datetime.now().isoformat())),
                            updated_at=datetime.fromisoformat(user_data['updated_at']) if user_data.get('updated_at') else None,
                            groups=user_data.get('groups', []),
                            permissions=user_data.get('permissions', {}),
                            metadata=user_data.get('metadata', {})
                        )
                        
                        self.users[user.user_id] = user
                        
                    except Exception as e:
                        logger.error(f"Failed to load user from {user_file}: {str(e)}")
            
            # Load policies
            policies_dir = Path(self.config.policies_directory) / "active"
            if policies_dir.exists():
                for policy_file in policies_dir.glob("*.json"):
                    try:
                        async with aiofiles.open(policy_file, 'r') as f:
                            policy_data = json.loads(await f.read())
                        
                        # Reconstruct policy object
                        policy = AccessPolicy(
                            policy_id=policy_data['policy_id'],
                            name=policy_data['name'],
                            description=policy_data.get('description', ''),
                            resource_patterns=policy_data['resource_patterns'],
                            allowed_users=policy_data.get('allowed_users', []),
                            allowed_roles=[UserRole(role) for role in policy_data.get('allowed_roles', [])],
                            allowed_groups=policy_data.get('allowed_groups', []),
                            denied_users=policy_data.get('denied_users', []),
                            permissions=[PermissionType(perm) for perm in policy_data.get('permissions', [])],
                            time_restrictions=policy_data.get('time_restrictions', {}),
                            ip_restrictions=policy_data.get('ip_restrictions', []),
                            location_restrictions=policy_data.get('location_restrictions', []),
                            priority=policy_data.get('priority', 50),
                            is_active=policy_data.get('is_active', True),
                            expires_at=datetime.fromisoformat(policy_data['expires_at']) if policy_data.get('expires_at') else None,
                            created_at=datetime.fromisoformat(policy_data.get('created_at', datetime.now().isoformat())),
                            created_by=policy_data.get('created_by', 'system'),
                            updated_at=datetime.fromisoformat(policy_data['updated_at']) if policy_data.get('updated_at') else None
                        )
                        
                        self.policies[policy.policy_id] = policy
                        
                    except Exception as e:
                        logger.error(f"Failed to load policy from {policy_file}: {str(e)}")
            
            logger.info(f"Loaded {len(self.users)} users and {len(self.policies)} policies")
            
        except Exception as e:
            logger.error(f"Failed to load initial data: {str(e)}")
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""



        try:
            # Start session cleanup
            asyncio.create_task(self._session_cleanup_task())
            
            # Start cache cleanup
            asyncio.create_task(self._cache_cleanup_task())
            
            # Start audit cleanup
            asyncio.create_task(self._audit_cleanup_task())
            
        except Exception as e:
            logger.error(f"Failed to start background tasks: {str(e)}")
    
    async def _session_cleanup_task(self) -> None:
        """Clean up expired sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session_data in self.active_sessions.items():
                    if current_time > session_data['expires_at']:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.active_sessions[session_id]
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except Exception as e:
                logger.error(f"Session cleanup error: {str(e)}")
    
    async def _cache_cleanup_task(self) -> None:
        """Clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                
                current_time = datetime.now()
                expired_entries = []
                
                for cache_key, cache_data in self.permission_cache.items():
                    if current_time > cache_data['expires_at']:
                        expired_entries.append(cache_key)
                
                for cache_key in expired_entries:
                    del self.permission_cache[cache_key]
                
                if expired_entries:
                    logger.info(f"Cleaned up {len(expired_entries)} expired cache entries")
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {str(e)}")
    
    async def _audit_cleanup_task(self) -> None:
        """Clean up old audit entries"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Clean up audit entries older than retention period
                cutoff_date = datetime.now() - timedelta(days=self.config.audit_retention_days)
                
                # This would implement actual audit cleanup
                # For now, just log the task
                logger.debug("Audit cleanup task executed")
                
            except Exception as e:
                logger.error(f"Audit cleanup error: {str(e)}")
    
    async def _save_user(self, user: User) -> None:
        """Save user to disk"""



        try:
            user_path = Path(self.config.users_directory) / f"{user.user_id}.json"
            
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'full_name': user.full_name,
                'role': user.role.value,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'api_key': user.api_key,
                'two_factor_enabled': user.two_factor_enabled,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'failed_login_attempts': user.failed_login_attempts,
                'locked_until': user.locked_until.isoformat() if user.locked_until else None,
                'created_at': user.created_at.isoformat(),
                'updated_at': datetime.now().isoformat(),
                'groups': user.groups,
                'permissions': user.permissions,
                'metadata': user.metadata
            }
            
            async with aiofiles.open(user_path, 'w') as f:
                await f.write(json.dumps(user_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save user: {str(e)}")
    
    async def _save_policy(self, policy: AccessPolicy) -> None:
        """Save policy to disk"""



        try:
            policy_path = Path(self.config.policies_directory) / "active" / f"{policy.policy_id}.json"
            
            policy_data = {
                'policy_id': policy.policy_id,
                'name': policy.name,
                'description': policy.description,
                'resource_patterns': policy.resource_patterns,
                'allowed_users': policy.allowed_users,
                'allowed_roles': [role.value for role in policy.allowed_roles],
                'allowed_groups': policy.allowed_groups,
                'denied_users': policy.denied_users,
                'permissions': [perm.value for perm in policy.permissions],
                'time_restrictions': policy.time_restrictions,
                'ip_restrictions': policy.ip_restrictions,
                'location_restrictions': policy.location_restrictions,
                'priority': policy.priority,
                'is_active': policy.is_active,
                'expires_at': policy.expires_at.isoformat() if policy.expires_at else None,
                'created_at': policy.created_at.isoformat(),
                'created_by': policy.created_by,
                'updated_at': datetime.now().isoformat()
            }
            
            async with aiofiles.open(policy_path, 'w') as f:
                await f.write(json.dumps(policy_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save policy: {str(e)}")


class AuthenticationManager:
    """Manages user authentication"""
    
    def __init__(self, access_controller: AccessController):
        """Initialize authentication manager"""
        self.access_controller = access_controller
    
    async def generate_token(self, user: User) -> str:
        """Generate JWT token for user"""



        try:
            payload = {
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role.value,
                'iat': int(time.time()),
                'exp': int(time.time()) + (self.access_controller.config.jwt_expiration_hours * 3600)
            }
            
            token = jwt.encode(
                payload,
                self.access_controller.config.jwt_secret_key,
                algorithm='HS256'
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            raise
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""



        try:
            payload = jwt.decode(
                token,
                self.access_controller.config.jwt_secret_key,
                algorithms=['HS256']
            )
            
            return {
                'valid': True,
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'Token expired'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'error': 'Invalid token'
            }
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }


class AuthorizationManager:
    """Manages authorization decisions"""
    
    def __init__(self, access_controller: AccessController):
        """Initialize authorization manager"""
        self.access_controller = access_controller
    
    async def make_decision(self, request: AccessRequest, user: User) -> AccessDecision:
        """Make authorization decision"""



        try:
            start_time = datetime.now()
            
            # Get applicable policies
            applicable_policies = await self._get_applicable_policies(request, user)
            
            # Calculate permissions
            granted_permissions = []
            denied_permissions = []
            decision_reason = ""
            security_warnings = []
            
            # Check each requested permission
            for permission in request.requested_permissions:
                if await self._check_permission(request, user, permission, applicable_policies):
                    granted_permissions.append(permission)
                else:
                    denied_permissions.append(permission)
            
            # Determine overall decision
            granted = len(granted_permissions) > 0 and len(denied_permissions) == 0
            
            if granted:
                decision_reason = "Access granted based on applicable policies"
            else:
                decision_reason = "Access denied - insufficient permissions"
            
            # Create decision
            decision = AccessDecision(
                request_id=request.request_id,
                granted=granted,
                granted_permissions=granted_permissions,
                denied_permissions=denied_permissions,
                decision_reason=decision_reason,
                applied_policies=[p.policy_id for p in applicable_policies],
                security_warnings=security_warnings,
                decided_at=datetime.now()
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Authorization decision failed: {str(e)}")
            
            # Return deny-all decision on error
            return AccessDecision(
                request_id=request.request_id,
                granted=False,
                denied_permissions=request.requested_permissions,
                decision_reason=f"Authorization error: {str(e)}"
            )
    
    async def calculate_effective_permissions(self, user: User, resource_path: str) -> List[str]:
        """Calculate effective permissions for user on resource"""



        try:
            # Get applicable policies
            request = AccessRequest(
                request_id="calc_perms",
                user_id=user.user_id,
                resource_path=resource_path,
                resource_type=self.access_controller._determine_resource_type(resource_path),
                requested_permissions=list(PermissionType)
            )
            
            applicable_policies = await self._get_applicable_policies(request, user)
            
            # Collect all permissions from applicable policies
            effective_permissions = set()
            
            for policy in applicable_policies:
                for permission in policy.permissions:
                    effective_permissions.add(permission.value)
            
            # Add role-based permissions
            role_permissions = self._get_role_permissions(user.role)
            effective_permissions.update(role_permissions)
            
            return list(effective_permissions)
            
        except Exception as e:
            logger.error(f"Effective permissions calculation failed: {str(e)}")
            return []
    
    async def _get_applicable_policies(self, request: AccessRequest, user: User) -> List[AccessPolicy]:
        """Get policies applicable to the request"""
        applicable_policies = []
        
        for policy in self.access_controller.policies.values():
            if not policy.is_active:
                continue
            
            if policy.expires_at and datetime.now() > policy.expires_at:
                continue
            
            # Check if resource matches policy patterns
            if not self._resource_matches_patterns(request.resource_path, policy.resource_patterns):
                continue
            
            # Check user/role/group permissions
            if await self._user_matches_policy(user, policy):
                applicable_policies.append(policy)
        
        # Sort by priority (higher priority first)
        applicable_policies.sort(key=lambda p: p.priority, reverse=True)
        
        return applicable_policies
    
    def _resource_matches_patterns(self, resource_path: str, patterns: List[str]) -> bool:
        """Check if resource path matches any of the patterns"""
        for pattern in patterns:
            # Simple glob-like pattern matching
            if pattern == "*" or pattern in resource_path:
                return True
        return False
    
    async def _user_matches_policy(self, user: User, policy: AccessPolicy) -> bool:
        """Check if user matches policy criteria"""
        # Check denied users first
        if user.user_id in policy.denied_users:
            return False
        
        # Check allowed users
        if policy.allowed_users and user.user_id in policy.allowed_users:
            return True
        
        # Check allowed roles
        if policy.allowed_roles and user.role in policy.allowed_roles:
            return True
        
        # Check allowed groups
        if policy.allowed_groups:
            for group in user.groups:
                if group in policy.allowed_groups:
                    return True
        
        # If no specific allow rules, default to deny
        if not policy.allowed_users and not policy.allowed_roles and not policy.allowed_groups:
            return True
        
        return False
    
    async def _check_permission(
        self,
        request: AccessRequest,
        user: User,
        permission: PermissionType,
        applicable_policies: List[AccessPolicy]
    ) -> bool:
        """Check if user has specific permission"""
        # Check if any applicable policy grants the permission
        for policy in applicable_policies:
            if permission in policy.permissions:
                return True
        
        # Check role-based permissions
        role_permissions = self._get_role_permissions(user.role)
        if permission.value in role_permissions:
            return True
        
        return False
    
    def _get_role_permissions(self, role: UserRole) -> List[str]:
        """Get default permissions for role"""
        role_permissions = {
            UserRole.GUEST: ['read'],
            UserRole.USER: ['read', 'write', 'download'],
            UserRole.EDITOR: ['read', 'write', 'delete', 'download', 'upload'],
            UserRole.MODERATOR: ['read', 'write', 'delete', 'download', 'upload', 'share'],
            UserRole.ADMIN: ['read', 'write', 'delete', 'execute', 'download', 'upload', 'share', 'modify_permissions'],
            UserRole.SUPER_ADMIN: [p.value for p in PermissionType],
            UserRole.SYSTEM: [p.value for p in PermissionType]
        }
        
        return role_permissions.get(role, [])


class AuditManager:
    """Manages audit logging"""
    
    def __init__(self, access_controller: AccessController):
        """Initialize audit manager"""
        self.access_controller = access_controller
    
    async def log_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_path: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
        user_agent: str = "",
        session_id: str = "",
        duration_ms: Optional[float] = None
    ) -> None:
        """Log audit action"""



        try:
            if not self.access_controller.config.audit_enabled:
                return
            
            entry_id = f"audit_{int(time.time())}_{secrets.token_hex(4)}"
            
            audit_entry = AuditEntry(
                entry_id=entry_id,
                user_id=user_id,
                action=action,
                resource_path=resource_path,
                success=success,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id,
                duration_ms=duration_ms
            )
            
            # Add to in-memory log
            self.access_controller.audit_entries.append(audit_entry)
            
            # Keep only recent entries in memory
            if len(self.access_controller.audit_entries) > 10000:
                self.access_controller.audit_entries = self.access_controller.audit_entries[-5000:]
            
            # Save to disk if detailed logging is enabled
            if self.access_controller.config.detailed_audit_logging:
                await self._save_audit_entry(audit_entry)
            
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}")
    
    async def get_audit_entries(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get audit entries with filtering"""



        try:
            filters = filters or {}
            filtered_entries = []
            
            for entry in reversed(self.access_controller.audit_entries):
                # Apply filters
                if 'user_id' in filters and entry.user_id != filters['user_id']:
                    continue
                
                if 'action' in filters and entry.action.value != filters['action']:
                    continue
                
                if 'resource_path' in filters and filters['resource_path'] not in entry.resource_path:
                    continue
                
                if 'success' in filters and entry.success != filters['success']:
                    continue
                
                if 'start_time' in filters:
                    start_time = datetime.fromisoformat(filters['start_time'])
                    if entry.timestamp < start_time:
                        continue
                
                if 'end_time' in filters:
                    end_time = datetime.fromisoformat(filters['end_time'])
                    if entry.timestamp > end_time:
                        continue
                
                # Convert to dict
                entry_dict = {
                    'entry_id': entry.entry_id,
                    'user_id': entry.user_id,
                    'action': entry.action.value,
                    'resource_path': entry.resource_path,
                    'success': entry.success,
                    'details': entry.details,
                    'ip_address': entry.ip_address,
                    'user_agent': entry.user_agent,
                    'session_id': entry.session_id,
                    'timestamp': entry.timestamp.isoformat(),
                    'duration_ms': entry.duration_ms,
                    'risk_score': entry.risk_score,
                    'anomaly_detected': entry.anomaly_detected
                }
                
                filtered_entries.append(entry_dict)
                
                if len(filtered_entries) >= limit:
                    break
            
            return {
                'success': True,
                'entries': filtered_entries,
                'total_count': len(filtered_entries)
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit entries: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _save_audit_entry(self, audit_entry: AuditEntry) -> None:
        """Save audit entry to disk"""



        try:
            # Create date-based directory structure
            date_str = audit_entry.timestamp.strftime("%Y/%m/%d")
            audit_dir = Path(self.access_controller.config.audit_directory) / "access" / date_str
            audit_dir.mkdir(parents=True, exist_ok=True)
            
            # Save entry
            entry_file = audit_dir / f"{audit_entry.entry_id}.json"
            
            entry_data = {
                'entry_id': audit_entry.entry_id,
                'user_id': audit_entry.user_id,
                'action': audit_entry.action.value,
                'resource_path': audit_entry.resource_path,
                'success': audit_entry.success,
                'details': audit_entry.details,
                'ip_address': audit_entry.ip_address,
                'user_agent': audit_entry.user_agent,
                'session_id': audit_entry.session_id,
                'timestamp': audit_entry.timestamp.isoformat(),
                'duration_ms': audit_entry.duration_ms,
                'risk_score': audit_entry.risk_score,
                'anomaly_detected': audit_entry.anomaly_detected
            }
            
            async with aiofiles.open(entry_file, 'w') as f:
                await f.write(json.dumps(entry_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save audit entry: {str(e)}")


class SessionManager:
    """Manages user sessions"""
    
    def __init__(self, access_controller: AccessController):
        """Initialize session manager"""
        self.access_controller = access_controller
    
    async def create_session(self, user: User, ip_address: str, user_agent: str) -> str:
        """Create new user session"""



        try:
            session_id = secrets.token_urlsafe(32)
            
            session_data = {
                'session_id': session_id,
                'user_id': user.user_id,
                'username': user.username,
                'role': user.role.value,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=self.access_controller.config.session_timeout_hours),
                'last_activity': datetime.now()
            }
            
            # Check concurrent session limit
            if not self.access_controller.config.allow_concurrent_sessions:
                # Remove existing sessions for user
                existing_sessions = [
                    sid for sid, data in self.access_controller.active_sessions.items()
                    if data['user_id'] == user.user_id
                ]
                
                for sid in existing_sessions:
                    del self.access_controller.active_sessions[sid]
            
            self.access_controller.active_sessions[session_id] = session_data
            
            # Update metrics
            self.access_controller.metrics['active_sessions'] = len(self.access_controller.active_sessions)
            
            return session_id
            
        except Exception as e:
            logger.error(f"Session creation failed: {str(e)}")
            raise
    
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate session"""



        try:
            if session_id not in self.access_controller.active_sessions:
                return {
                    'valid': False,
                    'error': 'Session not found'
                }
            
            session_data = self.access_controller.active_sessions[session_id]
            
            # Check if session is expired
            if datetime.now() > session_data['expires_at']:
                del self.access_controller.active_sessions[session_id]
                return {
                    'valid': False,
                    'error': 'Session expired'
                }
            
            # Update last activity
            session_data['last_activity'] = datetime.now()
            
            return {
                'valid': True,
                'session_data': session_data
            }
            
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def terminate_session(self, session_id: str) -> Dict[str, Any]:
        """Terminate session"""



        try:
            if session_id in self.access_controller.active_sessions:
                session_data = self.access_controller.active_sessions[session_id]
                del self.access_controller.active_sessions[session_id]
                
                # Log session termination
                await self.access_controller.audit_manager.log_action(
                    user_id=session_data['user_id'],
                    action=AuditAction.LOGOUT,
                    resource_path="system",
                    success=True,
                    details={'session_id': session_id},
                    session_id=session_id
                )
                
                return {
                    'success': True,
                    'message': 'Session terminated'
                }
            else:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
            
        except Exception as e:
            logger.error(f"Session termination failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Decorator for access control
def require_permission(permission: PermissionType):
    """Decorator to require specific permission for function access"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would implement the actual permission check
            # For now, just a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Export classes and functions
__all__ = [
    'AccessController',
    'AuthenticationManager',
    'AuthorizationManager',
    'AuditManager',
    'SessionManager',
    'User',
    'AccessPolicy',
    'AccessRequest',
    'AccessDecision',
    'AuditEntry',
    'AccessConfig',
    'AccessLevel',
    'ResourceType',
    'PermissionType',
    'UserRole',
    'AuditAction',
    'require_permission'
]
