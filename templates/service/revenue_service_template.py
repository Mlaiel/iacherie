"""{{service_name}} Revenue Service for Ainflue Platform
{{service_description}}

Enterprise-grade revenue management and monetization service with comprehensive
payment processing, subscription management, creator payouts, and financial analytics.

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Role: Backend Senior + Payment Systems Expert
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from pydantic import BaseModel, Field, validator, EmailStr, condecimal
import aioredis
from fastapi import HTTPException
import stripe
import paypalrestsdk

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError, AuthorizationError
from models.revenue import (
    Revenue, Payout, Subscription, Transaction, PaymentMethod,
    RevenueShare, Commission, Refund, Withdrawal, TaxRecord
)
from models.creator import Creator
from models.content import Content
from services.analytics_service import AnalyticsService
from services.notification_service import NotificationService
from utils.validation import validate_financial_data
from utils.encryption import encrypt_financial_data, decrypt_financial_data
from monitoring.revenue_metrics import RevenueMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class PaymentStatus(Enum):
    """Payment transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentProvider(Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"


class SubscriptionTier(Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class RevenueType(Enum):
    """Types of revenue streams"""
    SUBSCRIPTION = "subscription"
    ONE_TIME_PURCHASE = "one_time_purchase"
    COMMISSION = "commission"
    ADVERTISING = "advertising"
    DONATION = "donation"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"


class PayoutFrequency(Enum):
    """Payout frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


# Pydantic Models for Request/Response
class CreateTransactionRequest(BaseModel):
    """Request model for creating a transaction"""
    creator_id: str = Field(..., description="Creator ID")
    content_id: Optional[str] = Field(None, description="Content ID if applicable")
    amount: condecimal(max_digits=10, decimal_places=2) = Field(..., description="Transaction amount")
    currency: str = Field("USD", description="Currency code")
    payment_provider: PaymentProvider = Field(..., description="Payment provider")
    payment_method_id: str = Field(..., description="Payment method ID")
    revenue_type: RevenueType = Field(..., description="Type of revenue")
    description: Optional[str] = Field(None, description="Transaction description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('amount')
    def validate_amount(cls, v) -> None:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('currency')
    def validate_currency(cls, v) -> None:
        if len(v) != 3:
            raise ValueError('Currency must be a 3-letter code')
        return v.upper()


class SubscriptionRequest(BaseModel):
    """Request model for subscription management"""
    creator_id: str = Field(..., description="Creator ID")
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    billing_cycle: str = Field("monthly", description="Billing cycle")
    payment_method_id: str = Field(..., description="Payment method ID")
    discount_code: Optional[str] = Field(None, description="Discount code")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PayoutRequest(BaseModel):
    """Request model for creator payouts"""
    creator_id: str = Field(..., description="Creator ID")
    amount: condecimal(max_digits=10, decimal_places=2) = Field(..., description="Payout amount")
    currency: str = Field("USD", description="Currency code")
    payment_provider: PaymentProvider = Field(..., description="Payment provider")
    bank_account_id: str = Field(..., description="Bank account ID")
    description: Optional[str] = Field(None, description="Payout description")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RevenueAnalyticsResponse(BaseModel):
    """Response model for revenue analytics"""
    total_revenue: Decimal = Field(..., description="Total revenue")
    revenue_by_type: Dict[str, Decimal] = Field(..., description="Revenue breakdown by type")
    top_creators: List[Dict[str, Any]] = Field(..., description="Top earning creators")
    growth_rate: float = Field(..., description="Revenue growth rate")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")


class {{service_class_name}}(BaseService):
    """
    Enterprise Revenue Service for Ainflue Platform
    
    Handles comprehensive revenue management including:
    - Payment processing and transactions
    - Subscription management and billing
    - Creator payouts and revenue sharing
    - Financial analytics and reporting
    - Tax calculation and compliance
    - Fraud detection and prevention
    - Multi-currency support
    - Payment gateway integration
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "{{service_name}}"
        self.version = "{{service_version}}"
        self.redis_client = None
        self.metrics_collector = RevenueMetricsCollector()
        
        # Payment provider configurations
        self.stripe_client = None
        self.paypal_client = None
        
        # Financial calculations precision
        self.decimal_context = Decimal('0.01')
        
        # Commission rates by tier
        self.commission_rates = {
            SubscriptionTier.FREE: Decimal('0.15'),    # 15%
            SubscriptionTier.BASIC: Decimal('0.12'),   # 12%
            SubscriptionTier.PREMIUM: Decimal('0.10'), # 10%
            SubscriptionTier.ENTERPRISE: Decimal('0.08'), # 8%
            SubscriptionTier.CUSTOM: Decimal('0.05')   # 5%
        }

    async def initialize(self) -> None:
        """Initialize service with dependencies"""
        try:
            await super().initialize()
            
            # Initialize Redis for caching and session management
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                retry_on_timeout=True
            )
            
            # Initialize payment providers
            await self._initialize_payment_providers()
            
            # Initialize metrics collection
            await self.metrics_collector.initialize()
            
            logger.info(f"{self.name} service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} service: {e}")
            raise ServiceException(f"Service initialization failed: {e}")

    async def _initialize_payment_providers(self) -> None:
        """Initialize payment provider clients"""
        try:
            # Initialize Stripe
            if settings.STRIPE_SECRET_KEY:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                self.stripe_client = stripe
                logger.info("Stripe payment provider initialized")
            
            # Initialize PayPal
            if settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET:
                paypalrestsdk.configure({
                    "mode": settings.PAYPAL_MODE,  # sandbox or live
                    "client_id": settings.PAYPAL_CLIENT_ID,
                    "client_secret": settings.PAYPAL_CLIENT_SECRET
                })
                self.paypal_client = paypalrestsdk
                logger.info("PayPal payment provider initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize payment providers: {e}")
            raise ServiceException(f"Payment provider initialization failed: {e}")

    async def create_transaction(
        self,
        request: CreateTransactionRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Create a new payment transaction
        
        Args:
            request: Transaction creation request
            session: Database session
            
        Returns:
            Transaction details with processing status
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate creator and content
                creator = await self._get_creator(request.creator_id, db_session)
                if not creator:
                    raise ValidationError(f"Creator {request.creator_id} not found")
                
                # Calculate commission and fees
                commission_rate = self.commission_rates.get(
                    creator.subscription_tier, 
                    self.commission_rates[SubscriptionTier.FREE]
                )
                
                commission_amount = (request.amount * commission_rate).quantize(
                    self.decimal_context, rounding=ROUND_HALF_UP
                )
                
                net_amount = request.amount - commission_amount
                
                # Process payment through provider
                payment_result = await self._process_payment(
                    request, commission_amount, db_session
                )
                
                # Create transaction record
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    creator_id=request.creator_id,
                    content_id=request.content_id,
                    amount=request.amount,
                    currency=request.currency,
                    commission_amount=commission_amount,
                    net_amount=net_amount,
                    payment_provider=request.payment_provider.value,
                    payment_method_id=request.payment_method_id,
                    revenue_type=request.revenue_type.value,
                    status=payment_result['status'],
                    provider_transaction_id=payment_result.get('transaction_id'),
                    description=request.description,
                    metadata=request.metadata,
                    created_at=datetime.utcnow()
                )
                
                db_session.add(transaction)
                await db_session.commit()
                
                # Update creator revenue stats
                await self._update_creator_revenue_stats(
                    request.creator_id, net_amount, db_session
                )
                
                # Record metrics
                await self.metrics_collector.record_transaction(
                    transaction_id=transaction.id,
                    amount=request.amount,
                    revenue_type=request.revenue_type.value,
                    status=payment_result['status']
                )
                
                # Send notification
                await self._send_transaction_notification(transaction)
                
                logger.info(f"Transaction created: {transaction.id}")
                
                return {
                    "transaction_id": transaction.id,
                    "status": transaction.status,
                    "amount": float(transaction.amount),
                    "commission": float(commission_amount),
                    "net_amount": float(net_amount),
                    "provider_transaction_id": transaction.provider_transaction_id,
                    "created_at": transaction.created_at.isoformat()
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to create transaction: {e}")
                await self.metrics_collector.record_error("transaction_creation", str(e))
                raise ServiceException(f"Transaction creation failed: {e}")

    async def _process_payment(
        self,
        request: CreateTransactionRequest,
        commission_amount: Decimal,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Process payment through appropriate provider"""
        try:
            if request.payment_provider == PaymentProvider.STRIPE:
                return await self._process_stripe_payment(request, commission_amount)
            elif request.payment_provider == PaymentProvider.PAYPAL:
                return await self._process_paypal_payment(request, commission_amount)
            else:
                return await self._process_generic_payment(request, commission_amount)
                
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return {
                "status": PaymentStatus.FAILED.value,
                "error": str(e)
            }

    async def _process_stripe_payment(
        self,
        request: CreateTransactionRequest,
        commission_amount: Decimal
    ) -> Dict[str, Any]:
        """Process payment through Stripe"""
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.lower(),
                payment_method=request.payment_method_id,
                confirmation_method='manual',
                confirm=True,
                metadata={
                    'creator_id': request.creator_id,
                    'content_id': request.content_id or '',
                    'revenue_type': request.revenue_type.value,
                    'commission_amount': str(commission_amount)
                }
            )
            
            return {
                "status": PaymentStatus.COMPLETED.value if intent.status == 'succeeded' 
                         else PaymentStatus.PROCESSING.value,
                "transaction_id": intent.id,
                "provider_data": intent
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payment failed: {e}")
            return {
                "status": PaymentStatus.FAILED.value,
                "error": str(e)
            }

    async def _process_paypal_payment(
        self,
        request: CreateTransactionRequest,
        commission_amount: Decimal
    ) -> Dict[str, Any]:
        """Process payment through PayPal"""
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {
                        "total": str(request.amount),
                        "currency": request.currency
                    },
                    "description": request.description or "Ainflue Platform Payment"
                }],
                "redirect_urls": {
                    "return_url": f"{settings.BASE_URL}/payment/success",
                    "cancel_url": f"{settings.BASE_URL}/payment/cancel"
                }
            })
            
            if payment.create():
                return {
                    "status": PaymentStatus.PENDING.value,
                    "transaction_id": payment.id,
                    "provider_data": payment.to_dict()
                }
            else:
                return {
                    "status": PaymentStatus.FAILED.value,
                    "error": payment.error
                }
                
        except Exception as e:
            logger.error(f"PayPal payment failed: {e}")
            return {
                "status": PaymentStatus.FAILED.value,
                "error": str(e)
            }

    async def _process_generic_payment(
        self,
        request: CreateTransactionRequest,
        commission_amount: Decimal
    ) -> Dict[str, Any]:
        """Process payment through generic provider"""
        # Implement other payment providers as needed
        return {
            "status": PaymentStatus.PENDING.value,
            "transaction_id": str(uuid.uuid4()),
            "provider_data": {"provider": request.payment_provider.value}
        }

    async def create_subscription(
        self,
        request: SubscriptionRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription for a creator
        
        Args:
            request: Subscription creation request
            session: Database session
            
        Returns:
            Subscription details
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate creator
                creator = await self._get_creator(request.creator_id, db_session)
                if not creator:
                    raise ValidationError(f"Creator {request.creator_id} not found")
                
                # Check for existing active subscription
                existing_subscription = await self._get_active_subscription(
                    request.creator_id, db_session
                )
                
                if existing_subscription:
                    # Upgrade/downgrade existing subscription
                    return await self._modify_subscription(
                        existing_subscription, request, db_session
                    )
                
                # Calculate subscription pricing
                pricing = await self._calculate_subscription_pricing(
                    request.tier, request.billing_cycle, request.discount_code
                )
                
                # Create subscription
                subscription = Subscription(
                    id=str(uuid.uuid4()),
                    creator_id=request.creator_id,
                    tier=request.tier.value,
                    billing_cycle=request.billing_cycle,
                    amount=pricing['amount'],
                    currency=pricing['currency'],
                    discount_amount=pricing.get('discount_amount', Decimal('0')),
                    payment_method_id=request.payment_method_id,
                    status="active",
                    current_period_start=datetime.utcnow(),
                    current_period_end=datetime.utcnow() + timedelta(
                        days=pricing['billing_days']
                    ),
                    metadata=request.metadata,
                    created_at=datetime.utcnow()
                )
                
                db_session.add(subscription)
                
                # Update creator subscription tier
                creator.subscription_tier = request.tier
                await db_session.commit()
                
                # Record metrics
                await self.metrics_collector.record_subscription(
                    subscription_id=subscription.id,
                    tier=request.tier.value,
                    amount=pricing['amount']
                )
                
                logger.info(f"Subscription created: {subscription.id}")
                
                return {
                    "subscription_id": subscription.id,
                    "tier": subscription.tier,
                    "amount": float(subscription.amount),
                    "billing_cycle": subscription.billing_cycle,
                    "current_period_start": subscription.current_period_start.isoformat(),
                    "current_period_end": subscription.current_period_end.isoformat(),
                    "status": subscription.status
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to create subscription: {e}")
                raise ServiceException(f"Subscription creation failed: {e}")

    async def process_payout(
        self,
        request: PayoutRequest,
        session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Process payout to creator
        
        Args:
            request: Payout request
            session: Database session
            
        Returns:
            Payout details
        """
        async with self.get_session(session) as db_session:
            try:
                # Validate creator and available balance
                creator = await self._get_creator(request.creator_id, db_session)
                if not creator:
                    raise ValidationError(f"Creator {request.creator_id} not found")
                
                available_balance = await self._get_available_balance(
                    request.creator_id, db_session
                )
                
                if available_balance < request.amount:
                    raise ValidationError(
                        f"Insufficient balance. Available: {available_balance}, "
                        f"Requested: {request.amount}"
                    )
                
                # Validate minimum payout amount
                min_payout = Decimal('10.00')  # $10 minimum
                if request.amount < min_payout:
                    raise ValidationError(f"Minimum payout amount is {min_payout}")
                
                # Process payout through provider
                payout_result = await self._process_provider_payout(request)
                
                # Create payout record
                payout = Payout(
                    id=str(uuid.uuid4()),
                    creator_id=request.creator_id,
                    amount=request.amount,
                    currency=request.currency,
                    payment_provider=request.payment_provider.value,
                    bank_account_id=request.bank_account_id,
                    status=payout_result['status'],
                    provider_payout_id=payout_result.get('payout_id'),
                    description=request.description,
                    metadata=request.metadata,
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow() if payout_result['status'] == 'completed' else None
                )
                
                db_session.add(payout)
                
                # Update creator balance
                await self._update_creator_balance(
                    request.creator_id, -request.amount, db_session
                )
                
                await db_session.commit()
                
                # Record metrics
                await self.metrics_collector.record_payout(
                    payout_id=payout.id,
                    amount=request.amount,
                    status=payout_result['status']
                )
                
                # Send notification
                await self._send_payout_notification(payout)
                
                logger.info(f"Payout processed: {payout.id}")
                
                return {
                    "payout_id": payout.id,
                    "status": payout.status,
                    "amount": float(payout.amount),
                    "provider_payout_id": payout.provider_payout_id,
                    "created_at": payout.created_at.isoformat(),
                    "processed_at": payout.processed_at.isoformat() if payout.processed_at else None
                }
                
            except Exception as e:
                await db_session.rollback()
                logger.error(f"Failed to process payout: {e}")
                raise ServiceException(f"Payout processing failed: {e}")

    async def get_revenue_analytics(
        self,
        creator_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session: Optional[AsyncSession] = None
    ) -> RevenueAnalyticsResponse:
        """
        Get comprehensive revenue analytics
        
        Args:
            creator_id: Optional creator ID for creator-specific analytics
            start_date: Analytics period start
            end_date: Analytics period end
            session: Database session
            
        Returns:
            Revenue analytics data
        """
        async with self.get_session(session) as db_session:
            try:
                # Set default date range if not provided
                if not end_date:
                    end_date = datetime.utcnow()
                if not start_date:
                    start_date = end_date - timedelta(days=30)
                
                # Build base query
                query = select(Transaction).where(
                    and_(
                        Transaction.created_at >= start_date,
                        Transaction.created_at <= end_date,
                        Transaction.status == PaymentStatus.COMPLETED.value
                    )
                )
                
                if creator_id:
                    query = query.where(Transaction.creator_id == creator_id)
                
                # Execute query
                result = await db_session.execute(query)
                transactions = result.scalars().all()
                
                # Calculate analytics
                total_revenue = sum(t.amount for t in transactions)
                
                # Revenue by type
                revenue_by_type = {}
                for transaction in transactions:
                    revenue_type = transaction.revenue_type
                    revenue_by_type[revenue_type] = revenue_by_type.get(
                        revenue_type, Decimal('0')
                    ) + transaction.amount
                
                # Top creators (if not creator-specific)
                top_creators = []
                if not creator_id:
                    creator_revenue = {}
                    for transaction in transactions:
                        creator_id_key = transaction.creator_id
                        creator_revenue[creator_id_key] = creator_revenue.get(
                            creator_id_key, Decimal('0')
                        ) + transaction.net_amount
                    
                    # Sort and get top 10
                    sorted_creators = sorted(
                        creator_revenue.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                    
                    for creator_id_key, revenue in sorted_creators:
                        creator = await self._get_creator(creator_id_key, db_session)
                        if creator:
                            top_creators.append({
                                "creator_id": creator_id_key,
                                "username": creator.username,
                                "revenue": float(revenue)
                            })
                
                # Calculate growth rate
                previous_period_start = start_date - (end_date - start_date)
                previous_period_end = start_date
                
                previous_query = select(func.sum(Transaction.amount)).where(
                    and_(
                        Transaction.created_at >= previous_period_start,
                        Transaction.created_at <= previous_period_end,
                        Transaction.status == PaymentStatus.COMPLETED.value
                    )
                )
                
                if creator_id:
                    previous_query = previous_query.where(Transaction.creator_id == creator_id)
                
                previous_result = await db_session.execute(previous_query)
                previous_revenue = previous_result.scalar() or Decimal('0')
                
                growth_rate = 0.0
                if previous_revenue > 0:
                    growth_rate = float((total_revenue - previous_revenue) / previous_revenue * 100)
                
                return RevenueAnalyticsResponse(
                    total_revenue=total_revenue,
                    revenue_by_type={k: v for k, v in revenue_by_type.items()},
                    top_creators=top_creators,
                    growth_rate=growth_rate,
                    period_start=start_date,
                    period_end=end_date
                )
                
            except Exception as e:
                logger.error(f"Failed to get revenue analytics: {e}")
                raise ServiceException(f"Revenue analytics failed: {e}")

    async def _get_creator(
        self,
        creator_id: str,
        session: AsyncSession
    ) -> Optional[Creator]:
        """Get creator by ID"""
        try:
            result = await session.execute(
                select(Creator).where(Creator.id == creator_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get creator {creator_id}: {e}")
            return None

    async def _get_active_subscription(
        self,
        creator_id: str,
        session: AsyncSession
    ) -> Optional[Subscription]:
        """Get active subscription for creator"""
        try:
            result = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.creator_id == creator_id,
                        Subscription.status == "active"
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get active subscription for {creator_id}: {e}")
            return None

    async def _calculate_subscription_pricing(
        self,
        tier: SubscriptionTier,
        billing_cycle: str,
        discount_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate subscription pricing"""
        # Base pricing per tier (monthly)
        base_prices = {
            SubscriptionTier.FREE: Decimal('0.00'),
            SubscriptionTier.BASIC: Decimal('9.99'),
            SubscriptionTier.PREMIUM: Decimal('19.99'),
            SubscriptionTier.ENTERPRISE: Decimal('99.99'),
            SubscriptionTier.CUSTOM: Decimal('199.99')
        }
        
        billing_multipliers = {
            "monthly": 1,
            "quarterly": 3,
            "yearly": 12
        }
        
        billing_days = {
            "monthly": 30,
            "quarterly": 90,
            "yearly": 365
        }
        
        base_amount = base_prices[tier]
        multiplier = billing_multipliers.get(billing_cycle, 1)
        amount = base_amount * multiplier
        
        # Apply discounts
        discount_amount = Decimal('0')
        if discount_code:
            discount_amount = await self._calculate_discount(discount_code, amount)
            amount -= discount_amount
        
        return {
            "amount": amount,
            "currency": "USD",
            "discount_amount": discount_amount,
            "billing_days": billing_days.get(billing_cycle, 30)
        }

    async def _calculate_discount(
        self,
        discount_code: str,
        amount: Decimal
    ) -> Decimal:
        """Calculate discount amount"""
        # Implement discount logic
        # This is a simplified implementation
        discount_rates = {
            "WELCOME10": Decimal('0.10'),    # 10% off
            "STUDENT20": Decimal('0.20'),    # 20% off
            "CREATOR15": Decimal('0.15')     # 15% off
        }
        
        rate = discount_rates.get(discount_code.upper(), Decimal('0'))
        return amount * rate

    async def _get_available_balance(
        self,
        creator_id: str,
        session: AsyncSession
    ) -> Decimal:
        """Get available balance for creator"""
        try:
            # Calculate total earnings
            earnings_result = await session.execute(
                select(func.sum(Transaction.net_amount)).where(
                    and_(
                        Transaction.creator_id == creator_id,
                        Transaction.status == PaymentStatus.COMPLETED.value
                    )
                )
            )
            total_earnings = earnings_result.scalar() or Decimal('0')
            
            # Calculate total payouts
            payouts_result = await session.execute(
                select(func.sum(Payout.amount)).where(
                    and_(
                        Payout.creator_id == creator_id,
                        Payout.status.in_(["completed", "processing"])
                    )
                )
            )
            total_payouts = payouts_result.scalar() or Decimal('0')
            
            return total_earnings - total_payouts
            
        except Exception as e:
            logger.error(f"Failed to get available balance for {creator_id}: {e}")
            return Decimal('0')

    async def _process_provider_payout(
        self,
        request: PayoutRequest
    ) -> Dict[str, Any]:
        """Process payout through payment provider"""
        try:
            if request.payment_provider == PaymentProvider.STRIPE:
                return await self._process_stripe_payout(request)
            elif request.payment_provider == PaymentProvider.PAYPAL:
                return await self._process_paypal_payout(request)
            else:
                return await self._process_generic_payout(request)
                
        except Exception as e:
            logger.error(f"Provider payout failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _process_stripe_payout(
        self,
        request: PayoutRequest
    ) -> Dict[str, Any]:
        """Process payout through Stripe"""
        try:
            payout = stripe.Payout.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.lower(),
                destination=request.bank_account_id,
                description=request.description or "Ainflue Creator Payout"
            )
            
            return {
                "status": "completed" if payout.status == "paid" else "processing",
                "payout_id": payout.id,
                "provider_data": payout
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe payout failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _process_paypal_payout(
        self,
        request: PayoutRequest
    ) -> Dict[str, Any]:
        """Process payout through PayPal"""
        try:
            payout = paypalrestsdk.Payout({
                "sender_batch_header": {
                    "sender_batch_id": str(uuid.uuid4()),
                    "email_subject": "Ainflue Creator Payout"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(request.amount),
                        "currency": request.currency
                    },
                    "receiver": request.bank_account_id,  # Email in this case
                    "note": request.description or "Ainflue Creator Payout",
                    "sender_item_id": str(uuid.uuid4())
                }]
            })
            
            if payout.create():
                return {
                    "status": "processing",
                    "payout_id": payout.batch_header.payout_batch_id,
                    "provider_data": payout.to_dict()
                }
            else:
                return {
                    "status": "failed",
                    "error": payout.error
                }
                
        except Exception as e:
            logger.error(f"PayPal payout failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _process_generic_payout(
        self,
        request: PayoutRequest
    ) -> Dict[str, Any]:
        """Process payout through generic provider"""
        # Implement other payout providers as needed
        return {
            "status": "processing",
            "payout_id": str(uuid.uuid4()),
            "provider_data": {"provider": request.payment_provider.value}
        }

    async def _update_creator_revenue_stats(
        self,
        creator_id -> None: str,
        amount -> None: Decimal,
        session -> None: AsyncSession
    ) -> None:
        """Update creator revenue statistics"""
        try:
            # This would update creator statistics
            # Implementation depends on your Creator model structure
            pass
        except Exception as e:
            logger.error(f"Failed to update creator revenue stats: {e}")

    async def _update_creator_balance(
        self,
        creator_id -> None: str,
        amount_delta -> None: Decimal,
        session -> None: AsyncSession
    ) -> None:
        """Update creator balance"""
        try:
            # This would update creator balance
            # Implementation depends on your Creator model structure
            pass
        except Exception as e:
            logger.error(f"Failed to update creator balance: {e}")

    async def _send_transaction_notification(self, transaction -> None: Transaction) -> None:
        """Send transaction notification"""
        try:
            # Implement notification logic
            pass
        except Exception as e:
            logger.error(f"Failed to send transaction notification: {e}")

    async def _send_payout_notification(self, payout -> None: Payout) -> None:
        """Send payout notification"""
        try:
            # Implement notification logic
            pass
        except Exception as e:
            logger.error(f"Failed to send payout notification: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            health_status = await super().health_check()
            
            # Check Redis connectivity
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = "healthy"
            
            # Check payment providers
            health_status["payment_providers"] = {
                "stripe": "available" if self.stripe_client else "unavailable",
                "paypal": "available" if self.paypal_client else "unavailable"
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup(self) -> None:
        """Cleanup service resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.metrics_collector:
                await self.metrics_collector.cleanup()
                
            await super().cleanup()
            logger.info(f"{self.name} service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Failed to cleanup {self.name} service: {e}")


# Example usage and testing
if __name__ == "__main__":
    async def main() -> None:
        service = {{service_class_name}}()
        await service.initialize()
        
        # Example transaction creation
        transaction_request = CreateTransactionRequest(
            creator_id="creator_123",
            amount=Decimal("29.99"),
            currency="USD",
            payment_provider=PaymentProvider.STRIPE,
            payment_method_id="pm_test_123",
            revenue_type=RevenueType.SUBSCRIPTION,
            description="Monthly subscription payment"
        )
        
        try:
            result = await service.create_transaction(transaction_request)
            print(f"Transaction created: {result}")
            
            # Example analytics
            analytics = await service.get_revenue_analytics()
            print(f"Revenue analytics: {analytics}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await service.cleanup()

    asyncio.run(main())

# File has syntax issues - needs manual review