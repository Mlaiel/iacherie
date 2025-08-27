"""
Advanced Security Configurations for Crawlers
============================================

Enterprise-grade security configuration system for content crawling operations.
Provides comprehensive security controls, threat protection, and compliance management.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path
import hashlib
import secrets

class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    MAXIMUM = "maximum"

class ThreatLevel(Enum):
    """Threat level classifications."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"

class AuthenticationMethod(Enum):
    """Authentication methods for secure access."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    MUTUAL_TLS = "mutual_tls"
    CERTIFICATE = "certificate"
    MULTI_FACTOR = "multi_factor"
    BIOMETRIC = "biometric"

class EncryptionStandard(Enum):
    """Encryption standards."""
    AES_128 = "aes_128"
    AES_256 = "aes_256"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    ECDSA = "ecdsa"
    CHACHA20 = "chacha20"

class ComplianceFramework(Enum):
    """Compliance frameworks."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"

@dataclass
class EncryptionConfig:
    """Configuration for data encryption."""
    enabled: bool = True
    standard: EncryptionStandard = EncryptionStandard.AES_256
    key_rotation_days: int = 30
    key_storage_method: str = "secure_vault"  # secure_vault, hsm, kms
    encrypt_in_transit: bool = True
    encrypt_at_rest: bool = True
    encrypt_in_memory: bool = True
    
    # Key management
    master_key_path: Optional[str] = None
    key_derivation_iterations: int = 100000
    salt_length: int = 32
    iv_length: int = 16
    
    # Certificates
    tls_cert_path: Optional[str] = None
    tls_key_path: Optional[str] = None
    ca_cert_path: Optional[str] = None
    cert_validation_enabled: bool = True

@dataclass
class AccessControlConfig:
    """Configuration for access control and permissions."""
    enabled: bool = True
    
    # Role-based access control
    rbac_enabled: bool = True
    default_role: str = "guest"
    role_hierarchy: Dict[str, List[str]] = field(default_factory=lambda: {
        "admin": ["moderator", "user", "guest"],
        "moderator": ["user", "guest"],
        "user": ["guest"]
    })
    
    # Permission system
    resource_permissions: Dict[str, List[str]] = field(default_factory=dict)
    operation_permissions: Dict[str, List[str]] = field(default_factory=dict)
    time_based_access: bool = True
    location_based_access: bool = True
    
    # Session management
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 5
    session_encryption: bool = True
    secure_cookies: bool = True
    
    # Multi-factor authentication
    mfa_enabled: bool = True
    mfa_methods: List[str] = field(default_factory=lambda: ["totp", "sms", "email"])
    mfa_backup_codes: bool = True
    mfa_grace_period_hours: int = 24

@dataclass
class ThreatProtectionConfig:
    """Configuration for threat detection and protection."""
    enabled: bool = True
    
    # Intrusion detection
    ids_enabled: bool = True
    behavioral_analysis: bool = True
    anomaly_detection: bool = True
    signature_based_detection: bool = True
    
    # Rate limiting and DDoS protection
    rate_limiting_enabled: bool = True
    ddos_protection_enabled: bool = True
    ip_reputation_checking: bool = True
    geoblocking_enabled: bool = True
    blocked_countries: List[str] = field(default_factory=list)
    
    # Malware protection
    malware_scanning: bool = True
    virus_scanning: bool = True
    content_filtering: bool = True
    url_reputation_checking: bool = True
    
    # Honeypots and deception
    honeypot_enabled: bool = True
    honeypot_locations: List[str] = field(default_factory=lambda: ["/admin", "/backup", "/.env"])
    deception_techniques: bool = True
    
    # Response mechanisms
    auto_blocking_enabled: bool = True
    quarantine_enabled: bool = True
    incident_reporting: bool = True
    forensic_logging: bool = True

@dataclass
class ComplianceConfig:
    """Configuration for regulatory compliance."""
    enabled: bool = True
    
    # Applicable frameworks
    frameworks: List[ComplianceFramework] = field(default_factory=lambda: [
        ComplianceFramework.GDPR,
        ComplianceFramework.ISO_27001
    ])
    
    # Data protection
    data_minimization: bool = True
    purpose_limitation: bool = True
    storage_limitation: bool = True
    consent_management: bool = True
    right_to_erasure: bool = True
    data_portability: bool = True
    
    # Audit and reporting
    audit_logging: bool = True
    compliance_reporting: bool = True
    breach_notification: bool = True
    privacy_impact_assessment: bool = True
    
    # Retention policies
    data_retention_days: int = 365
    log_retention_days: int = 2555  # 7 years
    backup_retention_days: int = 90
    
    # Cross-border data transfer
    data_localization: bool = True
    cross_border_restrictions: List[str] = field(default_factory=list)
    adequacy_decisions: Dict[str, bool] = field(default_factory=dict)

@dataclass
class SecurityMonitoringConfig:
    """Configuration for security monitoring and alerting."""
    enabled: bool = True
    
    # Monitoring scope
    real_time_monitoring: bool = True
    network_monitoring: bool = True
    application_monitoring: bool = True
    data_monitoring: bool = True
    user_activity_monitoring: bool = True
    
    # Alert configuration
    security_alerts: bool = True
    threshold_alerts: bool = True
    anomaly_alerts: bool = True
    compliance_alerts: bool = True
    
    # Alert channels
    email_alerts: bool = True
    sms_alerts: bool = True
    slack_alerts: bool = True
    webhook_alerts: bool = True
    
    # SIEM integration
    siem_enabled: bool = True
    siem_endpoint: Optional[str] = None
    log_forwarding: bool = True
    correlation_rules: List[str] = field(default_factory=list)
    
    # Metrics and dashboards
    security_metrics: bool = True
    compliance_metrics: bool = True
    threat_intelligence: bool = True
    risk_scoring: bool = True

@dataclass
class VulnerabilityManagementConfig:
    """Configuration for vulnerability management."""
    enabled: bool = True
    
    # Scanning configuration
    vulnerability_scanning: bool = True
    dependency_scanning: bool = True
    container_scanning: bool = True
    code_scanning: bool = True
    
    # Scan frequency
    daily_scans: bool = True
    weekly_deep_scans: bool = True
    monthly_compliance_scans: bool = True
    on_demand_scans: bool = True
    
    # Remediation
    auto_patching: bool = False
    patch_testing: bool = True
    vulnerability_prioritization: bool = True
    remediation_tracking: bool = True
    
    # Reporting
    vulnerability_reports: bool = True
    trend_analysis: bool = True
    risk_assessment: bool = True
    executive_summaries: bool = True

class SecurityConfigManager:
    """Manager for security configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize security configuration manager."""
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent
        self.encryption = EncryptionConfig()
        self.access_control = AccessControlConfig()
        self.threat_protection = ThreatProtectionConfig()
        self.compliance = ComplianceConfig()
        self.monitoring = SecurityMonitoringConfig()
        self.vulnerability_management = VulnerabilityManagementConfig()
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        """Load security configurations from files."""
        try:
            config_file = self.config_dir / "security_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load configurations from file
                    if 'encryption' in data:
                        self.encryption = EncryptionConfig(**data['encryption'])
                    if 'access_control' in data:
                        self.access_control = AccessControlConfig(**data['access_control'])
        except Exception as e:
            print(f"Error loading security configurations: {e}")
    
    def generate_api_key(self, length: int = 32) -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify a password against its hash."""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == hashed
    
    def check_security_compliance(self) -> Dict[str, Any]:
        """Check current security compliance status."""
        compliance_status = {
            "overall_score": 0.0,
            "checks": {},
            "recommendations": []
        }
        
        checks = [
            ("encryption_enabled", self.encryption.enabled),
            ("access_control_enabled", self.access_control.enabled),
            ("mfa_enabled", self.access_control.mfa_enabled),
            ("threat_protection_enabled", self.threat_protection.enabled),
            ("monitoring_enabled", self.monitoring.enabled),
            ("vulnerability_scanning", self.vulnerability_management.enabled)
        ]
        
        passed_checks = sum(1 for _, status in checks if status)
        compliance_status["overall_score"] = (passed_checks / len(checks)) * 100
        
        for check_name, status in checks:
            compliance_status["checks"][check_name] = status
            if not status:
                compliance_status["recommendations"].append(f"Enable {check_name.replace('_', ' ')}")
        
        return compliance_status
    
    def get_security_policies(self) -> Dict[str, Any]:
        """Get comprehensive security policies."""
        return {
            "password_policy": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_symbols": True,
                "max_age_days": 90,
                "history_count": 12
            },
            "session_policy": {
                "timeout_minutes": self.access_control.session_timeout_minutes,
                "max_concurrent": self.access_control.max_concurrent_sessions,
                "secure_cookies": self.access_control.secure_cookies
            },
            "encryption_policy": {
                "standard": self.encryption.standard.value,
                "key_rotation_days": self.encryption.key_rotation_days,
                "encrypt_in_transit": self.encryption.encrypt_in_transit,
                "encrypt_at_rest": self.encryption.encrypt_at_rest
            }
        }
    
    def validate_security_configuration(self) -> Dict[str, List[str]]:
        """Validate security configuration."""
        issues = {"errors": [], "warnings": []}
        
        if not self.encryption.enabled:
            issues["errors"].append("Encryption is disabled")
        
        if not self.access_control.mfa_enabled:
            issues["warnings"].append("Multi-factor authentication is disabled")
        
        if self.access_control.session_timeout_minutes > 480:  # 8 hours
            issues["warnings"].append("Session timeout is too long")
        
        if not self.threat_protection.enabled:
            issues["errors"].append("Threat protection is disabled")
        
        return issues

# Global security configuration manager
security_config_manager = SecurityConfigManager()

# Security configuration presets
SECURITY_PRESETS = {
    "development": {
        "encryption": {"enabled": True, "standard": EncryptionStandard.AES_128},
        "access_control": {"mfa_enabled": False, "session_timeout_minutes": 480},
        "threat_protection": {"enabled": True, "auto_blocking_enabled": False}
    },
    "staging": {
        "encryption": {"enabled": True, "standard": EncryptionStandard.AES_256},
        "access_control": {"mfa_enabled": True, "session_timeout_minutes": 240},
        "threat_protection": {"enabled": True, "auto_blocking_enabled": True}
    },
    "production": {
        "encryption": {"enabled": True, "standard": EncryptionStandard.AES_256},
        "access_control": {"mfa_enabled": True, "session_timeout_minutes": 60},
        "threat_protection": {"enabled": True, "auto_blocking_enabled": True}
    }
}
