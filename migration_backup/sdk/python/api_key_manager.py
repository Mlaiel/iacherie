"""API Key Manager for Ainflue SDK

Multi-expert implementation:
- Security: Secure API key storage, rotation, and validation
- Backend Senior: Robust key management architecture  
- DevOps: Key monitoring and usage metrics
- DBA: Optimized key storage and retrieval patterns

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import base64
import hashlib
import json
import logging
import secrets
import time
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiofiles
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field

from .exceptions import (
    APIKeyError, SecurityError, ValidationError,
    ConfigurationError, AuthenticationError
)


class KeyPermission(Enum):
    """API key permission levels"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class KeyStatus(Enum):
    """API key status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


@dataclass
class KeyMetrics:
    """API key usage metrics (DevOps expertise)"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    last_used: Optional[datetime] = None
    first_used: Optional[datetime] = None
    bytes_transferred: int = 0
    unique_ips: set = field(default_factory=set)
    
    @property
    def success_rate(self) -> float:
        """Calculate request success rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def days_since_last_use(self) -> int:
        """Days since last use"""
        if not self.last_used:
            return 0
        return (datetime.now() - self.last_used).days


class APIKey(BaseModel):
    """API key model with security metadata"""
    # Key identification
    key_id: str = Field(..., description="Unique key identifier")
    key_hash: str = Field(..., description="Hashed key for storage")
    name: str = Field(..., description="Human-readable key name")
    description: Optional[str] = Field(default=None, description="Key description")
    
    # Security settings
    permissions: List[KeyPermission] = Field(..., description="Key permissions")
    status: KeyStatus = Field(default=KeyStatus.ACTIVE, description="Key status")
    
    # Rate limiting
    rate_limit: int = Field(default=1000, description="Requests per hour")
    rate_limit_window: int = Field(default=3600, description="Rate limit window (seconds)")
    
    # IP restrictions
    allowed_ips: Optional[List[str]] = Field(default=None, description="Allowed IP addresses")
    allowed_domains: Optional[List[str]] = Field(default=None, description="Allowed domains")
    
    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None, description="Key expiration")
    last_rotated: Optional[datetime] = Field(default=None, description="Last rotation")
    
    # Usage tracking
    metrics: KeyMetrics = Field(default_factory=KeyMetrics, description="Usage metrics")
    
    @property
    def is_expired(self) -> bool:
        """Check if key is expired"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Days until expiration"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)


class APIKeyConfig(BaseModel):
    """API key management configuration"""
    # Key generation settings
    key_length: int = Field(default=32, description="Key length in bytes")
    key_prefix: str = Field(default="ak_", description="Key prefix")
    
    # Security settings (Security expertise)
    encryption_key: Optional[str] = Field(default=None, description="Encryption key for storage")
    require_ip_validation: bool = Field(default=False, description="Require IP validation")
    require_domain_validation: bool = Field(default=False, description="Require domain validation")
    
    # Rotation settings
    auto_rotation_enabled: bool = Field(default=False, description="Enable automatic rotation")
    rotation_interval_days: int = Field(default=90, description="Rotation interval in days")
    rotation_overlap_hours: int = Field(default=24, description="Overlap period for old keys")
    
    # Rate limiting defaults
    default_rate_limit: int = Field(default=1000, description="Default rate limit per hour")
    max_rate_limit: int = Field(default=10000, description="Maximum allowed rate limit")
    
    # Monitoring settings
    alert_on_high_usage: bool = Field(default=True, description="Alert on high usage")
    high_usage_threshold: float = Field(default=0.8, description="High usage threshold (80%)")
    
    # Storage settings
    storage_backend: str = Field(default="memory", description="Storage backend (memory, file, database)")
    storage_path: Optional[str] = Field(default=None, description="Storage file path")


class KeyEncryption:
    """API key encryption utilities (Security expertise)"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key
        self._fernet = None
        
        if encryption_key:
            self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup Fernet encryption"""
        if isinstance(self.encryption_key, str):
            # Derive key from password
            password = self.encryption_key.encode()
            salt = b'ainflue_salt_key'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = self.encryption_key
        
        self._fernet = Fernet(key)
    
    def encrypt_key(self, key: str) -> str:
        """Encrypt API key for storage"""
        if not self._fernet:
            return key  # No encryption configured
        
        return self._fernet.encrypt(key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """Decrypt API key from storage"""
        if not self._fernet:
            return encrypted_key  # No encryption configured
        
        return self._fernet.decrypt(encrypted_key.encode()).decode()


class RateLimiter:
    """Rate limiting for API keys (Backend Senior expertise)"""
    
    def __init__(self):
        self.request_counts = {}  # key_id -> {window_start, count}
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    def check_rate_limit(self, key_id: str, rate_limit: int, window_seconds: int) -> bool:
        """Check if request is within rate limit"""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
        
        # Get or create request count for this key
        if key_id not in self.request_counts:
            self.request_counts[key_id] = []
        
        # Remove old requests outside the window
        self.request_counts[key_id] = [
            req_time for req_time in self.request_counts[key_id]
            if req_time > window_start
        ]
        
        # Check if within limit
        current_count = len(self.request_counts[key_id])
        if current_count >= rate_limit:
            return False
        
        # Add current request
        self.request_counts[key_id].append(current_time)
        return True
    
    def _cleanup_old_entries(self):
        """Clean up old rate limit entries"""
        current_time = time.time()
        self.last_cleanup = current_time
        
        # Remove entries older than 24 hours
        cutoff_time = current_time - 86400
        
        for key_id in list(self.request_counts.keys()):
            self.request_counts[key_id] = [
                req_time for req_time in self.request_counts[key_id]
                if req_time > cutoff_time
            ]
            
            # Remove empty entries
            if not self.request_counts[key_id]:
                del self.request_counts[key_id]
    
    def get_remaining_requests(self, key_id: str, rate_limit: int, window_seconds: int) -> int:
        """Get remaining requests in current window"""
        if key_id not in self.request_counts:
            return rate_limit
        
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Count requests in current window
        current_count = sum(1 for req_time in self.request_counts[key_id] if req_time > window_start)
        
        return max(0, rate_limit - current_count)


class KeyStorage:
    """API key storage abstraction (DBA expertise)"""
    
    def __init__(self, config: APIKeyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.encryption = KeyEncryption(config.encryption_key)
        
        # In-memory storage (enhance for production with database)
        self._keys = {}  # key_id -> APIKey
        self._key_lookup = {}  # key_hash -> key_id
    
    async def store_key(self, api_key: APIKey) -> bool:
        """Store API key securely"""
        try:
            # Store the key
            self._keys[api_key.key_id] = api_key
            self._key_lookup[api_key.key_hash] = api_key.key_id
            
            # Persist to storage if configured
            if self.config.storage_backend == "file" and self.config.storage_path:
                await self._persist_to_file()
            
            self.logger.info(f"Stored API key: {api_key.key_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store API key: {e}")
            return False
    
    async def get_key(self, key_id: str) -> Optional[APIKey]:
        """Retrieve API key by ID"""
        try:
            return self._keys.get(key_id)
        except Exception as e:
            self.logger.error(f"Failed to retrieve API key: {e}")
            return None
    
    async def get_key_by_hash(self, key_hash: str) -> Optional[APIKey]:
        """Retrieve API key by hash"""
        try:
            key_id = self._key_lookup.get(key_hash)
            if key_id:
                return self._keys.get(key_id)
            return None
        except Exception as e:
            self.logger.error(f"Failed to retrieve API key by hash: {e}")
            return None
    
    async def update_key(self, key_id: str, updates: Dict[str, Any]) -> bool:
        """Update API key"""
        try:
            if key_id not in self._keys:
                return False
            
            api_key = self._keys[key_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(api_key, field):
                    setattr(api_key, field, value)
            
            # Persist changes
            if self.config.storage_backend == "file" and self.config.storage_path:
                await self._persist_to_file()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update API key: {e}")
            return False
    
    async def delete_key(self, key_id: str) -> bool:
        """Delete API key"""
        try:
            if key_id in self._keys:
                api_key = self._keys[key_id]
                del self._keys[key_id]
                del self._key_lookup[api_key.key_hash]
                
                # Persist changes
                if self.config.storage_backend == "file" and self.config.storage_path:
                    await self._persist_to_file()
                
                self.logger.info(f"Deleted API key: {key_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete API key: {e}")
            return False
    
    async def list_keys(self, 
                       status: Optional[KeyStatus] = None,
                       permissions: Optional[List[KeyPermission]] = None) -> List[APIKey]:
        """List API keys with optional filtering"""
        try:
            keys = list(self._keys.values())
            
            # Filter by status
            if status:
                keys = [key for key in keys if key.status == status]
            
            # Filter by permissions
            if permissions:
                keys = [key for key in keys if any(perm in key.permissions for perm in permissions)]
            
            return keys
            
        except Exception as e:
            self.logger.error(f"Failed to list API keys: {e}")
            return []
    
    async def _persist_to_file(self):
        """Persist keys to file storage"""
        if not self.config.storage_path:
            return
        
        try:
            # Convert keys to serializable format
            keys_data = {}
            for key_id, api_key in self._keys.items():
                keys_data[key_id] = {
                    "key_id": api_key.key_id,
                    "key_hash": api_key.key_hash,
                    "name": api_key.name,
                    "description": api_key.description,
                    "permissions": [p.value for p in api_key.permissions],
                    "status": api_key.status.value,
                    "rate_limit": api_key.rate_limit,
                    "allowed_ips": api_key.allowed_ips,
                    "allowed_domains": api_key.allowed_domains,
                    "created_at": api_key.created_at.isoformat(),
                    "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
                }
            
            # Write to file
            async with aiofiles.open(self.config.storage_path, 'w') as f:
                await f.write(json.dumps(keys_data, indent=2))
                
        except Exception as e:
            self.logger.error(f"Failed to persist keys to file: {e}")


class APIKeyManager:
    """Main API key manager with multi-expert security implementation"""
    
    def __init__(self, config: APIKeyConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Expert components
        self.storage = KeyStorage(config)
        self.rate_limiter = RateLimiter()
        self.encryption = KeyEncryption(config.encryption_key)
        
        # Monitoring
        self.usage_stats = {}
        
    async def generate_key(self,
                          name: str,
                          description: Optional[str] = None,
                          permissions: Optional[List[KeyPermission]] = None,
                          rate_limit: Optional[int] = None,
                          expires_in_days: Optional[int] = None,
                          allowed_ips: Optional[List[str]] = None,
                          allowed_domains: Optional[List[str]] = None) -> tuple[str, APIKey]:
        """Generate new API key with security best practices"""
        try:
            # Generate secure random key
            key_bytes = secrets.token_bytes(self.config.key_length)
            key_b64 = base64.urlsafe_b64encode(key_bytes).decode().rstrip('=')
            api_key_value = f"{self.config.key_prefix}{key_b64}"
            
            # Generate unique key ID
            key_id = f"key_{secrets.token_hex(8)}"
            
            # Hash the key for storage (never store plaintext)
            key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()
            
            # Set defaults
            if permissions is None:
                permissions = [KeyPermission.READ]
            if rate_limit is None:
                rate_limit = self.config.default_rate_limit
            
            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            # Create API key object
            api_key = APIKey(
                key_id=key_id,
                key_hash=key_hash,
                name=name,
                description=description,
                permissions=permissions,
                rate_limit=min(rate_limit, self.config.max_rate_limit),
                allowed_ips=allowed_ips,
                allowed_domains=allowed_domains,
                expires_at=expires_at
            )
            
            # Store the key
            success = await self.storage.store_key(api_key)
            if not success:
                raise APIKeyError("Failed to store API key")
            
            self.logger.info(f"Generated API key: {key_id} for {name}")
            return api_key_value, api_key
            
        except Exception as e:
            self.logger.error(f"Key generation failed: {e}")
            raise APIKeyError(f"Key generation failed: {e}")
    
    async def validate_key(self,
                          api_key_value: str,
                          required_permissions: Optional[List[KeyPermission]] = None,
                          client_ip: Optional[str] = None,
                          domain: Optional[str] = None) -> tuple[bool, Optional[APIKey], Optional[str]]:
        """Validate API key with comprehensive security checks"""
        try:
            # Hash the provided key
            key_hash = hashlib.sha256(api_key_value.encode()).hexdigest()
            
            # Retrieve key from storage
            api_key = await self.storage.get_key_by_hash(key_hash)
            if not api_key:
                return False, None, "Invalid API key"
            
            # Check key status
            if api_key.status != KeyStatus.ACTIVE:
                return False, api_key, f"API key is {api_key.status.value}"
            
            # Check expiration
            if api_key.is_expired:
                # Update status to expired
                await self.storage.update_key(api_key.key_id, {"status": KeyStatus.EXPIRED})
                return False, api_key, "API key has expired"
            
            # Check rate limiting
            if not self.rate_limiter.check_rate_limit(
                api_key.key_id, 
                api_key.rate_limit, 
                api_key.rate_limit_window
            ):
                api_key.metrics.rate_limit_hits += 1
                return False, api_key, "Rate limit exceeded"
            
            # Check IP restrictions
            if self.config.require_ip_validation and api_key.allowed_ips:
                if not client_ip or client_ip not in api_key.allowed_ips:
                    return False, api_key, "IP address not allowed"
            
            # Check domain restrictions
            if self.config.require_domain_validation and api_key.allowed_domains:
                if not domain or domain not in api_key.allowed_domains:
                    return False, api_key, "Domain not allowed"
            
            # Check required permissions
            if required_permissions:
                if not any(perm in api_key.permissions for perm in required_permissions):
                    return False, api_key, "Insufficient permissions"
            
            # Update usage metrics
            await self._update_usage_metrics(api_key, client_ip)
            
            return True, api_key, "Valid"
            
        except Exception as e:
            self.logger.error(f"Key validation failed: {e}")
            return False, None, f"Validation error: {e}"
    
    async def rotate_key(self, key_id: str) -> tuple[str, APIKey]:
        """Rotate API key (generate new key, keep same metadata)"""
        try:
            # Get existing key
            existing_key = await self.storage.get_key(key_id)
            if not existing_key:
                raise APIKeyError("API key not found")
            
            # Generate new key value
            key_bytes = secrets.token_bytes(self.config.key_length)
            key_b64 = base64.urlsafe_b64encode(key_bytes).decode().rstrip('=')
            new_api_key_value = f"{self.config.key_prefix}{key_b64}"
            
            # Hash new key
            new_key_hash = hashlib.sha256(new_api_key_value.encode()).hexdigest()
            
            # Update key with new hash
            updates = {
                "key_hash": new_key_hash,
                "last_rotated": datetime.now(),
                "metrics": KeyMetrics()  # Reset metrics
            }
            
            success = await self.storage.update_key(key_id, updates)
            if not success:
                raise APIKeyError("Failed to update key during rotation")
            
            # Get updated key
            updated_key = await self.storage.get_key(key_id)
            
            self.logger.info(f"Rotated API key: {key_id}")
            return new_api_key_value, updated_key
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            raise APIKeyError(f"Key rotation failed: {e}")
    
    async def revoke_key(self, key_id: str, reason: Optional[str] = None) -> bool:
        """Revoke API key"""
        try:
            updates = {
                "status": KeyStatus.REVOKED,
                "description": f"Revoked: {reason}" if reason else "Revoked"
            }
            
            success = await self.storage.update_key(key_id, updates)
            if success:
                self.logger.info(f"Revoked API key: {key_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Key revocation failed: {e}")
            return False
    
    async def list_keys(self, include_metrics: bool = True) -> List[Dict[str, Any]]:
        """List all API keys with optional metrics"""
        try:
            keys = await self.storage.list_keys()
            
            result = []
            for key in keys:
                key_info = {
                    "key_id": key.key_id,
                    "name": key.name,
                    "description": key.description,
                    "permissions": [p.value for p in key.permissions],
                    "status": key.status.value,
                    "created_at": key.created_at.isoformat(),
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                    "days_until_expiry": key.days_until_expiry,
                    "rate_limit": key.rate_limit,
                }
                
                if include_metrics:
                    key_info["metrics"] = {
                        "total_requests": key.metrics.total_requests,
                        "success_rate": key.metrics.success_rate,
                        "last_used": key.metrics.last_used.isoformat() if key.metrics.last_used else None,
                        "days_since_last_use": key.metrics.days_since_last_use,
                        "rate_limit_hits": key.metrics.rate_limit_hits,
                        "unique_ips": len(key.metrics.unique_ips)
                    }
                
                result.append(key_info)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to list keys: {e}")
            return []
    
    async def get_key_stats(self) -> Dict[str, Any]:
        """Get overall key statistics"""
        try:
            all_keys = await self.storage.list_keys()
            
            stats = {
                "total_keys": len(all_keys),
                "active_keys": len([k for k in all_keys if k.status == KeyStatus.ACTIVE]),
                "expired_keys": len([k for k in all_keys if k.is_expired]),
                "revoked_keys": len([k for k in all_keys if k.status == KeyStatus.REVOKED]),
                "keys_expiring_soon": len([k for k in all_keys if k.days_until_expiry and k.days_until_expiry <= 7]),
                "total_requests": sum(k.metrics.total_requests for k in all_keys),
                "average_success_rate": sum(k.metrics.success_rate for k in all_keys) / len(all_keys) if all_keys else 0,
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get key stats: {e}")
            return {}
    
    async def _update_usage_metrics(self, api_key: APIKey, client_ip: Optional[str]):
        """Update key usage metrics"""
        try:
            # Update metrics
            api_key.metrics.total_requests += 1
            api_key.metrics.successful_requests += 1
            api_key.metrics.last_used = datetime.now()
            
            if not api_key.metrics.first_used:
                api_key.metrics.first_used = datetime.now()
            
            if client_ip:
                api_key.metrics.unique_ips.add(client_ip)
            
            # Persist updated metrics
            await self.storage.update_key(api_key.key_id, {"metrics": api_key.metrics})
            
        except Exception as e:
            self.logger.error(f"Failed to update usage metrics: {e}")
    
    async def cleanup_expired_keys(self) -> int:
        """Clean up expired keys"""
        try:
            all_keys = await self.storage.list_keys()
            cleaned_count = 0
            
            for key in all_keys:
                if key.is_expired and key.status == KeyStatus.ACTIVE:
                    await self.storage.update_key(key.key_id, {"status": KeyStatus.EXPIRED})
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} expired keys")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 0


# Example usage
async def example_api_key_usage():
    """Example API key management usage"""
    # Create configuration
    config = APIKeyConfig(
        key_prefix="ainflue_",
        encryption_key="your-encryption-password",
        default_rate_limit=5000,
        auto_rotation_enabled=True,
        rotation_interval_days=90
    )
    
    # Create key manager
    key_manager = APIKeyManager(config)
    
    # Generate a new API key
    api_key_value, api_key = await key_manager.generate_key(
        name="test-application",
        description="API key for test application",
        permissions=[KeyPermission.READ, KeyPermission.WRITE],
        rate_limit=2000,
        expires_in_days=365,
        allowed_ips=["192.168.1.100", "10.0.0.50"]
    )
    
    print(f"Generated API key: {api_key_value}")
    print(f"Key ID: {api_key.key_id}")
    
    # Validate the key
    is_valid, key_obj, message = await key_manager.validate_key(
        api_key_value,
        required_permissions=[KeyPermission.READ],
        client_ip="192.168.1.100"
    )
    
    print(f"Key validation: {is_valid}, {message}")
    
    # List all keys
    keys = await key_manager.list_keys()
    print(f"Total keys: {len(keys)}")
    
    # Get statistics
    stats = await key_manager.get_key_stats()
    print(f"Key statistics: {stats}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_api_key_usage())