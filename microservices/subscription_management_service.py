"""
💳 Subscription Management Service
Advanced subscription and billing management system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PENDING = "pending"


class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    QUARTERLY = "quarterly"


class SubscriptionManagementService:
    """Comprehensive subscription and billing management service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.subscription_plans: Dict[str, Dict[str, Any]] = {}
        self.billing_history: Dict[str, List[Dict[str, Any]]] = {}
        self.user_subscriptions: Dict[str, List[str]] = {}
        
        # Initialize default subscription plans
        self._initialize_default_plans()
        
        self.logger.info("✅ SubscriptionManagementService initialized")
    
    def _initialize_default_plans(self):
        """Initialize default subscription plans"""
        self.subscription_plans = {
            "basic": {
                "name": "Basic Plan",
                "price": Decimal("9.99"),
                "currency": "USD",
                "billing_cycles": [BillingCycle.MONTHLY.value],
                "features": [
                    "Basic AI content generation",
                    "5 projects per month",
                    "Email support",
                    "1GB storage"
                ],
                "limits": {
                    "projects": 5,
                    "storage_gb": 1,
                    "api_calls": 1000,
                    "collaborators": 1
                },
                "trial_days": 7
            },
            "pro": {
                "name": "Professional Plan", 
                "price": Decimal("29.99"),
                "currency": "USD",
                "billing_cycles": [BillingCycle.MONTHLY.value, BillingCycle.YEARLY.value],
                "features": [
                    "Advanced AI content generation",
                    "Unlimited projects",
                    "Priority support",
                    "Advanced analytics",
                    "Team collaboration"
                ],
                "limits": {
                    "projects": -1,  # Unlimited
                    "storage_gb": 10,
                    "api_calls": 10000,
                    "collaborators": 5
                },
                "trial_days": 14
            },
            "enterprise": {
                "name": "Enterprise Plan",
                "price": Decimal("99.99"),
                "currency": "USD", 
                "billing_cycles": [BillingCycle.MONTHLY.value, BillingCycle.YEARLY.value, BillingCycle.QUARTERLY.value],
                "features": [
                    "Full AI suite access",
                    "Unlimited everything",
                    "24/7 support",
                    "Custom integrations",
                    "White-label solutions",
                    "Advanced security",
                    "Custom training"
                ],
                "limits": {
                    "projects": -1,
                    "storage_gb": -1,
                    "api_calls": -1,
                    "collaborators": -1
                },
                "trial_days": 30
            }
        }
    
    async def create_subscription(self, user_id: str, plan_id: str, billing_cycle: str = "monthly") -> Dict[str, Any]:
        """Create new subscription for user"""
        try:
            if plan_id not in self.subscription_plans:
                return {
                    "success": False,
                    "error": "Invalid plan ID",
                    "available_plans": list(self.subscription_plans.keys())
                }
            
            plan = self.subscription_plans[plan_id]
            
            if billing_cycle not in plan["billing_cycles"]:
                return {
                    "success": False,
                    "error": "Invalid billing cycle for this plan",
                    "available_cycles": plan["billing_cycles"]
                }
            
            subscription_id = str(uuid.uuid4())
            
            # Calculate billing dates
            start_date = datetime.utcnow()
            if billing_cycle == BillingCycle.MONTHLY.value:
                next_billing = start_date + timedelta(days=30)
            elif billing_cycle == BillingCycle.YEARLY.value:
                next_billing = start_date + timedelta(days=365)
            elif billing_cycle == BillingCycle.WEEKLY.value:
                next_billing = start_date + timedelta(days=7)
            elif billing_cycle == BillingCycle.QUARTERLY.value:
                next_billing = start_date + timedelta(days=90)
            else:
                next_billing = start_date + timedelta(days=30)
            
            # Calculate price with discounts
            price = plan["price"]
            if billing_cycle == BillingCycle.YEARLY.value:
                price = price * 10  # 2 months free for yearly
            elif billing_cycle == BillingCycle.QUARTERLY.value:
                price = price * 2.8  # Small discount for quarterly
            
            subscription = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "status": SubscriptionStatus.ACTIVE.value,
                "billing_cycle": billing_cycle,
                "price": float(price),
                "currency": plan["currency"],
                "features": plan["features"],
                "limits": plan["limits"],
                "start_date": start_date.isoformat(),
                "next_billing_date": next_billing.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "trial_end_date": (start_date + timedelta(days=plan["trial_days"])).isoformat(),
                "auto_renewal": True,
                "payment_failures": 0
            }
            
            # Store subscription
            self.subscriptions[subscription_id] = subscription
            
            # Update user subscriptions
            if user_id not in self.user_subscriptions:
                self.user_subscriptions[user_id] = []
            self.user_subscriptions[user_id].append(subscription_id)
            
            # Initialize billing history
            if user_id not in self.billing_history:
                self.billing_history[user_id] = []
            
            return {
                "success": True,
                "subscription": subscription,
                "message": f"Subscription to {plan['name']} created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Subscription creation failed: {str(e)}")
            return {
                "success": False,
                "error": "Subscription creation failed",
                "message": str(e)
            }
    
    async def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> Dict[str, Any]:
        """Cancel user subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return {
                    "success": False,
                    "error": "Subscription not found"
                }
            
            subscription = self.subscriptions[subscription_id]
            
            if immediate:
                subscription["status"] = SubscriptionStatus.CANCELLED.value
                subscription["cancelled_at"] = datetime.utcnow().isoformat()
                subscription["end_date"] = datetime.utcnow().isoformat()
            else:
                # Cancel at end of billing period
                subscription["status"] = SubscriptionStatus.CANCELLED.value
                subscription["cancelled_at"] = datetime.utcnow().isoformat()
                subscription["end_date"] = subscription["next_billing_date"]
                subscription["auto_renewal"] = False
            
            return {
                "success": True,
                "message": "Subscription cancelled successfully",
                "effective_date": subscription.get("end_date"),
                "subscription": subscription
            }
            
        except Exception as e:
            self.logger.error(f"Subscription cancellation failed: {str(e)}")
            return {
                "success": False,
                "error": "Cancellation failed",
                "message": str(e)
            }
    
    async def upgrade_subscription(self, subscription_id: str, new_plan_id: str) -> Dict[str, Any]:
        """Upgrade user subscription to a different plan"""
        try:
            if subscription_id not in self.subscriptions:
                return {
                    "success": False,
                    "error": "Subscription not found"
                }
            
            if new_plan_id not in self.subscription_plans:
                return {
                    "success": False,
                    "error": "Invalid new plan ID"
                }
            
            subscription = self.subscriptions[subscription_id]
            new_plan = self.subscription_plans[new_plan_id]
            
            # Calculate prorated amount
            old_plan = self.subscription_plans[subscription["plan_id"]]
            proration_credit = await self._calculate_proration(subscription, old_plan, new_plan)
            
            # Update subscription
            subscription["plan_id"] = new_plan_id
            subscription["plan_name"] = new_plan["name"]
            subscription["price"] = float(new_plan["price"])
            subscription["features"] = new_plan["features"]
            subscription["limits"] = new_plan["limits"]
            subscription["upgraded_at"] = datetime.utcnow().isoformat()
            
            # Add billing record for upgrade
            billing_record = {
                "type": "upgrade",
                "from_plan": old_plan["name"],
                "to_plan": new_plan["name"],
                "proration_credit": proration_credit,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            user_id = subscription["user_id"]
            self.billing_history[user_id].append(billing_record)
            
            return {
                "success": True,
                "message": f"Subscription upgraded to {new_plan['name']}",
                "proration_credit": proration_credit,
                "subscription": subscription
            }
            
        except Exception as e:
            self.logger.error(f"Subscription upgrade failed: {str(e)}")
            return {
                "success": False,
                "error": "Upgrade failed",
                "message": str(e)
            }
    
    async def _calculate_proration(self, subscription: Dict[str, Any], old_plan: Dict[str, Any], new_plan: Dict[str, Any]) -> float:
        """Calculate proration for plan changes"""
        try:
            # Simple proration calculation
            days_remaining = (datetime.fromisoformat(subscription["next_billing_date"]) - datetime.utcnow()).days
            total_days = 30  # Assume monthly billing for simplification
            
            old_daily_rate = float(old_plan["price"]) / total_days
            new_daily_rate = float(new_plan["price"]) / total_days
            
            proration = (new_daily_rate - old_daily_rate) * days_remaining
            return round(proration, 2)
            
        except Exception:
            return 0.0
    
    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a user"""
        try:
            if user_id not in self.user_subscriptions:
                return []
            
            user_subscription_ids = self.user_subscriptions[user_id]
            subscriptions = []
            
            for sub_id in user_subscription_ids:
                if sub_id in self.subscriptions:
                    subscriptions.append(self.subscriptions[sub_id])
            
            return subscriptions
            
        except Exception as e:
            self.logger.error(f"Failed to get user subscriptions: {str(e)}")
            return []
    
    async def process_billing(self, subscription_id: str) -> Dict[str, Any]:
        """Process billing for a subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return {
                    "success": False,
                    "error": "Subscription not found"
                }
            
            subscription = self.subscriptions[subscription_id]
            
            if subscription["status"] != SubscriptionStatus.ACTIVE.value:
                return {
                    "success": False,
                    "error": "Subscription not active"
                }
            
            # Mock successful billing
            billing_record = {
                "subscription_id": subscription_id,
                "amount": subscription["price"],
                "currency": subscription["currency"],
                "status": "paid",
                "billing_date": datetime.utcnow().isoformat(),
                "period_start": subscription["next_billing_date"],
                "period_end": (datetime.fromisoformat(subscription["next_billing_date"]) + timedelta(days=30)).isoformat()
            }
            
            # Update next billing date
            if subscription["billing_cycle"] == BillingCycle.MONTHLY.value:
                next_billing = datetime.fromisoformat(subscription["next_billing_date"]) + timedelta(days=30)
            elif subscription["billing_cycle"] == BillingCycle.YEARLY.value:
                next_billing = datetime.fromisoformat(subscription["next_billing_date"]) + timedelta(days=365)
            else:
                next_billing = datetime.fromisoformat(subscription["next_billing_date"]) + timedelta(days=30)
            
            subscription["next_billing_date"] = next_billing.isoformat()
            subscription["last_billing_date"] = datetime.utcnow().isoformat()
            subscription["payment_failures"] = 0
            
            # Add to billing history
            user_id = subscription["user_id"]
            if user_id in self.billing_history:
                self.billing_history[user_id].append(billing_record)
            
            return {
                "success": True,
                "billing_record": billing_record,
                "next_billing_date": subscription["next_billing_date"]
            }
            
        except Exception as e:
            self.logger.error(f"Billing processing failed: {str(e)}")
            return {
                "success": False,
                "error": "Billing failed",
                "message": str(e)
            }
    
    async def get_billing_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get billing history for user"""
        try:
            if user_id not in self.billing_history:
                return []
            
            history = self.billing_history[user_id]
            # Return most recent records first
            return sorted(history, key=lambda x: x.get("billing_date", ""), reverse=True)[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get billing history: {str(e)}")
            return []
    
    async def get_subscription_analytics(self) -> Dict[str, Any]:
        """Get subscription analytics and metrics"""
        try:
            total_subscriptions = len(self.subscriptions)
            active_subscriptions = sum(1 for sub in self.subscriptions.values() 
                                     if sub["status"] == SubscriptionStatus.ACTIVE.value)
            
            # Revenue calculation
            total_monthly_revenue = sum(
                float(sub["price"]) for sub in self.subscriptions.values() 
                if sub["status"] == SubscriptionStatus.ACTIVE.value and sub["billing_cycle"] == "monthly"
            )
            
            # Plan distribution
            plan_distribution = {}
            for sub in self.subscriptions.values():
                plan_id = sub["plan_id"]
                plan_distribution[plan_id] = plan_distribution.get(plan_id, 0) + 1
            
            return {
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "monthly_recurring_revenue": round(total_monthly_revenue, 2),
                "plan_distribution": plan_distribution,
                "churn_rate": round((total_subscriptions - active_subscriptions) / max(1, total_subscriptions) * 100, 2),
                "analytics_generated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")
            return {"error": "Analytics generation failed"}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "SubscriptionManagementService",
            "status": "healthy",
            "total_subscriptions": len(self.subscriptions),
            "active_plans": len(self.subscription_plans),
            "users_with_subscriptions": len(self.user_subscriptions),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['SubscriptionManagementService', 'SubscriptionStatus', 'BillingCycle']