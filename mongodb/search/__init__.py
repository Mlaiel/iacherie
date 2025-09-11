"""MongoDB Search Engine Module
=============================

Full-text search, content discovery, and search optimization for MongoDB.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Track loaded search modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    try:
        module = __import__(f"mongodb.search.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded search.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load search.{module_name}: {e}")
        return False

# Import search modules
_safe_import('text_search_engine')
_safe_import('search_indexer')
_safe_import('faceted_search')
_safe_import('autocomplete_engine')
_safe_import('search_analytics')
_safe_import('relevance_tuner')
_safe_import('search_suggester')

__all__ = [
    'TextSearchEngine', 'SearchIndexer', 'FacetedSearch', 'AutocompleteEngine',
    'SearchAnalytics', 'RelevanceTuner', 'SearchSuggester',
    'get_text_search_engine', 'get_search_indexer', 'get_autocomplete_engine'
]

logger.info(f"MongoDB Search Engine module initialized - Version {__version__}")