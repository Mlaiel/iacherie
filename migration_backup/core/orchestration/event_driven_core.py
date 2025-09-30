"""
Ainflue Core Orchestration - Event Driven Core
===============================================

Enterprise-grade event-driven architecture system with event sourcing, CQRS integration,
event streaming, saga coordination, and distributed event processing capabilities.
Enables reactive and resilient system design patterns.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Event types in the system"""
    DOMAIN_EVENT = "domain_event"
    INTEGRATION_EVENT = "integration_event"
    SYSTEM_EVENT = "system_event"
    COMMAND_EVENT = "command_event"
    QUERY_EVENT = "query_event"

class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

@dataclass
class Event:
    """Base event structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    source: str = "ainflue-core"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

@dataclass
class EventHandler:
    """Event handler registration"""
    handler_id: str
    event_types: List[str]
    handler_func: Callable[[Event], Any]
    async_handler: bool = True
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    filter_conditions: Optional[Callable[[Event], bool]] = None
    priority: int = 0
    enabled: bool = True

@dataclass
class EventStream:
    """Event stream configuration"""
    stream_id: str
    stream_name: str
    event_types: List[str]
    retention_policy: Dict[str, Any] = field(default_factory=dict)
    partitioning_key: Optional[str] = None
    max_batch_size: int = 100
    flush_interval: int = 5000  # milliseconds

@dataclass
class EventSnapshot:
    """Event stream snapshot"""
    aggregate_id: str
    aggregate_type: str
    snapshot_data: Dict[str, Any]
    version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EventMetrics:
    """Event processing metrics"""
    events_published: int = 0
    events_processed: int = 0
    events_failed: int = 0
    events_retried: int = 0
    handlers_registered: int = 0
    streams_active: int = 0
    avg_processing_time: float = 0.0
    throughput_per_second: float = 0.0

class EventDrivenCore:
    """Enterprise event-driven architecture system"""
    
    def __init__(self, level: str = "enterprise"):
        """Initialize event-driven core"""
        self.level = level
        self.event_store: Dict[str, List[Event]] = defaultdict(list)
        self.handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self.streams: Dict[str, EventStream] = {}
        self.snapshots: Dict[str, EventSnapshot] = {}
        self.metrics = EventMetrics()
        
        # Event processing queues
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.dead_letter_queue: asyncio.Queue = asyncio.Queue()
        self.processing_tasks: List[asyncio.Task] = []
        
        # Configuration
        self.config = {
            "max_retry_attempts": 3,
            "retry_backoff_factor": 2,
            "dead_letter_ttl": 86400 * 7,  # 7 days
            "snapshot_frequency": 100,  # events
            "batch_processing_size": 50,
            "processing_timeout": 30,
            "enable_metrics": True
        }
        
        # Event processing state
        self.processing_stats: Dict[str, Any] = defaultdict(int)
        self.handler_errors: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Threading and concurrency
        self._shutdown_event = asyncio.Event()
        self._processing_lock = asyncio.Lock()
        
        # Start event processors
        self._start_event_processors()
        
        logger.info(f"🔄 Event Driven Core initialized - Level: {level}")

    def _start_event_processors(self):
        """Start background event processing tasks"""
        
        # Create event processing tasks
        for i in range(3):  # 3 concurrent processors
            task = asyncio.create_task(self._process_events())
            self.processing_tasks.append(task)
        
        # Dead letter processor
        dead_letter_task = asyncio.create_task(self._process_dead_letter_queue())
        self.processing_tasks.append(dead_letter_task)
        
        # Metrics collector
        if self.config["enable_metrics"]:
            metrics_task = asyncio.create_task(self._collect_metrics())
            self.processing_tasks.append(metrics_task)

    async def publish_event(self, event: Event):
        """Publish event to the event bus"""
        
        try:
            # Validate event
            if not event.event_type:
                raise ValueError("Event type is required")
            
            # Set metadata
            event.metadata.update({
                "published_at": datetime.utcnow().isoformat(),
                "publisher": "event_driven_core",
                "correlation_id": event.correlation_id or str(uuid.uuid4())
            })
            
            # Store event
            await self._store_event(event)
            
            # Queue for processing
            await self.event_queue.put(event)
            
            # Update metrics
            self.metrics.events_published += 1
            
            logger.debug(f"Published event {event.event_id} of type {event.event_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            raise

    async def _store_event(self, event: Event):
        """Store event in event store"""
        
        # Store by aggregate
        if event.aggregate_id:
            key = f"{event.aggregate_type}:{event.aggregate_id}"
            self.event_store[key].append(event)
            
            # Check if snapshot is needed
            event_count = len(self.event_store[key])
            if event_count % self.config["snapshot_frequency"] == 0:
                await self._create_snapshot(event.aggregate_id, event.aggregate_type)
        
        # Store by event type
        self.event_store[event.event_type].append(event)
        
        # Store in streams
        for stream in self.streams.values():
            if event.event_type in stream.event_types:
                stream_key = f"stream:{stream.stream_id}"
                self.event_store[stream_key].append(event)

    async def _create_snapshot(self, aggregate_id: str, aggregate_type: str):
        """Create aggregate snapshot"""
        
        try:
            # Get all events for aggregate
            key = f"{aggregate_type}:{aggregate_id}"
            events = self.event_store.get(key, [])
            
            if not events:
                return
            
            # Build aggregate state from events
            aggregate_state = await self._rebuild_aggregate_state(events)
            
            # Create snapshot
            snapshot = EventSnapshot(
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                snapshot_data=aggregate_state,
                version=len(events)
            )
            
            self.snapshots[f"{aggregate_type}:{aggregate_id}"] = snapshot
            
            logger.debug(f"Created snapshot for {aggregate_type}:{aggregate_id}")
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {str(e)}")

    async def _rebuild_aggregate_state(self, events: List[Event]) -> Dict[str, Any]:
        """Rebuild aggregate state from events"""
        
        # This is a simplified implementation
        # In a real system, this would use aggregate-specific logic
        state = {}
        
        for event in sorted(events, key=lambda e: e.timestamp):
            # Apply event to state
            state.update(event.event_data)
            state["version"] = event.version
            state["last_modified"] = event.timestamp.isoformat()
        
        return state

    async def register_handler(
        self,
        handler_id: str,
        event_types: List[str],
        handler_func: Callable[[Event], Any],
        async_handler: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
        filter_conditions: Optional[Callable[[Event], bool]] = None,
        priority: int = 0
    ) -> str:
        """Register event handler"""
        
        handler = EventHandler(
            handler_id=handler_id,
            event_types=event_types,
            handler_func=handler_func,
            async_handler=async_handler,
            retry_policy=retry_policy or {},
            filter_conditions=filter_conditions,
            priority=priority
        )
        
        # Register handler for each event type
        for event_type in event_types:
            self.handlers[event_type].append(handler)
            
            # Sort handlers by priority
            self.handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
        
        self.metrics.handlers_registered += 1
        
        logger.info(f"Registered handler {handler_id} for events: {event_types}")
        return handler_id

    async def unregister_handler(self, handler_id: str):
        """Unregister event handler"""
        
        removed_count = 0
        
        for event_type, handlers_list in self.handlers.items():
            handlers_to_keep = [h for h in handlers_list if h.handler_id != handler_id]
            removed = len(handlers_list) - len(handlers_to_keep)
            self.handlers[event_type] = handlers_to_keep
            removed_count += removed
        
        if removed_count > 0:
            self.metrics.handlers_registered -= 1
            logger.info(f"Unregistered handler {handler_id}")

    async def _process_events(self):
        """Process events from the queue"""
        
        while not self._shutdown_event.is_set():
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {str(e)}")

    async def _handle_event(self, event: Event):
        """Handle single event"""
        
        start_time = time.time()
        
        try:
            # Get handlers for event type
            handlers = self.handlers.get(event.event_type, [])
            
            if not handlers:
                logger.debug(f"No handlers found for event type: {event.event_type}")
                return
            
            # Process handlers
            for handler in handlers:
                if not handler.enabled:
                    continue
                
                # Check filter conditions
                if handler.filter_conditions and not handler.filter_conditions(event):
                    continue
                
                # Execute handler
                await self._execute_handler(handler, event)
            
            # Update metrics
            self.metrics.events_processed += 1
            processing_time = time.time() - start_time
            self._update_processing_time(processing_time)
            
        except Exception as e:
            logger.error(f"Failed to handle event {event.event_id}: {str(e)}")
            self.metrics.events_failed += 1
            
            # Send to dead letter queue
            await self.dead_letter_queue.put({
                "event": event,
                "error": str(e),
                "timestamp": datetime.utcnow(),
                "attempts": 1
            })

    async def _execute_handler(self, handler: EventHandler, event: Event):
        """Execute event handler with retry logic"""
        
        max_attempts = handler.retry_policy.get("max_attempts", self.config["max_retry_attempts"])
        backoff_factor = handler.retry_policy.get("backoff_factor", self.config["retry_backoff_factor"])
        
        for attempt in range(max_attempts):
            try:
                # Execute handler
                if handler.async_handler:
                    if asyncio.iscoroutinefunction(handler.handler_func):
                        await handler.handler_func(event)
                    else:
                        # Run sync function in thread pool
                        await asyncio.get_event_loop().run_in_executor(
                            None, handler.handler_func, event
                        )
                else:
                    handler.handler_func(event)
                
                # Success - no retry needed
                return
                
            except Exception as e:
                logger.warning(f"Handler {handler.handler_id} failed (attempt {attempt + 1}): {str(e)}")
                
                # Record error
                self.handler_errors[handler.handler_id].append({
                    "error": str(e),
                    "event_id": event.event_id,
                    "timestamp": datetime.utcnow(),
                    "attempt": attempt + 1
                })
                
                # Keep only recent errors (last 100)
                if len(self.handler_errors[handler.handler_id]) > 100:
                    self.handler_errors[handler.handler_id] = self.handler_errors[handler.handler_id][-100:]
                
                if attempt < max_attempts - 1:
                    # Wait before retry
                    wait_time = backoff_factor ** attempt
                    await asyncio.sleep(wait_time)
                    self.metrics.events_retried += 1
                else:
                    # Max attempts reached
                    raise

    async def _process_dead_letter_queue(self):
        """Process dead letter queue"""
        
        while not self._shutdown_event.is_set():
            try:
                # Get item from dead letter queue
                item = await asyncio.wait_for(
                    self.dead_letter_queue.get(),
                    timeout=5.0
                )
                
                # Log dead letter event
                event = item["event"]
                error = item["error"]
                
                logger.error(
                    f"Event {event.event_id} sent to dead letter queue: {error}"
                )
                
                # Store in dead letter store for analysis
                # In production, this would be persisted
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Dead letter processing error: {str(e)}")

    async def create_event_stream(
        self,
        stream_name: str,
        event_types: List[str],
        retention_policy: Optional[Dict[str, Any]] = None,
        partitioning_key: Optional[str] = None
    ) -> str:
        """Create event stream"""
        
        stream_id = f"stream_{int(time.time())}_{len(self.streams)}"
        
        stream = EventStream(
            stream_id=stream_id,
            stream_name=stream_name,
            event_types=event_types,
            retention_policy=retention_policy or {},
            partitioning_key=partitioning_key
        )
        
        self.streams[stream_id] = stream
        self.metrics.streams_active += 1
        
        logger.info(f"Created event stream '{stream_name}' ({stream_id})")
        return stream_id

    async def get_events_by_aggregate(
        self,
        aggregate_id: str,
        aggregate_type: str,
        from_version: Optional[int] = None
    ) -> List[Event]:
        """Get events for specific aggregate"""
        
        key = f"{aggregate_type}:{aggregate_id}"
        events = self.event_store.get(key, [])
        
        if from_version is not None:
            events = [e for e in events if e.version >= from_version]
        
        return sorted(events, key=lambda e: e.timestamp)

    async def get_events_by_type(
        self,
        event_type: str,
        limit: Optional[int] = None,
        from_timestamp: Optional[datetime] = None
    ) -> List[Event]:
        """Get events by type"""
        
        events = self.event_store.get(event_type, [])
        
        if from_timestamp:
            events = [e for e in events if e.timestamp >= from_timestamp]
        
        # Sort by timestamp
        events = sorted(events, key=lambda e: e.timestamp)
        
        if limit:
            events = events[-limit:]
        
        return events

    async def get_aggregate_state(
        self,
        aggregate_id: str,
        aggregate_type: str,
        version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get current state of aggregate"""
        
        # Check for snapshot
        snapshot_key = f"{aggregate_type}:{aggregate_id}"
        snapshot = self.snapshots.get(snapshot_key)
        
        if snapshot and (version is None or snapshot.version <= version):
            # Start from snapshot
            state = snapshot.snapshot_data.copy()
            from_version = snapshot.version + 1
        else:
            # Start from beginning
            state = {}
            from_version = 1
        
        # Apply events after snapshot
        events = await self.get_events_by_aggregate(aggregate_id, aggregate_type, from_version)
        
        if version is not None:
            events = [e for e in events if e.version <= version]
        
        # Apply events to state
        for event in events:
            state.update(event.event_data)
            state["version"] = event.version
            state["last_modified"] = event.timestamp.isoformat()
        
        return state

    async def replay_events(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime] = None,
        event_types: Optional[List[str]] = None
    ):
        """Replay events for reprocessing"""
        
        to_timestamp = to_timestamp or datetime.utcnow()
        
        # Collect events to replay
        events_to_replay = []
        
        for event_type, events in self.event_store.items():
            if event_types and event_type not in event_types:
                continue
            
            for event in events:
                if from_timestamp <= event.timestamp <= to_timestamp:
                    events_to_replay.append(event)
        
        # Sort by timestamp
        events_to_replay.sort(key=lambda e: e.timestamp)
        
        # Replay events
        for event in events_to_replay:
            # Mark as replay
            event.metadata["replayed"] = True
            event.metadata["replay_timestamp"] = datetime.utcnow().isoformat()
            
            await self.event_queue.put(event)
        
        logger.info(f"Replaying {len(events_to_replay)} events")

    def _update_processing_time(self, processing_time: float):
        """Update average processing time"""
        self.metrics.avg_processing_time = (
            self.metrics.avg_processing_time * 0.9 + processing_time * 0.1
        )

    async def _collect_metrics(self):
        """Collect throughput metrics"""
        
        last_count = 0
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                current_count = self.metrics.events_processed
                throughput = (current_count - last_count) / 60.0
                self.metrics.throughput_per_second = throughput
                last_count = current_count
                
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")

    def get_handler_errors(self, handler_id: str) -> List[Dict[str, Any]]:
        """Get recent errors for handler"""
        return self.handler_errors.get(handler_id, [])

    def get_metrics(self) -> EventMetrics:
        """Get event processing metrics"""
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for event-driven system"""
        try:
            # Test event publishing and handling
            test_event = Event(
                event_type="health_check",
                aggregate_id="test",
                aggregate_type="system",
                event_data={"test": True}
            )
            
            # Publish test event
            await self.publish_event(test_event)
            
            # Wait a bit for processing
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Event-driven health check failed: {str(e)}")
            return False

    async def shutdown(self):
        """Shutdown event processing"""
        logger.info("🛑 Shutting down event-driven core")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

# Module exports
__all__ = [
    "EventDrivenCore", "Event", "EventHandler", "EventStream", 
    "EventSnapshot", "EventType", "EventStatus", "EventMetrics"
]

logger.info("🔄 Event Driven Core module loaded")