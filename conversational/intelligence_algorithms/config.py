"""
Intelligence Algorithms Configuration - IA Influencer Agent Platform
==================================================================

Comprehensive configuration management for all intelligence algorithms
with environment-specific settings, performance tuning, and security
configurations for enterprise-grade deployment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL INTELLECTUAL PROPERTY WARNING 
This configuration system is the EXCLUSIVE property of Fahed Mlaiel.
ANY UNAUTHORIZED USE, COPYING, OR REVERSE ENGINEERING is strictly prohibited
and will result in immediate legal prosecution under international copyright laws.
Contact: mlaiel@live.de for legal authorization inquiries only.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Environment types for configuration management"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Logging levels for system configuration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class DatabaseConfig:
    """Database configuration for intelligence algorithms"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "ia_influencer_intelligence")
    username: str = os.getenv("DB_USERNAME", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"


@dataclass
class RedisConfig:
    """Redis configuration for caching and real-time processing"""
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = int(os.getenv("REDIS_DB", "0"))
    password: str = os.getenv("REDIS_PASSWORD", "")
    max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "100"))
    socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "30"))
    health_check_interval: int = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))


@dataclass
class AIModelConfig:
    """AI/ML model configuration for intelligence algorithms"""
    # Core AI Models
    bert_model_name: str = os.getenv("BERT_MODEL_NAME", "bert-base-multilingual-cased")
    clip_model_name: str = os.getenv("CLIP_MODEL_NAME", "openai/clip-vit-base-patch32")
    whisper_model_name: str = os.getenv("WHISPER_MODEL_NAME", "openai/whisper-base")
    
    # Model Performance Settings
    batch_size: int = int(os.getenv("AI_BATCH_SIZE", "32"))
    max_sequence_length: int = int(os.getenv("AI_MAX_SEQUENCE_LENGTH", "512"))
    inference_timeout: int = int(os.getenv("AI_INFERENCE_TIMEOUT", "30"))
    
    # GPU Configuration
    use_gpu: bool = os.getenv("AI_USE_GPU", "true").lower() == "true"
    gpu_memory_fraction: float = float(os.getenv("AI_GPU_MEMORY_FRACTION", "0.8"))
    
    # Model Cache Settings
    model_cache_dir: str = os.getenv("AI_MODEL_CACHE_DIR", "/tmp/ia_models")
    model_download_timeout: int = int(os.getenv("AI_MODEL_DOWNLOAD_TIMEOUT", "300"))


@dataclass
class VectorDatabaseConfig:
    """Vector database configuration for semantic search and embeddings"""
    # FAISS Configuration
    faiss_index_type: str = os.getenv("FAISS_INDEX_TYPE", "IVF")
    faiss_nlist: int = int(os.getenv("FAISS_NLIST", "1024"))
    faiss_nprobe: int = int(os.getenv("FAISS_NPROBE", "64"))
    
    # Pinecone Configuration
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "ia-influencer-intelligence")
    
    # Weaviate Configuration
    weaviate_url: str = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    weaviate_api_key: str = os.getenv("WEAVIATE_API_KEY", "")
    
    # Elasticsearch Configuration
    elasticsearch_hosts: str = os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200")
    elasticsearch_username: str = os.getenv("ELASTICSEARCH_USERNAME", "")
    elasticsearch_password: str = os.getenv("ELASTICSEARCH_PASSWORD", "")


@dataclass
class BlockchainConfig:
    """Blockchain configuration for content protection and ownership"""
    # Ethereum Configuration
    ethereum_rpc_url: str = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/your-project-id")
    ethereum_private_key: str = os.getenv("ETHEREUM_PRIVATE_KEY", "")
    ethereum_contract_address: str = os.getenv("ETHEREUM_CONTRACT_ADDRESS", "")
    
    # IPFS Configuration
    ipfs_gateway_url: str = os.getenv("IPFS_GATEWAY_URL", "https://ipfs.io/ipfs/")
    ipfs_api_url: str = os.getenv("IPFS_API_URL", "http://localhost:5001")
    
    # Gas and Transaction Settings
    gas_limit: int = int(os.getenv("ETHEREUM_GAS_LIMIT", "200000"))
    gas_price_gwei: int = int(os.getenv("ETHEREUM_GAS_PRICE_GWEI", "20"))


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    # Response Time Targets
    max_response_time_ms: int = int(os.getenv("MAX_RESPONSE_TIME_MS", "50"))
    api_timeout_seconds: int = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
    
    # Concurrency Settings
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "1000"))
    max_concurrent_algorithms: int = int(os.getenv("MAX_CONCURRENT_ALGORITHMS", "50"))
    worker_threads: int = int(os.getenv("WORKER_THREADS", "4"))
    
    # Caching Configuration
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    cache_max_size: int = int(os.getenv("CACHE_MAX_SIZE", "10000"))
    
    # Memory Management
    max_memory_usage_mb: int = int(os.getenv("MAX_MEMORY_USAGE_MB", "4096"))
    garbage_collection_threshold: int = int(os.getenv("GC_THRESHOLD", "1000"))


@dataclass
class SecurityConfig:
    """Security configuration for enterprise deployment"""
    # Encryption Settings
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # API Security
    rate_limit_requests_per_minute: int = int(os.getenv("RATE_LIMIT_RPM", "1000"))
    cors_allowed_origins: str = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    
    # Content Protection
    copyright_scan_enabled: bool = os.getenv("COPYRIGHT_SCAN_ENABLED", "true").lower() == "true"
    plagiarism_detection_enabled: bool = os.getenv("PLAGIARISM_DETECTION_ENABLED", "true").lower() == "true"
    
    # Audit and Compliance
    audit_logging_enabled: bool = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
    gdpr_compliance_enabled: bool = os.getenv("GDPR_COMPLIANCE_ENABLED", "true").lower() == "true"


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    # Health Checks
    health_check_enabled: bool = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
    health_check_interval_seconds: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    
    # Metrics and Analytics
    metrics_enabled: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    prometheus_endpoint: str = os.getenv("PROMETHEUS_ENDPOINT", "/metrics")
    grafana_dashboard_enabled: bool = os.getenv("GRAFANA_DASHBOARD_ENABLED", "true").lower() == "true"
    
    # Logging Configuration
    log_level: LogLevel = LogLevel(os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = os.getenv("LOG_FORMAT", "json")
    log_file_path: str = os.getenv("LOG_FILE_PATH", "/var/log/ia-influencer-intelligence.log")
    
    # Error Tracking
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    error_reporting_enabled: bool = os.getenv("ERROR_REPORTING_ENABLED", "true").lower() == "true"


@dataclass
class IntelligenceAlgorithmsConfig:
    """Main configuration class for all intelligence algorithms"""
    
    # Environment Settings
    environment: EnvironmentType = EnvironmentType(os.getenv("ENVIRONMENT", "development"))
    debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Component Configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ai_models: AIModelConfig = field(default_factory=AIModelConfig)
    vector_db: VectorDatabaseConfig = field(default_factory=VectorDatabaseConfig)
    blockchain: BlockchainConfig = field(default_factory=BlockchainConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Algorithm-Specific Settings
    algorithm_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        self._validate_configuration()
        self._setup_algorithm_defaults()
    
    def _validate_configuration(self):
        """Validate configuration settings for consistency and security"""
        # Validate environment-specific requirements
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.security.encryption_key:
                raise ValueError("Encryption key is required for production environment")
            if not self.security.jwt_secret_key:
                raise ValueError("JWT secret key is required for production environment")
        
        # Validate AI model settings
        if self.ai_models.batch_size <= 0:
            raise ValueError("AI batch size must be positive")
        
        # Validate performance settings
        if self.performance.max_response_time_ms <= 0:
            raise ValueError("Max response time must be positive")
        
        logger.info(f"Configuration validated for {self.environment.value} environment")
    
    def _setup_algorithm_defaults(self):
        """Setup default configurations for specific algorithms"""
        self.algorithm_settings.update({
            "content_protection": {
                "detection_threshold": 0.95,
                "scan_interval_hours": 24,
                "blockchain_logging": True
            },
            "revenue_optimization": {
                "price_update_frequency_hours": 6,
                "market_analysis_depth": "deep",
                "roi_calculation_window_days": 30
            },
            "collaboration_matching": {
                "compatibility_threshold": 0.8,
                "network_analysis_depth": 3,
                "recommendation_count": 10
            },
            "emotional_intelligence": {
                "sentiment_confidence_threshold": 0.9,
                "emotion_tracking_enabled": True,
                "mood_prediction_window_hours": 48
            },
            "platform_integration": {
                "sync_frequency_minutes": 15,
                "platform_count_limit": 25,
                "cross_platform_analytics": True
            },
            "workflow_optimization": {
                "automation_level": "advanced",
                "efficiency_target_percent": 95,
                "process_monitoring": True
            }
        })
    
    def get_algorithm_config(self, algorithm_name: str) -> Dict[str, Any]:
        """Get configuration for a specific algorithm"""



        return self.algorithm_settings.get(algorithm_name, {})
    
    def update_algorithm_config(self, algorithm_name: str, config: Dict[str, Any]):
        """Update configuration for a specific algorithm"""
        if algorithm_name not in self.algorithm_settings:
            self.algorithm_settings[algorithm_name] = {}
        self.algorithm_settings[algorithm_name].update(config)
        logger.info(f"Updated configuration for algorithm: {algorithm_name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format"""
        config_dict = {}
        for field_name, field_value in self.__dict__.items():
            if hasattr(field_value, '__dict__'):
                config_dict[field_name] = field_value.__dict__
            else:
                config_dict[field_name] = field_value
        return config_dict
    
    def to_json(self) -> str:
        """Convert configuration to JSON string"""



        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'IntelligenceAlgorithmsConfig':
        """Create configuration from JSON string"""
        config_data = json.loads(json_str)
        return cls(**config_data)
    
    @classmethod
    def from_file(cls, config_file_path: str) -> 'IntelligenceAlgorithmsConfig':
        """Load configuration from file"""
        with open(config_file_path, 'r') as f:
            if config_file_path.endswith('.json'):
                config_data = json.load(f)
            else:
                # Support for other formats like YAML can be added here
                raise ValueError("Unsupported configuration file format")
        return cls(**config_data)
    
    def save_to_file(self, config_file_path: str):
        """Save configuration to file"""
        with open(config_file_path, 'w') as f:
            if config_file_path.endswith('.json'):
                json.dump(self.to_dict(), f, indent=2, default=str)
            else:
                raise ValueError("Unsupported configuration file format")
        logger.info(f"Configuration saved to: {config_file_path}")


# Global configuration instance
config = IntelligenceAlgorithmsConfig()

# Configuration factory functions
def get_config() -> IntelligenceAlgorithmsConfig:
    """Get the global configuration instance"""



    return config

def create_config(environment: str = None, **kwargs) -> IntelligenceAlgorithmsConfig:
    """Create a new configuration instance with custom settings"""
    if environment:
        kwargs['environment'] = EnvironmentType(environment)
    return IntelligenceAlgorithmsConfig(**kwargs)

def load_config_from_environment() -> IntelligenceAlgorithmsConfig:
    """Load configuration from environment variables"""



    return IntelligenceAlgorithmsConfig()

def load_config_from_file(file_path: str) -> IntelligenceAlgorithmsConfig:
    """Load configuration from file"""



    return IntelligenceAlgorithmsConfig.from_file(file_path)

# Export configuration components
__all__ = [
    "IntelligenceAlgorithmsConfig",
    "DatabaseConfig",
    "RedisConfig",
    "AIModelConfig",
    "VectorDatabaseConfig",
    "BlockchainConfig",
    "PerformanceConfig",
    "SecurityConfig",
    "MonitoringConfig",
    "EnvironmentType",
    "LogLevel",
    "config",
    "get_config",
    "create_config",
    "load_config_from_environment",
    "load_config_from_file"
]
