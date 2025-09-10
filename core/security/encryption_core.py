"""Ainflue Core Encryption - Enterprise Encryption Management
===========================================================

Core encryption management system providing advanced cryptographic operations,
key management, data protection, secure communication, and enterprise-grade
encryption services for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import secrets
import base64
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import bcrypt

logger = logging.getLogger(__name__)

class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"

class HashAlgorithm(str, Enum):
    """Hash algorithms"""
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"
    BCRYPT = "bcrypt"

class KeyType(str, Enum):
    """Cryptographic key types"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    SIGNING = "signing"
    VERIFICATION = "verification"

@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    id: str
    algorithm: EncryptionAlgorithm
    key_type: KeyType
    key_data: bytes
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    default_hash: HashAlgorithm = HashAlgorithm.SHA256
    key_rotation_interval: int = 86400 * 30  # 30 days
    max_key_usage: int = 1000000
    password_rounds: int = 12
    enable_key_caching: bool = True
    secure_delete: bool = True

@dataclass
class EncryptionMetrics:
    """Encryption performance metrics"""
    total_encryptions: int = 0
    total_decryptions: int = 0
    total_hash_operations: int = 0
    total_key_generations: int = 0
    avg_encryption_time: float = 0.0
    avg_decryption_time: float = 0.0
    failed_operations: int = 0
    last_error: Optional[str] = None

class EncryptionCore:
    """Enterprise encryption core management system"""
    
    def __init__(self, config: Optional[EncryptionConfig] = None):
        """Initialize encryption core"""
        self.config = config or EncryptionConfig()
        self.metrics = EncryptionMetrics()
        
        # Key storage
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_key: Optional[bytes] = None
        
        # Key derivation cache
        self.derived_keys_cache: Dict[str, bytes] = {}
        
        logger.info("🔐 Encryption Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize encryption system"""
        try:
            logger.info("🔌 Initializing encryption system...")
            
            # Generate or load master key
            await self._initialize_master_key()
            
            # Initialize default keys
            await self._initialize_default_keys()
            
            logger.info("✅ Encryption Core initialization completed")
            return True
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Encryption Core initialization failed: {e}")
            return False
    
    async def _initialize_master_key(self):
        """Initialize master key for key encryption"""
        try:
            # Generate new master key (in production, load from secure storage)
            self.master_key = Fernet.generate_key()
            
            logger.info("🔑 Master key initialized")
            
        except Exception as e:
            logger.error(f"❌ Master key initialization failed: {e}")
            raise
    
    async def _initialize_default_keys(self):
        """Initialize default encryption keys"""
        try:
            # Generate default symmetric key
            default_key = await self.generate_key(
                algorithm=self.config.default_algorithm,
                key_id="default_symmetric"
            )
            
            # Generate RSA key pair
            await self.generate_asymmetric_key_pair(
                algorithm=EncryptionAlgorithm.RSA_2048,
                key_id="default_rsa"
            )
            
            logger.info("✅ Default encryption keys generated")
            
        except Exception as e:
            logger.error(f"❌ Default key generation failed: {e}")
            raise
    
    async def generate_key(self, algorithm: EncryptionAlgorithm, 
                          key_id: str, expires_in: Optional[int] = None) -> str:
        """Generate encryption key"""
        start_time = time.time()
        
        try:
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
            
            # Create key object
            expires_at = time.time() + expires_in if expires_in else None
            
            encryption_key = EncryptionKey(
                id=key_id,
                algorithm=algorithm,
                key_type=KeyType.SYMMETRIC,
                key_data=key_data,
                expires_at=expires_at,
                max_usage=self.config.max_key_usage
            )
            
            # Store encrypted key
            encrypted_key_data = await self._encrypt_key(key_data)
            encryption_key.key_data = encrypted_key_data
            
            self.keys[key_id] = encryption_key
            
            self.metrics.total_key_generations += 1
            generation_time = time.time() - start_time
            
            logger.info(f"🔑 Generated {algorithm.value} key: {key_id} ({generation_time:.3f}s)")
            
            return key_id
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Key generation failed: {e}")
            raise
    
    async def generate_asymmetric_key_pair(self, algorithm: EncryptionAlgorithm, 
                                         key_id: str) -> Tuple[str, str]:
        """Generate asymmetric key pair"""
        start_time = time.time()
        
        try:
            if algorithm == EncryptionAlgorithm.RSA_2048:
                key_size = 2048
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                key_size = 4096
            else:
                raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
            
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
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
            
            # Store private key
            private_key_id = f"{key_id}_private"
            private_encryption_key = EncryptionKey(
                id=private_key_id,
                algorithm=algorithm,
                key_type=KeyType.ASYMMETRIC_PRIVATE,
                key_data=await self._encrypt_key(private_pem)
            )
            
            # Store public key
            public_key_id = f"{key_id}_public"
            public_encryption_key = EncryptionKey(
                id=public_key_id,
                algorithm=algorithm,
                key_type=KeyType.ASYMMETRIC_PUBLIC,
                key_data=public_pem  # Public keys don't need encryption
            )
            
            self.keys[private_key_id] = private_encryption_key
            self.keys[public_key_id] = public_encryption_key
            
            self.metrics.total_key_generations += 2
            generation_time = time.time() - start_time
            
            logger.info(f"🔑 Generated {algorithm.value} key pair: {key_id} ({generation_time:.3f}s)")
            
            return private_key_id, public_key_id
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Asymmetric key generation failed: {e}")
            raise
    
    async def encrypt(self, data: Union[str, bytes], key_id: str, 
                     associated_data: Optional[bytes] = None) -> bytes:
        """Encrypt data using specified key"""
        start_time = time.time()
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            key = await self._get_key(key_id)
            if not key:
                raise ValueError(f"Key not found: {key_id}")
            
            # Check key expiration and usage limits
            await self._validate_key_usage(key)
            
            encrypted_data = await self._encrypt_with_algorithm(data, key, associated_data)
            
            # Update metrics
            key.usage_count += 1
            self.metrics.total_encryptions += 1
            
            encryption_time = time.time() - start_time
            self._update_avg_time('encryption', encryption_time)
            
            logger.debug(f"🔒 Data encrypted with key {key_id} ({encryption_time:.3f}s)")
            
            return encrypted_data
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Encryption failed: {e}")
            raise
    
    async def decrypt(self, encrypted_data: bytes, key_id: str, 
                     associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt data using specified key"""
        start_time = time.time()
        
        try:
            key = await self._get_key(key_id)
            if not key:
                raise ValueError(f"Key not found: {key_id}")
            
            decrypted_data = await self._decrypt_with_algorithm(encrypted_data, key, associated_data)
            
            # Update metrics
            self.metrics.total_decryptions += 1
            
            decryption_time = time.time() - start_time
            self._update_avg_time('decryption', decryption_time)
            
            logger.debug(f"🔓 Data decrypted with key {key_id} ({decryption_time:.3f}s)")
            
            return decrypted_data
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Decryption failed: {e}")
            raise
    
    async def hash_data(self, data: Union[str, bytes], 
                       algorithm: HashAlgorithm = None, salt: Optional[bytes] = None) -> str:
        """Hash data using specified algorithm"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            algorithm = algorithm or self.config.default_hash
            
            if algorithm == HashAlgorithm.SHA256:
                hasher = hashlib.sha256()
                if salt:
                    hasher.update(salt)
                hasher.update(data)
                return hasher.hexdigest()
            
            elif algorithm == HashAlgorithm.SHA512:
                hasher = hashlib.sha512()
                if salt:
                    hasher.update(salt)
                hasher.update(data)
                return hasher.hexdigest()
            
            elif algorithm == HashAlgorithm.BLAKE2B:
                hasher = hashlib.blake2b()
                if salt:
                    hasher.update(salt)
                hasher.update(data)
                return hasher.hexdigest()
            
            elif algorithm == HashAlgorithm.BCRYPT:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                salt_rounds = self.config.password_rounds
                hashed = bcrypt.hashpw(data, bcrypt.gensalt(rounds=salt_rounds))
                return hashed.decode('utf-8')
            
            elif algorithm == HashAlgorithm.SCRYPT:
                salt = salt or secrets.token_bytes(32)
                kdf = Scrypt(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    n=2**14,
                    r=8,
                    p=1
                )
                key = kdf.derive(data)
                return base64.b64encode(salt + key).decode('utf-8')
            
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Hashing failed: {e}")
            raise
    
    async def verify_hash(self, data: Union[str, bytes], hash_value: str, 
                         algorithm: HashAlgorithm = None) -> bool:
        """Verify data against hash"""
        try:
            if algorithm == HashAlgorithm.BCRYPT:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                return bcrypt.checkpw(data, hash_value.encode('utf-8'))
            
            # For other algorithms, compute hash and compare
            computed_hash = await self.hash_data(data, algorithm)
            return hmac.compare_digest(computed_hash, hash_value)
            
        except Exception as e:
            logger.error(f"❌ Hash verification failed: {e}")
            return False
    
    async def _encrypt_with_algorithm(self, data: bytes, key: EncryptionKey, 
                                    associated_data: Optional[bytes] = None) -> bytes:
        """Encrypt data with specific algorithm"""
        key_data = await self._decrypt_key(key.key_data)
        
        if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
            iv = secrets.token_bytes(12)  # 96-bit IV for GCM
            cipher = Cipher(algorithms.AES(key_data), modes.GCM(iv))
            encryptor = cipher.encryptor()
            
            if associated_data:
                encryptor.authenticate_additional_data(associated_data)
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            return iv + encryptor.tag + ciphertext
        
        elif key.algorithm == EncryptionAlgorithm.FERNET:
            fernet = Fernet(key_data)
            return fernet.encrypt(data)
        
        elif key.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            if key.key_type == KeyType.ASYMMETRIC_PUBLIC:
                # Load public key
                public_key = serialization.load_pem_public_key(key_data)
                return public_key.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            else:
                raise ValueError("Cannot encrypt with private key")
        
        else:
            raise ValueError(f"Unsupported encryption algorithm: {key.algorithm}")
    
    async def _decrypt_with_algorithm(self, encrypted_data: bytes, key: EncryptionKey, 
                                    associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt data with specific algorithm"""
        key_data = await self._decrypt_key(key.key_data)
        
        if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            cipher = Cipher(algorithms.AES(key_data), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            
            if associated_data:
                decryptor.authenticate_additional_data(associated_data)
            
            return decryptor.update(ciphertext) + decryptor.finalize()
        
        elif key.algorithm == EncryptionAlgorithm.FERNET:
            fernet = Fernet(key_data)
            return fernet.decrypt(encrypted_data)
        
        elif key.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            if key.key_type == KeyType.ASYMMETRIC_PRIVATE:
                # Load private key
                private_key = serialization.load_pem_private_key(key_data, password=None)
                return private_key.decrypt(
                    encrypted_data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            else:
                raise ValueError("Cannot decrypt with public key")
        
        else:
            raise ValueError(f"Unsupported decryption algorithm: {key.algorithm}")
    
    async def _get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Get encryption key by ID"""
        return self.keys.get(key_id)
    
    async def _encrypt_key(self, key_data: bytes) -> bytes:
        """Encrypt key data with master key"""
        if not self.master_key:
            raise RuntimeError("Master key not initialized")
        
        fernet = Fernet(self.master_key)
        return fernet.encrypt(key_data)
    
    async def _decrypt_key(self, encrypted_key_data: bytes) -> bytes:
        """Decrypt key data with master key"""
        if not self.master_key:
            raise RuntimeError("Master key not initialized")
        
        fernet = Fernet(self.master_key)
        return fernet.decrypt(encrypted_key_data)
    
    async def _validate_key_usage(self, key: EncryptionKey):
        """Validate key expiration and usage limits"""
        current_time = time.time()
        
        # Check expiration
        if key.expires_at and current_time > key.expires_at:
            raise ValueError(f"Key {key.id} has expired")
        
        # Check usage limit
        if key.max_usage and key.usage_count >= key.max_usage:
            raise ValueError(f"Key {key.id} has reached usage limit")
    
    def _update_avg_time(self, operation: str, duration: float):
        """Update average operation time"""
        if operation == 'encryption':
            if self.metrics.total_encryptions > 0:
                self.metrics.avg_encryption_time = (
                    (self.metrics.avg_encryption_time * (self.metrics.total_encryptions - 1) + duration)
                    / self.metrics.total_encryptions
                )
        elif operation == 'decryption':
            if self.metrics.total_decryptions > 0:
                self.metrics.avg_decryption_time = (
                    (self.metrics.avg_decryption_time * (self.metrics.total_decryptions - 1) + duration)
                    / self.metrics.total_decryptions
                )
    
    async def rotate_keys(self):
        """Rotate encryption keys"""
        try:
            logger.info("🔄 Starting key rotation")
            
            current_time = time.time()
            keys_to_rotate = []
            
            for key_id, key in self.keys.items():
                # Check if key needs rotation
                age = current_time - key.created_at
                if age > self.config.key_rotation_interval:
                    keys_to_rotate.append(key_id)
            
            for key_id in keys_to_rotate:
                old_key = self.keys[key_id]
                
                # Generate new key with same algorithm
                new_key_id = f"{key_id}_rotated_{int(current_time)}"
                
                if old_key.key_type == KeyType.SYMMETRIC:
                    await self.generate_key(old_key.algorithm, new_key_id)
                elif old_key.key_type in [KeyType.ASYMMETRIC_PRIVATE, KeyType.ASYMMETRIC_PUBLIC]:
                    base_id = key_id.replace('_private', '').replace('_public', '')
                    await self.generate_asymmetric_key_pair(old_key.algorithm, new_key_id)
                
                logger.info(f"🔄 Rotated key: {key_id} -> {new_key_id}")
            
            logger.info(f"✅ Key rotation completed: {len(keys_to_rotate)} keys rotated")
            
        except Exception as e:
            logger.error(f"❌ Key rotation failed: {e}")
    
    async def health_check(self) -> bool:
        """Perform encryption health check"""
        try:
            # Test encryption/decryption
            test_data = b"health_check_test_data"
            
            # Test with default key
            if "default_symmetric" in self.keys:
                encrypted = await self.encrypt(test_data, "default_symmetric")
                decrypted = await self.decrypt(encrypted, "default_symmetric")
                
                if decrypted != test_data:
                    return False
            
            # Test hashing
            hash_result = await self.hash_data(test_data)
            if not hash_result:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Encryption health check failed: {e}")
            return False

# Global encryption instance
encryption_core = EncryptionCore()

# Convenience functions
async def encrypt_data(data: Union[str, bytes], key_id: str) -> bytes:
    """Encrypt data"""
    return await encryption_core.encrypt(data, key_id)

async def decrypt_data(encrypted_data: bytes, key_id: str) -> bytes:
    """Decrypt data"""
    return await encryption_core.decrypt(encrypted_data, key_id)

async def hash_password(password: str) -> str:
    """Hash password securely"""
    return await encryption_core.hash_data(password, HashAlgorithm.BCRYPT)

async def verify_password(password: str, hash_value: str) -> bool:
    """Verify password against hash"""
    return await encryption_core.verify_hash(password, hash_value, HashAlgorithm.BCRYPT)

# Module exports
__all__ = [
    "EncryptionCore", "EncryptionKey", "EncryptionConfig", "EncryptionMetrics",
    "EncryptionAlgorithm", "HashAlgorithm", "KeyType", "encryption_core",
    "encrypt_data", "decrypt_data", "hash_password", "verify_password"
]