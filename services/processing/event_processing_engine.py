"""
Event Processing Engine - Enterprise Event-Driven Architecture Layer
====================================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Roles**: Microservices + Backend Senior + DevOps + Lead Dev IA + DBA
**Module**: Event Processing Engine
**Version**: 2.0.0 Enterprise
**Created**: 2025-01-07

Enterprise-grade event processing engine with event-driven architecture CQRS,
event sourcing, pattern matching, saga patterns, and circuit breaker resilience.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque
import hashlib
import re
from pathlib import Path

# Enterprise imports
try:
    import redis
    import aiofiles
    import psutil
    import numpy as np
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
except ImportError as e:
    logging.warning(f"Optional dependency missing: {e}")

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Event type classifications."""
    DOMAIN_EVENT = "domain_event"
    INTEGRATION_EVENT = "integration_event"
    COMMAND = "command"
    QUERY = "query"
    NOTIFICATION = "notification"
    SYSTEM_EVENT = "system_event"

class EventStatus(Enum):
    """Event processing status."""
    CREATED = "created"
    PUBLISHED = "published"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

class EventPriority(Enum):
    """Event priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class SagaStatus(Enum):
    """Saga execution status."""
    STARTED = "started"
    EXECUTING = "executing"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Event:
    """Event definition with full metadata."""
    event_id: str
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    event_name: str
    event_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    status: EventStatus = EventStatus.CREATED

@dataclass
class EventHandler:
    """Event handler definition."""
    handler_id: str
    handler_name: str
    event_patterns: List[str]  # Patterns to match events
    handler_function: Callable
    priority: int = 100
    async_processing: bool = True
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    circuit_breaker_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EventStream:
    """Event stream definition."""
    stream_id: str
    stream_name: str
    aggregate_type: str
    events: List[Event] = field(default_factory=list)
    version: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class SagaStep:
    """Saga orchestration step."""
    step_id: str
    step_name: str
    command: Dict[str, Any]
    compensation_command: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retry_count: int = 3

@dataclass
class Saga:
    """Saga orchestration definition."""
    saga_id: str
    saga_type: str
    correlation_id: str
    steps: List[SagaStep]
    current_step: int = 0
    status: SagaStatus = SagaStatus.STARTED
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    compensations: List[str] = field(default_factory=list)

@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking."""
    handler_id: str
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    failure_threshold: int = 5
    timeout: int = 60  # seconds
    half_open_max_calls: int = 3

class EventProcessingEngine:
    """
    🔗 **MICROSERVICES + BACKEND SENIOR + DEVOPS**
    Enterprise event processing engine with CQRS and event sourcing.
    
    Features:
    - Event-driven architecture CQRS
    - Event sourcing avec audit complet
    - Pattern matching et routing intelligent
    - Saga pattern pour transactions distribuées
    - Circuit breaker et resilience patterns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Event storage and streams
        self.event_store: Dict[str, Event] = {}
        self.event_streams: Dict[str, EventStream] = {}
        self.event_handlers: Dict[str, EventHandler] = {}
        self.sagas: Dict[str, Saga] = {}
        
        # Processing infrastructure
        self.event_queue: deque = deque()
        self.dead_letter_queue: deque = deque()
        self.processing_threads: List[threading.Thread] = []
        self.running = False
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        
        # Pattern matching
        self.compiled_patterns: Dict[str, re.Pattern] = {}
        
        # Performance metrics
        self.metrics = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "average_processing_time": 0.0,
            "handler_performance": defaultdict(lambda: {"processed": 0, "failed": 0, "avg_time": 0.0}),
            "saga_completions": 0,
            "saga_failures": 0,
            "circuit_breaker_opens": 0
        }
        
        # External systems
        self.kafka_producer = None
        self.kafka_consumer = None
        self.redis_client = None
        
        # Initialize external connections
        self._init_kafka()
        self._init_redis()
        
        logger.info("Event Processing Engine initialized")

    def _init_kafka(self) -> None:
        """🔗 **MICROSERVICES**: Initialize Kafka for external event streaming."""
        try:
            kafka_config = self.config.get("kafka", {})
            if kafka_config.get("enabled", False):
                self.kafka_producer = KafkaProducer(
                    bootstrap_servers=kafka_config.get("bootstrap_servers", ["localhost:9092"]),
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
                logger.info("Kafka producer initialized")
        except Exception as e:
            logger.warning(f"Kafka initialization failed: {e}")

    def _init_redis(self) -> None:
        """Initialize Redis for event caching and coordination."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 2),
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis connection established for event processing")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")

    def register_handler(self, handler: EventHandler) -> None:
        """
        📝 Register event handler with pattern matching.
        
        Args:
            handler: Event handler to register
        """
        self.event_handlers[handler.handler_id] = handler
        
        # Compile patterns for performance
        for pattern in handler.event_patterns:
            if pattern not in self.compiled_patterns:
                self.compiled_patterns[pattern] = re.compile(pattern)
        
        # Initialize circuit breaker
        self.circuit_breakers[handler.handler_id] = CircuitBreakerState(
            handler_id=handler.handler_id,
            **handler.circuit_breaker_config
        )
        
        logger.info(f"Event handler '{handler.handler_name}' registered")

    async def publish_event(self, event: Event) -> Dict[str, Any]:
        """
        🔗 **MICROSERVICES**: Publish event to processing engine.
        
        Args:
            event: Event to publish
            
        Returns:
            Publication result
        """
        start_time = time.time()
        
        try:
            # Generate unique event ID if not provided
            if not event.event_id:
                event.event_id = str(uuid.uuid4())
            
            # Set correlation and causation IDs
            if not event.correlation_id:
                event.correlation_id = event.event_id
            
            # Store event
            self.event_store[event.event_id] = event
            
            # Add to appropriate stream
            await self._add_to_stream(event)
            
            # Add to processing queue
            event.status = EventStatus.PUBLISHED
            self.event_queue.append(event)
            
            # Publish to Kafka if enabled
            if self.kafka_producer:
                await self._publish_to_kafka(event)
            
            # Cache in Redis
            if self.redis_client:
                await self._cache_event(event)
            
            # Update metrics
            self.metrics["events_published"] += 1
            
            return {
                "success": True,
                "event_id": event.event_id,
                "correlation_id": event.correlation_id,
                "stream_id": f"{event.aggregate_type}_{event.aggregate_id}",
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Event publication failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }

    async def _add_to_stream(self, event: Event) -> None:
        """🗄️ **DBA**: Add event to event stream for sourcing."""
        stream_id = f"{event.aggregate_type}_{event.aggregate_id}"
        
        if stream_id not in self.event_streams:
            self.event_streams[stream_id] = EventStream(
                stream_id=stream_id,
                stream_name=f"{event.aggregate_type} Stream",
                aggregate_type=event.aggregate_type
            )
        
        stream = self.event_streams[stream_id]
        stream.events.append(event)
        stream.version += 1
        stream.last_updated = datetime.now()

    async def _publish_to_kafka(self, event: Event) -> None:
        """Publish event to Kafka topic."""
        try:
            topic = f"events.{event.aggregate_type}.{event.event_name}"
            key = event.aggregate_id
            
            event_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "aggregate_id": event.aggregate_id,
                "aggregate_type": event.aggregate_type,
                "event_name": event.event_name,
                "event_data": event.event_data,
                "metadata": event.metadata,
                "timestamp": event.timestamp.isoformat(),
                "correlation_id": event.correlation_id,
                "version": event.version
            }
            
            self.kafka_producer.send(topic, key=key, value=event_data)
            self.kafka_producer.flush()
            
        except Exception as e:
            logger.error(f"Kafka publication failed: {e}")

    async def _cache_event(self, event: Event) -> None:
        """Cache event in Redis for quick access."""
        try:
            cache_key = f"event:{event.event_id}"
            event_data = asdict(event)
            event_data["timestamp"] = event.timestamp.isoformat()
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.redis_client.setex,
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(event_data, default=str)
            )
        except Exception as e:
            logger.error(f"Event caching failed: {e}")

    async def start_processing(self) -> None:
        """
        ⚙️ **DEVOPS**: Start event processing workers.
        """
        if self.running:
            return
        
        self.running = True
        worker_count = self.config.get("worker_count", 4)
        
        # Start processing workers
        for i in range(worker_count):
            worker = threading.Thread(
                target=self._process_events_worker,
                name=f"EventWorker-{i}",
                daemon=True
            )
            worker.start()
            self.processing_threads.append(worker)
        
        logger.info(f"Event processing started with {worker_count} workers")

    def _process_events_worker(self) -> None:
        """Event processing worker thread."""
        while self.running:
            try:
                if self.event_queue:
                    event = self.event_queue.popleft()
                    asyncio.run(self._process_event(event))
                else:
                    time.sleep(0.1)  # Brief pause when no events
            except Exception as e:
                logger.error(f"Event worker error: {e}")
                time.sleep(1)

    async def _process_event(self, event: Event) -> None:
        """
        🤖 **LEAD DEV IA**: Process individual event with intelligent routing.
        
        Args:
            event: Event to process
        """
        start_time = time.time()
        event.status = EventStatus.PROCESSING
        
        try:
            # Find matching handlers
            matching_handlers = await self._find_matching_handlers(event)
            
            if not matching_handlers:
                logger.warning(f"No handlers found for event {event.event_id}")
                event.status = EventStatus.PROCESSED
                return
            
            # Process with each handler
            results = []
            for handler in matching_handlers:
                result = await self._execute_handler(handler, event)
                results.append(result)
            
            # Check if all handlers succeeded
            all_succeeded = all(result["success"] for result in results)
            
            if all_succeeded:
                event.status = EventStatus.PROCESSED
                self.metrics["events_processed"] += 1
            else:
                await self._handle_processing_failure(event, results)
            
            # Update processing time metric
            processing_time = time.time() - start_time
            self.metrics["average_processing_time"] = (
                self.metrics["average_processing_time"] * (self.metrics["events_processed"] - 1) + processing_time
            ) / self.metrics["events_processed"] if self.metrics["events_processed"] > 0 else processing_time
            
        except Exception as e:
            logger.error(f"Event processing failed for {event.event_id}: {e}")
            await self._handle_processing_failure(event, [{"success": False, "error": str(e)}])

    async def _find_matching_handlers(self, event: Event) -> List[EventHandler]:
        """Find handlers that match the event using pattern matching."""
        matching_handlers = []
        
        # Create event signature for matching
        event_signature = f"{event.aggregate_type}.{event.event_name}"
        
        for handler in self.event_handlers.values():
            # Check circuit breaker
            if not self._is_circuit_breaker_closed(handler.handler_id):
                continue
            
            # Check patterns
            for pattern in handler.event_patterns:
                compiled_pattern = self.compiled_patterns.get(pattern)
                if compiled_pattern and compiled_pattern.match(event_signature):
                    matching_handlers.append(handler)
                    break
        
        # Sort by priority
        matching_handlers.sort(key=lambda h: h.priority)
        return matching_handlers

    async def _execute_handler(self, handler: EventHandler, event: Event) -> Dict[str, Any]:
        """Execute event handler with circuit breaker protection."""
        handler_start_time = time.time()
        
        try:
            # Execute handler function
            if handler.async_processing:
                result = await handler.handler_function(event)
            else:
                result = handler.handler_function(event)
            
            # Record success
            self._record_handler_success(handler.handler_id)
            
            # Update handler metrics
            processing_time = time.time() - handler_start_time
            handler_metrics = self.metrics["handler_performance"][handler.handler_id]
            handler_metrics["processed"] += 1
            handler_metrics["avg_time"] = (
                handler_metrics["avg_time"] * (handler_metrics["processed"] - 1) + processing_time
            ) / handler_metrics["processed"]
            
            return {
                "success": True,
                "handler_id": handler.handler_id,
                "result": result,
                "processing_time": processing_time
            }
            
        except Exception as e:
            # Record failure
            self._record_handler_failure(handler.handler_id)
            
            # Update failure metrics
            self.metrics["handler_performance"][handler.handler_id]["failed"] += 1
            
            return {
                "success": False,
                "handler_id": handler.handler_id,
                "error": str(e),
                "processing_time": time.time() - handler_start_time
            }

    def _is_circuit_breaker_closed(self, handler_id: str) -> bool:
        """Check if circuit breaker allows processing."""
        breaker = self.circuit_breakers.get(handler_id)
        if not breaker:
            return True
        
        now = datetime.now()
        
        if breaker.state == "closed":
            return True
        elif breaker.state == "open":
            # Check if timeout has passed
            if (breaker.last_failure_time and 
                (now - breaker.last_failure_time).total_seconds() >= breaker.timeout):
                breaker.state = "half_open"
                return True
            return False
        elif breaker.state == "half_open":
            # Allow limited calls in half-open state
            return True
        
        return False

    def _record_handler_success(self, handler_id: str) -> None:
        """Record successful handler execution."""
        breaker = self.circuit_breakers.get(handler_id)
        if breaker:
            breaker.failure_count = 0
            breaker.last_success_time = datetime.now()
            if breaker.state == "half_open":
                breaker.state = "closed"

    def _record_handler_failure(self, handler_id: str) -> None:
        """Record failed handler execution."""
        breaker = self.circuit_breakers.get(handler_id)
        if breaker:
            breaker.failure_count += 1
            breaker.last_failure_time = datetime.now()
            
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = "open"
                self.metrics["circuit_breaker_opens"] += 1
                logger.warning(f"Circuit breaker opened for handler {handler_id}")

    async def _handle_processing_failure(self, event: Event, results: List[Dict[str, Any]]) -> None:
        """Handle event processing failure with retry logic."""
        event.retry_count += 1
        
        if event.retry_count < event.max_retries:
            event.status = EventStatus.RETRYING
            # Add delay before retry
            await asyncio.sleep(min(2 ** event.retry_count, 30))  # Exponential backoff
            self.event_queue.append(event)
            logger.info(f"Event {event.event_id} queued for retry {event.retry_count}/{event.max_retries}")
        else:
            event.status = EventStatus.DEAD_LETTER
            self.dead_letter_queue.append(event)
            self.metrics["events_failed"] += 1
            logger.error(f"Event {event.event_id} moved to dead letter queue")

    async def start_saga(self, saga: Saga) -> Dict[str, Any]:
        """
        🔄 Start saga orchestration for distributed transactions.
        
        Args:
            saga: Saga to start
            
        Returns:
            Saga start result
        """
        try:
            saga.status = SagaStatus.STARTED
            self.sagas[saga.saga_id] = saga
            
            # Execute first step
            await self._execute_saga_step(saga, 0)
            
            return {
                "success": True,
                "saga_id": saga.saga_id,
                "status": saga.status.value,
                "current_step": saga.current_step
            }
            
        except Exception as e:
            logger.error(f"Saga start failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _execute_saga_step(self, saga: Saga, step_index: int) -> None:
        """Execute a single saga step."""
        if step_index >= len(saga.steps):
            # Saga completed
            saga.status = SagaStatus.COMPLETED
            saga.completed_at = datetime.now()
            self.metrics["saga_completions"] += 1
            logger.info(f"Saga {saga.saga_id} completed successfully")
            return
        
        step = saga.steps[step_index]
        saga.current_step = step_index
        saga.status = SagaStatus.EXECUTING
        
        try:
            # Execute step command
            await self._execute_saga_command(saga, step)
            
            # Move to next step
            await self._execute_saga_step(saga, step_index + 1)
            
        except Exception as e:
            logger.error(f"Saga step {step.step_name} failed: {e}")
            await self._compensate_saga(saga, step_index)

    async def _execute_saga_command(self, saga: Saga, step: SagaStep) -> None:
        """Execute saga step command."""
        # Create command event
        command_event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.COMMAND,
            aggregate_id=saga.correlation_id,
            aggregate_type="saga",
            event_name=f"execute_{step.step_name}",
            event_data=step.command,
            correlation_id=saga.correlation_id,
            metadata={"saga_id": saga.saga_id, "step_id": step.step_id}
        )
        
        # Publish and wait for completion
        await self.publish_event(command_event)
        
        # In a real implementation, we would wait for a response event
        # For this example, we'll simulate success
        await asyncio.sleep(0.1)

    async def _compensate_saga(self, saga: Saga, failed_step_index: int) -> None:
        """Compensate saga by executing compensation commands."""
        saga.status = SagaStatus.COMPENSATING
        
        # Execute compensations in reverse order
        for i in range(failed_step_index - 1, -1, -1):
            step = saga.steps[i]
            if step.compensation_command:
                try:
                    await self._execute_compensation_command(saga, step)
                    saga.compensations.append(step.step_id)
                except Exception as e:
                    logger.error(f"Compensation failed for step {step.step_name}: {e}")
        
        saga.status = SagaStatus.FAILED
        saga.completed_at = datetime.now()
        self.metrics["saga_failures"] += 1
        logger.error(f"Saga {saga.saga_id} failed and compensated")

    async def _execute_compensation_command(self, saga: Saga, step: SagaStep) -> None:
        """Execute compensation command for a saga step."""
        compensation_event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.COMMAND,
            aggregate_id=saga.correlation_id,
            aggregate_type="saga",
            event_name=f"compensate_{step.step_name}",
            event_data=step.compensation_command,
            correlation_id=saga.correlation_id,
            metadata={"saga_id": saga.saga_id, "step_id": step.step_id, "compensation": True}
        )
        
        await self.publish_event(compensation_event)

    async def get_event_stream(self, aggregate_type: str, aggregate_id: str) -> Dict[str, Any]:
        """
        📊 Get event stream for aggregate.
        
        Args:
            aggregate_type: Type of aggregate
            aggregate_id: Aggregate identifier
            
        Returns:
            Event stream data
        """
        stream_id = f"{aggregate_type}_{aggregate_id}"
        stream = self.event_streams.get(stream_id)
        
        if not stream:
            return {
                "success": False,
                "error": "Stream not found"
            }
        
        return {
            "success": True,
            "stream_id": stream.stream_id,
            "stream_name": stream.stream_name,
            "aggregate_type": stream.aggregate_type,
            "version": stream.version,
            "event_count": len(stream.events),
            "created_at": stream.created_at.isoformat(),
            "last_updated": stream.last_updated.isoformat(),
            "events": [
                {
                    "event_id": event.event_id,
                    "event_name": event.event_name,
                    "timestamp": event.timestamp.isoformat(),
                    "version": event.version,
                    "status": event.status.value
                }
                for event in stream.events
            ]
        }

    async def replay_events(self, stream_id: str, from_version: int = 0) -> Dict[str, Any]:
        """
        🔄 Replay events from a stream for event sourcing.
        
        Args:
            stream_id: Stream identifier
            from_version: Starting version for replay
            
        Returns:
            Replay result
        """
        stream = self.event_streams.get(stream_id)
        if not stream:
            return {
                "success": False,
                "error": "Stream not found"
            }
        
        # Get events from specified version
        replay_events = [
            event for event in stream.events
            if event.version >= from_version
        ]
        
        replayed_count = 0
        for event in replay_events:
            # Republish event for replay
            replay_event = Event(
                event_id=str(uuid.uuid4()),
                event_type=EventType.DOMAIN_EVENT,
                aggregate_id=event.aggregate_id,
                aggregate_type=event.aggregate_type,
                event_name=f"replay_{event.event_name}",
                event_data=event.event_data,
                metadata={**event.metadata, "replay": True, "original_event_id": event.event_id},
                correlation_id=event.correlation_id
            )
            
            await self.publish_event(replay_event)
            replayed_count += 1
        
        return {
            "success": True,
            "stream_id": stream_id,
            "replayed_events": replayed_count,
            "from_version": from_version,
            "to_version": stream.version
        }

    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        📊 Get comprehensive processing statistics.
        
        Returns:
            Processing statistics and metrics
        """
        total_events = self.metrics["events_processed"] + self.metrics["events_failed"]
        success_rate = (
            self.metrics["events_processed"] / total_events if total_events > 0 else 0.0
        )
        
        return {
            "events_published": self.metrics["events_published"],
            "events_processed": self.metrics["events_processed"],
            "events_failed": self.metrics["events_failed"],
            "success_rate": success_rate,
            "average_processing_time": self.metrics["average_processing_time"],
            "queue_size": len(self.event_queue),
            "dead_letter_queue_size": len(self.dead_letter_queue),
            "active_streams": len(self.event_streams),
            "registered_handlers": len(self.event_handlers),
            "active_sagas": len([s for s in self.sagas.values() if s.status in [SagaStatus.STARTED, SagaStatus.EXECUTING]]),
            "saga_completions": self.metrics["saga_completions"],
            "saga_failures": self.metrics["saga_failures"],
            "circuit_breaker_opens": self.metrics["circuit_breaker_opens"],
            "handler_performance": dict(self.metrics["handler_performance"]),
            "circuit_breaker_states": {
                cb_id: cb.state for cb_id, cb in self.circuit_breakers.items()
            }
        }

    async def stop_processing(self) -> None:
        """Stop event processing workers."""
        self.running = False
        
        # Wait for workers to finish
        for worker in self.processing_threads:
            worker.join(timeout=5)
        
        self.processing_threads.clear()
        logger.info("Event processing stopped")

    async def health_check(self) -> Dict[str, Any]:
        """
        🏥 Perform comprehensive health check.
        
        Returns:
            Health check results
        """
        start_time = time.time()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "event_processing": "healthy" if self.running else "stopped",
                "kafka_producer": "healthy" if self.kafka_producer else "disabled",
                "redis_cache": "healthy" if self.redis_client else "disabled",
                "event_store": "healthy",
                "saga_orchestration": "healthy"
            },
            "metrics": await self.get_processing_stats(),
            "response_time": time.time() - start_time
        }
        
        # Check for concerning conditions
        if len(self.dead_letter_queue) > 100:
            health_status["status"] = "warning"
            health_status["warnings"] = ["High dead letter queue size"]
        
        open_circuit_breakers = [
            cb_id for cb_id, cb in self.circuit_breakers.items() if cb.state == "open"
        ]
        if open_circuit_breakers:
            health_status["status"] = "degraded"
            health_status["open_circuit_breakers"] = open_circuit_breakers
        
        return health_status

# Example event handlers
async def user_created_handler(event: Event) -> Dict[str, Any]:
    """Example handler for user created events."""
    logger.info(f"Processing user created event: {event.event_id}")
    
    # Simulate processing
    await asyncio.sleep(0.1)
    
    return {
        "handler": "user_created_handler",
        "processed_user": event.event_data.get("user_id"),
        "actions_taken": ["send_welcome_email", "create_profile"]
    }

async def order_placed_handler(event: Event) -> Dict[str, Any]:
    """Example handler for order placed events."""
    logger.info(f"Processing order placed event: {event.event_id}")
    
    # Simulate processing
    await asyncio.sleep(0.2)
    
    return {
        "handler": "order_placed_handler",
        "processed_order": event.event_data.get("order_id"),
        "actions_taken": ["reserve_inventory", "calculate_shipping"]
    }

def sync_payment_handler(event: Event) -> Dict[str, Any]:
    """Example synchronous handler for payment events."""
    logger.info(f"Processing payment event: {event.event_id}")
    
    # Simulate processing
    time.sleep(0.1)
    
    return {
        "handler": "payment_handler",
        "processed_payment": event.event_data.get("payment_id"),
        "actions_taken": ["validate_payment", "update_balance"]
    }

# Example usage and testing
async def main():
    """Example usage of Event Processing Engine."""
    
    # Initialize engine
    engine = EventProcessingEngine({
        "worker_count": 2,
        "redis_host": "localhost",
        "kafka": {"enabled": False}
    })
    
    # Register event handlers
    user_handler = EventHandler(
        handler_id="user_handler",
        handler_name="User Event Handler",
        event_patterns=["user\\..*"],
        handler_function=user_created_handler,
        priority=10
    )
    
    order_handler = EventHandler(
        handler_id="order_handler",
        handler_name="Order Event Handler",
        event_patterns=["order\\..*"],
        handler_function=order_placed_handler,
        priority=20
    )
    
    payment_handler = EventHandler(
        handler_id="payment_handler",
        handler_name="Payment Event Handler",
        event_patterns=["payment\\..*"],
        handler_function=sync_payment_handler,
        priority=5,
        async_processing=False
    )
    
    engine.register_handler(user_handler)
    engine.register_handler(order_handler)
    engine.register_handler(payment_handler)
    
    # Start processing
    await engine.start_processing()
    
    # Publish sample events
    events = [
        Event(
            event_id="evt_001",
            event_type=EventType.DOMAIN_EVENT,
            aggregate_id="user_123",
            aggregate_type="user",
            event_name="created",
            event_data={"user_id": "user_123", "email": "test@example.com"}
        ),
        Event(
            event_id="evt_002",
            event_type=EventType.DOMAIN_EVENT,
            aggregate_id="order_456",
            aggregate_type="order",
            event_name="placed",
            event_data={"order_id": "order_456", "user_id": "user_123", "amount": 99.99}
        ),
        Event(
            event_id="evt_003",
            event_type=EventType.DOMAIN_EVENT,
            aggregate_id="payment_789",
            aggregate_type="payment",
            event_name="processed",
            event_data={"payment_id": "payment_789", "order_id": "order_456", "amount": 99.99}
        )
    ]
    
    # Publish events
    for event in events:
        result = await engine.publish_event(event)
        print(f"Event {event.event_id} published: {result}")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Test saga orchestration
    saga = Saga(
        saga_id="saga_001",
        saga_type="order_fulfillment",
        correlation_id="order_456",
        steps=[
            SagaStep(
                step_id="reserve_inventory",
                step_name="reserve_inventory",
                command={"action": "reserve", "items": ["item1", "item2"]},
                compensation_command={"action": "release", "items": ["item1", "item2"]}
            ),
            SagaStep(
                step_id="process_payment",
                step_name="process_payment",
                command={"action": "charge", "amount": 99.99},
                compensation_command={"action": "refund", "amount": 99.99}
            ),
            SagaStep(
                step_id="ship_order",
                step_name="ship_order",
                command={"action": "ship", "order_id": "order_456"}
            )
        ]
    )
    
    saga_result = await engine.start_saga(saga)
    print(f"Saga started: {saga_result}")
    
    # Get processing stats
    stats = await engine.get_processing_stats()
    print(f"Processing Statistics: {stats}")
    
    # Test event stream retrieval
    stream_result = await engine.get_event_stream("user", "user_123")
    print(f"User Stream: {stream_result}")
    
    # Health check
    health = await engine.health_check()
    print(f"Health Check: {health}")
    
    # Stop processing
    await engine.stop_processing()

if __name__ == "__main__":
    asyncio.run(main())