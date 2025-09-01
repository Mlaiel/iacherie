"""Backup Encryption Service for IA Influencer Agent Platform.

Provides enterprise-grade encryption and decryption capabilities
for backup data with key management and security features.

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
from dataclasses import dataclass
from enum import Enum
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from ...security.key_management import KeyManager
from ...core.exceptions import EncryptionError


class EncryptionAlgorithm(Enum):
    """
Encryption algorithm enumeration."""

    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"


class KeyDerivationMethod(Enum):
    """Key derivation method enumeration."""

    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"


@dataclass
class EncryptionConfig:
    """Encryption configuration."""
    algorithm: EncryptionAlgorithm
    key_size: int
    key_derivation: KeyDerivationMethod
    iterations: int
    salt_size: int
    iv_size: int
    tag_size: int
    compression_enabled: bool
    integrity_verification: bool


@dataclass
class EncryptionMetadata:
    """
Encryption operation metadata."""
    algorithm: str
    key_id: str
    key_derivation_method: str
    iterations: int
    salt: bytes
    iv: bytes
    tag: Optional[bytes]
    checksum: str
    encrypted_at: datetime
    compressed: bool
    original_size: int
    encrypted_size: int


class BackupEncryption:
    """
    Enterprise backup encryption service with advanced security features.
    
    Provides symmetric and asymmetric encryption, key derivation,
    integrity verification, and secure key management.
    """
    def __init__(
        self,
        master_key: Optional[str] = None,
        key_manager: Optional[KeyManager] = None,
        config: Optional[EncryptionConfig] = None
    ):
        """
        Initialize backup encryption service.
        
        Args:
            master_key: Master encryption key
            key_manager: Key management service
            config: Encryption configuration
        """
        self.logger = logging.getLogger(__name__)
        self.master_key = master_key
        self.key_manager = key_manager or KeyManager()
        self.config = config or self._get_default_config()
        
        # Encryption state
        self.derived_keys: Dict[str, bytes] = {}
        self.key_cache_ttl = timedelta(hours=1)
        self.key_cache: Dict[str, Tuple[bytes, datetime]] = {}
        
        # Initialize encryption backend
        self.backend = default_backend()

    def is_enabled(self) -> bool:
        """
Check if encryption is enabled."""
        return self.master_key is not None

    async def encrypt_data(
        self,
        data: Union[bytes, str],
        key_id: Optional[str] = None,
        algorithm: Optional[EncryptionAlgorithm] = None
    ) -> bytes:
        """
        Encrypt data with specified or default configuration.
        
        Args:
            data: Data to encrypt
            key_id: Key identifier (optional)
            algorithm: Encryption algorithm (optional)
            
        Returns:
            Encrypted data with metadata
        """
        if not self.is_enabled():
            raise EncryptionError("Encryption not enabled - no master key provided")
        
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use provided algorithm or default
        algorithm = algorithm or self.config.algorithm
        key_id = key_id or "default"
        
        self.logger.info(f"Encrypting data with algorithm: {algorithm.value}")
        
        # Compress data if enabled
        original_size = len(data)
        if self.config.compression_enabled:
            data = await self._compress_data(data)
        
        # Generate encryption materials
        salt = secrets.token_bytes(self.config.salt_size)
        iv = secrets.token_bytes(self.config.iv_size)
        
        # Derive encryption key
        encryption_key = await self._derive_key(salt, key_id)
        
        # Perform encryption
        encrypted_data, tag = await self._encrypt_with_algorithm(
            data, encryption_key, iv, algorithm
        )
        
        # Calculate checksum
        checksum = hashlib.sha256(data).hexdigest()
        
        # Create metadata
        metadata = EncryptionMetadata(
            algorithm=algorithm.value,
            key_id=key_id,
            key_derivation_method=self.config.key_derivation.value,
            iterations=self.config.iterations,
            salt=salt,
            iv=iv,
            tag=tag,
            checksum=checksum,
            encrypted_at=datetime.now(),
            compressed=self.config.compression_enabled,
            original_size=original_size,
            encrypted_size=len(encrypted_data)
        )
        
        # Package encrypted data with metadata
        packaged_data = await self._package_encrypted_data(encrypted_data, metadata)
        
        self.logger.info(f"Data encrypted successfully: {original_size} -> {len(encrypted_data)} bytes")
        return packaged_data

    async def decrypt_data(
        self,
        encrypted_data: bytes,
        key_id: Optional[str] = None
    ) -> bytes:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted data with metadata
            key_id: Key identifier (optional)
            
        Returns:
            Decrypted data
        """
        if not self.is_enabled():
            raise EncryptionError("Encryption not enabled - no master key provided")
        
        self.logger.info("Decrypting data...")
        
        # Unpackage encrypted data and metadata
        data, metadata = await self._unpackage_encrypted_data(encrypted_data)
        
        # Use provided key_id or extract from metadata
        key_id = key_id or metadata.key_id
        
        # Derive decryption key
        decryption_key = await self._derive_key(metadata.salt, key_id)
        
        # Perform decryption
        algorithm = EncryptionAlgorithm(metadata.algorithm)
        decrypted_data = await self._decrypt_with_algorithm(
            data, decryption_key, metadata.iv, algorithm, metadata.tag
        )
        
        # Decompress if necessary
        if metadata.compressed:
            decrypted_data = await self._decompress_data(decrypted_data)
        
        # Verify integrity
        if self.config.integrity_verification:
            calculated_checksum = hashlib.sha256(decrypted_data).hexdigest()
            if calculated_checksum != metadata.checksum:
                raise EncryptionError("Data integrity verification failed")
        
        self.logger.info(f"Data decrypted successfully: {len(data)} -> {len(decrypted_data)} bytes")
        return decrypted_data

    async def generate_key_pair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair for asymmetric encryption.
        
        Args:
            key_size: RSA key size in bits
            
        Returns:
            Tuple of (private_key, public_key) in PEM format
        """
        self.logger.info(f"Generating RSA key pair: {key_size} bits")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=self.backend
        )
        
        # Extract public key
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem

    async def encrypt_with_public_key(
        self,
        data: bytes,
        public_key_pem: bytes
    ) -> bytes:
        """
        Encrypt data using RSA public key.
        
        Args:
            data: Data to encrypt
            public_key_pem: Public key in PEM format
            
        Returns:
            Encrypted data
        """
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=self.backend
        )
        
        # Encrypt data
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted

    async def decrypt_with_private_key(
        self,
        encrypted_data: bytes,
        private_key_pem: bytes
    ) -> bytes:
        """
        Decrypt data using RSA private key.
        
        Args:
            encrypted_data: Encrypted data
            private_key_pem: Private key in PEM format
            
        Returns:
            Decrypted data
        """
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=self.backend
        )
        
        # Decrypt data
        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted

    async def rotate_encryption_key(self, old_key_id: str, new_key_id: str) -> bool:
        """
        Rotate encryption key for existing encrypted data.
        
        Args:
            old_key_id: Current key identifier
            new_key_id: New key identifier
            
        Returns:
            Success status
        """
        try:
            self.logger.info(f"Rotating encryption key: {old_key_id} -> {new_key_id}")
            
            # Generate new key
            await self.key_manager.generate_key(new_key_id)
            
            # Mark old key for rotation
            await self.key_manager.mark_key_for_rotation(old_key_id, new_key_id)
            
            # Clear key cache
            self.key_cache.clear()
            
            self.logger.info(f"Key rotation completed: {old_key_id} -> {new_key_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {e}")
            return False

    async def get_encryption_statistics(self) -> Dict[str, Any]:
        """
        Get encryption statistics and metrics.
        
        Returns:
            Encryption statistics
        """
        return {
            "encryption_enabled": self.is_enabled(),
            "default_algorithm": self.config.algorithm.value,
            "key_derivation_method": self.config.key_derivation.value,
            "compression_enabled": self.config.compression_enabled,
            "integrity_verification": self.config.integrity_verification,
            "cached_keys": len(self.key_cache),
            "key_cache_ttl_hours": self.key_cache_ttl.total_seconds() / 3600,
            "supported_algorithms": [alg.value for alg in EncryptionAlgorithm],
            "key_sizes": {
                "aes": 256,
                "chacha20": 256,
                "rsa": [1024, 2048, 4096]
            }
        }

    async def verify_encryption_integrity(self, encrypted_data: bytes) -> bool:
        """
        Verify integrity of encrypted data without decryption.
        
        Args:
            encrypted_data: Encrypted data to verify
            
        Returns:
            Integrity status
        """
        try:
            # Unpackage to get metadata
            _, metadata = await self._unpackage_encrypted_data(encrypted_data)
            
            # Verify metadata completeness
            required_fields = ["algorithm", "key_id", "salt", "iv", "checksum"]
            for field in required_fields:
                if not hasattr(metadata, field) or getattr(metadata, field) is None:
                    return False
            
            # Verify algorithm support
            try:
                EncryptionAlgorithm(metadata.algorithm)
            except ValueError:
                return False
            
            # Additional integrity checks could be added here
            
            return True
            
        except Exception as e:
            self.logger.error(f"Integrity verification failed: {e}")
            return False

    async def _derive_key(self, salt: bytes, key_id: str) -> bytes:
        """Derive encryption key from master key and salt."""
        # Check cache first
        cache_key = f"{key_id}:{base64.b64encode(salt).decode()}"
        if cache_key in self.key_cache:
            key, cached_at = self.key_cache[cache_key]
            if datetime.now() - cached_at < self.key_cache_ttl:
                return key
        
        # Get master key material
        master_key_material = self.master_key.encode('utf-8')
        
        # Derive key using PBKDF2
        if self.config.key_derivation == KeyDerivationMethod.PBKDF2:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=salt,
                iterations=self.config.iterations,
                backend=self.backend
            )
            derived_key = kdf.derive(master_key_material)
        else:
            # Add support for other key derivation methods
            raise EncryptionError(f"Unsupported key derivation method: {self.config.key_derivation}")
        
        # Cache the derived key
        self.key_cache[cache_key] = (derived_key, datetime.now())
        
        return derived_key

    async def _encrypt_with_algorithm(
        self,
        data: bytes,
        key: bytes,
        iv: bytes,
        algorithm: EncryptionAlgorithm
    ) -> Tuple[bytes, Optional[bytes]]:
        """Encrypt data with specified algorithm."""
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            return await self._encrypt_aes_gcm(data, key, iv)
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            return await self._encrypt_aes_cbc(data, key, iv)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return await self._encrypt_chacha20(data, key, iv)
        elif algorithm == EncryptionAlgorithm.FERNET:
            return await self._encrypt_fernet(data, key)
        else:
            raise EncryptionError(f"Unsupported encryption algorithm: {algorithm}")

    async def _decrypt_with_algorithm(
        self,
        data: bytes,
        key: bytes,
        iv: bytes,
        algorithm: EncryptionAlgorithm,
        tag: Optional[bytes] = None
    ) -> bytes:
        """Decrypt data with specified algorithm."""
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            return await self._decrypt_aes_gcm(data, key, iv, tag)
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            return await self._decrypt_aes_cbc(data, key, iv)
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return await self._decrypt_chacha20(data, key, iv, tag)
        elif algorithm == EncryptionAlgorithm.FERNET:
            return await self._decrypt_fernet(data, key)
        else:
            raise EncryptionError(f"Unsupported encryption algorithm: {algorithm}")

    async def _encrypt_aes_gcm(self, data: bytes, key: bytes, iv: bytes) -> Tuple[bytes, bytes]:
        """Encrypt using AES-256-GCM."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return ciphertext, encryptor.tag

    async def _decrypt_aes_gcm(self, data: bytes, key: bytes, iv: bytes, tag: bytes) -> bytes:
        """
Decrypt using AES-256-GCM."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(data) + decryptor.finalize()

    async def _encrypt_aes_cbc(self, data: bytes, key: bytes, iv: bytes) -> Tuple[bytes, None]:
        """
Encrypt using AES-256-CBC."""
        # Pad data to block size
        from cryptography.hazmat.primitives import padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, None

    async def _decrypt_aes_cbc(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """
Decrypt using AES-256-CBC."""
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(data) + decryptor.finalize()
        
        # Unpad data
        from cryptography.hazmat.primitives import padding
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()

    async def _encrypt_chacha20(self, data: bytes, key: bytes, nonce: bytes) -> Tuple[bytes, bytes]:
        """
Encrypt using ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        chacha = ChaCha20Poly1305(key)
        # ChaCha20Poly1305 returns ciphertext with tag appended
        encrypted_with_tag = chacha.encrypt(nonce, data, None)
        
        # Split ciphertext and tag
        ciphertext = encrypted_with_tag[:-16]
        tag = encrypted_with_tag[-16:]
        
        return ciphertext, tag

    async def _decrypt_chacha20(self, data: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
        """
Decrypt using ChaCha20-Poly1305."""
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        chacha = ChaCha20Poly1305(key)
        # Reconstruct encrypted data with tag
        encrypted_with_tag = data + tag
        
        return chacha.decrypt(nonce, encrypted_with_tag, None)

    async def _encrypt_fernet(self, data: bytes, key: bytes) -> Tuple[bytes, None]:
        """
Encrypt using Fernet."""
        # Fernet requires base64-encoded key
        fernet_key = base64.urlsafe_b64encode(key)
        f = Fernet(fernet_key)
        
        encrypted = f.encrypt(data)
        return encrypted, None

    async def _decrypt_fernet(self, data: bytes, key: bytes) -> bytes:
        """
Decrypt using Fernet."""
        # Fernet requires base64-encoded key
        fernet_key = base64.urlsafe_b64encode(key)
        f = Fernet(fernet_key)
        
        return f.decrypt(data)

    async def _compress_data(self, data: bytes) -> bytes:
        """
Compress data using gzip."""
        import gzip
        return gzip.compress(data, compresslevel=6)

    async def _decompress_data(self, data: bytes) -> bytes:
        """
Decompress gzip-compressed data."""
        import gzip
        return gzip.decompress(data)

    async def _package_encrypted_data(
        self,
        encrypted_data: bytes,
        metadata: EncryptionMetadata
    ) -> bytes:
        """
Package encrypted data with metadata."""
        # Convert metadata to dict
        metadata_dict = {
            "algorithm": metadata.algorithm,
            "key_id": metadata.key_id,
            "key_derivation_method": metadata.key_derivation_method,
            "iterations": metadata.iterations,
            "salt": base64.b64encode(metadata.salt).decode(),
            "iv": base64.b64encode(metadata.iv).decode(),
            "tag": base64.b64encode(metadata.tag).decode() if metadata.tag else None,
            "checksum": metadata.checksum,
            "encrypted_at": metadata.encrypted_at.isoformat(),
            "compressed": metadata.compressed,
            "original_size": metadata.original_size,
            "encrypted_size": metadata.encrypted_size
        }
        
        # Serialize metadata
        metadata_json = json.dumps(metadata_dict).encode('utf-8')
        metadata_length = len(metadata_json)
        
        # Package: [metadata_length(4 bytes)][metadata][encrypted_data]
        package = (
            metadata_length.to_bytes(4, byteorder='big') +
            metadata_json +
            encrypted_data
        )
        
        return package

    async def _unpackage_encrypted_data(
        self,
        packaged_data: bytes
    ) -> Tuple[bytes, EncryptionMetadata]:
        """Unpackage encrypted data and extract metadata."""
        if len(packaged_data) < 4:
            raise EncryptionError("Invalid packaged data format")
        
        # Extract metadata length
        metadata_length = int.from_bytes(packaged_data[:4], byteorder='big')
        
        if len(packaged_data) < 4 + metadata_length:
            raise EncryptionError("Invalid packaged data format")
        
        # Extract metadata
        metadata_json = packaged_data[4:4+metadata_length]
        metadata_dict = json.loads(metadata_json.decode('utf-8'))
        
        # Extract encrypted data
        encrypted_data = packaged_data[4+metadata_length:]
        
        # Reconstruct metadata
        metadata = EncryptionMetadata(
            algorithm=metadata_dict["algorithm"],
            key_id=metadata_dict["key_id"],
            key_derivation_method=metadata_dict["key_derivation_method"],
            iterations=metadata_dict["iterations"],
            salt=base64.b64decode(metadata_dict["salt"]),
            iv=base64.b64decode(metadata_dict["iv"]),
            tag=base64.b64decode(metadata_dict["tag"]) if metadata_dict["tag"] else None,
            checksum=metadata_dict["checksum"],
            encrypted_at=datetime.fromisoformat(metadata_dict["encrypted_at"]),
            compressed=metadata_dict["compressed"],
            original_size=metadata_dict["original_size"],
            encrypted_size=metadata_dict["encrypted_size"]
        )
        
        return encrypted_data, metadata

    def _get_default_config(self) -> EncryptionConfig:
        """Get default encryption configuration."""
        return EncryptionConfig(
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_size=32,  # 256 bits
            key_derivation=KeyDerivationMethod.PBKDF2,
            iterations=100000,
            salt_size=16,
            iv_size=16,
            tag_size=16,
            compression_enabled=True,
            integrity_verification=True
        )
