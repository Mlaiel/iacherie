"""Creator Payout Orchestrator - Automated Payout Management System
================================================================

Enterprise-grade creator payout orchestrator providing automated
payout processing, multi-gateway payment distribution, and comprehensive
payout management for content creators across all revenue streams.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/creator_payout_orchestrator.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4, UUID
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass, field
import json
from statistics import mean

logger = logging.getLogger(__name__)


class PayoutMethod(str, Enum):
    """Available payout methods."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTO_WALLET = "crypto_wallet"
    CHECK = "check"
    VIRTUAL_CARD = "virtual_card"
    PREPAID_CARD = "prepaid_card"


class PayoutStatus(str, Enum):
    """Payout processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    ON_HOLD = "on_hold"


class PayoutFrequency(str, Enum):
    """Payout frequency options."""
    INSTANT = "instant"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


class Currency(str, Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


@dataclass
class PayoutAccount:
    """Creator payout account information."""
    account_id: str
    creator_id: str
    payout_method: PayoutMethod
    account_details: Dict[str, Any]
    currency: Currency
    minimum_payout: Decimal = Decimal("10.00")
    is_primary: bool = False
    is_verified: bool = False
    verification_date: Optional[datetime] = None
    last_used: Optional[datetime] = None
    fees_percentage: Decimal = Decimal("0.00")
    processing_time_hours: int = 24
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutRule:
    """Automated payout rule configuration."""
    rule_id: str
    creator_id: str
    frequency: PayoutFrequency
    minimum_amount: Decimal
    preferred_method: PayoutMethod
    maximum_amount: Optional[Decimal] = None
    preferred_currency: Currency = Currency.USD
    auto_convert_currency: bool = True
    hold_weekends: bool = False
    hold_holidays: bool = False
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutRequest:
    """Individual payout request."""
    request_id: str
    creator_id: str
    payout_account_id: str
    amount: Decimal
    currency: Currency
    source_revenue_ids: List[str]
    payout_method: PayoutMethod
    status: PayoutStatus = PayoutStatus.PENDING
    fees: Decimal = Decimal("0.00")
    net_amount: Decimal = Decimal("0.00")
    exchange_rate: Optional[Decimal] = None
    processor_reference: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    processed_date: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutSummary:
    """Payout summary for reporting."""
    creator_id: str
    total_payouts: Decimal
    successful_payouts: int
    failed_payouts: int
    pending_payouts: int
    average_payout: Decimal
    largest_payout: Decimal
    method_breakdown: Dict[PayoutMethod, Decimal]
    currency_breakdown: Dict[Currency, Decimal]
    period_start: datetime
    period_end: datetime
    total_fees: Decimal = Decimal("0.00")


class PaymentGatewayInterface:
    """Base interface for payment gateway integrations."""
    
    def __init__(self, gateway_name: str, config: Dict[str, Any]):
        self.gateway_name = gateway_name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{gateway_name}")
    
    async def process_payout(self, payout_request: PayoutRequest) -> Dict[str, Any]:
        """Process a payout request."""
        raise NotImplementedError("Subclasses must implement process_payout")
    
    async def validate_account(self, account_details: Dict[str, Any]) -> bool:
        """Validate payout account details."""
        raise NotImplementedError("Subclasses must implement validate_account")
    
    async def get_fees(self, amount: Decimal, currency: Currency) -> Decimal:
        """Calculate processing fees."""
        raise NotImplementedError("Subclasses must implement get_fees")


class StripePayoutGateway(PaymentGatewayInterface):
    """Stripe payout gateway implementation."""
    
    async def process_payout(self, payout_request: PayoutRequest) -> Dict[str, Any]:
        """Process payout via Stripe."""
        try:
            # Simulate Stripe API call
            self.logger.info(f"Processing Stripe payout: {payout_request.request_id}")
            
            # Simulate processing delay
            await asyncio.sleep(2)
            
            # Calculate fees (2.9% + $0.30 for cards)
            fees = payout_request.amount * Decimal("0.029") + Decimal("0.30")
            
            return {
                "success": True,
                "transaction_id": f"stripe_{uuid4().hex[:12]}",
                "fees": fees,
                "net_amount": payout_request.amount - fees,
                "processing_time": "1-2 business days"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_account(self, account_details: Dict[str, Any]) -> bool:
        """Validate Stripe account details."""
        required_fields = ["account_id", "routing_number"]
        return all(field in account_details for field in required_fields)
    
    async def get_fees(self, amount: Decimal, currency: Currency) -> Decimal:
        """Calculate Stripe fees."""
        return amount * Decimal("0.029") + Decimal("0.30")


class PayPalPayoutGateway(PaymentGatewayInterface):
    """PayPal payout gateway implementation."""
    
    async def process_payout(self, payout_request: PayoutRequest) -> Dict[str, Any]:
        """Process payout via PayPal."""
        try:
            self.logger.info(f"Processing PayPal payout: {payout_request.request_id}")
            
            await asyncio.sleep(1.5)
            
            # PayPal fees: $0.25 per transaction
            fees = Decimal("0.25")
            
            return {
                "success": True,
                "transaction_id": f"paypal_{uuid4().hex[:12]}",
                "fees": fees,
                "net_amount": payout_request.amount - fees,
                "processing_time": "instant"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_account(self, account_details: Dict[str, Any]) -> bool:
        """Validate PayPal account details."""
        return "email" in account_details
    
    async def get_fees(self, amount: Decimal, currency: Currency) -> Decimal:
        """Calculate PayPal fees."""
        return Decimal("0.25")


class CreatorPayoutOrchestrator:
    """
    Advanced creator payout orchestrator providing automated payout
    processing and multi-gateway payment distribution.
    """
    
    def __init__(self):
        """Initialize the creator payout orchestrator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.payout_accounts: Dict[str, List[PayoutAccount]] = {}  # creator_id -> accounts
        self.payout_rules: Dict[str, PayoutRule] = {}  # creator_id -> rule
        self.payout_requests: Dict[str, PayoutRequest] = {}
        self.pending_revenue: Dict[str, Decimal] = {}  # creator_id -> amount
        self.payment_gateways: Dict[PayoutMethod, PaymentGatewayInterface] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.is_processing: bool = False
        
        # Exchange rates (simplified - in production, use real-time rates)
        self.exchange_rates = {
            (Currency.USD, Currency.EUR): Decimal("0.85"),
            (Currency.USD, Currency.GBP): Decimal("0.73"),
            (Currency.EUR, Currency.USD): Decimal("1.18"),
            (Currency.GBP, Currency.USD): Decimal("1.37"),
        }
        
        # Initialize payment gateways
        self._initialize_payment_gateways()
        
        self.logger.info("CreatorPayoutOrchestrator initialized")
    
    def _initialize_payment_gateways(self):
        """Initialize payment gateway integrations."""
        self.payment_gateways[PayoutMethod.STRIPE] = StripePayoutGateway(
            "stripe", {"api_key": "test_key"}
        )
        self.payment_gateways[PayoutMethod.PAYPAL] = PayPalPayoutGateway(
            "paypal", {"client_id": "test_client"}
        )
    
    async def register_payout_account(
        self,
        creator_id: str,
        payout_method: PayoutMethod,
        account_details: Dict[str, Any],
        currency: Currency = Currency.USD,
        minimum_payout: Decimal = Decimal("10.00"),
        is_primary: bool = False
    ) -> str:
        """Register a new payout account for creator."""
        try:
            # Validate account details
            gateway = self.payment_gateways.get(payout_method)
            if gateway and not await gateway.validate_account(account_details):
                raise ValueError(f"Invalid account details for {payout_method.value}")
            
            account_id = str(uuid4())
            
            # Calculate fees for this method
            fees_percentage = await self._calculate_fees_percentage(payout_method, currency)
            
            account = PayoutAccount(
                account_id=account_id,
                creator_id=creator_id,
                payout_method=payout_method,
                account_details=account_details,
                currency=currency,
                minimum_payout=minimum_payout,
                is_primary=is_primary,
                fees_percentage=fees_percentage,
                processing_time_hours=self._get_processing_time(payout_method)
            )
            
            # Store account
            if creator_id not in self.payout_accounts:
                self.payout_accounts[creator_id] = []
            
            # Set as primary if it's the first account or explicitly requested
            if is_primary or not self.payout_accounts[creator_id]:
                # Remove primary flag from other accounts
                for acc in self.payout_accounts[creator_id]:
                    acc.is_primary = False
                account.is_primary = True
            
            self.payout_accounts[creator_id].append(account)
            
            self.logger.info(f"Registered payout account: {account_id} for creator: {creator_id}")
            return account_id
            
        except Exception as e:
            self.logger.error(f"Error registering payout account: {e}")
            raise
    
    async def _calculate_fees_percentage(self, method: PayoutMethod, currency: Currency) -> Decimal:
        """Calculate fees percentage for payout method."""
        fee_rates = {
            PayoutMethod.STRIPE: Decimal("2.9"),
            PayoutMethod.PAYPAL: Decimal("0.5"),
            PayoutMethod.BANK_TRANSFER: Decimal("0.8"),
            PayoutMethod.WISE: Decimal("0.4"),
            PayoutMethod.CRYPTO_WALLET: Decimal("1.0")
        }
        return fee_rates.get(method, Decimal("1.0"))
    
    def _get_processing_time(self, method: PayoutMethod) -> int:
        """Get processing time in hours for payout method."""
        processing_times = {
            PayoutMethod.PAYPAL: 1,
            PayoutMethod.CRYPTO_WALLET: 1,
            PayoutMethod.STRIPE: 48,
            PayoutMethod.BANK_TRANSFER: 72,
            PayoutMethod.WISE: 24,
            PayoutMethod.CHECK: 168  # 1 week
        }
        return processing_times.get(method, 24)
    
    async def setup_payout_rule(
        self,
        creator_id: str,
        frequency: PayoutFrequency,
        minimum_amount: Decimal,
        preferred_method: PayoutMethod,
        maximum_amount: Optional[Decimal] = None
    ) -> str:
        """Setup automated payout rule for creator."""
        try:
            rule_id = str(uuid4())
            
            rule = PayoutRule(
                rule_id=rule_id,
                creator_id=creator_id,
                frequency=frequency,
                minimum_amount=minimum_amount,
                maximum_amount=maximum_amount,
                preferred_method=preferred_method
            )
            
            self.payout_rules[creator_id] = rule
            
            self.logger.info(f"Setup payout rule: {rule_id} for creator: {creator_id}")
            return rule_id
            
        except Exception as e:
            self.logger.error(f"Error setting up payout rule: {e}")
            raise
    
    async def add_revenue(
        self,
        creator_id: str,
        amount: Decimal,
        revenue_id: str,
        currency: Currency = Currency.USD
    ):
        """Add revenue to creator's pending payout balance."""
        if creator_id not in self.pending_revenue:
            self.pending_revenue[creator_id] = Decimal("0")
        
        # Convert to USD if needed
        if currency != Currency.USD:
            amount = await self._convert_currency(amount, currency, Currency.USD)
        
        self.pending_revenue[creator_id] += amount
        
        # Check if automated payout should be triggered
        await self._check_automated_payout(creator_id)
        
        self.logger.debug(f"Added revenue ${amount} for creator: {creator_id}")
    
    async def _convert_currency(
        self,
        amount: Decimal,
        from_currency: Currency,
        to_currency: Currency
    ) -> Decimal:
        """Convert amount between currencies."""
        if from_currency == to_currency:
            return amount
        
        rate = self.exchange_rates.get((from_currency, to_currency))
        if rate:
            return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Default to 1:1 if rate not found
        return amount
    
    async def _check_automated_payout(self, creator_id: str):
        """Check if automated payout should be triggered."""
        if creator_id not in self.payout_rules:
            return
        
        rule = self.payout_rules[creator_id]
        if not rule.is_active:
            return
        
        pending_amount = self.pending_revenue.get(creator_id, Decimal("0"))
        
        # Check minimum amount threshold
        if pending_amount < rule.minimum_amount:
            return
        
        # Check maximum amount threshold
        payout_amount = pending_amount
        if rule.maximum_amount and pending_amount > rule.maximum_amount:
            payout_amount = rule.maximum_amount
        
        # Create automated payout request
        await self.create_payout_request(
            creator_id=creator_id,
            amount=payout_amount,
            payout_method=rule.preferred_method,
            currency=rule.preferred_currency,
            auto_generated=True
        )
    
    async def create_payout_request(
        self,
        creator_id: str,
        amount: Decimal,
        payout_method: Optional[PayoutMethod] = None,
        currency: Currency = Currency.USD,
        payout_account_id: Optional[str] = None,
        auto_generated: bool = False
    ) -> str:
        """Create a new payout request."""
        try:
            # Validate creator has sufficient balance
            pending_amount = self.pending_revenue.get(creator_id, Decimal("0"))
            if amount > pending_amount:
                raise ValueError(f"Insufficient balance: {pending_amount}, requested: {amount}")
            
            # Find appropriate payout account
            if not payout_account_id:
                accounts = self.payout_accounts.get(creator_id, [])
                if not accounts:
                    raise ValueError("No payout accounts configured")
                
                # Use primary account or first account if no primary
                primary_account = next((acc for acc in accounts if acc.is_primary), accounts[0])
                payout_account_id = primary_account.account_id
                
                if not payout_method:
                    payout_method = primary_account.payout_method
            
            # Find the account
            account = None
            for acc in self.payout_accounts.get(creator_id, []):
                if acc.account_id == payout_account_id:
                    account = acc
                    break
            
            if not account:
                raise ValueError(f"Payout account not found: {payout_account_id}")
            
            # Check minimum payout
            if amount < account.minimum_payout:
                raise ValueError(f"Amount below minimum payout: {account.minimum_payout}")
            
            request_id = str(uuid4())
            
            # Calculate fees
            gateway = self.payment_gateways.get(payout_method)
            fees = await gateway.get_fees(amount, currency) if gateway else Decimal("0")
            
            payout_request = PayoutRequest(
                request_id=request_id,
                creator_id=creator_id,
                payout_account_id=payout_account_id,
                amount=amount,
                currency=currency,
                source_revenue_ids=[],  # TODO: Track specific revenue sources
                payout_method=payout_method,
                fees=fees,
                net_amount=amount - fees,
                metadata={"auto_generated": auto_generated}
            )
            
            self.payout_requests[request_id] = payout_request
            
            # Deduct from pending balance
            self.pending_revenue[creator_id] -= amount
            
            # Add to processing queue
            await self.processing_queue.put(request_id)
            
            self.logger.info(f"Created payout request: {request_id} for ${amount}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error creating payout request: {e}")
            raise
    
    async def start_payout_processor(self):
        """Start the payout processing service."""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.logger.info("Starting payout processor")
        
        async def process_payouts():
            while self.is_processing:
                try:
                    # Get next payout request
                    request_id = await asyncio.wait_for(
                        self.processing_queue.get(),
                        timeout=5.0
                    )
                    
                    await self._process_payout_request(request_id)
                    
                except asyncio.TimeoutError:
                    # No payouts to process
                    continue
                except Exception as e:
                    self.logger.error(f"Error in payout processor: {e}")
                    await asyncio.sleep(10)
        
        # Start processor task
        asyncio.create_task(process_payouts())
    
    async def _process_payout_request(self, request_id: str):
        """Process a single payout request."""
        try:
            payout_request = self.payout_requests.get(request_id)
            if not payout_request:
                self.logger.error(f"Payout request not found: {request_id}")
                return
            
            self.logger.info(f"Processing payout request: {request_id}")
            
            payout_request.status = PayoutStatus.PROCESSING
            
            # Get payment gateway
            gateway = self.payment_gateways.get(payout_request.payout_method)
            if not gateway:
                payout_request.status = PayoutStatus.FAILED
                payout_request.error_message = f"No gateway for method: {payout_request.payout_method.value}"
                return
            
            # Process payment
            result = await gateway.process_payout(payout_request)
            
            if result.get("success"):
                payout_request.status = PayoutStatus.COMPLETED
                payout_request.processor_reference = result.get("transaction_id")
                payout_request.processed_date = datetime.utcnow()
                payout_request.fees = result.get("fees", payout_request.fees)
                payout_request.net_amount = result.get("net_amount", payout_request.net_amount)
                
                self.logger.info(f"✅ Payout completed: {request_id}")
                
            else:
                payout_request.status = PayoutStatus.FAILED
                payout_request.error_message = result.get("error", "Unknown error")
                
                # Return amount to pending balance
                creator_id = payout_request.creator_id
                if creator_id not in self.pending_revenue:
                    self.pending_revenue[creator_id] = Decimal("0")
                self.pending_revenue[creator_id] += payout_request.amount
                
                # Retry if under limit
                if payout_request.retry_count < 3:
                    payout_request.retry_count += 1
                    payout_request.status = PayoutStatus.PENDING
                    await asyncio.sleep(300)  # Wait 5 minutes before retry
                    await self.processing_queue.put(request_id)
                    
                self.logger.error(f"❌ Payout failed: {request_id} - {payout_request.error_message}")
                
        except Exception as e:
            self.logger.error(f"Error processing payout {request_id}: {e}")
            if request_id in self.payout_requests:
                self.payout_requests[request_id].status = PayoutStatus.FAILED
                self.payout_requests[request_id].error_message = str(e)
    
    async def get_payout_status(self, request_id: str) -> Optional[PayoutRequest]:
        """Get payout request status."""
        return self.payout_requests.get(request_id)
    
    async def get_creator_payouts(
        self,
        creator_id: str,
        status: Optional[PayoutStatus] = None,
        limit: int = 50
    ) -> List[PayoutRequest]:
        """Get payout history for creator."""
        payouts = [
            request for request in self.payout_requests.values()
            if request.creator_id == creator_id
        ]
        
        # Filter by status if specified
        if status:
            payouts = [p for p in payouts if p.status == status]
        
        # Sort by creation date (newest first) and limit
        payouts.sort(key=lambda x: x.created_at, reverse=True)
        return payouts[:limit]
    
    async def get_pending_balance(self, creator_id: str) -> Decimal:
        """Get creator's pending payout balance."""
        return self.pending_revenue.get(creator_id, Decimal("0"))
    
    async def cancel_payout(self, request_id: str) -> bool:
        """Cancel a pending payout request."""
        try:
            payout_request = self.payout_requests.get(request_id)
            if not payout_request:
                return False
            
            if payout_request.status != PayoutStatus.PENDING:
                return False
            
            payout_request.status = PayoutStatus.CANCELLED
            
            # Return amount to pending balance
            creator_id = payout_request.creator_id
            if creator_id not in self.pending_revenue:
                self.pending_revenue[creator_id] = Decimal("0")
            self.pending_revenue[creator_id] += payout_request.amount
            
            self.logger.info(f"Cancelled payout request: {request_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cancelling payout: {e}")
            return False
    
    async def generate_payout_summary(
        self,
        creator_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> PayoutSummary:
        """Generate payout summary for reporting."""
        payouts = [
            request for request in self.payout_requests.values()
            if (request.creator_id == creator_id and
                start_date <= request.created_at <= end_date)
        ]
        
        total_payouts = sum(p.amount for p in payouts if p.status == PayoutStatus.COMPLETED)
        total_fees = sum(p.fees for p in payouts if p.status == PayoutStatus.COMPLETED)
        
        successful_payouts = len([p for p in payouts if p.status == PayoutStatus.COMPLETED])
        failed_payouts = len([p for p in payouts if p.status == PayoutStatus.FAILED])
        pending_payouts = len([p for p in payouts if p.status == PayoutStatus.PENDING])
        
        # Method breakdown
        method_breakdown = {}
        for payout in payouts:
            if payout.status == PayoutStatus.COMPLETED:
                method = payout.payout_method
                method_breakdown[method] = method_breakdown.get(method, Decimal("0")) + payout.amount
        
        # Currency breakdown
        currency_breakdown = {}
        for payout in payouts:
            if payout.status == PayoutStatus.COMPLETED:
                currency = payout.currency
                currency_breakdown[currency] = currency_breakdown.get(currency, Decimal("0")) + payout.amount
        
        avg_payout = total_payouts / max(successful_payouts, 1)
        largest_payout = max((p.amount for p in payouts if p.status == PayoutStatus.COMPLETED), default=Decimal("0"))
        
        return PayoutSummary(
            creator_id=creator_id,
            total_payouts=total_payouts,
            successful_payouts=successful_payouts,
            failed_payouts=failed_payouts,
            pending_payouts=pending_payouts,
            average_payout=avg_payout,
            largest_payout=largest_payout,
            method_breakdown=method_breakdown,
            currency_breakdown=currency_breakdown,
            period_start=start_date,
            period_end=end_date,
            total_fees=total_fees
        )
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide payout statistics."""
        total_requests = len(self.payout_requests)
        
        status_counts = {}
        method_counts = {}
        total_volume = Decimal("0")
        
        for request in self.payout_requests.values():
            # Status distribution
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Method distribution
            method = request.payout_method.value
            method_counts[method] = method_counts.get(method, 0) + 1
            
            # Volume calculation
            if request.status == PayoutStatus.COMPLETED:
                total_volume += request.amount
        
        success_rate = (
            status_counts.get("completed", 0) / max(total_requests, 1) * 100
        )
        
        return {
            "total_requests": total_requests,
            "total_volume": str(total_volume),
            "success_rate": round(success_rate, 2),
            "pending_queue_size": self.processing_queue.qsize(),
            "status_distribution": status_counts,
            "method_distribution": method_counts,
            "registered_creators": len(self.payout_accounts),
            "active_rules": len([r for r in self.payout_rules.values() if r.is_active])
        }
    
    async def stop(self):
        """Stop the payout orchestrator."""
        self.is_processing = False
        self.logger.info("Payout orchestrator stopped")


# Example usage and testing
async def main():
    """Example usage of CreatorPayoutOrchestrator."""
    orchestrator = CreatorPayoutOrchestrator()
    
    creator_id = "test_creator_123"
    
    # Register payout account
    account_id = await orchestrator.register_payout_account(
        creator_id=creator_id,
        payout_method=PayoutMethod.PAYPAL,
        account_details={"email": "creator@example.com"},
        currency=Currency.USD,
        minimum_payout=Decimal("25.00"),
        is_primary=True
    )
    print(f"Registered payout account: {account_id}")
    
    # Setup payout rule
    rule_id = await orchestrator.setup_payout_rule(
        creator_id=creator_id,
        frequency=PayoutFrequency.WEEKLY,
        minimum_amount=Decimal("50.00"),
        preferred_method=PayoutMethod.PAYPAL,
        maximum_amount=None
    )
    print(f"Setup payout rule: {rule_id}")
    
    # Start payout processor
    await orchestrator.start_payout_processor()
    
    # Add revenue
    await orchestrator.add_revenue(creator_id, Decimal("75.50"), "rev_123")
    print(f"Added revenue, pending balance: ${await orchestrator.get_pending_balance(creator_id)}")
    
    # Create manual payout
    payout_id = await orchestrator.create_payout_request(
        creator_id=creator_id,
        amount=Decimal("50.00"),
        payout_method=PayoutMethod.PAYPAL
    )
    print(f"Created payout request: {payout_id}")
    
    # Wait for processing
    await asyncio.sleep(5)
    
    # Check payout status
    payout = await orchestrator.get_payout_status(payout_id)
    if payout:
        print(f"Payout status: {payout.status.value}")
        print(f"Net amount: ${payout.net_amount}")
    
    # Get statistics
    stats = await orchestrator.get_system_statistics()
    print(f"System Statistics: {stats}")
    
    # Stop orchestrator
    await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())