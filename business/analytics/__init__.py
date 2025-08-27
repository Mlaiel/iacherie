"""
Business Analytics Module - IA Influencer Agent Platform
========================================================

Advanced analytics system for multi-format content creators with real-time insights,
predictive modeling, and comprehensive business intelligence for the entertainment industry.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
"""

from .performance_engine import PerformanceAnalyticsEngine
from .audience_intelligence import AudienceIntelligenceSystem
from .revenue_optimizer import RevenueOptimizationEngine
from .content_insights import ContentInsightsAnalyzer
from .predictive_modeling import PredictiveModelingEngine
from .engagement_tracker import EngagementTrackingSystem
from .platform_comparator import PlatformPerformanceComparator
from .trend_detector import TrendDetectionEngine
from .roi_calculator import ROICalculatorEngine
from .dashboard_aggregator import DashboardDataAggregator

__all__ = [
    'PerformanceAnalyticsEngine',
    'AudienceIntelligenceSystem', 
    'RevenueOptimizationEngine',
    'ContentInsightsAnalyzer',
    'PredictiveModelingEngine',
    'EngagementTrackingSystem',
    'PlatformPerformanceComparator',
    'TrendDetectionEngine',
    'ROICalculatorEngine',
    'DashboardDataAggregator'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
