"""
Security Configuration Module
============================

Enterprise-grade security configuration for the Ainflue Distribution Module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2024 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Set
from enum import Enum
import os
from pathlib import Path

class SecurityLevel(Enum):
    """Security configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"

class ThreatLevel(Enum):
    """Threat level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_4096 = "rsa_4096"
    ED25519 = "ed25519"

@dataclass
class AuthenticationConfig:
    """Authentication configuration"""
    
    # JWT Configuration
    jwt_secret_key: str = field(default_factory=lambda: os.getenv('JWT_SECRET_KEY', ''))
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_token_days: int = 30
    
    # Multi-factor Authentication
    mfa_enabled: bool = True
    mfa_required_for_admin: bool = True
    mfa_methods: List[str] = field(default_factory=lambda: ["totp", "sms", "email"])
    
    # OAuth2 Configuration
    oauth2_enabled: bool = True
    oauth2_providers: List[str] = field(default_factory=lambda: [
        "google", "facebook", "twitter", "linkedin", "github"
    ])
    
    # Password Policy
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    password_history_count: int = 10
    password_expiration_days: int = 90
    
    # Session Management
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 5
    force_logout_on_password_change: bool = True

@dataclass
class APISecurityConfig:
    """API security configuration"""
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    default_rate_limit_per_minute: int = 100
    authenticated_rate_limit_per_minute: int = 1000
    
    # API Key Configuration
    api_key_required: bool = True
    api_key_length: int = 64
    api_key_rotation_days: int = 90
    
    # Request Validation
    validate_content_type: bool = True
    max_request_size_mb: int = 100
    allowed_content_types: List[str] = field(default_factory=lambda: [
        "application/json",
        "multipart/form-data",
        "application/x-www-form-urlencoded"
    ])
    
    # CORS Configuration
    cors_enabled: bool = True
    cors_allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_allowed_methods: List[str] = field(default_factory=lambda: [
        "GET", "POST", "PUT", "DELETE", "OPTIONS"
    ])
    cors_allowed_headers: List[str] = field(default_factory=lambda: [
        "Authorization", "Content-Type", "X-API-Key"
    ])
    
    # Security Headers
    security_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    })

@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    
    # Encryption Settings
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int = 30
    
    # Data Encryption
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    encrypt_in_memory: bool = True
    
    # Database Encryption
    database_encryption_enabled: bool = True
    database_encryption_key: str = field(default_factory=lambda: os.getenv('DB_ENCRYPTION_KEY', ''))
    
    # File Encryption
    file_encryption_enabled: bool = True
    encrypted_file_extensions: List[str] = field(default_factory=lambda: [
        ".json", ".txt", ".log", ".csv", ".xml"
    ])
    
    # Key Management
    key_storage_method: str = "vault"  # "vault", "file", "env"
    key_backup_enabled: bool = True
    key_escrow_enabled: bool = False

@dataclass
class VaultConfig:
    """Credential vault configuration"""
    
    # Vault Settings
    vault_enabled: bool = True
    vault_url: str = field(default_factory=lambda: os.getenv('VAULT_URL', ''))
    vault_token: str = field(default_factory=lambda: os.getenv('VAULT_TOKEN', ''))
    vault_namespace: str = "distribution"
    
    # Secret Management
    secret_rotation_enabled: bool = True
    secret_rotation_interval_days: int = 30
    secret_versioning_enabled: bool = True
    secret_history_retention_days: int = 90
    
    # Platform Credentials Storage
    platform_credentials_path: str = "secret/platforms"
    api_keys_path: str = "secret/api-keys"
    certificates_path: str = "secret/certificates"
    
    # Backup and Recovery
    vault_backup_enabled: bool = True
    vault_backup_interval_hours: int = 6
    vault_recovery_keys_required: int = 3

@dataclass
class ThreatDetectionConfig:
    """Threat detection configuration"""
    
    # Detection Settings
    threat_detection_enabled: bool = True
    real_time_monitoring: bool = True
    
    # Anomaly Detection
    anomaly_detection_enabled: bool = True
    anomaly_threshold_score: float = 0.8
    learning_period_days: int = 30
    
    # Threat Categories
    monitored_threats: List[str] = field(default_factory=lambda: [
        "brute_force_attack",
        "sql_injection",
        "xss_attack",
        "ddos_attack",
        "account_takeover",
        "data_exfiltration",
        "privilege_escalation",
        "malware_upload"
    ])
    
    # Response Actions
    auto_block_enabled: bool = True
    auto_block_duration_minutes: int = 60
    escalation_threshold: int = 5
    
    # Logging and Alerting
    log_threats: bool = True
    alert_on_threat: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["email", "slack", "sms"])

@dataclass
class ComplianceConfig:
    """Compliance and regulatory configuration"""
    
    # Regulatory Frameworks
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    coppa_compliance: bool = True
    hipaa_compliance: bool = False
    
    # Data Protection
    data_minimization: bool = True
    data_retention_days: int = 365
    data_anonymization: bool = True
    right_to_deletion: bool = True
    
    # Privacy Settings
    privacy_by_design: bool = True
    consent_management: bool = True
    cookie_consent_required: bool = True
    
    # Audit Requirements
    audit_logging_enabled: bool = True
    audit_log_retention_years: int = 7
    audit_trail_integrity: bool = True
    compliance_reporting: bool = True

@dataclass
class AccessControlConfig:
    """Access control configuration"""
    
    # Role-Based Access Control (RBAC)
    rbac_enabled: bool = True
    default_role: str = "viewer"
    role_hierarchy: Dict[str, List[str]] = field(default_factory=lambda: {
        "admin": ["all"],
        "manager": ["read", "write", "delete"],
        "editor": ["read", "write"],
        "viewer": ["read"]
    })
    
    # Attribute-Based Access Control (ABAC)
    abac_enabled: bool = True
    
    # Permission Levels
    permission_levels: List[str] = field(default_factory=lambda: [
        "read", "write", "delete", "admin", "owner"
    ])
    
    # Resource Access
    resource_isolation: bool = True
    tenant_isolation: bool = True
    
    # Privileged Access
    privileged_access_monitoring: bool = True
    just_in_time_access: bool = True
    privileged_session_recording: bool = True

@dataclass
class SecurityMonitoringConfig:
    """Security monitoring configuration"""
    
    # Monitoring Settings
    security_monitoring_enabled: bool = True
    real_time_alerts: bool = True
    
    # Metrics Collection
    collect_security_metrics: bool = True
    metrics_retention_days: int = 90
    
    # Security Events
    log_security_events: bool = True
    security_event_retention_days: int = 365
    
    # SIEM Integration
    siem_enabled: bool = True
    siem_endpoint: str = field(default_factory=lambda: os.getenv('SIEM_ENDPOINT', ''))
    
    # Incident Response
    auto_incident_creation: bool = True
    incident_escalation_enabled: bool = True
    incident_response_team: List[str] = field(default_factory=lambda: [
        "security@ainflue.com", "incidents@ainflue.com"
    ])

@dataclass
class SecurityConfig:
    """Main security configuration"""
    
    # Security Level
    security_level: SecurityLevel = SecurityLevel.ENTERPRISE
    
    # Sub-configurations
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    api_security: APISecurityConfig = field(default_factory=APISecurityConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    vault: VaultConfig = field(default_factory=VaultConfig)
    threat_detection: ThreatDetectionConfig = field(default_factory=ThreatDetectionConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    access_control: AccessControlConfig = field(default_factory=AccessControlConfig)
    monitoring: SecurityMonitoringConfig = field(default_factory=SecurityMonitoringConfig)
    
    # Global Security Settings
    security_enabled: bool = True
    debug_mode: bool = False
    development_mode: bool = False
    
    # Environment Settings
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'production'))
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create security configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        if os.getenv('SECURITY_LEVEL'):
            config.security_level = SecurityLevel(os.getenv('SECURITY_LEVEL'))
        
        if os.getenv('ENVIRONMENT'):
            config.environment = os.getenv('ENVIRONMENT')
            
        # Development mode adjustments
        if config.environment == 'development':
            config.development_mode = True
            config.api_security.rate_limit_enabled = False
            config.threat_detection.auto_block_enabled = False
        
        return config
    
    def validate(self) -> List[str]:
        """Validate security configuration"""
        issues = []
        
        # Check required secrets
        if not self.authentication.jwt_secret_key:
            issues.append("JWT secret key is not configured")
        
        if self.vault.vault_enabled and not self.vault.vault_url:
            issues.append("Vault URL is required when vault is enabled")
        
        if self.encryption.database_encryption_enabled and not self.encryption.database_encryption_key:
            issues.append("Database encryption key is required")
        
        # Security level validations
        if self.security_level == SecurityLevel.MAXIMUM:
            if not self.authentication.mfa_enabled:
                issues.append("MFA must be enabled for maximum security level")
            
            if not self.encryption.encrypt_in_memory:
                issues.append("In-memory encryption required for maximum security")
        
        return issues
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "security_level": self.security_level.value,
            "authentication": self.authentication.__dict__,
            "api_security": self.api_security.__dict__,
            "encryption": self.encryption.__dict__,
            "vault": self.vault.__dict__,
            "threat_detection": self.threat_detection.__dict__,
            "compliance": self.compliance.__dict__,
            "access_control": self.access_control.__dict__,
            "monitoring": self.monitoring.__dict__,
            "global_settings": {
                "security_enabled": self.security_enabled,
                "debug_mode": self.debug_mode,
                "development_mode": self.development_mode,
                "environment": self.environment
            }
        }

# Default security configuration
DEFAULT_SECURITY_CONFIG = SecurityConfig()

# Environment-based security configuration
SECURITY_CONFIG = SecurityConfig.from_env()

__all__ = [
    "SecurityLevel",
    "ThreatLevel", 
    "EncryptionAlgorithm",
    "AuthenticationConfig",
    "APISecurityConfig",
    "EncryptionConfig",
    "VaultConfig",
    "ThreatDetectionConfig",
    "ComplianceConfig",
    "AccessControlConfig",
    "SecurityMonitoringConfig",
    "SecurityConfig",
    "DEFAULT_SECURITY_CONFIG",
    "SECURITY_CONFIG"
]