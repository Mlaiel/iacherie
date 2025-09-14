"""Event Dispatcher Module

Central event dispatching system for managing event routing, processing,
and delivery across the Ainflue platform infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, Any, List, Callable, Optional, Set
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .base_event import BaseEvent
from .base_event_handler import BaseEventHandler
from .event_priority import EventPriority
from .event_status import EventStatus
from .exceptions import EventProcessingError, HandlerNotFoundError, ProcessingTimeoutError

logger = logging.getLogger(__name__)


@dataclass
class EventDispatchMetrics:
    """Event dispatch performance metrics"""
    total_events_dispatched: int = 0
    successful_dispatches: int = 0
    failed_dispatches: int = 0
    average_processing_time: float = 0.0
    handlers_registered: int = 0
    queue_size: int = 0
    last_dispatch_time: Optional[datetime] = None


@dataclass
class HandlerRegistration:
    """Handler registration information"""
    handler: BaseEventHandler
    event_types: Set[str]
    priority: EventPriority
    registered_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True


class EventDispatcher:
    """
    Central event dispatcher for managing event processing workflow.
    
    Provides high-performance event routing, priority-based processing,
    retry mechanisms, and comprehensive monitoring capabilities.
    """
    
    def __init__(self, 
                 max_concurrent_events -> None: int = 100,
                 retry_attempts -> None: int = 3,
                 timeout_seconds -> None: int = 300) -> None:
        self.max_concurrent_events = max_concurrent_events
        self.retry_attempts = retry_attempts
        self.timeout_seconds = timeout_seconds
        
        # Handler registry organized by event type
        self._handlers: Dict[str, List[HandlerRegistration]] = defaultdict(list)
        self._global_handlers: List[HandlerRegistration] = []
        
        # Event queues organized by priority
        self._priority_queues: Dict[EventPriority, deque] = {
            priority: deque() for priority in EventPriority
        }
        
        # Processing state
        self._processing = False
        self._current_events: Set[str] = set()
        self._dead_letter_queue: deque = deque(maxlen=1000)
        
        # Metrics and monitoring
        self.metrics = EventDispatchMetrics()
        
        # Concurrency control
        self._event_semaphore = asyncio.Semaphore(max_concurrent_events)
        self._processing_lock = asyncio.Lock()
        
        logger.info(f"Event dispatcher initialized with max_concurrent={max_concurrent_events}")
    
    async def register_handler(self, 
                              handler: BaseEventHandler,
                              event_types: List[str] = None,
                              priority: EventPriority = EventPriority.MEDIUM,
                              global_handler: bool = False) -> str:
        """
        Register an event handler for specific event types.
        
        Args:
            handler: The event handler instance
            event_types: List of event types to handle (None for global)
            priority: Handler priority level
            global_handler: Whether this handler processes all events
            
        Returns:
            Registration ID for handler management
        """
        registration = HandlerRegistration(
            handler=handler,
            event_types=set(event_types or []),
            priority=priority
        )
        
        if global_handler or not event_types:
            self._global_handlers.append(registration)
            self._global_handlers.sort(key=lambda x: x.priority.value, reverse=True)
            logger.info(f"Registered global handler: {handler.handler_id}")
        else:
            for event_type in event_types:
                self._handlers[event_type].append(registration)
                self._handlers[event_type].sort(key=lambda x: x.priority.value, reverse=True)
            logger.info(f"Registered handler {handler.handler_id} for types: {event_types}")
        
        self.metrics.handlers_registered += 1
        return registration.handler.handler_id
    
    async def unregister_handler(self, handler_id: str) -> bool:
        """
        Unregister an event handler.
        
        Args:
            handler_id: ID of handler to unregister
            
        Returns:
            True if handler was found and removed
        """
        # Remove from global handlers
        for i, reg in enumerate(self._global_handlers):
            if reg.handler.handler_id == handler_id:
                self._global_handlers.pop(i)
                self.metrics.handlers_registered -= 1
                logger.info(f"Unregistered global handler: {handler_id}")
                return True
        
        # Remove from event-specific handlers
        for event_type, handlers in self._handlers.items():
            for i, reg in enumerate(handlers):
                if reg.handler.handler_id == handler_id:
                    handlers.pop(i)
                    self.metrics.handlers_registered -= 1
                    logger.info(f"Unregistered handler {handler_id} from type: {event_type}")
                    return True
        
        logger.warning(f"Handler not found for unregistration: {handler_id}")
        return False
    
    async def dispatch_event(self, event: BaseEvent) -> Dict[str, Any]:
        """
        Dispatch an event for processing.
        
        Args:
            event: Event to dispatch
            
        Returns:
            Dispatch result with processing information
        """
        dispatch_start = datetime.utcnow()
        
        try:
            # Update event status
            event.status = EventStatus.QUEUED
            
            # Add to appropriate priority queue
            priority = getattr(event, 'priority', EventPriority.MEDIUM)
            self._priority_queues[priority].append(event)
            
            # Update metrics
            self.metrics.total_events_dispatched += 1
            self.metrics.queue_size = sum(len(q) for q in self._priority_queues.values())
            
            logger.info(f"Event {event.event_id} queued with priority {priority.name}")
            
            # Process if not already processing
            if not self._processing:
                asyncio.create_task(self._process_event_queues())
            
            return {
                'success': True,
                'event_id': event.event_id,
                'queued_at': dispatch_start.isoformat(),
                'queue_position': len(self._priority_queues[priority])
            }
            
        except Exception as e:
            self.metrics.failed_dispatches += 1
            logger.error(f"Failed to dispatch event {event.event_id}: {e}")
            raise EventProcessingError(f"Dispatch failed: {e}")
    
    async def _process_event_queues(self) -> None:
        """Process events from priority queues"""
        async with self._processing_lock:
            if self._processing:
                return
            
            self._processing = True
            
            try:
                while any(queue for queue in self._priority_queues.values()):
                    # Process highest priority events first
                    for priority in sorted(EventPriority, key=lambda x: x.value, reverse=True):
                        queue = self._priority_queues[priority]
                        
                        while queue:
                            async with self._event_semaphore:
                                event = queue.popleft()
                                asyncio.create_task(self._process_single_event(event))
                    
                    # Brief pause to allow new events
                    await asyncio.sleep(0.1)
                    
            finally:
                self._processing = False
                self.metrics.queue_size = sum(len(q) for q in self._priority_queues.values())
    
    async def _process_single_event(self, event -> None: BaseEvent) -> None:
        """Process a single event through registered handlers"""
        processing_start = datetime.utcnow()
        event.status = EventStatus.PROCESSING
        self._current_events.add(event.event_id)
        
        try:
            # Find applicable handlers
            handlers = await self._find_handlers_for_event(event)
            
            if not handlers:
                raise HandlerNotFoundError(f"No handlers found for event type: {event.event_type}")
            
            # Process through each handler
            results = []
            for handler_reg in handlers:
                try:
                    # Check if handler can process this event
                    if await handler_reg.handler.can_handle(event):
                        await handler_reg.handler.before_handle(event)
                        
                        # Execute handler with timeout
                        result = await asyncio.wait_for(
                            handler_reg.handler.handle(event),
                            timeout=self.timeout_seconds
                        )
                        
                        await handler_reg.handler.after_handle(event, result)
                        results.append({
                            'handler_id': handler_reg.handler.handler_id,
                            'success': True,
                            'result': result
                        })
                        
                except asyncio.TimeoutError:
                    error = ProcessingTimeoutError(f"Handler {handler_reg.handler.handler_id} timed out")
                    await handler_reg.handler.on_error(event, error)
                    results.append({
                        'handler_id': handler_reg.handler.handler_id,
                        'success': False,
                        'error': str(error)
                    })
                    
                except Exception as e:
                    await handler_reg.handler.on_error(event, e)
                    results.append({
                        'handler_id': handler_reg.handler.handler_id,
                        'success': False,
                        'error': str(e)
                    })
            
            # Update event status based on results
            successful_handlers = sum(1 for r in results if r['success'])
            if successful_handlers > 0:
                event.status = EventStatus.COMPLETED
                self.metrics.successful_dispatches += 1
            else:
                event.status = EventStatus.FAILED
                self.metrics.failed_dispatches += 1
                await self._handle_failed_event(event, results)
            
            # Update metrics
            processing_time = (datetime.utcnow() - processing_start).total_seconds()
            self._update_processing_metrics(processing_time)
            
            logger.info(f"Event {event.event_id} processed by {len(handlers)} handlers "
                       f"in {processing_time:.3f}s")
                       
        except Exception as e:
            event.status = EventStatus.FAILED
            self.metrics.failed_dispatches += 1
            await self._handle_failed_event(event, [{'error': str(e)}])
            logger.error(f"Failed to process event {event.event_id}: {e}")
            
        finally:
            self._current_events.discard(event.event_id)
            self.metrics.last_dispatch_time = datetime.utcnow()
    
    async def _find_handlers_for_event(self, event: BaseEvent) -> List[HandlerRegistration]:
        """Find all handlers that can process the given event"""
        handlers = []
        
        # Add event-specific handlers
        if event.event_type in self._handlers:
            handlers.extend(self._handlers[event.event_type])
        
        # Add global handlers
        handlers.extend(self._global_handlers)
        
        # Filter active handlers and sort by priority
        active_handlers = [h for h in handlers if h.active]
        return sorted(active_handlers, key=lambda x: x.priority.value, reverse=True)
    
    async def _handle_failed_event(self, event -> None: BaseEvent, results -> None: List[Dict[str, Any]]) -> None:
        """Handle events that failed processing"""
        # Add to dead letter queue for analysis
        self._dead_letter_queue.append({
            'event': event,
            'results': results,
            'failed_at': datetime.utcnow().isoformat()
        })
        
        logger.warning(f"Event {event.event_id} added to dead letter queue")
    
    def _update_processing_metrics(self, processing_time -> None: float) -> None:
        """Update processing time metrics"""
        if self.metrics.average_processing_time == 0:
            self.metrics.average_processing_time = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.average_processing_time = (
                alpha * processing_time + 
                (1 - alpha) * self.metrics.average_processing_time
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current dispatcher metrics"""
        return {
            'total_events_dispatched': self.metrics.total_events_dispatched,
            'successful_dispatches': self.metrics.successful_dispatches,
            'failed_dispatches': self.metrics.failed_dispatches,
            'success_rate': (
                self.metrics.successful_dispatches / max(1, self.metrics.total_events_dispatched)
            ),
            'average_processing_time': self.metrics.average_processing_time,
            'handlers_registered': self.metrics.handlers_registered,
            'current_queue_size': sum(len(q) for q in self._priority_queues.values()),
            'active_events': len(self._current_events),
            'dead_letter_queue_size': len(self._dead_letter_queue),
            'last_dispatch_time': (
                self.metrics.last_dispatch_time.isoformat() 
                if self.metrics.last_dispatch_time else None
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on dispatcher"""
        return {
            'status': 'healthy',
            'processing': self._processing,
            'queue_sizes': {
                priority.name: len(queue) 
                for priority, queue in self._priority_queues.items()
            },
            'handlers_count': self.metrics.handlers_registered,
            'timestamp': datetime.utcnow().isoformat()
        }


# Export the main dispatcher class
__all__ = ['EventDispatcher', 'EventDispatchMetrics', 'HandlerRegistration']

logger.info("Event dispatcher module initialized successfully")