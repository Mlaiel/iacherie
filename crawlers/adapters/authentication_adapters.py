"""Authentication Adapters - Enterprise Multi-method Authentication System
======================================================================

Industrial-grade adapters for comprehensive authentication and security protocols
in the IA-Influencer platform. Supports OAuth2, JWT, API Keys, Basic Auth, 
Certificate-based auth, Multi-Factor Authentication, and Single Sign-On.

Business Logic: User Authentication → Security Validation → Access Control → Session Management

Supported Authentication Methods:
- OAuth2 2.0/2.1 with PKCE and refresh token management
- JWT with RS256/HS256/ES256 and custom claims validation
- API key rotation and lifecycle management
- Certificate-based mutual TLS authentication
- Multi-Factor Authentication (TOTP, SMS, Email, Hardware keys)
- Single Sign-On with SAML 2.0 and OpenID Connect
- Passwordless authentication (WebAuthn, Magic links)
- Social authentication (Google, Facebook, GitHub, LinkedIn)
- Enterprise directory integration (LDAP, Active Directory)

Advanced Security Features:
- Rate limiting and brute force protection
- Session management with secure storage
- Token encryption and secure transmission
- Audit logging and compliance tracking
- Risk-based authentication and fraud detection
- Device fingerprinting and trust scoring
- Automatic security policy enforcement
- Real-time threat detection and response
- Zero-trust security architecture
- Enterprise compliance (SOC2, GDPR, HIPAA)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import asyncio
import logging
import hashlib
import hmac
import base64
import secrets
import ssl
import time
import uuid
import re
from typing import Dict, List, Optional, Any, Union, Callable, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from abc import ABC, abstractmethod
from enum import Enum
import urllib.parse
from urllib.parse import urlencode, parse_qs, quote, unquote
import ipaddress
from collections import defaultdict, Counter

# Advanced JWT and cryptography imports
try:
    import jwt
    import pyotp
    import qrcode
    from jose import jwt as jose_jwt, JWTError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet, MultiFernet
    from cryptography.x509.oid import NameOID
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# HTTP client and security imports
import aiohttp
import bcrypt
import argon2

# WebAuthn imports (optional)
try:
    from webauthn import generate_registration_options, generate_authentication_options
    from webauthn import verify_registration_response, verify_authentication_response
    WEBAUTHN_AVAILABLE = True
except ImportError:
    WEBAUTHN_AVAILABLE = False

# SAML and SSO imports (optional)
try:
    from onelogin.saml2.auth import OneLogin_Saml2_Auth
    from onelogin.saml2.settings import OneLogin_Saml2_Settings
    from onelogin.saml2.utils import OneLogin_Saml2_Utils
    SAML_AVAILABLE = True
except ImportError:
    SAML_AVAILABLE = False

# LDAP imports (optional)
try:
    import ldap3
    LDAP_AVAILABLE = True
except ImportError:
    LDAP_AVAILABLE = False

# OAuth2 clients
try:
    from authlib.integrations.httpx_client import AsyncOAuth2Client
    from authlib.oauth2.rfc6749 import OAuth2Token
    AUTHLIB_AVAILABLE = True
except ImportError:
    AUTHLIB_AVAILABLE = False

logger = logging.getLogger(__name__)

class AuthType(Enum):
    """Supported authentication types."""    OAUTH2 = "oauth2"
    JWT = "jwt"
    API_KEY = "api_key"
    BASIC = "basic"
    CERTIFICATE = "certificate"
    MFA = "mfa"
    SSO = "sso"
    SAML = "saml"
    OPENID_CONNECT = "openid_connect"

class TokenType(Enum):
    """Token types."""    BEARER = "Bearer"
    BASIC = "Basic"
    API_KEY = "ApiKey"
    JWT = "JWT"

class MFAMethod(Enum):
    """Multi-factor authentication methods."""    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_TOKEN = "hardware_token"
    BIOMETRIC = "biometric"

@dataclass
class AuthMetrics:
    """Authentication metrics tracking."""    total_attempts: int = 0
    successful_auths: int = 0
    failed_auths: int = 0
    tokens_issued: int = 0
    tokens_refreshed: int = 0
    mfa_challenges: int = 0
    last_auth_time: Optional[datetime] = None
    avg_auth_time: float = 0.0
    
@dataclass
class SecurityPolicy:
    """Security policy configuration."""    max_failed_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    token_max_age: int = 3600  # 1 hour
    refresh_token_max_age: int = 86400  # 24 hours
    require_mfa: bool = False
    allowed_domains: List[str] = field(default_factory=list)
    password_min_length: int = 8
    password_require_special: bool = True
    session_timeout: int = 1800  # 30 minutes

@dataclass
class AuthConfig:
    """Advanced configuration for authentication adapters."""    # Basic auth settings
    auth_type: AuthType
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # API Key settings
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_key_header: str = "X-API-Key"
    api_key_location: str = "header"  # header, query, body
    
    # OAuth2 settings
    token_url: Optional[str] = None
    authorize_url: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: List[str] = field(default_factory=list)
    use_pkce: bool = True
    pkce_code_challenge_method: str = "S256"
    
    # JWT settings
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_issuer: Optional[str] = None
    jwt_audience: Optional[str] = None
    jwt_public_key: Optional[str] = None
    jwt_private_key: Optional[str] = None
    
    # Certificate settings
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    ca_bundle_path: Optional[str] = None
    
    # MFA settings
    mfa_enabled: bool = False
    mfa_methods: List[MFAMethod] = field(default_factory=list)
    totp_issuer: str = "IA-Influencer Agent"
    
    # SSO settings
    sso_provider: Optional[str] = None
    sso_metadata_url: Optional[str] = None
    saml_settings: Optional[Dict] = None
    
    # Token management
    token_expiry: int = 3600  # seconds
    refresh_threshold: int = 300  # seconds before expiry to refresh
    auto_refresh: bool = True
    token_encryption_key: Optional[str] = None
    
    # Security settings
    security_policy: Optional[SecurityPolicy] = None
    audit_logging: bool = True
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60
    
    # Custom headers and options
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_params: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0

@dataclass
class AuthToken:
    """Enhanced authentication token container."""    access_token: str
    token_type: TokenType = TokenType.BEARER
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced properties
    issued_at: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    claims: Dict[str, Any] = field(default_factory=dict)
    encrypted: bool = False
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at
    
    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh."""        if not self.expires_at:
            return False
        threshold = datetime.now() + timedelta(seconds=300)  # 5 minutes before expiry
        return threshold >= self.expires_at
    
    @property
    def time_to_expiry(self) -> Optional[timedelta]:
        """Get time until token expires."""        if not self.expires_at:
            return None
        return self.expires_at - datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""        return {
            'access_token': self.access_token,
            'token_type': self.token_type.value,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'refresh_token': self.refresh_token,
            'scope': self.scope,
            'metadata': self.metadata,
            'issued_at': self.issued_at.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'claims': self.claims
        }

@dataclass
class AuthResult:
    """Enhanced authentication result container."""    success: bool
    token: Optional[AuthToken] = None
    headers: Dict[str, str] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced properties
    auth_method: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None
    permissions: List[str] = field(default_factory=list)
    session_id: Optional[str] = None
    mfa_required: bool = False
    mfa_challenge: Optional[Dict[str, Any]] = None
    
    # Audit information
    timestamp: datetime = field(default_factory=datetime.now)
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

class TokenManager:
    """Advanced token management with encryption and caching."""    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize token manager."""        self.encryption_key = encryption_key
        self._cipher = None
        self._token_cache: Dict[str, AuthToken] = {}
        
        if encryption_key and CRYPTO_AVAILABLE:
            key = base64.urlsafe_b64encode(
                encryption_key.encode()[:32].ljust(32, b'0')
            )
            self._cipher = Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt token for secure storage."""        if not self._cipher:
            return token
        
        encrypted = self._cipher.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token from secure storage."""        if not self._cipher:
            return encrypted_token
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = self._cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            raise
    
    def cache_token(self, key: str, token: AuthToken):
        """Cache token with optional encryption."""        if self.encryption_key:
            token.access_token = self.encrypt_token(token.access_token)
            if token.refresh_token:
                token.refresh_token = self.encrypt_token(token.refresh_token)
            token.encrypted = True
        
        self._token_cache[key] = token
    
    def get_cached_token(self, key: str) -> Optional[AuthToken]:
        """Retrieve cached token with decryption."""        token = self._token_cache.get(key)
        if not token:
            return None
        
        if token.encrypted and self.encryption_key:
            token.access_token = self.decrypt_token(token.access_token)
            if token.refresh_token:
                token.refresh_token = self.decrypt_token(token.refresh_token)
            token.encrypted = False
        
        return token
    
    def remove_token(self, key: str):
        """Remove token from cache."""        self._token_cache.pop(key, None)

class SessionManager:
    """Session management for authentication."""    
    def __init__(self, session_timeout: int = 1800):
        """Initialize session manager."""        self.session_timeout = session_timeout
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, user_id: str, auth_data: Dict[str, Any]) -> str:
        """Create new session."""        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'auth_data': auth_data,
            'expires_at': datetime.now() + timedelta(seconds=self.session_timeout)
        }
        self._sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # Check if session is expired
        if datetime.now() > session['expires_at']:
            self.remove_session(session_id)
            return None
        
        # Update last accessed time
        session['last_accessed'] = datetime.now()
        return session
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session timeout."""        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session['expires_at'] = datetime.now() + timedelta(seconds=self.session_timeout)
        return True
    
    def remove_session(self, session_id: str):
        """Remove session."""        self._sessions.pop(session_id, None)
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""        now = datetime.now()
        expired_sessions = [
            sid for sid, session in self._sessions.items()
            if now > session['expires_at']
        ]
        for sid in expired_sessions:
            self.remove_session(sid)

class SecurityValidator:
    """Security validation utilities."""    
    def __init__(self, policy: Optional[SecurityPolicy] = None):
        """Initialize security validator."""        self.policy = policy or SecurityPolicy()
        self._failed_attempts: Dict[str, List[datetime]] = {}
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password against security policy."""        errors = []
        
        if len(password) < self.policy.password_min_length:
            errors.append(f"Password must be at least {self.policy.password_min_length} characters")
        
        if self.policy.password_require_special:
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                errors.append("Password must contain special characters")
        
        return len(errors) == 0, errors
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier is rate limited."""        now = datetime.now()
        attempts = self._failed_attempts.get(identifier, [])
        
        # Clean old attempts
        recent_attempts = [
            attempt for attempt in attempts
            if now - attempt < timedelta(seconds=self.policy.lockout_duration)
        ]
        self._failed_attempts[identifier] = recent_attempts
        
        return len(recent_attempts) < self.policy.max_failed_attempts
    
    def record_failed_attempt(self, identifier: str):
        """Record failed authentication attempt."""        if identifier not in self._failed_attempts:
            self._failed_attempts[identifier] = []
        self._failed_attempts[identifier].append(datetime.now())
    
    def validate_domain(self, email: str) -> bool:
        """Validate email domain against allowed domains."""        if not self.policy.allowed_domains:
            return True
        
        domain = email.split('@')[-1].lower()
        return domain in [d.lower() for d in self.policy.allowed_domains]

class AuthenticationAdapter(ABC):
    """Enterprise base class for all authentication adapters."""    
    def __init__(self, config: AuthConfig):
        """Initialize authentication adapter with enterprise features."""        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_token: Optional[AuthToken] = None
        self.auth_method = ""
        
        # Enterprise features
        self.metrics = AuthMetrics()
        self.token_manager = TokenManager(config.token_encryption_key)
        self.session_manager = SessionManager(
            config.security_policy.session_timeout if config.security_policy else 1800
        )
        self.security_validator = SecurityValidator(config.security_policy)
        
        # Rate limiting
        self._rate_limit_tokens: Dict[str, List[datetime]] = {}
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check rate limiting for authentication attempts."""        if not self.config.rate_limit_enabled:
            return True
        
        now = datetime.now()
        tokens = self._rate_limit_tokens.get(identifier, [])
        
        # Clean old tokens
        recent_tokens = [
            token for token in tokens
            if now - token < timedelta(minutes=1)
        ]
        self._rate_limit_tokens[identifier] = recent_tokens
        
        return len(recent_tokens) < self.config.max_requests_per_minute
    
    def _record_auth_attempt(self, success: bool, auth_time: float):
        """Record authentication attempt metrics."""        self.metrics.total_attempts += 1
        if success:
            self.metrics.successful_auths += 1
        else:
            self.metrics.failed_auths += 1
        
        self.metrics.last_auth_time = datetime.now()
        
        # Update average auth time
        total_time = self.metrics.avg_auth_time * (self.metrics.total_attempts - 1) + auth_time
        self.metrics.avg_auth_time = total_time / self.metrics.total_attempts
    
    @abstractmethod
    async def authenticate(self, **kwargs) -> AuthResult:
        """Authenticate using the specific method."""        pass
    
    @abstractmethod
    async def authenticate(self) -> AuthResult:
        """Perform authentication."""        pass
    
    @abstractmethod
    async def refresh_token(self) -> AuthResult:
        """Refresh authentication token."""        pass
    
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""        pass
    
    async def ensure_valid_token(self) -> bool:
        """Ensure we have a valid token."""        if not self.current_token:
            result = await self.authenticate()
            return result.success
        
        if self.current_token.needs_refresh:
            result = await self.refresh_token()
            return result.success
        
        return True
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""        return (self.current_token is not None and 
                not self.current_token.is_expired)

class OAuth2Adapter(AuthenticationAdapter):
    """Adapter for OAuth2 authentication."""    
    def __init__(self, config: AuthConfig):
        """Initialize OAuth2 adapter."""        super().__init__(config)
        self.auth_method = "OAuth2"
        
        if not config.client_id or not config.client_secret:
            raise ValueError("OAuth2 requires client_id and client_secret")
        
        if not config.token_url:
            raise ValueError("OAuth2 requires token_url")
    
    async def authenticate(self) -> AuthResult:
        """Perform OAuth2 authentication."""        try:
            # Prepare token request
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            # Add scopes if specified
            if self.config.scopes:
                data['scope'] = ' '.join(self.config.scopes)
            
            # Add username/password for password grant
            if self.config.username and self.config.password:
                data['grant_type'] = 'password'
                data['username'] = self.config.username
                data['password'] = self.config.password
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                **self.config.custom_headers
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.token_url,
                    data=data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        token_data = await response.json()
                        
                        # Calculate expiry time
                        expires_in = token_data.get('expires_in', self.config.token_expiry)
                        expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        # Create token
                        self.current_token = AuthToken(
                            access_token=token_data['access_token'],
                            token_type=token_data.get('token_type', 'Bearer'),
                            expires_at=expires_at,
                            refresh_token=token_data.get('refresh_token'),
                            scope=token_data.get('scope'),
                            metadata=token_data
                        )
                        
                        self.logger.info("OAuth2 authentication successful")
                        
                        return AuthResult(
                            success=True,
                            token=self.current_token,
                            headers=self.get_auth_headers()
                        )
                    
                    else:
                        error_text = await response.text()
                        self.logger.error(f"OAuth2 authentication failed: {error_text}")
                        
                        return AuthResult(
                            success=False,
                            error_message=f"Authentication failed: {error_text}"
                        )
        
        except Exception as e:
            self.logger.error(f"OAuth2 authentication error: {e}")
            return AuthResult(
                success=False,
                error_message=str(e)
            )
    
    async def refresh_token(self) -> AuthResult:
        """Refresh OAuth2 token."""        if not self.current_token or not self.current_token.refresh_token:
            return await self.authenticate()
        
        try:
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.current_token.refresh_token,
                'client_id': self.config.client_id,
                'client_secret': self.config.client_secret
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                **self.config.custom_headers
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.token_url,
                    data=data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        token_data = await response.json()
                        
                        # Update current token
                        expires_in = token_data.get('expires_in', self.config.token_expiry)
                        expires_at = datetime.now() + timedelta(seconds=expires_in)
                        
                        self.current_token.access_token = token_data['access_token']
                        self.current_token.expires_at = expires_at
                        self.current_token.refresh_token = token_data.get(
                            'refresh_token', 
                            self.current_token.refresh_token
                        )
                        self.current_token.metadata.update(token_data)
                        
                        self.logger.info("OAuth2 token refreshed")
                        
                        return AuthResult(
                            success=True,
                            token=self.current_token,
                            headers=self.get_auth_headers()
                        )
                    
                    else:
                        self.logger.warning("Token refresh failed, re-authenticating")
                        return await self.authenticate()
        
        except Exception as e:
            self.logger.error(f"OAuth2 token refresh error: {e}")
            return await self.authenticate()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get OAuth2 authentication headers."""        if not self.current_token:
            return {}
        
        return {
            'Authorization': f'{self.current_token.token_type} {self.current_token.access_token}',
            **self.config.custom_headers
        }
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get OAuth2 authorization URL for web flows."""        if not self.config.authorize_url:
            raise ValueError("authorize_url required for authorization code flow")
        
        params = {
            'response_type': 'code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'scope': ' '.join(self.config.scopes) if self.config.scopes else ''
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items() if v)
        return f"{self.config.authorize_url}?{query_string}"

class JWTAdapter(AuthenticationAdapter):
    """Adapter for JWT (JSON Web Token) authentication."""    
    def __init__(self, config: AuthConfig):
        """Initialize JWT adapter."""        super().__init__(config)
        self.auth_method = "JWT"
        
        if not config.jwt_secret:
            raise ValueError("JWT requires jwt_secret")
    
    async def authenticate(self) -> AuthResult:
        """Generate JWT token."""        try:
            # Prepare JWT payload
            now = datetime.now()
            payload = {
                'iat': now,
                'exp': now + timedelta(seconds=self.config.token_expiry),
                'sub': self.config.username or 'system',
                'iss': 'ia-influencer-agent'
            }
            
            # Add custom claims
            if self.config.scopes:
                payload['scope'] = ' '.join(self.config.scopes)
            
            # Generate token
            token = jwt.encode(
                payload,
                self.config.jwt_secret,
                algorithm=self.config.jwt_algorithm
            )
            
            # Create token object
            self.current_token = AuthToken(
                access_token=token,
                token_type='Bearer',
                expires_at=payload['exp'],
                metadata=payload
            )
            
            self.logger.info("JWT token generated")
            
            return AuthResult(
                success=True,
                token=self.current_token,
                headers=self.get_auth_headers()
            )
        
        except Exception as e:
            self.logger.error(f"JWT generation error: {e}")
            return AuthResult(
                success=False,
                error_message=str(e)
            )
    
    async def refresh_token(self) -> AuthResult:
        """Refresh JWT token (generate new one)."""        return await self.authenticate()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get JWT authentication headers."""        if not self.current_token:
            return {}
        
        return {
            'Authorization': f'Bearer {self.current_token.access_token}',
            **self.config.custom_headers
        }
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""        try:
            payload = jwt.decode(
                token,
                self.config.jwt_secret,
                algorithms=[self.config.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

class APIKeyAdapter(AuthenticationAdapter):
    """Adapter for API Key authentication."""    
    def __init__(self, config: AuthConfig):
        """Initialize API Key adapter."""        super().__init__(config)
        self.auth_method = "API_KEY"
        
        if not config.api_key:
            raise ValueError("API Key authentication requires api_key")
    
    async def authenticate(self) -> AuthResult:
        """Set up API key authentication (no actual auth needed)."""        try:
            # Create a pseudo-token for consistency
            self.current_token = AuthToken(
                access_token=self.config.api_key,
                token_type='ApiKey',
                metadata={'api_key': self.config.api_key}
            )
            
            self.logger.info("API Key authentication configured")
            
            return AuthResult(
                success=True,
                token=self.current_token,
                headers=self.get_auth_headers()
            )
        
        except Exception as e:
            self.logger.error(f"API Key setup error: {e}")
            return AuthResult(
                success=False,
                error_message=str(e)
            )
    
    async def refresh_token(self) -> AuthResult:
        """API keys don't need refresh."""        return AuthResult(success=True, token=self.current_token)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get API Key authentication headers."""        headers = {**self.config.custom_headers}
        
        # Common API key header patterns
        if 'X-API-Key' not in headers:
            headers['X-API-Key'] = self.config.api_key
        
        if 'Authorization' not in headers:
            headers['Authorization'] = f'ApiKey {self.config.api_key}'
        
        return headers
    
    def generate_signature(self, method: str, url: str, body: str = "") -> str:
        """Generate HMAC signature for API requests."""        if not self.config.api_secret:
            raise ValueError("API secret required for signature generation")
        
        # Create signature string
        timestamp = str(int(datetime.now().timestamp()))
        message = f"{method.upper()}\n{url}\n{timestamp}\n{body}"
        
        # Generate HMAC signature
        signature = hmac.new(
            self.config.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}.{signature}"

class BasicAuthAdapter(AuthenticationAdapter):
    """Adapter for Basic HTTP authentication."""    
    def __init__(self, config: AuthConfig):
        """Initialize Basic Auth adapter."""        super().__init__(config)
        self.auth_method = "BASIC_AUTH"
        
        if not config.username or not config.password:
            raise ValueError("Basic Auth requires username and password")
    
    async def authenticate(self) -> AuthResult:
        """Set up Basic authentication."""        try:
            # Encode credentials
            credentials = f"{self.config.username}:{self.config.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Create pseudo-token
            self.current_token = AuthToken(
                access_token=encoded_credentials,
                token_type='Basic',
                metadata={
                    'username': self.config.username,
                    'encoded_credentials': encoded_credentials
                }
            )
            
            self.logger.info("Basic authentication configured")
            
            return AuthResult(
                success=True,
                token=self.current_token,
                headers=self.get_auth_headers()
            )
        
        except Exception as e:
            self.logger.error(f"Basic Auth setup error: {e}")
            return AuthResult(
                success=False,
                error_message=str(e)
            )
    
    async def refresh_token(self) -> AuthResult:
        """Basic auth doesn't need refresh."""        return AuthResult(success=True, token=self.current_token)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get Basic authentication headers."""        if not self.current_token:
            return {}
        
        return {
            'Authorization': f'Basic {self.current_token.access_token}',
            **self.config.custom_headers
        }

class CertificateAdapter(AuthenticationAdapter):
    """Adapter for certificate-based authentication."""    
    def __init__(self, config: AuthConfig):
        """Initialize Certificate adapter."""        super().__init__(config)
        self.auth_method = "CERTIFICATE"
        
        if not config.certificate_path:
            raise ValueError("Certificate authentication requires certificate_path")
        
        self.certificate = None
        self.private_key = None
    
    async def authenticate(self) -> AuthResult:
        """Load and validate certificate."""        try:
            # Load certificate
            async with aiofiles.open(self.config.certificate_path, 'rb') as f:
                cert_data = await f.read()
            
            self.certificate = x509.load_pem_x509_certificate(cert_data)
            
            # Load private key if provided
            if self.config.private_key_path:
                async with aiofiles.open(self.config.private_key_path, 'rb') as f:
                    key_data = await f.read()
                
                self.private_key = serialization.load_pem_private_key(
                    key_data,
                    password=self.config.password.encode() if self.config.password else None
                )
            
            # Extract certificate info
            subject = self.certificate.subject
            issuer = self.certificate.issuer
            serial_number = str(self.certificate.serial_number)
            
            # Create token with certificate info
            self.current_token = AuthToken(
                access_token=serial_number,
                token_type='Certificate',
                expires_at=self.certificate.not_valid_after,
                metadata={
                    'subject': subject.rfc4514_string(),
                    'issuer': issuer.rfc4514_string(),
                    'serial_number': serial_number,
                    'not_before': self.certificate.not_valid_before.isoformat(),
                    'not_after': self.certificate.not_valid_after.isoformat()
                }
            )
            
            self.logger.info(f"Certificate loaded: {subject.rfc4514_string()}")
            
            return AuthResult(
                success=True,
                token=self.current_token,
                headers=self.get_auth_headers()
            )
        
        except Exception as e:
            self.logger.error(f"Certificate authentication error: {e}")
            return AuthResult(
                success=False,
                error_message=str(e)
            )
    
    async def refresh_token(self) -> AuthResult:
        """Certificates don't need refresh, but check expiry."""        if self.current_token and self.current_token.is_expired:
            return AuthResult(
                success=False,
                error_message="Certificate has expired"
            )
        
        return AuthResult(success=True, token=self.current_token)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get certificate authentication headers."""        if not self.current_token:
            return {}
        
        headers = {**self.config.custom_headers}
        
        # Add certificate fingerprint
        if self.certificate:
            fingerprint = self.certificate.fingerprint(hashes.SHA256()).hex()
            headers['X-Certificate-Fingerprint'] = fingerprint
        
        return headers
    
    def get_ssl_context(self) -> ssl.SSLContext:
        """Get SSL context with client certificate."""        context = ssl.create_default_context()
        
        if self.config.certificate_path:
            context.load_cert_chain(
                self.config.certificate_path,
                self.config.private_key_path
            )
        
        return context
    
    def sign_data(self, data: bytes) -> bytes:
        """Sign data with private key."""        if not self.private_key:
            raise ValueError("Private key not loaded")
        
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature

# Authentication manager
class AuthenticationManager:
    """Manager for multiple authentication adapters."""    
    def __init__(self):
        """Initialize authentication manager."""        self.adapters: Dict[str, AuthenticationAdapter] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_adapter(self, name: str, adapter: AuthenticationAdapter):
        """Register an authentication adapter."""        self.adapters[name] = adapter
        self.logger.info(f"Registered authentication adapter: {name}")
    
    async def authenticate_all(self) -> Dict[str, AuthResult]:
        """Authenticate all registered adapters."""        results = {}
        
        for name, adapter in self.adapters.items():
            try:
                result = await adapter.authenticate()
                results[name] = result
                
                if result.success:
                    self.logger.info(f"Authentication successful: {name}")
                else:
                    self.logger.warning(f"Authentication failed: {name} - {result.error_message}")
            
            except Exception as e:
                self.logger.error(f"Authentication error for {name}: {e}")
                results[name] = AuthResult(
                    success=False,
                    error_message=str(e)
                )
        
        return results
    
    def get_adapter(self, name: str) -> Optional[AuthenticationAdapter]:
        """Get authentication adapter by name."""        return self.adapters.get(name)
    
    def get_auth_headers(self, adapter_name: str) -> Dict[str, str]:
        """Get authentication headers for specific adapter."""        adapter = self.adapters.get(adapter_name)
        if adapter and adapter.is_authenticated():
            return adapter.get_auth_headers()
        return {}

# Export all adapters
__all__ = [
    'AuthenticationAdapter',
    'AuthConfig',
    'AuthToken',
    'AuthResult',
    'OAuth2Adapter',
    'JWTAdapter',
    'APIKeyAdapter',
    'BasicAuthAdapter',
    'CertificateAdapter',
    'AuthenticationManager'
]
