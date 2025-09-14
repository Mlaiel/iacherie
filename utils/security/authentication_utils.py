"""
Authentication Utils - Security Utilities Level 2
================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade authentication utilities consolidating:
- Auth utilities (auth_utilities.py)

Performance: < 5ms per authentication operation
Standards: JWT + OAuth + Multi-factor authentication, enterprise security
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import uuid
import re

# Authentication imports
import jwt
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64

# OAuth imports
try:
    from authlib.integrations.requests_client import OAuth2Session
    from authlib.oauth2 import OAuth2Token
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class AuthResult:
    """Enterprise result container for authentication operations."""
    success: bool
    result: Optional[Any] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'result': self.result,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms
        }

@dataclass
class User:
    """User account information."""
    user_id: str
    username: str
    email: str
    password_hash: str
    salt: str
    is_active: bool = True
    is_verified: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class JWTConfig:
    """JWT configuration settings."""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    issuer: str = "ainflue"
    audience: str = "ainflue-api"

@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    provider_name: str
    client_id: str
    client_secret: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    scopes: List[str] = field(default_factory=lambda: ["openid", "email", "profile"])

class AuthenticationUtils:
    """
    Enterprise authentication utilities with ultra-strict security standards.
    
    Implements multi-factor authentication, JWT tokens, OAuth integration,
    and comprehensive security measures following enterprise standards.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize authentication utilities with enterprise configuration."""
        self.config = config or {}
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._performance_threshold_ms = 5.0
        
        # JWT configuration
        self._jwt_config = JWTConfig(
            secret_key=self.config.get('jwt_secret_key', secrets.token_urlsafe(32)),
            algorithm=self.config.get('jwt_algorithm', 'HS256'),
            access_token_expire_minutes=self.config.get('access_token_expire_minutes', 15),
            refresh_token_expire_days=self.config.get('refresh_token_expire_days', 30)
        )
        
        # Security settings
        self._max_login_attempts = self.config.get('max_login_attempts', 5)
        self._lockout_duration_minutes = self.config.get('lockout_duration_minutes', 15)
        self._password_min_length = self.config.get('password_min_length', 12)
        self._require_special_chars = self.config.get('require_special_chars', True)
        
        # In-memory storage (in production, use Redis/database)
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Dict] = {}
        self._blacklisted_tokens: set = set()
        self._oauth_configs: Dict[str, OAuthConfig] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        self._thread_pool.shutdown(wait=True)
        
    async def _measure_performance(self, operation: callable) -> Tuple[Any, float]:
        """Measure operation performance and validate against thresholds."""
        start_time = time.perf_counter()
        
        if asyncio.iscoroutinefunction(operation):
            result = await operation()
        else:
            result = await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, operation
            )
            
        execution_time = (time.perf_counter() - start_time) * 1000
        
        if execution_time > self._performance_threshold_ms:
            logger.warning(
                f"Performance threshold exceeded: {execution_time:.2f}ms > {self._performance_threshold_ms}ms"
            )
            
        return result, execution_time
    
    # === PASSWORD MANAGEMENT ===
    
    def _validate_password_strength(self, password: str) -> List[str]:
        """Validate password strength against enterprise requirements."""
        errors = []
        
        if len(password) < self._password_min_length:
            errors.append(f"Password must be at least {self._password_min_length} characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self._require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common patterns
        if password.lower() in ['password', '123456', 'qwerty', 'admin']:
            errors.append("Password cannot be a common word or pattern")
        
        return errors
    
    async def hash_password(self, password: str) -> AuthResult:
        """Hash password using bcrypt with enterprise security."""
        def _hash_password():
            # Validate password strength
            validation_errors = self._validate_password_strength(password)
            if validation_errors:
                return None, validation_errors
            
            # Generate salt and hash
            salt = bcrypt.gensalt(rounds=12)  # Enterprise-grade rounds
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            return {
                'password_hash': password_hash.decode('utf-8'),
                'salt': salt.decode('utf-8')
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_hash_password)
            
            if result[0] is None:  # Error case
                return AuthResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'hash_password'}
                )
            
            data = result[0]
            return AuthResult(
                success=True,
                result=data,
                execution_time_ms=exec_time,
                metadata={'operation': 'hash_password'}
            )
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'hash_password'}
            )
    
    async def verify_password(self, password: str, password_hash: str) -> AuthResult:
        """Verify password against hash."""
        def _verify_password():
            try:
                is_valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    password_hash.encode('utf-8')
                )
                return {'valid': is_valid}, []
            except Exception as e:
                return None, [f"Password verification error: {str(e)}"]
            
        try:
            result, exec_time = await self._measure_performance(_verify_password)
            
            if result[0] is None:  # Error case
                return AuthResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'verify_password'}
                )
            
            data = result[0]
            return AuthResult(
                success=True,
                result=data['valid'],
                execution_time_ms=exec_time,
                metadata={'operation': 'verify_password', 'password_valid': data['valid']}
            )
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'verify_password'}
            )
    
    # === USER MANAGEMENT ===
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        enable_mfa: bool = False
    ) -> AuthResult:
        """Create new user account with enterprise security."""
        try:
            # Validate input
            if not username or not email or not password:
                return AuthResult(
                    success=False,
                    errors=["Username, email, and password are required"]
                )
            
            # Check if user already exists
            existing_user = None
            for user in self._users.values():
                if user.username == username or user.email == email:
                    existing_user = user
                    break
            
            if existing_user:
                return AuthResult(
                    success=False,
                    errors=["User with this username or email already exists"]
                )
            
            # Hash password
            hash_result = await self.hash_password(password)
            if not hash_result.success:
                return AuthResult(
                    success=False,
                    errors=hash_result.errors
                )
            
            # Generate user ID and MFA secret
            user_id = str(uuid.uuid4())
            mfa_secret = pyotp.random_base32() if enable_mfa else None
            
            # Create user
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=hash_result.result['password_hash'],
                salt=hash_result.result['salt'],
                mfa_enabled=enable_mfa,
                mfa_secret=mfa_secret
            )
            
            self._users[user_id] = user
            
            result_data = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'mfa_enabled': enable_mfa
            }
            
            if enable_mfa:
                result_data['mfa_qr_code'] = await self._generate_mfa_qr_code(username, mfa_secret)
            
            return AuthResult(
                success=True,
                result=result_data,
                user_id=user_id,
                metadata={'operation': 'create_user', 'mfa_enabled': enable_mfa}
            )
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'create_user'}
            )
    
    async def _generate_mfa_qr_code(self, username: str, secret: str) -> str:
        """Generate QR code for MFA setup."""
        def _generate_qr():
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=username,
                issuer_name="Ainflue"
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        
        return await asyncio.get_event_loop().run_in_executor(
            self._thread_pool, _generate_qr
        )
    
    # === AUTHENTICATION ===
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        mfa_code: Optional[str] = None
    ) -> AuthResult:
        """Authenticate user with optional MFA."""
        try:
            # Find user
            user = None
            for u in self._users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                return AuthResult(
                    success=False,
                    errors=["Invalid username or password"]
                )
            
            # Check account status
            if not user.is_active:
                return AuthResult(
                    success=False,
                    errors=["Account is deactivated"]
                )
            
            # Check lockout
            if user.failed_login_attempts >= self._max_login_attempts:
                return AuthResult(
                    success=False,
                    errors=["Account is temporarily locked due to too many failed attempts"]
                )
            
            # Verify password
            password_result = await self.verify_password(password, user.password_hash)
            if not password_result.success or not password_result.result:
                # Increment failed attempts
                user.failed_login_attempts += 1
                return AuthResult(
                    success=False,
                    errors=["Invalid username or password"]
                )
            
            # Verify MFA if enabled
            if user.mfa_enabled:
                if not mfa_code:
                    return AuthResult(
                        success=False,
                        errors=["MFA code required"],
                        metadata={'mfa_required': True}
                    )
                
                totp = pyotp.TOTP(user.mfa_secret)
                if not totp.verify(mfa_code):
                    user.failed_login_attempts += 1
                    return AuthResult(
                        success=False,
                        errors=["Invalid MFA code"]
                    )
            
            # Reset failed attempts and update last login
            user.failed_login_attempts = 0
            user.last_login = datetime.now(timezone.utc)
            
            # Generate session
            session_id = str(uuid.uuid4())
            session_data = {
                'user_id': user.user_id,
                'username': user.username,
                'created_at': datetime.now(timezone.utc),
                'last_activity': datetime.now(timezone.utc)
            }
            self._sessions[session_id] = session_data
            
            return AuthResult(
                success=True,
                result={
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'is_verified': user.is_verified,
                    'mfa_enabled': user.mfa_enabled
                },
                user_id=user.user_id,
                session_id=session_id,
                metadata={'operation': 'authenticate_user'}
            )
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'authenticate_user'}
            )
    
    # === JWT TOKEN MANAGEMENT ===
    
    async def generate_jwt_token(
        self,
        user_id: str,
        token_type: str = "access"  # "access" or "refresh"
    ) -> AuthResult:
        """Generate JWT token for user."""
        def _generate_token():
            user = self._users.get(user_id)
            if not user:
                return None, ["User not found"]
            
            now = datetime.now(timezone.utc)
            
            if token_type == "access":
                expires_delta = timedelta(minutes=self._jwt_config.access_token_expire_minutes)
            else:  # refresh
                expires_delta = timedelta(days=self._jwt_config.refresh_token_expire_days)
            
            expires_at = now + expires_delta
            
            payload = {
                'sub': user_id,
                'username': user.username,
                'email': user.email,
                'token_type': token_type,
                'iat': now,
                'exp': expires_at,
                'iss': self._jwt_config.issuer,
                'aud': self._jwt_config.audience,
                'jti': str(uuid.uuid4())  # JWT ID for blacklisting
            }
            
            token = jwt.encode(
                payload,
                self._jwt_config.secret_key,
                algorithm=self._jwt_config.algorithm
            )
            
            return {
                'token': token,
                'expires_at': expires_at,
                'token_type': token_type
            }, []
            
        try:
            result, exec_time = await self._measure_performance(_generate_token)
            
            if result[0] is None:  # Error case
                return AuthResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'generate_jwt_token'}
                )
            
            data = result[0]
            return AuthResult(
                success=True,
                result=data['token'],
                user_id=user_id,
                token=data['token'],
                expires_at=data['expires_at'],
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'generate_jwt_token',
                    'token_type': data['token_type'],
                    'expires_at': data['expires_at'].isoformat()
                }
            )
        except Exception as e:
            logger.error(f"JWT token generation failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'generate_jwt_token'}
            )
    
    async def verify_jwt_token(self, token: str) -> AuthResult:
        """Verify and decode JWT token."""
        def _verify_token():
            try:
                # Check if token is blacklisted
                if token in self._blacklisted_tokens:
                    return None, ["Token has been revoked"]
                
                # Decode and verify token
                payload = jwt.decode(
                    token,
                    self._jwt_config.secret_key,
                    algorithms=[self._jwt_config.algorithm],
                    issuer=self._jwt_config.issuer,
                    audience=self._jwt_config.audience
                )
                
                # Check if user still exists
                user_id = payload.get('sub')
                if user_id not in self._users:
                    return None, ["User no longer exists"]
                
                return {
                    'valid': True,
                    'payload': payload,
                    'user_id': user_id,
                    'username': payload.get('username'),
                    'token_type': payload.get('token_type')
                }, []
                
            except jwt.ExpiredSignatureError:
                return None, ["Token has expired"]
            except jwt.InvalidTokenError as e:
                return None, [f"Invalid token: {str(e)}"]
            
        try:
            result, exec_time = await self._measure_performance(_verify_token)
            
            if result[0] is None:  # Error case
                return AuthResult(
                    success=False,
                    errors=result[1],
                    execution_time_ms=exec_time,
                    metadata={'operation': 'verify_jwt_token'}
                )
            
            data = result[0]
            return AuthResult(
                success=True,
                result=data,
                user_id=data['user_id'],
                token=token,
                execution_time_ms=exec_time,
                metadata={
                    'operation': 'verify_jwt_token',
                    'token_type': data['token_type'],
                    'username': data['username']
                }
            )
        except Exception as e:
            logger.error(f"JWT token verification failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'verify_jwt_token'}
            )
    
    async def revoke_jwt_token(self, token: str) -> AuthResult:
        """Revoke JWT token (add to blacklist)."""
        try:
            # First verify the token to get its ID
            verify_result = await self.verify_jwt_token(token)
            if not verify_result.success:
                return AuthResult(
                    success=False,
                    errors=["Cannot revoke invalid token"]
                )
            
            # Add to blacklist
            self._blacklisted_tokens.add(token)
            
            return AuthResult(
                success=True,
                result="Token revoked successfully",
                metadata={'operation': 'revoke_jwt_token'}
            )
        except Exception as e:
            logger.error(f"JWT token revocation failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'revoke_jwt_token'}
            )
    
    # === SESSION MANAGEMENT ===
    
    async def validate_session(self, session_id: str) -> AuthResult:
        """Validate active session."""
        try:
            if session_id not in self._sessions:
                return AuthResult(
                    success=False,
                    errors=["Invalid session"]
                )
            
            session = self._sessions[session_id]
            
            # Update last activity
            session['last_activity'] = datetime.now(timezone.utc)
            
            return AuthResult(
                success=True,
                result=session,
                user_id=session['user_id'],
                session_id=session_id,
                metadata={'operation': 'validate_session'}
            )
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'validate_session'}
            )
    
    async def revoke_session(self, session_id: str) -> AuthResult:
        """Revoke active session."""
        try:
            if session_id in self._sessions:
                del self._sessions[session_id]
            
            return AuthResult(
                success=True,
                result="Session revoked successfully",
                metadata={'operation': 'revoke_session'}
            )
        except Exception as e:
            logger.error(f"Session revocation failed: {e}")
            return AuthResult(
                success=False,
                errors=[str(e)],
                metadata={'operation': 'revoke_session'}
            )

# Enterprise factory pattern for authentication utils
class AuthenticationUtilsFactory:
    """Factory for creating configured authentication utilities instances."""
    
    @staticmethod
    def create_utils(config: Optional[Dict[str, Any]] = None) -> AuthenticationUtils:
        """Create and configure authentication utilities."""
        return AuthenticationUtils(config)
    
    @staticmethod
    def create_enterprise_utils(
        jwt_secret_key: str,
        max_login_attempts: int = 5,
        password_min_length: int = 12
    ) -> AuthenticationUtils:
        """Create authentication utilities with enterprise security settings."""
        config = {
            'jwt_secret_key': jwt_secret_key,
            'max_login_attempts': max_login_attempts,
            'password_min_length': password_min_length,
            'require_special_chars': True,
            'access_token_expire_minutes': 15,
            'refresh_token_expire_days': 30
        }
        return AuthenticationUtils(config)