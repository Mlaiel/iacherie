"""Data Encryption Service - Chiffrement données

Enterprise-grade data encryption service for sensitive information protection.
Consolidates encryption functionality from existing modules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_OAEP_4096 = "rsa_oaep_4096"


class KeyType(Enum):
    """Types of cryptographic keys"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    CONTENT = "content"
    DATABASE = "database"


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptedData:
    """Encrypted data container"""
    data: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataEncryptionService:
    """
    Enterprise data encryption service providing unified encryption capabilities.
    Consolidates functionality from core/security/encryption.py and api/security/encryption.py
    """
    
    def __init__(self, master_key: Optional[str] = None):
        self.logger = logger
        self.master_key = master_key or self._generate_master_key()
        self.active_keys: Dict[str, EncryptionKey] = {}
        
    def _generate_master_key(self) -> str:
        """Generate master encryption key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    
    async def encrypt_sensitive_data(
        self, 
        data: Union[str, bytes], 
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        key_type: KeyType = KeyType.SYMMETRIC
    ) -> Tuple[EncryptedData, str]:
        """
        Encrypt sensitive data with appropriate algorithm
        
        Args:
            data: Data to encrypt (string or bytes)
            algorithm: Encryption algorithm to use
            key_type: Type of key to generate
            
        Returns:
            Tuple of (EncryptedData, key_id)
        """
        try:
            # Convert string to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Generate key for this data
            key_id = self._generate_key_id()
            
            # Encrypt based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = await self._encrypt_aes_gcm(data_bytes, key_id)
            elif algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = await self._encrypt_fernet(data_bytes, key_id)
            elif algorithm == EncryptionAlgorithm.RSA_OAEP_4096:
                encrypted_data = await self._encrypt_rsa(data_bytes, key_id)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
            return encrypted_data, key_id
            
        except Exception as e:
            self.logger.error(f"Data encryption failed: {str(e)}")
            raise
    
    async def decrypt_sensitive_data(self, encrypted_data: EncryptedData) -> bytes:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_data: EncryptedData object to decrypt
            
        Returns:
            Decrypted bytes
        """
        try:
            if encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM:
                return await self._decrypt_aes_gcm(encrypted_data)
            elif encrypted_data.algorithm == EncryptionAlgorithm.FERNET:
                return await self._decrypt_fernet(encrypted_data)
            elif encrypted_data.algorithm == EncryptionAlgorithm.RSA_OAEP_4096:
                return await self._decrypt_rsa(encrypted_data)
            else:
                raise ValueError(f"Unsupported algorithm: {encrypted_data.algorithm}")
                
        except Exception as e:
            self.logger.error(f"Data decryption failed: {str(e)}")
            raise
    
    async def _encrypt_aes_gcm(self, data: bytes, key_id: str) -> EncryptedData:
        """Encrypt data using AES-256-GCM"""
        key = secrets.token_bytes(32)  # 256-bit key
        iv = secrets.token_bytes(12)   # 96-bit IV for GCM
        
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(iv, data, None)
        
        # Store key securely (simplified for demo)
        self.active_keys[key_id] = EncryptionKey(
            key_id=key_id,
            key_type=KeyType.SYMMETRIC,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            created_at=datetime.now(),
            metadata={'key': base64.b64encode(key).decode()}
        )
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id=key_id,
            iv=iv,
            metadata={'encryption_time': datetime.now().isoformat()}
        )
    
    async def _decrypt_aes_gcm(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using AES-256-GCM"""
        if encrypted_data.key_id not in self.active_keys:
            raise ValueError(f"Key not found: {encrypted_data.key_id}")
        
        key_info = self.active_keys[encrypted_data.key_id]
        key = base64.b64decode(key_info.metadata['key'])
        
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(encrypted_data.iv, encrypted_data.data, None)
    
    async def _encrypt_fernet(self, data: bytes, key_id: str) -> EncryptedData:
        """Encrypt data using Fernet"""
        key = Fernet.generate_key()
        f = Fernet(key)
        ciphertext = f.encrypt(data)
        
        # Store key securely
        self.active_keys[key_id] = EncryptionKey(
            key_id=key_id,
            key_type=KeyType.SYMMETRIC,
            algorithm=EncryptionAlgorithm.FERNET,
            created_at=datetime.now(),
            metadata={'key': key.decode()}
        )
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.FERNET,
            key_id=key_id,
            metadata={'encryption_time': datetime.now().isoformat()}
        )
    
    async def _decrypt_fernet(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using Fernet"""
        if encrypted_data.key_id not in self.active_keys:
            raise ValueError(f"Key not found: {encrypted_data.key_id}")
        
        key_info = self.active_keys[encrypted_data.key_id]
        f = Fernet(key_info.metadata['key'].encode())
        return f.decrypt(encrypted_data.data)
    
    async def _encrypt_rsa(self, data: bytes, key_id: str) -> EncryptedData:
        """Encrypt data using RSA-OAEP"""
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Encrypt data
        ciphertext = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Store keys securely
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        self.active_keys[key_id] = EncryptionKey(
            key_id=key_id,
            key_type=KeyType.ASYMMETRIC,
            algorithm=EncryptionAlgorithm.RSA_OAEP_4096,
            created_at=datetime.now(),
            metadata={'private_key': base64.b64encode(private_pem).decode()}
        )
        
        return EncryptedData(
            data=ciphertext,
            algorithm=EncryptionAlgorithm.RSA_OAEP_4096,
            key_id=key_id,
            metadata={'encryption_time': datetime.now().isoformat()}
        )
    
    async def _decrypt_rsa(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using RSA-OAEP"""
        if encrypted_data.key_id not in self.active_keys:
            raise ValueError(f"Key not found: {encrypted_data.key_id}")
        
        key_info = self.active_keys[encrypted_data.key_id]
        private_pem = base64.b64decode(key_info.metadata['private_key'])
        
        private_key = serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
        
        return private_key.decrypt(
            encrypted_data.data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
    def _generate_key_id(self) -> str:
        """Generate unique key identifier"""
        timestamp = int(datetime.now().timestamp())
        random_part = secrets.token_hex(8)
        return f"key_{timestamp}_{random_part}"
    
    async def get_encryption_stats(self) -> Dict[str, Any]:
        """Get encryption service statistics"""
        return {
            'active_keys': len(self.active_keys),
            'algorithms_supported': [alg.value for alg in EncryptionAlgorithm],
            'service_status': 'active',
            'last_updated': datetime.now().isoformat()
        }