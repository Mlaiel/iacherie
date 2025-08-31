"""ML Agent Configuration - Advanced Configuration Management System

Industrial-grade configuration management for ML operations, providing centralized
configuration, environment-specific settings, and dynamic configuration updates
for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This configuration system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os
import yaml
import json
from enum import Enum

class Environment(Enum):
    """Deployment environments"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ModelFramework(Enum):
    """Supported ML frameworks"""    SCIKIT_LEARN = "scikit_learn"
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    HUGGINGFACE = "huggingface"

@dataclass
class DatabaseConfig:
    """Database configuration"""    host: str = "localhost"
    port: int = 5432
    database: str = "ml_agent_db"
    username: str = "ml_agent"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    ssl_mode: str = "prefer"

@dataclass
class RedisConfig:
    """Redis configuration"""    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    pool_size: int = 10
    socket_timeout: int = 5
    connection_timeout: int = 5

@dataclass
class S3Config:
    """S3 storage configuration"""    bucket_name: str = "ml-models"
    access_key: str = ""
    secret_key: str = ""
    region: str = "us-east-1"
    endpoint_url: Optional[str] = None
    use_ssl: bool = True

@dataclass
class MLFlowConfig:
    """MLflow configuration"""    tracking_uri: str = "http://localhost:5000"
    artifact_root: str = "s3://ml-experiments"
    experiment_name: str = "default"
    registry_uri: Optional[str] = None

@dataclass
class TrainingConfig:
    """Model training configuration"""    default_validation_split: float = 0.2
    default_test_split: float = 0.1
    default_cross_validation_folds: int = 5
    default_random_seed: int = 42
    max_training_time_hours: int = 24
    early_stopping_patience: int = 10
    checkpoint_interval: int = 1000
    supported_frameworks: List[ModelFramework] = field(
        default_factory=lambda: [
            ModelFramework.SCIKIT_LEARN,
            ModelFramework.TENSORFLOW,
            ModelFramework.PYTORCH
        ]
    )

@dataclass
class InferenceConfig:
    """Model inference configuration"""    max_batch_size: int = 32
    default_timeout: int = 30
    max_concurrent_requests: int = 100
    caching_enabled: bool = True
    cache_ttl_seconds: int = 3600
    gpu_enabled: bool = False
    cpu_threads: int = 4
    memory_limit_mb: int = 2048

@dataclass
class DeploymentConfig:
    """Model deployment configuration"""    default_replicas: int = 2
    max_replicas: int = 10
    cpu_request: str = "500m"
    cpu_limit: str = "2000m"
    memory_request: str = "1Gi"
    memory_limit: str = "4Gi"
    health_check_path: str = "/health"
    metrics_path: str = "/metrics"
    container_registry: str = "docker.io"
    image_pull_policy: str = "Always"

@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""    enabled: bool = True
    metrics_collection_interval: int = 60  # seconds
    drift_detection_enabled: bool = True
    drift_check_interval: int = 3600  # 1 hour
    quality_analysis_enabled: bool = True
    quality_check_interval: int = 1800  # 30 minutes
    alerting_enabled: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    retention_days: int = 30

@dataclass
class SecurityConfig:
    """Security configuration"""    encryption_enabled: bool = True
    jwt_secret_key: str = "your-secret-key-here"
    token_expiration_hours: int = 24
    api_rate_limit: int = 1000  # requests per hour
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    ssl_verify: bool = True
    audit_logging_enabled: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    json_logging: bool = False
    structured_logging: bool = True

@dataclass
class MLAgentConfig:
    """Complete ML Agent configuration"""    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    s3: S3Config = field(default_factory=S3Config)
    mlflow: MLFlowConfig = field(default_factory=MLFlowConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Additional settings
    feature_store_enabled: bool = False
    experiment_tracking_enabled: bool = True
    model_versioning_enabled: bool = True
    pipeline_orchestration_enabled: bool = True
    auto_scaling_enabled: bool = True
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'MLAgentConfig':
        """Load configuration from file"""        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MLAgentConfig':
        """Create configuration from dictionary"""        config = cls()
        
        # Update configuration fields
        for key, value in config_dict.items():
            if hasattr(config, key):
                if isinstance(getattr(config, key), type(value)):
                    setattr(config, key, value)
                elif hasattr(getattr(config, key), '__dict__'):
                    # Handle nested configuration objects
                    nested_config = getattr(config, key)
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            if hasattr(nested_config, nested_key):
                                setattr(nested_config, nested_key, nested_value)
        
        return config
    
    @classmethod
    def from_environment(cls) -> 'MLAgentConfig':
        """Create configuration from environment variables"""        config = cls()
        
        # Environment
        if os.getenv('ML_ENVIRONMENT'):
            config.environment = Environment(os.getenv('ML_ENVIRONMENT'))
        
        config.debug = os.getenv('ML_DEBUG', 'false').lower() == 'true'
        
        # Database configuration
        if os.getenv('DATABASE_HOST'):
            config.database.host = os.getenv('DATABASE_HOST')
        if os.getenv('DATABASE_PORT'):
            config.database.port = int(os.getenv('DATABASE_PORT'))
        if os.getenv('DATABASE_NAME'):
            config.database.database = os.getenv('DATABASE_NAME')
        if os.getenv('DATABASE_USER'):
            config.database.username = os.getenv('DATABASE_USER')
        if os.getenv('DATABASE_PASSWORD'):
            config.database.password = os.getenv('DATABASE_PASSWORD')
        
        # Redis configuration
        if os.getenv('REDIS_HOST'):
            config.redis.host = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            config.redis.port = int(os.getenv('REDIS_PORT'))
        if os.getenv('REDIS_PASSWORD'):
            config.redis.password = os.getenv('REDIS_PASSWORD')
        
        # S3 configuration
        if os.getenv('S3_BUCKET'):
            config.s3.bucket_name = os.getenv('S3_BUCKET')
        if os.getenv('S3_ACCESS_KEY'):
            config.s3.access_key = os.getenv('S3_ACCESS_KEY')
        if os.getenv('S3_SECRET_KEY'):
            config.s3.secret_key = os.getenv('S3_SECRET_KEY')
        if os.getenv('S3_REGION'):
            config.s3.region = os.getenv('S3_REGION')
        
        # MLflow configuration
        if os.getenv('MLFLOW_TRACKING_URI'):
            config.mlflow.tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        if os.getenv('MLFLOW_ARTIFACT_ROOT'):
            config.mlflow.artifact_root = os.getenv('MLFLOW_ARTIFACT_ROOT')
        
        # Security configuration
        if os.getenv('JWT_SECRET_KEY'):
            config.security.jwt_secret_key = os.getenv('JWT_SECRET_KEY')
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        return {
            'environment': self.environment.value,
            'debug': self.debug,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'username': self.database.username,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
                'ssl_mode': self.database.ssl_mode
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'database': self.redis.database,
                'pool_size': self.redis.pool_size,
                'socket_timeout': self.redis.socket_timeout,
                'connection_timeout': self.redis.connection_timeout
            },
            's3': {
                'bucket_name': self.s3.bucket_name,
                'region': self.s3.region,
                'endpoint_url': self.s3.endpoint_url,
                'use_ssl': self.s3.use_ssl
            },
            'mlflow': {
                'tracking_uri': self.mlflow.tracking_uri,
                'artifact_root': self.mlflow.artifact_root,
                'experiment_name': self.mlflow.experiment_name,
                'registry_uri': self.mlflow.registry_uri
            },
            'training': {
                'default_validation_split': self.training.default_validation_split,
                'default_test_split': self.training.default_test_split,
                'default_cross_validation_folds': self.training.default_cross_validation_folds,
                'default_random_seed': self.training.default_random_seed,
                'max_training_time_hours': self.training.max_training_time_hours,
                'early_stopping_patience': self.training.early_stopping_patience,
                'checkpoint_interval': self.training.checkpoint_interval,
                'supported_frameworks': [fw.value for fw in self.training.supported_frameworks]
            },
            'inference': {
                'max_batch_size': self.inference.max_batch_size,
                'default_timeout': self.inference.default_timeout,
                'max_concurrent_requests': self.inference.max_concurrent_requests,
                'caching_enabled': self.inference.caching_enabled,
                'cache_ttl_seconds': self.inference.cache_ttl_seconds,
                'gpu_enabled': self.inference.gpu_enabled,
                'cpu_threads': self.inference.cpu_threads,
                'memory_limit_mb': self.inference.memory_limit_mb
            },
            'deployment': {
                'default_replicas': self.deployment.default_replicas,
                'max_replicas': self.deployment.max_replicas,
                'cpu_request': self.deployment.cpu_request,
                'cpu_limit': self.deployment.cpu_limit,
                'memory_request': self.deployment.memory_request,
                'memory_limit': self.deployment.memory_limit,
                'health_check_path': self.deployment.health_check_path,
                'metrics_path': self.deployment.metrics_path,
                'container_registry': self.deployment.container_registry,
                'image_pull_policy': self.deployment.image_pull_policy
            },
            'monitoring': {
                'enabled': self.monitoring.enabled,
                'metrics_collection_interval': self.monitoring.metrics_collection_interval,
                'drift_detection_enabled': self.monitoring.drift_detection_enabled,
                'drift_check_interval': self.monitoring.drift_check_interval,
                'quality_analysis_enabled': self.monitoring.quality_analysis_enabled,
                'quality_check_interval': self.monitoring.quality_check_interval,
                'alerting_enabled': self.monitoring.alerting_enabled,
                'alert_channels': self.monitoring.alert_channels,
                'retention_days': self.monitoring.retention_days
            },
            'security': {
                'encryption_enabled': self.security.encryption_enabled,
                'token_expiration_hours': self.security.token_expiration_hours,
                'api_rate_limit': self.security.api_rate_limit,
                'allowed_origins': self.security.allowed_origins,
                'ssl_verify': self.security.ssl_verify,
                'audit_logging_enabled': self.security.audit_logging_enabled
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'log_file': self.logging.log_file,
                'max_file_size_mb': self.logging.max_file_size_mb,
                'backup_count': self.logging.backup_count,
                'json_logging': self.logging.json_logging,
                'structured_logging': self.logging.structured_logging
            },
            'feature_store_enabled': self.feature_store_enabled,
            'experiment_tracking_enabled': self.experiment_tracking_enabled,
            'model_versioning_enabled': self.model_versioning_enabled,
            'pipeline_orchestration_enabled': self.pipeline_orchestration_enabled,
            'auto_scaling_enabled': self.auto_scaling_enabled
        }
    
    def save_to_file(self, config_path: Union[str, Path], format: str = 'yaml'):
        """Save configuration to file"""        config_path = Path(config_path)
        config_dict = self.to_dict()
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'yaml':
            with open(config_path, 'w') as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""        errors = []
        
        # Validate database configuration
        if not self.database.host:
            errors.append("Database host is required")
        
        if self.database.port <= 0 or self.database.port > 65535:
            errors.append("Database port must be between 1 and 65535")
        
        # Validate training configuration
        if self.training.default_validation_split < 0 or self.training.default_validation_split >= 1:
            errors.append("Validation split must be between 0 and 1")
        
        if self.training.default_test_split < 0 or self.training.default_test_split >= 1:
            errors.append("Test split must be between 0 and 1")
        
        if (self.training.default_validation_split + self.training.default_test_split) >= 1:
            errors.append("Sum of validation and test splits must be less than 1")
        
        # Validate inference configuration
        if self.inference.max_batch_size <= 0:
            errors.append("Max batch size must be positive")
        
        if self.inference.default_timeout <= 0:
            errors.append("Default timeout must be positive")
        
        # Validate deployment configuration
        if self.deployment.default_replicas <= 0:
            errors.append("Default replicas must be positive")
        
        if self.deployment.max_replicas < self.deployment.default_replicas:
            errors.append("Max replicas must be >= default replicas")
        
        # Validate monitoring configuration
        if self.monitoring.metrics_collection_interval <= 0:
            errors.append("Metrics collection interval must be positive")
        
        if self.monitoring.retention_days <= 0:
            errors.append("Retention days must be positive")
        
        return errors
    
    def is_production(self) -> bool:
        """Check if running in production environment"""        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment"""        return self.environment == Environment.DEVELOPMENT

# Default configuration instance
default_config = MLAgentConfig()

# Environment-specific configurations
development_config = MLAgentConfig(
    environment=Environment.DEVELOPMENT,
    debug=True,
    monitoring=MonitoringConfig(
        drift_check_interval=7200,  # 2 hours
        quality_check_interval=3600,  # 1 hour
        retention_days=7
    )
)

production_config = MLAgentConfig(
    environment=Environment.PRODUCTION,
    debug=False,
    inference=InferenceConfig(
        max_concurrent_requests=500,
        gpu_enabled=True,
        memory_limit_mb=8192
    ),
    deployment=DeploymentConfig(
        default_replicas=3,
        max_replicas=20,
        cpu_limit="4000m",
        memory_limit="8Gi"
    ),
    monitoring=MonitoringConfig(
        metrics_collection_interval=30,
        drift_check_interval=1800,  # 30 minutes
        quality_check_interval=900,  # 15 minutes
        retention_days=90
    ),
    security=SecurityConfig(
        api_rate_limit=5000,
        allowed_origins=[]  # Specific origins only
    )
)

# Configuration factory
def get_config(environment: str = None, config_file: str = None) -> MLAgentConfig:
    """Get configuration based on environment or file"""    
    if config_file:
        return MLAgentConfig.from_file(config_file)
    
    if environment:
        env = Environment(environment.lower())
        if env == Environment.DEVELOPMENT:
            return development_config
        elif env == Environment.PRODUCTION:
            return production_config
        else:
            return default_config
    
    # Try to get from environment variables
    env_str = os.getenv('ML_ENVIRONMENT', 'development').lower()
    try:
        env = Environment(env_str)
        if env == Environment.DEVELOPMENT:
            config = MLAgentConfig.from_environment()
            config.environment = Environment.DEVELOPMENT
            config.debug = True
            return config
        elif env == Environment.PRODUCTION:
            config = MLAgentConfig.from_environment()
            config.environment = Environment.PRODUCTION
            config.debug = False
            return config
        else:
            return MLAgentConfig.from_environment()
    except ValueError:
        return default_config

# Export all components
__all__ = [
    'MLAgentConfig',
    'DatabaseConfig',
    'RedisConfig',
    'S3Config',
    'MLFlowConfig',
    'TrainingConfig',
    'InferenceConfig',
    'DeploymentConfig',
    'MonitoringConfig',
    'SecurityConfig',
    'LoggingConfig',
    'Environment',
    'ModelFramework',
    'default_config',
    'development_config',
    'production_config',
    'get_config'
]
