"""Subscription Manager - Client subscription and billing management.

Handles subscription tiers, billing cycles, payment processing,
and feature access control for IA Influencer platform creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import logging
from enum import Enum
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator

from ...core.database import get_db
from ...core.exceptions import (
    SubscriptionNotFoundError,
    PaymentError,
    SubscriptionServiceError
)
from ...models.subscription import (
    Subscription, SubscriptionTier, SubscriptionStatus, BillingCycle
)
from ...models.payment import Payment, PaymentStatus, PaymentMethod
from ...services.payment.stripe_service import StripePaymentService
from ...services.payment.paypal_service import PayPalPaymentService
from ...services.notification.email import EmailService
from ...services.analytics.billing import BillingAnalytics


logger = logging.getLogger(__name__)


class SubscriptionPlan(str, Enum):
    """
Available subscription plans."""

    FREE = "free"
    CREATOR = "creator"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PaymentProvider(str, Enum):
    """Supported payment providers."""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"


class SubscriptionCreateData(BaseModel):
    """Subscription creation data."""
    plan: SubscriptionPlan
    billing_cycle: BillingCycle
    payment_method_id: Optional[str] = None
    coupon_code: Optional[str] = None
    auto_renewal: bool = True
    
    @validator('plan')
    def validate_plan(cls, v):
        if v == SubscriptionPlan.FREE:
            return v
        # For paid plans, we'll need payment method
        return v


class PaymentMethodData(BaseModel):
    """
Payment method data for subscription."""
    provider: PaymentProvider
    token: str  # Payment provider token
    billing_address: Dict[str, str]
    is_default: bool = True


class UsageMetrics(BaseModel):
    """
Current period usage metrics."""
    content_uploads: int = 0
    storage_used_gb: Decimal = Decimal('0')
    fingerprints_created: int = 0
    api_calls: int = 0
    collaborations: int = 0


class SubscriptionManager:
    """
    Comprehensive subscription management system.
    
    Features:
    - Multi-tier subscription plans
    - Flexible billing cycles
    - Multiple payment providers
    - Usage tracking and limits
    - Feature access control
    - Automatic renewals
    - Upgrade/downgrade handling
    - Billing analytics integration
    """
    
    def __init__(
        self,
        db: Session,
        stripe_service: StripePaymentService,
        paypal_service: PayPalPaymentService,
        email_service: EmailService,
        billing_analytics: BillingAnalytics
    ):
        self.db = db
        self.stripe_service = stripe_service
        self.paypal_service = paypal_service
        self.email_service = email_service
        self.billing_analytics = billing_analytics
        
        # Subscription plan configurations
        self.plan_config = {
            SubscriptionPlan.FREE: {
                "monthly_price": Decimal('0.00'),
                "yearly_price": Decimal('0.00'),
                "limits": {
                    "content_uploads_per_month": 5,
                    "storage_gb": 1,
                    "fingerprints_per_month": 10,
                    "api_calls_per_month": 1000,
                    "collaborations_per_month": 1
                },
                "features": [
                    "basic_content_protection",
                    "manual_fingerprinting",
                    "basic_analytics"
                ]
            },
            SubscriptionPlan.CREATOR: {
                "monthly_price": Decimal('29.99'),
                "yearly_price": Decimal('299.99'),
                "limits": {
                    "content_uploads_per_month": 100,
                    "storage_gb": 50,
                    "fingerprints_per_month": 500,
                    "api_calls_per_month": 50000,
                    "collaborations_per_month": 10
                },
                "features": [
                    "advanced_content_protection",
                    "automated_fingerprinting",
                    "advanced_analytics",
                    "social_media_integration",
                    "email_support"
                ]
            },
            SubscriptionPlan.PROFESSIONAL: {
                "monthly_price": Decimal('99.99'),
                "yearly_price": Decimal('999.99'),
                "limits": {
                    "content_uploads_per_month": 500,
                    "storage_gb": 250,
                    "fingerprints_per_month": 2500,
                    "api_calls_per_month": 250000,
                    "collaborations_per_month": 50
                },
                "features": [
                    "premium_content_protection",
                    "real_time_monitoring",
                    "advanced_ai_analysis",
                    "custom_branding",
                    "priority_support",
                    "api_access"
                ]
            },
            SubscriptionPlan.ENTERPRISE: {
                "monthly_price": Decimal('299.99'),
                "yearly_price": Decimal('2999.99'),
                "limits": {
                    "content_uploads_per_month": -1,  # Unlimited
                    "storage_gb": 1000,
                    "fingerprints_per_month": -1,  # Unlimited
                    "api_calls_per_month": -1,  # Unlimited
                    "collaborations_per_month": -1  # Unlimited
                },
                "features": [
                    "enterprise_content_protection",
                    "dedicated_monitoring",
                    "custom_ai_models",
                    "white_label_solution",
                    "dedicated_support",
                    "full_api_access",
                    "custom_integrations"
                ]
            }
        }
        
    async def create_subscription(
        self,
        client_id: UUID,
        subscription_data: SubscriptionCreateData
    ) -> Dict[str, Any]:
        """
        Create new subscription for client.
        
        Args:
            client_id: Client identifier
            subscription_data: Subscription details
            
        Returns:
            Created subscription information
            
        Raises:
            PaymentError: If payment setup fails
        """
        try:
            # Check if client already has active subscription
            existing_subscription = self.db.query(Subscription).filter(
                Subscription.client_id == client_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if existing_subscription:
                raise SubscriptionServiceError("Client already has an active subscription")
                
            plan_config = self.plan_config[subscription_data.plan]
            
            # Calculate pricing based on billing cycle
            if subscription_data.billing_cycle == BillingCycle.MONTHLY:
                price = plan_config["monthly_price"]
            else:
                price = plan_config["yearly_price"]
                
            # Create subscription record
            subscription = Subscription(
                client_id=client_id,
                plan=SubscriptionTier(subscription_data.plan.value),
                billing_cycle=subscription_data.billing_cycle,
                price=price,
                currency="USD",
                status=SubscriptionStatus.PENDING,
                auto_renewal=subscription_data.auto_renewal,
                features=plan_config["features"],
                limits=plan_config["limits"],
                current_period_start=datetime.utcnow(),
                current_period_end=self._calculate_period_end(
                    datetime.utcnow(), subscription_data.billing_cycle
                )
            )
            
            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)
            
            # Handle payment for non-free plans
            if subscription_data.plan != SubscriptionPlan.FREE:
                if not subscription_data.payment_method_id:
                    raise PaymentError("Payment method required for paid plans")
                    
                payment_result = await self._process_initial_payment(
                    subscription, subscription_data.payment_method_id
                )
                
                if not payment_result["success"]:
                    subscription.status = SubscriptionStatus.PAYMENT_FAILED
                    self.db.commit()
                    raise PaymentError(f"Payment failed: {payment_result['error']}")
                    
            # Activate subscription
            subscription.status = SubscriptionStatus.ACTIVE
            if subscription_data.plan == SubscriptionPlan.FREE:
                subscription.activated_at = datetime.utcnow()
                
            self.db.commit()
            
            # Send confirmation email
            await self.email_service.send_subscription_confirmation(
                subscription.client.email,
                subscription.client.first_name,
                subscription_data.plan.value,
                price
            )
            
            # Track subscription creation
            await self.billing_analytics.track_subscription_event(
                client_id=client_id,
                event_type="subscription_created",
                plan=subscription_data.plan.value,
                amount=price
            )
            
            logger.info(f"Subscription created for client {client_id}: {subscription_data.plan.value}")
            
            return await self._format_subscription_data(subscription)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating subscription: {e}")
            raise SubscriptionServiceError("Failed to create subscription") from e
            
    async def get_subscription(self, client_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get current subscription for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Current subscription data or None
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.client_id == client_id,
                Subscription.status.in_([
                    SubscriptionStatus.ACTIVE,
                    SubscriptionStatus.PAST_DUE,
                    SubscriptionStatus.TRIAL
                ])
            ).first()
            
            if not subscription:
                return None
                
            return await self._format_subscription_data(subscription)
            
        except Exception as e:
            logger.error(f"Error retrieving subscription for client {client_id}: {e}")
            return None
            
    async def upgrade_subscription(
        self,
        client_id: UUID,
        new_plan: SubscriptionPlan,
        payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upgrade client subscription to higher tier.
        
        Args:
            client_id: Client identifier
            new_plan: New subscription plan
            payment_method_id: Payment method for upgrade
            
        Returns:
            Updated subscription information
        """
        try:
            current_subscription = self.db.query(Subscription).filter(
                Subscription.client_id == client_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if not current_subscription:
                raise SubscriptionNotFoundError("No active subscription found")
                
            current_plan = SubscriptionPlan(current_subscription.plan.value)
            
            # Validate upgrade path
            if not self._is_valid_upgrade(current_plan, new_plan):
                raise SubscriptionServiceError(f"Invalid upgrade from {current_plan.value} to {new_plan.value}")
                
            new_config = self.plan_config[new_plan]
            
            # Calculate prorated amount
            if current_subscription.billing_cycle == BillingCycle.MONTHLY:
                new_price = new_config["monthly_price"]
            else:
                new_price = new_config["yearly_price"]
                
            prorated_amount = await self._calculate_prorated_amount(
                current_subscription, new_price
            )
            
            # Process upgrade payment if needed
            if prorated_amount > 0 and payment_method_id:
                payment_result = await self._process_upgrade_payment(
                    current_subscription, prorated_amount, payment_method_id
                )
                
                if not payment_result["success"]:
                    raise PaymentError(f"Upgrade payment failed: {payment_result['error']}")
                    
            # Update subscription
            current_subscription.plan = SubscriptionTier(new_plan.value)
            current_subscription.price = new_price
            current_subscription.features = new_config["features"]
            current_subscription.limits = new_config["limits"]
            current_subscription.upgraded_at = datetime.utcnow()
            
            self.db.commit()
            
            # Send upgrade confirmation
            await self.email_service.send_subscription_upgrade_confirmation(
                current_subscription.client.email,
                current_subscription.client.first_name,
                new_plan.value,
                prorated_amount
            )
            
            # Track upgrade
            await self.billing_analytics.track_subscription_event(
                client_id=client_id,
                event_type="subscription_upgraded",
                plan=new_plan.value,
                amount=prorated_amount
            )
            
            logger.info(f"Subscription upgraded for client {client_id}: {current_plan.value} -> {new_plan.value}")
            
            return await self._format_subscription_data(current_subscription)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error upgrading subscription: {e}")
            raise SubscriptionServiceError("Failed to upgrade subscription") from e
            
    async def cancel_subscription(
        self,
        client_id: UUID,
        immediate: bool = False,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cancel client subscription.
        
        Args:
            client_id: Client identifier
            immediate: If True, cancel immediately; otherwise at period end
            reason: Cancellation reason
            
        Returns:
            Cancellation result
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.client_id == client_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
            
            if not subscription:
                raise SubscriptionNotFoundError("No active subscription found")
                
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                
                # Refund prorated amount if applicable
                refund_amount = await self._calculate_refund_amount(subscription)
                if refund_amount > 0:
                    await self._process_refund(subscription, refund_amount)
            else:
                subscription.cancel_at_period_end = True
                subscription.cancellation_reason = reason
                
            self.db.commit()
            
            # Send cancellation confirmation
            await self.email_service.send_subscription_cancellation_confirmation(
                subscription.client.email,
                subscription.client.first_name,
                immediate
            )
            
            # Track cancellation
            await self.billing_analytics.track_subscription_event(
                client_id=client_id,
                event_type="subscription_cancelled",
                plan=subscription.plan.value,
                reason=reason
            )
            
            logger.info(f"Subscription {'immediately ' if immediate else ''}cancelled for client {client_id}")
            
            return {
                "success": True,
                "cancelled_immediately": immediate,
                "active_until": subscription.current_period_end.isoformat() if not immediate else None
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error cancelling subscription: {e}")
            raise SubscriptionServiceError("Failed to cancel subscription") from e
            
    async def check_usage_limits(
        self,
        client_id: UUID,
        usage_type: str
    ) -> Dict[str, Any]:
        """
        Check if client has exceeded usage limits.
        
        Args:
            client_id: Client identifier
            usage_type: Type of usage to check
            
        Returns:
            Usage status and limits information
        """
        try:
            subscription = await self.get_subscription(client_id)
            if not subscription:
                return {"allowed": False, "reason": "No active subscription"}
                
            limits = subscription["limits"]
            current_usage = await self._get_current_usage(client_id)
            
            limit_key = f"{usage_type}_per_month"
            if limit_key not in limits:
                return {"allowed": True, "unlimited": True}
                
            limit_value = limits[limit_key]
            current_value = current_usage.get(usage_type, 0)
            
            # -1 means unlimited
            if limit_value == -1:
                return {"allowed": True, "unlimited": True}
                
            allowed = current_value < limit_value
            
            return {
                "allowed": allowed,
                "current_usage": current_value,
                "limit": limit_value,
                "remaining": max(0, limit_value - current_value),
                "percentage_used": (current_value / limit_value * 100) if limit_value > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            return {"allowed": False, "reason": "Error checking limits"}
            
    async def process_renewal(self, subscription_id: UUID) -> Dict[str, Any]:
        """
        Process subscription renewal payment.
        
        Args:
            subscription_id: Subscription identifier
            
        Returns:
            Renewal processing result
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            
            if not subscription:
                raise SubscriptionNotFoundError(f"Subscription not found: {subscription_id}")
                
            # Skip renewal for free plans
            if subscription.plan == SubscriptionTier.FREE:
                self._extend_subscription_period(subscription)
                return {"success": True, "amount": Decimal('0.00')}
                
            # Get default payment method
            payment_method = self.db.query(PaymentMethod).filter(
                PaymentMethod.client_id == subscription.client_id,
                PaymentMethod.is_default == True,
                PaymentMethod.is_active == True
            ).first()
            
            if not payment_method:
                subscription.status = SubscriptionStatus.PAST_DUE
                self.db.commit()
                
                await self.email_service.send_payment_method_required_email(
                    subscription.client.email,
                    subscription.client.first_name
                )
                
                return {"success": False, "error": "No valid payment method"}
                
            # Process renewal payment
            payment_result = await self._process_renewal_payment(subscription, payment_method)
            
            if payment_result["success"]:
                self._extend_subscription_period(subscription)
                
                await self.email_service.send_subscription_renewal_confirmation(
                    subscription.client.email,
                    subscription.client.first_name,
                    subscription.price
                )
                
                # Track renewal
                await self.billing_analytics.track_subscription_event(
                    client_id=subscription.client_id,
                    event_type="subscription_renewed",
                    plan=subscription.plan.value,
                    amount=subscription.price
                )
            else:
                subscription.status = SubscriptionStatus.PAST_DUE
                self.db.commit()
                
                await self.email_service.send_payment_failed_email(
                    subscription.client.email,
                    subscription.client.first_name,
                    payment_result["error"]
                )
                
            return payment_result
            
        except Exception as e:
            logger.error(f"Error processing renewal for subscription {subscription_id}: {e}")
            return {"success": False, "error": str(e)}
            
    def _calculate_period_end(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:
        """Calculate subscription period end date."""
        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.YEARLY:
            return start_date + timedelta(days=365)
        else:
            return start_date + timedelta(days=30)
            
    def _is_valid_upgrade(self, current_plan: SubscriptionPlan, new_plan: SubscriptionPlan) -> bool:
        """
Check if upgrade path is valid."""
        plan_hierarchy = [
            SubscriptionPlan.FREE,
            SubscriptionPlan.CREATOR,
            SubscriptionPlan.PROFESSIONAL,
            SubscriptionPlan.ENTERPRISE
        ]
        
        current_index = plan_hierarchy.index(current_plan)
        new_index = plan_hierarchy.index(new_plan)
        
        return new_index > current_index
        
    def _extend_subscription_period(self, subscription: Subscription) -> None:
        """
Extend subscription period for renewal."""
        subscription.current_period_start = subscription.current_period_end
        subscription.current_period_end = self._calculate_period_end(
            subscription.current_period_end,
            subscription.billing_cycle
        )
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.renewed_at = datetime.utcnow()
        self.db.commit()
        
    async def _get_current_usage(self, client_id: UUID) -> Dict[str, int]:
        """
Get current period usage metrics for client."""
        # Implementation would query usage from various services
        return {
            "content_uploads": 0,
            "storage_used_gb": 0,
            "fingerprints_created": 0,
            "api_calls": 0,
            "collaborations": 0
        }
        
    async def _format_subscription_data(self, subscription: Subscription) -> Dict[str, Any]:
        """Format subscription data for API response."""
        return {
            "id": str(subscription.id),
            "plan": subscription.plan.value,
            "billing_cycle": subscription.billing_cycle.value,
            "status": subscription.status.value,
            "price": float(subscription.price),
            "currency": subscription.currency,
            "features": subscription.features,
            "limits": subscription.limits,
            "current_period_start": subscription.current_period_start.isoformat(),
            "current_period_end": subscription.current_period_end.isoformat(),
            "auto_renewal": subscription.auto_renewal,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "created_at": subscription.created_at.isoformat(),
            "activated_at": subscription.activated_at.isoformat() if subscription.activated_at else None,
            "cancelled_at": subscription.cancelled_at.isoformat() if subscription.cancelled_at else None
        }
        
    async def _process_initial_payment(
        self,
        subscription: Subscription,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Process initial subscription payment."""
        # Implementation would handle payment processing
        return {"success": True}
        
    async def _process_upgrade_payment(
        self,
        subscription: Subscription,
        amount: Decimal,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Process upgrade prorated payment."""
        # Implementation would handle upgrade payment
        return {"success": True}
        
    async def _process_renewal_payment(
        self,
        subscription: Subscription,
        payment_method: PaymentMethod
    ) -> Dict[str, Any]:
        """Process subscription renewal payment."""
        # Implementation would handle renewal payment
        return {"success": True}
        
    async def _calculate_prorated_amount(
        self,
        subscription: Subscription,
        new_price: Decimal
    ) -> Decimal:
        """Calculate prorated amount for subscription change."""
        # Implementation would calculate prorated amount
        return Decimal('0.00')
        
    async def _calculate_refund_amount(self, subscription: Subscription) -> Decimal:
        """
Calculate refund amount for cancelled subscription."""
        # Implementation would calculate refund amount
        return Decimal('0.00')
        
    async def _process_refund(self, subscription: Subscription, amount: Decimal) -> Dict[str, Any]:
        """
Process subscription refund."""
        # Implementation would handle refund processing
        return {"success": True}
