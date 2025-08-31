"""Crawling Agent Configuration - Advanced Settings & Parameters

Comprehensive configuration system for all crawling agent components with
environment-specific settings, security parameters, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum

class EnvironmentType(Enum):
    """Environment types for configuration"""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(Enum):
    """Logging levels"""    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class DatabaseConfig:
    """Database configuration settings"""    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    database: str = os.getenv("POSTGRES_DB", "ia_influencer")
    username: str = os.getenv("POSTGRES_USER", "admin")
    password: str = os.getenv("POSTGRES_PASSWORD", "")
    pool_size: int = 20
    max_overflow: int = 50
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo_queries: bool = False

@dataclass
class RedisConfig:
    """Redis configuration for caching and queues"""    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    database: int = int(os.getenv("REDIS_DB", "0"))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    connection_pool_size: int = 50
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    socket_keepalive: bool = True
    socket_keepalive_options: Dict = field(default_factory=dict)

@dataclass
class CrawlingPerformanceConfig:
    """Performance tuning for crawling operations"""    max_concurrent_requests: int = 100
    max_concurrent_agents: int = 10
    request_timeout_seconds: int = 30
    connection_timeout_seconds: int = 10
    read_timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    exponential_backoff: bool = True
    max_delay_seconds: float = 60.0
    
    # Rate limiting
    requests_per_second: float = 10.0
    requests_per_minute: int = 600
    requests_per_hour: int = 36000
    burst_size: int = 20
    
    # Connection pooling
    connection_pool_size: int = 100
    connection_pool_max_size: int = 200
    keep_alive_timeout: int = 30
    tcp_keepalive: bool = True

@dataclass
class SecurityConfig:
    """Security configuration settings"""    # API security
    api_key_encryption_key: str = os.getenv("API_ENCRYPTION_KEY", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Content protection
    content_encryption_enabled: bool = True
    fingerprint_salt: str = os.getenv("FINGERPRINT_SALT", "default_salt")
    hash_algorithm: str = "sha256"
    
    # Network security
    enable_ssl_verification: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_domains: Set[str] = field(default_factory=set)
    
    # User agent rotation
    rotate_user_agents: bool = True
    custom_user_agents: List[str] = field(default_factory=list)
    
    # Proxy settings
    enable_proxy_rotation: bool = True
    proxy_providers: List[str] = field(default_factory=list)
    proxy_authentication: Dict[str, str] = field(default_factory=dict)

@dataclass 
class PlatformAPIConfig:
    """Platform API configuration and credentials"""    # Twitter API
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_token_secret: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # YouTube API
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    youtube_client_id: str = os.getenv("YOUTUBE_CLIENT_ID", "")
    youtube_client_secret: str = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    
    # Instagram API
    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_client_id: str = os.getenv("INSTAGRAM_CLIENT_ID", "")
    instagram_client_secret: str = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
    
    # Facebook API
    facebook_app_id: str = os.getenv("FACEBOOK_APP_ID", "")
    facebook_app_secret: str = os.getenv("FACEBOOK_APP_SECRET", "")
    facebook_access_token: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    
    # LinkedIn API
    linkedin_client_id: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    linkedin_client_secret: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    linkedin_access_token: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    
    # Spotify API
    spotify_client_id: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    spotify_client_secret: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    # TikTok API
    tiktok_client_key: str = os.getenv("TIKTOK_CLIENT_KEY", "")
    tiktok_client_secret: str = os.getenv("TIKTOK_CLIENT_SECRET", "")
    
    # Generic API settings
    api_request_timeout: int = 30
    api_max_retries: int = 3
    api_retry_delay: float = 1.0

@dataclass
class AlertConfig:
    """Alert and notification configuration"""    # Email settings
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    
    # SMS settings (Twilio)
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")
    
    # Webhook settings
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "")
    webhook_timeout: int = 30
    webhook_retries: int = 3
    
    # Slack settings
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_app_token: str = os.getenv("SLACK_APP_TOKEN", "")
    slack_default_channel: str = "#alerts"
    
    # Push notification settings
    push_service_key: str = os.getenv("PUSH_SERVICE_KEY", "")
    
    # Alert thresholds
    similarity_threshold: float = 0.8
    volume_threshold: int = 100
    frequency_threshold: int = 10

@dataclass
class MLConfig:
    """Machine Learning and AI configuration"""    # Model settings
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    similarity_model_path: str = "models/similarity/"
    embedding_dimension: int = 384
    
    # FAISS index settings
    faiss_index_type: str = "IndexFlatIP"
    faiss_nprobe: int = 10
    faiss_ef_search: int = 50
    
    # Content analysis
    enable_sentiment_analysis: bool = True
    enable_language_detection: bool = True
    enable_topic_modeling: bool = True
    enable_named_entity_recognition: bool = True
    
    # Image processing
    image_hash_size: int = 16
    image_similarity_threshold: float = 0.85
    enable_ocr: bool = True
    ocr_languages: List[str] = field(default_factory=lambda: ["eng", "ger", "fra"])
    
    # Audio processing
    audio_sample_rate: int = 22050
    audio_hop_length: int = 512
    audio_n_mels: int = 128
    audio_similarity_threshold: float = 0.8
    
    # Performance
    use_gpu: bool = False
    batch_size: int = 32
    num_workers: int = 4

@dataclass
class MonitoringConfig:
    """System monitoring and observability"""    # Metrics
    enable_prometheus: bool = True
    prometheus_port: int = 9090
    metrics_namespace: str = "crawling_agent"
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: str = "logs/crawling_agent.log"
    log_rotation_size: str = "100MB"
    log_retention_days: int = 30
    
    # Tracing
    enable_tracing: bool = True
    jaeger_endpoint: str = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
    trace_sample_rate: float = 0.1
    
    # Health checks
    health_check_interval: int = 60
    health_check_timeout: int = 30
    
    # Alerting on system issues
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0
    disk_threshold: float = 90.0
    response_time_threshold: float = 5.0

@dataclass
class StorageConfig:
    """Storage configuration for content and metadata"""    # File storage
    storage_backend: str = "s3"  # s3, gcs, azure, local
    storage_bucket: str = os.getenv("STORAGE_BUCKET", "ia-influencer-content")
    storage_region: str = os.getenv("STORAGE_REGION", "us-east-1")
    
    # AWS S3 settings
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    # Content retention
    content_retention_days: int = 365
    thumbnail_retention_days: int = 30
    log_retention_days: int = 90
    
    # Compression
    enable_compression: bool = True
    compression_algorithm: str = "gzip"
    compression_level: int = 6

@dataclass
class CrawlingAgentConfig:
    """Master configuration for crawling agent"""    environment: EnvironmentType = EnvironmentType.PRODUCTION
    debug_mode: bool = False
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    performance: CrawlingPerformanceConfig = field(default_factory=CrawlingPerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    platform_apis: PlatformAPIConfig = field(default_factory=PlatformAPIConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    ml: MLConfig = field(default_factory=MLConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # Agent-specific settings
    agent_id: str = "crawling_agent"
    agent_version: str = "2.0.0"
    max_concurrent_operations: int = 50
    operation_timeout_minutes: int = 30
    
    # Feature flags
    enable_real_time_monitoring: bool = True
    enable_similarity_detection: bool = True
    enable_content_analysis: bool = True
    enable_automated_alerts: bool = True
    enable_machine_learning: bool = True
    enable_advanced_crawling: bool = True
    
    # Experimental features
    enable_blockchain_verification: bool = False
    enable_ai_content_generation_detection: bool = True
    enable_deepfake_detection: bool = False
    enable_voice_cloning_detection: bool = False

def load_config_from_environment() -> CrawlingAgentConfig:
    """    Load configuration from environment variables with validation
    """    config = CrawlingAgentConfig()
    
    # Set environment type
    env_type = os.getenv("ENVIRONMENT", "production").lower()
    if env_type in ["dev", "development"]:
        config.environment = EnvironmentType.DEVELOPMENT
        config.debug_mode = True
    elif env_type in ["test", "testing"]:
        config.environment = EnvironmentType.TESTING
    elif env_type in ["stage", "staging"]:
        config.environment = EnvironmentType.STAGING
    else:
        config.environment = EnvironmentType.PRODUCTION
    
    # Validate critical configurations
    _validate_config(config)
    
    return config

def _validate_config(config: CrawlingAgentConfig) -> None:
    """    Validate configuration for required settings and logical consistency
    """    # Database validation
    if not config.database.host or not config.database.database:
        raise ValueError("Database host and database name are required")
    
    # Security validation
    if config.environment == EnvironmentType.PRODUCTION:
        if not config.security.api_key_encryption_key:
            raise ValueError("API key encryption key is required in production")
        if not config.security.jwt_secret_key:
            raise ValueError("JWT secret key is required in production")
    
    # Performance validation
    if config.performance.max_concurrent_requests < 1:
        raise ValueError("Max concurrent requests must be at least 1")
    
    # API validation for enabled platforms
    required_apis = []
    if config.platform_apis.twitter_api_key:
        required_apis.append("Twitter")
    if config.platform_apis.youtube_api_key:
        required_apis.append("YouTube")
    
    logger.info(f"Configuration validated for environment: {config.environment.value}")
    if required_apis:
        logger.info(f"Configured APIs: {', '.join(required_apis)}")

def get_config() -> CrawlingAgentConfig:
    """    Get the global configuration instance
    """    return load_config_from_environment()

# Pre-configured settings for different environments
DEVELOPMENT_CONFIG = CrawlingAgentConfig(
    environment=EnvironmentType.DEVELOPMENT,
    debug_mode=True,
    performance=CrawlingPerformanceConfig(
        max_concurrent_requests=10,
        max_concurrent_agents=2,
        requests_per_second=5.0
    ),
    monitoring=MonitoringConfig(
        log_level=LogLevel.DEBUG,
        enable_tracing=True,
        trace_sample_rate=1.0
    )
)

TESTING_CONFIG = CrawlingAgentConfig(
    environment=EnvironmentType.TESTING,
    debug_mode=True,
    performance=CrawlingPerformanceConfig(
        max_concurrent_requests=5,
        max_concurrent_agents=1,
        requests_per_second=2.0
    ),
    monitoring=MonitoringConfig(
        log_level=LogLevel.DEBUG,
        enable_prometheus=False,
        enable_tracing=False
    )
)

PRODUCTION_CONFIG = CrawlingAgentConfig(
    environment=EnvironmentType.PRODUCTION,
    debug_mode=False,
    performance=CrawlingPerformanceConfig(
        max_concurrent_requests=100,
        max_concurrent_agents=10,
        requests_per_second=20.0
    ),
    monitoring=MonitoringConfig(
        log_level=LogLevel.INFO,
        enable_prometheus=True,
        enable_tracing=True,
        trace_sample_rate=0.1
    ),
    security=SecurityConfig(
        enable_ssl_verification=True,
        rotate_user_agents=True,
        enable_proxy_rotation=True
    )
)

# Export main configuration interface
__all__ = [
    'CrawlingAgentConfig',
    'DatabaseConfig', 
    'RedisConfig',
    'CrawlingPerformanceConfig',
    'SecurityConfig',
    'PlatformAPIConfig',
    'AlertConfig',
    'MLConfig',
    'MonitoringConfig',
    'StorageConfig',
    'load_config_from_environment',
    'get_config',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG', 
    'PRODUCTION_CONFIG'
]
