"""IA Influencer Agent - Subscription Management Module

This module provides comprehensive subscription management for the multi-format creator platform.
Handles subscription plans, billing cycles, feature access control, and integration with payment processors.

Architecture:
- Subscription Plans: Multi-tier subscription management (Free, Pro, Enterprise, Creator Studio)
- Billing Engine: Automated billing cycles, prorations, and invoice generation
- Feature Access: Granular feature control based on subscription level
- Payment Integration: Stripe, Wise, PayPal integration for global payment processing
- Usage Tracking: Monitor usage limits and quotas per subscription tier
- Subscription Lifecycle: Upgrades, downgrades, cancellations, renewals

Core Business Logic:
User (creator) → Subscribe to plan → Access tier-specific features → Usage tracking → 
Billing cycle → Payment processing → Feature access control → Analytics & insights

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying, modification, or distribution strictly prohibited.

WARNING: This code is proprietary and confidential. Any unauthorized use, reproduction,
or distribution of this code or any portion of it may result in severe civil and
criminal penalties, and will be prosecuted to the maximum extent possible under law.
"""

from .subscription_service import SubscriptionService

from .subscription_manager import SubscriptionManager

from .billing_engine import BillingEngine

from .payment_processor import PaymentProcessor

from .subscription_analytics import SubscriptionAnalytics

from .tier_controller import TierController

from .lifecycle_manager import LifecycleManager

from .usage_tracker import UsageTracker

from .subscription_validators import SubscriptionValidators

from .models import (
    SubscriptionPlan,
    UserSubscription,
    BillingCycle,
    PaymentMethod,
    Invoice,
    UsageMetrics,
    SubscriptionHistory,
    FeatureAccess
)

__all__ = [
    'SubscriptionService',
    'SubscriptionManager', 
    'BillingEngine',
    'PaymentProcessor',
    'SubscriptionAnalytics',
    'TierController',
    'LifecycleManager',
    'UsageTracker',
    'SubscriptionValidators',
    'SubscriptionPlan',
    'UserSubscription',
    'BillingCycle',
    'PaymentMethod',
    'Invoice',
    'UsageMetrics',
    'SubscriptionHistory',
    'FeatureAccess'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
