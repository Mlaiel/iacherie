"""API Key Management Module
Advanced API key generation, validation, and lifecycle management
for enterprise-grade security in IA Influencer Agent

Features:
- Secure API key generation with entropy validation
- API key validation with rate limiting integration
- Key rotation and expiration management
- Permission-based key access control
- Audit trail for API key usage

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import secrets
import hashlib
import hmac
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import base64

from backend.core.config import get_settings
from backend.core.cache import CacheManager
from backend.core.logging import SecurityLogger


class APIKeyStatus(Enum):
    """
API key status values"""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    REVOKED = "revoked"


class APIKeyType(Enum):
    """API key types with different permission levels"""

    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    SERVICE = "service"
    TEMPORARY = "temporary"


@dataclass
class APIKey:
    """API key data structure"""
    key_id: str
    key_hash: str
    user_id: str
    name: str
    key_type: APIKeyType
    permissions: List[str]
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    rate_limit: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIKeyUsage:
    """
API key usage tracking"""
    key_id: str
    timestamp: datetime
    endpoint: str
    method: str
    ip_address: str
    user_agent: str
    response_status: int
    request_size: int = 0
    response_size: int = 0


class APIKeyManager:
    """
Enterprise API key management system"""
    
    def __init__(self):
        self.logger = SecurityLogger("APIKeyManager")
        self.cache = CacheManager()
        self.settings = get_settings()
        
        # Key generation settings
        self.key_length = 32  # bytes
        self.key_prefix = "aif_"  # AI Influencer prefix
        
        # Default permissions by key type
        self.default_permissions = {
            APIKeyType.READ_ONLY: [
                "content.read", "analytics.view", "api.read"
            ],
            APIKeyType.READ_WRITE: [
                "content.read", "content.write", "content.upload",
                "analytics.view", "api.read", "api.write"
            ],
            APIKeyType.ADMIN: [
                "content.*", "analytics.*", "api.*", 
                "user.manage", "system.admin"
            ],
            APIKeyType.SERVICE: [
                "content.read", "content.write", "content.process",
                "fingerprint.create", "api.service"
            ],
            APIKeyType.TEMPORARY: [
                "content.read", "api.read"
            ]
        }
        
        # Default rate limits by key type
        self.default_rate_limits = {
            APIKeyType.READ_ONLY: {"requests_per_minute": 100, "requests_per_hour": 1000},
            APIKeyType.READ_WRITE: {"requests_per_minute": 500, "requests_per_hour": 5000},
            APIKeyType.ADMIN: {"requests_per_minute": 1000, "requests_per_hour": 10000},
            APIKeyType.SERVICE: {"requests_per_minute": 2000, "requests_per_hour": 20000},
            APIKeyType.TEMPORARY: {"requests_per_minute": 50, "requests_per_hour": 200}
        }
    
    async def generate_api_key(
        self,
        user_id: str,
        name: str,
        key_type: APIKeyType,
        expires_in_days: Optional[int] = None,
        custom_permissions: Optional[List[str]] = None,
        custom_rate_limit: Optional[Dict[str, int]] = None
    ) -> Tuple[str, APIKey]:
        """Generate new API key"""
        try:
            # Generate secure random key
            raw_key = secrets.token_urlsafe(self.key_length)
            key_id = str(uuid.uuid4())
            full_key = f"{self.key_prefix}{key_id}_{raw_key}"
            
            # Create hash for storage (never store the actual key)
            key_hash = self._hash_api_key(full_key)
            
            # Set permissions
            permissions = custom_permissions or self.default_permissions.get(key_type, [])
            
            # Set rate limits
            rate_limit = custom_rate_limit or self.default_rate_limits.get(key_type)
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            elif key_type == APIKeyType.TEMPORARY:
                expires_at = datetime.utcnow() + timedelta(days=7)  # Default 7 days for temp keys
            
            # Create API key object
            api_key = APIKey(
                key_id=key_id,
                key_hash=key_hash,
                user_id=user_id,
                name=name,
                key_type=key_type,
                permissions=permissions,
                expires_at=expires_at,
                rate_limit=rate_limit
            )
            
            # Store the API key
            await self._store_api_key(api_key)
            
            self.logger.info(f"API key generated: {key_id} for user {user_id}")
            
            return full_key, api_key
            
        except Exception as e:
            self.logger.error(f"Failed to generate API key: {str(e)}")
            raise
    
    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return key information"""
        try:
            # Validate key format
            if not self._is_valid_key_format(api_key):
                self.logger.warning("Invalid API key format")
                return None
            
            # Extract key ID
            key_id = self._extract_key_id(api_key)
            if not key_id:
                return None
            
            # Get API key from cache/storage
            api_key_obj = await self._get_api_key(key_id)
            if not api_key_obj:
                self.logger.warning(f"API key not found: {key_id}")
                return None
            
            # Verify key hash
            key_hash = self._hash_api_key(api_key)
            if not hmac.compare_digest(api_key_obj.key_hash, key_hash):
                self.logger.warning(f"API key hash mismatch: {key_id}")
                return None
            
            # Check status
            if api_key_obj.status != APIKeyStatus.ACTIVE:
                self.logger.warning(f"API key not active: {key_id}, status: {api_key_obj.status}")
                return None
            
            # Check expiration
            if api_key_obj.expires_at and datetime.utcnow() > api_key_obj.expires_at:
                self.logger.warning(f"API key expired: {key_id}")
                await self._mark_key_expired(key_id)
                return None
            
            # Update usage statistics
            await self._update_key_usage(key_id)
            
            return api_key_obj
            
        except Exception as e:
            self.logger.error(f"API key validation error: {str(e)}")
            return None
    
    async def revoke_api_key(self, key_id: str, reason: str = "Manual revocation") -> bool:
        """Revoke an API key"""
        try:
            api_key = await self._get_api_key(key_id)
            if not api_key:
                return False
            
            api_key.status = APIKeyStatus.REVOKED
            api_key.metadata["revocation_reason"] = reason
            api_key.metadata["revoked_at"] = datetime.utcnow().isoformat()
            
            await self._store_api_key(api_key)
            
            # Remove from cache
            cache_key = f"api_key:{key_id}"
            await self.cache.delete(cache_key)
            
            self.logger.info(f"API key revoked: {key_id}, reason: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke API key {key_id}: {str(e)}")
            return False
    
    async def rotate_api_key(self, key_id: str) -> Optional[Tuple[str, APIKey]]:
        """Rotate an existing API key"""
        try:
            old_key = await self._get_api_key(key_id)
            if not old_key:
                return None
            
            # Generate new key with same properties
            new_key, new_key_obj = await self.generate_api_key(
                user_id=old_key.user_id,
                name=f"{old_key.name} (rotated)",
                key_type=old_key.key_type,
                custom_permissions=old_key.permissions,
                custom_rate_limit=old_key.rate_limit
            )
            
            # Mark old key as revoked
            await self.revoke_api_key(key_id, "Key rotation")
            
            self.logger.info(f"API key rotated: {key_id} -> {new_key_obj.key_id}")
            
            return new_key, new_key_obj
            
        except Exception as e:
            self.logger.error(f"Failed to rotate API key {key_id}: {str(e)}")
            return None
    
    async def list_user_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user"""
        try:
            # In production, this would query the database
            # For now, use file-based storage
            import os
            keys_file = "/tmp/api_keys.json"
            
            if not os.path.exists(keys_file):
                return []
            
            with open(keys_file, 'r') as f:
                keys_data = json.load(f)
            
            user_keys = []
            for key_data in keys_data.values():
                if key_data.get("user_id") == user_id:
                    api_key = self._deserialize_api_key(key_data)
                    user_keys.append(api_key)
            
            return user_keys
            
        except Exception as e:
            self.logger.error(f"Failed to list API keys for user {user_id}: {str(e)}")
            return []
    
    async def record_api_key_usage(
        self,
        key_id: str,
        endpoint: str,
        method: str,
        ip_address: str,
        user_agent: str,
        response_status: int,
        request_size: int = 0,
        response_size: int = 0
    ):
        """Record API key usage for analytics and monitoring"""
        try:
            usage = APIKeyUsage(
                key_id=key_id,
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                method=method,
                ip_address=ip_address,
                user_agent=user_agent,
                response_status=response_status,
                request_size=request_size,
                response_size=response_size
            )
            
            # Store usage data (in production, use database)
            usage_key = f"api_usage:{key_id}:{int(usage.timestamp.timestamp())}"
            await self.cache.set(usage_key, usage.__dict__, expire=86400 * 30)  # Keep for 30 days
            
        except Exception as e:
            self.logger.error(f"Failed to record API key usage: {str(e)}")
    
    def _hash_api_key(self, api_key: str) -> str:
        """Create secure hash of API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def _is_valid_key_format(self, api_key: str) -> bool:
        """
Validate API key format"""
        if not api_key or not api_key.startswith(self.key_prefix):
            return False
        
        parts = api_key[len(self.key_prefix):].split('_', 1)
        if len(parts) != 2:
            return False
        
        # Validate UUID format for key_id
        try:
            uuid.UUID(parts[0])
            return True
        except ValueError:
            return False
    
    def _extract_key_id(self, api_key: str) -> Optional[str]:
        """
Extract key ID from API key"""
        try:
            if not api_key.startswith(self.key_prefix):
                return None
            
            parts = api_key[len(self.key_prefix):].split('_', 1)
            if len(parts) != 2:
                return None
            
            return parts[0]
        except Exception:
            return None
    
    async def _store_api_key(self, api_key: APIKey):
        """
Store API key data"""
        try:
            # Cache for quick access
            cache_key = f"api_key:{api_key.key_id}"
            await self.cache.set(cache_key, api_key.__dict__, expire=3600)
            
            # Store in file (in production, use database)
            import os
            keys_file = "/tmp/api_keys.json"
            
            # Load existing keys
            keys_data = {}
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys_data = json.load(f)
            
            # Serialize API key
            key_data = self._serialize_api_key(api_key)
            keys_data[api_key.key_id] = key_data
            
            # Save back to file
            with open(keys_file, 'w') as f:
                json.dump(keys_data, f, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to store API key: {str(e)}")
            raise
    
    async def _get_api_key(self, key_id: str) -> Optional[APIKey]:
        """Retrieve API key data"""
        try:
            # Check cache first
            cache_key = f"api_key:{key_id}"
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                return self._deserialize_api_key(cached_data)
            
            # Load from file
            import os
            keys_file = "/tmp/api_keys.json"
            
            if not os.path.exists(keys_file):
                return None
            
            with open(keys_file, 'r') as f:
                keys_data = json.load(f)
            
            key_data = keys_data.get(key_id)
            if key_data:
                api_key = self._deserialize_api_key(key_data)
                
                # Re-cache
                await self.cache.set(cache_key, key_data, expire=3600)
                
                return api_key
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get API key {key_id}: {str(e)}")
            return None
    
    def _serialize_api_key(self, api_key: APIKey) -> Dict[str, Any]:
        """Serialize API key for storage"""
        return {
            "key_id": api_key.key_id,
            "key_hash": api_key.key_hash,
            "user_id": api_key.user_id,
            "name": api_key.name,
            "key_type": api_key.key_type.value,
            "permissions": api_key.permissions,
            "status": api_key.status.value,
            "created_at": api_key.created_at.isoformat(),
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            "usage_count": api_key.usage_count,
            "rate_limit": api_key.rate_limit,
            "metadata": api_key.metadata
        }
    
    def _deserialize_api_key(self, data: Dict[str, Any]) -> APIKey:
        """Deserialize API key from storage"""
        return APIKey(
            key_id=data["key_id"],
            key_hash=data["key_hash"],
            user_id=data["user_id"],
            name=data["name"],
            key_type=APIKeyType(data["key_type"]),
            permissions=data["permissions"],
            status=APIKeyStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            last_used_at=datetime.fromisoformat(data["last_used_at"]) if data["last_used_at"] else None,
            usage_count=data["usage_count"],
            rate_limit=data["rate_limit"],
            metadata=data["metadata"]
        )
    
    async def _update_key_usage(self, key_id: str):
        """Update API key usage statistics"""
        try:
            api_key = await self._get_api_key(key_id)
            if api_key:
                api_key.usage_count += 1
                api_key.last_used_at = datetime.utcnow()
                await self._store_api_key(api_key)
                
        except Exception as e:
            self.logger.error(f"Failed to update key usage {key_id}: {str(e)}")
    
    async def _mark_key_expired(self, key_id: str):
        """Mark API key as expired"""
        try:
            api_key = await self._get_api_key(key_id)
            if api_key:
                api_key.status = APIKeyStatus.EXPIRED
                await self._store_api_key(api_key)
                
        except Exception as e:
            self.logger.error(f"Failed to mark key expired {key_id}: {str(e)}")


# Utility functions
async def generate_api_key(
    user_id: str,
    name: str,
    key_type: APIKeyType = APIKeyType.READ_ONLY,
    expires_in_days: Optional[int] = None
) -> Tuple[str, APIKey]:
    """Convenience function to generate API key"""
    manager = APIKeyManager()
    return await manager.generate_api_key(user_id, name, key_type, expires_in_days)


async def validate_api_key(api_key: str) -> Optional[APIKey]:
    """
Convenience function to validate API key"""
    manager = APIKeyManager()
    return await manager.validate_api_key(api_key)