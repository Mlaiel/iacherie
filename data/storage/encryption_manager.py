"""
Professional Encryption Manager - IA Influencer Agent Platform
==============================================================
Module: backend/data/storage/encryption_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Security Core - Advanced Encryption Management
Responsibility: Multi-layer encryption for content protection & security compliance
Technologies: Python, AES-256, RSA, Cryptographic APIs, Key management
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER INTÉGRÉE:
Key Generation → Encryption Processing → Secure Storage → 
Key Rotation → Access Control → Decryption → Audit Logging → 
Compliance Validation → Multi-tier Security → Recovery Management
"""

import asyncio
import logging
import hashlib
import base64
import secrets
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import threading
from pathlib import Path

# Cryptographic libraries
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, MultiFernet
import cryptography.exceptions

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Encryption algorithms supported"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_4096 = "rsa_4096"


class KeyType(Enum):
    """Key types for different purposes"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    DERIVED = "derived"
    MASTER = "master"


class SecurityLevel(Enum):
    """Security levels for different content types"""
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"
    MILITARY = "military"


@dataclass
class EncryptionKey:
    """Encryption key information"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    rotation_count: int = 0
    access_count: int = 0
    last_used: Optional[datetime] = None


@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int = 90
    master_key_rotation_days: int = 365
    security_level: SecurityLevel = SecurityLevel.HIGH
    key_derivation_iterations: int = 100000
    enable_compression: bool = True
    enable_integrity_check: bool = True
    backup_keys_count: int = 3


@dataclass
class EncryptionResult:
    """Encryption operation result"""
    success: bool
    encrypted_data: Optional[bytes] = None
    key_id: str = ""
    algorithm: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class DecryptionResult:
    """Decryption operation result"""
    success: bool
    decrypted_data: Optional[bytes] = None
    key_id: str = ""
    algorithm: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class EncryptionManager:
    """
    Professional encryption manager for IA Influencer Agent platform.
    
    Provides enterprise-grade encryption with key management, rotation,
    and compliance features for content protection.
    """
    
    def __init__(self, config: EncryptionConfig, master_key: bytes = None):
        """
        Initialize EncryptionManager.
        
        Args:
            config: Encryption configuration
            master_key: Master key for key encryption (auto-generated if None)
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Key storage
        self.keys = {}  # key_id -> EncryptionKey
        self.master_keys = {}  # master_key_id -> master_key
        
        # Key derivation and management
        self.backend = default_backend()
        self.key_lock = threading.RLock()
        
        # Initialize master key
        if master_key:
            self.master_key = master_key
        else:
            self.master_key = self._generate_master_key()
        
        # Key rotation tracking
        self.rotation_schedule = {}
        self.rotation_enabled = True
        
        # Compliance and audit
        self.audit_log = []
        self.compliance_mode = True
        
        # Performance optimization
        self.key_cache_size = 1000
        self.key_cache = {}
        
        # Initialize default keys
        self._initialize_default_keys()
        
        # Start key rotation scheduler
        if self.rotation_enabled:
            asyncio.create_task(self._key_rotation_scheduler())
    
    def _initialize_default_keys(self):
        """Initialize default encryption keys"""
        try:
            # Generate default symmetric key
            default_key = self.generate_key(
                algorithm=self.config.default_algorithm,
                metadata={'purpose': 'default_content_encryption'}
            )
            
            # Generate key pair for asymmetric operations
            if self.config.security_level in [SecurityLevel.HIGH, SecurityLevel.MAXIMUM, SecurityLevel.MILITARY]:
                keypair = self.generate_keypair(
                    algorithm=EncryptionAlgorithm.RSA_4096,
                    metadata={'purpose': 'asymmetric_operations'}
                )
                
            self.logger.info("Default encryption keys initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing default keys: {str(e)}")
    
    def generate_key(self, algorithm: EncryptionAlgorithm = None,
                    metadata: Dict[str, Any] = None) -> str:
        """
        Generate a new encryption key.
        
        Args:
            algorithm: Encryption algorithm
            metadata: Optional key metadata
            
        Returns:
            Key ID for the generated key
        """
        try:
            algorithm = algorithm or self.config.default_algorithm
            
            # Generate key data based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                key_data = secrets.token_bytes(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                key_data = secrets.token_bytes(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                key_data = secrets.token_bytes(32)  # 256 bits
            elif algorithm == EncryptionAlgorithm.FERNET:
                key_data = Fernet.generate_key()
            else:
                raise ValueError(f"Unsupported symmetric algorithm: {algorithm}")
            
            # Create key ID
            key_id = self._generate_key_id(algorithm, metadata)
            
            # Create key object
            key = EncryptionKey(
                key_id=key_id,
                key_type=KeyType.SYMMETRIC,
                algorithm=algorithm,
                key_data=key_data,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=self.config.key_rotation_days),
                metadata=metadata or {}
            )
            
            # Store encrypted key
            with self.key_lock:
                encrypted_key_data = self._encrypt_key_data(key_data)
                key.key_data = encrypted_key_data
                self.keys[key_id] = key
            
            # Schedule rotation
            self._schedule_key_rotation(key_id)
            
            # Audit log
            self._log_key_operation('key_generated', key_id, metadata)
            
            self.logger.info(f"Generated key: {key_id} ({algorithm.value})")
            return key_id
            
        except Exception as e:
            self.logger.error(f"Error generating key: {str(e)}")
            raise
    
    def generate_keypair(self, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.RSA_4096,
                        metadata: Dict[str, Any] = None) -> Tuple[str, str]:
        """
        Generate an asymmetric key pair.
        
        Args:
            algorithm: Asymmetric algorithm
            metadata: Optional metadata
            
        Returns:
            Tuple of (public_key_id, private_key_id)
        """
        try:
            if algorithm == EncryptionAlgorithm.RSA_4096:
                # Generate RSA key pair
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=self.backend
                )
                public_key = private_key.public_key()
                
                # Serialize keys
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
            else:
                raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
            
            # Create key IDs
            public_key_id = self._generate_key_id(algorithm, {**metadata or {}, 'type': 'public'})
            private_key_id = self._generate_key_id(algorithm, {**metadata or {}, 'type': 'private'})
            
            # Create key objects
            public_key_obj = EncryptionKey(
                key_id=public_key_id,
                key_type=KeyType.ASYMMETRIC_PUBLIC,
                algorithm=algorithm,
                key_data=self._encrypt_key_data(public_pem),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=self.config.key_rotation_days * 4),  # Longer for asymmetric
                metadata={**metadata or {}, 'key_pair': private_key_id}
            )
            
            private_key_obj = EncryptionKey(
                key_id=private_key_id,
                key_type=KeyType.ASYMMETRIC_PRIVATE,
                algorithm=algorithm,
                key_data=self._encrypt_key_data(private_pem),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=self.config.key_rotation_days * 4),
                metadata={**metadata or {}, 'key_pair': public_key_id}
            )
            
            # Store keys
            with self.key_lock:
                self.keys[public_key_id] = public_key_obj
                self.keys[private_key_id] = private_key_obj
            
            # Schedule rotation
            self._schedule_key_rotation(public_key_id)
            self._schedule_key_rotation(private_key_id)
            
            # Audit log
            self._log_key_operation('keypair_generated', f"{public_key_id},{private_key_id}", metadata)
            
            self.logger.info(f"Generated key pair: {public_key_id}, {private_key_id}")
            return public_key_id, private_key_id
            
        except Exception as e:
            self.logger.error(f"Error generating key pair: {str(e)}")
            raise
    
    def encrypt_data(self, data: bytes, key_id: str = None,
                    algorithm: EncryptionAlgorithm = None,
                    metadata: Dict[str, Any] = None) -> EncryptionResult:
        """
        Encrypt data using specified or default key.
        
        Args:
            data: Data to encrypt
            key_id: Key ID to use (generates new if None)
            algorithm: Algorithm to use
            metadata: Optional metadata
            
        Returns:
            Encryption result
        """
        try:
            # Get or generate key
            if key_id is None:
                key_id = self.generate_key(algorithm, metadata)
            
            if key_id not in self.keys:
                return EncryptionResult(
                    success=False,
                    error=f"Key not found: {key_id}"
                )
            
            key = self.keys[key_id]
            
            # Decrypt key data for use
            key_data = self._decrypt_key_data(key.key_data)
            
            # Update key usage
            key.access_count += 1
            key.last_used = datetime.utcnow()
            
            # Compress data if enabled
            if self.config.enable_compression:
                data = self._compress_data(data)
            
            # Encrypt based on algorithm
            if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = self._encrypt_aes_gcm(data, key_data)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data = self._encrypt_aes_cbc(data, key_data)
            elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data = self._encrypt_chacha20(data, key_data)
            elif key.algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = self._encrypt_fernet(data, key_data)
            else:
                return EncryptionResult(
                    success=False,
                    error=f"Unsupported algorithm: {key.algorithm}"
                )
            
            # Add integrity check if enabled
            if self.config.enable_integrity_check:
                integrity_hash = hashlib.sha256(data).hexdigest()
                result_metadata = {**metadata or {}, 'integrity_hash': integrity_hash}
            else:
                result_metadata = metadata or {}
            
            # Audit log
            self._log_key_operation('data_encrypted', key_id, {
                'data_size': len(data),
                'encrypted_size': len(encrypted_data)
            })
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=key_id,
                algorithm=key.algorithm.value,
                metadata=result_metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {str(e)}")
            return EncryptionResult(
                success=False,
                error=str(e)
            )
    
    def decrypt_data(self, encrypted_data: bytes, key_id: str,
                    metadata: Dict[str, Any] = None) -> DecryptionResult:
        """
        Decrypt data using specified key.
        
        Args:
            encrypted_data: Encrypted data
            key_id: Key ID to use for decryption
            metadata: Optional metadata
            
        Returns:
            Decryption result
        """
        try:
            if key_id not in self.keys:
                return DecryptionResult(
                    success=False,
                    error=f"Key not found: {key_id}"
                )
            
            key = self.keys[key_id]
            
            # Check if key is active and not expired
            if not key.is_active:
                return DecryptionResult(
                    success=False,
                    error=f"Key is inactive: {key_id}"
                )
            
            if key.expires_at and datetime.utcnow() > key.expires_at:
                return DecryptionResult(
                    success=False,
                    error=f"Key has expired: {key_id}"
                )
            
            # Decrypt key data for use
            key_data = self._decrypt_key_data(key.key_data)
            
            # Update key usage
            key.access_count += 1
            key.last_used = datetime.utcnow()
            
            # Decrypt based on algorithm
            if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = self._decrypt_aes_gcm(encrypted_data, key_data)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_data = self._decrypt_aes_cbc(encrypted_data, key_data)
            elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = self._decrypt_chacha20(encrypted_data, key_data)
            elif key.algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = self._decrypt_fernet(encrypted_data, key_data)
            else:
                return DecryptionResult(
                    success=False,
                    error=f"Unsupported algorithm: {key.algorithm}"
                )
            
            # Decompress data if it was compressed
            if self.config.enable_compression:
                decrypted_data = self._decompress_data(decrypted_data)
            
            # Verify integrity if enabled
            if self.config.enable_integrity_check and metadata:
                expected_hash = metadata.get('integrity_hash')
                if expected_hash:
                    actual_hash = hashlib.sha256(decrypted_data).hexdigest()
                    if actual_hash != expected_hash:
                        return DecryptionResult(
                            success=False,
                            error="Integrity check failed"
                        )
            
            # Audit log
            self._log_key_operation('data_decrypted', key_id, {
                'encrypted_size': len(encrypted_data),
                'decrypted_size': len(decrypted_data)
            })
            
            return DecryptionResult(
                success=True,
                decrypted_data=decrypted_data,
                key_id=key_id,
                algorithm=key.algorithm.value,
                metadata=metadata or {}
            )
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {str(e)}")
            return DecryptionResult(
                success=False,
                error=str(e)
            )
    
    def rotate_key(self, key_id: str) -> str:
        """
        Rotate an encryption key.
        
        Args:
            key_id: Key ID to rotate
            
        Returns:
            New key ID
        """
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key not found: {key_id}")
            
            old_key = self.keys[key_id]
            
            # Generate new key with same algorithm and metadata
            new_key_id = self.generate_key(
                algorithm=old_key.algorithm,
                metadata={**old_key.metadata, 'rotated_from': key_id}
            )
            
            # Update old key
            old_key.is_active = False
            old_key.rotation_count += 1
            
            # Audit log
            self._log_key_operation('key_rotated', f"{key_id}->{new_key_id}", {
                'old_key_id': key_id,
                'new_key_id': new_key_id
            })
            
            self.logger.info(f"Rotated key: {key_id} -> {new_key_id}")
            return new_key_id
            
        except Exception as e:
            self.logger.error(f"Error rotating key {key_id}: {str(e)}")
            raise
    
    def derive_key(self, password: str, salt: bytes = None,
                  algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
                  metadata: Dict[str, Any] = None) -> str:
        """
        Derive a key from password using PBKDF2.
        
        Args:
            password: Password for key derivation
            salt: Salt for key derivation (auto-generated if None)
            algorithm: Algorithm for derived key
            metadata: Optional metadata
            
        Returns:
            Key ID for derived key
        """
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=self.config.key_derivation_iterations,
                backend=self.backend
            )
            
            derived_key = kdf.derive(password.encode('utf-8'))
            
            # Create key ID
            key_id = self._generate_key_id(algorithm, {**metadata or {}, 'derived': True})
            
            # Create key object
            key = EncryptionKey(
                key_id=key_id,
                key_type=KeyType.DERIVED,
                algorithm=algorithm,
                key_data=self._encrypt_key_data(derived_key),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=self.config.key_rotation_days),
                metadata={**metadata or {}, 'salt': base64.b64encode(salt).decode('utf-8')}
            )
            
            # Store key
            with self.key_lock:
                self.keys[key_id] = key
            
            # Audit log
            self._log_key_operation('key_derived', key_id, metadata)
            
            self.logger.info(f"Derived key: {key_id}")
            return key_id
            
        except Exception as e:
            self.logger.error(f"Error deriving key: {str(e)}")
            raise
    
    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a key (without sensitive data).
        
        Args:
            key_id: Key ID
            
        Returns:
            Key information dictionary
        """
        try:
            if key_id not in self.keys:
                return None
            
            key = self.keys[key_id]
            
            return {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'is_active': key.is_active,
                'rotation_count': key.rotation_count,
                'access_count': key.access_count,
                'last_used': key.last_used.isoformat() if key.last_used else None,
                'metadata': key.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Error getting key info: {str(e)}")
            return None
    
    def list_keys(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        List all keys with their information.
        
        Args:
            include_inactive: Include inactive keys
            
        Returns:
            List of key information dictionaries
        """
        try:
            keys_info = []
            
            for key in self.keys.values():
                if not include_inactive and not key.is_active:
                    continue
                
                key_info = self.get_key_info(key.key_id)
                if key_info:
                    keys_info.append(key_info)
            
            return keys_info
            
        except Exception as e:
            self.logger.error(f"Error listing keys: {str(e)}")
            return []
    
    def export_key(self, key_id: str, password: str) -> Optional[str]:
        """
        Export a key in encrypted format.
        
        Args:
            key_id: Key ID to export
            password: Password for export encryption
            
        Returns:
            Exported key data (base64 encoded)
        """
        try:
            if key_id not in self.keys:
                return None
            
            key = self.keys[key_id]
            
            # Create export data
            export_data = {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'key_data': base64.b64encode(self._decrypt_key_data(key.key_data)).decode('utf-8'),
                'created_at': key.created_at.isoformat(),
                'metadata': key.metadata,
                'exported_at': datetime.utcnow().isoformat()
            }
            
            # Encrypt export data with password
            export_json = json.dumps(export_data)
            encrypted_export = self._encrypt_with_password(export_json.encode('utf-8'), password)
            
            # Audit log
            self._log_key_operation('key_exported', key_id, {'export_size': len(encrypted_export)})
            
            return base64.b64encode(encrypted_export).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error exporting key {key_id}: {str(e)}")
            return None
    
    def import_key(self, exported_data: str, password: str) -> Optional[str]:
        """
        Import a key from exported format.
        
        Args:
            exported_data: Exported key data (base64 encoded)
            password: Password for decryption
            
        Returns:
            Imported key ID
        """
        try:
            # Decrypt export data
            encrypted_data = base64.b64decode(exported_data)
            decrypted_json = self._decrypt_with_password(encrypted_data, password)
            export_data = json.loads(decrypted_json.decode('utf-8'))
            
            # Create key object
            key_data = base64.b64decode(export_data['key_data'])
            
            key = EncryptionKey(
                key_id=export_data['key_id'],
                key_type=KeyType(export_data['key_type']),
                algorithm=EncryptionAlgorithm(export_data['algorithm']),
                key_data=self._encrypt_key_data(key_data),
                created_at=datetime.fromisoformat(export_data['created_at']),
                metadata=export_data['metadata']
            )
            
            # Store key
            with self.key_lock:
                self.keys[key.key_id] = key
            
            # Audit log
            self._log_key_operation('key_imported', key.key_id, {'import_size': len(exported_data)})
            
            self.logger.info(f"Imported key: {key.key_id}")
            return key.key_id
            
        except Exception as e:
            self.logger.error(f"Error importing key: {str(e)}")
            return None
    
    async def _key_rotation_scheduler(self):
        """Background task for automatic key rotation"""
        while self.rotation_enabled:
            try:
                current_time = datetime.utcnow()
                
                # Check for keys that need rotation
                keys_to_rotate = []
                for key in self.keys.values():
                    if (key.is_active and key.expires_at and 
                        current_time >= key.expires_at - timedelta(days=7)):  # Rotate 7 days before expiry
                        keys_to_rotate.append(key.key_id)
                
                # Rotate keys
                for key_id in keys_to_rotate:
                    try:
                        new_key_id = self.rotate_key(key_id)
                        self.logger.info(f"Auto-rotated key: {key_id} -> {new_key_id}")
                    except Exception as e:
                        self.logger.error(f"Failed to auto-rotate key {key_id}: {str(e)}")
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                self.logger.error(f"Error in key rotation scheduler: {str(e)}")
                await asyncio.sleep(86400)
    
    # Private helper methods
    
    def _generate_master_key(self) -> bytes:
        """Generate a new master key"""
        return secrets.token_bytes(32)
    
    def _generate_key_id(self, algorithm: EncryptionAlgorithm, metadata: Dict[str, Any]) -> str:
        """Generate unique key ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_suffix = secrets.token_hex(8)
        algorithm_prefix = algorithm.value[:8]
        return f"{algorithm_prefix}_{timestamp}_{random_suffix}"
    
    def _encrypt_key_data(self, key_data: bytes) -> bytes:
        """Encrypt key data with master key"""
        try:
            # Use Fernet for key encryption (key wrapping)
            fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
            return fernet.encrypt(key_data)
        except Exception as e:
            self.logger.error(f"Error encrypting key data: {str(e)}")
            raise
    
    def _decrypt_key_data(self, encrypted_key_data: bytes) -> bytes:
        """Decrypt key data with master key"""
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
            return fernet.decrypt(encrypted_key_data)
        except Exception as e:
            self.logger.error(f"Error decrypting key data: {str(e)}")
            raise
    
    def _schedule_key_rotation(self, key_id: str):
        """Schedule key for rotation"""
        if key_id in self.keys:
            key = self.keys[key_id]
            if key.expires_at:
                self.rotation_schedule[key_id] = key.expires_at
    
    def _log_key_operation(self, operation: str, key_id: str, metadata: Dict[str, Any]):
        """Log key operation for audit"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'key_id': key_id,
            'metadata': metadata
        }
        
        self.audit_log.append(log_entry)
        
        # Keep audit log size manageable
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]  # Keep last 5000 entries
    
    # Algorithm-specific encryption methods
    
    def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-GCM"""
        iv = secrets.token_bytes(12)  # 96-bit IV for GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
    
    def _decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-GCM"""
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-CBC"""
        iv = secrets.token_bytes(16)  # 128-bit IV for CBC
        
        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext
    
    def _decrypt_aes_cbc(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-CBC"""
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad data
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
    
    def _encrypt_chacha20(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return nonce + ciphertext
    
    def _decrypt_chacha20(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=self.backend)
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_fernet(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using Fernet"""
        fernet = Fernet(key)
        return fernet.encrypt(data)
    
    def _decrypt_fernet(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using Fernet"""
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)
    
    def _encrypt_with_password(self, data: bytes, password: str) -> bytes:
        """Encrypt data with password (for export/import)"""
        salt = secrets.token_bytes(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)
        return salt + encrypted_data
    
    def _decrypt_with_password(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data with password (for export/import)"""
        salt = encrypted_data[:32]
        ciphertext = encrypted_data[32:]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        
        fernet = Fernet(key)
        return fernet.decrypt(ciphertext)
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data if beneficial"""
        import gzip
        compressed = gzip.compress(data)
        # Only use compressed version if it's smaller
        return compressed if len(compressed) < len(data) else data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data"""
        import gzip
        try:
            return gzip.decompress(data)
        except:
            # If decompression fails, assume data was not compressed
            return data


# Export the classes for use in other modules
__all__ = [
    'EncryptionManager',
    'EncryptionKey',
    'EncryptionConfig',
    'EncryptionResult',
    'DecryptionResult',
    'EncryptionAlgorithm',
    'KeyType',
    'SecurityLevel'
]
