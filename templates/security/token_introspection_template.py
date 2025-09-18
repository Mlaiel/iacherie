"""Token Introspection Template for Ainflue Platform
RFC 7662 compliant token introspection service with advanced token validation,
security analysis, and creator-specific token management features.

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle protégée
"""

import logging
import secrets
import hashlib
import base64
import json
import asyncio
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import jwt
from pydantic import BaseModel, Field, validator
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

from core.config import get_settings
from utils.exceptions import TokenException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class TokenType(Enum):
    """Token types"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    API_KEY = "api_key"
    DEVICE_TOKEN = "device_token"
    SESSION_TOKEN = "session_token"
    WEBHOOK_TOKEN = "webhook_token"
    UPLOAD_TOKEN = "upload_token"


class TokenStatus(Enum):
    """Token status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    INVALID = "invalid"


class TokenFormat(Enum):
    """Token formats"""
    JWT = "jwt"
    OPAQUE = "opaque"
    REFERENCE = "reference"


class GrantType(Enum):
    """OAuth 2.0 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PASSWORD = "password"
    DEVICE_CODE = "device_code"
    IMPLICIT = "implicit"


class TokenMetadata(BaseModel):
    """Token metadata"""
    token_id: str = Field(..., description="Unique token identifier")
    token_type: TokenType = Field(..., description="Token type")
    format: TokenFormat = Field(..., description="Token format")
    client_id: Optional[str] = Field(default=None, description="OAuth client ID")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    subject: Optional[str] = Field(default=None, description="Token subject")
    audience: List[str] = Field(default_factory=list, description="Token audience")
    scopes: List[str] = Field(default_factory=list, description="Granted scopes")
    issued_at: datetime = Field(..., description="Token issuance time")
    expires_at: Optional[datetime] = Field(default=None, description="Token expiration")
    not_before: Optional[datetime] = Field(default=None, description="Not valid before")
    issuer: str = Field(..., description="Token issuer")
    grant_type: Optional[GrantType] = Field(default=None, description="Grant type used")
    auth_methods: List[str] = Field(default_factory=list, description="Authentication methods")
    device_id: Optional[str] = Field(default=None, description="Associated device ID")
    session_id: Optional[str] = Field(default=None, description="Associated session ID")
    ip_address: Optional[str] = Field(default=None, description="Client IP at issuance")
    user_agent: Optional[str] = Field(default=None, description="Client user agent")
    usage_count: int = Field(default=0, description="Token usage counter")
    last_used: Optional[datetime] = Field(default=None, description="Last usage time")
    revoked_at: Optional[datetime] = Field(default=None, description="Revocation time")
    revoked_by: Optional[str] = Field(default=None, description="Revoked by")
    revocation_reason: Optional[str] = Field(default=None, description="Revocation reason")
    custom_claims: Dict[str, Any] = Field(default_factory=dict, description="Custom claims")


class TokenIntrospectionRequest(BaseModel):
    """Token introspection request (RFC 7662)"""
    token: str = Field(..., description="Token to introspect")
    token_type_hint: Optional[TokenType] = Field(default=None, description="Token type hint")
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    client_secret: Optional[str] = Field(default=None, description="Client secret")
    additional_claims: Dict[str, Any] = Field(default_factory=dict, description="Additional claims to include")


class TokenIntrospectionResponse(BaseModel):
    """Token introspection response (RFC 7662)"""
    active: bool = Field(..., description="Token active status")
    token_type: Optional[str] = Field(default=None, description="Token type")
    scope: Optional[str] = Field(default=None, description="Space-separated scopes")
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    username: Optional[str] = Field(default=None, description="Username")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    subject: Optional[str] = Field(default=None, description="Subject identifier")
    audience: Optional[Union[str, List[str]]] = Field(default=None, description="Audience")
    issuer: Optional[str] = Field(default=None, description="Issuer identifier")
    issued_at: Optional[int] = Field(default=None, description="Issued at timestamp")
    expires_at: Optional[int] = Field(default=None, description="Expiration timestamp")
    not_before: Optional[int] = Field(default=None, description="Not before timestamp")
    jti: Optional[str] = Field(default=None, description="JWT ID")
    device_id: Optional[str] = Field(default=None, description="Device identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    auth_methods: Optional[List[str]] = Field(default=None, description="Authentication methods")
    grant_type: Optional[str] = Field(default=None, description="Grant type")
    usage_count: Optional[int] = Field(default=None, description="Usage count")
    last_used: Optional[int] = Field(default=None, description="Last used timestamp")
    security_level: Optional[str] = Field(default=None, description="Security level")
    # Custom Ainflue claims
    creator_tier: Optional[str] = Field(default=None, description="Creator tier level")
    content_permissions: Optional[List[str]] = Field(default=None, description="Content permissions")
    monetization_enabled: Optional[bool] = Field(default=None, description="Monetization status")
    collaboration_access: Optional[bool] = Field(default=None, description="Collaboration access")
    # Additional custom claims
    custom_claims: Dict[str, Any] = Field(default_factory=dict, description="Custom claims")


class TokenValidationRequest(BaseModel):
    """Token validation request"""
    token: str = Field(..., description="Token to validate")
    required_scopes: List[str] = Field(default_factory=list, description="Required scopes")
    required_audience: Optional[str] = Field(default=None, description="Required audience")
    client_id: Optional[str] = Field(default=None, description="Client making request")
    resource: Optional[str] = Field(default=None, description="Target resource")
    action: Optional[str] = Field(default=None, description="Action being performed")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class TokenValidationResponse(BaseModel):
    """Token validation response"""
    valid: bool = Field(..., description="Token validity")
    token_metadata: Optional[TokenMetadata] = Field(default=None, description="Token metadata")
    introspection_data: Optional[TokenIntrospectionResponse] = Field(default=None)
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    security_warnings: List[str] = Field(default_factory=list, description="Security warnings")
    rate_limit_remaining: Optional[int] = Field(default=None, description="Rate limit remaining")
    rate_limit_reset: Optional[datetime] = Field(default=None, description="Rate limit reset time")


class TokenRevocationRequest(BaseModel):
    """Token revocation request (RFC 7009)"""
    token: str = Field(..., description="Token to revoke")
    token_type_hint: Optional[TokenType] = Field(default=None, description="Token type hint")
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    client_secret: Optional[str] = Field(default=None, description="Client secret")
    revocation_reason: str = Field(default="user_request", description="Revocation reason")


class TokenIntrospectionService:
    """Comprehensive token introspection service for Ainflue platform
    
    Provides RFC 7662 compliant token introspection with:
    - Multi-format token support (JWT, opaque, reference)
    - Advanced token validation and security analysis
    - Real-time token status monitoring
    - Token lifecycle management and revocation
    - Creator-specific token features and permissions
    - Rate limiting and abuse protection
    - Audit logging and compliance reporting
    - High-performance token caching
    - Integration with session and device management
    """
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.cipher = Fernet(Fernet.generate_key())
        
        # Token storage
        self.token_metadata: Dict[str, TokenMetadata] = {}
        self.opaque_tokens: Dict[str, Dict[str, Any]] = {}
        self.revoked_tokens: set = set()
        
        # JWT configuration
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
        self.jwt_issuer = getattr(settings, 'JWT_ISSUER', 'ainflue.com')
        
        # RSA keys for JWT signing (if using RS256)
        self.private_key = None
        self.public_key = None
        self._load_jwt_keys()
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.rate_limit_config = {
            'requests_per_minute': 1000,
            'requests_per_hour': 10000
        }
        
        # Token introspection cache
        self.introspection_cache: Dict[str, Tuple[TokenIntrospectionResponse, datetime]] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Security patterns
        self.suspicious_patterns = {
            'rapid_introspection': {'threshold': 100, 'window': 60},
            'token_enumeration': {'threshold': 50, 'window': 300},
            'invalid_token_flood': {'threshold': 20, 'window': 60}
        }
        
        logger.info("Token introspection service initialized")
    
    def _load_jwt_keys(self):
        """Load JWT signing keys"""
        try:
            if hasattr(settings, 'JWT_PRIVATE_KEY') and settings.JWT_PRIVATE_KEY:
                self.private_key = load_pem_private_key(
                    settings.JWT_PRIVATE_KEY.encode(),
                    password=None
                )
            
            if hasattr(settings, 'JWT_PUBLIC_KEY') and settings.JWT_PUBLIC_KEY:
                self.public_key = load_pem_public_key(settings.JWT_PUBLIC_KEY.encode())
                
            logger.info("JWT keys loaded successfully")
        except Exception as e:
            logger.warning(f"JWT key loading failed: {e}")
    
    async def introspect_token(self, request: TokenIntrospectionRequest) -> TokenIntrospectionResponse:
        """Introspect token according to RFC 7662"""
        try:
            # Rate limiting check
            if not await self._check_rate_limit(request.client_id):
                return TokenIntrospectionResponse(active=False)
            
            # Check cache first
            cached_response = self._get_cached_introspection(request.token)
            if cached_response:
                return cached_response
            
            # Authenticate client if credentials provided
            if request.client_id and request.client_secret:
                if not await self._authenticate_client(request.client_id, request.client_secret):
                    return TokenIntrospectionResponse(active=False)
            
            # Check if token is revoked
            token_hash = self._hash_token(request.token)
            if token_hash in self.revoked_tokens:
                response = TokenIntrospectionResponse(active=False)
                self._cache_introspection_response(request.token, response)
                return response
            
            # Determine token format and introspect
            token_format = self._detect_token_format(request.token)
            
            if token_format == TokenFormat.JWT:
                response = await self._introspect_jwt_token(request)
            elif token_format == TokenFormat.OPAQUE:
                response = await self._introspect_opaque_token(request)
            elif token_format == TokenFormat.REFERENCE:
                response = await self._introspect_reference_token(request)
            else:
                response = TokenIntrospectionResponse(active=False)
            
            # Update token usage if active
            if response.active:
                await self._update_token_usage(request.token)
            
            # Cache response
            self._cache_introspection_response(request.token, response)
            
            # Record metrics
            await self.metrics_collector.record_token_introspection(
                token_type=response.token_type or "unknown",
                active=response.active,
                client_id=request.client_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Token introspection failed: {e}")
            return TokenIntrospectionResponse(active=False)
    
    async def validate_token(self, request: TokenValidationRequest) -> TokenValidationResponse:
        """Comprehensive token validation"""
        try:
            # Perform introspection
            introspection_req = TokenIntrospectionRequest(token=request.token)
            introspection_resp = await self.introspect_token(introspection_req)
            
            if not introspection_resp.active:
                return TokenValidationResponse(
                    valid=False,
                    introspection_data=introspection_resp,
                    validation_errors=["Token is not active"]
                )
            
            validation_errors = []
            security_warnings = []
            
            # Validate scopes
            if request.required_scopes:
                token_scopes = set(introspection_resp.scope.split() if introspection_resp.scope else [])
                required_scopes = set(request.required_scopes)
                
                if not required_scopes.issubset(token_scopes):
                    missing_scopes = required_scopes - token_scopes
                    validation_errors.append(f"Missing required scopes: {', '.join(missing_scopes)}")
            
            # Validate audience
            if request.required_audience and introspection_resp.audience:
                audiences = introspection_resp.audience if isinstance(introspection_resp.audience, list) else [introspection_resp.audience]
                if request.required_audience not in audiences:
                    validation_errors.append(f"Invalid audience. Required: {request.required_audience}")
            
            # Validate client
            if request.client_id and introspection_resp.client_id:
                if request.client_id != introspection_resp.client_id:
                    validation_errors.append("Token not issued for this client")
            
            # Check token age and usage patterns
            if introspection_resp.issued_at:
                token_age = datetime.utcnow().timestamp() - introspection_resp.issued_at
                
                # Warn about old tokens
                if token_age > 86400:  # 24 hours
                    security_warnings.append("Token is more than 24 hours old")
                
                # Check for suspicious usage patterns
                if introspection_resp.usage_count and introspection_resp.usage_count > 1000:
                    security_warnings.append("Token has high usage count")
            
            # Get token metadata
            token_metadata = self.token_metadata.get(self._hash_token(request.token))
            
            # Check rate limiting
            rate_limit_info = await self._get_rate_limit_info(introspection_resp.client_id)
            
            is_valid = len(validation_errors) == 0
            
            return TokenValidationResponse(
                valid=is_valid,
                token_metadata=token_metadata,
                introspection_data=introspection_resp,
                validation_errors=validation_errors,
                security_warnings=security_warnings,
                rate_limit_remaining=rate_limit_info.get('remaining'),
                rate_limit_reset=rate_limit_info.get('reset_time')
            )
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return TokenValidationResponse(
                valid=False,
                validation_errors=[str(e)]
            )
    
    async def revoke_token(self, request: TokenRevocationRequest) -> bool:
        """Revoke token according to RFC 7009"""
        try:
            # Authenticate client if credentials provided
            if request.client_id and request.client_secret:
                if not await self._authenticate_client(request.client_id, request.client_secret):
                    return False
            
            token_hash = self._hash_token(request.token)
            
            # Add to revoked tokens set
            self.revoked_tokens.add(token_hash)
            
            # Update token metadata if exists
            if token_hash in self.token_metadata:
                metadata = self.token_metadata[token_hash]
                metadata.revoked_at = datetime.utcnow()
                metadata.revocation_reason = request.revocation_reason
                metadata.revoked_by = request.client_id or "system"
            
            # Clear from introspection cache
            self._clear_token_from_cache(request.token)
            
            # Record metrics
            await self.metrics_collector.record_token_revocation(
                token_type=request.token_type_hint.value if request.token_type_hint else "unknown",
                reason=request.revocation_reason,
                client_id=request.client_id
            )
            
            logger.info(f"Token revoked: {request.revocation_reason}")
            return True
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def _detect_token_format(self, token: str) -> TokenFormat:
        """Detect token format"""
        # JWT tokens have 3 parts separated by dots
        if token.count('.') == 2:
            try:
                # Try to decode JWT header
                parts = token.split('.')
                header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
                if 'alg' in header:
                    return TokenFormat.JWT
            except:
                pass
        
        # Check if it's a reference token (UUID-like)
        if len(token) == 36 and token.count('-') == 4:
            return TokenFormat.REFERENCE
        
        # Default to opaque
        return TokenFormat.OPAQUE
    
    async def _introspect_jwt_token(self, request: TokenIntrospectionRequest) -> TokenIntrospectionResponse:
        """Introspect JWT token"""
        try:
            # Decode JWT without verification first to get header
            unverified_payload = jwt.decode(request.token, options={"verify_signature": False})
            
            # Verify JWT signature
            if self.jwt_algorithm.startswith('RS'):
                if not self.public_key:
                    raise TokenException("Public key not configured for RS256")
                payload = jwt.decode(request.token, self.public_key, algorithms=[self.jwt_algorithm])
            else:
                payload = jwt.decode(request.token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check expiration
            now = datetime.utcnow().timestamp()
            if 'exp' in payload and payload['exp'] < now:
                return TokenIntrospectionResponse(active=False)
            
            # Check not before
            if 'nbf' in payload and payload['nbf'] > now:
                return TokenIntrospectionResponse(active=False)
            
            # Extract standard claims
            response = TokenIntrospectionResponse(
                active=True,
                token_type="access_token",
                client_id=payload.get('client_id'),
                username=payload.get('username'),
                user_id=payload.get('user_id'),
                subject=payload.get('sub'),
                audience=payload.get('aud'),
                issuer=payload.get('iss'),
                issued_at=payload.get('iat'),
                expires_at=payload.get('exp'),
                not_before=payload.get('nbf'),
                jti=payload.get('jti'),
                scope=' '.join(payload.get('scope', [])) if isinstance(payload.get('scope'), list) else payload.get('scope'),
                device_id=payload.get('device_id'),
                session_id=payload.get('session_id'),
                auth_methods=payload.get('auth_methods'),
                grant_type=payload.get('grant_type'),
                security_level=payload.get('security_level'),
                # Ainflue-specific claims
                creator_tier=payload.get('creator_tier'),
                content_permissions=payload.get('content_permissions'),
                monetization_enabled=payload.get('monetization_enabled'),
                collaboration_access=payload.get('collaboration_access')
            )
            
            # Add custom claims
            reserved_claims = {
                'iss', 'sub', 'aud', 'exp', 'nbf', 'iat', 'jti', 'scope', 'client_id',
                'username', 'user_id', 'device_id', 'session_id', 'auth_methods',
                'grant_type', 'security_level', 'creator_tier', 'content_permissions',
                'monetization_enabled', 'collaboration_access'
            }
            
            custom_claims = {k: v for k, v in payload.items() if k not in reserved_claims}
            response.custom_claims = custom_claims
            
            return response
            
        except jwt.ExpiredSignatureError:
            return TokenIntrospectionResponse(active=False)
        except jwt.InvalidTokenError:
            return TokenIntrospectionResponse(active=False)
        except Exception as e:
            logger.error(f"JWT introspection failed: {e}")
            return TokenIntrospectionResponse(active=False)
    
    async def _introspect_opaque_token(self, request: TokenIntrospectionRequest) -> TokenIntrospectionResponse:
        """Introspect opaque token"""
        token_hash = self._hash_token(request.token)
        
        if token_hash not in self.opaque_tokens:
            return TokenIntrospectionResponse(active=False)
        
        token_data = self.opaque_tokens[token_hash]
        
        # Check expiration
        if 'expires_at' in token_data:
            if datetime.utcnow() > datetime.fromisoformat(token_data['expires_at']):
                return TokenIntrospectionResponse(active=False)
        
        # Build response from stored data
        return TokenIntrospectionResponse(
            active=True,
            token_type=token_data.get('token_type', 'access_token'),
            client_id=token_data.get('client_id'),
            username=token_data.get('username'),
            user_id=token_data.get('user_id'),
            subject=token_data.get('subject'),
            audience=token_data.get('audience'),
            issuer=token_data.get('issuer'),
            issued_at=int(datetime.fromisoformat(token_data['issued_at']).timestamp()) if 'issued_at' in token_data else None,
            expires_at=int(datetime.fromisoformat(token_data['expires_at']).timestamp()) if 'expires_at' in token_data else None,
            scope=token_data.get('scope'),
            device_id=token_data.get('device_id'),
            session_id=token_data.get('session_id'),
            custom_claims=token_data.get('custom_claims', {})
        )
    
    async def _introspect_reference_token(self, request: TokenIntrospectionRequest) -> TokenIntrospectionResponse:
        """Introspect reference token"""
        # Reference tokens are handled similarly to opaque tokens
        # but may involve external lookups
        return await self._introspect_opaque_token(request)
    
    async def _authenticate_client(self, client_id: str, client_secret: str) -> bool:
        """Authenticate OAuth client"""
        # Simplified client authentication
        # In production, verify against client registry
        return True  # Placeholder
    
    async def _check_rate_limit(self, client_id: Optional[str]) -> bool:
        """Check rate limiting"""
        if not client_id:
            return True
        
        now = datetime.utcnow()
        
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = []
        
        requests = self.rate_limits[client_id]
        
        # Remove old requests
        minute_ago = now - timedelta(minutes=1)
        requests[:] = [req_time for req_time in requests if req_time > minute_ago]
        
        # Check minute limit
        if len(requests) >= self.rate_limit_config['requests_per_minute']:
            return False
        
        # Add current request
        requests.append(now)
        
        return True
    
    async def _get_rate_limit_info(self, client_id: Optional[str]) -> Dict[str, Any]:
        """Get rate limit information"""
        if not client_id or client_id not in self.rate_limits:
            return {
                'remaining': self.rate_limit_config['requests_per_minute'],
                'reset_time': datetime.utcnow() + timedelta(minutes=1)
            }
        
        requests = self.rate_limits[client_id]
        remaining = max(0, self.rate_limit_config['requests_per_minute'] - len(requests))
        
        return {
            'remaining': remaining,
            'reset_time': datetime.utcnow() + timedelta(minutes=1)
        }
    
    def _hash_token(self, token: str) -> str:
        """Generate hash of token for storage/lookup"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _get_cached_introspection(self, token: str) -> Optional[TokenIntrospectionResponse]:
        """Get cached introspection response"""
        token_hash = self._hash_token(token)
        
        if token_hash in self.introspection_cache:
            response, cached_at = self.introspection_cache[token_hash]
            
            # Check cache expiry
            if datetime.utcnow() - cached_at < timedelta(seconds=self.cache_ttl):
                return response
            else:
                # Remove expired cache entry
                del self.introspection_cache[token_hash]
        
        return None
    
    def _cache_introspection_response(self, token: str, response: TokenIntrospectionResponse):
        """Cache introspection response"""
        token_hash = self._hash_token(token)
        self.introspection_cache[token_hash] = (response, datetime.utcnow())
        
        # Cleanup old cache entries (keep only last 10000)
        if len(self.introspection_cache) > 10000:
            oldest_entries = sorted(
                self.introspection_cache.items(),
                key=lambda x: x[1][1]
            )[:1000]
            
            for token_hash, _ in oldest_entries:
                del self.introspection_cache[token_hash]
    
    def _clear_token_from_cache(self, token: str):
        """Clear token from cache"""
        token_hash = self._hash_token(token)
        if token_hash in self.introspection_cache:
            del self.introspection_cache[token_hash]
    
    async def _update_token_usage(self, token: str):
        """Update token usage statistics"""
        token_hash = self._hash_token(token)
        
        if token_hash in self.token_metadata:
            metadata = self.token_metadata[token_hash]
            metadata.usage_count += 1
            metadata.last_used = datetime.utcnow()
    
    async def store_opaque_token(self, token: str, token_data: Dict[str, Any]) -> bool:
        """Store opaque token data"""
        try:
            token_hash = self._hash_token(token)
            self.opaque_tokens[token_hash] = token_data
            
            # Create metadata
            metadata = TokenMetadata(
                token_id=token_hash,
                token_type=TokenType(token_data.get('token_type', 'access_token')),
                format=TokenFormat.OPAQUE,
                client_id=token_data.get('client_id'),
                user_id=token_data.get('user_id'),
                subject=token_data.get('subject'),
                audience=token_data.get('audience', []),
                scopes=token_data.get('scope', '').split() if token_data.get('scope') else [],
                issued_at=datetime.fromisoformat(token_data['issued_at']) if 'issued_at' in token_data else datetime.utcnow(),
                expires_at=datetime.fromisoformat(token_data['expires_at']) if 'expires_at' in token_data else None,
                issuer=token_data.get('issuer', self.jwt_issuer),
                custom_claims=token_data.get('custom_claims', {})
            )
            
            self.token_metadata[token_hash] = metadata
            return True
            
        except Exception as e:
            logger.error(f"Failed to store opaque token: {e}")
            return False
    
    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens and cache entries"""
        cleaned_count = 0
        now = datetime.utcnow()
        
        # Clean expired opaque tokens
        expired_tokens = []
        for token_hash, token_data in self.opaque_tokens.items():
            if 'expires_at' in token_data:
                if now > datetime.fromisoformat(token_data['expires_at']):
                    expired_tokens.append(token_hash)
        
        for token_hash in expired_tokens:
            del self.opaque_tokens[token_hash]
            if token_hash in self.token_metadata:
                del self.token_metadata[token_hash]
            cleaned_count += 1
        
        # Clean expired cache entries
        expired_cache = []
        for token_hash, (response, cached_at) in self.introspection_cache.items():
            if now - cached_at > timedelta(seconds=self.cache_ttl):
                expired_cache.append(token_hash)
        
        for token_hash in expired_cache:
            del self.introspection_cache[token_hash]
        
        logger.info(f"Cleaned up {cleaned_count} expired tokens and {len(expired_cache)} cache entries")
        return cleaned_count
    
    async def get_token_statistics(self) -> Dict[str, Any]:
        """Get token statistics"""
        stats = {
            'total_tokens': len(self.token_metadata),
            'opaque_tokens': len(self.opaque_tokens),
            'revoked_tokens': len(self.revoked_tokens),
            'cached_introspections': len(self.introspection_cache),
            'token_types': {},
            'active_tokens': 0,
            'expired_tokens': 0
        }
        
        now = datetime.utcnow()
        
        for metadata in self.token_metadata.values():
            # Count by type
            token_type = metadata.token_type.value
            stats['token_types'][token_type] = stats['token_types'].get(token_type, 0) + 1
            
            # Count active vs expired
            if metadata.expires_at and metadata.expires_at < now:
                stats['expired_tokens'] += 1
            else:
                stats['active_tokens'] += 1
        
        return stats


# Export service instance
token_introspection_service = TokenIntrospectionService()

__all__ = [
    'TokenType',
    'TokenStatus',
    'TokenFormat',
    'GrantType',
    'TokenMetadata',
    'TokenIntrospectionRequest',
    'TokenIntrospectionResponse',
    'TokenValidationRequest',
    'TokenValidationResponse',
    'TokenRevocationRequest',
    'TokenIntrospectionService',
    'token_introspection_service'
]