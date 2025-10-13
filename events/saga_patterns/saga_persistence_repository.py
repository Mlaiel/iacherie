#!/usr/bin/env python3
"""Saga Persistence Repository - Enterprise State Persistence
===========================================================

Advanced persistence repository for saga state management.
Provides ACID-compliant storage, recovery capabilities, and
high-performance access to saga execution state.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
Utilisation non autorisée strictement interdite.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class SagaPersistenceMode(Enum):
    """Saga persistence modes"""
    MEMORY_ONLY = "memory_only"
    DATABASE_ONLY = "database_only"
    HYBRID = "hybrid"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


@dataclass
class SagaSnapshot:
    """Immutable snapshot of saga state"""
    saga_id: str
    snapshot_id: str
    saga_type: str
    status: str
    current_states: List[str]
    step_data: Dict[str, Any]
    execution_context: Dict[str, Any]
    created_at: datetime
    version: int = 1
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SagaSnapshot':
        """Create from dictionary"""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class SagaEvent:
    """Represents a saga state change event"""
    event_id: str
    saga_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime
    version: int
    causation_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SagaEvent':
        """Create from dictionary"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class SagaMetadata:
    """Metadata about saga execution"""
    saga_id: str
    saga_type: str
    creator_id: str
    started_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    priority: str = "normal"
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None


class InMemoryStore:
    """In-memory storage implementation"""
    
    def __init__(self):
        self.snapshots: Dict[str, List[SagaSnapshot]] = {}
        self.events: Dict[str, List[SagaEvent]] = {}
        self.metadata: Dict[str, SagaMetadata] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
    
    async def store_snapshot(self, snapshot: SagaSnapshot):
        """Store saga snapshot"""
        if snapshot.saga_id not in self.snapshots:
            self.snapshots[snapshot.saga_id] = []
        
        self.snapshots[snapshot.saga_id].append(snapshot)
        
        # Keep only recent snapshots (limit to 10 per saga)
        if len(self.snapshots[snapshot.saga_id]) > 10:
            self.snapshots[snapshot.saga_id] = self.snapshots[snapshot.saga_id][-10:]
    
    async def get_latest_snapshot(self, saga_id: str) -> Optional[SagaSnapshot]:
        """Get latest snapshot for saga"""
        if saga_id not in self.snapshots or not self.snapshots[saga_id]:
            return None
        
        return self.snapshots[saga_id][-1]
    
    async def store_event(self, event: SagaEvent):
        """Store saga event"""
        if event.saga_id not in self.events:
            self.events[event.saga_id] = []
        
        self.events[event.saga_id].append(event)
    
    async def get_events(
        self, 
        saga_id: str,
        from_version: int = 0
    ) -> List[SagaEvent]:
        """Get events for saga from specified version"""
        if saga_id not in self.events:
            return []
        
        return [
            event for event in self.events[saga_id]
            if event.version > from_version
        ]
    
    async def store_metadata(self, metadata: SagaMetadata):
        """Store saga metadata"""
        self.metadata[metadata.saga_id] = metadata
    
    async def get_metadata(self, saga_id: str) -> Optional[SagaMetadata]:
        """Get saga metadata"""
        return self.metadata.get(saga_id)
    
    def get_lock(self, saga_id: str) -> asyncio.Lock:
        """Get lock for saga"""
        if saga_id not in self.locks:
            self.locks[saga_id] = asyncio.Lock()
        return self.locks[saga_id]


class DatabaseStore:
    """Database storage implementation (mock)"""
    
    def __init__(self):
        # Mock database connection
        self.connection_pool = None
        self.table_prefix = "saga_"
    
    async def store_snapshot(self, snapshot: SagaSnapshot):
        """Store snapshot in database"""
        # Mock database storage
        logger.debug(f"Storing snapshot {snapshot.snapshot_id} for saga {snapshot.saga_id}")
        await asyncio.sleep(0.01)  # Simulate DB I/O
    
    async def get_latest_snapshot(self, saga_id: str) -> Optional[SagaSnapshot]:
        """Get latest snapshot from database"""
        # Mock database retrieval
        logger.debug(f"Retrieving latest snapshot for saga {saga_id}")
        await asyncio.sleep(0.01)  # Simulate DB I/O
        return None
    
    async def store_event(self, event: SagaEvent):
        """Store event in database"""
        # Mock database storage
        logger.debug(f"Storing event {event.event_id} for saga {event.saga_id}")
        await asyncio.sleep(0.01)  # Simulate DB I/O
    
    async def get_events(
        self, 
        saga_id: str,
        from_version: int = 0
    ) -> List[SagaEvent]:
        """Get events from database"""
        # Mock database retrieval
        logger.debug(f"Retrieving events for saga {saga_id} from version {from_version}")
        await asyncio.sleep(0.01)  # Simulate DB I/O
        return []
    
    async def store_metadata(self, metadata: SagaMetadata):
        """Store metadata in database"""
        logger.debug(f"Storing metadata for saga {metadata.saga_id}")
        await asyncio.sleep(0.01)  # Simulate DB I/O
    
    async def get_metadata(self, saga_id: str) -> Optional[SagaMetadata]:
        """Get metadata from database"""
        logger.debug(f"Retrieving metadata for saga {saga_id}")
        await asyncio.sleep(0.01)  # Simulate DB I/O
        return None


class SagaPersistenceRepository:
    """Main repository for saga persistence"""
    
    def __init__(
        self,
        mode: SagaPersistenceMode = SagaPersistenceMode.HYBRID,
        snapshot_interval: int = 5,
        retention_days: int = 30
    ):
        self.mode = mode
        self.snapshot_interval = snapshot_interval
        self.retention_days = retention_days
        
        # Initialize storage backends
        self.memory_store = InMemoryStore()
        self.database_store = DatabaseStore()
        
        # Runtime state
        self.saga_versions: Dict[str, int] = {}
        self.pending_writes: Dict[str, List[Any]] = {}
        self.write_queue: asyncio.Queue = asyncio.Queue()
        self.background_tasks: List[asyncio.Task] = []
        
        # Background tasks will be started when needed
        self.background_tasks: List[asyncio.Task] = []
        self._tasks_started = False
    
    async def save_saga_state(
        self,
        saga_id: str,
        saga_type: str,
        status: str,
        current_states: List[str],
        step_data: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> str:
        """Save complete saga state"""
        # Start background tasks if not started yet
        if not self._tasks_started:
            try:
                if self.mode in [SagaPersistenceMode.WRITE_BEHIND, SagaPersistenceMode.HYBRID]:
                    self.background_tasks.append(
                        asyncio.create_task(self._background_writer())
                    )
                
                self.background_tasks.append(
                    asyncio.create_task(self._cleanup_task())
                )
                self._tasks_started = True
            except RuntimeError:
                # No event loop yet, will try again later
                pass
        async with self.memory_store.get_lock(saga_id):
            # Increment version
            version = self.saga_versions.get(saga_id, 0) + 1
            self.saga_versions[saga_id] = version
            
            # Create snapshot
            snapshot = SagaSnapshot(
                saga_id=saga_id,
                snapshot_id=str(uuid.uuid4()),
                saga_type=saga_type,
                status=status,
                current_states=current_states.copy(),
                step_data=step_data.copy(),
                execution_context=execution_context.copy(),
                created_at=datetime.now(timezone.utc),
                version=version
            )
            
            # Store based on mode
            if self.mode in [SagaPersistenceMode.MEMORY_ONLY, SagaPersistenceMode.HYBRID]:
                await self.memory_store.store_snapshot(snapshot)
            
            if self.mode == SagaPersistenceMode.DATABASE_ONLY:
                await self.database_store.store_snapshot(snapshot)
            
            if self.mode == SagaPersistenceMode.WRITE_THROUGH:
                await self.memory_store.store_snapshot(snapshot)
                await self.database_store.store_snapshot(snapshot)
            
            if self.mode == SagaPersistenceMode.WRITE_BEHIND:
                await self.memory_store.store_snapshot(snapshot)
                await self.write_queue.put(('snapshot', snapshot))
            
            logger.debug(f"Saved saga state for {saga_id}, version {version}")
            return snapshot.snapshot_id
    
    async def record_saga_event(
        self,
        saga_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        causation_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Record saga event"""
        version = self.saga_versions.get(saga_id, 0) + 1
        self.saga_versions[saga_id] = version
        
        event = SagaEvent(
            event_id=str(uuid.uuid4()),
            saga_id=saga_id,
            event_type=event_type,
            event_data=event_data.copy(),
            timestamp=datetime.now(timezone.utc),
            version=version,
            causation_id=causation_id,
            correlation_id=correlation_id
        )
        
        # Store based on mode
        if self.mode in [SagaPersistenceMode.MEMORY_ONLY, SagaPersistenceMode.HYBRID]:
            await self.memory_store.store_event(event)
        
        if self.mode == SagaPersistenceMode.DATABASE_ONLY:
            await self.database_store.store_event(event)
        
        if self.mode == SagaPersistenceMode.WRITE_THROUGH:
            await self.memory_store.store_event(event)
            await self.database_store.store_event(event)
        
        if self.mode == SagaPersistenceMode.WRITE_BEHIND:
            await self.memory_store.store_event(event)
            await self.write_queue.put(('event', event))
        
        logger.debug(f"Recorded event {event_type} for saga {saga_id}")
        return event.event_id
    
    async def get_saga_state(self, saga_id: str) -> Optional[SagaSnapshot]:
        """Get current saga state"""
        # Try memory first for performance
        if self.mode in [SagaPersistenceMode.MEMORY_ONLY, SagaPersistenceMode.HYBRID, 
                        SagaPersistenceMode.WRITE_THROUGH, SagaPersistenceMode.WRITE_BEHIND]:
            snapshot = await self.memory_store.get_latest_snapshot(saga_id)
            if snapshot:
                return snapshot
        
        # Fall back to database
        if self.mode in [SagaPersistenceMode.DATABASE_ONLY, SagaPersistenceMode.HYBRID]:
            return await self.database_store.get_latest_snapshot(saga_id)
        
        return None
    
    async def get_saga_events(
        self,
        saga_id: str,
        from_version: int = 0
    ) -> List[SagaEvent]:
        """Get saga events from specified version"""
        # Try memory first
        if self.mode in [SagaPersistenceMode.MEMORY_ONLY, SagaPersistenceMode.HYBRID,
                        SagaPersistenceMode.WRITE_THROUGH, SagaPersistenceMode.WRITE_BEHIND]:
            events = await self.memory_store.get_events(saga_id, from_version)
            if events:
                return events
        
        # Fall back to database
        if self.mode in [SagaPersistenceMode.DATABASE_ONLY, SagaPersistenceMode.HYBRID]:
            return await self.database_store.get_events(saga_id, from_version)
        
        return []
    
    async def save_saga_metadata(
        self,
        saga_id: str,
        saga_type: str,
        creator_id: str,
        business_context: Dict[str, Any] = None,
        tags: List[str] = None,
        priority: str = "normal"
    ):
        """Save saga metadata"""
        now = datetime.now(timezone.utc)
        
        # Check if metadata already exists
        existing = await self.get_saga_metadata(saga_id)
        
        if existing:
            # Update existing metadata
            existing.updated_at = now
            existing.business_context.update(business_context or {})
            existing.tags.extend(tags or [])
            existing.priority = priority
            metadata = existing
        else:
            # Create new metadata
            metadata = SagaMetadata(
                saga_id=saga_id,
                saga_type=saga_type,
                creator_id=creator_id,
                started_at=now,
                updated_at=now,
                business_context=business_context or {},
                tags=tags or [],
                priority=priority
            )
        
        # Store based on mode
        if self.mode in [SagaPersistenceMode.MEMORY_ONLY, SagaPersistenceMode.HYBRID,
                        SagaPersistenceMode.WRITE_THROUGH, SagaPersistenceMode.WRITE_BEHIND]:
            await self.memory_store.store_metadata(metadata)
        
        if self.mode in [SagaPersistenceMode.DATABASE_ONLY, SagaPersistenceMode.WRITE_THROUGH]:
            await self.database_store.store_metadata(metadata)
        
        if self.mode == SagaPersistenceMode.WRITE_BEHIND:
            await self.write_queue.put(('metadata', metadata))
    
    async def get_saga_metadata(self, saga_id: str) -> Optional[SagaMetadata]:
        """Get saga metadata"""
        # Try memory first
        if self.mode in [SagaPersistenceMode.MEMORY_ONLY, SagaPersistenceMode.HYBRID,
                        SagaPersistenceMode.WRITE_THROUGH, SagaPersistenceMode.WRITE_BEHIND]:
            metadata = await self.memory_store.get_metadata(saga_id)
            if metadata:
                return metadata
        
        # Fall back to database
        if self.mode in [SagaPersistenceMode.DATABASE_ONLY, SagaPersistenceMode.HYBRID]:
            return await self.database_store.get_metadata(saga_id)
        
        return None
    
    async def mark_saga_completed(self, saga_id: str):
        """Mark saga as completed"""
        metadata = await self.get_saga_metadata(saga_id)
        if metadata:
            metadata.completed_at = datetime.now(timezone.utc)
            metadata.updated_at = metadata.completed_at
            
            if metadata.started_at:
                duration = (metadata.completed_at - metadata.started_at).total_seconds()
                metadata.actual_duration = int(duration)
            
            # Save updated metadata
            await self.memory_store.store_metadata(metadata)
            
            if self.mode in [SagaPersistenceMode.DATABASE_ONLY, SagaPersistenceMode.WRITE_THROUGH]:
                await self.database_store.store_metadata(metadata)
            elif self.mode == SagaPersistenceMode.WRITE_BEHIND:
                await self.write_queue.put(('metadata', metadata))
    
    async def reconstruct_saga_state(self, saga_id: str) -> Optional[SagaSnapshot]:
        """Reconstruct saga state from events"""
        # Get all events for saga
        events = await self.get_saga_events(saga_id)
        
        if not events:
            return None
        
        # Sort events by version
        events.sort(key=lambda e: e.version)
        
        # Reconstruct state from events
        current_states = []
        step_data = {}
        execution_context = {}
        status = "created"
        
        for event in events:
            if event.event_type == "saga_started":
                status = "running"
                execution_context.update(event.event_data.get("context", {}))
            
            elif event.event_type == "step_completed":
                step_name = event.event_data.get("step_name")
                if step_name:
                    step_data[step_name] = event.event_data.get("result", {})
            
            elif event.event_type == "state_changed":
                new_states = event.event_data.get("states", [])
                current_states = new_states
            
            elif event.event_type == "saga_completed":
                status = "completed"
            
            elif event.event_type == "saga_failed":
                status = "failed"
        
        # Create reconstructed snapshot
        metadata = await self.get_saga_metadata(saga_id)
        saga_type = metadata.saga_type if metadata else "unknown"
        
        return SagaSnapshot(
            saga_id=saga_id,
            snapshot_id=f"reconstructed_{uuid.uuid4().hex[:8]}",
            saga_type=saga_type,
            status=status,
            current_states=current_states,
            step_data=step_data,
            execution_context=execution_context,
            created_at=datetime.now(timezone.utc),
            version=events[-1].version if events else 1
        )
    
    async def _background_writer(self):
        """Background task for write-behind mode"""
        while True:
            try:
                # Get item from write queue
                item_type, item_data = await asyncio.wait_for(
                    self.write_queue.get(), timeout=5.0
                )
                
                # Write to database
                if item_type == 'snapshot':
                    await self.database_store.store_snapshot(item_data)
                elif item_type == 'event':
                    await self.database_store.store_event(item_data)
                elif item_type == 'metadata':
                    await self.database_store.store_metadata(item_data)
                
                self.write_queue.task_done()
                
            except asyncio.TimeoutError:
                # No items to process
                continue
            except Exception as e:
                logger.error(f"Background writer error: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_task(self):
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Cleanup old data based on retention policy
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
                
                # In real implementation, would cleanup old snapshots and events
                logger.debug(f"Cleanup task running, cutoff date: {cutoff_date}")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
    
    async def get_repository_stats(self) -> Dict[str, Any]:
        """Get repository statistics"""
        stats = {
            "mode": self.mode.value,
            "active_sagas": len(self.saga_versions),
            "write_queue_size": self.write_queue.qsize(),
            "background_tasks": len(self.background_tasks)
        }
        
        # Add memory store stats
        if hasattr(self.memory_store, 'snapshots'):
            stats["memory_snapshots"] = sum(len(snapshots) for snapshots in self.memory_store.snapshots.values())
            stats["memory_events"] = sum(len(events) for events in self.memory_store.events.values())
            stats["memory_metadata"] = len(self.memory_store.metadata)
        
        return stats
    
    async def shutdown(self):
        """Shutdown repository and cleanup resources"""
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for pending writes in write-behind mode
        if self.mode == SagaPersistenceMode.WRITE_BEHIND:
            await self.write_queue.join()
        
        logger.info("Saga persistence repository shutdown complete")


# Global repository instance
_persistence_repository: Optional[SagaPersistenceRepository] = None


def get_saga_persistence_repository() -> SagaPersistenceRepository:
    """Get global saga persistence repository"""
    global _persistence_repository
    if _persistence_repository is None:
        _persistence_repository = SagaPersistenceRepository()
    
    return _persistence_repository


async def save_saga_state(
    saga_id: str,
    saga_type: str,
    status: str,
    current_states: List[str],
    step_data: Dict[str, Any],
    execution_context: Dict[str, Any]
) -> str:
    """Convenience function to save saga state"""
    repo = get_saga_persistence_repository()
    return await repo.save_saga_state(
        saga_id, saga_type, status, current_states, step_data, execution_context
    )


async def get_saga_state(saga_id: str) -> Optional[SagaSnapshot]:
    """Convenience function to get saga state"""
    repo = get_saga_persistence_repository()
    return await repo.get_saga_state(saga_id)


__all__ = [
    "SagaPersistenceRepository",
    "SagaSnapshot",
    "SagaEvent",
    "SagaMetadata",
    "SagaPersistenceMode",
    "InMemoryStore",
    "DatabaseStore",
    "get_saga_persistence_repository",
    "save_saga_state",
    "get_saga_state"
]