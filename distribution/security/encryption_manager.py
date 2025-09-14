"""
Encryption Manager for Ainflue Distribution Security
Provides enterprise-grade encryption for sensitive data and communications

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
import base64
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
import jwt

# Configure logging
logger = logging.getLogger(__name__)


class EncryptionAlgorithm(str, Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_4096 = "rsa_4096"
    RSA_2048 = "rsa_2048"


class KeyType(str, Enum):
    """Encryption key types"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    SIGNING = "signing"
    API_KEY = "api_key"
    SESSION = "session"


class SecurityLevel(str, Enum):
    """Security levels for different data types"""
    LOW = "low"           # Basic encryption
    MEDIUM = "medium"     # Standard encryption
    HIGH = "high"         # Strong encryption
    CRITICAL = "critical" # Maximum security


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    security_level: SecurityLevel
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int = 0
    max_usage: Optional[int] = None
    is_active: bool = True
    
    def is_expired(self) -> bool:
        """Check if key is expired"""
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False
        
    def is_usage_exceeded(self) -> bool:
        """Check if key usage limit is exceeded"""
        if self.max_usage:
            return self.usage_count >= self.max_usage
        return False


class EncryptionManager:
    """
    Advanced encryption manager for content protection and secure communications
    Supports multiple algorithms, key rotation, and enterprise security standards
    """
    
    def __init__(self, master_key -> None: Optional[bytes] = None) -> None:
        self.master_key = master_key or self._generate_master_key()
        self.keys: Dict[str, Tuple[bytes, EncryptionKey]] = {}
        self.key_derivation_salt = secrets.token_bytes(32)
        self.jwt_secret = secrets.token_urlsafe(64)
        
        # Security settings
        self.key_rotation_interval = timedelta(days=30)
        self.max_key_usage = 1000000  # 1M operations per key
        self.require_secure_delete = True
        self.audit_encryption_operations = True
        
        # Algorithm preferences by security level
        self.algorithm_preferences = {
            SecurityLevel.LOW: EncryptionAlgorithm.FERNET,
            SecurityLevel.MEDIUM: EncryptionAlgorithm.AES_256_GCM,
            SecurityLevel.HIGH: EncryptionAlgorithm.CHACHA20_POLY1305,
            SecurityLevel.CRITICAL: EncryptionAlgorithm.CHACHA20_POLY1305
        }
        
        # Initialize default keys
        self._initialize_default_keys()
        
    def _generate_master_key(self) -> bytes:
        """Generate cryptographically secure master key"""
        return secrets.token_bytes(32)  # 256-bit key
        
    def _initialize_default_keys(self) -> None:
        """Initialize default encryption keys"""
        try:
            # Generate default symmetric keys for each security level
            for security_level in SecurityLevel:
                key_id = f"default_{security_level.value}"
                algorithm = self.algorithm_preferences[security_level]
                
                self.generate_key(
                    key_id=key_id,
                    key_type=KeyType.SYMMETRIC,
                    algorithm=algorithm,
                    security_level=security_level
                )
                
            # Generate default RSA key pair
            self.generate_asymmetric_key_pair(
                key_id="default_rsa",
                algorithm=EncryptionAlgorithm.RSA_4096,
                security_level=SecurityLevel.HIGH
            )
            
            logger.info("Default encryption keys initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize default keys: {e}")
            
    def generate_key(self, 
                    key_id: str,
                    key_type: KeyType,
                    algorithm: EncryptionAlgorithm,
                    security_level: SecurityLevel,
                    expires_hours: Optional[int] = None) -> bool:
        """
        Generate a new encryption key
        
        Args:
            key_id: Unique key identifier
            key_type: Type of key to generate
            algorithm: Encryption algorithm
            security_level: Security level
            expires_hours: Key expiration in hours
            
        Returns:
            Success status
        """
        try:
            # Generate key based on algorithm
            if algorithm == EncryptionAlgorithm.FERNET:
                key_bytes = Fernet.generate_key()
            elif algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.CHACHA20_POLY1305]:
                key_bytes = secrets.token_bytes(32)  # 256-bit key
            else:
                raise ValueError(f"Unsupported algorithm for symmetric key: {algorithm}")
                
            # Create key metadata
            expires_at = None
            if expires_hours:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
                
            key_metadata = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                security_level=security_level,
                created_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                max_usage=self.max_key_usage
            )
            
            # Store key
            self.keys[key_id] = (key_bytes, key_metadata)
            
            logger.info(f"Generated key: {key_id} ({algorithm.value})")
            return True
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            return False
            
    def generate_asymmetric_key_pair(self,
                                   key_id: str,
                                   algorithm: EncryptionAlgorithm,
                                   security_level: SecurityLevel,
                                   expires_hours: Optional[int] = None) -> bool:
        """
        Generate asymmetric key pair (RSA)
        
        Args:
            key_id: Base key identifier
            algorithm: RSA algorithm
            security_level: Security level
            expires_hours: Key expiration in hours
            
        Returns:
            Success status
        """
        try:
            # Determine key size
            key_size = 4096 if algorithm == EncryptionAlgorithm.RSA_4096 else 2048
            
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
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
            
            # Create metadata
            expires_at = None
            if expires_hours:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
                
            private_metadata = EncryptionKey(
                key_id=f"{key_id}_private",
                key_type=KeyType.ASYMMETRIC_PRIVATE,
                algorithm=algorithm,
                security_level=security_level,
                created_at=datetime.now(timezone.utc),
                expires_at=expires_at
            )
            
            public_metadata = EncryptionKey(
                key_id=f"{key_id}_public",
                key_type=KeyType.ASYMMETRIC_PUBLIC,
                algorithm=algorithm,
                security_level=security_level,
                created_at=datetime.now(timezone.utc),
                expires_at=expires_at
            )
            
            # Store keys
            self.keys[f"{key_id}_private"] = (private_pem, private_metadata)
            self.keys[f"{key_id}_public"] = (public_pem, public_metadata)
            
            logger.info(f"Generated RSA key pair: {key_id} ({key_size}-bit)")
            return True
            
        except Exception as e:
            logger.error(f"RSA key pair generation failed: {e}")
            return False
            
    def encrypt_data(self, 
                    data: Union[str, bytes],
                    key_id: Optional[str] = None,
                    security_level: SecurityLevel = SecurityLevel.MEDIUM) -> Optional[Dict[str, Any]]:
        """
        Encrypt data using specified key or security level
        
        Args:
            data: Data to encrypt
            key_id: Specific key to use (optional)
            security_level: Security level if no key specified
            
        Returns:
            Encrypted data package with metadata
        """
        try:
            # Convert string to bytes
            if isinstance(data, str):
                data = data.encode('utf-8')
                
            # Select key
            if key_id:
                if key_id not in self.keys:
                    raise ValueError(f"Key not found: {key_id}")
                key_bytes, key_metadata = self.keys[key_id]
            else:
                # Use default key for security level
                key_id = f"default_{security_level.value}"
                if key_id not in self.keys:
                    raise ValueError(f"No default key for security level: {security_level}")
                key_bytes, key_metadata = self.keys[key_id]
                
            # Check key validity
            if key_metadata.is_expired() or key_metadata.is_usage_exceeded():
                self._rotate_key(key_id)
                key_bytes, key_metadata = self.keys[key_id]
                
            # Encrypt based on algorithm
            if key_metadata.algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = self._encrypt_fernet(data, key_bytes)
            elif key_metadata.algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = self._encrypt_aes_gcm(data, key_bytes)
            elif key_metadata.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data = self._encrypt_chacha20_poly1305(data, key_bytes)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {key_metadata.algorithm}")
                
            # Update usage count
            key_metadata.usage_count += 1
            
            # Create encrypted package
            encrypted_package = {
                'encrypted_data': base64.b64encode(encrypted_data).decode('ascii'),
                'key_id': key_id,
                'algorithm': key_metadata.algorithm.value,
                'security_level': key_metadata.security_level.value,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '1.0'
            }
            
            if self.audit_encryption_operations:
                logger.debug(f"Encrypted data with key {key_id}")
                
            return encrypted_package
            
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            return None
            
    def decrypt_data(self, encrypted_package: Dict[str, Any]) -> Optional[bytes]:
        """
        Decrypt data from encrypted package
        
        Args:
            encrypted_package: Encrypted data package
            
        Returns:
            Decrypted data
        """
        try:
            # Extract package components
            encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
            key_id = encrypted_package['key_id']
            algorithm = EncryptionAlgorithm(encrypted_package['algorithm'])
            
            # Get key
            if key_id not in self.keys:
                raise ValueError(f"Decryption key not found: {key_id}")
                
            key_bytes, key_metadata = self.keys[key_id]
            
            # Check key validity
            if key_metadata.is_expired():
                raise ValueError(f"Decryption key expired: {key_id}")
                
            # Decrypt based on algorithm
            if algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = self._decrypt_fernet(encrypted_data, key_bytes)
            elif algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = self._decrypt_aes_gcm(encrypted_data, key_bytes)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = self._decrypt_chacha20_poly1305(encrypted_data, key_bytes)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {algorithm}")
                
            # Update usage count
            key_metadata.usage_count += 1
            
            if self.audit_encryption_operations:
                logger.debug(f"Decrypted data with key {key_id}")
                
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            return None
            
    def _encrypt_fernet(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using Fernet"""
        f = Fernet(key)
        return f.encrypt(data)
        
    def _decrypt_fernet(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using Fernet"""
        f = Fernet(key)
        return f.decrypt(encrypted_data)
        
    def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-GCM"""
        # Generate random nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Combine nonce + tag + ciphertext
        return nonce + encryptor.tag + ciphertext
        
    def _decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-GCM"""
        # Extract components
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
        
    def _encrypt_chacha20_poly1305(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using ChaCha20-Poly1305"""
        # Generate random nonce
        nonce = secrets.token_bytes(12)  # 96-bit nonce
        
        # Create cipher
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()
        
        # For ChaCha20-Poly1305, we need to use AEAD
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        aead = ChaCha20Poly1305(key)
        ciphertext = aead.encrypt(nonce, data, None)
        
        # Combine nonce + ciphertext
        return nonce + ciphertext
        
    def _decrypt_chacha20_poly1305(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        # Extract components
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Create AEAD cipher
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        aead = ChaCha20Poly1305(key)
        return aead.decrypt(nonce, ciphertext, None)
        
    def encrypt_rsa(self, data: bytes, public_key_id: str) -> Optional[bytes]:
        """
        Encrypt data using RSA public key
        
        Args:
            data: Data to encrypt
            public_key_id: Public key identifier
            
        Returns:
            Encrypted data
        """
        try:
            if public_key_id not in self.keys:
                raise ValueError(f"Public key not found: {public_key_id}")
                
            public_key_pem, key_metadata = self.keys[public_key_id]
            
            # Load public key
            public_key = serialization.load_pem_public_key(public_key_pem, backend=default_backend())
            
            # Encrypt data
            encrypted_data = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Update usage count
            key_metadata.usage_count += 1
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"RSA encryption failed: {e}")
            return None
            
    def decrypt_rsa(self, encrypted_data: bytes, private_key_id: str) -> Optional[bytes]:
        """
        Decrypt data using RSA private key
        
        Args:
            encrypted_data: Encrypted data
            private_key_id: Private key identifier
            
        Returns:
            Decrypted data
        """
        try:
            if private_key_id not in self.keys:
                raise ValueError(f"Private key not found: {private_key_id}")
                
            private_key_pem, key_metadata = self.keys[private_key_id]
            
            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem, 
                password=None, 
                backend=default_backend()
            )
            
            # Decrypt data
            decrypted_data = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Update usage count
            key_metadata.usage_count += 1
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"RSA decryption failed: {e}")
            return None
            
    def create_jwt_token(self, payload: Dict[str, Any], expires_minutes: int = 60) -> Optional[str]:
        """
        Create JWT token for secure authentication
        
        Args:
            payload: Token payload
            expires_minutes: Token expiration in minutes
            
        Returns:
            JWT token string
        """
        try:
            # Add standard claims
            now = datetime.now(timezone.utc)
            payload.update({
                'iat': now,
                'exp': now + timedelta(minutes=expires_minutes),
                'iss': 'ainflue-distribution'
            })
            
            # Create token
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            
            logger.debug("JWT token created")
            return token
            
        except Exception as e:
            logger.error(f"JWT token creation failed: {e}")
            return None
            
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            logger.debug("JWT token verified")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT token invalid: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT token verification failed: {e}")
            return None
            
    def hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Hash password using PBKDF2
        
        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hash, salt)
        """
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            password_hash = kdf.derive(password.encode('utf-8'))
            return password_hash, salt
            
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            return b'', b''
            
    def verify_password(self, password: str, password_hash: bytes, salt: bytes) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Password to verify
            password_hash: Stored password hash
            salt: Password salt
            
        Returns:
            True if password matches
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            kdf.verify(password.encode('utf-8'), password_hash)
            return True
            
        except Exception:
            return False
            
    def _rotate_key(self, key_id: str) -> bool:
        """
        Rotate encryption key
        
        Args:
            key_id: Key to rotate
            
        Returns:
            Success status
        """
        try:
            if key_id not in self.keys:
                return False
                
            old_key_bytes, old_metadata = self.keys[key_id]
            
            # Generate new key with same parameters
            success = self.generate_key(
                key_id=key_id,
                key_type=old_metadata.key_type,
                algorithm=old_metadata.algorithm,
                security_level=old_metadata.security_level
            )
            
            if success:
                logger.info(f"Rotated encryption key: {key_id}")
                
                # Securely delete old key if required
                if self.require_secure_delete:
                    self._secure_delete_key(old_key_bytes)
                    
            return success
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            return False
            
    def _secure_delete_key(self, key_bytes -> None: bytes) -> None:
        """Securely delete key from memory"""
        # Overwrite key bytes with random data
        if isinstance(key_bytes, bytes):
            # This is a basic approach - in production, use more secure methods
            del key_bytes
            
    async def rotate_expired_keys(self) -> None:
        """Rotate all expired keys"""
        expired_keys = [
            key_id for key_id, (_, metadata) in self.keys.items()
            if metadata.is_expired() or metadata.is_usage_exceeded()
        ]
        
        for key_id in expired_keys:
            self._rotate_key(key_id)
            
        if expired_keys:
            logger.info(f"Rotated {len(expired_keys)} expired keys")
            
    def get_key_status(self) -> Dict[str, Any]:
        """Get status of all keys"""
        status = {
            'total_keys': len(self.keys),
            'active_keys': 0,
            'expired_keys': 0,
            'keys_near_expiry': 0,
            'keys_near_usage_limit': 0,
            'keys_by_type': {},
            'keys_by_algorithm': {},
            'keys_by_security_level': {}
        }
        
        now = datetime.now(timezone.utc)
        near_expiry_threshold = now + timedelta(days=7)  # 7 days warning
        
        for key_id, (_, metadata) in self.keys.items():
            # Count by status
            if metadata.is_active and not metadata.is_expired():
                status['active_keys'] += 1
            
            if metadata.is_expired():
                status['expired_keys'] += 1
                
            if metadata.expires_at and metadata.expires_at <= near_expiry_threshold:
                status['keys_near_expiry'] += 1
                
            if metadata.max_usage and metadata.usage_count >= metadata.max_usage * 0.9:
                status['keys_near_usage_limit'] += 1
                
            # Count by type
            key_type = metadata.key_type.value
            status['keys_by_type'][key_type] = status['keys_by_type'].get(key_type, 0) + 1
            
            # Count by algorithm
            algorithm = metadata.algorithm.value
            status['keys_by_algorithm'][algorithm] = status['keys_by_algorithm'].get(algorithm, 0) + 1
            
            # Count by security level
            security_level = metadata.security_level.value
            status['keys_by_security_level'][security_level] = status['keys_by_security_level'].get(security_level, 0) + 1
            
        return status
        
    def export_public_keys(self) -> Dict[str, str]:
        """Export all public keys for sharing"""
        public_keys = {}
        
        for key_id, (key_bytes, metadata) in self.keys.items():
            if metadata.key_type == KeyType.ASYMMETRIC_PUBLIC:
                public_keys[key_id] = base64.b64encode(key_bytes).decode('ascii')
                
        return public_keys
        
    def import_public_key(self, key_id: str, public_key_data: str, 
                         algorithm: EncryptionAlgorithm, security_level: SecurityLevel) -> bool:
        """
        Import public key from external source
        
        Args:
            key_id: Key identifier
            public_key_data: Base64-encoded public key
            algorithm: Key algorithm
            security_level: Security level
            
        Returns:
            Success status
        """
        try:
            key_bytes = base64.b64decode(public_key_data)
            
            # Verify it's a valid public key
            serialization.load_pem_public_key(key_bytes, backend=default_backend())
            
            # Create metadata
            metadata = EncryptionKey(
                key_id=key_id,
                key_type=KeyType.ASYMMETRIC_PUBLIC,
                algorithm=algorithm,
                security_level=security_level,
                created_at=datetime.now(timezone.utc)
            )
            
            # Store key
            self.keys[key_id] = (key_bytes, metadata)
            
            logger.info(f"Imported public key: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Public key import failed: {e}")
            return False


# Export main classes
__all__ = [
    'EncryptionManager',
    'EncryptionKey',
    'EncryptionAlgorithm',
    'KeyType',
    'SecurityLevel'
]