"""Influencer Tycoon - Gaming Simulation System
=============================================

Immersive tycoon-style gaming system where content creators can simulate
and strategize their influencer empire growth through virtual mechanics,
asset management, and strategic decision-making gameplay.

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
Real Creator Data → Tycoon Simulation → Virtual Asset Management →
Strategic Upgrades → Passive Income → Growth Acceleration → Engagement Enhancement
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid
import asyncio
import random
import math

logger = logging.getLogger(__name__)


class TycoonAssetType(str, Enum):
    """Types of assets in the tycoon game."""
    CONTENT_STUDIO = "content_studio"
    EQUIPMENT = "equipment"
    VIRTUAL_ASSISTANT = "virtual_assistant"
    MARKETING_BOOST = "marketing_boost"
    COLLABORATION_HUB = "collaboration_hub"
    MONETIZATION_ENGINE = "monetization_engine"
    ANALYTICS_SUITE = "analytics_suite"
    BRAND_PARTNERSHIP = "brand_partnership"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    TALENT_SCOUT = "talent_scout"


class TycoonUpgradeType(str, Enum):
    """Types of upgrades available."""
    EFFICIENCY = "efficiency"
    CAPACITY = "capacity"
    QUALITY = "quality"
    AUTOMATION = "automation"
    REACH = "reach"
    ENGAGEMENT = "engagement"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"


class TycoonPlayerStatus(str, Enum):
    """Player status levels."""
    NOVICE = "novice"
    RISING = "rising"
    ESTABLISHED = "established"
    INFLUENCER = "influencer"
    CELEBRITY = "celebrity"
    LEGEND = "legend"


@dataclass
class TycoonAsset:
    """Represents an asset in the tycoon game."""
    asset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: TycoonAssetType = TycoonAssetType.CONTENT_STUDIO
    name: str = ""
    description: str = ""
    level: int = 1
    max_level: int = 10
    base_cost: Decimal = Decimal('1000')
    current_cost: Decimal = Decimal('1000')
    base_income: Decimal = Decimal('100')
    current_income: Decimal = Decimal('100')
    efficiency_multiplier: float = 1.0
    quality_multiplier: float = 1.0
    automation_level: float = 0.0
    unlock_requirements: Dict[str, Any] = field(default_factory=dict)
    purchased_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_income_generated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True


@dataclass
class TycoonUpgrade:
    """Represents an upgrade for assets."""
    upgrade_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    upgrade_type: TycoonUpgradeType = TycoonUpgradeType.EFFICIENCY
    name: str = ""
    description: str = ""
    target_asset_types: List[TycoonAssetType] = field(default_factory=list)
    cost: Decimal = Decimal('500')
    effect_multiplier: float = 1.2
    max_stack: int = 5
    current_stack: int = 0
    duration_hours: Optional[int] = None
    permanent: bool = True
    requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TycoonMetrics:
    """Player metrics and statistics."""
    player_id: str = ""
    total_income: Decimal = Decimal('0')
    passive_income_rate: Decimal = Decimal('0')
    total_spent: Decimal = Decimal('0')
    net_worth: Decimal = Decimal('0')
    assets_owned: int = 0
    total_upgrades: int = 0
    prestige_points: int = 0
    game_sessions: int = 0
    total_playtime_hours: float = 0.0
    highest_income_rate: Decimal = Decimal('0')
    fastest_growth_rate: float = 0.0
    efficiency_score: float = 0.0
    strategy_score: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TycoonPlayer:
    """Represents a player in the tycoon game."""
    player_id: str = ""
    user_id: str = ""
    username: str = ""
    display_name: str = ""
    avatar_url: Optional[str] = None
    current_cash: Decimal = Decimal('10000')
    total_income: Decimal = Decimal('0')
    player_level: int = 1
    experience_points: int = 0
    status: TycoonPlayerStatus = TycoonPlayerStatus.NOVICE
    assets: List[TycoonAsset] = field(default_factory=list)
    upgrades: List[TycoonUpgrade] = field(default_factory=list)
    metrics: TycoonMetrics = field(default_factory=TycoonMetrics)
    game_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    offline_progress_enabled: bool = True


class InfluencerTycoon:
    """
    Main tycoon game engine managing player progression, asset management,
    and income simulation for the influencer gaming experience.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.players: Dict[str, TycoonPlayer] = {}
        self.asset_templates: Dict[TycoonAssetType, Dict[str, Any]] = {}
        self.upgrade_templates: Dict[TycoonUpgradeType, Dict[str, Any]] = {}
        self.game_balance = self.config.get('game_balance', {})
        self.passive_income_rate = self.config.get('passive_income_rate', 1.0)
        self.offline_income_cap_hours = self.config.get('offline_income_cap_hours', 24)
        
        self._initialize_templates()
        logger.info("🎮 Influencer Tycoon initialized")
    
    def _initialize_templates(self):
        """Initialize asset and upgrade templates."""
        # Asset templates with balanced progression
        self.asset_templates = {
            TycoonAssetType.CONTENT_STUDIO: {
                "name": "Content Studio",
                "description": "Professional content creation space",
                "base_cost": Decimal('1000'),
                "base_income": Decimal('50'),
                "unlock_level": 1
            },
            TycoonAssetType.EQUIPMENT: {
                "name": "Professional Equipment",
                "description": "High-quality cameras, microphones, lighting",
                "base_cost": Decimal('2500'),
                "base_income": Decimal('120'),
                "unlock_level": 3
            },
            TycoonAssetType.VIRTUAL_ASSISTANT: {
                "name": "Virtual Assistant",
                "description": "AI-powered assistant for content management",
                "base_cost": Decimal('5000'),
                "base_income": Decimal('200'),
                "unlock_level": 5
            },
            TycoonAssetType.MARKETING_BOOST: {
                "name": "Marketing Campaign",
                "description": "Targeted advertising and promotion",
                "base_cost": Decimal('3000'),
                "base_income": Decimal('150'),
                "unlock_level": 4
            },
            TycoonAssetType.COLLABORATION_HUB: {
                "name": "Collaboration Hub",
                "description": "Platform for creator partnerships",
                "base_cost": Decimal('8000'),
                "base_income": Decimal('300'),
                "unlock_level": 7
            },
            TycoonAssetType.MONETIZATION_ENGINE: {
                "name": "Monetization Engine",
                "description": "Advanced revenue optimization system",
                "base_cost": Decimal('15000'),
                "base_income": Decimal('500'),
                "unlock_level": 10
            }
        }
        
        # Upgrade templates
        self.upgrade_templates = {
            TycoonUpgradeType.EFFICIENCY: {
                "name": "Efficiency Boost",
                "description": "Increases asset efficiency",
                "base_cost": Decimal('500'),
                "effect_multiplier": 1.15,
                "max_stack": 10
            },
            TycoonUpgradeType.AUTOMATION: {
                "name": "Automation System",
                "description": "Automates asset management",
                "base_cost": Decimal('1000'),
                "effect_multiplier": 1.25,
                "max_stack": 5
            },
            TycoonUpgradeType.QUALITY: {
                "name": "Quality Enhancement",
                "description": "Improves content quality",
                "base_cost": Decimal('750'),
                "effect_multiplier": 1.20,
                "max_stack": 8
            }
        }
    
    async def create_player(self, user_id: str, username: str, display_name: str = "") -> TycoonPlayer:
        """Create a new tycoon player."""
        try:
            player_id = str(uuid.uuid4())
            
            player = TycoonPlayer(
                player_id=player_id,
                user_id=user_id,
                username=username,
                display_name=display_name or username,
                current_cash=Decimal('10000'),  # Starting cash
                metrics=TycoonMetrics(player_id=player_id)
            )
            
            # Give starter assets
            starter_studio = await self._create_asset(TycoonAssetType.CONTENT_STUDIO, player)
            player.assets.append(starter_studio)
            
            self.players[player_id] = player
            
            logger.info(f"Created new tycoon player: {username} ({player_id})")
            return player
            
        except Exception as e:
            logger.error(f"Error creating tycoon player: {e}")
            raise
    
    async def _create_asset(self, asset_type: TycoonAssetType, player: TycoonPlayer, level: int = 1) -> TycoonAsset:
        """Create a new asset for a player."""
        template = self.asset_templates.get(asset_type, {})
        
        asset = TycoonAsset(
            asset_type=asset_type,
            name=template.get('name', asset_type.value),
            description=template.get('description', ''),
            level=level,
            base_cost=template.get('base_cost', Decimal('1000')),
            current_cost=template.get('base_cost', Decimal('1000')),
            base_income=template.get('base_income', Decimal('100')),
            current_income=template.get('base_income', Decimal('100'))
        )
        
        return asset
    
    async def purchase_asset(self, player_id: str, asset_type: TycoonAssetType) -> Dict[str, Any]:
        """Purchase a new asset for the player."""
        try:
            if player_id not in self.players:
                raise ValueError(f"Player {player_id} not found")
            
            player = self.players[player_id]
            template = self.asset_templates.get(asset_type)
            
            if not template:
                raise ValueError(f"Asset type {asset_type} not available")
            
            # Check if player meets requirements
            required_level = template.get('unlock_level', 1)
            if player.player_level < required_level:
                return {
                    "success": False,
                    "message": f"Requires player level {required_level}"
                }
            
            # Calculate cost (increases with each owned asset of same type)
            owned_count = sum(1 for asset in player.assets if asset.asset_type == asset_type)
            cost_multiplier = 1.5 ** owned_count
            final_cost = template['base_cost'] * Decimal(str(cost_multiplier))
            
            if player.current_cash < final_cost:
                return {
                    "success": False,
                    "message": f"Insufficient funds. Need {final_cost}, have {player.current_cash}"
                }
            
            # Purchase asset
            asset = await self._create_asset(asset_type, player)
            asset.current_cost = final_cost
            
            player.assets.append(asset)
            player.current_cash -= final_cost
            player.metrics.total_spent += final_cost
            player.metrics.assets_owned += 1
            
            # Update player level based on total spent
            await self._update_player_level(player)
            
            logger.info(f"Player {player.username} purchased {asset.name} for {final_cost}")
            
            return {
                "success": True,
                "asset": asset,
                "remaining_cash": player.current_cash,
                "new_level": player.player_level
            }
            
        except Exception as e:
            logger.error(f"Error purchasing asset: {e}")
            return {"success": False, "message": str(e)}
    
    async def upgrade_asset(self, player_id: str, asset_id: str, upgrade_type: TycoonUpgradeType) -> Dict[str, Any]:
        """Upgrade an existing asset."""
        try:
            if player_id not in self.players:
                raise ValueError(f"Player {player_id} not found")
            
            player = self.players[player_id]
            asset = next((a for a in player.assets if a.asset_id == asset_id), None)
            
            if not asset:
                return {"success": False, "message": "Asset not found"}
            
            if asset.level >= asset.max_level:
                return {"success": False, "message": "Asset already at max level"}
            
            # Calculate upgrade cost
            upgrade_cost = Decimal('500') * (asset.level ** 1.2)
            
            if player.current_cash < upgrade_cost:
                return {
                    "success": False,
                    "message": f"Insufficient funds. Need {upgrade_cost}"
                }
            
            # Apply upgrade
            player.current_cash -= upgrade_cost
            player.metrics.total_spent += upgrade_cost
            player.metrics.total_upgrades += 1
            
            asset.level += 1
            
            # Update asset stats based on upgrade type
            if upgrade_type == TycoonUpgradeType.EFFICIENCY:
                asset.efficiency_multiplier *= 1.15
            elif upgrade_type == TycoonUpgradeType.QUALITY:
                asset.quality_multiplier *= 1.20
            elif upgrade_type == TycoonUpgradeType.AUTOMATION:
                asset.automation_level = min(1.0, asset.automation_level + 0.1)
            
            # Recalculate income
            asset.current_income = asset.base_income * Decimal(str(
                asset.efficiency_multiplier * asset.quality_multiplier * (1 + asset.automation_level)
            ))
            
            await self._update_player_level(player)
            
            return {
                "success": True,
                "asset": asset,
                "cost": upgrade_cost,
                "remaining_cash": player.current_cash
            }
            
        except Exception as e:
            logger.error(f"Error upgrading asset: {e}")
            return {"success": False, "message": str(e)}
    
    async def calculate_passive_income(self, player_id: str) -> Decimal:
        """Calculate current passive income rate for a player."""
        try:
            if player_id not in self.players:
                return Decimal('0')
            
            player = self.players[player_id]
            total_income = Decimal('0')
            
            for asset in player.assets:
                if asset.active:
                    total_income += asset.current_income
            
            # Apply global multipliers
            total_income *= Decimal(str(self.passive_income_rate))
            
            player.metrics.passive_income_rate = total_income
            return total_income
            
        except Exception as e:
            logger.error(f"Error calculating passive income: {e}")
            return Decimal('0')
    
    async def process_offline_progress(self, player_id: str) -> Dict[str, Any]:
        """Process income earned while player was offline."""
        try:
            if player_id not in self.players:
                return {"income_earned": Decimal('0'), "hours_offline": 0}
            
            player = self.players[player_id]
            
            if not player.offline_progress_enabled:
                return {"income_earned": Decimal('0'), "hours_offline": 0}
            
            now = datetime.now(timezone.utc)
            offline_duration = now - player.last_active
            hours_offline = offline_duration.total_seconds() / 3600
            
            # Cap offline earnings
            capped_hours = min(hours_offline, self.offline_income_cap_hours)
            
            passive_income_rate = await self.calculate_passive_income(player_id)
            income_earned = passive_income_rate * Decimal(str(capped_hours))
            
            # Apply offline efficiency (reduced rate)
            offline_efficiency = 0.7  # 70% efficiency while offline
            income_earned *= Decimal(str(offline_efficiency))
            
            player.current_cash += income_earned
            player.metrics.total_income += income_earned
            player.last_active = now
            
            logger.info(f"Player {player.username} earned {income_earned} while offline for {hours_offline:.1f}h")
            
            return {
                "income_earned": income_earned,
                "hours_offline": hours_offline,
                "capped_hours": capped_hours,
                "new_cash": player.current_cash
            }
            
        except Exception as e:
            logger.error(f"Error processing offline progress: {e}")
            return {"income_earned": Decimal('0'), "hours_offline": 0}
    
    async def _update_player_level(self, player: TycoonPlayer):
        """Update player level based on progress."""
        # Simple level calculation based on total spent
        total_spent = float(player.metrics.total_spent)
        new_level = max(1, int(math.log(total_spent / 1000 + 1) * 5) + 1)
        
        if new_level > player.player_level:
            old_level = player.player_level
            player.player_level = new_level
            player.experience_points += (new_level - old_level) * 100
            
            # Update status based on level
            if new_level >= 50:
                player.status = TycoonPlayerStatus.LEGEND
            elif new_level >= 40:
                player.status = TycoonPlayerStatus.CELEBRITY
            elif new_level >= 30:
                player.status = TycoonPlayerStatus.INFLUENCER
            elif new_level >= 20:
                player.status = TycoonPlayerStatus.ESTABLISHED
            elif new_level >= 10:
                player.status = TycoonPlayerStatus.RISING
            
            logger.info(f"Player {player.username} leveled up: {old_level} → {new_level}")
    
    async def simulate_growth(self, player_id: str, simulation_hours: float = 1.0) -> Dict[str, Any]:
        """Simulate growth and income generation over time."""
        try:
            if player_id not in self.players:
                return {"success": False, "message": "Player not found"}
            
            player = self.players[player_id]
            passive_rate = await self.calculate_passive_income(player_id)
            
            # Simulate income generation
            income_generated = passive_rate * Decimal(str(simulation_hours))
            
            # Add some randomness for realism
            random_factor = random.uniform(0.8, 1.2)
            income_generated *= Decimal(str(random_factor))
            
            player.current_cash += income_generated
            player.metrics.total_income += income_generated
            
            # Update metrics
            if income_generated > player.metrics.highest_income_rate:
                player.metrics.highest_income_rate = income_generated
            
            player.metrics.last_updated = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "income_generated": income_generated,
                "new_cash": player.current_cash,
                "passive_rate": passive_rate,
                "simulation_hours": simulation_hours
            }
            
        except Exception as e:
            logger.error(f"Error simulating growth: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_player_stats(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive player statistics."""
        try:
            if player_id not in self.players:
                return None
            
            player = self.players[player_id]
            passive_income = await self.calculate_passive_income(player_id)
            
            # Calculate net worth
            asset_value = sum(float(asset.current_cost) * 0.7 for asset in player.assets)  # Assets worth 70% of purchase price
            net_worth = float(player.current_cash) + asset_value
            
            return {
                "player_id": player.player_id,
                "username": player.username,
                "level": player.player_level,
                "status": player.status.value,
                "current_cash": float(player.current_cash),
                "passive_income_rate": float(passive_income),
                "net_worth": net_worth,
                "assets_owned": len(player.assets),
                "total_income": float(player.metrics.total_income),
                "total_spent": float(player.metrics.total_spent),
                "experience_points": player.experience_points,
                "efficiency_score": player.metrics.efficiency_score,
                "last_active": player.last_active.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting player stats: {e}")
            return None


# Global instance
_tycoon_instance: Optional[InfluencerTycoon] = None


def get_tycoon_game() -> InfluencerTycoon:
    """Get the global tycoon game instance."""
    global _tycoon_instance
    if _tycoon_instance is None:
        _tycoon_instance = InfluencerTycoon()
    return _tycoon_instance


async def simulate_growth(player_id: str, hours: float = 1.0) -> Dict[str, Any]:
    """Simulate growth for a player."""
    tycoon = get_tycoon_game()
    return await tycoon.simulate_growth(player_id, hours)


async def calculate_passive_income(player_id: str) -> Decimal:
    """Calculate passive income for a player."""
    tycoon = get_tycoon_game()
    return await tycoon.calculate_passive_income(player_id)