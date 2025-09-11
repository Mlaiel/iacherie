"""Platform Optimization Engine

Platform-specific optimization system for maximizing performance across all social media
platforms. Adapts content and strategies to each platform's unique algorithms and features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .platform_analyzer import PlatformAnalyzer, PlatformMetrics
from .algorithm_tracker import AlgorithmTracker, AlgorithmChange
from .feature_optimizer import FeatureOptimizer, PlatformFeature
from .policy_monitor import PolicyMonitor, PolicyUpdate
from .trending_tracker import TrendingTracker, TrendingItem
from .creator_fund_optimizer import CreatorFundOptimizer, OptimizationStrategy
from .monetization_maximizer import MonetizationMaximizer, RevenueStrategy
from .competition_analyzer import CompetitionAnalyzer, CompetitiveInsights

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "PlatformAnalyzer", "PlatformMetrics", "AlgorithmTracker", "AlgorithmChange",
    "FeatureOptimizer", "PlatformFeature", "PolicyMonitor", "PolicyUpdate",
    "TrendingTracker", "TrendingItem", "CreatorFundOptimizer", "OptimizationStrategy",
    "MonetizationMaximizer", "RevenueStrategy", "CompetitionAnalyzer", "CompetitiveInsights"
]