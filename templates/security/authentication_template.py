"""{{auth_name}} Authentication Service Template for Ainflue Platform
{{auth_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import hashlib
import secrets
import base64
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum

import bcrypt
import jwt
from pydantic import BaseModel, Field, validator, EmailStr

from core.config import get_settings
from utils.exceptions import AuthenticationError, AuthorizationError, SecurityError
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthMethod(Enum):
    """Authentication methods"""
    PASSWORD = "password"
    MFA = "mfa" 
    SSO = "sso"
    API_KEY = "api_key"
    BIOMETRIC = "biometric"
    DEVICE_TOKEN = "device_token"


class TokenType(Enum):
    """Token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFY = "verify"
    API = "api"
    DEVICE = "device"


class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthRequest(BaseModel):
    """Authentication request"""
    identifier: str = Field(..., description="Username, email, or phone")
    credential: str = Field(..., description="Password, token, or other credential")
    auth_method: AuthMethod = Field(default=AuthMethod.PASSWORD, description="Authentication method")
    device_id: Optional[str] = Field(default=None, description="Device identifier")
    ip_address: Optional[str] = Field(default=None, description="Client IP address")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    mfa_code: Optional[str] = Field(default=None, description="MFA verification code")
    remember_device: bool = Field(default=False, description="Remember device for future logins")
    
    @validator('identifier')
    def validate_identifier(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Identifier must be at least 3 characters')
        return v.strip().lower()


class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool = Field(..., description="Authentication success status")
    user_id: Optional[str] = Field(default=None, description="Authenticated user ID")
    access_token: Optional[str] = Field(default=None, description="JWT access token")
    refresh_token: Optional[str] = Field(default=None, description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: Optional[int] = Field(default=None, description="Token expiration in seconds")
    mfa_required: bool = Field(default=False, description="MFA verification required")
    mfa_methods: List[str] = Field(default_factory=list, description="Available MFA methods")
    device_trusted: bool = Field(default=False, description="Device trust status")
    security_level: SecurityLevel = Field(default=SecurityLevel.MEDIUM, description="Session security level")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{auth_name}}AuthService:
    """{{auth_description}}
    
    Comprehensive authentication service providing:
    - Multi-factor authentication (MFA/2FA)
    - Password-based authentication with strong policies
    - JWT token management (access/refresh)
    - Device tracking and trust
    - Account lockout protection
    - Session management
    - API key authentication
    - SSO integration support
    - Biometric authentication
    - Security audit logging
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_collector = SecurityMetricsCollector()
        self.secret_key = settings.SECRET_KEY
        
    async def authenticate(self, request: AuthRequest) -> AuthResponse:
        """Authenticate user with various methods"""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Authentication attempt for {request.identifier} using {request.auth_method.value}")
            
            # Route to specific authentication method
            if request.auth_method == AuthMethod.PASSWORD:
                auth_result = await self._authenticate_password(request)
            elif request.auth_method == AuthMethod.API_KEY:
                auth_result = await self._authenticate_api_key(request)
            elif request.auth_method == AuthMethod.MFA:
                auth_result = await self._authenticate_mfa(request)
            elif request.auth_method == AuthMethod.SSO:
                auth_result = await self._authenticate_sso(request)
            elif request.auth_method == AuthMethod.BIOMETRIC:
                auth_result = await self._authenticate_biometric(request)
            elif request.auth_method == AuthMethod.DEVICE_TOKEN:
                auth_result = await self._authenticate_device_token(request)
            else:
                raise AuthenticationError(f"Unsupported authentication method: {request.auth_method}")
            
            if auth_result.success:
                # Generate tokens if authentication is complete
                if not auth_result.mfa_required:
                    tokens = await self._generate_tokens(auth_result.user_id, request)
                    auth_result.access_token = tokens["access_token"]
                    auth_result.refresh_token = tokens["refresh_token"]
                    auth_result.expires_in = 3600  # 1 hour
                    
                    # Get user permissions
                    auth_result.permissions = await self._get_user_permissions(auth_result.user_id)
                
                await self._record_security_event("login_success", request.identifier, request.ip_address)
            else:
                await self._record_security_event("login_failed", request.identifier, request.ip_address)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_auth_metrics(
                method=request.auth_method.value,
                success=auth_result.success,
                execution_time=execution_time,
                mfa_required=auth_result.mfa_required
            )
            
            return auth_result
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="Authentication failed due to internal error",
                security_level=SecurityLevel.CRITICAL
            )
    
    async def _authenticate_password(self, request: AuthRequest) -> AuthResponse:
        """Authenticate using username/password"""
        try:
            # Get user by identifier (email, username, phone)
            user = await self._get_user_by_identifier(request.identifier)
            if not user:
                return AuthResponse(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # Verify password
            if not self._verify_password(request.credential, user.password_hash):
                return AuthResponse(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # Check account status
            if not user.is_active:
                return AuthResponse(
                    success=False,
                    error_message="Account is disabled"
                )
            
            return AuthResponse(
                success=True,
                user_id=str(user.id),
                security_level=SecurityLevel.MEDIUM
            )
            
        except Exception as e:
            logger.error(f"Password authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="Authentication failed"
            )
    
    async def _authenticate_mfa(self, request: AuthRequest) -> AuthResponse:
        """Authenticate using MFA code"""
        if not request.mfa_code:
            return AuthResponse(
                success=False,
                error_message="MFA code is required"
            )
        
        try:
            # Get user
            user = await self._get_user_by_identifier(request.identifier)
            if not user:
                return AuthResponse(
                    success=False,
                    error_message="Invalid user"
                )
            
            # Verify MFA code
            if await self._verify_mfa_code(user.id, request.mfa_code):
                return AuthResponse(
                    success=True,
                    user_id=str(user.id),
                    security_level=SecurityLevel.HIGH
                )
            else:
                return AuthResponse(
                    success=False,
                    error_message="Invalid MFA code"
                )
                
        except Exception as e:
            logger.error(f"MFA authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="MFA authentication failed"
            )
    
    async def _authenticate_api_key(self, request: AuthRequest) -> AuthResponse:
        """Authenticate using API key"""
        try:
            # Validate API key format and decrypt
            api_key_data = await self._validate_api_key(request.credential)
            if not api_key_data:
                return AuthResponse(
                    success=False,
                    error_message="Invalid API key"
                )
            
            return AuthResponse(
                success=True,
                user_id=api_key_data['user_id'],
                security_level=SecurityLevel.MEDIUM,
                permissions=api_key_data.get('permissions', [])
            )
            
        except Exception as e:
            logger.error(f"API key authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="API key authentication failed"
            )
    
    async def _authenticate_sso(self, request: AuthRequest) -> AuthResponse:
        """Authenticate using SSO token"""
        try:
            # Validate SSO token with provider
            sso_data = await self._validate_sso_token(request.credential)
            if not sso_data:
                return AuthResponse(
                    success=False,
                    error_message="Invalid SSO token"
                )
            
            # Get or create user from SSO data
            user_id = await self._get_or_create_sso_user(sso_data)
            
            return AuthResponse(
                success=True,
                user_id=user_id,
                security_level=SecurityLevel.HIGH
            )
            
        except Exception as e:
            logger.error(f"SSO authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="SSO authentication failed"
            )
    
    async def _authenticate_biometric(self, request: AuthRequest) -> AuthResponse:
        """Authenticate using biometric data"""
        try:
            # Validate biometric signature
            biometric_valid = await self._validate_biometric(request.identifier, request.credential)
            if not biometric_valid:
                return AuthResponse(
                    success=False,
                    error_message="Biometric authentication failed"
                )
            
            user = await self._get_user_by_identifier(request.identifier)
            if not user:
                return AuthResponse(
                    success=False,
                    error_message="User not found"
                )
            
            return AuthResponse(
                success=True,
                user_id=str(user.id),
                security_level=SecurityLevel.HIGH
            )
            
        except Exception as e:
            logger.error(f"Biometric authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="Biometric authentication failed"
            )
    
    async def _authenticate_device_token(self, request: AuthRequest) -> AuthResponse:
        """Authenticate using device token"""
        try:
            # Validate device token
            device_data = await self._validate_device_token(request.credential, request.device_id)
            if not device_data:
                return AuthResponse(
                    success=False,
                    error_message="Invalid device token"
                )
            
            return AuthResponse(
                success=True,
                user_id=device_data['user_id'],
                security_level=SecurityLevel.MEDIUM,
                device_trusted=True
            )
            
        except Exception as e:
            logger.error(f"Device token authentication failed: {str(e)}")
            return AuthResponse(
                success=False,
                error_message="Device token authentication failed"
            )
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    async def _generate_tokens(self, user_id: str, request: Optional[AuthRequest]) -> Dict[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            'user_id': user_id,
            'type': TokenType.ACCESS.value,
            'iat': now.timestamp(),
            'exp': (now + timedelta(seconds=3600)).timestamp(),
            'jti': secrets.token_hex(16)
        }
        
        if request:
            access_payload.update({
                'device_id': request.device_id,
                'ip_address': request.ip_address
            })
        
        access_token = jwt.encode(
            access_payload,
            self.secret_key,
            algorithm="HS256"
        )
        
        # Refresh token
        refresh_payload = {
            'user_id': user_id,
            'type': TokenType.REFRESH.value,
            'iat': now.timestamp(),
            'exp': (now + timedelta(seconds=86400)).timestamp(),
            'jti': secrets.token_hex(16)
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            self.secret_key,
            algorithm="HS256"
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    async def validate_token(self, token: str, token_type: TokenType = TokenType.ACCESS) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            
            # Check token type
            if payload.get('type') != token_type.value:
                return None
            
            # Check expiration
            if payload.get('exp', 0) < datetime.utcnow().timestamp():
                return None
            
            return payload
            
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None
    
    # Placeholder methods that would be implemented with actual database operations
    async def _get_user_by_identifier(self, identifier: str): 
        """Get user by identifier (email, username, phone)"""
        pass
    
    async def _verify_mfa_code(self, user_id: str, code: str) -> bool: 
        """Verify MFA code"""
        return True
    
    async def _get_user_permissions(self, user_id: str) -> List[str]: 
        """Get user permissions"""
        return []
    
    async def _validate_api_key(self, api_key: str) -> Optional[Dict]: 
        """Validate API key"""
        return None
    
    async def _validate_sso_token(self, token: str) -> Optional[Dict]: 
        """Validate SSO token"""
        return None
    
    async def _get_or_create_sso_user(self, sso_data: Dict) -> str: 
        """Get or create user from SSO data"""
        return ""
    
    async def _validate_biometric(self, identifier: str, credential: str) -> bool: 
        """Validate biometric data"""
        return False
    
    async def _validate_device_token(self, token: str, device_id: str) -> Optional[Dict]: 
        """Validate device token"""
        return None
    
    async def _record_security_event(self, event_type: str, identifier: str, ip_address: Optional[str]): 
        """Record security event"""
        pass