"""
🎯 Advanced Metrics Module - Enterprise Analytics & Business Intelligence
========================================================================

Comprehensive advanced metrics collection and analysis system for the Ainflue platform.
Provides enterprise-grade business KPIs, user engagement analytics, content performance
metrics, and collaboration success tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
CRITICAL WARNING: Unauthorized use, copying, or distribution strictly prohibited.

Team Specialties:
- Lead IA Developer + Backend Senior + ML Engineer
- DBA + Security + Microservices + Audio + DevOps
- IA Prompt Engineer

Business Logic Flow:
User (musician/blogger/photographer/influencer/comedian) 
→ Upload multi-format content 
→ IA protection & rights validation
→ SEO professional optimization 
→ Collaboration matching + gamification
→ Distribution multi-platforms
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary"
__copyright__ = "Copyright (c) 2025 Fahed Mlaiel. All rights reserved."

# Core module imports
from .business_kpis import (
    BusinessKPICollector,
    BusinessKPIAnalyzer,
    KPIMetric,
    KPICategory,
    KPIAggregationType,
    RevenueMetrics,
    UserAcquisitionMetrics,
    ContentCreationMetrics,
    PlatformGrowthMetrics
)

from .user_engagement_metrics import (
    UserEngagementAnalyzer,
    EngagementMetricsCollector,
    EngagementEvent,
    EngagementType,
    UserSessionMetrics,
    ContentInteractionMetrics,
    SocialEngagementMetrics,
    RetentionAnalytics
)

from .content_performance import (
    ContentPerformanceAnalyzer,
    ContentMetricsCollector,
    ContentPerformanceMetrics,
    PlatformPerformanceTracker,
    ViralityAnalyzer,
    ContentOptimizationEngine,
    CrossPlatformAnalytics,
    ContentLifecycleMetrics
)

from .remix_quality_metrics import (
    RemixQualityAnalyzer,
    AIRemixMetricsCollector,
    RemixQualityMetrics,
    QualityDimension,
    RemixType,
    QualityScorer,
    RemixPerformanceTracker,
    CreativeInnovationMetrics
)

from .collaboration_success import (
    CollaborationSuccessAnalyzer,
    CollaborationMetricsCollector,
    CollaborationMetrics,
    CollaborationType,
    SuccessIndicator,
    NetworkEffectAnalyzer,
    PartnershipROICalculator,
    CommunityGrowthMetrics
)

from .index import (
    AdvancedMetricsManager,
    MetricsAggregator,
    MetricsDashboard,
    MetricsReporter,
    initialize_advanced_metrics,
    get_metrics_manager
)

# Export all public classes and functions
__all__ = [
    # Core managers
    "AdvancedMetricsManager",
    "MetricsAggregator", 
    "MetricsDashboard",
    "MetricsReporter",
    
    # Business KPIs
    "BusinessKPICollector",
    "BusinessKPIAnalyzer",
    "KPIMetric",
    "KPICategory",
    "KPIAggregationType",
    "RevenueMetrics",
    "UserAcquisitionMetrics",
    "ContentCreationMetrics",
    "PlatformGrowthMetrics",
    
    # User engagement
    "UserEngagementAnalyzer",
    "EngagementMetricsCollector",
    "EngagementEvent",
    "EngagementType",
    "UserSessionMetrics",
    "ContentInteractionMetrics",
    "SocialEngagementMetrics",
    "RetentionAnalytics",
    
    # Content performance
    "ContentPerformanceAnalyzer",
    "ContentMetricsCollector",
    "ContentPerformanceMetrics",
    "PlatformPerformanceTracker",
    "ViralityAnalyzer",
    "ContentOptimizationEngine",
    "CrossPlatformAnalytics",
    "ContentLifecycleMetrics",
    
    # Remix quality
    "RemixQualityAnalyzer",
    "AIRemixMetricsCollector",
    "RemixQualityMetrics",
    "QualityDimension",
    "RemixType",
    "QualityScorer",
    "RemixPerformanceTracker",
    "CreativeInnovationMetrics",
    
    # Collaboration success
    "CollaborationSuccessAnalyzer",
    "CollaborationMetricsCollector",
    "CollaborationMetrics",
    "CollaborationType",
    "SuccessIndicator",
    "NetworkEffectAnalyzer",
    "PartnershipROICalculator",
    "CommunityGrowthMetrics",
    
    # Utility functions
    "initialize_advanced_metrics",
    "get_metrics_manager"
]

# Module metadata
MODULE_INFO = {
    "name": "Advanced Metrics Module",
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "description": "Enterprise-grade advanced metrics and business intelligence system",
    "business_logic": [
        "Multi-format content upload processing",
        "IA protection and rights validation",
        "SEO optimization and platform readiness", 
        "Collaboration matching and gamification",
        "Multi-platform distribution analytics"
    ],
    "supported_content_types": [
        "audio", "video", "image", "text", "blog",
        "photography", "comedy", "music", "podcast"
    ],
    "supported_platforms": [
        "spotify", "youtube", "instagram", "tiktok", "linkedin",
        "twitter", "facebook", "soundcloud", "medium", "wordpress"
    ],
    "team_expertise": [
        "Lead IA Developer",
        "Backend Senior Engineer", 
        "ML Engineer",
        "Database Administrator",
        "Security Specialist",
        "Microservices Architect",
        "Audio Processing Expert",
        "DevOps Engineer",
        "IA Prompt Engineer"
    ]
}

def get_module_info() -> dict:
    """Get comprehensive module information and metadata"""
    return MODULE_INFO.copy()

def get_health_status() -> dict:
    """Get module health status and operational metrics"""
    return {
        "status": "operational",
        "version": __version__,
        "components": {
            "business_kpis": "active",
            "user_engagement": "active", 
            "content_performance": "active",
            "remix_quality": "active",
            "collaboration_success": "active"
        },
        "last_updated": "2025-01-01T00:00:00Z",
        "author": __author__,
        "contact": __email__
    }