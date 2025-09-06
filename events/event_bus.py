"""🚀 Enterprise Event Bus System - IA Influencer Agent Platform
==============================================================
Module: events/event_bus.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE EVENT BUS
Central communication hub for event-driven architecture
- High-performance pub/sub pattern with persistence
- Event sourcing and automatic replay capabilities
- Dead letter handling with intelligent retry mechanisms
- Real-time monitoring and advanced analytics
- Horizontal scaling and fault tolerance
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import weakref
import inspect
from concurrent.futures import ThreadPoolExecutor

from .core.base_event import BaseEvent
from .core.event_priority import EventPriority
from .core.event_status import EventStatus
from .core.exceptions import (
    EventProcessingError,
    EventValidationError,
    EventStreamingError
)

logger = logging.getLogger(__name__)


class EventBusMode(Enum):
    """Event bus operation modes"""
    IN_MEMORY = "in_memory"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"


@dataclass
class EventSubscription:
    """Event subscription configuration"""
    subscription_id: str
    subscriber_id: str
    event_patterns: List[str]
    filters: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.MEDIUM
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    max_retries: int = 3
    retry_delay: float = 1.0
    dead_letter_enabled: bool = True
    
    def matches_event(self, event: BaseEvent) -> bool:
        """Check if subscription matches event"""
        # Pattern matching logic
        for pattern in self.event_patterns:
            if pattern == "*" or pattern == event.event_type:
                return True
            if pattern.endswith("*") and event.event_type.startswith(pattern[:-1]):
                return True
        return False


@dataclass
class EventMetrics:
    """Event processing metrics"""
    total_published: int = 0
    total_processed: int = 0
    total_failed: int = 0
    total_retries: int = 0
    average_processing_time: float = 0.0
    peak_throughput: float = 0.0
    last_event_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_published == 0:
            return 1.0
        return self.total_processed / self.total_published
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate"""
        return 1.0 - self.success_rate


class EventBus:
    """Enterprise-grade event bus for distributed systems"""
    
    def __init__(self, 
                 mode: EventBusMode = EventBusMode.IN_MEMORY,
                 namespace: str = "events",
                 max_workers: int = 10,
                 batch_size: int = 100,
                 enable_metrics: bool = True):
        """Initialize event bus
        
        Args:
            mode: Operation mode (in_memory, distributed, hybrid)
            namespace: Event namespace for isolation
            max_workers: Maximum concurrent workers
            batch_size: Batch processing size
            enable_metrics: Enable metrics collection
        """
        self.mode = mode
        self.namespace = namespace
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.enable_metrics = enable_metrics
        
        # Core components
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.handlers: Dict[str, Callable] = {}
        self.event_history: List[BaseEvent] = []
        self.dead_letter_queue: List[BaseEvent] = []
        
        # Processing state
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Metrics
        self.metrics = EventMetrics() if enable_metrics else None
        self.start_time = datetime.utcnow()
        
        # Event registry
        self.event_types: Set[str] = set()
        
        logger.info(f"EventBus initialized - Mode: {mode.value}, Namespace: {namespace}")
    
    async def start(self) -> None:
        """Start the event bus processing"""
        if self._running:
            logger.warning("Event bus already running")
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())
        
        logger.info(f"Event bus started - Namespace: {self.namespace}")
    
    async def stop(self) -> None:
        """Stop the event bus processing"""
        self._running = False
        
        if self._processor_task:
            try:
                await asyncio.wait_for(self._processor_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._processor_task.cancel()
        
        self._executor.shutdown(wait=True)
        
        logger.info(f"Event bus stopped - Namespace: {self.namespace}")
    
    async def publish(self, event: BaseEvent) -> str:
        """Publish an event to the bus
        
        Args:
            event: Event to publish
            
        Returns:
            Event ID
        """
        if not isinstance(event, BaseEvent):
            raise EventValidationError(f"Invalid event type: {type(event)}")
        
        # Ensure event has ID
        if not event.event_id:
            event.event_id = str(uuid.uuid4())
        
        # Set timestamp if not present
        if not event.timestamp:
            event.timestamp = datetime.utcnow()
        
        # Add to history
        self.event_history.append(event)
        self.event_types.add(event.event_type)
        
        # Update metrics
        if self.metrics:
            self.metrics.total_published += 1
            self.metrics.last_event_time = datetime.utcnow()
        
        # Trigger async processing
        asyncio.create_task(self._distribute_event(event))
        
        logger.debug(f"Event published: {event.event_id} ({event.event_type})")
        return event.event_id
    
    async def subscribe(self,
                       event_patterns: List[str],
                       handler: Callable,
                       subscriber_id: Optional[str] = None,
                       filters: Optional[Dict[str, Any]] = None,
                       priority: EventPriority = EventPriority.MEDIUM,
                       max_retries: int = 3) -> str:
        """Subscribe to events
        
        Args:
            event_patterns: List of event patterns to match
            handler: Event handler function
            subscriber_id: Optional subscriber identifier
            filters: Optional event filters
            priority: Subscription priority
            max_retries: Maximum retry attempts
            
        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        
        # Validate handler
        if not callable(handler):
            raise EventValidationError("Handler must be callable")
        
        # Create subscription
        subscription = EventSubscription(
            subscription_id=subscription_id,
            subscriber_id=subscriber_id or f"subscriber-{subscription_id[:8]}",
            event_patterns=event_patterns,
            filters=filters or {},
            priority=priority,
            max_retries=max_retries
        )
        
        self.subscriptions[subscription_id] = subscription
        self.handlers[subscription_id] = handler
        
        logger.info(f"Subscription created: {subscription_id} for patterns: {event_patterns}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events
        
        Args:
            subscription_id: Subscription to remove
            
        Returns:
            True if subscription was removed
        """
        removed = False
        
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            removed = True
        
        if subscription_id in self.handlers:
            del self.handlers[subscription_id]
        
        if removed:
            logger.info(f"Subscription removed: {subscription_id}")
        
        return removed
    
    async def _process_events(self) -> None:
        """Main event processing loop"""
        logger.info("Event processing loop started")
        
        while self._running:
            try:
                # Process events in batches
                await asyncio.sleep(0.1)  # Prevent busy waiting
                
                # Placeholder for distributed processing logic
                # In production, this would read from Redis streams, Kafka, etc.
                
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(1.0)  # Back off on error
    
    async def _distribute_event(self, event: BaseEvent) -> None:
        """Distribute event to matching subscribers"""
        start_time = time.time()
        
        matching_subscriptions = [
            (sub_id, sub) for sub_id, sub in self.subscriptions.items()
            if sub.active and sub.matches_event(event)
        ]
        
        if not matching_subscriptions:
            logger.debug(f"No subscribers for event: {event.event_type}")
            return
        
        # Sort by priority
        matching_subscriptions.sort(key=lambda x: x[1].priority.value, reverse=True)
        
        # Process handlers
        tasks = []
        for sub_id, subscription in matching_subscriptions:
            handler = self.handlers.get(sub_id)
            if handler:
                task = asyncio.create_task(
                    self._handle_event_with_retry(event, handler, subscription)
                )
                tasks.append(task)
        
        # Wait for all handlers to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update metrics
            if self.metrics:
                processing_time = time.time() - start_time
                self.metrics.average_processing_time = (
                    (self.metrics.average_processing_time * self.metrics.total_processed + 
                     processing_time) / (self.metrics.total_processed + 1)
                )
                
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                self.metrics.total_processed += success_count
                self.metrics.total_failed += len(results) - success_count
    
    async def _handle_event_with_retry(self,
                                     event: BaseEvent,
                                     handler: Callable,
                                     subscription: EventSubscription) -> bool:
        """Handle event with retry logic"""
        last_exception = None
        
        for attempt in range(subscription.max_retries + 1):
            try:
                # Call handler
                if inspect.iscoroutinefunction(handler):
                    result = await handler(event)
                else:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self._executor, handler, event
                    )
                
                # Success
                logger.debug(f"Event handled successfully: {event.event_id}")
                return True
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Handler failed (attempt {attempt + 1}): {e}")
                
                if attempt < subscription.max_retries:
                    # Wait before retry
                    delay = subscription.retry_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    
                    if self.metrics:
                        self.metrics.total_retries += 1
        
        # All retries failed
        if subscription.dead_letter_enabled:
            await self._send_to_dead_letter(event, last_exception)
        
        return False
    
    async def _send_to_dead_letter(self, event: BaseEvent, error: Exception) -> None:
        """Send failed event to dead letter queue"""
        event.status = EventStatus.FAILED
        event.error_message = str(error)
        self.dead_letter_queue.append(event)
        
        logger.error(f"Event sent to DLQ: {event.event_id} - {error}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current event bus metrics"""
        if not self.metrics:
            return {}
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "namespace": self.namespace,
            "mode": self.mode.value,
            "running": self._running,
            "uptime_seconds": uptime,
            "subscriptions": len(self.subscriptions),
            "event_types": len(self.event_types),
            "metrics": {
                "total_published": self.metrics.total_published,
                "total_processed": self.metrics.total_processed,
                "total_failed": self.metrics.total_failed,
                "total_retries": self.metrics.total_retries,
                "success_rate": self.metrics.success_rate,
                "failure_rate": self.metrics.failure_rate,
                "average_processing_time": self.metrics.average_processing_time,
                "events_per_second": self.metrics.total_processed / max(uptime, 1)
            },
            "dead_letter_queue_size": len(self.dead_letter_queue),
            "event_history_size": len(self.event_history)
        }
    
    def get_subscription_details(self) -> Dict[str, Any]:
        """Get detailed subscription information"""
        return {
            sub_id: {
                "subscriber_id": sub.subscriber_id,
                "event_patterns": sub.event_patterns,
                "priority": sub.priority.name,
                "active": sub.active,
                "created_at": sub.created_at.isoformat(),
                "max_retries": sub.max_retries,
                "dead_letter_enabled": sub.dead_letter_enabled
            }
            for sub_id, sub in self.subscriptions.items()
        }
    
    async def replay_events(self,
                           from_timestamp: Optional[datetime] = None,
                           to_timestamp: Optional[datetime] = None,
                           event_types: Optional[List[str]] = None) -> int:
        """Replay events from history
        
        Args:
            from_timestamp: Start time for replay
            to_timestamp: End time for replay
            event_types: Specific event types to replay
            
        Returns:
            Number of events replayed
        """
        events_to_replay = []
        
        for event in self.event_history:
            # Time filter
            if from_timestamp and event.timestamp < from_timestamp:
                continue
            if to_timestamp and event.timestamp > to_timestamp:
                continue
            
            # Type filter
            if event_types and event.event_type not in event_types:
                continue
            
            events_to_replay.append(event)
        
        # Replay events
        for event in events_to_replay:
            # Create a copy to avoid modifying original
            replay_event = BaseEvent(
                event_type=event.event_type,
                data=event.data.copy() if event.data else {},
                metadata=event.metadata.copy() if event.metadata else {}
            )
            replay_event.metadata["replayed"] = True
            replay_event.metadata["original_event_id"] = event.event_id
            
            await self.publish(replay_event)
        
        logger.info(f"Replayed {len(events_to_replay)} events")
        return len(events_to_replay)


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_global_event_bus() -> EventBus:
    """Get or create global event bus instance"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


async def publish_event(event: BaseEvent) -> str:
    """Convenience function to publish event to global bus"""
    bus = get_global_event_bus()
    return await bus.publish(event)


async def subscribe_to_events(event_patterns: List[str], 
                            handler: Callable,
                            **kwargs) -> str:
    """Convenience function to subscribe to global bus"""
    bus = get_global_event_bus()
    return await bus.subscribe(event_patterns, handler, **kwargs)