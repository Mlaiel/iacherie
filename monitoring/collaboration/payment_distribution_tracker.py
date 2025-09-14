"""
Ainflue Platform - Payment Distribution Tracker
===============================================

Enterprise-grade payment distribution tracking for collaboration partnerships,
automated payment routing, revenue split management, and financial transparency.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment distribution status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    ON_HOLD = "on_hold"

class PaymentMethod(Enum):
    """Payment methods."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTOCURRENCY = "cryptocurrency"
    WISE = "wise"
    DIGITAL_WALLET = "digital_wallet"
    CHECK = "check"

class CurrencyType(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    BTC = "BTC"
    ETH = "ETH"

class RevenueSource(Enum):
    """Sources of revenue."""
    STREAMING_ROYALTIES = "streaming_royalties"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    MERCHANDISE_SALES = "merchandise_sales"
    LIVE_PERFORMANCES = "live_performances"
    LICENSING_DEALS = "licensing_deals"
    COLLABORATION_FEES = "collaboration_fees"
    SPONSORSHIP_REVENUE = "sponsorship_revenue"
    CONTENT_MONETIZATION = "content_monetization"

@dataclass
class PaymentRecipient:
    """Payment recipient information."""
    recipient_id: str
    creator_id: str
    name: str
    email: str
    payment_methods: Dict[PaymentMethod, Dict[str, Any]]
    tax_information: Dict[str, Any] = field(default_factory=dict)
    verification_status: str = "pending"
    preferred_payment_method: Optional[PaymentMethod] = None
    minimum_payment_threshold: Decimal = Decimal('25.00')
    payment_schedule: str = "monthly"  # weekly, monthly, quarterly

@dataclass
class RevenueStream:
    """Individual revenue stream."""
    stream_id: str
    collaboration_id: str
    source: RevenueSource
    total_revenue: Decimal
    currency: CurrencyType
    generated_date: datetime
    reporting_period: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False

@dataclass
class PaymentDistribution:
    """Payment distribution record."""
    distribution_id: str
    collaboration_id: str
    revenue_stream_id: str
    total_amount: Decimal
    currency: CurrencyType
    distribution_rules: Dict[str, Any]
    recipient_payments: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    status: PaymentStatus = PaymentStatus.PENDING
    fees: Dict[str, Decimal] = field(default_factory=dict)
    net_amount: Optional[Decimal] = None

@dataclass
class PaymentTransaction:
    """Individual payment transaction."""
    transaction_id: str
    distribution_id: str
    recipient_id: str
    amount: Decimal
    currency: CurrencyType
    payment_method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    processed_at: Optional[datetime] = None
    confirmation_code: Optional[str] = None
    fees: Decimal = Decimal('0.00')
    net_amount: Optional[Decimal] = None
    retry_count: int = 0
    error_message: Optional[str] = None

class PaymentDistributionTracker:
    """
    Advanced payment distribution tracking system for collaboration partnerships.
    
    Features:
    - Automated revenue split calculations
    - Multi-currency payment processing
    - Real-time payment tracking
    - Fee management and optimization
    - Tax compliance handling
    - Payment method routing
    - Failed payment retry logic
    - Financial reporting and analytics
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize payment distribution tracker."""
        self.config = config or {}
        self.recipients: Dict[str, PaymentRecipient] = {}
        self.revenue_streams: Dict[str, RevenueStream] = {}
        self.distributions: Dict[str, PaymentDistribution] = {}
        self.transactions: Dict[str, PaymentTransaction] = {}
        
        # Payment processor configurations
        self.payment_processors = {
            PaymentMethod.STRIPE: {"fee_rate": Decimal('0.029'), "fixed_fee": Decimal('0.30')},
            PaymentMethod.PAYPAL: {"fee_rate": Decimal('0.034'), "fixed_fee": Decimal('0.35')},
            PaymentMethod.WISE: {"fee_rate": Decimal('0.004'), "fixed_fee": Decimal('1.00')},
            PaymentMethod.BANK_TRANSFER: {"fee_rate": Decimal('0.001'), "fixed_fee": Decimal('2.50')},
            PaymentMethod.CRYPTOCURRENCY: {"fee_rate": Decimal('0.01'), "fixed_fee": Decimal('0.00')}
        }
        
        # Currency exchange rates (mock - would integrate with real exchange rate API)
        self.exchange_rates = {
            "USD": Decimal('1.00'),
            "EUR": Decimal('0.85'),
            "GBP": Decimal('0.73'),
            "CAD": Decimal('1.25'),
            "AUD": Decimal('1.35'),
            "JPY": Decimal('110.00'),
            "BTC": Decimal('0.000023'),
            "ETH": Decimal('0.00041')
        }
        
        # Metrics tracking
        self.metrics = {
            "total_distributions": 0,
            "total_revenue_processed": Decimal('0.00'),
            "total_fees_collected": Decimal('0.00'),
            "successful_payments": 0,
            "failed_payments": 0,
            "average_processing_time": 0,
            "payment_success_rate": 1.0
        }
        
        logger.info("💰 Payment Distribution Tracker initialized")
        self._setup_default_configurations()
    
    def _setup_default_configurations(self) -> None:
        """Setup default payment configurations."""
        self.default_distribution_rules = {
            "minimum_threshold": Decimal('10.00'),
            "payment_delay_days": 7,
            "currency_conversion": True,
            "fee_allocation": "proportional",  # proportional, deduct_from_total, separate_fee
            "retry_attempts": 3,
            "retry_delay_hours": 24
        }
    
    def register_payment_recipient(
        self,
        creator_id: str,
        name: str,
        email: str,
        payment_methods: Dict[str, Dict[str, Any]],
        tax_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a payment recipient.
        
        Args:
            creator_id: Creator identifier
            name: Recipient name
            email: Recipient email
            payment_methods: Available payment methods and details
            tax_info: Tax information
            
        Returns:
            Recipient ID
        """
        recipient_id = f"recipient_{creator_id}_{int(time.time())}"
        
        # Convert payment methods string keys to enum
        converted_methods = {}
        for method_str, details in payment_methods.items():
            try:
                method_enum = PaymentMethod(method_str)
                converted_methods[method_enum] = details
            except ValueError:
                logger.warning(f"Unknown payment method: {method_str}")
        
        recipient = PaymentRecipient(
            recipient_id=recipient_id,
            creator_id=creator_id,
            name=name,
            email=email,
            payment_methods=converted_methods,
            tax_information=tax_info or {},
            preferred_payment_method=list(converted_methods.keys())[0] if converted_methods else None
        )
        
        self.recipients[recipient_id] = recipient
        logger.info(f"💰 Registered payment recipient: {recipient_id} ({name})")
        return recipient_id
    
    def record_revenue_stream(
        self,
        collaboration_id: str,
        source: str,
        total_revenue: Union[float, Decimal],
        currency: str,
        reporting_period: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a new revenue stream.
        
        Args:
            collaboration_id: Collaboration identifier
            source: Revenue source
            total_revenue: Total revenue amount
            currency: Currency code
            reporting_period: Reporting period (e.g., "2025-01")
            metadata: Additional metadata
            
        Returns:
            Revenue stream ID
        """
        stream_id = f"revenue_{collaboration_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        revenue_stream = RevenueStream(
            stream_id=stream_id,
            collaboration_id=collaboration_id,
            source=RevenueSource(source),
            total_revenue=Decimal(str(total_revenue)),
            currency=CurrencyType(currency),
            generated_date=datetime.utcnow(),
            reporting_period=reporting_period,
            metadata=metadata or {}
        )
        
        self.revenue_streams[stream_id] = revenue_stream
        logger.info(f"💰 Recorded revenue stream: {stream_id} (${total_revenue} {currency})")
        return stream_id
    
    async def create_payment_distribution(
        self,
        collaboration_id: str,
        revenue_stream_id: str,
        distribution_rules: Dict[str, Any]
    ) -> str:
        """
        Create a payment distribution for a revenue stream.
        
        Args:
            collaboration_id: Collaboration identifier
            revenue_stream_id: Revenue stream to distribute
            distribution_rules: Rules for payment distribution
            
        Returns:
            Distribution ID
        """
        if revenue_stream_id not in self.revenue_streams:
            raise ValueError(f"Revenue stream {revenue_stream_id} not found")
        
        revenue_stream = self.revenue_streams[revenue_stream_id]
        distribution_id = f"dist_{collaboration_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Calculate fees
        total_fees = self._calculate_total_fees(revenue_stream.total_revenue, distribution_rules)
        net_amount = revenue_stream.total_revenue - total_fees
        
        # Create distribution record
        distribution = PaymentDistribution(
            distribution_id=distribution_id,
            collaboration_id=collaboration_id,
            revenue_stream_id=revenue_stream_id,
            total_amount=revenue_stream.total_revenue,
            currency=revenue_stream.currency,
            distribution_rules=distribution_rules,
            fees={"platform_fee": total_fees},
            net_amount=net_amount
        )
        
        # Calculate individual payments
        recipient_payments = await self._calculate_recipient_payments(
            distribution, distribution_rules
        )
        distribution.recipient_payments = recipient_payments
        
        self.distributions[distribution_id] = distribution
        self.metrics["total_distributions"] += 1
        
        logger.info(f"💰 Created payment distribution: {distribution_id} (${net_amount} {revenue_stream.currency.value})")
        return distribution_id
    
    def _calculate_total_fees(self, amount: Decimal, rules: Dict[str, Any]) -> Decimal:
        """Calculate total fees for payment distribution."""
        platform_fee_rate = Decimal(str(rules.get("platform_fee_rate", 0.05)))  # 5% default
        platform_fee = amount * platform_fee_rate
        
        # Additional fees based on payment methods and processors
        processor_fees = Decimal('0.00')
        payment_methods = rules.get("preferred_payment_methods", [])
        
        for method_str in payment_methods:
            try:
                method = PaymentMethod(method_str)
                processor_config = self.payment_processors.get(method, {})
                fee_rate = processor_config.get("fee_rate", Decimal('0.00'))
                fixed_fee = processor_config.get("fixed_fee", Decimal('0.00'))
                processor_fees += (amount * fee_rate) + fixed_fee
            except ValueError:
                continue
        
        # Average processor fees across methods
        if payment_methods:
            processor_fees = processor_fees / len(payment_methods)
        
        total_fees = platform_fee + processor_fees
        return total_fees.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_recipient_payments(
        self,
        distribution: PaymentDistribution,
        rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate individual recipient payments."""
        revenue_splits = rules.get("revenue_splits", {})
        recipient_payments = []
        
        for recipient_id, split_percentage in revenue_splits.items():
            if recipient_id not in self.recipients:
                logger.warning(f"Recipient {recipient_id} not found, skipping payment")
                continue
            
            recipient = self.recipients[recipient_id]
            
            # Calculate payment amount
            split_decimal = Decimal(str(split_percentage)) / Decimal('100')
            payment_amount = distribution.net_amount * split_decimal
            
            # Check minimum threshold
            if payment_amount < recipient.minimum_payment_threshold:
                logger.info(f"Payment ${payment_amount} below threshold for {recipient_id}, holding for next cycle")
                continue
            
            # Currency conversion if needed
            target_currency = rules.get("payment_currency", distribution.currency.value)
            converted_amount, conversion_rate = self._convert_currency(
                payment_amount, distribution.currency.value, target_currency
            )
            
            # Determine payment method
            payment_method = self._select_payment_method(recipient, rules)
            
            # Calculate fees for this payment
            payment_fees = self._calculate_payment_fees(converted_amount, payment_method)
            net_payment = converted_amount - payment_fees
            
            recipient_payment = {
                "recipient_id": recipient_id,
                "amount": payment_amount,
                "converted_amount": converted_amount,
                "net_amount": net_payment,
                "currency": target_currency,
                "conversion_rate": conversion_rate,
                "payment_method": payment_method.value,
                "fees": payment_fees,
                "split_percentage": split_percentage
            }
            
            recipient_payments.append(recipient_payment)
        
        return recipient_payments
    
    def _convert_currency(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str
    ) -> tuple[Decimal, Decimal]:
        """Convert currency amount."""
        if from_currency == to_currency:
            return amount, Decimal('1.00')
        
        from_rate = self.exchange_rates.get(from_currency, Decimal('1.00'))
        to_rate = self.exchange_rates.get(to_currency, Decimal('1.00'))
        
        # Convert to USD base, then to target currency
        usd_amount = amount / from_rate
        converted_amount = usd_amount * to_rate
        conversion_rate = to_rate / from_rate
        
        return converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), conversion_rate
    
    def _select_payment_method(
        self,
        recipient: PaymentRecipient,
        rules: Dict[str, Any]
    ) -> PaymentMethod:
        """Select optimal payment method for recipient."""
        # Check recipient preference first
        if recipient.preferred_payment_method and recipient.preferred_payment_method in recipient.payment_methods:
            return recipient.preferred_payment_method
        
        # Check distribution rules preferences
        preferred_methods = rules.get("preferred_payment_methods", [])
        for method_str in preferred_methods:
            try:
                method = PaymentMethod(method_str)
                if method in recipient.payment_methods:
                    return method
            except ValueError:
                continue
        
        # Default to first available method
        if recipient.payment_methods:
            return list(recipient.payment_methods.keys())[0]
        
        # Fallback
        return PaymentMethod.BANK_TRANSFER
    
    def _calculate_payment_fees(self, amount: Decimal, payment_method: PaymentMethod) -> Decimal:
        """Calculate fees for specific payment method."""
        processor_config = self.payment_processors.get(payment_method, {})
        fee_rate = processor_config.get("fee_rate", Decimal('0.00'))
        fixed_fee = processor_config.get("fixed_fee", Decimal('0.00'))
        
        total_fee = (amount * fee_rate) + fixed_fee
        return total_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def process_payment_distribution(self, distribution_id: str) -> Dict[str, Any]:
        """
        Process all payments in a distribution.
        
        Args:
            distribution_id: Distribution to process
            
        Returns:
            Processing results
        """
        if distribution_id not in self.distributions:
            return {"error": "Distribution not found"}
        
        distribution = self.distributions[distribution_id]
        
        if distribution.status != PaymentStatus.PENDING:
            return {"error": f"Distribution already {distribution.status.value}"}
        
        distribution.status = PaymentStatus.PROCESSING
        processing_results = {
            "distribution_id": distribution_id,
            "total_payments": len(distribution.recipient_payments),
            "successful_payments": 0,
            "failed_payments": 0,
            "transactions": []
        }
        
        try:
            # Process each recipient payment
            for payment_data in distribution.recipient_payments:
                transaction_result = await self._process_individual_payment(
                    distribution, payment_data
                )
                processing_results["transactions"].append(transaction_result)
                
                if transaction_result["status"] == PaymentStatus.COMPLETED.value:
                    processing_results["successful_payments"] += 1
                    self.metrics["successful_payments"] += 1
                else:
                    processing_results["failed_payments"] += 1
                    self.metrics["failed_payments"] += 1
            
            # Update distribution status
            if processing_results["failed_payments"] == 0:
                distribution.status = PaymentStatus.COMPLETED
            elif processing_results["successful_payments"] == 0:
                distribution.status = PaymentStatus.FAILED
            else:
                distribution.status = PaymentStatus.COMPLETED  # Partial success
            
            distribution.processed_at = datetime.utcnow()
            
            # Update metrics
            self.metrics["total_revenue_processed"] += distribution.total_amount
            self._update_payment_success_rate()
            
            logger.info(f"💰 Processed distribution {distribution_id}: {processing_results['successful_payments']}/{processing_results['total_payments']} successful")
            return processing_results
            
        except Exception as e:
            distribution.status = PaymentStatus.FAILED
            logger.error(f"❌ Error processing distribution {distribution_id}: {e}")
            return {"error": str(e)}
    
    async def _process_individual_payment(
        self,
        distribution: PaymentDistribution,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process an individual payment transaction."""
        transaction_id = f"txn_{distribution.distribution_id}_{payment_data['recipient_id']}_{int(time.time())}"
        
        try:
            recipient_id = payment_data["recipient_id"]
            recipient = self.recipients[recipient_id]
            payment_method = PaymentMethod(payment_data["payment_method"])
            
            # Create transaction record
            transaction = PaymentTransaction(
                transaction_id=transaction_id,
                distribution_id=distribution.distribution_id,
                recipient_id=recipient_id,
                amount=payment_data["converted_amount"],
                currency=CurrencyType(payment_data["currency"]),
                payment_method=payment_method,
                status=PaymentStatus.PROCESSING,
                created_at=datetime.utcnow(),
                fees=payment_data["fees"],
                net_amount=payment_data["net_amount"]
            )
            
            self.transactions[transaction_id] = transaction
            
            # Simulate payment processing (in real implementation, this would integrate with payment processors)
            processing_result = await self._simulate_payment_processing(
                transaction, recipient, payment_method
            )
            
            # Update transaction with result
            transaction.status = PaymentStatus(processing_result["status"])
            transaction.processed_at = datetime.utcnow()
            transaction.confirmation_code = processing_result.get("confirmation_code")
            transaction.error_message = processing_result.get("error_message")
            
            logger.info(f"💰 Payment {transaction_id}: {processing_result['status']}")
            
            return {
                "transaction_id": transaction_id,
                "recipient_id": recipient_id,
                "amount": str(payment_data["net_amount"]),
                "currency": payment_data["currency"],
                "status": processing_result["status"],
                "confirmation_code": processing_result.get("confirmation_code"),
                "error_message": processing_result.get("error_message")
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing payment for {payment_data.get('recipient_id')}: {e}")
            return {
                "transaction_id": transaction_id,
                "recipient_id": payment_data.get("recipient_id"),
                "status": PaymentStatus.FAILED.value,
                "error_message": str(e)
            }
    
    async def _simulate_payment_processing(
        self,
        transaction: PaymentTransaction,
        recipient: PaymentRecipient,
        payment_method: PaymentMethod
    ) -> Dict[str, Any]:
        """
        Simulate payment processing (mock implementation).
        In real implementation, this would integrate with actual payment processors.
        """
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Simulate success/failure based on various factors
        success_rate = 0.95  # 95% success rate
        
        # Reduce success rate for certain conditions
        if transaction.amount < Decimal('1.00'):
            success_rate = 0.8  # Lower success for small amounts
        
        if payment_method == PaymentMethod.CRYPTOCURRENCY:
            success_rate = 0.9  # Slightly lower for crypto
        
        # Simulate payment result
        import random
        if random.random() < success_rate:
            return {
                "status": PaymentStatus.COMPLETED.value,
                "confirmation_code": f"CONF_{uuid.uuid4().hex[:8].upper()}"
            }
        else:
            error_messages = [
                "Insufficient funds",
                "Invalid payment method",
                "Payment processor timeout",
                "Account verification required",
                "Daily limit exceeded"
            ]
            return {
                "status": PaymentStatus.FAILED.value,
                "error_message": random.choice(error_messages)
            }
    
    def _update_payment_success_rate(self) -> None:
        """Update payment success rate metric."""
        total_payments = self.metrics["successful_payments"] + self.metrics["failed_payments"]
        if total_payments > 0:
            self.metrics["payment_success_rate"] = self.metrics["successful_payments"] / total_payments
    
    async def retry_failed_payments(self, distribution_id: str) -> Dict[str, Any]:
        """Retry failed payments in a distribution."""
        if distribution_id not in self.distributions:
            return {"error": "Distribution not found"}
        
        distribution = self.distributions[distribution_id]
        
        # Find failed transactions
        failed_transactions = [
            t for t in self.transactions.values()
            if t.distribution_id == distribution_id and t.status == PaymentStatus.FAILED
        ]
        
        retry_results = {
            "distribution_id": distribution_id,
            "retried_payments": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "results": []
        }
        
        for transaction in failed_transactions:
            if transaction.retry_count >= 3:  # Max 3 retries
                continue
            
            transaction.retry_count += 1
            transaction.status = PaymentStatus.PROCESSING
            
            # Get recipient and payment method info
            recipient = self.recipients[transaction.recipient_id]
            
            # Retry payment processing
            processing_result = await self._simulate_payment_processing(
                transaction, recipient, transaction.payment_method
            )
            
            transaction.status = PaymentStatus(processing_result["status"])
            transaction.processed_at = datetime.utcnow()
            transaction.confirmation_code = processing_result.get("confirmation_code")
            transaction.error_message = processing_result.get("error_message")
            
            retry_results["retried_payments"] += 1
            
            if transaction.status == PaymentStatus.COMPLETED:
                retry_results["successful_retries"] += 1
            else:
                retry_results["failed_retries"] += 1
            
            retry_results["results"].append({
                "transaction_id": transaction.transaction_id,
                "status": transaction.status.value,
                "retry_count": transaction.retry_count
            })
        
        logger.info(f"💰 Retried {retry_results['retried_payments']} failed payments for {distribution_id}")
        return retry_results
    
    def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get status of a specific payment transaction."""
        if transaction_id not in self.transactions:
            return {"error": "Transaction not found"}
        
        transaction = self.transactions[transaction_id]
        
        return {
            "transaction_id": transaction_id,
            "status": transaction.status.value,
            "amount": str(transaction.amount),
            "currency": transaction.currency.value,
            "payment_method": transaction.payment_method.value,
            "created_at": transaction.created_at.isoformat(),
            "processed_at": transaction.processed_at.isoformat() if transaction.processed_at else None,
            "confirmation_code": transaction.confirmation_code,
            "retry_count": transaction.retry_count,
            "error_message": transaction.error_message
        }
    
    async def get_financial_report(
        self,
        collaboration_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive financial report.
        
        Args:
            collaboration_id: Optional collaboration filter
            period_days: Reporting period in days
            
        Returns:
            Financial report data
        """
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            # Filter data for the period
            if collaboration_id:
                distributions = [
                    d for d in self.distributions.values()
                    if d.collaboration_id == collaboration_id and d.created_at >= period_start
                ]
            else:
                distributions = [
                    d for d in self.distributions.values()
                    if d.created_at >= period_start
                ]
            
            period_transactions = [
                t for t in self.transactions.values()
                if t.created_at >= period_start
            ]
            
            # Calculate summary metrics
            total_revenue = sum(d.total_amount for d in distributions)
            total_fees = sum(sum(d.fees.values()) for d in distributions)
            total_distributed = sum(d.net_amount or Decimal('0') for d in distributions)
            
            successful_transactions = [t for t in period_transactions if t.status == PaymentStatus.COMPLETED]
            failed_transactions = [t for t in period_transactions if t.status == PaymentStatus.FAILED]
            
            # Revenue by source
            revenue_by_source = {}
            for dist in distributions:
                if dist.revenue_stream_id in self.revenue_streams:
                    revenue_stream = self.revenue_streams[dist.revenue_stream_id]
                    source = revenue_stream.source.value
                    revenue_by_source[source] = revenue_by_source.get(source, Decimal('0')) + dist.total_amount
            
            # Payment method analysis
            payment_method_stats = {}
            for transaction in successful_transactions:
                method = transaction.payment_method.value
                if method not in payment_method_stats:
                    payment_method_stats[method] = {"count": 0, "total_amount": Decimal('0'), "total_fees": Decimal('0')}
                
                payment_method_stats[method]["count"] += 1
                payment_method_stats[method]["total_amount"] += transaction.amount
                payment_method_stats[method]["total_fees"] += transaction.fees
            
            report = {
                "period_days": period_days,
                "collaboration_id": collaboration_id,
                "summary": {
                    "total_revenue": str(total_revenue),
                    "total_fees": str(total_fees),
                    "total_distributed": str(total_distributed),
                    "fee_percentage": float((total_fees / total_revenue * 100) if total_revenue > 0 else 0),
                    "total_distributions": len(distributions),
                    "total_transactions": len(period_transactions),
                    "successful_transactions": len(successful_transactions),
                    "failed_transactions": len(failed_transactions),
                    "success_rate": len(successful_transactions) / max(len(period_transactions), 1)
                },
                "revenue_by_source": {k: str(v) for k, v in revenue_by_source.items()},
                "payment_method_analysis": {
                    method: {
                        "count": stats["count"],
                        "total_amount": str(stats["total_amount"]),
                        "total_fees": str(stats["total_fees"]),
                        "average_amount": str(stats["total_amount"] / max(stats["count"], 1))
                    }
                    for method, stats in payment_method_stats.items()
                },
                "performance_metrics": {
                    "average_distribution_size": str(total_revenue / max(len(distributions), 1)),
                    "average_transaction_size": str(sum(t.amount for t in successful_transactions) / max(len(successful_transactions), 1)),
                    "fee_efficiency": float((total_distributed / total_revenue) if total_revenue > 0 else 0)
                }
            }
            
            logger.info(f"💰 Generated financial report for {period_days} days")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating financial report: {e}")
            return {"error": str(e)}
    
    def get_recipient_earnings(self, recipient_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get earnings summary for a specific recipient."""
        if recipient_id not in self.recipients:
            return {"error": "Recipient not found"}
        
        period_start = datetime.utcnow() - timedelta(days=period_days)
        
        # Find transactions for this recipient
        recipient_transactions = [
            t for t in self.transactions.values()
            if t.recipient_id == recipient_id and t.created_at >= period_start
        ]
        
        completed_transactions = [t for t in recipient_transactions if t.status == PaymentStatus.COMPLETED]
        pending_transactions = [t for t in recipient_transactions if t.status == PaymentStatus.PENDING]
        
        total_earnings = sum(t.net_amount or Decimal('0') for t in completed_transactions)
        pending_earnings = sum(t.net_amount or Decimal('0') for t in pending_transactions)
        total_fees = sum(t.fees for t in completed_transactions)
        
        return {
            "recipient_id": recipient_id,
            "period_days": period_days,
            "total_earnings": str(total_earnings),
            "pending_earnings": str(pending_earnings),
            "total_fees": str(total_fees),
            "transaction_count": len(completed_transactions),
            "pending_transactions": len(pending_transactions),
            "average_payment": str(total_earnings / max(len(completed_transactions), 1))
        }

# Global instance for enterprise payment tracking
payment_distribution_tracker = PaymentDistributionTracker()

__all__ = [
    'PaymentDistributionTracker',
    'PaymentRecipient',
    'RevenueStream',
    'PaymentDistribution',
    'PaymentTransaction',
    'PaymentStatus',
    'PaymentMethod',
    'CurrencyType',
    'RevenueSource',
    'payment_distribution_tracker'
]