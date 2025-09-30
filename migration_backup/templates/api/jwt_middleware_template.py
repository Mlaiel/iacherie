"""
🔒 JWT MIDDLEWARE TEMPLATE - SECURITY EXPERT IMPLEMENTATION
===========================================================

Enterprise-grade JWT middleware template with:
- JWT token validation and verification
- Token refresh mechanism
- Blacklist and whitelist management
- Role-based access control integration
- Rate limiting per user/token
- Audit logging and monitoring
- Multi-algorithm support (RS256, HS256, ES256)
- Token introspection and claims validation

Author: Security Expert
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
import jwt
import json
import time
from datetime import datetime, timedelta
import redis.asyncio as redis
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
import httpx
from pydantic import BaseModel, Field, validator
from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib


class JWTAlgorithm(Enum):
    """Supported JWT algorithms"""
    HS256 = "HS256"  # HMAC with SHA-256
    HS384 = "HS384"  # HMAC with SHA-384
    HS512 = "HS512"  # HMAC with SHA-512
    RS256 = "RS256"  # RSA with SHA-256
    RS384 = "RS384"  # RSA with SHA-384
    RS512 = "RS512"  # RSA with SHA-512
    ES256 = "ES256"  # ECDSA with SHA-256
    ES384 = "ES384"  # ECDSA with SHA-384
    ES512 = "ES512"  # ECDSA with SHA-512


class TokenType(Enum):
    """Token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    RESET = "reset"


class TokenStatus(Enum):
    """Token status"""
    VALID = "valid"
    EXPIRED = "expired"
    BLACKLISTED = "blacklisted"
    INVALID = "invalid"
    REVOKED = "revoked"


@dataclass
class JWTConfig:
    """JWT middleware configuration"""
    # Signing configuration
    algorithm: JWTAlgorithm = JWTAlgorithm.RS256
    secret_key: Optional[str] = None
    private_key: Optional[str] = None
    public_key: Optional[str] = None
    key_id: Optional[str] = None
    
    # Token expiration
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30
    id_token_expire_minutes: int = 60
    reset_token_expire_minutes: int = 15
    
    # Issuer and audience
    issuer: str = "ainflue-platform"
    audience: List[str] = field(default_factory=lambda: ["ainflue-api"])
    
    # Token validation
    verify_signature: bool = True
    verify_exp: bool = True
    verify_nbf: bool = True
    verify_iat: bool = True
    verify_aud: bool = True
    verify_iss: bool = True
    leeway: int = 0  # seconds
    
    # Security settings
    require_https: bool = True
    cookie_secure: bool = True
    cookie_httponly: bool = True
    cookie_samesite: str = "strict"
    
    # Rate limiting
    rate_limit_per_user: int = 1000  # requests per hour
    rate_limit_window: int = 3600  # seconds
    
    # Blacklist/whitelist
    enable_blacklist: bool = True
    enable_whitelist: bool = False
    blacklist_grace_period: int = 300  # seconds
    
    # Introspection
    enable_introspection: bool = True
    introspection_endpoint: Optional[str] = None
    introspection_cache_ttl: int = 300  # seconds
    
    # Monitoring
    enable_audit_logging: bool = True
    log_successful_auth: bool = False
    log_failed_auth: bool = True
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None


class JWTClaims(BaseModel):
    """JWT claims model"""
    # Standard claims
    iss: Optional[str] = None  # Issuer
    sub: Optional[str] = None  # Subject
    aud: Optional[Union[str, List[str]]] = None  # Audience
    exp: Optional[int] = None  # Expiration time
    nbf: Optional[int] = None  # Not before
    iat: Optional[int] = None  # Issued at
    jti: Optional[str] = None  # JWT ID
    
    # Custom claims
    token_type: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Metadata
    auth_method: Optional[str] = None
    mfa_verified: bool = False
    email_verified: bool = False
    phone_verified: bool = False
    account_type: Optional[str] = None
    subscription_tier: Optional[str] = None


class TokenValidationResult(BaseModel):
    """Token validation result"""
    valid: bool
    status: TokenStatus
    claims: Optional[JWTClaims] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    decoded_token: Optional[Dict[str, Any]] = None


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    user_id: str
    current_count: int
    limit: int
    window_start: datetime
    window_end: datetime
    blocked: bool


class AuditLogEntry(BaseModel):
    """JWT audit log entry"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    user_id: Optional[str] = None
    token_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    success: bool
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class AbstractTokenStore(ABC):
    """Abstract token store interface"""
    
    @abstractmethod
    async def is_blacklisted(self, token_id: str) -> bool:
        """Check if token is blacklisted"""
        pass
    
    @abstractmethod
    async def blacklist_token(self, token_id: str, expire_at: datetime) -> bool:
        """Add token to blacklist"""
        pass
    
    @abstractmethod
    async def is_whitelisted(self, token_id: str) -> bool:
        """Check if token is whitelisted"""
        pass
    
    @abstractmethod
    async def whitelist_token(self, token_id: str, expire_at: datetime) -> bool:
        """Add token to whitelist"""
        pass
    
    @abstractmethod
    async def get_rate_limit_info(self, user_id: str) -> RateLimitInfo:
        """Get rate limit information for user"""
        pass
    
    @abstractmethod
    async def increment_rate_limit(self, user_id: str) -> int:
        """Increment rate limit counter"""
        pass
    
    @abstractmethod
    async def store_audit_log(self, entry: AuditLogEntry) -> bool:
        """Store audit log entry"""
        pass


class RedisTokenStore(AbstractTokenStore):
    """Redis-based token store implementation"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.redis = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        """Connect to Redis"""
        self.redis = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
        await self.redis.ping()
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def is_blacklisted(self, token_id: str) -> bool:
        """Check if token is blacklisted"""
        try:
            result = await self.redis.get(f"blacklist:{token_id}")
            return result is not None
        except Exception as e:
            self.logger.error(f"Failed to check blacklist for {token_id}: {e}")
            return False
    
    async def blacklist_token(self, token_id: str, expire_at: datetime) -> bool:
        """Add token to blacklist"""
        try:
            ttl = int((expire_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis.setex(f"blacklist:{token_id}", ttl, "1")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to blacklist token {token_id}: {e}")
            return False
    
    async def is_whitelisted(self, token_id: str) -> bool:
        """Check if token is whitelisted"""
        try:
            result = await self.redis.get(f"whitelist:{token_id}")
            return result is not None
        except Exception as e:
            self.logger.error(f"Failed to check whitelist for {token_id}: {e}")
            return False
    
    async def whitelist_token(self, token_id: str, expire_at: datetime) -> bool:
        """Add token to whitelist"""
        try:
            ttl = int((expire_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis.setex(f"whitelist:{token_id}", ttl, "1")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to whitelist token {token_id}: {e}")
            return False
    
    async def get_rate_limit_info(self, user_id: str) -> RateLimitInfo:
        """Get rate limit information for user"""
        try:
            now = datetime.utcnow()
            window_start = now.replace(minute=0, second=0, microsecond=0)
            window_end = window_start + timedelta(hours=1)
            
            key = f"rate_limit:{user_id}:{int(window_start.timestamp())}"
            current_count = await self.redis.get(key) or 0
            current_count = int(current_count)
            
            return RateLimitInfo(
                user_id=user_id,
                current_count=current_count,
                limit=self.config.rate_limit_per_user,
                window_start=window_start,
                window_end=window_end,
                blocked=current_count >= self.config.rate_limit_per_user
            )
        except Exception as e:
            self.logger.error(f"Failed to get rate limit info for {user_id}: {e}")
            return RateLimitInfo(
                user_id=user_id,
                current_count=0,
                limit=self.config.rate_limit_per_user,
                window_start=datetime.utcnow(),
                window_end=datetime.utcnow() + timedelta(hours=1),
                blocked=False
            )
    
    async def increment_rate_limit(self, user_id: str) -> int:
        """Increment rate limit counter"""
        try:
            now = datetime.utcnow()
            window_start = now.replace(minute=0, second=0, microsecond=0)
            key = f"rate_limit:{user_id}:{int(window_start.timestamp())}"
            
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.config.rate_limit_window)
            results = await pipe.execute()
            
            return int(results[0])
        except Exception as e:
            self.logger.error(f"Failed to increment rate limit for {user_id}: {e}")
            return 0
    
    async def store_audit_log(self, entry: AuditLogEntry) -> bool:
        """Store audit log entry"""
        try:
            key = f"audit_log:{entry.timestamp.strftime('%Y-%m-%d')}"
            value = entry.json()
            await self.redis.lpush(key, value)
            await self.redis.expire(key, 30 * 24 * 3600)  # Keep for 30 days
            return True
        except Exception as e:
            self.logger.error(f"Failed to store audit log: {e}")
            return False


class JWTKeyManager:
    """JWT key management utilities"""
    
    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """Generate a random secret key"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_rsa_key_pair(key_size: int = 2048) -> tuple:
        """Generate RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    @staticmethod
    def generate_ec_key_pair(curve_name: str = "secp256r1") -> tuple:
        """Generate EC key pair"""
        if curve_name == "secp256r1":
            curve = ec.SECP256R1()
        elif curve_name == "secp384r1":
            curve = ec.SECP384R1()
        elif curve_name == "secp521r1":
            curve = ec.SECP521R1()
        else:
            raise ValueError(f"Unsupported curve: {curve_name}")
        
        private_key = ec.generate_private_key(curve)
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem


class JWTValidator:
    """JWT token validator"""
    
    def __init__(self, config: JWTConfig, token_store: AbstractTokenStore):
        self.config = config
        self.token_store = token_store
        self.logger = logging.getLogger(__name__)
        self._key = self._prepare_key()
    
    def _prepare_key(self) -> Union[str, bytes]:
        """Prepare the key for JWT operations"""
        if self.config.algorithm.value.startswith('HS'):
            if not self.config.secret_key:
                raise ValueError("Secret key required for HMAC algorithms")
            return self.config.secret_key.encode('utf-8')
        elif self.config.algorithm.value.startswith(('RS', 'ES')):
            if not self.config.public_key:
                raise ValueError("Public key required for RSA/ECDSA algorithms")
            return self.config.public_key
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
    
    async def validate_token(self, token: str, expected_type: Optional[TokenType] = None) -> TokenValidationResult:
        """Validate JWT token"""
        try:
            # Decode token without verification first to get claims
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check token type if specified
            if expected_type and unverified_payload.get('token_type') != expected_type.value:
                return TokenValidationResult(
                    valid=False,
                    status=TokenStatus.INVALID,
                    error=f"Invalid token type. Expected: {expected_type.value}",
                    error_code="INVALID_TOKEN_TYPE"
                )
            
            # Check blacklist
            token_id = unverified_payload.get('jti')
            if token_id and self.config.enable_blacklist:
                if await self.token_store.is_blacklisted(token_id):
                    return TokenValidationResult(
                        valid=False,
                        status=TokenStatus.BLACKLISTED,
                        error="Token is blacklisted",
                        error_code="TOKEN_BLACKLISTED"
                    )
            
            # Check whitelist if enabled
            if self.config.enable_whitelist and token_id:
                if not await self.token_store.is_whitelisted(token_id):
                    return TokenValidationResult(
                        valid=False,
                        status=TokenStatus.INVALID,
                        error="Token not in whitelist",
                        error_code="TOKEN_NOT_WHITELISTED"
                    )
            
            # Verify token signature and claims
            payload = jwt.decode(
                token,
                self._key,
                algorithms=[self.config.algorithm.value],
                audience=self.config.audience if self.config.verify_aud else None,
                issuer=self.config.issuer if self.config.verify_iss else None,
                options={
                    "verify_signature": self.config.verify_signature,
                    "verify_exp": self.config.verify_exp,
                    "verify_nbf": self.config.verify_nbf,
                    "verify_iat": self.config.verify_iat,
                    "verify_aud": self.config.verify_aud,
                    "verify_iss": self.config.verify_iss
                },
                leeway=self.config.leeway
            )
            
            # Create claims object
            claims = JWTClaims(**payload)
            
            # Additional custom validations
            validation_errors = await self._perform_custom_validations(claims, token)
            if validation_errors:
                return TokenValidationResult(
                    valid=False,
                    status=TokenStatus.INVALID,
                    error="; ".join(validation_errors),
                    error_code="CUSTOM_VALIDATION_FAILED"
                )
            
            # Token is valid
            return TokenValidationResult(
                valid=True,
                status=TokenStatus.VALID,
                claims=claims,
                decoded_token=payload
            )
            
        except jwt.ExpiredSignatureError:
            return TokenValidationResult(
                valid=False,
                status=TokenStatus.EXPIRED,
                error="Token has expired",
                error_code="TOKEN_EXPIRED"
            )
        except jwt.InvalidTokenError as e:
            return TokenValidationResult(
                valid=False,
                status=TokenStatus.INVALID,
                error=str(e),
                error_code="INVALID_TOKEN"
            )
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return TokenValidationResult(
                valid=False,
                status=TokenStatus.INVALID,
                error="Token validation failed",
                error_code="VALIDATION_ERROR"
            )
    
    async def _perform_custom_validations(self, claims: JWTClaims, token: str) -> List[str]:
        """Perform custom token validations"""
        errors = []
        
        # Check if user is still active (implement your user check logic)
        if claims.user_id:
            # In real implementation, check if user account is active
            pass
        
        # Check token introspection if enabled
        if self.config.enable_introspection and self.config.introspection_endpoint:
            try:
                is_active = await self._introspect_token(token)
                if not is_active:
                    errors.append("Token is not active according to introspection endpoint")
            except Exception as e:
                self.logger.warning(f"Token introspection failed: {e}")
        
        # Check MFA requirements for sensitive operations
        if claims.token_type == TokenType.ACCESS.value:
            # Add your MFA validation logic here
            pass
        
        return errors
    
    async def _introspect_token(self, token: str) -> bool:
        """Introspect token using external endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.introspection_endpoint,
                    data={"token": token},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("active", False)
                
                return False
        except Exception as e:
            self.logger.error(f"Token introspection failed: {e}")
            raise


class JWTMiddleware:
    """JWT middleware for FastAPI"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.token_store = RedisTokenStore(config)
        self.validator = JWTValidator(config, self.token_store)
        self.security = HTTPBearer(auto_error=False)
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize middleware"""
        await self.token_store.connect()
        self.logger.info("JWT middleware initialized")
    
    async def shutdown(self):
        """Shutdown middleware"""
        await self.token_store.disconnect()
    
    async def __call__(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
    ):
        """Middleware handler"""
        
        # Extract token
        token = None
        if credentials:
            token = credentials.credentials
        else:
            # Try to get token from cookie
            token = request.cookies.get("access_token")
        
        if not token:
            await self._log_auth_event(request, None, False, "No token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token
        validation_result = await self.validator.validate_token(token, TokenType.ACCESS)
        
        if not validation_result.valid:
            await self._log_auth_event(
                request,
                validation_result.claims.user_id if validation_result.claims else None,
                False,
                validation_result.error
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=validation_result.error,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check rate limiting
        if validation_result.claims.user_id:
            rate_limit_info = await self.token_store.get_rate_limit_info(validation_result.claims.user_id)
            if rate_limit_info.blocked:
                await self._log_auth_event(
                    request,
                    validation_result.claims.user_id,
                    False,
                    "Rate limit exceeded"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Increment rate limit counter
            await self.token_store.increment_rate_limit(validation_result.claims.user_id)
        
        # Add claims to request state
        request.state.jwt_claims = validation_result.claims
        request.state.jwt_token = token
        
        # Log successful authentication
        if self.config.log_successful_auth:
            await self._log_auth_event(request, validation_result.claims.user_id, True, None)
        
        return validation_result.claims
    
    async def _log_auth_event(
        self,
        request: Request,
        user_id: Optional[str],
        success: bool,
        error: Optional[str]
    ):
        """Log authentication event"""
        if not self.config.enable_audit_logging:
            return
        
        try:
            entry = AuditLogEntry(
                event_type="jwt_authentication",
                user_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                endpoint=str(request.url),
                success=success,
                error=error
            )
            
            await self.token_store.store_audit_log(entry)
        except Exception as e:
            self.logger.error(f"Failed to log auth event: {e}")


class JWTTokenGenerator:
    """JWT token generator"""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._key = self._prepare_signing_key()
    
    def _prepare_signing_key(self) -> Union[str, bytes]:
        """Prepare the signing key"""
        if self.config.algorithm.value.startswith('HS'):
            if not self.config.secret_key:
                raise ValueError("Secret key required for HMAC algorithms")
            return self.config.secret_key.encode('utf-8')
        elif self.config.algorithm.value.startswith(('RS', 'ES')):
            if not self.config.private_key:
                raise ValueError("Private key required for RSA/ECDSA algorithms")
            return self.config.private_key
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
    
    def generate_token(
        self,
        claims: JWTClaims,
        token_type: TokenType,
        expires_in: Optional[int] = None
    ) -> str:
        """Generate JWT token"""
        
        now = datetime.utcnow()
        
        # Set standard claims
        payload = {
            "iss": self.config.issuer,
            "aud": self.config.audience,
            "iat": int(now.timestamp()),
            "jti": secrets.token_urlsafe(16),
            "token_type": token_type.value
        }
        
        # Set expiration based on token type
        if expires_in:
            exp = now + timedelta(seconds=expires_in)
        elif token_type == TokenType.ACCESS:
            exp = now + timedelta(minutes=self.config.access_token_expire_minutes)
        elif token_type == TokenType.REFRESH:
            exp = now + timedelta(days=self.config.refresh_token_expire_days)
        elif token_type == TokenType.ID:
            exp = now + timedelta(minutes=self.config.id_token_expire_minutes)
        elif token_type == TokenType.RESET:
            exp = now + timedelta(minutes=self.config.reset_token_expire_minutes)
        else:
            exp = now + timedelta(minutes=self.config.access_token_expire_minutes)
        
        payload["exp"] = int(exp.timestamp())
        payload["nbf"] = int(now.timestamp())
        
        # Add custom claims
        for field, value in claims.dict(exclude_none=True).items():
            if field not in payload:
                payload[field] = value
        
        # Generate token
        try:
            token = jwt.encode(
                payload,
                self._key,
                algorithm=self.config.algorithm.value,
                headers={"kid": self.config.key_id} if self.config.key_id else None
            )
            
            return token
        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            raise


# Utility functions and decorators
def require_permissions(*required_permissions: str):
    """Decorator to require specific permissions"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Get JWT claims from request state
            request = kwargs.get('request') or (args[0] if args else None)
            if not hasattr(request.state, 'jwt_claims'):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            claims = request.state.jwt_claims
            user_permissions = set(claims.permissions)
            
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_roles(*required_roles: str):
    """Decorator to require specific roles"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Get JWT claims from request state
            request = kwargs.get('request') or (args[0] if args else None)
            if not hasattr(request.state, 'jwt_claims'):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            claims = request.state.jwt_claims
            user_roles = set(claims.roles)
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role privileges"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Usage example
async def main():
    """Example usage of JWT middleware"""
    
    # Generate key pair for RS256
    private_key, public_key = JWTKeyManager.generate_rsa_key_pair()
    
    # Configure JWT middleware
    config = JWTConfig(
        algorithm=JWTAlgorithm.RS256,
        private_key=private_key,
        public_key=public_key,
        access_token_expire_minutes=15,
        refresh_token_expire_days=30,
        issuer="ainflue-platform",
        audience=["ainflue-api", "ainflue-web"],
        enable_audit_logging=True
    )
    
    # Initialize middleware
    middleware = JWTMiddleware(config)
    await middleware.initialize()
    
    # Generate token
    generator = JWTTokenGenerator(config)
    
    claims = JWTClaims(
        user_id="user_123",
        username="john_doe",
        email="john@example.com",
        roles=["user", "creator"],
        permissions=["read:content", "write:content"],
        session_id="session_456"
    )
    
    access_token = generator.generate_token(claims, TokenType.ACCESS)
    print(f"Generated access token: {access_token[:50]}...")
    
    # Validate token
    validation_result = await middleware.validator.validate_token(access_token, TokenType.ACCESS)
    print(f"Token valid: {validation_result.valid}")
    print(f"User ID: {validation_result.claims.user_id if validation_result.claims else None}")
    
    await middleware.shutdown()


if __name__ == "__main__":
    asyncio.run(main())