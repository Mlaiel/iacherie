"""
Production Configuration for Parsers Module
===========================================

Ultra-professional production configuration with enterprise-grade settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. Unauthorized use, reproduction,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import yaml
import json


class EnvironmentType(Enum):
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


@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "require"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis cache configuration"""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    ssl: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    max_connections: int = 50
    retry_on_timeout: bool = True


@dataclass
class AIModelConfig:
    """AI model configuration"""
    # Semantic analysis models
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    entity_model: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    topic_model: str = "facebook/bart-large-mnli"
    
    # Computer vision models
    image_classification_model: str = "google/vit-base-patch16-224"
    object_detection_model: str = "facebook/detr-resnet-50"
    nsfw_detection_model: str = "Falconsai/nsfw_image_detection"
    
    # Audio analysis models
    audio_classification_model: str = "facebook/wav2vec2-base-960h"
    music_genre_model: str = "marsyas/gtzan"
    
    # Model cache settings
    cache_dir: str = "/tmp/transformers_cache"
    max_cache_size_gb: int = 10
    device: str = "auto"  # auto, cpu, cuda, mps
    
    # Inference settings
    batch_size: int = 8
    max_length: int = 512
    truncation: bool = True
    padding: bool = True


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    # Concurrency settings
    max_concurrent_parsers: int = 100
    max_concurrent_requests: int = 1000
    worker_threads: int = 8
    
    # Memory management
    max_memory_usage_mb: int = 4096
    gc_threshold: int = 1000
    enable_memory_profiling: bool = False
    
    # Caching
    enable_result_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_cache_entries: int = 10000
    
    # Rate limiting
    rate_limit_per_minute: int = 6000
    burst_limit: int = 100
    
    # Timeouts
    parser_timeout_seconds: int = 30
    ai_model_timeout_seconds: int = 60
    network_timeout_seconds: int = 10


@dataclass
class SecurityConfig:
    """Security configuration"""
    # API keys and secrets
    youtube_api_key: Optional[str] = None
    instagram_api_key: Optional[str] = None
    tiktok_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Encryption
    enable_encryption: bool = True
    encryption_key: Optional[str] = None
    hash_algorithm: str = "sha256"
    
    # Content protection
    enable_content_fingerprinting: bool = True
    enable_copyright_detection: bool = True
    dmca_notification_endpoint: Optional[str] = None
    
    # Rate limiting and abuse prevention
    enable_rate_limiting: bool = True
    max_requests_per_ip: int = 1000
    blacklisted_ips: List[str] = field(default_factory=list)
    
    # Data privacy
    enable_gdpr_compliance: bool = True
    data_retention_days: int = 365
    anonymize_user_data: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"
    log_file: Optional[str] = "/var/log/ia-influencer/parsers.log"
    enable_structured_logging: bool = True
    
    # Metrics
    enable_prometheus_metrics: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    
    # Health checks
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 5
    
    # Alerting
    enable_alerting: bool = True
    alert_webhook_url: Optional[str] = None
    error_threshold_per_minute: int = 10
    response_time_threshold_ms: int = 1000
    
    # Tracing
    enable_distributed_tracing: bool = True
    jaeger_endpoint: Optional[str] = None
    trace_sampling_rate: float = 0.1


@dataclass
class ProductionConfig:
    """Complete production configuration"""
    # Environment
    environment: EnvironmentType = EnvironmentType.PRODUCTION
    debug: bool = False
    testing: bool = False
    
    # Application
    app_name: str = "IA-Influencer-Agent-Parsers"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1/parsers"
    
    # Components
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ai_models: AIModelConfig = field(default_factory=AIModelConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Feature flags
    enable_semantic_analysis: bool = True
    enable_economic_intelligence: bool = True
    enable_collaboration_matching: bool = True
    enable_trend_analysis: bool = True
    enable_content_protection: bool = True
    
    # Platform-specific settings
    youtube_enabled: bool = True
    instagram_enabled: bool = True
    tiktok_enabled: bool = True
    spotify_enabled: bool = True
    twitch_enabled: bool = True
    
    @classmethod
    def from_environment(cls) -> 'ProductionConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override from environment variables
        config.environment = EnvironmentType(os.getenv('ENVIRONMENT', 'production'))
        config.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Database
        config.database.host = os.getenv('DB_HOST', config.database.host)
        config.database.port = int(os.getenv('DB_PORT', str(config.database.port)))
        config.database.database = os.getenv('DB_NAME', config.database.database)
        config.database.username = os.getenv('DB_USERNAME', config.database.username)
        config.database.password = os.getenv('DB_PASSWORD', config.database.password)
        
        # Redis
        config.redis.host = os.getenv('REDIS_HOST', config.redis.host)
        config.redis.port = int(os.getenv('REDIS_PORT', str(config.redis.port)))
        config.redis.password = os.getenv('REDIS_PASSWORD', config.redis.password)
        
        # Security
        config.security.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        config.security.instagram_api_key = os.getenv('INSTAGRAM_API_KEY')
        config.security.tiktok_api_key = os.getenv('TIKTOK_API_KEY')
        config.security.openai_api_key = os.getenv('OPENAI_API_KEY')
        config.security.encryption_key = os.getenv('ENCRYPTION_KEY')
        
        # Monitoring
        config.monitoring.log_level = LogLevel(os.getenv('LOG_LEVEL', 'INFO'))
        config.monitoring.alert_webhook_url = os.getenv('ALERT_WEBHOOK_URL')
        config.monitoring.jaeger_endpoint = os.getenv('JAEGER_ENDPOINT')
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ProductionConfig':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductionConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Apply configuration from dictionary
        for key, value in data.items():
            if hasattr(config, key):
                if key == 'environment':
                    setattr(config, key, EnvironmentType(value))
                elif key in ['database', 'redis', 'ai_models', 'performance', 'security', 'monitoring']:
                    # Handle nested configurations
                    nested_config = getattr(config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(config, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):
                # Handle nested configurations
                result[key] = value.__dict__
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        
        return result
    
    def save_to_file(self, config_path: str):
        """Save configuration to file"""
        data = self.to_dict()
        
        with open(config_path, 'w') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                yaml.dump(data, f, default_flow_style=False, indent=2)
            else:
                json.dump(data, f, indent=2)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Required API keys for production
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.security.youtube_api_key and self.youtube_enabled:
                errors.append("YouTube API key is required for production")
            
            if not self.security.encryption_key:
                errors.append("Encryption key is required for production")
            
            if not self.database.password:
                errors.append("Database password is required for production")
        
        # Performance validations
        if self.performance.max_concurrent_parsers <= 0:
            errors.append("max_concurrent_parsers must be greater than 0")
        
        if self.performance.max_memory_usage_mb <= 0:
            errors.append("max_memory_usage_mb must be greater than 0")
        
        # Security validations
        if self.security.rate_limit_per_minute <= 0:
            errors.append("rate_limit_per_minute must be greater than 0")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return len(self.validate()) == 0


# Predefined production configurations

PRODUCTION_CONFIG = ProductionConfig(
    environment=EnvironmentType.PRODUCTION,
    debug=False,
    database=DatabaseConfig(
        host="prod-db.ia-influencer.com",
        database="ia_influencer_prod",
        pool_size=50,
        max_overflow=100
    ),
    redis=RedisConfig(
        host="prod-redis.ia-influencer.com",
        ssl=True,
        max_connections=100
    ),
    performance=PerformanceConfig(
        max_concurrent_parsers=200,
        max_concurrent_requests=2000,
        worker_threads=16,
        max_memory_usage_mb=8192
    ),
    monitoring=MonitoringConfig(
        log_level=LogLevel.INFO,
        enable_prometheus_metrics=True,
        enable_alerting=True,
        enable_distributed_tracing=True
    )
)

STAGING_CONFIG = ProductionConfig(
    environment=EnvironmentType.STAGING,
    debug=False,
    database=DatabaseConfig(
        host="staging-db.ia-influencer.com",
        database="ia_influencer_staging"
    ),
    redis=RedisConfig(
        host="staging-redis.ia-influencer.com"
    ),
    performance=PerformanceConfig(
        max_concurrent_parsers=50,
        max_concurrent_requests=500
    ),
    monitoring=MonitoringConfig(
        log_level=LogLevel.DEBUG
    )
)

DEVELOPMENT_CONFIG = ProductionConfig(
    environment=EnvironmentType.DEVELOPMENT,
    debug=True,
    database=DatabaseConfig(
        host="localhost",
        echo=True
    ),
    redis=RedisConfig(
        host="localhost",
        ssl=False
    ),
    performance=PerformanceConfig(
        max_concurrent_parsers=10,
        max_concurrent_requests=100,
        enable_memory_profiling=True
    ),
    monitoring=MonitoringConfig(
        log_level=LogLevel.DEBUG,
        enable_prometheus_metrics=False,
        enable_alerting=False
    )
)


def get_config(environment: str = None) -> ProductionConfig:
    """Get configuration for specified environment"""
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    
    env_type = EnvironmentType(environment.lower())
    
    if env_type == EnvironmentType.PRODUCTION:
        return PRODUCTION_CONFIG
    elif env_type == EnvironmentType.STAGING:
        return STAGING_CONFIG
    elif env_type == EnvironmentType.DEVELOPMENT:
        return DEVELOPMENT_CONFIG
    else:
        # Load from environment variables
        return ProductionConfig.from_environment()


def create_config_template(output_path: str = "parsers_config_template.yaml"):
    """Create a configuration template file"""
    template_config = ProductionConfig()
    template_config.save_to_file(output_path)
    print(f"Configuration template created at: {output_path}")


if __name__ == "__main__":
    # Create configuration template
    create_config_template()
    
    # Example usage
    config = get_config("production")
    print(f"Loaded configuration for: {config.environment.value}")
    print(f"Configuration valid: {config.is_valid()}")
    
    if not config.is_valid():
        print("Validation errors:")
        for error in config.validate():
            print(f"  - {error}")
