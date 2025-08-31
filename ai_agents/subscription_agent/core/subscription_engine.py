"""Subscription Engine - Core subscription management functionality

Provides automated recurring revenue processing and subscription lifecycle management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    """Subscription status types"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"
    TRIAL = "trial"

class BillingCycle(Enum):
    """Billing cycle types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"

@dataclass
class Subscription:
    """Subscription data model"""
    subscription_id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    price: float
    currency: str
    start_date: datetime
    next_billing: datetime
    created_at: datetime

@dataclass
class SubscriptionPlan:
    """Subscription plan definition"""
    plan_id: str
    name: str
    description: str
    price: float
    currency: str
    billing_cycle: BillingCycle
    features: List[str]
    trial_days: int = 0

class SubscriptionEngine:
    """Automated subscription management engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.plans: Dict[str, SubscriptionPlan] = {}
        logger.info("Subscription Engine initialized")
    
    async def start(self):
        """Start the subscription engine"""
        logger.info("Starting Subscription Engine")
        await self._load_default_plans()
    
    async def _load_default_plans(self):
        """Load default subscription plans"""
        default_plans = [
            SubscriptionPlan(
                plan_id="basic_monthly",
                name="Basic Plan",
                description="Basic features for content creators",
                price=9.99,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                features=["Basic protection", "5GB storage", "Email support"],
                trial_days=7
            ),
            SubscriptionPlan(
                plan_id="pro_monthly",
                name="Pro Plan", 
                description="Advanced features for professional creators",
                price=29.99,
                currency="USD",
                billing_cycle=BillingCycle.MONTHLY,
                features=["Advanced protection", "50GB storage", "Priority support", "Analytics"],
                trial_days=14
            )
        ]
        
        for plan in default_plans:
            self.plans[plan.plan_id] = plan
    
    async def create_subscription(self, user_id: str, plan_id: str) -> Dict[str, Any]:
        """Create a new subscription"""
        try:
            if plan_id not in self.plans:
                raise ValueError(f"Plan {plan_id} not found")
            
            plan = self.plans[plan_id]
            subscription_id = f"sub_{user_id}_{plan_id}_{int(datetime.now().timestamp())}"
            
            start_date = datetime.now()
            trial_end = start_date + timedelta(days=plan.trial_days)
            next_billing = trial_end if plan.trial_days > 0 else start_date + timedelta(days=30)
            
            subscription = Subscription(
                subscription_id=subscription_id,
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.TRIAL if plan.trial_days > 0 else SubscriptionStatus.ACTIVE,
                billing_cycle=plan.billing_cycle,
                price=plan.price,
                currency=plan.currency,
                start_date=start_date,
                next_billing=next_billing,
                created_at=start_date
            )
            
            self.subscriptions[subscription_id] = subscription
            
            return {
                'subscription_id': subscription_id,
                'status': subscription.status.value,
                'next_billing': next_billing.isoformat(),
                'trial_ends': trial_end.isoformat() if plan.trial_days > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    async def process_billing(self, subscription_id: str) -> Dict[str, Any]:
        """Process billing for a subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            
            # Calculate next billing date
            if subscription.billing_cycle == BillingCycle.MONTHLY:
                next_billing = subscription.next_billing + timedelta(days=30)
            elif subscription.billing_cycle == BillingCycle.YEARLY:
                next_billing = subscription.next_billing + timedelta(days=365)
            else:
                next_billing = subscription.next_billing + timedelta(days=90)
            
            # Update subscription
            subscription.next_billing = next_billing
            subscription.status = SubscriptionStatus.ACTIVE
            
            return {
                'subscription_id': subscription_id,
                'amount_charged': subscription.price,
                'currency': subscription.currency,
                'next_billing': next_billing.isoformat(),
                'status': 'processed'
            }
            
        except Exception as e:
            logger.error(f"Billing processing failed: {e}")
            raise
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            subscription.status = SubscriptionStatus.CANCELED
            
            return {
                'subscription_id': subscription_id,
                'status': 'canceled',
                'canceled_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}")
            raise
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics and metrics"""
        try:
            active_subs = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
            trial_subs = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.TRIAL])
            canceled_subs = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.CANCELED])
            
            total_mrr = sum(s.price for s in self.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE)
            
            return {
                'total_subscriptions': len(self.subscriptions),
                'active_subscriptions': active_subs,
                'trial_subscriptions': trial_subs,
                'canceled_subscriptions': canceled_subs,
                'monthly_recurring_revenue': total_mrr,
                'churn_rate': canceled_subs / len(self.subscriptions) if self.subscriptions else 0
            }
            
        except Exception as e:
            logger.error(f"Analytics calculation failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the subscription engine"""
        logger.info("Subscription Engine shutdown")