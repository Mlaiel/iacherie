"""IA Influencer Agent - Event Sourcing Module

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
    
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.aggregate_type = self.__class__.__name__
        self.version = 0
        self.uncommitted_events: List[DomainEvent] = []
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get all uncommitted events"""
        return self.uncommitted_events.copy()
    
    def apply_event(self, event: DomainEvent):
        """Apply an event to the aggregate"""
        self._apply_event(event)
        self.version = event.event_version
        self.uncommitted_events.append(event)
    
    def mark_events_as_committed(self):
        """Mark all uncommitted events as committed"""
        self.uncommitted_events.clear()
    
    def _apply_event(self, event: DomainEvent):
        """Apply event to aggregate state - to be implemented by subclasses"""
        pass


class EventStore(EventStoreInterface):
    """Basic in-memory event store implementation"""
    
    def __init__(self):
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
    
    def __init__(self, event_store: EventStoreInterface):
        self.event_store = event_store
    
    async def save_aggregate(self, aggregate: AggregateRoot):
        """Save aggregate changes as events"""
        uncommitted_events = aggregate.get_uncommitted_events()
        if uncommitted_events:
            await self.event_store.save_events(
                aggregate.aggregate_id, 
                uncommitted_events, 
                aggregate.version
            )
            aggregate.mark_events_as_committed()
    
    async def get_aggregate(self, aggregate_id: str, aggregate_type):
        """Recreate aggregate from events"""
        events = await self.event_store.get_events(aggregate_id)
        
        aggregate = aggregate_type(aggregate_id)
        for event in events:
            aggregate.apply_event(event)
        
        aggregate.mark_events_as_committed()
        return aggregate


# Export classes for compatibility
__all__ = [
    'DomainEvent',
    'EventStoreInterface', 
    'EventStore',
    'EventRepository',
    'AggregateRoot'
]