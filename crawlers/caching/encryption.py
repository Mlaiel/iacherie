#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cache Encryption - Security and Encryption for Cache Data
========================================================

Advanced encryption system for sensitive cache data with
key management, rotation, and multiple encryption algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    Fernet = None

from ...core.config import get_settings
from ...core.utils import generate_uuid

logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """
Encryption algorithm types."""

    NONE = "none"
    FERNET = "fernet"
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"

class KeyDerivationMethod(Enum):
    """Key derivation methods."""

    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"

@dataclass
class EncryptionKey:
    """Encryption key with metadata."""
    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    salt: bytes
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    rotation_interval: int = 86400  # 24 hours
    usage_count: int = 0
    max_usage: Optional[int] = None
    
    def is_expired(self) -> bool:
        """
Check if key is expired."""
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        if self.max_usage and self.usage_count >= self.max_usage:
            return True
        return False
    
    def should_rotate(self) -> bool:
        """
Check if key should be rotated."""
        rotation_time = self.created_at + timedelta(seconds=self.rotation_interval)
        return datetime.now() > rotation_time

@dataclass
class EncryptionResult:
    """
Encryption operation result."""
    encrypted_data: bytes
    key_id: str
    algorithm: EncryptionAlgorithm
    nonce: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class CacheEncryption:
    """
    Advanced cache encryption system.
    
    Features:
    - Multiple encryption algorithms
    - Key rotation and management
    - Secure key derivation
    - Metadata protection
    - Performance optimization
    """
    
    def __init__(self, master_key: Optional[str] = None,
                 algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET,
                 key_rotation_interval: int = 86400):
        """
        Initialize cache encryption.
        
        Args:
            master_key: Master encryption key
            algorithm: Default encryption algorithm
            key_rotation_interval: Key rotation interval in seconds
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography package required for encryption")
        
        self.master_key = master_key or self._generate_master_key()
        self.algorithm = algorithm
        self.key_rotation_interval = key_rotation_interval
        self.logger = logging.getLogger(f"{__name__}.CacheEncryption")
        
        # Key management
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.current_key_id: Optional[str] = None
        
        # Algorithm availability
        self.available_algorithms = {
            EncryptionAlgorithm.FERNET: True,
            EncryptionAlgorithm.AES_256_GCM: True,
            EncryptionAlgorithm.AES_256_CBC: True,
            EncryptionAlgorithm.CHACHA20_POLY1305: True
        }
        
        # Statistics
        self.encryption_count = 0
        self.decryption_count = 0
        self.key_rotations = 0
        
        # Initialize with current key
        asyncio.create_task(self._initialize_current_key())
        
        self.logger.info(f"Cache encryption initialized with {algorithm.value}")
    
    def _generate_master_key(self) -> str:
        """Generate secure master key."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _derive_key(self, algorithm: EncryptionAlgorithm, 
                   salt: bytes, key_length: int = 32) -> bytes:
        """
Derive encryption key from master key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.master_key.encode())
    
    async def _initialize_current_key(self) -> None:
        """
Initialize current encryption key."""
        try:
            current_key = await self._generate_key(self.algorithm)
            self.current_key_id = current_key.key_id
            self.logger.info(f"Initialized encryption key: {self.current_key_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption key: {e}")
    
    async def _generate_key(self, algorithm: EncryptionAlgorithm) -> EncryptionKey:
        """Generate new encryption key."""
        key_id = generate_uuid()
        salt = secrets.token_bytes(16)
        
        # Determine key length based on algorithm
        key_length = 32  # Default for 256-bit
        if algorithm == EncryptionAlgorithm.FERNET:
            key_length = 32
        elif algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
            key_length = 32
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_length = 32
        
        key_data = self._derive_key(algorithm, salt, key_length)
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            key_data=key_data,
            salt=salt,
            rotation_interval=self.key_rotation_interval
        )
        
        self.encryption_keys[key_id] = encryption_key
        return encryption_key
    
    async def encrypt(self, data: Any, 
                     algorithm: Optional[EncryptionAlgorithm] = None) -> EncryptionResult:
        """
        Encrypt data for cache storage.
        
        Args:
            data: Data to encrypt
            algorithm: Encryption algorithm override
            
        Returns:
            Encryption result with metadata
        """
        try:
            # Serialize data
            if isinstance(data, bytes):
                plaintext = data
            elif isinstance(data, str):
                plaintext = data.encode('utf-8')
            else:
                plaintext = json.dumps(data, separators=(',', ':')).encode('utf-8')
            
            # Get encryption key
            selected_algorithm = algorithm or self.algorithm
            encryption_key = await self._get_current_key(selected_algorithm)
            
            # Encrypt based on algorithm
            if selected_algorithm == EncryptionAlgorithm.FERNET:
                result = await self._encrypt_fernet(plaintext, encryption_key)
            elif selected_algorithm == EncryptionAlgorithm.AES_256_GCM:
                result = await self._encrypt_aes_gcm(plaintext, encryption_key)
            elif selected_algorithm == EncryptionAlgorithm.AES_256_CBC:
                result = await self._encrypt_aes_cbc(plaintext, encryption_key)
            elif selected_algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                result = await self._encrypt_chacha20(plaintext, encryption_key)
            else:
                # No encryption
                result = EncryptionResult(
                    encrypted_data=plaintext,
                    key_id="none",
                    algorithm=EncryptionAlgorithm.NONE
                )
            
            # Update statistics
            encryption_key.usage_count += 1
            self.encryption_count += 1
            
            # Check for key rotation
            if encryption_key.should_rotate():
                asyncio.create_task(self._rotate_key())
            
            return result
            
        except Exception as e:
            self.logger.error(f"Encryption error: {e}")
            raise
    
    async def decrypt(self, encrypted_result: EncryptionResult) -> Any:
        """
        Decrypt cached data.
        
        Args:
            encrypted_result: Encryption result from encrypt()
            
        Returns:
            Original decrypted data
        """
        try:
            if encrypted_result.algorithm == EncryptionAlgorithm.NONE:
                return self._deserialize_data(encrypted_result.encrypted_data)
            
            # Get decryption key
            encryption_key = self.encryption_keys.get(encrypted_result.key_id)
            if not encryption_key:
                raise ValueError(f"Encryption key not found: {encrypted_result.key_id}")
            
            # Decrypt based on algorithm
            if encrypted_result.algorithm == EncryptionAlgorithm.FERNET:
                plaintext = await self._decrypt_fernet(encrypted_result, encryption_key)
            elif encrypted_result.algorithm == EncryptionAlgorithm.AES_256_GCM:
                plaintext = await self._decrypt_aes_gcm(encrypted_result, encryption_key)
            elif encrypted_result.algorithm == EncryptionAlgorithm.AES_256_CBC:
                plaintext = await self._decrypt_aes_cbc(encrypted_result, encryption_key)
            elif encrypted_result.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                plaintext = await self._decrypt_chacha20(encrypted_result, encryption_key)
            else:
                raise ValueError(f"Unsupported algorithm: {encrypted_result.algorithm}")
            
            # Update statistics
            self.decryption_count += 1
            
            return self._deserialize_data(plaintext)
            
        except Exception as e:
            self.logger.error(f"Decryption error: {e}")
            raise
    
    async def _encrypt_fernet(self, plaintext: bytes, 
                            encryption_key: EncryptionKey) -> EncryptionResult:
        """Encrypt with Fernet algorithm."""
        fernet = Fernet(base64.urlsafe_b64encode(encryption_key.key_data))
        encrypted_data = fernet.encrypt(plaintext)
        
        return EncryptionResult(
            encrypted_data=encrypted_data,
            key_id=encryption_key.key_id,
            algorithm=EncryptionAlgorithm.FERNET
        )
    
    async def _decrypt_fernet(self, encrypted_result: EncryptionResult,
                            encryption_key: EncryptionKey) -> bytes:
        """
Decrypt with Fernet algorithm."""
        fernet = Fernet(base64.urlsafe_b64encode(encryption_key.key_data))
        return fernet.decrypt(encrypted_result.encrypted_data)
    
    async def _encrypt_aes_gcm(self, plaintext: bytes,
                             encryption_key: EncryptionKey) -> EncryptionResult:
        """
Encrypt with AES-256-GCM."""
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        
        cipher = Cipher(
            algorithms.AES(encryption_key.key_data),
            modes.GCM(nonce),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            encrypted_data=ciphertext,
            key_id=encryption_key.key_id,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            nonce=nonce,
            tag=encryptor.tag
        )
    
    async def _decrypt_aes_gcm(self, encrypted_result: EncryptionResult,
                             encryption_key: EncryptionKey) -> bytes:
        """
Decrypt with AES-256-GCM."""
        cipher = Cipher(
            algorithms.AES(encryption_key.key_data),
            modes.GCM(encrypted_result.nonce, encrypted_result.tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_result.encrypted_data) + decryptor.finalize()
    
    async def _encrypt_aes_cbc(self, plaintext: bytes,
                             encryption_key: EncryptionKey) -> EncryptionResult:
        """
Encrypt with AES-256-CBC."""
        # Pad plaintext to 16-byte boundary
        padding_length = 16 - (len(plaintext) % 16)
        padded_plaintext = plaintext + bytes([padding_length] * padding_length)
        
        nonce = secrets.token_bytes(16)  # 128-bit IV for CBC
        
        cipher = Cipher(
            algorithms.AES(encryption_key.key_data),
            modes.CBC(nonce),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            encrypted_data=ciphertext,
            key_id=encryption_key.key_id,
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            nonce=nonce
        )
    
    async def _decrypt_aes_cbc(self, encrypted_result: EncryptionResult,
                             encryption_key: EncryptionKey) -> bytes:
        """
Decrypt with AES-256-CBC."""
        cipher = Cipher(
            algorithms.AES(encryption_key.key_data),
            modes.CBC(encrypted_result.nonce),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(encrypted_result.encrypted_data) + decryptor.finalize()
        
        # Remove padding
        padding_length = padded_plaintext[-1]
        return padded_plaintext[:-padding_length]
    
    async def _encrypt_chacha20(self, plaintext: bytes,
                              encryption_key: EncryptionKey) -> EncryptionResult:
        """
Encrypt with ChaCha20-Poly1305."""
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        
        cipher = Cipher(
            algorithms.ChaCha20(encryption_key.key_data, nonce),
            modes.GCM(b''),  # Using GCM mode for authentication
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptionResult(
            encrypted_data=ciphertext,
            key_id=encryption_key.key_id,
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            nonce=nonce,
            tag=encryptor.tag
        )
    
    async def _decrypt_chacha20(self, encrypted_result: EncryptionResult,
                              encryption_key: EncryptionKey) -> bytes:
        """
Decrypt with ChaCha20-Poly1305."""
        cipher = Cipher(
            algorithms.ChaCha20(encryption_key.key_data, encrypted_result.nonce),
            modes.GCM(b'', encrypted_result.tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_result.encrypted_data) + decryptor.finalize()
    
    async def _get_current_key(self, algorithm: EncryptionAlgorithm) -> EncryptionKey:
        """
Get current encryption key for algorithm."""
        if self.current_key_id:
            current_key = self.encryption_keys.get(self.current_key_id)
            if current_key and current_key.algorithm == algorithm and not current_key.is_expired():
                return current_key
        
        # Generate new key
        return await self._generate_key(algorithm)
    
    async def _rotate_key(self) -> None:
        """
Rotate encryption key."""
        try:
            new_key = await self._generate_key(self.algorithm)
            old_key_id = self.current_key_id
            self.current_key_id = new_key.key_id
            self.key_rotations += 1
            
            self.logger.info(f"Key rotated: {old_key_id} -> {new_key.key_id}")
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize decrypted data."""
        try:
            # Try JSON first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            
            # Try string
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                pass
            
            # Return as bytes
            return data
            
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            return data
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get encryption statistics."""
        active_keys = sum(1 for key in self.encryption_keys.values() if not key.is_expired())
        expired_keys = sum(1 for key in self.encryption_keys.values() if key.is_expired())
        
        return {
            "total_keys": len(self.encryption_keys),
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "current_key_id": self.current_key_id,
            "encryption_count": self.encryption_count,
            "decryption_count": self.decryption_count,
            "key_rotations": self.key_rotations,
            "available_algorithms": [
                algo.value for algo, available in self.available_algorithms.items()
                if available
            ]
        }

class SecureCacheManager:
    """
    Secure cache manager with encryption integration.
    
    Combines caching with automatic encryption for sensitive data.
    """
    
    def __init__(self, cache_manager, encryption: Optional[CacheEncryption] = None):
        """
Initialize secure cache manager."""
        self.cache_manager = cache_manager
        self.encryption = encryption or CacheEncryption()
        self.logger = logging.getLogger(f"{__name__}.SecureCacheManager")
        
        # Security settings
        self.encrypt_by_default = True
        self.sensitive_patterns = [
            r'.*password.*',
            r'.*token.*',
            r'.*secret.*',
            r'.*key.*',
            r'.*auth.*'
        ]
        
        self.logger.info("Secure cache manager initialized")
    
    def _should_encrypt(self, key: str, data: Any) -> bool:
        """Determine if data should be encrypted."""
        if self.encrypt_by_default:
            return True
        
        # Check for sensitive key patterns
        import re
        for pattern in self.sensitive_patterns:
            if re.match(pattern, key, re.IGNORECASE):
                return True
        
        # Check for sensitive data content
        if isinstance(data, (dict, str)) and isinstance(data, str):
            data_str = str(data).lower()
            if any(term in data_str for term in ['password', 'token', 'secret', 'key']):
                return True
        
        return False
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                 encrypt: Optional[bool] = None) -> bool:
        """
Set value with optional encryption."""
        try:
            should_encrypt = encrypt if encrypt is not None else self._should_encrypt(key, value)
            
            if should_encrypt:
                # Encrypt data
                encrypted_result = await self.encryption.encrypt(value)
                
                # Store encryption metadata separately
                metadata_key = f"_meta:{key}"
                metadata = {
                    "encrypted": True,
                    "algorithm": encrypted_result.algorithm.value,
                    "key_id": encrypted_result.key_id,
                    "nonce": base64.b64encode(encrypted_result.nonce).decode() if encrypted_result.nonce else None,
                    "tag": base64.b64encode(encrypted_result.tag).decode() if encrypted_result.tag else None
                }
                
                # Store encrypted data and metadata
                data_stored = await self.cache_manager.set(key, encrypted_result.encrypted_data, ttl)
                meta_stored = await self.cache_manager.set(metadata_key, metadata, ttl)
                
                return data_stored and meta_stored
            else:
                # Store unencrypted
                return await self.cache_manager.set(key, value, ttl)
                
        except Exception as e:
            self.logger.error(f"Error setting secure cache key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Any:
        """Get value with automatic decryption."""
        try:
            # Check if data is encrypted
            metadata_key = f"_meta:{key}"
            metadata = await self.cache_manager.get(metadata_key)
            
            if metadata and metadata.get('encrypted'):
                # Get encrypted data
                encrypted_data = await self.cache_manager.get(key)
                if encrypted_data is None:
                    return None
                
                # Reconstruct encryption result
                encrypted_result = EncryptionResult(
                    encrypted_data=encrypted_data,
                    key_id=metadata['key_id'],
                    algorithm=EncryptionAlgorithm(metadata['algorithm']),
                    nonce=base64.b64decode(metadata['nonce']) if metadata.get('nonce') else None,
                    tag=base64.b64decode(metadata['tag']) if metadata.get('tag') else None
                )
                
                # Decrypt data
                return await self.encryption.decrypt(encrypted_result)
            else:
                # Get unencrypted data
                return await self.cache_manager.get(key)
                
        except Exception as e:
            self.logger.error(f"Error getting secure cache key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete value and its metadata."""
        try:
            metadata_key = f"_meta:{key}"
            
            # Delete both data and metadata
            data_deleted = await self.cache_manager.delete(key)
            meta_deleted = await self.cache_manager.delete(metadata_key)
            
            return data_deleted or meta_deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting secure cache key {key}: {e}")
            return False
