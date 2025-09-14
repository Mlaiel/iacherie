"""{{encryption_name}} Encryption Template for Ainflue Platform
import asyncio

{{encryption_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import os
import base64
import hashlib
import hmac
import secrets
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
import bcrypt
from pydantic import BaseModel, Field, validator

from core.config import get_settings
from utils.exceptions import EncryptionException, SecurityException
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class EncryptionAlgorithm(Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"


class HashAlgorithm(Enum):
    """Hash algorithms"""
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    ARGON2 = "argon2"
    BCRYPT = "bcrypt"
    SCRYPT = "scrypt"
    PBKDF2 = "pbkdf2"


class KeyDerivationFunction(Enum):
    """Key derivation functions"""
    PBKDF2_HMAC = "pbkdf2_hmac"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"


class EncryptionConfig(BaseModel):
    """Encryption configuration"""
    algorithm: EncryptionAlgorithm = Field(..., description="Encryption algorithm")
    key_size: int = Field(default=256, description="Key size in bits")
    hash_algorithm: HashAlgorithm = Field(default=HashAlgorithm.SHA256, description="Hash algorithm")
    kdf: KeyDerivationFunction = Field(default=KeyDerivationFunction.PBKDF2_HMAC, description="Key derivation function")
    iterations: int = Field(default=100000, description="KDF iterations")
    salt_size: int = Field(default=32, description="Salt size in bytes")
    iv_size: int = Field(default=16, description="IV size in bytes")
    tag_size: int = Field(default=16, description="Authentication tag size in bytes")
    
    @validator('key_size')
    def validate_key_size(cls, v) -> None:
        if v not in [128, 192, 256, 512, 1024, 2048, 4096]:
            raise ValueError('Invalid key size')
        return v
    
    @validator('iterations')
    def validate_iterations(cls, v) -> None:
        if v < 1000:
            raise ValueError('Iterations must be at least 1000')
        return v


class EncryptedData(BaseModel):
    """Encrypted data container"""
    data: str = Field(..., description="Base64-encoded encrypted data")
    algorithm: str = Field(..., description="Encryption algorithm used")
    salt: Optional[str] = Field(None, description="Base64-encoded salt")
    iv: Optional[str] = Field(None, description="Base64-encoded initialization vector")
    tag: Optional[str] = Field(None, description="Base64-encoded authentication tag")
    key_id: Optional[str] = Field(None, description="Key identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Encryption timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class KeyInfo(BaseModel):
    """Cryptographic key information"""
    key_id: str = Field(..., description="Unique key identifier")
    algorithm: EncryptionAlgorithm = Field(..., description="Associated algorithm")
    key_type: str = Field(..., description="Key type (symmetric/asymmetric)")
    key_size: int = Field(..., description="Key size in bits")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Key creation time")
    expires_at: Optional[datetime] = Field(None, description="Key expiration time")
    is_active: bool = Field(default=True, description="Whether key is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Key metadata")


class {{encryption_name}}Manager:
    """{{encryption_description}} with comprehensive cryptographic operations"""
    
    def __init__(
        self,
        master_key: Optional[str] = None,
        key_rotation_interval: timedelta = timedelta(days=90),
        enable_key_rotation: bool = True,
        metrics_collector: Optional[SecurityMetricsCollector] = None
    ):
        self.master_key = master_key or self._generate_master_key()
        self.key_rotation_interval = key_rotation_interval
        self.enable_key_rotation = enable_key_rotation
        self.metrics_collector = metrics_collector or SecurityMetricsCollector()
        
        # Key storage
        self.symmetric_keys: Dict[str, bytes] = {}
        self.asymmetric_keys: Dict[str, Tuple[bytes, bytes]] = {}  # (private, public)
        self.key_info: Dict[str, KeyInfo] = {}
        
        # Default configurations
        self.default_config = EncryptionConfig()
        
        # Initialize backend
        self.backend = default_backend()
        
        logger.info("Encryption manager initialized")
    
    def _generate_master_key(self) -> str:
        """Generate a master key"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    # Key Management
    async def generate_symmetric_key(
        self, 
        key_id: str, 
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        key_size: int = 256
    ) -> str:
        """Generate a symmetric encryption key"""
        
        try:
            # Generate key
            if algorithm == EncryptionAlgorithm.FERNET:
                key = Fernet.generate_key()
            else:
                key = secrets.token_bytes(key_size // 8)
            
            # Store key
            self.symmetric_keys[key_id] = key
            
            # Store key info
            self.key_info[key_id] = KeyInfo(
                key_id=key_id,
                algorithm=algorithm,
                key_type="symmetric",
                key_size=key_size,
                expires_at=datetime.utcnow() + self.key_rotation_interval if self.enable_key_rotation else None
            )
            
            # Record metrics
            await self.metrics_collector.record_key_generation(
                key_id=key_id,
                algorithm=algorithm.value,
                key_type="symmetric",
                success=True
            )
            
            logger.info(f"Generated symmetric key: {key_id}")
            return key_id
            
        except Exception as e:
            await self.metrics_collector.record_key_generation(
                key_id=key_id,
                algorithm=algorithm.value,
                key_type="symmetric",
                success=False
            )
            logger.error(f"Failed to generate symmetric key {key_id}: {e}")
            raise EncryptionException(f"Key generation failed: {e}")
    
    async def generate_asymmetric_keypair(
        self, 
        key_id: str, 
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.RSA_2048
    ) -> str:
        """Generate an asymmetric key pair"""
        
        try:
            if algorithm == EncryptionAlgorithm.RSA_2048:
                key_size = 2048
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                key_size = 4096
            else:
                raise EncryptionException(f"Unsupported asymmetric algorithm: {algorithm}")
            
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
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
            
            # Store keys
            self.asymmetric_keys[key_id] = (private_pem, public_pem)
            
            # Store key info
            self.key_info[key_id] = KeyInfo(
                key_id=key_id,
                algorithm=algorithm,
                key_type="asymmetric",
                key_size=key_size,
                expires_at=datetime.utcnow() + self.key_rotation_interval if self.enable_key_rotation else None
            )
            
            # Record metrics
            await self.metrics_collector.record_key_generation(
                key_id=key_id,
                algorithm=algorithm.value,
                key_type="asymmetric",
                success=True
            )
            
            logger.info(f"Generated asymmetric key pair: {key_id}")
            return key_id
            
        except Exception as e:
            await self.metrics_collector.record_key_generation(
                key_id=key_id,
                algorithm=algorithm.value,
                key_type="asymmetric",
                success=False
            )
            logger.error(f"Failed to generate asymmetric key pair {key_id}: {e}")
            raise EncryptionException(f"Key pair generation failed: {e}")
    
    async def derive_key_from_password(
        self, 
        password: str, 
        salt: Optional[bytes] = None,
        kdf: KeyDerivationFunction = KeyDerivationFunction.PBKDF2_HMAC,
        iterations: int = 100000,
        key_length: int = 32
    ) -> Tuple[bytes, bytes]:
        """Derive encryption key from password"""
        
        try:
            # Generate salt if not provided
            if salt is None:
                salt = secrets.token_bytes(32)
            
            if kdf == KeyDerivationFunction.PBKDF2_HMAC:
                kdf_instance = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=key_length,
                    salt=salt,
                    iterations=iterations,
                    backend=self.backend
                )
                key = kdf_instance.derive(password.encode())
            
            elif kdf == KeyDerivationFunction.SCRYPT:
                kdf_instance = Scrypt(
                    algorithm=hashes.SHA256(),
                    length=key_length,
                    salt=salt,
                    n=2**14,
                    r=8,
                    p=1,
                    backend=self.backend
                )
                key = kdf_instance.derive(password.encode())
            
            else:
                raise EncryptionException(f"Unsupported KDF: {kdf}")
            
            return key, salt
            
        except Exception as e:
            logger.error(f"Key derivation failed: {e}")
            raise EncryptionException(f"Key derivation failed: {e}")
    
    # Symmetric Encryption
    async def encrypt_symmetric(
        self, 
        plaintext: Union[str, bytes], 
        key_id: Optional[str] = None,
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        config: Optional[EncryptionConfig] = None
    ) -> EncryptedData:
        """Encrypt data using symmetric encryption"""
        
        start_time = datetime.utcnow()
        
        try:
            # Convert to bytes if string
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            
            # Use provided config or default
            enc_config = config or self.default_config
            
            # Get or generate key
            if key_id and key_id in self.symmetric_keys:
                key = self.symmetric_keys[key_id]
            else:
                # Generate temporary key
                key = secrets.token_bytes(enc_config.key_size // 8)
                key_id = f"temp_{secrets.token_hex(8)}"
                self.symmetric_keys[key_id] = key
            
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = await self._encrypt_aes_gcm(plaintext, key, enc_config)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data = await self._encrypt_aes_cbc(plaintext, key, enc_config)
            elif algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = await self._encrypt_fernet(plaintext, key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data = await self._encrypt_chacha20_poly1305(plaintext, key, enc_config)
            else:
                raise EncryptionException(f"Unsupported symmetric algorithm: {algorithm}")
            
            # Add metadata
            encrypted_data.algorithm = algorithm.value
            encrypted_data.key_id = key_id
            encrypted_data.timestamp = datetime.utcnow()
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="encrypt",
                algorithm=algorithm.value,
                data_size=len(plaintext),
                processing_time=processing_time,
                success=True
            )
            
            return encrypted_data
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="encrypt",
                algorithm=algorithm.value,
                data_size=len(plaintext) if isinstance(plaintext, bytes) else len(plaintext.encode()),
                processing_time=processing_time,
                success=False
            )
            logger.error(f"Symmetric encryption failed: {e}")
            raise EncryptionException(f"Encryption failed: {e}")
    
    async def decrypt_symmetric(self, encrypted_data: EncryptedData) -> bytes:
        """Decrypt data using symmetric encryption"""
        
        start_time = datetime.utcnow()
        
        try:
            # Get key
            if not encrypted_data.key_id or encrypted_data.key_id not in self.symmetric_keys:
                raise EncryptionException("Encryption key not found")
            
            key = self.symmetric_keys[encrypted_data.key_id]
            algorithm = EncryptionAlgorithm(encrypted_data.algorithm)
            
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                plaintext = await self._decrypt_aes_gcm(encrypted_data, key)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                plaintext = await self._decrypt_aes_cbc(encrypted_data, key)
            elif algorithm == EncryptionAlgorithm.FERNET:
                plaintext = await self._decrypt_fernet(encrypted_data, key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                plaintext = await self._decrypt_chacha20_poly1305(encrypted_data, key)
            else:
                raise EncryptionException(f"Unsupported symmetric algorithm: {algorithm}")
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="decrypt",
                algorithm=algorithm.value,
                data_size=len(plaintext),
                processing_time=processing_time,
                success=True
            )
            
            return plaintext
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="decrypt",
                algorithm=encrypted_data.algorithm,
                data_size=0,
                processing_time=processing_time,
                success=False
            )
            logger.error(f"Symmetric decryption failed: {e}")
            raise EncryptionException(f"Decryption failed: {e}")
    
    # Asymmetric Encryption
    async def encrypt_asymmetric(
        self, 
        plaintext: Union[str, bytes], 
        key_id: str,
        use_public_key: bool = True
    ) -> EncryptedData:
        """Encrypt data using asymmetric encryption"""
        
        start_time = datetime.utcnow()
        
        try:
            # Convert to bytes if string
            if isinstance(plaintext, str):
                plaintext = plaintext.encode('utf-8')
            
            # Get key pair
            if key_id not in self.asymmetric_keys:
                raise EncryptionException(f"Key pair not found: {key_id}")
            
            private_pem, public_pem = self.asymmetric_keys[key_id]
            
            # Load appropriate key
            if use_public_key:
                key = serialization.load_pem_public_key(public_pem, backend=self.backend)
            else:
                key = serialization.load_pem_private_key(private_pem, password=None, backend=self.backend)
            
            # Encrypt data
            ciphertext = key.encrypt(
                plaintext,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Create encrypted data object
            encrypted_data = EncryptedData(
                data=base64.b64encode(ciphertext).decode(),
                algorithm=self.key_info[key_id].algorithm.value,
                key_id=key_id,
                timestamp=datetime.utcnow()
            )
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="encrypt",
                algorithm=encrypted_data.algorithm,
                data_size=len(plaintext),
                processing_time=processing_time,
                success=True
            )
            
            return encrypted_data
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="encrypt",
                algorithm="rsa",
                data_size=len(plaintext) if isinstance(plaintext, bytes) else len(plaintext.encode()),
                processing_time=processing_time,
                success=False
            )
            logger.error(f"Asymmetric encryption failed: {e}")
            raise EncryptionException(f"Asymmetric encryption failed: {e}")
    
    async def decrypt_asymmetric(self, encrypted_data: EncryptedData, use_private_key: bool = True) -> bytes:
        """Decrypt data using asymmetric encryption"""
        
        start_time = datetime.utcnow()
        
        try:
            # Get key pair
            if not encrypted_data.key_id or encrypted_data.key_id not in self.asymmetric_keys:
                raise EncryptionException("Key pair not found")
            
            private_pem, public_pem = self.asymmetric_keys[encrypted_data.key_id]
            
            # Load appropriate key
            if use_private_key:
                key = serialization.load_pem_private_key(private_pem, password=None, backend=self.backend)
            else:
                key = serialization.load_pem_public_key(public_pem, backend=self.backend)
            
            # Decrypt data
            ciphertext = base64.b64decode(encrypted_data.data.encode())
            plaintext = key.decrypt(
                ciphertext,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="decrypt",
                algorithm=encrypted_data.algorithm,
                data_size=len(plaintext),
                processing_time=processing_time,
                success=True
            )
            
            return plaintext
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_encryption_operation(
                operation="decrypt",
                algorithm=encrypted_data.algorithm,
                data_size=0,
                processing_time=processing_time,
                success=False
            )
            logger.error(f"Asymmetric decryption failed: {e}")
            raise EncryptionException(f"Asymmetric decryption failed: {e}")
    
    # Specific encryption implementations
    async def _encrypt_aes_gcm(self, plaintext: bytes, key: bytes, config: EncryptionConfig) -> EncryptedData:
        """Encrypt using AES-256-GCM"""
        iv = secrets.token_bytes(config.iv_size)
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptedData(
            data=base64.b64encode(ciphertext).decode(),
            algorithm=EncryptionAlgorithm.AES_256_GCM.value,
            iv=base64.b64encode(iv).decode(),
            tag=base64.b64encode(encryptor.tag).decode()
        )
    
    async def _decrypt_aes_gcm(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using AES-256-GCM"""
        ciphertext = base64.b64decode(encrypted_data.data.encode())
        iv = base64.b64decode(encrypted_data.iv.encode())
        tag = base64.b64decode(encrypted_data.tag.encode())
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _encrypt_aes_cbc(self, plaintext: bytes, key: bytes, config: EncryptionConfig) -> EncryptedData:
        """Encrypt using AES-256-CBC"""
        iv = secrets.token_bytes(config.iv_size)
        
        # Add PKCS7 padding
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return EncryptedData(
            data=base64.b64encode(ciphertext).decode(),
            algorithm=EncryptionAlgorithm.AES_256_CBC.value,
            iv=base64.b64encode(iv).decode()
        )
    
    async def _decrypt_aes_cbc(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using AES-256-CBC"""
        ciphertext = base64.b64decode(encrypted_data.data.encode())
        iv = base64.b64decode(encrypted_data.iv.encode())
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded_plaintext) + unpadder.finalize()
    
    async def _encrypt_fernet(self, plaintext: bytes, key: bytes) -> EncryptedData:
        """Encrypt using Fernet"""
        fernet = Fernet(key)
        ciphertext = fernet.encrypt(plaintext)
        
        return EncryptedData(
            data=base64.b64encode(ciphertext).decode(),
            algorithm=EncryptionAlgorithm.FERNET.value
        )
    
    async def _decrypt_fernet(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using Fernet"""
        fernet = Fernet(key)
        ciphertext = base64.b64decode(encrypted_data.data.encode())
        return fernet.decrypt(ciphertext)
    
    async def _encrypt_chacha20_poly1305(self, plaintext: bytes, key: bytes, config: EncryptionConfig) -> EncryptedData:
        """Encrypt using ChaCha20-Poly1305"""
        nonce = secrets.token_bytes(12)  # ChaCha20 uses 12-byte nonce
        
        cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=self.backend)
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return EncryptedData(
            data=base64.b64encode(ciphertext).decode(),
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305.value,
            iv=base64.b64encode(nonce).decode()
        )
    
    async def _decrypt_chacha20_poly1305(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        ciphertext = base64.b64decode(encrypted_data.data.encode())
        nonce = base64.b64decode(encrypted_data.iv.encode())
        
        cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=self.backend)
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    # Hashing and HMAC
    async def hash_data(
        self, 
        data: Union[str, bytes], 
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        salt: Optional[bytes] = None
    ) -> Tuple[str, Optional[str]]:
        """Hash data using specified algorithm"""
        
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == HashAlgorithm.SHA256:
                if salt:
                    data = salt + data
                hash_value = hashlib.sha256(data).hexdigest()
            elif algorithm == HashAlgorithm.SHA512:
                if salt:
                    data = salt + data
                hash_value = hashlib.sha512(data).hexdigest()
            elif algorithm == HashAlgorithm.BLAKE2B:
                hash_value = hashlib.blake2b(data, salt=salt).hexdigest()
            elif algorithm == HashAlgorithm.BCRYPT:
                # Generate salt if not provided
                if salt is None:
                    salt = bcrypt.gensalt()
                hash_value = bcrypt.hashpw(data, salt).decode()
            else:
                raise EncryptionException(f"Unsupported hash algorithm: {algorithm}")
            
            salt_b64 = base64.b64encode(salt).decode() if salt else None
            
            return hash_value, salt_b64
            
        except Exception as e:
            logger.error(f"Hashing failed: {e}")
            raise EncryptionException(f"Hashing failed: {e}")
    
    async def verify_hash(
        self, 
        data: Union[str, bytes], 
        hash_value: str,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        salt: Optional[str] = None
    ) -> bool:
        """Verify data against hash"""
        
        try:
            if algorithm == HashAlgorithm.BCRYPT:
                # Convert to bytes if string
                if isinstance(data, str):
                    data = data.encode('utf-8')
                return bcrypt.checkpw(data, hash_value.encode())
            else:
                # For other algorithms, compute hash and compare
                salt_bytes = base64.b64decode(salt.encode()) if salt else None
                computed_hash, _ = await self.hash_data(data, algorithm, salt_bytes)
                return hmac.compare_digest(computed_hash, hash_value)
                
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    async def generate_hmac(
        self, 
        data: Union[str, bytes], 
        key: Union[str, bytes],
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> str:
        """Generate HMAC for data"""
        
        try:
            # Convert to bytes if needed
            if isinstance(data, str):
                data = data.encode('utf-8')
            if isinstance(key, str):
                key = key.encode('utf-8')
            
            if algorithm == HashAlgorithm.SHA256:
                mac = hmac.new(key, data, hashlib.sha256)
            elif algorithm == HashAlgorithm.SHA512:
                mac = hmac.new(key, data, hashlib.sha512)
            else:
                raise EncryptionException(f"Unsupported HMAC algorithm: {algorithm}")
            
            return mac.hexdigest()
            
        except Exception as e:
            logger.error(f"HMAC generation failed: {e}")
            raise EncryptionException(f"HMAC generation failed: {e}")
    
    async def verify_hmac(
        self, 
        data: Union[str, bytes], 
        key: Union[str, bytes],
        expected_hmac: str,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ) -> bool:
        """Verify HMAC for data"""
        
        try:
            computed_hmac = await self.generate_hmac(data, key, algorithm)
            return hmac.compare_digest(computed_hmac, expected_hmac)
            
        except Exception as e:
            logger.error(f"HMAC verification failed: {e}")
            return False
    
    # Digital Signatures
    async def sign_data(self, data: Union[str, bytes], key_id: str) -> str:
        """Sign data using private key"""
        
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Get private key
            if key_id not in self.asymmetric_keys:
                raise EncryptionException(f"Key pair not found: {key_id}")
            
            private_pem, _ = self.asymmetric_keys[key_id]
            private_key = serialization.load_pem_private_key(private_pem, password=None, backend=self.backend)
            
            # Sign data
            signature = private_key.sign(
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return base64.b64encode(signature).decode()
            
        except Exception as e:
            logger.error(f"Data signing failed: {e}")
            raise EncryptionException(f"Data signing failed: {e}")
    
    async def verify_signature(self, data: Union[str, bytes], signature: str, key_id: str) -> bool:
        """Verify signature using public key"""
        
        try:
            # Convert to bytes if string
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Get public key
            if key_id not in self.asymmetric_keys:
                raise EncryptionException(f"Key pair not found: {key_id}")
            
            _, public_pem = self.asymmetric_keys[key_id]
            public_key = serialization.load_pem_public_key(public_pem, backend=self.backend)
            
            # Verify signature
            signature_bytes = base64.b64decode(signature.encode())
            
            public_key.verify(
                signature_bytes,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    # Key Management
    async def rotate_key(self, key_id: str) -> str:
        """Rotate an encryption key"""
        
        if key_id not in self.key_info:
            raise EncryptionException(f"Key not found: {key_id}")
        
        key_info = self.key_info[key_id]
        
        # Generate new key ID
        new_key_id = f"{key_id}_rotated_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate new key based on type
        if key_info.key_type == "symmetric":
            await self.generate_symmetric_key(new_key_id, key_info.algorithm, key_info.key_size)
        else:
            await self.generate_asymmetric_keypair(new_key_id, key_info.algorithm)
        
        # Mark old key as inactive
        key_info.is_active = False
        
        logger.info(f"Rotated key {key_id} to {new_key_id}")
        return new_key_id
    
    async def delete_key(self, key_id: str) -> bool:
        """Delete an encryption key"""
        
        try:
            # Remove from storage
            if key_id in self.symmetric_keys:
                del self.symmetric_keys[key_id]
            if key_id in self.asymmetric_keys:
                del self.asymmetric_keys[key_id]
            if key_id in self.key_info:
                del self.key_info[key_id]
            
            logger.info(f"Deleted key: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Key deletion failed: {e}")
            return False
    
    async def list_keys(self) -> List[KeyInfo]:
        """List all encryption keys"""
        return list(self.key_info.values())
    
    async def get_key_info(self, key_id: str) -> Optional[KeyInfo]:
        """Get information about a specific key"""
        return self.key_info.get(key_id)
    
    # Utility methods
    async def secure_random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(length)
    
    async def secure_random_string(self, length: int, alphabet: Optional[str] = None) -> str:
        """Generate cryptographically secure random string"""
        if alphabet:
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        else:
            return secrets.token_urlsafe(length)[:length]
    
    async def get_encryption_stats(self) -> Dict[str, Any]:
        """Get encryption system statistics"""
        active_keys = sum(1 for key in self.key_info.values() if key.is_active)
        expired_keys = sum(
            1 for key in self.key_info.values() 
            if key.expires_at and key.expires_at < datetime.utcnow()
        )
        
        return {
            "total_keys": len(self.key_info),
            "active_keys": active_keys,
            "expired_keys": expired_keys,
            "symmetric_keys": len(self.symmetric_keys),
            "asymmetric_keys": len(self.asymmetric_keys),
            "algorithms_in_use": list(set(key.algorithm.value for key in self.key_info.values()))
        }


# Template usage example
def create_encryption_manager_example() -> None:
    """Example of how to create and use the encryption manager"""
    
    # Create encryption manager
    encryption_manager = {{encryption_name}}Manager(
        master_key="your-master-key",
        enable_key_rotation=True
    )
    
    return encryption_manager


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "encryption_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive encryption system with multiple algorithms and key management",
    "required_parameters": [
        "encryption_name",
        "encryption_description",
        "author_name",
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_algorithms",
        "key_storage_backend",
        "compliance_requirements"
    ],
    "dependencies": [
        "cryptography>=41.0.7",
        "bcrypt>=4.0.0",
        "pydantic>=2.5.0"
    ],
    "features": [
        "Multiple encryption algorithms (AES, RSA, ChaCha20, Fernet)",
        "Symmetric and asymmetric encryption",
        "Key derivation functions",
        "Digital signatures",
        "HMAC generation and verification",
        "Secure hashing",
        "Key management and rotation",
        "Performance monitoring",
        "Compliance-ready implementation"
    ]
}

# File has syntax issues - needs manual review