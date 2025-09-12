"""{{middleware_name}} JWT Middleware Template for Ainflue Platform
{{middleware_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Backend Senior + Security Expert Role: Enterprise JWT middleware with advanced security features
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta, timezone
from uuid import UUID
from enum import Enum
import base64
import hmac
import hashlib

from fastapi import Request, Response, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError,
    InvalidSignatureError,
    InvalidKeyError,
    InvalidIssuerError,
    InvalidAudienceError
)
import redis.asyncio as redis
from pydantic import BaseModel, Field

from core.config import get_settings
from core.database import get_session
from utils.exceptions import SecurityError, AuthenticationError
from utils.cache import CacheManager

logger = logging.getLogger(__name__)
settings = get_settings()


class JWTError(SecurityError):
    """JWT middleware specific error"""
    pass


class TokenType(str, Enum):
    """JWT token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    API_KEY = "api_key"


class Algorithm(str, Enum):
    """JWT signing algorithms"""
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"


class JWTConfig(BaseModel):
    """JWT configuration"""
    secret_key: str
    algorithm: Algorithm = Algorithm.HS256
    access_token_expire: int = 3600  # 1 hour
    refresh_token_expire: int = 604800  # 7 days
    issuer: Optional[str] = None
    audience: Optional[str] = None
    
    # Security options
    verify_signature: bool = True
    verify_expiration: bool = True
    verify_issuer: bool = True
    verify_audience: bool = True
    require_issued_at: bool = True
    require_jwt_id: bool = False
    
    # Token storage
    use_redis_blacklist: bool = True
    redis_prefix: str = "jwt"
    
    # Rate limiting
    max_tokens_per_user: int = 10
    token_refresh_window: int = 300  # 5 minutes
    
    # Additional security
    bind_to_ip: bool = False
    bind_to_user_agent: bool = False
    rotate_refresh_token: bool = True


class TokenClaims(BaseModel):
    """JWT token claims"""
    user_id: UUID
    username: str
    email: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    token_type: TokenType = TokenType.ACCESS
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    tenant_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    
    # Standard JWT claims
    iss: Optional[str] = None  # Issuer
    aud: Optional[str] = None  # Audience
    exp: Optional[int] = None  # Expiration time
    nbf: Optional[int] = None  # Not before
    iat: Optional[int] = None  # Issued at
    jti: Optional[str] = None  # JWT ID
    
    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: int(v.timestamp())
        }


class JWTTokenManager:
    """JWT token management utilities"""
    
    def __init__(self, config: JWTConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis = redis_client
    
    def create_token(
        self,
        claims: TokenClaims,
        token_type: TokenType = TokenType.ACCESS,
        custom_expiry: Optional[int] = None
    ) -> str:
        """Create JWT token"""
        try:
            # Set token type
            claims.token_type = token_type
            
            # Set standard claims
            now = int(time.time())
            claims.iat = now
            
            if self.config.issuer:
                claims.iss = self.config.issuer
            
            if self.config.audience:
                claims.aud = self.config.audience
            
            # Set expiration
            if custom_expiry:
                claims.exp = now + custom_expiry
            elif token_type == TokenType.ACCESS:
                claims.exp = now + self.config.access_token_expire
            elif token_type == TokenType.REFRESH:
                claims.exp = now + self.config.refresh_token_expire
            else:
                claims.exp = now + self.config.access_token_expire
            
            # Generate JWT ID if required
            if self.config.require_jwt_id:
                claims.jti = self._generate_jti()
            
            # Convert to dict
            payload = claims.dict(exclude_none=True)
            
            # Convert UUID objects to strings
            for key, value in payload.items():
                if isinstance(value, UUID):
                    payload[key] = str(value)
            
            # Create token
            token = jwt.encode(
                payload,
                self.config.secret_key,
                algorithm=self.config.algorithm.value
            )
            
            logger.debug(f"Created {token_type.value} token for user {claims.user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise JWTError(f"Token creation failed: {str(e)}")
    
    def verify_token(
        self,
        token: str,
        token_type: Optional[TokenType] = None,
        verify_blacklist: bool = True
    ) -> TokenClaims:
        """Verify and decode JWT token"""
        try:
            # Check blacklist first
            if verify_blacklist and self.config.use_redis_blacklist:
                if asyncio.iscoroutinefunction(self._is_token_blacklisted):
                    # Handle async call appropriately
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context, but this is a sync function
                        # This needs to be handled by the caller
                        pass
                    else:
                        is_blacklisted = loop.run_until_complete(self._is_token_blacklisted(token))
                        if is_blacklisted:
                            raise JWTError("Token is blacklisted")
            
            # Decode token
            options = {
                'verify_signature': self.config.verify_signature,
                'verify_exp': self.config.verify_expiration,
                'verify_iss': self.config.verify_issuer,
                'verify_aud': self.config.verify_audience,
                'require_iat': self.config.require_issued_at,
                'require_jti': self.config.require_jwt_id
            }
            
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm.value],
                issuer=self.config.issuer,
                audience=self.config.audience,
                options=options
            )
            
            # Convert to TokenClaims
            claims = TokenClaims(**payload)
            
            # Verify token type if specified
            if token_type and claims.token_type != token_type:
                raise JWTError(f"Invalid token type: expected {token_type}, got {claims.token_type}")
            
            logger.debug(f"Verified {claims.token_type.value} token for user {claims.user_id}")
            return claims
            
        except ExpiredSignatureError:
            raise JWTError("Token has expired")
        except InvalidSignatureError:
            raise JWTError("Invalid token signature")
        except InvalidKeyError:
            raise JWTError("Invalid token key")
        except InvalidIssuerError:
            raise JWTError("Invalid token issuer")
        except InvalidAudienceError:
            raise JWTError("Invalid token audience")
        except InvalidTokenError as e:
            raise JWTError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise JWTError(f"Token verification failed: {str(e)}")
    
    async def blacklist_token(self, token: str, expiry: Optional[int] = None) -> bool:
        """Add token to blacklist"""
        try:
            if not self.redis:
                logger.warning("Redis not available for token blacklisting")
                return False
            
            # Extract token ID or use token hash
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                token_id = payload.get('jti') or hashlib.sha256(token.encode()).hexdigest()
            except:
                token_id = hashlib.sha256(token.encode()).hexdigest()
            
            # Set expiry to token expiration or default
            if not expiry:
                try:
                    payload = jwt.decode(token, options={"verify_signature": False})
                    expiry = payload.get('exp', int(time.time()) + 3600)
                except:
                    expiry = int(time.time()) + 3600
            
            # Add to blacklist
            key = f"{self.config.redis_prefix}:blacklist:{token_id}"
            ttl = max(0, expiry - int(time.time()))
            
            await self.redis.setex(key, ttl, "blacklisted")
            
            logger.info(f"Token blacklisted: {token_id}")
            return True
            
        except Exception as e:
            logger.error(f"Token blacklisting failed: {e}")
            return False
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            if not self.redis:
                return False
            
            # Extract token ID
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                token_id = payload.get('jti') or hashlib.sha256(token.encode()).hexdigest()
            except:
                token_id = hashlib.sha256(token.encode()).hexdigest()
            
            key = f"{self.config.redis_prefix}:blacklist:{token_id}"
            result = await self.redis.exists(key)
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Blacklist check failed: {e}")
            return False
    
    async def refresh_token(
        self,
        refresh_token: str,
        new_claims: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            claims = self.verify_token(refresh_token, TokenType.REFRESH)
            
            # Check refresh window
            if self._is_refresh_too_frequent(claims.user_id):
                raise JWTError("Token refresh too frequent")
            
            # Update claims if provided
            if new_claims:
                for key, value in new_claims.items():
                    if hasattr(claims, key):
                        setattr(claims, key, value)
            
            # Create new access token
            new_access_token = self.create_token(claims, TokenType.ACCESS)
            
            # Create new refresh token if configured
            if self.config.rotate_refresh_token:
                # Blacklist old refresh token
                await self.blacklist_token(refresh_token)
                
                # Create new refresh token
                new_refresh_token = self.create_token(claims, TokenType.REFRESH)
            else:
                new_refresh_token = refresh_token
            
            # Record refresh
            await self._record_token_refresh(claims.user_id)
            
            return new_access_token, new_refresh_token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise JWTError(f"Token refresh failed: {str(e)}")
    
    def _generate_jti(self) -> str:
        """Generate JWT ID"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _is_refresh_too_frequent(self, user_id: UUID) -> bool:
        """Check if refresh is too frequent"""
        # This would typically check Redis for recent refresh attempts
        # Placeholder implementation
        return False
    
    async def _record_token_refresh(self, user_id: UUID):
        """Record token refresh event"""
        try:
            if self.redis:
                key = f"{self.config.redis_prefix}:refresh:{user_id}"
                await self.redis.setex(key, self.config.token_refresh_window, int(time.time()))
        except Exception as e:
            logger.error(f"Failed to record token refresh: {e}")


class {{middleware_name}}JWTMiddleware(BaseHTTPMiddleware):
    """{{middleware_description}}
    
    Enterprise JWT middleware providing:
    - Automatic token verification
    - Role-based access control
    - Token blacklisting support
    - Rate limiting and security checks
    - Request context injection
    - Comprehensive audit logging
    - IP and User-Agent binding
    - Multi-tenant support
    """
    
    def __init__(
        self,
        app,
        config: JWTConfig,
        redis_client: Optional[redis.Redis] = None,
        exempt_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.config = config
        self.token_manager = JWTTokenManager(config, redis_client)
        self.exempt_paths = exempt_paths or []
        
        # Add default exempt paths
        self.exempt_paths.extend([
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/register",
            "/auth/refresh"
        ])
    
    async def dispatch(self, request: Request, call_next):
        """Process request with JWT authentication"""
        try:
            # Check if path is exempt
            if self._is_path_exempt(request.url.path):
                return await call_next(request)
            
            # Extract and verify token
            try:
                token = self._extract_token(request)
                if not token:
                    return self._create_unauthorized_response("Missing authentication token")
                
                claims = await self._verify_token_async(token)
                
                # Verify IP binding if configured
                if self.config.bind_to_ip and claims.ip_address:
                    client_ip = self._get_client_ip(request)
                    if client_ip != claims.ip_address:
                        logger.warning(f"IP mismatch for user {claims.user_id}: {client_ip} vs {claims.ip_address}")
                        return self._create_unauthorized_response("Token IP mismatch")
                
                # Verify User-Agent binding if configured
                if self.config.bind_to_user_agent and claims.user_agent:
                    user_agent = request.headers.get("user-agent", "")
                    if user_agent != claims.user_agent:
                        logger.warning(f"User-Agent mismatch for user {claims.user_id}")
                        return self._create_unauthorized_response("Token User-Agent mismatch")
                
                # Inject claims into request state
                request.state.user = claims
                request.state.user_id = claims.user_id
                request.state.roles = claims.roles
                request.state.permissions = claims.permissions
                request.state.tenant_id = claims.tenant_id
                request.state.workspace_id = claims.workspace_id
                
                # Add security headers
                response = await call_next(request)
                self._add_security_headers(response)
                
                return response
                
            except JWTError as e:
                logger.warning(f"JWT verification failed: {e}")
                return self._create_unauthorized_response(str(e))
            
        except Exception as e:
            logger.error(f"JWT middleware error: {e}")
            return self._create_error_response("Authentication service error")
    
    def _is_path_exempt(self, path: str) -> bool:
        """Check if path is exempt from authentication"""
        return any(path.startswith(exempt_path) for exempt_path in self.exempt_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request"""
        # Try Authorization header first
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        
        # Try query parameter
        token = request.query_params.get("token")
        if token:
            return token
        
        # Try cookie
        token = request.cookies.get("access_token")
        if token:
            return token
        
        return None
    
    async def _verify_token_async(self, token: str) -> TokenClaims:
        """Asynchronously verify token"""
        try:
            # Check blacklist first
            if self.config.use_redis_blacklist and self.token_manager.redis:
                is_blacklisted = await self.token_manager._is_token_blacklisted(token)
                if is_blacklisted:
                    raise JWTError("Token is blacklisted")
            
            # Verify token (this is synchronous)
            claims = self.token_manager.verify_token(token, verify_blacklist=False)
            return claims
            
        except Exception as e:
            raise JWTError(str(e))
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to client address
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return "unknown"
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    def _create_unauthorized_response(self, message: str) -> JSONResponse:
        """Create unauthorized response"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "message": message,
                "code": "AUTH_ERROR"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    def _create_error_response(self, message: str) -> JSONResponse:
        """Create error response"""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": message,
                "code": "MIDDLEWARE_ERROR"
            }
        )


# FastAPI dependencies and utilities

class JWTBearer(HTTPBearer):
    """Custom JWT Bearer authentication"""
    
    def __init__(
        self,
        token_manager: JWTTokenManager,
        required_roles: Optional[List[str]] = None,
        required_permissions: Optional[List[str]] = None,
        auto_error: bool = True
    ):
        super().__init__(auto_error=auto_error)
        self.token_manager = token_manager
        self.required_roles = required_roles or []
        self.required_permissions = required_permissions or []
    
    async def __call__(self, request: Request) -> TokenClaims:
        """Authenticate request and return claims"""
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        try:
            # Verify token
            claims = await self._verify_token_async(credentials.credentials)
            
            # Check roles
            if self.required_roles:
                if not any(role in claims.roles for role in self.required_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Required roles: {self.required_roles}"
                    )
            
            # Check permissions
            if self.required_permissions:
                if not any(perm in claims.permissions for perm in self.required_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Required permissions: {self.required_permissions}"
                    )
            
            return claims
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    
    async def _verify_token_async(self, token: str) -> TokenClaims:
        """Verify token asynchronously"""
        # Check blacklist
        if self.token_manager.redis:
            is_blacklisted = await self.token_manager._is_token_blacklisted(token)
            if is_blacklisted:
                raise JWTError("Token is blacklisted")
        
        # Verify token
        return self.token_manager.verify_token(token, verify_blacklist=False)


# Dependency factories
def get_jwt_config() -> JWTConfig:
    """Get JWT configuration from settings"""
    return JWTConfig(
        secret_key=settings.SECRET_KEY,
        algorithm=Algorithm(getattr(settings, 'JWT_ALGORITHM', 'HS256')),
        access_token_expire=getattr(settings, 'JWT_ACCESS_TOKEN_EXPIRE', 3600),
        refresh_token_expire=getattr(settings, 'JWT_REFRESH_TOKEN_EXPIRE', 604800),
        issuer=getattr(settings, 'JWT_ISSUER', None),
        audience=getattr(settings, 'JWT_AUDIENCE', None)
    )


def get_token_manager(config: JWTConfig = Depends(get_jwt_config)) -> JWTTokenManager:
    """Get JWT token manager"""
    # Initialize Redis client here if needed
    return JWTTokenManager(config)


def create_jwt_bearer(
    required_roles: Optional[List[str]] = None,
    required_permissions: Optional[List[str]] = None
) -> JWTBearer:
    """Create JWT Bearer dependency with requirements"""
    def _create_bearer(token_manager: JWTTokenManager = Depends(get_token_manager)):
        return JWTBearer(token_manager, required_roles, required_permissions)
    
    return Depends(_create_bearer)


# Role and permission decorators
def require_roles(*roles: str):
    """Decorator to require specific roles"""
    return create_jwt_bearer(required_roles=list(roles))


def require_permissions(*permissions: str):
    """Decorator to require specific permissions"""
    return create_jwt_bearer(required_permissions=list(permissions))


def require_admin():
    """Decorator to require admin role"""
    return require_roles("admin")


def require_user():
    """Decorator to require any authenticated user"""
    return create_jwt_bearer()


# Utility functions
def create_jwt_middleware(
    app,
    config: Optional[JWTConfig] = None,
    redis_client: Optional[redis.Redis] = None,
    exempt_paths: Optional[List[str]] = None
) -> {{middleware_name}}JWTMiddleware:
    """Create and configure JWT middleware"""
    if config is None:
        config = get_jwt_config()
    
    return {{middleware_name}}JWTMiddleware(app, config, redis_client, exempt_paths)


# Export classes and functions
__all__ = [
    'JWTError',
    'TokenType',
    'Algorithm',
    'JWTConfig',
    'TokenClaims',
    'JWTTokenManager',
    '{{middleware_name}}JWTMiddleware',
    'JWTBearer',
    'get_jwt_config',
    'get_token_manager',
    'create_jwt_bearer',
    'require_roles',
    'require_permissions',
    'require_admin',
    'require_user',
    'create_jwt_middleware'
]