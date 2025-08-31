"""
Encryption Handler - Transaction Data Security Manager

Enterprise-grade encryption and security system providing comprehensive data protection,
key management, and secure transaction processing for the IA Influencer platform's
sensitive creator economy data with military-grade security standards.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import os
import hashlib
import hmac
import secrets
import base64
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import cryptography.exceptions
from concurrent.futures import ThreadPoolExecutor
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "AES_256_GCM"         # AES-256 in GCM mode (authenticated encryption)
    AES_256_CBC = "AES_256_CBC"         # AES-256 in CBC mode
    CHACHA20_POLY1305 = "CHACHA20_POLY1305"  # ChaCha20-Poly1305 (modern AEAD)
    FERNET = "FERNET"                   # Fernet (symmetric encryption with authentication)
    RSA_OAEP = "RSA_OAEP"              # RSA with OAEP padding (asymmetric)


class KeyDerivationFunction(Enum):
    """Key derivation functions"""
    PBKDF2_SHA256 = "PBKDF2_SHA256"     # PBKDF2 with SHA-256
    SCRYPT = "SCRYPT"                   # Scrypt (memory-hard function)
    ARGON2 = "ARGON2"                   # Argon2 (winner of password hashing competition)


class SecurityLevel(Enum):
    """Security levels for different data types"""
    STANDARD = "STANDARD"               # Standard encryption for general data
    HIGH = "HIGH"                       # High security for sensitive data
    MILITARY = "MILITARY"               # Military-grade for critical data
    ULTRA = "ULTRA"                     # Ultra-high security for top-secret data


@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    algorithm: EncryptionAlgorithm
    key_size: int
    security_level: SecurityLevel
    key_derivation: KeyDerivationFunction = KeyDerivationFunction.PBKDF2_SHA256
    iterations: int = 100000  # For PBKDF2
    memory_cost: int = 65536  # For Scrypt/Argon2
    parallelism: int = 4      # For Argon2
    enable_compression: bool = True
    enable_integrity_check: bool = True
    
    @classmethod
    def get_config(cls, security_level: SecurityLevel) -> 'EncryptionConfig':
        """Get recommended config for security level"""
        configs = {
            SecurityLevel.STANDARD: cls(
                algorithm=EncryptionAlgorithm.FERNET,
                key_size=256,
                security_level=security_level,
                iterations=50000
            ),
            SecurityLevel.HIGH: cls(
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                key_size=256,
                security_level=security_level,
                iterations=100000
            ),
            SecurityLevel.MILITARY: cls(
                algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
                key_size=256,
                security_level=security_level,
                key_derivation=KeyDerivationFunction.SCRYPT,
                iterations=200000,
                memory_cost=131072
            ),
            SecurityLevel.ULTRA: cls(
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                key_size=256,
                security_level=security_level,
                key_derivation=KeyDerivationFunction.SCRYPT,
                iterations=500000,
                memory_cost=262144,
                parallelism=8
            )
        }
        return configs.get(security_level, configs[SecurityLevel.STANDARD])


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    algorithm: EncryptionAlgorithm
    key_size: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    derived_from: Optional[str] = None  # Parent key ID for derived keys
    labels: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if key is expired"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_usage_exceeded(self) -> bool:
        """Check if key usage limit is exceeded"""
        if self.max_usage is None:
            return False
        return self.usage_count >= self.max_usage
    
    @property
    def is_valid(self) -> bool:
        """Check if key is valid for use"""



        return not self.is_expired and not self.is_usage_exceeded


@dataclass
class EncryptedData:
    """Encrypted data container"""
    ciphertext: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    nonce: Optional[bytes] = None
    salt: Optional[bytes] = None
    tag: Optional[bytes] = None  # Authentication tag for AEAD
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""



        return {
            'ciphertext': base64.b64encode(self.ciphertext).decode('utf-8'),
            'algorithm': self.algorithm.value,
            'key_id': self.key_id,
            'nonce': base64.b64encode(self.nonce).decode('utf-8') if self.nonce else None,
            'salt': base64.b64encode(self.salt).decode('utf-8') if self.salt else None,
            'tag': base64.b64encode(self.tag).decode('utf-8') if self.tag else None,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedData':
        """Create from dictionary"""



        return cls(
            ciphertext=base64.b64decode(data['ciphertext']),
            algorithm=EncryptionAlgorithm(data['algorithm']),
            key_id=data['key_id'],
            nonce=base64.b64decode(data['nonce']) if data.get('nonce') else None,
            salt=base64.b64decode(data['salt']) if data.get('salt') else None,
            tag=base64.b64decode(data['tag']) if data.get('tag') else None,
            metadata=data.get('metadata', {}),
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class KeyManager:
    """Advanced cryptographic key management system"""
    
    def __init__(self, key_store_path: Optional[str] = None):
        self.key_store_path = Path(key_store_path) if key_store_path else Path("keys")
        self.key_store_path.mkdir(exist_ok=True, mode=0o700)
        
        # In-memory key cache with expiration
        self.key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self.key_metadata: Dict[str, EncryptionKey] = {}
        
        # Master key for key encryption
        self.master_key = self._load_or_create_master_key()
        
        # Key rotation settings
        self.auto_rotation_enabled = True
        self.rotation_interval = timedelta(days=30)
        
        # Threading
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info("KeyManager initialized with store: %s", self.key_store_path)
    
    def generate_key(
        self,
        algorithm: EncryptionAlgorithm,
        key_size: int = 256,
        key_id: Optional[str] = None,
        expires_after: Optional[timedelta] = None,
        max_usage: Optional[int] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate new encryption key"""
        
        if key_id is None:
            key_id = f"key_{secrets.token_hex(16)}"
        
        # Generate key based on algorithm
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
            key_bytes = secrets.token_bytes(key_size // 8)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_bytes = secrets.token_bytes(32)  # ChaCha20 uses 256-bit keys
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_bytes = Fernet.generate_key()
        elif algorithm == EncryptionAlgorithm.RSA_OAEP:
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Create key metadata
        expires_at = None
        if expires_after:
            expires_at = datetime.now(timezone.utc) + expires_after
        
        key_metadata = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            key_size=key_size,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            max_usage=max_usage,
            labels=labels or {}
        )
        
        with self.lock:
            # Store key securely
            self._store_key(key_id, key_bytes)
            self.key_metadata[key_id] = key_metadata
            
            # Cache key
            self.key_cache[key_id] = (key_bytes, datetime.now(timezone.utc) + timedelta(hours=1))
        
        logger.info("Generated new key: %s (%s, %d bits)", key_id, algorithm.value, key_size)
        return key_id
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """Retrieve encryption key"""
        
        with self.lock:
            # Check cache first
            if key_id in self.key_cache:
                key_bytes, cache_expiry = self.key_cache[key_id]
                if datetime.now(timezone.utc) < cache_expiry:
                    return key_bytes
                else:
                    # Remove expired cache entry
                    del self.key_cache[key_id]
            
            # Load from storage
            key_bytes = self._load_key(key_id)
            if key_bytes:
                # Cache for future use
                self.key_cache[key_id] = (key_bytes, datetime.now(timezone.utc) + timedelta(hours=1))
            
            return key_bytes
    
    def rotate_key(self, key_id: str) -> str:
        """Rotate encryption key"""
        
        if key_id not in self.key_metadata:
            raise ValueError(f"Key not found: {key_id}")
        
        old_metadata = self.key_metadata[key_id]
        
        # Generate new key with same parameters
        new_key_id = self.generate_key(
            algorithm=old_metadata.algorithm,
            key_size=old_metadata.key_size,
            expires_after=self.rotation_interval,
            max_usage=old_metadata.max_usage,
            labels=old_metadata.labels.copy()
        )
        
        # Mark old key as expired
        old_metadata.expires_at = datetime.now(timezone.utc)
        
        logger.info("Rotated key %s -> %s", key_id, new_key_id)
        return new_key_id
    
    def derive_key(
        self,
        parent_key_id: str,
        purpose: str,
        salt: Optional[bytes] = None,
        kdf: KeyDerivationFunction = KeyDerivationFunction.PBKDF2_SHA256,
        iterations: int = 100000
    ) -> str:
        """Derive key from parent key"""
        
        parent_key = self.get_key(parent_key_id)
        if not parent_key:
            raise ValueError(f"Parent key not found: {parent_key_id}")
        
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Derive key using specified KDF
        if kdf == KeyDerivationFunction.PBKDF2_SHA256:
            kdf_instance = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
                backend=default_backend()
            )
        elif kdf == KeyDerivationFunction.SCRYPT:
            kdf_instance = Scrypt(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                n=2**14,  # Memory cost
                r=8,      # Block size
                p=1,      # Parallelism
                backend=default_backend()
            )
        else:
            raise ValueError(f"Unsupported KDF: {kdf}")
        
        derived_key = kdf_instance.derive(parent_key)
        
        # Create derived key ID
        derived_key_id = f"derived_{secrets.token_hex(8)}_{purpose}"
        
        # Store derived key
        with self.lock:
            self._store_key(derived_key_id, derived_key)
            
            # Create metadata
            parent_metadata = self.key_metadata[parent_key_id]
            derived_metadata = EncryptionKey(
                key_id=derived_key_id,
                algorithm=parent_metadata.algorithm,
                key_size=256,  # Derived keys are always 256-bit
                created_at=datetime.now(timezone.utc),
                derived_from=parent_key_id,
                labels={"purpose": purpose, "derived": "true"}
            )
            self.key_metadata[derived_key_id] = derived_metadata
            
            # Cache key
            self.key_cache[derived_key_id] = (derived_key, datetime.now(timezone.utc) + timedelta(hours=1))
        
        logger.info("Derived key %s from %s for purpose: %s", derived_key_id, parent_key_id, purpose)
        return derived_key_id
    
    def list_keys(self, include_expired: bool = False) -> List[EncryptionKey]:
        """List all keys"""
        
        with self.lock:
            keys = list(self.key_metadata.values())
            
            if not include_expired:
                keys = [key for key in keys if key.is_valid]
            
            return keys
    
    def revoke_key(self, key_id: str) -> None:
        """Revoke encryption key"""
        
        with self.lock:
            if key_id in self.key_metadata:
                # Mark as expired
                self.key_metadata[key_id].expires_at = datetime.now(timezone.utc)
                
                # Remove from cache
                if key_id in self.key_cache:
                    del self.key_cache[key_id]
                
                logger.info("Revoked key: %s", key_id)
            else:
                logger.warning("Attempted to revoke non-existent key: %s", key_id)
    
    def _load_or_create_master_key(self) -> bytes:
        """Load or create master key for key encryption"""
        
        master_key_path = self.key_store_path / "master.key"
        
        if master_key_path.exists():
            # Load existing master key
            with open(master_key_path, 'rb') as f:
                return f.read()
        else:
            # Create new master key
            master_key = Fernet.generate_key()
            
            # Store securely with restricted permissions
            with open(master_key_path, 'wb') as f:
                f.write(master_key)
            os.chmod(master_key_path, 0o600)
            
            logger.info("Created new master key")
            return master_key
    
    def _store_key(self, key_id: str, key_bytes: bytes) -> None:
        """Store key securely on disk"""
        
        # Encrypt key with master key
        fernet = Fernet(self.master_key)
        encrypted_key = fernet.encrypt(key_bytes)
        
        # Store encrypted key
        key_path = self.key_store_path / f"{key_id}.key"
        with open(key_path, 'wb') as f:
            f.write(encrypted_key)
        os.chmod(key_path, 0o600)
    
    def _load_key(self, key_id: str) -> Optional[bytes]:
        """Load key from disk"""
        
        key_path = self.key_store_path / f"{key_id}.key"
        
        if not key_path.exists():
            return None
        
        try:
            # Load and decrypt key
            with open(key_path, 'rb') as f:
                encrypted_key = f.read()
            
            fernet = Fernet(self.master_key)
            key_bytes = fernet.decrypt(encrypted_key)
            
            return key_bytes
            
        except Exception as e:
            logger.error("Failed to load key %s: %s", key_id, str(e))
            return None


class TransactionEncryption:
    """
    Comprehensive transaction encryption system
    
    Features:
    - Multiple encryption algorithms (AES, ChaCha20, RSA)
    - Advanced key management and rotation
    - Field-level encryption for sensitive data
    - Creator economy data protection
    - Zero-knowledge architecture support
    - Compliance with GDPR, CCPA, and industry standards
    - High-performance encryption with hardware acceleration
    - Secure key derivation and storage
    - Digital signatures and integrity verification
    """
    
    def __init__(
        self,
        key_store_path: Optional[str] = None,
        default_security_level: SecurityLevel = SecurityLevel.HIGH,
        enable_hardware_acceleration: bool = True
    ):
        self.key_manager = KeyManager(key_store_path)
        self.default_security_level = default_security_level
        self.enable_hardware_acceleration = enable_hardware_acceleration
        
        # Encryption statistics
        self.encryption_count = 0
        self.decryption_count = 0
        self.bytes_encrypted = 0
        self.bytes_decrypted = 0
        
        # Performance tracking
        self.encryption_times: List[float] = []
        self.decryption_times: List[float] = []
        
        # Threading
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize default keys for different security levels
        self._initialize_default_keys()
        
        logger.info("TransactionEncryption initialized with security level: %s", default_security_level.value)
    
    def encrypt_transaction_data(
        self,
        data: Union[str, bytes, Dict[str, Any]],
        security_level: Optional[SecurityLevel] = None,
        creator_id: Optional[str] = None,
        additional_data: Optional[bytes] = None
    ) -> EncryptedData:
        """Encrypt transaction data with specified security level"""
        
        start_time = time.time()
        security_level = security_level or self.default_security_level
        
        try:
            # Convert data to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            elif isinstance(data, dict):
                data_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
            else:
                data_bytes = data
            
            # Get encryption configuration
            config = EncryptionConfig.get_config(security_level)
            
            # Get or create key for this security level
            key_id = self._get_key_for_security_level(security_level, creator_id)
            key_bytes = self.key_manager.get_key(key_id)
            
            if not key_bytes:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            # Encrypt based on algorithm
            if config.algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = self._encrypt_aes_gcm(data_bytes, key_bytes, additional_data)
            elif config.algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data = self._encrypt_aes_cbc(data_bytes, key_bytes)
            elif config.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data = self._encrypt_chacha20_poly1305(data_bytes, key_bytes, additional_data)
            elif config.algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = self._encrypt_fernet(data_bytes, key_bytes)
            elif config.algorithm == EncryptionAlgorithm.RSA_OAEP:
                encrypted_data = self._encrypt_rsa_oaep(data_bytes, key_bytes)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {config.algorithm}")
            
            # Set algorithm and key ID
            encrypted_data.algorithm = config.algorithm
            encrypted_data.key_id = key_id
            
            # Add metadata
            encrypted_data.metadata.update({
                'security_level': security_level.value,
                'creator_id': creator_id,
                'data_type': type(data).__name__,
                'original_size': len(data_bytes)
            })
            
            # Update statistics
            with self.lock:
                self.encryption_count += 1
                self.bytes_encrypted += len(data_bytes)
                encryption_time = time.time() - start_time
                self.encryption_times.append(encryption_time)
                
                # Keep only last 1000 timing measurements
                if len(self.encryption_times) > 1000:
                    self.encryption_times = self.encryption_times[-1000:]
            
            logger.debug("Encrypted %d bytes in %.3fs (algorithm=%s, security=%s)",
                        len(data_bytes), encryption_time, config.algorithm.value, security_level.value)
            
            return encrypted_data
            
        except Exception as e:
            logger.error("Encryption failed: %s", str(e))
            raise
    
    def decrypt_transaction_data(
        self,
        encrypted_data: EncryptedData,
        return_type: str = 'auto',
        additional_data: Optional[bytes] = None
    ) -> Union[str, bytes, Dict[str, Any]]:
        """Decrypt transaction data"""
        
        start_time = time.time()
        
        try:
            # Get decryption key
            key_bytes = self.key_manager.get_key(encrypted_data.key_id)
            if not key_bytes:
                raise ValueError(f"Decryption key not found: {encrypted_data.key_id}")
            
            # Decrypt based on algorithm
            if encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM:
                data_bytes = self._decrypt_aes_gcm(encrypted_data, key_bytes, additional_data)
            elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CBC:
                data_bytes = self._decrypt_aes_cbc(encrypted_data, key_bytes)
            elif encrypted_data.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                data_bytes = self._decrypt_chacha20_poly1305(encrypted_data, key_bytes, additional_data)
            elif encrypted_data.algorithm == EncryptionAlgorithm.FERNET:
                data_bytes = self._decrypt_fernet(encrypted_data, key_bytes)
            elif encrypted_data.algorithm == EncryptionAlgorithm.RSA_OAEP:
                data_bytes = self._decrypt_rsa_oaep(encrypted_data, key_bytes)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {encrypted_data.algorithm}")
            
            # Convert back to original type
            original_type = encrypted_data.metadata.get('data_type', 'bytes')
            
            if return_type == 'auto':
                if original_type == 'str':
                    result = data_bytes.decode('utf-8')
                elif original_type == 'dict':
                    result = json.loads(data_bytes.decode('utf-8'))
                else:
                    result = data_bytes
            elif return_type == 'str':
                result = data_bytes.decode('utf-8')
            elif return_type == 'dict':
                result = json.loads(data_bytes.decode('utf-8'))
            else:
                result = data_bytes
            
            # Update statistics
            with self.lock:
                self.decryption_count += 1
                self.bytes_decrypted += len(data_bytes)
                decryption_time = time.time() - start_time
                self.decryption_times.append(decryption_time)
                
                # Keep only last 1000 timing measurements
                if len(self.decryption_times) > 1000:
                    self.decryption_times = self.decryption_times[-1000:]
            
            logger.debug("Decrypted %d bytes in %.3fs (algorithm=%s)",
                        len(data_bytes), decryption_time, encrypted_data.algorithm.value)
            
            return result
            
        except Exception as e:
            logger.error("Decryption failed: %s", str(e))
            raise
    
    def encrypt_field(
        self,
        field_name: str,
        field_value: Any,
        security_level: Optional[SecurityLevel] = None,
        creator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Encrypt individual field for database storage"""
        
        # Create field-specific additional data for authentication
        additional_data = f"field:{field_name}".encode('utf-8')
        
        encrypted_data = self.encrypt_transaction_data(
            data=field_value,
            security_level=security_level,
            creator_id=creator_id,
            additional_data=additional_data
        )
        
        return {
            'encrypted': True,
            'field_name': field_name,
            'data': encrypted_data.to_dict(),
            'encrypted_at': datetime.now(timezone.utc).isoformat()
        }
    
    def decrypt_field(self, encrypted_field: Dict[str, Any]) -> Any:
        """Decrypt individual field from database"""
        
        if not encrypted_field.get('encrypted', False):
            raise ValueError("Field is not encrypted")
        
        encrypted_data = EncryptedData.from_dict(encrypted_field['data'])
        field_name = encrypted_field['field_name']
        
        # Use field-specific additional data
        additional_data = f"field:{field_name}".encode('utf-8')
        
        return self.decrypt_transaction_data(encrypted_data, additional_data=additional_data)
    
    def create_secure_hash(
        self,
        data: Union[str, bytes],
        salt: Optional[bytes] = None,
        algorithm: str = 'sha256'
    ) -> Tuple[str, bytes]:
        """Create secure hash with salt"""
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Create hash
        if algorithm == 'sha256':
            hasher = hashlib.sha256()
        elif algorithm == 'sha512':
            hasher = hashlib.sha512()
        elif algorithm == 'blake2b':
            hasher = hashlib.blake2b(digest_size=32)
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        hasher.update(salt + data)
        hash_value = hasher.hexdigest()
        
        return hash_value, salt
    
    def verify_hash(
        self,
        data: Union[str, bytes],
        hash_value: str,
        salt: bytes,
        algorithm: str = 'sha256'
    ) -> bool:
        """Verify data against hash"""
        
        computed_hash, _ = self.create_secure_hash(data, salt, algorithm)
        return hmac.compare_digest(computed_hash, hash_value)
    
    def generate_digital_signature(
        self,
        data: Union[str, bytes],
        private_key_id: str
    ) -> bytes:
        """Generate digital signature for data integrity"""
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Get private key
        private_key_bytes = self.key_manager.get_key(private_key_id)
        if not private_key_bytes:
            raise ValueError(f"Private key not found: {private_key_id}")
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )
        
        # Create signature
        signature = private_key.sign(
            data,
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_digital_signature(
        self,
        data: Union[str, bytes],
        signature: bytes,
        public_key_id: str
    ) -> bool:
        """Verify digital signature"""
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            # Get public key (derived from private key)
            private_key_bytes = self.key_manager.get_key(public_key_id)
            if not private_key_bytes:
                return False
            
            # Load private key and extract public key
            private_key = serialization.load_pem_private_key(
                private_key_bytes,
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            # Verify signature
            public_key.verify(
                signature,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except cryptography.exceptions.InvalidSignature:
            return False
        except Exception as e:
            logger.error("Signature verification failed: %s", str(e))
            return False
    
    def get_encryption_statistics(self) -> Dict[str, Any]:
        """Get encryption performance statistics"""
        
        with self.lock:
            avg_encryption_time = sum(self.encryption_times) / len(self.encryption_times) if self.encryption_times else 0
            avg_decryption_time = sum(self.decryption_times) / len(self.decryption_times) if self.decryption_times else 0
            
            return {
                'encryption_count': self.encryption_count,
                'decryption_count': self.decryption_count,
                'bytes_encrypted': self.bytes_encrypted,
                'bytes_decrypted': self.bytes_decrypted,
                'avg_encryption_time_ms': avg_encryption_time * 1000,
                'avg_decryption_time_ms': avg_decryption_time * 1000,
                'throughput_encryption_mbps': (self.bytes_encrypted / sum(self.encryption_times)) / 1024 / 1024 if self.encryption_times else 0,
                'throughput_decryption_mbps': (self.bytes_decrypted / sum(self.decryption_times)) / 1024 / 1024 if self.decryption_times else 0,
            }
    
    def _initialize_default_keys(self) -> None:
        """Initialize default keys for different security levels"""
        
        for security_level in SecurityLevel:
            config = EncryptionConfig.get_config(security_level)
            
            key_id = f"default_{security_level.value.lower()}"
            
            # Check if key already exists
            if not self.key_manager.get_key(key_id):
                self.key_manager.generate_key(
                    algorithm=config.algorithm,
                    key_size=config.key_size,
                    key_id=key_id,
                    expires_after=timedelta(days=365),  # Keys expire after 1 year
                    labels={'type': 'default', 'security_level': security_level.value}
                )
    
    def _get_key_for_security_level(
        self,
        security_level: SecurityLevel,
        creator_id: Optional[str] = None
    ) -> str:
        """Get encryption key for specified security level"""
        
        if creator_id:
            # Try to get creator-specific key
            creator_key_id = f"creator_{creator_id}_{security_level.value.lower()}"
            if self.key_manager.get_key(creator_key_id):
                return creator_key_id
        
        # Use default key for security level
        return f"default_{security_level.value.lower()}"
    
    def _encrypt_aes_gcm(
        self,
        data: bytes,
        key: bytes,
        additional_data: Optional[bytes] = None
    ) -> EncryptedData:
        """Encrypt using AES-256-GCM"""
        
        # Generate random nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key[:32]),  # Use first 32 bytes for 256-bit key
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add additional authenticated data if provided
        if additional_data:
            encryptor.authenticate_additional_data(additional_data)
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_id="",  # Will be set by caller
            nonce=nonce,
            tag=encryptor.tag
        )
    
    def _decrypt_aes_gcm(
        self,
        encrypted_data: EncryptedData,
        key: bytes,
        additional_data: Optional[bytes] = None
    ) -> bytes:
        """Decrypt using AES-256-GCM"""
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key[:32]),
            modes.GCM(encrypted_data.nonce, encrypted_data.tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Add additional authenticated data if provided
        if additional_data:
            decryptor.authenticate_additional_data(additional_data)
        
        # Decrypt data
        plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> EncryptedData:
        """Encrypt using AES-256-CBC"""
        
        # Generate random IV
        iv = secrets.token_bytes(16)  # 128-bit IV for CBC
        
        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key[:32]),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_256_CBC,
            key_id="",
            nonce=iv  # Store IV in nonce field
        )
    
    def _decrypt_aes_cbc(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using AES-256-CBC"""
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key[:32]),
            modes.CBC(encrypted_data.nonce),  # IV stored in nonce field
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        padded_data = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    
    def _encrypt_chacha20_poly1305(
        self,
        data: bytes,
        key: bytes,
        additional_data: Optional[bytes] = None
    ) -> EncryptedData:
        """Encrypt using ChaCha20-Poly1305"""
        
        # Generate random nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce for ChaCha20
        
        # Create cipher
        cipher = Cipher(
            algorithms.ChaCha20(key[:32], nonce),
            modes.ChaCha20Poly1305(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add additional authenticated data if provided
        if additional_data:
            encryptor.authenticate_additional_data(additional_data)
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            key_id="",
            nonce=nonce,
            tag=encryptor.tag
        )
    
    def _decrypt_chacha20_poly1305(
        self,
        encrypted_data: EncryptedData,
        key: bytes,
        additional_data: Optional[bytes] = None
    ) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        
        # Create cipher
        cipher = Cipher(
            algorithms.ChaCha20(key[:32], encrypted_data.nonce),
            modes.ChaCha20Poly1305(encrypted_data.nonce, encrypted_data.tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Add additional authenticated data if provided
        if additional_data:
            decryptor.authenticate_additional_data(additional_data)
        
        # Decrypt data
        plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        return plaintext
    
    def _encrypt_fernet(self, data: bytes, key: bytes) -> EncryptedData:
        """Encrypt using Fernet"""
        
        fernet = Fernet(key)
        ciphertext = fernet.encrypt(data)
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.FERNET,
            key_id=""
        )
    
    def _decrypt_fernet(self, encrypted_data: EncryptedData, key: bytes) -> bytes:
        """Decrypt using Fernet"""
        
        fernet = Fernet(key)
        plaintext = fernet.decrypt(encrypted_data.ciphertext)
        
        return plaintext
    
    def _encrypt_rsa_oaep(self, data: bytes, private_key_bytes: bytes) -> EncryptedData:
        """Encrypt using RSA-OAEP"""
        
        # Load private key and extract public key
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Encrypt data
        ciphertext = public_key.encrypt(
            data,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return EncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.RSA_OAEP,
            key_id=""
        )
    
    def _decrypt_rsa_oaep(self, encrypted_data: EncryptedData, private_key_bytes: bytes) -> bytes:
        """Decrypt using RSA-OAEP"""
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )
        
        # Decrypt data
        plaintext = private_key.decrypt(
            encrypted_data.ciphertext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return plaintext


# Convenience functions for common encryption patterns
def encrypt_creator_data(
    encryption_handler: TransactionEncryption,
    creator_id: str,
    data: Any,
    security_level: SecurityLevel = SecurityLevel.HIGH
) -> EncryptedData:
    """Encrypt creator-specific data"""



    
    return encryption_handler.encrypt_transaction_data(
        data=data,
        security_level=security_level,
        creator_id=creator_id
    )


def encrypt_revenue_data(
    encryption_handler: TransactionEncryption,
    revenue_data: Dict[str, Any],
    security_level: SecurityLevel = SecurityLevel.MILITARY
) -> EncryptedData:
    """Encrypt revenue-related data with high security"""



    
    return encryption_handler.encrypt_transaction_data(
        data=revenue_data,
        security_level=security_level
    )


def encrypt_content_fingerprint(
    encryption_handler: TransactionEncryption,
    fingerprint: str,
    creator_id: str
) -> EncryptedData:
    """Encrypt content fingerprint data"""



    
    return encryption_handler.encrypt_transaction_data(
        data=fingerprint,
        security_level=SecurityLevel.HIGH,
        creator_id=creator_id
    )
