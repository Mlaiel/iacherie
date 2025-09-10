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
    ViralPredictionConfig,
    TrendAnalysisConfig,
    TimingOptimizationConfig,
    ViralAmplificationConfig,
    NetworkDynamicsConfig,
    DEFAULT_VIRAL_CONFIG,
    VIRAL_CONFIG
)

from .security_configs import (
    SecurityConfig,
    SecurityLevel,
    ThreatLevel,
    EncryptionAlgorithm,
    AuthenticationConfig,
    APISecurityConfig,
    EncryptionConfig,
    VaultConfig,
    ThreatDetectionConfig,
    ComplianceConfig,
    AccessControlConfig,
    SecurityMonitoringConfig,
    DEFAULT_SECURITY_CONFIG,
    SECURITY_CONFIG
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
    
    # Viral Optimization Configuration
    'ViralOptimizationConfig',
    'ViralPredictionConfig',
    'TrendAnalysisConfig',
    'TimingOptimizationConfig',
    'ViralAmplificationConfig',
    'NetworkDynamicsConfig',
    'DEFAULT_VIRAL_CONFIG',
    'VIRAL_CONFIG',
    
    # Security Configuration
    'SecurityConfig',
    'SecurityLevel',
    'ThreatLevel',
    'EncryptionAlgorithm',
    'AuthenticationConfig',
    'APISecurityConfig',
    'EncryptionConfig',
    'VaultConfig',
    'ThreatDetectionConfig',
    'ComplianceConfig',
    'AccessControlConfig',
    'SecurityMonitoringConfig',
    'DEFAULT_SECURITY_CONFIG',
    'SECURITY_CONFIG'
]

__version__ = "1.0.0"