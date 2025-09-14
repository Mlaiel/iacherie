"""
💳 Subscription Management Microservice
Enterprise subscription lifecycle management with billing, renewals, and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
from abc import ABC, abstractmethod
from decimal import Decimal

logger = logging.getLogger(__name__)


class SubscriptionStatus(str, Enum):
    """Subscription status states"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    PENDING = "pending"
    PAST_DUE = "past_due"
    PAUSED = "paused"


class BillingCycle(str, Enum):
    """Billing cycle types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    DAILY = "daily"
    LIFETIME = "lifetime"


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class SubscriptionPlan:
    """Subscription plan configuration"""
    plan_id: str
    name: str
    tier: SubscriptionTier
    price: Decimal
    billing_cycle: BillingCycle
    features: List[str] = field(default_factory=list)
    limits: Dict[str, Any] = field(default_factory=dict)
    trial_days: int = 0
    setup_fee: Optional[Decimal] = None
    currency: str = "USD"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Subscription:
    """Customer subscription instance"""
    subscription_id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    billing_amount: Decimal = Decimal('0.00')
    currency: str = "USD"
    payment_method_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage_metrics: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BillingEvent:
    """Billing event record"""
    event_id: str
    subscription_id: str
    event_type: str  # charge, refund, upgrade, downgrade
    amount: Decimal
    currency: str
    status: str  # success, failed, pending
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BillingEngine(ABC):
    """Abstract billing engine interface"""
    
    @abstractmethod
    async def process_billing(self, subscription: Subscription) -> BillingEvent:
        """Process billing for subscription"""
        pass
    
    @abstractmethod
    async def handle_payment_failure(self, subscription: Subscription, error: str) -> bool:
        """Handle payment failure"""
        pass


class StripeBillingEngine(BillingEngine):
    """Stripe billing integration"""
    
    def __init__(self, api_key -> None: str) -> None:
        self.api_key = api_key
        
    async def process_billing(self, subscription: Subscription) -> BillingEvent:
        """Process billing via Stripe"""
        try:
            # Simulate Stripe billing
            event_id = str(uuid.uuid4())
            
            # Mock successful billing
            return BillingEvent(
                event_id=event_id,
                subscription_id=subscription.subscription_id,
                event_type="charge",
                amount=subscription.billing_amount,
                currency=subscription.currency,
                status="success",
                description=f"Billing processed for subscription {subscription.subscription_id}"
            )
            
        except Exception as e:
            logger.error(f"Stripe billing failed: {e}")
            return BillingEvent(
                event_id=str(uuid.uuid4()),
                subscription_id=subscription.subscription_id,
                event_type="charge",
                amount=subscription.billing_amount,
                currency=subscription.currency,
                status="failed",
                description=f"Billing failed: {str(e)}"
            )
    
    async def handle_payment_failure(self, subscription: Subscription, error: str) -> bool:
        """Handle Stripe payment failure"""
        logger.warning(f"Payment failure for subscription {subscription.subscription_id}: {error}")
        # Implement retry logic, dunning management, etc.
        return True


class SubscriptionManagementService:
    """Enterprise subscription management service"""
    
    def __init__(self) -> None:
        self.subscriptions: Dict[str, Subscription] = {}
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.billing_events: List[BillingEvent] = []
        self.billing_engines: Dict[str, BillingEngine] = {}
        self.usage_trackers: Dict[str, Dict[str, int]] = {}
        
        # Load default plans
        self._initialize_default_plans()
        
    def _initialize_default_plans(self) -> None:
        """Initialize default subscription plans"""
        default_plans = [
            SubscriptionPlan(
                plan_id="free",
                name="Free Plan",
                tier=SubscriptionTier.FREE,
                price=Decimal('0.00'),
                billing_cycle=BillingCycle.MONTHLY,
                features=["basic_upload", "5_projects"],
                limits={"uploads_per_month": 10, "storage_gb": 1}
            ),
            SubscriptionPlan(
                plan_id="premium",
                name="Premium Plan",
                tier=SubscriptionTier.PREMIUM,
                price=Decimal('29.99'),
                billing_cycle=BillingCycle.MONTHLY,
                features=["unlimited_upload", "ai_enhancement", "analytics"],
                limits={"uploads_per_month": 1000, "storage_gb": 100},
                trial_days=14
            ),
            SubscriptionPlan(
                plan_id="enterprise",
                name="Enterprise Plan",
                tier=SubscriptionTier.ENTERPRISE,
                price=Decimal('299.99'),
                billing_cycle=BillingCycle.MONTHLY,
                features=["unlimited_everything", "priority_support", "custom_ai"],
                limits={"uploads_per_month": -1, "storage_gb": -1}  # unlimited
            )
        ]
        
        for plan in default_plans:
            self.plans[plan.plan_id] = plan
    
    async def create_subscription(
        self, 
        customer_id: str, 
        plan_id: str,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Create new subscription"""
        
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        subscription_id = str(uuid.uuid4())
        
        # Calculate dates
        start_date = datetime.utcnow()
        trial_end_date = None
        next_billing_date = None
        
        if plan.trial_days > 0:
            trial_end_date = start_date + timedelta(days=plan.trial_days)
            next_billing_date = trial_end_date
        else:
            # Calculate next billing based on cycle
            if plan.billing_cycle == BillingCycle.MONTHLY:
                next_billing_date = start_date + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                next_billing_date = start_date + timedelta(days=365)
        
        subscription = Subscription(
            subscription_id=subscription_id,
            customer_id=customer_id,
            plan_id=plan_id,
            status=SubscriptionStatus.TRIAL if plan.trial_days > 0 else SubscriptionStatus.ACTIVE,
            start_date=start_date,
            trial_end_date=trial_end_date,
            next_billing_date=next_billing_date,
            billing_amount=plan.price,
            currency=plan.currency,
            payment_method_id=payment_method_id,
            metadata=metadata or {}
        )
        
        self.subscriptions[subscription_id] = subscription
        self.usage_trackers[subscription_id] = {}
        
        logger.info(f"Created subscription {subscription_id} for customer {customer_id}")
        return subscription
    
    async def process_renewals(self) -> List[BillingEvent]:
        """Process subscription renewals"""
        events = []
        current_time = datetime.utcnow()
        
        for subscription in self.subscriptions.values():
            if (subscription.next_billing_date and 
                subscription.next_billing_date <= current_time and
                subscription.status == SubscriptionStatus.ACTIVE):
                
                # Process billing
                billing_engine = self.billing_engines.get("stripe")
                if billing_engine:
                    event = await billing_engine.process_billing(subscription)
                    events.append(event)
                    self.billing_events.append(event)
                    
                    if event.status == "success":
                        # Update next billing date
                        plan = self.plans[subscription.plan_id]
                        if plan.billing_cycle == BillingCycle.MONTHLY:
                            subscription.next_billing_date += timedelta(days=30)
                        elif plan.billing_cycle == BillingCycle.YEARLY:
                            subscription.next_billing_date += timedelta(days=365)
                    else:
                        # Handle payment failure
                        await self._handle_billing_failure(subscription, event)
        
        return events
    
    async def _handle_billing_failure(self, subscription -> None: Subscription, event -> None: BillingEvent) -> None:
        """Handle billing failure"""
        # Move to past due status
        subscription.status = SubscriptionStatus.PAST_DUE
        subscription.updated_at = datetime.utcnow()
        
        # Schedule retry (implement dunning management)
        logger.warning(f"Billing failed for subscription {subscription.subscription_id}")
    
    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> bool:
        """Upgrade subscription to new plan"""
        if subscription_id not in self.subscriptions:
            return False
        
        if new_plan_id not in self.plans:
            return False
        
        subscription = self.subscriptions[subscription_id]
        old_plan = self.plans[subscription.plan_id]
        new_plan = self.plans[new_plan_id]
        
        # Calculate prorated amount
        prorated_amount = await self._calculate_proration(subscription, old_plan, new_plan)
        
        # Update subscription
        subscription.plan_id = new_plan_id
        subscription.billing_amount = new_plan.price
        subscription.updated_at = datetime.utcnow()
        
        # Create billing event for upgrade
        upgrade_event = BillingEvent(
            event_id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            event_type="upgrade",
            amount=prorated_amount,
            currency=subscription.currency,
            status="success",
            description=f"Upgraded from {old_plan.name} to {new_plan.name}"
        )
        
        self.billing_events.append(upgrade_event)
        logger.info(f"Upgraded subscription {subscription_id} to {new_plan_id}")
        return True
    
    async def _calculate_proration(
        self, 
        subscription: Subscription, 
        old_plan: SubscriptionPlan, 
        new_plan: SubscriptionPlan
    ) -> Decimal:
        """Calculate prorated amount for plan change"""
        # Simplified proration calculation
        price_difference = new_plan.price - old_plan.price
        
        if subscription.next_billing_date:
            days_remaining = (subscription.next_billing_date - datetime.utcnow()).days
            total_days = 30 if old_plan.billing_cycle == BillingCycle.MONTHLY else 365
            proration_factor = Decimal(days_remaining) / Decimal(total_days)
            return price_difference * proration_factor
        
        return price_difference
    
    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> bool:
        """Cancel subscription"""
        if subscription_id not in self.subscriptions:
            return False
        
        subscription = self.subscriptions[subscription_id]
        
        if immediate:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.end_date = datetime.utcnow()
        else:
            # Cancel at end of billing period
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.end_date = subscription.next_billing_date
        
        subscription.updated_at = datetime.utcnow()
        
        logger.info(f"Cancelled subscription {subscription_id}")
        return True
    
    async def track_usage(self, subscription_id -> None: str, feature -> None: str, amount -> None: int = 1) -> None:
        """Track feature usage for subscription"""
        if subscription_id in self.usage_trackers:
            if feature not in self.usage_trackers[subscription_id]:
                self.usage_trackers[subscription_id][feature] = 0
            self.usage_trackers[subscription_id][feature] += amount
    
    async def check_usage_limits(self, subscription_id: str, feature: str) -> bool:
        """Check if usage is within limits"""
        if subscription_id not in self.subscriptions:
            return False
        
        subscription = self.subscriptions[subscription_id]
        plan = self.plans[subscription.plan_id]
        
        if feature not in plan.limits:
            return True  # No limit defined
        
        limit = plan.limits[feature]
        if limit == -1:  # Unlimited
            return True
        
        usage = self.usage_trackers.get(subscription_id, {}).get(feature, 0)
        return usage < limit
    
    async def get_subscription_analytics(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription analytics"""
        if subscription_id not in self.subscriptions:
            return {}
        
        subscription = self.subscriptions[subscription_id]
        plan = self.plans[subscription.plan_id]
        usage = self.usage_trackers.get(subscription_id, {})
        
        # Calculate metrics
        days_active = (datetime.utcnow() - subscription.start_date).days
        revenue = subscription.billing_amount * Decimal(max(1, days_active // 30))
        
        return {
            "subscription_id": subscription_id,
            "customer_id": subscription.customer_id,
            "plan_name": plan.name,
            "status": subscription.status.value,
            "days_active": days_active,
            "total_revenue": float(revenue),
            "usage_metrics": usage,
            "limits": plan.limits,
            "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None
        }
    
    async def get_churn_analysis(self) -> Dict[str, Any]:
        """Analyze subscription churn"""
        total_subscriptions = len(self.subscriptions)
        cancelled_subscriptions = len([s for s in self.subscriptions.values() 
                                     if s.status == SubscriptionStatus.CANCELLED])
        
        churn_rate = (cancelled_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0
        
        # Revenue analysis
        active_revenue = sum([s.billing_amount for s in self.subscriptions.values() 
                            if s.status == SubscriptionStatus.ACTIVE])
        
        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": total_subscriptions - cancelled_subscriptions,
            "cancelled_subscriptions": cancelled_subscriptions,
            "churn_rate_percent": round(churn_rate, 2),
            "monthly_recurring_revenue": float(active_revenue),
            "average_revenue_per_user": float(active_revenue / max(1, total_subscriptions - cancelled_subscriptions))
        }


# Global service instance
subscription_service = SubscriptionManagementService()

async def get_subscription_service() -> SubscriptionManagementService:
    """Get subscription management service instance"""
    return subscription_service