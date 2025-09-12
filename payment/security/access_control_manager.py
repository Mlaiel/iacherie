"""🔒 Access Control Manager
===========================

Enterprise access control management system for payment processing with
role-based access control, multi-factor authentication, and permission management.

Features:
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- Permission management and inheritance
- Access audit logging
- Session management
- Principle of least privilege enforcement

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import secrets
import jwt
import pyotp
import qrcode
from io import BytesIO
import bcrypt
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class ResourceType(Enum):
    """Types of resources that can be protected"""
    PAYMENT_GATEWAY = "payment_gateway"
    TRANSACTION = "transaction"
    USER_DATA = "user_data"
    FINANCIAL_REPORT = "financial_report"
    CONFIGURATION = "configuration"
    ADMIN_PANEL = "admin_panel"
    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"


class Permission(Enum):
    """Available permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    ADMIN = "admin"
    AUDIT = "audit"


class AuthMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"


class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    LOCKED = "locked"


@dataclass
class Role:
    """Role definition"""
    role_id: str
    name: str
    description: str
    permissions: Set[Permission]
    resource_types: Set[ResourceType]
    created_at: datetime
    is_active: bool = True
    parent_roles: Set[str] = field(default_factory=set)
    
    def can_access(self, resource_type: ResourceType, permission: Permission) -> bool:
        """Check if role can access resource with permission"""
        return (resource_type in self.resource_types and 
                permission in self.permissions and 
                self.is_active)


@dataclass
class User:
    """User definition"""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: Set[str]
    mfa_enabled: bool
    mfa_secret: Optional[str]
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked: bool = False
    password_expires_at: Optional[datetime] = None
    
    def is_locked(self) -> bool:
        """Check if account is locked"""
        return self.account_locked or (
            self.password_expires_at and 
            datetime.utcnow() > self.password_expires_at
        )
    
    def needs_password_change(self) -> bool:
        """Check if password needs to be changed"""
        if self.password_expires_at:
            return datetime.utcnow() > self.password_expires_at
        return False


@dataclass
class Session:
    """User session"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    status: SessionStatus
    mfa_verified: bool = False
    
    def is_valid(self) -> bool:
        """Check if session is valid"""
        return (self.status == SessionStatus.ACTIVE and 
                datetime.utcnow() < self.expires_at)
    
    def needs_mfa(self) -> bool:
        """Check if session needs MFA verification"""
        return not self.mfa_verified


@dataclass
class AccessAttempt:
    """Access attempt record"""
    attempt_id: str
    user_id: Optional[str]
    resource_type: ResourceType
    permission: Permission
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    failure_reason: Optional[str] = None


class AccessControlManager:
    """Enterprise access control management system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.db_session: Optional[AsyncSession] = None
        
        # Access control settings
        self.session_timeout = timedelta(hours=config.get('session_timeout_hours', 8))
        self.max_failed_attempts = config.get('max_failed_attempts', 5)
        self.lockout_duration = timedelta(minutes=config.get('lockout_duration_minutes', 30))
        self.password_expiry = timedelta(days=config.get('password_expiry_days', 90))
        self.jwt_secret = config.get('jwt_secret', secrets.token_urlsafe(32))
        
        # In-memory caches
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
    
    async def initialize(self):
        """Initialize the access control system"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 2),
                decode_responses=True
            )
            
            # Initialize database connection
            db_config = self.config.get('database', {})
            db_url = f"postgresql+asyncpg://{db_config.get('user')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}"
            engine = create_async_engine(db_url)
            async_session = sessionmaker(engine, class_=AsyncSession)
            self.db_session = async_session()
            
            # Load roles and users
            await self._load_roles()
            await self._load_users()
            
            # Create default roles if they don't exist
            await self._create_default_roles()
            
            logger.info("Access control system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize access control system: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str, ip_address: str, user_agent: str) -> Optional[str]:
        """Authenticate user and return session token"""
        try:
            user = await self._get_user_by_username(username)
            if not user:
                await self._log_access_attempt(None, ResourceType.ADMIN_PANEL, Permission.READ, ip_address, user_agent, False, "User not found")
                return None
            
            # Check if account is locked
            if user.is_locked():
                await self._log_access_attempt(user.user_id, ResourceType.ADMIN_PANEL, Permission.READ, ip_address, user_agent, False, "Account locked")
                return None
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                user.failed_login_attempts += 1
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.account_locked = True
                    logger.warning(f"Account locked due to failed attempts: {username}")
                
                await self._update_user(user)
                await self._log_access_attempt(user.user_id, ResourceType.ADMIN_PANEL, Permission.READ, ip_address, user_agent, False, "Invalid password")
                return None
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            await self._update_user(user)
            
            # Create session
            session = await self._create_session(user.user_id, ip_address, user_agent)
            
            # If MFA is enabled, session is not fully authenticated yet
            if user.mfa_enabled:
                session.mfa_verified = False
            else:
                session.mfa_verified = True
            
            await self._store_session(session)
            await self._log_access_attempt(user.user_id, ResourceType.ADMIN_PANEL, Permission.READ, ip_address, user_agent, True)
            
            return session.session_id
            
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}")
            raise
    
    async def verify_mfa(self, session_id: str, mfa_code: str) -> bool:
        """Verify MFA code for session"""
        try:
            session = await self._get_session(session_id)
            if not session or not session.is_valid():
                return False
            
            user = await self._get_user(session.user_id)
            if not user or not user.mfa_enabled:
                return False
            
            # Verify TOTP code
            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(mfa_code, valid_window=1):
                return False
            
            # Mark session as MFA verified
            session.mfa_verified = True
            await self._store_session(session)
            
            logger.info(f"MFA verified for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify MFA: {e}")
            return False
    
    async def check_permission(self, session_id: str, resource_type: ResourceType, permission: Permission) -> bool:
        """Check if session has permission for resource"""
        try:
            session = await self._get_session(session_id)
            if not session or not session.is_valid():
                return False
            
            # Check if MFA is required and verified
            user = await self._get_user(session.user_id)
            if user and user.mfa_enabled and not session.mfa_verified:
                return False
            
            # Update session activity
            session.last_activity = datetime.utcnow()
            await self._store_session(session)
            
            # Check user permissions
            return await self._check_user_permission(session.user_id, resource_type, permission)
            
        except Exception as e:
            logger.error(f"Failed to check permission: {e}")
            return False
    
    async def _check_user_permission(self, user_id: str, resource_type: ResourceType, permission: Permission) -> bool:
        """Check if user has permission for resource"""
        user = await self._get_user(user_id)
        if not user:
            return False
        
        # Check each role
        for role_id in user.roles:
            role = self.roles.get(role_id)
            if role and role.can_access(resource_type, permission):
                return True
            
            # Check parent roles
            if role:
                for parent_role_id in role.parent_roles:
                    parent_role = self.roles.get(parent_role_id)
                    if parent_role and parent_role.can_access(resource_type, permission):
                        return True
        
        return False
    
    async def create_role(self, role_data: Dict[str, Any]) -> Role:
        """Create a new role"""
        try:
            role = Role(
                role_id=f"role_{secrets.token_hex(8)}",
                name=role_data['name'],
                description=role_data['description'],
                permissions=set(Permission(p) for p in role_data['permissions']),
                resource_types=set(ResourceType(r) for r in role_data['resource_types']),
                created_at=datetime.utcnow(),
                parent_roles=set(role_data.get('parent_roles', []))
            )
            
            # Store role
            await self._store_role(role)
            self.roles[role.role_id] = role
            
            logger.info(f"Created new role: {role.name}")
            return role
            
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            raise
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user = User(
                user_id=f"user_{secrets.token_hex(8)}",
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash,
                roles=set(user_data.get('roles', [])),
                mfa_enabled=user_data.get('mfa_enabled', False),
                mfa_secret=pyotp.random_base32() if user_data.get('mfa_enabled', False) else None,
                created_at=datetime.utcnow(),
                password_expires_at=datetime.utcnow() + self.password_expiry
            )
            
            # Store user
            await self._store_user(user)
            self.users[user.user_id] = user
            
            logger.info(f"Created new user: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def enable_mfa(self, user_id: str) -> str:
        """Enable MFA for user and return QR code"""
        try:
            user = await self._get_user(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Generate MFA secret
            if not user.mfa_secret:
                user.mfa_secret = pyotp.random_base32()
            
            user.mfa_enabled = True
            await self._update_user(user)
            
            # Generate QR code
            totp = pyotp.TOTP(user.mfa_secret)
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="Ainflue Payment Gateway"
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            
            logger.info(f"MFA enabled for user: {user.username}")
            return img_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to enable MFA: {e}")
            raise
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate a user session"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            session.status = SessionStatus.TERMINATED
            await self._store_session(session)
            
            # Remove from Redis cache
            await self.redis_client.delete(f"session:{session_id}")
            
            logger.info(f"Terminated session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")
            return False
    
    async def _create_session(self, user_id: str, ip_address: str, user_agent: str) -> Session:
        """Create a new user session"""
        session = Session(
            session_id=f"sess_{secrets.token_urlsafe(32)}",
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.session_timeout,
            ip_address=ip_address,
            user_agent=user_agent,
            status=SessionStatus.ACTIVE
        )
        
        return session
    
    async def _store_session(self, session: Session):
        """Store session in Redis"""
        if not self.redis_client:
            return
        
        session_data = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'status': session.status.value,
            'mfa_verified': session.mfa_verified
        }
        
        await self.redis_client.hset(
            f"session:{session.session_id}",
            mapping=session_data
        )
        
        # Set expiration
        await self.redis_client.expireat(
            f"session:{session.session_id}",
            int(session.expires_at.timestamp())
        )
    
    async def _get_session(self, session_id: str) -> Optional[Session]:
        """Get session from Redis"""
        if not self.redis_client:
            return None
        
        session_data = await self.redis_client.hgetall(f"session:{session_id}")
        if not session_data:
            return None
        
        return Session(
            session_id=session_data['session_id'],
            user_id=session_data['user_id'],
            created_at=datetime.fromisoformat(session_data['created_at']),
            last_activity=datetime.fromisoformat(session_data['last_activity']),
            expires_at=datetime.fromisoformat(session_data['expires_at']),
            ip_address=session_data['ip_address'],
            user_agent=session_data['user_agent'],
            status=SessionStatus(session_data['status']),
            mfa_verified=session_data['mfa_verified'] == 'True'
        )
    
    async def _get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    async def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    async def _store_role(self, role: Role):
        """Store role (placeholder for database storage)"""
        # In production, this would store to database
        pass
    
    async def _store_user(self, user: User):
        """Store user (placeholder for database storage)"""
        # In production, this would store to database
        pass
    
    async def _update_user(self, user: User):
        """Update user (placeholder for database storage)"""
        # In production, this would update database
        pass
    
    async def _load_roles(self):
        """Load roles from database"""
        # Placeholder for database loading
        pass
    
    async def _load_users(self):
        """Load users from database"""
        # Placeholder for database loading
        pass
    
    async def _create_default_roles(self):
        """Create default system roles"""
        default_roles = [
            {
                'name': 'admin',
                'description': 'Full system administrator',
                'permissions': [p.value for p in Permission],
                'resource_types': [r.value for r in ResourceType]
            },
            {
                'name': 'payment_manager',
                'description': 'Payment processing manager',
                'permissions': [Permission.READ.value, Permission.WRITE.value, Permission.EXECUTE.value],
                'resource_types': [ResourceType.PAYMENT_GATEWAY.value, ResourceType.TRANSACTION.value, ResourceType.FINANCIAL_REPORT.value]
            },
            {
                'name': 'viewer',
                'description': 'Read-only access',
                'permissions': [Permission.READ.value],
                'resource_types': [ResourceType.TRANSACTION.value, ResourceType.FINANCIAL_REPORT.value]
            }
        ]
        
        for role_data in default_roles:
            # Check if role already exists
            role_exists = any(role.name == role_data['name'] for role in self.roles.values())
            if not role_exists:
                await self.create_role(role_data)
    
    async def _log_access_attempt(self, user_id: Optional[str], resource_type: ResourceType, 
                                permission: Permission, ip_address: str, user_agent: str, 
                                success: bool, failure_reason: Optional[str] = None):
        """Log access attempt"""
        attempt = AccessAttempt(
            attempt_id=f"attempt_{secrets.token_hex(8)}",
            user_id=user_id,
            resource_type=resource_type,
            permission=permission,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            success=success,
            failure_reason=failure_reason
        )
        
        # Store in Redis for real-time monitoring
        if self.redis_client:
            attempt_data = {
                'user_id': attempt.user_id or 'anonymous',
                'resource_type': attempt.resource_type.value,
                'permission': attempt.permission.value,
                'ip_address': attempt.ip_address,
                'timestamp': attempt.timestamp.isoformat(),
                'success': attempt.success,
                'failure_reason': attempt.failure_reason or ''
            }
            
            await self.redis_client.lpush(
                "access_attempts",
                json.dumps(attempt_data)
            )
            
            # Keep only last 1000 attempts
            await self.redis_client.ltrim("access_attempts", 0, 999)
        
        if not success:
            logger.warning(f"Access denied: {user_id} -> {resource_type.value}:{permission.value} from {ip_address}")
    
    def get_access_metrics(self) -> Dict[str, Any]:
        """Get access control metrics"""
        active_sessions = sum(1 for session in self.sessions.values() if session.is_valid())
        locked_accounts = sum(1 for user in self.users.values() if user.is_locked())
        mfa_enabled_users = sum(1 for user in self.users.values() if user.mfa_enabled)
        
        return {
            "total_users": len(self.users),
            "total_roles": len(self.roles),
            "active_sessions": active_sessions,
            "locked_accounts": locked_accounts,
            "mfa_enabled_users": mfa_enabled_users,
            "session_timeout_minutes": int(self.session_timeout.total_seconds() / 60),
            "max_failed_attempts": self.max_failed_attempts
        }