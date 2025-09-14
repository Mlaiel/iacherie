"""
Real Time Streaming Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Real-Time Streaming Engine - Enterprise Core Component
Real-time data streaming and processing system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive real-time streaming capabilities including:
- Real-time data streaming
- Stream processing and analytics
- Event stream aggregation
- Stream state management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import deque, defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Stream types"""
    EVENT_STREAM = "event_stream"
    DATA_STREAM = "data_stream"
    LOG_STREAM = "log_stream"
    METRIC_STREAM = "metric_stream"
    USER_ACTIVITY = "user_activity"
    SYSTEM_EVENTS = "system_events"
    REAL_TIME_ANALYTICS = "real_time_analytics"


class ProcessingMode(Enum):
    """Stream processing modes"""
    REAL_TIME = "real_time"
    MICRO_BATCH = "micro_batch"
    WINDOWED = "windowed"
    CONTINUOUS = "continuous"


class WindowType(Enum):
    """Window types for stream processing"""
    TUMBLING = "tumbling"
    SLIDING = "sliding"
    SESSION = "session"
    GLOBAL = "global"


class SerializationFormat(Enum):
    """Serialization formats"""
    JSON = "json"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    BINARY = "binary"


@dataclass
class StreamMessage:
    """Stream message structure"""
    message_id: str
    stream_id: str
    partition_key: Optional[str]
    timestamp: datetime
    data: Any
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StreamConfig:
    """Stream configuration"""
    stream_id: str
    name: str
    stream_type: StreamType
    partitions: int = 1
    retention_hours: int = 24
    compression_enabled: bool = True
    serialization_format: SerializationFormat = SerializationFormat.JSON
    max_message_size: int = 1048576  # 1MB
    rate_limit: Optional[int] = None  # messages per second
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessorConfig:
    """Stream processor configuration"""
    processor_id: str
    name: str
    input_streams: List[str]
    output_streams: List[str]
    processing_mode: ProcessingMode
    window_config: Optional[Dict[str, Any]] = None
    parallelism: int = 1
    processor_function: Optional[Callable] = None
    enabled: bool = True


@dataclass
class WindowConfig:
    """Window configuration for stream processing"""
    window_type: WindowType
    size: timedelta
    slide: Optional[timedelta] = None
    grace_period: timedelta = field(default_factory=lambda: timedelta(minutes=1))
    allowed_lateness: timedelta = field(default_factory=lambda: timedelta(minutes=5))


@dataclass
class StreamMetrics:
    """Stream metrics"""
    messages_produced: int = 0
    messages_consumed: int = 0
    bytes_produced: int = 0
    bytes_consumed: int = 0
    production_rate: float = 0.0
    consumption_rate: float = 0.0
    lag: int = 0
    last_activity: Optional[datetime] = None


@dataclass
class ProcessingWindow:
    """Processing window state"""
    window_id: str
    start_time: datetime
    end_time: datetime
    messages: List[StreamMessage] = field(default_factory=list)
    aggregated_data: Dict[str, Any] = field(default_factory=dict)
    is_closed: bool = False


class StreamConsumer:
    """Stream consumer"""
    
    def __init__(self, consumer_id -> None: str, stream_id -> None: str, consumer_group -> None: str = "default") -> None:
        self.consumer_id = consumer_id
        self.stream_id = stream_id
        self.consumer_group = consumer_group
        self.position = 0
        self.is_active = False
        self.message_handler: Optional[Callable] = None
        self.consumer_task: Optional[asyncio.Task] = None


class StreamProducer:
    """Stream producer"""
    
    def __init__(self, producer_id -> None: str, stream_id -> None: str) -> None:
        self.producer_id = producer_id
        self.stream_id = stream_id
        self.is_active = False
        self.batch_size = 100
        self.batch_timeout = 1000  # milliseconds


class RealTimeStreamingEngine:
    """
    Enterprise Real-Time Streaming Engine
    
    Manages comprehensive real-time data streaming with processing capabilities,
    windowed operations, and enterprise-grade performance monitoring.
    """
    
    def __init__(self) -> None:
        self.streams: Dict[str, StreamConfig] = {}
        self.stream_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100000))
        self.stream_metrics: Dict[str, StreamMetrics] = defaultdict(StreamMetrics)
        
        # Consumers and producers
        self.consumers: Dict[str, StreamConsumer] = {}
        self.producers: Dict[str, StreamProducer] = {}
        self.consumer_groups: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        
        # Stream processors
        self.processors: Dict[str, ProcessorConfig] = {}
        self.processor_tasks: Dict[str, asyncio.Task] = {}
        self.processing_windows: Dict[str, List[ProcessingWindow]] = defaultdict(list)
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "message_produced": [],
            "message_consumed": [],
            "stream_created": [],
            "processor_started": [],
            "window_closed": [],
            "backpressure_detected": []
        }
        
        # Configuration
        self.max_streams = 1000
        self.default_retention_hours = 24
        self.backpressure_threshold = 10000
        self.metrics_update_interval = 10  # seconds
        
        # Start metrics updater
        self._metrics_task: Optional[asyncio.Task] = None
        self._engine_started = False
        
        logger.info("Real-Time Streaming Engine initialized")
    
    async def start_engine(self) -> None:
        """Start the streaming engine"""
        if not self._engine_started:
            self._metrics_task = asyncio.create_task(self._metrics_updater())
            self._engine_started = True
            logger.info("Real-Time Streaming Engine started")
    
    async def create_stream(self, config: StreamConfig) -> bool:
        """Create a new stream"""
        try:
            if len(self.streams) >= self.max_streams:
                logger.error("Maximum number of streams reached")
                return False
            
            self.streams[config.stream_id] = config
            self.stream_data[config.stream_id] = deque(maxlen=100000)
            self.stream_metrics[config.stream_id] = StreamMetrics()
            
            await self._trigger_event("stream_created", config.stream_id)
            logger.info(f"Stream created: {config.stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create stream {config.stream_id}: {e}")
            return False
    
    async def create_producer(self, producer_id: str, stream_id: str) -> StreamProducer:
        """Create stream producer"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream not found: {stream_id}")
        
        producer = StreamProducer(producer_id, stream_id)
        self.producers[producer_id] = producer
        producer.is_active = True
        
        logger.info(f"Producer created: {producer_id} for stream {stream_id}")
        return producer
    
    async def create_consumer(
        self,
        consumer_id: str,
        stream_id: str,
        consumer_group: str = "default",
        message_handler: Optional[Callable] = None
    ) -> StreamConsumer:
        """Create stream consumer"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream not found: {stream_id}")
        
        consumer = StreamConsumer(consumer_id, stream_id, consumer_group)
        consumer.message_handler = message_handler
        
        self.consumers[consumer_id] = consumer
        self.consumer_groups[stream_id][consumer_group].append(consumer_id)
        
        if message_handler:
            await self._start_consumer(consumer)
        
        logger.info(f"Consumer created: {consumer_id} for stream {stream_id}")
        return consumer
    
    async def produce_message(
        self,
        producer_id: str,
        data: Any,
        partition_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Produce message to stream"""
        producer = self.producers.get(producer_id)
        if not producer or not producer.is_active:
            raise ValueError(f"Producer not found or inactive: {producer_id}")
        
        await self.start_engine()
        
        message_id = str(uuid.uuid4())
        
        message = StreamMessage(
            message_id=message_id,
            stream_id=producer.stream_id,
            partition_key=partition_key,
            timestamp=datetime.utcnow(),
            data=data,
            headers=headers or {}
        )
        
        # Add to stream
        self.stream_data[producer.stream_id].append(message)
        
        # Update metrics
        metrics = self.stream_metrics[producer.stream_id]
        metrics.messages_produced += 1
        metrics.bytes_produced += len(str(data))
        metrics.last_activity = datetime.utcnow()
        
        # Check for backpressure
        if len(self.stream_data[producer.stream_id]) > self.backpressure_threshold:
            await self._trigger_event("backpressure_detected", producer.stream_id)
        
        await self._trigger_event("message_produced", message_id)
        
        return message_id
    
    async def consume_messages(
        self,
        consumer_id: str,
        batch_size: int = 10,
        timeout_ms: int = 1000
    ) -> List[StreamMessage]:
        """Consume messages from stream"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            raise ValueError(f"Consumer not found: {consumer_id}")
        
        stream_data = self.stream_data[consumer.stream_id]
        messages = []
        
        # Get messages from current position
        start_position = consumer.position
        end_position = min(start_position + batch_size, len(stream_data))
        
        for i in range(start_position, end_position):
            if i < len(stream_data):
                messages.append(stream_data[i])
        
        # Update consumer position
        consumer.position = end_position
        
        # Update metrics
        if messages:
            metrics = self.stream_metrics[consumer.stream_id]
            metrics.messages_consumed += len(messages)
            metrics.bytes_consumed += sum(len(str(m.data)) for m in messages)
            metrics.lag = len(stream_data) - consumer.position
            
            for message in messages:
                await self._trigger_event("message_consumed", message.message_id)
        
        return messages
    
    async def create_processor(self, config: ProcessorConfig) -> bool:
        """Create stream processor"""
        try:
            # Validate input streams exist
            for stream_id in config.input_streams:
                if stream_id not in self.streams:
                    logger.error(f"Input stream not found: {stream_id}")
                    return False
            
            self.processors[config.processor_id] = config
            
            if config.enabled:
                await self._start_processor(config)
            
            logger.info(f"Stream processor created: {config.processor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create processor {config.processor_id}: {e}")
            return False
    
    async def get_stream_metrics(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get stream metrics"""
        if stream_id not in self.streams:
            return None
        
        metrics = self.stream_metrics[stream_id]
        config = self.streams[stream_id]
        
        return {
            "stream_id": stream_id,
            "stream_name": config.name,
            "stream_type": config.stream_type.value,
            "messages_produced": metrics.messages_produced,
            "messages_consumed": metrics.messages_consumed,
            "bytes_produced": metrics.bytes_produced,
            "bytes_consumed": metrics.bytes_consumed,
            "production_rate": metrics.production_rate,
            "consumption_rate": metrics.consumption_rate,
            "current_lag": metrics.lag,
            "current_size": len(self.stream_data[stream_id]),
            "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None,
            "partitions": config.partitions,
            "retention_hours": config.retention_hours
        }
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all streams"""
        metrics = {}
        
        for stream_id in self.streams:
            stream_metrics = await self.get_stream_metrics(stream_id)
            if stream_metrics:
                metrics[stream_id] = stream_metrics
        
        return {
            "streams": metrics,
            "summary": {
                "total_streams": len(self.streams),
                "total_producers": len(self.producers),
                "total_consumers": len(self.consumers),
                "total_processors": len(self.processors),
                "engine_uptime": datetime.utcnow().isoformat()
            }
        }
    
    async def create_windowed_processor(
        self,
        processor_id: str,
        input_stream: str,
        output_stream: str,
        window_config: WindowConfig,
        aggregator_function: Callable[[List[StreamMessage]], Any]
    ) -> bool:
        """Create windowed stream processor"""
        try:
            config = ProcessorConfig(
                processor_id=processor_id,
                name=f"Windowed Processor {processor_id}",
                input_streams=[input_stream],
                output_streams=[output_stream],
                processing_mode=ProcessingMode.WINDOWED,
                window_config={
                    "window_type": window_config.window_type.value,
                    "size_seconds": window_config.size.total_seconds(),
                    "slide_seconds": window_config.slide.total_seconds() if window_config.slide else None,
                    "grace_period_seconds": window_config.grace_period.total_seconds(),
                    "allowed_lateness_seconds": window_config.allowed_lateness.total_seconds()
                },
                processor_function=aggregator_function
            )
            
            return await self.create_processor(config)
            
        except Exception as e:
            logger.error(f"Failed to create windowed processor {processor_id}: {e}")
            return False
    
    async def query_stream(
        self,
        stream_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[StreamMessage]:
        """Query stream messages"""
        if stream_id not in self.streams:
            return []
        
        messages = list(self.stream_data[stream_id])
        
        # Filter by time range
        if start_time or end_time:
            filtered_messages = []
            for message in messages:
                if start_time and message.timestamp < start_time:
                    continue
                if end_time and message.timestamp > end_time:
                    continue
                filtered_messages.append(message)
            messages = filtered_messages
        
        # Apply limit
        return messages[:limit]
    
    async def replay_stream(
        self,
        stream_id: str,
        consumer_id: str,
        from_timestamp: datetime,
        to_timestamp: Optional[datetime] = None
    ) -> int:
        """Replay stream messages for consumer"""
        consumer = self.consumers.get(consumer_id)
        if not consumer or consumer.stream_id != stream_id:
            raise ValueError(f"Consumer not found or stream mismatch: {consumer_id}")
        
        messages = await self.query_stream(stream_id, from_timestamp, to_timestamp)
        
        # Reset consumer position to replay from
        stream_data = self.stream_data[stream_id]
        for i, message in enumerate(stream_data):
            if message.timestamp >= from_timestamp:
                consumer.position = i
                break
        
        logger.info(f"Stream replay initiated for {consumer_id}: {len(messages)} messages")
        return len(messages)
    
    async def pause_consumer(self, consumer_id: str) -> bool:
        """Pause consumer"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return False
        
        consumer.is_active = False
        if consumer.consumer_task:
            consumer.consumer_task.cancel()
        
        logger.info(f"Consumer paused: {consumer_id}")
        return True
    
    async def resume_consumer(self, consumer_id: str) -> bool:
        """Resume consumer"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return False
        
        consumer.is_active = True
        if consumer.message_handler:
            await self._start_consumer(consumer)
        
        logger.info(f"Consumer resumed: {consumer_id}")
        return True
    
    async def delete_stream(self, stream_id: str, force: bool = False) -> bool:
        """Delete stream"""
        try:
            if stream_id not in self.streams:
                return False
            
            # Check for active consumers/producers
            active_consumers = [c for c in self.consumers.values() if c.stream_id == stream_id and c.is_active]
            active_producers = [p for p in self.producers.values() if p.stream_id == stream_id and p.is_active]
            
            if (active_consumers or active_producers) and not force:
                logger.error(f"Cannot delete stream with active consumers/producers: {stream_id}")
                return False
            
            # Stop and remove consumers/producers
            for consumer in active_consumers:
                await self.pause_consumer(consumer.consumer_id)
                del self.consumers[consumer.consumer_id]
            
            for producer in active_producers:
                producer.is_active = False
                del self.producers[producer.producer_id]
            
            # Remove stream data
            del self.streams[stream_id]
            del self.stream_data[stream_id]
            del self.stream_metrics[stream_id]
            
            logger.info(f"Stream deleted: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete stream {stream_id}: {e}")
            return False
    
    # Private methods
    
    async def _start_consumer(self, consumer -> None: StreamConsumer) -> None:
        """Start consumer task"""
        async def consumer_loop() -> None:
            consumer.is_active = True
            
            while consumer.is_active:
                try:
                    messages = await self.consume_messages(consumer.consumer_id, batch_size=10)
                    
                    if messages and consumer.message_handler:
                        for message in messages:
                            try:
                                if asyncio.iscoroutinefunction(consumer.message_handler):
                                    await consumer.message_handler(message)
                                else:
                                    consumer.message_handler(message)
                            except Exception as e:
                                logger.error(f"Message handler error: {e}")
                    
                    if not messages:
                        await asyncio.sleep(0.1)  # Small delay when no messages
                        
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Consumer loop error: {e}")
                    await asyncio.sleep(1)
            
            consumer.is_active = False
        
        consumer.consumer_task = asyncio.create_task(consumer_loop())
    
    async def _start_processor(self, config -> None: ProcessorConfig) -> None:
        """Start stream processor"""
        async def processor_loop() -> None:
            logger.info(f"Starting processor: {config.processor_id}")
            
            while config.enabled:
                try:
                    # Process based on mode
                    if config.processing_mode == ProcessingMode.WINDOWED:
                        await self._process_windowed(config)
                    elif config.processing_mode == ProcessingMode.REAL_TIME:
                        await self._process_real_time(config)
                    elif config.processing_mode == ProcessingMode.MICRO_BATCH:
                        await self._process_micro_batch(config)
                    
                    await asyncio.sleep(1)  # Processing interval
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Processor error {config.processor_id}: {e}")
                    await asyncio.sleep(5)
        
        task = asyncio.create_task(processor_loop())
        self.processor_tasks[config.processor_id] = task
        
        await self._trigger_event("processor_started", config.processor_id)
    
    async def _process_windowed(self, config -> None: ProcessorConfig) -> None:
        """Process windowed stream data"""
        if not config.window_config:
            return
        
        window_size = timedelta(seconds=config.window_config["size_seconds"])
        current_time = datetime.utcnow()
        
        # Create or update windows
        for input_stream in config.input_streams:
            windows = self.processing_windows[config.processor_id]
            
            # Find or create current window
            current_window = None
            for window in windows:
                if not window.is_closed and current_time < window.end_time:
                    current_window = window
                    break
            
            if not current_window:
                # Create new window
                window_start = current_time.replace(second=0, microsecond=0)
                current_window = ProcessingWindow(
                    window_id=str(uuid.uuid4()),
                    start_time=window_start,
                    end_time=window_start + window_size
                )
                windows.append(current_window)
            
            # Add messages to window
            stream_messages = await self.query_stream(
                input_stream,
                current_window.start_time,
                current_window.end_time,
                limit=1000
            )
            
            current_window.messages.extend(stream_messages)
            
            # Close and process completed windows
            completed_windows = [w for w in windows if current_time >= w.end_time and not w.is_closed]
            
            for window in completed_windows:
                if config.processor_function and window.messages:
                    try:
                        result = config.processor_function(window.messages)
                        window.aggregated_data = result
                        
                        # Send result to output streams
                        for output_stream in config.output_streams:
                            if output_stream in self.streams:
                                await self._send_processed_result(output_stream, result, window)
                        
                    except Exception as e:
                        logger.error(f"Window processing error: {e}")
                
                window.is_closed = True
                await self._trigger_event("window_closed", window.window_id)
            
            # Cleanup old windows
            self.processing_windows[config.processor_id] = [
                w for w in windows
                if current_time - w.end_time < timedelta(hours=1)
            ]
    
    async def _process_real_time(self, config -> None: ProcessorConfig) -> None:
        """Process real-time stream data"""
        for input_stream in config.input_streams:
            # Get recent messages
            recent_messages = await self.query_stream(input_stream, limit=100)
            
            if recent_messages and config.processor_function:
                try:
                    result = config.processor_function(recent_messages)
                    
                    # Send to output streams
                    for output_stream in config.output_streams:
                        if output_stream in self.streams:
                            await self._send_processed_result(output_stream, result)
                            
                except Exception as e:
                    logger.error(f"Real-time processing error: {e}")
    
    async def _process_micro_batch(self, config -> None: ProcessorConfig) -> None:
        """Process micro-batch stream data"""
        batch_size = 1000
        
        for input_stream in config.input_streams:
            messages = await self.query_stream(input_stream, limit=batch_size)
            
            if messages and config.processor_function:
                try:
                    result = config.processor_function(messages)
                    
                    # Send to output streams
                    for output_stream in config.output_streams:
                        if output_stream in self.streams:
                            await self._send_processed_result(output_stream, result)
                            
                except Exception as e:
                    logger.error(f"Micro-batch processing error: {e}")
    
    async def _send_processed_result(
        self,
        output_stream -> None: str,
        result -> None: Any,
        window -> None: Optional[ProcessingWindow] = None
    ) -> None:
        """Send processed result to output stream"""
        message = StreamMessage(
            message_id=str(uuid.uuid4()),
            stream_id=output_stream,
            partition_key=window.window_id if window else None,
            timestamp=datetime.utcnow(),
            data=result,
            headers={"processed": "true"},
            metadata={"window_id": window.window_id} if window else {}
        )
        
        self.stream_data[output_stream].append(message)
        
        # Update metrics
        metrics = self.stream_metrics[output_stream]
        metrics.messages_produced += 1
        metrics.bytes_produced += len(str(result))
        metrics.last_activity = datetime.utcnow()
    
    async def _metrics_updater(self) -> None:
        """Update stream metrics periodically"""
        while True:
            try:
                await asyncio.sleep(self.metrics_update_interval)
                
                for stream_id, metrics in self.stream_metrics.items():
                    # Calculate rates (simplified)
                    if metrics.last_activity:
                        time_diff = (datetime.utcnow() - metrics.last_activity).total_seconds()
                        if time_diff > 0:
                            metrics.production_rate = metrics.messages_produced / time_diff
                            metrics.consumption_rate = metrics.messages_consumed / time_diff
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
    
    async def _trigger_event(self, event_type -> None: str, event_data -> None: str) -> None:
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
real_time_streaming_engine = RealTimeStreamingEngine()


# Convenience functions
async def create_simple_stream(stream_id: str, name: str, stream_type: StreamType) -> bool:
    """Create a simple stream"""
    config = StreamConfig(
        stream_id=stream_id,
        name=name,
        stream_type=stream_type
    )
    return await real_time_streaming_engine.create_stream(config)


async def create_event_stream(stream_id: str, name: str) -> bool:
    """Create event stream"""
    return await create_simple_stream(stream_id, name, StreamType.EVENT_STREAM)


async def create_metrics_stream(stream_id: str, name: str) -> bool:
    """Create metrics stream"""
    return await create_simple_stream(stream_id, name, StreamType.METRIC_STREAM)


async def produce_event(producer_id: str, event_data: Dict[str, Any]) -> str:
    """Produce event to stream"""
    return await real_time_streaming_engine.produce_message(producer_id, event_data)


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Create event stream
        await create_event_stream("user_events", "User Activity Events")
        
        # Create producer and consumer
        producer = await real_time_streaming_engine.create_producer("event_producer", "user_events")
        
        def message_handler(message -> None: StreamMessage) -> None:
            print(f"Received event: {message.data}")
        
        consumer = await real_time_streaming_engine.create_consumer(
            "event_consumer", "user_events", message_handler=message_handler
        )
        
        # Produce some events
        await produce_event("event_producer", {"user_id": "123", "action": "login"})
        await produce_event("event_producer", {"user_id": "456", "action": "purchase"})
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get metrics
        metrics = await real_time_streaming_engine.get_stream_metrics("user_events")
        print(f"Stream metrics: {metrics}")
        
        all_metrics = await real_time_streaming_engine.get_all_metrics()
        print(f"All metrics: {all_metrics}")
    
    asyncio.run(main())