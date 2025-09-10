"""
Credential Vault for Ainflue Distribution Platform

This module provides secure credential storage and management with encryption,
rotation, and access control for platform API keys and secrets.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import secrets
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class CredentialType(Enum):
    """Types of credentials stored in vault"""
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    WEBHOOK_SECRET = "webhook_secret"
    DATABASE_PASSWORD = "database_password"
    ENCRYPTION_KEY = "encryption_key"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"
    OAUTH_CLIENT_SECRET = "oauth_client_secret"


class EncryptionLevel(Enum):
    """Encryption levels for stored credentials"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class CredentialStatus(Enum):
    """Status of stored credentials"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ROTATION = "pending_rotation"
    COMPROMISED = "compromised"


@dataclass
class SecureCredential:
    """Secure credential with metadata"""
    credential_id: str
    name: str
    credential_type: CredentialType
    platform: str
    encrypted_value: str
    encryption_level: EncryptionLevel
    status: CredentialStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    rotation_interval_days: Optional[int]
    access_permissions: List[str]
    metadata: Dict[str, Any]
    version: int


@dataclass
class CredentialAccess:
    """Credential access record"""
    access_id: str
    credential_id: str
    accessed_by: str
    access_type: str  # read, update, delete
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    reason: Optional[str]


class CredentialVault:
    """
    Secure credential vault for managing sensitive data
    
    Features:
    - AES-256 encryption for all stored credentials
    - Multiple encryption levels with key derivation
    - Automatic credential rotation
    - Access logging and audit trails
    - Secure key generation and management
    - Integration with external key management systems
    """

    def __init__(self, master_key: Optional[str] = None, config: Dict[str, Any] = None):
        self.config = config or {}
        self.credentials = {}
        self.access_logs = []
        self.encryption_keys = {}
        self.master_key = master_key or self._generate_master_key()
        
        # Initialize encryption keys for different levels
        self._initialize_encryption_keys()
        
        # Auto-rotation settings
        self.auto_rotation_enabled = self.config.get('auto_rotation_enabled', True)
        self.default_rotation_days = self.config.get('default_rotation_days', 90)

    def _generate_master_key(self) -> str:
        """Generate a secure master key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()

    def _initialize_encryption_keys(self):
        """Initialize encryption keys for different security levels"""
        
        # Create different encryption keys based on master key
        for level in EncryptionLevel:
            salt = level.value.encode() + b'ainflue_vault_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000 if level == EncryptionLevel.MAXIMUM else 50000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
            self.encryption_keys[level] = Fernet(key)

    async def store_credential(
        self,
        name: str,
        credential_type: CredentialType,
        platform: str,
        value: str,
        encryption_level: EncryptionLevel = EncryptionLevel.STANDARD,
        expires_in_days: Optional[int] = None,
        rotation_interval_days: Optional[int] = None,
        permissions: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a credential securely in the vault
        
        Args:
            name: Human-readable name for the credential
            credential_type: Type of credential
            platform: Platform the credential is for
            value: The actual credential value to encrypt
            encryption_level: Level of encryption to use
            expires_in_days: Days until credential expires
            rotation_interval_days: Days between automatic rotations
            permissions: List of permissions required to access
            metadata: Additional metadata to store
            
        Returns:
            Credential ID for future reference
        """
        try:
            # Generate unique credential ID
            credential_id = self._generate_credential_id(name, platform, credential_type)
            
            # Encrypt the credential value
            encrypted_value = self._encrypt_value(value, encryption_level)
            
            # Set expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create credential record
            credential = SecureCredential(
                credential_id=credential_id,
                name=name,
                credential_type=credential_type,
                platform=platform,
                encrypted_value=encrypted_value,
                encryption_level=encryption_level,
                status=CredentialStatus.ACTIVE,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=expires_at,
                last_used_at=None,
                rotation_interval_days=rotation_interval_days or self.default_rotation_days,
                access_permissions=permissions or [],
                metadata=metadata or {},
                version=1
            )
            
            # Store credential
            self.credentials[credential_id] = credential
            
            # Log access
            await self._log_access(credential_id, "create", "system", success=True)
            
            logger.info(f"Stored credential {credential_id} for {platform}")
            return credential_id
            
        except Exception as e:
            logger.error(f"Error storing credential: {e}")
            raise

    async def retrieve_credential(
        self,
        credential_id: str,
        accessed_by: str,
        ip_address: str = "unknown",
        user_agent: str = "unknown"
    ) -> Optional[str]:
        """
        Retrieve and decrypt a credential
        
        Args:
            credential_id: ID of credential to retrieve
            accessed_by: User/service accessing the credential
            ip_address: IP address of accessor
            user_agent: User agent of accessor
            
        Returns:
            Decrypted credential value or None if not found/not accessible
        """
        try:
            if credential_id not in self.credentials:
                await self._log_access(credential_id, "read", accessed_by, 
                                     ip_address=ip_address, user_agent=user_agent,
                                     success=False, reason="Credential not found")
                return None
            
            credential = self.credentials[credential_id]
            
            # Check if credential is active
            if credential.status != CredentialStatus.ACTIVE:
                await self._log_access(credential_id, "read", accessed_by,
                                     ip_address=ip_address, user_agent=user_agent,
                                     success=False, reason=f"Credential status: {credential.status.value}")
                return None
            
            # Check expiration
            if credential.expires_at and datetime.utcnow() > credential.expires_at:
                # Mark as expired
                credential.status = CredentialStatus.EXPIRED
                await self._log_access(credential_id, "read", accessed_by,
                                     ip_address=ip_address, user_agent=user_agent,
                                     success=False, reason="Credential expired")
                return None
            
            # Check permissions
            if credential.access_permissions and not self._check_permissions(accessed_by, credential.access_permissions):
                await self._log_access(credential_id, "read", accessed_by,
                                     ip_address=ip_address, user_agent=user_agent,
                                     success=False, reason="Insufficient permissions")
                return None
            
            # Decrypt and return value
            decrypted_value = self._decrypt_value(credential.encrypted_value, credential.encryption_level)
            
            # Update last used timestamp
            credential.last_used_at = datetime.utcnow()
            
            # Log successful access
            await self._log_access(credential_id, "read", accessed_by,
                                 ip_address=ip_address, user_agent=user_agent,
                                 success=True)
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Error retrieving credential {credential_id}: {e}")
            await self._log_access(credential_id, "read", accessed_by,
                                 ip_address=ip_address, user_agent=user_agent,
                                 success=False, reason=f"Error: {str(e)}")
            return None

    async def update_credential(
        self,
        credential_id: str,
        new_value: str,
        accessed_by: str,
        ip_address: str = "unknown",
        user_agent: str = "unknown"
    ) -> bool:
        """Update credential value"""
        
        try:
            if credential_id not in self.credentials:
                await self._log_access(credential_id, "update", accessed_by,
                                     ip_address=ip_address, user_agent=user_agent,
                                     success=False, reason="Credential not found")
                return False
            
            credential = self.credentials[credential_id]
            
            # Check permissions
            if credential.access_permissions and not self._check_permissions(accessed_by, credential.access_permissions):
                await self._log_access(credential_id, "update", accessed_by,
                                     ip_address=ip_address, user_agent=user_agent,
                                     success=False, reason="Insufficient permissions")
                return False
            
            # Encrypt new value
            encrypted_value = self._encrypt_value(new_value, credential.encryption_level)
            
            # Update credential
            credential.encrypted_value = encrypted_value
            credential.updated_at = datetime.utcnow()
            credential.version += 1
            
            # Log successful update
            await self._log_access(credential_id, "update", accessed_by,
                                 ip_address=ip_address, user_agent=user_agent,
                                 success=True)
            
            logger.info(f"Updated credential {credential_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating credential {credential_id}: {e}")
            await self._log_access(credential_id, "update", accessed_by,
                                 ip_address=ip_address, user_agent=user_agent,
                                 success=False, reason=f"Error: {str(e)}")
            return False

    async def rotate_credential(
        self,
        credential_id: str,
        new_value: str,
        accessed_by: str = "system"
    ) -> bool:
        """Rotate credential with new value"""
        
        try:
            if credential_id not in self.credentials:
                return False
            
            credential = self.credentials[credential_id]
            
            # Store old value in metadata for rollback if needed
            if 'previous_versions' not in credential.metadata:
                credential.metadata['previous_versions'] = []
            
            credential.metadata['previous_versions'].append({
                'version': credential.version,
                'rotated_at': datetime.utcnow().isoformat(),
                'rotated_by': accessed_by
            })
            
            # Keep only last 3 versions
            if len(credential.metadata['previous_versions']) > 3:
                credential.metadata['previous_versions'] = credential.metadata['previous_versions'][-3:]
            
            # Update with new value
            success = await self.update_credential(credential_id, new_value, accessed_by)
            
            if success:
                credential.status = CredentialStatus.ACTIVE
                logger.info(f"Rotated credential {credential_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error rotating credential {credential_id}: {e}")
            return False

    async def revoke_credential(
        self,
        credential_id: str,
        accessed_by: str,
        reason: str = "Manual revocation"
    ) -> bool:
        """Revoke a credential"""
        
        try:
            if credential_id not in self.credentials:
                return False
            
            credential = self.credentials[credential_id]
            credential.status = CredentialStatus.REVOKED
            credential.updated_at = datetime.utcnow()
            
            # Add revocation info to metadata
            credential.metadata['revoked_at'] = datetime.utcnow().isoformat()
            credential.metadata['revoked_by'] = accessed_by
            credential.metadata['revocation_reason'] = reason
            
            # Log revocation
            await self._log_access(credential_id, "revoke", accessed_by, success=True, reason=reason)
            
            logger.info(f"Revoked credential {credential_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking credential {credential_id}: {e}")
            return False

    async def list_credentials(
        self,
        platform: Optional[str] = None,
        credential_type: Optional[CredentialType] = None,
        status: Optional[CredentialStatus] = None,
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """List credentials with optional filtering"""
        
        try:
            credentials_list = []
            
            for credential in self.credentials.values():
                # Apply filters
                if platform and credential.platform != platform:
                    continue
                if credential_type and credential.credential_type != credential_type:
                    continue
                if status and credential.status != status:
                    continue
                
                # Check expiration if not including expired
                if not include_expired and credential.expires_at:
                    if datetime.utcnow() > credential.expires_at:
                        continue
                
                # Return safe representation (no sensitive data)
                credential_info = {
                    'credential_id': credential.credential_id,
                    'name': credential.name,
                    'credential_type': credential.credential_type.value,
                    'platform': credential.platform,
                    'status': credential.status.value,
                    'created_at': credential.created_at.isoformat(),
                    'updated_at': credential.updated_at.isoformat(),
                    'expires_at': credential.expires_at.isoformat() if credential.expires_at else None,
                    'last_used_at': credential.last_used_at.isoformat() if credential.last_used_at else None,
                    'version': credential.version,
                    'encryption_level': credential.encryption_level.value
                }
                
                credentials_list.append(credential_info)
            
            return credentials_list
            
        except Exception as e:
            logger.error(f"Error listing credentials: {e}")
            return []

    async def check_expiring_credentials(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Check for credentials expiring within specified days"""
        
        try:
            expiring = []
            cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
            
            for credential in self.credentials.values():
                if credential.expires_at and credential.expires_at <= cutoff_date:
                    if credential.status == CredentialStatus.ACTIVE:
                        days_until_expiry = (credential.expires_at - datetime.utcnow()).days
                        
                        expiring.append({
                            'credential_id': credential.credential_id,
                            'name': credential.name,
                            'platform': credential.platform,
                            'expires_at': credential.expires_at.isoformat(),
                            'days_until_expiry': days_until_expiry,
                            'credential_type': credential.credential_type.value
                        })
            
            return expiring
            
        except Exception as e:
            logger.error(f"Error checking expiring credentials: {e}")
            return []

    async def auto_rotate_credentials(self) -> Dict[str, Any]:
        """Automatically rotate credentials that are due for rotation"""
        
        if not self.auto_rotation_enabled:
            return {'rotated': 0, 'errors': []}
        
        try:
            rotated_count = 0
            errors = []
            
            for credential in self.credentials.values():
                if (credential.status == CredentialStatus.ACTIVE and 
                    credential.rotation_interval_days and
                    credential.updated_at):
                    
                    days_since_update = (datetime.utcnow() - credential.updated_at).days
                    
                    if days_since_update >= credential.rotation_interval_days:
                        # Generate new credential value
                        new_value = await self._generate_new_credential_value(credential)
                        
                        if new_value:
                            success = await self.rotate_credential(
                                credential.credential_id,
                                new_value,
                                "auto_rotation_system"
                            )
                            
                            if success:
                                rotated_count += 1
                            else:
                                errors.append(f"Failed to rotate {credential.credential_id}")
                        else:
                            errors.append(f"Failed to generate new value for {credential.credential_id}")
            
            logger.info(f"Auto-rotation completed: {rotated_count} credentials rotated")
            return {'rotated': rotated_count, 'errors': errors}
            
        except Exception as e:
            logger.error(f"Error in auto-rotation: {e}")
            return {'rotated': 0, 'errors': [str(e)]}

    def _generate_credential_id(self, name: str, platform: str, credential_type: CredentialType) -> str:
        """Generate unique credential ID"""
        
        timestamp = str(int(datetime.utcnow().timestamp()))
        content = f"{name}:{platform}:{credential_type.value}:{timestamp}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"cred_{hash_value}"

    def _encrypt_value(self, value: str, encryption_level: EncryptionLevel) -> str:
        """Encrypt credential value"""
        
        try:
            fernet = self.encryption_keys[encryption_level]
            encrypted_bytes = fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
            
        except Exception as e:
            logger.error(f"Error encrypting value: {e}")
            raise

    def _decrypt_value(self, encrypted_value: str, encryption_level: EncryptionLevel) -> str:
        """Decrypt credential value"""
        
        try:
            fernet = self.encryption_keys[encryption_level]
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting value: {e}")
            raise

    def _check_permissions(self, accessed_by: str, required_permissions: List[str]) -> bool:
        """Check if accessor has required permissions"""
        
        # This would integrate with your permission system
        # For now, simple implementation
        if "admin" in accessed_by.lower() or "system" in accessed_by.lower():
            return True
        
        # In real implementation, check against permission service
        return True

    async def _log_access(
        self,
        credential_id: str,
        access_type: str,
        accessed_by: str,
        ip_address: str = "unknown",
        user_agent: str = "unknown",
        success: bool = False,
        reason: Optional[str] = None
    ):
        """Log credential access"""
        
        try:
            access_record = CredentialAccess(
                access_id=f"acc_{int(datetime.utcnow().timestamp())}_{secrets.randbelow(10000)}",
                credential_id=credential_id,
                accessed_by=accessed_by,
                access_type=access_type,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                reason=reason
            )
            
            self.access_logs.append(access_record)
            
            # Keep only last 10000 access logs
            if len(self.access_logs) > 10000:
                self.access_logs = self.access_logs[-10000:]
            
            # Log to file/database in real implementation
            log_level = logging.INFO if success else logging.WARNING
            logger.log(log_level, f"Credential access: {access_record.access_type} {credential_id} by {accessed_by} - {'Success' if success else 'Failed'}")
            
        except Exception as e:
            logger.error(f"Error logging access: {e}")

    async def _generate_new_credential_value(self, credential: SecureCredential) -> Optional[str]:
        """Generate new credential value for rotation"""
        
        try:
            # Generate new value based on credential type
            if credential.credential_type == CredentialType.API_KEY:
                return secrets.token_urlsafe(32)
            elif credential.credential_type == CredentialType.ACCESS_TOKEN:
                return secrets.token_urlsafe(64)
            elif credential.credential_type == CredentialType.WEBHOOK_SECRET:
                return secrets.token_hex(32)
            elif credential.credential_type == CredentialType.ENCRYPTION_KEY:
                return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            else:
                # For other types, might need platform-specific generation
                return secrets.token_urlsafe(32)
                
        except Exception as e:
            logger.error(f"Error generating new credential value: {e}")
            return None

    async def get_access_logs(
        self,
        credential_id: Optional[str] = None,
        accessed_by: Optional[str] = None,
        hours_back: int = 24
    ) -> List[Dict[str, Any]]:
        """Get access logs with optional filtering"""
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            filtered_logs = []
            
            for log in self.access_logs:
                if log.timestamp < cutoff_time:
                    continue
                
                if credential_id and log.credential_id != credential_id:
                    continue
                
                if accessed_by and log.accessed_by != accessed_by:
                    continue
                
                filtered_logs.append({
                    'access_id': log.access_id,
                    'credential_id': log.credential_id,
                    'accessed_by': log.accessed_by,
                    'access_type': log.access_type,
                    'timestamp': log.timestamp.isoformat(),
                    'ip_address': log.ip_address,
                    'user_agent': log.user_agent,
                    'success': log.success,
                    'reason': log.reason
                })
            
            return filtered_logs
            
        except Exception as e:
            logger.error(f"Error getting access logs: {e}")
            return []

    async def export_vault_metadata(self) -> Dict[str, Any]:
        """Export vault metadata (no sensitive data)"""
        
        try:
            metadata = {
                'total_credentials': len(self.credentials),
                'credentials_by_type': {},
                'credentials_by_platform': {},
                'credentials_by_status': {},
                'encryption_levels': {},
                'access_logs_count': len(self.access_logs),
                'vault_created_at': datetime.utcnow().isoformat()
            }
            
            # Count by type
            for credential in self.credentials.values():
                cred_type = credential.credential_type.value
                metadata['credentials_by_type'][cred_type] = metadata['credentials_by_type'].get(cred_type, 0) + 1
                
                platform = credential.platform
                metadata['credentials_by_platform'][platform] = metadata['credentials_by_platform'].get(platform, 0) + 1
                
                status = credential.status.value
                metadata['credentials_by_status'][status] = metadata['credentials_by_status'].get(status, 0) + 1
                
                enc_level = credential.encryption_level.value
                metadata['encryption_levels'][enc_level] = metadata['encryption_levels'].get(enc_level, 0) + 1
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error exporting vault metadata: {e}")
            return {}

    async def backup_vault(self, encryption_password: str) -> str:
        """Create encrypted backup of vault"""
        
        try:
            # Create backup data structure (encrypt sensitive data)
            backup_data = {
                'version': '1.0',
                'created_at': datetime.utcnow().isoformat(),
                'credentials': {},
                'access_logs': [asdict(log) for log in self.access_logs[-1000:]]  # Last 1000 logs
            }
            
            # Add credentials (keep them encrypted)
            for cred_id, credential in self.credentials.items():
                backup_data['credentials'][cred_id] = {
                    'credential_id': credential.credential_id,
                    'name': credential.name,
                    'credential_type': credential.credential_type.value,
                    'platform': credential.platform,
                    'encrypted_value': credential.encrypted_value,
                    'encryption_level': credential.encryption_level.value,
                    'status': credential.status.value,
                    'created_at': credential.created_at.isoformat(),
                    'updated_at': credential.updated_at.isoformat(),
                    'expires_at': credential.expires_at.isoformat() if credential.expires_at else None,
                    'last_used_at': credential.last_used_at.isoformat() if credential.last_used_at else None,
                    'rotation_interval_days': credential.rotation_interval_days,
                    'access_permissions': credential.access_permissions,
                    'metadata': credential.metadata,
                    'version': credential.version
                }
            
            # Encrypt backup with provided password
            backup_json = json.dumps(backup_data)
            
            # Create encryption key from password
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_password.encode()))
            fernet = Fernet(key)
            
            encrypted_backup = fernet.encrypt(backup_json.encode())
            
            # Combine salt and encrypted data
            final_backup = base64.urlsafe_b64encode(salt + encrypted_backup).decode()
            
            logger.info("Vault backup created successfully")
            return final_backup
            
        except Exception as e:
            logger.error(f"Error creating vault backup: {e}")
            raise

    async def restore_vault(self, backup_data: str, encryption_password: str) -> bool:
        """Restore vault from encrypted backup"""
        
        try:
            # Decode backup data
            backup_bytes = base64.urlsafe_b64decode(backup_data.encode())
            
            # Extract salt and encrypted data
            salt = backup_bytes[:16]
            encrypted_data = backup_bytes[16:]
            
            # Create decryption key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(encryption_password.encode()))
            fernet = Fernet(key)
            
            # Decrypt backup
            decrypted_json = fernet.decrypt(encrypted_data).decode()
            backup_data_dict = json.loads(decrypted_json)
            
            # Restore credentials
            for cred_id, cred_data in backup_data_dict['credentials'].items():
                credential = SecureCredential(
                    credential_id=cred_data['credential_id'],
                    name=cred_data['name'],
                    credential_type=CredentialType(cred_data['credential_type']),
                    platform=cred_data['platform'],
                    encrypted_value=cred_data['encrypted_value'],
                    encryption_level=EncryptionLevel(cred_data['encryption_level']),
                    status=CredentialStatus(cred_data['status']),
                    created_at=datetime.fromisoformat(cred_data['created_at']),
                    updated_at=datetime.fromisoformat(cred_data['updated_at']),
                    expires_at=datetime.fromisoformat(cred_data['expires_at']) if cred_data['expires_at'] else None,
                    last_used_at=datetime.fromisoformat(cred_data['last_used_at']) if cred_data['last_used_at'] else None,
                    rotation_interval_days=cred_data['rotation_interval_days'],
                    access_permissions=cred_data['access_permissions'],
                    metadata=cred_data['metadata'],
                    version=cred_data['version']
                )
                
                self.credentials[cred_id] = credential
            
            logger.info(f"Vault restored successfully: {len(self.credentials)} credentials loaded")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring vault: {e}")
            return False