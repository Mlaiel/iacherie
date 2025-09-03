"""Subscription Manager - Advanced Subscription Lifecycle Management
===================================================================

Comprehensive subscription management system with lifecycle handling,
billing automation, and multi-tier subscription support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    SUSPENDED = "suspended"
    PAUSED = "paused"
    EXPIRED = "expired"


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingCycle(str, Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


@dataclass
class SubscriptionPlan:
    """Subscription plan definition."""
    id: str
    name: str
    tier: SubscriptionTier
    price: Decimal
    billing_cycle: BillingCycle
    features: List[str]
    limits: Dict[str, Any]
    trial_days: int = 0
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subscription:
    """User subscription instance."""
    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SubscriptionUsage:
    """Subscription usage tracking."""
    subscription_id: str
    period_start: datetime
    period_end: datetime
    usage_data: Dict[str, Any]
    overage_charges: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.now)


class SubscriptionManager:
    """Advanced subscription lifecycle management system."""
    
    def __init__(self):
        """Initialize subscription manager."""
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.usage_records: Dict[str, List[SubscriptionUsage]] = {}
        
        # Default subscription plans
        self._initialize_default_plans()
        
        logger.info("Subscription manager initialized")
    
    def _initialize_default_plans(self) -> None:
        """Initialize default subscription plans."""
        default_plans = [
            SubscriptionPlan(
                id="free",
                name="Free Plan",
                tier=SubscriptionTier.FREE,
                price=Decimal("0"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "basic_content_creation",
                    "social_media_posting",
                    "basic_analytics"
                ],
                limits={
                    "posts_per_month": 10,
                    "storage_gb": 1,
                    "ai_generations": 5
                },
                description="Basic features for getting started"
            ),
            SubscriptionPlan(
                id="basic",
                name="Basic Plan",
                tier=SubscriptionTier.BASIC,
                price=Decimal("19.99"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "advanced_content_creation",
                    "multi_platform_posting",
                    "analytics_dashboard",
                    "content_scheduling"
                ],
                limits={
                    "posts_per_month": 100,
                    "storage_gb": 10,
                    "ai_generations": 50
                },
                trial_days=14,
                description="Perfect for individual creators"
            ),
            SubscriptionPlan(
                id="premium",
                name="Premium Plan",
                tier=SubscriptionTier.PREMIUM,
                price=Decimal("49.99"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "all_basic_features",
                    "ai_powered_optimization",
                    "advanced_analytics",
                    "collaboration_tools",
                    "priority_support"
                ],
                limits={
                    "posts_per_month": 500,
                    "storage_gb": 50,
                    "ai_generations": 200
                },
                trial_days=30,
                description="For growing creators and small teams"
            ),
            SubscriptionPlan(
                id="professional",
                name="Professional Plan",
                tier=SubscriptionTier.PROFESSIONAL,
                price=Decimal("99.99"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "all_premium_features",
                    "white_label_solutions",
                    "api_access",
                    "custom_integrations",
                    "dedicated_support"
                ],
                limits={
                    "posts_per_month": 2000,
                    "storage_gb": 200,
                    "ai_generations": 1000
                },
                trial_days=30,
                description="For agencies and professional creators"
            ),
            SubscriptionPlan(
                id="enterprise",
                name="Enterprise Plan",
                tier=SubscriptionTier.ENTERPRISE,
                price=Decimal("299.99"),
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "all_professional_features",
                    "unlimited_usage",
                    "custom_development",
                    "sla_guarantees",
                    "enterprise_support"
                ],
                limits={
                    "posts_per_month": -1,  # Unlimited
                    "storage_gb": -1,  # Unlimited
                    "ai_generations": -1  # Unlimited
                },
                trial_days=30,
                description="For large organizations and enterprises"
            )
        ]
        
        for plan in default_plans:
            self.plans[plan.id] = plan
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method_id: Optional[str] = None,
        start_trial: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Create a new subscription.
        
        Args:
            user_id: User identifier
            plan_id: Subscription plan identifier
            payment_method_id: Payment method identifier
            start_trial: Whether to start with trial period
            metadata: Additional metadata
            
        Returns:
            Created subscription
        """
        try:
            if plan_id not in self.plans:
                raise ValueError(f"Plan not found: {plan_id}")
            
            plan = self.plans[plan_id]
            subscription_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Calculate subscription periods
            if start_trial and plan.trial_days > 0:
                trial_end = now + timedelta(days=plan.trial_days)
                period_start = trial_end
                status = SubscriptionStatus.TRIALING
            else:
                trial_end = None
                period_start = now
                status = SubscriptionStatus.ACTIVE
            
            # Calculate period end based on billing cycle
            if plan.billing_cycle == BillingCycle.MONTHLY:
                period_end = period_start + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.QUARTERLY:
                period_end = period_start + timedelta(days=90)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                period_end = period_start + timedelta(days=365)
            else:  # LIFETIME
                period_end = period_start + timedelta(days=365 * 100)  # Far future
            
            subscription = Subscription(
                id=subscription_id,
                user_id=user_id,
                plan_id=plan_id,
                status=status,
                current_period_start=period_start,
                current_period_end=period_end,
                trial_end=trial_end,
                payment_method_id=payment_method_id,
                metadata=metadata or {}
            )
            
            self.subscriptions[subscription_id] = subscription
            
            # Schedule trial end notification if applicable
            if trial_end:
                asyncio.create_task(self._schedule_trial_notifications(subscription_id))
            
            logger.info(f"Created subscription: {subscription_id} for user {user_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        prorate: bool = True
    ) -> Subscription:
        """Upgrade subscription to a higher tier.
        
        Args:
            subscription_id: Subscription identifier
            new_plan_id: New plan identifier
            prorate: Whether to prorate the upgrade
            
        Returns:
            Updated subscription
        """
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            if new_plan_id not in self.plans:
                raise ValueError(f"Plan not found: {new_plan_id}")
            
            subscription = self.subscriptions[subscription_id]
            old_plan = self.plans[subscription.plan_id]
            new_plan = self.plans[new_plan_id]
            
            # Validate upgrade (new plan should be higher tier)
            tier_order = {
                SubscriptionTier.FREE: 0,
                SubscriptionTier.BASIC: 1,
                SubscriptionTier.PREMIUM: 2,
                SubscriptionTier.PROFESSIONAL: 3,
                SubscriptionTier.ENTERPRISE: 4
            }
            
            if tier_order[new_plan.tier] <= tier_order[old_plan.tier]:
                raise ValueError("Cannot upgrade to same or lower tier")
            
            # Calculate prorated amount if applicable
            if prorate and old_plan.price > 0:
                remaining_days = (subscription.current_period_end - datetime.now()).days
                total_days = (subscription.current_period_end - subscription.current_period_start).days
                proration_factor = remaining_days / total_days if total_days > 0 else 0
                
                old_plan_refund = old_plan.price * Decimal(str(proration_factor))
                new_plan_charge = new_plan.price * Decimal(str(proration_factor))
                upgrade_cost = new_plan_charge - old_plan_refund
                
                logger.info(f"Upgrade cost calculated: ${upgrade_cost}")
            
            # Update subscription
            subscription.plan_id = new_plan_id
            subscription.updated_at = datetime.now()
            
            logger.info(f"Upgraded subscription {subscription_id} to {new_plan_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to upgrade subscription: {e}")
            raise
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False,
        reason: Optional[str] = None
    ) -> Subscription:
        """Cancel a subscription.
        
        Args:
            subscription_id: Subscription identifier
            immediate: Whether to cancel immediately
            reason: Cancellation reason
            
        Returns:
            Canceled subscription
        """
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.now()
            else:
                # Cancel at period end
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = subscription.current_period_end
            
            if reason:
                subscription.metadata["cancellation_reason"] = reason
            
            subscription.updated_at = datetime.now()
            
            logger.info(f"Canceled subscription: {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise
    
    async def reactivate_subscription(
        self,
        subscription_id: str,
        new_plan_id: Optional[str] = None
    ) -> Subscription:
        """Reactivate a canceled subscription.
        
        Args:
            subscription_id: Subscription identifier
            new_plan_id: Optional new plan identifier
            
        Returns:
            Reactivated subscription
        """
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            
            if subscription.status not in [SubscriptionStatus.CANCELED, SubscriptionStatus.EXPIRED]:
                raise ValueError("Can only reactivate canceled or expired subscriptions")
            
            # Update plan if specified
            if new_plan_id and new_plan_id in self.plans:
                subscription.plan_id = new_plan_id
            
            # Reset subscription periods
            now = datetime.now()
            plan = self.plans[subscription.plan_id]
            
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = now
            subscription.canceled_at = None
            
            # Calculate new period end
            if plan.billing_cycle == BillingCycle.MONTHLY:
                subscription.current_period_end = now + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.QUARTERLY:
                subscription.current_period_end = now + timedelta(days=90)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                subscription.current_period_end = now + timedelta(days=365)
            
            subscription.updated_at = now
            
            logger.info(f"Reactivated subscription: {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to reactivate subscription: {e}")
            raise
    
    async def record_usage(
        self,
        subscription_id: str,
        usage_data: Dict[str, Any]
    ) -> SubscriptionUsage:
        """Record subscription usage for billing.
        
        Args:
            subscription_id: Subscription identifier
            usage_data: Usage metrics
            
        Returns:
            Usage record
        """
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            usage_record = SubscriptionUsage(
                subscription_id=subscription_id,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                usage_data=usage_data
            )
            
            # Calculate overage charges
            overage_charges = Decimal("0")
            
            for metric, usage in usage_data.items():
                if metric in plan.limits:
                    limit = plan.limits[metric]
                    if limit > 0 and usage > limit:  # -1 means unlimited
                        overage = usage - limit
                        # Simple overage pricing: $0.01 per unit
                        overage_charges += Decimal(str(overage)) * Decimal("0.01")
            
            usage_record.overage_charges = overage_charges
            
            # Store usage record
            if subscription_id not in self.usage_records:
                self.usage_records[subscription_id] = []
            self.usage_records[subscription_id].append(usage_record)
            
            logger.info(f"Recorded usage for subscription {subscription_id}: {usage_data}")
            return usage_record
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            raise
    
    async def _schedule_trial_notifications(self, subscription_id: str) -> None:
        """Schedule trial end notifications.
        
        Args:
            subscription_id: Subscription identifier
        """
        try:
            if subscription_id not in self.subscriptions:
                return
            
            subscription = self.subscriptions[subscription_id]
            if not subscription.trial_end:
                return
            
            # Schedule notifications at 7, 3, and 1 days before trial ends
            warning_days = [7, 3, 1]
            
            for days in warning_days:
                notification_time = subscription.trial_end - timedelta(days=days)
                
                if notification_time > datetime.now():
                    delay = (notification_time - datetime.now()).total_seconds()
                    
                    asyncio.create_task(self._send_trial_notification(
                        subscription_id, days, delay
                    ))
            
        except Exception as e:
            logger.error(f"Failed to schedule trial notifications: {e}")
    
    async def _send_trial_notification(
        self,
        subscription_id: str,
        days_remaining: int,
        delay: float
    ) -> None:
        """Send trial end notification after delay.
        
        Args:
            subscription_id: Subscription identifier
            days_remaining: Days remaining in trial
            delay: Delay in seconds before sending
        """
        try:
            await asyncio.sleep(delay)
            
            if subscription_id not in self.subscriptions:
                return
            
            subscription = self.subscriptions[subscription_id]
            
            # Only send if subscription is still in trial
            if subscription.status == SubscriptionStatus.TRIALING:
                logger.info(f"Trial notification: {days_remaining} days remaining for {subscription_id}")
                # In real implementation, would send email/push notification
            
        except Exception as e:
            logger.error(f"Failed to send trial notification: {e}")
    
    async def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID.
        
        Args:
            subscription_id: Subscription identifier
            
        Returns:
            Subscription if found
        """
        return self.subscriptions.get(subscription_id)
    
    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get all subscriptions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user subscriptions
        """
        return [
            sub for sub in self.subscriptions.values()
            if sub.user_id == user_id
        ]
    
    async def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Subscription plan if found
        """
        return self.plans.get(plan_id)
    
    async def list_plans(self) -> List[SubscriptionPlan]:
        """List all available subscription plans.
        
        Returns:
            List of subscription plans
        """
        return list(self.plans.values())