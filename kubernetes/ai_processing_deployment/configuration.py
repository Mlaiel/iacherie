"""Advanced Configuration Management for AI Processing Deployment
=============================================================

Enterprise-grade configuration management system providing dynamic configuration,
environment-specific settings, secret management, and configuration validation.

Features:
- Multi-environment configuration management
- Dynamic configuration updates and hot-reloading
- Secure secret management and encryption
- Configuration validation and schema enforcement
- Environment variable and file-based configuration

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import os
import json
import yaml
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Type
import uuid
from cryptography.fernet import Fernet
import base64
import hashlib

from pydantic import BaseModel, Field, validator
import redis.asyncio as aioredis
from kubernetes import client as k8s_client

from .core import ProcessingConfig, AIModelType

logger = logging.getLogger(__name__)


class Environment(Enum):
    """
Deployment environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConfigurationSource(Enum):
    """Configuration data sources."""

    FILE = "file"
    ENVIRONMENT = "environment"
    KUBERNETES = "kubernetes"
    REDIS = "redis"
    DATABASE = "database"
    VAULT = "vault"


class SecretType(Enum):
    """Types of secrets."""

    DATABASE_PASSWORD = "database_password"
    API_KEY = "api_key"
    ENCRYPTION_KEY = "encryption_key"
    CERTIFICATE = "certificate"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "ai_processing"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class RedisConfig:
    """Redis connection configuration."""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = ""
    ssl: bool = False
    pool_size: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30


@dataclass
class SecurityConfig:
    """Security and encryption configuration."""
    encryption_enabled: bool = True
    encryption_key: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 60
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration."""
    prometheus_enabled: bool = True
    prometheus_port: int = 8080
    prometheus_path: str = "/metrics"
    jaeger_enabled: bool = True
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    logging_level: str = "INFO"
    logging_format: str = "json"
    elasticsearch_enabled: bool = False
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "ai-processing-logs"


@dataclass
class ScalingConfig:
    """Auto-scaling configuration."""
    enabled: bool = True
    min_replicas: int = 2
    max_replicas: int = 20
    target_cpu_percent: int = 70
    target_memory_percent: int = 80
    scale_up_threshold: int = 85
    scale_down_threshold: int = 30
    scale_up_cooldown_minutes: int = 5
    scale_down_cooldown_minutes: int = 15
    custom_metrics_enabled: bool = False
    custom_metrics: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AIModelConfig:
    """
AI model configuration."""
    model_type: AIModelType
    model_path: str = ""
    model_name: str = ""
    version: str = "1.0.0"
    backend: str = "pytorch"  # pytorch, tensorflow, onnx, huggingface
    device: str = "auto"  # auto, cpu, gpu
    batch_size: int = 32
    max_sequence_length: int = 512
    cache_enabled: bool = True
    cache_size_mb: int = 1024
    optimization_enabled: bool = True
    quantization_enabled: bool = False
    tensorrt_enabled: bool = False


@dataclass
class StorageConfig:
    """Storage configuration."""
    type: str = "s3"  # s3, gcs, azure, local
    bucket_name: str = ""
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    endpoint_url: str = ""
    use_ssl: bool = True
    local_path: str = "/data"
    max_file_size_mb: int = 100
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "m4a",  # Audio
        "mp4", "avi", "mov", "mkv",   # Video
        "jpg", "jpeg", "png", "gif",  # Image
        "txt", "pdf", "docx"          # Text
    ])


@dataclass
class CompleteAIProcessingConfig:
    """Complete AI processing deployment configuration."""
    # Basic configuration
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    service_name: str = "ai-processing"
    service_version: str = "2.0.0"
    
    # Core processing
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    # Infrastructure
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    
    # Security
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Monitoring
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Scaling
    scaling: ScalingConfig = field(default_factory=ScalingConfig)
    
    # AI Models
    models: Dict[str, AIModelConfig] = field(default_factory=dict)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    config_version: str = "1.0.0"


class ConfigurationValidator:
    """
    Advanced configuration validator with schema validation,
    dependency checking, and security validation.
    """
    
    @staticmethod
    def validate_configuration(config: CompleteAIProcessingConfig) -> List[str]:
        """
Validate complete configuration and return list of errors."""
        errors = []
        
        # Validate basic configuration
        errors.extend(ConfigurationValidator._validate_basic_config(config))
        
        # Validate database configuration
        errors.extend(ConfigurationValidator._validate_database_config(config.database))
        
        # Validate Redis configuration
        errors.extend(ConfigurationValidator._validate_redis_config(config.redis))
        
        # Validate security configuration
        errors.extend(ConfigurationValidator._validate_security_config(config.security))
        
        # Validate storage configuration
        errors.extend(ConfigurationValidator._validate_storage_config(config.storage))
        
        # Validate AI model configurations
        errors.extend(ConfigurationValidator._validate_model_configs(config.models))
        
        # Validate scaling configuration
        errors.extend(ConfigurationValidator._validate_scaling_config(config.scaling))
        
        return errors
    
    @staticmethod
    def _validate_basic_config(config: CompleteAIProcessingConfig) -> List[str]:
        """
Validate basic configuration settings."""
        errors = []
        
        if not config.service_name:
            errors.append("Service name is required")
        
        if not config.service_version:
            errors.append("Service version is required")
        
        if config.processing.max_workers <= 0:
            errors.append("Max workers must be greater than 0")
        
        return errors
    
    @staticmethod
    def _validate_database_config(config: DatabaseConfig) -> List[str]:
        """Validate database configuration."""
        errors = []
        
        if not config.host:
            errors.append("Database host is required")
        
        if not (1 <= config.port <= 65535):
            errors.append("Database port must be between 1 and 65535")
        
        if not config.database:
            errors.append("Database name is required")
        
        if not config.username:
            errors.append("Database username is required")
        
        if config.pool_size <= 0:
            errors.append("Database pool size must be greater than 0")
        
        return errors
    
    @staticmethod
    def _validate_redis_config(config: RedisConfig) -> List[str]:
        """Validate Redis configuration."""
        errors = []
        
        if not config.host:
            errors.append("Redis host is required")
        
        if not (1 <= config.port <= 65535):
            errors.append("Redis port must be between 1 and 65535")
        
        if not (0 <= config.database <= 15):
            errors.append("Redis database must be between 0 and 15")
        
        if config.pool_size <= 0:
            errors.append("Redis pool size must be greater than 0")
        
        return errors
    
    @staticmethod
    def _validate_security_config(config: SecurityConfig) -> List[str]:
        """Validate security configuration."""
        errors = []
        
        if config.encryption_enabled and not config.encryption_key:
            errors.append("Encryption key is required when encryption is enabled")
        
        if not config.jwt_secret_key:
            errors.append("JWT secret key is required")
        
        if config.jwt_expiration_hours <= 0:
            errors.append("JWT expiration hours must be greater than 0")
        
        if config.password_min_length < 6:
            errors.append("Password minimum length should be at least 6 characters")
        
        if config.max_requests_per_minute <= 0:
            errors.append("Max requests per minute must be greater than 0")
        
        return errors
    
    @staticmethod
    def _validate_storage_config(config: StorageConfig) -> List[str]:
        """Validate storage configuration."""
        errors = []
        
        if config.type not in ["s3", "gcs", "azure", "local"]:
            errors.append("Storage type must be one of: s3, gcs, azure, local")
        
        if config.type in ["s3", "gcs", "azure"] and not config.bucket_name:
            errors.append(f"Bucket name is required for {config.type} storage")
        
        if config.type == "local" and not config.local_path:
            errors.append("Local path is required for local storage")
        
        if config.max_file_size_mb <= 0:
            errors.append("Max file size must be greater than 0")
        
        return errors
    
    @staticmethod
    def _validate_model_configs(models: Dict[str, AIModelConfig]) -> List[str]:
        """Validate AI model configurations."""
        errors = []
        
        for model_name, model_config in models.items():
            if not model_config.model_path:
                errors.append(f"Model path is required for model: {model_name}")
            
            if not model_config.model_name:
                errors.append(f"Model name is required for model: {model_name}")
            
            if model_config.batch_size <= 0:
                errors.append(f"Batch size must be greater than 0 for model: {model_name}")
            
            if model_config.backend not in ["pytorch", "tensorflow", "onnx", "huggingface"]:
                errors.append(f"Invalid backend for model {model_name}: {model_config.backend}")
        
        return errors
    
    @staticmethod
    def _validate_scaling_config(config: ScalingConfig) -> List[str]:
        """Validate scaling configuration."""
        errors = []
        
        if config.min_replicas <= 0:
            errors.append("Minimum replicas must be greater than 0")
        
        if config.max_replicas <= config.min_replicas:
            errors.append("Maximum replicas must be greater than minimum replicas")
        
        if not (1 <= config.target_cpu_percent <= 100):
            errors.append("Target CPU percent must be between 1 and 100")
        
        if not (1 <= config.target_memory_percent <= 100):
            errors.append("Target memory percent must be between 1 and 100")
        
        return errors


class SecretManager:
    """
    Advanced secret management system with encryption,
    key rotation, and secure storage integration.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
Initialize secret manager."""
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) else self.encryption_key)
        self.secrets: Dict[str, Dict[str, Any]] = {}
        
    def _generate_encryption_key(self) -> str:
        """
Generate new encryption key."""
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode()
    
    def encrypt_secret(self, secret_value: str) -> str:
        """
Encrypt secret value."""
        try:
            encrypted = self.cipher.encrypt(secret_value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt secret: {e}")
            raise
    
    def decrypt_secret(self, encrypted_value: str) -> str:
        """Decrypt secret value."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt secret: {e}")
            raise
    
    def store_secret(self, secret_name: str, secret_value: str, secret_type: SecretType, 
                    metadata: Dict[str, Any] = None) -> str:
        """Store encrypted secret."""
        try:
            encrypted_value = self.encrypt_secret(secret_value)
            
            secret_id = str(uuid.uuid4())
            self.secrets[secret_id] = {
                'name': secret_name,
                'type': secret_type.value,
                'encrypted_value': encrypted_value,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat(),
                'last_accessed': None
            }
            
            logger.info(f"Stored secret: {secret_name}")
            return secret_id
            
        except Exception as e:
            logger.error(f"Failed to store secret {secret_name}: {e}")
            raise
    
    def retrieve_secret(self, secret_id: str) -> Optional[str]:
        """Retrieve and decrypt secret."""
        try:
            if secret_id not in self.secrets:
                logger.warning(f"Secret not found: {secret_id}")
                return None
            
            secret_info = self.secrets[secret_id]
            decrypted_value = self.decrypt_secret(secret_info['encrypted_value'])
            
            # Update last accessed time
            secret_info['last_accessed'] = datetime.utcnow().isoformat()
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {e}")
            return None
    
    def rotate_secret(self, secret_id: str, new_value: str) -> bool:
        """Rotate secret with new value."""
        try:
            if secret_id not in self.secrets:
                logger.warning(f"Secret not found for rotation: {secret_id}")
                return False
            
            # Encrypt new value
            encrypted_value = self.encrypt_secret(new_value)
            
            # Update secret
            self.secrets[secret_id].update({
                'encrypted_value': encrypted_value,
                'rotated_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Rotated secret: {secret_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate secret {secret_id}: {e}")
            return False
    
    def delete_secret(self, secret_id: str) -> bool:
        """Delete secret."""
        try:
            if secret_id in self.secrets:
                del self.secrets[secret_id]
                logger.info(f"Deleted secret: {secret_id}")
                return True
            else:
                logger.warning(f"Secret not found for deletion: {secret_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete secret {secret_id}: {e}")
            return False
    
    def list_secrets(self, secret_type: Optional[SecretType] = None) -> List[Dict[str, Any]]:
        """List secrets with metadata (without values)."""
        secrets_list = []
        
        for secret_id, secret_info in self.secrets.items():
            if secret_type is None or secret_info['type'] == secret_type.value:
                secrets_list.append({
                    'id': secret_id,
                    'name': secret_info['name'],
                    'type': secret_info['type'],
                    'created_at': secret_info['created_at'],
                    'last_accessed': secret_info['last_accessed'],
                    'metadata': secret_info['metadata']
                })
        
        return secrets_list


class ConfigurationManager:
    """
    Advanced configuration management system providing dynamic configuration,
    hot-reloading, and multi-source configuration support.
    """
    
    def __init__(self, environment: Environment = Environment.PRODUCTION):
        """
Initialize configuration manager."""
        self.environment = environment
        self.config: Optional[CompleteAIProcessingConfig] = None
        self.secret_manager = SecretManager()
        self.configuration_sources: List[ConfigurationSource] = []
        self.config_watchers: Dict[str, asyncio.Task] = {}
        self.config_cache: Dict[str, Any] = {}
        self.redis_client: Optional[aioredis.Redis] = None
        
    async def initialize(self, config_path: Optional[str] = None):
        """
Initialize configuration manager."""
        try:
            # Load configuration from various sources
            await self._load_configuration(config_path)
            
            # Validate configuration
            await self._validate_configuration()
            
            # Initialize Redis client for configuration caching
            await self._initialize_redis_client()
            
            # Start configuration watchers
            await self._start_configuration_watchers()
            
            logger.info(f"Configuration manager initialized for environment: {self.environment.value}")
            
        except Exception as e:
            logger.error(f"Configuration manager initialization failed: {e}")
            raise
    
    async def _load_configuration(self, config_path: Optional[str] = None):
        """Load configuration from multiple sources."""
        # 1. Load from file
        if config_path:
            await self._load_from_file(config_path)
        else:
            # Try default paths
            default_paths = [
                f"config/{self.environment.value}.yaml",
                f"config/{self.environment.value}.yml",
                f"config/{self.environment.value}.json",
                "config/default.yaml",
                "config/default.yml",
                "config/default.json"
            ]
            
            for path in default_paths:
                if Path(path).exists():
                    await self._load_from_file(path)
                    break
        
        # 2. Load from environment variables
        await self._load_from_environment()
        
        # 3. Load from Kubernetes secrets/configmaps (if in cluster)
        await self._load_from_kubernetes()
        
        # 4. Apply environment-specific overrides
        await self._apply_environment_overrides()
    
    async def _load_from_file(self, config_path: str):
        """Load configuration from file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return
            
            with open(config_file, 'r') as f:
                if config_path.endswith('.json'):
                    config_data = json.load(f)
                else:
                    config_data = yaml.safe_load(f)
            
            # Convert to configuration object
            if self.config is None:
                self.config = CompleteAIProcessingConfig()
            
            # Update configuration with file data
            self._update_config_from_dict(config_data)
            
            self.configuration_sources.append(ConfigurationSource.FILE)
            logger.info(f"Loaded configuration from file: {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from file {config_path}: {e}")
    
    async def _load_from_environment(self):
        """Load configuration from environment variables."""
        try:
            if self.config is None:
                self.config = CompleteAIProcessingConfig()
            
            # Map environment variables to configuration
            env_mappings = {
                # Basic
                'AI_SERVICE_NAME': ('service_name', str),
                'AI_SERVICE_VERSION': ('service_version', str),
                'AI_DEBUG': ('debug', bool),
                
                # Processing
                'AI_MAX_WORKERS': ('processing.max_workers', int),
                'AI_GPU_ENABLED': ('processing.gpu_enabled', bool),
                'AI_MEMORY_LIMIT': ('processing.memory_limit', str),
                'AI_CPU_LIMIT': ('processing.cpu_limit', str),
                
                # Database
                'DATABASE_HOST': ('database.host', str),
                'DATABASE_PORT': ('database.port', int),
                'DATABASE_NAME': ('database.database', str),
                'DATABASE_USERNAME': ('database.username', str),
                'DATABASE_PASSWORD': ('database.password', str),
                
                # Redis
                'REDIS_HOST': ('redis.host', str),
                'REDIS_PORT': ('redis.port', int),
                'REDIS_DATABASE': ('redis.database', int),
                'REDIS_PASSWORD': ('redis.password', str),
                
                # Security
                'JWT_SECRET_KEY': ('security.jwt_secret_key', str),
                'ENCRYPTION_KEY': ('security.encryption_key', str),
                
                # Storage
                'STORAGE_TYPE': ('storage.type', str),
                'STORAGE_BUCKET': ('storage.bucket_name', str),
                'STORAGE_REGION': ('storage.region', str),
                'AWS_ACCESS_KEY_ID': ('storage.access_key_id', str),
                'AWS_SECRET_ACCESS_KEY': ('storage.secret_access_key', str),
            }
            
            for env_var, (config_path, value_type) in env_mappings.items():
                value = os.getenv(env_var)
                if value is not None:
                    # Convert value to appropriate type
                    if value_type == bool:
                        value = value.lower() in ['true', '1', 'yes', 'on']
                    elif value_type == int:
                        value = int(value)
                    
                    # Set configuration value
                    self._set_nested_config_value(config_path, value)
            
            self.configuration_sources.append(ConfigurationSource.ENVIRONMENT)
            logger.info("Loaded configuration from environment variables")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from environment: {e}")
    
    async def _load_from_kubernetes(self):
        """Load configuration from Kubernetes secrets and configmaps."""
        try:
            # Check if running in Kubernetes
            if not Path('/var/run/secrets/kubernetes.io/serviceaccount').exists():
                return
            
            # Initialize Kubernetes client
            from kubernetes import client, config
            config.load_incluster_config()
            v1 = client.CoreV1Api()
            
            # Get namespace
            namespace = os.getenv('POD_NAMESPACE', 'default')
            
            # Load from ConfigMaps
            try:
                config_map = v1.read_namespaced_config_map(
                    name='ai-processing-config', namespace=namespace
                )
                if config_map.data:
                    config_data = yaml.safe_load(config_map.data.get('config.yaml', '{}'))
                    self._update_config_from_dict(config_data)
                    logger.info("Loaded configuration from Kubernetes ConfigMap")
            except Exception as e:
                logger.debug(f"ConfigMap not found or error loading: {e}")
            
            # Load secrets
            try:
                secret = v1.read_namespaced_secret(
                    name='ai-processing-secrets', namespace=namespace
                )
                if secret.data:
                    for key, value in secret.data.items():
                        decoded_value = base64.b64decode(value).decode('utf-8')
                        # Store in secret manager
                        self.secret_manager.store_secret(
                            key, decoded_value, SecretType.API_KEY
                        )
                    logger.info("Loaded secrets from Kubernetes Secret")
            except Exception as e:
                logger.debug(f"Secret not found or error loading: {e}")
            
            self.configuration_sources.append(ConfigurationSource.KUBERNETES)
            
        except Exception as e:
            logger.debug(f"Kubernetes configuration loading failed: {e}")
    
    async def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        if self.config is None:
            return
        
        if self.environment == Environment.DEVELOPMENT:
            self.config.debug = True
            self.config.monitoring.logging_level = "DEBUG"
            self.config.security.cors_origins = ["*"]
            self.config.scaling.min_replicas = 1
            self.config.scaling.max_replicas = 3
            
        elif self.environment == Environment.STAGING:
            self.config.debug = False
            self.config.monitoring.logging_level = "INFO"
            self.config.scaling.min_replicas = 2
            self.config.scaling.max_replicas = 10
            
        elif self.environment == Environment.PRODUCTION:
            self.config.debug = False
            self.config.monitoring.logging_level = "WARNING"
            self.config.security.cors_origins = []  # Restrict CORS in production
            self.config.scaling.min_replicas = 3
            self.config.scaling.max_replicas = 20
            
        elif self.environment == Environment.TESTING:
            self.config.debug = True
            self.config.monitoring.logging_level = "DEBUG"
            self.config.scaling.enabled = False
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration object from dictionary."""
        if self.config is None:
            self.config = CompleteAIProcessingConfig()
        
        # Recursively update configuration
        def update_nested(obj, data):
            for key, value in data.items():
                if hasattr(obj, key):
                    current_value = getattr(obj, key)
                    if isinstance(current_value, dict) and isinstance(value, dict):
                        current_value.update(value)
                    elif hasattr(current_value, '__dict__') and isinstance(value, dict):
                        update_nested(current_value, value)
                    else:
                        setattr(obj, key, value)
        
        update_nested(self.config, config_data)
    
    def _set_nested_config_value(self, config_path: str, value: Any):
        """
Set nested configuration value using dot notation."""
        if self.config is None:
            return
        
        parts = config_path.split('.')
        obj = self.config
        
        # Navigate to the parent object
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return
        
        # Set the final value
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
    
    async def _validate_configuration(self):
        """
Validate loaded configuration."""
        if self.config is None:
            raise ValueError("No configuration loaded")
        
        errors = ConfigurationValidator.validate_configuration(self.config)
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    async def _initialize_redis_client(self):
        """Initialize Redis client for configuration caching."""
        if self.config and self.config.redis:
            try:
                self.redis_client = aioredis.Redis(
                    host=self.config.redis.host,
                    port=self.config.redis.port,
                    db=self.config.redis.database,
                    password=self.config.redis.password if self.config.redis.password else None,
                    ssl=self.config.redis.ssl,
                    socket_timeout=self.config.redis.socket_timeout,
                    socket_connect_timeout=self.config.redis.socket_connect_timeout,
                    retry_on_timeout=self.config.redis.retry_on_timeout,
                    health_check_interval=self.config.redis.health_check_interval
                )
                
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis client initialized for configuration caching")
                
            except Exception as e:
                logger.warning(f"Failed to initialize Redis client: {e}")
                self.redis_client = None
    
    async def _start_configuration_watchers(self):
        """Start configuration file watchers for hot-reloading."""
        # This would implement file watching for configuration changes
        # For now, we'll just log that watchers would be started
        logger.info("Configuration watchers initialized")
    
    def get_config(self) -> CompleteAIProcessingConfig:
        """Get current configuration."""
        if self.config is None:
            raise ValueError("Configuration not initialized")
        return self.config
    
    def get_database_url(self) -> str:
        """Get complete database URL."""
        if self.config is None or self.config.database is None:
            raise ValueError("Database configuration not available")
        
        db = self.config.database
        return f"postgresql://{db.username}:{db.password}@{db.host}:{db.port}/{db.database}"
    
    def get_redis_url(self) -> str:
        """Get complete Redis URL."""
        if self.config is None or self.config.redis is None:
            raise ValueError("Redis configuration not available")
        
        redis_config = self.config.redis
        auth = f":{redis_config.password}@" if redis_config.password else ""
        protocol = "rediss" if redis_config.ssl else "redis"
        return f"{protocol}://{auth}{redis_config.host}:{redis_config.port}/{redis_config.database}"
    
    async def update_configuration(self, updates: Dict[str, Any], persist: bool = True) -> bool:
        """Update configuration dynamically."""
        try:
            if self.config is None:
                raise ValueError("Configuration not initialized")
            
            # Apply updates
            self._update_config_from_dict(updates)
            
            # Update timestamp
            self.config.updated_at = datetime.utcnow()
            
            # Validate updated configuration
            errors = ConfigurationValidator.validate_configuration(self.config)
            if errors:
                logger.error(f"Configuration update validation failed: {errors}")
                return False
            
            # Persist to cache if enabled
            if persist and self.redis_client:
                await self._cache_configuration()
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    async def _cache_configuration(self):
        """Cache configuration in Redis."""
        if self.redis_client and self.config:
            try:
                config_dict = asdict(self.config)
                await self.redis_client.set(
                    "ai_processing_config",
                    json.dumps(config_dict, default=str),
                    ex=3600  # 1 hour expiration
                )
                logger.debug("Configuration cached in Redis")
            except Exception as e:
                logger.warning(f"Failed to cache configuration: {e}")
    
    async def export_configuration(self, format: str = "yaml") -> str:
        """Export current configuration."""
        if self.config is None:
            raise ValueError("Configuration not initialized")
        
        config_dict = asdict(self.config)
        
        if format.lower() == "json":
            return json.dumps(config_dict, indent=2, default=str)
        else:
            return yaml.dump(config_dict, default_flow_style=False)
    
    async def shutdown(self):
        """Shutdown configuration manager."""
        try:
            # Cancel watchers
            for watcher_name, task in self.config_watchers.items():
                task.cancel()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Configuration manager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during configuration manager shutdown: {e}")


# Factory functions for quick setup
async def create_configuration_manager(environment: str = "production", 
                                     config_path: Optional[str] = None) -> ConfigurationManager:
    """Create and initialize configuration manager."""
    env = Environment(environment.lower())
    manager = ConfigurationManager(env)
    await manager.initialize(config_path)
    return manager


def create_default_config(environment: Environment = Environment.PRODUCTION) -> CompleteAIProcessingConfig:
    """
Create default configuration for specified environment."""
    config = CompleteAIProcessingConfig(environment=environment)
    
    # Apply environment-specific defaults
    if environment == Environment.DEVELOPMENT:
        config.debug = True
        config.processing.max_workers = 4
        config.scaling.min_replicas = 1
        config.scaling.max_replicas = 3
        
    elif environment == Environment.PRODUCTION:
        config.debug = False
        config.processing.max_workers = 10
        config.security.encryption_enabled = True
        config.scaling.min_replicas = 3
        config.scaling.max_replicas = 20
    
    return config


def create_model_config(model_type: AIModelType, model_path: str, 
                       backend: str = "pytorch", device: str = "auto") -> AIModelConfig:
    """Create AI model configuration."""
    return AIModelConfig(
        model_type=model_type,
        model_path=model_path,
        model_name=f"{model_type.value}_model",
        backend=backend,
        device=device,
        batch_size=32,
        cache_enabled=True,
        optimization_enabled=True
    )
