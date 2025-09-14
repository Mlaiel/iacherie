"""IA Influencer Agent - Event Sourcing Module

import asyncio

Enterprise-grade event sourcing implementation for the IA Influencer Agent Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    """Base domain event for event sourcing"""
    
    event_id: str
    aggregate_id: str
    aggregate_type: str
    event_type: str
    event_data: Dict[str, Any]
    event_version: int
    occurred_at: datetime


class EventStoreInterface(ABC):
    """Interface for event store implementations"""
    
    @abstractmethod
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], 
                         expected_version: int = None) -> None:
        """Save events to the store"""
        pass

    @abstractmethod
    async def get_events(self, aggregate_id: str, 
                        from_version: int = 0) -> List[DomainEvent]:
        """Get events for an aggregate"""
        pass

    @abstractmethod  
    async def get_all_events(self, from_event_id: str = None, 
                           limit: int = 100) -> List[DomainEvent]:
        """Get all events with optional pagination"""
        pass


class AggregateRoot:
    """Base class for all aggregates in event sourcing"""
    
    def __init__(self, aggregate_id -> None: str) -> None:
        self.aggregate_id = aggregate_id
        self.aggregate_type = self.__class__.__name__
        self.version = 0
        self.uncommitted_events: List[DomainEvent] = []
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get all uncommitted events"""
        return self.uncommitted_events.copy()
    
    def apply_event(self, event -> None: DomainEvent) -> None:
        """Apply an event to the aggregate"""
        self._apply_event(event)
        self.version = event.event_version
        self.uncommitted_events.append(event)
    
    def mark_events_as_committed(self) -> None:
        """Mark all uncommitted events as committed"""
        self.uncommitted_events.clear()
    
    def _apply_event(self, event -> None: DomainEvent) -> None:
        """Apply event to aggregate state - to be implemented by subclasses"""
        pass


class EventStore(EventStoreInterface):
    """Basic in-memory event store implementation"""
    
    def __init__(self) -> None:
        self.events: Dict[str, List[DomainEvent]] = {}
    
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], 
                         expected_version: int = None) -> None:
        """Save events to the store"""
        if aggregate_id not in self.events:
            self.events[aggregate_id] = []
        
        self.events[aggregate_id].extend(events)
    
    async def get_events(self, aggregate_id: str, 
                        from_version: int = 0) -> List[DomainEvent]:
        """Get events for an aggregate"""
        if aggregate_id not in self.events:
            return []
        
        return [e for e in self.events[aggregate_id] if e.event_version >= from_version]
    
    async def get_all_events(self, from_event_id: str = None, 
                           limit: int = 100) -> List[DomainEvent]:
        """Get all events with optional pagination"""
        all_events = []
        for events in self.events.values():
            all_events.extend(events)
        
        # Sort by occurred_at
        all_events.sort(key=lambda x: x.occurred_at)
        
        return all_events[:limit]


class EventRepository:
    """Repository for managing aggregates with event sourcing"""
    
    def __init__(self, event_store -> None: EventStoreInterface) -> None:
        self.event_store = event_store
    
    async def save_aggregate(self, aggregate -> None: AggregateRoot) -> None:
        """Save aggregate changes as events"""
        uncommitted_events = aggregate.get_uncommitted_events()
        if uncommitted_events:
            await self.event_store.save_events(
                aggregate.aggregate_id, 
                uncommitted_events, 
                aggregate.version
            )
            aggregate.mark_events_as_committed()
    
    async def get_aggregate(self, aggregate_id -> None: str, aggregate_type) -> None:
        """Recreate aggregate from events"""
        events = await self.event_store.get_events(aggregate_id)
        
        aggregate = aggregate_type(aggregate_id)
        for event in events:
            aggregate.apply_event(event)
        
        aggregate.mark_events_as_committed()
        return aggregate


# Import all enterprise classes
try:
    from .enterprise_event_store import (
        EnterpriseEventStore, StorageBackend, BackendConfig, 
        PostgreSQLAdapter, MongoDBAdapter, EventStoreMetrics
    )
except ImportError as e:
    logger.warning(f"Failed to import enterprise_event_store: {e}")
    EnterpriseEventStore = None

try:
    from .postgresql_event_repository import (
        PostgreSQLEventRepository, PostgreSQLConfig, PartitionStrategy, 
        IndexStrategy, QueryMetrics
    )
except ImportError as e:
    logger.warning(f"Failed to import postgresql_event_repository: {e}")
    PostgreSQLEventRepository = None

try:
    from .mongodb_event_collection import (
        MongoDBEventCollection, MongoDBConfig, ShardingStrategy, 
        CompressionLevel, MongoDBMetrics
    )
except ImportError as e:
    logger.warning(f"Failed to import mongodb_event_collection: {e}")
    MongoDBEventCollection = None

try:
    from .aggregate_snapshot_manager import (
        AggregateSnapshotManager, SnapshotConfig, SnapshotStrategy,
        SnapshotMetadata, SnapshotData, MemorySnapshotStorage,
        FileSystemSnapshotStorage
    )
except ImportError as e:
    logger.warning(f"Failed to import aggregate_snapshot_manager: {e}")
    AggregateSnapshotManager = None

try:
    from .event_stream_processor import (
        EventStreamProcessor, StreamConfig, StreamingBackend,
        ProcessingMode, EventFilter, EventTransformer, EventBatch
    )
except ImportError as e:
    logger.warning(f"Failed to import event_stream_processor: {e}")
    EventStreamProcessor = None

try:
    from .event_versioning_engine import (
        EventVersioningEngine, SemanticVersion, EventSchema,
        VersionType, CompatibilityLevel, SchemaChange, MigrationRule
    )
except ImportError as e:
    logger.warning(f"Failed to import event_versioning_engine: {e}")
    EventVersioningEngine = None

try:
    from .event_migration_orchestrator import (
        EventMigrationOrchestrator, MigrationConfig, MigrationStatus,
        MigrationStrategy, MigrationProgress, ConflictResolution
    )
except ImportError as e:
    logger.warning(f"Failed to import event_migration_orchestrator: {e}")
    EventMigrationOrchestrator = None

try:
    from .consistency_validation_service import (
        ConsistencyValidationService, ValidationRule, ValidationIssue,
        ValidationReport, ValidationSeverity, ValidationCategory
    )
except ImportError as e:
    logger.warning(f"Failed to import consistency_validation_service: {e}")
    ConsistencyValidationService = None

try:
    from .optimistic_concurrency_manager import (
        OptimisticConcurrencyManager, ConflictInfo, ConflictType,
        ConflictResolutionStrategy, LockInfo, LockType, ConcurrencyMetrics
    )
except ImportError as e:
    logger.warning(f"Failed to import optimistic_concurrency_manager: {e}")
    OptimisticConcurrencyManager = None

try:
    from .event_compaction_optimizer import (
        EventCompactionOptimizer, CompactionRule, CompactionStrategy,
        CompactionJob, CompactionMetrics, ArchivalTier
    )
except ImportError as e:
    logger.warning(f"Failed to import event_compaction_optimizer: {e}")
    EventCompactionOptimizer = None

try:
    from .projection_rebuild_coordinator import (
        ProjectionRebuildCoordinator, ProjectionDefinition, ProjectionType,
        RebuildStrategy, RebuildJob, ProjectionHandler, ProjectionMetrics
    )
except ImportError as e:
    logger.warning(f"Failed to import projection_rebuild_coordinator: {e}")
    ProjectionRebuildCoordinator = None

# Export classes for compatibility
__all__ = [
    # Core classes
    'DomainEvent',
    'EventStoreInterface', 
    'EventStore',
    'EventRepository',
    'AggregateRoot',
    
    # Enterprise Event Store
    'EnterpriseEventStore',
    'StorageBackend',
    'BackendConfig',
    'PostgreSQLAdapter',
    'MongoDBAdapter',
    'EventStoreMetrics',
    
    # PostgreSQL Repository
    'PostgreSQLEventRepository',
    'PostgreSQLConfig',
    'PartitionStrategy',
    'IndexStrategy',
    'QueryMetrics',
    
    # MongoDB Collection
    'MongoDBEventCollection',
    'MongoDBConfig',
    'ShardingStrategy',
    'CompressionLevel',
    'MongoDBMetrics',
    
    # Snapshot Manager
    'AggregateSnapshotManager',
    'SnapshotConfig',
    'SnapshotStrategy',
    'SnapshotMetadata',
    'SnapshotData',
    'MemorySnapshotStorage',
    'FileSystemSnapshotStorage',
    
    # Stream Processor
    'EventStreamProcessor',
    'StreamConfig',
    'StreamingBackend',
    'ProcessingMode',
    'EventFilter',
    'EventTransformer',
    'EventBatch',
    
    # Versioning Engine
    'EventVersioningEngine',
    'SemanticVersion',
    'EventSchema',
    'VersionType',
    'CompatibilityLevel',
    'SchemaChange',
    'MigrationRule',
    
    # Migration Orchestrator
    'EventMigrationOrchestrator',
    'MigrationConfig',
    'MigrationStatus',
    'MigrationStrategy',
    'MigrationProgress',
    'ConflictResolution',
    
    # Consistency Validation
    'ConsistencyValidationService',
    'ValidationRule',
    'ValidationIssue',
    'ValidationReport',
    'ValidationSeverity',
    'ValidationCategory',
    
    # Concurrency Manager
    'OptimisticConcurrencyManager',
    'ConflictInfo',
    'ConflictType',
    'ConflictResolutionStrategy',
    'LockInfo',
    'LockType',
    'ConcurrencyMetrics',
    
    # Compaction Optimizer
    'EventCompactionOptimizer',
    'CompactionRule',
    'CompactionStrategy',
    'CompactionJob',
    'CompactionMetrics',
    'ArchivalTier',
    
    # Projection Coordinator
    'ProjectionRebuildCoordinator',
    'ProjectionDefinition',
    'ProjectionType',
    'RebuildStrategy',
    'RebuildJob',
    'ProjectionHandler',
    'ProjectionMetrics'
]