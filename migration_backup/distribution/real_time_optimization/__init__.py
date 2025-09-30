"""Real-Time Optimization Engine

Real-time performance optimization and adaptive adjustment system for the Ainflue platform.
Continuously monitors and optimizes content performance in real-time using AI-powered
adaptive algorithms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .live_performance_monitor import LivePerformanceMonitor, PerformanceMetrics
from .adaptive_optimizer import AdaptiveOptimizer, AdaptiveStrategy
from .emergency_response import EmergencyResponse, ResponseProtocol
from .trend_surfing_engine import TrendSurfingEngine, SurfingStrategy
from .momentum_capitalizer import MomentumCapitalizer, CapitalizationStrategy
from .real_time_ab_tester import RealTimeABTester, ABTestResults
from .instant_feedback_processor import InstantFeedbackProcessor, FeedbackAnalysis
from .dynamic_content_optimizer import DynamicContentOptimizer, ContentAdjustments

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "LivePerformanceMonitor", "PerformanceMetrics", "AdaptiveOptimizer", "AdaptiveStrategy",
    "EmergencyResponse", "ResponseProtocol", "TrendSurfingEngine", "SurfingStrategy",
    "MomentumCapitalizer", "CapitalizationStrategy", "RealTimeABTester", "ABTestResults",
    "InstantFeedbackProcessor", "FeedbackAnalysis", "DynamicContentOptimizer", "ContentAdjustments"
]