#!/usr/bin/env python3
"""
🔐 Rights Manager - Enterprise Security Module
==============================================

Ultra-secure Digital Rights Management (DRM) with content protection,
license management, and usage tracking for enterprise content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + DRM + Licensing + Content Protection
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import base64
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

import redis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of protected content"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    SOFTWARE = "software"
    DATASET = "dataset"
    MODEL = "model"
    STREAM = "stream"

class LicenseType(Enum):
    """License types for content access"""
    SINGLE_USE = "single_use"
    TIME_LIMITED = "time_limited"
    DEVICE_LIMITED = "device_limited"
    CONCURRENT_USERS = "concurrent_users"
    SUBSCRIPTION = "subscription"
    PERPETUAL = "perpetual"
    TRIAL = "trial"
    PREMIUM = "premium"

class AccessRight(Enum):
    """Access rights for content"""
    VIEW = "view"
    DOWNLOAD = "download"
    COPY = "copy"
    MODIFY = "modify"
    SHARE = "share"
    PRINT = "print"
    OFFLINE_ACCESS = "offline_access"
    STREAMING = "streaming"
    ANALYTICS = "analytics"

class ProtectionLevel(Enum):
    """Content protection levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class DigitalRights:
    """Digital rights definition for content"""
    rights_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    content_type: ContentType = ContentType.DOCUMENT
    owner_id: str = ""
    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    allowed_rights: Set[AccessRight] = field(default_factory=set)
    forbidden_rights: Set[AccessRight] = field(default_factory=set)
    expiration_date: Optional[datetime] = None
    max_views: Optional[int] = None
    max_downloads: Optional[int] = None
    allowed_devices: Set[str] = field(default_factory=set)
    allowed_users: Set[str] = field(default_factory=set)
    geographic_restrictions: List[str] = field(default_factory=list)
    watermark_required: bool = True
    encryption_required: bool = True
    audit_trail_required: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccessToken:
    """Access token for content consumption"""
    token_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    user_id: str = ""
    device_id: str = ""
    rights_id: str = ""
    license_id: str = ""
    granted_rights: Set[AccessRight] = field(default_factory=set)
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))
    usage_count: int = 0
    max_usage: Optional[int] = None
    ip_address: str = "unknown"
    session_id: Optional[str] = None
    is_active: bool = True
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentLicense:
    """License for content access"""
    license_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    license_type: LicenseType = LicenseType.TIME_LIMITED
    licensee_id: str = ""
    licensor_id: str = ""
    granted_rights: Set[AccessRight] = field(default_factory=set)
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None
    max_concurrent_users: Optional[int] = None
    max_devices: Optional[int] = None
    max_usage_count: Optional[int] = None
    current_usage_count: int = 0
    geographic_scope: List[str] = field(default_factory=list)
    device_restrictions: List[str] = field(default_factory=list)
    price: Optional[float] = None
    currency: str = "USD"
    is_active: bool = True
    revoked_at: Optional[datetime] = None
    terms_and_conditions: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageRecord:
    """Usage tracking record"""
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    user_id: str = ""
    device_id: str = ""
    token_id: str = ""
    license_id: str = ""
    access_right: AccessRight = AccessRight.VIEW
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: Optional[int] = None
    bytes_consumed: Optional[int] = None
    ip_address: str = "unknown"
    user_agent: str = ""
    location: Optional[Dict[str, str]] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class LicenseManager:
    """
    License management system for content licensing.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.license_cache: Dict[str, ContentLicense] = {}
        
    async def initialize(self) -> None:
        """Initialize license manager"""
        try:
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("License manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize license manager: {e}")
            raise

    async def create_license(self, license_data: ContentLicense) -> bool:
        """Create new content license"""
        try:
            # Validate license
            if not await self._validate_license(license_data):
                return False
            
            # Store license
            await self._store_license(license_data)
            
            # Cache license
            self.license_cache[license_data.license_id] = license_data
            
            logger.info(f"Created license {license_data.license_id} for content {license_data.content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create license: {e}")
            return False

    async def get_license(self, license_id: str) -> Optional[ContentLicense]:
        """Get license by ID"""
        try:
            # Check cache first
            if license_id in self.license_cache:
                license_data = self.license_cache[license_id]
                
                # Check if still valid
                if await self._is_license_valid(license_data):
                    return license_data
                else:
                    # Remove from cache if invalid
                    del self.license_cache[license_id]
            
            # Load from storage
            license_data = await self._load_license(license_id)
            if license_data and await self._is_license_valid(license_data):
                self.license_cache[license_id] = license_data
                return license_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get license {license_id}: {e}")
            return None

    async def validate_license_usage(
        self,
        license_id: str,
        user_id: str,
        device_id: str,
        requested_right: AccessRight
    ) -> Tuple[bool, Optional[str]]:
        """Validate license usage request"""
        try:
            license_data = await self.get_license(license_id)
            if not license_data:
                return False, "License not found"
            
            # Check if license is active
            if not license_data.is_active:
                return False, "License is inactive"
            
            # Check validity period
            now = datetime.now(timezone.utc)
            if license_data.valid_from > now:
                return False, "License not yet valid"
            
            if license_data.valid_until and license_data.valid_until < now:
                return False, "License has expired"
            
            # Check granted rights
            if requested_right not in license_data.granted_rights:
                return False, f"Right '{requested_right.value}' not granted"
            
            # Check usage limits
            if (license_data.max_usage_count and 
                license_data.current_usage_count >= license_data.max_usage_count):
                return False, "Usage limit exceeded"
            
            # Check concurrent users (simplified)
            if license_data.max_concurrent_users:
                current_users = await self._get_current_concurrent_users(license_id)
                if len(current_users) >= license_data.max_concurrent_users:
                    if user_id not in current_users:
                        return False, "Concurrent user limit exceeded"
            
            # Check device restrictions
            if license_data.device_restrictions and device_id not in license_data.device_restrictions:
                return False, "Device not authorized"
            
            return True, None
            
        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return False, f"Validation error: {e}"

    async def increment_usage(self, license_id: str) -> bool:
        """Increment license usage count"""
        try:
            license_data = await self.get_license(license_id)
            if license_data:
                license_data.current_usage_count += 1
                await self._store_license(license_data)
                
                # Update cache
                self.license_cache[license_id] = license_data
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to increment usage for license {license_id}: {e}")
            return False

    async def revoke_license(self, license_id: str, reason: str) -> bool:
        """Revoke a license"""
        try:
            license_data = await self.get_license(license_id)
            if license_data:
                license_data.is_active = False
                license_data.revoked_at = datetime.now(timezone.utc)
                license_data.metadata["revocation_reason"] = reason
                
                await self._store_license(license_data)
                
                # Remove from cache
                if license_id in self.license_cache:
                    del self.license_cache[license_id]
                
                logger.info(f"Revoked license {license_id}: {reason}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke license {license_id}: {e}")
            return False

    async def _validate_license(self, license_data: ContentLicense) -> bool:
        """Validate license data"""
        try:
            # Basic validation
            if not license_data.content_id or not license_data.licensee_id:
                return False
            
            # Check date consistency
            if license_data.valid_until and license_data.valid_from >= license_data.valid_until:
                return False
            
            # Check granted rights
            if not license_data.granted_rights:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return False

    async def _is_license_valid(self, license_data: ContentLicense) -> bool:
        """Check if license is currently valid"""
        try:
            if not license_data.is_active:
                return False
            
            now = datetime.now(timezone.utc)
            
            if license_data.valid_from > now:
                return False
            
            if license_data.valid_until and license_data.valid_until < now:
                return False
            
            return True
            
        except Exception:
            return False

    async def _store_license(self, license_data: ContentLicense) -> None:
        """Store license in Redis"""
        try:
            license_dict = {
                "license_id": license_data.license_id,
                "content_id": license_data.content_id,
                "license_type": license_data.license_type.value,
                "licensee_id": license_data.licensee_id,
                "licensor_id": license_data.licensor_id,
                "granted_rights": [right.value for right in license_data.granted_rights],
                "issued_at": license_data.issued_at.isoformat(),
                "valid_from": license_data.valid_from.isoformat(),
                "valid_until": license_data.valid_until.isoformat() if license_data.valid_until else None,
                "max_concurrent_users": license_data.max_concurrent_users,
                "max_devices": license_data.max_devices,
                "max_usage_count": license_data.max_usage_count,
                "current_usage_count": license_data.current_usage_count,
                "geographic_scope": license_data.geographic_scope,
                "device_restrictions": license_data.device_restrictions,
                "price": license_data.price,
                "currency": license_data.currency,
                "is_active": license_data.is_active,
                "revoked_at": license_data.revoked_at.isoformat() if license_data.revoked_at else None,
                "terms_and_conditions": license_data.terms_and_conditions,
                "metadata": license_data.metadata
            }
            
            await self.redis.setex(
                f"content_license:{license_data.license_id}",
                86400 * 365,  # 1 year
                json.dumps(license_dict, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store license: {e}")
            raise

    async def _load_license(self, license_id: str) -> Optional[ContentLicense]:
        """Load license from Redis"""
        try:
            license_data = await self.redis.get(f"content_license:{license_id}")
            if not license_data:
                return None
            
            license_dict = json.loads(license_data)
            
            license_obj = ContentLicense(
                license_id=license_dict["license_id"],
                content_id=license_dict["content_id"],
                license_type=LicenseType(license_dict["license_type"]),
                licensee_id=license_dict["licensee_id"],
                licensor_id=license_dict["licensor_id"],
                granted_rights=set(AccessRight(right) for right in license_dict["granted_rights"]),
                issued_at=datetime.fromisoformat(license_dict["issued_at"]),
                valid_from=datetime.fromisoformat(license_dict["valid_from"]),
                valid_until=datetime.fromisoformat(license_dict["valid_until"]) if license_dict["valid_until"] else None,
                max_concurrent_users=license_dict["max_concurrent_users"],
                max_devices=license_dict["max_devices"],
                max_usage_count=license_dict["max_usage_count"],
                current_usage_count=license_dict["current_usage_count"],
                geographic_scope=license_dict["geographic_scope"],
                device_restrictions=license_dict["device_restrictions"],
                price=license_dict["price"],
                currency=license_dict["currency"],
                is_active=license_dict["is_active"],
                revoked_at=datetime.fromisoformat(license_dict["revoked_at"]) if license_dict["revoked_at"] else None,
                terms_and_conditions=license_dict["terms_and_conditions"],
                metadata=license_dict["metadata"]
            )
            
            return license_obj
            
        except Exception as e:
            logger.error(f"Failed to load license {license_id}: {e}")
            return None

    async def _get_current_concurrent_users(self, license_id: str) -> Set[str]:
        """Get current concurrent users for license"""
        try:
            # Get active tokens for this license
            pattern = f"access_token:*:{license_id}"
            keys = await self.redis.keys(pattern)
            
            current_users = set()
            current_time = datetime.now(timezone.utc)
            
            for key in keys:
                token_data = await self.redis.get(key)
                if token_data:
                    token_dict = json.loads(token_data)
                    expires_at = datetime.fromisoformat(token_dict["expires_at"])
                    
                    if expires_at > current_time and token_dict["is_active"]:
                        current_users.add(token_dict["user_id"])
            
            return current_users
            
        except Exception as e:
            logger.error(f"Failed to get concurrent users: {e}")
            return set()

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()

class ContentProtection:
    """
    Content protection system with encryption and watermarking.
    """
    
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    async def protect_content(
        self,
        content: bytes,
        protection_level: ProtectionLevel,
        rights: DigitalRights
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Protect content based on protection level"""
        try:
            protected_content = content
            protection_metadata = {}
            
            # Apply protection based on level
            if protection_level in [ProtectionLevel.STANDARD, ProtectionLevel.HIGH, ProtectionLevel.ULTRA]:
                # Encrypt content
                if rights.encryption_required:
                    protected_content = await self._encrypt_content(protected_content)
                    protection_metadata["encrypted"] = True
                
                # Add watermark
                if rights.watermark_required:
                    protected_content = await self._add_watermark(
                        protected_content,
                        rights.content_type,
                        rights.owner_id
                    )
                    protection_metadata["watermarked"] = True
            
            if protection_level in [ProtectionLevel.HIGH, ProtectionLevel.ULTRA]:
                # Add tamper detection
                protection_metadata["integrity_hash"] = await self._calculate_integrity_hash(protected_content)
                
                # Add DRM wrapper
                protected_content = await self._add_drm_wrapper(protected_content, rights)
                protection_metadata["drm_protected"] = True
            
            if protection_level == ProtectionLevel.ULTRA:
                # Add additional security measures
                protection_metadata["ultra_protection"] = True
                
                # Hardware-based protection (placeholder)
                # In production, this would integrate with hardware security modules
                
            return protected_content, protection_metadata
            
        except Exception as e:
            logger.error(f"Content protection failed: {e}")
            raise

    async def _encrypt_content(self, content: bytes) -> bytes:
        """Encrypt content"""
        try:
            return self.cipher_suite.encrypt(content)
        except Exception as e:
            logger.error(f"Content encryption failed: {e}")
            raise

    async def _add_watermark(
        self,
        content: bytes,
        content_type: ContentType,
        owner_id: str
    ) -> bytes:
        """Add watermark to content"""
        try:
            # Simplified watermarking - in production, use specialized libraries
            watermark_data = f"OWNER:{owner_id};TIMESTAMP:{int(time.time())}"
            
            if content_type in [ContentType.IMAGE, ContentType.VIDEO]:
                # For images/video, embed watermark in metadata or pixels
                # This is a placeholder - real implementation would use image processing
                watermark_bytes = watermark_data.encode()
                return content + b"\x00WATERMARK\x00" + watermark_bytes
            elif content_type in [ContentType.AUDIO]:
                # For audio, embed in audio stream
                watermark_bytes = watermark_data.encode()
                return content + b"\x00AUDIOMARK\x00" + watermark_bytes
            elif content_type == ContentType.DOCUMENT:
                # For documents, embed in metadata
                watermark_bytes = watermark_data.encode()
                return content + b"\x00DOCMARK\x00" + watermark_bytes
            else:
                # Generic watermarking
                watermark_bytes = watermark_data.encode()
                return content + b"\x00GENERICMARK\x00" + watermark_bytes
                
        except Exception as e:
            logger.error(f"Watermarking failed: {e}")
            return content

    async def _calculate_integrity_hash(self, content: bytes) -> str:
        """Calculate integrity hash"""
        try:
            import hashlib
            return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"Integrity hash calculation failed: {e}")
            return ""

    async def _add_drm_wrapper(self, content: bytes, rights: DigitalRights) -> bytes:
        """Add DRM wrapper to content"""
        try:
            # Create DRM header
            drm_header = {
                "version": "1.0",
                "rights_id": rights.rights_id,
                "content_type": rights.content_type.value,
                "protection_level": rights.protection_level.value,
                "allowed_rights": [right.value for right in rights.allowed_rights],
                "encryption_required": rights.encryption_required,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            header_json = json.dumps(drm_header)
            header_bytes = header_json.encode()
            header_length = len(header_bytes).to_bytes(4, 'big')
            
            # Wrap content with DRM header
            drm_wrapped = b"DRM1.0" + header_length + header_bytes + content
            
            return drm_wrapped
            
        except Exception as e:
            logger.error(f"DRM wrapping failed: {e}")
            return content

class DRMEngine:
    """
    Digital Rights Management engine.
    """
    
    def __init__(self):
        self.content_protection = ContentProtection()
        
    async def wrap_content(
        self,
        content: bytes,
        rights: DigitalRights
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Wrap content with DRM protection"""
        try:
            return await self.content_protection.protect_content(
                content,
                rights.protection_level,
                rights
            )
        except Exception as e:
            logger.error(f"DRM wrapping failed: {e}")
            raise

    async def unwrap_content(
        self,
        protected_content: bytes,
        access_token: AccessToken
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Unwrap DRM-protected content"""
        try:
            # Check DRM header
            if not protected_content.startswith(b"DRM1.0"):
                return False, None, "Invalid DRM format"
            
            # Extract header
            header_length = int.from_bytes(protected_content[6:10], 'big')
            header_bytes = protected_content[10:10+header_length]
            content_bytes = protected_content[10+header_length:]
            
            try:
                drm_header = json.loads(header_bytes.decode())
            except:
                return False, None, "Invalid DRM header"
            
            # Validate access token rights
            required_rights = set(AccessRight(right) for right in drm_header["allowed_rights"])
            if not access_token.granted_rights.intersection(required_rights):
                return False, None, "Insufficient rights"
            
            # Decrypt if needed
            if drm_header.get("encryption_required", False):
                try:
                    decrypted_content = await self._decrypt_content(content_bytes)
                    return True, decrypted_content, None
                except:
                    return False, None, "Decryption failed"
            
            return True, content_bytes, None
            
        except Exception as e:
            logger.error(f"DRM unwrapping failed: {e}")
            return False, None, f"Unwrapping error: {e}"

    async def _decrypt_content(self, encrypted_content: bytes) -> bytes:
        """Decrypt protected content"""
        try:
            return self.content_protection.cipher_suite.decrypt(encrypted_content)
        except Exception as e:
            logger.error(f"Content decryption failed: {e}")
            raise

class RightsManager:
    """
    Main digital rights management system.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        encryption_key: Optional[bytes] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize components
        self.license_manager = LicenseManager(redis_url)
        self.drm_engine = DRMEngine()
        
        # Token management
        self.active_tokens: Dict[str, AccessToken] = {}
        self.usage_records: List[UsageRecord] = []
        
        # Configuration
        self.config = {
            "default_token_expiry": 86400,  # 24 hours
            "max_concurrent_tokens_per_user": 5,
            "audit_all_access": True,
            "enable_geographic_restrictions": True,
            "enable_device_fingerprinting": True,
            "watermark_all_content": True,
            "require_secure_channel": True
        }

    async def initialize(self) -> None:
        """Initialize rights management system"""
        try:
            # Initialize Redis connection
            self.redis = redis.from_url(self.redis_url)
            await self.redis.ping()
            
            # Initialize components
            await self.license_manager.initialize()
            
            # Start background tasks
            asyncio.create_task(self._token_cleanup_task())
            asyncio.create_task(self._usage_analytics_task())
            
            logger.info("Rights management system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize rights manager: {e}")
            raise

    async def create_digital_rights(self, rights: DigitalRights) -> bool:
        """Create digital rights for content"""
        try:
            # Validate rights
            if not await self._validate_rights(rights):
                return False
            
            # Store rights
            await self._store_rights(rights)
            
            logger.info(f"Created digital rights {rights.rights_id} for content {rights.content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create digital rights: {e}")
            return False

    async def request_access_token(
        self,
        content_id: str,
        user_id: str,
        device_id: str,
        requested_rights: List[AccessRight],
        license_id: Optional[str] = None,
        ip_address: str = "unknown",
        session_id: Optional[str] = None
    ) -> Tuple[bool, Optional[AccessToken], Optional[str]]:
        """Request access token for content"""
        try:
            # Get content rights
            rights = await self._get_content_rights(content_id)
            if not rights:
                return False, None, "Content rights not found"
            
            # Check if user is allowed
            if rights.allowed_users and user_id not in rights.allowed_users:
                return False, None, "User not authorized"
            
            # Check device restrictions
            if rights.allowed_devices and device_id not in rights.allowed_devices:
                return False, None, "Device not authorized"
            
            # Check geographic restrictions
            if (self.config["enable_geographic_restrictions"] and 
                rights.geographic_restrictions):
                # Would check user location against restrictions
                pass
            
            # Validate license if provided
            if license_id:
                license_valid, license_error = await self.license_manager.validate_license_usage(
                    license_id, user_id, device_id, requested_rights[0] if requested_rights else AccessRight.VIEW
                )
                if not license_valid:
                    return False, None, f"License validation failed: {license_error}"
            
            # Check requested rights against allowed rights
            granted_rights = set(requested_rights).intersection(rights.allowed_rights)
            forbidden_requested = set(requested_rights).intersection(rights.forbidden_rights)
            
            if forbidden_requested:
                return False, None, f"Forbidden rights requested: {forbidden_requested}"
            
            if not granted_rights:
                return False, None, "No valid rights requested"
            
            # Check concurrent token limit
            user_token_count = await self._count_user_active_tokens(user_id)
            if user_token_count >= self.config["max_concurrent_tokens_per_user"]:
                return False, None, "Concurrent token limit exceeded"
            
            # Create access token
            access_token = AccessToken(
                content_id=content_id,
                user_id=user_id,
                device_id=device_id,
                rights_id=rights.rights_id,
                license_id=license_id or "",
                granted_rights=granted_rights,
                ip_address=ip_address,
                session_id=session_id,
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.config["default_token_expiry"])
            )
            
            # Apply content-specific restrictions
            if rights.max_views:
                access_token.max_usage = rights.max_views
            
            # Store token
            await self._store_access_token(access_token)
            self.active_tokens[access_token.token_id] = access_token
            
            # Increment license usage if applicable
            if license_id:
                await self.license_manager.increment_usage(license_id)
            
            # Log access token creation
            if self.config["audit_all_access"]:
                await self._log_access_event(
                    "token_created",
                    user_id,
                    content_id,
                    {"token_id": access_token.token_id, "granted_rights": [r.value for r in granted_rights]}
                )
            
            logger.info(f"Created access token {access_token.token_id} for user {user_id}")
            return True, access_token, None
            
        except Exception as e:
            logger.error(f"Access token request failed: {e}")
            return False, None, f"Token request error: {e}"

    async def validate_access_token(
        self,
        token_id: str,
        requested_right: AccessRight,
        device_id: str,
        ip_address: str = "unknown"
    ) -> Tuple[bool, Optional[AccessToken], Optional[str]]:
        """Validate access token for specific operation"""
        try:
            # Get token
            access_token = await self._get_access_token(token_id)
            if not access_token:
                return False, None, "Token not found"
            
            # Check if token is active
            if not access_token.is_active:
                return False, None, "Token is inactive"
            
            # Check expiration
            if datetime.now(timezone.utc) > access_token.expires_at:
                return False, None, "Token has expired"
            
            # Check device
            if access_token.device_id != device_id:
                return False, None, "Device mismatch"
            
            # Check IP address (if strict mode)
            if (self.config["require_secure_channel"] and 
                access_token.ip_address != "unknown" and
                access_token.ip_address != ip_address):
                return False, None, "IP address mismatch"
            
            # Check requested right
            if requested_right not in access_token.granted_rights:
                return False, None, f"Right '{requested_right.value}' not granted"
            
            # Check usage limits
            if (access_token.max_usage and 
                access_token.usage_count >= access_token.max_usage):
                return False, None, "Usage limit exceeded"
            
            # Increment usage count
            access_token.usage_count += 1
            await self._store_access_token(access_token)
            self.active_tokens[token_id] = access_token
            
            # Record usage
            usage_record = UsageRecord(
                content_id=access_token.content_id,
                user_id=access_token.user_id,
                device_id=device_id,
                token_id=token_id,
                license_id=access_token.license_id,
                access_right=requested_right,
                ip_address=ip_address,
                success=True
            )
            
            await self._record_usage(usage_record)
            
            return True, access_token, None
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False, None, f"Validation error: {e}"

    async def revoke_access_token(self, token_id: str, reason: str) -> bool:
        """Revoke access token"""
        try:
            access_token = await self._get_access_token(token_id)
            if access_token:
                access_token.is_active = False
                access_token.revoked_at = datetime.now(timezone.utc)
                access_token.revocation_reason = reason
                
                await self._store_access_token(access_token)
                
                # Remove from active tokens
                if token_id in self.active_tokens:
                    del self.active_tokens[token_id]
                
                # Log revocation
                if self.config["audit_all_access"]:
                    await self._log_access_event(
                        "token_revoked",
                        access_token.user_id,
                        access_token.content_id,
                        {"token_id": token_id, "reason": reason}
                    )
                
                logger.info(f"Revoked access token {token_id}: {reason}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke token {token_id}: {e}")
            return False

    async def protect_content(
        self,
        content_id: str,
        content: bytes
    ) -> Tuple[bool, Optional[bytes], Optional[Dict[str, Any]]]:
        """Apply DRM protection to content"""
        try:
            # Get content rights
            rights = await self._get_content_rights(content_id)
            if not rights:
                return False, None, None
            
            # Apply DRM protection
            protected_content, protection_metadata = await self.drm_engine.wrap_content(
                content, rights
            )
            
            return True, protected_content, protection_metadata
            
        except Exception as e:
            logger.error(f"Content protection failed: {e}")
            return False, None, None

    async def access_content(
        self,
        token_id: str,
        protected_content: bytes
    ) -> Tuple[bool, Optional[bytes], Optional[str]]:
        """Access DRM-protected content using token"""
        try:
            # Get and validate token
            access_token = await self._get_access_token(token_id)
            if not access_token:
                return False, None, "Invalid token"
            
            # Unwrap content
            success, content, error = await self.drm_engine.unwrap_content(
                protected_content, access_token
            )
            
            if success and self.config["audit_all_access"]:
                await self._log_access_event(
                    "content_accessed",
                    access_token.user_id,
                    access_token.content_id,
                    {"token_id": token_id}
                )
            
            return success, content, error
            
        except Exception as e:
            logger.error(f"Content access failed: {e}")
            return False, None, f"Access error: {e}"

    async def _validate_rights(self, rights: DigitalRights) -> bool:
        """Validate digital rights"""
        try:
            # Basic validation
            if not rights.content_id or not rights.owner_id:
                return False
            
            # Check for conflicting rights
            if rights.allowed_rights.intersection(rights.forbidden_rights):
                return False
            
            # Check expiration date
            if rights.expiration_date and rights.expiration_date <= datetime.now(timezone.utc):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rights validation failed: {e}")
            return False

    async def _store_rights(self, rights: DigitalRights) -> None:
        """Store digital rights"""
        try:
            rights_dict = {
                "rights_id": rights.rights_id,
                "content_id": rights.content_id,
                "content_type": rights.content_type.value,
                "owner_id": rights.owner_id,
                "protection_level": rights.protection_level.value,
                "allowed_rights": [right.value for right in rights.allowed_rights],
                "forbidden_rights": [right.value for right in rights.forbidden_rights],
                "expiration_date": rights.expiration_date.isoformat() if rights.expiration_date else None,
                "max_views": rights.max_views,
                "max_downloads": rights.max_downloads,
                "allowed_devices": list(rights.allowed_devices),
                "allowed_users": list(rights.allowed_users),
                "geographic_restrictions": rights.geographic_restrictions,
                "watermark_required": rights.watermark_required,
                "encryption_required": rights.encryption_required,
                "audit_trail_required": rights.audit_trail_required,
                "created_at": rights.created_at.isoformat(),
                "updated_at": rights.updated_at.isoformat(),
                "metadata": rights.metadata
            }
            
            await self.redis.setex(
                f"digital_rights:{rights.content_id}",
                86400 * 365,  # 1 year
                json.dumps(rights_dict, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store rights: {e}")
            raise

    async def _get_content_rights(self, content_id: str) -> Optional[DigitalRights]:
        """Get digital rights for content"""
        try:
            rights_data = await self.redis.get(f"digital_rights:{content_id}")
            if not rights_data:
                return None
            
            rights_dict = json.loads(rights_data)
            
            rights = DigitalRights(
                rights_id=rights_dict["rights_id"],
                content_id=rights_dict["content_id"],
                content_type=ContentType(rights_dict["content_type"]),
                owner_id=rights_dict["owner_id"],
                protection_level=ProtectionLevel(rights_dict["protection_level"]),
                allowed_rights=set(AccessRight(right) for right in rights_dict["allowed_rights"]),
                forbidden_rights=set(AccessRight(right) for right in rights_dict["forbidden_rights"]),
                expiration_date=datetime.fromisoformat(rights_dict["expiration_date"]) if rights_dict["expiration_date"] else None,
                max_views=rights_dict["max_views"],
                max_downloads=rights_dict["max_downloads"],
                allowed_devices=set(rights_dict["allowed_devices"]),
                allowed_users=set(rights_dict["allowed_users"]),
                geographic_restrictions=rights_dict["geographic_restrictions"],
                watermark_required=rights_dict["watermark_required"],
                encryption_required=rights_dict["encryption_required"],
                audit_trail_required=rights_dict["audit_trail_required"],
                created_at=datetime.fromisoformat(rights_dict["created_at"]),
                updated_at=datetime.fromisoformat(rights_dict["updated_at"]),
                metadata=rights_dict["metadata"]
            )
            
            return rights
            
        except Exception as e:
            logger.error(f"Failed to get content rights: {e}")
            return None

    async def _store_access_token(self, token: AccessToken) -> None:
        """Store access token"""
        try:
            token_dict = {
                "token_id": token.token_id,
                "content_id": token.content_id,
                "user_id": token.user_id,
                "device_id": token.device_id,
                "rights_id": token.rights_id,
                "license_id": token.license_id,
                "granted_rights": [right.value for right in token.granted_rights],
                "issued_at": token.issued_at.isoformat(),
                "expires_at": token.expires_at.isoformat(),
                "usage_count": token.usage_count,
                "max_usage": token.max_usage,
                "ip_address": token.ip_address,
                "session_id": token.session_id,
                "is_active": token.is_active,
                "revoked_at": token.revoked_at.isoformat() if token.revoked_at else None,
                "revocation_reason": token.revocation_reason,
                "metadata": token.metadata
            }
            
            # Calculate TTL
            ttl = max(3600, int((token.expires_at - datetime.now(timezone.utc)).total_seconds()))
            
            await self.redis.setex(
                f"access_token:{token.user_id}:{token.token_id}",
                ttl,
                json.dumps(token_dict, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to store access token: {e}")
            raise

    async def _get_access_token(self, token_id: str) -> Optional[AccessToken]:
        """Get access token"""
        try:
            # Check active tokens first
            if token_id in self.active_tokens:
                return self.active_tokens[token_id]
            
            # Search in Redis
            pattern = f"access_token:*:{token_id}"
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return None
            
            token_data = await self.redis.get(keys[0])
            if not token_data:
                return None
            
            token_dict = json.loads(token_data)
            
            token = AccessToken(
                token_id=token_dict["token_id"],
                content_id=token_dict["content_id"],
                user_id=token_dict["user_id"],
                device_id=token_dict["device_id"],
                rights_id=token_dict["rights_id"],
                license_id=token_dict["license_id"],
                granted_rights=set(AccessRight(right) for right in token_dict["granted_rights"]),
                issued_at=datetime.fromisoformat(token_dict["issued_at"]),
                expires_at=datetime.fromisoformat(token_dict["expires_at"]),
                usage_count=token_dict["usage_count"],
                max_usage=token_dict["max_usage"],
                ip_address=token_dict["ip_address"],
                session_id=token_dict["session_id"],
                is_active=token_dict["is_active"],
                revoked_at=datetime.fromisoformat(token_dict["revoked_at"]) if token_dict["revoked_at"] else None,
                revocation_reason=token_dict["revocation_reason"],
                metadata=token_dict["metadata"]
            )
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            return None

    async def _count_user_active_tokens(self, user_id: str) -> int:
        """Count active tokens for user"""
        try:
            pattern = f"access_token:{user_id}:*"
            keys = await self.redis.keys(pattern)
            
            active_count = 0
            current_time = datetime.now(timezone.utc)
            
            for key in keys:
                token_data = await self.redis.get(key)
                if token_data:
                    token_dict = json.loads(token_data)
                    expires_at = datetime.fromisoformat(token_dict["expires_at"])
                    
                    if expires_at > current_time and token_dict["is_active"]:
                        active_count += 1
            
            return active_count
            
        except Exception as e:
            logger.error(f"Failed to count user tokens: {e}")
            return 0

    async def _record_usage(self, usage_record: UsageRecord) -> None:
        """Record content usage"""
        try:
            usage_dict = {
                "record_id": usage_record.record_id,
                "content_id": usage_record.content_id,
                "user_id": usage_record.user_id,
                "device_id": usage_record.device_id,
                "token_id": usage_record.token_id,
                "license_id": usage_record.license_id,
                "access_right": usage_record.access_right.value,
                "timestamp": usage_record.timestamp.isoformat(),
                "duration_seconds": usage_record.duration_seconds,
                "bytes_consumed": usage_record.bytes_consumed,
                "ip_address": usage_record.ip_address,
                "user_agent": usage_record.user_agent,
                "location": usage_record.location,
                "success": usage_record.success,
                "error_message": usage_record.error_message,
                "metadata": usage_record.metadata
            }
            
            await self.redis.setex(
                f"usage_record:{usage_record.record_id}",
                86400 * 90,  # Keep for 90 days
                json.dumps(usage_dict, default=str)
            )
            
            # Add to recent usage list
            self.usage_records.append(usage_record)
            if len(self.usage_records) > 1000:  # Keep last 1000 records in memory
                self.usage_records.pop(0)
                
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")

    async def _log_access_event(
        self,
        event_type: str,
        user_id: str,
        content_id: str,
        details: Dict[str, Any]
    ) -> None:
        """Log access event for auditing"""
        try:
            event_data = {
                "event_type": event_type,
                "user_id": user_id,
                "content_id": content_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details
            }
            
            await self.redis.setex(
                f"access_event:{int(time.time())}:{secrets.token_hex(8)}",
                86400 * 365,  # Keep for 1 year
                json.dumps(event_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to log access event: {e}")

    async def _token_cleanup_task(self) -> None:
        """Background task to cleanup expired tokens"""
        try:
            while True:
                await asyncio.sleep(3600)  # Run every hour
                
                expired_tokens = []
                current_time = datetime.now(timezone.utc)
                
                for token_id, token in self.active_tokens.items():
                    if current_time > token.expires_at or not token.is_active:
                        expired_tokens.append(token_id)
                
                for token_id in expired_tokens:
                    del self.active_tokens[token_id]
                
                if expired_tokens:
                    logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
                    
        except Exception as e:
            logger.error(f"Token cleanup task failed: {e}")

    async def _usage_analytics_task(self) -> None:
        """Background task for usage analytics"""
        try:
            while True:
                await asyncio.sleep(86400)  # Run daily
                
                # Generate usage analytics
                await self._generate_usage_analytics()
                
        except Exception as e:
            logger.error(f"Usage analytics task failed: {e}")

    async def _generate_usage_analytics(self) -> None:
        """Generate usage analytics"""
        try:
            # This would generate usage reports and analytics
            # Placeholder implementation
            logger.info("Generated usage analytics")
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get rights management statistics"""
        active_tokens_count = len(self.active_tokens)
        recent_usage_count = len(self.usage_records)
        
        return {
            "active_tokens": active_tokens_count,
            "recent_usage_records": recent_usage_count,
            "license_cache_size": len(self.license_manager.license_cache),
            "config": self.config
        }

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis:
            await self.redis.close()
        await self.license_manager.cleanup()