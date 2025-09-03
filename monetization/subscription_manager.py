"""Subscription Management System
Advanced subscription lifecycle management with automated billing, 
plan changes, dunning, and customer lifecycle analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json

from .billing_engine import BillingEngine, BillingPlan, Subscription, SubscriptionStatus, BillingCycle, PlanTier
from .payment_processor import PaymentProcessor, PaymentTransaction, PaymentStatus
from .financial_dashboard import financial_dashboard, RevenueType

logger = logging.getLogger(__name__)


class SubscriptionEvent(Enum):
    """Subscription lifecycle events"""
    CREATED = "created"
    ACTIVATED = "activated"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"
    PLAN_CHANGED = "plan_changed"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    REACTIVATED = "reactivated"
    EXPIRED = "expired"


class CustomerSegment(Enum):
    """Customer segmentation"""
    NEW = "new"
    TRIAL = "trial"
    ACTIVE = "active"
    AT_RISK = "at_risk"
    CHURNED = "churned"
    WINBACK = "winback"
    VIP = "vip"


@dataclass
class SubscriptionMetrics:
    """Subscription metrics and analytics"""
    subscription_id: str
    customer_id: str
    lifetime_value: Decimal
    total_payments: int
    successful_payments: int
    failed_payments: int
    days_active: int
    plan_changes: int
    support_tickets: int
    engagement_score: Decimal
    churn_probability: Decimal
    segment: CustomerSegment
    last_activity: datetime


@dataclass
class ChurnPrediction:
    """Churn prediction model result"""
    customer_id: str
    subscription_id: str
    churn_probability: Decimal
    risk_factors: List[str]
    recommended_actions: List[str]
    prediction_date: datetime
    confidence_score: Decimal


@dataclass
class SubscriptionEvent:
    """Subscription event record"""
    id: str
    subscription_id: str
    event_type: SubscriptionEvent
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict] = None


class SubscriptionManager:
    """Comprehensive subscription management system"""
    
    def __init__(self):
        self.billing_engine = BillingEngine()
        self.payment_processor = PaymentProcessor()
        self.subscription_metrics = {}
        self.subscription_events = {}
        self.customer_segments = {}
        self.churn_predictions = {}
        
    async def create_subscription_with_trial(
        self,
        customer_id: str,
        plan_id: str,
        payment_method_id: str,
        trial_days: Optional[int] = None,
        coupon_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create subscription with optional trial period"""
        try:
            # Get plan details
            plan = self.billing_engine.plans.get(plan_id)
            if not plan:
                raise ValueError(f"Plan not found: {plan_id}")
                
            # Apply coupon if provided
            discount_amount = Decimal('0')
            if coupon_code:
                discount_amount = await self._apply_coupon(coupon_code, plan.price)
                
            # Determine trial period
            effective_trial_days = trial_days or plan.trial_period_days
            trial_end = None
            if effective_trial_days > 0:
                trial_end = datetime.now() + timedelta(days=effective_trial_days)
                
            # Create subscription
            subscription = await self.billing_engine.create_subscription(
                customer_id=customer_id,
                plan_id=plan_id,
                payment_method_id=payment_method_id,
                trial_end=trial_end,
                metadata={
                    "coupon_code": coupon_code,
                    "discount_amount": float(discount_amount)
                }
            )
            
            # Record event
            await self._record_subscription_event(
                subscription.id,
                SubscriptionEvent.CREATED,
                {
                    "plan_id": plan_id,
                    "trial_days": effective_trial_days,
                    "discount_amount": float(discount_amount)
                }
            )
            
            # Initialize metrics
            await self._initialize_subscription_metrics(subscription)
            
            # Set up automated billing
            await self._schedule_billing_cycle(subscription)
            
            # Track revenue
            if subscription.status == SubscriptionStatus.ACTIVE:
                await financial_dashboard.track_revenue(
                    amount=plan.price - discount_amount,
                    currency=plan.currency,
                    revenue_type=RevenueType.SUBSCRIPTION,
                    customer_id=customer_id,
                    subscription_id=subscription.id
                )
                
            result = {
                "subscription": asdict(subscription),
                "plan": asdict(plan),
                "trial_end": trial_end.isoformat() if trial_end else None,
                "discount_applied": float(discount_amount),
                "next_billing_date": subscription.current_period_end.isoformat(),
                "status": subscription.status.value
            }
            
            logger.info(f"Subscription created with trial: {subscription.id}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating subscription with trial: {str(e)}")
            raise
            
    async def handle_plan_change(
        self,
        subscription_id: str,
        new_plan_id: str,
        proration: bool = True,
        effective_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Handle subscription plan change with proration"""
        try:
            subscription = self.billing_engine.subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")
                
            old_plan = self.billing_engine.plans.get(subscription.plan_id)
            new_plan = self.billing_engine.plans.get(new_plan_id)
            
            if not new_plan:
                raise ValueError(f"New plan not found: {new_plan_id}")
                
            # Calculate proration if enabled
            proration_amount = Decimal('0')
            proration_credit = Decimal('0')
            
            if proration and effective_date is None:
                proration_result = await self._calculate_plan_change_proration(
                    subscription, old_plan, new_plan
                )
                proration_amount = proration_result["charge"]
                proration_credit = proration_result["credit"]
                
            # Update subscription
            updated_subscription = await self.billing_engine.update_subscription(
                subscription_id=subscription_id,
                plan_id=new_plan_id,
                proration=proration
            )
            
            # Process proration payment if needed
            proration_payment = None
            if proration_amount > 0:
                proration_payment = await self.payment_processor.process_license_payment(
                    license_id=f"proration_{subscription_id}",
                    payer_id=subscription.customer_id,
                    payee_id="platform",
                    amount=proration_amount,
                    currency=new_plan.currency,
                    payment_method_id=subscription.payment_method_id
                )
                
            # Record event
            await self._record_subscription_event(
                subscription_id,
                SubscriptionEvent.PLAN_CHANGED,
                {
                    "old_plan_id": subscription.plan_id,
                    "new_plan_id": new_plan_id,
                    "proration_amount": float(proration_amount),
                    "proration_credit": float(proration_credit)
                }
            )
            
            # Update metrics
            await self._update_subscription_metrics(subscription_id, "plan_change")
            
            # Track revenue change
            revenue_change = new_plan.price - old_plan.price
            if revenue_change != 0:
                await financial_dashboard.track_revenue(
                    amount=revenue_change,
                    currency=new_plan.currency,
                    revenue_type=RevenueType.SUBSCRIPTION,
                    customer_id=subscription.customer_id,
                    subscription_id=subscription_id,
                    metadata={"plan_change": True, "old_plan": old_plan.name, "new_plan": new_plan.name}
                )
                
            result = {
                "subscription": asdict(updated_subscription),
                "old_plan": asdict(old_plan),
                "new_plan": asdict(new_plan),
                "proration": {
                    "charge": float(proration_amount),
                    "credit": float(proration_credit),
                    "payment": asdict(proration_payment) if proration_payment else None
                },
                "effective_date": (effective_date or datetime.now()).isoformat()
            }
            
            logger.info(f"Plan change processed: {subscription_id} from {old_plan.name} to {new_plan.name}")
            return result
            
        except Exception as e:
            logger.error(f"Error handling plan change: {str(e)}")
            raise
            
    async def pause_subscription(
        self,
        subscription_id: str,
        pause_until: datetime,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Pause subscription for a specific period"""
        try:
            subscription = self.billing_engine.subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")
                
            # Store original status
            original_status = subscription.status
            
            # Update subscription metadata
            if not subscription.metadata:
                subscription.metadata = {}
                
            subscription.metadata.update({
                "paused": True,
                "pause_until": pause_until.isoformat(),
                "pause_reason": reason,
                "original_status": original_status.value,
                "paused_at": datetime.now().isoformat()
            })
            
            # Set subscription to paused state (using canceled status with metadata)
            subscription.status = SubscriptionStatus.CANCELED
            
            # Schedule reactivation
            asyncio.create_task(self._schedule_subscription_reactivation(subscription_id, pause_until))
            
            # Record event
            await self._record_subscription_event(
                subscription_id,
                SubscriptionEvent.CANCELED,  # Using canceled event type for pause
                {
                    "action": "pause",
                    "pause_until": pause_until.isoformat(),
                    "reason": reason,
                    "original_status": original_status.value
                }
            )
            
            result = {
                "subscription_id": subscription_id,
                "status": "paused",
                "paused_until": pause_until.isoformat(),
                "reason": reason,
                "can_reactivate_early": True
            }
            
            logger.info(f"Subscription paused: {subscription_id} until {pause_until}")
            return result
            
        except Exception as e:
            logger.error(f"Error pausing subscription: {str(e)}")
            raise
            
    async def reactivate_subscription(
        self,
        subscription_id: str,
        new_payment_method_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Reactivate paused or canceled subscription"""
        try:
            subscription = self.billing_engine.subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")
                
            # Check if subscription can be reactivated
            if subscription.status not in [SubscriptionStatus.CANCELED, SubscriptionStatus.PAST_DUE]:
                raise ValueError(f"Subscription cannot be reactivated from status: {subscription.status}")
                
            # Update payment method if provided
            if new_payment_method_id:
                subscription.payment_method_id = new_payment_method_id
                
            # Restore subscription
            if subscription.metadata and subscription.metadata.get("paused"):
                # Restore from pause
                original_status = SubscriptionStatus(subscription.metadata.get("original_status", "active"))
                subscription.status = original_status
                
                # Clear pause metadata
                subscription.metadata.update({
                    "paused": False,
                    "reactivated_at": datetime.now().isoformat()
                })
            else:
                # Regular reactivation
                subscription.status = SubscriptionStatus.ACTIVE
                
            # Update billing cycle
            subscription.current_period_start = datetime.now()
            plan = self.billing_engine.plans.get(subscription.plan_id)
            
            if plan.billing_cycle == BillingCycle.MONTHLY:
                subscription.current_period_end = subscription.current_period_start + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                subscription.current_period_end = subscription.current_period_start + timedelta(days=365)
                
            # Create immediate invoice for reactivation
            reactivation_invoice = await self.billing_engine.create_invoice(
                customer_id=subscription.customer_id,
                amount=plan.price,
                currency=plan.currency,
                description=f"Subscription reactivation - {plan.name}",
                subscription_id=subscription_id
            )
            
            # Process payment
            if subscription.payment_method_id:
                payment_result = await self.billing_engine.pay_invoice(
                    reactivation_invoice.id,
                    subscription.payment_method_id
                )
                
                if not payment_result["success"]:
                    subscription.status = SubscriptionStatus.PAST_DUE
                    
            # Record event
            await self._record_subscription_event(
                subscription_id,
                SubscriptionEvent.REACTIVATED,
                {
                    "reactivation_type": "manual",
                    "new_payment_method": new_payment_method_id is not None,
                    "invoice_id": reactivation_invoice.id
                }
            )
            
            # Resume billing cycle
            await self._schedule_billing_cycle(subscription)
            
            result = {
                "subscription": asdict(subscription),
                "reactivation_invoice": asdict(reactivation_invoice),
                "status": subscription.status.value,
                "next_billing_date": subscription.current_period_end.isoformat()
            }
            
            logger.info(f"Subscription reactivated: {subscription_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error reactivating subscription: {str(e)}")
            raise
            
    async def analyze_customer_health(self, customer_id: str) -> Dict[str, Any]:
        """Analyze customer health and predict churn risk"""
        try:
            # Get customer subscriptions
            customer_subscriptions = [
                sub for sub in self.billing_engine.subscriptions.values()
                if sub.customer_id == customer_id
            ]
            
            if not customer_subscriptions:
                return {"error": "No subscriptions found for customer"}
                
            # Analyze subscription metrics
            total_revenue = Decimal('0')
            total_payments = 0
            failed_payments = 0
            plan_changes = 0
            
            for subscription in customer_subscriptions:
                metrics = self.subscription_metrics.get(subscription.id)
                if metrics:
                    total_revenue += metrics.lifetime_value
                    total_payments += metrics.total_payments
                    failed_payments += metrics.failed_payments
                    plan_changes += metrics.plan_changes
                    
            # Calculate health scores
            payment_success_rate = ((total_payments - failed_payments) / total_payments * 100) if total_payments > 0 else 100
            
            # Engagement factors
            engagement_factors = []
            risk_factors = []
            
            if payment_success_rate < 80:
                risk_factors.append("Low payment success rate")
            if failed_payments > 2:
                risk_factors.append("Multiple payment failures")
            if plan_changes > 3:
                risk_factors.append("Frequent plan changes")
                
            # Calculate churn probability
            churn_probability = await self._calculate_churn_probability(customer_id, risk_factors)
            
            # Determine customer segment
            segment = await self._determine_customer_segment(customer_id, customer_subscriptions)
            
            # Generate recommendations
            recommendations = await self._generate_customer_recommendations(
                customer_id, churn_probability, risk_factors, segment
            )
            
            health_analysis = {
                "customer_id": customer_id,
                "health_score": float(100 - churn_probability),
                "churn_probability": float(churn_probability),
                "segment": segment.value,
                "lifetime_value": float(total_revenue),
                "metrics": {
                    "total_subscriptions": len(customer_subscriptions),
                    "active_subscriptions": len([s for s in customer_subscriptions if s.status == SubscriptionStatus.ACTIVE]),
                    "total_payments": total_payments,
                    "payment_success_rate": round(payment_success_rate, 2),
                    "plan_changes": plan_changes
                },
                "risk_factors": risk_factors,
                "engagement_factors": engagement_factors,
                "recommendations": recommendations,
                "analysis_date": datetime.now().isoformat()
            }
            
            return health_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing customer health: {str(e)}")
            return {"error": str(e)}
            
    async def get_subscription_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive subscription analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get subscriptions in period
            period_subscriptions = [
                sub for sub in self.billing_engine.subscriptions.values()
                if sub.created_at and start_date <= sub.created_at <= end_date
            ]
            
            # Calculate metrics
            total_subscriptions = len(self.billing_engine.subscriptions)
            new_subscriptions = len(period_subscriptions)
            active_subscriptions = len([s for s in self.billing_engine.subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
            trial_subscriptions = len([s for s in self.billing_engine.subscriptions.values() if s.status == SubscriptionStatus.TRIALING])
            canceled_subscriptions = len([s for s in self.billing_engine.subscriptions.values() if s.status == SubscriptionStatus.CANCELED])
            
            # Calculate MRR
            mrr_result = await self.billing_engine.calculate_mrr()
            
            # Plan distribution
            plan_distribution = {}
            for subscription in self.billing_engine.subscriptions.values():
                plan = self.billing_engine.plans.get(subscription.plan_id)
                if plan:
                    plan_name = plan.name
                    if plan_name not in plan_distribution:
                        plan_distribution[plan_name] = 0
                    plan_distribution[plan_name] += 1
                    
            # Churn analysis
            churn_rate = (canceled_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0
            
            analytics = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": period_days
                },
                "subscription_metrics": {
                    "total_subscriptions": total_subscriptions,
                    "new_subscriptions": new_subscriptions,
                    "active_subscriptions": active_subscriptions,
                    "trial_subscriptions": trial_subscriptions,
                    "canceled_subscriptions": canceled_subscriptions,
                    "churn_rate": round(churn_rate, 2)
                },
                "revenue_metrics": {
                    "mrr": mrr_result.get("total_mrr", 0),
                    "arr": float(mrr_result.get("total_mrr", 0) * 12),
                    "mrr_by_plan": mrr_result.get("mrr_by_plan", {})
                },
                "plan_distribution": plan_distribution,
                "growth_metrics": {
                    "subscription_growth_rate": (new_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0,
                    "net_new_subscriptions": new_subscriptions - canceled_subscriptions
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting subscription analytics: {str(e)}")
            return {"error": str(e)}
            
    async def _apply_coupon(self, coupon_code: str, original_amount: Decimal) -> Decimal:
        """Apply coupon discount"""
        # Simplified coupon system
        coupon_discounts = {
            "WELCOME10": Decimal('0.10'),  # 10% off
            "SAVE20": Decimal('0.20'),     # 20% off
            "FIRST50": Decimal('0.50'),    # 50% off first month
            "ANNUAL25": Decimal('0.25')    # 25% off annual plans
        }
        
        discount_rate = coupon_discounts.get(coupon_code, Decimal('0'))
        return original_amount * discount_rate
        
    async def _record_subscription_event(
        self,
        subscription_id: str,
        event_type: SubscriptionEvent,
        data: Dict[str, Any]
    ):
        """Record subscription lifecycle event"""
        event_id = str(uuid.uuid4())
        
        event = SubscriptionEvent(
            id=event_id,
            subscription_id=subscription_id,
            event_type=event_type,
            timestamp=datetime.now(),
            data=data
        )
        
        self.subscription_events[event_id] = event
        
    async def _initialize_subscription_metrics(self, subscription: Subscription):
        """Initialize metrics tracking for new subscription"""
        metrics = SubscriptionMetrics(
            subscription_id=subscription.id,
            customer_id=subscription.customer_id,
            lifetime_value=Decimal('0'),
            total_payments=0,
            successful_payments=0,
            failed_payments=0,
            days_active=0,
            plan_changes=0,
            support_tickets=0,
            engagement_score=Decimal('50'),  # Start with neutral score
            churn_probability=Decimal('10'),  # Low initial churn risk
            segment=CustomerSegment.NEW,
            last_activity=datetime.now()
        )
        
        self.subscription_metrics[subscription.id] = metrics
        
    async def _update_subscription_metrics(self, subscription_id: str, event_type: str):
        """Update subscription metrics based on event"""
        metrics = self.subscription_metrics.get(subscription_id)
        if not metrics:
            return
            
        if event_type == "payment_success":
            metrics.successful_payments += 1
            metrics.total_payments += 1
            metrics.engagement_score += Decimal('5')
        elif event_type == "payment_failure":
            metrics.failed_payments += 1
            metrics.total_payments += 1
            metrics.churn_probability += Decimal('10')
        elif event_type == "plan_change":
            metrics.plan_changes += 1
            metrics.engagement_score += Decimal('2')
            
        metrics.last_activity = datetime.now()
        
    async def _schedule_billing_cycle(self, subscription: Subscription):
        """Schedule automated billing for subscription"""
        # In production, this would integrate with a job scheduler
        logger.info(f"Billing cycle scheduled for subscription: {subscription.id}")
        
    async def _calculate_plan_change_proration(
        self,
        subscription: Subscription,
        old_plan: BillingPlan,
        new_plan: BillingPlan
    ) -> Dict[str, Decimal]:
        """Calculate proration for plan change"""
        
        # Calculate remaining time in current period
        now = datetime.now()
        total_period = (subscription.current_period_end - subscription.current_period_start).total_seconds()
        remaining_period = (subscription.current_period_end - now).total_seconds()
        
        if total_period <= 0:
            return {"charge": Decimal('0'), "credit": Decimal('0')}
            
        proration_factor = Decimal(str(remaining_period / total_period))
        
        # Calculate proration amounts
        old_plan_credit = old_plan.price * proration_factor
        new_plan_charge = new_plan.price * proration_factor
        
        net_charge = max(Decimal('0'), new_plan_charge - old_plan_credit)
        net_credit = max(Decimal('0'), old_plan_credit - new_plan_charge)
        
        return {
            "charge": net_charge,
            "credit": net_credit
        }
        
    async def _schedule_subscription_reactivation(self, subscription_id: str, reactivate_at: datetime):
        """Schedule automatic subscription reactivation"""
        # In production, this would use a proper job scheduler
        logger.info(f"Subscription reactivation scheduled for {subscription_id} at {reactivate_at}")
        
    async def _calculate_churn_probability(self, customer_id: str, risk_factors: List[str]) -> Decimal:
        """Calculate churn probability using risk factors"""
        
        base_probability = Decimal('10')  # 10% base churn risk
        
        # Risk factor weights
        risk_weights = {
            "Low payment success rate": Decimal('20'),
            "Multiple payment failures": Decimal('15'),
            "Frequent plan changes": Decimal('10'),
            "No recent activity": Decimal('25'),
            "Downgraded plan": Decimal('12'),
            "Support complaints": Decimal('8')
        }
        
        total_risk = base_probability
        for factor in risk_factors:
            weight = risk_weights.get(factor, Decimal('5'))
            total_risk += weight
            
        # Cap at 95%
        return min(total_risk, Decimal('95'))
        
    async def _determine_customer_segment(
        self,
        customer_id: str,
        subscriptions: List[Subscription]
    ) -> CustomerSegment:
        """Determine customer segment based on behavior"""
        
        active_subs = [s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE]
        trial_subs = [s for s in subscriptions if s.status == SubscriptionStatus.TRIALING]
        canceled_subs = [s for s in subscriptions if s.status == SubscriptionStatus.CANCELED]
        
        # Determine segment
        if trial_subs:
            return CustomerSegment.TRIAL
        elif not active_subs and canceled_subs:
            return CustomerSegment.CHURNED
        elif active_subs:
            # Check for high-value customers
            total_value = sum(
                self.subscription_metrics.get(s.id, SubscriptionMetrics(
                    subscription_id=s.id,
                    customer_id=customer_id,
                    lifetime_value=Decimal('0'),
                    total_payments=0,
                    successful_payments=0,
                    failed_payments=0,
                    days_active=0,
                    plan_changes=0,
                    support_tickets=0,
                    engagement_score=Decimal('50'),
                    churn_probability=Decimal('10'),
                    segment=CustomerSegment.NEW,
                    last_activity=datetime.now()
                )).lifetime_value for s in active_subs
            )
            
            if total_value > Decimal('1000'):
                return CustomerSegment.VIP
            else:
                return CustomerSegment.ACTIVE
        else:
            return CustomerSegment.NEW
            
    async def _generate_customer_recommendations(
        self,
        customer_id: str,
        churn_probability: Decimal,
        risk_factors: List[str],
        segment: CustomerSegment
    ) -> List[str]:
        """Generate recommendations for customer retention"""
        
        recommendations = []
        
        if churn_probability > 70:
            recommendations.append("High churn risk - immediate intervention required")
            recommendations.append("Offer retention discount or plan downgrade")
            recommendations.append("Schedule customer success call")
            
        if "Multiple payment failures" in risk_factors:
            recommendations.append("Update payment method required")
            recommendations.append("Consider payment plan or alternative payment options")
            
        if "Frequent plan changes" in risk_factors:
            recommendations.append("Review plan features alignment with usage")
            recommendations.append("Provide plan optimization consultation")
            
        if segment == CustomerSegment.TRIAL:
            recommendations.append("Provide onboarding assistance")
            recommendations.append("Highlight key features and value proposition")
            
        if segment == CustomerSegment.VIP:
            recommendations.append("Offer premium support and exclusive features")
            recommendations.append("Consider loyalty rewards program")
            
        return recommendations


# Global subscription manager instance
subscription_manager = SubscriptionManager()


async def create_trial_subscription(
    customer_id: str,
    plan_id: str,
    payment_method_id: str,
    trial_days: int = 14
) -> Dict[str, Any]:
    """Global function to create trial subscription"""
    return await subscription_manager.create_subscription_with_trial(
        customer_id=customer_id,
        plan_id=plan_id,
        payment_method_id=payment_method_id,
        trial_days=trial_days
    )


async def upgrade_subscription(
    subscription_id: str,
    new_plan_id: str
) -> Dict[str, Any]:
    """Global function to upgrade subscription"""
    return await subscription_manager.handle_plan_change(
        subscription_id=subscription_id,
        new_plan_id=new_plan_id,
        proration=True
    )