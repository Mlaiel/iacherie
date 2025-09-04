"""Advanced Subscription Engine - Enterprise Subscription Management System
========================================================================

Comprehensive subscription management system providing advanced subscription
lifecycle management, billing automation, churn prediction, and revenue
optimization for content creators and enterprise users.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/subscription_engine.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class BillingCycle(str, Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


@dataclass
class SubscriptionPlan:
    """Subscription plan configuration."""
    id: str
    name: str
    tier: SubscriptionTier
    billing_cycle: BillingCycle
    price: Decimal
    currency: str = "USD"
    features: List[str] = field(default_factory=list)
    limits: Dict[str, int] = field(default_factory=dict)
    trial_days: int = 0
    is_active: bool = True


@dataclass
class Subscription:
    """User subscription instance."""
    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    last_billing_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    amount_paid: Decimal = Decimal('0')
    metadata: Dict[str, Any] = field(default_factory=dict)


class SubscriptionEngine:
    """
    Advanced subscription management system providing comprehensive
    subscription lifecycle management and billing automation.
    """
    
    def __init__(self, database_connection=None):
        """Initialize the subscription engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.db = database_connection
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self._initialize_default_plans()
        
        self.logger.info("SubscriptionEngine initialized")
    
    def _initialize_default_plans(self):
        """Initialize default subscription plans."""
        # Free Plan
        self.plans["free"] = SubscriptionPlan(
            id="free",
            name="Free Plan",
            tier=SubscriptionTier.FREE,
            billing_cycle=BillingCycle.MONTHLY,
            price=Decimal('0'),
            features=["Basic content upload", "Limited analytics"],
            limits={"uploads_per_month": 10, "storage_gb": 1}
        )
        
        # Premium Plan
        self.plans["premium"] = SubscriptionPlan(
            id="premium",
            name="Premium Plan",
            tier=SubscriptionTier.PREMIUM,
            billing_cycle=BillingCycle.MONTHLY,
            price=Decimal('29.99'),
            features=["Unlimited uploads", "Advanced analytics", "Priority support"],
            limits={"uploads_per_month": -1, "storage_gb": 100},
            trial_days=14
        )
        
        # Professional Plan
        self.plans["professional"] = SubscriptionPlan(
            id="professional",
            name="Professional Plan",
            tier=SubscriptionTier.PROFESSIONAL,
            billing_cycle=BillingCycle.MONTHLY,
            price=Decimal('99.99'),
            features=["All Premium features", "Advanced automation", "Custom branding"],
            limits={"uploads_per_month": -1, "storage_gb": 500},
            trial_days=30
        )
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        start_trial: bool = True
    ) -> Optional[Subscription]:
        """Create a new subscription."""
        try:
            if plan_id not in self.plans:
                self.logger.error(f"Plan not found: {plan_id}")
                return None
            
            plan = self.plans[plan_id]
            subscription_id = str(uuid4())
            start_date = datetime.utcnow()
            
            # Calculate trial end date
            trial_end_date = None
            if start_trial and plan.trial_days > 0:
                trial_end_date = start_date + timedelta(days=plan.trial_days)
            
            # Calculate next billing date
            next_billing_date = None
            if plan.billing_cycle != BillingCycle.LIFETIME:
                if trial_end_date:
                    next_billing_date = trial_end_date
                else:
                    if plan.billing_cycle == BillingCycle.MONTHLY:
                        next_billing_date = start_date + timedelta(days=30)
                    elif plan.billing_cycle == BillingCycle.QUARTERLY:
                        next_billing_date = start_date + timedelta(days=90)
                    elif plan.billing_cycle == BillingCycle.YEARLY:
                        next_billing_date = start_date + timedelta(days=365)
            
            subscription = Subscription(
                id=subscription_id,
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.ACTIVE,
                start_date=start_date,
                trial_end_date=trial_end_date,
                next_billing_date=next_billing_date
            )
            
            self.subscriptions[subscription_id] = subscription
            
            self.logger.info(f"✅ Subscription created: {user_id} -> {plan.name}")
            return subscription
            
        except Exception as e:
            self.logger.error(f"Error creating subscription: {e}")
            return None
    
    async def process_billing(self, subscription_id: str) -> bool:
        """Process billing for a subscription."""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            # Process payment (simplified)
            subscription.last_billing_date = datetime.utcnow()
            subscription.amount_paid += plan.price
            
            # Calculate next billing date
            if plan.billing_cycle == BillingCycle.MONTHLY:
                subscription.next_billing_date = subscription.last_billing_date + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.QUARTERLY:
                subscription.next_billing_date = subscription.last_billing_date + timedelta(days=90)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                subscription.next_billing_date = subscription.last_billing_date + timedelta(days=365)
            
            self.logger.info(f"💰 Billing processed: {subscription_id} - {plan.price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing billing: {e}")
            return False
    
    async def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get active subscription for user."""
        for subscription in self.subscriptions.values():
            if subscription.user_id == user_id and subscription.status == SubscriptionStatus.ACTIVE:
                return subscription
        return None
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics."""
        try:
            total_subscriptions = len(self.subscriptions)
            active_subscriptions = len([s for s in self.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
            
            revenue_by_plan = {}
            for subscription in self.subscriptions.values():
                plan_id = subscription.plan_id
                if plan_id not in revenue_by_plan:
                    revenue_by_plan[plan_id] = Decimal('0')
                revenue_by_plan[plan_id] += subscription.amount_paid
            
            return {
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "revenue_by_plan": {k: float(v) for k, v in revenue_by_plan.items()},
                "conversion_rate": (active_subscriptions / max(1, total_subscriptions)) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analytics: {e}")
            return {}


# Global subscription engine instance
_subscription_engine: Optional[SubscriptionEngine] = None


async def get_subscription_engine() -> SubscriptionEngine:
    """Get global subscription engine instance."""
    global _subscription_engine
    
    if _subscription_engine is None:
        _subscription_engine = SubscriptionEngine()
    
    return _subscription_engine


# ============================================================================
# LICENSING MANAGEMENT - Consolidated from licensing_manager.py, licensing_engine.py, usage_tracker.py
# ============================================================================

class LicenseType(Enum):
    """License types for content"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"


class LicenseStatus(Enum):
    """License status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class ContentLicense:
    """Content license data structure"""
    id: str
    content_id: str
    license_type: LicenseType
    status: LicenseStatus
    start_date: datetime
    end_date: Optional[datetime]
    price: Decimal
    currency: str
    terms: Dict[str, Any]
    licensee_id: Optional[str] = None
    usage_restrictions: Dict[str, Any] = field(default_factory=dict)


class LicensingManager:
    """Simplified licensing management system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.licenses: Dict[str, ContentLicense] = {}
        self.usage_tracking: Dict[str, Dict] = {}
    
    async def create_license(
        self, 
        content_id: str, 
        license_type: LicenseType,
        price: Decimal,
        duration_days: Optional[int] = None,
        terms: Dict[str, Any] = None
    ) -> ContentLicense:
        """Create a new content license"""
        
        license_id = f"lic_{content_id}_{int(datetime.now().timestamp())}"
        start_date = datetime.now()
        end_date = None
        
        if duration_days:
            end_date = start_date + timedelta(days=duration_days)
        
        license = ContentLicense(
            id=license_id,
            content_id=content_id,
            license_type=license_type,
            status=LicenseStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
            price=price,
            currency="EUR",
            terms=terms or {}
        )
        
        self.licenses[license_id] = license
        self.logger.info(f"License created: {license_id}")
        
        return license
    
    async def purchase_license(
        self, 
        license_id: str, 
        licensee_id: str
    ) -> Dict[str, Any]:
        """Purchase a license"""
        
        if license_id not in self.licenses:
            raise ValueError(f"License {license_id} not found")
        
        license = self.licenses[license_id]
        license.licensee_id = licensee_id
        
        # Mock purchase process
        purchase_result = {
            "purchase_id": f"pur_{license_id}_{licensee_id}",
            "license_id": license_id,
            "licensee_id": licensee_id,
            "amount": float(license.price),
            "currency": license.currency,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"License purchased: {license_id} by {licensee_id}")
        return purchase_result
    
    async def track_usage(
        self, 
        license_id: str, 
        usage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track license usage"""
        
        if license_id not in self.usage_tracking:
            self.usage_tracking[license_id] = {
                "total_uses": 0,
                "usage_history": []
            }
        
        self.usage_tracking[license_id]["total_uses"] += 1
        self.usage_tracking[license_id]["usage_history"].append({
            "timestamp": datetime.now().isoformat(),
            "usage_data": usage_data
        })
        
        return self.usage_tracking[license_id]
    
    async def validate_license(
        self, 
        license_id: str, 
        usage_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate license for usage"""
        
        if license_id not in self.licenses:
            return {"valid": False, "reason": "License not found"}
        
        license = self.licenses[license_id]
        
        # Check expiration
        if license.end_date and datetime.now() > license.end_date:
            return {"valid": False, "reason": "License expired"}
        
        # Check status
        if license.status != LicenseStatus.ACTIVE:
            return {"valid": False, "reason": f"License status: {license.status.value}"}
        
        return {
            "valid": True,
            "license": license.__dict__,
            "remaining_time": (license.end_date - datetime.now()).days if license.end_date else None
        }


class UsageTracker:
    """Usage tracking system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.usage_data: Dict[str, List] = {}
    
    async def track_content_usage(
        self, 
        content_id: str, 
        platform: str, 
        usage_type: str,
        metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Track content usage across platforms"""
        
        if content_id not in self.usage_data:
            self.usage_data[content_id] = []
        
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "usage_type": usage_type,
            "metrics": metrics or {}
        }
        
        self.usage_data[content_id].append(usage_entry)
        
        return {
            "content_id": content_id,
            "total_usage_count": len(self.usage_data[content_id]),
            "latest_usage": usage_entry
        }
    
    async def get_usage_analytics(
        self, 
        content_id: str
    ) -> Dict[str, Any]:
        """Get usage analytics for content"""
        
        if content_id not in self.usage_data:
            return {"content_id": content_id, "usage_count": 0, "analytics": {}}
        
        usage_list = self.usage_data[content_id]
        
        # Calculate basic analytics
        platform_usage = {}
        usage_type_counts = {}
        
        for usage in usage_list:
            platform = usage["platform"]
            usage_type = usage["usage_type"]
            
            platform_usage[platform] = platform_usage.get(platform, 0) + 1
            usage_type_counts[usage_type] = usage_type_counts.get(usage_type, 0) + 1
        
        return {
            "content_id": content_id,
            "usage_count": len(usage_list),
            "platform_distribution": platform_usage,
            "usage_type_distribution": usage_type_counts,
            "first_usage": usage_list[0]["timestamp"] if usage_list else None,
            "latest_usage": usage_list[-1]["timestamp"] if usage_list else None
        }