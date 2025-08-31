"""
Hardware Security Module (HSM) Integration
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

HSM integration for secure key management and cryptographic operations.
"""

import os
import secrets
import json
import base64
from typing import Dict, Optional, List, Any, Union
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

# Try to import PyKCS11 for HSM support
try:
    import PyKCS11
    HSM_AVAILABLE = True
except ImportError:
    HSM_AVAILABLE = False
    PyKCS11 = None

# Try to import boto3 for AWS KMS support
try:
    import boto3
    AWS_KMS_AVAILABLE = True
except ImportError:
    AWS_KMS_AVAILABLE = False
    boto3 = None

# Try to import hvac for HashiCorp Vault support
try:
    import hvac
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False
    hvac = None

logger = logging.getLogger(__name__)


class KeyType(Enum):
    """Key types for different purposes."""
    MASTER_KEY = "master"
    DATA_ENCRYPTION_KEY = "dek"
    KEY_ENCRYPTION_KEY = "kek"
    SIGNING_KEY = "signing"
    AUTHENTICATION_KEY = "auth"
    SESSION_KEY = "session"


class HSMBackend(Enum):
    """Supported HSM backends."""
    PKCS11 = "pkcs11"
    AWS_KMS = "aws_kms"
    AZURE_KEY_VAULT = "azure_kv"
    HASHICORP_VAULT = "vault"
    GOOGLE_KMS = "google_kms"
    LOCAL_HSM = "local"  # Software-based for development


@dataclass
class KeyMetadata:
    """Metadata for cryptographic keys."""
    key_id: str
    key_type: KeyType
    algorithm: str
    key_size: int
    created_at: datetime
    expires_at: Optional[datetime]
    rotation_schedule: Optional[int]  # Days
    usage_count: int = 0
    max_usage: Optional[int] = None
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyMetadata':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['key_type'] = KeyType(data['key_type'])
        return cls(**data)


class BaseHSM:
    """Base class for HSM implementations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_connected = False
        self.key_metadata: Dict[str, KeyMetadata] = {}
    
    async def connect(self) -> bool:
        """Connect to HSM."""
        raise NotImplementedError
    
    async def disconnect(self):
        """Disconnect from HSM."""
        raise NotImplementedError
    
    async def generate_key(self, key_type: KeyType, algorithm: str, 
                          key_size: int, key_id: Optional[str] = None) -> str:
        """Generate a new key."""
        raise NotImplementedError
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data with specified key."""
        raise NotImplementedError
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data with specified key."""
        raise NotImplementedError
    
    async def sign(self, key_id: str, data: bytes) -> bytes:
        """Sign data with specified key."""
        raise NotImplementedError
    
    async def verify(self, key_id: str, data: bytes, signature: bytes) -> bool:
        """Verify signature with specified key."""
        raise NotImplementedError
    
    async def get_public_key(self, key_id: str) -> bytes:
        """Get public key for asymmetric key pair."""
        raise NotImplementedError
    
    async def delete_key(self, key_id: str) -> bool:
        """Delete key from HSM."""
        raise NotImplementedError
    
    async def list_keys(self) -> List[str]:
        """List all key IDs."""
        raise NotImplementedError
    
    async def rotate_key(self, key_id: str) -> str:
        """Rotate key and return new key ID."""
        raise NotImplementedError


class PKCS11HSM(BaseHSM):
    """PKCS#11 HSM implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not HSM_AVAILABLE:
            raise ImportError("PyKCS11 not available. Install with: pip install PyKCS11")
        
        self.lib_path = config.get('lib_path', '/opt/cloudhsm/lib/libcloudhsm_pkcs11.so')
        self.slot_id = config.get('slot_id', 0)
        self.pin = config.get('pin') or os.getenv('HSM_PIN')
        self.pkcs11 = None
        self.session = None
    
    async def connect(self) -> bool:
        """Connect to PKCS#11 HSM."""
        try:
            self.pkcs11 = PyKCS11.PyKCS11Lib()
            self.pkcs11.load(self.lib_path)
            
            slots = self.pkcs11.getSlotList()
            if not slots:
                raise Exception("No HSM slots available")
            
            slot = slots[self.slot_id] if self.slot_id < len(slots) else slots[0]
            self.session = self.pkcs11.openSession(slot, PyKCS11.CKF_SERIAL_SESSION | PyKCS11.CKF_RW_SESSION)
            
            if self.pin:
                self.session.login(self.pin)
            
            self.is_connected = True
            logger.info("Connected to PKCS#11 HSM")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PKCS#11 HSM: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from PKCS#11 HSM."""
        try:
            if self.session:
                self.session.logout()
                self.session.closeSession()
            self.is_connected = False
            logger.info("Disconnected from PKCS#11 HSM")
            
        except Exception as e:
            logger.error(f"Failed to disconnect from HSM: {str(e)}")
    
    async def generate_key(self, key_type: KeyType, algorithm: str, 
                          key_size: int, key_id: Optional[str] = None) -> str:
        """Generate key in HSM."""
        try:
            if not self.is_connected:
                await self.connect()
            
            if not key_id:
                key_id = f"{key_type.value}_{secrets.token_hex(8)}"
            
            # Create key template based on algorithm
            if algorithm.startswith('AES'):
                # Generate AES key
                template = [
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_SECRET_KEY),
                    (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_AES),
                    (PyKCS11.CKA_VALUE_LEN, key_size // 8),
                    (PyKCS11.CKA_LABEL, key_id),
                    (PyKCS11.CKA_TOKEN, True),
                    (PyKCS11.CKA_PRIVATE, True),
                    (PyKCS11.CKA_ENCRYPT, True),
                    (PyKCS11.CKA_DECRYPT, True),
                ]
                
                key_handle = self.session.generateKey(PyKCS11.CKM_AES_KEY_GEN, template)
                
            elif algorithm.startswith('RSA'):
                # Generate RSA key pair
                pub_template = [
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_PUBLIC_KEY),
                    (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA),
                    (PyKCS11.CKA_MODULUS_BITS, key_size),
                    (PyKCS11.CKA_PUBLIC_EXPONENT, (0x01, 0x00, 0x01)),
                    (PyKCS11.CKA_LABEL, f"{key_id}_pub"),
                    (PyKCS11.CKA_TOKEN, True),
                    (PyKCS11.CKA_ENCRYPT, True),
                    (PyKCS11.CKA_VERIFY, True),
                ]
                
                priv_template = [
                    (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
                    (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA),
                    (PyKCS11.CKA_LABEL, f"{key_id}_priv"),
                    (PyKCS11.CKA_TOKEN, True),
                    (PyKCS11.CKA_PRIVATE, True),
                    (PyKCS11.CKA_DECRYPT, True),
                    (PyKCS11.CKA_SIGN, True),
                ]
                
                pub_key, priv_key = self.session.generateKeyPair(
                    PyKCS11.CKM_RSA_PKCS_KEY_PAIR_GEN, pub_template, priv_template
                )
                key_handle = priv_key
            
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Store key metadata
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_size=key_size,
                created_at=datetime.utcnow(),
                expires_at=None,
                rotation_schedule=None
            )
            self.key_metadata[key_id] = metadata
            
            logger.info(f"Generated {algorithm}-{key_size} key: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise


class AWSKMSHSM(BaseHSM):
    """AWS KMS HSM implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not AWS_KMS_AVAILABLE:
            raise ImportError("boto3 not available. Install with: pip install boto3")
        
        self.region = config.get('region', 'us-east-1')
        self.aws_access_key_id = config.get('aws_access_key_id') or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = config.get('aws_secret_access_key') or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.kms_client = None
    
    async def connect(self) -> bool:
        """Connect to AWS KMS."""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region
            )
            self.kms_client = session.client('kms')
            
            # Test connection
            response = self.kms_client.list_keys(Limit=1)
            
            self.is_connected = True
            logger.info("Connected to AWS KMS")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to AWS KMS: {str(e)}")
            return False
    
    async def generate_key(self, key_type: KeyType, algorithm: str, 
                          key_size: int, key_id: Optional[str] = None) -> str:
        """Generate key in AWS KMS."""
        try:
            if not self.is_connected:
                await self.connect()
            
            description = f"{key_type.value} key for Ainflue platform"
            
            # Determine key spec based on algorithm and size
            if algorithm.startswith('AES'):
                key_spec = 'SYMMETRIC_DEFAULT'
                key_usage = 'ENCRYPT_DECRYPT'
            elif algorithm.startswith('RSA'):
                if key_size == 2048:
                    key_spec = 'RSA_2048'
                elif key_size == 3072:
                    key_spec = 'RSA_3072'
                elif key_size == 4096:
                    key_spec = 'RSA_4096'
                else:
                    raise ValueError(f"Unsupported RSA key size: {key_size}")
                key_usage = 'ENCRYPT_DECRYPT'
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            response = self.kms_client.create_key(
                Description=description,
                KeyUsage=key_usage,
                KeySpec=key_spec,
                Tags=[
                    {'TagKey': 'KeyType', 'TagValue': key_type.value},
                    {'TagKey': 'Algorithm', 'TagValue': algorithm},
                    {'TagKey': 'Platform', 'TagValue': 'Ainflue'},
                    {'TagKey': 'CreatedAt', 'TagValue': datetime.utcnow().isoformat()}
                ]
            )
            
            key_id = response['KeyMetadata']['KeyId']
            
            # Store key metadata
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_size=key_size,
                created_at=datetime.utcnow(),
                expires_at=None,
                rotation_schedule=None
            )
            self.key_metadata[key_id] = metadata
            
            logger.info(f"Generated AWS KMS key: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"AWS KMS key generation failed: {str(e)}")
            raise
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data with AWS KMS key."""
        try:
            response = self.kms_client.encrypt(
                KeyId=key_id,
                Plaintext=plaintext
            )
            return response['CiphertextBlob']
            
        except Exception as e:
            logger.error(f"AWS KMS encryption failed: {str(e)}")
            raise
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data with AWS KMS key."""
        try:
            response = self.kms_client.decrypt(
                CiphertextBlob=ciphertext
            )
            return response['Plaintext']
            
        except Exception as e:
            logger.error(f"AWS KMS decryption failed: {str(e)}")
            raise


class LocalHSM(BaseHSM):
    """Software-based HSM for development and testing."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.key_storage_path = config.get('storage_path', './keys')
        self.keys: Dict[str, bytes] = {}
        os.makedirs(self.key_storage_path, exist_ok=True)
    
    async def connect(self) -> bool:
        """Connect to local HSM."""
        try:
            # Load existing keys
            for file_path in os.listdir(self.key_storage_path):
                if file_path.endswith('.key'):
                    key_id = file_path[:-4]  # Remove .key extension
                    with open(os.path.join(self.key_storage_path, file_path), 'rb') as f:
                        self.keys[key_id] = f.read()
            
            self.is_connected = True
            logger.info(f"Connected to local HSM with {len(self.keys)} keys")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to local HSM: {str(e)}")
            return False
    
    async def generate_key(self, key_type: KeyType, algorithm: str, 
                          key_size: int, key_id: Optional[str] = None) -> str:
        """Generate key in local HSM."""
        try:
            if not key_id:
                key_id = f"{key_type.value}_{secrets.token_hex(8)}"
            
            # Generate random key
            key_bytes = secrets.token_bytes(key_size // 8)
            
            # Store key
            self.keys[key_id] = key_bytes
            
            # Save to file
            key_file_path = os.path.join(self.key_storage_path, f"{key_id}.key")
            with open(key_file_path, 'wb') as f:
                f.write(key_bytes)
            
            # Store metadata
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_size=key_size,
                created_at=datetime.utcnow(),
                expires_at=None,
                rotation_schedule=None
            )
            self.key_metadata[key_id] = metadata
            
            # Save metadata
            metadata_file = os.path.join(self.key_storage_path, f"{key_id}.meta")
            with open(metadata_file, 'w') as f:
                json.dump(metadata.to_dict(), f, indent=2)
            
            logger.info(f"Generated local key: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"Local key generation failed: {str(e)}")
            raise
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data with local key (simplified implementation)."""
        try:
            if key_id not in self.keys:
                raise ValueError(f"Key {key_id} not found")
            
            # Simple XOR encryption for demonstration
            # In real implementation, use proper AES encryption
            key = self.keys[key_id]
            ciphertext = bytearray()
            
            for i, byte in enumerate(plaintext):
                ciphertext.append(byte ^ key[i % len(key)])
            
            return bytes(ciphertext)
            
        except Exception as e:
            logger.error(f"Local encryption failed: {str(e)}")
            raise
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data with local key."""
        # XOR is symmetric, so decryption is same as encryption
        return await self.encrypt(key_id, ciphertext)


class HSMManager:
    """Manager for HSM operations with multiple backend support."""
    
    def __init__(self, backend: HSMBackend = HSMBackend.LOCAL_HSM, config: Dict[str, Any] = None):
        self.backend = backend
        self.config = config or {}
        self.hsm = None
        self.initialize_hsm()
    
    def initialize_hsm(self):
        """Initialize HSM based on backend type."""
        try:
            if self.backend == HSMBackend.PKCS11:
                self.hsm = PKCS11HSM(self.config)
            elif self.backend == HSMBackend.AWS_KMS:
                self.hsm = AWSKMSHSM(self.config)
            elif self.backend == HSMBackend.LOCAL_HSM:
                self.hsm = LocalHSM(self.config)
            else:
                raise ValueError(f"Unsupported HSM backend: {self.backend}")
            
            logger.info(f"Initialized HSM manager with {self.backend.value} backend")
            
        except Exception as e:
            logger.error(f"HSM initialization failed: {str(e)}")
            raise
    
    async def connect(self) -> bool:
        """Connect to HSM."""
        return await self.hsm.connect()
    
    async def create_master_key(self) -> str:
        """Create master encryption key."""
        return await self.hsm.generate_key(
            KeyType.MASTER_KEY,
            "AES-256",
            256,
            "ainflue_master_key"
        )
    
    async def create_data_encryption_key(self, purpose: str) -> str:
        """Create data encryption key for specific purpose."""
        key_id = f"dek_{purpose}_{secrets.token_hex(4)}"
        return await self.hsm.generate_key(
            KeyType.DATA_ENCRYPTION_KEY,
            "AES-256",
            256,
            key_id
        )
    
    async def encrypt_data(self, key_id: str, data: bytes) -> bytes:
        """Encrypt data using specified key."""
        return await self.hsm.encrypt(key_id, data)
    
    async def decrypt_data(self, key_id: str, encrypted_data: bytes) -> bytes:
        """Decrypt data using specified key."""
        return await self.hsm.decrypt(key_id, encrypted_data)
    
    async def rotate_key(self, old_key_id: str) -> str:
        """Rotate key and return new key ID."""
        if hasattr(self.hsm, 'rotate_key'):
            return await self.hsm.rotate_key(old_key_id)
        else:
            # Manual rotation: create new key
            metadata = self.hsm.key_metadata.get(old_key_id)
            if metadata:
                new_key_id = await self.hsm.generate_key(
                    metadata.key_type,
                    metadata.algorithm,
                    metadata.key_size
                )
                logger.info(f"Rotated key {old_key_id} -> {new_key_id}")
                return new_key_id
            else:
                raise ValueError(f"Key metadata not found for {old_key_id}")
    
    def get_key_info(self, key_id: str) -> Optional[KeyMetadata]:
        """Get key metadata."""
        return self.hsm.key_metadata.get(key_id)
    
    async def cleanup_expired_keys(self):
        """Clean up expired keys."""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key_id, metadata in self.hsm.key_metadata.items():
            if metadata.expires_at and current_time > metadata.expires_at:
                expired_keys.append(key_id)
        
        for key_id in expired_keys:
            try:
                await self.hsm.delete_key(key_id)
                del self.hsm.key_metadata[key_id]
                logger.info(f"Deleted expired key: {key_id}")
            except Exception as e:
                logger.error(f"Failed to delete expired key {key_id}: {str(e)}")


# Global HSM manager instance
hsm_manager = None


def get_hsm_manager(backend: HSMBackend = HSMBackend.LOCAL_HSM, 
                   config: Dict[str, Any] = None) -> HSMManager:
    """Get HSM manager instance."""
    global hsm_manager
    
    if hsm_manager is None:
        hsm_manager = HSMManager(backend, config)
    
    return hsm_manager


async def initialize_hsm(backend: HSMBackend = HSMBackend.LOCAL_HSM, 
                        config: Dict[str, Any] = None) -> HSMManager:
    """Initialize HSM manager and connect."""
    manager = get_hsm_manager(backend, config)
    await manager.connect()
    return manager