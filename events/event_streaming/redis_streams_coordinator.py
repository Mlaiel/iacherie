"""IA Influencer Agent - Redis Streams Coordinator
High-Frequency Event Coordination using Redis Streams for Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. This is proprietary technology.
"""

from typing import Dict, Any, List, Optional, Callable, Union, AsyncGenerator, TYPE_CHECKING

if TYPE_CHECKING:
    import redis.asyncio as redis_async
else:
    try:
        import redis.asyncio as redis_async
    except ImportError:
        import redis as redis_async
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import logging
import time
import redis
from uuid import uuid4
from collections import defaultdict

logger = logging.getLogger(__name__)


class StreamReadMode(Enum):
    """Stream reading modes"""
    BLOCKING = "blocking"
    NON_BLOCKING = "non_blocking"
    TAILING = "tailing"


class ConsumerGroupState(Enum):
    """Consumer group states"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class AinflueBusinesRedisStreams:
    """Redis streams for Ainflue high-frequency events"""
    
    # High-frequency events
    USER_INTERACTIONS = "ainflue:user:interactions"
    REAL_TIME_ANALYTICS = "ainflue:analytics:realtime"
    ENGAGEMENT_TRACKING = "ainflue:engagement:tracking"
    
    # Content processing queues
    CONTENT_UPLOAD_QUEUE = "ainflue:content:upload:queue"
    AI_PROCESSING_QUEUE = "ainflue:ai:processing:queue"
    
    # Collaboration real-time
    COLLABORATION_NOTIFICATIONS = "ainflue:collaboration:notifications"
    MATCHING_UPDATES = "ainflue:matching:updates"
    
    # Revenue tracking
    REVENUE_EVENTS = "ainflue:revenue:events"
    PAYMENT_NOTIFICATIONS = "ainflue:payment:notifications"


@dataclass
class RedisStreamMessage:
    """Redis stream message structure"""
    
    stream_name: str
    message_id: str
    fields: Dict[str, Any]
    timestamp: datetime
    consumer_group: Optional[str] = None
    consumer_name: Optional[str] = None
    delivery_count: int = 0


@dataclass
class ConsumerGroupConfig:
    """Configuration for Redis consumer group"""
    
    group_name: str
    consumer_name: str
    streams: List[str]
    block_time_ms: int = 1000
    count: int = 10
    auto_ack: bool = False
    max_retries: int = 3
    retry_delay_ms: int = 5000
    trim_strategy: str = "MAXLEN"
    trim_threshold: int = 10000
    backup_to_kafka: bool = True


@dataclass
class StreamMetrics:
    """Stream performance metrics"""
    
    stream_name: str
    message_count: int = 0
    consumer_groups: int = 0
    pending_messages: int = 0
    memory_usage_bytes: int = 0
    last_entry_id: str = "0-0"
    throughput_per_sec: float = 0.0
    avg_processing_time_ms: float = 0.0
    error_count: int = 0


@dataclass
class ConsumerGroupMetrics:
    """Consumer group metrics"""
    
    group_name: str
    consumer_count: int = 0
    pending_count: int = 0
    lag: int = 0
    messages_processed: int = 0
    messages_failed: int = 0
    last_delivered_id: str = "0-0"
    state: ConsumerGroupState = ConsumerGroupState.ACTIVE


class RedisStreamConsumer:
    """Individual Redis stream consumer"""
    
    def __init__(self, 
                 redis_client -> None: Any, 
                 config -> None: ConsumerGroupConfig,
                 message_handler -> None: Callable[[RedisStreamMessage], bool],
                 metrics_collector=None) -> None:
        self.redis = redis_client
        self.config = config
        self.message_handler = message_handler
        self.metrics_collector = metrics_collector
        self.state = ConsumerGroupState.STOPPED
        self._consumer_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Start unpaused
        self.metrics = ConsumerGroupMetrics(group_name=config.group_name)
        
    async def start(self) -> None:
        """Start the consumer"""
        try:
            if self.state != ConsumerGroupState.STOPPED:
                raise ValueError(f"Consumer {self.config.consumer_name} is not stopped")
            
            logger.info(f"Starting Redis stream consumer {self.config.consumer_name}")
            
            # Create consumer groups if they don't exist
            await self._ensure_consumer_groups()
            
            # Start consumer task
            self._consumer_task = asyncio.create_task(self._consumer_loop())
            
            self.state = ConsumerGroupState.ACTIVE
            self.metrics.state = ConsumerGroupState.ACTIVE
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("redis_consumer_started")
            
            logger.info(f"Redis stream consumer {self.config.consumer_name} started")
            
        except Exception as e:
            self.state = ConsumerGroupState.ERROR
            self.metrics.state = ConsumerGroupState.ERROR
            logger.error(f"Failed to start Redis consumer {self.config.consumer_name}: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the consumer gracefully"""
        try:
            if self.state == ConsumerGroupState.STOPPED:
                return
            
            logger.info(f"Stopping Redis stream consumer {self.config.consumer_name}")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Wait for consumer task
            if self._consumer_task:
                await self._consumer_task
            
            self.state = ConsumerGroupState.STOPPED
            self.metrics.state = ConsumerGroupState.STOPPED
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("redis_consumer_stopped")
            
            logger.info(f"Redis stream consumer {self.config.consumer_name} stopped")
            
        except Exception as e:
            self.state = ConsumerGroupState.ERROR
            logger.error(f"Error stopping Redis consumer {self.config.consumer_name}: {e}")
            raise
    
    async def pause(self) -> None:
        """Pause the consumer"""
        if self.state == ConsumerGroupState.ACTIVE:
            self.state = ConsumerGroupState.PAUSED
            self.metrics.state = ConsumerGroupState.PAUSED
            self._pause_event.clear()
            logger.info(f"Redis consumer {self.config.consumer_name} paused")
    
    async def resume(self) -> None:
        """Resume the consumer"""
        if self.state == ConsumerGroupState.PAUSED:
            self.state = ConsumerGroupState.ACTIVE
            self.metrics.state = ConsumerGroupState.ACTIVE
            self._pause_event.set()
            logger.info(f"Redis consumer {self.config.consumer_name} resumed")
    
    async def _ensure_consumer_groups(self) -> None:
        """Ensure consumer groups exist for all streams"""
        try:
            for stream in self.config.streams:
                try:
                    await self.redis.xgroup_create(
                        stream, 
                        self.config.group_name, 
                        id="0", 
                        mkstream=True
                    )
                    logger.debug(f"Created consumer group {self.config.group_name} for stream {stream}")
                except redis.ResponseError as e:
                    if "BUSYGROUP" in str(e):
                        # Group already exists
                        logger.debug(f"Consumer group {self.config.group_name} already exists for {stream}")
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Error ensuring consumer groups: {e}")
            raise
    
    async def _consumer_loop(self) -> None:
        """Main consumer loop"""
        try:
            while not self._shutdown_event.is_set():
                # Wait if paused
                await self._pause_event.wait()
                
                try:
                    # Read messages from streams
                    stream_data = await self._read_from_streams()
                    
                    if stream_data:
                        await self._process_stream_data(stream_data)
                    
                    # Process pending messages
                    await self._process_pending_messages()
                    
                except asyncio.TimeoutError:
                    # No messages received, continue
                    continue
                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}")
                    await asyncio.sleep(1)  # Brief pause before retrying
                    
        except Exception as e:
            logger.error(f"Fatal error in consumer loop: {e}")
            self.state = ConsumerGroupState.ERROR
            self.metrics.state = ConsumerGroupState.ERROR
            raise
    
    async def _read_from_streams(self) -> Optional[List]:
        """Read messages from Redis streams"""
        try:
            # Prepare stream dict for XREADGROUP
            streams = {stream: ">" for stream in self.config.streams}
            
            # Read messages
            result = await self.redis.xreadgroup(
                self.config.group_name,
                self.config.consumer_name,
                streams,
                count=self.config.count,
                block=self.config.block_time_ms
            )
            
            return result
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error reading from streams: {e}")
            return None
    
    async def _process_stream_data(self, stream_data -> None: List) -> None:
        """Process received stream data"""
        try:
            for stream_name, messages in stream_data:
                stream_name = stream_name.decode() if isinstance(stream_name, bytes) else stream_name
                
                for message_id, fields in messages:
                    message_id = message_id.decode() if isinstance(message_id, bytes) else message_id
                    
                    # Parse fields
                    parsed_fields = {}
                    for key, value in fields.items():
                        key = key.decode() if isinstance(key, bytes) else key
                        value = value.decode() if isinstance(value, bytes) else value
                        parsed_fields[key] = value
                    
                    # Create message object
                    message = RedisStreamMessage(
                        stream_name=stream_name,
                        message_id=message_id,
                        fields=parsed_fields,
                        timestamp=datetime.now(timezone.utc),
                        consumer_group=self.config.group_name,
                        consumer_name=self.config.consumer_name
                    )
                    
                    # Process message
                    await self._process_single_message(message)
                    
        except Exception as e:
            logger.error(f"Error processing stream data: {e}")
            raise
    
    async def _process_single_message(self, message -> None: RedisStreamMessage) -> None:
        """Process a single message"""
        try:
            start_time = time.time()
            
            # Call message handler
            success = await self.message_handler(message)
            
            processing_time = (time.time() - start_time) * 1000
            
            if success:
                # Acknowledge message if auto-ack is enabled
                if self.config.auto_ack:
                    await self._acknowledge_message(message)
                
                self.metrics.messages_processed += 1
                
                # Update processing time
                if self.metrics.avg_processing_time_ms == 0:
                    self.metrics.avg_processing_time_ms = processing_time
                else:
                    alpha = 0.1
                    self.metrics.avg_processing_time_ms = (
                        (1 - alpha) * self.metrics.avg_processing_time_ms + 
                        alpha * processing_time
                    )
                
                if self.metrics_collector:
                    self.metrics_collector.histogram("redis_message_processing_time", processing_time)
                    self.metrics_collector.increment_counter("redis_messages_processed")
                
                logger.debug(f"Processed message {message.message_id} in {processing_time:.2f}ms")
                
            else:
                self.metrics.messages_failed += 1
                logger.warning(f"Failed to process message {message.message_id}")
                
                if self.metrics_collector:
                    self.metrics_collector.increment_counter("redis_message_processing_errors")
                
        except Exception as e:
            self.metrics.messages_failed += 1
            logger.error(f"Error processing message {message.message_id}: {e}")
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("redis_message_processing_errors")
    
    async def _acknowledge_message(self, message -> None: RedisStreamMessage) -> None:
        """Acknowledge a processed message"""
        try:
            await self.redis.xack(
                message.stream_name,
                self.config.group_name,
                message.message_id
            )
            logger.debug(f"Acknowledged message {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error acknowledging message {message.message_id}: {e}")
    
    async def _process_pending_messages(self) -> None:
        """Process pending messages that may have failed previously"""
        try:
            for stream in self.config.streams:
                # Get pending messages for this consumer
                pending = await self.redis.xpending_range(
                    stream,
                    self.config.group_name,
                    min="-",
                    max="+",
                    count=10,
                    consumer=self.config.consumer_name
                )
                
                for message_info in pending:
                    message_id = message_info[0].decode()
                    delivery_count = message_info[3]
                    
                    # Check if message should be retried
                    if delivery_count <= self.config.max_retries:
                        # Claim and reprocess message
                        claimed = await self.redis.xclaim(
                            stream,
                            self.config.group_name,
                            self.config.consumer_name,
                            min_idle_time=self.config.retry_delay_ms,
                            message_ids=[message_id]
                        )
                        
                        if claimed:
                            # Process claimed message
                            for claim_stream, claim_messages in claimed:
                                for claim_message_id, fields in claim_messages:
                                    # Create message object
                                    parsed_fields = {}
                                    for key, value in fields.items():
                                        key = key.decode() if isinstance(key, bytes) else key
                                        value = value.decode() if isinstance(value, bytes) else value
                                        parsed_fields[key] = value
                                    
                                    message = RedisStreamMessage(
                                        stream_name=stream,
                                        message_id=claim_message_id.decode(),
                                        fields=parsed_fields,
                                        timestamp=datetime.now(timezone.utc),
                                        consumer_group=self.config.group_name,
                                        consumer_name=self.config.consumer_name,
                                        delivery_count=delivery_count
                                    )
                                    
                                    await self._process_single_message(message)
                    else:
                        # Max retries exceeded, acknowledge to remove from pending
                        await self.redis.xack(stream, self.config.group_name, message_id)
                        logger.warning(f"Max retries exceeded for message {message_id}, removing from pending")
                        
        except Exception as e:
            logger.error(f"Error processing pending messages: {e}")


class RedisStreamsCoordinator:
    """Coordinates Redis Streams for high-frequency Ainflue events"""
    
    def __init__(self, redis_client -> None: Any, metrics_collector=None) -> None:
        self.redis = redis_client
        self.metrics_collector = metrics_collector
        self.consumers: Dict[str, RedisStreamConsumer] = {}
        self.stream_metrics: Dict[str, StreamMetrics] = {}
        self._coordinator_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._backup_producers: Dict[str, Callable] = {}  # For Kafka backup
        
    async def start(self) -> None:
        """Start the Redis streams coordinator"""
        try:
            logger.info("Starting Redis Streams Coordinator")
            
            # Start coordinator monitoring task
            self._coordinator_task = asyncio.create_task(self._coordinator_loop())
            
            # Setup default streams for Ainflue
            await self._setup_default_streams()
            
            logger.info("Redis Streams Coordinator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Redis streams coordinator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the coordinator"""
        try:
            logger.info("Stopping Redis Streams Coordinator")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop all consumers
            for consumer in self.consumers.values():
                await consumer.stop()
            
            # Wait for coordinator task
            if self._coordinator_task:
                await self._coordinator_task
            
            logger.info("Redis Streams Coordinator stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping Redis streams coordinator: {e}")
            raise
    
    async def _setup_default_streams(self) -> None:
        """Setup default Redis streams for Ainflue"""
        try:
            # Create default streams
            default_streams = [
                AinflueBusinesRedisStreams.USER_INTERACTIONS,
                AinflueBusinesRedisStreams.REAL_TIME_ANALYTICS,
                AinflueBusinesRedisStreams.ENGAGEMENT_TRACKING,
                AinflueBusinesRedisStreams.CONTENT_UPLOAD_QUEUE,
                AinflueBusinesRedisStreams.AI_PROCESSING_QUEUE,
                AinflueBusinesRedisStreams.COLLABORATION_NOTIFICATIONS,
                AinflueBusinesRedisStreams.MATCHING_UPDATES,
                AinflueBusinesRedisStreams.REVENUE_EVENTS,
                AinflueBusinesRedisStreams.PAYMENT_NOTIFICATIONS
            ]
            
            for stream_name in default_streams:
                # Initialize stream metrics
                self.stream_metrics[stream_name] = StreamMetrics(stream_name=stream_name)
                
                # Create stream if it doesn't exist
                try:
                    await self.redis.xadd(stream_name, {"init": "stream"}, id="0-1")
                    await self.redis.xdel(stream_name, "0-1")  # Remove init message
                except Exception:
                    # Stream might already exist
                    pass
            
            logger.info(f"Setup {len(default_streams)} default Redis streams")
            
        except Exception as e:
            logger.error(f"Error setting up default streams: {e}")
            raise
    
    async def create_consumer(self, 
                            consumer_name: str, 
                            config: ConsumerGroupConfig,
                            message_handler: Callable[[RedisStreamMessage], bool]) -> str:
        """Create a new Redis stream consumer"""
        try:
            if consumer_name in self.consumers:
                raise ValueError(f"Consumer {consumer_name} already exists")
            
            logger.info(f"Creating Redis stream consumer {consumer_name}")
            
            # Create consumer
            consumer = RedisStreamConsumer(
                redis_client=self.redis,
                config=config,
                message_handler=message_handler,
                metrics_collector=self.metrics_collector
            )
            
            # Start consumer
            await consumer.start()
            
            # Store consumer
            self.consumers[consumer_name] = consumer
            
            logger.info(f"Created Redis stream consumer {consumer_name} successfully")
            return consumer_name
            
        except Exception as e:
            logger.error(f"Error creating Redis consumer {consumer_name}: {e}")
            raise
    
    async def remove_consumer(self, consumer_name -> None: str) -> None:
        """Remove a Redis stream consumer"""
        try:
            if consumer_name not in self.consumers:
                raise ValueError(f"Consumer {consumer_name} not found")
            
            logger.info(f"Removing Redis stream consumer {consumer_name}")
            
            # Stop and remove consumer
            consumer = self.consumers[consumer_name]
            await consumer.stop()
            del self.consumers[consumer_name]
            
            logger.info(f"Removed Redis stream consumer {consumer_name}")
            
        except Exception as e:
            logger.error(f"Error removing Redis consumer {consumer_name}: {e}")
            raise
    
    async def publish_event(self, 
                           stream_name: str, 
                           event_data: Dict[str, Any],
                           message_id: Optional[str] = None) -> str:
        """Publish an event to Redis stream"""
        try:
            # Prepare message fields
            fields = {
                "event_type": event_data.get("event_type", "generic"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": json.dumps(event_data),
                "source": "ainflue-platform"
            }
            
            # Add to stream
            result_id = await self.redis.xadd(
                stream_name, 
                fields, 
                id=message_id or "*"
            )
            
            # Update stream metrics
            if stream_name in self.stream_metrics:
                self.stream_metrics[stream_name].message_count += 1
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("redis_messages_published")
                self.metrics_collector.histogram("redis_message_size", len(json.dumps(fields)))
            
            logger.debug(f"Published event to {stream_name} with ID {result_id}")
            
            # Backup to Kafka if configured
            if self.config.backup_to_kafka and stream_name in self._backup_producers:
                await self._backup_to_kafka(stream_name, event_data)
            
            return result_id.decode() if isinstance(result_id, bytes) else result_id
            
        except Exception as e:
            logger.error(f"Error publishing event to {stream_name}: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("redis_publish_errors")
            raise
    
    async def _backup_to_kafka(self, stream_name -> None: str, event_data -> None: Dict[str, Any]) -> None:
        """Backup Redis stream message to Kafka for durability"""
        try:
            if stream_name in self._backup_producers:
                backup_producer = self._backup_producers[stream_name]
                await backup_producer(event_data)
                
                if self.metrics_collector:
                    self.metrics_collector.increment_counter("redis_kafka_backup_sent")
                    
        except Exception as e:
            logger.error(f"Error backing up to Kafka: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("redis_kafka_backup_errors")
    
    async def trim_streams(self) -> None:
        """Trim streams to manage memory usage"""
        try:
            for stream_name, metrics in self.stream_metrics.items():
                try:
                    # Get stream info
                    info = await self.redis.xinfo_stream(stream_name)
                    length = info[b"length"]
                    
                    # Trim if above threshold
                    if length > 10000:  # Default threshold
                        await self.redis.xtrim(stream_name, maxlen=8000, approximate=True)
                        logger.info(f"Trimmed stream {stream_name} from {length} to ~8000 messages")
                        
                except Exception as e:
                    logger.warning(f"Error trimming stream {stream_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in stream trimming: {e}")
    
    async def _coordinator_loop(self) -> None:
        """Main coordinator monitoring loop"""
        try:
            while not self._shutdown_event.is_set():
                # Update stream metrics
                await self._update_stream_metrics()
                
                # Trim streams if needed
                await self.trim_streams()
                
                # Monitor consumer health
                await self._monitor_consumer_health()
                
                # Sleep before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            logger.error(f"Error in coordinator loop: {e}")
    
    async def _update_stream_metrics(self) -> None:
        """Update metrics for all streams"""
        try:
            for stream_name, metrics in self.stream_metrics.items():
                try:
                    # Get stream info
                    info = await self.redis.xinfo_stream(stream_name)
                    
                    metrics.message_count = info[b"length"]
                    metrics.consumer_groups = info[b"groups"]
                    
                    if info[b"last-entry"]:
                        metrics.last_entry_id = info[b"last-entry"][0].decode()
                    
                    # Get memory usage (approximate)
                    memory_info = await self.redis.memory_usage(stream_name)
                    if memory_info:
                        metrics.memory_usage_bytes = memory_info
                    
                except Exception as e:
                    logger.warning(f"Error updating metrics for stream {stream_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error updating stream metrics: {e}")
    
    async def _monitor_consumer_health(self) -> None:
        """Monitor health of all consumers"""
        try:
            for consumer_name, consumer in self.consumers.items():
                if consumer.state == ConsumerGroupState.ERROR:
                    logger.warning(f"Consumer {consumer_name} is in error state, attempting restart")
                    
                    try:
                        await consumer.stop()
                        await consumer.start()
                        logger.info(f"Successfully restarted consumer {consumer_name}")
                    except Exception as e:
                        logger.error(f"Failed to restart consumer {consumer_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Error monitoring consumer health: {e}")
    
    def get_coordinator_metrics(self) -> Dict[str, Any]:
        """Get comprehensive coordinator metrics"""
        try:
            total_messages = sum(m.message_count for m in self.stream_metrics.values())
            total_memory = sum(m.memory_usage_bytes for m in self.stream_metrics.values())
            
            metrics = {
                "total_streams": len(self.stream_metrics),
                "total_consumers": len(self.consumers),
                "total_messages": total_messages,
                "total_memory_bytes": total_memory,
                "streams": {},
                "consumers": {}
            }
            
            # Stream metrics
            for stream_name, stream_metrics in self.stream_metrics.items():
                metrics["streams"][stream_name] = {
                    "message_count": stream_metrics.message_count,
                    "consumer_groups": stream_metrics.consumer_groups,
                    "pending_messages": stream_metrics.pending_messages,
                    "memory_usage_bytes": stream_metrics.memory_usage_bytes,
                    "last_entry_id": stream_metrics.last_entry_id,
                    "throughput_per_sec": stream_metrics.throughput_per_sec,
                    "avg_processing_time_ms": stream_metrics.avg_processing_time_ms
                }
            
            # Consumer metrics
            for consumer_name, consumer in self.consumers.items():
                metrics["consumers"][consumer_name] = {
                    "state": consumer.state.value,
                    "messages_processed": consumer.metrics.messages_processed,
                    "messages_failed": consumer.metrics.messages_failed,
                    "avg_processing_time_ms": consumer.metrics.avg_processing_time_ms,
                    "streams": consumer.config.streams
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting coordinator metrics: {e}")
            return {"error": str(e)}


# Export public API
__all__ = [
    "RedisStreamsCoordinator", "RedisStreamConsumer", "ConsumerGroupConfig",
    "RedisStreamMessage", "AinflueBusinesRedisStreams", "StreamMetrics",
    "ConsumerGroupMetrics", "StreamReadMode", "ConsumerGroupState"
]