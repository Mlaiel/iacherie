"""Digital Rights Management Template for iacherie Creator Protection

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Enterprise Digital Rights Management Expert
"""

import hashlib
import hmac
import base64
import json
import logging
from typing import Dict, Any, Optional, List, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
from pathlib import Path

from pydantic import BaseModel, Field, validator
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from core.config import get_settings
from utils.exceptions import DRMError, LicenseError, AccessDeniedError
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    NFT = "nft"


class UsageRight(Enum):
    """Individual usage rights"""
    VIEW = "view"
    DOWNLOAD = "download"
    SHARE = "share"
    MODIFY = "modify"
    DISTRIBUTE = "distribute"
    COMMERCIAL_USE = "commercial_use"
    PRINT = "print"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    REMIX = "remix"


class ProtectionLevel(Enum):
    """Content protection levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"
    MILITARY_GRADE = "military_grade"


class LicenseStatus(Enum):
    """License status values"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING = "pending"
    TRANSFERRED = "transferred"


class DRMConfig(BaseModel):
    """DRM configuration model"""
    content_id: str = Field(..., min_length=1)
    creator_id: str = Field(..., min_length=1)
    license_type: LicenseType
    protection_level: ProtectionLevel = ProtectionLevel.STANDARD
    usage_rights: Set[UsageRight] = Field(default_factory=set)
    geographic_restrictions: List[str] = Field(default_factory=list)
    device_restrictions: Dict[str, Any] = Field(default_factory=dict)
    time_restrictions: Dict[str, datetime] = Field(default_factory=dict)
    copy_protection: bool = True
    watermarking_enabled: bool = True
    blockchain_anchored: bool = False
    
    @validator('usage_rights')
    def validate_usage_rights(cls, v):
        if not v:
            return {UsageRight.VIEW}
        return v


class LicenseMetadata(BaseModel):
    """License metadata structure"""
    license_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    issuer: str
    recipient: str
    content_fingerprint: str
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    usage_count: int = 0
    max_usage_count: Optional[int] = None
    device_bindings: List[str] = Field(default_factory=list)
    transfer_history: List[Dict[str, Any]] = Field(default_factory=list)
    revenue_terms: Dict[str, Any] = Field(default_factory=dict)


class AccessPolicy(BaseModel):
    """Content access policy"""
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    allowed_users: Set[str] = Field(default_factory=set)
    allowed_groups: Set[str] = Field(default_factory=set)
    allowed_devices: Set[str] = Field(default_factory=set)
    time_windows: List[Tuple[datetime, datetime]] = Field(default_factory=list)
    ip_restrictions: List[str] = Field(default_factory=list)
    concurrent_access_limit: Optional[int] = None
    bandwidth_restrictions: Dict[str, int] = Field(default_factory=dict)


class DigitalRightsManagementTemplate:
    """Enterprise-grade digital rights management system for creator protection"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize DRM template
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics = SecurityMetricsCollector()
        self._initialize_drm_system()
        
    def _initialize_drm_system(self) -> None:
        """Initialize DRM system components"""
        try:
            # Initialize encryption keys
            self.master_key = self.config.get('master_key', settings.DRM_MASTER_KEY)
            self.license_signing_key = self.config.get('license_signing_key', settings.DRM_SIGNING_KEY)
            
            # Initialize key derivation
            self.key_derivation_salt = self.config.get('salt', settings.DRM_SALT)
            
            # Initialize blockchain integration if enabled
            self.blockchain_enabled = self.config.get('blockchain_enabled', False)
            self.blockchain_network = self.config.get('blockchain_network', 'ethereum')
            
            # Initialize content encryption
            self.content_cipher = Fernet(base64.urlsafe_b64encode(self.master_key[:32]))
            
            # Initialize license storage
            self.license_store = {}
            self.access_policies = {}
            
            self.logger.info("DRM system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DRM system: {e}")
            raise DRMError(f"DRM initialization failed: {e}")
    
    def protect_content(self, content: bytes, drm_config: DRMConfig) -> Tuple[bytes, Dict[str, Any]]:
        """Apply DRM protection to content
        
        Args:
            content: Raw content to protect
            drm_config: DRM configuration
            
        Returns:
            Tuple of (protected_content, drm_metadata)
        """
        try:
            self.logger.info(f"Applying DRM protection to content {drm_config.content_id}")
            
            # Generate content fingerprint
            content_fingerprint = self._generate_content_fingerprint(content)
            
            # Encrypt content based on protection level
            if drm_config.protection_level == ProtectionLevel.NONE:
                protected_content = content
                encryption_metadata = {'encrypted': False}
            else:
                protected_content, encryption_metadata = self._encrypt_content(content, drm_config)
            
            # Generate DRM metadata
            drm_metadata = self._generate_drm_metadata(drm_config, content_fingerprint, encryption_metadata)
            
            # Apply additional protection measures
            if drm_config.copy_protection:
                protected_content = self._apply_copy_protection(protected_content, drm_config)
            
            # Create content access policy
            access_policy = self._create_access_policy(drm_config)
            self.access_policies[drm_config.content_id] = access_policy
            
            # Anchor to blockchain if enabled
            if drm_config.blockchain_anchored:
                blockchain_hash = self._anchor_to_blockchain(drm_config, drm_metadata)
                drm_metadata['blockchain_hash'] = blockchain_hash
            
            # Log protection metrics
            self.metrics.increment_counter('content_protected', {
                'protection_level': drm_config.protection_level.value,
                'license_type': drm_config.license_type.value
            })
            
            return protected_content, drm_metadata
            
        except Exception as e:
            self.logger.error(f"Failed to protect content: {e}")
            self.metrics.increment_counter('drm_protection_errors')
            raise DRMError(f"Content protection failed: {e}")
    
    def issue_license(self, drm_config: DRMConfig, recipient: str, 
                     custom_terms: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Issue content license to user
        
        Args:
            drm_config: DRM configuration
            recipient: License recipient identifier
            custom_terms: Optional custom license terms
            
        Returns:
            License data dictionary
        """
        try:
            self.logger.info(f"Issuing {drm_config.license_type.value} license for content {drm_config.content_id} to {recipient}")
            
            # Create license metadata
            license_metadata = LicenseMetadata(
                issuer=drm_config.creator_id,
                recipient=recipient,
                content_fingerprint=self._generate_content_fingerprint_from_id(drm_config.content_id)
            )
            
            # Apply custom terms if provided
            if custom_terms:
                license_metadata.revenue_terms.update(custom_terms.get('revenue_terms', {}))
                if 'expiration_date' in custom_terms:
                    license_metadata.expiration_date = custom_terms['expiration_date']
                if 'max_usage_count' in custom_terms:
                    license_metadata.max_usage_count = custom_terms['max_usage_count']
            
            # Generate license key
            license_key = self._generate_license_key(drm_config, license_metadata)
            
            # Create license document
            license_document = self._create_license_document(drm_config, license_metadata, license_key)
            
            # Sign license
            signed_license = self._sign_license(license_document)
            
            # Store license
            self.license_store[license_metadata.license_id] = {
                'license': signed_license,
                'metadata': license_metadata,
                'status': LicenseStatus.ACTIVE,
                'config': drm_config
            }
            
            # Log license issuance
            self.metrics.increment_counter('licenses_issued', {
                'license_type': drm_config.license_type.value,
                'recipient': recipient
            })
            
            return {
                'license_id': license_metadata.license_id,
                'license_key': license_key,
                'license_document': signed_license,
                'access_url': self._generate_access_url(license_metadata.license_id),
                'terms': self._get_license_terms(drm_config, license_metadata)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to issue license: {e}")
            self.metrics.increment_counter('license_issuance_errors')
            raise LicenseError(f"License issuance failed: {e}")
    
    def validate_access(self, content_id: str, user_id: str, 
                       requested_rights: Set[UsageRight],
                       device_id: Optional[str] = None,
                       ip_address: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """Validate user access to protected content
        
        Args:
            content_id: Content identifier
            user_id: User identifier
            requested_rights: Requested usage rights
            device_id: Optional device identifier
            ip_address: Optional IP address
            
        Returns:
            Tuple of (access_granted, access_details)
        """
        try:
            self.logger.info(f"Validating access for user {user_id} to content {content_id}")
            
            # Find active license for user and content
            license_data = self._find_user_license(content_id, user_id)
            if not license_data:
                return False, {'error': 'No valid license found', 'code': 'NO_LICENSE'}
            
            # Check license status
            if license_data['status'] != LicenseStatus.ACTIVE:
                return False, {'error': 'License not active', 'code': 'INACTIVE_LICENSE'}
            
            # Check expiration
            if self._is_license_expired(license_data['metadata']):
                self._update_license_status(license_data['metadata'].license_id, LicenseStatus.EXPIRED)
                return False, {'error': 'License expired', 'code': 'EXPIRED_LICENSE'}
            
            # Check usage limits
            if not self._check_usage_limits(license_data['metadata']):
                return False, {'error': 'Usage limit exceeded', 'code': 'USAGE_LIMIT_EXCEEDED'}
            
            # Check requested rights
            if not self._check_usage_rights(license_data['config'], requested_rights):
                return False, {'error': 'Insufficient rights', 'code': 'INSUFFICIENT_RIGHTS'}
            
            # Check access policy
            access_policy = self.access_policies.get(content_id)
            if access_policy and not self._check_access_policy(access_policy, user_id, device_id, ip_address):
                return False, {'error': 'Access policy violation', 'code': 'POLICY_VIOLATION'}
            
            # Check device restrictions
            if device_id and not self._check_device_restrictions(license_data['config'], device_id):
                return False, {'error': 'Device not authorized', 'code': 'DEVICE_RESTRICTED'}
            
            # Check geographic restrictions
            if ip_address and not self._check_geographic_restrictions(license_data['config'], ip_address):
                return False, {'error': 'Geographic restriction', 'code': 'GEO_RESTRICTED'}
            
            # Update usage tracking
            self._update_usage_tracking(license_data['metadata'])
            
            # Log successful access
            self.metrics.increment_counter('access_granted', {
                'content_id': content_id,
                'user_id': user_id,
                'rights': [right.value for right in requested_rights]
            })
            
            return True, {
                'license_id': license_data['metadata'].license_id,
                'granted_rights': list(requested_rights),
                'access_url': self._generate_secure_access_url(content_id, user_id),
                'session_token': self._generate_session_token(content_id, user_id),
                'expires_at': license_data['metadata'].expiration_date
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate access: {e}")
            self.metrics.increment_counter('access_validation_errors')
            return False, {'error': 'Validation failed', 'code': 'VALIDATION_ERROR'}
    
    def decrypt_content(self, protected_content: bytes, license_key: str,
                       user_id: str) -> bytes:
        """Decrypt protected content for authorized user
        
        Args:
            protected_content: DRM-protected content
            license_key: User's license key
            user_id: User identifier
            
        Returns:
            Decrypted content
        """
        try:
            self.logger.info(f"Decrypting content for user {user_id}")
            
            # Validate license key
            if not self._validate_license_key(license_key, user_id):
                raise AccessDeniedError("Invalid license key")
            
            # Extract DRM metadata from content
            drm_metadata = self._extract_drm_metadata(protected_content)
            
            # Decrypt content based on protection level
            content_encryption_key = self._derive_content_key(license_key, drm_metadata)
            decrypted_content = self._decrypt_content_data(protected_content, content_encryption_key)
            
            # Log decryption activity
            self.metrics.increment_counter('content_decrypted', {
                'user_id': user_id,
                'content_id': drm_metadata.get('content_id')
            })
            
            return decrypted_content
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt content: {e}")
            self.metrics.increment_counter('decryption_errors')
            raise DRMError(f"Content decryption failed: {e}")
    
    def revoke_license(self, license_id: str, reason: str, 
                      revoker_id: str) -> bool:
        """Revoke content license
        
        Args:
            license_id: License identifier
            reason: Revocation reason
            revoker_id: Who is revoking the license
            
        Returns:
            True if successfully revoked
        """
        try:
            self.logger.info(f"Revoking license {license_id} by {revoker_id}")
            
            # Find license
            license_data = self.license_store.get(license_id)
            if not license_data:
                raise LicenseError("License not found")
            
            # Check revocation authorization
            if not self._authorize_license_revocation(license_data, revoker_id):
                raise AccessDeniedError("Unauthorized license revocation")
            
            # Update license status
            license_data['status'] = LicenseStatus.REVOKED
            license_data['revocation_info'] = {
                'revoked_by': revoker_id,
                'revoked_at': datetime.utcnow(),
                'reason': reason
            }
            
            # Add to blockchain if enabled
            if license_data['config'].blockchain_anchored:
                self._record_revocation_on_blockchain(license_id, reason)
            
            # Log revocation
            self.metrics.increment_counter('licenses_revoked', {
                'license_id': license_id,
                'reason': reason
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke license: {e}")
            self.metrics.increment_counter('license_revocation_errors')
            raise LicenseError(f"License revocation failed: {e}")
    
    def transfer_license(self, license_id: str, new_recipient: str,
                        current_holder: str) -> Dict[str, Any]:
        """Transfer license to new recipient
        
        Args:
            license_id: License identifier
            new_recipient: New license holder
            current_holder: Current license holder
            
        Returns:
            Transfer result data
        """
        try:
            self.logger.info(f"Transferring license {license_id} from {current_holder} to {new_recipient}")
            
            # Find and validate current license
            license_data = self.license_store.get(license_id)
            if not license_data:
                raise LicenseError("License not found")
            
            if license_data['metadata'].recipient != current_holder:
                raise AccessDeniedError("Current holder mismatch")
            
            # Check if license is transferable
            if not self._is_license_transferable(license_data):
                raise LicenseError("License not transferable")
            
            # Create transfer record
            transfer_record = {
                'transfer_id': str(uuid.uuid4()),
                'from_user': current_holder,
                'to_user': new_recipient,
                'transfer_date': datetime.utcnow(),
                'license_id': license_id
            }
            
            # Update license recipient
            license_data['metadata'].recipient = new_recipient
            license_data['metadata'].transfer_history.append(transfer_record)
            license_data['status'] = LicenseStatus.TRANSFERRED
            
            # Generate new license key for new recipient
            new_license_key = self._generate_license_key(license_data['config'], license_data['metadata'])
            
            # Record on blockchain if enabled
            if license_data['config'].blockchain_anchored:
                self._record_transfer_on_blockchain(transfer_record)
            
            # Log transfer
            self.metrics.increment_counter('licenses_transferred', {
                'from_user': current_holder,
                'to_user': new_recipient
            })
            
            return {
                'transfer_id': transfer_record['transfer_id'],
                'new_license_key': new_license_key,
                'transfer_date': transfer_record['transfer_date'],
                'status': 'completed'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to transfer license: {e}")
            self.metrics.increment_counter('license_transfer_errors')
            raise LicenseError(f"License transfer failed: {e}")
    
    def audit_content_access(self, content_id: str, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Audit content access history
        
        Args:
            content_id: Content identifier
            start_date: Optional audit start date
            end_date: Optional audit end date
            
        Returns:
            Audit report data
        """
        try:
            self.logger.info(f"Auditing access for content {content_id}")
            
            # Collect access logs
            access_logs = self._get_access_logs(content_id, start_date, end_date)
            
            # Collect license information
            content_licenses = self._get_content_licenses(content_id)
            
            # Generate statistics
            stats = {
                'total_accesses': len(access_logs),
                'unique_users': len(set(log['user_id'] for log in access_logs)),
                'total_licenses': len(content_licenses),
                'active_licenses': len([l for l in content_licenses if l['status'] == LicenseStatus.ACTIVE]),
                'access_by_right': self._calculate_access_by_right(access_logs),
                'geographic_distribution': self._calculate_geographic_distribution(access_logs),
                'device_distribution': self._calculate_device_distribution(access_logs)
            }
            
            # Detect anomalies
            anomalies = self._detect_access_anomalies(access_logs)
            
            audit_report = {
                'content_id': content_id,
                'audit_period': {
                    'start': start_date or datetime.min,
                    'end': end_date or datetime.utcnow()
                },
                'statistics': stats,
                'access_logs': access_logs,
                'licenses': content_licenses,
                'anomalies': anomalies,
                'generated_at': datetime.utcnow()
            }
            
            return audit_report
            
        except Exception as e:
            self.logger.error(f"Failed to audit content access: {e}")
            raise DRMError(f"Access audit failed: {e}")
    
    # Helper methods
    def _encrypt_content(self, content: bytes, drm_config: DRMConfig) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt content based on protection level"""
        if drm_config.protection_level == ProtectionLevel.BASIC:
            # Simple Fernet encryption
            encrypted_content = self.content_cipher.encrypt(content)
            metadata = {'algorithm': 'Fernet', 'key_derivation': 'static'}
            
        elif drm_config.protection_level == ProtectionLevel.STANDARD:
            # AES-256-GCM encryption
            encrypted_content, metadata = self._encrypt_with_aes_gcm(content, drm_config)
            
        elif drm_config.protection_level == ProtectionLevel.ENHANCED:
            # AES-256-GCM with key derivation
            encrypted_content, metadata = self._encrypt_with_enhanced_aes(content, drm_config)
            
        elif drm_config.protection_level == ProtectionLevel.MAXIMUM:
            # Multiple encryption layers
            encrypted_content, metadata = self._encrypt_with_multiple_layers(content, drm_config)
            
        elif drm_config.protection_level == ProtectionLevel.MILITARY_GRADE:
            # Military-grade encryption with hardware security
            encrypted_content, metadata = self._encrypt_military_grade(content, drm_config)
            
        else:
            raise DRMError(f"Unsupported protection level: {drm_config.protection_level}")
        
        metadata['encrypted'] = True
        metadata['protection_level'] = drm_config.protection_level.value
        
        return encrypted_content, metadata
    
    def _generate_content_fingerprint(self, content: bytes) -> str:
        """Generate unique content fingerprint"""
        return hashlib.sha256(content).hexdigest()
    
    def _generate_license_key(self, drm_config: DRMConfig, metadata: LicenseMetadata) -> str:
        """Generate license key for user"""
        key_data = f"{drm_config.content_id}:{metadata.recipient}:{metadata.license_id}:{self.master_key}"
        license_key = hashlib.pbkdf2_hmac('sha256', key_data.encode(), self.key_derivation_salt, 100000)
        return base64.urlsafe_b64encode(license_key).decode()
    
    def _generate_drm_metadata(self, drm_config: DRMConfig, content_fingerprint: str,
                             encryption_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive DRM metadata"""
        return {
            'drm_version': '4.0.0',
            'content_id': drm_config.content_id,
            'creator_id': drm_config.creator_id,
            'content_fingerprint': content_fingerprint,
            'protection_level': drm_config.protection_level.value,
            'license_type': drm_config.license_type.value,
            'usage_rights': [right.value for right in drm_config.usage_rights],
            'encryption': encryption_metadata,
            'copy_protection': drm_config.copy_protection,
            'watermarking_enabled': drm_config.watermarking_enabled,
            'created_at': datetime.utcnow().isoformat(),
            'signature': self._sign_metadata(drm_config, content_fingerprint)
        }
    
    def _sign_metadata(self, drm_config: DRMConfig, content_fingerprint: str) -> str:
        """Sign DRM metadata for integrity verification"""
        data = f"{drm_config.content_id}:{drm_config.creator_id}:{content_fingerprint}"
        signature = hmac.new(
            self.license_signing_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _create_access_policy(self, drm_config: DRMConfig) -> AccessPolicy:
        """Create access policy from DRM configuration"""
        return AccessPolicy(
            content_id=drm_config.content_id,
            ip_restrictions=drm_config.geographic_restrictions,
            concurrent_access_limit=drm_config.device_restrictions.get('max_concurrent', None),
            bandwidth_restrictions=drm_config.device_restrictions.get('bandwidth', {})
        )
    
    # Additional helper methods would be implemented here...
    # (Continuing with license validation, blockchain integration, etc.)


class LicenseManager:
    """Advanced license management and tracking system"""
    
    def __init__(self, drm_template: DigitalRightsManagementTemplate):
        """Initialize license manager
        
        Args:
            drm_template: DRM template instance
        """
        self.drm = drm_template
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def bulk_issue_licenses(self, content_configs: List[Tuple[DRMConfig, str]]) -> List[Dict[str, Any]]:
        """Issue multiple licenses in batch
        
        Args:
            content_configs: List of (DRMConfig, recipient) tuples
            
        Returns:
            List of issued license data
        """
        results = []
        for drm_config, recipient in content_configs:
            try:
                license_data = self.drm.issue_license(drm_config, recipient)
                results.append({
                    'success': True,
                    'license_data': license_data,
                    'content_id': drm_config.content_id,
                    'recipient': recipient
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'content_id': drm_config.content_id,
                    'recipient': recipient
                })
        
        return results
    
    def generate_usage_report(self, creator_id: str) -> Dict[str, Any]:
        """Generate comprehensive usage report for creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Usage report data
        """
        # Collect creator's content
        creator_content = self._get_creator_content(creator_id)
        
        # Collect usage statistics
        usage_stats = {}
        for content_id in creator_content:
            audit_data = self.drm.audit_content_access(content_id)
            usage_stats[content_id] = audit_data['statistics']
        
        # Calculate revenue
        revenue_data = self._calculate_creator_revenue(creator_id, usage_stats)
        
        return {
            'creator_id': creator_id,
            'content_count': len(creator_content),
            'usage_statistics': usage_stats,
            'revenue_data': revenue_data,
            'generated_at': datetime.utcnow()
        }


# Export main components
__all__ = [
    'DigitalRightsManagementTemplate',
    'LicenseManager',
    'LicenseType',
    'UsageRight',
    'ProtectionLevel',
    'LicenseStatus',
    'DRMConfig',
    'LicenseMetadata',
    'AccessPolicy'
]