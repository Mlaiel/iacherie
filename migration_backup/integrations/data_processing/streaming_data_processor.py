"""Streaming Data Processor - Real-time Data Processing
====================================================

High-throughput streaming analytics for creator content with
Apache Kafka integration, windowed analytics, and real-time processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics

try:
    import aiokafka
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    aiokafka = None

import redis.asyncio as redis
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class StreamType(Enum):
    """Stream data types."""
    USER_ACTIVITY = "user_activity"
    CONTENT_INTERACTION = "content_interaction"
    PLATFORM_EVENT = "platform_event"
    MONETIZATION_EVENT = "monetization_event"
    SECURITY_EVENT = "security_event"
    SYSTEM_METRIC = "system_metric"


class WindowType(Enum):
    """Stream window types."""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    COUNT = "count"


class AggregationType(Enum):
    """Stream aggregation types."""
    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    DISTINCT_COUNT = "distinct_count"
    PERCENTILE = "percentile"
    STANDARD_DEVIATION = "std_dev"


@dataclass
class StreamEvent:
    """Stream event data structure."""
    id: str
    stream_type: StreamType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    platform: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamWindow:
    """Stream processing window configuration."""
    id: str
    name: str
    window_type: WindowType
    size: Union[int, timedelta]  # seconds for time-based, count for count-based
    slide: Optional[Union[int, timedelta]] = None  # for sliding windows
    session_timeout: Optional[timedelta] = None  # for session windows
    key_field: Optional[str] = None  # field to group by
    enabled: bool = True


@dataclass
class StreamAggregation:
    """Stream aggregation configuration."""
    id: str
    name: str
    window_id: str
    aggregation_type: AggregationType
    field: str  # field to aggregate
    conditions: List[str] = field(default_factory=list)  # filter conditions
    output_topic: Optional[str] = None
    enabled: bool = True


@dataclass
class StreamProcessor:
    """Stream processor configuration."""
    id: str
    name: str
    input_topics: List[str]
    output_topics: List[str]
    processor_function: Callable
    windows: List[StreamWindow] = field(default_factory=list)
    aggregations: List[StreamAggregation] = field(default_factory=list)
    parallelism: int = 1
    enabled: bool = True


@dataclass
class WindowState:
    """State of a processing window."""
    window_id: str
    key: Optional[str]
    start_time: datetime
    end_time: datetime
    events: List[StreamEvent] = field(default_factory=list)
    aggregation_results: Dict[str, Any] = field(default_factory=dict)
    event_count: int = 0
    last_update: datetime = field(default_factory=datetime.utcnow)


Base = declarative_base()


class StreamProcessingMetrics(Base):
    """Stream processing metrics model."""
    __tablename__ = 'stream_metrics'
    
    id = sa.Column(sa.String(36), primary_key=True)
    processor_id = sa.Column(sa.String(100), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    events_processed = sa.Column(sa.BigInteger, default=0)
    events_per_second = sa.Column(sa.Float, default=0.0)
    processing_latency = sa.Column(sa.Float, default=0.0)
    error_count = sa.Column(sa.Integer, default=0)
    window_count = sa.Column(sa.Integer, default=0)
    meta_data = sa.Column(sa.Text)


class StreamingDataProcessor:
    """High-performance streaming data processor."""
    
    def __init__(
        self,
        kafka_config: Optional[Dict[str, Any]] = None,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Kafka configuration
        self.kafka_config = kafka_config or {}
        self.kafka_available = KAFKA_AVAILABLE and kafka_config
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup for state management
        self.redis_url = redis_url
        self.redis_client = None
        
        # Stream processors
        self.processors: Dict[str, StreamProcessor] = {}
        self.active_consumers: Dict[str, Any] = {}
        self.active_producers: Dict[str, Any] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
        # Window state management
        self.active_windows: Dict[str, Dict[str, WindowState]] = defaultdict(dict)
        self.window_timers: Dict[str, asyncio.Task] = {}
        
        # Performance metrics
        self.metrics = {
            'total_events_processed': 0,
            'events_per_second': 0.0,
            'average_processing_latency': 0.0,
            'active_windows': 0,
            'error_count': 0
        }
        
        # Processing state
        self.is_running = False
        self.event_buffer: Dict[str, deque] = defaultdict(deque)
        self.latency_measurements: deque = deque(maxlen=1000)
        
        # Built-in stream processors
        self._setup_built_in_processors()
    
    async def initialize(self):
        """Initialize the streaming processor."""
        # Initialize database if configured
        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        # Initialize Kafka components if available
        if self.kafka_available:
            await self._initialize_kafka()
        
        self.logger.info("Streaming data processor initialized")
    
    def _setup_built_in_processors(self):
        """Setup built-in stream processors."""
        # User activity processor
        user_activity_processor = StreamProcessor(
            id="user_activity_processor",
            name="User Activity Stream Processor",
            input_topics=["user_activity"],
            output_topics=["user_activity_aggregated"],
            processor_function=self._process_user_activity,
            windows=[
                StreamWindow(
                    id="user_activity_1min",
                    name="1-minute User Activity Window",
                    window_type=WindowType.TUMBLING,
                    size=timedelta(minutes=1),
                    key_field="user_id"
                ),
                StreamWindow(
                    id="user_activity_5min",
                    name="5-minute User Activity Window",
                    window_type=WindowType.SLIDING,
                    size=timedelta(minutes=5),
                    slide=timedelta(minutes=1),
                    key_field="user_id"
                )
            ],
            aggregations=[
                StreamAggregation(
                    id="user_activity_count",
                    name="User Activity Count",
                    window_id="user_activity_1min",
                    aggregation_type=AggregationType.COUNT,
                    field="event_id"
                ),
                StreamAggregation(
                    id="user_engagement_avg",
                    name="User Engagement Average",
                    window_id="user_activity_5min",
                    aggregation_type=AggregationType.AVG,
                    field="engagement_score"
                )
            ]
        )
        
        # Content interaction processor
        content_interaction_processor = StreamProcessor(
            id="content_interaction_processor",
            name="Content Interaction Stream Processor",
            input_topics=["content_interaction"],
            output_topics=["content_interaction_aggregated"],
            processor_function=self._process_content_interaction,
            windows=[
                StreamWindow(
                    id="content_interaction_10min",
                    name="10-minute Content Interaction Window",
                    window_type=WindowType.TUMBLING,
                    size=timedelta(minutes=10),
                    key_field="content_id"
                )
            ],
            aggregations=[
                StreamAggregation(
                    id="interaction_count",
                    name="Interaction Count",
                    window_id="content_interaction_10min",
                    aggregation_type=AggregationType.COUNT,
                    field="interaction_id"
                ),
                StreamAggregation(
                    id="unique_users",
                    name="Unique Users",
                    window_id="content_interaction_10min",
                    aggregation_type=AggregationType.DISTINCT_COUNT,
                    field="user_id"
                )
            ]
        )
        
        # Register built-in processors
        self.processors["user_activity_processor"] = user_activity_processor
        self.processors["content_interaction_processor"] = content_interaction_processor
    
    async def _initialize_kafka(self):
        """Initialize Kafka producers and consumers."""
        if not self.kafka_available:
            return
        
        # Get all unique topics from processors
        all_topics = set()
        for processor in self.processors.values():
            all_topics.update(processor.input_topics)
            all_topics.update(processor.output_topics)
        
        # Create consumers for input topics
        input_topics = set()
        for processor in self.processors.values():
            input_topics.update(processor.input_topics)
        
        if input_topics:
            consumer = AIOKafkaConsumer(
                *input_topics,
                bootstrap_servers=self.kafka_config.get('bootstrap_servers', 'localhost:9092'),
                group_id=self.kafka_config.get('group_id', 'streaming_processor'),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest'
            )
            self.active_consumers['main'] = consumer
        
        # Create producer for output topics
        producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_config.get('bootstrap_servers', 'localhost:9092'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.active_producers['main'] = producer
    
    def register_processor(self, processor: StreamProcessor):
        """Register a stream processor."""
        self.processors[processor.id] = processor
        self.logger.info(f"Registered stream processor: {processor.name}")
    
    async def start_processing(self):
        """Start stream processing."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start Kafka components if available
        if self.kafka_available:
            for consumer in self.active_consumers.values():
                await consumer.start()
            for producer in self.active_producers.values():
                await producer.start()
        
        # Start processing tasks for each processor
        for processor_id, processor in self.processors.items():
            if processor.enabled:
                task = asyncio.create_task(self._process_stream(processor))
                self.processing_tasks[processor_id] = task
        
        # Start metrics collection
        asyncio.create_task(self._collect_metrics())
        
        # Start window cleanup
        asyncio.create_task(self._cleanup_expired_windows())
        
        self.logger.info("Stream processing started")
    
    async def stop_processing(self):
        """Stop stream processing."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks.values():
            task.cancel()
        
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks.values(), return_exceptions=True)
        
        # Stop Kafka components
        if self.kafka_available:
            for consumer in self.active_consumers.values():
                await consumer.stop()
            for producer in self.active_producers.values():
                await producer.stop()
        
        # Cancel window timers
        for timer in self.window_timers.values():
            timer.cancel()
        
        self.logger.info("Stream processing stopped")
    
    async def _process_stream(self, processor: StreamProcessor):
        """Process stream for a specific processor."""
        try:
            if self.kafka_available:
                await self._process_kafka_stream(processor)
            else:
                await self._process_local_stream(processor)
        except Exception as e:
            self.logger.error(f"Stream processing error for {processor.id}: {e}")
            self.metrics['error_count'] += 1
    
    async def _process_kafka_stream(self, processor: StreamProcessor):
        """Process Kafka stream for a processor."""
        consumer = self.active_consumers.get('main')
        if not consumer:
            return
        
        async for message in consumer:
            if not self.is_running:
                break
            
            try:
                # Check if message topic is relevant for this processor
                if message.topic not in processor.input_topics:
                    continue
                
                # Create stream event
                event_data = message.value
                event = StreamEvent(
                    id=event_data.get('id', str(uuid.uuid4())),
                    stream_type=StreamType(event_data.get('stream_type', 'user_activity')),
                    timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.utcnow().isoformat())),
                    user_id=event_data.get('user_id'),
                    session_id=event_data.get('session_id'),
                    platform=event_data.get('platform'),
                    data=event_data.get('data', {}),
                    metadata=event_data.get('metadata', {})
                )
                
                # Process event
                await self._process_event(processor, event)
                
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                self.metrics['error_count'] += 1
    
    async def _process_local_stream(self, processor: StreamProcessor):
        """Process local event buffer for a processor."""
        while self.is_running:
            try:
                # Check event buffer for relevant topics
                events_to_process = []
                for topic in processor.input_topics:
                    if topic in self.event_buffer and self.event_buffer[topic]:
                        event_data = self.event_buffer[topic].popleft()
                        
                        event = StreamEvent(
                            id=event_data.get('id', str(uuid.uuid4())),
                            stream_type=StreamType(event_data.get('stream_type', 'user_activity')),
                            timestamp=datetime.fromisoformat(event_data.get('timestamp', datetime.utcnow().isoformat())),
                            user_id=event_data.get('user_id'),
                            session_id=event_data.get('session_id'),
                            platform=event_data.get('platform'),
                            data=event_data.get('data', {}),
                            metadata=event_data.get('metadata', {})
                        )
                        
                        events_to_process.append(event)
                
                # Process events
                for event in events_to_process:
                    await self._process_event(processor, event)
                
                # Sleep if no events to process
                if not events_to_process:
                    await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in local stream processing: {e}")
                self.metrics['error_count'] += 1
    
    async def _process_event(self, processor: StreamProcessor, event: StreamEvent):
        """Process individual event."""
        start_time = time.time()
        
        try:
            # Apply processor function
            processed_data = await processor.processor_function(event)
            
            # Add to windows
            await self._add_to_windows(processor, event)
            
            # Update metrics
            self.metrics['total_events_processed'] += 1
            processing_latency = time.time() - start_time
            self.latency_measurements.append(processing_latency)
            
            # Send to output topics if available
            if self.kafka_available and processor.output_topics:
                producer = self.active_producers.get('main')
                if producer and processed_data:
                    for topic in processor.output_topics:
                        await producer.send(topic, processed_data)
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.id}: {e}")
            self.metrics['error_count'] += 1
    
    async def _add_to_windows(self, processor: StreamProcessor, event: StreamEvent):
        """Add event to relevant windows."""
        for window in processor.windows:
            if not window.enabled:
                continue
            
            # Determine window key
            window_key = "default"
            if window.key_field and window.key_field in event.data:
                window_key = str(event.data[window.key_field])
            elif window.key_field == "user_id" and event.user_id:
                window_key = event.user_id
            elif window.key_field == "session_id" and event.session_id:
                window_key = event.session_id
            elif window.key_field == "platform" and event.platform:
                window_key = event.platform
            
            # Get or create window state
            window_state_key = f"{window.id}:{window_key}"
            
            if window.window_type == WindowType.TUMBLING:
                await self._add_to_tumbling_window(window, window_state_key, event)
            elif window.window_type == WindowType.SLIDING:
                await self._add_to_sliding_window(window, window_state_key, event)
            elif window.window_type == WindowType.SESSION:
                await self._add_to_session_window(window, window_state_key, event)
            elif window.window_type == WindowType.COUNT:
                await self._add_to_count_window(window, window_state_key, event)
    
    async def _add_to_tumbling_window(self, window: StreamWindow, window_key: str, event: StreamEvent):
        """Add event to tumbling window."""
        current_time = event.timestamp
        window_size = window.size
        
        # Calculate window boundaries
        if isinstance(window_size, timedelta):
            window_start = current_time.replace(
                second=0, microsecond=0
            ) - timedelta(
                minutes=current_time.minute % int(window_size.total_seconds() / 60)
            )
            window_end = window_start + window_size
        else:
            # Count-based window (simplified)
            window_start = current_time
            window_end = current_time + timedelta(hours=1)  # Default 1 hour for count windows
        
        # Check if event belongs to current window
        if current_time < window_start or current_time >= window_end:
            return
        
        # Get or create window state
        if window_key not in self.active_windows[window.id]:
            self.active_windows[window.id][window_key] = WindowState(
                window_id=window.id,
                key=window_key.split(':')[1] if ':' in window_key else None,
                start_time=window_start,
                end_time=window_end
            )
        
        window_state = self.active_windows[window.id][window_key]
        window_state.events.append(event)
        window_state.event_count += 1
        window_state.last_update = datetime.utcnow()
        
        # Schedule window closure if not already scheduled
        timer_key = f"{window.id}:{window_key}:{window_end.isoformat()}"
        if timer_key not in self.window_timers:
            delay = (window_end - datetime.utcnow()).total_seconds()
            if delay > 0:
                timer = asyncio.create_task(self._close_window_after_delay(window, window_key, delay))
                self.window_timers[timer_key] = timer
    
    async def _add_to_sliding_window(self, window: StreamWindow, window_key: str, event: StreamEvent):
        """Add event to sliding window."""
        # For sliding windows, we maintain multiple overlapping windows
        # This is a simplified implementation
        await self._add_to_tumbling_window(window, window_key, event)
    
    async def _add_to_session_window(self, window: StreamWindow, window_key: str, event: StreamEvent):
        """Add event to session window."""
        session_timeout = window.session_timeout or timedelta(minutes=30)
        current_time = event.timestamp
        
        # Get existing window or create new one
        if window_key not in self.active_windows[window.id]:
            self.active_windows[window.id][window_key] = WindowState(
                window_id=window.id,
                key=window_key.split(':')[1] if ':' in window_key else None,
                start_time=current_time,
                end_time=current_time + session_timeout
            )
        
        window_state = self.active_windows[window.id][window_key]
        
        # Check if event extends the session
        time_since_last = current_time - window_state.last_update
        if time_since_last <= session_timeout:
            # Extend session
            window_state.end_time = current_time + session_timeout
            window_state.events.append(event)
            window_state.event_count += 1
            window_state.last_update = current_time
        else:
            # Close current session and start new one
            await self._close_window(window, window_key)
            
            # Create new session
            self.active_windows[window.id][window_key] = WindowState(
                window_id=window.id,
                key=window_key.split(':')[1] if ':' in window_key else None,
                start_time=current_time,
                end_time=current_time + session_timeout
            )
            window_state = self.active_windows[window.id][window_key]
            window_state.events.append(event)
            window_state.event_count += 1
            window_state.last_update = current_time
    
    async def _add_to_count_window(self, window: StreamWindow, window_key: str, event: StreamEvent):
        """Add event to count-based window."""
        max_count = window.size if isinstance(window.size, int) else 100
        
        # Get or create window state
        if window_key not in self.active_windows[window.id]:
            self.active_windows[window.id][window_key] = WindowState(
                window_id=window.id,
                key=window_key.split(':')[1] if ':' in window_key else None,
                start_time=event.timestamp,
                end_time=event.timestamp + timedelta(hours=1)  # Default end time
            )
        
        window_state = self.active_windows[window.id][window_key]
        window_state.events.append(event)
        window_state.event_count += 1
        window_state.last_update = datetime.utcnow()
        
        # Close window if count reached
        if window_state.event_count >= max_count:
            await self._close_window(window, window_key)
    
    async def _close_window_after_delay(self, window: StreamWindow, window_key: str, delay: float):
        """Close window after specified delay."""
        await asyncio.sleep(delay)
        await self._close_window(window, window_key)
    
    async def _close_window(self, window: StreamWindow, window_key: str):
        """Close window and compute aggregations."""
        if window_key not in self.active_windows[window.id]:
            return
        
        window_state = self.active_windows[window.id][window_key]
        
        # Get processor for this window
        processor = None
        for proc in self.processors.values():
            if any(w.id == window.id for w in proc.windows):
                processor = proc
                break
        
        if not processor:
            return
        
        # Compute aggregations
        for aggregation in processor.aggregations:
            if aggregation.window_id != window.id or not aggregation.enabled:
                continue
            
            try:
                result = await self._compute_aggregation(aggregation, window_state)
                window_state.aggregation_results[aggregation.id] = result
            except Exception as e:
                self.logger.error(f"Error computing aggregation {aggregation.id}: {e}")
        
        # Send aggregation results if output topic specified
        if self.kafka_available:
            producer = self.active_producers.get('main')
            if producer:
                for aggregation in processor.aggregations:
                    if (aggregation.window_id == window.id and 
                        aggregation.output_topic and 
                        aggregation.id in window_state.aggregation_results):
                        
                        result_data = {
                            'window_id': window.id,
                            'window_key': window_state.key,
                            'start_time': window_state.start_time.isoformat(),
                            'end_time': window_state.end_time.isoformat(),
                            'aggregation_id': aggregation.id,
                            'result': window_state.aggregation_results[aggregation.id],
                            'event_count': window_state.event_count,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
                        await producer.send(aggregation.output_topic, result_data)
        
        # Store aggregation results if database available
        if self.async_session:
            await self._store_window_results(window_state, processor)
        
        # Remove window from active windows
        del self.active_windows[window.id][window_key]
        
        self.logger.debug(f"Closed window {window_key} with {window_state.event_count} events")
    
    async def _compute_aggregation(self, aggregation: StreamAggregation, window_state: WindowState) -> Any:
        """Compute aggregation for window state."""
        events = window_state.events
        field = aggregation.field
        
        # Apply filters if specified
        filtered_events = events
        if aggregation.conditions:
            filtered_events = []
            for event in events:
                if self._evaluate_conditions(event, aggregation.conditions):
                    filtered_events.append(event)
        
        if not filtered_events:
            return None
        
        # Extract field values
        values = []
        for event in filtered_events:
            if field in event.data:
                values.append(event.data[field])
            elif field == "event_id":
                values.append(event.id)
            elif field == "timestamp":
                values.append(event.timestamp.timestamp())
            elif field == "user_id":
                values.append(event.user_id)
        
        # Compute aggregation
        if aggregation.aggregation_type == AggregationType.COUNT:
            return len(filtered_events)
        elif aggregation.aggregation_type == AggregationType.SUM:
            return sum(v for v in values if isinstance(v, (int, float)))
        elif aggregation.aggregation_type == AggregationType.AVG:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            return statistics.mean(numeric_values) if numeric_values else None
        elif aggregation.aggregation_type == AggregationType.MIN:
            return min(values) if values else None
        elif aggregation.aggregation_type == AggregationType.MAX:
            return max(values) if values else None
        elif aggregation.aggregation_type == AggregationType.DISTINCT_COUNT:
            return len(set(values))
        elif aggregation.aggregation_type == AggregationType.PERCENTILE:
            # Default to 95th percentile
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                return statistics.quantiles(numeric_values, n=20)[18]  # 95th percentile
            return None
        elif aggregation.aggregation_type == AggregationType.STANDARD_DEVIATION:
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            return statistics.stdev(numeric_values) if len(numeric_values) > 1 else None
        
        return None
    
    def _evaluate_conditions(self, event: StreamEvent, conditions: List[str]) -> bool:
        """Evaluate filter conditions for event."""
        # Simplified condition evaluation
        context = {
            'event': event,
            'data': event.data,
            'user_id': event.user_id,
            'platform': event.platform,
            'timestamp': event.timestamp
        }
        
        try:
            for condition in conditions:
                if not eval(condition, {"__builtins__": {}}, context):
                    return False
            return True
        except Exception:
            return False
    
    async def _store_window_results(self, window_state: WindowState, processor: StreamProcessor):
        """Store window results to database."""
        try:
            async with self.async_session() as session:
                metrics_record = StreamProcessingMetrics(
                    id=str(uuid.uuid4()),
                    processor_id=processor.id,
                    timestamp=datetime.utcnow(),
                    events_processed=window_state.event_count,
                    window_count=1,
                    metadata=json.dumps({
                        'window_id': window_state.window_id,
                        'window_key': window_state.key,
                        'aggregation_results': window_state.aggregation_results,
                        'start_time': window_state.start_time.isoformat(),
                        'end_time': window_state.end_time.isoformat()
                    })
                )
                session.add(metrics_record)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing window results: {e}")
    
    async def _collect_metrics(self):
        """Collect and update performance metrics."""
        while self.is_running:
            try:
                # Calculate events per second
                if self.latency_measurements:
                    current_time = time.time()
                    recent_events = len([
                        m for m in self.latency_measurements 
                        if current_time - m < 60  # Last minute
                    ])
                    self.metrics['events_per_second'] = recent_events / 60.0
                    
                    # Calculate average latency
                    self.metrics['average_processing_latency'] = statistics.mean(
                        self.latency_measurements
                    ) if self.latency_measurements else 0.0
                
                # Update active windows count
                total_windows = sum(len(windows) for windows in self.active_windows.values())
                self.metrics['active_windows'] = total_windows
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")
    
    async def _cleanup_expired_windows(self):
        """Clean up expired windows."""
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                expired_windows = []
                
                for window_id, windows in self.active_windows.items():
                    for window_key, window_state in windows.items():
                        # Check if window is expired
                        if (current_time - window_state.last_update).total_seconds() > 3600:  # 1 hour
                            expired_windows.append((window_id, window_key))
                
                # Remove expired windows
                for window_id, window_key in expired_windows:
                    if window_key in self.active_windows[window_id]:
                        del self.active_windows[window_id][window_key]
                
                if expired_windows:
                    self.logger.info(f"Cleaned up {len(expired_windows)} expired windows")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error cleaning up windows: {e}")
    
    # Built-in processor functions
    async def _process_user_activity(self, event: StreamEvent) -> Dict[str, Any]:
        """Process user activity events."""
        # Calculate engagement score
        engagement_score = 0
        if 'action' in event.data:
            action_scores = {
                'view': 1,
                'like': 2,
                'comment': 3,
                'share': 4,
                'purchase': 5
            }
            engagement_score = action_scores.get(event.data['action'], 0)
        
        return {
            'event_id': event.id,
            'user_id': event.user_id,
            'platform': event.platform,
            'engagement_score': engagement_score,
            'timestamp': event.timestamp.isoformat(),
            'processed_at': datetime.utcnow().isoformat()
        }
    
    async def _process_content_interaction(self, event: StreamEvent) -> Dict[str, Any]:
        """Process content interaction events."""
        return {
            'interaction_id': event.id,
            'content_id': event.data.get('content_id'),
            'user_id': event.user_id,
            'interaction_type': event.data.get('interaction_type'),
            'platform': event.platform,
            'timestamp': event.timestamp.isoformat(),
            'processed_at': datetime.utcnow().isoformat()
        }
    
    async def send_event(self, topic: str, event_data: Dict[str, Any]):
        """Send event to stream (for testing or manual triggering)."""
        if self.kafka_available:
            producer = self.active_producers.get('main')
            if producer:
                await producer.send(topic, event_data)
        else:
            # Add to local buffer
            self.event_buffer[topic].append(event_data)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current processing metrics."""
        return self.metrics.copy()
    
    def get_active_windows_count(self) -> int:
        """Get count of active windows."""
        return sum(len(windows) for windows in self.active_windows.values())
    
    async def get_window_state(self, window_id: str, window_key: str) -> Optional[Dict[str, Any]]:
        """Get current state of a window."""
        if window_id in self.active_windows and window_key in self.active_windows[window_id]:
            window_state = self.active_windows[window_id][window_key]
            return {
                'window_id': window_state.window_id,
                'key': window_state.key,
                'start_time': window_state.start_time.isoformat(),
                'end_time': window_state.end_time.isoformat(),
                'event_count': window_state.event_count,
                'last_update': window_state.last_update.isoformat(),
                'aggregation_results': window_state.aggregation_results
            }
        return None


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize streaming processor
        processor = StreamingDataProcessor(
            kafka_config={
                'bootstrap_servers': 'localhost:9092',
                'group_id': 'streaming_processor'
            },
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await processor.initialize()
        await processor.start_processing()
        
        # Send test events
        test_event = {
            'id': str(uuid.uuid4()),
            'stream_type': 'user_activity',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': 'user123',
            'platform': 'youtube',
            'data': {
                'action': 'like',
                'content_id': 'video456'
            }
        }
        
        await processor.send_event('user_activity', test_event)
        
        # Let it process for a while
        await asyncio.sleep(10)
        
        # Check metrics
        metrics = processor.get_metrics()
        print(f"Processing metrics: {metrics}")
        
        await processor.stop_processing()
    
    asyncio.run(main())