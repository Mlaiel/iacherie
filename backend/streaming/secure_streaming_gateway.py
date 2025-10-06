"""
Secure Streaming Gateway - Real Implementation

Copyright (c) 2025 Fahed Mlaiel
"""

import asyncio
import hashlib
import hmac
import jwt
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AuthenticationMethod(Enum):
    JWT = "jwt"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    CERTIFICATE = "certificate"


class AccessStatus(Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    RATE_LIMITED = "rate_limited"
    SUSPENDED = "suspended"


# Alias
AccessType = AccessStatus


class EncryptionProtocol(Enum):
    TLS_1_2 = "tls_1_2"
    TLS_1_3 = "tls_1_3"
    DTLS = "dtls"
    SRTP = "srtp"


@dataclass
class GatewayConfig:
    config_id: str
    security_level: SecurityLevel
    auth_methods: List[AuthenticationMethod]
    encryption_protocol: EncryptionProtocol
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 60


@dataclass
class StreamingToken:
    token_id: str
    user_id: str
    stream_id: str
    security_level: SecurityLevel
    issued_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(hours=2))
    permissions: List[str] = field(default_factory=list)
    jwt_token: Optional[str] = None


@dataclass
class AccessRequest:
    request_id: str
    user_id: str
    stream_id: str
    auth_method: AuthenticationMethod
    credentials: Dict[str, Any]
    client_ip: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Alias
SecurityRequest = AccessRequest


@dataclass
class AccessResponse:
    response_id: str
    request_id: str
    status: AccessStatus
    token: Optional[StreamingToken] = None
    error_message: Optional[str] = None
    retry_after_sec: Optional[int] = None


@dataclass
class RateLimitInfo:
    user_id: str
    request_count: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    is_limited: bool = False


@dataclass
class SecureStreamingRecord:
    record_id: str = field(default_factory=lambda: str(uuid4()))
    stream_id: str = ""
    config: Optional[GatewayConfig] = None
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    rate_limited_requests: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


# Alias
SecureStreamingGatewayRecord = SecureStreamingRecord


class SecureStreamingGateway:
    """Gateway sécurisé avec authentification, rate limiting et chiffrement."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Clés de sécurité (en production: stockées dans HSM/KMS)
        self.jwt_secret = secrets.token_urlsafe(32)
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        
        # Tokens actifs
        self.active_tokens: Dict[str, StreamingToken] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        
        # Blacklist IP/users
        self.blacklisted_ips: Set[str] = set()
        self.suspended_users: Set[str] = set()
        
        # Métriques
        self.total_requests = 0
        self.allowed_count = 0
        self.denied_count = 0
        self.rate_limited_count = 0
        
        self.logger = logging.getLogger(__name__)
        
        # Nettoyage périodique
        asyncio.create_task(self._cleanup_expired_tokens())

    async def authenticate(
        self,
        access_request: AccessRequest,
        gateway_config: Optional[GatewayConfig] = None
    ) -> AccessResponse:
        """Authentifie une demande d'accès."""
        
        self.total_requests += 1
        
        try:
            # Vérifier blacklist IP
            if access_request.client_ip in self.blacklisted_ips:
                self.denied_count += 1
                return self._create_denied_response(
                    access_request,
                    "IP blacklisted"
                )
            
            # Vérifier utilisateur suspendu
            if access_request.user_id in self.suspended_users:
                self.denied_count += 1
                return AccessResponse(
                    response_id=str(uuid4()),
                    request_id=access_request.request_id,
                    status=AccessStatus.SUSPENDED,
                    error_message="User suspended"
                )
            
            # Rate limiting
            if gateway_config and gateway_config.enable_rate_limiting:
                rate_check = await self._check_rate_limit(
                    access_request.user_id,
                    gateway_config.rate_limit_per_minute
                )
                
                if not rate_check["allowed"]:
                    self.rate_limited_count += 1
                    return AccessResponse(
                        response_id=str(uuid4()),
                        request_id=access_request.request_id,
                        status=AccessStatus.RATE_LIMITED,
                        error_message="Rate limit exceeded",
                        retry_after_sec=rate_check["retry_after"]
                    )
            
            # Authentification selon la méthode
            auth_result = await self._verify_credentials(access_request)
            
            if not auth_result["valid"]:
                self.denied_count += 1
                return self._create_denied_response(
                    access_request,
                    auth_result["error"]
                )
            
            # Générer token sécurisé
            security_level = gateway_config.security_level if gateway_config else SecurityLevel.AUTHENTICATED
            
            token = await self._generate_token(
                access_request.user_id,
                access_request.stream_id,
                security_level,
                auth_result.get("permissions", [])
            )
            
            self.allowed_count += 1
            
            self.logger.info(
                f"Access granted: user={access_request.user_id}, "
                f"stream={access_request.stream_id}, "
                f"level={security_level.value}"
            )
            
            return AccessResponse(
                response_id=str(uuid4()),
                request_id=access_request.request_id,
                status=AccessStatus.ALLOWED,
                token=token
            )
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            self.denied_count += 1
            return self._create_denied_response(access_request, str(e))

    async def _verify_credentials(self, request: AccessRequest) -> Dict[str, Any]:
        """Vérifie les credentials selon la méthode d'auth."""
        
        if request.auth_method == AuthenticationMethod.JWT:
            return await self._verify_jwt(request.credentials.get("token", ""))
        
        elif request.auth_method == AuthenticationMethod.API_KEY:
            return await self._verify_api_key(request.credentials.get("api_key", ""))
        
        elif request.auth_method == AuthenticationMethod.OAUTH2:
            return await self._verify_oauth2(request.credentials.get("access_token", ""))
        
        elif request.auth_method == AuthenticationMethod.CERTIFICATE:
            return await self._verify_certificate(request.credentials.get("cert", ""))
        
        return {"valid": False, "error": "Unknown auth method"}

    async def _verify_jwt(self, token: str) -> Dict[str, Any]:
        """Vérifie un JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Vérifier expiration
            exp = payload.get("exp", 0)
            if datetime.fromtimestamp(exp) < datetime.utcnow():
                return {"valid": False, "error": "Token expired"}
            
            return {
                "valid": True,
                "permissions": payload.get("permissions", []),
                "user_id": payload.get("sub")
            }
            
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": f"Invalid JWT: {e}"}

    async def _verify_api_key(self, api_key: str) -> Dict[str, Any]:
        """Vérifie une clé API."""
        if api_key in self.api_keys:
            return {
                "valid": True,
                "permissions": ["stream:read"],
                "user_id": self.api_keys[api_key]
            }
        return {"valid": False, "error": "Invalid API key"}

    async def _verify_oauth2(self, access_token: str) -> Dict[str, Any]:
        """Vérifie un token OAuth2."""
        # En production: validation contre serveur OAuth2
        # Simulation: vérification format
        if len(access_token) >= 32:
            return {
                "valid": True,
                "permissions": ["stream:read", "stream:write"]
            }
        return {"valid": False, "error": "Invalid OAuth2 token"}

    async def _verify_certificate(self, cert: str) -> Dict[str, Any]:
        """Vérifie un certificat client."""
        # En production: validation X.509 certificate
        # Simulation
        if cert:
            return {
                "valid": True,
                "permissions": ["stream:read", "stream:write", "admin"]
            }
        return {"valid": False, "error": "Invalid certificate"}

    async def _check_rate_limit(self, user_id: str, limit_per_minute: int) -> Dict[str, Any]:
        """Vérifie le rate limit."""
        now = datetime.utcnow()
        
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = RateLimitInfo(user_id=user_id)
        
        rate_info = self.rate_limits[user_id]
        
        # Réinitialiser si nouvelle fenêtre
        window_elapsed = (now - rate_info.window_start).total_seconds()
        if window_elapsed >= 60:
            rate_info.request_count = 0
            rate_info.window_start = now
            rate_info.is_limited = False
        
        # Incrémenter compteur
        rate_info.request_count += 1
        
        # Vérifier limite
        if rate_info.request_count > limit_per_minute:
            rate_info.is_limited = True
            retry_after = int(60 - window_elapsed)
            return {"allowed": False, "retry_after": retry_after}
        
        return {"allowed": True}

    async def _generate_token(
        self,
        user_id: str,
        stream_id: str,
        security_level: SecurityLevel,
        permissions: List[str]
    ) -> StreamingToken:
        """Génère un token de streaming sécurisé."""
        
        token_id = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=2)
        
        # Générer JWT
        jwt_payload = {
            "sub": user_id,
            "stream_id": stream_id,
            "security_level": security_level.value,
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": expires_at,
            "jti": token_id
        }
        
        jwt_token = jwt.encode(jwt_payload, self.jwt_secret, algorithm="HS256")
        
        token = StreamingToken(
            token_id=token_id,
            user_id=user_id,
            stream_id=stream_id,
            security_level=security_level,
            expires_at=expires_at,
            permissions=permissions,
            jwt_token=jwt_token
        )
        
        self.active_tokens[token_id] = token
        
        return token

    async def validate_token(self, token_str: str) -> Optional[StreamingToken]:
        """Valide un token de streaming."""
        try:
            payload = jwt.decode(token_str, self.jwt_secret, algorithms=["HS256"])
            token_id = payload.get("jti")
            
            if token_id in self.active_tokens:
                token = self.active_tokens[token_id]
                
                if token.expires_at > datetime.utcnow():
                    return token
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Token validation failed: {e}")
            return None

    async def revoke_token(self, token_id: str) -> bool:
        """Révoque un token."""
        if token_id in self.active_tokens:
            del self.active_tokens[token_id]
            self.logger.info(f"Token revoked: {token_id}")
            return True
        return False

    async def blacklist_ip(self, ip: str, reason: str) -> None:
        """Blacklist une adresse IP."""
        self.blacklisted_ips.add(ip)
        self.logger.warning(f"IP blacklisted: {ip}, reason={reason}")

    async def suspend_user(self, user_id: str, reason: str) -> None:
        """Suspend un utilisateur."""
        self.suspended_users.add(user_id)
        
        # Révoquer tous les tokens de l'utilisateur
        tokens_to_revoke = [
            tid for tid, token in self.active_tokens.items()
            if token.user_id == user_id
        ]
        
        for tid in tokens_to_revoke:
            await self.revoke_token(tid)
        
        self.logger.warning(
            f"User suspended: {user_id}, reason={reason}, "
            f"tokens_revoked={len(tokens_to_revoke)}"
        )

    def register_api_key(self, user_id: str) -> str:
        """Génère et enregistre une clé API."""
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        self.api_keys[api_key] = user_id
        self.logger.info(f"API key registered for user: {user_id}")
        return api_key

    async def _cleanup_expired_tokens(self) -> None:
        """Nettoyage périodique des tokens expirés."""
        while True:
            try:
                await asyncio.sleep(300)  # Toutes les 5 minutes
                
                now = datetime.utcnow()
                expired = [
                    tid for tid, token in self.active_tokens.items()
                    if token.expires_at < now
                ]
                
                for tid in expired:
                    del self.active_tokens[tid]
                
                if expired:
                    self.logger.info(f"Cleanup: {len(expired)} tokens expired")
                    
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

    def _create_denied_response(
        self,
        request: AccessRequest,
        error_message: str
    ) -> AccessResponse:
        """Crée une réponse de refus."""
        return AccessResponse(
            response_id=str(uuid4()),
            request_id=request.request_id,
            status=AccessStatus.DENIED,
            error_message=error_message
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Statistiques du gateway."""
        success_rate = (self.allowed_count / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            "total_requests": self.total_requests,
            "allowed": self.allowed_count,
            "denied": self.denied_count,
            "rate_limited": self.rate_limited_count,
            "success_rate_pct": round(success_rate, 2),
            "active_tokens": len(self.active_tokens),
            "blacklisted_ips": len(self.blacklisted_ips),
            "suspended_users": len(self.suspended_users)
        }


def create_securestreaming_gateway(config: Optional[Dict[str, Any]] = None) -> SecureStreamingGateway:
    return SecureStreamingGateway(config=config)


create_secure_streaming_gateway = create_securestreaming_gateway


__all__ = [
    "SecureStreamingGateway",
    "SecurityLevel",
    "AuthenticationMethod",
    "AccessStatus",
    "AccessType",
    "EncryptionProtocol",
    "GatewayConfig",
    "StreamingToken",
    "AccessRequest",
    "SecurityRequest",
    "AccessResponse",
    "RateLimitInfo",
    "SecureStreamingRecord",
    "SecureStreamingGatewayRecord",
    "create_securestreaming_gateway",
    "create_secure_streaming_gateway"
]
