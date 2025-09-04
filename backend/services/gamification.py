"""Gamification Service - Consolidated Gamification and Engagement Services
================================================================

Comprehensive gamification system providing achievements, rewards, challenges,
leaderboards, and engagement mechanics for the IA Influencer Agent platform.

Consolidates:
- gamification/ subdirectory (achievements, challenges, rewards modules)
- badge system and social proof engine
- point system and tier management
- competition engine and leaderboards

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/gamification.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Enums
class AchievementType(Enum):
    """Achievement type enumeration"""
    MILESTONE = "milestone"
    PROGRESS = "progress"
    SOCIAL = "social"
    SKILL = "skill"
    SPECIAL = "special"
    SEASONAL = "seasonal"

class AchievementDifficulty(Enum):
    """Achievement difficulty enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    LEGENDARY = "legendary"

class BadgeCategory(Enum):
    """Badge category enumeration"""
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    MENTOR = "mentor"
    INNOVATOR = "innovator"
    COMMUNITY = "community"
    EXPERT = "expert"

class RewardType(Enum):
    """Reward type enumeration"""
    POINTS = "points"
    BADGE = "badge"
    TITLE = "title"
    FEATURE_ACCESS = "feature_access"
    DISCOUNT = "discount"
    MERCHANDISE = "merchandise"
    CURRENCY = "currency"

class ChallengeType(Enum):
    """Challenge type enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    COMMUNITY = "community"
    PERSONAL = "personal"

class TierLevel(Enum):
    """Tier level enumeration"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"

class LeaderboardType(Enum):
    """Leaderboard type enumeration"""
    POINTS = "points"
    ACHIEVEMENTS = "achievements"
    CONTENT_QUALITY = "content_quality"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"

# Data structures
@dataclass
class Achievement:
    """Achievement data structure"""
    achievement_id: str
    name: str
    description: str
    type: AchievementType
    difficulty: AchievementDifficulty
    category: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    points_value: int = 0
    icon_url: Optional[str] = None
    is_hidden: bool = False
    is_repeatable: bool = False
    prerequisites: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass
class UserAchievement:
    """User achievement progress data structure"""
    user_achievement_id: str
    user_id: str
    achievement_id: str
    progress: float = 0.0  # 0.0 to 1.0
    completed: bool = False
    completed_at: Optional[datetime] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    current_values: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Badge:
    """Badge data structure"""
    badge_id: str
    name: str
    description: str
    category: BadgeCategory
    rarity: AchievementDifficulty
    icon_url: Optional[str] = None
    requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass
class UserBadge:
    """User badge data structure"""
    user_badge_id: str
    user_id: str
    badge_id: str
    earned_at: datetime = field(default_factory=datetime.utcnow)
    is_displayed: bool = True

@dataclass
class Challenge:
    """Challenge data structure"""
    challenge_id: str
    name: str
    description: str
    type: ChallengeType
    requirements: Dict[str, Any] = field(default_factory=dict)
    rewards: List[Dict[str, Any]] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    max_participants: Optional[int] = None
    current_participants: int = 0
    is_active: bool = True
    created_by: Optional[str] = None

@dataclass
class UserChallenge:
    """User challenge participation data structure"""
    user_challenge_id: str
    user_id: str
    challenge_id: str
    progress: float = 0.0
    completed: bool = False
    joined_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    current_values: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserPoints:
    """User points data structure"""
    user_id: str
    total_points: int = 0
    current_tier: TierLevel = TierLevel.BRONZE
    points_to_next_tier: int = 0
    lifetime_points: int = 0
    points_breakdown: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Reward:
    """Reward data structure"""
    reward_id: str
    name: str
    description: str
    type: RewardType
    value: Any
    cost: int = 0  # Points cost
    requirements: Dict[str, Any] = field(default_factory=dict)
    is_limited: bool = False
    total_available: Optional[int] = None
    claimed_count: int = 0
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass
class UserReward:
    """User reward claim data structure"""
    user_reward_id: str
    user_id: str
    reward_id: str
    claimed_at: datetime = field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    is_used: bool = False

@dataclass
class LeaderboardEntry:
    """Leaderboard entry data structure"""
    user_id: str
    username: str
    avatar_url: Optional[str]
    score: float
    rank: int
    tier: TierLevel
    badges_count: int = 0
    achievements_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

# Services
class AchievementService:
    """Achievement management and tracking service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.achievements_store: Dict[str, Achievement] = {}
        self.user_achievements_store: Dict[str, List[UserAchievement]] = {}
        self._initialize_achievements()
        logger.info("🏆 Achievement Service initialized")
    
    def _initialize_achievements(self):
        """Initialize default achievements"""
        default_achievements = [
            {
                "achievement_id": "first_content",
                "name": "First Steps",
                "description": "Upload your first piece of content",
                "type": AchievementType.MILESTONE,
                "difficulty": AchievementDifficulty.EASY,
                "category": "content",
                "requirements": {"content_uploads": 1},
                "rewards": [{"type": "points", "value": 100}, {"type": "badge", "value": "creator_badge"}],
                "points_value": 100
            },
            {
                "achievement_id": "social_butterfly",
                "name": "Social Butterfly",
                "description": "Collaborate with 10 different creators",
                "type": AchievementType.SOCIAL,
                "difficulty": AchievementDifficulty.MEDIUM,
                "category": "collaboration",
                "requirements": {"unique_collaborators": 10},
                "rewards": [{"type": "points", "value": 500}, {"type": "title", "value": "Collaborator"}],
                "points_value": 500
            },
            {
                "achievement_id": "viral_hit",
                "name": "Viral Hit",
                "description": "Create content that reaches 1M views",
                "type": AchievementType.MILESTONE,
                "difficulty": AchievementDifficulty.HARD,
                "category": "engagement",
                "requirements": {"total_views": 1000000},
                "rewards": [{"type": "points", "value": 2000}, {"type": "badge", "value": "viral_star"}],
                "points_value": 2000
            },
            {
                "achievement_id": "daily_creator",
                "name": "Daily Creator",
                "description": "Upload content for 30 consecutive days",
                "type": AchievementType.PROGRESS,
                "difficulty": AchievementDifficulty.MEDIUM,
                "category": "consistency",
                "requirements": {"consecutive_days": 30},
                "rewards": [{"type": "points", "value": 1000}, {"type": "feature_access", "value": "premium_tools"}],
                "points_value": 1000
            }
        ]
        
        for achievement_data in default_achievements:
            achievement = Achievement(
                achievement_id=achievement_data["achievement_id"],
                name=achievement_data["name"],
                description=achievement_data["description"],
                type=achievement_data["type"],
                difficulty=achievement_data["difficulty"],
                category=achievement_data["category"],
                requirements=achievement_data["requirements"],
                rewards=achievement_data["rewards"],
                points_value=achievement_data["points_value"]
            )
            self.achievements_store[achievement.achievement_id] = achievement
    
    async def create_achievement(self, achievement_data: Dict[str, Any]) -> Achievement:
        """Create new achievement"""
        try:
            achievement = Achievement(
                achievement_id=achievement_data.get("achievement_id", str(uuid.uuid4())),
                name=achievement_data["name"],
                description=achievement_data["description"],
                type=AchievementType(achievement_data["type"]),
                difficulty=AchievementDifficulty(achievement_data["difficulty"]),
                category=achievement_data["category"],
                requirements=achievement_data.get("requirements", {}),
                rewards=achievement_data.get("rewards", []),
                points_value=achievement_data.get("points_value", 0),
                icon_url=achievement_data.get("icon_url"),
                is_hidden=achievement_data.get("is_hidden", False),
                is_repeatable=achievement_data.get("is_repeatable", False),
                prerequisites=achievement_data.get("prerequisites", [])
            )
            
            self.achievements_store[achievement.achievement_id] = achievement
            logger.info(f"Created achievement: {achievement.achievement_id}")
            return achievement
        except Exception as e:
            logger.error(f"Achievement creation error: {e}")
            raise
    
    async def check_achievement_progress(self, user_id: str, event_data: Dict[str, Any]) -> List[UserAchievement]:
        """Check and update achievement progress for user"""
        try:
            completed_achievements = []
            
            # Get or create user achievements
            if user_id not in self.user_achievements_store:
                self.user_achievements_store[user_id] = []
            
            user_achievements = self.user_achievements_store[user_id]
            
            for achievement in self.achievements_store.values():
                if not achievement.is_active:
                    continue
                
                # Find existing user achievement or create new one
                user_achievement = None
                for ua in user_achievements:
                    if ua.achievement_id == achievement.achievement_id:
                        user_achievement = ua
                        break
                
                if not user_achievement:
                    user_achievement = UserAchievement(
                        user_achievement_id=str(uuid.uuid4()),
                        user_id=user_id,
                        achievement_id=achievement.achievement_id
                    )
                    user_achievements.append(user_achievement)
                
                # Skip if already completed and not repeatable
                if user_achievement.completed and not achievement.is_repeatable:
                    continue
                
                # Check progress
                progress_updated = await self._update_achievement_progress(
                    user_achievement, achievement, event_data
                )
                
                if progress_updated and user_achievement.progress >= 1.0 and not user_achievement.completed:
                    user_achievement.completed = True
                    user_achievement.completed_at = datetime.utcnow()
                    completed_achievements.append(user_achievement)
                    logger.info(f"Achievement completed: {achievement.name} by user {user_id}")
            
            return completed_achievements
        except Exception as e:
            logger.error(f"Achievement progress check error: {e}")
            return []
    
    async def _update_achievement_progress(self, user_achievement: UserAchievement, achievement: Achievement, event_data: Dict[str, Any]) -> bool:
        """Update progress for specific achievement"""
        try:
            requirements = achievement.requirements
            current_values = user_achievement.current_values
            progress_updated = False
            
            for req_key, req_value in requirements.items():
                if req_key in event_data:
                    # Update current value
                    if req_key in current_values:
                        if req_key.startswith("total_") or req_key.startswith("lifetime_"):
                            current_values[req_key] += event_data[req_key]
                        else:
                            current_values[req_key] = event_data[req_key]
                    else:
                        current_values[req_key] = event_data[req_key]
                    
                    progress_updated = True
            
            if progress_updated:
                # Calculate overall progress
                total_progress = 0.0
                req_count = len(requirements)
                
                for req_key, req_value in requirements.items():
                    current_value = current_values.get(req_key, 0)
                    req_progress = min(current_value / req_value, 1.0) if req_value > 0 else 0.0
                    total_progress += req_progress
                
                user_achievement.progress = total_progress / req_count if req_count > 0 else 0.0
            
            return progress_updated
        except Exception as e:
            logger.error(f"Achievement progress update error: {e}")
            return False
    
    async def get_user_achievements(self, user_id: str, completed_only: bool = False) -> List[UserAchievement]:
        """Get user achievements"""
        try:
            user_achievements = self.user_achievements_store.get(user_id, [])
            
            if completed_only:
                user_achievements = [ua for ua in user_achievements if ua.completed]
            
            return user_achievements
        except Exception as e:
            logger.error(f"User achievements retrieval error: {e}")
            return []
    
    async def get_available_achievements(self, user_id: str) -> List[Achievement]:
        """Get available achievements for user"""
        try:
            user_achievements = self.user_achievements_store.get(user_id, [])
            completed_ids = {ua.achievement_id for ua in user_achievements if ua.completed}
            
            available = []
            for achievement in self.achievements_store.values():
                if not achievement.is_active or achievement.is_hidden:
                    continue
                
                # Check if already completed and not repeatable
                if achievement.achievement_id in completed_ids and not achievement.is_repeatable:
                    continue
                
                # Check prerequisites
                if achievement.prerequisites:
                    if not all(prereq in completed_ids for prereq in achievement.prerequisites):
                        continue
                
                available.append(achievement)
            
            return available
        except Exception as e:
            logger.error(f"Available achievements retrieval error: {e}")
            return []

class BadgeService:
    """Badge system and social proof service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.badges_store: Dict[str, Badge] = {}
        self.user_badges_store: Dict[str, List[UserBadge]] = {}
        self._initialize_badges()
        logger.info("🥇 Badge Service initialized")
    
    def _initialize_badges(self):
        """Initialize default badges"""
        default_badges = [
            {
                "badge_id": "creator_badge",
                "name": "Content Creator",
                "description": "Awarded for creating quality content",
                "category": BadgeCategory.CREATOR,
                "rarity": AchievementDifficulty.EASY
            },
            {
                "badge_id": "collaborator_badge",
                "name": "Team Player",
                "description": "Excellent collaboration skills",
                "category": BadgeCategory.COLLABORATOR,
                "rarity": AchievementDifficulty.MEDIUM
            },
            {
                "badge_id": "viral_star",
                "name": "Viral Star",
                "description": "Content reached viral status",
                "category": BadgeCategory.CREATOR,
                "rarity": AchievementDifficulty.HARD
            },
            {
                "badge_id": "mentor_badge",
                "name": "Mentor",
                "description": "Helps and guides other creators",
                "category": BadgeCategory.MENTOR,
                "rarity": AchievementDifficulty.MEDIUM
            }
        ]
        
        for badge_data in default_badges:
            badge = Badge(
                badge_id=badge_data["badge_id"],
                name=badge_data["name"],
                description=badge_data["description"],
                category=badge_data["category"],
                rarity=badge_data["rarity"]
            )
            self.badges_store[badge.badge_id] = badge
    
    async def award_badge(self, user_id: str, badge_id: str) -> bool:
        """Award badge to user"""
        try:
            badge = self.badges_store.get(badge_id)
            if not badge or not badge.is_active:
                return False
            
            # Check if user already has this badge
            user_badges = self.user_badges_store.get(user_id, [])
            if any(ub.badge_id == badge_id for ub in user_badges):
                return False  # Already has badge
            
            # Award badge
            user_badge = UserBadge(
                user_badge_id=str(uuid.uuid4()),
                user_id=user_id,
                badge_id=badge_id
            )
            
            if user_id not in self.user_badges_store:
                self.user_badges_store[user_id] = []
            
            self.user_badges_store[user_id].append(user_badge)
            
            logger.info(f"Awarded badge {badge.name} to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Badge award error: {e}")
            return False
    
    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user badges with badge details"""
        try:
            user_badges = self.user_badges_store.get(user_id, [])
            
            badges_with_details = []
            for user_badge in user_badges:
                badge = self.badges_store.get(user_badge.badge_id)
                if badge:
                    badges_with_details.append({
                        "user_badge": user_badge,
                        "badge": badge
                    })
            
            return badges_with_details
        except Exception as e:
            logger.error(f"User badges retrieval error: {e}")
            return []

class ChallengeService:
    """Challenge creation and management service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.challenges_store: Dict[str, Challenge] = {}
        self.user_challenges_store: Dict[str, List[UserChallenge]] = {}
        self._initialize_challenges()
        logger.info("🎯 Challenge Service initialized")
    
    def _initialize_challenges(self):
        """Initialize default challenges"""
        # Create daily/weekly challenges
        current_time = datetime.utcnow()
        
        daily_challenge = Challenge(
            challenge_id="daily_content",
            name="Daily Content Challenge",
            description="Upload one piece of content today",
            type=ChallengeType.DAILY,
            requirements={"content_uploads": 1},
            rewards=[{"type": "points", "value": 50}],
            start_date=current_time.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        
        weekly_challenge = Challenge(
            challenge_id="weekly_collaboration",
            name="Weekly Collaboration Challenge",
            description="Collaborate with 3 different creators this week",
            type=ChallengeType.WEEKLY,
            requirements={"unique_collaborators": 3},
            rewards=[{"type": "points", "value": 300}, {"type": "badge", "value": "collaborator_badge"}],
            start_date=current_time - timedelta(days=current_time.weekday()),
            end_date=current_time + timedelta(days=6-current_time.weekday())
        )
        
        self.challenges_store[daily_challenge.challenge_id] = daily_challenge
        self.challenges_store[weekly_challenge.challenge_id] = weekly_challenge
    
    async def create_challenge(self, challenge_data: Dict[str, Any]) -> Challenge:
        """Create new challenge"""
        try:
            challenge = Challenge(
                challenge_id=challenge_data.get("challenge_id", str(uuid.uuid4())),
                name=challenge_data["name"],
                description=challenge_data["description"],
                type=ChallengeType(challenge_data["type"]),
                requirements=challenge_data.get("requirements", {}),
                rewards=challenge_data.get("rewards", []),
                start_date=challenge_data.get("start_date", datetime.utcnow()),
                end_date=challenge_data.get("end_date", datetime.utcnow() + timedelta(days=7)),
                max_participants=challenge_data.get("max_participants"),
                created_by=challenge_data.get("created_by")
            )
            
            self.challenges_store[challenge.challenge_id] = challenge
            logger.info(f"Created challenge: {challenge.challenge_id}")
            return challenge
        except Exception as e:
            logger.error(f"Challenge creation error: {e}")
            raise
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """User joins a challenge"""
        try:
            challenge = self.challenges_store.get(challenge_id)
            if not challenge or not challenge.is_active:
                return False
            
            # Check if challenge is still open
            current_time = datetime.utcnow()
            if current_time > challenge.end_date:
                return False
            
            # Check participant limit
            if challenge.max_participants and challenge.current_participants >= challenge.max_participants:
                return False
            
            # Check if user already joined
            user_challenges = self.user_challenges_store.get(user_id, [])
            if any(uc.challenge_id == challenge_id for uc in user_challenges):
                return False
            
            # Join challenge
            user_challenge = UserChallenge(
                user_challenge_id=str(uuid.uuid4()),
                user_id=user_id,
                challenge_id=challenge_id
            )
            
            if user_id not in self.user_challenges_store:
                self.user_challenges_store[user_id] = []
            
            self.user_challenges_store[user_id].append(user_challenge)
            challenge.current_participants += 1
            
            logger.info(f"User {user_id} joined challenge {challenge_id}")
            return True
        except Exception as e:
            logger.error(f"Challenge join error: {e}")
            return False
    
    async def update_challenge_progress(self, user_id: str, event_data: Dict[str, Any]) -> List[UserChallenge]:
        """Update challenge progress for user"""
        try:
            completed_challenges = []
            user_challenges = self.user_challenges_store.get(user_id, [])
            
            for user_challenge in user_challenges:
                if user_challenge.completed:
                    continue
                
                challenge = self.challenges_store.get(user_challenge.challenge_id)
                if not challenge or not challenge.is_active:
                    continue
                
                # Check if challenge is still active
                current_time = datetime.utcnow()
                if current_time > challenge.end_date:
                    continue
                
                # Update progress similar to achievements
                progress_updated = await self._update_challenge_progress(
                    user_challenge, challenge, event_data
                )
                
                if progress_updated and user_challenge.progress >= 1.0:
                    user_challenge.completed = True
                    user_challenge.completed_at = datetime.utcnow()
                    completed_challenges.append(user_challenge)
                    logger.info(f"Challenge completed: {challenge.name} by user {user_id}")
            
            return completed_challenges
        except Exception as e:
            logger.error(f"Challenge progress update error: {e}")
            return []
    
    async def _update_challenge_progress(self, user_challenge: UserChallenge, challenge: Challenge, event_data: Dict[str, Any]) -> bool:
        """Update progress for specific challenge"""
        try:
            requirements = challenge.requirements
            current_values = user_challenge.current_values
            progress_updated = False
            
            for req_key, req_value in requirements.items():
                if req_key in event_data:
                    # Update current value
                    if req_key in current_values:
                        current_values[req_key] += event_data[req_key]
                    else:
                        current_values[req_key] = event_data[req_key]
                    
                    progress_updated = True
            
            if progress_updated:
                # Calculate overall progress
                total_progress = 0.0
                req_count = len(requirements)
                
                for req_key, req_value in requirements.items():
                    current_value = current_values.get(req_key, 0)
                    req_progress = min(current_value / req_value, 1.0) if req_value > 0 else 0.0
                    total_progress += req_progress
                
                user_challenge.progress = total_progress / req_count if req_count > 0 else 0.0
            
            return progress_updated
        except Exception as e:
            logger.error(f"Challenge progress update error: {e}")
            return False
    
    async def get_active_challenges(self) -> List[Challenge]:
        """Get active challenges"""
        try:
            current_time = datetime.utcnow()
            active_challenges = []
            
            for challenge in self.challenges_store.values():
                if (challenge.is_active and 
                    challenge.start_date <= current_time <= challenge.end_date):
                    active_challenges.append(challenge)
            
            return active_challenges
        except Exception as e:
            logger.error(f"Active challenges retrieval error: {e}")
            return []

class PointsRewardService:
    """Points system and reward management service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.user_points_store: Dict[str, UserPoints] = {}
        self.rewards_store: Dict[str, Reward] = {}
        self.user_rewards_store: Dict[str, List[UserReward]] = {}
        self.tier_thresholds = {
            TierLevel.BRONZE: 0,
            TierLevel.SILVER: 1000,
            TierLevel.GOLD: 5000,
            TierLevel.PLATINUM: 15000,
            TierLevel.DIAMOND: 50000,
            TierLevel.MASTER: 100000
        }
        self._initialize_rewards()
        logger.info("💎 Points & Reward Service initialized")
    
    def _initialize_rewards(self):
        """Initialize default rewards"""
        default_rewards = [
            {
                "reward_id": "premium_access_30d",
                "name": "30-Day Premium Access",
                "description": "Unlock premium features for 30 days",
                "type": RewardType.FEATURE_ACCESS,
                "value": {"feature": "premium", "duration_days": 30},
                "cost": 5000
            },
            {
                "reward_id": "profile_badge_custom",
                "name": "Custom Profile Badge",
                "description": "Display a custom badge on your profile",
                "type": RewardType.BADGE,
                "value": "custom_badge",
                "cost": 2000
            },
            {
                "reward_id": "bonus_points_1000",
                "name": "1000 Bonus Points",
                "description": "Get 1000 bonus points instantly",
                "type": RewardType.POINTS,
                "value": 1000,
                "cost": 800
            }
        ]
        
        for reward_data in default_rewards:
            reward = Reward(
                reward_id=reward_data["reward_id"],
                name=reward_data["name"],
                description=reward_data["description"],
                type=RewardType(reward_data["type"]),
                value=reward_data["value"],
                cost=reward_data["cost"]
            )
            self.rewards_store[reward.reward_id] = reward
    
    async def award_points(self, user_id: str, points: int, source: str = "general") -> UserPoints:
        """Award points to user"""
        try:
            if user_id not in self.user_points_store:
                self.user_points_store[user_id] = UserPoints(user_id=user_id)
            
            user_points = self.user_points_store[user_id]
            user_points.total_points += points
            user_points.lifetime_points += points
            
            # Update breakdown
            if source in user_points.points_breakdown:
                user_points.points_breakdown[source] += points
            else:
                user_points.points_breakdown[source] = points
            
            # Check tier upgrade
            new_tier = await self._calculate_tier(user_points.total_points)
            if new_tier != user_points.current_tier:
                logger.info(f"User {user_id} tier upgraded from {user_points.current_tier.value} to {new_tier.value}")
                user_points.current_tier = new_tier
            
            # Calculate points to next tier
            user_points.points_to_next_tier = await self._points_to_next_tier(user_points.total_points, new_tier)
            user_points.last_updated = datetime.utcnow()
            
            logger.debug(f"Awarded {points} points to user {user_id} (source: {source})")
            return user_points
        except Exception as e:
            logger.error(f"Points award error: {e}")
            raise
    
    async def _calculate_tier(self, total_points: int) -> TierLevel:
        """Calculate tier based on total points"""
        for tier in reversed(list(TierLevel)):
            if total_points >= self.tier_thresholds[tier]:
                return tier
        return TierLevel.BRONZE
    
    async def _points_to_next_tier(self, total_points: int, current_tier: TierLevel) -> int:
        """Calculate points needed for next tier"""
        try:
            tier_levels = list(TierLevel)
            current_index = tier_levels.index(current_tier)
            
            if current_index < len(tier_levels) - 1:
                next_tier = tier_levels[current_index + 1]
                return self.tier_thresholds[next_tier] - total_points
            
            return 0  # Already at max tier
        except Exception:
            return 0
    
    async def redeem_reward(self, user_id: str, reward_id: str) -> bool:
        """Redeem reward with points"""
        try:
            reward = self.rewards_store.get(reward_id)
            if not reward or not reward.is_active:
                return False
            
            user_points = self.user_points_store.get(user_id)
            if not user_points or user_points.total_points < reward.cost:
                return False
            
            # Check availability
            if reward.is_limited and reward.claimed_count >= (reward.total_available or 0):
                return False
            
            # Check expiry
            if reward.expires_at and datetime.utcnow() > reward.expires_at:
                return False
            
            # Deduct points
            user_points.total_points -= reward.cost
            user_points.last_updated = datetime.utcnow()
            
            # Create user reward
            user_reward = UserReward(
                user_reward_id=str(uuid.uuid4()),
                user_id=user_id,
                reward_id=reward_id
            )
            
            if user_id not in self.user_rewards_store:
                self.user_rewards_store[user_id] = []
            
            self.user_rewards_store[user_id].append(user_reward)
            reward.claimed_count += 1
            
            logger.info(f"User {user_id} redeemed reward {reward.name}")
            return True
        except Exception as e:
            logger.error(f"Reward redemption error: {e}")
            return False
    
    async def get_user_points(self, user_id: str) -> UserPoints:
        """Get user points information"""
        try:
            if user_id not in self.user_points_store:
                self.user_points_store[user_id] = UserPoints(user_id=user_id)
            
            return self.user_points_store[user_id]
        except Exception as e:
            logger.error(f"User points retrieval error: {e}")
            return UserPoints(user_id=user_id)

class LeaderboardService:
    """Leaderboard and ranking service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        logger.info("🏅 Leaderboard Service initialized")
    
    async def get_leaderboard(self, leaderboard_type: LeaderboardType, limit: int = 50) -> List[LeaderboardEntry]:
        """Get leaderboard entries"""
        try:
            # Mock leaderboard data (in real implementation would query actual data)
            entries = []
            
            for i in range(min(limit, 20)):  # Generate mock data
                entry = LeaderboardEntry(
                    user_id=f"user_{i+1}",
                    username=f"Creator{i+1}",
                    avatar_url=f"https://example.com/avatar{i+1}.jpg",
                    score=1000 - (i * 50),
                    rank=i + 1,
                    tier=TierLevel.GOLD if i < 5 else TierLevel.SILVER if i < 15 else TierLevel.BRONZE,
                    badges_count=5 - (i // 5),
                    achievements_count=10 - (i // 2)
                )
                entries.append(entry)
            
            return entries
        except Exception as e:
            logger.error(f"Leaderboard retrieval error: {e}")
            return []
    
    async def get_user_rank(self, user_id: str, leaderboard_type: LeaderboardType) -> Optional[Dict[str, Any]]:
        """Get user's rank in leaderboard"""
        try:
            # Mock user rank data
            return {
                "user_id": user_id,
                "rank": 42,
                "score": 750,
                "tier": TierLevel.SILVER.value,
                "percentile": 85.5,
                "leaderboard_type": leaderboard_type.value
            }
        except Exception as e:
            logger.error(f"User rank retrieval error: {e}")
            return None

class GamificationService:
    """
    Unified Gamification Service that orchestrates all gamification-related services
    
    Consolidates:
    - Achievement System
    - Badge Management
    - Challenge System
    - Points & Rewards
    - Leaderboards
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize sub-services
        self.achievements = AchievementService(self.config.get('achievements', {}))
        self.badges = BadgeService(self.config.get('badges', {}))
        self.challenges = ChallengeService(self.config.get('challenges', {}))
        self.points_rewards = PointsRewardService(self.config.get('points_rewards', {}))
        self.leaderboards = LeaderboardService(self.config.get('leaderboards', {}))
        
        logger.info("🎮 Gamification Service initialized - All gamification-related services consolidated")
    
    async def initialize(self):
        """Initialize all gamification services"""
        logger.info("🚀 Initializing Gamification Service")
        # Any initialization logic here
    
    async def shutdown(self):
        """Shutdown all gamification services"""
        logger.info("🛑 Shutting down Gamification Service")
        # Any cleanup logic here
    
    async def process_user_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user event for all gamification systems"""
        try:
            results = {
                "user_id": user_id,
                "event_type": event_type,
                "achievements_completed": [],
                "challenges_completed": [],
                "badges_earned": [],
                "points_awarded": 0
            }
            
            # Check achievements
            completed_achievements = await self.achievements.check_achievement_progress(user_id, event_data)
            results["achievements_completed"] = completed_achievements
            
            # Check challenges
            completed_challenges = await self.challenges.update_challenge_progress(user_id, event_data)
            results["challenges_completed"] = completed_challenges
            
            # Award points and badges based on completed achievements/challenges
            total_points = 0
            badges_earned = []
            
            for achievement in completed_achievements:
                achievement_details = self.achievements.achievements_store.get(achievement.achievement_id)
                if achievement_details:
                    # Award points
                    total_points += achievement_details.points_value
                    
                    # Award badges from rewards
                    for reward in achievement_details.rewards:
                        if reward["type"] == "badge":
                            badge_awarded = await self.badges.award_badge(user_id, reward["value"])
                            if badge_awarded:
                                badges_earned.append(reward["value"])
            
            for challenge in completed_challenges:
                challenge_details = self.challenges.challenges_store.get(challenge.challenge_id)
                if challenge_details:
                    # Award rewards
                    for reward in challenge_details.rewards:
                        if reward["type"] == "points":
                            total_points += reward["value"]
                        elif reward["type"] == "badge":
                            badge_awarded = await self.badges.award_badge(user_id, reward["value"])
                            if badge_awarded:
                                badges_earned.append(reward["value"])
            
            # Award total points
            if total_points > 0:
                await self.points_rewards.award_points(user_id, total_points, event_type)
                results["points_awarded"] = total_points
            
            results["badges_earned"] = badges_earned
            
            return results
        except Exception as e:
            logger.error(f"User event processing error: {e}")
            return {"error": str(e)}
    
    # Achievement methods
    async def get_user_achievements(self, user_id: str, completed_only: bool = False) -> List[UserAchievement]:
        """Get user achievements"""
        return await self.achievements.get_user_achievements(user_id, completed_only)
    
    async def get_available_achievements(self, user_id: str) -> List[Achievement]:
        """Get available achievements"""
        return await self.achievements.get_available_achievements(user_id)
    
    # Badge methods
    async def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user badges"""
        return await self.badges.get_user_badges(user_id)
    
    # Challenge methods
    async def get_active_challenges(self) -> List[Challenge]:
        """Get active challenges"""
        return await self.challenges.get_active_challenges()
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join challenge"""
        return await self.challenges.join_challenge(user_id, challenge_id)
    
    # Points and rewards methods
    async def get_user_points(self, user_id: str) -> UserPoints:
        """Get user points"""
        return await self.points_rewards.get_user_points(user_id)
    
    async def redeem_reward(self, user_id: str, reward_id: str) -> bool:
        """Redeem reward"""
        return await self.points_rewards.redeem_reward(user_id, reward_id)
    
    # Leaderboard methods
    async def get_leaderboard(self, leaderboard_type: LeaderboardType, limit: int = 50) -> List[LeaderboardEntry]:
        """Get leaderboard"""
        return await self.leaderboards.get_leaderboard(leaderboard_type, limit)
    
    async def get_user_rank(self, user_id: str, leaderboard_type: LeaderboardType) -> Optional[Dict[str, Any]]:
        """Get user rank"""
        return await self.leaderboards.get_user_rank(user_id, leaderboard_type)
    
    # Summary methods
    async def get_user_gamification_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification summary for user"""
        try:
            user_points = await self.get_user_points(user_id)
            user_achievements = await self.get_user_achievements(user_id, completed_only=True)
            user_badges = await self.get_user_badges(user_id)
            user_rank = await self.get_user_rank(user_id, LeaderboardType.POINTS)
            
            return {
                "user_id": user_id,
                "points": {
                    "total": user_points.total_points,
                    "tier": user_points.current_tier.value,
                    "points_to_next_tier": user_points.points_to_next_tier
                },
                "achievements": {
                    "total_completed": len(user_achievements),
                    "recent_completions": [ua for ua in user_achievements if ua.completed_at and 
                                         ua.completed_at > datetime.utcnow() - timedelta(days=7)]
                },
                "badges": {
                    "total_earned": len(user_badges),
                    "categories": {}
                },
                "rank": user_rank,
                "summary_generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Gamification summary error: {e}")
            return {"error": str(e)}

# Export all classes
__all__ = [
    # Enums
    "AchievementType",
    "AchievementDifficulty",
    "BadgeCategory",
    "RewardType",
    "ChallengeType",
    "TierLevel",
    "LeaderboardType",
    
    # Data structures
    "Achievement",
    "UserAchievement",
    "Badge",
    "UserBadge",
    "Challenge",
    "UserChallenge",
    "UserPoints",
    "Reward",
    "UserReward",
    "LeaderboardEntry",
    
    # Services
    "AchievementService",
    "BadgeService",
    "ChallengeService",
    "PointsRewardService",
    "LeaderboardService",
    "GamificationService"
]

# Module initialization
logger.info(f"🎮 Gamification Service v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("🎯 Consolidated: gamification/ subdirectory modules into unified gamification system")