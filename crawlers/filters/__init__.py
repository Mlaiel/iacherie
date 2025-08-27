"""
IA Influencer Agent - Filters Module
====================================

Professional content filtering system for multi-format content analysis.
Centralized export point for all filter modules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ STRICT COPYRIGHT PROTECTION ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
UNAUTHORIZED USE STRICTLY PROHIBITED - Legal action will be taken.

Technical Team Expertise:
- Lead IA Developer: Advanced AI/ML algorithms and neural networks
- Backend Senior: Enterprise architecture and microservices
- ML Engineer: Machine learning pipelines and model optimization
- Database Administrator: Data architecture and optimization
- Security Specialist: Cybersecurity and data protection
- Microservices Architect: Distributed systems and scalability
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: Infrastructure automation and deployment
- IA Prompt Engineer: Prompt optimization and AI interaction

Project Owner: Fahed Mlaiel - mlaiel@live.de
"""

# Core engine and configuration
from .filter_engine import (
    ContentFilterEngine, 
    FilterResponse, 
    FilterResult, 
    FilterType, 
    ContentItem
)

from .config import (
    FilterConfigManager,
    FilterType as ConfigFilterType,
    QualityLevel,
    SecurityLevel,
    AudioFilterConfig,
    VideoFilterConfig,
    ImageFilterConfig,
    TextFilterConfig,
    SecurityFilterConfig,
    PerformanceFilterConfig
)

# Advanced configuration
from .advanced_config import (
    AdvancedFilterConfig,
    ProcessingPriority,
    AnalysisDepth,
    OptimizationLevel
)

# Specialized content filters
from .audio_filters import (
    AudioContentFilter,
    AudioQualityMetrics,
    AdvancedAudioAnalyzer,
    AudioContentClassifier
)

from .video_filters import VideoContentFilter
from .image_filters import ImageContentFilter
from .text_filters import TextContentFilter

from .security_filters import (
    SecurityContentFilter,
    ThreatAnalyzer,
    VulnerabilityScanner,
    SecurityIncidentHandler
)

from .performance_filters import (
    PerformanceContentFilter,
    QualityContentFilter,
    RelevanceContentFilter,
    DuplicateContentFilter
)

# New advanced modules
from .content_filters import (
    IntelligentContentAnalyzer,
    ContentFilterOrchestrator,
    ContentCategory,
    ContentComplexity,
    ContentMetadata
)

from .quality_assurance import (
    QualityAssuranceEngine,
    TechnicalQualityAnalyzer,
    ContentQualityAnalyzer,
    QualityMetrics,
    QualityDimension,
    QualityLevel as QAQualityLevel
)

from .monetization_filters import (
    MonetizationEngine,
    MarketAnalyzer,
    RevenueEstimator,
    MonetizationMetrics,
    MonetizationTier,
    RevenueModel,
    Platform
)

from .collaboration_filters import (
    CollaborationEngine,
    CreatorProfileAnalyzer,
    CollaborationMatcher,
    CollaborationMetrics,
    CollaborationOpportunity,
    CollaborationType,
    CompatibilityLevel,
    CreatorProfile
)

__all__ = [
    # Core engine
    'ContentFilterEngine',
    'FilterResponse',
    'FilterResult',
    'FilterType',
    'ContentItem',
    
    # Configuration
    'FilterConfigManager',
    'ConfigFilterType',
    'QualityLevel',
    'SecurityLevel',
    'AudioFilterConfig',
    'VideoFilterConfig',
    'ImageFilterConfig',
    'TextFilterConfig',
    'SecurityFilterConfig',
    'PerformanceFilterConfig',
    'AdvancedFilterConfig',
    'ProcessingPriority',
    'AnalysisDepth',
    'OptimizationLevel',
    
    # Basic content filters
    'AudioContentFilter',
    'VideoContentFilter',
    'ImageContentFilter',
    'TextContentFilter',
    'SecurityContentFilter',
    'PerformanceContentFilter',
    'QualityContentFilter',
    'RelevanceContentFilter',
    'DuplicateContentFilter',
    
    # Audio analysis components
    'AudioQualityMetrics',
    'AdvancedAudioAnalyzer',
    'AudioContentClassifier',
    
    # Security components
    'ThreatAnalyzer',
    'VulnerabilityScanner',
    'SecurityIncidentHandler',
    
    # Advanced content analysis
    'IntelligentContentAnalyzer',
    'ContentFilterOrchestrator',
    'ContentCategory',
    'ContentComplexity',
    'ContentMetadata',
    
    # Quality assurance
    'QualityAssuranceEngine',
    'TechnicalQualityAnalyzer',
    'ContentQualityAnalyzer',
    'QualityMetrics',
    'QualityDimension',
    'QAQualityLevel',
    
    # Monetization analysis
    'MonetizationEngine',
    'MarketAnalyzer',
    'RevenueEstimator',
    'MonetizationMetrics',
    'MonetizationTier',
    'RevenueModel',
    'Platform',
    
    # Collaboration matching
    'CollaborationEngine',
    'CreatorProfileAnalyzer',
    'CollaborationMatcher',
    'CollaborationMetrics',
    'CollaborationOpportunity',
    'CollaborationType',
    'CompatibilityLevel',
    'CreatorProfile'
]

# Module version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "Copyright 2025, Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Unauthorized use prohibited"

# Export grouped functionality
AUDIO_COMPONENTS = [
    'AudioContentFilter', 
    'AudioQualityMetrics', 
    'AdvancedAudioAnalyzer', 
    'AudioContentClassifier'
]

QUALITY_COMPONENTS = [
    'QualityAssuranceEngine', 
    'TechnicalQualityAnalyzer', 
    'ContentQualityAnalyzer'
]

MONETIZATION_COMPONENTS = [
    'MonetizationEngine', 
    'MarketAnalyzer', 
    'RevenueEstimator'
]

COLLABORATION_COMPONENTS = [
    'CollaborationEngine', 
    'CreatorProfileAnalyzer', 
    'CollaborationMatcher'
]

SECURITY_COMPONENTS = [
    'SecurityContentFilter', 
    'ThreatAnalyzer', 
    'VulnerabilityScanner'
]

# Helper function for module initialization
def get_available_filters():
    """Get list of available filter types."""
    return [
        'audio', 'video', 'image', 'text', 
        'security', 'performance', 'quality',
        'monetization', 'collaboration'
    ]

def create_comprehensive_filter_engine(config_path: str = None):
    """Create a comprehensive filter engine with all components."""
    from .config import FilterConfigManager
    
    config_manager = FilterConfigManager(config_path)
    
    # Initialize all engines
    engines = {
        'content': ContentFilterEngine(config_manager),
        'quality': QualityAssuranceEngine(config_manager),
        'monetization': MonetizationEngine(config_manager),
        'collaboration': CollaborationEngine(config_manager)
    }
    
    return engines
    'QualityLevel',
    'SecurityLevel',
    'AudioFilterConfig',
    'VideoFilterConfig',
    'ImageFilterConfig',
    'TextFilterConfig',
    'SecurityFilterConfig',
    'PerformanceFilterConfig',
    
    # Content filters
    'AudioContentFilter',
    'VideoContentFilter',
    'ImageContentFilter',
    'TextContentFilter',
    'SecurityContentFilter',
    'PerformanceContentFilter',
    'QualityContentFilter',
    'RelevanceContentFilter',
    'DuplicateContentFilter'
]

# Version information
__version__ = '1.0.0'
__author__ = 'Fahed Mlaiel'
__email__ = 'mlaiel@live.de'
__copyright__ = 'Copyright 2024 - All rights reserved'
