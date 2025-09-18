"""
Event Bus Template for Enterprise Microservices
==============================================

Production-ready event-driven architecture with:
- Event sourcing capabilities
- Saga pattern support
- Event replay and versioning
- Distributed transaction coordination
- Real-time event streaming
- Event store integration

Author: Fahed Mlaiel (mlaiel@live.de)
Microservices Architect & Event-Driven Expert
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Callable, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

import redis.asyncio as redis
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types in creator economy"""
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    COLLABORATION_STARTED = "collaboration.started"
    COLLABORATION_COMPLETED = "collaboration.completed"
    REVENUE_GENERATED = "revenue.generated"
    USER_REGISTERED = "user.registered"
    CREATOR_VERIFIED = "creator.verified"
    DISTRIBUTION_COMPLETED = "distribution.completed"
    AI_PROCESSING_COMPLETED = "ai.processing.completed"
    PROTECTION_APPLIED = "protection.applied"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class DomainEvent:
    """Domain event structure for event sourcing"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    aggregate_id: str = ""
    aggregate_type: str = ""
    version: int = 1
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    ttl: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'aggregate_type': self.aggregate_type,
            'version': self.version,
            'payload': self.payload,
            'metadata': self.metadata,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'ttl': self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from dictionary"""
        return cls(
            id=data['id'],
            event_type=data['event_type'],
            aggregate_id=data['aggregate_id'],
            aggregate_type=data['aggregate_type'],
            version=data['version'],
            payload=data['payload'],
            metadata=data['metadata'],
            correlation_id=data.get('correlation_id'),
            causation_id=data.get('causation_id'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            priority=EventPriority(data['priority']),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            ttl=data.get('ttl')
        )


class EventHandler:
    """Base class for event handlers"""
    
    def __init__(self, event_types: List[str]):
        self.event_types = event_types
    
    async def handle(self, event: DomainEvent) -> bool:
        """Handle event - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def can_handle(self, event: DomainEvent) -> bool:
        """Check if handler can process event"""
        return event.event_type in self.event_types


class EventBusConfig(BaseModel):
    """Event bus configuration"""
    redis_url: str = Field(..., description="Redis connection URL")
    event_stream: str = Field(default="events", description="Main event stream")
    event_store_stream: str = Field(default="event_store", description="Event store stream")
    consumer_group: str = Field(..., description="Consumer group name")
    consumer_name: str = Field(..., description="Consumer name")
    batch_size: int = Field(default=10, description="Event batch size")
    block_timeout: int = Field(default=1000, description="Block timeout in ms")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: int = Field(default=5, description="Retry delay in seconds")
    enable_event_store: bool = Field(default=True, description="Enable event sourcing")
    enable_snapshots: bool = Field(default=True, description="Enable aggregate snapshots")
    snapshot_frequency: int = Field(default=10, description="Snapshot frequency")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")


class EventBusTemplate(BaseMicroservice):
    """
    Enterprise Event Bus Template
    
    Comprehensive event-driven architecture with:
    - Event sourcing and CQRS patterns
    - Saga orchestration support
    - Event replay capabilities
    - Distributed transaction coordination
    - Real-time event streaming
    - Aggregate state management
    """
    
    def __init__(self, config: EventBusConfig):
        super().__init__()
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=redis.RedisError
        )
        
        # Event handlers registry
        self.event_handlers: Dict[str, List[EventHandler]] = {}
        self.saga_handlers: Dict[str, Callable] = {}
        self.middleware_stack: List[Callable] = []
        
        # Event store for event sourcing
        self.aggregate_snapshots: Dict[str, Dict[str, Any]] = {}
        
        # Metrics
        if config.monitoring_enabled:
            self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        self.events_published = Counter(
            'event_bus_events_published_total',
            'Total events published',
            ['event_type', 'aggregate_type', 'priority']
        )
        
        self.events_processed = Counter(
            'event_bus_events_processed_total',
            'Total events processed',
            ['event_type', 'handler_type', 'status']
        )
        
        self.event_processing_time = Histogram(
            'event_bus_processing_duration_seconds',
            'Event processing duration',
            ['event_type', 'handler_type']
        )
        
        self.event_bus_size = Gauge(
            'event_bus_stream_size',
            'Current event stream size',
            ['stream_name']
        )
        
        self.active_sagas = Gauge(
            'event_bus_active_sagas',
            'Number of active sagas',
            ['saga_type']
        )
    
    async def start(self):
        """Start event bus service"""
        await super().start()
        
        # Initialize Redis connection
        self.redis_client = redis.from_url(
            self.config.redis_url,
            decode_responses=True,
            retry_on_timeout=True,
            socket_keepalive=True
        )
        
        # Create consumer groups
        for stream in [self.config.event_stream, self.config.event_store_stream]:
            try:
                await self.redis_client.xgroup_create(
                    stream,
                    self.config.consumer_group,
                    id='0',
                    mkstream=True
                )
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
        
        logger.info(f"Event bus started - Stream: {self.config.event_stream}")
    
    async def stop(self):
        """Stop event bus service"""
        if self.redis_client:
            await self.redis_client.close()
        await super().stop()
        logger.info("Event bus stopped")
    
    def register_handler(self, event_type: str, handler: EventHandler):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")
    
    def register_saga_handler(self, saga_type: str, handler: Callable):
        """Register saga handler"""
        self.saga_handlers[saga_type] = handler
        logger.info(f"Registered saga handler: {saga_type}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to event processing pipeline"""
        self.middleware_stack.append(middleware)
    
    @CircuitBreaker.circuit_breaker
    async def publish_event(
        self,
        event_type: str,
        aggregate_id: str,
        aggregate_type: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        version: int = 1
    ) -> str:
        """
        Publish domain event
        
        Args:
            event_type: Type of event
            aggregate_id: ID of aggregate
            aggregate_type: Type of aggregate
            payload: Event payload
            metadata: Event metadata
            correlation_id: Correlation ID for tracing
            causation_id: Causation ID for event chain
            priority: Event priority
            version: Event version
            
        Returns:
            Event ID
        """
        event = DomainEvent(
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            payload=payload,
            metadata=metadata or {},
            correlation_id=correlation_id,
            causation_id=causation_id,
            priority=priority,
            version=version
        )
        
        # Add to event stream
        await self._add_to_stream(self.config.event_stream, event)
        
        # Add to event store if enabled
        if self.config.enable_event_store:
            await self._add_to_event_store(event)
        
        # Update metrics
        if self.config.monitoring_enabled:
            self.events_published.labels(
                event_type=event_type,
                aggregate_type=aggregate_type,
                priority=priority.name.lower()
            ).inc()
        
        logger.debug(f"Published event: {event.id} ({event_type})")
        return event.id
    
    async def _add_to_stream(self, stream_name: str, event: DomainEvent):
        """Add event to Redis stream"""
        event_data = event.to_dict()
        event_data['payload'] = json.dumps(event_data['payload'])
        event_data['metadata'] = json.dumps(event_data['metadata'])
        
        # Create priority-based stream ID
        priority_prefix = f"{10 - event.priority.value:02d}"
        stream_id = f"{priority_prefix}-{int(time.time() * 1000)}-{hash(event.id) % 1000}"
        
        await self.redis_client.xadd(stream_name, event_data, id=stream_id)
    
    async def _add_to_event_store(self, event: DomainEvent):
        """Add event to event store for event sourcing"""
        store_key = f"aggregate:{event.aggregate_type}:{event.aggregate_id}"
        
        # Add to aggregate's event stream
        await self.redis_client.xadd(store_key, event.to_dict())
        
        # Create snapshot if needed
        if self.config.enable_snapshots:
            await self._create_snapshot_if_needed(event)
    
    async def _create_snapshot_if_needed(self, event: DomainEvent):
        """Create aggregate snapshot if frequency reached"""
        store_key = f"aggregate:{event.aggregate_type}:{event.aggregate_id}"
        stream_length = await self.redis_client.xlen(store_key)
        
        if stream_length % self.config.snapshot_frequency == 0:
            # Replay events to create current state
            current_state = await self.replay_events(
                event.aggregate_type,
                event.aggregate_id
            )
            
            # Save snapshot
            snapshot_key = f"snapshot:{event.aggregate_type}:{event.aggregate_id}"
            await self.redis_client.hset(snapshot_key, mapping={
                'version': event.version,
                'timestamp': datetime.utcnow().isoformat(),
                'state': json.dumps(current_state)
            })
            
            logger.debug(f"Created snapshot for aggregate {event.aggregate_id}")
    
    async def consume_events(self, count: int = None) -> List[DomainEvent]:
        """
        Consume events from event stream
        
        Args:
            count: Number of events to consume
            
        Returns:
            List of consumed events
        """
        batch_size = count or self.config.batch_size
        
        try:
            # Read from event stream
            messages = await self.redis_client.xreadgroup(
                self.config.consumer_group,
                self.config.consumer_name,
                {self.config.event_stream: '>'},
                count=batch_size,
                block=self.config.block_timeout
            )
            
            events = []
            
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    try:
                        # Deserialize event
                        fields['payload'] = json.loads(fields['payload'])
                        fields['metadata'] = json.loads(fields['metadata'])
                        
                        event = DomainEvent.from_dict(fields)
                        events.append(event)
                        
                        # Acknowledge event
                        await self.redis_client.xack(
                            self.config.event_stream,
                            self.config.consumer_group,
                            msg_id
                        )
                        
                    except Exception as e:
                        logger.error(f"Error processing event {msg_id}: {e}")
                        continue
            
            return events
            
        except redis.RedisError as e:
            logger.error(f"Redis error consuming events: {e}")
            return []
    
    async def process_event(self, event: DomainEvent) -> bool:
        """
        Process individual event
        
        Args:
            event: Event to process
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        success = True
        
        try:
            # Apply middleware
            for middleware in self.middleware_stack:
                event = await middleware(event)
                if event is None:
                    return True  # Event filtered out
            
            # Get handlers for event type
            handlers = self.event_handlers.get(event.event_type, [])
            
            # Process with all handlers
            for handler in handlers:
                try:
                    if await handler.can_handle(event):
                        handler_start = time.time()
                        result = await handler.handle(event)
                        
                        # Update metrics
                        if self.config.monitoring_enabled:
                            processing_time = time.time() - handler_start
                            self.event_processing_time.labels(
                                event_type=event.event_type,
                                handler_type=handler.__class__.__name__
                            ).observe(processing_time)
                            
                            self.events_processed.labels(
                                event_type=event.event_type,
                                handler_type=handler.__class__.__name__,
                                status='success' if result else 'error'
                            ).inc()
                        
                        if not result:
                            success = False
                            
                except Exception as e:
                    logger.error(f"Handler {handler.__class__.__name__} failed for event {event.id}: {e}")
                    success = False
                    
                    if self.config.monitoring_enabled:
                        self.events_processed.labels(
                            event_type=event.event_type,
                            handler_type=handler.__class__.__name__,
                            status='error'
                        ).inc()
            
            # Check for saga triggers
            await self._process_saga_triggers(event)
            
            logger.debug(f"Processed event: {event.id} ({event.event_type})")
            return success
            
        except Exception as e:
            logger.error(f"Error processing event {event.id}: {e}")
            return False
    
    async def _process_saga_triggers(self, event: DomainEvent):
        """Process saga triggers for event"""
        for saga_type, handler in self.saga_handlers.items():
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Saga {saga_type} failed for event {event.id}: {e}")
    
    async def replay_events(
        self,
        aggregate_type: str,
        aggregate_id: str,
        from_version: int = 0,
        to_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Replay events for aggregate
        
        Args:
            aggregate_type: Type of aggregate
            aggregate_id: ID of aggregate
            from_version: Start version
            to_version: End version
            
        Returns:
            Replayed aggregate state
        """
        store_key = f"aggregate:{aggregate_type}:{aggregate_id}"
        
        # Get events from store
        events = await self.redis_client.xrange(store_key, min='-', max='+')
        
        # Filter by version if specified
        filtered_events = []
        for event_id, fields in events:
            version = int(fields.get('version', 0))
            if version >= from_version and (to_version is None or version <= to_version):
                filtered_events.append(DomainEvent.from_dict(fields))
        
        # Sort by version
        filtered_events.sort(key=lambda e: e.version)
        
        # Replay events to build state
        state = {}
        for event in filtered_events:
            state = await self._apply_event_to_state(state, event)
        
        return state
    
    async def _apply_event_to_state(self, state: Dict[str, Any], event: DomainEvent) -> Dict[str, Any]:
        """Apply event to aggregate state"""
        # This would be implemented based on specific aggregate logic
        # For now, just merge the payload
        if 'events' not in state:
            state['events'] = []
        
        state['events'].append({
            'type': event.event_type,
            'version': event.version,
            'timestamp': event.timestamp.isoformat(),
            'payload': event.payload
        })
        
        # Update aggregate metadata
        state.update({
            'last_event_id': event.id,
            'version': event.version,
            'updated_at': event.timestamp.isoformat()
        })
        
        return state
    
    async def get_aggregate_state(
        self,
        aggregate_type: str,
        aggregate_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get current aggregate state"""
        # Try to get from snapshot first
        if self.config.enable_snapshots:
            snapshot_key = f"snapshot:{aggregate_type}:{aggregate_id}"
            snapshot = await self.redis_client.hgetall(snapshot_key)
            
            if snapshot:
                state = json.loads(snapshot['state'])
                snapshot_version = int(snapshot['version'])
                
                # Get events since snapshot
                recent_state = await self.replay_events(
                    aggregate_type,
                    aggregate_id,
                    from_version=snapshot_version + 1
                )
                
                # Merge with snapshot
                state.update(recent_state)
                return state
        
        # Replay all events
        return await self.replay_events(aggregate_type, aggregate_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for event bus"""
        try:
            # Test Redis connection
            await self.redis_client.ping()
            
            # Get stream info
            stream_info = await self.redis_client.xinfo_stream(self.config.event_stream)
            
            return {
                'status': 'healthy',
                'redis_connected': True,
                'event_stream_length': stream_info['length'],
                'circuit_breaker_state': self.circuit_breaker.state.name,
                'registered_handlers': len(self.event_handlers),
                'registered_sagas': len(self.saga_handlers)
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'redis_connected': False,
                'error': str(e),
                'circuit_breaker_state': self.circuit_breaker.state.name
            }


# Example event handlers for Creator Economy
class ContentProcessingEventHandler(EventHandler):
    """Handler for content processing events"""
    
    def __init__(self):
        super().__init__([
            EventType.CONTENT_UPLOADED.value,
            EventType.AI_PROCESSING_COMPLETED.value
        ])
    
    async def handle(self, event: DomainEvent) -> bool:
        """Handle content processing events"""
        if event.event_type == EventType.CONTENT_UPLOADED.value:
            return await self._handle_content_upload(event)
        elif event.event_type == EventType.AI_PROCESSING_COMPLETED.value:
            return await self._handle_ai_processing_completed(event)
        return False
    
    async def _handle_content_upload(self, event: DomainEvent) -> bool:
        """Handle content upload event"""
        content_id = event.payload.get('content_id')
        content_type = event.payload.get('content_type')
        
        logger.info(f"Processing uploaded content: {content_id} ({content_type})")
        
        # Trigger AI processing
        # This would publish another event to start AI processing
        return True
    
    async def _handle_ai_processing_completed(self, event: DomainEvent) -> bool:
        """Handle AI processing completion"""
        content_id = event.payload.get('content_id')
        processing_results = event.payload.get('results')
        
        logger.info(f"AI processing completed for content: {content_id}")
        
        # Apply protection and prepare for distribution
        return True


class CollaborationEventHandler(EventHandler):
    """Handler for collaboration events"""
    
    def __init__(self):
        super().__init__([
            EventType.COLLABORATION_STARTED.value,
            EventType.COLLABORATION_COMPLETED.value
        ])
    
    async def handle(self, event: DomainEvent) -> bool:
        """Handle collaboration events"""
        if event.event_type == EventType.COLLABORATION_STARTED.value:
            return await self._handle_collaboration_started(event)
        elif event.event_type == EventType.COLLABORATION_COMPLETED.value:
            return await self._handle_collaboration_completed(event)
        return False
    
    async def _handle_collaboration_started(self, event: DomainEvent) -> bool:
        """Handle collaboration start"""
        collaboration_id = event.payload.get('collaboration_id')
        participants = event.payload.get('participants')
        
        logger.info(f"Collaboration started: {collaboration_id} with {len(participants)} participants")
        
        # Setup collaboration workspace
        # Send notifications to participants
        return True
    
    async def _handle_collaboration_completed(self, event: DomainEvent) -> bool:
        """Handle collaboration completion"""
        collaboration_id = event.payload.get('collaboration_id')
        final_content = event.payload.get('final_content')
        
        logger.info(f"Collaboration completed: {collaboration_id}")
        
        # Process final content
        # Distribute revenue
        # Send completion notifications
        return True


# Example Saga for Content Monetization
async def content_monetization_saga(event: DomainEvent):
    """Saga for content monetization workflow"""
    if event.event_type == EventType.CONTENT_PROCESSED.value:
        content_id = event.payload.get('content_id')
        creator_id = event.payload.get('creator_id')
        
        logger.info(f"Starting monetization saga for content: {content_id}")
        
        # Step 1: Apply protection
        # Step 2: Setup distribution channels
        # Step 3: Configure revenue sharing
        # Step 4: Enable monetization
        
        # This would publish events to trigger each step
        pass