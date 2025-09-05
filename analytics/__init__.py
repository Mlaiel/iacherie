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
    UserBehaviorAnalyzer
)
from .creator_performance_engine import (
    CreatorPerformanceEngine,
    CreatorMetrics,
    CreatorType,
    ContentFormat
)
from .ai_processing_metrics import (
    AIProcessingMetricsEngine,
    AIProcessingMetrics,
    AITaskType,
    ProcessingStatus
)
from .content_protection_analytics import (
    ContentProtectionAnalytics,
    ProtectionAnalytics,
    ViolationEvent,
    ProtectionType
)
from .collaboration_intelligence import (
    CollaborationIntelligence,
    CollaborationAnalytics,
    MatchingScore,
    CollaborationType
)
from .gamification_metrics import (
    GamificationAnalytics,
    GamificationMetrics,
    GamificationElement,
    EngagementAction
)

__all__ = [
    # Core Analytics
    "RevenueTracker",
    "PerformanceAnalyzer",
    "BusinessIntelligenceManager",
    "ContentPerformanceAnalyzer", 
    "PredictiveAnalyticsEngine",
    "UserBehaviorAnalyzer",
    
    # Creator Performance
    "CreatorPerformanceEngine",
    "CreatorMetrics",
    "CreatorType",
    "ContentFormat",
    
    # AI Processing
    "AIProcessingMetricsEngine",
    "AIProcessingMetrics",
    "AITaskType",
    "ProcessingStatus",
    
    # Content Protection
    "ContentProtectionAnalytics",
    "ProtectionAnalytics",
    "ViolationEvent",
    "ProtectionType",
    
    # Collaboration Intelligence
    "CollaborationIntelligence",
    "CollaborationAnalytics",
    "MatchingScore",
    "CollaborationType",
    
    # Gamification
    "GamificationAnalytics",
    "GamificationMetrics",
    "GamificationElement",
    "EngagementAction"
]