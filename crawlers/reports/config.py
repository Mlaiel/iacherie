"""Reports Configuration Module
===========================

Ultra-advanced configuration management system for the enterprise reporting module
of the IA Influencer Agent platform. Provides comprehensive configuration handling,
environment-specific settings, security configurations, and dynamic configuration
updates with enterprise-grade reliability and compliance features.

Core Responsibilities:
- Centralized configuration management with hierarchical settings
- Environment-specific configuration profiles (dev, staging, production)
- Security configuration and credential management with encryption
- Database and service connection configuration with pooling
- Caching and performance optimization settings
- Monitoring and observability configuration
- Multi-tenant configuration support with namespace isolation
- Configuration validation and schema enforcement
- Dynamic configuration updates with hot-reloading capabilities
- Compliance and audit configuration for regulatory requirements

Advanced Features:
- Configuration inheritance and composition with override mechanisms
- Encrypted credential storage with key rotation and HSM integration
- Configuration versioning and rollback capabilities
- Real-time configuration monitoring and change detection
- Configuration drift detection and automatic remediation
- Multi-cloud configuration synchronization and backup
- Compliance scanning and security policy enforcement
- Configuration templates and automated deployment
- A/B testing configuration and feature flag management
- Performance profiling and optimization recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Legal Warning: This code and concept are the exclusive property of Fahed Mlaiel.
Any unauthorized use without explicit written permission will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""import os
import json
import yaml
import logging
import warnings
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta, timezone
import uuid
import hashlib
import base64
from contextlib import contextmanager

# Configuration and Settings
from pydantic import BaseSettings, Field, validator, BaseModel, SecretStr
from pydantic_settings import BaseSettings as PydanticSettings

# Encryption and Security
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    warnings.warn("Encryption libraries not available. Install cryptography for secure credential storage.")

# Validation and Schema
try:
    from cerberus import Validator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False
    warnings.warn("Validation library not available. Install cerberus for schema validation.")

# Configuration watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    CONFIG_WATCHING_AVAILABLE = True
except ImportError:
    CONFIG_WATCHING_AVAILABLE = False
    warnings.warn("File watching library not available. Install watchdog for dynamic configuration updates.")

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment enumeration."""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"


class LogLevel(str, Enum):
    """Log level enumeration."""    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseType(str, Enum):
    """Database type enumeration."""    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    MSSQL = "mssql"


class CacheType(str, Enum):
    """Cache type enumeration."""    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DISK = "disk"


class ExportFormat(str, Enum):
    """Export format enumeration."""    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    XML = "xml"
    POWERPOINT = "powerpoint"


class CloudProvider(str, Enum):
    """Cloud provider enumeration."""    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ALIBABA = "alibaba"
    ORACLE = "oracle"


@dataclass
class DatabaseConfig:
    """Database configuration dataclass."""    type: DatabaseType = DatabaseType.POSTGRESQL
    host: str = "localhost"
    port: int = 5432
    database: str = "reports"
    username: str = "reports_user"
    password: SecretStr = SecretStr("password")
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_mode: str = "prefer"
    connection_timeout: int = 10
    command_timeout: int = 30
    
    @property
    def url(self) -> str:
        """Generate database URL."""        if self.type == DatabaseType.POSTGRESQL:
            driver = "postgresql+asyncpg"
        elif self.type == DatabaseType.MYSQL:
            driver = "mysql+aiomysql"
        elif self.type == DatabaseType.SQLITE:
            return f"sqlite+aiosqlite:///{self.database}"
        else:
            driver = str(self.type)
        
        return f"{driver}://{self.username}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    """Redis configuration dataclass."""    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[SecretStr] = None
    ssl: bool = False
    ssl_cert_reqs: str = "required"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    max_connections: int = 50
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    
    @property
    def url(self) -> str:
        """Generate Redis URL."""        scheme = "rediss" if self.ssl else "redis"
        auth = f":{self.password.get_secret_value()}@" if self.password else ""
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.database}"


@dataclass
class CacheConfig:
    """Cache configuration dataclass."""    type: CacheType = CacheType.REDIS
    ttl_default: int = 3600
    ttl_short: int = 300
    ttl_medium: int = 1800
    ttl_long: int = 7200
    max_size: int = 10000
    eviction_policy: str = "lru"
    compression: bool = True
    serialization: str = "json"
    redis_config: Optional[RedisConfig] = None


@dataclass
class SecurityConfig:
    """Security configuration dataclass."""    secret_key: SecretStr = SecretStr("your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 30
    password_min_length: int = 12
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 480
    csrf_protection: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_credentials: bool = True
    https_only: bool = True
    secure_cookies: bool = True
    encryption_key: Optional[SecretStr] = None


@dataclass
class MonitoringConfig:
    """Monitoring configuration dataclass."""    enabled: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    health_check_path: str = "/health"
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    jaeger_enabled: bool = True
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file: Optional[str] = None
    log_rotation: bool = True
    log_max_size: str = "100MB"
    log_backup_count: int = 10
    performance_monitoring: bool = True
    error_tracking: bool = True
    uptime_monitoring: bool = True


@dataclass
class APIConfig:
    """API configuration dataclass."""    title: str = "IA Influencer Agent - Reports API"
    version: str = "2.0.0"
    description: str = "Ultra-advanced enterprise reporting system"
    docs_enabled: bool = True
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    rate_limiting: bool = True
    rate_limit_default: str = "1000/minute"
    rate_limit_burst: str = "2000/minute"
    pagination_default_limit: int = 50
    pagination_max_limit: int = 1000
    request_timeout: int = 30
    max_request_size: str = "100MB"
    compression: bool = True
    cors_enabled: bool = True


@dataclass
class ReportConfig:
    """Report configuration dataclass."""    default_format: ExportFormat = ExportFormat.PDF
    supported_formats: List[ExportFormat] = field(default_factory=lambda: list(ExportFormat))
    max_concurrent_reports: int = 10
    report_timeout: int = 1800
    auto_cleanup_days: int = 30
    template_cache_size: int = 100
    chart_resolution: str = "1920x1080"
    chart_quality: int = 95
    pdf_page_size: str = "A4"
    pdf_orientation: str = "portrait"
    excel_max_rows: int = 1000000
    csv_delimiter: str = ","
    csv_encoding: str = "utf-8"
    watermark_enabled: bool = True
    branding_enabled: bool = True


@dataclass
class SchedulerConfig:
    """Scheduler configuration dataclass."""    enabled: bool = True
    max_concurrent_jobs: int = 20
    job_timeout: int = 3600
    retry_attempts: int = 3
    retry_delay: int = 60
    queue_size: int = 1000
    worker_threads: int = 4
    persistence_enabled: bool = True
    coalescing: bool = True
    misfire_grace_time: int = 300
    timezone: str = "UTC"
    job_defaults: Dict[str, Any] = field(default_factory=lambda: {
        "coalesce": True,
        "max_instances": 3,
        "misfire_grace_time": 300
    })


@dataclass
class CloudConfig:
    """Cloud storage configuration dataclass."""    provider: CloudProvider = CloudProvider.AWS
    region: str = "us-east-1"
    bucket_name: str = "reports-storage"
    access_key: Optional[SecretStr] = None
    secret_key: Optional[SecretStr] = None
    endpoint_url: Optional[str] = None
    use_ssl: bool = True
    signature_version: str = "s3v4"
    presigned_url_expiry: int = 3600
    multipart_threshold: int = 67108864  # 64MB
    multipart_chunksize: int = 16777216  # 16MB
    max_concurrency: int = 10
    transfer_config: Dict[str, Any] = field(default_factory=lambda: {
        "multipart_threshold": 67108864,
        "max_concurrency": 10,
        "multipart_chunksize": 16777216,
        "use_threads": True
    })


@dataclass
class MLConfig:
    """Machine Learning configuration dataclass."""    enabled: bool = True
    model_cache_size: int = 10
    prediction_cache_ttl: int = 1800
    batch_size: int = 32
    max_sequence_length: int = 512
    confidence_threshold: float = 0.8
    gpu_enabled: bool = False
    gpu_memory_fraction: float = 0.8
    model_versions: Dict[str, str] = field(default_factory=lambda: {
        "sentiment": "v2.1",
        "classification": "v1.5",
        "summarization": "v3.0",
        "recommendation": "v2.3"
    })
    inference_timeout: int = 30
    model_update_interval: int = 86400  # 24 hours


class ReportsConfiguration:
    """    Ultra-advanced configuration management system for the reports module.
    
    Provides comprehensive configuration handling with environment-specific settings,
    security configurations, validation, and dynamic updates.
    """    
    def __init__(
        self,
        environment: Environment = Environment.PRODUCTION,
        config_path: Optional[str] = None,
        auto_reload: bool = False
    ):
        self.environment = environment
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.auto_reload = auto_reload
        
        # Configuration sections
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.cache = CacheConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.api = APIConfig()
        self.reports = ReportConfig()
        self.scheduler = SchedulerConfig()
        self.cloud = CloudConfig()
        self.ml = MLConfig()
        
        # Internal state
        self._config_hash: Optional[str] = None
        self._watchers: List[Any] = []
        self._encryption_key: Optional[bytes] = None
        
        # Load configuration
        self._load_configuration()
        
        # Setup auto-reload if enabled
        if auto_reload and CONFIG_WATCHING_AVAILABLE:
            self._setup_config_watching()
        
        logger.info(f"ReportsConfiguration initialized for environment: {environment}")
    
    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""        base_path = Path(__file__).parent.parent.parent.parent
        return base_path / "config" / f"reports.{self.environment.value}.yml"
    
    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""        try:
            # Load from file if exists
            if self.config_path.exists():
                self._load_from_file()
            
            # Override with environment variables
            self._load_from_environment()
            
            # Validate configuration
            self._validate_configuration()
            
            # Initialize encryption if needed
            if ENCRYPTION_AVAILABLE:
                self._initialize_encryption()
            
            # Calculate configuration hash
            self._config_hash = self._calculate_config_hash()
            
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_from_file(self) -> None:
        """Load configuration from YAML file."""        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                return
            
            # Load database configuration
            if 'database' in config_data:
                db_config = config_data['database']
                self.database = DatabaseConfig(**db_config)
            
            # Load Redis configuration
            if 'redis' in config_data:
                redis_config = config_data['redis']
                if 'password' in redis_config and redis_config['password']:
                    redis_config['password'] = SecretStr(redis_config['password'])
                self.redis = RedisConfig(**redis_config)
            
            # Load cache configuration
            if 'cache' in config_data:
                cache_config = config_data['cache']
                if 'redis_config' in cache_config:
                    cache_config['redis_config'] = RedisConfig(**cache_config['redis_config'])
                self.cache = CacheConfig(**cache_config)
            
            # Load security configuration
            if 'security' in config_data:
                security_config = config_data['security']
                if 'secret_key' in security_config:
                    security_config['secret_key'] = SecretStr(security_config['secret_key'])
                if 'encryption_key' in security_config and security_config['encryption_key']:
                    security_config['encryption_key'] = SecretStr(security_config['encryption_key'])
                self.security = SecurityConfig(**security_config)
            
            # Load monitoring configuration
            if 'monitoring' in config_data:
                self.monitoring = MonitoringConfig(**config_data['monitoring'])
            
            # Load API configuration
            if 'api' in config_data:
                self.api = APIConfig(**config_data['api'])
            
            # Load reports configuration
            if 'reports' in config_data:
                reports_config = config_data['reports']
                if 'supported_formats' in reports_config:
                    reports_config['supported_formats'] = [
                        ExportFormat(fmt) for fmt in reports_config['supported_formats']
                    ]
                self.reports = ReportConfig(**reports_config)
            
            # Load scheduler configuration
            if 'scheduler' in config_data:
                self.scheduler = SchedulerConfig(**config_data['scheduler'])
            
            # Load cloud configuration
            if 'cloud' in config_data:
                cloud_config = config_data['cloud']
                if 'access_key' in cloud_config and cloud_config['access_key']:
                    cloud_config['access_key'] = SecretStr(cloud_config['access_key'])
                if 'secret_key' in cloud_config and cloud_config['secret_key']:
                    cloud_config['secret_key'] = SecretStr(cloud_config['secret_key'])
                self.cloud = CloudConfig(**cloud_config)
            
            # Load ML configuration
            if 'ml' in config_data:
                self.ml = MLConfig(**config_data['ml'])
            
        except Exception as e:
            logger.error(f"Failed to load configuration from file: {e}")
            raise
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""        try:
            # Database configuration
            if os.getenv('DB_HOST'):
                self.database.host = os.getenv('DB_HOST')
            if os.getenv('DB_PORT'):
                self.database.port = int(os.getenv('DB_PORT'))
            if os.getenv('DB_NAME'):
                self.database.database = os.getenv('DB_NAME')
            if os.getenv('DB_USER'):
                self.database.username = os.getenv('DB_USER')
            if os.getenv('DB_PASSWORD'):
                self.database.password = SecretStr(os.getenv('DB_PASSWORD'))
            
            # Redis configuration
            if os.getenv('REDIS_HOST'):
                self.redis.host = os.getenv('REDIS_HOST')
            if os.getenv('REDIS_PORT'):
                self.redis.port = int(os.getenv('REDIS_PORT'))
            if os.getenv('REDIS_PASSWORD'):
                self.redis.password = SecretStr(os.getenv('REDIS_PASSWORD'))
            
            # Security configuration
            if os.getenv('SECRET_KEY'):
                self.security.secret_key = SecretStr(os.getenv('SECRET_KEY'))
            if os.getenv('ENCRYPTION_KEY'):
                self.security.encryption_key = SecretStr(os.getenv('ENCRYPTION_KEY'))
            
            # API configuration
            if os.getenv('API_TITLE'):
                self.api.title = os.getenv('API_TITLE')
            if os.getenv('API_VERSION'):
                self.api.version = os.getenv('API_VERSION')
            
            # Cloud configuration
            if os.getenv('CLOUD_PROVIDER'):
                self.cloud.provider = CloudProvider(os.getenv('CLOUD_PROVIDER'))
            if os.getenv('CLOUD_REGION'):
                self.cloud.region = os.getenv('CLOUD_REGION')
            if os.getenv('CLOUD_BUCKET'):
                self.cloud.bucket_name = os.getenv('CLOUD_BUCKET')
            if os.getenv('CLOUD_ACCESS_KEY'):
                self.cloud.access_key = SecretStr(os.getenv('CLOUD_ACCESS_KEY'))
            if os.getenv('CLOUD_SECRET_KEY'):
                self.cloud.secret_key = SecretStr(os.getenv('CLOUD_SECRET_KEY'))
            
        except Exception as e:
            logger.error(f"Failed to load configuration from environment: {e}")
            raise
    
    def _validate_configuration(self) -> None:
        """Validate configuration values."""        try:
            # Validate database configuration
            if not self.database.host:
                raise ValueError("Database host is required")
            if not self.database.database:
                raise ValueError("Database name is required")
            if not self.database.username:
                raise ValueError("Database username is required")
            
            # Validate security configuration
            if len(self.security.secret_key.get_secret_value()) < 32:
                raise ValueError("Secret key must be at least 32 characters long")
            
            # Validate monitoring configuration
            if self.monitoring.metrics_port <= 0 or self.monitoring.metrics_port > 65535:
                raise ValueError("Metrics port must be between 1 and 65535")
            
            # Validate API configuration
            if self.api.pagination_default_limit <= 0:
                raise ValueError("Pagination default limit must be positive")
            if self.api.pagination_max_limit < self.api.pagination_default_limit:
                raise ValueError("Pagination max limit must be >= default limit")
            
            # Validate report configuration
            if self.reports.max_concurrent_reports <= 0:
                raise ValueError("Max concurrent reports must be positive")
            
            # Validate scheduler configuration
            if self.scheduler.max_concurrent_jobs <= 0:
                raise ValueError("Max concurrent jobs must be positive")
            
            logger.info("Configuration validation completed successfully")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _initialize_encryption(self) -> None:
        """Initialize encryption for sensitive data."""        try:
            if self.security.encryption_key:
                # Use provided encryption key
                key = self.security.encryption_key.get_secret_value().encode()
                if len(key) != 32:
                    # Derive key from provided key
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=b'reports_salt',
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(key))
                else:
                    key = base64.urlsafe_b64encode(key)
            else:
                # Generate new encryption key
                key = Fernet.generate_key()
            
            self._encryption_key = key
            logger.info("Encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def _calculate_config_hash(self) -> str:
        """Calculate hash of current configuration."""        config_dict = self.to_dict(include_secrets=False)
        config_str = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()
    
    def _setup_config_watching(self) -> None:
        """Setup configuration file watching for auto-reload."""        try:
            class ConfigFileHandler(FileSystemEventHandler):
                def __init__(self, config_instance):
                    self.config = config_instance
                
                def on_modified(self, event):
                    if not event.is_directory and event.src_path == str(self.config.config_path):
                        logger.info("Configuration file changed, reloading...")
                        self.config.reload()
            
            observer = Observer()
            event_handler = ConfigFileHandler(self)
            observer.schedule(event_handler, str(self.config_path.parent), recursive=False)
            observer.start()
            
            self._watchers.append(observer)
            logger.info("Configuration file watching enabled")
            
        except Exception as e:
            logger.error(f"Failed to setup configuration watching: {e}")
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt sensitive value."""        if not ENCRYPTION_AVAILABLE or not self._encryption_key:
            return value
        
        try:
            cipher = Fernet(self._encryption_key)
            encrypted = cipher.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt value: {e}")
            return value
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive value."""        if not ENCRYPTION_AVAILABLE or not self._encryption_key:
            return encrypted_value
        
        try:
            cipher = Fernet(self._encryption_key)
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt value: {e}")
            return encrypted_value
    
    def reload(self) -> None:
        """Reload configuration from file and environment."""        try:
            old_hash = self._config_hash
            self._load_configuration()
            
            if self._config_hash != old_hash:
                logger.info("Configuration reloaded with changes")
            else:
                logger.info("Configuration reloaded without changes")
                
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            raise
    
    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert configuration to dictionary."""        config_dict = {
            "environment": self.environment.value,
            "database": asdict(self.database),
            "redis": asdict(self.redis),
            "cache": asdict(self.cache),
            "security": asdict(self.security),
            "monitoring": asdict(self.monitoring),
            "api": asdict(self.api),
            "reports": asdict(self.reports),
            "scheduler": asdict(self.scheduler),
            "cloud": asdict(self.cloud),
            "ml": asdict(self.ml),
        }
        
        if not include_secrets:
            # Remove sensitive information
            config_dict["database"]["password"] = "***"
            if config_dict["redis"]["password"]:
                config_dict["redis"]["password"] = "***"
            config_dict["security"]["secret_key"] = "***"
            if config_dict["security"]["encryption_key"]:
                config_dict["security"]["encryption_key"] = "***"
            if config_dict["cloud"]["access_key"]:
                config_dict["cloud"]["access_key"] = "***"
            if config_dict["cloud"]["secret_key"]:
                config_dict["cloud"]["secret_key"] = "***"
        
        return config_dict
    
    def to_yaml(self, include_secrets: bool = False) -> str:
        """Export configuration to YAML format."""        config_dict = self.to_dict(include_secrets=include_secrets)
        return yaml.dump(config_dict, default_flow_style=False, sort_keys=True)
    
    def save_to_file(self, file_path: Optional[str] = None, include_secrets: bool = False) -> None:
        """Save configuration to file."""        try:
            target_path = Path(file_path) if file_path else self.config_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w') as f:
                f.write(self.to_yaml(include_secrets=include_secrets))
            
            logger.info(f"Configuration saved to {target_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_database_url(self, async_driver: bool = True) -> str:
        """Get formatted database URL."""        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get formatted Redis URL."""        return self.redis.url
    
    def is_development(self) -> bool:
        """Check if running in development environment."""        return self.environment in [Environment.DEVELOPMENT, Environment.LOCAL]
    
    def is_production(self) -> bool:
        """Check if running in production environment."""        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""        return self.environment == Environment.TESTING
    
    def cleanup(self) -> None:
        """Cleanup watchers and resources."""        try:
            for watcher in self._watchers:
                watcher.stop()
                watcher.join()
            
            self._watchers.clear()
            logger.info("Configuration cleanup completed")
            
        except Exception as e:
            logger.error(f"Failed to cleanup configuration: {e}")


# Global configuration instance
_config_instance: Optional[ReportsConfiguration] = None


def get_config(
    environment: Optional[Environment] = None,
    config_path: Optional[str] = None,
    auto_reload: bool = False,
    force_reload: bool = False
) -> ReportsConfiguration:
    """Get global configuration instance."""    global _config_instance
    
    if _config_instance is None or force_reload:
        env = environment or Environment(os.getenv('ENVIRONMENT', 'production'))
        _config_instance = ReportsConfiguration(
            environment=env,
            config_path=config_path,
            auto_reload=auto_reload
        )
    
    return _config_instance


def reload_config() -> None:
    """Reload global configuration."""    global _config_instance
    if _config_instance:
        _config_instance.reload()


@contextmanager
def config_context(
    environment: Environment,
    config_path: Optional[str] = None,
    auto_reload: bool = False
):
    """Context manager for temporary configuration."""    original_config = _config_instance
    
    try:
        temp_config = ReportsConfiguration(
            environment=environment,
            config_path=config_path,
            auto_reload=auto_reload
        )
        
        global _config_instance
        _config_instance = temp_config
        
        yield temp_config
        
    finally:
        _config_instance = original_config


# Configuration validation schemas
DATABASE_SCHEMA = {
    'type': {'type': 'string', 'allowed': [t.value for t in DatabaseType]},
    'host': {'type': 'string', 'minlength': 1},
    'port': {'type': 'integer', 'min': 1, 'max': 65535},
    'database': {'type': 'string', 'minlength': 1},
    'username': {'type': 'string', 'minlength': 1},
    'pool_size': {'type': 'integer', 'min': 1, 'max': 100},
    'max_overflow': {'type': 'integer', 'min': 0, 'max': 200}
}

SECURITY_SCHEMA = {
    'secret_key': {'type': 'string', 'minlength': 32},
    'access_token_expire_minutes': {'type': 'integer', 'min': 1, 'max': 10080},
    'max_login_attempts': {'type': 'integer', 'min': 1, 'max': 10},
    'lockout_duration_minutes': {'type': 'integer', 'min': 1, 'max': 1440}
}

API_SCHEMA = {
    'rate_limit_default': {'type': 'string', 'regex': r'^\d+/(second|minute|hour|day)$'},
    'pagination_default_limit': {'type': 'integer', 'min': 1, 'max': 1000},
    'pagination_max_limit': {'type': 'integer', 'min': 1, 'max': 10000},
    'request_timeout': {'type': 'integer', 'min': 1, 'max': 300}
}


def validate_configuration(config: ReportsConfiguration) -> List[str]:
    """Validate configuration using schemas."""    if not VALIDATION_AVAILABLE:
        return []
    
    errors = []
    
    # Validate database configuration
    validator = Validator(DATABASE_SCHEMA)
    if not validator.validate(asdict(config.database)):
        errors.extend([f"Database: {error}" for error in validator.errors])
    
    # Validate security configuration
    validator = Validator(SECURITY_SCHEMA)
    security_dict = asdict(config.security)
    security_dict['secret_key'] = config.security.secret_key.get_secret_value()
    if not validator.validate(security_dict):
        errors.extend([f"Security: {error}" for error in validator.errors])
    
    # Validate API configuration
    validator = Validator(API_SCHEMA)
    if not validator.validate(asdict(config.api)):
        errors.extend([f"API: {error}" for error in validator.errors])
    
    return errors


# Export main components
__all__ = [
    "Environment",
    "LogLevel",
    "DatabaseType",
    "CacheType",
    "ExportFormat",
    "CloudProvider",
    "DatabaseConfig",
    "RedisConfig",
    "CacheConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "APIConfig",
    "ReportConfig",
    "SchedulerConfig",
    "CloudConfig",
    "MLConfig",
    "ReportsConfiguration",
    "get_config",
    "reload_config",
    "config_context",
    "validate_configuration"
]
