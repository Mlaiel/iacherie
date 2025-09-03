"""Key Management Service - Gestion clés

Enterprise-grade cryptographic key management system with rotation and lifecycle management.
Consolidates key management functionality from existing modules.

Author: Fahed Mlaiel <mlaiel@live.de>  
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import secrets
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import base64
import json

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .data_encryption import EncryptionKey, EncryptionAlgorithm, KeyType

logger = logging.getLogger(__name__)


class KeyStatus(Enum):
    """Key lifecycle status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ARCHIVED = "archived"


@dataclass
class KeyRotationInfo:
    """Key rotation information"""
    key_id: str
    old_key_id: Optional[str]
    rotation_date: datetime
    next_rotation: Optional[datetime]
    reason: str


class KeyManagementService:
    """
    Secure key management system with automated rotation and lifecycle management.
    Consolidates functionality from existing key management modules.
    """
    
    def __init__(self, master_key_file: Optional[str] = None):
        self.logger = logger
        self.keys: Dict[str, EncryptionKey] = {}
        self.key_rotation_schedule: Dict[str, datetime] = {}
        self.rotation_history: List[KeyRotationInfo] = []
        self.last_rotation_check = datetime.now()
        
        # Initialize master key
        self.master_key_file = master_key_file or os.environ.get('MASTER_KEY_FILE', '.master_key')
        self.master_key = self._generate_master_key()
        
    def _generate_master_key(self) -> bytes:
        """
        Generate or load master key for key encryption
        Consolidated from data_management/storage/encryption_engine.py
        """
        try:
            if os.path.exists(self.master_key_file):
                with open(self.master_key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new master key
                master_key = secrets.token_bytes(32)
                with open(self.master_key_file, 'wb') as f:
                    f.write(master_key)
                os.chmod(self.master_key_file, 0o600)  # Restrictive permissions
                return master_key
                
        except Exception as e:
            self.logger.error(f"Master key generation failed: {str(e)}")
            # Fallback to in-memory key (not recommended for production)
            return secrets.token_bytes(32)
    
    def generate_key(self, algorithm: EncryptionAlgorithm, key_type: KeyType = KeyType.SYMMETRIC) -> EncryptionKey:
        """
        Generate new encryption key
        Consolidated from data_management/storage/encryption_engine.py
        """
        key_id = self._generate_key_id()
        
        try:
            if algorithm in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                key_data = secrets.token_bytes(32)  # 256 bits
                metadata = {'key': base64.b64encode(key_data).decode()}
                
            elif algorithm == EncryptionAlgorithm.FERNET:
                key_data = Fernet.generate_key()
                metadata = {'key': key_data.decode()}
                
            elif algorithm == EncryptionAlgorithm.RSA_OAEP_4096:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=default_backend()
                )
                
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                public_pem = private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                metadata = {
                    'private_key': base64.b64encode(private_pem).decode(),
                    'public_key': base64.b64encode(public_pem).decode()
                }
                
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Create key with expiration
            expires_at = datetime.now() + timedelta(days=365)  # 1 year default
            
            key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                created_at=datetime.now(),
                expires_at=expires_at,
                metadata=metadata
            )
            
            # Store key
            self.keys[key_id] = key
            
            # Schedule rotation
            self.key_rotation_schedule[key_id] = expires_at
            
            self.logger.info(f"Generated new {algorithm.value} key: {key_id}")
            return key
            
        except Exception as e:
            self.logger.error(f"Key generation failed: {str(e)}")
            raise
    
    async def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Retrieve encryption key by ID"""
        return self.keys.get(key_id)
    
    async def store_key(self, key: EncryptionKey, encrypt_at_rest: bool = True) -> bool:
        """
        Store encryption key securely
        """
        try:
            if encrypt_at_rest:
                # Encrypt key metadata with master key
                key_data = json.dumps({
                    'key_id': key.key_id,
                    'key_type': key.key_type.value,
                    'algorithm': key.algorithm.value,
                    'created_at': key.created_at.isoformat(),
                    'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                    'is_active': key.is_active,
                    'metadata': key.metadata
                })
                
                # Simple encryption with master key (in production, use proper KMS)
                fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
                encrypted_key = fernet.encrypt(key_data.encode())
                
                # Store encrypted key (simplified storage)
                key.metadata['encrypted'] = base64.b64encode(encrypted_key).decode()
            
            self.keys[key.key_id] = key
            self.logger.info(f"Stored key: {key.key_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Key storage failed: {str(e)}")
            return False
    
    async def rotate_key(self, key_id: str) -> Optional[EncryptionKey]:
        """
        Rotate encryption key
        Consolidated from api/security/encryption.py
        """
        old_key = await self.get_key(key_id)
        if not old_key:
            return None
        
        try:
            # Generate new key with same parameters
            new_key = self.generate_key(old_key.algorithm, old_key.key_type)
            
            # Mark old key as inactive
            old_key.is_active = False
            await self.store_key(old_key)
            
            # Update rotation schedule
            self.key_rotation_schedule[new_key.key_id] = datetime.now() + timedelta(days=90)  # 3 months
            
            # Record rotation
            rotation_info = KeyRotationInfo(
                key_id=new_key.key_id,
                old_key_id=key_id,
                rotation_date=datetime.now(),
                next_rotation=self.key_rotation_schedule[new_key.key_id],
                reason="scheduled_rotation"
            )
            self.rotation_history.append(rotation_info)
            
            self.logger.info(f"Rotated key {key_id} -> {new_key.key_id}")
            return new_key
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {str(e)}")
            return None
    
    def rotate_keys(self) -> Dict[str, Any]:
        """
        Rotate expired keys
        Consolidated from data_management/storage/encryption_engine.py
        """
        rotated_keys = []
        current_time = datetime.now()
        
        for key_id, key in self.keys.items():
            if key.expires_at and current_time > key.expires_at and key.is_active:
                # Deactivate old key
                key.is_active = False
                
                # Generate new key with same algorithm
                try:
                    new_key = self.generate_key(key.algorithm, key.key_type)
                    rotated_keys.append({
                        'old_key_id': key_id,
                        'new_key_id': new_key.key_id,
                        'algorithm': key.algorithm.value
                    })
                except Exception as e:
                    self.logger.error(f"Failed to rotate key {key_id}: {str(e)}")
        
        self.last_rotation_check = current_time
        
        return {
            'rotated_count': len(rotated_keys),
            'rotated_keys': rotated_keys,
            'next_check': (current_time + timedelta(hours=24)).isoformat()
        }
    
    async def delete_key(self, key_id: str) -> bool:
        """Securely delete encryption key"""
        try:
            if key_id in self.keys:
                # Mark as revoked first
                self.keys[key_id].is_active = False
                
                # Securely overwrite key data
                key = self.keys[key_id]
                if 'key' in key.metadata:
                    # Overwrite key data
                    key.metadata['key'] = 'DELETED'
                
                # Remove from active keys
                del self.keys[key_id]
                
                # Remove from rotation schedule
                if key_id in self.key_rotation_schedule:
                    del self.key_rotation_schedule[key_id]
                
                self.logger.info(f"Deleted key: {key_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Key deletion failed: {str(e)}")
            return False
    
    def _generate_key_id(self) -> str:
        """
        Generate unique key identifier
        From data_management/storage/encryption_engine.py
        """
        timestamp = int(time.time())
        random_part = secrets.token_hex(8)
        return f"key_{timestamp}_{random_part}"
    
    async def get_key_stats(self) -> Dict[str, Any]:
        """Get key management statistics"""
        active_keys = sum(1 for key in self.keys.values() if key.is_active)
        expired_keys = sum(1 for key in self.keys.values() 
                          if key.expires_at and datetime.now() > key.expires_at)
        
        return {
            'total_keys': len(self.keys),
            'active_keys': active_keys,
            'expired_keys': expired_keys,
            'rotation_history_count': len(self.rotation_history),
            'last_rotation_check': self.last_rotation_check.isoformat(),
            'algorithms_in_use': list(set(key.algorithm.value for key in self.keys.values()))
        }
    
    async def check_rotation_schedule(self) -> List[str]:
        """Check which keys need rotation"""
        current_time = datetime.now()
        keys_to_rotate = []
        
        for key_id, rotation_time in self.key_rotation_schedule.items():
            if current_time >= rotation_time and key_id in self.keys and self.keys[key_id].is_active:
                keys_to_rotate.append(key_id)
        
        return keys_to_rotate