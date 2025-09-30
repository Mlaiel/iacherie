#!/usr/bin/env python3
"""
⚡ gRPC Authentication Template - Enterprise Security
🏗️ Architecture: Ainflue Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import grpc
from grpc import aio
import jwt
import time
import json
import logging
import hashlib
import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import redis
import uuid

# Expert Team: Lead Dev IA + Backend Senior + Security Expert + Cryptography Expert
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class AuthMethod(str, Enum):
    """Authentication methods"""
    JWT_BEARER = "jwt_bearer"
    API_KEY = "api_key"
    MUTUAL_TLS = "mutual_tls"
    OAUTH2 = "oauth2"
    CREATOR_TOKEN = "creator_token"
    ADMIN_KEY = "admin_key"
    SERVICE_ACCOUNT = "service_account"


class UserRole(str, Enum):
    """User roles for authorization"""
    ANONYMOUS = "anonymous"
    USER = "user"
    CREATOR = "creator"
    PREMIUM_CREATOR = "premium_creator"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    SERVICE_ACCOUNT = "service_account"


class AuthScope(str, Enum):
    """Authentication scopes"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    CREATOR_CONTENT = "creator:content"
    CREATOR_ANALYTICS = "creator:analytics"
    CREATOR_MONETIZATION = "creator:monetization"
    PLATFORM_MANAGEMENT = "platform:management"


@dataclass
class AuthContext:
    """Authentication context for requests"""
    user_id: str
    username: str
    role: UserRole
    scopes: List[AuthScope]
    creator_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Token information
    token_type: AuthMethod = AuthMethod.JWT_BEARER
    token_issued_at: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_creator(self) -> bool:
        """Check if user is a creator"""
        return self.role in [UserRole.CREATOR, UserRole.PREMIUM_CREATOR]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.MODERATOR]
    
    @property
    def is_expired(self) -> bool:
        """Check if authentication is expired"""
        if self.token_expires_at:
            return datetime.utcnow() > self.token_expires_at
        return False
    
    def has_scope(self, scope: AuthScope) -> bool:
        """Check if user has specific scope"""
        return scope in self.scopes
    
    def has_any_scope(self, scopes: List[AuthScope]) -> bool:
        """Check if user has any of the specified scopes"""
        return any(scope in self.scopes for scope in scopes)


@dataclass
class AuthConfig:
    """Enterprise authentication configuration"""
    # JWT settings
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire: int = 3600  # 1 hour
    jwt_refresh_token_expire: int = 86400 * 7  # 7 days
    
    # Public key for JWT verification (for RS256)
    jwt_public_key: Optional[str] = None
    jwt_private_key: Optional[str] = None
    
    # API key settings
    api_key_header: str = "x-api-key"
    api_key_prefix: str = "ak_"
    api_key_length: int = 32
    
    # OAuth2 settings
    oauth2_issuer: str = "https://auth.ainflue.com"
    oauth2_audience: str = "ainflue-api"
    oauth2_jwks_url: str = "https://auth.ainflue.com/.well-known/jwks.json"
    
    # mTLS settings
    enable_mtls: bool = False
    ca_cert_path: Optional[str] = None
    require_client_cert: bool = False
    
    # Session management
    enable_sessions: bool = True
    session_timeout: int = 3600  # 1 hour
    max_sessions_per_user: int = 5
    
    # Security settings
    enable_rate_limiting: bool = True
    max_auth_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    enable_audit_logging: bool = True
    
    # Creator-specific settings
    creator_token_prefix: str = "ct_"
    creator_token_scopes: List[AuthScope] = field(default_factory=lambda: [
        AuthScope.READ, AuthScope.WRITE,
        AuthScope.CREATOR_CONTENT, AuthScope.CREATOR_ANALYTICS, AuthScope.CREATOR_MONETIZATION
    ])
    
    # Cache settings
    enable_auth_cache: bool = True
    cache_ttl: int = 300  # 5 minutes
    redis_url: Optional[str] = None
    
    # Advanced features
    enable_2fa: bool = True
    enable_device_tracking: bool = True
    enable_geo_blocking: bool = False
    allowed_countries: List[str] = field(default_factory=list)


class AuthenticationError(grpc.RpcError):
    """Custom authentication error"""
    
    def __init__(self, message: str, code: grpc.StatusCode = grpc.StatusCode.UNAUTHENTICATED):
        self.message = message
        self.code = lambda: code
        self.details = lambda: message
    
    def __str__(self):
        return self.message


class AuthorizationError(grpc.RpcError):
    """Custom authorization error"""
    
    def __init__(self, message: str, code: grpc.StatusCode = grpc.StatusCode.PERMISSION_DENIED):
        self.message = message
        self.code = lambda: code
        self.details = lambda: message
    
    def __str__(self):
        return self.message


class TokenManager:
    """
    🔑 Enterprise Token Management
    
    Features:
    - JWT token generation and validation
    - Token refresh mechanism
    - Token blacklisting
    - Multi-algorithm support
    """
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger("grpc_token_manager")
        self.blacklisted_tokens: set = set()
        
        # Setup Redis cache if enabled
        self.redis_client = None
        if config.enable_auth_cache and config.redis_url:
            try:
                self.redis_client = redis.from_url(config.redis_url)
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
    
    def generate_access_token(
        self,
        user_id: str,
        username: str,
        role: UserRole,
        scopes: List[AuthScope],
        creator_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(seconds=self.config.jwt_access_token_expire)
        
        payload = {
            "sub": user_id,
            "username": username,
            "role": role.value,
            "scopes": [scope.value for scope in scopes],
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "iss": self.config.oauth2_issuer,
            "aud": self.config.oauth2_audience,
            "jti": str(uuid.uuid4())  # JWT ID for tracking
        }
        
        if creator_id:
            payload["creator_id"] = creator_id
        
        if metadata:
            payload["metadata"] = metadata
        
        # Generate token
        if self.config.jwt_algorithm.startswith("RS"):
            # RSA algorithm
            if not self.config.jwt_private_key:
                raise ValueError("Private key required for RSA algorithm")
            
            private_key = serialization.load_pem_private_key(
                self.config.jwt_private_key.encode(),
                password=None
            )
            token = jwt.encode(payload, private_key, algorithm=self.config.jwt_algorithm)
        else:
            # HMAC algorithm
            token = jwt.encode(payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
        
        # Cache token metadata
        if self.redis_client:
            cache_key = f"token:{payload['jti']}"
            cache_data = {
                "user_id": user_id,
                "role": role.value,
                "created_at": now.isoformat()
            }
            self.redis_client.setex(
                cache_key, 
                self.config.jwt_access_token_expire, 
                json.dumps(cache_data)
            )
        
        return token
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh token"""
        now = datetime.utcnow()
        expire = now + timedelta(seconds=self.config.jwt_refresh_token_expire)
        
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
    
    def validate_token(self, token: str) -> AuthContext:
        """Validate and decode JWT token"""
        try:
            # Check if token is blacklisted
            if token in self.blacklisted_tokens:
                raise AuthenticationError("Token has been revoked")
            
            # Decode token
            if self.config.jwt_algorithm.startswith("RS"):
                # RSA algorithm
                if not self.config.jwt_public_key:
                    raise ValueError("Public key required for RSA algorithm")
                
                public_key = serialization.load_pem_public_key(
                    self.config.jwt_public_key.encode()
                )
                payload = jwt.decode(
                    token, 
                    public_key, 
                    algorithms=[self.config.jwt_algorithm],
                    audience=self.config.oauth2_audience,
                    issuer=self.config.oauth2_issuer
                )
            else:
                # HMAC algorithm
                payload = jwt.decode(
                    token,
                    self.config.jwt_secret_key,
                    algorithms=[self.config.jwt_algorithm],
                    audience=self.config.oauth2_audience,
                    issuer=self.config.oauth2_issuer
                )
            
            # Extract information
            user_id = payload.get("sub")
            username = payload.get("username", "")
            role = UserRole(payload.get("role", UserRole.USER.value))
            scopes = [AuthScope(scope) for scope in payload.get("scopes", [])]
            creator_id = payload.get("creator_id")
            
            # Create auth context
            auth_context = AuthContext(
                user_id=user_id,
                username=username,
                role=role,
                scopes=scopes,
                creator_id=creator_id,
                token_type=AuthMethod.JWT_BEARER,
                token_issued_at=datetime.fromtimestamp(payload.get("iat", 0)),
                token_expires_at=datetime.fromtimestamp(payload.get("exp", 0)),
                metadata=payload.get("metadata", {})
            )
            
            return auth_context
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def revoke_token(self, token: str):
        """Revoke (blacklist) a token"""
        try:
            # Decode to get JTI
            payload = jwt.decode(
                token,
                options={"verify_signature": False}  # We just need the JTI
            )
            jti = payload.get("jti")
            
            if jti:
                self.blacklisted_tokens.add(jti)
                
                # Store in Redis if available
                if self.redis_client:
                    self.redis_client.setex(f"blacklist:{jti}", 86400, "1")
            
        except Exception as e:
            self.logger.error(f"Error revoking token: {e}")
    
    def generate_api_key(self, user_id: str, scopes: List[AuthScope]) -> str:
        """Generate API key"""
        # Create a structured API key
        timestamp = int(time.time())
        random_part = secrets.token_urlsafe(16)
        
        # Create payload
        payload = {
            "user_id": user_id,
            "scopes": [scope.value for scope in scopes],
            "created_at": timestamp
        }
        
        # Encode payload
        encoded_payload = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).decode().rstrip("=")
        
        # Create signature
        signature = hashlib.sha256(
            f"{encoded_payload}{random_part}{self.config.jwt_secret_key}".encode()
        ).hexdigest()[:16]
        
        # Construct API key
        api_key = f"{self.config.api_key_prefix}{encoded_payload}.{random_part}.{signature}"
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> AuthContext:
        """Validate API key"""
        try:
            # Check prefix
            if not api_key.startswith(self.config.api_key_prefix):
                raise AuthenticationError("Invalid API key format")
            
            # Remove prefix
            key_data = api_key[len(self.config.api_key_prefix):]
            
            # Split parts
            parts = key_data.split(".")
            if len(parts) != 3:
                raise AuthenticationError("Invalid API key format")
            
            encoded_payload, random_part, signature = parts
            
            # Verify signature
            expected_signature = hashlib.sha256(
                f"{encoded_payload}{random_part}{self.config.jwt_secret_key}".encode()
            ).hexdigest()[:16]
            
            if not secrets.compare_digest(signature, expected_signature):
                raise AuthenticationError("Invalid API key signature")
            
            # Decode payload
            payload_data = base64.urlsafe_b64decode(
                encoded_payload + "=" * (4 - len(encoded_payload) % 4)
            )
            payload = json.loads(payload_data.decode())
            
            # Extract information
            user_id = payload["user_id"]
            scopes = [AuthScope(scope) for scope in payload["scopes"]]
            created_at = datetime.fromtimestamp(payload["created_at"])
            
            # Create auth context
            auth_context = AuthContext(
                user_id=user_id,
                username=f"api_user_{user_id}",
                role=UserRole.USER,  # Default role for API keys
                scopes=scopes,
                token_type=AuthMethod.API_KEY,
                token_issued_at=created_at,
                metadata={"api_key_id": signature}
            )
            
            return auth_context
            
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise AuthenticationError(f"Invalid API key: {str(e)}")


class SessionManager:
    """
    📝 Enterprise Session Management
    
    Features:
    - Session tracking
    - Multi-device support
    - Session invalidation
    - Concurrent session limits
    """
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger("grpc_session_manager")
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Setup Redis for distributed sessions
        self.redis_client = None
        if config.redis_url:
            try:
                self.redis_client = redis.from_url(config.redis_url)
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}")
    
    def create_session(self, auth_context: AuthContext, metadata: Dict[str, Any]) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": auth_context.user_id,
            "username": auth_context.username,
            "role": auth_context.role.value,
            "creator_id": auth_context.creator_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "ip_address": metadata.get("ip_address"),
            "user_agent": metadata.get("user_agent"),
            "device_id": metadata.get("device_id"),
            "is_active": True
        }
        
        # Check session limits
        if self.config.max_sessions_per_user > 0:
            user_sessions = self.get_user_sessions(auth_context.user_id)
            if len(user_sessions) >= self.config.max_sessions_per_user:
                # Remove oldest session
                oldest_session = min(user_sessions, key=lambda s: s["created_at"])
                self.invalidate_session(oldest_session["session_id"])
        
        # Store session
        if self.redis_client:
            self.redis_client.setex(
                f"session:{session_id}",
                self.config.session_timeout,
                json.dumps(session_data)
            )
        else:
            self.active_sessions[session_id] = session_data
        
        self.logger.info(f"Session created: {session_id} for user {auth_context.user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        if self.redis_client:
            session_data = self.redis_client.get(f"session:{session_id}")
            if session_data:
                return json.loads(session_data)
        else:
            return self.active_sessions.get(session_id)
        
        return None
    
    def update_session_activity(self, session_id: str):
        """Update session last activity"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data["last_activity"] = datetime.utcnow().isoformat()
            
            if self.redis_client:
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.config.session_timeout,
                    json.dumps(session_data)
                )
            else:
                self.active_sessions[session_id] = session_data
    
    def invalidate_session(self, session_id: str):
        """Invalidate session"""
        if self.redis_client:
            self.redis_client.delete(f"session:{session_id}")
        else:
            self.active_sessions.pop(session_id, None)
        
        self.logger.info(f"Session invalidated: {session_id}")
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for user"""
        sessions = []
        
        if self.redis_client:
            # Scan for user sessions in Redis
            for key in self.redis_client.scan_iter(match="session:*"):
                session_data = self.redis_client.get(key)
                if session_data:
                    session = json.loads(session_data)
                    if session.get("user_id") == user_id:
                        sessions.append(session)
        else:
            # Filter in-memory sessions
            for session_data in self.active_sessions.values():
                if session_data.get("user_id") == user_id:
                    sessions.append(session_data)
        
        return sessions
    
    def invalidate_user_sessions(self, user_id: str, except_session: Optional[str] = None):
        """Invalidate all sessions for user"""
        user_sessions = self.get_user_sessions(user_id)
        for session in user_sessions:
            if except_session and session["session_id"] == except_session:
                continue
            self.invalidate_session(session["session_id"])
        
        self.logger.info(f"All sessions invalidated for user: {user_id}")


class GRPCAuthenticator:
    """
    🛡️ Enterprise gRPC Authenticator
    
    Features:
    - Multi-method authentication
    - Role-based authorization
    - Scope validation
    - Session management
    - Audit logging
    """
    
    def __init__(self, config: AuthConfig):
        self.config = config
        self.logger = logging.getLogger("grpc_authenticator")
        self.token_manager = TokenManager(config)
        self.session_manager = SessionManager(config) if config.enable_sessions else None
        
        # Rate limiting for authentication attempts
        self.auth_attempts: Dict[str, List[datetime]] = {}
        self.locked_ips: Dict[str, datetime] = {}
    
    async def authenticate(self, context) -> AuthContext:
        """Authenticate gRPC request"""
        try:
            # Extract metadata
            metadata = dict(context.invocation_metadata())
            client_ip = self._get_client_ip(context, metadata)
            
            # Check IP lockout
            if await self._is_ip_locked(client_ip):
                raise AuthenticationError("IP address is temporarily locked")
            
            # Try different authentication methods
            auth_context = None
            
            # JWT Bearer token
            auth_header = metadata.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix
                try:
                    auth_context = self.token_manager.validate_token(token)
                    auth_context.ip_address = client_ip
                    auth_context.user_agent = metadata.get("user-agent")
                except AuthenticationError:
                    pass  # Try next method
            
            # API Key
            if not auth_context:
                api_key = metadata.get(self.config.api_key_header)
                if api_key:
                    try:
                        auth_context = self.token_manager.validate_api_key(api_key)
                        auth_context.ip_address = client_ip
                        auth_context.user_agent = metadata.get("user-agent")
                    except AuthenticationError:
                        pass  # Try next method
            
            # Creator Token (special handling)
            if not auth_context:
                creator_token = metadata.get("x-creator-token")
                if creator_token:
                    try:
                        auth_context = await self._validate_creator_token(creator_token)
                        auth_context.ip_address = client_ip
                        auth_context.user_agent = metadata.get("user-agent")
                    except AuthenticationError:
                        pass
            
            # mTLS (if enabled)
            if not auth_context and self.config.enable_mtls:
                try:
                    auth_context = await self._validate_mtls(context)
                except AuthenticationError:
                    pass
            
            # Check if any authentication succeeded
            if not auth_context:
                await self._record_auth_failure(client_ip)
                raise AuthenticationError("Authentication failed")
            
            # Validate session if enabled
            if self.session_manager:
                session_id = metadata.get("x-session-id")
                if session_id:
                    session_data = self.session_manager.get_session(session_id)
                    if session_data and session_data.get("user_id") == auth_context.user_id:
                        auth_context.session_id = session_id
                        self.session_manager.update_session_activity(session_id)
            
            # Additional security checks
            await self._perform_security_checks(auth_context, metadata)
            
            # Log successful authentication
            if self.config.enable_audit_logging:
                self.logger.info(
                    f"Authentication successful: {auth_context.user_id} "
                    f"({auth_context.role.value}) from {client_ip}"
                )
            
            return auth_context
            
        except AuthenticationError:
            # Record failure
            await self._record_auth_failure(client_ip)
            raise
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Authentication failed")
    
    async def authorize(self, auth_context: AuthContext, required_scopes: List[AuthScope]) -> bool:
        """Authorize request based on scopes"""
        try:
            # Check if user has required scopes
            if not auth_context.has_any_scope(required_scopes):
                self.logger.warning(
                    f"Authorization failed: {auth_context.user_id} lacks required scopes {required_scopes}"
                )
                return False
            
            # Additional role-based checks
            if AuthScope.ADMIN in required_scopes and not auth_context.is_admin:
                return False
            
            # Creator-specific authorization
            if any(scope.value.startswith("creator:") for scope in required_scopes):
                if not auth_context.is_creator and not auth_context.is_admin:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Authorization error: {e}")
            return False
    
    async def _validate_creator_token(self, creator_token: str) -> AuthContext:
        """Validate creator-specific token"""
        if not creator_token.startswith(self.config.creator_token_prefix):
            raise AuthenticationError("Invalid creator token format")
        
        # Extract the actual token
        token = creator_token[len(self.config.creator_token_prefix):]
        
        # Validate as JWT token
        auth_context = self.token_manager.validate_token(token)
        
        # Ensure it's a creator token
        if not auth_context.is_creator:
            raise AuthenticationError("Token is not a creator token")
        
        # Set creator-specific scopes
        auth_context.scopes = self.config.creator_token_scopes
        
        return auth_context
    
    async def _validate_mtls(self, context) -> AuthContext:
        """Validate mutual TLS authentication"""
        # Extract client certificate from context
        # This is a simplified implementation
        peer_identity = context.peer_identity()
        if not peer_identity:
            raise AuthenticationError("No client certificate provided")
        
        # Validate certificate
        # Implementation would verify the certificate chain
        
        # Create auth context for mTLS
        auth_context = AuthContext(
            user_id="mtls_client",
            username="mTLS Client",
            role=UserRole.SERVICE_ACCOUNT,
            scopes=[AuthScope.READ, AuthScope.WRITE],
            token_type=AuthMethod.MUTUAL_TLS
        )
        
        return auth_context
    
    async def _perform_security_checks(self, auth_context: AuthContext, metadata: Dict[str, str]):
        """Perform additional security checks"""
        # Check token expiration
        if auth_context.is_expired:
            raise AuthenticationError("Token has expired")
        
        # Geo-blocking check
        if self.config.enable_geo_blocking and self.config.allowed_countries:
            client_country = metadata.get("x-country")
            if client_country and client_country not in self.config.allowed_countries:
                raise AuthenticationError("Access not allowed from this country")
        
        # Device validation (if enabled)
        if self.config.enable_device_tracking:
            device_id = metadata.get("x-device-id")
            if device_id:
                # Validate device (implementation would check against known devices)
                pass
    
    def _get_client_ip(self, context, metadata: Dict[str, str]) -> str:
        """Extract client IP from context"""
        # Try various headers for client IP
        forwarded_for = metadata.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = metadata.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Get from gRPC context
        peer = context.peer()
        if peer and ":" in peer:
            return peer.split(":")[0]
        
        return "unknown"
    
    async def _is_ip_locked(self, ip_address: str) -> bool:
        """Check if IP is temporarily locked"""
        if ip_address in self.locked_ips:
            lock_time = self.locked_ips[ip_address]
            if datetime.utcnow() > lock_time:
                # Lock expired, remove it
                del self.locked_ips[ip_address]
                return False
            return True
        return False
    
    async def _record_auth_failure(self, ip_address: str):
        """Record authentication failure"""
        current_time = datetime.utcnow()
        
        # Initialize or clean old attempts
        if ip_address not in self.auth_attempts:
            self.auth_attempts[ip_address] = []
        
        # Remove attempts older than lockout duration
        cutoff_time = current_time - timedelta(seconds=self.config.lockout_duration)
        self.auth_attempts[ip_address] = [
            attempt for attempt in self.auth_attempts[ip_address]
            if attempt > cutoff_time
        ]
        
        # Add current attempt
        self.auth_attempts[ip_address].append(current_time)
        
        # Check if IP should be locked
        if len(self.auth_attempts[ip_address]) >= self.config.max_auth_attempts:
            lock_until = current_time + timedelta(seconds=self.config.lockout_duration)
            self.locked_ips[ip_address] = lock_until
            
            self.logger.warning(
                f"IP locked due to repeated auth failures: {ip_address} "
                f"until {lock_until}"
            )


class AuthInterceptor(grpc.aio.ServerInterceptor):
    """
    🔐 gRPC Authentication Interceptor
    
    Integrates authentication into gRPC service calls
    """
    
    def __init__(self, config: AuthConfig, required_scopes: Optional[List[AuthScope]] = None):
        self.config = config
        self.authenticator = GRPCAuthenticator(config)
        self.required_scopes = required_scopes or []
        self.logger = logging.getLogger("grpc_auth_interceptor")
    
    async def intercept_service(self, continuation, handler_call_details):
        """Intercept and authenticate service calls"""
        method_name = handler_call_details.method
        
        # Check if method requires authentication
        if await self._requires_auth(method_name):
            async def auth_wrapper(request, context):
                try:
                    # Authenticate request
                    auth_context = await self.authenticator.authenticate(context)
                    
                    # Authorize request
                    if self.required_scopes:
                        if not await self.authenticator.authorize(auth_context, self.required_scopes):
                            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                            context.set_details("Insufficient permissions")
                            return None
                    
                    # Add auth context to metadata
                    context.set_trailing_metadata([
                        ("x-user-id", auth_context.user_id),
                        ("x-user-role", auth_context.role.value),
                    ])
                    
                    if auth_context.creator_id:
                        context.set_trailing_metadata([
                            ("x-creator-id", auth_context.creator_id)
                        ])
                    
                    # Call the actual handler
                    handler = continuation(handler_call_details)
                    return await handler(request, context)
                    
                except AuthenticationError as e:
                    context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                    context.set_details(str(e))
                    return None
                
                except AuthorizationError as e:
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details(str(e))
                    return None
                
                except Exception as e:
                    self.logger.error(f"Auth interceptor error: {e}")
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Authentication error")
                    return None
            
            return grpc.aio.unary_unary_rpc_method_handler(auth_wrapper)
        
        # No authentication required, proceed normally
        return continuation(handler_call_details)
    
    async def _requires_auth(self, method_name: str) -> bool:
        """Check if method requires authentication"""
        # Define public methods that don't require authentication
        public_methods = [
            "/health.HealthService/Check",
            "/auth.AuthService/Login",
            "/auth.AuthService/Register",
            "/public.PublicService/GetPublicContent"
        ]
        
        return method_name not in public_methods


# Factory functions for easy integration
def create_auth_interceptor(
    config: Optional[AuthConfig] = None,
    required_scopes: Optional[List[AuthScope]] = None
) -> AuthInterceptor:
    """
    🏭 Factory function to create authentication interceptor
    
    Args:
        config: Authentication configuration
        required_scopes: Required scopes for authorization
    
    Returns:
        Configured authentication interceptor
    """
    if config is None:
        config = AuthConfig()
    
    return AuthInterceptor(config, required_scopes)


def setup_creator_auth() -> AuthInterceptor:
    """
    🎯 Creator-specific authentication setup
    Optimized for content creation platforms
    """
    config = AuthConfig(
        # Enhanced JWT settings for creators
        jwt_access_token_expire=7200,  # 2 hours for creators
        jwt_refresh_token_expire=86400 * 30,  # 30 days
        
        # Creator token settings
        creator_token_prefix="ct_",
        creator_token_scopes=[
            AuthScope.READ, AuthScope.WRITE,
            AuthScope.CREATOR_CONTENT, AuthScope.CREATOR_ANALYTICS,
            AuthScope.CREATOR_MONETIZATION
        ],
        
        # Enhanced session management
        enable_sessions=True,
        session_timeout=7200,  # 2 hours
        max_sessions_per_user=10,  # Multiple devices for creators
        
        # Security settings for creator accounts
        enable_rate_limiting=True,
        max_auth_attempts=3,  # Stricter for creator accounts
        lockout_duration=1800,  # 30 minutes
        
        # Advanced features
        enable_2fa=True,
        enable_device_tracking=True,
        enable_audit_logging=True,
        
        # Cache settings for performance
        enable_auth_cache=True,
        cache_ttl=600,  # 10 minutes
    )
    
    # Creator-specific required scopes
    creator_scopes = [AuthScope.CREATOR_CONTENT]
    
    return AuthInterceptor(config, creator_scopes)


if __name__ == "__main__":
    # Example usage
    async def example_auth_server():
        """Example authenticated gRPC server"""
        # Create auth configuration
        config = AuthConfig(
            jwt_secret_key="your-secret-key",
            enable_sessions=True,
            enable_audit_logging=True
        )
        
        # Create auth interceptor
        auth_interceptor = create_auth_interceptor(
            config,
            required_scopes=[AuthScope.READ]
        )
        
        # Create server with auth interceptor
        server = grpc.aio.server(interceptors=[auth_interceptor])
        
        # Add your services here
        # server.add_insecure_port('[::]:50051')
        
        print("Authenticated gRPC server example")
        print("Auth interceptor configured with JWT and sessions")
        
        # Generate example tokens
        token_manager = TokenManager(config)
        
        # Generate access token for a creator
        access_token = token_manager.generate_access_token(
            user_id="creator_123",
            username="john_creator",
            role=UserRole.CREATOR,
            scopes=[AuthScope.READ, AuthScope.WRITE, AuthScope.CREATOR_CONTENT],
            creator_id="creator_123"
        )
        
        print(f"\nExample creator access token:")
        print(f"{access_token[:50]}...")
        
        # Generate API key
        api_key = token_manager.generate_api_key(
            user_id="api_user_456",
            scopes=[AuthScope.READ]
        )
        
        print(f"\nExample API key:")
        print(f"{api_key[:50]}...")
    
    # Run example
    print("gRPC Authentication Template Example")
    print("This demonstrates enterprise authentication for gRPC services")
    
    asyncio.run(example_auth_server())