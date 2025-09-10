"""
Ainflue Core Security - JWT Manager Core
========================================

Enterprise-grade JWT (JSON Web Token) management system with advanced security
features, token lifecycle management, refresh token rotation, and multi-algorithm
support for secure authentication and authorization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

# Third-party imports (with fallbacks)
try:
    import jwt
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)

class TokenType(str, Enum):
    """JWT token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    RESET = "reset"
    VERIFICATION = "verification"
    API = "api"

class TokenAlgorithm(str, Enum):
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

class TokenStatus(str, Enum):
    """Token status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"
    BLACKLISTED = "blacklisted"

@dataclass
class TokenClaims:
    """JWT token claims"""
    user_id: str
    token_type: TokenType
    issued_at: datetime
    expires_at: datetime
    not_before: Optional[datetime] = None
    issuer: str = "ainflue-core"
    audience: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    jti: str = field(default_factory=lambda: str(uuid.uuid4()))
    scopes: List[str] = field(default_factory=list)
    custom_claims: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenPair:
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    refresh_expires_in: int = 86400
    scope: str = ""

@dataclass
class TokenInfo:
    """Token information and metadata"""
    token_id: str
    user_id: str
    token_type: TokenType
    status: TokenStatus
    created_at: datetime
    expires_at: datetime
    last_used: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_fingerprint: Optional[str] = None
    refresh_count: int = 0

@dataclass
class JWTMetrics:
    """JWT management metrics"""
    tokens_issued: int = 0
    tokens_verified: int = 0
    tokens_revoked: int = 0
    tokens_refreshed: int = 0
    verification_failures: int = 0
    expired_tokens: int = 0
    blacklisted_tokens: int = 0

class JWTManagerCore:
    """Enterprise JWT management system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize JWT manager core"""
        self.level = level
        self.metrics = JWTMetrics()
        
        # Token storage
        self.active_tokens: Dict[str, TokenInfo] = {}
        self.blacklist: set = set()
        self.refresh_tokens: Dict[str, str] = {}  # refresh_token -> access_token_id
        
        # Security configurations
        self.default_algorithm = TokenAlgorithm.HS256
        self.access_token_ttl = 3600  # 1 hour
        self.refresh_token_ttl = 86400 * 7  # 7 days
        self.max_refresh_count = 10
        
        # Secrets and keys
        self.signing_secret = self._generate_secret()
        self.refresh_secret = self._generate_secret()
        self.private_key = None
        self.public_key = None
        
        # Rate limiting
        self.rate_limits = {
            "token_generation": {"count": 100, "window": 3600},
            "token_verification": {"count": 1000, "window": 3600},
            "token_refresh": {"count": 50, "window": 3600}
        }
        self.rate_limit_storage: Dict[str, Dict[str, Any]] = {}
        
        # Initialize cryptographic keys if available
        if CRYPTO_AVAILABLE and level == "enterprise":
            self._initialize_rsa_keys()
        
        logger.info(f"🔑 JWT Manager Core initialized - Level: {level}")

    def _generate_secret(self) -> str:
        """Generate cryptographically secure secret"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')

    def _initialize_rsa_keys(self):
        """Initialize RSA key pair for asymmetric signing"""
        try:
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            self.private_key = private_key
            self.public_key = private_key.public_key()
            
            # Use RS256 as default for enterprise
            self.default_algorithm = TokenAlgorithm.RS256
            
            logger.info("🔐 RSA key pair initialized for JWT signing")
            
        except Exception as e:
            logger.error(f"Failed to initialize RSA keys: {str(e)}")

    async def generate_token_pair(
        self,
        user_id: str,
        scopes: Optional[List[str]] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        client_info: Optional[Dict[str, str]] = None
    ) -> TokenPair:
        """Generate access and refresh token pair"""
        
        # Rate limiting check
        if not await self._check_rate_limit("token_generation", user_id):
            raise ValueError("Rate limit exceeded for token generation")
        
        now = datetime.utcnow()
        
        # Generate access token
        access_claims = TokenClaims(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            issued_at=now,
            expires_at=now + timedelta(seconds=self.access_token_ttl),
            scopes=scopes or [],
            custom_claims=custom_claims or {}
        )
        
        access_token = await self._create_token(access_claims)
        
        # Generate refresh token
        refresh_claims = TokenClaims(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            issued_at=now,
            expires_at=now + timedelta(seconds=self.refresh_token_ttl),
            custom_claims={"access_token_id": access_claims.jti}
        )
        
        refresh_token = await self._create_token(refresh_claims, use_refresh_secret=True)
        
        # Store token info
        token_info = TokenInfo(
            token_id=access_claims.jti,
            user_id=user_id,
            token_type=TokenType.ACCESS,
            status=TokenStatus.ACTIVE,
            created_at=now,
            expires_at=access_claims.expires_at,
            ip_address=client_info.get("ip_address") if client_info else None,
            user_agent=client_info.get("user_agent") if client_info else None,
            device_fingerprint=client_info.get("device_fingerprint") if client_info else None
        )
        
        self.active_tokens[access_claims.jti] = token_info
        self.refresh_tokens[refresh_token] = access_claims.jti
        
        # Update metrics
        self.metrics.tokens_issued += 2
        
        # Create token pair
        token_pair = TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_ttl,
            refresh_expires_in=self.refresh_token_ttl,
            scope=" ".join(scopes or [])
        )
        
        logger.debug(f"Generated token pair for user {user_id}")
        return token_pair

    async def _create_token(
        self,
        claims: TokenClaims,
        algorithm: Optional[TokenAlgorithm] = None,
        use_refresh_secret: bool = False
    ) -> str:
        """Create JWT token from claims"""
        
        if not CRYPTO_AVAILABLE:
            raise ImportError("JWT library not available")
        
        # Prepare payload
        payload = {
            "sub": claims.user_id,
            "typ": claims.token_type.value,
            "iat": int(claims.issued_at.timestamp()),
            "exp": int(claims.expires_at.timestamp()),
            "iss": claims.issuer,
            "jti": claims.jti
        }
        
        # Add optional claims
        if claims.not_before:
            payload["nbf"] = int(claims.not_before.timestamp())
        
        if claims.audience:
            payload["aud"] = claims.audience
        
        if claims.subject:
            payload["sub"] = claims.subject
        
        if claims.scopes:
            payload["scope"] = " ".join(claims.scopes)
        
        # Add custom claims
        payload.update(claims.custom_claims)
        
        # Select algorithm and key
        alg = algorithm or self.default_algorithm
        
        if alg in [TokenAlgorithm.HS256, TokenAlgorithm.HS384, TokenAlgorithm.HS512]:
            # HMAC algorithms
            secret = self.refresh_secret if use_refresh_secret else self.signing_secret
            token = jwt.encode(payload, secret, algorithm=alg.value)
        elif alg in [TokenAlgorithm.RS256, TokenAlgorithm.RS384, TokenAlgorithm.RS512]:
            # RSA algorithms
            if not self.private_key:
                raise ValueError("RSA private key not available")
            
            # Convert private key to PEM format
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            token = jwt.encode(payload, private_pem, algorithm=alg.value)
        else:
            raise ValueError(f"Unsupported algorithm: {alg.value}")
        
        return token

    async def verify_token(
        self,
        token: str,
        token_type: Optional[TokenType] = None,
        verify_expiration: bool = True
    ) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        
        # Rate limiting check
        if not await self._check_rate_limit("token_verification", "global"):
            raise ValueError("Rate limit exceeded for token verification")
        
        try:
            if not CRYPTO_AVAILABLE:
                raise ImportError("JWT library not available")
            
            # Decode token header to get algorithm
            unverified_header = jwt.get_unverified_header(token)
            algorithm = unverified_header.get("alg", self.default_algorithm.value)
            
            # Select appropriate key/secret
            if algorithm in ["HS256", "HS384", "HS512"]:
                key = self.signing_secret
            elif algorithm in ["RS256", "RS384", "RS512"]:
                if not self.public_key:
                    raise ValueError("RSA public key not available")
                
                # Convert public key to PEM format
                key = self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Verify and decode token
            options = {"verify_exp": verify_expiration}
            payload = jwt.decode(token, key, algorithms=[algorithm], options=options)
            
            # Check token type if specified
            if token_type and payload.get("typ") != token_type.value:
                raise ValueError(f"Invalid token type: expected {token_type.value}")
            
            # Check if token is blacklisted
            token_id = payload.get("jti")
            if token_id and token_id in self.blacklist:
                raise ValueError("Token is blacklisted")
            
            # Update token usage
            if token_id and token_id in self.active_tokens:
                self.active_tokens[token_id].last_used = datetime.utcnow()
            
            # Update metrics
            self.metrics.tokens_verified += 1
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.metrics.expired_tokens += 1
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            self.metrics.verification_failures += 1
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            self.metrics.verification_failures += 1
            raise ValueError(f"Token verification failed: {str(e)}")

    async def refresh_token(
        self,
        refresh_token: str,
        client_info: Optional[Dict[str, str]] = None
    ) -> TokenPair:
        """Refresh access token using refresh token"""
        
        # Rate limiting check
        if not await self._check_rate_limit("token_refresh", "global"):
            raise ValueError("Rate limit exceeded for token refresh")
        
        try:
            # Verify refresh token
            payload = await self.verify_token(refresh_token, TokenType.REFRESH)
            
            user_id = payload.get("sub")
            access_token_id = payload.get("access_token_id")
            
            # Check if refresh token exists in our records
            if refresh_token not in self.refresh_tokens:
                raise ValueError("Refresh token not found")
            
            # Get original access token info
            if access_token_id not in self.active_tokens:
                raise ValueError("Associated access token not found")
            
            token_info = self.active_tokens[access_token_id]
            
            # Check refresh count limit
            if token_info.refresh_count >= self.max_refresh_count:
                # Revoke old tokens
                await self.revoke_token(access_token_id)
                await self.revoke_refresh_token(refresh_token)
                raise ValueError("Maximum refresh count exceeded")
            
            # Revoke old access token
            await self.revoke_token(access_token_id)
            
            # Generate new token pair
            new_token_pair = await self.generate_token_pair(
                user_id=user_id,
                scopes=payload.get("scope", "").split() if payload.get("scope") else [],
                client_info=client_info
            )
            
            # Update refresh count
            new_access_token_id = await self._get_token_id(new_token_pair.access_token)
            if new_access_token_id and new_access_token_id in self.active_tokens:
                self.active_tokens[new_access_token_id].refresh_count = token_info.refresh_count + 1
            
            # Revoke old refresh token
            await self.revoke_refresh_token(refresh_token)
            
            # Update metrics
            self.metrics.tokens_refreshed += 1
            
            logger.debug(f"Refreshed token for user {user_id}")
            return new_token_pair
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise

    async def _get_token_id(self, token: str) -> Optional[str]:
        """Extract token ID from JWT without verification"""
        try:
            if not CRYPTO_AVAILABLE:
                return None
            
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            return unverified_payload.get("jti")
        except Exception:
            return None

    async def revoke_token(self, token_id: str):
        """Revoke specific token by ID"""
        
        if token_id in self.active_tokens:
            self.active_tokens[token_id].status = TokenStatus.REVOKED
            self.blacklist.add(token_id)
            self.metrics.tokens_revoked += 1
            
            logger.debug(f"Revoked token {token_id}")

    async def revoke_refresh_token(self, refresh_token: str):
        """Revoke refresh token"""
        
        if refresh_token in self.refresh_tokens:
            access_token_id = self.refresh_tokens.pop(refresh_token)
            # Also revoke associated access token
            await self.revoke_token(access_token_id)

    async def revoke_all_user_tokens(self, user_id: str):
        """Revoke all tokens for a specific user"""
        
        revoked_count = 0
        
        # Revoke access tokens
        for token_id, token_info in self.active_tokens.items():
            if token_info.user_id == user_id and token_info.status == TokenStatus.ACTIVE:
                await self.revoke_token(token_id)
                revoked_count += 1
        
        # Revoke refresh tokens
        refresh_tokens_to_remove = []
        for refresh_token, access_token_id in self.refresh_tokens.items():
            if access_token_id in self.active_tokens:
                token_info = self.active_tokens[access_token_id]
                if token_info.user_id == user_id:
                    refresh_tokens_to_remove.append(refresh_token)
        
        for refresh_token in refresh_tokens_to_remove:
            self.refresh_tokens.pop(refresh_token, None)
        
        logger.info(f"Revoked {revoked_count} tokens for user {user_id}")

    async def validate_token_scopes(self, token: str, required_scopes: List[str]) -> bool:
        """Validate if token has required scopes"""
        
        try:
            payload = await self.verify_token(token)
            token_scopes = payload.get("scope", "").split()
            
            # Check if all required scopes are present
            return all(scope in token_scopes for scope in required_scopes)
            
        except Exception:
            return False

    async def get_token_info(self, token_id: str) -> Optional[TokenInfo]:
        """Get token information by ID"""
        return self.active_tokens.get(token_id)

    async def list_user_tokens(self, user_id: str) -> List[TokenInfo]:
        """List all active tokens for a user"""
        
        user_tokens = []
        for token_info in self.active_tokens.values():
            if (token_info.user_id == user_id and 
                token_info.status == TokenStatus.ACTIVE):
                user_tokens.append(token_info)
        
        return user_tokens

    async def cleanup_expired_tokens(self):
        """Clean up expired tokens from storage"""
        
        now = datetime.utcnow()
        expired_tokens = []
        
        for token_id, token_info in self.active_tokens.items():
            if (token_info.expires_at < now and 
                token_info.status != TokenStatus.EXPIRED):
                expired_tokens.append(token_id)
        
        # Mark tokens as expired
        for token_id in expired_tokens:
            self.active_tokens[token_id].status = TokenStatus.EXPIRED
            self.blacklist.add(token_id)
        
        # Clean up refresh tokens
        refresh_tokens_to_remove = []
        for refresh_token, access_token_id in self.refresh_tokens.items():
            if access_token_id in expired_tokens:
                refresh_tokens_to_remove.append(refresh_token)
        
        for refresh_token in refresh_tokens_to_remove:
            self.refresh_tokens.pop(refresh_token, None)
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")

    async def _check_rate_limit(self, operation: str, identifier: str) -> bool:
        """Check rate limit for operation"""
        
        if operation not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[operation]
        window = limit_config["window"]
        max_count = limit_config["count"]
        
        now = time.time()
        key = f"{operation}:{identifier}"
        
        if key not in self.rate_limit_storage:
            self.rate_limit_storage[key] = {"count": 0, "window_start": now}
        
        storage = self.rate_limit_storage[key]
        
        # Reset window if expired
        if now - storage["window_start"] > window:
            storage["count"] = 0
            storage["window_start"] = now
        
        # Check limit
        if storage["count"] >= max_count:
            return False
        
        storage["count"] += 1
        return True

    async def generate_api_token(
        self,
        user_id: str,
        name: str,
        scopes: List[str],
        expires_in: Optional[int] = None
    ) -> str:
        """Generate long-lived API token"""
        
        now = datetime.utcnow()
        expiry = now + timedelta(seconds=expires_in) if expires_in else now + timedelta(days=365)
        
        claims = TokenClaims(
            user_id=user_id,
            token_type=TokenType.API,
            issued_at=now,
            expires_at=expiry,
            scopes=scopes,
            custom_claims={"name": name}
        )
        
        api_token = await self._create_token(claims)
        
        # Store token info
        token_info = TokenInfo(
            token_id=claims.jti,
            user_id=user_id,
            token_type=TokenType.API,
            status=TokenStatus.ACTIVE,
            created_at=now,
            expires_at=expiry
        )
        
        self.active_tokens[claims.jti] = token_info
        self.metrics.tokens_issued += 1
        
        logger.info(f"Generated API token '{name}' for user {user_id}")
        return api_token

    def get_metrics(self) -> JWTMetrics:
        """Get JWT management metrics"""
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for JWT management system"""
        try:
            # Test token generation and verification
            test_user_id = "health_check_user"
            
            # Generate test token pair
            token_pair = await self.generate_token_pair(test_user_id)
            
            # Verify access token
            payload = await self.verify_token(token_pair.access_token)
            
            # Clean up test tokens
            token_id = payload.get("jti")
            if token_id:
                await self.revoke_token(token_id)
            
            await self.revoke_refresh_token(token_pair.refresh_token)
            
            return payload.get("sub") == test_user_id
            
        except Exception as e:
            logger.error(f"JWT health check failed: {str(e)}")
            return False

# Module exports
__all__ = [
    "JWTManagerCore", "TokenType", "TokenAlgorithm", "TokenStatus",
    "TokenClaims", "TokenPair", "TokenInfo", "JWTMetrics"
]

logger.info("🔑 JWT Manager Core module loaded")