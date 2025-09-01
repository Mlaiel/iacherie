"""Content Guidance Configuration - Production-Ready Settings
==========================================================

Advanced configuration management for the content guidance system with
environment-specific settings, service parameters, and performance tuning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path

from backend.core.config import get_settings


class ServiceTier(Enum):
    """Service tier levels for different quality/performance requirements."""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ULTRA = "ultra"


class ProcessingMode(Enum):
    """Processing modes for different performance characteristics."""
    FAST = "fast"              # Quick processing, lower accuracy
    BALANCED = "balanced"      # Balanced speed and accuracy
    ACCURATE = "accurate"      # High accuracy, slower processing
    COMPREHENSIVE = "comprehensive"  # Maximum analysis depth


@dataclass
class ServiceConfiguration:
    """Configuration for individual content guidance services."""
    
    enabled: bool = True
    service_tier: ServiceTier = ServiceTier.PROFESSIONAL
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    timeout_seconds: float = 30.0
    max_retries: int = 3
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    rate_limit_per_minute: int = 100
    quality_threshold: float = 0.7
    confidence_threshold: float = 0.6
    
    # Service-specific parameters
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentGuidanceConfig:
    """Main configuration for the content guidance system."""
    
    # Global settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug_mode: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # System performance
    max_concurrent_requests: int = 50
    default_timeout: float = 60.0
    memory_limit_mb: int = 2048
    cpu_limit_percent: int = 80
    
    # Cache configuration
    redis_enabled: bool = True
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    cache_prefix: str = "content_guidance"
    
    # Database configuration
    database_enabled: bool = True
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/ia_influencer")
    connection_pool_size: int = 20
    connection_timeout: float = 30.0
    
    # AI/ML Model configuration
    model_base_path: str = "/models/content_guidance"
    model_cache_size: int = 5
    gpu_enabled: bool = bool(os.getenv("GPU_ENABLED", "false").lower() == "true")
    model_precision: str = "float16"  # float32, float16, int8
    
    # Content processing limits
    max_content_length: int = 50000  # characters
    max_media_size_mb: int = 100
    supported_content_types: List[str] = field(default_factory=lambda: [
        "text", "video", "image", "audio", "document", "mixed"
    ])
    supported_platforms: List[str] = field(default_factory=lambda: [
        "youtube", "instagram", "tiktok", "twitter", "facebook", 
        "linkedin", "twitch", "discord", "telegram", "snapchat"
    ])
    
    # Security and compliance
    content_filtering_enabled: bool = True
    pii_detection_enabled: bool = True
    adult_content_filtering: bool = True
    brand_safety_strict_mode: bool = False
    compliance_regions: List[str] = field(default_factory=lambda: ["EU", "US", "CA"])
    
    # Service-specific configurations
    content_optimizer: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    platform_recommendations: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    monetization_guidance: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    trend_analyzer: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    audience_insights: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    brand_safety: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    collaboration_finder: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    content_scheduler: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    creative_assistant: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    performance_tracker: ServiceConfiguration = field(default_factory=ServiceConfiguration)
    
    def __post_init__(self):
        """Post-initialization configuration adjustments."""
        self._apply_environment_overrides()
        self._configure_service_parameters()
        self._validate_configuration()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        
        if self.environment == "production":
            # Production settings
            self.debug_mode = False
            self.log_level = "WARNING"
            self.max_concurrent_requests = 200
            self.memory_limit_mb = 8192
            self.cpu_limit_percent = 90
            self.brand_safety_strict_mode = True
            
            # Enable enterprise tier for all services
            for service_config in self._get_all_service_configs():
                service_config.service_tier = ServiceTier.ENTERPRISE
                service_config.processing_mode = ProcessingMode.COMPREHENSIVE
                service_config.timeout_seconds = 120.0
                service_config.rate_limit_per_minute = 500
        
        elif self.environment == "staging":
            # Staging settings
            self.debug_mode = True
            self.log_level = "INFO"
            self.max_concurrent_requests = 100
            self.memory_limit_mb = 4096
            
            # Professional tier for staging
            for service_config in self._get_all_service_configs():
                service_config.service_tier = ServiceTier.PROFESSIONAL
                service_config.processing_mode = ProcessingMode.BALANCED
        
        elif self.environment == "development":
            # Development settings
            self.debug_mode = True
            self.log_level = "DEBUG"
            self.max_concurrent_requests = 20
            self.memory_limit_mb = 1024
            self.cpu_limit_percent = 60
            
            # Basic tier for development
            for service_config in self._get_all_service_configs():
                service_config.service_tier = ServiceTier.BASIC
                service_config.processing_mode = ProcessingMode.FAST
                service_config.timeout_seconds = 15.0
                service_config.rate_limit_per_minute = 50
    
    def _configure_service_parameters(self):
        """Configure service-specific parameters based on requirements."""
        
        # Content Optimizer specific settings
        self.content_optimizer.custom_parameters.update({
            "seo_analysis_depth": "comprehensive" if self.content_optimizer.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "standard",
            "grammar_checking": True,
            "readability_analysis": True,
            "sentiment_analysis": True,
            "keyword_optimization": True,
            "image_optimization": True,
            "video_optimization": True
        })
        
        # Platform Recommendations specific settings
        self.platform_recommendations.custom_parameters.update({
            "platform_analysis_depth": "deep" if self.platform_recommendations.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "surface",
            "audience_matching_precision": "high",
            "content_format_analysis": True,
            "competitor_analysis": True,
            "growth_prediction": True
        })
        
        # Monetization Guidance specific settings
        self.monetization_guidance.custom_parameters.update({
            "revenue_modeling": "advanced" if self.monetization_guidance.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "basic",
            "brand_partnership_matching": True,
            "product_placement_analysis": True,
            "subscription_optimization": True,
            "ad_revenue_optimization": True,
            "affiliate_marketing_analysis": True
        })
        
        # Trend Analyzer specific settings
        self.trend_analyzer.custom_parameters.update({
            "trend_detection_sensitivity": "high" if self.trend_analyzer.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "medium",
            "viral_prediction": True,
            "hashtag_analysis": True,
            "seasonal_trend_analysis": True,
            "geographic_trend_analysis": True,
            "demographic_trend_analysis": True
        })
        
        # Audience Insights specific settings
        self.audience_insights.custom_parameters.update({
            "demographic_analysis_depth": "comprehensive" if self.audience_insights.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "standard",
            "behavioral_analysis": True,
            "psychographic_analysis": True,
            "engagement_pattern_analysis": True,
            "audience_growth_prediction": True,
            "cross_platform_analysis": True
        })
        
        # Brand Safety specific settings
        self.brand_safety.custom_parameters.update({
            "safety_scanning_depth": "thorough" if self.brand_safety.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "standard",
            "adult_content_detection": True,
            "violence_detection": True,
            "hate_speech_detection": True,
            "copyright_infringement_check": True,
            "trademark_violation_check": True,
            "regulatory_compliance_check": True
        })
        
        # Collaboration Finder specific settings
        self.collaboration_finder.custom_parameters.update({
            "matching_algorithm": "advanced" if self.collaboration_finder.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "basic",
            "compatibility_analysis": True,
            "audience_overlap_analysis": True,
            "brand_alignment_analysis": True,
            "performance_prediction": True,
            "collaboration_type_optimization": True
        })
        
        # Content Scheduler specific settings
        self.content_scheduler.custom_parameters.update({
            "scheduling_optimization": "ai_powered" if self.content_scheduler.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "rule_based",
            "timezone_optimization": True,
            "audience_activity_prediction": True,
            "platform_algorithm_adaptation": True,
            "content_cadence_optimization": True,
            "seasonal_scheduling": True
        })
        
        # Creative Assistant specific settings
        self.creative_assistant.custom_parameters.update({
            "creativity_level": "high" if self.creative_assistant.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "medium",
            "idea_generation_count": 20 if self.creative_assistant.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else 10,
            "content_format_suggestions": True,
            "visual_concept_generation": True,
            "audio_concept_generation": True,
            "script_generation": True,
            "storyboard_creation": True
        })
        
        # Performance Tracker specific settings
        self.performance_tracker.custom_parameters.update({
            "analytics_depth": "comprehensive" if self.performance_tracker.service_tier in [
                ServiceTier.ENTERPRISE, ServiceTier.ULTRA
            ] else "standard",
            "real_time_tracking": True,
            "predictive_analytics": True,
            "competitive_benchmarking": True,
            "roi_analysis": True,
            "attribution_modeling": True,
            "custom_metrics": True
        })
    
    def _get_all_service_configs(self) -> List[ServiceConfiguration]:
        """Get all service configurations for bulk operations."""
        return [
            self.content_optimizer,
            self.platform_recommendations,
            self.monetization_guidance,
            self.trend_analyzer,
            self.audience_insights,
            self.brand_safety,
            self.collaboration_finder,
            self.content_scheduler,
            self.creative_assistant,
            self.performance_tracker
        ]
    
    def _validate_configuration(self):
        """Validate configuration settings for consistency and requirements."""
        
        # Validate timeouts
        if self.default_timeout <= 0:
            raise ValueError("Default timeout must be positive")
        
        # Validate resource limits
        if self.max_concurrent_requests <= 0:
            raise ValueError("Max concurrent requests must be positive")
        
        if self.memory_limit_mb <= 0:
            raise ValueError("Memory limit must be positive")
        
        if not (0 < self.cpu_limit_percent <= 100):
            raise ValueError("CPU limit must be between 0 and 100")
        
        # Validate service configurations
        for service_config in self._get_all_service_configs():
            if service_config.timeout_seconds <= 0:
                raise ValueError("Service timeout must be positive")
            
            if service_config.max_retries < 0:
                raise ValueError("Max retries cannot be negative")
            
            if not (0 <= service_config.quality_threshold <= 1):
                raise ValueError("Quality threshold must be between 0 and 1")
            
            if not (0 <= service_config.confidence_threshold <= 1):
                raise ValueError("Confidence threshold must be between 0 and 1")
        
        # Validate content limits
        if self.max_content_length <= 0:
            raise ValueError("Max content length must be positive")
        
        if self.max_media_size_mb <= 0:
            raise ValueError("Max media size must be positive")
        
        # Validate supported platforms and content types
        if not self.supported_platforms:
            raise ValueError("At least one platform must be supported")
        
        if not self.supported_content_types:
            raise ValueError("At least one content type must be supported")
    
    def get_service_config(self, service_name: str) -> ServiceConfiguration:
        """Get configuration for a specific service."""
        
        service_mapping = {
            "content_optimizer": self.content_optimizer,
            "platform_recommendations": self.platform_recommendations,
            "monetization_guidance": self.monetization_guidance,
            "trend_analyzer": self.trend_analyzer,
            "audience_insights": self.audience_insights,
            "brand_safety": self.brand_safety,
            "collaboration_finder": self.collaboration_finder,
            "content_scheduler": self.content_scheduler,
            "creative_assistant": self.creative_assistant,
            "performance_tracker": self.performance_tracker
        }
        
        if service_name not in service_mapping:
            raise ValueError(f"Unknown service: {service_name}")
        
        return service_mapping[service_name]
    
    def update_service_config(self, service_name: str, **kwargs):
        """Update configuration for a specific service."""
        
        service_config = self.get_service_config(service_name)
        
        for key, value in kwargs.items():
            if hasattr(service_config, key):
                setattr(service_config, key, value)
            else:
                service_config.custom_parameters[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        
        result = {}
        
        # Add main configuration fields
        for field_name in self.__dataclass_fields__:
            field_value = getattr(self, field_name)
            
            if isinstance(field_value, ServiceConfiguration):
                # Convert service configuration to dict
                service_dict = {}
                for service_field in field_value.__dataclass_fields__:
                    service_value = getattr(field_value, service_field)
                    if isinstance(service_value, Enum):
                        service_dict[service_field] = service_value.value
                    else:
                        service_dict[service_field] = service_value
                result[field_name] = service_dict
            elif isinstance(field_value, Enum):
                result[field_name] = field_value.value
            else:
                result[field_name] = field_value
        
        return result
    
    def export_config(self, file_path: Union[str, Path]):
        """Export configuration to file."""
        
        import json
        
        config_dict = self.to_dict()
        
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2, sort_keys=True)
    
    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> 'ContentGuidanceConfig':
        """Load configuration from file."""
        
        import json
        
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        
        # Convert back to proper types
        # This is a simplified implementation - in practice, you'd want more robust deserialization
        return cls(**config_dict)


# Global configuration instance
_config_instance: Optional[ContentGuidanceConfig] = None


def get_content_guidance_config() -> ContentGuidanceConfig:
    """Get the global content guidance configuration instance."""
    
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ContentGuidanceConfig()
    
    return _config_instance


def update_config(**kwargs):
    """Update the global configuration with new values."""
    
    config = get_content_guidance_config()
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration parameter: {key}")


def reset_config():
    """Reset the global configuration to default values."""
    
    global _config_instance
    _config_instance = ContentGuidanceConfig()


# Environment-specific configuration presets
ENVIRONMENT_PRESETS = {
    "development": {
        "debug_mode": True,
        "log_level": "DEBUG",
        "max_concurrent_requests": 10,
        "memory_limit_mb": 512,
        "cpu_limit_percent": 50,
        "cache_enabled": False,
        "brand_safety_strict_mode": False
    },
    
    "testing": {
        "debug_mode": True,
        "log_level": "INFO",
        "max_concurrent_requests": 5,
        "memory_limit_mb": 256,
        "cpu_limit_percent": 30,
        "cache_enabled": False,
        "database_enabled": False,
        "content_filtering_enabled": False
    },
    
    "staging": {
        "debug_mode": True,
        "log_level": "INFO",
        "max_concurrent_requests": 50,
        "memory_limit_mb": 2048,
        "cpu_limit_percent": 70,
        "cache_enabled": True,
        "brand_safety_strict_mode": False
    },
    
    "production": {
        "debug_mode": False,
        "log_level": "WARNING",
        "max_concurrent_requests": 500,
        "memory_limit_mb": 16384,
        "cpu_limit_percent": 95,
        "cache_enabled": True,
        "brand_safety_strict_mode": True,
        "content_filtering_enabled": True,
        "pii_detection_enabled": True,
        "adult_content_filtering": True
    }
}


def apply_environment_preset(environment: str):
    """Apply a predefined environment configuration preset."""
    
    if environment not in ENVIRONMENT_PRESETS:
        raise ValueError(f"Unknown environment preset: {environment}")
    
    preset = ENVIRONMENT_PRESETS[environment]
    update_config(**preset)


# Export main configuration components
__all__ = [
    "ContentGuidanceConfig",
    "ServiceConfiguration", 
    "ServiceTier",
    "ProcessingMode",
    "get_content_guidance_config",
    "update_config",
    "reset_config",
    "apply_environment_preset",
    "ENVIRONMENT_PRESETS"
]
