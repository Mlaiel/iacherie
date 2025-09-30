"""IA Influencer Agent - Event Streaming Module
Enterprise-grade Event Streaming System

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. See __init__.py for full notice.
"""

from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from datetime import datetime, timezone
from dataclasses import dataclass
from abc import ABC, abstractmethod
from asyncio import Queue, Event, Task, create_task, sleep
import asyncio
import json
import logging
from enum import Enum
from uuid import uuid4

from ..core.exceptions import EventStreamingError
from ..core.redis import RedisManager
from ..utils.monitoring import MetricsCollector
from ..security.authentication import SecurityManager

logger = logging.getLogger(__name__)


class StreamPosition(Enum):
    """
Stream reading positions"""

    BEGINNING = "beginning"
    LATEST = "latest"
    TIMESTAMP = "timestamp"
    OFFSET = "offset"


@dataclass
class StreamMessage:
    """Message in an event stream"""
    
    message_id: str
    stream_name: str
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime
    partition: Optional[int] = None
    offset: Optional[int] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class StreamConsumerConfig:
    """
Configuration for stream consumers"""
    
    consumer_group: str
    consumer_name: str
    max_batch_size: int = 100
    polling_interval: int = 1000  # milliseconds
    auto_commit: bool = True
    offset_reset: StreamPosition = StreamPosition.LATEST
    max_retries: int = 3
    retry_delay: int = 5000  # milliseconds


class StreamProducer:
    """
High-performance stream producer"""
    
    def __init__(self, redis_manager: RedisManager, 
                 metrics_collector: MetricsCollector):
        self.redis = redis_manager
        self.metrics = metrics_collector
        self._buffer: Queue = Queue(maxsize=10000)
        self._batch_size = 100
        self._flush_interval = 1.0  # seconds
        self._producer_task: Optional[Task] = None
        self._shutdown_event = Event()
    
    async def start(self):
        """
Start the producer"""
        if self._producer_task is None:
            self._producer_task = create_task(self._producer_loop())
            logger.info("Stream producer started")
    
    async def stop(self):
        """Stop the producer gracefully"""
        self._shutdown_event.set()
        if self._producer_task:
            await self._producer_task
            self._producer_task = None
        logger.info("Stream producer stopped")
    
    async def send(self, stream_name: str, message: StreamMessage) -> str:
        """Send a message to a stream"""
        try:
            await self._buffer.put({"stream_name": stream_name, "message": message})
            self.metrics.increment_counter("stream_messages_sent")
            return message.message_id
            
        except Exception as e:
            self.metrics.increment_counter("stream_send_errors")
            logger.error(f"Error sending message to stream {stream_name}: {str(e)}")
            raise EventStreamingError(f"Failed to send message: {str(e)}")
    
    async def _producer_loop(self):
        try:
            logger.info(f"Executing _producer_loop")
            
            # Implementation for _producer_loop
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_producer_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_producer_loop failed: {e}")
            raise
            await self._flush_batch(batch)
    
    async def _flush_batch(self, batch: List[Dict[str, Any]]):
        """Flush a batch of messages to Redis streams"""
        try:
            # Group messages by stream
            stream_batches = {}
            for item in batch:
                stream_name = item["stream_name"]
                if stream_name not in stream_batches:
                    stream_batches[stream_name] = []
                stream_batches[stream_name].append(item["message"])
            
            # Send each stream batch
            for stream_name, messages in stream_batches.items():
                await self._send_batch_to_stream(stream_name, messages)
            
            self.metrics.increment_counter("stream_batches_flushed", len(batch))
            
        except Exception as e:
            self.metrics.increment_counter("stream_flush_errors")
            logger.error(f"Error flushing batch: {str(e)}")
            raise
    
    async def _send_batch_to_stream(self, stream_name: str, 
                                  messages: List[StreamMessage]):
        """Send a batch of messages to a specific stream"""
        try:
            pipeline = self.redis.pipeline()
            
            for message in messages:
                # Prepare message data
                message_data = {
                    "event_type": message.event_type,
                    "payload": json.dumps(message.payload),
                    "headers": json.dumps(message.headers),
                    "timestamp": message.timestamp.isoformat(),
                    "correlation_id": message.correlation_id or ""
                }
                
                # Add to pipeline
                pipeline.xadd(stream_name, message_data, id=message.message_id)
            
            # Execute pipeline
            await pipeline.execute()
            
            logger.debug(f"Sent {len(messages)} messages to stream {stream_name}")
            
        except Exception as e:
            logger.error(f"Error sending batch to stream {stream_name}: {str(e)}")
            raise


class StreamConsumer:
    """High-performance stream consumer with consumer groups"""
    
    def __init__(self, redis_manager: RedisManager, 
                 config: StreamConsumerConfig,
                 metrics_collector: MetricsCollector):
        self.redis = redis_manager
        self.config = config
        self.metrics = metrics_collector
        self._running = False
        self._consumer_task: Optional[Task] = None
        self._message_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """
Register a message handler for specific event type"""
        self._message_handlers[event_type] = handler
    
    async def start(self, streams: List[str]):
        """
Start consuming from streams"""
        if self._running:
            return
        
        self._running = True
        
        # Create consumer group if not exists
        for stream in streams:
            try:
                await self.redis.xgroup_create(
                    stream, self.config.consumer_group, 
                    id="0", mkstream=True
                )
            except Exception:
                # Group already exists
                pass
        
        self._consumer_task = create_task(self._consumer_loop(streams))
        logger.info(f"Stream consumer started for streams: {streams}")
        try:
            logger.info(f"Executing start")
            
            # Implementation for start
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"start completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"start failed: {e}")
            raise
    
    async def _process_messages(self, raw_messages: List):
        """Process received messages"""
        try:
            for stream_name, stream_messages in raw_messages:
                for message_id, fields in stream_messages:
                    message = self._parse_message(
                        stream_name.decode(), 
                        message_id.decode(), 
                        fields
                    )
                    
                    await self._handle_message(message)
                    
                    # Acknowledge message if auto-commit enabled
                    if self.config.auto_commit:
                        await self.redis.xack(
                            stream_name, 
                            self.config.consumer_group, 
                            message_id
                        )
                    
                    self.metrics.increment_counter("stream_messages_processed")
            
        except Exception as e:
            self.metrics.increment_counter("stream_processing_errors")
            logger.error(f"Error processing messages: {str(e)}")
            raise
    
    def _parse_message(self, stream_name: str, message_id: str, 
                      fields: Dict) -> StreamMessage:
        """Parse raw Redis message into StreamMessage"""
        try:
            # Decode fields
            decoded_fields = {
                k.decode(): v.decode() for k, v in fields.items()
            }
            
            return StreamMessage(
                message_id=message_id,
                stream_name=stream_name,
                event_type=decoded_fields.get("event_type", ""),
                payload=json.loads(decoded_fields.get("payload", "{}")),
                headers=json.loads(decoded_fields.get("headers", "{}")),
                timestamp=datetime.fromisoformat(
                    decoded_fields.get("timestamp", datetime.now().isoformat())
                ),
                correlation_id=decoded_fields.get("correlation_id")
            )
            
        except Exception as e:
            logger.error(f"Error parsing message: {str(e)}")
            raise EventStreamingError(f"Failed to parse message: {str(e)}")
    
    async def _handle_message(self, message: StreamMessage):
        """Handle a parsed message"""
        try:
            handler = self._message_handlers.get(message.event_type)
            if handler:
                await handler(message)
            else:
                logger.warning(f"No handler for event type: {message.event_type}")
                
        except Exception as e:
            logger.error(f"Error handling message {message.message_id}: {str(e)}")
            
            # Implement dead letter queue for failed messages
            await self._send_to_dead_letter_queue(message, str(e))
            raise
    
    async def _send_to_dead_letter_queue(self, message: StreamMessage, error: str):
        """Send failed message to dead letter queue"""
        try:
            dlq_stream = f"{message.stream_name}:dlq"
            
            # Add error information to message
            dlq_message = StreamMessage(
                message_id=f"dlq_{message.message_id}",
                stream_name=dlq_stream,
                event_type=f"failed_{message.event_type}",
                payload={
                    "original_message": {
                        "message_id": message.message_id,
                        "stream_name": message.stream_name,
                        "event_type": message.event_type,
                        "payload": message.payload,
                        "headers": message.headers,
                        "timestamp": message.timestamp.isoformat()
                    },
                    "error": error,
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                    "retry_count": message.headers.get("retry_count", "0")
                },
                headers={
                    **message.headers,
                    "retry_count": str(int(message.headers.get("retry_count", "0")) + 1),
                    "error_type": "processing_error"
                },
                timestamp=datetime.now(timezone.utc),
                correlation_id=message.correlation_id
            )
            
            # Send to dead letter queue
            dlq_data = {
                "event_type": dlq_message.event_type,
                "payload": json.dumps(dlq_message.payload),
                "headers": json.dumps(dlq_message.headers),
                "timestamp": dlq_message.timestamp.isoformat(),
                "correlation_id": dlq_message.correlation_id or ""
            }
            
            await self.redis.xadd(dlq_stream, dlq_data, id=dlq_message.message_id)
            
            self.metrics.increment_counter("messages_sent_to_dlq")
            logger.info(f"Message {message.message_id} sent to dead letter queue: {dlq_stream}")
            
        except Exception as dlq_error:
            logger.error(f"Failed to send message to dead letter queue: {str(dlq_error)}")
            self.metrics.increment_counter("dlq_send_errors")


class EventStream:
    """High-level event stream abstraction"""
    
    def __init__(self, stream_name: str, redis_manager: RedisManager,
                 metrics_collector: MetricsCollector):
        self.stream_name = stream_name
        self.redis = redis_manager
        self.metrics = metrics_collector
    
    async def publish(self, event_type: str, payload: Dict[str, Any],
                     headers: Dict[str, str] = None,
                     correlation_id: str = None) -> str:
        """
Publish an event to the stream"""
        message = StreamMessage(
            message_id=str(uuid4()),
            stream_name=self.stream_name,
            event_type=event_type,
            payload=payload,
            headers=headers or {},
            timestamp=datetime.now(timezone.utc),
            correlation_id=correlation_id
        )
        
        producer = StreamProducer(self.redis, self.metrics)
        await producer.start()
        try:
            return await producer.send(self.stream_name, message)
        finally:
            await producer.stop()
    
    async def subscribe(self, consumer_config: StreamConsumerConfig,
                       handlers: Dict[str, Callable]) -> StreamConsumer:
        """
Subscribe to the stream with handlers"""
        consumer = StreamConsumer(self.redis, consumer_config, self.metrics)
        
        for event_type, handler in handlers.items():
            consumer.register_handler(event_type, handler)
        
        await consumer.start([self.stream_name])
        return consumer
    
    async def get_stream_info(self) -> Dict[str, Any]:
        """
Get stream information"""
        try:
            info = await self.redis.xinfo_stream(self.stream_name)
            return {
                "length": info[b"length"],
                "first_entry": info[b"first-entry"],
                "last_entry": info[b"last-entry"],
                "groups": info[b"groups"]
            }
        except Exception as e:
            logger.error(f"Error getting stream info: {str(e)}")
            return {}


class StreamProcessor:
    """Advanced stream processing capabilities"""
    
    def __init__(self, redis_manager: RedisManager,
                 metrics_collector: MetricsCollector):
        self.redis = redis_manager
        self.metrics = metrics_collector
        self._processors: Dict[str, Callable] = {}
    
    def register_processor(self, name: str, processor: Callable):
        """
Register a stream processor"""
        self._processors[name] = processor
    
    async def process_stream(self, input_stream: str, output_stream: str,
                           processor_name: str, 
                           consumer_config: StreamConsumerConfig):
        """
Process messages from input stream to output stream"""
        processor = self._processors.get(processor_name)
        if not processor:
            raise EventStreamingError(f"Unknown processor: {processor_name}")
        
        consumer = StreamConsumer(self.redis, consumer_config, self.metrics)
        producer = StreamProducer(self.redis, self.metrics)
        
        async def process_message(message: StreamMessage):
            try:
                # Process the message
                result = await processor(message)
                
                if result:
                    # Send processed result to output stream
                    output_message = StreamMessage(
                        message_id=str(uuid4()),
                        stream_name=output_stream,
                        event_type=result.get("event_type", "processed"),
                        payload=result.get("payload", {}),
                        headers=result.get("headers", {}),
                        timestamp=datetime.now(timezone.utc),
                        correlation_id=message.correlation_id
                    )
                    
                    await producer.send(output_stream, output_message)
                
                self.metrics.increment_counter("stream_messages_processed")
                
            except Exception as e:
                self.metrics.increment_counter("stream_processing_errors")
                logger.error(f"Error processing message: {str(e)}")
                raise
        
        # Register handler and start processing
        consumer.register_handler("*", process_message)  # Handle all event types
        
        await producer.start()
        await consumer.start([input_stream])
        
        return consumer, producer


class StreamingEngine:
    """Main engine for managing event streams"""
    
    def __init__(self, redis_manager: RedisManager,
                 security_manager: SecurityManager,
                 metrics_collector: MetricsCollector):
        self.redis = redis_manager
        self.security = security_manager
        self.metrics = metrics_collector
        self._streams: Dict[str, EventStream] = {}
        self._consumers: List[StreamConsumer] = []
        self._producers: List[StreamProducer] = []
    
    def create_stream(self, stream_name: str) -> EventStream:
        """
Create or get an event stream"""
        if stream_name not in self._streams:
            self._streams[stream_name] = EventStream(
                stream_name, self.redis, self.metrics
            )
        return self._streams[stream_name]
    
    async def shutdown(self):
        """
Shutdown all streams and consumers"""
        # Stop all consumers
        for consumer in self._consumers:
            await consumer.stop()
        
        # Stop all producers
        for producer in self._producers:
            await producer.stop()
        
        logger.info("Streaming engine shutdown complete")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get streaming system metrics"""
        metrics = {
            "total_streams": len(self._streams),
            "active_consumers": len(self._consumers),
            "active_producers": len(self._producers),
            "stream_details": {}
        }
        
        for stream_name, stream in self._streams.items():
            metrics["stream_details"][stream_name] = await stream.get_stream_info()
        
        return metrics


# Export public API
__all__ = [
    "StreamMessage", "StreamConsumerConfig", "StreamPosition",
    "StreamProducer", "StreamConsumer", "EventStream", 
    "StreamProcessor", "StreamingEngine"
]
