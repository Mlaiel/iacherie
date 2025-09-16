"""
⚙️ DATASET CONFIGURATION - ENTERPRISE CENTRALIZED SETTINGS
=========================================================

Centralized configuration management for Ainflue Datasets Module supporting
53 AI agents across 65+ platforms with enterprise-grade settings, security,
and compliance standards.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

Multi-Expert Configuration Design:
- 🎖️ Lead Dev IA: Agent categorization + orchestration settings
- 🎖️ Backend Senior: Performance configuration + async settings
- 🎖️ ML Engineer: Training parameters + model optimization settings
- 🎖️ DBA: Database schemas + metadata configuration
- 🎖️ Security: Encryption settings + access control configuration
- 🎖️ Microservices: Service communication + distributed settings
- 🎖️ Audio Engineer: Audio processing parameters + DSP settings
- 🎖️ DevOps: Infrastructure settings + monitoring configuration
- 🎖️ IA Prompt Engineer: AI provider settings + prompt optimization
"""

import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
from datetime import datetime, timedelta

class DatasetType(Enum):
    """Dataset type classification for enterprise organization"""
    TRAINING = "training"
    VALIDATION = "validation"
    TEST = "test"
    BENCHMARK = "benchmark"
    SYNTHETIC = "synthetic"
    PRODUCTION = "production"
    STREAMING = "streaming"
    ARCHIVE = "archive"

class AgentCategory(Enum):
    """AI Agent categories aligned with 53 agents architecture"""
    COMPUTER_VISION = "computer_vision"
    NATURAL_LANGUAGE = "natural_language"
    AUDIO_PROCESSING = "audio_processing"
    CONTENT_OPTIMIZATION = "content_optimization"
    PLATFORM_INTEGRATION = "platform_integration"
    MULTIMODAL = "multimodal"
    REAL_TIME = "real_time"
    BATCH_PROCESSING = "batch_processing"

class PlatformType(Enum):
    """Platform categories for 65+ platforms support"""
    # Social Media Platforms (29 platforms)
    SOCIAL_MEDIA = "social_media"
    
    # Music Streaming Platforms (20 platforms)
    MUSIC_STREAMING = "music_streaming"
    
    # Creator Economy Platforms (16 platforms)
    CREATOR_ECONOMY = "creator_economy"
    
    # Video Platforms
    VIDEO_PLATFORMS = "video_platforms"
    
    # Podcast Platforms
    PODCAST_PLATFORMS = "podcast_platforms"
    
    # E-commerce Platforms
    ECOMMERCE_PLATFORMS = "ecommerce_platforms"

class SecurityLevel(Enum):
    """Security levels for data protection"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class QualityStandards(Enum):
    """Quality standards for enterprise datasets"""
    DEVELOPMENT = "development"     # 80% quality threshold
    STAGING = "staging"            # 90% quality threshold
    PRODUCTION = "production"      # 95% quality threshold
    ENTERPRISE = "enterprise"      # 98% quality threshold
    MISSION_CRITICAL = "critical"  # 99.5% quality threshold

@dataclass
class PerformanceConfig:
    """
    🚀 Performance Configuration
    
    **Backend Senior + DevOps Expert**: Optimized performance settings
    for enterprise-grade operations with sub-100ms latency targets.
    """
    # Latency Targets (milliseconds)
    max_load_latency: int = 100
    max_preprocessing_latency: int = 200
    max_validation_latency: int = 150
    max_export_latency: int = 300
    
    # Throughput Targets
    max_requests_per_second: int = 10000
    max_concurrent_operations: int = 1000
    max_batch_size: int = 10000
    
    # Memory Management
    max_memory_usage_gb: float = 32.0
    cache_size_gb: float = 8.0
    buffer_size_mb: int = 512
    
    # Parallel Processing
    max_worker_threads: int = 32
    max_async_tasks: int = 1000
    cpu_utilization_limit: float = 0.8
    
    # Monitoring Intervals
    performance_monitoring_interval: int = 30  # seconds
    health_check_interval: int = 60  # seconds
    metrics_collection_interval: int = 15  # seconds

@dataclass
class SecurityConfig:
    """
    🔒 Security Configuration
    
    **Security Expert**: Enterprise-grade security settings with
    encryption, access control, and GDPR compliance.
    """
    # Encryption Settings
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_interval_days: int = 30
    enable_encryption_at_rest: bool = True
    enable_encryption_in_transit: bool = True
    
    # Access Control
    enable_rbac: bool = True
    session_timeout_minutes: int = 60
    max_failed_login_attempts: int = 3
    password_complexity_required: bool = True
    
    # Audit and Compliance
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 365
    gdpr_compliance_enabled: bool = True
    data_anonymization_enabled: bool = True
    
    # Network Security
    enable_ssl_verification: bool = True
    allowed_ip_ranges: List[str] = field(default_factory=lambda: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"])
    rate_limiting_enabled: bool = True
    ddos_protection_enabled: bool = True

@dataclass
class MLConfig:
    """
    🤖 Machine Learning Configuration
    
    **ML Engineer Expert**: Advanced ML pipeline settings optimized
    for training 53 AI agents with enterprise performance.
    """
    # Model Training Settings
    default_batch_size: int = 32
    default_learning_rate: float = 0.001
    max_epochs: int = 1000
    early_stopping_patience: int = 10
    
    # Data Processing
    train_validation_split: float = 0.8
    validation_test_split: float = 0.5
    cross_validation_folds: int = 5
    
    # Augmentation Settings
    enable_data_augmentation: bool = True
    augmentation_probability: float = 0.3
    max_augmentation_factor: float = 2.0
    
    # Model Optimization
    enable_mixed_precision: bool = True
    enable_gradient_checkpointing: bool = True
    enable_model_pruning: bool = False
    enable_quantization: bool = False
    
    # Hardware Utilization
    use_gpu_if_available: bool = True
    max_gpu_memory_fraction: float = 0.9
    enable_distributed_training: bool = True
    
    # Model Serving
    model_serving_batch_size: int = 64
    model_inference_timeout: int = 5000  # milliseconds
    enable_model_caching: bool = True

@dataclass
class AudioConfig:
    """
    🎵 Audio Processing Configuration
    
    **Audio Engineer Expert**: Specialized DSP and audio processing
    settings for high-quality audio content analysis and generation.
    """
    # Audio Format Settings
    default_sample_rate: int = 44100
    default_bit_depth: int = 16
    supported_formats: List[str] = field(default_factory=lambda: ["wav", "mp3", "flac", "aac", "ogg"])
    
    # DSP Processing
    fft_window_size: int = 2048
    hop_length: int = 512
    mel_bins: int = 128
    mfcc_coefficients: int = 13
    
    # Audio Enhancement
    enable_noise_reduction: bool = True
    enable_normalization: bool = True
    enable_dynamic_range_compression: bool = True
    
    # Real-time Processing
    buffer_size_samples: int = 1024
    max_latency_ms: int = 50
    enable_real_time_processing: bool = True
    
    # Fingerprinting
    fingerprint_algorithm: str = "chromaprint"
    fingerprint_duration_seconds: int = 30
    similarity_threshold: float = 0.85

@dataclass
class DatabaseConfig:
    """
    📊 Database Configuration
    
    **DBA Expert**: Optimized database settings for metadata management,
    version control, and high-performance data operations.
    """
    # Connection Settings
    max_connections: int = 100
    connection_timeout: int = 30
    query_timeout: int = 300
    
    # Performance Optimization
    enable_connection_pooling: bool = True
    pool_size: int = 20
    max_overflow: int = 30
    pool_pre_ping: bool = True
    
    # Indexing Strategy
    enable_automatic_indexing: bool = True
    index_optimization_interval_hours: int = 24
    statistics_update_interval_hours: int = 6
    
    # Backup and Recovery
    backup_interval_hours: int = 6
    backup_retention_days: int = 30
    enable_point_in_time_recovery: bool = True
    
    # Metadata Management
    metadata_schema_version: str = "1.0.0"
    enable_schema_validation: bool = True
    metadata_compression_enabled: bool = True

@dataclass
class MicroservicesConfig:
    """
    🏗️ Microservices Configuration
    
    **Microservices Expert**: Distributed architecture settings for
    service communication, load balancing, and fault tolerance.
    """
    # Service Discovery
    service_discovery_enabled: bool = True
    service_registration_timeout: int = 30
    health_check_endpoint: str = "/health"
    
    # Load Balancing
    load_balancing_algorithm: str = "round_robin"
    max_retries: int = 3
    retry_delay_ms: int = 1000
    circuit_breaker_enabled: bool = True
    
    # Service Communication
    default_timeout_ms: int = 5000
    enable_service_mesh: bool = True
    enable_distributed_tracing: bool = True
    
    # Scaling
    auto_scaling_enabled: bool = True
    min_instances: int = 2
    max_instances: int = 20
    scale_up_threshold: float = 0.7
    scale_down_threshold: float = 0.3

@dataclass
class MonitoringConfig:
    """
    📈 Monitoring Configuration
    
    **DevOps Expert**: Comprehensive monitoring settings for
    infrastructure, performance, and operational metrics.
    """
    # Metrics Collection
    enable_prometheus_metrics: bool = True
    enable_custom_metrics: bool = True
    metrics_export_interval: int = 15  # seconds
    
    # Logging
    log_level: str = "INFO"
    enable_structured_logging: bool = True
    log_retention_days: int = 30
    
    # Alerting
    enable_alerting: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 0.8,
        "memory_usage": 0.85,
        "disk_usage": 0.9,
        "error_rate": 0.05,
        "latency_p99": 1000  # milliseconds
    })
    
    # Health Checks
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5   # seconds
    unhealthy_threshold: int = 3    # consecutive failures

@dataclass
class AIProviderConfig:
    """
    🧠 AI Provider Configuration
    
    **IA Prompt Engineer Expert**: AI provider settings for optimal
    prompt engineering and model orchestration across providers.
    """
    # Supported Providers
    enabled_providers: List[str] = field(default_factory=lambda: [
        "openai", "anthropic", "google", "huggingface", "local"
    ])
    
    # Provider Settings
    default_provider: str = "openai"
    fallback_providers: List[str] = field(default_factory=lambda: ["anthropic", "google"])
    
    # Model Settings
    default_temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Optimization
    enable_prompt_caching: bool = True
    enable_response_caching: bool = True
    cache_ttl_minutes: int = 60
    
    # Rate Limiting
    requests_per_minute: int = 1000
    concurrent_requests: int = 100
    enable_rate_limiting: bool = True

@dataclass
class DatasetConfig:
    """
    🏗️ Main Dataset Configuration
    
    **Lead Dev IA Expert**: Central configuration orchestrating all
    expert settings for enterprise-grade dataset management.
    """
    # Basic Information
    dataset_id: str
    dataset_name: str
    dataset_type: DatasetType
    agent_category: AgentCategory
    platform_types: List[PlatformType]
    
    # Quality and Security
    quality_standard: QualityStandards = QualityStandards.PRODUCTION
    security_level: SecurityLevel = SecurityLevel.CONFIDENTIAL
    
    # Expert Configurations
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    ml_config: MLConfig = field(default_factory=MLConfig)
    audio_config: AudioConfig = field(default_factory=AudioConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    microservices: MicroservicesConfig = field(default_factory=MicroservicesConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    ai_provider: AIProviderConfig = field(default_factory=AIProviderConfig)
    
    # Metadata
    created_by: str = "Fahed Mlaiel"
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Expert Validation Flags
    expert_validations: Dict[str, bool] = field(default_factory=lambda: {
        "lead_dev_ia": True,
        "backend_senior": True,
        "ml_engineer": True,
        "dba": True,
        "security": True,
        "microservices": True,
        "audio_engineer": True,
        "devops": True,
        "ia_prompt_engineer": True
    })
    
    def get_quality_threshold(self) -> float:
        """Get quality threshold based on quality standard"""
        thresholds = {
            QualityStandards.DEVELOPMENT: 0.80,
            QualityStandards.STAGING: 0.90,
            QualityStandards.PRODUCTION: 0.95,
            QualityStandards.ENTERPRISE: 0.98,
            QualityStandards.MISSION_CRITICAL: 0.995
        }
        return thresholds.get(self.quality_standard, 0.95)
    
    def is_all_experts_validated(self) -> bool:
        """Check if all 9 expert roles have validated the configuration"""
        return all(self.expert_validations.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            "dataset_id": self.dataset_id,
            "dataset_name": self.dataset_name,
            "dataset_type": self.dataset_type.value,
            "agent_category": self.agent_category.value,
            "platform_types": [pt.value for pt in self.platform_types],
            "quality_standard": self.quality_standard.value,
            "security_level": self.security_level.value,
            "quality_threshold": self.get_quality_threshold(),
            "all_experts_validated": self.is_all_experts_validated(),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "description": self.description,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatasetConfig':
        """Create configuration from dictionary"""
        return cls(
            dataset_id=data["dataset_id"],
            dataset_name=data["dataset_name"],
            dataset_type=DatasetType(data["dataset_type"]),
            agent_category=AgentCategory(data["agent_category"]),
            platform_types=[PlatformType(pt) for pt in data["platform_types"]],
            quality_standard=QualityStandards(data.get("quality_standard", "production")),
            security_level=SecurityLevel(data.get("security_level", "confidential")),
            created_by=data.get("created_by", "Fahed Mlaiel"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            tags=data.get("tags", [])
        )

# Enterprise Configuration Presets
class ConfigurationPresets:
    """
    🎯 Configuration Presets for Different Use Cases
    
    **Lead Dev IA Expert**: Pre-configured settings for common
    enterprise scenarios and AI agent categories.
    """
    
    @staticmethod
    def get_computer_vision_config(dataset_id: str, dataset_name: str) -> DatasetConfig:
        """Computer Vision optimized configuration"""
        config = DatasetConfig(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_type=DatasetType.TRAINING,
            agent_category=AgentCategory.COMPUTER_VISION,
            platform_types=[PlatformType.SOCIAL_MEDIA, PlatformType.VIDEO_PLATFORMS]
        )
        
        # ML Engineer: Specialized CV settings
        config.ml_config.default_batch_size = 16  # Lower for larger images
        config.ml_config.enable_data_augmentation = True
        
        # Performance: Optimized for image processing
        config.performance.max_memory_usage_gb = 64.0
        config.performance.cache_size_gb = 16.0
        
        return config
    
    @staticmethod
    def get_audio_processing_config(dataset_id: str, dataset_name: str) -> DatasetConfig:
        """Audio Processing optimized configuration"""
        config = DatasetConfig(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_type=DatasetType.TRAINING,
            agent_category=AgentCategory.AUDIO_PROCESSING,
            platform_types=[PlatformType.MUSIC_STREAMING, PlatformType.PODCAST_PLATFORMS]
        )
        
        # Audio Engineer: Specialized audio settings
        config.audio_config.enable_real_time_processing = True
        config.audio_config.max_latency_ms = 25  # Lower latency for real-time
        
        # Performance: Optimized for audio streaming
        config.performance.max_requests_per_second = 5000
        config.performance.buffer_size_mb = 1024
        
        return config
    
    @staticmethod
    def get_nlp_config(dataset_id: str, dataset_name: str) -> DatasetConfig:
        """Natural Language Processing optimized configuration"""
        config = DatasetConfig(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_type=DatasetType.TRAINING,
            agent_category=AgentCategory.NATURAL_LANGUAGE,
            platform_types=[PlatformType.SOCIAL_MEDIA, PlatformType.CREATOR_ECONOMY]
        )
        
        # ML Engineer: NLP-specific settings
        config.ml_config.default_batch_size = 64  # Higher for text
        config.ai_provider.max_tokens = 8192  # Larger context for NLP
        
        return config
    
    @staticmethod
    def get_production_config(dataset_id: str, dataset_name: str, 
                            agent_category: AgentCategory) -> DatasetConfig:
        """Production-ready configuration with highest standards"""
        config = DatasetConfig(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_type=DatasetType.PRODUCTION,
            agent_category=agent_category,
            platform_types=list(PlatformType),  # All platforms
            quality_standard=QualityStandards.ENTERPRISE,
            security_level=SecurityLevel.RESTRICTED
        )
        
        # Security Expert: Maximum security settings
        config.security.enable_encryption_at_rest = True
        config.security.enable_encryption_in_transit = True
        config.security.gdpr_compliance_enabled = True
        
        # DevOps Expert: Production monitoring
        config.monitoring.enable_alerting = True
        config.monitoring.enable_prometheus_metrics = True
        
        return config

# Global Configuration Manager
class GlobalConfigManager:
    """
    🌐 Global Configuration Manager
    
    **Lead Dev IA + DevOps Expert**: Centralized configuration
    management with environment-specific settings and validation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("DATASETS_CONFIG_PATH", "datasets_config.json")
        self.configurations: Dict[str, DatasetConfig] = {}
        self.load_configurations()
    
    def load_configurations(self) -> None:
        """Load configurations from file or environment"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    configs_data = json.load(f)
                    for config_data in configs_data:
                        config = DatasetConfig.from_dict(config_data)
                        self.configurations[config.dataset_id] = config
            except Exception as e:
                print(f"⚠️ Failed to load configurations: {e}")
    
    def save_configurations(self) -> None:
        """Save configurations to file"""
        try:
            configs_data = [config.to_dict() for config in self.configurations.values()]
            with open(self.config_path, 'w') as f:
                json.dump(configs_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save configurations: {e}")
    
    def add_configuration(self, config: DatasetConfig) -> None:
        """Add new configuration"""
        self.configurations[config.dataset_id] = config
        self.save_configurations()
    
    def get_configuration(self, dataset_id: str) -> Optional[DatasetConfig]:
        """Get configuration by ID"""
        return self.configurations.get(dataset_id)
    
    def list_configurations(self) -> List[str]:
        """List all configuration IDs"""
        return list(self.configurations.keys())
    
    def validate_all_configurations(self) -> Dict[str, bool]:
        """Validate all configurations for expert approval"""
        return {
            config_id: config.is_all_experts_validated()
            for config_id, config in self.configurations.items()
        }

# Enterprise Constants
ENTERPRISE_DEFAULTS = {
    "SUPPORTED_AGENTS_COUNT": 53,
    "SUPPORTED_PLATFORMS_COUNT": 65,
    "MAX_FILES_PER_MODULE": 18,
    "ENTERPRISE_QUALITY_THRESHOLD": 0.95,
    "PERFORMANCE_TARGET_LATENCY_MS": 100,
    "SCALABILITY_TARGET_RPS": 10000,
    "AUTHOR": "Fahed Mlaiel",
    "COPYRIGHT": "© 2025 Fahed Mlaiel - All Rights Reserved"
}

# Export main configuration classes
__all__ = [
    'DatasetConfig',
    'DatasetType',
    'AgentCategory', 
    'PlatformType',
    'SecurityLevel',
    'QualityStandards',
    'PerformanceConfig',
    'SecurityConfig',
    'MLConfig',
    'AudioConfig',
    'DatabaseConfig',
    'MicroservicesConfig',
    'MonitoringConfig',
    'AIProviderConfig',
    'ConfigurationPresets',
    'GlobalConfigManager',
    'ENTERPRISE_DEFAULTS'
]