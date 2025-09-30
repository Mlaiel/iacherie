"""MongoDB Data Synchronization Module
===================================

Real-time data synchronization and change streams management for MongoDB
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel - Intelligent sync algorithms and conflict resolution
- Backend Senior Engineer: Infrastructure robuste temps réel et performance enterprise
- ML Engineer: Algorithmes prediction patterns et sync optimization
- DBA: Optimisation change streams et gestion oplog avancée
- Security Specialist: Chiffrement sync et audit trails complets
- Microservices Architect: Architecture distribuée event-driven
- DevOps Engineer: Monitoring sync temps réel et orchestration
"""

import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SyncDirection(Enum):
    """Data synchronization directions."""
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"

class SyncStatus(Enum):
    """Synchronization status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"
    INITIALIZING = "initializing"

class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    LATEST_WINS = "latest_wins"
    SOURCE_WINS = "source_wins"
    TARGET_WINS = "target_wins"
    MANUAL = "manual"
    MERGE = "merge"

@dataclass
class SyncConfiguration:
    """Synchronization configuration."""
    sync_id: str
    source_connection: str
    target_connection: str
    direction: SyncDirection
    collections: List[str]
    conflict_resolution: ConflictResolution
    batch_size: int
    sync_interval_seconds: int
    filters: Dict[str, Any]
    transformations: List[Dict[str, Any]]

@dataclass
class SyncEvent:
    """Synchronization event information."""
    event_id: str
    sync_id: str
    operation_type: str
    collection: str
    document_id: Any
    timestamp: datetime
    data: Dict[str, Any]
    status: str
    error_message: Optional[str] = None

# Export classes and functions
__all__ = [
    'SyncDirection',
    'SyncStatus', 
    'ConflictResolution',
    'SyncConfiguration',
    'SyncEvent',
    'ChangeStreamManager',
    'EventProcessor',
    'SyncCoordinator',
    'ConflictResolver',
    'WebhookDispatcher',
    'BatchProcessor',
    'RealtimeUpdater'
]

# Module initialization
logger.info("MongoDB Sync module initialized - Real-time synchronization ready")