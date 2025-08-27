"""
Subscription Management Index

Central hub for subscription-related operations and services.
Provides unified access to all subscription management functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from .subscription_service import SubscriptionService
from .subscription_manager import SubscriptionManager
from .billing_engine import BillingEngine
from .payment_processor import PaymentProcessor
from .subscription_analytics import SubscriptionAnalytics
from .tier_controller import TierController
from .lifecycle_manager import LifecycleManager
from .usage_tracker import UsageTracker


class SubscriptionIndex:
    """
    Central subscription management hub providing unified access to all subscription services.
    
    Manages the complete subscription lifecycle from plan selection to billing and analytics.
    Integrates with payment processors and provides real-time usage tracking.
    """
    
    def __init__(self):
        """Initialize subscription management hub."""
        self.service = SubscriptionService()
        self.manager = SubscriptionManager()
        self.billing = BillingEngine()
        self.payment = PaymentProcessor()
        self.analytics = SubscriptionAnalytics()
        self.tier_controller = TierController()
        self.lifecycle = LifecycleManager()
        self.usage_tracker = UsageTracker()
    
    async def get_user_subscription_status(self, user_id: int) -> Dict[str, Any]:
        """Get complete subscription status for user."""
        subscription = await self.manager.get_active_subscription(user_id)
        usage = await self.usage_tracker.get_current_usage(user_id)
        features = await self.tier_controller.get_available_features(user_id)
        
        return {
            "subscription": subscription,
            "usage": usage,
            "features": features,
            "billing_status": await self.billing.get_billing_status(user_id),
            "next_payment": await self.billing.get_next_payment_date(user_id)
        }
    
    async def process_subscription_change(
        self, 
        user_id: int, 
        new_plan_id: int,
        change_type: str = "upgrade"
    ) -> Dict[str, Any]:
        """Process subscription plan changes with prorations."""
        return await self.lifecycle.process_plan_change(
            user_id, new_plan_id, change_type
        )
    
    async def handle_payment_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle payment processor webhooks."""
        return await self.payment.process_webhook(webhook_data)
    
    async def generate_subscription_analytics(
        self, 
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive subscription analytics."""
        return await self.analytics.generate_analytics_report(start_date, end_date)
    
    async def check_feature_access(self, user_id: int, feature_name: str) -> bool:
        """Check if user has access to specific feature."""
        return await self.tier_controller.check_feature_access(user_id, feature_name)
    
    async def track_feature_usage(
        self, 
        user_id: int, 
        feature_name: str,
        usage_amount: int = 1
    ) -> Dict[str, Any]:
        """Track feature usage and check limits."""
        return await self.usage_tracker.track_usage(
            user_id, feature_name, usage_amount
        )


# Global subscription index instance
subscription_index = SubscriptionIndex()

__all__ = ['SubscriptionIndex', 'subscription_index']
