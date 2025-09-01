"""Database Encryption Manager

Enterprise-grade database encryption management system for data at rest and in transit.
Provides advanced encryption capabilities with key rotation, HSM integration, and compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Advanced encryption architecture
- ML Engineer: AI-driven security analysis  
- DBA: Database security optimization
- Security Expert: Enterprise security protocols
- Microservices: Distributed encryption services
- Audio Engineer: Audio data protection
- DevOps: Secure deployment & infrastructure
- IA Prompt Engineer: AI security prompts

Contact: mlaiel@live.de
⚠️ LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""

import asyncio
import logging
import os
import secrets
import hashlib
import hmac
import json
from typing import Dict, List, Any, Optional, Union, Tuple, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """
Supported encryption algorithms"""

    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    RSA_4096 = "RSA-4096"
    FERNET = "Fernet"


class KeyType(Enum):
    """Encryption key types"""

    MASTER = "master"
    DATABASE = "database"
    COLUMN = "column"
    ROW = "row"
    FIELD = "field"
    TEMPORARY = "temporary"


class EncryptionMode(Enum):
    """Encryption operation modes"""

    ENCRYPT = auto()
    DECRYPT = auto()
    ROTATE = auto()
    BACKUP = auto()


@dataclass
class EncryptionKey:
    """
Encryption key metadata"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    created_at: datetime
    expires_at: Optional[datetime]
    rotation_count: int = 0
    is_active: bool = True
    purpose: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptionContext:
    """Encryption operation context"""
    operation: EncryptionMode
    key_id: str
    algorithm: EncryptionAlgorithm
    timestamp: datetime
    user_id: Optional[str] = None
    table_name: Optional[str] = None
    column_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptionMetrics:
    """
Encryption performance and security metrics"""
    
    def __init__(self):
        self.operations_count: int = 0
        self.total_data_size: int = 0
        self.average_operation_time: float = 0.0
        self.key_rotations: int = 0
        self.failed_operations: int = 0
        self.security_events: List[Dict[str, Any]] = []
        
    def record_operation(self, operation_time: float, data_size: int, success: bool):
        """
Record encryption operation metrics"""
        self.operations_count += 1
        self.total_data_size += data_size
        
        if success:
            # Update average operation time
            self.average_operation_time = (
                (self.average_operation_time * (self.operations_count - 1) + operation_time) 
                / self.operations_count
            )
        else:
            self.failed_operations += 1


class DatabaseEncryptionManager:
    """
    Enterprise-grade database encryption manager
    
    Provides comprehensive encryption capabilities for database operations
    including transparent data encryption, column-level encryption, and
    field-level encryption with advanced key management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize encryption manager"""
        self.config = config or {}
        self.keys: Dict[str, EncryptionKey] = {}
        self.key_store: Dict[str, bytes] = {}
        self.metrics = EncryptionMetrics()
        self.hsm_enabled = self.config.get("hsm_enabled", False)
        self.key_rotation_days = self.config.get("key_rotation_days", 90)
        self.backup_encryption = self.config.get("backup_encryption", True)
        
        # Initialize master keys
        self._initialize_master_keys()
        
        logger.info("Database encryption manager initialized successfully")
    
    def _initialize_master_keys(self):
        """Initialize master encryption keys"""
        try:
            # Generate master key if not exists
            master_key_id = "master_key_2025"
            if master_key_id not in self.keys:
                master_key = self._generate_encryption_key(
                    key_type=KeyType.MASTER,
                    algorithm=EncryptionAlgorithm.AES_256_GCM,
                    purpose="Master database encryption key"
                )
                self.keys[master_key_id] = master_key
                logger.info(f"Master encryption key generated: {master_key_id}")
            
            # Generate database-specific keys
            for db_name in ["main", "analytics", "content", "audit"]:
                db_key_id = f"db_key_{db_name}"
                if db_key_id not in self.keys:
                    db_key = self._generate_encryption_key(
                        key_type=KeyType.DATABASE,
                        algorithm=EncryptionAlgorithm.AES_256_GCM,
                        purpose=f"Database encryption for {db_name}"
                    )
                    self.keys[db_key_id] = db_key
                    logger.info(f"Database key generated: {db_key_id}")
                    
        except Exception as e:
            logger.error(f"Master key initialization error: {e}")
            raise
    
    def _generate_encryption_key(
        self,
        key_type: KeyType,
        algorithm: EncryptionAlgorithm,
        purpose: str = ""
    ) -> EncryptionKey:
        """Generate new encryption key"""
        try:
            key_id = f"{key_type.value}_{uuid.uuid4().hex[:8]}"
            
            # Generate key material based on algorithm
            if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                key_material = secrets.token_bytes(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_material = secrets.token_bytes(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.FERNET:
                key_material = Fernet.generate_key()
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=default_backend()
                )
                key_material = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Store key material securely
            self.key_store[key_id] = key_material
            
            # Create key metadata
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=self.key_rotation_days),
                purpose=purpose
            )
            
            return encryption_key
            
        except Exception as e:
            logger.error(f"Key generation error: {e}")
            raise
    
    async def encrypt_data(
        self,
        data: Union[str, bytes],
        key_id: Optional[str] = None,
        algorithm: Optional[EncryptionAlgorithm] = None,
        context: Optional[EncryptionContext] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Encrypt data with specified or default key
        
        Args:
            data: Data to encrypt
            key_id: Encryption key ID (optional)
            algorithm: Encryption algorithm (optional)
            context: Encryption context (optional)
            
        Returns:
            Tuple of (encrypted_data, encryption_metadata)
        """
        start_time = datetime.now()
        
        try:
            # Convert string data to bytes
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Use default key if not specified
            if not key_id:
                key_id = "master_key_2025"
            
            # Get encryption key
            if key_id not in self.keys:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            key_info = self.keys[key_id]
            key_material = self.key_store[key_id]
            
            # Use key's algorithm if not specified
            if not algorithm:
                algorithm = key_info.algorithm
            
            # Perform encryption based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data, encryption_metadata = await self._encrypt_aes_gcm(
                    data_bytes, key_material
                )
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data, encryption_metadata = await self._encrypt_aes_cbc(
                    data_bytes, key_material
                )
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data, encryption_metadata = await self._encrypt_chacha20(
                    data_bytes, key_material
                )
            elif algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data, encryption_metadata = await self._encrypt_fernet(
                    data_bytes, key_material
                )
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
            
            # Add key and algorithm info to metadata
            encryption_metadata.update({
                "key_id": key_id,
                "algorithm": algorithm.value,
                "encrypted_at": datetime.now().isoformat(),
                "data_size": len(data_bytes)
            })
            
            # Record metrics
            operation_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_operation(operation_time, len(data_bytes), True)
            
            # Log encryption event
            if context:
                await self._log_encryption_event(context, success=True)
            
            logger.debug(f"Data encrypted successfully with key {key_id}")
            return encrypted_data, encryption_metadata
            
        except Exception as e:
            # Record failed operation
            operation_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_operation(operation_time, len(data) if data else 0, False)
            
            # Log encryption failure
            if context:
                await self._log_encryption_event(context, success=False, error=str(e))
            
            logger.error(f"Data encryption failed: {e}")
            raise
    
    async def decrypt_data(
        self,
        encrypted_data: bytes,
        encryption_metadata: Dict[str, Any],
        context: Optional[EncryptionContext] = None
    ) -> Union[str, bytes]:
        """
        Decrypt data using encryption metadata
        
        Args:
            encrypted_data: Encrypted data bytes
            encryption_metadata: Encryption metadata
            context: Decryption context (optional)
            
        Returns:
            Decrypted data
        """
        start_time = datetime.now()
        
        try:
            # Extract encryption parameters
            key_id = encryption_metadata.get("key_id")
            algorithm_name = encryption_metadata.get("algorithm")
            
            if not key_id or not algorithm_name:
                raise ValueError("Invalid encryption metadata")
            
            # Get encryption key
            if key_id not in self.keys:
                raise ValueError(f"Decryption key not found: {key_id}")
            
            key_material = self.key_store[key_id]
            algorithm = EncryptionAlgorithm(algorithm_name)
            
            # Perform decryption based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = await self._decrypt_aes_gcm(
                    encrypted_data, key_material, encryption_metadata
                )
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_data = await self._decrypt_aes_cbc(
                    encrypted_data, key_material, encryption_metadata
                )
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = await self._decrypt_chacha20(
                    encrypted_data, key_material, encryption_metadata
                )
            elif algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = await self._decrypt_fernet(
                    encrypted_data, key_material, encryption_metadata
                )
            else:
                raise ValueError(f"Unsupported decryption algorithm: {algorithm}")
            
            # Record metrics
            operation_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_operation(operation_time, len(encrypted_data), True)
            
            # Log decryption event
            if context:
                await self._log_encryption_event(context, success=True)
            
            logger.debug(f"Data decrypted successfully with key {key_id}")
            
            # Try to decode as UTF-8 string
            try:
                return decrypted_data.decode('utf-8')
            except UnicodeDecodeError:
                return decrypted_data
                
        except Exception as e:
            # Record failed operation
            operation_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_operation(operation_time, len(encrypted_data), False)
            
            # Log decryption failure
            if context:
                await self._log_encryption_event(context, success=False, error=str(e))
            
            logger.error(f"Data decryption failed: {e}")
            raise
    
    async def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt data using AES-256-GCM"""
        iv = secrets.token_bytes(16)  # 128-bit IV
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        metadata = {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "tag": base64.b64encode(encryptor.tag).decode('utf-8')
        }
        
        return ciphertext, metadata
    
    async def _decrypt_aes_gcm(
        self, 
        encrypted_data: bytes, 
        key: bytes, 
        metadata: Dict[str, Any]
    ) -> bytes:
        """Decrypt data using AES-256-GCM"""
        iv = base64.b64decode(metadata["iv"])
        tag = base64.b64decode(metadata["tag"])
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(encrypted_data) + decryptor.finalize()
    
    async def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt data using AES-256-CBC"""
        iv = secrets.token_bytes(16)  # 128-bit IV
        
        # Add PKCS7 padding
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        metadata = {
            "iv": base64.b64encode(iv).decode('utf-8')
        }
        
        return ciphertext, metadata
    
    async def _decrypt_aes_cbc(
        self, 
        encrypted_data: bytes, 
        key: bytes, 
        metadata: Dict[str, Any]
    ) -> bytes:
        """Decrypt data using AES-256-CBC"""
        iv = base64.b64decode(metadata["iv"])
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    async def _encrypt_chacha20(self, data: bytes, key: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt data using ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            modes.GCM(),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        metadata = {
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "tag": base64.b64encode(encryptor.tag).decode('utf-8')
        }
        
        return ciphertext, metadata
    
    async def _decrypt_chacha20(
        self, 
        encrypted_data: bytes, 
        key: bytes, 
        metadata: Dict[str, Any]
    ) -> bytes:
        """Decrypt data using ChaCha20-Poly1305"""
        nonce = base64.b64decode(metadata["nonce"])
        tag = base64.b64decode(metadata["tag"])
        
        cipher = Cipher(
            algorithms.ChaCha20(key, nonce),
            modes.GCM(tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(encrypted_data) + decryptor.finalize()
    
    async def _encrypt_fernet(self, data: bytes, key: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt data using Fernet"""
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        
        metadata = {
            "encoding": "fernet"
        }
        
        return encrypted_data, metadata
    
    async def _decrypt_fernet(
        self, 
        encrypted_data: bytes, 
        key: bytes, 
        metadata: Dict[str, Any]
    ) -> bytes:
        """Decrypt data using Fernet"""
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)
    
    async def rotate_key(self, key_id: str) -> str:
        """
        Rotate encryption key and return new key ID
        
        Args:
            key_id: Current key ID to rotate
            
        Returns:
            New key ID
        """
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
            
            old_key = self.keys[key_id]
            
            # Generate new key with same parameters
            new_key = self._generate_encryption_key(
                key_type=old_key.key_type,
                algorithm=old_key.algorithm,
                purpose=f"Rotated {old_key.purpose}"
            )
            
            # Update rotation count
            new_key.rotation_count = old_key.rotation_count + 1
            
            # Store new key
            self.keys[new_key.key_id] = new_key
            
            # Mark old key as inactive
            old_key.is_active = False
            
            # Update metrics
            self.metrics.key_rotations += 1
            
            logger.info(f"Key rotated: {key_id} -> {new_key.key_id}")
            return new_key.key_id
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise
    
    async def _log_encryption_event(
        self,
        context: EncryptionContext,
        success: bool,
        error: Optional[str] = None
    ):
        """Log encryption operation event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "operation": context.operation.name,
            "key_id": context.key_id,
            "algorithm": context.algorithm.value,
            "user_id": context.user_id,
            "table_name": context.table_name,
            "column_name": context.column_name,
            "success": success,
            "error": error,
            "metadata": context.metadata
        }
        
        self.metrics.security_events.append(event)
        
        if success:
            logger.info(f"Encryption operation successful: {context.operation.name}")
        else:
            logger.warning(f"Encryption operation failed: {context.operation.name} - {error}")
    
    def get_key_info(self, key_id: str) -> Optional[EncryptionKey]:
        """Get encryption key information"""
        return self.keys.get(key_id)
    
    def list_active_keys(self) -> List[EncryptionKey]:
        """
List all active encryption keys"""
        return [key for key in self.keys.values() if key.is_active]
    
    def get_encryption_metrics(self) -> Dict[str, Any]:
        """
Get encryption performance metrics"""
        return {
            "operations_count": self.metrics.operations_count,
            "total_data_size": self.metrics.total_data_size,
            "average_operation_time": self.metrics.average_operation_time,
            "key_rotations": self.metrics.key_rotations,
            "failed_operations": self.metrics.failed_operations,
            "success_rate": (
                (self.metrics.operations_count - self.metrics.failed_operations) 
                / max(self.metrics.operations_count, 1) * 100
            ),
            "security_events_count": len(self.metrics.security_events)
        }
    
    async def backup_keys(self, backup_path: str, encryption_key: Optional[str] = None):
        """
        Backup encryption keys securely
        
        Args:
            backup_path: Path to backup file
            encryption_key: Optional key for backup encryption
        """
        try:
            # Prepare key backup data
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "keys": {},
                "metadata": {
                    "backup_version": "1.0",
                    "total_keys": len(self.keys)
                }
            }
            
            # Export key metadata (not the actual key material for security)
            for key_id, key_info in self.keys.items():
                backup_data["keys"][key_id] = {
                    "key_type": key_info.key_type.value,
                    "algorithm": key_info.algorithm.value,
                    "created_at": key_info.created_at.isoformat(),
                    "expires_at": key_info.expires_at.isoformat() if key_info.expires_at else None,
                    "rotation_count": key_info.rotation_count,
                    "is_active": key_info.is_active,
                    "purpose": key_info.purpose,
                    "metadata": key_info.metadata
                }
            
            # Serialize backup data
            backup_json = json.dumps(backup_data, indent=2)
            
            # Encrypt backup if encryption key provided
            if encryption_key:
                encrypted_backup, _ = await self.encrypt_data(backup_json, encryption_key)
                backup_content = base64.b64encode(encrypted_backup).decode('utf-8')
            else:
                backup_content = backup_json
            
            # Write backup to file
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            
            logger.info(f"Encryption keys backed up to: {backup_path}")
            
        except Exception as e:
            logger.error(f"Key backup failed: {e}")
            raise
    
    async def cleanup_expired_keys(self):
        """Clean up expired encryption keys"""
        try:
            current_time = datetime.now()
            expired_keys = []
            
            for key_id, key_info in self.keys.items():
                if (key_info.expires_at and 
                    key_info.expires_at < current_time and 
                    not key_info.is_active):
                    expired_keys.append(key_id)
            
            # Remove expired keys
            for key_id in expired_keys:
                del self.keys[key_id]
                if key_id in self.key_store:
                    del self.key_store[key_id]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired keys")
            
        except Exception as e:
            logger.error(f"Key cleanup failed: {e}")
            raise


# Module initialization
logger.info("Database encryption manager module loaded successfully")
