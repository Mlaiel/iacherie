"""
Event Dispatcher module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Event Dispatcher - Utils Module - Enterprise Implementation

© 2025 Fahed Mlaiel. All rights reserved.
This software and associated documentation files are proprietary and confidential.
Unauthorized copying, distribution, or modification is strictly prohibited.
Licensed under Enterprise Commercial License.

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Developer & AI Architect - Event-driven architecture and real-time processing
Backend Senior Engineer - Event handling and message dispatching
Microservices Architect - Inter-service communication and event routing
DevOps Engineer - Event monitoring and performance optimization

⚠️ STRICT WARNING: Any attempt to steal, copy, or use this concept, idea, or code
without written personal authorization from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import weakref
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
    EMERGENCY = 5

class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class DeliveryMode(Enum):
    """Event delivery modes"""
    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    GUARANTEED = "guaranteed"

@dataclass
class Event:
    """Event data structure"""
    id: str
    event_type: str
    source: str
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    expires_at: Optional[datetime] = None

@dataclass
class EventHandler:
    """Event handler configuration"""
    handler_id: str
    handler_function: Callable
    event_types: Set[str]
    priority: int = 0
    is_async: bool = True
    timeout_seconds: int = 30
    max_concurrent: int = 10
    retry_on_failure: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventExecution:
    """Event execution record"""
    execution_id: str
    event_id: str
    handler_id: str
    status: EventStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None

@dataclass
class EventFilter:
    """Event filtering configuration"""
    event_types: Optional[Set[str]] = None
    sources: Optional[Set[str]] = None
    priority_levels: Optional[Set[EventPriority]] = None
    user_ids: Optional[Set[str]] = None
    metadata_filters: Dict[str, Any] = field(default_factory=dict)

class EventDispatcher:
    """
    Enterprise event dispatcher for real-time event handling,
    message routing, and asynchronous communication
    """
    
    def __init__(self, max_queue_size -> None: int = 10000) -> None:
        self.handlers: Dict[str, EventHandler] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.executions: Dict[str, EventExecution] = {}
        self.metrics: Dict[str, Any] = defaultdict(int)
        
        # Event routing
        self.event_type_handlers: Dict[str, List[str]] = defaultdict(list)
        self.wildcard_handlers: List[str] = []
        
        # Processing state
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []
        self.max_workers = 10
        
        # Dead letter queue
        self.dead_letter_queue: List[Event] = []
        self.max_dead_letter_size = 1000
        
        # Event filters
        self.global_filters: List[EventFilter] = []
        
        logger.info("EventDispatcher initialized")
    
    async def initialize_dispatcher(self) -> bool:
        """Initialize event dispatcher"""
        try:
            logger.info("Initializing event dispatcher...")
            
            # Start processing workers
            await self.start_processing()
            
            # Setup monitoring
            await self._setup_monitoring()
            
            logger.info("Event dispatcher initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize event dispatcher: {e}")
            return False
    
    async def register_handler(self, handler: EventHandler) -> bool:
        """Register an event handler"""
        try:
            logger.info(f"Registering event handler: {handler.handler_id}")
            
            # Validate handler
            if not callable(handler.handler_function):
                raise ValueError(f"Handler function for {handler.handler_id} is not callable")
            
            # Store handler
            self.handlers[handler.handler_id] = handler
            
            # Register for event types
            for event_type in handler.event_types:
                if event_type == "*":
                    self.wildcard_handlers.append(handler.handler_id)
                else:
                    self.event_type_handlers[event_type].append(handler.handler_id)
            
            logger.info(f"Event handler {handler.handler_id} registered for types: {handler.event_types}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register event handler {handler.handler_id}: {e}")
            return False
    
    async def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an event handler"""
        try:
            if handler_id not in self.handlers:
                logger.warning(f"Handler {handler_id} not found")
                return False
            
            handler = self.handlers[handler_id]
            
            # Remove from event type mappings
            for event_type in handler.event_types:
                if event_type == "*":
                    if handler_id in self.wildcard_handlers:
                        self.wildcard_handlers.remove(handler_id)
                else:
                    if handler_id in self.event_type_handlers[event_type]:
                        self.event_type_handlers[event_type].remove(handler_id)
            
            # Remove handler
            del self.handlers[handler_id]
            
            logger.info(f"Event handler {handler_id} unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister event handler {handler_id}: {e}")
            return False
    
    async def dispatch_event(self, event: Event) -> str:
        """Dispatch an event for processing"""
        try:
            # Apply global filters
            if not self._passes_filters(event):
                logger.debug(f"Event {event.id} filtered out")
                return event.id
            
            # Set expiration if not set
            if not event.expires_at and event.timeout_seconds > 0:
                event.expires_at = datetime.now(timezone.utc) + timedelta(seconds=event.timeout_seconds)
            
            # Add to queue
            await self.event_queue.put(event)
            
            # Update metrics
            self.metrics['events_dispatched'] += 1
            self.metrics[f'events_by_type_{event.event_type}'] += 1
            self.metrics[f'events_by_priority_{event.priority.name}'] += 1
            
            logger.debug(f"Event dispatched: {event.id} (type: {event.event_type})")
            return event.id
            
        except asyncio.QueueFull:
            logger.error(f"Event queue full, dropping event: {event.id}")
            self.metrics['events_dropped'] += 1
            return event.id
        except Exception as e:
            logger.error(f"Failed to dispatch event {event.id}: {e}")
            self.metrics['events_failed'] += 1
            return event.id
    
    async def emit_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: str = "unknown",
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    ) -> str:
        """Emit a new event"""
        try:
            event = Event(
                id=str(uuid.uuid4()),
                event_type=event_type,
                source=source,
                data=data,
                priority=priority,
                correlation_id=correlation_id,
                user_id=user_id,
                delivery_mode=delivery_mode
            )
            
            return await self.dispatch_event(event)
            
        except Exception as e:
            logger.error(f"Failed to emit event {event_type}: {e}")
            raise
    
    async def start_processing(self) -> bool:
        """Start event processing workers"""
        try:
            if self.is_running:
                logger.warning("Event processing is already running")
                return True
            
            logger.info("Starting event processing workers...")
            self.is_running = True
            
            # Start worker tasks
            for i in range(self.max_workers):
                worker_task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
                self.worker_tasks.append(worker_task)
            
            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitoring_loop())
            self.worker_tasks.append(monitor_task)
            
            logger.info(f"Started {self.max_workers} event processing workers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start event processing: {e}")
            return False
    
    async def stop_processing(self) -> bool:
        """Stop event processing workers"""
        try:
            logger.info("Stopping event processing workers...")
            
            self.is_running = False
            
            # Cancel all worker tasks
            for task in self.worker_tasks:
                task.cancel()
            
            # Wait for workers to finish
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            self.worker_tasks.clear()
            
            logger.info("Event processing workers stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop event processing: {e}")
            return False
    
    async def get_dispatcher_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dispatcher metrics"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Calculate recent metrics
            time_window = timedelta(minutes=5)
            recent_executions = [
                exec for exec in self.executions.values()
                if current_time - exec.start_time <= time_window
            ]
            
            successful_recent = len([e for e in recent_executions if e.status == EventStatus.COMPLETED])
            failed_recent = len([e for e in recent_executions if e.status == EventStatus.FAILED])
            
            success_rate = (successful_recent / len(recent_executions) * 100) if recent_executions else 0
            
            # Average processing time
            completed_executions = [e for e in recent_executions if e.processing_time_ms is not None]
            avg_processing_time = 0
            if completed_executions:
                avg_processing_time = sum(e.processing_time_ms for e in completed_executions) / len(completed_executions)
            
            return {
                'dispatcher_status': 'running' if self.is_running else 'stopped',
                'active_workers': len(self.worker_tasks),
                'registered_handlers': len(self.handlers),
                'queue_size': self.event_queue.qsize(),
                'dead_letter_queue_size': len(self.dead_letter_queue),
                'total_metrics': dict(self.metrics),
                'recent_metrics': {
                    'total_executions': len(recent_executions),
                    'successful_executions': successful_recent,
                    'failed_executions': failed_recent,
                    'success_rate': round(success_rate, 2),
                    'average_processing_time_ms': round(avg_processing_time, 2)
                },
                'handler_info': {
                    handler_id: {
                        'event_types': list(handler.event_types),
                        'priority': handler.priority,
                        'max_concurrent': handler.max_concurrent
                    }
                    for handler_id, handler in self.handlers.items()
                },
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dispatcher metrics: {e}")
            return {'error': str(e)}
    
    async def add_filter(self, event_filter: EventFilter) -> bool:
        """Add a global event filter"""
        try:
            self.global_filters.append(event_filter)
            logger.info(f"Added global event filter: {event_filter}")
            return True
        except Exception as e:
            logger.error(f"Failed to add event filter: {e}")
            return False
    
    async def get_event_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific event"""
        try:
            executions = [e for e in self.executions.values() if e.event_id == event_id]
            
            if not executions:
                return None
            
            return {
                'event_id': event_id,
                'executions': [
                    {
                        'execution_id': exec.execution_id,
                        'handler_id': exec.handler_id,
                        'status': exec.status.value,
                        'start_time': exec.start_time.isoformat(),
                        'end_time': exec.end_time.isoformat() if exec.end_time else None,
                        'processing_time_ms': exec.processing_time_ms,
                        'error_message': exec.error_message
                    }
                    for exec in executions
                ],
                'total_executions': len(executions),
                'successful_executions': len([e for e in executions if e.status == EventStatus.COMPLETED]),
                'failed_executions': len([e for e in executions if e.status == EventStatus.FAILED])
            }
            
        except Exception as e:
            logger.error(f"Failed to get event status for {event_id}: {e}")
            return None
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    async def _worker_loop(self, worker_id -> None: str) -> None:
        """Worker loop for processing events"""
        logger.info(f"Event worker {worker_id} started")
        
        while self.is_running:
            try:
                # Get event from queue with timeout
                try:
                    event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Check if event has expired
                if event.expires_at and datetime.now(timezone.utc) > event.expires_at:
                    logger.warning(f"Event {event.id} expired, moving to dead letter queue")
                    await self._handle_dead_letter(event, "Event expired")
                    continue
                
                # Find handlers for this event
                handlers = await self._find_handlers_for_event(event)
                
                if not handlers:
                    logger.debug(f"No handlers found for event {event.id} (type: {event.event_type})")
                    continue
                
                # Process event with all handlers
                await self._process_event_with_handlers(event, handlers)
                
            except Exception as e:
                logger.error(f"Error in worker {worker_id}: {e}")
                await asyncio.sleep(1)  # Brief pause on error
        
        logger.info(f"Event worker {worker_id} stopped")
    
    async def _find_handlers_for_event(self, event: Event) -> List[EventHandler]:
        """Find all handlers that should process this event"""
        handler_ids = set()
        
        # Add specific event type handlers
        handler_ids.update(self.event_type_handlers.get(event.event_type, []))
        
        # Add wildcard handlers
        handler_ids.update(self.wildcard_handlers)
        
        # Return handler objects sorted by priority
        handlers = [self.handlers[hid] for hid in handler_ids if hid in self.handlers]
        return sorted(handlers, key=lambda h: h.priority, reverse=True)
    
    async def _process_event_with_handlers(self, event -> None: Event, handlers -> None: List[EventHandler]) -> None:
        """Process event with all applicable handlers"""
        tasks = []
        
        for handler in handlers:
            # Create execution record
            execution = EventExecution(
                execution_id=str(uuid.uuid4()),
                event_id=event.id,
                handler_id=handler.handler_id,
                status=EventStatus.PENDING,
                start_time=datetime.now(timezone.utc)
            )
            
            self.executions[execution.execution_id] = execution
            
            # Create task for handler execution
            task = asyncio.create_task(
                self._execute_handler(event, handler, execution)
            )
            tasks.append(task)
        
        # Wait for all handlers to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_handler(self, event -> None: Event, handler -> None: EventHandler, execution -> None: EventExecution) -> None:
        """Execute a single event handler"""
        try:
            execution.status = EventStatus.PROCESSING
            start_time = time.time()
            
            # Prepare handler arguments
            handler_args = {
                'event': event,
                'event_data': event.data,
                'event_type': event.event_type,
                'source': event.source,
                'correlation_id': event.correlation_id,
                'user_id': event.user_id,
                'metadata': event.metadata
            }
            
            # Execute handler with timeout
            if handler.is_async:
                result = await asyncio.wait_for(
                    handler.handler_function(**handler_args),
                    timeout=handler.timeout_seconds
                )
            else:
                # Run sync handler in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: handler.handler_function(**handler_args)
                )
            
            # Record successful execution
            execution.status = EventStatus.COMPLETED
            execution.result = result
            execution.end_time = datetime.now(timezone.utc)
            execution.processing_time_ms = (time.time() - start_time) * 1000
            
            self.metrics['events_processed'] += 1
            self.metrics[f'handler_{handler.handler_id}_success'] += 1
            
            logger.debug(f"Handler {handler.handler_id} processed event {event.id} successfully")
            
        except asyncio.TimeoutError:
            execution.status = EventStatus.TIMEOUT
            execution.error_message = f"Handler timed out after {handler.timeout_seconds}s"
            execution.end_time = datetime.now(timezone.utc)
            
            self.metrics['events_timeout'] += 1
            self.metrics[f'handler_{handler.handler_id}_timeout'] += 1
            
            logger.warning(f"Handler {handler.handler_id} timed out processing event {event.id}")
            
        except Exception as e:
            execution.status = EventStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now(timezone.utc)
            
            self.metrics['events_failed'] += 1
            self.metrics[f'handler_{handler.handler_id}_failed'] += 1
            
            logger.error(f"Handler {handler.handler_id} failed processing event {event.id}: {e}")
            
            # Handle retry logic
            if handler.retry_on_failure and event.retry_count < event.max_retries:
                event.retry_count += 1
                logger.info(f"Retrying event {event.id} (attempt {event.retry_count}/{event.max_retries})")
                await asyncio.sleep(2 ** event.retry_count)  # Exponential backoff
                await self.event_queue.put(event)
            else:
                await self._handle_dead_letter(event, f"Handler failed: {e}")
    
    async def _handle_dead_letter(self, event -> None: Event, reason -> None: str) -> None:
        """Handle events that cannot be processed"""
        try:
            if len(self.dead_letter_queue) >= self.max_dead_letter_size:
                # Remove oldest event
                self.dead_letter_queue.pop(0)
            
            # Add to dead letter queue with reason
            event.metadata['dead_letter_reason'] = reason
            event.metadata['dead_letter_timestamp'] = datetime.now(timezone.utc).isoformat()
            self.dead_letter_queue.append(event)
            
            self.metrics['events_dead_lettered'] += 1
            logger.warning(f"Event {event.id} moved to dead letter queue: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to handle dead letter event {event.id}: {e}")
    
    def _passes_filters(self, event: Event) -> bool:
        """Check if event passes all global filters"""
        for event_filter in self.global_filters:
            if not self._event_matches_filter(event, event_filter):
                return False
        return True
    
    def _event_matches_filter(self, event: Event, event_filter: EventFilter) -> bool:
        """Check if event matches a specific filter"""
        # Check event types
        if event_filter.event_types and event.event_type not in event_filter.event_types:
            return False
        
        # Check sources
        if event_filter.sources and event.source not in event_filter.sources:
            return False
        
        # Check priority levels
        if event_filter.priority_levels and event.priority not in event_filter.priority_levels:
            return False
        
        # Check user IDs
        if event_filter.user_ids and event.user_id not in event_filter.user_ids:
            return False
        
        # Check metadata filters
        for key, value in event_filter.metadata_filters.items():
            if key not in event.metadata or event.metadata[key] != value:
                return False
        
        return True
    
    async def _monitoring_loop(self) -> None:
        """Monitoring loop for cleanup and metrics"""
        logger.info("Event dispatcher monitoring loop started")
        
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Clean up old executions (older than 24 hours)
                cutoff_time = current_time - timedelta(hours=24)
                old_executions = [
                    exec_id for exec_id, exec in self.executions.items()
                    if exec.start_time < cutoff_time
                ]
                
                for exec_id in old_executions:
                    del self.executions[exec_id]
                
                if old_executions:
                    logger.debug(f"Cleaned up {len(old_executions)} old executions")
                
                # Log metrics periodically
                if self.metrics['events_dispatched'] > 0:
                    logger.info(f"Event metrics - Dispatched: {self.metrics['events_dispatched']}, "
                              f"Processed: {self.metrics['events_processed']}, "
                              f"Failed: {self.metrics['events_failed']}, "
                              f"Queue size: {self.event_queue.qsize()}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
        
        logger.info("Event dispatcher monitoring loop stopped")

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def example_event_dispatching() -> None:
    """Example usage of EventDispatcher"""
    try:
        # Initialize dispatcher
        dispatcher = EventDispatcher(max_queue_size=1000)
        await dispatcher.initialize_dispatcher()
        
        # Define event handlers
        async def content_upload_handler(event_data, **kwargs) -> None:
            content_id = event_data.get('content_id')
            logger.info(f"Processing content upload: {content_id}")
            await asyncio.sleep(1)  # Simulate processing
            return {'processed': True, 'content_id': content_id}
        
        async def user_activity_handler(event_data, **kwargs) -> None:
            user_id = event_data.get('user_id')
            activity = event_data.get('activity')
            logger.info(f"Recording user activity: {user_id} - {activity}")
            await asyncio.sleep(0.5)  # Simulate processing
            return {'recorded': True, 'user_id': user_id}
        
        async def audit_handler(event_data, **kwargs) -> None:
            logger.info(f"Audit log: {event_data}")
            await asyncio.sleep(0.1)  # Simulate logging
            return {'audited': True}
        
        # Register handlers
        content_handler = EventHandler(
            handler_id="content_processor",
            handler_function=content_upload_handler,
            event_types={"content.uploaded", "content.updated"},
            priority=1
        )
        
        activity_handler = EventHandler(
            handler_id="activity_tracker",
            handler_function=user_activity_handler,
            event_types={"user.login", "user.action"},
            priority=2
        )
        
        audit_handler_config = EventHandler(
            handler_id="audit_logger",
            handler_function=audit_handler,
            event_types={"*"},  # Handle all events
            priority=0
        )
        
        await dispatcher.register_handler(content_handler)
        await dispatcher.register_handler(activity_handler)
        await dispatcher.register_handler(audit_handler_config)
        
        # Emit some events
        event1_id = await dispatcher.emit_event(
            event_type="content.uploaded",
            data={"content_id": "content_123", "user_id": "user_456", "file_size": 1024000},
            source="content_service",
            priority=EventPriority.HIGH
        )
        
        event2_id = await dispatcher.emit_event(
            event_type="user.login",
            data={"user_id": "user_456", "ip_address": "192.168.1.100", "device": "mobile"},
            source="auth_service",
            priority=EventPriority.NORMAL
        )
        
        event3_id = await dispatcher.emit_event(
            event_type="user.action",
            data={"user_id": "user_456", "activity": "like_content", "target_id": "content_123"},
            source="interaction_service",
            priority=EventPriority.LOW
        )
        
        # Wait for processing
        await asyncio.sleep(5)
        
        # Get metrics
        metrics = await dispatcher.get_dispatcher_metrics()
        logger.info(f"Dispatcher metrics: {json.dumps(metrics, indent=2)}")
        
        # Get event status
        for event_id in [event1_id, event2_id, event3_id]:
            status = await dispatcher.get_event_status(event_id)
            if status:
                logger.info(f"Event {event_id} status: {json.dumps(status, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Example event dispatching failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(example_event_dispatching())