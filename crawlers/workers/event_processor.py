"""
Event Processor Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/event_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Event Processing System
Responsibility: Real-time event processing and workflow orchestration
Technologies: AsyncIO, Event Sourcing, CQRS, WebSockets, Message Queues
================================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Event ingestion → Event validation → Event routing → 
Processing pipeline → State management → Notification → Audit trail
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, Generic, TypeVar
import logging
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import weakref
from contextlib import asynccontextmanager
import threading
from concurrent.futures import ThreadPoolExecutor

from .crawler_worker import CrawlerTask, TaskResult, CrawlerWorker
from .worker_pool import WorkerPool
from ...monitoring.performance_monitor import PerformanceMonitor
from ...security.access_control import AccessControl
from ...utils.json_utils import JsonUtils
from ...core.events.event_bus import EventBus, Event
from ...ai.content_protection.fingerprint_engine import FingerprintEngine

logger = logging.getLogger(__name__)

T = TypeVar('T')


class EventType(Enum):
    """Types of events in the system"""
    WORKER_STARTED = "worker_started"
    WORKER_STOPPED = "worker_stopped"
    WORKER_STATUS_CHANGED = "worker_status_changed"
    TASK_SUBMITTED = "task_submitted"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_RETRY = "task_retry"
    RESOURCE_ALLOCATED = "resource_allocated"
    RESOURCE_DEALLOCATED = "resource_deallocated"
    RESOURCE_SHORTAGE = "resource_shortage"
    SCALING_EVENT = "scaling_event"
    PERFORMANCE_ALERT = "performance_alert"
    SECURITY_EVENT = "security_event"
    CONTENT_PROTECTED = "content_protected"
    FINGERPRINT_GENERATED = "fingerprint_generated"
    VIOLATION_DETECTED = "violation_detected"
    SYSTEM_ERROR = "system_error"


class EventPriority(Enum):
    """Event processing priorities"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class ProcessingMode(Enum):
    """Event processing modes"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"
    PARALLEL = "parallel"


@dataclass
class WorkerEvent:
    """Worker system event"""
    event_id: str
    event_type: EventType
    source: str
    target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    version: int = 1
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class EventProcessingResult:
    """Result of event processing"""
    event_id: str
    status: EventStatus
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None


@dataclass
class EventHandler:
    """Event handler registration"""
    handler_id: str
    event_types: List[EventType]
    handler_func: Callable[[WorkerEvent], Any]
    priority: int = 100
    filter_func: Optional[Callable[[WorkerEvent], bool]] = None
    is_async: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30


class EventProcessor:
    """
    High-performance event processor for worker system
    
    Features:
    - Real-time event processing
    - Event sourcing and CQRS patterns
    - Prioritized event queues
    - Handler registration and routing
    - Retry mechanisms with backoff
    - Event correlation and causation
    - Performance monitoring
    """

    def __init__(self, processor_id: str = None, max_concurrent_events: int = 100):
        self.processor_id = processor_id or str(uuid.uuid4())
        self.max_concurrent_events = max_concurrent_events
        
        # Event storage
        self.event_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.processing_events: Dict[str, WorkerEvent] = {}
        self.completed_events: deque = deque(maxlen=10000)
        self.failed_events: deque = deque(maxlen=1000)
        
        # Handler management
        self.event_handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self.global_handlers: List[EventHandler] = []
        self.handler_registry: Dict[str, EventHandler] = {}
        
        # Processing control
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        self.processing_semaphore = asyncio.Semaphore(max_concurrent_events)
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Event store for event sourcing
        self.event_store: List[WorkerEvent] = []
        self.event_snapshots: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.processing_stats = {
            "total_events": 0,
            "successful_events": 0,
            "failed_events": 0,
            "average_processing_time": 0.0,
            "events_per_second": 0.0
        }
        
        # Components
        self.json_utils = JsonUtils()
        self.access_control = AccessControl()
        self.event_bus = EventBus()
        
        # Thread pool for synchronous handlers
        self.thread_pool = ThreadPoolExecutor(
            max_workers=10, 
            thread_name_prefix=f"EventProcessor-{self.processor_id}"
        )

    async def start(self) -> bool:
        """Start event processor"""



        try:
            logger.info(f" Starting event processor: {self.processor_id}")
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            
            # Register with global event bus
            await self.event_bus.register_processor(self)
            
            logger.info(f" Event processor {self.processor_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f" Failed to start event processor {self.processor_id}: {e}")
            return False

    async def stop(self) -> None:
        """Stop event processor gracefully"""



        try:
            logger.info(f" Stopping event processor: {self.processor_id}")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Wait for processing events to complete
            await self._wait_for_processing_completion()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True, timeout=30)
            
            # Unregister from event bus
            await self.event_bus.unregister_processor(self.processor_id)
            
            logger.info(f" Event processor {self.processor_id} stopped")
            
        except Exception as e:
            logger.error(f" Error stopping event processor {self.processor_id}: {e}")

    async def publish_event(self, event: WorkerEvent) -> bool:
        """Publish an event for processing"""



        try:
            # Validate event
            if not await self._validate_event(event):
                logger.warning(f" Invalid event rejected: {event.event_id}")
                return False
            
            # Add to event store
            self.event_store.append(event)
            
            # Queue for processing based on priority
            priority_value = event.priority.value
            await self.event_queue.put((priority_value, event.timestamp, event))
            
            logger.debug(f" Event published: {event.event_id} ({event.event_type.value})")
            return True
            
        except Exception as e:
            logger.error(f" Failed to publish event {event.event_id}: {e}")
            return False

    async def register_handler(self, handler: EventHandler) -> bool:
        """Register an event handler"""



        try:
            # Validate handler
            if not await self._validate_handler(handler):
                logger.warning(f" Invalid handler rejected: {handler.handler_id}")
                return False
            
            # Register for specific event types
            for event_type in handler.event_types:
                self.event_handlers[event_type].append(handler)
            
            # Store in registry
            self.handler_registry[handler.handler_id] = handler
            
            logger.info(f" Event handler registered: {handler.handler_id} for {[et.value for et in handler.event_types]}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to register handler {handler.handler_id}: {e}")
            return False

    async def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an event handler"""



        try:
            handler = self.handler_registry.get(handler_id)
            if not handler:
                logger.warning(f" Handler not found: {handler_id}")
                return False
            
            # Remove from event type mappings
            for event_type in handler.event_types:
                if handler in self.event_handlers[event_type]:
                    self.event_handlers[event_type].remove(handler)
            
            # Remove from registry
            del self.handler_registry[handler_id]
            
            logger.info(f" Event handler unregistered: {handler_id}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to unregister handler {handler_id}: {e}")
            return False

    async def get_processing_status(self) -> Dict[str, Any]:
        """Get comprehensive processing status"""



        try:
            return {
                "processor_id": self.processor_id,
                "is_running": self.is_running,
                "queue_size": self.event_queue.qsize(),
                "processing_events": len(self.processing_events),
                "completed_events": len(self.completed_events),
                "failed_events": len(self.failed_events),
                "registered_handlers": len(self.handler_registry),
                "event_store_size": len(self.event_store),
                "stats": self.processing_stats.copy(),
                "max_concurrent_events": self.max_concurrent_events,
                "available_slots": self.processing_semaphore._value
            }
            
        except Exception as e:
            logger.error(f" Failed to get processing status: {e}")
            return {"error": str(e)}

    async def replay_events(self, from_timestamp: datetime, 
                          to_timestamp: Optional[datetime] = None,
                          event_types: Optional[List[EventType]] = None) -> int:
        """Replay events from event store"""



        try:
            to_timestamp = to_timestamp or datetime.utcnow()
            
            # Filter events
            events_to_replay = [
                event for event in self.event_store
                if (from_timestamp <= event.timestamp <= to_timestamp and
                    (not event_types or event.event_type in event_types))
            ]
            
            # Replay events
            replayed_count = 0
            for event in events_to_replay:
                # Create new event ID for replay
                replay_event = WorkerEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=event.event_type,
                    source=event.source,
                    target=event.target,
                    payload=event.payload.copy(),
                    metadata={**event.metadata, "is_replay": True, "original_event_id": event.event_id},
                    priority=event.priority,
                    correlation_id=event.correlation_id,
                    causation_id=event.event_id,  # Original event caused this replay
                    tenant_id=event.tenant_id,
                    user_id=event.user_id,
                    tags=event.tags.copy()
                )
                
                if await self.publish_event(replay_event):
                    replayed_count += 1
            
            logger.info(f" Replayed {replayed_count} events")
            return replayed_count
            
        except Exception as e:
            logger.error(f" Failed to replay events: {e}")
            return 0

    async def create_snapshot(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """Create an entity snapshot for event sourcing"""



        try:
            snapshot = {
                "entity_id": entity_id,
                "snapshot_data": entity_data,
                "timestamp": datetime.utcnow().isoformat(),
                "event_count": len([e for e in self.event_store if e.target == entity_id])
            }
            
            self.event_snapshots[entity_id] = snapshot
            
            logger.info(f" Snapshot created for entity: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to create snapshot for {entity_id}: {e}")
            return False

    async def _start_background_tasks(self) -> None:
        """Start background processing tasks"""



        try:
            # Main event processor
            processor_task = asyncio.create_task(self._event_processor_loop())
            self.background_tasks.add(processor_task)
            
            # Statistics updater
            stats_task = asyncio.create_task(self._stats_updater_loop())
            self.background_tasks.add(stats_task)
            
            # Event store cleanup
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.background_tasks.add(cleanup_task)
            
            # Health monitor
            health_task = asyncio.create_task(self._health_monitor_loop())
            self.background_tasks.add(health_task)
            
            logger.info(f" Background tasks started for event processor {self.processor_id}")
            
        except Exception as e:
            logger.error(f" Failed to start background tasks: {e}")
            raise

    async def _event_processor_loop(self) -> None:
        """Main event processing loop"""
        while not self.shutdown_event.is_set():
            try:
                # Get next event with timeout
                try:
                    priority, timestamp, event = await asyncio.wait_for(
                        self.event_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process event asynchronously
                asyncio.create_task(self._process_event(event))
                
            except Exception as e:
                logger.error(f" Event processor loop error: {e}")
                await asyncio.sleep(5)

    async def _process_event(self, event: WorkerEvent) -> None:
        """Process a single event"""
        async with self.processing_semaphore:
            start_time = time.time()
            
            try:
                # Add to processing events
                self.processing_events[event.event_id] = event
                
                logger.debug(f" Processing event: {event.event_id} ({event.event_type.value})")
                
                # Get handlers for this event
                handlers = await self._get_event_handlers(event)
                
                if not handlers:
                    logger.debug(f"ℹ No handlers for event: {event.event_id}")
                    await self._mark_event_completed(event, EventStatus.COMPLETED, start_time)
                    return
                
                # Process with handlers
                results = await self._execute_handlers(event, handlers)
                
                # Determine overall result
                if all(r.status == EventStatus.COMPLETED for r in results):
                    await self._mark_event_completed(event, EventStatus.COMPLETED, start_time)
                elif any(r.status == EventStatus.FAILED for r in results):
                    await self._mark_event_failed(event, "Handler execution failed", start_time)
                else:
                    await self._mark_event_completed(event, EventStatus.COMPLETED, start_time)
                
            except Exception as e:
                logger.error(f" Failed to process event {event.event_id}: {e}")
                await self._mark_event_failed(event, str(e), start_time)
                
            finally:
                # Remove from processing
                self.processing_events.pop(event.event_id, None)

    async def _get_event_handlers(self, event: WorkerEvent) -> List[EventHandler]:
        """Get all handlers for an event"""



        try:
            handlers = []
            
            # Get specific handlers for event type
            type_handlers = self.event_handlers.get(event.event_type, [])
            
            # Add global handlers
            all_handlers = type_handlers + self.global_handlers
            
            # Filter handlers
            for handler in all_handlers:
                if await self._should_handle_event(handler, event):
                    handlers.append(handler)
            
            # Sort by priority
            handlers.sort(key=lambda h: h.priority)
            
            return handlers
            
        except Exception as e:
            logger.error(f" Failed to get event handlers: {e}")
            return []

    async def _should_handle_event(self, handler: EventHandler, event: WorkerEvent) -> bool:
        """Check if handler should process event"""



        try:
            # Check event type
            if event.event_type not in handler.event_types:
                return False
            
            # Check filter function
            if handler.filter_func:
                try:
                    if handler.is_async:
                        return await handler.filter_func(event)
                    else:
                        return handler.filter_func(event)
                except Exception as e:
                    logger.error(f" Handler filter error: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f" Failed to check if handler should process event: {e}")
            return False

    async def _execute_handlers(self, event: WorkerEvent, handlers: List[EventHandler]) -> List[EventProcessingResult]:
        """Execute all handlers for an event"""



        try:
            results = []
            
            # Execute handlers based on their configuration
            for handler in handlers:
                try:
                    result = await self._execute_single_handler(event, handler)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f" Handler execution failed: {handler.handler_id}: {e}")
                    
                    error_result = EventProcessingResult(
                        event_id=event.event_id,
                        status=EventStatus.FAILED,
                        error_message=str(e)
                    )
                    results.append(error_result)
            
            return results
            
        except Exception as e:
            logger.error(f" Failed to execute handlers: {e}")
            return []

    async def _execute_single_handler(self, event: WorkerEvent, handler: EventHandler) -> EventProcessingResult:
        """Execute a single handler"""
        start_time = time.time()
        
        try:
            if handler.is_async:
                # Execute async handler with timeout
                result_data = await asyncio.wait_for(
                    handler.handler_func(event),
                    timeout=handler.timeout_seconds
                )
            else:
                # Execute sync handler in thread pool
                result_data = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    handler.handler_func,
                    event
                )
            
            processing_time = time.time() - start_time
            
            return EventProcessingResult(
                event_id=event.event_id,
                status=EventStatus.COMPLETED,
                result_data=result_data if isinstance(result_data, dict) else {"result": result_data},
                processing_time=processing_time
            )
            
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            
            return EventProcessingResult(
                event_id=event.event_id,
                status=EventStatus.FAILED,
                error_message=f"Handler timeout after {handler.timeout_seconds}s",
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return EventProcessingResult(
                event_id=event.event_id,
                status=EventStatus.FAILED,
                error_message=str(e),
                processing_time=processing_time
            )

    async def _mark_event_completed(self, event: WorkerEvent, status: EventStatus, start_time: float) -> None:
        """Mark event as completed"""



        try:
            processing_time = time.time() - start_time
            
            result = EventProcessingResult(
                event_id=event.event_id,
                status=status,
                processing_time=processing_time
            )
            
            self.completed_events.append(result)
            self.processing_stats["successful_events"] += 1
            
            # Update average processing time
            total_time = (self.processing_stats["average_processing_time"] * 
                         (self.processing_stats["successful_events"] - 1) + processing_time)
            self.processing_stats["average_processing_time"] = total_time / self.processing_stats["successful_events"]
            
            logger.debug(f" Event completed: {event.event_id} in {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f" Failed to mark event completed: {e}")

    async def _mark_event_failed(self, event: WorkerEvent, error_message: str, start_time: float) -> None:
        """Mark event as failed"""



        try:
            processing_time = time.time() - start_time
            
            result = EventProcessingResult(
                event_id=event.event_id,
                status=EventStatus.FAILED,
                error_message=error_message,
                processing_time=processing_time
            )
            
            self.failed_events.append(result)
            self.processing_stats["failed_events"] += 1
            
            logger.error(f" Event failed: {event.event_id}: {error_message}")
            
        except Exception as e:
            logger.error(f" Failed to mark event failed: {e}")

    async def _validate_event(self, event: WorkerEvent) -> bool:
        """Validate event before processing"""



        try:
            # Basic validation
            if not event.event_id or not event.event_type or not event.source:
                return False
            
            # Security validation
            if not await self.access_control.can_publish_event(event):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f" Event validation failed: {e}")
            return False

    async def _validate_handler(self, handler: EventHandler) -> bool:
        """Validate event handler before registration"""



        try:
            # Basic validation
            if not handler.handler_id or not handler.event_types or not handler.handler_func:
                return False
            
            # Check for duplicate handler ID
            if handler.handler_id in self.handler_registry:
                return False
            
            # Security validation
            if not await self.access_control.can_register_handler(handler):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f" Handler validation failed: {e}")
            return False

    async def _wait_for_processing_completion(self) -> None:
        """Wait for all processing events to complete"""



        try:
            timeout = 60  # 1 minute timeout
            start_time = time.time()
            
            while self.processing_events and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)
            
            if self.processing_events:
                logger.warning(f" {len(self.processing_events)} events still processing during shutdown")
            
        except Exception as e:
            logger.error(f" Failed to wait for processing completion: {e}")

    async def _stats_updater_loop(self) -> None:
        """Background stats update loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._update_processing_stats()
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f" Stats updater error: {e}")
                await asyncio.sleep(120)

    async def _update_processing_stats(self) -> None:
        """Update processing statistics"""



        try:
            # Update total events
            total_events = self.processing_stats["successful_events"] + self.processing_stats["failed_events"]
            self.processing_stats["total_events"] = total_events
            
            # Calculate events per second (simplified)
            if total_events > 0:
                # This would need historical data for accurate calculation
                self.processing_stats["events_per_second"] = 1.0  # Placeholder
            
        except Exception as e:
            logger.error(f" Failed to update processing stats: {e}")

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._cleanup_old_events()
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f" Cleanup loop error: {e}")
                await asyncio.sleep(1800)

    async def _cleanup_old_events(self) -> None:
        """Clean up old events from event store"""



        try:
            # Keep events for 7 days
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            
            original_count = len(self.event_store)
            self.event_store = [
                event for event in self.event_store
                if event.timestamp > cutoff_time
            ]
            
            cleaned_count = original_count - len(self.event_store)
            if cleaned_count > 0:
                logger.info(f"🧹 Cleaned up {cleaned_count} old events")
            
        except Exception as e:
            logger.error(f" Failed to cleanup old events: {e}")

    async def _health_monitor_loop(self) -> None:
        """Background health monitoring loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._check_processor_health()
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f" Health monitor error: {e}")
                await asyncio.sleep(600)

    async def _check_processor_health(self) -> None:
        """Check processor health and emit alerts if needed"""



        try:
            status = await self.get_processing_status()
            
            # Check queue size
            if status["queue_size"] > 1000:
                await self._emit_health_alert("high_queue_size", status["queue_size"])
            
            # Check processing events
            if status["processing_events"] > self.max_concurrent_events * 0.9:
                await self._emit_health_alert("high_processing_load", status["processing_events"])
            
            # Check error rate
            total_events = status["stats"]["total_events"]
            failed_events = status["stats"]["failed_events"]
            if total_events > 100 and (failed_events / total_events) > 0.1:  # 10% error rate
                await self._emit_health_alert("high_error_rate", failed_events / total_events)
            
        except Exception as e:
            logger.error(f" Failed to check processor health: {e}")

    async def _emit_health_alert(self, alert_type: str, value: Any) -> None:
        """Emit health alert event"""



        try:
            alert_event = WorkerEvent(
                event_id=str(uuid.uuid4()),
                event_type=EventType.PERFORMANCE_ALERT,
                source=f"event_processor_{self.processor_id}",
                payload={
                    "alert_type": alert_type,
                    "value": value,
                    "processor_id": self.processor_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                priority=EventPriority.HIGH
            )
            
            await self.publish_event(alert_event)
            
        except Exception as e:
            logger.error(f" Failed to emit health alert: {e}")


class WorkerEventFactory:
    """Factory for creating worker events"""

    @staticmethod
    def create_worker_started_event(worker_id: str, worker_config: Dict[str, Any]) -> WorkerEvent:
        """Create worker started event"""



        return WorkerEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WORKER_STARTED,
            source=f"worker_{worker_id}",
            payload={
                "worker_id": worker_id,
                "config": worker_config,
                "start_time": datetime.utcnow().isoformat()
            },
            priority=EventPriority.NORMAL
        )

    @staticmethod
    def create_task_completed_event(worker_id: str, task: CrawlerTask, result: TaskResult) -> WorkerEvent:
        """Create task completed event"""



        return WorkerEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.TASK_COMPLETED,
            source=f"worker_{worker_id}",
            target=f"task_{task.task_id}",
            payload={
                "task_id": task.task_id,
                "worker_id": worker_id,
                "result": result.value,
                "completion_time": datetime.utcnow().isoformat(),
                "task_type": task.task_type,
                "target_url": task.target_url
            },
            priority=EventPriority.NORMAL,
            correlation_id=task.task_id,
            tenant_id=task.tenant_id,
            user_id=task.user_id
        )

    @staticmethod
    def create_content_protected_event(content_id: str, fingerprint_data: Dict[str, Any]) -> WorkerEvent:
        """Create content protected event"""



        return WorkerEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.CONTENT_PROTECTED,
            source="fingerprint_engine",
            target=f"content_{content_id}",
            payload={
                "content_id": content_id,
                "fingerprint_data": fingerprint_data,
                "protection_time": datetime.utcnow().isoformat()
            },
            priority=EventPriority.HIGH
        )

    @staticmethod
    def create_violation_detected_event(content_id: str, violation_data: Dict[str, Any]) -> WorkerEvent:
        """Create violation detected event"""



        return WorkerEvent(
            event_id=str(uuid.uuid4()),
            event_type=EventType.VIOLATION_DETECTED,
            source="content_monitor",
            target=f"content_{content_id}",
            payload={
                "content_id": content_id,
                "violation_data": violation_data,
                "detection_time": datetime.utcnow().isoformat(),
                "severity": violation_data.get("severity", "medium")
            },
            priority=EventPriority.CRITICAL
        )


# Global event processor registry
_event_processors: Dict[str, EventProcessor] = {}


def get_event_processor(processor_id: str = "default") -> EventProcessor:
    """Get or create event processor"""
    if processor_id not in _event_processors:
        _event_processors[processor_id] = EventProcessor(processor_id)
    
    return _event_processors[processor_id]


async def initialize_event_processing() -> bool:
    """Initialize global event processing"""



    try:
        processor = get_event_processor()
        return await processor.start()
        
    except Exception as e:
        logger.error(f" Failed to initialize event processing: {e}")
        return False


async def shutdown_event_processing() -> None:
    """Shutdown all event processors"""



    try:
        for processor in _event_processors.values():
            await processor.stop()
        
        _event_processors.clear()
        
    except Exception as e:
        logger.error(f" Failed to shutdown event processing: {e}")


# High-level event publishing functions
async def publish_worker_event(event_type: EventType, source: str, payload: Dict[str, Any], 
                              priority: EventPriority = EventPriority.NORMAL) -> bool:
    """Publish a worker event"""



    try:
        event = WorkerEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            source=source,
            payload=payload,
            priority=priority
        )
        
        processor = get_event_processor()
        return await processor.publish_event(event)
        
    except Exception as e:
        logger.error(f" Failed to publish worker event: {e}")
        return False


async def register_event_handler(event_types: List[EventType], handler_func: Callable,
                                handler_id: str = None, priority: int = 100) -> bool:
    """Register an event handler"""



    try:
        handler_id = handler_id or str(uuid.uuid4())
        
        handler = EventHandler(
            handler_id=handler_id,
            event_types=event_types,
            handler_func=handler_func,
            priority=priority
        )
        
        processor = get_event_processor()
        return await processor.register_handler(handler)
        
    except Exception as e:
        logger.error(f" Failed to register event handler: {e}")
        return False
