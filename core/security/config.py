"""Security Configuration Module
Advanced security configuration for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms
"""from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import os


class SecurityLevel(Enum):
    """Security levels for different environments"""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


@dataclass
class AuthenticationConfig:
    """Authentication configuration"""    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    session_timeout_minutes: int = 120
    require_2fa: bool = False
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True


@dataclass
class EncryptionConfig:
    """Encryption configuration"""    default_algorithm: str = "AES_256_GCM"
    key_rotation_days: int = 90
    encryption_key: str = ""
    signing_key: str = ""
    use_hsm: bool = False
    hsm_config: Dict[str, Any] = field(default_factory=dict)
    quantum_resistant: bool = False


@dataclass
class MonitoringConfig:
    """Security monitoring configuration"""    enabled: bool = True
    log_level: str = "INFO"
    alert_threshold_high: int = 10
    alert_threshold_critical: int = 5
    retention_days: int = 365
    real_time_analysis: bool = True
    threat_intelligence_feeds: List[str] = field(default_factory=list)
    anomaly_detection_sensitivity: float = 0.8


@dataclass
class FirewallConfig:
    """API firewall configuration"""    enabled: bool = True
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200
    ddos_protection_enabled: bool = True
    geo_blocking_enabled: bool = False
    allowed_countries: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    bot_protection_enabled: bool = True
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)


@dataclass
class ComplianceConfig:
    """Compliance configuration"""    gdpr_enabled: bool = True
    ccpa_enabled: bool = True
    dmca_enabled: bool = True
    audit_logging: bool = True
    data_retention_days: int = 2555  # 7 years
    auto_deletion_enabled: bool = True
    privacy_by_design: bool = True
    consent_management: bool = True


@dataclass
class ValidationConfig:
    """Content validation configuration"""    malware_scanning_enabled: bool = True
    virus_scanning_enabled: bool = True
    content_analysis_enabled: bool = True
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(default_factory=lambda: [
        'audio/mpeg', 'audio/wav', 'audio/flac',
        'video/mp4', 'video/avi', 'video/mov',
        'image/jpeg', 'image/png', 'image/gif',
        'text/plain', 'application/pdf'
    ])
    quarantine_suspicious_files: bool = True


@dataclass
class SecurityConfig:
    """Main security configuration"""    security_level: SecurityLevel = SecurityLevel.PRODUCTION
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    firewall: FirewallConfig = field(default_factory=FirewallConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization"""        self._validate_config()
    
    def _validate_config(self):
        """Validate security configuration"""        # Validate required keys
        if not self.authentication.jwt_secret_key:
            if self.security_level in [SecurityLevel.PRODUCTION, SecurityLevel.ENTERPRISE]:
                raise ValueError("JWT secret key is required for production environments")
        
        if not self.encryption.encryption_key:
            if self.security_level in [SecurityLevel.PRODUCTION, SecurityLevel.ENTERPRISE]:
                raise ValueError("Encryption key is required for production environments")
        
        # Validate security level requirements
        if self.security_level == SecurityLevel.ENTERPRISE:
            self._validate_enterprise_requirements()
    
    def _validate_enterprise_requirements(self):
        """Validate enterprise security requirements"""        requirements = {
            "2FA must be enabled": self.authentication.require_2fa,
            "Quantum resistance should be enabled": self.encryption.quantum_resistant,
            "Real-time monitoring must be enabled": self.monitoring.real_time_analysis,
            "DDoS protection must be enabled": self.firewall.ddos_protection_enabled,
            "Bot protection must be enabled": self.firewall.bot_protection_enabled,
            "GDPR compliance must be enabled": self.compliance.gdpr_enabled,
            "Audit logging must be enabled": self.compliance.audit_logging,
            "Malware scanning must be enabled": self.validation.malware_scanning_enabled
        }
        
        failures = [req for req, enabled in requirements.items() if not enabled]
        if failures:
            raise ValueError(f"Enterprise security requirements not met: {', '.join(failures)}")


def load_security_config() -> SecurityConfig:
    """Load security configuration from environment variables"""    config = SecurityConfig()
    
    # Security Level
    security_level = os.getenv('SECURITY_LEVEL', 'production').lower()
    if security_level in [level.value for level in SecurityLevel]:
        config.security_level = SecurityLevel(security_level)
    
    # Authentication Configuration
    config.authentication.jwt_secret_key = os.getenv('JWT_SECRET_KEY', '')
    config.authentication.jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
    config.authentication.jwt_expire_minutes = int(os.getenv('JWT_EXPIRE_MINUTES', '30'))
    config.authentication.refresh_token_expire_days = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    config.authentication.max_login_attempts = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    config.authentication.require_2fa = os.getenv('REQUIRE_2FA', 'false').lower() == 'true'
    
    # Encryption Configuration
    config.encryption.encryption_key = os.getenv('ENCRYPTION_KEY', '')
    config.encryption.signing_key = os.getenv('SIGNING_KEY', '')
    config.encryption.key_rotation_days = int(os.getenv('KEY_ROTATION_DAYS', '90'))
    config.encryption.quantum_resistant = os.getenv('QUANTUM_RESISTANT', 'false').lower() == 'true'
    
    # Monitoring Configuration
    config.monitoring.enabled = os.getenv('SECURITY_MONITORING_ENABLED', 'true').lower() == 'true'
    config.monitoring.log_level = os.getenv('SECURITY_LOG_LEVEL', 'INFO')
    config.monitoring.retention_days = int(os.getenv('SECURITY_LOG_RETENTION_DAYS', '365'))
    config.monitoring.real_time_analysis = os.getenv('REAL_TIME_ANALYSIS', 'true').lower() == 'true'
    
    # Firewall Configuration
    config.firewall.enabled = os.getenv('FIREWALL_ENABLED', 'true').lower() == 'true'
    config.firewall.rate_limit_per_minute = int(os.getenv('RATE_LIMIT_PER_MINUTE', '100'))
    config.firewall.ddos_protection_enabled = os.getenv('DDOS_PROTECTION_ENABLED', 'true').lower() == 'true'
    config.firewall.bot_protection_enabled = os.getenv('BOT_PROTECTION_ENABLED', 'true').lower() == 'true'
    
    # Compliance Configuration
    config.compliance.gdpr_enabled = os.getenv('GDPR_ENABLED', 'true').lower() == 'true'
    config.compliance.ccpa_enabled = os.getenv('CCPA_ENABLED', 'true').lower() == 'true'
    config.compliance.dmca_enabled = os.getenv('DMCA_ENABLED', 'true').lower() == 'true'
    config.compliance.audit_logging = os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'
    
    # Validation Configuration
    config.validation.malware_scanning_enabled = os.getenv('MALWARE_SCANNING_ENABLED', 'true').lower() == 'true'
    config.validation.virus_scanning_enabled = os.getenv('VIRUS_SCANNING_ENABLED', 'true').lower() == 'true'
    config.validation.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
    
    return config


# Default configurations for different environments
SECURITY_CONFIGS = {
    SecurityLevel.DEVELOPMENT: SecurityConfig(
        security_level=SecurityLevel.DEVELOPMENT,
        authentication=AuthenticationConfig(
            jwt_expire_minutes=60,
            require_2fa=False,
            max_login_attempts=10
        ),
        monitoring=MonitoringConfig(
            log_level="DEBUG",
            real_time_analysis=False
        ),
        firewall=FirewallConfig(
            rate_limit_per_minute=1000,
            ddos_protection_enabled=False
        )
    ),
    
    SecurityLevel.PRODUCTION: SecurityConfig(
        security_level=SecurityLevel.PRODUCTION,
        authentication=AuthenticationConfig(
            jwt_expire_minutes=30,
            require_2fa=True,
            max_login_attempts=5
        ),
        monitoring=MonitoringConfig(
            log_level="INFO",
            real_time_analysis=True,
            alert_threshold_high=10,
            alert_threshold_critical=5
        ),
        firewall=FirewallConfig(
            rate_limit_per_minute=100,
            ddos_protection_enabled=True,
            bot_protection_enabled=True
        )
    ),
    
    SecurityLevel.ENTERPRISE: SecurityConfig(
        security_level=SecurityLevel.ENTERPRISE,
        authentication=AuthenticationConfig(
            jwt_expire_minutes=15,
            require_2fa=True,
            max_login_attempts=3,
            session_timeout_minutes=60
        ),
        encryption=EncryptionConfig(
            quantum_resistant=True,
            key_rotation_days=30,
            use_hsm=True
        ),
        monitoring=MonitoringConfig(
            log_level="DEBUG",
            real_time_analysis=True,
            alert_threshold_high=5,
            alert_threshold_critical=2,
            retention_days=2555  # 7 years
        ),
        firewall=FirewallConfig(
            rate_limit_per_minute=50,
            ddos_protection_enabled=True,
            bot_protection_enabled=True,
            geo_blocking_enabled=True
        )
    )
}


def get_security_config(level: Optional[SecurityLevel] = None) -> SecurityConfig:
    """Get security configuration for specified level"""    if level is None:
        # Try to load from environment
        try:
            return load_security_config()
        except:
            # Fallback to production default
            level = SecurityLevel.PRODUCTION
    
    return SECURITY_CONFIGS.get(level, SECURITY_CONFIGS[SecurityLevel.PRODUCTION])
