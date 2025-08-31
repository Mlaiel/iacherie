"""AI Engines Configuration Module

Enterprise-grade configuration management for all AI content processing engines.
Provides centralized configuration, environment management, and performance tuning.

🚀 Enterprise Team Project Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written consent from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will face legal action under international copyright law.

⚖️ LEGAL NOTICE: THEFT OF IDEAS, CONCEPTS, OR CODE WITHOUT EXPLICIT WRITTEN AUTHORIZATION  
FROM FAHED MLAIEL (mlaiel@live.de) IS STRICTLY FORBIDDEN AND WILL RESULT  
IN IMMEDIATE LEGAL PROSECUTION UNDER INTERNATIONAL COPYRIGHT LAW.

🔒 NO UNAUTHORIZED USE, COPYING, MODIFICATION, OR DISTRIBUTION ALLOWED.

Business Logic: User Upload → AI Processing → Protection → SEO → Collaboration → Distribution
"""
import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import logging
from datetime import datetime


class EnvironmentType(Enum):
    """Deployment environment types"""    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class PerformanceProfile(Enum):
    """Performance optimization profiles"""    ECONOMY = "economy"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    ULTRA_PERFORMANCE = "ultra_performance"


@dataclass
class DatabaseConfig:
    """Database configuration for engines"""    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"
    connection_timeout: int = 30
    
    
@dataclass
class RedisConfig:
    """Redis configuration for caching and queues"""    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    health_check_interval: int = 30
    retry_on_timeout: bool = True
    

@dataclass
class AIModelConfig:
    """AI model configuration settings"""    model_name: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    

@dataclass
class SecurityConfig:
    """Security configuration for engines"""    encryption_key: Optional[str] = None
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_time: int = 3600
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    max_upload_size_mb: int = 100
    allowed_file_types: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".mp3", ".wav", ".txt", ".pdf"
    ])
    enable_content_scanning: bool = True
    enable_virus_scanning: bool = True
    

@dataclass
class PerformanceConfig:
    """Performance tuning configuration"""    max_concurrent_workers: int = 10
    processing_timeout: int = 300
    memory_limit_mb: int = 2048
    cpu_limit_cores: int = 4
    enable_gpu_acceleration: bool = False
    gpu_memory_limit_mb: int = 4096
    enable_distributed_processing: bool = False
    queue_max_size: int = 1000
    batch_processing_size: int = 10
    

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: str = "/var/log/ia-influencer/engines.log"
    log_rotation_size_mb: int = 100
    log_retention_days: int = 30
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_health_checks: bool = True
    health_check_interval: int = 30
    

@dataclass
class ContentProtectionConfig:
    """Content protection and copyright configuration"""    enable_fingerprinting: bool = True
    fingerprint_sensitivity: float = 0.85
    enable_watermarking: bool = True
    watermark_strength: float = 0.3
    enable_drm: bool = False
    copyright_detection_threshold: float = 0.9
    enable_real_time_monitoring: bool = True
    monitoring_platforms: List[str] = field(default_factory=lambda: [
        "youtube", "tiktok", "instagram", "facebook", "twitter", "spotify"
    ])
    

@dataclass
class MonetizationConfig:
    """Monetization and revenue configuration"""    enable_revenue_tracking: bool = True
    default_commission_rate: float = 0.15
    minimum_payout_threshold: float = 50.0
    supported_payment_methods: List[str] = field(default_factory=lambda: [
        "paypal", "stripe", "bank_transfer", "crypto"
    ])
    enable_affiliate_program: bool = True
    affiliate_commission_rate: float = 0.10
    enable_licensing: bool = True
    default_license_type: str = "standard"
    

@dataclass
class CollaborationConfig:
    """Collaboration and networking configuration"""    enable_collaboration_matching: bool = True
    matching_algorithm: str = "ml_based"
    similarity_threshold: float = 0.75
    max_collaboration_suggestions: int = 10
    enable_cross_platform_matching: bool = True
    supported_platforms: List[str] = field(default_factory=lambda: [
        "spotify", "youtube", "tiktok", "instagram", "soundcloud", "bandcamp"
    ])
    enable_automatic_outreach: bool = False
    

@dataclass
class EngineSpecificConfig:
    """Engine-specific configuration settings"""    audio_engines: Dict[str, Any] = field(default_factory=lambda: {
        "audio_processing": {
            "sample_rate": 44100,
            "bit_depth": 16,
            "channels": 2,
            "enable_noise_reduction": True,
            "enable_audio_enhancement": True,
            "supported_formats": ["mp3", "wav", "flac", "aac"]
        },
        "music_generation": {
            "model_type": "transformer",
            "sequence_length": 1024,
            "enable_style_transfer": True,
            "enable_melody_generation": True,
            "enable_harmony_generation": True
        },
        "voice_synthesis": {
            "voice_model": "neural_tts",
            "enable_emotion": True,
            "enable_multilingual": True,
            "supported_languages": ["en", "de", "fr", "es", "it"]
        }
    })
    
    video_engines: Dict[str, Any] = field(default_factory=lambda: {
        "video_processing": {
            "resolution": "1080p",
            "frame_rate": 30,
            "codec": "h264",
            "enable_stabilization": True,
            "enable_color_correction": True,
            "supported_formats": ["mp4", "mov", "avi", "mkv"]
        },
        "visual_effects": {
            "enable_motion_tracking": True,
            "enable_green_screen": True,
            "enable_3d_effects": True,
            "render_quality": "high"
        }
    })
    
    image_engines: Dict[str, Any] = field(default_factory=lambda: {
        "image_processing": {
            "max_resolution": "4K",
            "supported_formats": ["jpg", "png", "webp", "tiff"],
            "enable_auto_enhancement": True,
            "enable_object_detection": True,
            "enable_style_transfer": True
        },
        "nft_generation": {
            "blockchain": "ethereum",
            "enable_metadata_generation": True,
            "enable_rarity_scoring": True,
            "image_quality": "ultra_high"
        }
    })
    
    text_engines: Dict[str, Any] = field(default_factory=lambda: {
        "text_generation": {
            "max_length": 4096,
            "enable_seo_optimization": True,
            "enable_plagiarism_check": True,
            "supported_languages": ["en", "de", "fr", "es", "it"],
            "writing_styles": ["professional", "casual", "creative", "technical"]
        },
        "seo_optimization": {
            "enable_keyword_analysis": True,
            "enable_competitor_analysis": True,
            "enable_content_scoring": True,
            "target_readability_score": 60
        }
    })


@dataclass
class EnginesConfig:
    """Complete configuration for AI engines module"""    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    performance_profile: PerformanceProfile = PerformanceProfile.BALANCED
    
    # Core configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    ai_models: AIModelConfig = field(default_factory=AIModelConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Business configurations
    content_protection: ContentProtectionConfig = field(default_factory=ContentProtectionConfig)
    monetization: MonetizationConfig = field(default_factory=MonetizationConfig)
    collaboration: CollaborationConfig = field(default_factory=CollaborationConfig)
    
    # Engine-specific configurations
    engines: EngineSpecificConfig = field(default_factory=EngineSpecificConfig)
    
    # Feature flags
    enable_experimental_features: bool = False
    enable_beta_engines: bool = False
    enable_debug_mode: bool = False
    

class ConfigManager:
    """    Advanced configuration manager for AI engines.
    
    Handles loading, validation, and hot-reloading of configuration
    from multiple sources including environment variables, files, and databases.
    """    
    def __init__(
        self,
        config_file: Optional[str] = None,
        environment: Optional[str] = None
    ):
        self.config_file = config_file or self._get_default_config_file()
        self.environment = EnvironmentType(environment or os.getenv("ENVIRONMENT", "development"))
        self.logger = logging.getLogger(__name__)
        
        # Configuration cache
        self._config_cache: Optional[EnginesConfig] = None
        self._last_modified: Optional[datetime] = None
        
        # Configuration validators
        self._validators: Dict[str, callable] = {}
        self._register_validators()
        
    def _get_default_config_file(self) -> str:
        """Get default configuration file path"""        config_dir = Path(__file__).parent / "config"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "engines_config.yaml")
        
    def _register_validators(self):
        """Register configuration validators"""        self._validators = {
            "database": self._validate_database_config,
            "redis": self._validate_redis_config,
            "security": self._validate_security_config,
            "performance": self._validate_performance_config
        }
        
    def load_config(self, force_reload: bool = False) -> EnginesConfig:
        """        Load configuration from all sources.
        
        Args:
            force_reload: Force reload even if cached
            
        Returns:
            Complete engines configuration
        """        if not force_reload and self._config_cache and not self._config_needs_reload():
            return self._config_cache
            
        # Start with default configuration
        config = EnginesConfig()
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                file_config = self._load_config_file()
                config = self._merge_configs(config, file_config)
            except Exception as e:
                self.logger.error(f"Failed to load config file: {str(e)}")
                
        # Override with environment variables
        config = self._apply_environment_overrides(config)
        
        # Apply environment-specific settings
        config = self._apply_environment_settings(config)
        
        # Validate configuration
        self._validate_config(config)
        
        # Cache the configuration
        self._config_cache = config
        self._last_modified = datetime.now()
        
        self.logger.info(f"Configuration loaded for {self.environment.value} environment")
        return config
        
    def _config_needs_reload(self) -> bool:
        """Check if configuration needs to be reloaded"""        if not os.path.exists(self.config_file):
            return False
            
        file_modified = datetime.fromtimestamp(os.path.getmtime(self.config_file))
        return self._last_modified is None or file_modified > self._last_modified
        
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from file"""        with open(self.config_file, 'r', encoding='utf-8') as f:
            if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                return yaml.safe_load(f)
            elif self.config_file.endswith('.json'):
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {self.config_file}")
                
    def _merge_configs(self, base_config: EnginesConfig, file_config: Dict[str, Any]) -> EnginesConfig:
        """Merge file configuration with base configuration"""        config_dict = asdict(base_config)
        
        def deep_merge(base: Dict, override: Dict) -> Dict:
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
            
        merged_dict = deep_merge(config_dict, file_config)
        
        # Convert back to dataclass (simplified conversion)
        try:
            return EnginesConfig(**merged_dict)
        except Exception as e:
            self.logger.warning(f"Could not convert merged config to dataclass: {str(e)}")
            return base_config
            
    def _apply_environment_overrides(self, config: EnginesConfig) -> EnginesConfig:
        """Apply environment variable overrides"""        env_overrides = {
            "DATABASE_HOST": ("database", "host"),
            "DATABASE_PORT": ("database", "port"),
            "DATABASE_NAME": ("database", "database"),
            "DATABASE_USER": ("database", "username"),
            "DATABASE_PASSWORD": ("database", "password"),
            "REDIS_HOST": ("redis", "host"),
            "REDIS_PORT": ("redis", "port"),
            "REDIS_PASSWORD": ("redis", "password"),
            "AI_MODEL_API_KEY": ("ai_models", "api_key"),
            "AI_MODEL_NAME": ("ai_models", "model_name"),
            "JWT_SECRET_KEY": ("security", "jwt_secret_key"),
            "ENCRYPTION_KEY": ("security", "encryption_key"),
            "LOG_LEVEL": ("monitoring", "log_level")
        }
        
        for env_var, (section, key) in env_overrides.items():
            value = os.getenv(env_var)
            if value:
                section_obj = getattr(config, section)
                if hasattr(section_obj, key):
                    # Type conversion
                    current_value = getattr(section_obj, key)
                    if isinstance(current_value, int):
                        value = int(value)
                    elif isinstance(current_value, float):
                        value = float(value)
                    elif isinstance(current_value, bool):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                        
                    setattr(section_obj, key, value)
                    
        return config
        
    def _apply_environment_settings(self, config: EnginesConfig) -> EnginesConfig:
        """Apply environment-specific settings"""        if self.environment == EnvironmentType.PRODUCTION:
            # Production optimizations
            config.performance.max_concurrent_workers = 20
            config.security.rate_limit_per_minute = 30
            config.monitoring.log_level = "WARNING"
            config.enable_debug_mode = False
            config.enable_experimental_features = False
            
        elif self.environment == EnvironmentType.DEVELOPMENT:
            # Development settings
            config.performance.max_concurrent_workers = 5
            config.security.rate_limit_per_minute = 100
            config.monitoring.log_level = "DEBUG"
            config.enable_debug_mode = True
            config.enable_experimental_features = True
            
        elif self.environment == EnvironmentType.TESTING:
            # Testing configurations
            config.database.database = "ia_influencer_test"
            config.redis.database = 1
            config.monitoring.log_level = "ERROR"
            config.enable_debug_mode = False
            
        return config
        
    def _validate_config(self, config: EnginesConfig):
        """Validate complete configuration"""        for section_name, validator in self._validators.items():
            if hasattr(config, section_name):
                section_config = getattr(config, section_name)
                try:
                    validator(section_config)
                except Exception as e:
                    self.logger.error(f"Configuration validation failed for {section_name}: {str(e)}")
                    raise
                    
    def _validate_database_config(self, config: DatabaseConfig):
        """Validate database configuration"""        if not config.host:
            raise ValueError("Database host is required")
        if not config.database:
            raise ValueError("Database name is required")
        if config.port < 1 or config.port > 65535:
            raise ValueError("Database port must be between 1 and 65535")
            
    def _validate_redis_config(self, config: RedisConfig):
        """Validate Redis configuration"""        if not config.host:
            raise ValueError("Redis host is required")
        if config.port < 1 or config.port > 65535:
            raise ValueError("Redis port must be between 1 and 65535")
            
    def _validate_security_config(self, config: SecurityConfig):
        """Validate security configuration"""        if not config.jwt_secret_key:
            raise ValueError("JWT secret key is required")
        if len(config.jwt_secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters")
            
    def _validate_performance_config(self, config: PerformanceConfig):
        """Validate performance configuration"""        if config.max_concurrent_workers < 1:
            raise ValueError("Max concurrent workers must be at least 1")
        if config.processing_timeout < 1:
            raise ValueError("Processing timeout must be at least 1 second")
            
    def save_config(self, config: EnginesConfig, file_path: Optional[str] = None):
        """        Save configuration to file.
        
        Args:
            config: Configuration to save
            file_path: Optional custom file path
        """        save_path = file_path or self.config_file
        config_dict = asdict(config)
        
        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w', encoding='utf-8') as f:
            if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif save_path.endswith('.json'):
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {save_path}")
                
        self.logger.info(f"Configuration saved to {save_path}")
        
    def get_engine_config(self, engine_name: str) -> Dict[str, Any]:
        """        Get configuration for specific engine.
        
        Args:
            engine_name: Name of the engine
            
        Returns:
            Engine-specific configuration
        """        config = self.load_config()
        
        # Determine engine category
        audio_engines = ["audio_processing", "music_generation", "voice_synthesis"]
        video_engines = ["video_processing", "visual_effects"]
        image_engines = ["image_processing", "nft_generation"]
        text_engines = ["text_generation", "seo_optimization"]
        
        if engine_name in audio_engines:
            return config.engines.audio_engines.get(engine_name, {})
        elif engine_name in video_engines:
            return config.engines.video_engines.get(engine_name, {})
        elif engine_name in image_engines:
            return config.engines.image_engines.get(engine_name, {})
        elif engine_name in text_engines:
            return config.engines.text_engines.get(engine_name, {})
        else:
            return {}
            
    def update_engine_config(self, engine_name: str, engine_config: Dict[str, Any]):
        """        Update configuration for specific engine.
        
        Args:
            engine_name: Name of the engine
            engine_config: New configuration for the engine
        """        config = self.load_config()
        
        # Update appropriate engine category
        audio_engines = ["audio_processing", "music_generation", "voice_synthesis"]
        video_engines = ["video_processing", "visual_effects"]
        image_engines = ["image_processing", "nft_generation"]
        text_engines = ["text_generation", "seo_optimization"]
        
        if engine_name in audio_engines:
            config.engines.audio_engines[engine_name] = engine_config
        elif engine_name in video_engines:
            config.engines.video_engines[engine_name] = engine_config
        elif engine_name in image_engines:
            config.engines.image_engines[engine_name] = engine_config
        elif engine_name in text_engines:
            config.engines.text_engines[engine_name] = engine_config
            
        # Save updated configuration
        self.save_config(config)
        
        # Clear cache to force reload
        self._config_cache = None


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> EnginesConfig:
    """Get current engines configuration"""    return config_manager.load_config()


def get_engine_config(engine_name: str) -> Dict[str, Any]:
    """Get configuration for specific engine"""    return config_manager.get_engine_config(engine_name)


def reload_config() -> EnginesConfig:
    """Force reload configuration"""    return config_manager.load_config(force_reload=True)


# Export configuration classes and functions
__all__ = [
    "EnginesConfig",
    "DatabaseConfig",
    "RedisConfig",
    "AIModelConfig",
    "SecurityConfig",
    "PerformanceConfig",
    "MonitoringConfig",
    "ContentProtectionConfig",
    "MonetizationConfig",
    "CollaborationConfig",
    "EngineSpecificConfig",
    "EnvironmentType",
    "PerformanceProfile",
    "ConfigManager",
    "config_manager",
    "get_config",
    "get_engine_config",
    "reload_config"
]
