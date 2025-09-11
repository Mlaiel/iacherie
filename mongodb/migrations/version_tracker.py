"""Version Tracker for MongoDB Migrations
======================================

Database version tracking and migration history management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VersionInfo:
    """Database version information."""
    version: str
    applied_at: datetime
    applied_by: str
    migration_count: int
    checksum: str

class VersionTracker:
    """Database version tracking system."""
    
    def __init__(self):
        """Initialize version tracker."""
        self._version_history: List[VersionInfo] = []
        self._current_version = "0.0.0"
    
    def record_version(self, version: str, applied_by: str, migration_count: int, checksum: str):
        """Record a new database version."""
        version_info = VersionInfo(
            version=version,
            applied_at=datetime.utcnow(),
            applied_by=applied_by,
            migration_count=migration_count,
            checksum=checksum
        )
        
        self._version_history.append(version_info)
        self._current_version = version
        
        logger.info(f"Recorded database version: {version}")
    
    def get_current_version(self) -> str:
        """Get current database version."""
        return self._current_version
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get complete version history."""
        return [
            {
                "version": v.version,
                "applied_at": v.applied_at.isoformat(),
                "applied_by": v.applied_by,
                "migration_count": v.migration_count,
                "checksum": v.checksum
            }
            for v in self._version_history
        ]

_default_tracker: Optional[VersionTracker] = None

def get_version_tracker() -> VersionTracker:
    global _default_tracker
    if _default_tracker is None:
        _default_tracker = VersionTracker()
    return _default_tracker

__all__ = ['VersionInfo', 'VersionTracker', 'get_version_tracker']