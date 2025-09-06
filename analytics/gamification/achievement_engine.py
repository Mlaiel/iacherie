"""Unified Achievement Engine - Enterprise Gamification System
===========================================================

Comprehensive unified achievement system combining general platform gamification
and specialized gaming achievements with sophisticated progress tracking,
achievement unlocking, and reward distribution with real-time analytics.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/achievement_engine.py
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
Achievement Tracking → Gaming Achievements → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================================================
# UNIFIED ENUMS AND TYPES
# ============================================================================

class AchievementTier(str, Enum):
    """Achievement difficulty tiers."""
    BRONZE = "bronze"
    SILVER = "silver" 
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class AchievementCategory(str, Enum):
    """Unified achievement categories."""
    # General Platform Categories
    CONTENT_CREATION = "content_creation"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PROTECTION = "protection"
    ENGAGEMENT = "engagement"
    COMMUNITY = "community"
    INNOVATION = "innovation"
    
    # Gaming-Specific Categories
    TYCOON_MASTERY = "tycoon_mastery"
    WEALTH_BUILDER = "wealth_builder"
    ASSET_COLLECTOR = "asset_collector"
    EFFICIENCY_EXPERT = "efficiency_expert"
    COMPETITIVE_CHAMPION = "competitive_champion"
    MILESTONE_HUNTER = "milestone_hunter"
    SPEED_RUNNER = "speed_runner"
    STRATEGIST = "strategist"
    COLLECTOR = "collector"
    SOCIAL_GAMER = "social_gamer"
    SEASONAL_CHAMPION = "seasonal_champion"
    RARE_ACHIEVER = "rare_achiever"


class AchievementType(str, Enum):
    """Types of achievements."""
    MILESTONE = "milestone"
    CUMULATIVE = "cumulative"
    STREAK = "streak"
    SPEED = "speed"
    EFFICIENCY = "efficiency"
    COLLECTION = "collection"
    COMPETITIVE = "competitive"
    HIDDEN = "hidden"
    SEASONAL = "seasonal"
    CHALLENGE = "challenge"


class AchievementStatus(str, Enum):
    """Achievement status."""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"
    CLAIMED = "claimed"
    EXPIRED = "expired"


class RewardType(str, Enum):
    """Types of rewards."""
    CREDITS = "credits"
    GAMING_GEMS = "gaming_gems"
    EXPERIENCE_POINTS = "experience_points"
    BADGES = "badges"
    TITLES = "titles"
    SPECIAL_ITEMS = "special_items"
    UNLOCKS = "unlocks"
    MULTIPLIERS = "multipliers"


# ============================================================================
# UNIFIED DATA STRUCTURES
# ============================================================================

@dataclass
class AchievementRequirement:
    """Unified achievement requirement."""
    requirement_id: str = field(default_factory=lambda: str(uuid4()))
    metric_key: str = ""
    required_value: Union[int, float, Decimal] = 0
    comparison_type: str = "greater_equal"  # greater_equal, equal, less_equal, between
    value_range: Optional[tuple] = None
    time_window_hours: Optional[int] = None
    description: str = ""
    weight: float = 1.0


@dataclass
class AchievementReward:
    """Unified achievement reward definition."""
    reward_id: str = field(default_factory=lambda: str(uuid4()))
    reward_type: RewardType = RewardType.CREDITS
    amount: Union[int, float, Decimal] = 0
    currency: str = "CREDITS"
    bonus_multiplier: float = 1.0
    special_items: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    unlocks: List[str] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Achievement:
    """Unified achievement definition."""
    achievement_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    title: str = ""
    description: str = ""
    category: AchievementCategory = AchievementCategory.CONTENT_CREATION
    tier: AchievementTier = AchievementTier.BRONZE
    achievement_type: AchievementType = AchievementType.MILESTONE
    requirements: List[AchievementRequirement] = field(default_factory=list)
    rewards: List[AchievementReward] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    icon_url: Optional[str] = None
    badge_image: Optional[str] = None
    points_value: int = 10
    rarity_score: float = 1.0
    is_hidden: bool = False
    is_seasonal: bool = False
    is_gaming: bool = False  # Flag to distinguish gaming achievements
    season_id: Optional[str] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    max_completions: int = 1
    completion_window_hours: Optional[int] = None
    unlock_message: str = ""
    nft_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserAchievementProgress:
    """Unified user progress tracking."""
    progress_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    achievement_id: str = ""
    status: AchievementStatus = AchievementStatus.AVAILABLE
    current_progress: Dict[str, Union[int, float, Decimal]] = field(default_factory=dict)
    completion_percentage: float = 0.0
    completions_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    streak_count: int = 0
    best_time: Optional[float] = None
    is_gaming_achievement: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserAchievementStats:
    """Comprehensive user achievement statistics."""
    user_id: str = ""
    # General stats
    total_achievements: int = 0
    completed_achievements: int = 0
    claimed_achievements: int = 0
    total_points: int = 0
    total_experience: int = 0
    rarity_score: float = 0.0
    
    # Category breakdowns
    categories_completed: Dict[AchievementCategory, int] = field(default_factory=dict)
    tier_completed: Dict[AchievementTier, int] = field(default_factory=dict)
    
    # Performance metrics
    completion_rate: float = 0.0
    average_completion_time: float = 0.0
    fastest_completion: Optional[float] = None
    longest_streak: int = 0
    
    # Gaming-specific stats
    gaming_achievements: int = 0
    gaming_points: int = 0
    gaming_gems: Decimal = Decimal('0')
    
    # Time-based stats
    seasonal_completions: int = 0
    hidden_discoveries: int = 0
    last_achievement_date: Optional[datetime] = None
    achievement_velocity: float = 0.0  # achievements per day
    
    # Social stats
    leaderboard_rank: Optional[int] = None
    badges_earned: List[str] = field(default_factory=list)
    titles_earned: List[str] = field(default_factory=list)


# ============================================================================
# UNIFIED ACHIEVEMENT ENGINE
# ============================================================================

class UnifiedAchievementEngine:
    """
    Unified achievement engine combining general platform gamification
    and specialized gaming achievements with comprehensive tracking.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.achievements: Dict[str, Achievement] = {}
        self.user_progress: Dict[str, Dict[str, UserAchievementProgress]] = {}
        self.user_stats: Dict[str, UserAchievementStats] = {}
        self.achievement_templates: Dict[str, Dict[str, Any]] = {}
        self.seasonal_achievements: Dict[str, List[str]] = {}
        self.hidden_achievements: List[str] = []
        
        # Gaming-specific storage
        self.gaming_achievements: Dict[str, Achievement] = {}
        self.gaming_templates: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_achievement_templates()
        logger.info("🏆 Unified Achievement Engine initialized")
    
    def _initialize_achievement_templates(self):
        """Initialize both general and gaming achievement templates."""
        
        # General Platform Achievement Templates
        self.achievement_templates.update({
            "first_upload": {
                "name": "First Creator",
                "description": "Upload your first piece of content",
                "category": AchievementCategory.CONTENT_CREATION,
                "tier": AchievementTier.BRONZE,
                "points": 10,
                "requirements": [{"metric_key": "content_uploads", "required_value": 1}],
                "rewards": [{"reward_type": "credits", "amount": 100}]
            },
            "viral_hit": {
                "name": "Viral Star",
                "description": "Achieve 1 million views/listens",
                "category": AchievementCategory.ENGAGEMENT,
                "tier": AchievementTier.GOLD,
                "points": 100,
                "requirements": [{"metric_key": "total_views", "required_value": 1000000}],
                "rewards": [{"reward_type": "credits", "amount": 5000}]
            },
            "collaboration_master": {
                "name": "Collaboration Master",
                "description": "Complete 10 successful collaborations",
                "category": AchievementCategory.COLLABORATION,
                "tier": AchievementTier.SILVER,
                "points": 50,
                "requirements": [{"metric_key": "collaborations_completed", "required_value": 10}],
                "rewards": [{"reward_type": "credits", "amount": 1000}]
            }
        })
        
        # Gaming Achievement Templates
        self.gaming_templates.update({
            "tycoon_starter": {
                "name": "Tycoon Starter",
                "description": "Purchase your first asset in Influencer Tycoon",
                "category": AchievementCategory.TYCOON_MASTERY,
                "tier": AchievementTier.BRONZE,
                "points": 15,
                "is_gaming": True,
                "requirements": [{"metric_key": "assets_purchased", "required_value": 1}],
                "rewards": [{"reward_type": "gaming_gems", "amount": 50}]
            },
            "wealth_builder": {
                "name": "Wealth Builder",
                "description": "Accumulate 1 million in tycoon cash",
                "category": AchievementCategory.WEALTH_BUILDER,
                "tier": AchievementTier.GOLD,
                "points": 75,
                "is_gaming": True,
                "requirements": [{"metric_key": "total_cash", "required_value": 1000000}],
                "rewards": [{"reward_type": "gaming_gems", "amount": 500}]
            },
            "efficiency_expert": {
                "name": "Efficiency Expert",
                "description": "Upgrade 5 assets to maximum efficiency",
                "category": AchievementCategory.EFFICIENCY_EXPERT,
                "tier": AchievementTier.PLATINUM,
                "points": 100,
                "is_gaming": True,
                "requirements": [{"metric_key": "max_efficiency_assets", "required_value": 5}],
                "rewards": [{"reward_type": "gaming_gems", "amount": 1000}]
            }
        })
    
    async def create_achievement(self, achievement_data: Dict[str, Any]) -> Achievement:
        """Create a new achievement from template or custom data."""
        try:
            # Use template if specified
            template_id = achievement_data.get('template_id')
            if template_id:
                templates = self.gaming_templates if achievement_data.get('is_gaming') else self.achievement_templates
                template = templates.get(template_id, {})
                achievement_data = {**template, **achievement_data}
            
            # Create requirements
            requirements = []
            for req_data in achievement_data.get('requirements', []):
                requirement = AchievementRequirement(
                    metric_key=req_data.get('metric_key', ''),
                    required_value=req_data.get('required_value', 0),
                    comparison_type=req_data.get('comparison_type', 'greater_equal'),
                    description=req_data.get('description', ''),
                    weight=req_data.get('weight', 1.0)
                )
                requirements.append(requirement)
            
            # Create rewards
            rewards = []
            for reward_data in achievement_data.get('rewards', []):
                reward = AchievementReward(
                    reward_type=RewardType(reward_data.get('reward_type', 'credits')),
                    amount=reward_data.get('amount', 0),
                    currency=reward_data.get('currency', 'CREDITS'),
                    description=reward_data.get('description', ''),
                    badges=reward_data.get('badges', []),
                    titles=reward_data.get('titles', [])
                )
                rewards.append(reward)
            
            # Create achievement
            achievement = Achievement(
                name=achievement_data.get('name', ''),
                title=achievement_data.get('title', ''),
                description=achievement_data.get('description', ''),
                category=AchievementCategory(achievement_data.get('category', 'content_creation')),
                tier=AchievementTier(achievement_data.get('tier', 'bronze')),
                achievement_type=AchievementType(achievement_data.get('achievement_type', 'milestone')),
                requirements=requirements,
                rewards=rewards,
                points_value=achievement_data.get('points', 10),
                is_gaming=achievement_data.get('is_gaming', False),
                is_hidden=achievement_data.get('is_hidden', False),
                is_seasonal=achievement_data.get('is_seasonal', False)
            )
            
            # Store achievement
            self.achievements[achievement.achievement_id] = achievement
            
            if achievement.is_gaming:
                self.gaming_achievements[achievement.achievement_id] = achievement
            
            if achievement.is_hidden:
                self.hidden_achievements.append(achievement.achievement_id)
            
            logger.info(f"Created achievement: {achievement.name} ({achievement.achievement_id})")
            return achievement
            
        except Exception as e:
            logger.error(f"Error creating achievement: {e}")
            raise
    
    async def track_user_action(self, user_id: str, action_type: str, 
                               metrics: Dict[str, Union[int, float, Decimal]]) -> List[str]:
        """Track user action and check for achievement unlocks."""
        try:
            unlocked_achievements = []
            
            # Initialize user data if needed
            if user_id not in self.user_progress:
                self.user_progress[user_id] = {}
                self.user_stats[user_id] = UserAchievementStats(user_id=user_id)
            
            # Check all achievements for potential unlocks
            for achievement_id, achievement in self.achievements.items():
                
                # Skip if user already completed this achievement (unless repeatable)
                progress = self.user_progress[user_id].get(achievement_id)
                if progress and progress.status == AchievementStatus.COMPLETED:
                    if achievement.max_completions <= progress.completions_count:
                        continue
                
                # Initialize progress if needed
                if not progress:
                    progress = UserAchievementProgress(
                        user_id=user_id,
                        achievement_id=achievement_id,
                        is_gaming_achievement=achievement.is_gaming,
                        status=AchievementStatus.AVAILABLE if not achievement.is_hidden else AchievementStatus.LOCKED
                    )
                    self.user_progress[user_id][achievement_id] = progress
                
                # Check if user meets requirements
                unlock_result = await self._check_achievement_unlock(user_id, achievement, metrics)
                
                if unlock_result["unlocked"]:
                    await self._unlock_achievement(user_id, achievement_id)
                    unlocked_achievements.append(achievement_id)
                elif unlock_result["progress_updated"]:
                    progress.current_progress.update(unlock_result.get("progress", {}))
                    progress.completion_percentage = unlock_result.get("completion_percentage", 0)
                    progress.last_updated = datetime.now(timezone.utc)
            
            # Update user stats
            await self._update_user_stats(user_id)
            
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Error tracking user action: {e}")
            return []
    
    async def _check_achievement_unlock(self, user_id: str, achievement: Achievement, 
                                      current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check if achievement can be unlocked with current metrics."""
        try:
            progress = self.user_progress[user_id].get(achievement.achievement_id)
            if not progress:
                return {"unlocked": False, "progress_updated": False}
            
            total_requirements = len(achievement.requirements)
            met_requirements = 0
            progress_data = {}
            
            for requirement in achievement.requirements:
                metric_value = current_metrics.get(requirement.metric_key, 0)
                progress_data[requirement.metric_key] = metric_value
                
                # Check if requirement is met
                if requirement.comparison_type == "greater_equal":
                    if metric_value >= requirement.required_value:
                        met_requirements += 1
                elif requirement.comparison_type == "equal":
                    if metric_value == requirement.required_value:
                        met_requirements += 1
                elif requirement.comparison_type == "less_equal":
                    if metric_value <= requirement.required_value:
                        met_requirements += 1
            
            completion_percentage = (met_requirements / total_requirements) * 100 if total_requirements > 0 else 0
            unlocked = met_requirements == total_requirements
            
            return {
                "unlocked": unlocked,
                "progress_updated": True,
                "progress": progress_data,
                "completion_percentage": completion_percentage,
                "met_requirements": met_requirements,
                "total_requirements": total_requirements
            }
            
        except Exception as e:
            logger.error(f"Error checking achievement unlock: {e}")
            return {"unlocked": False, "progress_updated": False}
    
    async def _unlock_achievement(self, user_id: str, achievement_id: str):
        """Unlock an achievement for a user."""
        try:
            achievement = self.achievements.get(achievement_id)
            progress = self.user_progress[user_id].get(achievement_id)
            
            if not achievement or not progress:
                return
            
            # Update progress status
            progress.status = AchievementStatus.COMPLETED
            progress.completed_at = datetime.now(timezone.utc)
            progress.completions_count += 1
            progress.completion_percentage = 100.0
            
            # Award rewards
            total_credits = 0
            total_gems = 0
            total_experience = 0
            
            for reward in achievement.rewards:
                if reward.reward_type == RewardType.CREDITS:
                    total_credits += int(reward.amount)
                elif reward.reward_type == RewardType.GAMING_GEMS:
                    total_gems += int(reward.amount)
                elif reward.reward_type == RewardType.EXPERIENCE_POINTS:
                    total_experience += int(reward.amount)
            
            # Update user stats
            stats = self.user_stats[user_id]
            stats.completed_achievements += 1
            stats.total_points += achievement.points_value
            stats.total_experience += total_experience
            
            if achievement.is_gaming:
                stats.gaming_achievements += 1
                stats.gaming_points += achievement.points_value
                stats.gaming_gems += Decimal(str(total_gems))
            
            stats.last_achievement_date = datetime.now(timezone.utc)
            
            # Add badges and titles
            for reward in achievement.rewards:
                stats.badges_earned.extend(reward.badges)
                stats.titles_earned.extend(reward.titles)
            
            logger.info(f"🏆 Achievement unlocked: {achievement.name} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error unlocking achievement: {e}")
    
    async def _update_user_stats(self, user_id: str):
        """Update comprehensive user achievement statistics."""
        try:
            stats = self.user_stats[user_id]
            progress_data = self.user_progress[user_id]
            
            # Calculate completion rate
            total_available = len([a for a in self.achievements.values() if not a.is_hidden])
            completed = len([p for p in progress_data.values() if p.status == AchievementStatus.COMPLETED])
            
            stats.total_achievements = total_available
            stats.completed_achievements = completed
            stats.completion_rate = (completed / total_available) * 100 if total_available > 0 else 0
            
            # Calculate category completions
            stats.categories_completed.clear()
            stats.tier_completed.clear()
            
            for progress in progress_data.values():
                if progress.status == AchievementStatus.COMPLETED:
                    achievement = self.achievements.get(progress.achievement_id)
                    if achievement:
                        category_count = stats.categories_completed.get(achievement.category, 0)
                        stats.categories_completed[achievement.category] = category_count + 1
                        
                        tier_count = stats.tier_completed.get(achievement.tier, 0)
                        stats.tier_completed[achievement.tier] = tier_count + 1
            
            # Calculate rarity score
            stats.rarity_score = sum(
                self.achievements[p.achievement_id].rarity_score 
                for p in progress_data.values() 
                if p.status == AchievementStatus.COMPLETED and p.achievement_id in self.achievements
            )
            
            # Calculate achievement velocity (achievements per day)
            if stats.last_achievement_date:
                days_active = (datetime.now(timezone.utc) - stats.last_achievement_date).days or 1
                stats.achievement_velocity = completed / days_active
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
    
    async def get_user_achievements(self, user_id: str, include_hidden: bool = False) -> Dict[str, Any]:
        """Get comprehensive user achievement data."""
        try:
            if user_id not in self.user_stats:
                return {"error": "User not found"}
            
            stats = self.user_stats[user_id]
            progress_data = self.user_progress.get(user_id, {})
            
            # Get achievement details with progress
            achievements_with_progress = []
            for achievement_id, achievement in self.achievements.items():
                if achievement.is_hidden and not include_hidden:
                    continue
                
                progress = progress_data.get(achievement_id)
                achievement_data = {
                    "achievement": achievement,
                    "progress": progress,
                    "completion_percentage": progress.completion_percentage if progress else 0,
                    "status": progress.status.value if progress else "locked"
                }
                achievements_with_progress.append(achievement_data)
            
            return {
                "user_id": user_id,
                "stats": stats,
                "achievements": achievements_with_progress,
                "gaming_achievements": [a for a in achievements_with_progress if a["achievement"].is_gaming],
                "platform_achievements": [a for a in achievements_with_progress if not a["achievement"].is_gaming],
                "recent_completions": sorted([
                    a for a in achievements_with_progress 
                    if a["progress"] and a["progress"].completed_at
                ], key=lambda x: x["progress"].completed_at, reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Error getting user achievements: {e}")
            return {"error": str(e)}
    
    async def claim_achievement_rewards(self, user_id: str, achievement_id: str) -> Dict[str, Any]:
        """Claim rewards for a completed achievement."""
        try:
            progress = self.user_progress[user_id].get(achievement_id)
            achievement = self.achievements.get(achievement_id)
            
            if not progress or not achievement:
                return {"success": False, "message": "Achievement not found"}
            
            if progress.status != AchievementStatus.COMPLETED:
                return {"success": False, "message": "Achievement not completed"}
            
            if progress.claimed_at:
                return {"success": False, "message": "Rewards already claimed"}
            
            # Mark as claimed
            progress.claimed_at = datetime.now(timezone.utc)
            progress.status = AchievementStatus.CLAIMED
            
            # Calculate total rewards
            rewards_summary = {
                "credits": 0,
                "gaming_gems": 0,
                "experience_points": 0,
                "badges": [],
                "titles": [],
                "special_items": []
            }
            
            for reward in achievement.rewards:
                if reward.reward_type == RewardType.CREDITS:
                    rewards_summary["credits"] += int(reward.amount)
                elif reward.reward_type == RewardType.GAMING_GEMS:
                    rewards_summary["gaming_gems"] += int(reward.amount)
                elif reward.reward_type == RewardType.EXPERIENCE_POINTS:
                    rewards_summary["experience_points"] += int(reward.amount)
                
                rewards_summary["badges"].extend(reward.badges)
                rewards_summary["titles"].extend(reward.titles)
                rewards_summary["special_items"].extend(reward.special_items)
            
            # Update user stats
            stats = self.user_stats[user_id]
            stats.claimed_achievements += 1
            
            logger.info(f"💎 User {user_id} claimed rewards for achievement: {achievement.name}")
            
            return {
                "success": True,
                "achievement": achievement,
                "rewards": rewards_summary,
                "message": f"Claimed rewards for {achievement.name}"
            }
            
        except Exception as e:
            logger.error(f"Error claiming achievement rewards: {e}")
            return {"success": False, "message": str(e)}


# Global instance
_achievement_engine_instance: Optional[UnifiedAchievementEngine] = None


def get_achievement_engine() -> UnifiedAchievementEngine:
    """Get the global unified achievement engine instance."""
    global _achievement_engine_instance
    if _achievement_engine_instance is None:
        _achievement_engine_instance = UnifiedAchievementEngine()
    return _achievement_engine_instance


async def track_user_action(user_id: str, action_type: str, metrics: Dict[str, Any]) -> List[str]:
    """Track user action and return unlocked achievements."""
    engine = get_achievement_engine()
    return await engine.track_user_action(user_id, action_type, metrics)


async def get_user_achievements(user_id: str, include_hidden: bool = False) -> Dict[str, Any]:
    """Get user achievements and progress."""
    engine = get_achievement_engine()
    return await engine.get_user_achievements(user_id, include_hidden)
