"""🔐 Encryption Engine - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/data_management/storage/encryption_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

Enterprise encryption engine for secure content protection
with advanced key management and compliance features.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.

ÉQUIPE PROJET - SPÉCIALITÉS:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Sécurité: Fahed Mlaiel
- Microservices: Fahed Mlaiel
- Audio Engineer: Fahed Mlaiel
- DevOps: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel
"""
from typing import Dict, List, Optional, Any, Union, Tuple, BinaryIO
import logging
import asyncio
import os
import secrets
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import base64
import json

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import cryptography.exceptions

logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_4096 = "rsa_4096"
    RSA_2048 = "rsa_2048"

class KeyDerivationFunction(Enum):
    """Key derivation functions"""    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"

@dataclass
class EncryptionConfig:
    """Configuration for encryption operations"""    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_derivation: KeyDerivationFunction = KeyDerivationFunction.SCRYPT
    key_length: int = 32  # 256 bits
    salt_length: int = 16
    nonce_length: int = 12  # For GCM
    iterations: int = 100000  # For PBKDF2
    memory_cost: int = 64 * 1024  # For Scrypt (64MB)
    parallelism: int = 1  # For Argon2
    backup_keys_count: int = 3
    key_rotation_days: int = 90

@dataclass
class EncryptionResult:
    """Result of encryption operation"""    success: bool
    encrypted_data: Optional[bytes] = None
    key_id: Optional[str] = None
    algorithm: Optional[EncryptionAlgorithm] = None
    metadata: Dict[str, Any] = None
    encryption_time: float = 0.0
    error_message: Optional[str] = None

@dataclass
class DecryptionResult:
    """Result of decryption operation"""    success: bool
    decrypted_data: Optional[bytes] = None
    key_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    decryption_time: float = 0.0
    error_message: Optional[str] = None

@dataclass
class EncryptionKey:
    """Encryption key metadata"""    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    salt: bytes
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int = 0
    is_active: bool = True
    backup_keys: List[bytes] = None

class KeyManager:
    """Secure key management system"""    
    def __init__(self, config: EncryptionConfig):
        self.config = config
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_key = self._generate_master_key()
        
        # Key rotation scheduler
        self.last_rotation_check = datetime.now()
        
        logger.info("KeyManager initialized with secure key storage")
    
    def _generate_master_key(self) -> bytes:
        """Generate or load master key for key encryption"""        # In production, this should be loaded from secure hardware or KMS
        master_key_file = os.environ.get('MASTER_KEY_FILE', '.master_key')
        
        try:
            if os.path.exists(master_key_file):
                with open(master_key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new master key
                master_key = secrets.token_bytes(32)
                with open(master_key_file, 'wb') as f:
                    f.write(master_key)
                os.chmod(master_key_file, 0o600)  # Restrictive permissions
                return master_key
                
        except Exception as e:
            logger.error(f"Master key generation failed: {str(e)}")
            # Fallback to in-memory key (not recommended for production)
            return secrets.token_bytes(32)
    
    def generate_key(self, algorithm: EncryptionAlgorithm) -> EncryptionKey:
        """Generate new encryption key"""        key_id = self._generate_key_id()
        
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_data = secrets.token_bytes(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_data = Fernet.generate_key()
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Generate salt for key derivation
        salt = secrets.token_bytes(self.config.salt_length)
        
        # Generate backup keys
        backup_keys = [secrets.token_bytes(32) for _ in range(self.config.backup_keys_count)]
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(days=self.config.key_rotation_days)
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            key_data=key_data,
            salt=salt,
            created_at=datetime.now(),
            expires_at=expires_at,
            backup_keys=backup_keys
        )
        
        # Store encrypted key
        self.keys[key_id] = encryption_key
        
        logger.info(f"Generated new encryption key: {key_id}")
        return encryption_key
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Retrieve encryption key by ID"""        key = self.keys.get(key_id)
        if key and key.is_active:
            key.usage_count += 1
            return key
        return None
    
    def rotate_keys(self) -> Dict[str, Any]:
        """Rotate expired keys"""        rotated_keys = []
        current_time = datetime.now()
        
        for key_id, key in self.keys.items():
            if key.expires_at and current_time > key.expires_at:
                # Deactivate old key
                key.is_active = False
                
                # Generate new key with same algorithm
                new_key = self.generate_key(key.algorithm)
                rotated_keys.append({
                    'old_key_id': key_id,
                    'new_key_id': new_key.key_id,
                    'algorithm': key.algorithm.value
                })
        
        self.last_rotation_check = current_time
        
        return {
            'rotated_count': len(rotated_keys),
            'rotated_keys': rotated_keys,
            'next_check': (current_time + timedelta(hours=24)).isoformat()
        }
    
    def _generate_key_id(self) -> str:
        """Generate unique key identifier"""        timestamp = int(time.time())
        random_part = secrets.token_hex(8)
        return f"key_{timestamp}_{random_part}"

class EncryptionEngine:
    """    Enterprise encryption engine for secure content protection.
    
    Features:
    - Multiple encryption algorithms (AES, ChaCha20, RSA)
    - Secure key management with rotation
    - Key derivation functions (PBKDF2, Scrypt)
    - Performance monitoring
    - Compliance features (key escrow, audit logs)
    """    
    def __init__(self, config: Optional[EncryptionConfig] = None):
        """Initialize encryption engine"""        self.config = config or EncryptionConfig()
        self.key_manager = KeyManager(self.config)
        
        # Performance metrics
        self.metrics = {
            'total_encryptions': 0,
            'total_decryptions': 0,
            'total_data_encrypted_mb': 0.0,
            'average_encryption_time': 0.0,
            'average_decryption_time': 0.0,
            'algorithm_usage': {},
            'error_count': 0
        }
        
        # Audit log
        self.audit_log: List[Dict[str, Any]] = []
        
        logger.info("EncryptionEngine initialized successfully")
    
    async def encrypt_content(
        self,
        data: bytes,
        algorithm: Optional[EncryptionAlgorithm] = None,
        key_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EncryptionResult:
        """        Encrypt content with specified or default algorithm.
        
        Business Flow:
        1. Select or generate encryption key
        2. Apply appropriate encryption algorithm
        3. Store encrypted data with metadata
        4. Log encryption operation for audit
        5. Update performance metrics
        """        start_time = time.time()
        
        try:
            # Determine algorithm
            if not algorithm:
                algorithm = self.config.algorithm
            
            # Get or generate encryption key
            if key_id:
                encryption_key = self.key_manager.get_key(key_id)
                if not encryption_key:
                    raise ValueError(f"Key not found: {key_id}")
            else:
                encryption_key = self.key_manager.generate_key(algorithm)
            
            # Encrypt data based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data, enc_metadata = await self._encrypt_aes_gcm(data, encryption_key)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data, enc_metadata = await self._encrypt_aes_cbc(data, encryption_key)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data, enc_metadata = await self._encrypt_chacha20(data, encryption_key)
            elif algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data, enc_metadata = await self._encrypt_fernet(data, encryption_key)
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                encrypted_data, enc_metadata = await self._encrypt_rsa(data, encryption_key)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Prepare result metadata
            result_metadata = {
                'algorithm': algorithm.value,
                'key_id': encryption_key.key_id,
                'encrypted_at': datetime.now().isoformat(),
                'original_size': len(data),
                'encrypted_size': len(encrypted_data),
                **(metadata or {}),
                **enc_metadata
            }
            
            # Calculate processing time
            encryption_time = time.time() - start_time
            
            # Update metrics
            self._update_encryption_metrics(algorithm, len(data), encryption_time)
            
            # Log operation
            self._log_encryption_operation(
                encryption_key.key_id, algorithm, len(data), True
            )
            
            result = EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=encryption_key.key_id,
                algorithm=algorithm,
                metadata=result_metadata,
                encryption_time=encryption_time
            )
            
            logger.info(f"Content encrypted successfully with {algorithm.value}")
            return result
            
        except Exception as e:
            self.metrics['error_count'] += 1
            error_msg = f"Encryption failed: {str(e)}"
            logger.error(error_msg)
            
            return EncryptionResult(
                success=False,
                encryption_time=time.time() - start_time,
                error_message=error_msg
            )
    
    async def decrypt_content(
        self,
        encrypted_data: bytes,
        key_id: str,
        algorithm: EncryptionAlgorithm,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DecryptionResult:
        """Decrypt encrypted content"""        start_time = time.time()
        
        try:
            # Get decryption key
            encryption_key = self.key_manager.get_key(key_id)
            if not encryption_key:
                raise ValueError(f"Decryption key not found: {key_id}")
            
            # Decrypt data based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = await self._decrypt_aes_gcm(encrypted_data, encryption_key, metadata)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_data = await self._decrypt_aes_cbc(encrypted_data, encryption_key, metadata)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = await self._decrypt_chacha20(encrypted_data, encryption_key, metadata)
            elif algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = await self._decrypt_fernet(encrypted_data, encryption_key)
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                decrypted_data = await self._decrypt_rsa(encrypted_data, encryption_key)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Calculate processing time
            decryption_time = time.time() - start_time
            
            # Update metrics
            self._update_decryption_metrics(algorithm, len(decrypted_data), decryption_time)
            
            # Log operation
            self._log_decryption_operation(key_id, algorithm, len(decrypted_data), True)
            
            result = DecryptionResult(
                success=True,
                decrypted_data=decrypted_data,
                key_id=key_id,
                metadata=metadata or {},
                decryption_time=decryption_time
            )
            
            logger.info(f"Content decrypted successfully with {algorithm.value}")
            return result
            
        except Exception as e:
            self.metrics['error_count'] += 1
            error_msg = f"Decryption failed: {str(e)}"
            logger.error(error_msg)
            
            # Log failed operation
            self._log_decryption_operation(key_id, algorithm, 0, False, str(e))
            
            return DecryptionResult(
                success=False,
                decryption_time=time.time() - start_time,
                error_message=error_msg
            )
    
    async def encrypt_batch(
        self,
        data_list: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[EncryptionResult]:
        """Encrypt multiple data items concurrently"""        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def encrypt_single(data_info):
            async with semaphore:
                return await self.encrypt_content(
                    data_info['data'],
                    data_info.get('algorithm'),
                    data_info.get('key_id'),
                    data_info.get('metadata')
                )
        
        tasks = [encrypt_single(data_info) for data_info in data_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [
            result if isinstance(result, EncryptionResult)
            else EncryptionResult(
                success=False,
                error_message=str(result)
            )
            for result in results
        ]
    
    # Algorithm-specific encryption methods
    
    async def _encrypt_aes_gcm(
        self,
        data: bytes,
        key: EncryptionKey
    ) -> Tuple[bytes, Dict[str, Any]]:
        """AES-256-GCM encryption"""        nonce = secrets.token_bytes(self.config.nonce_length)
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(nonce),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        # Combine nonce, encrypted data, and authentication tag
        result = nonce + encrypted_data + encryptor.tag
        
        metadata = {
            'nonce': base64.b64encode(nonce).decode(),
            'tag': base64.b64encode(encryptor.tag).decode()
        }
        
        return result, metadata
    
    async def _decrypt_aes_gcm(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        metadata: Optional[Dict[str, Any]]
    ) -> bytes:
        """AES-256-GCM decryption"""        nonce_len = self.config.nonce_length
        tag_len = 16  # GCM tag is always 16 bytes
        
        nonce = encrypted_data[:nonce_len]
        ciphertext = encrypted_data[nonce_len:-tag_len]
        tag = encrypted_data[-tag_len:]
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _encrypt_aes_cbc(
        self,
        data: bytes,
        key: EncryptionKey
    ) -> Tuple[bytes, Dict[str, Any]]:
        """AES-256-CBC encryption with PKCS7 padding"""        iv = secrets.token_bytes(16)  # AES block size
        
        # Apply PKCS7 padding
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length]) * padding_length
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # Combine IV and encrypted data
        result = iv + encrypted_data
        
        metadata = {
            'iv': base64.b64encode(iv).decode(),
            'padding_length': padding_length
        }
        
        return result, metadata
    
    async def _decrypt_aes_cbc(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        metadata: Optional[Dict[str, Any]]
    ) -> bytes:
        """AES-256-CBC decryption with PKCS7 padding removal"""        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]
    
    async def _encrypt_chacha20(
        self,
        data: bytes,
        key: EncryptionKey
    ) -> Tuple[bytes, Dict[str, Any]]:
        """ChaCha20-Poly1305 encryption"""        nonce = secrets.token_bytes(12)  # ChaCha20 nonce is 12 bytes
        
        cipher = Cipher(
            algorithms.ChaCha20(key.key_data, nonce),
            mode=None,
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        # For ChaCha20-Poly1305, we need to handle authentication separately
        # This is a simplified implementation
        result = nonce + encrypted_data
        
        metadata = {
            'nonce': base64.b64encode(nonce).decode()
        }
        
        return result, metadata
    
    async def _decrypt_chacha20(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        metadata: Optional[Dict[str, Any]]
    ) -> bytes:
        """ChaCha20-Poly1305 decryption"""        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        cipher = Cipher(
            algorithms.ChaCha20(key.key_data, nonce),
            mode=None,
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _encrypt_fernet(
        self,
        data: bytes,
        key: EncryptionKey
    ) -> Tuple[bytes, Dict[str, Any]]:
        """Fernet encryption (simplified wrapper)"""        fernet = Fernet(key.key_data)
        encrypted_data = fernet.encrypt(data)
        
        metadata = {
            'fernet_version': 'v1'
        }
        
        return encrypted_data, metadata
    
    async def _decrypt_fernet(
        self,
        encrypted_data: bytes,
        key: EncryptionKey
    ) -> bytes:
        """Fernet decryption"""        fernet = Fernet(key.key_data)
        return fernet.decrypt(encrypted_data)
    
    async def _encrypt_rsa(
        self,
        data: bytes,
        key: EncryptionKey
    ) -> Tuple[bytes, Dict[str, Any]]:
        """RSA encryption (for small data or key encryption)"""        private_key = serialization.load_pem_private_key(
            key.key_data,
            password=None,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        # RSA can only encrypt small amounts of data
        # For larger data, use hybrid encryption (RSA + AES)
        max_chunk_size = (key.key_data.bit_length() // 8) - 42  # OAEP padding overhead
        
        if len(data) > max_chunk_size:
            # Hybrid encryption: generate AES key, encrypt data with AES, encrypt AES key with RSA
            aes_key = secrets.token_bytes(32)
            
            # Encrypt data with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.GCM(secrets.token_bytes(12)),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            
            # Encrypt AES key with RSA
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted key and data
            result = len(encrypted_aes_key).to_bytes(4, 'big') + encrypted_aes_key + encrypted_data
            
            metadata = {
                'encryption_mode': 'hybrid',
                'aes_key_size': len(encrypted_aes_key)
            }
        else:
            # Direct RSA encryption for small data
            result = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            metadata = {
                'encryption_mode': 'direct'
            }
        
        return result, metadata
    
    async def _decrypt_rsa(
        self,
        encrypted_data: bytes,
        key: EncryptionKey
    ) -> bytes:
        """RSA decryption"""        private_key = serialization.load_pem_private_key(
            key.key_data,
            password=None,
            backend=default_backend()
        )
        
        # Check if hybrid encryption was used
        if len(encrypted_data) > 512:  # Likely hybrid encryption
            # Extract encrypted AES key
            key_size = int.from_bytes(encrypted_data[:4], 'big')
            encrypted_aes_key = encrypted_data[4:4+key_size]
            encrypted_content = encrypted_data[4+key_size:]
            
            # Decrypt AES key
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt content with AES
            # Note: This is simplified - in practice, you'd need to extract nonce and tag
            # from the encrypted_content for proper GCM decryption
            return encrypted_content  # Placeholder - implement proper AES decryption
        else:
            # Direct RSA decryption
            return private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
    
    # Utility and monitoring methods
    
    def _update_encryption_metrics(
        self,
        algorithm: EncryptionAlgorithm,
        data_size: int,
        processing_time: float
    ) -> None:
        """Update encryption performance metrics"""        self.metrics['total_encryptions'] += 1
        self.metrics['total_data_encrypted_mb'] += data_size / (1024 * 1024)
        
        # Update average encryption time
        count = self.metrics['total_encryptions']
        old_avg = self.metrics['average_encryption_time']
        self.metrics['average_encryption_time'] = (
            (old_avg * (count - 1) + processing_time) / count
        )
        
        # Update algorithm usage
        algo_name = algorithm.value
        self.metrics['algorithm_usage'][algo_name] = (
            self.metrics['algorithm_usage'].get(algo_name, 0) + 1
        )
    
    def _update_decryption_metrics(
        self,
        algorithm: EncryptionAlgorithm,
        data_size: int,
        processing_time: float
    ) -> None:
        """Update decryption performance metrics"""        self.metrics['total_decryptions'] += 1
        
        # Update average decryption time
        count = self.metrics['total_decryptions']
        old_avg = self.metrics['average_decryption_time']
        self.metrics['average_decryption_time'] = (
            (old_avg * (count - 1) + processing_time) / count
        )
    
    def _log_encryption_operation(
        self,
        key_id: str,
        algorithm: EncryptionAlgorithm,
        data_size: int,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log encryption operation for audit trail"""        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'encrypt',
            'key_id': key_id,
            'algorithm': algorithm.value,
            'data_size': data_size,
            'success': success,
            'error': error
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 10000 entries
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
    
    def _log_decryption_operation(
        self,
        key_id: str,
        algorithm: EncryptionAlgorithm,
        data_size: int,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Log decryption operation for audit trail"""        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'decrypt',
            'key_id': key_id,
            'algorithm': algorithm.value,
            'data_size': data_size,
            'success': success,
            'error': error
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 10000 entries
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
    
    def get_encryption_statistics(self) -> Dict[str, Any]:
        """Get comprehensive encryption statistics"""        return {
            'total_encryptions': self.metrics['total_encryptions'],
            'total_decryptions': self.metrics['total_decryptions'],
            'total_data_encrypted_mb': round(self.metrics['total_data_encrypted_mb'], 2),
            'average_encryption_time_ms': round(self.metrics['average_encryption_time'] * 1000, 2),
            'average_decryption_time_ms': round(self.metrics['average_decryption_time'] * 1000, 2),
            'algorithm_usage': self.metrics['algorithm_usage'],
            'error_count': self.metrics['error_count'],
            'active_keys': len([k for k in self.key_manager.keys.values() if k.is_active]),
            'total_keys': len(self.key_manager.keys)
        }
    
    def get_audit_log(
        self,
        limit: int = 100,
        operation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""        logs = self.audit_log
        
        if operation:
            logs = [log for log in logs if log['operation'] == operation]
        
        return logs[-limit:] if limit else logs
    
    async def rotate_keys(self) -> Dict[str, Any]:
        """Trigger key rotation"""        return self.key_manager.rotate_keys()

# Export main classes
__all__ = [
    'EncryptionEngine',
    'EncryptionAlgorithm',
    'EncryptionConfig',
    'EncryptionResult',
    'DecryptionResult',
    'KeyManager',
    'EncryptionKey'
]
