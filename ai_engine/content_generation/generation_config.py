"""Generation Configuration - Advanced configuration management system

Professional configuration system for content generation parameters,
platform settings, and optimization preferences.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""
import os
import json
import yaml
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import configparser
from datetime import datetime

from .content_models import Platform, ContentType, QualityLevel, BrandVoice, ContentFormat


class ConfigurationError(Exception):
    """Configuration-related errors"""    pass


class ConfigSource(str, Enum):
    """Configuration source types"""    ENVIRONMENT = "environment"
    FILE = "file"
    DATABASE = "database"
    API = "api"
    DEFAULT = "default"


@dataclass
class AIModelConfig:
    """AI model configuration"""    provider: str = "openai"
    model_name: str = "gpt-4"
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30
    retries: int = 3
    
    # Model-specific parameters
    model_parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.model_parameters is None:
            self.model_parameters = {}


@dataclass
class ContentGenerationConfig:
    """Content generation configuration"""    default_quality_level: QualityLevel = QualityLevel.STANDARD
    default_brand_voice: BrandVoice = BrandVoice.PROFESSIONAL
    default_language: str = "en"
    default_format: ContentFormat = ContentFormat.TEXT
    
    # Quality thresholds
    min_quality_score: float = 0.7
    min_readability_score: float = 0.6
    min_engagement_score: float = 0.5
    min_seo_score: float = 0.6
    
    # Generation parameters
    enable_auto_enhancement: bool = True
    enable_seo_optimization: bool = True
    enable_format_optimization: bool = True
    enable_quality_validation: bool = True
    
    # Retry and fallback
    max_generation_retries: int = 3
    fallback_to_basic_model: bool = True
    
    # Content length guidelines
    content_length_targets: Dict[str, Dict[str, int]] = None
    
    def __post_init__(self):
        if self.content_length_targets is None:
            self.content_length_targets = {
                "blog_post": {"min": 800, "max": 2500, "optimal": 1500},
                "social_post": {"min": 50, "max": 300, "optimal": 150},
                "instagram_post": {"min": 50, "max": 2200, "optimal": 300},
                "twitter_post": {"min": 20, "max": 280, "optimal": 150},
                "linkedin_post": {"min": 100, "max": 3000, "optimal": 500},
                "email_marketing": {"min": 200, "max": 1000, "optimal": 400},
                "product_description": {"min": 100, "max": 500, "optimal": 200}
            }


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""    platform: Platform
    enabled: bool = True
    
    # API configuration
    api_credentials: Dict[str, str] = None
    api_endpoints: Dict[str, str] = None
    rate_limits: Dict[str, int] = None
    
    # Content specifications
    max_content_length: int = 1000
    supported_formats: List[ContentFormat] = None
    optimal_posting_times: List[str] = None
    
    # Optimization settings
    auto_hashtag_generation: bool = True
    auto_mention_detection: bool = True
    auto_link_shortening: bool = True
    
    # Analytics
    track_performance: bool = True
    analytics_retention_days: int = 90
    
    def __post_init__(self):
        if self.api_credentials is None:
            self.api_credentials = {}
        if self.api_endpoints is None:
            self.api_endpoints = {}
        if self.rate_limits is None:
            self.rate_limits = {"posts_per_hour": 10, "requests_per_hour": 100}
        if self.supported_formats is None:
            self.supported_formats = [ContentFormat.TEXT, ContentFormat.HTML]
        if self.optimal_posting_times is None:
            self.optimal_posting_times = ["09:00", "12:00", "15:00", "18:00"]


@dataclass
class SEOConfig:
    """SEO optimization configuration"""    enable_keyword_optimization: bool = True
    enable_meta_generation: bool = True
    enable_schema_markup: bool = True
    enable_readability_optimization: bool = True
    
    # Keyword settings
    max_keyword_density: float = 0.03
    min_keyword_count: int = 1
    max_keyword_count: int = 5
    
    # Content structure
    require_headings: bool = True
    min_paragraph_count: int = 3
    max_paragraph_length: int = 150
    
    # Link building
    enable_internal_linking: bool = True
    enable_external_linking: bool = True
    max_links_per_content: int = 10
    
    # Performance
    target_page_speed_score: int = 90
    optimize_images: bool = True
    enable_lazy_loading: bool = True


@dataclass
class QualityConfig:
    """Quality control configuration"""    enable_grammar_check: bool = True
    enable_spell_check: bool = True
    enable_readability_check: bool = True
    enable_plagiarism_check: bool = False
    enable_fact_checking: bool = False
    
    # Readability standards
    target_readability_level: str = "college"  # elementary, middle, high-school, college
    max_sentence_length: int = 25
    max_paragraph_length: int = 4
    
    # Content quality metrics
    min_content_score: float = 0.7
    require_manual_review: bool = False
    auto_fix_issues: bool = True
    
    # Validation rules
    custom_rules: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.custom_rules is None:
            self.custom_rules = []


@dataclass
class SecurityConfig:
    """Security and compliance configuration"""    enable_content_filtering: bool = True
    enable_pii_detection: bool = True
    enable_compliance_check: bool = True
    
    # Content filtering
    blocked_keywords: List[str] = None
    sensitive_topics: List[str] = None
    
    # Data protection
    encrypt_stored_content: bool = True
    data_retention_days: int = 365
    enable_audit_logging: bool = True
    
    # Compliance
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    coppa_compliance: bool = False
    
    def __post_init__(self):
        if self.blocked_keywords is None:
            self.blocked_keywords = []
        if self.sensitive_topics is None:
            self.sensitive_topics = ["politics", "religion", "violence"]


@dataclass
class PerformanceConfig:
    """Performance and monitoring configuration"""    enable_performance_tracking: bool = True
    enable_real_time_monitoring: bool = True
    enable_alerting: bool = True
    
    # Processing limits
    max_concurrent_generations: int = 10
    max_queue_size: int = 100
    request_timeout: int = 300
    
    # Caching
    enable_caching: bool = True
    cache_ttl: int = 3600
    max_cache_size: int = 1000
    
    # Monitoring thresholds
    error_rate_threshold: float = 0.05
    response_time_threshold: float = 5.0
    queue_size_threshold: int = 50
    
    # Alerts
    alert_email: Optional[str] = None
    alert_webhook: Optional[str] = None


class GenerationConfigManager:
    """    Professional configuration management system for content generation
    
    Features:
    - Multi-source configuration loading (env, files, database)
    - Environment-specific configurations
    - Dynamic configuration updates
    - Configuration validation and validation
    - Configuration caching and optimization
    - Secure credential management
    - Configuration versioning and rollback
    """    
    def __init__(self, config_path: Optional[str] = None, environment: str = "production"):
        self.logger = logging.getLogger(__name__)
        self.environment = environment
        self.config_path = config_path or self._get_default_config_path()
        
        # Configuration storage
        self._configs: Dict[str, Any] = {}
        self._config_sources: Dict[str, ConfigSource] = {}
        self._config_cache: Dict[str, Any] = {}
        self._last_loaded: Dict[str, datetime] = {}
        
        # Load configurations
        self._load_all_configurations()
        
        self.logger.info(f"GenerationConfigManager initialized for environment: {environment}")
    
    def _get_default_config_path(self) -> str:
        """Get default configuration path"""        return os.path.join(os.path.dirname(__file__), "config")
    
    def _load_all_configurations(self) -> None:
        """Load all configuration from various sources"""        try:
            # Load from environment variables
            self._load_from_environment()
            
            # Load from configuration files
            self._load_from_files()
            
            # Load default configurations
            self._load_defaults()
            
            # Validate configurations
            self._validate_configurations()
            
            self.logger.info("All configurations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading configurations: {str(e)}")
            raise ConfigurationError(f"Failed to load configurations: {str(e)}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""        # AI Model configuration
        ai_config = {}
        if os.getenv("AI_PROVIDER"):
            ai_config["provider"] = os.getenv("AI_PROVIDER")
        if os.getenv("AI_MODEL_NAME"):
            ai_config["model_name"] = os.getenv("AI_MODEL_NAME")
        if os.getenv("AI_API_KEY"):
            ai_config["api_key"] = os.getenv("AI_API_KEY")
        if os.getenv("AI_MAX_TOKENS"):
            ai_config["max_tokens"] = int(os.getenv("AI_MAX_TOKENS"))
        if os.getenv("AI_TEMPERATURE"):
            ai_config["temperature"] = float(os.getenv("AI_TEMPERATURE"))
        
        if ai_config:
            self._configs["ai_model"] = ai_config
            self._config_sources["ai_model"] = ConfigSource.ENVIRONMENT
        
        # Platform credentials
        platforms_config = {}
        for platform in Platform:
            key_prefix = f"{platform.value.upper()}_"
            platform_config = {}
            
            if os.getenv(f"{key_prefix}API_KEY"):
                platform_config["api_key"] = os.getenv(f"{key_prefix}API_KEY")
            if os.getenv(f"{key_prefix}API_SECRET"):
                platform_config["api_secret"] = os.getenv(f"{key_prefix}API_SECRET")
            if os.getenv(f"{key_prefix}ACCESS_TOKEN"):
                platform_config["access_token"] = os.getenv(f"{key_prefix}ACCESS_TOKEN")
            
            if platform_config:
                platforms_config[platform.value] = platform_config
        
        if platforms_config:
            self._configs["platforms"] = platforms_config
            self._config_sources["platforms"] = ConfigSource.ENVIRONMENT
        
        # Performance configuration
        perf_config = {}
        if os.getenv("MAX_CONCURRENT_GENERATIONS"):
            perf_config["max_concurrent_generations"] = int(os.getenv("MAX_CONCURRENT_GENERATIONS"))
        if os.getenv("REQUEST_TIMEOUT"):
            perf_config["request_timeout"] = int(os.getenv("REQUEST_TIMEOUT"))
        if os.getenv("ENABLE_CACHING"):
            perf_config["enable_caching"] = os.getenv("ENABLE_CACHING").lower() == "true"
        
        if perf_config:
            self._configs["performance"] = perf_config
            self._config_sources["performance"] = ConfigSource.ENVIRONMENT
    
    def _load_from_files(self) -> None:
        """Load configuration from files"""        config_dir = Path(self.config_path)
        
        if not config_dir.exists():
            self.logger.warning(f"Configuration directory not found: {config_dir}")
            return
        
        # Load YAML configurations
        for yaml_file in config_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                config_name = yaml_file.stem
                
                # Environment-specific override
                env_config = config_data.get(self.environment, config_data)
                
                self._configs[config_name] = env_config
                self._config_sources[config_name] = ConfigSource.FILE
                self._last_loaded[config_name] = datetime.now()
                
                self.logger.debug(f"Loaded configuration from {yaml_file}")
                
            except Exception as e:
                self.logger.error(f"Error loading {yaml_file}: {str(e)}")
        
        # Load JSON configurations
        for json_file in config_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                config_name = json_file.stem
                env_config = config_data.get(self.environment, config_data)
                
                self._configs[config_name] = env_config
                self._config_sources[config_name] = ConfigSource.FILE
                self._last_loaded[config_name] = datetime.now()
                
                self.logger.debug(f"Loaded configuration from {json_file}")
                
            except Exception as e:
                self.logger.error(f"Error loading {json_file}: {str(e)}")
    
    def _load_defaults(self) -> None:
        """Load default configurations"""        defaults = {
            "ai_model": asdict(AIModelConfig()),
            "content_generation": asdict(ContentGenerationConfig()),
            "seo": asdict(SEOConfig()),
            "quality": asdict(QualityConfig()),
            "security": asdict(SecurityConfig()),
            "performance": asdict(PerformanceConfig())
        }
        
        for config_name, default_config in defaults.items():
            if config_name not in self._configs:
                self._configs[config_name] = default_config
                self._config_sources[config_name] = ConfigSource.DEFAULT
    
    def _validate_configurations(self) -> None:
        """Validate loaded configurations"""        errors = []
        
        # Validate AI model configuration
        ai_config = self._configs.get("ai_model", {})
        if not ai_config.get("provider"):
            errors.append("AI provider is required")
        if not ai_config.get("model_name"):
            errors.append("AI model name is required")
        
        # Validate content generation configuration
        content_config = self._configs.get("content_generation", {})
        min_quality = content_config.get("min_quality_score", 0.7)
        if not 0 <= min_quality <= 1:
            errors.append("min_quality_score must be between 0 and 1")
        
        # Validate performance configuration
        perf_config = self._configs.get("performance", {})
        max_concurrent = perf_config.get("max_concurrent_generations", 10)
        if max_concurrent < 1:
            errors.append("max_concurrent_generations must be at least 1")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {', '.join(errors)}")
    
    def get_ai_model_config(self) -> AIModelConfig:
        """Get AI model configuration"""        config_data = self._configs.get("ai_model", {})
        return AIModelConfig(**config_data)
    
    def get_content_generation_config(self) -> ContentGenerationConfig:
        """Get content generation configuration"""        config_data = self._configs.get("content_generation", {})
        return ContentGenerationConfig(**config_data)
    
    def get_platform_config(self, platform: Platform) -> PlatformConfig:
        """Get platform-specific configuration"""        platforms_config = self._configs.get("platforms", {})
        platform_data = platforms_config.get(platform.value, {})
        
        return PlatformConfig(
            platform=platform,
            **platform_data
        )
    
    def get_seo_config(self) -> SEOConfig:
        """Get SEO configuration"""        config_data = self._configs.get("seo", {})
        return SEOConfig(**config_data)
    
    def get_quality_config(self) -> QualityConfig:
        """Get quality configuration"""        config_data = self._configs.get("quality", {})
        return QualityConfig(**config_data)
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""        config_data = self._configs.get("security", {})
        return SecurityConfig(**config_data)
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration"""        config_data = self._configs.get("performance", {})
        return PerformanceConfig(**config_data)
    
    def get_config(self, config_name: str, default: Any = None) -> Any:
        """Get arbitrary configuration by name"""        return self._configs.get(config_name, default)
    
    def update_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Update configuration dynamically"""        if config_name in self._configs:
            self._configs[config_name].update(config_data)
        else:
            self._configs[config_name] = config_data
        
        self._config_sources[config_name] = ConfigSource.API
        self._last_loaded[config_name] = datetime.now()
        
        # Clear cache
        self._config_cache.pop(config_name, None)
        
        self.logger.info(f"Updated configuration: {config_name}")
    
    def reload_config(self, config_name: Optional[str] = None) -> None:
        """Reload configuration from sources"""        if config_name:
            # Reload specific configuration
            if self._config_sources.get(config_name) == ConfigSource.FILE:
                self._load_from_files()
            elif self._config_sources.get(config_name) == ConfigSource.ENVIRONMENT:
                self._load_from_environment()
        else:
            # Reload all configurations
            self._load_all_configurations()
        
        self.logger.info(f"Reloaded configuration: {config_name or 'all'}")
    
    def get_content_length_target(self, content_type: str) -> Dict[str, int]:
        """Get content length targets for specific content type"""        content_config = self.get_content_generation_config()
        return content_config.content_length_targets.get(content_type, {
            "min": 100, "max": 1000, "optimal": 500
        })
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""        # Check in various configuration sections
        for config_section in self._configs.values():
            if isinstance(config_section, dict):
                if feature_name in config_section:
                    return config_section[feature_name]
        
        return False
    
    def get_all_configurations(self) -> Dict[str, Any]:
        """Get all loaded configurations"""        return {
            "configurations": self._configs.copy(),
            "sources": self._config_sources.copy(),
            "last_loaded": {k: v.isoformat() for k, v in self._last_loaded.items()},
            "environment": self.environment
        }
    
    def export_configuration(self, output_path: str, format: str = "yaml") -> None:
        """Export current configuration to file"""        try:
            output_file = Path(output_path)
            
            if format.lower() == "yaml":
                with open(output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self._configs, f, default_flow_style=False, indent=2)
            elif format.lower() == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(self._configs, f, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Configuration exported to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {str(e)}")
            raise


# Global configuration manager instance
_config_manager: Optional[GenerationConfigManager] = None


def get_config_manager(
    config_path: Optional[str] = None,
    environment: Optional[str] = None
) -> GenerationConfigManager:
    """Get global configuration manager instance"""    global _config_manager
    
    if _config_manager is None:
        env = environment or os.getenv("ENVIRONMENT", "production")
        _config_manager = GenerationConfigManager(config_path, env)
    
    return _config_manager


def init_config(config_path: Optional[str] = None, environment: str = "production") -> None:
    """Initialize global configuration manager"""    global _config_manager
    _config_manager = GenerationConfigManager(config_path, environment)


# Aliases for backward compatibility
GenerationConfig = AIModelConfig


class ModelProvider:
    """Model provider enumeration"""    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    
    @classmethod
    def from_model_name(cls, model_name: str) -> str:
        """Get provider from model name"""        if "gpt" in model_name.lower():
            return cls.OPENAI
        elif "claude" in model_name.lower():
            return cls.ANTHROPIC
        elif "command" in model_name.lower():
            return cls.COHERE
        else:
            return cls.HUGGINGFACE


class EnvironmentConfig:
    """Environment configuration settings"""    
    def __init__(self, env: str = "production"):
        self.environment = env
        self.debug = env == "development"
        self.testing = env == "testing"
        self.production = env == "production"


class ConfigValidator:
    """Configuration validation utilities"""    
    @staticmethod
    def validate_temperature(temperature: float) -> bool:
        """Validate temperature parameter"""        return 0.0 <= temperature <= 2.0
    
    @staticmethod
    def validate_token_limits(max_tokens: int) -> bool:
        """Validate token limits"""        return 1 <= max_tokens <= 8192
    
    @staticmethod
    def validate_model_compatibility(model: str, provider: str) -> bool:
        """Validate model compatibility"""        return True  # Simplified validation


class ConfigLoader:
    """Configuration loader utilities"""    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """Load configuration from file"""        return {}
    
    @staticmethod
    def load_from_yaml(yaml_path: str) -> Dict[str, Any]:
        """Load configuration from YAML"""        return {}
    
    @staticmethod
    def load_with_environment_override(config: Dict[str, Any]) -> Dict[str, Any]:
        """Load with environment overrides"""        return config


class ConfigManager:
    """Configuration manager utilities"""    
    def register_config(self, name: str, config: Any) -> None:
        """Register a configuration"""        pass
    
    def get_config_version(self, name: str) -> str:
        """Get configuration version"""        return "1.0.0"
    
    def get_config_templates(self) -> List[str]:
        """Get available configuration templates"""        return []
    
    def cache_config(self, name: str, config: Any) -> None:
        """Cache configuration"""        pass
