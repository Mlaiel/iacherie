"""
🚌 Event Bus Service
Enterprise event-driven architecture with real-time messaging and event sourcing

Demonstrates: Microservices + DevOps + Backend Senior + DBA expertise
Features: Event streaming, message routing, event sourcing, real-time subscriptions

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable, AsyncGenerator
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import uuid
import json
from dataclasses import dataclass, field
import structlog
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import weakref
import hashlib
import pickle
import gzip
import base64
import time

logger = structlog.get_logger(__name__)

class EventType(str, Enum):
    """Event types in the system"""
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_PUBLISHED = "content.published"
    PAYMENT_PROCESSED = "payment.processed"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    COLLABORATION_INVITED = "collaboration.invited"
    NOTIFICATION_SENT = "notification.sent"
    SYSTEM_ERROR = "system.error"
    CUSTOM_EVENT = "custom.event"

class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class DeliveryMode(str, Enum):
    """Event delivery modes"""
    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    ORDERED = "ordered"

class SubscriptionType(str, Enum):
    """Event subscription types"""
    PUSH = "push"
    PULL = "pull"
    STREAM = "stream"

class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"

class Event(BaseModel):
    """Base event class"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    source_service: str = Field(..., description="Service that generated the event")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    ttl_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    tags: List[str] = Field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        """Check if event has expired"""
        if not self.ttl_seconds:
            return False
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl_seconds

class EventFilter(BaseModel):
    """Event filter criteria"""
    event_types: Optional[List[EventType]] = None
    source_services: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    tenant_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    priority: Optional[EventPriority] = None
    since_timestamp: Optional[datetime] = None
    metadata_filters: Dict[str, Any] = Field(default_factory=dict)

class EventSubscription(BaseModel):
    """Event subscription configuration"""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = Field(..., description="Unique subscriber identifier")
    name: str = Field(..., description="Human-readable subscription name")
    event_filter: EventFilter
    subscription_type: SubscriptionType = SubscriptionType.PUSH
    endpoint_url: Optional[str] = None  # For push subscriptions
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    retry_policy: Dict[str, Any] = Field(default_factory=dict)
    dead_letter_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    stats: Dict[str, int] = Field(default_factory=lambda: {
        'events_received': 0,
        'events_delivered': 0,
        'events_failed': 0,
        'events_retried': 0
    })

class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    def __init__(self, handler_id: str, name: str):
        self.handler_id = handler_id
        self.name = name
        self.is_active = True
        self.processing_stats = {
            'events_processed': 0,
            'events_failed': 0,
            'average_processing_time': 0.0
        }
    
    @abstractmethod
    async def handle_event(self, event: Event) -> bool:
        """Handle an event, return True if successful"""
        pass
    
    def matches_event(self, event: Event, event_filter: EventFilter) -> bool:
        """Check if event matches the handler's filter"""
        
        # Event type filter
        if event_filter.event_types and event.event_type not in event_filter.event_types:
            return False
        
        # Source service filter
        if event_filter.source_services and event.source_service not in event_filter.source_services:
            return False
        
        # User ID filter
        if event_filter.user_ids and event.user_id not in event_filter.user_ids:
            return False
        
        # Tenant ID filter
        if event_filter.tenant_ids and event.tenant_id not in event_filter.tenant_ids:
            return False
        
        # Priority filter
        if event_filter.priority and event.priority != event_filter.priority:
            return False
        
        # Tags filter
        if event_filter.tags and not any(tag in event.tags for tag in event_filter.tags):
            return False
        
        # Timestamp filter
        if event_filter.since_timestamp and event.timestamp < event_filter.since_timestamp:
            return False
        
        # Metadata filters
        for key, value in event_filter.metadata_filters.items():
            if event.metadata.get(key) != value:
                return False
        
        return True

class EmailNotificationHandler(EventHandler):
    """Email notification event handler"""
    
    def __init__(self):
        super().__init__("email_notification", "Email Notification Handler")
    
    async def handle_event(self, event: Event) -> bool:
        """Send email notification for relevant events"""
        try:
            # Simulate email sending
            await asyncio.sleep(0.1)
            
            if event.event_type in [EventType.USER_CREATED, EventType.PAYMENT_PROCESSED]:
                logger.info("Email notification sent",
                           event_id=event.event_id,
                           event_type=event.event_type,
                           recipient=event.data.get('email', 'unknown'))
            
            return True
            
        except Exception as e:
            logger.error("Email notification failed",
                        event_id=event.event_id,
                        error=str(e))
            return False

class WebhookHandler(EventHandler):
    """Webhook delivery event handler"""
    
    def __init__(self, webhook_url: str):
        super().__init__(f"webhook_{hashlib.md5(webhook_url.encode()).hexdigest()[:8]}", 
                        f"Webhook Handler ({webhook_url})")
        self.webhook_url = webhook_url
    
    async def handle_event(self, event: Event) -> bool:
        """Deliver event via webhook"""
        try:
            # Simulate webhook delivery
            await asyncio.sleep(0.05)
            
            logger.info("Webhook delivered",
                       event_id=event.event_id,
                       webhook_url=self.webhook_url,
                       event_type=event.event_type)
            
            return True
            
        except Exception as e:
            logger.error("Webhook delivery failed",
                        event_id=event.event_id,
                        webhook_url=self.webhook_url,
                        error=str(e))
            return False

class EventStore:
    """
    Event store for event sourcing and replay
    
    DBA: Event persistence, querying, indexing
    Backend Senior: Performance optimization, data integrity
    """
    
    def __init__(self, max_events: int = 100000):
        self.events: deque = deque(maxlen=max_events)
        self.event_index: Dict[str, Event] = {}
        self.type_index: Dict[EventType, List[str]] = defaultdict(list)
        self.source_index: Dict[str, List[str]] = defaultdict(list)
        self.user_index: Dict[str, List[str]] = defaultdict(list)
        self.timestamp_index: List[Tuple[datetime, str]] = []
    
    async def store_event(self, event: Event) -> bool:
        """Store event with indexing"""
        try:
            # Add to main storage
            self.events.append(event)
            self.event_index[event.event_id] = event
            
            # Update indexes
            self.type_index[event.event_type].append(event.event_id)
            self.source_index[event.source_service].append(event.event_id)
            
            if event.user_id:
                self.user_index[event.user_id].append(event.event_id)
            
            self.timestamp_index.append((event.timestamp, event.event_id))
            
            # Keep timestamp index sorted and trimmed
            self.timestamp_index.sort(key=lambda x: x[0])
            if len(self.timestamp_index) > 50000:  # Keep last 50k entries
                self.timestamp_index = self.timestamp_index[-25000:]
            
            return True
            
        except Exception as e:
            logger.error("Event storage failed",
                        event_id=event.event_id,
                        error=str(e))
            return False
    
    async def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        return self.event_index.get(event_id)
    
    async def query_events(self, event_filter: EventFilter, 
                          limit: int = 100, offset: int = 0) -> List[Event]:
        """Query events with filtering"""
        try:
            candidate_event_ids = set()
            
            # Use indexes to find candidate events
            if event_filter.event_types:
                for event_type in event_filter.event_types:
                    candidate_event_ids.update(self.type_index.get(event_type, []))
            
            if event_filter.source_services:
                service_ids = set()
                for service in event_filter.source_services:
                    service_ids.update(self.source_index.get(service, []))
                
                if candidate_event_ids:
                    candidate_event_ids &= service_ids
                else:
                    candidate_event_ids = service_ids
            
            if event_filter.user_ids:
                user_ids = set()
                for user_id in event_filter.user_ids:
                    user_ids.update(self.user_index.get(user_id, []))
                
                if candidate_event_ids:
                    candidate_event_ids &= user_ids
                else:
                    candidate_event_ids = user_ids
            
            # If no specific filters, use all events
            if not candidate_event_ids and not any([
                event_filter.event_types,
                event_filter.source_services,
                event_filter.user_ids
            ]):
                candidate_event_ids = set(self.event_index.keys())
            
            # Apply remaining filters
            matching_events = []
            
            for event_id in candidate_event_ids:
                event = self.event_index.get(event_id)
                if not event:
                    continue
                
                # Apply additional filters
                if event_filter.since_timestamp and event.timestamp < event_filter.since_timestamp:
                    continue
                
                if event_filter.priority and event.priority != event_filter.priority:
                    continue
                
                if event_filter.tags and not any(tag in event.tags for tag in event_filter.tags):
                    continue
                
                # Metadata filters
                matches_metadata = True
                for key, value in event_filter.metadata_filters.items():
                    if event.metadata.get(key) != value:
                        matches_metadata = False
                        break
                
                if not matches_metadata:
                    continue
                
                matching_events.append(event)
            
            # Sort by timestamp (newest first)
            matching_events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            
            return matching_events[start_idx:end_idx]
            
        except Exception as e:
            logger.error("Event query failed",
                        event_filter=event_filter.dict(),
                        error=str(e))
            return []
    
    async def get_event_stats(self) -> Dict[str, Any]:
        """Get event store statistics"""
        type_counts = {event_type.value: len(event_ids) 
                      for event_type, event_ids in self.type_index.items()}
        
        source_counts = {service: len(event_ids)
                        for service, event_ids in self.source_index.items()}
        
        return {
            'total_events': len(self.events),
            'events_by_type': type_counts,
            'events_by_source': source_counts,
            'unique_users': len(self.user_index),
            'oldest_event': self.events[0].timestamp.isoformat() if self.events else None,
            'newest_event': self.events[-1].timestamp.isoformat() if self.events else None
        }

class EventBusService:
    """
    Enterprise Event Bus Service
    
    Demonstrates expertise in:
    - Microservices: Event-driven architecture, service decoupling
    - DevOps: Real-time processing, monitoring, performance optimization
    - Backend Senior: Async message processing, queue management
    - DBA: Event sourcing, data persistence, querying
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.event_store = EventStore(max_events=self.config.get('max_stored_events', 100000))
        
        # Subscriptions and handlers
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_handlers: Dict[str, EventHandler] = {}
        self.subscription_handlers: Dict[str, List[str]] = defaultdict(list)  # subscription_id -> handler_ids
        
        # Event streams and queues
        self.event_streams: Dict[str, asyncio.Queue] = {}  # subscription_id -> queue
        self.dead_letter_queue: asyncio.Queue = asyncio.Queue()
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
        # Real-time subscribers
        self.stream_subscribers: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
        
        self.metrics = {
            'events_published': 0,
            'events_delivered': 0,
            'events_failed': 0,
            'events_retried': 0,
            'active_subscriptions': 0,
            'active_handlers': 0,
            'average_processing_time': 0.0,
            'throughput_per_second': 0.0
        }
        
        # Initialize default handlers
        self._initialize_default_handlers()
        
        # Start background processors
        self._start_background_processors()
        
        logger.info("Event Bus Service initialized",
                   config=self.config)
    
    def _initialize_default_handlers(self):
        """Initialize default system event handlers"""
        # Email notification handler
        email_handler = EmailNotificationHandler()
        self.event_handlers[email_handler.handler_id] = email_handler
        
        # System webhook handler (if configured)
        if 'system_webhook_url' in self.config:
            webhook_handler = WebhookHandler(self.config['system_webhook_url'])
            self.event_handlers[webhook_handler.handler_id] = webhook_handler
    
    def _start_background_processors(self):
        """Start background event processing tasks"""
        asyncio.create_task(self._event_processor())
        asyncio.create_task(self._dead_letter_processor())
        asyncio.create_task(self._metrics_updater())
    
    async def publish_event(self, event: Event) -> bool:
        """
        Publish event to the event bus
        
        Microservices: Event publishing, service decoupling
        Backend Senior: Async processing, error handling
        """
        try:
            # Validate event
            if event.is_expired:
                logger.warning("Attempted to publish expired event",
                              event_id=event.event_id,
                              event_type=event.event_type)
                return False
            
            # Store event for sourcing
            await self.event_store.store_event(event)
            
            # Add to processing queue
            await self.processing_queue.put(event)
            
            self.metrics['events_published'] += 1
            
            logger.info("Event published",
                       event_id=event.event_id,
                       event_type=event.event_type,
                       source_service=event.source_service)
            
            return True
            
        except Exception as e:
            logger.error("Event publishing failed",
                        event_id=event.event_id,
                        error=str(e))
            return False
    
    async def _event_processor(self):
        """Background event processor"""
        while True:
            try:
                # Get event from processing queue
                event = await self.processing_queue.get()
                
                start_time = asyncio.get_event_loop().time()
                
                # Find matching subscriptions
                matching_subscriptions = await self._find_matching_subscriptions(event)
                
                # Process each matching subscription
                delivery_tasks = []
                
                for subscription in matching_subscriptions:
                    if not subscription.is_active:
                        continue
                    
                    # Create delivery task
                    task = asyncio.create_task(
                        self._deliver_event_to_subscription(event, subscription)
                    )
                    delivery_tasks.append(task)
                    
                    # Update subscription stats
                    subscription.stats['events_received'] += 1
                    subscription.last_activity = datetime.now()
                
                # Wait for all deliveries to complete
                if delivery_tasks:
                    await asyncio.gather(*delivery_tasks, return_exceptions=True)
                
                # Deliver to real-time stream subscribers
                await self._deliver_to_stream_subscribers(event)
                
                # Update metrics
                processing_time = asyncio.get_event_loop().time() - start_time
                self._update_processing_time_metric(processing_time)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error("Event processor error", error=str(e))
                await asyncio.sleep(1)
    
    async def _find_matching_subscriptions(self, event: Event) -> List[EventSubscription]:
        """Find subscriptions that match the event"""
        matching = []
        
        for subscription in self.subscriptions.values():
            if not subscription.is_active:
                continue
            
            # Check if event matches subscription filter
            handler = EventHandler("temp", "temp")  # Temporary handler for matching
            if handler.matches_event(event, subscription.event_filter):
                matching.append(subscription)
        
        return matching
    
    async def _deliver_event_to_subscription(self, event: Event, subscription: EventSubscription):
        """Deliver event to a specific subscription"""
        try:
            if subscription.subscription_type == SubscriptionType.PUSH:
                await self._deliver_push_event(event, subscription)
            elif subscription.subscription_type == SubscriptionType.PULL:
                await self._deliver_pull_event(event, subscription)
            elif subscription.subscription_type == SubscriptionType.STREAM:
                await self._deliver_stream_event(event, subscription)
            
            subscription.stats['events_delivered'] += 1
            self.metrics['events_delivered'] += 1
            
        except Exception as e:
            logger.error("Event delivery failed",
                        event_id=event.event_id,
                        subscription_id=subscription.subscription_id,
                        error=str(e))
            
            subscription.stats['events_failed'] += 1
            self.metrics['events_failed'] += 1
            
            # Handle retry logic
            await self._handle_delivery_failure(event, subscription, str(e))
    
    async def _deliver_push_event(self, event: Event, subscription: EventSubscription):
        """Deliver event via push (webhook)"""
        if not subscription.endpoint_url:
            raise ValueError("Push subscription requires endpoint_url")
        
        # Find or create webhook handler
        webhook_handler = None
        for handler in self.event_handlers.values():
            if (isinstance(handler, WebhookHandler) and 
                handler.webhook_url == subscription.endpoint_url):
                webhook_handler = handler
                break
        
        if not webhook_handler:
            webhook_handler = WebhookHandler(subscription.endpoint_url)
            self.event_handlers[webhook_handler.handler_id] = webhook_handler
        
        # Deliver via webhook
        success = await webhook_handler.handle_event(event)
        if not success:
            raise Exception("Webhook delivery failed")
    
    async def _deliver_pull_event(self, event: Event, subscription: EventSubscription):
        """Deliver event to pull queue"""
        # Get or create queue for subscription
        if subscription.subscription_id not in self.event_streams:
            max_size = subscription.retry_policy.get('max_queue_size', 1000)
            self.event_streams[subscription.subscription_id] = asyncio.Queue(maxsize=max_size)
        
        queue = self.event_streams[subscription.subscription_id]
        
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            # Queue is full, move to dead letter queue
            await self.dead_letter_queue.put((event, subscription, "Queue full"))
            raise Exception("Subscription queue is full")
    
    async def _deliver_stream_event(self, event: Event, subscription: EventSubscription):
        """Deliver event to stream subscribers"""
        subscription_streams = self.stream_subscribers.get(subscription.subscription_id, set())
        
        # Remove closed streams
        closed_streams = set()
        for stream_queue in subscription_streams:
            try:
                stream_queue.put_nowait(event)
            except:
                closed_streams.add(stream_queue)
        
        # Clean up closed streams
        for closed_stream in closed_streams:
            subscription_streams.discard(closed_stream)
    
    async def _deliver_to_stream_subscribers(self, event: Event):
        """Deliver event to all real-time stream subscribers"""
        for subscription_id, streams in self.stream_subscribers.items():
            subscription = self.subscriptions.get(subscription_id)
            if not subscription or not subscription.is_active:
                continue
            
            # Check if event matches subscription
            handler = EventHandler("temp", "temp")
            if handler.matches_event(event, subscription.event_filter):
                closed_streams = set()
                
                for stream_queue in streams:
                    try:
                        stream_queue.put_nowait(event)
                    except:
                        closed_streams.add(stream_queue)
                
                # Clean up closed streams
                for closed_stream in closed_streams:
                    streams.discard(closed_stream)
    
    async def _handle_delivery_failure(self, event: Event, subscription: EventSubscription, error: str):
        """Handle event delivery failure with retry logic"""
        
        # Check if event should be retried
        if event.retry_count < event.max_retries:
            event.retry_count += 1
            
            # Calculate retry delay (exponential backoff)
            base_delay = subscription.retry_policy.get('base_delay_seconds', 1)
            max_delay = subscription.retry_policy.get('max_delay_seconds', 60)
            delay = min(base_delay * (2 ** (event.retry_count - 1)), max_delay)
            
            # Schedule retry
            asyncio.create_task(self._schedule_retry(event, subscription, delay))
            
            subscription.stats['events_retried'] += 1
            self.metrics['events_retried'] += 1
            
            logger.info("Event delivery scheduled for retry",
                       event_id=event.event_id,
                       subscription_id=subscription.subscription_id,
                       retry_count=event.retry_count,
                       delay_seconds=delay)
        else:
            # Move to dead letter queue
            await self.dead_letter_queue.put((event, subscription, error))
            
            logger.warning("Event moved to dead letter queue",
                          event_id=event.event_id,
                          subscription_id=subscription.subscription_id,
                          error=error)
    
    async def _schedule_retry(self, event: Event, subscription: EventSubscription, delay: float):
        """Schedule event retry after delay"""
        await asyncio.sleep(delay)
        await self._deliver_event_to_subscription(event, subscription)
    
    async def _dead_letter_processor(self):
        """Process dead letter queue"""
        while True:
            try:
                # Get failed event from dead letter queue
                event, subscription, error = await self.dead_letter_queue.get()
                
                logger.error("Processing dead letter event",
                           event_id=event.event_id,
                           subscription_id=subscription.subscription_id,
                           error=error)
                
                # Could implement dead letter handling logic here
                # e.g., store in persistent storage, send alerts, etc.
                
                self.dead_letter_queue.task_done()
                
            except Exception as e:
                logger.error("Dead letter processor error", error=str(e))
                await asyncio.sleep(1)
    
    async def _metrics_updater(self):
        """Update throughput metrics"""
        last_events_published = 0
        
        while True:
            await asyncio.sleep(60)  # Update every minute
            
            try:
                current_events = self.metrics['events_published']
                events_per_minute = current_events - last_events_published
                self.metrics['throughput_per_second'] = events_per_minute / 60.0
                last_events_published = current_events
                
                # Update active counts
                self.metrics['active_subscriptions'] = len([
                    s for s in self.subscriptions.values() if s.is_active
                ])
                self.metrics['active_handlers'] = len([
                    h for h in self.event_handlers.values() if h.is_active
                ])
                
            except Exception as e:
                logger.error("Metrics update failed", error=str(e))
    
    def _update_processing_time_metric(self, processing_time: float):
        """Update average processing time metric"""
        current_avg = self.metrics['average_processing_time']
        total_events = self.metrics['events_published']
        
        if total_events <= 1:
            self.metrics['average_processing_time'] = processing_time
        else:
            self.metrics['average_processing_time'] = (
                (current_avg * (total_events - 1) + processing_time) / total_events
            )
    
    async def create_subscription(self, subscription: EventSubscription) -> bool:
        """
        Create a new event subscription
        
        Microservices: Service subscription management
        Backend Senior: Configuration management, validation
        """
        try:
            # Validate subscription
            if subscription.subscription_id in self.subscriptions:
                logger.warning("Subscription already exists",
                              subscription_id=subscription.subscription_id)
                return False
            
            # Validate endpoint for push subscriptions
            if (subscription.subscription_type == SubscriptionType.PUSH and 
                not subscription.endpoint_url):
                raise ValueError("Push subscriptions require endpoint_url")
            
            # Store subscription
            self.subscriptions[subscription.subscription_id] = subscription
            
            # Initialize queue for pull subscriptions
            if subscription.subscription_type == SubscriptionType.PULL:
                max_size = subscription.retry_policy.get('max_queue_size', 1000)
                self.event_streams[subscription.subscription_id] = asyncio.Queue(maxsize=max_size)
            
            # Initialize stream subscriber set for stream subscriptions
            if subscription.subscription_type == SubscriptionType.STREAM:
                self.stream_subscribers[subscription.subscription_id] = set()
            
            logger.info("Event subscription created",
                       subscription_id=subscription.subscription_id,
                       subscriber_id=subscription.subscriber_id,
                       subscription_type=subscription.subscription_type)
            
            return True
            
        except Exception as e:
            logger.error("Subscription creation failed",
                        subscription_id=subscription.subscription_id,
                        error=str(e))
            return False
    
    async def pull_events(self, subscription_id: str, max_events: int = 10, 
                         timeout_seconds: float = 5.0) -> List[Event]:
        """
        Pull events from subscription queue
        
        Microservices: Pull-based event consumption
        DevOps: Performance optimization, timeout handling
        """
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            if subscription.subscription_type != SubscriptionType.PULL:
                raise ValueError("Subscription is not configured for pull mode")
            
            if subscription_id not in self.event_streams:
                return []
            
            queue = self.event_streams[subscription_id]
            events = []
            
            # Pull events with timeout
            for _ in range(max_events):
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=timeout_seconds)
                    events.append(event)
                    queue.task_done()
                    
                    # Reset timeout for subsequent events
                    timeout_seconds = 0.1
                    
                except asyncio.TimeoutError:
                    break
            
            # Update subscription stats
            if events:
                subscription.last_activity = datetime.now()
            
            logger.info("Events pulled from subscription",
                       subscription_id=subscription_id,
                       events_count=len(events))
            
            return events
            
        except Exception as e:
            logger.error("Event pull failed",
                        subscription_id=subscription_id,
                        error=str(e))
            return []
    
    async def subscribe_to_stream(self, subscription_id: str) -> AsyncGenerator[Event, None]:
        """
        Subscribe to real-time event stream
        
        Microservices: Real-time event streaming
        DevOps: Real-time monitoring, live updates
        """
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            if subscription.subscription_type != SubscriptionType.STREAM:
                raise ValueError("Subscription is not configured for stream mode")
            
            # Create stream queue for this client
            stream_queue = asyncio.Queue(maxsize=1000)
            
            # Add to subscription streams
            self.stream_subscribers[subscription_id].add(stream_queue)
            
            try:
                logger.info("Client subscribed to event stream",
                           subscription_id=subscription_id)
                
                # Yield events from stream
                while True:
                    event = await stream_queue.get()
                    yield event
                    stream_queue.task_done()
                    
            finally:
                # Clean up when client disconnects
                self.stream_subscribers[subscription_id].discard(stream_queue)
                
                logger.info("Client unsubscribed from event stream",
                           subscription_id=subscription_id)
                
        except Exception as e:
            logger.error("Event stream subscription failed",
                        subscription_id=subscription_id,
                        error=str(e))
            raise
    
    async def query_events(self, event_filter: EventFilter, 
                          limit: int = 100, offset: int = 0) -> List[Event]:
        """
        Query historical events
        
        DBA: Event querying, indexing, filtering
        Backend Senior: Performance optimization
        """
        return await self.event_store.query_events(event_filter, limit, offset)
    
    async def replay_events(self, event_filter: EventFilter, 
                           target_subscription_id: str) -> int:
        """
        Replay historical events to a subscription
        
        DBA: Event sourcing, replay capabilities
        Microservices: Event replay for service recovery
        """
        try:
            if target_subscription_id not in self.subscriptions:
                raise ValueError(f"Target subscription not found: {target_subscription_id}")
            
            # Query matching events
            events = await self.event_store.query_events(event_filter, limit=10000)
            
            target_subscription = self.subscriptions[target_subscription_id]
            replayed_count = 0
            
            # Replay events
            for event in events:
                try:
                    await self._deliver_event_to_subscription(event, target_subscription)
                    replayed_count += 1
                except Exception as e:
                    logger.warning("Event replay delivery failed",
                                 event_id=event.event_id,
                                 error=str(e))
            
            logger.info("Event replay completed",
                       target_subscription_id=target_subscription_id,
                       replayed_count=replayed_count,
                       total_matching=len(events))
            
            return replayed_count
            
        except Exception as e:
            logger.error("Event replay failed",
                        target_subscription_id=target_subscription_id,
                        error=str(e))
            return 0
    
    async def get_subscription_stats(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a subscription"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return None
        
        stats = subscription.stats.copy()
        
        # Add queue information for pull subscriptions
        if subscription.subscription_type == SubscriptionType.PULL:
            queue = self.event_streams.get(subscription_id)
            if queue:
                stats['queue_size'] = queue.qsize()
                stats['queue_max_size'] = queue.maxsize
        
        # Add stream information for stream subscriptions
        elif subscription.subscription_type == SubscriptionType.STREAM:
            streams = self.stream_subscribers.get(subscription_id, set())
            stats['active_streams'] = len(streams)
        
        return stats
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        event_store_stats = await self.event_store.get_event_stats()
        
        return {
            **self.metrics,
            'total_subscriptions': len(self.subscriptions),
            'total_handlers': len(self.event_handlers),
            'dead_letter_queue_size': self.dead_letter_queue.qsize(),
            'processing_queue_size': self.processing_queue.qsize(),
            'event_store': event_store_stats,
            'service_status': 'healthy'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'event_bus_service',
            'status': 'healthy',
            'version': '1.0.0',
            'subscriptions': len(self.subscriptions),
            'active_handlers': len([h for h in self.event_handlers.values() if h.is_active]),
            'processing_queue_size': self.processing_queue.qsize(),
            'throughput_per_second': self.metrics['throughput_per_second']
        }

# Example usage and testing
async def example_usage():
    """Example usage of the Event Bus Service"""
    
    # Initialize event bus
    event_bus = EventBusService()
    
    # Create a subscription
    subscription = EventSubscription(
        subscriber_id="user_service",
        name="User Service Events",
        event_filter=EventFilter(
            event_types=[EventType.USER_CREATED, EventType.USER_UPDATED],
            source_services=["auth_service", "profile_service"]
        ),
        subscription_type=SubscriptionType.PULL
    )
    
    await event_bus.create_subscription(subscription)
    
    # Publish some events
    events = [
        Event(
            event_type=EventType.USER_CREATED,
            source_service="auth_service",
            data={
                "user_id": "user_123",
                "email": "test@example.com",
                "name": "Test User"
            },
            user_id="user_123"
        ),
        Event(
            event_type=EventType.CONTENT_UPLOADED,
            source_service="content_service",
            data={
                "content_id": "content_456",
                "user_id": "user_123",
                "file_type": "video"
            },
            user_id="user_123"
        ),
        Event(
            event_type=EventType.USER_UPDATED,
            source_service="profile_service",
            data={
                "user_id": "user_123",
                "updated_fields": ["profile_picture", "bio"]
            },
            user_id="user_123"
        )
    ]
    
    # Publish events
    for event in events:
        await event_bus.publish_event(event)
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Pull events from subscription
    pulled_events = await event_bus.pull_events(subscription.subscription_id, max_events=5)
    print(f"Pulled {len(pulled_events)} events from subscription")
    
    for event in pulled_events:
        print(f"- {event.event_type}: {event.data}")
    
    # Query historical events
    event_filter = EventFilter(
        event_types=[EventType.USER_CREATED, EventType.USER_UPDATED],
        user_ids=["user_123"]
    )
    
    historical_events = await event_bus.query_events(event_filter)
    print(f"Found {len(historical_events)} historical events")
    
    # Get service metrics
    metrics = await event_bus.get_service_metrics()
    print(f"Service metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(example_usage())