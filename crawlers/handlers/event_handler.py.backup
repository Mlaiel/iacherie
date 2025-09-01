"""Event Handler Module
===================

Professional event handling system for crawler operations and asynchronous processing.
Manages events, callbacks, webhooks, and real-time notifications with enterprise-grade reliability.

Event Types Supported:
- Content Detection Events
- Protection Alert Events  
- Monetization Events
- System Status Events
- User Action Events
- Platform Integration Events

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""
import asyncio
import logging
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Coroutine
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import weakref
import traceback
from functools import wraps
import aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import (
    EventHandlingError,
    EventValidationError,
    HandlerRegistrationError
)
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.database.models import EventLog, User, ContentFingerprint
from backend.database.session import async_session
from backend.utils.redis_client import get_redis_client
from backend.utils.notification_utils import NotificationManager
from backend.utils.webhook_utils import WebhookManager

logger = get_logger(__name__)


class EventType(Enum):
    """Enumeration of supported event types."""
    
    # Content Events
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_FINGERPRINTED = "content.fingerprinted"
    CONTENT_PROTECTED = "content.protected"
    
    # Detection Events
    INFRINGEMENT_DETECTED = "infringement.detected"
    SIMILARITY_FOUND = "similarity.found"
    PLATFORM_MATCH = "platform.match"
    
    # Protection Events
    TAKEDOWN_REQUESTED = "protection.takedown_requested"
    TAKEDOWN_COMPLETED = "protection.takedown_completed"
    DMCA_FILED = "protection.dmca_filed"
    
    # Monetization Events
    REVENUE_DETECTED = "monetization.revenue_detected"
    PAYMENT_PROCESSED = "monetization.payment_processed"
    LICENSING_OFFERED = "monetization.licensing_offered"
    
    # User Events
    USER_REGISTERED = "user.registered"
    USER_UPGRADED = "user.upgraded"
    USER_ACTIVITY = "user.activity"
    
    # System Events
    SYSTEM_HEALTH = "system.health"
    CRAWLER_STATUS = "crawler.status"
    API_RATE_LIMIT = "api.rate_limit"
    
    # Platform Events
    PLATFORM_CONNECTED = "platform.connected"
    PLATFORM_DISCONNECTED = "platform.disconnected"
    PLATFORM_ERROR = "platform.error"


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class Event:
    """Event data structure with comprehensive metadata."""
    
    event_id: str
    event_type: EventType
    priority: EventPriority
    timestamp: datetime
    user_id: Optional[int] = None
    content_id: Optional[int] = None
    platform: Optional[str] = None
    data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    source: Optional[str] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'content_id': self.content_id,
            'platform': self.platform,
            'data': self.data,
            'metadata': self.metadata,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'correlation_id': self.correlation_id,
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            priority=EventPriority(data['priority']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_id=data.get('user_id'),
            content_id=data.get('content_id'),
            platform=data.get('platform'),
            data=data.get('data', {}),
            metadata=data.get('metadata', {}),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            correlation_id=data.get('correlation_id'),
            source=data.get('source')
        )


class EventHandler:
    """Base class for event handlers."""
    
    def __init__(self, name: str, handler_id: Optional[str] = None):
        self.name = name
        self.handler_id = handler_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.execution_count = 0
        self.last_execution = None
        self.error_count = 0
    
    async def handle(self, event: Event) -> bool:
        """
        Handle an event - base implementation.
        
        Args:
            event: Event to handle
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Basic event handling implementation
            logger.info(f"Handling event {event.event_id} of type {event.event_type} in {self.name}")
            
            # Check if we can handle this event
            if not await self.can_handle(event):
                logger.warning(f"Handler {self.name} cannot handle event {event.event_id}")
                return False
            
            # Record handling start
            start_time = datetime.utcnow()
            
            # Basic event processing - log event details
            logger.info(f"Processing event: {event.event_type}")
            logger.debug(f"Event data: {event.data}")
            
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.01)  # Minimal processing delay
            
            # Update event status
            event.status = EventStatus.PROCESSED
            event.processed_at = datetime.utcnow()
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update statistics
            self.update_stats(True)
            
            logger.info(f"Successfully handled event {event.event_id} in {processing_time:.3f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error handling event {event.event_id} in {self.name}: {str(e)}")
            
            # Update event status
            event.status = EventStatus.FAILED
            event.error = str(e)
            
            # Update statistics
            self.update_stats(False)
            
            return False
    
    async def can_handle(self, event: Event) -> bool:
        """
        Check if this handler can handle the event.
        
        Args:
            event: Event to check
            
        Returns:
            True if can handle, False otherwise
        """
        return self.is_active
    
    def update_stats(self, success: bool):
        """Update handler execution statistics."""
        self.execution_count += 1
        self.last_execution = datetime.utcnow()
        if not success:
            self.error_count += 1


class AsyncEventHandler(EventHandler):
    """Async event handler with coroutine support."""
    
    def __init__(
        self, 
        name: str, 
        handler_func: Callable[[Event], Coroutine[Any, Any, bool]],
        event_types: Optional[List[EventType]] = None,
        handler_id: Optional[str] = None
    ):
        super().__init__(name, handler_id)
        self.handler_func = handler_func
        self.event_types = event_types or []
    
    async def handle(self, event: Event) -> bool:
        """Execute the async handler function."""
        try:
            result = await self.handler_func(event)
            self.update_stats(True)
            return result
        except Exception as e:
            logger.error(f"Handler {self.name} failed: {e}")
            self.update_stats(False)
            return False
    
    async def can_handle(self, event: Event) -> bool:
        """Check if handler can handle the event type."""
        if not await super().can_handle(event):
            return False
        
        if not self.event_types:
            return True
        
        return event.event_type in self.event_types


class SyncEventHandler(EventHandler):
    """Synchronous event handler with thread pool execution."""
    
    def __init__(
        self, 
        name: str, 
        handler_func: Callable[[Event], bool],
        event_types: Optional[List[EventType]] = None,
        handler_id: Optional[str] = None
    ):
        super().__init__(name, handler_id)
        self.handler_func = handler_func
        self.event_types = event_types or []
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def handle(self, event: Event) -> bool:
        """Execute the sync handler function in thread pool."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, self.handler_func, event
            )
            self.update_stats(True)
            return result
        except Exception as e:
            logger.error(f"Handler {self.name} failed: {e}")
            self.update_stats(False)
            return False
    
    async def can_handle(self, event: Event) -> bool:
        """Check if handler can handle the event type."""
        if not await super().can_handle(event):
            return False
        
        if not self.event_types:
            return True
        
        return event.event_type in self.event_types


class EventQueue:
    """Professional event queue with Redis backend and priority handling."""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.queue_key = "crawler:event_queue"
        self.processing_key = "crawler:processing_events"
        self.failed_key = "crawler:failed_events"
        self.stats_key = "crawler:event_stats"
    
    async def enqueue(self, event: Event) -> bool:
        """
        Add event to queue with priority handling.
        
        Args:
            event: Event to enqueue
            
        Returns:
            True if enqueued successfully
        """
        try:
            # Serialize event
            event_data = json.dumps(event.to_dict())
            
            # Add to priority queue (Redis sorted set with priority as score)
            priority_score = event.priority.value * 1000 + int(event.timestamp.timestamp())
            
            await self.redis.zadd(self.queue_key, {event_data: priority_score})
            
            # Update stats
            await self._update_stats('enqueued')
            
            logger.debug(f"Event {event.event_id} enqueued with priority {event.priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enqueue event {event.event_id}: {e}")
            return False
    
    async def dequeue(self, timeout: int = 10) -> Optional[Event]:
        """
        Get next event from queue based on priority.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            Next event or None if timeout
        """
        try:
            # Get highest priority event (highest score)
            result = await self.redis.bzpopmax(self.queue_key, timeout)
            
            if not result:
                return None
            
            queue_name, event_data, score = result
            event_dict = json.loads(event_data)
            event = Event.from_dict(event_dict)
            
            # Move to processing set
            await self.redis.hset(
                self.processing_key, 
                event.event_id, 
                event_data
            )
            
            # Update stats
            await self._update_stats('dequeued')
            
            return event
            
        except Exception as e:
            logger.error(f"Failed to dequeue event: {e}")
            return None
    
    async def mark_completed(self, event_id: str) -> bool:
        """Mark event as completed and remove from processing."""
        try:
            await self.redis.hdel(self.processing_key, event_id)
            await self._update_stats('completed')
            return True
        except Exception as e:
            logger.error(f"Failed to mark event {event_id} as completed: {e}")
            return False
    
    async def mark_failed(self, event: Event, error: str) -> bool:
        """Mark event as failed and handle retry logic."""
        try:
            # Remove from processing
            await self.redis.hdel(self.processing_key, event.event_id)
            
            # Check if should retry
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                event.metadata['last_error'] = error
                event.metadata['failed_at'] = datetime.utcnow().isoformat()
                
                # Re-enqueue with delay
                await asyncio.sleep(2 ** event.retry_count)  # Exponential backoff
                await self.enqueue(event)
                
                logger.info(f"Event {event.event_id} requeued for retry {event.retry_count}")
            else:
                # Max retries reached, move to failed queue
                failed_data = {
                    'event': event.to_dict(),
                    'error': error,
                    'failed_at': datetime.utcnow().isoformat()
                }
                
                await self.redis.lpush(
                    self.failed_key, 
                    json.dumps(failed_data)
                )
                
                logger.error(f"Event {event.event_id} permanently failed after {event.retry_count} retries")
            
            await self._update_stats('failed')
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark event {event.event_id} as failed: {e}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        try:
            pending = await self.redis.zcard(self.queue_key)
            processing = await self.redis.hlen(self.processing_key)
            failed = await self.redis.llen(self.failed_key)
            
            stats_data = await self.redis.hgetall(self.stats_key)
            stats = {k.decode(): int(v.decode()) for k, v in stats_data.items()}
            
            return {
                'pending': pending,
                'processing': processing,
                'failed': failed,
                'total_enqueued': stats.get('enqueued', 0),
                'total_dequeued': stats.get('dequeued', 0),
                'total_completed': stats.get('completed', 0),
                'total_failed': stats.get('failed', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    async def _update_stats(self, operation: str):
        """Update queue statistics."""
        try:
            await self.redis.hincrby(self.stats_key, operation, 1)
        except Exception as e:
            logger.warning(f"Failed to update stats for {operation}: {e}")


class EventRegistry:
    """Registry for event handlers with dynamic registration and management."""
    
    def __init__(self):
        self.handlers: Dict[str, EventHandler] = {}
        self.type_handlers: Dict[EventType, List[str]] = {}
        self._lock = asyncio.Lock()
    
    async def register_handler(
        self, 
        handler: EventHandler,
        event_types: Optional[List[EventType]] = None
    ) -> bool:
        """
        Register an event handler.
        
        Args:
            handler: Handler to register
            event_types: Event types this handler can process
            
        Returns:
            True if registered successfully
        """
        try:
            async with self._lock:
                # Check for duplicate handler IDs
                if handler.handler_id in self.handlers:
                    raise HandlerRegistrationError(
                        f"Handler with ID {handler.handler_id} already registered"
                    )
                
                # Register handler
                self.handlers[handler.handler_id] = handler
                
                # Map event types to handler
                if event_types:
                    for event_type in event_types:
                        if event_type not in self.type_handlers:
                            self.type_handlers[event_type] = []
                        self.type_handlers[event_type].append(handler.handler_id)
                
                logger.info(f"Handler {handler.name} registered with ID {handler.handler_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register handler {handler.name}: {e}")
            return False
    
    async def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an event handler."""
        try:
            async with self._lock:
                if handler_id not in self.handlers:
                    return False
                
                handler = self.handlers.pop(handler_id)
                
                # Remove from type mappings
                for event_type, handler_ids in self.type_handlers.items():
                    if handler_id in handler_ids:
                        handler_ids.remove(handler_id)
                
                logger.info(f"Handler {handler.name} unregistered")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unregister handler {handler_id}: {e}")
            return False
    
    async def get_handlers_for_event(self, event: Event) -> List[EventHandler]:
        """Get all handlers that can process the given event."""
        try:
            eligible_handlers = []
            
            # Get handlers specifically registered for this event type
            handler_ids = self.type_handlers.get(event.event_type, [])
            
            # Add all handlers (they can filter themselves)
            all_handler_ids = set(handler_ids + list(self.handlers.keys()))
            
            for handler_id in all_handler_ids:
                handler = self.handlers.get(handler_id)
                if handler and await handler.can_handle(event):
                    eligible_handlers.append(handler)
            
            # Sort by priority (handlers with fewer errors first)
            eligible_handlers.sort(key=lambda h: h.error_count)
            
            return eligible_handlers
            
        except Exception as e:
            logger.error(f"Failed to get handlers for event {event.event_id}: {e}")
            return []
    
    def get_handler_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all registered handlers."""
        stats = {}
        for handler_id, handler in self.handlers.items():
            stats[handler_id] = {
                'name': handler.name,
                'is_active': handler.is_active,
                'execution_count': handler.execution_count,
                'error_count': handler.error_count,
                'last_execution': handler.last_execution.isoformat() if handler.last_execution else None,
                'created_at': handler.created_at.isoformat()
            }
        return stats


class EventDispatcher:
    """Main event dispatcher orchestrating event processing."""
    
    def __init__(
        self, 
        redis_client: aioredis.Redis,
        notification_manager: Optional[NotificationManager] = None,
        webhook_manager: Optional[WebhookManager] = None
    ):
        self.queue = EventQueue(redis_client)
        self.registry = EventRegistry()
        self.notification_manager = notification_manager
        self.webhook_manager = webhook_manager
        self.is_running = False
        self.worker_tasks: List[asyncio.Task] = []
        self.worker_count = settings.EVENT_WORKER_COUNT
        self._shutdown_event = asyncio.Event()
    
    async def dispatch_event(self, event: Event) -> bool:
        """
        Dispatch an event for processing.
        
        Args:
            event: Event to dispatch
            
        Returns:
            True if dispatched successfully
        """
        try:
            # Validate event
            self._validate_event(event)
            
            # Log event
            await self._log_event(event)
            
            # Enqueue for processing
            success = await self.queue.enqueue(event)
            
            # Send immediate notifications for critical events
            if event.priority == EventPriority.CRITICAL and self.notification_manager:
                await self.notification_manager.send_critical_alert(event)
            
            logger.info(f"Event {event.event_id} dispatched successfully")
            return success
            
        except Exception as e:
            logger.error(f"Failed to dispatch event {event.event_id}: {e}")
            return False
    
    def _validate_event(self, event: Event):
        """Validate event data."""
        if not event.event_id:
            raise EventValidationError("Event ID is required")
        
        if not isinstance(event.event_type, EventType):
            raise EventValidationError("Invalid event type")
        
        if not isinstance(event.priority, EventPriority):
            raise EventValidationError("Invalid event priority")
    
    async def _log_event(self, event: Event):
        """Log event to database."""
        try:
            async with async_session() as session:
                event_log = EventLog(
                    event_id=event.event_id,
                    event_type=event.event_type.value,
                    priority=event.priority.value,
                    user_id=event.user_id,
                    content_id=event.content_id,
                    platform=event.platform,
                    data=event.data,
                    metadata=event.metadata,
                    correlation_id=event.correlation_id,
                    source=event.source,
                    created_at=event.timestamp
                )
                
                session.add(event_log)
                await session.commit()
                
        except Exception as e:
            logger.warning(f"Failed to log event {event.event_id}: {e}")
    
    async def start_workers(self):
        """Start event processing workers."""
        if self.is_running:
            return
        
        self.is_running = True
        self._shutdown_event.clear()
        
        # Start worker tasks
        for i in range(self.worker_count):
            task = asyncio.create_task(
                self._worker_loop(f"worker-{i}"),
                name=f"event-worker-{i}"
            )
            self.worker_tasks.append(task)
        
        logger.info(f"Started {self.worker_count} event workers")
    
    async def stop_workers(self):
        """Stop event processing workers."""
        if not self.is_running:
            return
        
        self.is_running = False
        self._shutdown_event.set()
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        logger.info("Event workers stopped")
    
    async def _worker_loop(self, worker_name: str):
        """Main worker loop for processing events."""
        logger.info(f"Event worker {worker_name} started")
        
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Get next event from queue
                event = await self.queue.dequeue(timeout=5)
                
                if not event:
                    continue
                
                logger.debug(f"Worker {worker_name} processing event {event.event_id}")
                
                # Get handlers for event
                handlers = await self.registry.get_handlers_for_event(event)
                
                if not handlers:
                    logger.warning(f"No handlers found for event {event.event_id}")
                    await self.queue.mark_completed(event.event_id)
                    continue
                
                # Process event with handlers
                success = await self._process_event_with_handlers(event, handlers)
                
                if success:
                    await self.queue.mark_completed(event.event_id)
                    
                    # Send webhooks if configured
                    if self.webhook_manager:
                        await self.webhook_manager.send_event_webhook(event)
                        
                else:
                    await self.queue.mark_failed(event, "Handler processing failed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)  # Brief pause on error
        
        logger.info(f"Event worker {worker_name} stopped")
    
    async def _process_event_with_handlers(
        self, 
        event: Event, 
        handlers: List[EventHandler]
    ) -> bool:
        """Process event with multiple handlers."""
        success_count = 0
        
        for handler in handlers:
            try:
                result = await handler.handle(event)
                if result:
                    success_count += 1
                    logger.debug(f"Handler {handler.name} processed event {event.event_id}")
                else:
                    logger.warning(f"Handler {handler.name} failed to process event {event.event_id}")
                    
            except Exception as e:
                logger.error(f"Handler {handler.name} error processing event {event.event_id}: {e}")
        
        # Consider successful if at least one handler succeeded
        return success_count > 0
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        queue_stats = await self.queue.get_queue_stats()
        handler_stats = self.registry.get_handler_stats()
        
        return {
            'queue': queue_stats,
            'handlers': handler_stats,
            'workers': {
                'count': self.worker_count,
                'running': self.is_running,
                'active_tasks': len([t for t in self.worker_tasks if not t.done()])
            },
            'timestamp': datetime.utcnow().isoformat()
        }


# Utility functions for common event patterns
async def create_content_event(
    event_type: EventType,
    user_id: int,
    content_id: int,
    data: Dict[str, Any],
    priority: EventPriority = EventPriority.NORMAL
) -> Event:
    """Create a content-related event."""
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        priority=priority,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        content_id=content_id,
        data=data,
        source="content_system"
    )


async def create_platform_event(
    event_type: EventType,
    platform: str,
    user_id: Optional[int],
    data: Dict[str, Any],
    priority: EventPriority = EventPriority.NORMAL
) -> Event:
    """Create a platform-related event."""
    return Event(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        priority=priority,
        timestamp=datetime.utcnow(),
        user_id=user_id,
        platform=platform,
        data=data,
        source=f"{platform}_integration"
    )


# Factory function
async def create_event_dispatcher(
    redis_client: Optional[aioredis.Redis] = None
) -> EventDispatcher:
    """Create and return an EventDispatcher instance."""
    if redis_client is None:
        redis_client = await get_redis_client()
    
    return EventDispatcher(redis_client)
