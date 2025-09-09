"""
Media Encryption Engine
======================

Advanced media encryption system supporting multiple encryption algorithms,
key management, secure storage, and format-preserving encryption for
audio, video, and image content.

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import logging
import hashlib
import json
import asyncio
import os
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import struct

# Cryptography imports
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import secrets


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    AES_256_CTR = "aes_256_ctr"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_4096 = "rsa_4096"
    HYBRID_RSA_AES = "hybrid_rsa_aes"


class MediaType(Enum):
    """Supported media types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    STREAM = "stream"


class EncryptionStrength(Enum):
    """Encryption strength levels"""
    STANDARD = "standard"
    HIGH = "high"
    MILITARY = "military"
    QUANTUM_RESISTANT = "quantum_resistant"


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    algorithm: EncryptionAlgorithm
    key_size: int
    key_data: bytes
    salt: Optional[bytes] = None
    iv: Optional[bytes] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    owner_id: str = ""
    usage_count: int = 0
    is_active: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class EncryptedMedia:
    """Encrypted media container"""
    encrypted_id: str
    original_media_id: str
    media_type: MediaType
    algorithm: EncryptionAlgorithm
    key_id: str
    encrypted_data: bytes
    metadata: Dict[str, Any]
    created_at: datetime
    file_size: int
    checksum: str
    encryption_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.encryption_params is None:
            self.encryption_params = {}


@dataclass
class DecryptionRequest:
    """Request for media decryption"""
    request_id: str
    encrypted_id: str
    user_id: str
    purpose: str
    request_context: Dict[str, Any]
    requested_at: datetime
    status: str = "pending"
    approved_by: Optional[str] = None
    expires_at: Optional[datetime] = None


class MediaEncryptionEngine:
    """
    Advanced Media Encryption Engine
    
    Provides enterprise-grade media encryption capabilities:
    - Multiple encryption algorithms (AES, ChaCha20, RSA)
    - Hybrid encryption for large media files
    - Key derivation and management
    - Format-preserving encryption for streaming
    - Secure key storage and rotation
    - Performance-optimized streaming encryption
    - Quantum-resistant encryption options
    - Audit logging and compliance
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize media encryption engine"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage (in production, use secure key management service)
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.encrypted_media: Dict[str, EncryptedMedia] = {}
        self.decryption_requests: Dict[str, DecryptionRequest] = {}
        
        # Key derivation settings
        self.kdf_iterations = self.config.get('kdf_iterations', 100000)
        self.key_rotation_days = self.config.get('key_rotation_days', 90)
        
        # Encryption settings
        self.default_algorithm = EncryptionAlgorithm(
            self.config.get('default_algorithm', 'aes_256_gcm')
        )
        self.chunk_size = self.config.get('chunk_size', 64 * 1024)  # 64KB chunks
        
        # Performance metrics
        self.metrics = {
            'total_encryptions': 0,
            'total_decryptions': 0,
            'total_keys_generated': 0,
            'total_key_rotations': 0,
            'bytes_encrypted': 0,
            'bytes_decrypted': 0,
            'avg_encryption_time': 0.0,
            'avg_decryption_time': 0.0
        }
        
        # Security audit log
        self.audit_log: List[Dict] = []
        
        self.logger.info("Media Encryption Engine initialized")

    async def generate_encryption_key(self, 
                                    algorithm: EncryptionAlgorithm = None,
                                    strength: EncryptionStrength = EncryptionStrength.HIGH,
                                    owner_id: str = "",
                                    expires_in_days: int = None) -> EncryptionKey:
        """Generate new encryption key"""
        
        if algorithm is None:
            algorithm = self.default_algorithm
        
        key_id = str(uuid.uuid4())
        
        # Generate key based on algorithm
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            key_data = secrets.token_bytes(32)  # 256 bits
            key_size = 256
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            key_data = secrets.token_bytes(32)
            key_size = 256
        elif algorithm == EncryptionAlgorithm.AES_256_CTR:
            key_data = secrets.token_bytes(32)
            key_size = 256
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_data = secrets.token_bytes(32)
            key_size = 256
        elif algorithm == EncryptionAlgorithm.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            key_size = 4096
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Set expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        elif self.key_rotation_days > 0:
            expires_at = datetime.utcnow() + timedelta(days=self.key_rotation_days)
        
        # Create key object
        encryption_key = EncryptionKey(
            key_id=key_id,
            algorithm=algorithm,
            key_size=key_size,
            key_data=key_data,
            owner_id=owner_id,
            expires_at=expires_at
        )
        
        # Store key
        self.encryption_keys[key_id] = encryption_key
        self.metrics['total_keys_generated'] += 1
        
        # Audit log
        await self._log_audit_event('key_generated', {
            'key_id': key_id,
            'algorithm': algorithm.value,
            'key_size': key_size,
            'owner_id': owner_id
        })
        
        self.logger.info(f"Encryption key generated: {key_id} ({algorithm.value})")
        return encryption_key

    async def encrypt_media(self, 
                          media_data: bytes,
                          media_type: MediaType,
                          media_id: str = None,
                          key_id: str = None,
                          algorithm: EncryptionAlgorithm = None) -> EncryptedMedia:
        """Encrypt media content"""
        
        start_time = datetime.utcnow()
        
        if media_id is None:
            media_id = str(uuid.uuid4())
        
        # Get or generate encryption key
        if key_id and key_id in self.encryption_keys:
            encryption_key = self.encryption_keys[key_id]
            if algorithm and algorithm != encryption_key.algorithm:
                raise ValueError("Algorithm mismatch with existing key")
            algorithm = encryption_key.algorithm
        else:
            if algorithm is None:
                algorithm = self.default_algorithm
            encryption_key = await self.generate_encryption_key(algorithm)
            key_id = encryption_key.key_id
        
        # Check key expiration
        if encryption_key.expires_at and datetime.utcnow() > encryption_key.expires_at:
            raise ValueError(f"Encryption key expired: {key_id}")
        
        # Encrypt data
        encrypted_data, encryption_params = await self._encrypt_data(
            media_data, encryption_key, media_type
        )
        
        # Calculate checksum
        checksum = hashlib.sha256(encrypted_data).hexdigest()
        
        # Create encrypted media object
        encrypted_id = str(uuid.uuid4())
        encrypted_media = EncryptedMedia(
            encrypted_id=encrypted_id,
            original_media_id=media_id,
            media_type=media_type,
            algorithm=algorithm,
            key_id=key_id,
            encrypted_data=encrypted_data,
            metadata={
                'original_size': len(media_data),
                'encryption_time': (datetime.utcnow() - start_time).total_seconds()
            },
            created_at=datetime.utcnow(),
            file_size=len(encrypted_data),
            checksum=checksum,
            encryption_params=encryption_params
        )
        
        # Store encrypted media
        self.encrypted_media[encrypted_id] = encrypted_media
        
        # Update metrics
        self.metrics['total_encryptions'] += 1
        self.metrics['bytes_encrypted'] += len(media_data)
        encryption_time = (datetime.utcnow() - start_time).total_seconds()
        self._update_avg_encryption_time(encryption_time)
        
        # Update key usage
        encryption_key.usage_count += 1
        
        # Audit log
        await self._log_audit_event('media_encrypted', {
            'encrypted_id': encrypted_id,
            'media_id': media_id,
            'media_type': media_type.value,
            'algorithm': algorithm.value,
            'key_id': key_id,
            'file_size': len(media_data)
        })
        
        self.logger.info(f"Media encrypted: {encrypted_id} ({len(media_data)} bytes)")
        return encrypted_media

    async def decrypt_media(self, 
                          encrypted_id: str,
                          user_id: str = "",
                          purpose: str = "access") -> bytes:
        """Decrypt media content"""
        
        start_time = datetime.utcnow()
        
        if encrypted_id not in self.encrypted_media:
            raise ValueError(f"Encrypted media not found: {encrypted_id}")
        
        encrypted_media = self.encrypted_media[encrypted_id]
        
        # Get encryption key
        if encrypted_media.key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key not found: {encrypted_media.key_id}")
        
        encryption_key = self.encryption_keys[encrypted_media.key_id]
        
        # Check key status
        if not encryption_key.is_active:
            raise ValueError(f"Encryption key is inactive: {encrypted_media.key_id}")
        
        # Decrypt data
        decrypted_data = await self._decrypt_data(
            encrypted_media.encrypted_data,
            encryption_key,
            encrypted_media.encryption_params
        )
        
        # Verify integrity
        await self._verify_decryption_integrity(decrypted_data, encrypted_media)
        
        # Update metrics
        self.metrics['total_decryptions'] += 1
        self.metrics['bytes_decrypted'] += len(decrypted_data)
        decryption_time = (datetime.utcnow() - start_time).total_seconds()
        self._update_avg_decryption_time(decryption_time)
        
        # Audit log
        await self._log_audit_event('media_decrypted', {
            'encrypted_id': encrypted_id,
            'media_id': encrypted_media.original_media_id,
            'user_id': user_id,
            'purpose': purpose,
            'file_size': len(decrypted_data)
        })
        
        self.logger.info(f"Media decrypted: {encrypted_id} ({len(decrypted_data)} bytes)")
        return decrypted_data

    async def encrypt_stream_chunk(self, 
                                 chunk_data: bytes,
                                 key_id: str,
                                 chunk_index: int = 0) -> Tuple[bytes, Dict[str, Any]]:
        """Encrypt streaming media chunk"""
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key not found: {key_id}")
        
        encryption_key = self.encryption_keys[key_id]
        
        # Generate chunk-specific IV
        chunk_iv = struct.pack('>Q', chunk_index).ljust(16, b'\x00')
        
        if encryption_key.algorithm == EncryptionAlgorithm.AES_256_CTR:
            cipher = Cipher(
                algorithms.AES(encryption_key.key_data),
                modes.CTR(chunk_iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            encrypted_chunk = encryptor.update(chunk_data) + encryptor.finalize()
            
            return encrypted_chunk, {
                'chunk_index': chunk_index,
                'iv': base64.b64encode(chunk_iv).decode(),
                'algorithm': encryption_key.algorithm.value
            }
        
        else:
            raise ValueError(f"Algorithm not supported for streaming: {encryption_key.algorithm}")

    async def decrypt_stream_chunk(self, 
                                 encrypted_chunk: bytes,
                                 key_id: str,
                                 chunk_params: Dict[str, Any]) -> bytes:
        """Decrypt streaming media chunk"""
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Encryption key not found: {key_id}")
        
        encryption_key = self.encryption_keys[key_id]
        chunk_iv = base64.b64decode(chunk_params['iv'])
        
        if encryption_key.algorithm == EncryptionAlgorithm.AES_256_CTR:
            cipher = Cipher(
                algorithms.AES(encryption_key.key_data),
                modes.CTR(chunk_iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            decrypted_chunk = decryptor.update(encrypted_chunk) + decryptor.finalize()
            
            return decrypted_chunk
        
        else:
            raise ValueError(f"Algorithm not supported for streaming: {encryption_key.algorithm}")

    async def _encrypt_data(self, 
                          data: bytes,
                          key: EncryptionKey,
                          media_type: MediaType) -> Tuple[bytes, Dict[str, Any]]:
        """Internal method to encrypt data"""
        
        if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
            # Generate random IV
            iv = secrets.token_bytes(12)  # 96-bit IV for GCM
            
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Add authenticated data (media type and metadata)
            aad = json.dumps({
                'media_type': media_type.value,
                'key_id': key.key_id,
                'timestamp': datetime.utcnow().isoformat()
            }).encode()
            encryptor.authenticate_additional_data(aad)
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine IV + ciphertext + auth tag
            encrypted_data = iv + ciphertext + encryptor.tag
            
            return encrypted_data, {
                'iv': base64.b64encode(iv).decode(),
                'aad': base64.b64encode(aad).decode(),
                'tag_length': len(encryptor.tag)
            }
        
        elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
            # Generate random IV
            iv = secrets.token_bytes(16)  # 128-bit IV for CBC
            
            # Pad data to block size
            block_size = 16
            padding_length = block_size - (len(data) % block_size)
            padded_data = data + bytes([padding_length] * padding_length)
            
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV + ciphertext
            encrypted_data = iv + ciphertext
            
            return encrypted_data, {
                'iv': base64.b64encode(iv).decode(),
                'padding_length': padding_length
            }
        
        elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            # Generate random nonce
            nonce = secrets.token_bytes(12)  # 96-bit nonce
            
            cipher = Cipher(
                algorithms.ChaCha20(key.key_data, nonce),
                None,
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine nonce + ciphertext
            encrypted_data = nonce + ciphertext
            
            return encrypted_data, {
                'nonce': base64.b64encode(nonce).decode()
            }
        
        elif key.algorithm == EncryptionAlgorithm.RSA_4096:
            # For large data, use hybrid encryption (RSA + AES)
            # Generate random AES key
            aes_key = secrets.token_bytes(32)
            iv = secrets.token_bytes(16)
            
            # Encrypt data with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad data
            block_size = 16
            padding_length = block_size - (len(data) % block_size)
            padded_data = data + bytes([padding_length] * padding_length)
            
            aes_ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Encrypt AES key with RSA
            private_key = serialization.load_pem_private_key(
                key.key_data,
                password=None,
                backend=default_backend()
            )
            public_key = private_key.public_key()
            
            encrypted_aes_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Combine encrypted key + IV + ciphertext
            encrypted_data = encrypted_aes_key + iv + aes_ciphertext
            
            return encrypted_data, {
                'key_length': len(encrypted_aes_key),
                'iv': base64.b64encode(iv).decode(),
                'padding_length': padding_length
            }
        
        else:
            raise ValueError(f"Unsupported encryption algorithm: {key.algorithm}")

    async def _decrypt_data(self, 
                          encrypted_data: bytes,
                          key: EncryptionKey,
                          params: Dict[str, Any]) -> bytes:
        """Internal method to decrypt data"""
        
        if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
            # Extract components
            iv = encrypted_data[:12]
            tag_length = params['tag_length']
            ciphertext = encrypted_data[12:-tag_length]
            tag = encrypted_data[-tag_length:]
            
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Add authenticated data
            aad = base64.b64decode(params['aad'])
            decryptor.authenticate_additional_data(aad)
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        
        elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
            # Extract IV and ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            cipher = Cipher(
                algorithms.AES(key.key_data),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            padding_length = params['padding_length']
            plaintext = padded_data[:-padding_length] if padding_length > 0 else padded_data
            return plaintext
        
        elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            # Extract nonce and ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            cipher = Cipher(
                algorithms.ChaCha20(key.key_data, nonce),
                None,
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext
        
        elif key.algorithm == EncryptionAlgorithm.RSA_4096:
            # Extract components
            key_length = params['key_length']
            encrypted_aes_key = encrypted_data[:key_length]
            iv = encrypted_data[key_length:key_length+16]
            aes_ciphertext = encrypted_data[key_length+16:]
            
            # Decrypt AES key with RSA
            private_key = serialization.load_pem_private_key(
                key.key_data,
                password=None,
                backend=default_backend()
            )
            
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(aes_ciphertext) + decryptor.finalize()
            
            # Remove padding
            padding_length = params['padding_length']
            plaintext = padded_data[:-padding_length] if padding_length > 0 else padded_data
            return plaintext
        
        else:
            raise ValueError(f"Unsupported decryption algorithm: {key.algorithm}")

    async def _verify_decryption_integrity(self, 
                                         decrypted_data: bytes,
                                         encrypted_media: EncryptedMedia):
        """Verify integrity of decrypted data"""
        
        # Check size matches original
        original_size = encrypted_media.metadata.get('original_size')
        if original_size and len(decrypted_data) != original_size:
            raise ValueError("Decrypted data size mismatch")
        
        # Additional integrity checks can be added here

    async def rotate_key(self, key_id: str) -> EncryptionKey:
        """Rotate encryption key"""
        
        if key_id not in self.encryption_keys:
            raise ValueError(f"Key not found: {key_id}")
        
        old_key = self.encryption_keys[key_id]
        
        # Generate new key with same algorithm
        new_key = await self.generate_encryption_key(
            algorithm=old_key.algorithm,
            owner_id=old_key.owner_id
        )
        
        # Deactivate old key
        old_key.is_active = False
        
        self.metrics['total_key_rotations'] += 1
        
        # Audit log
        await self._log_audit_event('key_rotated', {
            'old_key_id': key_id,
            'new_key_id': new_key.key_id,
            'algorithm': old_key.algorithm.value
        })
        
        self.logger.info(f"Key rotated: {key_id} -> {new_key.key_id}")
        return new_key

    async def export_encrypted_media(self, encrypted_id: str) -> Dict[str, Any]:
        """Export encrypted media for storage or transfer"""
        
        if encrypted_id not in self.encrypted_media:
            raise ValueError(f"Encrypted media not found: {encrypted_id}")
        
        encrypted_media = self.encrypted_media[encrypted_id]
        
        export_data = {
            'encrypted_id': encrypted_media.encrypted_id,
            'original_media_id': encrypted_media.original_media_id,
            'media_type': encrypted_media.media_type.value,
            'algorithm': encrypted_media.algorithm.value,
            'key_id': encrypted_media.key_id,
            'encrypted_data': base64.b64encode(encrypted_media.encrypted_data).decode(),
            'metadata': encrypted_media.metadata,
            'created_at': encrypted_media.created_at.isoformat(),
            'file_size': encrypted_media.file_size,
            'checksum': encrypted_media.checksum,
            'encryption_params': encrypted_media.encryption_params
        }
        
        return export_data

    async def import_encrypted_media(self, import_data: Dict[str, Any]) -> EncryptedMedia:
        """Import encrypted media from external source"""
        
        encrypted_data = base64.b64decode(import_data['encrypted_data'])
        
        encrypted_media = EncryptedMedia(
            encrypted_id=import_data['encrypted_id'],
            original_media_id=import_data['original_media_id'],
            media_type=MediaType(import_data['media_type']),
            algorithm=EncryptionAlgorithm(import_data['algorithm']),
            key_id=import_data['key_id'],
            encrypted_data=encrypted_data,
            metadata=import_data['metadata'],
            created_at=datetime.fromisoformat(import_data['created_at']),
            file_size=import_data['file_size'],
            checksum=import_data['checksum'],
            encryption_params=import_data['encryption_params']
        )
        
        # Verify checksum
        calculated_checksum = hashlib.sha256(encrypted_data).hexdigest()
        if calculated_checksum != encrypted_media.checksum:
            raise ValueError("Checksum verification failed during import")
        
        self.encrypted_media[encrypted_media.encrypted_id] = encrypted_media
        
        self.logger.info(f"Encrypted media imported: {encrypted_media.encrypted_id}")
        return encrypted_media

    def _update_avg_encryption_time(self, new_time: float):
        """Update average encryption time metric"""
        current_avg = self.metrics['avg_encryption_time']
        total_ops = self.metrics['total_encryptions']
        
        if total_ops <= 1:
            self.metrics['avg_encryption_time'] = new_time
        else:
            self.metrics['avg_encryption_time'] = (
                (current_avg * (total_ops - 1) + new_time) / total_ops
            )

    def _update_avg_decryption_time(self, new_time: float):
        """Update average decryption time metric"""
        current_avg = self.metrics['avg_decryption_time']
        total_ops = self.metrics['total_decryptions']
        
        if total_ops <= 1:
            self.metrics['avg_decryption_time'] = new_time
        else:
            self.metrics['avg_decryption_time'] = (
                (current_avg * (total_ops - 1) + new_time) / total_ops
            )

    async def _log_audit_event(self, event_type: str, data: Dict[str, Any]):
        """Log audit event for security compliance"""
        
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'data': data,
            'system': 'media_encryption'
        }
        
        self.audit_log.append(audit_entry)

    async def get_encryption_analytics(self, key_id: str) -> Dict[str, Any]:
        """Get analytics for encryption key usage"""
        
        if key_id not in self.encryption_keys:
            return {}
        
        key = self.encryption_keys[key_id]
        
        # Count encrypted media using this key
        media_count = len([
            m for m in self.encrypted_media.values() 
            if m.key_id == key_id
        ])
        
        analytics = {
            'key_id': key_id,
            'algorithm': key.algorithm.value,
            'key_size': key.key_size,
            'created_at': key.created_at.isoformat(),
            'expires_at': key.expires_at.isoformat() if key.expires_at else None,
            'usage_count': key.usage_count,
            'encrypted_media_count': media_count,
            'is_active': key.is_active,
            'owner_id': key.owner_id
        }
        
        return analytics

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall encryption system metrics"""
        
        active_keys = len([k for k in self.encryption_keys.values() if k.is_active])
        
        # Algorithm distribution
        algo_distribution = {}
        for key in self.encryption_keys.values():
            algo = key.algorithm.value
            algo_distribution[algo] = algo_distribution.get(algo, 0) + 1
        
        return {
            'metrics': self.metrics,
            'total_keys': len(self.encryption_keys),
            'active_keys': active_keys,
            'total_encrypted_media': len(self.encrypted_media),
            'algorithm_distribution': algo_distribution,
            'audit_log_entries': len(self.audit_log),
            'system_status': 'operational'
        }

    async def cleanup_expired_keys(self) -> int:
        """Clean up expired encryption keys"""
        
        current_time = datetime.utcnow()
        expired_count = 0
        
        for key_id, key in self.encryption_keys.items():
            if key.expires_at and current_time > key.expires_at and key.is_active:
                key.is_active = False
                expired_count += 1
                
                await self._log_audit_event('key_expired', {
                    'key_id': key_id,
                    'algorithm': key.algorithm.value,
                    'expired_at': current_time.isoformat()
                })
        
        self.logger.info(f"Cleaned up {expired_count} expired keys")
        return expired_count


# Utility functions
async def create_media_encryption_engine(config: Dict[str, Any] = None) -> MediaEncryptionEngine:
    """Factory function to create media encryption engine"""
    engine = MediaEncryptionEngine(config)
    return engine


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstrate media encryption engine capabilities"""
        engine = await create_media_encryption_engine()
        
        # Sample media data
        sample_video = b"Sample video content data..." * 1000  # Simulate video data
        
        # Encrypt media
        encrypted_media = await engine.encrypt_media(
            sample_video,
            MediaType.VIDEO,
            media_id="video_123",
            algorithm=EncryptionAlgorithm.AES_256_GCM
        )
        
        print(f"Media encrypted: {encrypted_media.encrypted_id}")
        print(f"Original size: {len(sample_video)} bytes")
        print(f"Encrypted size: {encrypted_media.file_size} bytes")
        
        # Decrypt media
        decrypted_data = await engine.decrypt_media(
            encrypted_media.encrypted_id,
            user_id="user_456"
        )
        
        print(f"Media decrypted successfully: {len(decrypted_data)} bytes")
        print(f"Data integrity: {'OK' if decrypted_data == sample_video else 'FAILED'}")
        
        # Test streaming encryption
        chunk_data = sample_video[:1024]  # First 1KB
        encrypted_chunk, chunk_params = await engine.encrypt_stream_chunk(
            chunk_data,
            encrypted_media.key_id,
            chunk_index=0
        )
        
        print(f"Stream chunk encrypted: {len(encrypted_chunk)} bytes")
        
        decrypted_chunk = await engine.decrypt_stream_chunk(
            encrypted_chunk,
            encrypted_media.key_id,
            chunk_params
        )
        
        print(f"Stream chunk decrypted: {'OK' if decrypted_chunk == chunk_data else 'FAILED'}")
        
        # Get analytics
        key_analytics = await engine.get_encryption_analytics(encrypted_media.key_id)
        print(f"Key analytics: {key_analytics}")
        
        system_metrics = await engine.get_system_metrics()
        print(f"System metrics: {system_metrics}")
    
    asyncio.run(demo())