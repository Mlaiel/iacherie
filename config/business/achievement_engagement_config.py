"""
Achievement Engagement Configuration - Enterprise Configuration Management
Enterprise configuration for achievement management and engagement systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        class Config:
    """Config: class implementation"""
            env_prefix = ""
            extra = "allow"
    def Field(**kwargs) -> None:
        return kwargs.get('default_factory', kwargs.get('default'))()


class AchievementCategory(str, Enum):
    """Achievement categories"""
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration" 
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"
    COMMUNITY = "community"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"


class AchievementType(str, Enum):
    """Achievement types"""
    MILESTONE_BASED = "milestone_based"
    PROGRESS_BASED = "progress_based"
    TIME_BASED = "time_based"
    SKILL_BASED = "skill_based"
    SOCIAL_BASED = "social_based"
    RARE_EVENT = "rare_event"


@dataclass
class AchievementConfiguration:
    """Achievement configuration"""
    category: AchievementCategory
    achievement_type: AchievementType
    name: str
    description: str
    criteria: Dict[str, Any]
    rewards: List[str]
    points_value: int
    rarity: str
    hidden: bool
    repeatable: bool
    prerequisites: List[str]


class AchievementEngagementSettings(BaseSettings):
    """Achievement engagement configuration settings"""
    
    # Achievement Definitions
    achievements: Dict[str, AchievementConfiguration] = Field(
        default_factory=lambda: {
            "first_upload": AchievementConfiguration(
                category=AchievementCategory.CONTENT_CREATION,
                achievement_type=AchievementType.MILESTONE_BASED,
                name="First Steps",
                description="Upload your first piece of content",
                criteria={"content_uploads": 1},
                rewards=["welcome_badge", "bonus_points_100"],
                points_value=100,
                rarity="common",
                hidden=False,
                repeatable=False,
                prerequisites=[]
            ),
            "viral_hit": AchievementConfiguration(
                category=AchievementCategory.ENGAGEMENT,
                achievement_type=AchievementType.MILESTONE_BASED,
                name="Viral Sensation",
                description="Achieve 1 million views on a single piece of content",
                criteria={"single_content_views": 1000000},
                rewards=["viral_badge", "premium_access_30days", "bonus_points_5000"],
                points_value=5000,
                rarity="legendary",
                hidden=False,
                repeatable=True,
                prerequisites=["content_creator_verified"]
            ),
            "collaboration_master": AchievementConfiguration(
                category=AchievementCategory.COLLABORATION,
                achievement_type=AchievementType.PROGRESS_BASED,
                name="Collaboration Master",
                description="Complete 50 successful collaborations",
                criteria={"successful_collaborations": 50},
                rewards=["collaboration_expert_badge", "featured_profile", "bonus_points_2500"],
                points_value=2500,
                rarity="epic",
                hidden=False,
                repeatable=False,
                prerequisites=["verified_creator"]
            ),
            "community_leader": AchievementConfiguration(
                category=AchievementCategory.COMMUNITY,
                achievement_type=AchievementType.SOCIAL_BASED,
                name="Community Leader",
                description="Help 100 other creators through mentoring",
                criteria={"mentored_creators": 100, "positive_feedback_rate": 0.95},
                rewards=["mentor_badge", "community_recognition", "bonus_points_3000"],
                points_value=3000,
                rarity="epic",
                hidden=False,
                repeatable=False,
                prerequisites=["established_creator"]
            ),
            "revenue_milestone_1k": AchievementConfiguration(
                category=AchievementCategory.MONETIZATION,
                achievement_type=AchievementType.MILESTONE_BASED,
                name="First $1K",
                description="Earn your first $1,000 through the platform",
                criteria={"total_earnings_usd": 1000},
                rewards=["entrepreneur_badge", "revenue_sharing_boost", "bonus_points_1000"],
                points_value=1000,
                rarity="rare",
                hidden=False,
                repeatable=False,
                prerequisites=["monetization_enabled"]
            )
        }
    )
    
    # Engagement Mechanics
    engagement_mechanics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "progress_tracking": {
                "enabled": True,
                "real_time_updates": True,
                "visual_progress_bars": True,
                "milestone_notifications": True,
                "achievement_previews": True
            },
            "social_features": {
                "achievement_sharing": True,
                "leaderboards": True,
                "peer_comparison": True,
                "achievement_reactions": True,
                "congratulations_system": True
            },
            "personalization": {
                "recommended_achievements": True,
                "difficulty_adjustment": True,
                "interest_based_suggestions": True,
                "adaptive_challenges": True,
                "personal_goals": True
            },
            "retention_features": {
                "streak_tracking": True,
                "comeback_achievements": True,
                "seasonal_events": True,
                "limited_time_achievements": True,
                "surprise_rewards": True
            }
        }
    )
    
    # Notification System
    notification_system: Dict[str, Any] = Field(
        default_factory=lambda: {
            "achievement_unlocked": True,
            "progress_milestones": True,
            "near_completion_alerts": True,
            "social_achievements": True,
            "seasonal_reminders": True,
            "personalized_suggestions": True,
            "celebration_animations": True,
            "email_summaries": True
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "ACHIEVEMENT_ENGAGEMENT_"
        case_sensitive = False
        extra = "allow"
    
    def validate_configuration(self) -> List[str]:
        """Validate achievement configuration"""
        errors = []
        for achievement_name, achievement in self.achievements.items():
            if not achievement.criteria:
                errors.append(f"Achievement '{achievement_name}' has no criteria")
            if achievement.points_value < 0:
                errors.append(f"Achievement '{achievement_name}' has negative points")
        return errors


# Global achievement engagement settings instance  
achievement_engagement_settings = AchievementEngagementSettings()

__all__ = [
    "AchievementEngagementSettings",
    "achievement_engagement_settings", 
    "AchievementCategory",
    "AchievementType",
    "AchievementConfiguration"
]