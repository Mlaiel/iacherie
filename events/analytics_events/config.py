"""Analytics Events Configuration Module

Ultra-advanced configuration management for analytics events with
ML model parameters, performance thresholds, and optimization settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import os


class AnalyticsEnvironment(Enum):
    """
Analytics environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class MLModelType(Enum):
    """Machine learning model types"""

    ENGAGEMENT_PREDICTOR = "engagement_predictor"
    REVENUE_FORECASTER = "revenue_forecaster"
    COLLABORATION_MATCHER = "collaboration_matcher"
    CONTENT_OPTIMIZER = "content_optimizer"
    TREND_DETECTOR = "trend_detector"
    ANOMALY_DETECTOR = "anomaly_detector"


@dataclass
class DatabaseConfig:
    """Database configuration for analytics"""
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer_analytics"
    username: str = "analytics_user"
    password: str = "secure_password"
    pool_size: int = 20
    max_overflow: int = 50
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_mode: str = "require"


@dataclass
class CacheConfig:
    """Cache configuration for analytics"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 50
    socket_timeout: int = 30
    socket_connect_timeout: int = 10
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class MLModelConfig:
    """Machine learning model configuration"""
    model_type: MLModelType
    model_path: str
    input_features: List[str]
    output_features: List[str]
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    model_version: str = "1.0.0"
    retrain_frequency_hours: int = 24
    performance_threshold: float = 0.85
    drift_detection_enabled: bool = True
    auto_retrain_enabled: bool = True


@dataclass
class PerformanceThresholds:
    """Performance thresholds for analytics alerts"""
    # Engagement thresholds
    engagement_rate_low: float = 0.02
    engagement_rate_high: float = 0.15
    engagement_growth_alert: float = 0.50  # 50% growth trigger
    
    # Revenue thresholds
    revenue_drop_alert: float = 0.20  # 20% drop
    revenue_spike_multiplier: float = 3.0  # 3x average
    revenue_forecast_accuracy: float = 0.90
    
    # Protection thresholds
    fingerprint_accuracy_min: float = 0.85
    violation_response_time_max: int = 300  # 5 minutes
    false_positive_rate_max: float = 0.10
    
    # Collaboration thresholds
    compatibility_score_min: float = 0.70
    success_probability_min: float = 0.60
    
    # System performance thresholds
    api_response_time_max: float = 2.0  # seconds
    database_query_time_max: float = 1.0  # seconds
    cache_hit_rate_min: float = 0.80
    cpu_usage_max: float = 0.80
    memory_usage_max: float = 0.85


@dataclass
class StreamingConfig:
    """
Real-time streaming configuration"""
    kafka_brokers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    kafka_topics: Dict[str, str] = field(default_factory=lambda: {
        "engagement_events": "analytics.engagement",
        "revenue_events": "analytics.revenue",
        "protection_events": "analytics.protection",
        "collaboration_events": "analytics.collaboration"
    })
    batch_size: int = 100
    flush_interval_ms: int = 1000
    compression_type: str = "gzip"
    acks: str = "all"
    retries: int = 3
    retry_backoff_ms: int = 100
    consumer_group_id: str = "analytics_processors"
    auto_offset_reset: str = "latest"
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000


@dataclass
class SecurityConfig:
    """Security configuration for analytics"""
    encryption_key: str = "analytics_encryption_key_2025"
    jwt_secret: str = "analytics_jwt_secret_secure"
    jwt_expiration_hours: int = 24
    api_rate_limit_per_minute: int = 1000
    api_rate_limit_burst: int = 100
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_enabled: bool = True
    csrf_protection: bool = True
    content_security_policy: bool = True
    audit_logging: bool = True
    data_retention_days: int = 2555  # 7 years
    gdpr_compliance: bool = True
    anonymization_enabled: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    prometheus_enabled: bool = True
    prometheus_port: int = 8000
    metrics_collection_interval: int = 30  # seconds
    log_level: str = "INFO"
    log_format: str = "json"
    distributed_tracing: bool = True
    jaeger_endpoint: str = "http://localhost:14268/api/traces"
    health_check_endpoint: str = "/health"
    metrics_endpoint: str = "/metrics"
    alert_manager_enabled: bool = True
    alert_webhook_url: str = "http://localhost:9093/api/v1/alerts"


@dataclass
class OptimizationConfig:
    """Optimization configuration for analytics"""
    auto_scaling_enabled: bool = True
    min_replicas: int = 2
    max_replicas: int = 20
    target_cpu_utilization: float = 0.70
    target_memory_utilization: float = 0.80
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    
    # Query optimization
    query_cache_enabled: bool = True
    query_cache_ttl: int = 300
    connection_pooling: bool = True
    prepared_statements: bool = True
    batch_processing: bool = True
    async_processing: bool = True
    
    # ML optimization
    model_caching: bool = True
    feature_caching: bool = True
    prediction_caching: bool = True
    model_quantization: bool = True
    gpu_acceleration: bool = True


@dataclass
class IntegrationConfig:
    """
Third-party integration configuration"""
    # Payment processors
    stripe_api_key: str = "sk_test_..."
    stripe_webhook_secret: str = "whsec_..."
    paypal_client_id: str = "paypal_client_id"
    paypal_client_secret: str = "paypal_client_secret"
    
    # Platform APIs
    youtube_api_key: str = "youtube_api_key"
    instagram_api_key: str = "instagram_api_key"
    tiktok_api_key: str = "tiktok_api_key"
    spotify_client_id: str = "spotify_client_id"
    spotify_client_secret: str = "spotify_client_secret"
    
    # Cloud services
    aws_access_key: str = "aws_access_key"
    aws_secret_key: str = "aws_secret_key"
    aws_region: str = "eu-central-1"
    s3_bucket: str = "ia-influencer-analytics"
    
    # External APIs
    openai_api_key: str = "openai_api_key"
    huggingface_api_key: str = "huggingface_api_key"
    
    # Rate limiting for external APIs
    api_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "youtube": 10000,  # requests per day
        "instagram": 200,  # requests per hour
        "tiktok": 100,     # requests per hour
        "spotify": 100,    # requests per hour
    })


class AnalyticsConfig:
    """Main analytics configuration class"""
    
    def __init__(self, environment: AnalyticsEnvironment = AnalyticsEnvironment.DEVELOPMENT):
        self.environment = environment
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.streaming = StreamingConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.optimization = OptimizationConfig()
        self.integrations = IntegrationConfig()
        self.thresholds = PerformanceThresholds()
        
        # ML model configurations
        self.ml_models = {
            MLModelType.ENGAGEMENT_PREDICTOR: MLModelConfig(
                model_type=MLModelType.ENGAGEMENT_PREDICTOR,
                model_path="/models/engagement_predictor",
                input_features=[
                    "user_demographics", "content_features", "platform_data",
                    "historical_engagement", "timing_features"
                ],
                output_features=["engagement_probability", "engagement_score"],
                batch_size=64,
                learning_rate=0.001
            ),
            MLModelType.REVENUE_FORECASTER: MLModelConfig(
                model_type=MLModelType.REVENUE_FORECASTER,
                model_path="/models/revenue_forecaster",
                input_features=[
                    "historical_revenue", "market_trends", "creator_metrics",
                    "seasonal_patterns", "external_factors"
                ],
                output_features=["revenue_forecast", "confidence_interval"],
                batch_size=32,
                learning_rate=0.0005
            ),
            MLModelType.COLLABORATION_MATCHER: MLModelConfig(
                model_type=MLModelType.COLLABORATION_MATCHER,
                model_path="/models/collaboration_matcher",
                input_features=[
                    "creator_profiles", "audience_overlap", "content_similarity",
                    "performance_metrics", "collaboration_history"
                ],
                output_features=["compatibility_score", "success_probability"],
                batch_size=16,
                learning_rate=0.002
            ),
            MLModelType.CONTENT_OPTIMIZER: MLModelConfig(
                model_type=MLModelType.CONTENT_OPTIMIZER,
                model_path="/models/content_optimizer",
                input_features=[
                    "content_features", "audience_preferences", "platform_algorithms",
                    "trending_topics", "creator_style"
                ],
                output_features=["optimization_score", "recommendations"],
                batch_size=64,
                learning_rate=0.001
            ),
            MLModelType.TREND_DETECTOR: MLModelConfig(
                model_type=MLModelType.TREND_DETECTOR,
                model_path="/models/trend_detector",
                input_features=[
                    "content_virality", "engagement_velocity", "social_signals",
                    "platform_features", "temporal_patterns"
                ],
                output_features=["trend_probability", "viral_potential"],
                batch_size=128,
                learning_rate=0.0008
            ),
            MLModelType.ANOMALY_DETECTOR: MLModelConfig(
                model_type=MLModelType.ANOMALY_DETECTOR,
                model_path="/models/anomaly_detector",
                input_features=[
                    "system_metrics", "user_behavior", "performance_indicators",
                    "security_events", "business_metrics"
                ],
                output_features=["anomaly_score", "anomaly_type"],
                batch_size=256,
                learning_rate=0.0005
            )
        }
        
        # Load environment-specific configurations
        self._load_environment_config()
    
    def _load_environment_config(self) -> None:
        """Load environment-specific configuration overrides"""
        if self.environment == AnalyticsEnvironment.PRODUCTION:
            self._load_production_config()
        elif self.environment == AnalyticsEnvironment.STAGING:
            self._load_staging_config()
        elif self.environment == AnalyticsEnvironment.TESTING:
            self._load_testing_config()
    
    def _load_production_config(self) -> None:
        """
Load production environment configuration"""
        # Database configuration
        self.database.host = os.getenv("PROD_DB_HOST", "prod-analytics-db.cluster-xyz.eu-central-1.rds.amazonaws.com")
        self.database.port = int(os.getenv("PROD_DB_PORT", "5432"))
        self.database.database = os.getenv("PROD_DB_NAME", "ia_influencer_analytics_prod")
        self.database.username = os.getenv("PROD_DB_USER", "analytics_prod")
        self.database.password = os.getenv("PROD_DB_PASSWORD", "")
        self.database.pool_size = 50
        self.database.max_overflow = 100
        
        # Cache configuration
        self.cache.redis_host = os.getenv("PROD_REDIS_HOST", "prod-analytics-cache.cluster.cache.amazonaws.com")
        self.cache.redis_port = int(os.getenv("PROD_REDIS_PORT", "6379"))
        self.cache.redis_password = os.getenv("PROD_REDIS_PASSWORD", "")
        self.cache.max_connections = 100
        
        # Security configuration
        self.security.encryption_key = os.getenv("PROD_ENCRYPTION_KEY", "")
        self.security.jwt_secret = os.getenv("PROD_JWT_SECRET", "")
        self.security.api_rate_limit_per_minute = 2000
        self.security.audit_logging = True
        
        # Monitoring configuration
        self.monitoring.log_level = "INFO"
        self.monitoring.distributed_tracing = True
        self.monitoring.alert_manager_enabled = True
        
        # Optimization configuration
        self.optimization.auto_scaling_enabled = True
        self.optimization.min_replicas = 5
        self.optimization.max_replicas = 50
        self.optimization.gpu_acceleration = True
    
    def _load_staging_config(self) -> None:
        """Load staging environment configuration"""
        # Similar to production but with reduced resources
        self.database.pool_size = 20
        self.cache.max_connections = 50
        self.optimization.min_replicas = 2
        self.optimization.max_replicas = 10
        self.monitoring.log_level = "DEBUG"
    
    def _load_testing_config(self) -> None:
        """Load testing environment configuration"""
        # Minimal configuration for testing
        self.database.database = "ia_influencer_analytics_test"
        self.database.pool_size = 5
        self.cache.redis_db = 15  # Use different Redis DB for testing
        self.optimization.auto_scaling_enabled = False
        self.monitoring.log_level = "DEBUG"
        self.security.audit_logging = False
    
    def get_model_config(self, model_type: MLModelType) -> MLModelConfig:
        """Get configuration for specific ML model"""
        return self.ml_models.get(model_type)
    
    def update_model_config(self, model_type: MLModelType, config: MLModelConfig) -> None:
        """
Update configuration for specific ML model"""
        self.ml_models[model_type] = config
    
    def get_threshold(self, threshold_name: str) -> Any:
        """
Get specific performance threshold"""
        return getattr(self.thresholds, threshold_name, None)
    
    def validate_config(self) -> bool:
        """
Validate configuration completeness and correctness"""
        try:
            # Validate database configuration
            if not all([self.database.host, self.database.database, 
                       self.database.username, self.database.password]):
                return False
            
            # Validate cache configuration
            if not self.cache.redis_host:
                return False
            
            # Validate security configuration
            if not all([self.security.encryption_key, self.security.jwt_secret]):
                return False
            
            # Validate ML model configurations
            for model_config in self.ml_models.values():
                if not all([model_config.model_path, model_config.input_features]):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert configuration to dictionary"""
        return {
            "environment": self.environment.value,
            "database": self.database.__dict__,
            "cache": self.cache.__dict__,
            "streaming": self.streaming.__dict__,
            "security": {k: v for k, v in self.security.__dict__.items() 
                        if not k.endswith('_key') and not k.endswith('_secret')},
            "monitoring": self.monitoring.__dict__,
            "optimization": self.optimization.__dict__,
            "thresholds": self.thresholds.__dict__,
            "ml_models": {model_type.value: config.__dict__ 
                         for model_type, config in self.ml_models.items()}
        }


# Global configuration instance
analytics_config = AnalyticsConfig(
    environment=AnalyticsEnvironment(os.getenv("ANALYTICS_ENV", "development"))
)


# Configuration validation on import
if not analytics_config.validate_config():
    raise ValueError("Invalid analytics configuration detected. Please check your environment variables and configuration files.")
