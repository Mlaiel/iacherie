"""
Subscription Manager

High-level subscription management orchestrator providing unified interface
for subscription operations, feature access control, and business logic coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple
import asyncio
import logging
from sqlalchemy.orm import Session

from .models import (
    UserSubscription, SubscriptionPlan, SubscriptionStatus,
    BillingCycleType, UsageQuota, BillingSummary
)
from .subscription_service import SubscriptionService
from .billing_engine import BillingEngine
from .payment_processor import PaymentProcessor
from .tier_controller import TierController
from .usage_tracker import UsageTracker
from .lifecycle_manager import LifecycleManager
from ..core.database import get_db_session
from ..core.exceptions import (
    SubscriptionError, ValidationError, 
    SubscriptionNotFoundError, InsufficientPermissionError
)
from ..core.cache import CacheManager
from ..core.events import EventPublisher
from ..core.logging import get_logger

logger = get_logger(__name__)


class SubscriptionManager:
    """
    Comprehensive subscription management orchestrator.
    
    Coordinates all subscription-related operations including:
    - Subscription lifecycle management
    - Feature access control and validation
    - Usage tracking and limit enforcement
    - Billing and payment coordination
    - Analytics and reporting
    - Event publishing for integrations
    """
    
    def __init__(self):
        """Initialize subscription manager with required services."""
        self.service = SubscriptionService()
        self.billing = BillingEngine()
        self.payment = PaymentProcessor()
        self.tier_controller = TierController()
        self.usage_tracker = UsageTracker()
        self.lifecycle = LifecycleManager()
        self.cache = CacheManager()
        self.events = EventPublisher()
        self.logger = get_logger(__name__)
    
    async def get_subscription_overview(
        self, 
        user_id: int,
        include_usage: bool = True,
        include_billing: bool = True,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive subscription overview for user.
        
        Args:
            user_id: User ID
            include_usage: Include usage metrics
            include_billing: Include billing information
            db: Database session
            
        Returns:
            Complete subscription overview
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get active subscription
            subscription = await self.service.get_active_subscription(user_id, db)
            if not subscription:
                return await self._get_non_subscriber_overview(user_id)
            
            # Build overview data
            overview = {
                "subscription": {
                    "id": subscription.id,
                    "plan": {
                        "name": subscription.plan.name,
                        "display_name": subscription.plan.display_name,
                        "tier_level": subscription.plan.tier_level,
                        "features": subscription.plan.features,
                        "limits": subscription.plan.limits
                    },
                    "status": subscription.status,
                    "billing_cycle": subscription.billing_cycle,
                    "start_date": subscription.start_date.isoformat(),
                    "end_date": subscription.end_date.isoformat(),
                    "trial_end_date": subscription.trial_end_date.isoformat() if subscription.trial_end_date else None,
                    "is_trial": subscription.status == SubscriptionStatus.TRIAL.value,
                    "days_remaining": (subscription.end_date - datetime.utcnow()).days
                }
            }
            
            # Include usage metrics if requested
            if include_usage:
                usage_data = await self.usage_tracker.get_comprehensive_usage(user_id, db)
                overview["usage"] = usage_data
                
                # Add usage warnings
                overview["usage_warnings"] = await self._get_usage_warnings(usage_data)
            
            # Include billing information if requested
            if include_billing:
                billing_data = await self.billing.get_billing_summary(subscription.id, db)
                overview["billing"] = billing_data
                
                # Add payment method info
                if subscription.payment_method_id:
                    payment_method = await self.payment.get_payment_method_info(
                        subscription.payment_method_id
                    )
                    overview["payment_method"] = payment_method
            
            # Add available actions
            overview["available_actions"] = await self._get_available_actions(subscription)
            
            # Cache overview for performance
            cache_key = f"subscription_overview:{user_id}"
            await self.cache.set(cache_key, overview, ttl=300)  # 5 minutes
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Failed to get subscription overview for user {user_id}: {str(e)}")
            raise SubscriptionError(f"Failed to get subscription overview: {str(e)}")
    
    async def check_and_enforce_limits(
        self, 
        user_id: int, 
        feature_name: str,
        requested_usage: int = 1,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Check feature limits and enforce usage quotas.
        
        Args:
            user_id: User ID
            feature_name: Feature name to check
            requested_usage: Amount of usage requested
            db: Database session
            
        Returns:
            Usage check result with enforcement actions
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get subscription and feature access
            subscription = await self.service.get_active_subscription(user_id, db)
            if not subscription:
                # Free tier limitations
                has_access = await self.tier_controller.check_free_tier_access(feature_name)
                if not has_access:
                    return {
                        "allowed": False,
                        "reason": "feature_not_available_free_tier",
                        "action_required": "subscription_upgrade",
                        "suggested_plans": await self._get_plans_with_feature(feature_name, db)
                    }
            
            # Check feature access for current plan
            has_feature_access = await self.tier_controller.check_feature_access(
                user_id, feature_name, db
            )
            
            if not has_feature_access:
                return {
                    "allowed": False,
                    "reason": "feature_not_in_plan",
                    "action_required": "plan_upgrade",
                    "suggested_plans": await self._get_plans_with_feature(feature_name, db)
                }
            
            # Check usage quotas
            usage_check = await self.usage_tracker.check_usage_limit(
                user_id, feature_name, requested_usage, db
            )
            
            if not usage_check["within_limit"]:
                # Determine enforcement action
                if usage_check["quota_exceeded"]:
                    # Hard limit reached
                    return {
                        "allowed": False,
                        "reason": "quota_exceeded",
                        "current_usage": usage_check["current_usage"],
                        "quota_limit": usage_check["quota_limit"],
                        "reset_date": usage_check["reset_date"],
                        "action_required": "wait_or_upgrade",
                        "suggested_plans": await self._get_higher_tier_plans(user_id, db)
                    }
                else:
                    # Soft limit warning
                    return {
                        "allowed": True,
                        "warning": "approaching_limit",
                        "current_usage": usage_check["current_usage"],
                        "quota_limit": usage_check["quota_limit"],
                        "usage_percentage": usage_check["usage_percentage"],
                        "suggested_action": "consider_upgrade"
                    }
            
            # Usage allowed - track it
            await self.usage_tracker.track_usage(user_id, feature_name, requested_usage, db)
            
            return {
                "allowed": True,
                "current_usage": usage_check["current_usage"] + requested_usage,
                "quota_limit": usage_check["quota_limit"],
                "usage_percentage": usage_check["usage_percentage"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check limits for user {user_id}, feature {feature_name}: {str(e)}")
            raise SubscriptionError(f"Failed to check feature limits: {str(e)}")
    
    async def handle_subscription_change(
        self,
        user_id: int,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Handle subscription changes with comprehensive validation and processing.
        
        Args:
            user_id: User ID
            action: Change action (subscribe, upgrade, downgrade, cancel, reactivate)
            **kwargs: Action-specific parameters
            
        Returns:
            Change result with updated subscription info
        """
        try:
            # Validate action parameters
            await self._validate_change_parameters(user_id, action, kwargs)
            
            # Execute change through lifecycle manager
            result = await self.lifecycle.handle_subscription_change(
                user_id, action, **kwargs
            )
            
            # Clear relevant caches
            await self._clear_subscription_caches(user_id)
            
            # Publish subscription change event
            await self.events.publish("subscription.changed", {
                "user_id": user_id,
                "action": action,
                "subscription_id": result.get("subscription_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "details": kwargs
            })
            
            # Send notifications
            await self._send_subscription_notifications(user_id, action, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to handle subscription change for user {user_id}: {str(e)}")
            raise SubscriptionError(f"Failed to process subscription change: {str(e)}")
    
    async def process_billing_cycle(
        self, 
        subscription_id: int,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Process subscription billing cycle.
        
        Args:
            subscription_id: Subscription ID
            db: Database session
            
        Returns:
            Billing processing result
        """
        if not db:
            db = get_db_session()
        
        try:
            # Get subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.id == subscription_id
            ).first()
            
            if not subscription:
                raise SubscriptionNotFoundError(f"Subscription {subscription_id} not found")
            
            # Check if billing is due
            current_time = datetime.utcnow()
            if subscription.next_billing_date and subscription.next_billing_date <= current_time:
                
                # Process payment through billing engine
                billing_result = await self.billing.process_subscription_billing(
                    subscription_id, db
                )
                
                if billing_result["success"]:
                    # Update subscription for next cycle
                    await self._update_subscription_for_next_cycle(subscription, db)
                    
                    # Reset usage metrics for new billing period
                    await self.usage_tracker.reset_usage_metrics(
                        subscription.user_id, db
                    )
                    
                    # Publish billing success event
                    await self.events.publish("billing.processed", {
                        "subscription_id": subscription_id,
                        "user_id": subscription.user_id,
                        "amount": str(billing_result["amount"]),
                        "currency": billing_result["currency"],
                        "timestamp": current_time.isoformat()
                    })
                    
                    return {
                        "success": True,
                        "action": "billing_processed",
                        "next_billing_date": subscription.next_billing_date.isoformat(),
                        "amount_charged": billing_result["amount"]
                    }
                
                else:
                    # Handle payment failure
                    await self._handle_billing_failure(subscription, billing_result, db)
                    
                    return {
                        "success": False,
                        "action": "billing_failed",
                        "reason": billing_result["error"],
                        "retry_date": billing_result.get("retry_date")
                    }
            
            return {
                "success": True,
                "action": "no_billing_due",
                "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process billing cycle for subscription {subscription_id}: {str(e)}")
            raise SubscriptionError(f"Failed to process billing cycle: {str(e)}")
    
    async def get_subscription_analytics(
        self,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get subscription analytics and insights.
        
        Args:
            user_id: User ID (None for all users)
            start_date: Analytics start date
            end_date: Analytics end date
            db: Database session
            
        Returns:
            Subscription analytics data
        """
        if not db:
            db = get_db_session()
        
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            analytics_data = {}
            
            if user_id:
                # User-specific analytics
                analytics_data = await self._get_user_analytics(
                    user_id, start_date, end_date, db
                )
            else:
                # Platform-wide analytics
                analytics_data = await self._get_platform_analytics(
                    start_date, end_date, db
                )
            
            return analytics_data
            
        except Exception as e:
            self.logger.error(f"Failed to get subscription analytics: {str(e)}")
            raise SubscriptionError(f"Failed to get analytics: {str(e)}")
    
    # Private helper methods
    
    async def _get_non_subscriber_overview(self, user_id: int) -> Dict[str, Any]:
        """Get overview for non-subscribed user."""
        free_plan_features = await self.tier_controller.get_free_tier_features()
        return {
            "subscription": None,
            "status": "no_subscription",
            "available_features": free_plan_features,
            "suggested_plans": await self.service.get_subscription_plans(),
            "available_actions": ["subscribe"]
        }
    
    async def _get_usage_warnings(self, usage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate usage warnings based on current usage."""
        warnings = []
        
        for feature, usage_info in usage_data.items():
            if isinstance(usage_info, dict) and "usage_percentage" in usage_info:
                percentage = usage_info["usage_percentage"]
                
                if percentage >= 90:
                    warnings.append({
                        "feature": feature,
                        "level": "critical",
                        "message": f"{feature} usage at {percentage}% of limit",
                        "action": "upgrade_recommended"
                    })
                elif percentage >= 75:
                    warnings.append({
                        "feature": feature,
                        "level": "warning", 
                        "message": f"{feature} usage at {percentage}% of limit",
                        "action": "monitor_usage"
                    })
        
        return warnings
    
    async def _get_available_actions(
        self, 
        subscription: UserSubscription
    ) -> List[str]:
        """Get available actions for subscription."""
        actions = []
        
        if subscription.status == SubscriptionStatus.ACTIVE.value:
            actions.extend(["upgrade", "downgrade", "cancel", "update_payment"])
        elif subscription.status == SubscriptionStatus.TRIAL.value:
            actions.extend(["upgrade", "cancel", "add_payment_method"])
        elif subscription.status == SubscriptionStatus.CANCELLED.value:
            actions.extend(["reactivate"])
        elif subscription.status == SubscriptionStatus.SUSPENDED.value:
            actions.extend(["update_payment", "reactivate"])
        
        return actions
    
    async def _get_plans_with_feature(
        self, 
        feature_name: str, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get subscription plans that include specific feature."""
        plans = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True
        ).all()
        
        plans_with_feature = []
        for plan in plans:
            if feature_name in plan.features and plan.features[feature_name]:
                plans_with_feature.append({
                    "id": plan.id,
                    "name": plan.name,
                    "display_name": plan.display_name,
                    "tier_level": plan.tier_level,
                    "monthly_price": float(plan.monthly_price),
                    "yearly_price": float(plan.yearly_price)
                })
        
        return sorted(plans_with_feature, key=lambda x: x["tier_level"])
    
    async def _get_higher_tier_plans(
        self, 
        user_id: int, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get higher tier plans for user."""
        current_subscription = await self.service.get_active_subscription(user_id, db)
        if not current_subscription:
            return await self._get_plans_with_feature("", db)  # All plans
        
        current_tier = current_subscription.plan.tier_level
        
        higher_plans = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True,
            SubscriptionPlan.tier_level > current_tier
        ).all()
        
        return [{
            "id": plan.id,
            "name": plan.name,
            "display_name": plan.display_name,
            "tier_level": plan.tier_level,
            "monthly_price": float(plan.monthly_price),
            "yearly_price": float(plan.yearly_price)
        } for plan in higher_plans]
    
    async def _validate_change_parameters(
        self, 
        user_id: int, 
        action: str, 
        kwargs: Dict[str, Any]
    ) -> None:
        """Validate subscription change parameters."""
        valid_actions = ["subscribe", "upgrade", "downgrade", "cancel", "reactivate"]
        
        if action not in valid_actions:
            raise ValidationError(f"Invalid action: {action}")
        
        if action in ["subscribe", "upgrade", "downgrade"] and "plan_id" not in kwargs:
            raise ValidationError(f"plan_id required for action: {action}")
        
        if action == "reactivate" and "payment_method_id" not in kwargs:
            raise ValidationError("payment_method_id required for reactivation")
    
    async def _clear_subscription_caches(self, user_id: int) -> None:
        """Clear subscription-related caches."""
        cache_keys = [
            f"subscription_overview:{user_id}",
            f"user_subscription:{user_id}",
            f"usage_metrics:{user_id}",
            f"feature_access:{user_id}"
        ]
        
        for key in cache_keys:
            await self.cache.delete(key)
    
    async def _send_subscription_notifications(
        self, 
        user_id: int, 
        action: str, 
        result: Dict[str, Any]
    ) -> None:
        """Send subscription change notifications."""
        # Implementation would send emails/notifications based on action
        # This is a placeholder for notification service integration
        pass
    
    async def _update_subscription_for_next_cycle(
        self, 
        subscription: UserSubscription, 
        db: Session
    ) -> None:
        """Update subscription for next billing cycle."""
        # Calculate next billing date
        if subscription.billing_cycle == BillingCycleType.MONTHLY.value:
            subscription.next_billing_date += timedelta(days=30)
            subscription.end_date += timedelta(days=30)
        elif subscription.billing_cycle == BillingCycleType.YEARLY.value:
            subscription.next_billing_date += timedelta(days=365)
            subscription.end_date += timedelta(days=365)
        elif subscription.billing_cycle == BillingCycleType.QUARTERLY.value:
            subscription.next_billing_date += timedelta(days=90)
            subscription.end_date += timedelta(days=90)
        
        subscription.updated_at = datetime.utcnow()
        db.commit()
    
    async def _handle_billing_failure(
        self, 
        subscription: UserSubscription, 
        billing_result: Dict[str, Any],
        db: Session
    ) -> None:
        """Handle billing failure scenarios."""
        # Update subscription status
        subscription.status = SubscriptionStatus.SUSPENDED.value
        subscription.updated_at = datetime.utcnow()
        
        # Schedule retry if applicable
        retry_days = billing_result.get("retry_days", 3)
        subscription.next_billing_date = datetime.utcnow() + timedelta(days=retry_days)
        
        db.commit()
        
        # Publish billing failure event
        await self.events.publish("billing.failed", {
            "subscription_id": subscription.id,
            "user_id": subscription.user_id,
            "error": billing_result["error"],
            "retry_date": subscription.next_billing_date.isoformat()
        })
    
    async def _get_user_analytics(
        self, 
        user_id: int, 
        start_date: datetime,
        end_date: datetime, 
        db: Session
    ) -> Dict[str, Any]:
        """Get analytics for specific user."""
        # Implementation for user-specific analytics
        return {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "subscription_history": [],
            "usage_trends": {},
            "billing_summary": {}
        }
    
    async def _get_platform_analytics(
        self, 
        start_date: datetime,
        end_date: datetime, 
        db: Session
    ) -> Dict[str, Any]:
        """Get platform-wide subscription analytics."""
        # Implementation for platform analytics
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "subscribers_by_plan": {},
            "revenue_metrics": {},
            "churn_analysis": {},
            "growth_metrics": {}
        }


__all__ = ['SubscriptionManager']
