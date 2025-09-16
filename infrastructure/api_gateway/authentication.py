"""
Authentication Gateway - Multi-Provider Authentication System
© 2025 Fahed Mlaiel. All rights reserved.

Authentication Gateway providing OAuth2/OIDC, JWT, API Key, and multi-factor
authentication for the creator platform with comprehensive security features.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import hashlib
import secrets
import base64
import hmac
from dataclasses import dataclass, field
import time
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class AuthenticationMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    API_KEY = "api_key"
    BIOMETRIC = "biometric"
    MFA = "mfa"
    SSO = "sso"


class TokenType(Enum):
    """Token types"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    API_KEY = "api_key"
    SESSION_TOKEN = "session_token"


class UserRole(Enum):
    """User roles"""
    CREATOR = "creator"
    ADMIN = "admin"
    MODERATOR = "moderator"
    PLATFORM_INTEGRATION = "platform_integration"
    AI_SERVICE = "ai_service"
    GUEST = "guest"


class AuthenticationStatus(Enum):
    """Authentication status"""
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"
    BLOCKED = "blocked"
    REQUIRES_MFA = "requires_mfa"
    REQUIRES_VERIFICATION = "requires_verification"


@dataclass
class User:
    """User information"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    display_name: str = ""
    roles: List[UserRole] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    mfa_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthenticationToken:
    """Authentication token"""
    token: str
    type: TokenType
    user_id: str
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_revoked: bool = False


@dataclass
class AuthenticationAttempt:
    """Authentication attempt record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    method: AuthenticationMethod = AuthenticationMethod.PASSWORD
    status: AuthenticationStatus = AuthenticationStatus.FAILED
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OAuth2Provider:
    """OAuth2 provider configuration"""
    name: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scopes: List[str] = field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIKey:
    """API Key configuration"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    name: str = ""
    user_id: str = ""
    scopes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True
    rate_limit: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AuthenticationGateway:
    """
    Enterprise Authentication Gateway
    
    Provides comprehensive authentication services including:
    - Multi-provider OAuth2/OIDC authentication
    - JWT token management and validation
    - API key generation and validation
    - Multi-factor authentication (MFA)
    - Session management
    - Biometric authentication support
    - Security logging and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Authentication Gateway"""
        self.config = config or {}
        self.users: Dict[str, User] = {}
        self.tokens: Dict[str, AuthenticationToken] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.oauth2_providers: Dict[str, OAuth2Provider] = {}
        self.auth_attempts: List[AuthenticationAttempt] = []
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.blacklisted_tokens: set = set()
        
        # Configuration
        self.jwt_secret = self.config.get('jwt_secret', self._generate_secret())
        self.jwt_algorithm = self.config.get('jwt_algorithm', 'HS256')
        self.access_token_ttl = self.config.get('access_token_ttl', 3600)  # 1 hour
        self.refresh_token_ttl = self.config.get('refresh_token_ttl', 86400 * 7)  # 7 days
        self.api_key_ttl = self.config.get('api_key_ttl', 86400 * 365)  # 1 year
        self.session_ttl = self.config.get('session_ttl', 3600 * 24)  # 24 hours
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.lockout_duration = self.config.get('lockout_duration', 900)  # 15 minutes
        
        # Security settings
        self.require_mfa_for_admin = self.config.get('require_mfa_for_admin', True)
        self.password_min_length = self.config.get('password_min_length', 8)
        self.enable_rate_limiting = self.config.get('enable_rate_limiting', True)
        self.enable_geo_blocking = self.config.get('enable_geo_blocking', False)
        
        # Setup default OAuth2 providers
        self._setup_oauth2_providers()
        
        # Start cleanup tasks
        self._start_cleanup_tasks()
        
        logger.info("Authentication Gateway initialized")
    
    def _setup_oauth2_providers(self):
        """Setup default OAuth2 providers"""
        # Note: In production, these would come from environment variables
        default_providers = {
            'google': OAuth2Provider(
                name='Google',
                client_id=self.config.get('google_client_id', 'google_client_id'),
                client_secret=self.config.get('google_client_secret', 'google_client_secret'),
                auth_url='https://accounts.google.com/o/oauth2/auth',
                token_url='https://oauth2.googleapis.com/token',
                user_info_url='https://www.googleapis.com/oauth2/v2/userinfo',
                scopes=['openid', 'email', 'profile']
            ),
            'github': OAuth2Provider(
                name='GitHub',
                client_id=self.config.get('github_client_id', 'github_client_id'),
                client_secret=self.config.get('github_client_secret', 'github_client_secret'),
                auth_url='https://github.com/login/oauth/authorize',
                token_url='https://github.com/login/oauth/access_token',
                user_info_url='https://api.github.com/user',
                scopes=['user:email']
            ),
            'twitter': OAuth2Provider(
                name='Twitter',
                client_id=self.config.get('twitter_client_id', 'twitter_client_id'),
                client_secret=self.config.get('twitter_client_secret', 'twitter_client_secret'),
                auth_url='https://twitter.com/i/oauth2/authorize',
                token_url='https://api.twitter.com/2/oauth2/token',
                user_info_url='https://api.twitter.com/2/users/me',
                scopes=['tweet.read', 'users.read']
            ),
            'youtube': OAuth2Provider(
                name='YouTube',
                client_id=self.config.get('youtube_client_id', 'youtube_client_id'),
                client_secret=self.config.get('youtube_client_secret', 'youtube_client_secret'),
                auth_url='https://accounts.google.com/o/oauth2/auth',
                token_url='https://oauth2.googleapis.com/token',
                user_info_url='https://www.googleapis.com/youtube/v3/channels',
                scopes=['https://www.googleapis.com/auth/youtube.readonly']
            ),
            'tiktok': OAuth2Provider(
                name='TikTok',
                client_id=self.config.get('tiktok_client_id', 'tiktok_client_id'),
                client_secret=self.config.get('tiktok_client_secret', 'tiktok_client_secret'),
                auth_url='https://www.tiktok.com/auth/authorize/',
                token_url='https://open-api.tiktok.com/oauth/access_token/',
                user_info_url='https://open-api.tiktok.com/oauth/userinfo/',
                scopes=['user.info.basic']
            )
        }
        
        self.oauth2_providers.update(default_providers)
        logger.info(f"Setup {len(default_providers)} OAuth2 providers")
    
    def _start_cleanup_tasks(self):
        """Start background cleanup tasks"""
        asyncio.create_task(self._cleanup_expired_tokens())
        asyncio.create_task(self._cleanup_old_auth_attempts())
        asyncio.create_task(self._cleanup_expired_sessions())
    
    async def authenticate_password(self, username: str, password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Tuple[AuthenticationStatus, Optional[Dict[str, Any]]]:
        """Authenticate user with username/password"""
        try:
            # Check rate limiting
            if not await self._check_rate_limit(username, ip_address):
                return AuthenticationStatus.BLOCKED, None
            
            # Find user
            user = self._find_user_by_username(username)
            if not user:
                await self._record_auth_attempt(
                    user_id=None,
                    method=AuthenticationMethod.PASSWORD,
                    status=AuthenticationStatus.FAILED,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason="User not found"
                )
                return AuthenticationStatus.FAILED, None
            
            # Verify password
            if not await self._verify_password(user.id, password):
                await self._record_auth_attempt(
                    user_id=user.id,
                    method=AuthenticationMethod.PASSWORD,
                    status=AuthenticationStatus.FAILED,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason="Invalid password"
                )
                return AuthenticationStatus.FAILED, None
            
            # Check if user is active
            if not user.is_active:
                await self._record_auth_attempt(
                    user_id=user.id,
                    method=AuthenticationMethod.PASSWORD,
                    status=AuthenticationStatus.BLOCKED,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason="User account disabled"
                )
                return AuthenticationStatus.BLOCKED, None
            
            # Check MFA requirement
            if user.mfa_enabled or (UserRole.ADMIN in user.roles and self.require_mfa_for_admin):
                await self._record_auth_attempt(
                    user_id=user.id,
                    method=AuthenticationMethod.PASSWORD,
                    status=AuthenticationStatus.REQUIRES_MFA,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return AuthenticationStatus.REQUIRES_MFA, {'user_id': user.id, 'mfa_required': True}
            
            # Generate tokens
            tokens = await self._generate_tokens(user)
            
            # Update user login time
            user.last_login = datetime.utcnow()
            
            # Record successful authentication
            await self._record_auth_attempt(
                user_id=user.id,
                method=AuthenticationMethod.PASSWORD,
                status=AuthenticationStatus.SUCCESS,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return AuthenticationStatus.SUCCESS, {
                'user': self._user_to_dict(user),
                'tokens': tokens
            }
            
        except Exception as e:
            logger.error(f"Password authentication error: {e}")
            return AuthenticationStatus.FAILED, None
    
    async def authenticate_oauth2(self, provider: str, authorization_code: str, redirect_uri: str) -> Tuple[AuthenticationStatus, Optional[Dict[str, Any]]]:
        """Authenticate user with OAuth2 authorization code"""
        try:
            if provider not in self.oauth2_providers:
                logger.error(f"OAuth2 provider not found: {provider}")
                return AuthenticationStatus.FAILED, None
            
            oauth_provider = self.oauth2_providers[provider]
            
            # Exchange authorization code for access token
            token_response = await self._exchange_oauth2_code(oauth_provider, authorization_code, redirect_uri)
            if not token_response:
                return AuthenticationStatus.FAILED, None
            
            # Get user info from provider
            user_info = await self._get_oauth2_user_info(oauth_provider, token_response['access_token'])
            if not user_info:
                return AuthenticationStatus.FAILED, None
            
            # Find or create user
            user = await self._find_or_create_oauth2_user(provider, user_info)
            
            # Generate tokens
            tokens = await self._generate_tokens(user)
            
            # Update user login time
            user.last_login = datetime.utcnow()
            
            # Record successful authentication
            await self._record_auth_attempt(
                user_id=user.id,
                method=AuthenticationMethod.OAUTH2,
                status=AuthenticationStatus.SUCCESS,
                metadata={'provider': provider}
            )
            
            return AuthenticationStatus.SUCCESS, {
                'user': self._user_to_dict(user),
                'tokens': tokens,
                'provider': provider
            }
            
        except Exception as e:
            logger.error(f"OAuth2 authentication error: {e}")
            return AuthenticationStatus.FAILED, None
    
    async def validate_jwt_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate JWT token"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                return False, None
            
            # Decode and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check expiration
            if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
                return False, None
            
            # Get user info
            user_id = payload.get('user_id')
            if not user_id or user_id not in self.users:
                return False, None
            
            user = self.users[user_id]
            if not user.is_active:
                return False, None
            
            return True, {
                'user_id': user_id,
                'username': user.username,
                'roles': [role.value for role in user.roles],
                'scopes': payload.get('scopes', []),
                'token_type': payload.get('token_type', 'access_token')
            }
            
        except jwt.ExpiredSignatureError:
            return False, None
        except jwt.InvalidTokenError:
            return False, None
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return False, None
    
    async def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate API key"""
        try:
            # Find API key
            key_obj = None
            for key in self.api_keys.values():
                if key.key == api_key and key.is_active:
                    key_obj = key
                    break
            
            if not key_obj:
                return False, None
            
            # Check expiration
            if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
                key_obj.is_active = False
                return False, None
            
            # Check user
            if key_obj.user_id not in self.users:
                return False, None
            
            user = self.users[key_obj.user_id]
            if not user.is_active:
                return False, None
            
            # Update last used
            key_obj.last_used = datetime.utcnow()
            
            return True, {
                'user_id': user.id,
                'username': user.username,
                'roles': [role.value for role in user.roles],
                'scopes': key_obj.scopes,
                'api_key_id': key_obj.id,
                'api_key_name': key_obj.name
            }
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False, None
    
    async def create_api_key(self, user_id: str, name: str, scopes: List[str], expires_days: Optional[int] = None) -> Optional[APIKey]:
        """Create new API key for user"""
        try:
            if user_id not in self.users:
                logger.error(f"User not found: {user_id}")
                return None
            
            expires_at = None
            if expires_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            api_key = APIKey(
                name=name,
                user_id=user_id,
                scopes=scopes,
                expires_at=expires_at
            )
            
            self.api_keys[api_key.id] = api_key
            
            logger.info(f"API key created: {api_key.id} for user {user_id}")
            return api_key
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        try:
            # Add to blacklist
            self.blacklisted_tokens.add(token)
            
            # Try to decode to get token info for logging
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm], options={"verify_exp": False})
                logger.info(f"Token revoked for user: {payload.get('user_id')}")
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token using refresh token"""
        try:
            # Validate refresh token
            valid, payload = await self.validate_jwt_token(refresh_token)
            if not valid or not payload:
                return None
            
            # Check if it's a refresh token
            token_data = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm], options={"verify_exp": False})
            if token_data.get('token_type') != 'refresh_token':
                return None
            
            # Get user
            user_id = payload['user_id']
            if user_id not in self.users:
                return None
            
            user = self.users[user_id]
            
            # Generate new tokens
            tokens = await self._generate_tokens(user)
            
            # Revoke old refresh token
            await self.revoke_token(refresh_token)
            
            return tokens
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """Create new user"""
        try:
            user = User(
                username=user_data['username'],
                email=user_data.get('email', ''),
                display_name=user_data.get('display_name', user_data['username']),
                roles=[UserRole(role) for role in user_data.get('roles', ['creator'])],
                is_verified=user_data.get('is_verified', False),
                mfa_enabled=user_data.get('mfa_enabled', False),
                metadata=user_data.get('metadata', {})
            )
            
            self.users[user.id] = user
            
            # Store password hash if provided
            if 'password' in user_data:
                await self._store_password_hash(user.id, user_data['password'])
            
            logger.info(f"User created: {user.id} ({user.username})")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active sessions for user"""
        try:
            user_sessions = []
            for session_id, session_data in self.sessions.items():
                if session_data.get('user_id') == user_id:
                    user_sessions.append({
                        'session_id': session_id,
                        'created_at': session_data.get('created_at'),
                        'last_activity': session_data.get('last_activity'),
                        'ip_address': session_data.get('ip_address'),
                        'user_agent': session_data.get('user_agent')
                    })
            
            return user_sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []
    
    async def get_auth_metrics(self) -> Dict[str, Any]:
        """Get authentication metrics"""
        try:
            recent_attempts = [
                attempt for attempt in self.auth_attempts
                if (datetime.utcnow() - attempt.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            successful_auths = len([a for a in recent_attempts if a.status == AuthenticationStatus.SUCCESS])
            failed_auths = len([a for a in recent_attempts if a.status == AuthenticationStatus.FAILED])
            
            # Count by authentication method
            method_counts = {}
            for method in AuthenticationMethod:
                method_counts[method.value] = len([a for a in recent_attempts if a.method == method])
            
            # Active sessions and tokens
            active_sessions = len(self.sessions)
            active_tokens = len([t for t in self.tokens.values() if not t.is_revoked and t.expires_at > datetime.utcnow()])
            active_api_keys = len([k for k in self.api_keys.values() if k.is_active])
            
            return {
                'recent_auth_attempts': len(recent_attempts),
                'successful_authentications': successful_auths,
                'failed_authentications': failed_auths,
                'success_rate': (successful_auths / len(recent_attempts) * 100) if recent_attempts else 0,
                'auth_methods': method_counts,
                'active_users': len([u for u in self.users.values() if u.is_active]),
                'active_sessions': active_sessions,
                'active_tokens': active_tokens,
                'active_api_keys': active_api_keys,
                'oauth2_providers': len([p for p in self.oauth2_providers.values() if p.enabled]),
                'blacklisted_tokens': len(self.blacklisted_tokens),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting auth metrics: {e}")
            return {'error': str(e)}
    
    # Internal Implementation Methods
    
    def _generate_secret(self) -> str:
        """Generate JWT secret"""
        return base64.b64encode(secrets.token_bytes(32)).decode()
    
    def _find_user_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        for user in self.users.values():
            if user.username == username or user.email == username:
                return user
        return None
    
    async def _verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password"""
        # In production, this would check against stored password hash
        # For demo purposes, we'll use a simple check
        stored_hash = getattr(self, f'_password_hash_{user_id}', None)
        if not stored_hash:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(stored_hash, password_hash)
    
    async def _store_password_hash(self, user_id: str, password: str):
        """Store password hash for user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        setattr(self, f'_password_hash_{user_id}', password_hash)
    
    async def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens for user"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'roles': [role.value for role in user.roles],
            'token_type': 'access_token',
            'iat': now,
            'exp': now + timedelta(seconds=self.access_token_ttl)
        }
        
        access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Refresh token
        refresh_payload = {
            'user_id': user.id,
            'token_type': 'refresh_token',
            'iat': now,
            'exp': now + timedelta(seconds=self.refresh_token_ttl)
        }
        
        refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store tokens
        access_token_obj = AuthenticationToken(
            token=access_token,
            type=TokenType.ACCESS_TOKEN,
            user_id=user.id,
            expires_at=now + timedelta(seconds=self.access_token_ttl)
        )
        
        refresh_token_obj = AuthenticationToken(
            token=refresh_token,
            type=TokenType.REFRESH_TOKEN,
            user_id=user.id,
            expires_at=now + timedelta(seconds=self.refresh_token_ttl)
        )
        
        self.tokens[access_token] = access_token_obj
        self.tokens[refresh_token] = refresh_token_obj
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': self.access_token_ttl
        }
    
    async def _exchange_oauth2_code(self, provider: OAuth2Provider, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange OAuth2 authorization code for access token"""
        # In production, this would make HTTP request to provider's token endpoint
        # For demo, return mock response
        return {
            'access_token': f'mock_access_token_{secrets.token_urlsafe(16)}',
            'token_type': 'bearer',
            'expires_in': 3600,
            'refresh_token': f'mock_refresh_token_{secrets.token_urlsafe(16)}'
        }
    
    async def _get_oauth2_user_info(self, provider: OAuth2Provider, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from OAuth2 provider"""
        # In production, this would make HTTP request to provider's user info endpoint
        # For demo, return mock user info
        return {
            'id': f'oauth_{provider.name}_{secrets.token_urlsafe(8)}',
            'email': f'user@{provider.name.lower()}.com',
            'name': f'{provider.name} User',
            'username': f'{provider.name.lower()}_user_{secrets.token_urlsafe(4)}'
        }
    
    async def _find_or_create_oauth2_user(self, provider: str, user_info: Dict[str, Any]) -> User:
        """Find existing user or create new user from OAuth2 info"""
        # Try to find existing user by email
        email = user_info.get('email', '')
        existing_user = None
        
        for user in self.users.values():
            if user.email == email:
                existing_user = user
                break
        
        if existing_user:
            return existing_user
        
        # Create new user
        user = User(
            username=user_info.get('username', f"{provider}_{secrets.token_urlsafe(4)}"),
            email=email,
            display_name=user_info.get('name', ''),
            roles=[UserRole.CREATOR],
            is_verified=True,  # OAuth2 users are pre-verified
            metadata={'oauth2_provider': provider, 'oauth2_id': user_info.get('id')}
        )
        
        self.users[user.id] = user
        return user
    
    async def _check_rate_limit(self, username: str, ip_address: Optional[str]) -> bool:
        """Check rate limiting for authentication attempts"""
        if not self.enable_rate_limiting:
            return True
        
        # Check recent failed attempts
        recent_attempts = [
            attempt for attempt in self.auth_attempts
            if (datetime.utcnow() - attempt.timestamp).total_seconds() < self.lockout_duration
        ]
        
        # Count failed attempts by username
        username_failures = len([
            a for a in recent_attempts
            if a.user_id == username and a.status == AuthenticationStatus.FAILED
        ])
        
        # Count failed attempts by IP
        ip_failures = 0
        if ip_address:
            ip_failures = len([
                a for a in recent_attempts
                if a.ip_address == ip_address and a.status == AuthenticationStatus.FAILED
            ])
        
        return username_failures < self.max_login_attempts and ip_failures < self.max_login_attempts
    
    async def _record_auth_attempt(self, user_id: Optional[str], method: AuthenticationMethod, status: AuthenticationStatus, ip_address: Optional[str] = None, user_agent: Optional[str] = None, failure_reason: Optional[str] = None):
        """Record authentication attempt"""
        attempt = AuthenticationAttempt(
            user_id=user_id,
            method=method,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        )
        
        self.auth_attempts.append(attempt)
        
        # Log attempt
        log_level = logging.INFO if status == AuthenticationStatus.SUCCESS else logging.WARNING
        logger.log(log_level, f"Auth attempt: {method.value} for user {user_id} from {ip_address} - {status.value}")
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user object to dictionary"""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'display_name': user.display_name,
            'roles': [role.value for role in user.roles],
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'mfa_enabled': user.mfa_enabled,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    async def _cleanup_expired_tokens(self):
        """Clean up expired tokens"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_tokens = [
                    token for token, token_obj in self.tokens.items()
                    if token_obj.expires_at < current_time
                ]
                
                for token in expired_tokens:
                    del self.tokens[token]
                    self.blacklisted_tokens.discard(token)
                
                if expired_tokens:
                    logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in token cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def _cleanup_old_auth_attempts(self):
        """Clean up old authentication attempts"""
        while True:
            try:
                cutoff_time = datetime.utcnow() - timedelta(days=7)  # Keep 7 days
                
                old_count = len(self.auth_attempts)
                self.auth_attempts = [
                    attempt for attempt in self.auth_attempts
                    if attempt.timestamp > cutoff_time
                ]
                
                cleaned_count = old_count - len(self.auth_attempts)
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} old auth attempts")
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Error in auth attempts cleanup: {e}")
                await asyncio.sleep(86400)
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session_data in self.sessions.items():
                    last_activity = session_data.get('last_activity', session_data.get('created_at'))
                    if isinstance(last_activity, str):
                        last_activity = datetime.fromisoformat(last_activity)
                    
                    if (current_time - last_activity).total_seconds() > self.session_ttl:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.sessions[session_id]
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(3600)


# Authentication Gateway Factory
def create_authentication_gateway(config: Optional[Dict[str, Any]] = None) -> AuthenticationGateway:
    """Factory function to create Authentication Gateway instance"""
    return AuthenticationGateway(config)


# Creator Platform Authentication Scopes
CREATOR_PLATFORM_SCOPES = {
    'content:read': 'Read access to content',
    'content:write': 'Write access to content',
    'content:delete': 'Delete content',
    'analytics:read': 'Read analytics data',
    'revenue:read': 'Read revenue data',
    'profile:read': 'Read profile information',
    'profile:write': 'Update profile information',
    'collaboration:read': 'Read collaboration data',
    'collaboration:write': 'Create and manage collaborations',
    'ai:process': 'Use AI processing services',
    'admin:users': 'Manage users (admin only)',
    'admin:platform': 'Manage platform settings (admin only)',
    'platform:integrate': 'Integrate with external platforms',
    'api:access': 'General API access'
}


if __name__ == "__main__":
    # Example usage
    async def main():
        auth_gateway = create_authentication_gateway({
            'jwt_secret': 'test_secret',
            'access_token_ttl': 3600,
            'require_mfa_for_admin': True
        })
        
        # Create test user
        user_data = {
            'username': 'test_creator',
            'email': 'creator@example.com',
            'password': 'secure_password123',
            'roles': ['creator'],
            'display_name': 'Test Creator'
        }
        
        user = await auth_gateway.create_user(user_data)
        if user:
            print(f"User created: {user.username}")
            
            # Test password authentication
            status, result = await auth_gateway.authenticate_password('test_creator', 'secure_password123')
            print(f"Authentication status: {status}")
            
            if result and 'tokens' in result:
                # Test token validation
                access_token = result['tokens']['access_token']
                valid, token_data = await auth_gateway.validate_jwt_token(access_token)
                print(f"Token validation: {valid}")
                
                # Create API key
                api_key = await auth_gateway.create_api_key(
                    user.id, 
                    'Test API Key', 
                    ['content:read', 'analytics:read']
                )
                if api_key:
                    print(f"API key created: {api_key.key[:16]}...")
                    
                    # Test API key validation
                    valid, key_data = await auth_gateway.validate_api_key(api_key.key)
                    print(f"API key validation: {valid}")
        
        # Get metrics
        metrics = await auth_gateway.get_auth_metrics()
        print(f"Auth metrics: {json.dumps(metrics, indent=2)}")
    
    asyncio.run(main())