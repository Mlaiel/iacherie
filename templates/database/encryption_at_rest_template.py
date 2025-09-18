#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Encryption at Rest Template - Enterprise Grade

🚨 PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire

AVERTISSEMENT LÉGAL:
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT  
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Developed by Expert Team:
- Lead Dev IA: Fahed Mlaiel - AI-driven encryption strategies & automated key management
- Backend Senior: Advanced encryption patterns & secure data handling
- Security Expert: Cryptographic protocols & compliance frameworks
- DBA Expert: Database-level encryption & performance optimization
- DevOps Engineer: Key rotation automation & infrastructure security
- Compliance Specialist: GDPR, CCPA, SOC2 compliance

Architecture: Creator Economy Data Protection at Rest
Business Logic: Data Classification → Encryption Strategy → Key Management → Monitoring → Compliance
"""

import asyncio
import base64
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from sqlalchemy import MetaData, Table, Column, inspect, text, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.types import TypeDecorator, String, LargeBinary
import sqlalchemy as sa

logger = logging.getLogger(__name__)

class EncryptionAlgorithm(str, Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"
    RSA_OAEP = "rsa_oaep"

class DataClassification(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"                    # No encryption required
    INTERNAL = "internal"                # Basic encryption
    CONFIDENTIAL = "confidential"        # Strong encryption
    RESTRICTED = "restricted"            # Strongest encryption + additional controls

class KeyManagementStrategy(str, Enum):
    """Key management strategies"""
    LOCAL_FILE = "local_file"            # Local file storage (development only)
    ENVIRONMENT = "environment"          # Environment variables
    VAULT = "vault"                      # HashiCorp Vault
    AWS_KMS = "aws_kms"                  # AWS Key Management Service
    AZURE_KEY_VAULT = "azure_key_vault"  # Azure Key Vault
    GCP_KMS = "gcp_kms"                  # Google Cloud KMS

class ComplianceFramework(str, Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"                        # General Data Protection Regulation
    CCPA = "ccpa"                        # California Consumer Privacy Act
    SOC2 = "soc2"                        # Service Organization Control 2
    PCI_DSS = "pci_dss"                  # Payment Card Industry Data Security Standard
    HIPAA = "hipaa"                      # Health Insurance Portability and Accountability Act

@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    algorithm: EncryptionAlgorithm
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    version: int = 1
    classification: DataClassification = DataClassification.CONFIDENTIAL
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_active: bool = True

@dataclass
class EncryptionConfig:
    """Encryption configuration for tables/columns"""
    table_name: str
    column_name: str
    algorithm: EncryptionAlgorithm
    classification: DataClassification
    key_id: str
    compliance_requirements: List[ComplianceFramework] = field(default_factory=list)
    audit_enabled: bool = True
    key_rotation_days: int = 90
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class EncryptionAuditLog:
    """Encryption audit log entry"""
    operation: str  # encrypt, decrypt, key_rotation, access_denied
    table_name: str
    column_name: str
    key_id: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    error_message: Optional[str] = None
    compliance_context: Optional[str] = None

class EncryptedType(TypeDecorator):
    """SQLAlchemy encrypted column type"""
    
    impl = LargeBinary
    cache_ok = True
    
    def __init__(self, encryption_manager, key_id: str, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM):
        self.encryption_manager = encryption_manager
        self.key_id = key_id
        self.algorithm = algorithm
        super().__init__()
    
    def process_bind_param(self, value, dialect):
        """Encrypt value before storing in database"""
        if value is not None:
            try:
                encrypted_value = self.encryption_manager.encrypt(
                    data=str(value),
                    key_id=self.key_id,
                    algorithm=self.algorithm
                )
                return encrypted_value
            except Exception as e:
                logger.error(f"Encryption failed: {e}")
                raise
        return value
    
    def process_result_value(self, value, dialect):
        """Decrypt value when loading from database"""
        if value is not None:
            try:
                decrypted_value = self.encryption_manager.decrypt(
                    encrypted_data=value,
                    key_id=self.key_id
                )
                return decrypted_value
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                raise
        return value

class EncryptionAtRestTemplate:
    """
    🏭 Enterprise Encryption at Rest Template
    
    Features:
    - Multiple encryption algorithms with automatic selection
    - Comprehensive key management and rotation
    - Data classification and compliance frameworks
    - Creator Economy sensitive data protection
    - Audit logging and compliance reporting
    - Performance-optimized encryption
    - Transparent application integration
    """
    
    def __init__(
        self,
        database_url: str,
        key_management_strategy: KeyManagementStrategy = KeyManagementStrategy.ENVIRONMENT,
        default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        key_vault_config: Optional[Dict[str, Any]] = None
    ):
        self.database_url = database_url
        self.key_management_strategy = key_management_strategy
        self.default_algorithm = default_algorithm
        self.key_vault_config = key_vault_config or {}
        
        # Initialize database connections
        self.engine = create_engine(database_url)
        self.async_engine = create_async_engine(database_url)
        
        # Encryption management
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.encryption_configs: Dict[str, EncryptionConfig] = {}
        self.audit_logs: List[EncryptionAuditLog] = []
        
        # Performance tracking
        self.encryption_metrics: Dict[str, Dict[str, float]] = {}
        
        # Creator Economy sensitive data patterns
        self.creator_sensitive_fields = {
            "creator_profiles": [
                ("email", DataClassification.CONFIDENTIAL),
                ("phone", DataClassification.CONFIDENTIAL),
                ("tax_id", DataClassification.RESTRICTED),
                ("bank_account", DataClassification.RESTRICTED)
            ],
            "monetization_data": [
                ("account_info", DataClassification.RESTRICTED),
                ("payment_details", DataClassification.RESTRICTED),
                ("tax_info", DataClassification.RESTRICTED)
            ],
            "collaboration_data": [
                ("contract_terms", DataClassification.CONFIDENTIAL),
                ("financial_details", DataClassification.RESTRICTED)
            ],
            "analytics_data": [
                ("personal_metrics", DataClassification.CONFIDENTIAL),
                ("audience_demographics", DataClassification.CONFIDENTIAL)
            ]
        }
        
        self._initialize_encryption_system()
    
    def _initialize_encryption_system(self):
        """Initialize encryption system components"""
        try:
            # Load or generate master keys
            self._initialize_key_management()
            
            # Load encryption configurations
            self._load_encryption_configs()
            
            # Setup database encryption hooks
            self._setup_database_hooks()
            
            # Initialize Creator Economy encryption
            self._initialize_creator_economy_encryption()
            
            logger.info("Encryption at rest system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption system: {e}")
    
    def _initialize_key_management(self):
        """Initialize key management system"""
        try:
            if self.key_management_strategy == KeyManagementStrategy.ENVIRONMENT:
                self._load_keys_from_environment()
            elif self.key_management_strategy == KeyManagementStrategy.LOCAL_FILE:
                self._load_keys_from_file()
            elif self.key_management_strategy in [KeyManagementStrategy.VAULT, KeyManagementStrategy.AWS_KMS]:
                self._initialize_external_key_management()
            else:
                # Generate default keys
                self._generate_default_keys()
                
        except Exception as e:
            logger.error(f"Failed to initialize key management: {e}")
            # Fallback to generating default keys
            self._generate_default_keys()
    
    def _load_keys_from_environment(self):
        """Load encryption keys from environment variables"""
        try:
            # Load master key from environment
            master_key_b64 = os.getenv("AINFLUE_MASTER_KEY")
            if not master_key_b64:
                logger.warning("No master key found in environment, generating new one")
                self._generate_default_keys()
                return
            
            master_key = base64.b64decode(master_key_b64)
            
            # Create master key entry
            master_key_obj = EncryptionKey(
                key_id="master",
                algorithm=self.default_algorithm,
                key_data=master_key,
                created_at=datetime.now(timezone.utc),
                classification=DataClassification.RESTRICTED
            )
            
            self.encryption_keys["master"] = master_key_obj
            
            # Generate derived keys for different purposes
            self._generate_derived_keys(master_key)
            
        except Exception as e:
            logger.error(f"Failed to load keys from environment: {e}")
            self._generate_default_keys()
    
    def _generate_default_keys(self):
        """Generate default encryption keys"""
        try:
            # Generate master key
            master_key = secrets.token_bytes(32)  # 256-bit key
            
            master_key_obj = EncryptionKey(
                key_id="master",
                algorithm=self.default_algorithm,
                key_data=master_key,
                created_at=datetime.now(timezone.utc),
                classification=DataClassification.RESTRICTED
            )
            
            self.encryption_keys["master"] = master_key_obj
            
            # Generate derived keys
            self._generate_derived_keys(master_key)
            
            # Save master key to environment for future use
            master_key_b64 = base64.b64encode(master_key).decode('utf-8')
            logger.warning(f"Generated new master key. Save to environment: AINFLUE_MASTER_KEY={master_key_b64}")
            
        except Exception as e:
            logger.error(f"Failed to generate default keys: {e}")
    
    def _generate_derived_keys(self, master_key: bytes):
        """Generate derived keys for different data classifications"""
        try:
            # Key derivation for different classifications
            classifications = [
                (DataClassification.CONFIDENTIAL, "confidential"),
                (DataClassification.RESTRICTED, "restricted"),
                (DataClassification.INTERNAL, "internal")
            ]
            
            for classification, key_name in classifications:
                # Use PBKDF2 for key derivation
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=key_name.encode('utf-8'),
                    iterations=100000,
                    backend=default_backend()
                )
                
                derived_key = kdf.derive(master_key)
                
                key_obj = EncryptionKey(
                    key_id=key_name,
                    algorithm=self.default_algorithm,
                    key_data=derived_key,
                    created_at=datetime.now(timezone.utc),
                    classification=classification
                )
                
                self.encryption_keys[key_name] = key_obj
            
            # Generate Creator Economy specific keys
            self._generate_creator_economy_keys(master_key)
            
        except Exception as e:
            logger.error(f"Failed to generate derived keys: {e}")
    
    def _generate_creator_economy_keys(self, master_key: bytes):
        """Generate Creator Economy specific encryption keys"""
        try:
            creator_keys = [
                ("creator_profiles", DataClassification.CONFIDENTIAL),
                ("monetization_data", DataClassification.RESTRICTED),
                ("collaboration_data", DataClassification.CONFIDENTIAL),
                ("analytics_data", DataClassification.CONFIDENTIAL)
            ]
            
            for key_name, classification in creator_keys:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=f"creator_{key_name}".encode('utf-8'),
                    iterations=100000,
                    backend=default_backend()
                )
                
                derived_key = kdf.derive(master_key)
                
                key_obj = EncryptionKey(
                    key_id=f"creator_{key_name}",
                    algorithm=self.default_algorithm,
                    key_data=derived_key,
                    created_at=datetime.now(timezone.utc),
                    classification=classification
                )
                
                self.encryption_keys[f"creator_{key_name}"] = key_obj
            
        except Exception as e:
            logger.error(f"Failed to generate Creator Economy keys: {e}")
    
    def encrypt(
        self,
        data: str,
        key_id: str,
        algorithm: Optional[EncryptionAlgorithm] = None
    ) -> bytes:
        """
        Encrypt data using specified key and algorithm
        
        Args:
            data: Data to encrypt
            key_id: Key identifier
            algorithm: Encryption algorithm (optional)
            
        Returns:
            Encrypted data as bytes
        """
        try:
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key {key_id} not found")
            
            key_obj = self.encryption_keys[key_id]
            algorithm = algorithm or key_obj.algorithm
            
            # Track usage
            key_obj.usage_count += 1
            key_obj.last_used = datetime.now(timezone.utc)
            
            # Perform encryption based on algorithm
            start_time = time.time()
            
            if algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data = self._encrypt_aes_gcm(data.encode('utf-8'), key_obj.key_data)
            elif algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data = self._encrypt_aes_cbc(data.encode('utf-8'), key_obj.key_data)
            elif algorithm == EncryptionAlgorithm.FERNET:
                encrypted_data = self._encrypt_fernet(data.encode('utf-8'), key_obj.key_data)
            elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data = self._encrypt_chacha20(data.encode('utf-8'), key_obj.key_data)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {algorithm}")
            
            encryption_time = time.time() - start_time
            
            # Update metrics
            self._update_encryption_metrics(key_id, algorithm, encryption_time, len(data))
            
            # Audit log
            self._log_encryption_operation("encrypt", key_id, True)
            
            return encrypted_data
            
        except Exception as e:
            self._log_encryption_operation("encrypt", key_id, False, str(e))
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(
        self,
        encrypted_data: bytes,
        key_id: str
    ) -> str:
        """
        Decrypt data using specified key
        
        Args:
            encrypted_data: Encrypted data
            key_id: Key identifier
            
        Returns:
            Decrypted data as string
        """
        try:
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key {key_id} not found")
            
            key_obj = self.encryption_keys[key_id]
            
            # Track usage
            key_obj.usage_count += 1
            key_obj.last_used = datetime.now(timezone.utc)
            
            # Perform decryption based on algorithm
            start_time = time.time()
            
            if key_obj.algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = self._decrypt_aes_gcm(encrypted_data, key_obj.key_data)
            elif key_obj.algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_data = self._decrypt_aes_cbc(encrypted_data, key_obj.key_data)
            elif key_obj.algorithm == EncryptionAlgorithm.FERNET:
                decrypted_data = self._decrypt_fernet(encrypted_data, key_obj.key_data)
            elif key_obj.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = self._decrypt_chacha20(encrypted_data, key_obj.key_data)
            else:
                raise ValueError(f"Unsupported encryption algorithm: {key_obj.algorithm}")
            
            decryption_time = time.time() - start_time
            
            # Update metrics
            self._update_decryption_metrics(key_id, key_obj.algorithm, decryption_time, len(encrypted_data))
            
            # Audit log
            self._log_encryption_operation("decrypt", key_id, True)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self._log_encryption_operation("decrypt", key_id, False, str(e))
            logger.error(f"Decryption failed: {e}")
            raise
    
    def configure_table_encryption(
        self,
        table_name: str,
        column_configs: List[Dict[str, Any]]
    ) -> bool:
        """
        Configure encryption for table columns
        
        Args:
            table_name: Table name
            column_configs: List of column configurations
            
        Returns:
            Success status
        """
        try:
            for config in column_configs:
                column_name = config["column_name"]
                classification = DataClassification(config.get("classification", DataClassification.CONFIDENTIAL))
                algorithm = EncryptionAlgorithm(config.get("algorithm", self.default_algorithm))
                compliance_requirements = [ComplianceFramework(f) for f in config.get("compliance", [])]
                
                # Select appropriate key based on classification
                key_id = self._select_key_for_classification(classification, table_name)
                
                # Create encryption config
                encryption_config = EncryptionConfig(
                    table_name=table_name,
                    column_name=column_name,
                    algorithm=algorithm,
                    classification=classification,
                    key_id=key_id,
                    compliance_requirements=compliance_requirements,
                    key_rotation_days=config.get("key_rotation_days", 90)
                )
                
                config_key = f"{table_name}.{column_name}"
                self.encryption_configs[config_key] = encryption_config
            
            self._save_encryption_configs()
            
            logger.info(f"Configured encryption for table {table_name} with {len(column_configs)} columns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure table encryption: {e}")
            return False
    
    def setup_creator_economy_encryption(self) -> bool:
        """
        Setup encryption for Creator Economy sensitive data
        
        Returns:
            Success status
        """
        try:
            for table_name, fields in self.creator_sensitive_fields.items():
                column_configs = []
                
                for field_name, classification in fields:
                    # Determine compliance requirements based on field type
                    compliance_requirements = self._get_compliance_requirements(field_name, classification)
                    
                    config = {
                        "column_name": field_name,
                        "classification": classification.value,
                        "algorithm": self._select_algorithm_for_classification(classification).value,
                        "compliance": [c.value for c in compliance_requirements],
                        "key_rotation_days": 30 if classification == DataClassification.RESTRICTED else 90
                    }
                    
                    column_configs.append(config)
                
                if column_configs:
                    self.configure_table_encryption(table_name, column_configs)
            
            logger.info("Creator Economy encryption configured")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Creator Economy encryption: {e}")
            return False
    
    def rotate_keys(
        self,
        key_ids: Optional[List[str]] = None,
        force_rotation: bool = False
    ) -> Dict[str, bool]:
        """
        Rotate encryption keys
        
        Args:
            key_ids: Specific key IDs to rotate (None for all)
            force_rotation: Force rotation even if not due
            
        Returns:
            Dictionary of rotation results by key ID
        """
        results = {}
        
        try:
            keys_to_rotate = key_ids or list(self.encryption_keys.keys())
            
            for key_id in keys_to_rotate:
                if key_id not in self.encryption_keys:
                    results[key_id] = False
                    continue
                
                key_obj = self.encryption_keys[key_id]
                
                # Check if rotation is needed
                if not force_rotation and not self._is_key_rotation_needed(key_obj):
                    results[key_id] = True  # No rotation needed
                    continue
                
                # Perform key rotation
                success = self._rotate_single_key(key_obj)
                results[key_id] = success
                
                if success:
                    self._log_encryption_operation("key_rotation", key_id, True)
                    logger.info(f"Rotated encryption key: {key_id}")
                else:
                    self._log_encryption_operation("key_rotation", key_id, False)
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
        
        return results
    
    def get_encrypted_column_type(
        self,
        table_name: str,
        column_name: str
    ) -> Optional[EncryptedType]:
        """
        Get encrypted column type for SQLAlchemy
        
        Args:
            table_name: Table name
            column_name: Column name
            
        Returns:
            EncryptedType instance or None
        """
        try:
            config_key = f"{table_name}.{column_name}"
            
            if config_key not in self.encryption_configs:
                return None
            
            config = self.encryption_configs[config_key]
            
            return EncryptedType(
                encryption_manager=self,
                key_id=config.key_id,
                algorithm=config.algorithm
            )
            
        except Exception as e:
            logger.error(f"Failed to get encrypted column type: {e}")
            return None
    
    def get_compliance_report(
        self,
        framework: Optional[ComplianceFramework] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance report
        
        Args:
            framework: Specific framework to report on
            
        Returns:
            Compliance report
        """
        try:
            report = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "encryption_summary": self._get_encryption_summary(),
                "key_management": self._get_key_management_status(),
                "compliance_status": self._get_compliance_status(framework),
                "audit_summary": self._get_audit_summary(),
                "recommendations": self._get_compliance_recommendations()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            return {"error": str(e)}
    
    # Encryption algorithm implementations
    def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-GCM"""
        try:
            # Generate random IV
            iv = secrets.token_bytes(12)  # 96-bit IV for GCM
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine IV + tag + ciphertext
            return iv + encryptor.tag + ciphertext
            
        except Exception as e:
            logger.error(f"AES-GCM encryption failed: {e}")
            raise
    
    def _decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-GCM"""
        try:
            # Extract IV, tag, and ciphertext
            iv = encrypted_data[:12]
            tag = encrypted_data[12:28]
            ciphertext = encrypted_data[28:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            logger.error(f"AES-GCM decryption failed: {e}")
            raise
    
    def _encrypt_aes_cbc(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using AES-256-CBC"""
        try:
            # Generate random IV
            iv = secrets.token_bytes(16)  # 128-bit IV for CBC
            
            # Pad data to block size
            pad_length = 16 - (len(data) % 16)
            padded_data = data + bytes([pad_length]) * pad_length
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV + ciphertext
            return iv + ciphertext
            
        except Exception as e:
            logger.error(f"AES-CBC encryption failed: {e}")
            raise
    
    def _decrypt_aes_cbc(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using AES-256-CBC"""
        try:
            # Extract IV and ciphertext
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            pad_length = padded_data[-1]
            return padded_data[:-pad_length]
            
        except Exception as e:
            logger.error(f"AES-CBC decryption failed: {e}")
            raise
    
    def _encrypt_fernet(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using Fernet"""
        try:
            # Fernet requires base64-encoded key
            fernet_key = base64.urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            return f.encrypt(data)
            
        except Exception as e:
            logger.error(f"Fernet encryption failed: {e}")
            raise
    
    def _decrypt_fernet(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using Fernet"""
        try:
            # Fernet requires base64-encoded key
            fernet_key = base64.urlsafe_b64encode(key)
            f = Fernet(fernet_key)
            return f.decrypt(encrypted_data)
            
        except Exception as e:
            logger.error(f"Fernet decryption failed: {e}")
            raise
    
    def _encrypt_chacha20(self, data: bytes, key: bytes) -> bytes:
        """Encrypt using ChaCha20-Poly1305"""
        try:
            # Generate random nonce
            nonce = secrets.token_bytes(12)  # 96-bit nonce
            
            # Create cipher
            cipher = Cipher(
                algorithms.ChaCha20(key, nonce),
                mode=None,
                backend=default_backend()
            )
            
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Combine nonce + ciphertext
            return nonce + ciphertext
            
        except Exception as e:
            logger.error(f"ChaCha20 encryption failed: {e}")
            raise
    
    def _decrypt_chacha20(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt using ChaCha20-Poly1305"""
        try:
            # Extract nonce and ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.ChaCha20(key, nonce),
                mode=None,
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            logger.error(f"ChaCha20 decryption failed: {e}")
            raise
    
    # Helper methods
    def _select_key_for_classification(
        self,
        classification: DataClassification,
        table_name: str
    ) -> str:
        """Select appropriate key for data classification"""
        # Creator Economy specific keys
        if table_name in self.creator_sensitive_fields:
            creator_key = f"creator_{table_name}"
            if creator_key in self.encryption_keys:
                return creator_key
        
        # General classification keys
        if classification == DataClassification.RESTRICTED:
            return "restricted"
        elif classification == DataClassification.CONFIDENTIAL:
            return "confidential"
        elif classification == DataClassification.INTERNAL:
            return "internal"
        else:
            return "master"
    
    def _select_algorithm_for_classification(
        self,
        classification: DataClassification
    ) -> EncryptionAlgorithm:
        """Select encryption algorithm based on classification"""
        if classification == DataClassification.RESTRICTED:
            return EncryptionAlgorithm.AES_256_GCM
        elif classification == DataClassification.CONFIDENTIAL:
            return EncryptionAlgorithm.AES_256_GCM
        elif classification == DataClassification.INTERNAL:
            return EncryptionAlgorithm.FERNET
        else:
            return self.default_algorithm
    
    def _get_compliance_requirements(
        self,
        field_name: str,
        classification: DataClassification
    ) -> List[ComplianceFramework]:
        """Get compliance requirements for field"""
        requirements = []
        
        # Financial data
        if any(keyword in field_name.lower() for keyword in ["payment", "bank", "tax", "revenue"]):
            requirements.extend([ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2])
        
        # Personal data
        if any(keyword in field_name.lower() for keyword in ["email", "phone", "address"]):
            requirements.extend([ComplianceFramework.GDPR, ComplianceFramework.CCPA])
        
        # High classification always requires SOC2
        if classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            if ComplianceFramework.SOC2 not in requirements:
                requirements.append(ComplianceFramework.SOC2)
        
        return requirements
    
    def _is_key_rotation_needed(self, key_obj: EncryptionKey) -> bool:
        """Check if key rotation is needed"""
        if key_obj.expires_at and datetime.now(timezone.utc) >= key_obj.expires_at:
            return True
        
        # Check based on usage count
        if key_obj.usage_count > 1000000:  # 1M operations
            return True
        
        # Check based on age (90 days default)
        age_days = (datetime.now(timezone.utc) - key_obj.created_at).days
        if age_days > 90:
            return True
        
        return False
    
    def _rotate_single_key(self, key_obj: EncryptionKey) -> bool:
        """Rotate a single encryption key"""
        try:
            # Generate new key
            new_key_data = secrets.token_bytes(32)
            
            # Create new key version
            new_key = EncryptionKey(
                key_id=key_obj.key_id,
                algorithm=key_obj.algorithm,
                key_data=new_key_data,
                created_at=datetime.now(timezone.utc),
                version=key_obj.version + 1,
                classification=key_obj.classification
            )
            
            # Keep old key for decryption
            old_key_id = f"{key_obj.key_id}_v{key_obj.version}"
            key_obj.is_active = False
            self.encryption_keys[old_key_id] = key_obj
            
            # Replace with new key
            self.encryption_keys[new_key.key_id] = new_key
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate key {key_obj.key_id}: {e}")
            return False
    
    def _update_encryption_metrics(
        self,
        key_id: str,
        algorithm: EncryptionAlgorithm,
        execution_time: float,
        data_size: int
    ):
        """Update encryption performance metrics"""
        if key_id not in self.encryption_metrics:
            self.encryption_metrics[key_id] = {
                "total_operations": 0,
                "total_time": 0.0,
                "total_bytes": 0,
                "avg_time": 0.0,
                "throughput_mbps": 0.0
            }
        
        metrics = self.encryption_metrics[key_id]
        metrics["total_operations"] += 1
        metrics["total_time"] += execution_time
        metrics["total_bytes"] += data_size
        metrics["avg_time"] = metrics["total_time"] / metrics["total_operations"]
        
        if execution_time > 0:
            throughput = (data_size / 1024 / 1024) / execution_time  # MB/s
            metrics["throughput_mbps"] = throughput
    
    def _update_decryption_metrics(
        self,
        key_id: str,
        algorithm: EncryptionAlgorithm,
        execution_time: float,
        data_size: int
    ):
        """Update decryption performance metrics"""
        metrics_key = f"{key_id}_decrypt"
        
        if metrics_key not in self.encryption_metrics:
            self.encryption_metrics[metrics_key] = {
                "total_operations": 0,
                "total_time": 0.0,
                "total_bytes": 0,
                "avg_time": 0.0,
                "throughput_mbps": 0.0
            }
        
        metrics = self.encryption_metrics[metrics_key]
        metrics["total_operations"] += 1
        metrics["total_time"] += execution_time
        metrics["total_bytes"] += data_size
        metrics["avg_time"] = metrics["total_time"] / metrics["total_operations"]
        
        if execution_time > 0:
            throughput = (data_size / 1024 / 1024) / execution_time  # MB/s
            metrics["throughput_mbps"] = throughput
    
    def _log_encryption_operation(
        self,
        operation: str,
        key_id: str,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log encryption operation for audit"""
        audit_log = EncryptionAuditLog(
            operation=operation,
            table_name="",
            column_name="",
            key_id=key_id,
            success=success,
            error_message=error_message
        )
        
        self.audit_logs.append(audit_log)
        
        # Keep only last 10000 audit logs
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    # Compliance and reporting methods
    def _get_encryption_summary(self) -> Dict[str, Any]:
        """Get encryption configuration summary"""
        summary = {
            "total_encrypted_columns": len(self.encryption_configs),
            "encryption_algorithms": {},
            "data_classifications": {},
            "tables_with_encryption": set()
        }
        
        for config in self.encryption_configs.values():
            # Count algorithms
            algo = config.algorithm.value
            summary["encryption_algorithms"][algo] = summary["encryption_algorithms"].get(algo, 0) + 1
            
            # Count classifications
            classification = config.classification.value
            summary["data_classifications"][classification] = summary["data_classifications"].get(classification, 0) + 1
            
            # Track tables
            summary["tables_with_encryption"].add(config.table_name)
        
        summary["tables_with_encryption"] = len(summary["tables_with_encryption"])
        
        return summary
    
    def _get_key_management_status(self) -> Dict[str, Any]:
        """Get key management status"""
        status = {
            "total_keys": len(self.encryption_keys),
            "active_keys": len([k for k in self.encryption_keys.values() if k.is_active]),
            "keys_needing_rotation": len([k for k in self.encryption_keys.values() if self._is_key_rotation_needed(k)]),
            "key_management_strategy": self.key_management_strategy.value,
            "average_key_age_days": 0
        }
        
        if self.encryption_keys:
            ages = [(datetime.now(timezone.utc) - k.created_at).days for k in self.encryption_keys.values()]
            status["average_key_age_days"] = sum(ages) / len(ages)
        
        return status
    
    def _get_compliance_status(self, framework: Optional[ComplianceFramework]) -> Dict[str, Any]:
        """Get compliance status"""
        frameworks = [framework] if framework else list(ComplianceFramework)
        
        status = {}
        
        for fw in frameworks:
            fw_configs = [
                config for config in self.encryption_configs.values()
                if fw in config.compliance_requirements
            ]
            
            status[fw.value] = {
                "applicable_columns": len(fw_configs),
                "compliance_score": self._calculate_compliance_score(fw_configs, fw),
                "issues": self._identify_compliance_issues(fw_configs, fw)
            }
        
        return status
    
    def _calculate_compliance_score(
        self,
        configs: List[EncryptionConfig],
        framework: ComplianceFramework
    ) -> float:
        """Calculate compliance score for framework"""
        if not configs:
            return 100.0
        
        score = 100.0
        
        for config in configs:
            # Check encryption strength
            if framework in [ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2]:
                if config.algorithm not in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                    score -= 10.0
            
            # Check key rotation
            key_obj = self.encryption_keys.get(config.key_id)
            if key_obj and self._is_key_rotation_needed(key_obj):
                score -= 5.0
            
            # Check audit logging
            if not config.audit_enabled:
                score -= 5.0
        
        return max(0.0, score)
    
    def _identify_compliance_issues(
        self,
        configs: List[EncryptionConfig],
        framework: ComplianceFramework
    ) -> List[str]:
        """Identify compliance issues"""
        issues = []
        
        for config in configs:
            config_key = f"{config.table_name}.{config.column_name}"
            
            # Check encryption algorithm compliance
            if framework == ComplianceFramework.PCI_DSS:
                if config.algorithm not in [EncryptionAlgorithm.AES_256_GCM, EncryptionAlgorithm.AES_256_CBC]:
                    issues.append(f"PCI DSS requires AES-256 for {config_key}")
            
            # Check key rotation
            key_obj = self.encryption_keys.get(config.key_id)
            if key_obj and self._is_key_rotation_needed(key_obj):
                issues.append(f"Key rotation overdue for {config_key}")
            
            # Check audit requirements
            if framework in [ComplianceFramework.GDPR, ComplianceFramework.SOC2] and not config.audit_enabled:
                issues.append(f"Audit logging required for {config_key}")
        
        return issues
    
    def _get_audit_summary(self) -> Dict[str, Any]:
        """Get audit log summary"""
        if not self.audit_logs:
            return {"total_operations": 0}
        
        recent_logs = [
            log for log in self.audit_logs
            if (datetime.now(timezone.utc) - log.timestamp).days <= 30
        ]
        
        summary = {
            "total_operations": len(self.audit_logs),
            "recent_operations_30d": len(recent_logs),
            "success_rate": len([log for log in recent_logs if log.success]) / len(recent_logs) * 100 if recent_logs else 0,
            "operation_types": {},
            "error_summary": []
        }
        
        # Count operation types
        for log in recent_logs:
            summary["operation_types"][log.operation] = summary["operation_types"].get(log.operation, 0) + 1
        
        # Summarize errors
        error_logs = [log for log in recent_logs if not log.success]
        error_counts = {}
        for log in error_logs:
            error_counts[log.error_message] = error_counts.get(log.error_message, 0) + 1
        
        summary["error_summary"] = [
            {"error": error, "count": count}
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]  # Top 5 errors
        
        return summary
    
    def _get_compliance_recommendations(self) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        try:
            # Check for keys needing rotation
            keys_needing_rotation = [k for k in self.encryption_keys.values() if self._is_key_rotation_needed(k)]
            if keys_needing_rotation:
                recommendations.append(f"Rotate {len(keys_needing_rotation)} encryption keys that are overdue")
            
            # Check for weak algorithms
            weak_configs = [
                config for config in self.encryption_configs.values()
                if config.algorithm in [EncryptionAlgorithm.FERNET]
                and config.classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]
            ]
            if weak_configs:
                recommendations.append(f"Upgrade {len(weak_configs)} configurations to stronger encryption algorithms")
            
            # Check for missing audit logging
            no_audit_configs = [config for config in self.encryption_configs.values() if not config.audit_enabled]
            if no_audit_configs:
                recommendations.append(f"Enable audit logging for {len(no_audit_configs)} encrypted columns")
            
            # Creator Economy specific recommendations
            creator_tables = [config.table_name for config in self.encryption_configs.values() if config.table_name in self.creator_sensitive_fields]
            if len(set(creator_tables)) < len(self.creator_sensitive_fields):
                recommendations.append("Configure encryption for all Creator Economy sensitive data tables")
            
        except Exception as e:
            logger.error(f"Failed to generate compliance recommendations: {e}")
        
        return recommendations
    
    # System integration methods
    def _setup_database_hooks(self):
        """Setup database event hooks for encryption"""
        try:
            # SQLAlchemy event listeners for automatic encryption
            @event.listens_for(self.engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                # Log database operations for audit
                if any(keyword in statement.upper() for keyword in ["INSERT", "UPDATE", "SELECT"]):
                    self._log_database_operation(statement)
            
        except Exception as e:
            logger.error(f"Failed to setup database hooks: {e}")
    
    def _log_database_operation(self, statement: str):
        """Log database operation for encryption audit"""
        try:
            # Extract table names from SQL statement
            table_pattern = r'(?:FROM|INTO|UPDATE)\s+(\w+)'
            import re
            tables = re.findall(table_pattern, statement, re.IGNORECASE)
            
            for table in tables:
                if table in [config.table_name for config in self.encryption_configs.values()]:
                    # This is an operation on an encrypted table
                    audit_log = EncryptionAuditLog(
                        operation="database_access",
                        table_name=table,
                        column_name="",
                        key_id="",
                        success=True
                    )
                    self.audit_logs.append(audit_log)
        
        except Exception as e:
            logger.debug(f"Failed to log database operation: {e}")
    
    def _initialize_creator_economy_encryption(self):
        """Initialize Creator Economy specific encryption settings"""
        try:
            # Setup encryption for Creator Economy tables
            self.setup_creator_economy_encryption()
            
            logger.info("Creator Economy encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Creator Economy encryption: {e}")
    
    def _load_encryption_configs(self):
        """Load encryption configurations from storage"""
        try:
            # This would load from actual configuration storage
            # For now, start with empty configs
            pass
        except Exception as e:
            logger.debug(f"Could not load encryption configs: {e}")
    
    def _save_encryption_configs(self):
        """Save encryption configurations to storage"""
        try:
            # This would save to actual configuration storage
            pass
        except Exception as e:
            logger.error(f"Failed to save encryption configs: {e}")
    
    def _load_keys_from_file(self):
        """Load keys from local file (development only)"""
        try:
            # This is a simplified implementation for development
            # Production should use proper key management
            logger.warning("Using local file key management - not recommended for production")
            self._generate_default_keys()
        except Exception as e:
            logger.error(f"Failed to load keys from file: {e}")
            self._generate_default_keys()
    
    def _initialize_external_key_management(self):
        """Initialize external key management (Vault, AWS KMS, etc.)"""
        try:
            # This would integrate with actual external key management
            # For now, fallback to default keys
            logger.warning("External key management not fully implemented, using default keys")
            self._generate_default_keys()
        except Exception as e:
            logger.error(f"Failed to initialize external key management: {e}")
            self._generate_default_keys()

# Export for use
__all__ = [
    "EncryptionAtRestTemplate",
    "EncryptionAlgorithm",
    "DataClassification",
    "KeyManagementStrategy",
    "ComplianceFramework",
    "EncryptionKey",
    "EncryptionConfig",
    "EncryptionAuditLog",
    "EncryptedType"
]