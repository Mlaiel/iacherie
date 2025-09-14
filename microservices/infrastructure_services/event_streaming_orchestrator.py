"""
🔄 Enterprise Event Streaming Orchestrator
🎖️ Multi-Expert Implementation: ML Engineer + Backend Senior + Microservices + DevOps

Advanced event-driven architecture with:
- Kafka integration for event streaming
- CQRS and Event Sourcing patterns
- ML-powered event analytics
- Real-time event processing
- Dead letter queue handling
- Event replay capabilities
- Saga pattern implementation
- Circuit breaker for event handling

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import uuid
import hashlib
from collections import defaultdict, deque
import pickle
import gzip
import httpx
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import redis.asyncio as aioredis
import aiokafka
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from pydantic import BaseModel, Field
import yaml

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types in the system"""
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    AI_INFERENCE_REQUESTED = "ai.inference.requested"
    AI_INFERENCE_COMPLETED = "ai.inference.completed"
    USER_AUTHENTICATED = "user.authenticated"
    PAYMENT_PROCESSED = "payment.processed"
    COLLABORATION_INITIATED = "collaboration.initiated"
    SEO_OPTIMIZATION_COMPLETED = "seo.optimization.completed"
    PLATFORM_SYNC_REQUESTED = "platform.sync.requested"
    PLATFORM_SYNC_COMPLETED = "platform.sync.completed"
    SECURITY_THREAT_DETECTED = "security.threat.detected"
    SYSTEM_ALERT = "system.alert"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    SAGA_STARTED = "saga.started"
    SAGA_COMPLETED = "saga.completed"
    SAGA_FAILED = "saga.failed"
    SAGA_COMPENSATED = "saga.compensated"


class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventProcessingStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


@dataclass
class EventMetadata:
    """Event metadata"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_service: str = ""
    correlation_id: str = ""
    causation_id: str = ""
    version: int = 1
    priority: EventPriority = EventPriority.NORMAL
    ttl_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    tags: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None


@dataclass
class DomainEvent:
    """Base domain event"""
    event_type: EventType
    payload: Dict[str, Any]
    metadata: EventMetadata = field(default_factory=EventMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_type": self.event_type.value,
            "payload": self.payload,
            "metadata": asdict(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from dictionary"""
        metadata_data = data.get("metadata", {})
        metadata = EventMetadata(**metadata_data)
        return cls(
            event_type=EventType(data["event_type"]),
            payload=data["payload"],
            metadata=metadata
        )
    
    def serialize(self) -> bytes:
        """Serialize event for storage/transmission"""
        data = self.to_dict()
        # Convert datetime to ISO string
        data["metadata"]["timestamp"] = self.metadata.timestamp.isoformat()
        return gzip.compress(json.dumps(data).encode('utf-8'))
    
    @classmethod
    def deserialize(cls, data: bytes) -> 'DomainEvent':
        """Deserialize event from storage/transmission"""
        decompressed = gzip.decompress(data)
        event_data = json.loads(decompressed.decode('utf-8'))
        # Convert ISO string back to datetime
        event_data["metadata"]["timestamp"] = datetime.fromisoformat(event_data["metadata"]["timestamp"])
        return cls.from_dict(event_data)


class EventHandler(ABC):
    """Abstract event handler"""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> bool:
        """Handle the event. Return True if successful, False otherwise."""
        pass
    
    @property
    @abstractmethod
    def handled_events(self) -> List[EventType]:
        """List of event types this handler can process"""
        pass


class SagaStep:
    """Saga step definition"""
    
    def __init__(self, action: Callable, compensation: Callable):
        self.action = action
        self.compensation = compensation


class SagaOrchestrator:
    """
    🔄 Saga Pattern Orchestrator
    Manages distributed transactions across microservices
    """
    
    def __init__(self, event_bus: 'EventBus'):
        self.event_bus = event_bus
        self.active_sagas = {}
        self.saga_definitions = {}
    
    def define_saga(self, saga_name: str, steps: List[SagaStep]):
        """Define a saga with its steps"""
        self.saga_definitions[saga_name] = steps
        logger.info(f"Saga defined: {saga_name} with {len(steps)} steps")
    
    async def start_saga(self, saga_name: str, initial_data: Dict[str, Any]) -> str:
        """Start a saga execution"""
        saga_id = str(uuid.uuid4())
        
        if saga_name not in self.saga_definitions:
            raise ValueError(f"Saga {saga_name} not defined")
        
        saga_state = {
            "saga_id": saga_id,
            "saga_name": saga_name,
            "status": "running",
            "current_step": 0,
            "completed_steps": [],
            "failed_steps": [],
            "initial_data": initial_data,
            "step_results": {},
            "started_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.active_sagas[saga_id] = saga_state
        
        # Emit saga started event
        await self.event_bus.publish(DomainEvent(
            event_type=EventType.SAGA_STARTED,
            payload={
                "saga_id": saga_id,
                "saga_name": saga_name,
                "initial_data": initial_data
            },
            metadata=EventMetadata(
                source_service="saga-orchestrator",
                correlation_id=saga_id
            )
        ))
        
        # Start executing saga
        asyncio.create_task(self._execute_saga(saga_id))
        
        logger.info(f"Saga started: {saga_name} ({saga_id})")
        return saga_id
    
    async def _execute_saga(self, saga_id: str):
        """Execute saga steps"""
        try:
            saga_state = self.active_sagas[saga_id]
            saga_name = saga_state["saga_name"]
            steps = self.saga_definitions[saga_name]
            
            for step_index, step in enumerate(steps):
                saga_state["current_step"] = step_index
                saga_state["updated_at"] = datetime.utcnow().isoformat()
                
                try:
                    # Execute step action
                    result = await step.action(saga_state)
                    saga_state["step_results"][step_index] = result
                    saga_state["completed_steps"].append(step_index)
                    
                except Exception as e:
                    logger.error(f"Saga {saga_id} step {step_index} failed: {e}")
                    saga_state["failed_steps"].append(step_index)
                    
                    # Compensate completed steps
                    await self._compensate_saga(saga_id, step_index - 1)
                    return
            
            # All steps completed successfully
            saga_state["status"] = "completed"
            saga_state["updated_at"] = datetime.utcnow().isoformat()
            
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.SAGA_COMPLETED,
                payload={
                    "saga_id": saga_id,
                    "saga_name": saga_name,
                    "completed_at": saga_state["updated_at"]
                },
                metadata=EventMetadata(
                    source_service="saga-orchestrator",
                    correlation_id=saga_id
                )
            ))
            
            logger.info(f"Saga completed successfully: {saga_id}")
            
        except Exception as e:
            logger.error(f"Saga execution error: {e}")
            await self._fail_saga(saga_id)
    
    async def _compensate_saga(self, saga_id: str, from_step: int):
        """Compensate saga from given step backwards"""
        try:
            saga_state = self.active_sagas[saga_id]
            saga_name = saga_state["saga_name"]
            steps = self.saga_definitions[saga_name]
            
            # Compensate in reverse order
            for step_index in range(from_step, -1, -1):
                if step_index in saga_state["completed_steps"]:
                    try:
                        await steps[step_index].compensation(saga_state)
                        logger.info(f"Compensated step {step_index} for saga {saga_id}")
                    except Exception as e:
                        logger.error(f"Compensation failed for step {step_index}: {e}")
            
            saga_state["status"] = "compensated"
            saga_state["updated_at"] = datetime.utcnow().isoformat()
            
            await self.event_bus.publish(DomainEvent(
                event_type=EventType.SAGA_COMPENSATED,
                payload={
                    "saga_id": saga_id,
                    "saga_name": saga_name,
                    "compensated_at": saga_state["updated_at"]
                },
                metadata=EventMetadata(
                    source_service="saga-orchestrator",
                    correlation_id=saga_id
                )
            ))
            
        except Exception as e:
            logger.error(f"Saga compensation error: {e}")
            await self._fail_saga(saga_id)
    
    async def _fail_saga(self, saga_id: str):
        """Mark saga as failed"""
        saga_state = self.active_sagas[saga_id]
        saga_state["status"] = "failed"
        saga_state["updated_at"] = datetime.utcnow().isoformat()
        
        await self.event_bus.publish(DomainEvent(
            event_type=EventType.SAGA_FAILED,
            payload={
                "saga_id": saga_id,
                "saga_name": saga_state["saga_name"],
                "failed_at": saga_state["updated_at"]
            },
            metadata=EventMetadata(
                source_service="saga-orchestrator",
                correlation_id=saga_id
            )
        ))


class EventAnalytics:
    """
    📊 ML-Powered Event Analytics
    Analyzes event patterns and detects anomalies
    """
    
    def __init__(self):
        self.event_history = deque(maxlen=10000)
        self.event_patterns = defaultdict(list)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def add_event(self, event: DomainEvent):
        """Add event to analytics"""
        event_data = {
            "timestamp": event.metadata.timestamp.timestamp(),
            "event_type": event.event_type.value,
            "source_service": event.metadata.source_service,
            "priority": event.metadata.priority.value,
            "payload_size": len(json.dumps(event.payload))
        }
        
        self.event_history.append(event_data)
        self.event_patterns[event.event_type].append(event_data)
    
    def get_event_metrics(self) -> Dict[str, Any]:
        """Get event metrics"""
        if not self.event_history:
            return {"message": "No events to analyze"}
        
        events_by_type = defaultdict(int)
        events_by_service = defaultdict(int)
        events_by_priority = defaultdict(int)
        
        for event in self.event_history:
            events_by_type[event["event_type"]] += 1
            events_by_service[event["source_service"]] += 1
            events_by_priority[event["priority"]] += 1
        
        return {
            "total_events": len(self.event_history),
            "events_by_type": dict(events_by_type),
            "events_by_service": dict(events_by_service),
            "events_by_priority": dict(events_by_priority),
            "average_payload_size": np.mean([e["payload_size"] for e in self.event_history]),
            "events_per_minute": self._calculate_events_per_minute()
        }
    
    def _calculate_events_per_minute(self) -> float:
        """Calculate events per minute rate"""
        if len(self.event_history) < 2:
            return 0.0
        
        current_time = time.time()
        one_minute_ago = current_time - 60
        
        recent_events = [e for e in self.event_history if e["timestamp"] > one_minute_ago]
        return len(recent_events)
    
    def train_anomaly_detection(self):
        """Train anomaly detection model"""
        if len(self.event_history) < 100:
            logger.warning("Not enough events to train anomaly detection")
            return
        
        # Prepare features
        features = []
        for event in self.event_history:
            feature_vector = [
                event["timestamp"] % 86400,  # Time of day
                hash(event["event_type"]) % 1000,  # Event type hash
                hash(event["source_service"]) % 1000,  # Service hash
                event["payload_size"],
                {"low": 0, "normal": 1, "high": 2, "critical": 3}[event["priority"]]
            ]
            features.append(feature_vector)
        
        features = np.array(features)
        
        # Scale features
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        
        # Train anomaly detector
        self.anomaly_detector.fit(scaled_features)
        self.is_trained = True
        
        logger.info("Event anomaly detection model trained")
    
    def detect_anomaly(self, event: DomainEvent) -> Tuple[bool, float]:
        """Detect if event is anomalous"""
        if not self.is_trained:
            return False, 0.0
        
        feature_vector = np.array([[
            event.metadata.timestamp.timestamp() % 86400,
            hash(event.event_type.value) % 1000,
            hash(event.metadata.source_service) % 1000,
            len(json.dumps(event.payload)),
            {"low": 0, "normal": 1, "high": 2, "critical": 3}[event.metadata.priority.value]
        ]])
        
        scaled_features = self.scaler.transform(feature_vector)
        prediction = self.anomaly_detector.predict(scaled_features)[0]
        score = self.anomaly_detector.decision_function(scaled_features)[0]
        
        is_anomaly = prediction == -1
        return is_anomaly, abs(score)


class EventStore:
    """
    📚 Event Store for Event Sourcing
    Stores events permanently for replay and auditing
    """
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def append_event(self, stream_id: str, event: DomainEvent) -> int:
        """Append event to stream"""
        serialized_event = event.serialize()
        
        # Store in Redis stream
        stream_key = f"events:{stream_id}"
        event_id = await self.redis.xadd(
            stream_key,
            {
                "event_type": event.event_type.value,
                "data": serialized_event,
                "timestamp": event.metadata.timestamp.isoformat(),
                "source": event.metadata.source_service
            }
        )
        
        # Store event metadata for quick access
        metadata_key = f"event_metadata:{event.metadata.event_id}"
        await self.redis.setex(
            metadata_key,
            86400 * 30,  # 30 days TTL
            json.dumps({
                "stream_id": stream_id,
                "event_id": event_id.decode(),
                "event_type": event.event_type.value,
                "timestamp": event.metadata.timestamp.isoformat(),
                "source_service": event.metadata.source_service
            })
        )
        
        logger.debug(f"Event stored: {stream_id}:{event_id}")
        return len(stream_key)
    
    async def get_events(self, stream_id: str, from_id: str = "0") -> List[DomainEvent]:
        """Get events from stream"""
        stream_key = f"events:{stream_id}"
        
        events = await self.redis.xrange(stream_key, min=from_id)
        domain_events = []
        
        for event_id, fields in events:
            try:
                serialized_data = fields[b"data"]
                domain_event = DomainEvent.deserialize(serialized_data)
                domain_events.append(domain_event)
            except Exception as e:
                logger.error(f"Failed to deserialize event {event_id}: {e}")
        
        return domain_events
    
    async def replay_events(self, stream_id: str, handler: EventHandler, from_id: str = "0") -> int:
        """Replay events from stream"""
        events = await self.get_events(stream_id, from_id)
        processed_count = 0
        
        for event in events:
            if event.event_type in handler.handled_events:
                try:
                    await handler.handle(event)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Failed to replay event {event.metadata.event_id}: {e}")
        
        logger.info(f"Replayed {processed_count} events from stream {stream_id}")
        return processed_count


class CircuitBreaker:
    """Circuit breaker for event processing"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_process(self) -> bool:
        """Check if event processing is allowed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def record_success(self):
        """Record successful processing"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed processing"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class EventBus:
    """
    🚀 Enterprise Event Bus
    🎖️ Central event processing hub with enterprise features
    """
    
    def __init__(self, kafka_bootstrap_servers: str = "localhost:9092", 
                 redis_url: str = "redis://localhost:6379"):
        self.kafka_servers = kafka_bootstrap_servers
        self.redis_url = redis_url
        self.producer = None
        self.consumers = {}
        self.handlers = defaultdict(list)
        self.redis_client = None
        self.event_store = None
        self.event_analytics = EventAnalytics()
        self.saga_orchestrator = None
        self.circuit_breaker = CircuitBreaker()
        self.dead_letter_queue = deque()
        self.processing_metrics = {
            "events_processed": 0,
            "events_failed": 0,
            "events_retried": 0,
            "events_dead_lettered": 0
        }
    
    async def initialize(self):
        """Initialize event bus"""
        try:
            # Initialize Redis
            self.redis_client = aioredis.from_url(self.redis_url)
            self.event_store = EventStore(self.redis_client)
            
            # Initialize Kafka producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.kafka_servers,
                value_serializer=lambda v: v,
                compression_type="gzip",
                batch_size=16384,
                linger_ms=10
            )
            await self.producer.start()
            
            # Initialize saga orchestrator
            self.saga_orchestrator = SagaOrchestrator(self)
            
            # Setup default sagas
            await self._setup_default_sagas()
            
            logger.info("Event bus initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize event bus: {e}")
            raise
    
    async def _setup_default_sagas(self):
        """Setup default Ainflue workflow sagas"""
        
        # Content Processing Saga
        async def upload_content(saga_state):
            return {"content_id": "generated_id", "status": "uploaded"}
        
        async def compensate_upload(saga_state):
            # Delete uploaded content
            pass
        
        async def process_content(saga_state):
            return {"processed": True, "metadata": {}}
        
        async def compensate_process(saga_state):
            # Revert content processing
            pass
        
        async def ai_inference(saga_state):
            return {"ai_results": {}, "confidence": 0.95}
        
        async def compensate_ai(saga_state):
            # Clean up AI resources
            pass
        
        content_saga_steps = [
            SagaStep(upload_content, compensate_upload),
            SagaStep(process_content, compensate_process),
            SagaStep(ai_inference, compensate_ai)
        ]
        
        self.saga_orchestrator.define_saga("content_processing", content_saga_steps)
        
        # Payment Processing Saga
        async def reserve_funds(saga_state):
            return {"reservation_id": "res_123", "amount": saga_state["initial_data"]["amount"]}
        
        async def compensate_reserve(saga_state):
            # Release reserved funds
            pass
        
        async def charge_payment(saga_state):
            return {"transaction_id": "txn_456", "status": "charged"}
        
        async def compensate_charge(saga_state):
            # Refund payment
            pass
        
        async def update_wallet(saga_state):
            return {"wallet_updated": True}
        
        async def compensate_wallet(saga_state):
            # Revert wallet update
            pass
        
        payment_saga_steps = [
            SagaStep(reserve_funds, compensate_reserve),
            SagaStep(charge_payment, compensate_charge),
            SagaStep(update_wallet, compensate_wallet)
        ]
        
        self.saga_orchestrator.define_saga("payment_processing", payment_saga_steps)
    
    def register_handler(self, handler: EventHandler):
        """Register event handler"""
        for event_type in handler.handled_events:
            self.handlers[event_type].append(handler)
        
        logger.info(f"Handler registered for events: {[e.value for e in handler.handled_events]}")
    
    async def publish(self, event: DomainEvent, topic: Optional[str] = None):
        """Publish event to the bus"""
        try:
            # Add to analytics
            self.event_analytics.add_event(event)
            
            # Store in event store
            stream_id = event.metadata.correlation_id or "default"
            await self.event_store.append_event(stream_id, event)
            
            # Determine topic
            if not topic:
                topic = f"ainflue.{event.event_type.value.replace('.', '_')}"
            
            # Serialize event
            serialized_event = event.serialize()
            
            # Publish to Kafka
            await self.producer.send(topic, serialized_event)
            
            # Process locally if handlers exist
            await self._process_event_locally(event)
            
            logger.debug(f"Event published: {event.event_type.value} to topic {topic}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def _process_event_locally(self, event: DomainEvent):
        """Process event with local handlers"""
        if not self.circuit_breaker.can_process():
            logger.warning("Circuit breaker open, skipping local processing")
            return
        
        handlers = self.handlers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                success = await handler.handle(event)
                if success:
                    self.circuit_breaker.record_success()
                    self.processing_metrics["events_processed"] += 1
                else:
                    await self._handle_processing_failure(event, handler)
                    
            except Exception as e:
                logger.error(f"Handler {handler.__class__.__name__} failed: {e}")
                await self._handle_processing_failure(event, handler)
    
    async def _handle_processing_failure(self, event: DomainEvent, handler: EventHandler):
        """Handle event processing failure"""
        self.circuit_breaker.record_failure()
        
        if event.metadata.retry_count < event.metadata.max_retries:
            # Retry event
            event.metadata.retry_count += 1
            self.processing_metrics["events_retried"] += 1
            
            # Schedule retry with exponential backoff
            delay = 2 ** event.metadata.retry_count
            asyncio.create_task(self._retry_event_after_delay(event, delay))
            
        else:
            # Send to dead letter queue
            self.dead_letter_queue.append(event)
            self.processing_metrics["events_dead_lettered"] += 1
            
            logger.error(f"Event moved to dead letter queue: {event.metadata.event_id}")
        
        self.processing_metrics["events_failed"] += 1
    
    async def _retry_event_after_delay(self, event: DomainEvent, delay: int):
        """Retry event processing after delay"""
        await asyncio.sleep(delay)
        await self._process_event_locally(event)
    
    async def subscribe(self, topic: str, group_id: str = "default") -> AIOKafkaConsumer:
        """Subscribe to topic"""
        try:
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.kafka_servers,
                group_id=group_id,
                value_deserializer=lambda v: v,
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            
            await consumer.start()
            self.consumers[topic] = consumer
            
            # Start consuming in background
            asyncio.create_task(self._consume_events(consumer))
            
            logger.info(f"Subscribed to topic: {topic} with group: {group_id}")
            return consumer
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {e}")
            raise
    
    async def _consume_events(self, consumer: AIOKafkaConsumer):
        """Consume events from Kafka"""
        try:
            async for message in consumer:
                try:
                    # Deserialize event
                    event = DomainEvent.deserialize(message.value)
                    
                    # Process event
                    await self._process_event_locally(event)
                    
                except Exception as e:
                    logger.error(f"Failed to process consumed event: {e}")
                    
        except Exception as e:
            logger.error(f"Event consumption error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        analytics_metrics = self.event_analytics.get_event_metrics()
        
        return {
            "processing_metrics": self.processing_metrics,
            "analytics": analytics_metrics,
            "circuit_breaker": {
                "state": self.circuit_breaker.state,
                "failure_count": self.circuit_breaker.failure_count
            },
            "dead_letter_queue_size": len(self.dead_letter_queue),
            "active_consumers": len(self.consumers),
            "saga_orchestrator": {
                "active_sagas": len(self.saga_orchestrator.active_sagas),
                "defined_sagas": len(self.saga_orchestrator.saga_definitions)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def start_content_processing_workflow(self, content_data: Dict[str, Any]) -> str:
        """Start content processing workflow saga"""
        return await self.saga_orchestrator.start_saga("content_processing", content_data)
    
    async def start_payment_processing_workflow(self, payment_data: Dict[str, Any]) -> str:
        """Start payment processing workflow saga"""
        return await self.saga_orchestrator.start_saga("payment_processing", payment_data)
    
    async def shutdown(self):
        """Shutdown event bus gracefully"""
        # Stop producer
        if self.producer:
            await self.producer.stop()
        
        # Stop consumers
        for consumer in self.consumers.values():
            await consumer.stop()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Event bus shutdown complete")


# Example event handlers for Ainflue
class ContentUploadHandler(EventHandler):
    """Handler for content upload events"""
    
    @property
    def handled_events(self) -> List[EventType]:
        return [EventType.CONTENT_UPLOADED]
    
    async def handle(self, event: DomainEvent) -> bool:
        try:
            content_data = event.payload
            logger.info(f"Processing content upload: {content_data.get('content_id')}")
            
            # Simulate content processing
            await asyncio.sleep(0.1)
            
            return True
        except Exception as e:
            logger.error(f"Content upload handler failed: {e}")
            return False


class AIInferenceHandler(EventHandler):
    """Handler for AI inference events"""
    
    @property
    def handled_events(self) -> List[EventType]:
        return [EventType.AI_INFERENCE_REQUESTED, EventType.AI_INFERENCE_COMPLETED]
    
    async def handle(self, event: DomainEvent) -> bool:
        try:
            if event.event_type == EventType.AI_INFERENCE_REQUESTED:
                logger.info(f"Starting AI inference: {event.payload.get('model_id')}")
                # Simulate AI processing
                await asyncio.sleep(0.5)
                
            elif event.event_type == EventType.AI_INFERENCE_COMPLETED:
                logger.info(f"AI inference completed: {event.payload.get('inference_id')}")
            
            return True
        except Exception as e:
            logger.error(f"AI inference handler failed: {e}")
            return False


class SecurityThreatHandler(EventHandler):
    """Handler for security threat events"""
    
    @property
    def handled_events(self) -> List[EventType]:
        return [EventType.SECURITY_THREAT_DETECTED]
    
    async def handle(self, event: DomainEvent) -> bool:
        try:
            threat_data = event.payload
            logger.warning(f"Security threat detected: {threat_data.get('threat_type')}")
            
            # Immediate response to high/critical threats
            if threat_data.get('severity') in ['high', 'critical']:
                # Block IP, alert security team, etc.
                logger.critical(f"High severity threat response activated")
            
            return True
        except Exception as e:
            logger.error(f"Security threat handler failed: {e}")
            return False


# Example usage
async def setup_ainflue_event_bus():
    """Setup Ainflue event bus with handlers"""
    event_bus = EventBus()
    await event_bus.initialize()
    
    # Register handlers
    event_bus.register_handler(ContentUploadHandler())
    event_bus.register_handler(AIInferenceHandler())
    event_bus.register_handler(SecurityThreatHandler())
    
    # Subscribe to topics
    await event_bus.subscribe("ainflue.content_uploaded")
    await event_bus.subscribe("ainflue.ai_inference_requested")
    await event_bus.subscribe("ainflue.security_threat_detected")
    
    # Train anomaly detection
    event_bus.event_analytics.train_anomaly_detection()
    
    return event_bus


if __name__ == "__main__":
    async def main():
        event_bus = await setup_ainflue_event_bus()
        
        # Example: Publish some events
        test_events = [
            DomainEvent(
                event_type=EventType.CONTENT_UPLOADED,
                payload={"content_id": "test_123", "user_id": "user_456", "size": 1024},
                metadata=EventMetadata(source_service="content-service", priority=EventPriority.NORMAL)
            ),
            DomainEvent(
                event_type=EventType.AI_INFERENCE_REQUESTED,
                payload={"model_id": "ai_model_v1", "content_id": "test_123"},
                metadata=EventMetadata(source_service="ai-service", priority=EventPriority.HIGH)
            )
        ]
        
        for event in test_events:
            await event_bus.publish(event)
        
        # Start a content processing workflow
        content_data = {"content_id": "workflow_test", "user_id": "user_789"}
        saga_id = await event_bus.start_content_processing_workflow(content_data)
        print(f"Started content processing saga: {saga_id}")
        
        # Get metrics
        metrics = await event_bus.get_metrics()
        print(f"Event bus metrics: {json.dumps(metrics, indent=2)}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(10)
                metrics = await event_bus.get_metrics()
                logger.info(f"Events processed: {metrics['processing_metrics']['events_processed']}")
        except KeyboardInterrupt:
            await event_bus.shutdown()
    
    asyncio.run(main())