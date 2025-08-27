"""
Monetization Module
Automated monetization system for the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .revenue_calculator import RevenueCalculator
from .platform_apis import PlatformAPIManager
from .licensing_engine import LicensingEngine
from .payment_processor import PaymentProcessor
from .distribution_engine import DistributionEngine

__all__ = [
    "RevenueCalculator",
    "PlatformAPIManager", 
    "LicensingEngine",
    "PaymentProcessor",
    "DistributionEngine"
]