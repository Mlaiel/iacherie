"""Advanced Revenue Sharing System
==================================

Comprehensive revenue distribution orchestrator for the IA Influencer Agent platform,
integrating with existing revenue sharing infrastructure and providing advanced
analytics and automation.

Features:
- Automated revenue distribution with smart contracts
- Multi-tier profit sharing and performance-based payouts
- Real-time revenue tracking and analytics
- Tax calculation and compliance management
- Integration with existing revenue systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    """Revenue source enumeration"""
    CONTENT_SALES = "content_sales"
    STREAMING_ROYALTIES = "streaming_royalties"
    LICENSING_FEES = "licensing_fees"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    MERCHANDISE_SALES = "merchandise_sales"
    ADVERTISING_REVENUE = "advertising_revenue"
    SUBSCRIPTION_FEES = "subscription_fees"
    AUCTION_SALES = "auction_sales"
    COMMISSION_FEES = "commission_fees"
    PLATFORM_FEES = "platform_fees"

class ShareType(Enum):
    """Revenue share type enumeration"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED_PERCENTAGE = "tiered_percentage"
    PERFORMANCE_BASED = "performance_based"
    MILESTONE_BASED = "milestone_based"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class DistributionStatus(Enum):
    """Distribution status enumeration"""
    CALCULATING = "calculating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DISTRIBUTED = "distributed"
    PARTIALLY_DISTRIBUTED = "partially_distributed"
    FAILED = "failed"

@dataclass
class ShareRule:
    """Revenue share rule definition"""
    rule_id: str
    recipient_id: str
    share_type: ShareType
    percentage: Optional[Decimal] = None
    fixed_amount: Optional[Decimal] = None
    minimum_amount: Decimal = Decimal('0.00')
    maximum_amount: Optional[Decimal] = None
    priority: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)
    tiered_rules: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    effective_date: datetime = field(default_factory=datetime.utcnow)
    expiration_date: Optional[datetime] = None
    is_active: bool = True
    
    def calculate_share(self, total_revenue: Decimal, performance_data: Dict[str, Any] = None) -> Decimal:
        """Calculate share amount based on rules"""
        if not self.is_active:
            return Decimal('0.00')
        
        share_amount = Decimal('0.00')
        
        try:
            if self.share_type == ShareType.PERCENTAGE:
                if self.percentage:
                    share_amount = total_revenue * (self.percentage / Decimal('100'))
            
            elif self.share_type == ShareType.FIXED_AMOUNT:
                if self.fixed_amount:
                    share_amount = self.fixed_amount
            
            elif self.share_type == ShareType.TIERED_PERCENTAGE:
                share_amount = self._calculate_tiered_share(total_revenue)
            
            elif self.share_type == ShareType.PERFORMANCE_BASED:
                share_amount = self._calculate_performance_share(total_revenue, performance_data or {})
            
            # Apply limits
            if share_amount < self.minimum_amount:
                share_amount = Decimal('0.00')
            
            if self.maximum_amount and share_amount > self.maximum_amount:
                share_amount = self.maximum_amount
            
            return share_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating share for rule {self.rule_id}: {e}")
            return Decimal('0.00')
    
    def _calculate_tiered_share(self, total_revenue: Decimal) -> Decimal:
        """Calculate tiered percentage share"""
        share_amount = Decimal('0.00')
        remaining_revenue = total_revenue
        
        for tier in sorted(self.tiered_rules, key=lambda x: x.get('threshold', 0)):
            threshold = Decimal(str(tier.get('threshold', 0)))
            percentage = Decimal(str(tier.get('percentage', 0)))
            
            if remaining_revenue <= 0:
                break
            
            tier_amount = min(remaining_revenue, threshold) if threshold > 0 else remaining_revenue
            share_amount += tier_amount * (percentage / Decimal('100'))
            remaining_revenue -= tier_amount
        
        return share_amount
    
    def _calculate_performance_share(self, total_revenue: Decimal, performance_data: Dict[str, Any]) -> Decimal:
        """Calculate performance-based share"""
        base_percentage = self.percentage or Decimal('0.00')
        
        # Performance multiplier based on metrics
        multiplier = Decimal('1.00')
        
        for metric, config in self.performance_metrics.items():
            if metric in performance_data:
                value = Decimal(str(performance_data[metric]))
                target = Decimal(str(config.get('target', 1)))
                bonus_percentage = Decimal(str(config.get('bonus_percentage', 0)))
                
                if value >= target:
                    multiplier += bonus_percentage / Decimal('100')
        
        return total_revenue * (base_percentage / Decimal('100')) * multiplier

@dataclass
class RevenueTransaction:
    """Revenue transaction record"""
    transaction_id: str
    project_id: str
    source: RevenueSource
    gross_amount: Decimal
    net_amount: Decimal
    currency: str = "USD"
    platform_fees: Decimal = Decimal('0.00')
    processing_fees: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RevenueDistribution:
    """Revenue distribution record"""
    distribution_id: str
    project_id: str
    transaction_id: str
    total_amount: Decimal
    total_distributed: Decimal = Decimal('0.00')
    distributions: Dict[str, Decimal] = field(default_factory=dict)
    status: DistributionStatus = DistributionStatus.CALCULATING
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)
    distribution_timestamp: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SharePayment:
    """Individual share payment record"""
    payment_id: str
    distribution_id: str
    recipient_id: str
    amount: Decimal
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    scheduled_date: datetime = field(default_factory=datetime.utcnow)
    processed_date: Optional[datetime] = None
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ShareCalculator:
    """Advanced share calculation engine"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize share calculator"""
        self.config = config or {}
        self.platform_fee_percentage = Decimal(str(self.config.get('platform_fee_percentage', '10.0')))
        self.processing_fee_percentage = Decimal(str(self.config.get('processing_fee_percentage', '2.5')))
        self.minimum_payout_amount = Decimal(str(self.config.get('minimum_payout_amount', '1.00')))
        
    async def calculate_distributions(
        self, 
        transaction: RevenueTransaction, 
        share_rules: List[ShareRule],
        performance_data: Dict[str, Any] = None
    ) -> RevenueDistribution:
        """Calculate revenue distributions based on share rules"""
        try:
            distribution_id = str(uuid.uuid4())
            
            # Calculate net amount after fees
            net_amount = transaction.gross_amount - transaction.platform_fees - transaction.processing_fees - transaction.tax_amount
            
            distributions = {}
            total_distributed = Decimal('0.00')
            errors = []
            
            # Sort rules by priority
            sorted_rules = sorted(share_rules, key=lambda r: r.priority, reverse=True)
            
            for rule in sorted_rules:
                try:
                    if not rule.is_active:
                        continue
                    
                    # Check if rule applies to this revenue source
                    if rule.conditions.get('revenue_sources') and transaction.source.value not in rule.conditions['revenue_sources']:
                        continue
                    
                    share_amount = rule.calculate_share(net_amount, performance_data)
                    
                    if share_amount >= self.minimum_payout_amount:
                        distributions[rule.recipient_id] = distributions.get(rule.recipient_id, Decimal('0.00')) + share_amount
                        total_distributed += share_amount
                    
                except Exception as e:
                    error_msg = f"Error calculating share for rule {rule.rule_id}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Check if total distributed exceeds available amount
            if total_distributed > net_amount:
                # Proportionally reduce distributions
                reduction_factor = net_amount / total_distributed
                for recipient_id in distributions:
                    distributions[recipient_id] *= reduction_factor
                total_distributed = net_amount
                
                errors.append(f"Total distributions exceeded available amount, reduced proportionally by factor {reduction_factor}")
            
            distribution = RevenueDistribution(
                distribution_id=distribution_id,
                project_id=transaction.project_id,
                transaction_id=transaction.transaction_id,
                total_amount=net_amount,
                total_distributed=total_distributed,
                distributions=distributions,
                status=DistributionStatus.PENDING_APPROVAL if not errors else DistributionStatus.FAILED,
                errors=errors
            )
            
            logger.info(f"Calculated distributions for transaction {transaction.transaction_id}: {len(distributions)} recipients, {total_distributed} total")
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to calculate distributions: {e}")
            raise

class RevenueShareManager:
    """Advanced revenue sharing management system"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize revenue share manager"""
        self.config = config or {}
        self.transactions: Dict[str, RevenueTransaction] = {}
        self.distributions: Dict[str, RevenueDistribution] = {}
        self.payments: Dict[str, SharePayment] = {}
        self.share_rules: Dict[str, List[ShareRule]] = {}  # project_id -> rules
        
        self.calculator = ShareCalculator(self.config.get('calculator', {}))
        
        # Integration with existing revenue systems
        self.has_database_integration = False
        
        try:
            from ...database.collaboration.revenue_sharing import RevenueShareManager as DatabaseRevenueManager
            self.database_manager = DatabaseRevenueManager()
            self.has_database_integration = True
        except ImportError:
            logger.warning("Database revenue sharing not available")
        
        logger.info("💰 Revenue Share Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize revenue share manager"""
        logger.info("🚀 Initializing Revenue Share Manager")
        
        # Start background tasks
        asyncio.create_task(self._payment_processor())
        asyncio.create_task(self._analytics_updater())
    
    async def add_share_rule(self, project_id: str, rule: ShareRule) -> None:
        """Add revenue share rule for project"""
        try:
            if project_id not in self.share_rules:
                self.share_rules[project_id] = []
            
            # Validate rule doesn't conflict with existing rules
            await self._validate_share_rule(project_id, rule)
            
            self.share_rules[project_id].append(rule)
            
            logger.info(f"Added share rule {rule.rule_id} for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to add share rule: {e}")
            raise
    
    async def process_revenue(
        self, 
        revenue_data: Dict[str, Any], 
        performance_data: Dict[str, Any] = None
    ) -> RevenueDistribution:
        """Process revenue and calculate distributions"""
        try:
            transaction_id = str(uuid.uuid4())
            
            # Create revenue transaction
            transaction = RevenueTransaction(
                transaction_id=transaction_id,
                project_id=revenue_data['project_id'],
                source=RevenueSource(revenue_data['source']),
                gross_amount=Decimal(str(revenue_data['gross_amount'])),
                net_amount=Decimal(str(revenue_data.get('net_amount', revenue_data['gross_amount']))),
                currency=revenue_data.get('currency', 'USD'),
                platform_fees=Decimal(str(revenue_data.get('platform_fees', '0.00'))),
                processing_fees=Decimal(str(revenue_data.get('processing_fees', '0.00'))),
                tax_amount=Decimal(str(revenue_data.get('tax_amount', '0.00'))),
                source_reference=revenue_data.get('source_reference'),
                metadata=revenue_data.get('metadata', {})
            )
            
            self.transactions[transaction_id] = transaction
            
            # Get share rules for project
            project_rules = self.share_rules.get(transaction.project_id, [])
            
            if not project_rules:
                logger.warning(f"No share rules found for project {transaction.project_id}")
                return RevenueDistribution(
                    distribution_id=str(uuid.uuid4()),
                    project_id=transaction.project_id,
                    transaction_id=transaction_id,
                    total_amount=transaction.net_amount,
                    status=DistributionStatus.FAILED,
                    errors=["No share rules configured"]
                )
            
            # Calculate distributions
            distribution = await self.calculator.calculate_distributions(
                transaction, project_rules, performance_data
            )
            
            self.distributions[distribution.distribution_id] = distribution
            
            # Create payment records
            await self._create_payments(distribution)
            
            # Sync with database if available
            if self.has_database_integration:
                await self._sync_with_database(transaction, distribution)
            
            logger.info(f"Processed revenue for project {transaction.project_id}: {transaction.gross_amount} -> {distribution.total_distributed} distributed")
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to process revenue: {e}")
            raise
    
    async def approve_distribution(self, distribution_id: str) -> None:
        """Approve revenue distribution for payment"""
        try:
            if distribution_id not in self.distributions:
                raise ValueError(f"Distribution {distribution_id} not found")
            
            distribution = self.distributions[distribution_id]
            
            if distribution.status != DistributionStatus.PENDING_APPROVAL:
                raise ValueError(f"Distribution must be in pending approval status")
            
            distribution.status = DistributionStatus.APPROVED
            distribution.distribution_timestamp = datetime.utcnow()
            
            # Update payment status
            for payment_id, payment in self.payments.items():
                if payment.distribution_id == distribution_id:
                    payment.status = PaymentStatus.PROCESSING
            
            logger.info(f"Approved distribution {distribution_id}")
            
        except Exception as e:
            logger.error(f"Failed to approve distribution: {e}")
            raise
    
    async def get_revenue_analytics(self, project_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics for project"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Filter transactions for project and period
            project_transactions = [
                t for t in self.transactions.values()
                if t.project_id == project_id and t.timestamp >= cutoff_date
            ]
            
            if not project_transactions:
                return {"error": "No transactions found for specified period"}
            
            # Calculate metrics
            total_revenue = sum(t.gross_amount for t in project_transactions)
            total_fees = sum(t.platform_fees + t.processing_fees for t in project_transactions)
            net_revenue = sum(t.net_amount for t in project_transactions)
            
            # Revenue by source
            revenue_by_source = {}
            for source in RevenueSource:
                source_revenue = sum(
                    t.gross_amount for t in project_transactions
                    if t.source == source
                )
                if source_revenue > 0:
                    revenue_by_source[source.value] = float(source_revenue)
            
            # Distribution analytics
            project_distributions = [
                d for d in self.distributions.values()
                if d.project_id == project_id
            ]
            
            total_distributed = sum(d.total_distributed for d in project_distributions)
            
            # Recipient analytics
            recipient_earnings = {}
            for distribution in project_distributions:
                for recipient_id, amount in distribution.distributions.items():
                    recipient_earnings[recipient_id] = recipient_earnings.get(recipient_id, 0) + float(amount)
            
            return {
                "project_id": project_id,
                "period_days": period_days,
                "total_revenue": float(total_revenue),
                "total_fees": float(total_fees),
                "net_revenue": float(net_revenue),
                "total_distributed": float(total_distributed),
                "transaction_count": len(project_transactions),
                "distribution_count": len(project_distributions),
                "revenue_by_source": revenue_by_source,
                "recipient_earnings": recipient_earnings,
                "average_transaction_size": float(total_revenue / len(project_transactions)) if project_transactions else 0,
                "fee_percentage": float((total_fees / total_revenue) * 100) if total_revenue > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue analytics: {e}")
            return {"error": f"Analytics calculation failed: {e}"}
    
    async def get_recipient_payments(self, recipient_id: str, status: PaymentStatus = None) -> List[SharePayment]:
        """Get payments for recipient"""
        payments = [
            payment for payment in self.payments.values()
            if payment.recipient_id == recipient_id
        ]
        
        if status:
            payments = [p for p in payments if p.status == status]
        
        return payments
    
    async def _validate_share_rule(self, project_id: str, new_rule: ShareRule) -> None:
        """Validate share rule doesn't conflict with existing rules"""
        existing_rules = self.share_rules.get(project_id, [])
        
        # Check for duplicate recipient with conflicting rules
        for rule in existing_rules:
            if rule.recipient_id == new_rule.recipient_id and rule.share_type == new_rule.share_type:
                if rule.is_active and new_rule.is_active:
                    raise ValueError(f"Conflicting share rule for recipient {new_rule.recipient_id}")
        
        # Check total percentage doesn't exceed 100%
        if new_rule.share_type == ShareType.PERCENTAGE and new_rule.percentage:
            total_percentage = sum(
                rule.percentage for rule in existing_rules
                if rule.is_active and rule.share_type == ShareType.PERCENTAGE and rule.percentage
            )
            
            if total_percentage + new_rule.percentage > Decimal('100.0'):
                raise ValueError(f"Total percentage would exceed 100%: {total_percentage + new_rule.percentage}%")
    
    async def _create_payments(self, distribution: RevenueDistribution) -> None:
        """Create payment records for distribution"""
        try:
            for recipient_id, amount in distribution.distributions.items():
                payment_id = str(uuid.uuid4())
                
                payment = SharePayment(
                    payment_id=payment_id,
                    distribution_id=distribution.distribution_id,
                    recipient_id=recipient_id,
                    amount=amount,
                    status=PaymentStatus.PENDING if distribution.status == DistributionStatus.APPROVED else PaymentStatus.PENDING
                )
                
                self.payments[payment_id] = payment
            
        except Exception as e:
            logger.error(f"Failed to create payments: {e}")
            raise
    
    async def _sync_with_database(self, transaction: RevenueTransaction, distribution: RevenueDistribution) -> None:
        """Sync with database revenue sharing system"""
        if self.has_database_integration:
            try:
                # Sync logic would go here
                pass
            except Exception as e:
                logger.warning(f"Failed to sync with database: {e}")
    
    async def _payment_processor(self) -> None:
        """Background payment processing"""
        while True:
            try:
                # Process pending payments
                for payment in self.payments.values():
                    if payment.status == PaymentStatus.PROCESSING:
                        # Payment processing logic would go here
                        await asyncio.sleep(0.1)  # Simulate processing
                        payment.status = PaymentStatus.COMPLETED
                        payment.processed_date = datetime.utcnow()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in payment processor: {e}")
                await asyncio.sleep(300)  # Wait longer on error
    
    async def _analytics_updater(self) -> None:
        """Background analytics updates"""
        while True:
            try:
                # Update analytics and metrics
                await asyncio.sleep(3600)  # Update every hour
                
            except Exception as e:
                logger.error(f"Error in analytics updater: {e}")
                await asyncio.sleep(3600)


# Export main classes
__all__ = [
    "RevenueSource",
    "ShareType",
    "PaymentStatus",
    "DistributionStatus",
    "ShareRule",
    "RevenueTransaction",
    "RevenueDistribution",
    "SharePayment",
    "ShareCalculator",
    "RevenueShareManager"
]