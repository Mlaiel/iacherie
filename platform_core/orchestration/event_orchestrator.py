#!/usr/bin/env python3
"""
Event Orchestrator - Enterprise Core Component
Event-driven architecture coordination and real-time event stream processing

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive event orchestration capabilities including:
- Event-driven architecture coordination
- Cross-service event propagation
- Event sourcing and replay capabilities
- Real-time event stream processing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from abc import ABC, abstractmethod
import heapq
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DeliveryMode(Enum):
    """Event delivery modes"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class EventMetadata:
    """Event metadata for tracking and routing"""
    event_id: str
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    source_service: Optional[str] = None
    trace_id: Optional[str] = None
    version: int = 1
    tags: Set[str] = field(default_factory=set)
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class Event:
    """Event definition with comprehensive metadata"""
    event_type: str
    payload: Dict[str, Any]
    metadata: EventMetadata
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE


@dataclass
class EventSubscription:
    """Event subscription configuration"""
    subscription_id: str
    event_types: Set[str]
    handler: Callable[[Event], Awaitable[None]]
    filter_conditions: Dict[str, Any] = field(default_factory=dict)
    max_concurrent_events: int = 10
    dead_letter_queue: bool = True
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventStream:
    """Event stream definition"""
    stream_id: str
    name: str
    event_types: Set[str]
    partitions: int = 1
    retention_hours: int = 168  # 7 days default
    max_batch_size: int = 1000
    compression_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingStats:
    """Event processing statistics"""
    total_events: int = 0
    successful_events: int = 0
    failed_events: int = 0
    retried_events: int = 0
    average_processing_time_ms: float = 0.0
    events_per_second: float = 0.0
    last_processed_at: Optional[datetime] = None


class EventStore(ABC):
    """Abstract event store interface"""
    
    @abstractmethod
    async def append_event(self, stream_id: str, event: Event) -> bool:
        """Append event to stream"""
        pass
    
    @abstractmethod
    async def get_events(self, stream_id: str, from_version: int = 0, limit: int = 1000) -> List[Event]:
        """Get events from stream"""
        pass
    
    @abstractmethod
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get specific event by ID"""
        pass


class InMemoryEventStore(EventStore):
    """In-memory event store implementation"""
    
    def __init__(self):
        self.streams: Dict[str, List[Event]] = defaultdict(list)
        self.event_index: Dict[str, Event] = {}
    
    async def append_event(self, stream_id: str, event: Event) -> bool:
        """Append event to stream"""
        try:
            self.streams[stream_id].append(event)
            self.event_index[event.metadata.event_id] = event
            return True
        except Exception as e:
            logger.error(f"Failed to append event to stream {stream_id}: {e}")
            return False
    
    async def get_events(self, stream_id: str, from_version: int = 0, limit: int = 1000) -> List[Event]:
        """Get events from stream"""
        try:
            events = self.streams.get(stream_id, [])
            return events[from_version:from_version + limit]
        except Exception as e:
            logger.error(f"Failed to get events from stream {stream_id}: {e}")
            return []
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get specific event by ID"""
        return self.event_index.get(event_id)


class EventOrchestrator:
    """
    Enterprise Event Orchestrator
    
    Provides comprehensive event-driven architecture coordination including
    cross-service event propagation, event sourcing, replay capabilities,
    and real-time event stream processing with enterprise-grade reliability.
    """
    
    def __init__(self, event_store: Optional[EventStore] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.event_store = event_store or InMemoryEventStore()
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.streams: Dict[str, EventStream] = {}
        self.event_handlers: Dict[str, List[EventSubscription]] = defaultdict(list)
        self.processing_queue: List[Tuple[float, Event, EventSubscription]] = []
        self.dead_letter_queue: List[Event] = []
        self.processing_stats: Dict[str, ProcessingStats] = defaultdict(ProcessingStats)
        self.running_handlers: Dict[str, Set[asyncio.Task]] = defaultdict(set)
        
        # Configuration
        self._max_queue_size = self.config.get('max_queue_size', 10000)
        self._batch_processing_size = self.config.get('batch_processing_size', 100)
        self._processing_interval = self.config.get('processing_interval', 0.1)
        self._dead_letter_retention_hours = self.config.get('dead_letter_retention_hours', 72)
        self._metrics_interval = self.config.get('metrics_interval', 60)
        
        # Background tasks
        self._processing_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("Event Orchestrator initialized")
    
    async def start(self) -> None:
        """Start the event orchestrator"""
        try:
            logger.info("Starting Event Orchestrator...")
            
            # Start background tasks
            self._processing_task = asyncio.create_task(self._processing_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self._metrics_task = asyncio.create_task(self._metrics_loop())
            
            # Initialize core event streams
            await self._initialize_core_streams()
            
            logger.info("Event Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Event Orchestrator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the event orchestrator"""
        try:
            logger.info("Stopping Event Orchestrator...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            if self._processing_task:
                self._processing_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            if self._metrics_task:
                self._metrics_task.cancel()
            
            # Cancel all running handlers
            for handler_tasks in self.running_handlers.values():
                for task in handler_tasks:
                    task.cancel()
            
            # Wait for handlers to complete
            for handler_tasks in self.running_handlers.values():
                if handler_tasks:
                    await asyncio.gather(*handler_tasks, return_exceptions=True)
            
            logger.info("Event Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Event Orchestrator: {e}")
    
    # Event Publishing
    async def publish_event(self, event: Event, stream_id: Optional[str] = None) -> bool:
        """Publish an event to the orchestrator"""
        try:
            # Validate event
            if not event.event_type or not event.payload:
                raise ValueError("Event type and payload are required")
            
            # Check expiration
            if event.expires_at and event.expires_at < datetime.utcnow():
                logger.warning(f"Event {event.metadata.event_id} expired, not publishing")
                return False
            
            # Store event if stream specified
            if stream_id:
                if stream_id not in self.streams:
                    logger.warning(f"Stream {stream_id} not found, creating default stream")
                    await self.create_stream(EventStream(
                        stream_id=stream_id,
                        name=stream_id,
                        event_types={event.event_type}
                    ))
                
                await self.event_store.append_event(stream_id, event)
            
            # Find matching subscriptions
            matching_subscriptions = self._find_matching_subscriptions(event)
            
            if not matching_subscriptions:
                logger.debug(f"No subscriptions found for event type: {event.event_type}")
                return True
            
            # Queue event for processing
            for subscription in matching_subscriptions:
                priority_value = event.priority.value
                heapq.heappush(self.processing_queue, (-priority_value, event, subscription))
            
            logger.debug(f"Event {event.metadata.event_id} queued for {len(matching_subscriptions)} subscriptions")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.metadata.event_id}: {e}")
            return False
    
    async def publish_events_batch(self, events: List[Event], stream_id: Optional[str] = None) -> int:
        """Publish multiple events in batch"""
        try:
            successful_count = 0
            
            for event in events:
                if await self.publish_event(event, stream_id):
                    successful_count += 1
            
            logger.info(f"Published {successful_count}/{len(events)} events successfully")
            return successful_count
            
        except Exception as e:
            logger.error(f"Failed to publish event batch: {e}")
            return 0
    
    # Event Subscription
    async def subscribe(self, subscription: EventSubscription) -> bool:
        """Subscribe to events"""
        try:
            # Validate subscription
            if not subscription.subscription_id or not subscription.event_types:
                raise ValueError("Subscription ID and event types are required")
            
            # Register subscription
            self.subscriptions[subscription.subscription_id] = subscription
            
            # Index by event types
            for event_type in subscription.event_types:
                self.event_handlers[event_type].append(subscription)
            
            logger.info(f"Subscription {subscription.subscription_id} registered for event types: {subscription.event_types}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register subscription {subscription.subscription_id}: {e}")
            return False
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        try:
            if subscription_id not in self.subscriptions:
                logger.warning(f"Subscription {subscription_id} not found")
                return False
            
            subscription = self.subscriptions.pop(subscription_id)
            
            # Remove from event handlers
            for event_type in subscription.event_types:
                if event_type in self.event_handlers:
                    self.event_handlers[event_type] = [
                        sub for sub in self.event_handlers[event_type]
                        if sub.subscription_id != subscription_id
                    ]
            
            # Cancel running handlers for this subscription
            if subscription_id in self.running_handlers:
                for task in self.running_handlers[subscription_id]:
                    task.cancel()
                del self.running_handlers[subscription_id]
            
            logger.info(f"Subscription {subscription_id} unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister subscription {subscription_id}: {e}")
            return False
    
    # Stream Management
    async def create_stream(self, stream: EventStream) -> bool:
        """Create an event stream"""
        try:
            self.streams[stream.stream_id] = stream
            logger.info(f"Event stream {stream.stream_id} created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create stream {stream.stream_id}: {e}")
            return False
    
    async def delete_stream(self, stream_id: str) -> bool:
        """Delete an event stream"""
        try:
            if stream_id in self.streams:
                del self.streams[stream_id]
                logger.info(f"Event stream {stream_id} deleted")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete stream {stream_id}: {e}")
            return False
    
    async def get_stream_events(self, stream_id: str, from_version: int = 0, limit: int = 1000) -> List[Event]:
        """Get events from a stream"""
        return await self.event_store.get_events(stream_id, from_version, limit)
    
    # Event Replay
    async def replay_events(self, stream_id: str, from_timestamp: datetime, to_timestamp: Optional[datetime] = None) -> int:
        """Replay events from a stream within time range"""
        try:
            events = await self.event_store.get_events(stream_id)
            to_timestamp = to_timestamp or datetime.utcnow()
            
            replayed_count = 0
            for event in events:
                if from_timestamp <= event.timestamp <= to_timestamp:
                    # Create replay event with new metadata
                    replay_event = Event(
                        event_type=f"replay.{event.event_type}",
                        payload=event.payload,
                        metadata=EventMetadata(
                            event_id=str(uuid.uuid4()),
                            correlation_id=event.metadata.event_id,
                            source_service="event_orchestrator"
                        ),
                        priority=EventPriority.LOW
                    )
                    
                    if await self.publish_event(replay_event):
                        replayed_count += 1
            
            logger.info(f"Replayed {replayed_count} events from stream {stream_id}")
            return replayed_count
            
        except Exception as e:
            logger.error(f"Failed to replay events from stream {stream_id}: {e}")
            return 0
    
    # Statistics and Monitoring
    async def get_processing_stats(self, subscription_id: Optional[str] = None) -> Dict[str, Any]:
        """Get event processing statistics"""
        try:
            if subscription_id:
                if subscription_id in self.processing_stats:
                    stats = self.processing_stats[subscription_id]
                    return {
                        "subscription_id": subscription_id,
                        "total_events": stats.total_events,
                        "successful_events": stats.successful_events,
                        "failed_events": stats.failed_events,
                        "retried_events": stats.retried_events,
                        "average_processing_time_ms": stats.average_processing_time_ms,
                        "events_per_second": stats.events_per_second,
                        "last_processed_at": stats.last_processed_at.isoformat() if stats.last_processed_at else None
                    }
                else:
                    return {"subscription_id": subscription_id, "error": "not_found"}
            else:
                # Return aggregated stats
                total_stats = {
                    "total_subscriptions": len(self.subscriptions),
                    "total_streams": len(self.streams),
                    "queue_size": len(self.processing_queue),
                    "dead_letter_queue_size": len(self.dead_letter_queue),
                    "subscriptions": {}
                }
                
                for sub_id, stats in self.processing_stats.items():
                    total_stats["subscriptions"][sub_id] = {
                        "total_events": stats.total_events,
                        "successful_events": stats.successful_events,
                        "failed_events": stats.failed_events,
                        "events_per_second": stats.events_per_second
                    }
                
                return total_stats
            
        except Exception as e:
            logger.error(f"Failed to get processing stats: {e}")
            return {"error": str(e)}
    
    # Internal Methods
    def _find_matching_subscriptions(self, event: Event) -> List[EventSubscription]:
        """Find subscriptions that match the event"""
        matching_subscriptions = []
        
        for subscription in self.event_handlers.get(event.event_type, []):
            # Check filter conditions
            if self._event_matches_filters(event, subscription.filter_conditions):
                matching_subscriptions.append(subscription)
        
        return matching_subscriptions
    
    def _event_matches_filters(self, event: Event, filters: Dict[str, Any]) -> bool:
        """Check if event matches subscription filters"""
        if not filters:
            return True
        
        for key, expected_value in filters.items():
            # Support nested key access with dot notation
            actual_value = self._get_nested_value(event.payload, key)
            
            if actual_value != expected_value:
                return False
        
        return True
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    async def _initialize_core_streams(self) -> None:
        """Initialize core platform event streams"""
        try:
            # Platform events stream
            platform_stream = EventStream(
                stream_id="platform_events",
                name="Platform Core Events",
                event_types={
                    "service.registered", "service.unregistered", "service.health_changed",
                    "workflow.started", "workflow.completed", "workflow.failed",
                    "tenant.created", "tenant.updated", "tenant.deleted",
                    "subscription.created", "subscription.updated", "subscription.cancelled"
                },
                retention_hours=168,
                max_batch_size=1000
            )
            
            await self.create_stream(platform_stream)
            
            # Creator events stream
            creator_stream = EventStream(
                stream_id="creator_events",
                name="Creator Workflow Events",
                event_types={
                    "content.uploaded", "content.protected", "content.enhanced",
                    "content.distributed", "content.monetized",
                    "collaboration.started", "collaboration.completed",
                    "gamification.achievement", "gamification.reward"
                },
                retention_hours=720,  # 30 days
                max_batch_size=500
            )
            
            await self.create_stream(creator_stream)
            
            logger.info("Core event streams initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize core streams: {e}")
    
    async def _processing_loop(self) -> None:
        """Background event processing loop"""
        while not self._shutdown_event.is_set():
            try:
                if not self.processing_queue:
                    await asyncio.sleep(self._processing_interval)
                    continue
                
                # Process events in batches
                batch_size = min(len(self.processing_queue), self._batch_processing_size)
                batch = []
                
                for _ in range(batch_size):
                    if self.processing_queue:
                        _, event, subscription = heapq.heappop(self.processing_queue)
                        batch.append((event, subscription))
                
                # Process batch
                if batch:
                    await self._process_event_batch(batch)
                
                await asyncio.sleep(self._processing_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(1)
    
    async def _process_event_batch(self, batch: List[Tuple[Event, EventSubscription]]) -> None:
        """Process a batch of events"""
        tasks = []
        
        for event, subscription in batch:
            # Check concurrent handler limit
            running_count = len(self.running_handlers[subscription.subscription_id])
            if running_count >= subscription.max_concurrent_events:
                # Re-queue event for later processing
                priority_value = event.priority.value
                heapq.heappush(self.processing_queue, (-priority_value, event, subscription))
                continue
            
            # Create processing task
            task = asyncio.create_task(self._process_single_event(event, subscription))
            tasks.append(task)
            self.running_handlers[subscription.subscription_id].add(task)
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_event(self, event: Event, subscription: EventSubscription) -> None:
        """Process a single event"""
        start_time = datetime.utcnow()
        stats = self.processing_stats[subscription.subscription_id]
        
        try:
            stats.total_events += 1
            
            # Call event handler
            await subscription.handler(event)
            
            # Update statistics
            stats.successful_events += 1
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            stats.average_processing_time_ms = (
                (stats.average_processing_time_ms * (stats.successful_events - 1) + processing_time) 
                / stats.successful_events
            )
            stats.last_processed_at = datetime.utcnow()
            
            logger.debug(f"Event {event.metadata.event_id} processed successfully by {subscription.subscription_id}")
            
        except Exception as e:
            stats.failed_events += 1
            
            logger.error(f"Event {event.metadata.event_id} processing failed in {subscription.subscription_id}: {e}")
            
            # Handle retry logic
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                stats.retried_events += 1
                
                # Re-queue for retry with exponential backoff
                delay = min(2 ** event.retry_count, 60)  # Max 60 seconds
                await asyncio.sleep(delay)
                
                priority_value = event.priority.value
                heapq.heappush(self.processing_queue, (-priority_value, event, subscription))
                
                logger.info(f"Event {event.metadata.event_id} queued for retry {event.retry_count}")
            else:
                # Send to dead letter queue
                if subscription.dead_letter_queue:
                    self.dead_letter_queue.append(event)
                    logger.warning(f"Event {event.metadata.event_id} sent to dead letter queue")
        
        finally:
            # Remove from running handlers
            self.running_handlers[subscription.subscription_id].discard(asyncio.current_task())
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                # Clean up expired events from dead letter queue
                cutoff_time = current_time - timedelta(hours=self._dead_letter_retention_hours)
                self.dead_letter_queue = [
                    event for event in self.dead_letter_queue
                    if event.timestamp > cutoff_time
                ]
                
                # Clean up expired events from processing queue
                filtered_queue = []
                for priority, event, subscription in self.processing_queue:
                    if not event.expires_at or event.expires_at > current_time:
                        filtered_queue.append((priority, event, subscription))
                
                self.processing_queue = filtered_queue
                heapq.heapify(self.processing_queue)
                
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(300)
    
    async def _metrics_loop(self) -> None:
        """Background metrics calculation loop"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                # Calculate events per second for each subscription
                for sub_id, stats in self.processing_stats.items():
                    if stats.last_processed_at:
                        time_diff = (current_time - stats.last_processed_at).total_seconds()
                        if time_diff > 0:
                            stats.events_per_second = stats.successful_events / time_diff
                
                await asyncio.sleep(self._metrics_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics loop error: {e}")
                await asyncio.sleep(60)
    
    # Context Manager Support
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Factory function
def create_event_orchestrator(event_store: Optional[EventStore] = None, config: Optional[Dict[str, Any]] = None) -> EventOrchestrator:
    """Factory function to create an Event Orchestrator"""
    return EventOrchestrator(event_store, config)


# Example event handlers
async def handle_service_registered(event: Event) -> None:
    """Example handler for service registration events"""
    service_info = event.payload
    logger.info(f"Service registered: {service_info.get('service_id')} - {service_info.get('name')}")


async def handle_workflow_completed(event: Event) -> None:
    """Example handler for workflow completion events"""
    workflow_info = event.payload
    logger.info(f"Workflow completed: {workflow_info.get('workflow_id')} - Status: {workflow_info.get('status')}")


async def handle_content_uploaded(event: Event) -> None:
    """Example handler for content upload events"""
    content_info = event.payload
    logger.info(f"Content uploaded: {content_info.get('content_id')} by {content_info.get('creator_id')}")


# Example usage
async def main():
    """Example usage of Event Orchestrator"""
    async with create_event_orchestrator() as orchestrator:
        # Create subscriptions
        service_subscription = EventSubscription(
            subscription_id="service_monitor",
            event_types={"service.registered", "service.unregistered"},
            handler=handle_service_registered,
            max_concurrent_events=5
        )
        
        workflow_subscription = EventSubscription(
            subscription_id="workflow_monitor",
            event_types={"workflow.completed", "workflow.failed"},
            handler=handle_workflow_completed,
            filter_conditions={"priority": "high"}
        )
        
        content_subscription = EventSubscription(
            subscription_id="content_monitor",
            event_types={"content.uploaded"},
            handler=handle_content_uploaded
        )
        
        # Register subscriptions
        await orchestrator.subscribe(service_subscription)
        await orchestrator.subscribe(workflow_subscription)
        await orchestrator.subscribe(content_subscription)
        
        # Publish some test events
        service_event = Event(
            event_type="service.registered",
            payload={
                "service_id": "content_service_1",
                "name": "Content Management Service",
                "version": "1.0.0"
            },
            metadata=EventMetadata(
                event_id=str(uuid.uuid4()),
                source_service="service_registry"
            ),
            priority=EventPriority.HIGH
        )
        
        content_event = Event(
            event_type="content.uploaded",
            payload={
                "content_id": "content_123",
                "creator_id": "creator_456",
                "content_type": "video",
                "size_bytes": 1024000
            },
            metadata=EventMetadata(
                event_id=str(uuid.uuid4()),
                source_service="content_service"
            )
        )
        
        await orchestrator.publish_event(service_event, "platform_events")
        await orchestrator.publish_event(content_event, "creator_events")
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get statistics
        stats = await orchestrator.get_processing_stats()
        print(f"Processing stats: {json.dumps(stats, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())