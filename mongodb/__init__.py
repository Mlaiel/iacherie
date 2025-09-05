"""MongoDB Module for Ainflue Platform
=====================================

Advanced MongoDB integration module providing comprehensive database management,
connection pooling, indexing, and monitoring capabilities for the Ainflue
Influencer Agent platform.

This module provides:
- Asynchronous MongoDB connection management
- Collection management and indexing utilities
- Health monitoring and performance tracking
- Security and authentication handling
- Data validation and schema management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel (mlaiel@live.de)
- Database Architecture Specialist: Fahed Mlaiel (mlaiel@live.de)
- MongoDB Expert: Fahed Mlaiel (mlaiel@live.de)
- Backend Systems Engineer: Fahed Mlaiel (mlaiel@live.de)
- Security Specialist: Fahed Mlaiel (mlaiel@live.de)
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

# Track loaded submodules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    """Safely import a module with error handling."""
    try:
        module = __import__(f"mongodb.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded mongodb.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load mongodb.{module_name}: {e}")
        return False

# Import core MongoDB modules
_safe_import('connection')
_safe_import('collections')
_safe_import('indexing')
_safe_import('monitoring')
_safe_import('models')

# Export public interface
__all__ = [
    # Core classes (will be available after successful imports)
    'MongoDBConnection',
    'MongoDBCollectionManager', 
    'MongoDBIndexManager',
    'MongoDBMonitor',
    'MongoDBModels',
    
    # Utility functions
    'get_connection',
    'get_collection_manager',
    'get_index_manager',
    'get_monitor',
    
    # Module info
    '__version__',
    '__author__',
    '__email__',
    'get_loaded_modules',
    'get_failed_modules'
]

def get_loaded_modules() -> list:
    """Get list of successfully loaded modules."""
    return _loaded_modules.copy()

def get_failed_modules() -> list:
    """Get list of modules that failed to load."""
    return _failed_modules.copy()

# Module initialization complete
logger.info(f"MongoDB module initialized - Version {__version__}")
if _failed_modules:
    logger.warning(f"Some modules failed to load: {[name for name, _ in _failed_modules]}")