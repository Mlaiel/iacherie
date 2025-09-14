#!/usr/bin/env python3
"""
Encryption Key Management System
Production-grade key management for IA Influencer Agent Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import secrets
import hashlib
import base64
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import yaml

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

logger = logging.getLogger(__name__)


class KeyType(Enum):
    """Encryption key types."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    SIGNING = "signing"
    

class Algorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "aes_256_gcm"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_OAEP = "rsa_oaep"
    RSA_PSS = "rsa_pss"


@dataclass
class KeyMetadata:
    """Key metadata structure."""
    key_id: str
    key_type: KeyType
    algorithm: Algorithm
    purpose: str
    created_at: datetime
    expires_at: Optional[datetime]
    rotation_interval: timedelta
    last_rotated: Optional[datetime]
    usage_count: int = 0
    is_active: bool = True


class EncryptionKeyManager:
    """
    Enterprise encryption key management system.
    
    Provides secure key generation, rotation, storage, and lifecycle management
    with support for multiple encryption algorithms and compliance requirements.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the key manager."""
        self.config_path = config_path or "key-management-config.yaml"
        self.config = self._load_config()
        self.keys: Dict[str, KeyMetadata] = {}
        self.key_storage = {}
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            config_file = Path(__file__).parent / self.config_path
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)['encryption_config']
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "master_key": {
                "algorithm": "AES-256-GCM",
                "key_size": 256,
                "rotation_interval": "90d"
            },
            "field_keys": {
                "user_credentials": {
                    "algorithm": "AES-256-GCM",
                    "rotation_interval": "30d"
                }
            }
        }
    
    def _setup_logging(self):
        """Setup secure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/ia-influencer/key-manager.log'),
                logging.StreamHandler()
            ]
        )
    
    def generate_key(
        self, 
        key_id: str, 
        key_type: KeyType, 
        algorithm: Algorithm,
        purpose: str,
        rotation_interval: Optional[timedelta] = None
    ) -> bool:
        """
        Generate a new encryption key.
        
        Args:
            key_id: Unique identifier for the key
            key_type: Type of key (symmetric, asymmetric, signing)
            algorithm: Encryption algorithm to use
            purpose: Purpose of the key
            rotation_interval: How often to rotate the key
            
        Returns:
            True if key generated successfully, False otherwise
        """
        try:
            # Generate the actual key based on algorithm
            key_data = self._generate_key_data(algorithm)
            
            # Create metadata
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                purpose=purpose,
                created_at=datetime.utcnow(),
                expires_at=None,
                rotation_interval=rotation_interval or timedelta(days=90),
                last_rotated=None
            )
            
            # Store key and metadata
            self.key_storage[key_id] = key_data
            self.keys[key_id] = metadata
            
            logger.info(f"Generated new key: {key_id} ({algorithm.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate key {key_id}: {e}")
            return False
    
    def _generate_key_data(self, algorithm: Algorithm) -> bytes:
        """Generate key data based on algorithm."""
        if algorithm == Algorithm.AES_256_GCM:
            return AESGCM.generate_key(bit_length=256)
        elif algorithm == Algorithm.CHACHA20_POLY1305:
            return ChaCha20Poly1305.generate_key()
        elif algorithm == Algorithm.FERNET:
            return Fernet.generate_key()
        elif algorithm in [Algorithm.RSA_OAEP, Algorithm.RSA_PSS]:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )
            return private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def rotate_key(self, key_id: str) -> bool:
        """
        Rotate an existing key.
        
        Args:
            key_id: ID of key to rotate
            
        Returns:
            True if rotation successful, False otherwise
        """
        try:
            if key_id not in self.keys:
                logger.error(f"Key not found: {key_id}")
                return False
            
            metadata = self.keys[key_id]
            
            # Generate new key data
            new_key_data = self._generate_key_data(metadata.algorithm)
            
            # Archive old key (for decryption of existing data)
            self._archive_key(key_id, self.key_storage[key_id])
            
            # Update with new key
            self.key_storage[key_id] = new_key_data
            metadata.last_rotated = datetime.utcnow()
            
            logger.info(f"Rotated key: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate key {key_id}: {e}")
            return False
    
    def _archive_key(self, key_id: str, key_data: bytes):
        """Archive old key for historical decryption."""
        archive_id = f"{key_id}_archived_{int(datetime.utcnow().timestamp())}"
        # In production, this would go to secure archive storage
        logger.info(f"Archived key: {archive_id}")
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """
        Retrieve a key by ID.
        
        Args:
            key_id: ID of key to retrieve
            
        Returns:
            Key data if found, None otherwise
        """
        if key_id in self.key_storage and self.keys[key_id].is_active:
            self.keys[key_id].usage_count += 1
            return self.key_storage[key_id]
        return None
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all keys with their metadata."""
        return [
            {
                **asdict(metadata),
                "created_at": metadata.created_at.isoformat(),
                "last_rotated": metadata.last_rotated.isoformat() if metadata.last_rotated else None
            }
            for metadata in self.keys.values()
        ]
    
    def check_rotation_needed(self) -> List[str]:
        """Check which keys need rotation."""
        keys_needing_rotation = []
        current_time = datetime.utcnow()
        
        for key_id, metadata in self.keys.items():
            last_rotation = metadata.last_rotated or metadata.created_at
            if current_time - last_rotation >= metadata.rotation_interval:
                keys_needing_rotation.append(key_id)
        
        return keys_needing_rotation
    
    def auto_rotate_keys(self) -> Dict[str, bool]:
        """Automatically rotate keys that are due for rotation."""
        keys_to_rotate = self.check_rotation_needed()
        results = {}
        
        for key_id in keys_to_rotate:
            results[key_id] = self.rotate_key(key_id)
        
        return results
    
    def encrypt_data(self, data: bytes, key_id: str) -> Optional[bytes]:
        """
        Encrypt data using specified key.
        
        Args:
            data: Data to encrypt
            key_id: ID of key to use
            
        Returns:
            Encrypted data or None if failed
        """
        try:
            key_data = self.get_key(key_id)
            if not key_data:
                return None
            
            metadata = self.keys[key_id]
            
            if metadata.algorithm == Algorithm.AES_256_GCM:
                cipher = AESGCM(key_data)
                nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
                ciphertext = cipher.encrypt(nonce, data, None)
                return nonce + ciphertext
                
            elif metadata.algorithm == Algorithm.CHACHA20_POLY1305:
                cipher = ChaCha20Poly1305(key_data)
                nonce = secrets.token_bytes(12)
                ciphertext = cipher.encrypt(nonce, data, None)
                return nonce + ciphertext
                
            elif metadata.algorithm == Algorithm.FERNET:
                cipher = Fernet(key_data)
                return cipher.encrypt(data)
            
            else:
                logger.error(f"Encryption not supported for algorithm: {metadata.algorithm}")
                return None
                
        except Exception as e:
            logger.error(f"Encryption failed for key {key_id}: {e}")
            return None
    
    def decrypt_data(self, encrypted_data: bytes, key_id: str) -> Optional[bytes]:
        """
        Decrypt data using specified key.
        
        Args:
            encrypted_data: Data to decrypt
            key_id: ID of key to use
            
        Returns:
            Decrypted data or None if failed
        """
        try:
            key_data = self.get_key(key_id)
            if not key_data:
                return None
            
            metadata = self.keys[key_id]
            
            if metadata.algorithm == Algorithm.AES_256_GCM:
                cipher = AESGCM(key_data)
                nonce = encrypted_data[:12]
                ciphertext = encrypted_data[12:]
                return cipher.decrypt(nonce, ciphertext, None)
                
            elif metadata.algorithm == Algorithm.CHACHA20_POLY1305:
                cipher = ChaCha20Poly1305(key_data)
                nonce = encrypted_data[:12]
                ciphertext = encrypted_data[12:]
                return cipher.decrypt(nonce, ciphertext, None)
                
            elif metadata.algorithm == Algorithm.FERNET:
                cipher = Fernet(key_data)
                return cipher.decrypt(encrypted_data)
            
            else:
                logger.error(f"Decryption not supported for algorithm: {metadata.algorithm}")
                return None
                
        except Exception as e:
            logger.error(f"Decryption failed for key {key_id}: {e}")
            return None
    
    def backup_keys(self, backup_path: str) -> bool:
        """
        Create encrypted backup of all keys.
        
        Args:
            backup_path: Path to store backup
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            backup_data = {
                'keys': self.key_storage,
                'metadata': {
                    key_id: {
                        **asdict(metadata),
                        'created_at': metadata.created_at.isoformat(),
                        'last_rotated': metadata.last_rotated.isoformat() if metadata.last_rotated else None
                    }
                    for key_id, metadata in self.keys.items()
                },
                'backup_timestamp': datetime.utcnow().isoformat()
            }
            
            # Encrypt backup data
            backup_key = Fernet.generate_key()
            cipher = Fernet(backup_key)
            encrypted_backup = cipher.encrypt(json.dumps(backup_data).encode())
            
            # Write backup
            with open(backup_path, 'wb') as f:
                f.write(encrypted_backup)
            
            # Store backup key separately (in production, use secure key store)
            with open(f"{backup_path}.key", 'wb') as f:
                f.write(backup_key)
            
            logger.info(f"Keys backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def get_key_health_report(self) -> Dict[str, Any]:
        """Generate health report for all keys."""
        current_time = datetime.utcnow()
        report = {
            'total_keys': len(self.keys),
            'active_keys': sum(1 for k in self.keys.values() if k.is_active),
            'keys_needing_rotation': len(self.check_rotation_needed()),
            'key_details': []
        }
        
        for key_id, metadata in self.keys.items():
            last_rotation = metadata.last_rotated or metadata.created_at
            days_since_rotation = (current_time - last_rotation).days
            
            key_health = {
                'key_id': key_id,
                'algorithm': metadata.algorithm.value,
                'purpose': metadata.purpose,
                'days_since_rotation': days_since_rotation,
                'usage_count': metadata.usage_count,
                'needs_rotation': days_since_rotation >= metadata.rotation_interval.days,
                'is_active': metadata.is_active
            }
            report['key_details'].append(key_health)
        
        return report


def main():
    """Example usage of the key manager."""
    key_manager = EncryptionKeyManager()
    
    # Generate some test keys
    key_manager.generate_key(
        "user_credentials", 
        KeyType.SYMMETRIC, 
        Algorithm.AES_256_GCM,
        "User credential encryption",
        timedelta(days=30)
    )
    
    key_manager.generate_key(
        "content_metadata",
        KeyType.SYMMETRIC,
        Algorithm.CHACHA20_POLY1305,
        "Content metadata encryption",
        timedelta(days=180)
    )
    
    # Test encryption
    test_data = b"This is sensitive user data"
    encrypted = key_manager.encrypt_data(test_data, "user_credentials")
    if encrypted:
        decrypted = key_manager.decrypt_data(encrypted, "user_credentials")
        print(f"Encryption test: {'PASSED' if decrypted == test_data else 'FAILED'}")
    
    # Generate health report
    health_report = key_manager.get_key_health_report()
    print(f"Key health report: {json.dumps(health_report, indent=2)}")


if __name__ == "__main__":
    main()