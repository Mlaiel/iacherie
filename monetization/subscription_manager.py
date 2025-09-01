"""Advanced Subscription Management with Automatic Prorations
Comprehensive subscription lifecycle management with intelligent proration calculations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import json

from .billing_engine import BillingEngine, BillingPlan, Subscription, SubscriptionStatus

logger = logging.getLogger(__name__)


class ProrationMethod(Enum):
    """Proration calculation methods"""
    DAILY = "daily"
    HOURLY = "hourly"
    IMMEDIATE = "immediate"
    NEXT_CYCLE = "next_cycle"


class SubscriptionChangeType(Enum):
    """Types of subscription changes"""
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    ADDON = "addon"
    REMOVAL = "removal"
    QUANTITY_CHANGE = "quantity_change"


@dataclass
class SubscriptionAddon:
    """Subscription addon structure"""
    id: str
    name: str
    price: Decimal
    currency: str
    quantity: int = 1
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SubscriptionChange:
    """Subscription change tracking"""
    id: str
    subscription_id: str
    change_type: SubscriptionChangeType
    old_plan_id: Optional[str] = None
    new_plan_id: Optional[str] = None
    old_quantity: Optional[int] = None
    new_quantity: Optional[int] = None
    proration_amount: Decimal = Decimal("0.00")
    effective_date: datetime = None
    created_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.effective_date is None:
            self.effective_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()


class SubscriptionManager:
    """Advanced subscription management with prorations"""
    
    def __init__(self, billing_engine: BillingEngine):
        self.billing_engine = billing_engine
        self.subscription_addons: Dict[str, List[SubscriptionAddon]] = {}
        self.subscription_changes: Dict[str, List[SubscriptionChange]] = {}
        self.proration_credits: Dict[str, Decimal] = {}  # customer_id -> credit_amount
        self._initialize_addon_catalog()
    
    def _initialize_addon_catalog(self):
        """Initialize available addon services"""
        self.addon_catalog = {
            "extra_storage_10gb": SubscriptionAddon(
                id="extra_storage_10gb",
                name="Extra 10GB Storage",
                price=Decimal("9.99"),
                currency="EUR"
            ),
            "premium_analytics": SubscriptionAddon(
                id="premium_analytics",
                name="Premium Analytics Package",
                price=Decimal("19.99"),
                currency="EUR"
            ),
            "white_label": SubscriptionAddon(
                id="white_label",
                name="White Label Solution",
                price=Decimal("49.99"),
                currency="EUR"
            ),
            "priority_support": SubscriptionAddon(
                id="priority_support",
                name="Priority Support 24/7",
                price=Decimal("29.99"),
                currency="EUR"
            ),
            "api_access": SubscriptionAddon(
                id="api_access",
                name="Advanced API Access",
                price=Decimal("39.99"),
                currency="EUR"
            )
        }
    
    async def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        proration_method: ProrationMethod = ProrationMethod.DAILY,
        effective_immediately: bool = True
    ) -> Dict[str, Any]:
        """Upgrade subscription with intelligent proration"""
        try:
            if subscription_id not in self.billing_engine.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            subscription = self.billing_engine.subscriptions[subscription_id]
            old_plan = self.billing_engine.plans[subscription.plan_id]
            new_plan = self.billing_engine.plans[new_plan_id]
            
            # Validate upgrade path
            if new_plan.price <= old_plan.price:
                return {"success": False, "error": "New plan must be higher value for upgrade"}
            
            # Calculate proration
            proration_result = await self._calculate_upgrade_proration(
                subscription, old_plan, new_plan, proration_method
            )
            
            # Record the change
            change_id = str(uuid.uuid4())
            change = SubscriptionChange(
                id=change_id,
                subscription_id=subscription_id,
                change_type=SubscriptionChangeType.UPGRADE,
                old_plan_id=old_plan.id,
                new_plan_id=new_plan.id,
                proration_amount=proration_result["proration_amount"],
                metadata={
                    "proration_method": proration_method.value,
                    "effective_immediately": effective_immediately
                }
            )
            
            if subscription_id not in self.subscription_changes:
                self.subscription_changes[subscription_id] = []
            self.subscription_changes[subscription_id].append(change)
            
            if effective_immediately:
                # Update subscription immediately
                subscription.plan_id = new_plan_id
                
                # Create proration invoice if amount > 0
                if proration_result["proration_amount"] > 0:
                    await self._create_proration_invoice(
                        subscription, proration_result["proration_amount"], "upgrade"
                    )
                
                # Update next billing cycle
                await self._update_billing_cycle(subscription, new_plan)
            
            logger.info(f"Subscription upgraded: {subscription_id} -> {new_plan_id}")
            return {
                "success": True,
                "subscription": asdict(subscription),
                "proration": proration_result,
                "change_id": change_id
            }
            
        except Exception as e:
            logger.error(f"Error upgrading subscription: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def downgrade_subscription(
        self,
        subscription_id: str,
        new_plan_id: str,
        at_period_end: bool = True,
        proration_method: ProrationMethod = ProrationMethod.DAILY
    ) -> Dict[str, Any]:
        """Downgrade subscription with credit calculation"""
        try:
            if subscription_id not in self.billing_engine.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            subscription = self.billing_engine.subscriptions[subscription_id]
            old_plan = self.billing_engine.plans[subscription.plan_id]
            new_plan = self.billing_engine.plans[new_plan_id]
            
            # Validate downgrade path
            if new_plan.price >= old_plan.price:
                return {"success": False, "error": "New plan must be lower value for downgrade"}
            
            # Calculate credit for downgrade
            credit_result = await self._calculate_downgrade_credit(
                subscription, old_plan, new_plan, proration_method, at_period_end
            )
            
            # Record the change
            change_id = str(uuid.uuid4())
            change = SubscriptionChange(
                id=change_id,
                subscription_id=subscription_id,
                change_type=SubscriptionChangeType.DOWNGRADE,
                old_plan_id=old_plan.id,
                new_plan_id=new_plan.id,
                proration_amount=-credit_result["credit_amount"],  # Negative for credit
                effective_date=subscription.current_period_end if at_period_end else datetime.now(),
                metadata={
                    "proration_method": proration_method.value,
                    "at_period_end": at_period_end
                }
            )
            
            if subscription_id not in self.subscription_changes:
                self.subscription_changes[subscription_id] = []
            self.subscription_changes[subscription_id].append(change)
            
            if at_period_end:
                # Schedule downgrade for period end
                subscription.metadata = subscription.metadata or {}
                subscription.metadata["scheduled_downgrade"] = {
                    "new_plan_id": new_plan_id,
                    "change_id": change_id,
                    "effective_date": subscription.current_period_end.isoformat()
                }
                
                logger.info(f"Subscription downgrade scheduled for period end: {subscription_id}")
                return {
                    "success": True,
                    "message": "Downgrade scheduled for period end",
                    "effective_date": subscription.current_period_end.isoformat(),
                    "change_id": change_id
                }
            else:
                # Immediate downgrade
                subscription.plan_id = new_plan_id
                
                # Apply credit to customer account
                if credit_result["credit_amount"] > 0:
                    await self._apply_proration_credit(
                        subscription.customer_id, credit_result["credit_amount"]
                    )
                
                logger.info(f"Subscription downgraded immediately: {subscription_id}")
                return {
                    "success": True,
                    "subscription": asdict(subscription),
                    "credit": credit_result,
                    "change_id": change_id
                }
                
        except Exception as e:
            logger.error(f"Error downgrading subscription: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_subscription_addon(
        self,
        subscription_id: str,
        addon_id: str,
        quantity: int = 1,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """Add addon to subscription with proration"""
        try:
            if subscription_id not in self.billing_engine.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            if addon_id not in self.addon_catalog:
                return {"success": False, "error": "Addon not found"}
            
            subscription = self.billing_engine.subscriptions[subscription_id]
            addon_template = self.addon_catalog[addon_id]
            
            # Create addon instance
            addon = SubscriptionAddon(
                id=str(uuid.uuid4()),
                name=addon_template.name,
                price=addon_template.price,
                currency=addon_template.currency,
                quantity=quantity,
                metadata={"template_id": addon_id, "added_at": datetime.now().isoformat()}
            )
            
            # Add to subscription
            if subscription_id not in self.subscription_addons:
                self.subscription_addons[subscription_id] = []
            self.subscription_addons[subscription_id].append(addon)
            
            # Calculate proration if enabled
            proration_amount = Decimal("0.00")
            if prorate:
                proration_amount = await self._calculate_addon_proration(subscription, addon)
                
                # Create immediate invoice for proration
                if proration_amount > 0:
                    await self._create_addon_invoice(subscription, addon, proration_amount)
            
            # Record the change
            change_id = str(uuid.uuid4())
            change = SubscriptionChange(
                id=change_id,
                subscription_id=subscription_id,
                change_type=SubscriptionChangeType.ADDON,
                proration_amount=proration_amount,
                metadata={
                    "addon_id": addon.id,
                    "addon_template_id": addon_id,
                    "quantity": quantity
                }
            )
            
            if subscription_id not in self.subscription_changes:
                self.subscription_changes[subscription_id] = []
            self.subscription_changes[subscription_id].append(change)
            
            logger.info(f"Addon added to subscription: {subscription_id} + {addon_id}")
            return {
                "success": True,
                "addon": asdict(addon),
                "proration_amount": float(proration_amount),
                "change_id": change_id
            }
            
        except Exception as e:
            logger.error(f"Error adding subscription addon: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def remove_subscription_addon(
        self,
        subscription_id: str,
        addon_id: str,
        prorate_credit: bool = True
    ) -> Dict[str, Any]:
        """Remove addon from subscription with credit calculation"""
        try:
            if subscription_id not in self.subscription_addons:
                return {"success": False, "error": "No addons found for subscription"}
            
            addon_list = self.subscription_addons[subscription_id]
            addon = next((a for a in addon_list if a.id == addon_id), None)
            
            if not addon:
                return {"success": False, "error": "Addon not found"}
            
            # Remove addon
            addon_list.remove(addon)
            
            # Calculate credit if enabled
            credit_amount = Decimal("0.00")
            if prorate_credit:
                subscription = self.billing_engine.subscriptions[subscription_id]
                credit_amount = await self._calculate_addon_removal_credit(subscription, addon)
                
                # Apply credit to customer account
                if credit_amount > 0:
                    await self._apply_proration_credit(subscription.customer_id, credit_amount)
            
            # Record the change
            change_id = str(uuid.uuid4())
            change = SubscriptionChange(
                id=change_id,
                subscription_id=subscription_id,
                change_type=SubscriptionChangeType.REMOVAL,
                proration_amount=-credit_amount,  # Negative for credit
                metadata={
                    "removed_addon_id": addon_id,
                    "addon_name": addon.name
                }
            )
            
            if subscription_id not in self.subscription_changes:
                self.subscription_changes[subscription_id] = []
            self.subscription_changes[subscription_id].append(change)
            
            logger.info(f"Addon removed from subscription: {subscription_id} - {addon_id}")
            return {
                "success": True,
                "removed_addon": asdict(addon),
                "credit_amount": float(credit_amount),
                "change_id": change_id
            }
            
        except Exception as e:
            logger.error(f"Error removing subscription addon: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def change_subscription_quantity(
        self,
        subscription_id: str,
        new_quantity: int,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """Change subscription quantity with proration"""
        try:
            if subscription_id not in self.billing_engine.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            subscription = self.billing_engine.subscriptions[subscription_id]
            old_quantity = subscription.quantity
            
            if new_quantity == old_quantity:
                return {"success": True, "message": "No change needed"}
            
            plan = self.billing_engine.plans[subscription.plan_id]
            
            # Calculate proration for quantity change
            proration_amount = Decimal("0.00")
            if prorate:
                quantity_diff = new_quantity - old_quantity
                proration_amount = await self._calculate_quantity_proration(
                    subscription, plan, quantity_diff
                )
            
            # Update subscription
            subscription.quantity = new_quantity
            
            # Handle proration
            if proration_amount > 0:
                # Additional charge
                await self._create_proration_invoice(
                    subscription, proration_amount, "quantity_increase"
                )
            elif proration_amount < 0:
                # Credit
                await self._apply_proration_credit(
                    subscription.customer_id, abs(proration_amount)
                )
            
            # Record the change
            change_id = str(uuid.uuid4())
            change = SubscriptionChange(
                id=change_id,
                subscription_id=subscription_id,
                change_type=SubscriptionChangeType.QUANTITY_CHANGE,
                old_quantity=old_quantity,
                new_quantity=new_quantity,
                proration_amount=proration_amount
            )
            
            if subscription_id not in self.subscription_changes:
                self.subscription_changes[subscription_id] = []
            self.subscription_changes[subscription_id].append(change)
            
            logger.info(f"Subscription quantity changed: {subscription_id} {old_quantity} -> {new_quantity}")
            return {
                "success": True,
                "subscription": asdict(subscription),
                "proration_amount": float(proration_amount),
                "change_id": change_id
            }
            
        except Exception as e:
            logger.error(f"Error changing subscription quantity: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_scheduled_changes(self) -> Dict[str, Any]:
        """Process all scheduled subscription changes"""
        try:
            now = datetime.now()
            processed_count = 0
            results = []
            
            for subscription in self.billing_engine.subscriptions.values():
                if not subscription.metadata:
                    continue
                
                # Check for scheduled downgrades
                if "scheduled_downgrade" in subscription.metadata:
                    downgrade_info = subscription.metadata["scheduled_downgrade"]
                    effective_date = datetime.fromisoformat(downgrade_info["effective_date"])
                    
                    if effective_date <= now:
                        # Execute downgrade
                        old_plan_id = subscription.plan_id
                        new_plan_id = downgrade_info["new_plan_id"]
                        
                        subscription.plan_id = new_plan_id
                        
                        # Calculate and apply credit
                        old_plan = self.billing_engine.plans[old_plan_id]
                        new_plan = self.billing_engine.plans[new_plan_id]
                        
                        # Remove scheduled downgrade metadata
                        del subscription.metadata["scheduled_downgrade"]
                        
                        processed_count += 1
                        results.append({
                            "subscription_id": subscription.id,
                            "action": "downgrade_executed",
                            "old_plan": old_plan_id,
                            "new_plan": new_plan_id
                        })
                        
                        logger.info(f"Scheduled downgrade executed: {subscription.id}")
            
            return {
                "success": True,
                "processed": processed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing scheduled changes: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_upgrade_proration(
        self,
        subscription: Subscription,
        old_plan: BillingPlan,
        new_plan: BillingPlan,
        method: ProrationMethod
    ) -> Dict[str, Any]:
        """Calculate proration amount for upgrade"""
        try:
            now = datetime.now()
            
            if method == ProrationMethod.IMMEDIATE:
                # Full new plan price immediately
                return {
                    "proration_amount": new_plan.price * subscription.quantity,
                    "method": method.value,
                    "calculation": "immediate_full_charge"
                }
            
            if method == ProrationMethod.NEXT_CYCLE:
                # No immediate charge, change takes effect next cycle
                return {
                    "proration_amount": Decimal("0.00"),
                    "method": method.value,
                    "calculation": "next_cycle_effective"
                }
            
            # Daily or hourly proration
            total_period = subscription.current_period_end - subscription.current_period_start
            used_period = now - subscription.current_period_start
            remaining_period = subscription.current_period_end - now
            
            if method == ProrationMethod.DAILY:
                total_days = total_period.days
                remaining_days = remaining_period.days
                
                # Calculate unused amount from old plan
                daily_old_rate = (old_plan.price * subscription.quantity) / total_days
                unused_old_amount = daily_old_rate * remaining_days
                
                # Calculate new plan amount for remaining period
                daily_new_rate = (new_plan.price * subscription.quantity) / total_days
                new_amount_remaining = daily_new_rate * remaining_days
                
                proration_amount = new_amount_remaining - unused_old_amount
                
                return {
                    "proration_amount": max(Decimal("0.00"), proration_amount),
                    "method": method.value,
                    "total_days": total_days,
                    "remaining_days": remaining_days,
                    "unused_old_amount": float(unused_old_amount),
                    "new_amount_remaining": float(new_amount_remaining)
                }
            
            elif method == ProrationMethod.HOURLY:
                total_hours = int(total_period.total_seconds() / 3600)
                remaining_hours = int(remaining_period.total_seconds() / 3600)
                
                # Calculate hourly rates
                hourly_old_rate = (old_plan.price * subscription.quantity) / total_hours
                hourly_new_rate = (new_plan.price * subscription.quantity) / total_hours
                
                unused_old_amount = hourly_old_rate * remaining_hours
                new_amount_remaining = hourly_new_rate * remaining_hours
                
                proration_amount = new_amount_remaining - unused_old_amount
                
                return {
                    "proration_amount": max(Decimal("0.00"), proration_amount),
                    "method": method.value,
                    "total_hours": total_hours,
                    "remaining_hours": remaining_hours,
                    "unused_old_amount": float(unused_old_amount),
                    "new_amount_remaining": float(new_amount_remaining)
                }
            
            # Default to daily
            return await self._calculate_upgrade_proration(
                subscription, old_plan, new_plan, ProrationMethod.DAILY
            )
            
        except Exception as e:
            logger.error(f"Error calculating upgrade proration: {str(e)}")
            return {
                "proration_amount": Decimal("0.00"),
                "method": "error",
                "error": str(e)
            }
    
    async def _calculate_downgrade_credit(
        self,
        subscription: Subscription,
        old_plan: BillingPlan,
        new_plan: BillingPlan,
        method: ProrationMethod,
        at_period_end: bool
    ) -> Dict[str, Any]:
        """Calculate credit amount for downgrade"""
        try:
            if at_period_end:
                # No immediate credit, change takes effect at period end
                return {
                    "credit_amount": Decimal("0.00"),
                    "method": "at_period_end",
                    "calculation": "no_immediate_credit"
                }
            
            now = datetime.now()
            remaining_period = subscription.current_period_end - now
            total_period = subscription.current_period_end - subscription.current_period_start
            
            if method == ProrationMethod.DAILY:
                total_days = total_period.days
                remaining_days = remaining_period.days
                
                # Calculate what customer paid for old plan for remaining period
                daily_old_rate = (old_plan.price * subscription.quantity) / total_days
                old_amount_remaining = daily_old_rate * remaining_days
                
                # Calculate what they should pay for new plan for remaining period
                daily_new_rate = (new_plan.price * subscription.quantity) / total_days
                new_amount_remaining = daily_new_rate * remaining_days
                
                credit_amount = old_amount_remaining - new_amount_remaining
                
                return {
                    "credit_amount": max(Decimal("0.00"), credit_amount),
                    "method": method.value,
                    "total_days": total_days,
                    "remaining_days": remaining_days,
                    "old_amount_remaining": float(old_amount_remaining),
                    "new_amount_remaining": float(new_amount_remaining)
                }
            
            # Default calculation
            return {
                "credit_amount": Decimal("0.00"),
                "method": "default",
                "calculation": "no_credit_calculated"
            }
            
        except Exception as e:
            logger.error(f"Error calculating downgrade credit: {str(e)}")
            return {
                "credit_amount": Decimal("0.00"),
                "method": "error",
                "error": str(e)
            }
    
    async def _calculate_addon_proration(
        self,
        subscription: Subscription,
        addon: SubscriptionAddon
    ) -> Decimal:
        """Calculate proration for addon addition"""
        try:
            now = datetime.now()
            remaining_period = subscription.current_period_end - now
            total_period = subscription.current_period_end - subscription.current_period_start
            
            total_days = total_period.days
            remaining_days = remaining_period.days
            
            if remaining_days <= 0:
                return Decimal("0.00")
            
            # Calculate prorated amount for remaining period
            daily_rate = (addon.price * addon.quantity) / total_days
            proration_amount = daily_rate * remaining_days
            
            return proration_amount
            
        except Exception as e:
            logger.error(f"Error calculating addon proration: {str(e)}")
            return Decimal("0.00")
    
    async def _calculate_addon_removal_credit(
        self,
        subscription: Subscription,
        addon: SubscriptionAddon
    ) -> Decimal:
        """Calculate credit for addon removal"""
        try:
            now = datetime.now()
            remaining_period = subscription.current_period_end - now
            total_period = subscription.current_period_end - subscription.current_period_start
            
            total_days = total_period.days
            remaining_days = remaining_period.days
            
            if remaining_days <= 0:
                return Decimal("0.00")
            
            # Calculate credit for remaining period
            daily_rate = (addon.price * addon.quantity) / total_days
            credit_amount = daily_rate * remaining_days
            
            return credit_amount
            
        except Exception as e:
            logger.error(f"Error calculating addon removal credit: {str(e)}")
            return Decimal("0.00")
    
    async def _calculate_quantity_proration(
        self,
        subscription: Subscription,
        plan: BillingPlan,
        quantity_diff: int
    ) -> Decimal:
        """Calculate proration for quantity change"""
        try:
            now = datetime.now()
            remaining_period = subscription.current_period_end - now
            total_period = subscription.current_period_end - subscription.current_period_start
            
            total_days = total_period.days
            remaining_days = remaining_period.days
            
            if remaining_days <= 0:
                return Decimal("0.00")
            
            # Calculate proration for quantity difference
            daily_rate = plan.price / total_days
            proration_amount = daily_rate * quantity_diff * remaining_days
            
            return proration_amount
            
        except Exception as e:
            logger.error(f"Error calculating quantity proration: {str(e)}")
            return Decimal("0.00")
    
    async def _create_proration_invoice(
        self,
        subscription: Subscription,
        amount: Decimal,
        description: str
    ):
        """Create invoice for proration charges"""
        # This would integrate with the billing engine's invoice creation
        # For now, just log the action
        logger.info(f"Proration invoice created: {subscription.id} - {amount} - {description}")
    
    async def _create_addon_invoice(
        self,
        subscription: Subscription,
        addon: SubscriptionAddon,
        amount: Decimal
    ):
        """Create invoice for addon charges"""
        logger.info(f"Addon invoice created: {subscription.id} - {addon.name} - {amount}")
    
    async def _apply_proration_credit(self, customer_id: str, credit_amount: Decimal):
        """Apply proration credit to customer account"""
        if customer_id not in self.proration_credits:
            self.proration_credits[customer_id] = Decimal("0.00")
        
        self.proration_credits[customer_id] += credit_amount
        logger.info(f"Proration credit applied: {customer_id} - {credit_amount}")
    
    async def _update_billing_cycle(self, subscription: Subscription, new_plan: BillingPlan):
        """Update billing cycle after plan change"""
        # Adjust billing cycle if needed
        if subscription.current_period_end <= datetime.now():
            subscription.current_period_start = datetime.now()
            subscription.current_period_end = self.billing_engine._calculate_period_end(
                subscription.current_period_start, new_plan.billing_cycle
            )
    
    async def get_subscription_summary(self, subscription_id: str) -> Dict[str, Any]:
        """Get comprehensive subscription summary with addons and changes"""
        try:
            if subscription_id not in self.billing_engine.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            subscription = self.billing_engine.subscriptions[subscription_id]
            plan = self.billing_engine.plans[subscription.plan_id]
            
            # Get addons
            addons = self.subscription_addons.get(subscription_id, [])
            
            # Get change history
            changes = self.subscription_changes.get(subscription_id, [])
            changes.sort(key=lambda x: x.created_at, reverse=True)
            
            # Calculate total monthly cost
            base_cost = plan.price * subscription.quantity
            addon_cost = sum(addon.price * addon.quantity for addon in addons)
            total_cost = base_cost + addon_cost
            
            return {
                "success": True,
                "subscription": asdict(subscription),
                "plan": asdict(plan),
                "addons": [asdict(addon) for addon in addons],
                "recent_changes": [asdict(change) for change in changes[:10]],
                "cost_breakdown": {
                    "base_cost": float(base_cost),
                    "addon_cost": float(addon_cost),
                    "total_cost": float(total_cost)
                },
                "available_addons": [asdict(addon) for addon in self.addon_catalog.values()]
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription summary: {str(e)}")
            return {"success": False, "error": str(e)}