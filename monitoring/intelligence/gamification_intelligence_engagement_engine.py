"""Gamification Intelligence Engagement Engine
===========================================

Enterprise-grade Gamification Intelligence system providing comprehensive
engagement optimization, intelligent reward systems, and advanced gamification
analytics for the IA Chérie Creator Economy. Implements sophisticated behavioral
psychology, achievement tracking, and intelligent engagement optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team technical training included
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

# Optional imports for enhanced functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy for basic operations
    np = type('MockNumpy', (), {
        'random': type('MockRandom', (), {
            'rand': lambda: __import__('random').random(),
            'choice': lambda x: __import__('random').choice(x)
        })(),
        'mean': lambda x: sum(x) / len(x) if x else 0,
        'std': lambda x: (sum((i - sum(x)/len(x))**2 for i in x) / len(x))**0.5 if x else 0
    })()

logger = logging.getLogger(__name__)

class EngagementActionType(Enum):
    """Types of engagement actions that can be tracked"""
    CONTENT_CREATION = "content_creation"
    CONTENT_LIKE = "content_like"
    CONTENT_SHARE = "content_share"
    CONTENT_COMMENT = "content_comment"
    FOLLOWER_GAINED = "follower_gained"
    COLLABORATION_STARTED = "collaboration_started"
    COLLABORATION_COMPLETED = "collaboration_completed"
    REVENUE_MILESTONE = "revenue_milestone"
    PLATFORM_JOIN = "platform_join"
    LIVE_STREAM = "live_stream"
    VIRAL_CONTENT = "viral_content"
    BRAND_PARTNERSHIP = "brand_partnership"
    CREATOR_MENTORSHIP = "creator_mentorship"
    COMMUNITY_BUILDING = "community_building"
    SKILL_DEVELOPMENT = "skill_development"

class RewardType(Enum):
    """Types of rewards in the gamification system"""
    POINTS = "points"
    BADGE = "badge"
    ACHIEVEMENT = "achievement"
    TIER_UPGRADE = "tier_upgrade"
    EXCLUSIVE_ACCESS = "exclusive_access"
    MONETARY_BONUS = "monetary_bonus"
    FEATURE_UNLOCK = "feature_unlock"
    RECOGNITION = "recognition"
    COLLABORATION_OPPORTUNITY = "collaboration_opportunity"
    PREMIUM_SUPPORT = "premium_support"

class AchievementCategory(Enum):
    """Categories of achievements"""
    CREATOR_MILESTONE = "creator_milestone"
    ENGAGEMENT_MASTER = "engagement_master"
    COLLABORATION_EXPERT = "collaboration_expert"
    REVENUE_CHAMPION = "revenue_champion"
    PLATFORM_EXPLORER = "platform_explorer"
    COMMUNITY_LEADER = "community_leader"
    INNOVATION_PIONEER = "innovation_pioneer"
    CONSISTENCY_KING = "consistency_king"
    VIRAL_CREATOR = "viral_creator"
    MENTOR_GUIDE = "mentor_guide"

class EngagementLevel(Enum):
    """User engagement levels"""
    NEWCOMER = "newcomer"
    ACTIVE = "active"
    ENGAGED = "engaged"
    SUPER_ENGAGED = "super_engaged"
    CHAMPION = "champion"

@dataclass
class EngagementAction:
    """Engagement action data structure"""
    action_id: str
    creator_id: str
    action_type: EngagementActionType
    timestamp: datetime
    points_earned: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    platform: Optional[str] = None
    content_id: Optional[str] = None

@dataclass
class Achievement:
    """Achievement definition"""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    points_reward: int
    requirements: Dict[str, Any]
    icon_url: Optional[str] = None
    is_hidden: bool = False
    rarity: str = "common"  # common, rare, epic, legendary
    unlock_date: Optional[datetime] = None

@dataclass
class CreatorAchievement:
    """Creator's earned achievement"""
    achievement_id: str
    creator_id: str
    earned_date: datetime
    progress: float = 1.0
    is_completed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Reward:
    """Reward given to creator"""
    reward_id: str
    creator_id: str
    reward_type: RewardType
    value: Any  # Could be points, badge, etc.
    earned_date: datetime
    description: str
    is_claimed: bool = False
    expiry_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorGamificationProfile:
    """Creator's gamification profile"""
    creator_id: str
    username: str
    total_points: int = 0
    engagement_level: EngagementLevel = EngagementLevel.NEWCOMER
    achievements: List[str] = field(default_factory=list)  # Achievement IDs
    badges: List[str] = field(default_factory=list)
    streak_days: int = 0
    last_active_date: Optional[datetime] = None
    join_date: datetime = field(default_factory=datetime.now)
    engagement_score: float = 0.0
    collaboration_count: int = 0
    content_count: int = 0
    follower_count: int = 0
    revenue_generated: float = 0.0
    platform_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EngagementAnalytics:
    """Engagement analytics data"""
    timeframe: str
    total_actions: int
    unique_creators: int
    top_actions: List[Dict[str, Any]]
    engagement_trends: Dict[str, List[float]]
    achievement_stats: Dict[str, int]
    reward_distribution: Dict[str, int]
    level_distribution: Dict[str, int]

@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    rank: int
    creator_id: str
    username: str
    score: float
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class GamificationIntelligenceEngagementEngine:
    """Enterprise Gamification Intelligence Engagement Engine
    
    Provides comprehensive gamification system with intelligent engagement
    optimization, achievement tracking, reward management, and behavioral analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Gamification Intelligence Engagement Engine
        
        Args:
            config: Configuration dictionary for gamification settings
        """
        self.config = config or {}
        self.creator_profiles = {}
        self.achievements = {}
        self.creator_achievements = defaultdict(list)
        self.engagement_actions = defaultdict(list)
        self.rewards = defaultdict(list)
        self.leaderboards = {}
        self.engagement_analytics = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize default achievements and reward structure
        self._initialize_default_achievements()
        self._initialize_point_system()
        
        # Engagement level thresholds
        self.engagement_thresholds = {
            EngagementLevel.NEWCOMER: {"points": 0, "actions": 0},
            EngagementLevel.ACTIVE: {"points": 100, "actions": 10},
            EngagementLevel.ENGAGED: {"points": 500, "actions": 50},
            EngagementLevel.SUPER_ENGAGED: {"points": 2000, "actions": 200},
            EngagementLevel.CHAMPION: {"points": 10000, "actions": 1000}
        }
        
        logger.info("Gamification Intelligence Engagement Engine initialized successfully")
    
    def _initialize_default_achievements(self):
        """Initialize default achievement system"""
        default_achievements = [
            # Creator Milestone Achievements
            Achievement(
                achievement_id="first_content",
                name="First Steps",
                description="Create your first piece of content",
                category=AchievementCategory.CREATOR_MILESTONE,
                points_reward=50,
                requirements={"content_count": 1},
                rarity="common"
            ),
            Achievement(
                achievement_id="content_creator_10",
                name="Content Creator",
                description="Create 10 pieces of content",
                category=AchievementCategory.CREATOR_MILESTONE,
                points_reward=200,
                requirements={"content_count": 10},
                rarity="common"
            ),
            Achievement(
                achievement_id="content_master_100",
                name="Content Master",
                description="Create 100 pieces of content",
                category=AchievementCategory.CREATOR_MILESTONE,
                points_reward=1000,
                requirements={"content_count": 100},
                rarity="rare"
            ),
            
            # Engagement Master Achievements
            Achievement(
                achievement_id="engagement_starter",
                name="Engagement Starter",
                description="Reach 100 total engagement points",
                category=AchievementCategory.ENGAGEMENT_MASTER,
                points_reward=100,
                requirements={"total_points": 100},
                rarity="common"
            ),
            Achievement(
                achievement_id="engagement_expert",
                name="Engagement Expert",
                description="Reach 1000 total engagement points",
                category=AchievementCategory.ENGAGEMENT_MASTER,
                points_reward=500,
                requirements={"total_points": 1000},
                rarity="rare"
            ),
            Achievement(
                achievement_id="engagement_legend",
                name="Engagement Legend",
                description="Reach 10000 total engagement points",
                category=AchievementCategory.ENGAGEMENT_MASTER,
                points_reward=2500,
                requirements={"total_points": 10000},
                rarity="legendary"
            ),
            
            # Collaboration Expert Achievements
            Achievement(
                achievement_id="first_collaboration",
                name="Team Player",
                description="Complete your first collaboration",
                category=AchievementCategory.COLLABORATION_EXPERT,
                points_reward=150,
                requirements={"collaboration_count": 1},
                rarity="common"
            ),
            Achievement(
                achievement_id="collaboration_master",
                name="Collaboration Master",
                description="Complete 10 collaborations",
                category=AchievementCategory.COLLABORATION_EXPERT,
                points_reward=750,
                requirements={"collaboration_count": 10},
                rarity="rare"
            ),
            
            # Revenue Champion Achievements
            Achievement(
                achievement_id="first_dollar",
                name="First Earnings",
                description="Generate your first dollar in revenue",
                category=AchievementCategory.REVENUE_CHAMPION,
                points_reward=100,
                requirements={"revenue_generated": 1.0},
                rarity="common"
            ),
            Achievement(
                achievement_id="revenue_milestone_1k",
                name="Thousand Club",
                description="Generate $1,000 in revenue",
                category=AchievementCategory.REVENUE_CHAMPION,
                points_reward=1000,
                requirements={"revenue_generated": 1000.0},
                rarity="epic"
            ),
            
            # Platform Explorer Achievements
            Achievement(
                achievement_id="multi_platform",
                name="Platform Explorer",
                description="Join 3 different platforms",
                category=AchievementCategory.PLATFORM_EXPLORER,
                points_reward=300,
                requirements={"platform_count": 3},
                rarity="common"
            ),
            Achievement(
                achievement_id="platform_master",
                name="Platform Master",
                description="Join 5 different platforms",
                category=AchievementCategory.PLATFORM_EXPLORER,
                points_reward=800,
                requirements={"platform_count": 5},
                rarity="rare"
            ),
            
            # Consistency Achievements
            Achievement(
                achievement_id="weekly_streak",
                name="Consistent Creator",
                description="Maintain a 7-day activity streak",
                category=AchievementCategory.CONSISTENCY_KING,
                points_reward=200,
                requirements={"streak_days": 7},
                rarity="common"
            ),
            Achievement(
                achievement_id="monthly_streak",
                name="Dedication Master",
                description="Maintain a 30-day activity streak",
                category=AchievementCategory.CONSISTENCY_KING,
                points_reward=1000,
                requirements={"streak_days": 30},
                rarity="epic"
            ),
            
            # Community Leader Achievements
            Achievement(
                achievement_id="follower_milestone_100",
                name="Rising Star",
                description="Reach 100 followers",
                category=AchievementCategory.COMMUNITY_LEADER,
                points_reward=300,
                requirements={"follower_count": 100},
                rarity="common"
            ),
            Achievement(
                achievement_id="follower_milestone_1k",
                name="Influencer",
                description="Reach 1,000 followers",
                category=AchievementCategory.COMMUNITY_LEADER,
                points_reward=1500,
                requirements={"follower_count": 1000},
                rarity="rare"
            ),
            Achievement(
                achievement_id="follower_milestone_10k",
                name="Community Leader",
                description="Reach 10,000 followers",
                category=AchievementCategory.COMMUNITY_LEADER,
                points_reward=5000,
                requirements={"follower_count": 10000},
                rarity="legendary"
            )
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.achievement_id] = achievement
        
        logger.info(f"Initialized {len(default_achievements)} default achievements")
    
    def _initialize_point_system(self):
        """Initialize point reward system for different actions"""
        self.action_points = {
            EngagementActionType.CONTENT_CREATION: 20,
            EngagementActionType.CONTENT_LIKE: 1,
            EngagementActionType.CONTENT_SHARE: 5,
            EngagementActionType.CONTENT_COMMENT: 3,
            EngagementActionType.FOLLOWER_GAINED: 2,
            EngagementActionType.COLLABORATION_STARTED: 50,
            EngagementActionType.COLLABORATION_COMPLETED: 100,
            EngagementActionType.REVENUE_MILESTONE: 200,
            EngagementActionType.PLATFORM_JOIN: 30,
            EngagementActionType.LIVE_STREAM: 40,
            EngagementActionType.VIRAL_CONTENT: 500,
            EngagementActionType.BRAND_PARTNERSHIP: 300,
            EngagementActionType.CREATOR_MENTORSHIP: 150,
            EngagementActionType.COMMUNITY_BUILDING: 75,
            EngagementActionType.SKILL_DEVELOPMENT: 25
        }
    
    async def register_creator(self, creator_id: str, username: str) -> bool:
        """Register a new creator in the gamification system
        
        Args:
            creator_id: Unique creator identifier
            username: Creator's username
            
        Returns:
            Success status of registration
        """
        try:
            if creator_id in self.creator_profiles:
                logger.warning(f"Creator {creator_id} already registered")
                return True
            
            profile = CreatorGamificationProfile(
                creator_id=creator_id,
                username=username,
                last_active_date=datetime.now()
            )
            
            self.creator_profiles[creator_id] = profile
            
            # Initialize engagement action tracking
            self.engagement_actions[creator_id] = []
            self.creator_achievements[creator_id] = []
            self.rewards[creator_id] = []
            
            # Award welcome achievement
            await self._check_and_award_achievements(creator_id)
            
            logger.info(f"Creator {username} registered successfully in gamification system")
            return True
            
        except Exception as e:
            logger.error(f"Error registering creator: {str(e)}")
            return False
    
    async def record_engagement_action(self, action: EngagementAction) -> bool:
        """Record an engagement action and process rewards
        
        Args:
            action: Engagement action to record
            
        Returns:
            Success status of recording
        """
        try:
            if action.creator_id not in self.creator_profiles:
                logger.warning(f"Unknown creator ID: {action.creator_id}")
                return False
            
            # Calculate points for this action
            base_points = self.action_points.get(action.action_type, 10)
            
            # Apply multipliers based on creator level and streaks
            profile = self.creator_profiles[action.creator_id]
            multiplier = await self._calculate_point_multiplier(profile, action)
            
            action.points_earned = int(base_points * multiplier)
            
            # Record the action
            self.engagement_actions[action.creator_id].append(action)
            
            # Update creator profile
            await self._update_creator_profile(action)
            
            # Check for achievements
            await self._check_and_award_achievements(action.creator_id)
            
            # Update engagement level
            await self._update_engagement_level(action.creator_id)
            
            # Update leaderboards
            await self._update_leaderboards(action.creator_id)
            
            logger.debug(f"Engagement action recorded: {action.action_type.value} (+{action.points_earned} points)")
            return True
            
        except Exception as e:
            logger.error(f"Error recording engagement action: {str(e)}")
            return False
    
    async def _calculate_point_multiplier(
        self, 
        profile: CreatorGamificationProfile, 
        action: EngagementAction
    ) -> float:
        """Calculate point multiplier based on various factors"""
        multiplier = 1.0
        
        # Streak bonus
        if profile.streak_days >= 30:
            multiplier += 0.5  # 50% bonus for 30+ day streak
        elif profile.streak_days >= 7:
            multiplier += 0.2  # 20% bonus for 7+ day streak
        
        # Level bonus
        level_bonuses = {
            EngagementLevel.NEWCOMER: 1.0,
            EngagementLevel.ACTIVE: 1.1,
            EngagementLevel.ENGAGED: 1.2,
            EngagementLevel.SUPER_ENGAGED: 1.3,
            EngagementLevel.CHAMPION: 1.5
        }
        multiplier *= level_bonuses.get(profile.engagement_level, 1.0)
        
        # Special action bonuses
        if action.action_type == EngagementActionType.VIRAL_CONTENT:
            multiplier *= 2.0  # Double points for viral content
        elif action.action_type == EngagementActionType.COLLABORATION_COMPLETED:
            multiplier *= 1.5  # 50% bonus for completed collaborations
        
        # Time-based bonuses (e.g., weekend bonus)
        if datetime.now().weekday() >= 5:  # Weekend
            multiplier *= 1.1
        
        return multiplier
    
    async def _update_creator_profile(self, action: EngagementAction):
        """Update creator profile based on engagement action"""
        profile = self.creator_profiles[action.creator_id]
        
        # Add points
        profile.total_points += action.points_earned
        
        # Update last active date
        profile.last_active_date = action.timestamp
        
        # Update streak
        await self._update_activity_streak(profile, action.timestamp)
        
        # Update specific counters based on action type
        if action.action_type == EngagementActionType.CONTENT_CREATION:
            profile.content_count += 1
        elif action.action_type == EngagementActionType.COLLABORATION_COMPLETED:
            profile.collaboration_count += 1
        elif action.action_type == EngagementActionType.FOLLOWER_GAINED:
            profile.follower_count += action.metadata.get("count", 1)
        elif action.action_type == EngagementActionType.REVENUE_MILESTONE:
            profile.revenue_generated += action.metadata.get("amount", 0)
        elif action.action_type == EngagementActionType.PLATFORM_JOIN:
            profile.platform_count += 1
        
        # Calculate engagement score
        profile.engagement_score = await self._calculate_engagement_score(profile)
    
    async def _update_activity_streak(self, profile: CreatorGamificationProfile, action_date: datetime):
        """Update creator's activity streak"""
        if not profile.last_active_date:
            profile.streak_days = 1
            return
        
        # Check if action is on consecutive day
        last_date = profile.last_active_date.date()
        current_date = action_date.date()
        
        if current_date == last_date + timedelta(days=1):
            # Consecutive day - extend streak
            profile.streak_days += 1
        elif current_date == last_date:
            # Same day - maintain streak
            pass
        else:
            # Gap in activity - reset streak
            profile.streak_days = 1
    
    async def _calculate_engagement_score(self, profile: CreatorGamificationProfile) -> float:
        """Calculate overall engagement score for creator"""
        # Base score from points
        base_score = profile.total_points
        
        # Bonus for consistency (streak)
        streak_bonus = min(profile.streak_days * 10, 500)  # Max 500 bonus
        
        # Bonus for diversification
        diversification_bonus = profile.platform_count * 50
        
        # Bonus for achievements
        achievement_bonus = len(profile.achievements) * 25
        
        # Bonus for collaboration
        collaboration_bonus = profile.collaboration_count * 75
        
        total_score = base_score + streak_bonus + diversification_bonus + achievement_bonus + collaboration_bonus
        
        return round(total_score, 2)
    
    async def _check_and_award_achievements(self, creator_id: str):
        """Check and award new achievements for creator"""
        profile = self.creator_profiles[creator_id]
        
        for achievement_id, achievement in self.achievements.items():
            # Skip if already earned
            if achievement_id in profile.achievements:
                continue
            
            # Check if requirements are met
            if await self._check_achievement_requirements(profile, achievement):
                await self._award_achievement(creator_id, achievement_id)
    
    async def _check_achievement_requirements(
        self, 
        profile: CreatorGamificationProfile, 
        achievement: Achievement
    ) -> bool:
        """Check if creator meets achievement requirements"""
        requirements = achievement.requirements
        
        for req_key, req_value in requirements.items():
            profile_value = getattr(profile, req_key, 0)
            
            if isinstance(req_value, (int, float)):
                if profile_value < req_value:
                    return False
            elif isinstance(req_value, str):
                if str(profile_value) != req_value:
                    return False
            elif isinstance(req_value, list):
                if profile_value not in req_value:
                    return False
        
        return True
    
    async def _award_achievement(self, creator_id: str, achievement_id: str):
        """Award achievement to creator"""
        achievement = self.achievements[achievement_id]
        profile = self.creator_profiles[creator_id]
        
        # Add achievement to profile
        profile.achievements.append(achievement_id)
        
        # Create achievement record
        creator_achievement = CreatorAchievement(
            achievement_id=achievement_id,
            creator_id=creator_id,
            earned_date=datetime.now()
        )
        self.creator_achievements[creator_id].append(creator_achievement)
        
        # Award points
        profile.total_points += achievement.points_reward
        
        # Create reward
        reward = Reward(
            reward_id=str(uuid.uuid4()),
            creator_id=creator_id,
            reward_type=RewardType.ACHIEVEMENT,
            value=achievement_id,
            earned_date=datetime.now(),
            description=f"Achievement unlocked: {achievement.name}"
        )
        self.rewards[creator_id].append(reward)
        
        # Check for tier upgrades
        await self._check_tier_upgrade(creator_id)
        
        logger.info(f"Achievement '{achievement.name}' awarded to creator {profile.username}")
    
    async def _update_engagement_level(self, creator_id: str):
        """Update creator's engagement level based on activity"""
        profile = self.creator_profiles[creator_id]
        
        # Count recent actions (last 30 days)
        recent_actions = [
            action for action in self.engagement_actions[creator_id]
            if action.timestamp >= datetime.now() - timedelta(days=30)
        ]
        
        # Determine new level based on points and activity
        new_level = EngagementLevel.NEWCOMER
        
        for level in [EngagementLevel.CHAMPION, EngagementLevel.SUPER_ENGAGED, 
                      EngagementLevel.ENGAGED, EngagementLevel.ACTIVE]:
            thresholds = self.engagement_thresholds[level]
            if (profile.total_points >= thresholds["points"] and 
                len(recent_actions) >= thresholds["actions"]):
                new_level = level
                break
        
        # Check for level up
        if new_level != profile.engagement_level:
            old_level = profile.engagement_level
            profile.engagement_level = new_level
            
            # Award level up bonus
            await self._award_level_up_bonus(creator_id, old_level, new_level)
            
            logger.info(f"Creator {profile.username} leveled up from {old_level.value} to {new_level.value}")
    
    async def _award_level_up_bonus(
        self, 
        creator_id: str, 
        old_level: EngagementLevel, 
        new_level: EngagementLevel
    ):
        """Award bonus for leveling up"""
        level_bonuses = {
            EngagementLevel.ACTIVE: 100,
            EngagementLevel.ENGAGED: 250,
            EngagementLevel.SUPER_ENGAGED: 500,
            EngagementLevel.CHAMPION: 1000
        }
        
        bonus_points = level_bonuses.get(new_level, 0)
        
        if bonus_points > 0:
            profile = self.creator_profiles[creator_id]
            profile.total_points += bonus_points
            
            # Create reward
            reward = Reward(
                reward_id=str(uuid.uuid4()),
                creator_id=creator_id,
                reward_type=RewardType.POINTS,
                value=bonus_points,
                earned_date=datetime.now(),
                description=f"Level up bonus: {old_level.value} → {new_level.value}"
            )
            self.rewards[creator_id].append(reward)
    
    async def _check_tier_upgrade(self, creator_id: str):
        """Check if creator qualifies for tier upgrade"""
        # This would integrate with the tier management system
        # For now, we'll just log the potential upgrade
        profile = self.creator_profiles[creator_id]
        
        # Simple tier logic based on points and achievements
        if (profile.total_points >= 10000 and len(profile.achievements) >= 10 and 
            profile.engagement_level == EngagementLevel.CHAMPION):
            logger.info(f"Creator {profile.username} qualifies for premium tier upgrade")
    
    async def _update_leaderboards(self, creator_id: str):
        """Update leaderboards with creator's latest performance"""
        profile = self.creator_profiles[creator_id]
        
        # Update different leaderboard categories
        leaderboard_categories = ["total_points", "engagement_score", "achievements", "streak_days"]
        
        for category in leaderboard_categories:
            if category not in self.leaderboards:
                self.leaderboards[category] = []
            
            # Remove existing entry for this creator
            self.leaderboards[category] = [
                entry for entry in self.leaderboards[category]
                if entry.creator_id != creator_id
            ]
            
            # Add new entry
            score = getattr(profile, category, 0)
            if isinstance(score, list):
                score = len(score)
            
            entry = LeaderboardEntry(
                rank=0,  # Will be calculated when retrieving leaderboard
                creator_id=creator_id,
                username=profile.username,
                score=float(score),
                category=category
            )
            
            self.leaderboards[category].append(entry)
            
            # Sort and limit to top 100
            self.leaderboards[category].sort(key=lambda x: x.score, reverse=True)
            self.leaderboards[category] = self.leaderboards[category][:100]
            
            # Update ranks
            for i, entry in enumerate(self.leaderboards[category]):
                entry.rank = i + 1
    
    async def get_creator_gamification_profile(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive gamification profile for creator
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Gamification profile data
        """
        try:
            if creator_id not in self.creator_profiles:
                return None
            
            profile = self.creator_profiles[creator_id]
            achievements_data = []
            
            # Get achievement details
            for achievement_id in profile.achievements:
                achievement = self.achievements.get(achievement_id)
                if achievement:
                    achievements_data.append({
                        "id": achievement_id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "category": achievement.category.value,
                        "rarity": achievement.rarity,
                        "points": achievement.points_reward
                    })
            
            # Get recent rewards
            recent_rewards = [
                {
                    "type": reward.reward_type.value,
                    "value": reward.value,
                    "description": reward.description,
                    "earned_date": reward.earned_date.isoformat(),
                    "is_claimed": reward.is_claimed
                }
                for reward in self.rewards[creator_id][-10:]  # Last 10 rewards
            ]
            
            # Get recent activities
            recent_activities = [
                {
                    "action": action.action_type.value,
                    "points": action.points_earned,
                    "timestamp": action.timestamp.isoformat(),
                    "platform": action.platform
                }
                for action in self.engagement_actions[creator_id][-20:]  # Last 20 actions
            ]
            
            return {
                "creator_id": creator_id,
                "username": profile.username,
                "total_points": profile.total_points,
                "engagement_level": profile.engagement_level.value,
                "engagement_score": profile.engagement_score,
                "streak_days": profile.streak_days,
                "achievements": achievements_data,
                "achievement_count": len(profile.achievements),
                "badges": profile.badges,
                "recent_rewards": recent_rewards,
                "recent_activities": recent_activities,
                "stats": {
                    "content_count": profile.content_count,
                    "collaboration_count": profile.collaboration_count,
                    "follower_count": profile.follower_count,
                    "revenue_generated": profile.revenue_generated,
                    "platform_count": profile.platform_count
                },
                "join_date": profile.join_date.isoformat(),
                "last_active": profile.last_active_date.isoformat() if profile.last_active_date else None
            }
            
        except Exception as e:
            logger.error(f"Error getting gamification profile: {str(e)}")
            return None
    
    async def get_leaderboard(self, category: str = "total_points", limit: int = 50) -> List[Dict[str, Any]]:
        """Get leaderboard for specified category
        
        Args:
            category: Leaderboard category
            limit: Maximum number of entries to return
            
        Returns:
            Leaderboard entries
        """
        try:
            if category not in self.leaderboards:
                return []
            
            entries = self.leaderboards[category][:limit]
            
            return [
                {
                    "rank": entry.rank,
                    "creator_id": entry.creator_id,
                    "username": entry.username,
                    "score": entry.score,
                    "category": entry.category
                }
                for entry in entries
            ]
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {str(e)}")
            return []
    
    async def get_available_achievements(self, creator_id: str) -> List[Dict[str, Any]]:
        """Get achievements available for creator to unlock
        
        Args:
            creator_id: Creator identifier
            
        Returns:
            Available achievements with progress
        """
        try:
            if creator_id not in self.creator_profiles:
                return []
            
            profile = self.creator_profiles[creator_id]
            available_achievements = []
            
            for achievement_id, achievement in self.achievements.items():
                if achievement_id in profile.achievements:
                    continue  # Already earned
                
                # Calculate progress
                progress = await self._calculate_achievement_progress(profile, achievement)
                
                available_achievements.append({
                    "id": achievement_id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "category": achievement.category.value,
                    "points_reward": achievement.points_reward,
                    "rarity": achievement.rarity,
                    "progress": progress,
                    "requirements": achievement.requirements,
                    "is_hidden": achievement.is_hidden
                })
            
            # Sort by progress (closest to completion first)
            available_achievements.sort(key=lambda x: x["progress"], reverse=True)
            
            return available_achievements
            
        except Exception as e:
            logger.error(f"Error getting available achievements: {str(e)}")
            return []
    
    async def _calculate_achievement_progress(
        self, 
        profile: CreatorGamificationProfile, 
        achievement: Achievement
    ) -> float:
        """Calculate progress towards achievement completion"""
        total_progress = 0.0
        requirement_count = len(achievement.requirements)
        
        for req_key, req_value in achievement.requirements.items():
            profile_value = getattr(profile, req_key, 0)
            
            if isinstance(req_value, (int, float)) and req_value > 0:
                requirement_progress = min(1.0, profile_value / req_value)
            else:
                requirement_progress = 1.0 if profile_value == req_value else 0.0
            
            total_progress += requirement_progress
        
        return round(total_progress / requirement_count, 3) if requirement_count > 0 else 0.0
    
    async def get_engagement_analytics(self, timeframe: str = "30d") -> EngagementAnalytics:
        """Get engagement analytics for specified timeframe
        
        Args:
            timeframe: Analytics timeframe (7d, 30d, 90d, 1y)
            
        Returns:
            Engagement analytics data
        """
        try:
            # Parse timeframe
            days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = days_map.get(timeframe, 30)
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Collect analytics data
            total_actions = 0
            unique_creators = set()
            action_counts = defaultdict(int)
            daily_engagement = defaultdict(list)
            
            for creator_id, actions in self.engagement_actions.items():
                creator_actions = [
                    action for action in actions
                    if action.timestamp >= cutoff_date
                ]
                
                if creator_actions:
                    unique_creators.add(creator_id)
                    total_actions += len(creator_actions)
                    
                    for action in creator_actions:
                        action_counts[action.action_type.value] += 1
                        day_key = action.timestamp.date().isoformat()
                        daily_engagement[day_key].append(action.points_earned)
            
            # Top actions
            top_actions = [
                {"action": action, "count": count}
                for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Daily engagement trends
            engagement_trends = {}
            for day, points in daily_engagement.items():
                engagement_trends[day] = sum(points)
            
            # Achievement statistics
            achievement_stats = defaultdict(int)
            for creator_achievements in self.creator_achievements.values():
                for creator_achievement in creator_achievements:
                    if creator_achievement.earned_date >= cutoff_date:
                        achievement = self.achievements.get(creator_achievement.achievement_id)
                        if achievement:
                            achievement_stats[achievement.category.value] += 1
            
            # Reward distribution
            reward_distribution = defaultdict(int)
            for creator_rewards in self.rewards.values():
                for reward in creator_rewards:
                    if reward.earned_date >= cutoff_date:
                        reward_distribution[reward.reward_type.value] += 1
            
            # Level distribution
            level_distribution = defaultdict(int)
            for profile in self.creator_profiles.values():
                level_distribution[profile.engagement_level.value] += 1
            
            return EngagementAnalytics(
                timeframe=timeframe,
                total_actions=total_actions,
                unique_creators=len(unique_creators),
                top_actions=top_actions,
                engagement_trends=dict(engagement_trends),
                achievement_stats=dict(achievement_stats),
                reward_distribution=dict(reward_distribution),
                level_distribution=dict(level_distribution)
            )
            
        except Exception as e:
            logger.error(f"Error getting engagement analytics: {str(e)}")
            return EngagementAnalytics(
                timeframe=timeframe,
                total_actions=0,
                unique_creators=0,
                top_actions=[],
                engagement_trends={},
                achievement_stats={},
                reward_distribution={},
                level_distribution={}
            )
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and performance metrics
        
        Returns:
            System health information
        """
        try:
            total_achievements_earned = sum(
                len(achievements) for achievements in self.creator_achievements.values()
            )
            
            total_rewards_given = sum(
                len(rewards) for rewards in self.rewards.values()
            )
            
            total_actions = sum(
                len(actions) for actions in self.engagement_actions.values()
            )
            
            return {
                "total_creators": len(self.creator_profiles),
                "total_achievements_defined": len(self.achievements),
                "total_achievements_earned": total_achievements_earned,
                "total_rewards_given": total_rewards_given,
                "total_engagement_actions": total_actions,
                "leaderboard_categories": len(self.leaderboards),
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {"status": "error", "message": str(e)}

# Export main class and types
__all__ = [
    'GamificationIntelligenceEngagementEngine',
    'EngagementActionType',
    'RewardType',
    'AchievementCategory',
    'EngagementLevel',
    'EngagementAction',
    'Achievement',
    'CreatorAchievement',
    'Reward',
    'CreatorGamificationProfile',
    'EngagementAnalytics',
    'LeaderboardEntry'
]