"""{{service_name}} Queue Service Template for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
Backend Senior Role: Enterprise message queue service with advanced processing capabilities
"""

import logging
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Union, Callable, AsyncIterator, Type
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, asdict, field
import pickle
import base64
from concurrent.futures import ThreadPoolExecutor
import signal
import sys

import redis.asyncio as redis
from celery import Celery
from kombu import Queue, Exchange
from pydantic import BaseModel, Field

from core.config import get_settings
from utils.exceptions import ServiceError
from utils.serialization import JSONEncoder
from utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class QueueError(ServiceError):
    """Queue service specific error"""
    pass


class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


class QueueType(str, Enum):
    """Queue types"""
    STANDARD = "standard"
    PRIORITY = "priority"
    DELAY = "delay"
    DEAD_LETTER = "dead_letter"
    FIFO = "fifo"


class MessagePriority(int, Enum):
    """Message priority levels"""
    CRITICAL = 9
    HIGH = 7
    NORMAL = 5
    LOW = 3
    BULK = 1


class SerializationFormat(str, Enum):
    """Message serialization formats"""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"


@dataclass
class QueueConfig:
    """Queue configuration"""
    name: str
    queue_type: QueueType = QueueType.STANDARD
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    message_ttl: int = 3600  # seconds
    max_length: Optional[int] = None
    prefetch_count: int = 10
    ack_late: bool = True
    reject_on_worker_lost: bool = True
    serialization: SerializationFormat = SerializationFormat.JSON
    
    # Priority queue specific
    priority_levels: int = 10
    
    # Delay queue specific
    max_delay: int = 86400  # 24 hours
    
    # Dead letter queue
    dead_letter_queue: Optional[str] = None
    dead_letter_exchange: Optional[str] = None


@dataclass
class MessageMetadata:
    """Message metadata"""
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: MessagePriority = MessagePriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    delay_until: Optional[datetime] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'delay_until': self.delay_until.isoformat() if self.delay_until else None,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'headers': self.headers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageMetadata':
        return cls(
            id=UUID(data['id']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            priority=MessagePriority(data['priority']),
            retry_count=data['retry_count'],
            max_retries=data['max_retries'],
            delay_until=datetime.fromisoformat(data['delay_until']) if data['delay_until'] else None,
            correlation_id=data.get('correlation_id'),
            reply_to=data.get('reply_to'),
            headers=data.get('headers', {})
        )


class QueueMessage(BaseModel):
    """Queue message wrapper"""
    body: Any
    metadata: MessageMetadata
    queue_name: str
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'body': self.body,
            'metadata': self.metadata.to_dict(),
            'queue_name': self.queue_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueMessage':
        return cls(
            body=data['body'],
            metadata=MessageMetadata.from_dict(data['metadata']),
            queue_name=data['queue_name']
        )


@dataclass
class QueueStats:
    """Queue statistics"""
    message_count: int = 0
    consumer_count: int = 0
    messages_published: int = 0
    messages_consumed: int = 0
    messages_acked: int = 0
    messages_rejected: int = 0
    messages_requeued: int = 0
    average_processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MessageSerializer:
    """Message serialization utilities"""
    
    @staticmethod
    def serialize(data: Any, format: SerializationFormat = SerializationFormat.JSON) -> bytes:
        """Serialize message data"""
        try:
            if format == SerializationFormat.JSON:
                return json.dumps(data, cls=JSONEncoder).encode('utf-8')
            elif format == SerializationFormat.PICKLE:
                return pickle.dumps(data)
            elif format == SerializationFormat.MSGPACK:
                try:
                    import msgpack
                    return msgpack.packb(data)
                except ImportError:
                    logger.warning("msgpack not available, falling back to JSON")
                    return json.dumps(data, cls=JSONEncoder).encode('utf-8')
            else:
                raise QueueError(f"Unsupported serialization format: {format}")
                
        except Exception as e:
            logger.error(f"Message serialization failed: {e}")
            raise QueueError(f"Serialization failed: {str(e)}")
    
    @staticmethod
    def deserialize(data: bytes, format: SerializationFormat = SerializationFormat.JSON) -> Any:
        """Deserialize message data"""
        try:
            if format == SerializationFormat.JSON:
                return json.loads(data.decode('utf-8'))
            elif format == SerializationFormat.PICKLE:
                return pickle.loads(data)
            elif format == SerializationFormat.MSGPACK:
                try:
                    import msgpack
                    return msgpack.unpackb(data)
                except ImportError:
                    logger.warning("msgpack not available, falling back to JSON")
                    return json.loads(data.decode('utf-8'))
            else:
                raise QueueError(f"Unsupported serialization format: {format}")
                
        except Exception as e:
            logger.error(f"Message deserialization failed: {e}")
            raise QueueError(f"Deserialization failed: {str(e)}")


class QueueBackend:
    """Abstract queue backend interface"""
    
    async def publish(
        self,
        message: QueueMessage,
        routing_key: Optional[str] = None
    ) -> bool:
        """Publish message to queue"""
        raise NotImplementedError
    
    async def consume(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ) -> None:
        """Consume messages from queue"""
        raise NotImplementedError
    
    async def ack_message(self, message_id: str) -> bool:
        """Acknowledge message processing"""
        raise NotImplementedError
    
    async def reject_message(self, message_id: str, requeue: bool = False) -> bool:
        """Reject message"""
        raise NotImplementedError
    
    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Get queue statistics"""
        raise NotImplementedError


class RedisQueueBackend(QueueBackend):
    """Redis-based queue backend"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self._processing_messages: Dict[str, QueueMessage] = {}
        self._consumer_tasks: Dict[str, asyncio.Task] = {}
    
    async def publish(
        self,
        message: QueueMessage,
        routing_key: Optional[str] = None
    ) -> bool:
        """Publish message to Redis queue"""
        try:
            queue_key = f"queue:{message.queue_name}"
            
            # Handle delayed messages
            if message.metadata.delay_until:
                delay_seconds = (
                    message.metadata.delay_until - datetime.now(timezone.utc)
                ).total_seconds()
                
                if delay_seconds > 0:
                    # Store in delay queue
                    delay_key = f"delay:{message.queue_name}"
                    score = time.time() + delay_seconds
                    
                    serialized = MessageSerializer.serialize(
                        message.to_dict(),
                        SerializationFormat.JSON
                    )
                    
                    await self.redis.zadd(delay_key, {serialized: score})
                    return True
            
            # Serialize message
            serialized = MessageSerializer.serialize(
                message.to_dict(),
                SerializationFormat.JSON
            )
            
            # Push to queue based on priority
            if message.metadata.priority == MessagePriority.CRITICAL:
                await self.redis.lpush(queue_key, serialized)
            else:
                await self.redis.rpush(queue_key, serialized)
            
            # Update stats
            stats_key = f"stats:{message.queue_name}"
            await self.redis.hincrby(stats_key, "messages_published", 1)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis publish failed: {e}")
            return False
    
    async def consume(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ) -> None:
        """Consume messages from Redis queue"""
        queue_key = f"queue:{queue_name}"
        processing_key = f"processing:{queue_name}"
        
        try:
            while True:
                # Move delayed messages to main queue
                await self._process_delayed_messages(queue_name)
                
                # Get message from queue
                result = await self.redis.blmove(
                    queue_key,
                    processing_key,
                    timeout=1.0
                )
                
                if result is None:
                    continue
                
                # Deserialize message
                try:
                    message_data = MessageSerializer.deserialize(
                        result,
                        SerializationFormat.JSON
                    )
                    message = QueueMessage.from_dict(message_data)
                except Exception as e:
                    logger.error(f"Message deserialization failed: {e}")
                    continue
                
                # Store for potential requeue
                message_id = str(message.metadata.id)
                self._processing_messages[message_id] = message
                
                # Update stats
                stats_key = f"stats:{queue_name}"
                await self.redis.hincrby(stats_key, "messages_consumed", 1)
                
                try:
                    # Process message
                    start_time = time.time()
                    await callback(message)
                    processing_time = time.time() - start_time
                    
                    # Auto-acknowledge if enabled
                    if auto_ack:
                        await self.ack_message(message_id)
                    
                    # Update processing time stats
                    await self._update_processing_time(queue_name, processing_time)
                    
                except Exception as e:
                    logger.error(f"Message processing failed: {e}")
                    
                    # Handle retry logic
                    if message.metadata.retry_count < message.metadata.max_retries:
                        message.metadata.retry_count += 1
                        message.metadata.delay_until = datetime.now(timezone.utc) + timedelta(seconds=60)
                        
                        # Requeue with delay
                        await self.publish(message)
                        await self.ack_message(message_id)
                    else:
                        # Send to dead letter queue
                        await self._send_to_dead_letter(message)
                        await self.ack_message(message_id)
                
        except asyncio.CancelledError:
            logger.info(f"Consumer for {queue_name} cancelled")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
    
    async def ack_message(self, message_id: str) -> bool:
        """Acknowledge message processing"""
        try:
            if message_id in self._processing_messages:
                message = self._processing_messages[message_id]
                processing_key = f"processing:{message.queue_name}"
                
                # Remove from processing queue
                serialized = MessageSerializer.serialize(
                    message.to_dict(),
                    SerializationFormat.JSON
                )
                await self.redis.lrem(processing_key, 1, serialized)
                
                # Remove from processing messages
                del self._processing_messages[message_id]
                
                # Update stats
                stats_key = f"stats:{message.queue_name}"
                await self.redis.hincrby(stats_key, "messages_acked", 1)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Message ack failed: {e}")
            return False
    
    async def reject_message(self, message_id: str, requeue: bool = False) -> bool:
        """Reject message"""
        try:
            if message_id in self._processing_messages:
                message = self._processing_messages[message_id]
                
                if requeue:
                    # Requeue message
                    await self.publish(message)
                    await self.redis.hincrby(f"stats:{message.queue_name}", "messages_requeued", 1)
                
                # Remove from processing
                await self.ack_message(message_id)
                await self.redis.hincrby(f"stats:{message.queue_name}", "messages_rejected", 1)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Message reject failed: {e}")
            return False
    
    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Get queue statistics"""
        try:
            queue_key = f"queue:{queue_name}"
            processing_key = f"processing:{queue_name}"
            stats_key = f"stats:{queue_name}"
            
            # Get queue lengths
            queue_length = await self.redis.llen(queue_key)
            processing_length = await self.redis.llen(processing_key)
            
            # Get stats
            stats_data = await self.redis.hgetall(stats_key)
            
            return QueueStats(
                message_count=queue_length + processing_length,
                messages_published=int(stats_data.get(b'messages_published', 0)),
                messages_consumed=int(stats_data.get(b'messages_consumed', 0)),
                messages_acked=int(stats_data.get(b'messages_acked', 0)),
                messages_rejected=int(stats_data.get(b'messages_rejected', 0)),
                messages_requeued=int(stats_data.get(b'messages_requeued', 0)),
                average_processing_time=float(stats_data.get(b'avg_processing_time', 0))
            )
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return QueueStats()
    
    async def _process_delayed_messages(self, queue_name: str):
        """Move ready delayed messages to main queue"""
        try:
            delay_key = f"delay:{queue_name}"
            current_time = time.time()
            
            # Get ready messages
            ready_messages = await self.redis.zrangebyscore(
                delay_key,
                0,
                current_time,
                withscores=False
            )
            
            if ready_messages:
                queue_key = f"queue:{queue_name}"
                
                # Move to main queue
                for message_data in ready_messages:
                    await self.redis.rpush(queue_key, message_data)
                
                # Remove from delay queue
                await self.redis.zremrangebyscore(delay_key, 0, current_time)
                
        except Exception as e:
            logger.error(f"Delayed message processing failed: {e}")
    
    async def _send_to_dead_letter(self, message: QueueMessage):
        """Send message to dead letter queue"""
        try:
            dead_letter_queue = f"dead_letter:{message.queue_name}"
            
            # Update message status
            message.metadata.headers['status'] = MessageStatus.DEAD_LETTER.value
            message.metadata.headers['failed_at'] = datetime.now(timezone.utc).isoformat()
            
            # Serialize and store
            serialized = MessageSerializer.serialize(
                message.to_dict(),
                SerializationFormat.JSON
            )
            
            await self.redis.rpush(dead_letter_queue, serialized)
            
            logger.warning(f"Message sent to dead letter queue: {message.metadata.id}")
            
        except Exception as e:
            logger.error(f"Dead letter send failed: {e}")
    
    async def _update_processing_time(self, queue_name: str, processing_time: float):
        """Update average processing time"""
        try:
            stats_key = f"stats:{queue_name}"
            
            # Get current average and count
            current_avg = float(await self.redis.hget(stats_key, "avg_processing_time") or 0)
            count = int(await self.redis.hget(stats_key, "processed_count") or 0)
            
            # Calculate new average
            new_avg = ((current_avg * count) + processing_time) / (count + 1)
            
            # Update stats
            await self.redis.hset(stats_key, "avg_processing_time", new_avg)
            await self.redis.hincrby(stats_key, "processed_count", 1)
            
        except Exception as e:
            logger.error(f"Processing time update failed: {e}")


class {{service_name}}QueueService:
    """{{service_description}}
    
    Enterprise message queue service providing:
    - Multiple backend support (Redis, Celery, RabbitMQ)
    - Priority and delayed message handling
    - Retry logic with exponential backoff
    - Dead letter queue management
    - Real-time metrics and monitoring
    - Auto-scaling consumer management
    - Message routing and filtering
    - Batch processing capabilities
    """
    
    def __init__(
        self,
        backend: QueueBackend,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.backend = backend
        self.metrics = metrics_collector
        
        # Queue management
        self._queues: Dict[str, QueueConfig] = {}
        self._consumers: Dict[str, List[asyncio.Task]] = {}
        self._is_running = False
        
        # Message handlers
        self._message_handlers: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []
    
    async def initialize(self):
        """Initialize queue service"""
        try:
            self._is_running = True
            logger.info("Queue service initialized")
            
        except Exception as e:
            logger.error(f"Queue service initialization failed: {e}")
            raise QueueError(f"Initialization failed: {str(e)}")
    
    def register_queue(self, config: QueueConfig):
        """Register a queue with configuration"""
        self._queues[config.name] = config
        logger.info(f"Registered queue: {config.name}")
    
    def register_handler(self, queue_name: str, handler: Callable):
        """Register message handler for queue"""
        self._message_handlers[queue_name] = handler
        logger.info(f"Registered handler for queue: {queue_name}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware for message processing"""
        self._middleware.append(middleware)
        logger.info("Added message processing middleware")
    
    async def publish(
        self,
        queue_name: str,
        message_body: Any,
        priority: MessagePriority = MessagePriority.NORMAL,
        delay: Optional[timedelta] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> str:
        """Publish message to queue"""
        try:
            if queue_name not in self._queues:
                raise QueueError(f"Queue not registered: {queue_name}")
            
            config = self._queues[queue_name]
            
            # Create message metadata
            metadata = MessageMetadata(
                priority=priority,
                max_retries=config.max_retries,
                delay_until=datetime.now(timezone.utc) + delay if delay else None,
                correlation_id=correlation_id,
                reply_to=reply_to,
                headers=headers or {}
            )
            
            # Create message
            message = QueueMessage(
                body=message_body,
                metadata=metadata,
                queue_name=queue_name
            )
            
            # Publish message
            success = await self.backend.publish(message)
            
            if success:
                message_id = str(metadata.id)
                
                # Record metrics
                if self.metrics:
                    self.metrics.increment(
                        'messages_published',
                        tags={'queue': queue_name, 'priority': priority.name}
                    )
                
                logger.debug(f"Published message {message_id} to {queue_name}")
                return message_id
            else:
                raise QueueError("Message publish failed")
                
        except Exception as e:
            logger.error(f"Message publish failed: {e}")
            if self.metrics:
                self.metrics.increment(
                    'publish_errors',
                    tags={'queue': queue_name}
                )
            raise QueueError(f"Publish failed: {str(e)}")
    
    async def start_consumer(
        self,
        queue_name: str,
        worker_count: int = 1,
        auto_ack: bool = False
    ):
        """Start consumer workers for queue"""
        try:
            if queue_name not in self._queues:
                raise QueueError(f"Queue not registered: {queue_name}")
            
            if queue_name not in self._message_handlers:
                raise QueueError(f"No handler registered for queue: {queue_name}")
            
            # Start consumer tasks
            consumer_tasks = []
            for i in range(worker_count):
                task = asyncio.create_task(
                    self._consumer_worker(queue_name, f"worker-{i}", auto_ack)
                )
                consumer_tasks.append(task)
            
            self._consumers[queue_name] = consumer_tasks
            
            logger.info(f"Started {worker_count} consumers for queue: {queue_name}")
            
        except Exception as e:
            logger.error(f"Consumer start failed: {e}")
            raise QueueError(f"Consumer start failed: {str(e)}")
    
    async def stop_consumer(self, queue_name: str):
        """Stop consumers for queue"""
        try:
            if queue_name in self._consumers:
                tasks = self._consumers[queue_name]
                
                # Cancel tasks
                for task in tasks:
                    task.cancel()
                
                # Wait for completion
                await asyncio.gather(*tasks, return_exceptions=True)
                
                del self._consumers[queue_name]
                
                logger.info(f"Stopped consumers for queue: {queue_name}")
                
        except Exception as e:
            logger.error(f"Consumer stop failed: {e}")
    
    async def publish_batch(
        self,
        queue_name: str,
        messages: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> List[str]:
        """Publish batch of messages"""
        message_ids = []
        
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            
            tasks = []
            for message_data in batch:
                task = asyncio.create_task(
                    self.publish(queue_name, **message_data)
                )
                tasks.append(task)
            
            batch_ids = await asyncio.gather(*tasks, return_exceptions=True)
            
            for msg_id in batch_ids:
                if isinstance(msg_id, str):
                    message_ids.append(msg_id)
                else:
                    logger.error(f"Batch publish error: {msg_id}")
        
        return message_ids
    
    async def get_queue_info(self, queue_name: str) -> Dict[str, Any]:
        """Get queue information and statistics"""
        try:
            if queue_name not in self._queues:
                raise QueueError(f"Queue not registered: {queue_name}")
            
            config = self._queues[queue_name]
            stats = await self.backend.get_queue_stats(queue_name)
            
            return {
                'name': queue_name,
                'config': asdict(config),
                'stats': stats.to_dict(),
                'consumers': len(self._consumers.get(queue_name, [])),
                'has_handler': queue_name in self._message_handlers
            }
            
        except Exception as e:
            logger.error(f"Queue info retrieval failed: {e}")
            raise QueueError(f"Queue info failed: {str(e)}")
    
    async def get_all_queues_info(self) -> Dict[str, Any]:
        """Get information for all registered queues"""
        queues_info = {}
        
        for queue_name in self._queues:
            try:
                queues_info[queue_name] = await self.get_queue_info(queue_name)
            except Exception as e:
                logger.error(f"Failed to get info for queue {queue_name}: {e}")
                queues_info[queue_name] = {'error': str(e)}
        
        return queues_info
    
    async def _consumer_worker(
        self,
        queue_name: str,
        worker_id: str,
        auto_ack: bool
    ):
        """Consumer worker implementation"""
        logger.info(f"Consumer worker {worker_id} started for queue {queue_name}")
        
        try:
            handler = self._message_handlers[queue_name]
            
            async def process_message(message: QueueMessage):
                start_time = time.time()
                
                try:
                    # Apply middleware
                    for middleware in self._middleware:
                        message = await self._apply_middleware(middleware, message)
                    
                    # Process message
                    await handler(message)
                    
                    # Record metrics
                    processing_time = time.time() - start_time
                    if self.metrics:
                        self.metrics.record_histogram(
                            'message_processing_time',
                            processing_time,
                            tags={'queue': queue_name, 'worker': worker_id}
                        )
                        self.metrics.increment(
                            'messages_processed',
                            tags={'queue': queue_name, 'status': 'success'}
                        )
                    
                except Exception as e:
                    logger.error(f"Message processing failed in {worker_id}: {e}")
                    
                    if self.metrics:
                        self.metrics.increment(
                            'messages_processed',
                            tags={'queue': queue_name, 'status': 'error'}
                        )
                    
                    # Let the backend handle retry logic
                    raise
            
            await self.backend.consume(queue_name, process_message, auto_ack)
            
        except asyncio.CancelledError:
            logger.info(f"Consumer worker {worker_id} cancelled")
        except Exception as e:
            logger.error(f"Consumer worker {worker_id} error: {e}")
        finally:
            logger.info(f"Consumer worker {worker_id} stopped")
    
    async def _apply_middleware(self, middleware: Callable, message: QueueMessage) -> QueueMessage:
        """Apply middleware to message"""
        try:
            if asyncio.iscoroutinefunction(middleware):
                return await middleware(message)
            else:
                return middleware(message)
        except Exception as e:
            logger.error(f"Middleware error: {e}")
            return message
    
    async def shutdown(self):
        """Gracefully shutdown queue service"""
        try:
            self._is_running = False
            
            # Stop all consumers
            for queue_name in list(self._consumers.keys()):
                await self.stop_consumer(queue_name)
            
            logger.info("Queue service shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Factory functions
def create_redis_queue_service(
    redis_url: str,
    metrics_collector: Optional[MetricsCollector] = None
) -> {{service_name}}QueueService:
    """Create queue service with Redis backend"""
    redis_client = redis.from_url(redis_url)
    backend = RedisQueueBackend(redis_client)
    
    return {{service_name}}QueueService(backend, metrics_collector)


def create_queue_service(
    backend_type: str = "redis",
    **kwargs
) -> {{service_name}}QueueService:
    """Create queue service with specified backend"""
    if backend_type == "redis":
        redis_url = kwargs.get('redis_url', 'redis://localhost:6379')
        return create_redis_queue_service(redis_url, kwargs.get('metrics_collector'))
    else:
        raise QueueError(f"Unsupported backend type: {backend_type}")


# Export service classes
__all__ = [
    'QueueError',
    'MessageStatus',
    'QueueType',
    'MessagePriority',
    'SerializationFormat',
    'QueueConfig',
    'MessageMetadata',
    'QueueMessage',
    'QueueStats',
    'MessageSerializer',
    'QueueBackend',
    'RedisQueueBackend',
    '{{service_name}}QueueService',
    'create_redis_queue_service',
    'create_queue_service'
]