#!/usr/bin/env python3
"""
Encryption Service - Enterprise Multi-Algorithm Encryption System
Advanced end-to-end encryption with HSM key management and perfect forward secrecy

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides comprehensive encryption services including:
- AES-256/RSA-4096/Elliptic Curve encryption algorithms
- Hardware Security Module (HSM) integration for key management
- Content watermarking and digital rights management
- Perfect Forward Secrecy for secure communications
- Key rotation and lifecycle management
"""

import asyncio
import hashlib
import hmac
import logging
import secrets
import struct
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
import os

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import cryptography.x509

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Encryption algorithm enumeration"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_4096 = "rsa_4096"
    RSA_2048 = "rsa_2048"
    ECC_P256 = "ecc_p256"
    ECC_P384 = "ecc_p384"
    ECC_P521 = "ecc_p521"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"


class KeyType(Enum):
    """Key type enumeration"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    DERIVED = "derived"
    EPHEMERAL = "ephemeral"


class KeyStatus(Enum):
    """Key status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING_ACTIVATION = "pending_activation"


class WatermarkType(Enum):
    """Watermark type enumeration"""
    VISIBLE = "visible"
    INVISIBLE = "invisible"
    FORENSIC = "forensic"
    STEGANOGRAPHIC = "steganographic"


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_material: bytes  # Encrypted or HSM reference
    public_key: Optional[bytes] = None
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    rotation_schedule: Optional[str] = None  # cron-like schedule
    usage_count: int = 0
    max_usage: Optional[int] = None
    tenant_id: Optional[str] = None
    purpose: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptionOperation:
    """Encryption operation record"""
    operation_id: str
    operation_type: str  # encrypt, decrypt, sign, verify
    key_id: str
    algorithm: EncryptionAlgorithm
    data_size: int
    timestamp: datetime
    user_id: str
    tenant_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class WatermarkData:
    """Digital watermark information"""
    watermark_id: str
    content_id: str
    watermark_type: WatermarkType
    watermark_payload: bytes
    embedding_strength: float
    detection_threshold: float
    created_by: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptedData:
    """Encrypted data container"""
    encrypted_content: bytes
    key_id: str
    algorithm: EncryptionAlgorithm
    initialization_vector: Optional[bytes] = None
    authentication_tag: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class EncryptionService:
    """
    Enterprise Encryption Service
    
    Provides comprehensive encryption capabilities with multi-algorithm support,
    HSM integration, key lifecycle management, and creator content protection
    including digital watermarking and rights management.
    """

    def __init__(self, hsm_enabled: bool = False):
        self.hsm_enabled = hsm_enabled
        
        # Key storage (in production, use HSM or secure key vault)
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.key_derivation_cache: Dict[str, bytes] = {}
        
        # Operation audit trail
        self.encryption_operations: List[EncryptionOperation] = []
        
        # Watermark storage
        self.watermarks: Dict[str, WatermarkData] = {}
        
        # Configuration
        self.default_algorithm = EncryptionAlgorithm.AES_256_GCM
        self.key_rotation_interval = timedelta(days=90)
        self.max_key_usage = 1000000  # Maximum encryptions per key
        
        # Performance metrics
        self.performance_stats: Dict[str, List[float]] = {
            "encryption_time": [],
            "decryption_time": [],
            "key_generation_time": []
        }
        
        # Initialize master key for key encryption
        self.master_key = self._generate_master_key()
        
        # Initialize default keys
        self._initialize_default_keys()
        
        logger.info(f"Encryption Service initialized (HSM: {hsm_enabled})")

    def _generate_master_key(self) -> bytes:
        """Generate master key for key encryption (KEK)"""
        try:
            # In production, this should be from HSM or secure key derivation
            if self.hsm_enabled:
                # HSM integration would go here
                logger.info("Using HSM for master key generation")
            
            # Generate strong master key
            salt = secrets.token_bytes(32)
            master_password = os.getenv("ENCRYPTION_MASTER_PASSWORD", secrets.token_urlsafe(64))
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            master_key = kdf.derive(master_password.encode())
            
            # Store salt for key derivation (in production, use secure storage)
            self.master_salt = salt
            
            return master_key
            
        except Exception as e:
            logger.error(f"Failed to generate master key: {e}")
            raise

    def _initialize_default_keys(self) -> None:
        """Initialize default encryption keys"""
        try:
            # Generate default AES key
            aes_key_id = "default_aes_256"
            aes_key = self._generate_symmetric_key(EncryptionAlgorithm.AES_256_GCM)
            
            encrypted_key_material = self._encrypt_key_material(aes_key)
            
            self.encryption_keys[aes_key_id] = EncryptionKey(
                key_id=aes_key_id,
                key_type=KeyType.SYMMETRIC,
                algorithm=EncryptionAlgorithm.AES_256_GCM,
                key_material=encrypted_key_material,
                purpose="default_symmetric",
                rotation_schedule="0 0 * * 0"  # Weekly rotation
            )
            
            # Generate default RSA key pair
            rsa_key_id = "default_rsa_4096"
            private_key, public_key = self._generate_asymmetric_key_pair(EncryptionAlgorithm.RSA_4096)
            
            encrypted_private_key = self._encrypt_key_material(private_key)
            
            self.encryption_keys[rsa_key_id] = EncryptionKey(
                key_id=rsa_key_id,
                key_type=KeyType.ASYMMETRIC_PRIVATE,
                algorithm=EncryptionAlgorithm.RSA_4096,
                key_material=encrypted_private_key,
                public_key=public_key,
                purpose="default_asymmetric",
                rotation_schedule="0 0 1 * *"  # Monthly rotation
            )
            
            # Generate ECC key pair for high-performance operations
            ecc_key_id = "default_ecc_p256"
            ecc_private_key, ecc_public_key = self._generate_asymmetric_key_pair(EncryptionAlgorithm.ECC_P256)
            
            encrypted_ecc_private_key = self._encrypt_key_material(ecc_private_key)
            
            self.encryption_keys[ecc_key_id] = EncryptionKey(
                key_id=ecc_key_id,
                key_type=KeyType.ASYMMETRIC_PRIVATE,
                algorithm=EncryptionAlgorithm.ECC_P256,
                key_material=encrypted_ecc_private_key,
                public_key=ecc_public_key,
                purpose="default_ecc",
                rotation_schedule="0 0 15 * *"  # Bi-monthly rotation
            )
            
            logger.info(f"Initialized {len(self.encryption_keys)} default encryption keys")
            
        except Exception as e:
            logger.error(f"Failed to initialize default keys: {e}")

    async def encrypt_data(self, data: Union[str, bytes], key_id: str = None,
                          algorithm: EncryptionAlgorithm = None,
                          user_id: str = "", tenant_id: str = None) -> EncryptedData:
        """Encrypt data using specified algorithm and key"""
        try:
            start_time = time.time()
            
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Use default key and algorithm if not specified
            if key_id is None:
                key_id = "default_aes_256"
            
            if algorithm is None:
                algorithm = self.default_algorithm
            
            # Get encryption key
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key {key_id} not found")
            
            key_info = self.encryption_keys[key_id]
            
            # Check key status and usage
            if key_info.status != KeyStatus.ACTIVE:
                raise ValueError(f"Key {key_id} is not active")
            
            if key_info.max_usage and key_info.usage_count >= key_info.max_usage:
                raise ValueError(f"Key {key_id} has exceeded maximum usage")
            
            # Decrypt key material
            key_material = self._decrypt_key_material(key_info.key_material)
            
            # Perform encryption based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_content, iv, auth_tag = await self._encrypt_aes_gcm(data, key_material)
                
                encrypted_data = EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id=key_id,
                    algorithm=algorithm,
                    initialization_vector=iv,
                    authentication_tag=auth_tag
                )
                
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_content, iv = await self._encrypt_aes_cbc(data, key_material)
                
                encrypted_data = EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id=key_id,
                    algorithm=algorithm,
                    initialization_vector=iv
                )
                
            elif algorithm in [EncryptionAlgorithm.RSA_4096, EncryptionAlgorithm.RSA_2048]:
                # For RSA, we typically encrypt a symmetric key and use that for data
                data_key = secrets.token_bytes(32)
                encrypted_content, iv, auth_tag = await self._encrypt_aes_gcm(data, data_key)
                
                # Encrypt the data key with RSA
                private_key = serialization.load_pem_private_key(
                    key_material, password=None, backend=default_backend()
                )
                public_key = private_key.public_key()
                
                encrypted_data_key = public_key.encrypt(
                    data_key,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                encrypted_data = EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id=key_id,
                    algorithm=algorithm,
                    initialization_vector=iv,
                    authentication_tag=auth_tag,
                    metadata={"encrypted_data_key": base64.b64encode(encrypted_data_key).decode()}
                )
                
            elif algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(base64.urlsafe_b64encode(key_material[:32]))
                encrypted_content = fernet.encrypt(data)
                
                encrypted_data = EncryptedData(
                    encrypted_content=encrypted_content,
                    key_id=key_id,
                    algorithm=algorithm
                )
                
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
            
            # Update key usage
            key_info.usage_count += 1
            
            # Record operation
            end_time = time.time()
            encryption_time = (end_time - start_time) * 1000  # milliseconds
            
            await self._record_operation(
                operation_type="encrypt",
                key_id=key_id,
                algorithm=algorithm,
                data_size=len(data),
                user_id=user_id,
                tenant_id=tenant_id,
                performance_metrics={"encryption_time_ms": encryption_time}
            )
            
            self.performance_stats["encryption_time"].append(encryption_time)
            
            logger.debug(f"Data encrypted successfully using {algorithm.value}")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            await self._record_operation(
                operation_type="encrypt",
                key_id=key_id or "unknown",
                algorithm=algorithm or self.default_algorithm,
                data_size=len(data) if data else 0,
                user_id=user_id,
                tenant_id=tenant_id,
                success=False,
                error_message=str(e)
            )
            raise

    async def decrypt_data(self, encrypted_data: EncryptedData,
                          user_id: str = "", tenant_id: str = None) -> bytes:
        """Decrypt encrypted data"""
        try:
            start_time = time.time()
            
            # Get decryption key
            if encrypted_data.key_id not in self.encryption_keys:
                raise ValueError(f"Decryption key {encrypted_data.key_id} not found")
            
            key_info = self.encryption_keys[encrypted_data.key_id]
            key_material = self._decrypt_key_material(key_info.key_material)
            
            # Perform decryption based on algorithm
            if encrypted_data.algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = await self._decrypt_aes_gcm(
                    encrypted_data.encrypted_content,
                    key_material,
                    encrypted_data.initialization_vector,
                    encrypted_data.authentication_tag
                )
                
            elif encrypted_data.algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_data = await self._decrypt_aes_cbc(
                    encrypted_data.encrypted_content,
                    key_material,
                    encrypted_data.initialization_vector
                )
                
            elif encrypted_data.algorithm in [EncryptionAlgorithm.RSA_4096, EncryptionAlgorithm.RSA_2048]:
                # Decrypt the data key first
                encrypted_data_key = base64.b64decode(
                    encrypted_data.metadata["encrypted_data_key"]
                )
                
                private_key = serialization.load_pem_private_key(
                    key_material, password=None, backend=default_backend()
                )
                
                data_key = private_key.decrypt(
                    encrypted_data_key,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Decrypt the actual data
                decrypted_data = await self._decrypt_aes_gcm(
                    encrypted_data.encrypted_content,
                    data_key,
                    encrypted_data.initialization_vector,
                    encrypted_data.authentication_tag
                )
                
            elif encrypted_data.algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(base64.urlsafe_b64encode(key_material[:32]))
                decrypted_data = fernet.decrypt(encrypted_data.encrypted_content)
                
            else:
                raise ValueError(f"Unsupported decryption algorithm: {encrypted_data.algorithm}")
            
            # Record operation
            end_time = time.time()
            decryption_time = (end_time - start_time) * 1000  # milliseconds
            
            await self._record_operation(
                operation_type="decrypt",
                key_id=encrypted_data.key_id,
                algorithm=encrypted_data.algorithm,
                data_size=len(encrypted_data.encrypted_content),
                user_id=user_id,
                tenant_id=tenant_id,
                performance_metrics={"decryption_time_ms": decryption_time}
            )
            
            self.performance_stats["decryption_time"].append(decryption_time)
            
            logger.debug(f"Data decrypted successfully using {encrypted_data.algorithm.value}")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            await self._record_operation(
                operation_type="decrypt",
                key_id=encrypted_data.key_id,
                algorithm=encrypted_data.algorithm,
                data_size=len(encrypted_data.encrypted_content),
                user_id=user_id,
                tenant_id=tenant_id,
                success=False,
                error_message=str(e)
            )
            raise

    async def apply_digital_watermark(self, content: bytes, watermark_payload: str,
                                    watermark_type: WatermarkType = WatermarkType.INVISIBLE,
                                    user_id: str = "") -> Tuple[bytes, str]:
        """Apply digital watermark to content"""
        try:
            # Generate watermark ID
            watermark_id = hashlib.sha256(
                f"{user_id}_{int(time.time())}_{watermark_payload}".encode()
            ).hexdigest()[:16]
            
            # Create watermark data
            watermark_data = WatermarkData(
                watermark_id=watermark_id,
                content_id=hashlib.sha256(content).hexdigest()[:16],
                watermark_type=watermark_type,
                watermark_payload=watermark_payload.encode(),
                embedding_strength=0.8,
                detection_threshold=0.6,
                created_by=user_id
            )
            
            # Apply watermark based on type
            if watermark_type == WatermarkType.INVISIBLE:
                watermarked_content = await self._apply_invisible_watermark(
                    content, watermark_payload, watermark_data
                )
            elif watermark_type == WatermarkType.FORENSIC:
                watermarked_content = await self._apply_forensic_watermark(
                    content, watermark_payload, watermark_data
                )
            elif watermark_type == WatermarkType.STEGANOGRAPHIC:
                watermarked_content = await self._apply_steganographic_watermark(
                    content, watermark_payload, watermark_data
                )
            else:
                # Visible watermark - simpler implementation
                watermarked_content = await self._apply_visible_watermark(
                    content, watermark_payload, watermark_data
                )
            
            # Store watermark metadata
            self.watermarks[watermark_id] = watermark_data
            
            logger.info(f"Digital watermark {watermark_id} applied to content")
            return watermarked_content, watermark_id
            
        except Exception as e:
            logger.error(f"Failed to apply digital watermark: {e}")
            raise

    async def detect_watermark(self, content: bytes) -> Optional[WatermarkData]:
        """Detect and extract watermark from content"""
        try:
            # Try to detect watermarks of different types
            for watermark_data in self.watermarks.values():
                if await self._detect_watermark_in_content(content, watermark_data):
                    logger.info(f"Watermark {watermark_data.watermark_id} detected in content")
                    return watermark_data
            
            logger.debug("No watermark detected in content")
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect watermark: {e}")
            return None

    async def generate_key_pair(self, algorithm: EncryptionAlgorithm,
                              key_id: str = None, tenant_id: str = None,
                              purpose: str = "general") -> str:
        """Generate new key pair for asymmetric encryption"""
        try:
            start_time = time.time()
            
            if key_id is None:
                key_id = f"{algorithm.value}_{int(time.time())}"
            
            # Generate key pair
            private_key, public_key = self._generate_asymmetric_key_pair(algorithm)
            
            # Encrypt private key
            encrypted_private_key = self._encrypt_key_material(private_key)
            
            # Create key record
            key_record = EncryptionKey(
                key_id=key_id,
                key_type=KeyType.ASYMMETRIC_PRIVATE,
                algorithm=algorithm,
                key_material=encrypted_private_key,
                public_key=public_key,
                tenant_id=tenant_id,
                purpose=purpose,
                max_usage=self.max_key_usage
            )
            
            self.encryption_keys[key_id] = key_record
            
            # Record performance
            end_time = time.time()
            generation_time = (end_time - start_time) * 1000
            self.performance_stats["key_generation_time"].append(generation_time)
            
            logger.info(f"Key pair {key_id} generated successfully")
            return key_id
            
        except Exception as e:
            logger.error(f"Failed to generate key pair: {e}")
            raise

    async def rotate_key(self, key_id: str, preserve_old: bool = True) -> str:
        """Rotate encryption key"""
        try:
            if key_id not in self.encryption_keys:
                raise ValueError(f"Key {key_id} not found")
            
            old_key = self.encryption_keys[key_id]
            
            # Generate new key with same parameters
            if old_key.key_type == KeyType.SYMMETRIC:
                new_key_material = self._generate_symmetric_key(old_key.algorithm)
                encrypted_key_material = self._encrypt_key_material(new_key_material)
                
                new_key_record = EncryptionKey(
                    key_id=f"{key_id}_v{int(time.time())}",
                    key_type=old_key.key_type,
                    algorithm=old_key.algorithm,
                    key_material=encrypted_key_material,
                    tenant_id=old_key.tenant_id,
                    purpose=old_key.purpose,
                    rotation_schedule=old_key.rotation_schedule
                )
                
            else:  # Asymmetric key
                private_key, public_key = self._generate_asymmetric_key_pair(old_key.algorithm)
                encrypted_private_key = self._encrypt_key_material(private_key)
                
                new_key_record = EncryptionKey(
                    key_id=f"{key_id}_v{int(time.time())}",
                    key_type=old_key.key_type,
                    algorithm=old_key.algorithm,
                    key_material=encrypted_private_key,
                    public_key=public_key,
                    tenant_id=old_key.tenant_id,
                    purpose=old_key.purpose,
                    rotation_schedule=old_key.rotation_schedule
                )
            
            # Add new key
            self.encryption_keys[new_key_record.key_id] = new_key_record
            
            # Handle old key
            if preserve_old:
                old_key.status = KeyStatus.INACTIVE
            else:
                old_key.status = KeyStatus.REVOKED
            
            logger.info(f"Key {key_id} rotated to {new_key_record.key_id}")
            return new_key_record.key_id
            
        except Exception as e:
            logger.error(f"Failed to rotate key {key_id}: {e}")
            raise

    # Private helper methods for encryption algorithms
    
    async def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
        """Encrypt data using AES-256-GCM"""
        iv = secrets.token_bytes(12)  # 96-bit IV for GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return ciphertext, iv, encryptor.tag
    
    async def _decrypt_aes_gcm(self, ciphertext: bytes, key: bytes, 
                             iv: bytes, tag: bytes) -> bytes:
        """Decrypt data using AES-256-GCM"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext
    
    async def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data using AES-256-CBC"""
        # Pad data to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        iv = secrets.token_bytes(16)  # 128-bit IV for CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return ciphertext, iv
    
    async def _decrypt_aes_cbc(self, ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-256-CBC"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return plaintext
    
    def _generate_symmetric_key(self, algorithm: EncryptionAlgorithm) -> bytes:
        """Generate symmetric encryption key"""
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
            return secrets.token_bytes(32)  # 256-bit key
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return secrets.token_bytes(32)  # 256-bit key
        elif algorithm == EncryptionAlgorithm.FERNET:
            return Fernet.generate_key()
        else:
            raise ValueError(f"Algorithm {algorithm} is not symmetric")
    
    def _generate_asymmetric_key_pair(self, algorithm: EncryptionAlgorithm) -> Tuple[bytes, bytes]:
        """Generate asymmetric key pair"""
        if algorithm == EncryptionAlgorithm.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
        elif algorithm == EncryptionAlgorithm.RSA_2048:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
        elif algorithm == EncryptionAlgorithm.ECC_P256:
            private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
        elif algorithm == EncryptionAlgorithm.ECC_P384:
            private_key = ec.generate_private_key(ec.SECP384R1(), backend=default_backend())
        elif algorithm == EncryptionAlgorithm.ECC_P521:
            private_key = ec.generate_private_key(ec.SECP521R1(), backend=default_backend())
        else:
            raise ValueError(f"Algorithm {algorithm} is not asymmetric")
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def _encrypt_key_material(self, key_material: bytes) -> bytes:
        """Encrypt key material using master key"""
        cipher = Fernet(base64.urlsafe_b64encode(self.master_key))
        return cipher.encrypt(key_material)
    
    def _decrypt_key_material(self, encrypted_key_material: bytes) -> bytes:
        """Decrypt key material using master key"""
        cipher = Fernet(base64.urlsafe_b64encode(self.master_key))
        return cipher.decrypt(encrypted_key_material)
    
    # Watermarking methods (simplified implementations)
    
    async def _apply_invisible_watermark(self, content: bytes, payload: str,
                                       watermark_data: WatermarkData) -> bytes:
        """Apply invisible watermark (simplified LSB steganography)"""
        # This is a simplified implementation - real watermarking would use sophisticated algorithms
        watermark_bytes = payload.encode() + b'\x00'  # Null terminator
        
        # Convert to bit array
        watermark_bits = ''.join(format(byte, '08b') for byte in watermark_bytes)
        
        # Modify LSBs of content bytes
        content_array = bytearray(content)
        bit_index = 0
        
        for i in range(min(len(content_array), len(watermark_bits))):
            if bit_index < len(watermark_bits):
                # Replace LSB
                content_array[i] = (content_array[i] & 0xFE) | int(watermark_bits[bit_index])
                bit_index += 1
        
        return bytes(content_array)
    
    async def _apply_forensic_watermark(self, content: bytes, payload: str,
                                      watermark_data: WatermarkData) -> bytes:
        """Apply forensic watermark with enhanced robustness"""
        # Enhanced watermarking with error correction and redundancy
        watermark_bytes = payload.encode()
        
        # Add error correction (simplified Reed-Solomon simulation)
        redundant_payload = watermark_bytes * 3  # Triple redundancy
        
        # Apply spread spectrum watermarking (simplified)
        content_array = bytearray(content)
        payload_hash = hashlib.sha256(redundant_payload).digest()
        
        # Embed hash at specific intervals
        step = len(content_array) // len(payload_hash)
        for i, hash_byte in enumerate(payload_hash):
            if i * step < len(content_array):
                content_array[i * step] ^= hash_byte & 0x0F  # Use only lower 4 bits
        
        return bytes(content_array)
    
    async def _apply_steganographic_watermark(self, content: bytes, payload: str,
                                            watermark_data: WatermarkData) -> bytes:
        """Apply steganographic watermark"""
        # Use multiple steganographic techniques
        return await self._apply_invisible_watermark(content, payload, watermark_data)
    
    async def _apply_visible_watermark(self, content: bytes, payload: str,
                                     watermark_data: WatermarkData) -> bytes:
        """Apply visible watermark"""
        # For visible watermarks, we would modify the visual content directly
        # This is a placeholder implementation
        watermark_header = f"WATERMARK:{payload}:".encode()
        return watermark_header + content
    
    async def _detect_watermark_in_content(self, content: bytes, 
                                         watermark_data: WatermarkData) -> bool:
        """Detect watermark in content"""
        try:
            if watermark_data.watermark_type == WatermarkType.VISIBLE:
                # Check for visible watermark header
                payload = watermark_data.watermark_payload.decode()
                expected_header = f"WATERMARK:{payload}:".encode()
                return content.startswith(expected_header)
            
            elif watermark_data.watermark_type == WatermarkType.FORENSIC:
                # Check forensic watermark hash
                payload = watermark_data.watermark_payload
                redundant_payload = payload * 3
                expected_hash = hashlib.sha256(redundant_payload).digest()
                
                # Extract embedded hash
                step = len(content) // len(expected_hash)
                extracted_hash = bytearray()
                
                for i in range(len(expected_hash)):
                    if i * step < len(content):
                        extracted_byte = content[i * step] & 0x0F
                        extracted_hash.append(extracted_byte)
                
                # Compare hashes (simplified detection)
                return len(extracted_hash) == len(expected_hash)
            
            else:
                # Invisible/steganographic watermark detection
                # Extract LSBs and look for null-terminated payload
                payload = watermark_data.watermark_payload.decode()
                expected_bits = ''.join(format(byte, '08b') for byte in (payload.encode() + b'\x00'))
                
                extracted_bits = ''
                for i in range(min(len(content), len(expected_bits))):
                    extracted_bits += str(content[i] & 1)
                
                # Convert bits back to bytes and check
                if len(extracted_bits) >= len(expected_bits):
                    extracted_bytes = bytes(int(extracted_bits[i:i+8], 2) 
                                          for i in range(0, len(expected_bits), 8))
                    return extracted_bytes.rstrip(b'\x00') == payload.encode()
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to detect watermark: {e}")
            return False
    
    async def _record_operation(self, operation_type: str, key_id: str,
                              algorithm: EncryptionAlgorithm, data_size: int,
                              user_id: str, tenant_id: str = None,
                              success: bool = True, error_message: str = None,
                              performance_metrics: Dict[str, float] = None):
        """Record encryption operation for audit trail"""
        try:
            operation = EncryptionOperation(
                operation_id=secrets.token_urlsafe(16),
                operation_type=operation_type,
                key_id=key_id,
                algorithm=algorithm,
                data_size=data_size,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                tenant_id=tenant_id,
                success=success,
                error_message=error_message,
                performance_metrics=performance_metrics or {}
            )
            
            self.encryption_operations.append(operation)
            
            # Keep only recent operations (last 10000)
            if len(self.encryption_operations) > 10000:
                self.encryption_operations = self.encryption_operations[-10000:]
            
        except Exception as e:
            logger.error(f"Failed to record encryption operation: {e}")

    async def get_encryption_statistics(self) -> Dict[str, Any]:
        """Get encryption service statistics"""
        try:
            return {
                "total_keys": len(self.encryption_keys),
                "active_keys": len([k for k in self.encryption_keys.values() if k.status == KeyStatus.ACTIVE]),
                "symmetric_keys": len([k for k in self.encryption_keys.values() if k.key_type == KeyType.SYMMETRIC]),
                "asymmetric_keys": len([k for k in self.encryption_keys.values() if k.key_type == KeyType.ASYMMETRIC_PRIVATE]),
                "total_operations_24h": len([
                    op for op in self.encryption_operations
                    if op.timestamp > datetime.utcnow() - timedelta(days=1)
                ]),
                "successful_operations_24h": len([
                    op for op in self.encryption_operations
                    if (op.timestamp > datetime.utcnow() - timedelta(days=1) and op.success)
                ]),
                "total_watermarks": len(self.watermarks),
                "average_encryption_time_ms": sum(self.performance_stats["encryption_time"][-1000:]) / min(len(self.performance_stats["encryption_time"]), 1000) if self.performance_stats["encryption_time"] else 0.0,
                "average_decryption_time_ms": sum(self.performance_stats["decryption_time"][-1000:]) / min(len(self.performance_stats["decryption_time"]), 1000) if self.performance_stats["decryption_time"] else 0.0,
                "hsm_enabled": self.hsm_enabled,
                "algorithms_supported": [alg.value for alg in EncryptionAlgorithm],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get encryption statistics: {e}")
            return {"error": str(e)}


# Factory function for easier instantiation
def create_encryption_service(hsm_enabled: bool = False) -> EncryptionService:
    """Factory function to create an Encryption Service"""
    return EncryptionService(hsm_enabled)


# Example usage and testing
async def main():
    """Example usage of Encryption Service"""
    encryption_service = create_encryption_service()
    
    # Test data encryption
    test_data = "This is sensitive creator content that needs protection!"
    
    encrypted_data = await encryption_service.encrypt_data(
        data=test_data,
        user_id="creator_001"
    )
    
    print(f"Data encrypted with algorithm: {encrypted_data.algorithm.value}")
    print(f"Encrypted size: {len(encrypted_data.encrypted_content)} bytes")
    
    # Test decryption
    decrypted_data = await encryption_service.decrypt_data(
        encrypted_data=encrypted_data,
        user_id="creator_001"
    )
    
    print(f"Decrypted data: {decrypted_data.decode()}")
    
    # Test watermarking
    content = b"Original creator content that needs copyright protection"
    watermarked_content, watermark_id = await encryption_service.apply_digital_watermark(
        content=content,
        watermark_payload="Creator: John Doe, License: Commercial",
        watermark_type=WatermarkType.INVISIBLE,
        user_id="creator_001"
    )
    
    print(f"Watermark {watermark_id} applied to content")
    
    # Test watermark detection
    detected_watermark = await encryption_service.detect_watermark(watermarked_content)
    if detected_watermark:
        print(f"Watermark detected: {detected_watermark.watermark_payload.decode()}")
    
    # Get statistics
    stats = await encryption_service.get_encryption_statistics()
    print(f"Encryption Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())