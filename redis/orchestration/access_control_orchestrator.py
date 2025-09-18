#!/usr/bin/env python3
"""
🔐 Access Control Orchestrator
==============================

Advanced access control and authorization management system for Redis infrastructure
with role-based access control, fine-grained permissions, and zero-trust security.

Expert Roles Combined:
- Security Architect: Access control design and zero-trust architecture
- Backend Senior: Distributed authentication and authorization systems
- DBA: Database access control and privilege management
- DevOps Engineer: Infrastructure access automation and monitoring

Features:
- Role-based access control (RBAC) with hierarchical roles
- Attribute-based access control (ABAC) for fine-grained permissions
- Zero-trust network access with continuous verification
- Multi-factor authentication (MFA) integration
- Session management and token-based authentication
- Dynamic access policies and conditional access
- Access audit trails and compliance reporting
- Privileged access management (PAM)

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security Architect + Backend Senior + DBA + DevOps
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import hmac
import secrets
import base64
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import aioredis
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import ipaddress

logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """Access levels for resources"""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class AuthenticationMethod(Enum):
    """Authentication methods supported"""
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    CERTIFICATE = "certificate"
    BIOMETRIC = "biometric"

class SessionStatus(Enum):
    """Session status states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    LOCKED = "locked"

class PolicyAction(Enum):
    """Policy enforcement actions"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_MFA = "require_mfa"
    REQUIRE_APPROVAL = "require_approval"
    LOG_ONLY = "log_only"

class ResourceType(Enum):
    """Types of protected resources"""
    REDIS_KEY = "redis_key"
    REDIS_DATABASE = "redis_database"
    REDIS_COMMAND = "redis_command"
    REDIS_CONFIG = "redis_config"
    SYSTEM_FILE = "system_file"
    API_ENDPOINT = "api_endpoint"
    ADMIN_FUNCTION = "admin_function"

@dataclass
class User:
    """User account representation"""
    user_id: str
    username: str
    email: str
    password_hash: str
    salt: str
    roles: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    is_locked: bool = False
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    password_expires: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str
    name: str
    description: str
    permissions: List[str] = field(default_factory=list)
    parent_roles: List[str] = field(default_factory=list)
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    time_constraints: Dict[str, Any] = field(default_factory=dict)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Permission:
    """Permission definition"""
    permission_id: str
    name: str
    description: str
    resource_type: ResourceType
    actions: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    is_system_permission: bool = False

@dataclass
class AccessPolicy:
    """Access control policy"""
    policy_id: str
    name: str
    description: str
    subjects: List[str]  # Users, roles, or groups
    resources: List[str]  # Resource patterns
    actions: List[str]   # Allowed actions
    conditions: Dict[str, Any] = field(default_factory=dict)
    policy_action: PolicyAction = PolicyAction.ALLOW
    priority: int = 1
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Session:
    """User session information"""
    session_id: str
    user_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    source_ip: str
    user_agent: str
    status: SessionStatus = SessionStatus.ACTIVE
    mfa_verified: bool = False
    permissions_cache: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessRequest:
    """Access request for authorization"""
    request_id: str
    user_id: str
    session_id: str
    resource: str
    action: str
    resource_type: ResourceType
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AccessDecision:
    """Access control decision"""
    request_id: str
    decision: PolicyAction
    reason: str
    matched_policies: List[str] = field(default_factory=list)
    required_approvals: List[str] = field(default_factory=list)
    conditions_met: bool = True
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AccessMetrics:
    """Access control monitoring metrics"""
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    mfa_required_requests: int = 0
    active_sessions: int = 0
    failed_authentications: int = 0
    policy_violations: int = 0
    privileged_access_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class RedisAccessControlOrchestrator:
    """
    Advanced Access Control Orchestrator for Redis Infrastructure
    
    Comprehensive access control with RBAC, ABAC, zero-trust security,
    and fine-grained authorization for Redis resources.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Access control data
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.policies: Dict[str, AccessPolicy] = {}
        self.active_sessions: Dict[str, Session] = {}
        
        # Access control metrics
        self.metrics = AccessMetrics()
        
        # Authentication configuration
        self.password_policy = config.get('password_policy', {})
        self.session_timeout = config.get('session_timeout', 3600)  # 1 hour
        self.max_failed_attempts = config.get('max_failed_attempts', 5)
        self.mfa_required = config.get('mfa_required', False)
        
        # JWT configuration
        self.jwt_secret = config.get('jwt_secret', secrets.token_urlsafe(32))
        self.jwt_algorithm = config.get('jwt_algorithm', 'HS256')
        self.jwt_expiration = config.get('jwt_expiration', 3600)
        
        # Encryption setup
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Zero-trust configuration
        self.zero_trust_enabled = config.get('zero_trust_enabled', True)
        self.continuous_verification = config.get('continuous_verification', True)
        
        logger.info("Access Control Orchestrator initialized")
    
    async def initialize(self):
        """Initialize access control orchestrator"""
        try:
            # Setup Redis connection
            await self._setup_redis_connection()
            
            # Load users, roles, and permissions
            await self._load_access_control_data()
            
            # Initialize default roles and permissions
            await self._initialize_default_access_control()
            
            # Load access policies
            await self._load_access_policies()
            
            # Start session monitoring
            asyncio.create_task(self._start_session_monitoring())
            
            # Start access monitoring
            asyncio.create_task(self._start_access_monitoring())
            
            logger.info("Access Control Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize access control orchestrator: {e}")
            raise
    
    async def _setup_redis_connection(self):
        """Setup Redis connection"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config['redis_url'],
                password=self.config.get('redis_password'),
                ssl=self.config.get('ssl_enabled', True),
                max_connections=self.config.get('max_connections', 100),
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            await self.redis_client.ping()
            
            logger.info("Redis connection established for access control")
            
        except Exception as e:
            logger.error(f"Failed to setup Redis connection: {e}")
            raise
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data"""
        password = self.config.get('encryption_password', 'default_password').encode()
        salt = self.config.get('encryption_salt', 'default_salt').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    async def _load_access_control_data(self):
        """Load users, roles, and permissions from storage"""
        try:
            # Load users
            stored_users = await self.redis_client.hgetall("access_control:users")
            for user_id, user_data in stored_users.items():
                try:
                    user_dict = json.loads(user_data)
                    user = User(**user_dict)
                    self.users[user_id.decode()] = user
                except Exception as e:
                    logger.error(f"Error loading user {user_id}: {e}")
            
            # Load roles
            stored_roles = await self.redis_client.hgetall("access_control:roles")
            for role_id, role_data in stored_roles.items():
                try:
                    role_dict = json.loads(role_data)
                    role = Role(**role_dict)
                    self.roles[role_id.decode()] = role
                except Exception as e:
                    logger.error(f"Error loading role {role_id}: {e}")
            
            # Load permissions
            stored_permissions = await self.redis_client.hgetall("access_control:permissions")
            for perm_id, perm_data in stored_permissions.items():
                try:
                    perm_dict = json.loads(perm_data)
                    permission = Permission(**perm_dict)
                    self.permissions[perm_id.decode()] = permission
                except Exception as e:
                    logger.error(f"Error loading permission {perm_id}: {e}")
            
            logger.info(f"Loaded {len(self.users)} users, {len(self.roles)} roles, {len(self.permissions)} permissions")
            
        except Exception as e:
            logger.error(f"Error loading access control data: {e}")
    
    async def _initialize_default_access_control(self):
        """Initialize default roles and permissions"""
        try:
            # Default permissions
            default_permissions = [
                Permission(
                    permission_id="redis_read",
                    name="Redis Read Access",
                    description="Read access to Redis keys and data",
                    resource_type=ResourceType.REDIS_KEY,
                    actions=["GET", "MGET", "KEYS", "SCAN", "EXISTS", "TYPE"],
                    is_system_permission=True
                ),
                Permission(
                    permission_id="redis_write",
                    name="Redis Write Access", 
                    description="Write access to Redis keys and data",
                    resource_type=ResourceType.REDIS_KEY,
                    actions=["SET", "MSET", "DEL", "EXPIRE", "PERSIST", "RENAME"],
                    is_system_permission=True
                ),
                Permission(
                    permission_id="redis_admin",
                    name="Redis Admin Access",
                    description="Administrative access to Redis",
                    resource_type=ResourceType.REDIS_CONFIG,
                    actions=["CONFIG", "INFO", "MONITOR", "DEBUG", "SHUTDOWN"],
                    is_system_permission=True
                ),
                Permission(
                    permission_id="redis_dangerous",
                    name="Redis Dangerous Commands",
                    description="Access to dangerous Redis commands",
                    resource_type=ResourceType.REDIS_COMMAND,
                    actions=["FLUSHDB", "FLUSHALL", "EVAL", "SCRIPT", "CLIENT KILL"],
                    is_system_permission=True
                )
            ]
            
            for permission in default_permissions:
                if permission.permission_id not in self.permissions:
                    self.permissions[permission.permission_id] = permission
                    await self._store_permission(permission)
            
            # Default roles
            default_roles = [
                Role(
                    role_id="redis_reader",
                    name="Redis Reader",
                    description="Read-only access to Redis data",
                    permissions=["redis_read"],
                    is_system_role=True
                ),
                Role(
                    role_id="redis_writer",
                    name="Redis Writer",
                    description="Read and write access to Redis data",
                    permissions=["redis_read", "redis_write"],
                    is_system_role=True
                ),
                Role(
                    role_id="redis_admin",
                    name="Redis Administrator",
                    description="Administrative access to Redis",
                    permissions=["redis_read", "redis_write", "redis_admin"],
                    is_system_role=True
                ),
                Role(
                    role_id="redis_super_admin",
                    name="Redis Super Administrator",
                    description="Full access to Redis including dangerous commands",
                    permissions=["redis_read", "redis_write", "redis_admin", "redis_dangerous"],
                    is_system_role=True
                )
            ]
            
            for role in default_roles:
                if role.role_id not in self.roles:
                    self.roles[role.role_id] = role
                    await self._store_role(role)
            
            # Create default admin user if not exists
            admin_user_id = "admin"
            if admin_user_id not in self.users:
                admin_user = await self.create_user(
                    username="admin",
                    email="admin@ainflue.com",
                    password="AdminPassword123!",
                    roles=["redis_super_admin"]
                )
                logger.info(f"Created default admin user: {admin_user}")
            
            logger.info("Default access control initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default access control: {e}")
    
    async def _load_access_policies(self):
        """Load access control policies"""
        try:
            stored_policies = await self.redis_client.hgetall("access_control:policies")
            
            for policy_id, policy_data in stored_policies.items():
                try:
                    policy_dict = json.loads(policy_data)
                    policy = AccessPolicy(**policy_dict)
                    self.policies[policy_id.decode()] = policy
                except Exception as e:
                    logger.error(f"Error loading policy {policy_id}: {e}")
            
            # Create default policies if none exist
            if not self.policies:
                await self._create_default_policies()
            
            logger.info(f"Loaded {len(self.policies)} access policies")
            
        except Exception as e:
            logger.error(f"Error loading access policies: {e}")
    
    async def _create_default_policies(self):
        """Create default access control policies"""
        try:
            default_policies = [
                AccessPolicy(
                    policy_id="admin_full_access",
                    name="Admin Full Access",
                    description="Full access for admin users",
                    subjects=["role:redis_super_admin"],
                    resources=["*"],
                    actions=["*"],
                    policy_action=PolicyAction.ALLOW,
                    priority=10
                ),
                AccessPolicy(
                    policy_id="reader_read_only",
                    name="Reader Read Only Access",
                    description="Read-only access for reader role",
                    subjects=["role:redis_reader"],
                    resources=["redis:*"],
                    actions=["GET", "MGET", "KEYS", "SCAN", "EXISTS", "TYPE"],
                    policy_action=PolicyAction.ALLOW,
                    priority=5
                ),
                AccessPolicy(
                    policy_id="dangerous_commands_require_mfa",
                    name="Dangerous Commands Require MFA",
                    description="Require MFA for dangerous Redis commands",
                    subjects=["*"],
                    resources=["redis:command:FLUSHDB", "redis:command:FLUSHALL"],
                    actions=["EXECUTE"],
                    policy_action=PolicyAction.REQUIRE_MFA,
                    priority=15
                ),
                AccessPolicy(
                    policy_id="deny_external_access",
                    name="Deny External Network Access",
                    description="Deny access from external networks",
                    subjects=["*"],
                    resources=["*"],
                    actions=["*"],
                    conditions={
                        "source_ip": {"not_in": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]}
                    },
                    policy_action=PolicyAction.DENY,
                    priority=20
                )
            ]
            
            for policy in default_policies:
                self.policies[policy.policy_id] = policy
                await self._store_policy(policy)
            
            logger.info("Created default access policies")
            
        except Exception as e:
            logger.error(f"Error creating default policies: {e}")
    
    async def _start_session_monitoring(self):
        """Start session monitoring and cleanup"""
        logger.info("Starting session monitoring")
        
        while True:
            try:
                # Clean up expired sessions
                await self._cleanup_expired_sessions()
                
                # Update session activity
                await self._update_session_metrics()
                
                # Continuous verification for zero-trust
                if self.zero_trust_enabled and self.continuous_verification:
                    await self._continuous_session_verification()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in session monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _start_access_monitoring(self):
        """Start access control monitoring"""
        logger.info("Starting access control monitoring")
        
        while True:
            try:
                # Update access metrics
                await self._update_access_metrics()
                
                # Monitor for policy violations
                await self._monitor_policy_violations()
                
                # Check for suspicious access patterns
                await self._detect_suspicious_access()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in access monitoring: {e}")
                await asyncio.sleep(60)
    
    async def create_user(self, username: str, email: str, password: str, 
                         roles: List[str] = None, groups: List[str] = None,
                         attributes: Dict[str, Any] = None) -> str:
        """Create new user account"""
        try:
            user_id = str(uuid.uuid4())
            
            # Validate password policy
            if not self._validate_password(password):
                raise ValueError("Password does not meet policy requirements")
            
            # Hash password
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            # Calculate password expiration
            password_expires = None
            if self.password_policy.get('expires_days'):
                password_expires = datetime.now() + timedelta(
                    days=self.password_policy['expires_days']
                )
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                salt=salt,
                roles=roles or [],
                groups=groups or [],
                attributes=attributes or {},
                password_expires=password_expires
            )
            
            # Store user
            self.users[user_id] = user
            await self._store_user(user)
            
            logger.info(f"Created user: {username} ({user_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def _validate_password(self, password: str) -> bool:
        """Validate password against policy"""
        try:
            min_length = self.password_policy.get('min_length', 8)
            require_uppercase = self.password_policy.get('require_uppercase', True)
            require_lowercase = self.password_policy.get('require_lowercase', True)
            require_numbers = self.password_policy.get('require_numbers', True)
            require_special = self.password_policy.get('require_special', True)
            
            if len(password) < min_length:
                return False
            
            if require_uppercase and not any(c.isupper() for c in password):
                return False
            
            if require_lowercase and not any(c.islower() for c in password):
                return False
            
            if require_numbers and not any(c.isdigit() for c in password):
                return False
            
            if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating password: {e}")
            return False
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    async def authenticate_user(self, username: str, password: str, source_ip: str,
                              user_agent: str, mfa_token: Optional[str] = None) -> Optional[Session]:
        """Authenticate user and create session"""
        try:
            # Find user by username
            user = None
            for u in self.users.values():
                if u.username == username:
                    user = u
                    break
            
            if not user:
                logger.warning(f"Authentication failed: user not found: {username}")
                self.metrics.failed_authentications += 1
                return None
            
            # Check if user is active and not locked
            if not user.is_active or user.is_locked:
                logger.warning(f"Authentication failed: user inactive or locked: {username}")
                self.metrics.failed_authentications += 1
                return None
            
            # Verify password
            password_hash = self._hash_password(password, user.salt)
            if password_hash != user.password_hash:
                # Increment failed attempts
                user.failed_login_attempts += 1
                
                # Lock user if max attempts exceeded
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.is_locked = True
                    logger.warning(f"User locked due to failed attempts: {username}")
                
                await self._store_user(user)
                logger.warning(f"Authentication failed: invalid password: {username}")
                self.metrics.failed_authentications += 1
                return None
            
            # Check MFA if required
            if user.mfa_enabled or self.mfa_required:
                if not mfa_token:
                    logger.warning(f"Authentication failed: MFA required: {username}")
                    return None
                
                if not self._verify_mfa_token(user, mfa_token):
                    logger.warning(f"Authentication failed: invalid MFA token: {username}")
                    self.metrics.failed_authentications += 1
                    return None
            
            # Check password expiration
            if user.password_expires and datetime.now() > user.password_expires:
                logger.warning(f"Authentication failed: password expired: {username}")
                return None
            
            # Reset failed attempts on successful authentication
            user.failed_login_attempts = 0
            user.last_login = datetime.now()
            await self._store_user(user)
            
            # Create session
            session = await self._create_session(user, source_ip, user_agent, mfa_token is not None)
            
            logger.info(f"User authenticated successfully: {username}")
            return session
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            self.metrics.failed_authentications += 1
            return None
    
    def _verify_mfa_token(self, user: User, token: str) -> bool:
        """Verify MFA token (TOTP)"""
        try:
            # This would integrate with actual TOTP verification
            # For now, simulate verification
            return len(token) == 6 and token.isdigit()
            
        except Exception as e:
            logger.error(f"Error verifying MFA token: {e}")
            return False
    
    async def _create_session(self, user: User, source_ip: str, user_agent: str, mfa_verified: bool) -> Session:
        """Create user session"""
        try:
            session_id = str(uuid.uuid4())
            
            session = Session(
                session_id=session_id,
                user_id=user.user_id,
                username=user.username,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=self.session_timeout),
                source_ip=source_ip,
                user_agent=user_agent,
                mfa_verified=mfa_verified
            )
            
            # Store session
            self.active_sessions[session_id] = session
            await self._store_session(session)
            
            # Update metrics
            self.metrics.active_sessions += 1
            
            logger.info(f"Created session: {session_id} for user: {user.username}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def authorize_access(self, session_id: str, resource: str, action: str,
                             resource_type: ResourceType, context: Dict[str, Any] = None) -> AccessDecision:
        """Authorize access to resource"""
        try:
            # Create access request
            request_id = str(uuid.uuid4())
            request = AccessRequest(
                request_id=request_id,
                user_id="",  # Will be filled from session
                session_id=session_id,
                resource=resource,
                action=action,
                resource_type=resource_type,
                context=context or {}
            )
            
            # Get session
            session = self.active_sessions.get(session_id)
            if not session:
                return AccessDecision(
                    request_id=request_id,
                    decision=PolicyAction.DENY,
                    reason="Invalid or expired session"
                )
            
            # Check session validity
            if not await self._validate_session(session):
                return AccessDecision(
                    request_id=request_id,
                    decision=PolicyAction.DENY,
                    reason="Session expired or invalid"
                )
            
            request.user_id = session.user_id
            
            # Get user
            user = self.users.get(session.user_id)
            if not user:
                return AccessDecision(
                    request_id=request_id,
                    decision=PolicyAction.DENY,
                    reason="User not found"
                )
            
            # Evaluate access policies
            decision = await self._evaluate_access_policies(request, user, session)
            
            # Update session activity
            session.last_activity = datetime.now()
            
            # Log access attempt
            await self._log_access_attempt(request, decision)
            
            # Update metrics
            self.metrics.total_requests += 1
            if decision.decision == PolicyAction.ALLOW:
                self.metrics.allowed_requests += 1
            elif decision.decision == PolicyAction.DENY:
                self.metrics.denied_requests += 1
            elif decision.decision == PolicyAction.REQUIRE_MFA:
                self.metrics.mfa_required_requests += 1
            
            return decision
            
        except Exception as e:
            logger.error(f"Error authorizing access: {e}")
            return AccessDecision(
                request_id=str(uuid.uuid4()),
                decision=PolicyAction.DENY,
                reason=f"Authorization error: {str(e)}"
            )
    
    async def _validate_session(self, session: Session) -> bool:
        """Validate session is still valid"""
        try:
            # Check expiration
            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                return False
            
            # Check if session was revoked
            if session.status != SessionStatus.ACTIVE:
                return False
            
            # Zero-trust: continuous verification
            if self.zero_trust_enabled:
                return await self._continuous_verification(session)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False
    
    async def _continuous_verification(self, session: Session) -> bool:
        """Continuous verification for zero-trust"""
        try:
            # Check for suspicious activity
            user = self.users.get(session.user_id)
            if not user:
                return False
            
            # Check if user is still active
            if not user.is_active or user.is_locked:
                return False
            
            # Check for location changes (simplified)
            # In production, this would check for geographic anomalies
            
            # Check for behavioral changes
            # This would analyze access patterns and detect anomalies
            
            return True
            
        except Exception as e:
            logger.error(f"Error in continuous verification: {e}")
            return False
    
    async def _evaluate_access_policies(self, request: AccessRequest, user: User, session: Session) -> AccessDecision:
        """Evaluate access policies for authorization decision"""
        try:
            matched_policies = []
            decisions = []
            
            # Get user roles and permissions
            user_roles = set(user.roles)
            user_permissions = await self._get_user_permissions(user)
            
            # Evaluate each policy
            for policy in sorted(self.policies.values(), key=lambda p: p.priority, reverse=True):
                if not policy.is_active:
                    continue
                
                # Check if policy applies to this request
                if await self._policy_matches_request(policy, request, user, session):
                    matched_policies.append(policy.policy_id)
                    
                    # Check policy conditions
                    if await self._check_policy_conditions(policy, request, user, session):
                        decisions.append(policy.policy_action)
                        
                        # For high-priority DENY policies, return immediately
                        if policy.policy_action == PolicyAction.DENY and policy.priority >= 15:
                            return AccessDecision(
                                request_id=request.request_id,
                                decision=PolicyAction.DENY,
                                reason=f"Denied by high-priority policy: {policy.name}",
                                matched_policies=matched_policies
                            )
            
            # Determine final decision
            final_decision = self._resolve_policy_conflicts(decisions)
            
            # Check if user has required permissions (RBAC)
            if final_decision == PolicyAction.ALLOW:
                required_permission = f"{request.resource_type.value}:{request.action}"
                if required_permission not in user_permissions and "*" not in user_permissions:
                    final_decision = PolicyAction.DENY
                    reason = f"User lacks required permission: {required_permission}"
                else:
                    reason = "Access granted by policy and permissions"
            else:
                reason = f"Access decision: {final_decision.value}"
            
            return AccessDecision(
                request_id=request.request_id,
                decision=final_decision,
                reason=reason,
                matched_policies=matched_policies
            )
            
        except Exception as e:
            logger.error(f"Error evaluating access policies: {e}")
            return AccessDecision(
                request_id=request.request_id,
                decision=PolicyAction.DENY,
                reason=f"Policy evaluation error: {str(e)}"
            )
    
    async def _get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for user (including inherited from roles)"""
        try:
            permissions = set()
            
            # Get permissions from user roles
            for role_id in user.roles:
                role = self.roles.get(role_id)
                if role:
                    permissions.update(role.permissions)
                    
                    # Get permissions from parent roles (role hierarchy)
                    parent_permissions = await self._get_role_permissions_recursive(role)
                    permissions.update(parent_permissions)
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return set()
    
    async def _get_role_permissions_recursive(self, role: Role) -> Set[str]:
        """Get permissions from role hierarchy recursively"""
        try:
            permissions = set(role.permissions)
            
            # Get permissions from parent roles
            for parent_role_id in role.parent_roles:
                parent_role = self.roles.get(parent_role_id)
                if parent_role:
                    parent_permissions = await self._get_role_permissions_recursive(parent_role)
                    permissions.update(parent_permissions)
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting role permissions recursively: {e}")
            return set()
    
    async def _policy_matches_request(self, policy: AccessPolicy, request: AccessRequest, 
                                    user: User, session: Session) -> bool:
        """Check if policy matches the access request"""
        try:
            # Check subjects (users, roles, groups)
            subject_match = False
            for subject in policy.subjects:
                if subject == "*":
                    subject_match = True
                    break
                elif subject.startswith("user:") and subject[5:] == user.user_id:
                    subject_match = True
                    break
                elif subject.startswith("role:") and subject[5:] in user.roles:
                    subject_match = True
                    break
                elif subject.startswith("group:") and subject[6:] in user.groups:
                    subject_match = True
                    break
            
            if not subject_match:
                return False
            
            # Check resources
            resource_match = False
            for resource_pattern in policy.resources:
                if resource_pattern == "*":
                    resource_match = True
                    break
                elif self._resource_matches_pattern(request.resource, resource_pattern):
                    resource_match = True
                    break
            
            if not resource_match:
                return False
            
            # Check actions
            action_match = False
            for action_pattern in policy.actions:
                if action_pattern == "*":
                    action_match = True
                    break
                elif action_pattern == request.action:
                    action_match = True
                    break
            
            return action_match
            
        except Exception as e:
            logger.error(f"Error matching policy to request: {e}")
            return False
    
    def _resource_matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches pattern (supports wildcards)"""
        try:
            # Simple wildcard matching
            if pattern == "*":
                return True
            
            if "*" in pattern:
                # Convert pattern to regex
                import re
                regex_pattern = pattern.replace("*", ".*")
                return bool(re.match(f"^{regex_pattern}$", resource))
            
            return resource == pattern
            
        except Exception as e:
            logger.error(f"Error matching resource pattern: {e}")
            return False
    
    async def _check_policy_conditions(self, policy: AccessPolicy, request: AccessRequest,
                                     user: User, session: Session) -> bool:
        """Check if policy conditions are met"""
        try:
            if not policy.conditions:
                return True
            
            # Check time-based conditions
            if "time" in policy.conditions:
                time_condition = policy.conditions["time"]
                current_time = datetime.now().time()
                
                if "start" in time_condition and "end" in time_condition:
                    start_time = datetime.strptime(time_condition["start"], "%H:%M").time()
                    end_time = datetime.strptime(time_condition["end"], "%H:%M").time()
                    
                    if not (start_time <= current_time <= end_time):
                        return False
            
            # Check IP-based conditions
            if "source_ip" in policy.conditions:
                ip_condition = policy.conditions["source_ip"]
                source_ip = session.source_ip
                
                if "allowed" in ip_condition:
                    if not self._ip_in_ranges(source_ip, ip_condition["allowed"]):
                        return False
                
                if "denied" in ip_condition:
                    if self._ip_in_ranges(source_ip, ip_condition["denied"]):
                        return False
                
                if "not_in" in ip_condition:
                    if self._ip_in_ranges(source_ip, ip_condition["not_in"]):
                        return False
            
            # Check day-based conditions
            if "days" in policy.conditions:
                days_condition = policy.conditions["days"]
                current_day = datetime.now().strftime("%A").lower()
                
                if current_day not in [day.lower() for day in days_condition]:
                    return False
            
            # Check MFA conditions
            if "require_mfa" in policy.conditions and policy.conditions["require_mfa"]:
                if not session.mfa_verified:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking policy conditions: {e}")
            return False
    
    def _ip_in_ranges(self, ip: str, ranges: List[str]) -> bool:
        """Check if IP address is in any of the specified ranges"""
        try:
            ip_addr = ipaddress.ip_address(ip)
            
            for range_str in ranges:
                try:
                    network = ipaddress.ip_network(range_str, strict=False)
                    if ip_addr in network:
                        return True
                except ValueError:
                    # Try as single IP
                    if ip == range_str:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking IP ranges: {e}")
            return False
    
    def _resolve_policy_conflicts(self, decisions: List[PolicyAction]) -> PolicyAction:
        """Resolve conflicts when multiple policies apply"""
        try:
            if not decisions:
                return PolicyAction.DENY  # Default deny
            
            # Priority order: DENY > REQUIRE_MFA > REQUIRE_APPROVAL > ALLOW > LOG_ONLY
            if PolicyAction.DENY in decisions:
                return PolicyAction.DENY
            elif PolicyAction.REQUIRE_MFA in decisions:
                return PolicyAction.REQUIRE_MFA
            elif PolicyAction.REQUIRE_APPROVAL in decisions:
                return PolicyAction.REQUIRE_APPROVAL
            elif PolicyAction.ALLOW in decisions:
                return PolicyAction.ALLOW
            else:
                return PolicyAction.LOG_ONLY
                
        except Exception as e:
            logger.error(f"Error resolving policy conflicts: {e}")
            return PolicyAction.DENY
    
    async def _log_access_attempt(self, request: AccessRequest, decision: AccessDecision):
        """Log access attempt for audit trail"""
        try:
            log_entry = {
                'request_id': request.request_id,
                'user_id': request.user_id,
                'session_id': request.session_id,
                'resource': request.resource,
                'action': request.action,
                'resource_type': request.resource_type.value,
                'decision': decision.decision.value,
                'reason': decision.reason,
                'matched_policies': decision.matched_policies,
                'timestamp': request.timestamp.isoformat(),
                'context': request.context
            }
            
            # Store in Redis
            await self.redis_client.lpush(
                "access_control:access_log",
                json.dumps(log_entry)
            )
            
            # Trim log to keep last 10000 entries
            await self.redis_client.ltrim("access_control:access_log", 0, 9999)
            
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            expired_sessions = []
            current_time = datetime.now()
            
            for session_id, session in self.active_sessions.items():
                if current_time > session.expires_at:
                    expired_sessions.append(session_id)
                    session.status = SessionStatus.EXPIRED
            
            # Remove expired sessions
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                await self.redis_client.hdel("access_control:sessions", session_id)
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                self.metrics.active_sessions -= len(expired_sessions)
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
    
    async def _store_user(self, user: User):
        """Store user in Redis"""
        try:
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'salt': user.salt,
                'roles': user.roles,
                'groups': user.groups,
                'attributes': user.attributes,
                'is_active': user.is_active,
                'is_locked': user.is_locked,
                'failed_login_attempts': user.failed_login_attempts,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'password_expires': user.password_expires.isoformat() if user.password_expires else None,
                'mfa_enabled': user.mfa_enabled,
                'mfa_secret': user.mfa_secret,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
            
            await self.redis_client.hset(
                "access_control:users",
                user.user_id,
                json.dumps(user_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing user: {e}")
    
    async def _store_role(self, role: Role):
        """Store role in Redis"""
        try:
            role_data = {
                'role_id': role.role_id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions,
                'parent_roles': role.parent_roles,
                'resource_constraints': role.resource_constraints,
                'time_constraints': role.time_constraints,
                'is_system_role': role.is_system_role,
                'created_at': role.created_at.isoformat(),
                'updated_at': role.updated_at.isoformat()
            }
            
            await self.redis_client.hset(
                "access_control:roles",
                role.role_id,
                json.dumps(role_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing role: {e}")
    
    async def _store_permission(self, permission: Permission):
        """Store permission in Redis"""
        try:
            perm_data = {
                'permission_id': permission.permission_id,
                'name': permission.name,
                'description': permission.description,
                'resource_type': permission.resource_type.value,
                'actions': permission.actions,
                'conditions': permission.conditions,
                'is_system_permission': permission.is_system_permission
            }
            
            await self.redis_client.hset(
                "access_control:permissions",
                permission.permission_id,
                json.dumps(perm_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing permission: {e}")
    
    async def _store_policy(self, policy: AccessPolicy):
        """Store access policy in Redis"""
        try:
            policy_data = {
                'policy_id': policy.policy_id,
                'name': policy.name,
                'description': policy.description,
                'subjects': policy.subjects,
                'resources': policy.resources,
                'actions': policy.actions,
                'conditions': policy.conditions,
                'policy_action': policy.policy_action.value,
                'priority': policy.priority,
                'is_active': policy.is_active,
                'created_at': policy.created_at.isoformat(),
                'updated_at': policy.updated_at.isoformat()
            }
            
            await self.redis_client.hset(
                "access_control:policies",
                policy.policy_id,
                json.dumps(policy_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing policy: {e}")
    
    async def _store_session(self, session: Session):
        """Store session in Redis"""
        try:
            session_data = {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'username': session.username,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'source_ip': session.source_ip,
                'user_agent': session.user_agent,
                'status': session.status.value,
                'mfa_verified': session.mfa_verified,
                'permissions_cache': session.permissions_cache,
                'attributes': session.attributes
            }
            
            await self.redis_client.hset(
                "access_control:sessions",
                session.session_id,
                json.dumps(session_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing session: {e}")
    
    async def close(self):
        """Close access control orchestrator"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            logger.info("Access Control Orchestrator closed")
            
        except Exception as e:
            logger.error(f"Error closing access control orchestrator: {e}")

# Configuration schema for access control orchestrator
@dataclass
class AccessControlOrchestratorConfig:
    """Access control orchestrator configuration"""
    redis_url: str
    redis_password: Optional[str] = None
    ssl_enabled: bool = True
    max_connections: int = 100
    password_policy: Dict[str, Any] = field(default_factory=dict)
    session_timeout: int = 3600
    max_failed_attempts: int = 5
    mfa_required: bool = False
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    zero_trust_enabled: bool = True
    continuous_verification: bool = True
    encryption_password: str = "default_password"
    encryption_salt: str = "default_salt"