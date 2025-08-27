"""
Content Guidance Module - AI-Powered Content Strategy and Optimization
=====================================================================

This module provides comprehensive content guidance capabilities including
optimization, platform recommendations, monetization strategies, trend analysis,
audience insights, scheduling optimization, collaboration discovery, brand safety
compliance, performance tracking, and creative assistance for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use prohibited and legally prosecuted.
"""

# Content Optimization
from .content_optimizer import (
    ContentOptimizer,
    OptimizationEngine,
    ContentFormat,
    OptimizationType,
    OptimizationResult,
    ContentAnalysis,
    PlatformRequirements,
    OptimizationRecommendation
)

# Platform Recommendations
from .platform_recommendations import (
    PlatformRecommendationEngine,
    ContentStrategyAnalyzer,
    PlatformProfile,
    ContentStrategy,
    CrossPlatformStrategy,
    PlatformRecommendation,
    StrategyMetrics,
    CompetitorAnalysis
)

# Monetization Guidance
from .monetization_guidance import (
    MonetizationGuidanceEngine,
    RevenueOptimizer,
    MonetizationStrategy,
    RevenueStream,
    MarketAnalysis,
    PricingStrategy,
    SponsorshipOpportunity,
    RevenueProjection
)

# Trend Analysis
from .trend_analyzer import (
    TrendAnalyzer,
    ContentTrendEngine,
    TrendData,
    TrendPrediction,
    ViralityFactor,
    TrendingContent,
    HashtagAnalysis,
    TrendReport
)

# Audience Insights
from .audience_insights import (
    AudienceInsightEngine,
    EngagementAnalyzer,
    AudienceProfile,
    DemographicData,
    EngagementPattern,
    AudienceSegment,
    ContentPreference,
    AudienceInsight
)

# Content Scheduling
from .content_scheduler import (
    PublishingOptimizer,
    ContentScheduler,
    SchedulingStrategy,
    OptimalTiming,
    ContentCalendar,
    PublishingRecommendation,
    SchedulingAnalytics,
    TimingOptimization
)

# Collaboration Finder
from .collaboration_finder import (
    InfluencerMatchingEngine,
    CollaborationFinder,
    CreatorProfile,
    CollaborationOpportunity,
    PartnershipMatch,
    CollaborationMetrics,
    NetworkAnalysis,
    PartnershipRecommendation
)

# Brand Safety
from .brand_safety import (
    ContentComplianceEngine,
    BrandSafetyAnalyzer,
    ComplianceCheck,
    SafetyAnalysis,
    BrandCompatibility,
    RegulatoryCompliance,
    ContentModeration,
    SafetyReport
)

# Performance Tracking
from .performance_tracker import (
    MetricsCollector,
    PerformanceAnalyzer,
    PerformanceTracker,
    MetricType,
    TimeFrame,
    PerformanceCategory,
    TrendDirection,
    MetricDataPoint,
    PerformanceTrend,
    ContentPerformanceMetrics,
    PlatformPerformance,
    PerformanceBenchmark,
    PerformanceInsight,
    PerformanceReport
)

# Creative Assistant
from .creative_assistant import (
    ContentIdeationEngine,
    CreativeAssistant,
    ContentType,
    CreativeStyle,
    IdeationType,
    CreativityLevel,
    ContentIdea,
    CreativeTemplate,
    ContentScript,
    VisualConcept,
    AudioConcept,
    CreativeBrief
)

# Central Orchestrator and Index
from .index import (
    ContentGuidanceOrchestrator,
    ContentGuidanceRequest,
    ContentGuidanceResponse,
    ContentGuidanceServiceType,
    content_guidance_orchestrator,
    get_comprehensive_content_guidance,
    get_specific_content_guidance
)

__all__ = [
    # Content Optimization
    'ContentOptimizer',
    'OptimizationEngine',
    'ContentFormat',
    'OptimizationType',
    'OptimizationResult',
    'ContentAnalysis',
    'PlatformRequirements',
    'OptimizationRecommendation',
    
    # Platform Recommendations
    'PlatformRecommendationEngine',
    'ContentStrategyAnalyzer',
    'PlatformProfile',
    'ContentStrategy',
    'CrossPlatformStrategy',
    'PlatformRecommendation',
    'StrategyMetrics',
    'CompetitorAnalysis',
    
    # Monetization Guidance
    'MonetizationGuidanceEngine',
    'RevenueOptimizer',
    'MonetizationStrategy',
    'RevenueStream',
    'MarketAnalysis',
    'PricingStrategy',
    'SponsorshipOpportunity',
    'RevenueProjection',
    
    # Trend Analysis
    'TrendAnalyzer',
    'ContentTrendEngine',
    'TrendData',
    'TrendPrediction',
    'ViralityFactor',
    'TrendingContent',
    'HashtagAnalysis',
    'TrendReport',
    
    # Audience Insights
    'AudienceInsightEngine',
    'EngagementAnalyzer',
    'AudienceProfile',
    'DemographicData',
    'EngagementPattern',
    'AudienceSegment',
    'ContentPreference',
    'AudienceInsight',
    
    # Content Scheduling
    'PublishingOptimizer',
    'ContentScheduler',
    'SchedulingStrategy',
    'OptimalTiming',
    'ContentCalendar',
    'PublishingRecommendation',
    'SchedulingAnalytics',
    'TimingOptimization',
    
    # Collaboration Finder
    'InfluencerMatchingEngine',
    'CollaborationFinder',
    'CreatorProfile',
    'CollaborationOpportunity',
    'PartnershipMatch',
    'CollaborationMetrics',
    'NetworkAnalysis',
    'PartnershipRecommendation',
    
    # Brand Safety
    'ContentComplianceEngine',
    'BrandSafetyAnalyzer',
    'ComplianceCheck',
    'SafetyAnalysis',
    'BrandCompatibility',
    'RegulatoryCompliance',
    'ContentModeration',
    'SafetyReport',
    
    # Performance Tracking
    'MetricsCollector',
    'PerformanceAnalyzer',
    'PerformanceTracker',
    'MetricType',
    'TimeFrame',
    'PerformanceCategory',
    'TrendDirection',
    'MetricDataPoint',
    'PerformanceTrend',
    'ContentPerformanceMetrics',
    'PlatformPerformance',
    'PerformanceBenchmark',
    'PerformanceInsight',
    'PerformanceReport',
    
    # Creative Assistant
    'ContentIdeationEngine',
    'CreativeAssistant',
    'ContentType',
    'CreativeStyle',
    'IdeationType',
    'CreativityLevel',
    'ContentIdea',
    'CreativeTemplate',
    'ContentScript',
    'VisualConcept',
    'AudioConcept',
    'CreativeBrief'
]

from .content_optimizer import ContentOptimizer, OptimizationEngine
from .platform_recommendations import PlatformRecommendationEngine, ContentStrategyAnalyzer
from .monetization_guidance import MonetizationGuidanceEngine, RevenueOptimizer
from .trend_analyzer import TrendAnalyzer, ContentTrendEngine
from .audience_insights import AudienceInsightEngine, EngagementAnalyzer
from .content_scheduler import ContentScheduler, PublishingOptimizer
from .collaboration_finder import CollaborationFinder, InfluencerMatchingEngine
from .brand_safety import BrandSafetyAnalyzer, ContentComplianceEngine
from .performance_tracker import PerformanceTracker, MetricsCollector
from .creative_assistant import CreativeAssistant, ContentIdeationEngine

__all__ = [
    # Content Optimization
    'ContentOptimizer',
    'OptimizationEngine',
    
    # Platform Strategies
    'PlatformRecommendationEngine',
    'ContentStrategyAnalyzer',
    
    # Monetization
    'MonetizationGuidanceEngine',
    'RevenueOptimizer',
    
    # Analytics & Trends
    'TrendAnalyzer',
    'ContentTrendEngine',
    'AudienceInsightEngine',
    'EngagementAnalyzer',
    
    # Scheduling & Optimization
    'ContentScheduler',
    'PublishingOptimizer',
    
    # Collaboration
    'CollaborationFinder',
    'InfluencerMatchingEngine',
    
    # Safety & Compliance
    'BrandSafetyAnalyzer',
    'ContentComplianceEngine',
    
    # Performance & Tracking
    'PerformanceTracker',
    'MetricsCollector',
    
    # Creative Tools
    'CreativeAssistant',
    'ContentIdeationEngine',
    
    # Central Orchestrator
    'ContentGuidanceOrchestrator',
    'ContentGuidanceRequest', 
    'ContentGuidanceResponse',
    'ContentGuidanceServiceType',
    'content_guidance_orchestrator',
    'get_comprehensive_content_guidance',
    'get_specific_content_guidance'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
