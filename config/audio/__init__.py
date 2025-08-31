"""Audio Configuration Module for IA-Influencer Agent Platform
===========================================================

Professional audio processing and analysis configuration management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""from .audio_processing_config import AudioProcessingConfig
from .codec_config import CodecConfig
from .audio_fingerprint_config import AudioFingerprintConfig
from .spectral_analysis_config import SpectralAnalysisConfig
from .audio_quality_config import AudioQualityConfig
from .streaming_audio_config import StreamingAudioConfig
from .audio_enhancement_config import AudioEnhancementConfig
from .audio_compression_config import AudioCompressionConfig

# New advanced modules
from .platform_optimization_config import (
    PlatformOptimizationConfig, 
    PlatformAudioProfile,
    StreamingPlatform,
    get_platform_profile,
    get_multi_platform_strategy,
    validate_content_for_platform
)
from .ai_processing_config import (
    AIAudioProcessingConfig,
    AIModelConfig,
    EnhancementPipeline,
    AIModelType,
    get_model_config,
    get_pipeline_config,
    optimize_for_hardware
)
from .monetization_config import (
    MonetizationConfig,
    PlatformMonetizationConfig,
    RevenueTrackingConfig,
    LicensingConfig,
    PaymentProcessorConfig,
    AutomatedPayoutConfig
)
from .content_protection_config import (
    ContentProtectionConfig,
    FingerprintingConfig,
    WatermarkingConfig,
    DetectionConfig,
    EnforcementConfig,
    ProtectionLevel,
    get_protection_profile,
    validate_content_protection
)
from .metadata_enrichment_config import (
    MetadataEnrichmentConfig,
    TaggingConfig,
    SEOOptimizationConfig,
    ContentClassificationConfig,
    AnalyticsTagConfig,
    enrich_audio_metadata
)
from .collaboration_config import (
    CollaborationConfig,
    MatchingConfig,
    NetworkingConfig,
    ProjectManagementConfig,
    CommunicationConfig,
    WorkflowConfig
)
from .distribution_config import (
    DistributionConfig,
    PlatformDistributionConfig,
    AutomatedUploadConfig,
    SyncConfig,
    SchedulingConfig,
    MultiPlatformStrategy
)
from .quality_assurance_config import (
    QualityAssuranceConfig,
    ValidationConfig,
    TestingConfig,
    BenchmarkConfig,
    PerformanceConfig,
    ComplianceConfig
)
from .real_time_config import (
    RealTimeConfig,
    StreamingConfig,
    LiveProcessingConfig,
    BroadcastConfig,
    InteractiveConfig,
    LatencyOptimizationConfig
    MonetizationType,
    LicensingTier,
    get_platform_config as get_monetization_platform_config,
    calculate_revenue,
    get_multi_platform_strategy as get_monetization_strategy
)
from .content_protection_config import (
    ContentProtectionConfig,
    ProtectionProfile,
    ProtectionLevel,
    FingerprintType,
    get_protection_profile,
    validate_protection_setup,
    get_protection_recommendations
)


# Export all configuration classes and functions
__all__ = [
    # Core processing configurations
    "AudioProcessingConfig",
    "CodecConfig", 
    "AudioFingerprintConfig",
    "SpectralAnalysisConfig",
    "AudioQualityConfig",
    "StreamingAudioConfig",
    "AudioEnhancementConfig",
    "AudioCompressionConfig",
    
    # Platform optimization
    "PlatformOptimizationConfig",
    "PlatformAudioProfile",
    "StreamingPlatform",
    "get_platform_profile",
    "get_multi_platform_strategy",
    "validate_content_for_platform",
    
    # AI processing
    "AIAudioProcessingConfig",
    "AIModelConfig",
    "EnhancementPipeline",
    "AIModelType",
    "get_model_config",
    "get_pipeline_config",
    "optimize_for_hardware",
    
    # Monetization
    "MonetizationConfig",
    "PlatformMonetizationConfig",
    "RevenueTrackingConfig",
    "LicensingConfig",
    "PaymentProcessorConfig",
    "AutomatedPayoutConfig",
    
    # Content protection
    "ContentProtectionConfig",
    "FingerprintingConfig",
    "WatermarkingConfig",
    "DetectionConfig",
    "EnforcementConfig",
    "ProtectionLevel",
    "get_protection_profile",
    "validate_content_protection",
    
    # Metadata enrichment
    "MetadataEnrichmentConfig",
    "TaggingConfig",
    "SEOOptimizationConfig",
    "ContentClassificationConfig",
    "AnalyticsTagConfig",
    "enrich_audio_metadata",
    
    # Collaboration
    "CollaborationConfig",
    "MatchingConfig",
    "NetworkingConfig",
    "ProjectManagementConfig",
    "CommunicationConfig",
    "WorkflowConfig",
    
    # Distribution
    "DistributionConfig",
    "PlatformDistributionConfig",
    "AutomatedUploadConfig",
    "SyncConfig",
    "SchedulingConfig",
    "MultiPlatformStrategy",
    
    # Quality assurance
    "QualityAssuranceConfig",
    "ValidationConfig",
    "TestingConfig",
    "BenchmarkConfig",
    "PerformanceConfig",
    "ComplianceConfig",
    
    # Real-time processing
    "RealTimeConfig",
    "StreamingConfig",
    "LiveProcessingConfig",
    "BroadcastConfig",
    "InteractiveConfig",
    "LatencyOptimizationConfig",
]


# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

__all__ = [
    # Core audio processing configs
    'AudioProcessingConfig',
    'CodecConfig',
    'AudioFingerprintConfig',
    'SpectralAnalysisConfig',
    'AudioQualityConfig',
    'StreamingAudioConfig',
    'AudioEnhancementConfig',
    'AudioCompressionConfig',
    
    # Platform optimization
    'PlatformOptimizationConfig',
    'PlatformAudioProfile', 
    'StreamingPlatform',
    'get_platform_profile',
    'get_multi_platform_strategy',
    'validate_content_for_platform',
    
    # AI processing
    'AIAudioProcessingConfig',
    'AIModelConfig',
    'EnhancementPipeline',
    'AIModelType',
    'get_model_config',
    'get_pipeline_config', 
    'optimize_for_hardware',
    
    # Monetization
    'MonetizationConfig',
    'PlatformMonetizationConfig',
    'MonetizationType',
    'LicensingTier',
    'get_monetization_platform_config',
    'calculate_revenue',
    'get_monetization_strategy',
    
    # Content protection
    'ContentProtectionConfig',
    'ProtectionProfile',
    'ProtectionLevel',
    'FingerprintType',
    'get_protection_profile',
    'validate_protection_setup',
    'get_protection_recommendations'
]
