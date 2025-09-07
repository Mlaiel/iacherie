# -*- coding: utf-8 -*-
"""Gamification-Monetization Bridge - IA Influencer Agent Platform
================================================================

Enterprise bridge connecting gamification systems with monetization rewards,
enabling achievement-based monetary rewards, engagement monetization, loyalty
program integration, and milestone-based revenue multipliers.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/gamification_monetization_bridge.py
Business Logic: Gamification → Achievement Rewards → Monetization → Creator Incentives

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

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from uuid import UUID, uuid4

import aiohttp
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, DECIMAL, JSON
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
logger = logging.getLogger(__name__)

Base = declarative_base()


class AchievementType(str, Enum):
    """Types of achievements that can earn monetary rewards."""
    CONTENT_MILESTONE = "content_milestone"
    ENGAGEMENT_THRESHOLD = "engagement_threshold"
    REVENUE_TARGET = "revenue_target"
    COLLABORATION_SUCCESS = "collaboration_success"
    PROTECTION_EFFICIENCY = "protection_efficiency"
    SEO_PERFORMANCE = "seo_performance"
    COMMUNITY_BUILDING = "community_building"
    CONSISTENCY_STREAK = "consistency_streak"
    QUALITY_SCORE = "quality_score"
    INNOVATION_BONUS = "innovation_bonus"


class RewardType(str, Enum):
    """Types of monetary rewards for achievements."""
    CASH_BONUS = "cash_bonus"
    REVENUE_MULTIPLIER = "revenue_multiplier"
    PLATFORM_CREDITS = "platform_credits"
    PREMIUM_FEATURES = "premium_features"
    REDUCED_FEES = "reduced_fees"
    COLLABORATION_BOOST = "collaboration_boost"
    PRIORITY_SUPPORT = "priority_support"
    MARKETING_BOOST = "marketing_boost"


class RewardStatus(str, Enum):
    """Status of reward redemption."""
    EARNED = "earned"
    PENDING_VERIFICATION = "pending_verification"
    APPROVED = "approved"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


class LoyaltyTier(str, Enum):
    """Loyalty program tiers with different benefits."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    ELITE = "elite"


@dataclass
class Achievement:
    """Achievement definition with monetization potential."""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    criteria: Dict[str, Any]
    reward_type: RewardType
    reward_value: Decimal
    reward_duration_days: Optional[int] = None
    max_redemptions: Optional[int] = None
    tier_requirement: Optional[LoyaltyTier] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserAchievement:
    """User's earned achievement with reward details."""
    user_achievement_id: str
    user_id: str
    achievement_id: str
    earned_at: datetime
    status: RewardStatus
    reward_value: Decimal
    reward_applied_at: Optional[datetime] = None
    reward_expires_at: Optional[datetime] = None
    verification_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoyaltyProgram:
    """Loyalty program configuration."""
    program_id: str
    name: str
    tier_requirements: Dict[LoyaltyTier, Dict[str, Any]]
    tier_benefits: Dict[LoyaltyTier, Dict[str, Any]]
    points_per_dollar: Decimal = Decimal('1.0')
    revenue_multipliers: Dict[LoyaltyTier, Decimal] = field(default_factory=dict)
    fee_discounts: Dict[LoyaltyTier, Decimal] = field(default_factory=dict)


@dataclass
class EngagementMetrics:
    """User engagement metrics for gamification."""
    user_id: str
    content_count: int = 0
    total_views: int = 0
    total_engagement: int = 0
    revenue_generated: Decimal = Decimal('0.00')
    collaborations_completed: int = 0
    protection_score: Decimal = Decimal('0.00')
    consistency_days: int = 0
    quality_score: Decimal = Decimal('0.00')
    last_updated: datetime = field(default_factory=datetime.utcnow)


class GamificationMonetizationBridge:
    """
    Enterprise bridge integrating gamification with monetization rewards.
    
    Capabilities:
    - Achievement-based monetary rewards
    - Engagement-driven revenue multipliers
    - Loyalty program monetization
    - Milestone bonus calculations
    - Competition prize management
    - Level-based revenue enhancements
    """
    
    def __init__(
        self,
        api_base_url: str = "https://api.ainflue.com/v1",
        enable_auto_rewards: bool = True,
        max_reward_per_user_daily: Decimal = Decimal('100.00'),
        loyalty_program_enabled: bool = True
    ):
        """Initialize Gamification-Monetization Bridge."""
        self.api_base_url = api_base_url
        self.enable_auto_rewards = enable_auto_rewards
        self.max_reward_per_user_daily = max_reward_per_user_daily
        self.loyalty_program_enabled = loyalty_program_enabled
        
        # Active achievements and rewards
        self.active_achievements: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, List[UserAchievement]] = {}
        self.user_engagement_metrics: Dict[str, EngagementMetrics] = {}
        self.daily_reward_tracking: Dict[str, Dict[str, Decimal]] = {}  # user_id -> date -> amount
        
        # Initialize default achievements
        self._initialize_default_achievements()
        
        # Initialize loyalty program
        self.loyalty_program = self._initialize_loyalty_program()
        
        logger.info("🎮💰 Gamification-Monetization Bridge initialized")
    
    def _initialize_default_achievements(self) -> None:
        """Initialize default achievements with monetary rewards."""
        default_achievements = [
            Achievement(
                achievement_id="first_content",
                name="First Content Creator",
                description="Upload your first piece of content",
                achievement_type=AchievementType.CONTENT_MILESTONE,
                criteria={"content_count": 1},
                reward_type=RewardType.CASH_BONUS,
                reward_value=Decimal('5.00')
            ),
            Achievement(
                achievement_id="viral_content",
                name="Viral Success",
                description="Achieve 100K+ views on a single content",
                achievement_type=AchievementType.ENGAGEMENT_THRESHOLD,
                criteria={"single_content_views": 100000},
                reward_type=RewardType.CASH_BONUS,
                reward_value=Decimal('50.00')
            ),
            Achievement(
                achievement_id="revenue_milestone_100",
                name="First $100 Revenue",
                description="Generate your first $100 in revenue",
                achievement_type=AchievementType.REVENUE_TARGET,
                criteria={"total_revenue": 100.00},
                reward_type=RewardType.REVENUE_MULTIPLIER,
                reward_value=Decimal('1.10'),  # 10% bonus
                reward_duration_days=30
            ),
            Achievement(
                achievement_id="consistency_streak_30",
                name="Consistency Champion",
                description="Upload content for 30 consecutive days",
                achievement_type=AchievementType.CONSISTENCY_STREAK,
                criteria={"consecutive_days": 30},
                reward_type=RewardType.REDUCED_FEES,
                reward_value=Decimal('0.50'),  # 50% fee reduction
                reward_duration_days=90
            ),
            Achievement(
                achievement_id="collaboration_master",
                name="Collaboration Master",
                description="Complete 10 successful collaborations",
                achievement_type=AchievementType.COLLABORATION_SUCCESS,
                criteria={"collaborations_completed": 10},
                reward_type=RewardType.COLLABORATION_BOOST,
                reward_value=Decimal('25.00'),
                reward_duration_days=60
            ),
            Achievement(
                achievement_id="protection_champion",
                name="Protection Champion",
                description="Maintain 95%+ protection efficiency",
                achievement_type=AchievementType.PROTECTION_EFFICIENCY,
                criteria={"protection_score": 0.95},
                reward_type=RewardType.CASH_BONUS,
                reward_value=Decimal('75.00')
            ),
            Achievement(
                achievement_id="seo_optimizer",
                name="SEO Optimization Expert",
                description="Achieve top 3 ranking for target keywords",
                achievement_type=AchievementType.SEO_PERFORMANCE,
                criteria={"seo_ranking_top3": 5},
                reward_type=RewardType.MARKETING_BOOST,
                reward_value=Decimal('100.00'),
                reward_duration_days=30
            ),
            Achievement(
                achievement_id="quality_perfectionist",
                name="Quality Perfectionist",
                description="Maintain 4.8+ quality score for 50+ content pieces",
                achievement_type=AchievementType.QUALITY_SCORE,
                criteria={"quality_score": 4.8, "content_count": 50},
                reward_type=RewardType.PREMIUM_FEATURES,
                reward_value=Decimal('200.00'),
                reward_duration_days=180
            )
        ]
        
        for achievement in default_achievements:
            self.active_achievements[achievement.achievement_id] = achievement
    
    def _initialize_loyalty_program(self) -> LoyaltyProgram:
        """Initialize loyalty program with tier-based benefits."""
        tier_requirements = {
            LoyaltyTier.BRONZE: {"revenue": 0, "content_count": 0},
            LoyaltyTier.SILVER: {"revenue": 500, "content_count": 10},
            LoyaltyTier.GOLD: {"revenue": 2000, "content_count": 25},
            LoyaltyTier.PLATINUM: {"revenue": 10000, "content_count": 100},
            LoyaltyTier.DIAMOND: {"revenue": 50000, "content_count": 500},
            LoyaltyTier.ELITE: {"revenue": 200000, "content_count": 1000}
        }
        
        tier_benefits = {
            LoyaltyTier.BRONZE: {"fee_discount": 0.0, "revenue_multiplier": 1.0},
            LoyaltyTier.SILVER: {"fee_discount": 0.05, "revenue_multiplier": 1.05},
            LoyaltyTier.GOLD: {"fee_discount": 0.10, "revenue_multiplier": 1.10},
            LoyaltyTier.PLATINUM: {"fee_discount": 0.15, "revenue_multiplier": 1.15},
            LoyaltyTier.DIAMOND: {"fee_discount": 0.20, "revenue_multiplier": 1.25},
            LoyaltyTier.ELITE: {"fee_discount": 0.25, "revenue_multiplier": 1.35}
        }
        
        revenue_multipliers = {
            tier: Decimal(str(benefits["revenue_multiplier"]))
            for tier, benefits in tier_benefits.items()
        }
        
        fee_discounts = {
            tier: Decimal(str(benefits["fee_discount"]))
            for tier, benefits in tier_benefits.items()
        }
        
        return LoyaltyProgram(
            program_id="ainflue_loyalty",
            name="Ainflue Creator Loyalty Program",
            tier_requirements=tier_requirements,
            tier_benefits=tier_benefits,
            points_per_dollar=Decimal('1.0'),
            revenue_multipliers=revenue_multipliers,
            fee_discounts=fee_discounts
        )
    
    async def process_user_activity(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user activity for achievement detection and reward calculation.
        
        Args:
            user_id: User identifier
            activity_data: Activity metrics and events
            
        Returns:
            Dict containing earned achievements and rewards
        """
        try:
            # Update user engagement metrics
            await self._update_user_engagement_metrics(user_id, activity_data)
            
            # Check for earned achievements
            earned_achievements = await self._check_achievements(user_id)
            
            # Process earned rewards
            processed_rewards = []
            for achievement in earned_achievements:
                reward = await self._process_achievement_reward(user_id, achievement)
                if reward:
                    processed_rewards.append(reward)
            
            # Update loyalty tier
            new_tier = await self._update_loyalty_tier(user_id)
            
            # Calculate current active multipliers
            active_multipliers = await self._calculate_active_multipliers(user_id)
            
            result = {
                "user_id": user_id,
                "earned_achievements": [
                    {
                        "achievement_id": ach.achievement_id,
                        "name": ach.name,
                        "reward_type": ach.reward_type.value,
                        "reward_value": float(ach.reward_value)
                    }
                    for ach in earned_achievements
                ],
                "processed_rewards": processed_rewards,
                "loyalty_tier": new_tier.value if new_tier else None,
                "active_multipliers": active_multipliers,
                "total_rewards_today": float(await self._get_daily_rewards_total(user_id)),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"🎮 User activity processed: {user_id}, "
                       f"Achievements: {len(earned_achievements)}, "
                       f"Rewards: {len(processed_rewards)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing user activity: {e}")
            raise
    
    async def _update_user_engagement_metrics(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> None:
        """Update user engagement metrics with new activity data."""
        try:
            if user_id not in self.user_engagement_metrics:
                self.user_engagement_metrics[user_id] = EngagementMetrics(user_id=user_id)
            
            metrics = self.user_engagement_metrics[user_id]
            
            # Update metrics based on activity data
            if "content_uploaded" in activity_data:
                metrics.content_count += 1
            
            if "views_gained" in activity_data:
                metrics.total_views += activity_data["views_gained"]
            
            if "engagement_gained" in activity_data:
                metrics.total_engagement += activity_data["engagement_gained"]
            
            if "revenue_earned" in activity_data:
                metrics.revenue_generated += Decimal(str(activity_data["revenue_earned"]))
            
            if "collaboration_completed" in activity_data:
                metrics.collaborations_completed += 1
            
            if "protection_score" in activity_data:
                metrics.protection_score = Decimal(str(activity_data["protection_score"]))
            
            if "quality_score" in activity_data:
                metrics.quality_score = Decimal(str(activity_data["quality_score"]))
            
            # Update consistency tracking
            if "content_uploaded" in activity_data:
                await self._update_consistency_streak(user_id)
            
            metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Error updating engagement metrics: {e}")
    
    async def _check_achievements(self, user_id: str) -> List[Achievement]:
        """Check for newly earned achievements."""
        try:
            earned_achievements = []
            metrics = self.user_engagement_metrics.get(user_id)
            if not metrics:
                return earned_achievements
            
            # Get user's existing achievements to avoid duplicates
            existing_achievement_ids = {
                ua.achievement_id
                for ua in self.user_achievements.get(user_id, [])
            }
            
            for achievement in self.active_achievements.values():
                if not achievement.active:
                    continue
                
                if achievement.achievement_id in existing_achievement_ids:
                    continue
                
                # Check if achievement criteria are met
                if await self._check_achievement_criteria(achievement, metrics):
                    earned_achievements.append(achievement)
            
            return earned_achievements
            
        except Exception as e:
            logger.error(f"❌ Error checking achievements: {e}")
            return []
    
    async def _check_achievement_criteria(
        self,
        achievement: Achievement,
        metrics: EngagementMetrics
    ) -> bool:
        """Check if achievement criteria are met."""
        try:
            criteria = achievement.criteria
            
            if achievement.achievement_type == AchievementType.CONTENT_MILESTONE:
                return metrics.content_count >= criteria.get("content_count", 0)
            
            elif achievement.achievement_type == AchievementType.ENGAGEMENT_THRESHOLD:
                if "single_content_views" in criteria:
                    # This would need more sophisticated tracking in real implementation
                    return metrics.total_views >= criteria["single_content_views"]
                return metrics.total_engagement >= criteria.get("total_engagement", 0)
            
            elif achievement.achievement_type == AchievementType.REVENUE_TARGET:
                return metrics.revenue_generated >= Decimal(str(criteria.get("total_revenue", 0)))
            
            elif achievement.achievement_type == AchievementType.COLLABORATION_SUCCESS:
                return metrics.collaborations_completed >= criteria.get("collaborations_completed", 0)
            
            elif achievement.achievement_type == AchievementType.PROTECTION_EFFICIENCY:
                return metrics.protection_score >= Decimal(str(criteria.get("protection_score", 0)))
            
            elif achievement.achievement_type == AchievementType.CONSISTENCY_STREAK:
                return metrics.consistency_days >= criteria.get("consecutive_days", 0)
            
            elif achievement.achievement_type == AchievementType.QUALITY_SCORE:
                return (metrics.quality_score >= Decimal(str(criteria.get("quality_score", 0))) and
                        metrics.content_count >= criteria.get("content_count", 0))
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking achievement criteria: {e}")
            return False
    
    async def _process_achievement_reward(
        self,
        user_id: str,
        achievement: Achievement
    ) -> Optional[Dict[str, Any]]:
        """Process reward for earned achievement."""
        try:
            # Check daily reward limit
            daily_total = await self._get_daily_rewards_total(user_id)
            if daily_total + achievement.reward_value > self.max_reward_per_user_daily:
                logger.warning(f"⚠️ Daily reward limit exceeded for {user_id}")
                return None
            
            # Create user achievement record
            user_achievement_id = str(uuid4())
            user_achievement = UserAchievement(
                user_achievement_id=user_achievement_id,
                user_id=user_id,
                achievement_id=achievement.achievement_id,
                earned_at=datetime.utcnow(),
                status=RewardStatus.APPROVED if self.enable_auto_rewards else RewardStatus.PENDING_VERIFICATION,
                reward_value=achievement.reward_value,
                reward_expires_at=datetime.utcnow() + timedelta(days=achievement.reward_duration_days) if achievement.reward_duration_days else None
            )
            
            # Store user achievement
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = []
            self.user_achievements[user_id].append(user_achievement)
            
            # Apply reward if auto-rewards enabled
            reward_applied = False
            if self.enable_auto_rewards:
                reward_applied = await self._apply_achievement_reward(user_achievement, achievement)
                if reward_applied:
                    user_achievement.status = RewardStatus.REDEEMED
                    user_achievement.reward_applied_at = datetime.utcnow()
            
            # Track daily rewards
            await self._track_daily_reward(user_id, achievement.reward_value)
            
            # Log achievement earned
            await self._log_achievement_event(user_achievement, achievement, "achievement_earned")
            
            return {
                "user_achievement_id": user_achievement_id,
                "achievement_id": achievement.achievement_id,
                "achievement_name": achievement.name,
                "reward_type": achievement.reward_type.value,
                "reward_value": float(achievement.reward_value),
                "status": user_achievement.status.value,
                "reward_applied": reward_applied,
                "expires_at": user_achievement.reward_expires_at.isoformat() if user_achievement.reward_expires_at else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing achievement reward: {e}")
            return None
    
    async def _apply_achievement_reward(
        self,
        user_achievement: UserAchievement,
        achievement: Achievement
    ) -> bool:
        """Apply the actual reward to user account."""
        try:
            if achievement.reward_type == RewardType.CASH_BONUS:
                # Process cash payment
                success = await self._process_cash_bonus(
                    user_achievement.user_id, achievement.reward_value
                )
            
            elif achievement.reward_type == RewardType.PLATFORM_CREDITS:
                # Add platform credits
                success = await self._add_platform_credits(
                    user_achievement.user_id, achievement.reward_value
                )
            
            elif achievement.reward_type in [
                RewardType.REVENUE_MULTIPLIER,
                RewardType.REDUCED_FEES,
                RewardType.COLLABORATION_BOOST,
                RewardType.MARKETING_BOOST,
                RewardType.PREMIUM_FEATURES
            ]:
                # Activate time-limited benefit
                success = await self._activate_timed_benefit(
                    user_achievement.user_id, achievement
                )
            
            else:
                # Default to platform credits
                success = await self._add_platform_credits(
                    user_achievement.user_id, achievement.reward_value
                )
            
            if success:
                logger.info(f"💰 Reward applied: {user_achievement.user_id}, "
                           f"{achievement.reward_type.value}, ${achievement.reward_value}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error applying achievement reward: {e}")
            return False
    
    async def _process_cash_bonus(self, user_id: str, amount: Decimal) -> bool:
        """Process cash bonus payment to user."""
        try:
            # In real implementation, this would integrate with payment processor
            logger.info(f"💵 Cash bonus: {user_id}, ${amount}")
            return True
        except Exception as e:
            logger.error(f"❌ Cash bonus failed: {e}")
            return False
    
    async def _add_platform_credits(self, user_id: str, amount: Decimal) -> bool:
        """Add platform credits to user account."""
        try:
            # In real implementation, this would update user credit balance
            logger.info(f"🏆 Platform credits: {user_id}, ${amount}")
            return True
        except Exception as e:
            logger.error(f"❌ Platform credits failed: {e}")
            return False
    
    async def _activate_timed_benefit(self, user_id: str, achievement: Achievement) -> bool:
        """Activate time-limited benefit for user."""
        try:
            # In real implementation, this would register the benefit in user profile
            logger.info(f"⚡ Timed benefit activated: {user_id}, "
                       f"{achievement.reward_type.value}, {achievement.reward_duration_days} days")
            return True
        except Exception as e:
            logger.error(f"❌ Timed benefit activation failed: {e}")
            return False
    
    async def _update_loyalty_tier(self, user_id: str) -> Optional[LoyaltyTier]:
        """Update user's loyalty tier based on metrics."""
        try:
            if not self.loyalty_program_enabled:
                return None
            
            metrics = self.user_engagement_metrics.get(user_id)
            if not metrics:
                return None
            
            # Determine appropriate tier
            current_tier = LoyaltyTier.BRONZE
            for tier, requirements in self.loyalty_program.tier_requirements.items():
                if (metrics.revenue_generated >= Decimal(str(requirements["revenue"])) and
                    metrics.content_count >= requirements["content_count"]):
                    current_tier = tier
            
            # In real implementation, this would update user profile
            logger.debug(f"🏅 Loyalty tier: {user_id} -> {current_tier.value}")
            
            return current_tier
            
        except Exception as e:
            logger.error(f"❌ Error updating loyalty tier: {e}")
            return None
    
    async def _calculate_active_multipliers(self, user_id: str) -> Dict[str, float]:
        """Calculate currently active revenue multipliers for user."""
        try:
            multipliers = {"base": 1.0}
            
            # Get loyalty tier multiplier
            if self.loyalty_program_enabled:
                metrics = self.user_engagement_metrics.get(user_id)
                if metrics:
                    tier = await self._update_loyalty_tier(user_id)
                    if tier:
                        tier_multiplier = self.loyalty_program.revenue_multipliers.get(tier, Decimal('1.0'))
                        multipliers["loyalty_tier"] = float(tier_multiplier)
            
            # Get achievement-based multipliers
            user_achievements = self.user_achievements.get(user_id, [])
            achievement_multiplier = Decimal('1.0')
            
            for user_achievement in user_achievements:
                if user_achievement.status != RewardStatus.REDEEMED:
                    continue
                
                if (user_achievement.reward_expires_at and
                    user_achievement.reward_expires_at < datetime.utcnow()):
                    continue
                
                achievement = self.active_achievements.get(user_achievement.achievement_id)
                if achievement and achievement.reward_type == RewardType.REVENUE_MULTIPLIER:
                    achievement_multiplier *= achievement.reward_value
            
            if achievement_multiplier > Decimal('1.0'):
                multipliers["achievements"] = float(achievement_multiplier)
            
            return multipliers
            
        except Exception as e:
            logger.error(f"❌ Error calculating active multipliers: {e}")
            return {"base": 1.0}
    
    async def _get_daily_rewards_total(self, user_id: str) -> Decimal:
        """Get total rewards earned by user today."""
        try:
            today = datetime.utcnow().date().isoformat()
            user_daily_rewards = self.daily_reward_tracking.get(user_id, {})
            return user_daily_rewards.get(today, Decimal('0.00'))
        except Exception as e:
            logger.error(f"❌ Error getting daily rewards total: {e}")
            return Decimal('0.00')
    
    async def _track_daily_reward(self, user_id: str, amount: Decimal) -> None:
        """Track daily reward for user."""
        try:
            today = datetime.utcnow().date().isoformat()
            if user_id not in self.daily_reward_tracking:
                self.daily_reward_tracking[user_id] = {}
            
            current_total = self.daily_reward_tracking[user_id].get(today, Decimal('0.00'))
            self.daily_reward_tracking[user_id][today] = current_total + amount
            
        except Exception as e:
            logger.error(f"❌ Error tracking daily reward: {e}")
    
    async def _update_consistency_streak(self, user_id: str) -> None:
        """Update user's consistency streak."""
        try:
            # In real implementation, this would track daily activity
            metrics = self.user_engagement_metrics.get(user_id)
            if metrics:
                metrics.consistency_days += 1
        except Exception as e:
            logger.error(f"❌ Error updating consistency streak: {e}")
    
    async def get_user_gamification_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive gamification status for user."""
        try:
            metrics = self.user_engagement_metrics.get(user_id)
            if not metrics:
                return {"error": "User metrics not found"}
            
            user_achievements = self.user_achievements.get(user_id, [])
            active_multipliers = await self._calculate_active_multipliers(user_id)
            loyalty_tier = await self._update_loyalty_tier(user_id)
            daily_rewards = await self._get_daily_rewards_total(user_id)
            
            # Calculate total lifetime rewards
            total_rewards = sum(
                ua.reward_value for ua in user_achievements
                if ua.status == RewardStatus.REDEEMED
            )
            
            return {
                "user_id": user_id,
                "engagement_metrics": {
                    "content_count": metrics.content_count,
                    "total_views": metrics.total_views,
                    "total_engagement": metrics.total_engagement,
                    "revenue_generated": float(metrics.revenue_generated),
                    "collaborations_completed": metrics.collaborations_completed,
                    "protection_score": float(metrics.protection_score),
                    "consistency_days": metrics.consistency_days,
                    "quality_score": float(metrics.quality_score)
                },
                "achievements": {
                    "total_earned": len(user_achievements),
                    "total_rewards": float(total_rewards),
                    "recent_achievements": [
                        {
                            "achievement_id": ua.achievement_id,
                            "earned_at": ua.earned_at.isoformat(),
                            "reward_value": float(ua.reward_value),
                            "status": ua.status.value
                        }
                        for ua in sorted(user_achievements, key=lambda x: x.earned_at, reverse=True)[:5]
                    ]
                },
                "loyalty_program": {
                    "current_tier": loyalty_tier.value if loyalty_tier else "bronze",
                    "tier_benefits": self.loyalty_program.tier_benefits.get(loyalty_tier, {}) if loyalty_tier else {}
                },
                "active_multipliers": active_multipliers,
                "daily_rewards": float(daily_rewards),
                "daily_limit_remaining": float(self.max_reward_per_user_daily - daily_rewards),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting user gamification status: {e}")
            return {"error": str(e)}
    
    async def _log_achievement_event(
        self,
        user_achievement: UserAchievement,
        achievement: Achievement,
        event_type: str
    ) -> None:
        """Log achievement event for analytics."""
        try:
            event_data = {
                "user_achievement_id": user_achievement.user_achievement_id,
                "user_id": user_achievement.user_id,
                "achievement_id": achievement.achievement_id,
                "achievement_type": achievement.achievement_type.value,
                "reward_type": achievement.reward_type.value,
                "reward_value": float(achievement.reward_value),
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In real implementation, send to analytics pipeline
            logger.debug(f"📊 Achievement event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"❌ Error logging achievement event: {e}")


# Factory function for easy instantiation
def get_gamification_monetization_bridge(**kwargs) -> GamificationMonetizationBridge:
    """Get configured Gamification-Monetization Bridge instance."""
    return GamificationMonetizationBridge(**kwargs)


if __name__ == "__main__":
    # Example usage
    async def main():
        bridge = get_gamification_monetization_bridge()
        
        # Simulate user activity
        activity_data = {
            "content_uploaded": True,
            "views_gained": 15000,
            "engagement_gained": 1200,
            "revenue_earned": 25.50,
            "quality_score": 4.7
        }
        
        # Process activity for achievement detection
        result = await bridge.process_user_activity("creator_123", activity_data)
        print(f"🎮 Activity processed: {result}")
        
        # Get user status
        status = await bridge.get_user_gamification_status("creator_123")
        print(f"📊 User status: {status}")
    
    # Run example
    asyncio.run(main())