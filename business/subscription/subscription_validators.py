"""
Subscription Validators

Comprehensive validation system for subscription operations, business rules,
and data integrity checks across the subscription management system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any, List, Tuple
import re
import logging
from sqlalchemy.orm import Session

from .models import (
    UserSubscription, SubscriptionPlan, PaymentMethod,
    SubscriptionStatus, BillingCycleType, PaymentStatus,
    FeatureType, SubscriptionPlanConfig
)
from ..core.database import get_db_session
from ..core.exceptions import (
    ValidationError, SubscriptionError, PaymentError,
    SubscriptionNotFoundError, InsufficientPermissionError
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class SubscriptionValidators:
    """
    Comprehensive validation system for subscription operations.
    
    Provides validation for:
    - Subscription plan configurations and business rules
    - User subscription state transitions and validity
    - Payment method validation and security checks
    - Billing cycle and pricing validations
    - Feature access and quota limit validations
    - Usage tracking and limit enforcement validations
    - Data integrity and consistency checks
    - Business rule compliance and policy enforcement
    """
    
    def __init__(self):
        """Initialize subscription validators."""
        self.logger = get_logger(__name__)
        
        # Validation configuration
        self.min_plan_price = Decimal('0.00')
        self.max_plan_price = Decimal('9999.99')
        self.max_trial_days = 90
        self.min_trial_days = 0
        self.valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
        self.valid_billing_cycles = [cycle.value for cycle in BillingCycleType]
        self.valid_subscription_statuses = [status.value for status in SubscriptionStatus]
        
        # Business rule configuration
        self.max_concurrent_subscriptions = 1  # One active subscription per user
        self.allow_immediate_downgrades = False
        self.require_payment_method_for_paid_plans = True
        self.enforce_trial_limitations = True
    
    async def validate_subscription_plan(
        self,
        plan_config: SubscriptionPlanConfig,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Validate subscription plan configuration.
        
        Args:
            plan_config: Plan configuration to validate
            db: Database session
            
        Returns:
            Validation result with errors and warnings
        """
        if not db:
            db = get_db_session()
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "plan_config": plan_config
        }
        
        try:
            # Basic field validation
            await self._validate_plan_basic_fields(plan_config, validation_result)
            
            # Pricing validation
            await self._validate_plan_pricing(plan_config, validation_result)
            
            # Features and limits validation
            await self._validate_plan_features(plan_config, validation_result)
            
            # Business rule validation
            await self._validate_plan_business_rules(plan_config, validation_result, db)
            
            # Tier hierarchy validation
            await self._validate_plan_tier_hierarchy(plan_config, validation_result, db)
            
            # Set overall validity
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Plan validation failed: {str(e)}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation system error: {str(e)}")
            return validation_result
    
    async def validate_subscription_creation(
        self,
        user_id: int,
        plan_id: int,
        billing_cycle: str,
        payment_method_id: Optional[str] = None,
        trial_days: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Validate subscription creation request.
        
        Args:
            user_id: User ID
            plan_id: Subscription plan ID
            billing_cycle: Billing cycle
            payment_method_id: Payment method ID
            trial_days: Trial days override
            db: Database session
            
        Returns:
            Validation result
        """
        if not db:
            db = get_db_session()
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "subscription_data": {
                "user_id": user_id,
                "plan_id": plan_id,
                "billing_cycle": billing_cycle,
                "payment_method_id": payment_method_id,
                "trial_days": trial_days
            }
        }
        
        try:
            # Validate user eligibility
            await self._validate_user_eligibility(user_id, validation_result, db)
            
            # Validate plan exists and is active
            plan = await self._validate_plan_availability(plan_id, validation_result, db)
            
            # Validate billing cycle
            await self._validate_billing_cycle(billing_cycle, validation_result)
            
            # Validate payment method requirements
            if plan:
                await self._validate_payment_method_requirements(
                    plan, payment_method_id, validation_result, db
                )
            
            # Validate trial configuration
            await self._validate_trial_configuration(
                plan, trial_days, validation_result
            )
            
            # Validate business rules
            await self._validate_subscription_business_rules(
                user_id, plan, validation_result, db
            )
            
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Subscription creation validation failed: {str(e)}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation system error: {str(e)}")
            return validation_result
    
    async def validate_subscription_change(
        self,
        user_id: int,
        current_subscription: UserSubscription,
        change_type: str,
        new_plan_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate subscription change request.
        
        Args:
            user_id: User ID
            current_subscription: Current subscription
            change_type: Type of change (upgrade, downgrade, cancel, etc.)
            new_plan_id: New plan ID for upgrades/downgrades
            **kwargs: Additional change parameters
            
        Returns:
            Validation result
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "change_data": {
                "user_id": user_id,
                "change_type": change_type,
                "current_plan_id": current_subscription.plan_id,
                "new_plan_id": new_plan_id
            }
        }
        
        try:
            # Validate current subscription state
            await self._validate_subscription_state(current_subscription, validation_result)
            
            # Validate change type
            await self._validate_change_type(change_type, validation_result)
            
            # Validate specific change requirements
            if change_type in ["upgrade", "downgrade"]:
                await self._validate_plan_change(
                    current_subscription, new_plan_id, change_type, validation_result
                )
            elif change_type == "cancel":
                await self._validate_cancellation(current_subscription, validation_result, **kwargs)
            elif change_type == "reactivate":
                await self._validate_reactivation(current_subscription, validation_result, **kwargs)
            
            # Validate business rules for change
            await self._validate_change_business_rules(
                current_subscription, change_type, validation_result, **kwargs
            )
            
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Subscription change validation failed: {str(e)}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation system error: {str(e)}")
            return validation_result
    
    async def validate_payment_method(
        self,
        user_id: int,
        payment_data: Dict[str, Any],
        provider: str = "stripe"
    ) -> Dict[str, Any]:
        """
        Validate payment method data.
        
        Args:
            user_id: User ID
            payment_data: Payment method data
            provider: Payment provider
            
        Returns:
            Validation result
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "payment_data": payment_data
        }
        
        try:
            # Validate provider
            if provider not in ["stripe", "paypal", "wise"]:
                validation_result["errors"].append(f"Unsupported payment provider: {provider}")
            
            # Validate payment data based on provider
            if provider == "stripe":
                await self._validate_stripe_payment_data(payment_data, validation_result)
            elif provider == "paypal":
                await self._validate_paypal_payment_data(payment_data, validation_result)
            elif provider == "wise":
                await self._validate_wise_payment_data(payment_data, validation_result)
            
            # Validate billing details
            await self._validate_billing_details(payment_data, validation_result)
            
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Payment method validation failed: {str(e)}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation system error: {str(e)}")
            return validation_result
    
    async def validate_usage_tracking(
        self,
        user_id: int,
        feature_name: str,
        usage_amount: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate usage tracking request.
        
        Args:
            user_id: User ID
            feature_name: Feature name
            usage_amount: Usage amount
            metadata: Usage metadata
            
        Returns:
            Validation result
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "usage_data": {
                "user_id": user_id,
                "feature_name": feature_name,
                "usage_amount": usage_amount,
                "metadata": metadata
            }
        }
        
        try:
            # Validate user ID
            if not isinstance(user_id, int) or user_id <= 0:
                validation_result["errors"].append("Invalid user ID")
            
            # Validate feature name
            if not feature_name or not isinstance(feature_name, str):
                validation_result["errors"].append("Feature name is required")
            elif not re.match(r'^[a-z_][a-z0-9_]*$', feature_name):
                validation_result["errors"].append("Invalid feature name format")
            
            # Validate usage amount
            if not isinstance(usage_amount, int) or usage_amount < 0:
                validation_result["errors"].append("Usage amount must be a non-negative integer")
            elif usage_amount > 10000:  # Reasonable upper limit
                validation_result["warnings"].append("Large usage amount detected")
            
            # Validate metadata
            if metadata is not None:
                if not isinstance(metadata, dict):
                    validation_result["errors"].append("Metadata must be a dictionary")
                elif len(str(metadata)) > 10000:  # Size limit
                    validation_result["warnings"].append("Large metadata size detected")
            
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Usage tracking validation failed: {str(e)}")
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation system error: {str(e)}")
            return validation_result
    
    # Private validation helper methods
    
    async def _validate_plan_basic_fields(
        self, 
        plan_config: SubscriptionPlanConfig, 
        result: Dict[str, Any]
    ) -> None:
        """Validate basic plan fields."""
        # Name validation
        if not plan_config.name:
            result["errors"].append("Plan name is required")
        elif not re.match(r'^[a-z_][a-z0-9_]*$', plan_config.name):
            result["errors"].append("Plan name must contain only lowercase letters, numbers, and underscores")
        elif len(plan_config.name) > 50:
            result["errors"].append("Plan name must be 50 characters or less")
        
        # Display name validation
        if not plan_config.display_name:
            result["errors"].append("Plan display name is required")
        elif len(plan_config.display_name) > 150:
            result["errors"].append("Plan display name must be 150 characters or less")
        
        # Description validation
        if plan_config.description and len(plan_config.description) > 1000:
            result["warnings"].append("Plan description is quite long")
        
        # Tier level validation
        if not isinstance(plan_config.tier_level, int) or plan_config.tier_level < 0:
            result["errors"].append("Tier level must be a non-negative integer")
        elif plan_config.tier_level > 10:
            result["warnings"].append("High tier level detected")
    
    async def _validate_plan_pricing(
        self, 
        plan_config: SubscriptionPlanConfig, 
        result: Dict[str, Any]
    ) -> None:
        """Validate plan pricing."""



        try:
            # Monthly price validation
            if plan_config.monthly_price < self.min_plan_price:
                result["errors"].append(f"Monthly price must be at least {self.min_plan_price}")
            elif plan_config.monthly_price > self.max_plan_price:
                result["errors"].append(f"Monthly price must not exceed {self.max_plan_price}")
            
            # Yearly price validation
            if plan_config.yearly_price < self.min_plan_price:
                result["errors"].append(f"Yearly price must be at least {self.min_plan_price}")
            elif plan_config.yearly_price > self.max_plan_price * 12:
                result["errors"].append(f"Yearly price seems too high")
            
            # Price relationship validation
            if (plan_config.monthly_price > 0 and plan_config.yearly_price > 0 and
                plan_config.yearly_price > plan_config.monthly_price * 12):
                result["warnings"].append("Yearly price is higher than 12x monthly price")
            elif (plan_config.monthly_price > 0 and plan_config.yearly_price > 0 and
                  plan_config.yearly_price < plan_config.monthly_price * 8):
                result["warnings"].append("Yearly price offers significant discount (>33%)")
            
        except (InvalidOperation, TypeError) as e:
            result["errors"].append("Invalid price format")
    
    async def _validate_plan_features(
        self, 
        plan_config: SubscriptionPlanConfig, 
        result: Dict[str, Any]
    ) -> None:
        """Validate plan features and limits."""
        # Features validation
        if not isinstance(plan_config.features, dict):
            result["errors"].append("Features must be a dictionary")
        else:
            for feature_name, feature_value in plan_config.features.items():
                if not isinstance(feature_name, str):
                    result["errors"].append(f"Feature name must be string: {feature_name}")
                elif not re.match(r'^[a-z_][a-z0-9_]*$', feature_name):
                    result["errors"].append(f"Invalid feature name format: {feature_name}")
        
        # Limits validation
        if not isinstance(plan_config.limits, dict):
            result["errors"].append("Limits must be a dictionary")
        else:
            for limit_name, limit_value in plan_config.limits.items():
                if not isinstance(limit_name, str):
                    result["errors"].append(f"Limit name must be string: {limit_name}")
                elif not isinstance(limit_value, (int, type(None))):
                    result["errors"].append(f"Limit value must be integer or null: {limit_name}")
                elif isinstance(limit_value, int) and limit_value < 0:
                    result["errors"].append(f"Limit value must be non-negative: {limit_name}")
        
        # Trial days validation
        if not isinstance(plan_config.trial_days, int) or plan_config.trial_days < self.min_trial_days:
            result["errors"].append(f"Trial days must be at least {self.min_trial_days}")
        elif plan_config.trial_days > self.max_trial_days:
            result["errors"].append(f"Trial days must not exceed {self.max_trial_days}")
    
    async def _validate_plan_business_rules(
        self, 
        plan_config: SubscriptionPlanConfig, 
        result: Dict[str, Any], 
        db: Session
    ) -> None:
        """Validate plan business rules."""
        # Check for duplicate plan names
        existing_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == plan_config.name
        ).first()
        
        if existing_plan:
            result["errors"].append(f"Plan with name '{plan_config.name}' already exists")
        
        # Validate free tier rules
        if plan_config.monthly_price == 0 and plan_config.yearly_price == 0:
            if plan_config.trial_days > 0:
                result["warnings"].append("Free plans typically don't need trial periods")
        
        # Validate enterprise plan rules
        if plan_config.is_enterprise:
            if plan_config.tier_level < 3:
                result["warnings"].append("Enterprise plans typically have high tier levels")
    
    async def _validate_plan_tier_hierarchy(
        self, 
        plan_config: SubscriptionPlanConfig, 
        result: Dict[str, Any], 
        db: Session
    ) -> None:
        """Validate plan tier hierarchy consistency."""
        # Get existing plans at same tier level
        existing_same_tier = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier_level == plan_config.tier_level,
            SubscriptionPlan.is_active == True
        ).all()
        
        if existing_same_tier:
            result["warnings"].append(f"Another plan exists at tier level {plan_config.tier_level}")
        
        # Check pricing consistency with tier hierarchy
        lower_tier_plans = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier_level < plan_config.tier_level,
            SubscriptionPlan.is_active == True
        ).all()
        
        for lower_plan in lower_tier_plans:
            if (lower_plan.monthly_price > plan_config.monthly_price and 
                plan_config.monthly_price > 0):
                result["warnings"].append(
                    f"Lower tier plan '{lower_plan.name}' has higher monthly price"
                )
    
    async def _validate_user_eligibility(
        self, 
        user_id: int, 
        result: Dict[str, Any], 
        db: Session
    ) -> None:
        """Validate user eligibility for subscription."""
        # Check for existing active subscriptions
        existing_subscriptions = db.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ])
        ).count()
        
        if existing_subscriptions >= self.max_concurrent_subscriptions:
            result["errors"].append("User already has the maximum number of active subscriptions")
    
    async def _validate_plan_availability(
        self, 
        plan_id: int, 
        result: Dict[str, Any], 
        db: Session
    ) -> Optional[SubscriptionPlan]:
        """Validate plan exists and is available."""
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == plan_id
        ).first()
        
        if not plan:
            result["errors"].append(f"Subscription plan {plan_id} not found")
            return None
        
        if not plan.is_active:
            result["errors"].append(f"Subscription plan {plan_id} is not active")
            return None
        
        return plan
    
    async def _validate_billing_cycle(
        self, 
        billing_cycle: str, 
        result: Dict[str, Any]
    ) -> None:
        """Validate billing cycle."""
        if billing_cycle not in self.valid_billing_cycles:
            result["errors"].append(f"Invalid billing cycle: {billing_cycle}")
    
    async def _validate_payment_method_requirements(
        self, 
        plan: SubscriptionPlan, 
        payment_method_id: Optional[str], 
        result: Dict[str, Any], 
        db: Session
    ) -> None:
        """Validate payment method requirements."""
        # Check if payment method is required for paid plans
        if (self.require_payment_method_for_paid_plans and 
            plan.monthly_price > 0 and plan.yearly_price > 0 and 
            not payment_method_id):
            result["errors"].append("Payment method is required for paid plans")
        
        # Validate payment method exists if provided
        if payment_method_id:
            payment_method = db.query(PaymentMethod).filter(
                PaymentMethod.payment_method_id == payment_method_id,
                PaymentMethod.is_active == True
            ).first()
            
            if not payment_method:
                result["errors"].append("Payment method not found or inactive")
    
    async def _validate_trial_configuration(
        self, 
        plan: Optional[SubscriptionPlan], 
        trial_days: Optional[int], 
        result: Dict[str, Any]
    ) -> None:
        """Validate trial configuration."""
        if trial_days is not None:
            if trial_days < self.min_trial_days or trial_days > self.max_trial_days:
                result["errors"].append(
                    f"Trial days must be between {self.min_trial_days} and {self.max_trial_days}"
                )
            
            # Check if trial is appropriate for plan
            if plan and plan.monthly_price == 0 and trial_days > 0:
                result["warnings"].append("Trial period for free plan may not be necessary")
    
    async def _validate_subscription_business_rules(
        self, 
        user_id: int, 
        plan: Optional[SubscriptionPlan], 
        result: Dict[str, Any], 
        db: Session
    ) -> None:
        """Validate subscription business rules."""
        # Check trial limitations if enabled
        if self.enforce_trial_limitations and plan:
            # Check if user has already used trial for this plan
            previous_trials = db.query(UserSubscription).filter(
                UserSubscription.user_id == user_id,
                UserSubscription.plan_id == plan.id,
                UserSubscription.trial_end_date.isnot(None)
            ).count()
            
            if previous_trials > 0:
                result["warnings"].append("User has previously used trial for this plan")
    
    async def _validate_subscription_state(
        self, 
        subscription: UserSubscription, 
        result: Dict[str, Any]
    ) -> None:
        """Validate current subscription state."""
        if subscription.status not in self.valid_subscription_statuses:
            result["errors"].append(f"Invalid subscription status: {subscription.status}")
        
        # Check subscription is not expired
        if subscription.end_date <= datetime.utcnow():
            result["errors"].append("Subscription has expired")
    
    async def _validate_change_type(
        self, 
        change_type: str, 
        result: Dict[str, Any]
    ) -> None:
        """Validate subscription change type."""
        valid_change_types = ["upgrade", "downgrade", "cancel", "reactivate", "convert_trial"]
        if change_type not in valid_change_types:
            result["errors"].append(f"Invalid change type: {change_type}")
    
    async def _validate_plan_change(
        self, 
        current_subscription: UserSubscription, 
        new_plan_id: Optional[int], 
        change_type: str, 
        result: Dict[str, Any]
    ) -> None:
        """Validate plan change request."""
        if not new_plan_id:
            result["errors"].append("New plan ID is required for plan changes")
            return
        
        if new_plan_id == current_subscription.plan_id:
            result["errors"].append("New plan is the same as current plan")
            return
        
        # Validate change direction matches plan tiers
        # This would require fetching the new plan and comparing tier levels
    
    async def _validate_cancellation(
        self, 
        subscription: UserSubscription, 
        result: Dict[str, Any], 
        **kwargs
    ) -> None:
        """Validate cancellation request."""
        if subscription.status == SubscriptionStatus.CANCELLED.value:
            result["errors"].append("Subscription is already cancelled")
        
        if subscription.status == SubscriptionStatus.EXPIRED.value:
            result["warnings"].append("Cancelling an expired subscription")
    
    async def _validate_reactivation(
        self, 
        subscription: UserSubscription, 
        result: Dict[str, Any], 
        **kwargs
    ) -> None:
        """Validate reactivation request."""
        if subscription.status not in [SubscriptionStatus.CANCELLED.value, SubscriptionStatus.SUSPENDED.value]:
            result["errors"].append("Can only reactivate cancelled or suspended subscriptions")
        
        payment_method_id = kwargs.get("payment_method_id")
        if not payment_method_id:
            result["errors"].append("Payment method is required for reactivation")
    
    async def _validate_change_business_rules(
        self, 
        subscription: UserSubscription, 
        change_type: str, 
        result: Dict[str, Any], 
        **kwargs
    ) -> None:
        """Validate business rules for subscription changes."""
        # Implement business rule validations
        # For example, restrictions on downgrades, minimum subscription periods, etc.
        pass
    
    async def _validate_stripe_payment_data(
        self, 
        payment_data: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """Validate Stripe payment method data."""
        if "type" not in payment_data:
            result["errors"].append("Payment method type is required")
        
        if payment_data.get("type") == "card":
            if "card" not in payment_data:
                result["errors"].append("Card details are required for card payments")
    
    async def _validate_paypal_payment_data(
        self, 
        payment_data: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """Validate PayPal payment method data."""
        # PayPal-specific validation logic
        pass
    
    async def _validate_wise_payment_data(
        self, 
        payment_data: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """Validate Wise payment method data."""
        # Wise-specific validation logic
        pass
    
    async def _validate_billing_details(
        self, 
        payment_data: Dict[str, Any], 
        result: Dict[str, Any]
    ) -> None:
        """Validate billing details."""
        billing_details = payment_data.get("billing_details", {})
        
        # Name validation
        if "name" in billing_details:
            if not billing_details["name"] or len(billing_details["name"]) < 2:
                result["warnings"].append("Billing name seems too short")
        
        # Email validation
        if "email" in billing_details:
            email = billing_details["email"]
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                result["errors"].append("Invalid email format in billing details")
        
        # Address validation
        address = billing_details.get("address", {})
        if address:
            if not address.get("country"):
                result["warnings"].append("Country is recommended in billing address")


__all__ = ['SubscriptionValidators']
