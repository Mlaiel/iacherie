"""Advanced Gamification Services - Enterprise Gaming System
========================================================

Comprehensive gamification ecosystem providing achievement tracking, reward systems,
and challenge management for content creators with advanced analytics and
comprehensive engagement features.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification/__init__.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Achievement/Ranking/Rewards/Challenges/Badges → Distribution → Monetization → Analytics
"""

import logging
from typing import Dict, List, Optional, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."

# Achievements module imports
try:
    from .achievements.achievement_engine import AchievementEngine, get_achievement_engine
    from .achievements.badge_system import BadgeSystem, get_badge_system
    from .achievements.leaderboards import Leaderboards, get_leaderboards
    from .achievements.social_proof_engine import SocialProofEngine, get_social_proof_engine
    achievements_available = True
    logger.info("✅ Achievements module loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Achievements module not available: {e}")
    achievements_available = False

# Rewards module imports
try:
    from .rewards.point_system import PointSystem, get_point_system
    from .rewards.reward_distributor import RewardDistributor, get_reward_distributor
    from .rewards.tier_manager import TierManager, get_tier_manager
    rewards_available = True
    logger.info("✅ Rewards module loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Rewards module not available: {e}")
    rewards_available = False

# Challenges module imports
try:
    from .challenges.challenge_creator import ChallengeCreator, get_challenge_creator
    from .challenges.competition_engine import CompetitionEngine, get_competition_engine
    challenges_available = True
    logger.info("✅ Challenges module loaded successfully")
except ImportError as e:
    logger.warning(f"❌ Challenges module not available: {e}")
    challenges_available = False


class GamificationServices:
    """
    Central orchestrator for the complete gamification services ecosystem.
    
    Coordinates between all gamification modules to provide a unified
    gaming experience for content creators.
    """
    
    def __init__(self):
        """Initialize the gamification services orchestrator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize services
        self.achievement_engine = None
        self.badge_system = None
        self.social_proof_engine = None
        self.point_system = None
        self.reward_distributor = None
        self.tier_manager = None
        self.challenge_creator = None
        self.competition_engine = None
        
        self.logger.info("GamificationServices orchestrator initialized")
    
    async def initialize(self) -> bool:
        """Initialize all gamification services."""
        try:
            # Initialize achievements
            if achievements_available:
                self.achievement_engine = get_achievement_engine()
                self.badge_system = get_badge_system()
                self.social_proof_engine = get_social_proof_engine()
            
            # Initialize rewards
            if rewards_available:
                self.point_system = get_point_system()
                self.reward_distributor = get_reward_distributor()
                self.tier_manager = get_tier_manager()
            
            # Initialize challenges
            if challenges_available:
                self.challenge_creator = get_challenge_creator()
                self.competition_engine = get_competition_engine()
            
            self.logger.info("✅ All gamification services initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize gamification services: {e}")
            return False
    
    @property
    def achievements(self):
        """Access to achievements module."""
        return self.achievement_engine
    
    @property
    def rewards(self):
        """Access to rewards module."""
        return self.reward_distributor
    
    @property
    def challenges(self):
        """Access to challenges module."""
        return self.challenge_creator
    
    async def process_user_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a user action across all gamification services."""
        results = {
            "user_id": user_id,
            "action_type": action_type,
            "achievements": [],
            "rewards": [],
            "challenges": [],
            "social_proofs": [],
            "tier_changes": []
        }
        
        try:
            # Process achievements
            if self.achievement_engine and achievements_available:
                achievement_results = await self.achievement_engine.process_action(
                    user_id, action_type, action_data
                )
                results["achievements"] = achievement_results
            
            # Process social proof (NEW)
            if self.social_proof_engine and achievements_available:
                social_proof_results = await self.social_proof_engine.process_user_action(
                    user_id, action_type, action_data
                )
                results["social_proofs"] = social_proof_results
            
            # Process rewards
            if self.reward_distributor and rewards_available:
                reward_results = await self.reward_distributor.process_action(
                    user_id, action_type, action_data
                )
                results["rewards"] = reward_results
            
            # Process challenges
            if self.challenge_creator and challenges_available:
                challenge_results = await self.challenge_creator.process_action(
                    user_id, action_type, action_data
                )
                results["challenges"] = challenge_results
            
            # Process tier changes
            if self.tier_manager and rewards_available:
                tier_results = await self.tier_manager.check_tier_progression(
                    user_id, user_profile
                )
                results["tier_changes"] = tier_results
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing user action: {e}")
            return results
    
    async def get_user_gamification_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification summary for a user."""
        summary = {
            "user_id": user_id,
            "achievements": {},
            "rewards": {},
            "challenges": {},
            "social_proofs": {},
            "tier": {}
        }
        
        try:
            # Get achievement summary
            if self.achievement_engine and achievements_available:
                summary["achievements"] = await self.achievement_engine.get_user_summary(user_id)
            
            # Get social proof summary (NEW)
            if self.social_proof_engine and achievements_available:
                summary["social_proofs"] = await self.social_proof_engine.get_user_social_proofs(user_id)
            
            # Get rewards summary
            if self.point_system and rewards_available:
                summary["rewards"] = await self.point_system.get_user_summary(user_id)
            
            # Get challenges summary
            if self.challenge_creator and challenges_available:
                summary["challenges"] = await self.challenge_creator.get_user_summary(user_id)
            
            # Get tier summary
            if self.tier_manager and rewards_available:
                summary["tier"] = await self.tier_manager.get_user_tier_info(user_id)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting user gamification summary: {e}")
            return summary


# Export main classes and functions
__all__ = [
    # Core orchestrator
    "GamificationServices",
    
    # Achievement services
    "AchievementEngine",
    "BadgeSystem", 
    "Leaderboards",
    "SocialProofEngine",
    "get_achievement_engine",
    "get_badge_system",
    "get_leaderboards",
    "get_social_proof_engine",
    
    # Reward services
    "PointSystem",
    "RewardDistributor",
    "TierManager",
    "get_point_system", 
    "get_reward_distributor",
    "get_tier_manager",
    
    # Challenge services
    "ChallengeCreator",
    "CompetitionEngine",
    "get_challenge_creator",
    "get_competition_engine",
    
    # Module availability flags
    "achievements_available",
    "rewards_available", 
    "challenges_available"
]

# Module initialization
logger.info(f"IA Influencer Agent Gamification Services v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")

# Availability summary
available_count = sum([achievements_available, rewards_available, challenges_available])
logger.info(f"🎮 Gamification services loaded: {available_count}/3 modules available")