"""Ainflue Core Encryption - Enterprise Encryption & Cryptography
============================================================

Advanced encryption management providing symmetric/asymmetric encryption,
digital signatures, key management, secure communication, and cryptographic
operations for the Ainflue platform security core.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import secrets
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet
    import cryptography
except ImportError:
    cryptography = None
    hashes = None
    serialization = None
    rsa = None
    ec = None
    padding = None
    Cipher = None
    algorithms = None
    modes = None
    PBKDF2HMAC = None
    HKDF = None
    default_backend = None
    Fernet = None

logger = logging.getLogger(__name__)

class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECC_P256 = "ecc_p256"
    ECC_P384 = "ecc_p384"

class HashAlgorithm(str, Enum):
    """Hash algorithms"""
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"

class KeyDerivation(str, Enum):
    """Key derivation functions"""
    PBKDF2 = "pbkdf2"
    HKDF = "hkdf"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"

@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    key_derivation: KeyDerivation = KeyDerivation.PBKDF2
    key_size: int = 32  # 256 bits
    iv_size: int = 16  # 128 bits
    salt_size: int = 32  # 256 bits
    iterations: int = 100000  # PBKDF2 iterations
    rsa_key_size: int = 2048
    key_rotation_interval: int = 86400  # 24 hours
    auto_key_rotation: bool = True
    secure_memory: bool = True

@dataclass
class KeyMetadata:
    """Encryption key metadata"""
    key_id: str
    algorithm: EncryptionAlgorithm
    created_at: float
    expires_at: Optional[float] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    purpose: str = "general"
    is_active: bool = True

@dataclass
class EncryptionMetrics:
    """Encryption performance metrics"""
    encryptions_performed: int = 0
    decryptions_performed: int = 0
    keys_generated: int = 0
    keys_rotated: int = 0
    failed_operations: int = 0
    avg_encryption_time: float = 0.0
    avg_decryption_time: float = 0.0
    bytes_encrypted: int = 0
    bytes_decrypted: int = 0
    last_health_check: float = field(default_factory=time.time)

class EncryptionCore:
    """Enterprise encryption core management system"""
    
    def __init__(self, config -> None: Optional[EncryptionConfig] = None, level -> None: str = "enterprise") -> None:
        """Initialize encryption core"""
        self.config = config or EncryptionConfig()
        self.level = level
        self.metrics = EncryptionMetrics()
        self.start_time = time.time()
        
        # Key management
        self.symmetric_keys: Dict[str, bytes] = {}
        self.asymmetric_keys: Dict[str, Dict[str, Any]] = {}
        self.key_metadata: Dict[str, KeyMetadata] = {}
        
        # Fernet instances for high-level encryption
        self.fernet_instances: Dict[str, Any] = {}
        
        # Security state
        self.master_key: Optional[bytes] = None
        self.is_initialized = False
        
        # Health monitoring
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("🔐 Encryption Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize encryption system"""
        try:
            logger.info("🚀 Initializing encryption core")
            
            if not cryptography:
                logger.warning("⚠️ Cryptography library not available, using basic encryption")
                self.is_initialized = True
                return True
            
            # Generate master key if not exists
            if not self.master_key:
                self.master_key = self._generate_secure_key(32)
            
            # Generate default encryption key
            await self.generate_key("default", EncryptionAlgorithm.AES_256_GCM)
            
            # Generate default RSA key pair
            await self.generate_asymmetric_key_pair("default_rsa", EncryptionAlgorithm.RSA_2048)
            
            self.is_initialized = True
            logger.info("✅ Encryption core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Encryption initialization failed: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start encryption core"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Start health monitoring
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            # Start key rotation if enabled
            if self.config.auto_key_rotation:
                asyncio.create_task(self._key_rotation_loop())
            
            logger.info("🚀 Encryption core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Encryption core start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop encryption core"""
        try:
            logger.info("🛑 Stopping encryption core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel health monitoring
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass
            
            # Clear sensitive data
            self._clear_sensitive_data()
            
            logger.info("✅ Encryption core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Encryption core stop failed: {str(e)}")
            return False
    
    def _generate_secure_key(self, key_size: int) -> bytes:
        """Generate cryptographically secure key"""
        return secrets.token_bytes(key_size)
    
    def _generate_salt(self) -> bytes:
        """Generate cryptographic salt"""
        return secrets.token_bytes(self.config.salt_size)
    
    def _generate_iv(self) -> bytes:
        """Generate initialization vector"""
        return secrets.token_bytes(self.config.iv_size)
    
    async def generate_key(self, key_id: str, algorithm: EncryptionAlgorithm) -> bool:
        """Generate symmetric encryption key"""
        try:
            if algorithm == EncryptionAlgorithm.FERNET:
                if Fernet:
                    key = Fernet.generate_key()
                    self.fernet_instances[key_id] = Fernet(key)
                    self.symmetric_keys[key_id] = key
                else:
                    key = self._generate_secure_key(32)
                    self.symmetric_keys[key_id] = key
            else:
                key = self._generate_secure_key(self.config.key_size)
                self.symmetric_keys[key_id] = key
            
            # Store metadata
            self.key_metadata[key_id] = KeyMetadata(
                key_id=key_id,
                algorithm=algorithm,
                created_at=time.time(),
                expires_at=time.time() + self.config.key_rotation_interval if self.config.auto_key_rotation else None
            )
            
            self.metrics.keys_generated += 1
            logger.info(f"🔑 Generated key '{key_id}' with algorithm {algorithm.value}")
            return True
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            return False
    
    async def generate_asymmetric_key_pair(self, key_id: str, algorithm: EncryptionAlgorithm) -> bool:
        """Generate asymmetric key pair"""
        try:
            if not cryptography:
                logger.warning("Cryptography not available for asymmetric keys")
                return False
            
            if algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=default_backend()
                )
                public_key = private_key.public_key()
                
            elif algorithm in [EncryptionAlgorithm.ECC_P256, EncryptionAlgorithm.ECC_P384]:
                curve = ec.SECP256R1() if algorithm == EncryptionAlgorithm.ECC_P256 else ec.SECP384R1()
                private_key = ec.generate_private_key(curve, default_backend())
                public_key = private_key.public_key()
            
            else:
                raise ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
            
            # Store keys
            self.asymmetric_keys[key_id] = {
                "private_key": private_key,
                "public_key": public_key,
                "algorithm": algorithm
            }
            
            # Store metadata
            self.key_metadata[f"{key_id}_asym"] = KeyMetadata(
                key_id=f"{key_id}_asym",
                algorithm=algorithm,
                created_at=time.time(),
                purpose="asymmetric"
            )
            
            self.metrics.keys_generated += 1
            logger.info(f"🔑 Generated asymmetric key pair '{key_id}' with algorithm {algorithm.value}")
            return True
            
        except Exception as e:
            logger.error(f"Asymmetric key generation failed: {str(e)}")
            return False
    
    async def encrypt(self, data: Union[str, bytes], key_id: str = "default") -> Optional[Dict[str, Any]]:
        """Encrypt data with specified key"""
        start_time = time.time()
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if key_id not in self.symmetric_keys:
                logger.error(f"Key '{key_id}' not found")
                return None
            
            key_meta = self.key_metadata.get(key_id)
            if not key_meta or not key_meta.is_active:
                logger.error(f"Key '{key_id}' is not active")
                return None
            
            algorithm = key_meta.algorithm
            
            if algorithm == EncryptionAlgorithm.FERNET and Fernet:
                fernet = self.fernet_instances.get(key_id)
                if fernet:
                    encrypted_data = fernet.encrypt(data)
                    result = {
                        "data": base64.b64encode(encrypted_data).decode('utf-8'),
                        "algorithm": algorithm.value,
                        "key_id": key_id
                    }
                else:
                    return None
            
            elif algorithm == EncryptionAlgorithm.AES_256_GCM and cryptography:
                iv = self._generate_iv()
                cipher = Cipher(algorithms.AES(self.symmetric_keys[key_id]), modes.GCM(iv), backend=default_backend())
                encryptor = cipher.encryptor()
                encrypted_data = encryptor.update(data) + encryptor.finalize()
                
                result = {
                    "data": base64.b64encode(encrypted_data).decode('utf-8'),
                    "iv": base64.b64encode(iv).decode('utf-8'),
                    "tag": base64.b64encode(encryptor.tag).decode('utf-8'),
                    "algorithm": algorithm.value,
                    "key_id": key_id
                }
            
            else:
                # Basic XOR encryption as fallback
                key = self.symmetric_keys[key_id]
                encrypted_data = bytes(a ^ b for a, b in zip(data, (key * (len(data) // len(key) + 1))[:len(data)]))
                result = {
                    "data": base64.b64encode(encrypted_data).decode('utf-8'),
                    "algorithm": "xor_fallback",
                    "key_id": key_id
                }
            
            # Update metrics
            self.metrics.encryptions_performed += 1
            self.metrics.bytes_encrypted += len(data)
            self._update_avg_time('encryption', start_time)
            
            # Update key usage
            key_meta.usage_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            self.metrics.failed_operations += 1
            return None
    
    async def decrypt(self, encrypted_data: Dict[str, Any]) -> Optional[bytes]:
        """Decrypt data"""
        start_time = time.time()
        
        try:
            key_id = encrypted_data.get("key_id", "default")
            algorithm = encrypted_data.get("algorithm")
            data = base64.b64decode(encrypted_data["data"])
            
            if key_id not in self.symmetric_keys:
                logger.error(f"Key '{key_id}' not found")
                return None
            
            if algorithm == "fernet" and Fernet:
                fernet = self.fernet_instances.get(key_id)
                if fernet:
                    decrypted_data = fernet.decrypt(data)
                else:
                    return None
            
            elif algorithm == "aes_256_gcm" and cryptography:
                iv = base64.b64decode(encrypted_data["iv"])
                tag = base64.b64decode(encrypted_data["tag"])
                cipher = Cipher(algorithms.AES(self.symmetric_keys[key_id]), modes.GCM(iv, tag), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_data = decryptor.update(data) + decryptor.finalize()
            
            else:
                # Basic XOR decryption as fallback
                key = self.symmetric_keys[key_id]
                decrypted_data = bytes(a ^ b for a, b in zip(data, (key * (len(data) // len(key) + 1))[:len(data)]))
            
            # Update metrics
            self.metrics.decryptions_performed += 1
            self.metrics.bytes_decrypted += len(decrypted_data)
            self._update_avg_time('decryption', start_time)
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            self.metrics.failed_operations += 1
            return None
    
    async def sign_data(self, data: Union[str, bytes], key_id: str = "default_rsa") -> Optional[str]:
        """Create digital signature"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if key_id not in self.asymmetric_keys:
                logger.error(f"Asymmetric key '{key_id}' not found")
                return None
            
            if not cryptography:
                logger.warning("Cryptography not available for signing")
                return None
            
            private_key = self.asymmetric_keys[key_id]["private_key"]
            
            if isinstance(private_key.private_numbers(), rsa.RSAPrivateNumbers):
                signature = private_key.sign(
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            else:  # ECC
                signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
            
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            return None
    
    async def verify_signature(self, data: Union[str, bytes], signature: str, key_id: str = "default_rsa") -> bool:
        """Verify digital signature"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if key_id not in self.asymmetric_keys:
                logger.error(f"Asymmetric key '{key_id}' not found")
                return False
            
            if not cryptography:
                logger.warning("Cryptography not available for verification")
                return False
            
            public_key = self.asymmetric_keys[key_id]["public_key"]
            signature_bytes = base64.b64decode(signature)
            
            if isinstance(public_key.public_numbers(), rsa.RSAPublicNumbers):
                public_key.verify(
                    signature_bytes,
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            else:  # ECC
                public_key.verify(signature_bytes, data, ec.ECDSA(hashes.SHA256()))
            
            return True
            
        except Exception as e:
            logger.debug(f"Signature verification failed: {str(e)}")
            return False
    
    def hash_data(self, data: Union[str, bytes], algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> str:
        """Hash data with specified algorithm"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA384:
            return hashlib.sha384(data).hexdigest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(data).hexdigest()
        elif algorithm == HashAlgorithm.BLAKE2B:
            return hashlib.blake2b(data).hexdigest()
        elif algorithm == HashAlgorithm.BLAKE2S:
            return hashlib.blake2s(data).hexdigest()
        else:
            return hashlib.sha256(data).hexdigest()
    
    def _update_avg_time(self, operation -> None: str, start_time -> None: float) -> None:
        """Update average operation time"""
        operation_time = time.time() - start_time
        
        if operation == 'encryption':
            total_ops = self.metrics.encryptions_performed
            self.metrics.avg_encryption_time = (
                (self.metrics.avg_encryption_time * (total_ops - 1) + operation_time) / total_ops
            )
        elif operation == 'decryption':
            total_ops = self.metrics.decryptions_performed
            self.metrics.avg_decryption_time = (
                (self.metrics.avg_decryption_time * (total_ops - 1) + operation_time) / total_ops
            )
    
    async def _key_rotation_loop(self) -> None:
        """Automatic key rotation loop"""
        while not self._shutdown_event.is_set():
            try:
                current_time = time.time()
                
                for key_id, metadata in list(self.key_metadata.items()):
                    if metadata.expires_at and current_time >= metadata.expires_at and metadata.is_active:
                        # Rotate key
                        await self.rotate_key(key_id)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Key rotation error: {str(e)}")
                await asyncio.sleep(3600)
    
    async def rotate_key(self, key_id: str) -> bool:
        """Rotate encryption key"""
        try:
            if key_id not in self.key_metadata:
                return False
            
            old_metadata = self.key_metadata[key_id]
            
            # Generate new key
            success = await self.generate_key(f"{key_id}_new", old_metadata.algorithm)
            if success:
                # Deactivate old key
                old_metadata.is_active = False
                
                # Rename new key to replace old one
                self.symmetric_keys[key_id] = self.symmetric_keys.pop(f"{key_id}_new")
                self.key_metadata[key_id] = self.key_metadata.pop(f"{key_id}_new")
                
                if key_id in self.fernet_instances:
                    self.fernet_instances[key_id] = self.fernet_instances.pop(f"{key_id}_new", None)
                
                self.metrics.keys_rotated += 1
                logger.info(f"🔄 Rotated key '{key_id}'")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            return False
    
    def _clear_sensitive_data(self) -> None:
        """Clear sensitive data from memory"""
        if self.config.secure_memory:
            self.symmetric_keys.clear()
            self.asymmetric_keys.clear()
            self.fernet_instances.clear()
            self.master_key = None
    
    async def health_check(self) -> bool:
        """Perform encryption health check"""
        try:
            # Test encryption/decryption
            test_data = "health_check_test"
            encrypted = await self.encrypt(test_data)
            if encrypted:
                decrypted = await self.decrypt(encrypted)
                if decrypted and decrypted.decode('utf-8') == test_data:
                    self.metrics.last_health_check = time.time()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Encryption health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Encryption health monitor error: {str(e)}")
                await asyncio.sleep(600)  # Wait longer on error
    
    def get_metrics(self) -> EncryptionMetrics:
        """Get current encryption metrics"""
        return self.metrics
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get encryption status summary"""
        return {
            "is_initialized": self.is_initialized,
            "active_keys": len([k for k, m in self.key_metadata.items() if m.is_active]),
            "total_keys": len(self.key_metadata),
            "asymmetric_keys": len(self.asymmetric_keys),
            "encryptions_performed": self.metrics.encryptions_performed,
            "decryptions_performed": self.metrics.decryptions_performed,
            "keys_generated": self.metrics.keys_generated,
            "keys_rotated": self.metrics.keys_rotated,
            "avg_encryption_time_ms": round(self.metrics.avg_encryption_time * 1000, 2),
            "avg_decryption_time_ms": round(self.metrics.avg_decryption_time * 1000, 2),
            "success_rate": (
                (self.metrics.encryptions_performed + self.metrics.decryptions_performed - self.metrics.failed_operations) /
                max(self.metrics.encryptions_performed + self.metrics.decryptions_performed, 1) * 100
            )
        }

# Module exports
__all__ = [
    "EncryptionCore", "EncryptionConfig", "EncryptionMetrics", "KeyMetadata",
    "EncryptionAlgorithm", "HashAlgorithm", "KeyDerivation"
]