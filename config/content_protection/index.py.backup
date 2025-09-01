"""Content Protection Configuration Index
=====================================

Central index and factory for content protection configuration management.
Provides unified access to all configuration modules and factory functions
for creating optimized configurations for different environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, Any, Optional, List, Set, Type, Union
import os
from datetime import datetime

# Import all configuration classes
from .fingerprint_engine_config import (
    FingerprintEngineConfig,
    ContentType,
    FingerprintAlgorithm,
    create_production_fingerprint_config,
    create_development_fingerprint_config,
    create_testing_fingerprint_config
)

from .crawler_config import (
    WebCrawlerConfig,
    CrawlerType,
    Platform,
    create_production_crawler_config,
    create_development_crawler_config,
    create_testing_crawler_config
)

from .detection_config import (
    ContentDetectionConfig,
    DetectionMode,
    create_production_detection_config,
    create_development_detection_config,
    create_testing_detection_config
)

from .matching_config import (
    SimilarityMatchingConfig,
    SimilarityMetric,
    create_production_matching_config,
    create_development_matching_config,
    create_testing_matching_config
)

from .watermark_config import (
    WatermarkConfig,
    WatermarkType,
    create_production_watermark_config,
    create_development_watermark_config,
    create_testing_watermark_config
)

from .takedown_config import (
    TakedownConfig,
    TakedownType,
    create_production_takedown_config,
    create_development_takedown_config,
    create_testing_takedown_config
)

from .licensing_config import (
    LicensingConfig,
    LicenseType,
    create_production_licensing_config,
    create_development_licensing_config,
    create_testing_licensing_config
)

from .dmca_config import (
    DMCAConfig,
    DMCANoticeType,
    create_production_dmca_config,
    create_development_dmca_config,
    create_testing_dmca_config
)

from .revenue_tracking_config import (
    RevenueTrackingConfig,
    RevenueTrackingMode,
    create_production_config as create_production_revenue_config,
    create_development_config as create_development_revenue_config,
    create_testing_config as create_testing_revenue_config
)

from .platform_integration_config import (
    PlatformIntegrationConfig,
    IntegrationMethod,
    create_production_platform_config,
    create_development_platform_config,
    create_testing_platform_config
)

from .automated_surveillance_config import (
    AutomatedSurveillanceConfig,
    SurveillanceMode,
    create_high_security_surveillance_config,
    create_real_time_surveillance_config,
    create_enterprise_surveillance_config
)

from .analytics_reporting_config import (
    AnalyticsReportingConfig,
    AnalyticsScope,
    create_enterprise_analytics_config,
    create_basic_analytics_config,
    create_compliance_focused_config
)


class ContentProtectionConfigIndex:
    """
    Central configuration index and factory for content protection system.
    Provides unified access to all configuration modules and environment-specific
    configuration creation.
    """
    
    def __init__(self):
        """Initialize the configuration index."""
        self._config_registry = {}
        self._factory_registry = {}
        self._initialize_registries()
    
    def _initialize_registries(self):
        """Initialize configuration and factory registries."""
        # Configuration class registry
        self._config_registry = {
            'fingerprint_engine': FingerprintEngineConfig,
            'web_crawler': WebCrawlerConfig,
            'content_detection': ContentDetectionConfig,
            'similarity_matching': SimilarityMatchingConfig,
            'watermark': WatermarkConfig,
            'takedown': TakedownConfig,
            'licensing': LicensingConfig,
            'dmca': DMCAConfig,
            'revenue_tracking': RevenueTrackingConfig,
            'platform_integration': PlatformIntegrationConfig,
            'automated_surveillance': AutomatedSurveillanceConfig,
            'analytics_reporting': AnalyticsReportingConfig
        }
        
        # Factory function registry
        self._factory_registry = {
            'fingerprint_engine': {
                'production': create_production_fingerprint_config,
                'development': create_development_fingerprint_config,
                'testing': create_testing_fingerprint_config
            },
            'web_crawler': {
                'production': create_production_crawler_config,
                'development': create_development_crawler_config,
                'testing': create_testing_crawler_config
            },
            'content_detection': {
                'production': create_production_detection_config,
                'development': create_development_detection_config,
                'testing': create_testing_detection_config
            },
            'similarity_matching': {
                'production': create_production_matching_config,
                'development': create_development_matching_config,
                'testing': create_testing_matching_config
            },
            'watermark': {
                'production': create_production_watermark_config,
                'development': create_development_watermark_config,
                'testing': create_testing_watermark_config
            },
            'takedown': {
                'production': create_production_takedown_config,
                'development': create_development_takedown_config,
                'testing': create_testing_takedown_config
            },
            'licensing': {
                'production': create_production_licensing_config,
                'development': create_development_licensing_config,
                'testing': create_testing_licensing_config
            },
            'dmca': {
                'production': create_production_dmca_config,
                'development': create_development_dmca_config,
                'testing': create_testing_dmca_config
            },
            'revenue_tracking': {
                'production': create_production_revenue_config,
                'development': create_development_revenue_config,
                'testing': create_testing_revenue_config
            },
            'platform_integration': {
                'production': create_production_platform_config,
                'development': create_development_platform_config,
                'testing': create_testing_platform_config
            },
            'automated_surveillance': {
                'production': create_enterprise_surveillance_config,
                'development': create_real_time_surveillance_config,
                'testing': create_high_security_surveillance_config
            },
            'analytics_reporting': {
                'production': create_enterprise_analytics_config,
                'development': create_basic_analytics_config,
                'testing': create_compliance_focused_config
            }
        }
    
    def get_config_class(self, config_type: str) -> Optional[Type]:
        """Get configuration class by type name."""
        return self._config_registry.get(config_type)
    
    def create_config(self, config_type: str, environment: str = 'production') -> Any:
        """
        Create configuration instance for specified type and environment.
        
        Args:
            config_type: Type of configuration ('fingerprint_engine', 'web_crawler', etc.)
            environment: Target environment ('production', 'development', 'testing')
        
        Returns:
            Configuration instance or None if not found
        """
        factories = self._factory_registry.get(config_type, {})
        factory = factories.get(environment)
        
        if factory:
            return factory()
        else:
            # Fallback to default constructor
            config_class = self.get_config_class(config_type)
            if config_class:
                return config_class()
        
        return None
    
    def create_complete_config_set(self, environment: str = 'production') -> Dict[str, Any]:
        """
        Create complete set of configurations for specified environment.
        
        Args:
            environment: Target environment
        
        Returns:
            Dictionary of all configuration instances
        """
        configs = {}
        
        for config_type in self._config_registry.keys():
            configs[config_type] = self.create_config(config_type, environment)
        
        return configs
    
    def validate_all_configs(self, configs: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate all configurations in the provided set.
        
        Args:
            configs: Dictionary of configuration instances
        
        Returns:
            Dictionary of validation results
        """
        validation_results = {}
        
        for config_name, config_instance in configs.items():
            if hasattr(config_instance, 'validate_config'):
                validation_results[config_name] = config_instance.validate_config()
            else:
                validation_results[config_name] = True  # Assume valid if no validation method
        
        return validation_results
    
    def get_supported_environments(self) -> List[str]:
        """Get list of supported environments."""
        return ['production', 'development', 'testing']
    
    def get_available_config_types(self) -> List[str]:
        """Get list of available configuration types."""
        return list(self._config_registry.keys())
    
    def export_config_summary(self, configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export summary information for all configurations.
        
        Args:
            configs: Dictionary of configuration instances
        
        Returns:
            Summary dictionary
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_configs': len(configs),
            'config_details': {}
        }
        
        for config_name, config_instance in configs.items():
            config_details = {
                'type': type(config_instance).__name__,
                'module': type(config_instance).__module__
            }
            
            # Add configuration-specific summary if available
            if hasattr(config_instance, 'to_dict'):
                config_details['summary'] = config_instance.to_dict()
            
            summary['config_details'][config_name] = config_details
        
        return summary


# Factory functions for different deployment scenarios

def create_enterprise_production_config() -> Dict[str, Any]:
    """Create enterprise production configuration set."""
    index = ContentProtectionConfigIndex()
    configs = index.create_complete_config_set('production')
    
    # Apply enterprise-specific optimizations
    configs['fingerprint_engine'].enable_distributed_processing = True
    configs['automated_surveillance'].enable_ai_assisted_detection = True
    configs['analytics_reporting'].enable_predictive_modeling = True
    configs['revenue_tracking'].tracking_mode = RevenueTrackingMode.REAL_TIME
    
    return configs


def create_startup_config() -> Dict[str, Any]:
    """Create cost-optimized configuration for startups."""
    index = ContentProtectionConfigIndex()
    configs = index.create_complete_config_set('development')
    
    # Apply cost optimizations
    configs['platform_integration'].enabled_platforms = {'youtube', 'instagram'}
    configs['automated_surveillance'].target_platforms = {'youtube', 'instagram'}
    configs['analytics_reporting'] = create_basic_analytics_config()
    
    return configs


def create_compliance_focused_config() -> Dict[str, Any]:
    """Create compliance-heavy configuration for regulated industries."""
    index = ContentProtectionConfigIndex()
    configs = index.create_complete_config_set('production')
    
    # Apply compliance focus
    configs['automated_surveillance'] = create_high_security_surveillance_config()
    configs['analytics_reporting'] = create_compliance_focused_config()
    configs['revenue_tracking'].compliance_config.enable_gdpr_compliance = True
    configs['revenue_tracking'].compliance_config.enable_ccpa_compliance = True
    configs['revenue_tracking'].compliance_config.enable_sox_compliance = True
    
    return configs


def create_development_environment_config() -> Dict[str, Any]:
    """Create development-friendly configuration."""
    index = ContentProtectionConfigIndex()
    configs = index.create_complete_config_set('development')
    
    # Apply development optimizations
    for config in configs.values():
        if hasattr(config, 'security_config'):
            config.security_config.require_authentication = False
        if hasattr(config, 'performance_config'):
            config.performance_config.max_concurrent_requests = 10
    
    return configs


def create_testing_environment_config() -> Dict[str, Any]:
    """Create testing configuration with minimal resource usage."""
    index = ContentProtectionConfigIndex()
    configs = index.create_complete_config_set('testing')
    
    # Apply testing optimizations
    configs['platform_integration'].enabled_platforms = {'youtube'}
    configs['automated_surveillance'].target_platforms = {'youtube'}
    
    return configs


# Global configuration index instance
config_index = ContentProtectionConfigIndex()

# Export commonly used functions and classes
__all__ = [
    'ContentProtectionConfigIndex',
    'config_index',
    'create_enterprise_production_config',
    'create_startup_config',
    'create_compliance_focused_config',
    'create_development_environment_config',
    'create_testing_environment_config'
]

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
