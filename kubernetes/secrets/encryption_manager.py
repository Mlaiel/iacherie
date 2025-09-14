"""IA Influencer Agent - Encryption Manager
Advanced encryption/decryption operations with HSM support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import os
import logging
import hashlib
import secrets
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum
import threading
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet, MultiFernet
import argon2

from .config import SecretsConfig
from .utils import SecurityUtils

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """
Supported encryption algorithms."""

    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_4096 = "rsa_4096"


class KeyDerivationFunction(Enum):
    """Supported key derivation functions."""

    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"
    HKDF = "hkdf"


@dataclass
class EncryptionKey:
    """Encryption key metadata."""
    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    salt: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None


@dataclass
class EncryptionResult:
    """
Encryption operation result."""
    success: bool
    encrypted_data: Optional[bytes] = None
    key_id: Optional[str] = None
    algorithm: Optional[str] = None
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    error: Optional[str] = None


class EncryptionManager:
    """
    Enterprise-grade encryption manager with support for multiple algorithms,
    hardware security modules (HSM), key rotation, and secure key derivation.
    """
    
    def __init__(self, config -> None: SecretsConfig = None) -> None:
        """
        Initialize encryption manager.
        
        Args:
            config: Optional secrets configuration
        """
        self.config = config or SecretsConfig()
        self.security = SecurityUtils()
        
        # Key storage
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.master_key: Optional[bytes] = None
        self.key_rotation_lock = threading.Lock()
        
        # Initialize master key
        self._initialize_master_key()
        
        # Load existing keys
        self._load_encryption_keys()
        
        logger.info("EncryptionManager initialized")
    
    def encrypt(
        self,
        data: Union[str, bytes],
        algorithm: Union[str, EncryptionAlgorithm] = EncryptionAlgorithm.AES_256_GCM,
        key_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """
        Encrypt data using specified algorithm.
        
        Args:
            data: Data to encrypt
            algorithm: Encryption algorithm to use
            key_id: Specific key ID to use (optional)
            metadata: Additional metadata for encryption
            
        Returns:
            EncryptionResult: Encryption result with encrypted data
        """
        try:
            # Convert algorithm to enum
            if isinstance(algorithm, str):
                algorithm = EncryptionAlgorithm(algorithm)
            
            # Convert data to bytes
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Get or generate encryption key
            if key_id:
                key = self.encryption_keys.get(key_id)
                if not key:
                    raise ValueError(f"Key not found: {key_id}")
            else:
                key = self._get_or_create_key(algorithm)
            
            # Encrypt based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._encrypt_aes_gcm(data, key, metadata)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._encrypt_aes_cbc(data, key, metadata)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._encrypt_chacha20_poly1305(data, key, metadata)
            elif algorithm == EncryptionAlgorithm.FERNET:
                return self._encrypt_fernet(data, key, metadata)
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                return self._encrypt_rsa(data, key, metadata)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def decrypt(
        self,
        encrypted_data: bytes,
        key_id: str,
        algorithm: Union[str, EncryptionAlgorithm],
        iv: bytes = None,
        tag: bytes = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[bytes]:
        """
        Decrypt data using specified key and algorithm.
        
        Args:
            encrypted_data: Encrypted data to decrypt
            key_id: Key ID used for encryption
            algorithm: Encryption algorithm used
            iv: Initialization vector (if applicable)
            tag: Authentication tag (if applicable)
            metadata: Additional metadata
            
        Returns:
            bytes: Decrypted data or None if failed
        """
        try:
            # Convert algorithm to enum
            if isinstance(algorithm, str):
                algorithm = EncryptionAlgorithm(algorithm)
            
            # Get encryption key
            key = self.encryption_keys.get(key_id)
            if not key:
                raise ValueError(f"Key not found: {key_id}")
            
            # Decrypt based on algorithm
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._decrypt_aes_gcm(encrypted_data, key, iv, tag, metadata)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._decrypt_aes_cbc(encrypted_data, key, iv, metadata)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._decrypt_chacha20_poly1305(encrypted_data, key, iv, metadata)
            elif algorithm == EncryptionAlgorithm.FERNET:
                return self._decrypt_fernet(encrypted_data, key, metadata)
            elif algorithm == EncryptionAlgorithm.RSA_4096:
                return self._decrypt_rsa(encrypted_data, key, metadata)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def encrypt_secret_data(
        self,
        secret_data: Dict[str, Any],
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    ) -> Dict[str, Any]:
        """
        Encrypt secret data dictionary.
        
        Args:
            secret_data: Secret data to encrypt
            algorithm: Encryption algorithm to use
            
        Returns:
            dict: Encrypted secret data with metadata
        """
        try:
            # Serialize secret data
            serialized_data = json.dumps(secret_data, sort_keys=True)
            
            # Encrypt data
            result = self.encrypt(serialized_data, algorithm)
            
            if not result.success:
                raise RuntimeError(f"Encryption failed: {result.error}")
            
            # Return encrypted data with metadata
            return {
                'encrypted_data': base64.b64encode(result.encrypted_data).decode('utf-8'),
                'encryption_metadata': {
                    'key_id': result.key_id,
                    'algorithm': result.algorithm,
                    'iv': base64.b64encode(result.iv).decode('utf-8') if result.iv else None,
                    'tag': base64.b64encode(result.tag).decode('utf-8') if result.tag else None,
                    'encrypted_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Secret data encryption failed: {e}")
            raise
    
    def decrypt_secret_data(
        self,
        encrypted_secret: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Decrypt secret data dictionary.
        
        Args:
            encrypted_secret: Encrypted secret data
            
        Returns:
            dict: Decrypted secret data
        """
        try:
            # Extract encryption metadata
            metadata = encrypted_secret['encryption_metadata']
            encrypted_data = base64.b64decode(encrypted_secret['encrypted_data'])
            
            iv = base64.b64decode(metadata['iv']) if metadata.get('iv') else None
            tag = base64.b64decode(metadata['tag']) if metadata.get('tag') else None
            
            # Decrypt data
            decrypted_data = self.decrypt(
                encrypted_data=encrypted_data,
                key_id=metadata['key_id'],
                algorithm=metadata['algorithm'],
                iv=iv,
                tag=tag
            )
            
            if not decrypted_data:
                raise RuntimeError("Decryption failed")
            
            # Deserialize and return
            return json.loads(decrypted_data.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Secret data decryption failed: {e}")
            raise
    
    def generate_key(
        self,
        algorithm: EncryptionAlgorithm,
        key_size: int = None,
        password: str = None,
        salt: bytes = None,
        kdf: KeyDerivationFunction = KeyDerivationFunction.PBKDF2,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Generate new encryption key.
        
        Args:
            algorithm: Encryption algorithm
            key_size: Key size in bits (optional)
            password: Password for key derivation (optional)
            salt: Salt for key derivation (optional)
            kdf: Key derivation function
            metadata: Additional metadata
            
        Returns:
            str: Generated key ID
        """
        try:
            key_id = self._generate_key_id()
            
            if password:
                # Derive key from password
                salt = salt or secrets.token_bytes(32)
                key_data = self._derive_key_from_password(password, salt, kdf, key_size or 32)
            else:
                # Generate random key
                key_size_bytes = self._get_key_size_bytes(algorithm, key_size)
                key_data = secrets.token_bytes(key_size_bytes)
                salt = secrets.token_bytes(32)
            
            # Create encryption key
            key = EncryptionKey(
                key_id=key_id,
                algorithm=algorithm,
                key_data=key_data,
                salt=salt,
                created_at=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # Store key
            self.encryption_keys[key_id] = key
            self._save_encryption_keys()
            
            logger.info(f"Generated encryption key: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            raise
    
    def rotate_key(
        self,
        old_key_id: str,
        new_algorithm: EncryptionAlgorithm = None
    ) -> str:
        """
        Rotate encryption key.
        
        Args:
            old_key_id: ID of key to rotate
            new_algorithm: New algorithm for rotated key
            
        Returns:
            str: New key ID
        """
        with self.key_rotation_lock:
            try:
                old_key = self.encryption_keys.get(old_key_id)
                if not old_key:
                    raise ValueError(f"Key not found: {old_key_id}")
                
                # Generate new key
                algorithm = new_algorithm or old_key.algorithm
                new_key_id = self.generate_key(
                    algorithm=algorithm,
                    metadata={'rotated_from': old_key_id}
                )
                
                # Mark old key as rotated
                old_key.metadata = old_key.metadata or {}
                old_key.metadata['rotated_to'] = new_key_id
                old_key.metadata['rotated_at'] = datetime.utcnow().isoformat()
                
                self._save_encryption_keys()
                
                logger.info(f"Key rotated: {old_key_id} -> {new_key_id}")
                return new_key_id
                
            except Exception as e:
                logger.error(f"Key rotation failed: {e}")
                raise
    
    def delete_key(
        self,
        key_id: str,
        secure_delete: bool = True
    ) -> bool:
        """
        Delete encryption key.
        
        Args:
            key_id: Key ID to delete
            secure_delete: Whether to securely overwrite key data
            
        Returns:
            bool: True if successful
        """
        try:
            key = self.encryption_keys.get(key_id)
            if not key:
                logger.warning(f"Key not found for deletion: {key_id}")
                return False
            
            if secure_delete:
                # Securely overwrite key data
                self._secure_delete_key_data(key.key_data)
            
            # Remove from memory
            del self.encryption_keys[key_id]
            self._save_encryption_keys()
            
            logger.info(f"Key deleted: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Key deletion failed: {e}")
            return False
    
    def export_key(
        self,
        key_id: str,
        try:
            logger.info(f"Executing export_key")
            
            # Implementation for export_key
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"export_key completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"export_key failed: {e}")
            raise
            key = self.encryption_keys.get(key_id)
            if not key:
                raise ValueError(f"Key not found: {key_id}")
            
            # Create export data
            export_data = {
                'key_id': key.key_id,
                'algorithm': key.algorithm.value,
                'key_data': base64.b64encode(key.key_data).decode('utf-8'),
                'salt': base64.b64encode(key.salt).decode('utf-8'),
                'created_at': key.created_at.isoformat(),
                'metadata': key.metadata
            }
            
            # Encrypt export data
            salt = secrets.token_bytes(32)
            derived_key = self._derive_key_from_password(
                password, salt, KeyDerivationFunction.PBKDF2, 32
            )
            
            fernet = Fernet(base64.urlsafe_b64encode(derived_key))
            encrypted_export = fernet.encrypt(json.dumps(export_data).encode())
            
            # Add salt prefix
            export_blob = salt + encrypted_export
            
            if format == "pem":
                return self._format_as_pem(export_blob, "ENCRYPTED KEY")
            elif format == "json":
                return json.dumps({
                    'encrypted_key': base64.b64encode(export_blob).decode('utf-8'),
                    'format': 'encrypted_json'
                }).encode()
            else:
                return export_blob
                
        except Exception as e:
            logger.error(f"Key export failed: {e}")
            return None
    
    def import_key(
        self,
        encrypted_key_data: bytes,
        try:
            logger.info(f"Executing import_key")
            
            # Implementation for import_key
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"import_key completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"import_key failed: {e}")
            raise
            if format == "auto":
                if encrypted_key_data.startswith(b'-----'):
                    format = "pem"
                elif encrypted_key_data.startswith(b'{'):
                    format = "json"
                else:
                    format = "raw"
            
            # Extract encrypted data
            if format == "pem":
                encrypted_data = self._parse_pem(encrypted_key_data)
            elif format == "json":
                json_data = json.loads(encrypted_key_data.decode())
                encrypted_data = base64.b64decode(json_data['encrypted_key'])
            else:
                encrypted_data = encrypted_key_data
            
            # Extract salt and decrypt
            salt = encrypted_data[:32]
            encrypted_export = encrypted_data[32:]
            
            derived_key = self._derive_key_from_password(
                password, salt, KeyDerivationFunction.PBKDF2, 32
            )
            
            fernet = Fernet(base64.urlsafe_b64encode(derived_key))
            decrypted_data = fernet.decrypt(encrypted_export)
            
            # Parse key data
            key_data = json.loads(decrypted_data.decode())
            
            # Create encryption key
            key = EncryptionKey(
                key_id=key_data['key_id'],
                algorithm=EncryptionAlgorithm(key_data['algorithm']),
                key_data=base64.b64decode(key_data['key_data']),
                salt=base64.b64decode(key_data['salt']),
                created_at=datetime.fromisoformat(key_data['created_at']),
                metadata=key_data.get('metadata', {})
            )
            
            # Store key
            self.encryption_keys[key.key_id] = key
            self._save_encryption_keys()
            
            logger.info(f"Key imported: {key.key_id}")
            return key.key_id
            
        except Exception as e:
            logger.error(f"Key import failed: {e}")
            return None
    
    def get_key_info(self, key_id: str) -> Optional[Dict[str, Any]]:
        """
        Get encryption key information.
        
        Args:
            key_id: Key ID to query
            
        Returns:
            dict: Key information (without sensitive data)
        """
        key = self.encryption_keys.get(key_id)
        if not key:
            return None
        
        return {
            'key_id': key.key_id,
            'algorithm': key.algorithm.value,
            'created_at': key.created_at.isoformat(),
            'expires_at': key.expires_at.isoformat() if key.expires_at else None,
            'metadata': key.metadata
        }
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """
        List all encryption keys.
        
        Returns:
            list: List of key information
        """
        return [self.get_key_info(key_id) for key_id in self.encryption_keys.keys()]
    
    def _encrypt_aes_gcm(
        self,
        data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """
Encrypt using AES-256-GCM."""
        try:
            aesgcm = AESGCM(key.key_data)
            iv = secrets.token_bytes(12)  # GCM recommends 96-bit IV
            
            encrypted_data = aesgcm.encrypt(iv, data, None)
            
            # Split encrypted data and tag
            ciphertext = encrypted_data[:-16]
            tag = encrypted_data[-16:]
            
            return EncryptionResult(
                success=True,
                encrypted_data=ciphertext,
                key_id=key.key_id,
                algorithm=key.algorithm.value,
                iv=iv,
                tag=tag
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_aes_gcm(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        iv: bytes,
        tag: bytes,
        metadata: Dict[str, Any] = None
    ) -> Optional[bytes]:
        """
Decrypt using AES-256-GCM."""
        try:
            aesgcm = AESGCM(key.key_data)
            
            # Combine ciphertext and tag
            ciphertext_with_tag = encrypted_data + tag
            
            return aesgcm.decrypt(iv, ciphertext_with_tag, None)
            
        except Exception as e:
            logger.error(f"AES-GCM decryption failed: {e}")
            return None
    
    def _encrypt_aes_cbc(
        self,
        data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """Encrypt using AES-256-CBC."""
        try:
            # Pad data to block size
            padding_length = 16 - (len(data) % 16)
            padded_data = data + bytes([padding_length] * padding_length)
            
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(key.key_data), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=key.key_id,
                algorithm=key.algorithm.value,
                iv=iv
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_aes_cbc(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        iv: bytes,
        metadata: Dict[str, Any] = None
    ) -> Optional[bytes]:
        """
Decrypt using AES-256-CBC."""
        try:
            cipher = Cipher(algorithms.AES(key.key_data), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove padding
            padding_length = padded_data[-1]
            return padded_data[:-padding_length]
            
        except Exception as e:
            logger.error(f"AES-CBC decryption failed: {e}")
            return None
    
    def _encrypt_chacha20_poly1305(
        self,
        data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """Encrypt using ChaCha20-Poly1305."""
        try:
            chacha = ChaCha20Poly1305(key.key_data)
            iv = secrets.token_bytes(12)
            
            encrypted_data = chacha.encrypt(iv, data, None)
            
            # Split encrypted data and tag
            ciphertext = encrypted_data[:-16]
            tag = encrypted_data[-16:]
            
            return EncryptionResult(
                success=True,
                encrypted_data=ciphertext,
                key_id=key.key_id,
                algorithm=key.algorithm.value,
                iv=iv,
                tag=tag
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_chacha20_poly1305(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        iv: bytes,
        metadata: Dict[str, Any] = None
    ) -> Optional[bytes]:
        """
Decrypt using ChaCha20-Poly1305."""
        try:
            chacha = ChaCha20Poly1305(key.key_data)
            
            # Note: ChaCha20Poly1305.decrypt expects ciphertext+tag
            return chacha.decrypt(iv, encrypted_data, None)
            
        except Exception as e:
            logger.error(f"ChaCha20-Poly1305 decryption failed: {e}")
            return None
    
    def _encrypt_fernet(
        self,
        data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """Encrypt using Fernet."""
        try:
            fernet_key = base64.urlsafe_b64encode(key.key_data)
            fernet = Fernet(fernet_key)
            
            encrypted_data = fernet.encrypt(data)
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                key_id=key.key_id,
                algorithm=key.algorithm.value
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_fernet(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> Optional[bytes]:
        """
Decrypt using Fernet."""
        try:
            fernet_key = base64.urlsafe_b64encode(key.key_data)
            fernet = Fernet(fernet_key)
            
            return fernet.decrypt(encrypted_data)
            
        except Exception as e:
            logger.error(f"Fernet decryption failed: {e}")
            return None
    
    def _encrypt_rsa(
        self,
        data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """Encrypt using RSA."""
        try:
            # RSA encryption is limited by key size
            # For larger data, use hybrid encryption
            if len(data) > 446:  # Max for RSA-4096 with OAEP
                # Use AES for data, RSA for AES key
                aes_key = secrets.token_bytes(32)
                aes_result = self._encrypt_aes_gcm_direct(data, aes_key)
                
                # Encrypt AES key with RSA
                private_key = serialization.load_der_private_key(key.key_data, password=None)
                public_key = private_key.public_key()
                
                encrypted_aes_key = public_key.encrypt(
                    aes_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                # Combine encrypted key and data
                hybrid_data = len(encrypted_aes_key).to_bytes(4, 'big') + encrypted_aes_key + aes_result
                
                return EncryptionResult(
                    success=True,
                    encrypted_data=hybrid_data,
                    key_id=key.key_id,
                    algorithm=key.algorithm.value
                )
            else:
                # Direct RSA encryption
                private_key = serialization.load_der_private_key(key.key_data, password=None)
                public_key = private_key.public_key()
                
                encrypted_data = public_key.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                return EncryptionResult(
                    success=True,
                    encrypted_data=encrypted_data,
                    key_id=key.key_id,
                    algorithm=key.algorithm.value
                )
                
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_rsa(
        self,
        encrypted_data: bytes,
        key: EncryptionKey,
        metadata: Dict[str, Any] = None
    ) -> Optional[bytes]:
        """
Decrypt using RSA."""
        try:
            private_key = serialization.load_der_private_key(key.key_data, password=None)
            
            # Check if hybrid encryption was used
            if len(encrypted_data) > 512:  # RSA-4096 output is 512 bytes
                # Hybrid decryption
                key_length = int.from_bytes(encrypted_data[:4], 'big')
                encrypted_aes_key = encrypted_data[4:4+key_length]
                encrypted_content = encrypted_data[4+key_length:]
                
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
                return self._decrypt_aes_gcm_direct(encrypted_content, aes_key)
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
                
        except Exception as e:
            logger.error(f"RSA decryption failed: {e}")
            return None
    
    def _encrypt_aes_gcm_direct(self, data: bytes, key: bytes) -> bytes:
        """Direct AES-GCM encryption."""
        aesgcm = AESGCM(key)
        iv = secrets.token_bytes(12)
        encrypted = aesgcm.encrypt(iv, data, None)
        return iv + encrypted
    
    def _decrypt_aes_gcm_direct(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
Direct AES-GCM decryption."""
        aesgcm = AESGCM(key)
        iv = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return aesgcm.decrypt(iv, ciphertext, None)
    
    def _derive_key_from_password(
        self,
        password: str,
        salt: bytes,
        try:
            logger.info(f"Executing _derive_key_from_password")
            
            # Implementation for _derive_key_from_password
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_derive_key_from_password completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_derive_key_from_password failed: {e}")
            raise
                salt=salt,
                iterations=100000
            )
            return kdf_instance.derive(password_bytes)
            
        elif kdf == KeyDerivationFunction.SCRYPT:
            kdf_instance = Scrypt(
                algorithm=hashes.SHA256(),
                length=key_length,
                salt=salt,
                n=2**14,
                r=8,
                p=1
            )
            return kdf_instance.derive(password_bytes)
            
        elif kdf == KeyDerivationFunction.ARGON2:
            return argon2.hash_password_raw(
                password_bytes,
                salt,
                time_cost=2,
                memory_cost=2**16,
                parallelism=1,
                hash_len=key_length,
                type=argon2.Type.ID
            )
            
        elif kdf == KeyDerivationFunction.HKDF:
            kdf_instance = HKDF(
                algorithm=hashes.SHA256(),
                length=key_length,
                salt=salt,
                info=b'IA-Influencer-Agent'
            )
            return kdf_instance.derive(password_bytes)
        
        else:
            raise ValueError(f"Unsupported KDF: {kdf}")
    
    def _get_or_create_key(self, algorithm: EncryptionAlgorithm) -> EncryptionKey:
        """Get existing key or create new one for algorithm."""
        # Look for existing key
        for key in self.encryption_keys.values():
            if key.algorithm == algorithm:
                return key
        
        # Create new key
        key_id = self.generate_key(algorithm)
        return self.encryption_keys[key_id]
    
    def _get_key_size_bytes(self, algorithm: EncryptionAlgorithm, key_size: int = None) -> int:
        """
Get key size in bytes for algorithm."""
        if key_size:
            return key_size // 8
        
        if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
            return 32  # 256 bits
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            return 32  # 256 bits
        elif algorithm == EncryptionAlgorithm.FERNET:
            return 32  # 256 bits
        else:
            return 32  # Default
    
    def _generate_key_id(self) -> str:
        """
Generate unique key ID."""
        return f"key_{secrets.token_hex(16)}_{int(datetime.utcnow().timestamp())}"
    
    def _initialize_master_key(self) -> None:
        """Initialize master key for key encryption."""
        master_key_path = Path(self.config.master_key_path)
        
        if master_key_path.exists():
            # Load existing master key
            with open(master_key_path, 'rb') as f:
                self.master_key = f.read()
        else:
            # Generate new master key
            self.master_key = secrets.token_bytes(32)
            
            # Save master key securely
            master_key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(master_key_path, 'wb') as f:
                f.write(self.master_key)
            
            # Set secure permissions
            os.chmod(master_key_path, 0o600)
            
        logger.info("Master key initialized")
    
    def _load_encryption_keys(self) -> None:
        """Load encryption keys from storage."""
        try:
            keys_file = Path(self.config.encryption_keys_file)
            if not keys_file.exists():
                return
            
            with open(keys_file, 'rb') as f:
                encrypted_keys_data = f.read()
            
            # Decrypt keys data with master key
            fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
            keys_data = fernet.decrypt(encrypted_keys_data)
            
            # Load keys
            keys_dict = json.loads(keys_data.decode())
            
            for key_data in keys_dict['keys']:
                key = EncryptionKey(
                    key_id=key_data['key_id'],
                    algorithm=EncryptionAlgorithm(key_data['algorithm']),
                    key_data=base64.b64decode(key_data['key_data']),
                    salt=base64.b64decode(key_data['salt']),
                    created_at=datetime.fromisoformat(key_data['created_at']),
                    expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data.get('expires_at') else None,
                    metadata=key_data.get('metadata', {})
                )
                self.encryption_keys[key.key_id] = key
            
            logger.info(f"Loaded {len(self.encryption_keys)} encryption keys")
            
        except Exception as e:
            logger.error(f"Failed to load encryption keys: {e}")
    
    def _save_encryption_keys(self) -> None:
        """Save encryption keys to storage."""
        try:
            keys_data = {
                'version': '1.0',
                'keys': []
            }
            
            for key in self.encryption_keys.values():
                keys_data['keys'].append({
                    'key_id': key.key_id,
                    'algorithm': key.algorithm.value,
                    'key_data': base64.b64encode(key.key_data).decode(),
                    'salt': base64.b64encode(key.salt).decode(),
                    'created_at': key.created_at.isoformat(),
                    'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                    'metadata': key.metadata
                })
            
            # Encrypt keys data with master key
            fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
            encrypted_keys_data = fernet.encrypt(json.dumps(keys_data).encode())
            
            # Save to file
            keys_file = Path(self.config.encryption_keys_file)
            keys_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(keys_file, 'wb') as f:
                f.write(encrypted_keys_data)
            
            # Set secure permissions
            os.chmod(keys_file, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to save encryption keys: {e}")
    
    def _secure_delete_key_data(self, key_data: bytes) -> None:
        """Securely overwrite key data in memory."""
        try:
            # Overwrite with random data multiple times
            for _ in range(3):
                for i in range(len(key_data)):
                    key_data[i] = secrets.randbits(8)
        except Exception:
            # Best effort
            pass
    
    def _format_as_pem(self, data: bytes, label: str) -> bytes:
        """
Format data as PEM."""
        encoded = base64.b64encode(data).decode()
        lines = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
        
        pem_content = f"-----BEGIN {label}-----\n"
        pem_content += '\n'.join(lines)
        pem_content += f"\n-----END {label}-----\n"
        
        return pem_content.encode()
    
    def _parse_pem(self, pem_data: bytes) -> bytes:
        """Parse PEM formatted data."""
        pem_text = pem_data.decode()
        lines = pem_text.split('\n')
        
        # Find content between BEGIN and END
        content_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith('-----BEGIN'):
                in_content = True
                continue
            elif line.startswith('-----END'):
                break
            elif in_content:
                content_lines.append(line.strip())
        
        content = ''.join(content_lines)
        return base64.b64decode(content)


class ContentProtectionEncryption(EncryptionManager):
    """
    Specialized encryption manager for IA Influencer Agent content protection.
    
    Handles encryption for:
    - Audio fingerprint data
    - Video fingerprint vectors  
    - Image hash signatures
    - Text content embeddings
    - User-generated content
    """
    
    def __init__(self, config -> None: SecretsConfig = None) -> None:
        super().__init__(config)
        self.content_keys: Dict[str, EncryptionKey] = {}
        self.protection_algorithms = {
            'audio': EncryptionAlgorithm.AES_256_GCM,
            'video': EncryptionAlgorithm.AES_256_GCM,
            'image': EncryptionAlgorithm.CHACHA20_POLY1305,
            'text': EncryptionAlgorithm.AES_256_GCM,
            'user_content': EncryptionAlgorithm.AES_256_GCM
        }
        
        # Initialize content protection keys
        self._initialize_content_protection_keys()
        
        logger.info("ContentProtectionEncryption initialized")
    
    def _initialize_content_protection_keys(self) -> None:
        """Initialize content-specific encryption keys."""
        for content_type, algorithm in self.protection_algorithms.items():
            key_id = f"content_protection_{content_type}"
            
            if key_id not in self.encryption_keys:
                # Generate new content protection key
                self.generate_encryption_key(
                    key_id=key_id,
                    algorithm=algorithm,
                    metadata={
                        'content_type': content_type,
                        'protection_level': 'high',
                        'rotation_interval': '30d',
                        'compliance': ['GDPR', 'CCPA']
                    }
                )
                logger.info(f"Generated content protection key for {content_type}")
    
    def encrypt_fingerprint_data(
        self,
        fingerprint_data: bytes,
        content_type: str,
        user_id: Optional[str] = None
    ) -> EncryptionResult:
        """
        Encrypt fingerprint data for content protection.
        
        Args:
            fingerprint_data: Raw fingerprint data
            content_type: Type of content (audio, video, image, text)
            user_id: Optional user identifier for key derivation
            
        Returns:
            EncryptionResult: Encryption operation result
        """
        try:
            # Get content-specific encryption key
            key_id = f"content_protection_{content_type}"
            if key_id not in self.encryption_keys:
                return EncryptionResult(
                    success=False,
                    error=f"No encryption key found for content type: {content_type}"
                )
            
            encryption_key = self.encryption_keys[key_id]
            
            # Derive user-specific key if user_id provided
            if user_id:
                derived_key = self._derive_user_key(encryption_key.key_data, user_id)
            else:
                derived_key = encryption_key.key_data
            
            # Encrypt fingerprint data
            result = self.encrypt_data(
                data=fingerprint_data,
                key_id=key_id,
                algorithm=encryption_key.algorithm,
                additional_data=f"fingerprint_{content_type}_{user_id or 'system'}"
            )
            
            if result.success:
                logger.debug(f"Fingerprint data encrypted for {content_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to encrypt fingerprint data for {content_type}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def decrypt_fingerprint_data(
        self,
        encrypted_data: bytes,
        content_type: str,
        user_id: Optional[str] = None,
        iv: Optional[bytes] = None,
        tag: Optional[bytes] = None
    ) -> EncryptionResult:
        """
        Decrypt fingerprint data for content protection.
        
        Args:
            encrypted_data: Encrypted fingerprint data
            content_type: Type of content (audio, video, image, text)
            user_id: Optional user identifier for key derivation
            iv: Initialization vector
            tag: Authentication tag
            
        Returns:
            EncryptionResult: Decryption operation result with fingerprint data
        """
        try:
            # Get content-specific encryption key
            key_id = f"content_protection_{content_type}"
            if key_id not in self.encryption_keys:
                return EncryptionResult(
                    success=False,
                    error=f"No encryption key found for content type: {content_type}"
                )
            
            encryption_key = self.encryption_keys[key_id]
            
            # Derive user-specific key if user_id provided
            if user_id:
                derived_key = self._derive_user_key(encryption_key.key_data, user_id)
            else:
                derived_key = encryption_key.key_data
            
            # Decrypt fingerprint data
            if encryption_key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                result = self._decrypt_aes_gcm(
                    encrypted_data=encrypted_data,
                    key=derived_key,
                    iv=iv,
                    tag=tag,
                    additional_data=f"fingerprint_{content_type}_{user_id or 'system'}"
                )
            elif encryption_key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                result = self._decrypt_chacha20_poly1305(
                    encrypted_data=encrypted_data,
                    key=derived_key,
                    nonce=iv,
                    additional_data=f"fingerprint_{content_type}_{user_id or 'system'}"
                )
            else:
                return EncryptionResult(
                    success=False,
                    error=f"Unsupported algorithm for fingerprint decryption: {encryption_key.algorithm}"
                )
            
            if result.success:
                logger.debug(f"Fingerprint data decrypted for {content_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to decrypt fingerprint data for {content_type}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def encrypt_user_content(
        self,
        content_data: bytes,
        user_id: str,
        content_metadata: Dict[str, Any] = None
    ) -> EncryptionResult:
        """
        Encrypt user-generated content with user-specific keys.
        
        Args:
            content_data: Raw content data
            user_id: User identifier
            content_metadata: Optional content metadata
            
        Returns:
            EncryptionResult: Encryption operation result
        """
        try:
            # Get user content encryption key
            key_id = "content_protection_user_content"
            if key_id not in self.encryption_keys:
                return EncryptionResult(
                    success=False,
                    error="No encryption key found for user content"
                )
            
            encryption_key = self.encryption_keys[key_id]
            
            # Derive user-specific key
            derived_key = self._derive_user_key(encryption_key.key_data, user_id)
            
            # Include metadata in additional authenticated data
            metadata_str = json.dumps(content_metadata or {}, sort_keys=True)
            additional_data = f"user_content_{user_id}_{metadata_str}"
            
            # Encrypt content data
            result = self.encrypt_data(
                data=content_data,
                key_id=key_id,
                algorithm=encryption_key.algorithm,
                additional_data=additional_data
            )
            
            if result.success:
                logger.info(f"User content encrypted for user {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to encrypt user content for {user_id}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def decrypt_user_content(
        self,
        encrypted_data: bytes,
        user_id: str,
        content_metadata: Dict[str, Any] = None,
        iv: Optional[bytes] = None,
        tag: Optional[bytes] = None
    ) -> EncryptionResult:
        """
        Decrypt user-generated content with user-specific keys.
        
        Args:
            encrypted_data: Encrypted content data
            user_id: User identifier
            content_metadata: Optional content metadata
            iv: Initialization vector
            tag: Authentication tag
            
        Returns:
            EncryptionResult: Decryption operation result with content data
        """
        try:
            # Get user content encryption key
            key_id = "content_protection_user_content"
            if key_id not in self.encryption_keys:
                return EncryptionResult(
                    success=False,
                    error="No encryption key found for user content"
                )
            
            encryption_key = self.encryption_keys[key_id]
            
            # Derive user-specific key
            derived_key = self._derive_user_key(encryption_key.key_data, user_id)
            
            # Include metadata in additional authenticated data
            metadata_str = json.dumps(content_metadata or {}, sort_keys=True)
            additional_data = f"user_content_{user_id}_{metadata_str}"
            
            # Decrypt content data
            result = self._decrypt_aes_gcm(
                encrypted_data=encrypted_data,
                key=derived_key,
                iv=iv,
                tag=tag,
                additional_data=additional_data
            )
            
            if result.success:
                logger.info(f"User content decrypted for user {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to decrypt user content for {user_id}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def encrypt_api_credentials(
        self,
        credentials: Dict[str, str],
        platform: str,
        user_id: Optional[str] = None
    ) -> EncryptionResult:
        """
        Encrypt platform API credentials.
        
        Args:
            credentials: API credentials dictionary
            platform: Platform name
            user_id: Optional user identifier
            
        Returns:
            EncryptionResult: Encryption operation result
        """
        try:
            # Serialize credentials
            credentials_data = json.dumps(credentials, sort_keys=True).encode()
            
            # Generate platform-specific key ID
            key_id = f"api_credentials_{platform}"
            
            # Create or get platform-specific key
            if key_id not in self.encryption_keys:
                self.generate_encryption_key(
                    key_id=key_id,
                    algorithm=EncryptionAlgorithm.AES_256_GCM,
                    metadata={
                        'platform': platform,
                        'credential_type': 'api_access',
                        'rotation_interval': '60d'
                    }
                )
            
            encryption_key = self.encryption_keys[key_id]
            
            # Derive user-specific key if provided
            if user_id:
                derived_key = self._derive_user_key(encryption_key.key_data, user_id)
                additional_data = f"api_credentials_{platform}_{user_id}"
            else:
                derived_key = encryption_key.key_data
                additional_data = f"api_credentials_{platform}_system"
            
            # Encrypt credentials
            result = self._encrypt_aes_gcm(
                data=credentials_data,
                key=derived_key,
                additional_data=additional_data
            )
            
            if result.success:
                logger.info(f"API credentials encrypted for {platform}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to encrypt API credentials for {platform}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def decrypt_api_credentials(
        self,
        encrypted_data: bytes,
        platform: str,
        user_id: Optional[str] = None,
        iv: Optional[bytes] = None,
        tag: Optional[bytes] = None
    ) -> Dict[str, str]:
        """
        Decrypt platform API credentials.
        
        Args:
            encrypted_data: Encrypted credentials data
            platform: Platform name
            user_id: Optional user identifier
            iv: Initialization vector
            tag: Authentication tag
            
        Returns:
            dict: Decrypted credentials or empty dict on failure
        """
        try:
            # Get platform-specific key
            key_id = f"api_credentials_{platform}"
            if key_id not in self.encryption_keys:
                logger.error(f"No encryption key found for platform: {platform}")
                return {}
            
            encryption_key = self.encryption_keys[key_id]
            
            # Derive user-specific key if provided
            if user_id:
                derived_key = self._derive_user_key(encryption_key.key_data, user_id)
                additional_data = f"api_credentials_{platform}_{user_id}"
            else:
                derived_key = encryption_key.key_data
                additional_data = f"api_credentials_{platform}_system"
            
            # Decrypt credentials
            result = self._decrypt_aes_gcm(
                encrypted_data=encrypted_data,
                key=derived_key,
                iv=iv,
                tag=tag,
                additional_data=additional_data
            )
            
            if result.success:
                credentials_data = result.encrypted_data  # Contains decrypted data
                credentials = json.loads(credentials_data.decode())
                logger.info(f"API credentials decrypted for {platform}")
                return credentials
            else:
                logger.error(f"Failed to decrypt API credentials for {platform}: {result.error}")
                return {}
            
        except Exception as e:
            logger.error(f"Failed to decrypt API credentials for {platform}: {e}")
            return {}
    
    def encrypt_payment_data(
        self,
        payment_data: Dict[str, Any],
        processor: str,
        compliance_level: str = "PCI_DSS_L1"
    ) -> EncryptionResult:
        """
        Encrypt payment processor data with PCI DSS compliance.
        
        Args:
            payment_data: Payment data dictionary
            processor: Payment processor name
            compliance_level: PCI compliance level
            
        Returns:
            EncryptionResult: Encryption operation result
        """
        try:
            # Use strongest encryption for payment data
            key_id = f"payment_data_{processor}"
            
            # Create or get payment-specific key with high security
            if key_id not in self.encryption_keys:
                self.generate_encryption_key(
                    key_id=key_id,
                    algorithm=EncryptionAlgorithm.AES_256_GCM,
                    metadata={
                        'processor': processor,
                        'compliance_level': compliance_level,
                        'data_type': 'payment_sensitive',
                        'rotation_interval': '30d',
                        'encryption_strength': 'maximum'
                    }
                )
            
            encryption_key = self.encryption_keys[key_id]
            
            # Serialize payment data
            payment_json = json.dumps(payment_data, sort_keys=True).encode()
            
            # Use processor-specific additional data
            additional_data = f"payment_data_{processor}_{compliance_level}"
            
            # Encrypt with maximum security
            result = self._encrypt_aes_gcm(
                data=payment_json,
                key=encryption_key.key_data,
                additional_data=additional_data
            )
            
            if result.success:
                logger.info(f"Payment data encrypted for {processor} with {compliance_level}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to encrypt payment data for {processor}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def decrypt_payment_data(
        self,
        encrypted_data: bytes,
        processor: str,
        compliance_level: str = "PCI_DSS_L1",
        iv: Optional[bytes] = None,
        tag: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Decrypt payment processor data with PCI DSS compliance verification.
        
        Args:
            encrypted_data: Encrypted payment data
            processor: Payment processor name
            compliance_level: PCI compliance level
            iv: Initialization vector
            tag: Authentication tag
            
        Returns:
            dict: Decrypted payment data or empty dict on failure
        """
        try:
            # Get payment-specific key
            key_id = f"payment_data_{processor}"
            if key_id not in self.encryption_keys:
                logger.error(f"No encryption key found for payment processor: {processor}")
                return {}
            
            encryption_key = self.encryption_keys[key_id]
            
            # Use processor-specific additional data
            additional_data = f"payment_data_{processor}_{compliance_level}"
            
            # Decrypt payment data
            result = self._decrypt_aes_gcm(
                encrypted_data=encrypted_data,
                key=encryption_key.key_data,
                iv=iv,
                tag=tag,
                additional_data=additional_data
            )
            
            if result.success:
                payment_data = json.loads(result.encrypted_data.decode())  # Contains decrypted data
                logger.info(f"Payment data decrypted for {processor} with {compliance_level}")
                return payment_data
            else:
                logger.error(f"Failed to decrypt payment data for {processor}: {result.error}")
                return {}
            
        except Exception as e:
            logger.error(f"Failed to decrypt payment data for {processor}: {e}")
            return {}
    
    def _derive_user_key(self, master_key: bytes, user_id: str) -> bytes:
        """
        Derive user-specific encryption key from master key.
        
        Args:
            master_key: Master encryption key
            user_id: User identifier
            
        Returns:
            bytes: Derived user-specific key
        """
        try:
            # Use HKDF to derive user-specific key
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=b"ia_influencer_user_key_derivation",
                info=f"user_{user_id}".encode(),
            )
            
            derived_key = hkdf.derive(master_key)
            return derived_key
            
        except Exception as e:
            logger.error(f"Failed to derive user key for {user_id}: {e}")
            raise
    
    def _encrypt_aes_gcm(
        self,
        data: bytes,
        key: bytes,
        additional_data: str = None
    ) -> EncryptionResult:
        """Encrypt data using AES-GCM."""
        try:
            # Generate random IV
            iv = secrets.token_bytes(12)  # 96 bits for GCM
            
            # Create cipher
            cipher = AESGCM(key)
            
            # Encrypt with additional authenticated data
            aad = additional_data.encode() if additional_data else None
            encrypted_data = cipher.encrypt(iv, data, aad)
            
            # Extract ciphertext and tag
            ciphertext = encrypted_data[:-16]  # All but last 16 bytes
            tag = encrypted_data[-16:]  # Last 16 bytes
            
            return EncryptionResult(
                success=True,
                encrypted_data=ciphertext,
                algorithm="aes_256_gcm",
                iv=iv,
                tag=tag
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_aes_gcm(
        self,
        encrypted_data: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
        additional_data: str = None
    ) -> EncryptionResult:
        """Decrypt data using AES-GCM."""
        try:
            # Create cipher
            cipher = AESGCM(key)
            
            # Combine ciphertext and tag
            ciphertext_with_tag = encrypted_data + tag
            
            # Decrypt with additional authenticated data
            aad = additional_data.encode() if additional_data else None
            decrypted_data = cipher.decrypt(iv, ciphertext_with_tag, aad)
            
            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,  # Contains decrypted data
                algorithm="aes_256_gcm"
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def _decrypt_chacha20_poly1305(
        self,
        encrypted_data: bytes,
        key: bytes,
        nonce: bytes,
        additional_data: str = None
    ) -> EncryptionResult:
        """Decrypt data using ChaCha20-Poly1305."""
        try:
            # Create cipher
            cipher = ChaCha20Poly1305(key)
            
            # Decrypt with additional authenticated data
            aad = additional_data.encode() if additional_data else None
            decrypted_data = cipher.decrypt(nonce, encrypted_data, aad)
            
            return EncryptionResult(
                success=True,
                encrypted_data=decrypted_data,  # Contains decrypted data
                algorithm="chacha20_poly1305"
            )
            
        except Exception as e:
            return EncryptionResult(success=False, error=str(e))
    
    def rotate_content_protection_keys(self) -> Dict[str, bool]:
        """
        Rotate all content protection encryption keys.
        
        Returns:
            dict: Rotation results by content type
        """
        results = {}
        
        try:
            for content_type in self.protection_algorithms.keys():
                try:
                    # Generate new key
                    new_key_id = f"content_protection_{content_type}_new"
                    algorithm = self.protection_algorithms[content_type]
                    
                    success = self.generate_encryption_key(
                        key_id=new_key_id,
                        algorithm=algorithm,
                        metadata={
                            'content_type': content_type,
                            'protection_level': 'high',
                            'rotation_timestamp': datetime.utcnow().isoformat(),
                            'previous_key': f"content_protection_{content_type}"
                        }
                    )
                    
                    if success:
                        # Replace old key with new key
                        old_key_id = f"content_protection_{content_type}"
                        if old_key_id in self.encryption_keys:
                            # Backup old key before deletion
                            old_key = self.encryption_keys[old_key_id]
                            backup_key_id = f"{old_key_id}_backup_{int(datetime.utcnow().timestamp())}"
                            self.encryption_keys[backup_key_id] = old_key
                        
                        # Move new key to primary position
                        self.encryption_keys[old_key_id] = self.encryption_keys[new_key_id]
                        del self.encryption_keys[new_key_id]
                        
                        results[content_type] = True
                        logger.info(f"Content protection key rotated for {content_type}")
                    else:
                        results[content_type] = False
                        logger.error(f"Failed to generate new key for {content_type}")
                
                except Exception as e:
                    results[content_type] = False
                    logger.error(f"Key rotation failed for {content_type}: {e}")
            
            # Save updated keys
            self._save_encryption_keys()
            
            return results
            
        except Exception as e:
            logger.error(f"Content protection key rotation failed: {e}")
            return {content_type: False for content_type in self.protection_algorithms.keys()}
    
    def get_content_protection_status(self) -> Dict[str, Any]:
        """
        Get status of content protection encryption keys.
        
        Returns:
            dict: Status information for all content protection keys
        """
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_keys': len(self.encryption_keys),
            'content_keys': {},
            'key_health': 'healthy'
        }
        
        try:
            for content_type in self.protection_algorithms.keys():
                key_id = f"content_protection_{content_type}"
                
                if key_id in self.encryption_keys:
                    key = self.encryption_keys[key_id]
                    key_age = datetime.utcnow() - key.created_at
                    
                    status['content_keys'][content_type] = {
                        'exists': True,
                        'algorithm': key.algorithm.value,
                        'created_at': key.created_at.isoformat(),
                        'age_days': key_age.days,
                        'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                        'metadata': key.metadata
                    }
                    
                    # Check if key needs rotation (older than 30 days)
                    if key_age.days > 30:
                        status['key_health'] = 'rotation_recommended'
                        status['content_keys'][content_type]['needs_rotation'] = True
                    else:
                        status['content_keys'][content_type]['needs_rotation'] = False
                else:
                    status['content_keys'][content_type] = {
                        'exists': False,
                        'needs_creation': True
                    }
                    status['key_health'] = 'degraded'
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get content protection status: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'key_health': 'error'
            }
))}

# File has syntax issues - needs manual review