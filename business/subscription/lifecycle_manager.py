"""Lifecycle Manager

Subscription lifecycle management orchestrator handling state transitions,
automated workflows, and business rule enforcement throughout subscription lifecycle.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
import logging
from sqlalchemy.orm import Session
from enum import Enum

from .models import (
    UserSubscription, SubscriptionPlan, SubscriptionHistory,
    SubscriptionStatus, BillingCycleType, PaymentStatus
)
from .subscription_service import SubscriptionService
from .billing_engine import BillingEngine
from .payment_processor import PaymentProcessor
from ..core.database import get_db_session
from ..core.exceptions import (
    SubscriptionError, ValidationError, LifecycleError,
    SubscriptionNotFoundError, PaymentError
)
from ..core.logging import get_logger
from ..core.events import EventPublisher
from ..core.notifications import NotificationService

logger = get_logger(__name__)


class LifecycleEvent(Enum):
    """Subscription lifecycle events."""    SUBSCRIPTION_CREATED = "subscription_created"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDING_SOON = "trial_ending_soon"
    TRIAL_CONVERTED = "trial_converted"
    TRIAL_EXPIRED = "trial_expired"
    SUBSCRIPTION_RENEWED = "subscription_renewed"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    SUBSCRIPTION_DOWNGRADED = "subscription_downgraded"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_RETRY_SCHEDULED = "payment_retry_scheduled"
    SUBSCRIPTION_SUSPENDED = "subscription_suspended"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    SUBSCRIPTION_REACTIVATED = "subscription_reactivated"
    SUBSCRIPTION_EXPIRED = "subscription_expired"


class LifecycleManager:
    """    Comprehensive subscription lifecycle management system.
    
    Manages:
    - Subscription state transitions and validation
    - Automated lifecycle workflows and triggers
    - Trial period management and conversion tracking
    - Payment failure handling and dunning management
    - Subscription upgrade/downgrade workflows
    - Cancellation and reactivation processes
    - Automated notifications and communications
    - Business rule enforcement and validation
    - Analytics and lifecycle reporting
    """    
    def __init__(self):
        """Initialize lifecycle manager."""        self.logger = get_logger(__name__)
        self.subscription_service = SubscriptionService()
        self.billing_engine = BillingEngine()
        self.payment_processor = PaymentProcessor()
        self.events = EventPublisher()
        self.notifications = NotificationService()
        
        # Lifecycle configuration
        self.trial_warning_days = [7, 3, 1]  # Days before trial ends
        self.payment_retry_schedule = [1, 3, 7]  # Days between payment retries
        self.suspension_grace_period = 7  # Days before suspension after payment failure
        self.cancellation_survey_enabled = True
        self.reactivation_incentive_enabled = True
    
    async def handle_subscription_change(
        self,
        user_id: int,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """        Handle subscription lifecycle changes with validation and automation.
        
        Args:
            user_id: User ID
            action: Lifecycle action to perform
            **kwargs: Action-specific parameters
            
        Returns:
            Change result with updated subscription information
        """        try:
            # Validate action
            if action not in self._get_valid_actions():
                raise ValidationError(f"Invalid lifecycle action: {action}")
            
            # Execute action based on type
            if action == "subscribe":
                result = await self._handle_subscription_creation(user_id, **kwargs)
            elif action == "upgrade":
                result = await self._handle_subscription_upgrade(user_id, **kwargs)
            elif action == "downgrade":
                result = await self._handle_subscription_downgrade(user_id, **kwargs)
            elif action == "cancel":
                result = await self._handle_subscription_cancellation(user_id, **kwargs)
            elif action == "reactivate":
                result = await self._handle_subscription_reactivation(user_id, **kwargs)
            elif action == "convert_trial":
                result = await self._handle_trial_conversion(user_id, **kwargs)
            else:
                raise ValidationError(f"Unhandled action: {action}")
            
            # Trigger post-change workflows
            await self._trigger_post_change_workflows(user_id, action, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Subscription lifecycle change failed for user {user_id}: {str(e)}")
            raise LifecycleError(f"Lifecycle change failed: {str(e)}")
    
    async def process_scheduled_tasks(
        self,
        task_types: Optional[List[str]] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Process scheduled lifecycle tasks.
        
        Args:
            task_types: Optional list of task types to process
            db: Database session
            
        Returns:
            Processing results
        """        if not db:
            db = get_db_session()
        
        all_task_types = [
            "trial_warnings",
            "trial_expirations",
            "payment_retries",
            "subscription_renewals",
            "suspension_processing",
            "expiration_cleanup"
        ]
        
        if task_types is None:
            task_types = all_task_types
        
        results = {}
        
        try:
            for task_type in task_types:
                if task_type == "trial_warnings":
                    results["trial_warnings"] = await self._process_trial_warnings(db)
                elif task_type == "trial_expirations":
                    results["trial_expirations"] = await self._process_trial_expirations(db)
                elif task_type == "payment_retries":
                    results["payment_retries"] = await self._process_payment_retries(db)
                elif task_type == "subscription_renewals":
                    results["subscription_renewals"] = await self._process_subscription_renewals(db)
                elif task_type == "suspension_processing":
                    results["suspension_processing"] = await self._process_suspensions(db)
                elif task_type == "expiration_cleanup":
                    results["expiration_cleanup"] = await self._process_expirations(db)
            
            return {
                "processed_tasks": list(results.keys()),
                "results": results,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Scheduled task processing failed: {str(e)}")
            raise LifecycleError(f"Scheduled task processing failed: {str(e)}")
    
    async def get_lifecycle_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        db: Session = None
    ) -> Dict[str, Any]:
        """        Get lifecycle analytics for specified period.
        
        Args:
            start_date: Analysis start date
            end_date: Analysis end date
            db: Database session
            
        Returns:
            Lifecycle analytics data
        """        if not db:
            db = get_db_session()
        
        try:
            # Get lifecycle events from history
            lifecycle_events = db.query(SubscriptionHistory).filter(
                SubscriptionHistory.created_at >= start_date,
                SubscriptionHistory.created_at <= end_date
            ).all()
            
            # Analyze events
            event_counts = {}
            conversion_metrics = {}
            
            for event in lifecycle_events:
                action = event.action_type
                event_counts[action] = event_counts.get(action, 0) + 1
            
            # Trial conversion analysis
            trial_starts = event_counts.get("subscribe", 0)  # Trials that started
            trial_conversions = event_counts.get("convert_trial", 0)  # Trials converted to paid
            conversion_rate = (trial_conversions / max(trial_starts, 1)) * 100
            
            # Churn analysis
            cancellations = event_counts.get("cancel", 0)
            reactivations = event_counts.get("reactivate", 0)
            net_churn = cancellations - reactivations
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "event_counts": event_counts,
                "conversion_metrics": {
                    "trial_starts": trial_starts,
                    "trial_conversions": trial_conversions,
                    "conversion_rate_percent": round(conversion_rate, 2)
                },
                "churn_metrics": {
                    "cancellations": cancellations,
                    "reactivations": reactivations,
                    "net_churn": net_churn
                }
            }
            
        except Exception as e:
            self.logger.error(f"Lifecycle analytics generation failed: {str(e)}")
            raise LifecycleError(f"Failed to generate lifecycle analytics: {str(e)}")
    
    # Private action handlers
    
    async def _handle_subscription_creation(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle new subscription creation."""        try:
            # Create subscription through service
            subscription = await self.subscription_service.subscribe_user_to_plan(
                user_id=user_id,
                plan_id=kwargs["plan_id"],
                billing_cycle=kwargs.get("billing_cycle", "monthly"),
                payment_method_id=kwargs.get("payment_method_id"),
                trial_days=kwargs.get("trial_days")
            )
            
            # Determine if this is a trial or paid subscription
            if subscription.status == SubscriptionStatus.TRIAL.value:
                await self._trigger_lifecycle_event(
                    user_id, LifecycleEvent.TRIAL_STARTED, {"subscription_id": subscription.id}
                )
            else:
                await self._trigger_lifecycle_event(
                    user_id, LifecycleEvent.SUBSCRIPTION_CREATED, {"subscription_id": subscription.id}
                )
            
            return {
                "success": True,
                "action": "subscription_created",
                "subscription_id": subscription.id,
                "status": subscription.status,
                "is_trial": subscription.status == SubscriptionStatus.TRIAL.value,
                "end_date": subscription.end_date.isoformat()
            }
            
        except Exception as e:
            raise LifecycleError(f"Subscription creation failed: {str(e)}")
    
    async def _handle_subscription_upgrade(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle subscription upgrade."""        try:
            subscription = await self.subscription_service.upgrade_subscription(
                user_id=user_id,
                new_plan_id=kwargs["plan_id"],
                proration=kwargs.get("proration", True)
            )
            
            await self._trigger_lifecycle_event(
                user_id, 
                LifecycleEvent.SUBSCRIPTION_UPGRADED,
                {
                    "subscription_id": subscription.id,
                    "new_plan_id": kwargs["plan_id"],
                    "proration_applied": kwargs.get("proration", True)
                }
            )
            
            return {
                "success": True,
                "action": "subscription_upgraded",
                "subscription_id": subscription.id,
                "new_plan": subscription.plan.name,
                "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None
            }
            
        except Exception as e:
            raise LifecycleError(f"Subscription upgrade failed: {str(e)}")
    
    async def _handle_subscription_downgrade(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle subscription downgrade."""        try:
            subscription = await self.subscription_service.downgrade_subscription(
                user_id=user_id,
                new_plan_id=kwargs["plan_id"],
                effective_date=kwargs.get("effective_date")
            )
            
            await self._trigger_lifecycle_event(
                user_id,
                LifecycleEvent.SUBSCRIPTION_DOWNGRADED,
                {
                    "subscription_id": subscription.id,
                    "new_plan_id": kwargs["plan_id"],
                    "effective_date": kwargs.get("effective_date")
                }
            )
            
            return {
                "success": True,
                "action": "subscription_downgraded",
                "subscription_id": subscription.id,
                "new_plan": subscription.plan.name,
                "effective_date": kwargs.get("effective_date", datetime.utcnow()).isoformat()
            }
            
        except Exception as e:
            raise LifecycleError(f"Subscription downgrade failed: {str(e)}")
    
    async def _handle_subscription_cancellation(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle subscription cancellation."""        try:
            subscription = await self.subscription_service.cancel_subscription(
                user_id=user_id,
                cancellation_reason=kwargs.get("reason"),
                immediate=kwargs.get("immediate", False)
            )
            
            await self._trigger_lifecycle_event(
                user_id,
                LifecycleEvent.SUBSCRIPTION_CANCELLED,
                {
                    "subscription_id": subscription.id,
                    "reason": kwargs.get("reason"),
                    "immediate": kwargs.get("immediate", False)
                }
            )
            
            # Schedule cancellation survey if enabled
            if self.cancellation_survey_enabled:
                await self._schedule_cancellation_survey(user_id, subscription)
            
            return {
                "success": True,
                "action": "subscription_cancelled",
                "subscription_id": subscription.id,
                "cancelled_at": subscription.cancelled_at.isoformat(),
                "access_until": subscription.end_date.isoformat()
            }
            
        except Exception as e:
            raise LifecycleError(f"Subscription cancellation failed: {str(e)}")
    
    async def _handle_subscription_reactivation(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle subscription reactivation."""        try:
            subscription = await self.subscription_service.reactivate_subscription(
                user_id=user_id,
                payment_method_id=kwargs["payment_method_id"]
            )
            
            await self._trigger_lifecycle_event(
                user_id,
                LifecycleEvent.SUBSCRIPTION_REACTIVATED,
                {"subscription_id": subscription.id}
            )
            
            return {
                "success": True,
                "action": "subscription_reactivated",
                "subscription_id": subscription.id,
                "status": subscription.status,
                "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None
            }
            
        except Exception as e:
            raise LifecycleError(f"Subscription reactivation failed: {str(e)}")
    
    async def _handle_trial_conversion(
        self,
        user_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Handle trial to paid conversion."""        try:
            db = get_db_session()
            
            # Get trial subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status == SubscriptionStatus.TRIAL.value
            ).first()
            
            if not subscription:
                raise SubscriptionNotFoundError("No trial subscription found")
            
            # Update subscription status
            subscription.status = SubscriptionStatus.ACTIVE.value
            subscription.payment_method_id = kwargs["payment_method_id"]
            subscription.trial_end_date = None
            
            # Set next billing date
            subscription.next_billing_date = subscription.end_date
            subscription.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(subscription)
            
            await self._trigger_lifecycle_event(
                user_id,
                LifecycleEvent.TRIAL_CONVERTED,
                {"subscription_id": subscription.id}
            )
            
            return {
                "success": True,
                "action": "trial_converted",
                "subscription_id": subscription.id,
                "status": subscription.status,
                "next_billing_date": subscription.next_billing_date.isoformat()
            }
            
        except Exception as e:
            raise LifecycleError(f"Trial conversion failed: {str(e)}")
    
    # Private task processors
    
    async def _process_trial_warnings(self, db: Session) -> Dict[str, Any]:
        """Process trial ending warnings."""        processed = 0
        
        for warning_days in self.trial_warning_days:
            warning_date = datetime.utcnow() + timedelta(days=warning_days)
            
            # Find trials ending in warning_days
            trials_ending = db.query(UserSubscription).filter(
                UserSubscription.status == SubscriptionStatus.TRIAL.value,
                UserSubscription.trial_end_date >= warning_date.date(),
                UserSubscription.trial_end_date < (warning_date + timedelta(days=1)).date()
            ).all()
            
            for subscription in trials_ending:
                await self._trigger_lifecycle_event(
                    subscription.user_id,
                    LifecycleEvent.TRIAL_ENDING_SOON,
                    {
                        "subscription_id": subscription.id,
                        "days_remaining": warning_days
                    }
                )
                processed += 1
        
        return {"trial_warnings_sent": processed}
    
    async def _process_trial_expirations(self, db: Session) -> Dict[str, Any]:
        """Process expired trials."""        current_date = datetime.utcnow()
        
        expired_trials = db.query(UserSubscription).filter(
            UserSubscription.status == SubscriptionStatus.TRIAL.value,
            UserSubscription.trial_end_date < current_date.date()
        ).all()
        
        processed = 0
        for subscription in expired_trials:
            # Update subscription status
            subscription.status = SubscriptionStatus.EXPIRED.value
            subscription.end_date = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            
            await self._trigger_lifecycle_event(
                subscription.user_id,
                LifecycleEvent.TRIAL_EXPIRED,
                {"subscription_id": subscription.id}
            )
            
            processed += 1
        
        db.commit()
        return {"expired_trials_processed": processed}
    
    async def _process_payment_retries(self, db: Session) -> Dict[str, Any]:
        """Process payment retries for failed payments."""        # Implementation would handle payment retry logic
        return {"payment_retries_processed": 0}
    
    async def _process_subscription_renewals(self, db: Session) -> Dict[str, Any]:
        """Process subscription renewals."""        # Implementation would handle automatic renewals
        return {"renewals_processed": 0}
    
    async def _process_suspensions(self, db: Session) -> Dict[str, Any]:
        """Process subscription suspensions for failed payments."""        # Implementation would handle suspension logic
        return {"suspensions_processed": 0}
    
    async def _process_expirations(self, db: Session) -> Dict[str, Any]:
        """Process subscription expirations."""        # Implementation would handle expiration cleanup
        return {"expirations_processed": 0}
    
    # Private helper methods
    
    def _get_valid_actions(self) -> List[str]:
        """Get list of valid lifecycle actions."""        return [
            "subscribe",
            "upgrade", 
            "downgrade",
            "cancel",
            "reactivate",
            "convert_trial"
        ]
    
    async def _trigger_lifecycle_event(
        self,
        user_id: int,
        event: LifecycleEvent,
        data: Dict[str, Any]
    ) -> None:
        """Trigger lifecycle event with notifications and analytics."""        event_data = {
            "user_id": user_id,
            "event_type": event.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        # Publish event
        await self.events.publish(f"subscription.lifecycle.{event.value}", event_data)
        
        # Send notifications based on event type
        await self._send_lifecycle_notification(user_id, event, data)
    
    async def _send_lifecycle_notification(
        self,
        user_id: int,
        event: LifecycleEvent,
        data: Dict[str, Any]
    ) -> None:
        """Send appropriate notification based on lifecycle event."""        notification_templates = {
            LifecycleEvent.TRIAL_STARTED: "trial_welcome",
            LifecycleEvent.TRIAL_ENDING_SOON: "trial_ending_reminder",
            LifecycleEvent.TRIAL_CONVERTED: "subscription_welcome",
            LifecycleEvent.TRIAL_EXPIRED: "trial_expired_upgrade_offer",
            LifecycleEvent.SUBSCRIPTION_CREATED: "subscription_confirmation",
            LifecycleEvent.SUBSCRIPTION_UPGRADED: "upgrade_confirmation",
            LifecycleEvent.SUBSCRIPTION_CANCELLED: "cancellation_confirmation",
            LifecycleEvent.SUBSCRIPTION_REACTIVATED: "reactivation_welcome",
            LifecycleEvent.PAYMENT_FAILED: "payment_failure_notice"
        }
        
        template = notification_templates.get(event)
        if template:
            await self.notifications.send_email(
                user_id=user_id,
                template=template,
                data=data
            )
    
    async def _trigger_post_change_workflows(
        self,
        user_id: int,
        action: str,
        result: Dict[str, Any]
    ) -> None:
        """Trigger post-change workflows and automation."""        # This would handle post-change automation like:
        # - Updating user permissions
        # - Triggering integrations
        # - Starting onboarding flows
        # - Analytics tracking
        pass
    
    async def _schedule_cancellation_survey(
        self,
        user_id: int,
        subscription: UserSubscription
    ) -> None:
        """Schedule cancellation survey."""        # Implementation would schedule a cancellation survey
        # to understand why the user cancelled
        pass


__all__ = ['LifecycleManager', 'LifecycleEvent']
