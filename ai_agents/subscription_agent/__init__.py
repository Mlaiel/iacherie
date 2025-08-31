"""Subscription Agent - Ultra-Advanced Enterprise System

This module provides enterprise-grade subscription capabilities with
intelligent management and comprehensive functionality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

# Master Manager
from .manager import (
    SubscriptionManager,
    SubscriptionSystemStatus
)

# Core System
from .core.subscription_engine import (
    SubscriptionEngine,
    SubscriptionJob,
    SubscriptionResult
)

# Legacy compatibility (for smooth migration)
from .manager import SubscriptionManager as SubscriptionAgent

__all__ = [
    # Master Manager
    'SubscriptionManager',
    'SubscriptionSystemStatus',
    
    # Core System
    'SubscriptionEngine',
    'SubscriptionJob',
    'SubscriptionResult',
    
    # Legacy compatibility
    'SubscriptionAgent'
]