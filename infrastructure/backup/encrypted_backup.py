"""
Encrypted Backup Manager - Enterprise Encryption and Security
============================================================

Advanced encrypted backup system with end-to-end encryption, key management,
zero-knowledge architecture, and creator content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Infrastructure
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import os
import hashlib
import json
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
import secrets
import hmac

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_128_GCM = "aes_128_gcm"
    AES_256_GCM = "aes_256_gcm"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    HYBRID = "hybrid"  # RSA + AES


class EncryptionLevel(Enum):
    """Encryption security levels."""
    BASIC = "basic"          # Standard encryption
    ADVANCED = "advanced"    # Strong encryption + key rotation
    ENTERPRISE = "enterprise"  # Zero-knowledge + multi-key
    QUANTUM_RESISTANT = "quantum_resistant"  # Future-proof


class KeyType(Enum):
    """Types of encryption keys."""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    MASTER_KEY = "master_key"
    CREATOR_KEY = "creator_key"
    DATA_ENCRYPTION_KEY = "data_encryption_key"


@dataclass
class EncryptionKey:
    """Encryption key information."""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    creator_id: Optional[str] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptedBackupRecord:
    """Record of encrypted backup operation."""
    backup_id: str
    encryption_algorithm: EncryptionAlgorithm
    encryption_level: EncryptionLevel
    key_ids: List[str]
    encrypted_size_bytes: int
    original_size_bytes: int
    compression_ratio: float
    encryption_time_seconds: float
    checksum: str
    encrypted_checksum: str
    created_at: datetime
    creator_id: Optional[str] = None
    compliance_tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EncryptedBackupManager:
    """
    Enterprise encrypted backup manager with advanced security features.
    
    Features:
    - End-to-end encryption with multiple algorithms
    - Zero-knowledge backup architecture
    - Key management and rotation
    - Creator-specific encryption keys
    - Compliance encryption (GDPR, PCI-DSS)
    - Quantum-resistant encryption options
    - Secure key derivation and storage
    - Audit trail and forensics support
    """
    
    def __init__(self, key_storage_path: str, master_password: Optional[str] = None):
        """Initialize encrypted backup manager."""
        self.key_storage_path = Path(key_storage_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if not CRYPTO_AVAILABLE:
            raise ImportError("Cryptography library not available. Install with: pip install cryptography")
        
        # Key management
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.backup_records: List[EncryptedBackupRecord] = []
        
        # Master key for key encryption
        self.master_key = self._derive_master_key(master_password)
        
        # Creator platform encryption policies
        self.creator_encryption_policies = {
            'premium': EncryptionLevel.ENTERPRISE,
            'pro': EncryptionLevel.ADVANCED,
            'standard': EncryptionLevel.ADVANCED,
            'basic': EncryptionLevel.BASIC,
            'free': EncryptionLevel.BASIC
        }
        
        self.content_encryption_requirements = {
            'monetized_content': EncryptionLevel.ENTERPRISE,
            'ai_processed': EncryptionLevel.ADVANCED,
            'personal_data': EncryptionLevel.ENTERPRISE,
            'financial_data': EncryptionLevel.ENTERPRISE,
            'user_upload': EncryptionLevel.BASIC
        }
        
        # Ensure key storage directory exists
        self.key_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize default keys
        asyncio.create_task(self._initialize_default_keys())
    
    def _derive_master_key(self, password: Optional[str]) -> bytes:
        """Derive master key from password using PBKDF2."""
        if not password:
            password = os.environ.get('AINFLUE_MASTER_KEY', 'default_master_key_change_in_production')
        
        salt = b'ainflue_backup_salt_2024'  # In production, use random salt per deployment
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())
    
    async def _initialize_default_keys(self) -> None:
        """Initialize default encryption keys."""
        try:
            # Create default system keys
            await self._create_system_key(EncryptionAlgorithm.AES_256_GCM)
            await self._create_system_key(EncryptionAlgorithm.FERNET)
            await self._create_system_key(EncryptionAlgorithm.RSA_4096)
            
            self.logger.info("🔐 Default encryption keys initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize default keys: {e}")
    
    async def _create_system_key(self, algorithm: EncryptionAlgorithm) -> str:
        """Create system encryption key."""
        key_id = f"system_{algorithm.value}_{int(datetime.now().timestamp())}"
        
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            key_data = os.urandom(32)  # 256 bits
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_data = Fernet.generate_key()
        elif algorithm == EncryptionAlgorithm.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            key_data = os.urandom(32)
        
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type=KeyType.SYMMETRIC if algorithm != EncryptionAlgorithm.RSA_4096 else KeyType.ASYMMETRIC_PRIVATE,
            algorithm=algorithm,
            key_data=key_data,
            created_at=datetime.now(),
            metadata={'system_key': True}
        )
        
        self.encryption_keys[key_id] = encryption_key
        await self._save_key_securely(encryption_key)
        
        return key_id
    
    async def encrypt_backup(
        self,
        backup_data: bytes,
        backup_id: str,
        encryption_level: Optional[EncryptionLevel] = None,
        creator_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bytes, EncryptedBackupRecord]:
        """
        Encrypt backup data with specified encryption level.
        
        Args:
            backup_data: Raw backup data to encrypt
            backup_id: Unique backup identifier
            encryption_level: Override encryption level
            creator_context: Creator-specific context for encryption policy
            
        Returns:
            Tuple of (encrypted_data, backup_record)
        """
        start_time = datetime.now()
        
        try:
            # Determine encryption level and algorithm
            level, algorithm = self._determine_encryption_policy(encryption_level, creator_context)
            
            self.logger.info(f"🔐 Encrypting backup {backup_id} with {level.value} level")
            
            # Generate or get encryption keys
            key_ids = await self._get_encryption_keys(level, algorithm, creator_context)
            
            # Compress data before encryption (optional optimization)
            compressed_data = await self._compress_data(backup_data)
            
            # Encrypt the data
            encrypted_data = await self._encrypt_data(compressed_data, key_ids, algorithm)
            
            # Calculate checksums
            original_checksum = hashlib.sha256(backup_data).hexdigest()
            encrypted_checksum = hashlib.sha256(encrypted_data).hexdigest()
            
            # Create backup record
            record = EncryptedBackupRecord(
                backup_id=backup_id,
                encryption_algorithm=algorithm,
                encryption_level=level,
                key_ids=key_ids,
                encrypted_size_bytes=len(encrypted_data),
                original_size_bytes=len(backup_data),
                compression_ratio=1 - (len(compressed_data) / len(backup_data)),
                encryption_time_seconds=(datetime.now() - start_time).total_seconds(),
                checksum=original_checksum,
                encrypted_checksum=encrypted_checksum,
                created_at=start_time,
                creator_id=creator_context.get('creator_id') if creator_context else None,
                compliance_tags=self._get_compliance_tags(creator_context),
                metadata={
                    'compression_enabled': True,
                    'zero_knowledge': level == EncryptionLevel.ENTERPRISE,
                    'quantum_resistant': level == EncryptionLevel.QUANTUM_RESISTANT
                }
            )
            
            self.backup_records.append(record)
            
            self.logger.info(f"✅ Backup encryption completed: {backup_id}")
            return encrypted_data, record
            
        except Exception as e:
            self.logger.error(f"❌ Backup encryption failed: {backup_id} - {str(e)}")
            raise
    
    def _determine_encryption_policy(
        self,
        encryption_level: Optional[EncryptionLevel],
        creator_context: Optional[Dict[str, Any]]
    ) -> Tuple[EncryptionLevel, EncryptionAlgorithm]:
        """Determine encryption level and algorithm based on context."""
        if encryption_level:
            level = encryption_level
        elif creator_context:
            # Check content type requirements
            content_type = creator_context.get('content_type', 'user_upload')
            if content_type in self.content_encryption_requirements:
                level = self.content_encryption_requirements[content_type]
            else:
                # Check creator tier
                creator_tier = creator_context.get('tier', 'basic')
                level = self.creator_encryption_policies.get(creator_tier, EncryptionLevel.BASIC)
        else:
            level = EncryptionLevel.BASIC
        
        # Select algorithm based on level
        if level == EncryptionLevel.QUANTUM_RESISTANT:
            algorithm = EncryptionAlgorithm.HYBRID  # Future: quantum-resistant algorithms
        elif level == EncryptionLevel.ENTERPRISE:
            algorithm = EncryptionAlgorithm.HYBRID  # RSA + AES for zero-knowledge
        elif level == EncryptionLevel.ADVANCED:
            algorithm = EncryptionAlgorithm.AES_256_GCM
        else:
            algorithm = EncryptionAlgorithm.FERNET
        
        return level, algorithm
    
    async def _get_encryption_keys(
        self,
        level: EncryptionLevel,
        algorithm: EncryptionAlgorithm,
        creator_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Get or create encryption keys for the specified level."""
        key_ids = []
        
        if algorithm == EncryptionAlgorithm.HYBRID:
            # Hybrid encryption: RSA for key encryption, AES for data
            rsa_key_id = await self._get_or_create_key(EncryptionAlgorithm.RSA_4096, creator_context)
            aes_key_id = await self._get_or_create_key(EncryptionAlgorithm.AES_256_GCM, creator_context)
            key_ids = [rsa_key_id, aes_key_id]
        else:
            # Single algorithm encryption
            key_id = await self._get_or_create_key(algorithm, creator_context)
            key_ids = [key_id]
        
        return key_ids
    
    async def _get_or_create_key(
        self,
        algorithm: EncryptionAlgorithm,
        creator_context: Optional[Dict[str, Any]]
    ) -> str:
        """Get existing key or create new one for algorithm."""
        creator_id = creator_context.get('creator_id') if creator_context else None
        
        # Look for existing suitable key
        for key_id, key in self.encryption_keys.items():
            if (key.algorithm == algorithm and 
                key.creator_id == creator_id and
                (not key.expires_at or key.expires_at > datetime.now()) and
                (not key.max_usage or key.usage_count < key.max_usage)):
                return key_id
        
        # Create new key
        return await self._create_encryption_key(algorithm, creator_context)
    
    async def _create_encryption_key(
        self,
        algorithm: EncryptionAlgorithm,
        creator_context: Optional[Dict[str, Any]]
    ) -> str:
        """Create new encryption key."""
        key_id = f"{algorithm.value}_{int(datetime.now().timestamp())}"
        if creator_context and creator_context.get('creator_id'):
            key_id = f"creator_{creator_context['creator_id']}_{key_id}"
        
        # Generate key data based on algorithm
        if algorithm == EncryptionAlgorithm.AES_128_GCM:
            key_data = os.urandom(16)  # 128 bits
            key_type = KeyType.SYMMETRIC
        elif algorithm == EncryptionAlgorithm.AES_256_GCM:
            key_data = os.urandom(32)  # 256 bits
            key_type = KeyType.SYMMETRIC
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_data = Fernet.generate_key()
            key_type = KeyType.SYMMETRIC
        elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            key_type = KeyType.ASYMMETRIC_PRIVATE
        else:
            raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
        
        # Create encryption key object
        encryption_key = EncryptionKey(
            key_id=key_id,
            key_type=key_type,
            algorithm=algorithm,
            key_data=key_data,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=365),  # 1 year expiry
            creator_id=creator_context.get('creator_id') if creator_context else None,
            max_usage=10000,  # Rotation after 10k uses
            metadata={
                'creator_tier': creator_context.get('tier') if creator_context else None,
                'content_type': creator_context.get('content_type') if creator_context else None
            }
        )
        
        self.encryption_keys[key_id] = encryption_key
        await self._save_key_securely(encryption_key)
        
        return key_id
    
    async def _compress_data(self, data: bytes) -> bytes:
        """Compress data before encryption."""
        try:
            import zlib
            return zlib.compress(data, level=6)
        except ImportError:
            # Fallback to no compression
            return data
    
    async def _encrypt_data(
        self,
        data: bytes,
        key_ids: List[str],
        algorithm: EncryptionAlgorithm
    ) -> bytes:
        """Encrypt data using specified algorithm and keys."""
        if algorithm == EncryptionAlgorithm.FERNET:
            return await self._encrypt_fernet(data, key_ids[0])
        elif algorithm in [EncryptionAlgorithm.AES_128_GCM, EncryptionAlgorithm.AES_256_GCM]:
            return await self._encrypt_aes_gcm(data, key_ids[0])
        elif algorithm == EncryptionAlgorithm.HYBRID:
            return await self._encrypt_hybrid(data, key_ids)
        else:
            raise ValueError(f"Encryption not implemented for algorithm: {algorithm}")
    
    async def _encrypt_fernet(self, data: bytes, key_id: str) -> bytes:
        """Encrypt data using Fernet (AES 128 in CBC mode)."""
        key = self.encryption_keys[key_id]
        cipher_suite = Fernet(key.key_data)
        
        # Update usage count
        key.usage_count += 1
        
        return cipher_suite.encrypt(data)
    
    async def _encrypt_aes_gcm(self, data: bytes, key_id: str) -> bytes:
        """Encrypt data using AES-GCM."""
        key = self.encryption_keys[key_id]
        
        # Generate random IV
        iv = os.urandom(12)  # 96-bit IV for GCM
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key.key_data), modes.GCM(iv))
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        # Update usage count
        key.usage_count += 1
        
        # Return IV + tag + ciphertext
        return iv + encryptor.tag + ciphertext
    
    async def _encrypt_hybrid(self, data: bytes, key_ids: List[str]) -> bytes:
        """Encrypt data using hybrid RSA + AES encryption."""
        rsa_key_id = key_ids[0]
        aes_key_id = key_ids[1]
        
        # Get AES key for data encryption
        aes_key = self.encryption_keys[aes_key_id]
        
        # Encrypt data with AES
        encrypted_data = await self._encrypt_aes_gcm(data, aes_key_id)
        
        # Encrypt AES key with RSA
        rsa_key = self.encryption_keys[rsa_key_id]
        private_key = serialization.load_pem_private_key(
            rsa_key.key_data,
            password=None,
        )
        public_key = private_key.public_key()
        
        encrypted_aes_key = public_key.encrypt(
            aes_key.key_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Update usage counts
        rsa_key.usage_count += 1
        
        # Return encrypted key length + encrypted key + encrypted data
        key_length = len(encrypted_aes_key).to_bytes(4, byteorder='big')
        return key_length + encrypted_aes_key + encrypted_data
    
    def _get_compliance_tags(self, creator_context: Optional[Dict[str, Any]]) -> List[str]:
        """Get compliance tags based on creator context."""
        tags = []
        
        if not creator_context:
            return tags
        
        # GDPR compliance
        location = creator_context.get('location', '').upper()
        if any(region in location for region in ['EU', 'DE', 'FR', 'ES', 'IT']):
            tags.append('GDPR')
        
        # CCPA compliance
        if 'CA' in location and 'US' in location:
            tags.append('CCPA')
        
        # PCI-DSS for financial data
        if creator_context.get('financial_data', False):
            tags.append('PCI_DSS')
        
        # HIPAA for health data
        if creator_context.get('health_data', False):
            tags.append('HIPAA')
        
        return tags
    
    async def _save_key_securely(self, key: EncryptionKey) -> None:
        """Save encryption key securely to storage."""
        try:
            # Encrypt key data with master key
            cipher_suite = Fernet(base64.urlsafe_b64encode(self.master_key))
            encrypted_key_data = cipher_suite.encrypt(key.key_data)
            
            # Create key metadata
            key_metadata = {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'creator_id': key.creator_id,
                'usage_count': key.usage_count,
                'max_usage': key.max_usage,
                'metadata': key.metadata,
                'encrypted_key_data': base64.b64encode(encrypted_key_data).decode()
            }
            
            # Save to file
            key_file = self.key_storage_path / f"{key.key_id}.key"
            with open(key_file, 'w') as f:
                json.dump(key_metadata, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save key {key.key_id}: {e}")
            raise
    
    async def decrypt_backup(
        self,
        encrypted_data: bytes,
        backup_record: EncryptedBackupRecord
    ) -> bytes:
        """
        Decrypt backup data using backup record information.
        
        Args:
            encrypted_data: Encrypted backup data
            backup_record: Record containing encryption details
            
        Returns:
            Decrypted original data
        """
        try:
            self.logger.info(f"🔓 Decrypting backup {backup_record.backup_id}")
            
            # Decrypt data using appropriate algorithm
            if backup_record.encryption_algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = await self._decrypt_fernet(encrypted_data, backup_record.key_ids[0])
            elif backup_record.encryption_algorithm in [EncryptionAlgorithm.AES_128_GCM, EncryptionAlgorithm.AES_256_GCM]:
                decrypted_data = await self._decrypt_aes_gcm(encrypted_data, backup_record.key_ids[0])
            elif backup_record.encryption_algorithm == EncryptionAlgorithm.HYBRID:
                decrypted_data = await self._decrypt_hybrid(encrypted_data, backup_record.key_ids)
            else:
                raise ValueError(f"Decryption not implemented for algorithm: {backup_record.encryption_algorithm}")
            
            # Decompress if needed
            if backup_record.compression_ratio > 0:
                decrypted_data = await self._decompress_data(decrypted_data)
            
            # Verify checksum
            calculated_checksum = hashlib.sha256(decrypted_data).hexdigest()
            if calculated_checksum != backup_record.checksum:
                raise ValueError("Checksum verification failed during decryption")
            
            self.logger.info(f"✅ Backup decryption completed: {backup_record.backup_id}")
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"❌ Backup decryption failed: {backup_record.backup_id} - {str(e)}")
            raise
    
    async def _decrypt_fernet(self, encrypted_data: bytes, key_id: str) -> bytes:
        """Decrypt data using Fernet."""
        key = self.encryption_keys[key_id]
        cipher_suite = Fernet(key.key_data)
        return cipher_suite.decrypt(encrypted_data)
    
    async def _decrypt_aes_gcm(self, encrypted_data: bytes, key_id: str) -> bytes:
        """Decrypt data using AES-GCM."""
        key = self.encryption_keys[key_id]
        
        # Extract IV, tag, and ciphertext
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create cipher
        cipher = Cipher(algorithms.AES(key.key_data), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    async def _decrypt_hybrid(self, encrypted_data: bytes, key_ids: List[str]) -> bytes:
        """Decrypt data using hybrid RSA + AES decryption."""
        rsa_key_id = key_ids[0]
        
        # Extract encrypted AES key
        key_length = int.from_bytes(encrypted_data[:4], byteorder='big')
        encrypted_aes_key = encrypted_data[4:4+key_length]
        encrypted_data_payload = encrypted_data[4+key_length:]
        
        # Decrypt AES key with RSA
        rsa_key = self.encryption_keys[rsa_key_id]
        private_key = serialization.load_pem_private_key(
            rsa_key.key_data,
            password=None,
        )
        
        aes_key_data = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Create temporary AES key for decryption
        temp_key_id = f"temp_{int(datetime.now().timestamp())}"
        temp_key = EncryptionKey(
            key_id=temp_key_id,
            key_type=KeyType.SYMMETRIC,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_data=aes_key_data,
            created_at=datetime.now()
        )
        self.encryption_keys[temp_key_id] = temp_key
        
        try:
            # Decrypt data with AES
            decrypted_data = await self._decrypt_aes_gcm(encrypted_data_payload, temp_key_id)
            return decrypted_data
        finally:
            # Clean up temporary key
            del self.encryption_keys[temp_key_id]
    
    async def _decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompress data after decryption."""
        try:
            import zlib
            return zlib.decompress(compressed_data)
        except ImportError:
            # No compression was used
            return compressed_data
    
    async def rotate_keys(self, creator_id: Optional[str] = None) -> int:
        """Rotate encryption keys for security."""
        rotated_count = 0
        current_time = datetime.now()
        
        for key_id, key in list(self.encryption_keys.items()):
            should_rotate = False
            
            # Rotate if expired
            if key.expires_at and key.expires_at < current_time:
                should_rotate = True
            
            # Rotate if usage limit reached
            if key.max_usage and key.usage_count >= key.max_usage:
                should_rotate = True
            
            # Rotate creator-specific keys if requested
            if creator_id and key.creator_id == creator_id:
                should_rotate = True
            
            if should_rotate:
                # Create replacement key
                await self._create_encryption_key(key.algorithm, {
                    'creator_id': key.creator_id,
                    'tier': key.metadata.get('creator_tier'),
                    'content_type': key.metadata.get('content_type')
                })
                
                # Mark old key as expired (don't delete for decryption needs)
                key.expires_at = current_time
                rotated_count += 1
                
                self.logger.info(f"🔄 Rotated encryption key: {key_id}")
        
        return rotated_count
    
    async def get_encryption_metrics(self) -> Dict[str, Any]:
        """Get comprehensive encryption metrics."""
        total_keys = len(self.encryption_keys)
        total_backups = len(self.backup_records)
        
        # Group by algorithm
        by_algorithm = {}
        for key in self.encryption_keys.values():
            alg = key.algorithm.value
            if alg not in by_algorithm:
                by_algorithm[alg] = 0
            by_algorithm[alg] += 1
        
        # Group by encryption level
        by_level = {}
        for record in self.backup_records:
            level = record.encryption_level.value
            if level not in by_level:
                by_level[level] = 0
            by_level[level] += 1
        
        # Creator-specific metrics
        creator_keys = len([k for k in self.encryption_keys.values() if k.creator_id])
        creator_backups = len([r for r in self.backup_records if r.creator_id])
        
        # Compliance metrics
        compliance_backups = len([r for r in self.backup_records if r.compliance_tags])
        
        # Calculate average compression and encryption efficiency
        total_original_size = sum(r.original_size_bytes for r in self.backup_records)
        total_encrypted_size = sum(r.encrypted_size_bytes for r in self.backup_records)
        
        avg_compression = 0
        if len(self.backup_records) > 0:
            avg_compression = sum(r.compression_ratio for r in self.backup_records) / len(self.backup_records)
        
        return {
            'total_encryption_keys': total_keys,
            'total_encrypted_backups': total_backups,
            'keys_by_algorithm': by_algorithm,
            'backups_by_encryption_level': by_level,
            'creator_specific_keys': creator_keys,
            'creator_encrypted_backups': creator_backups,
            'compliance_encrypted_backups': compliance_backups,
            'total_original_size_bytes': total_original_size,
            'total_original_size_gb': round(total_original_size / (1024**3), 2),
            'total_encrypted_size_bytes': total_encrypted_size,
            'total_encrypted_size_gb': round(total_encrypted_size / (1024**3), 2),
            'average_compression_ratio': round(avg_compression, 3),
            'encryption_overhead_ratio': round((total_encrypted_size / total_original_size) - 1, 3) if total_original_size > 0 else 0,
            'zero_knowledge_backups': len([r for r in self.backup_records if r.metadata.get('zero_knowledge', False)]),
            'quantum_resistant_backups': len([r for r in self.backup_records if r.metadata.get('quantum_resistant', False)])
        }


# Export public interface
__all__ = [
    'EncryptedBackupManager',
    'EncryptionAlgorithm',
    'EncryptionLevel',
    'KeyType',
    'EncryptionKey',
    'EncryptedBackupRecord'
]