"""Creator Collaboration Hub

Advanced creator collaboration and partnership management system for the Ainflue platform.
Facilitates collaborations, cross-promotions, and partnership opportunities between creators
using AI-powered matching and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .collaboration_orchestrator import CollaborationOrchestrator, CollaborationPlan
from .cross_creator_amplifier import CrossCreatorAmplifier, AmplificationPlan
from .collaboration_matcher import CollaborationMatcher, MatchingResults
from .joint_campaign_manager import JointCampaignManager, CampaignStrategy
from .creator_network_builder import CreatorNetworkBuilder, NetworkStrategy
from .collaboration_analytics import CollaborationAnalytics, CollaborationMetrics
from .partnership_optimizer import PartnershipOptimizer, PartnershipStrategy
from .revenue_sharing_calculator import RevenueSharingCalculator, SharingModel

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    "CollaborationOrchestrator", "CollaborationPlan", "CrossCreatorAmplifier", "AmplificationPlan",
    "CollaborationMatcher", "MatchingResults", "JointCampaignManager", "CampaignStrategy",
    "CreatorNetworkBuilder", "NetworkStrategy", "CollaborationAnalytics", "CollaborationMetrics",
    "PartnershipOptimizer", "PartnershipStrategy", "RevenueSharingCalculator", "SharingModel"
]