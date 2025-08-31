"""IA Influencer Agent - Event Sourcing Module
Enterprise-grade Event Sourcing Implementation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. See __init__.py for full notice.
"""
from typing import Dict, Any, List, Optional, Type, Union, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from uuid import uuid4, UUID
import json
import asyncio
import logging
from enum import Enum

from ..core.exceptions import EventSourcingError
from ..core.database import DatabaseManager
from ..utils.serialization import JsonEncoder, JsonDecoder
from ..security.encryption import EncryptionManager

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
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid4())
        if not self.occurred_at:
            self.occurred_at = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}


class EventStoreInterface(ABC):
    """Interface for event store implementations"""    
    @abstractmethod
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], 
                         expected_version: int) -> None:
        """Save events to the store"""        pass
    
    @abstractmethod
    async def get_events(self, aggregate_id: str, 
                        from_version: int = 0) -> List[DomainEvent]:
        """Retrieve events for an aggregate"""        pass
    
    @abstractmethod
    async def get_all_events(self, from_event_id: str = None, 
                           limit: int = 1000) -> List[DomainEvent]:
        """Retrieve all events with optional pagination"""        pass


class PostgreSQLEventStore(EventStoreInterface):
    """PostgreSQL implementation of event store"""    
    def __init__(self, db_manager: DatabaseManager, 
                 encryption_manager: EncryptionManager):
        self.db = db_manager
        self.encryption = encryption_manager
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Create event store tables if they don't exist"""        create_events_table = """        CREATE TABLE IF NOT EXISTS event_store (
            event_id UUID PRIMARY KEY,
            aggregate_id VARCHAR(255) NOT NULL,
            aggregate_type VARCHAR(100) NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            event_version INTEGER NOT NULL,
            occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
            user_id VARCHAR(255),
            correlation_id VARCHAR(255),
            causation_id VARCHAR(255),
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(aggregate_id, event_version)
        );
        
        CREATE INDEX IF NOT EXISTS idx_event_store_aggregate_id 
            ON event_store(aggregate_id);
        CREATE INDEX IF NOT EXISTS idx_event_store_occurred_at 
            ON event_store(occurred_at);
        CREATE INDEX IF NOT EXISTS idx_event_store_event_type 
            ON event_store(event_type);
        """        
        asyncio.create_task(self.db.execute(create_events_table))
    
    async def save_events(self, aggregate_id: str, events: List[DomainEvent], 
                         expected_version: int) -> None:
        """Save events with optimistic concurrency control"""        try:
            async with self.db.transaction():
                # Check current version
                current_version_query = """                SELECT COALESCE(MAX(event_version), 0) as current_version
                FROM event_store WHERE aggregate_id = $1
                """                result = await self.db.fetch_one(current_version_query, aggregate_id)
                current_version = result["current_version"] if result else 0
                
                if current_version != expected_version:
                    raise EventSourcingError(
                        f"Concurrency conflict: expected version {expected_version}, "
                        f"but current version is {current_version}"
                    )
                
                # Insert events
                for event in events:
                    # Encrypt sensitive data
                    encrypted_data = await self.encryption.encrypt_data(
                        json.dumps(event.event_data, cls=JsonEncoder)
                    )
                    
                    insert_query = """                    INSERT INTO event_store (
                        event_id, aggregate_id, aggregate_type, event_type,
                        event_data, event_version, occurred_at, user_id,
                        correlation_id, causation_id, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """                    
                    await self.db.execute(
                        insert_query,
                        UUID(event.event_id), event.aggregate_id, 
                        event.aggregate_type, event.event_type,
                        encrypted_data, event.event_version,
                        event.occurred_at, event.user_id,
                        event.correlation_id, event.causation_id,
                        json.dumps(event.metadata or {})
                    )
                
                logger.info(f"Saved {len(events)} events for aggregate {aggregate_id}")
                
        except Exception as e:
            logger.error(f"Error saving events: {str(e)}")
            raise EventSourcingError(f"Failed to save events: {str(e)}")
    
    async def get_events(self, aggregate_id: str, 
                        from_version: int = 0) -> List[DomainEvent]:
        """Retrieve and decrypt events for an aggregate"""        try:
            query = """            SELECT event_id, aggregate_id, aggregate_type, event_type,
                   event_data, event_version, occurred_at, user_id,
                   correlation_id, causation_id, metadata
            FROM event_store 
            WHERE aggregate_id = $1 AND event_version > $2
            ORDER BY event_version
            """            
            rows = await self.db.fetch_all(query, aggregate_id, from_version)
            events = []
            
            for row in rows:
                # Decrypt event data
                decrypted_data = await self.encryption.decrypt_data(
                    row["event_data"]
                )
                event_data = json.loads(decrypted_data, cls=JsonDecoder)
                
                event = DomainEvent(
                    event_id=str(row["event_id"]),
                    aggregate_id=row["aggregate_id"],
                    aggregate_type=row["aggregate_type"],
                    event_type=row["event_type"],
                    event_data=event_data,
                    event_version=row["event_version"],
                    occurred_at=row["occurred_at"],
                    user_id=row["user_id"],
                    correlation_id=row["correlation_id"],
                    causation_id=row["causation_id"],
                    metadata=json.loads(row["metadata"] or "{}")
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving events: {str(e)}")
            raise EventSourcingError(f"Failed to retrieve events: {str(e)}")
    
    async def get_all_events(self, from_event_id: str = None, 
                           limit: int = 1000) -> List[DomainEvent]:
        """Retrieve all events with pagination"""        try:
            if from_event_id:
                query = """                SELECT event_id, aggregate_id, aggregate_type, event_type,
                       event_data, event_version, occurred_at, user_id,
                       correlation_id, causation_id, metadata
                FROM event_store 
                WHERE occurred_at > (
                    SELECT occurred_at FROM event_store WHERE event_id = $1
                )
                ORDER BY occurred_at
                LIMIT $2
                """                rows = await self.db.fetch_all(query, UUID(from_event_id), limit)
            else:
                query = """                SELECT event_id, aggregate_id, aggregate_type, event_type,
                       event_data, event_version, occurred_at, user_id,
                       correlation_id, causation_id, metadata
                FROM event_store 
                ORDER BY occurred_at
                LIMIT $1
                """                rows = await self.db.fetch_all(query, limit)
            
            events = []
            for row in rows:
                decrypted_data = await self.encryption.decrypt_data(
                    row["event_data"]
                )
                event_data = json.loads(decrypted_data, cls=JsonDecoder)
                
                event = DomainEvent(
                    event_id=str(row["event_id"]),
                    aggregate_id=row["aggregate_id"],
                    aggregate_type=row["aggregate_type"],
                    event_type=row["event_type"],
                    event_data=event_data,
                    event_version=row["event_version"],
                    occurred_at=row["occurred_at"],
                    user_id=row["user_id"],
                    correlation_id=row["correlation_id"],
                    causation_id=row["causation_id"],
                    metadata=json.loads(row["metadata"] or "{}")
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving all events: {str(e)}")
            raise EventSourcingError(f"Failed to retrieve all events: {str(e)}")


class AggregateRoot(ABC):
    """Base class for aggregate roots in event sourcing"""    
    def __init__(self, aggregate_id: str = None):
        self.aggregate_id = aggregate_id or str(uuid4())
        self.version = 0
        self.uncommitted_events: List[DomainEvent] = []
    
    def mark_events_as_committed(self):
        """Mark all uncommitted events as committed"""        self.uncommitted_events.clear()
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get all uncommitted events"""        return self.uncommitted_events.copy()
    
    def apply_event(self, event: DomainEvent):
        """Apply an event to the aggregate"""        self._apply_event(event)
        self.version = event.event_version
    
    def raise_event(self, event_type: str, event_data: Dict[str, Any], 
                   user_id: str = None, correlation_id: str = None):
        """Raise a new domain event"""        event = DomainEvent(
            event_id=str(uuid4()),
            aggregate_id=self.aggregate_id,
            aggregate_type=self.__class__.__name__,
            event_type=event_type,
            event_data=event_data,
            event_version=self.version + 1,
            occurred_at=datetime.now(timezone.utc),
            user_id=user_id,
            correlation_id=correlation_id
        )
        
        self.apply_event(event)
        self.uncommitted_events.append(event)
    
    @abstractmethod
    def _apply_event(self, event: DomainEvent):
        """Apply event to aggregate state (to be implemented by subclasses)"""        pass


class EventRepository:
    """Repository for loading and saving aggregates"""    
    def __init__(self, event_store: EventStoreInterface):
        self.event_store = event_store
    
    async def save(self, aggregate: AggregateRoot):
        """Save aggregate by persisting uncommitted events"""        uncommitted_events = aggregate.get_uncommitted_events()
        if not uncommitted_events:
            return
        
        expected_version = aggregate.version - len(uncommitted_events)
        await self.event_store.save_events(
            aggregate.aggregate_id, 
            uncommitted_events, 
            expected_version
        )
        aggregate.mark_events_as_committed()
    
    async def load(self, aggregate_type: Type[AggregateRoot], 
                  aggregate_id: str) -> Optional[AggregateRoot]:
        """Load aggregate by replaying events"""        events = await self.event_store.get_events(aggregate_id)
        if not events:
            return None
        
        aggregate = aggregate_type(aggregate_id)
        for event in events:
            aggregate.apply_event(event)
        
        aggregate.mark_events_as_committed()
        return aggregate


class SnapshotStore:
    """Store for aggregate snapshots to improve performance"""    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Create snapshot tables if they don't exist"""        create_snapshots_table = """        CREATE TABLE IF NOT EXISTS aggregate_snapshots (
            aggregate_id VARCHAR(255) PRIMARY KEY,
            aggregate_type VARCHAR(100) NOT NULL,
            aggregate_data JSONB NOT NULL,
            version INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_snapshots_type_version 
            ON aggregate_snapshots(aggregate_type, version);
        """        
        asyncio.create_task(self.db.execute(create_snapshots_table))
    
    async def save_snapshot(self, aggregate: AggregateRoot):
        """Save aggregate snapshot"""        try:
            # Serialize aggregate state
            aggregate_data = {
                "state": aggregate.__dict__,
                "class_name": aggregate.__class__.__name__
            }
            
            query = """            INSERT INTO aggregate_snapshots 
                (aggregate_id, aggregate_type, aggregate_data, version)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (aggregate_id) 
            DO UPDATE SET 
                aggregate_data = EXCLUDED.aggregate_data,
                version = EXCLUDED.version,
                created_at = NOW()
            """            
            await self.db.execute(
                query,
                aggregate.aggregate_id,
                aggregate.__class__.__name__,
                json.dumps(aggregate_data),
                aggregate.version
            )
            
            logger.info(f"Saved snapshot for aggregate {aggregate.aggregate_id}")
            
        except Exception as e:
            logger.error(f"Error saving snapshot: {str(e)}")
            raise EventSourcingError(f"Failed to save snapshot: {str(e)}")
    
    async def load_snapshot(self, aggregate_type: Type[AggregateRoot], 
                           aggregate_id: str) -> Optional[AggregateRoot]:
        """Load aggregate snapshot"""        try:
            query = """            SELECT aggregate_data, version 
            FROM aggregate_snapshots 
            WHERE aggregate_id = $1 AND aggregate_type = $2
            """            
            result = await self.db.fetch_one(
                query, aggregate_id, aggregate_type.__name__
            )
            
            if not result:
                return None
            
            aggregate_data = json.loads(result["aggregate_data"])
            aggregate = aggregate_type(aggregate_id)
            
            # Restore aggregate state
            for key, value in aggregate_data["state"].items():
                setattr(aggregate, key, value)
            
            return aggregate
            
        except Exception as e:
            logger.error(f"Error loading snapshot: {str(e)}")
            return None


class EventProjection(ABC):
    """Base class for event projections"""    
    @abstractmethod
    async def handle(self, event: DomainEvent):
        """Handle a domain event for projection"""        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if this projection can handle the event type"""        pass


class ProjectionManager:
    """Manages event projections"""    
    def __init__(self, event_store: EventStoreInterface):
        self.event_store = event_store
        self.projections: List[EventProjection] = []
        self.last_processed_event_id: Optional[str] = None
    
    def register_projection(self, projection: EventProjection):
        """Register a new projection"""        self.projections.append(projection)
    
    async def rebuild_projections(self):
        """Rebuild all projections from scratch"""        logger.info("Starting projection rebuild...")
        
        events = await self.event_store.get_all_events()
        
        for event in events:
            for projection in self.projections:
                if projection.can_handle(event.event_type):
                    await projection.handle(event)
            
            self.last_processed_event_id = event.event_id
        
        logger.info(f"Rebuilt {len(self.projections)} projections "
                   f"with {len(events)} events")
    
    async def process_new_events(self):
        """Process new events since last processed"""        events = await self.event_store.get_all_events(
            from_event_id=self.last_processed_event_id
        )
        
        for event in events:
            for projection in self.projections:
                if projection.can_handle(event.event_type):
                    await projection.handle(event)
            
            self.last_processed_event_id = event.event_id


# Export public API
__all__ = [
    "DomainEvent", "EventStoreInterface", "PostgreSQLEventStore",
    "AggregateRoot", "EventRepository", "SnapshotStore",
    "EventProjection", "ProjectionManager"
]
