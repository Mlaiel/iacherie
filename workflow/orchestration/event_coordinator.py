"""
🔥 ENTERPRISE EVENT COORDINATOR - AINFLUE PLATFORM
Ultra-advanced event-driven coordination for enterprise workflows
Handles async communication and event orchestration
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Set, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import logging
from collections import defaultdict, deque
import weakref

try:
    from ..core.exceptions import EventCoordinatorException
    from ..utils.metrics import MetricsCollector
except ImportError:
    # Fallback for missing dependencies
    class EventCoordinatorException(Exception): pass
    class MetricsCollector: pass


class EventType(Enum):
    """Types of workflow events."""
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    
    STAGE_STARTED = "stage.started"
    STAGE_COMPLETED = "stage.completed"
    STAGE_FAILED = "stage.failed"
    
    TASK_SCHEDULED = "task.scheduled"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_RETRIED = "task.retried"
    
    STATE_CHANGED = "state.changed"
    CHECKPOINT_CREATED = "checkpoint.created"
    RECOVERY_INITIATED = "recovery.initiated"
    
    RESOURCE_ALLOCATED = "resource.allocated"
    RESOURCE_RELEASED = "resource.released"
    THRESHOLD_EXCEEDED = "threshold.exceeded"
    
    CUSTOM_EVENT = "custom.event"


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EventStatus(Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class WorkflowEvent:
    """Enterprise workflow event."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CUSTOM_EVENT
    source: str = ""
    target: Optional[str] = None
    workflow_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    status: EventStatus = EventStatus.PENDING


@dataclass
class EventHandler:
    """Event handler registration."""
    handler_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_types: List[EventType] = field(default_factory=list)
    handler_func: Callable = None
    condition: Optional[Callable] = None  # Condition function for filtering
    priority: int = 0  # Handler priority (higher number = higher priority)
    async_execution: bool = True
    max_concurrent: int = 10
    timeout_seconds: int = 30
    enabled: bool = True


@dataclass
class EventSubscription:
    """Event subscription configuration."""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = ""
    event_types: List[EventType] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    delivery_mode: str = "async"  # async, sync, batch
    batch_size: int = 10
    batch_timeout_seconds: int = 60
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class EventCoordinatorConfig:
    """Event coordinator configuration."""
    max_event_queue_size: int = 10000
    max_concurrent_handlers: int = 100
    enable_event_persistence: bool = True
    enable_metrics: bool = True
    cleanup_interval_seconds: int = 3600
    batch_processing_interval_seconds: int = 10
    dead_letter_queue_enabled: bool = True


class EventCoordinator:
    """
    🔥 ENTERPRISE EVENT COORDINATOR
    
    Ultra-advanced event coordination with:
    - High-performance async event processing
    - Priority-based event queues
    - Intelligent event routing
    - Advanced subscription management
    - Comprehensive error handling
    - Enterprise monitoring and metrics
    """
    
    def __init__(self, config: EventCoordinatorConfig = None):
        """Initialize enterprise event coordinator."""
        self.config = config or EventCoordinatorConfig()
        
        # Event queues by priority
        self.event_queues: Dict[EventPriority, deque] = {
            priority: deque() for priority in EventPriority
        }
        
        # Event handlers and subscriptions
        self.event_handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self.global_handlers: List[EventHandler] = []  # Handlers for all events
        self.subscriptions: Dict[str, EventSubscription] = {}
        
        # Event processing state
        self.processing_events: Dict[str, WorkflowEvent] = {}
        self.completed_events: Dict[str, WorkflowEvent] = {}
        self.failed_events: Dict[str, WorkflowEvent] = {}
        self.dead_letter_queue: deque = deque()
        
        # Handler execution tracking
        self.handler_semaphores: Dict[str, asyncio.Semaphore] = {}
        self.running_handlers: Set[str] = set()
        
        # Batching support
        self.batch_queues: Dict[str, List[WorkflowEvent]] = defaultdict(list)
        self.batch_timers: Dict[str, asyncio.Task] = {}
        
        # Metrics and monitoring
        self.metrics = MetricsCollector() if self.config.enable_metrics else None
        self.logger = logging.getLogger(__name__)
        
        # Event coordinator state
        self._coordinator_active = True
        self._event_processor_task = None
        self._cleanup_task = None
        self._batch_processor_task = None
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background processing tasks."""
        if not self._event_processor_task:
            self._event_processor_task = asyncio.create_task(self._event_processing_loop())
        
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if not self._batch_processor_task:
            self._batch_processor_task = asyncio.create_task(self._batch_processing_loop())
    
    # EVENT PUBLISHING METHODS
    
    async def publish_event(self, event: WorkflowEvent) -> str:
        """Publish an event for processing."""
        # Validate event
        if not event.event_type:
            raise EventCoordinatorException("Event type is required")
        
        # Check queue capacity
        total_queued = sum(len(queue) for queue in self.event_queues.values())
        if total_queued >= self.config.max_event_queue_size:
            raise EventCoordinatorException("Event queue is full")
        
        # Add to priority queue
        self.event_queues[event.priority].append(event)
        
        self.logger.debug(f"Published event {event.event_id} of type {event.event_type.value}")
        
        if self.metrics:
            self.metrics.increment_counter(
                "events_published",
                tags={"event_type": event.event_type.value, "priority": event.priority.name}
            )
        
        return event.event_id
    
    async def publish_workflow_event(
        self,
        event_type: EventType,
        workflow_id: str,
        source: str,
        data: Dict[str, Any] = None,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str = None
    ) -> str:
        """Convenience method to publish workflow events."""
        event = WorkflowEvent(
            event_type=event_type,
            workflow_id=workflow_id,
            source=source,
            data=data or {},
            priority=priority,
            correlation_id=correlation_id
        )
        
        return await self.publish_event(event)
    
    # EVENT HANDLER REGISTRATION
    
    def register_handler(
        self,
        event_types: Union[EventType, List[EventType]],
        handler_func: Callable,
        condition: Optional[Callable] = None,
        priority: int = 0,
        async_execution: bool = True,
        max_concurrent: int = 10,
        timeout_seconds: int = 30
    ) -> str:
        """Register an event handler."""
        if isinstance(event_types, EventType):
            event_types = [event_types]
        
        handler = EventHandler(
            event_types=event_types,
            handler_func=handler_func,
            condition=condition,
            priority=priority,
            async_execution=async_execution,
            max_concurrent=max_concurrent,
            timeout_seconds=timeout_seconds
        )
        
        # Create semaphore for concurrency control
        self.handler_semaphores[handler.handler_id] = asyncio.Semaphore(max_concurrent)
        
        # Register handler for each event type
        for event_type in event_types:
            self.event_handlers[event_type].append(handler)
            # Sort handlers by priority (higher priority first)
            self.event_handlers[event_type].sort(key=lambda h: h.priority, reverse=True)
        
        self.logger.info(f"Registered handler {handler.handler_id} for events {[et.value for et in event_types]}")
        
        return handler.handler_id
    
    def register_global_handler(
        self,
        handler_func: Callable,
        condition: Optional[Callable] = None,
        priority: int = 0,
        async_execution: bool = True,
        max_concurrent: int = 10,
        timeout_seconds: int = 30
    ) -> str:
        """Register a global handler that receives all events."""
        handler = EventHandler(
            event_types=[],  # Empty means all events
            handler_func=handler_func,
            condition=condition,
            priority=priority,
            async_execution=async_execution,
            max_concurrent=max_concurrent,
            timeout_seconds=timeout_seconds
        )
        
        # Create semaphore for concurrency control
        self.handler_semaphores[handler.handler_id] = asyncio.Semaphore(max_concurrent)
        
        self.global_handlers.append(handler)
        self.global_handlers.sort(key=lambda h: h.priority, reverse=True)
        
        self.logger.info(f"Registered global handler {handler.handler_id}")
        
        return handler.handler_id
    
    def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an event handler."""
        # Remove from event-specific handlers
        for event_type, handlers in self.event_handlers.items():
            self.event_handlers[event_type] = [h for h in handlers if h.handler_id != handler_id]
        
        # Remove from global handlers
        self.global_handlers = [h for h in self.global_handlers if h.handler_id != handler_id]
        
        # Remove semaphore
        if handler_id in self.handler_semaphores:
            del self.handler_semaphores[handler_id]
        
        self.logger.info(f"Unregistered handler {handler_id}")
        return True
    
    # EVENT SUBSCRIPTION METHODS
    
    def subscribe(
        self,
        subscriber_id: str,
        event_types: Union[EventType, List[EventType]],
        filters: Dict[str, Any] = None,
        delivery_mode: str = "async",
        batch_size: int = 10,
        batch_timeout_seconds: int = 60
    ) -> str:
        """Subscribe to events."""
        if isinstance(event_types, EventType):
            event_types = [event_types]
        
        subscription = EventSubscription(
            subscriber_id=subscriber_id,
            event_types=event_types,
            filters=filters or {},
            delivery_mode=delivery_mode,
            batch_size=batch_size,
            batch_timeout_seconds=batch_timeout_seconds
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        
        self.logger.info(f"Created subscription {subscription.subscription_id} for {subscriber_id}")
        
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            
            # Cancel any pending batch timer
            if subscription_id in self.batch_timers:
                self.batch_timers[subscription_id].cancel()
                del self.batch_timers[subscription_id]
            
            self.logger.info(f"Removed subscription {subscription_id}")
            return True
        
        return False
    
    # EVENT PROCESSING METHODS
    
    async def _event_processing_loop(self):
        """Main event processing loop."""
        while self._coordinator_active:
            try:
                # Process events by priority
                event_processed = False
                
                for priority in sorted(EventPriority, key=lambda p: p.value, reverse=True):
                    queue = self.event_queues[priority]
                    
                    if queue:
                        event = queue.popleft()
                        await self._process_event(event)
                        event_processed = True
                        break
                
                # Sleep briefly if no events were processed
                if not event_processed:
                    await asyncio.sleep(0.01)
                
            except Exception as e:
                self.logger.error(f"Event processing loop error: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: WorkflowEvent):
        """Process a single event."""
        event.status = EventStatus.PROCESSING
        self.processing_events[event.event_id] = event
        
        try:
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, []).copy()
            handlers.extend(self.global_handlers)
            
            # Filter handlers based on conditions
            applicable_handlers = []
            for handler in handlers:
                if not handler.enabled:
                    continue
                
                if handler.condition and not await self._evaluate_condition(handler.condition, event):
                    continue
                
                applicable_handlers.append(handler)
            
            # Execute handlers
            handler_tasks = []
            for handler in applicable_handlers:
                if handler.async_execution:
                    task = asyncio.create_task(self._execute_handler(handler, event))
                    handler_tasks.append(task)
                else:
                    # Synchronous execution
                    await self._execute_handler(handler, event)
            
            # Wait for all async handlers to complete
            if handler_tasks:
                await asyncio.gather(*handler_tasks, return_exceptions=True)
            
            # Process subscriptions
            await self._process_subscriptions(event)
            
            # Mark event as completed
            event.status = EventStatus.COMPLETED
            self.completed_events[event.event_id] = event
            
            if self.metrics:
                processing_time = (datetime.utcnow() - event.timestamp).total_seconds()
                self.metrics.record_timer(
                    "event_processing_time",
                    processing_time,
                    tags={"event_type": event.event_type.value}
                )
        
        except Exception as e:
            await self._handle_event_failure(event, e)
        
        finally:
            # Remove from processing events
            self.processing_events.pop(event.event_id, None)
    
    async def _execute_handler(self, handler: EventHandler, event: WorkflowEvent):
        """Execute a single event handler."""
        handler_id = handler.handler_id
        semaphore = self.handler_semaphores.get(handler_id)
        
        if not semaphore:
            return
        
        async with semaphore:
            self.running_handlers.add(handler_id)
            
            try:
                # Execute handler with timeout
                await asyncio.wait_for(
                    handler.handler_func(event),
                    timeout=handler.timeout_seconds
                )
                
                if self.metrics:
                    self.metrics.increment_counter(
                        "handler_executions",
                        tags={"handler_id": handler_id, "event_type": event.event_type.value}
                    )
            
            except asyncio.TimeoutError:
                self.logger.warning(f"Handler {handler_id} timed out for event {event.event_id}")
                
                if self.metrics:
                    self.metrics.increment_counter(
                        "handler_timeouts",
                        tags={"handler_id": handler_id}
                    )
            
            except Exception as e:
                self.logger.error(f"Handler {handler_id} failed for event {event.event_id}: {e}")
                
                if self.metrics:
                    self.metrics.increment_counter(
                        "handler_errors",
                        tags={"handler_id": handler_id, "error_type": type(e).__name__}
                    )
            
            finally:
                self.running_handlers.discard(handler_id)
    
    async def _evaluate_condition(self, condition: Callable, event: WorkflowEvent) -> bool:
        """Evaluate handler condition."""
        try:
            if asyncio.iscoroutinefunction(condition):
                return await condition(event)
            else:
                return condition(event)
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            return False
    
    async def _process_subscriptions(self, event: WorkflowEvent):
        """Process event subscriptions."""
        for subscription in self.subscriptions.values():
            if not subscription.enabled:
                continue
            
            # Check if event type matches subscription
            if event.event_type not in subscription.event_types:
                continue
            
            # Apply filters
            if not self._apply_filters(event, subscription.filters):
                continue
            
            # Handle different delivery modes
            if subscription.delivery_mode == "batch":
                await self._add_to_batch(subscription, event)
            else:
                await self._deliver_event(subscription, event)
    
    def _apply_filters(self, event: WorkflowEvent, filters: Dict[str, Any]) -> bool:
        """Apply subscription filters to event."""
        for filter_key, filter_value in filters.items():
            event_value = getattr(event, filter_key, None) or event.data.get(filter_key)
            
            if event_value != filter_value:
                return False
        
        return True
    
    async def _add_to_batch(self, subscription: EventSubscription, event: WorkflowEvent):
        """Add event to batch queue."""
        subscription_id = subscription.subscription_id
        batch_queue = self.batch_queues[subscription_id]
        batch_queue.append(event)
        
        # Start batch timer if not already running
        if subscription_id not in self.batch_timers:
            self.batch_timers[subscription_id] = asyncio.create_task(
                self._batch_timeout(subscription)
            )
        
        # Check if batch is ready
        if len(batch_queue) >= subscription.batch_size:
            await self._deliver_batch(subscription)
    
    async def _batch_timeout(self, subscription: EventSubscription):
        """Handle batch timeout."""
        await asyncio.sleep(subscription.batch_timeout_seconds)
        await self._deliver_batch(subscription)
    
    async def _deliver_batch(self, subscription: EventSubscription):
        """Deliver a batch of events."""
        subscription_id = subscription.subscription_id
        batch_queue = self.batch_queues[subscription_id]
        
        if not batch_queue:
            return
        
        # Get events to deliver
        events_to_deliver = batch_queue.copy()
        batch_queue.clear()
        
        # Cancel timer
        if subscription_id in self.batch_timers:
            self.batch_timers[subscription_id].cancel()
            del self.batch_timers[subscription_id]
        
        # Deliver batch
        # Implementation would deliver to subscriber
        self.logger.debug(f"Delivered batch of {len(events_to_deliver)} events to {subscription.subscriber_id}")
    
    async def _deliver_event(self, subscription: EventSubscription, event: WorkflowEvent):
        """Deliver single event to subscriber."""
        # Implementation would deliver to subscriber
        self.logger.debug(f"Delivered event {event.event_id} to {subscription.subscriber_id}")
    
    async def _handle_event_failure(self, event: WorkflowEvent, error: Exception):
        """Handle event processing failure."""
        event.retry_count += 1
        
        if event.retry_count <= event.max_retries:
            # Retry event
            event.status = EventStatus.RETRYING
            
            # Add back to queue with delay
            await asyncio.sleep(2 ** event.retry_count)  # Exponential backoff
            self.event_queues[event.priority].append(event)
            
            self.logger.info(f"Retrying event {event.event_id} (attempt {event.retry_count})")
        else:
            # Move to dead letter queue
            event.status = EventStatus.FAILED
            self.failed_events[event.event_id] = event
            
            if self.config.dead_letter_queue_enabled:
                self.dead_letter_queue.append(event)
            
            self.logger.error(f"Event {event.event_id} failed permanently: {error}")
            
            if self.metrics:
                self.metrics.increment_counter(
                    "events_failed",
                    tags={"event_type": event.event_type.value}
                )
    
    # BACKGROUND TASKS
    
    async def _cleanup_loop(self):
        """Background cleanup task."""
        while self._coordinator_active:
            try:
                await self._cleanup_old_events()
                await asyncio.sleep(self.config.cleanup_interval_seconds)
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def _batch_processing_loop(self):
        """Background batch processing task."""
        while self._coordinator_active:
            try:
                # Process any pending batches
                for subscription in self.subscriptions.values():
                    if subscription.delivery_mode == "batch":
                        batch_queue = self.batch_queues[subscription.subscription_id]
                        if batch_queue:
                            await self._deliver_batch(subscription)
                
                await asyncio.sleep(self.config.batch_processing_interval_seconds)
            except Exception as e:
                self.logger.error(f"Batch processing loop error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_events(self):
        """Clean up old completed and failed events."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean up completed events
        old_completed = [
            event_id for event_id, event in self.completed_events.items()
            if event.timestamp < cutoff_time
        ]
        for event_id in old_completed:
            del self.completed_events[event_id]
        
        # Clean up failed events
        old_failed = [
            event_id for event_id, event in self.failed_events.items()
            if event.timestamp < cutoff_time
        ]
        for event_id in old_failed:
            del self.failed_events[event_id]
        
        # Clean up dead letter queue
        while (self.dead_letter_queue and 
               self.dead_letter_queue[0].timestamp < cutoff_time):
            self.dead_letter_queue.popleft()
    
    # STATUS AND MANAGEMENT METHODS
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get event coordinator status."""
        return {
            'active': self._coordinator_active,
            'queued_events': {
                priority.name: len(queue) 
                for priority, queue in self.event_queues.items()
            },
            'processing_events': len(self.processing_events),
            'completed_events': len(self.completed_events),
            'failed_events': len(self.failed_events),
            'dead_letter_queue': len(self.dead_letter_queue),
            'registered_handlers': sum(len(handlers) for handlers in self.event_handlers.values()),
            'global_handlers': len(self.global_handlers),
            'active_subscriptions': len([s for s in self.subscriptions.values() if s.enabled]),
            'running_handlers': len(self.running_handlers)
        }
    
    async def shutdown(self):
        """Shutdown event coordinator."""
        self._coordinator_active = False
        
        # Cancel background tasks
        if self._event_processor_task:
            self._event_processor_task.cancel()
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        if self._batch_processor_task:
            self._batch_processor_task.cancel()
        
        # Cancel batch timers
        for timer_task in self.batch_timers.values():
            timer_task.cancel()
        
        self.logger.info("Event coordinator shutdown completed")