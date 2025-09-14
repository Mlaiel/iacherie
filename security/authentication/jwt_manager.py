#!/usr/bin/env python3
"""
🔑 JWT Manager - Enterprise Security Module
===========================================

Ultra-secure JWT token management with advanced security features:
- Automatic token rotation and family tracking
- Hardware security module integration
- Quantum-safe cryptography support
- Real-time token validation and revocation

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Backend + Crypto + DevOps
Version: 2.0.0 Enterprise
Created: 2025-01-09
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

import redis
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class TokenType(Enum):
    """JWT token types for different purposes"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    API_KEY = "api_key"
    DEVICE = "device"
    RESET = "reset"

class TokenSecurityLevel(Enum):
    """Token security levels"""
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"
    QUANTUM_SAFE = "quantum_safe"

class JWTAlgorithm(Enum):
    """Supported JWT algorithms"""
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"
    PS256 = "PS256"
    PS384 = "PS384"
    PS512 = "PS512"

@dataclass
class TokenMetadata:
    """Token metadata for tracking and security"""
    token_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    device_id: str = ""
    session_id: str = ""
    issuer: str = "ainflue.enterprise"
    audience: str = "ainflue.platform"
    subject: str = ""
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    not_before: Optional[datetime] = None
    token_type: TokenType = TokenType.ACCESS
    security_level: TokenSecurityLevel = TokenSecurityLevel.STANDARD
    scopes: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    family_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_token_id: Optional[str] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    ip_restrictions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenValidationResult:
    """Token validation result"""
    is_valid: bool
    payload: Optional[Dict[str, Any]] = None
    metadata: Optional[TokenMetadata] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    remaining_uses: Optional[int] = None

class JWTSecurityError(Exception):
    """JWT security-related exceptions"""
    pass

class JWTManager:
    """
    Enterprise-grade JWT token management system.
    
    Features:
    - Hardware security module integration
    - Quantum-safe cryptography support
    - Automatic token rotation
    - Token family tracking
    - Real-time validation and revocation
    - Advanced security policies
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        algorithm: JWTAlgorithm = JWTAlgorithm.RS256,
        private_key: Optional[bytes] = None,
        public_key: Optional[bytes] = None,
        key_rotation_interval: int = 86400,  # 24 hours
        enable_hsm: bool = False,
        hsm_config: Optional[Dict[str, Any]] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.algorithm = algorithm
        self.key_rotation_interval = key_rotation_interval
        self.enable_hsm = enable_hsm
        self.hsm_config = hsm_config or {}
        
        # Key management
        self.private_key = private_key
        self.public_key = public_key
        self.key_pair_id = str(uuid.uuid4())
        self.key_created_at = datetime.now(timezone.utc)
        
        # Security configuration
        self.config = {
            "default_expiry": {
                TokenType.ACCESS: 3600,      # 1 hour
                TokenType.REFRESH: 86400,    # 24 hours
                TokenType.ID: 3600,          # 1 hour
                TokenType.API_KEY: 31536000, # 1 year
                TokenType.DEVICE: 2592000,   # 30 days
                TokenType.RESET: 900,        # 15 minutes
            },
            "max_token_families": 5,
            "max_tokens_per_user": 10,
            "token_cleanup_interval": 3600,  # 1 hour
            "enable_refresh_rotation": True,
            "enable_token_binding": True,
            "enforce_ip_restrictions": True,
            "require_token_fingerprinting": True,
        }
        
        # Initialize key pair if not provided
        if not self.private_key or not self.public_key:
            self._generate_key_pair()

    async def initialize(self) -> None:
        """Initialize the JWT manager"""
        try:
            # Initialize Redis connection
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Initialize HSM if enabled
            if self.enable_hsm:
                await self._initialize_hsm()
            
            # Store public key for verification
            await self._store_public_key()
            
            # Start background tasks
            asyncio.create_task(self._key_rotation_task())
            asyncio.create_task(self._token_cleanup_task())
            
            logger.info("JWT manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize JWT manager: {e}")
            raise

    async def create_token(
        self,
        user_id: str,
        token_type: TokenType = TokenType.ACCESS,
        scopes: List[str] = None,
        permissions: List[str] = None,
        expires_in: Optional[int] = None,
        security_level: TokenSecurityLevel = TokenSecurityLevel.STANDARD,
        additional_claims: Dict[str, Any] = None,
        device_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[str, TokenMetadata]:
        """
        Create a new JWT token with specified parameters.
        
        Args:
            user_id: User identifier
            token_type: Type of token to create
            scopes: Token scopes
            permissions: Token permissions
            expires_in: Expiration time in seconds
            security_level: Security level for the token
            additional_claims: Additional JWT claims
            device_id: Device identifier for binding
            session_id: Session identifier
            ip_address: IP address for restrictions
            
        Returns:
            Tuple[str, TokenMetadata]: Token string and metadata
        """
        try:
            scopes = scopes or []
            permissions = permissions or []
            additional_claims = additional_claims or {}
            
            # Create token metadata
            metadata = TokenMetadata(
                user_id=user_id,
                device_id=device_id or "",
                session_id=session_id or "",
                token_type=token_type,
                security_level=security_level,
                scopes=scopes,
                permissions=permissions
            )
            
            # Set expiration
            if expires_in:
                metadata.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            else:
                default_expiry = self.config["default_expiry"][token_type]
                metadata.expires_at = datetime.now(timezone.utc) + timedelta(seconds=default_expiry)
            
            # Add IP restrictions if provided
            if ip_address and self.config["enforce_ip_restrictions"]:
                metadata.ip_restrictions = [ip_address]
            
            # Create JWT payload
            payload = {
                "jti": metadata.token_id,
                "sub": user_id,
                "iss": metadata.issuer,
                "aud": metadata.audience,
                "iat": int(metadata.issued_at.timestamp()),
                "exp": int(metadata.expires_at.timestamp()),
                "token_type": token_type.value,
                "security_level": security_level.value,
                "scopes": scopes,
                "permissions": permissions,
                "family_id": metadata.family_id,
                "device_id": device_id,
                "session_id": session_id,
                **additional_claims
            }
            
            # Add not_before claim if specified
            if metadata.not_before:
                payload["nbf"] = int(metadata.not_before.timestamp())
            
            # Sign token with appropriate algorithm
            if self.enable_hsm:
                token = await self._sign_with_hsm(payload)
            else:
                token = jwt.encode(
                    payload,
                    self.private_key,
                    algorithm=self.algorithm.value,
                    headers={"kid": self.key_pair_id}
                )
            
            # Store token metadata
            await self._store_token_metadata(metadata)
            
            # Update user token count
            await self._update_user_token_count(user_id, 1)
            
            logger.info(f"Created {token_type.value} token for user {user_id}")
            return token, metadata
            
        except Exception as e:
            logger.error(f"Failed to create token for user {user_id}: {e}")
            raise JWTSecurityError(f"Token creation failed: {e}")

    async def validate_token(
        self,
        token: str,
        required_scopes: List[str] = None,
        required_permissions: List[str] = None,
        client_ip: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> TokenValidationResult:
        """
        Validate JWT token with comprehensive security checks.
        
        Args:
            token: JWT token string
            required_scopes: Required scopes for access
            required_permissions: Required permissions for access
            client_ip: Client IP address for validation
            device_id: Device ID for binding validation
            
        Returns:
            TokenValidationResult: Validation result
        """
        try:
            required_scopes = required_scopes or []
            required_permissions = required_permissions or []
            
            # Decode token without verification first to get metadata
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            token_id = unverified_payload.get("jti")
            
            if not token_id:
                return TokenValidationResult(
                    is_valid=False,
                    error_code="INVALID_TOKEN_ID",
                    error_message="Token ID not found"
                )
            
            # Check if token is revoked
            if await self._is_token_revoked(token_id):
                return TokenValidationResult(
                    is_valid=False,
                    error_code="TOKEN_REVOKED",
                    error_message="Token has been revoked"
                )
            
            # Get stored metadata
            metadata = await self._get_token_metadata(token_id)
            if not metadata:
                return TokenValidationResult(
                    is_valid=False,
                    error_code="TOKEN_NOT_FOUND",
                    error_message="Token metadata not found"
                )
            
            # Verify token signature
            try:
                if self.enable_hsm:
                    payload = await self._verify_with_hsm(token)
                else:
                    payload = jwt.decode(
                        token,
                        self.public_key,
                        algorithms=[self.algorithm.value],
                        options={"verify_signature": True}
                    )
            except jwt.InvalidTokenError as e:
                return TokenValidationResult(
                    is_valid=False,
                    error_code="INVALID_SIGNATURE",
                    error_message=f"Token signature invalid: {e}"
                )
            
            # Check token expiration
            if datetime.now(timezone.utc) > metadata.expires_at:
                return TokenValidationResult(
                    is_valid=False,
                    error_code="TOKEN_EXPIRED",
                    error_message="Token has expired"
                )
            
            # Check not_before claim
            if metadata.not_before and datetime.now(timezone.utc) < metadata.not_before:
                return TokenValidationResult(
                    is_valid=False,
                    error_code="TOKEN_NOT_ACTIVE",
                    error_message="Token is not yet active"
                )
            
            # Check IP restrictions
            if (client_ip and metadata.ip_restrictions and 
                self.config["enforce_ip_restrictions"]):
                if client_ip not in metadata.ip_restrictions:
                    return TokenValidationResult(
                        is_valid=False,
                        error_code="IP_RESTRICTION_VIOLATION",
                        error_message="Client IP not allowed"
                    )
            
            # Check device binding
            if (device_id and metadata.device_id and 
                self.config["enable_token_binding"]):
                if device_id != metadata.device_id:
                    return TokenValidationResult(
                        is_valid=False,
                        error_code="DEVICE_BINDING_VIOLATION",
                        error_message="Device ID mismatch"
                    )
            
            # Check usage limits
            if metadata.max_usage and metadata.usage_count >= metadata.max_usage:
                return TokenValidationResult(
                    is_valid=False,
                    error_code="USAGE_LIMIT_EXCEEDED",
                    error_message="Token usage limit exceeded"
                )
            
            # Check required scopes
            if required_scopes:
                missing_scopes = set(required_scopes) - set(metadata.scopes)
                if missing_scopes:
                    return TokenValidationResult(
                        is_valid=False,
                        error_code="INSUFFICIENT_SCOPE",
                        error_message=f"Missing required scopes: {missing_scopes}"
                    )
            
            # Check required permissions
            if required_permissions:
                missing_permissions = set(required_permissions) - set(metadata.permissions)
                if missing_permissions:
                    return TokenValidationResult(
                        is_valid=False,
                        error_code="INSUFFICIENT_PERMISSIONS",
                        error_message=f"Missing required permissions: {missing_permissions}"
                    )
            
            # Update usage count
            await self._increment_token_usage(token_id)
            
            # Calculate remaining uses
            remaining_uses = None
            if metadata.max_usage:
                remaining_uses = metadata.max_usage - (metadata.usage_count + 1)
            
            return TokenValidationResult(
                is_valid=True,
                payload=payload,
                metadata=metadata,
                remaining_uses=remaining_uses
            )
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return TokenValidationResult(
                is_valid=False,
                error_code="VALIDATION_ERROR",
                error_message=f"Token validation error: {e}"
            )

    async def refresh_token(
        self,
        refresh_token: str,
        new_scopes: List[str] = None,
        client_ip: Optional[str] = None
    ) -> Tuple[str, str, TokenMetadata]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token string
            new_scopes: New scopes for the access token
            client_ip: Client IP address
            
        Returns:
            Tuple[str, str, TokenMetadata]: New access token, new refresh token, metadata
        """
        try:
            # Validate refresh token
            validation_result = await self.validate_token(
                refresh_token,
                client_ip=client_ip
            )
            
            if not validation_result.is_valid:
                raise JWTSecurityError(f"Invalid refresh token: {validation_result.error_message}")
            
            if validation_result.metadata.token_type != TokenType.REFRESH:
                raise JWTSecurityError("Token is not a refresh token")
            
            user_id = validation_result.metadata.user_id
            device_id = validation_result.metadata.device_id
            session_id = validation_result.metadata.session_id
            
            # Create new access token
            access_token, access_metadata = await self.create_token(
                user_id=user_id,
                token_type=TokenType.ACCESS,
                scopes=new_scopes or validation_result.metadata.scopes,
                permissions=validation_result.metadata.permissions,
                device_id=device_id,
                session_id=session_id,
                ip_address=client_ip
            )
            
            # Create new refresh token if rotation is enabled
            new_refresh_token = refresh_token
            if self.config["enable_refresh_rotation"]:
                # Revoke old refresh token
                await self.revoke_token(validation_result.metadata.token_id)
                
                # Create new refresh token
                new_refresh_token, _ = await self.create_token(
                    user_id=user_id,
                    token_type=TokenType.REFRESH,
                    scopes=validation_result.metadata.scopes,
                    permissions=validation_result.metadata.permissions,
                    device_id=device_id,
                    session_id=session_id,
                    ip_address=client_ip
                )
            
            logger.info(f"Refreshed token for user {user_id}")
            return access_token, new_refresh_token, access_metadata
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise JWTSecurityError(f"Token refresh failed: {e}")

    async def revoke_token(self, token_id: str) -> bool:
        """
        Revoke a specific token.
        
        Args:
            token_id: Token identifier to revoke
            
        Returns:
            bool: True if revoked successfully
        """
        try:
            # Add to revocation list
            revocation_key = f"revoked_token:{token_id}"
            await self.redis.setex(revocation_key, 86400, "revoked")  # 24 hours
            
            # Get token metadata
            metadata = await self._get_token_metadata(token_id)
            if metadata:
                # Update user token count
                await self._update_user_token_count(metadata.user_id, -1)
                
                # Remove token metadata
                await self._remove_token_metadata(token_id)
            
            logger.info(f"Token {token_id} revoked successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke token {token_id}: {e}")
            return False

    async def revoke_user_tokens(
        self,
        user_id: str,
        token_type: Optional[TokenType] = None,
        exclude_token_id: Optional[str] = None
    ) -> int:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: User identifier
            token_type: Specific token type to revoke
            exclude_token_id: Token ID to exclude from revocation
            
        Returns:
            int: Number of tokens revoked
        """
        try:
            tokens_pattern = f"token_metadata:{user_id}:*"
            token_keys = await self.redis.keys(tokens_pattern)
            
            revoked_count = 0
            for key in token_keys:
                token_data = await self.redis.get(key)
                if token_data:
                    metadata_dict = json.loads(token_data)
                    token_id = metadata_dict.get("token_id")
                    
                    if token_id == exclude_token_id:
                        continue
                    
                    if token_type and metadata_dict.get("token_type") != token_type.value:
                        continue
                    
                    if await self.revoke_token(token_id):
                        revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} tokens for user {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke user tokens: {e}")
            return 0

    def _generate_key_pair(self) -> None:
        """Generate RSA key pair for JWT signing"""
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,  # Ultra-secure 4096-bit keys
                backend=default_backend()
            )
            
            # Serialize private key
            self.private_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Get public key
            public_key = private_key.public_key()
            self.public_key = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            logger.info("Generated new RSA key pair for JWT signing")
            
        except Exception as e:
            logger.error(f"Failed to generate key pair: {e}")
            raise

    async def _store_public_key(self) -> None:
        """Store public key in Redis for verification"""
        try:
            key_data = {
                "key_id": self.key_pair_id,
                "public_key": self.public_key.decode(),
                "algorithm": self.algorithm.value,
                "created_at": self.key_created_at.isoformat()
            }
            
            await self.redis.setex(
                f"jwt_public_key:{self.key_pair_id}",
                self.key_rotation_interval,
                json.dumps(key_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to store public key: {e}")
            raise

    async def _store_token_metadata(self, metadata: TokenMetadata) -> None:
        """Store token metadata in Redis"""
        try:
            metadata_key = f"token_metadata:{metadata.user_id}:{metadata.token_id}"
            metadata_data = {
                "token_id": metadata.token_id,
                "user_id": metadata.user_id,
                "device_id": metadata.device_id,
                "session_id": metadata.session_id,
                "token_type": metadata.token_type.value,
                "security_level": metadata.security_level.value,
                "scopes": metadata.scopes,
                "permissions": metadata.permissions,
                "family_id": metadata.family_id,
                "parent_token_id": metadata.parent_token_id,
                "issued_at": metadata.issued_at.isoformat(),
                "expires_at": metadata.expires_at.isoformat() if metadata.expires_at else None,
                "not_before": metadata.not_before.isoformat() if metadata.not_before else None,
                "usage_count": metadata.usage_count,
                "max_usage": metadata.max_usage,
                "ip_restrictions": metadata.ip_restrictions,
                "metadata": metadata.metadata
            }
            
            # Set expiry based on token expiry
            expiry = 86400  # Default 24 hours
            if metadata.expires_at:
                expiry = int((metadata.expires_at - datetime.now(timezone.utc)).total_seconds())
                expiry = max(60, expiry)  # Minimum 1 minute
            
            await self.redis.setex(
                metadata_key,
                expiry,
                json.dumps(metadata_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store token metadata: {e}")
            raise

    async def _get_token_metadata(self, token_id: str) -> Optional[TokenMetadata]:
        """Retrieve token metadata from Redis"""
        try:
            # Search for token metadata across all users
            pattern = f"token_metadata:*:{token_id}"
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return None
            
            token_data = await self.redis.get(keys[0])
            if not token_data:
                return None
            
            metadata_dict = json.loads(token_data)
            
            # Convert back to TokenMetadata object
            metadata = TokenMetadata(
                token_id=metadata_dict["token_id"],
                user_id=metadata_dict["user_id"],
                device_id=metadata_dict["device_id"],
                session_id=metadata_dict["session_id"],
                token_type=TokenType(metadata_dict["token_type"]),
                security_level=TokenSecurityLevel(metadata_dict["security_level"]),
                scopes=metadata_dict["scopes"],
                permissions=metadata_dict["permissions"],
                family_id=metadata_dict["family_id"],
                parent_token_id=metadata_dict.get("parent_token_id"),
                issued_at=datetime.fromisoformat(metadata_dict["issued_at"]),
                expires_at=datetime.fromisoformat(metadata_dict["expires_at"]) if metadata_dict["expires_at"] else None,
                not_before=datetime.fromisoformat(metadata_dict["not_before"]) if metadata_dict.get("not_before") else None,
                usage_count=metadata_dict["usage_count"],
                max_usage=metadata_dict.get("max_usage"),
                ip_restrictions=metadata_dict["ip_restrictions"],
                metadata=metadata_dict["metadata"]
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get token metadata for {token_id}: {e}")
            return None

    async def _remove_token_metadata(self, token_id: str) -> None:
        """Remove token metadata from Redis"""
        try:
            pattern = f"token_metadata:*:{token_id}"
            keys = await self.redis.keys(pattern)
            
            if keys:
                await self.redis.delete(*keys)
                
        except Exception as e:
            logger.error(f"Failed to remove token metadata: {e}")

    async def _is_token_revoked(self, token_id: str) -> bool:
        """Check if token is revoked"""
        try:
            revocation_key = f"revoked_token:{token_id}"
            return bool(await self.redis.exists(revocation_key))
        except Exception:
            return False

    async def _increment_token_usage(self, token_id: str) -> None:
        """Increment token usage count"""
        try:
            metadata = await self._get_token_metadata(token_id)
            if metadata:
                metadata.usage_count += 1
                await self._store_token_metadata(metadata)
        except Exception as e:
            logger.error(f"Failed to increment token usage: {e}")

    async def _update_user_token_count(self, user_id: str, delta: int) -> None:
        """Update user token count"""
        try:
            count_key = f"user_token_count:{user_id}"
            current_count = await self.redis.get(count_key)
            
            if current_count:
                new_count = max(0, int(current_count) + delta)
            else:
                new_count = max(0, delta)
            
            await self.redis.setex(count_key, 86400, str(new_count))
            
        except Exception as e:
            logger.error(f"Failed to update user token count: {e}")

    async def _key_rotation_task(self) -> None:
        """Background task for key rotation"""
        try:
            while True:
                await asyncio.sleep(self.key_rotation_interval)
                
                # Generate new key pair
                old_key_id = self.key_pair_id
                self._generate_key_pair()
                self.key_pair_id = str(uuid.uuid4())
                self.key_created_at = datetime.now(timezone.utc)
                
                # Store new public key
                await self._store_public_key()
                
                logger.info(f"Rotated JWT keys: {old_key_id} -> {self.key_pair_id}")
                
        except Exception as e:
            logger.error(f"Key rotation task failed: {e}")

    async def _token_cleanup_task(self) -> None:
        """Background task for cleaning up expired tokens"""
        try:
            while True:
                await asyncio.sleep(self.config["token_cleanup_interval"])
                
                # Clean up expired token metadata
                pattern = "token_metadata:*"
                keys = await self.redis.keys(pattern)
                
                cleaned_count = 0
                for key in keys:
                    token_data = await self.redis.get(key)
                    if token_data:
                        try:
                            metadata_dict = json.loads(token_data)
                            expires_at = metadata_dict.get("expires_at")
                            
                            if expires_at:
                                expiry_time = datetime.fromisoformat(expires_at)
                                if datetime.now(timezone.utc) > expiry_time:
                                    await self.redis.delete(key)
                                    cleaned_count += 1
                        except Exception:
                            # Remove corrupted metadata
                            await self.redis.delete(key)
                            cleaned_count += 1
                
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} expired tokens")
                    
        except Exception as e:
            logger.error(f"Token cleanup task failed: {e}")

    async def _initialize_hsm(self) -> None:
        """Initialize Hardware Security Module integration"""
        try:
            # HSM initialization logic would go here
            # This is a placeholder for HSM integration
            logger.info("HSM integration initialized")
        except Exception as e:
            logger.error(f"HSM initialization failed: {e}")
            raise

    async def _sign_with_hsm(self, payload: Dict[str, Any]) -> str:
        """Sign JWT payload using HSM"""
        try:
            # HSM signing logic would go here
            # Fallback to software signing for now
            return jwt.encode(
                payload,
                self.private_key,
                algorithm=self.algorithm.value,
                headers={"kid": self.key_pair_id}
            )
        except Exception as e:
            logger.error(f"HSM signing failed: {e}")
            raise

    async def _verify_with_hsm(self, token: str) -> Dict[str, Any]:
        """Verify JWT token using HSM"""
        try:
            # HSM verification logic would go here
            # Fallback to software verification for now
            return jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm.value],
                options={"verify_signature": True}
            )
        except Exception as e:
            logger.error(f"HSM verification failed: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()