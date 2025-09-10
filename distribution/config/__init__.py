"""
Configuration Module for Ainflue Distribution Platform

This module provides comprehensive configuration management for all distribution
components including database configurations, platform settings, and optimization parameters.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .platform_configs import (
    PlatformConfiguration,
    PlatformSettings,
    APILimits,
    ContentSpecs
)

from .database_configs import (
    DatabaseConfiguration,
    ConnectionPool,
    QueryOptimization,
    BackupSettings
)

from .viral_configs import (
    ViralOptimizationConfig,
    TrendingParameters,
    ViralThresholds,
    AmplificationSettings
)

from .audience_configs import (
    AudienceAnalysisConfig,
    SegmentationSettings,
    BehaviorParameters,
    PredictionConfig
)

from .security_configs import (
    SecurityConfiguration,
    EncryptionSettings,
    AuthenticationConfig,
    AuditSettings
)

from .monitoring_configs import (
    MonitoringConfiguration,
    MetricsSettings,
    AlertingConfig,
    PerformanceThresholds
)

__all__ = [
    # Platform Configuration
    'PlatformConfiguration',
    'PlatformSettings',
    'APILimits',
    'ContentSpecs',
    
    # Database Configuration
    'DatabaseConfiguration',
    'ConnectionPool',
    'QueryOptimization',
    'BackupSettings',
    
    # Viral Optimization
    'ViralOptimizationConfig',
    'TrendingParameters',
    'ViralThresholds',
    'AmplificationSettings',
    
    # Audience Analysis
    'AudienceAnalysisConfig',
    'SegmentationSettings',
    'BehaviorParameters',
    'PredictionConfig',
    
    # Security Configuration
    'SecurityConfiguration',
    'EncryptionSettings',
    'AuthenticationConfig',
    'AuditSettings',
    
    # Monitoring Configuration
    'MonitoringConfiguration',
    'MetricsSettings',
    'AlertingConfig',
    'PerformanceThresholds'
]

__version__ = "1.0.0"