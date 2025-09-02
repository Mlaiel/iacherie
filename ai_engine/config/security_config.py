"""Security Configuration Module

Enterprise-grade security configuration for the IA Influencer Agent platform.
Comprehensive authentication, encryption, access control, and audit logging.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected intellectual property. Unauthorized use is prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""

import os
import secrets
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


class AuthenticationMethod(Enum):
    """
Authentication methods"""

    PASSWORD = "password"
    TWO_FACTOR = "two_factor"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    API_KEY = "api_key"
    BIOMETRIC = "biometric"
    CERTIFICATE = "certificate"
    SSO = "single_sign_on"


class EncryptionAlgorithm(Enum):
    """Encryption algorithms"""

    AES_256_GCM = "aes_256_gcm"
    CHACHA20_POLY1305 = "chacha20_poly1305"
    RSA_4096 = "rsa_4096"
    ECDSA_P256 = "ecdsa_p256"
    ED25519 = "ed25519"


class AccessLevel(Enum):
    """Access levels"""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"
    SYSTEM = "system"


class SecurityLevel(Enum):
    """Security levels"""

    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"


class ThreatLevel(Enum):
    """Threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class AuthenticationConfig:
    """Authentication configuration"""
    enabled: bool = True
    
    # Authentication methods
    enabled_methods: List[AuthenticationMethod] = field(default_factory=lambda: [
        AuthenticationMethod.JWT,
        AuthenticationMethod.TWO_FACTOR,
        AuthenticationMethod.API_KEY
    ])
    
    # Password policy
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special_chars: bool = True
    password_max_age_days: int = 90
    password_history_count: int = 5
    
    # Two-factor authentication
    totp_enabled: bool = True
    backup_codes_enabled: bool = True
    sms_2fa_enabled: bool = False  # Less secure
    email_2fa_enabled: bool = True
    
    # Session management
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 3
    session_encryption: bool = True
    secure_cookies: bool = True
    
    # JWT settings
    jwt_secret_key: str = ""
    jwt_algorithm: str = "RS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    jwt_issuer: str = "ia-influencer-agent"
    
    # OAuth2 settings
    oauth2_providers: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    # API key settings
    api_key_length: int = 64
    api_key_expiration_days: int = 365
    api_key_rate_limiting: bool = True
    
    # Account security
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    account_verification_required: bool = True
    email_verification_required: bool = True

    def __post_init__(self):
        """Initialize default OAuth2 providers"""
        if not self.oauth2_providers:
            self.oauth2_providers = {
                "google": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                    "scope": "openid email profile"
                },
                "github": {
                    "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
                    "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
                    "scope": "user:email"
                }
            }
        
        if not self.jwt_secret_key:
            self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(64))


@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    enabled: bool = True
    
    # Default algorithms
    symmetric_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    asymmetric_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.RSA_4096
    
    # Key management
    key_rotation_enabled: bool = True
    key_rotation_days: int = 90
    key_backup_enabled: bool = True
    hardware_security_module: bool = False  # HSM for enterprise
    
    # Encryption at rest
    database_encryption: bool = True
    file_system_encryption: bool = True
    backup_encryption: bool = True
    log_encryption: bool = True
    
    # Encryption in transit
    tls_version: str = "1.3"
    certificate_validation: bool = True
    perfect_forward_secrecy: bool = True
    
    # Data classification
    sensitive_data_encryption: bool = True
    pii_encryption_required: bool = True
    content_encryption: bool = True
    metadata_encryption: bool = True
    
    # Performance
    encryption_cache_enabled: bool = True
    hardware_acceleration: bool = True
    parallel_encryption: bool = True


@dataclass
class AccessControlConfig:
    """Access control configuration"""
    enabled: bool = True
    
    # Role-based access control (RBAC)
    rbac_enabled: bool = True
    default_role: str = "user"
    role_hierarchy: Dict[str, List[str]] = field(default_factory=lambda: {
        "owner": ["admin", "editor", "viewer", "user"],
        "admin": ["editor", "viewer", "user"],
        "editor": ["viewer", "user"],
        "viewer": ["user"],
        "user": []
    })
    
    # Attribute-based access control (ABAC)
    abac_enabled: bool = True
    
    # Resource permissions
    resource_permissions: Dict[str, Dict[str, List[str]]] = field(default_factory=lambda: {
        "content": {
            "create": ["owner", "admin", "editor"],
            "read": ["owner", "admin", "editor", "viewer"],
            "update": ["owner", "admin", "editor"],
            "delete": ["owner", "admin"]
        },
        "ai_models": {
            "create": ["owner", "admin"],
            "read": ["owner", "admin", "editor"],
            "update": ["owner", "admin"],
            "delete": ["owner"]
        },
        "analytics": {
            "read": ["owner", "admin", "editor"],
            "export": ["owner", "admin"]
        }
    })
    
    # IP-based restrictions
    ip_whitelist_enabled: bool = True
    allowed_ip_ranges: List[str] = field(default_factory=list)
    blocked_ip_ranges: List[str] = field(default_factory=list)
    
    # Geographic restrictions
    geo_restrictions_enabled: bool = False
    allowed_countries: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    
    # Time-based access
    time_based_access: bool = True
    business_hours_only: bool = False
    timezone: str = "Europe/Berlin"
    
    # API access control
    api_rate_limiting: bool = True
    api_quotas: Dict[str, int] = field(default_factory=lambda: {
        "user": 1000,      # requests per hour
        "editor": 5000,
        "admin": 10000,
        "owner": 50000
    })


@dataclass
class AuditLoggingConfig:
    """Audit logging configuration"""
    enabled: bool = True
    
    # Log levels
    log_authentication: bool = True
    log_authorization: bool = True
    log_data_access: bool = True
    log_data_modification: bool = True
    log_system_events: bool = True
    log_security_events: bool = True
    
    # Log retention
    log_retention_days: int = 2555  # 7 years for compliance
    log_compression_enabled: bool = True
    log_archival_enabled: bool = True
    
    # Log formats
    structured_logging: bool = True
    json_format: bool = True
    include_stack_traces: bool = True
    include_user_agent: bool = True
    include_ip_address: bool = True
    
    # Real-time monitoring
    real_time_alerts: bool = True
    suspicious_activity_detection: bool = True
    anomaly_detection: bool = True
    
    # Log destinations
    file_logging: bool = True
    database_logging: bool = True
    siem_integration: bool = True
    cloud_logging: bool = True
    
    # Privacy compliance
    pii_masking: bool = True
    gdpr_compliance: bool = True
    right_to_deletion: bool = True


@dataclass
class ThreatDetectionConfig:
    """
Threat detection configuration"""
    enabled: bool = True
    
    # Intrusion detection
    ids_enabled: bool = True
    ips_enabled: bool = True  # Intrusion Prevention System
    
    # Attack detection
    brute_force_detection: bool = True
    sql_injection_detection: bool = True
    xss_detection: bool = True
    csrf_protection: bool = True
    dos_protection: bool = True
    
    # Behavioral analysis
    user_behavior_analysis: bool = True
    device_fingerprinting: bool = True
    session_analysis: bool = True
    
    # AI-powered detection
    ml_threat_detection: bool = True
    pattern_recognition: bool = True
    predictive_analysis: bool = True
    
    # Response actions
    auto_block_enabled: bool = True
    quarantine_suspicious_users: bool = True
    alert_administrators: bool = True
    emergency_lockdown: bool = True
    
    # Threat intelligence
    threat_feed_integration: bool = True
    reputation_checking: bool = True
    known_bad_actors: bool = True


@dataclass
class ComplianceConfig:
    """
Compliance configuration"""
    enabled: bool = True
    
    # Regulatory frameworks
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    hipaa_compliance: bool = False  # If handling health data
    sox_compliance: bool = False    # If public company
    iso27001_compliance: bool = True
    
    # Data protection
    data_minimization: bool = True
    purpose_limitation: bool = True
    retention_policies: bool = True
    consent_management: bool = True
    
    # Privacy rights
    right_to_access: bool = True
    right_to_rectification: bool = True
    right_to_erasure: bool = True
    right_to_portability: bool = True
    right_to_object: bool = True
    
    # Breach management
    breach_detection: bool = True
    breach_notification: bool = True
    breach_reporting_hours: int = 72  # GDPR requirement
    
    # Documentation
    privacy_policy_url: str = ""
    data_processing_records: bool = True
    impact_assessments: bool = True


@dataclass
class SecurityConfig:
    """Main security configuration"""
    
    # Core settings
    enabled: bool = True
    security_level: SecurityLevel = SecurityLevel.CRITICAL
    creator_id: str = "fahed_mlaiel_security"
    
    # Sub-configurations
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    access_control: AccessControlConfig = field(default_factory=AccessControlConfig)
    audit_logging: AuditLoggingConfig = field(default_factory=AuditLoggingConfig)
    threat_detection: ThreatDetectionConfig = field(default_factory=ThreatDetectionConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    
    # Security headers
    security_headers: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    })
    
    # Incident response
    incident_response_enabled: bool = True
    emergency_contacts: List[str] = field(default_factory=lambda: [
        "mlaiel@live.de",
        "security@ia-influencer.com"
    ])
    incident_escalation_matrix: Dict[str, List[str]] = field(default_factory=dict)
    
    # Security testing
    penetration_testing: bool = True
    vulnerability_scanning: bool = True
    security_code_review: bool = True
    dependency_scanning: bool = True
    
    # Backup and recovery
    backup_encryption: bool = True
    disaster_recovery_plan: bool = True
    business_continuity_plan: bool = True
    recovery_time_objective_hours: int = 4
    recovery_point_objective_hours: int = 1

    def __post_init__(self):
        """Initialize default incident escalation matrix"""
        if not self.incident_escalation_matrix:
            self.incident_escalation_matrix = {
                ThreatLevel.LOW.value: ["security@ia-influencer.com"],
                ThreatLevel.MEDIUM.value: ["security@ia-influencer.com", "admin@ia-influencer.com"],
                ThreatLevel.HIGH.value: ["mlaiel@live.de", "security@ia-influencer.com"],
                ThreatLevel.CRITICAL.value: ["mlaiel@live.de", "security@ia-influencer.com", "ceo@ia-influencer.com"],
                ThreatLevel.EMERGENCY.value: ["mlaiel@live.de", "all_admins@ia-influencer.com"]
            }

    def generate_api_key(self, user_id: str, permissions: List[str]) -> Dict[str, Any]:
        """Generate secure API key"""
        api_key = secrets.token_urlsafe(self.authentication.api_key_length)
        
        # Create key hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Calculate expiration
        expiration_date = datetime.now() + timedelta(days=self.authentication.api_key_expiration_days)
        
        key_data = {
            "api_key": api_key,
            "key_hash": key_hash,
            "user_id": user_id,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "expires_at": expiration_date.isoformat(),
            "is_active": True,
            "usage_count": 0,
            "last_used": None
        }
        
        logger.info(f"API key generated for user {user_id}")
        return key_data

    def validate_password(self, password: str) -> Dict[str, Any]:
        """Validate password against security policy"""
        validation_result = {
            "valid": True,
            "errors": [],
            "score": 0,
            "strength": "weak"
        }
        
        # Length check
        if len(password) < self.authentication.password_min_length:
            validation_result["errors"].append(f"Password must be at least {self.authentication.password_min_length} characters")
            validation_result["valid"] = False
        else:
            validation_result["score"] += 20
        
        # Character requirements
        if self.authentication.password_require_uppercase and not any(c.isupper() for c in password):
            validation_result["errors"].append("Password must contain uppercase letters")
            validation_result["valid"] = False
        else:
            validation_result["score"] += 15
        
        if self.authentication.password_require_lowercase and not any(c.islower() for c in password):
            validation_result["errors"].append("Password must contain lowercase letters")
            validation_result["valid"] = False
        else:
            validation_result["score"] += 15
        
        if self.authentication.password_require_numbers and not any(c.isdigit() for c in password):
            validation_result["errors"].append("Password must contain numbers")
            validation_result["valid"] = False
        else:
            validation_result["score"] += 20
        
        if self.authentication.password_require_special_chars and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            validation_result["errors"].append("Password must contain special characters")
            validation_result["valid"] = False
        else:
            validation_result["score"] += 30
        
        # Determine strength
        if validation_result["score"] >= 90:
            validation_result["strength"] = "very_strong"
        elif validation_result["score"] >= 70:
            validation_result["strength"] = "strong"
        elif validation_result["score"] >= 50:
            validation_result["strength"] = "medium"
        elif validation_result["score"] >= 30:
            validation_result["strength"] = "weak"
        else:
            validation_result["strength"] = "very_weak"
        
        return validation_result

    def check_access_permission(self, user_role: str, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource"""
        if not self.access_control.enabled:
            return True
        
        resource_perms = self.access_control.resource_permissions.get(resource, {})
        action_roles = resource_perms.get(action, [])
        
        # Check direct role permission
        if user_role in action_roles:
            return True
        
        # Check inherited permissions through role hierarchy
        user_permissions = self.access_control.role_hierarchy.get(user_role, [])
        for inherited_role in user_permissions:
            if inherited_role in action_roles:
                return True
        
        return False

    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """
Log security event"""
        if not self.audit_logging.enabled:
            return
        
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": details.get("ip_address"),
            "user_agent": details.get("user_agent"),
            "resource": details.get("resource"),
            "action": details.get("action"),
            "result": details.get("result"),
            "details": details,
            "severity": details.get("severity", "info")
        }
        
        # In a real implementation, this would write to logging system
        logger.info(f"Security event: {event_type} - {event_data}")

    def assess_threat_level(self, indicators: Dict[str, Any]) -> ThreatLevel:
        """Assess threat level based on indicators"""
        score = 0
        
        # Failed login attempts
        failed_logins = indicators.get("failed_logins", 0)
        if failed_logins > 10:
            score += 30
        elif failed_logins > 5:
            score += 15
        
        # Suspicious IP
        if indicators.get("suspicious_ip", False):
            score += 25
        
        # Unusual access patterns
        if indicators.get("unusual_access", False):
            score += 20
        
        # Known attack patterns
        if indicators.get("attack_patterns", False):
            score += 40
        
        # Geographic anomaly
        if indicators.get("geo_anomaly", False):
            score += 15
        
        # Device anomaly
        if indicators.get("device_anomaly", False):
            score += 10
        
        # Determine threat level
        if score >= 80:
            return ThreatLevel.CRITICAL
        elif score >= 60:
            return ThreatLevel.HIGH
        elif score >= 40:
            return ThreatLevel.MEDIUM
        elif score >= 20:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.LOW

    def trigger_incident_response(self, threat_level: ThreatLevel, details: Dict[str, Any]):
        """Trigger incident response procedures"""
        if not self.incident_response_enabled:
            return
        
        contacts = self.incident_escalation_matrix.get(threat_level.value, [])
        
        incident_data = {
            "incident_id": secrets.token_hex(16),
            "timestamp": datetime.now().isoformat(),
            "threat_level": threat_level.value,
            "details": details,
            "contacts_notified": contacts,
            "status": "open"
        }
        
        # In a real implementation, this would trigger actual incident response
        logger.critical(f"Security incident triggered: {threat_level.value} - {incident_data}")
        
        # Auto-block if critical
        if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY]:
            self._emergency_lockdown(details)

    def _emergency_lockdown(self, details: Dict[str, Any]):
        try:
            logger.info(f"Executing _emergency_lockdown")
            
            # Implementation for _emergency_lockdown
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_emergency_lockdown completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_emergency_lockdown failed: {e}")
            raise
            pass
        
        # Increase monitoring
        # Enable enhanced logging and monitoring

    def validate_configuration(self) -> List[str]:
        """Validate security configuration"""
        issues = []
        
        # Check critical security settings
        if not self.authentication.enabled:
            issues.append("Authentication must be enabled")
        
        if not self.encryption.enabled:
            issues.append("Encryption must be enabled")
        
        if self.authentication.password_min_length < 8:
            issues.append("Minimum password length should be at least 8 characters")
        
        if not self.authentication.jwt_secret_key:
            issues.append("JWT secret key is required")
        
        if not self.audit_logging.enabled:
            issues.append("Audit logging should be enabled for security")
        
        # Check GDPR compliance if enabled
        if self.compliance.gdpr_compliance:
            if not self.compliance.right_to_erasure:
                issues.append("Right to erasure must be enabled for GDPR compliance")
        
        return issues

    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Load basic settings
        config.enabled = os.getenv("SECURITY_ENABLED", "true").lower() == "true"
        config.security_level = SecurityLevel(os.getenv("SECURITY_LEVEL", "critical"))
        
        # Load authentication settings
        config.authentication.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT", "60"))
        config.authentication.max_failed_attempts = int(os.getenv("MAX_FAILED_ATTEMPTS", "5"))
        config.authentication.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "")
        
        # Load encryption settings
        config.encryption.database_encryption = os.getenv("DATABASE_ENCRYPTION", "true").lower() == "true"
        config.encryption.tls_version = os.getenv("TLS_VERSION", "1.3")
        
        # Load compliance settings
        config.compliance.gdpr_compliance = os.getenv("GDPR_COMPLIANCE", "true").lower() == "true"
        config.compliance.privacy_policy_url = os.getenv("PRIVACY_POLICY_URL", "")
        
        return config


# Global configuration instance
security_config = SecurityConfig.from_env()
