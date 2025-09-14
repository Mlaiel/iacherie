"""
Gamification Business Configuration - Enterprise Configuration Management
Enterprise configuration for gamification business logic and engagement systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        class Config:
    """Config: class implementation"""
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    def Field(**kwargs) -> None:
        return kwargs.get('default_factory', kwargs.get('default'))()
    def validator(field_name) -> None:
        def decorator(func) -> None:
            return func
        return decorator


class RewardType(str, Enum):
    """Reward types for gamification"""
    POINTS = "points"
    BADGES = "badges"
    LEVELS = "levels"
    VIRTUAL_CURRENCY = "virtual_currency"
    REAL_CURRENCY = "real_currency"
    PREMIUM_FEATURES = "premium_features"
    EXCLUSIVE_CONTENT = "exclusive_content"
    RECOGNITION = "recognition"


class ChallengeType(str, Enum):
    """Challenge types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    MILESTONE = "milestone"
    COMMUNITY = "community"
    COMPETITIVE = "competitive"
    COLLABORATIVE = "collaborative"


class LeaderboardType(str, Enum):
    """Leaderboard types"""
    GLOBAL = "global"
    REGIONAL = "regional"
    CATEGORY_SPECIFIC = "category_specific"
    PEER_GROUP = "peer_group"
    SEASONAL = "seasonal"
    ALL_TIME = "all_time"


@dataclass
class RewardConfiguration:
    """Reward configuration"""
    reward_type: RewardType
    name: str
    description: str
    value: Union[int, float, str]
    rarity: str  # common, rare, epic, legendary
    requirements: List[str]
    expiry_days: Optional[int]
    transferable: bool
    stackable: bool


@dataclass
class ChallengeConfiguration:
    """Challenge configuration"""
    challenge_type: ChallengeType
    name: str
    description: str
    objectives: List[str]
    rewards: List[str]
    duration_days: int
    difficulty: str  # easy, medium, hard, expert
    prerequisites: List[str]
    max_participants: Optional[int]
    auto_start: bool


class GamificationBusinessSettings(BaseSettings):
    """Gamification business configuration settings"""
    
    # Reward System Configuration
    rewards: Dict[str, RewardConfiguration] = Field(
        default_factory=lambda: {
            "content_creator_points": RewardConfiguration(
                reward_type=RewardType.POINTS,
                name="Creator Points",
                description="Points earned for creating content",
                value=100,
                rarity="common",
                requirements=["content_upload"],
                expiry_days=None,
                transferable=False,
                stackable=True
            ),
            "viral_content_badge": RewardConfiguration(
                reward_type=RewardType.BADGES,
                name="Viral Content Badge",
                description="Badge for creating viral content",
                value="viral_badge_icon",
                rarity="epic",
                requirements=["content_views_100k", "engagement_rate_10"],
                expiry_days=None,
                transferable=False,
                stackable=False
            ),
            "collaboration_master": RewardConfiguration(
                reward_type=RewardType.BADGES,
                name="Collaboration Master",
                description="Badge for successful collaborations",
                value="collab_master_badge",
                rarity="rare",
                requirements=["successful_collaborations_10"],
                expiry_days=None,
                transferable=False,
                stackable=False
            ),
            "premium_access": RewardConfiguration(
                reward_type=RewardType.PREMIUM_FEATURES,
                name="Premium Feature Access",
                description="Access to premium platform features",
                value="premium_tier_access",
                rarity="legendary",
                requirements=["creator_level_50", "total_points_10000"],
                expiry_days=30,
                transferable=False,
                stackable=False
            )
        }
    )
    
    # Challenge System Configuration
    challenges: Dict[str, ChallengeConfiguration] = Field(
        default_factory=lambda: {
            "daily_upload": ChallengeConfiguration(
                challenge_type=ChallengeType.DAILY,
                name="Daily Content Upload",
                description="Upload content every day for a week",
                objectives=["upload_content_daily_7days"],
                rewards=["content_creator_points", "streak_badge"],
                duration_days=7,
                difficulty="easy",
                prerequisites=[],
                max_participants=None,
                auto_start=True
            ),
            "monthly_collaboration": ChallengeConfiguration(
                challenge_type=ChallengeType.MONTHLY,
                name="Monthly Collaboration Challenge",
                description="Complete 3 collaborations in a month",
                objectives=["complete_collaborations_3"],
                rewards=["collaboration_master", "premium_access"],
                duration_days=30,
                difficulty="medium",
                prerequisites=["profile_verified"],
                max_participants=1000,
                auto_start=True
            ),
            "viral_content_quest": ChallengeConfiguration(
                challenge_type=ChallengeType.MILESTONE,
                name="Viral Content Quest",
                description="Create content that reaches 100K views",
                objectives=["content_views_100k"],
                rewards=["viral_content_badge", "bonus_currency"],
                duration_days=90,
                difficulty="hard",
                prerequisites=["creator_level_20"],
                max_participants=None,
                auto_start=False
            )
        }
    )
    
    # Leaderboard Configuration
    leaderboards: Dict[str, Any] = Field(
        default_factory=lambda: {
            "global_creators": {
                "type": LeaderboardType.GLOBAL,
                "metric": "total_points",
                "update_frequency": "real_time",
                "display_count": 100,
                "reset_period": "monthly",
                "rewards": ["top_creator_badge", "recognition_feature"]
            },
            "regional_engagement": {
                "type": LeaderboardType.REGIONAL,
                "metric": "engagement_score",
                "update_frequency": "hourly",
                "display_count": 50,
                "reset_period": "weekly",
                "rewards": ["regional_champion_badge"]
            },
            "collaboration_leaders": {
                "type": LeaderboardType.CATEGORY_SPECIFIC,
                "metric": "collaboration_score",
                "update_frequency": "daily",
                "display_count": 25,
                "reset_period": "quarterly",
                "rewards": ["collaboration_leader_badge"]
            }
        }
    )
    
    # Engagement Mechanics
    engagement_mechanics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "level_system": {
                "enabled": True,
                "max_level": 100,
                "experience_per_level": 1000,
                "level_up_rewards": True,
                "prestige_system": True
            },
            "achievement_system": {
                "enabled": True,
                "categories": ["content", "collaboration", "engagement", "community"],
                "progression_tracking": True,
                "completion_rewards": True
            },
            "streak_system": {
                "enabled": True,
                "types": ["daily_login", "content_upload", "collaboration"],
                "streak_multipliers": True,
                "streak_recovery": True
            },
            "social_features": {
                "following": True,
                "likes": True,
                "comments": True,
                "shares": True,
                "reactions": True,
                "mentions": True
            }
        }
    )
    
    # Monetization Integration
    monetization_integration: Dict[str, Any] = Field(
        default_factory=lambda: {
            "reward_monetization": True,
            "virtual_currency_exchange": True,
            "premium_reward_tiers": True,
            "sponsored_challenges": True,
            "brand_partnership_rewards": True,
            "creator_fund_integration": True,
            "tip_jar_gamification": True,
            "subscription_perks": True
        }
    )
    
    # Analytics and Tracking
    analytics_tracking: Dict[str, Any] = Field(
        default_factory=lambda: {
            "engagement_analytics": True,
            "reward_effectiveness": True,
            "challenge_completion_rates": True,
            "user_progression_tracking": True,
            "retention_analysis": True,
            "behavioral_insights": True,
            "a_b_testing": True,
            "predictive_modeling": True
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "GAMIFICATION_"
        case_sensitive = False
        extra = "allow"
    
    def validate_configuration(self) -> List[str]:
        """Validate gamification configuration"""
        errors = []
        
        # Validate rewards
        for reward_name, reward in self.rewards.items():
            if not reward.requirements:
                errors.append(f"Reward '{reward_name}' has no requirements")
        
        # Validate challenges
        for challenge_name, challenge in self.challenges.items():
            if not challenge.objectives:
                errors.append(f"Challenge '{challenge_name}' has no objectives")
            if challenge.duration_days <= 0:
                errors.append(f"Challenge '{challenge_name}' has invalid duration")
        
        return errors


# Global gamification settings instance
gamification_business_settings = GamificationBusinessSettings()

__all__ = [
    "GamificationBusinessSettings",
    "gamification_business_settings",
    "RewardType",
    "ChallengeType", 
    "LeaderboardType",
    "RewardConfiguration",
    "ChallengeConfiguration"
]