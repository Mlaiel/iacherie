"""
Digital Rights Management System
================================

Enterprise-grade DRM system for content protection and rights management.
Integrates with existing protection infrastructure and provides comprehensive
content usage control and license management.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import hashlib
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class LicenseType(Enum):
    """Content license types"""
    VIEW_ONLY = "view_only"
    DOWNLOAD = "download"
    MODIFY = "modify"
    REDISTRIBUTE = "redistribute"
    COMMERCIAL = "commercial"
    EXCLUSIVE = "exclusive"


class ContentType(Enum):
    """Supported content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"


@dataclass
class DRMPolicy:
    """Digital Rights Management policy definition"""
    policy_id: str
    content_id: str
    license_type: LicenseType
    content_type: ContentType
    owner_id: str
    usage_limits: Dict[str, Any]
    expiration_date: Optional[datetime] = None
    geographical_restrictions: List[str] = None
    device_limits: int = 5
    concurrent_access_limit: int = 1
    watermark_required: bool = True
    encryption_required: bool = True
    audit_logging: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.geographical_restrictions is None:
            self.geographical_restrictions = []


@dataclass
class DRMLicense:
    """DRM license for content access"""
    license_id: str
    policy_id: str
    user_id: str
    content_id: str
    access_token: str
    issued_at: datetime
    expires_at: datetime
    usage_count: int = 0
    last_accessed: Optional[datetime] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    status: str = "active"


class DigitalRightsManagement:
    """
    Enterprise Digital Rights Management System
    
    Provides comprehensive content protection through:
    - License management and enforcement
    - Content encryption and decryption
    - Usage tracking and analytics
    - Access control and authentication
    - Compliance monitoring
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize DRM system"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Storage for policies and licenses (in production, use database)
        self.policies: Dict[str, DRMPolicy] = {}
        self.licenses: Dict[str, DRMLicense] = {}
        self.usage_logs: List[Dict] = []
        
        # Performance monitoring
        self.metrics = {
            'licenses_issued': 0,
            'licenses_validated': 0,
            'licenses_revoked': 0,
            'policy_violations': 0,
            'content_accesses': 0
        }
        
        self.logger.info("Digital Rights Management system initialized")

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for content protection"""
        password = self.config.get('drm_password', 'ainflue-drm-default-key').encode()
        salt = self.config.get('drm_salt', b'ainflue-salt-2025')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    async def create_policy(self, 
                          content_id: str,
                          owner_id: str,
                          license_type: LicenseType,
                          content_type: ContentType,
                          **kwargs) -> DRMPolicy:
        """Create a new DRM policy for content"""
        policy_id = str(uuid.uuid4())
        
        # Default usage limits
        default_limits = {
            'max_views': kwargs.get('max_views', 1000),
            'max_downloads': kwargs.get('max_downloads', 10),
            'max_shares': kwargs.get('max_shares', 5),
            'time_limit_minutes': kwargs.get('time_limit_minutes', 1440),  # 24 hours
        }
        
        policy = DRMPolicy(
            policy_id=policy_id,
            content_id=content_id,
            license_type=license_type,
            content_type=content_type,
            owner_id=owner_id,
            usage_limits=default_limits,
            **kwargs
        )
        
        self.policies[policy_id] = policy
        
        await self._log_audit_event("policy_created", {
            'policy_id': policy_id,
            'content_id': content_id,
            'owner_id': owner_id,
            'license_type': license_type.value
        })
        
        self.logger.info(f"DRM policy created: {policy_id} for content: {content_id}")
        return policy

    async def issue_license(self, 
                          policy_id: str,
                          user_id: str,
                          device_fingerprint: str = None,
                          ip_address: str = None) -> DRMLicense:
        """Issue a new license for content access"""
        
        if policy_id not in self.policies:
            raise ValueError(f"Policy not found: {policy_id}")
        
        policy = self.policies[policy_id]
        license_id = str(uuid.uuid4())
        
        # Generate secure access token
        token_data = {
            'license_id': license_id,
            'user_id': user_id,
            'content_id': policy.content_id,
            'issued_at': datetime.utcnow().isoformat()
        }
        access_token = self._encrypt_data(json.dumps(token_data))
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(
            minutes=policy.usage_limits.get('time_limit_minutes', 1440)
        )
        
        license = DRMLicense(
            license_id=license_id,
            policy_id=policy_id,
            user_id=user_id,
            content_id=policy.content_id,
            access_token=access_token,
            issued_at=datetime.utcnow(),
            expires_at=expires_at,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address
        )
        
        self.licenses[license_id] = license
        self.metrics['licenses_issued'] += 1
        
        await self._log_audit_event("license_issued", {
            'license_id': license_id,
            'policy_id': policy_id,
            'user_id': user_id,
            'content_id': policy.content_id
        })
        
        self.logger.info(f"License issued: {license_id} for user: {user_id}")
        return license

    async def validate_license(self, access_token: str, 
                             usage_type: str = "view") -> bool:
        """Validate license and check permissions"""
        try:
            # Decrypt and validate token
            token_data = json.loads(self._decrypt_data(access_token))
            license_id = token_data.get('license_id')
            
            if license_id not in self.licenses:
                self.logger.warning(f"License not found: {license_id}")
                return False
            
            license = self.licenses[license_id]
            policy = self.policies[license.policy_id]
            
            # Check expiration
            if datetime.utcnow() > license.expires_at:
                self.logger.warning(f"License expired: {license_id}")
                return False
            
            # Check usage limits
            if not await self._check_usage_limits(license, policy, usage_type):
                return False
            
            # Update usage tracking
            license.usage_count += 1
            license.last_accessed = datetime.utcnow()
            self.metrics['licenses_validated'] += 1
            
            await self._log_audit_event("license_validated", {
                'license_id': license_id,
                'user_id': license.user_id,
                'usage_type': usage_type,
                'content_id': license.content_id
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"License validation failed: {str(e)}")
            return False

    async def revoke_license(self, license_id: str, reason: str = "user_request") -> bool:
        """Revoke a license"""
        if license_id not in self.licenses:
            return False
        
        license = self.licenses[license_id]
        license.status = "revoked"
        self.metrics['licenses_revoked'] += 1
        
        await self._log_audit_event("license_revoked", {
            'license_id': license_id,
            'user_id': license.user_id,
            'reason': reason,
            'content_id': license.content_id
        })
        
        self.logger.info(f"License revoked: {license_id}, reason: {reason}")
        return True

    async def encrypt_content(self, content: bytes, policy_id: str) -> bytes:
        """Encrypt content according to DRM policy"""
        if policy_id not in self.policies:
            raise ValueError(f"Policy not found: {policy_id}")
        
        policy = self.policies[policy_id]
        
        if not policy.encryption_required:
            return content
        
        # Add DRM metadata header
        drm_header = {
            'policy_id': policy_id,
            'content_id': policy.content_id,
            'encryption_version': '1.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        header_bytes = json.dumps(drm_header).encode()
        header_length = len(header_bytes).to_bytes(4, byteorder='big')
        
        # Encrypt content
        encrypted_content = self.cipher_suite.encrypt(content)
        
        # Combine header + content
        protected_content = header_length + header_bytes + encrypted_content
        
        self.logger.info(f"Content encrypted for policy: {policy_id}")
        return protected_content

    async def decrypt_content(self, protected_content: bytes, access_token: str) -> bytes:
        """Decrypt content with valid access token"""
        try:
            # Extract header
            header_length = int.from_bytes(protected_content[:4], byteorder='big')
            header_bytes = protected_content[4:4+header_length]
            encrypted_content = protected_content[4+header_length:]
            
            drm_header = json.loads(header_bytes.decode())
            
            # Validate access token
            if not await self.validate_license(access_token, "view"):
                raise PermissionError("Invalid or expired license")
            
            # Decrypt content
            content = self.cipher_suite.decrypt(encrypted_content)
            
            self.metrics['content_accesses'] += 1
            self.logger.info(f"Content decrypted for policy: {drm_header['policy_id']}")
            return content
            
        except Exception as e:
            self.logger.error(f"Content decryption failed: {str(e)}")
            raise

    async def _check_usage_limits(self, license: DRMLicense, 
                                policy: DRMPolicy, usage_type: str) -> bool:
        """Check if usage is within policy limits"""
        limits = policy.usage_limits
        
        # Check usage count limits
        if usage_type == "view" and license.usage_count >= limits.get('max_views', float('inf')):
            self.metrics['policy_violations'] += 1
            return False
        
        if usage_type == "download" and license.usage_count >= limits.get('max_downloads', float('inf')):
            self.metrics['policy_violations'] += 1
            return False
        
        # Additional checks can be added here for other usage types
        return True

    def _encrypt_data(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    async def _log_audit_event(self, event_type: str, data: Dict):
        """Log audit event for compliance"""
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data,
            'system': 'drm'
        }
        self.usage_logs.append(audit_entry)

    async def get_policy_analytics(self, policy_id: str) -> Dict[str, Any]:
        """Get analytics for a specific policy"""
        if policy_id not in self.policies:
            return {}
        
        policy = self.policies[policy_id]
        
        # Count licenses for this policy
        policy_licenses = [l for l in self.licenses.values() if l.policy_id == policy_id]
        
        analytics = {
            'policy_id': policy_id,
            'content_id': policy.content_id,
            'total_licenses': len(policy_licenses),
            'active_licenses': len([l for l in policy_licenses if l.status == 'active']),
            'total_usage': sum(l.usage_count for l in policy_licenses),
            'last_access': max([l.last_accessed for l in policy_licenses if l.last_accessed], default=None),
            'created_at': policy.created_at.isoformat()
        }
        
        return analytics

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall DRM system metrics"""
        return {
            'metrics': self.metrics,
            'total_policies': len(self.policies),
            'total_licenses': len(self.licenses),
            'audit_logs': len(self.usage_logs),
            'system_status': 'operational'
        }

    async def cleanup_expired_licenses(self) -> int:
        """Clean up expired licenses"""
        current_time = datetime.utcnow()
        expired_count = 0
        
        for license_id, license in list(self.licenses.items()):
            if current_time > license.expires_at and license.status == 'active':
                license.status = 'expired'
                expired_count += 1
                
                await self._log_audit_event("license_expired", {
                    'license_id': license_id,
                    'user_id': license.user_id,
                    'content_id': license.content_id
                })
        
        self.logger.info(f"Cleaned up {expired_count} expired licenses")
        return expired_count


# Utility functions
async def create_drm_system(config: Dict[str, Any] = None) -> DigitalRightsManagement:
    """Factory function to create DRM system"""
    drm = DigitalRightsManagement(config)
    return drm


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate DRM system capabilities"""
        drm = await create_drm_system()
        
        # Create policy
        policy = await drm.create_policy(
            content_id="audio_123",
            owner_id="creator_456",
            license_type=LicenseType.VIEW_ONLY,
            content_type=ContentType.AUDIO,
            max_views=100,
            time_limit_minutes=2880  # 48 hours
        )
        
        # Issue license
        license = await drm.issue_license(
            policy.policy_id,
            user_id="user_789",
            device_fingerprint="device_abc"
        )
        
        # Validate license
        is_valid = await drm.validate_license(license.access_token)
        print(f"License valid: {is_valid}")
        
        # Get analytics
        analytics = await drm.get_policy_analytics(policy.policy_id)
        print(f"Policy analytics: {analytics}")
        
        metrics = await drm.get_system_metrics()
        print(f"System metrics: {metrics}")
    
    asyncio.run(demo())