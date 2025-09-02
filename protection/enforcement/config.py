"""Configuration and Settings for Copyright Enforcement Module
Professional configuration management with environment support
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
import json
from pathlib import Path

from pydantic import BaseSettings, Field, validator


logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """
Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PlatformType(Enum):
    """Supported platform types"""

    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    DEEZER = "deezer"
    APPLE_MUSIC = "apple_music"
    AMAZON_MUSIC = "amazon_music"
    PODCAST_PLATFORMS = "podcast_platforms"
    GENERIC = "generic"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "ia_influencer_agent"
    username: str = "postgres"
    password: str = ""
    
    # Connection pool settings
    min_connections: int = 5
    max_connections: int = 20
    connection_timeout: int = 30
    
    # Performance settings
    query_timeout: int = 60
    statement_timeout: int = 300
    
    # SSL settings
    ssl_mode: str = "prefer"
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    
    @property
    def connection_string(self) -> str:
        try:
            logger.info(f"Executing connection_string")
            
            # Implementation for connection_string
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"connection_string completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"connection_string failed: {e}")
            raise
@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    
    # Connection settings
    connection_timeout: int = 5
    socket_timeout: int = 5
    max_connections: int = 50
    
    # Key prefixes
    cache_prefix: str = "ia_agent:cache:"
    queue_prefix: str = "ia_agent:queue:"
    lock_prefix: str = "ia_agent:lock:"
    
    # Cache settings
    default_ttl: int = 3600  # 1 hour
    max_memory_policy: str = "allkeys-lru"


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration"""
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Index settings
    index_prefix: str = "ia_agent"
    shards: int = 1
    replicas: int = 0
    
    # Connection settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 1
    
    # Security
    use_ssl: bool = False
    verify_certs: bool = True
    ca_certs_path: Optional[str] = None


@dataclass
class AIServiceConfig:
    """AI service configuration"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    
    # Model settings
    default_model: str = "gpt-4-turbo-preview"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # Content analysis
    content_analysis_threshold: float = 0.85
    similarity_threshold: float = 0.90
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_day: int = 1000
    
    # Timeout settings
    request_timeout: int = 60
    max_retries: int = 3


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    platform_type: PlatformType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    
    # Enforcement settings
    auto_takedown_enabled: bool = True
    escalation_delay_hours: int = 24
    max_retries: int = 3
    
    # Content detection
    content_matching_threshold: float = 0.85
    fingerprint_enabled: bool = True
    metadata_matching: bool = True
    
    # Notification settings
    webhook_url: Optional[str] = None
    notification_email: Optional[str] = None


@dataclass
class NotificationConfig:
    """
Notification system configuration"""
    # Email settings
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    from_email: str = "noreply@ia-influencer-agent.com"
    
    # Webhook settings
    webhook_timeout: int = 30
    webhook_retries: int = 3
    webhook_retry_delay: int = 5
    
    # Slack settings
    slack_webhook_url: Optional[str] = None
    slack_channel: str = "#copyright-alerts"
    slack_username: str = "IA Influencer Agent"
    
    # SMS settings (Twilio)
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None
    
    # Rate limiting
    max_notifications_per_hour: int = 100
    max_notifications_per_day: int = 1000


@dataclass
class SecurityConfig:
    """Security configuration"""
    # API Security
    api_key_header: str = "X-API-Key"
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Rate limiting
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour
    
    # CORS settings
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Encryption
    encryption_key: Optional[str] = None
    hash_algorithm: str = "sha256"
    
    # SSL/TLS
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    # Security headers
    enable_security_headers: bool = True
    hsts_max_age: int = 31536000  # 1 year


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    # Metrics
    metrics_enabled: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    
    # Health checks
    health_check_enabled: bool = True
    health_check_interval: int = 60
    
    # Performance monitoring
    performance_monitoring: bool = True
    slow_query_threshold: int = 1000  # milliseconds
    memory_threshold_mb: int = 512
    
    # Alerting
    alerting_enabled: bool = True
    alert_webhooks: List[str] = field(default_factory=list)
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file_path: Optional[str] = None
    log_max_size_mb: int = 100
    log_backup_count: int = 5


@dataclass
class StorageConfig:
    """Storage configuration"""
    # Local storage
    base_storage_path: str = "/data/ia-influencer-agent"
    evidence_storage_path: str = "/data/evidence"
    reports_storage_path: str = "/data/reports"
    temp_storage_path: str = "/tmp/ia-agent"
    
    # Cloud storage (AWS S3)
    s3_bucket: Optional[str] = None
    s3_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Azure Blob Storage
    azure_account_name: Optional[str] = None
    azure_account_key: Optional[str] = None
    azure_container: Optional[str] = None
    
    # Google Cloud Storage
    gcs_bucket: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    
    # File retention
    evidence_retention_days: int = 365
    report_retention_days: int = 180
    temp_file_retention_hours: int = 24


@dataclass
class LegalConfig:
    """Legal document configuration"""
    # Document templates
    templates_path: str = "/templates/legal"
    output_path: str = "/documents/legal"
    
    # Default settings
    default_jurisdiction: str = "US"
    default_law_firm: str = "Your Legal Firm"
    default_attorney: str = "Attorney Name"
    
    # DMCA settings
    dmca_agent_name: str = "DMCA Agent"
    dmca_agent_email: str = "dmca@your-company.com"
    dmca_agent_address: str = "123 Legal St, City, State 12345"
    
    # Copyright notice
    copyright_holder: str = "IA Influencer Agent Platform"
    copyright_year: int = 2024
    
    # Document formatting
    document_font: str = "Arial"
    document_font_size: int = 12
    line_spacing: float = 1.5
    margin_inches: float = 1.0


class EnforcementSettings(BaseSettings):
    """Main settings class for copyright enforcement module"""
    
    # Environment
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Application
    app_name: str = Field(default="IA Influencer Agent - Copyright Enforcement", env="APP_NAME")
    app_version: str = Field(default="2.0.0", env="APP_VERSION")
    app_description: str = Field(default="Professional copyright enforcement and protection system", env="APP_DESCRIPTION")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    elasticsearch: ElasticsearchConfig = Field(default_factory=ElasticsearchConfig)
    
    # AI Services
    ai_service: AIServiceConfig = Field(default_factory=AIServiceConfig)
    
    # Platform configurations
    platforms: Dict[str, PlatformConfig] = Field(default_factory=dict)
    
    # Notifications
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    
    # Security
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Monitoring
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # Storage
    storage: StorageConfig = Field(default_factory=StorageConfig)
    
    # Legal
    legal: LegalConfig = Field(default_factory=LegalConfig)
    
    # Business logic settings
    auto_enforcement_enabled: bool = Field(default=True, env="AUTO_ENFORCEMENT_ENABLED")
    manual_review_required: bool = Field(default=False, env="MANUAL_REVIEW_REQUIRED")
    escalation_enabled: bool = Field(default=True, env="ESCALATION_ENABLED")
    
    # Content matching
    content_matching_enabled: bool = Field(default=True, env="CONTENT_MATCHING_ENABLED")
    fingerprinting_enabled: bool = Field(default=True, env="FINGERPRINTING_ENABLED")
    ai_analysis_enabled: bool = Field(default=True, env="AI_ANALYSIS_ENABLED")
    
    # Performance settings
    max_concurrent_cases: int = Field(default=100, env="MAX_CONCURRENT_CASES")
    batch_processing_size: int = Field(default=50, env="BATCH_PROCESSING_SIZE")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # External integrations
    blockchain_timestamping: bool = Field(default=False, env="BLOCKCHAIN_TIMESTAMPING")
    legal_service_integration: bool = Field(default=False, env="LEGAL_SERVICE_INTEGRATION")
    payment_processing: bool = Field(default=False, env="PAYMENT_PROCESSING")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        use_enum_values = True
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment setting"""
        if isinstance(v, str):
            try:
                return EnvironmentType(v.lower())
            except ValueError:
                return EnvironmentType.DEVELOPMENT
        return v
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """
Validate platform configurations"""
        if not v:
            # Initialize with default platform configs
            default_platforms = {}
            for platform in PlatformType:
                default_platforms[platform.value] = PlatformConfig(platform_type=platform)
            return default_platforms
        return v
    
    @validator('security')
    def validate_security(cls, v, values):
        """
Validate security configuration"""
        if values.get('environment') == EnvironmentType.PRODUCTION:
            if v.jwt_secret_key == "your-secret-key-change-in-production":
                raise ValueError("JWT secret key must be changed in production")
        return v
    
    def get_platform_config(self, platform_type: PlatformType) -> Optional[PlatformConfig]:
        """Get configuration for specific platform"""
        return self.platforms.get(platform_type.value)
    
    def update_platform_config(self, platform_type: PlatformType, config: PlatformConfig):
        """
Update configuration for specific platform"""
        self.platforms[platform_type.value] = config
    
    def is_production(self) -> bool:
        """
Check if running in production environment"""
        return self.environment == EnvironmentType.PRODUCTION
    
    def is_development(self) -> bool:
        """
Check if running in development environment"""
        return self.environment == EnvironmentType.DEVELOPMENT
    
    def get_log_level(self) -> str:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_redis_url_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_redis_url failed: {e}")
                    return {"status": "error", "message": str(e)}
    def get_database_url(self) -> str:
        """
Get database connection URL"""
        return self.database.connection_string
    
    def get_redis_url(self) -> str:
        """
Get Redis connection URL"""
        auth_part = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth_part}{self.redis.host}:{self.redis.port}/{self.redis.database}"
    
    def get_storage_paths(self) -> Dict[str, str]:
        """Get all storage paths"""
        return {
            'base': self.storage.base_storage_path,
            'evidence': self.storage.evidence_storage_path,
            'reports': self.storage.reports_storage_path,
            'temp': self.storage.temp_storage_path,
            'legal_templates': self.legal.templates_path,
            'legal_output': self.legal.output_path
        }
    
    def ensure_directories(self):
        """
Ensure all required directories exist"""
        paths = self.get_storage_paths()
        for path_name, path in paths.items():
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {path}")
            except Exception as e:
                logger.error(f"Failed to create directory {path}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'environment': self.environment.value,
            'debug': self.debug,
            'app_name': self.app_name,
            'app_version': self.app_version,
            'host': self.host,
            'port': self.port,
            'workers': self.workers,
            'auto_enforcement_enabled': self.auto_enforcement_enabled,
            'manual_review_required': self.manual_review_required,
            'escalation_enabled': self.escalation_enabled,
            'content_matching_enabled': self.content_matching_enabled,
            'fingerprinting_enabled': self.fingerprinting_enabled,
            'ai_analysis_enabled': self.ai_analysis_enabled,
            'max_concurrent_cases': self.max_concurrent_cases,
            'batch_processing_size': self.batch_processing_size,
            'cache_ttl_seconds': self.cache_ttl_seconds,
            'blockchain_timestamping': self.blockchain_timestamping,
            'legal_service_integration': self.legal_service_integration,
            'payment_processing': self.payment_processing
        }
    
    @classmethod
    def from_file(cls, config_path: str) -> 'EnforcementSettings':
        """
Load settings from configuration file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Override environment variables with file values
            for key, value in config_data.items():
                if hasattr(cls, key):
                    os.environ[key.upper()] = str(value)
            
            return cls()
            
        except Exception as e:
            logger.error(f"Error loading config from file {config_path}: {e}")
            return cls()
    
    def save_to_file(self, config_path: str):
        """Save current settings to configuration file"""
        try:
            config_data = self.to_dict()
            
            # Ensure directory exists
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config to file {config_path}: {e}")


# Global settings instance
settings = EnforcementSettings()


def get_settings() -> EnforcementSettings:
    """Get the global settings instance"""
    return settings


def reload_settings():
    """
Reload settings from environment"""
    global settings
    settings = EnforcementSettings()
    return settings


def configure_logging():
    """
Configure logging based on settings"""
    try:
        log_config = {
            'level': getattr(logging, settings.get_log_level()),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
        
        if settings.monitoring.log_format == "json":
            log_config['format'] = '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        
        if settings.monitoring.log_file_path:
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                settings.monitoring.log_file_path,
                maxBytes=settings.monitoring.log_max_size_mb * 1024 * 1024,
                backupCount=settings.monitoring.log_backup_count
            )
            logging.basicConfig(
                level=log_config['level'],
                format=log_config['format'],
                handlers=[handler, logging.StreamHandler()]
            )
        else:
            logging.basicConfig(**log_config)
        
        logger.info(f"Logging configured for {settings.environment.value} environment")
        
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logger.error(f"Error configuring logging: {e}")


# Initialize logging on import
configure_logging()


__all__ = [
    'EnforcementSettings',
    'DatabaseConfig',
    'RedisConfig',
    'ElasticsearchConfig',
    'AIServiceConfig',
    'PlatformConfig',
    'NotificationConfig',
    'SecurityConfig',
    'MonitoringConfig',
    'StorageConfig',
    'LegalConfig',
    'EnvironmentType',
    'LogLevel',
    'PlatformType',
    'settings',
    'get_settings',
    'reload_settings',
    'configure_logging'
]
