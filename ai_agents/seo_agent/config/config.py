"""SEO Agent Configuration - Advanced Configuration Management

Comprehensive configuration system for the SEO Agent module with environment-specific
settings, AI model configurations, and optimization parameters.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

class EnvironmentType(Enum):
    """
Environment types for configuration"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class OptimizationMode(Enum):
    """SEO optimization modes"""

    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"
    CUSTOM = "custom"

@dataclass
class AIModelConfig:
    """AI model configuration"""
    model_name: str
    model_path: Optional[str] = None
    cache_size: int = 10000
    batch_size: int = 32
    threshold: float = 0.75
    max_tokens: int = 512
    temperature: float = 0.7
    enabled: bool = True

@dataclass
class CacheConfig:
    """
Caching configuration"""
    enabled: bool = True
    backend: str = "redis"  # redis, memory, database
    ttl: int = 3600  # Time to live in seconds
    max_size: int = 100000
    compression: bool = True
    persistence: bool = True

@dataclass
class APIConfig:
    """External API configuration"""
    enabled: bool = True
    rate_limit: int = 1000  # Requests per hour
    timeout: int = 30  # Timeout in seconds
    retry_count: int = 3
    api_key: Optional[str] = None
    base_url: Optional[str] = None

@dataclass
class PerformanceConfig:
    """
Performance optimization configuration"""
    async_processing: bool = True
    parallel_workers: int = 4
    batch_processing: bool = True
    memory_limit: str = "2GB"
    cpu_limit: float = 2.0
    optimization_timeout: int = 300  # 5 minutes

class SEOAgentConfig:
    """
    Comprehensive SEO Agent Configuration Manager.
    
    Manages all configuration aspects including:
    - Environment-specific settings
    - AI model configurations
    - Performance optimization
    - External API settings
    - Caching strategies
    - Security configurations
    """
    
    def __init__(self, environment: EnvironmentType = EnvironmentType.PRODUCTION):
        self.environment = environment
        
        # Load base configuration
        self._load_base_config()
        
        # Load environment-specific configuration
        self._load_environment_config()
        
        # Initialize component configurations
        self._initialize_component_configs()
    
    def _load_base_config(self):
        """
Load base configuration settings"""
        
        # SEO Agent Core Settings
        self.seo_agent = {
            'agent_id': 'seo_agent',
            'version': '1.0.0',
            'optimization_mode': OptimizationMode.ADVANCED,
            'supported_languages': ['en', 'de', 'fr', 'es', 'it', 'pt'],
            'max_concurrent_campaigns': 5,
            'max_content_per_campaign': 100,
            'default_analysis_depth': 'comprehensive',
            'auto_optimization': True,
            'real_time_monitoring': True
        }
        
        # Keyword Research Settings
        self.keyword_research = {
            'max_keywords_per_request': 1000,
            'min_search_volume': 10,
            'max_related_keywords': 50,
            'difficulty_calculation_method': 'advanced',
            'trend_analysis_window_days': 90,
            'seasonal_analysis_years': 2,
            'competitor_analysis_depth': 'deep',
            'keyword_clustering_enabled': True
        }
        
        # Content Optimization Settings
        self.content_optimization = {
            'title_max_length': 60,
            'description_max_length': 160,
            'keywords_max_count': 10,
            'ideal_paragraph_length': 150,
            'max_sentence_length': 25,
            'heading_keyword_density': 0.8,
            'content_quality_threshold': 0.7,
            'readability_target': 'intermediate',
            'auto_internal_linking': True
        }
        
        # Technical SEO Settings
        self.technical_seo = {
            'page_speed_threshold': 3.0,  # seconds
            'mobile_friendly_required': True,
            'ssl_required': True,
            'schema_markup_auto_generation': True,
            'canonical_url_auto_detection': True,
            'robots_txt_optimization': True,
            'sitemap_auto_update': True,
            'image_alt_text_required': True
        }
        
        # Analytics & Monitoring Settings
        self.analytics = {
            'real_time_tracking': True,
            'performance_alerts': True,
            'ranking_monitoring_frequency': 'daily',
            'traffic_analysis_depth': 'detailed',
            'conversion_tracking': True,
            'custom_event_tracking': True,
            'data_retention_days': 365
        }
        
        # Security Settings
        self.security = {
            'api_rate_limiting': True,
            'authentication_required': True,
            'data_encryption': True,
            'audit_logging': True,
            'ip_whitelisting': False,
            'request_sanitization': True,
            'output_filtering': True
        }
    
    def _load_environment_config(self):
        """
Load environment-specific configuration"""
        
        env_configs = {
            EnvironmentType.DEVELOPMENT: self._get_development_config(),
            EnvironmentType.TESTING: self._get_testing_config(),
            EnvironmentType.STAGING: self._get_staging_config(),
            EnvironmentType.PRODUCTION: self._get_production_config()
        }
        
        env_config = env_configs.get(self.environment, {})
        self._merge_config(env_config)
    
    def _get_development_config(self) -> Dict[str, Any]:
        """
Development environment configuration"""
        return {
            'seo_agent': {
                'optimization_mode': OptimizationMode.STANDARD,
                'max_concurrent_campaigns': 2,
                'real_time_monitoring': False
            },
            'ai_models': {
                'keyword_similarity': AIModelConfig(
                    model_name='sentence-transformers/all-MiniLM-L6-v2',
                    cache_size=1000,
                    batch_size=16
                ),
                'content_optimization': AIModelConfig(
                    model_name='gpt-3.5-turbo',
                    max_tokens=256,
                    temperature=0.5
                )
            },
            'caching': CacheConfig(
                backend='memory',
                ttl=1800,
                max_size=10000,
                persistence=False
            ),
            'performance': PerformanceConfig(
                parallel_workers=2,
                memory_limit='1GB',
                cpu_limit=1.0
            )
        }
    
    def _get_testing_config(self) -> Dict[str, Any]:
        """
Testing environment configuration"""
        return {
            'seo_agent': {
                'optimization_mode': OptimizationMode.BASIC,
                'max_concurrent_campaigns': 1,
                'real_time_monitoring': False,
                'auto_optimization': False
            },
            'keyword_research': {
                'max_keywords_per_request': 100,
                'competitor_analysis_depth': 'basic'
            },
            'ai_models': {
                'keyword_similarity': AIModelConfig(
                    model_name='mock_model',
                    enabled=False
                )
            },
            'caching': CacheConfig(
                enabled=False
            ),
            'analytics': {
                'real_time_tracking': False,
                'performance_alerts': False
            }
        }
    
    def _get_staging_config(self) -> Dict[str, Any]:
        """
Staging environment configuration"""
        return {
            'seo_agent': {
                'optimization_mode': OptimizationMode.ADVANCED,
                'max_concurrent_campaigns': 3
            },
            'ai_models': {
                'keyword_similarity': AIModelConfig(
                    model_name='sentence-transformers/all-MiniLM-L6-v2',
                    cache_size=5000,
                    batch_size=24
                ),
                'content_optimization': AIModelConfig(
                    model_name='gpt-4',
                    max_tokens=512,
                    temperature=0.3
                )
            },
            'caching': CacheConfig(
                backend='redis',
                ttl=7200,
                max_size=50000
            ),
            'performance': PerformanceConfig(
                parallel_workers=3,
                memory_limit='1.5GB',
                cpu_limit=1.5
            )
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """
Production environment configuration"""
        return {
            'seo_agent': {
                'optimization_mode': OptimizationMode.EXPERT,
                'max_concurrent_campaigns': 10,
                'real_time_monitoring': True,
                'auto_optimization': True
            },
            'ai_models': {
                'keyword_similarity': AIModelConfig(
                    model_name='sentence-transformers/all-mpnet-base-v2',
                    cache_size=50000,
                    batch_size=64
                ),
                'content_optimization': AIModelConfig(
                    model_name='gpt-4-turbo',
                    max_tokens=1024,
                    temperature=0.2
                ),
                'trend_prediction': AIModelConfig(
                    model_name='custom_trend_model_v2',
                    model_path='/models/trend_predictor.pkl',
                    threshold=0.85
                )
            },
            'caching': CacheConfig(
                backend='redis',
                ttl=3600,
                max_size=1000000,
                compression=True,
                persistence=True
            ),
            'performance': PerformanceConfig(
                async_processing=True,
                parallel_workers=8,
                batch_processing=True,
                memory_limit='4GB',
                cpu_limit=4.0,
                optimization_timeout=600
            ),
            'security': {
                'api_rate_limiting': True,
                'authentication_required': True,
                'data_encryption': True,
                'audit_logging': True,
                'request_sanitization': True,
                'output_filtering': True
            }
        }
    
    def _initialize_component_configs(self):
        """
Initialize specific component configurations"""
        
        # External API Configurations
        self.apis = {
            'google_search_console': APIConfig(
                enabled=os.getenv('GOOGLE_SEARCH_CONSOLE_ENABLED', 'true').lower() == 'true',
                api_key=os.getenv('GOOGLE_SEARCH_CONSOLE_API_KEY'),
                rate_limit=1000
            ),
            'google_analytics': APIConfig(
                enabled=os.getenv('GOOGLE_ANALYTICS_ENABLED', 'true').lower() == 'true',
                api_key=os.getenv('GOOGLE_ANALYTICS_API_KEY'),
                rate_limit=2000
            ),
            'semrush': APIConfig(
                enabled=os.getenv('SEMRUSH_ENABLED', 'false').lower() == 'true',
                api_key=os.getenv('SEMRUSH_API_KEY'),
                base_url='https://api.semrush.com',
                rate_limit=500
            ),
            'ahrefs': APIConfig(
                enabled=os.getenv('AHREFS_ENABLED', 'false').lower() == 'true',
                api_key=os.getenv('AHREFS_API_KEY'),
                base_url='https://apiv2.ahrefs.com',
                rate_limit=300
            ),
            'moz': APIConfig(
                enabled=os.getenv('MOZ_ENABLED', 'false').lower() == 'true',
                api_key=os.getenv('MOZ_API_KEY'),
                base_url='https://lsapi.seomoz.com',
                rate_limit=1000
            )
        }
        
        # Database Configuration
        self.database = {
            'seo_data_retention_days': 365,
            'keyword_data_retention_days': 180,
            'campaign_data_retention_days': 730,
            'analytics_data_retention_days': 365,
            'backup_frequency': 'daily',
            'partitioning_enabled': True,
            'indexing_strategy': 'optimized'
        }
        
        # Notification Configuration
        self.notifications = {
            'email_enabled': True,
            'slack_enabled': os.getenv('SLACK_WEBHOOK_URL') is not None,
            'webhook_enabled': True,
            'sms_enabled': False,
            'campaign_completion_notifications': True,
            'performance_alert_notifications': True,
            'error_notifications': True,
            'daily_summary_enabled': True
        }
    
    def _merge_config(self, env_config: Dict[str, Any]):
        """
Merge environment-specific configuration with base configuration"""
        
        for key, value in env_config.items():
            if hasattr(self, key):
                base_config = getattr(self, key)
                if isinstance(base_config, dict) and isinstance(value, dict):
                    base_config.update(value)
                else:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)
    
    def get_ai_model_config(self, model_name: str) -> Optional[AIModelConfig]:
        """
Get configuration for a specific AI model"""
        ai_models = getattr(self, 'ai_models', {})
        return ai_models.get(model_name)
    
    def get_api_config(self, api_name: str) -> Optional[APIConfig]:
        """
Get configuration for a specific API"""
        return self.apis.get(api_name)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
Check if a specific feature is enabled"""
        # Check in various configuration sections
        for config_section in [self.seo_agent, self.keyword_research, 
                              self.content_optimization, self.technical_seo,
                              self.analytics, self.security]:
            if feature_name in config_section:
                return config_section[feature_name]
        return False
    
    def get_optimization_weights(self) -> Dict[str, float]:
        """
Get optimization weights for SEO scoring"""
        return {
            'keyword_relevance': 0.25,
            'content_quality': 0.20,
            'technical_seo': 0.20,
            'user_engagement': 0.15,
            'social_signals': 0.10,
            'backlink_profile': 0.10
        }
    
    def get_performance_thresholds(self) -> Dict[str, float]:
        """
Get performance thresholds for SEO metrics"""
        return {
            'min_seo_score': 0.6,
            'min_content_quality': 0.7,
            'max_page_load_time': 3.0,
            'min_mobile_score': 0.8,
            'min_keyword_density': 0.5,
            'max_keyword_density': 3.0,
            'min_readability_score': 0.6
        }
    
    def export_config(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
Export configuration as dictionary"""
        config_dict = {}
        
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                attr_value = getattr(self, attr_name)
                
                # Skip sensitive data if not requested
                if not include_sensitive and 'api_key' in str(attr_value).lower():
                    continue
                    
                config_dict[attr_name] = attr_value
        
        return config_dict
    
    def validate_config(self) -> Dict[str, Any]:
        """
Validate current configuration"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Validate AI model configurations
        ai_models = getattr(self, 'ai_models', {})
        for model_name, model_config in ai_models.items():
            if model_config.enabled and not model_config.model_name:
                validation_results['errors'].append(
                    f"AI model '{model_name}' is enabled but has no model_name specified"
                )
                validation_results['valid'] = False
        
        # Validate API configurations
        for api_name, api_config in self.apis.items():
            if api_config.enabled and not api_config.api_key:
                validation_results['warnings'].append(
                    f"API '{api_name}' is enabled but has no API key configured"
                )
        
        # Validate performance settings
        performance = getattr(self, 'performance', None)
        if performance:
            if performance.parallel_workers > 16:
                validation_results['warnings'].append(
                    "High number of parallel workers may impact performance"
                )
            
            if performance.memory_limit and int(performance.memory_limit[:-2]) > 8:
                validation_results['recommendations'].append(
                    "Consider monitoring memory usage with high memory limits"
                )
        
        return validation_results

# Global configuration instance
seo_config = SEOAgentConfig()

# Configuration utilities
def get_config(environment: Optional[EnvironmentType] = None) -> SEOAgentConfig:
    """Get SEO agent configuration for specific environment"""
    if environment:
        return SEOAgentConfig(environment)
    return seo_config

def reload_config(environment: Optional[EnvironmentType] = None):
    """
Reload global configuration"""
    global seo_config
    seo_config = SEOAgentConfig(environment or seo_config.environment)

# Export configuration classes and utilities
__all__ = [
    'SEOAgentConfig',
    'EnvironmentType',
    'OptimizationMode',
    'AIModelConfig',
    'CacheConfig',
    'APIConfig',
    'PerformanceConfig',
    'seo_config',
    'get_config',
    'reload_config'
]
