"""Monetization Manager - Central orchestration for all monetization systems.
Coordinates revenue engine, payments, subscriptions, commissions, analytics, and pricing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
from .revenue_engine import RevenueEngine, RevenueTransaction, RevenueStreamType
from .payment_gateway import PaymentGatewayManager, PaymentRequest, PaymentMethod, GatewayType
from .subscription_manager import SubscriptionManager, SubscriptionTier, BillingCycle
from .commission_manager import CommissionManager, CommissionType
from .analytics_engine import AnalyticsEngine, MetricType, ReportType
from .pricing_engine import PricingEngine, ContentType, PricingStrategy

logger = logging.getLogger(__name__)


class MonetizationEvent(Enum):
    """
Monetization system events."""

    REVENUE_GENERATED = "revenue_generated"
    PAYMENT_PROCESSED = "payment_processed"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    COMMISSION_EARNED = "commission_earned"
    PRICE_OPTIMIZED = "price_optimized"
    FRAUD_DETECTED = "fraud_detected"


@dataclass
class MonetizationConfig:
    """Central monetization configuration."""
    revenue_share_rate: Decimal = Decimal("0.15")  # 15% platform fee
    min_payout_threshold: Decimal = Decimal("50.00")
    default_currency: str = "EUR"
    payment_gateways: List[GatewayType] = field(default_factory=lambda: [GatewayType.STRIPE, GatewayType.PAYPAL])
    subscription_trial_days: int = 14
    commission_rate: Decimal = Decimal("10.0")  # 10% default commission
    auto_pricing_enabled: bool = True
    fraud_detection_enabled: bool = True
    analytics_retention_days: int = 365
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "revenue_share_rate": float(self.revenue_share_rate),
            "min_payout_threshold": float(self.min_payout_threshold),
            "default_currency": self.default_currency,
            "payment_gateways": [gw.value for gw in self.payment_gateways],
            "subscription_trial_days": self.subscription_trial_days,
            "commission_rate": float(self.commission_rate),
            "auto_pricing_enabled": self.auto_pricing_enabled,
            "fraud_detection_enabled": self.fraud_detection_enabled,
            "analytics_retention_days": self.analytics_retention_days
        }


@dataclass
class MonetizationStats:
    """Aggregated monetization statistics."""
    total_revenue: Decimal
    active_subscriptions: int
    pending_commissions: Decimal
    conversion_rate: float
    avg_revenue_per_user: Decimal
    growth_rate: float
    top_revenue_stream: str
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert stats to dictionary."""
        return {
            "total_revenue": float(self.total_revenue),
            "active_subscriptions": self.active_subscriptions,
            "pending_commissions": float(self.pending_commissions),
            "conversion_rate": self.conversion_rate,
            "avg_revenue_per_user": float(self.avg_revenue_per_user),
            "growth_rate": self.growth_rate,
            "top_revenue_stream": self.top_revenue_stream,
            "last_updated": self.last_updated.isoformat()
        }


class MonetizationManager:
    """
    Central monetization management system.
    Orchestrates all monetization components and provides unified interface.
    """
    
    def __init__(self, config -> None: Optional[MonetizationConfig] = None) -> None:
        self.config = config or MonetizationConfig()
        
        # Initialize core components
        self.revenue_engine = RevenueEngine()
        self.payment_gateway = PaymentGatewayManager()
        self.subscription_manager = SubscriptionManager()
        self.commission_manager = CommissionManager()
        self.analytics_engine = AnalyticsEngine()
        self.pricing_engine = PricingEngine()
        
        # Event handlers
        self.event_handlers: Dict[MonetizationEvent, List[callable]] = {}
        
        # Cache and state
        self.cached_stats: Optional[MonetizationStats] = None
        self.stats_cache_expiry: Optional[datetime] = None
        self.is_initialized = False
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
    
    async def initialize(self, gateway_configs: Dict[GatewayType, Dict[str, str]] = None) -> bool:
        """
Initialize all monetization components."""
        try:
            logger.info("Initializing monetization manager...")
            
            # Initialize components in order
            components_initialized = []
            
            # Revenue Engine
            if await self.revenue_engine.initialize():
                components_initialized.append("Revenue Engine")
            else:
                logger.error("Revenue engine initialization failed")
                return False
            
            # Payment Gateway
            if gateway_configs:
                if await self.payment_gateway.initialize(gateway_configs):
                    components_initialized.append("Payment Gateway")
                else:
                    logger.warning("Payment gateway initialization failed")
            
            # Subscription Manager
            if await self.subscription_manager.initialize():
                components_initialized.append("Subscription Manager")
            else:
                logger.error("Subscription manager initialization failed")
                return False
            
            # Commission Manager
            if await self.commission_manager.initialize():
                components_initialized.append("Commission Manager")
            else:
                logger.error("Commission manager initialization failed")
                return False
            
            # Analytics Engine
            if await self.analytics_engine.initialize(
                self.revenue_engine, 
                self.subscription_manager, 
                self.commission_manager
            ):
                components_initialized.append("Analytics Engine")
            else:
                logger.warning("Analytics engine initialization failed")
            
            # Pricing Engine
            if await self.pricing_engine.initialize():
                components_initialized.append("Pricing Engine")
            else:
                logger.warning("Pricing engine initialization failed")
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            logger.info(f"Monetization manager initialized successfully. Components: {', '.join(components_initialized)}")
            return True
            
        except Exception as e:
            logger.error(f"Monetization manager initialization failed: {e}")
            return False
    
    async def process_content_monetization(
        self,
        user_id: str,
        content_id: str,
        content_type: ContentType,
        viewer_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process complete content monetization flow."""
        if not self.is_initialized:
            await self.initialize()
        
        context = context or {}
        
        try:
            result = {
                "success": False,
                "transaction_id": None,
                "amount": 0,
                "payment_url": None,
                "error": None
            }
            
            # Get optimized price
            price = await self.pricing_engine.get_price(content_type, viewer_id, context)
            
            # Create payment request
            payment_request = PaymentRequest(
                request_id=str(uuid.uuid4()),
                user_id=viewer_id,
                amount=price,
                currency=self.config.default_currency,
                description=f"Content access: {content_id}",
                metadata={
                    "content_id": content_id,
                    "content_type": content_type.value,
                    "creator_id": user_id
                }
            )
            
            # Process payment
            payment_response = await self.payment_gateway.process_payment(payment_request)
            
            if payment_response.status.value in ["completed", "authorized"]:
                # Create revenue transaction
                revenue_transaction = RevenueTransaction(
                    transaction_id=payment_response.response_id,
                    user_id=user_id,
                    content_id=content_id,
                    stream_type=RevenueStreamType.PAY_PER_VIEW,
                    amount=price,
                    currency=self.config.default_currency,
                    platform="direct",
                    metadata={
                        "content_type": content_type.value,
                        "viewer_id": viewer_id,
                        "payment_gateway": payment_response.gateway_response.get("gateway", "unknown")
                    }
                )
                
                # Process revenue
                revenue_success = await self.revenue_engine.process_revenue(revenue_transaction)
                
                if revenue_success:
                    # Handle commissions if applicable
                    await self._process_referral_commission(viewer_id, price, content_id)
                    
                    # Record purchase for pricing optimization
                    await self.pricing_engine.record_purchase(viewer_id, content_type, price, price)
                    
                    # Emit event
                    await self._emit_event(MonetizationEvent.REVENUE_GENERATED, {
                        "user_id": user_id,
                        "content_id": content_id,
                        "amount": float(price),
                        "viewer_id": viewer_id
                    })
                    
                    result.update({
                        "success": True,
                        "transaction_id": revenue_transaction.transaction_id,
                        "amount": float(price),
                        "content_access_granted": True
                    })
                    
                    logger.info(f"Content monetization successful: {content_id}, amount: {price}")
                else:
                    result["error"] = "Revenue processing failed"
            else:
                result["error"] = f"Payment failed: {payment_response.error_message}"
                result["payment_url"] = payment_response.redirect_url
            
            return result
            
        except Exception as e:
            logger.error(f"Content monetization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method: PaymentMethod = PaymentMethod.CREDIT_CARD
    ) -> Dict[str, Any]:
        """Create a new subscription with payment processing."""
        try:
            result = {
                "success": False,
                "subscription_id": None,
                "trial_end": None,
                "next_billing": None,
                "error": None
            }
            
            # Get subscription plan
            plan = self.subscription_manager.get_plan(plan_id)
            if not plan:
                result["error"] = "Invalid subscription plan"
                return result
            
            # Create subscription
            subscription = await self.subscription_manager.create_subscription(
                user_id=user_id,
                plan_id=plan_id,
                start_trial=plan.trial_days > 0
            )
            
            if not subscription:
                result["error"] = "Subscription creation failed"
                return result
            
            # Process initial payment if not in trial
            if not subscription.is_trial() and plan.price > 0:
                payment_request = PaymentRequest(
                    request_id=str(uuid.uuid4()),
                    user_id=user_id,
                    amount=plan.price,
                    currency=self.config.default_currency,
                    payment_method=payment_method,
                    description=f"Subscription: {plan.name}",
                    metadata={
                        "subscription_id": subscription.subscription_id,
                        "plan_id": plan_id
                    }
                )
                
                payment_response = await self.payment_gateway.process_payment(payment_request)
                
                if payment_response.status.value not in ["completed", "authorized"]:
                    # Cancel subscription if payment failed
                    await self.subscription_manager.cancel_subscription(subscription.subscription_id, immediate=True)
                    result["error"] = f"Payment failed: {payment_response.error_message}"
                    return result
            
            # Create revenue transaction
            if plan.price > 0:
                revenue_transaction = RevenueTransaction(
                    transaction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    content_id=f"subscription_{plan_id}",
                    stream_type=RevenueStreamType.SUBSCRIPTION,
                    amount=plan.price,
                    currency=self.config.default_currency,
                    metadata={
                        "subscription_id": subscription.subscription_id,
                        "plan_name": plan.name
                    }
                )
                
                await self.revenue_engine.process_revenue(revenue_transaction)
            
            # Emit event
            await self._emit_event(MonetizationEvent.SUBSCRIPTION_CREATED, {
                "user_id": user_id,
                "subscription_id": subscription.subscription_id,
                "plan_id": plan_id,
                "amount": float(plan.price)
            })
            
            result.update({
                "success": True,
                "subscription_id": subscription.subscription_id,
                "trial_end": subscription.trial_end.isoformat() if subscription.trial_end else None,
                "next_billing": subscription.current_period_end.isoformat(),
                "plan_name": plan.name,
                "amount": float(plan.price)
            })
            
            logger.info(f"Subscription created: {subscription.subscription_id} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_monetization_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive monetization summary for a user."""
        try:
            summary = {
                "user_id": user_id,
                "revenue": {},
                "subscriptions": {},
                "commissions": {},
                "analytics": {},
                "recommendations": []
            }
            
            # Revenue summary
            revenue_summary = self.revenue_engine.get_revenue_summary(user_id)
            summary["revenue"] = revenue_summary
            
            # Subscription summary
            user_subscriptions = await self.subscription_manager.get_user_subscriptions(user_id)
            summary["subscriptions"] = {
                "active_count": len([s for s in user_subscriptions if s.is_active()]),
                "total_count": len(user_subscriptions),
                "current_plans": [s.plan_id for s in user_subscriptions if s.is_active()]
            }
            
            # Commission summary (if user is an affiliate)
            affiliate = self.commission_manager.get_affiliate_by_code(user_id)
            if affiliate:
                commission_performance = await self.commission_manager.get_affiliate_performance(affiliate.affiliate_id)
                summary["commissions"] = commission_performance
            
            # Analytics summary
            analytics_summary = await self.analytics_engine.get_real_time_metrics(user_id)
            summary["analytics"] = analytics_summary
            
            # Performance insights
            insights = await self.analytics_engine.get_performance_insights(user_id)
            summary["recommendations"] = insights
            
            return summary
            
        except Exception as e:
            logger.error(f"User monetization summary failed: {e}")
            return {
                "user_id": user_id,
                "error": str(e)
            }
    
    async def generate_monetization_report(
        self,
        report_type: ReportType = ReportType.MONTHLY,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive monetization report."""
        try:
            # Calculate report period
            now = datetime.utcnow()
            if report_type == ReportType.DAILY:
                start_date = now - timedelta(days=1)
            elif report_type == ReportType.WEEKLY:
                start_date = now - timedelta(days=7)
            elif report_type == ReportType.MONTHLY:
                start_date = now - timedelta(days=30)
            elif report_type == ReportType.QUARTERLY:
                start_date = now - timedelta(days=90)
            else:
                start_date = now - timedelta(days=30)
            
            # Generate analytics report
            analytics_report = await self.analytics_engine.generate_report(
                report_type, start_date, now, user_id
            )
            
            # Add monetization-specific insights
            monetization_insights = {
                "revenue_optimization": await self._get_revenue_optimization_insights(user_id),
                "pricing_recommendations": await self._get_pricing_recommendations(user_id),
                "subscription_insights": await self._get_subscription_insights(user_id),
                "commission_opportunities": await self._get_commission_opportunities(user_id)
            }
            
            report_dict = analytics_report.to_dict()
            report_dict["monetization_insights"] = monetization_insights
            
            return report_dict
            
        except Exception as e:
            logger.error(f"Monetization report generation failed: {e}")
            return {
                "error": str(e),
                "report_type": report_type.value
            }
    
    async def optimize_monetization(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Run automated monetization optimization."""
        try:
            optimization_results = {
                "pricing_optimization": {},
                "subscription_optimization": {},
                "commission_optimization": {},
                "overall_score": 0.0,
                "recommendations": []
            }
            
            # Price optimization
            if self.config.auto_pricing_enabled:
                pricing_results = await self.pricing_engine.optimize_prices()
                optimization_results["pricing_optimization"] = pricing_results
            
            # Subscription optimization
            subscription_analytics = await self.subscription_manager.get_subscription_analytics()
            if subscription_analytics.get("churn_rate", 0) > 0.1:  # 10% churn threshold
                optimization_results["recommendations"].append("High subscription churn detected - review pricing and value proposition")
            
            # Commission optimization
            commission_analytics = await self.commission_manager.get_commission_analytics()
            if commission_analytics.get("active_affiliates", 0) < 10:
                optimization_results["recommendations"].append("Low affiliate engagement - consider expanding affiliate program")
            
            # Calculate overall optimization score
            score_components = []
            
            if optimization_results["pricing_optimization"].get("optimized_count", 0) > 0:
                score_components.append(25)  # Pricing optimization points
            
            if subscription_analytics.get("churn_rate", 0) < 0.05:
                score_components.append(25)  # Low churn points
            
            if commission_analytics.get("commission_rate", 0) > 5:
                score_components.append(25)  # Good commission performance
            
            revenue_summary = self.revenue_engine.get_revenue_summary(user_id or "global")
            if revenue_summary.get("total_revenue", 0) > 1000:
                score_components.append(25)  # Revenue performance points
            
            optimization_results["overall_score"] = sum(score_components)
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Monetization optimization failed: {e}")
            return {
                "error": str(e)
            }
    
    async def get_monetization_stats(self, force_refresh: bool = False) -> MonetizationStats:
        """Get aggregated monetization statistics."""
        # Check cache
        if (not force_refresh and 
            self.cached_stats and 
            self.stats_cache_expiry and 
            datetime.utcnow() < self.stats_cache_expiry):
            return self.cached_stats
        
        try:
            # Calculate stats
            total_revenue = Decimal("0")
            for transaction in self.revenue_engine.transactions:
                total_revenue += transaction.amount
            
            active_subs = len([
                s for s in self.subscription_manager.subscriptions.values()
                if s.is_active()
            ])
            
            pending_commissions = sum(
                c.commission_amount for c in self.commission_manager.commissions.values()
                if c.status.value == "pending"
            )
            
            # Calculate conversion rate (simplified)
            total_views = len(self.revenue_engine.transactions) * 10  # Estimate
            total_conversions = len(self.revenue_engine.transactions)
            conversion_rate = total_conversions / total_views if total_views > 0 else 0
            
            # Calculate ARPU
            unique_users = len(set(t.user_id for t in self.revenue_engine.transactions))
            avg_revenue_per_user = total_revenue / unique_users if unique_users > 0 else Decimal("0")
            
            # Find top revenue stream
            stream_revenues = {}
            for transaction in self.revenue_engine.transactions:
                stream = transaction.stream_type.value
                stream_revenues[stream] = stream_revenues.get(stream, Decimal("0")) + transaction.amount
            
            top_stream = max(stream_revenues.items(), key=lambda x: x[1])[0] if stream_revenues else "none"
            
            stats = MonetizationStats(
                total_revenue=total_revenue,
                active_subscriptions=active_subs,
                pending_commissions=pending_commissions,
                conversion_rate=conversion_rate,
                avg_revenue_per_user=avg_revenue_per_user,
                growth_rate=0.15,  # Placeholder
                top_revenue_stream=top_stream
            )
            
            # Cache for 5 minutes
            self.cached_stats = stats
            self.stats_cache_expiry = datetime.utcnow() + timedelta(minutes=5)
            
            return stats
            
        except Exception as e:
            logger.error(f"Monetization stats calculation failed: {e}")
            return MonetizationStats(
                total_revenue=Decimal("0"),
                active_subscriptions=0,
                pending_commissions=Decimal("0"),
                conversion_rate=0.0,
                avg_revenue_per_user=Decimal("0"),
                growth_rate=0.0,
                top_revenue_stream="none"
            )
    
    def register_event_handler(self, event: MonetizationEvent, handler: callable) -> None:
        """Register event handler for monetization events."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def shutdown(self) -> None:
        """
Shutdown monetization manager and cleanup resources."""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.background_tasks.clear()
            self.is_initialized = False
            
            logger.info("Monetization manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Monetization manager shutdown failed: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        try:
            # Subscription renewal task
            renewal_task = asyncio.create_task(self._subscription_renewal_task())
            self.background_tasks.append(renewal_task)
            
            # Commission payout task
            payout_task = asyncio.create_task(self._commission_payout_task())
            self.background_tasks.append(payout_task)
            
            # Price optimization task
            if self.config.auto_pricing_enabled:
                pricing_task = asyncio.create_task(self._pricing_optimization_task())
                self.background_tasks.append(pricing_task)
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Background task startup failed: {e}")
    
    async def _subscription_renewal_task(self) -> None:
        """Background task for subscription renewals."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.subscription_manager.process_renewals()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Subscription renewal task failed: {e}")
    
    async def _commission_payout_task(self) -> None:
        """Background task for commission payouts."""
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily
                await self.commission_manager.process_payouts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Commission payout task failed: {e}")
    
    async def _pricing_optimization_task(self) -> None:
        """Background task for price optimization."""
        while True:
            try:
                await asyncio.sleep(3600 * 6)  # Run every 6 hours
                await self.pricing_engine.optimize_prices()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pricing optimization task failed: {e}")
    
    async def _emit_event(self, event: MonetizationEvent, data: Dict[str, Any]) -> None:
        """Emit monetization event to registered handlers."""
        try:
            handlers = self.event_handlers.get(event, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event, data)
                    else:
                        handler(event, data)
                except Exception as e:
                    logger.error(f"Event handler failed for {event}: {e}")
        except Exception as e:
            logger.error(f"Event emission failed: {e}")
    
    async def _process_referral_commission(
        self, 
        user_id: str, 
        amount: Decimal, 
        reference_id: str
    ) -> None:
        """Process referral commission if applicable."""
        try:
            # Check if user was referred by an affiliate
            # This would typically check a referral tracking system
            # For now, we'll simulate a 10% chance of referral
            import random
            if random.random() < 0.1:  # 10% chance of referral
                # Find a random affiliate for simulation
                affiliates = list(self.commission_manager.affiliates.values())
                if affiliates:
                    affiliate = random.choice(affiliates)
                    await self.commission_manager.create_commission(
                        affiliate_id=affiliate.affiliate_id,
                        transaction_id=str(uuid.uuid4()),
                        amount=amount,
                        reference_type="referral",
                        reference_id=reference_id
                    )
        except Exception as e:
            logger.error(f"Referral commission processing failed: {e}")
    
    async def _get_revenue_optimization_insights(self, user_id: Optional[str]) -> List[str]:
        """Get revenue optimization insights."""
        insights = []
        
        try:
            stats = await self.get_monetization_stats()
            
            if stats.conversion_rate < 0.05:
                insights.append("Low conversion rate - consider improving pricing strategy")
            
            if stats.avg_revenue_per_user < Decimal("50"):
                insights.append("Low ARPU - explore upselling and cross-selling opportunities")
            
            if stats.active_subscriptions < 100:
                insights.append("Limited subscription base - focus on recurring revenue growth")
            
        except Exception as e:
            logger.error(f"Revenue optimization insights failed: {e}")
        
        return insights
    
    async def _get_pricing_recommendations(self, user_id: Optional[str]) -> List[str]:
        """Get pricing optimization recommendations."""
        recommendations = []
        
        try:
            pricing_analytics = await self.pricing_engine.get_pricing_analytics()
            
            opportunities = pricing_analytics.get("optimization_opportunities", [])
            for opportunity in opportunities:
                if opportunity["opportunity"] == "price_increase":
                    recommendations.append(f"Consider increasing price for {opportunity['content_type']}")
                elif opportunity["opportunity"] == "price_decrease":
                    recommendations.append(f"Consider decreasing price for {opportunity['content_type']}")
            
        except Exception as e:
            logger.error(f"Pricing recommendations failed: {e}")
        
        return recommendations
    
    async def _get_subscription_insights(self, user_id: Optional[str]) -> List[str]:
        """Get subscription optimization insights."""
        insights = []
        
        try:
            sub_analytics = await self.subscription_manager.get_subscription_analytics()
            
            churn_rate = sub_analytics.get("churn_rate", 0)
            if churn_rate > 0.1:
                insights.append(f"High churn rate ({churn_rate:.1%}) - review retention strategies")
            
            trial_conversion = sub_analytics.get("trial_conversion_rate", 0)
            if trial_conversion < 0.3:
                insights.append("Low trial conversion - optimize onboarding experience")
            
        except Exception as e:
            logger.error(f"Subscription insights failed: {e}")
        
        return insights
    
    async def _get_commission_opportunities(self, user_id: Optional[str]) -> List[str]:
        """Get commission program opportunities."""
        opportunities = []
        
        try:
            commission_analytics = await self.commission_manager.get_commission_analytics()
            
            active_affiliates = commission_analytics.get("active_affiliates", 0)
            if active_affiliates < 10:
                opportunities.append("Low affiliate participation - expand affiliate recruitment")
            
            avg_commission = commission_analytics.get("average_commission", 0)
            if avg_commission < 10:
                opportunities.append("Low commission amounts - review commission rates")
            
        except Exception as e:
            logger.error(f"Commission opportunities failed: {e}")
        
        return opportunities
