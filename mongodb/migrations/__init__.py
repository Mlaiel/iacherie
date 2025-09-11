"""MongoDB Migration System for Ainflue Platform
=============================================

Database schema migrations, version management, and data transformation
with rollback capabilities and compatibility checking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTED:
- DBA: Database schema migration and version control
- DevOps: Automated migration deployment and rollback
- Backend Senior: Data transformation and compatibility
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

# Track loaded migration modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    """Safely import a migration module with error handling."""
    try:
        module = __import__(f"mongodb.migrations.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded migrations.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load migrations.{module_name}: {e}")
        return False

# Import migration modules
_safe_import('migration_manager')
_safe_import('schema_validator')
_safe_import('data_transformer')
_safe_import('rollback_manager')
_safe_import('version_tracker')
_safe_import('migration_templates')
_safe_import('testing_framework')

# Export public interface
__all__ = [
    # Core migration classes
    'MigrationManager',
    'SchemaValidator',
    'DataTransformer',
    'RollbackManager',
    'VersionTracker',
    'MigrationTemplates',
    'TestingFramework',
    
    # Utility functions
    'get_migration_manager',
    'get_schema_validator',
    'get_version_tracker',
    'create_migration',
    'apply_migration',
    'rollback_migration',
    
    # Module info
    '__version__',
    '__author__',
    'get_loaded_migration_modules',
    'get_failed_migration_modules'
]

def get_loaded_migration_modules() -> list:
    """Get list of successfully loaded migration modules."""
    return _loaded_modules.copy()

def get_failed_migration_modules() -> list:
    """Get list of migration modules that failed to load."""
    return _failed_modules.copy()

def create_migration(name: str, migration_type: str = "schema") -> Dict[str, Any]:
    """Create new migration template."""
    migration_templates = {
        "schema": {"type": "schema_change", "requires_downtime": False},
        "data": {"type": "data_transformation", "requires_downtime": True},
        "index": {"type": "index_management", "requires_downtime": False},
        "collection": {"type": "collection_management", "requires_downtime": True}
    }
    
    template = migration_templates.get(migration_type, migration_templates["schema"])
    
    return {
        "migration_name": name,
        "migration_type": migration_type,
        "template": template,
        "available_modules": _loaded_modules,
        "status": "ready" if "MigrationManager" in globals() else "unavailable"
    }

# Module initialization complete
logger.info(f"MongoDB Migration System initialized - Version {__version__}")
if _failed_modules:
    logger.warning(f"Some migration modules failed to load: {[name for name, _ in _failed_modules]}")