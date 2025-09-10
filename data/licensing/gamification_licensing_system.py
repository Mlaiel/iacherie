"""🎮 Gamification Licensing System - Creator Engagement & Rewards Engine
=====================================================================

Ultra-advanced gamification system for licensing with creator engagement and incentives.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Union, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math

logger = logging.getLogger(__name__)

class CreatorTier(Enum):
    """Creator tier levels in the gamification system."""
    NEWCOMER = "newcomer"
    RISING_STAR = "rising_star"
    ESTABLISHED = "established"
    PROFESSIONAL = "professional"
    ELITE = "elite"
    LEGENDARY = "legendary"
    MASTER = "master"

class AchievementCategory(Enum):
    """Categories of achievements."""
    LICENSING = "licensing"
    REVENUE = "revenue"
    COLLABORATION = "collaboration"
    COMMUNITY = "community"
    INNOVATION = "innovation"
    PLATFORM_MASTERY = "platform_mastery"
    LEGAL_COMPLIANCE = "legal_compliance"
    GLOBAL_REACH = "global_reach"

class RewardType(Enum):
    """Types of rewards in the system."""
    ROYALTY_BONUS = "royalty_bonus"
    PLATFORM_CREDITS = "platform_credits"
    EXCLUSIVE_ACCESS = "exclusive_access"
    FEATURE_UNLOCK = "feature_unlock"
    BADGE = "badge"
    TITLE = "title"
    NFT_REWARD = "nft_reward"
    CASH_BONUS = "cash_bonus"

class ChallengeType(Enum):
    """Types of challenges."""
    INDIVIDUAL = "individual"
    COLLABORATIVE = "collaborative"
    COMMUNITY = "community"
    PLATFORM_SPECIFIC = "platform_specific"
    TIME_LIMITED = "time_limited"
    MILESTONE = "milestone"

@dataclass
class CreatorProfile:
    """Creator profile with gamification data."""
    creator_id: str
    username: str
    email: str
    current_tier: CreatorTier
    experience_points: int
    level: int
    total_revenue: Decimal
    licensing_count: int
    collaboration_count: int
    achievements: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    active_challenges: List[str] = field(default_factory=list)
    completed_challenges: List[str] = field(default_factory=list)
    tier_progress: float = 0.0
    reputation_score: float = 100.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    platform_stats: Dict[str, Any] = field(default_factory=dict)
    social_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Achievement:
    """Achievement definition and tracking."""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    criteria: Dict[str, Any]
    reward_type: RewardType
    reward_value: Union[Decimal, str, Dict[str, Any]]
    xp_bonus: int
    rarity: str
    icon_url: str
    unlock_conditions: List[str]
    is_hidden: bool = False
    is_repeatable: bool = False
    platform_specific: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Badge:
    """Badge representation."""
    badge_id: str
    name: str
    description: str
    design_url: str
    rarity: str
    earned_by: int = 0
    is_animated: bool = False
    unlock_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Challenge:
    """Challenge or competition definition."""
    challenge_id: str
    name: str
    description: str
    challenge_type: ChallengeType
    start_date: datetime
    end_date: datetime
    max_participants: Optional[int]
    entry_requirements: Dict[str, Any]
    objectives: List[Dict[str, Any]]
    rewards: List[Dict[str, Any]]
    leaderboard: List[Dict[str, Any]] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    is_active: bool = True
    prize_pool: Optional[Decimal] = None
    sponsor: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Leaderboard:
    """Leaderboard for competitions and rankings."""
    leaderboard_id: str
    name: str
    category: str
    time_period: str
    entries: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    is_global: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Reward:
    """Reward tracking and distribution."""
    reward_id: str
    creator_id: str
    reward_type: RewardType
    value: Union[Decimal, str, Dict[str, Any]]
    source: str
    earned_at: datetime
    claimed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_claimed: bool = False
    is_expired: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SocialAction:
    """Social action tracking for community features."""
    action_id: str
    creator_id: str
    action_type: str
    target_id: str
    target_type: str
    platform: str
    timestamp: datetime
    impact_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class GamificationLicensingSystem:
    """Advanced Gamification Licensing System with Creator Engagement & Rewards."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Gamification Licensing System."""
        self.config = config or {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.achievements: Dict[str, Achievement] = {}
        self.badges: Dict[str, Badge] = {}
        self.challenges: Dict[str, Challenge] = {}
        self.leaderboards: Dict[str, Leaderboard] = {}
        self.rewards: Dict[str, Reward] = {}
        self.social_actions: List[SocialAction] = []
        
        self._initialize_default_achievements()
        self._initialize_default_badges()
        self._initialize_tier_system()
        self._initialize_leaderboards()
        
        logger.info("Gamification Licensing System initialized")

    def _initialize_default_achievements(self) -> None:
        """Initialize default achievements for the system."""
        achievements = [
            Achievement(
                achievement_id="first_license",
                name="First Steps",
                description="Create your first licensing agreement",
                category=AchievementCategory.LICENSING,
                criteria={"licensing_count": 1},
                reward_type=RewardType.PLATFORM_CREDITS,
                reward_value=Decimal("100"),
                xp_bonus=50,
                rarity="common",
                icon_url="/icons/achievements/first_license.png",
                unlock_conditions=["account_verified"]
            ),
            Achievement(
                achievement_id="licensing_veteran",
                name="Licensing Veteran",
                description="Complete 100 licensing agreements",
                category=AchievementCategory.LICENSING,
                criteria={"licensing_count": 100},
                reward_type=RewardType.ROYALTY_BONUS,
                reward_value=Decimal("5.0"),
                xp_bonus=1000,
                rarity="rare",
                icon_url="/icons/achievements/licensing_veteran.png",
                unlock_conditions=["licensing_count>=10"]
            ),
            Achievement(
                achievement_id="first_thousand",
                name="First Thousand",
                description="Earn $1,000 in licensing revenue",
                category=AchievementCategory.REVENUE,
                criteria={"total_revenue": Decimal("1000")},
                reward_type=RewardType.CASH_BONUS,
                reward_value=Decimal("50"),
                xp_bonus=200,
                rarity="common",
                icon_url="/icons/achievements/first_thousand.png",
                unlock_conditions=["licensing_count>=1"]
            )
        ]
        
        for achievement in achievements:
            self.achievements[achievement.achievement_id] = achievement

    def _initialize_default_badges(self) -> None:
        """Initialize default badges for the system."""
        badges = [
            Badge(
                badge_id="verified_creator",
                name="Verified Creator",
                description="Verified content creator with authentic licensing",
                design_url="/badges/verified_creator.svg",
                rarity="common"
            ),
            Badge(
                badge_id="top_earner",
                name="Top Earner",
                description="Top 1% revenue performer this month",
                design_url="/badges/top_earner.svg",
                rarity="rare",
                is_animated=True
            )
        ]
        
        for badge in badges:
            self.badges[badge.badge_id] = badge

    def _initialize_tier_system(self) -> None:
        """Initialize the creator tier system."""
        self.tier_requirements = {
            CreatorTier.NEWCOMER: {
                "min_xp": 0,
                "min_revenue": Decimal("0"),
                "min_licenses": 0,
                "benefits": {"royalty_bonus": Decimal("0")}
            },
            CreatorTier.RISING_STAR: {
                "min_xp": 500,
                "min_revenue": Decimal("1000"),
                "min_licenses": 5,
                "benefits": {"royalty_bonus": Decimal("1.0")}
            },
            CreatorTier.PROFESSIONAL: {
                "min_xp": 5000,
                "min_revenue": Decimal("50000"),
                "min_licenses": 100,
                "benefits": {"royalty_bonus": Decimal("5.0")}
            },
            CreatorTier.MASTER: {
                "min_xp": 100000,
                "min_revenue": Decimal("5000000"),
                "min_licenses": 10000,
                "benefits": {"royalty_bonus": Decimal("15.0")}
            }
        }

    def _initialize_leaderboards(self) -> None:
        """Initialize default leaderboards."""
        configs = [
            {"leaderboard_id": "top_earners", "name": "Top Earners", "category": "revenue", "time_period": "monthly"},
            {"leaderboard_id": "most_licensed", "name": "Most Licensed", "category": "licensing", "time_period": "weekly"}
        ]
        
        for config in configs:
            leaderboard = Leaderboard(**config)
            self.leaderboards[leaderboard.leaderboard_id] = leaderboard

    async def create_creator_profile(self, creator_id: str, username: str, email: str, initial_data: Dict[str, Any] = None) -> CreatorProfile:
        """Create a new creator profile."""
        if creator_id in self.creator_profiles:
            raise ValueError(f"Creator profile already exists: {creator_id}")
        
        profile = CreatorProfile(
            creator_id=creator_id,
            username=username,
            email=email,
            current_tier=CreatorTier.NEWCOMER,
            experience_points=0,
            level=1,
            total_revenue=Decimal("0"),
            licensing_count=0,
            collaboration_count=0
        )
        
        if initial_data:
            for key, value in initial_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
        
        self.creator_profiles[creator_id] = profile
        logger.info(f"Creator profile created: {creator_id}")
        return profile

    async def update_creator_stats(self, creator_id: str, stat_updates: Dict[str, Any]) -> CreatorProfile:
        """Update creator statistics."""
        if creator_id not in self.creator_profiles:
            raise ValueError(f"Creator profile not found: {creator_id}")
        
        profile = self.creator_profiles[creator_id]
        
        for stat, value in stat_updates.items():
            if hasattr(profile, stat):
                current_value = getattr(profile, stat)
                if isinstance(current_value, (int, float, Decimal)):
                    if stat in ["experience_points", "total_revenue", "licensing_count", "collaboration_count"]:
                        setattr(profile, stat, current_value + value)
                    else:
                        setattr(profile, stat, value)
        
        profile.level = self._calculate_level_from_xp(profile.experience_points)
        profile.current_tier = self._calculate_tier(profile)
        profile.tier_progress = self._calculate_tier_progress(profile)
        profile.last_active = datetime.utcnow()
        
        await self._check_and_award_achievements(creator_id, stat_updates)
        
        logger.info(f"Creator stats updated: {creator_id}")
        return profile

    async def award_achievement(self, creator_id: str, achievement_id: str, context: Dict[str, Any] = None) -> Reward:
        """Award an achievement to a creator."""
        if creator_id not in self.creator_profiles:
            raise ValueError(f"Creator profile not found: {creator_id}")
        
        if achievement_id not in self.achievements:
            raise ValueError(f"Achievement not found: {achievement_id}")
        
        profile = self.creator_profiles[creator_id]
        achievement = self.achievements[achievement_id]
        
        if achievement_id in profile.achievements and not achievement.is_repeatable:
            return None
        
        profile.achievements.append(achievement_id)
        profile.experience_points += achievement.xp_bonus
        
        reward = Reward(
            reward_id=str(uuid.uuid4()),
            creator_id=creator_id,
            reward_type=achievement.reward_type,
            value=achievement.reward_value,
            source=f"achievement:{achievement_id}",
            earned_at=datetime.utcnow(),
            metadata={"achievement_name": achievement.name}
        )
        
        self.rewards[reward.reward_id] = reward
        
        logger.info(f"Achievement awarded: {achievement.name} to {creator_id}")
        return reward

    async def calculate_performance_bonus(self, creator_id: str, base_amount: Decimal, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance-based bonus for a creator."""
        if creator_id not in self.creator_profiles:
            raise ValueError(f"Creator profile not found: {creator_id}")
        
        profile = self.creator_profiles[creator_id]
        tier_benefits = self.tier_requirements[profile.current_tier]["benefits"]
        tier_bonus_percentage = tier_benefits["royalty_bonus"]
        
        platform_bonus = Decimal("0")
        for platform, metrics in performance_metrics.get("platform_metrics", {}).items():
            if metrics.get("performance_score", 0) > 0.8:
                platform_bonus += Decimal("2.0")
        
        total_bonus_percentage = tier_bonus_percentage + platform_bonus
        bonus_amount = (base_amount * total_bonus_percentage / Decimal("100")).quantize(Decimal("0.01"))
        final_amount = base_amount + bonus_amount
        
        return {
            "creator_id": creator_id,
            "base_amount": str(base_amount),
            "bonus_amount": str(bonus_amount),
            "final_amount": str(final_amount),
            "total_bonus_percentage": str(total_bonus_percentage),
            "tier": profile.current_tier.value,
            "calculated_at": datetime.utcnow().isoformat()
        }

    def _calculate_level_from_xp(self, experience_points: int) -> int:
        """Calculate creator level from experience points."""
        return int(math.sqrt(experience_points / 100)) + 1

    def _calculate_tier(self, profile: CreatorProfile) -> CreatorTier:
        """Calculate appropriate tier for creator."""
        for tier in reversed(list(CreatorTier)):
            requirements = self.tier_requirements[tier]
            if (profile.experience_points >= requirements["min_xp"] and
                profile.total_revenue >= requirements["min_revenue"] and
                profile.licensing_count >= requirements["min_licenses"]):
                return tier
        return CreatorTier.NEWCOMER

    def _calculate_tier_progress(self, profile: CreatorProfile) -> float:
        """Calculate progress towards next tier."""
        current_tier = profile.current_tier
        tier_list = list(CreatorTier)
        current_index = tier_list.index(current_tier)
        
        if current_index >= len(tier_list) - 1:
            return 100.0
        
        next_tier = tier_list[current_index + 1]
        current_reqs = self.tier_requirements[current_tier]
        next_reqs = self.tier_requirements[next_tier]
        
        xp_progress = min((profile.experience_points - current_reqs["min_xp"]) / max(next_reqs["min_xp"] - current_reqs["min_xp"], 1), 1.0)
        revenue_progress = min(float((profile.total_revenue - current_reqs["min_revenue"]) / max(next_reqs["min_revenue"] - current_reqs["min_revenue"], Decimal("1"))), 1.0)
        license_progress = min((profile.licensing_count - current_reqs["min_licenses"]) / max(next_reqs["min_licenses"] - current_reqs["min_licenses"], 1), 1.0)
        
        return (xp_progress + revenue_progress + license_progress) / 3.0 * 100.0

    async def _check_and_award_achievements(self, creator_id: str, update_data: Dict[str, Any]) -> List[str]:
        """Check if any achievements should be awarded."""
        awarded_achievements = []
        
        if creator_id not in self.creator_profiles:
            return awarded_achievements
        
        profile = self.creator_profiles[creator_id]
        
        for achievement_id, achievement in self.achievements.items():
            if achievement_id in profile.achievements and not achievement.is_repeatable:
                continue
            
            criteria_met = True
            for criterion, target_value in achievement.criteria.items():
                if hasattr(profile, criterion):
                    current_value = getattr(profile, criterion)
                    if isinstance(current_value, (int, float, Decimal)):
                        if current_value < target_value:
                            criteria_met = False
                            break
            
            if criteria_met:
                reward = await self.award_achievement(creator_id, achievement_id, update_data)
                if reward:
                    awarded_achievements.append(achievement_id)
        
        return awarded_achievements

# Export main classes
__all__ = [
    "GamificationLicensingSystem",
    "CreatorProfile", 
    "Achievement",
    "Badge",
    "Challenge",
    "Leaderboard",
    "Reward",
    "SocialAction",
    "CreatorTier",
    "AchievementCategory",
    "RewardType",
    "ChallengeType"
]