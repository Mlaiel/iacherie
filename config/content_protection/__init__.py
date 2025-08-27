"""
Content Protection Configuration Module for IA-Influencer Agent Platform
=========================================================================

Professional content protection and fingerprinting configuration management.
Industrial-grade configuration for multi-format content protection, automated takedowns,
licensing management, and DMCA compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.

MODULES OVERVIEW:
================
- fingerprint_engine_config: AI fingerprinting configuration (audio, video, image, text)
- crawler_config: Web crawler configuration for content surveillance
- detection_config: Content detection and analysis configuration
- matching_config: Similarity matching and comparison configuration
- watermark_config: Digital watermarking configuration
- takedown_config: Automated takedown procedures configuration
- licensing_config: Content licensing and monetization configuration
- dmca_config: DMCA compliance and automation configuration

FEATURES:
=========
✅ Multi-format fingerprinting (Audio, Video, Image, Text)
✅ Real-time content surveillance across platforms
✅ AI-powered similarity matching and duplicate detection
✅ Invisible watermarking with robustness testing
✅ Automated DMCA takedown procedures
✅ Smart licensing with automated negotiations
✅ Revenue tracking and royalty distribution
✅ Legal compliance and audit trails
✅ Enterprise-grade security and performance
✅ Industrial scalability and reliability
"""

from .fingerprint_engine_config import (
    FingerprintEngineConfig,
    ContentType,
    FingerprintAlgorithm,
    AudioFingerprintConfig,
    VideoFingerprintConfig,
    ImageFingerprintConfig,
    TextFingerprintConfig,
    VectorStoreConfig,
    PerformanceConfig as FingerprintPerformanceConfig,
    SecurityConfig as FingerprintSecurityConfig
)

from .crawler_config import (
    WebCrawlerConfig,
    CrawlerType,
    Platform,
    CrawlingStrategy,
    PlatformCredentials,
    RateLimitConfig,
    RetryConfig,
    ScrapingConfig,
    ContentFilterConfig,
    StorageConfig,
    MonitoringConfig,
    YoutubeCrawlerConfig,
    TiktokCrawlerConfig,
    InstagramCrawlerConfig,
    TwitterCrawlerConfig
)

from .detection_config import (
    ContentDetectionConfig,
    DetectionMode,
    DetectionLevel,
    ContentCategory,
    DetectionEngine,
    AudioDetectionConfig,
    VideoDetectionConfig,
    ImageDetectionConfig,
    TextDetectionConfig,
    RealTimeConfig,
    BatchConfig,
    MachineLearningConfig,
    QualityAssuranceConfig,
    OutputConfig
)

from .matching_config import (
    SimilarityMatchingConfig,
    SimilarityMetric,
    MatchingAlgorithm,
    ContentSimilarityType,
    VectorMatchingConfig,
    HashMatchingConfig,
    AudioMatchingConfig,
    VideoMatchingConfig,
    ImageMatchingConfig,
    TextMatchingConfig,
    PerformanceConfig as MatchingPerformanceConfig,
    QualityConfig,
    AlertConfig
)

from .watermark_config import (
    WatermarkConfig,
    WatermarkType,
    WatermarkAlgorithm,
    EmbeddingStrength,
    WatermarkPayload,
    AudioWatermarkConfig,
    VideoWatermarkConfig,
    ImageWatermarkConfig,
    TextWatermarkConfig,
    RobustnessConfig,
    SecurityConfig as WatermarkSecurityConfig,
    ExtractionConfig,
    QualityAssessmentConfig
)

from .takedown_config import (
    TakedownConfig,
    TakedownType,
    TakedownStatus,
    PlatformType,
    LegalJurisdiction,
    TakedownTemplate,
    DMCAConfig as TakedownDMCAConfig,
    PlatformTakedownConfig,
    LegalComplianceConfig,
    EscalationConfig,
    NotificationConfig,
    DocumentationConfig
)

from .licensing_config import (
    LicensingConfig,
    LicenseType,
    UsageType,
    LicenseStatus,
    PricingModel,
    Territory,
    LicenseTerms,
    PricingStructure,
    AutomatedNegotiationConfig,
    RoyaltyTrackingConfig,
    ComplianceConfig,
    IntegrationConfig
)

from .dmca_config import (
    DMCAConfig,
    DMCANoticeType,
    DMCAStatus,
    InfringementType,
    CopyrightHolderInfo,
    InfringementEvidence,
    DMCANoticeTemplate,
    SafeHarborConfig,
    CounterNotificationConfig,
    AutomationConfig as DMCAAutomationConfig,
    TrackingConfig as DMCATrackingConfig
)

from .revenue_tracking_config import (
    RevenueTrackingConfig,
    RevenueTrackingMode,
    PlatformType,
    RevenueStreamType,
    CurrencyType,
    PaymentProcessor,
    PlatformCredentials,
    RevenueMetricsConfig,
    PaymentProcessingConfig,
    LicensingAutomationConfig,
    ComplianceConfig as RevenueComplianceConfig,
    AlertingConfig as RevenueAlertingConfig,
    PerformanceConfig as RevenuePerformanceConfig,
    SecurityConfig as RevenueSecurityConfig
)

from .platform_integration_config import (
    PlatformIntegrationConfig,
    PlatformConfig,
    IntegrationMethod,
    AuthenticationMethod,
    PlatformCapability,
    DataFormat,
    RateLimitConfig as PlatformRateLimitConfig,
    AuthConfig,
    ContentFilterConfig as PlatformContentFilterConfig,
    MonitoringConfig as PlatformMonitoringConfig,
    DataExtractionConfig,
    ErrorHandlingConfig,
    YoutubeConfig,
    InstagramConfig,
    TiktokConfig,
    TwitterConfig,
    SpotifyConfig,
    SoundcloudConfig
)

from .automated_surveillance_config import (
    AutomatedSurveillanceConfig,
    SurveillanceMode,
    MonitoringScope,
    AlertSeverity,
    AlertType,
    ResponseAction,
    EvidenceType,
    SurveillanceSchedule,
    ContentTargetConfig,
    AlertConfig as SurveillanceAlertConfig,
    EvidenceCollectionConfig,
    ResponseAutomationConfig,
    PerformanceConfig as SurveillancePerformanceConfig,
    SecurityConfig as SurveillanceSecurityConfig,
    ReportingConfig as SurveillanceReportingConfig
)

from .analytics_reporting_config import (
    AnalyticsReportingConfig,
    AnalyticsScope,
    MetricType,
    ReportType,
    ReportFormat,
    AggregationLevel,
    VisualizationType,
    MetricConfig,
    DashboardConfig,
    ReportScheduleConfig,
    DataSourceConfig,
    PerformanceMetricsConfig,
    ComplianceReportingConfig,
    AdvancedAnalyticsConfig,
    SecurityConfig as AnalyticsSecurityConfig
)

# Main configuration classes
__all__ = [
    # Primary Configuration Classes
    'FingerprintEngineConfig',
    'WebCrawlerConfig',
    'ContentDetectionConfig',
    'SimilarityMatchingConfig',
    'WatermarkConfig',
    'TakedownConfig',
    'LicensingConfig',
    'DMCAConfig',
    'RevenueTrackingConfig',
    'PlatformIntegrationConfig',
    'AutomatedSurveillanceConfig',
    'AnalyticsReportingConfig',
    
    # Fingerprinting Components
    'ContentType',
    'FingerprintAlgorithm',
    'AudioFingerprintConfig',
    'VideoFingerprintConfig',
    'ImageFingerprintConfig',
    'TextFingerprintConfig',
    'VectorStoreConfig',
    'FingerprintPerformanceConfig',
    'FingerprintSecurityConfig',
    
    # Crawler Components
    'CrawlerType',
    'Platform',
    'CrawlingStrategy',
    'PlatformCredentials',
    'RateLimitConfig',
    'RetryConfig',
    'ScrapingConfig',
    'ContentFilterConfig',
    'StorageConfig',
    'MonitoringConfig',
    'YoutubeCrawlerConfig',
    'TiktokCrawlerConfig',
    'InstagramCrawlerConfig',
    'TwitterCrawlerConfig',
    
    # Detection Components
    'DetectionMode',
    'DetectionLevel',
    'ContentCategory',
    'DetectionEngine',
    'AudioDetectionConfig',
    'VideoDetectionConfig',
    'ImageDetectionConfig',
    'TextDetectionConfig',
    'RealTimeConfig',
    'BatchConfig',
    'MachineLearningConfig',
    'QualityAssuranceConfig',
    'OutputConfig',
    
    # Matching Components
    'SimilarityMetric',
    'MatchingAlgorithm',
    'ContentSimilarityType',
    'VectorMatchingConfig',
    'HashMatchingConfig',
    'AudioMatchingConfig',
    'VideoMatchingConfig',
    'ImageMatchingConfig',
    'TextMatchingConfig',
    'MatchingPerformanceConfig',
    'QualityConfig',
    'AlertConfig',
    
    # Watermark Components
    'WatermarkType',
    'WatermarkAlgorithm',
    'EmbeddingStrength',
    'WatermarkPayload',
    'AudioWatermarkConfig',
    'VideoWatermarkConfig',
    'ImageWatermarkConfig',
    'TextWatermarkConfig',
    'RobustnessConfig',
    'WatermarkSecurityConfig',
    'ExtractionConfig',
    'QualityAssessmentConfig',
    
    # Takedown Components
    'TakedownType',
    'TakedownStatus',
    'PlatformType',
    'LegalJurisdiction',
    'TakedownTemplate',
    'TakedownDMCAConfig',
    'PlatformTakedownConfig',
    'LegalComplianceConfig',
    'EscalationConfig',
    'NotificationConfig',
    'DocumentationConfig',
    
    # Licensing Components
    'LicenseType',
    'UsageType',
    'LicenseStatus',
    'PricingModel',
    'Territory',
    'LicenseTerms',
    'PricingStructure',
    'AutomatedNegotiationConfig',
    'RoyaltyTrackingConfig',
    'ComplianceConfig',
    'IntegrationConfig',
    
    # DMCA Components
    'DMCANoticeType',
    'DMCAStatus',
    'InfringementType',
    'CopyrightHolderInfo',
    'InfringementEvidence',
    'DMCANoticeTemplate',
    'SafeHarborConfig',
    'CounterNotificationConfig',
    'DMCAAutomationConfig',
    'DMCATrackingConfig',
    
    # Revenue Tracking Components
    'RevenueTrackingMode',
    'RevenueStreamType',
    'CurrencyType',
    'PaymentProcessor',
    'RevenueMetricsConfig',
    'PaymentProcessingConfig',
    'LicensingAutomationConfig',
    'RevenueComplianceConfig',
    'RevenueAlertingConfig',
    'RevenuePerformanceConfig',
    'RevenueSecurityConfig',
    
    # Platform Integration Components
    'PlatformConfig',
    'IntegrationMethod',
    'AuthenticationMethod',
    'PlatformCapability',
    'DataFormat',
    'PlatformRateLimitConfig',
    'AuthConfig',
    'PlatformContentFilterConfig',
    'PlatformMonitoringConfig',
    'DataExtractionConfig',
    'ErrorHandlingConfig',
    'YoutubeConfig',
    'InstagramConfig',
    'TiktokConfig',
    'TwitterConfig',
    'SpotifyConfig',
    'SoundcloudConfig',
    
    # Automated Surveillance Components
    'SurveillanceMode',
    'MonitoringScope',
    'AlertSeverity',
    'AlertType',
    'ResponseAction',
    'EvidenceType',
    'SurveillanceSchedule',
    'ContentTargetConfig',
    'SurveillanceAlertConfig',
    'EvidenceCollectionConfig',
    'ResponseAutomationConfig',
    'SurveillancePerformanceConfig',
    'SurveillanceSecurityConfig',
    'SurveillanceReportingConfig',
    
    # Analytics and Reporting Components
    'AnalyticsScope',
    'MetricType',
    'ReportType',
    'ReportFormat',
    'AggregationLevel',
    'VisualizationType',
    'MetricConfig',
    'DashboardConfig',
    'ReportScheduleConfig',
    'DataSourceConfig',
    'PerformanceMetricsConfig',
    'ComplianceReportingConfig',
    'AdvancedAnalyticsConfig',
    'AnalyticsSecurityConfig'
]

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Import index module for unified access
from .index import (
    ContentProtectionConfigIndex,
    config_index,
    create_enterprise_production_config,
    create_startup_config,
    create_compliance_focused_config,
    create_development_environment_config,
    create_testing_environment_config
)

# Add index exports to __all__
__all__.extend([
    'ContentProtectionConfigIndex',
    'config_index',
    'create_enterprise_production_config',
    'create_startup_config', 
    'create_compliance_focused_config',
    'create_development_environment_config',
    'create_testing_environment_config'
])
