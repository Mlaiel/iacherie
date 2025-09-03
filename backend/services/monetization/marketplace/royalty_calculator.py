"""Royalty Calculator - Advanced Royalty Distribution Engine
=========================================================

Sophisticated royalty calculation and distribution system with
multi-stakeholder support, automated splits, and compliance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class StakeholderType(str, Enum):
    """Types of royalty stakeholders."""
    CREATOR = "creator"
    PRODUCER = "producer"
    PUBLISHER = "publisher"
    DISTRIBUTOR = "distributor"
    PLATFORM = "platform"
    INVESTOR = "investor"
    COLLABORATOR = "collaborator"
    AGENT = "agent"


class RoyaltyType(str, Enum):
    """Types of royalty payments."""
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    DIGITAL = "digital"
    PRINT = "print"
    STREAMING = "streaming"
    SALES = "sales"
    LICENSING = "licensing"


class PaymentStatus(str, Enum):
    """Royalty payment status."""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


@dataclass
class Stakeholder:
    """Royalty stakeholder information."""
    id: str
    name: str
    type: StakeholderType
    email: str
    payment_info: Dict[str, Any]
    tax_info: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoyaltySplit:
    """Royalty split configuration."""
    stakeholder_id: str
    percentage: Decimal
    minimum_amount: Decimal = Decimal("0.01")
    royalty_types: List[RoyaltyType] = field(default_factory=lambda: list(RoyaltyType))
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoyaltyRevenue:
    """Revenue source for royalty calculation."""
    id: str
    content_id: str
    revenue_type: RoyaltyType
    gross_amount: Decimal
    net_amount: Decimal
    platform: str
    territory: str
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoyaltyCalculation:
    """Royalty calculation result."""
    id: str
    content_id: str
    revenue_id: str
    period_start: datetime
    period_end: datetime
    gross_revenue: Decimal
    total_royalties: Decimal
    platform_fee: Decimal
    splits: List[Dict[str, Any]]
    status: PaymentStatus = PaymentStatus.CALCULATED
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoyaltyPayment:
    """Individual royalty payment."""
    id: str
    calculation_id: str
    stakeholder_id: str
    amount: Decimal
    royalty_type: RoyaltyType
    status: PaymentStatus
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None


class RoyaltyCalculator:
    """Advanced royalty calculation and distribution engine."""
    
    def __init__(self):
        """Initialize royalty calculator."""
        self.stakeholders: Dict[str, Stakeholder] = {}
        self.content_splits: Dict[str, List[RoyaltySplit]] = {}
        self.revenue_records: Dict[str, RoyaltyRevenue] = {}
        self.calculations: Dict[str, RoyaltyCalculation] = {}
        self.payments: Dict[str, RoyaltyPayment] = {}
        
        # Default platform fee (percentage)
        self.platform_fee_rate = Decimal("0.15")  # 15%
        
        # Minimum payment threshold
        self.minimum_payment_threshold = Decimal("1.00")
        
        logger.info("Royalty calculator initialized")
    
    async def register_stakeholder(
        self,
        name: str,
        stakeholder_type: StakeholderType,
        email: str,
        payment_info: Dict[str, Any],
        tax_info: Optional[Dict[str, Any]] = None
    ) -> Stakeholder:
        """Register a new royalty stakeholder.
        
        Args:
            name: Stakeholder name
            stakeholder_type: Type of stakeholder
            email: Contact email
            payment_info: Payment information
            tax_info: Tax information
            
        Returns:
            Registered stakeholder
        """
        try:
            stakeholder_id = str(uuid.uuid4())
            
            stakeholder = Stakeholder(
                id=stakeholder_id,
                name=name,
                type=stakeholder_type,
                email=email,
                payment_info=payment_info,
                tax_info=tax_info or {}
            )
            
            self.stakeholders[stakeholder_id] = stakeholder
            
            logger.info(f"Stakeholder registered: {stakeholder_id} ({name})")
            return stakeholder
            
        except Exception as e:
            logger.error(f"Failed to register stakeholder: {e}")
            raise
    
    async def configure_content_splits(
        self,
        content_id: str,
        splits: List[RoyaltySplit]
    ) -> bool:
        """Configure royalty splits for content.
        
        Args:
            content_id: Content identifier
            splits: List of royalty splits
            
        Returns:
            True if configured successfully
        """
        try:
            # Validate splits total 100%
            total_percentage = sum(split.percentage for split in splits)
            if total_percentage != Decimal("100.0"):
                raise ValueError(f"Splits must total 100%, got {total_percentage}%")
            
            # Validate stakeholders exist
            for split in splits:
                if split.stakeholder_id not in self.stakeholders:
                    raise ValueError(f"Unknown stakeholder: {split.stakeholder_id}")
            
            self.content_splits[content_id] = splits
            
            logger.info(f"Royalty splits configured for content: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure splits: {e}")
            return False
    
    async def record_revenue(
        self,
        content_id: str,
        revenue_type: RoyaltyType,
        gross_amount: Decimal,
        platform: str,
        territory: str = "worldwide",
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RoyaltyRevenue:
        """Record revenue for royalty calculation.
        
        Args:
            content_id: Content identifier
            revenue_type: Type of revenue
            gross_amount: Gross revenue amount
            platform: Platform name
            territory: Territory/region
            period_start: Revenue period start
            period_end: Revenue period end
            metadata: Additional metadata
            
        Returns:
            Recorded revenue
        """
        try:
            revenue_id = str(uuid.uuid4())
            
            # Default period to last month if not specified
            if not period_end:
                period_end = datetime.now()
            if not period_start:
                period_start = period_end - timedelta(days=30)
            
            # Calculate net amount (after platform fees)
            platform_fee = gross_amount * self.platform_fee_rate
            net_amount = gross_amount - platform_fee
            
            revenue = RoyaltyRevenue(
                id=revenue_id,
                content_id=content_id,
                revenue_type=revenue_type,
                gross_amount=gross_amount,
                net_amount=net_amount,
                platform=platform,
                territory=territory,
                period_start=period_start,
                period_end=period_end,
                metadata=metadata or {}
            )
            
            self.revenue_records[revenue_id] = revenue
            
            # Automatically trigger royalty calculation
            calculation = await self.calculate_royalties(revenue_id)
            
            logger.info(f"Revenue recorded: {revenue_id} - ${gross_amount}")
            return revenue
            
        except Exception as e:
            logger.error(f"Failed to record revenue: {e}")
            raise
    
    async def calculate_royalties(self, revenue_id: str) -> RoyaltyCalculation:
        """Calculate royalties for recorded revenue.
        
        Args:
            revenue_id: Revenue record identifier
            
        Returns:
            Royalty calculation
        """
        try:
            if revenue_id not in self.revenue_records:
                raise ValueError(f"Revenue record not found: {revenue_id}")
            
            revenue = self.revenue_records[revenue_id]
            content_id = revenue.content_id
            
            if content_id not in self.content_splits:
                raise ValueError(f"No royalty splits configured for content: {content_id}")
            
            calculation_id = str(uuid.uuid4())
            splits = self.content_splits[content_id]
            
            # Calculate platform fee
            platform_fee = revenue.gross_amount * self.platform_fee_rate
            distributable_amount = revenue.net_amount
            
            split_results = []
            total_distributed = Decimal("0")
            
            for split in splits:
                # Check if this split applies to this revenue type
                if revenue.revenue_type not in split.royalty_types:
                    continue
                
                # Calculate split amount
                split_amount = (distributable_amount * split.percentage / Decimal("100")).quantize(
                    Decimal("0.01"), rounding=ROUND_DOWN
                )
                
                # Apply minimum amount check
                if split_amount < split.minimum_amount:
                    logger.info(f"Split amount ${split_amount} below minimum ${split.minimum_amount}")
                    continue
                
                # Check split conditions
                if not await self._check_split_conditions(split, revenue):
                    continue
                
                stakeholder = self.stakeholders[split.stakeholder_id]
                
                split_result = {
                    "stakeholder_id": split.stakeholder_id,
                    "stakeholder_name": stakeholder.name,
                    "stakeholder_type": stakeholder.type.value,
                    "percentage": float(split.percentage),
                    "amount": split_amount,
                    "royalty_type": revenue.revenue_type.value
                }
                
                split_results.append(split_result)
                total_distributed += split_amount
            
            calculation = RoyaltyCalculation(
                id=calculation_id,
                content_id=content_id,
                revenue_id=revenue_id,
                period_start=revenue.period_start,
                period_end=revenue.period_end,
                gross_revenue=revenue.gross_amount,
                total_royalties=total_distributed,
                platform_fee=platform_fee,
                splits=split_results
            )
            
            self.calculations[calculation_id] = calculation
            
            # Create individual payment records
            await self._create_payment_records(calculation)
            
            logger.info(f"Royalties calculated: {calculation_id} - ${total_distributed} distributed")
            return calculation
            
        except Exception as e:
            logger.error(f"Failed to calculate royalties: {e}")
            raise
    
    async def _check_split_conditions(
        self,
        split: RoyaltySplit,
        revenue: RoyaltyRevenue
    ) -> bool:
        """Check if split conditions are met.
        
        Args:
            split: Royalty split configuration
            revenue: Revenue record
            
        Returns:
            True if conditions are met
        """
        try:
            if not split.conditions:
                return True
            
            # Check territory conditions
            if "territories" in split.conditions:
                allowed_territories = split.conditions["territories"]
                if revenue.territory not in allowed_territories:
                    return False
            
            # Check platform conditions
            if "platforms" in split.conditions:
                allowed_platforms = split.conditions["platforms"]
                if revenue.platform not in allowed_platforms:
                    return False
            
            # Check minimum revenue conditions
            if "minimum_revenue" in split.conditions:
                minimum = Decimal(str(split.conditions["minimum_revenue"]))
                if revenue.gross_amount < minimum:
                    return False
            
            # Check date range conditions
            if "valid_from" in split.conditions:
                valid_from = datetime.fromisoformat(split.conditions["valid_from"])
                if revenue.period_start < valid_from:
                    return False
            
            if "valid_to" in split.conditions:
                valid_to = datetime.fromisoformat(split.conditions["valid_to"])
                if revenue.period_end > valid_to:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check split conditions: {e}")
            return False
    
    async def _create_payment_records(self, calculation: RoyaltyCalculation) -> None:
        """Create individual payment records from calculation.
        
        Args:
            calculation: Royalty calculation
        """
        try:
            for split in calculation.splits:
                payment_id = str(uuid.uuid4())
                
                payment = RoyaltyPayment(
                    id=payment_id,
                    calculation_id=calculation.id,
                    stakeholder_id=split["stakeholder_id"],
                    amount=split["amount"],
                    royalty_type=RoyaltyType(split["royalty_type"]),
                    status=PaymentStatus.PENDING,
                    payment_method="bank_transfer"  # Default payment method
                )
                
                self.payments[payment_id] = payment
            
            logger.info(f"Created {len(calculation.splits)} payment records")
            
        except Exception as e:
            logger.error(f"Failed to create payment records: {e}")
    
    async def process_payments(
        self,
        calculation_id: str,
        payment_processor_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Process royalty payments for a calculation.
        
        Args:
            calculation_id: Calculation identifier
            payment_processor_callback: Optional payment processor function
            
        Returns:
            Payment processing results
        """
        try:
            if calculation_id not in self.calculations:
                raise ValueError(f"Calculation not found: {calculation_id}")
            
            # Get payments for this calculation
            payments = [
                payment for payment in self.payments.values()
                if payment.calculation_id == calculation_id and payment.status == PaymentStatus.PENDING
            ]
            
            if not payments:
                return {"status": "no_payments", "message": "No pending payments found"}
            
            # Filter payments above minimum threshold
            eligible_payments = [
                payment for payment in payments
                if payment.amount >= self.minimum_payment_threshold
            ]
            
            if not eligible_payments:
                return {"status": "below_threshold", "message": "All payments below minimum threshold"}
            
            results = {
                "successful": 0,
                "failed": 0,
                "total_amount": Decimal("0"),
                "payments": []
            }
            
            for payment in eligible_payments:
                try:
                    # Use provided payment processor or simulate payment
                    if payment_processor_callback:
                        success = await payment_processor_callback(payment)
                    else:
                        success = await self._simulate_payment(payment)
                    
                    if success:
                        payment.status = PaymentStatus.PAID
                        payment.paid_at = datetime.now()
                        payment.transaction_id = f"tx_{uuid.uuid4().hex[:8]}"
                        
                        results["successful"] += 1
                        results["total_amount"] += payment.amount
                    else:
                        payment.status = PaymentStatus.FAILED
                        results["failed"] += 1
                    
                    results["payments"].append({
                        "payment_id": payment.id,
                        "stakeholder_id": payment.stakeholder_id,
                        "amount": payment.amount,
                        "status": payment.status.value
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to process payment {payment.id}: {e}")
                    payment.status = PaymentStatus.FAILED
                    results["failed"] += 1
            
            # Update calculation status
            calculation = self.calculations[calculation_id]
            if results["failed"] == 0:
                calculation.status = PaymentStatus.PAID
            elif results["successful"] > 0:
                calculation.status = PaymentStatus.APPROVED  # Partial success
            
            logger.info(f"Processed payments for calculation {calculation_id}: {results['successful']} successful, {results['failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to process payments: {e}")
            raise
    
    async def _simulate_payment(self, payment: RoyaltyPayment) -> bool:
        """Simulate payment processing.
        
        Args:
            payment: Payment to process
            
        Returns:
            True if payment successful
        """
        try:
            # Simulate payment delay
            await asyncio.sleep(0.1)
            
            # 95% success rate for simulation
            import random
            return random.random() > 0.05
            
        except Exception as e:
            logger.error(f"Payment simulation failed: {e}")
            return False
    
    async def get_stakeholder_earnings(
        self,
        stakeholder_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get earnings summary for a stakeholder.
        
        Args:
            stakeholder_id: Stakeholder identifier
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Earnings summary
        """
        try:
            if stakeholder_id not in self.stakeholders:
                raise ValueError(f"Stakeholder not found: {stakeholder_id}")
            
            # Filter payments by date range
            stakeholder_payments = [
                payment for payment in self.payments.values()
                if payment.stakeholder_id == stakeholder_id
            ]
            
            if start_date or end_date:
                filtered_payments = []
                for payment in stakeholder_payments:
                    if start_date and payment.created_at < start_date:
                        continue
                    if end_date and payment.created_at > end_date:
                        continue
                    filtered_payments.append(payment)
                stakeholder_payments = filtered_payments
            
            # Calculate totals
            total_earned = sum(
                payment.amount for payment in stakeholder_payments
                if payment.status == PaymentStatus.PAID
            )
            
            pending_amount = sum(
                payment.amount for payment in stakeholder_payments
                if payment.status == PaymentStatus.PENDING
            )
            
            payment_count = len(stakeholder_payments)
            
            # Group by royalty type
            by_royalty_type = {}
            for payment in stakeholder_payments:
                royalty_type = payment.royalty_type.value
                if royalty_type not in by_royalty_type:
                    by_royalty_type[royalty_type] = {
                        "total": Decimal("0"),
                        "count": 0
                    }
                by_royalty_type[royalty_type]["total"] += payment.amount
                by_royalty_type[royalty_type]["count"] += 1
            
            stakeholder = self.stakeholders[stakeholder_id]
            
            return {
                "stakeholder_id": stakeholder_id,
                "stakeholder_name": stakeholder.name,
                "stakeholder_type": stakeholder.type.value,
                "total_earned": total_earned,
                "pending_amount": pending_amount,
                "payment_count": payment_count,
                "by_royalty_type": by_royalty_type,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get stakeholder earnings: {e}")
            return {}
    
    async def get_content_royalty_summary(self, content_id: str) -> Dict[str, Any]:
        """Get royalty summary for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Royalty summary
        """
        try:
            # Get calculations for this content
            content_calculations = [
                calc for calc in self.calculations.values()
                if calc.content_id == content_id
            ]
            
            if not content_calculations:
                return {"content_id": content_id, "total_revenue": Decimal("0"), "calculations": []}
            
            total_revenue = sum(calc.gross_revenue for calc in content_calculations)
            total_royalties = sum(calc.total_royalties for calc in content_calculations)
            total_platform_fees = sum(calc.platform_fee for calc in content_calculations)
            
            return {
                "content_id": content_id,
                "total_revenue": total_revenue,
                "total_royalties": total_royalties,
                "total_platform_fees": total_platform_fees,
                "calculation_count": len(content_calculations),
                "calculations": [
                    {
                        "id": calc.id,
                        "period": f"{calc.period_start.date()} to {calc.period_end.date()}",
                        "revenue": calc.gross_revenue,
                        "royalties": calc.total_royalties,
                        "status": calc.status.value
                    }
                    for calc in content_calculations
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get content royalty summary: {e}")
            return {}
    
    async def get_calculation(self, calculation_id: str) -> Optional[RoyaltyCalculation]:
        """Get royalty calculation by ID.
        
        Args:
            calculation_id: Calculation identifier
            
        Returns:
            Royalty calculation if found
        """
        return self.calculations.get(calculation_id)
    
    async def get_payment(self, payment_id: str) -> Optional[RoyaltyPayment]:
        """Get royalty payment by ID.
        
        Args:
            payment_id: Payment identifier
            
        Returns:
            Royalty payment if found
        """
        return self.payments.get(payment_id)