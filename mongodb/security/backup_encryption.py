"""Backup Encryption for MongoDB
==============================

Encrypted backup management with secure key handling,
compression, and integrity verification.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import os
import gzip
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class BackupEncryption:
    """Encrypted backup management system."""
    
    def __init__(self, encryption_key -> None: Optional[str] = None) -> None:
        """Initialize backup encryption."""
        self._encryption_key = encryption_key or self._generate_key()
        self._fernet = Fernet(self._encryption_key.encode() if isinstance(self._encryption_key, str) else self._encryption_key)
    
    def _generate_key(self) -> bytes:
        """Generate encryption key for backups."""
        # Use environment variable or generate new key
        env_key = os.getenv('AINFLUE_BACKUP_KEY')
        if env_key:
            return env_key.encode()
        
        # Generate new key
        new_key = Fernet.generate_key()
        logger.warning("Generated new backup encryption key - store in AINFLUE_BACKUP_KEY environment variable")
        return new_key
    
    def encrypt_backup(self, backup_data: bytes, compress: bool = True) -> Dict[str, Any]:
        """Encrypt backup data."""
        try:
            # Compress if requested
            if compress:
                compressed_data = gzip.compress(backup_data)
                logger.info(f"Compressed backup from {len(backup_data)} to {len(compressed_data)} bytes")
            else:
                compressed_data = backup_data
            
            # Encrypt
            encrypted_data = self._fernet.encrypt(compressed_data)
            
            # Calculate checksums
            original_checksum = hashlib.sha256(backup_data).hexdigest()
            encrypted_checksum = hashlib.sha256(encrypted_data).hexdigest()
            
            return {
                "encrypted_data": encrypted_data,
                "compressed": compress,
                "original_size": len(backup_data),
                "encrypted_size": len(encrypted_data),
                "original_checksum": original_checksum,
                "encrypted_checksum": encrypted_checksum,
                "encryption_algorithm": "Fernet",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to encrypt backup: {e}")
            raise
    
    def decrypt_backup(self, backup_metadata: Dict[str, Any]) -> bytes:
        """Decrypt backup data."""
        try:
            encrypted_data = backup_metadata["encrypted_data"]
            compressed = backup_metadata.get("compressed", False)
            
            # Verify encrypted data checksum
            if "encrypted_checksum" in backup_metadata:
                expected_checksum = backup_metadata["encrypted_checksum"]
                actual_checksum = hashlib.sha256(encrypted_data).hexdigest()
                if expected_checksum != actual_checksum:
                    raise ValueError("Encrypted backup checksum mismatch")
            
            # Decrypt
            decrypted_data = self._fernet.decrypt(encrypted_data)
            
            # Decompress if needed
            if compressed:
                original_data = gzip.decompress(decrypted_data)
            else:
                original_data = decrypted_data
            
            # Verify original data checksum
            if "original_checksum" in backup_metadata:
                expected_checksum = backup_metadata["original_checksum"]
                actual_checksum = hashlib.sha256(original_data).hexdigest()
                if expected_checksum != actual_checksum:
                    raise ValueError("Original backup checksum mismatch")
            
            return original_data
            
        except Exception as e:
            logger.error(f"Failed to decrypt backup: {e}")
            raise

# Global backup encryption instance
_default_encryption: Optional[BackupEncryption] = None

def get_backup_encryption() -> BackupEncryption:
    """Get or create default backup encryption."""
    global _default_encryption
    if _default_encryption is None:
        _default_encryption = BackupEncryption()
    return _default_encryption

__all__ = ['BackupEncryption', 'get_backup_encryption']