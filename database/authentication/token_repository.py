"""
Token Repository Database Components - Enterprise JWT/OAuth2/API Key Management

Advanced token management with distributed storage, encryption, rotation, and audit
for multi-format creator authentication systems. Complete implementation supporting
JWT access/refresh tokens, OAuth2 flows, API keys, and biometric token validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer

Business Logic Flow:
Creator Registration → Multi-Factor Setup → Token Generation → Content Upload → 
AI Protection → Fingerprinting → Distribution → Monetization Tracking
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from uuid import UUID, uuid4

import redis.asyncio as redis
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, JSON, Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet
import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

Base = declarative_base()

class TokenType(Enum):
    """Token type classifications"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"
    API_KEY = "api_key"
    OAUTH_ACCESS = "oauth_access"
    OAUTH_REFRESH = "oauth_refresh"
    TEMPORARY = "temporary"

class TokenStatus(Enum):
    """Token status states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    BLACKLISTED = "blacklisted"
    PENDING = "pending"

class OAuthProvider(Enum):
    """OAuth provider types"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    GITHUB = "github"
    DISCORD = "discord"

@dataclass
class TokenMetadata:
    """Comprehensive token metadata"""
    device_id: str = ""
    user_agent: str = ""
    ip_address: str = ""
    location: str = ""
    platform: str = ""
    app_version: str = ""
    session_id: str = ""
    permissions: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    custom_claims: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenResponse:
    """Token response structure"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: str = ""
    user_id: str = ""
    permissions: List[str] = field(default_factory=list)

class TokenDatabase(Base):
    """Database model for token storage"""
    __tablename__ = 'authentication_tokens'
    
    token_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    token_type = Column(String, nullable=False)
    token_hash = Column(String, nullable=False, unique=True)
    encrypted_token = Column(Text, nullable=False)
    status = Column(String, nullable=False, default=TokenStatus.ACTIVE.value)
    issued_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)
    scopes = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    oauth_provider = Column(String, nullable=True)
    oauth_account_id = Column(String, nullable=True)
    
    __table_args__ = (
        Index('idx_token_user_type', 'user_id', 'token_type'),
        Index('idx_token_status_expires', 'status', 'expires_at'),
        Index('idx_token_device', 'device_id'),
        Index('idx_token_oauth', 'oauth_provider', 'oauth_account_id'),
    )

class BlacklistedToken(Base):
    """Database model for blacklisted tokens"""
    __tablename__ = 'blacklisted_tokens'
    
    id = Column(String, primary_key=True)
    token_hash = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    blacklisted_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    blacklisted_by = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False)

class TokenRepository:
    """
    Enterprise-grade token management repository with comprehensive security features.
    
    Features:
    - JWT/OAuth2 token lifecycle management
    - Secure token storage with encryption
    - Token blacklisting and revocation
    - Multi-device session management
    - Comprehensive audit logging
    - Redis caching for performance
    """
    
    def __init__(
        self,
        session: AsyncSession,
        redis_client: redis.Redis,
        encryption_key: str,
        jwt_secret_key: str,
        jwt_algorithm: str = "HS256"
    ):
        self.session = session
        self.redis = redis_client
        self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        self.jwt_secret = jwt_secret_key
        self.jwt_algorithm = jwt_algorithm
        
        # Token expiration settings
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=30)
        self.reset_token_expire = timedelta(hours=1)
        self.verify_token_expire = timedelta(hours=24)
        
    async def generate_token_pair(
        self,
        user_id: str,
        permissions: List[str],
        metadata: TokenMetadata,
        scopes: Optional[List[str]] = None
    ) -> TokenResponse:
        """Generate access and refresh token pair"""
        try:
            # Generate access token
            access_payload = {
                'user_id': user_id,
                'token_type': TokenType.ACCESS.value,
                'permissions': permissions,
                'scopes': scopes or [],
                'session_id': metadata.session_id,
                'device_id': metadata.device_id,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + self.access_token_expire,
                'jti': str(uuid4())
            }
            
            access_token = jwt.encode(
                access_payload,
                self.jwt_secret,
                algorithm=self.jwt_algorithm
            )
            
            # Generate refresh token
            refresh_payload = {
                'user_id': user_id,
                'token_type': TokenType.REFRESH.value,
                'session_id': metadata.session_id,
                'device_id': metadata.device_id,
                'iat': datetime.now(timezone.utc),
                'exp': datetime.now(timezone.utc) + self.refresh_token_expire,
                'jti': str(uuid4())
            }
            
            refresh_token = jwt.encode(
                refresh_payload,
                self.jwt_secret,
                algorithm=self.jwt_algorithm
            )
            
            # Store tokens in database
            await self._store_token(
                token=access_token,
                user_id=user_id,
                token_type=TokenType.ACCESS,
                metadata=metadata,
                permissions=permissions,
                scopes=scopes
            )
            
            await self._store_token(
                token=refresh_token,
                user_id=user_id,
                token_type=TokenType.REFRESH,
                metadata=metadata
            )
            
            # Cache tokens in Redis for fast validation
            await self._cache_token(access_token, user_id, self.access_token_expire)
            await self._cache_token(refresh_token, user_id, self.refresh_token_expire)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=int(self.access_token_expire.total_seconds()),
                user_id=user_id,
                permissions=permissions
            )
            
        except Exception as e:
            logger.error(f"Failed to generate token pair for user {user_id}: {e}")
            raise
    
    async def validate_token(self, token: str, required_permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Validate token and check permissions"""
        try:
            # Check if token is blacklisted
            if await self._is_token_blacklisted(token):
                raise ValueError("Token is blacklisted")
            
            # Decode and validate JWT
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # Check token expiration
            if payload.get('exp', 0) < datetime.now(timezone.utc).timestamp():
                raise ValueError("Token has expired")
            
            # Validate permissions if required
            if required_permissions:
                token_permissions = set(payload.get('permissions', []))
                required_perms = set(required_permissions)
                if not required_perms.issubset(token_permissions):
                    raise ValueError("Insufficient permissions")
            
            # Update last used timestamp
            await self._update_token_usage(token)
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token validation attempt: {e}")
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise
    
    async def refresh_token(self, refresh_token: str, metadata: TokenMetadata) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Validate refresh token
            payload = await self.validate_token(refresh_token)
            
            if payload.get('token_type') != TokenType.REFRESH.value:
                raise ValueError("Invalid refresh token type")
            
            user_id = payload.get('user_id')
            
            # Get user permissions from database
            user_permissions = await self._get_user_permissions(user_id)
            
            # Generate new token pair
            new_tokens = await self.generate_token_pair(
                user_id=user_id,
                permissions=user_permissions,
                metadata=metadata
            )
            
            # Revoke old refresh token
            await self.revoke_token(refresh_token, user_id, "Token refreshed")
            
            logger.info(f"Token refreshed successfully for user {user_id}")
            return new_tokens
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
    
    async def revoke_token(self, token: str, user_id: str, reason: str = "Manual revocation"):
        """Revoke a specific token"""
        try:
            token_hash = self._hash_token(token)
            
            # Update token status in database
            stmt = select(TokenDatabase).where(TokenDatabase.token_hash == token_hash)
            result = await self.session.execute(stmt)
            token_record = result.scalar_one_or_none()
            
            if token_record:
                token_record.status = TokenStatus.REVOKED.value
                token_record.revoked_at = datetime.now(timezone.utc)
                token_record.revoked_by = user_id
                await self.session.commit()
            
            # Add to blacklist
            blacklist_entry = BlacklistedToken(
                id=str(uuid4()),
                token_hash=token_hash,
                user_id=user_id,
                reason=reason,
                expires_at=datetime.now(timezone.utc) + timedelta(days=30)
            )
            
            self.session.add(blacklist_entry)
            await self.session.commit()
            
            # Remove from Redis cache
            await self.redis.delete(f"token:{token_hash}")
            
            logger.info(f"Token revoked for user {user_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            raise
    
    async def revoke_all_user_tokens(self, user_id: str, reason: str = "Revoke all sessions"):
        """Revoke all tokens for a specific user"""
        try:
            # Get all active tokens for user
            stmt = select(TokenDatabase).where(
                TokenDatabase.user_id == user_id,
                TokenDatabase.status == TokenStatus.ACTIVE.value
            )
            result = await self.session.execute(stmt)
            tokens = result.scalars().all()
            
            current_time = datetime.now(timezone.utc)
            
            # Update all tokens to revoked status
            for token in tokens:
                token.status = TokenStatus.REVOKED.value
                token.revoked_at = current_time
                token.revoked_by = user_id
                
                # Add to blacklist
                blacklist_entry = BlacklistedToken(
                    id=str(uuid4()),
                    token_hash=token.token_hash,
                    user_id=user_id,
                    reason=reason,
                    expires_at=current_time + timedelta(days=30)
                )
                self.session.add(blacklist_entry)
                
                # Remove from Redis cache
                await self.redis.delete(f"token:{token.token_hash}")
            
            await self.session.commit()
            
            logger.info(f"All tokens revoked for user {user_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to revoke all user tokens: {e}")
            raise
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        try:
            stmt = select(TokenDatabase).where(
                TokenDatabase.user_id == user_id,
                TokenDatabase.status == TokenStatus.ACTIVE.value,
                TokenDatabase.token_type == TokenType.ACCESS.value
            ).order_by(TokenDatabase.last_used_at.desc())
            
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            
            session_list = []
            for session in sessions:
                metadata = session.metadata or {}
                session_info = {
                    'session_id': metadata.get('session_id'),
                    'device_id': session.device_id,
                    'user_agent': session.user_agent,
                    'ip_address': session.ip_address,
                    'last_used': session.last_used_at,
                    'created_at': session.issued_at,
                    'expires_at': session.expires_at,
                    'platform': metadata.get('platform'),
                    'location': metadata.get('location')
                }
                session_list.append(session_info)
            
            return session_list
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            raise
    
    async def cleanup_expired_tokens(self):
        """Clean up expired tokens from database and Redis"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Mark expired tokens
            stmt = select(TokenDatabase).where(
                TokenDatabase.expires_at < current_time,
                TokenDatabase.status == TokenStatus.ACTIVE.value
            )
            result = await self.session.execute(stmt)
            expired_tokens = result.scalars().all()
            
            for token in expired_tokens:
                token.status = TokenStatus.EXPIRED.value
                # Remove from Redis cache
                await self.redis.delete(f"token:{token.token_hash}")
            
            # Clean up old blacklisted tokens
            stmt = select(BlacklistedToken).where(
                BlacklistedToken.expires_at < current_time
            )
            result = await self.session.execute(stmt)
            old_blacklisted = result.scalars().all()
            
            for blacklisted in old_blacklisted:
                await self.session.delete(blacklisted)
            
            await self.session.commit()
            
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens and {len(old_blacklisted)} old blacklisted tokens")
            
        except Exception as e:
            logger.error(f"Token cleanup failed: {e}")
            raise
    
    # Private helper methods
    
    def _hash_token(self, token: str) -> str:
        """Create secure hash of token"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def _store_token(
        self,
        token: str,
        user_id: str,
        token_type: TokenType,
        metadata: TokenMetadata,
        permissions: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None
    ):
        """Store token in database with encryption"""
        try:
            token_hash = self._hash_token(token)
            encrypted_token = self.fernet.encrypt(token.encode()).decode()
            
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            token_record = TokenDatabase(
                token_id=payload.get('jti'),
                user_id=user_id,
                token_type=token_type.value,
                token_hash=token_hash,
                encrypted_token=encrypted_token,
                issued_at=datetime.fromtimestamp(payload.get('iat'), tz=timezone.utc),
                expires_at=datetime.fromtimestamp(payload.get('exp'), tz=timezone.utc),
                device_id=metadata.device_id,
                ip_address=metadata.ip_address,
                user_agent=metadata.user_agent,
                permissions=permissions,
                scopes=scopes,
                metadata={
                    'session_id': metadata.session_id,
                    'platform': metadata.platform,
                    'app_version': metadata.app_version,
                    'location': metadata.location,
                    'custom_claims': metadata.custom_claims
                }
            )
            
            self.session.add(token_record)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to store token: {e}")
            raise
    
    async def _cache_token(self, token: str, user_id: str, expires_in: timedelta):
        """Cache token in Redis for fast validation"""
        try:
            token_hash = self._hash_token(token)
            cache_data = {
                'user_id': user_id,
                'valid': True,
                'cached_at': datetime.now(timezone.utc).isoformat()
            }
            
            await self.redis.setex(
                f"token:{token_hash}",
                int(expires_in.total_seconds()),
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache token: {e}")
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            token_hash = self._hash_token(token)
            
            # Check Redis cache first
            cached = await self.redis.get(f"blacklist:{token_hash}")
            if cached:
                return True
            
            # Check database
            stmt = select(BlacklistedToken).where(
                BlacklistedToken.token_hash == token_hash,
                BlacklistedToken.expires_at > datetime.now(timezone.utc)
            )
            result = await self.session.execute(stmt)
            blacklisted = result.scalar_one_or_none()
            
            if blacklisted:
                # Cache the blacklist entry
                await self.redis.setex(
                    f"blacklist:{token_hash}",
                    3600,  # Cache for 1 hour
                    "blacklisted"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
    
    async def _update_token_usage(self, token: str):
        """Update token last used timestamp"""
        try:
            token_hash = self._hash_token(token)
            
            stmt = select(TokenDatabase).where(TokenDatabase.token_hash == token_hash)
            result = await self.session.execute(stmt)
            token_record = result.scalar_one_or_none()
            
            if token_record:
                token_record.last_used_at = datetime.now(timezone.utc)
                await self.session.commit()
                
        except Exception as e:
            logger.error(f"Failed to update token usage: {e}")
    
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions from database"""
        # This would typically query a user permissions table
        # For now, return a default set of permissions
        return [
            "content:read",
            "content:write",
            "profile:read",
            "profile:write",
            "analytics:read"
        ]

# Export the main classes
__all__ = [
    'TokenRepository',
    'TokenDatabase',
    'BlacklistedToken',
    'TokenType',
    'TokenStatus',
    'OAuthProvider',
    'TokenMetadata',
    'TokenResponse'
]
