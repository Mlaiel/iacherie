"""{{config_name}} Configuration Template for Ainflue Platform
{{config_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseSettings, Field, validator, root_validator
from pydantic.env_settings import SettingsSourceCallable
import yaml
import json
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment types"""
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


class DatabaseDriver(Enum):
    """Database drivers"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"


class CacheBackend(Enum):
    """Cache backends"""
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"
    DISK = "disk"


class {{config_name}}Config(BaseSettings):
    """{{config_description}}
    
    Comprehensive configuration management providing:
    - Environment-specific settings
    - Type validation and conversion
    - Secure secret management
    - Database configuration
    - Cache and queue settings
    - External service integration
    - Monitoring and logging setup
    - Feature flags and toggles
    - Performance tuning parameters
    - Security configuration
    """
    
    # ============================================================================
    # APPLICATION SETTINGS
    # ============================================================================
    
    # Basic application info
    app_name: str = Field(default="Ainflue Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS settings
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    allowed_methods: List[str] = Field(default=["*"], env="ALLOWED_METHODS")
    allowed_headers: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # ============================================================================
    # DATABASE SETTINGS
    # ============================================================================
    
    # Primary database
    database_driver: DatabaseDriver = Field(default=DatabaseDriver.POSTGRESQL, env="DATABASE_DRIVER")
    database_host: str = Field(default="localhost", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_name: str = Field(default="ainflue", env="DATABASE_NAME")
    database_user: str = Field(default="postgres", env="DATABASE_USER")
    database_password: str = Field("", env="DATABASE_PASSWORD")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Read replica database (optional)
    read_database_host: Optional[str] = Field(default=None, env="READ_DATABASE_HOST")
    read_database_port: Optional[int] = Field(default=None, env="READ_DATABASE_PORT")
    read_database_name: Optional[str] = Field(default=None, env="READ_DATABASE_NAME")
    read_database_user: Optional[str] = Field(default=None, env="READ_DATABASE_USER")
    read_database_password: Optional[str] = Field(default=None, env="READ_DATABASE_PASSWORD")
    
    # ============================================================================
    # CACHE & QUEUE SETTINGS
    # ============================================================================
    
    # Redis configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    
    # Cache settings
    cache_backend: CacheBackend = Field(default=CacheBackend.REDIS, env="CACHE_BACKEND")
    cache_ttl: int = Field(default=300, env="CACHE_TTL")
    cache_key_prefix: str = Field(default="ainflue", env="CACHE_KEY_PREFIX")
    
    # Message queue settings
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    
    # ============================================================================
    # EXTERNAL SERVICES
    # ============================================================================
    
    # AI Services
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_ai_api_key: Optional[str] = Field(default=None, env="GOOGLE_AI_API_KEY")
    
    # Cloud Storage
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Email service
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # Social media APIs
    twitter_api_key: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, env="TWITTER_API_SECRET")
    instagram_api_key: Optional[str] = Field(default=None, env="INSTAGRAM_API_KEY")
    youtube_api_key: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    
    # ============================================================================
    # MONITORING & LOGGING
    # ============================================================================
    
    # Logging configuration
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_max_size: int = Field(default=100, env="LOG_MAX_SIZE")  # MB
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Metrics and monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    prometheus_pushgateway_url: Optional[str] = Field(default=None, env="PROMETHEUS_PUSHGATEWAY_URL")
    
    # Sentry error tracking
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: Optional[str] = Field(default=None, env="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.1, env="SENTRY_TRACES_SAMPLE_RATE")
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Feature toggles
    enable_registration: bool = Field(default=True, env="ENABLE_REGISTRATION")
    enable_social_login: bool = Field(default=True, env="ENABLE_SOCIAL_LOGIN")
    enable_ai_features: bool = Field(default=True, env="ENABLE_AI_FEATURES")
    enable_content_moderation: bool = Field(default=True, env="ENABLE_CONTENT_MODERATION")
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    enable_notifications: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    
    # Rate limiting
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    rate_limit_requests_per_minute: int = Field(default=100, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_burst_size: int = Field(default=20, env="RATE_LIMIT_BURST_SIZE")
    
    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    
    # Request handling
    max_request_size: int = Field(default=100, env="MAX_REQUEST_SIZE")  # MB
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")  # seconds
    keep_alive_timeout: int = Field(default=5, env="KEEP_ALIVE_TIMEOUT")  # seconds
    
    # Background tasks
    max_background_tasks: int = Field(default=10, env="MAX_BACKGROUND_TASKS")
    task_queue_max_size: int = Field(default=1000, env="TASK_QUEUE_MAX_SIZE")
    
    # File uploads
    max_upload_size: int = Field(default=50, env="MAX_UPLOAD_SIZE")  # MB
    allowed_file_types: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "mp4", "mp3", "wav", "pdf"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # ============================================================================
    # VALIDATION & COMPUTED PROPERTIES
    # ============================================================================
    
    @validator('secret_key', 'jwt_secret_key')
    def validate_secret_keys(cls, v):
        if len(v) < 32:
            raise ValueError('Secret keys must be at least 32 characters long')
        return v
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @validator('database_pool_size', 'database_max_overflow')
    def validate_positive_integers(cls, v):
        if v <= 0:
            raise ValueError('Value must be positive')
        return v
    
    @validator('allowed_origins', 'allowed_methods', 'allowed_headers', 'allowed_file_types', pre=True)
    def validate_string_lists(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    @root_validator
    def validate_environment_consistency(cls, values):
        environment = values.get('environment')
        debug = values.get('debug')
        
        # Ensure production environment has debug disabled
        if environment == Environment.PRODUCTION and debug:
            raise ValueError('Debug mode cannot be enabled in production environment')
        
        # Ensure required secrets in production
        if environment == Environment.PRODUCTION:
            required_secrets = ['secret_key', 'jwt_secret_key', 'database_password']
            for secret in required_secrets:
                if not values.get(secret):
                    raise ValueError(f'{secret} is required in production environment')
        
        return values
    
    # ============================================================================
    # COMPUTED PROPERTIES
    # ============================================================================
    
    @property
    def database_url(self) -> str:
        """Generate database URL from components"""
        if self.database_driver == DatabaseDriver.SQLITE:
            return f"sqlite:///{self.database_name}.db"
        elif self.database_driver == DatabaseDriver.POSTGRESQL:
            return (f"postgresql://{self.database_user}:{self.database_password}"
                   f"@{self.database_host}:{self.database_port}/{self.database_name}")
        elif self.database_driver == DatabaseDriver.MYSQL:
            return (f"mysql://{self.database_user}:{self.database_password}"
                   f"@{self.database_host}:{self.database_port}/{self.database_name}")
        elif self.database_driver == DatabaseDriver.MONGODB:
            auth = f"{self.database_user}:{self.database_password}@" if self.database_user else ""
            return f"mongodb://{auth}{self.database_host}:{self.database_port}/{self.database_name}"
        else:
            raise ValueError(f"Unsupported database driver: {self.database_driver}")
    
    @property
    def async_database_url(self) -> str:
        """Generate async database URL"""
        if self.database_driver == DatabaseDriver.SQLITE:
            return f"sqlite+aiosqlite:///{self.database_name}.db"
        elif self.database_driver == DatabaseDriver.POSTGRESQL:
            return (f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
                   f"@{self.database_host}:{self.database_port}/{self.database_name}")
        else:
            # Fallback to sync URL
            return self.database_url
    
    @property
    def redis_url(self) -> str:
        """Generate Redis URL"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.environment == Environment.TESTING
    
    # ============================================================================
    # CONFIGURATION SOURCES
    # ============================================================================
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """Customize configuration sources priority"""
            return (
                init_settings,  # Arguments passed to constructor
                yaml_settings,  # Custom YAML file loader
                env_settings,   # Environment variables
                file_secret_settings,  # Docker secrets
            )


def yaml_settings(settings: BaseSettings) -> Dict[str, Any]:
    """Load settings from YAML file"""
    yaml_file = os.getenv("CONFIG_FILE", "config.yaml")
    
    if os.path.exists(yaml_file):
        try:
            with open(yaml_file, 'r') as f:
                config_data = yaml.safe_load(f)
                return config_data or {}
        except Exception as e:
            logger.warning(f"Failed to load YAML config from {yaml_file}: {e}")
    
    return {}


# ============================================================================
# CONFIGURATION FACTORY
# ============================================================================

_config_instance: Optional[{{config_name}}Config] = None


def get_settings() -> {{config_name}}Config:
    """Get application settings (singleton pattern)"""
    global _config_instance
    
    if _config_instance is None:
        # Load .env file
        load_dotenv()
        
        # Create configuration instance
        _config_instance = {{config_name}}Config()
        
        # Setup logging based on configuration
        setup_logging(_config_instance)
        
        logger.info(f"Configuration loaded for environment: {_config_instance.environment.value}")
    
    return _config_instance


def reload_settings() -> {{config_name}}Config:
    """Reload settings (useful for testing)"""
    global _config_instance
    _config_instance = None
    return get_settings()


def setup_logging(config: {{config_name}}Config):
    """Setup logging based on configuration"""
    import logging.handlers
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level.value),
        format=config.log_format,
        handlers=[]
    )
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.log_format))
    logging.getLogger().addHandler(console_handler)
    
    # Add file handler if specified
    if config.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            config.log_file,
            maxBytes=config.log_max_size * 1024 * 1024,  # Convert MB to bytes
            backupCount=config.log_backup_count
        )
        file_handler.setFormatter(logging.Formatter(config.log_format))
        logging.getLogger().addHandler(file_handler)


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_configuration(config: {{config_name}}Config) -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []
    
    # Check database connectivity (mock validation)
    if config.database_driver == DatabaseDriver.POSTGRESQL:
        if not config.database_password and config.is_production:
            issues.append("Database password is required in production")
    
    # Check required external services
    if config.enable_ai_features:
        if not any([config.openai_api_key, config.anthropic_api_key, config.google_ai_api_key]):
            issues.append("At least one AI service API key is required when AI features are enabled")
    
    # Check email configuration
    if config.enable_notifications:
        if not all([config.smtp_host, config.smtp_username, config.smtp_password]):
            issues.append("SMTP configuration is incomplete for notifications")
    
    # Check production readiness
    if config.is_production:
        if config.debug:
            issues.append("Debug mode should not be enabled in production")
        
        if not config.sentry_dsn:
            issues.append("Sentry DSN is recommended for production error tracking")
    
    return issues


# ============================================================================
# CONFIGURATION EXPORT
# ============================================================================

def export_config_template(file_path: str = "config.template.yaml"):
    """Export configuration template file"""
    config = {{config_name}}Config()
    
    # Create template with comments
    template_data = {
        "# Application Settings": None,
        "app_name": config.app_name,
        "app_version": config.app_version,
        "environment": config.environment.value,
        "debug": config.debug,
        
        "# Server Configuration": None,
        "host": config.host,
        "port": config.port,
        "workers": config.workers,
        
        "# Database Settings": None,
        "database_driver": config.database_driver.value,
        "database_host": config.database_host,
        "database_port": config.database_port,
        "database_name": config.database_name,
        "database_user": config.database_user,
        
        "# Cache Settings": None,
        "redis_host": config.redis_host,
        "redis_port": config.redis_port,
        "cache_ttl": config.cache_ttl,
        
        "# Feature Flags": None,
        "enable_ai_features": config.enable_ai_features,
        "enable_content_moderation": config.enable_content_moderation,
        "enable_analytics": config.enable_analytics,
    }
    
    with open(file_path, 'w') as f:
        yaml.dump(template_data, f, default_flow_style=False, indent=2)
    
    logger.info(f"Configuration template exported to {file_path}")


if __name__ == "__main__":
    # Example usage
    config = get_settings()
    
    print(f"Application: {config.app_name} v{config.app_version}")
    print(f"Environment: {config.environment.value}")
    print(f"Database URL: {config.database_url}")
    print(f"Redis URL: {config.redis_url}")
    
    # Validate configuration
    issues = validate_configuration(config)
    if issues:
        print("\nConfiguration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nConfiguration is valid!")
    
    # Export template
    export_config_template()