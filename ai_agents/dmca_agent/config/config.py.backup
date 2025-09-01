"""DMCA Agent Configuration - Enterprise Legal Protection System Settings
====================================================================

Comprehensive configuration system for the DMCA Agent with production-ready
settings for legal compliance, automation parameters, and security configurations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission is strictly prohibited and will result in immediate legal action.
"""
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

class EnvironmentType(Enum):
    """Environment types for configuration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "dmca_agent_db"
    username: str = "dmca_user"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    timeout: int = 30
    
    # Redis configuration for caching and queuing
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ssl: bool = False
    
    # MongoDB for document storage
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "dmca_documents"
    mongo_username: Optional[str] = None
    mongo_password: Optional[str] = None
    mongo_auth_source: str = "admin"

@dataclass
class SecurityConfig:
    """Security configuration"""
    # Encryption settings
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_expiry_hours: int = 24
    api_rate_limit: int = 1000  # requests per hour
    
    # Digital signature settings
    signature_algorithm: str = "RSA-SHA256"
    key_size: int = 2048
    certificate_validity_days: int = 365
    
    # Blockchain settings
    blockchain_network: str = "ethereum"
    blockchain_provider_url: str = ""
    smart_contract_address: str = ""
    gas_limit: int = 100000
    gas_price_gwei: int = 20
    
    # IP protection
    allowed_ips: List[str] = field(default_factory=list)
    blocked_ips: List[str] = field(default_factory=list)
    geo_blocking_enabled: bool = False
    blocked_countries: List[str] = field(default_factory=list)

@dataclass
class LegalConfig:
    """Legal compliance configuration"""
    # Default legal framework
    default_framework: str = "dmca_us"
    
    # Supported jurisdictions
    supported_jurisdictions: List[str] = field(default_factory=lambda: [
        "US", "CA", "UK", "EU", "AU", "NZ", "JP", "KR", "SG", "HK", "IN", "BR", "MX", "AR"
    ])
    
    # Legal document settings
    document_retention_days: int = 2555  # 7 years
    automatic_archival: bool = True
    legal_review_required: bool = True
    notarization_required: bool = False
    
    # Compliance thresholds
    minimum_compliance_score: float = 0.75
    high_risk_threshold: float = 0.85
    automatic_processing_threshold: float = 0.90
    
    # Legal notice settings
    notice_response_days: int = 7
    counter_notice_days: int = 14
    escalation_days: int = 21
    
    # Attorney information
    law_firm_name: str = ""
    attorney_name: str = ""
    attorney_email: str = ""
    attorney_phone: str = ""
    bar_registration: str = ""

@dataclass
class TakedownConfig:
    """Takedown automation configuration"""
    # Platform configurations
    platform_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Retry settings
    max_retries: int = 3
    retry_delay_minutes: int = 60
    escalation_delay_hours: int = 24
    
    # Rate limiting
    requests_per_minute: int = 10
    requests_per_hour: int = 100
    requests_per_day: int = 1000
    
    # Success criteria
    success_response_codes: List[int] = field(default_factory=lambda: [200, 201, 202])
    success_keywords: List[str] = field(default_factory=lambda: [
        "received", "processed", "under review", "investigating"
    ])
    
    # Email settings for manual platforms
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    from_email: str = ""
    
    # Web form automation
    browser_headless: bool = True
    page_timeout_seconds: int = 30
    form_fill_delay_ms: int = 100
    screenshot_on_error: bool = True

@dataclass
class CopyrightConfig:
    """Copyright verification configuration"""
    # Verification methods
    enabled_methods: List[str] = field(default_factory=lambda: [
        "blockchain", "digital_signature", "registry_lookup", 
        "timestamp_verification", "metadata_analysis", "hash_comparison"
    ])
    
    # Registry integrations
    copyright_registries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Blockchain verification
    blockchain_confirmations: int = 6
    verification_timeout_minutes: int = 10
    
    # Digital signature validation
    trusted_ca_list: List[str] = field(default_factory=list)
    signature_validation_strict: bool = True
    
    # Metadata verification
    exif_verification: bool = True
    watermark_detection: bool = True
    fingerprint_matching: bool = True
    
    # Scoring weights
    verification_weights: Dict[str, float] = field(default_factory=lambda: {
        "blockchain_proof": 0.30,
        "digital_signature": 0.25,
        "registry_match": 0.25,
        "timestamp_consistency": 0.10,
        "metadata_integrity": 0.10
    })

@dataclass
class DocumentConfig:
    """Document generation configuration"""
    # Template settings
    template_directory: str = "templates"
    custom_template_directory: str = "custom_templates"
    
    # Generation settings
    default_language: str = "en"
    default_format: str = "html"
    generate_pdf: bool = True
    pdf_encryption: bool = True
    
    # Document validation
    spell_check_enabled: bool = True
    grammar_check_enabled: bool = True
    legal_terminology_check: bool = True
    
    # Watermarking and signatures
    watermark_enabled: bool = True
    digital_signature_required: bool = True
    timestamp_documents: bool = True
    
    # Storage settings
    document_storage_path: str = "generated_documents"
    backup_enabled: bool = True
    compression_enabled: bool = True
    
    # Language-specific settings
    language_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "en": {"currency": "USD", "date_format": "%m/%d/%Y", "jurisdiction": "US"},
        "de": {"currency": "EUR", "date_format": "%d.%m.%Y", "jurisdiction": "DE"},
        "fr": {"currency": "EUR", "date_format": "%d/%m/%Y", "jurisdiction": "FR"},
        "es": {"currency": "EUR", "date_format": "%d/%m/%Y", "jurisdiction": "ES"},
        "it": {"currency": "EUR", "date_format": "%d/%m/%Y", "jurisdiction": "IT"}
    })

@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""
    # Metrics collection
    metrics_enabled: bool = True
    metrics_endpoint: str = "/metrics"
    metrics_port: int = 8080
    
    # Health checks
    health_check_interval_minutes: int = 5
    health_check_timeout_seconds: int = 30
    
    # Alerting
    alert_email: str = ""
    alert_webhook: str = ""
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "error_rate": 0.05,
        "response_time_ms": 5000,
        "memory_usage_percent": 80,
        "disk_usage_percent": 85,
        "queue_size": 1000
    })
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "dmca_agent.log"
    log_rotation_size: str = "100MB"
    log_retention_days: int = 30
    
    # Performance monitoring
    performance_sampling_rate: float = 0.1
    slow_query_threshold_ms: int = 1000
    memory_profiling_enabled: bool = False

@dataclass
class DMCAAgentConfig:
    """Complete DMCA Agent configuration"""
    # Environment settings
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    debug_mode: bool = False
    testing_mode: bool = False
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    legal: LegalConfig = field(default_factory=LegalConfig)
    takedown: TakedownConfig = field(default_factory=TakedownConfig)
    copyright: CopyrightConfig = field(default_factory=CopyrightConfig)
    document: DocumentConfig = field(default_factory=DocumentConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Processing settings
    max_concurrent_cases: int = 100
    case_timeout_hours: int = 24
    batch_size: int = 50
    worker_threads: int = 4
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        "batch_processing": True,
        "automated_takedowns": True,
        "blockchain_verification": True,
        "ai_content_analysis": True,
        "multi_language_support": True,
        "advanced_analytics": True,
        "real_time_monitoring": True,
        "audit_trail": True
    })
    
    @classmethod
    def from_environment(cls) -> 'DMCAAgentConfig':
        """
        Create configuration from environment variables
        
        Returns:
            DMCAAgentConfig: Configuration loaded from environment
        """
        config = cls()
        
        # Load environment type
        env_type = os.getenv("DMCA_ENVIRONMENT", "development").lower()
        config.environment = EnvironmentType(env_type)
        config.debug_mode = env_type == "development"
        
        # Database configuration
        config.database.host = os.getenv("DMCA_DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DMCA_DB_PORT", str(config.database.port)))
        config.database.name = os.getenv("DMCA_DB_NAME", config.database.name)
        config.database.username = os.getenv("DMCA_DB_USER", config.database.username)
        config.database.password = os.getenv("DMCA_DB_PASSWORD", config.database.password)
        
        # Redis configuration
        config.database.redis_host = os.getenv("DMCA_REDIS_HOST", config.database.redis_host)
        config.database.redis_port = int(os.getenv("DMCA_REDIS_PORT", str(config.database.redis_port)))
        config.database.redis_password = os.getenv("DMCA_REDIS_PASSWORD")
        
        # Security configuration
        config.security.encryption_key = os.getenv("DMCA_ENCRYPTION_KEY", config.security.encryption_key)
        config.security.jwt_secret = os.getenv("DMCA_JWT_SECRET", config.security.jwt_secret)
        config.security.blockchain_provider_url = os.getenv("DMCA_BLOCKCHAIN_URL", config.security.blockchain_provider_url)
        
        # Legal configuration
        config.legal.law_firm_name = os.getenv("DMCA_LAW_FIRM", config.legal.law_firm_name)
        config.legal.attorney_name = os.getenv("DMCA_ATTORNEY", config.legal.attorney_name)
        config.legal.attorney_email = os.getenv("DMCA_ATTORNEY_EMAIL", config.legal.attorney_email)
        
        # API configuration
        config.api_host = os.getenv("DMCA_API_HOST", config.api_host)
        config.api_port = int(os.getenv("DMCA_API_PORT", str(config.api_port)))
        
        # Feature flags from environment
        for feature in config.features:
            env_var = f"DMCA_FEATURE_{feature.upper()}"
            if env_var in os.environ:
                config.features[feature] = os.getenv(env_var, "true").lower() == "true"
        
        return config
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> 'DMCAAgentConfig':
        """
        Load configuration from JSON file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            DMCAAgentConfig: Loaded configuration
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def to_file(self, config_file: Union[str, Path]) -> None:
        """
        Save configuration to JSON file
        
        Args:
            config_file: Path to save configuration
        """
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary, handling enums and dataclasses
        config_dict = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Enum):
                config_dict[field_name] = field_value.value
            elif hasattr(field_value, '__dict__'):
                # Handle nested dataclasses
                nested_dict = {}
                for nested_field, nested_value in field_value.__dict__.items():
                    if isinstance(nested_value, Enum):
                        nested_dict[nested_field] = nested_value.value
                    else:
                        nested_dict[nested_field] = nested_value
                config_dict[field_name] = nested_dict
            else:
                config_dict[field_name] = field_value
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of issues
        
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Validate required security settings for production
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.security.encryption_key:
                errors.append("Encryption key is required for production")
            if not self.security.jwt_secret:
                errors.append("JWT secret is required for production")
            if self.debug_mode:
                errors.append("Debug mode should be disabled in production")
        
        # Validate database settings
        if not self.database.password and self.environment != EnvironmentType.DEVELOPMENT:
            errors.append("Database password is required for non-development environments")
        
        # Validate legal settings
        if self.legal.automatic_processing_threshold <= self.legal.minimum_compliance_score:
            errors.append("Automatic processing threshold must be higher than minimum compliance score")
        
        # Validate takedown settings
        if self.takedown.max_retries < 1:
            errors.append("Maximum retries must be at least 1")
        
        # Validate copyright verification weights
        weight_sum = sum(self.copyright.verification_weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            errors.append(f"Verification weights must sum to 1.0 (current: {weight_sum})")
        
        return errors
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get configuration for a specific platform
        
        Args:
            platform: Platform name
            
        Returns:
            Dict containing platform-specific configuration
        """
        return self.takedown.platform_configs.get(platform, {})
    
    def update_platform_config(self, platform: str, config: Dict[str, Any]) -> None:
        """
        Update configuration for a specific platform
        
        Args:
            platform: Platform name
            config: Platform configuration
        """
        self.takedown.platform_configs[platform] = config

# Global configuration instance
_global_config: Optional[DMCAAgentConfig] = None

def get_config() -> DMCAAgentConfig:
    """
    Get global DMCA Agent configuration
    
    Returns:
        DMCAAgentConfig: Current configuration
    """
    global _global_config
    if _global_config is None:
        _global_config = DMCAAgentConfig.from_environment()
    return _global_config

def set_config(config: DMCAAgentConfig) -> None:
    """
    Set global DMCA Agent configuration
    
    Args:
        config: Configuration to set as global
    """
    global _global_config
    _global_config = config

def reload_config(config_file: Optional[Union[str, Path]] = None) -> DMCAAgentConfig:
    """
    Reload configuration from environment or file
    
    Args:
        config_file: Optional configuration file path
        
    Returns:
        DMCAAgentConfig: Reloaded configuration
    """
    global _global_config
    if config_file:
        _global_config = DMCAAgentConfig.from_file(config_file)
    else:
        _global_config = DMCAAgentConfig.from_environment()
    return _global_config

# Default platform configurations
DEFAULT_PLATFORM_CONFIGS = {
    "youtube": {
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "auth_method": "oauth2",
        "rate_limit": 100,
        "takedown_form_url": "https://www.youtube.com/copyright_complaint_form",
        "response_time_hours": 24,
        "success_indicators": ["Content removed", "Under review"]
    },
    "tiktok": {
        "api_endpoint": "https://open-api.tiktok.com/platform/v1",
        "auth_method": "api_key",
        "rate_limit": 50,
        "takedown_form_url": "https://www.tiktok.com/legal/copyright",
        "response_time_hours": 48,
        "success_indicators": ["Report received", "Investigation started"]
    },
    "instagram": {
        "api_endpoint": "https://graph.facebook.com/v13.0",
        "auth_method": "oauth2",
        "rate_limit": 200,
        "takedown_form_url": "https://help.instagram.com/contact/372592039493026",
        "response_time_hours": 24,
        "success_indicators": ["Report submitted", "Content under review"]
    },
    "facebook": {
        "api_endpoint": "https://graph.facebook.com/v13.0",
        "auth_method": "oauth2",
        "rate_limit": 200,
        "takedown_form_url": "https://www.facebook.com/help/contact/634636770043106",
        "response_time_hours": 24,
        "success_indicators": ["Report received", "Under investigation"]
    },
    "twitter": {
        "api_endpoint": "https://api.twitter.com/2",
        "auth_method": "oauth2",
        "rate_limit": 300,
        "takedown_form_url": "https://help.twitter.com/forms/dmca",
        "response_time_hours": 12,
        "success_indicators": ["Report submitted successfully", "Under review"]
    },
    "twitch": {
        "api_endpoint": "https://api.twitch.tv/helix",
        "auth_method": "oauth2",
        "rate_limit": 800,
        "takedown_form_url": "https://www.twitch.tv/p/legal/dmca-guidelines",
        "response_time_hours": 48,
        "success_indicators": ["DMCA notice received", "Content flagged"]
    }
}

# Initialize default platform configurations
def initialize_default_configs():
    """Initialize default platform configurations"""
    config = get_config()
    for platform, platform_config in DEFAULT_PLATFORM_CONFIGS.items():
        if platform not in config.takedown.platform_configs:
            config.update_platform_config(platform, platform_config)
