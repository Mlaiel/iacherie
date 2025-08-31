"""
AI Core Configuration Module

Centralized configuration management for the IA-Influencer-Agent AI system.
Enterprise-grade configuration with environment-specific settings, security policies,
and performance optimization parameters.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 UNAUTHORIZED USE STRICTLY PROHIBITED 
This configuration system contains sensitive business logic and security parameters.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class SecurityLevel(Enum):
    """Security configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


@dataclass
class AIEngineConfig:
    """Configuration for AI Engine Manager"""
    max_concurrent_models: int = 5
    auto_cleanup_interval: int = 300
    memory_threshold_gb: float = 8.0
    default_device: str = "auto"
    model_cache_size: int = 1000
    inference_timeout: int = 30
    batch_size: int = 32
    enable_gpu: bool = True
    enable_model_versioning: bool = True
    model_repository_path: str = "./models"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "max_concurrent_models": self.max_concurrent_models,
            "auto_cleanup_interval": self.auto_cleanup_interval,
            "memory_threshold_gb": self.memory_threshold_gb,
            "default_device": self.default_device,
            "model_cache_size": self.model_cache_size,
            "inference_timeout": self.inference_timeout,
            "batch_size": self.batch_size,
            "enable_gpu": self.enable_gpu,
            "enable_model_versioning": self.enable_model_versioning,
            "model_repository_path": self.model_repository_path
        }


@dataclass
class ValidationConfig:
    """Configuration for Content Validator"""
    enable_security_validation: bool = True
    enable_quality_analysis: bool = True
    enable_seo_validation: bool = True
    enable_audio_validation: bool = True
    enable_image_validation: bool = True
    min_quality_score: float = 70.0
    min_safety_score: float = 80.0
    min_compliance_score: float = 85.0
    max_content_size_mb: float = 100.0
    supported_formats: List[str] = field(default_factory=lambda: [
        ".mp3", ".wav", ".flac", ".jpg", ".jpeg", ".png", ".mp4", ".avi"
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "enable_security_validation": self.enable_security_validation,
            "enable_quality_analysis": self.enable_quality_analysis,
            "enable_seo_validation": self.enable_seo_validation,
            "enable_audio_validation": self.enable_audio_validation,
            "enable_image_validation": self.enable_image_validation,
            "min_quality_score": self.min_quality_score,
            "min_safety_score": self.min_safety_score,
            "min_compliance_score": self.min_compliance_score,
            "max_content_size_mb": self.max_content_size_mb,
            "supported_formats": self.supported_formats
        }


@dataclass
class PerformanceConfig:
    """Configuration for Performance Monitor"""
    monitoring_interval: int = 30
    history_size: int = 1000
    enable_auto_optimization: bool = True
    enable_predictions: bool = True
    cpu_warning_threshold: float = 70.0
    cpu_critical_threshold: float = 85.0
    memory_warning_threshold: float = 80.0
    memory_critical_threshold: float = 90.0
    disk_warning_threshold: float = 85.0
    disk_critical_threshold: float = 95.0
    response_time_warning: float = 2.0
    response_time_critical: float = 5.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "monitoring_interval": self.monitoring_interval,
            "history_size": self.history_size,
            "enable_auto_optimization": self.enable_auto_optimization,
            "enable_predictions": self.enable_predictions,
            "cpu_warning_threshold": self.cpu_warning_threshold,
            "cpu_critical_threshold": self.cpu_critical_threshold,
            "memory_warning_threshold": self.memory_warning_threshold,
            "memory_critical_threshold": self.memory_critical_threshold,
            "disk_warning_threshold": self.disk_warning_threshold,
            "disk_critical_threshold": self.disk_critical_threshold,
            "response_time_warning": self.response_time_warning,
            "response_time_critical": self.response_time_critical
        }


@dataclass
class MetricsConfig:
    """Configuration for Metrics Collector"""
    max_entries: int = 10000
    auto_flush_interval: int = 300
    enable_system_metrics: bool = True
    enable_business_metrics: bool = True
    metric_retention_days: int = 30
    export_format: str = "json"
    enable_prometheus_export: bool = False
    prometheus_port: int = 9090
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "max_entries": self.max_entries,
            "auto_flush_interval": self.auto_flush_interval,
            "enable_system_metrics": self.enable_system_metrics,
            "enable_business_metrics": self.enable_business_metrics,
            "metric_retention_days": self.metric_retention_days,
            "export_format": self.export_format,
            "enable_prometheus_export": self.enable_prometheus_export,
            "prometheus_port": self.prometheus_port
        }


@dataclass
class PipelineConfig:
    """Configuration for Content Processing Pipeline"""
    max_concurrent_pipelines: int = 10
    stage_timeout_seconds: int = 300
    enable_stage_caching: bool = True
    enable_parallel_processing: bool = True
    retry_failed_stages: bool = True
    max_retries: int = 3
    enable_stage_skipping: bool = False
    required_stages: List[str] = field(default_factory=lambda: [
        "validation", "ai_analysis", "protection"
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""



        return {
            "max_concurrent_pipelines": self.max_concurrent_pipelines,
            "stage_timeout_seconds": self.stage_timeout_seconds,
            "enable_stage_caching": self.enable_stage_caching,
            "enable_parallel_processing": self.enable_parallel_processing,
            "retry_failed_stages": self.retry_failed_stages,
            "max_retries": self.max_retries,
            "enable_stage_skipping": self.enable_stage_skipping,
            "required_stages": self.required_stages
        }


@dataclass
class CoreConfig:
    """Master configuration for AI Core module"""
    environment: str = "development"
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_detailed_logging: bool = True
    
    # Component configurations
    ai_engine: AIEngineConfig = field(default_factory=AIEngineConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    
    # Security settings
    enable_encryption: bool = True
    api_rate_limit: int = 1000
    max_request_size_mb: float = 50.0
    
    # Business logic settings
    enable_monetization: bool = True
    enable_collaboration: bool = True
    enable_seo_optimization: bool = True
    enable_content_protection: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert complete configuration to dictionary"""



        return {
            "environment": self.environment,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level,
            "enable_detailed_logging": self.enable_detailed_logging,
            "ai_engine": self.ai_engine.to_dict(),
            "validation": self.validation.to_dict(),
            "performance": self.performance.to_dict(),
            "metrics": self.metrics.to_dict(),
            "pipeline": self.pipeline.to_dict(),
            "enable_encryption": self.enable_encryption,
            "api_rate_limit": self.api_rate_limit,
            "max_request_size_mb": self.max_request_size_mb,
            "enable_monetization": self.enable_monetization,
            "enable_collaboration": self.enable_collaboration,
            "enable_seo_optimization": self.enable_seo_optimization,
            "enable_content_protection": self.enable_content_protection
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CoreConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update basic settings
        for key in ["environment", "debug_mode", "log_level", "enable_detailed_logging"]:
            if key in data:
                setattr(config, key, data[key])
                
        # Update component configurations
        if "ai_engine" in data:
            for key, value in data["ai_engine"].items():
                if hasattr(config.ai_engine, key):
                    setattr(config.ai_engine, key, value)
                    
        if "validation" in data:
            for key, value in data["validation"].items():
                if hasattr(config.validation, key):
                    setattr(config.validation, key, value)
                    
        if "performance" in data:
            for key, value in data["performance"].items():
                if hasattr(config.performance, key):
                    setattr(config.performance, key, value)
                    
        if "metrics" in data:
            for key, value in data["metrics"].items():
                if hasattr(config.metrics, key):
                    setattr(config.metrics, key, value)
                    
        if "pipeline" in data:
            for key, value in data["pipeline"].items():
                if hasattr(config.pipeline, key):
                    setattr(config.pipeline, key, value)
                    
        # Update other settings
        for key in ["enable_encryption", "api_rate_limit", "max_request_size_mb",
                   "enable_monetization", "enable_collaboration", "enable_seo_optimization",
                   "enable_content_protection"]:
            if key in data:
                setattr(config, key, data[key])
                
        return config


class ConfigManager:
    """
    Configuration manager for AI Core module
    
    Features:
    - Environment-based configuration
    - Configuration validation
    - Hot reload capability
    - Default fallbacks
    - Configuration export/import
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config: Optional[CoreConfig] = None
        self._watchers: List[Callable] = []
        
    def load_config(self, config_path: Optional[str] = None) -> CoreConfig:
        """Load configuration from file or environment"""
        config_path = config_path or self.config_path
        
        # Start with default configuration
        config = CoreConfig()
        
        # Load from environment variables
        self._load_from_environment(config)
        
        # Load from file if specified
        if config_path and Path(config_path).exists():
            self._load_from_file(config, config_path)
            
        # Validate configuration
        self._validate_config(config)
        
        self._config = config
        
        # Notify watchers
        for watcher in self._watchers:
            try:
                watcher(config)
            except Exception as e:
                logger.error(f"Error in config watcher: {e}")
                
        logger.info(f"Configuration loaded successfully (environment: {config.environment})")
        return config
        
    def _load_from_environment(self, config: CoreConfig):
        """Load configuration from environment variables"""
        # Basic settings
        config.environment = os.getenv("AI_ENVIRONMENT", config.environment)
        config.debug_mode = os.getenv("AI_DEBUG", str(config.debug_mode)).lower() == "true"
        config.log_level = os.getenv("AI_LOG_LEVEL", config.log_level)
        
        # AI Engine settings
        if os.getenv("AI_MAX_MODELS"):
            config.ai_engine.max_concurrent_models = int(os.getenv("AI_MAX_MODELS"))
        if os.getenv("AI_MEMORY_THRESHOLD"):
            config.ai_engine.memory_threshold_gb = float(os.getenv("AI_MEMORY_THRESHOLD"))
        if os.getenv("AI_MODEL_PATH"):
            config.ai_engine.model_repository_path = os.getenv("AI_MODEL_PATH")
            
        # Performance settings
        if os.getenv("AI_MONITORING_INTERVAL"):
            config.performance.monitoring_interval = int(os.getenv("AI_MONITORING_INTERVAL"))
        if os.getenv("AI_CPU_WARNING"):
            config.performance.cpu_warning_threshold = float(os.getenv("AI_CPU_WARNING"))
        if os.getenv("AI_MEMORY_WARNING"):
            config.performance.memory_warning_threshold = float(os.getenv("AI_MEMORY_WARNING"))
            
        # Validation settings
        if os.getenv("AI_MIN_QUALITY_SCORE"):
            config.validation.min_quality_score = float(os.getenv("AI_MIN_QUALITY_SCORE"))
        if os.getenv("AI_MAX_CONTENT_SIZE"):
            config.validation.max_content_size_mb = float(os.getenv("AI_MAX_CONTENT_SIZE"))
            
        # Business settings
        config.enable_monetization = os.getenv("AI_ENABLE_MONETIZATION", "true").lower() == "true"
        config.enable_collaboration = os.getenv("AI_ENABLE_COLLABORATION", "true").lower() == "true"
        config.enable_content_protection = os.getenv("AI_ENABLE_PROTECTION", "true").lower() == "true"
        
    def _load_from_file(self, config: CoreConfig, config_path: str):
        """Load configuration from JSON file"""



        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                
            # Merge with existing config
            merged_config = CoreConfig.from_dict(data)
            
            # Update config object
            for attr_name in dir(merged_config):
                if not attr_name.startswith('_') and hasattr(config, attr_name):
                    setattr(config, attr_name, getattr(merged_config, attr_name))
                    
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            
    def _validate_config(self, config: CoreConfig):
        """Validate configuration values"""
        errors = []
        
        # Validate AI Engine config
        if config.ai_engine.max_concurrent_models < 1:
            errors.append("max_concurrent_models must be at least 1")
        if config.ai_engine.memory_threshold_gb < 1.0:
            errors.append("memory_threshold_gb must be at least 1.0")
            
        # Validate Performance config
        if config.performance.monitoring_interval < 10:
            errors.append("monitoring_interval must be at least 10 seconds")
        if config.performance.cpu_warning_threshold >= config.performance.cpu_critical_threshold:
            errors.append("cpu_warning_threshold must be less than cpu_critical_threshold")
            
        # Validate Validation config
        if config.validation.min_quality_score < 0 or config.validation.min_quality_score > 100:
            errors.append("min_quality_score must be between 0 and 100")
            
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
            
    def get_config(self) -> CoreConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load_config()
        return self._config
        
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save current configuration to file"""
        if self._config is None:
            logger.error("No configuration loaded to save")
            return False
            
        config_path = config_path or self.config_path
        if not config_path:
            logger.error("No config path specified for saving")
            return False
            
        try:
            config_data = self._config.to_dict()
            
            # Ensure directory exists
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            return False
            
    def add_config_watcher(self, callback: Callable[[CoreConfig], None]):
        """Add callback to be called when configuration changes"""
        self._watchers.append(callback)
        
    def reload_config(self) -> CoreConfig:
        """Reload configuration from source"""



        return self.load_config()
        
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        if self._config is None:
            self.load_config()
            
        try:
            # Apply updates
            current_dict = self._config.to_dict()
            current_dict.update(updates)
            
            # Create new config and validate
            new_config = CoreConfig.from_dict(current_dict)
            self._validate_config(new_config)
            
            # Update current config
            self._config = new_config
            
            # Notify watchers
            for watcher in self._watchers:
                try:
                    watcher(self._config)
                except Exception as e:
                    logger.error(f"Error in config watcher: {e}")
                    
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False


# Global configuration manager
config_manager = ConfigManager()

# Convenience functions
def get_config() -> CoreConfig:
    """Get current AI core configuration"""



    return config_manager.get_config()

def load_config(config_path: Optional[str] = None) -> CoreConfig:
    """Load AI core configuration"""



    return config_manager.load_config(config_path)

def save_config(config_path: Optional[str] = None) -> bool:
    """Save current AI core configuration"""



    return config_manager.save_config(config_path)

def update_config(updates: Dict[str, Any]) -> bool:
    """Update AI core configuration"""



    return config_manager.update_config(updates)

def add_config_watcher(callback: Callable[[CoreConfig], None]):
    """Add configuration change watcher"""
    config_manager.add_config_watcher(callback)
