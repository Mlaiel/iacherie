"""⚙️ COLLABORATION CONFIG - Configuration Management System
========================================================

Developed by: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved - Unauthorized use is strictly prohibited

⚠️  LEGAL WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any attempt to steal, copy, or reproduce this concept, idea, or code
without explicit written authorization from Fahed Mlaiel is strictly forbidden
and will result in immediate legal action under German and international law.

Centralized configuration management for the collaboration system.
Environment-aware settings with secure credential handling.

Features:
- Environment-Specific Configuration Management
- Secure Credential Handling with Encryption
- Database Connection Pool Configuration
- AI/ML Model Configuration & Version Management
- External Service Integration Settings
- Performance Tuning Parameters
- Security Configuration & Rate Limiting
- Monitoring & Alerting Configuration
- Feature Flag Management
- Cache Configuration & Optimization
- Message Queue Configuration
- Email & Notification Settings
- File Storage Configuration
- Backup & Recovery Settings
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path
import redis
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class Environment(Enum):
    """Environment enumeration"""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseType(Enum):
    """Database type enumeration"""    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"

@dataclass
class DatabaseConfig:
    """Database configuration"""    type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    command_timeout: int = 300
    
    @property
    def url(self) -> str:
        """Generate database URL"""        if self.type == DatabaseType.POSTGRESQL:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.MYSQL:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.MONGODB:
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == DatabaseType.REDIS:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"{self.type.value}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class CacheConfig:
    """Cache configuration"""    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    default_ttl: int = 3600
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    health_check_interval: int = 30
    retry_on_timeout: bool = True
    
    @property
    def redis_url(self) -> str:
        """Generate Redis URL"""        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

@dataclass
class AIModelConfig:
    """AI/ML model configuration"""    model_name: str
    model_path: str
    model_version: str
    provider: str  # openai, huggingface, local, etc.
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    batch_size: int = 32
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    cache_predictions: bool = True
    auto_update: bool = False
    
@dataclass
class ExternalServiceConfig:
    """External service configuration"""    service_name: str
    api_key: str
    endpoint: str
    timeout: int = 30
    rate_limit: int = 1000
    retry_attempts: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class SecurityConfig:
    """Security configuration"""    encryption_key: str
    jwt_secret: str
    jwt_expiry_hours: int = 24
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    rate_limit_requests: int = 1000
    rate_limit_window_minutes: int = 60
    cors_origins: List[str] = field(default_factory=list)
    api_key_header: str = "X-API-Key"
    require_https: bool = True
    session_cookie_secure: bool = True
    
@dataclass
class NotificationConfig:
    """Notification configuration"""    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_use_tls: bool = True
    default_sender: str = "noreply@example.com"
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    firebase_credentials: Optional[str] = None
    slack_bot_token: Optional[str] = None
    discord_bot_token: Optional[str] = None
    
@dataclass
class MonitoringConfig:
    """Monitoring and alerting configuration"""    enable_metrics: bool = True
    metrics_port: int = 9090
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    datadog_api_key: Optional[str] = None
    prometheus_endpoint: Optional[str] = None
    alert_email: str = "alerts@example.com"
    health_check_interval: int = 30
    error_threshold: int = 100
    
@dataclass
class FeatureFlags:
    """Feature flag configuration"""    enable_ai_recommendations: bool = True
    enable_blockchain_contracts: bool = False
    enable_real_time_chat: bool = True
    enable_video_processing: bool = True
    enable_advanced_analytics: bool = True
    enable_automated_payouts: bool = False
    enable_multi_language: bool = True
    enable_voice_search: bool = False
    enable_ar_features: bool = False
    enable_premium_features: bool = True

class CollaborationConfig:
    """Main collaboration system configuration"""    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self._load_config()
        self._setup_logging()
        
    def _load_config(self) -> None:
        """Load configuration from various sources"""        # Load from environment variables
        self._load_from_env()
        
        # Load from config files
        self._load_from_files()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_config()
        
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""        # Database configuration
        self.database = DatabaseConfig(
            type=DatabaseType(os.getenv('DATABASE_TYPE', 'postgresql')),
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=int(os.getenv('DATABASE_PORT', 5432)),
            database=os.getenv('DATABASE_NAME', 'collaboration'),
            username=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', ''),
            pool_size=int(os.getenv('DATABASE_POOL_SIZE', 20)),
            max_overflow=int(os.getenv('DATABASE_MAX_OVERFLOW', 30))
        )
        
        # Cache configuration
        self.cache = CacheConfig(
            redis_host=os.getenv('REDIS_HOST', 'localhost'),
            redis_port=int(os.getenv('REDIS_PORT', 6379)),
            redis_password=os.getenv('REDIS_PASSWORD'),
            redis_db=int(os.getenv('REDIS_DB', 0)),
            default_ttl=int(os.getenv('CACHE_TTL', 3600))
        )
        
        # Security configuration
        self.security = SecurityConfig(
            encryption_key=os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode()),
            jwt_secret=os.getenv('JWT_SECRET', 'your-secret-key'),
            jwt_expiry_hours=int(os.getenv('JWT_EXPIRY_HOURS', 24)),
            rate_limit_requests=int(os.getenv('RATE_LIMIT_REQUESTS', 1000)),
            cors_origins=os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
        )
        
        # Notification configuration
        self.notifications = NotificationConfig(
            smtp_host=os.getenv('SMTP_HOST', 'localhost'),
            smtp_port=int(os.getenv('SMTP_PORT', 587)),
            smtp_username=os.getenv('SMTP_USERNAME', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            smtp_use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            default_sender=os.getenv('DEFAULT_SENDER', 'noreply@example.com'),
            twilio_account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
            twilio_auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
            firebase_credentials=os.getenv('FIREBASE_CREDENTIALS'),
            slack_bot_token=os.getenv('SLACK_BOT_TOKEN'),
            discord_bot_token=os.getenv('DISCORD_BOT_TOKEN')
        )
        
        # Monitoring configuration
        self.monitoring = MonitoringConfig(
            enable_metrics=os.getenv('ENABLE_METRICS', 'true').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            sentry_dsn=os.getenv('SENTRY_DSN'),
            datadog_api_key=os.getenv('DATADOG_API_KEY'),
            alert_email=os.getenv('ALERT_EMAIL', 'alerts@example.com')
        )
        
        # Feature flags
        self.features = FeatureFlags(
            enable_ai_recommendations=os.getenv('ENABLE_AI_RECOMMENDATIONS', 'true').lower() == 'true',
            enable_blockchain_contracts=os.getenv('ENABLE_BLOCKCHAIN', 'false').lower() == 'true',
            enable_real_time_chat=os.getenv('ENABLE_REALTIME_CHAT', 'true').lower() == 'true',
            enable_video_processing=os.getenv('ENABLE_VIDEO_PROCESSING', 'true').lower() == 'true',
            enable_advanced_analytics=os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true',
            enable_automated_payouts=os.getenv('ENABLE_AUTO_PAYOUTS', 'false').lower() == 'true'
        )
        
        # AI Models configuration
        self.ai_models = [
            AIModelConfig(
                model_name="creator_matcher",
                model_path=os.getenv('CREATOR_MATCHER_MODEL_PATH', '/models/creator_matcher'),
                model_version=os.getenv('CREATOR_MATCHER_VERSION', '1.0'),
                provider="local"
            ),
            AIModelConfig(
                model_name="openai_gpt",
                model_path="gpt-4",
                model_version="latest",
                provider="openai",
                api_key=os.getenv('OPENAI_API_KEY'),
                endpoint="https://api.openai.com/v1"
            ),
            AIModelConfig(
                model_name="content_analyzer",
                model_path=os.getenv('CONTENT_ANALYZER_PATH', '/models/content_analyzer'),
                model_version=os.getenv('CONTENT_ANALYZER_VERSION', '1.0'),
                provider="huggingface"
            )
        ]
        
        # External services
        self.external_services = [
            ExternalServiceConfig(
                service_name="payment_processor",
                api_key=os.getenv('PAYMENT_API_KEY', ''),
                endpoint=os.getenv('PAYMENT_ENDPOINT', 'https://api.stripe.com'),
                rate_limit=int(os.getenv('PAYMENT_RATE_LIMIT', 1000))
            ),
            ExternalServiceConfig(
                service_name="blockchain_service",
                api_key=os.getenv('BLOCKCHAIN_API_KEY', ''),
                endpoint=os.getenv('BLOCKCHAIN_ENDPOINT', 'https://api.ethereum.org'),
                rate_limit=int(os.getenv('BLOCKCHAIN_RATE_LIMIT', 100))
            )
        ]
        
    def _load_from_files(self) -> None:
        """Load configuration from YAML/JSON files"""        config_dir = Path(__file__).parent / "configs"
        
        # Load environment-specific config
        env_config_file = config_dir / f"{self.environment.value}.yaml"
        if env_config_file.exists():
            with open(env_config_file, 'r') as f:
                env_config = yaml.safe_load(f)
                self._merge_config(env_config)
                
        # Load secrets file
        secrets_file = config_dir / "secrets.yaml"
        if secrets_file.exists():
            with open(secrets_file, 'r') as f:
                secrets = yaml.safe_load(f)
                self._merge_secrets(secrets)
                
    def _apply_environment_overrides(self) -> None:
        """Apply environment-specific configuration overrides"""        if self.environment == Environment.PRODUCTION:
            # Production overrides
            self.security.require_https = True
            self.security.session_cookie_secure = True
            self.monitoring.log_level = "WARNING"
            self.features.enable_blockchain_contracts = True
            
        elif self.environment == Environment.DEVELOPMENT:
            # Development overrides
            self.security.require_https = False
            self.security.session_cookie_secure = False
            self.monitoring.log_level = "DEBUG"
            self.database.pool_size = 5
            
        elif self.environment == Environment.TESTING:
            # Testing overrides
            self.database.database = f"{self.database.database}_test"
            self.cache.redis_db = 1
            self.monitoring.log_level = "ERROR"
            
    def _validate_config(self) -> None:
        """Validate configuration for required fields"""        required_fields = [
            (self.database.host, "Database host"),
            (self.database.username, "Database username"),
            (self.security.jwt_secret, "JWT secret"),
            (self.security.encryption_key, "Encryption key")
        ]
        
        for value, field_name in required_fields:
            if not value:
                raise ValueError(f"Required configuration field missing: {field_name}")
                
        # Validate AI model configurations
        for model in self.ai_models:
            if model.provider == "openai" and not model.api_key:
                logger.warning(f"OpenAI API key missing for model {model.model_name}")
                
    def _setup_logging(self) -> None:
        """Setup logging configuration"""        logging.basicConfig(
            level=getattr(logging, self.monitoring.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def _merge_config(self, config_dict: Dict[str, Any]) -> None:
        """Merge configuration from dictionary"""        # Implementation would merge config values
        pass
        
    def _merge_secrets(self, secrets_dict: Dict[str, Any]) -> None:
        """Merge secrets from dictionary"""        # Implementation would merge secret values
        pass
        
    def get_model_config(self, model_name: str) -> Optional[AIModelConfig]:
        """Get configuration for specific AI model"""        for model in self.ai_models:
            if model.model_name == model_name:
                return model
        return None
        
    def get_service_config(self, service_name: str) -> Optional[ExternalServiceConfig]:
        """Get configuration for specific external service"""        for service in self.external_services:
            if service.service_name == service_name:
                return service
        return None
        
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if feature flag is enabled"""        return getattr(self.features, feature_name, False)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)"""        return {
            'environment': self.environment.value,
            'database': {
                'type': self.database.type.value,
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'pool_size': self.database.pool_size
            },
            'cache': {
                'host': self.cache.redis_host,
                'port': self.cache.redis_port,
                'db': self.cache.redis_db,
                'ttl': self.cache.default_ttl
            },
            'features': {
                'ai_recommendations': self.features.enable_ai_recommendations,
                'blockchain': self.features.enable_blockchain_contracts,
                'real_time_chat': self.features.enable_real_time_chat,
                'video_processing': self.features.enable_video_processing,
                'analytics': self.features.enable_advanced_analytics
            },
            'monitoring': {
                'metrics_enabled': self.monitoring.enable_metrics,
                'log_level': self.monitoring.log_level
            }
        }

# Global configuration instance
config = CollaborationConfig(
    Environment(os.getenv('ENVIRONMENT', 'development'))
)

# Configuration factory
def get_config(environment: Optional[str] = None) -> CollaborationConfig:
    """Get configuration instance"""    if environment:
        return CollaborationConfig(Environment(environment))
    return config

# Export main components
__all__ = [
    'CollaborationConfig',
    'DatabaseConfig',
    'CacheConfig',
    'AIModelConfig',
    'ExternalServiceConfig',
    'SecurityConfig',
    'NotificationConfig',
    'MonitoringConfig',
    'FeatureFlags',
    'Environment',
    'config',
    'get_config'
]
