"""Configuration Management for Intent Recognition

Centralized configuration system for intent recognition components with
environment-specific settings, model parameters, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging

from ...core.config import BaseConfig


@dataclass
class ModelConfiguration:
    """Model-specific configuration parameters"""    
    # Transformer model settings
    transformer_model_name: str = "distilbert-base-uncased"
    custom_model_path: Optional[str] = None
    model_version: str = "2.0.0"
    max_sequence_length: int = 512
    
    # Ensemble model settings
    ensemble_models_path: Optional[str] = None
    use_ensemble: bool = True
    
    # TF-IDF settings
    tfidf_max_features: int = 10000
    
    # Random Forest settings
    rf_n_estimators: int = 100
    rf_max_depth: int = 20
    
    # spaCy model
    spacy_model: str = "en_core_web_sm"
    
    # Model paths
    models_dir: str = "models/intent_recognition"
    checkpoints_dir: str = "checkpoints/intent_recognition"
    
    # Calibration settings
    calibration_data_path: Optional[str] = None
    use_confidence_calibration: bool = True


@dataclass 
class PerformanceSettings:
    """Performance and optimization settings"""    
    # Processing settings
    processor_threads: int = 4
    max_queue_size: int = 1000
    max_requests_per_second: int = 100
    
    # Cache settings
    cache_ttl_seconds: int = 300  # 5 minutes
    max_cache_size: int = 10000
    cache_cleanup_interval_seconds: int = 600  # 10 minutes
    
    # Timeout settings
    default_timeout_ms: int = 500
    batch_timeout_ms: int = 5000
    streaming_timeout_ms: int = 100
    
    # Metrics settings
    metrics_interval_seconds: int = 60
    enable_detailed_metrics: bool = True
    
    # Memory management
    max_memory_mb: int = 1024
    gc_threshold: int = 10000


@dataclass
class ConfidenceSettings:
    """Confidence scoring and uncertainty quantification settings"""    
    # Temperature scaling
    temperature_scaling: float = 1.0
    temperature_optimization_enabled: bool = True
    
    # Ensemble settings
    ensemble_size: int = 5
    ensemble_voting_method: str = "weighted_average"
    
    # Uncertainty thresholds
    high_confidence_threshold: float = 0.85
    medium_confidence_threshold: float = 0.65
    low_confidence_threshold: float = 0.45
    
    # Calibration settings
    calibration_method: str = "isotonic"
    calibration_enabled: bool = True
    recalibration_frequency: int = 1000  # samples
    
    # Uncertainty quantification
    enable_epistemic_uncertainty: bool = True
    enable_aleatoric_uncertainty: bool = True
    uncertainty_estimation_method: str = "ensemble_variance"
    
    # Out-of-distribution detection
    ood_detection_enabled: bool = True
    ood_threshold: float = 0.3
    
    # Confidence explanation
    enable_explanations: bool = True
    explanation_detail_level: str = "medium"


@dataclass
class ContextualSettings:
    """Contextual processing configuration"""    
    # Context types and weights
    enable_conversation_context: bool = True
    enable_user_profile_context: bool = True
    enable_temporal_context: bool = True
    enable_business_context: bool = True
    enable_environmental_context: bool = False
    
    # Context window sizes
    conversation_history_window: int = 20
    intent_pattern_window: int = 10
    sentiment_history_window: int = 5
    
    # Context cache settings
    context_cache_ttl: int = 3600  # 1 hour
    max_cached_sessions: int = 10000
    
    # Enhancement thresholds
    minimum_enhancement_threshold: float = 0.1
    maximum_enhancement_boost: float = 0.5
    
    # Context conflict resolution
    enable_conflict_detection: bool = True
    conflict_resolution_strategy: str = "weighted_average"
    
    # Temporal context
    business_hours_start: int = 9
    business_hours_end: int = 17
    timezone_awareness: bool = True
    
    # User profile integration
    profile_update_frequency: int = 7  # days
    experience_level_auto_adjustment: bool = True
    
    # Pattern recognition
    enable_intent_pattern_learning: bool = True
    pattern_significance_threshold: int = 3
    
    # Context warnings
    enable_context_warnings: bool = True
    warning_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "low_confidence": 0.3,
        "context_conflict": 0.4,
        "missing_protection": 0.8
    })


@dataclass
class CreativeWorkflowSettings:
    """Creative industry specific workflow settings"""    
    # Creator types
    supported_creator_types: List[str] = field(default_factory=lambda: [
        "musician", "influencer", "photographer", "blogger", 
        "podcaster", "video_creator", "artist", "writer"
    ])
    
    # Platform integrations
    supported_platforms: List[str] = field(default_factory=lambda: [
        "spotify", "instagram", "youtube", "tiktok", "soundcloud",
        "bandcamp", "twitter", "facebook", "pinterest", "twitch"
    ])
    
    # Content types
    supported_content_types: List[str] = field(default_factory=lambda: [
        "audio", "video", "image", "text", "livestream", "podcast"
    ])
    
    # Workflow stages
    workflow_stages: List[str] = field(default_factory=lambda: [
        "creation", "editing", "protection", "upload", "promotion",
        "analytics", "monetization", "collaboration"
    ])
    
    # Intent categories for creators
    creator_intent_categories: Dict[str, List[str]] = field(default_factory=lambda: {
        "content_creation": [
            "create_music", "create_video", "create_image", "create_post",
            "edit_content", "mix_audio", "color_grade", "apply_effects"
        ],
        "content_management": [
            "upload_content", "organize_files", "backup_content",
            "version_control", "metadata_management"
        ],
        "protection_and_rights": [
            "protect_content", "copyright_registration", "dmca_takedown",
            "rights_management", "license_content", "watermark_content"
        ],
        "distribution_and_promotion": [
            "publish_content", "schedule_posts", "cross_platform_sharing",
            "seo_optimization", "hashtag_generation", "audience_targeting"
        ],
        "analytics_and_insights": [
            "view_analytics", "track_performance", "audience_analysis",
            "revenue_tracking", "engagement_metrics", "trend_analysis"
        ],
        "collaboration_and_networking": [
            "find_collaborators", "manage_partnerships", "brand_deals",
            "influencer_matching", "contract_management", "team_coordination"
        ],
        "monetization": [
            "setup_monetization", "track_revenue", "payment_processing",
            "tax_reporting", "subscription_management", "donation_setup"
        ]
    })
    
    # Business model support
    monetization_models: List[str] = field(default_factory=lambda: [
        "streaming_royalties", "brand_partnerships", "merchandise",
        "subscriptions", "donations", "licensing", "live_performances",
        "online_courses", "affiliate_marketing"
    ])


@dataclass
class SecuritySettings:
    """Security and validation settings"""    
    # Input validation
    max_text_length: int = 10000
    min_text_length: int = 1
    allowed_languages: List[str] = field(default_factory=lambda: ["en", "de", "fr", "es", "it"])
    
    # Rate limiting
    rate_limit_per_user: int = 1000  # requests per hour
    rate_limit_per_ip: int = 5000    # requests per hour
    rate_limit_burst: int = 50       # burst requests
    
    # Content filtering
    enable_content_filtering: bool = True
    blocked_patterns: List[str] = field(default_factory=list)
    
    # Privacy settings
    anonymize_logs: bool = True
    data_retention_days: int = 30
    
    # API security
    require_authentication: bool = True
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=list)


@dataclass
class IntegrationSettings:
    """Integration settings for external services"""    
    # Database settings
    use_database_cache: bool = True
    cache_database_url: Optional[str] = None
    
    # Message queue settings
    use_message_queue: bool = False
    message_queue_url: Optional[str] = None
    
    # Monitoring integration
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # Logging integration
    log_level: str = "INFO"
    log_format: str = "json"
    log_file_path: Optional[str] = None
    
    # External AI services
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # Webhooks
    webhook_urls: List[str] = field(default_factory=list)
    webhook_events: List[str] = field(default_factory=lambda: ["classification_complete", "error"])


class IntentRecognitionConfig(BaseConfig):
    """    Main configuration class for intent recognition system
    
    Provides centralized configuration management with:
    - Environment-specific settings
    - Model parameter management
    - Performance optimization
    - Security and validation rules
    - Integration settings
    """    
    def __init__(
        self,
        environment: str = "development",
        config_file: Optional[str] = None,
        **kwargs
    ):
        super().__init__()
        
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        
        # Initialize configuration sections
        self.model = ModelConfiguration()
        self.performance = PerformanceSettings()
        self.security = SecuritySettings()
        self.integration = IntegrationSettings()
        self.confidence_config = ConfidenceSettings()
        self.contextual_config = ContextualSettings()
        self.creative_workflow_config = CreativeWorkflowSettings()
        
        # Load configuration
        self._load_configuration(config_file, **kwargs)
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_configuration(self, config_file: Optional[str] = None, **kwargs) -> None:
        """Load configuration from multiple sources"""        
        # 1. Load from environment variables
        self._load_from_environment()
        
        # 2. Load from configuration file if provided
        if config_file:
            self._load_from_file(config_file)
        
        # 3. Override with explicit parameters
        self._apply_overrides(**kwargs)
        
        # 4. Apply environment-specific settings
        self._apply_environment_settings()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""        
        # Model configuration
        if os.getenv("INTENT_TRANSFORMER_MODEL"):
            self.model.transformer_model_name = os.getenv("INTENT_TRANSFORMER_MODEL")
        
        if os.getenv("INTENT_CUSTOM_MODEL_PATH"):
            self.model.custom_model_path = os.getenv("INTENT_CUSTOM_MODEL_PATH")
        
        if os.getenv("INTENT_MAX_SEQUENCE_LENGTH"):
            self.model.max_sequence_length = int(os.getenv("INTENT_MAX_SEQUENCE_LENGTH"))
        
        # Performance configuration
        if os.getenv("INTENT_PROCESSOR_THREADS"):
            self.performance.processor_threads = int(os.getenv("INTENT_PROCESSOR_THREADS"))
        
        if os.getenv("INTENT_MAX_QUEUE_SIZE"):
            self.performance.max_queue_size = int(os.getenv("INTENT_MAX_QUEUE_SIZE"))
        
        if os.getenv("INTENT_CACHE_TTL"):
            self.performance.cache_ttl_seconds = int(os.getenv("INTENT_CACHE_TTL"))
        
        # Security configuration
        if os.getenv("INTENT_MAX_TEXT_LENGTH"):
            self.security.max_text_length = int(os.getenv("INTENT_MAX_TEXT_LENGTH"))
        
        if os.getenv("INTENT_RATE_LIMIT_PER_USER"):
            self.security.rate_limit_per_user = int(os.getenv("INTENT_RATE_LIMIT_PER_USER"))
        
        # Integration configuration
        if os.getenv("INTENT_DATABASE_URL"):
            self.integration.cache_database_url = os.getenv("INTENT_DATABASE_URL")
        
        if os.getenv("OPENAI_API_KEY"):
            self.integration.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("HUGGINGFACE_API_KEY"):
            self.integration.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON/YAML file"""        try:
            config_path = Path(config_file)
            
            if not config_path.exists():
                self.logger.warning(f"Configuration file not found: {config_file}")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    # Assume YAML
                    import yaml
                    config_data = yaml.safe_load(f)
            
            # Apply configuration sections
            if 'model' in config_data:
                self._update_dataclass(self.model, config_data['model'])
            
            if 'performance' in config_data:
                self._update_dataclass(self.performance, config_data['performance'])
            
            if 'security' in config_data:
                self._update_dataclass(self.security, config_data['security'])
            
            if 'integration' in config_data:
                self._update_dataclass(self.integration, config_data['integration'])
            
            self.logger.info(f"Configuration loaded from: {config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from file: {str(e)}")
    
    def _update_dataclass(self, obj: Any, updates: Dict[str, Any]) -> None:
        """Update dataclass fields from dictionary"""        for key, value in updates.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
            else:
                self.logger.warning(f"Unknown configuration key: {key}")
    
    def _apply_overrides(self, **kwargs) -> None:
        """Apply explicit parameter overrides"""        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif hasattr(self.model, key):
                setattr(self.model, key, value)
            elif hasattr(self.performance, key):
                setattr(self.performance, key, value)
            elif hasattr(self.security, key):
                setattr(self.security, key, value)
            elif hasattr(self.integration, key):
                setattr(self.integration, key, value)
            else:
                self.logger.warning(f"Unknown configuration override: {key}")
    
    def _apply_environment_settings(self) -> None:
        """Apply environment-specific configuration adjustments"""        
        if self.environment == "development":
            # Development optimizations
            self.performance.processor_threads = 2
            self.performance.max_queue_size = 100
            self.performance.cache_ttl_seconds = 60
            self.security.require_authentication = False
            self.integration.log_level = "DEBUG"
            
        elif self.environment == "testing":
            # Testing optimizations
            self.performance.processor_threads = 1
            self.performance.max_queue_size = 50
            self.performance.cache_ttl_seconds = 30
            self.security.require_authentication = False
            self.integration.log_level = "WARNING"
            
        elif self.environment == "staging":
            # Staging settings (production-like but with reduced resources)
            self.performance.processor_threads = 3
            self.performance.max_queue_size = 500
            self.performance.cache_ttl_seconds = 180
            self.security.require_authentication = True
            self.integration.log_level = "INFO"
            
        elif self.environment == "production":
            # Production optimizations
            self.performance.processor_threads = 8
            self.performance.max_queue_size = 2000
            self.performance.cache_ttl_seconds = 600
            self.security.require_authentication = True
            self.security.anonymize_logs = True
            self.integration.log_level = "WARNING"
            self.integration.prometheus_enabled = True
        
        self.logger.info(f"Applied {self.environment} environment settings")
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings"""        
        errors = []
        
        # Validate model configuration
        if self.model.max_sequence_length <= 0:
            errors.append("max_sequence_length must be positive")
        
        if self.model.max_sequence_length > 2048:
            errors.append("max_sequence_length too large (max: 2048)")
        
        # Validate performance configuration
        if self.performance.processor_threads <= 0:
            errors.append("processor_threads must be positive")
        
        if self.performance.max_queue_size <= 0:
            errors.append("max_queue_size must be positive")
        
        if self.performance.cache_ttl_seconds <= 0:
            errors.append("cache_ttl_seconds must be positive")
        
        # Validate security configuration
        if self.security.max_text_length <= self.security.min_text_length:
            errors.append("max_text_length must be greater than min_text_length")
        
        if self.security.rate_limit_per_user <= 0:
            errors.append("rate_limit_per_user must be positive")
        
        # Validate integration configuration
        if self.integration.prometheus_port <= 0 or self.integration.prometheus_port > 65535:
            errors.append("prometheus_port must be valid port number")
        
        if errors:
            error_message = "Configuration validation failed: " + "; ".join(errors)
            self.logger.error(error_message)
            raise ValueError(error_message)
        
        self.logger.info("Configuration validation passed")
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration as dictionary"""        return {
            'transformer_model_name': self.model.transformer_model_name,
            'custom_model_path': self.model.custom_model_path,
            'model_version': self.model.model_version,
            'max_sequence_length': self.model.max_sequence_length,
            'ensemble_models_path': self.model.ensemble_models_path,
            'use_ensemble': self.model.use_ensemble,
            'spacy_model': self.model.spacy_model
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration as dictionary"""        return {
            'processor_threads': self.performance.processor_threads,
            'max_queue_size': self.performance.max_queue_size,
            'max_requests_per_second': self.performance.max_requests_per_second,
            'cache_ttl_seconds': self.performance.cache_ttl_seconds,
            'max_cache_size': self.performance.max_cache_size,
            'default_timeout_ms': self.performance.default_timeout_ms
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration as dictionary"""        return {
            'max_text_length': self.security.max_text_length,
            'min_text_length': self.security.min_text_length,
            'allowed_languages': self.security.allowed_languages,
            'rate_limit_per_user': self.security.rate_limit_per_user,
            'enable_content_filtering': self.security.enable_content_filtering,
            'require_authentication': self.security.require_authentication
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire configuration to dictionary"""        return {
            'environment': self.environment,
            'model': self.get_model_config(),
            'performance': self.get_performance_config(),
            'security': self.get_security_config(),
            'integration': {
                'use_database_cache': self.integration.use_database_cache,
                'prometheus_enabled': self.integration.prometheus_enabled,
                'log_level': self.integration.log_level,
                'log_format': self.integration.log_format
            }
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save current configuration to file"""        try:
            config_dict = self.to_dict()
            
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                if file_path_obj.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2)
                else:
                    # Assume YAML
                    import yaml
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            raise
    
    @classmethod
    def load_from_file(cls, file_path: str, environment: str = "development") -> 'IntentRecognitionConfig':
        """Create configuration instance from file"""        return cls(environment=environment, config_file=file_path)
    
    @classmethod
    def create_default(cls, environment: str = "development") -> 'IntentRecognitionConfig':
        """Create default configuration for specified environment"""        return cls(environment=environment)
    
    def __str__(self) -> str:
        """String representation of configuration"""        return f"IntentRecognitionConfig(environment={self.environment}, model={self.model.transformer_model_name})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""        return (
            f"IntentRecognitionConfig("
            f"environment={self.environment}, "
            f"model={self.model.transformer_model_name}, "
            f"threads={self.performance.processor_threads}, "
            f"cache_ttl={self.performance.cache_ttl_seconds}"
            f")"
        )


# Convenience functions for common configurations

def get_development_config() -> IntentRecognitionConfig:
    """Get development configuration"""    return IntentRecognitionConfig.create_default("development")


def get_production_config() -> IntentRecognitionConfig:
    """Get production configuration"""    return IntentRecognitionConfig.create_default("production")


def get_testing_config() -> IntentRecognitionConfig:
    """Get testing configuration"""    return IntentRecognitionConfig.create_default("testing")


# Configuration constants
DEFAULT_MODEL_NAME = "distilbert-base-uncased"
DEFAULT_CACHE_TTL = 300
DEFAULT_MAX_SEQUENCE_LENGTH = 512
DEFAULT_PROCESSOR_THREADS = 4
DEFAULT_MAX_QUEUE_SIZE = 1000
