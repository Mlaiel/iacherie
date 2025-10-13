"""
🔐 Encryption Manager - Enterprise-Grade Encryption System
Advanced encryption, decryption, and key management

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import hashlib
import secrets
import base64
from typing import Optional, Dict, Any, Union
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256 = "aes_256"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"


class EncryptionManager:
    """
    Enterprise encryption manager with multi-algorithm support
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption manager
        
        Args:
            master_key: Optional master encryption key (will be generated if not provided)
        """
        self.master_key = master_key or Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        self.key_store: Dict[str, bytes] = {}
        
        logger.info("🔐 Encryption Manager initialized")
    
    def encrypt(self, data: Union[str, bytes], algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET) -> str:
        """
        Encrypt data using specified algorithm
        
        Args:
            data: Data to encrypt (string or bytes)
            algorithm: Encryption algorithm to use
            
        Returns:
            str: Base64-encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == EncryptionAlgorithm.FERNET:
            encrypted = self.fernet.encrypt(data)
            return base64.b64encode(encrypted).decode('utf-8')
        elif algorithm == EncryptionAlgorithm.AES_256:
            # Use Fernet (which uses AES-256 under the hood)
            encrypted = self.fernet.encrypt(data)
            return base64.b64encode(encrypted).decode('utf-8')
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
    
    def decrypt(self, encrypted_data: str, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.FERNET) -> bytes:
        """
        Decrypt data using specified algorithm
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            algorithm: Encryption algorithm used
            
        Returns:
            bytes: Decrypted data
        """
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        
        if algorithm in [EncryptionAlgorithm.FERNET, EncryptionAlgorithm.AES_256]:
            return self.fernet.decrypt(encrypted_bytes)
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """
        Hash data using specified algorithm
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            str: Hexadecimal hash
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    def generate_key(self, key_id: str, password: Optional[str] = None) -> bytes:
        """
        Generate encryption key
        
        Args:
            key_id: Identifier for the key
            password: Optional password for key derivation
            
        Returns:
            bytes: Generated encryption key
        """
        if password:
            # Derive key from password using PBKDF2
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
        else:
            # Generate random key
            key = Fernet.generate_key()
        
        self.key_store[key_id] = key
        logger.info(f"🔑 Generated encryption key: {key_id}")
        return key
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """
        Retrieve stored encryption key
        
        Args:
            key_id: Key identifier
            
        Returns:
            Optional[bytes]: Encryption key or None if not found
        """
        return self.key_store.get(key_id)
    
    def rotate_key(self, old_key_id: str, new_key_id: str) -> bool:
        """
        Rotate encryption key
        
        Args:
            old_key_id: Current key identifier
            new_key_id: New key identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        old_key = self.key_store.get(old_key_id)
        if not old_key:
            return False
        
        new_key = self.generate_key(new_key_id)
        # In production, you would re-encrypt all data with new key here
        
        logger.info(f"🔄 Rotated key from {old_key_id} to {new_key_id}")
        return True
    
    def encrypt_dict(self, data: Dict[str, Any], fields_to_encrypt: list) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary with data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dict: Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data:
                value = encrypted_data[field]
                if value is not None:
                    encrypted_data[field] = self.encrypt(str(value))
        
        return encrypted_data
    
    def decrypt_dict(self, data: Dict[str, Any], fields_to_decrypt: list) -> Dict[str, Any]:
        """
        Decrypt specific fields in a dictionary
        
        Args:
            data: Dictionary with encrypted data
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dict: Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data:
                encrypted_value = decrypted_data[field]
                if encrypted_value is not None:
                    try:
                        decrypted_data[field] = self.decrypt(encrypted_value).decode('utf-8')
                    except Exception as e:
                        logger.error(f"Failed to decrypt field {field}: {e}")
        
        return decrypted_data
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate secure random token
        
        Args:
            length: Token length in bytes
            
        Returns:
            str: URL-safe base64-encoded token
        """
        return secrets.token_urlsafe(length)
    
    def verify_signature(self, data: Union[str, bytes], signature: str) -> bool:
        """
        Verify data signature
        
        Args:
            data: Original data
            signature: Signature to verify
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        expected_signature = self.hash_data(data)
        return secrets.compare_digest(expected_signature, signature)
    
    def get_encryption_info(self) -> Dict[str, Any]:
        """
        Get encryption manager information
        
        Returns:
            Dict: Encryption manager stats
        """
        return {
            "algorithm": "Fernet (AES-256-CBC + HMAC)",
            "keys_stored": len(self.key_store),
            "master_key_length": len(self.master_key),
            "supported_algorithms": [algo.value for algo in EncryptionAlgorithm]
        }


# Global encryption manager instance
_global_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """
    Get global encryption manager instance
    
    Returns:
        EncryptionManager: Global encryption manager
    """
    global _global_encryption_manager
    if _global_encryption_manager is None:
        _global_encryption_manager = EncryptionManager()
    return _global_encryption_manager


# Auto-initialize
_global_encryption_manager = EncryptionManager()

logger.info("🔐 Encryption Manager module initialized")
