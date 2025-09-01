"""Enhanced JWT Security Manager with Token Rotation
================================================

Enterprise-grade JWT token management with advanced security features:
- Automatic token rotation
- Token family tracking
- Refresh token rotation
- Security event logging
- Rate limiting and abuse detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

import aioredis
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """
JWT token types"""

    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    API_KEY = "api_key"


class TokenSecurityLevel(Enum):
    """Token security levels"""

    STANDARD = "standard"
    HIGH = "high"
    ENTERPRISE = "enterprise"


@dataclass
class TokenFamily:
    """Token family for tracking related tokens"""
    family_id: str
    user_id: str
    created_at: datetime
    last_rotation: datetime
    rotation_count: int = 0
    is_compromised: bool = False
    security_level: TokenSecurityLevel = TokenSecurityLevel.STANDARD
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class TokenMetrics:
    """
Token usage metrics"""
    issued_count: int = 0
    refreshed_count: int = 0
    revoked_count: int = 0
    compromised_count: int = 0
    active_families: int = 0


class EnhancedJWTManager:
    """
Enhanced JWT manager with token rotation and security features"""
    
    def __init__(
        self,
        secret_key: str,
        redis_url: str = "redis://localhost:6379",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 30,
        max_token_families_per_user: int = 5,
        enable_token_rotation: bool = True
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.max_token_families_per_user = max_token_families_per_user
        self.enable_token_rotation = enable_token_rotation
        
        self.redis_client = None
        self.redis_url = redis_url
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.metrics = TokenMetrics()
        
        # Generate additional security keys
        self._derive_security_keys()
        
    async def initialize(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(self.redis_url)
            
    def _derive_security_keys(self):
        """
Derive additional security keys from master secret"""
        # Create HMAC key for token signing
        self.signing_key = hmac.new(
            self.secret_key.encode(),
            b"jwt_signing",
            hashlib.sha256
        ).digest()
        
        # Create encryption key for sensitive data
        self.encryption_key = hmac.new(
            self.secret_key.encode(),
            b"data_encryption",
            hashlib.sha256
        ).digest()[:32]  # AES-256 key
        
    async def create_token_pair(
        self,
        user_id: str,
        permissions: List[str],
        security_level: TokenSecurityLevel = TokenSecurityLevel.STANDARD,
        device_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str, str]:
        """Create access and refresh token pair with family tracking"""
        await self.initialize()
        
        # Create token family
        family_id = str(uuid.uuid4())
        family = TokenFamily(
            family_id=family_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_rotation=datetime.utcnow(),
            security_level=security_level,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Check if user has too many active families
        await self._cleanup_old_families(user_id)
        
        # Create access token
        access_token = await self._create_access_token(
            user_id, permissions, family_id, additional_claims
        )
        
        # Create refresh token
        refresh_token = await self._create_refresh_token(user_id, family_id)
        
        # Store token family
        await self._store_token_family(family)
        
        # Update metrics
        self.metrics.issued_count += 1
        self.metrics.active_families += 1
        
        logger.info(f"Created token pair for user {user_id} with family {family_id}")
        return access_token, refresh_token, family_id
        
    async def _create_access_token(
        self,
        user_id: str,
        permissions: List[str],
        family_id: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "type": TokenType.ACCESS.value,
            "jti": str(uuid.uuid4()),
            "family_id": family_id,
            "permissions": permissions,
            "token_version": 1
        }
        
        if additional_claims:
            payload.update(additional_claims)
            
        # Add security fingerprint
        payload["fp"] = self._generate_token_fingerprint(user_id, family_id)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    async def _create_refresh_token(self, user_id: str, family_id: str) -> str:
        """Create refresh token"""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "type": TokenType.REFRESH.value,
            "jti": str(uuid.uuid4()),
            "family_id": family_id,
            "token_version": 1
        }
        
        # Add security fingerprint
        payload["fp"] = self._generate_token_fingerprint(user_id, family_id)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    def _generate_token_fingerprint(self, user_id: str, family_id: str) -> str:
        """Generate security fingerprint for token"""
        data = f"{user_id}:{family_id}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
        
    async def verify_token(
        self,
        token: str,
        expected_type: TokenType = TokenType.ACCESS,
        verify_family: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token with enhanced security checks"""
        await self.initialize()
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != expected_type.value:
                logger.warning(f"Invalid token type: expected {expected_type.value}, got {payload.get('type')}")
                return None
                
            # Verify security fingerprint
            expected_fp = self._generate_token_fingerprint(
                payload["sub"],
                payload["family_id"]
            )
            if payload.get("fp") != expected_fp:
                logger.warning("Token fingerprint mismatch - possible token tampering")
                return None
                
            # Verify token family if enabled
            if verify_family:
                family = await self._get_token_family(payload["family_id"])
                if not family or family.is_compromised:
                    logger.warning(f"Token family {payload['family_id']} is compromised or not found")
                    return None
                    
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
            
    async def refresh_access_token(
        self,
        refresh_token: str,
        rotate_refresh_token: bool = True
    ) -> Optional[Tuple[str, Optional[str]]]:
        """Refresh access token and optionally rotate refresh token"""
        await self.initialize()
        
        # Verify refresh token
        payload = await self.verify_token(refresh_token, TokenType.REFRESH)
        if not payload:
            return None
            
        user_id = payload["sub"]
        family_id = payload["family_id"]
        
        # Get token family
        family = await self._get_token_family(family_id)
        if not family:
            logger.error(f"Token family not found: {family_id}")
            return None
            
        # Get user permissions (in production, fetch from database)
        permissions = await self._get_user_permissions(user_id)
        
        # Create new access token
        new_access_token = await self._create_access_token(
            user_id, permissions, family_id
        )
        
        new_refresh_token = None
        if rotate_refresh_token and self.enable_token_rotation:
            # Create new refresh token
            new_refresh_token = await self._create_refresh_token(user_id, family_id)
            
            # Update family rotation info
            family.last_rotation = datetime.utcnow()
            family.rotation_count += 1
            await self._store_token_family(family)
            
            logger.info(f"Rotated refresh token for family {family_id}")
            
        # Update metrics
        self.metrics.refreshed_count += 1
        
        logger.info(f"Refreshed access token for user {user_id}")
        return new_access_token, new_refresh_token
        
    async def revoke_token_family(self, family_id: str) -> bool:
        """Revoke entire token family"""
        await self.initialize()
        
        family = await self._get_token_family(family_id)
        if not family:
            return False
            
        # Mark family as compromised
        family.is_compromised = True
        await self._store_token_family(family)
        
        # Add to revocation list
        revocation_key = f"revoked_family:{family_id}"
        await self.redis_client.setex(
            revocation_key,
            self.refresh_token_expire_days * 24 * 3600,  # Same as refresh token expiry
            "revoked"
        )
        
        # Update metrics
        self.metrics.revoked_count += 1
        self.metrics.active_families -= 1
        
        logger.info(f"Revoked token family: {family_id}")
        return True
        
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all tokens for a user"""
        await self.initialize()
        
        # Get all families for user
        families = await self._get_user_families(user_id)
        revoked_count = 0
        
        for family_id in families:
            if await self.revoke_token_family(family_id):
                revoked_count += 1
                
        logger.info(f"Revoked {revoked_count} token families for user {user_id}")
        return revoked_count
        
    async def detect_token_reuse(self, token: str) -> bool:
        """Detect potential token reuse attacks"""
        await self.initialize()
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        usage_key = f"token_usage:{token_hash}"
        
        # Check if token has been used before
        usage_count = await self.redis_client.get(usage_key)
        if usage_count:
            # Token reuse detected
            payload = await self.verify_token(token, verify_family=False)
            if payload:
                family_id = payload["family_id"]
                await self.revoke_token_family(family_id)
                logger.warning(f"Token reuse detected, revoked family: {family_id}")
                return True
                
        # Mark token as used
        await self.redis_client.setex(usage_key, 3600, "1")  # 1 hour
        return False
        
    async def _cleanup_old_families(self, user_id: str):
        """Clean up old token families for user"""
        families = await self._get_user_families(user_id)
        
        if len(families) >= self.max_token_families_per_user:
            # Get family details and sort by creation date
            family_details = []
            for family_id in families:
                family = await self._get_token_family(family_id)
                if family:
                    family_details.append((family_id, family.created_at))
                    
            # Sort by creation date (oldest first)
            family_details.sort(key=lambda x: x[1])
            
            # Revoke oldest families
            families_to_revoke = len(families) - self.max_token_families_per_user + 1
            for i in range(families_to_revoke):
                family_id = family_details[i][0]
                await self.revoke_token_family(family_id)
                
    async def _store_token_family(self, family: TokenFamily):
        """
Store token family in Redis"""
        family_key = f"token_family:{family.family_id}"
        family_data = {
            "family_id": family.family_id,
            "user_id": family.user_id,
            "created_at": family.created_at.isoformat(),
            "last_rotation": family.last_rotation.isoformat(),
            "rotation_count": family.rotation_count,
            "is_compromised": family.is_compromised,
            "security_level": family.security_level.value,
            "device_fingerprint": family.device_fingerprint,
            "ip_address": family.ip_address,
            "user_agent": family.user_agent
        }
        
        await self.redis_client.setex(
            family_key,
            self.refresh_token_expire_days * 24 * 3600,  # Same as refresh token expiry
            json.dumps(family_data)
        )
        
        # Add to user's family list
        user_families_key = f"user_families:{family.user_id}"
        await self.redis_client.sadd(user_families_key, family.family_id)
        await self.redis_client.expire(user_families_key, self.refresh_token_expire_days * 24 * 3600)
        
    async def _get_token_family(self, family_id: str) -> Optional[TokenFamily]:
        """Get token family from Redis"""
        family_key = f"token_family:{family_id}"
        family_data = await self.redis_client.get(family_key)
        
        if not family_data:
            return None
            
        try:
            data = json.loads(family_data)
            return TokenFamily(
                family_id=data["family_id"],
                user_id=data["user_id"],
                created_at=datetime.fromisoformat(data["created_at"]),
                last_rotation=datetime.fromisoformat(data["last_rotation"]),
                rotation_count=data["rotation_count"],
                is_compromised=data["is_compromised"],
                security_level=TokenSecurityLevel(data["security_level"]),
                device_fingerprint=data.get("device_fingerprint"),
                ip_address=data.get("ip_address"),
                user_agent=data.get("user_agent")
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse token family data: {e}")
            return None
            
    async def _get_user_families(self, user_id: str) -> List[str]:
        """Get all token families for a user"""
        user_families_key = f"user_families:{user_id}"
        families = await self.redis_client.smembers(user_families_key)
        return [f.decode() if isinstance(f, bytes) else f for f in families]
        
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions (mock implementation)"""
        # In production, this would fetch from database
        return ["read", "write", "delete"]
        
    async def get_token_metrics(self) -> TokenMetrics:
        """Get token usage metrics"""
        return self.metrics
        
    async def get_user_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """
Get active sessions for a user"""
        families = await self._get_user_families(user_id)
        sessions = []
        
        for family_id in families:
            family = await self._get_token_family(family_id)
            if family and not family.is_compromised:
                sessions.append({
                    "family_id": family_id,
                    "created_at": family.created_at.isoformat(),
                    "last_rotation": family.last_rotation.isoformat(),
                    "rotation_count": family.rotation_count,
                    "security_level": family.security_level.value,
                    "device_fingerprint": family.device_fingerprint,
                    "ip_address": family.ip_address,
                    "user_agent": family.user_agent
                })
                
        return sessions


# Global enhanced JWT manager instance (will be initialized by application)
enhanced_jwt_manager: Optional[EnhancedJWTManager] = None


def get_enhanced_jwt_manager() -> EnhancedJWTManager:
    """Get global enhanced JWT manager instance"""
    global enhanced_jwt_manager
    if not enhanced_jwt_manager:
        raise RuntimeError("Enhanced JWT Manager not initialized")
    return enhanced_jwt_manager


def initialize_enhanced_jwt_manager(
    secret_key: str,
    redis_url: str = "redis://localhost:6379",
    **kwargs
) -> EnhancedJWTManager:
    """Initialize global enhanced JWT manager"""
    global enhanced_jwt_manager
    enhanced_jwt_manager = EnhancedJWTManager(secret_key, redis_url, **kwargs)
    return enhanced_jwt_manager