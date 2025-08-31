"""
Enterprise Configuration Management Module

Comprehensive configuration management system for the IA Influencer Agent + Content Protection Platform.
Provides secure configuration handling, environment-specific settings, secrets management, 
validation, encryption, and dynamic configuration updates across all deployment environments.

Project Owner: Fahed Mlaiel (mlaiel@live.de)

 CRITICAL LEGAL WARNING:
This software and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or appropriation of this code, concept, 
or business idea without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is strictly prohibited and will result in immediate legal action. All rights reserved.

Business Logic Flow:
Content Creator → Upload Multi-format → AI Protection & Fingerprinting → SEO Optimization → 
Collaboration Matching → Multi-platform Distribution → Monetization & Revenue Tracking

Architecture Components:
- Environment-specific configuration management
- Secure secrets handling with encryption
- Configuration validation and schema enforcement
- Dynamic configuration updates and reloading
- Multi-cloud provider configuration
- Database and service connection management
- Monitoring and logging configuration
- Security and compliance settings
"""

import os
import json
import yaml
import logging
import hashlib
import base64
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import boto3
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from google.cloud import secretmanager
import jinja2

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Supported configuration formats"""
    YAML = "yaml"
    JSON = "json"
    ENV = "env"
    PROPERTIES = "properties"
    TOML = "toml"


class SecretProvider(Enum):
    """Supported secret management providers"""
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_SECRET_MANAGER = "gcp_secret_manager"
    KUBERNETES_SECRETS = "kubernetes_secrets"
    HASHICORP_VAULT = "hashicorp_vault"
    LOCAL_ENCRYPTED = "local_encrypted"


class EnvironmentType(Enum):
    """Environment types for configuration"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class ConfigMetadata:
    """Metadata for configuration files"""
    name: str
    environment: EnvironmentType
    version: str
    created_by: str
    created_at: str
    updated_at: str
    checksum: str
    encrypted: bool = False
    secret_provider: Optional[SecretProvider] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Add default tags"""
        self.tags.update({
            'project': 'IA-Influencer-Agent',
            'environment': self.environment.value,
            'managed_by': 'ConfigManager'
        })


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    max_connections: int = 100
    connection_timeout: int = 30
    pool_size: int = 20
    pool_timeout: int = 30
    charset: str = "utf8mb4"
    engine_options: Dict[str, Any] = field(default_factory=dict)
    
    def get_connection_string(self, include_password: bool = True) -> str:
        """Generate database connection string"""
        password_part = f":{self.password}" if include_password and self.password else ""
        return f"postgresql://{self.username}{password_part}@{self.host}:{self.port}/{self.database}"


@dataclass
class RedisConfig:
    """Redis configuration settings"""
    host: str
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    ssl: bool = False
    ssl_verify: bool = True
    max_connections: int = 50
    connection_timeout: int = 10
    socket_timeout: int = 10
    socket_keepalive: bool = True
    socket_keepalive_options: Dict[str, int] = field(default_factory=dict)
    
    def get_connection_url(self, include_password: bool = True) -> str:
        """Generate Redis connection URL"""
        protocol = "rediss" if self.ssl else "redis"
        password_part = f":{self.password}@" if include_password and self.password else ""
        return f"{protocol}://{password_part}{self.host}:{self.port}/{self.database}"


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    prometheus_scrape_interval: str = "15s"
    prometheus_retention: str = "15d"
    grafana_enabled: bool = True
    grafana_port: int = 3000
    grafana_admin_password: Optional[str] = None
    jaeger_enabled: bool = True
    jaeger_agent_port: int = 14268
    jaeger_collector_port: int = 14250
    logging_level: str = "INFO"
    log_format: str = "json"
    log_retention_days: int = 30
    metrics_enabled: bool = True
    tracing_enabled: bool = True
    health_check_interval: int = 30
    alertmanager_enabled: bool = True
    alertmanager_port: int = 9093
    notification_channels: List[str] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """Security and compliance configuration"""
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    jwt_secret_key: Optional[str] = None
    jwt_expiration_hours: int = 24
    oauth2_enabled: bool = True
    oauth2_providers: List[str] = field(default_factory=lambda: ["google", "github"])
    mfa_enabled: bool = False
    password_policy: Dict[str, Any] = field(default_factory=lambda: {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digits": True,
        "require_special_chars": True
    })
    session_timeout_minutes: int = 480
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    cors_allowed_origins: List[str] = field(default_factory=list)
    cors_allow_credentials: bool = True
    rate_limiting_enabled: bool = True
    rate_limit_per_minute: int = 100
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)
    audit_logging_enabled: bool = True
    compliance_mode: str = "GDPR"  # GDPR, CCPA, SOX, HIPAA


@dataclass
class AIConfig:
    """AI and Machine Learning configuration"""
    fingerprinting_enabled: bool = True
    audio_fingerprinting_algorithm: str = "chromaprint"
    video_fingerprinting_algorithm: str = "perceptual_hash"
    image_fingerprinting_algorithm: str = "clip_embedding"
    text_fingerprinting_algorithm: str = "bert_similarity"
    similarity_threshold: float = 0.85
    batch_size: int = 32
    max_workers: int = 4
    gpu_enabled: bool = True
    model_cache_size_gb: int = 10
    feature_extraction_timeout: int = 300
    similarity_search_timeout: int = 30
    vector_database_url: Optional[str] = None
    vector_database_index: str = "ia_influencer_vectors"
    content_analysis_api_key: Optional[str] = None
    nlp_models: List[str] = field(default_factory=lambda: [
        "bert-base-uncased",
        "distilbert-base-uncased",
        "roberta-base"
    ])
    cv_models: List[str] = field(default_factory=lambda: [
        "clip-vit-base-patch32",
        "resnet50",
        "efficientnet-b0"
    ])
    audio_models: List[str] = field(default_factory=lambda: [
        "wav2vec2-base",
        "whisper-small",
        "yamnet"
    ])


@dataclass
class ContentProtectionConfig:
    """Content protection and monitoring configuration"""
    monitoring_enabled: bool = True
    real_time_detection: bool = True
    crawling_enabled: bool = True
    crawling_interval_hours: int = 6
    platforms_to_monitor: List[str] = field(default_factory=lambda: [
        "youtube", "tiktok", "instagram", "twitter", "facebook", "spotify"
    ])
    automated_takedown_enabled: bool = False
    manual_review_required: bool = True
    notification_on_detection: bool = True
    evidence_collection_enabled: bool = True
    watermarking_enabled: bool = True
    drm_enabled: bool = False
    copyright_protection_level: str = "standard"  # basic, standard, premium
    api_rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "youtube": 10000,
        "tiktok": 5000,
        "instagram": 200,
        "twitter": 300
    })
    proxy_rotation_enabled: bool = True
    captcha_solving_enabled: bool = False
    headless_browser_enabled: bool = True


@dataclass
class MonetizationConfig:
    """Monetization and revenue tracking configuration"""
    revenue_tracking_enabled: bool = True
    automated_licensing_enabled: bool = True
    payment_processing_enabled: bool = True
    supported_currencies: List[str] = field(default_factory=lambda: [
        "USD", "EUR", "GBP", "CAD", "AUD"
    ])
    default_currency: str = "USD"
    commission_rate: float = 0.15  # 15% commission
    minimum_payout_threshold: float = 50.0
    payout_frequency: str = "monthly"  # daily, weekly, monthly
    payment_providers: List[str] = field(default_factory=lambda: [
        "stripe", "paypal", "wise"
    ])
    tax_calculation_enabled: bool = True
    invoice_generation_enabled: bool = True
    revenue_analytics_enabled: bool = True
    blockchain_payments_enabled: bool = False
    cryptocurrency_support: List[str] = field(default_factory=lambda: [
        "BTC", "ETH", "USDC"
    ])


@dataclass
class StorageConfig:
    """Storage and file management configuration"""
    storage_provider: str = "s3"  # s3, gcp, azure, local
    bucket_name: str = "ia-influencer-content"
    region: str = "us-east-1"
    encryption_enabled: bool = True
    versioning_enabled: bool = True
    lifecycle_policies_enabled: bool = True
    backup_enabled: bool = True
    backup_retention_days: int = 90
    cdn_enabled: bool = True
    cdn_provider: str = "cloudfront"
    max_file_size_mb: int = 500
    allowed_file_types: List[str] = field(default_factory=lambda: [
        "mp3", "wav", "flac", "m4a", "aac",  # Audio
        "mp4", "avi", "mov", "mkv", "webm",  # Video
        "jpg", "jpeg", "png", "gif", "webp", "svg",  # Image
        "pdf", "doc", "docx", "txt", "md"  # Documents
    ])
    virus_scanning_enabled: bool = True
    content_moderation_enabled: bool = True
    automatic_thumbnails: bool = True
    image_optimization: bool = True
    video_transcoding: bool = True


@dataclass
class NetworkConfig:
    """Network and connectivity configuration"""
    load_balancer_enabled: bool = True
    load_balancer_type: str = "application"  # application, network
    ssl_termination: str = "load_balancer"  # load_balancer, application
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    health_check_healthy_threshold: int = 2
    health_check_unhealthy_threshold: int = 3
    cdn_enabled: bool = True
    cdn_cache_ttl: int = 3600
    dns_provider: str = "route53"
    domain_name: Optional[str] = None
    subdomain_prefix: str = "api"
    ssl_certificate_arn: Optional[str] = None
    waf_enabled: bool = True
    ddos_protection_enabled: bool = True
    firewall_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScalingConfig:
    """Auto-scaling and performance configuration"""
    auto_scaling_enabled: bool = True
    min_instances: int = 2
    max_instances: int = 20
    target_cpu_percentage: int = 70
    target_memory_percentage: int = 80
    scale_up_cooldown: int = 300
    scale_down_cooldown: int = 300
    predictive_scaling_enabled: bool = False
    scheduled_scaling_enabled: bool = False
    load_balancing_algorithm: str = "round_robin"  # round_robin, least_connections, ip_hash
    session_affinity_enabled: bool = False
    connection_draining_timeout: int = 300
    instance_warmup_time: int = 180


@dataclass
class BackupConfig:
    """Backup and disaster recovery configuration"""
    automated_backups_enabled: bool = True
    backup_frequency: str = "daily"  # hourly, daily, weekly
    backup_retention_days: int = 30
    cross_region_backups: bool = True
    backup_encryption: bool = True
    point_in_time_recovery: bool = True
    backup_verification: bool = True
    disaster_recovery_enabled: bool = False
    rto_minutes: int = 60  # Recovery Time Objective
    rpo_minutes: int = 15  # Recovery Point Objective
    backup_storage_class: str = "standard_ia"
    backup_compression: bool = True
    incremental_backups: bool = True


@dataclass
class EnvironmentConfig:
    """Complete environment configuration"""
    metadata: ConfigMetadata
    database: DatabaseConfig
    redis: RedisConfig
    monitoring: MonitoringConfig
    security: SecurityConfig
    ai: AIConfig
    content_protection: ContentProtectionConfig
    monetization: MonetizationConfig
    storage: StorageConfig
    network: NetworkConfig
    scaling: ScalingConfig
    backup: BackupConfig
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate configuration for consistency and completeness"""
        errors = []
        
        # Validate database configuration
        if not self.database.host:
            errors.append("Database host is required")
        if self.database.port <= 0 or self.database.port > 65535:
            errors.append("Database port must be between 1 and 65535")
        
        # Validate Redis configuration
        if not self.redis.host:
            errors.append("Redis host is required")
        if self.redis.port <= 0 or self.redis.port > 65535:
            errors.append("Redis port must be between 1 and 65535")
        
        # Validate security settings
        if self.security.jwt_expiration_hours <= 0:
            errors.append("JWT expiration must be positive")
        if self.security.rate_limit_per_minute <= 0:
            errors.append("Rate limit must be positive")
        
        # Validate AI configuration
        if self.ai.similarity_threshold < 0 or self.ai.similarity_threshold > 1:
            errors.append("AI similarity threshold must be between 0 and 1")
        
        # Validate monetization settings
        if self.monetization.commission_rate < 0 or self.monetization.commission_rate > 1:
            errors.append("Commission rate must be between 0 and 1")
        
        # Validate scaling configuration
        if self.scaling.min_instances > self.scaling.max_instances:
            errors.append("Minimum instances cannot exceed maximum instances")
        if self.scaling.target_cpu_percentage <= 0 or self.scaling.target_cpu_percentage > 100:
            errors.append("Target CPU percentage must be between 1 and 100")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""



        return {
            'metadata': asdict(self.metadata),
            'database': asdict(self.database),
            'redis': asdict(self.redis),
            'monitoring': asdict(self.monitoring),
            'security': asdict(self.security),
            'ai': asdict(self.ai),
            'content_protection': asdict(self.content_protection),
            'monetization': asdict(self.monetization),
            'storage': asdict(self.storage),
            'network': asdict(self.network),
            'scaling': asdict(self.scaling),
            'backup': asdict(self.backup),
            'custom_settings': self.custom_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentConfig':
        """Create configuration from dictionary"""



        return cls(
            metadata=ConfigMetadata(**data['metadata']),
            database=DatabaseConfig(**data['database']),
            redis=RedisConfig(**data['redis']),
            monitoring=MonitoringConfig(**data['monitoring']),
            security=SecurityConfig(**data['security']),
            ai=AIConfig(**data['ai']),
            content_protection=ContentProtectionConfig(**data['content_protection']),
            monetization=MonetizationConfig(**data['monetization']),
            storage=StorageConfig(**data['storage']),
            network=NetworkConfig(**data['network']),
            scaling=ScalingConfig(**data['scaling']),
            backup=BackupConfig(**data['backup']),
            custom_settings=data.get('custom_settings', {})
        )
    health_check_port: int = 8080
    log_format: str = "json"
    log_retention_days: int = 30
    metrics_retention_days: int = 90
    trace_sampling_rate: float = 0.1
    alert_rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_enabled: bool = True
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    cors_origins: List[str] = field(default_factory=list)
    rate_limiting_enabled: bool = True
    rate_limit_per_minute: int = 100
    ssl_required: bool = True
    password_min_length: int = 12
    password_require_special: bool = True
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15


@dataclass
class StorageConfig:
    """Storage configuration settings"""
    s3_bucket: str
    s3_region: str
    s3_access_key: str
    s3_secret_key: str
    s3_endpoint: Optional[str] = None
    encryption_enabled: bool = True
    versioning_enabled: bool = True
    lifecycle_rules: List[Dict[str, Any]] = field(default_factory=list)
    backup_retention_days: int = 30
    content_types_allowed: List[str] = field(default_factory=lambda: [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'video/mp4', 'video/avi', 'video/mov', 'video/wmv',
        'audio/mp3', 'audio/wav', 'audio/flac', 'audio/ogg',
        'text/plain', 'application/pdf'
    ])


@dataclass
class AIConfig:
    """AI and ML service configuration"""
    fingerprinting_enabled: bool = True
    content_protection_enabled: bool = True
    model_cache_size: int = 1000
    gpu_enabled: bool = False
    batch_size: int = 32
    model_timeout_seconds: int = 300
    vector_dimension: int = 512
    similarity_threshold: float = 0.85
    models: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'audio': {
            'provider': 'chromaprint',
            'model_path': '/models/audio',
            'enabled': True
        },
        'video': {
            'provider': 'opencv',
            'model_path': '/models/video',
            'enabled': True
        },
        'image': {
            'provider': 'clip',
            'model_path': '/models/image',
            'enabled': True
        },
        'text': {
            'provider': 'bert',
            'model_path': '/models/text',
            'enabled': True
        }
    })


@dataclass
class ApplicationConfig:
    """Main application configuration"""
    name: str = "IA Influencer Platform"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    debug: bool = False
    testing: bool = False
    timezone: str = "UTC"
    language: str = "en"
    secret_key: str = ""
    database: DatabaseConfig = field(default_factory=lambda: DatabaseConfig("", 0, "", "", ""))
    redis: RedisConfig = field(default_factory=lambda: RedisConfig(""))
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    storage: StorageConfig = field(default_factory=lambda: StorageConfig("", "", "", ""))
    ai: AIConfig = field(default_factory=AIConfig)
    
    metadata: ConfigMetadata = field(default_factory=lambda: ConfigMetadata(
        "", EnvironmentType.DEVELOPMENT, "1.0.0", "", "", "", "", False
    ))


class BaseConfigManager(ABC):
    """Abstract base class for configuration management"""
    
    def __init__(self, environment: EnvironmentType):
        self.environment = environment
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._config_cache: Dict[str, Any] = {}
        
    @abstractmethod
    def load_config(self, config_name: str) -> ApplicationConfig:
        """Load configuration from source"""
        pass
    
    @abstractmethod
    def save_config(self, config: ApplicationConfig, config_name: str) -> bool:
        """Save configuration to source"""
        pass
    
    @abstractmethod
    def validate_config(self, config: ApplicationConfig) -> Dict[str, bool]:
        """Validate configuration"""
        pass
    
    def generate_config_checksum(self, config_data: Dict[str, Any]) -> str:
        """Generate checksum for configuration data"""
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()


class FileConfigManager(BaseConfigManager):
    """File-based configuration manager"""
    
    def __init__(self, environment: EnvironmentType, config_dir: str):
        super().__init__(environment)
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def load_config(self, config_name: str) -> ApplicationConfig:
        """Load configuration from YAML file"""
        config_file = self.config_dir / f"{config_name}-{self.environment.value}.yaml"
        
        if not config_file.exists():
            self.logger.warning(f"Config file not found: {config_file}")
            return self._create_default_config()
        
        try:
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Convert dict to ApplicationConfig
            config = self._dict_to_config(config_data)
            
            # Cache the configuration
            self._config_cache[config_name] = config
            
            self.logger.info(f"Loaded configuration: {config_name}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading config {config_name}: {str(e)}")
            return self._create_default_config()
    
    def save_config(self, config: ApplicationConfig, config_name: str) -> bool:
        """Save configuration to YAML file"""
        config_file = self.config_dir / f"{config_name}-{self.environment.value}.yaml"
        
        try:
            # Convert ApplicationConfig to dict
            config_data = asdict(config)
            
            # Update metadata
            config_data['metadata']['updated_at'] = self._get_timestamp()
            config_data['metadata']['checksum'] = self.generate_config_checksum(config_data)
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved configuration: {config_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving config {config_name}: {str(e)}")
            return False
    
    def validate_config(self, config: ApplicationConfig) -> Dict[str, bool]:
        """Validate configuration settings"""
        validation_results = {}
        
        # Validate database configuration
        validation_results['database_host'] = bool(config.database.host)
        validation_results['database_port'] = 1 <= config.database.port <= 65535
        validation_results['database_name'] = bool(config.database.database)
        validation_results['database_username'] = bool(config.database.username)
        validation_results['database_password'] = bool(config.database.password)
        
        # Validate Redis configuration
        validation_results['redis_host'] = bool(config.redis.host)
        validation_results['redis_port'] = 1 <= config.redis.port <= 65535
        
        # Validate application configuration
        validation_results['app_name'] = bool(config.name)
        validation_results['app_version'] = bool(config.version)
        validation_results['app_port'] = 1 <= config.port <= 65535
        validation_results['app_workers'] = config.workers > 0
        validation_results['app_secret_key'] = len(config.secret_key) >= 32
        
        # Validate security configuration
        validation_results['jwt_secret'] = len(config.security.jwt_secret_key) >= 32
        validation_results['password_policy'] = config.security.password_min_length >= 8
        
        # Validate storage configuration
        validation_results['s3_bucket'] = bool(config.storage.s3_bucket)
        validation_results['s3_region'] = bool(config.storage.s3_region)
        validation_results['s3_credentials'] = bool(config.storage.s3_access_key and config.storage.s3_secret_key)
        
        return validation_results
    
    def _dict_to_config(self, config_data: Dict[str, Any]) -> ApplicationConfig:
        """Convert dictionary to ApplicationConfig"""
        # Handle nested objects
        if 'database' in config_data:
            config_data['database'] = DatabaseConfig(**config_data['database'])
        
        if 'redis' in config_data:
            config_data['redis'] = RedisConfig(**config_data['redis'])
        
        if 'monitoring' in config_data:
            config_data['monitoring'] = MonitoringConfig(**config_data['monitoring'])
        
        if 'security' in config_data:
            config_data['security'] = SecurityConfig(**config_data['security'])
        
        if 'storage' in config_data:
            config_data['storage'] = StorageConfig(**config_data['storage'])
        
        if 'ai' in config_data:
            config_data['ai'] = AIConfig(**config_data['ai'])
        
        if 'metadata' in config_data:
            metadata_dict = config_data['metadata']
            metadata_dict['environment'] = EnvironmentType(metadata_dict['environment'])
            if 'secret_provider' in metadata_dict and metadata_dict['secret_provider']:
                metadata_dict['secret_provider'] = SecretProvider(metadata_dict['secret_provider'])
            config_data['metadata'] = ConfigMetadata(**metadata_dict)
        
        return ApplicationConfig(**config_data)
    
    def _create_default_config(self) -> ApplicationConfig:
        """Create default configuration"""



        return ApplicationConfig(
            metadata=ConfigMetadata(
                name="default",
                environment=self.environment,
                version="1.0.0",
                created_by="system",
                created_at=self._get_timestamp(),
                updated_at=self._get_timestamp(),
                checksum=""
            )
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class SecretManager:
    """Secure secret management"""
    
    def __init__(self, provider: SecretProvider, **kwargs):
        self.provider = provider
        self.logger = logging.getLogger(__name__)
        self._initialize_provider(**kwargs)
    
    def _initialize_provider(self, **kwargs):
        """Initialize secret provider client"""
        if self.provider == SecretProvider.AWS_SECRETS_MANAGER:
            self.client = boto3.client('secretsmanager', region_name=kwargs.get('region', 'us-east-1'))
        elif self.provider == SecretProvider.AZURE_KEY_VAULT:
            vault_url = kwargs.get('vault_url')
            credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=vault_url, credential=credential)
        elif self.provider == SecretProvider.GCP_SECRET_MANAGER:
            self.client = secretmanager.SecretManagerServiceClient()
            self.project_id = kwargs.get('project_id')
        elif self.provider == SecretProvider.LOCAL_ENCRYPTED:
            self.encryption_key = kwargs.get('encryption_key') or self._generate_encryption_key()
        else:
            raise ValueError(f"Unsupported secret provider: {self.provider}")
    
    def store_secret(self, secret_name: str, secret_value: str) -> bool:
        """Store a secret"""



        try:
            if self.provider == SecretProvider.AWS_SECRETS_MANAGER:
                self.client.create_secret(Name=secret_name, SecretString=secret_value)
            elif self.provider == SecretProvider.AZURE_KEY_VAULT:
                self.client.set_secret(secret_name, secret_value)
            elif self.provider == SecretProvider.GCP_SECRET_MANAGER:
                parent = f"projects/{self.project_id}"
                secret = {"replication": {"automatic": {}}}
                secret_response = self.client.create_secret(
                    request={"parent": parent, "secret_id": secret_name, "secret": secret}
                )
                self.client.add_secret_version(
                    request={"parent": secret_response.name, "payload": {"data": secret_value.encode()}}
                )
            elif self.provider == SecretProvider.LOCAL_ENCRYPTED:
                encrypted_value = self._encrypt_value(secret_value)
                with open(f".secrets/{secret_name}", 'w') as f:
                    f.write(encrypted_value)
            
            self.logger.info(f"Stored secret: {secret_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing secret {secret_name}: {str(e)}")
            return False
    
    def retrieve_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve a secret"""



        try:
            if self.provider == SecretProvider.AWS_SECRETS_MANAGER:
                response = self.client.get_secret_value(SecretId=secret_name)
                return response['SecretString']
            elif self.provider == SecretProvider.AZURE_KEY_VAULT:
                secret = self.client.get_secret(secret_name)
                return secret.value
            elif self.provider == SecretProvider.GCP_SECRET_MANAGER:
                name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                response = self.client.access_secret_version(request={"name": name})
                return response.payload.data.decode()
            elif self.provider == SecretProvider.LOCAL_ENCRYPTED:
                with open(f".secrets/{secret_name}", 'r') as f:
                    encrypted_value = f.read()
                return self._decrypt_value(encrypted_value)
            
        except Exception as e:
            self.logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            return None
    
    def delete_secret(self, secret_name: str) -> bool:
        """Delete a secret"""



        try:
            if self.provider == SecretProvider.AWS_SECRETS_MANAGER:
                self.client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)
            elif self.provider == SecretProvider.AZURE_KEY_VAULT:
                self.client.begin_delete_secret(secret_name)
            elif self.provider == SecretProvider.GCP_SECRET_MANAGER:
                name = f"projects/{self.project_id}/secrets/{secret_name}"
                self.client.delete_secret(request={"name": name})
            elif self.provider == SecretProvider.LOCAL_ENCRYPTED:
                os.remove(f".secrets/{secret_name}")
            
            self.logger.info(f"Deleted secret: {secret_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting secret {secret_name}: {str(e)}")
            return False
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for local storage"""
        password = os.environ.get('ENCRYPTION_PASSWORD', 'default-password')
        salt = os.environ.get('ENCRYPTION_SALT', 'default-salt').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a value for local storage"""
        f = Fernet(self.encryption_key)
        encrypted_value = f.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted_value).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value from local storage"""
        f = Fernet(self.encryption_key)
        decoded_value = base64.urlsafe_b64decode(encrypted_value.encode())
        decrypted_value = f.decrypt(decoded_value)
        return decrypted_value.decode()


class ConfigTemplateEngine:
    """Template engine for dynamic configuration generation"""
    
    def __init__(self):
        self.template_env = jinja2.Environment(
            loader=jinja2.DictLoader({}),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        self.logger = logging.getLogger(__name__)
    
    def render_config_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Render configuration template with variables"""



        try:
            template = self.template_env.from_string(template_content)
            return template.render(**variables)
        except Exception as e:
            self.logger.error(f"Error rendering template: {str(e)}")
            raise
    
    def generate_kubernetes_config(self, app_config: ApplicationConfig) -> Dict[str, str]:
        """Generate Kubernetes configuration from application config"""
        
        # ConfigMap template
        configmap_template = '''
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ app_name }}-config
  namespace: {{ namespace }}
data:
  app-config.yaml: |
    name: {{ app_name }}
    version: {{ app_version }}
    host: {{ app_host }}
    port: {{ app_port }}
    workers: {{ app_workers }}
    debug: {{ app_debug }}
    timezone: {{ app_timezone }}
    language: {{ app_language }}
    
    monitoring:
      prometheus_enabled: {{ monitoring_prometheus }}
      grafana_enabled: {{ monitoring_grafana }}
      logging_level: {{ logging_level }}
      metrics_port: {{ metrics_port }}
      
    security:
      encryption_enabled: {{ security_encryption }}
      cors_origins: {{ cors_origins | tojson }}
      rate_limiting_enabled: {{ rate_limiting }}
      ssl_required: {{ ssl_required }}
      
    ai:
      fingerprinting_enabled: {{ ai_fingerprinting }}
      content_protection_enabled: {{ ai_content_protection }}
      batch_size: {{ ai_batch_size }}
      similarity_threshold: {{ ai_similarity_threshold }}
'''
        
        # Secret template
        secret_template = '''
apiVersion: v1
kind: Secret
metadata:
  name: {{ app_name }}-secrets
  namespace: {{ namespace }}
type: Opaque
data:
  database-url: {{ database_url | b64encode }}
  redis-url: {{ redis_url | b64encode }}
  jwt-secret: {{ jwt_secret | b64encode }}
  s3-access-key: {{ s3_access_key | b64encode }}
  s3-secret-key: {{ s3_secret_key | b64encode }}
'''
        
        variables = {
            'app_name': app_config.name.lower().replace(' ', '-'),
            'namespace': 'ia-influencer',
            'app_version': app_config.version,
            'app_host': app_config.host,
            'app_port': app_config.port,
            'app_workers': app_config.workers,
            'app_debug': str(app_config.debug).lower(),
            'app_timezone': app_config.timezone,
            'app_language': app_config.language,
            'monitoring_prometheus': str(app_config.monitoring.prometheus_enabled).lower(),
            'monitoring_grafana': str(app_config.monitoring.grafana_enabled).lower(),
            'logging_level': app_config.monitoring.logging_level,
            'metrics_port': app_config.monitoring.metrics_port,
            'security_encryption': str(app_config.security.encryption_enabled).lower(),
            'cors_origins': app_config.security.cors_origins,
            'rate_limiting': str(app_config.security.rate_limiting_enabled).lower(),
            'ssl_required': str(app_config.security.ssl_required).lower(),
            'ai_fingerprinting': str(app_config.ai.fingerprinting_enabled).lower(),
            'ai_content_protection': str(app_config.ai.content_protection_enabled).lower(),
            'ai_batch_size': app_config.ai.batch_size,
            'ai_similarity_threshold': app_config.ai.similarity_threshold,
            'database_url': app_config.database.get_connection_string(),
            'redis_url': app_config.redis.get_connection_url(),
            'jwt_secret': app_config.security.jwt_secret_key,
            's3_access_key': app_config.storage.s3_access_key,
            's3_secret_key': app_config.storage.s3_secret_key
        }
        
        # Add custom Jinja2 filters
        self.template_env.filters['b64encode'] = lambda x: base64.b64encode(x.encode()).decode()
        
        configmap_yaml = self.render_config_template(configmap_template, variables)
        secret_yaml = self.render_config_template(secret_template, variables)
        
        return {
            'configmap.yaml': configmap_yaml,
            'secret.yaml': secret_yaml
        }


class EnvironmentConfigManager:
    """Manager for environment-specific configurations"""
    
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.config_managers: Dict[EnvironmentType, FileConfigManager] = {}
        self.secret_manager: Optional[SecretManager] = None
        self.template_engine = ConfigTemplateEngine()
        self.logger = logging.getLogger(__name__)
        
        # Initialize config managers for each environment
        for env_type in EnvironmentType:
            self.config_managers[env_type] = FileConfigManager(env_type, config_dir)
    
    def set_secret_manager(self, secret_manager: SecretManager):
        """Set the secret manager"""
        self.secret_manager = secret_manager
    
    def load_environment_config(self, environment: EnvironmentType, 
                              config_name: str = "app") -> ApplicationConfig:
        """Load configuration for specific environment"""
        manager = self.config_managers.get(environment)
        if not manager:
            raise ValueError(f"No config manager for environment: {environment}")
        
        config = manager.load_config(config_name)
        
        # Load secrets if secret manager is available
        if self.secret_manager:
            config = self._load_secrets_into_config(config, environment)
        
        return config
    
    def save_environment_config(self, environment: EnvironmentType, 
                              config: ApplicationConfig, 
                              config_name: str = "app") -> bool:
        """Save configuration for specific environment"""
        manager = self.config_managers.get(environment)
        if not manager:
            raise ValueError(f"No config manager for environment: {environment}")
        
        # Save secrets if secret manager is available
        if self.secret_manager:
            self._save_secrets_from_config(config, environment)
        
        return manager.save_config(config, config_name)
    
    def validate_all_environments(self) -> Dict[EnvironmentType, Dict[str, bool]]:
        """Validate configurations for all environments"""
        results = {}
        
        for env_type in EnvironmentType:
            try:
                config = self.load_environment_config(env_type)
                manager = self.config_managers[env_type]
                results[env_type] = manager.validate_config(config)
            except Exception as e:
                self.logger.error(f"Error validating {env_type}: {str(e)}")
                results[env_type] = {'error': str(e)}
        
        return results
    
    def generate_kubernetes_configs(self, environment: EnvironmentType) -> Dict[str, str]:
        """Generate Kubernetes configurations for environment"""
        config = self.load_environment_config(environment)
        return self.template_engine.generate_kubernetes_config(config)
    
    def _load_secrets_into_config(self, config: ApplicationConfig, 
                                environment: EnvironmentType) -> ApplicationConfig:
        """Load secrets from secret manager into configuration"""
        env_prefix = environment.value
        
        # Load database password
        db_password = self.secret_manager.retrieve_secret(f"{env_prefix}-database-password")
        if db_password:
            config.database.password = db_password
        
        # Load Redis password
        redis_password = self.secret_manager.retrieve_secret(f"{env_prefix}-redis-password")
        if redis_password:
            config.redis.password = redis_password
        
        # Load JWT secret
        jwt_secret = self.secret_manager.retrieve_secret(f"{env_prefix}-jwt-secret")
        if jwt_secret:
            config.security.jwt_secret_key = jwt_secret
        
        # Load S3 credentials
        s3_access_key = self.secret_manager.retrieve_secret(f"{env_prefix}-s3-access-key")
        if s3_access_key:
            config.storage.s3_access_key = s3_access_key
        
        s3_secret_key = self.secret_manager.retrieve_secret(f"{env_prefix}-s3-secret-key")
        if s3_secret_key:
            config.storage.s3_secret_key = s3_secret_key
        
        return config
    
    def _save_secrets_from_config(self, config: ApplicationConfig, 
                                environment: EnvironmentType):
        """Save secrets from configuration to secret manager"""
        env_prefix = environment.value
        
        # Save database password
        if config.database.password:
            self.secret_manager.store_secret(
                f"{env_prefix}-database-password", 
                config.database.password
            )
        
        # Save Redis password
        if config.redis.password:
            self.secret_manager.store_secret(
                f"{env_prefix}-redis-password", 
                config.redis.password
            )
        
        # Save JWT secret
        if config.security.jwt_secret_key:
            self.secret_manager.store_secret(
                f"{env_prefix}-jwt-secret", 
                config.security.jwt_secret_key
            )
        
        # Save S3 credentials
        if config.storage.s3_access_key:
            self.secret_manager.store_secret(
                f"{env_prefix}-s3-access-key", 
                config.storage.s3_access_key
            )
        
        if config.storage.s3_secret_key:
            self.secret_manager.store_secret(
                f"{env_prefix}-s3-secret-key", 
                config.storage.s3_secret_key
            )


# Utility functions
def generate_secure_password(length: int = 32) -> str:
    """Generate a secure random password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret() -> str:
    """Generate a secure JWT secret"""



    return secrets.token_urlsafe(64)


def create_default_environment_configs(config_dir: str) -> Dict[EnvironmentType, ApplicationConfig]:
    """Create default configurations for all environments"""
    configs = {}
    
    for env_type in EnvironmentType:
        config = ApplicationConfig(
            name="IA Influencer Platform",
            version="1.0.0",
            debug=env_type == EnvironmentType.DEVELOPMENT,
            testing=env_type == EnvironmentType.TESTING,
            secret_key=generate_secure_password(64),
            database=DatabaseConfig(
                host=f"ia-influencer-postgresql-{env_type.value}",
                port=5432,
                database="ia_influencer_platform",
                username="iainfluencer",
                password=generate_secure_password(32)
            ),
            redis=RedisConfig(
                host=f"ia-influencer-redis-{env_type.value}",
                password=generate_secure_password(32)
            ),
            security=SecurityConfig(
                jwt_secret_key=generate_jwt_secret(),
                cors_origins=["*"] if env_type == EnvironmentType.DEVELOPMENT else [],
                rate_limit_per_minute=1000 if env_type == EnvironmentType.DEVELOPMENT else 100
            ),
            storage=StorageConfig(
                s3_bucket=f"ia-influencer-{env_type.value}",
                s3_region="us-east-1",
                s3_access_key="",
                s3_secret_key=""
            ),
            metadata=ConfigMetadata(
                name="app",
                environment=env_type,
                version="1.0.0",
                created_by="system",
                created_at="",
                updated_at="",
                checksum=""
            )
        )
        
        configs[env_type] = config
    
    return configs
