"""Analytics Module - IA Influencer Agent + Content Protection Platform

Enterprise-grade analytics system for multi-format content creators
(musicians, bloggers, photographers, influencers, comedians) with AI-powered insights.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert
Architecture: Enterprise-grade, microservices-ready, production-optimized

 INTELLECTUAL PROPERTY WARNING 
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Violations will be prosecuted under international copyright law.

Specialties of Project Team:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
# Import all analytics modules
from .performance_tracker import (
    PerformanceTracker, 
    MetricsCollector,
    ContentPerformance,
    MetricsHistory,
    PerformanceAlerts,
    ContentFormat,
    PlatformType,
    MetricType,
    MetricSnapshot
)

from .engagement_analyzer import (
    EngagementAnalyzer,
    AudienceInsights,
    EngagementMetric,
    EngagementInsight,
    EngagementType,
    SentimentType
)

from .content_insights import (
    ContentInsights,
    TrendAnalyzer,
    ContentInsightModel,
    ContentTrend,
    ContentOptimizationRecommendation,
    ContentCategory,
    TrendStatus,
    ContentElement
)

from .predictive_analytics import (
    PredictiveAnalytics,
    ForecastEngine,
    PredictionResult,
    ModelPerformance,
    PredictionType,
    TimeHorizon,
    ModelType
)

from .recommendation_engine import (
    RecommendationEngine,
    ContentOptimizer,
    Recommendation,
    RecommendationResult,
    RecommendationType,
    RecommendationPriority,
    RecommendationCategory
)

from .revenue_analytics import (
    RevenueAnalytics,
    RevenueOptimizationExperiment, 
    RevenueAnalyticsManager,
    RevenueTimeframe,
    RevenueSource,
    PredictionModel,
    RevenueOptimizationStrategy,
    RevenueInsight,
    RevenueForecast
)

from .content_performance_analytics import (
    ContentPerformanceAnalytics,
    ContentOptimizationRecommendation as ContentPerfOptimizationRec,
    ContentPerformanceManager,
    ContentType,
    Platform, 
    EngagementMetric as ContentEngagementMetric,
    OptimizationCategory,
    ContentInsight
)

from .audience_intelligence import (
    AudienceIntelligence,
    AudienceSegmentDetails,
    AudienceIntelligenceManager,
    AudienceSegment,
    AudienceAction,
    EngagementLevel, 
    PredictionType as AudiencePredictionType,
    AudienceInsight
)

# New advanced analytics modules
from .cross_platform_analytics import (
    CrossPlatformAnalyticsEngine,
    CrossPlatformAnalytics,
    PlatformInsights,
    PlatformMetrics,
    PlatformType,
    ContentFormat as CrossPlatformContentFormat,
    MetricCategory
)

from .ai_content_optimizer import (
    AIContentOptimizer,
    OptimizationRecommendation,
    ContentOptimizationHistory,
    OptimizationRecommendationModel,
    OptimizationType,
    ContentElement,
    OptimizationPriority
)

from .real_time_dashboard import (
    RealTimeDashboard,
    AlertManager,
    DashboardAlert,
    RealTimeMetric,
    DashboardSession,
    DashboardMetrics,
    DashboardWidget,
    MetricTimeframe,
    AlertSeverity
)

from .competitive_intelligence import (
    CompetitiveIntelligenceEngine,
    CompetitorProfile,
    CompetitorAnalysis,
    CompetitorInsight,
    MarketIntelligence,
    CompetitorTier,
    AnalysisType,
    MarketPosition
)

# Define comprehensive exports
__all__ = [
    # Performance Tracking
    "PerformanceTracker",
    "MetricsCollector",
    "ContentPerformance",
    "MetricsHistory",
    "PerformanceAlerts",
    "ContentFormat",
    "PlatformType",
    "MetricType",
    "MetricSnapshot",
    
    # Engagement Analytics
    "EngagementAnalyzer",
    "AudienceInsights",
    "EngagementMetric",
    "EngagementInsight",
    "EngagementType",
    "SentimentType",
    
    # Content Insights
    "ContentInsights",
    "TrendAnalyzer",
    "ContentInsightModel",
    "ContentTrend",
    "ContentOptimizationRecommendation",
    "ContentCategory",
    "TrendStatus",
    "ContentElement",
    
    # Predictive Analytics
    "PredictiveAnalytics",
    "ForecastEngine",
    "PredictionResult",
    "ModelPerformance",
    "PredictionType",
    "ModelType",
    "TrainingStatus",
    
    # Content Performance Analytics
    "ContentPerformanceAnalytics",
    "ContentMetrics",
    "PerformanceComparison",
    "ContentPerformanceInsight",
    "PerformanceMetricType",
    "ComparisonPeriod",
    "PerformanceCategory",
    
    # Recommendation Engine
    "RecommendationEngine",
    "ContentRecommendation",
    "RecommendationType",
    "RecommendationScore",
    "UserPreference",
    "RecommendationFeedback",
    "AlgorithmType",
    
    # Revenue Analytics
    "RevenueAnalytics",
    "RevenueStream",
    "RevenueProjection",
    "MonetizationOpportunity",
    "RevenueMetric",
    "PaymentProvider",
    "RevenueCategory",
    
    # Audience Intelligence
    "AudienceIntelligence",
    "AudienceSegmentDetails",
    "AudienceIntelligenceManager",
    "AudienceSegment",
    "AudienceAction",
    "EngagementLevel",
    "AudiencePredictionType",
    "AudienceInsight",
    
    # Cross-Platform Analytics
    "CrossPlatformAnalyticsEngine",
    "CrossPlatformAnalytics",
    "PlatformInsights",
    "PlatformMetrics",
    "CrossPlatformContentFormat",
    "MetricCategory",
    
    # AI Content Optimizer
    "AIContentOptimizer",
    "OptimizationRecommendation", 
    "ContentOptimizationHistory",
    "OptimizationRecommendationModel",
    "OptimizationType",
    "OptimizationPriority",
    
    # Real-Time Dashboard
    "RealTimeDashboard",
    "AlertManager",
    "DashboardAlert",
    "RealTimeMetric",
    "DashboardSession",
    "DashboardMetrics",
    "DashboardWidget",
    "MetricTimeframe",
    "AlertSeverity",
    
    # Competitive Intelligence
    "CompetitiveIntelligenceEngine",
    "CompetitorProfile",
    "CompetitorAnalysis",
    "CompetitorInsight",
    "MarketIntelligence",
    "CompetitorTier",
    "AnalysisType",
    "MarketPosition"
]
    "PredictionType",
    "TimeHorizon",
    "ModelType",
    
    # Recommendation Engine
    "RecommendationEngine",
    "ContentOptimizer",
    "Recommendation",
    "RecommendationResult",
    "RecommendationType",
    "RecommendationPriority",
    "RecommendationCategory",
    
    # Revenue Analytics
    "RevenueAnalytics",
    "RevenueOptimizationExperiment", 
    "RevenueAnalyticsManager",
    "RevenueTimeframe",
    "RevenueSource",
    "PredictionModel",
    "RevenueOptimizationStrategy",
    "RevenueInsight",
    "RevenueForecast",
    
    # Content Performance Analytics
    "ContentPerformanceAnalytics",
    "ContentPerfOptimizationRec",
    "ContentPerformanceManager",
    "ContentType",
    "Platform", 
    "ContentEngagementMetric",
    "OptimizationCategory",
    "ContentInsight",
    
    # Audience Intelligence
    "AudienceIntelligence",
    "AudienceSegmentDetails",
    "AudienceIntelligenceManager",
    "AudienceSegment",
    "AudienceAction",
    "EngagementLevel", 
    "AudiencePredictionType",
    "AudienceInsight"
]
