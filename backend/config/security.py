"""Security Configuration Module - Consolidated Security Configs
=============================================================

Consolidates all security-related configurations from:
- config/security/ (19 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import os

# ===== AUTHENTICATION CONFIGURATION =====

class AuthenticationMethod(str, Enum):
    """Authentication methods"""
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    API_KEY = "api_key"
    MULTI_FACTOR = "multi_factor"
    SAML = "saml"
    LDAP = "ldap"

class TokenType(str, Enum):
    """Token types"""
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    ID_TOKEN = "id_token"
    API_TOKEN = "api_token"

@dataclass
class AuthenticationConfig:
    """Authentication configuration"""
    method: AuthenticationMethod = AuthenticationMethod.JWT
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "ia-influencer-agent"
    audience: str = "ia-influencer-users"
    require_email_verification: bool = True
    allow_password_reset: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30

# ===== AUTHORIZATION CONFIGURATION =====

class Permission(str, Enum):
    """System permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SHARE = "share"
    MONETIZE = "monetize"

class UserRole(str, Enum):
    """User roles"""
    GUEST = "guest"
    USER = "user"
    CREATOR = "creator"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

@dataclass
class RoleDefinition:
    """Role definition with permissions"""
    name: UserRole
    permissions: List[Permission]
    resource_access: Dict[str, List[str]] = field(default_factory=dict)
    inherits_from: Optional[UserRole] = None

@dataclass
class AuthorizationConfig:
    """Authorization configuration"""
    enabled: bool = True
    default_role: UserRole = UserRole.USER
    require_permissions: bool = True
    roles: List[RoleDefinition] = field(default_factory=list)
    resource_based_access: bool = True
    inheritance_enabled: bool = True

# ===== ENCRYPTION CONFIGURATION =====

class EncryptionAlgorithm(str, Enum):
    """Encryption algorithms"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    FERNET = "fernet"

class HashingAlgorithm(str, Enum):
    """Hashing algorithms"""
    BCRYPT = "bcrypt"
    SCRYPT = "scrypt"
    ARGON2 = "argon2"
    PBKDF2 = "pbkdf2"
    SHA256 = "sha256"
    SHA512 = "sha512"

@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    default_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_enabled: bool = True
    key_rotation_days: int = 90
    password_hashing: HashingAlgorithm = HashingAlgorithm.BCRYPT
    bcrypt_rounds: int = 12
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    field_level_encryption: bool = True
    key_management_service: str = "local"  # local, aws_kms, azure_vault, hashicorp_vault

# ===== RATE LIMITING CONFIGURATION =====

class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitRule:
    """Rate limit rule"""
    name: str
    path_pattern: str
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    burst_allowed: bool = True
    burst_multiplier: float = 2.0

@dataclass
class RateLimitingConfig:
    """Rate limiting configuration"""
    enabled: bool = True
    default_requests_per_minute: int = 60
    default_requests_per_hour: int = 1000
    default_requests_per_day: int = 10000
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    rules: List[RateLimitRule] = field(default_factory=list)
    redis_backend: bool = True
    bypass_for_authenticated: bool = False
    custom_headers: bool = True

# ===== CONTENT VALIDATION CONFIGURATION =====

class ValidationLevel(str, Enum):
    """Content validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    PARANOID = "paranoid"

class ContentType(str, Enum):
    """Content types for validation"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"

@dataclass
class ContentValidationRule:
    """Content validation rule"""
    name: str
    content_type: ContentType
    max_file_size: int  # bytes
    allowed_extensions: List[str]
    allowed_mime_types: List[str]
    scan_for_malware: bool = True
    scan_for_inappropriate_content: bool = True
    extract_metadata: bool = True

@dataclass
class ContentValidationConfig:
    """Content validation configuration"""
    enabled: bool = True
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    max_upload_size: int = 104857600  # 100MB
    rules: List[ContentValidationRule] = field(default_factory=list)
    quarantine_suspicious: bool = True
    log_all_uploads: bool = True
    virus_scanning_enabled: bool = True
    content_filter_enabled: bool = True

# ===== AUDIT LOGGING CONFIGURATION =====

class AuditEventType(str, Enum):
    """Audit event types"""
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    DELETE = "delete"
    SHARE = "share"
    PAYMENT = "payment"
    ADMIN_ACTION = "admin_action"
    SECURITY_EVENT = "security_event"

@dataclass
class AuditLoggingConfig:
    """Audit logging configuration"""
    enabled: bool = True
    log_all_events: bool = False
    logged_events: List[AuditEventType] = field(default_factory=lambda: [
        AuditEventType.LOGIN,
        AuditEventType.UPLOAD,
        AuditEventType.DELETE,
        AuditEventType.ADMIN_ACTION,
        AuditEventType.SECURITY_EVENT
    ])
    retention_days: int = 365
    compress_logs: bool = True
    encrypt_logs: bool = True
    send_to_siem: bool = False
    siem_endpoint: Optional[str] = None

# ===== THREAT DETECTION CONFIGURATION =====

class ThreatLevel(str, Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AttackType(str, Enum):
    """Attack types"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDoS = "ddos"
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_EXFILTRATION = "data_exfiltration"

@dataclass
class ThreatDetectionRule:
    """Threat detection rule"""
    name: str
    attack_type: AttackType
    threshold: int
    time_window_minutes: int
    threat_level: ThreatLevel
    enabled: bool = True
    auto_block: bool = False
    notification_enabled: bool = True

@dataclass
class ThreatDetectionConfig:
    """Threat detection configuration"""
    enabled: bool = True
    real_time_monitoring: bool = True
    machine_learning_enabled: bool = True
    rules: List[ThreatDetectionRule] = field(default_factory=list)
    auto_response_enabled: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    integration_siem: bool = False

# ===== API SECURITY CONFIGURATION =====

@dataclass
class CorsConfig:
    """CORS configuration"""
    enabled: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    allowed_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    allowed_headers: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = True
    max_age: int = 3600

@dataclass
class CSPConfig:
    """Content Security Policy configuration"""
    enabled: bool = True
    default_src: List[str] = field(default_factory=lambda: ["'self'"])
    script_src: List[str] = field(default_factory=lambda: ["'self'"])
    style_src: List[str] = field(default_factory=lambda: ["'self'", "'unsafe-inline'"])
    img_src: List[str] = field(default_factory=lambda: ["'self'", "data:", "https:"])
    report_uri: Optional[str] = None

@dataclass
class ApiSecurityConfig:
    """API security configuration"""
    require_https: bool = True
    hsts_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year
    cors: CorsConfig = field(default_factory=CorsConfig)
    csp: CSPConfig = field(default_factory=CSPConfig)
    api_versioning_required: bool = True
    request_size_limit: int = 10485760  # 10MB
    response_compression: bool = True

# ===== COMPLIANCE CONFIGURATION =====

class ComplianceStandard(str, Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"

@dataclass
class ComplianceConfig:
    """Compliance configuration"""
    enabled_standards: List[ComplianceStandard] = field(default_factory=lambda: [
        ComplianceStandard.GDPR
    ])
    data_retention_days: int = 2555  # 7 years
    right_to_deletion: bool = True
    data_portability: bool = True
    consent_management: bool = True
    privacy_by_design: bool = True
    regular_audits: bool = True
    compliance_officer_email: Optional[str] = None

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_security_config() -> Dict[str, Any]:
    """Get development security configuration"""
    return {
        "authentication": AuthenticationConfig(
            jwt_secret_key="dev-secret-key",
            access_token_expire_minutes=60,
            require_email_verification=False
        ),
        "authorization": AuthorizationConfig(
            require_permissions=False
        ),
        "encryption": EncryptionConfig(
            encrypt_at_rest=False,
            key_rotation_enabled=False
        ),
        "rate_limiting": RateLimitingConfig(
            enabled=False
        ),
        "threat_detection": ThreatDetectionConfig(
            enabled=False
        ),
        "api_security": ApiSecurityConfig(
            require_https=False,
            hsts_enabled=False
        )
    }

def get_production_security_config() -> Dict[str, Any]:
    """Get production security configuration"""
    return {
        "authentication": AuthenticationConfig(
            jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-me-in-production"),
            access_token_expire_minutes=15,
            require_email_verification=True
        ),
        "authorization": AuthorizationConfig(
            require_permissions=True
        ),
        "encryption": EncryptionConfig(
            encrypt_at_rest=True,
            key_rotation_enabled=True
        ),
        "rate_limiting": RateLimitingConfig(
            enabled=True,
            default_requests_per_minute=30
        ),
        "threat_detection": ThreatDetectionConfig(
            enabled=True,
            real_time_monitoring=True
        ),
        "api_security": ApiSecurityConfig(
            require_https=True,
            hsts_enabled=True
        )
    }

def get_testing_security_config() -> Dict[str, Any]:
    """Get testing security configuration"""
    return {
        "authentication": AuthenticationConfig(
            jwt_secret_key="test-secret-key",
            access_token_expire_minutes=120,
            require_email_verification=False
        ),
        "authorization": AuthorizationConfig(
            require_permissions=True
        ),
        "encryption": EncryptionConfig(
            encrypt_at_rest=False,
            key_rotation_enabled=False
        ),
        "rate_limiting": RateLimitingConfig(
            enabled=False
        ),
        "threat_detection": ThreatDetectionConfig(
            enabled=False
        ),
        "api_security": ApiSecurityConfig(
            require_https=False,
            hsts_enabled=False
        )
    }

# ===== SECURITY CONFIGURATION FACTORY =====

class SecurityConfigurationFactory:
    """Factory for creating security configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> Dict[str, Any]:
        """Create security configuration for environment"""
        if environment.lower() == "production":
            return get_production_security_config()
        elif environment.lower() == "testing":
            return get_testing_security_config()
        else:
            return get_development_security_config()

# Export all security configurations
__all__ = [
    # Enums
    "AuthenticationMethod",
    "TokenType",
    "Permission", 
    "UserRole",
    "EncryptionAlgorithm",
    "HashingAlgorithm",
    "RateLimitStrategy",
    "ValidationLevel",
    "ContentType",
    "AuditEventType",
    "ThreatLevel",
    "AttackType",
    "ComplianceStandard",
    
    # Configuration Classes
    "AuthenticationConfig",
    "RoleDefinition",
    "AuthorizationConfig",
    "EncryptionConfig",
    "RateLimitRule",
    "RateLimitingConfig",
    "ContentValidationRule",
    "ContentValidationConfig",
    "AuditLoggingConfig",
    "ThreatDetectionRule",
    "ThreatDetectionConfig",
    "CorsConfig",
    "CSPConfig",
    "ApiSecurityConfig",
    "ComplianceConfig",
    
    # Factory and Functions
    "SecurityConfigurationFactory",
    "get_development_security_config",
    "get_production_security_config",
    "get_testing_security_config"
]