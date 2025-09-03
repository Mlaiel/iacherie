"""Secure Storage Service - Stockage sécurisé

Enterprise-grade secure storage service for encrypted data persistence.
Provides secure storage backend for encrypted data and keys.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import json
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from .data_encryption import EncryptedData, EncryptionKey

logger = logging.getLogger(__name__)


class StorageBackend(Enum):
    """Supported storage backends"""
    FILE_SYSTEM = "filesystem"
    DATABASE = "database"
    CLOUD_KMS = "cloud_kms"
    HSM = "hsm"


class StorageSecurityLevel(Enum):
    """Security levels for storage"""
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StorageRecord:
    """Secure storage record"""
    record_id: str
    data_type: str
    encrypted_data: bytes
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    access_count: int = 0
    security_level: StorageSecurityLevel = StorageSecurityLevel.STANDARD


@dataclass 
class StorageConfig:
    """Storage configuration"""
    backend: StorageBackend
    encryption_enabled: bool = True
    compression_enabled: bool = False
    backup_enabled: bool = True
    integrity_check: bool = True
    storage_path: str = "./secure_storage"
    max_record_size: int = 100 * 1024 * 1024  # 100MB


class SecureStorageService:
    """
    Enterprise secure storage service providing encrypted data persistence.
    Integrates with key management for secure data storage and retrieval.
    """
    
    def __init__(self, config: Optional[StorageConfig] = None, master_key: Optional[str] = None):
        self.logger = logger
        self.config = config or StorageConfig(backend=StorageBackend.FILE_SYSTEM)
        self.master_key = master_key or self._generate_master_key()
        self.storage_records: Dict[str, StorageRecord] = {}
        
        # Initialize storage backend
        self._initialize_storage_backend()
        
    def _generate_master_key(self) -> str:
        """Generate master key for storage encryption"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    
    def _initialize_storage_backend(self):
        """Initialize the configured storage backend"""
        if self.config.backend == StorageBackend.FILE_SYSTEM:
            os.makedirs(self.config.storage_path, exist_ok=True)
            
        self.logger.info(f"Initialized {self.config.backend.value} storage backend")
    
    async def store_encrypted_data(
        self,
        record_id: str,
        encrypted_data: EncryptedData,
        security_level: StorageSecurityLevel = StorageSecurityLevel.STANDARD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store encrypted data securely
        
        Args:
            record_id: Unique identifier for the record
            encrypted_data: EncryptedData object to store
            security_level: Security level for storage
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Validate input
            if len(encrypted_data.data) > self.config.max_record_size:
                raise ValueError("Data exceeds maximum record size")
            
            # Prepare storage data
            storage_data = {
                'data': base64.b64encode(encrypted_data.data).decode(),
                'algorithm': encrypted_data.algorithm.value,
                'key_id': encrypted_data.key_id,
                'iv': base64.b64encode(encrypted_data.iv).decode() if encrypted_data.iv else None,
                'tag': base64.b64encode(encrypted_data.tag).decode() if encrypted_data.tag else None,
                'metadata': encrypted_data.metadata
            }
            
            # Additional encryption for storage if required
            if self.config.encryption_enabled and security_level in [StorageSecurityLevel.HIGH, StorageSecurityLevel.CRITICAL]:
                storage_data = await self._encrypt_for_storage(storage_data)
            
            # Create storage record
            record = StorageRecord(
                record_id=record_id,
                data_type="encrypted_data",
                encrypted_data=json.dumps(storage_data).encode(),
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                security_level=security_level
            )
            
            # Store based on backend
            success = await self._store_record(record)
            
            if success:
                self.storage_records[record_id] = record
                self.logger.info(f"Stored encrypted data: {record_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to store encrypted data: {str(e)}")
            return False
    
    async def retrieve_encrypted_data(self, record_id: str) -> Optional[EncryptedData]:
        """
        Retrieve encrypted data by record ID
        
        Args:
            record_id: Unique identifier for the record
            
        Returns:
            EncryptedData object or None if not found
        """
        try:
            # Retrieve record
            record = await self._retrieve_record(record_id)
            if not record:
                return None
            
            # Parse storage data
            storage_data = json.loads(record.encrypted_data.decode())
            
            # Decrypt storage data if needed
            if self.config.encryption_enabled and record.security_level in [StorageSecurityLevel.HIGH, StorageSecurityLevel.CRITICAL]:
                storage_data = await self._decrypt_from_storage(storage_data)
            
            # Reconstruct EncryptedData
            from .data_encryption import EncryptionAlgorithm
            
            encrypted_data = EncryptedData(
                data=base64.b64decode(storage_data['data']),
                algorithm=EncryptionAlgorithm(storage_data['algorithm']),
                key_id=storage_data['key_id'],
                iv=base64.b64decode(storage_data['iv']) if storage_data['iv'] else None,
                tag=base64.b64decode(storage_data['tag']) if storage_data['tag'] else None,
                metadata=storage_data['metadata']
            )
            
            # Update access tracking
            record.access_count += 1
            record.updated_at = datetime.now()
            await self._update_record(record)
            
            self.logger.info(f"Retrieved encrypted data: {record_id}")
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve encrypted data: {str(e)}")
            return None
    
    async def store_encryption_key(
        self,
        key: EncryptionKey,
        security_level: StorageSecurityLevel = StorageSecurityLevel.HIGH
    ) -> bool:
        """
        Store encryption key securely
        
        Args:
            key: EncryptionKey to store
            security_level: Security level for key storage
            
        Returns:
            Success status
        """
        try:
            # Serialize key
            key_data = {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active,
                'metadata': key.metadata
            }
            
            # Always encrypt keys for storage
            encrypted_key_data = await self._encrypt_for_storage(key_data)
            
            # Create storage record
            record = StorageRecord(
                record_id=key.key_id,
                data_type="encryption_key",
                encrypted_data=json.dumps(encrypted_key_data).encode(),
                metadata={'key_type': key.key_type.value, 'algorithm': key.algorithm.value},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                security_level=security_level
            )
            
            success = await self._store_record(record)
            
            if success:
                self.storage_records[key.key_id] = record
                self.logger.info(f"Stored encryption key: {key.key_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to store encryption key: {str(e)}")
            return False
    
    async def retrieve_encryption_key(self, key_id: str) -> Optional[EncryptionKey]:
        """
        Retrieve encryption key by ID
        
        Args:
            key_id: Key identifier
            
        Returns:
            EncryptionKey object or None if not found
        """
        try:
            record = await self._retrieve_record(key_id)
            if not record or record.data_type != "encryption_key":
                return None
            
            # Decrypt and parse key data
            encrypted_key_data = json.loads(record.encrypted_data.decode())
            key_data = await self._decrypt_from_storage(encrypted_key_data)
            
            # Reconstruct EncryptionKey
            from .data_encryption import KeyType, EncryptionAlgorithm
            
            key = EncryptionKey(
                key_id=key_data['key_id'],
                key_type=KeyType(key_data['key_type']),
                algorithm=EncryptionAlgorithm(key_data['algorithm']),
                created_at=datetime.fromisoformat(key_data['created_at']),
                expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data['expires_at'] else None,
                is_active=key_data['is_active'],
                metadata=key_data['metadata']
            )
            
            # Update access tracking
            record.access_count += 1
            record.updated_at = datetime.now()
            await self._update_record(record)
            
            return key
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve encryption key: {str(e)}")
            return None
    
    async def delete_record(self, record_id: str) -> bool:
        """Delete a storage record securely"""
        try:
            # Retrieve record first
            record = await self._retrieve_record(record_id)
            if not record:
                return False
            
            # Securely overwrite data
            record.encrypted_data = b'DELETED' * (len(record.encrypted_data) // 7 + 1)[:len(record.encrypted_data)]
            
            # Remove from backend storage
            success = await self._delete_record(record_id)
            
            if success and record_id in self.storage_records:
                del self.storage_records[record_id]
                self.logger.info(f"Deleted storage record: {record_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete record: {str(e)}")
            return False
    
    async def _encrypt_for_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt data for storage using master key"""
        try:
            # Convert to JSON
            json_data = json.dumps(data).encode()
            
            # Derive storage key from master key
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            storage_key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
            
            # Encrypt data
            fernet = Fernet(storage_key)
            encrypted_data = fernet.encrypt(json_data)
            
            return {
                'encrypted': base64.b64encode(encrypted_data).decode(),
                'salt': base64.b64encode(salt).decode(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Storage encryption failed: {str(e)}")
            raise
    
    async def _decrypt_from_storage(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt data from storage using master key"""
        try:
            # Restore storage key
            salt = base64.b64decode(encrypted_data['salt'])
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            storage_key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
            
            # Decrypt data
            fernet = Fernet(storage_key)
            decrypted_data = fernet.decrypt(base64.b64decode(encrypted_data['encrypted']))
            
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            self.logger.error(f"Storage decryption failed: {str(e)}")
            raise
    
    async def _store_record(self, record: StorageRecord) -> bool:
        """Store record based on configured backend"""
        if self.config.backend == StorageBackend.FILE_SYSTEM:
            return await self._store_record_filesystem(record)
        else:
            # Implement other backends as needed
            self.logger.warning(f"Backend {self.config.backend.value} not implemented")
            return False
    
    async def _retrieve_record(self, record_id: str) -> Optional[StorageRecord]:
        """Retrieve record based on configured backend"""
        if self.config.backend == StorageBackend.FILE_SYSTEM:
            return await self._retrieve_record_filesystem(record_id)
        else:
            self.logger.warning(f"Backend {self.config.backend.value} not implemented")
            return None
    
    async def _update_record(self, record: StorageRecord) -> bool:
        """Update record based on configured backend"""
        if self.config.backend == StorageBackend.FILE_SYSTEM:
            return await self._store_record_filesystem(record)  # Overwrite for filesystem
        else:
            return False
    
    async def _delete_record(self, record_id: str) -> bool:
        """Delete record based on configured backend"""
        if self.config.backend == StorageBackend.FILE_SYSTEM:
            return await self._delete_record_filesystem(record_id)
        else:
            return False
    
    async def _store_record_filesystem(self, record: StorageRecord) -> bool:
        """Store record to filesystem"""
        try:
            # Create record data
            record_data = {
                'record_id': record.record_id,
                'data_type': record.data_type,
                'encrypted_data': base64.b64encode(record.encrypted_data).decode(),
                'metadata': record.metadata,
                'created_at': record.created_at.isoformat(),
                'updated_at': record.updated_at.isoformat(),
                'access_count': record.access_count,
                'security_level': record.security_level.value
            }
            
            # Write to file
            file_path = os.path.join(self.config.storage_path, f"{record.record_id}.json")
            with open(file_path, 'w') as f:
                json.dump(record_data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(file_path, 0o600)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Filesystem storage failed: {str(e)}")
            return False
    
    async def _retrieve_record_filesystem(self, record_id: str) -> Optional[StorageRecord]:
        """Retrieve record from filesystem"""
        try:
            file_path = os.path.join(self.config.storage_path, f"{record_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                record_data = json.load(f)
            
            return StorageRecord(
                record_id=record_data['record_id'],
                data_type=record_data['data_type'],
                encrypted_data=base64.b64decode(record_data['encrypted_data']),
                metadata=record_data['metadata'],
                created_at=datetime.fromisoformat(record_data['created_at']),
                updated_at=datetime.fromisoformat(record_data['updated_at']),
                access_count=record_data['access_count'],
                security_level=StorageSecurityLevel(record_data['security_level'])
            )
            
        except Exception as e:
            self.logger.error(f"Filesystem retrieval failed: {str(e)}")
            return None
    
    async def _delete_record_filesystem(self, record_id: str) -> bool:
        """Delete record from filesystem"""
        try:
            file_path = os.path.join(self.config.storage_path, f"{record_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Filesystem deletion failed: {str(e)}")
            return False
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage service statistics"""
        return {
            'backend': self.config.backend.value,
            'total_records': len(self.storage_records),
            'encryption_enabled': self.config.encryption_enabled,
            'storage_path': self.config.storage_path,
            'record_types': list(set(record.data_type for record in self.storage_records.values())),
            'security_levels': list(set(record.security_level.value for record in self.storage_records.values())),
            'last_updated': datetime.now().isoformat()
        }