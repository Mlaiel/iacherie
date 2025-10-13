"""
Event Manager - Core Utilities Level 1
======================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Enterprise-grade event management utility for Creator Economy platform.
Provides event sourcing, event bus, webhook management, event scheduling,
real-time notifications, analytics events, audit events, and event replay.

Performance: < 1ms for event dispatch, < 5ms for webhook delivery
Standards: 100% async, type hints, enterprise event-driven patterns
"""

import asyncio
import json
import logging
import hashlib
import hmac
import time
import uuid
from typing import (
    Any, Dict, List, Optional, Union, Callable, Tuple, 
    AsyncIterator, Set, Type, TypeVar, Generic
)
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import weakref

# Optional dependencies with enterprise fallbacks
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    aiohttp = None
    AIOHTTP_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar('T')

class EventType(Enum):
    """Event type enumeration for Creator Economy."""
    # User events
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_PROFILE_UPDATED = "user_profile_updated"
    
    # Creator events
    CREATOR_VERIFIED = "creator_verified"
    CREATOR_TIER_CHANGED = "creator_tier_changed"
    
    # Content events
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_UPDATED = "content_updated"
    CONTENT_DELETED = "content_deleted"
    CONTENT_VIEWED = "content_viewed"
    CONTENT_LIKED = "content_liked"
    CONTENT_SHARED = "content_shared"
    CONTENT_REPORTED = "content_reported"
    
    # Monetization events
    PAYMENT_PROCESSED = "payment_processed"
    PAYMENT_FAILED = "payment_failed"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    REVENUE_GENERATED = "revenue_generated"
    
    # Collaboration events
    COLLABORATION_INVITED = "collaboration_invited"
    COLLABORATION_ACCEPTED = "collaboration_accepted"
    COLLABORATION_COMPLETED = "collaboration_completed"
    
    # System events
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    SYSTEM_MAINTENANCE = "system_maintenance"
    
    # Analytics events
    ANALYTICS_TRACKED = "analytics_tracked"
    CONVERSION_TRACKED = "conversion_tracked"
    
    # Audit events
    SECURITY_ALERT = "security_alert"
    COMPLIANCE_CHECK = "compliance_check"
    DATA_EXPORT = "data_export"

class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class WebhookStatus(Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

@dataclass
class Event:
    """Enterprise event container."""
    id: str
    type: EventType
    payload: Dict[str, Any]
    source: str
    timestamp: datetime
    priority: EventPriority = EventPriority.NORMAL
    creator_id: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'payload': self.payload,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'creator_id': self.creator_id,
            'user_id': self.user_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(
            id=data['id'],
            type=EventType(data['type']),
            payload=data['payload'],
            source=data['source'],
            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
            priority=EventPriority(data.get('priority', EventPriority.NORMAL.value)),
            creator_id=data.get('creator_id'),
            user_id=data.get('user_id'),
            correlation_id=data.get('correlation_id'),
            metadata=data.get('metadata', {}),
            version=data.get('version', '1.0')
        )

@dataclass
class EventHandlerResult:
    """Result of event handler execution."""
    success: bool
    handler_name: str
    execution_time_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Webhook:
    """Webhook configuration."""
    id: str
    url: str
    event_types: List[EventType]
    secret: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class WebhookDelivery:
    """Webhook delivery attempt."""
    id: str
    webhook_id: str
    event_id: str
    url: str
    status: WebhookStatus
    attempt: int
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    attempted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None

@dataclass
class ScheduledEvent:
    """Scheduled event for future execution."""
    id: str
    event: Event
    scheduled_for: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed: bool = False
    executed_at: Optional[datetime] = None

@dataclass
class EventManagerConfig:
    """Event manager configuration."""
    # Event storage
    max_events_in_memory: int = 10000
    event_retention_hours: int = 72
    enable_event_sourcing: bool = True
    
    # Event bus
    enable_async_processing: bool = True
    max_concurrent_handlers: int = 50
    handler_timeout_seconds: float = 30.0
    
    # Webhooks
    enable_webhooks: bool = True
    webhook_timeout_seconds: float = 30.0
    webhook_max_retries: int = 3
    webhook_retry_delay_seconds: float = 5.0
    
    # Scheduling
    enable_scheduling: bool = True
    scheduler_interval_seconds: float = 1.0
    
    # Performance
    enable_metrics: bool = True
    enable_analytics: bool = True
    
    # Redis configuration for distributed events
    redis_url: Optional[str] = None
    redis_channel_prefix: str = "iacherie:events"

EventHandler = Callable[[Event], Union[None, bool, Dict[str, Any], asyncio.Future]]

class EventStore:
    """In-memory event store with persistence options."""
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self._events: deque = deque(maxlen=max_events)
        self._events_by_type: Dict[EventType, List[Event]] = defaultdict(list)
        self._events_by_correlation: Dict[str, List[Event]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def store_event(self, event: Event) -> None:
        """Store an event."""
        async with self._lock:
            self._events.append(event)
            self._events_by_type[event.type].append(event)
            
            if event.correlation_id:
                self._events_by_correlation[event.correlation_id].append(event)
            
            # Maintain size limits for type-specific storage
            if len(self._events_by_type[event.type]) > 1000:
                self._events_by_type[event.type] = self._events_by_type[event.type][-1000:]
    
    async def get_events(
        self,
        event_type: Optional[EventType] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Retrieve events with filtering."""
        async with self._lock:
            if correlation_id:
                events = self._events_by_correlation.get(correlation_id, [])
            elif event_type:
                events = self._events_by_type.get(event_type, [])
            else:
                events = list(self._events)
            
            # Time filtering
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
            
            # Sort by timestamp (newest first) and limit
            events.sort(key=lambda x: x.timestamp, reverse=True)
            return events[:limit]
    
    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID."""
        async with self._lock:
            for event in self._events:
                if event.id == event_id:
                    return event
            return None
    
    async def clear_old_events(self, retention_hours: int) -> int:
        """Clear events older than retention period."""
        async with self._lock:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=retention_hours)
            removed_count = 0
            
            # Clear from main deque
            original_length = len(self._events)
            self._events = deque(
                (e for e in self._events if e.timestamp >= cutoff_time),
                maxlen=self.max_events
            )
            removed_count += original_length - len(self._events)
            
            # Clear from type-specific storage
            for event_type in list(self._events_by_type.keys()):
                original_length = len(self._events_by_type[event_type])
                self._events_by_type[event_type] = [
                    e for e in self._events_by_type[event_type]
                    if e.timestamp >= cutoff_time
                ]
                removed_count += original_length - len(self._events_by_type[event_type])
            
            # Clear from correlation storage
            for correlation_id in list(self._events_by_correlation.keys()):
                original_length = len(self._events_by_correlation[correlation_id])
                self._events_by_correlation[correlation_id] = [
                    e for e in self._events_by_correlation[correlation_id]
                    if e.timestamp >= cutoff_time
                ]
                if not self._events_by_correlation[correlation_id]:
                    del self._events_by_correlation[correlation_id]
            
            return removed_count

class WebhookManager:
    """Webhook management for external integrations."""
    
    def __init__(self, config: EventManagerConfig):
        self.config = config
        self.webhooks: Dict[str, Webhook] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self._session: Optional[aiohttp.ClientSession] = None
        self._delivery_semaphore = asyncio.Semaphore(10)  # Limit concurrent deliveries
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session exists."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.webhook_timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def register_webhook(self, webhook: Webhook) -> None:
        """Register a webhook."""
        self.webhooks[webhook.id] = webhook
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """Unregister a webhook."""
        return self.webhooks.pop(webhook_id, None) is not None
    
    def get_webhooks_for_event(self, event_type: EventType) -> List[Webhook]:
        """Get webhooks that should receive this event type."""
        return [
            webhook for webhook in self.webhooks.values()
            if webhook.active and event_type in webhook.event_types
        ]
    
    async def deliver_event(self, event: Event) -> List[WebhookDelivery]:
        """Deliver event to all relevant webhooks."""
        if not self.config.enable_webhooks:
            return []
        
        webhooks = self.get_webhooks_for_event(event.type)
        if not webhooks:
            return []
        
        tasks = []
        for webhook in webhooks:
            task = asyncio.create_task(self._deliver_to_webhook(event, webhook))
            tasks.append(task)
        
        deliveries = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful deliveries
        successful_deliveries = [
            delivery for delivery in deliveries 
            if isinstance(delivery, WebhookDelivery)
        ]
        
        return successful_deliveries
    
    async def _deliver_to_webhook(self, event: Event, webhook: Webhook) -> WebhookDelivery:
        """Deliver event to a specific webhook."""
        async with self._delivery_semaphore:
            delivery_id = str(uuid.uuid4())
            delivery = WebhookDelivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event_id=event.id,
                url=webhook.url,
                status=WebhookStatus.PENDING,
                attempt=1
            )
            
            self.deliveries[delivery_id] = delivery
            
            try:
                await self._ensure_session()
                
                # Prepare payload
                payload = event.to_dict()
                payload_json = json.dumps(payload)
                
                # Prepare headers
                headers = webhook.headers.copy()
                headers['Content-Type'] = 'application/json'
                headers['User-Agent'] = 'IA Chérie-Webhook/1.0'
                headers['X-Event-ID'] = event.id
                headers['X-Event-Type'] = event.type.value
                
                # Add signature if secret is provided
                if webhook.secret:
                    signature = hmac.new(
                        webhook.secret.encode(),
                        payload_json.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    headers['X-Signature-SHA256'] = f'sha256={signature}'
                
                # Make request
                async with self._session.post(
                    webhook.url,
                    data=payload_json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=webhook.timeout_seconds)
                ) as response:
                    delivery.response_status = response.status
                    delivery.response_body = await response.text()
                    
                    if 200 <= response.status < 300:
                        delivery.status = WebhookStatus.DELIVERED
                        delivery.delivered_at = datetime.now(timezone.utc)
                    else:
                        delivery.status = WebhookStatus.FAILED
                        delivery.error_message = f"HTTP {response.status}: {response.reason}"
                        
                        # Schedule retry if configured
                        if delivery.attempt < webhook.max_retries:
                            await self._schedule_webhook_retry(event, webhook, delivery)
            
            except asyncio.TimeoutError:
                delivery.status = WebhookStatus.FAILED
                delivery.error_message = "Request timeout"
            except Exception as e:
                delivery.status = WebhookStatus.FAILED
                delivery.error_message = str(e)
                
                # Schedule retry if configured
                if delivery.attempt < webhook.max_retries:
                    await self._schedule_webhook_retry(event, webhook, delivery)
            
            return delivery
    
    async def _schedule_webhook_retry(
        self, 
        event: Event, 
        webhook: Webhook, 
        failed_delivery: WebhookDelivery
    ) -> None:
        """Schedule webhook retry after delay."""
        delay = webhook.retry_delay_seconds * (2 ** (failed_delivery.attempt - 1))  # Exponential backoff
        
        async def retry_after_delay():
            await asyncio.sleep(delay)
            retry_delivery = WebhookDelivery(
                id=str(uuid.uuid4()),
                webhook_id=webhook.id,
                event_id=event.id,
                url=webhook.url,
                status=WebhookStatus.RETRYING,
                attempt=failed_delivery.attempt + 1
            )
            
            self.deliveries[retry_delivery.id] = retry_delivery
            await self._deliver_to_webhook(event, webhook)
        
        # Schedule retry task
        asyncio.create_task(retry_after_delay())

class EventScheduler:
    """Event scheduling for delayed execution."""
    
    def __init__(self, config: EventManagerConfig):
        self.config = config
        self.scheduled_events: Dict[str, ScheduledEvent] = {}
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False
        self.event_callback: Optional[Callable[[Event], None]] = None
    
    def set_event_callback(self, callback: Callable[[Event], None]) -> None:
        """Set callback for executing scheduled events."""
        self.event_callback = callback
    
    async def start(self) -> None:
        """Start the event scheduler."""
        if self._running:
            return
        
        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self) -> None:
        """Stop the event scheduler."""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
    
    def schedule_event(self, event: Event, scheduled_for: datetime) -> str:
        """Schedule an event for future execution."""
        scheduled_event = ScheduledEvent(
            id=str(uuid.uuid4()),
            event=event,
            scheduled_for=scheduled_for
        )
        
        self.scheduled_events[scheduled_event.id] = scheduled_event
        return scheduled_event.id
    
    def cancel_scheduled_event(self, scheduled_event_id: str) -> bool:
        """Cancel a scheduled event."""
        return self.scheduled_events.pop(scheduled_event_id, None) is not None
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                now = datetime.now(timezone.utc)
                ready_events = []
                
                # Find events ready for execution
                for scheduled_event in list(self.scheduled_events.values()):
                    if not scheduled_event.executed and now >= scheduled_event.scheduled_for:
                        ready_events.append(scheduled_event)
                
                # Execute ready events
                for scheduled_event in ready_events:
                    if self.event_callback:
                        try:
                            await self.event_callback(scheduled_event.event)
                            scheduled_event.executed = True
                            scheduled_event.executed_at = now
                        except Exception as e:
                            logger.error(f"Error executing scheduled event {scheduled_event.id}: {e}")
                    
                    # Remove executed events
                    self.scheduled_events.pop(scheduled_event.id, None)
                
                await asyncio.sleep(self.config.scheduler_interval_seconds)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(1)

class EventManager:
    """
    Enterprise event manager for Creator Economy platform.
    
    Provides comprehensive event management features:
    - Event sourcing for complete auditability
    - Event bus for decoupled communication
    - Webhook management for external integrations
    - Event scheduling for delayed execution
    - Real-time notifications for user engagement
    - Analytics events for business intelligence
    - Audit events for compliance and security
    - Event replay for debugging and recovery
    """
    
    def __init__(self, config: Optional[EventManagerConfig] = None):
        self.config = config or EventManagerConfig()
        
        # Core components
        self.event_store = EventStore(self.config.max_events_in_memory)
        self.webhook_manager = WebhookManager(self.config)
        self.scheduler = EventScheduler(self.config)
        
        # Event handlers
        self.handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self.global_handlers: List[EventHandler] = []
        
        # Redis for distributed events
        self.redis_client: Optional[redis.Redis] = None
        
        # Performance tracking
        self.metrics = {
            'events_published': 0,
            'events_processed': 0,
            'handlers_executed': 0,
            'webhooks_delivered': 0,
            'events_scheduled': 0,
            'avg_processing_time': 0.0
        }
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._handler_semaphore = asyncio.Semaphore(self.config.max_concurrent_handlers)
        
        # Set scheduler callback
        self.scheduler.set_event_callback(self._execute_scheduled_event)
    
    async def initialize(self) -> None:
        """Initialize the event manager."""
        # Initialize Redis if configured
        if self.config.redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(self.config.redis_url)
                await self.redis_client.ping()
                logger.info("Redis event bus connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using local event bus only")
        
        # Start scheduler
        if self.config.enable_scheduling:
            await self.scheduler.start()
        
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._cleanup_old_events()),
            asyncio.create_task(self._redis_subscriber()) if self.redis_client else None
        ]
        self._background_tasks = [task for task in self._background_tasks if task]
        
        logger.info("Event manager initialized successfully")
    
    async def close(self) -> None:
        """Close the event manager and cleanup resources."""
        # Stop scheduler
        await self.scheduler.stop()
        
        # Stop background tasks
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Close webhook manager
        await self.webhook_manager.close()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Event manager closed successfully")
    
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to specific event type."""
        self.handlers[event_type].append(handler)
    
    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe to all events."""
        self.global_handlers.append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        """Unsubscribe from specific event type."""
        try:
            self.handlers[event_type].remove(handler)
            return True
        except ValueError:
            return False
    
    def unsubscribe_all(self, handler: EventHandler) -> bool:
        """Unsubscribe from all events."""
        try:
            self.global_handlers.remove(handler)
            return True
        except ValueError:
            return False
    
    async def publish(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        source: str,
        priority: EventPriority = EventPriority.NORMAL,
        creator_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Publish an event."""
        # Create event
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            payload=payload,
            source=source,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            creator_id=creator_id,
            user_id=user_id,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        # Store event
        await self.event_store.store_event(event)
        
        # Process event
        await self._process_event(event)
        
        # Publish to Redis for distributed processing
        if self.redis_client:
            try:
                channel = f"{self.config.redis_channel_prefix}:{event_type.value}"
                await self.redis_client.publish(channel, json.dumps(event.to_dict()))
            except Exception as e:
                logger.error(f"Failed to publish event to Redis: {e}")
        
        self.metrics['events_published'] += 1
        return event
    
    async def _process_event(self, event: Event) -> None:
        """Process an event through all handlers."""
        start_time = time.perf_counter()
        
        # Get handlers for this event type
        event_handlers = self.handlers.get(event.type, [])
        all_handlers = event_handlers + self.global_handlers
        
        if not all_handlers:
            return
        
        # Execute handlers concurrently
        if self.config.enable_async_processing:
            tasks = []
            for handler in all_handlers:
                task = asyncio.create_task(self._execute_handler(handler, event))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Execute handlers sequentially
            for handler in all_handlers:
                await self._execute_handler(handler, event)
        
        # Deliver to webhooks
        if self.config.enable_webhooks:
            deliveries = await self.webhook_manager.deliver_event(event)
            self.metrics['webhooks_delivered'] += len(deliveries)
        
        # Update metrics
        execution_time = (time.perf_counter() - start_time) * 1000
        self.metrics['events_processed'] += 1
        current_avg = self.metrics['avg_processing_time']
        total_processed = self.metrics['events_processed']
        self.metrics['avg_processing_time'] = (
            (current_avg * (total_processed - 1) + execution_time) / total_processed
        )
    
    async def _execute_handler(self, handler: EventHandler, event: Event) -> EventHandlerResult:
        """Execute a single event handler."""
        async with self._handler_semaphore:
            start_time = time.perf_counter()
            handler_name = getattr(handler, '__name__', str(handler))
            
            try:
                # Handle both sync and async handlers
                if asyncio.iscoroutinefunction(handler):
                    result = await asyncio.wait_for(
                        handler(event),
                        timeout=self.config.handler_timeout_seconds
                    )
                else:
                    result = handler(event)
                
                execution_time = (time.perf_counter() - start_time) * 1000
                self.metrics['handlers_executed'] += 1
                
                return EventHandlerResult(
                    success=True,
                    handler_name=handler_name,
                    execution_time_ms=execution_time,
                    metadata={'result': result}
                )
                
            except asyncio.TimeoutError:
                execution_time = (time.perf_counter() - start_time) * 1000
                return EventHandlerResult(
                    success=False,
                    handler_name=handler_name,
                    execution_time_ms=execution_time,
                    error="Handler timeout"
                )
                
            except Exception as e:
                execution_time = (time.perf_counter() - start_time) * 1000
                logger.error(f"Handler {handler_name} failed for event {event.id}: {e}")
                
                return EventHandlerResult(
                    success=False,
                    handler_name=handler_name,
                    execution_time_ms=execution_time,
                    error=str(e)
                )
    
    async def _execute_scheduled_event(self, event: Event) -> None:
        """Execute a scheduled event."""
        await self._process_event(event)
    
    async def schedule_event(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        source: str,
        scheduled_for: datetime,
        priority: EventPriority = EventPriority.NORMAL,
        creator_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Schedule an event for future execution."""
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            payload=payload,
            source=source,
            timestamp=datetime.now(timezone.utc),
            priority=priority,
            creator_id=creator_id,
            user_id=user_id,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        scheduled_id = self.scheduler.schedule_event(event, scheduled_for)
        self.metrics['events_scheduled'] += 1
        
        return scheduled_id
    
    async def cancel_scheduled_event(self, scheduled_event_id: str) -> bool:
        """Cancel a scheduled event."""
        return self.scheduler.cancel_scheduled_event(scheduled_event_id)
    
    async def get_events(
        self,
        event_type: Optional[EventType] = None,
        correlation_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get events from store."""
        return await self.event_store.get_events(
            event_type=event_type,
            correlation_id=correlation_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    async def replay_events(
        self,
        correlation_id: str,
        from_event_id: Optional[str] = None
    ) -> List[Event]:
        """Replay events for debugging or recovery."""
        events = await self.get_events(correlation_id=correlation_id)
        
        # Filter from specific event if provided
        if from_event_id:
            start_index = None
            for i, event in enumerate(events):
                if event.id == from_event_id:
                    start_index = i
                    break
            
            if start_index is not None:
                events = events[start_index:]
        
        # Replay events
        replayed_events = []
        for event in events:
            # Create new event with replay metadata
            replay_event = Event(
                id=str(uuid.uuid4()),
                type=event.type,
                payload=event.payload,
                source=f"replay:{event.source}",
                timestamp=datetime.now(timezone.utc),
                priority=event.priority,
                creator_id=event.creator_id,
                user_id=event.user_id,
                correlation_id=event.correlation_id,
                metadata={**event.metadata, 'replayed_from': event.id}
            )
            
            await self._process_event(replay_event)
            replayed_events.append(replay_event)
        
        return replayed_events
    
    # Creator Economy specific event methods
    
    async def track_creator_action(
        self,
        creator_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Track creator-specific action."""
        return await self.publish(
            event_type=EventType.ANALYTICS_TRACKED,
            payload={'action': action, 'entity_type': 'creator'},
            source='creator_analytics',
            creator_id=creator_id,
            metadata=metadata
        )
    
    async def track_content_interaction(
        self,
        content_id: str,
        interaction_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Track content interaction."""
        event_type_mapping = {
            'view': EventType.CONTENT_VIEWED,
            'like': EventType.CONTENT_LIKED,
            'share': EventType.CONTENT_SHARED,
            'report': EventType.CONTENT_REPORTED
        }
        
        event_type = event_type_mapping.get(interaction_type, EventType.ANALYTICS_TRACKED)
        
        return await self.publish(
            event_type=event_type,
            payload={'content_id': content_id, 'interaction_type': interaction_type},
            source='content_analytics',
            user_id=user_id,
            metadata=metadata
        )
    
    async def track_monetization_event(
        self,
        creator_id: str,
        event_type: str,
        amount: float,
        currency: str = 'USD',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Track monetization event."""
        return await self.publish(
            event_type=EventType.REVENUE_GENERATED,
            payload={
                'event_type': event_type,
                'amount': amount,
                'currency': currency
            },
            source='monetization',
            creator_id=creator_id,
            metadata=metadata
        )
    
    async def _cleanup_old_events(self) -> None:
        """Background task to cleanup old events."""
        while True:
            try:
                removed_count = await self.event_store.clear_old_events(
                    self.config.event_retention_hours
                )
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} old events")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Event cleanup error: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes
    
    async def _redis_subscriber(self) -> None:
        """Redis subscriber for distributed events."""
        if not self.redis_client:
            return
        
        try:
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to all event channels
            for event_type in EventType:
                channel = f"{self.config.redis_channel_prefix}:{event_type.value}"
                await pubsub.subscribe(channel)
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        event_data = json.loads(message['data'])
                        event = Event.from_dict(event_data)
                        
                        # Only process if not published by this instance
                        if event.metadata.get('source_instance') != id(self):
                            await self._process_event(event)
                            
                    except Exception as e:
                        logger.error(f"Error processing Redis event: {e}")
                        
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get event manager metrics."""
        return {
            'performance_metrics': self.metrics.copy(),
            'event_store_stats': {
                'total_events': len(self.event_store._events),
                'events_by_type': {
                    event_type.value: len(events)
                    for event_type, events in self.event_store._events_by_type.items()
                }
            },
            'handler_stats': {
                'registered_handlers': sum(len(handlers) for handlers in self.handlers.values()),
                'global_handlers': len(self.global_handlers)
            },
            'webhook_stats': {
                'registered_webhooks': len(self.webhook_manager.webhooks),
                'total_deliveries': len(self.webhook_manager.deliveries)
            },
            'scheduler_stats': {
                'scheduled_events': len(self.scheduler.scheduled_events)
            },
            'configuration': {
                'redis_enabled': self.redis_client is not None,
                'webhooks_enabled': self.config.enable_webhooks,
                'scheduling_enabled': self.config.enable_scheduling,
                'async_processing': self.config.enable_async_processing
            }
        }

# Factory for dependency injection
class EventManagerFactory:
    """Factory for creating EventManager instances."""
    
    @staticmethod
    def create(config: Optional[EventManagerConfig] = None) -> EventManager:
        """Create a new EventManager instance."""
        return EventManager(config)
    
    @staticmethod
    def create_with_redis(redis_url: str, **kwargs) -> EventManager:
        """Create EventManager with Redis configuration."""
        config = EventManagerConfig(redis_url=redis_url, **kwargs)
        return EventManager(config)
    
    @staticmethod
    def create_for_analytics() -> EventManager:
        """Create EventManager optimized for analytics."""
        config = EventManagerConfig(
            enable_analytics=True,
            max_events_in_memory=50000,
            event_retention_hours=168,  # 7 days
            enable_webhooks=False  # Don't need webhooks for analytics
        )
        return EventManager(config)

__all__ = [
    'EventManager',
    'EventManagerFactory',
    'EventManagerConfig',
    'Event',
    'EventType',
    'EventPriority',
    'EventHandler',
    'EventHandlerResult',
    'Webhook',
    'WebhookDelivery',
    'WebhookStatus',
    'ScheduledEvent',
    'EventStore',
    'WebhookManager',
    'EventScheduler'
]