"""MongoDB Aggregation Engine for Ainflue Platform
===============================================

Advanced aggregation pipelines for analytics, reporting, and business intelligence
with dynamic pipeline building and performance optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTED:
- ML Engineer: Advanced analytics and data processing
- DBA: Optimized aggregation pipelines and indexing
- Backend Senior: High-performance data aggregation
- Business Intelligence: Comprehensive reporting and metrics
"""

import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel - All Rights Reserved"
__license__ = "Proprietary - Unauthorized use prohibited"

# Track loaded aggregation modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    """Safely import an aggregation module with error handling."""
    try:
        module = __import__(f"mongodb.aggregation.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded aggregation.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load aggregation.{module_name}: {e}")
        return False

# Import aggregation modules
_safe_import('pipeline_builder')
_safe_import('content_analytics')
_safe_import('user_analytics')
_safe_import('collaboration_analytics')
_safe_import('revenue_analytics')
_safe_import('performance_optimizer')
_safe_import('streaming_aggregation')

# Export public interface
__all__ = [
    # Core aggregation classes
    'PipelineBuilder',
    'ContentAnalytics',
    'UserAnalytics',
    'CollaborationAnalytics',
    'RevenueAnalytics',
    'PerformanceOptimizer',
    'StreamingAggregation',
    
    # Utility functions
    'get_pipeline_builder',
    'get_content_analytics',
    'get_user_analytics',
    'get_performance_optimizer',
    'build_analytics_pipeline',
    
    # Module info
    '__version__',
    '__author__',
    'get_loaded_aggregation_modules',
    'get_failed_aggregation_modules'
]

def get_loaded_aggregation_modules() -> list:
    """Get list of successfully loaded aggregation modules."""
    return _loaded_modules.copy()

def get_failed_aggregation_modules() -> list:
    """Get list of aggregation modules that failed to load."""
    return _failed_modules.copy()

def build_analytics_pipeline(analytics_type: str, **kwargs) -> Dict[str, Any]:
    """Build analytics pipeline based on type."""
    pipeline_configs = {
        "content": {"aggregation_class": "ContentAnalytics", "default_metrics": ["views", "engagement", "reach"]},
        "user": {"aggregation_class": "UserAnalytics", "default_metrics": ["activity", "retention", "growth"]},
        "collaboration": {"aggregation_class": "CollaborationAnalytics", "default_metrics": ["projects", "success_rate", "efficiency"]},
        "revenue": {"aggregation_class": "RevenueAnalytics", "default_metrics": ["earnings", "conversion", "growth"]}
    }
    
    config = pipeline_configs.get(analytics_type)
    if not config:
        return {"error": f"Unknown analytics type: {analytics_type}"}
    
    return {
        "analytics_type": analytics_type,
        "config": config,
        "available_modules": _loaded_modules,
        "build_status": "ready" if config["aggregation_class"] in globals() else "unavailable"
    }

# Module initialization complete
logger.info(f"MongoDB Aggregation Engine initialized - Version {__version__}")
if _failed_modules:
    logger.warning(f"Some aggregation modules failed to load: {[name for name, _ in _failed_modules]}")