"""
Subscription Management - Professional subscription and recurring payment system.
Handles all subscription lifecycle management, billing, and customer management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta, date
from enum import Enum
import asyncio
import logging
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


class SubscriptionTier(Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(Enum):
    """Subscription status states."""
    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    PAUSED = "paused"


class BillingCycle(Enum):
    """Billing cycle intervals."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class SubscriptionFeature(Enum):
    """Available subscription features."""
    CONTENT_UPLOAD = "content_upload"
    AI_PROTECTION = "ai_protection"
    ANALYTICS = "analytics"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    PREMIUM_SUPPORT = "premium_support"
    API_ACCESS = "api_access"
    WHITE_LABEL = "white_label"
    UNLIMITED_STORAGE = "unlimited_storage"
    ADVANCED_ANALYTICS = "advanced_analytics"


@dataclass
class SubscriptionPlan:
    """Subscription plan configuration."""
    plan_id: str
    name: str
    tier: SubscriptionTier
    price: Decimal
    currency: str = "EUR"
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    features: List[SubscriptionFeature] = field(default_factory=list)
    limits: Dict[str, int] = field(default_factory=dict)
    trial_days: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "tier": self.tier.value,
            "price": float(self.price),
            "currency": self.currency,
            "billing_cycle": self.billing_cycle.value,
            "features": [f.value for f in self.features],
            "limits": self.limits,
            "trial_days": self.trial_days,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class Subscription:
    """Individual subscription instance."""
    subscription_id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    billing_cycle_anchor: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary."""
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "billing_cycle_anchor": self.billing_cycle_anchor.isoformat(),
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]
    
    def is_trial(self) -> bool:
        """Check if subscription is in trial period."""
        return (self.status == SubscriptionStatus.TRIAL and 
                self.trial_end and 
                datetime.utcnow() < self.trial_end)
    
    def days_until_renewal(self) -> int:
        """Calculate days until next renewal."""
        if not self.is_active():
            return 0
        
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)
    
    def calculate_prorated_amount(self, new_plan_price: Decimal) -> Decimal:
        """Calculate prorated amount for plan changes."""
        days_remaining = self.days_until_renewal()
        days_in_period = (self.current_period_end - self.current_period_start).days
        
        if days_in_period <= 0:
            return new_plan_price
        
        proration_factor = Decimal(days_remaining) / Decimal(days_in_period)
        return new_plan_price * proration_factor


@dataclass
class BillingHistory:
    """Billing history record."""
    invoice_id: str
    subscription_id: str
    amount: Decimal
    currency: str
    status: str
    billing_date: datetime
    due_date: datetime
    paid_date: Optional[datetime] = None
    payment_method: str = ""
    invoice_url: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class SubscriptionManager:
    """
    Professional subscription management system.
    Handles all aspects of subscription lifecycle and billing.
    """
    
    def __init__(self):
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.billing_history: List[BillingHistory] = []
        self.default_plans = self._create_default_plans()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize subscription manager."""
        try:
            # Create default plans
            for plan in self.default_plans:
                self.plans[plan.plan_id] = plan
            
            self.is_initialized = True
            logger.info("Subscription manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"Subscription manager initialization failed: {e}")
            return False
    
    def _create_default_plans(self) -> List[SubscriptionPlan]:
        """Create default subscription plans."""
        plans = []
        
        # Free Plan
        free_plan = SubscriptionPlan(
            plan_id="free_plan",
            name="Free Creator",
            tier=SubscriptionTier.FREE,
            price=Decimal("0"),
            features=[
                SubscriptionFeature.CONTENT_UPLOAD,
                SubscriptionFeature.AI_PROTECTION
            ],
            limits={
                "uploads_per_month": 10,
                "storage_gb": 1,
                "protection_scans": 5
            }
        )
        plans.append(free_plan)
        
        # Basic Plan
        basic_plan = SubscriptionPlan(
            plan_id="basic_plan",
            name="Basic Creator",
            tier=SubscriptionTier.BASIC,
            price=Decimal("9.99"),
            features=[
                SubscriptionFeature.CONTENT_UPLOAD,
                SubscriptionFeature.AI_PROTECTION,
                SubscriptionFeature.ANALYTICS,
                SubscriptionFeature.MONETIZATION
            ],
            limits={
                "uploads_per_month": 100,
                "storage_gb": 10,
                "protection_scans": 50
            },
            trial_days=14
        )
        plans.append(basic_plan)
        
        # Premium Plan
        premium_plan = SubscriptionPlan(
            plan_id="premium_plan",
            name="Premium Creator",
            tier=SubscriptionTier.PREMIUM,
            price=Decimal("29.99"),
            features=[
                SubscriptionFeature.CONTENT_UPLOAD,
                SubscriptionFeature.AI_PROTECTION,
                SubscriptionFeature.ANALYTICS,
                SubscriptionFeature.MONETIZATION,
                SubscriptionFeature.COLLABORATION,
                SubscriptionFeature.API_ACCESS
            ],
            limits={
                "uploads_per_month": 500,
                "storage_gb": 50,
                "protection_scans": 200,
                "collaborators": 5
            },
            trial_days=14
        )
        plans.append(premium_plan)
        
        # Pro Plan
        pro_plan = SubscriptionPlan(
            plan_id="pro_plan",
            name="Pro Creator",
            tier=SubscriptionTier.PRO,
            price=Decimal("79.99"),
            features=[
                SubscriptionFeature.CONTENT_UPLOAD,
                SubscriptionFeature.AI_PROTECTION,
                SubscriptionFeature.ANALYTICS,
                SubscriptionFeature.MONETIZATION,
                SubscriptionFeature.COLLABORATION,
                SubscriptionFeature.API_ACCESS,
                SubscriptionFeature.PREMIUM_SUPPORT,
                SubscriptionFeature.ADVANCED_ANALYTICS
            ],
            limits={
                "uploads_per_month": 2000,
                "storage_gb": 200,
                "protection_scans": 1000,
                "collaborators": 20
            },
            trial_days=14
        )
        plans.append(pro_plan)
        
        # Enterprise Plan
        enterprise_plan = SubscriptionPlan(
            plan_id="enterprise_plan",
            name="Enterprise Creator",
            tier=SubscriptionTier.ENTERPRISE,
            price=Decimal("199.99"),
            features=list(SubscriptionFeature),  # All features
            limits={
                "uploads_per_month": -1,  # Unlimited
                "storage_gb": -1,  # Unlimited
                "protection_scans": -1,  # Unlimited
                "collaborators": -1  # Unlimited
            },
            trial_days=30
        )
        plans.append(enterprise_plan)
        
        return plans
    
    async def create_subscription(
        self, 
        user_id: str, 
        plan_id: str,
        start_trial: bool = True
    ) -> Optional[Subscription]:
        """Create a new subscription."""
        if not self.is_initialized:
            await self.initialize()
        
        plan = self.plans.get(plan_id)
        if not plan:
            logger.error(f"Plan not found: {plan_id}")
            return None
        
        try:
            subscription_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            # Calculate period dates
            if plan.billing_cycle == BillingCycle.MONTHLY:
                period_end = now + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                period_end = now + timedelta(days=365)
            elif plan.billing_cycle == BillingCycle.QUARTERLY:
                period_end = now + timedelta(days=90)
            else:
                period_end = now + timedelta(days=30)
            
            # Set trial end if applicable
            trial_end = None
            status = SubscriptionStatus.ACTIVE
            if start_trial and plan.trial_days > 0:
                trial_end = now + timedelta(days=plan.trial_days)
                status = SubscriptionStatus.TRIAL
            
            subscription = Subscription(
                subscription_id=subscription_id,
                user_id=user_id,
                plan_id=plan_id,
                status=status,
                current_period_start=now,
                current_period_end=period_end,
                trial_end=trial_end,
                billing_cycle_anchor=now
            )
            
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Subscription created: {subscription_id} for user {user_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            return None
    
    async def update_subscription(
        self, 
        subscription_id: str, 
        new_plan_id: str,
        prorate: bool = True
    ) -> bool:
        """Update subscription to a new plan."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            logger.error(f"Subscription not found: {subscription_id}")
            return False
        
        new_plan = self.plans.get(new_plan_id)
        if not new_plan:
            logger.error(f"Plan not found: {new_plan_id}")
            return False
        
        try:
            old_plan_id = subscription.plan_id
            
            # Calculate proration if needed
            if prorate and subscription.is_active():
                prorated_amount = subscription.calculate_prorated_amount(new_plan.price)
                # Create billing record for proration
                await self._create_proration_invoice(subscription, prorated_amount)
            
            # Update subscription
            subscription.plan_id = new_plan_id
            subscription.updated_at = datetime.utcnow()
            
            # If upgrading from free, end trial immediately
            if old_plan_id == "free_plan" and subscription.trial_end:
                subscription.trial_end = datetime.utcnow()
                subscription.status = SubscriptionStatus.ACTIVE
            
            logger.info(f"Subscription updated: {subscription_id} from {old_plan_id} to {new_plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Subscription update failed: {e}")
            return False
    
    async def cancel_subscription(
        self, 
        subscription_id: str, 
        immediate: bool = False
    ) -> bool:
        """Cancel a subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            logger.error(f"Subscription not found: {subscription_id}")
            return False
        
        try:
            now = datetime.utcnow()
            subscription.cancelled_at = now
            subscription.updated_at = now
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.ended_at = now
            else:
                # Cancel at period end
                subscription.status = SubscriptionStatus.CANCELLED
            
            logger.info(f"Subscription cancelled: {subscription_id}, immediate: {immediate}")
            return True
            
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {e}")
            return False
    
    async def reactivate_subscription(self, subscription_id: str) -> bool:
        """Reactivate a cancelled subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return False
        
        if subscription.status != SubscriptionStatus.CANCELLED:
            return False
        
        try:
            now = datetime.utcnow()
            
            # Reset subscription
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.cancelled_at = None
            subscription.ended_at = None
            subscription.updated_at = now
            
            # Extend period if needed
            if subscription.current_period_end < now:
                subscription.current_period_start = now
                subscription.current_period_end = now + timedelta(days=30)
            
            logger.info(f"Subscription reactivated: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Subscription reactivation failed: {e}")
            return False
    
    async def process_renewals(self) -> Dict[str, Any]:
        """Process subscription renewals."""
        now = datetime.utcnow()
        renewal_results = {
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        for subscription in self.subscriptions.values():
            if not subscription.is_active():
                continue
            
            # Check if renewal is due
            if subscription.current_period_end <= now:
                try:
                    plan = self.plans.get(subscription.plan_id)
                    if not plan:
                        renewal_results["failed"] += 1
                        continue
                    
                    # Create invoice
                    invoice = await self._create_invoice(subscription, plan.price)
                    
                    # Update subscription period
                    if plan.billing_cycle == BillingCycle.MONTHLY:
                        new_end = subscription.current_period_end + timedelta(days=30)
                    elif plan.billing_cycle == BillingCycle.YEARLY:
                        new_end = subscription.current_period_end + timedelta(days=365)
                    else:
                        new_end = subscription.current_period_end + timedelta(days=30)
                    
                    subscription.current_period_start = subscription.current_period_end
                    subscription.current_period_end = new_end
                    subscription.updated_at = now
                    
                    renewal_results["processed"] += 1
                    renewal_results["details"].append({
                        "subscription_id": subscription.subscription_id,
                        "amount": float(plan.price),
                        "next_billing": new_end.isoformat()
                    })
                    
                except Exception as e:
                    logger.error(f"Renewal failed for {subscription.subscription_id}: {e}")
                    renewal_results["failed"] += 1
            else:
                renewal_results["skipped"] += 1
        
        logger.info(f"Renewal processing complete: {renewal_results}")
        return renewal_results
    
    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get all subscriptions for a user."""
        return [
            sub for sub in self.subscriptions.values() 
            if sub.user_id == user_id
        ]
    
    async def get_subscription_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get subscription analytics."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter recent subscriptions
        recent_subs = [
            sub for sub in self.subscriptions.values()
            if sub.created_at >= cutoff_date
        ]
        
        # Calculate metrics
        total_revenue = Decimal("0")
        plan_distribution = {}
        status_distribution = {}
        
        for sub in self.subscriptions.values():
            if sub.is_active():
                plan = self.plans.get(sub.plan_id)
                if plan:
                    total_revenue += plan.price
            
            # Plan distribution
            plan_distribution[sub.plan_id] = plan_distribution.get(sub.plan_id, 0) + 1
            
            # Status distribution
            status_distribution[sub.status.value] = status_distribution.get(sub.status.value, 0) + 1
        
        return {
            "period_days": days,
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s.is_active()]),
            "new_subscriptions": len(recent_subs),
            "total_mrr": float(total_revenue),
            "plan_distribution": plan_distribution,
            "status_distribution": status_distribution,
            "churn_rate": self._calculate_churn_rate(days),
            "ltv": self._calculate_customer_ltv()
        }
    
    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID."""
        return self.plans.get(plan_id)
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)
    
    def list_plans(self, active_only: bool = True) -> List[SubscriptionPlan]:
        """List all available plans."""
        plans = list(self.plans.values())
        if active_only:
            plans = [p for p in plans if p.is_active]
        return plans
    
    async def _create_invoice(self, subscription: Subscription, amount: Decimal) -> BillingHistory:
        """Create billing invoice."""
        invoice = BillingHistory(
            invoice_id=str(uuid.uuid4()),
            subscription_id=subscription.subscription_id,
            amount=amount,
            currency="EUR",
            status="pending",
            billing_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=7)
        )
        
        self.billing_history.append(invoice)
        return invoice
    
    async def _create_proration_invoice(self, subscription: Subscription, amount: Decimal) -> BillingHistory:
        """Create proration invoice for plan changes."""
        invoice = BillingHistory(
            invoice_id=str(uuid.uuid4()),
            subscription_id=subscription.subscription_id,
            amount=amount,
            currency="EUR",
            status="proration",
            billing_date=datetime.utcnow(),
            due_date=datetime.utcnow(),
            metadata={"type": "proration"}
        )
        
        self.billing_history.append(invoice)
        return invoice
    
    def _calculate_churn_rate(self, days: int) -> float:
        """Calculate subscription churn rate."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Subscriptions that were active at start of period
        active_start = [
            s for s in self.subscriptions.values()
            if s.created_at < cutoff_date and s.status != SubscriptionStatus.CANCELLED
        ]
        
        # Subscriptions that cancelled during period
        cancelled_period = [
            s for s in active_start
            if s.cancelled_at and s.cancelled_at >= cutoff_date
        ]
        
        if not active_start:
            return 0.0
        
        return len(cancelled_period) / len(active_start)
    
    def _calculate_customer_ltv(self) -> float:
        """Calculate average customer lifetime value."""
        active_subs = [s for s in self.subscriptions.values() if s.is_active()]
        
        if not active_subs:
            return 0.0
        
        total_value = 0.0
        for sub in active_subs:
            plan = self.plans.get(sub.plan_id)
            if plan:
                # Simple LTV calculation: monthly price * 12 months
                monthly_price = float(plan.price)
                if plan.billing_cycle == BillingCycle.YEARLY:
                    monthly_price = monthly_price / 12
                total_value += monthly_price * 12
        
        return total_value / len(active_subs)
