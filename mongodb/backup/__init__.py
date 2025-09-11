"""MongoDB Backup Module
======================

Automated backup, restore, and disaster recovery for MongoDB.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"

# Track loaded backup modules
_loaded_modules = []
_failed_modules = []

def _safe_import(module_name: str) -> bool:
    try:
        module = __import__(f"mongodb.backup.{module_name}", fromlist=[module_name])
        globals().update(getattr(module, '__dict__', {}))
        _loaded_modules.append(module_name)
        logger.info(f"Successfully loaded backup.{module_name}")
        return True
    except Exception as e:
        _failed_modules.append((module_name, str(e)))
        logger.warning(f"Failed to load backup.{module_name}: {e}")
        return False

# Import backup modules
_safe_import('backup_scheduler')
_safe_import('restore_manager')
_safe_import('incremental_backup')
_safe_import('cloud_backup')
_safe_import('backup_validator')
_safe_import('retention_policy')
_safe_import('point_in_time_recovery')

__all__ = [
    'BackupScheduler', 'RestoreManager', 'IncrementalBackup', 'CloudBackup',
    'BackupValidator', 'RetentionPolicy', 'PointInTimeRecovery',
    'get_backup_scheduler', 'get_restore_manager', 'get_cloud_backup'
]

logger.info(f"MongoDB Backup module initialized - Version {__version__}")