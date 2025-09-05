"""Subscription Handler - IA Influencer Agent Platform
==================================================

Advanced subscription management system with automated billing,
tier management, and customer lifecycle optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Subscription status types."""
    ACTIVE = "active"
    TRIAL = "trial"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"


class BillingCycle(Enum):
    """Billing cycle types."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class SubscriptionTier:
    """Subscription tier definition."""
    tier_id: str
    name: str
    price: Decimal
    billing_cycle: BillingCycle
    features: List[str]
    limits: Dict[str, Any]
    trial_days: int = 0


@dataclass
class Subscription:
    """Subscription instance."""
    subscription_id: str
    customer_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    start_date: datetime
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime
    total_paid: Decimal
    metadata: Dict[str, Any]


class SubscriptionHandler:
    """Advanced subscription management system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize subscription handler."""
        self.config = config or {}
        self.subscription_tiers: Dict[str, SubscriptionTier] = {}
        self.active_subscriptions: Dict[str, Subscription] = {}
        self.billing_history: List[Dict[str, Any]] = []
        self._initialize_default_tiers()
        
    async def create_subscription(
        self,
        customer_id: str,
        tier_id: str,
        payment_method: Dict[str, Any],
        promo_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new subscription."""
        try:
            # Get subscription tier
            tier = self.subscription_tiers.get(tier_id)
            if not tier:
                raise ValueError(f"Subscription tier {tier_id} not found")
            
            # Apply promo code if provided
            discounted_price = await self._apply_promo_code(tier.price, promo_code)
            
            # Calculate billing dates
            start_date = datetime.utcnow()
            current_period_end = await self._calculate_period_end(start_date, tier.billing_cycle)
            
            # Create subscription
            subscription = Subscription(
                subscription_id=str(uuid.uuid4()),
                customer_id=customer_id,
                tier=tier,
                status=SubscriptionStatus.TRIAL if tier.trial_days > 0 else SubscriptionStatus.ACTIVE,
                start_date=start_date,
                current_period_start=start_date,
                current_period_end=current_period_end,
                next_billing_date=current_period_end if tier.trial_days == 0 else start_date + timedelta(days=tier.trial_days),
                total_paid=Decimal('0'),
                metadata={
                    'promo_code': promo_code,
                    'discounted_price': float(discounted_price),
                    'payment_method': payment_method
                }
            )
            
            # Store subscription
            self.active_subscriptions[subscription.subscription_id] = subscription
            
            # Process initial payment if not trial
            if tier.trial_days == 0:
                payment_result = await self._process_payment(subscription, discounted_price)
                if not payment_result['success']:
                    raise Exception(f"Payment failed: {payment_result['error']}")
            
            return {
                "subscription_id": subscription.subscription_id,
                "status": subscription.status.value,
                "tier": tier.name,
                "next_billing_date": subscription.next_billing_date.isoformat(),
                "amount": float(discounted_price),
                "trial_days": tier.trial_days,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            raise
    
    async def manage_subscription_lifecycle(
        self,
        subscription_id: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manage subscription lifecycle (upgrade, downgrade, pause, cancel)."""
        try:
            subscription = self.active_subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            parameters = parameters or {}
            
            if action == "upgrade":
                return await self._upgrade_subscription(subscription, parameters)
            elif action == "downgrade":
                return await self._downgrade_subscription(subscription, parameters)
            elif action == "pause":
                return await self._pause_subscription(subscription, parameters)
            elif action == "resume":
                return await self._resume_subscription(subscription, parameters)
            elif action == "cancel":
                return await self._cancel_subscription(subscription, parameters)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Subscription lifecycle management failed: {e}")
            raise
    
    async def process_billing_cycle(self) -> Dict[str, Any]:
        """Process billing for all active subscriptions."""
        try:
            billing_results = []
            successful_billings = 0
            failed_billings = 0
            total_revenue = Decimal('0')
            
            current_time = datetime.utcnow()
            
            for subscription in self.active_subscriptions.values():
                if subscription.next_billing_date <= current_time:
                    billing_result = await self._process_subscription_billing(subscription)
                    billing_results.append(billing_result)
                    
                    if billing_result['success']:
                        successful_billings += 1
                        total_revenue += Decimal(str(billing_result['amount']))
                    else:
                        failed_billings += 1
            
            # Generate billing summary
            billing_summary = {
                "billing_date": current_time.isoformat(),
                "total_subscriptions_billed": len(billing_results),
                "successful_billings": successful_billings,
                "failed_billings": failed_billings,
                "total_revenue": float(total_revenue),
                "billing_results": billing_results
            }
            
            # Store billing history
            self.billing_history.append(billing_summary)
            
            return billing_summary
            
        except Exception as e:
            logger.error(f"Billing cycle processing failed: {e}")
            raise
    
    async def analyze_subscription_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze subscription metrics and KPIs."""
        try:
            # Calculate key metrics
            metrics = await self._calculate_subscription_metrics(start_date, end_date)
            
            # Analyze churn patterns
            churn_analysis = await self._analyze_churn_patterns(start_date, end_date)
            
            # Calculate lifetime value
            ltv_analysis = await self._calculate_customer_ltv()
            
            # Generate growth insights
            growth_insights = await self._analyze_subscription_growth(start_date, end_date)
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "key_metrics": metrics,
                "churn_analysis": churn_analysis,
                "ltv_analysis": ltv_analysis,
                "growth_insights": growth_insights,
                "recommendations": await self._generate_subscription_recommendations(
                    metrics, churn_analysis, growth_insights
                )
            }
            
        except Exception as e:
            logger.error(f"Subscription metrics analysis failed: {e}")
            raise
    
    def _initialize_default_tiers(self) -> None:
        """Initialize default subscription tiers."""
        # Basic tier
        basic_tier = SubscriptionTier(
            tier_id="basic",
            name="Basic Plan",
            price=Decimal('9.99'),
            billing_cycle=BillingCycle.MONTHLY,
            features=["Basic content access", "Standard support"],
            limits={"content_downloads": 10, "api_calls": 1000},
            trial_days=7
        )
        
        # Professional tier
        pro_tier = SubscriptionTier(
            tier_id="professional",
            name="Professional Plan",
            price=Decimal('29.99'),
            billing_cycle=BillingCycle.MONTHLY,
            features=["Full content access", "Priority support", "Analytics dashboard"],
            limits={"content_downloads": 100, "api_calls": 10000},
            trial_days=14
        )
        
        # Enterprise tier
        enterprise_tier = SubscriptionTier(
            tier_id="enterprise",
            name="Enterprise Plan",
            price=Decimal('99.99'),
            billing_cycle=BillingCycle.MONTHLY,
            features=["Unlimited access", "24/7 support", "Custom integrations", "Advanced analytics"],
            limits={"content_downloads": -1, "api_calls": -1},  # -1 means unlimited
            trial_days=30
        )
        
        self.subscription_tiers = {
            "basic": basic_tier,
            "professional": pro_tier,
            "enterprise": enterprise_tier
        }
    
    async def _apply_promo_code(
        self,
        base_price: Decimal,
        promo_code: Optional[str]
    ) -> Decimal:
        """Apply promotional code discount."""
        if not promo_code:
            return base_price
        
        # Sample promo codes
        promo_discounts = {
            "WELCOME20": 0.20,    # 20% discount
            "SAVE50": 0.50,       # 50% discount
            "NEWUSER": 0.15,      # 15% discount
            "ENTERPRISE25": 0.25  # 25% discount
        }
        
        discount = promo_discounts.get(promo_code.upper(), 0)
        discounted_price = base_price * (Decimal('1') - Decimal(str(discount)))
        
        return discounted_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_period_end(
        self,
        start_date: datetime,
        billing_cycle: BillingCycle
    ) -> datetime:
        """Calculate billing period end date."""
        if billing_cycle == BillingCycle.WEEKLY:
            return start_date + timedelta(weeks=1)
        elif billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.YEARLY:
            return start_date + timedelta(days=365)
        else:
            return start_date + timedelta(days=30)  # Default to monthly
    
    async def _process_payment(
        self,
        subscription: Subscription,
        amount: Decimal
    ) -> Dict[str, Any]:
        """Process subscription payment."""
        # Simulate payment processing
        # In real implementation, this would integrate with payment gateway
        
        payment_result = {
            "success": True,  # Assume successful for demo
            "transaction_id": str(uuid.uuid4()),
            "amount": float(amount),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if payment_result["success"]:
            subscription.total_paid += amount
            
            # Record billing event
            billing_record = {
                "subscription_id": subscription.subscription_id,
                "customer_id": subscription.customer_id,
                "amount": float(amount),
                "status": "paid",
                "billing_date": datetime.utcnow().isoformat(),
                "transaction_id": payment_result["transaction_id"]
            }
            
            self.billing_history.append(billing_record)
        
        return payment_result
    
    async def _upgrade_subscription(
        self,
        subscription: Subscription,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upgrade subscription to higher tier."""
        new_tier_id = parameters.get("new_tier_id")
        new_tier = self.subscription_tiers.get(new_tier_id)
        
        if not new_tier:
            raise ValueError(f"Target tier {new_tier_id} not found")
        
        if new_tier.price <= subscription.tier.price:
            raise ValueError("Cannot upgrade to lower or same price tier")
        
        # Calculate prorated amount
        days_remaining = (subscription.current_period_end - datetime.utcnow()).days
        proration = await self._calculate_proration(subscription, new_tier, days_remaining)
        
        # Process prorated payment
        if proration > 0:
            payment_result = await self._process_payment(subscription, Decimal(str(proration)))
            if not payment_result['success']:
                raise Exception("Upgrade payment failed")
        
        # Update subscription
        old_tier = subscription.tier.name
        subscription.tier = new_tier
        
        return {
            "success": True,
            "old_tier": old_tier,
            "new_tier": new_tier.name,
            "proration_amount": proration,
            "next_billing_amount": float(new_tier.price)
        }
    
    async def _downgrade_subscription(
        self,
        subscription: Subscription,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Downgrade subscription to lower tier."""
        new_tier_id = parameters.get("new_tier_id")
        new_tier = self.subscription_tiers.get(new_tier_id)
        
        if not new_tier:
            raise ValueError(f"Target tier {new_tier_id} not found")
        
        if new_tier.price >= subscription.tier.price:
            raise ValueError("Cannot downgrade to higher or same price tier")
        
        # Schedule downgrade for next billing cycle
        old_tier = subscription.tier.name
        subscription.metadata["scheduled_downgrade"] = {
            "new_tier_id": new_tier_id,
            "effective_date": subscription.next_billing_date.isoformat()
        }
        
        return {
            "success": True,
            "old_tier": old_tier,
            "new_tier": new_tier.name,
            "effective_date": subscription.next_billing_date.isoformat(),
            "message": "Downgrade scheduled for next billing cycle"
        }
    
    async def _pause_subscription(
        self,
        subscription: Subscription,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Pause subscription."""
        if subscription.status == SubscriptionStatus.PAUSED:
            raise ValueError("Subscription is already paused")
        
        pause_duration = parameters.get("pause_duration_days", 30)
        
        subscription.status = SubscriptionStatus.PAUSED
        subscription.metadata["pause_info"] = {
            "paused_at": datetime.utcnow().isoformat(),
            "pause_duration_days": pause_duration,
            "resume_date": (datetime.utcnow() + timedelta(days=pause_duration)).isoformat()
        }
        
        return {
            "success": True,
            "status": "paused",
            "pause_duration_days": pause_duration,
            "resume_date": subscription.metadata["pause_info"]["resume_date"]
        }
    
    async def _resume_subscription(
        self,
        subscription: Subscription,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resume paused subscription."""
        if subscription.status != SubscriptionStatus.PAUSED:
            raise ValueError("Subscription is not paused")
        
        subscription.status = SubscriptionStatus.ACTIVE
        
        # Update billing dates
        current_time = datetime.utcnow()
        subscription.current_period_start = current_time
        subscription.current_period_end = await self._calculate_period_end(
            current_time, subscription.tier.billing_cycle
        )
        subscription.next_billing_date = subscription.current_period_end
        
        # Remove pause info
        if "pause_info" in subscription.metadata:
            del subscription.metadata["pause_info"]
        
        return {
            "success": True,
            "status": "active",
            "next_billing_date": subscription.next_billing_date.isoformat()
        }
    
    async def _cancel_subscription(
        self,
        subscription: Subscription,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cancel subscription."""
        cancellation_type = parameters.get("type", "immediate")  # immediate or end_of_period
        
        if cancellation_type == "immediate":
            subscription.status = SubscriptionStatus.CANCELLED
            cancellation_date = datetime.utcnow()
        else:
            # Cancel at end of current period
            subscription.metadata["scheduled_cancellation"] = subscription.current_period_end.isoformat()
            cancellation_date = subscription.current_period_end
        
        subscription.metadata["cancellation_info"] = {
            "cancelled_at": datetime.utcnow().isoformat(),
            "cancellation_type": cancellation_type,
            "effective_date": cancellation_date.isoformat(),
            "reason": parameters.get("reason", "user_requested")
        }
        
        return {
            "success": True,
            "status": "cancelled" if cancellation_type == "immediate" else "scheduled_for_cancellation",
            "effective_date": cancellation_date.isoformat(),
            "access_until": subscription.current_period_end.isoformat()
        }
    
    async def _process_subscription_billing(
        self,
        subscription: Subscription
    ) -> Dict[str, Any]:
        """Process billing for individual subscription."""
        try:
            # Check for scheduled tier changes
            if "scheduled_downgrade" in subscription.metadata:
                downgrade_info = subscription.metadata["scheduled_downgrade"]
                new_tier = self.subscription_tiers[downgrade_info["new_tier_id"]]
                subscription.tier = new_tier
                del subscription.metadata["scheduled_downgrade"]
            
            # Check for scheduled cancellation
            if "scheduled_cancellation" in subscription.metadata:
                subscription.status = SubscriptionStatus.CANCELLED
                return {
                    "subscription_id": subscription.subscription_id,
                    "success": True,
                    "amount": 0,
                    "status": "cancelled",
                    "message": "Subscription cancelled as scheduled"
                }
            
            # Process payment
            payment_result = await self._process_payment(subscription, subscription.tier.price)
            
            if payment_result["success"]:
                # Update billing dates
                subscription.current_period_start = subscription.current_period_end
                subscription.current_period_end = await self._calculate_period_end(
                    subscription.current_period_end, subscription.tier.billing_cycle
                )
                subscription.next_billing_date = subscription.current_period_end
                
                return {
                    "subscription_id": subscription.subscription_id,
                    "success": True,
                    "amount": float(subscription.tier.price),
                    "transaction_id": payment_result["transaction_id"],
                    "next_billing_date": subscription.next_billing_date.isoformat()
                }
            else:
                # Payment failed - mark as past due
                subscription.status = SubscriptionStatus.PAST_DUE
                
                return {
                    "subscription_id": subscription.subscription_id,
                    "success": False,
                    "amount": float(subscription.tier.price),
                    "error": "Payment failed",
                    "status": "past_due"
                }
                
        except Exception as e:
            logger.error(f"Billing processing failed for subscription {subscription.subscription_id}: {e}")
            return {
                "subscription_id": subscription.subscription_id,
                "success": False,
                "error": str(e)
            }
    
    async def _calculate_proration(
        self,
        subscription: Subscription,
        new_tier: SubscriptionTier,
        days_remaining: int
    ) -> float:
        """Calculate prorated amount for tier upgrade."""
        current_daily_rate = float(subscription.tier.price) / 30  # Assuming monthly billing
        new_daily_rate = float(new_tier.price) / 30
        
        proration = (new_daily_rate - current_daily_rate) * days_remaining
        return max(0, proration)
    
    async def _calculate_subscription_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate key subscription metrics."""
        active_subs = len([s for s in self.active_subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
        trial_subs = len([s for s in self.active_subscriptions.values() if s.status == SubscriptionStatus.TRIAL])
        cancelled_subs = len([s for s in self.active_subscriptions.values() if s.status == SubscriptionStatus.CANCELLED])
        
        # Calculate MRR (Monthly Recurring Revenue)
        mrr = sum(
            float(s.tier.price) for s in self.active_subscriptions.values()
            if s.status == SubscriptionStatus.ACTIVE and s.tier.billing_cycle == BillingCycle.MONTHLY
        )
        
        # Calculate ARPU (Average Revenue Per User)
        total_users = len(self.active_subscriptions)
        arpu = mrr / total_users if total_users > 0 else 0
        
        # Calculate churn rate (simplified)
        total_at_start = active_subs + cancelled_subs
        churn_rate = cancelled_subs / total_at_start if total_at_start > 0 else 0
        
        return {
            "active_subscriptions": active_subs,
            "trial_subscriptions": trial_subs,
            "cancelled_subscriptions": cancelled_subs,
            "monthly_recurring_revenue": mrr,
            "average_revenue_per_user": arpu,
            "churn_rate": churn_rate,
            "total_subscriptions": total_users
        }
    
    async def _analyze_churn_patterns(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze subscription churn patterns."""
        churn_reasons = {}
        tier_churn_rates = {}
        
        for subscription in self.active_subscriptions.values():
            if subscription.status == SubscriptionStatus.CANCELLED:
                cancellation_info = subscription.metadata.get("cancellation_info", {})
                reason = cancellation_info.get("reason", "unknown")
                
                churn_reasons[reason] = churn_reasons.get(reason, 0) + 1
                
                tier_name = subscription.tier.name
                if tier_name not in tier_churn_rates:
                    tier_churn_rates[tier_name] = {"churned": 0, "total": 0}
                tier_churn_rates[tier_name]["churned"] += 1
        
        # Calculate total by tier
        for subscription in self.active_subscriptions.values():
            tier_name = subscription.tier.name
            if tier_name not in tier_churn_rates:
                tier_churn_rates[tier_name] = {"churned": 0, "total": 0}
            tier_churn_rates[tier_name]["total"] += 1
        
        # Calculate churn rates by tier
        for tier_name in tier_churn_rates:
            data = tier_churn_rates[tier_name]
            data["churn_rate"] = data["churned"] / data["total"] if data["total"] > 0 else 0
        
        return {
            "churn_reasons": churn_reasons,
            "tier_churn_rates": tier_churn_rates,
            "overall_patterns": await self._identify_churn_patterns()
        }
    
    async def _identify_churn_patterns(self) -> List[str]:
        """Identify common churn patterns."""
        patterns = []
        
        # Analyze trial conversion
        trials = [s for s in self.active_subscriptions.values() if s.status == SubscriptionStatus.TRIAL]
        if len(trials) > 5:  # If we have enough trial data
            patterns.append("High trial volume - focus on trial-to-paid conversion")
        
        # Analyze early churn
        early_churns = [
            s for s in self.active_subscriptions.values()
            if s.status == SubscriptionStatus.CANCELLED and
            (datetime.utcnow() - s.start_date).days < 30
        ]
        
        if len(early_churns) > 3:
            patterns.append("Early churn detected - review onboarding experience")
        
        return patterns
    
    async def _calculate_customer_ltv(self) -> Dict[str, Any]:
        """Calculate customer lifetime value."""
        # Simplified LTV calculation
        total_revenue = sum(float(s.total_paid) for s in self.active_subscriptions.values())
        total_customers = len(self.active_subscriptions)
        
        avg_revenue_per_customer = total_revenue / total_customers if total_customers > 0 else 0
        
        # Estimate average customer lifespan (simplified)
        avg_lifespan_months = 12  # Assume 12 months average
        
        ltv = avg_revenue_per_customer * avg_lifespan_months
        
        return {
            "average_ltv": ltv,
            "average_revenue_per_customer": avg_revenue_per_customer,
            "estimated_lifespan_months": avg_lifespan_months,
            "total_customers_analyzed": total_customers
        }
    
    async def _analyze_subscription_growth(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze subscription growth trends."""
        # Calculate growth metrics
        period_days = (end_date - start_date).days
        
        # Growth rate calculation (simplified)
        current_subs = len([s for s in self.active_subscriptions.values() if s.status == SubscriptionStatus.ACTIVE])
        
        # Simulate historical data for growth calculation
        historical_subs = max(1, current_subs - (period_days // 7))  # Assume some growth
        growth_rate = (current_subs - historical_subs) / historical_subs if historical_subs > 0 else 0
        
        return {
            "current_active_subscriptions": current_subs,
            "growth_rate": growth_rate,
            "projected_monthly_growth": growth_rate * 4,  # Weekly to monthly
            "growth_trend": "positive" if growth_rate > 0 else "negative" if growth_rate < 0 else "stable"
        }
    
    async def _generate_subscription_recommendations(
        self,
        metrics: Dict[str, Any],
        churn_analysis: Dict[str, Any],
        growth_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate subscription optimization recommendations."""
        recommendations = []
        
        # Churn recommendations
        churn_rate = metrics.get("churn_rate", 0)
        if churn_rate > 0.1:  # >10% churn rate
            recommendations.append("High churn rate detected - implement retention campaigns")
        
        # Growth recommendations
        growth_rate = growth_insights.get("growth_rate", 0)
        if growth_rate < 0.05:  # <5% growth
            recommendations.append("Low growth rate - consider promotional campaigns or new features")
        
        # ARPU recommendations
        arpu = metrics.get("average_revenue_per_user", 0)
        if arpu < 20:  # Low ARPU
            recommendations.append("Consider tier optimization or upselling strategies")
        
        # Trial conversion recommendations
        trial_subs = metrics.get("trial_subscriptions", 0)
        active_subs = metrics.get("active_subscriptions", 0)
        if trial_subs > active_subs * 0.5:  # High trial to active ratio
            recommendations.append("High trial volume - optimize trial-to-paid conversion flow")
        
        # General recommendations
        recommendations.extend([
            "Implement usage-based billing for enterprise customers",
            "Consider annual billing discounts to improve cash flow",
            "Set up win-back campaigns for cancelled subscribers"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations