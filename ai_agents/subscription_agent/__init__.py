"""Subscription Agent - Recurring Revenue Models Management

This module provides comprehensive subscription management with automated
recurring revenue processing and customer lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .manager import SubscriptionManager
from .core.subscription_engine import SubscriptionEngine

# Legacy compatibility
SubscriptionAgent = SubscriptionManager

__all__ = [
    'SubscriptionManager',
    'SubscriptionEngine', 
    'SubscriptionAgent'
]