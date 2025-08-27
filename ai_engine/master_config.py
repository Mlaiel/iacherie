"""
Ultra-Industrial AI Module Master Configuration
IA-Influencer-Agent | Enterprise Content Protection Platform

Master configuration system for all AI module components and services.

© 2025 Fahed Mlaiel. All Rights Reserved.
Contact: mlaiel@live.de

⚠️ STRICT COPYRIGHT WARNING ⚠️
This configuration system contains proprietary settings and algorithms.
Unauthorized use is strictly prohibited.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import yaml

# Configure logging
logger = logging.getLogger(__name__)

class EnvironmentType(Enum):
    """Environment type enumeration"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(Enum):
    """Log level enumeration"""
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
    database: str = "ia_influencer_agent"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    health_check_interval: int = 30
    max_connections: int = 50

@dataclass
class AIModelsConfig:
    """AI models configuration"""
    model_cache_dir: str = "./models/cache"
    max_model_memory: int = 4096  # MB
    model_timeout: int = 300  # seconds
    auto_download: bool = True
    model_versions: Dict[str, str] = field(default_factory=lambda: {
        "bert_base": "bert-base-uncased",
        "gpt_model": "gpt-3.5-turbo",
        "vision_model": "clip-vit-base-patch32",
        "audio_model": "wav2vec2-base-960h"
    })
    api_keys: Dict[str, str] = field(default_factory=dict)

@dataclass
class ContentProtectionConfig:
    """Content protection configuration"""
    fingerprint_algorithm: str = "perceptual_hash"
    similarity_threshold: float = 0.85
    blockchain_enabled: bool = True
    watermark_strength: float = 0.3
    protection_levels: List[str] = field(default_factory=lambda: [
        "basic", "standard", "enterprise", "ultra"
    ])
    copyright_detection: bool = True
    dmca_compliance: bool = True

@dataclass
class PerformanceConfig:
    """Performance configuration"""
    max_concurrent_operations: int = 100
    request_timeout: int = 300
    cache_ttl: int = 3600
    batch_size: int = 32
    memory_limit: int = 8192  # MB
    cpu_cores: Optional[int] = None  # Auto-detect
    gpu_enabled: bool = True
    optimization_level: str = "balanced"  # conservative, balanced, aggressive

@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_algorithm: str = "AES-256-GCM"
    jwt_secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    jwt_expiration: int = 86400  # 24 hours
    rate_limiting: bool = True
    max_requests_per_minute: int = 1000
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    security_headers: bool = True
    audit_logging: bool = True

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    metrics_enabled: bool = True
    logging_level: LogLevel = LogLevel.INFO
    log_rotation: bool = True
    max_log_size: int = 100  # MB
    log_retention_days: int = 30
    health_check_interval: int = 60
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 85.0,
        "disk_usage": 90.0,
        "response_time": 2.0,
        "error_rate": 0.05
    })

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    spotify_api_key: Optional[str] = None
    youtube_api_key: Optional[str] = None
    instagram_api_key: Optional[str] = None
    tiktok_api_key: Optional[str] = None
    twitter_api_key: Optional[str] = None
    webhook_urls: Dict[str, str] = field(default_factory=dict)
    external_apis: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class AIModuleMasterConfig:
    """
    Ultra-Industrial AI Module Master Configuration
    
    Central configuration management system for all AI module components.
    Provides environment-specific configurations and runtime settings.
    """
    
    def __init__(self, environment: EnvironmentType = EnvironmentType.DEVELOPMENT):
        """Initialize master configuration"""
        self.environment = environment
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize all configurations
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.ai_models = AIModelsConfig()
        self.content_protection = ContentProtectionConfig()
        self.performance = PerformanceConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.integration = IntegrationConfig()
        
        # Load environment-specific configurations
        self._load_environment_config()
        self._load_secrets()
        
        logger.info(f"AI Module Master Configuration initialized for {environment.value}")
    
    def _load_environment_config(self):
        """Load environment-specific configuration"""
        config_file = self.config_dir / f"config.{self.environment.value}.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    env_config = yaml.safe_load(f)
                
                # Update configurations with environment-specific values
                self._update_config_from_dict(env_config)
                
                logger.info(f"Loaded environment config from {config_file}")
                
            except Exception as e:
                logger.warning(f"Failed to load environment config: {e}")
        else:
            logger.info(f"No environment config file found for {self.environment.value}")
    
    def _load_secrets(self):
        """Load secrets from environment variables or secure storage"""
        # Database secrets
        if os.getenv('DATABASE_PASSWORD'):
            self.database.password = os.getenv('DATABASE_PASSWORD')
        
        # Redis secrets
        if os.getenv('REDIS_PASSWORD'):
            self.redis.password = os.getenv('REDIS_PASSWORD')
        
        # Security secrets
        if os.getenv('JWT_SECRET_KEY'):
            self.security.jwt_secret_key = os.getenv('JWT_SECRET_KEY')
        
        # API keys
        api_key_mapping = {
            'OPENAI_API_KEY': 'openai',
            'SPOTIFY_API_KEY': 'spotify',
            'YOUTUBE_API_KEY': 'youtube',
            'INSTAGRAM_API_KEY': 'instagram',
            'TIKTOK_API_KEY': 'tiktok',
            'TWITTER_API_KEY': 'twitter'
        }
        
        for env_var, key_name in api_key_mapping.items():
            if os.getenv(env_var):
                if key_name in ['openai']:
                    self.ai_models.api_keys[key_name] = os.getenv(env_var)
                else:
                    setattr(self.integration, f"{key_name}_api_key", os.getenv(env_var))
    
    def _update_config_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary"""
        for section, values in config_dict.items():
            if hasattr(self, section) and isinstance(values, dict):
                config_obj = getattr(self, section)
                for key, value in values.items():
                    if hasattr(config_obj, key):
                        setattr(config_obj, key, value)
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return (
            f"postgresql://{self.database.username}:{self.database.password}@"
            f"{self.database.host}:{self.database.port}/{self.database.database}"
        )
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL"""
        auth = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth}{self.redis.host}:{self.redis.port}/{self.redis.db}"
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                }
            },
            'handlers': {
                'default': {
                    'level': self.monitoring.logging_level.value,
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'level': self.monitoring.logging_level.value,
                    'formatter': 'detailed',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'ai_module.log',
                    'maxBytes': self.monitoring.max_log_size * 1024 * 1024,
                    'backupCount': 5
                }
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['default', 'file'],
                    'level': self.monitoring.logging_level.value,
                    'propagate': False
                }
            }
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration"""
        return {
            'allow_origins': self.security.allowed_origins,
            'allow_credentials': True,
            'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['*']
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate database configuration
        if not self.database.password and self.environment == EnvironmentType.PRODUCTION:
            issues.append("Database password is required in production")
        
        # Validate security configuration
        if self.security.jwt_secret_key == "CHANGE_THIS_IN_PRODUCTION" and self.environment == EnvironmentType.PRODUCTION:
            issues.append("JWT secret key must be changed in production")
        
        # Validate API keys
        if not self.ai_models.api_keys.get('openai') and self.environment == EnvironmentType.PRODUCTION:
            issues.append("OpenAI API key is required for AI operations")
        
        # Validate performance settings
        if self.performance.max_concurrent_operations < 1:
            issues.append("Max concurrent operations must be at least 1")
        
        # Validate monitoring settings
        if self.monitoring.alert_thresholds.get('cpu_usage', 0) > 100:
            issues.append("CPU usage threshold cannot exceed 100%")
        
        return issues
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        config_dict = {
            'environment': self.environment.value,
            'database': self._dataclass_to_dict(self.database, include_secrets),
            'redis': self._dataclass_to_dict(self.redis, include_secrets),
            'ai_models': self._dataclass_to_dict(self.ai_models, include_secrets),
            'content_protection': self._dataclass_to_dict(self.content_protection, include_secrets),
            'performance': self._dataclass_to_dict(self.performance, include_secrets),
            'security': self._dataclass_to_dict(self.security, include_secrets),
            'monitoring': self._dataclass_to_dict(self.monitoring, include_secrets),
            'integration': self._dataclass_to_dict(self.integration, include_secrets)
        }
        
        return config_dict
    
    def save_config_template(self, file_path: Optional[str] = None):
        """Save configuration template file"""
        if file_path is None:
            file_path = self.config_dir / f"config.{self.environment.value}.template.yaml"
        
        config_dict = self.export_config(include_secrets=False)
        
        with open(file_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration template saved to {file_path}")
    
    def _dataclass_to_dict(self, config_obj, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert dataclass to dictionary"""
        result = {}
        
        for field_name in dir(config_obj):
            if not field_name.startswith('_'):
                value = getattr(config_obj, field_name)
                
                # Skip sensitive fields if not including secrets
                if not include_secrets and self._is_sensitive_field(field_name, value):
                    if isinstance(value, str):
                        result[field_name] = "***HIDDEN***"
                    elif isinstance(value, dict):
                        result[field_name] = {k: "***HIDDEN***" for k in value.keys()}
                    else:
                        result[field_name] = "***HIDDEN***"
                else:
                    # Convert enum values
                    if hasattr(value, 'value'):
                        result[field_name] = value.value
                    else:
                        result[field_name] = value
        
        return result
    
    def _is_sensitive_field(self, field_name: str, value: Any) -> bool:
        """Check if field contains sensitive information"""
        sensitive_keywords = [
            'password', 'secret', 'key', 'token', 'credential',
            'api_key', 'auth', 'private'
        ]
        
        field_lower = field_name.lower()
        return any(keyword in field_lower for keyword in sensitive_keywords)
    
    @classmethod
    def from_file(cls, config_file: str, environment: EnvironmentType = EnvironmentType.DEVELOPMENT):
        """Create configuration from file"""
        config = cls(environment)
        
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            config._update_config_from_dict(config_data)
            logger.info(f"Configuration loaded from {config_file}")
        else:
            logger.warning(f"Configuration file not found: {config_file}")
        
        return config

# Global configuration instance
master_config = AIModuleMasterConfig()

# Configuration factory functions
def get_config(environment: Optional[EnvironmentType] = None) -> AIModuleMasterConfig:
    """Get configuration for specified environment"""
    if environment is None:
        return master_config
    return AIModuleMasterConfig(environment)

def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return master_config.database

def get_redis_config() -> RedisConfig:
    """Get Redis configuration"""
    return master_config.redis

def get_ai_models_config() -> AIModelsConfig:
    """Get AI models configuration"""
    return master_config.ai_models

def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return master_config.security

def get_monitoring_config() -> MonitoringConfig:
    """Get monitoring configuration"""
    return master_config.monitoring

# Export all configuration classes and functions
__all__ = [
    'AIModuleMasterConfig',
    'DatabaseConfig',
    'RedisConfig',
    'AIModelsConfig',
    'ContentProtectionConfig',
    'PerformanceConfig',
    'SecurityConfig',
    'MonitoringConfig',
    'IntegrationConfig',
    'EnvironmentType',
    'LogLevel',
    'master_config',
    'get_config',
    'get_database_config',
    'get_redis_config',
    'get_ai_models_config',
    'get_security_config',
    'get_monitoring_config'
]

# Initialize logging with configuration
logging.config.dictConfig(master_config.get_logging_config())

logger.info("Ultra-Industrial AI Module Master Configuration system loaded")
logger.info(f"Environment: {master_config.environment.value}")
logger.info(f"Configuration validated with {len(master_config.validate_configuration())} issues")
