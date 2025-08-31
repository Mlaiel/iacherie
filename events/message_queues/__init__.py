"""IA Influencer Agent - Message Queues Module
Enterprise-grade Message Queue System

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.0.0

⚠️ LEGAL WARNING: Unauthorized use prohibited. See __init__.py for full notice.
"""
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from asyncio import Queue, Event, Task, create_task, sleep, wait_for
import asyncio
import json
import logging
from enum import Enum
from uuid import uuid4
import pickle
import hashlib

from ..core.exceptions import MessageQueueError
from ..core.redis import RedisManager
from ..core.database import DatabaseManager
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class MessageStatus(Enum):
    """Message processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


@dataclass
class QueueMessage:
    """Message in a queue"""    
    message_id: str
    queue_name: str
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid4())
    
    def is_expired(self) -> bool:
        """Check if message is expired"""        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False
    
    def should_process_now(self) -> bool:
        """Check if message should be processed now"""        if self.scheduled_at:
            return datetime.now(timezone.utc) >= self.scheduled_at
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""        return {
            "message_id": self.message_id,
            "queue_name": self.queue_name,
            "payload": self.payload,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status.value,
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to,
            "headers": self.headers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueueMessage":
        """Create message from dictionary"""        return cls(
            message_id=data["message_id"],
            queue_name=data["queue_name"],
            payload=data["payload"],
            priority=MessagePriority(data["priority"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
            status=MessageStatus(data["status"]),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to"),
            headers=data.get("headers", {})
        )


class MessageQueue(ABC):
    """Abstract base class for message queues"""    
    @abstractmethod
    async def enqueue(self, message: QueueMessage) -> str:
        """Add message to queue"""        pass
    
    @abstractmethod
    async def dequeue(self, timeout: Optional[int] = None) -> Optional[QueueMessage]:
        """Remove and return message from queue"""        pass
    
    @abstractmethod
    async def peek(self) -> Optional[QueueMessage]:
        """Peek at next message without removing it"""        pass
    
    @abstractmethod
    async def ack(self, message_id: str) -> bool:
        """Acknowledge message processing"""        pass
    
    @abstractmethod
    async def nack(self, message_id: str, requeue: bool = True) -> bool:
        """Negative acknowledge - message processing failed"""        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get queue size"""        pass
    
    @abstractmethod
    async def purge(self) -> int:
        """Remove all messages from queue"""        pass


class RedisMessageQueue(MessageQueue):
    """Redis-based message queue implementation"""    
    def __init__(self, queue_name: str, redis_manager: RedisManager,
                 encryption_manager: EncryptionManager,
                 metrics_collector: MetricsCollector):
        self.queue_name = queue_name
        self.redis = redis_manager
        self.encryption = encryption_manager
        self.metrics = metrics_collector
        
        # Redis keys
        self.pending_key = f"queue:{queue_name}:pending"
        self.processing_key = f"queue:{queue_name}:processing"
        self.scheduled_key = f"queue:{queue_name}:scheduled"
        self.dead_letter_key = f"queue:{queue_name}:dead_letter"
        self.stats_key = f"queue:{queue_name}:stats"
    
    async def enqueue(self, message: QueueMessage) -> str:
        """Add message to Redis queue with priority support"""        try:
            # Encrypt message payload
            encrypted_payload = await self.encryption.encrypt_data(
                json.dumps(message.payload)
            )
            
            # Create message data
            message_data = message.to_dict()
            message_data["payload"] = encrypted_payload
            
            # Serialize message
            serialized_message = json.dumps(message_data)
            
            # Add to appropriate queue based on scheduling
            if message.scheduled_at and message.scheduled_at > datetime.now(timezone.utc):
                # Scheduled message - add to scheduled set with timestamp score
                timestamp = message.scheduled_at.timestamp()
                await self.redis.zadd(self.scheduled_key, {message.message_id: timestamp})
                await self.redis.hset(f"message:{message.message_id}", mapping={
                    "data": serialized_message
                })
            else:
                # Immediate message - add to priority queue
                priority_score = message.priority.value
                await self.redis.zadd(self.pending_key, {message.message_id: priority_score})
                await self.redis.hset(f"message:{message.message_id}", mapping={
                    "data": serialized_message
                })
            
            # Update stats
            await self.redis.hincrby(self.stats_key, "total_enqueued", 1)
            self.metrics.increment_counter("queue_messages_enqueued", 
                                         tags={"queue": self.queue_name})
            
            logger.debug(f"Enqueued message {message.message_id} to queue {self.queue_name}")
            return message.message_id
            
        except Exception as e:
            self.metrics.increment_counter("queue_enqueue_errors",
                                         tags={"queue": self.queue_name})
            logger.error(f"Error enqueueing message: {str(e)}")
            raise MessageQueueError(f"Failed to enqueue message: {str(e)}")
    
    async def dequeue(self, timeout: Optional[int] = None) -> Optional[QueueMessage]:
        """Dequeue message with timeout support"""        try:
            # Move scheduled messages that are ready
            await self._process_scheduled_messages()
            
            # Get highest priority message
            if timeout:
                # Blocking pop with timeout
                result = await self.redis.bzpopmin(self.pending_key, timeout=timeout)
                if not result:
                    return None
                _, message_id, _ = result
            else:
                # Non-blocking pop
                result = await self.redis.zpopmin(self.pending_key)
                if not result:
                    return None
                message_id, _ = result[0]
            
            message_id = message_id.decode() if isinstance(message_id, bytes) else message_id
            
            # Get message data
            message_data = await self.redis.hget(f"message:{message_id}", "data")
            if not message_data:
                logger.warning(f"Message data not found for {message_id}")
                return None
            
            # Parse and decrypt message
            parsed_data = json.loads(message_data)
            
            # Decrypt payload
            encrypted_payload = parsed_data["payload"]
            decrypted_payload = await self.encryption.decrypt_data(encrypted_payload)
            parsed_data["payload"] = json.loads(decrypted_payload)
            
            message = QueueMessage.from_dict(parsed_data)
            message.status = MessageStatus.PROCESSING
            
            # Move to processing queue
            await self.redis.zadd(self.processing_key, {message_id: datetime.now().timestamp()})
            
            # Update stats
            await self.redis.hincrby(self.stats_key, "total_dequeued", 1)
            self.metrics.increment_counter("queue_messages_dequeued",
                                         tags={"queue": self.queue_name})
            
            logger.debug(f"Dequeued message {message_id} from queue {self.queue_name}")
            return message
            
        except Exception as e:
            self.metrics.increment_counter("queue_dequeue_errors",
                                         tags={"queue": self.queue_name})
            logger.error(f"Error dequeuing message: {str(e)}")
            raise MessageQueueError(f"Failed to dequeue message: {str(e)}")
    
    async def peek(self) -> Optional[QueueMessage]:
        """Peek at next message without removing it"""        try:
            await self._process_scheduled_messages()
            
            # Get highest priority message without removing
            result = await self.redis.zrange(self.pending_key, 0, 0, withscores=True)
            if not result:
                return None
            
            message_id, _ = result[0]
            message_id = message_id.decode() if isinstance(message_id, bytes) else message_id
            
            # Get message data
            message_data = await self.redis.hget(f"message:{message_id}", "data")
            if not message_data:
                return None
            
            # Parse and decrypt message
            parsed_data = json.loads(message_data)
            encrypted_payload = parsed_data["payload"]
            decrypted_payload = await self.encryption.decrypt_data(encrypted_payload)
            parsed_data["payload"] = json.loads(decrypted_payload)
            
            return QueueMessage.from_dict(parsed_data)
            
        except Exception as e:
            logger.error(f"Error peeking message: {str(e)}")
            return None
    
    async def ack(self, message_id: str) -> bool:
        """Acknowledge successful message processing"""        try:
            # Remove from processing queue
            removed = await self.redis.zrem(self.processing_key, message_id)
            
            # Delete message data
            await self.redis.delete(f"message:{message_id}")
            
            # Update stats
            if removed:
                await self.redis.hincrby(self.stats_key, "total_acked", 1)
                self.metrics.increment_counter("queue_messages_acked",
                                             tags={"queue": self.queue_name})
            
            logger.debug(f"Acknowledged message {message_id}")
            return bool(removed)
            
        except Exception as e:
            logger.error(f"Error acknowledging message {message_id}: {str(e)}")
            return False
    
    async def nack(self, message_id: str, requeue: bool = True) -> bool:
        """Negative acknowledge - handle failed message"""        try:
            # Get message from processing queue
            score = await self.redis.zscore(self.processing_key, message_id)
            if score is None:
                return False
            
            # Remove from processing
            await self.redis.zrem(self.processing_key, message_id)
            
            if requeue:
                # Get message data to check retry count
                message_data = await self.redis.hget(f"message:{message_id}", "data")
                if message_data:
                    parsed_data = json.loads(message_data)
                    retry_count = parsed_data.get("retry_count", 0)
                    max_retries = parsed_data.get("max_retries", 3)
                    
                    if retry_count < max_retries:
                        # Increment retry count and requeue
                        parsed_data["retry_count"] = retry_count + 1
                        parsed_data["status"] = MessageStatus.RETRY.value
                        
                        updated_data = json.dumps(parsed_data)
                        await self.redis.hset(f"message:{message_id}", "data", updated_data)
                        
                        # Add back to pending queue with lower priority (higher number)
                        priority = parsed_data.get("priority", MessagePriority.NORMAL.value)
                        await self.redis.zadd(self.pending_key, {message_id: priority + 10})
                        
                        await self.redis.hincrby(self.stats_key, "total_retried", 1)
                        self.metrics.increment_counter("queue_messages_retried",
                                                     tags={"queue": self.queue_name})
                    else:
                        # Move to dead letter queue
                        await self.redis.zadd(self.dead_letter_key, 
                                            {message_id: datetime.now().timestamp()})
                        
                        await self.redis.hincrby(self.stats_key, "total_dead_letter", 1)
                        self.metrics.increment_counter("queue_messages_dead_letter",
                                                     tags={"queue": self.queue_name})
            else:
                # Delete message completely
                await self.redis.delete(f"message:{message_id}")
            
            await self.redis.hincrby(self.stats_key, "total_nacked", 1)
            self.metrics.increment_counter("queue_messages_nacked",
                                         tags={"queue": self.queue_name})
            
            logger.debug(f"Negative acknowledged message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error nacking message {message_id}: {str(e)}")
            return False
    
    async def size(self) -> int:
        """Get total queue size"""        try:
            pending_size = await self.redis.zcard(self.pending_key)
            processing_size = await self.redis.zcard(self.processing_key)
            scheduled_size = await self.redis.zcard(self.scheduled_key)
            
            return pending_size + processing_size + scheduled_size
            
        except Exception as e:
            logger.error(f"Error getting queue size: {str(e)}")
            return 0
    
    async def purge(self) -> int:
        """Remove all messages from queue"""        try:
            # Get all message IDs
            pending_ids = await self.redis.zrange(self.pending_key, 0, -1)
            processing_ids = await self.redis.zrange(self.processing_key, 0, -1)
            scheduled_ids = await self.redis.zrange(self.scheduled_key, 0, -1)
            dead_letter_ids = await self.redis.zrange(self.dead_letter_key, 0, -1)
            
            all_ids = set(pending_ids + processing_ids + scheduled_ids + dead_letter_ids)
            
            # Delete message data
            if all_ids:
                message_keys = [f"message:{msg_id}" for msg_id in all_ids]
                await self.redis.delete(*message_keys)
            
            # Clear all queues
            deleted_count = len(all_ids)
            await self.redis.delete(
                self.pending_key, self.processing_key, 
                self.scheduled_key, self.dead_letter_key
            )
            
            # Reset stats
            await self.redis.delete(self.stats_key)
            
            logger.info(f"Purged {deleted_count} messages from queue {self.queue_name}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error purging queue: {str(e)}")
            return 0
    
    async def _process_scheduled_messages(self):
        """Move ready scheduled messages to pending queue"""        try:
            current_time = datetime.now(timezone.utc).timestamp()
            
            # Get messages that are ready to be processed
            ready_messages = await self.redis.zrangebyscore(
                self.scheduled_key, 0, current_time
            )
            
            if ready_messages:
                # Move to pending queue
                pipeline = self.redis.pipeline()
                
                for message_id in ready_messages:
                    message_id = message_id.decode() if isinstance(message_id, bytes) else message_id
                    
                    # Get message data to determine priority
                    message_data = await self.redis.hget(f"message:{message_id}", "data")
                    if message_data:
                        parsed_data = json.loads(message_data)
                        priority = parsed_data.get("priority", MessagePriority.NORMAL.value)
                        
                        # Add to pending and remove from scheduled
                        pipeline.zadd(self.pending_key, {message_id: priority})
                        pipeline.zrem(self.scheduled_key, message_id)
                
                await pipeline.execute()
                
                logger.debug(f"Moved {len(ready_messages)} scheduled messages to pending")
                
        except Exception as e:
            logger.error(f"Error processing scheduled messages: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""        try:
            stats = await self.redis.hgetall(self.stats_key)
            
            # Convert byte keys/values to strings/integers
            converted_stats = {}
            for key, value in stats.items():
                key_str = key.decode() if isinstance(key, bytes) else key
                value_int = int(value.decode() if isinstance(value, bytes) else value)
                converted_stats[key_str] = value_int
            
            # Add current queue sizes
            converted_stats.update({
                "pending_size": await self.redis.zcard(self.pending_key),
                "processing_size": await self.redis.zcard(self.processing_key),
                "scheduled_size": await self.redis.zcard(self.scheduled_key),
                "dead_letter_size": await self.redis.zcard(self.dead_letter_key)
            })
            
            return converted_stats
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {str(e)}")
            return {}


class QueueProcessor:
    """Process messages from a queue with configurable workers"""    
    def __init__(self, queue: MessageQueue, worker_count: int = 1):
        self.queue = queue
        self.worker_count = worker_count
        self._running = False
        self._workers: List[Task] = []
        self._handlers: Dict[str, Callable] = {}
        self._shutdown_event = Event()
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler for specific message type"""        self._handlers[message_type] = handler
    
    async def start(self):
        """Start processing messages"""        if self._running:
            return
        
        self._running = True
        self._shutdown_event.clear()
        
        # Start worker tasks
        for i in range(self.worker_count):
            worker_task = create_task(self._worker_loop(i))
            self._workers.append(worker_task)
        
        logger.info(f"Started queue processor with {self.worker_count} workers")
    
    async def stop(self, timeout: float = 30.0):
        """Stop processing messages gracefully"""        if not self._running:
            return
        
        self._running = False
        self._shutdown_event.set()
        
        # Wait for workers to finish
        if self._workers:
            try:
                await wait_for(
                    asyncio.gather(*self._workers, return_exceptions=True),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for workers to stop")
                
                # Cancel remaining workers
                for worker in self._workers:
                    if not worker.done():
                        worker.cancel()
        
        self._workers.clear()
        logger.info("Queue processor stopped")
    
    async def _worker_loop(self, worker_id: int):
        """Main worker loop"""        logger.info(f"Worker {worker_id} started")
        
        while self._running:
            try:
                # Get message from queue
                message = await self.queue.dequeue(timeout=1)
                if not message:
                    continue
                
                # Check if message is expired
                if message.is_expired():
                    await self.queue.ack(message.message_id)
                    logger.warning(f"Expired message {message.message_id} discarded")
                    continue
                
                # Process message
                await self._process_message(message, worker_id)
                
            except Exception as e:
                logger.error(f"Error in worker {worker_id}: {str(e)}")
                await sleep(1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _process_message(self, message: QueueMessage, worker_id: int):
        """Process a single message"""        try:
            # Determine message type from payload or headers
            message_type = (
                message.headers.get("message_type") or
                message.payload.get("type") or
                "default"
            )
            
            # Get handler for message type
            handler = self._handlers.get(message_type)
            if not handler:
                logger.warning(f"No handler for message type: {message_type}")
                await self.queue.ack(message.message_id)
                return
            
            # Execute handler
            result = await handler(message)
            
            # Handle response
            if message.reply_to and result:
                # Send response to reply queue
                reply_queue = RedisMessageQueue(
                    message.reply_to, 
                    self.queue.redis, 
                    self.queue.encryption,
                    self.queue.metrics
                )
                
                reply_message = QueueMessage(
                    message_id=str(uuid4()),
                    queue_name=message.reply_to,
                    payload=result,
                    correlation_id=message.correlation_id
                )
                
                await reply_queue.enqueue(reply_message)
            
            # Acknowledge successful processing
            await self.queue.ack(message.message_id)
            
            logger.debug(f"Worker {worker_id} processed message {message.message_id}")
            
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {str(e)}")
            
            # Negative acknowledge with retry
            await self.queue.nack(message.message_id, requeue=True)


class QueueManager:
    """Manage multiple message queues"""    
    def __init__(self, redis_manager: RedisManager,
                 encryption_manager: EncryptionManager,
                 metrics_collector: MetricsCollector):
        self.redis = redis_manager
        self.encryption = encryption_manager
        self.metrics = metrics_collector
        self._queues: Dict[str, RedisMessageQueue] = {}
        self._processors: Dict[str, QueueProcessor] = {}
    
    def create_queue(self, queue_name: str) -> RedisMessageQueue:
        """Create or get a message queue"""        if queue_name not in self._queues:
            self._queues[queue_name] = RedisMessageQueue(
                queue_name, self.redis, self.encryption, self.metrics
            )
        return self._queues[queue_name]
    
    def create_processor(self, queue_name: str, 
                        worker_count: int = 1) -> QueueProcessor:
        """Create a processor for a queue"""        queue = self.create_queue(queue_name)
        processor = QueueProcessor(queue, worker_count)
        self._processors[queue_name] = processor
        return processor
    
    async def start_all_processors(self):
        """Start all registered processors"""        for processor in self._processors.values():
            await processor.start()
    
    async def stop_all_processors(self):
        """Stop all processors"""        for processor in self._processors.values():
            await processor.stop()
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues"""        stats = {
            "total_queues": len(self._queues),
            "queue_stats": {}
        }
        
        for queue_name, queue in self._queues.items():
            stats["queue_stats"][queue_name] = await queue.get_stats()
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all queues"""        health = {
            "healthy": True,
            "queues": {}
        }
        
        for queue_name, queue in self._queues.items():
            try:
                # Test basic queue operations
                size = await queue.size()
                health["queues"][queue_name] = {
                    "healthy": True,
                    "size": size
                }
            except Exception as e:
                health["healthy"] = False
                health["queues"][queue_name] = {
                    "healthy": False,
                    "error": str(e)
                }
        
        return health


# Export public API
__all__ = [
    "QueueMessage", "MessagePriority", "MessageStatus",
    "MessageQueue", "RedisMessageQueue", "QueueProcessor", "QueueManager"
]
