"""Point System - Système de points
=================================

Point management system for tracking, awarding, and managing various
types of points and virtual currencies for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal


class PointType(str, Enum):
    """Types of points in the system."""
    EXPERIENCE_POINTS = "xp"
    CREDITS = "credits"
    COLLABORATION_COINS = "collaboration_coins"
    QUALITY_CRYSTALS = "quality_crystals"
    ACHIEVEMENT_GEMS = "achievement_gems"
    CREATOR_TOKENS = "creator_tokens"
    PREMIUM_POINTS = "premium_points"


class TransactionType(str, Enum):
    """Types of point transactions."""
    EARNED = "earned"
    SPENT = "spent"
    BONUS = "bonus"
    PENALTY = "penalty"
    TRANSFER = "transfer"
    EXCHANGE = "exchange"
    REFUND = "refund"


@dataclass
class PointTransaction:
    """Point transaction record."""
    id: str
    user_id: str
    point_type: PointType
    transaction_type: TransactionType
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    source: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UserPointBalance:
    """User's point balances."""
    user_id: str
    balances: Dict[PointType, Decimal] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_earned: Dict[PointType, Decimal] = field(default_factory=dict)
    total_spent: Dict[PointType, Decimal] = field(default_factory=dict)


@dataclass
class PointMultiplier:
    """Point earning multiplier."""
    name: str
    multiplier: float
    point_types: List[PointType]
    condition: str
    active_until: Optional[datetime] = None
    max_applications: Optional[int] = None
    current_applications: int = 0


class PointSystem:
    """
    Comprehensive point management system providing sophisticated point
    tracking, exchange rates, and virtual economy management.
    """
    
    def __init__(self, database_connection=None, cache_client=None):
        """Initialize the point system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.cache = cache_client
        self.user_balances: Dict[str, UserPointBalance] = {}
        self.transactions: List[PointTransaction] = []
        self.multipliers: Dict[str, PointMultiplier] = {}
        self.exchange_rates: Dict[str, Decimal] = {}
        
        # Initialize system
        self._initialize_exchange_rates()
        self._initialize_default_multipliers()
        
        self.logger.info("PointSystem initialized")
    
    def _initialize_exchange_rates(self):
        """Initialize exchange rates between point types."""
        try:
            # Base exchange rates (relative to credits)
            self.exchange_rates = {
                "credits_to_collaboration_coins": Decimal("0.8"),
                "credits_to_quality_crystals": Decimal("0.5"),
                "credits_to_achievement_gems": Decimal("0.3"),
                "credits_to_creator_tokens": Decimal("0.1"),
                "credits_to_premium_points": Decimal("0.05"),
                
                # Reverse rates
                "collaboration_coins_to_credits": Decimal("1.25"),
                "quality_crystals_to_credits": Decimal("2.0"),
                "achievement_gems_to_credits": Decimal("3.33"),
                "creator_tokens_to_credits": Decimal("10.0"),
                "premium_points_to_credits": Decimal("20.0"),
            }
            
            self.logger.info(f"Initialized {len(self.exchange_rates)} exchange rates")
            
        except Exception as e:
            self.logger.error(f"Error initializing exchange rates: {e}")
    
    def _initialize_default_multipliers(self):
        """Initialize default point multipliers."""
        try:
            # Weekend bonus
            self.multipliers["weekend_bonus"] = PointMultiplier(
                name="Weekend Bonus",
                multiplier=1.5,
                point_types=[PointType.EXPERIENCE_POINTS, PointType.CREDITS],
                condition="weekend",
                active_until=None
            )
            
            # New user bonus
            self.multipliers["new_user_bonus"] = PointMultiplier(
                name="New User Bonus",
                multiplier=2.0,
                point_types=list(PointType),
                condition="first_week",
                active_until=None,
                max_applications=10
            )
            
            # Quality content bonus
            self.multipliers["quality_bonus"] = PointMultiplier(
                name="Quality Content Bonus",
                multiplier=1.25,
                point_types=[PointType.QUALITY_CRYSTALS, PointType.CREDITS],
                condition="high_quality_score"
            )
            
            self.logger.info(f"Initialized {len(self.multipliers)} default multipliers")
            
        except Exception as e:
            self.logger.error(f"Error initializing default multipliers: {e}")
    
    async def award_points(
        self,
        user_id: str,
        point_type: PointType,
        amount: Union[int, float, Decimal],
        source: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Award points to a user."""
        try:
            amount = Decimal(str(amount))
            
            # Apply multipliers
            final_amount = await self._apply_multipliers(user_id, point_type, amount, source)
            
            # Get current balance
            balance = await self.get_user_balance(user_id)
            current_balance = balance.balances.get(point_type, Decimal("0"))
            new_balance = current_balance + final_amount
            
            # Create transaction
            transaction = PointTransaction(
                id=f"txn_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                point_type=point_type,
                transaction_type=TransactionType.EARNED,
                amount=final_amount,
                balance_before=current_balance,
                balance_after=new_balance,
                source=source,
                description=description,
                metadata=metadata or {}
            )
            
            # Update balance
            balance.balances[point_type] = new_balance
            balance.total_earned[point_type] = balance.total_earned.get(point_type, Decimal("0")) + final_amount
            balance.last_updated = datetime.now(timezone.utc)
            
            # Store transaction
            self.transactions.append(transaction)
            self.user_balances[user_id] = balance
            
            self.logger.info(f"💎 Awarded {final_amount} {point_type} to user {user_id} from {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error awarding points: {e}")
            return False
    
    async def spend_points(
        self,
        user_id: str,
        point_type: PointType,
        amount: Union[int, float, Decimal],
        source: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Spend points for a user."""
        try:
            amount = Decimal(str(amount))
            
            # Get current balance
            balance = await self.get_user_balance(user_id)
            current_balance = balance.balances.get(point_type, Decimal("0"))
            
            # Check sufficient balance
            if current_balance < amount:
                self.logger.warning(f"Insufficient {point_type} for user {user_id}: {current_balance} < {amount}")
                return False
            
            new_balance = current_balance - amount
            
            # Create transaction
            transaction = PointTransaction(
                id=f"txn_{user_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                point_type=point_type,
                transaction_type=TransactionType.SPENT,
                amount=-amount,
                balance_before=current_balance,
                balance_after=new_balance,
                source=source,
                description=description,
                metadata=metadata or {}
            )
            
            # Update balance
            balance.balances[point_type] = new_balance
            balance.total_spent[point_type] = balance.total_spent.get(point_type, Decimal("0")) + amount
            balance.last_updated = datetime.now(timezone.utc)
            
            # Store transaction
            self.transactions.append(transaction)
            self.user_balances[user_id] = balance
            
            self.logger.info(f"💸 User {user_id} spent {amount} {point_type} for {source}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error spending points: {e}")
            return False
    
    async def exchange_points(
        self,
        user_id: str,
        from_type: PointType,
        to_type: PointType,
        amount: Union[int, float, Decimal]
    ) -> bool:
        """Exchange one point type for another."""
        try:
            amount = Decimal(str(amount))
            
            # Get exchange rate
            from_value = from_type.value if hasattr(from_type, 'value') else str(from_type)
            to_value = to_type.value if hasattr(to_type, 'value') else str(to_type)
            exchange_key = f"{from_value}_to_{to_value}"
            if exchange_key not in self.exchange_rates:
                self.logger.warning(f"Exchange rate not found: {exchange_key}")
                return False
            
            rate = self.exchange_rates[exchange_key]
            received_amount = amount * rate
            
            # Check balance and perform exchange
            balance = await self.get_user_balance(user_id)
            current_balance = balance.balances.get(from_type, Decimal("0"))
            
            if current_balance < amount:
                self.logger.warning(f"Insufficient {from_type} for exchange: {current_balance} < {amount}")
                return False
            
            # Spend source points
            await self.spend_points(
                user_id, from_type, amount, "exchange",
                f"Exchanged {amount} {from_type} to {to_type}"
            )
            
            # Award target points
            await self.award_points(
                user_id, to_type, received_amount, "exchange",
                f"Received from exchanging {amount} {from_type}"
            )
            
            self.logger.info(f"🔄 User {user_id} exchanged {amount} {from_type} for {received_amount} {to_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exchanging points: {e}")
            return False
    
    async def _apply_multipliers(
        self,
        user_id: str,
        point_type: PointType,
        amount: Decimal,
        source: str
    ) -> Decimal:
        """Apply applicable multipliers to point amount."""
        try:
            final_amount = amount
            applied_multipliers = []
            
            for multiplier_id, multiplier in self.multipliers.items():
                # Check if point type is eligible
                if point_type not in multiplier.point_types:
                    continue
                
                # Check conditions
                if await self._check_multiplier_condition(user_id, multiplier, source):
                    # Check usage limits
                    if multiplier.max_applications and multiplier.current_applications >= multiplier.max_applications:
                        continue
                    
                    # Check expiry
                    if multiplier.active_until and datetime.now(timezone.utc) > multiplier.active_until:
                        continue
                    
                    # Apply multiplier
                    final_amount *= Decimal(str(multiplier.multiplier))
                    applied_multipliers.append(multiplier.name)
                    multiplier.current_applications += 1
            
            if applied_multipliers:
                self.logger.info(f"Applied multipliers to {user_id}: {applied_multipliers}")
            
            return final_amount
            
        except Exception as e:
            self.logger.error(f"Error applying multipliers: {e}")
            return amount
    
    async def _check_multiplier_condition(
        self,
        user_id: str,
        multiplier: PointMultiplier,
        source: str
    ) -> bool:
        """Check if multiplier condition is met."""
        try:
            condition = multiplier.condition
            
            if condition == "weekend":
                # Check if it's weekend
                now = datetime.now(timezone.utc)
                return now.weekday() >= 5  # Saturday or Sunday
            
            elif condition == "first_week":
                # Check if user is in first week (simplified)
                # In real implementation, would check user registration date
                return True
            
            elif condition == "high_quality_score":
                # Check if source indicates high quality
                return "quality" in source.lower() or "viral" in source.lower()
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking multiplier condition: {e}")
            return False
    
    async def get_user_balance(self, user_id: str) -> UserPointBalance:
        """Get user's current point balances."""
        if user_id not in self.user_balances:
            self.user_balances[user_id] = UserPointBalance(
                user_id=user_id,
                balances={pt: Decimal("0") for pt in PointType},
                total_earned={pt: Decimal("0") for pt in PointType},
                total_spent={pt: Decimal("0") for pt in PointType}
            )
        
        return self.user_balances[user_id]
    
    async def get_user_transactions(
        self,
        user_id: str,
        limit: int = 50,
        point_type: Optional[PointType] = None
    ) -> List[Dict[str, Any]]:
        """Get user's point transaction history."""
        try:
            user_transactions = [
                t for t in self.transactions
                if t.user_id == user_id and (not point_type or t.point_type == point_type)
            ]
            
            # Sort by timestamp (newest first)
            user_transactions.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply limit
            limited_transactions = user_transactions[:limit]
            
            return [
                {
                    "id": t.id,
                    "point_type": t.point_type,
                    "transaction_type": t.transaction_type,
                    "amount": float(t.amount),
                    "balance_before": float(t.balance_before),
                    "balance_after": float(t.balance_after),
                    "source": t.source,
                    "description": t.description,
                    "timestamp": t.timestamp.isoformat(),
                    "metadata": t.metadata
                }
                for t in limited_transactions
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting user transactions: {e}")
            return []
    
    async def get_user_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive point summary for a user."""
        try:
            balance = await self.get_user_balance(user_id)
            recent_transactions = await self.get_user_transactions(user_id, limit=10)
            
            summary = {
                "user_id": user_id,
                "balances": {pt: float(balance.balances[pt]) for pt in PointType},
                "total_earned": {pt: float(balance.total_earned[pt]) for pt in PointType},
                "total_spent": {pt: float(balance.total_spent[pt]) for pt in PointType},
                "last_updated": balance.last_updated.isoformat(),
                "recent_transactions": recent_transactions,
                "total_transaction_count": len([t for t in self.transactions if t.user_id == user_id])
            }
            
            # Calculate total value in credits
            total_value = Decimal("0")
            for pt, amount in balance.balances.items():
                if pt == PointType.CREDITS:
                    total_value += amount
                else:
                    # Convert to credits using exchange rate
                    pt_value = pt.value if hasattr(pt, 'value') else str(pt)
                    exchange_key = f"{pt_value}_to_credits"
                    if exchange_key in self.exchange_rates:
                        total_value += amount * self.exchange_rates[exchange_key]
            
            summary["total_value_in_credits"] = float(total_value)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting user summary: {e}")
            return {}
    
    async def process_action(
        self,
        user_id: str,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process a user action and award appropriate points."""
        results = []
        
        try:
            # Map action types to point awards
            point_awards = {
                "content_upload": [(PointType.EXPERIENCE_POINTS, 50), (PointType.CREDITS, 10)],
                "content_view": [(PointType.EXPERIENCE_POINTS, 1)],
                "collaboration_complete": [(PointType.COLLABORATION_COINS, 100), (PointType.EXPERIENCE_POINTS, 200)],
                "achievement_unlock": [(PointType.ACHIEVEMENT_GEMS, 10), (PointType.EXPERIENCE_POINTS, 100)],
                "quality_milestone": [(PointType.QUALITY_CRYSTALS, 25), (PointType.CREDITS, 50)]
            }
            
            awards = point_awards.get(action_type, [])
            
            for point_type, base_amount in awards:
                # Apply action-specific modifiers
                amount = base_amount
                if action_type == "content_view":
                    amount = min(action_data.get("view_count", 1) // 100, 10)  # 1 XP per 100 views, max 10
                elif action_type == "quality_milestone":
                    quality_score = action_data.get("quality_score", 1.0)
                    amount = int(base_amount * quality_score)
                
                # Award points
                if amount > 0:
                    success = await self.award_points(
                        user_id, point_type, amount, action_type,
                        f"Points for {action_type}", action_data
                    )
                    
                    if success:
                        results.append({
                            "type": "points_awarded",
                            "point_type": point_type,
                            "amount": amount,
                            "source": action_type
                        })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing action for points: {e}")
            return []


# Global instance
_point_system = None

def get_point_system(database_connection=None, cache_client=None) -> PointSystem:
    """Get the global point system instance."""
    global _point_system
    if _point_system is None:
        _point_system = PointSystem(database_connection, cache_client)
    return _point_system