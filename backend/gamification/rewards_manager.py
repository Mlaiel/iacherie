"""Advanced Rewards Manager - Intelligent Reward Distribution System
==================================================================

Sophisticated reward calculation and distribution engine providing dynamic
reward algorithms, multi-currency support, time-based bonuses, and
comprehensive reward analytics for content creators.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/rewards_manager.py
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
Reward Calculation → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
from statistics import mean

logger = logging.getLogger(__name__)


class RewardType(str, Enum):
    """Types of rewards."""
    CURRENCY = "currency"
    EXPERIENCE = "experience"
    BADGE = "badge"
    NFT = "nft"
    BOOST = "boost"
    ACCESS = "access"
    SUBSCRIPTION = "subscription"
    REVENUE_SHARE = "revenue_share"


class CurrencyType(str, Enum):
    """Virtual currency types."""
    CREDITS = "credits"
    COLLABORATION_COINS = "collaboration_coins"
    QUALITY_CRYSTALS = "quality_crystals"
    ACHIEVEMENT_GEMS = "achievement_gems"
    CREATOR_TOKENS = "creator_tokens"
    PREMIUM_POINTS = "premium_points"


class RewardSource(str, Enum):
    """Sources of rewards."""
    CONTENT_UPLOAD = "content_upload"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    COLLABORATION_COMPLETE = "collaboration_complete"
    DAILY_LOGIN = "daily_login"
    QUALITY_MILESTONE = "quality_milestone"
    ENGAGEMENT_BONUS = "engagement_bonus"
    REFERRAL = "referral"
    CHALLENGE_COMPLETE = "challenge_complete"
    TIER_PROMOTION = "tier_promotion"
    SPECIAL_EVENT = "special_event"


class RewardStatus(str, Enum):
    """Reward status."""
    PENDING = "pending"
    AWARDED = "awarded"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class RewardCalculationContext:
    """Context for reward calculations."""
    user_id: str
    source: RewardSource
    base_data: Dict[str, Any]
    user_profile: Dict[str, Any] = field(default_factory=dict)
    multipliers: Dict[str, float] = field(default_factory=dict)
    bonuses: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Reward:
    """Individual reward definition."""
    id: str
    user_id: str
    reward_type: RewardType
    currency_type: Optional[CurrencyType]
    amount: Union[int, float, Decimal]
    source: RewardSource
    description: str
    status: RewardStatus = RewardStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    awarded_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None


@dataclass
class RewardBundle:
    """Collection of rewards awarded together."""
    id: str
    user_id: str
    source: RewardSource
    rewards: List[Reward]
    total_value: Decimal
    bonus_multiplier: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RewardMultiplier:
    """Reward multiplier configuration."""
    name: str
    multiplier: float
    condition: str
    active_until: Optional[datetime] = None
    max_applications: Optional[int] = None
    current_applications: int = 0


class RewardsManager:
    """
    Advanced rewards management system providing intelligent reward
    calculation, distribution, and analytics with multi-currency support.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the rewards manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.pending_rewards: Dict[str, List[Reward]] = {}
        self.reward_multipliers: Dict[str, RewardMultiplier] = {}
        self.base_reward_configs = self._initialize_base_rewards()
        self.daily_limits = self._initialize_daily_limits()
        
        self.logger.info("RewardsManager initialized")
    
    def _initialize_base_rewards(self) -> Dict[RewardSource, Dict[str, Any]]:
        """Initialize base reward configurations."""
        return {
            RewardSource.CONTENT_UPLOAD: {
                "base_credits": 50,
                "quality_bonus_multiplier": 2.0,
                "view_bonus_per_1k": 5,
                "engagement_bonus_multiplier": 1.5,
                "platform_diversity_bonus": 10
            },
            RewardSource.ACHIEVEMENT_UNLOCK: {
                "bronze_credits": 100,
                "silver_credits": 250,
                "gold_credits": 500,
                "platinum_credits": 1000,
                "diamond_credits": 2500,
                "legendary_credits": 5000
            },
            RewardSource.COLLABORATION_COMPLETE: {
                "base_collab_coins": 25,
                "success_bonus_multiplier": 2.0,
                "duration_bonus_per_day": 5,
                "partner_rating_bonus": 15
            },
            RewardSource.DAILY_LOGIN: {
                "base_credits": 10,
                "streak_multiplier": 0.1,  # +10% per day
                "weekly_bonus": 50,
                "monthly_bonus": 200
            },
            RewardSource.QUALITY_MILESTONE: {
                "quality_crystals_per_point": 10,
                "excellence_bonus": 100,
                "consistency_bonus": 50
            },
            RewardSource.ENGAGEMENT_BONUS: {
                "credits_per_percent": 2,
                "viral_threshold": 100000,
                "viral_bonus": 1000
            },
            RewardSource.REFERRAL: {
                "base_credits": 100,
                "successful_referral_bonus": 500,
                "tier_bonus_multiplier": 1.5
            },
            RewardSource.CHALLENGE_COMPLETE: {
                "base_credits": 200,
                "difficulty_multiplier": {
                    "easy": 1.0,
                    "medium": 1.5,
                    "hard": 2.0,
                    "expert": 3.0
                },
                "time_bonus_multiplier": 0.5
            },
            RewardSource.TIER_PROMOTION: {
                "rising_bonus": 500,
                "skilled_bonus": 1500,
                "expert_bonus": 5000,
                "master_bonus": 15000,
                "legend_bonus": 50000,
                "champion_bonus": 150000
            }
        }
    
    def _initialize_daily_limits(self) -> Dict[RewardSource, int]:
        """Initialize daily reward limits."""
        return {
            RewardSource.CONTENT_UPLOAD: 1000,  # Max 1000 credits per day from uploads
            RewardSource.DAILY_LOGIN: 100,     # Max 100 credits per day from login
            RewardSource.ENGAGEMENT_BONUS: 500, # Max 500 credits per day from engagement
            RewardSource.REFERRAL: 2000,       # Max 2000 credits per day from referrals
        }
    
    async def calculate_rewards(
        self,
        context: RewardCalculationContext
    ) -> RewardBundle:
        """
        Calculate rewards based on context and source.
        
        Args:
            context: Reward calculation context
            
        Returns:
            Bundle of calculated rewards
        """
        try:
            rewards = []
            bundle_id = str(uuid4())
            
            # Get base reward configuration
            base_config = self.base_reward_configs.get(context.source, {})
            
            if context.source == RewardSource.CONTENT_UPLOAD:
                rewards.extend(await self._calculate_content_upload_rewards(context, base_config))
            
            elif context.source == RewardSource.ACHIEVEMENT_UNLOCK:
                rewards.extend(await self._calculate_achievement_rewards(context, base_config))
            
            elif context.source == RewardSource.COLLABORATION_COMPLETE:
                rewards.extend(await self._calculate_collaboration_rewards(context, base_config))
            
            elif context.source == RewardSource.DAILY_LOGIN:
                rewards.extend(await self._calculate_login_rewards(context, base_config))
            
            elif context.source == RewardSource.QUALITY_MILESTONE:
                rewards.extend(await self._calculate_quality_rewards(context, base_config))
            
            elif context.source == RewardSource.ENGAGEMENT_BONUS:
                rewards.extend(await self._calculate_engagement_rewards(context, base_config))
            
            elif context.source == RewardSource.REFERRAL:
                rewards.extend(await self._calculate_referral_rewards(context, base_config))
            
            elif context.source == RewardSource.CHALLENGE_COMPLETE:
                rewards.extend(await self._calculate_challenge_rewards(context, base_config))
            
            elif context.source == RewardSource.TIER_PROMOTION:
                rewards.extend(await self._calculate_tier_promotion_rewards(context, base_config))
            
            # Apply global multipliers
            rewards = await self._apply_multipliers(rewards, context)
            
            # Check daily limits
            rewards = await self._apply_daily_limits(rewards, context)
            
            # Calculate total value
            total_value = sum(
                Decimal(str(reward.amount)) for reward in rewards 
                if reward.reward_type == RewardType.CURRENCY
            )
            
            bundle = RewardBundle(
                id=bundle_id,
                user_id=context.user_id,
                source=context.source,
                rewards=rewards,
                total_value=total_value
            )
            
            self.logger.info(f"💰 Calculated {len(rewards)} rewards for {context.user_id} ({context.source.value})")
            
            return bundle
            
        except Exception as e:
            self.logger.error(f"Error calculating rewards: {e}")
            return RewardBundle(
                id=str(uuid4()),
                user_id=context.user_id,
                source=context.source,
                rewards=[],
                total_value=Decimal('0')
            )
    
    async def _calculate_content_upload_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for content upload."""
        rewards = []
        
        try:
            # Base credits reward
            base_credits = config.get("base_credits", 50)
            
            # Quality bonus
            quality_score = context.base_data.get("quality_score", 0)
            quality_multiplier = 1 + (quality_score / 10) * config.get("quality_bonus_multiplier", 2.0)
            
            # View bonus
            views = context.base_data.get("views", 0)
            view_bonus = (views // 1000) * config.get("view_bonus_per_1k", 5)
            
            # Engagement bonus
            engagement_rate = context.base_data.get("engagement_rate", 0)
            engagement_bonus = engagement_rate * config.get("engagement_bonus_multiplier", 1.5)
            
            # Platform diversity bonus
            platforms_count = len(context.base_data.get("platforms", []))
            platform_bonus = platforms_count * config.get("platform_diversity_bonus", 10)
            
            total_credits = int(
                (base_credits * quality_multiplier) + view_bonus + engagement_bonus + platform_bonus
            )
            
            # Main credits reward
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.CREDITS,
                amount=total_credits,
                source=context.source,
                description=f"Content upload reward (Quality: {quality_score}/10)",
                metadata={
                    "quality_score": quality_score,
                    "views": views,
                    "engagement_rate": engagement_rate,
                    "platforms_count": platforms_count
                }
            ))
            
            # Experience points
            exp_points = max(10, int(total_credits * 0.5))
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.EXPERIENCE,
                currency_type=None,
                amount=exp_points,
                source=context.source,
                description="Experience for content creation"
            ))
            
            # Quality crystals for high-quality content
            if quality_score >= 8:
                quality_crystals = int((quality_score - 7) * 5)
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.CURRENCY,
                    currency_type=CurrencyType.QUALITY_CRYSTALS,
                    amount=quality_crystals,
                    source=context.source,
                    description=f"High quality content bonus ({quality_score}/10)"
                ))
            
        except Exception as e:
            self.logger.error(f"Error calculating content upload rewards: {e}")
        
        return rewards
    
    async def _calculate_achievement_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for achievement unlock."""
        rewards = []
        
        try:
            achievement_tier = context.base_data.get("tier", "bronze")
            achievement_points = context.base_data.get("points", 0)
            
            # Base credits based on tier
            tier_credits = {
                "bronze": config.get("bronze_credits", 100),
                "silver": config.get("silver_credits", 250),
                "gold": config.get("gold_credits", 500),
                "platinum": config.get("platinum_credits", 1000),
                "diamond": config.get("diamond_credits", 2500),
                "legendary": config.get("legendary_credits", 5000)
            }
            
            base_credits = tier_credits.get(achievement_tier, 100)
            
            # Credits reward
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.ACHIEVEMENT_GEMS,
                amount=base_credits,
                source=context.source,
                description=f"Achievement unlock: {achievement_tier.title()} tier",
                metadata={"tier": achievement_tier, "points": achievement_points}
            ))
            
            # Experience points
            exp_points = achievement_points or (base_credits // 2)
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.EXPERIENCE,
                currency_type=None,
                amount=exp_points,
                source=context.source,
                description="Achievement experience bonus"
            ))
            
            # Special rewards for high-tier achievements
            if achievement_tier in ["platinum", "diamond", "legendary"]:
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.BADGE,
                    currency_type=None,
                    amount=1,
                    source=context.source,
                    description=f"{achievement_tier.title()} Achievement Badge",
                    metadata={"badge_type": f"{achievement_tier}_achiever"}
                ))
            
            # NFT for legendary achievements
            if achievement_tier == "legendary":
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.NFT,
                    currency_type=None,
                    amount=1,
                    source=context.source,
                    description="Legendary Achievement NFT",
                    metadata={"nft_type": "legendary_achievement"}
                ))
        
        except Exception as e:
            self.logger.error(f"Error calculating achievement rewards: {e}")
        
        return rewards
    
    async def _calculate_collaboration_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for collaboration completion."""
        rewards = []
        
        try:
            base_coins = config.get("base_collab_coins", 25)
            success_score = context.base_data.get("success_score", 5)
            duration_days = context.base_data.get("duration_days", 1)
            partner_rating = context.base_data.get("partner_rating", 5)
            
            # Calculate bonus multipliers
            success_multiplier = 1 + (success_score / 10) * config.get("success_bonus_multiplier", 2.0)
            duration_bonus = duration_days * config.get("duration_bonus_per_day", 5)
            rating_bonus = partner_rating * config.get("partner_rating_bonus", 15)
            
            total_coins = int(base_coins * success_multiplier + duration_bonus + rating_bonus)
            
            # Collaboration coins reward
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.COLLABORATION_COINS,
                amount=total_coins,
                source=context.source,
                description=f"Collaboration completion (Success: {success_score}/10)",
                metadata={
                    "success_score": success_score,
                    "duration_days": duration_days,
                    "partner_rating": partner_rating
                }
            ))
            
            # Experience points
            exp_points = int(total_coins * 0.8)
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.EXPERIENCE,
                currency_type=None,
                amount=exp_points,
                source=context.source,
                description="Collaboration experience"
            ))
        
        except Exception as e:
            self.logger.error(f"Error calculating collaboration rewards: {e}")
        
        return rewards
    
    async def _calculate_login_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for daily login."""
        rewards = []
        
        try:
            base_credits = config.get("base_credits", 10)
            login_streak = context.base_data.get("login_streak", 1)
            
            # Streak multiplier
            streak_multiplier = 1 + (login_streak * config.get("streak_multiplier", 0.1))
            total_credits = int(base_credits * streak_multiplier)
            
            # Daily login reward
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.CREDITS,
                amount=total_credits,
                source=context.source,
                description=f"Daily login bonus (Streak: {login_streak})",
                metadata={"login_streak": login_streak}
            ))
            
            # Weekly bonus
            if login_streak % 7 == 0:
                weekly_bonus = config.get("weekly_bonus", 50)
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.CURRENCY,
                    currency_type=CurrencyType.CREDITS,
                    amount=weekly_bonus,
                    source=context.source,
                    description=f"Weekly streak bonus (Week {login_streak // 7})"
                ))
            
            # Monthly bonus
            if login_streak % 30 == 0:
                monthly_bonus = config.get("monthly_bonus", 200)
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.CURRENCY,
                    currency_type=CurrencyType.PREMIUM_POINTS,
                    amount=monthly_bonus,
                    source=context.source,
                    description=f"Monthly streak bonus (Month {login_streak // 30})"
                ))
        
        except Exception as e:
            self.logger.error(f"Error calculating login rewards: {e}")
        
        return rewards
    
    async def _calculate_quality_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for quality milestones."""
        rewards = []
        
        try:
            quality_points = context.base_data.get("quality_points", 0)
            crystals_per_point = config.get("quality_crystals_per_point", 10)
            
            total_crystals = quality_points * crystals_per_point
            
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.QUALITY_CRYSTALS,
                amount=total_crystals,
                source=context.source,
                description=f"Quality milestone: {quality_points} points",
                metadata={"quality_points": quality_points}
            ))
        
        except Exception as e:
            self.logger.error(f"Error calculating quality rewards: {e}")
        
        return rewards
    
    async def _calculate_engagement_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for engagement bonuses."""
        rewards = []
        
        try:
            engagement_rate = context.base_data.get("engagement_rate", 0)
            total_views = context.base_data.get("total_views", 0)
            
            credits_per_percent = config.get("credits_per_percent", 2)
            base_credits = int(engagement_rate * credits_per_percent)
            
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.CREDITS,
                amount=base_credits,
                source=context.source,
                description=f"Engagement bonus ({engagement_rate:.1f}%)",
                metadata={"engagement_rate": engagement_rate}
            ))
            
            # Viral bonus
            viral_threshold = config.get("viral_threshold", 100000)
            if total_views >= viral_threshold:
                viral_bonus = config.get("viral_bonus", 1000)
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.CURRENCY,
                    currency_type=CurrencyType.CREATOR_TOKENS,
                    amount=viral_bonus,
                    source=context.source,
                    description=f"Viral content bonus ({total_views:,} views)"
                ))
        
        except Exception as e:
            self.logger.error(f"Error calculating engagement rewards: {e}")
        
        return rewards
    
    async def _calculate_referral_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for referrals."""
        rewards = []
        
        try:
            base_credits = config.get("base_credits", 100)
            referral_success = context.base_data.get("referral_success", False)
            
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.CREDITS,
                amount=base_credits,
                source=context.source,
                description="Referral bonus"
            ))
            
            if referral_success:
                success_bonus = config.get("successful_referral_bonus", 500)
                rewards.append(Reward(
                    id=str(uuid4()),
                    user_id=context.user_id,
                    reward_type=RewardType.CURRENCY,
                    currency_type=CurrencyType.PREMIUM_POINTS,
                    amount=success_bonus,
                    source=context.source,
                    description="Successful referral bonus"
                ))
        
        except Exception as e:
            self.logger.error(f"Error calculating referral rewards: {e}")
        
        return rewards
    
    async def _calculate_challenge_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for challenge completion."""
        rewards = []
        
        try:
            base_credits = config.get("base_credits", 200)
            difficulty = context.base_data.get("difficulty", "medium")
            completion_time = context.base_data.get("completion_time_hours", 24)
            
            difficulty_multipliers = config.get("difficulty_multiplier", {
                "easy": 1.0, "medium": 1.5, "hard": 2.0, "expert": 3.0
            })
            
            difficulty_mult = difficulty_multipliers.get(difficulty, 1.0)
            time_bonus_mult = max(0.5, 2.0 - (completion_time / 24))
            
            total_credits = int(base_credits * difficulty_mult * time_bonus_mult)
            
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.CREDITS,
                amount=total_credits,
                source=context.source,
                description=f"Challenge completed ({difficulty})",
                metadata={
                    "difficulty": difficulty,
                    "completion_time_hours": completion_time
                }
            ))
        
        except Exception as e:
            self.logger.error(f"Error calculating challenge rewards: {e}")
        
        return rewards
    
    async def _calculate_tier_promotion_rewards(
        self,
        context: RewardCalculationContext,
        config: Dict[str, Any]
    ) -> List[Reward]:
        """Calculate rewards for tier promotions."""
        rewards = []
        
        try:
            new_tier = context.base_data.get("new_tier", "rising")
            
            tier_bonuses = {
                "rising": config.get("rising_bonus", 500),
                "skilled": config.get("skilled_bonus", 1500),
                "expert": config.get("expert_bonus", 5000),
                "master": config.get("master_bonus", 15000),
                "legend": config.get("legend_bonus", 50000),
                "champion": config.get("champion_bonus", 150000)
            }
            
            bonus_amount = tier_bonuses.get(new_tier, 500)
            
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.CURRENCY,
                currency_type=CurrencyType.PREMIUM_POINTS,
                amount=bonus_amount,
                source=context.source,
                description=f"Tier promotion to {new_tier.title()}",
                metadata={"new_tier": new_tier}
            ))
            
            # Special badge for tier promotion
            rewards.append(Reward(
                id=str(uuid4()),
                user_id=context.user_id,
                reward_type=RewardType.BADGE,
                currency_type=None,
                amount=1,
                source=context.source,
                description=f"{new_tier.title()} Tier Badge",
                metadata={"badge_type": f"{new_tier}_tier"}
            ))
        
        except Exception as e:
            self.logger.error(f"Error calculating tier promotion rewards: {e}")
        
        return rewards
    
    async def _apply_multipliers(
        self,
        rewards: List[Reward],
        context: RewardCalculationContext
    ) -> List[Reward]:
        """Apply global multipliers to rewards."""
        try:
            # Apply context multipliers
            for reward in rewards:
                if reward.reward_type == RewardType.CURRENCY:
                    multiplier_key = f"{reward.currency_type.value}_multiplier"
                    if multiplier_key in context.multipliers:
                        multiplier = context.multipliers[multiplier_key]
                        reward.amount = int(float(reward.amount) * multiplier)
                        reward.metadata["applied_multiplier"] = multiplier
            
            # Apply active global multipliers
            for multiplier_name, multiplier_config in self.reward_multipliers.items():
                if self._is_multiplier_active(multiplier_config, context):
                    for reward in rewards:
                        if reward.reward_type == RewardType.CURRENCY:
                            reward.amount = int(float(reward.amount) * multiplier_config.multiplier)
                            reward.metadata[f"global_multiplier_{multiplier_name}"] = multiplier_config.multiplier
        
        except Exception as e:
            self.logger.error(f"Error applying multipliers: {e}")
        
        return rewards
    
    async def _apply_daily_limits(
        self,
        rewards: List[Reward],
        context: RewardCalculationContext
    ) -> List[Reward]:
        """Apply daily limits to rewards."""
        try:
            daily_limit = self.daily_limits.get(context.source, float('inf'))
            
            if daily_limit < float('inf'):
                # In a real implementation, would check current daily total from database
                current_daily_total = 0  # Mock value
                
                remaining_limit = max(0, daily_limit - current_daily_total)
                
                currency_rewards = [r for r in rewards if r.reward_type == RewardType.CURRENCY]
                total_currency = sum(float(r.amount) for r in currency_rewards)
                
                if total_currency > remaining_limit:
                    # Scale down rewards proportionally
                    scale_factor = remaining_limit / total_currency
                    for reward in currency_rewards:
                        reward.amount = int(float(reward.amount) * scale_factor)
                        reward.metadata["daily_limit_applied"] = True
        
        except Exception as e:
            self.logger.error(f"Error applying daily limits: {e}")
        
        return rewards
    
    def _is_multiplier_active(
        self,
        multiplier: RewardMultiplier,
        context: RewardCalculationContext
    ) -> bool:
        """Check if a multiplier is currently active."""
        try:
            # Check expiration
            if multiplier.active_until and datetime.utcnow() > multiplier.active_until:
                return False
            
            # Check max applications
            if (multiplier.max_applications and 
                multiplier.current_applications >= multiplier.max_applications):
                return False
            
            # Check condition (simplified implementation)
            # In a real implementation, this would evaluate complex conditions
            return True
        
        except Exception as e:
            self.logger.error(f"Error checking multiplier active status: {e}")
            return False
    
    async def award_rewards(self, reward_bundle: RewardBundle) -> bool:
        """Award a bundle of rewards to the user."""
        try:
            # Add to pending rewards
            if reward_bundle.user_id not in self.pending_rewards:
                self.pending_rewards[reward_bundle.user_id] = []
            
            # Update reward status
            for reward in reward_bundle.rewards:
                reward.status = RewardStatus.AWARDED
                reward.awarded_at = datetime.utcnow()
            
            self.pending_rewards[reward_bundle.user_id].extend(reward_bundle.rewards)
            
            # In a real implementation, would save to database
            self.logger.info(f"✅ Awarded {len(reward_bundle.rewards)} rewards to {reward_bundle.user_id}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error awarding rewards: {e}")
            return False
    
    async def claim_reward(self, user_id: str, reward_id: str) -> bool:
        """Claim a specific reward."""
        try:
            if user_id not in self.pending_rewards:
                return False
            
            for reward in self.pending_rewards[user_id]:
                if reward.id == reward_id and reward.status == RewardStatus.AWARDED:
                    reward.status = RewardStatus.CLAIMED
                    reward.claimed_at = datetime.utcnow()
                    
                    # Process the reward (add to user balance, etc.)
                    await self._process_claimed_reward(reward)
                    
                    self.logger.info(f"🎁 Reward claimed: {user_id} - {reward.description}")
                    return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error claiming reward: {e}")
            return False
    
    async def _process_claimed_reward(self, reward: Reward) -> bool:
        """Process a claimed reward."""
        try:
            if reward.reward_type == RewardType.CURRENCY:
                # Add currency to user balance
                pass
            elif reward.reward_type == RewardType.EXPERIENCE:
                # Add experience points
                pass
            elif reward.reward_type == RewardType.BADGE:
                # Award badge
                pass
            elif reward.reward_type == RewardType.NFT:
                # Mint/award NFT
                pass
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error processing claimed reward: {e}")
            return False
    
    async def get_user_pending_rewards(self, user_id: str) -> List[Reward]:
        """Get all pending rewards for a user."""
        try:
            if user_id not in self.pending_rewards:
                return []
            
            return [
                r for r in self.pending_rewards[user_id] 
                if r.status == RewardStatus.AWARDED
            ]
        
        except Exception as e:
            self.logger.error(f"Error getting user pending rewards: {e}")
            return []
    
    async def get_reward_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get reward analytics for a user."""
        try:
            if user_id not in self.pending_rewards:
                return {}
            
            user_rewards = self.pending_rewards[user_id]
            
            analytics = {
                "total_rewards": len(user_rewards),
                "total_value": sum(float(r.amount) for r in user_rewards if r.reward_type == RewardType.CURRENCY),
                "by_type": {},
                "by_currency": {},
                "by_source": {},
                "claimed_count": len([r for r in user_rewards if r.status == RewardStatus.CLAIMED]),
                "pending_count": len([r for r in user_rewards if r.status == RewardStatus.AWARDED])
            }
            
            # Group by type
            for reward in user_rewards:
                reward_type = reward.reward_type.value
                if reward_type not in analytics["by_type"]:
                    analytics["by_type"][reward_type] = 0
                analytics["by_type"][reward_type] += 1
                
                # Group by currency
                if reward.currency_type:
                    currency = reward.currency_type.value
                    if currency not in analytics["by_currency"]:
                        analytics["by_currency"][currency] = 0
                    analytics["by_currency"][currency] += float(reward.amount)
                
                # Group by source
                source = reward.source.value
                if source not in analytics["by_source"]:
                    analytics["by_source"][source] = 0
                analytics["by_source"][source] += 1
            
            return analytics
        
        except Exception as e:
            self.logger.error(f"Error getting reward analytics: {e}")
            return {}


# Global rewards manager instance
_rewards_manager: Optional[RewardsManager] = None


async def get_rewards_manager() -> RewardsManager:
    """Get global rewards manager instance."""
    global _rewards_manager
    
    if _rewards_manager is None:
        _rewards_manager = RewardsManager()
    
    return _rewards_manager


async def calculate_and_award_rewards(
    user_id: str,
    source: RewardSource,
    base_data: Dict[str, Any],
    user_profile: Optional[Dict[str, Any]] = None
) -> RewardBundle:
    """Convenience function to calculate and award rewards."""
    manager = await get_rewards_manager()
    
    context = RewardCalculationContext(
        user_id=user_id,
        source=source,
        base_data=base_data,
        user_profile=user_profile or {}
    )
    
    reward_bundle = await manager.calculate_rewards(context)
    await manager.award_rewards(reward_bundle)
    
    return reward_bundle