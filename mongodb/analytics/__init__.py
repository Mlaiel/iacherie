"""MongoDB Analytics Engine Module
================================

Business intelligence and advanced analytics for MongoDB data.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Track loaded analytics modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    try:
        module = __import__(f"mongodb.analytics.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded analytics.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load analytics.{module_name}: {e}")
        return False

# Import analytics modules
_safe_import('metrics_calculator')
_safe_import('trend_analyzer')
_safe_import('cohort_analyzer')
_safe_import('funnel_analyzer')
_safe_import('retention_analyzer')
_safe_import('revenue_analyzer')
_safe_import('behavior_analyzer')

__all__ = [
    'MetricsCalculator', 'TrendAnalyzer', 'CohortAnalyzer', 'FunnelAnalyzer',
    'RetentionAnalyzer', 'RevenueAnalyzer', 'BehaviorAnalyzer',
    'get_metrics_calculator', 'get_trend_analyzer', 'get_cohort_analyzer'
]

logger.info(f"MongoDB Analytics Engine module initialized - Version {__version__}")