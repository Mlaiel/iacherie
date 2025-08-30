"""
Enterprise Virtual Economy - Virtual currency and economic system for IA Influencer platform.

This module provides a comprehensive virtual economy management system that handles
virtual currency transactions, economic balance, marketplace operations, and
financial gameplay mechanics for multi-format content creators.

Architecture: Enterprise Production-Ready (Backend Level 2)
Module: backend/business/engagement/virtual_economy.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

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
Virtual Economy → Distribution → Monetization → Analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import uuid4, UUID
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class CurrencyType(str, Enum):
    """Types of virtual currencies."""
    CREDITS = "credits"            # Main platform currency
    GEMS = "gems"                  # Premium currency
    TOKENS = "tokens"              # Special event currency
    INFLUENCE_POINTS = "influence_points"  # Influence-based currency
    COLLABORATION_COINS = "collaboration_coins"  # Collaboration rewards
    QUALITY_CRYSTALS = "quality_crystals"  # Quality-based rewards


class TransactionType(str, Enum):
    """Types of virtual economy transactions."""
    EARN = "earn"
    SPEND = "spend"
    TRANSFER = "transfer"
    PURCHASE = "purchase"
    SELL = "sell"
    EXCHANGE = "exchange"
    BONUS = "bonus"
    PENALTY = "penalty"
    REFUND = "refund"
    GIFT = "gift"


class TransactionSource(str, Enum):
    """Sources of virtual economy transactions."""
    CONTENT_UPLOAD = "content_upload"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    CHALLENGE_COMPLETION = "challenge_completion"
    DAILY_LOGIN = "daily_login"
    STREAK_BONUS = "streak_bonus"
    COLLABORATION_REWARD = "collaboration_reward"
    QUALITY_BONUS = "quality_bonus"
    ENGAGEMENT_BONUS = "engagement_bonus"
    MARKETPLACE_PURCHASE = "marketplace_purchase"
    MARKETPLACE_SALE = "marketplace_sale"
    PREMIUM_FEATURE = "premium_feature"
    BOOST_PURCHASE = "boost_purchase"
    SUBSCRIPTION_BENEFIT = "subscription_benefit"
    REFERRAL_BONUS = "referral_bonus"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    PROMOTIONAL_GIFT = "promotional_gift"
    SEASONAL_EVENT = "seasonal_event"


class MarketplaceItemType(str, Enum):
    """Types of items in the virtual marketplace."""
    CONTENT_BOOST = "content_boost"
    PROFILE_CUSTOMIZATION = "profile_customization"
    SPECIAL_BADGE = "special_badge"
    PREMIUM_ANALYTICS = "premium_analytics"
    COLLABORATION_TOOLS = "collaboration_tools"
    EXCLUSIVE_FEATURES = "exclusive_features"
    VIRTUAL_GIFTS = "virtual_gifts"
    PLATFORM_CREDITS = "platform_credits"
    TIME_MULTIPLIERS = "time_multipliers"
    SKILL_BOOSTERS = "skill_boosters"


@dataclass
class VirtualWallet:
    """Represents a user's virtual wallet."""
    wallet_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    
    # Currency balances
    balances: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    
    # Spending limits and controls
    daily_spending_limit: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    total_earned: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    total_spent: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_transaction: Optional[datetime] = None
    
    # Security
    locked: bool = False
    lock_reason: Optional[str] = None
    
    def get_balance(self, currency: CurrencyType) -> Decimal:
        """Get balance for a specific currency."""
        return self.balances.get(currency, Decimal('0'))
    
    def has_sufficient_balance(self, currency: CurrencyType, amount: Decimal) -> bool:
        """Check if wallet has sufficient balance."""
        return self.get_balance(currency) >= amount
    
    def get_net_worth(self, exchange_rates: Dict[CurrencyType, Decimal]) -> Decimal:
        """Calculate total wallet value in credits equivalent."""
        total_value = Decimal('0')
        
        for currency, balance in self.balances.items():
            rate = exchange_rates.get(currency, Decimal('1'))
            total_value += balance * rate
        
        return total_value


@dataclass
class VirtualTransaction:
    """Represents a virtual economy transaction."""
    transaction_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    
    # Transaction details
    transaction_type: TransactionType = TransactionType.EARN
    source: TransactionSource = TransactionSource.CONTENT_UPLOAD
    currency: CurrencyType = CurrencyType.CREDITS
    amount: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Related entities
    related_user_id: Optional[str] = None  # For transfers/gifts
    related_item_id: Optional[str] = None  # For marketplace purchases
    related_challenge_id: Optional[str] = None  # For challenge rewards
    
    # Metadata
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False
    processed_at: Optional[datetime] = None
    
    # Balances (for audit trail)
    balance_before: Decimal = field(default_factory=lambda: Decimal('0'))
    balance_after: Decimal = field(default_factory=lambda: Decimal('0'))
    
    # Validation
    validated: bool = False
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class MarketplaceItem:
    """Represents an item in the virtual marketplace."""
    item_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    detailed_description: str = ""
    
    # Classification
    item_type: MarketplaceItemType = MarketplaceItemType.CONTENT_BOOST
    category: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Pricing
    price: Decimal = field(default_factory=lambda: Decimal('0'))
    currency: CurrencyType = CurrencyType.CREDITS
    alternative_currencies: Dict[CurrencyType, Decimal] = field(default_factory=dict)
    
    # Availability
    available: bool = True
    stock_quantity: Optional[int] = None  # None = unlimited
    max_per_user: Optional[int] = None
    
    # Timing
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    
    # Effects and benefits
    effects: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[timedelta] = None  # For temporary items
    
    # Requirements
    level_requirement: Optional[int] = None
    achievement_requirements: List[str] = field(default_factory=list)
    creator_type_requirements: List[str] = field(default_factory=list)
    
    # Metadata
    icon_url: str = ""
    preview_images: List[str] = field(default_factory=list)
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    
    # Statistics
    total_purchases: int = 0
    total_revenue: Decimal = field(default_factory=lambda: Decimal('0'))
    popularity_score: float = 0.0
    
    # Administrative
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    
    def is_available(self) -> bool:
        """Check if item is currently available for purchase."""
        if not self.available:
            return False
        
        now = datetime.utcnow()
        
        if self.available_from and now < self.available_from:
            return False
        
        if self.available_until and now > self.available_until:
            return False
        
        if self.stock_quantity is not None and self.stock_quantity <= 0:
            return False
        
        return True
    
    def can_user_purchase(self, user_profile: Dict[str, Any], user_purchases: int) -> Tuple[bool, List[str]]:
        """Check if a user can purchase this item."""
        reasons = []
        
        # Check level requirement
        if self.level_requirement:
            user_level = user_profile.get("level", 1)
            if user_level < self.level_requirement:
                reasons.append(f"Requires level {self.level_requirement}")
        
        # Check achievement requirements
        user_achievements = set(user_profile.get("achievements", []))
        required_achievements = set(self.achievement_requirements)
        missing_achievements = required_achievements - user_achievements
        
        if missing_achievements:
            reasons.append(f"Missing achievements: {', '.join(missing_achievements)}")
        
        # Check creator type requirements
        if self.creator_type_requirements:
            user_creator_type = user_profile.get("creator_type", "")
            if user_creator_type not in self.creator_type_requirements:
                reasons.append(f"Only available for: {', '.join(self.creator_type_requirements)}")
        
        # Check purchase limit
        if self.max_per_user and user_purchases >= self.max_per_user:
            reasons.append(f"Maximum {self.max_per_user} per user")
        
        return len(reasons) == 0, reasons


class VirtualEconomy:
    """
    Enterprise-grade virtual economy management system.
    
    Manages virtual currencies, transactions, marketplace operations,
    and economic balance across the platform.
    """
    
    def __init__(self):
        """Initialize the virtual economy system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._wallets: Dict[str, VirtualWallet] = {}
        self._transactions: List[VirtualTransaction] = []
        self._marketplace_items: Dict[str, MarketplaceItem] = {}
        self._user_purchases: Dict[str, List[str]] = {}  # user_id -> item_ids
        self._exchange_rates: Dict[CurrencyType, Decimal] = {}
        self._transaction_lock = asyncio.Lock()
        
        # Initialize exchange rates
        self._initialize_exchange_rates()
        
        # Initialize marketplace
        self._initialize_marketplace()
        
        self.logger.info("VirtualEconomy initialized successfully")
    
    def _initialize_exchange_rates(self) -> None:
        """Initialize currency exchange rates (relative to credits)."""
        self._exchange_rates = {
            CurrencyType.CREDITS: Decimal('1.0'),
            CurrencyType.GEMS: Decimal('10.0'),  # 1 gem = 10 credits
            CurrencyType.TOKENS: Decimal('5.0'),  # 1 token = 5 credits
            CurrencyType.INFLUENCE_POINTS: Decimal('0.1'),  # 10 influence points = 1 credit
            CurrencyType.COLLABORATION_COINS: Decimal('2.0'),  # 1 collab coin = 2 credits
            CurrencyType.QUALITY_CRYSTALS: Decimal('25.0')  # 1 quality crystal = 25 credits
        }
    
    def _initialize_marketplace(self) -> None:
        """Initialize marketplace with default items."""
        
        # Content Boosts
        content_boost_small = MarketplaceItem(
            name="Content Boost (Small)",
            description="Boost your content visibility for 24 hours",
            detailed_description="Increase your content's reach and visibility by 25% for 24 hours.",
            item_type=MarketplaceItemType.CONTENT_BOOST,
            category="boosts",
            price=Decimal('100'),
            currency=CurrencyType.CREDITS,
            duration=timedelta(hours=24),
            effects={"visibility_boost": 0.25, "engagement_boost": 0.15},
            tags=["boost", "visibility", "engagement"],
            rarity="common"
        )
        self._marketplace_items[content_boost_small.item_id] = content_boost_small
        
        content_boost_large = MarketplaceItem(
            name="Content Boost (Large)",
            description="Massive content boost for 72 hours",
            detailed_description="Increase your content's reach and visibility by 50% for 72 hours.",
            item_type=MarketplaceItemType.CONTENT_BOOST,
            category="boosts",
            price=Decimal('500'),
            currency=CurrencyType.CREDITS,
            alternative_currencies={CurrencyType.GEMS: Decimal('50')},
            duration=timedelta(hours=72),
            effects={"visibility_boost": 0.50, "engagement_boost": 0.30},
            tags=["boost", "visibility", "engagement", "premium"],
            rarity="uncommon"
        )
        self._marketplace_items[content_boost_large.item_id] = content_boost_large
        
        # Profile Customizations
        custom_badge = MarketplaceItem(
            name="Custom Profile Badge",
            description="Create a personalized badge for your profile",
            detailed_description="Design and display a unique badge that represents your brand and achievements.",
            item_type=MarketplaceItemType.PROFILE_CUSTOMIZATION,
            category="customization",
            price=Decimal('750'),
            currency=CurrencyType.CREDITS,
            alternative_currencies={CurrencyType.GEMS: Decimal('75')},
            effects={"custom_badge": True, "profile_distinction": True},
            tags=["badge", "customization", "profile"],
            rarity="rare",
            max_per_user=3
        )
        self._marketplace_items[custom_badge.item_id] = custom_badge
        
        # Premium Analytics
        premium_analytics = MarketplaceItem(
            name="Premium Analytics (30 days)",
            description="Advanced analytics and insights for 30 days",
            detailed_description="Get detailed performance metrics, audience insights, and optimization recommendations.",
            item_type=MarketplaceItemType.PREMIUM_ANALYTICS,
            category="tools",
            price=Decimal('1200'),
            currency=CurrencyType.CREDITS,
            alternative_currencies={CurrencyType.GEMS: Decimal('120')},
            duration=timedelta(days=30),
            effects={"advanced_analytics": True, "detailed_reports": True, "optimization_tips": True},
            tags=["analytics", "insights", "premium"],
            rarity="uncommon",
            level_requirement=10
        )
        self._marketplace_items[premium_analytics.item_id] = premium_analytics
        
        # Collaboration Tools
        collab_tools = MarketplaceItem(
            name="Collaboration Toolkit",
            description="Enhanced tools for creator collaboration",
            detailed_description="Access advanced collaboration features including project management and communication tools.",
            item_type=MarketplaceItemType.COLLABORATION_TOOLS,
            category="tools",
            price=Decimal('2000'),
            currency=CurrencyType.COLLABORATION_COINS,
            alternative_currencies={CurrencyType.CREDITS: Decimal('4000')},
            duration=timedelta(days=90),
            effects={"advanced_collab_tools": True, "project_management": True, "priority_matching": True},
            tags=["collaboration", "tools", "networking"],
            rarity="epic",
            level_requirement=25
        )
        self._marketplace_items[collab_tools.item_id] = collab_tools
        
        # Special Multipliers
        xp_multiplier = MarketplaceItem(
            name="Experience Multiplier (2x)",
            description="Double your experience point gains for 7 days",
            detailed_description="Earn twice as many experience points from all activities for one week.",
            item_type=MarketplaceItemType.TIME_MULTIPLIERS,
            category="multipliers",
            price=Decimal('150'),
            currency=CurrencyType.GEMS,
            duration=timedelta(days=7),
            effects={"xp_multiplier": 2.0},
            tags=["multiplier", "experience", "growth"],
            rarity="rare",
            max_per_user=2  # Can only have 2 active at once
        )
        self._marketplace_items[xp_multiplier.item_id] = xp_multiplier
        
        # Virtual Gifts
        virtual_flower = MarketplaceItem(
            name="Virtual Flower Bouquet",
            description="Send appreciation to another creator",
            detailed_description="Show your appreciation for another creator's work with a beautiful virtual flower bouquet.",
            item_type=MarketplaceItemType.VIRTUAL_GIFTS,
            category="gifts",
            price=Decimal('50'),
            currency=CurrencyType.CREDITS,
            effects={"gift_value": 25, "appreciation_points": 10},
            tags=["gift", "appreciation", "social"],
            rarity="common"
        )
        self._marketplace_items[virtual_flower.item_id] = virtual_flower
        
        # Platform Credits
        platform_credits = MarketplaceItem(
            name="Platform Advertising Credits",
            description="Credits for promoting your content",
            detailed_description="Use these credits to promote your content across the platform's advertising network.",
            item_type=MarketplaceItemType.PLATFORM_CREDITS,
            category="promotion",
            price=Decimal('500'),
            currency=CurrencyType.CREDITS,
            effects={"ad_credits": 500, "promotion_reach": 10000},
            tags=["advertising", "promotion", "reach"],
            rarity="common"
        )
        self._marketplace_items[platform_credits.item_id] = platform_credits
    
    async def get_user_wallet(self, user_id: str) -> VirtualWallet:
        """Get or create a user's virtual wallet."""
        if user_id not in self._wallets:
            wallet = VirtualWallet(user_id=user_id)
            
            # Initialize with starting balances
            wallet.balances = {
                CurrencyType.CREDITS: Decimal('100'),  # Starting credits
                CurrencyType.GEMS: Decimal('0'),
                CurrencyType.TOKENS: Decimal('0'),
                CurrencyType.INFLUENCE_POINTS: Decimal('0'),
                CurrencyType.COLLABORATION_COINS: Decimal('0'),
                CurrencyType.QUALITY_CRYSTALS: Decimal('0')
            }
            
            # Initialize spending limits
            wallet.daily_spending_limit = {
                CurrencyType.CREDITS: Decimal('5000'),
                CurrencyType.GEMS: Decimal('500'),
                CurrencyType.TOKENS: Decimal('1000'),
                CurrencyType.INFLUENCE_POINTS: Decimal('10000'),
                CurrencyType.COLLABORATION_COINS: Decimal('2000'),
                CurrencyType.QUALITY_CRYSTALS: Decimal('200')
            }
            
            # Initialize tracking
            wallet.total_earned = {currency: Decimal('0') for currency in CurrencyType}
            wallet.total_spent = {currency: Decimal('0') for currency in CurrencyType}
            
            self._wallets[user_id] = wallet
            self.logger.info(f"Created new wallet for user {user_id}")
        
        return self._wallets[user_id]
    
    async def process_transaction(
        self,
        user_id: str,
        transaction_type: TransactionType,
        source: TransactionSource,
        currency: CurrencyType,
        amount: Decimal,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        related_user_id: Optional[str] = None,
        related_item_id: Optional[str] = None
    ) -> VirtualTransaction:
        """Process a virtual economy transaction."""
        async with self._transaction_lock:
            try:
                wallet = await self.get_user_wallet(user_id)
                metadata = metadata or {}
                
                # Create transaction record
                transaction = VirtualTransaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    source=source,
                    currency=currency,
                    amount=amount,
                    description=description,
                    metadata=metadata,
                    related_user_id=related_user_id,
                    related_item_id=related_item_id,
                    balance_before=wallet.get_balance(currency)
                )
                
                # Validate transaction
                validation_result = await self._validate_transaction(transaction, wallet)
                if not validation_result["valid"]:
                    transaction.validation_errors = validation_result["errors"]
                    self._transactions.append(transaction)
                    return transaction
                
                # Process based on transaction type
                if transaction_type in [TransactionType.EARN, TransactionType.BONUS]:
                    await self._process_earn_transaction(transaction, wallet)
                
                elif transaction_type in [TransactionType.SPEND, TransactionType.PURCHASE]:
                    await self._process_spend_transaction(transaction, wallet)
                
                elif transaction_type == TransactionType.TRANSFER:
                    await self._process_transfer_transaction(transaction, wallet)
                
                elif transaction_type == TransactionType.EXCHANGE:
                    await self._process_exchange_transaction(transaction, wallet)
                
                elif transaction_type == TransactionType.REFUND:
                    await self._process_refund_transaction(transaction, wallet)
                
                # Update wallet metadata
                wallet.last_transaction = datetime.utcnow()
                
                # Mark transaction as processed
                transaction.processed = True
                transaction.processed_at = datetime.utcnow()
                transaction.validated = True
                transaction.balance_after = wallet.get_balance(currency)
                
                # Store transaction
                self._transactions.append(transaction)
                
                self.logger.info(
                    f"Processed {transaction_type.value} transaction: "
                    f"{amount} {currency.value} for user {user_id}"
                )
                
                return transaction
                
            except Exception as e:
                self.logger.error(f"Error processing transaction: {e}")
                # Create failed transaction record
                failed_transaction = VirtualTransaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    source=source,
                    currency=currency,
                    amount=amount,
                    description=description,
                    metadata=metadata or {},
                    validation_errors=[str(e)]
                )
                self._transactions.append(failed_transaction)
                return failed_transaction
    
    async def _validate_transaction(
        self,
        transaction: VirtualTransaction,
        wallet: VirtualWallet
    ) -> Dict[str, Any]:
        """Validate a transaction before processing."""
        errors = []
        
        # Check if wallet is locked
        if wallet.locked:
            errors.append(f"Wallet is locked: {wallet.lock_reason}")
        
        # Check for sufficient balance on spend transactions
        if transaction.transaction_type in [TransactionType.SPEND, TransactionType.PURCHASE, TransactionType.TRANSFER]:
            if not wallet.has_sufficient_balance(transaction.currency, transaction.amount):
                errors.append(f"Insufficient {transaction.currency.value} balance")
        
        # Check daily spending limits
        if transaction.transaction_type in [TransactionType.SPEND, TransactionType.PURCHASE]:
            daily_spent = await self._get_daily_spending(wallet.user_id, transaction.currency)
            daily_limit = wallet.daily_spending_limit.get(transaction.currency, Decimal('0'))
            
            if daily_spent + transaction.amount > daily_limit:
                errors.append(f"Daily spending limit exceeded for {transaction.currency.value}")
        
        # Validate amount
        if transaction.amount <= 0:
            errors.append("Transaction amount must be positive")
        
        # Validate related entities
        if transaction.transaction_type == TransactionType.TRANSFER and not transaction.related_user_id:
            errors.append("Transfer transactions require related_user_id")
        
        if transaction.transaction_type == TransactionType.PURCHASE and not transaction.related_item_id:
            errors.append("Purchase transactions require related_item_id")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _get_daily_spending(self, user_id: str, currency: CurrencyType) -> Decimal:
        """Get user's spending for today in a specific currency."""
        today = datetime.utcnow().date()
        daily_spent = Decimal('0')
        
        for transaction in self._transactions:
            if (transaction.user_id == user_id and 
                transaction.currency == currency and
                transaction.transaction_type in [TransactionType.SPEND, TransactionType.PURCHASE] and
                transaction.processed and
                transaction.timestamp.date() == today):
                daily_spent += transaction.amount
        
        return daily_spent
    
    async def _process_earn_transaction(
        self,
        transaction: VirtualTransaction,
        wallet: VirtualWallet
    ) -> None:
        """Process an earn/bonus transaction."""
        current_balance = wallet.get_balance(transaction.currency)
        new_balance = current_balance + transaction.amount
        
        wallet.balances[transaction.currency] = new_balance
        wallet.total_earned[transaction.currency] = wallet.total_earned.get(transaction.currency, Decimal('0')) + transaction.amount
    
    async def _process_spend_transaction(
        self,
        transaction: VirtualTransaction,
        wallet: VirtualWallet
    ) -> None:
        """Process a spend/purchase transaction."""
        current_balance = wallet.get_balance(transaction.currency)
        new_balance = current_balance - transaction.amount
        
        wallet.balances[transaction.currency] = new_balance
        wallet.total_spent[transaction.currency] = wallet.total_spent.get(transaction.currency, Decimal('0')) + transaction.amount
    
    async def _process_transfer_transaction(
        self,
        transaction: VirtualTransaction,
        wallet: VirtualWallet
    ) -> None:
        """Process a transfer transaction."""
        if not transaction.related_user_id:
            raise ValueError("Transfer requires related_user_id")
        
        # Deduct from sender
        await self._process_spend_transaction(transaction, wallet)
        
        # Add to receiver
        recipient_wallet = await self.get_user_wallet(transaction.related_user_id)
        recipient_balance = recipient_wallet.get_balance(transaction.currency)
        recipient_wallet.balances[transaction.currency] = recipient_balance + transaction.amount
        recipient_wallet.total_earned[transaction.currency] = recipient_wallet.total_earned.get(transaction.currency, Decimal('0')) + transaction.amount
        
        # Create corresponding receive transaction
        receive_transaction = VirtualTransaction(
            user_id=transaction.related_user_id,
            transaction_type=TransactionType.EARN,
            source=TransactionSource.PROMOTIONAL_GIFT,
            currency=transaction.currency,
            amount=transaction.amount,
            description=f"Transfer from user {transaction.user_id}",
            related_user_id=transaction.user_id,
            balance_before=recipient_balance,
            balance_after=recipient_balance + transaction.amount,
            processed=True,
            processed_at=datetime.utcnow(),
            validated=True
        )
        self._transactions.append(receive_transaction)
    
    async def _process_exchange_transaction(
        self,
        transaction: VirtualTransaction,
        wallet: VirtualWallet
    ) -> None:
        """Process a currency exchange transaction."""
        # Extract exchange details from transaction metadata
        exchange_data = transaction.metadata or {}
        from_currency = CurrencyType(exchange_data.get('from_currency', CurrencyType.POINTS))
        to_currency = transaction.currency
        exchange_rate = exchange_data.get('exchange_rate', 1.0)
        from_amount = transaction.amount / Decimal(str(exchange_rate))
        
        # Validate user has sufficient balance in source currency
        current_from_balance = wallet.get_balance(from_currency)
        if current_from_balance < from_amount:
            raise ValueError(f"Insufficient {from_currency.value} balance for exchange")
        
        # Process the exchange: deduct from source, add to target
        wallet.balances[from_currency] = current_from_balance - from_amount
        current_to_balance = wallet.get_balance(to_currency)
        wallet.balances[to_currency] = current_to_balance + transaction.amount
        
        # Log the exchange transaction details
        self.logger.info(
            f"Currency exchange processed: {from_amount} {from_currency.value} → "
            f"{transaction.amount} {to_currency.value} (rate: {exchange_rate}) for user {transaction.user_id}"
        )
    
    async def _process_refund_transaction(
        self,
        transaction: VirtualTransaction,
        wallet: VirtualWallet
    ) -> None:
        """Process a refund transaction."""
        # Add refunded amount back to wallet
        current_balance = wallet.get_balance(transaction.currency)
        new_balance = current_balance + transaction.amount
        
        wallet.balances[transaction.currency] = new_balance
        # Don't add to total_earned since it's a refund
    
    async def purchase_marketplace_item(
        self,
        user_id: str,
        item_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """Purchase an item from the virtual marketplace."""
        try:
            if item_id not in self._marketplace_items:
                return {"success": False, "error": "Item not found"}
            
            item = self._marketplace_items[item_id]
            
            if not item.is_available():
                return {"success": False, "error": "Item not available"}
            
            # Get user profile and purchase history
            wallet = await self.get_user_wallet(user_id)
            user_purchases = self._user_purchases.get(user_id, [])
            item_purchase_count = len([p for p in user_purchases if p == item_id])
            
            # Get user profile data for purchase validation
            # In production, this would integrate with the user service
            user_profile = {
                "level": "creator",
                "achievements": [],
                "membership_tier": "basic",
                "creation_date": datetime.now(timezone.utc),
                "total_points": 0,
                "subscription_active": False
            }
            
            # Check if user can purchase
            can_purchase, reasons = item.can_user_purchase(user_profile, item_purchase_count)
            if not can_purchase:
                return {"success": False, "error": f"Cannot purchase: {'; '.join(reasons)}"}
            
            # Calculate total cost
            total_cost = item.price * quantity
            
            # Check if user has sufficient balance
            if not wallet.has_sufficient_balance(item.currency, total_cost):
                return {"success": False, "error": f"Insufficient {item.currency.value} balance"}
            
            # Process purchase transaction
            transaction = await self.process_transaction(
                user_id=user_id,
                transaction_type=TransactionType.PURCHASE,
                source=TransactionSource.MARKETPLACE_PURCHASE,
                currency=item.currency,
                amount=total_cost,
                description=f"Purchase: {item.name} (x{quantity})",
                metadata={
                    "item_id": item_id,
                    "item_name": item.name,
                    "quantity": quantity,
                    "unit_price": float(item.price)
                },
                related_item_id=item_id
            )
            
            if not transaction.validated:
                return {"success": False, "error": "Transaction failed", "errors": transaction.validation_errors}
            
            # Update item statistics
            item.total_purchases += quantity
            item.total_revenue += total_cost
            
            # Update stock if limited
            if item.stock_quantity is not None:
                item.stock_quantity -= quantity
            
            # Record user purchase
            if user_id not in self._user_purchases:
                self._user_purchases[user_id] = []
            
            for _ in range(quantity):
                self._user_purchases[user_id].append(item_id)
            
            # Apply item effects (this would integrate with other systems)
            effects_applied = await self._apply_item_effects(user_id, item, quantity)
            
            self.logger.info(f"User {user_id} purchased {quantity}x {item.name}")
            
            return {
                "success": True,
                "transaction_id": transaction.transaction_id,
                "item": {
                    "id": item_id,
                    "name": item.name,
                    "quantity": quantity,
                    "total_cost": float(total_cost),
                    "currency": item.currency.value
                },
                "effects_applied": effects_applied,
                "new_balance": float(wallet.get_balance(item.currency))
            }
            
        except Exception as e:
            self.logger.error(f"Error purchasing marketplace item: {e}")
            return {"success": False, "error": str(e)}
    
    async def _apply_item_effects(
        self,
        user_id: str,
        item: MarketplaceItem,
        quantity: int
    ) -> List[Dict[str, Any]]:
        """Apply the effects of purchased items."""
        effects_applied = []
        
        # This would integrate with other systems to apply effects
        # For now, we'll just record what effects should be applied
        
        for effect_name, effect_value in item.effects.items():
            effect_record = {
                "effect_name": effect_name,
                "effect_value": effect_value,
                "quantity": quantity,
                "duration": item.duration.total_seconds() if item.duration else None,
                "applied_at": datetime.utcnow().isoformat()
            }
            effects_applied.append(effect_record)
        
        return effects_applied
    
    async def get_marketplace_items(
        self,
        category: Optional[str] = None,
        item_type: Optional[MarketplaceItemType] = None,
        user_profile: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get marketplace items with optional filtering."""
        try:
            filtered_items = []
            
            for item in self._marketplace_items.values():
                # Apply filters
                if category and item.category != category:
                    continue
                
                if item_type and item.item_type != item_type:
                    continue
                
                if not item.is_available():
                    continue
                
                # Check user eligibility if profile provided
                if user_profile:
                    user_purchases = self._user_purchases.get(user_profile.get("user_id", ""), [])
                    item_purchase_count = len([p for p in user_purchases if p == item.item_id])
                    
                    can_purchase, _ = item.can_user_purchase(user_profile, item_purchase_count)
                    if not can_purchase:
                        continue
                
                # Convert to serializable format
                item_data = {
                    "item_id": item.item_id,
                    "name": item.name,
                    "description": item.description,
                    "detailed_description": item.detailed_description,
                    "type": item.item_type.value,
                    "category": item.category,
                    "price": float(item.price),
                    "currency": item.currency.value,
                    "alternative_currencies": {k.value: float(v) for k, v in item.alternative_currencies.items()},
                    "rarity": item.rarity,
                    "tags": item.tags,
                    "icon_url": item.icon_url,
                    "preview_images": item.preview_images,
                    "effects": item.effects,
                    "duration_hours": item.duration.total_seconds() / 3600 if item.duration else None,
                    "level_requirement": item.level_requirement,
                    "achievement_requirements": item.achievement_requirements,
                    "creator_type_requirements": item.creator_type_requirements,
                    "max_per_user": item.max_per_user,
                    "stock_quantity": item.stock_quantity,
                    "total_purchases": item.total_purchases,
                    "popularity_score": item.popularity_score
                }
                
                filtered_items.append(item_data)
            
            # Sort by popularity and rarity
            rarity_order = {"common": 1, "uncommon": 2, "rare": 3, "epic": 4, "legendary": 5}
            filtered_items.sort(key=lambda x: (-x["popularity_score"], -rarity_order.get(x["rarity"], 0)))
            
            # Apply pagination
            total_items = len(filtered_items)
            paginated_items = filtered_items[offset:offset + limit]
            
            return {
                "items": paginated_items,
                "pagination": {
                    "total": total_items,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_items
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting marketplace items: {e}")
            return {"items": [], "pagination": {"total": 0, "limit": limit, "offset": offset, "has_more": False}}
    
    async def get_user_transaction_history(
        self,
        user_id: str,
        currency: Optional[CurrencyType] = None,
        transaction_type: Optional[TransactionType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user's transaction history with optional filtering."""
        try:
            user_transactions = []
            
            for transaction in self._transactions:
                if transaction.user_id != user_id:
                    continue
                
                if currency and transaction.currency != currency:
                    continue
                
                if transaction_type and transaction.transaction_type != transaction_type:
                    continue
                
                transaction_data = {
                    "transaction_id": transaction.transaction_id,
                    "type": transaction.transaction_type.value,
                    "source": transaction.source.value,
                    "currency": transaction.currency.value,
                    "amount": float(transaction.amount),
                    "description": transaction.description,
                    "timestamp": transaction.timestamp.isoformat(),
                    "processed": transaction.processed,
                    "validated": transaction.validated,
                    "balance_before": float(transaction.balance_before),
                    "balance_after": float(transaction.balance_after),
                    "metadata": transaction.metadata
                }
                
                user_transactions.append(transaction_data)
            
            # Sort by timestamp (newest first)
            user_transactions.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Apply pagination
            total_transactions = len(user_transactions)
            paginated_transactions = user_transactions[offset:offset + limit]
            
            return {
                "transactions": paginated_transactions,
                "pagination": {
                    "total": total_transactions,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_transactions
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user transaction history: {e}")
            return {"transactions": [], "pagination": {"total": 0, "limit": limit, "offset": offset, "has_more": False}}
    
    async def get_user_financial_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive financial summary for a user."""
        try:
            wallet = await self.get_user_wallet(user_id)
            
            # Calculate net worth
            net_worth = wallet.get_net_worth(self._exchange_rates)
            
            # Get recent transaction statistics
            recent_transactions = [
                t for t in self._transactions
                if (t.user_id == user_id and 
                    t.processed and
                    (datetime.utcnow() - t.timestamp).days <= 30)
            ]
            
            # Calculate monthly earning/spending
            monthly_earned = {}
            monthly_spent = {}
            
            for currency in CurrencyType:
                earned = sum(
                    t.amount for t in recent_transactions
                    if t.currency == currency and t.transaction_type in [TransactionType.EARN, TransactionType.BONUS]
                )
                spent = sum(
                    t.amount for t in recent_transactions
                    if t.currency == currency and t.transaction_type in [TransactionType.SPEND, TransactionType.PURCHASE]
                )
                
                monthly_earned[currency.value] = float(earned)
                monthly_spent[currency.value] = float(spent)
            
            # Get purchase statistics
            user_purchases = self._user_purchases.get(user_id, [])
            unique_items_purchased = len(set(user_purchases))
            total_purchases = len(user_purchases)
            
            return {
                "user_id": user_id,
                "wallet": {
                    "balances": {k.value: float(v) for k, v in wallet.balances.items()},
                    "net_worth_credits": float(net_worth),
                    "total_earned": {k.value: float(v) for k, v in wallet.total_earned.items()},
                    "total_spent": {k.value: float(v) for k, v in wallet.total_spent.items()},
                    "daily_spending_limits": {k.value: float(v) for k, v in wallet.daily_spending_limit.items()},
                    "locked": wallet.locked,
                    "last_transaction": wallet.last_transaction.isoformat() if wallet.last_transaction else None
                },
                "monthly_activity": {
                    "earned": monthly_earned,
                    "spent": monthly_spent,
                    "transactions_count": len(recent_transactions)
                },
                "marketplace_activity": {
                    "total_purchases": total_purchases,
                    "unique_items_purchased": unique_items_purchased
                },
                "exchange_rates": {k.value: float(v) for k, v in self._exchange_rates.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user financial summary: {e}")
            return {}
    
    async def daily_login_bonus(self, user_id: str, consecutive_days: int) -> VirtualTransaction:
        """Award daily login bonus based on consecutive days."""
        try:
            # Calculate bonus based on streak
            base_credits = 25
            streak_bonus = min(consecutive_days * 5, 100)  # Max 100 bonus credits
            total_credits = base_credits + streak_bonus
            
            # Add gem bonus for longer streaks
            gem_bonus = 0
            if consecutive_days >= 7:
                gem_bonus = 1
            if consecutive_days >= 30:
                gem_bonus = 5
            
            # Process credits transaction
            credits_transaction = await self.process_transaction(
                user_id=user_id,
                transaction_type=TransactionType.BONUS,
                source=TransactionSource.DAILY_LOGIN,
                currency=CurrencyType.CREDITS,
                amount=Decimal(str(total_credits)),
                description=f"Daily login bonus (Day {consecutive_days})",
                metadata={
                    "consecutive_days": consecutive_days,
                    "base_bonus": base_credits,
                    "streak_bonus": streak_bonus
                }
            )
            
            # Process gem bonus if applicable
            if gem_bonus > 0:
                await self.process_transaction(
                    user_id=user_id,
                    transaction_type=TransactionType.BONUS,
                    source=TransactionSource.DAILY_LOGIN,
                    currency=CurrencyType.GEMS,
                    amount=Decimal(str(gem_bonus)),
                    description=f"Daily login gem bonus (Day {consecutive_days})",
                    metadata={
                        "consecutive_days": consecutive_days,
                        "gem_bonus": gem_bonus
                    }
                )
            
            return credits_transaction
            
        except Exception as e:
            self.logger.error(f"Error awarding daily login bonus: {e}")
            raise


# Global virtual economy instance
_virtual_economy: Optional[VirtualEconomy] = None


async def get_virtual_economy() -> VirtualEconomy:
    """Get the global virtual economy instance."""
    global _virtual_economy
    
    if _virtual_economy is None:
        _virtual_economy = VirtualEconomy()
    
    return _virtual_economy


# Convenience functions for common operations
async def award_currency(
    user_id: str,
    currency: CurrencyType,
    amount: Union[int, float, Decimal],
    source: TransactionSource,
    description: str = ""
) -> VirtualTransaction:
    """Award currency to a user (convenience function)."""
    economy = await get_virtual_economy()
    return await economy.process_transaction(
        user_id=user_id,
        transaction_type=TransactionType.EARN,
        source=source,
        currency=currency,
        amount=Decimal(str(amount)),
        description=description
    )


async def spend_currency(
    user_id: str,
    currency: CurrencyType,
    amount: Union[int, float, Decimal],
    source: TransactionSource,
    description: str = ""
) -> VirtualTransaction:
    """Spend currency for a user (convenience function)."""
    economy = await get_virtual_economy()
    return await economy.process_transaction(
        user_id=user_id,
        transaction_type=TransactionType.SPEND,
        source=source,
        currency=currency,
        amount=Decimal(str(amount)),
        description=description
    )


async def get_user_balance(user_id: str, currency: CurrencyType) -> Decimal:
    """Get user's balance for a specific currency (convenience function)."""
    economy = await get_virtual_economy()
    wallet = await economy.get_user_wallet(user_id)
    return wallet.get_balance(currency)