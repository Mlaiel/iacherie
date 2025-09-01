"""Payment Processing Agent - Industrial Payment Ecosystem Core

Main agent class coordinating all payment processing operations, revenue tracking,
creator payouts, fraud detection, and financial compliance for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Union, Any, Tuple
from uuid import uuid4
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..base import BaseAgent, AgentStatus, AgentCapability
from .models import (
    PaymentTransaction,
    PayoutSchedule, 
    PaymentMethod,
    RevenueAllocation,
    TaxConfiguration,
    PaymentProvider
)
from .processors import (
    StripeProcessor,
    WiseProcessor,
    PayPalProcessor,
    CryptoProcessor
)
from .validators import PaymentValidator
from .schedulers import PayoutScheduler
from .analytics import PaymentAnalytics
from .compliance import ComplianceManager
from .fraud_detection import FraudDetectionEngine
from .webhooks import WebhookHandler
from .exceptions import (
    PaymentProcessingError,
    InsufficientFundsError,
    InvalidPaymentMethodError,
    FraudDetectedError,
    ComplianceError
)
from .config import PaymentConfig

logger = logging.getLogger(__name__)


class PaymentProcessingAgent(BaseAgent):
    """
    Industrial payment processing agent for creator monetization ecosystem.
    
    Handles multi-currency payments, automated payouts, fraud detection,
    tax compliance, and revenue analytics for content creators.
    """
    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        db_session: Optional[Session] = None,
        **kwargs
    ):
        """
Initialize payment processing agent with enterprise configuration."""
        super().__init__(
            name="payment_processing_agent",
            version="1.0.0",
            capabilities=[
                AgentCapability.PAYMENT_PROCESSING,
                AgentCapability.REVENUE_TRACKING,
                AgentCapability.FRAUD_DETECTION,
                AgentCapability.COMPLIANCE_MANAGEMENT,
                AgentCapability.ANALYTICS_REPORTING
            ],
            **kwargs
        )
        
        self.config = config or PaymentConfig()
        self.db_session = db_session
        
        # Initialize payment processors
        self.processors = self._initialize_processors()
        
        # Initialize core components
        self.validator = PaymentValidator()
        self.scheduler = PayoutScheduler(db_session=db_session)
        self.analytics = PaymentAnalytics(db_session=db_session)
        self.compliance = ComplianceManager()
        self.fraud_detector = FraudDetectionEngine()
        self.webhook_handler = WebhookHandler()
        
        # Performance metrics
        self.metrics = {
            "payments_processed": 0,
            "total_revenue": Decimal("0.00"),
            "fraud_detected": 0,
            "payouts_completed": 0
        }
        
    def _initialize_processors(self) -> Dict[str, Any]:
        """Initialize payment processors based on configuration."""
        processors = {}
        
        if "stripe" in self.config.providers:
            processors["stripe"] = StripeProcessor(
                api_key=self.config.providers["stripe"]["api_key"],
                webhook_secret=self.config.providers["stripe"].get("webhook_secret")
            )
            
        if "wise" in self.config.providers:
            processors["wise"] = WiseProcessor(
                api_key=self.config.providers["wise"]["api_key"],
                profile_id=self.config.providers["wise"]["profile_id"]
            )
            
        if "paypal" in self.config.providers:
            processors["paypal"] = PayPalProcessor(
                client_id=self.config.providers["paypal"]["client_id"],
                client_secret=self.config.providers["paypal"]["client_secret"]
            )
            
        if "crypto" in self.config.providers:
            processors["crypto"] = CryptoProcessor(
                network_configs=self.config.providers["crypto"]
            )
            
        return processors

    async def process_content_revenue(
        self,
        creator_id: str,
        content_id: str,
        amount: Union[Decimal, float],
        currency: str = "EUR",
        source: str = "platform_revenue",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentTransaction:
        """
        Process revenue from content monetization.
        
        Args:
            creator_id: Creator account identifier
            content_id: Content being monetized
            amount: Revenue amount
            currency: Currency code (EUR, USD, etc.)
            source: Revenue source (spotify_royalties, youtube_ads, etc.)
            metadata: Additional transaction metadata
            
        Returns:
            PaymentTransaction: Processed transaction record
            
        Raises:
            PaymentProcessingError: If processing fails
        """
        try:
            # Validate inputs
            amount = Decimal(str(amount)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            await self.validator.validate_revenue_processing(
                creator_id, content_id, amount, currency
            )
            
            # Check for fraud indicators
            fraud_score = await self.fraud_detector.analyze_revenue(
                creator_id=creator_id,
                amount=amount,
                source=source,
                metadata=metadata or {}
            )
            
            if fraud_score > self.config.fraud_threshold:
                raise FraudDetectedError(
                    f"High fraud risk detected: {fraud_score:.2f}"
                )
            
            # Calculate fees and taxes
            fees = await self._calculate_platform_fees(amount, currency)
            taxes = await self.compliance.calculate_taxes(
                creator_id, amount, currency
            )
            
            net_amount = amount - fees - taxes
            
            # Create transaction record
            transaction = PaymentTransaction(
                id=str(uuid4()),
                creator_id=creator_id,
                content_id=content_id,
                transaction_type="revenue",
                amount=amount,
                currency=currency,
                fees=fees,
                taxes=taxes,
                net_amount=net_amount,
                source=source,
                status="completed",
                fraud_score=fraud_score,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.db_session:
                self.db_session.add(transaction)
                self.db_session.commit()
            
            # Update metrics
            self.metrics["payments_processed"] += 1
            self.metrics["total_revenue"] += amount
            
            # Log transaction
            logger.info(
                f"Revenue processed: {amount} {currency} for creator {creator_id}"
            )
            
            # Schedule payout if conditions met
            await self._check_payout_eligibility(creator_id)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Revenue processing failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to process revenue: {str(e)}")

    async def process_collaboration_payment(
        self,
        content_id: str,
        total_amount: Union[Decimal, float],
        splits: Dict[str, Union[int, float]],
        currency: str = "EUR",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[PaymentTransaction]:
        """
        Process split payment for content collaboration.
        
        Args:
            content_id: Content being monetized
            total_amount: Total revenue to split
            splits: Creator ID to percentage mapping
            currency: Currency code
            metadata: Additional metadata
            
        Returns:
            List[PaymentTransaction]: Transaction records for each creator
        """
        try:
            total_amount = Decimal(str(total_amount)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            # Validate split percentages
            total_percentage = sum(splits.values())
            if abs(total_percentage - 100) > 0.01:
                raise PaymentProcessingError(
                    f"Split percentages must sum to 100%, got {total_percentage}%"
                )
            
            transactions = []
            
            for creator_id, percentage in splits.items():
                creator_amount = (total_amount * Decimal(str(percentage)) / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                
                transaction = await self.process_content_revenue(
                    creator_id=creator_id,
                    content_id=content_id,
                    amount=creator_amount,
                    currency=currency,
                    source="collaboration_split",
                    metadata={
                        **(metadata or {}),
                        "collaboration_id": content_id,
                        "split_percentage": percentage,
                        "total_amount": str(total_amount)
                    }
                )
                
                transactions.append(transaction)
            
            logger.info(
                f"Collaboration payment processed: {total_amount} {currency} "
                f"split among {len(splits)} creators"
            )
            
            return transactions
            
        except Exception as e:
            logger.error(f"Collaboration payment failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to process collaboration: {str(e)}")

    async def schedule_payout(
        self,
        creator_id: str,
        amount: Optional[Union[Decimal, float]] = None,
        method: str = "stripe_bank_transfer",
        currency: str = "EUR",
        scheduled_date: Optional[datetime] = None
    ) -> PayoutSchedule:
        """
        Schedule payout to creator's payment method.
        
        Args:
            creator_id: Creator account identifier
            amount: Amount to payout (None for all available balance)
            method: Payment method identifier
            currency: Currency code
            scheduled_date: When to execute payout (None for immediate)
            
        Returns:
            PayoutSchedule: Scheduled payout record
        """
        try:
            # Get creator's available balance
            available_balance = await self._get_creator_balance(creator_id, currency)
            
            if amount is None:
                amount = available_balance
            else:
                amount = Decimal(str(amount)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            
            # Validate payout eligibility
            if amount < self.config.minimum_payout:
                raise PaymentProcessingError(
                    f"Amount {amount} below minimum payout {self.config.minimum_payout}"
                )
                
            if amount > available_balance:
                raise InsufficientFundsError(
                    f"Insufficient balance: {available_balance} available, {amount} requested"
                )
            
            # Get payment method
            payment_method = await self._get_payment_method(creator_id, method)
            if not payment_method:
                raise InvalidPaymentMethodError(f"Payment method {method} not found")
            
            # Create payout schedule
            payout = PayoutSchedule(
                id=str(uuid4()),
                creator_id=creator_id,
                amount=amount,
                currency=currency,
                payment_method=method,
                scheduled_date=scheduled_date or datetime.utcnow(),
                status="scheduled",
                metadata={
                    "balance_before": str(available_balance),
                    "payment_method_details": payment_method.to_dict()
                },
                created_at=datetime.utcnow()
            )
            
            # Save to database
            if self.db_session:
                self.db_session.add(payout)
                self.db_session.commit()
            
            # Execute immediately if no scheduled date
            if scheduled_date is None:
                await self._execute_payout(payout)
            else:
                # Add to scheduler queue
                await self.scheduler.schedule_payout(payout)
            
            logger.info(f"Payout scheduled: {amount} {currency} to creator {creator_id}")
            
            return payout
            
        except Exception as e:
            logger.error(f"Payout scheduling failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to schedule payout: {str(e)}")

    async def detect_fraud(
        self,
        transaction_id: Optional[str] = None,
        amount: Optional[Union[Decimal, float]] = None,
        user_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform fraud detection analysis on transaction or parameters.
        
        Args:
            transaction_id: Existing transaction to analyze
            amount: Transaction amount for analysis
            user_id: User account identifier
            payment_method: Payment method type
            metadata: Additional context data
            
        Returns:
            Dict with fraud analysis results
        """
        try:
            if transaction_id:
                # Analyze existing transaction
                transaction = await self._get_transaction(transaction_id)
                if not transaction:
                    raise PaymentProcessingError(f"Transaction {transaction_id} not found")
                
                fraud_analysis = await self.fraud_detector.analyze_transaction(transaction)
            else:
                # Analyze parameters
                fraud_analysis = await self.fraud_detector.analyze_parameters(
                    amount=amount,
                    user_id=user_id,
                    payment_method=payment_method,
                    metadata=metadata or {}
                )
            
            # Update fraud metrics
            if fraud_analysis["risk_level"] > self.config.fraud_threshold:
                self.metrics["fraud_detected"] += 1
            
            return fraud_analysis
            
        except Exception as e:
            logger.error(f"Fraud detection failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to detect fraud: {str(e)}")

    async def get_creator_revenue_analytics(
        self,
        creator_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """
        Get comprehensive revenue analytics for creator.
        
        Args:
            creator_id: Creator account identifier
            start_date: Analytics period start
            end_date: Analytics period end
            currency: Currency for calculations
            
        Returns:
            Dict with revenue analytics data
        """
        try:
            return await self.analytics.get_creator_analytics(
                creator_id=creator_id,
                start_date=start_date,
                end_date=end_date,
                currency=currency
            )
            
        except Exception as e:
            logger.error(f"Revenue analytics failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to get analytics: {str(e)}")

    async def generate_tax_report(
        self,
        creator_id: str,
        year: int,
        country: str = "DE"
    ) -> Dict[str, Any]:
        """
        Generate tax compliance report for creator.
        
        Args:
            creator_id: Creator account identifier
            year: Tax year
            country: Country code for tax rules
            
        Returns:
            Dict with tax report data
        """
        try:
            return await self.compliance.generate_tax_report(
                creator_id=creator_id,
                year=year,
                country=country
            )
            
        except Exception as e:
            logger.error(f"Tax report generation failed: {str(e)}")
            raise ComplianceError(f"Failed to generate tax report: {str(e)}")

    async def process_webhook(
        self,
        provider: str,
        event_type: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process payment provider webhook events.
        
        Args:
            provider: Payment provider name (stripe, wise, etc.)
            event_type: Webhook event type
            payload: Event payload
            signature: Webhook signature for verification
            
        Returns:
            Dict with processing results
        """
        try:
            return await self.webhook_handler.process_webhook(
                provider=provider,
                event_type=event_type,
                payload=payload,
                signature=signature
            )
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            raise PaymentProcessingError(f"Failed to process webhook: {str(e)}")

    # Private helper methods
    async def _calculate_platform_fees(
        self, 
        amount: Decimal, 
        currency: str
    ) -> Decimal:
        """Calculate platform fees for transaction."""
        fee_rate = self.config.platform_fee_rate
        min_fee = Decimal(str(self.config.minimum_fee))
        
        calculated_fee = (amount * Decimal(str(fee_rate)) / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return max(calculated_fee, min_fee)

    async def _get_creator_balance(self, creator_id: str, currency: str) -> Decimal:
        """
Get creator's available balance for payout."""
        if not self.db_session:
            return Decimal("0.00")
            
        # Sum completed revenues minus scheduled payouts
        revenue_sum = self.db_session.query(
            func.coalesce(func.sum(PaymentTransaction.net_amount), 0)
        ).filter(
            and_(
                PaymentTransaction.creator_id == creator_id,
                PaymentTransaction.currency == currency,
                PaymentTransaction.status == "completed"
            )
        ).scalar()
        
        payout_sum = self.db_session.query(
            func.coalesce(func.sum(PayoutSchedule.amount), 0)
        ).filter(
            and_(
                PayoutSchedule.creator_id == creator_id,
                PayoutSchedule.currency == currency,
                PayoutSchedule.status.in_(["scheduled", "processing", "completed"])
            )
        ).scalar()
        
        return Decimal(str(revenue_sum or 0)) - Decimal(str(payout_sum or 0))

    async def _get_payment_method(
        self, 
        creator_id: str, 
        method_id: str
    ) -> Optional[PaymentMethod]:
        """Get creator's payment method by ID."""
        if not self.db_session:
            return None
            
        return self.db_session.query(PaymentMethod).filter(
            and_(
                PaymentMethod.creator_id == creator_id,
                PaymentMethod.method_id == method_id,
                PaymentMethod.is_active == True
            )
        ).first()

    async def _get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """
Get transaction by ID."""
        if not self.db_session:
            return None
            
        return self.db_session.query(PaymentTransaction).filter(
            PaymentTransaction.id == transaction_id
        ).first()

    async def _check_payout_eligibility(self, creator_id: str):
        """
Check if creator is eligible for automatic payout."""
        balance = await self._get_creator_balance(creator_id, self.config.default_currency)
        
        if balance >= self.config.auto_payout_threshold:
            await self.schedule_payout(
                creator_id=creator_id,
                amount=balance,
                currency=self.config.default_currency
            )

    async def _execute_payout(self, payout: PayoutSchedule):
        """
Execute scheduled payout through payment processor."""
        try:
            # Get appropriate processor
            processor_name = payout.payment_method.split('_')[0]  # e.g., 'stripe' from 'stripe_bank_transfer'
            processor = self.processors.get(processor_name)
            
            if not processor:
                raise PaymentProcessingError(f"Processor {processor_name} not available")
            
            # Update status to processing
            payout.status = "processing"
            payout.processing_started_at = datetime.utcnow()
            
            if self.db_session:
                self.db_session.commit()
            
            # Execute payout through processor
            result = await processor.execute_payout(
                amount=payout.amount,
                currency=payout.currency,
                payment_method=payout.payment_method,
                recipient_id=payout.creator_id
            )
            
            # Update payout record with results
            payout.status = "completed" if result.get("success") else "failed"
            payout.external_id = result.get("transaction_id")
            payout.completed_at = datetime.utcnow()
            payout.metadata.update(result.get("metadata", {}))
            
            if self.db_session:
                self.db_session.commit()
            
            # Update metrics
            if payout.status == "completed":
                self.metrics["payouts_completed"] += 1
                
            logger.info(f"Payout executed: {payout.id} - Status: {payout.status}")
            
        except Exception as e:
            payout.status = "failed"
            payout.error_message = str(e)
            
            if self.db_session:
                self.db_session.commit()
                
            logger.error(f"Payout execution failed: {payout.id} - {str(e)}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics."""
        status = await super().get_status()
        
        status.update({
            "payment_processors": list(self.processors.keys()),
            "metrics": self.metrics,
            "config": {
                "minimum_payout": str(self.config.minimum_payout),
                "platform_fee_rate": self.config.platform_fee_rate,
                "fraud_threshold": self.config.fraud_threshold
            }
        })
        
        return status

    async def health_check(self) -> bool:
        """Perform health check on payment systems."""
        try:
            # Check database connection
            if self.db_session:
                self.db_session.execute("SELECT 1")
            
            # Check payment processors
            for name, processor in self.processors.items():
                if hasattr(processor, 'health_check'):
                    if not await processor.health_check():
                        logger.warning(f"Payment processor {name} failed health check")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
