"""
Data Encryption Manager
Enterprise-grade encryption for ML data and models

Features:
- End-to-end data encryption
- Model encryption and secure storage
- Key management and rotation
- Encrypted data pipelines
- Secure model serving
- Privacy-preserving computations

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import json
import logging
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import numpy as np


class EncryptionType(Enum):
    """Types of encryption"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    HYBRID = "hybrid"
    HOMOMORPHIC = "homomorphic"


class KeyType(Enum):
    """Types of encryption keys"""
    DATA_ENCRYPTION = "data_encryption"
    MODEL_ENCRYPTION = "model_encryption"
    COMMUNICATION = "communication"
    STORAGE = "storage"


@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    encryption_type: EncryptionType
    key_size: int = 2048
    algorithm: str = "AES-256"
    key_rotation_days: int = 90
    backup_keys: int = 3
    secure_key_storage: bool = True


@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: KeyType
    algorithm: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    encrypted_key: bytes
    metadata: Dict[str, Any]


@dataclass
class EncryptionMetrics:
    """Encryption operation metrics"""
    total_operations: int
    encryptions: int
    decryptions: int
    key_rotations: int
    failed_operations: int
    average_encryption_time: float
    average_decryption_time: float


class DataEncryptionManager:
    """
    Enterprise Data Encryption Manager
    Comprehensive encryption for ML data and models
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.keys: Dict[str, EncryptionKey] = {}
        self.encryption_configs: Dict[str, EncryptionConfig] = {}
        self.metrics = EncryptionMetrics(0, 0, 0, 0, 0, 0.0, 0.0)
        self.master_key = self._generate_master_key()
        
    async def configure_encryption(
        self,
        context_id: str,
        config: EncryptionConfig
    ) -> bool:
        """Configure encryption for a specific context (model, dataset, etc.)"""
        try:
            self.encryption_configs[context_id] = config
            
            # Generate initial encryption key
            await self.generate_key(context_id, KeyType.DATA_ENCRYPTION)
            
            self.logger.info(f"Encryption configured for context {context_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure encryption for {context_id}: {str(e)}")
            return False
    
    async def generate_key(
        self,
        context_id: str,
        key_type: KeyType,
        force_rotation: bool = False
    ) -> str:
        """Generate new encryption key"""
        try:
            config = self.encryption_configs.get(context_id)
            if not config:
                raise ValueError(f"No encryption config for context {context_id}")
            
            # Check if we need to rotate existing key
            existing_key_id = self._get_active_key_id(context_id, key_type)
            if existing_key_id and not force_rotation:
                existing_key = self.keys.get(existing_key_id)
                if existing_key and existing_key.is_active:
                    if not self._should_rotate_key(existing_key, config):
                        return existing_key_id
            
            # Generate new key
            key_id = f"{context_id}_{key_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if config.encryption_type == EncryptionType.SYMMETRIC:
                raw_key = Fernet.generate_key()
            elif config.encryption_type == EncryptionType.ASYMMETRIC:
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=config.key_size
                )
                raw_key = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            else:
                raw_key = os.urandom(32)  # Default to 256-bit key
            
            # Encrypt the key with master key
            encrypted_key = self._encrypt_with_master_key(raw_key)
            
            # Create key metadata
            key_metadata = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=config.algorithm,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=config.key_rotation_days),
                is_active=True,
                encrypted_key=encrypted_key,
                metadata={
                    "context_id": context_id,
                    "encryption_type": config.encryption_type.value,
                    "key_size": config.key_size
                }
            )
            
            # Deactivate old key if rotating
            if existing_key_id:
                old_key = self.keys.get(existing_key_id)
                if old_key:
                    old_key.is_active = False
                    self.keys[existing_key_id] = old_key
                    self.metrics.key_rotations += 1
            
            self.keys[key_id] = key_metadata
            
            self.logger.info(f"Generated new {key_type.value} key for context {context_id}")
            return key_id
            
        except Exception as e:
            self.logger.error(f"Failed to generate key for {context_id}: {str(e)}")
            raise
    
    async def encrypt_data(
        self,
        context_id: str,
        data: Union[bytes, np.ndarray, Dict[str, Any]],
        key_type: KeyType = KeyType.DATA_ENCRYPTION
    ) -> Tuple[bytes, str]:
        """Encrypt data using configured encryption"""
        start_time = datetime.now()
        
        try:
            config = self.encryption_configs.get(context_id)
            if not config:
                raise ValueError(f"No encryption config for context {context_id}")
            
            key_id = self._get_active_key_id(context_id, key_type)
            if not key_id:
                key_id = await self.generate_key(context_id, key_type)
            
            # Convert data to bytes if needed
            data_bytes = self._serialize_data(data)
            
            # Encrypt based on configuration
            if config.encryption_type == EncryptionType.SYMMETRIC:
                encrypted_data = await self._encrypt_symmetric(key_id, data_bytes)
            elif config.encryption_type == EncryptionType.ASYMMETRIC:
                encrypted_data = await self._encrypt_asymmetric(key_id, data_bytes)
            elif config.encryption_type == EncryptionType.HYBRID:
                encrypted_data = await self._encrypt_hybrid(key_id, data_bytes)
            else:
                raise ValueError(f"Encryption type {config.encryption_type} not supported")
            
            # Update metrics
            self.metrics.total_operations += 1
            self.metrics.encryptions += 1
            encryption_time = (datetime.now() - start_time).total_seconds()
            self.metrics.average_encryption_time = (
                (self.metrics.average_encryption_time * (self.metrics.encryptions - 1) + encryption_time) /
                self.metrics.encryptions
            )
            
            return encrypted_data, key_id
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.logger.error(f"Data encryption failed for context {context_id}: {str(e)}")
            raise
    
    async def decrypt_data(
        self,
        context_id: str,
        encrypted_data: bytes,
        key_id: str,
        output_type: str = "bytes"
    ) -> Union[bytes, np.ndarray, Dict[str, Any]]:
        """Decrypt data using specified key"""
        start_time = datetime.now()
        
        try:
            config = self.encryption_configs.get(context_id)
            if not config:
                raise ValueError(f"No encryption config for context {context_id}")
            
            key_metadata = self.keys.get(key_id)
            if not key_metadata:
                raise ValueError(f"Key {key_id} not found")
            
            # Decrypt based on configuration
            if config.encryption_type == EncryptionType.SYMMETRIC:
                data_bytes = await self._decrypt_symmetric(key_id, encrypted_data)
            elif config.encryption_type == EncryptionType.ASYMMETRIC:
                data_bytes = await self._decrypt_asymmetric(key_id, encrypted_data)
            elif config.encryption_type == EncryptionType.HYBRID:
                data_bytes = await self._decrypt_hybrid(key_id, encrypted_data)
            else:
                raise ValueError(f"Encryption type {config.encryption_type} not supported")
            
            # Convert back to original type
            decrypted_data = self._deserialize_data(data_bytes, output_type)
            
            # Update metrics
            self.metrics.total_operations += 1
            self.metrics.decryptions += 1
            decryption_time = (datetime.now() - start_time).total_seconds()
            self.metrics.average_decryption_time = (
                (self.metrics.average_decryption_time * (self.metrics.decryptions - 1) + decryption_time) /
                self.metrics.decryptions
            )
            
            return decrypted_data
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.logger.error(f"Data decryption failed for context {context_id}: {str(e)}")
            raise
    
    async def encrypt_model(
        self,
        model_id: str,
        model_data: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bytes, str]:
        """Encrypt ML model"""
        try:
            # Configure encryption for model if not exists
            if model_id not in self.encryption_configs:
                config = EncryptionConfig(
                    encryption_type=EncryptionType.HYBRID,
                    key_size=2048,
                    algorithm="AES-256-RSA",
                    key_rotation_days=180  # Longer rotation for models
                )
                await self.configure_encryption(model_id, config)
            
            encrypted_data, key_id = await self.encrypt_data(
                model_id, model_data, KeyType.MODEL_ENCRYPTION
            )
            
            self.logger.info(f"Model {model_id} encrypted successfully")
            return encrypted_data, key_id
            
        except Exception as e:
            self.logger.error(f"Model encryption failed for {model_id}: {str(e)}")
            raise
    
    async def decrypt_model(
        self,
        model_id: str,
        encrypted_model: bytes,
        key_id: str
    ) -> bytes:
        """Decrypt ML model"""
        try:
            model_data = await self.decrypt_data(
                model_id, encrypted_model, key_id, "bytes"
            )
            
            self.logger.info(f"Model {model_id} decrypted successfully")
            return model_data
            
        except Exception as e:
            self.logger.error(f"Model decryption failed for {model_id}: {str(e)}")
            raise
    
    async def secure_data_pipeline(
        self,
        pipeline_id: str,
        data_stages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create secure encrypted data pipeline"""
        try:
            secure_stages = []
            
            for stage in data_stages:
                stage_id = f"{pipeline_id}_{stage['name']}"
                
                # Configure encryption for this stage
                config = EncryptionConfig(
                    encryption_type=EncryptionType.SYMMETRIC,
                    algorithm="AES-256",
                    key_rotation_days=30  # More frequent rotation for pipelines
                )
                await self.configure_encryption(stage_id, config)
                
                # Encrypt stage data if present
                if 'data' in stage:
                    encrypted_data, key_id = await self.encrypt_data(
                        stage_id, stage['data']
                    )
                    stage['encrypted_data'] = encrypted_data
                    stage['encryption_key_id'] = key_id
                    del stage['data']  # Remove unencrypted data
                
                stage['encryption_enabled'] = True
                stage['stage_id'] = stage_id
                secure_stages.append(stage)
            
            self.logger.info(f"Secure data pipeline created for {pipeline_id}")
            return secure_stages
            
        except Exception as e:
            self.logger.error(f"Secure pipeline creation failed for {pipeline_id}: {str(e)}")
            raise
    
    async def rotate_keys(
        self,
        context_id: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, List[str]]:
        """Rotate encryption keys"""
        try:
            rotated_keys = {"rotated": [], "failed": []}
            
            # Get contexts to rotate
            contexts = [context_id] if context_id else list(self.encryption_configs.keys())
            
            for ctx_id in contexts:
                config = self.encryption_configs.get(ctx_id)
                if not config:
                    continue
                
                # Find keys that need rotation
                for key_id, key_metadata in self.keys.items():
                    if (key_metadata.metadata.get("context_id") == ctx_id and 
                        key_metadata.is_active and 
                        (force or self._should_rotate_key(key_metadata, config))):
                        
                        try:
                            new_key_id = await self.generate_key(
                                ctx_id, key_metadata.key_type, force_rotation=True
                            )
                            rotated_keys["rotated"].append(new_key_id)
                        except Exception as e:
                            rotated_keys["failed"].append(key_id)
                            self.logger.error(f"Failed to rotate key {key_id}: {str(e)}")
            
            return rotated_keys
            
        except Exception as e:
            self.logger.error(f"Key rotation failed: {str(e)}")
            raise
    
    async def get_encryption_metrics(self) -> Dict[str, Any]:
        """Get encryption operation metrics"""
        try:
            active_keys = len([k for k in self.keys.values() if k.is_active])
            total_keys = len(self.keys)
            
            return {
                "metrics": {
                    "total_operations": self.metrics.total_operations,
                    "encryptions": self.metrics.encryptions,
                    "decryptions": self.metrics.decryptions,
                    "key_rotations": self.metrics.key_rotations,
                    "failed_operations": self.metrics.failed_operations,
                    "average_encryption_time": self.metrics.average_encryption_time,
                    "average_decryption_time": self.metrics.average_decryption_time
                },
                "keys": {
                    "active_keys": active_keys,
                    "total_keys": total_keys,
                    "contexts_configured": len(self.encryption_configs)
                },
                "health": {
                    "encryption_success_rate": (
                        (self.metrics.total_operations - self.metrics.failed_operations) / 
                        max(self.metrics.total_operations, 1)
                    ),
                    "average_operation_time": (
                        (self.metrics.average_encryption_time + self.metrics.average_decryption_time) / 2
                    )
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get encryption metrics: {str(e)}")
            raise
    
    # Private methods
    
    def _generate_master_key(self) -> bytes:
        """Generate master key for key encryption"""
        # In production, this would be managed by a proper key management service
        return Fernet.generate_key()
    
    def _encrypt_with_master_key(self, data: bytes) -> bytes:
        """Encrypt data with master key"""
        f = Fernet(self.master_key)
        return f.encrypt(data)
    
    def _decrypt_with_master_key(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with master key"""
        f = Fernet(self.master_key)
        return f.decrypt(encrypted_data)
    
    def _get_active_key_id(self, context_id: str, key_type: KeyType) -> Optional[str]:
        """Get active key ID for context and type"""
        for key_id, key_metadata in self.keys.items():
            if (key_metadata.metadata.get("context_id") == context_id and
                key_metadata.key_type == key_type and
                key_metadata.is_active):
                return key_id
        return None
    
    def _should_rotate_key(self, key_metadata: EncryptionKey, config: EncryptionConfig) -> bool:
        """Check if key should be rotated"""
        if key_metadata.expires_at and datetime.now() >= key_metadata.expires_at:
            return True
        
        # Check if key is approaching expiration (rotate 7 days early)
        if key_metadata.expires_at:
            warning_time = key_metadata.expires_at - timedelta(days=7)
            if datetime.now() >= warning_time:
                return True
        
        return False
    
    def _serialize_data(self, data: Union[bytes, np.ndarray, Dict[str, Any]]) -> bytes:
        """Serialize data to bytes"""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, np.ndarray):
            return data.tobytes()
        elif isinstance(data, (dict, list)):
            return json.dumps(data, default=str).encode('utf-8')
        else:
            return str(data).encode('utf-8')
    
    def _deserialize_data(self, data_bytes: bytes, output_type: str) -> Union[bytes, np.ndarray, Dict[str, Any]]:
        """Deserialize bytes to original data type"""
        if output_type == "bytes":
            return data_bytes
        elif output_type == "numpy":
            return np.frombuffer(data_bytes)
        elif output_type == "json":
            return json.loads(data_bytes.decode('utf-8'))
        else:
            return data_bytes.decode('utf-8')
    
    async def _encrypt_symmetric(self, key_id: str, data: bytes) -> bytes:
        """Encrypt using symmetric encryption"""
        key_metadata = self.keys[key_id]
        raw_key = self._decrypt_with_master_key(key_metadata.encrypted_key)
        
        f = Fernet(raw_key)
        return f.encrypt(data)
    
    async def _decrypt_symmetric(self, key_id: str, encrypted_data: bytes) -> bytes:
        """Decrypt using symmetric encryption"""
        key_metadata = self.keys[key_id]
        raw_key = self._decrypt_with_master_key(key_metadata.encrypted_key)
        
        f = Fernet(raw_key)
        return f.decrypt(encrypted_data)
    
    async def _encrypt_asymmetric(self, key_id: str, data: bytes) -> bytes:
        """Encrypt using asymmetric encryption"""
        key_metadata = self.keys[key_id]
        private_key_bytes = self._decrypt_with_master_key(key_metadata.encrypted_key)
        
        private_key = serialization.load_pem_private_key(
            private_key_bytes, password=None
        )
        public_key = private_key.public_key()
        
        # Asymmetric encryption has size limits, so use hybrid approach for large data
        if len(data) > 190:  # RSA-2048 limit
            return await self._encrypt_hybrid(key_id, data)
        
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted
    
    async def _decrypt_asymmetric(self, key_id: str, encrypted_data: bytes) -> bytes:
        """Decrypt using asymmetric encryption"""
        key_metadata = self.keys[key_id]
        private_key_bytes = self._decrypt_with_master_key(key_metadata.encrypted_key)
        
        private_key = serialization.load_pem_private_key(
            private_key_bytes, password=None
        )
        
        # Check if this is hybrid encryption
        if len(encrypted_data) > 256:  # RSA-2048 output size
            return await self._decrypt_hybrid(key_id, encrypted_data)
        
        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted
    
    async def _encrypt_hybrid(self, key_id: str, data: bytes) -> bytes:
        """Encrypt using hybrid encryption (RSA + AES)"""
        # Generate random AES key
        aes_key = Fernet.generate_key()
        f = Fernet(aes_key)
        
        # Encrypt data with AES
        encrypted_data = f.encrypt(data)
        
        # Encrypt AES key with RSA
        encrypted_aes_key = await self._encrypt_asymmetric(key_id, aes_key)
        
        # Combine encrypted key and data
        return len(encrypted_aes_key).to_bytes(4, 'big') + encrypted_aes_key + encrypted_data
    
    async def _decrypt_hybrid(self, key_id: str, encrypted_data: bytes) -> bytes:
        """Decrypt using hybrid encryption (RSA + AES)"""
        # Extract encrypted AES key length
        key_length = int.from_bytes(encrypted_data[:4], 'big')
        
        # Extract encrypted AES key and data
        encrypted_aes_key = encrypted_data[4:4+key_length]
        encrypted_payload = encrypted_data[4+key_length:]
        
        # Decrypt AES key with RSA
        aes_key = await self._decrypt_asymmetric(key_id, encrypted_aes_key)
        
        # Decrypt data with AES
        f = Fernet(aes_key)
        return f.decrypt(encrypted_payload)


# Global instance
data_encryption_manager = DataEncryptionManager()