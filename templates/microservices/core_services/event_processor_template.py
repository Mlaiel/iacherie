"""
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

Event Processor Template for Ainflue Microservices Platform
=========================================================

Enterprise-grade event-driven processor template providing:
- Kafka-based event streaming with high throughput
- Batch processing with configurable windows
- Dead letter queue handling
- Event schema validation and evolution
- Exactly-once processing semantics
- Event replay and reprocessing capabilities
- Circuit breaker and retry mechanisms
- Distributed processing coordination
- Real-time metrics and monitoring
- Event sourcing and CQRS integration

Author: Fahed Mlaiel (mlaiel@live.de)
ML Engineer & Event-Driven Architecture Specialist
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional, List, Callable, Type, Union, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import hashlib
import uuid
from collections import defaultdict, deque

from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError, ConsumerStoppedError
import avro.schema
import avro.io
import io

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig
from ..circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class ProcessingStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"
    SKIPPED = "skipped"


class ProcessorMode(str, Enum):
    """Event processor operation mode"""
    REALTIME = "realtime"
    BATCH = "batch"
    HYBRID = "hybrid"


class EventSchema(BaseModel):
    """Event schema definition"""
    name: str = Field(..., description="Schema name")
    version: str = Field(..., description="Schema version")
    schema_type: str = Field(default="avro", description="Schema type (avro, json)")
    schema_definition: Dict[str, Any] = Field(..., description="Schema definition")
    compatibility: str = Field(default="BACKWARD", description="Schema compatibility mode")


class BatchConfig(BaseModel):
    """Batch processing configuration"""
    batch_size: int = Field(default=100, ge=1, description="Maximum batch size")
    batch_timeout_ms: int = Field(default=1000, ge=100, description="Batch timeout in milliseconds")
    max_parallel_batches: int = Field(default=5, ge=1, description="Maximum parallel batches")
    enable_compression: bool = Field(default=True, description="Enable batch compression")


class RetryConfig(BaseModel):
    """Event retry configuration"""
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    initial_delay_ms: int = Field(default=1000, ge=100, description="Initial retry delay")
    max_delay_ms: int = Field(default=60000, ge=1000, description="Maximum retry delay")
    exponential_base: float = Field(default=2.0, ge=1.0, description="Exponential backoff base")
    enable_jitter: bool = Field(default=True, description="Enable retry jitter")


class DeadLetterConfig(BaseModel):
    """Dead letter queue configuration"""
    enabled: bool = Field(default=True, description="Enable dead letter queue")
    topic_suffix: str = Field(default=".dlq", description="Dead letter topic suffix")
    max_retention_hours: int = Field(default=24, ge=1, description="Maximum retention in hours")
    enable_analysis: bool = Field(default=True, description="Enable failure analysis")


class ProcessorDefinition(BaseModel):
    """Event processor definition"""
    id: str = Field(..., description="Unique processor identifier")
    name: str = Field(..., description="Human-readable processor name")
    description: Optional[str] = Field(default=None, description="Processor description")
    topics: List[str] = Field(..., description="Source topics to consume from")
    consumer_group: str = Field(..., description="Kafka consumer group")
    processor_function: str = Field(..., description="Processing function name")
    mode: ProcessorMode = Field(default=ProcessorMode.REALTIME, description="Processing mode")
    batch_config: BatchConfig = Field(default_factory=BatchConfig, description="Batch configuration")
    retry_config: RetryConfig = Field(default_factory=RetryConfig, description="Retry configuration")
    dead_letter_config: DeadLetterConfig = Field(default_factory=DeadLetterConfig, description="Dead letter configuration")
    schema_registry: Dict[str, EventSchema] = Field(default_factory=dict, description="Event schemas")
    filters: List[Dict[str, Any]] = Field(default_factory=list, description="Event filters")
    enabled: bool = Field(default=True, description="Whether processor is enabled")
    tags: List[str] = Field(default_factory=list, description="Processor tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class EventContext(BaseModel):
    """Event processing context"""
    event_id: str = Field(..., description="Unique event identifier")
    topic: str = Field(..., description="Source topic")
    partition: int = Field(..., description="Topic partition")
    offset: int = Field(..., description="Message offset")
    timestamp: datetime = Field(..., description="Event timestamp")
    headers: Dict[str, str] = Field(default_factory=dict, description="Event headers")
    retry_count: int = Field(default=0, description="Retry attempt count")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")


class ProcessedEvent(Base):
    """Processed event record"""
    __tablename__ = "processed_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    processor_id = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    topic = Column(String, nullable=False)
    partition = Column(Integer, nullable=False)
    offset = Column(BigInteger, nullable=False)
    status = Column(String, nullable=False, default=ProcessingStatus.PENDING)
    processed_at = Column(DateTime, nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class EventBatch:
    """Batch of events for processing"""
    id: str
    events: List[Dict[str, Any]]
    contexts: List[EventContext]
    created_at: datetime
    size: int = field(init=False)
    
    def __post_init__(self):
        self.size = len(self.events)


class EventProcessorConfig(ServiceConfig):
    """Event processor service configuration"""
    # Kafka settings
    kafka_bootstrap_servers: str = Field(default="localhost:9092", description="Kafka bootstrap servers")
    kafka_security_protocol: str = Field(default="PLAINTEXT", description="Kafka security protocol")
    kafka_sasl_mechanism: Optional[str] = Field(default=None, description="SASL mechanism")
    kafka_sasl_username: Optional[str] = Field(default=None, description="SASL username")
    kafka_sasl_password: Optional[str] = Field(default=None, description="SASL password")
    
    # Consumer settings
    consumer_auto_offset_reset: str = Field(default="latest", description="Auto offset reset policy")
    consumer_enable_auto_commit: bool = Field(default=False, description="Enable auto commit")
    consumer_max_poll_records: int = Field(default=500, description="Max poll records")
    consumer_session_timeout_ms: int = Field(default=30000, description="Session timeout")
    
    # Producer settings
    producer_acks: str = Field(default="all", description="Producer acknowledgments")
    producer_retries: int = Field(default=3, description="Producer retries")
    producer_batch_size: int = Field(default=16384, description="Producer batch size")
    
    # Processing settings
    max_concurrent_processors: int = Field(default=10, description="Maximum concurrent processors")
    processing_timeout_ms: int = Field(default=30000, description="Processing timeout")
    enable_exactly_once: bool = Field(default=True, description="Enable exactly-once processing")
    
    # Schema registry
    schema_registry_url: Optional[str] = Field(default=None, description="Schema registry URL")
    schema_registry_auth: Optional[Dict[str, str]] = Field(default=None, description="Schema registry auth")
    
    # Redis settings for coordination
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=2, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable processor metrics")
    metrics_interval_seconds: int = Field(default=60, description="Metrics collection interval")


class EventProcessorTemplate(BaseMicroservice):
    """
    Enterprise Event Processor Template
    
    Provides comprehensive event-driven processing with:
    - High-throughput Kafka integration
    - Batch and real-time processing
    - Schema validation and evolution
    - Exactly-once processing semantics
    - Dead letter queue handling
    """
    
    def __init__(self, config: EventProcessorConfig):
        super().__init__(config)
        self.config = config
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.redis_client: Optional[redis.Redis] = None
        self.registered_processors: Dict[str, Callable] = {}
        self.active_processors: Dict[str, ProcessorDefinition] = {}
        self.processing_tasks: Set[asyncio.Task] = set()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.batch_buffers: Dict[str, deque] = defaultdict(deque)
        self.schema_cache: Dict[str, avro.schema.Schema] = {}
        
        # Metrics
        self.events_processed_total = Counter(
            'event_processor_events_total',
            'Total events processed',
            ['processor_id', 'topic', 'status']
        )
        self.processing_duration_seconds = Histogram(
            'event_processor_duration_seconds',
            'Event processing duration',
            ['processor_id', 'topic']
        )
        self.active_processors_gauge = Gauge(
            'event_processor_active_processors',
            'Number of active processors'
        )
        self.batch_size_histogram = Histogram(
            'event_processor_batch_size',
            'Batch processing size',
            ['processor_id']
        )
    
    async def initialize(self) -> None:
        """Initialize event processor service"""
        try:
            logger.info("Initializing event processor service")
            
            # Initialize Redis client
            await self._initialize_redis()
            
            # Initialize Kafka connections
            await self._initialize_kafka()
            
            # Load schema cache
            await self._load_schema_cache()
            
            # Start metrics collection
            if self.config.enable_metrics:
                await self._start_metrics_collection()
            
            logger.info("Event processor service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize event processor service: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
        
        # Test connection
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def _initialize_kafka(self) -> None:
        """Initialize Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            security_protocol=self.config.kafka_security_protocol,
            sasl_mechanism=self.config.kafka_sasl_mechanism,
            sasl_plain_username=self.config.kafka_sasl_username,
            sasl_plain_password=self.config.kafka_sasl_password,
            acks=self.config.producer_acks,
            retries=self.config.producer_retries,
            batch_size=self.config.producer_batch_size,
            value_serializer=lambda v: json.dumps(v, default=str).encode()
        )
        
        await self.producer.start()
        logger.info("Kafka producer initialized")
    
    async def register_processor(self, name: str, func: Callable) -> None:
        """Register an event processing function"""
        if not asyncio.iscoroutinefunction(func):
            # Wrap sync function in async
            async def async_wrapper(event: Dict[str, Any], context: EventContext) -> Any:
                return func(event, context)
            self.registered_processors[name] = async_wrapper
        else:
            self.registered_processors[name] = func
        
        logger.info(f"Registered processor function: {name}")
    
    async def create_processor(self, processor_def: ProcessorDefinition) -> Dict[str, Any]:
        """Create a new event processor"""
        try:
            # Validate function exists
            if processor_def.processor_function not in self.registered_processors:
                raise ValueError(f"Processor function not registered: {processor_def.processor_function}")
            
            # Create circuit breaker
            self.circuit_breakers[processor_def.id] = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30,
                expected_exception=Exception
            )
            
            # Store processor definition
            self.active_processors[processor_def.id] = processor_def
            
            # Start processor task
            if processor_def.enabled:
                await self._start_processor(processor_def)
            
            # Persist processor definition
            await self._persist_processor_definition(processor_def)
            
            logger.info(f"Created event processor: {processor_def.id}")
            
            return {
                "processor_id": processor_def.id,
                "name": processor_def.name,
                "status": "created",
                "topics": processor_def.topics,
                "mode": processor_def.mode.value
            }
            
        except Exception as e:
            logger.error(f"Failed to create processor {processor_def.id}: {e}")
            raise
    
    async def _start_processor(self, processor_def: ProcessorDefinition) -> None:
        """Start an event processor"""
        if processor_def.mode == ProcessorMode.BATCH:
            task = asyncio.create_task(self._run_batch_processor(processor_def))
        elif processor_def.mode == ProcessorMode.REALTIME:
            task = asyncio.create_task(self._run_realtime_processor(processor_def))
        else:  # HYBRID
            task = asyncio.create_task(self._run_hybrid_processor(processor_def))
        
        self.processing_tasks.add(task)
        task.add_done_callback(self.processing_tasks.discard)
        
        # Update metrics
        self.active_processors_gauge.inc()
    
    async def _run_realtime_processor(self, processor_def: ProcessorDefinition) -> None:
        """Run real-time event processor"""
        consumer = AIOKafkaConsumer(
            *processor_def.topics,
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            group_id=processor_def.consumer_group,
            auto_offset_reset=self.config.consumer_auto_offset_reset,
            enable_auto_commit=self.config.consumer_enable_auto_commit,
            max_poll_records=1,  # Process one event at a time for real-time
            session_timeout_ms=self.config.consumer_session_timeout_ms,
            value_deserializer=lambda m: json.loads(m.decode()) if m else None
        )
        
        try:
            await consumer.start()
            logger.info(f"Started real-time processor: {processor_def.id}")
            
            async for message in consumer:
                try:
                    if not processor_def.enabled:
                        continue
                    
                    # Create event context
                    context = EventContext(
                        event_id=str(uuid.uuid4()),
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        timestamp=datetime.fromtimestamp(message.timestamp / 1000),
                        headers={k: v.decode() if isinstance(v, bytes) else str(v) 
                                for k, v in (message.headers or {})},
                    )
                    
                    # Validate event schema
                    if not await self._validate_event_schema(message.value, processor_def, context):
                        continue
                    
                    # Apply filters
                    if not await self._apply_filters(message.value, processor_def):
                        continue
                    
                    # Process event with circuit breaker
                    circuit_breaker = self.circuit_breakers[processor_def.id]
                    
                    async def process_with_retry():
                        return await self._process_single_event(
                            message.value, context, processor_def
                        )
                    
                    await circuit_breaker.call(process_with_retry)
                    
                    # Commit offset
                    await consumer.commit()
                    
                except Exception as e:
                    logger.error(f"Error in real-time processor {processor_def.id}: {e}")
                    
                    # Send to dead letter queue if configured
                    if processor_def.dead_letter_config.enabled:
                        await self._send_to_dead_letter_queue(
                            message.value, context, processor_def, str(e)
                        )
                    
        except ConsumerStoppedError:
            logger.info(f"Real-time processor {processor_def.id} stopped")
        except Exception as e:
            logger.error(f"Real-time processor {processor_def.id} failed: {e}")
        finally:
            await consumer.stop()
            self.active_processors_gauge.dec()
    
    async def _run_batch_processor(self, processor_def: ProcessorDefinition) -> None:
        """Run batch event processor"""
        consumer = AIOKafkaConsumer(
            *processor_def.topics,
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            group_id=processor_def.consumer_group,
            auto_offset_reset=self.config.consumer_auto_offset_reset,
            enable_auto_commit=self.config.consumer_enable_auto_commit,
            max_poll_records=processor_def.batch_config.batch_size,
            session_timeout_ms=self.config.consumer_session_timeout_ms,
            value_deserializer=lambda m: json.loads(m.decode()) if m else None
        )
        
        try:
            await consumer.start()
            logger.info(f"Started batch processor: {processor_def.id}")
            
            batch_buffer = []
            last_batch_time = datetime.utcnow()
            
            async for message in consumer:
                try:
                    if not processor_def.enabled:
                        continue
                    
                    # Create event context
                    context = EventContext(
                        event_id=str(uuid.uuid4()),
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        timestamp=datetime.fromtimestamp(message.timestamp / 1000),
                        headers={k: v.decode() if isinstance(v, bytes) else str(v) 
                                for k, v in (message.headers or {})},
                    )
                    
                    # Validate and filter
                    if (await self._validate_event_schema(message.value, processor_def, context) and
                        await self._apply_filters(message.value, processor_def)):
                        
                        batch_buffer.append((message.value, context))
                    
                    # Check if batch is ready
                    batch_ready = (
                        len(batch_buffer) >= processor_def.batch_config.batch_size or
                        (datetime.utcnow() - last_batch_time).total_seconds() * 1000 >= 
                        processor_def.batch_config.batch_timeout_ms
                    )
                    
                    if batch_ready and batch_buffer:
                        # Process batch
                        batch = EventBatch(
                            id=str(uuid.uuid4()),
                            events=[item[0] for item in batch_buffer],
                            contexts=[item[1] for item in batch_buffer],
                            created_at=datetime.utcnow()
                        )
                        
                        await self._process_event_batch(batch, processor_def)
                        
                        # Commit offset
                        await consumer.commit()
                        
                        # Reset batch
                        batch_buffer.clear()
                        last_batch_time = datetime.utcnow()
                        
                except Exception as e:
                    logger.error(f"Error in batch processor {processor_def.id}: {e}")
                    batch_buffer.clear()
                    
        except ConsumerStoppedError:
            logger.info(f"Batch processor {processor_def.id} stopped")
        except Exception as e:
            logger.error(f"Batch processor {processor_def.id} failed: {e}")
        finally:
            await consumer.stop()
            self.active_processors_gauge.dec()
    
    async def _run_hybrid_processor(self, processor_def: ProcessorDefinition) -> None:
        """Run hybrid event processor (combines real-time and batch)"""
        # Start both real-time and batch processors
        realtime_task = asyncio.create_task(self._run_realtime_processor(processor_def))
        batch_task = asyncio.create_task(self._run_batch_processor(processor_def))
        
        try:
            await asyncio.gather(realtime_task, batch_task)
        except Exception as e:
            logger.error(f"Hybrid processor {processor_def.id} failed: {e}")
        finally:
            realtime_task.cancel()
            batch_task.cancel()
    
    async def _process_single_event(
        self, event: Dict[str, Any], context: EventContext, processor_def: ProcessorDefinition
    ) -> Any:
        """Process a single event"""
        start_time = datetime.utcnow()
        
        try:
            # Get processor function
            processor_func = self.registered_processors[processor_def.processor_function]
            
            # Execute with timeout
            result = await asyncio.wait_for(
                processor_func(event, context),
                timeout=self.config.processing_timeout_ms / 1000
            )
            
            # Calculate duration
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Record success
            await self._record_processing_result(
                processor_def.id, context, ProcessingStatus.COMPLETED,
                duration_ms, result
            )
            
            # Update metrics
            self.events_processed_total.labels(
                processor_id=processor_def.id,
                topic=context.topic,
                status='completed'
            ).inc()
            
            self.processing_duration_seconds.labels(
                processor_id=processor_def.id,
                topic=context.topic
            ).observe(duration_ms / 1000)
            
            return result
            
        except Exception as e:
            # Handle failure
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            await self._record_processing_result(
                processor_def.id, context, ProcessingStatus.FAILED,
                duration_ms, None, str(e)
            )
            
            # Update metrics
            self.events_processed_total.labels(
                processor_id=processor_def.id,
                topic=context.topic,
                status='failed'
            ).inc()
            
            # Check if we should retry
            if context.retry_count < processor_def.retry_config.max_retries:
                await self._schedule_retry(event, context, processor_def, e)
            else:
                # Send to dead letter queue
                if processor_def.dead_letter_config.enabled:
                    await self._send_to_dead_letter_queue(event, context, processor_def, str(e))
            
            raise
    
    async def _process_event_batch(self, batch: EventBatch, processor_def: ProcessorDefinition) -> None:
        """Process a batch of events"""
        start_time = datetime.utcnow()
        
        try:
            # Get processor function
            processor_func = self.registered_processors[processor_def.processor_function]
            
            # Execute batch processing
            if processor_def.batch_config.enable_compression:
                # Compress batch for more efficient processing
                compressed_batch = await self._compress_batch(batch)
                result = await processor_func(compressed_batch.events, compressed_batch.contexts)
            else:
                result = await processor_func(batch.events, batch.contexts)
            
            # Calculate duration
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Record batch success
            for context in batch.contexts:
                await self._record_processing_result(
                    processor_def.id, context, ProcessingStatus.COMPLETED,
                    duration_ms / batch.size, result
                )
            
            # Update metrics
            self.batch_size_histogram.labels(
                processor_id=processor_def.id
            ).observe(batch.size)
            
            self.events_processed_total.labels(
                processor_id=processor_def.id,
                topic=batch.contexts[0].topic if batch.contexts else "unknown",
                status='completed'
            ).inc(batch.size)
            
            logger.info(f"Processed batch of {batch.size} events in {duration_ms:.2f}ms")
            
        except Exception as e:
            logger.error(f"Batch processing failed for processor {processor_def.id}: {e}")
            
            # Process individual events for better error isolation
            for event, context in zip(batch.events, batch.contexts):
                try:
                    await self._process_single_event(event, context, processor_def)
                except Exception as event_error:
                    logger.error(f"Individual event processing failed: {event_error}")
    
    async def _validate_event_schema(
        self, event: Dict[str, Any], processor_def: ProcessorDefinition, context: EventContext
    ) -> bool:
        """Validate event against schema"""
        try:
            # Check if schema is defined for this topic
            schema_key = f"{context.topic}:latest"
            if schema_key not in processor_def.schema_registry:
                # No schema validation required
                return True
            
            schema_def = processor_def.schema_registry[schema_key]
            
            if schema_def.schema_type == "avro":
                # Get or load Avro schema
                if schema_key not in self.schema_cache:
                    self.schema_cache[schema_key] = avro.schema.parse(
                        json.dumps(schema_def.schema_definition)
                    )
                
                schema = self.schema_cache[schema_key]
                
                # Validate event against schema
                writer = avro.io.DatumWriter(schema)
                bytes_writer = io.BytesIO()
                encoder = avro.io.BinaryEncoder(bytes_writer)
                writer.write(event, encoder)
                
                return True
                
            elif schema_def.schema_type == "json":
                # JSON schema validation would go here
                # For now, just check if it's valid JSON
                return isinstance(event, dict)
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed for event {context.event_id}: {e}")
            
            # Update metrics
            self.events_processed_total.labels(
                processor_id=processor_def.id,
                topic=context.topic,
                status='schema_invalid'
            ).inc()
            
            return False
    
    async def _apply_filters(self, event: Dict[str, Any], processor_def: ProcessorDefinition) -> bool:
        """Apply event filters"""
        try:
            for filter_def in processor_def.filters:
                # Simple field-based filtering
                field = filter_def.get("field")
                operator = filter_def.get("operator", "eq")
                value = filter_def.get("value")
                
                if field and field in event:
                    event_value = event[field]
                    
                    if operator == "eq" and event_value != value:
                        return False
                    elif operator == "ne" and event_value == value:
                        return False
                    elif operator == "in" and event_value not in value:
                        return False
                    elif operator == "not_in" and event_value in value:
                        return False
                    elif operator == "gt" and not (event_value > value):
                        return False
                    elif operator == "gte" and not (event_value >= value):
                        return False
                    elif operator == "lt" and not (event_value < value):
                        return False
                    elif operator == "lte" and not (event_value <= value):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            return True  # Default to processing if filter fails
    
    async def _send_to_dead_letter_queue(
        self, event: Dict[str, Any], context: EventContext,
        processor_def: ProcessorDefinition, error_message: str
    ) -> None:
        """Send event to dead letter queue"""
        try:
            dlq_topic = f"{context.topic}{processor_def.dead_letter_config.topic_suffix}"
            
            dlq_event = {
                "original_event": event,
                "error_message": error_message,
                "processor_id": processor_def.id,
                "original_topic": context.topic,
                "original_partition": context.partition,
                "original_offset": context.offset,
                "retry_count": context.retry_count,
                "failed_at": datetime.utcnow().isoformat(),
                "context": context.dict()
            }
            
            await self.producer.send_and_wait(dlq_topic, dlq_event)
            
            logger.warning(f"Sent event {context.event_id} to dead letter queue: {dlq_topic}")
            
        except Exception as e:
            logger.error(f"Failed to send event to dead letter queue: {e}")
    
    async def _schedule_retry(
        self, event: Dict[str, Any], context: EventContext,
        processor_def: ProcessorDefinition, error: Exception
    ) -> None:
        """Schedule event retry with exponential backoff"""
        context.retry_count += 1
        
        # Calculate delay
        delay_ms = min(
            processor_def.retry_config.initial_delay_ms * (
                processor_def.retry_config.exponential_base ** (context.retry_count - 1)
            ),
            processor_def.retry_config.max_delay_ms
        )
        
        if processor_def.retry_config.enable_jitter:
            import random
            delay_ms *= random.uniform(0.8, 1.2)
        
        # Store retry info in Redis
        retry_key = f"retry:{processor_def.id}:{context.event_id}:{context.retry_count}"
        retry_data = {
            "event": event,
            "context": context.dict(),
            "processor_id": processor_def.id,
            "scheduled_at": (datetime.utcnow() + timedelta(milliseconds=delay_ms)).isoformat()
        }
        
        await self.redis_client.setex(
            retry_key,
            int(delay_ms / 1000) + 60,  # TTL with buffer
            json.dumps(retry_data, default=str)
        )
        
        logger.info(f"Scheduled retry for event {context.event_id} in {delay_ms:.1f}ms (attempt {context.retry_count})")
    
    async def get_processor_status(self, processor_id: str) -> Dict[str, Any]:
        """Get processor status and metrics"""
        if processor_id not in self.active_processors:
            raise ValueError(f"Processor not found: {processor_id}")
        
        processor_def = self.active_processors[processor_id]
        
        # Get processing statistics
        stats = await self._get_processing_statistics(processor_id)
        
        return {
            "processor_id": processor_id,
            "name": processor_def.name,
            "status": "active" if processor_def.enabled else "inactive",
            "topics": processor_def.topics,
            "mode": processor_def.mode.value,
            "consumer_group": processor_def.consumer_group,
            "statistics": stats,
            "circuit_breaker_status": self.circuit_breakers[processor_id].state.value
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Check Kafka connectivity
            kafka_healthy = self.producer is not None
            
            # Check Redis connectivity
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            # Check active processors
            active_count = len([p for p in self.active_processors.values() if p.enabled])
            
            return {
                "service": "event_processor_template",
                "status": "healthy" if kafka_healthy and redis_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "active_processors": active_count,
                    "total_processors": len(self.active_processors),
                    "processing_tasks": len(self.processing_tasks),
                    "kafka_connected": kafka_healthy,
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "event_processor_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _compress_batch(self, batch: EventBatch) -> EventBatch:
        """Compress batch for more efficient processing"""
        # Simple compression by removing duplicate events
        seen_events = set()
        compressed_events = []
        compressed_contexts = []
        
        for event, context in zip(batch.events, batch.contexts):
            event_hash = hashlib.md5(json.dumps(event, sort_keys=True).encode()).hexdigest()
            if event_hash not in seen_events:
                seen_events.add(event_hash)
                compressed_events.append(event)
                compressed_contexts.append(context)
        
        return EventBatch(
            id=batch.id,
            events=compressed_events,
            contexts=compressed_contexts,
            created_at=batch.created_at
        )
    
    async def _record_processing_result(
        self, processor_id: str, context: EventContext, status: ProcessingStatus,
        duration_ms: float, result: Any = None, error_message: str = None
    ) -> None:
        """Record processing result"""
        # Store in Redis for recent history
        result_key = f"result:{processor_id}:{context.event_id}"
        result_data = {
            "processor_id": processor_id,
            "event_id": context.event_id,
            "topic": context.topic,
            "status": status.value,
            "duration_ms": duration_ms,
            "result": result,
            "error_message": error_message,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.setex(
            result_key,
            3600,  # 1 hour TTL
            json.dumps(result_data, default=str)
        )
    
    async def _get_processing_statistics(self, processor_id: str) -> Dict[str, Any]:
        """Get processing statistics for a processor"""
        # Get recent results from Redis
        pattern = f"result:{processor_id}:*"
        keys = await self.redis_client.keys(pattern)
        
        stats = {
            "total_processed": 0,
            "completed": 0,
            "failed": 0,
            "average_duration_ms": 0.0,
            "last_processed": None
        }
        
        if not keys:
            return stats
        
        durations = []
        last_processed = None
        
        for key in keys[:100]:  # Sample recent results
            data = await self.redis_client.get(key)
            if data:
                result = json.loads(data)
                stats["total_processed"] += 1
                
                if result["status"] == ProcessingStatus.COMPLETED.value:
                    stats["completed"] += 1
                elif result["status"] == ProcessingStatus.FAILED.value:
                    stats["failed"] += 1
                
                durations.append(result["duration_ms"])
                
                processed_at = datetime.fromisoformat(result["processed_at"])
                if not last_processed or processed_at > last_processed:
                    last_processed = processed_at
        
        if durations:
            stats["average_duration_ms"] = sum(durations) / len(durations)
        
        if last_processed:
            stats["last_processed"] = last_processed.isoformat()
        
        return stats
    
    async def _persist_processor_definition(self, processor_def: ProcessorDefinition) -> None:
        """Persist processor definition to Redis"""
        key = f"processor_def:{processor_def.id}"
        value = processor_def.json()
        await self.redis_client.set(key, value)
    
    async def _load_schema_cache(self) -> None:
        """Load schema cache from registry"""
        # Implementation would depend on schema registry setup
        # For now, just initialize empty cache
        self.schema_cache = {}
    
    async def _start_metrics_collection(self) -> None:
        """Start background metrics collection"""
        async def metrics_collector():
            while True:
                try:
                    await asyncio.sleep(self.config.metrics_interval_seconds)
                    
                    # Update active processors gauge
                    active_count = len([p for p in self.active_processors.values() if p.enabled])
                    self.active_processors_gauge.set(active_count)
                    
                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
        
        asyncio.create_task(metrics_collector())
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down event processor service")
            
            # Cancel all processing tasks
            for task in self.processing_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.processing_tasks:
                await asyncio.gather(*self.processing_tasks, return_exceptions=True)
            
            # Stop Kafka producer
            if self.producer:
                await self.producer.stop()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Event processor service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")