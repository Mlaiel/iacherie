"""Gaming Reward System - Specialized Gaming Rewards
==================================================

Advanced gaming-specific reward system providing virtual currencies,
gaming achievements rewards, competitive bonuses, and immersive
gaming mechanics for the influencer tycoon experience.

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
Gaming Actions → Gaming Reward Calculation → Virtual Currency → Gaming Progression →
Competitive Bonuses → Seasonal Rewards → Real Benefit Conversion → Engagement Enhancement
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import asyncio
import random
import math

logger = logging.getLogger(__name__)


class GamingRewardType(str, Enum):
    """Types of gaming rewards."""
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


class GamingRewardTier(str, Enum):
    """Reward tier classifications."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    DIVINE = "divine"


class GamingCurrency(str, Enum):
    """Gaming currency types."""
    TYCOON_CASH = "tycoon_cash"
    GAMING_GEMS = "gaming_gems"
    PRESTIGE_POINTS = "prestige_points"
    COMPETITIVE_TOKENS = "competitive_tokens"
    SEASONAL_CURRENCY = "seasonal_currency"
    PREMIUM_CREDITS = "premium_credits"
    COLLECTOR_COINS = "collector_coins"


class GamingRewardSource(str, Enum):
    """Sources of gaming rewards."""
    TYCOON_PROGRESS = "tycoon_progress"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    COMPETITIVE_RANKING = "competitive_ranking"
    DAILY_LOGIN = "daily_login"
    SEASONAL_EVENT = "seasonal_event"
    SPECIAL_CHALLENGE = "special_challenge"
    MILESTONE_REACHED = "milestone_reached"
    TOURNAMENT_WIN = "tournament_win"
    COMMUNITY_EVENT = "community_event"
    RARE_ACTION = "rare_action"


class GamingRewardStatus(str, Enum):
    """Status of gaming rewards."""
    PENDING = "pending"
    AVAILABLE = "available"
    CLAIMED = "claimed"
    EXPIRED = "expired"
    LOCKED = "locked"
    PROCESSING = "processing"


@dataclass
class GamingReward:
    """Represents a gaming reward."""
    reward_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str = ""
    reward_type: GamingRewardType = GamingRewardType.VIRTUAL_CURRENCY
    currency_type: GamingCurrency = GamingCurrency.TYCOON_CASH
    amount: Decimal = Decimal('0')
    tier: GamingRewardTier = GamingRewardTier.COMMON
    source: GamingRewardSource = GamingRewardSource.TYCOON_PROGRESS
    status: GamingRewardStatus = GamingRewardStatus.PENDING
    name: str = ""
    description: str = ""
    rarity_multiplier: float = 1.0
    bonus_multiplier: float = 1.0
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    claimed_at: Optional[datetime] = None
    requirements_met: bool = True
    unlock_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GamingRewardMultiplier:
    """Gaming reward multiplier configuration."""
    multiplier_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    multiplier_value: float = 1.0
    applicable_types: List[GamingRewardType] = field(default_factory=list)
    applicable_sources: List[GamingRewardSource] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    duration_hours: Optional[int] = None
    max_applications: Optional[int] = None
    applications_used: int = 0
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


@dataclass
class GamingRewardBundle:
    """Bundle of multiple gaming rewards."""
    bundle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    rewards: List[GamingReward] = field(default_factory=list)
    tier: GamingRewardTier = GamingRewardTier.COMMON
    bundle_bonus_multiplier: float = 1.0
    unlock_requirements: Dict[str, Any] = field(default_factory=dict)
    limited_quantity: Optional[int] = None
    remaining_quantity: Optional[int] = None
    available_from: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    available_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PlayerGamingWallet:
    """Player's gaming currency wallet."""
    player_id: str = ""
    currencies: Dict[GamingCurrency, Decimal] = field(default_factory=dict)
    total_earned: Dict[GamingCurrency, Decimal] = field(default_factory=dict)
    total_spent: Dict[GamingCurrency, Decimal] = field(default_factory=dict)
    transaction_history: List[Dict[str, Any]] = field(default_factory=list)
    active_multipliers: List[GamingRewardMultiplier] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize default currency balances."""
        for currency in GamingCurrency:
            if currency not in self.currencies:
                self.currencies[currency] = Decimal('0')
            if currency not in self.total_earned:
                self.total_earned[currency] = Decimal('0')
            if currency not in self.total_spent:
                self.total_spent[currency] = Decimal('0')


class GamingRewardSystem:
    """
    Advanced gaming reward system managing virtual currencies,
    competitive rewards, and immersive gaming mechanics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.player_wallets: Dict[str, PlayerGamingWallet] = {}
        self.reward_templates: Dict[str, Dict[str, Any]] = {}
        self.active_multipliers: List[GamingRewardMultiplier] = []
        self.seasonal_bonuses: Dict[str, float] = {}
        self.rarity_rates: Dict[GamingRewardTier, float] = {}
        self.conversion_rates: Dict[Tuple[GamingCurrency, GamingCurrency], float] = {}
        
        self._initialize_reward_system()
        logger.info("🎮 Gaming Reward System initialized")
    
    def _initialize_reward_system(self):
        """Initialize the gaming reward system with templates and rates."""
        # Initialize rarity rates
        self.rarity_rates = {
            GamingRewardTier.COMMON: 0.65,      # 65% chance
            GamingRewardTier.UNCOMMON: 0.25,    # 25% chance
            GamingRewardTier.RARE: 0.08,        # 8% chance
            GamingRewardTier.EPIC: 0.015,       # 1.5% chance
            GamingRewardTier.LEGENDARY: 0.004,  # 0.4% chance
            GamingRewardTier.MYTHICAL: 0.0009,  # 0.09% chance
            GamingRewardTier.DIVINE: 0.0001     # 0.01% chance
        }
        
        # Initialize reward templates
        self.reward_templates = {
            "tycoon_milestone": {
                "base_amount": Decimal('1000'),
                "currency": GamingCurrency.TYCOON_CASH,
                "tier": GamingRewardTier.COMMON,
                "scaling_factor": 1.5
            },
            "achievement_unlock": {
                "base_amount": Decimal('500'),
                "currency": GamingCurrency.GAMING_GEMS,
                "tier": GamingRewardTier.RARE,
                "scaling_factor": 2.0
            },
            "competitive_victory": {
                "base_amount": Decimal('2000'),
                "currency": GamingCurrency.COMPETITIVE_TOKENS,
                "tier": GamingRewardTier.EPIC,
                "scaling_factor": 1.8
            },
            "daily_login": {
                "base_amount": Decimal('100'),
                "currency": GamingCurrency.GAMING_GEMS,
                "tier": GamingRewardTier.COMMON,
                "scaling_factor": 1.1
            }
        }
        
        # Initialize currency conversion rates
        self.conversion_rates = {
            (GamingCurrency.GAMING_GEMS, GamingCurrency.TYCOON_CASH): 10.0,
            (GamingCurrency.PRESTIGE_POINTS, GamingCurrency.GAMING_GEMS): 5.0,
            (GamingCurrency.COMPETITIVE_TOKENS, GamingCurrency.PREMIUM_CREDITS): 2.5,
            (GamingCurrency.SEASONAL_CURRENCY, GamingCurrency.GAMING_GEMS): 3.0
        }
    
    async def create_player_wallet(self, player_id: str) -> PlayerGamingWallet:
        """Create a new gaming wallet for a player."""
        try:
            if player_id in self.player_wallets:
                return self.player_wallets[player_id]
            
            wallet = PlayerGamingWallet(player_id=player_id)
            
            # Give starting currencies
            wallet.currencies[GamingCurrency.TYCOON_CASH] = Decimal('10000')
            wallet.currencies[GamingCurrency.GAMING_GEMS] = Decimal('100')
            
            self.player_wallets[player_id] = wallet
            
            logger.info(f"Created gaming wallet for player: {player_id}")
            return wallet
            
        except Exception as e:
            logger.error(f"Error creating player wallet: {e}")
            raise
    
    async def calculate_gaming_rewards(
        self,
        player_id: str,
        source: GamingRewardSource,
        base_amount: Decimal,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[GamingReward]:
        """Calculate gaming rewards based on action and context."""
        try:
            metadata = metadata or {}
            rewards = []
            
            # Get player wallet
            wallet = await self.get_player_wallet(player_id)
            
            # Determine reward tier based on rarity
            tier = self._determine_reward_tier()
            
            # Get template for reward calculation
            template_key = self._get_template_key(source)
            template = self.reward_templates.get(template_key, {})
            
            # Calculate final amount with multipliers
            final_amount = await self._calculate_final_amount(
                base_amount, tier, source, wallet, metadata
            )
            
            # Determine currency type
            currency_type = template.get('currency', GamingCurrency.TYCOON_CASH)
            
            # Create main reward
            main_reward = GamingReward(
                player_id=player_id,
                reward_type=GamingRewardType.VIRTUAL_CURRENCY,
                currency_type=currency_type,
                amount=final_amount,
                tier=tier,
                source=source,
                name=f"{source.value.replace('_', ' ').title()} Reward",
                description=f"Earned from {source.value.replace('_', ' ')}",
                rarity_multiplier=self._get_tier_multiplier(tier),
                metadata=metadata
            )
            
            rewards.append(main_reward)
            
            # Add bonus rewards for higher tiers
            if tier in [GamingRewardTier.EPIC, GamingRewardTier.LEGENDARY, GamingRewardTier.MYTHICAL, GamingRewardTier.DIVINE]:
                bonus_rewards = await self._generate_bonus_rewards(player_id, tier, source)
                rewards.extend(bonus_rewards)
            
            logger.info(f"Calculated {len(rewards)} gaming rewards for player {player_id}")
            return rewards
            
        except Exception as e:
            logger.error(f"Error calculating gaming rewards: {e}")
            return []
    
    def _determine_reward_tier(self) -> GamingRewardTier:
        """Determine reward tier based on rarity rates."""
        rand = random.random()
        cumulative = 0.0
        
        for tier, rate in self.rarity_rates.items():
            cumulative += rate
            if rand <= cumulative:
                return tier
        
        return GamingRewardTier.COMMON
    
    def _get_template_key(self, source: GamingRewardSource) -> str:
        """Get template key based on reward source."""
        source_mapping = {
            GamingRewardSource.TYCOON_PROGRESS: "tycoon_milestone",
            GamingRewardSource.ACHIEVEMENT_UNLOCK: "achievement_unlock",
            GamingRewardSource.COMPETITIVE_RANKING: "competitive_victory",
            GamingRewardSource.DAILY_LOGIN: "daily_login",
            GamingRewardSource.TOURNAMENT_WIN: "competitive_victory",
            GamingRewardSource.MILESTONE_REACHED: "tycoon_milestone"
        }
        return source_mapping.get(source, "tycoon_milestone")
    
    async def _calculate_final_amount(
        self,
        base_amount: Decimal,
        tier: GamingRewardTier,
        source: GamingRewardSource,
        wallet: PlayerGamingWallet,
        metadata: Dict[str, Any]
    ) -> Decimal:
        """Calculate final reward amount with all multipliers."""
        amount = base_amount
        
        # Apply tier multiplier
        tier_multiplier = self._get_tier_multiplier(tier)
        amount *= Decimal(str(tier_multiplier))
        
        # Apply active multipliers
        for multiplier in wallet.active_multipliers:
            if self._multiplier_applies(multiplier, source):
                amount *= Decimal(str(multiplier.multiplier_value))
        
        # Apply seasonal bonuses
        season = metadata.get('season', 'default')
        seasonal_bonus = self.seasonal_bonuses.get(season, 1.0)
        amount *= Decimal(str(seasonal_bonus))
        
        # Apply streak bonuses
        streak = metadata.get('streak', 1)
        streak_bonus = min(2.0, 1.0 + (streak - 1) * 0.1)  # Max 2x bonus
        amount *= Decimal(str(streak_bonus))
        
        return amount.quantize(Decimal('0.01'))
    
    def _get_tier_multiplier(self, tier: GamingRewardTier) -> float:
        """Get multiplier based on reward tier."""
        multipliers = {
            GamingRewardTier.COMMON: 1.0,
            GamingRewardTier.UNCOMMON: 1.5,
            GamingRewardTier.RARE: 2.0,
            GamingRewardTier.EPIC: 3.5,
            GamingRewardTier.LEGENDARY: 6.0,
            GamingRewardTier.MYTHICAL: 10.0,
            GamingRewardTier.DIVINE: 20.0
        }
        return multipliers.get(tier, 1.0)
    
    def _multiplier_applies(self, multiplier: GamingRewardMultiplier, source: GamingRewardSource) -> bool:
        """Check if a multiplier applies to a reward source."""
        if not multiplier.active:
            return False
        
        if multiplier.expires_at and datetime.now(timezone.utc) > multiplier.expires_at:
            multiplier.active = False
            return False
        
        if multiplier.max_applications and multiplier.applications_used >= multiplier.max_applications:
            return False
        
        if multiplier.applicable_sources and source not in multiplier.applicable_sources:
            return False
        
        return True
    
    async def _generate_bonus_rewards(
        self,
        player_id: str,
        tier: GamingRewardTier,
        source: GamingRewardSource
    ) -> List[GamingReward]:
        """Generate bonus rewards for higher tier rewards."""
        bonus_rewards = []
        
        if tier in [GamingRewardTier.EPIC, GamingRewardTier.LEGENDARY]:
            # Add gaming gems bonus
            gems_reward = GamingReward(
                player_id=player_id,
                reward_type=GamingRewardType.VIRTUAL_CURRENCY,
                currency_type=GamingCurrency.GAMING_GEMS,
                amount=Decimal('50') * Decimal(str(self._get_tier_multiplier(tier))),
                tier=tier,
                source=source,
                name="Bonus Gaming Gems",
                description="Bonus reward for exceptional achievement"
            )
            bonus_rewards.append(gems_reward)
        
        if tier in [GamingRewardTier.LEGENDARY, GamingRewardTier.MYTHICAL, GamingRewardTier.DIVINE]:
            # Add prestige points
            prestige_reward = GamingReward(
                player_id=player_id,
                reward_type=GamingRewardType.VIRTUAL_CURRENCY,
                currency_type=GamingCurrency.PRESTIGE_POINTS,
                amount=Decimal('10') * Decimal(str(self._get_tier_multiplier(tier))),
                tier=tier,
                source=source,
                name="Prestige Points",
                description="Rare prestige points for legendary achievement"
            )
            bonus_rewards.append(prestige_reward)
        
        if tier == GamingRewardTier.DIVINE:
            # Add premium credits for divine tier
            premium_reward = GamingReward(
                player_id=player_id,
                reward_type=GamingRewardType.VIRTUAL_CURRENCY,
                currency_type=GamingCurrency.PREMIUM_CREDITS,
                amount=Decimal('5'),
                tier=tier,
                source=source,
                name="Premium Credits",
                description="Exclusive premium credits for divine achievement"
            )
            bonus_rewards.append(premium_reward)
        
        return bonus_rewards
    
    async def process_gaming_rewards(self, player_id: str, rewards: List[GamingReward]) -> Dict[str, Any]:
        """Process and distribute gaming rewards to a player."""
        try:
            wallet = await self.get_player_wallet(player_id)
            processed_rewards = []
            total_value = Decimal('0')
            
            for reward in rewards:
                if reward.status == GamingRewardStatus.PENDING and reward.requirements_met:
                    # Add currency to wallet
                    current_amount = wallet.currencies.get(reward.currency_type, Decimal('0'))
                    wallet.currencies[reward.currency_type] = current_amount + reward.amount
                    
                    # Update totals
                    current_total = wallet.total_earned.get(reward.currency_type, Decimal('0'))
                    wallet.total_earned[reward.currency_type] = current_total + reward.amount
                    
                    # Add transaction to history
                    transaction = {
                        "reward_id": reward.reward_id,
                        "currency": reward.currency_type.value,
                        "amount": float(reward.amount),
                        "source": reward.source.value,
                        "tier": reward.tier.value,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    wallet.transaction_history.append(transaction)
                    
                    # Update reward status
                    reward.status = GamingRewardStatus.CLAIMED
                    reward.claimed_at = datetime.now(timezone.utc)
                    
                    processed_rewards.append(reward)
                    total_value += reward.amount
                    
                    logger.info(f"Processed gaming reward: {reward.amount} {reward.currency_type.value} for player {player_id}")
            
            wallet.last_updated = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "processed_count": len(processed_rewards),
                "total_value": float(total_value),
                "wallet_balances": {k.value: float(v) for k, v in wallet.currencies.items()},
                "rewards": [{"id": r.reward_id, "amount": float(r.amount), "currency": r.currency_type.value} for r in processed_rewards]
            }
            
        except Exception as e:
            logger.error(f"Error processing gaming rewards: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_player_wallet(self, player_id: str) -> PlayerGamingWallet:
        """Get or create a player's gaming wallet."""
        if player_id not in self.player_wallets:
            return await self.create_player_wallet(player_id)
        return self.player_wallets[player_id]
    
    async def convert_currency(
        self,
        player_id: str,
        from_currency: GamingCurrency,
        to_currency: GamingCurrency,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Convert between gaming currencies."""
        try:
            wallet = await self.get_player_wallet(player_id)
            conversion_key = (from_currency, to_currency)
            
            if conversion_key not in self.conversion_rates:
                return {"success": False, "message": "Conversion not available"}
            
            rate = self.conversion_rates[conversion_key]
            current_balance = wallet.currencies.get(from_currency, Decimal('0'))
            
            if current_balance < amount:
                return {"success": False, "message": "Insufficient balance"}
            
            converted_amount = amount * Decimal(str(rate))
            
            # Update balances
            wallet.currencies[from_currency] -= amount
            wallet.currencies[to_currency] = wallet.currencies.get(to_currency, Decimal('0')) + converted_amount
            
            # Add transaction
            transaction = {
                "type": "conversion",
                "from_currency": from_currency.value,
                "to_currency": to_currency.value,
                "from_amount": float(amount),
                "to_amount": float(converted_amount),
                "rate": rate,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            wallet.transaction_history.append(transaction)
            wallet.last_updated = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "converted_amount": float(converted_amount),
                "rate": rate,
                "new_balances": {
                    from_currency.value: float(wallet.currencies[from_currency]),
                    to_currency.value: float(wallet.currencies[to_currency])
                }
            }
            
        except Exception as e:
            logger.error(f"Error converting currency: {e}")
            return {"success": False, "message": str(e)}
    
    async def add_multiplier(self, player_id: str, multiplier: GamingRewardMultiplier) -> bool:
        """Add a reward multiplier for a player."""
        try:
            wallet = await self.get_player_wallet(player_id)
            
            # Set expiration if duration is specified
            if multiplier.duration_hours:
                multiplier.expires_at = datetime.now(timezone.utc) + timedelta(hours=multiplier.duration_hours)
            
            wallet.active_multipliers.append(multiplier)
            logger.info(f"Added gaming reward multiplier for player {player_id}: {multiplier.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding multiplier: {e}")
            return False
    
    async def get_player_stats(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive gaming reward statistics for a player."""
        try:
            wallet = await self.get_player_wallet(player_id)
            
            total_earned_value = sum(
                float(amount) * self.conversion_rates.get((currency, GamingCurrency.GAMING_GEMS), 1.0)
                for currency, amount in wallet.total_earned.items()
            )
            
            return {
                "player_id": player_id,
                "balances": {k.value: float(v) for k, v in wallet.currencies.items()},
                "total_earned": {k.value: float(v) for k, v in wallet.total_earned.items()},
                "total_spent": {k.value: float(v) for k, v in wallet.total_spent.items()},
                "total_earned_value": total_earned_value,
                "active_multipliers": len(wallet.active_multipliers),
                "transaction_count": len(wallet.transaction_history),
                "last_updated": wallet.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return None


# Global instance
_gaming_rewards_instance: Optional[GamingRewardSystem] = None


def get_gaming_rewards() -> GamingRewardSystem:
    """Get the global gaming reward system instance."""
    global _gaming_rewards_instance
    if _gaming_rewards_instance is None:
        _gaming_rewards_instance = GamingRewardSystem()
    return _gaming_rewards_instance


async def calculate_gaming_rewards(
    player_id: str,
    source: GamingRewardSource,
    base_amount: Decimal,
    metadata: Optional[Dict[str, Any]] = None
) -> List[GamingReward]:
    """Calculate gaming rewards for a player."""
    system = get_gaming_rewards()
    return await system.calculate_gaming_rewards(player_id, source, base_amount, metadata)


async def process_gaming_rewards(player_id: str, rewards: List[GamingReward]) -> Dict[str, Any]:
    """Process and distribute gaming rewards."""
    system = get_gaming_rewards()
    return await system.process_gaming_rewards(player_id, rewards)