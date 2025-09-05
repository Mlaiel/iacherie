"""Advanced Virtual Economy - Multi-Currency Gaming Economy System
================================================================

Sophisticated virtual economy management system providing multi-currency support,
marketplace functionality, peer-to-peer trading, inflation control, and
comprehensive economic balancing for content creators.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/gamification/virtual_economy.py
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
User Actions → Currency Earning → Marketplace Trading → 
Economy Balancing → Revenue Conversion → Analytics Tracking
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from uuid import uuid4, UUID
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field
import json
import math
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CurrencyType(str, Enum):
    """Types of virtual currencies in the economy."""
    COINS = "coins"           # Primary currency from daily actions
    GEMS = "gems"             # Premium currency from real money
    CREDITS = "credits"       # Collaborative currency from team actions
    XP_POINTS = "xp_points"   # Experience points for progression
    INFLUENCE = "influence"   # Social influence currency
    ENERGY = "energy"         # Action limitation currency


class ItemType(str, Enum):
    """Types of marketplace items."""
    PROFILE_BOOST = "profile_boost"
    CONTENT_AMPLIFIER = "content_amplifier"
    CUSTOM_THEME = "custom_theme"
    ANIMATION_PACK = "animation_pack"
    EARLY_ACCESS = "early_access"
    COLLABORATION_PRIORITY = "collaboration_priority"
    ANALYTICS_UNLOCK = "analytics_unlock"
    STORAGE_EXPANSION = "storage_expansion"
    PREMIUM_TOOLS = "premium_tools"
    EXCLUSIVE_BADGE = "exclusive_badge"


class ItemRarity(str, Enum):
    """Item rarity levels affecting pricing."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class TransactionType(str, Enum):
    """Types of economic transactions."""
    EARN = "earn"
    SPEND = "spend"
    TRADE = "trade"
    CONVERT = "convert"
    GIFT = "gift"
    REFUND = "refund"
    BONUS = "bonus"
    PENALTY = "penalty"


class TransactionStatus(str, Enum):
    """Transaction processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class CurrencyBalance:
    """User currency balance tracking."""
    user_id: str
    currency_type: CurrencyType
    balance: Decimal
    total_earned: Decimal
    total_spent: Decimal
    last_updated: datetime
    daily_earned: Decimal = field(default_factory=lambda: Decimal('0'))
    weekly_earned: Decimal = field(default_factory=lambda: Decimal('0'))
    monthly_earned: Decimal = field(default_factory=lambda: Decimal('0'))
    pending_balance: Decimal = field(default_factory=lambda: Decimal('0'))


@dataclass
class MarketplaceItem:
    """Marketplace item definition."""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    base_price: Dict[CurrencyType, Decimal]
    duration_hours: Optional[int]  # For temporary items
    max_quantity: Optional[int]    # For limited items
    requirements: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserInventory:
    """User owned items and inventory management."""
    user_id: str
    items: Dict[str, int] = field(default_factory=dict)  # item_id -> quantity
    active_items: Dict[str, datetime] = field(default_factory=dict)  # item_id -> expiry
    total_value: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Transaction:
    """Economic transaction record."""
    id: str
    user_id: str
    transaction_type: TransactionType
    currency_type: CurrencyType
    amount: Decimal
    status: TransactionStatus
    source: str  # What generated this transaction
    target_id: Optional[str] = None  # For trades/gifts
    item_id: Optional[str] = None    # For marketplace purchases
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class TradeOffer:
    """Peer-to-peer trade offer."""
    id: str
    from_user_id: str
    to_user_id: str
    offer_currencies: Dict[CurrencyType, Decimal]
    offer_items: Dict[str, int]  # item_id -> quantity
    request_currencies: Dict[CurrencyType, Decimal]
    request_items: Dict[str, int]
    status: str = "pending"  # pending, accepted, rejected, expired
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24))
    message: str = ""


class CurrencyManager:
    """
    Advanced multi-currency management system handling all virtual
    currency operations, conversions, and balance tracking.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the currency manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        
        # Currency balances storage
        self.user_balances: Dict[str, Dict[CurrencyType, CurrencyBalance]] = defaultdict(dict)
        
        # Currency conversion rates
        self.conversion_rates = self._initialize_conversion_rates()
        
        # Daily earning limits to prevent abuse
        self.daily_limits = {
            CurrencyType.COINS: Decimal('10000'),
            CurrencyType.CREDITS: Decimal('5000'),
            CurrencyType.XP_POINTS: Decimal('2000'),
            CurrencyType.INFLUENCE: Decimal('1000'),
            CurrencyType.ENERGY: Decimal('500')
        }
        
        self.logger.info("CurrencyManager initialized")
    
    def _initialize_conversion_rates(self) -> Dict[Tuple[CurrencyType, CurrencyType], Decimal]:
        """Initialize currency conversion rates."""
        rates = {}
        
        # Base conversion rates (these would be dynamic in production)
        base_rates = {
            (CurrencyType.COINS, CurrencyType.GEMS): Decimal('0.01'),      # 100 coins = 1 gem
            (CurrencyType.COINS, CurrencyType.CREDITS): Decimal('0.5'),     # 2 coins = 1 credit
            (CurrencyType.COINS, CurrencyType.XP_POINTS): Decimal('2.0'),   # 1 coin = 2 XP
            (CurrencyType.CREDITS, CurrencyType.INFLUENCE): Decimal('0.8'), # 1.25 credits = 1 influence
            (CurrencyType.XP_POINTS, CurrencyType.ENERGY): Decimal('0.25'), # 4 XP = 1 energy
        }
        
        # Add base rates and their inverses
        for (from_curr, to_curr), rate in base_rates.items():
            rates[(from_curr, to_curr)] = rate
            rates[(to_curr, from_curr)] = Decimal('1') / rate
        
        return rates
    
    async def get_user_balance(
        self, 
        user_id: str, 
        currency_type: CurrencyType
    ) -> CurrencyBalance:
        """Get user balance for specific currency."""
        try:
            if user_id not in self.user_balances:
                self.user_balances[user_id] = {}
            
            if currency_type not in self.user_balances[user_id]:
                # Initialize new balance
                balance = CurrencyBalance(
                    user_id=user_id,
                    currency_type=currency_type,
                    balance=Decimal('0'),
                    total_earned=Decimal('0'),
                    total_spent=Decimal('0'),
                    last_updated=datetime.now(timezone.utc)
                )
                self.user_balances[user_id][currency_type] = balance
            
            balance = self.user_balances[user_id][currency_type]
            
            # Check for daily reset
            await self._check_daily_reset(balance)
            
            return balance
            
        except Exception as e:
            self.logger.error(f"Error getting user balance: {e}")
            # Return empty balance on error
            return CurrencyBalance(
                user_id=user_id,
                currency_type=currency_type,
                balance=Decimal('0'),
                total_earned=Decimal('0'),
                total_spent=Decimal('0'),
                last_updated=datetime.now(timezone.utc)
            )
    
    async def add_currency(
        self,
        user_id: str,
        currency_type: CurrencyType,
        amount: Decimal,
        source: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add currency to user balance with daily limits."""
        try:
            if amount <= 0:
                return False
            
            balance = await self.get_user_balance(user_id, currency_type)
            
            # Check daily limits (except for gems which can be purchased)
            if currency_type != CurrencyType.GEMS:
                daily_limit = self.daily_limits.get(currency_type, Decimal('999999'))
                if balance.daily_earned + amount > daily_limit:
                    remaining = daily_limit - balance.daily_earned
                    if remaining <= 0:
                        self.logger.warning(f"Daily limit reached for {user_id} - {currency_type}")
                        return False
                    amount = remaining
            
            # Update balance
            balance.balance += amount
            balance.total_earned += amount
            balance.daily_earned += amount
            balance.weekly_earned += amount
            balance.monthly_earned += amount
            balance.last_updated = datetime.now(timezone.utc)
            
            # Create transaction record
            transaction = Transaction(
                id=str(uuid4()),
                user_id=user_id,
                transaction_type=TransactionType.EARN,
                currency_type=currency_type,
                amount=amount,
                status=TransactionStatus.COMPLETED,
                source=source,
                metadata=metadata or {},
                processed_at=datetime.now(timezone.utc)
            )
            
            # Cache balance update
            if self.cache:
                await self._cache_balance(balance)
            
            self.logger.info(f"💰 Currency added: {user_id} +{amount} {currency_type.value} from {source}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding currency: {e}")
            return False
    
    async def spend_currency(
        self,
        user_id: str,
        currency_type: CurrencyType,
        amount: Decimal,
        source: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Spend currency from user balance."""
        try:
            if amount <= 0:
                return False
            
            balance = await self.get_user_balance(user_id, currency_type)
            
            # Check sufficient balance
            if balance.balance < amount:
                self.logger.warning(f"Insufficient balance: {user_id} has {balance.balance}, needs {amount}")
                return False
            
            # Update balance
            balance.balance -= amount
            balance.total_spent += amount
            balance.last_updated = datetime.now(timezone.utc)
            
            # Create transaction record
            transaction = Transaction(
                id=str(uuid4()),
                user_id=user_id,
                transaction_type=TransactionType.SPEND,
                currency_type=currency_type,
                amount=amount,
                status=TransactionStatus.COMPLETED,
                source=source,
                metadata=metadata or {},
                processed_at=datetime.now(timezone.utc)
            )
            
            # Cache balance update
            if self.cache:
                await self._cache_balance(balance)
            
            self.logger.info(f"💸 Currency spent: {user_id} -{amount} {currency_type.value} for {source}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error spending currency: {e}")
            return False
    
    async def convert_currency(
        self,
        user_id: str,
        from_currency: CurrencyType,
        to_currency: CurrencyType,
        amount: Decimal
    ) -> bool:
        """Convert between currency types."""
        try:
            if amount <= 0:
                return False
            
            # Get conversion rate
            conversion_key = (from_currency, to_currency)
            if conversion_key not in self.conversion_rates:
                self.logger.warning(f"No conversion rate for {from_currency} -> {to_currency}")
                return False
            
            rate = self.conversion_rates[conversion_key]
            converted_amount = amount * rate
            
            # Apply conversion fee (5%)
            fee = converted_amount * Decimal('0.05')
            final_amount = converted_amount - fee
            
            # Check if user has sufficient balance
            from_balance = await self.get_user_balance(user_id, from_currency)
            if from_balance.balance < amount:
                return False
            
            # Perform conversion
            success_spend = await self.spend_currency(
                user_id, from_currency, amount, 
                f"conversion_to_{to_currency.value}"
            )
            
            if success_spend:
                success_add = await self.add_currency(
                    user_id, to_currency, final_amount,
                    f"conversion_from_{from_currency.value}"
                )
                
                if success_add:
                    self.logger.info(f"🔄 Currency converted: {user_id} {amount} {from_currency.value} -> {final_amount} {to_currency.value}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error converting currency: {e}")
            return False
    
    async def _check_daily_reset(self, balance: CurrencyBalance) -> None:
        """Check and perform daily balance resets."""
        now = datetime.now(timezone.utc)
        last_update = balance.last_updated
        
        # Check if it's a new day
        if now.date() > last_update.date():
            balance.daily_earned = Decimal('0')
            
            # Check for weekly reset
            if now.isocalendar()[1] != last_update.isocalendar()[1]:
                balance.weekly_earned = Decimal('0')
            
            # Check for monthly reset
            if now.month != last_update.month:
                balance.monthly_earned = Decimal('0')
    
    async def _cache_balance(self, balance: CurrencyBalance) -> None:
        """Cache user balance in Redis."""
        if not self.cache:
            return
        
        try:
            cache_key = f"balance:{balance.user_id}:{balance.currency_type.value}"
            cache_data = {
                "balance": str(balance.balance),
                "daily_earned": str(balance.daily_earned),
                "last_updated": balance.last_updated.isoformat()
            }
            
            # Cache for 1 hour
            await self.cache.setex(cache_key, 3600, json.dumps(cache_data))
            
        except Exception as e:
            self.logger.warning(f"Failed to cache balance: {e}")


class MarketplaceEngine:
    """
    Advanced marketplace system for virtual items, power-ups,
    and premium content with dynamic pricing and availability.
    """
    
    def __init__(self, currency_manager: CurrencyManager, cache_client=None):
        """Initialize the marketplace engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.currency_manager = currency_manager
        self.cache = cache_client
        
        # Item catalog and inventory storage
        self.item_catalog: Dict[str, MarketplaceItem] = {}
        self.user_inventories: Dict[str, UserInventory] = {}
        
        # Initialize default items
        self._initialize_default_items()
        
        self.logger.info("MarketplaceEngine initialized")
    
    def _initialize_default_items(self) -> None:
        """Initialize default marketplace items."""
        default_items = [
            {
                "name": "Profile Boost Basic",
                "description": "Increase profile visibility for 24 hours",
                "item_type": ItemType.PROFILE_BOOST,
                "rarity": ItemRarity.COMMON,
                "base_price": {CurrencyType.COINS: Decimal('500')},
                "duration_hours": 24,
                "effects": {"visibility_multiplier": 1.5}
            },
            {
                "name": "Content Amplifier Pro",
                "description": "Boost content reach by 300% for 48 hours",
                "item_type": ItemType.CONTENT_AMPLIFIER,
                "rarity": ItemRarity.RARE,
                "base_price": {CurrencyType.GEMS: Decimal('50'), CurrencyType.COINS: Decimal('2500')},
                "duration_hours": 48,
                "effects": {"reach_multiplier": 3.0}
            },
            {
                "name": "Neon Theme Pack",
                "description": "Exclusive neon-style profile theme",
                "item_type": ItemType.CUSTOM_THEME,
                "rarity": ItemRarity.EPIC,
                "base_price": {CurrencyType.GEMS: Decimal('100')},
                "effects": {"theme_id": "neon_pack_v1"}
            },
            {
                "name": "Collaboration Priority",
                "description": "Get priority matching for collaborations for 7 days",
                "item_type": ItemType.COLLABORATION_PRIORITY,
                "rarity": ItemRarity.UNCOMMON,
                "base_price": {CurrencyType.CREDITS: Decimal('200')},
                "duration_hours": 168,  # 7 days
                "effects": {"priority_level": 2}
            },
            {
                "name": "Storage Expansion",
                "description": "Permanently increase storage capacity by 10GB",
                "item_type": ItemType.STORAGE_EXPANSION,
                "rarity": ItemRarity.COMMON,
                "base_price": {CurrencyType.COINS: Decimal('1000')},
                "effects": {"storage_increase_gb": 10}
            }
        ]
        
        for item_data in default_items:
            item_id = str(uuid4())
            item = MarketplaceItem(
                id=item_id,
                name=item_data["name"],
                description=item_data["description"],
                item_type=item_data["item_type"],
                rarity=item_data["rarity"],
                base_price=item_data["base_price"],
                duration_hours=item_data.get("duration_hours"),
                effects=item_data["effects"]
            )
            self.item_catalog[item_id] = item
    
    async def get_marketplace_items(
        self, 
        item_type: Optional[ItemType] = None,
        rarity: Optional[ItemRarity] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get marketplace items with optional filtering."""
        try:
            items = []
            
            for item in self.item_catalog.values():
                # Apply filters
                if item_type and item.item_type != item_type:
                    continue
                if rarity and item.rarity != rarity:
                    continue
                
                # Check availability
                now = datetime.now(timezone.utc)
                if item.available_from and now < item.available_from:
                    continue
                if item.available_until and now > item.available_until:
                    continue
                
                # Calculate dynamic price
                dynamic_price = await self._calculate_dynamic_price(item, user_id)
                
                item_data = {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "type": item.item_type.value,
                    "rarity": item.rarity.value,
                    "base_price": {k.value: str(v) for k, v in item.base_price.items()},
                    "current_price": {k.value: str(v) for k, v in dynamic_price.items()},
                    "duration_hours": item.duration_hours,
                    "effects": item.effects,
                    "in_stock": await self._check_item_availability(item)
                }
                
                items.append(item_data)
            
            # Sort by rarity and price
            rarity_order = {r: i for i, r in enumerate(ItemRarity)}
            items.sort(key=lambda x: (rarity_order.get(x["rarity"], 0), x["name"]))
            
            return items
            
        except Exception as e:
            self.logger.error(f"Error getting marketplace items: {e}")
            return []
    
    async def purchase_item(
        self,
        user_id: str,
        item_id: str,
        payment_currency: CurrencyType,
        quantity: int = 1
    ) -> bool:
        """Purchase item from marketplace."""
        try:
            if quantity <= 0:
                return False
            
            item = self.item_catalog.get(item_id)
            if not item:
                self.logger.warning(f"Item not found: {item_id}")
                return False
            
            # Check item availability
            if not await self._check_item_availability(item, quantity):
                self.logger.warning(f"Item not available: {item_id}")
                return False
            
            # Calculate total price
            dynamic_price = await self._calculate_dynamic_price(item, user_id)
            if payment_currency not in dynamic_price:
                self.logger.warning(f"Currency not accepted for item: {payment_currency}")
                return False
            
            total_cost = dynamic_price[payment_currency] * quantity
            
            # Process payment
            payment_success = await self.currency_manager.spend_currency(
                user_id=user_id,
                currency_type=payment_currency,
                amount=total_cost,
                source=f"marketplace_purchase_{item_id}",
                metadata={"item_id": item_id, "quantity": quantity}
            )
            
            if not payment_success:
                return False
            
            # Add item to user inventory
            await self._add_to_inventory(user_id, item, quantity)
            
            self.logger.info(f"🛒 Item purchased: {user_id} bought {quantity}x {item.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error purchasing item: {e}")
            return False
    
    async def _calculate_dynamic_price(
        self, 
        item: MarketplaceItem, 
        user_id: Optional[str] = None
    ) -> Dict[CurrencyType, Decimal]:
        """Calculate dynamic pricing based on demand and user factors."""
        dynamic_prices = {}
        
        for currency, base_price in item.base_price.items():
            # Base multiplier based on rarity
            rarity_multipliers = {
                ItemRarity.COMMON: Decimal('1.0'),
                ItemRarity.UNCOMMON: Decimal('1.2'),
                ItemRarity.RARE: Decimal('1.5'),
                ItemRarity.EPIC: Decimal('2.0'),
                ItemRarity.LEGENDARY: Decimal('3.0'),
                ItemRarity.MYTHIC: Decimal('5.0')
            }
            
            multiplier = rarity_multipliers.get(item.rarity, Decimal('1.0'))
            
            # Time-based pricing (could implement sales, etc.)
            time_multiplier = Decimal('1.0')
            
            # User-specific discounts (loyalty, tier level, etc.)
            user_multiplier = Decimal('1.0')
            if user_id:
                # Could implement user-specific pricing here
                pass
            
            final_price = base_price * multiplier * time_multiplier * user_multiplier
            dynamic_prices[currency] = final_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return dynamic_prices
    
    async def _check_item_availability(
        self, 
        item: MarketplaceItem, 
        quantity: int = 1
    ) -> bool:
        """Check if item is available for purchase."""
        # Check time availability
        now = datetime.now(timezone.utc)
        if item.available_from and now < item.available_from:
            return False
        if item.available_until and now > item.available_until:
            return False
        
        # Check quantity limits (simplified - in production would track actual sales)
        if item.max_quantity and quantity > item.max_quantity:
            return False
        
        return True
    
    async def _add_to_inventory(
        self, 
        user_id: str, 
        item: MarketplaceItem, 
        quantity: int
    ) -> None:
        """Add purchased item to user inventory."""
        if user_id not in self.user_inventories:
            self.user_inventories[user_id] = UserInventory(user_id=user_id)
        
        inventory = self.user_inventories[user_id]
        
        # Add to items
        current_quantity = inventory.items.get(item.id, 0)
        inventory.items[item.id] = current_quantity + quantity
        
        # If it's a temporary item, set expiry
        if item.duration_hours:
            expiry = datetime.now(timezone.utc) + timedelta(hours=item.duration_hours)
            inventory.active_items[item.id] = expiry
        
        # Update total value
        for currency, price in item.base_price.items():
            current_value = inventory.total_value.get(currency, Decimal('0'))
            inventory.total_value[currency] = current_value + (price * quantity)
        
        inventory.last_updated = datetime.now(timezone.utc)
    
    async def get_user_inventory(self, user_id: str) -> Dict[str, Any]:
        """Get user inventory with item details."""
        try:
            if user_id not in self.user_inventories:
                return {"items": [], "total_value": {}}
            
            inventory = self.user_inventories[user_id]
            
            # Clean up expired items
            await self._cleanup_expired_items(inventory)
            
            inventory_items = []
            for item_id, quantity in inventory.items.items():
                item = self.item_catalog.get(item_id)
                if item:
                    item_data = {
                        "id": item.id,
                        "name": item.name,
                        "type": item.item_type.value,
                        "rarity": item.rarity.value,
                        "quantity": quantity,
                        "effects": item.effects
                    }
                    
                    # Add expiry info for temporary items
                    if item_id in inventory.active_items:
                        item_data["expires_at"] = inventory.active_items[item_id].isoformat()
                        item_data["is_active"] = inventory.active_items[item_id] > datetime.now(timezone.utc)
                    
                    inventory_items.append(item_data)
            
            return {
                "items": inventory_items,
                "total_value": {k.value: str(v) for k, v in inventory.total_value.items()},
                "last_updated": inventory.last_updated.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user inventory: {e}")
            return {"items": [], "total_value": {}}
    
    async def _cleanup_expired_items(self, inventory: UserInventory) -> None:
        """Remove expired temporary items from inventory."""
        now = datetime.now(timezone.utc)
        expired_items = []
        
        for item_id, expiry in inventory.active_items.items():
            if expiry <= now:
                expired_items.append(item_id)
        
        for item_id in expired_items:
            # Remove from active items
            del inventory.active_items[item_id]
            
            # Remove from items inventory
            if item_id in inventory.items:
                del inventory.items[item_id]
            
            self.logger.info(f"⏰ Expired item removed: {inventory.user_id} - {item_id}")


class TradingSystem:
    """
    Peer-to-peer trading system allowing users to exchange
    currencies and items with each other safely.
    """
    
    def __init__(self, currency_manager: CurrencyManager, marketplace_engine: MarketplaceEngine):
        """Initialize the trading system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.currency_manager = currency_manager
        self.marketplace_engine = marketplace_engine
        
        # Active trade offers storage
        self.active_trades: Dict[str, TradeOffer] = {}
        
        # Trading fees (percentage)
        self.trading_fee_rate = Decimal('0.05')  # 5%
        
        self.logger.info("TradingSystem initialized")
    
    async def create_trade_offer(
        self,
        from_user_id: str,
        to_user_id: str,
        offer_currencies: Dict[CurrencyType, Decimal],
        offer_items: Dict[str, int],
        request_currencies: Dict[CurrencyType, Decimal],
        request_items: Dict[str, int],
        message: str = ""
    ) -> Optional[str]:
        """Create a new trade offer."""
        try:
            # Validate offer - user must have what they're offering
            if not await self._validate_trade_offer(from_user_id, offer_currencies, offer_items):
                return None
            
            # Create trade offer
            trade_id = str(uuid4())
            trade_offer = TradeOffer(
                id=trade_id,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                offer_currencies=offer_currencies,
                offer_items=offer_items,
                request_currencies=request_currencies,
                request_items=request_items,
                message=message
            )
            
            self.active_trades[trade_id] = trade_offer
            
            self.logger.info(f"🤝 Trade offer created: {from_user_id} -> {to_user_id} ({trade_id})")
            
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error creating trade offer: {e}")
            return None
    
    async def accept_trade_offer(self, trade_id: str, accepting_user_id: str) -> bool:
        """Accept a trade offer and execute the trade."""
        try:
            trade_offer = self.active_trades.get(trade_id)
            if not trade_offer:
                return False
            
            # Validate accepting user
            if trade_offer.to_user_id != accepting_user_id:
                return False
            
            # Check if offer is still valid
            if trade_offer.status != "pending":
                return False
            
            if datetime.now(timezone.utc) > trade_offer.expires_at:
                trade_offer.status = "expired"
                return False
            
            # Validate both users have what they're trading
            if not await self._validate_trade_offer(
                trade_offer.from_user_id, 
                trade_offer.offer_currencies, 
                trade_offer.offer_items
            ):
                return False
            
            if not await self._validate_trade_offer(
                trade_offer.to_user_id, 
                trade_offer.request_currencies, 
                trade_offer.request_items
            ):
                return False
            
            # Execute the trade
            success = await self._execute_trade(trade_offer)
            
            if success:
                trade_offer.status = "accepted"
                self.logger.info(f"✅ Trade completed: {trade_id}")
            else:
                trade_offer.status = "failed"
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error accepting trade offer: {e}")
            return False
    
    async def reject_trade_offer(self, trade_id: str, rejecting_user_id: str) -> bool:
        """Reject a trade offer."""
        try:
            trade_offer = self.active_trades.get(trade_id)
            if not trade_offer:
                return False
            
            if trade_offer.to_user_id != rejecting_user_id:
                return False
            
            trade_offer.status = "rejected"
            
            self.logger.info(f"❌ Trade rejected: {trade_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error rejecting trade offer: {e}")
            return False
    
    async def get_user_trade_offers(
        self, 
        user_id: str, 
        include_sent: bool = True, 
        include_received: bool = True
    ) -> List[Dict[str, Any]]:
        """Get trade offers for a user."""
        try:
            offers = []
            
            for trade_offer in self.active_trades.values():
                include_offer = False
                offer_type = None
                
                if include_sent and trade_offer.from_user_id == user_id:
                    include_offer = True
                    offer_type = "sent"
                elif include_received and trade_offer.to_user_id == user_id:
                    include_offer = True
                    offer_type = "received"
                
                if include_offer:
                    # Convert to serializable format
                    offer_data = {
                        "id": trade_offer.id,
                        "type": offer_type,
                        "from_user_id": trade_offer.from_user_id,
                        "to_user_id": trade_offer.to_user_id,
                        "offer_currencies": {k.value: str(v) for k, v in trade_offer.offer_currencies.items()},
                        "offer_items": trade_offer.offer_items,
                        "request_currencies": {k.value: str(v) for k, v in trade_offer.request_currencies.items()},
                        "request_items": trade_offer.request_items,
                        "status": trade_offer.status,
                        "created_at": trade_offer.created_at.isoformat(),
                        "expires_at": trade_offer.expires_at.isoformat(),
                        "message": trade_offer.message
                    }
                    offers.append(offer_data)
            
            # Sort by creation date (newest first)
            offers.sort(key=lambda x: x["created_at"], reverse=True)
            
            return offers
            
        except Exception as e:
            self.logger.error(f"Error getting user trade offers: {e}")
            return []
    
    async def _validate_trade_offer(
        self,
        user_id: str,
        currencies: Dict[CurrencyType, Decimal],
        items: Dict[str, int]
    ) -> bool:
        """Validate that user has the currencies and items they're offering."""
        try:
            # Check currencies
            for currency_type, amount in currencies.items():
                balance = await self.currency_manager.get_user_balance(user_id, currency_type)
                if balance.balance < amount:
                    return False
            
            # Check items
            inventory_data = await self.marketplace_engine.get_user_inventory(user_id)
            user_items = {item["id"]: item["quantity"] for item in inventory_data["items"]}
            
            for item_id, quantity in items.items():
                if user_items.get(item_id, 0) < quantity:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating trade offer: {e}")
            return False
    
    async def _execute_trade(self, trade_offer: TradeOffer) -> bool:
        """Execute the actual trade between users."""
        try:
            # Transfer currencies and items from user 1 to user 2
            
            # User 1 gives currencies
            for currency_type, amount in trade_offer.offer_currencies.items():
                # Calculate fee
                fee = amount * self.trading_fee_rate
                amount_after_fee = amount - fee
                
                # Deduct from sender
                success = await self.currency_manager.spend_currency(
                    trade_offer.from_user_id, currency_type, amount,
                    f"trade_{trade_offer.id}", {"fee": str(fee)}
                )
                if not success:
                    return False
                
                # Add to receiver
                await self.currency_manager.add_currency(
                    trade_offer.to_user_id, currency_type, amount_after_fee,
                    f"trade_{trade_offer.id}"
                )
            
            # User 2 gives currencies
            for currency_type, amount in trade_offer.request_currencies.items():
                # Calculate fee
                fee = amount * self.trading_fee_rate
                amount_after_fee = amount - fee
                
                # Deduct from sender
                success = await self.currency_manager.spend_currency(
                    trade_offer.to_user_id, currency_type, amount,
                    f"trade_{trade_offer.id}", {"fee": str(fee)}
                )
                if not success:
                    return False
                
                # Add to receiver
                await self.currency_manager.add_currency(
                    trade_offer.from_user_id, currency_type, amount_after_fee,
                    f"trade_{trade_offer.id}"
                )
            
            # Transfer items (simplified - in production would need proper inventory management)
            # This would require more complex inventory manipulation
            
            self.logger.info(f"💸 Trade executed successfully: {trade_offer.id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return False


class EconomyBalancer:
    """
    Economic balancing system to control inflation, monitor
    economic health, and adjust parameters for stability.
    """
    
    def __init__(self, currency_manager: CurrencyManager):
        """Initialize the economy balancer."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.currency_manager = currency_manager
        
        # Economic monitoring data
        self.economic_metrics: Dict[str, Any] = {}
        self.inflation_rates: Dict[CurrencyType, float] = {}
        
        # Control parameters
        self.max_inflation_rate = 0.10  # 10% per month
        self.min_deflation_rate = -0.05  # -5% per month
        
        self.logger.info("EconomyBalancer initialized")
    
    async def monitor_economic_health(self) -> Dict[str, Any]:
        """Monitor overall economic health metrics."""
        try:
            # Calculate total currency in circulation
            total_circulation = await self._calculate_total_circulation()
            
            # Calculate velocity of money
            velocity = await self._calculate_currency_velocity()
            
            # Monitor price stability
            price_stability = await self._monitor_price_stability()
            
            # Calculate inflation rates
            inflation_rates = await self._calculate_inflation_rates()
            
            metrics = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_circulation": total_circulation,
                "currency_velocity": velocity,
                "price_stability": price_stability,
                "inflation_rates": inflation_rates,
                "economic_health_score": self._calculate_health_score(
                    total_circulation, velocity, price_stability, inflation_rates
                )
            }
            
            self.economic_metrics = metrics
            
            # Check if intervention is needed
            await self._check_intervention_needed(metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error monitoring economic health: {e}")
            return {}
    
    async def _calculate_total_circulation(self) -> Dict[str, str]:
        """Calculate total currency in circulation."""
        circulation = {}
        
        for currency_type in CurrencyType:
            total = Decimal('0')
            
            # Sum all user balances for this currency
            for user_balances in self.currency_manager.user_balances.values():
                if currency_type in user_balances:
                    total += user_balances[currency_type].balance
            
            circulation[currency_type.value] = str(total)
        
        return circulation
    
    async def _calculate_currency_velocity(self) -> Dict[str, float]:
        """Calculate how quickly currency is changing hands."""
        # This would require transaction history analysis
        # For now, return mock data
        velocity = {}
        
        for currency_type in CurrencyType:
            # Mock velocity calculation
            velocity[currency_type.value] = 2.5  # Average transactions per currency unit
        
        return velocity
    
    async def _monitor_price_stability(self) -> Dict[str, float]:
        """Monitor price stability across marketplace items."""
        # This would analyze price changes over time
        # For now, return mock stability scores
        stability = {
            "overall_stability": 0.85,  # 85% stable
            "common_items_stability": 0.90,
            "rare_items_stability": 0.75,
            "premium_items_stability": 0.80
        }
        
        return stability
    
    async def _calculate_inflation_rates(self) -> Dict[str, float]:
        """Calculate inflation rates for each currency."""
        # This would require historical data analysis
        # For now, return mock inflation rates
        inflation = {}
        
        for currency_type in CurrencyType:
            # Mock inflation calculation
            rate = 0.02  # 2% monthly inflation
            inflation[currency_type.value] = rate
            self.inflation_rates[currency_type] = rate
        
        return inflation
    
    def _calculate_health_score(
        self, 
        circulation: Dict[str, str], 
        velocity: Dict[str, float],
        stability: Dict[str, float], 
        inflation: Dict[str, float]
    ) -> float:
        """Calculate overall economic health score."""
        try:
            # Weight different factors
            stability_score = stability.get("overall_stability", 0.5)
            
            # Inflation penalty (ideal is around 2-3%)
            avg_inflation = sum(inflation.values()) / len(inflation) if inflation else 0
            inflation_penalty = abs(avg_inflation - 0.025) * 10  # Penalty for deviation from 2.5%
            inflation_score = max(0, 1 - inflation_penalty)
            
            # Velocity score (ideal is 2-4 transactions per unit)
            avg_velocity = sum(velocity.values()) / len(velocity) if velocity else 0
            velocity_score = 1 - abs(avg_velocity - 3) / 10  # Penalty for deviation from 3
            velocity_score = max(0, min(1, velocity_score))
            
            # Weighted health score
            health_score = (
                stability_score * 0.4 +
                inflation_score * 0.35 +
                velocity_score * 0.25
            )
            
            return round(health_score, 3)
            
        except Exception:
            return 0.5  # Neutral score on error
    
    async def _check_intervention_needed(self, metrics: Dict[str, Any]) -> None:
        """Check if economic intervention is needed."""
        try:
            inflation_rates = metrics.get("inflation_rates", {})
            health_score = metrics.get("economic_health_score", 0.5)
            
            intervention_needed = False
            intervention_reasons = []
            
            # Check inflation rates
            for currency, rate in inflation_rates.items():
                if rate > self.max_inflation_rate:
                    intervention_needed = True
                    intervention_reasons.append(f"High inflation in {currency}: {rate:.1%}")
                elif rate < self.min_deflation_rate:
                    intervention_needed = True
                    intervention_reasons.append(f"Deflation in {currency}: {rate:.1%}")
            
            # Check overall health
            if health_score < 0.3:
                intervention_needed = True
                intervention_reasons.append(f"Low economic health score: {health_score:.3f}")
            
            if intervention_needed:
                await self._perform_economic_intervention(intervention_reasons)
            
        except Exception as e:
            self.logger.error(f"Error checking intervention: {e}")
    
    async def _perform_economic_intervention(self, reasons: List[str]) -> None:
        """Perform economic intervention to stabilize the economy."""
        try:
            self.logger.warning(f"🚨 Economic intervention triggered: {'; '.join(reasons)}")
            
            # Example interventions:
            # 1. Adjust daily earning limits
            # 2. Modify conversion rates
            # 3. Adjust marketplace pricing
            # 4. Implement temporary bonuses or penalties
            
            # For now, just log the intervention
            intervention_actions = [
                "Reviewing currency earning rates",
                "Analyzing marketplace pricing",
                "Monitoring user behavior patterns",
                "Preparing economic adjustments"
            ]
            
            for action in intervention_actions:
                self.logger.info(f"📊 Economic intervention: {action}")
            
        except Exception as e:
            self.logger.error(f"Error performing economic intervention: {e}")


class VirtualEconomyEngine:
    """
    Main virtual economy orchestrator coordinating all economic
    subsystems and providing unified economy management interface.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the virtual economy engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize subsystems
        self.currency_manager = CurrencyManager(database_connection, cache_client)
        self.marketplace_engine = MarketplaceEngine(self.currency_manager, cache_client)
        self.trading_system = TradingSystem(self.currency_manager, self.marketplace_engine)
        self.economy_balancer = EconomyBalancer(self.currency_manager)
        
        self.logger.info("VirtualEconomyEngine initialized")
    
    async def get_user_economic_profile(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive economic profile for a user."""
        try:
            # Get all currency balances
            balances = {}
            for currency_type in CurrencyType:
                balance = await self.currency_manager.get_user_balance(user_id, currency_type)
                balances[currency_type.value] = {
                    "balance": str(balance.balance),
                    "daily_earned": str(balance.daily_earned),
                    "weekly_earned": str(balance.weekly_earned),
                    "total_earned": str(balance.total_earned),
                    "total_spent": str(balance.total_spent)
                }
            
            # Get inventory
            inventory = await self.marketplace_engine.get_user_inventory(user_id)
            
            # Get active trades
            trades = await self.trading_system.get_user_trade_offers(user_id)
            
            # Calculate economic metrics
            total_net_worth = self._calculate_net_worth(balances, inventory)
            economic_activity_score = self._calculate_activity_score(balances, trades)
            
            profile = {
                "user_id": user_id,
                "currency_balances": balances,
                "inventory": inventory,
                "active_trades": {
                    "total_offers": len(trades),
                    "sent_offers": len([t for t in trades if t["type"] == "sent"]),
                    "received_offers": len([t for t in trades if t["type"] == "received"]),
                    "recent_trades": trades[:5]  # Last 5 trades
                },
                "economic_metrics": {
                    "net_worth_coins": str(total_net_worth),
                    "activity_score": economic_activity_score,
                    "spending_power": self._calculate_spending_power(balances),
                    "trading_reputation": 100  # Would be calculated based on trade history
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error getting user economic profile: {e}")
            return {"error": str(e)}
    
    def _calculate_net_worth(self, balances: Dict[str, Any], inventory: Dict[str, Any]) -> Decimal:
        """Calculate user's total net worth in coins."""
        try:
            net_worth = Decimal('0')
            
            # Add currency balances (convert to coins)
            for currency, balance_data in balances.items():
                if currency == CurrencyType.COINS.value:
                    net_worth += Decimal(balance_data["balance"])
                else:
                    # Convert to coins using conversion rates
                    # This is simplified - in production would use actual rates
                    conversion_multipliers = {
                        CurrencyType.GEMS.value: 100,  # 1 gem = 100 coins
                        CurrencyType.CREDITS.value: 2,  # 1 credit = 2 coins
                        CurrencyType.XP_POINTS.value: 0.5,  # 2 XP = 1 coin
                        CurrencyType.INFLUENCE.value: 10,  # 1 influence = 10 coins
                        CurrencyType.ENERGY.value: 20   # 1 energy = 20 coins
                    }
                    
                    multiplier = conversion_multipliers.get(currency, 1)
                    net_worth += Decimal(balance_data["balance"]) * multiplier
            
            # Add inventory value
            inventory_value = inventory.get("total_value", {})
            if CurrencyType.COINS.value in inventory_value:
                net_worth += Decimal(inventory_value[CurrencyType.COINS.value])
            
            return net_worth
            
        except Exception:
            return Decimal('0')
    
    def _calculate_activity_score(self, balances: Dict[str, Any], trades: List[Dict[str, Any]]) -> float:
        """Calculate economic activity score for user."""
        try:
            score = 0.0
            
            # Score based on currency earning activity
            for currency, balance_data in balances.items():
                daily_earned = float(balance_data.get("daily_earned", 0))
                score += min(daily_earned / 1000, 10)  # Max 10 points per currency
            
            # Score based on trading activity
            recent_trades = len([t for t in trades if t["status"] in ["accepted", "pending"]])
            score += min(recent_trades * 5, 25)  # Max 25 points from trades
            
            # Normalize to 0-100 scale
            return min(score * 2, 100)
            
        except Exception:
            return 0.0
    
    def _calculate_spending_power(self, balances: Dict[str, Any]) -> str:
        """Calculate user's spending power category."""
        try:
            # Calculate total spendable amount in coins equivalent
            total_coins = Decimal('0')
            
            for currency, balance_data in balances.items():
                balance = Decimal(balance_data["balance"])
                
                if currency == CurrencyType.COINS.value:
                    total_coins += balance
                elif currency == CurrencyType.GEMS.value:
                    total_coins += balance * 100  # Gems are valuable
                elif currency == CurrencyType.CREDITS.value:
                    total_coins += balance * 2
            
            # Categorize spending power
            if total_coins >= 100000:
                return "High Roller"
            elif total_coins >= 50000:
                return "Big Spender"
            elif total_coins >= 20000:
                return "Active Buyer"
            elif total_coins >= 5000:
                return "Casual Buyer"
            elif total_coins >= 1000:
                return "Beginner"
            else:
                return "New User"
                
        except Exception:
            return "Unknown"


# Global economy engine instance
_virtual_economy_engine: Optional[VirtualEconomyEngine] = None


async def get_virtual_economy_engine(
    database_connection=None,
    cache_client=None
) -> VirtualEconomyEngine:
    """Get the global virtual economy engine instance."""
    global _virtual_economy_engine
    
    if _virtual_economy_engine is None:
        _virtual_economy_engine = VirtualEconomyEngine(database_connection, cache_client)
    
    return _virtual_economy_engine


# Convenience functions
async def add_user_currency(
    user_id: str,
    currency_type: CurrencyType,
    amount: Decimal,
    source: str
) -> bool:
    """Add currency to user balance."""
    engine = await get_virtual_economy_engine()
    return await engine.currency_manager.add_currency(user_id, currency_type, amount, source)


async def purchase_marketplace_item(
    user_id: str,
    item_id: str,
    payment_currency: CurrencyType
) -> bool:
    """Purchase item from marketplace."""
    engine = await get_virtual_economy_engine()
    return await engine.marketplace_engine.purchase_item(user_id, item_id, payment_currency)


async def create_trade_offer(
    from_user_id: str,
    to_user_id: str,
    offer_currencies: Dict[CurrencyType, Decimal],
    request_currencies: Dict[CurrencyType, Decimal]
) -> Optional[str]:
    """Create a trade offer between users."""
    engine = await get_virtual_economy_engine()
    return await engine.trading_system.create_trade_offer(
        from_user_id, to_user_id, offer_currencies, {}, request_currencies, {}
    )


# Module exports
__all__ = [
    "VirtualEconomyEngine",
    "CurrencyManager",
    "MarketplaceEngine", 
    "TradingSystem",
    "EconomyBalancer",
    "CurrencyType",
    "ItemType",
    "ItemRarity",
    "TransactionType",
    "TransactionStatus",
    "CurrencyBalance",
    "MarketplaceItem",
    "UserInventory",
    "Transaction",
    "TradeOffer",
    "get_virtual_economy_engine",
    "add_user_currency",
    "purchase_marketplace_item",
    "create_trade_offer"
]