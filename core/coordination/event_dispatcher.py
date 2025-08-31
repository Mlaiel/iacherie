"""
Event Dispatcher - Enterprise Event Processing & Distribution System

Advanced event dispatching system providing real-time event processing,
routing, and coordination for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL WARNING:
This event dispatching system is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization.

 BUSINESS LOGIC:
Event Generation → Routing → Filtering → Processing → Distribution → Acknowledgment
"""

import asyncio
import uuid
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import weakref
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events in the system"""
    WORKFLOW_EVENT = "workflow_event"
    PROCESS_EVENT = "process_event"
    TASK_EVENT = "task_event"
    RESOURCE_EVENT = "resource_event"
    STATE_EVENT = "state_event"
    CONTENT_EVENT = "content_event"
    PROTECTION_EVENT = "protection_event"
    MONETIZATION_EVENT = "monetization_event"
    USER_EVENT = "user_event"
    SYSTEM_EVENT = "system_event"
    ALERT_EVENT = "alert_event"
    NOTIFICATION_EVENT = "notification_event"


class EventPriority(Enum):
    """Event processing priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class EventStatus(Enum):
    """Event processing status"""
    CREATED = "created"
    QUEUED = "queued"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DeliveryMode(Enum):
    """Event delivery modes"""
    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    RELIABLE = "reliable"


@dataclass
class EventFilter:
    """Event filtering criteria"""
    event_types: List[EventType] = field(default_factory=list)
    source_patterns: List[str] = field(default_factory=list)
    tag_filters: Dict[str, Any] = field(default_factory=dict)
    payload_filters: Dict[str, Any] = field(default_factory=dict)
    priority_min: Optional[EventPriority] = None
    priority_max: Optional[EventPriority] = None


@dataclass
class EventSubscription:
    """Event subscription configuration"""
    subscription_id: str
    subscriber_id: str
    filters: EventFilter
    callback: Callable
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    max_retries: int = 3
    retry_delay_seconds: int = 5
    timeout_seconds: int = 30
    batch_size: int = 1
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    """Core event structure"""
    event_id: str
    event_type: EventType
    source: str
    timestamp: datetime
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    tags: Dict[str, str] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    delivery_attempts: int = 0
    status: EventStatus = EventStatus.CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventDelivery:
    """Event delivery tracking"""
    delivery_id: str
    event_id: str
    subscription_id: str
    attempted_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None


class EventDispatcher:
    """Enterprise event processing and distribution system"""
    
    def __init__(self, max_workers: int = 20, queue_size: int = 10000):
        self.max_workers = max_workers
        self.queue_size = queue_size
        
        # Event queues and processing
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self.priority_queues: Dict[EventPriority, deque] = {
            priority: deque() for priority in EventPriority
        }
        self.processing_active = False
        self.processing_tasks: List[asyncio.Task] = []
        
        # Subscriptions and routing
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_routing: Dict[EventType, List[str]] = defaultdict(list)
        self.subscriber_routing: Dict[str, List[str]] = defaultdict(list)
        
        # Event storage and tracking
        self.event_store: Dict[str, Event] = {}
        self.delivery_tracking: Dict[str, EventDelivery] = {}
        self.event_history: deque = deque(maxlen=1000)
        
        # Processing and performance
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.processing_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Filtering and routing optimization
        self.compiled_filters: Dict[str, Any] = {}
        self.routing_cache: Dict[str, List[str]] = {}
        
        # Dead letter queue
        self.dead_letter_queue: deque = deque(maxlen=1000)
        self.failed_deliveries: Dict[str, List[EventDelivery]] = defaultdict(list)
        
        # Initialize standard event types
        self._initialize_standard_subscriptions()
        
        # Start processing
        self.start_processing()
        
        logger.info("EventDispatcher initialized successfully")
    
    def _initialize_standard_subscriptions(self):
        """Initialize standard system event subscriptions"""
        # System monitoring subscription
        monitoring_subscription = EventSubscription(
            subscription_id="system_monitoring",
            subscriber_id="system_monitor",
            filters=EventFilter(
                event_types=[EventType.SYSTEM_EVENT, EventType.ALERT_EVENT],
                priority_min=EventPriority.HIGH
            ),
            callback=self._handle_system_monitoring,
            delivery_mode=DeliveryMode.RELIABLE,
            max_retries=5
        )
        
        # Workflow coordination subscription
        workflow_subscription = EventSubscription(
            subscription_id="workflow_coordination",
            subscriber_id="workflow_coordinator",
            filters=EventFilter(
                event_types=[EventType.WORKFLOW_EVENT, EventType.TASK_EVENT],
                source_patterns=["workflow_*", "task_*"]
            ),
            callback=self._handle_workflow_coordination,
            delivery_mode=DeliveryMode.AT_LEAST_ONCE,
            batch_size=10
        )
        
        # Content protection subscription
        protection_subscription = EventSubscription(
            subscription_id="content_protection",
            subscriber_id="protection_monitor",
            filters=EventFilter(
                event_types=[EventType.CONTENT_EVENT, EventType.PROTECTION_EVENT],
                tag_filters={"protection_required": "true"}
            ),
            callback=self._handle_content_protection,
            delivery_mode=DeliveryMode.EXACTLY_ONCE,
            max_retries=3
        )
        
        # User notification subscription
        notification_subscription = EventSubscription(
            subscription_id="user_notifications",
            subscriber_id="notification_service",
            filters=EventFilter(
                event_types=[EventType.NOTIFICATION_EVENT, EventType.ALERT_EVENT],
                priority_min=EventPriority.NORMAL
            ),
            callback=self._handle_user_notifications,
            delivery_mode=DeliveryMode.FIRE_AND_FORGET
        )
        
        # Register standard subscriptions
        self.subscribe(monitoring_subscription)
        self.subscribe(workflow_subscription)
        self.subscribe(protection_subscription)
        self.subscribe(notification_subscription)
    
    def subscribe(self, subscription: EventSubscription) -> bool:
        """Register a new event subscription"""



        try:
            # Validate subscription
            if not self._validate_subscription(subscription):
                return False
            
            # Store subscription
            self.subscriptions[subscription.subscription_id] = subscription
            
            # Update routing tables
            self._update_routing_tables(subscription)
            
            # Compile filters for performance
            self._compile_filters(subscription)
            
            logger.info(f"Event subscription registered: {subscription.subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Event subscription failed: {e}")
            return False
    
    def _validate_subscription(self, subscription: EventSubscription) -> bool:
        """Validate event subscription configuration"""



        try:
            # Required fields
            if not all([subscription.subscription_id, subscription.subscriber_id, subscription.callback]):
                logger.error("Missing required subscription fields")
                return False
            
            # Callback validation
            if not callable(subscription.callback):
                logger.error("Subscription callback is not callable")
                return False
            
            # Timeout validation
            if subscription.timeout_seconds <= 0:
                logger.error("Invalid timeout value")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Subscription validation error: {e}")
            return False
    
    def _update_routing_tables(self, subscription: EventSubscription):
        """Update event routing tables"""
        # Update event type routing
        for event_type in subscription.filters.event_types:
            if subscription.subscription_id not in self.event_routing[event_type]:
                self.event_routing[event_type].append(subscription.subscription_id)
        
        # Update subscriber routing
        if subscription.subscription_id not in self.subscriber_routing[subscription.subscriber_id]:
            self.subscriber_routing[subscription.subscriber_id].append(subscription.subscription_id)
    
    def _compile_filters(self, subscription: EventSubscription):
        """Compile event filters for performance optimization"""
        # This would compile complex filters into optimized forms
        # For now, store the filters as-is
        self.compiled_filters[subscription.subscription_id] = subscription.filters
    
    async def publish(
        self,
        event_type: EventType,
        source: str,
        payload: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        tags: Dict[str, str] = None,
        correlation_id: str = None,
        trace_id: str = None,
        expires_in_seconds: int = None
    ) -> str:
        """Publish an event to the system"""



        try:
            event_id = str(uuid.uuid4())
            
            # Calculate expiration
            expires_at = None
            if expires_in_seconds:
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
            
            # Create event
            event = Event(
                event_id=event_id,
                event_type=event_type,
                source=source,
                timestamp=datetime.now(timezone.utc),
                payload=payload,
                priority=priority,
                tags=tags or {},
                correlation_id=correlation_id,
                trace_id=trace_id,
                expires_at=expires_at
            )
            
            # Store event
            self.event_store[event_id] = event
            
            # Queue for processing
            await self._queue_event(event)
            
            # Add to history
            self.event_history.append({
                "event_id": event_id,
                "event_type": event_type.value,
                "source": source,
                "timestamp": event.timestamp.isoformat(),
                "priority": priority.value
            })
            
            logger.debug(f"Event published: {event_id} from {source}")
            return event_id
            
        except Exception as e:
            logger.error(f"Event publication failed: {e}")
            raise
    
    async def _queue_event(self, event: Event):
        """Queue event for processing"""



        try:
            # Check if event has expired
            if event.expires_at and event.expires_at <= datetime.now(timezone.utc):
                event.status = EventStatus.EXPIRED
                logger.warning(f"Event expired before processing: {event.event_id}")
                return
            
            # Queue by priority
            if event.priority == EventPriority.CRITICAL:
                # Critical events bypass queue limits
                await self.event_queue.put(event)
            else:
                # Add to priority queue
                self.priority_queues[event.priority].append(event)
            
            event.status = EventStatus.QUEUED
            
        except Exception as e:
            logger.error(f"Event queuing failed: {e}")
            event.status = EventStatus.FAILED
    
    def start_processing(self):
        """Start event processing"""
        if not self.processing_active:
            self.processing_active = True
            
            # Start worker tasks
            for i in range(self.max_workers):
                task = asyncio.create_task(self._processing_worker(f"worker-{i}"))
                self.processing_tasks.append(task)
            
            # Start priority queue processor
            priority_task = asyncio.create_task(self._priority_queue_processor())
            self.processing_tasks.append(priority_task)
            
            logger.info(f"Event processing started with {self.max_workers} workers")
    
    def stop_processing(self):
        """Stop event processing"""
        self.processing_active = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        self.processing_tasks = []
        logger.info("Event processing stopped")
    
    async def _processing_worker(self, worker_id: str):
        """Event processing worker"""
        while self.processing_active:
            try:
                # Get event from queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Process event
                await self._process_event(event, worker_id)
                
                # Mark task done
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    async def _priority_queue_processor(self):
        """Process priority queues in order"""
        while self.processing_active:
            try:
                # Process queues by priority
                for priority in EventPriority:
                    queue = self.priority_queues[priority]
                    
                    # Process up to 10 events per priority level
                    processed = 0
                    while queue and processed < 10:
                        event = queue.popleft()
                        
                        # Add to main processing queue
                        try:
                            await asyncio.wait_for(self.event_queue.put(event), timeout=0.1)
                            processed += 1
                        except asyncio.TimeoutError:
                            # Queue full, put event back
                            queue.appendleft(event)
                            break
                
                await asyncio.sleep(0.1)  # Brief pause
                
            except Exception as e:
                logger.error(f"Priority queue processor error: {e}")
    
    async def _process_event(self, event: Event, worker_id: str):
        """Process a single event"""



        try:
            start_time = datetime.now(timezone.utc)
            event.status = EventStatus.PROCESSING
            
            # Find matching subscriptions
            matching_subscriptions = self._find_matching_subscriptions(event)
            
            if not matching_subscriptions:
                logger.debug(f"No matching subscriptions for event: {event.event_id}")
                event.status = EventStatus.PROCESSED
                return
            
            # Deliver to matching subscriptions
            delivery_tasks = []
            for subscription_id in matching_subscriptions:
                subscription = self.subscriptions[subscription_id]
                if subscription.enabled:
                    task = self._deliver_event(event, subscription)
                    delivery_tasks.append(task)
            
            # Wait for all deliveries
            if delivery_tasks:
                await asyncio.gather(*delivery_tasks, return_exceptions=True)
            
            # Update status
            event.status = EventStatus.PROCESSED
            
            # Track performance
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.processing_metrics[event.event_type.value].append(processing_time)
            
            logger.debug(f"Event processed: {event.event_id} by {worker_id} in {processing_time:.3f}s")
            
        except Exception as e:
            event.status = EventStatus.FAILED
            logger.error(f"Event processing failed: {event.event_id} - {e}")
    
    def _find_matching_subscriptions(self, event: Event) -> List[str]:
        """Find subscriptions that match the event"""



        try:
            matching = []
            
            # Check cached routes first
            cache_key = f"{event.event_type.value}:{event.source}"
            if cache_key in self.routing_cache:
                return self.routing_cache[cache_key]
            
            # Find matching subscriptions
            for subscription_id, subscription in self.subscriptions.items():
                if self._event_matches_filter(event, subscription.filters):
                    matching.append(subscription_id)
            
            # Cache result
            self.routing_cache[cache_key] = matching
            
            # Limit cache size
            if len(self.routing_cache) > 1000:
                # Remove oldest entries
                oldest_keys = list(self.routing_cache.keys())[:100]
                for key in oldest_keys:
                    del self.routing_cache[key]
            
            return matching
            
        except Exception as e:
            logger.error(f"Subscription matching failed: {e}")
            return []
    
    def _event_matches_filter(self, event: Event, filters: EventFilter) -> bool:
        """Check if event matches subscription filters"""



        try:
            # Event type filter
            if filters.event_types and event.event_type not in filters.event_types:
                return False
            
            # Source pattern filter
            if filters.source_patterns:
                source_match = False
                for pattern in filters.source_patterns:
                    if self._matches_pattern(event.source, pattern):
                        source_match = True
                        break
                if not source_match:
                    return False
            
            # Tag filters
            for tag_key, tag_value in filters.tag_filters.items():
                if tag_key not in event.tags or event.tags[tag_key] != tag_value:
                    return False
            
            # Payload filters
            for payload_key, payload_value in filters.payload_filters.items():
                if (payload_key not in event.payload or 
                    event.payload[payload_key] != payload_value):
                    return False
            
            # Priority filters
            if filters.priority_min and event.priority.value > filters.priority_min.value:
                return False
            
            if filters.priority_max and event.priority.value < filters.priority_max.value:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Event filter matching failed: {e}")
            return False
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Simple pattern matching with wildcards"""
        if '*' not in pattern:
            return text == pattern
        
        # Simple wildcard matching
        if pattern.endswith('*'):
            return text.startswith(pattern[:-1])
        elif pattern.startswith('*'):
            return text.endswith(pattern[1:])
        else:
            # More complex patterns would need regex
            return text == pattern
    
    async def _deliver_event(self, event: Event, subscription: EventSubscription):
        """Deliver event to a subscription"""



        try:
            delivery_id = str(uuid.uuid4())
            
            # Create delivery tracking
            delivery = EventDelivery(
                delivery_id=delivery_id,
                event_id=event.event_id,
                subscription_id=subscription.subscription_id,
                attempted_at=datetime.now(timezone.utc)
            )
            
            self.delivery_tracking[delivery_id] = delivery
            
            # Attempt delivery
            success = await self._attempt_delivery(event, subscription, delivery)
            
            if success:
                delivery.success = True
                delivery.completed_at = datetime.now(timezone.utc)
            else:
                # Handle retry logic
                await self._handle_delivery_failure(event, subscription, delivery)
            
        except Exception as e:
            logger.error(f"Event delivery failed: {e}")
    
    async def _attempt_delivery(
        self,
        event: Event,
        subscription: EventSubscription,
        delivery: EventDelivery
    ) -> bool:
        """Attempt to deliver event to subscription"""



        try:
            # Prepare callback data
            callback_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "source": event.source,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
                "tags": event.tags,
                "correlation_id": event.correlation_id,
                "trace_id": event.trace_id
            }
            
            # Execute callback with timeout
            if asyncio.iscoroutinefunction(subscription.callback):
                await asyncio.wait_for(
                    subscription.callback(callback_data),
                    timeout=subscription.timeout_seconds
                )
            else:
                # Run sync callback in thread pool
                loop = asyncio.get_event_loop()
                await asyncio.wait_for(
                    loop.run_in_executor(
                        self.thread_executor,
                        subscription.callback,
                        callback_data
                    ),
                    timeout=subscription.timeout_seconds
                )
            
            event.delivery_attempts += 1
            delivery.attempted_at = datetime.now(timezone.utc)
            
            return True
            
        except asyncio.TimeoutError:
            delivery.error_message = f"Delivery timeout after {subscription.timeout_seconds}s"
            logger.warning(f"Delivery timeout: {delivery.delivery_id}")
            return False
        except Exception as e:
            delivery.error_message = str(e)
            logger.error(f"Delivery callback failed: {e}")
            return False
    
    async def _handle_delivery_failure(
        self,
        event: Event,
        subscription: EventSubscription,
        delivery: EventDelivery
    ):
        """Handle failed event delivery"""



        try:
            delivery.retry_count += 1
            
            # Check if retries are exhausted
            if delivery.retry_count >= subscription.max_retries:
                # Move to dead letter queue
                self.dead_letter_queue.append({
                    "event": event,
                    "subscription": subscription,
                    "delivery": delivery,
                    "failed_at": datetime.now(timezone.utc).isoformat()
                })
                
                self.failed_deliveries[subscription.subscription_id].append(delivery)
                
                logger.error(f"Event delivery failed permanently: {delivery.delivery_id}")
                return
            
            # Schedule retry
            retry_delay = subscription.retry_delay_seconds * (delivery.retry_count ** 2)  # Exponential backoff
            delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
            
            # Schedule retry task
            asyncio.create_task(self._schedule_retry(event, subscription, delivery, retry_delay))
            
        except Exception as e:
            logger.error(f"Delivery failure handling failed: {e}")
    
    async def _schedule_retry(
        self,
        event: Event,
        subscription: EventSubscription,
        delivery: EventDelivery,
        delay_seconds: float
    ):
        """Schedule event delivery retry"""



        try:
            await asyncio.sleep(delay_seconds)
            
            # Attempt delivery again
            success = await self._attempt_delivery(event, subscription, delivery)
            
            if not success:
                await self._handle_delivery_failure(event, subscription, delivery)
            else:
                delivery.success = True
                delivery.completed_at = datetime.now(timezone.utc)
                
        except Exception as e:
            logger.error(f"Retry scheduling failed: {e}")
    
    # Standard event handlers
    async def _handle_system_monitoring(self, event_data: Dict[str, Any]):
        """Handle system monitoring events"""
        logger.info(f"System monitoring event: {event_data.get('event_type')}")
    
    async def _handle_workflow_coordination(self, event_data: Dict[str, Any]):
        """Handle workflow coordination events"""
        logger.info(f"Workflow coordination event: {event_data.get('event_type')}")
    
    async def _handle_content_protection(self, event_data: Dict[str, Any]):
        """Handle content protection events"""
        logger.info(f"Content protection event: {event_data.get('event_type')}")
    
    async def _handle_user_notifications(self, event_data: Dict[str, Any]):
        """Handle user notification events"""
        logger.info(f"User notification event: {event_data.get('event_type')}")
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Remove event subscription"""



        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            
            # Remove from routing tables
            for event_type in subscription.filters.event_types:
                if subscription_id in self.event_routing[event_type]:
                    self.event_routing[event_type].remove(subscription_id)
            
            if subscription_id in self.subscriber_routing[subscription.subscriber_id]:
                self.subscriber_routing[subscription.subscriber_id].remove(subscription_id)
            
            # Remove subscription
            del self.subscriptions[subscription_id]
            
            # Clear compiled filters
            if subscription_id in self.compiled_filters:
                del self.compiled_filters[subscription_id]
            
            # Clear routing cache
            self.routing_cache.clear()
            
            logger.info(f"Event subscription removed: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Event unsubscription failed: {e}")
            return False
    
    def get_event_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event processing status"""
        event = self.event_store.get(event_id)
        if not event:
            return None
        
        return {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "source": event.source,
            "status": event.status.value,
            "priority": event.priority.value,
            "timestamp": event.timestamp.isoformat(),
            "delivery_attempts": event.delivery_attempts,
            "retry_count": event.retry_count
        }
    
    def get_subscription_status(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription status"""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return None
        
        # Count deliveries
        successful_deliveries = len([
            d for d in self.delivery_tracking.values()
            if d.subscription_id == subscription_id and d.success
        ])
        
        failed_deliveries = len(self.failed_deliveries.get(subscription_id, []))
        
        return {
            "subscription_id": subscription.subscription_id,
            "subscriber_id": subscription.subscriber_id,
            "enabled": subscription.enabled,
            "delivery_mode": subscription.delivery_mode.value,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "event_types": [et.value for et in subscription.filters.event_types]
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get event system metrics"""
        active_subscriptions = len([s for s in self.subscriptions.values() if s.enabled])
        total_events = len(self.event_store)
        queued_events = sum(len(queue) for queue in self.priority_queues.values())
        
        # Calculate processing statistics
        processing_stats = {}
        for event_type, times in self.processing_metrics.items():
            if times:
                processing_stats[event_type] = {
                    "count": len(times),
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times)
                }
        
        return {
            "active_subscriptions": active_subscriptions,
            "total_subscriptions": len(self.subscriptions),
            "total_events": total_events,
            "queued_events": queued_events,
            "dead_letter_events": len(self.dead_letter_queue),
            "processing_workers": len(self.processing_tasks),
            "processing_active": self.processing_active,
            "processing_statistics": processing_stats,
            "routing_cache_size": len(self.routing_cache)
        }
    
    async def replay_dead_letter_events(self, max_events: int = 100) -> int:
        """Replay events from dead letter queue"""



        try:
            replayed = 0
            
            while self.dead_letter_queue and replayed < max_events:
                dead_event_data = self.dead_letter_queue.popleft()
                event = dead_event_data["event"]
                
                # Reset event status and retry counts
                event.status = EventStatus.CREATED
                event.retry_count = 0
                event.delivery_attempts = 0
                
                # Re-queue for processing
                await self._queue_event(event)
                replayed += 1
            
            logger.info(f"Replayed {replayed} events from dead letter queue")
            return replayed
            
        except Exception as e:
            logger.error(f"Dead letter replay failed: {e}")
            return 0
    
    def cleanup_expired_events(self) -> int:
        """Cleanup expired events from storage"""



        try:
            current_time = datetime.now(timezone.utc)
            expired_events = []
            
            for event_id, event in self.event_store.items():
                if event.expires_at and event.expires_at <= current_time:
                    expired_events.append(event_id)
            
            # Remove expired events
            for event_id in expired_events:
                del self.event_store[event_id]
            
            # Cleanup old delivery tracking
            old_deliveries = []
            for delivery_id, delivery in self.delivery_tracking.items():
                age = (current_time - delivery.attempted_at).days
                if age > 7:  # Keep for 7 days
                    old_deliveries.append(delivery_id)
            
            for delivery_id in old_deliveries:
                del self.delivery_tracking[delivery_id]
            
            logger.info(f"Cleaned up {len(expired_events)} expired events and {len(old_deliveries)} old deliveries")
            return len(expired_events)
            
        except Exception as e:
            logger.error(f"Event cleanup failed: {e}")
            return 0
    
    def shutdown(self):
        """Shutdown event dispatcher and cleanup"""



        try:
            self.stop_processing()
            
            # Shutdown thread executor
            self.thread_executor.shutdown(wait=True)
            
            logger.info("EventDispatcher shutdown completed")
            
        except Exception as e:
            logger.error(f"EventDispatcher shutdown failed: {e}")
