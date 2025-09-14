"""Unified Reward System - Enterprise Gamification Rewards
========================================================

Comprehensive unified reward system combining general platform rewards
and specialized gaming rewards with intelligent distribution algorithms,
multi-currency support, and advanced analytics.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/reward_system.py
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
Reward Calculation → Gaming Rewards → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import math
import random
from statistics import mean

logger = logging.getLogger(__name__)


# ============================================================================
# UNIFIED REWARD ENUMS AND TYPES
# ============================================================================

class RewardType(str, Enum):
    """Unified reward types."""
    # General Platform Rewards
    CURRENCY = "currency"
    EXPERIENCE = "experience"
    BADGE = "badge"
    NFT = "nft"
    BOOST = "boost"
    ACCESS = "access"
    SUBSCRIPTION = "subscription"
    REVENUE_SHARE = "revenue_share"
    
    # Gaming-Specific Rewards
    VIRTUAL_CURRENCY = "virtual_currency"
    TYCOON_CASH = "tycoon_cash"
    GAMING_XP = "gaming_xp"
    PREMIUM_TOKENS = "premium_tokens"
    COMPETITIVE_POINTS = "competitive_points"
    SEASONAL_COINS = "seasonal_coins"
    ACHIEVEMENT_GEMS = "achievement_gems"
    RARE_COLLECTIBLES = "rare_collectibles"
    POWER_UPS = "power_ups"
    EXCLUSIVE_ASSETS = "exclusive_assets"
    MULTIPLIER_BOOSTS = "multiplier_boosts"
    TIME_ACCELERATORS = "time_accelerators"


class CurrencyType(str, Enum):
    """Unified currency types."""
    # Platform Currencies
    CREDITS = "credits"
    COLLABORATION_COINS = "collaboration_coins"
    QUALITY_CRYSTALS = "quality_crystals"
    CREATOR_TOKENS = "creator_tokens"
    PREMIUM_POINTS = "premium_points"
    
    # Gaming Currencies
    TYCOON_CASH = "tycoon_cash"
    GAMING_GEMS = "gaming_gems"
    PRESTIGE_POINTS = "prestige_points"
    COMPETITIVE_TOKENS = "competitive_tokens"
    SEASONAL_CURRENCY = "seasonal_currency"
    COLLECTOR_COINS = "collector_coins"


class RewardTier(str, Enum):
    """Unified reward tier classifications."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    DIVINE = "divine"


class RewardSource(str, Enum):
    """Unified reward sources."""
    # Platform Sources
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
    
    # Gaming Sources
    TYCOON_PROGRESS = "tycoon_progress"
    COMPETITIVE_RANKING = "competitive_ranking"
    SEASONAL_EVENT = "seasonal_event"
    SPECIAL_CHALLENGE = "special_challenge"
    MILESTONE_REACHED = "milestone_reached"
    TOURNAMENT_WIN = "tournament_win"
    COMMUNITY_EVENT = "community_event"
    RARE_ACTION = "rare_action"


class RewardStatus(str, Enum):
    """Unified reward status."""
    PENDING = "pending"
    AVAILABLE = "available"
    AWARDED = "awarded"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    LOCKED = "locked"
    PROCESSING = "processing"


# ============================================================================
# UNIFIED DATA STRUCTURES
# ============================================================================

@dataclass
class RewardCalculationContext:
    """Context for unified reward calculations."""
    user_id: str
    source: RewardSource
    base_data: Dict[str, Any]
    user_profile: Dict[str, Any] = field(default_factory=dict)
    multipliers: Dict[str, float] = field(default_factory=dict)
    bonuses: Dict[str, float] = field(default_factory=dict)
    is_gaming_context: bool = False
    gaming_stats: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Reward:
    """Unified reward definition."""
    reward_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    reward_type: RewardType = RewardType.CURRENCY
    currency_type: Optional[CurrencyType] = None
    amount: Union[int, float, Decimal] = 0
    tier: RewardTier = RewardTier.COMMON
    source: RewardSource = RewardSource.CONTENT_UPLOAD
    status: RewardStatus = RewardStatus.PENDING
    
    # Metadata
    title: str = ""
    description: str = ""
    icon_url: Optional[str] = None
    
    # Gaming specific
    is_gaming_reward: bool = False
    tycoon_player_id: Optional[str] = None
    gaming_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    awarded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    claimed_at: Optional[datetime] = None
    
    # Context
    source_context: Dict[str, Any] = field(default_factory=dict)
    calculation_details: Dict[str, Any] = field(default_factory=dict)
    multipliers_applied: Dict[str, float] = field(default_factory=dict)


@dataclass
class UserRewardStats:
    """Comprehensive user reward statistics."""
    user_id: str = ""
    
    # General Stats
    total_rewards_received: int = 0
    total_rewards_claimed: int = 0
    total_currency_earned: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    total_experience_earned: int = 0
    
    # Gaming Stats
    gaming_rewards_received: int = 0
    gaming_currency_earned: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    tycoon_rewards: int = 0
    competitive_rewards: int = 0
    
    # Performance Stats
    average_reward_value: float = 0.0
    highest_single_reward: Decimal = Decimal('0')
    reward_streak_current: int = 0
    reward_streak_best: int = 0
    
    # Source Breakdown
    rewards_by_source: Dict[RewardSource, int] = field(default_factory=dict)
    rewards_by_tier: Dict[RewardTier, int] = field(default_factory=dict)
    
    # Time-based Stats
    daily_rewards_claimed: int = 0
    weekly_rewards_claimed: int = 0
    monthly_rewards_claimed: int = 0
    last_reward_date: Optional[datetime] = None
    
    # Special Achievements
    rare_rewards_count: int = 0
    legendary_rewards_count: int = 0
    seasonal_rewards_count: int = 0


# ============================================================================
# UNIFIED REWARD SYSTEM
# ============================================================================

class UnifiedRewardSystem:
    """
    Unified reward system combining general platform rewards
    and specialized gaming rewards with intelligent distribution.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.user_rewards: Dict[str, List[Reward]] = {}
        self.user_stats: Dict[str, UserRewardStats] = {}
        self.reward_templates: Dict[str, Dict[str, Any]] = {}
        self.currency_rates: Dict[CurrencyType, float] = {}
        self.multiplier_rules: Dict[str, float] = {}
        
        # Gaming-specific storage
        self.gaming_reward_templates: Dict[str, Dict[str, Any]] = {}
        self.tycoon_rewards: Dict[str, List[Reward]] = {}
        
        self._initialize_reward_templates()
        self._initialize_currency_rates()
        logger.info("💰 Unified Reward System initialized")
    
    def _initialize_reward_templates(self) -> None:
        """Initialize reward templates for both platform and gaming."""
        
        # Platform Reward Templates
        self.reward_templates.update({
            "first_upload": {
                "reward_type": RewardType.CURRENCY,
                "currency_type": CurrencyType.CREDITS,
                "base_amount": 100,
                "tier": RewardTier.COMMON,
                "title": "First Upload Bonus",
                "description": "Welcome reward for your first content upload"
            },
            "collaboration_complete": {
                "reward_type": RewardType.CURRENCY,
                "currency_type": CurrencyType.COLLABORATION_COINS,
                "base_amount": 250,
                "tier": RewardTier.UNCOMMON,
                "title": "Collaboration Reward",
                "description": "Earned for completing a collaboration"
            },
            "achievement_unlock": {
                "reward_type": RewardType.CURRENCY,
                "currency_type": CurrencyType.ACHIEVEMENT_GEMS,
                "base_amount": 50,
                "tier": RewardTier.RARE,
                "title": "Achievement Reward",
                "description": "Earned for unlocking an achievement"
            }
        })
        
        # Gaming Reward Templates
        self.gaming_reward_templates.update({
            "tycoon_asset_purchase": {
                "reward_type": RewardType.GAMING_XP,
                "currency_type": CurrencyType.GAMING_GEMS,
                "base_amount": 25,
                "tier": RewardTier.COMMON,
                "title": "Asset Purchase Bonus",
                "description": "XP for purchasing a tycoon asset",
                "is_gaming_reward": True
            },
            "tycoon_milestone": {
                "reward_type": RewardType.TYCOON_CASH,
                "currency_type": CurrencyType.TYCOON_CASH,
                "base_amount": 1000,
                "tier": RewardTier.UNCOMMON,
                "title": "Tycoon Milestone",
                "description": "Cash bonus for reaching tycoon milestone",
                "is_gaming_reward": True
            },
            "competitive_win": {
                "reward_type": RewardType.COMPETITIVE_POINTS,
                "currency_type": CurrencyType.COMPETITIVE_TOKENS,
                "base_amount": 500,
                "tier": RewardTier.EPIC,
                "title": "Competitive Victory",
                "description": "Tokens for winning competitive event",
                "is_gaming_reward": True
            }
        })
    
    def _initialize_currency_rates(self) -> None:
        """Initialize exchange rates between currencies."""
        self.currency_rates = {
            # Platform currencies (base rate: 1 credit = 1.0)
            CurrencyType.CREDITS: 1.0,
            CurrencyType.COLLABORATION_COINS: 2.5,
            CurrencyType.QUALITY_CRYSTALS: 5.0,
            CurrencyType.CREATOR_TOKENS: 10.0,
            CurrencyType.PREMIUM_POINTS: 20.0,
            
            # Gaming currencies
            CurrencyType.TYCOON_CASH: 0.1,  # More abundant
            CurrencyType.GAMING_GEMS: 3.0,
            CurrencyType.PRESTIGE_POINTS: 15.0,
            CurrencyType.COMPETITIVE_TOKENS: 25.0,
            CurrencyType.SEASONAL_CURRENCY: 8.0,
            CurrencyType.COLLECTOR_COINS: 50.0,
        }
    
    async def calculate_reward(self, context: RewardCalculationContext) -> List[Reward]:
        """Calculate rewards based on context."""
        try:
            rewards = []
            
            # Get base template
            template_key = self._get_template_key(context.source, context.is_gaming_context)
            templates = self.gaming_reward_templates if context.is_gaming_context else self.reward_templates
            template = templates.get(template_key, {})
            
            if not template:
                logger.warning(f"No template found for source: {context.source}")
                return rewards
            
            # Calculate base amount
            base_amount = template.get('base_amount', 100)
            final_amount = self._apply_multipliers(base_amount, context)
            
            # Create reward
            reward = Reward(
                user_id=context.user_id,
                reward_type=RewardType(template.get('reward_type', 'currency')),
                currency_type=CurrencyType(template.get('currency_type', 'credits')) if template.get('currency_type') else None,
                amount=Decimal(str(final_amount)),
                tier=RewardTier(template.get('tier', 'common')),
                source=context.source,
                title=template.get('title', ''),
                description=template.get('description', ''),
                is_gaming_reward=context.is_gaming_context,
                source_context=context.base_data,
                calculation_details={
                    'base_amount': base_amount,
                    'final_amount': final_amount,
                    'template_used': template_key
                },
                multipliers_applied=context.multipliers
            )
            
            # Add gaming-specific data
            if context.is_gaming_context:
                reward.gaming_metadata = context.gaming_stats
                reward.tycoon_player_id = context.gaming_stats.get('player_id')
            
            rewards.append(reward)
            
            # Add bonus rewards for special conditions
            bonus_rewards = await self._calculate_bonus_rewards(context, reward)
            rewards.extend(bonus_rewards)
            
            return rewards
            
        except Exception as e:
            logger.error(f"Error calculating reward: {e}")
            return []
    
    def _get_template_key(self, source: RewardSource, is_gaming: bool) -> str:
        """Get template key based on source and context."""
        mapping = {
            # Platform sources
            RewardSource.CONTENT_UPLOAD: "first_upload",
            RewardSource.COLLABORATION_COMPLETE: "collaboration_complete",
            RewardSource.ACHIEVEMENT_UNLOCK: "achievement_unlock",
            
            # Gaming sources
            RewardSource.TYCOON_PROGRESS: "tycoon_asset_purchase",
            RewardSource.MILESTONE_REACHED: "tycoon_milestone",
            RewardSource.COMPETITIVE_RANKING: "competitive_win",
        }
        return mapping.get(source, "first_upload")
    
    def _apply_multipliers(self, base_amount: float, context: RewardCalculationContext) -> float:
        """Apply various multipliers to base reward amount."""
        final_amount = float(base_amount)
        
        # Apply context multipliers
        for multiplier_name, multiplier_value in context.multipliers.items():
            final_amount *= multiplier_value
        
        # Apply user profile bonuses
        profile = context.user_profile
        if profile.get('premium_member', False):
            final_amount *= 1.5
        
        if profile.get('creator_tier') == 'gold':
            final_amount *= 1.25
        elif profile.get('creator_tier') == 'platinum':
            final_amount *= 1.5
        
        # Apply gaming-specific multipliers
        if context.is_gaming_context:
            gaming_level = context.gaming_stats.get('level', 1)
            level_multiplier = 1.0 + (gaming_level - 1) * 0.02  # 2% per level
            final_amount *= level_multiplier
            
            # Apply prestige bonuses
            prestige_points = context.gaming_stats.get('prestige_points', 0)
            if prestige_points > 0:
                prestige_multiplier = 1.0 + (prestige_points * 0.01)  # 1% per prestige point
                final_amount *= prestige_multiplier
        
        # Add random variance (±5%)
        variance = random.uniform(-0.05, 0.05)
        final_amount *= (1.0 + variance)
        
        return max(1.0, final_amount)  # Minimum 1 unit
    
    async def _calculate_bonus_rewards(self, context: RewardCalculationContext, 
                                     primary_reward: Reward) -> List[Reward]:
        """Calculate additional bonus rewards."""
        bonus_rewards = []
        
        try:
            # Daily login streak bonus
            if context.source == RewardSource.DAILY_LOGIN:
                streak_days = context.base_data.get('streak_days', 1)
                if streak_days >= 7:  # Weekly bonus
                    bonus_rewards.append(Reward(
                        user_id=context.user_id,
                        reward_type=RewardType.CURRENCY,
                        currency_type=CurrencyType.PREMIUM_POINTS,
                        amount=Decimal('100'),
                        tier=RewardTier.RARE,
                        source=context.source,
                        title="Weekly Streak Bonus",
                        description=f"Bonus for {streak_days} day login streak"
                    ))
            
            # Gaming achievement bonus
            if context.is_gaming_context and context.source == RewardSource.ACHIEVEMENT_UNLOCK:
                achievement_tier = context.base_data.get('achievement_tier', 'bronze')
                if achievement_tier in ['legendary', 'mythical']:
                    bonus_rewards.append(Reward(
                        user_id=context.user_id,
                        reward_type=RewardType.RARE_COLLECTIBLES,
                        amount=Decimal('1'),
                        tier=RewardTier.LEGENDARY,
                        source=context.source,
                        title="Legendary Achievement Bonus",
                        description="Rare collectible for legendary achievement",
                        is_gaming_reward=True
                    ))
            
            # Quality milestone bonus
            if context.source == RewardSource.QUALITY_MILESTONE:
                quality_score = context.base_data.get('quality_score', 0)
                if quality_score >= 95:  # Exceptional quality
                    bonus_rewards.append(Reward(
                        user_id=context.user_id,
                        reward_type=RewardType.CURRENCY,
                        currency_type=CurrencyType.QUALITY_CRYSTALS,
                        amount=Decimal('50'),
                        tier=RewardTier.EPIC,
                        source=context.source,
                        title="Exceptional Quality Bonus",
                        description="Extra crystals for exceptional content quality"
                    ))
            
            return bonus_rewards
            
        except Exception as e:
            logger.error(f"Error calculating bonus rewards: {e}")
            return []
    
    async def award_rewards(self, user_id: str, rewards: List[Reward]) -> Dict[str, Any]:
        """Award calculated rewards to a user."""
        try:
            if user_id not in self.user_rewards:
                self.user_rewards[user_id] = []
                self.user_stats[user_id] = UserRewardStats(user_id=user_id)
            
            awarded_rewards = []
            total_value = Decimal('0')
            
            for reward in rewards:
                # Set reward as awarded
                reward.status = RewardStatus.AWARDED
                reward.awarded_at = datetime.now(timezone.utc)
                
                # Add to user rewards
                self.user_rewards[user_id].append(reward)
                awarded_rewards.append(reward)
                
                # Calculate value for stats
                if reward.currency_type:
                    rate = self.currency_rates.get(reward.currency_type, 1.0)
                    total_value += Decimal(str(reward.amount)) * Decimal(str(rate))
            
            # Update user stats
            await self._update_user_stats(user_id, awarded_rewards, total_value)
            
            logger.info(f"💰 Awarded {len(awarded_rewards)} rewards to user {user_id}")
            
            return {
                "success": True,
                "rewards_awarded": len(awarded_rewards),
                "total_value": float(total_value),
                "rewards": awarded_rewards
            }
            
        except Exception as e:
            logger.error(f"Error awarding rewards: {e}")
            return {"success": False, "message": str(e)}
    
    async def claim_reward(self, user_id: str, reward_id: str) -> Dict[str, Any]:
        """Claim a specific reward."""
        try:
            user_rewards = self.user_rewards.get(user_id, [])
            reward = next((r for r in user_rewards if r.reward_id == reward_id), None)
            
            if not reward:
                return {"success": False, "message": "Reward not found"}
            
            if reward.status != RewardStatus.AWARDED:
                return {"success": False, "message": "Reward not available for claiming"}
            
            if reward.expires_at and datetime.now(timezone.utc) > reward.expires_at:
                reward.status = RewardStatus.EXPIRED
                return {"success": False, "message": "Reward has expired"}
            
            # Claim the reward
            reward.status = RewardStatus.CLAIMED
            reward.claimed_at = datetime.now(timezone.utc)
            
            # Update user stats
            stats = self.user_stats[user_id]
            stats.total_rewards_claimed += 1
            
            if reward.is_gaming_reward:
                stats.gaming_rewards_received += 1
            
            # Update currency totals
            if reward.currency_type:
                current_amount = stats.total_currency_earned.get(reward.currency_type, Decimal('0'))
                stats.total_currency_earned[reward.currency_type] = current_amount + Decimal(str(reward.amount))
                
                if reward.is_gaming_reward:
                    gaming_current = stats.gaming_currency_earned.get(reward.currency_type, Decimal('0'))
                    stats.gaming_currency_earned[reward.currency_type] = gaming_current + Decimal(str(reward.amount))
            
            logger.info(f"💎 User {user_id} claimed reward: {reward.title}")
            
            return {
                "success": True,
                "reward": reward,
                "message": f"Successfully claimed {reward.title}"
            }
            
        except Exception as e:
            logger.error(f"Error claiming reward: {e}")
            return {"success": False, "message": str(e)}
    
    async def _update_user_stats(self, user_id -> None: str, rewards -> None: List[Reward], total_value -> None: Decimal) -> None:
        """Update comprehensive user reward statistics."""
        try:
            stats = self.user_stats[user_id]
            
            # Update basic stats
            stats.total_rewards_received += len(rewards)
            stats.last_reward_date = datetime.now(timezone.utc)
            
            # Update value stats
            if total_value > stats.highest_single_reward:
                stats.highest_single_reward = total_value
            
            # Update source and tier breakdowns
            for reward in rewards:
                # Source breakdown
                current_source_count = stats.rewards_by_source.get(reward.source, 0)
                stats.rewards_by_source[reward.source] = current_source_count + 1
                
                # Tier breakdown
                current_tier_count = stats.rewards_by_tier.get(reward.tier, 0)
                stats.rewards_by_tier[reward.tier] = current_tier_count + 1
                
                # Gaming stats
                if reward.is_gaming_reward:
                    stats.gaming_rewards_received += 1
                
                # Special reward counts
                if reward.tier in [RewardTier.RARE, RewardTier.EPIC]:
                    stats.rare_rewards_count += 1
                elif reward.tier in [RewardTier.LEGENDARY, RewardTier.MYTHICAL]:
                    stats.legendary_rewards_count += 1
            
            # Calculate average reward value
            all_rewards = self.user_rewards.get(user_id, [])
            if all_rewards:
                values = []
                for r in all_rewards:
                    if r.currency_type:
                        rate = self.currency_rates.get(r.currency_type, 1.0)
                        value = float(r.amount) * rate
                        values.append(value)
                
                if values:
                    stats.average_reward_value = mean(values)
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
    
    async def get_user_rewards(self, user_id: str, status_filter: Optional[RewardStatus] = None,
                              is_gaming_only: bool = False) -> Dict[str, Any]:
        """Get user rewards with optional filtering."""
        try:
            user_rewards = self.user_rewards.get(user_id, [])
            stats = self.user_stats.get(user_id, UserRewardStats(user_id=user_id))
            
            # Apply filters
            filtered_rewards = user_rewards
            
            if status_filter:
                filtered_rewards = [r for r in filtered_rewards if r.status == status_filter]
            
            if is_gaming_only:
                filtered_rewards = [r for r in filtered_rewards if r.is_gaming_reward]
            
            # Sort by most recent first
            filtered_rewards.sort(key=lambda x: x.awarded_at, reverse=True)
            
            return {
                "user_id": user_id,
                "stats": stats,
                "rewards": filtered_rewards,
                "total_rewards": len(filtered_rewards),
                "claimable_rewards": len([r for r in user_rewards if r.status == RewardStatus.AWARDED]),
                "gaming_rewards": len([r for r in user_rewards if r.is_gaming_reward]),
                "platform_rewards": len([r for r in user_rewards if not r.is_gaming_reward])
            }
            
        except Exception as e:
            logger.error(f"Error getting user rewards: {e}")
            return {"error": str(e)}


# Global instance
_reward_system_instance: Optional[UnifiedRewardSystem] = None


def get_reward_system() -> UnifiedRewardSystem:
    """Get the global unified reward system instance."""
    global _reward_system_instance
    if _reward_system_instance is None:
        _reward_system_instance = UnifiedRewardSystem()
    return _reward_system_instance


async def calculate_and_award_reward(user_id: str, source: RewardSource, 
                                    base_data: Dict[str, Any],
                                    is_gaming_context: bool = False) -> Dict[str, Any]:
    """Calculate and award rewards for a user action."""
    try:
        system = get_reward_system()
        
        # Create calculation context
        context = RewardCalculationContext(
            user_id=user_id,
            source=source,
            base_data=base_data,
            is_gaming_context=is_gaming_context
        )
        
        # Calculate rewards
        rewards = await system.calculate_reward(context)
        
        # Award rewards
        if rewards:
            result = await system.award_rewards(user_id, rewards)
            return result
        else:
            return {"success": False, "message": "No rewards calculated"}
            
    except Exception as e:
        logger.error(f"Error in calculate_and_award_reward: {e}")
        return {"success": False, "message": str(e)}
