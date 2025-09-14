"""Field-Level Encryption Manager for MongoDB
==========================================

Enterprise-grade field-level encryption for sensitive data protection
with key rotation, multiple encryption algorithms, and performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTED:
- Security Engineer: AES-256 encryption with key rotation
- DBA: Field-level encryption for sensitive data
- DevOps: Performance-optimized encryption/decryption
"""

import os
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import json

logger = logging.getLogger(__name__)

@dataclass
class EncryptionKey:
    """Encryption key metadata."""
    key_id: str
    key_data: bytes
    algorithm: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: str = "active"  # active, rotated, expired

class EncryptionManager:
    """Advanced field-level encryption manager."""
    
    def __init__(self) -> None:
        """Initialize encryption manager."""
        self._keys: Dict[str, EncryptionKey] = {}
        self._current_key_id: Optional[str] = None
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes
        self._sensitive_fields = {
            'email', 'phone', 'ssn', 'credit_card', 'bank_account',
            'passport', 'license', 'address', 'personal_id', 'tax_id',
            'medical_record', 'payment_info', 'api_key', 'token',
            'password_hash', 'secret', 'private_key'
        }
        
        # Initialize master key from environment or generate
        self._initialize_master_key()
    
    def _initialize_master_key(self) -> None:
        """Initialize or generate master encryption key."""
        master_key = os.getenv('AINFLUE_MASTER_KEY')
        if not master_key:
            # Generate new master key
            master_key = Fernet.generate_key().decode()
            logger.warning("Generated new master key - store in AINFLUE_MASTER_KEY environment variable")
        
        self._master_fernet = Fernet(master_key.encode())
        
        # Create default encryption key
        self._create_default_key()
    
    def _create_default_key(self) -> None:
        """Create default encryption key."""
        key_id = "default_v1"
        key_data = Fernet.generate_key()
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            algorithm="Fernet",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365)
        )
        
        self._keys[key_id] = encryption_key
        self._current_key_id = key_id
        logger.info(f"Created default encryption key: {key_id}")
    
    def generate_key(self, algorithm: str = "Fernet", expires_days: int = 365) -> str:
        """Generate new encryption key."""
        key_id = f"{algorithm}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        if algorithm == "Fernet":
            key_data = Fernet.generate_key()
        elif algorithm == "AES256":
            key_data = secrets.token_bytes(32)  # 256 bits
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_data=key_data,
            algorithm=algorithm,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=expires_days)
        )
        
        self._keys[key_id] = encryption_key
        logger.info(f"Generated new encryption key: {key_id}")
        
        return key_id
    
    def rotate_key(self, old_key_id: Optional[str] = None) -> str:
        """Rotate encryption key."""
        if old_key_id is None:
            old_key_id = self._current_key_id
        
        if old_key_id and old_key_id in self._keys:
            # Mark old key as rotated
            self._keys[old_key_id].status = "rotated"
        
        # Generate new key
        new_key_id = self.generate_key()
        self._current_key_id = new_key_id
        
        logger.info(f"Rotated key from {old_key_id} to {new_key_id}")
        return new_key_id
    
    def encrypt_field(self, value: Any, field_name: str = None, key_id: str = None) -> Dict[str, Any]:
        """Encrypt a field value."""
        if value is None:
            return {"encrypted": False, "value": None}
        
        # Check if field should be encrypted
        if field_name and not self._should_encrypt_field(field_name):
            return {"encrypted": False, "value": value}
        
        try:
            # Use specified key or current key
            key_id = key_id or self._current_key_id
            if key_id not in self._keys:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            encryption_key = self._keys[key_id]
            
            # Convert value to string for encryption
            if isinstance(value, (dict, list)):
                plaintext = json.dumps(value).encode()
            else:
                plaintext = str(value).encode()
            
            # Encrypt based on algorithm
            if encryption_key.algorithm == "Fernet":
                fernet = Fernet(encryption_key.key_data)
                ciphertext = fernet.encrypt(plaintext)
            elif encryption_key.algorithm == "AES256":
                # Generate random IV
                iv = secrets.token_bytes(16)
                cipher = Cipher(algorithms.AES(encryption_key.key_data), modes.CBC(iv))
                encryptor = cipher.encryptor()
                
                # Pad plaintext to multiple of 16 bytes
                padding_length = 16 - (len(plaintext) % 16)
                padded_plaintext = plaintext + bytes([padding_length] * padding_length)
                
                ciphertext = iv + encryptor.update(padded_plaintext) + encryptor.finalize()
            else:
                raise ValueError(f"Unsupported algorithm: {encryption_key.algorithm}")
            
            # Return encrypted metadata
            return {
                "encrypted": True,
                "value": base64.b64encode(ciphertext).decode(),
                "key_id": key_id,
                "algorithm": encryption_key.algorithm,
                "encrypted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to encrypt field {field_name}: {e}")
            # Return unencrypted as fallback
            return {"encrypted": False, "value": value, "error": str(e)}
    
    def decrypt_field(self, encrypted_data: Dict[str, Any]) -> Any:
        """Decrypt a field value."""
        if not encrypted_data.get("encrypted", False):
            return encrypted_data.get("value")
        
        try:
            key_id = encrypted_data["key_id"]
            algorithm = encrypted_data["algorithm"]
            ciphertext = base64.b64decode(encrypted_data["value"])
            
            if key_id not in self._keys:
                raise ValueError(f"Decryption key not found: {key_id}")
            
            encryption_key = self._keys[key_id]
            
            # Decrypt based on algorithm
            if algorithm == "Fernet":
                fernet = Fernet(encryption_key.key_data)
                plaintext = fernet.decrypt(ciphertext)
            elif algorithm == "AES256":
                # Extract IV (first 16 bytes)
                iv = ciphertext[:16]
                actual_ciphertext = ciphertext[16:]
                
                cipher = Cipher(algorithms.AES(encryption_key.key_data), modes.CBC(iv))
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
                
                # Remove padding
                padding_length = padded_plaintext[-1]
                plaintext = padded_plaintext[:-padding_length]
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Convert back to original type
            try:
                # Try to parse as JSON first
                return json.loads(plaintext.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Return as string
                return plaintext.decode()
                
        except Exception as e:
            logger.error(f"Failed to decrypt field: {e}")
            return None
    
    def encrypt_document(self, document: Dict[str, Any], 
                        encryption_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Encrypt sensitive fields in a document."""
        if not document:
            return document
        
        encrypted_doc = {}
        for field_name, value in document.items():
            if self._should_encrypt_field(field_name, encryption_policy):
                encrypted_doc[field_name] = self.encrypt_field(value, field_name)
            else:
                encrypted_doc[field_name] = value
        
        # Add encryption metadata
        encrypted_doc["_encryption_metadata"] = {
            "encrypted_fields": [
                field for field in document.keys() 
                if self._should_encrypt_field(field, encryption_policy)
            ],
            "encrypted_at": datetime.utcnow().isoformat(),
            "key_id": self._current_key_id
        }
        
        return encrypted_doc
    
    def decrypt_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt encrypted fields in a document."""
        if not document:
            return document
        
        decrypted_doc = {}
        for field_name, value in document.items():
            if field_name == "_encryption_metadata":
                continue  # Skip metadata
            
            if isinstance(value, dict) and value.get("encrypted", False):
                decrypted_doc[field_name] = self.decrypt_field(value)
            else:
                decrypted_doc[field_name] = value
        
        return decrypted_doc
    
    def _should_encrypt_field(self, field_name: str, 
                             encryption_policy: Optional[Dict[str, Any]] = None) -> bool:
        """Determine if a field should be encrypted."""
        if encryption_policy:
            # Check explicit policy
            if "encrypt" in encryption_policy:
                return field_name in encryption_policy["encrypt"]
            if "exclude" in encryption_policy:
                return field_name not in encryption_policy["exclude"]
        
        # Check against sensitive fields
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self._sensitive_fields)
    
    def get_key_info(self, key_id: str = None) -> Dict[str, Any]:
        """Get encryption key information."""
        key_id = key_id or self._current_key_id
        if key_id not in self._keys:
            return {"error": f"Key not found: {key_id}"}
        
        key = self._keys[key_id]
        return {
            "key_id": key.key_id,
            "algorithm": key.algorithm,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "status": key.status,
            "is_current": key_id == self._current_key_id
        }
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all encryption keys."""
        return [self.get_key_info(key_id) for key_id in self._keys.keys()]
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired keys."""
        now = datetime.utcnow()
        expired_keys = []
        
        for key_id, key in self._keys.items():
            if key.expires_at and key.expires_at < now and key.status != "active":
                expired_keys.append(key_id)
        
        for key_id in expired_keys:
            del self._keys[key_id]
            
        logger.info(f"Cleaned up {len(expired_keys)} expired keys")
        return len(expired_keys)

# Global encryption manager instance
_default_manager: Optional[EncryptionManager] = None

def get_encryption_manager() -> EncryptionManager:
    """Get or create default encryption manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = EncryptionManager()
    return _default_manager

# Export main classes and functions
__all__ = [
    'EncryptionKey',
    'EncryptionManager',
    'get_encryption_manager'
]