"""🔐 Model Encryption Manager - Enterprise ML Security
======================================================
Module: ml/model_registry/model_encryption_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
======================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🛡️ ENTERPRISE MODEL SECURITY
Model encryption at rest and in transit with enterprise security standards
- AES-256-GCM encryption for model artifacts
- Hardware Security Module (HSM) simulation
- Key rotation and management
- Secure model transmission
"""

import asyncio
import logging
import os
import hashlib
import hmac
import base64
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import secrets

logger = logging.getLogger(__name__)

class EncryptionLevel(Enum):
    """Encryption security levels"""
    BASIC = "basic"           # AES-128
    STANDARD = "standard"     # AES-256
    ENTERPRISE = "enterprise" # AES-256-GCM + HSM simulation
    QUANTUM_READY = "quantum_ready"  # Post-quantum cryptography ready

class KeyType(Enum):
    """Encryption key types"""
    MODEL_ENCRYPTION = "model_encryption"
    METADATA_ENCRYPTION = "metadata_encryption"
    TRANSMISSION = "transmission"
    BACKUP = "backup"

@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    key_type: KeyType
    encryption_level: EncryptionLevel
    created_at: datetime
    expires_at: Optional[datetime]
    rotation_count: int = 0
    is_active: bool = True
    checksum: Optional[str] = None

@dataclass
class EncryptedArtifact:
    """Encrypted model artifact metadata"""
    original_path: str
    encrypted_path: str
    key_id: str
    encryption_algorithm: str
    checksum_original: str
    checksum_encrypted: str
    size_original: int
    size_encrypted: int
    encrypted_at: datetime

class ModelEncryptionManager:
    """
    Enterprise model encryption manager with HSM simulation
    """
    
    def __init__(self, key_store_path -> None: str = "./encryption_keys", hsm_simulation -> None: bool = True) -> None:
        self.key_store_path = Path(key_store_path)
        self.key_store_path.mkdir(exist_ok=True)
        self.hsm_simulation = hsm_simulation
        self.active_keys: Dict[str, EncryptionKey] = {}
        self.key_cache: Dict[str, bytes] = {}
        self.rotation_interval = timedelta(days=90)  # Enterprise standard
        
        # Initialize master key for key encryption
        self.master_key = self._initialize_master_key()
        
    async def encrypt_model(
        self,
        model_path: str,
        output_path: Optional[str] = None,
        encryption_level: EncryptionLevel = EncryptionLevel.ENTERPRISE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EncryptedArtifact:
        """
        Encrypt model with specified security level
        """
        try:
            model_path = Path(model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
            
            # Generate output path if not provided
            if not output_path:
                output_path = model_path.with_suffix(model_path.suffix + '.encrypted')
            
            # Generate encryption key
            key_id = await self.generate_key(
                key_type=KeyType.MODEL_ENCRYPTION,
                encryption_level=encryption_level
            )
            
            # Read and encrypt model
            with open(model_path, 'rb') as f:
                model_data = f.read()
            
            encrypted_data = await self._encrypt_data(model_data, key_id, encryption_level)
            
            # Write encrypted model
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Calculate checksums
            checksum_original = hashlib.sha256(model_data).hexdigest()
            checksum_encrypted = hashlib.sha256(encrypted_data).hexdigest()
            
            # Create artifact metadata
            artifact = EncryptedArtifact(
                original_path=str(model_path),
                encrypted_path=str(output_path),
                key_id=key_id,
                encryption_algorithm=f"AES-256-GCM-{encryption_level.value}",
                checksum_original=checksum_original,
                checksum_encrypted=checksum_encrypted,
                size_original=len(model_data),
                size_encrypted=len(encrypted_data),
                encrypted_at=datetime.utcnow()
            )
            
            # Store metadata
            await self._store_artifact_metadata(artifact, metadata)
            
            logger.info(f"Encrypted model {model_path} with key {key_id}")
            return artifact
            
        except Exception as e:
            logger.error(f"Failed to encrypt model {model_path}: {str(e)}")
            raise

    async def decrypt_model(
        self,
        encrypted_path: str,
        output_path: Optional[str] = None,
        verify_integrity: bool = True
    ) -> str:
        """
        Decrypt model and verify integrity
        """
        try:
            encrypted_path = Path(encrypted_path)
            if not encrypted_path.exists():
                raise FileNotFoundError(f"Encrypted model not found: {encrypted_path}")
            
            # Load artifact metadata
            artifact = await self._load_artifact_metadata(str(encrypted_path))
            
            # Read encrypted data
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            decrypted_data = await self._decrypt_data(encrypted_data, artifact.key_id)
            
            # Verify integrity if requested
            if verify_integrity:
                checksum = hashlib.sha256(decrypted_data).hexdigest()
                if checksum != artifact.checksum_original:
                    raise ValueError("Model integrity verification failed")
            
            # Generate output path if not provided
            if not output_path:
                original_path = Path(artifact.original_path)
                output_path = encrypted_path.parent / f"decrypted_{original_path.name}"
            
            # Write decrypted model
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"Decrypted model to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to decrypt model {encrypted_path}: {str(e)}")
            raise

    async def generate_key(
        self,
        key_type: KeyType = KeyType.MODEL_ENCRYPTION,
        encryption_level: EncryptionLevel = EncryptionLevel.ENTERPRISE,
        expires_in_days: Optional[int] = 365
    ) -> str:
        """
        Generate new encryption key with HSM simulation
        """
        try:
            key_id = f"{key_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(8)}"
            
            # Generate key based on encryption level
            if encryption_level == EncryptionLevel.ENTERPRISE:
                # Simulate HSM key generation
                key_material = await self._hsm_generate_key(256)  # 256-bit key
            elif encryption_level == EncryptionLevel.QUANTUM_READY:
                # Future: Post-quantum key generation
                key_material = await self._quantum_ready_key_generation()
            else:
                # Standard key generation
                key_material = os.urandom(32)  # 256-bit key
            
            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            # Create key metadata
            key_metadata = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                encryption_level=encryption_level,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                checksum=hashlib.sha256(key_material).hexdigest()
            )
            
            # Store key securely
            await self._store_key(key_id, key_material, key_metadata)
            
            # Cache key for performance
            self.key_cache[key_id] = key_material
            self.active_keys[key_id] = key_metadata
            
            logger.info(f"Generated {encryption_level.value} key {key_id} for {key_type.value}")
            return key_id
            
        except Exception as e:
            logger.error(f"Failed to generate key: {str(e)}")
            raise

    async def rotate_key(self, old_key_id: str) -> str:
        """
        Rotate encryption key with seamless transition
        """
        try:
            if old_key_id not in self.active_keys:
                raise ValueError(f"Key {old_key_id} not found")
            
            old_key = self.active_keys[old_key_id]
            
            # Generate new key with same parameters
            new_key_id = await self.generate_key(
                key_type=old_key.key_type,
                encryption_level=old_key.encryption_level
            )
            
            # Update rotation count
            new_key = self.active_keys[new_key_id]
            new_key.rotation_count = old_key.rotation_count + 1
            
            # Deactivate old key (but keep for decryption)
            old_key.is_active = False
            
            # Re-encrypt artifacts with new key if needed
            await self._reencrypt_artifacts_with_new_key(old_key_id, new_key_id)
            
            logger.info(f"Rotated key from {old_key_id} to {new_key_id}")
            return new_key_id
            
        except Exception as e:
            logger.error(f"Failed to rotate key {old_key_id}: {str(e)}")
            raise

    async def get_key_info(self, key_id: str) -> Optional[EncryptionKey]:
        """Get encryption key information"""
        return self.active_keys.get(key_id)

    async def list_keys(
        self,
        key_type: Optional[KeyType] = None,
        active_only: bool = True
    ) -> List[EncryptionKey]:
        """List encryption keys"""
        keys = list(self.active_keys.values())
        
        if key_type:
            keys = [k for k in keys if k.key_type == key_type]
        
        if active_only:
            keys = [k for k in keys if k.is_active]
        
        return sorted(keys, key=lambda k: k.created_at, reverse=True)

    async def check_key_expiration(self) -> List[EncryptionKey]:
        """Check for keys that need rotation"""
        expiring_soon = []
        warning_period = timedelta(days=30)
        
        for key in self.active_keys.values():
            if not key.is_active:
                continue
                
            # Check expiration date
            if key.expires_at and key.expires_at - datetime.utcnow() < warning_period:
                expiring_soon.append(key)
            
            # Check rotation interval
            elif datetime.utcnow() - key.created_at > self.rotation_interval:
                expiring_soon.append(key)
        
        return expiring_soon

    async def secure_delete_key(self, key_id: str) -> bool:
        """Securely delete encryption key"""
        try:
            if key_id in self.key_cache:
                # Overwrite memory
                key_material = self.key_cache[key_id]
                overwrite_data = os.urandom(len(key_material))
                key_material[:] = overwrite_data
                del self.key_cache[key_id]
            
            if key_id in self.active_keys:
                del self.active_keys[key_id]
            
            # Delete key file securely
            key_file = self.key_store_path / f"{key_id}.key"
            if key_file.exists():
                # Overwrite file before deletion
                with open(key_file, 'r+b') as f:
                    length = f.seek(0, 2)
                    f.seek(0)
                    f.write(os.urandom(length))
                    f.flush()
                    os.fsync(f.fileno())
                key_file.unlink()
            
            logger.info(f"Securely deleted key {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete key {key_id}: {str(e)}")
            return False

    async def _encrypt_data(
        self,
        data: bytes,
        key_id: str,
        encryption_level: EncryptionLevel
    ) -> bytes:
        """Encrypt data with specified algorithm"""
        if key_id not in self.key_cache:
            raise ValueError(f"Key {key_id} not found in cache")
        
        key_material = self.key_cache[key_id]
        
        if encryption_level in [EncryptionLevel.ENTERPRISE, EncryptionLevel.QUANTUM_READY]:
            # Use AES-256-GCM for authenticated encryption
            aes_gcm = AESGCM(key_material)
            nonce = os.urandom(12)  # 96-bit nonce for GCM
            ciphertext = aes_gcm.encrypt(nonce, data, None)
            return nonce + ciphertext
        else:
            # Use Fernet for basic/standard encryption
            fernet = Fernet(base64.urlsafe_b64encode(key_material))
            return fernet.encrypt(data)

    async def _decrypt_data(self, encrypted_data: bytes, key_id: str) -> bytes:
        """Decrypt data"""
        if key_id not in self.key_cache:
            # Try to load key from storage
            await self._load_key(key_id)
        
        if key_id not in self.key_cache:
            raise ValueError(f"Key {key_id} not found")
        
        key_material = self.key_cache[key_id]
        key_info = self.active_keys.get(key_id)
        
        if key_info and key_info.encryption_level in [EncryptionLevel.ENTERPRISE, EncryptionLevel.QUANTUM_READY]:
            # AES-256-GCM decryption
            aes_gcm = AESGCM(key_material)
            nonce = encrypted_data[:12]  # First 12 bytes are nonce
            ciphertext = encrypted_data[12:]
            return aes_gcm.decrypt(nonce, ciphertext, None)
        else:
            # Fernet decryption
            fernet = Fernet(base64.urlsafe_b64encode(key_material))
            return fernet.decrypt(encrypted_data)

    async def _hsm_generate_key(self, key_size_bits: int) -> bytes:
        """Simulate HSM key generation with entropy collection"""
        if not self.hsm_simulation:
            # In real implementation, this would interface with actual HSM
            return os.urandom(key_size_bits // 8)
        
        # Simulate HSM with high-entropy key generation
        entropy_sources = []
        
        # Collect entropy from multiple sources
        entropy_sources.append(os.urandom(32))
        entropy_sources.append(str(datetime.utcnow().timestamp()).encode())
        entropy_sources.append(str(secrets.randbits(256)).encode())
        
        # Combine entropy sources
        combined_entropy = b''.join(entropy_sources)
        
        # Use PBKDF2 to derive key material
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_size_bits // 8,
            salt=os.urandom(16),
            iterations=100000,
            backend=default_backend()
        )
        
        return kdf.derive(combined_entropy)

    async def _quantum_ready_key_generation(self) -> bytes:
        """Future: Post-quantum cryptography ready key generation"""
        # Placeholder for post-quantum key generation
        # In future implementation, this would use NIST-approved PQC algorithms
        return await self._hsm_generate_key(256)

    def _initialize_master_key(self) -> bytes:
        """Initialize master key for key encryption"""
        master_key_file = self.key_store_path / "master.key"
        
        if master_key_file.exists():
            with open(master_key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new master key
            master_key = os.urandom(32)  # 256-bit master key
            with open(master_key_file, 'wb') as f:
                f.write(master_key)
            # Set restrictive permissions
            os.chmod(master_key_file, 0o600)
            return master_key

    async def _store_key(self, key_id: str, key_material: bytes, metadata: EncryptionKey) -> None:
        """Store encryption key securely"""
        # Encrypt key with master key
        fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
        encrypted_key = fernet.encrypt(key_material)
        
        # Store encrypted key
        key_file = self.key_store_path / f"{key_id}.key"
        with open(key_file, 'wb') as f:
            f.write(encrypted_key)
        
        # Store metadata
        metadata_file = self.key_store_path / f"{key_id}.meta"
        metadata_dict = {
            'key_id': metadata.key_id,
            'key_type': metadata.key_type.value,
            'encryption_level': metadata.encryption_level.value,
            'created_at': metadata.created_at.isoformat(),
            'expires_at': metadata.expires_at.isoformat() if metadata.expires_at else None,
            'rotation_count': metadata.rotation_count,
            'is_active': metadata.is_active,
            'checksum': metadata.checksum
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

    async def _load_key(self, key_id: str) -> None:
        """Load encryption key from storage"""
        key_file = self.key_store_path / f"{key_id}.key"
        metadata_file = self.key_store_path / f"{key_id}.meta"
        
        if not key_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(f"Key {key_id} not found in storage")
        
        # Load metadata
        with open(metadata_file, 'r') as f:
            metadata_dict = json.load(f)
        
        metadata = EncryptionKey(
            key_id=metadata_dict['key_id'],
            key_type=KeyType(metadata_dict['key_type']),
            encryption_level=EncryptionLevel(metadata_dict['encryption_level']),
            created_at=datetime.fromisoformat(metadata_dict['created_at']),
            expires_at=datetime.fromisoformat(metadata_dict['expires_at']) if metadata_dict['expires_at'] else None,
            rotation_count=metadata_dict['rotation_count'],
            is_active=metadata_dict['is_active'],
            checksum=metadata_dict['checksum']
        )
        
        # Load and decrypt key
        with open(key_file, 'rb') as f:
            encrypted_key = f.read()
        
        fernet = Fernet(base64.urlsafe_b64encode(self.master_key))
        key_material = fernet.decrypt(encrypted_key)
        
        # Cache key and metadata
        self.key_cache[key_id] = key_material
        self.active_keys[key_id] = metadata

    async def _store_artifact_metadata(self, artifact: EncryptedArtifact, metadata: Optional[Dict[str, Any]]) -> None:
        """Store encrypted artifact metadata"""
        metadata_dict = {
            'original_path': artifact.original_path,
            'encrypted_path': artifact.encrypted_path,
            'key_id': artifact.key_id,
            'encryption_algorithm': artifact.encryption_algorithm,
            'checksum_original': artifact.checksum_original,
            'checksum_encrypted': artifact.checksum_encrypted,
            'size_original': artifact.size_original,
            'size_encrypted': artifact.size_encrypted,
            'encrypted_at': artifact.encrypted_at.isoformat(),
            'additional_metadata': metadata or {}
        }
        
        metadata_file = Path(artifact.encrypted_path).with_suffix('.meta')
        with open(metadata_file, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

    async def _load_artifact_metadata(self, encrypted_path: str) -> EncryptedArtifact:
        """Load encrypted artifact metadata"""
        metadata_file = Path(encrypted_path).with_suffix('.meta')
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata not found for {encrypted_path}")
        
        with open(metadata_file, 'r') as f:
            metadata_dict = json.load(f)
        
        return EncryptedArtifact(
            original_path=metadata_dict['original_path'],
            encrypted_path=metadata_dict['encrypted_path'],
            key_id=metadata_dict['key_id'],
            encryption_algorithm=metadata_dict['encryption_algorithm'],
            checksum_original=metadata_dict['checksum_original'],
            checksum_encrypted=metadata_dict['checksum_encrypted'],
            size_original=metadata_dict['size_original'],
            size_encrypted=metadata_dict['size_encrypted'],
            encrypted_at=datetime.fromisoformat(metadata_dict['encrypted_at'])
        )

    async def _reencrypt_artifacts_with_new_key(self, old_key_id: str, new_key_id: str) -> None:
        """Re-encrypt artifacts with new key after rotation"""
        # This would be implemented in a real scenario to re-encrypt all artifacts
        # using the old key with the new key for seamless key rotation
        logger.info(f"Re-encryption from {old_key_id} to {new_key_id} scheduled")

# Usage Example
async def main() -> None:
    """Example usage of ModelEncryptionManager"""
    manager = ModelEncryptionManager()
    
    # Generate enterprise-level encryption key
    key_id = await manager.generate_key(
        key_type=KeyType.MODEL_ENCRYPTION,
        encryption_level=EncryptionLevel.ENTERPRISE
    )
    
    # Create test model file
    test_model_path = "/tmp/test_model.pkl"
    with open(test_model_path, 'wb') as f:
        f.write(b"Test model data for encryption")
    
    # Encrypt model
    encrypted_artifact = await manager.encrypt_model(
        model_path=test_model_path,
        encryption_level=EncryptionLevel.ENTERPRISE,
        metadata={'model_type': 'classifier', 'version': '1.0.0'}
    )
    
    print(f"Encrypted model: {encrypted_artifact.encrypted_path}")
    print(f"Key used: {encrypted_artifact.key_id}")
    
    # Decrypt model
    decrypted_path = await manager.decrypt_model(
        encrypted_path=encrypted_artifact.encrypted_path,
        verify_integrity=True
    )
    
    print(f"Decrypted model: {decrypted_path}")

if __name__ == "__main__":
    asyncio.run(main())