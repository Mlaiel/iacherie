"""Event Streaming Template for Ainflue Platform
Enterprise-grade event streaming and real-time data processing

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Union, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel, validator, Field
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import aiokafka
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError

from core.config import get_settings
from core.database import get_db_session, Base
from core.auth import verify_streaming_token
from utils.exceptions import StreamingException, EventProcessingException
from monitoring.streaming_metrics import StreamingMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class EventType(str, Enum):
    """Types of events in the streaming system"""
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    USER_ACTION = "user.action"
    COLLABORATION_EVENT = "collaboration.event"
    PAYMENT_EVENT = "payment.event"
    SECURITY_ALERT = "security.alert"
    SYSTEM_EVENT = "system.event"
    ANALYTICS_EVENT = "analytics.event"
    NOTIFICATION_EVENT = "notification.event"
    MARKETPLACE_EVENT = "marketplace.event"
    AI_PROCESSING_EVENT = "ai.processing.event"


class StreamingProtocol(str, Enum):
    """Supported streaming protocols"""
    WEBSOCKET = "websocket"
    SSE = "server_sent_events"
    KAFKA = "kafka"
    REDIS_STREAMS = "redis_streams"
    WEBHOOK = "webhook"


class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StreamingConfig:
    """Configuration for event streaming"""
    kafka_bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    redis_url: str = "redis://localhost:6379"
    default_partition_count: int = 3
    default_replication_factor: int = 1
    consumer_group_id: str = "ainflue-consumers"
    batch_size: int = 100
    max_poll_interval_ms: int = 300000
    session_timeout_ms: int = 30000
    enable_auto_commit: bool = False
    compression_type: str = "gzip"


class StreamEvent(BaseModel):
    """Event model for streaming"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    source: str = Field(..., description="Event source service/module")
    data: Dict[str, Any] = Field(..., description="Event payload data")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    priority: EventPriority = Field(default=EventPriority.NORMAL, description="Event priority")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    tenant_id: Optional[str] = Field(default=None, description="Tenant/organization ID")
    version: str = Field(default="1.0", description="Event schema version")
    ttl_seconds: Optional[int] = Field(default=None, description="Time to live in seconds")

    @validator('event_id')
    def validate_event_id(cls, v):
        if not v:
            raise ValueError('Event ID cannot be empty')
        return v

    @validator('data')
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Data must be a dictionary')
        return v


class EventSubscription(BaseModel):
    """Event subscription model"""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_types: List[EventType] = Field(..., description="Event types to subscribe to")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Event filters")
    protocol: StreamingProtocol = Field(default=StreamingProtocol.WEBSOCKET)
    endpoint: Optional[str] = Field(default=None, description="Endpoint for webhook delivery")
    user_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EventLog(Base):
    """Database model for event logging"""
    __tablename__ = "event_stream_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    source = Column(String(255), nullable=False, index=True)
    priority = Column(String(50), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    correlation_id = Column(String(255), nullable=True, index=True)
    data = Column(JSONB, nullable=False)
    metadata = Column(JSONB, nullable=True)
    processed = Column(Boolean, default=False, nullable=False)
    processing_attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)


class BaseEventStreamer(ABC):
    """Abstract base class for event streamers"""

    def __init__(self, config: StreamingConfig):
        self.config = config
        self.metrics = StreamingMetrics()
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}

    @abstractmethod
    async def initialize(self):
        """Initialize the streamer"""
        pass

    @abstractmethod
    async def publish_event(self, event: StreamEvent, topic: Optional[str] = None):
        """Publish an event to the stream"""
        pass

    @abstractmethod
    async def subscribe(self, subscription: EventSubscription):
        """Subscribe to events"""
        pass

    @abstractmethod
    async def close(self):
        """Close the streamer and cleanup resources"""
        pass

    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def process_event(self, event: StreamEvent):
        """Process incoming event with registered handlers"""
        try:
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler failed for {event.event_type}: {e}")

            await self.metrics.increment_events_processed(event.event_type.value)
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            await self.metrics.increment_events_failed(event.event_type.value)


class KafkaEventStreamer(BaseEventStreamer):
    """Kafka-based event streaming implementation"""

    def __init__(self, config: StreamingConfig):
        super().__init__(config)
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self.admin_client = None

    async def initialize(self):
        """Initialize Kafka producer and admin client"""
        try:
            # Initialize producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                compression_type=self.config.compression_type,
                retry_backoff_ms=100,
                max_in_flight_requests_per_connection=5,
                acks='all'
            )
            await self.producer.start()

            # Initialize admin client for topic management
            from aiokafka.admin import AIOKafkaAdminClient, NewTopic
            self.admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.config.kafka_bootstrap_servers
            )
            await self.admin_client.start()

            logger.info("Kafka event streamer initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Kafka streamer: {e}")
            raise StreamingException(f"Kafka initialization failed: {e}")

    async def create_topic(self, topic_name: str, num_partitions: Optional[int] = None):
        """Create Kafka topic if it doesn't exist"""
        try:
            from aiokafka.admin import NewTopic
            
            # Check if topic exists
            metadata = await self.admin_client.describe_topics([topic_name])
            if topic_name in metadata:
                return

            # Create topic
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions or self.config.default_partition_count,
                replication_factor=self.config.default_replication_factor
            )
            
            await self.admin_client.create_topics([topic])
            logger.info(f"Created Kafka topic: {topic_name}")

        except Exception as e:
            logger.error(f"Failed to create topic {topic_name}: {e}")

    async def publish_event(self, event: StreamEvent, topic: Optional[str] = None):
        """Publish event to Kafka topic"""
        try:
            topic_name = topic or f"ainflue-{event.event_type.value.replace('.', '-')}"
            
            # Ensure topic exists
            await self.create_topic(topic_name)

            # Prepare event data
            event_data = event.dict()
            
            # Determine partition key (for event ordering)
            partition_key = None
            if event.user_id:
                partition_key = event.user_id
            elif event.correlation_id:
                partition_key = event.correlation_id
            else:
                partition_key = event.event_id

            # Send to Kafka
            await self.producer.send_and_wait(
                topic_name,
                value=event_data,
                key=partition_key.encode('utf-8') if partition_key else None
            )

            await self.metrics.increment_events_published(event.event_type.value)
            logger.debug(f"Published event {event.event_id} to topic {topic_name}")

        except Exception as e:
            logger.error(f"Failed to publish event to Kafka: {e}")
            await self.metrics.increment_events_failed(event.event_type.value)
            raise StreamingException(f"Event publishing failed: {e}")

    async def subscribe(self, subscription: EventSubscription):
        """Subscribe to Kafka topics"""
        try:
            # Create consumer
            consumer = AIOKafkaConsumer(
                group_id=f"{self.config.consumer_group_id}-{subscription.subscription_id}",
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=self.config.enable_auto_commit,
                max_poll_interval_ms=self.config.max_poll_interval_ms,
                session_timeout_ms=self.config.session_timeout_ms
            )

            # Subscribe to relevant topics
            topics = [f"ainflue-{et.value.replace('.', '-')}" for et in subscription.event_types]
            consumer.subscribe(topics)
            
            await consumer.start()
            self.consumers[subscription.subscription_id] = consumer
            self.subscriptions[subscription.subscription_id] = subscription

            # Start consuming in background
            asyncio.create_task(self._consume_events(subscription.subscription_id))
            
            logger.info(f"Created Kafka subscription {subscription.subscription_id} for topics: {topics}")

        except Exception as e:
            logger.error(f"Failed to create Kafka subscription: {e}")
            raise StreamingException(f"Subscription failed: {e}")

    async def _consume_events(self, subscription_id: str):
        """Consume events from Kafka"""
        consumer = self.consumers.get(subscription_id)
        subscription = self.subscriptions.get(subscription_id)
        
        if not consumer or not subscription:
            return

        try:
            async for message in consumer:
                try:
                    # Deserialize event
                    event_data = message.value
                    event = StreamEvent(**event_data)

                    # Apply filters if configured
                    if subscription.filters:
                        if not self._apply_filters(event, subscription.filters):
                            continue

                    # Process event
                    await self.process_event(event)

                    # Commit offset
                    if not self.config.enable_auto_commit:
                        await consumer.commit()

                except Exception as e:
                    logger.error(f"Failed to process Kafka message: {e}")

        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")

    def _apply_filters(self, event: StreamEvent, filters: Dict[str, Any]) -> bool:
        """Apply filters to determine if event should be processed"""
        try:
            for key, value in filters.items():
                if key == 'user_id' and event.user_id != value:
                    return False
                elif key == 'source' and event.source != value:
                    return False
                elif key == 'priority' and event.priority != value:
                    return False
                # Add more filter logic as needed
            
            return True
        except Exception:
            return False

    async def close(self):
        """Close Kafka connections"""
        if self.producer:
            await self.producer.stop()
        
        for consumer in self.consumers.values():
            await consumer.stop()
        
        if self.admin_client:
            await self.admin_client.close()


class RedisEventStreamer(BaseEventStreamer):
    """Redis Streams-based event streaming implementation"""

    def __init__(self, config: StreamingConfig):
        super().__init__(config)
        self.redis: Optional[aioredis.Redis] = None

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis event streamer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis streamer: {e}")
            raise StreamingException(f"Redis initialization failed: {e}")

    async def publish_event(self, event: StreamEvent, topic: Optional[str] = None):
        """Publish event to Redis stream"""
        try:
            stream_name = topic or f"ainflue:{event.event_type.value}"
            
            # Prepare event data
            event_data = event.dict()
            fields = {}
            for key, value in event_data.items():
                fields[key] = json.dumps(value, default=str)

            # Add to Redis stream
            message_id = await self.redis.xadd(stream_name, fields)
            
            # Set TTL if specified
            if event.ttl_seconds:
                await self.redis.expire(stream_name, event.ttl_seconds)

            await self.metrics.increment_events_published(event.event_type.value)
            logger.debug(f"Published event {event.event_id} to Redis stream {stream_name}: {message_id}")

        except Exception as e:
            logger.error(f"Failed to publish event to Redis: {e}")
            await self.metrics.increment_events_failed(event.event_type.value)
            raise StreamingException(f"Event publishing failed: {e}")

    async def subscribe(self, subscription: EventSubscription):
        """Subscribe to Redis streams"""
        try:
            self.subscriptions[subscription.subscription_id] = subscription
            
            # Start consuming in background
            asyncio.create_task(self._consume_redis_events(subscription))
            
            logger.info(f"Created Redis subscription {subscription.subscription_id}")

        except Exception as e:
            logger.error(f"Failed to create Redis subscription: {e}")
            raise StreamingException(f"Subscription failed: {e}")

    async def _consume_redis_events(self, subscription: EventSubscription):
        """Consume events from Redis streams"""
        try:
            # Create consumer group
            group_name = f"group-{subscription.subscription_id}"
            consumer_name = f"consumer-{subscription.subscription_id}"
            
            streams = {f"ainflue:{et.value}": ">" for et in subscription.event_types}
            
            while True:
                try:
                    # Read from streams
                    messages = await self.redis.xreadgroup(
                        group_name,
                        consumer_name,
                        streams,
                        count=self.config.batch_size,
                        block=1000
                    )

                    for stream_name, stream_messages in messages:
                        for message_id, fields in stream_messages:
                            try:
                                # Deserialize event
                                event_data = {}
                                for key, value in fields.items():
                                    event_data[key] = json.loads(value)
                                
                                event = StreamEvent(**event_data)

                                # Apply filters
                                if subscription.filters:
                                    if not self._apply_filters(event, subscription.filters):
                                        continue

                                # Process event
                                await self.process_event(event)

                                # Acknowledge message
                                await self.redis.xack(stream_name, group_name, message_id)

                            except Exception as e:
                                logger.error(f"Failed to process Redis message: {e}")

                except Exception as e:
                    logger.error(f"Redis consumer error: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Redis consumer failed: {e}")

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()


class WebSocketEventStreamer(BaseEventStreamer):
    """WebSocket-based event streaming for real-time browser connections"""

    def __init__(self, config: StreamingConfig):
        super().__init__(config)
        self.active_connections: Dict[str, WebSocket] = {}

    async def initialize(self):
        """Initialize WebSocket streamer"""
        logger.info("WebSocket event streamer initialized")

    async def connect_websocket(self, websocket: WebSocket, subscription: EventSubscription):
        """Accept WebSocket connection and setup subscription"""
        await websocket.accept()
        self.active_connections[subscription.subscription_id] = websocket
        self.subscriptions[subscription.subscription_id] = subscription
        
        logger.info(f"WebSocket connected: {subscription.subscription_id}")

    async def disconnect_websocket(self, subscription_id: str):
        """Disconnect WebSocket"""
        if subscription_id in self.active_connections:
            del self.active_connections[subscription_id]
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
        
        logger.info(f"WebSocket disconnected: {subscription_id}")

    async def publish_event(self, event: StreamEvent, topic: Optional[str] = None):
        """Publish event to relevant WebSocket connections"""
        try:
            # Find matching subscriptions
            for subscription_id, subscription in self.subscriptions.items():
                if event.event_type in subscription.event_types:
                    # Apply filters
                    if subscription.filters and not self._apply_filters(event, subscription.filters):
                        continue

                    # Send to WebSocket
                    websocket = self.active_connections.get(subscription_id)
                    if websocket:
                        try:
                            await websocket.send_json(event.dict())
                            await self.metrics.increment_events_published(event.event_type.value)
                        except Exception as e:
                            logger.warning(f"Failed to send to WebSocket {subscription_id}: {e}")
                            await self.disconnect_websocket(subscription_id)

        except Exception as e:
            logger.error(f"Failed to publish event to WebSocket: {e}")

    async def subscribe(self, subscription: EventSubscription):
        """Subscribe is handled via connect_websocket"""
        pass

    async def close(self):
        """Close all WebSocket connections"""
        for websocket in self.active_connections.values():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")


class EventStreamManager:
    """Manager for multiple event streamers"""

    def __init__(self, config: StreamingConfig):
        self.config = config
        self.streamers: Dict[StreamingProtocol, BaseEventStreamer] = {}
        self.default_streamer: Optional[BaseEventStreamer] = None

    async def initialize(self):
        """Initialize all streamers"""
        try:
            # Initialize Kafka streamer
            kafka_streamer = KafkaEventStreamer(self.config)
            await kafka_streamer.initialize()
            self.streamers[StreamingProtocol.KAFKA] = kafka_streamer
            
            # Initialize Redis streamer
            redis_streamer = RedisEventStreamer(self.config)
            await redis_streamer.initialize()
            self.streamers[StreamingProtocol.REDIS_STREAMS] = redis_streamer
            
            # Initialize WebSocket streamer
            websocket_streamer = WebSocketEventStreamer(self.config)
            await websocket_streamer.initialize()
            self.streamers[StreamingProtocol.WEBSOCKET] = websocket_streamer

            # Set default streamer
            self.default_streamer = kafka_streamer

            logger.info("Event stream manager initialized with all protocols")

        except Exception as e:
            logger.error(f"Failed to initialize event stream manager: {e}")
            raise

    async def publish_event(
        self,
        event: StreamEvent,
        protocols: Optional[List[StreamingProtocol]] = None,
        topic: Optional[str] = None
    ):
        """Publish event to specified protocols"""
        try:
            if protocols is None:
                protocols = [StreamingProtocol.KAFKA]  # Default to Kafka

            for protocol in protocols:
                streamer = self.streamers.get(protocol)
                if streamer:
                    await streamer.publish_event(event, topic)
                else:
                    logger.warning(f"No streamer available for protocol: {protocol}")

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise EventProcessingException(f"Event publishing failed: {e}")

    async def subscribe(
        self,
        subscription: EventSubscription,
        protocol: Optional[StreamingProtocol] = None
    ):
        """Subscribe to events using specified protocol"""
        try:
            target_protocol = protocol or subscription.protocol
            streamer = self.streamers.get(target_protocol)
            
            if not streamer:
                raise StreamingException(f"No streamer available for protocol: {target_protocol}")

            await streamer.subscribe(subscription)

        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise

    def get_streamer(self, protocol: StreamingProtocol) -> Optional[BaseEventStreamer]:
        """Get streamer for specific protocol"""
        return self.streamers.get(protocol)

    async def close_all(self):
        """Close all streamers"""
        for streamer in self.streamers.values():
            try:
                await streamer.close()
            except Exception as e:
                logger.error(f"Error closing streamer: {e}")


# Global event stream manager
stream_manager = EventStreamManager(StreamingConfig())

async def get_stream_manager() -> EventStreamManager:
    """Dependency to get stream manager"""
    return stream_manager


# FastAPI integration for WebSocket streaming
app = FastAPI()

@app.websocket("/ws/events/{subscription_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    subscription_id: str,
    event_types: str = "user.action,content.created",  # Comma-separated
    filters: Optional[str] = None
):
    """WebSocket endpoint for real-time event streaming"""
    try:
        # Parse event types
        parsed_event_types = [EventType(et.strip()) for et in event_types.split(",")]
        
        # Parse filters
        parsed_filters = None
        if filters:
            import urllib.parse
            parsed_filters = dict(urllib.parse.parse_qsl(filters))

        # Create subscription
        subscription = EventSubscription(
            subscription_id=subscription_id,
            event_types=parsed_event_types,
            filters=parsed_filters,
            protocol=StreamingProtocol.WEBSOCKET
        )

        # Get WebSocket streamer
        websocket_streamer = stream_manager.get_streamer(StreamingProtocol.WEBSOCKET)
        if not websocket_streamer:
            await websocket.close(code=1011, reason="WebSocket streaming not available")
            return

        # Connect and handle WebSocket
        await websocket_streamer.connect_websocket(websocket, subscription)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                # Could handle client messages here (ping/pong, etc.)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {subscription_id}")
        finally:
            await websocket_streamer.disconnect_websocket(subscription_id)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


# Example event publishing
async def publish_content_event(content_id: str, user_id: str, action: str):
    """Example function to publish content-related events"""
    event = StreamEvent(
        event_type=EventType.CONTENT_CREATED if action == "created" else EventType.CONTENT_UPDATED,
        source="content_service",
        data={
            "content_id": content_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        },
        user_id=user_id,
        priority=EventPriority.HIGH
    )
    
    # Publish to all protocols
    await stream_manager.publish_event(
        event,
        protocols=[StreamingProtocol.KAFKA, StreamingProtocol.WEBSOCKET]
    )


if __name__ == "__main__":
    import uvicorn
    
    async def startup():
        await stream_manager.initialize()
    
    async def shutdown():
        await stream_manager.close_all()
    
    app.add_event_handler("startup", startup)
    app.add_event_handler("shutdown", shutdown)
    
    uvicorn.run(app, host="0.0.0.0", port=8003)