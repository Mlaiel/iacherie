"""MongoDB Performance Optimization Module
=======================================

Query optimization, caching, connection pooling, and performance monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Track loaded performance modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    try:
        module = __import__(f"mongodb.performance.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded performance.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load performance.{module_name}: {e}")
        return False

# Import performance modules
_safe_import('query_optimizer')
_safe_import('cache_manager')
_safe_import('connection_pooling')
_safe_import('read_preference')
_safe_import('write_concern')
_safe_import('slow_query_analyzer')
_safe_import('performance_profiler')

__all__ = [
    'QueryOptimizer', 'CacheManager', 'ConnectionPooling', 'ReadPreference',
    'WriteConcern', 'SlowQueryAnalyzer', 'PerformanceProfiler',
    'get_query_optimizer', 'get_cache_manager', 'get_performance_profiler'
]

logger.info(f"MongoDB Performance Optimization module initialized - Version {__version__}")