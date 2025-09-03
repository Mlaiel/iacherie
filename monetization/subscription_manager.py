"""Subscription Management System
Advanced subscription lifecycle management with automated billing and plan management.

Author: Fahed Mlaiel <mlaiel@live.de>
⚠️ COPYRIGHT WARNING: Proprietary code - unauthorized use prohibited.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Subscription status enumeration."""
    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    PAUSED = "paused"


class SubscriptionTier(Enum):
    """Subscription tier enumeration."""
    FREE = "free"
    CREATOR = "creator"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class BillingCycle(Enum):
    """Billing cycle enumeration."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    LIFETIME = "lifetime"


@dataclass
class SubscriptionPlan:
    """Subscription plan data structure."""
    plan_id: str
    name: str
    tier: SubscriptionTier
    price: Decimal
    currency: str
    billing_cycle: BillingCycle
    features: Dict[str, Any]
    limits: Dict[str, int]
    trial_days: int = 0
    setup_fee: Decimal = Decimal('0.00')
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class Subscription:
    """Subscription data structure."""
    subscription_id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    payment_method_id: Optional[str] = None
    discount_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class SubscriptionUsage:
    """Subscription usage tracking."""
    subscription_id: str
    feature: str
    usage_count: int
    limit: int
    period_start: datetime
    period_end: datetime
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class SubscriptionManager:
    """Advanced subscription management system."""

    def __init__(self):
        """Initialize subscription manager."""
        try:
            logger.info("Initializing SubscriptionManager")
            
            # Subscription storage (in production, use database)
            self.plans: Dict[str, SubscriptionPlan] = {}
            self.subscriptions: Dict[str, Subscription] = {}
            self.usage_tracking: Dict[str, Dict[str, SubscriptionUsage]] = {}
            
            # Initialize default plans
            self._initialize_default_plans()
            
            # Configuration
            self.grace_period_days = 3
            self.retry_attempts = 3
            self.dunning_period_days = 7
            
            # Supported currencies
            self.supported_currencies = [
                "EUR", "USD", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"
            ]
            
            # Tax rates by country (simplified)
            self.tax_rates = {
                "DE": 0.19,  # Germany VAT
                "FR": 0.20,  # France VAT
                "GB": 0.20,  # UK VAT
                "US": 0.08,  # Average US sales tax
                "CA": 0.13,  # Average Canadian tax
                "AU": 0.10,  # Australian GST
            }
            
            logger.info("SubscriptionManager initialized successfully")
            
        except Exception as e:
            logger.error(f"SubscriptionManager initialization failed: {e}")
            raise

    def _initialize_default_plans(self):
        """Initialize default subscription plans."""
        try:
            # Free tier
            free_plan = SubscriptionPlan(
                plan_id="free_tier",
                name="Free Tier",
                tier=SubscriptionTier.FREE,
                price=Decimal('0.00'),
                currency="EUR",
                billing_cycle=BillingCycle.MONTHLY,
                features={
                    "uploads": True,
                    "fingerprinting": True,
                    "collaboration": True,
                    "analytics": "basic",
                    "support": "community",
                    "export_quality": "standard",
                    "ai_features": "basic"
                },
                limits={
                    "uploads_per_month": 10,
                    "fingerprinting_scans": 5,
                    "active_projects": 2,
                    "storage_gb": 1,
                    "analytics_history_days": 30
                }
            )
            
            # Creator tier
            creator_plan = SubscriptionPlan(
                plan_id="creator_tier",
                name="Creator Tier",
                tier=SubscriptionTier.CREATOR,
                price=Decimal('29.00'),
                currency="EUR",
                billing_cycle=BillingCycle.MONTHLY,
                features={
                    "uploads": True,
                    "fingerprinting": True,
                    "collaboration": True,
                    "analytics": "advanced",
                    "support": "email",
                    "export_quality": "high",
                    "ai_features": "standard"
                },
                limits={
                    "uploads_per_month": 100,
                    "fingerprinting_scans": 50,
                    "active_projects": 10,
                    "storage_gb": 50,
                    "analytics_history_days": 365
                },
                trial_days=14
            )
            
            # Pro tier
            pro_plan = SubscriptionPlan(
                plan_id="pro_tier",
                name="Pro Tier",
                tier=SubscriptionTier.PRO,
                price=Decimal('99.00'),
                currency="EUR",
                billing_cycle=BillingCycle.MONTHLY,
                features={
                    "uploads": True,
                    "fingerprinting": True,
                    "collaboration": True,
                    "analytics": "professional",
                    "support": "priority",
                    "export_quality": "professional",
                    "ai_features": "advanced",
                    "white_label": True,
                    "api_access": "limited"
                },
                limits={
                    "uploads_per_month": 500,
                    "fingerprinting_scans": 200,
                    "active_projects": 50,
                    "storage_gb": 200,
                    "analytics_history_days": 1825
                },
                trial_days=30
            )
            
            # Enterprise tier
            enterprise_plan = SubscriptionPlan(
                plan_id="enterprise_tier",
                name="Enterprise Tier",
                tier=SubscriptionTier.ENTERPRISE,
                price=Decimal('499.00'),
                currency="EUR",
                billing_cycle=BillingCycle.MONTHLY,
                features={
                    "uploads": True,
                    "fingerprinting": True,
                    "collaboration": True,
                    "analytics": "enterprise",
                    "support": "dedicated",
                    "export_quality": "studio",
                    "ai_features": "full",
                    "white_label": True,
                    "api_access": "full",
                    "custom_integrations": True,
                    "sla": True,
                    "on_premise": True
                },
                limits={
                    "uploads_per_month": -1,  # Unlimited
                    "fingerprinting_scans": -1,
                    "active_projects": -1,
                    "storage_gb": -1,
                    "analytics_history_days": -1
                },
                trial_days=30
            )
            
            # Store plans
            for plan in [free_plan, creator_plan, pro_plan, enterprise_plan]:
                self.plans[plan.plan_id] = plan
                
            logger.info(f"Initialized {len(self.plans)} default subscription plans")
            
        except Exception as e:
            logger.error(f"Error initializing default plans: {e}")
            raise

    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Create a new subscription."""
        try:
            # Validate plan exists
            if plan_id not in self.plans:
                raise ValueError(f"Plan {plan_id} not found")
                
            plan = self.plans[plan_id]
            subscription_id = str(uuid.uuid4())
            
            # Calculate trial and billing periods
            now = datetime.utcnow()
            trial_days = trial_days or plan.trial_days
            
            if trial_days > 0:
                trial_start = now
                trial_end = now + timedelta(days=trial_days)
                current_period_start = trial_end
                status = SubscriptionStatus.TRIALING
            else:
                trial_start = None
                trial_end = None
                current_period_start = now
                status = SubscriptionStatus.ACTIVE if plan.price == 0 else SubscriptionStatus.PENDING
            
            # Calculate billing period end
            if plan.billing_cycle == BillingCycle.MONTHLY:
                current_period_end = current_period_start + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.QUARTERLY:
                current_period_end = current_period_start + timedelta(days=90)
            elif plan.billing_cycle == BillingCycle.ANNUALLY:
                current_period_end = current_period_start + timedelta(days=365)
            else:  # LIFETIME
                current_period_end = current_period_start + timedelta(days=36500)  # 100 years
                
            # Create subscription
            subscription = Subscription(
                subscription_id=subscription_id,
                user_id=user_id,
                plan_id=plan_id,
                status=status,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                trial_start=trial_start,
                trial_end=trial_end,
                payment_method_id=payment_method_id,
                metadata=metadata or {}
            )
            
            # Store subscription
            self.subscriptions[subscription_id] = subscription
            
            # Initialize usage tracking
            self._initialize_usage_tracking(subscription_id, plan_id)
            
            logger.info(f"Created subscription {subscription_id} for user {user_id} on plan {plan_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True,
        reason: Optional[str] = None
    ) -> Subscription:
        """Cancel a subscription."""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
                
            subscription = self.subscriptions[subscription_id]
            now = datetime.utcnow()
            
            if cancel_at_period_end:
                subscription.cancelled_at = now
                subscription.ended_at = subscription.current_period_end
                # Keep active until period end
            else:
                subscription.cancelled_at = now
                subscription.ended_at = now
                subscription.status = SubscriptionStatus.CANCELLED
                
            subscription.updated_at = now
            
            if reason:
                subscription.metadata["cancellation_reason"] = reason
                
            logger.info(f"Cancelled subscription {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise

    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        prorate: bool = True
    ) -> Subscription:
        """Upgrade/downgrade a subscription to a new plan."""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
                
            if new_plan_id not in self.plans:
                raise ValueError(f"Plan {new_plan_id} not found")
                
            subscription = self.subscriptions[subscription_id]
            old_plan = self.plans[subscription.plan_id]
            new_plan = self.plans[new_plan_id]
            
            # Calculate prorated amount if upgrading mid-cycle
            if prorate and new_plan.price > old_plan.price:
                days_remaining = (subscription.current_period_end - datetime.utcnow()).days
                total_days = (subscription.current_period_end - subscription.current_period_start).days
                proration_factor = days_remaining / total_days
                prorated_amount = (new_plan.price - old_plan.price) * Decimal(str(proration_factor))
                
                subscription.metadata["prorated_charge"] = float(prorated_amount)
                
            # Update subscription
            subscription.plan_id = new_plan_id
            subscription.updated_at = datetime.utcnow()
            
            # Update usage tracking for new plan
            self._initialize_usage_tracking(subscription_id, new_plan_id)
            
            logger.info(f"Upgraded subscription {subscription_id} to plan {new_plan_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error upgrading subscription: {e}")
            raise

    async def track_usage(
        self,
        subscription_id: str,
        feature: str,
        usage_amount: int = 1
    ) -> SubscriptionUsage:
        """Track usage for a subscription feature."""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
                
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            # Get or create usage tracking
            if subscription_id not in self.usage_tracking:
                self.usage_tracking[subscription_id] = {}
                
            if feature not in self.usage_tracking[subscription_id]:
                # Create new usage tracking for this feature
                limit = plan.limits.get(feature, 0)
                if limit == -1:  # Unlimited
                    limit = float('inf')
                    
                usage = SubscriptionUsage(
                    subscription_id=subscription_id,
                    feature=feature,
                    usage_count=0,
                    limit=limit,
                    period_start=subscription.current_period_start,
                    period_end=subscription.current_period_end
                )
                self.usage_tracking[subscription_id][feature] = usage
            else:
                usage = self.usage_tracking[subscription_id][feature]
                
            # Update usage
            usage.usage_count += usage_amount
            usage.last_updated = datetime.utcnow()
            
            logger.info(f"Tracked {usage_amount} usage for {feature} in subscription {subscription_id}")
            return usage
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            raise

    async def check_usage_limits(
        self,
        subscription_id: str,
        feature: str,
        requested_amount: int = 1
    ) -> bool:
        """Check if usage request is within limits."""
        try:
            if subscription_id not in self.subscriptions:
                return False
                
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            # Check if feature is allowed in plan
            if feature not in plan.limits:
                return True  # If not limited, allow
                
            limit = plan.limits[feature]
            if limit == -1:  # Unlimited
                return True
                
            # Get current usage
            current_usage = 0
            if (subscription_id in self.usage_tracking and 
                feature in self.usage_tracking[subscription_id]):
                current_usage = self.usage_tracking[subscription_id][feature].usage_count
                
            return (current_usage + requested_amount) <= limit
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            return False

    async def get_subscription_analytics(
        self,
        subscription_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get subscription analytics."""
        try:
            analytics = {
                "total_subscriptions": len(self.subscriptions),
                "active_subscriptions": 0,
                "trial_subscriptions": 0,
                "cancelled_subscriptions": 0,
                "revenue": {
                    "monthly": Decimal('0.00'),
                    "quarterly": Decimal('0.00'),
                    "annually": Decimal('0.00')
                },
                "plan_distribution": {},
                "churn_rate": 0.0,
                "mrr": Decimal('0.00'),  # Monthly Recurring Revenue
                "arpu": Decimal('0.00')  # Average Revenue Per User
            }
            
            total_revenue = Decimal('0.00')
            plan_counts = {}
            
            for sub in self.subscriptions.values():
                # Filter by criteria
                if subscription_id and sub.subscription_id != subscription_id:
                    continue
                if user_id and sub.user_id != user_id:
                    continue
                    
                # Count by status
                if sub.status == SubscriptionStatus.ACTIVE:
                    analytics["active_subscriptions"] += 1
                elif sub.status == SubscriptionStatus.TRIALING:
                    analytics["trial_subscriptions"] += 1
                elif sub.status == SubscriptionStatus.CANCELLED:
                    analytics["cancelled_subscriptions"] += 1
                    
                # Count by plan
                plan = self.plans.get(sub.plan_id)
                if plan:
                    plan_name = plan.name
                    if plan_name not in plan_counts:
                        plan_counts[plan_name] = 0
                    plan_counts[plan_name] += 1
                    
                    # Calculate revenue
                    if sub.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
                        if plan.billing_cycle == BillingCycle.MONTHLY:
                            analytics["revenue"]["monthly"] += plan.price
                            total_revenue += plan.price
                        elif plan.billing_cycle == BillingCycle.QUARTERLY:
                            analytics["revenue"]["quarterly"] += plan.price
                            total_revenue += plan.price / 3  # Monthly equivalent
                        elif plan.billing_cycle == BillingCycle.ANNUALLY:
                            analytics["revenue"]["annually"] += plan.price
                            total_revenue += plan.price / 12  # Monthly equivalent
                            
            analytics["plan_distribution"] = plan_counts
            analytics["mrr"] = total_revenue
            
            # Calculate ARPU
            if analytics["active_subscriptions"] > 0:
                analytics["arpu"] = total_revenue / analytics["active_subscriptions"]
                
            # Calculate churn rate (simplified)
            if analytics["total_subscriptions"] > 0:
                analytics["churn_rate"] = (
                    analytics["cancelled_subscriptions"] / analytics["total_subscriptions"]
                ) * 100
                
            logger.info("Generated subscription analytics")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating subscription analytics: {e}")
            return {}

    def _initialize_usage_tracking(self, subscription_id: str, plan_id: str):
        """Initialize usage tracking for a subscription."""
        try:
            plan = self.plans[plan_id]
            subscription = self.subscriptions[subscription_id]
            
            if subscription_id not in self.usage_tracking:
                self.usage_tracking[subscription_id] = {}
                
            # Initialize tracking for each limited feature
            for feature, limit in plan.limits.items():
                if limit == -1:  # Unlimited
                    limit = float('inf')
                    
                usage = SubscriptionUsage(
                    subscription_id=subscription_id,
                    feature=feature,
                    usage_count=0,
                    limit=limit,
                    period_start=subscription.current_period_start,
                    period_end=subscription.current_period_end
                )
                self.usage_tracking[subscription_id][feature] = usage
                
        except Exception as e:
            logger.error(f"Error initializing usage tracking: {e}")

    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get all subscriptions for a user."""
        try:
            user_subscriptions = [
                sub for sub in self.subscriptions.values()
                if sub.user_id == user_id
            ]
            
            # Sort by creation date, newest first
            user_subscriptions.sort(key=lambda x: x.created_at, reverse=True)
            
            return user_subscriptions
            
        except Exception as e:
            logger.error(f"Error getting user subscriptions: {e}")
            return []

    async def get_subscription_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.subscriptions.get(subscription_id)

    async def get_plan_by_id(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get plan by ID."""
        return self.plans.get(plan_id)

    async def list_available_plans(self, active_only: bool = True) -> List[SubscriptionPlan]:
        """List all available subscription plans."""
        plans = list(self.plans.values())
        
        if active_only:
            plans = [plan for plan in plans if plan.is_active]
            
        # Sort by price
        plans.sort(key=lambda x: x.price)
        
        return plans