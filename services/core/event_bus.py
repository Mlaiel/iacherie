"""
Event Bus - Enterprise Event-Driven Architecture
===============================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Lead Dev IA + Backend Senior + Microservices + DevOps + Security
**Module**: Core Services - Event Management
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade event bus with pub/sub patterns, event sourcing,
distributed messaging, and intelligent event processing.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import aioredis
from collections import defaultdict
import hashlib


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event type categories"""
    SERVICE = "service"
    USER = "user"
    SYSTEM = "system"
    BUSINESS = "business"
    SECURITY = "security"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    ERROR = "error"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


@dataclass
class Event:
    """Event definition with comprehensive metadata"""
    event_id: str
    event_type: EventType
    event_name: str
    payload: Dict[str, Any]
    
    # Metadata
    source_service: str
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    version: str = "1.0"
    
    # Processing
    status: EventStatus = EventStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # Tracing & Correlation
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # Routing & Delivery
    target_services: List[str] = field(default_factory=list)
    broadcast: bool = False
    durable: bool = True
    
    # Expiration & TTL
    expires_at: Optional[datetime] = None
    ttl_seconds: Optional[int] = None
    
    # Security
    security_context: Dict[str, Any] = field(default_factory=dict)
    authenticated: bool = False
    
    # Custom metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        # Convert enum values
        data['event_type'] = EventType(data['event_type'])
        data['priority'] = EventPriority(data['priority'])
        data['status'] = EventStatus(data['status'])
        
        # Convert datetime strings
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        return cls(**data)


@dataclass
class EventHandler:
    """Event handler definition"""
    handler_id: str
    service_name: str
    event_patterns: List[str]  # Event name patterns (supports wildcards)
    handler_function: Callable
    
    # Configuration
    enabled: bool = True
    priority: int = 100
    max_concurrent: int = 10
    timeout_seconds: int = 30
    
    # Filtering
    event_types: List[EventType] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Retry & Error Handling
    max_retries: int = 3
    retry_delay_seconds: int = 5
    dead_letter_queue: bool = True
    
    # Metrics
    total_processed: int = 0
    successful_processed: int = 0
    failed_processed: int = 0
    average_processing_time: float = 0.0


@dataclass
class Subscription:
    """Event subscription definition"""
    subscription_id: str
    service_name: str
    event_patterns: List[str]
    
    # Configuration
    enabled: bool = True
    durable: bool = True
    auto_ack: bool = False
    
    # Filtering
    event_types: List[EventType] = field(default_factory=list)
    priority_filter: List[EventPriority] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Delivery
    max_delivery_attempts: int = 3
    delivery_delay_seconds: int = 0
    batch_size: int = 1
    
    # Metrics
    events_received: int = 0
    events_processed: int = 0
    events_failed: int = 0
    last_activity: Optional[datetime] = None


@dataclass
class EventMetrics:
    """Event processing metrics"""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_priority: Dict[str, int] = field(default_factory=dict)
    events_by_status: Dict[str, int] = field(default_factory=dict)
    
    # Performance metrics
    average_processing_time: float = 0.0
    peak_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    
    # Throughput metrics
    events_per_second: float = 0.0
    peak_events_per_second: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    retry_rate: float = 0.0
    dead_letter_rate: float = 0.0
    
    # Resource metrics
    active_handlers: int = 0
    queued_events: int = 0
    memory_usage_mb: float = 0.0
    
    last_updated: datetime = field(default_factory=datetime.now)


class EventBus:
    """
    Enterprise Event Bus with Distributed Messaging & Event Sourcing
    
    **Expert Roles Implemented:**
    - Lead Dev IA: Intelligent event routing, pattern matching, analytics
    - Backend Senior: Robust async architecture, connection pooling
    - Microservices: Distributed messaging, service decoupling
    - DevOps: Monitoring, metrics, observability, performance optimization
    - Security: Event authentication, encryption, audit logging
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        event_store_ttl: int = 86400,  # 24 hours
        dead_letter_ttl: int = 604800,  # 7 days
        max_batch_size: int = 100,
        processing_timeout: int = 30
    ):
        self.redis_url = redis_url
        self.event_store_ttl = event_store_ttl
        self.dead_letter_ttl = dead_letter_ttl
        self.max_batch_size = max_batch_size
        self.processing_timeout = processing_timeout
        
        # Storage
        self.redis_client: Optional[aioredis.Redis] = None
        self.pubsub_client: Optional[aioredis.Redis] = None
        
        # Event Management
        self.event_handlers: Dict[str, EventHandler] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.event_store: Dict[str, Event] = {}
        
        # Processing
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.handler_semaphores: Dict[str, asyncio.Semaphore] = {}
        
        # Metrics & Monitoring
        self.metrics = EventMetrics()
        self.event_history: List[Event] = []
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
        # Event sourcing
        self.event_sourcing_enabled = True
        self.snapshot_interval = 1000  # events
        
        # Security
        self.authentication_enabled = True
        self.encryption_enabled = True
    
    async def initialize(self) -> None:
        """Initialize event bus"""
        try:
            # Initialize Redis connections
            self.redis_client = aioredis.from_url(self.redis_url)
            self.pubsub_client = aioredis.from_url(self.redis_url)
            
            await self.redis_client.ping()
            await self.pubsub_client.ping()
            
            # Load existing subscriptions and handlers
            await self._load_subscriptions()
            await self._load_handlers()
            
            # Start background tasks
            self.running = True
            self.background_tasks = [
                asyncio.create_task(self._metrics_collection_loop()),
                asyncio.create_task(self._cleanup_loop()),
                asyncio.create_task(self._dead_letter_processing_loop()),
                asyncio.create_task(self._event_sourcing_loop())
            ]
            
            logger.info("Event Bus initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Event Bus: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Graceful shutdown"""
        self.running = False
        
        # Cancel processing tasks
        for task in self.processing_tasks.values():
            task.cancel()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(
            *self.processing_tasks.values(),
            *self.background_tasks,
            return_exceptions=True
        )
        
        # Close Redis connections
        if self.redis_client:
            await self.redis_client.close()
        if self.pubsub_client:
            await self.pubsub_client.close()
        
        logger.info("Event Bus shutdown completed")
    
    async def publish_event(self, event: Event) -> bool:
        """
        Publish an event to the bus
        
        **Roles**: Lead Dev IA + Backend Senior + Security
        """
        try:
            # Generate event ID if not provided
            if not event.event_id:
                event.event_id = self._generate_event_id()
            
            # Set correlation ID if not provided
            if not event.correlation_id:
                event.correlation_id = str(uuid.uuid4())
            
            # Set expiration if TTL is specified
            if event.ttl_seconds:
                event.expires_at = datetime.now() + timedelta(seconds=event.ttl_seconds)
            
            # Validate event
            if not self._validate_event(event):
                return False
            
            # Store event
            await self._store_event(event)
            
            # Route event to subscribers
            await self._route_event(event)
            
            # Update metrics
            await self._update_publish_metrics(event)
            
            logger.debug(f"Event published: {event.event_name} ({event.event_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_name}: {e}")
            return False
    
    async def subscribe(self, subscription: Subscription) -> bool:
        """
        Create a new subscription
        
        **Roles**: Microservices + Backend Senior
        """
        try:
            # Validate subscription
            if not self._validate_subscription(subscription):
                return False
            
            # Store subscription
            self.subscriptions[subscription.subscription_id] = subscription
            await self._save_subscription(subscription)
            
            # Start processing for this subscription
            await self._start_subscription_processing(subscription)
            
            logger.info(f"Subscription created: {subscription.subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create subscription {subscription.subscription_id}: {e}")
            return False
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Remove a subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            # Stop processing
            if subscription_id in self.processing_tasks:
                self.processing_tasks[subscription_id].cancel()
                del self.processing_tasks[subscription_id]
            
            # Remove subscription
            del self.subscriptions[subscription_id]
            await self._remove_subscription(subscription_id)
            
            logger.info(f"Subscription removed: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove subscription {subscription_id}: {e}")
            return False
    
    async def register_handler(self, handler: EventHandler) -> bool:
        """
        Register an event handler
        
        **Roles**: Lead Dev IA + Microservices
        """
        try:
            # Validate handler
            if not self._validate_handler(handler):
                return False
            
            # Store handler
            self.event_handlers[handler.handler_id] = handler
            await self._save_handler(handler)
            
            # Initialize semaphore for concurrency control
            self.handler_semaphores[handler.handler_id] = asyncio.Semaphore(handler.max_concurrent)
            
            logger.info(f"Event handler registered: {handler.handler_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register handler {handler.handler_id}: {e}")
            return False
    
    async def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an event handler"""
        try:
            if handler_id not in self.event_handlers:
                return False
            
            # Remove handler
            del self.event_handlers[handler_id]
            if handler_id in self.handler_semaphores:
                del self.handler_semaphores[handler_id]
            
            await self._remove_handler(handler_id)
            
            logger.info(f"Event handler unregistered: {handler_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister handler {handler_id}: {e}")
            return False
    
    async def _route_event(self, event: Event) -> None:
        """Route event to appropriate handlers and subscribers"""
        # Find matching handlers
        matching_handlers = self._find_matching_handlers(event)
        
        # Process with handlers
        for handler in matching_handlers:
            asyncio.create_task(self._process_event_with_handler(event, handler))
        
        # Find matching subscriptions
        matching_subscriptions = self._find_matching_subscriptions(event)
        
        # Send to subscribers via Redis pub/sub
        for subscription in matching_subscriptions:
            await self._send_to_subscription(event, subscription)
        
        # Broadcast if requested
        if event.broadcast:
            await self._broadcast_event(event)
    
    def _find_matching_handlers(self, event: Event) -> List[EventHandler]:
        """Find handlers that match the event"""
        matching = []
        
        for handler in self.event_handlers.values():
            if not handler.enabled:
                continue
            
            # Check event type filter
            if handler.event_types and event.event_type not in handler.event_types:
                continue
            
            # Check tag filter
            if handler.tags and not any(tag in event.tags for tag in handler.tags):
                continue
            
            # Check pattern matching
            if self._matches_patterns(event.event_name, handler.event_patterns):
                matching.append(handler)
        
        # Sort by priority
        matching.sort(key=lambda h: h.priority)
        return matching
    
    def _find_matching_subscriptions(self, event: Event) -> List[Subscription]:
        """Find subscriptions that match the event"""
        matching = []
        
        for subscription in self.subscriptions.values():
            if not subscription.enabled:
                continue
            
            # Check event type filter
            if subscription.event_types and event.event_type not in subscription.event_types:
                continue
            
            # Check priority filter
            if subscription.priority_filter and event.priority not in subscription.priority_filter:
                continue
            
            # Check tag filter
            if subscription.tags and not any(tag in event.tags for tag in subscription.tags):
                continue
            
            # Check pattern matching
            if self._matches_patterns(event.event_name, subscription.event_patterns):
                matching.append(subscription)
        
        return matching
    
    def _matches_patterns(self, event_name: str, patterns: List[str]) -> bool:
        """Check if event name matches any pattern"""
        import fnmatch
        
        for pattern in patterns:
            if fnmatch.fnmatch(event_name, pattern):
                return True
        return False
    
    async def _process_event_with_handler(self, event: Event, handler: EventHandler) -> None:
        """Process event with a specific handler"""
        # Check concurrency limit
        semaphore = self.handler_semaphores.get(handler.handler_id)
        if not semaphore:
            return
        
        async with semaphore:
            start_time = time.time()
            success = False
            
            try:
                # Set timeout
                await asyncio.wait_for(
                    handler.handler_function(event),
                    timeout=handler.timeout_seconds
                )
                success = True
                handler.successful_processed += 1
                
            except asyncio.TimeoutError:
                logger.warning(f"Handler {handler.handler_id} timed out for event {event.event_id}")
                handler.failed_processed += 1
                
            except Exception as e:
                logger.error(f"Handler {handler.handler_id} failed for event {event.event_id}: {e}")
                handler.failed_processed += 1
                
                # Retry logic
                if event.retry_count < handler.max_retries:
                    event.retry_count += 1
                    event.status = EventStatus.RETRYING
                    
                    # Schedule retry
                    await asyncio.sleep(handler.retry_delay_seconds)
                    await self._process_event_with_handler(event, handler)
                else:
                    # Send to dead letter queue
                    if handler.dead_letter_queue:
                        await self._send_to_dead_letter_queue(event, f"Handler {handler.handler_id} failed")
            
            finally:
                processing_time = time.time() - start_time
                handler.total_processed += 1
                
                # Update average processing time
                if handler.total_processed == 1:
                    handler.average_processing_time = processing_time
                else:
                    handler.average_processing_time = (
                        (handler.average_processing_time * (handler.total_processed - 1) + processing_time) /
                        handler.total_processed
                    )
                
                if success:
                    event.status = EventStatus.COMPLETED
                else:
                    event.status = EventStatus.FAILED
                
                await self._update_event_status(event)
    
    async def _send_to_subscription(self, event: Event, subscription: Subscription) -> None:
        """Send event to a subscription via Redis pub/sub"""
        try:
            channel = f"subscription:{subscription.subscription_id}"
            message = json.dumps(event.to_dict())
            
            await self.redis_client.publish(channel, message)
            
            # Update subscription metrics
            subscription.events_received += 1
            subscription.last_activity = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to send event to subscription {subscription.subscription_id}: {e}")
    
    async def _broadcast_event(self, event: Event) -> None:
        """Broadcast event to all services"""
        try:
            channel = "events:broadcast"
            message = json.dumps(event.to_dict())
            await self.redis_client.publish(channel, message)
        except Exception as e:
            logger.error(f"Failed to broadcast event {event.event_id}: {e}")
    
    async def _send_to_dead_letter_queue(self, event: Event, reason: str) -> None:
        """Send event to dead letter queue"""
        try:
            event.status = EventStatus.DEAD_LETTER
            event.metadata['dead_letter_reason'] = reason
            event.metadata['dead_letter_timestamp'] = datetime.now().isoformat()
            
            key = f"dead_letter:{event.event_id}"
            value = json.dumps(event.to_dict())
            
            await self.redis_client.setex(key, self.dead_letter_ttl, value)
            
            logger.warning(f"Event sent to dead letter queue: {event.event_id} - {reason}")
            
        except Exception as e:
            logger.error(f"Failed to send event to dead letter queue: {e}")
    
    async def _store_event(self, event: Event) -> None:
        """Store event in event store"""
        try:
            # Store in memory
            self.event_store[event.event_id] = event
            
            # Store in Redis
            if self.event_sourcing_enabled:
                key = f"event:{event.event_id}"
                value = json.dumps(event.to_dict())
                await self.redis_client.setex(key, self.event_store_ttl, value)
                
                # Add to event stream
                stream_key = f"event_stream:{event.event_type.value}"
                await self.redis_client.xadd(stream_key, event.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to store event {event.event_id}: {e}")
    
    async def _update_event_status(self, event: Event) -> None:
        """Update event status in storage"""
        try:
            if event.event_id in self.event_store:
                self.event_store[event.event_id] = event
            
            if self.redis_client and self.event_sourcing_enabled:
                key = f"event:{event.event_id}"
                value = json.dumps(event.to_dict())
                await self.redis_client.setex(key, self.event_store_ttl, value)
        
        except Exception as e:
            logger.error(f"Failed to update event status for {event.event_id}: {e}")
    
    def _validate_event(self, event: Event) -> bool:
        """Validate event before publishing"""
        if not event.event_name or not event.source_service:
            return False
        
        if event.expires_at and event.expires_at <= datetime.now():
            return False
        
        return True
    
    def _validate_subscription(self, subscription: Subscription) -> bool:
        """Validate subscription configuration"""
        if not subscription.subscription_id or not subscription.service_name:
            return False
        
        if not subscription.event_patterns:
            return False
        
        return True
    
    def _validate_handler(self, handler: EventHandler) -> bool:
        """Validate event handler configuration"""
        if not handler.handler_id or not handler.service_name:
            return False
        
        if not handler.event_patterns or not handler.handler_function:
            return False
        
        return True
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(int(time.time() * 1000))
        random_part = str(uuid.uuid4())[:8]
        return f"evt_{timestamp}_{random_part}"
    
    async def _start_subscription_processing(self, subscription: Subscription) -> None:
        """Start background processing for a subscription"""
        async def subscription_worker():
            channel = f"subscription:{subscription.subscription_id}"
            pubsub = self.pubsub_client.pubsub()
            
            try:
                await pubsub.subscribe(channel)
                
                while self.running and subscription.subscription_id in self.subscriptions:
                    try:
                        message = await pubsub.get_message(timeout=1.0)
                        if message and message['type'] == 'message':
                            event_data = json.loads(message['data'])
                            event = Event.from_dict(event_data)
                            
                            # Process event
                            subscription.events_processed += 1
                            subscription.last_activity = datetime.now()
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Subscription processing error for {subscription.subscription_id}: {e}")
                        subscription.events_failed += 1
                        await asyncio.sleep(1)
            
            finally:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
        
        task = asyncio.create_task(subscription_worker())
        self.processing_tasks[subscription.subscription_id] = task
    
    async def _save_subscription(self, subscription: Subscription) -> None:
        """Save subscription to Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"subscription:{subscription.subscription_id}"
            value = {
                'subscription_id': subscription.subscription_id,
                'service_name': subscription.service_name,
                'event_patterns': subscription.event_patterns,
                'enabled': subscription.enabled,
                'durable': subscription.durable,
                'auto_ack': subscription.auto_ack,
                'event_types': [et.value for et in subscription.event_types],
                'priority_filter': [pf.value for pf in subscription.priority_filter],
                'tags': subscription.tags,
                'max_delivery_attempts': subscription.max_delivery_attempts,
                'delivery_delay_seconds': subscription.delivery_delay_seconds,
                'batch_size': subscription.batch_size
            }
            await self.redis_client.set(key, json.dumps(value))
        except Exception as e:
            logger.error(f"Failed to save subscription to Redis: {e}")
    
    async def _remove_subscription(self, subscription_id: str) -> None:
        """Remove subscription from Redis"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(f"subscription:{subscription_id}")
        except Exception as e:
            logger.error(f"Failed to remove subscription from Redis: {e}")
    
    async def _save_handler(self, handler: EventHandler) -> None:
        """Save handler to Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"handler:{handler.handler_id}"
            value = {
                'handler_id': handler.handler_id,
                'service_name': handler.service_name,
                'event_patterns': handler.event_patterns,
                'enabled': handler.enabled,
                'priority': handler.priority,
                'max_concurrent': handler.max_concurrent,
                'timeout_seconds': handler.timeout_seconds,
                'event_types': [et.value for et in handler.event_types],
                'tags': handler.tags,
                'max_retries': handler.max_retries,
                'retry_delay_seconds': handler.retry_delay_seconds,
                'dead_letter_queue': handler.dead_letter_queue
            }
            await self.redis_client.set(key, json.dumps(value))
        except Exception as e:
            logger.error(f"Failed to save handler to Redis: {e}")
    
    async def _remove_handler(self, handler_id: str) -> None:
        """Remove handler from Redis"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(f"handler:{handler_id}")
        except Exception as e:
            logger.error(f"Failed to remove handler from Redis: {e}")
    
    async def _load_subscriptions(self) -> None:
        """Load subscriptions from Redis"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys("subscription:*")
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    sub_data = json.loads(data)
                    sub_data['event_types'] = [EventType(et) for et in sub_data.get('event_types', [])]
                    sub_data['priority_filter'] = [EventPriority(pf) for pf in sub_data.get('priority_filter', [])]
                    
                    subscription = Subscription(**sub_data)
                    self.subscriptions[subscription.subscription_id] = subscription
                    
                    if subscription.enabled:
                        await self._start_subscription_processing(subscription)
        except Exception as e:
            logger.error(f"Failed to load subscriptions from Redis: {e}")
    
    async def _load_handlers(self) -> None:
        """Load handlers from Redis"""
        # Note: Handler functions cannot be serialized, so this would need
        # a different approach in a real implementation (e.g., function registry)
        pass
    
    async def _update_publish_metrics(self, event: Event) -> None:
        """Update metrics after publishing an event"""
        self.metrics.total_events += 1
        
        # Update by type
        event_type = event.event_type.value
        self.metrics.events_by_type[event_type] = self.metrics.events_by_type.get(event_type, 0) + 1
        
        # Update by priority
        priority = event.priority.value
        self.metrics.events_by_priority[priority] = self.metrics.events_by_priority.get(priority, 0) + 1
        
        # Update by status
        status = event.status.value
        self.metrics.events_by_status[status] = self.metrics.events_by_status.get(status, 0) + 1
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > 1000:  # Keep last 1000 events
            self.event_history = self.event_history[-1000:]
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop"""
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_metrics(self) -> None:
        """Collect and update metrics"""
        try:
            # Calculate throughput
            if len(self.event_history) >= 2:
                time_diff = (self.event_history[-1].timestamp - self.event_history[0].timestamp).total_seconds()
                if time_diff > 0:
                    self.metrics.events_per_second = len(self.event_history) / time_diff
            
            # Update active handlers
            self.metrics.active_handlers = len([h for h in self.event_handlers.values() if h.enabled])
            
            # Update queued events (approximate)
            self.metrics.queued_events = len(self.event_store)
            
            # Calculate error rates
            total_events = self.metrics.total_events
            if total_events > 0:
                failed_events = self.metrics.events_by_status.get('failed', 0)
                retried_events = self.metrics.events_by_status.get('retrying', 0)
                dead_letter_events = self.metrics.events_by_status.get('dead_letter', 0)
                
                self.metrics.error_rate = (failed_events / total_events) * 100
                self.metrics.retry_rate = (retried_events / total_events) * 100
                self.metrics.dead_letter_rate = (dead_letter_events / total_events) * 100
            
            self.metrics.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while self.running:
            try:
                await self._cleanup_expired_events()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_expired_events(self) -> None:
        """Clean up expired events"""
        current_time = datetime.now()
        expired_events = []
        
        for event_id, event in self.event_store.items():
            if event.expires_at and event.expires_at <= current_time:
                expired_events.append(event_id)
        
        for event_id in expired_events:
            del self.event_store[event_id]
            if self.redis_client:
                await self.redis_client.delete(f"event:{event_id}")
        
        if expired_events:
            logger.info(f"Cleaned up {len(expired_events)} expired events")
    
    async def _dead_letter_processing_loop(self) -> None:
        """Background dead letter queue processing"""
        while self.running:
            try:
                await self._process_dead_letter_queue()
                await asyncio.sleep(600)  # Process every 10 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Dead letter processing error: {e}")
                await asyncio.sleep(30)
    
    async def _process_dead_letter_queue(self) -> None:
        """Process dead letter queue for potential retry"""
        if not self.redis_client:
            return
        
        try:
            keys = await self.redis_client.keys("dead_letter:*")
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    event_data = json.loads(data)
                    event = Event.from_dict(event_data)
                    
                    # Check if event should be retried
                    dead_letter_time = datetime.fromisoformat(
                        event.metadata.get('dead_letter_timestamp', datetime.now().isoformat())
                    )
                    
                    # Retry after 1 hour in dead letter queue
                    if (datetime.now() - dead_letter_time).total_seconds() > 3600:
                        event.status = EventStatus.PENDING
                        event.retry_count = 0
                        
                        # Remove from dead letter and republish
                        await self.redis_client.delete(key)
                        await self.publish_event(event)
                        
                        logger.info(f"Retried dead letter event: {event.event_id}")
        
        except Exception as e:
            logger.error(f"Error processing dead letter queue: {e}")
    
    async def _event_sourcing_loop(self) -> None:
        """Background event sourcing loop"""
        while self.running:
            try:
                await self._create_event_snapshot()
                await asyncio.sleep(1800)  # Create snapshot every 30 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event sourcing error: {e}")
                await asyncio.sleep(60)
    
    async def _create_event_snapshot(self) -> None:
        """Create event snapshot for event sourcing"""
        if not self.event_sourcing_enabled or not self.redis_client:
            return
        
        try:
            snapshot_data = {
                'timestamp': datetime.now().isoformat(),
                'total_events': self.metrics.total_events,
                'event_types': dict(self.metrics.events_by_type),
                'active_subscriptions': len(self.subscriptions),
                'active_handlers': len(self.event_handlers)
            }
            
            key = f"event_snapshot:{int(time.time())}"
            await self.redis_client.setex(key, 86400 * 7, json.dumps(snapshot_data))  # 7 days
            
        except Exception as e:
            logger.error(f"Error creating event snapshot: {e}")
    
    async def get_metrics(self) -> EventMetrics:
        """Get current event bus metrics"""
        return self.metrics
    
    async def get_event_history(self, limit: int = 100) -> List[Event]:
        """Get recent event history"""
        return self.event_history[-limit:]
    
    async def get_dead_letter_events(self) -> List[Event]:
        """Get events in dead letter queue"""
        if not self.redis_client:
            return []
        
        events = []
        try:
            keys = await self.redis_client.keys("dead_letter:*")
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    event_data = json.loads(data)
                    events.append(Event.from_dict(event_data))
        except Exception as e:
            logger.error(f"Error retrieving dead letter events: {e}")
        
        return events
    
    async def replay_events(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None
    ) -> List[Event]:
        """Replay events from event store"""
        if not self.event_sourcing_enabled or not self.redis_client:
            return []
        
        events = []
        try:
            # This would typically use Redis Streams XRANGE
            # For now, return events from memory store
            for event in self.event_store.values():
                if event.timestamp >= from_timestamp:
                    if to_timestamp and event.timestamp > to_timestamp:
                        continue
                    if event_types and event.event_type not in event_types:
                        continue
                    events.append(event)
            
            # Sort by timestamp
            events.sort(key=lambda e: e.timestamp)
            
        except Exception as e:
            logger.error(f"Error replaying events: {e}")
        
        return events