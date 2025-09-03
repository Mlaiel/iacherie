"""Payment Services - Secure Payment Processing Module
===================================================

Comprehensive payment processing services including Stripe integration,
cryptocurrency payments, and subscription management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Import payment services
try:
    from .stripe_integration import StripeIntegration
    stripe_available = True
except ImportError as e:
    logger.warning(f"Stripe integration not available: {e}")
    stripe_available = False

try:
    from .crypto_payments import CryptoPayments
    crypto_available = True
except ImportError as e:
    logger.warning(f"Crypto payments not available: {e}")
    crypto_available = False

try:
    from .subscription_manager import SubscriptionManager
    subscription_available = True
except ImportError as e:
    logger.warning(f"Subscription manager not available: {e}")
    subscription_available = False

__all__ = [
    "StripeIntegration",
    "CryptoPayments",
    "SubscriptionManager",
    "stripe_available",
    "crypto_available", 
    "subscription_available"
]