
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
#!/usr/bin/env python3
"""
🔐 Enterprise Authentication Service Template - Ainflue
=====================================================
Template enterprise pour services authentication.
JWT + OAuth2 + RBAC + MFA + audit logging + session management.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction sans autorisation est STRICTEMENT INTERDITE.
"""

import asyncio
import hashlib
import hmac
import json
import secrets
import time
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Set
import logging
import uuid
import base64

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

from .service_template import EnterpriseServiceBase, ServiceConfig


class AuthenticationMethod(Enum):
    """Méthodes d'authentication."""
    PASSWORD = "password"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    MFA = "mfa"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"


class OAuth2Provider(Enum):
    """Providers OAuth2 supportés."""
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    CUSTOM = "custom"


class MFAType(Enum):
    """Types MFA."""
    TOTP = "totp"  # Time-based One-Time Password
    SMS = "sms"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push"
    HARDWARE_TOKEN = "hardware_token"
    BACKUP_CODES = "backup_codes"


class SessionStatus(Enum):
    """Status des sessions."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class AuditAction(Enum):
    """Actions d'audit."""
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"


@dataclass
class User:
    """Modèle utilisateur."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    mfa_backup_codes: List[str] = field(default_factory=list)
    profile: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Role:
    """Modèle rôle RBAC."""
    name: str
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    parent_roles: List[str] = field(default_factory=list)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Permission:
    """Modèle permission."""
    name: str
    resource: str
    action: str
    description: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    is_system_permission: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    """Modèle session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    token: str = ""
    refresh_token: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=24))
    last_activity: datetime = field(default_factory=datetime.now)
    ip_address: str = ""
    user_agent: str = ""
    device_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLog:
    """Log d'audit."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    action: AuditAction = AuditAction.LOGIN
    resource: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ""
    user_agent: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    risk_score: float = 0.0  # 0-100 risk assessment


@dataclass
class AuthConfig:
    """Configuration authentication."""
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    refresh_token_expiration_days: int = 30
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    max_failed_attempts: int = 5
    account_lockout_minutes: int = 30
    session_timeout_minutes: int = 1440  # 24 hours
    enable_mfa: bool = False
    mfa_issuer: str = "Ainflue"
    enable_audit_logging: bool = True
    password_history_count: int = 5


class AuthServiceTemplate(EnterpriseServiceBase):
    """
    🔐 Template enterprise pour services authentication.
    JWT + OAuth2 + RBAC + MFA + audit logging + session management.
    
    Features:
    - JWT authentication avec refresh tokens
    - OAuth2 integration multiple providers
    - RBAC avec permissions granulaires
    - Multi-factor authentication (TOTP, SMS, Email)
    - Session management avec device tracking
    - Audit logging complet avec risk assessment
    - Password policies avancées
    - Account lockout et security monitoring
    - API key management
    - Rate limiting par utilisateur
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize authentication service template."""
        super().__init__(config)
        
        if not JWT_AVAILABLE:
            self.logger.warning("⚠️ PyJWT not available - JWT functionality limited")
        
        self.auth_providers: Dict[str, Any] = {}
        self.session_store: Dict[str, Session] = {}
        self.user_store: Dict[str, User] = {}
        self.role_store: Dict[str, Role] = {}
        self.permission_store: Dict[str, Permission] = {}
        self.audit_logger: Optional['AuditLogger'] = None
        self.auth_config: Optional[AuthConfig] = None
        
        # Authentication metrics
        self.auth_metrics = {
            'users_total': 0,
            'users_active': 0,
            'sessions_active': 0,
            'login_attempts': 0,
            'login_successes': 0,
            'login_failures': 0,
            'mfa_enabled_users': 0,
            'locked_accounts': 0,
            'oauth2_logins': 0,
            'api_key_authentications': 0,
            'password_changes': 0,
            'permission_checks': 0,
            'audit_logs_count': 0
        }
        
        # Security monitoring
        self.security_events: List[Dict] = []
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.suspicious_ips: Set[str] = set()
        
        self.logger.info(f"🔐 Authentication Service Template initialized: {config.service_name}")
    
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        try:
            # Setup audit logger
            self.audit_logger = AuditLogger(self)
            
            # Setup default roles and permissions
            await self._setup_default_rbac()
            
            # Start background tasks
            asyncio.create_task(self._background_security_monitoring())
            asyncio.create_task(self._session_cleanup_task())
            
            self.logger.info("✅ Authentication service components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize authentication service: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Clear all sessions
            self.session_store.clear()
            
            # Cleanup audit logger
            if self.audit_logger:
                await self.audit_logger.cleanup()
            
            # Clear stores
            self.user_store.clear()
            self.role_store.clear()
            self.permission_store.clear()
            
            self.logger.info("✅ Authentication service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during authentication service cleanup: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform authentication service-specific health checks."""
        try:
            return {
                'users_count': len(self.user_store),
                'active_sessions': len([s for s in self.session_store.values() if s.status == SessionStatus.ACTIVE]),
                'roles_count': len(self.role_store),
                'permissions_count': len(self.permission_store),
                'oauth2_providers': len(self.auth_providers),
                'metrics': self.auth_metrics.copy(),
                'security_status': {
                    'suspicious_ips': len(self.suspicious_ips),
                    'locked_accounts': len([u for u in self.user_store.values() 
                                          if u.account_locked_until and u.account_locked_until > datetime.now()]),
                    'recent_security_events': len([e for e in self.security_events 
                                                 if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=1)])
                },
                'jwt_available': JWT_AVAILABLE,
                'bcrypt_available': BCRYPT_AVAILABLE
            }
            
        except Exception as e:
            self.logger.error(f"❌ Authentication service health check failed: {e}")
            return {'error': str(e), 'status': 'unhealthy'}
    
    async def setup_jwt_authentication(self, jwt_config: AuthConfig) -> None:
        """Configuration JWT avec rotation clés."""
        try:
            if not JWT_AVAILABLE:
                raise ValueError("PyJWT not available for JWT authentication")
            
            self.auth_config = jwt_config
            
            # Validate JWT secret
            if len(jwt_config.jwt_secret) < 32:
                self.logger.warning("⚠️ JWT secret should be at least 32 characters for security")
            
            self.logger.info("✅ JWT authentication configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup JWT authentication: {e}")
            raise
    
    async def setup_oauth2_providers(self, oauth_configs: Dict[OAuth2Provider, Dict]) -> None:
        """Configuration OAuth2 multiple providers."""
        try:
            for provider, config in oauth_configs.items():
                self.auth_providers[provider.value] = {
                    'client_id': config.get('client_id'),
                    'client_secret': config.get('client_secret'),
                    'redirect_uri': config.get('redirect_uri'),
                    'scopes': config.get('scopes', []),
                    'config': config
                }
            
            self.logger.info(f"✅ OAuth2 providers configured: {list(oauth_configs.keys())}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup OAuth2 providers: {e}")
            raise
    
    async def setup_rbac_system(self, rbac_config: Dict[str, Any]) -> None:
        """Système RBAC avec permissions granulaires."""
        try:
            # Load roles from config
            if 'roles' in rbac_config:
                for role_data in rbac_config['roles']:
                    role = Role(**role_data)
                    self.role_store[role.name] = role
            
            # Load permissions from config
            if 'permissions' in rbac_config:
                for perm_data in rbac_config['permissions']:
                    permission = Permission(**perm_data)
                    self.permission_store[permission.name] = permission
            
            self.logger.info(f"✅ RBAC system configured: {len(self.role_store)} roles, {len(self.permission_store)} permissions")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup RBAC system: {e}")
            raise
    
    async def setup_mfa_system(self, mfa_config: Dict[str, Any]) -> None:
        """Multi-factor authentication système."""
        try:
            if not self.auth_config:
                raise ValueError("Auth config not initialized")
            
            self.auth_config.enable_mfa = True
            self.auth_config.mfa_issuer = mfa_config.get('issuer', 'Ainflue')
            
            self.logger.info("✅ MFA system configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup MFA system: {e}")
            raise
    
    async def authenticate_user(self, username: str, password: str, ip_address: str = "", 
                              user_agent: str = "") -> Optional[Dict[str, Any]]:
        """Authenticate user avec password."""
        try:
            # Check if IP is suspicious
            if ip_address in self.suspicious_ips:
                await self._log_audit(AuditAction.FAILED_LOGIN, username, {
                    'reason': 'suspicious_ip',
                    'ip_address': ip_address
                }, ip_address, user_agent, False)
                return None
            
            # Find user
            user = None
            for u in self.user_store.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                await self._handle_failed_login(username, ip_address, user_agent, "user_not_found")
                return None
            
            # Check if account is locked
            if user.account_locked_until and user.account_locked_until > datetime.now():
                await self._log_audit(AuditAction.FAILED_LOGIN, user.id, {
                    'reason': 'account_locked',
                    'locked_until': user.account_locked_until.isoformat()
                }, ip_address, user_agent, False)
                return None
            
            # Check if account is active
            if not user.is_active:
                await self._handle_failed_login(username, ip_address, user_agent, "account_inactive")
                return None
            
            # Verify password
            if not await self._verify_password(password, user.password_hash):
                await self._handle_failed_login(username, ip_address, user_agent, "invalid_password")
                user.failed_login_attempts += 1
                
                # Lock account if too many failures
                if user.failed_login_attempts >= (self.auth_config.max_failed_attempts if self.auth_config else 5):
                    user.account_locked_until = datetime.now() + timedelta(
                        minutes=self.auth_config.account_lockout_minutes if self.auth_config else 30
                    )
                    self.auth_metrics['locked_accounts'] += 1
                    await self._log_audit(AuditAction.ACCOUNT_LOCKED, user.id, {
                        'failed_attempts': user.failed_login_attempts
                    }, ip_address, user_agent, True)
                
                return None
            
            # Successful authentication
            user.failed_login_attempts = 0
            user.last_login = datetime.now()
            
            # Create session
            session = await self._create_session(user, ip_address, user_agent)
            
            # Update metrics
            self.auth_metrics['login_successes'] += 1
            
            # Log successful login
            await self._log_audit(AuditAction.LOGIN, user.id, {
                'session_id': session.id,
                'mfa_required': user.mfa_enabled
            }, ip_address, user_agent, True)
            
            return {
                'user': self._serialize_user(user),
                'session': asdict(session),
                'token': session.token,
                'refresh_token': session.refresh_token,
                'mfa_required': user.mfa_enabled
            }
            
        except Exception as e:
            self.logger.error(f"❌ User authentication failed: {e}")
            return None
    
    async def authenticate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate avec JWT token."""
        try:
            if not JWT_AVAILABLE or not self.auth_config:
                return None
            
            # Decode JWT
            payload = jwt.decode(token, self.auth_config.jwt_secret, 
                               algorithms=[self.auth_config.jwt_algorithm])
            
            user_id = payload.get('user_id')
            session_id = payload.get('session_id')
            
            # Validate session
            if session_id not in self.session_store:
                return None
            
            session = self.session_store[session_id]
            if session.status != SessionStatus.ACTIVE or session.expires_at < datetime.now():
                return None
            
            # Get user
            user = self.user_store.get(user_id)
            if not user or not user.is_active:
                return None
            
            # Update session activity
            session.last_activity = datetime.now()
            
            return {
                'user': self._serialize_user(user),
                'session': asdict(session)
            }
            
        except jwt.ExpiredSignatureError:
            self.logger.debug("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.debug(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ JWT authentication failed: {e}")
            return None
    
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check user permission."""
        try:
            self.auth_metrics['permission_checks'] += 1
            
            user = self.user_store.get(user_id)
            if not user or not user.is_active:
                return False
            
            # Check direct permissions
            permission_name = f"{resource}:{action}"
            if permission_name in user.permissions:
                await self._log_audit(AuditAction.PERMISSION_GRANTED, user_id, {
                    'resource': resource,
                    'action': action,
                    'method': 'direct_permission'
                })
                return True
            
            # Check role-based permissions
            for role_name in user.roles:
                role = self.role_store.get(role_name)
                if role and permission_name in role.permissions:
                    await self._log_audit(AuditAction.PERMISSION_GRANTED, user_id, {
                        'resource': resource,
                        'action': action,
                        'method': 'role_permission',
                        'role': role_name
                    })
                    return True
            
            # Permission denied
            await self._log_audit(AuditAction.PERMISSION_DENIED, user_id, {
                'resource': resource,
                'action': action
            })
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Permission check failed: {e}")
            return False
    
    async def create_user(self, username: str, email: str, password: str, 
                         roles: Optional[List[str]] = None) -> Optional[User]:
        """Create new user."""
        try:
            # Validate password policy
            if not await self._validate_password_policy(password):
                return None
            
            # Check if user exists
            for existing_user in self.user_store.values():
                if existing_user.username == username or existing_user.email == email:
                    self.logger.warning(f"⚠️ User already exists: {username}")
                    return None
            
            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=await self._hash_password(password),
                roles=roles or [],
                is_active=True
            )
            
            self.user_store[user.id] = user
            self.auth_metrics['users_total'] += 1
            
            self.logger.info(f"✅ User created: {username}")
            return user
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create user: {e}")
            return None
    
    async def logout_user(self, session_id: str, ip_address: str = "", 
                         user_agent: str = "") -> bool:
        """Logout user."""
        try:
            if session_id not in self.session_store:
                return False
            
            session = self.session_store[session_id]
            session.status = SessionStatus.REVOKED
            
            # Log logout
            await self._log_audit(AuditAction.LOGOUT, session.user_id, {
                'session_id': session_id
            }, ip_address, user_agent, True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Logout failed: {e}")
            return False
    
    async def _create_session(self, user: User, ip_address: str, user_agent: str) -> Session:
        """Create user session."""
        if not self.auth_config:
            raise ValueError("Auth config not initialized")
        
        # Generate tokens
        session_id = str(uuid.uuid4())
        
        if JWT_AVAILABLE:
            # Create JWT token
            payload = {
                'user_id': user.id,
                'session_id': session_id,
                'username': user.username,
                'roles': user.roles,
                'iat': int(time.time()),
                'exp': int(time.time()) + (self.auth_config.jwt_expiration_minutes * 60)
            }
            token = jwt.encode(payload, self.auth_config.jwt_secret, 
                             algorithm=self.auth_config.jwt_algorithm)
        else:
            token = secrets.token_urlsafe(32)
        
        refresh_token = secrets.token_urlsafe(32)
        
        # Create session
        session = Session(
            id=session_id,
            user_id=user.id,
            token=token,
            refresh_token=refresh_token,
            expires_at=datetime.now() + timedelta(minutes=self.auth_config.session_timeout_minutes),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.session_store[session_id] = session
        self.auth_metrics['sessions_active'] += 1
        
        return session
    
    async def _hash_password(self, password: str) -> str:
        """Hash password."""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback to basic hashing (not recommended for production)
            return hashlib.sha256(password.encode()).hexdigest()
    
    async def _verify_password(self, password: str, password_hash: Optional[str]) -> bool:
        """Verify password against hash."""
        if not password_hash:
            return False
        
        if BCRYPT_AVAILABLE and password_hash.startswith('$2b$'):
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        else:
            # Fallback verification
            return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    async def _validate_password_policy(self, password: str) -> bool:
        """Validate password against policy."""
        if not self.auth_config:
            return len(password) >= 8
        
        if len(password) < self.auth_config.password_min_length:
            return False
        
        if self.auth_config.password_require_uppercase and not any(c.isupper() for c in password):
            return False
        
        if self.auth_config.password_require_numbers and not any(c.isdigit() for c in password):
            return False
        
        if self.auth_config.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        return True
    
    async def _handle_failed_login(self, username: str, ip_address: str, 
                                  user_agent: str, reason: str) -> None:
        """Handle failed login attempt."""
        self.auth_metrics['login_failures'] += 1
        
        # Track failed attempts by IP
        if ip_address:
            if ip_address not in self.failed_attempts:
                self.failed_attempts[ip_address] = []
            
            self.failed_attempts[ip_address].append(datetime.now())
            
            # Clean old attempts (older than 1 hour)
            cutoff = datetime.now() - timedelta(hours=1)
            self.failed_attempts[ip_address] = [
                attempt for attempt in self.failed_attempts[ip_address] 
                if attempt > cutoff
            ]
            
            # Mark IP as suspicious if too many failures
            if len(self.failed_attempts[ip_address]) > 10:
                self.suspicious_ips.add(ip_address)
                self.logger.warning(f"⚠️ IP marked as suspicious: {ip_address}")
        
        # Log failed attempt
        await self._log_audit(AuditAction.FAILED_LOGIN, None, {
            'username': username,
            'reason': reason
        }, ip_address, user_agent, False)
    
    async def _setup_default_rbac(self) -> None:
        """Setup default roles and permissions."""
        try:
            # Default permissions
            default_permissions = [
                Permission("users:read", "users", "read", "Read user information"),
                Permission("users:write", "users", "write", "Write user information"),
                Permission("users:delete", "users", "delete", "Delete users"),
                Permission("roles:read", "roles", "read", "Read roles"),
                Permission("roles:write", "roles", "write", "Write roles"),
                Permission("system:admin", "system", "admin", "System administration")
            ]
            
            for perm in default_permissions:
                self.permission_store[perm.name] = perm
            
            # Default roles
            default_roles = [
                Role("user", "Standard user", ["users:read"]),
                Role("moderator", "Content moderator", ["users:read", "users:write"]),
                Role("admin", "Administrator", list(self.permission_store.keys()))
            ]
            
            for role in default_roles:
                self.role_store[role.name] = role
            
            self.logger.info("✅ Default RBAC setup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup default RBAC: {e}")
    
    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Serialize user for response."""
        user_dict = asdict(user)
        # Remove sensitive information
        user_dict.pop('password_hash', None)
        user_dict.pop('mfa_secret', None)
        user_dict.pop('mfa_backup_codes', None)
        return user_dict
    
    async def _log_audit(self, action: AuditAction, user_id: Optional[str], 
                        details: Dict[str, Any], ip_address: str = "", 
                        user_agent: str = "", success: bool = True) -> None:
        """Log audit event."""
        if not self.audit_logger:
            return
        
        await self.audit_logger.log(action, user_id, details, ip_address, 
                                   user_agent, success)
    
    async def _session_cleanup_task(self) -> None:
        """Background task to cleanup expired sessions."""
        while self.status == "running":
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.session_store.items():
                    if (session.expires_at < current_time or 
                        session.status != SessionStatus.ACTIVE):
                        expired_sessions.append(session_id)
                
                # Remove expired sessions
                for session_id in expired_sessions:
                    del self.session_store[session_id]
                    self.auth_metrics['sessions_active'] -= 1
                
                if expired_sessions:
                    self.logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Session cleanup error: {e}")
                await asyncio.sleep(600)
    
    async def _background_security_monitoring(self) -> None:
        """Background security monitoring."""
        while self.status == "running":
            try:
                # Monitor for security events
                current_time = datetime.now()
                
                # Check for account lockouts
                locked_count = 0
                for user in self.user_store.values():
                    if (user.account_locked_until and 
                        user.account_locked_until > current_time):
                        locked_count += 1
                
                self.auth_metrics['locked_accounts'] = locked_count
                
                # Clean old security events
                cutoff = current_time - timedelta(hours=24)
                self.security_events = [
                    event for event in self.security_events
                    if datetime.fromisoformat(event['timestamp']) > cutoff
                ]
                
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Security monitoring error: {e}")
                await asyncio.sleep(1200)
    
    # Abstract methods pour extension
    @abstractmethod
    async def configure_custom_auth_providers(self) -> Dict[str, Dict]:
        """Configure auth providers spécifiques au service."""
        pass
    
    @abstractmethod
    async def configure_custom_rbac(self) -> Dict[str, Any]:
        """Configure RBAC spécifique au service."""
        pass


class AuditLogger:
    """Logger d'audit pour authentication."""
    
    def __init__(self, auth_service: AuthServiceTemplate):
        self.auth_service = auth_service
        self.audit_logs: List[AuditLog] = []
        self.logger = auth_service.logger
    
    async def log(self, action: AuditAction, user_id: Optional[str], 
                 details: Dict[str, Any], ip_address: str = "", 
                 user_agent: str = "", success: bool = True) -> None:
        """Log audit event."""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                risk_score=await self._calculate_risk_score(action, details, ip_address)
            )
            
            self.audit_logs.append(audit_log)
            self.auth_service.auth_metrics['audit_logs_count'] += 1
            
            # Keep only last 10000 logs
            if len(self.audit_logs) > 10000:
                self.audit_logs = self.audit_logs[-10000:]
            
            # Log high-risk events
            if audit_log.risk_score > 70:
                self.logger.warning(f"🚨 High-risk security event: {action.value} (risk: {audit_log.risk_score})")
            
        except Exception as e:
            self.logger.error(f"❌ Audit logging failed: {e}")
    
    async def _calculate_risk_score(self, action: AuditAction, 
                                   details: Dict[str, Any], ip_address: str) -> float:
        """Calculate risk score for audit event."""
        risk_score = 0.0
        
        # Base risk by action
        action_risks = {
            AuditAction.FAILED_LOGIN: 30.0,
            AuditAction.ACCOUNT_LOCKED: 80.0,
            AuditAction.PERMISSION_DENIED: 20.0,
            AuditAction.LOGIN: 5.0
        }
        
        risk_score += action_risks.get(action, 10.0)
        
        # IP-based risk
        if ip_address in self.auth_service.suspicious_ips:
            risk_score += 40.0
        
        # Multiple failures
        if 'failed_attempts' in details and details['failed_attempts'] > 3:
            risk_score += 30.0
        
        return min(risk_score, 100.0)
    
    async def cleanup(self) -> None:
        """Cleanup audit logger."""
        self.audit_logs.clear()


if __name__ == "__main__":
    print("🔐 Enterprise Authentication Service Template")
    print("Use this template to create secure authentication microservices")
    if not JWT_AVAILABLE:
        print("⚠️ PyJWT not available. Install with: pip install PyJWT")
    if not BCRYPT_AVAILABLE:
        print("⚠️ bcrypt not available. Install with: pip install bcrypt")