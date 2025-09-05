"""Analytics Module
Revenue tracking and performance analytics for the Ainflue platform.

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

__all__ = [
    "RevenueTracker",
    "PerformanceAnalyzer",
    "BusinessIntelligenceManager",
    "ContentPerformanceAnalyzer", 
    "PredictiveAnalyticsEngine",
    "UserBehaviorAnalyzer"
]