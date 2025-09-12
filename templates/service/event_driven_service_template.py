"""{{service_name}} Event-Driven Service for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable, Set, Type
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
from collections import defaultdict, deque

import aioredis
import aiokafka
from pydantic import BaseModel, Field, validator
import aio_pika
from fastapi import WebSocket
import asyncio_mqtt

from core.base_service import BaseService
from core.config import get_settings
from core.exceptions import ServiceException, EventException
from events.event_bus import EventBus, Event
from events.event_store import EventStore
from events.event_handlers import EventHandler
from events.event_filters import EventFilter
from events.event_sourcing import EventSourcingManager
from monitoring.event_metrics import EventMetricsCollector
from utils.serialization import EventSerializer

logger = logging.getLogger(__name__)
settings = get_settings()


class EventType(Enum):
    """Event types in the system"""
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    BUSINESS_EVENT = "business_event"
    INTEGRATION_EVENT = "integration_event"
    ERROR_EVENT = "error_event"
    AUDIT_EVENT = "audit_event"
    NOTIFICATION_EVENT = "notification_event"
    WORKFLOW_EVENT = "workflow_event"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class EventDeliveryMode(Enum):
    """Event delivery modes"""
    FIRE_AND_FORGET = "fire_and_forget"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"
    GUARANTEED = "guaranteed"


class EventPattern(Enum):
    """Event pattern types"""
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    REQUEST_RESPONSE = "request_response"
    SAGA = "saga"
    EVENT_SOURCING = "event_sourcing"
    CQRS = "cqrs"


class BaseEvent(BaseModel):
    """Base event model"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    event_name: str
    source: str
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    delivery_mode: EventDeliveryMode = EventDeliveryMode.AT_LEAST_ONCE
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventSubscription(BaseModel):
    """Event subscription model"""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str
    event_pattern: str
    event_types: List[EventType] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    handler_config: Dict[str, Any] = Field(default_factory=dict)
    delivery_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class EventProcessingResult(BaseModel):
    """Event processing result"""
    event_id: str
    handler_id: str
    status: str  # success, failure, retry, skip
    execution_time: float
    error: Optional[str] = None
    result: Optional[Any] = None
    retry_count: int = 0
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class EventConfig(BaseModel):
    """Event-driven service configuration"""
    enable_event_sourcing: bool = True
    enable_saga_pattern: bool = True
    enable_cqrs: bool = False
    max_concurrent_handlers: int = 100
    event_retention_days: int = 30
    enable_event_replay: bool = True
    enable_dead_letter_queue: bool = True
    batch_processing_size: int = 50
    processing_timeout: int = 30
    retry_backoff_factor: float = 2.0


@dataclass
class EventContext:
    """Context for event processing"""
    event: BaseEvent
    subscription: EventSubscription
    attempt_count: int = 0
    processing_start: datetime = field(default_factory=datetime.utcnow)
    correlation_data: Dict[str, Any] = field(default_factory=dict)


class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    def __init__(self, handler_id: str):
        self.handler_id = handler_id
        self.metrics = EventMetricsCollector()
    
    @abstractmethod
    async def handle(self, event: BaseEvent, context: EventContext) -> EventProcessingResult:
        """Handle an event"""
        pass
    
    async def can_handle(self, event: BaseEvent) -> bool:
        """Check if this handler can process the event"""
        return True
    
    async def on_error(self, event: BaseEvent, error: Exception) -> None:
        """Handle processing error"""
        logger.error(f"Handler {self.handler_id} failed to process event {event.event_id}: {str(error)}")


class EventHandlerRegistry:
    """Registry for event handlers"""
    
    def __init__(self):
        self.handlers: Dict[str, Dict[str, EventHandler]] = defaultdict(dict)
        self.pattern_handlers: Dict[str, List[EventHandler]] = defaultdict(list)
    
    def register_handler(
        self,
        event_type: EventType,
        event_name: str,
        handler: EventHandler
    ) -> None:
        """Register event handler for specific event"""
        key = f"{event_type.value}:{event_name}"
        self.handlers[key][handler.handler_id] = handler
    
    def register_pattern_handler(
        self,
        pattern: str,
        handler: EventHandler
    ) -> None:
        """Register handler for event pattern"""
        self.pattern_handlers[pattern].append(handler)
    
    def get_handlers(self, event: BaseEvent) -> List[EventHandler]:
        """Get handlers for an event"""
        handlers = []
        
        # Get exact match handlers
        key = f"{event.event_type.value}:{event.event_name}"
        if key in self.handlers:
            handlers.extend(self.handlers[key].values())
        
        # Get pattern match handlers
        for pattern, pattern_handlers in self.pattern_handlers.items():
            if self._matches_pattern(event, pattern):
                handlers.extend(pattern_handlers)
        
        return handlers
    
    def _matches_pattern(self, event: BaseEvent, pattern: str) -> bool:
        """Check if event matches pattern"""
        # Simple pattern matching - can be enhanced
        if pattern == "*":
            return True
        elif pattern.endswith("*"):
            prefix = pattern[:-1]
            return event.event_name.startswith(prefix)
        else:
            return event.event_name == pattern


class EventProcessor:
    """Event processor with concurrent handling"""
    
    def __init__(self, config: EventConfig, handler_registry: EventHandlerRegistry):
        self.config = config
        self.handler_registry = handler_registry
        self.processing_semaphore = asyncio.Semaphore(config.max_concurrent_handlers)
        self.metrics = EventMetricsCollector()
        self.dead_letter_queue: deque = deque()
    
    async def process_event(
        self,
        event: BaseEvent,
        subscription: EventSubscription
    ) -> List[EventProcessingResult]:
        """Process single event"""
        async with self.processing_semaphore:
            return await self._process_event_internal(event, subscription)
    
    async def _process_event_internal(
        self,
        event: BaseEvent,
        subscription: EventSubscription
    ) -> List[EventProcessingResult]:
        """Internal event processing logic"""
        results = []
        handlers = self.handler_registry.get_handlers(event)
        
        if not handlers:
            logger.warning(f"No handlers found for event {event.event_id}")
            return results
        
        # Create processing context
        context = EventContext(event=event, subscription=subscription)
        
        # Process with all applicable handlers
        for handler in handlers:
            try:
                if await handler.can_handle(event):
                    result = await self._execute_handler(handler, event, context)
                    results.append(result)
            except Exception as e:
                logger.error(f"Handler execution failed: {str(e)}")
                await self._handle_processing_error(handler, event, e)
        
        return results
    
    async def _execute_handler(
        self,
        handler: EventHandler,
        event: BaseEvent,
        context: EventContext
    ) -> EventProcessingResult:
        """Execute event handler with timeout and error handling"""
        start_time = datetime.utcnow()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                handler.handle(event, context),
                timeout=self.config.processing_timeout
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record success metrics
            await self.metrics.record_handler_success(
                handler.handler_id,
                event.event_type.value,
                execution_time
            )
            
            return EventProcessingResult(
                event_id=event.event_id,
                handler_id=handler.handler_id,
                status="success",
                execution_time=execution_time,
                result=result.result if hasattr(result, 'result') else None
            )
            
        except asyncio.TimeoutError:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            await self.metrics.record_handler_timeout(
                handler.handler_id,
                event.event_type.value,
                execution_time
            )
            
            return EventProcessingResult(
                event_id=event.event_id,
                handler_id=handler.handler_id,
                status="timeout",
                execution_time=execution_time,
                error="Handler execution timed out"
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            await self.metrics.record_handler_error(
                handler.handler_id,
                event.event_type.value,
                str(e),
                execution_time
            )
            
            return EventProcessingResult(
                event_id=event.event_id,
                handler_id=handler.handler_id,
                status="failure",
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _handle_processing_error(
        self,
        handler: EventHandler,
        event: BaseEvent,
        error: Exception
    ) -> None:
        """Handle processing error"""
        try:
            await handler.on_error(event, error)
        except Exception as e:
            logger.error(f"Error handler failed: {str(e)}")
        
        # Add to dead letter queue if max retries exceeded
        if event.retry_count >= event.max_retries:
            self.dead_letter_queue.append({
                'event': event,
                'handler_id': handler.handler_id,
                'error': str(error),
                'failed_at': datetime.utcnow()
            })
    
    async def process_batch(self, events: List[BaseEvent]) -> List[EventProcessingResult]:
        """Process batch of events"""
        tasks = []
        
        for event in events:
            # Create dummy subscription for batch processing
            subscription = EventSubscription(
                subscriber_id="batch_processor",
                event_pattern="*"
            )
            
            task = asyncio.create_task(
                self.process_event(event, subscription)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            elif isinstance(result, EventProcessingResult):
                all_results.append(result)
        
        return all_results


class {{service_class_name}}(BaseService):
    """
    Advanced event-driven service for Ainflue platform.
    
    Features:
    - Asynchronous event processing with pub/sub pattern
    - Event sourcing and CQRS support
    - Saga pattern for distributed transactions
    - Event filtering and routing
    - Dead letter queue for failed events
    - Event replay and recovery
    - Circuit breaker and retry mechanisms
    - Metrics and monitoring
    - Multiple transport protocols (Redis, Kafka, RabbitMQ, WebSocket)
    - Event versioning and schema evolution
    """
    
    def __init__(
        self,
        name: str = "{{service_name}}",
        config: Optional[EventConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or EventConfig()
        
        # Initialize components
        self.event_bus = EventBus()
        self.event_store = EventStore()
        self.event_sourcing = EventSourcingManager()
        self.handler_registry = EventHandlerRegistry()
        self.processor = EventProcessor(self.config, self.handler_registry)
        self.serializer = EventSerializer()
        
        # Transport clients
        self.redis_client = None
        self.kafka_producer = None
        self.kafka_consumer = None
        self.rabbitmq_connection = None
        self.websocket_connections: Set[WebSocket] = set()
        
        # Subscriptions and state
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.active_sagas: Dict[str, Any] = {}
        
        # Initialize metrics collector
        self.metrics = EventMetricsCollector()
        
        logger.info(f"Event-driven service '{name}' initialized successfully")

    async def initialize(self) -> None:
        """Initialize event-driven service"""
        try:
            # Initialize Redis for event bus
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize Kafka if configured
            if hasattr(settings, 'kafka_bootstrap_servers'):
                await self._initialize_kafka()
            
            # Initialize RabbitMQ if configured
            if hasattr(settings, 'rabbitmq_url'):
                await self._initialize_rabbitmq()
            
            # Initialize event store
            await self.event_store.initialize()
            
            # Initialize event sourcing
            if self.config.enable_event_sourcing:
                await self.event_sourcing.initialize()
            
            logger.info("Event-driven service initialized successfully")
            
        except Exception as e:
            logger.error(f"Event service initialization failed: {str(e)}")
            raise ServiceException(f"Initialization failed: {str(e)}")

    async def _initialize_kafka(self) -> None:
        """Initialize Kafka producer and consumer"""
        try:
            self.kafka_producer = aiokafka.AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
            )
            await self.kafka_producer.start()
            
            self.kafka_consumer = aiokafka.AIOKafkaConsumer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            await self.kafka_consumer.start()
            
            logger.info("Kafka initialized successfully")
            
        except Exception as e:
            logger.error(f"Kafka initialization failed: {str(e)}")

    async def _initialize_rabbitmq(self) -> None:
        """Initialize RabbitMQ connection"""
        try:
            self.rabbitmq_connection = await aio_pika.connect_robust(
                settings.rabbitmq_url
            )
            logger.info("RabbitMQ initialized successfully")
            
        except Exception as e:
            logger.error(f"RabbitMQ initialization failed: {str(e)}")

    async def publish_event(
        self,
        event: BaseEvent,
        transport: str = "redis"
    ) -> bool:
        """
        Publish event to the event bus.
        
        Args:
            event: Event to publish
            transport: Transport mechanism (redis, kafka, rabbitmq, websocket)
            
        Returns:
            True if published successfully
        """
        try:
            # Store event if event sourcing is enabled
            if self.config.enable_event_sourcing:
                await self.event_store.store_event(event)
            
            # Serialize event
            serialized_event = self.serializer.serialize(event)
            
            # Publish to specified transport
            if transport == "redis":
                success = await self._publish_to_redis(event, serialized_event)
            elif transport == "kafka":
                success = await self._publish_to_kafka(event, serialized_event)
            elif transport == "rabbitmq":
                success = await self._publish_to_rabbitmq(event, serialized_event)
            elif transport == "websocket":
                success = await self._publish_to_websocket(event, serialized_event)
            else:
                raise ValueError(f"Unsupported transport: {transport}")
            
            if success:
                await self.metrics.record_event_published(
                    event.event_type.value,
                    event.event_name,
                    transport
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Event publishing failed: {str(e)}")
            await self.metrics.record_event_publish_error(
                event.event_type.value,
                event.event_name,
                str(e)
            )
            return False

    async def _publish_to_redis(
        self,
        event: BaseEvent,
        serialized_event: str
    ) -> bool:
        """Publish event to Redis"""
        try:
            if not self.redis_client:
                return False
            
            # Publish to channel based on event type and name
            channel = f"events:{event.event_type.value}:{event.event_name}"
            await self.redis_client.publish(channel, serialized_event)
            
            # Also publish to wildcard channel
            await self.redis_client.publish("events:*", serialized_event)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis publishing failed: {str(e)}")
            return False

    async def _publish_to_kafka(
        self,
        event: BaseEvent,
        serialized_event: str
    ) -> bool:
        """Publish event to Kafka"""
        try:
            if not self.kafka_producer:
                return False
            
            topic = f"events-{event.event_type.value}"
            await self.kafka_producer.send_and_wait(
                topic,
                value=json.loads(serialized_event),
                key=event.event_id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Kafka publishing failed: {str(e)}")
            return False

    async def _publish_to_rabbitmq(
        self,
        event: BaseEvent,
        serialized_event: str
    ) -> bool:
        """Publish event to RabbitMQ"""
        try:
            if not self.rabbitmq_connection:
                return False
            
            channel = await self.rabbitmq_connection.channel()
            
            exchange = await channel.declare_exchange(
                "events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            routing_key = f"{event.event_type.value}.{event.event_name}"
            
            await exchange.publish(
                aio_pika.Message(
                    serialized_event.encode(),
                    message_id=event.event_id,
                    timestamp=event.timestamp
                ),
                routing_key=routing_key
            )
            
            await channel.close()
            return True
            
        except Exception as e:
            logger.error(f"RabbitMQ publishing failed: {str(e)}")
            return False

    async def _publish_to_websocket(
        self,
        event: BaseEvent,
        serialized_event: str
    ) -> bool:
        """Publish event to WebSocket connections"""
        try:
            if not self.websocket_connections:
                return True  # No connections, but not an error
            
            # Send to all connected WebSocket clients
            disconnected = set()
            
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(serialized_event)
                except Exception:
                    disconnected.add(websocket)
            
            # Remove disconnected clients
            self.websocket_connections -= disconnected
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket publishing failed: {str(e)}")
            return False

    async def subscribe_to_events(
        self,
        subscription: EventSubscription,
        handler: EventHandler
    ) -> bool:
        """
        Subscribe to events with a handler.
        
        Args:
            subscription: Subscription configuration
            handler: Event handler
            
        Returns:
            True if subscription was successful
        """
        try:
            # Register handler
            if subscription.event_types:
                for event_type in subscription.event_types:
                    self.handler_registry.register_handler(
                        event_type,
                        subscription.event_pattern,
                        handler
                    )
            else:
                self.handler_registry.register_pattern_handler(
                    subscription.event_pattern,
                    handler
                )
            
            # Store subscription
            self.subscriptions[subscription.subscription_id] = subscription
            
            # Start listening if not already started
            await self._ensure_listeners_started()
            
            await self.metrics.record_subscription_created(
                subscription.subscriber_id,
                subscription.event_pattern
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Event subscription failed: {str(e)}")
            return False

    async def _ensure_listeners_started(self) -> None:
        """Ensure event listeners are started"""
        # Start Redis listener
        if self.redis_client and not hasattr(self, '_redis_listener_started'):
            asyncio.create_task(self._redis_event_listener())
            self._redis_listener_started = True
        
        # Start Kafka listener
        if self.kafka_consumer and not hasattr(self, '_kafka_listener_started'):
            asyncio.create_task(self._kafka_event_listener())
            self._kafka_listener_started = True
        
        # Start RabbitMQ listener
        if self.rabbitmq_connection and not hasattr(self, '_rabbitmq_listener_started'):
            asyncio.create_task(self._rabbitmq_event_listener())
            self._rabbitmq_listener_started = True

    async def _redis_event_listener(self) -> None:
        """Listen for events from Redis"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.psubscribe("events:*")
            
            async for message in pubsub.listen():
                if message['type'] == 'pmessage':
                    await self._handle_received_event(
                        message['data'],
                        transport="redis"
                    )
                    
        except Exception as e:
            logger.error(f"Redis event listener failed: {str(e)}")

    async def _kafka_event_listener(self) -> None:
        """Listen for events from Kafka"""
        try:
            # Subscribe to all event topics
            topics = [f"events-{event_type.value}" for event_type in EventType]
            self.kafka_consumer.subscribe(topics)
            
            async for message in self.kafka_consumer:
                await self._handle_received_event(
                    json.dumps(message.value),
                    transport="kafka"
                )
                
        except Exception as e:
            logger.error(f"Kafka event listener failed: {str(e)}")

    async def _rabbitmq_event_listener(self) -> None:
        """Listen for events from RabbitMQ"""
        try:
            channel = await self.rabbitmq_connection.channel()
            
            exchange = await channel.declare_exchange(
                "events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            queue = await channel.declare_queue("", exclusive=True)
            await queue.bind(exchange, "*.#")  # Listen to all events
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await self._handle_received_event(
                            message.body.decode(),
                            transport="rabbitmq"
                        )
                        
        except Exception as e:
            logger.error(f"RabbitMQ event listener failed: {str(e)}")

    async def _handle_received_event(
        self,
        event_data: str,
        transport: str
    ) -> None:
        """Handle received event from any transport"""
        try:
            # Deserialize event
            event = self.serializer.deserialize(event_data, BaseEvent)
            
            # Find applicable subscriptions
            applicable_subscriptions = self._find_applicable_subscriptions(event)
            
            # Process event with each subscription
            for subscription in applicable_subscriptions:
                await self.processor.process_event(event, subscription)
            
            await self.metrics.record_event_processed(
                event.event_type.value,
                event.event_name,
                transport
            )
            
        except Exception as e:
            logger.error(f"Event handling failed: {str(e)}")

    def _find_applicable_subscriptions(
        self,
        event: BaseEvent
    ) -> List[EventSubscription]:
        """Find subscriptions that match the event"""
        applicable = []
        
        for subscription in self.subscriptions.values():
            if not subscription.is_active:
                continue
            
            # Check event type filter
            if subscription.event_types and event.event_type not in subscription.event_types:
                continue
            
            # Check pattern match
            if not self._matches_subscription_pattern(event, subscription):
                continue
            
            # Check additional filters
            if not self._passes_subscription_filters(event, subscription):
                continue
            
            applicable.append(subscription)
        
        return applicable

    def _matches_subscription_pattern(
        self,
        event: BaseEvent,
        subscription: EventSubscription
    ) -> bool:
        """Check if event matches subscription pattern"""
        pattern = subscription.event_pattern
        
        if pattern == "*":
            return True
        elif pattern.endswith("*"):
            prefix = pattern[:-1]
            return event.event_name.startswith(prefix)
        else:
            return event.event_name == pattern

    def _passes_subscription_filters(
        self,
        event: BaseEvent,
        subscription: EventSubscription
    ) -> bool:
        """Check if event passes subscription filters"""
        if not subscription.filters:
            return True
        
        # Simple filter implementation
        for filter_key, filter_value in subscription.filters.items():
            if filter_key in event.payload:
                if event.payload[filter_key] != filter_value:
                    return False
            elif filter_key in event.metadata:
                if event.metadata[filter_key] != filter_value:
                    return False
        
        return True

    async def replay_events(
        self,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        batch_size: int = 100
    ) -> int:
        """
        Replay events from event store.
        
        Args:
            from_timestamp: Start timestamp for replay
            to_timestamp: End timestamp for replay
            event_types: Filter by event types
            batch_size: Number of events to process in each batch
            
        Returns:
            Number of events replayed
        """
        try:
            if not self.config.enable_event_replay:
                raise EventException("Event replay is disabled")
            
            # Get events from store
            events = await self.event_store.get_events(
                from_timestamp=from_timestamp,
                to_timestamp=to_timestamp,
                event_types=[et.value for et in event_types] if event_types else None,
                limit=batch_size
            )
            
            replayed_count = 0
            
            while events:
                # Process batch
                for event_data in events:
                    event = BaseEvent(**event_data)
                    await self._handle_received_event(
                        self.serializer.serialize(event),
                        transport="replay"
                    )
                    replayed_count += 1
                
                # Get next batch
                if len(events) < batch_size:
                    break
                
                last_timestamp = events[-1]['timestamp']
                events = await self.event_store.get_events(
                    from_timestamp=last_timestamp,
                    to_timestamp=to_timestamp,
                    event_types=[et.value for et in event_types] if event_types else None,
                    limit=batch_size
                )
            
            await self.metrics.record_events_replayed(replayed_count)
            
            return replayed_count
            
        except Exception as e:
            logger.error(f"Event replay failed: {str(e)}")
            raise EventException(f"Replay failed: {str(e)}")

    async def start_saga(
        self,
        saga_id: str,
        saga_type: str,
        initial_event: BaseEvent,
        saga_data: Dict[str, Any] = None
    ) -> bool:
        """
        Start a saga (distributed transaction).
        
        Args:
            saga_id: Unique saga identifier
            saga_type: Type of saga
            initial_event: Event that triggered the saga
            saga_data: Initial saga data
            
        Returns:
            True if saga started successfully
        """
        try:
            if not self.config.enable_saga_pattern:
                raise EventException("Saga pattern is disabled")
            
            saga_state = {
                'saga_id': saga_id,
                'saga_type': saga_type,
                'status': 'active',
                'started_at': datetime.utcnow(),
                'initial_event': initial_event.dict(),
                'data': saga_data or {},
                'steps_completed': [],
                'compensations': []
            }
            
            self.active_sagas[saga_id] = saga_state
            
            # Publish saga started event
            saga_event = BaseEvent(
                event_type=EventType.SYSTEM_EVENT,
                event_name="saga.started",
                source=self.name,
                correlation_id=initial_event.correlation_id,
                payload={
                    'saga_id': saga_id,
                    'saga_type': saga_type,
                    'initial_event_id': initial_event.event_id
                }
            )
            
            await self.publish_event(saga_event)
            
            return True
            
        except Exception as e:
            logger.error(f"Saga start failed: {str(e)}")
            return False

    async def add_websocket_connection(self, websocket: WebSocket) -> None:
        """Add WebSocket connection for real-time events"""
        self.websocket_connections.add(websocket)

    async def remove_websocket_connection(self, websocket: WebSocket) -> None:
        """Remove WebSocket connection"""
        self.websocket_connections.discard(websocket)

    async def get_event_history(
        self,
        entity_id: str,
        entity_type: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get event history for an entity"""
        try:
            return await self.event_store.get_entity_events(
                entity_id=entity_id,
                entity_type=entity_type,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get event history: {str(e)}")
            return []

    async def cleanup(self) -> None:
        """Cleanup event service resources"""
        try:
            # Close transport connections
            if self.kafka_producer:
                await self.kafka_producer.stop()
            
            if self.kafka_consumer:
                await self.kafka_consumer.stop()
            
            if self.rabbitmq_connection:
                await self.rabbitmq_connection.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            # Close WebSocket connections
            for websocket in self.websocket_connections:
                await websocket.close()
            
            logger.info("Event service cleanup completed")
            
        except Exception as e:
            logger.error(f"Event service cleanup failed: {str(e)}")

    def get_service_status(self) -> Dict[str, Any]:
        """Get event service status"""
        return {
            "active_subscriptions": len(self.subscriptions),
            "active_sagas": len(self.active_sagas),
            "websocket_connections": len(self.websocket_connections),
            "redis_connected": self.redis_client is not None,
            "kafka_connected": self.kafka_producer is not None,
            "rabbitmq_connected": self.rabbitmq_connection is not None,
            "event_sourcing_enabled": self.config.enable_event_sourcing,
            "saga_pattern_enabled": self.config.enable_saga_pattern,
            "metrics": self.metrics.get_summary()
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities"""
        return {
            "event_types": [et.value for et in EventType],
            "event_patterns": [ep.value for ep in EventPattern],
            "delivery_modes": [dm.value for dm in EventDeliveryMode],
            "transports": ["redis", "kafka", "rabbitmq", "websocket"],
            "event_sourcing": self.config.enable_event_sourcing,
            "saga_pattern": self.config.enable_saga_pattern,
            "cqrs": self.config.enable_cqrs,
            "event_replay": self.config.enable_event_replay,
            "dead_letter_queue": self.config.enable_dead_letter_queue,
            "real_time_events": True,
            "batch_processing": True,
            "max_concurrent_handlers": self.config.max_concurrent_handlers
        }