"""Analytics Services - Revenue Analytics and Performance Tracking
================================================================

Comprehensive analytics services for revenue analysis and performance
monitoring across monetization systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Import analytics services
try:
    from .revenue_analytics import RevenueAnalytics
    revenue_analytics_available = True
except ImportError as e:
    logger.warning(f"Revenue analytics not available: {e}")
    revenue_analytics_available = False

try:
    from .performance_tracker import PerformanceTracker
    performance_tracking_available = True
except ImportError as e:
    logger.warning(f"Performance tracker not available: {e}")
    performance_tracking_available = False

__all__ = [
    "RevenueAnalytics",
    "PerformanceTracker",
    "revenue_analytics_available",
    "performance_tracking_available"
]