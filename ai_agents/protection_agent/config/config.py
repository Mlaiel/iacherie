"""
Configuration Management for Advanced Protection Agent
Professional configuration handling for all protection services

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited

This module provides comprehensive configuration management for:
- Protection levels and policies
- Service-specific configurations
- Performance tuning parameters
- Security and compliance settings
- Enterprise deployment options

Project Team Specialties:
- Lead IA Developer: Advanced AI algorithms and machine learning
- Backend Senior Engineer: Scalable microservices architecture
- ML Engineer: Content analysis and pattern recognition
- Database Administrator: High-performance data management
- Security Engineer: Cryptography and digital signatures
- Microservices Architect: Distributed systems design
- Audio Engineer: Audio fingerprinting and processing
- DevOps Engineer: Cloud deployment and monitoring
- IA Prompt Engineer: Natural language processing

COPYRIGHT NOTICE:
All code, concepts, and intellectual property in this module are the exclusive
property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, copying,
modification, distribution, or reverse engineering of this code or its concepts
is strictly prohibited and will result in legal action.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import os
import json


class DeploymentEnvironment(Enum):
    """Deployment environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ENTERPRISE = "enterprise"


class PerformanceProfile(Enum):
    """Performance optimization profiles"""
    BALANCED = "balanced"
    SPEED_OPTIMIZED = "speed_optimized"
    ACCURACY_OPTIMIZED = "accuracy_optimized"
    RESOURCE_CONSERVATIVE = "resource_conservative"


@dataclass
class ContentAnalysisConfig:
    """Configuration for content analysis services"""
    enable_audio_fingerprinting: bool = True
    enable_video_analysis: bool = True
    enable_image_analysis: bool = True
    enable_text_analysis: bool = True
    
    # Performance settings
    max_file_size_mb: int = 500
    analysis_timeout_seconds: int = 300
    parallel_processing: bool = True
    max_concurrent_analyses: int = 10
    
    # AI Model settings
    model_precision: str = "high"  # low, medium, high, ultra
    confidence_threshold: float = 0.85
    enable_deep_learning: bool = True
    
    # Feature extraction
    audio_features: List[str] = field(default_factory=lambda: [
        "spectral_centroid", "mfcc", "chroma", "spectral_rolloff"
    ])
    video_features: List[str] = field(default_factory=lambda: [
        "histogram", "edge_detection", "motion_vectors"
    ])
    image_features: List[str] = field(default_factory=lambda: [
        "sift", "surf", "orb", "histogram"
    ])


@dataclass
class CopyrightConfig:
    """Configuration for copyright management"""
    auto_registration: bool = True
    enable_dmca_automation: bool = True
    dmca_response_time_hours: int = 24
    
    # Monitoring settings
    platform_monitoring: List[str] = field(default_factory=lambda: [
        "youtube", "vimeo", "dailymotion", "facebook", "instagram", "tiktok"
    ])
    monitoring_frequency_hours: int = 6
    deep_scan_enabled: bool = True
    
    # Legal settings
    auto_takedown_threshold: float = 0.95
    evidence_collection: bool = True
    legal_notification: bool = True
    
    # Geographic settings
    jurisdictions: List[str] = field(default_factory=lambda: [
        "US", "EU", "CA", "AU", "UK", "JP"
    ])


@dataclass
class RightsManagementConfig:
    """Configuration for rights management"""
    enable_licensing: bool = True
    auto_monetization: bool = True
    revenue_sharing: bool = True
    
    # Licensing options
    default_license_type: str = "exclusive"  # exclusive, non_exclusive, creative_commons
    geographic_restrictions: bool = True
    time_based_licensing: bool = True
    usage_tracking: bool = True
    
    # Monetization
    dynamic_pricing: bool = True
    price_optimization: bool = True
    revenue_analytics: bool = True
    
    # Compliance
    tax_reporting: bool = True
    royalty_distribution: bool = True


@dataclass
class WatermarkingConfig:
    """Configuration for watermarking services"""
    enable_visible_watermarking: bool = False
    enable_invisible_watermarking: bool = True
    enable_digital_signatures: bool = True
    
    # Watermark strength
    robustness_level: str = "high"  # low, medium, high, maximum
    invisibility_level: str = "high"  # low, medium, high, maximum
    
    # Digital signature settings
    signature_algorithm: str = "rsa_2048"
    hash_algorithm: str = "sha256"
    key_rotation_days: int = 90
    
    # Attack resistance
    jpeg_compression_resistance: bool = True
    scaling_resistance: bool = True
    rotation_resistance: bool = True
    noise_resistance: bool = True


@dataclass
class MonitoringConfig:
    """Configuration for monitoring and alerting"""
    real_time_monitoring: bool = True
    alert_notifications: bool = True
    performance_tracking: bool = True
    
    # Alert settings
    alert_email: Optional[str] = None
    alert_webhook: Optional[str] = None
    alert_slack: Optional[str] = None
    
    # Thresholds
    violation_alert_threshold: int = 1
    performance_degradation_threshold: float = 0.8
    
    # Metrics collection
    detailed_metrics: bool = True
    metrics_retention_days: int = 90


@dataclass
class SecurityConfig:
    """Configuration for security settings"""
    encryption_enabled: bool = True
    encryption_algorithm: str = "aes_256"
    
    # Authentication
    api_key_required: bool = True
    rate_limiting: bool = True
    requests_per_minute: int = 1000
    
    # Data protection
    data_anonymization: bool = True
    gdpr_compliance: bool = True
    data_retention_days: int = 365
    
    # Audit logging
    audit_logging: bool = True
    log_retention_days: int = 90
    sensitive_data_masking: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization"""
    profile: PerformanceProfile = PerformanceProfile.BALANCED
    
    # Resource limits
    max_memory_mb: int = 4096
    max_cpu_cores: int = 8
    max_concurrent_requests: int = 100
    
    # Caching
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    cache_size_mb: int = 1024
    
    # Database
    connection_pool_size: int = 20
    query_timeout_seconds: int = 30
    
    # Network
    request_timeout_seconds: int = 60
    retry_attempts: int = 3


@dataclass
class AdvancedProtectionConfig:
    """Complete configuration for Advanced Protection Agent"""
    
    # Environment
    environment: DeploymentEnvironment = DeploymentEnvironment.PRODUCTION
    debug_mode: bool = False
    verbose_logging: bool = True
    
    # Core service configurations
    content_analysis: ContentAnalysisConfig = field(default_factory=ContentAnalysisConfig)
    copyright: CopyrightConfig = field(default_factory=CopyrightConfig)
    rights_management: RightsManagementConfig = field(default_factory=RightsManagementConfig)
    watermarking: WatermarkingConfig = field(default_factory=WatermarkingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Enterprise features
    enterprise_features: bool = False
    multi_tenant: bool = False
    white_label: bool = False
    custom_branding: bool = False
    
    # Integration settings
    external_apis: Dict[str, str] = field(default_factory=dict)
    webhook_endpoints: List[str] = field(default_factory=list)
    
    @classmethod
    def from_environment(cls) -> 'AdvancedProtectionConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Environment detection
        env_name = os.getenv('PROTECTION_ENVIRONMENT', 'production').lower()
        if env_name in [e.value for e in DeploymentEnvironment]:
            config.environment = DeploymentEnvironment(env_name)
        
        # Debug settings
        config.debug_mode = os.getenv('PROTECTION_DEBUG', 'false').lower() == 'true'
        config.verbose_logging = os.getenv('PROTECTION_VERBOSE', 'true').lower() == 'true'
        
        # Enterprise features
        config.enterprise_features = os.getenv('PROTECTION_ENTERPRISE', 'false').lower() == 'true'
        
        return config
    
    @classmethod
    def from_file(cls, config_file: str) -> 'AdvancedProtectionConfig':
        """Load configuration from JSON file"""



        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # Convert dict to dataclass (simplified)
            config = cls()
            
            for key, value in data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            return config
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_file}: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        result = {}
        
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):
                # Nested dataclass
                result[key] = value.__dict__.copy()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        
        return result
    
    def save_to_file(self, config_file: str):
        """Save configuration to JSON file"""



        try:
            with open(config_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {config_file}: {str(e)}")
    
    def validate(self) -> List[str]:
        """Validate configuration settings"""
        errors = []
        
        # Validate content analysis
        if self.content_analysis.max_file_size_mb <= 0:
            errors.append("Content analysis max file size must be positive")
        
        if not (0.0 <= self.content_analysis.confidence_threshold <= 1.0):
            errors.append("Content analysis confidence threshold must be between 0 and 1")
        
        # Validate copyright
        if self.copyright.monitoring_frequency_hours <= 0:
            errors.append("Copyright monitoring frequency must be positive")
        
        # Validate performance
        if self.performance.max_memory_mb <= 0:
            errors.append("Performance max memory must be positive")
        
        if self.performance.max_cpu_cores <= 0:
            errors.append("Performance max CPU cores must be positive")
        
        # Validate security
        if self.security.requests_per_minute <= 0:
            errors.append("Security requests per minute must be positive")
        
        return errors
    
    def optimize_for_environment(self):
        """Optimize configuration based on environment"""
        if self.environment == DeploymentEnvironment.DEVELOPMENT:
            self.debug_mode = True
            self.verbose_logging = True
            self.security.rate_limiting = False
            self.performance.max_concurrent_requests = 10
            
        elif self.environment == DeploymentEnvironment.PRODUCTION:
            self.debug_mode = False
            self.verbose_logging = False
            self.security.rate_limiting = True
            self.monitoring.real_time_monitoring = True
            
        elif self.environment == DeploymentEnvironment.ENTERPRISE:
            self.enterprise_features = True
            self.multi_tenant = True
            self.security.audit_logging = True
            self.performance.max_concurrent_requests = 1000


# Predefined configurations
DEVELOPMENT_CONFIG = AdvancedProtectionConfig(
    environment=DeploymentEnvironment.DEVELOPMENT,
    debug_mode=True,
    verbose_logging=True
)

PRODUCTION_CONFIG = AdvancedProtectionConfig(
    environment=DeploymentEnvironment.PRODUCTION,
    debug_mode=False,
    verbose_logging=False
)

ENTERPRISE_CONFIG = AdvancedProtectionConfig(
    environment=DeploymentEnvironment.ENTERPRISE,
    debug_mode=False,
    verbose_logging=True,
    enterprise_features=True,
    multi_tenant=True
)

# Optimize predefined configurations
DEVELOPMENT_CONFIG.optimize_for_environment()
PRODUCTION_CONFIG.optimize_for_environment()
ENTERPRISE_CONFIG.optimize_for_environment()


def get_default_config(environment: str = "production") -> AdvancedProtectionConfig:
    """Get default configuration for specified environment"""
    env_map = {
        "development": DEVELOPMENT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "enterprise": ENTERPRISE_CONFIG
    }
    
    return env_map.get(environment.lower(), PRODUCTION_CONFIG)


def create_custom_config(**kwargs) -> AdvancedProtectionConfig:
    """Create custom configuration with overrides"""
    config = AdvancedProtectionConfig()
    
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config
