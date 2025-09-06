"""Analytics Module
Advanced analytics and business intelligence for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .revenue_tracker import RevenueTracker
from .performance_analyzer import PerformanceAnalyzer
from .business_intelligence import (
    BusinessIntelligenceManager,
    ContentPerformanceAnalyzer,
    PredictiveAnalyticsEngine,
    UserBehaviorAnalyzer,
    GlobalBusinessIntelligenceEcosystem
)
from .creator_performance_engine import (
    CreatorPerformanceEngine,
    CreatorMetrics,
    CreatorType,
    ContentFormat,
    GlobalCreatorPerformanceIntelligence
)
from .ai_processing_metrics import (
    AIProcessingMetricsEngine,
    AIProcessingMetrics,
    AITaskType,
    ProcessingStatus,
    QuantumAIProcessingIntelligence
)
from .content_protection_analytics import (
    ContentProtectionAnalytics,
    ProtectionAnalytics,
    ViolationEvent,
    ProtectionType,
    QuantumContentProtectionIntelligence
)
from .collaboration_intelligence import (
    CollaborationIntelligence,
    CollaborationAnalytics,
    MatchingScore,
    CollaborationType,
    AdvancedCollaborationIntelligenceEcosystem
)
from .gamification_metrics import (
    GamificationAnalytics,
    GamificationMetrics,
    GamificationElement,
    EngagementAction
)
from .seo_intelligence_engine import (
    SEOIntelligenceEngine,
    SEOIntelligenceMetrics,
    SEOPlatform,
    ContentType as SEOContentType
)
from .distribution_intelligence import (
    DistributionIntelligenceEngine,
    DistributionIntelligence,
    DistributionPlatform,
    ContentFormat as DistributionContentFormat
)
from .security_intelligence import (
    SecurityIntelligenceEngine,
    SecurityMetrics,
    ThreatEvent,
    SecurityEventType
)
from .predictive_intelligence import (
    PredictiveIntelligenceEngine,
    PredictionResult,
    TrendAnalysis,
    PredictionType
)

__all__ = [
    # Core Analytics
    "RevenueTracker",
    "PerformanceAnalyzer",
    "BusinessIntelligenceManager",
    "ContentPerformanceAnalyzer", 
    "PredictiveAnalyticsEngine",
    "UserBehaviorAnalyzer",
    "GlobalBusinessIntelligenceEcosystem",
    
    # Creator Performance
    "CreatorPerformanceEngine",
    "CreatorMetrics",
    "CreatorType",
    "ContentFormat",
    "GlobalCreatorPerformanceIntelligence",
    
    # AI Processing
    "AIProcessingMetricsEngine",
    "AIProcessingMetrics",
    "AITaskType",
    "ProcessingStatus",
    "QuantumAIProcessingIntelligence",
    
    # Content Protection
    "ContentProtectionAnalytics",
    "ProtectionAnalytics",
    "ViolationEvent",
    "ProtectionType",
    "QuantumContentProtectionIntelligence",
    
    # Collaboration Intelligence
    "CollaborationIntelligence",
    "CollaborationAnalytics",
    "MatchingScore",
    "CollaborationType",
    "AdvancedCollaborationIntelligenceEcosystem",
    
    # Gamification
    "GamificationAnalytics",
    "GamificationMetrics",
    "GamificationElement",
    "EngagementAction",
    
    # SEO Intelligence
    "SEOIntelligenceEngine",
    "SEOIntelligenceMetrics",
    "SEOPlatform",
    "SEOContentType",
    
    # Distribution Intelligence
    "DistributionIntelligenceEngine",
    "DistributionIntelligence",
    "DistributionPlatform",
    "DistributionContentFormat",
    
    # Security Intelligence
    "SecurityIntelligenceEngine",
    "SecurityMetrics",
    "ThreatEvent",
    "SecurityEventType",
    
    # Predictive Intelligence
    "PredictiveIntelligenceEngine",
    "PredictionResult",
    "TrendAnalysis",
    "PredictionType"
]