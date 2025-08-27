"""
Commission Manager - Professional commission and affiliate tracking system.
Handles revenue sharing, affiliate programs, and commission calculations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class CommissionType(Enum):
    """Types of commission structures."""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


class CommissionStatus(Enum):
    """Commission payment status."""
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    HOLD = "hold"


class AffiliateStatus(Enum):
    """Affiliate account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_APPROVAL = "pending_approval"
    BANNED = "banned"


class PayoutMethod(Enum):
    """Available payout methods."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CHECK = "check"
    CRYPTOCURRENCY = "cryptocurrency"


@dataclass
class CommissionRule:
    """Commission calculation rule."""
    rule_id: str
    name: str
    commission_type: CommissionType
    rate: Decimal  # Percentage (0-100) or fixed amount
    min_amount: Decimal = Decimal("0")
    max_amount: Optional[Decimal] = None
    tier_rates: Dict[str, Decimal] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_commission(self, amount: Decimal, metadata: Dict[str, Any] = None) -> Decimal:
        """Calculate commission based on rule."""
        if amount < self.min_amount:
            return Decimal("0")
        
        commission = Decimal("0")
        
        if self.commission_type == CommissionType.PERCENTAGE:
            commission = (amount * self.rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        elif self.commission_type == CommissionType.FIXED_AMOUNT:
            commission = self.rate
        elif self.commission_type == CommissionType.TIERED:
            commission = self._calculate_tiered_commission(amount)
        elif self.commission_type == CommissionType.PERFORMANCE_BASED:
            commission = self._calculate_performance_commission(amount, metadata or {})
        
        # Apply max amount limit
        if self.max_amount and commission > self.max_amount:
            commission = self.max_amount
        
        return commission
    
    def _calculate_tiered_commission(self, amount: Decimal) -> Decimal:
        """Calculate tiered commission."""
        if not self.tier_rates:
            return Decimal("0")
        
        # Sort tiers by threshold
        sorted_tiers = sorted(
            [(Decimal(threshold), rate) for threshold, rate in self.tier_rates.items()],
            key=lambda x: x[0]
        )
        
        commission = Decimal("0")
        remaining_amount = amount
        
        for i, (threshold, rate) in enumerate(sorted_tiers):
            if remaining_amount <= 0:
                break
            
            # Calculate amount in this tier
            if i < len(sorted_tiers) - 1:
                next_threshold = sorted_tiers[i + 1][0]
                tier_amount = min(remaining_amount, next_threshold - threshold)
            else:
                tier_amount = remaining_amount
            
            tier_commission = (tier_amount * rate / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            commission += tier_commission
            remaining_amount -= tier_amount
        
        return commission
    
    def _calculate_performance_commission(self, amount: Decimal, metadata: Dict[str, Any]) -> Decimal:
        """Calculate performance-based commission."""
        base_commission = (amount * self.rate / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Performance multipliers
        performance_score = metadata.get("performance_score", 1.0)
        quality_score = metadata.get("quality_score", 1.0)
        
        multiplier = Decimal(str(performance_score * quality_score))
        return (base_commission * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Affiliate:
    """Affiliate partner information."""
    affiliate_id: str
    user_id: str
    name: str
    email: str
    status: AffiliateStatus
    commission_rule_id: str
    referral_code: str
    total_earnings: Decimal = Decimal("0")
    total_referrals: int = 0
    conversion_rate: float = 0.0
    payout_method: PayoutMethod = PayoutMethod.PAYPAL
    payout_details: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert affiliate to dictionary."""
        return {
            "affiliate_id": self.affiliate_id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "status": self.status.value,
            "commission_rule_id": self.commission_rule_id,
            "referral_code": self.referral_code,
            "total_earnings": float(self.total_earnings),
            "total_referrals": self.total_referrals,
            "conversion_rate": self.conversion_rate,
            "payout_method": self.payout_method.value,
            "payout_details": self.payout_details,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Commission:
    """Individual commission record."""
    commission_id: str
    affiliate_id: str
    transaction_id: str
    amount: Decimal
    commission_amount: Decimal
    rule_id: str
    status: CommissionStatus = CommissionStatus.PENDING
    reference_type: str = "sale"  # sale, subscription, referral
    reference_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert commission to dictionary."""
        return {
            "commission_id": self.commission_id,
            "affiliate_id": self.affiliate_id,
            "transaction_id": self.transaction_id,
            "amount": float(self.amount),
            "commission_amount": float(self.commission_amount),
            "rule_id": self.rule_id,
            "status": self.status.value,
            "reference_type": self.reference_type,
            "reference_id": self.reference_id,
            "metadata": self.metadata,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class PayoutBatch:
    """Batch payout processing."""
    batch_id: str
    total_amount: Decimal
    commission_count: int
    status: str = "pending"
    commission_ids: List[str] = field(default_factory=list)
    payout_method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class CommissionCalculator(ABC):
    """Abstract base class for commission calculators."""
    
    @abstractmethod
    def calculate(
        self, 
        amount: Decimal, 
        rule: CommissionRule, 
        metadata: Dict[str, Any] = None
    ) -> Decimal:
        """Calculate commission amount."""
        pass


class StandardCommissionCalculator(CommissionCalculator):
    """Standard commission calculation implementation."""
    
    def calculate(
        self, 
        amount: Decimal, 
        rule: CommissionRule, 
        metadata: Dict[str, Any] = None
    ) -> Decimal:
        """Calculate commission using standard rules."""
        return rule.calculate_commission(amount, metadata)


class CommissionManager:
    """
    Professional commission and affiliate management system.
    Handles all aspects of commission tracking, calculation, and payouts.
    """
    
    def __init__(self):
        self.commission_rules: Dict[str, CommissionRule] = {}
        self.affiliates: Dict[str, Affiliate] = {}
        self.commissions: Dict[str, Commission] = {}
        self.payout_batches: Dict[str, PayoutBatch] = {}
        self.calculator = StandardCommissionCalculator()
        self.default_rules = self._create_default_rules()
        self.min_payout_amount = Decimal("50.00")
        self.payout_schedule_days = 30
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize commission manager."""
        try:
            # Create default commission rules
            for rule in self.default_rules:
                self.commission_rules[rule.rule_id] = rule
            
            self.is_initialized = True
            logger.info("Commission manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"Commission manager initialization failed: {e}")
            return False
    
    def _create_default_rules(self) -> List[CommissionRule]:
        """Create default commission rules."""
        rules = []
        
        # Basic affiliate rule
        basic_rule = CommissionRule(
            rule_id="basic_affiliate",
            name="Basic Affiliate Commission",
            commission_type=CommissionType.PERCENTAGE,
            rate=Decimal("10.0"),  # 10%
            min_amount=Decimal("5.00")
        )
        rules.append(basic_rule)
        
        # Premium affiliate rule
        premium_rule = CommissionRule(
            rule_id="premium_affiliate",
            name="Premium Affiliate Commission",
            commission_type=CommissionType.PERCENTAGE,
            rate=Decimal("15.0"),  # 15%
            min_amount=Decimal("1.00")
        )
        rules.append(premium_rule)
        
        # Tiered commission rule
        tiered_rule = CommissionRule(
            rule_id="tiered_affiliate",
            name="Tiered Affiliate Commission",
            commission_type=CommissionType.TIERED,
            rate=Decimal("0"),  # Base rate (not used for tiered)
            tier_rates={
                "0": Decimal("5.0"),     # 0-100: 5%
                "100": Decimal("10.0"),  # 100-500: 10%
                "500": Decimal("15.0"),  # 500+: 15%
            },
            min_amount=Decimal("1.00")
        )
        rules.append(tiered_rule)
        
        # Performance-based rule
        performance_rule = CommissionRule(
            rule_id="performance_affiliate",
            name="Performance-Based Commission",
            commission_type=CommissionType.PERFORMANCE_BASED,
            rate=Decimal("12.0"),  # Base 12%
            min_amount=Decimal("1.00")
        )
        rules.append(performance_rule)
        
        return rules
    
    async def register_affiliate(
        self, 
        user_id: str, 
        name: str, 
        email: str,
        commission_rule_id: str = "basic_affiliate"
    ) -> Optional[Affiliate]:
        """Register a new affiliate."""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            affiliate_id = str(uuid.uuid4())
            referral_code = self._generate_referral_code(name)
            
            affiliate = Affiliate(
                affiliate_id=affiliate_id,
                user_id=user_id,
                name=name,
                email=email,
                status=AffiliateStatus.PENDING_APPROVAL,
                commission_rule_id=commission_rule_id,
                referral_code=referral_code
            )
            
            self.affiliates[affiliate_id] = affiliate
            
            logger.info(f"Affiliate registered: {affiliate_id} ({name})")
            return affiliate
            
        except Exception as e:
            logger.error(f"Affiliate registration failed: {e}")
            return None
    
    async def approve_affiliate(self, affiliate_id: str) -> bool:
        """Approve an affiliate application."""
        affiliate = self.affiliates.get(affiliate_id)
        if not affiliate:
            return False
        
        try:
            affiliate.status = AffiliateStatus.ACTIVE
            affiliate.updated_at = datetime.utcnow()
            
            logger.info(f"Affiliate approved: {affiliate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Affiliate approval failed: {e}")
            return False
    
    async def create_commission(
        self,
        affiliate_id: str,
        transaction_id: str,
        amount: Decimal,
        reference_type: str = "sale",
        reference_id: str = "",
        metadata: Dict[str, Any] = None
    ) -> Optional[Commission]:
        """Create a new commission record."""
        affiliate = self.affiliates.get(affiliate_id)
        if not affiliate or affiliate.status != AffiliateStatus.ACTIVE:
            logger.warning(f"Invalid or inactive affiliate: {affiliate_id}")
            return None
        
        rule = self.commission_rules.get(affiliate.commission_rule_id)
        if not rule:
            logger.error(f"Commission rule not found: {affiliate.commission_rule_id}")
            return None
        
        try:
            commission_amount = self.calculator.calculate(amount, rule, metadata)
            
            if commission_amount <= 0:
                logger.info(f"No commission calculated for amount {amount}")
                return None
            
            commission_id = str(uuid.uuid4())
            commission = Commission(
                commission_id=commission_id,
                affiliate_id=affiliate_id,
                transaction_id=transaction_id,
                amount=amount,
                commission_amount=commission_amount,
                rule_id=rule.rule_id,
                reference_type=reference_type,
                reference_id=reference_id,
                metadata=metadata or {}
            )
            
            self.commissions[commission_id] = commission
            
            # Update affiliate stats
            affiliate.total_earnings += commission_amount
            affiliate.total_referrals += 1
            affiliate.updated_at = datetime.utcnow()
            
            logger.info(f"Commission created: {commission_id}, amount: {commission_amount}")
            return commission
            
        except Exception as e:
            logger.error(f"Commission creation failed: {e}")
            return None
    
    async def approve_commission(self, commission_id: str) -> bool:
        """Approve a pending commission."""
        commission = self.commissions.get(commission_id)
        if not commission:
            return False
        
        try:
            commission.status = CommissionStatus.APPROVED
            commission.approved_at = datetime.utcnow()
            
            logger.info(f"Commission approved: {commission_id}")
            return True
            
        except Exception as e:
            logger.error(f"Commission approval failed: {e}")
            return False
    
    async def process_payouts(
        self, 
        payout_method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    ) -> PayoutBatch:
        """Process commission payouts."""
        try:
            # Find approved commissions ready for payout
            eligible_commissions = []
            affiliate_totals = {}
            
            for commission in self.commissions.values():
                if commission.status == CommissionStatus.APPROVED:
                    # Check if enough time has passed since approval
                    days_since_approval = (datetime.utcnow() - commission.approved_at).days
                    if days_since_approval >= self.payout_schedule_days:
                        eligible_commissions.append(commission)
                        
                        # Track affiliate totals
                        affiliate_id = commission.affiliate_id
                        if affiliate_id not in affiliate_totals:
                            affiliate_totals[affiliate_id] = Decimal("0")
                        affiliate_totals[affiliate_id] += commission.commission_amount
            
            # Filter affiliates with minimum payout amount
            payout_commissions = []
            total_payout_amount = Decimal("0")
            
            for commission in eligible_commissions:
                affiliate_total = affiliate_totals[commission.affiliate_id]
                if affiliate_total >= self.min_payout_amount:
                    payout_commissions.append(commission)
                    total_payout_amount += commission.commission_amount
            
            if not payout_commissions:
                logger.info("No commissions eligible for payout")
                return PayoutBatch(
                    batch_id="empty_batch",
                    total_amount=Decimal("0"),
                    commission_count=0,
                    status="empty"
                )
            
            # Create payout batch
            batch_id = str(uuid.uuid4())
            batch = PayoutBatch(
                batch_id=batch_id,
                total_amount=total_payout_amount,
                commission_count=len(payout_commissions),
                commission_ids=[c.commission_id for c in payout_commissions],
                payout_method=payout_method
            )
            
            # Update commission statuses
            for commission in payout_commissions:
                commission.status = CommissionStatus.PAID
                commission.paid_at = datetime.utcnow()
            
            self.payout_batches[batch_id] = batch
            
            logger.info(f"Payout batch created: {batch_id}, amount: {total_payout_amount}")
            return batch
            
        except Exception as e:
            logger.error(f"Payout processing failed: {e}")
            return PayoutBatch(
                batch_id="error_batch",
                total_amount=Decimal("0"),
                commission_count=0,
                status="error"
            )
    
    async def get_affiliate_performance(self, affiliate_id: str, days: int = 30) -> Dict[str, Any]:
        """Get affiliate performance metrics."""
        affiliate = self.affiliates.get(affiliate_id)
        if not affiliate:
            return {}
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        period_commissions = [
            c for c in self.commissions.values()
            if c.affiliate_id == affiliate_id and c.created_at >= cutoff_date
        ]
        
        total_commissions = sum(c.commission_amount for c in period_commissions)
        total_sales = sum(c.amount for c in period_commissions)
        commission_count = len(period_commissions)
        
        return {
            "affiliate_id": affiliate_id,
            "period_days": days,
            "total_commissions": float(total_commissions),
            "total_sales": float(total_sales),
            "commission_count": commission_count,
            "average_commission": float(total_commissions / commission_count) if commission_count else 0,
            "conversion_rate": affiliate.conversion_rate,
            "status": affiliate.status.value,
            "total_lifetime_earnings": float(affiliate.total_earnings),
            "total_lifetime_referrals": affiliate.total_referrals
        }
    
    async def get_commission_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get commission system analytics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        period_commissions = [
            c for c in self.commissions.values()
            if c.created_at >= cutoff_date
        ]
        
        total_commissions = sum(c.commission_amount for c in period_commissions)
        total_sales = sum(c.amount for c in period_commissions)
        
        # Status distribution
        status_dist = {}
        for commission in period_commissions:
            status = commission.status.value
            status_dist[status] = status_dist.get(status, 0) + 1
        
        # Top affiliates
        affiliate_performance = {}
        for commission in period_commissions:
            aid = commission.affiliate_id
            if aid not in affiliate_performance:
                affiliate_performance[aid] = {"commissions": Decimal("0"), "count": 0}
            affiliate_performance[aid]["commissions"] += commission.commission_amount
            affiliate_performance[aid]["count"] += 1
        
        top_affiliates = sorted(
            affiliate_performance.items(),
            key=lambda x: x[1]["commissions"],
            reverse=True
        )[:10]
        
        return {
            "period_days": days,
            "total_commissions": float(total_commissions),
            "total_sales": float(total_sales),
            "commission_rate": float(total_commissions / total_sales * 100) if total_sales else 0,
            "commission_count": len(period_commissions),
            "average_commission": float(total_commissions / len(period_commissions)) if period_commissions else 0,
            "status_distribution": status_dist,
            "active_affiliates": len([a for a in self.affiliates.values() if a.status == AffiliateStatus.ACTIVE]),
            "top_affiliates": [
                {
                    "affiliate_id": aid,
                    "name": self.affiliates.get(aid, {}).name if self.affiliates.get(aid) else "Unknown",
                    "commissions": float(data["commissions"]),
                    "count": data["count"]
                }
                for aid, data in top_affiliates
            ]
        }
    
    def get_affiliate(self, affiliate_id: str) -> Optional[Affiliate]:
        """Get affiliate by ID."""
        return self.affiliates.get(affiliate_id)
    
    def get_affiliate_by_code(self, referral_code: str) -> Optional[Affiliate]:
        """Get affiliate by referral code."""
        for affiliate in self.affiliates.values():
            if affiliate.referral_code == referral_code:
                return affiliate
        return None
    
    def get_commission(self, commission_id: str) -> Optional[Commission]:
        """Get commission by ID."""
        return self.commissions.get(commission_id)
    
    def list_affiliate_commissions(
        self, 
        affiliate_id: str, 
        status: Optional[CommissionStatus] = None
    ) -> List[Commission]:
        """List all commissions for an affiliate."""
        commissions = [
            c for c in self.commissions.values()
            if c.affiliate_id == affiliate_id
        ]
        
        if status:
            commissions = [c for c in commissions if c.status == status]
        
        return sorted(commissions, key=lambda x: x.created_at, reverse=True)
    
    def _generate_referral_code(self, name: str) -> str:
        """Generate unique referral code."""
        base_code = name.upper().replace(" ", "")[:6]
        timestamp = str(int(datetime.utcnow().timestamp()))[-4:]
        return f"{base_code}{timestamp}"
