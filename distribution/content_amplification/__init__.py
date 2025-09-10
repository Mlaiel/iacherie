"""Content Amplification Engine

Advanced content amplification and reach maximization system for the Ainflue platform.
Optimizes organic reach, manages paid boosts, and implements cross-promotion strategies
using AI-powered amplification techniques.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .amplification_engine import AmplificationEngine, AmplificationStrategy
from .boost_optimizer import BoostOptimizer, BoostStrategy
from .organic_reach_maximizer import OrganicReachMaximizer, OrganicStrategy
from .cross_promotion_manager import CrossPromotionManager, PromotionPlan
from .influencer_connector import InfluencerConnector, InfluencerNetwork
from .community_builder import CommunityBuilder, CommunityStrategy
from .engagement_multiplier import EngagementMultiplier, MultiplicationStrategy
from .reach_analytics import ReachAnalytics, ReachMetrics

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "AmplificationEngine", "AmplificationStrategy", "BoostOptimizer", "BoostStrategy",
    "OrganicReachMaximizer", "OrganicStrategy", "CrossPromotionManager", "PromotionPlan",
    "InfluencerConnector", "InfluencerNetwork", "CommunityBuilder", "CommunityStrategy",
    "EngagementMultiplier", "MultiplicationStrategy", "ReachAnalytics", "ReachMetrics"
]