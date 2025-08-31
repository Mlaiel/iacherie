"""Image Agent Configuration - Production-Grade Configuration Management

Centralized configuration management for the Image Agent module with environment-specific
settings, security configurations, and performance optimizations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum


class EnvironmentType(Enum):
    """Environment types for configuration"""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelTier(Enum):
    """Model performance tiers"""    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ULTRA = "ultra"


@dataclass
class ProcessingConfig:
    """Image processing configuration"""    max_resolution: int = 8192
    max_file_size_mb: int = 100
    concurrent_operations: int = 10
    gpu_acceleration: bool = True
    cache_size_gb: float = 1.0
    quality_preset: str = "professional"
    preserve_metadata: bool = True
    auto_optimization: bool = True
    batch_processing: bool = True
    processing_timeout: int = 300  # seconds


@dataclass
class SecurityConfig:
    """Security and protection configuration"""    enable_content_filtering: bool = True
    enable_watermarking: bool = True
    enable_fingerprinting: bool = True
    enable_tamper_detection: bool = True
    encryption_enabled: bool = True
    audit_logging: bool = True
    rate_limiting: bool = True
    max_requests_per_minute: int = 100
    security_scan_level: str = "strict"


@dataclass
class AIModelConfig:
    """AI model configuration"""    generation_model: str = "stable_diffusion_v2_1"
    enhancement_model: str = "real_esrgan"
    analysis_model: str = "clip_vit_large"
    style_transfer_model: str = "neural_style_transfer"
    model_cache_dir: str = "/models/image_agent"
    model_tier: ModelTier = ModelTier.PROFESSIONAL
    enable_model_caching: bool = True
    auto_model_updates: bool = False


@dataclass
class StorageConfig:
    """Storage and file management configuration"""    upload_directory: str = "/uploads/images"
    processed_directory: str = "/processed/images"
    cache_directory: str = "/cache/images"
    backup_directory: str = "/backups/images"
    temp_directory: str = "/tmp/images"
    max_storage_gb: float = 100.0
    auto_cleanup_days: int = 30
    backup_retention_days: int = 90


@dataclass
class AnalyticsConfig:
    """Analytics and monitoring configuration"""    enable_performance_tracking: bool = True
    enable_business_analytics: bool = True
    enable_seo_optimization: bool = True
    metrics_retention_days: int = 365
    real_time_monitoring: bool = True
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "processing_time_ms": 10000,
        "error_rate_percent": 5.0,
        "memory_usage_percent": 85.0,
        "disk_usage_percent": 90.0
    })


@dataclass
class IntegrationConfig:
    """External integration configuration"""    cloud_storage_enabled: bool = True
    cloud_storage_provider: str = "aws_s3"
    cdn_enabled: bool = True
    cdn_provider: str = "cloudflare"
    api_keys: Dict[str, str] = field(default_factory=dict)
    webhook_endpoints: List[str] = field(default_factory=list)
    external_apis: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class ImageAgentConfig:
    """Main Image Agent Configuration Manager"""    
    def __init__(self, environment: EnvironmentType = EnvironmentType.PRODUCTION):
        self.environment = environment
        self._config: Dict[str, Any] = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration based on environment"""        # Base configuration
        self._config = self._get_base_config()
        
        # Environment-specific overrides
        env_config = self._get_environment_config()
        self._config.update(env_config)
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from config file if exists
        self._load_from_file()
    
    def _get_base_config(self) -> Dict[str, Any]:
        """Get base configuration settings"""        return {
            "processing": ProcessingConfig(),
            "security": SecurityConfig(),
            "ai_models": AIModelConfig(),
            "storage": StorageConfig(),
            "analytics": AnalyticsConfig(),
            "integration": IntegrationConfig(),
            "version": "2.0.0",
            "debug": False,
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "/logs/image_agent.log",
                "max_size_mb": 100,
                "backup_count": 5
            }
        }
    
    def _get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""        configs = {
            EnvironmentType.DEVELOPMENT: {
                "debug": True,
                "processing": ProcessingConfig(
                    max_resolution=4096,
                    concurrent_operations=5,
                    gpu_acceleration=False
                ),
                "security": SecurityConfig(
                    rate_limiting=False,
                    max_requests_per_minute=1000
                ),
                "logging": {"level": "DEBUG"}
            },
            EnvironmentType.TESTING: {
                "debug": True,
                "processing": ProcessingConfig(
                    max_resolution=2048,
                    concurrent_operations=3,
                    cache_size_gb=0.5
                ),
                "security": SecurityConfig(
                    enable_content_filtering=False,
                    audit_logging=False
                ),
                "logging": {"level": "DEBUG"}
            },
            EnvironmentType.STAGING: {
                "debug": False,
                "processing": ProcessingConfig(
                    max_resolution=6144,
                    concurrent_operations=8
                ),
                "logging": {"level": "INFO"}
            },
            EnvironmentType.PRODUCTION: {
                "debug": False,
                "processing": ProcessingConfig(
                    max_resolution=8192,
                    concurrent_operations=15,
                    gpu_acceleration=True
                ),
                "security": SecurityConfig(
                    security_scan_level="strict",
                    rate_limiting=True
                ),
                "logging": {"level": "WARNING"}
            }
        }
        
        return configs.get(self.environment, {})
    
    def _load_from_env(self):
        """Load configuration from environment variables"""        env_mappings = {
            "IMAGE_AGENT_MAX_RESOLUTION": ("processing.max_resolution", int),
            "IMAGE_AGENT_GPU_ENABLED": ("processing.gpu_acceleration", bool),
            "IMAGE_AGENT_CACHE_SIZE_GB": ("processing.cache_size_gb", float),
            "IMAGE_AGENT_DEBUG": ("debug", bool),
            "IMAGE_AGENT_LOG_LEVEL": ("logging.level", str),
            "IMAGE_AGENT_MODEL_DIR": ("ai_models.model_cache_dir", str),
            "IMAGE_AGENT_UPLOAD_DIR": ("storage.upload_directory", str),
            "IMAGE_AGENT_MAX_STORAGE_GB": ("storage.max_storage_gb", float),
            "IMAGE_AGENT_RATE_LIMIT": ("security.max_requests_per_minute", int),
        }
        
        for env_var, (config_path, data_type) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Convert value to appropriate type
                    if data_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif data_type in (int, float):
                        value = data_type(value)
                    
                    # Set nested configuration value
                    self._set_nested_config(config_path, value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid value for {env_var}: {value} ({e})")
    
    def _load_from_file(self):
        """Load configuration from JSON file"""        config_files = [
            f"/config/image_agent_{self.environment.value}.json",
            "/config/image_agent.json",
            "config/image_agent.json",
            "image_agent_config.json"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        file_config = json.load(f)
                        self._merge_config(file_config)
                    print(f"Loaded configuration from: {config_file}")
                    break
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not load config from {config_file}: {e}")
    
    def _set_nested_config(self, path: str, value: Any):
        """Set nested configuration value using dot notation"""        keys = path.split('.')
        config_section = self._config
        
        for key in keys[:-1]:
            if key not in config_section:
                config_section[key] = {}
            config_section = config_section[key]
        
        config_section[keys[-1]] = value
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Recursively merge new configuration"""        def merge_dict(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self._config, new_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value with dot notation support"""        self._set_nested_config(key, value)
    
    def get_processing_config(self) -> ProcessingConfig:
        """Get processing configuration"""        return self._config.get("processing", ProcessingConfig())
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""        return self._config.get("security", SecurityConfig())
    
    def get_ai_model_config(self) -> AIModelConfig:
        """Get AI model configuration"""        return self._config.get("ai_models", AIModelConfig())
    
    def get_storage_config(self) -> StorageConfig:
        """Get storage configuration"""        return self._config.get("storage", StorageConfig())
    
    def get_analytics_config(self) -> AnalyticsConfig:
        """Get analytics configuration"""        return self._config.get("analytics", AnalyticsConfig())
    
    def get_integration_config(self) -> IntegrationConfig:
        """Get integration configuration"""        return self._config.get("integration", IntegrationConfig())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""        return self._config.copy()
    
    def save_to_file(self, filename: str):
        """Save current configuration to file"""        try:
            with open(filename, 'w') as f:
                json.dump(self._config, f, indent=2, default=str)
            print(f"Configuration saved to: {filename}")
        except IOError as e:
            print(f"Error saving configuration: {e}")


# Global configuration instance
_global_config: Optional[ImageAgentConfig] = None


def get_config(environment: Optional[EnvironmentType] = None) -> ImageAgentConfig:
    """Get global configuration instance"""    global _global_config
    
    if _global_config is None or (environment and _global_config.environment != environment):
        env = environment or EnvironmentType(os.getenv("IMAGE_AGENT_ENV", "production"))
        _global_config = ImageAgentConfig(env)
    
    return _global_config


def reload_config(environment: Optional[EnvironmentType] = None):
    """Reload configuration from sources"""    global _global_config
    _global_config = None
    return get_config(environment)


# Pre-defined configuration presets
PRESET_CONFIGURATIONS = {
    "high_performance": {
        "processing": {
            "max_resolution": 8192,
            "concurrent_operations": 20,
            "gpu_acceleration": True,
            "cache_size_gb": 2.0
        },
        "ai_models": {
            "model_tier": "ultra"
        }
    },
    "memory_optimized": {
        "processing": {
            "max_resolution": 4096,
            "concurrent_operations": 8,
            "cache_size_gb": 0.5
        }
    },
    "security_focused": {
        "security": {
            "security_scan_level": "paranoid",
            "enable_content_filtering": True,
            "enable_tamper_detection": True,
            "rate_limiting": True,
            "max_requests_per_minute": 50
        }
    },
    "cost_optimized": {
        "processing": {
            "gpu_acceleration": False,
            "concurrent_operations": 5,
            "cache_size_gb": 0.25
        },
        "ai_models": {
            "model_tier": "basic"
        }
    }
}


def apply_preset(preset_name: str, config: Optional[ImageAgentConfig] = None) -> ImageAgentConfig:
    """Apply a configuration preset"""    if preset_name not in PRESET_CONFIGURATIONS:
        raise ValueError(f"Unknown preset: {preset_name}")
    
    if config is None:
        config = get_config()
    
    preset = PRESET_CONFIGURATIONS[preset_name]
    config._merge_config(preset)
    
    return config
