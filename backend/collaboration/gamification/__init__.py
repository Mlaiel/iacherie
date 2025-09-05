"""Gamification Module - Advanced Engagement and Motivation System
================================================================

Comprehensive gamification system providing:
- Multi-dimensional achievement system
- Dynamic points and level management
- Interactive badges and rewards
- Competitive leaderboards
- Personalized challenges
- Social engagement features

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

from .achievement_system import (
    AchievementSystem,
    Achievement,
    AchievementType,
    AchievementTier,
    AchievementProgress,
    AchievementRule
)

from .points_calculator import (
    PointsCalculator,
    PointsTransaction,
    PointsCategory,
    PointsMultiplier,
    PointsBonus,
    PointsBalance
)

from .level_manager import (
    LevelManager,
    UserLevel,
    LevelTier,
    LevelRequirement,
    LevelReward,
    LevelProgression
)

from .badge_engine import (
    BadgeEngine,
    Badge,
    BadgeType,
    BadgeRarity,
    BadgeCollection,
    BadgeCondition
)

from .leaderboard_system import (
    LeaderboardSystem,
    Leaderboard,
    LeaderboardType,
    LeaderboardEntry,
    SeasonalRanking,
    CompetitionBoard
)

from .challenge_creator import (
    ChallengeCreator,
    Challenge,
    ChallengeType,
    ChallengeDifficulty,
    ChallengeReward,
    PersonalizedChallenge
)

from .reward_distributor import (
    RewardDistributor,
    Reward,
    RewardType,
    RewardTier,
    RewardSchedule,
    RewardClaim
)

from .streak_tracker import (
    StreakTracker,
    StreakRecord,
    StreakType,
    StreakMilestone,
    StreakBonus,
    ActivityStreak
)

from .competition_manager import (
    CompetitionManager,
    Competition,
    CompetitionType,
    CompetitionRules,
    CompetitionReward,
    TeamCompetition
)

from .social_rewards import (
    SocialRewardSystem,
    SocialReward,
    SocialAction,
    ViralBonus,
    CommunityReward,
    CollaborationBonus
)

from .engagement_booster import (
    EngagementBooster,
    EngagementMetric,
    BoostStrategy,
    EngagementGoal,
    MotivationTrigger,
    RetentionBooster
)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Advanced Gamification and Engagement System"

# Export all public classes and functions
__all__ = [
    # Achievement System
    "AchievementSystem",
    "Achievement",
    "AchievementType",
    "AchievementTier",
    "AchievementProgress",
    "AchievementRule",
    
    # Points Calculator
    "PointsCalculator",
    "PointsTransaction",
    "PointsCategory",
    "PointsMultiplier",
    "PointsBonus",
    "PointsBalance",
    
    # Level Manager
    "LevelManager",
    "UserLevel",
    "LevelTier",
    "LevelRequirement",
    "LevelReward",
    "LevelProgression",
    
    # Badge Engine
    "BadgeEngine",
    "Badge",
    "BadgeType",
    "BadgeRarity",
    "BadgeCollection",
    "BadgeCondition",
    
    # Leaderboard System
    "LeaderboardSystem",
    "Leaderboard",
    "LeaderboardType",
    "LeaderboardEntry",
    "SeasonalRanking",
    "CompetitionBoard",
    
    # Challenge Creator
    "ChallengeCreator",
    "Challenge",
    "ChallengeType",
    "ChallengeDifficulty",
    "ChallengeReward",
    "PersonalizedChallenge",
    
    # Reward Distributor
    "RewardDistributor",
    "Reward",
    "RewardType",
    "RewardTier",
    "RewardSchedule",
    "RewardClaim",
    
    # Streak Tracker
    "StreakTracker",
    "StreakRecord",
    "StreakType",
    "StreakMilestone",
    "StreakBonus",
    "ActivityStreak",
    
    # Competition Manager
    "CompetitionManager",
    "Competition",
    "CompetitionType",
    "CompetitionRules",
    "CompetitionReward",
    "TeamCompetition",
    
    # Social Rewards
    "SocialRewardSystem",
    "SocialReward",
    "SocialAction",
    "ViralBonus",
    "CommunityReward",
    "CollaborationBonus",
    
    # Engagement Booster
    "EngagementBooster",
    "EngagementMetric",
    "BoostStrategy",
    "EngagementGoal",
    "MotivationTrigger",
    "RetentionBooster"
]

# Module initialization
import logging
logger = logging.getLogger(__name__)
logger.info(f"🎮 Gamification Module v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("🏆 Advanced engagement and motivation system initialized")