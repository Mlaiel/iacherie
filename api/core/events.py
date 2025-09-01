"""Enterprise-grade event handling system for IA Influencer Agent.
Implements professional event sourcing and domain events patterns.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 IA Influencer Agent. Unauthorized use strictly prohibited.
"""

from typing import Any, Dict, List, Optional, Type, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import asyncio
import threading
import json
import uuid
from contextlib import asynccontextmanager


class EventPriority(Enum):
    """
Event priority levels for processing order."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventStatus(Enum):
    """
Event processing status tracking."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class DomainEvent:
    """Base domain event with enterprise-grade metadata."""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default="")
    aggregate_id: str = field(default="")
    aggregate_type: str = field(default="")
    event_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = field(default=1)
    priority: EventPriority = field(default=EventPriority.NORMAL)
    correlation_id: Optional[str] = field(default=None)
    causation_id: Optional[str] = field(default=None)
    user_id: Optional[str] = field(default=None)
    tenant_id: Optional[str] = field(default=None)
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "event_data": self.event_data,
            "metadata": self.metadata,
            "occurred_at": self.occurred_at.isoformat(),
            "version": self.version,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from dictionary."""
        occurred_at = datetime.fromisoformat(data.get("occurred_at", datetime.now(timezone.utc).isoformat()))
        priority = EventPriority(data.get("priority", EventPriority.NORMAL.value))
        
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=data.get("event_type", ""),
            aggregate_id=data.get("aggregate_id", ""),
            aggregate_type=data.get("aggregate_type", ""),
            event_data=data.get("event_data", {}),
            metadata=data.get("metadata", {}),
            occurred_at=occurred_at,
            version=data.get("version", 1),
            priority=priority,
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            user_id=data.get("user_id"),
            tenant_id=data.get("tenant_id")
        )


class IEventHandler(ABC):
    """Interface for event handlers."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> bool:
        """
Handle domain event. Return True if successful."""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """
Check if handler can process event type."""
        pass


class IEventStore(ABC):
    """
Interface for event store implementation."""
    
    @abstractmethod
    async def append_event(self, event: DomainEvent) -> bool:
        """
Append event to store."""
        pass
    
    @abstractmethod
    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 1,
        to_version: Optional[int] = None
    ) -> List[DomainEvent]:
        """
Get events for aggregate."""
        pass
    
    @abstractmethod
    async def get_events_by_type(
        self,
        event_type: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[DomainEvent]:
        """
Get events by type and date range."""
        pass


class InMemoryEventStore(IEventStore):
    """
In-memory event store for development/testing."""
    
    def __init__(self):
        self._events: List[DomainEvent] = []
        self._lock = threading.RLock()
    
    async def append_event(self, event: DomainEvent) -> bool:
        """
Append event to in-memory store."""
        with self._lock:
            self._events.append(event)
            return True
    
    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 1,
        to_version: Optional[int] = None
    ) -> List[DomainEvent]:
        """
Get events for aggregate from memory."""
        with self._lock:
            events = [
                e for e in self._events
                if e.aggregate_id == aggregate_id and e.version >= from_version
            ]
            
            if to_version:
                events = [e for e in events if e.version <= to_version]
            
            return sorted(events, key=lambda x: x.version)
    
    async def get_events_by_type(
        self,
        event_type: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[DomainEvent]:
        """
Get events by type from memory."""
        with self._lock:
            events = [e for e in self._events if e.event_type == event_type]
            
            if from_date:
                events = [e for e in events if e.occurred_at >= from_date]
            
            if to_date:
                events = [e for e in events if e.occurred_at <= to_date]
            
            return sorted(events, key=lambda x: x.occurred_at)


@dataclass
class EventSubscription:
    """
Event subscription configuration."""
    handler: IEventHandler
    event_types: List[str]
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 3
    timeout_seconds: int = 30


class EventBus:
    """
Professional event bus implementation with async support."""
    
    def __init__(self, event_store: Optional[IEventStore] = None):
        self._handlers: Dict[str, List[EventSubscription]] = {}
        self._global_handlers: List[EventSubscription] = []
        self._event_store = event_store or InMemoryEventStore()
        self._lock = threading.RLock()
        self._processing_queue = asyncio.Queue()
        self._is_running = False
        
    async def start(self):
        """
Start event processing."""
        if self._is_running:
            return
        
        self._is_running = True
        asyncio.create_task(self._process_events())
    
    async def stop(self):
        """
Stop event processing."""
        self._is_running = False
    
    def subscribe(
        self,
        handler: IEventHandler,
        event_types: List[str],
        priority: EventPriority = EventPriority.NORMAL,
        retry_count: int = 3,
        timeout_seconds: int = 30
    ):
        """
Subscribe handler to specific event types."""
        subscription = EventSubscription(
            handler=handler,
            event_types=event_types,
            priority=priority,
            retry_count=retry_count,
            timeout_seconds=timeout_seconds
        )
        
        with self._lock:
            for event_type in event_types:
                if event_type not in self._handlers:
                    self._handlers[event_type] = []
                self._handlers[event_type].append(subscription)
                # Sort by priority
                self._handlers[event_type].sort(key=lambda x: x.priority.value, reverse=True)
    
    def subscribe_global(
        self,
        handler: IEventHandler,
        priority: EventPriority = EventPriority.NORMAL,
        retry_count: int = 3,
        timeout_seconds: int = 30
    ):
        """
Subscribe handler to all events."""
        subscription = EventSubscription(
            handler=handler,
            event_types=["*"],
            priority=priority,
            retry_count=retry_count,
            timeout_seconds=timeout_seconds
        )
        
        with self._lock:
            self._global_handlers.append(subscription)
            self._global_handlers.sort(key=lambda x: x.priority.value, reverse=True)
    
    async def publish(self, event: DomainEvent) -> bool:
        """Publish event to subscribers."""
        # Store event
        await self._event_store.append_event(event)
        
        # Queue for processing
        await self._processing_queue.put(event)
        
        return True
    
    async def _process_events(self):
        """
Background event processing loop."""
        while self._is_running:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(
                    self._processing_queue.get(),
                    timeout=1.0
                )
                
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                # Log error but continue processing
                print(f"Event processing error: {e}")
    
    async def _handle_event(self, event: DomainEvent):
        """Handle single event with all subscribed handlers."""
        handlers_to_run = []
        
        # Get specific handlers
        with self._lock:
            if event.event_type in self._handlers:
                handlers_to_run.extend(self._handlers[event.event_type])
            
            # Add global handlers
            handlers_to_run.extend(self._global_handlers)
        
        # Execute handlers in priority order
        handlers_to_run.sort(key=lambda x: x.priority.value, reverse=True)
        
        for subscription in handlers_to_run:
            if subscription.handler.can_handle(event.event_type):
                await self._execute_handler(subscription, event)
    
    async def _execute_handler(self, subscription: EventSubscription, event: DomainEvent):
        """
Execute handler with retry logic and timeout."""
        retry_count = 0
        max_retries = subscription.retry_count
        
        while retry_count <= max_retries:
            try:
                # Execute with timeout
                success = await asyncio.wait_for(
                    subscription.handler.handle(event),
                    timeout=subscription.timeout_seconds
                )
                
                if success:
                    return
                
            except asyncio.TimeoutError:
                print(f"Handler timeout for event {event.event_type}")
            except Exception as e:
                print(f"Handler error for event {event.event_type}: {e}")
            
            retry_count += 1
            if retry_count <= max_retries:
                # Exponential backoff
                await asyncio.sleep(2 ** retry_count)
    
    def get_subscriptions(self) -> Dict[str, List[EventSubscription]]:
        """Get all subscriptions for debugging."""
        with self._lock:
            return self._handlers.copy()


# Content Protection Domain Events
@dataclass
class ContentUploadedEvent(DomainEvent):
    """
Event raised when content is uploaded."""
    
    def __init__(
        self,
        content_id: str,
        user_id: str,
        content_type: str,
        file_path: str,
        file_size: int,
        **kwargs
    ):
        super().__init__(
            aggregate_id=content_id,
            aggregate_type="Content",
            event_data={
                "content_id": content_id,
                "content_type": content_type,
                "file_path": file_path,
                "file_size": file_size
            },
            user_id=user_id,
            **kwargs
        )


@dataclass
class FingerprintGeneratedEvent(DomainEvent):
    """Event raised when content fingerprint is generated."""
    
    def __init__(
        self,
        content_id: str,
        fingerprint_hash: str,
        fingerprint_type: str,
        confidence_score: float,
        **kwargs
    ):
        super().__init__(
            aggregate_id=content_id,
            aggregate_type="Content",
            event_data={
                "content_id": content_id,
                "fingerprint_hash": fingerprint_hash,
                "fingerprint_type": fingerprint_type,
                "confidence_score": confidence_score
            },
            **kwargs
        )


@dataclass
class ContentProtectedEvent(DomainEvent):
    """Event raised when content protection is activated."""
    
    def __init__(
        self,
        content_id: str,
        protection_type: str,
        protection_settings: Dict[str, Any],
        **kwargs
    ):
        super().__init__(
            aggregate_id=content_id,
            aggregate_type="Content",
            event_data={
                "content_id": content_id,
                "protection_type": protection_type,
                "protection_settings": protection_settings
            },
            **kwargs
        )


@dataclass
class InfringementDetectedEvent(DomainEvent):
    """Event raised when content infringement is detected."""
    
    def __init__(
        self,
        content_id: str,
        infringement_url: str,
        platform: str,
        similarity_score: float,
        **kwargs
    ):
        super().__init__(
            aggregate_id=content_id,
            aggregate_type="Content",
            event_data={
                "content_id": content_id,
                "infringement_url": infringement_url,
                "platform": platform,
                "similarity_score": similarity_score
            },
            priority=EventPriority.HIGH,
            **kwargs
        )


@dataclass
class RevenueGeneratedEvent(DomainEvent):
    """Event raised when revenue is generated from protected content."""
    
    def __init__(
        self,
        content_id: str,
        amount: float,
        currency: str,
        platform: str,
        revenue_type: str,
        **kwargs
    ):
        super().__init__(
            aggregate_id=content_id,
            aggregate_type="Content",
            event_data={
                "content_id": content_id,
                "amount": amount,
                "currency": currency,
                "platform": platform,
                "revenue_type": revenue_type
            },
            **kwargs
        )


# Global event bus instance
_event_bus: Optional[EventBus] = None
_event_bus_lock = threading.RLock()


async def get_event_bus(event_store: Optional[IEventStore] = None) -> EventBus:
    """Get global event bus instance."""
    global _event_bus
    
    with _event_bus_lock:
        if _event_bus is None:
            _event_bus = EventBus(event_store)
            await _event_bus.start()
        
        return _event_bus


async def publish_event(event: DomainEvent) -> bool:
    """
Publish event to global event bus."""
    bus = await get_event_bus()
    return await bus.publish(event)


def event_handler(event_types: List[str], priority: EventPriority = EventPriority.NORMAL):
    """
Decorator to register event handler."""
    def decorator(cls: Type[IEventHandler]) -> Type[IEventHandler]:
        # Store registration info for later use
        cls._event_types = event_types
        cls._event_priority = priority
        return cls
    return decorator
