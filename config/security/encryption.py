"""Enhanced Security Configuration for Data Protection
Updated to support the four data protection requirements:
1. AES-256 encryption repos
2. TLS 1.3 encryption transit
3. End-to-end encryption communications
4. Key management HSM

Business Logic Integration:
- Content file encryption before upload processing
- Creator data protection during multi-platform distribution
- Secure fingerprint storage and matching
- Protected revenue and analytics data encryption

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class EncryptionAlgorithm(Enum):
    """
Supported encryption algorithms - Enhanced for data protection requirements."""
    # Required for Repository Encryption (Requirement 1)
    AES_256_GCM = "aes-256-gcm"  # Primary algorithm for repos
    AES_256_CBC = "aes-256-cbc"  # Alternative for repos
    
    # For End-to-End Communications (Requirement 3)
    ChaCha20_Poly1305 = "chacha20-poly1305"
    RSA_4096 = "rsa-4096"  # Required for E2E key exchange
    
    # Digital signatures and key exchange
    ECDSA_P256 = "ecdsa-p256"
    ECDH_P256 = "ecdh-p256"


class TransitSecurityLevel(Enum):
    """Transit security levels for TLS requirements"""

    TLS_1_2 = "tls-1.2"
    TLS_1_3 = "tls-1.3"  # Required for Requirement 2
    TLS_1_3_STRICT = "tls-1.3-strict"


class HSMComplianceLevel(Enum):
    """HSM compliance levels for key management"""

    FIPS_140_2_LEVEL_2 = "fips-140-2-level-2"
    FIPS_140_2_LEVEL_3 = "fips-140-2-level-3"
    FIPS_140_2_LEVEL_4 = "fips-140-2-level-4"  # Required for Requirement 4


class KeyType(Enum):
    """Encryption key types with data protection categories."""

    MASTER_KEY = "master"
    DATA_KEY = "data"
    CONTENT_KEY = "content"
    API_KEY = "api"
    SESSION_KEY = "session"
    FINGERPRINT_KEY = "fingerprint"
    REVENUE_KEY = "revenue"
    # New for data protection requirements
    REPOSITORY_KEY = "repository"  # For repo encryption
    TRANSIT_KEY = "transit"        # For TLS/transit
    E2E_KEY = "e2e"               # For end-to-end
    HSM_KEY = "hsm"               # For HSM management


@dataclass
class DataProtectionEncryptionConfig:
    """Enhanced encryption configuration for data protection requirements"""
    
    # Requirement 1: AES-256 encryption repos
    repository_encryption_enabled: bool = True
    repository_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    repository_key_size: int = 256
    
    # Requirement 2: TLS 1.3 encryption transit
    transit_encryption_enabled: bool = True
    min_tls_version: TransitSecurityLevel = TransitSecurityLevel.TLS_1_3
    perfect_forward_secrecy: bool = True
    
    # Requirement 3: End-to-end encryption communications  
    e2e_encryption_enabled: bool = True
    e2e_asymmetric_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.RSA_4096
    e2e_symmetric_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    
    # Requirement 4: Key management HSM
    hsm_enabled: bool = True
    hsm_compliance_level: HSMComplianceLevel = HSMComplianceLevel.FIPS_140_2_LEVEL_4
    hsm_tamper_resistance: bool = True
    
    # Additional security settings
    key_rotation_enabled: bool = True
    key_rotation_interval_days: int = 90
    audit_logging_enabled: bool = True


class KeyDerivationFunction(Enum):
    """
Key derivation functions."""

    PBKDF2_SHA256 = "pbkdf2-sha256"
    SCRYPT = "scrypt"
    ARGON2ID = "argon2id"
    HKDF_SHA256 = "hkdf-sha256"


@dataclass
class KeyConfiguration:
    """Individual key configuration settings."""
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    key_size: int
    rotation_days: int = 90
    backup_enabled: bool = True
    
    # Key usage restrictions
    max_encryptions: Optional[int] = None
    usage_contexts: List[str] = field(default_factory=list)
    
    # Key derivation settings
    kdf: Optional[KeyDerivationFunction] = None
    salt_size: int = 32
    iterations: int = 100000  # For PBKDF2
    memory_cost: int = 65536  # For Argon2id/Scrypt
    parallelism: int = 1      # For Argon2id


@dataclass
class ContentEncryptionConfig:
    """
Content-specific encryption configuration."""
    
    # File encryption settings
    file_encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    chunk_size: int = 64 * 1024  # 64KB chunks
    compression_before_encryption: bool = True
    
    # Content type specific settings
    content_type_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "audio": {
            "algorithm": EncryptionAlgorithm.AES_256_GCM,
            "key_rotation_days": 30,
            "metadata_encryption": True,
            "thumbnail_encryption": True
        },
        "video": {
            "algorithm": EncryptionAlgorithm.AES_256_GCM,
            "key_rotation_days": 30,
            "metadata_encryption": True,
            "preview_encryption": True,
            "subtitle_encryption": True
        },
        "image": {
            "algorithm": EncryptionAlgorithm.AES_256_GCM,
            "key_rotation_days": 60,
            "metadata_encryption": True,
            "watermark_encryption": False  # Watermarks need to be visible
        },
        "text": {
            "algorithm": EncryptionAlgorithm.AES_256_GCM,
            "key_rotation_days": 90,
            "tokenization": True,
            "format_preservation": True
        }
    })
    
    # Creator-specific encryption levels
    encryption_by_tier: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "free": {
            "algorithm": EncryptionAlgorithm.AES_256_CBC,
            "key_size": 256,
            "compression": False
        },
        "basic": {
            "algorithm": EncryptionAlgorithm.AES_256_GCM,
            "key_size": 256,
            "compression": True,
            "integrity_check": True
        },
        "professional": {
            "algorithm": EncryptionAlgorithm.AES_256_GCM,
            "key_size": 256,
            "compression": True,
            "integrity_check": True,
            "forward_secrecy": True
        },
        "enterprise": {
            "algorithm": EncryptionAlgorithm.ChaCha20_Poly1305,
            "key_size": 256,
            "compression": True,
            "integrity_check": True,
            "forward_secrecy": True,
            "quantum_resistant": True
        }
    })


@dataclass
class DatabaseEncryptionConfig:
    """Database encryption configuration."""
    
    # Table-level encryption settings
    encrypted_tables: List[str] = field(default_factory=lambda: [
        "users",
        "creators",
        "content_files",
        "fingerprints", 
        "revenue_data",
        "api_keys",
        "session_data",
        "audit_logs"
    ])
    
    # Column-level encryption
    encrypted_columns: Dict[str, List[str]] = field(default_factory=lambda: {
        "users": ["email", "phone", "personal_data"],
        "creators": ["real_name", "tax_id", "bank_details", "address"],
        "content_files": ["file_path", "metadata", "original_filename"],
        "fingerprints": ["fingerprint_data", "similarity_vectors"],
        "revenue_data": ["amount", "payout_details", "tax_information"],
        "api_keys": ["key_value", "secret"],
        "session_data": ["session_content", "user_context"]
    })
    
    # Encryption at rest
    tablespace_encryption: bool = True
    backup_encryption: bool = True
    log_encryption: bool = True
    
    # Key management for database
    database_master_key_rotation_days: int = 180
    column_key_rotation_days: int = 90
    
    # Performance considerations
    encryption_cache_size: int = 256 * 1024 * 1024  # 256MB
    lazy_decryption: bool = True  # Decrypt only when needed


@dataclass
class TransmissionEncryptionConfig:
    """Data transmission encryption configuration."""
    
    # TLS configuration
    tls_version: str = "1.3"
    cipher_suites: List[str] = field(default_factory=lambda: [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256"
    ])
    
    # API encryption
    api_payload_encryption: bool = True
    api_response_encryption: bool = True
    
    # WebSocket encryption
    websocket_encryption: bool = True
    
    # File transfer encryption
    upload_encryption: bool = True
    download_encryption: bool = True
    
    # Platform-specific transmission
    platform_encryption: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "spotify": {
            "oauth_token_encryption": True,
            "api_request_signing": True,
            "response_validation": True
        },
        "youtube": {
            "oauth_token_encryption": True,
            "upload_stream_encryption": True,
            "metadata_encryption": True
        },
        "instagram": {
            "oauth_token_encryption": True,
            "media_encryption": True,
            "story_encryption": True
        }
    })


@dataclass
class KeyManagementConfig:
    """Key management system configuration."""
    
    # Key storage
    key_storage_backend: str = "hsm"  # hsm, vault, kms, local
    key_storage_config: Dict[str, Any] = field(default_factory=lambda: {
        "hsm": {
            "module_path": "/opt/cloudhsm/lib/libcloudhsm_pkcs11.so",
            "slot_id": 0,
            "pin_env_var": "HSM_PIN"
        },
        "vault": {
            "url": os.getenv("VAULT_URL", ""),
            "token": os.getenv("VAULT_TOKEN", ""),
            "mount_point": "ia-influencer-kms"
        },
        "aws_kms": {
            "region": os.getenv("AWS_REGION", "us-east-1"),
            "key_spec": "SYMMETRIC_DEFAULT",
            "key_usage": "ENCRYPT_DECRYPT"
        }
    })
    
    # Key lifecycle management
    automatic_rotation: bool = True
    rotation_schedule: Dict[KeyType, int] = field(default_factory=lambda: {
        KeyType.MASTER_KEY: 365,      # 1 year
        KeyType.DATA_KEY: 90,         # 3 months
        KeyType.CONTENT_KEY: 30,      # 1 month
        KeyType.API_KEY: 180,         # 6 months
        KeyType.SESSION_KEY: 1,       # 1 day
        KeyType.FINGERPRINT_KEY: 60,  # 2 months
        KeyType.REVENUE_KEY: 90       # 3 months
    })
    
    # Key backup and recovery
    key_backup_enabled: bool = True
    backup_encryption_enabled: bool = True
    backup_locations: List[str] = field(default_factory=lambda: ["primary", "secondary"])
    recovery_threshold: int = 3  # Shamir's secret sharing threshold
    
    # Key access control
    key_access_logging: bool = True
    multi_person_authorization: bool = True  # For sensitive operations
    key_usage_monitoring: bool = True
    
    # Emergency procedures
    emergency_key_revocation: bool = True
    key_compromise_procedures: bool = True


@dataclass
class QuantumResistanceConfig:
    """Quantum-resistant encryption configuration."""
    
    # Post-quantum cryptography
    quantum_safe_algorithms: List[str] = field(default_factory=lambda: [
        "CRYSTALS-Kyber",
        "CRYSTALS-Dilithium", 
        "FALCON",
        "SPHINCS+"
    ])
    
    # Hybrid classical-quantum approach
    hybrid_mode_enabled: bool = True
    classical_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    quantum_safe_algorithm: str = "CRYSTALS-Kyber"
    
    # Migration timeline
    quantum_migration_planned: bool = True
    migration_start_date: Optional[str] = "2030-01-01"
    full_migration_deadline: Optional[str] = "2035-01-01"


@dataclass
class ComplianceEncryptionConfig:
    """Compliance-specific encryption requirements."""
    
    # Regulatory compliance
    gdpr_compliant_encryption: bool = True
    ccpa_compliant_encryption: bool = True
    pci_dss_compliant: bool = True
    
    # Industry standards
    fips_140_2_level: int = 2  # FIPS 140-2 Level 2 compliance
    common_criteria_eal: int = 4  # Common Criteria EAL 4
    
    # Content protection compliance
    dmca_compliant_encryption: bool = True
    copyright_protection_encryption: bool = True
    
    # International compliance
    eu_data_protection: bool = True
    us_data_protection: bool = True
    export_control_compliance: bool = True


@dataclass
class PerformanceConfig:
    """
Encryption performance optimization configuration."""
    
    # Hardware acceleration
    hardware_acceleration: bool = True
    aes_ni_enabled: bool = True  # AES New Instructions
    avx_enabled: bool = True     # Advanced Vector Extensions
    
    # Parallel processing
    parallel_encryption: bool = True
    max_threads: int = 8
    thread_pool_size: int = 16
    
    # Caching
    encryption_cache_enabled: bool = True
    key_cache_size: int = 1000
    key_cache_ttl_seconds: int = 3600
    
    # Batch processing
    batch_encryption_enabled: bool = True
    batch_size: int = 100
    batch_timeout_seconds: int = 30


@dataclass
class EncryptionConfig:
    """
Main encryption configuration container."""
    
    # Core configurations
    content_encryption: ContentEncryptionConfig = field(default_factory=ContentEncryptionConfig)
    database_encryption: DatabaseEncryptionConfig = field(default_factory=DatabaseEncryptionConfig)
    transmission_encryption: TransmissionEncryptionConfig = field(default_factory=TransmissionEncryptionConfig)
    key_management: KeyManagementConfig = field(default_factory=KeyManagementConfig)
    quantum_resistance: QuantumResistanceConfig = field(default_factory=QuantumResistanceConfig)
    compliance: ComplianceEncryptionConfig = field(default_factory=ComplianceEncryptionConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Key configurations
    key_configs: Dict[KeyType, KeyConfiguration] = field(default_factory=lambda: {
        KeyType.MASTER_KEY: KeyConfiguration(
            key_type=KeyType.MASTER_KEY,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_size=256,
            rotation_days=365,
            kdf=KeyDerivationFunction.HKDF_SHA256
        ),
        KeyType.CONTENT_KEY: KeyConfiguration(
            key_type=KeyType.CONTENT_KEY,
            algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_size=256,
            rotation_days=30,
            max_encryptions=1000000
        ),
        KeyType.FINGERPRINT_KEY: KeyConfiguration(
            key_type=KeyType.FINGERPRINT_KEY,
            algorithm=EncryptionAlgorithm.ChaCha20_Poly1305,
            key_size=256,
            rotation_days=60
        )
    })
    
    # Global settings
    encryption_enabled: bool = True
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    
    # Security policies
    enforce_encryption_at_rest: bool = True
    enforce_encryption_in_transit: bool = True
    enforce_key_rotation: bool = True
    
    # Monitoring and alerting
    encryption_monitoring_enabled: bool = True
    key_usage_alerts: bool = True
    encryption_failure_alerts: bool = True
    
    # Development and testing
    test_key_generation: bool = False  # Only for development
    encryption_bypass_for_testing: bool = False  # Only for development


# Default configuration instance
encryption_config = EncryptionConfig()


def get_encryption_config() -> EncryptionConfig:
    """
Get the encryption configuration instance."""
    return encryption_config


def get_content_encryption_config(content_type: str, tier: str) -> Dict[str, Any]:
    """
Get encryption configuration for specific content type and tier."""
    config = get_encryption_config()
    
    # Get content type specific config
    content_config = config.content_encryption.content_type_configs.get(
        content_type, config.content_encryption.content_type_configs["text"]
    )
    
    # Get tier specific config
    tier_config = config.content_encryption.encryption_by_tier.get(
        tier, config.content_encryption.encryption_by_tier["basic"]
    )
    
    # Merge configurations
    merged_config = {**content_config, **tier_config}
    return merged_config


def validate_encryption_config(config: EncryptionConfig) -> bool:
    """Validate encryption configuration settings."""
    # Validate key configurations
    for key_config in config.key_configs.values():
        if key_config.key_size < 128:
            raise ValueError(f"Key size too small: {key_config.key_size}")
        
        if key_config.rotation_days < 1:
            raise ValueError(f"Invalid rotation period: {key_config.rotation_days}")
    
    # Validate algorithm support
    supported_algorithms = [alg.value for alg in EncryptionAlgorithm]
    if config.default_algorithm.value not in supported_algorithms:
        raise ValueError(f"Unsupported algorithm: {config.default_algorithm}")
    
    return True
