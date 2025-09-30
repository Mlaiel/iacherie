"""Ainflue Core Infrastructure - Event Sourcing Core
=================================================

Enterprise-grade event sourcing implementation providing event store management,
aggregate reconstruction, event streaming, snapshots, and CQRS pattern support
for maintaining complete audit trail and system state in the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Type, Generic, TypeVar, Union
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import threading
import copy
from collections import defaultdict

# Setup logger
logger = logging.getLogger(__name__)

T = TypeVar('T')  # For generic types

class EventType(str, Enum):
    """Event types"""
    DOMAIN = "domain"
    SYSTEM = "system"
    INTEGRATION = "integration"
    AUDIT = "audit"
    NOTIFICATION = "notification"

class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    REPLAYING = "replaying"

@dataclass
class Event:
    """Base event class"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    aggregate_type: str = ""
    event_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    status: EventStatus = EventStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'aggregate_id': self.aggregate_id,
            'aggregate_type': self.aggregate_type,
            'event_type': self.event_type,
            'event_data': self.event_data,
            'metadata': self.metadata,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'user_id': self.user_id,
            'status': self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        event = cls()
        event.id = data.get('id', event.id)
        event.aggregate_id = data.get('aggregate_id', '')
        event.aggregate_type = data.get('aggregate_type', '')
        event.event_type = data.get('event_type', '')
        event.event_data = data.get('event_data', {})
        event.metadata = data.get('metadata', {})
        event.version = data.get('version', 1)
        event.timestamp = datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.utcnow()
        event.correlation_id = data.get('correlation_id')
        event.causation_id = data.get('causation_id')
        event.user_id = data.get('user_id')
        event.status = EventStatus(data.get('status', EventStatus.PENDING.value))
        return event

@dataclass
class Snapshot:
    """Aggregate snapshot"""
    aggregate_id: str
    aggregate_type: str
    version: int
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary"""
        return {
            'aggregate_id': self.aggregate_id,
            'aggregate_type': self.aggregate_type,
            'version': self.version,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Snapshot':
        """Create snapshot from dictionary"""
        return cls(
            aggregate_id=data['aggregate_id'],
            aggregate_type=data['aggregate_type'],
            version=data['version'],
            data=data['data'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )

class AggregateRoot(ABC, Generic[T]):
    """Base aggregate root class"""
    
    def __init__(self, aggregate_id: str):
        self.id = aggregate_id
        self.version = 0
        self.uncommitted_events: List[Event] = []
        self.applied_events: List[Event] = []
    
    @abstractmethod
    def apply_event(self, event: Event):
        """Apply event to aggregate"""
        pass
    
    def raise_event(self, event_type: str, event_data: Dict[str, Any], 
                   metadata: Optional[Dict[str, Any]] = None):
        """Raise new domain event"""
        event = Event(
            aggregate_id=self.id,
            aggregate_type=self.__class__.__name__,
            event_type=event_type,
            event_data=event_data,
            metadata=metadata or {},
            version=self.version + 1
        )
        self.uncommitted_events.append(event)
    
    def mark_events_as_committed(self):
        """Mark uncommitted events as committed"""
        self.applied_events.extend(self.uncommitted_events)
        self.uncommitted_events.clear()
    
    def load_from_history(self, events: List[Event]):
        """Load aggregate from event history"""
        for event in events:
            self.apply_event(event)
            self.version = event.version
        self.mark_events_as_committed()
    
    def get_uncommitted_events(self) -> List[Event]:
        """Get uncommitted events"""
        return self.uncommitted_events.copy()
    
    def create_snapshot(self) -> Dict[str, Any]:
        """Create aggregate snapshot data"""
        return {
            'id': self.id,
            'version': self.version,
            'state': self.__dict__.copy()
        }
    
    def load_from_snapshot(self, snapshot_data: Dict[str, Any]):
        """Load aggregate from snapshot"""
        self.version = snapshot_data['version']
        state = snapshot_data.get('state', {})
        for key, value in state.items():
            if key not in ['uncommitted_events', 'applied_events']:
                setattr(self, key, value)

class EventStore:
    """In-memory event store implementation"""
    
    def __init__(self):
        self.events: Dict[str, List[Event]] = defaultdict(list)
        self.snapshots: Dict[str, Snapshot] = {}
        self.global_events: List[Event] = []
        self.subscribers: Dict[str, List[callable]] = defaultdict(list)
        self.lock = threading.Lock()
        self.next_sequence = 1
    
    def append_events(self, aggregate_id: str, events: List[Event], 
                     expected_version: int = -1) -> bool:
        """Append events to aggregate stream"""
        try:
            with self.lock:
                current_events = self.events[aggregate_id]
                current_version = len(current_events)
                
                # Check optimistic concurrency
                if expected_version >= 0 and current_version != expected_version:
                    raise Exception(f"Concurrency conflict: expected version {expected_version}, got {current_version}")
                
                # Append events
                for i, event in enumerate(events):
                    event.version = current_version + i + 1
                    event.status = EventStatus.PROCESSED
                    current_events.append(event)
                    self.global_events.append(event)
                    
                    # Notify subscribers
                    self._notify_subscribers(event)
                
                logger.debug(f"Appended {len(events)} events to aggregate {aggregate_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to append events: {str(e)}")
            return False
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for aggregate"""
        with self.lock:
            events = self.events.get(aggregate_id, [])
            return [e for e in events if e.version > from_version]
    
    def get_all_events(self, from_sequence: int = 0) -> List[Event]:
        """Get all events from sequence number"""
        with self.lock:
            return self.global_events[from_sequence:]
    
    def save_snapshot(self, snapshot: Snapshot) -> bool:
        """Save aggregate snapshot"""
        try:
            with self.lock:
                key = f"{snapshot.aggregate_type}:{snapshot.aggregate_id}"
                self.snapshots[key] = snapshot
                logger.debug(f"Saved snapshot for {key} at version {snapshot.version}")
                return True
        except Exception as e:
            logger.error(f"Failed to save snapshot: {str(e)}")
            return False
    
    def get_snapshot(self, aggregate_id: str, aggregate_type: str) -> Optional[Snapshot]:
        """Get latest snapshot for aggregate"""
        with self.lock:
            key = f"{aggregate_type}:{aggregate_id}"
            return self.snapshots.get(key)
    
    def subscribe(self, event_type: str, handler: callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: callable):
        """Unsubscribe from event type"""
        if handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
    
    def _notify_subscribers(self, event: Event):
        """Notify event subscribers"""
        for handler in self.subscribers.get(event.event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(event))
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Subscriber error for event {event.id}: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event store statistics"""
        with self.lock:
            return {
                'total_aggregates': len(self.events),
                'total_events': len(self.global_events),
                'total_snapshots': len(self.snapshots),
                'total_subscribers': sum(len(handlers) for handlers in self.subscribers.values()),
                'aggregate_stats': {
                    aggregate_id: len(events) 
                    for aggregate_id, events in self.events.items()
                }
            }

class Repository(ABC, Generic[T]):
    """Abstract repository for aggregates"""
    
    def __init__(self, event_store: EventStore, aggregate_type: Type[T]):
        self.event_store = event_store
        self.aggregate_type = aggregate_type
        self.snapshot_frequency = 10  # Take snapshot every 10 events
    
    @abstractmethod
    def create_aggregate(self, aggregate_id: str) -> T:
        """Create new aggregate instance"""
        pass
    
    async def get_by_id(self, aggregate_id: str) -> Optional[T]:
        """Get aggregate by ID"""
        try:
            # Try to load from snapshot first
            snapshot = self.event_store.get_snapshot(aggregate_id, self.aggregate_type.__name__)
            
            if snapshot:
                aggregate = self.create_aggregate(aggregate_id)
                aggregate.load_from_snapshot(snapshot.data)
                
                # Load events after snapshot
                events = self.event_store.get_events(aggregate_id, snapshot.version)
                aggregate.load_from_history(events)
            else:
                # Load from full event history
                events = self.event_store.get_events(aggregate_id)
                if not events:
                    return None
                
                aggregate = self.create_aggregate(aggregate_id)
                aggregate.load_from_history(events)
            
            return aggregate
            
        except Exception as e:
            logger.error(f"Failed to get aggregate {aggregate_id}: {str(e)}")
            return None
    
    async def save(self, aggregate: T, expected_version: int = -1) -> bool:
        """Save aggregate changes"""
        try:
            uncommitted_events = aggregate.get_uncommitted_events()
            if not uncommitted_events:
                return True
            
            # Save events
            success = self.event_store.append_events(
                aggregate.id, uncommitted_events, expected_version
            )
            
            if success:
                aggregate.mark_events_as_committed()
                
                # Check if snapshot is needed
                if aggregate.version % self.snapshot_frequency == 0:
                    await self._create_snapshot(aggregate)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to save aggregate {aggregate.id}: {str(e)}")
            return False
    
    async def _create_snapshot(self, aggregate: T):
        """Create and save snapshot"""
        try:
            snapshot_data = aggregate.create_snapshot()
            snapshot = Snapshot(
                aggregate_id=aggregate.id,
                aggregate_type=self.aggregate_type.__name__,
                version=aggregate.version,
                data=snapshot_data
            )
            self.event_store.save_snapshot(snapshot)
            logger.debug(f"Created snapshot for aggregate {aggregate.id} at version {aggregate.version}")
        except Exception as e:
            logger.error(f"Failed to create snapshot: {str(e)}")

class EventProjection(ABC):
    """Abstract event projection"""
    
    def __init__(self, name: str):
        self.name = name
        self.last_processed_version = 0
        self.is_rebuilding = False
    
    @abstractmethod
    async def handle_event(self, event: Event):
        """Handle event for projection"""
        pass
    
    @abstractmethod
    async def reset(self):
        """Reset projection state"""
        pass
    
    async def rebuild(self, events: List[Event]):
        """Rebuild projection from events"""
        try:
            self.is_rebuilding = True
            await self.reset()
            
            for event in events:
                await self.handle_event(event)
                self.last_processed_version = event.version
            
            self.is_rebuilding = False
            logger.info(f"Rebuilt projection {self.name} with {len(events)} events")
            
        except Exception as e:
            logger.error(f"Failed to rebuild projection {self.name}: {str(e)}")
            self.is_rebuilding = False

class EventSourcingCore:
    """Core event sourcing management system"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.event_store = EventStore()
        self.repositories: Dict[str, Repository] = {}
        self.projections: Dict[str, EventProjection] = {}
        self.event_handlers: Dict[str, List[callable]] = defaultdict(list)
        self.is_running = False
        self.projection_tasks: Dict[str, asyncio.Task] = {}
        self.metrics = {
            'events_processed': 0,
            'projections_updated': 0,
            'start_time': datetime.utcnow()
        }
        
        logger.info(f"Event Sourcing Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize event sourcing system"""
        try:
            # Setup default event handlers
            self.event_store.subscribe("*", self._handle_global_event)
            
            logger.info("Event Sourcing Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Event Sourcing Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start event sourcing system"""
        try:
            self.is_running = True
            
            # Start projection processors
            for projection_name, projection in self.projections.items():
                if projection_name not in self.projection_tasks:
                    self.projection_tasks[projection_name] = asyncio.create_task(
                        self._projection_processor(projection)
                    )
            
            logger.info("Event Sourcing Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Event Sourcing Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop event sourcing system"""
        try:
            self.is_running = False
            
            # Cancel projection tasks
            for task in self.projection_tasks.values():
                task.cancel()
            
            if self.projection_tasks:
                await asyncio.gather(*self.projection_tasks.values(), return_exceptions=True)
            
            self.projection_tasks.clear()
            logger.info("Event Sourcing Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Event Sourcing Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check event store responsiveness
            stats = self.event_store.get_stats()
            
            # Check if projections are running
            active_projections = len([
                task for task in self.projection_tasks.values() 
                if not task.done()
            ])
            
            if active_projections != len(self.projections):
                logger.warning("Some projections are not running")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def register_repository(self, name: str, repository: Repository):
        """Register aggregate repository"""
        self.repositories[name] = repository
        logger.info(f"Registered repository: {name}")
    
    def register_projection(self, projection: EventProjection):
        """Register event projection"""
        self.projections[projection.name] = projection
        logger.info(f"Registered projection: {projection.name}")
    
    def register_event_handler(self, event_type: str, handler: callable):
        """Register event handler"""
        self.event_handlers[event_type].append(handler)
        self.event_store.subscribe(event_type, handler)
        logger.info(f"Registered event handler for: {event_type}")
    
    def get_repository(self, name: str) -> Optional[Repository]:
        """Get repository by name"""
        return self.repositories.get(name)
    
    def get_projection(self, name: str) -> Optional[EventProjection]:
        """Get projection by name"""
        return self.projections.get(name)
    
    async def replay_events(self, projection_name: str, from_sequence: int = 0) -> bool:
        """Replay events for specific projection"""
        try:
            projection = self.projections.get(projection_name)
            if not projection:
                return False
            
            events = self.event_store.get_all_events(from_sequence)
            await projection.rebuild(events)
            
            logger.info(f"Replayed {len(events)} events for projection {projection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to replay events for {projection_name}: {str(e)}")
            return False
    
    async def _handle_global_event(self, event: Event):
        """Handle global event processing"""
        try:
            self.metrics['events_processed'] += 1
            
            # Process event handlers
            for handler in self.event_handlers.get(event.event_type, []):
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Global event handling error: {str(e)}")
    
    async def _projection_processor(self, projection: EventProjection):
        """Process events for projection"""
        while self.is_running:
            try:
                # Get new events for projection
                all_events = self.event_store.get_all_events()
                new_events = [
                    e for e in all_events 
                    if e.version > projection.last_processed_version
                ]
                
                for event in new_events:
                    await projection.handle_event(event)
                    projection.last_processed_version = event.version
                    self.metrics['projections_updated'] += 1
                
                await asyncio.sleep(1)  # Process every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Projection processor error for {projection.name}: {str(e)}")
                await asyncio.sleep(5)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
        event_store_stats = self.event_store.get_stats()
        
        return {
            'level': self.level,
            'uptime_seconds': uptime,
            'events_processed': self.metrics['events_processed'],
            'projections_updated': self.metrics['projections_updated'],
            'active_repositories': len(self.repositories),
            'active_projections': len(self.projections),
            'event_store_stats': event_store_stats,
            'projection_health': {
                name: not projection.is_rebuilding 
                for name, projection in self.projections.items()
            }
        }

# Global instance
event_sourcing_core = EventSourcingCore()

# Convenience functions
def get_repository(name: str) -> Optional[Repository]:
    """Get repository by name"""
    return event_sourcing_core.get_repository(name)

def get_projection(name: str) -> Optional[EventProjection]:
    """Get projection by name"""
    return event_sourcing_core.get_projection(name)

async def replay_projection(name: str, from_sequence: int = 0) -> bool:
    """Replay events for projection"""
    return await event_sourcing_core.replay_events(name, from_sequence)

# Module exports
__all__ = [
    "EventSourcingCore", "Event", "Snapshot", "AggregateRoot", "EventStore",
    "Repository", "EventProjection", "EventType", "EventStatus",
    "event_sourcing_core", "get_repository", "get_projection", "replay_projection"
]

logger.info("Event Sourcing Core module loaded")