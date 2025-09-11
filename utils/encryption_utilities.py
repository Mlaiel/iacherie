"""
Encryption Utilities - Security Expert Implementation
====================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade encryption and security utilities implementing industry standards.
"""

import base64
import hashlib
import hmac
import secrets
import logging
from typing import Dict, Any, Optional, Union, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import bcrypt
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EncryptionUtilities:
    """
    Enterprise security implementation covering:
    - Symmetric and asymmetric encryption
    - Password hashing and verification
    - JWT token management
    - Digital signatures
    - Secure key generation and management
    """
    
    def __init__(self):
        """Initialize encryption utilities with security best practices"""
        self.algorithm = 'HS256'
        self.token_expiry = 3600  # 1 hour default
        
        # Generate master key for this session (in production, load from secure storage)
        self._master_key = self._generate_master_key()
        
        logger.info("EncryptionUtilities initialized with enterprise security")
    
    def _generate_master_key(self) -> bytes:
        """Generate a secure master key"""
        return secrets.token_bytes(32)  # 256-bit key
    
    def generate_fernet_key(self) -> str:
        """Generate a Fernet key for symmetric encryption"""
        key = Fernet.generate_key()
        logger.debug("Generated new Fernet key")
        return key.decode()
    
    def encrypt_symmetric(self, data: str, key: Optional[str] = None) -> str:
        """
        Encrypt data using symmetric encryption (Fernet)
        Returns base64-encoded encrypted data
        """
        try:
            if key is None:
                key = self.generate_fernet_key()
            
            fernet = Fernet(key.encode() if isinstance(key, str) else key)
            encrypted_data = fernet.encrypt(data.encode())
            
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Symmetric encryption failed: {e}")
            raise
    
    def decrypt_symmetric(self, encrypted_data: str, key: str) -> str:
        """
        Decrypt data using symmetric encryption (Fernet)
        """
        try:
            fernet = Fernet(key.encode() if isinstance(key, str) else key)
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Symmetric decryption failed: {e}")
            raise
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[str, str]:
        """
        Generate RSA public/private key pair
        Returns (private_key_pem, public_key_pem)
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            
            # Serialize private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Serialize public key
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            logger.info(f"Generated RSA keypair ({key_size} bits)")
            return private_pem.decode(), public_pem.decode()
            
        except Exception as e:
            logger.error(f"RSA keypair generation failed: {e}")
            raise
    
    def encrypt_asymmetric(self, data: str, public_key_pem: str) -> str:
        """Encrypt data using RSA public key"""
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
            
            encrypted_data = public_key.encrypt(
                data.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Asymmetric encryption failed: {e}")
            raise
    
    def decrypt_asymmetric(self, encrypted_data: str, private_key_pem: str) -> str:
        """Decrypt data using RSA private key"""
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
            
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = private_key.decrypt(
                decoded_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Asymmetric decryption failed: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt(rounds=12)  # Strong salt
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()
            
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def generate_jwt_token(self, payload: Dict[str, Any], 
                          secret_key: Optional[str] = None,
                          expiry_hours: int = 1) -> str:
        """Generate JWT token with payload"""
        try:
            if secret_key is None:
                secret_key = base64.b64encode(self._master_key).decode()
            
            # Add expiration and issued at claims
            payload.update({
                'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
                'iat': datetime.utcnow(),
                'iss': 'ainflue-platform'
            })
            
            token = jwt.encode(payload, secret_key, algorithm=self.algorithm)
            logger.debug("Generated JWT token")
            return token
            
        except Exception as e:
            logger.error(f"JWT token generation failed: {e}")
            raise
    
    def verify_jwt_token(self, token: str, secret_key: Optional[str] = None) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            if secret_key is None:
                secret_key = base64.b64encode(self._master_key).decode()
            
            payload = jwt.decode(token, secret_key, algorithms=[self.algorithm])
            logger.debug("JWT token verified successfully")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            raise
        except Exception as e:
            logger.error(f"JWT token verification failed: {e}")
            raise
    
    def create_hmac_signature(self, data: str, secret: str) -> str:
        """Create HMAC signature for data integrity"""
        try:
            signature = hmac.new(
                secret.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return signature
            
        except Exception as e:
            logger.error(f"HMAC signature creation failed: {e}")
            raise
    
    def verify_hmac_signature(self, data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature"""
        try:
            expected_signature = self.create_hmac_signature(data, secret)
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"HMAC signature verification failed: {e}")
            return False
    
    def hash_data(self, data: str, algorithm: str = 'sha256') -> str:
        """Hash data using specified algorithm"""
        try:
            if algorithm == 'sha256':
                return hashlib.sha256(data.encode()).hexdigest()
            elif algorithm == 'sha512':
                return hashlib.sha512(data.encode()).hexdigest()
            elif algorithm == 'md5':
                return hashlib.md5(data.encode()).hexdigest()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Data hashing failed: {e}")
            raise
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        Returns (key, salt)
        """
        try:
            if salt is None:
                salt = secrets.token_bytes(32)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = kdf.derive(password.encode())
            return key, salt
            
        except Exception as e:
            logger.error(f"Key derivation failed: {e}")
            raise
    
    def encrypt_file_content(self, content: bytes, password: str) -> Tuple[bytes, bytes]:
        """
        Encrypt file content with password
        Returns (encrypted_content, salt)
        """
        try:
            # Derive key from password
            key, salt = self.derive_key_from_password(password)
            
            # Encrypt using AES
            iv = secrets.token_bytes(16)  # AES block size
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
            encryptor = cipher.encryptor()
            
            encrypted_content = iv + encryptor.update(content) + encryptor.finalize()
            
            return encrypted_content, salt
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file_content(self, encrypted_content: bytes, password: str, salt: bytes) -> bytes:
        """Decrypt file content with password"""
        try:
            # Derive key from password and salt
            key, _ = self.derive_key_from_password(password, salt)
            
            # Extract IV and encrypted data
            iv = encrypted_content[:16]
            encrypted_data = encrypted_content[16:]
            
            # Decrypt using AES
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
            decryptor = cipher.decryptor()
            
            decrypted_content = decryptor.update(encrypted_data) + decryptor.finalize()
            
            return decrypted_content
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise
    
    def generate_api_key(self, prefix: str = "ak", length: int = 32) -> str:
        """Generate secure API key with prefix"""
        random_part = secrets.token_urlsafe(length)
        return f"{prefix}_{random_part}"
    
    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        """Mask sensitive data for logging"""
        if len(data) <= visible_chars * 2:
            return "*" * len(data)
        
        return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]


# Global instance for easy access
encryption_utils = EncryptionUtilities()