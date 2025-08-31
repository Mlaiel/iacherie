"""Advertising Agent - Intelligent Ad Monetization

This module provides intelligent advertising monetization with automated
ad placement optimization and revenue maximization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .manager import AdvertisingManager
from .core.advertising_engine import AdvertisingEngine

# Legacy compatibility
AdvertisingAgent = AdvertisingManager

__all__ = [
    'AdvertisingManager',
    'AdvertisingEngine',
    'AdvertisingAgent'
]