"""💰 Revenue Distributor - Automated Revenue Distribution Engine
============================================================

Professional revenue distribution system for licensing:
- Multi-party revenue splitting
- Automated royalty calculations
- Real-time payment processing
- Transparent distribution tracking
- Tax compliance and reporting

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + FinTech Engineer + Business Analyst + Tax Specialist
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class DistributionMethod(Enum):
    """Revenue distribution methods"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    WATERFALL = "waterfall"
    PERFORMANCE_BASED = "performance_based"

class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class RevenueType(Enum):
    """Types of revenue streams"""
    LICENSING_FEE = "licensing_fee"
    ROYALTIES = "royalties"
    STREAMING_REVENUE = "streaming_revenue"
    PERFORMANCE_REVENUE = "performance_revenue"
    SYNC_REVENUE = "sync_revenue"
    MECHANICAL_REVENUE = "mechanical_revenue"
    DIGITAL_SALES = "digital_sales"
    PHYSICAL_SALES = "physical_sales"

@dataclass
class RevenueShare:
    """Individual revenue share definition"""
    participant_id: str
    participant_name: str
    share_percentage: float
    minimum_amount: Optional[Decimal]
    maximum_amount: Optional[Decimal]
    payment_method: str
    payment_details: Dict[str, Any]
    tax_jurisdiction: str

@dataclass
class DistributionRecord:
    """Revenue distribution record"""
    distribution_id: str
    license_id: str
    total_revenue: Decimal
    currency: str
    distribution_date: datetime
    revenue_period_start: datetime
    revenue_period_end: datetime
    shares: List[RevenueShare]
    payment_statuses: Dict[str, PaymentStatus]
    fees_deducted: Decimal
    net_distributed: Decimal

@dataclass
class PaymentTransaction:
    """Individual payment transaction"""
    transaction_id: str
    participant_id: str
    amount: Decimal
    currency: str
    payment_method: str
    status: PaymentStatus
    initiated_at: datetime
    completed_at: Optional[datetime]
    failure_reason: Optional[str]
    external_reference: Optional[str]

class RevenueDistributor:
    """
    🚀 Professional revenue distribution engine
    
    Advanced system for automated revenue splitting and distribution
    with multi-party support and regulatory compliance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize revenue distributor with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize payment processors
        self.payment_processors = {}
        self.supported_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'JPY']
        
        # Initialize tax calculators
        self.tax_calculators = {}
        
        # Distribution tracking
        self.active_distributions = {}
        self.distribution_history = []
        
        # Performance metrics
        self.metrics = {
            'total_distributions': 0,
            'total_revenue_distributed': Decimal('0.00'),
            'successful_payments': 0,
            'failed_payments': 0,
            'average_distribution_time': 0.0
        }
        
        self._initialize_payment_processors()
        self._initialize_tax_calculators()
    
    def _initialize_payment_processors(self):
        """Initialize payment processing integrations."""
        try:
            # Stripe integration
            if self.config.get('stripe_enabled', False):
                from .integrations.stripe_processor import StripeProcessor
                self.payment_processors['stripe'] = StripeProcessor(
                    self.config.get('stripe_config', {})
                )
            
            # PayPal integration
            if self.config.get('paypal_enabled', False):
                from .integrations.paypal_processor import PayPalProcessor
                self.payment_processors['paypal'] = PayPalProcessor(
                    self.config.get('paypal_config', {})
                )
            
            # Wise (formerly TransferWise) integration
            if self.config.get('wise_enabled', False):
                from .integrations.wise_processor import WiseProcessor
                self.payment_processors['wise'] = WiseProcessor(
                    self.config.get('wise_config', {})
                )
            
            # Bank transfer integration
            if self.config.get('bank_transfer_enabled', False):
                from .integrations.bank_processor import BankProcessor
                self.payment_processors['bank_transfer'] = BankProcessor(
                    self.config.get('bank_config', {})
                )
            
            self.logger.info(f"Initialized {len(self.payment_processors)} payment processors")
            
        except ImportError as e:
            self.logger.warning(f"Some payment processors not available: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize payment processors: {e}")
            raise
    
    def _initialize_tax_calculators(self):
        """Initialize tax calculation engines."""
        tax_calculators = {
            'us': {
                'federal_tax_rate': 0.21,
                'state_tax_rates': {
                    'CA': 0.088,
                    'NY': 0.063,
                    'TX': 0.00,
                    'FL': 0.00
                },
                'withholding_requirements': True
            },
            'eu': {
                'vat_rates': {
                    'germany': 0.19,
                    'france': 0.20,
                    'italy': 0.22,
                    'spain': 0.21
                },
                'royalty_withholding': 0.05
            },
            'germany': {
                'income_tax_rate': 0.42,
                'solidarity_surcharge': 0.055,
                'church_tax_rate': 0.08,
                'artist_social_insurance': 0.056
            },
            'uk': {
                'corporation_tax': 0.19,
                'vat_rate': 0.20,
                'royalty_withholding': 0.20
            }
        }
        
        self.tax_calculators = tax_calculators
        self.logger.info(f"Initialized tax calculators for {len(tax_calculators)} jurisdictions")
    
    async def process_final_distribution(
        self,
        license_id: str,
        termination_date: datetime
    ) -> Dict[str, Any]:
        """Process final revenue distribution upon license termination."""
        try:
            self.logger.info(f"Processing final distribution for license: {license_id}")
            
            # Calculate final revenue period
            final_period_end = termination_date
            last_distribution = await self._get_last_distribution_date(license_id)
            final_period_start = last_distribution or (termination_date - timedelta(days=90))
            
            # Get final revenue data
            final_revenue = await self._calculate_final_revenue(
                license_id=license_id,
                period_start=final_period_start,
                period_end=final_period_end
            )
            
            if final_revenue <= 0:
                return {
                    'distribution_id': None,
                    'total_revenue': 0,
                    'message': 'No revenue to distribute for final period'
                }
            
            # Process distribution
            distribution_result = await self.distribute_revenue(
                license_id=license_id,
                total_revenue=final_revenue,
                revenue_period_start=final_period_start,
                revenue_period_end=final_period_end,
                is_final_distribution=True
            )
            
            return distribution_result
            
        except Exception as e:
            self.logger.error(f"Failed to process final distribution: {e}")
            raise
    
    async def distribute_revenue(
        self,
        license_id: str,
        total_revenue: Decimal,
        revenue_period_start: datetime,
        revenue_period_end: datetime,
        currency: str = 'USD',
        is_final_distribution: bool = False
    ) -> Dict[str, Any]:
        """
        💰 Distribute revenue among license participants
        
        Args:
            license_id: License identifier
            total_revenue: Total revenue to distribute
            revenue_period_start: Start date of revenue period
            revenue_period_end: End date of revenue period
            currency: Revenue currency
            is_final_distribution: Whether this is the final distribution
            
        Returns:
            distribution_result: Distribution processing result
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Distributing revenue for license {license_id}: {total_revenue} {currency}")
            
            # Get license revenue sharing configuration
            revenue_shares = await self._get_license_revenue_shares(license_id)
            
            if not revenue_shares:
                raise ValueError(f"No revenue sharing configuration found for license {license_id}")
            
            # Validate total revenue shares
            total_percentage = sum(share.share_percentage for share in revenue_shares)
            if abs(total_percentage - 100.0) > 0.01:
                raise ValueError(f"Revenue shares total {total_percentage}%, must equal 100%")
            
            # Calculate platform fees
            platform_fee_rate = self.config.get('platform_fee_rate', 0.05)
            platform_fee = total_revenue * Decimal(str(platform_fee_rate))
            distributable_revenue = total_revenue - platform_fee
            
            # Calculate individual distributions
            distribution_id = str(uuid.uuid4())
            payment_transactions = []
            
            for share in revenue_shares:
                # Calculate share amount
                share_amount = distributable_revenue * Decimal(str(share.share_percentage / 100))
                
                # Apply minimum/maximum constraints
                if share.minimum_amount and share_amount < share.minimum_amount:
                    share_amount = share.minimum_amount
                elif share.maximum_amount and share_amount > share.maximum_amount:
                    share_amount = share.maximum_amount
                
                # Calculate taxes
                net_amount = await self._calculate_net_amount(
                    gross_amount=share_amount,
                    participant_id=share.participant_id,
                    tax_jurisdiction=share.tax_jurisdiction
                )
                
                # Create payment transaction
                transaction = await self._create_payment_transaction(
                    distribution_id=distribution_id,
                    participant=share,
                    amount=net_amount,
                    currency=currency
                )
                
                payment_transactions.append(transaction)
            
            # Create distribution record
            distribution_record = DistributionRecord(
                distribution_id=distribution_id,
                license_id=license_id,
                total_revenue=total_revenue,
                currency=currency,
                distribution_date=datetime.now(),
                revenue_period_start=revenue_period_start,
                revenue_period_end=revenue_period_end,
                shares=revenue_shares,
                payment_statuses={t.participant_id: t.status for t in payment_transactions},
                fees_deducted=platform_fee,
                net_distributed=sum(t.amount for t in payment_transactions)
            )
            
            # Store distribution record
            self.active_distributions[distribution_id] = distribution_record
            
            # Process payments asynchronously
            payment_tasks = []
            for transaction in payment_transactions:
                task = asyncio.create_task(
                    self._process_payment_transaction(transaction)
                )
                payment_tasks.append(task)
            
            # Wait for all payments to complete
            payment_results = await asyncio.gather(*payment_tasks, return_exceptions=True)
            
            # Update distribution record with final payment statuses
            successful_payments = 0
            failed_payments = 0
            
            for i, result in enumerate(payment_results):
                transaction = payment_transactions[i]
                if isinstance(result, Exception):
                    transaction.status = PaymentStatus.FAILED
                    transaction.failure_reason = str(result)
                    failed_payments += 1
                else:
                    transaction.status = PaymentStatus.COMPLETED
                    transaction.completed_at = datetime.now()
                    successful_payments += 1
                
                distribution_record.payment_statuses[transaction.participant_id] = transaction.status
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['total_distributions'] += 1
            self.metrics['total_revenue_distributed'] += total_revenue
            self.metrics['successful_payments'] += successful_payments
            self.metrics['failed_payments'] += failed_payments
            self.metrics['average_distribution_time'] = (
                (self.metrics['average_distribution_time'] * (self.metrics['total_distributions'] - 1) + processing_time)
                / self.metrics['total_distributions']
            )
            
            # Move to history if all payments processed
            if successful_payments + failed_payments == len(payment_transactions):
                self.distribution_history.append(distribution_record)
                del self.active_distributions[distribution_id]
            
            return {
                'distribution_id': distribution_id,
                'total_revenue': float(total_revenue),
                'fees_deducted': float(platform_fee),
                'net_distributed': float(distribution_record.net_distributed),
                'successful_payments': successful_payments,
                'failed_payments': failed_payments,
                'payment_transactions': [asdict(t) for t in payment_transactions],
                'processing_time_seconds': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to distribute revenue: {e}")
            raise
    
    async def _get_license_revenue_shares(self, license_id: str) -> List[RevenueShare]:
        """Get revenue sharing configuration for a license."""
        # This would typically fetch from a database
        # For now, return a default configuration
        return [
            RevenueShare(
                participant_id="creator_001",
                participant_name="Primary Creator",
                share_percentage=70.0,
                minimum_amount=Decimal('10.00'),
                maximum_amount=None,
                payment_method="stripe",
                payment_details={"account_id": "acct_creator_001"},
                tax_jurisdiction="us"
            ),
            RevenueShare(
                participant_id="label_001",
                participant_name="Record Label",
                share_percentage=20.0,
                minimum_amount=Decimal('5.00'),
                maximum_amount=None,
                payment_method="bank_transfer",
                payment_details={"account_number": "1234567890", "routing_number": "987654321"},
                tax_jurisdiction="us"
            ),
            RevenueShare(
                participant_id="manager_001",
                participant_name="Artist Manager",
                share_percentage=10.0,
                minimum_amount=Decimal('2.50'),
                maximum_amount=Decimal('1000.00'),
                payment_method="paypal",
                payment_details={"email": "manager@example.com"},
                tax_jurisdiction="us"
            )
        ]
    
    async def _calculate_net_amount(
        self,
        gross_amount: Decimal,
        participant_id: str,
        tax_jurisdiction: str
    ) -> Decimal:
        """Calculate net amount after taxes and withholdings."""
        tax_config = self.tax_calculators.get(tax_jurisdiction, {})
        
        # Calculate applicable taxes
        total_tax_rate = Decimal('0.00')
        
        if tax_jurisdiction == 'us':
            # Federal tax
            total_tax_rate += Decimal(str(tax_config.get('federal_tax_rate', 0)))
            
            # State tax (would need participant's state)
            state_tax_rates = tax_config.get('state_tax_rates', {})
            # Default to California rate for example
            total_tax_rate += Decimal(str(state_tax_rates.get('CA', 0)))
        
        elif tax_jurisdiction == 'germany':
            # Income tax
            total_tax_rate += Decimal(str(tax_config.get('income_tax_rate', 0)))
            
            # Artist social insurance
            total_tax_rate += Decimal(str(tax_config.get('artist_social_insurance', 0)))
        
        elif tax_jurisdiction in ['eu']:
            # Royalty withholding
            total_tax_rate += Decimal(str(tax_config.get('royalty_withholding', 0)))
        
        # Calculate net amount
        tax_amount = gross_amount * total_tax_rate
        net_amount = gross_amount - tax_amount
        
        return net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _create_payment_transaction(
        self,
        distribution_id: str,
        participant: RevenueShare,
        amount: Decimal,
        currency: str
    ) -> PaymentTransaction:
        """Create a payment transaction record."""
        return PaymentTransaction(
            transaction_id=str(uuid.uuid4()),
            participant_id=participant.participant_id,
            amount=amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            currency=currency,
            payment_method=participant.payment_method,
            status=PaymentStatus.PENDING,
            initiated_at=datetime.now(),
            completed_at=None,
            failure_reason=None,
            external_reference=None
        )
    
    async def _process_payment_transaction(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Process individual payment transaction."""
        try:
            self.logger.info(f"Processing payment transaction: {transaction.transaction_id}")
            
            # Get appropriate payment processor
            processor = self.payment_processors.get(transaction.payment_method)
            if not processor:
                raise ValueError(f"Payment processor not available: {transaction.payment_method}")
            
            # Update status to processing
            transaction.status = PaymentStatus.PROCESSING
            
            # Process payment through external processor
            payment_result = await processor.process_payment(
                amount=float(transaction.amount),
                currency=transaction.currency,
                recipient_details=transaction.participant_id,  # Would include actual payment details
                reference=transaction.transaction_id
            )
            
            # Update transaction with result
            transaction.external_reference = payment_result.get('external_id')
            
            if payment_result.get('success', False):
                transaction.status = PaymentStatus.COMPLETED
                transaction.completed_at = datetime.now()
            else:
                transaction.status = PaymentStatus.FAILED
                transaction.failure_reason = payment_result.get('error_message')
            
            return payment_result
            
        except Exception as e:
            self.logger.error(f"Failed to process payment transaction {transaction.transaction_id}: {e}")
            transaction.status = PaymentStatus.FAILED
            transaction.failure_reason = str(e)
            raise
    
    async def _get_last_distribution_date(self, license_id: str) -> Optional[datetime]:
        """Get the date of the last revenue distribution for a license."""
        # This would typically query a database
        # For now, return None to indicate no previous distributions
        return None
    
    async def _calculate_final_revenue(
        self,
        license_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Decimal:
        """Calculate final revenue for a license period."""
        # This would typically aggregate revenue from various sources
        # For now, return a sample amount
        return Decimal('500.00')
    
    def get_distribution_status(self) -> Dict[str, Any]:
        """Get revenue distribution status and metrics."""
        return {
            **{k: float(v) if isinstance(v, Decimal) else v for k, v in self.metrics.items()},
            'active_distributions': len(self.active_distributions),
            'completed_distributions': len(self.distribution_history),
            'supported_payment_methods': list(self.payment_processors.keys()),
            'supported_currencies': self.supported_currencies,
            'timestamp': datetime.now().isoformat()
        }
    
    async def get_distribution_history(
        self,
        license_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get distribution history for a license or all licenses."""
        history = self.distribution_history
        
        if license_id:
            history = [d for d in history if d.license_id == license_id]
        
        # Sort by distribution date, most recent first
        history.sort(key=lambda x: x.distribution_date, reverse=True)
        
        # Apply limit
        history = history[:limit]
        
        # Convert to dict format
        return [asdict(record) for record in history]
