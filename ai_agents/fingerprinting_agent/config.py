"""
Configuration Module for Fingerprinting Agent

Ultra-professional configuration management with environment-specific settings,
security controls, performance optimization, and monitoring integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import os
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import timedelta


class Environment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging level configuration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer_agent"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo_sql: bool = False
    ssl_mode: str = "prefer"


@dataclass
class RedisConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    socket_timeout: int = 30
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=lambda: {})
    health_check_interval: int = 30


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration for text search"""
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    use_ssl: bool = False
    verify_certs: bool = False
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True


@dataclass
class StorageConfig:
    """File storage configuration"""
    base_path: str = "/tmp/fingerprinting"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".mp3", ".wav", ".flac", ".ogg", ".m4a",  # Audio
        ".mp4", ".avi", ".mov", ".webm", ".mkv",  # Video
        ".jpg", ".png", ".gif", ".bmp", ".webp",  # Image
        ".txt", ".pdf", ".docx", ".html", ".md"   # Text
    ])
    cleanup_interval: int = 86400  # 24 hours
    retention_period: int = 604800  # 7 days


@dataclass
class SecurityConfig:
    """Security and authentication configuration"""
    jwt_secret_key: str = "ultra-secure-fingerprinting-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    max_concurrent_requests: int = 50
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    api_key_header: str = "X-API-Key"
    require_api_key: bool = True


@dataclass
class ModelConfig:
    """AI/ML model configuration"""
    # Model directories
    model_cache_dir: str = "/tmp/models"
    download_timeout: int = 300
    
    # Audio models
    wav2vec2_model: str = "facebook/wav2vec2-base-960h"
    hubert_model: str = "facebook/hubert-base-ls960"
    enable_audio_gpu: bool = True
    
    # Vision models
    resnet_model: str = "resnet50"
    clip_model: str = "ViT-B/32"
    enable_vision_gpu: bool = True
    
    # NLP models
    bert_model: str = "bert-base-uncased"
    roberta_model: str = "roberta-base"
    spacy_model: str = "en_core_web_sm"
    enable_nlp_gpu: bool = True
    
    # Performance settings
    batch_size: int = 32
    max_sequence_length: int = 512
    model_precision: str = "fp16"  # fp32, fp16, int8


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    # Threading
    max_workers: int = 8
    thread_pool_executor: bool = True
    
    # Processing
    enable_parallel_processing: bool = True
    chunk_size: int = 1024
    buffer_size: int = 8192
    
    # Caching
    enable_memory_cache: bool = True
    memory_cache_size: int = 1000
    cache_ttl_seconds: int = 3600
    
    # Resource limits
    max_memory_usage: int = 8 * 1024 * 1024 * 1024  # 8GB
    max_cpu_usage: float = 0.8  # 80%
    
    # Quality thresholds
    similarity_threshold: float = 0.75
    confidence_threshold: float = 0.8
    quality_threshold: float = 0.85


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    enable_metrics: bool = True
    metrics_port: int = 8090
    metrics_path: str = "/metrics"
    
    enable_health_check: bool = True
    health_check_port: int = 8091
    health_check_path: str = "/health"
    
    enable_distributed_tracing: bool = True
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file: Optional[str] = None
    log_max_size: int = 100 * 1024 * 1024  # 100MB
    log_backup_count: int = 5


@dataclass
class FingerprintingConfig:
    """Complete fingerprinting agent configuration"""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    models: ModelConfig = field(default_factory=ModelConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    @classmethod
    def from_env(cls) -> 'FingerprintingConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Environment
        env_name = os.getenv("FINGERPRINTING_ENV", "development")
        config.environment = Environment(env_name)
        config.debug = os.getenv("FINGERPRINTING_DEBUG", "false").lower() == "true"
        
        # Database
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", str(config.database.port)))
        config.database.database = os.getenv("DB_NAME", config.database.database)
        config.database.username = os.getenv("DB_USER", config.database.username)
        config.database.password = os.getenv("DB_PASSWORD", config.database.password)
        
        # Redis
        config.redis.host = os.getenv("REDIS_HOST", config.redis.host)
        config.redis.port = int(os.getenv("REDIS_PORT", str(config.redis.port)))
        config.redis.password = os.getenv("REDIS_PASSWORD", config.redis.password)
        
        # Elasticsearch
        es_hosts = os.getenv("ES_HOSTS", ",".join(config.elasticsearch.hosts))
        config.elasticsearch.hosts = [host.strip() for host in es_hosts.split(",")]
        config.elasticsearch.username = os.getenv("ES_USERNAME", config.elasticsearch.username)
        config.elasticsearch.password = os.getenv("ES_PASSWORD", config.elasticsearch.password)
        
        # Storage
        config.storage.base_path = os.getenv("STORAGE_PATH", config.storage.base_path)
        config.storage.max_file_size = int(os.getenv("MAX_FILE_SIZE", str(config.storage.max_file_size)))
        
        # Security
        config.security.jwt_secret_key = os.getenv("JWT_SECRET", config.security.jwt_secret_key)
        config.security.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", str(config.security.rate_limit_per_minute)))
        
        # Performance
        config.performance.max_workers = int(os.getenv("MAX_WORKERS", str(config.performance.max_workers)))
        config.performance.similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", str(config.performance.similarity_threshold)))
        
        # Models
        config.models.model_cache_dir = os.getenv("MODEL_CACHE_DIR", config.models.model_cache_dir)
        config.models.enable_audio_gpu = os.getenv("ENABLE_AUDIO_GPU", "true").lower() == "true"
        config.models.enable_vision_gpu = os.getenv("ENABLE_VISION_GPU", "true").lower() == "true"
        config.models.enable_nlp_gpu = os.getenv("ENABLE_NLP_GPU", "true").lower() == "true"
        
        return config
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'FingerprintingConfig':
        """Load configuration from JSON file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert nested dictionaries to dataclass instances
        config = cls()
        
        for key, value in data.items():
            if hasattr(config, key):
                if key == "environment":
                    setattr(config, key, Environment(value))
                elif key == "monitoring" and "log_level" in value:
                    value["log_level"] = LogLevel(value["log_level"])
                    setattr(config, key, MonitoringConfig(**value))
                elif isinstance(getattr(config, key), (DatabaseConfig, RedisConfig, ElasticsearchConfig, StorageConfig, SecurityConfig, ModelConfig, PerformanceConfig, MonitoringConfig)):
                    config_class = type(getattr(config, key))
                    setattr(config, key, config_class(**value))
                else:
                    setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            
            if isinstance(value, Enum):
                result[field_name] = value.value
            elif hasattr(value, '__dataclass_fields__'):
                # Nested dataclass
                nested_dict = {}
                for nested_field in value.__dataclass_fields__:
                    nested_value = getattr(value, nested_field)
                    if isinstance(nested_value, Enum):
                        nested_dict[nested_field] = nested_value.value
                    else:
                        nested_dict[nested_field] = nested_value
                result[field_name] = nested_dict
            else:
                result[field_name] = value
        
        return result
    
    def save_to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to JSON file"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Database validation
        if not self.database.host:
            errors.append("Database host is required")
        if not (1 <= self.database.port <= 65535):
            errors.append("Database port must be between 1 and 65535")
        if not self.database.database:
            errors.append("Database name is required")
        
        # Redis validation
        if not self.redis.host:
            errors.append("Redis host is required")
        if not (1 <= self.redis.port <= 65535):
            errors.append("Redis port must be between 1 and 65535")
        
        # Storage validation
        if not self.storage.base_path:
            errors.append("Storage base path is required")
        if self.storage.max_file_size <= 0:
            errors.append("Maximum file size must be positive")
        
        # Security validation
        if not self.security.jwt_secret_key:
            errors.append("JWT secret key is required")
        if len(self.security.jwt_secret_key) < 32:
            errors.append("JWT secret key should be at least 32 characters")
        
        # Performance validation
        if self.performance.max_workers <= 0:
            errors.append("Max workers must be positive")
        if not (0.0 <= self.performance.similarity_threshold <= 1.0):
            errors.append("Similarity threshold must be between 0.0 and 1.0")
        
        return errors
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return (
            f"postgresql://{self.database.username}:{self.database.password}"
            f"@{self.database.host}:{self.database.port}/{self.database.database}"
        )
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        auth = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth}{self.redis.host}:{self.redis.port}/{self.redis.database}"
    
    def setup_logging(self) -> None:
        """Configure logging based on monitoring settings"""
        log_level = getattr(logging, self.monitoring.log_level.value)
        
        if self.monitoring.log_format == "json":
            import json
            
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_data = {
                        "timestamp": self.formatTime(record),
                        "level": record.levelname,
                        "logger": record.name,
                        "message": record.getMessage(),
                        "module": record.module,
                        "function": record.funcName,
                        "line": record.lineno
                    }
                    if record.exc_info:
                        log_data["exception"] = self.formatException(record.exc_info)
                    return json.dumps(log_data)
            
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if self.monitoring.log_file:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                self.monitoring.log_file,
                maxBytes=self.monitoring.log_max_size,
                backupCount=self.monitoring.log_backup_count
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)


# Global configuration instance
_config: Optional[FingerprintingConfig] = None


def get_config() -> FingerprintingConfig:
    """Get global configuration instance"""
    global _config
    
    if _config is None:
        # Try to load from file first
        config_file = os.getenv("FINGERPRINTING_CONFIG_FILE")
        if config_file and Path(config_file).exists():
            _config = FingerprintingConfig.from_file(config_file)
        else:
            # Load from environment
            _config = FingerprintingConfig.from_env()
        
        # Validate configuration
        errors = _config.validate()
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        # Setup logging
        _config.setup_logging()
        
        logging.info(f"Fingerprinting Agent configuration loaded for {_config.environment.value} environment")
    
    return _config


def set_config(config: FingerprintingConfig) -> None:
    """Set global configuration instance"""
    global _config
    _config = config


def reset_config() -> None:
    """Reset global configuration instance"""
    global _config
    _config = None


# Configuration presets for different environments
DEVELOPMENT_CONFIG = {
    "environment": "development",
    "debug": True,
    "database": {
        "echo_sql": True,
        "pool_size": 5
    },
    "security": {
        "require_api_key": False,
        "rate_limit_per_minute": 1000
    },
    "performance": {
        "max_workers": 2,
        "similarity_threshold": 0.7
    },
    "monitoring": {
        "log_level": "DEBUG",
        "log_format": "text"
    }
}

PRODUCTION_CONFIG = {
    "environment": "production",
    "debug": False,
    "database": {
        "echo_sql": False,
        "pool_size": 20,
        "ssl_mode": "require"
    },
    "security": {
        "require_api_key": True,
        "rate_limit_per_minute": 100
    },
    "performance": {
        "max_workers": 16,
        "similarity_threshold": 0.85
    },
    "monitoring": {
        "log_level": "INFO",
        "log_format": "json",
        "enable_metrics": True,
        "enable_distributed_tracing": True
    }
}
