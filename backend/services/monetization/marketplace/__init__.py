"""Marketplace Services - Content Marketplace and Licensing Module
===============================================================

Comprehensive marketplace services for content licensing, royalty calculation,
and marketplace management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Import marketplace services
try:
    from .content_marketplace import ContentMarketplace
    marketplace_available = True
except ImportError as e:
    logger.warning(f"Content marketplace not available: {e}")
    marketplace_available = False

try:
    from .licensing_engine import LicensingEngine
    licensing_available = True
except ImportError as e:
    logger.warning(f"Licensing engine not available: {e}")
    licensing_available = False

try:
    from .royalty_calculator import RoyaltyCalculator
    royalty_available = True
except ImportError as e:
    logger.warning(f"Royalty calculator not available: {e}")
    royalty_available = False

__all__ = [
    "ContentMarketplace",
    "LicensingEngine",
    "RoyaltyCalculator",
    "marketplace_available",
    "licensing_available",
    "royalty_available"
]