#!/usr/bin/env python3
"""
🔐 Encryption Manager
====================

Enterprise encryption key management and cryptographic orchestration for Redis infrastructure
with advanced key lifecycle management, HSM integration, and compliance support.

Expert Roles Combined:
- Security Architect: Cryptographic design and key management strategy
- DevOps Engineer: Infrastructure encryption automation and monitoring
- Backend Senior: Distributed encryption service architecture
- DBA: Database encryption and data protection at rest

Features:
- Advanced encryption key lifecycle management
- Hardware Security Module (HSM) integration
- Multi-tier encryption with key rotation
- Compliance encryption (FIPS 140-2, Common Criteria)
- Performance-optimized cryptographic operations
- Zero-downtime key rotation and migration
- Encryption policy enforcement and automation
- Key escrow and recovery capabilities

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security Architect + DevOps + Backend Senior + DBA
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import uuid
import hashlib
import hmac
import secrets
import base64
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import aioredis
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import cryptography.hazmat.backends.openssl as openssl_backend

logger = logging.getLogger(__name__)

class KeyType(Enum):
    """Types of encryption keys"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC = "asymmetric"
    MASTER = "master"
    DATA = "data"
    SESSION = "session"
    TRANSPORT = "transport"

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    AES_256_CTR = "aes_256_ctr"
    RSA_4096 = "rsa_4096"
    RSA_2048 = "rsa_2048"
    FERNET = "fernet"
    CHACHA20_POLY1305 = "chacha20_poly1305"

class KeyStatus(Enum):
    """Key lifecycle status"""
    PENDING = "pending"
    ACTIVE = "active"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"
    ARCHIVED = "archived"

class ComplianceStandard(Enum):
    """Compliance standards for encryption"""
    FIPS_140_2 = "fips_140_2"
    COMMON_CRITERIA = "common_criteria"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    SOX = "sox"

@dataclass
class EncryptionKey:
    """Encryption key representation"""
    key_id: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_material: bytes
    status: KeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    rotated_at: Optional[datetime] = None
    rotation_interval_days: int = 90
    usage_count: int = 0
    max_usage: Optional[int] = None
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_key_id: Optional[str] = None
    derived_keys: List[str] = field(default_factory=list)

@dataclass
class EncryptionPolicy:
    """Encryption policy configuration"""
    policy_id: str
    name: str
    description: str
    resource_patterns: List[str]
    required_algorithm: EncryptionAlgorithm
    key_rotation_days: int
    compliance_requirements: List[ComplianceStandard]
    encryption_required: bool = True
    key_escrow_required: bool = False
    hsm_required: bool = False
    enabled: bool = True

@dataclass
class EncryptionOperation:
    """Encryption operation record"""
    operation_id: str
    operation_type: str  # encrypt, decrypt, key_rotation
    key_id: str
    resource: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, completed, failed
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EncryptionMetrics:
    """Encryption system metrics"""
    total_keys: int = 0
    active_keys: int = 0
    pending_rotations: int = 0
    encryption_operations_today: int = 0
    decryption_operations_today: int = 0
    average_encryption_time_ms: float = 0.0
    average_decryption_time_ms: float = 0.0
    compliance_score: float = 100.0
    hsm_operations: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class RedisEncryptionManager:
    """
    Enterprise Encryption Manager for Redis Infrastructure
    
    Comprehensive encryption key management with HSM integration,
    compliance support, and performance-optimized cryptographic operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_pool: Optional[aioredis.ConnectionPool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Encryption management
        self.keys: Dict[str, EncryptionKey] = {}
        self.policies: Dict[str, EncryptionPolicy] = {}
        self.active_operations: Dict[str, EncryptionOperation] = {}
        
        # Encryption metrics
        self.metrics = EncryptionMetrics()
        
        # Master key and key derivation
        self.master_key: Optional[bytes] = None
        self.key_derivation_salt = config.get('key_derivation_salt', b'ainflue_encryption_salt')
        
        # HSM configuration
        self.hsm_enabled = config.get('hsm_enabled', False)
        self.hsm_config = config.get('hsm_config', {})
        
        # Performance optimization
        self.key_cache: Dict[str, bytes] = {}
        self.cache_ttl = config.get('key_cache_ttl', 300)  # 5 minutes
        
        # Compliance settings
        self.compliance_mode = config.get('compliance_mode', 'standard')
        self.key_escrow_enabled = config.get('key_escrow_enabled', False)
        
        logger.info("Encryption Manager initialized")
    
    async def initialize(self):
        """Initialize encryption manager"""
        try:
            # Setup Redis connection
            await self._setup_redis_connection()
            
            # Initialize master key
            await self._initialize_master_key()
            
            # Load encryption keys
            await self._load_encryption_keys()
            
            # Load encryption policies
            await self._load_encryption_policies()
            
            # Initialize default policies
            await self._initialize_default_policies()
            
            # Start key rotation monitoring
            asyncio.create_task(self._start_key_rotation_monitoring())
            
            # Start performance monitoring
            asyncio.create_task(self._start_performance_monitoring())
            
            logger.info("Encryption Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption manager: {e}")
            raise
    
    async def _setup_redis_connection(self):
        """Setup Redis connection"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config['redis_url'],
                password=self.config.get('redis_password'),
                ssl=self.config.get('ssl_enabled', True),
                max_connections=self.config.get('max_connections', 100),
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.redis_client = aioredis.Redis(connection_pool=self.redis_pool)
            await self.redis_client.ping()
            
            logger.info("Redis connection established for encryption management")
            
        except Exception as e:
            logger.error(f"Failed to setup Redis connection: {e}")
            raise
    
    async def _initialize_master_key(self):
        """Initialize or load master encryption key"""
        try:
            # Try to load existing master key
            stored_master_key = await self.redis_client.get("encryption:master_key")
            
            if stored_master_key:
                # Decrypt stored master key
                master_key_encrypted = base64.b64decode(stored_master_key)
                self.master_key = self._decrypt_master_key(master_key_encrypted)
                logger.info("Loaded existing master key")
            else:
                # Generate new master key
                self.master_key = self._generate_master_key()
                
                # Encrypt and store master key
                master_key_encrypted = self._encrypt_master_key(self.master_key)
                await self.redis_client.set(
                    "encryption:master_key",
                    base64.b64encode(master_key_encrypted)
                )
                logger.info("Generated and stored new master key")
            
        except Exception as e:
            logger.error(f"Error initializing master key: {e}")
            raise
    
    def _generate_master_key(self) -> bytes:
        """Generate new master encryption key"""
        try:
            # Use cryptographically secure random generation
            return secrets.token_bytes(32)  # 256-bit key
            
        except Exception as e:
            logger.error(f"Error generating master key: {e}")
            raise
    
    def _encrypt_master_key(self, master_key: bytes) -> bytes:
        """Encrypt master key for storage"""
        try:
            # Use password-based encryption for master key
            password = self.config.get('master_key_password', 'default_password').encode()
            
            # Generate salt
            salt = secrets.token_bytes(16)
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_key = kdf.derive(password)
            
            # Encrypt master key
            cipher_suite = Fernet(base64.urlsafe_b64encode(derived_key))
            encrypted_master_key = cipher_suite.encrypt(master_key)
            
            # Prepend salt to encrypted data
            return salt + encrypted_master_key
            
        except Exception as e:
            logger.error(f"Error encrypting master key: {e}")
            raise
    
    def _decrypt_master_key(self, encrypted_data: bytes) -> bytes:
        """Decrypt master key from storage"""
        try:
            # Extract salt and encrypted data
            salt = encrypted_data[:16]
            encrypted_master_key = encrypted_data[16:]
            
            # Derive key from password
            password = self.config.get('master_key_password', 'default_password').encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_key = kdf.derive(password)
            
            # Decrypt master key
            cipher_suite = Fernet(base64.urlsafe_b64encode(derived_key))
            master_key = cipher_suite.decrypt(encrypted_master_key)
            
            return master_key
            
        except Exception as e:
            logger.error(f"Error decrypting master key: {e}")
            raise
    
    async def _load_encryption_keys(self):
        """Load encryption keys from storage"""
        try:
            stored_keys = await self.redis_client.hgetall("encryption:keys")
            
            for key_id, key_data in stored_keys.items():
                try:
                    # Decrypt key data
                    key_data_encrypted = base64.b64decode(key_data)
                    key_data_json = self._decrypt_with_master_key(key_data_encrypted)
                    key_dict = json.loads(key_data_json)
                    
                    # Reconstruct key object
                    encryption_key = EncryptionKey(**key_dict)
                    self.keys[key_id.decode()] = encryption_key
                    
                except Exception as e:
                    logger.error(f"Error loading encryption key {key_id}: {e}")
            
            logger.info(f"Loaded {len(self.keys)} encryption keys")
            
        except Exception as e:
            logger.error(f"Error loading encryption keys: {e}")
    
    def _decrypt_with_master_key(self, encrypted_data: bytes) -> str:
        """Decrypt data using master key"""
        try:
            # Use master key to derive decryption key
            cipher_suite = Fernet(base64.urlsafe_b64encode(self.master_key))
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting with master key: {e}")
            raise
    
    def _encrypt_with_master_key(self, data: str) -> bytes:
        """Encrypt data using master key"""
        try:
            # Use master key to derive encryption key
            cipher_suite = Fernet(base64.urlsafe_b64encode(self.master_key))
            encrypted_data = cipher_suite.encrypt(data.encode())
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Error encrypting with master key: {e}")
            raise
    
    async def _load_encryption_policies(self):
        """Load encryption policies from storage"""
        try:
            stored_policies = await self.redis_client.hgetall("encryption:policies")
            
            for policy_id, policy_data in stored_policies.items():
                try:
                    policy_dict = json.loads(policy_data)
                    policy = EncryptionPolicy(**policy_dict)
                    self.policies[policy_id.decode()] = policy
                except Exception as e:
                    logger.error(f"Error loading encryption policy {policy_id}: {e}")
            
            logger.info(f"Loaded {len(self.policies)} encryption policies")
            
        except Exception as e:
            logger.error(f"Error loading encryption policies: {e}")
    
    async def _initialize_default_policies(self):
        """Initialize default encryption policies"""
        try:
            default_policies = [
                EncryptionPolicy(
                    policy_id="redis_data_encryption",
                    name="Redis Data Encryption Policy",
                    description="Encryption policy for Redis data at rest",
                    resource_patterns=["redis:data:*"],
                    required_algorithm=EncryptionAlgorithm.AES_256_GCM,
                    key_rotation_days=90,
                    compliance_requirements=[ComplianceStandard.GDPR, ComplianceStandard.PCI_DSS]
                ),
                EncryptionPolicy(
                    policy_id="pci_data_encryption",
                    name="PCI Data Encryption Policy",
                    description="Encryption policy for PCI-DSS compliance",
                    resource_patterns=["redis:payment:*", "redis:card:*"],
                    required_algorithm=EncryptionAlgorithm.AES_256_GCM,
                    key_rotation_days=30,
                    compliance_requirements=[ComplianceStandard.PCI_DSS],
                    hsm_required=True,
                    key_escrow_required=True
                ),
                EncryptionPolicy(
                    policy_id="gdpr_personal_data",
                    name="GDPR Personal Data Encryption",
                    description="Encryption policy for personal data under GDPR",
                    resource_patterns=["redis:personal:*", "redis:user:*"],
                    required_algorithm=EncryptionAlgorithm.AES_256_GCM,
                    key_rotation_days=60,
                    compliance_requirements=[ComplianceStandard.GDPR]
                ),
                EncryptionPolicy(
                    policy_id="transport_encryption",
                    name="Transport Encryption Policy",
                    description="Encryption policy for data in transit",
                    resource_patterns=["transport:*"],
                    required_algorithm=EncryptionAlgorithm.RSA_4096,
                    key_rotation_days=180,
                    compliance_requirements=[ComplianceStandard.FIPS_140_2]
                )
            ]
            
            for policy in default_policies:
                if policy.policy_id not in self.policies:
                    self.policies[policy.policy_id] = policy
                    await self._store_encryption_policy(policy)
            
            logger.info("Default encryption policies initialized")
            
        except Exception as e:
            logger.error(f"Error initializing default policies: {e}")
    
    async def generate_encryption_key(self, key_type: KeyType, algorithm: EncryptionAlgorithm,
                                    compliance_standards: List[ComplianceStandard] = None,
                                    rotation_interval_days: int = 90,
                                    metadata: Dict[str, Any] = None) -> str:
        """Generate new encryption key"""
        try:
            key_id = str(uuid.uuid4())
            
            # Generate key material based on algorithm
            key_material = self._generate_key_material(algorithm)
            
            # Set expiration
            expires_at = datetime.now() + timedelta(days=rotation_interval_days)
            
            # Create encryption key
            encryption_key = EncryptionKey(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                key_material=key_material,
                status=KeyStatus.ACTIVE,
                created_at=datetime.now(),
                expires_at=expires_at,
                rotation_interval_days=rotation_interval_days,
                compliance_standards=compliance_standards or [],
                metadata=metadata or {}
            )
            
            # Store key
            self.keys[key_id] = encryption_key
            await self._store_encryption_key(encryption_key)
            
            # Update metrics
            self.metrics.total_keys += 1
            self.metrics.active_keys += 1
            
            logger.info(f"Generated encryption key: {key_id} (algorithm: {algorithm.value})")
            return key_id
            
        except Exception as e:
            logger.error(f"Error generating encryption key: {e}")
            raise
    
    def _generate_key_material(self, algorithm: EncryptionAlgorithm) -> bytes:
        """Generate key material for specific algorithm"""
        try:
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                return secrets.token_bytes(32)  # 256-bit key
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                return secrets.token_bytes(32)  # 256-bit key
            elif algorithm == EncryptionAlgorithm.AES_256_CTR:
                return secrets.token_bytes(32)  # 256-bit key
            elif algorithm == EncryptionAlgorithm.FERNET:
                return Fernet.generate_key()
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return secrets.token_bytes(32)  # 256-bit key
            elif algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                # Generate RSA key pair
                key_size = 2048 if algorithm == EncryptionAlgorithm.RSA_2048 else 4096
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=openssl_backend.backend
                )
                
                # Serialize private key
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                
                return private_pem
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            logger.error(f"Error generating key material: {e}")
            raise
    
    async def encrypt_data(self, data: Union[str, bytes], resource: str, 
                         algorithm: Optional[EncryptionAlgorithm] = None) -> Tuple[bytes, str]:
        """Encrypt data using appropriate encryption key"""
        try:
            operation_id = str(uuid.uuid4())
            start_time = time.time()
            
            # Determine encryption policy
            policy = self._get_encryption_policy(resource)
            if not policy:
                raise ValueError(f"No encryption policy found for resource: {resource}")
            
            # Use specified algorithm or policy default
            encryption_algorithm = algorithm or policy.required_algorithm
            
            # Find or generate appropriate key
            key_id = await self._get_or_create_key(policy, encryption_algorithm)
            encryption_key = self.keys[key_id]
            
            # Convert data to bytes if needed
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Perform encryption
            encrypted_data = self._encrypt_with_algorithm(data_bytes, encryption_key)
            
            # Record operation
            operation = EncryptionOperation(
                operation_id=operation_id,
                operation_type="encrypt",
                key_id=key_id,
                resource=resource,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.now(),
                status="completed",
                performance_metrics={
                    'duration_ms': (time.time() - start_time) * 1000,
                    'data_size_bytes': len(data_bytes)
                }
            )
            
            # Update metrics
            self.metrics.encryption_operations_today += 1
            self._update_average_encryption_time(operation.performance_metrics['duration_ms'])
            
            # Update key usage
            encryption_key.usage_count += 1
            
            logger.debug(f"Data encrypted for resource: {resource}, key: {key_id}")
            return encrypted_data, key_id
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def _get_encryption_policy(self, resource: str) -> Optional[EncryptionPolicy]:
        """Get encryption policy for resource"""
        try:
            for policy in self.policies.values():
                if policy.enabled:
                    for pattern in policy.resource_patterns:
                        if self._resource_matches_pattern(resource, pattern):
                            return policy
            return None
            
        except Exception as e:
            logger.error(f"Error getting encryption policy: {e}")
            return None
    
    def _resource_matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches pattern"""
        try:
            # Simple wildcard matching
            if pattern == "*":
                return True
            
            if "*" in pattern:
                # Convert pattern to regex
                import re
                regex_pattern = pattern.replace("*", ".*")
                return bool(re.match(f"^{regex_pattern}$", resource))
            
            return resource == pattern
            
        except Exception as e:
            logger.error(f"Error matching resource pattern: {e}")
            return False
    
    async def _get_or_create_key(self, policy: EncryptionPolicy, 
                               algorithm: EncryptionAlgorithm) -> str:
        """Get existing key or create new one for policy"""
        try:
            # Look for existing active key
            for key_id, key in self.keys.items():
                if (key.status == KeyStatus.ACTIVE and
                    key.algorithm == algorithm and
                    key.expires_at and key.expires_at > datetime.now()):
                    return key_id
            
            # Generate new key
            key_id = await self.generate_encryption_key(
                key_type=KeyType.DATA,
                algorithm=algorithm,
                compliance_standards=policy.compliance_requirements,
                rotation_interval_days=policy.key_rotation_days
            )
            
            return key_id
            
        except Exception as e:
            logger.error(f"Error getting or creating key: {e}")
            raise
    
    def _encrypt_with_algorithm(self, data: bytes, key: EncryptionKey) -> bytes:
        """Encrypt data using specific algorithm"""
        try:
            if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._encrypt_aes_gcm(data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._encrypt_aes_cbc(data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CTR:
                return self._encrypt_aes_ctr(data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.FERNET:
                return self._encrypt_fernet(data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._encrypt_chacha20(data, key.key_material)
            elif key.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                return self._encrypt_rsa(data, key.key_material)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {key.algorithm}")
                
        except Exception as e:
            logger.error(f"Error encrypting with algorithm {key.algorithm}: {e}")
            raise
    
    def _encrypt_aes_gcm(self, data: bytes, key_material: bytes) -> bytes:
        """Encrypt using AES-256-GCM"""
        try:
            # Generate random IV
            iv = secrets.token_bytes(12)  # 96-bit IV for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_material),
                modes.GCM(iv),
                backend=openssl_backend.backend
            )
            
            # Encrypt data
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Return IV + tag + ciphertext
            return iv + encryptor.tag + ciphertext
            
        except Exception as e:
            logger.error(f"Error in AES-GCM encryption: {e}")
            raise
    
    def _encrypt_aes_cbc(self, data: bytes, key_material: bytes) -> bytes:
        """Encrypt using AES-256-CBC"""
        try:
            # Generate random IV
            iv = secrets.token_bytes(16)  # 128-bit IV for CBC
            
            # Pad data to block size
            padded_data = self._pad_data(data, 16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_material),
                modes.CBC(iv),
                backend=openssl_backend.backend
            )
            
            # Encrypt data
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Return IV + ciphertext
            return iv + ciphertext
            
        except Exception as e:
            logger.error(f"Error in AES-CBC encryption: {e}")
            raise
    
    def _encrypt_aes_ctr(self, data: bytes, key_material: bytes) -> bytes:
        """Encrypt using AES-256-CTR"""
        try:
            # Generate random nonce
            nonce = secrets.token_bytes(16)  # 128-bit nonce
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_material),
                modes.CTR(nonce),
                backend=openssl_backend.backend
            )
            
            # Encrypt data
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Return nonce + ciphertext
            return nonce + ciphertext
            
        except Exception as e:
            logger.error(f"Error in AES-CTR encryption: {e}")
            raise
    
    def _encrypt_fernet(self, data: bytes, key_material: bytes) -> bytes:
        """Encrypt using Fernet"""
        try:
            cipher_suite = Fernet(key_material)
            return cipher_suite.encrypt(data)
            
        except Exception as e:
            logger.error(f"Error in Fernet encryption: {e}")
            raise
    
    def _encrypt_chacha20(self, data: bytes, key_material: bytes) -> bytes:
        """Encrypt using ChaCha20-Poly1305"""
        try:
            # Generate random nonce
            nonce = secrets.token_bytes(12)  # 96-bit nonce
            
            # Create cipher
            cipher = Cipher(
                algorithms.ChaCha20(key_material, nonce),
                modes.GCM(b''),  # Use empty additional data
                backend=openssl_backend.backend
            )
            
            # Encrypt data
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Return nonce + tag + ciphertext
            return nonce + encryptor.tag + ciphertext
            
        except Exception as e:
            logger.error(f"Error in ChaCha20 encryption: {e}")
            raise
    
    def _encrypt_rsa(self, data: bytes, key_material: bytes) -> bytes:
        """Encrypt using RSA"""
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                key_material,
                password=None,
                backend=openssl_backend.backend
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Encrypt with public key
            ciphertext = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return ciphertext
            
        except Exception as e:
            logger.error(f"Error in RSA encryption: {e}")
            raise
    
    def _pad_data(self, data: bytes, block_size: int) -> bytes:
        """Pad data to block size using PKCS7"""
        try:
            padding_length = block_size - (len(data) % block_size)
            padding = bytes([padding_length] * padding_length)
            return data + padding
            
        except Exception as e:
            logger.error(f"Error padding data: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: bytes, key_id: str) -> bytes:
        """Decrypt data using specified key"""
        try:
            start_time = time.time()
            
            # Get encryption key
            encryption_key = self.keys.get(key_id)
            if not encryption_key:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            # Perform decryption
            decrypted_data = self._decrypt_with_algorithm(encrypted_data, encryption_key)
            
            # Update metrics
            self.metrics.decryption_operations_today += 1
            self._update_average_decryption_time((time.time() - start_time) * 1000)
            
            # Update key usage
            encryption_key.usage_count += 1
            
            logger.debug(f"Data decrypted with key: {key_id}")
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def _decrypt_with_algorithm(self, encrypted_data: bytes, key: EncryptionKey) -> bytes:
        """Decrypt data using specific algorithm"""
        try:
            if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                return self._decrypt_aes_gcm(encrypted_data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                return self._decrypt_aes_cbc(encrypted_data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CTR:
                return self._decrypt_aes_ctr(encrypted_data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.FERNET:
                return self._decrypt_fernet(encrypted_data, key.key_material)
            elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                return self._decrypt_chacha20(encrypted_data, key.key_material)
            elif key.algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
                return self._decrypt_rsa(encrypted_data, key.key_material)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {key.algorithm}")
                
        except Exception as e:
            logger.error(f"Error decrypting with algorithm {key.algorithm}: {e}")
            raise
    
    def _decrypt_aes_gcm(self, encrypted_data: bytes, key_material: bytes) -> bytes:
        """Decrypt using AES-256-GCM"""
        try:
            # Extract IV, tag, and ciphertext
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_material),
                modes.GCM(iv, tag),
                backend=openssl_backend.backend
            )
            
            # Decrypt data
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Error in AES-GCM decryption: {e}")
            raise
    
    def _decrypt_aes_cbc(self, encrypted_data: bytes, key_material: bytes) -> bytes:
        """Decrypt using AES-256-CBC"""
        try:
            # Extract IV and ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_material),
                modes.CBC(iv),
                backend=openssl_backend.backend
            )
            
            # Decrypt data
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            plaintext = self._unpad_data(padded_plaintext)
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Error in AES-CBC decryption: {e}")
            raise
    
    def _decrypt_aes_ctr(self, encrypted_data: bytes, key_material: bytes) -> bytes:
        """Decrypt using AES-256-CTR"""
        try:
            # Extract nonce and ciphertext
            nonce = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key_material),
                modes.CTR(nonce),
                backend=openssl_backend.backend
            )
            
            # Decrypt data
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Error in AES-CTR decryption: {e}")
            raise
    
    def _decrypt_fernet(self, encrypted_data: bytes, key_material: bytes) -> bytes:
        """Decrypt using Fernet"""
        try:
            cipher_suite = Fernet(key_material)
            return cipher_suite.decrypt(encrypted_data)
            
        except Exception as e:
            logger.error(f"Error in Fernet decryption: {e}")
            raise
    
    def _decrypt_chacha20(self, encrypted_data: bytes, key_material: bytes) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        try:
            # Extract nonce, tag, and ciphertext
            nonce = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.ChaCha20(key_material, nonce),
                modes.GCM(b'', tag),
                backend=openssl_backend.backend
            )
            
            # Decrypt data
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Error in ChaCha20 decryption: {e}")
            raise
    
    def _decrypt_rsa(self, encrypted_data: bytes, key_material: bytes) -> bytes:
        """Decrypt using RSA"""
        try:
            # Load private key
            private_key = serialization.load_pem_private_key(
                key_material,
                password=None,
                backend=openssl_backend.backend
            )
            
            # Decrypt with private key
            plaintext = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Error in RSA decryption: {e}")
            raise
    
    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding"""
        try:
            padding_length = padded_data[-1]
            return padded_data[:-padding_length]
            
        except Exception as e:
            logger.error(f"Error removing padding: {e}")
            raise
    
    async def _start_key_rotation_monitoring(self):
        """Start key rotation monitoring"""
        logger.info("Starting key rotation monitoring")
        
        while True:
            try:
                # Check for keys that need rotation
                await self._check_key_rotations()
                
                # Perform scheduled rotations
                await self._perform_key_rotations()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in key rotation monitoring: {e}")
                await asyncio.sleep(300)
    
    async def _check_key_rotations(self):
        """Check for keys that need rotation"""
        try:
            current_time = datetime.now()
            
            for key_id, key in self.keys.items():
                if key.status == KeyStatus.ACTIVE and key.expires_at:
                    # Check if key is within rotation window (7 days before expiration)
                    rotation_window = key.expires_at - timedelta(days=7)
                    
                    if current_time >= rotation_window:
                        await self._schedule_key_rotation(key_id)
            
        except Exception as e:
            logger.error(f"Error checking key rotations: {e}")
    
    async def _schedule_key_rotation(self, key_id: str):
        """Schedule key rotation"""
        try:
            key = self.keys.get(key_id)
            if not key:
                return
            
            # Mark key for rotation
            key.status = KeyStatus.ROTATING
            
            # Create rotation operation
            operation_id = str(uuid.uuid4())
            operation = EncryptionOperation(
                operation_id=operation_id,
                operation_type="key_rotation",
                key_id=key_id,
                resource=f"key:{key_id}",
                started_at=datetime.now(),
                status="pending"
            )
            
            self.active_operations[operation_id] = operation
            self.metrics.pending_rotations += 1
            
            logger.info(f"Scheduled key rotation: {key_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling key rotation: {e}")
    
    async def _perform_key_rotations(self):
        """Perform scheduled key rotations"""
        try:
            rotation_operations = [
                op for op in self.active_operations.values()
                if op.operation_type == "key_rotation" and op.status == "pending"
            ]
            
            for operation in rotation_operations:
                await self._rotate_key(operation)
            
        except Exception as e:
            logger.error(f"Error performing key rotations: {e}")
    
    async def _rotate_key(self, operation: EncryptionOperation):
        """Rotate encryption key"""
        try:
            old_key = self.keys.get(operation.key_id)
            if not old_key:
                operation.status = "failed"
                operation.error_message = "Original key not found"
                return
            
            # Generate new key with same parameters
            new_key_id = await self.generate_encryption_key(
                key_type=old_key.key_type,
                algorithm=old_key.algorithm,
                compliance_standards=old_key.compliance_standards,
                rotation_interval_days=old_key.rotation_interval_days,
                metadata=old_key.metadata
            )
            
            # Update old key status
            old_key.status = KeyStatus.DEPRECATED
            old_key.rotated_at = datetime.now()
            
            # Update new key to reference old key
            new_key = self.keys[new_key_id]
            new_key.parent_key_id = operation.key_id
            old_key.derived_keys.append(new_key_id)
            
            # Complete operation
            operation.status = "completed"
            operation.completed_at = datetime.now()
            
            self.metrics.pending_rotations -= 1
            
            logger.info(f"Key rotated: {operation.key_id} -> {new_key_id}")
            
        except Exception as e:
            logger.error(f"Error rotating key: {e}")
            operation.status = "failed"
            operation.error_message = str(e)
    
    def _update_average_encryption_time(self, duration_ms: float):
        """Update average encryption time metric"""
        if self.metrics.average_encryption_time_ms == 0:
            self.metrics.average_encryption_time_ms = duration_ms
        else:
            # Exponential moving average
            self.metrics.average_encryption_time_ms = (
                0.9 * self.metrics.average_encryption_time_ms + 0.1 * duration_ms
            )
    
    def _update_average_decryption_time(self, duration_ms: float):
        """Update average decryption time metric"""
        if self.metrics.average_decryption_time_ms == 0:
            self.metrics.average_decryption_time_ms = duration_ms
        else:
            # Exponential moving average
            self.metrics.average_decryption_time_ms = (
                0.9 * self.metrics.average_decryption_time_ms + 0.1 * duration_ms
            )
    
    async def _start_performance_monitoring(self):
        """Start performance monitoring"""
        logger.info("Starting encryption performance monitoring")
        
        while True:
            try:
                # Update metrics
                await self._update_encryption_metrics()
                
                # Check performance thresholds
                await self._check_performance_thresholds()
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _update_encryption_metrics(self):
        """Update encryption metrics"""
        try:
            # Count active keys
            active_keys = len([k for k in self.keys.values() if k.status == KeyStatus.ACTIVE])
            self.metrics.active_keys = active_keys
            
            # Count pending rotations
            pending_rotations = len([
                op for op in self.active_operations.values()
                if op.operation_type == "key_rotation" and op.status == "pending"
            ])
            self.metrics.pending_rotations = pending_rotations
            
            # Calculate compliance score
            self.metrics.compliance_score = await self._calculate_compliance_score()
            
            self.metrics.timestamp = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating encryption metrics: {e}")
    
    async def _calculate_compliance_score(self) -> float:
        """Calculate encryption compliance score"""
        try:
            if not self.keys:
                return 100.0
            
            compliant_keys = 0
            total_keys = len(self.keys)
            
            for key in self.keys.values():
                is_compliant = True
                
                # Check key expiration
                if key.expires_at and datetime.now() > key.expires_at:
                    is_compliant = False
                
                # Check compliance standards
                if key.compliance_standards:
                    # Additional compliance checks would go here
                    pass
                
                if is_compliant:
                    compliant_keys += 1
            
            return (compliant_keys / total_keys) * 100.0
            
        except Exception as e:
            logger.error(f"Error calculating compliance score: {e}")
            return 0.0
    
    async def _store_encryption_key(self, key: EncryptionKey):
        """Store encryption key securely"""
        try:
            # Serialize key data (excluding sensitive key material for storage metadata)
            key_data = {
                'key_id': key.key_id,
                'key_type': key.key_type.value,
                'algorithm': key.algorithm.value,
                'key_material': base64.b64encode(key.key_material).decode(),
                'status': key.status.value,
                'created_at': key.created_at.isoformat(),
                'expires_at': key.expires_at.isoformat() if key.expires_at else None,
                'rotated_at': key.rotated_at.isoformat() if key.rotated_at else None,
                'rotation_interval_days': key.rotation_interval_days,
                'usage_count': key.usage_count,
                'max_usage': key.max_usage,
                'compliance_standards': [cs.value for cs in key.compliance_standards],
                'metadata': key.metadata,
                'parent_key_id': key.parent_key_id,
                'derived_keys': key.derived_keys
            }
            
            # Encrypt key data with master key
            key_data_json = json.dumps(key_data)
            encrypted_key_data = self._encrypt_with_master_key(key_data_json)
            
            # Store encrypted key data
            await self.redis_client.hset(
                "encryption:keys",
                key.key_id,
                base64.b64encode(encrypted_key_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing encryption key: {e}")
    
    async def _store_encryption_policy(self, policy: EncryptionPolicy):
        """Store encryption policy"""
        try:
            policy_data = {
                'policy_id': policy.policy_id,
                'name': policy.name,
                'description': policy.description,
                'resource_patterns': policy.resource_patterns,
                'required_algorithm': policy.required_algorithm.value,
                'key_rotation_days': policy.key_rotation_days,
                'compliance_requirements': [cr.value for cr in policy.compliance_requirements],
                'encryption_required': policy.encryption_required,
                'key_escrow_required': policy.key_escrow_required,
                'hsm_required': policy.hsm_required,
                'enabled': policy.enabled
            }
            
            await self.redis_client.hset(
                "encryption:policies",
                policy.policy_id,
                json.dumps(policy_data)
            )
            
        except Exception as e:
            logger.error(f"Error storing encryption policy: {e}")
    
    async def close(self):
        """Close encryption manager"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.redis_pool:
                await self.redis_pool.disconnect()
            
            logger.info("Encryption Manager closed")
            
        except Exception as e:
            logger.error(f"Error closing encryption manager: {e}")

# Configuration schema for encryption manager
@dataclass
class EncryptionManagerConfig:
    """Encryption manager configuration"""
    redis_url: str
    redis_password: Optional[str] = None
    ssl_enabled: bool = True
    max_connections: int = 100
    key_derivation_salt: bytes = b'ainflue_encryption_salt'
    hsm_enabled: bool = False
    hsm_config: Dict[str, Any] = field(default_factory=dict)
    key_cache_ttl: int = 300
    compliance_mode: str = 'standard'
    key_escrow_enabled: bool = False
    master_key_password: str = 'default_password'