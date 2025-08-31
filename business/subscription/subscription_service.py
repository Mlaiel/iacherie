"""Subscription Service

Core subscription management service providing comprehensive subscription lifecycle management.
Handles plan subscriptions, upgrades, downgrades, cancellations, and feature access control.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List, Tuple
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import (
    SubscriptionPlan, UserSubscription, BillingCycle, PaymentMethod,
    Invoice, UsageMetrics, SubscriptionHistory, FeatureAccess,
    SubscriptionStatus, BillingCycleType, PaymentStatus,
    SubscriptionPlanConfig, SUBSCRIPTION_PLANS
)
from ..core.database import get_db_session
from ..core.exceptions import (
    SubscriptionError, ValidationError, PaymentError,
    SubscriptionNotFoundError, InsufficientPermissionError
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class SubscriptionService:
    """    Comprehensive subscription management service.
    
    Provides complete subscription lifecycle management including:
    - Plan creation and management
    - User subscription handling
    - Feature access control
    - Usage tracking and limits
    - Billing and payment integration
    """    
    def __init__(self):
        """Initialize subscription service."""        self.logger = logging.getLogger(__name__)
    
    async def create_subscription_plan(
        self, 
        plan_config: SubscriptionPlanConfig,
        db: Session = None
    ) -> SubscriptionPlan:
        """        Create a new subscription plan.
        
        Args:
            plan_config: Plan configuration
            db: Database session
            
        Returns:
            Created subscription plan
            
        Raises:
            ValidationError: If plan configuration is invalid
        """        if not db:
            db = get_db_session()
        
        try:
            # Validate plan configuration
            await self._validate_plan_config(plan_config)
            
            # Check for existing plan with same name
            existing_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.name == plan_config.name
            ).first()
            
            if existing_plan:
                raise ValidationError(f"Plan with name '{plan_config.name}' already exists")
            
            # Create new plan
            plan = SubscriptionPlan(
                name=plan_config.name,
                display_name=plan_config.display_name,
                description=plan_config.description,
                tier_level=plan_config.tier_level,
                monthly_price=plan_config.monthly_price,
                yearly_price=plan_config.yearly_price,
                features=plan_config.features,
                limits=plan_config.limits,
                trial_days=plan_config.trial_days,
                is_popular=plan_config.is_popular,
                is_enterprise=plan_config.is_enterprise
            )
            
            db.add(plan)
            db.commit()
            db.refresh(plan)
            
            # Create feature access entries
            await self._create_feature_access_entries(plan, db)
            
            self.logger.info(f"Created subscription plan: {plan.name}")
            return plan
            
        except Exception as e:
            db.rollback()
            raise SubscriptionError(f"Failed to create subscription plan: {str(e)}")
    
    async def subscribe_user_to_plan(
        self,
        user_id: int,
        plan_id: int,
        billing_cycle: str = "monthly",
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None,
        db: Session = None
    ) -> UserSubscription:
        """        Subscribe user to a plan.
        
        Args:
            user_id: User ID
            plan_id: Subscription plan ID
            billing_cycle: Billing cycle type
            payment_method_id: Payment method ID
            trial_days: Override trial days
            db: Database session
            
        Returns:
            User subscription
            
        Raises:
            SubscriptionError: If subscription creation fails
        """        if not db:
            db = get_db_session()
        
        try:
            # Get subscription plan
            plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == plan_id,
                SubscriptionPlan.is_active == True
            ).first()
            
            if not plan:
                raise SubscriptionNotFoundError(f"Subscription plan {plan_id} not found")
            
            # Check for existing active subscription
            existing_subscription = await self.get_active_subscription(user_id, db)
            if existing_subscription:
                raise SubscriptionError("User already has an active subscription")
            
            # Calculate subscription dates
            start_date = datetime.utcnow()
            trial_end_date = None
            
            # Determine trial period
            actual_trial_days = trial_days if trial_days is not None else plan.trial_days
            if actual_trial_days > 0:
                trial_end_date = start_date + timedelta(days=actual_trial_days)
                end_date = trial_end_date
                status = SubscriptionStatus.TRIAL.value
            else:
                # Calculate end date based on billing cycle
                if billing_cycle == BillingCycleType.MONTHLY.value:
                    end_date = start_date + timedelta(days=30)
                elif billing_cycle == BillingCycleType.YEARLY.value:
                    end_date = start_date + timedelta(days=365)
                elif billing_cycle == BillingCycleType.QUARTERLY.value:
                    end_date = start_date + timedelta(days=90)
                else:
                    raise ValidationError(f"Invalid billing cycle: {billing_cycle}")
                
                status = SubscriptionStatus.ACTIVE.value if payment_method_id else SubscriptionStatus.PENDING.value
            
            # Create subscription
            subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                status=status,
                billing_cycle=billing_cycle,
                start_date=start_date,
                end_date=end_date,
                trial_end_date=trial_end_date,
                payment_method_id=payment_method_id,
                subscription_id=self._generate_subscription_id(),
                next_billing_date=end_date if status != SubscriptionStatus.TRIAL.value else None
            )
            
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            # Initialize usage metrics
            await self._initialize_usage_metrics(subscription, db)
            
            # Record subscription history
            await self._record_subscription_history(
                user_id, subscription.id, "subscribe", None, plan_id,
                None, status, "user", db
            )
            
            self.logger.info(f"User {user_id} subscribed to plan {plan.name}")
            return subscription
            
        except Exception as e:
            db.rollback()
            raise SubscriptionError(f"Failed to create subscription: {str(e)}")
    
    async def get_active_subscription(
        self, 
        user_id: int, 
        db: Session = None
    ) -> Optional[UserSubscription]:
        """        Get active subscription for user.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Active subscription or None
        """        if not db:
            db = get_db_session()
        
        return db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ]),
            UserSubscription.end_date > datetime.utcnow()
        ).first()
    
    async def get_subscription_plans(
        self, 
        include_inactive: bool = False,
        db: Session = None
    ) -> List[SubscriptionPlan]:
        """        Get all available subscription plans.
        
        Args:
            include_inactive: Include inactive plans
            db: Database session
            
        Returns:
            List of subscription plans
        """        if not db:
            db = get_db_session()
        
        query = db.query(SubscriptionPlan)
        if not include_inactive:
            query = query.filter(SubscriptionPlan.is_active == True)
        
        return query.order_by(SubscriptionPlan.tier_level).all()
    
    async def upgrade_subscription(
        self,
        user_id: int,
        new_plan_id: int,
        proration: bool = True,
        db: Session = None
    ) -> UserSubscription:
        """        Upgrade user subscription to higher tier.
        
        Args:
            user_id: User ID
            new_plan_id: New subscription plan ID
            proration: Apply proration for billing
            db: Database session
            
        Returns:
            Updated subscription
            
        Raises:
            SubscriptionError: If upgrade fails
        """        if not db:
            db = get_db_session()
        
        try:
            # Get current subscription
            current_subscription = await self.get_active_subscription(user_id, db)
            if not current_subscription:
                raise SubscriptionNotFoundError("No active subscription found")
            
            # Get new plan
            new_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == new_plan_id,
                SubscriptionPlan.is_active == True
            ).first()
            
            if not new_plan:
                raise SubscriptionNotFoundError(f"Plan {new_plan_id} not found")
            
            # Validate upgrade (new plan must be higher tier)
            current_plan = current_subscription.plan
            if new_plan.tier_level <= current_plan.tier_level:
                raise ValidationError("Can only upgrade to higher tier plans")
            
            # Calculate proration if needed
            proration_amount = Decimal('0.00')
            if proration:
                proration_amount = await self._calculate_proration(
                    current_subscription, new_plan, db
                )
            
            # Update subscription
            old_plan_id = current_subscription.plan_id
            current_subscription.plan_id = new_plan_id
            current_subscription.updated_at = datetime.utcnow()
            
            # Recalculate next billing amount
            if current_subscription.billing_cycle == BillingCycleType.MONTHLY.value:
                current_subscription.next_payment_amount = new_plan.monthly_price
            elif current_subscription.billing_cycle == BillingCycleType.YEARLY.value:
                current_subscription.next_payment_amount = new_plan.yearly_price
            elif current_subscription.billing_cycle == BillingCycleType.QUARTERLY.value:
                current_subscription.next_payment_amount = new_plan.quarterly_price
            
            db.commit()
            db.refresh(current_subscription)
            
            # Update usage metrics for new plan limits
            await self._update_usage_metrics_for_plan_change(current_subscription, db)
            
            # Record subscription history
            await self._record_subscription_history(
                user_id, current_subscription.id, "upgrade", old_plan_id, new_plan_id,
                None, None, "user", db
            )
            
            # Create billing adjustment if proration applies
            if proration_amount > 0:
                await self._create_proration_billing_cycle(
                    current_subscription, proration_amount, db
                )
            
            self.logger.info(f"User {user_id} upgraded from plan {old_plan_id} to {new_plan_id}")
            return current_subscription
            
        except Exception as e:
            db.rollback()
            raise SubscriptionError(f"Failed to upgrade subscription: {str(e)}")
    
    async def downgrade_subscription(
        self,
        user_id: int,
        new_plan_id: int,
        effective_date: Optional[datetime] = None,
        db: Session = None
    ) -> UserSubscription:
        """        Downgrade user subscription to lower tier.
        
        Args:
            user_id: User ID
            new_plan_id: New subscription plan ID
            effective_date: When downgrade takes effect
            db: Database session
            
        Returns:
            Updated subscription
            
        Raises:
            SubscriptionError: If downgrade fails
        """        if not db:
            db = get_db_session()
        
        try:
            # Get current subscription
            current_subscription = await self.get_active_subscription(user_id, db)
            if not current_subscription:
                raise SubscriptionNotFoundError("No active subscription found")
            
            # Get new plan
            new_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.id == new_plan_id,
                SubscriptionPlan.is_active == True
            ).first()
            
            if not new_plan:
                raise SubscriptionNotFoundError(f"Plan {new_plan_id} not found")
            
            # Validate downgrade (new plan must be lower tier)
            current_plan = current_subscription.plan
            if new_plan.tier_level >= current_plan.tier_level:
                raise ValidationError("Can only downgrade to lower tier plans")
            
            # Determine effective date (default to next billing cycle)
            if not effective_date:
                effective_date = current_subscription.next_billing_date or current_subscription.end_date
            
            old_plan_id = current_subscription.plan_id
            
            # If effective immediately
            if effective_date <= datetime.utcnow():
                current_subscription.plan_id = new_plan_id
                current_subscription.updated_at = datetime.utcnow()
                
                # Update billing amount
                if current_subscription.billing_cycle == BillingCycleType.MONTHLY.value:
                    current_subscription.next_payment_amount = new_plan.monthly_price
                elif current_subscription.billing_cycle == BillingCycleType.YEARLY.value:
                    current_subscription.next_payment_amount = new_plan.yearly_price
                elif current_subscription.billing_cycle == BillingCycleType.QUARTERLY.value:
                    current_subscription.next_payment_amount = new_plan.quarterly_price
                
                # Update usage metrics immediately
                await self._update_usage_metrics_for_plan_change(current_subscription, db)
                
            else:
                # Schedule downgrade for future date
                # This would typically involve creating a scheduled change record
                # For now, we'll implement immediate downgrade
                current_subscription.plan_id = new_plan_id
                current_subscription.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(current_subscription)
            
            # Record subscription history
            await self._record_subscription_history(
                user_id, current_subscription.id, "downgrade", old_plan_id, new_plan_id,
                None, None, "user", db
            )
            
            self.logger.info(f"User {user_id} downgraded from plan {old_plan_id} to {new_plan_id}")
            return current_subscription
            
        except Exception as e:
            db.rollback()
            raise SubscriptionError(f"Failed to downgrade subscription: {str(e)}")
    
    async def cancel_subscription(
        self,
        user_id: int,
        cancellation_reason: Optional[str] = None,
        immediate: bool = False,
        db: Session = None
    ) -> UserSubscription:
        """        Cancel user subscription.
        
        Args:
            user_id: User ID
            cancellation_reason: Reason for cancellation
            immediate: Cancel immediately vs. at period end
            db: Database session
            
        Returns:
            Cancelled subscription
            
        Raises:
            SubscriptionError: If cancellation fails
        """        if not db:
            db = get_db_session()
        
        try:
            # Get active subscription
            subscription = await self.get_active_subscription(user_id, db)
            if not subscription:
                raise SubscriptionNotFoundError("No active subscription found")
            
            old_status = subscription.status
            subscription.cancelled_at = datetime.utcnow()
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED.value
                subscription.end_date = datetime.utcnow()
            else:
                # Cancel at period end
                subscription.status = SubscriptionStatus.CANCELLED.value
                # Keep existing end_date to allow access until period ends
            
            subscription.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(subscription)
            
            # Record subscription history
            await self._record_subscription_history(
                user_id, subscription.id, "cancel", None, None,
                old_status, SubscriptionStatus.CANCELLED.value, "user", db
            )
            
            self.logger.info(f"Cancelled subscription for user {user_id}")
            return subscription
            
        except Exception as e:
            db.rollback()
            raise SubscriptionError(f"Failed to cancel subscription: {str(e)}")
    
    async def reactivate_subscription(
        self,
        user_id: int,
        payment_method_id: str,
        db: Session = None
    ) -> UserSubscription:
        """        Reactivate cancelled subscription.
        
        Args:
            user_id: User ID
            payment_method_id: Payment method ID
            db: Database session
            
        Returns:
            Reactivated subscription
            
        Raises:
            SubscriptionError: If reactivation fails
        """        if not db:
            db = get_db_session()
        
        try:
            # Get most recent subscription
            subscription = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status == SubscriptionStatus.CANCELLED.value
            ).order_by(UserSubscription.cancelled_at.desc()).first()
            
            if not subscription:
                raise SubscriptionNotFoundError("No cancelled subscription found to reactivate")
            
            # Reactivate subscription
            old_status = subscription.status
            subscription.status = SubscriptionStatus.ACTIVE.value
            subscription.payment_method_id = payment_method_id
            subscription.cancelled_at = None
            
            # Extend subscription period
            current_time = datetime.utcnow()
            if subscription.billing_cycle == BillingCycleType.MONTHLY.value:
                subscription.end_date = current_time + timedelta(days=30)
                subscription.next_billing_date = subscription.end_date
            elif subscription.billing_cycle == BillingCycleType.YEARLY.value:
                subscription.end_date = current_time + timedelta(days=365)
                subscription.next_billing_date = subscription.end_date
            elif subscription.billing_cycle == BillingCycleType.QUARTERLY.value:
                subscription.end_date = current_time + timedelta(days=90)
                subscription.next_billing_date = subscription.end_date
            
            subscription.updated_at = current_time
            
            db.commit()
            db.refresh(subscription)
            
            # Reinitialize usage metrics
            await self._initialize_usage_metrics(subscription, db)
            
            # Record subscription history
            await self._record_subscription_history(
                user_id, subscription.id, "reactivate", None, None,
                old_status, SubscriptionStatus.ACTIVE.value, "user", db
            )
            
            self.logger.info(f"Reactivated subscription for user {user_id}")
            return subscription
            
        except Exception as e:
            db.rollback()
            raise SubscriptionError(f"Failed to reactivate subscription: {str(e)}")
    
    # Private helper methods
    
    async def _validate_plan_config(self, config: SubscriptionPlanConfig) -> None:
        """Validate subscription plan configuration."""        if not config.name or not config.display_name:
            raise ValidationError("Plan name and display name are required")
        
        if config.tier_level < 0:
            raise ValidationError("Tier level must be non-negative")
        
        if config.monthly_price < 0 or config.yearly_price < 0:
            raise ValidationError("Prices must be non-negative")
        
        if not isinstance(config.features, dict) or not isinstance(config.limits, dict):
            raise ValidationError("Features and limits must be dictionaries")
    
    async def _create_feature_access_entries(
        self, 
        plan: SubscriptionPlan, 
        db: Session
    ) -> None:
        """Create feature access entries for subscription plan."""        # This would create FeatureAccess entries based on plan configuration
        # Implementation depends on specific feature definitions
        pass
    
    def _generate_subscription_id(self) -> str:
        """Generate unique subscription ID."""        import uuid
        return f"sub_{uuid.uuid4().hex[:12]}"
    
    async def _initialize_usage_metrics(
        self, 
        subscription: UserSubscription, 
        db: Session
    ) -> None:
        """Initialize usage metrics for new subscription."""        plan = subscription.plan
        current_time = datetime.utcnow()
        
        # Calculate period based on billing cycle
        if subscription.billing_cycle == BillingCycleType.MONTHLY.value:
            period_end = current_time + timedelta(days=30)
        elif subscription.billing_cycle == BillingCycleType.YEARLY.value:
            period_end = current_time + timedelta(days=365)
        elif subscription.billing_cycle == BillingCycleType.QUARTERLY.value:
            period_end = current_time + timedelta(days=90)
        else:
            period_end = current_time + timedelta(days=30)
        
        # Create usage metrics for each limited feature
        for feature_name, limit in plan.limits.items():
            if isinstance(limit, int):
                usage_metric = UsageMetrics(
                    subscription_id=subscription.id,
                    user_id=subscription.user_id,
                    feature_name=feature_name,
                    usage_count=0,
                    quota_limit=limit,
                    period_start=current_time,
                    period_end=period_end
                )
                db.add(usage_metric)
        
        db.commit()
    
    async def _update_usage_metrics_for_plan_change(
        self, 
        subscription: UserSubscription, 
        db: Session
    ) -> None:
        """Update usage metrics when plan changes."""        # Update quota limits based on new plan
        new_plan = subscription.plan
        
        # Get current usage metrics
        usage_metrics = db.query(UsageMetrics).filter(
            UsageMetrics.subscription_id == subscription.id,
            UsageMetrics.period_end > datetime.utcnow()
        ).all()
        
        # Update limits based on new plan
        for metric in usage_metrics:
            if metric.feature_name in new_plan.limits:
                metric.quota_limit = new_plan.limits[metric.feature_name]
                metric.updated_at = datetime.utcnow()
        
        db.commit()
    
    async def _record_subscription_history(
        self,
        user_id: int,
        subscription_id: Optional[int],
        action_type: str,
        from_plan_id: Optional[int],
        to_plan_id: Optional[int],
        from_status: Optional[str],
        to_status: Optional[str],
        triggered_by: str,
        db: Session
    ) -> None:
        """Record subscription change in history."""        history = SubscriptionHistory(
            user_id=user_id,
            subscription_id=subscription_id,
            action_type=action_type,
            from_plan_id=from_plan_id,
            to_plan_id=to_plan_id,
            from_status=from_status,
            to_status=to_status,
            triggered_by=triggered_by
        )
        
        db.add(history)
        db.commit()
    
    async def _calculate_proration(
        self, 
        subscription: UserSubscription, 
        new_plan: SubscriptionPlan, 
        db: Session
    ) -> Decimal:
        """Calculate proration amount for plan change."""        # Implementation would calculate pro-rated amount
        # based on remaining time in current billing cycle
        # and price difference between plans
        return Decimal('0.00')  # Placeholder
    
    async def _create_proration_billing_cycle(
        self, 
        subscription: UserSubscription, 
        proration_amount: Decimal, 
        db: Session
    ) -> None:
        """Create billing cycle entry for proration."""        billing_cycle = BillingCycle(
            subscription_id=subscription.id,
            cycle_start=datetime.utcnow(),
            cycle_end=datetime.utcnow(),
            billing_amount=proration_amount,
            payment_status=PaymentStatus.PENDING.value,
            prorated_amount=proration_amount
        )
        
        db.add(billing_cycle)
        db.commit()


async def initialize_default_plans(db: Session = None) -> None:
    """Initialize default subscription plans."""    if not db:
        db = get_db_session()
    
    service = SubscriptionService()
    
    for plan_name, plan_config in SUBSCRIPTION_PLANS.items():
        try:
            existing = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.name == plan_name
            ).first()
            
            if not existing:
                await service.create_subscription_plan(plan_config, db)
                logger.info(f"Created default subscription plan: {plan_name}")
            
        except Exception as e:
            logger.error(f"Failed to create plan {plan_name}: {str(e)}")


__all__ = ['SubscriptionService', 'initialize_default_plans']
