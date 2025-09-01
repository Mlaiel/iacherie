"""Advanced Subscription Management System
Complete subscription lifecycle management with prorations and billing automation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid

from .billing_engine import ComprehensiveBillingEngine, BillingCycle, SubscriptionStatus, Subscription

logger = logging.getLogger(__name__)


class SubscriptionAction(Enum):
    """Subscription management actions"""
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    REACTIVATE = "reactivate"


class ProrationMethod(Enum):
    """Proration calculation methods"""
    IMMEDIATE = "immediate"      # Apply changes immediately with proration
    NEXT_CYCLE = "next_cycle"   # Apply changes at next billing cycle
    NO_PRORATION = "no_proration"  # Change without proration


@dataclass
class SubscriptionPlan:
    """Subscription plan definition"""
    id: str
    name: str
    description: str
    base_price: Decimal
    currency: str
    billing_cycles: List[BillingCycle]
    features: List[str]
    trial_days: int = 0
    setup_fee: Decimal = Decimal('0')
    cancellation_policy: str = "anytime"
    usage_limits: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubscriptionModification:
    """Record of subscription modifications for audit trail"""
    id: str
    subscription_id: str
    action: SubscriptionAction
    old_plan_id: Optional[str]
    new_plan_id: Optional[str]
    old_amount: Optional[Decimal]
    new_amount: Optional[Decimal]
    proration_amount: Decimal
    effective_date: datetime
    reason: str
    user_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class AdvancedSubscriptionManager:
    """Advanced subscription management with comprehensive features"""
    
    def __init__(self, billing_engine: ComprehensiveBillingEngine):
        self.billing_engine = billing_engine
        self.plans: Dict[str, SubscriptionPlan] = {}
        self.modifications: Dict[str, SubscriptionModification] = {}
        
        # Initialize default plans
        self._initialize_default_plans()
    
    def _initialize_default_plans(self):
        """Initialize default subscription plans"""
        # Basic plan
        self.plans["basic"] = SubscriptionPlan(
            id="basic",
            name="Basic Plan",
            description="Essential features for individuals",
            base_price=Decimal("9.99"),
            currency="EUR",
            billing_cycles=[BillingCycle.MONTHLY, BillingCycle.ANNUAL],
            features=["basic_protection", "email_support"],
            trial_days=7,
            usage_limits={"api_calls": 1000, "storage_gb": 5}
        )
        
        # Professional plan
        self.plans["professional"] = SubscriptionPlan(
            id="professional",
            name="Professional Plan",
            description="Advanced features for professionals",
            base_price=Decimal("29.99"),
            currency="EUR",
            billing_cycles=[BillingCycle.MONTHLY, BillingCycle.ANNUAL],
            features=["advanced_protection", "priority_support", "analytics"],
            trial_days=14,
            usage_limits={"api_calls": 10000, "storage_gb": 50}
        )
        
        # Enterprise plan
        self.plans["enterprise"] = SubscriptionPlan(
            id="enterprise",
            name="Enterprise Plan",
            description="Full features for large organizations",
            base_price=Decimal("99.99"),
            currency="EUR",
            billing_cycles=[BillingCycle.MONTHLY, BillingCycle.QUARTERLY, BillingCycle.ANNUAL],
            features=["full_protection", "dedicated_support", "custom_analytics", "api_access"],
            trial_days=30,
            setup_fee=Decimal("199.99"),
            usage_limits={"api_calls": 100000, "storage_gb": 500}
        )
    
    async def create_subscription_with_plan(
        self,
        customer_id: str,
        plan_id: str,
        billing_cycle: BillingCycle,
        custom_pricing: Optional[Decimal] = None,
        coupon_code: Optional[str] = None,
        payment_method_id: Optional[str] = None
    ) -> Subscription:
        """Create subscription based on predefined plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        if billing_cycle not in plan.billing_cycles:
            raise ValueError(f"Billing cycle {billing_cycle.value} not supported for plan {plan_id}")
        
        # Calculate pricing
        amount = custom_pricing or plan.base_price
        
        # Apply discount for annual billing
        if billing_cycle == BillingCycle.ANNUAL:
            amount = amount * Decimal('10')  # 10 months price for annual
        elif billing_cycle == BillingCycle.QUARTERLY:
            amount = amount * Decimal('2.7')  # 2.7 months price for quarterly
        
        # Apply coupon if provided
        if coupon_code:
            amount = await self._apply_coupon(amount, coupon_code)
        
        # Create subscription
        subscription = await self.billing_engine.create_subscription(
            customer_id=customer_id,
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            amount=amount,
            currency=plan.currency,
            trial_days=plan.trial_days,
            payment_method_id=payment_method_id
        )
        
        # Add setup fee if applicable
        if plan.setup_fee > 0:
            await self._charge_setup_fee(subscription.id, plan.setup_fee)
        
        logger.info(f"Created subscription {subscription.id} with plan {plan_id}")
        return subscription
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        proration_method: ProrationMethod = ProrationMethod.IMMEDIATE,
        effective_date: Optional[datetime] = None,
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """Upgrade subscription to higher tier plan"""
        subscription = self.billing_engine.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        old_plan = self.plans.get(subscription.plan_id)
        new_plan = self.plans.get(new_plan_id)
        
        if not old_plan or not new_plan:
            raise ValueError("Invalid plan ID")
        
        if new_plan.base_price <= old_plan.base_price:
            raise ValueError("New plan must be higher tier for upgrade")
        
        effective_date = effective_date or datetime.now()
        
        # Calculate new amount based on billing cycle
        if subscription.billing_cycle == BillingCycle.ANNUAL:
            new_amount = new_plan.base_price * Decimal('10')
        elif subscription.billing_cycle == BillingCycle.QUARTERLY:
            new_amount = new_plan.base_price * Decimal('2.7')
        else:
            new_amount = new_plan.base_price
        
        proration_amount = Decimal('0')
        
        if proration_method == ProrationMethod.IMMEDIATE:
            # Calculate proration
            proration_amount = await self.billing_engine.calculate_proration(
                subscription_id, new_amount, effective_date
            )
            
            # Update subscription immediately
            subscription.plan_id = new_plan_id
            subscription.amount = new_amount
            
            # Generate prorated invoice if positive amount
            if proration_amount > 0:
                await self.billing_engine.generate_invoice(
                    subscription_id,
                    custom_amount=proration_amount
                )
        
        elif proration_method == ProrationMethod.NEXT_CYCLE:
            # Schedule change for next billing cycle
            subscription.metadata["scheduled_plan_change"] = {
                "new_plan_id": new_plan_id,
                "new_amount": float(new_amount),
                "effective_date": subscription.next_billing_date.isoformat()
            }
        
        # Record modification
        modification = SubscriptionModification(
            id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            action=SubscriptionAction.UPGRADE,
            old_plan_id=old_plan.id,
            new_plan_id=new_plan.id,
            old_amount=subscription.amount if proration_method == ProrationMethod.IMMEDIATE else None,
            new_amount=new_amount,
            proration_amount=proration_amount,
            effective_date=effective_date,
            reason="customer_upgrade",
            user_id=user_id
        )
        
        self.modifications[modification.id] = modification
        
        logger.info(f"Upgraded subscription {subscription_id} from {old_plan.id} to {new_plan.id}")
        
        return {
            "success": True,
            "modification_id": modification.id,
            "proration_amount": float(proration_amount),
            "effective_date": effective_date.isoformat(),
            "new_plan": new_plan.name
        }
    
    async def downgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        proration_method: ProrationMethod = ProrationMethod.NEXT_CYCLE,
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """Downgrade subscription to lower tier plan"""
        subscription = self.billing_engine.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        old_plan = self.plans.get(subscription.plan_id)
        new_plan = self.plans.get(new_plan_id)
        
        if not old_plan or not new_plan:
            raise ValueError("Invalid plan ID")
        
        if new_plan.base_price >= old_plan.base_price:
            raise ValueError("New plan must be lower tier for downgrade")
        
        # Calculate new amount
        if subscription.billing_cycle == BillingCycle.ANNUAL:
            new_amount = new_plan.base_price * Decimal('10')
        elif subscription.billing_cycle == BillingCycle.QUARTERLY:
            new_amount = new_plan.base_price * Decimal('2.7')
        else:
            new_amount = new_plan.base_price
        
        effective_date = datetime.now()
        proration_amount = Decimal('0')
        
        if proration_method == ProrationMethod.IMMEDIATE:
            # Immediate downgrade with credit
            proration_amount = await self.billing_engine.calculate_proration(
                subscription_id, new_amount, effective_date
            )
            
            subscription.plan_id = new_plan_id
            subscription.amount = new_amount
            
            # Issue credit for the difference (negative proration)
            if proration_amount < 0:
                await self._issue_account_credit(
                    subscription.customer_id, 
                    abs(proration_amount),
                    f"Downgrade credit for subscription {subscription_id}"
                )
        
        else:
            # Schedule downgrade for next billing cycle
            subscription.metadata["scheduled_plan_change"] = {
                "new_plan_id": new_plan_id,
                "new_amount": float(new_amount),
                "effective_date": subscription.next_billing_date.isoformat()
            }
            effective_date = subscription.next_billing_date
        
        # Record modification
        modification = SubscriptionModification(
            id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            action=SubscriptionAction.DOWNGRADE,
            old_plan_id=old_plan.id,
            new_plan_id=new_plan.id,
            old_amount=subscription.amount,
            new_amount=new_amount,
            proration_amount=proration_amount,
            effective_date=effective_date,
            reason="customer_downgrade",
            user_id=user_id
        )
        
        self.modifications[modification.id] = modification
        
        logger.info(f"Downgraded subscription {subscription_id} from {old_plan.id} to {new_plan.id}")
        
        return {
            "success": True,
            "modification_id": modification.id,
            "credit_amount": float(abs(proration_amount)) if proration_amount < 0 else 0,
            "effective_date": effective_date.isoformat(),
            "new_plan": new_plan.name
        }
    
    async def pause_subscription(
        self,
        subscription_id: str,
        pause_until: Optional[datetime] = None,
        reason: str = "customer_request",
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """Pause subscription billing"""
        subscription = self.billing_engine.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ValueError("Can only pause active subscriptions")
        
        # Set pause period
        pause_until = pause_until or (datetime.now() + timedelta(days=30))
        
        # Update subscription
        subscription.status = SubscriptionStatus.SUSPENDED
        subscription.metadata["paused_until"] = pause_until.isoformat()
        subscription.metadata["paused_at"] = datetime.now().isoformat()
        subscription.metadata["pause_reason"] = reason
        
        # Adjust next billing date
        pause_duration = pause_until - datetime.now()
        subscription.next_billing_date += pause_duration
        subscription.current_period_end += pause_duration
        
        # Record modification
        modification = SubscriptionModification(
            id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            action=SubscriptionAction.PAUSE,
            old_plan_id=subscription.plan_id,
            new_plan_id=subscription.plan_id,
            old_amount=subscription.amount,
            new_amount=subscription.amount,
            proration_amount=Decimal('0'),
            effective_date=datetime.now(),
            reason=reason,
            user_id=user_id,
            metadata={"pause_until": pause_until.isoformat()}
        )
        
        self.modifications[modification.id] = modification
        
        logger.info(f"Paused subscription {subscription_id} until {pause_until}")
        
        return {
            "success": True,
            "modification_id": modification.id,
            "paused_until": pause_until.isoformat(),
            "next_billing_date": subscription.next_billing_date.isoformat()
        }
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_immediately: bool = False,
        reason: str = "customer_request",
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """Cancel subscription"""
        subscription = self.billing_engine.subscriptions.get(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        effective_date = datetime.now()
        
        if cancel_immediately:
            # Immediate cancellation
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = effective_date
            
            # Calculate refund if applicable
            refund_amount = await self._calculate_cancellation_refund(subscription)
            
            if refund_amount > 0:
                await self._issue_account_credit(
                    subscription.customer_id,
                    refund_amount,
                    f"Cancellation refund for subscription {subscription_id}"
                )
        else:
            # Cancel at end of current period
            subscription.metadata["cancel_at_period_end"] = True
            subscription.metadata["cancellation_date"] = subscription.current_period_end.isoformat()
            effective_date = subscription.current_period_end
        
        # Record modification
        modification = SubscriptionModification(
            id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            action=SubscriptionAction.CANCEL,
            old_plan_id=subscription.plan_id,
            new_plan_id=None,
            old_amount=subscription.amount,
            new_amount=Decimal('0'),
            proration_amount=Decimal('0'),
            effective_date=effective_date,
            reason=reason,
            user_id=user_id,
            metadata={
                "immediate": cancel_immediately,
                "refund_amount": float(refund_amount) if cancel_immediately else 0
            }
        )
        
        self.modifications[modification.id] = modification
        
        logger.info(f"Cancelled subscription {subscription_id} {'immediately' if cancel_immediately else 'at period end'}")
        
        return {
            "success": True,
            "modification_id": modification.id,
            "effective_date": effective_date.isoformat(),
            "refund_amount": float(refund_amount) if cancel_immediately else 0,
            "immediate": cancel_immediately
        }
    
    async def get_subscription_analytics(
        self,
        customer_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get subscription analytics and metrics"""
        # Filter subscriptions
        subscriptions = list(self.billing_engine.subscriptions.values())
        
        if customer_id:
            subscriptions = [s for s in subscriptions if s.customer_id == customer_id]
        
        if plan_id:
            subscriptions = [s for s in subscriptions if s.plan_id == plan_id]
        
        if start_date:
            subscriptions = [s for s in subscriptions if s.created_at >= start_date]
        
        if end_date:
            subscriptions = [s for s in subscriptions if s.created_at <= end_date]
        
        # Calculate metrics
        total_subscriptions = len(subscriptions)
        active_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE])
        cancelled_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.CANCELLED])
        
        total_mrr = sum(
            s.amount for s in subscriptions 
            if s.status == SubscriptionStatus.ACTIVE and s.billing_cycle == BillingCycle.MONTHLY
        )
        
        # Plan distribution
        plan_distribution = {}
        for subscription in subscriptions:
            plan_distribution[subscription.plan_id] = plan_distribution.get(subscription.plan_id, 0) + 1
        
        # Churn analysis
        modifications = list(self.modifications.values())
        cancellations = [m for m in modifications if m.action == SubscriptionAction.CANCEL]
        upgrades = [m for m in modifications if m.action == SubscriptionAction.UPGRADE]
        downgrades = [m for m in modifications if m.action == SubscriptionAction.DOWNGRADE]
        
        analytics = {
            "period_start": start_date.isoformat() if start_date else None,
            "period_end": end_date.isoformat() if end_date else None,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "cancelled_subscriptions": cancelled_subscriptions,
            "churn_rate": (cancelled_subscriptions / total_subscriptions) if total_subscriptions > 0 else 0,
            "monthly_recurring_revenue": float(total_mrr),
            "plan_distribution": plan_distribution,
            "modifications": {
                "cancellations": len(cancellations),
                "upgrades": len(upgrades),
                "downgrades": len(downgrades)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return analytics
    
    async def _apply_coupon(self, amount: Decimal, coupon_code: str) -> Decimal:
        """Apply coupon discount (simplified implementation)"""
        # This would integrate with a coupon management system
        coupon_discounts = {
            "WELCOME10": Decimal("0.10"),  # 10% off
            "SAVE20": Decimal("0.20"),     # 20% off
            "HALFPRICE": Decimal("0.50")   # 50% off
        }
        
        discount = coupon_discounts.get(coupon_code, Decimal("0"))
        return amount * (Decimal("1") - discount)
    
    async def _charge_setup_fee(self, subscription_id: str, setup_fee: Decimal):
        """Charge one-time setup fee"""
        invoice = await self.billing_engine.generate_invoice(
            subscription_id,
            custom_amount=setup_fee
        )
        invoice.metadata["fee_type"] = "setup"
        logger.info(f"Charged setup fee {setup_fee} for subscription {subscription_id}")
    
    async def _issue_account_credit(self, customer_id: str, amount: Decimal, reason: str):
        """Issue account credit to customer"""
        # This would integrate with customer credit management
        logger.info(f"Issued credit {amount} to customer {customer_id}: {reason}")
    
    async def _calculate_cancellation_refund(self, subscription: Subscription) -> Decimal:
        """Calculate refund amount for immediate cancellation"""
        # Calculate unused portion of current period
        now = datetime.now()
        period_total_days = (subscription.current_period_end - subscription.current_period_start).days
        remaining_days = (subscription.current_period_end - now).days
        
        if remaining_days <= 0:
            return Decimal('0')
        
        daily_rate = subscription.amount / period_total_days
        refund_amount = daily_rate * remaining_days
        
        return max(Decimal('0'), refund_amount)