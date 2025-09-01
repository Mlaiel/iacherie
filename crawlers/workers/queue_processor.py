"""Queue Processor Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/queue_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Queue Processing System
Responsibility: High-performance queue management and task distribution
Technologies: Redis, RabbitMQ, Priority Queues, Dead Letter Queues
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Queue ingestion → Priority analysis → Dead letter handling → 
Batch processing → Distribution optimization → Recovery mechanisms → Monitoring
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, Generic, TypeVar
import logging
import asyncio
import redis.asyncio as redis
import aioredis
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import pickle
from collections import defaultdict, deque
import heapq
from contextlib import asynccontextmanager
import msgpack
from abc import ABC, abstractmethod

from .crawler_worker import CrawlerTask, TaskPriority, TaskResult
from ...core.managers.queue_manager import ProductionQueueManager, QueueType
from ...monitoring.performance_monitor import PerformanceMonitor
from ...security.access_control import AccessControl
from ...utils.serialization_utils import SerializationUtils

logger = logging.getLogger(__name__)

T = TypeVar('T')


class QueueType(Enum):
    """
Queue types for different processing needs"""

    HIGH_PRIORITY = "high_priority"
    NORMAL_PRIORITY = "normal_priority"
    LOW_PRIORITY = "low_priority"
    BATCH_PROCESSING = "batch_processing"
    DEAD_LETTER = "dead_letter"
    RETRY = "retry"
    DELAYED = "delayed"
    BROADCAST = "broadcast"


class QueueStatus(Enum):
    """Queue processing status"""

    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"
    BLOCKED = "blocked"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ProcessingMode(Enum):
    """Queue processing modes"""

    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"
    BATCH = "batch"
    STREAMING = "streaming"
    ROUND_ROBIN = "round_robin"


@dataclass
class QueueConfig:
    """Queue configuration settings"""
    queue_name: str
    queue_type: QueueType
    processing_mode: ProcessingMode
    max_size: int = 10000
    batch_size: int = 10
    visibility_timeout: int = 300
    max_retries: int = 3
    dead_letter_threshold: int = 5
    compression_enabled: bool = True
    encryption_enabled: bool = False
    ttl_seconds: Optional[int] = None
    consumer_prefetch: int = 10
    auto_acknowledge: bool = False


@dataclass
class QueueMetrics:
    """
Queue performance metrics"""
    queue_name: str
    total_messages: int = 0
    pending_messages: int = 0
    processing_messages: int = 0
    completed_messages: int = 0
    failed_messages: int = 0
    dead_letter_messages: int = 0
    average_processing_time: float = 0.0
    throughput_per_second: float = 0.0
    error_rate: float = 0.0
    oldest_message_age: float = 0.0
    newest_message_age: float = 0.0
    consumer_count: int = 0
    last_activity: Optional[datetime] = None


@dataclass
class QueueMessage(Generic[T]):
    """
Queue message wrapper"""
    message_id: str
    queue_name: str
    payload: T
    priority: int = 0
    attempt_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None


class QueueProcessor:
    """
    High-performance queue processor for distributed task management
    
    Features:
    - Multiple queue types and priorities
    - Dead letter queue handling
    - Batch and streaming processing
    - Redis and RabbitMQ backends
    - Compression and encryption
    - Circuit breaker patterns
    """
    def __init__(self, config: QueueConfig, redis_url: str = "redis://localhost:6379"):
        self.config = config
        self.queue_name = config.queue_name
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        
        # Processing state
        self.status = QueueStatus.ACTIVE
        self.metrics = QueueMetrics(queue_name=self.queue_name)
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Message storage
        self.pending_messages: deque = deque()
        self.processing_messages: Dict[str, QueueMessage] = {}
        self.dead_letter_messages: deque = deque(maxlen=1000)
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.serialization_utils = SerializationUtils()
        
        # Circuit breaker
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = None

    async def start(self) -> bool:
        """Start queue processor"""
        try:
            logger.info(f"🚀 Starting queue processor: {self.queue_name}")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Start background processors
            await self._start_background_tasks()
            
            self.is_running = True
            self.status = QueueStatus.ACTIVE
            
            logger.info(f"✅ Queue processor {self.queue_name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start queue processor {self.queue_name}: {e}")
            self.status = QueueStatus.ERROR
            return False

    async def stop(self) -> None:
        """Stop queue processor gracefully"""
        try:
            logger.info(f"🛑 Stopping queue processor: {self.queue_name}")
            
            self.is_running = False
            self.status = QueueStatus.DRAINING
            self.shutdown_event.set()
            
            # Drain pending messages
            await self._drain_messages()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Close Redis connection
            if self.redis:
                await self.redis.close()
            
            logger.info(f"✅ Queue processor {self.queue_name} stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error stopping queue processor {self.queue_name}: {e}")

    async def enqueue(self, payload: Any, priority: int = 0, delay_seconds: int = 0, 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Enqueue a message for processing"""
        try:
            # Create message
            message = QueueMessage(
                message_id=str(uuid.uuid4()),
                queue_name=self.queue_name,
                payload=payload,
                priority=priority,
                metadata=metadata or {},
                scheduled_at=datetime.utcnow() + timedelta(seconds=delay_seconds) if delay_seconds > 0 else None
            )
            
            # Set TTL if configured
            if self.config.ttl_seconds:
                message.expires_at = datetime.utcnow() + timedelta(seconds=self.config.ttl_seconds)
            
            # Serialize message
            serialized_data = await self._serialize_message(message)
            
            # Store in Redis based on processing mode
            await self._store_message(message, serialized_data)
            
            # Update metrics
            self.metrics.total_messages += 1
            self.metrics.pending_messages += 1
            
            logger.debug(f"📝 Message enqueued: {message.message_id} in queue {self.queue_name}")
            return message.message_id
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue message: {e}")
            raise

    async def dequeue(self, timeout: int = 30) -> Optional[QueueMessage]:
        """Dequeue a message for processing"""
        try:
            if self.status != QueueStatus.ACTIVE:
                return None
            
            # Get message based on processing mode
            message = await self._get_next_message(timeout)
            
            if message:
                # Move to processing
                self.processing_messages[message.message_id] = message
                self.metrics.pending_messages -= 1
                self.metrics.processing_messages += 1
                
                logger.debug(f"📤 Message dequeued: {message.message_id} from queue {self.queue_name}")
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Failed to dequeue message: {e}")
            return None

    async def acknowledge(self, message_id: str, success: bool = True, error_message: Optional[str] = None) -> bool:
        """Acknowledge message processing completion"""
        try:
            message = self.processing_messages.get(message_id)
            if not message:
                logger.warning(f"⚠️ Message not found for acknowledgment: {message_id}")
                return False
            
            # Remove from processing
            del self.processing_messages[message_id]
            self.metrics.processing_messages -= 1
            
            if success:
                # Mark as completed
                self.metrics.completed_messages += 1
                await self._remove_message_from_storage(message_id)
                
                logger.debug(f"✅ Message acknowledged successfully: {message_id}")
                
            else:
                # Handle failure
                await self._handle_failed_message(message, error_message)
                
                logger.warning(f"❌ Message acknowledged with failure: {message_id}")
            
            # Update metrics
            self.metrics.last_activity = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to acknowledge message {message_id}: {e}")
            return False

    async def get_queue_info(self) -> Dict[str, Any]:
        """Get comprehensive queue information"""
        try:
            # Update current metrics
            await self._update_metrics()
            
            return {
                "queue_name": self.queue_name,
                "queue_type": self.config.queue_type.value,
                "processing_mode": self.config.processing_mode.value,
                "status": self.status.value,
                "is_running": self.is_running,
                "config": {
                    "max_size": self.config.max_size,
                    "batch_size": self.config.batch_size,
                    "visibility_timeout": self.config.visibility_timeout,
                    "max_retries": self.config.max_retries,
                    "compression_enabled": self.config.compression_enabled,
                    "encryption_enabled": self.config.encryption_enabled
                },
                "metrics": {
                    "total_messages": self.metrics.total_messages,
                    "pending_messages": self.metrics.pending_messages,
                    "processing_messages": self.metrics.processing_messages,
                    "completed_messages": self.metrics.completed_messages,
                    "failed_messages": self.metrics.failed_messages,
                    "dead_letter_messages": self.metrics.dead_letter_messages,
                    "average_processing_time": self.metrics.average_processing_time,
                    "throughput_per_second": self.metrics.throughput_per_second,
                    "error_rate": self.metrics.error_rate,
                    "oldest_message_age": self.metrics.oldest_message_age,
                    "consumer_count": self.metrics.consumer_count,
                    "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
                },
                "circuit_breaker": {
                    "open": self.circuit_breaker_open,
                    "failures": self.circuit_breaker_failures,
                    "last_failure": self.circuit_breaker_last_failure.isoformat() if self.circuit_breaker_last_failure else None
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get queue info: {e}")
            return {"error": str(e)}

    async def clear_queue(self, queue_type: Optional[QueueType] = None) -> int:
        """Clear messages from queue"""
        try:
            if queue_type == QueueType.DEAD_LETTER:
                count = len(self.dead_letter_messages)
                self.dead_letter_messages.clear()
                await self._clear_redis_queue(f"{self.queue_name}:dead_letter")
            else:
                count = self.metrics.pending_messages
                self.pending_messages.clear()
                await self._clear_redis_queue(self.queue_name)
                self.metrics.pending_messages = 0
            
            logger.info(f"🧹 Cleared {count} messages from queue {self.queue_name}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to clear queue: {e}")
            return 0

    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=False)
            
            # Test connection
            await self.redis.ping()
            
            logger.info(f"✅ Redis connection established for queue {self.queue_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            raise

    async def _start_background_tasks(self) -> None:
        """Start background processing tasks"""
        try:
            # Message processor
            processor_task = asyncio.create_task(self._background_processor())
            self.background_tasks.add(processor_task)
            
            # Dead letter handler
            dlq_task = asyncio.create_task(self._dead_letter_processor())
            self.background_tasks.add(dlq_task)
            
            # Metrics updater
            metrics_task = asyncio.create_task(self._metrics_updater())
            self.background_tasks.add(metrics_task)
            
            # TTL cleaner
            ttl_task = asyncio.create_task(self._ttl_cleaner())
            self.background_tasks.add(ttl_task)
            
            # Circuit breaker monitor
            circuit_task = asyncio.create_task(self._circuit_breaker_monitor())
            self.background_tasks.add(circuit_task)
            
            logger.info(f"✅ Background tasks started for queue {self.queue_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _serialize_message(self, message: QueueMessage) -> bytes:
        """Serialize message for storage"""
        try:
            # Convert to dict
            message_dict = {
                'message_id': message.message_id,
                'queue_name': message.queue_name,
                'payload': message.payload,
                'priority': message.priority,
                'attempt_count': message.attempt_count,
                'max_retries': message.max_retries,
                'created_at': message.created_at.isoformat(),
                'scheduled_at': message.scheduled_at.isoformat() if message.scheduled_at else None,
                'expires_at': message.expires_at.isoformat() if message.expires_at else None,
                'metadata': message.metadata,
                'source': message.source,
                'correlation_id': message.correlation_id,
                'reply_to': message.reply_to
            }
            
            # Serialize with msgpack for efficiency
            serialized = msgpack.packb(message_dict)
            
            # Compress if enabled
            if self.config.compression_enabled:
                serialized = await self.serialization_utils.compress_data(serialized)
            
            # Encrypt if enabled
            if self.config.encryption_enabled:
                serialized = await self.serialization_utils.encrypt_data(serialized)
            
            return serialized
            
        except Exception as e:
            logger.error(f"❌ Failed to serialize message: {e}")
            raise

    async def _deserialize_message(self, data: bytes) -> QueueMessage:
        """Deserialize message from storage"""
        try:
            # Decrypt if enabled
            if self.config.encryption_enabled:
                data = await self.serialization_utils.decrypt_data(data)
            
            # Decompress if enabled
            if self.config.compression_enabled:
                data = await self.serialization_utils.decompress_data(data)
            
            # Deserialize with msgpack
            message_dict = msgpack.unpackb(data, raw=False)
            
            # Convert back to QueueMessage
            message = QueueMessage(
                message_id=message_dict['message_id'],
                queue_name=message_dict['queue_name'],
                payload=message_dict['payload'],
                priority=message_dict['priority'],
                attempt_count=message_dict['attempt_count'],
                max_retries=message_dict['max_retries'],
                created_at=datetime.fromisoformat(message_dict['created_at']),
                scheduled_at=datetime.fromisoformat(message_dict['scheduled_at']) if message_dict['scheduled_at'] else None,
                expires_at=datetime.fromisoformat(message_dict['expires_at']) if message_dict['expires_at'] else None,
                metadata=message_dict['metadata'],
                source=message_dict['source'],
                correlation_id=message_dict['correlation_id'],
                reply_to=message_dict['reply_to']
            )
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Failed to deserialize message: {e}")
            raise

    async def _store_message(self, message: QueueMessage, serialized_data: bytes) -> None:
        """Store message in Redis based on processing mode"""
        try:
            queue_key = self._get_queue_key(message)
            
            if self.config.processing_mode == ProcessingMode.PRIORITY:
                # Use sorted set for priority queue
                await self.redis.zadd(queue_key, {serialized_data: message.priority})
            elif message.scheduled_at and message.scheduled_at > datetime.utcnow():
                # Delayed message - use sorted set with timestamp
                timestamp = message.scheduled_at.timestamp()
                delayed_key = f"{self.queue_name}:delayed"
                await self.redis.zadd(delayed_key, {serialized_data: timestamp})
            else:
                # Regular FIFO/LIFO queue
                if self.config.processing_mode == ProcessingMode.LIFO:
                    await self.redis.lpush(queue_key, serialized_data)
                else:  # FIFO
                    await self.redis.rpush(queue_key, serialized_data)
            
            # Set TTL if configured
            if self.config.ttl_seconds:
                await self.redis.expire(queue_key, self.config.ttl_seconds)
            
        except Exception as e:
            logger.error(f"❌ Failed to store message: {e}")
            raise

    async def _get_next_message(self, timeout: int) -> Optional[QueueMessage]:
        """Get next message based on processing mode"""
        try:
            queue_key = self._get_queue_key()
            
            if self.config.processing_mode == ProcessingMode.PRIORITY:
                # Get highest priority message
                result = await self.redis.zpopmax(queue_key)
                if result:
                    serialized_data, priority = result[0]
                    return await self._deserialize_message(serialized_data)
            else:
                # FIFO/LIFO processing
                if self.config.processing_mode == ProcessingMode.LIFO:
                    result = await self.redis.blpop(queue_key, timeout=timeout)
                else:  # FIFO
                    result = await self.redis.brpop(queue_key, timeout=timeout)
                
                if result:
                    _, serialized_data = result
                    return await self._deserialize_message(serialized_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get next message: {e}")
            return None

    async def _handle_failed_message(self, message: QueueMessage, error_message: Optional[str] = None) -> None:
        """Handle failed message processing"""
        try:
            message.attempt_count += 1
            
            if message.attempt_count <= message.max_retries:
                # Retry message with exponential backoff
                delay = min(60, 2 ** message.attempt_count)
                message.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
                
                # Re-enqueue for retry
                serialized_data = await self._serialize_message(message)
                retry_key = f"{self.queue_name}:retry"
                timestamp = message.scheduled_at.timestamp()
                await self.redis.zadd(retry_key, {serialized_data: timestamp})
                
                logger.info(f"🔄 Message scheduled for retry {message.attempt_count}/{message.max_retries}: {message.message_id}")
                
            else:
                # Move to dead letter queue
                await self._move_to_dead_letter(message, error_message)
                self.metrics.failed_messages += 1
                
                logger.warning(f"💀 Message moved to dead letter queue: {message.message_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle failed message: {e}")

    async def _move_to_dead_letter(self, message: QueueMessage, error_message: Optional[str] = None) -> None:
        """Move message to dead letter queue"""
        try:
            # Add error information
            message.metadata['error_message'] = error_message
            message.metadata['failed_at'] = datetime.utcnow().isoformat()
            message.metadata['final_attempt_count'] = message.attempt_count
            
            # Store in dead letter queue
            dlq_key = f"{self.queue_name}:dead_letter"
            serialized_data = await self._serialize_message(message)
            await self.redis.lpush(dlq_key, serialized_data)
            
            # Add to local dead letter queue
            self.dead_letter_messages.append(message)
            self.metrics.dead_letter_messages += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to move message to dead letter queue: {e}")

    async def _background_processor(self) -> None:
        """Background task for processing delayed messages"""
        while not self.shutdown_event.is_set():
            try:
                # Process delayed messages
                await self._process_delayed_messages()
                
                # Process retry messages
                await self._process_retry_messages()
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Background processor error: {e}")
                await asyncio.sleep(30)

    async def _process_delayed_messages(self) -> None:
        """Process delayed messages that are ready"""
        try:
            delayed_key = f"{self.queue_name}:delayed"
            current_time = datetime.utcnow().timestamp()
            
            # Get messages ready for processing
            ready_messages = await self.redis.zrangebyscore(
                delayed_key, 0, current_time, withscores=True
            )
            
            for serialized_data, timestamp in ready_messages:
                try:
                    # Remove from delayed queue
                    await self.redis.zrem(delayed_key, serialized_data)
                    
                    # Add to main queue
                    queue_key = self._get_queue_key()
                    await self.redis.rpush(queue_key, serialized_data)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process delayed message: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process delayed messages: {e}")

    async def _process_retry_messages(self) -> None:
        """Process retry messages that are ready"""
        try:
            retry_key = f"{self.queue_name}:retry"
            current_time = datetime.utcnow().timestamp()
            
            # Get messages ready for retry
            ready_messages = await self.redis.zrangebyscore(
                retry_key, 0, current_time, withscores=True
            )
            
            for serialized_data, timestamp in ready_messages:
                try:
                    # Remove from retry queue
                    await self.redis.zrem(retry_key, serialized_data)
                    
                    # Add to main queue
                    queue_key = self._get_queue_key()
                    await self.redis.rpush(queue_key, serialized_data)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process retry message: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process retry messages: {e}")

    async def _dead_letter_processor(self) -> None:
        """Background task for dead letter queue processing"""
        while not self.shutdown_event.is_set():
            try:
                # Monitor dead letter queue size
                dlq_size = await self.redis.llen(f"{self.queue_name}:dead_letter")
                
                if dlq_size > 1000:  # Alert if too many dead letters
                    logger.warning(f"⚠️ High dead letter queue size: {dlq_size} for queue {self.queue_name}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Dead letter processor error: {e}")
                await asyncio.sleep(120)

    async def _metrics_updater(self) -> None:
        """Background task for updating metrics"""
        while not self.shutdown_event.is_set():
            try:
                await self._update_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Metrics updater error: {e}")
                await asyncio.sleep(60)

    async def _update_metrics(self) -> None:
        """Update queue metrics"""
        try:
            # Update queue sizes
            queue_key = self._get_queue_key()
            self.metrics.pending_messages = await self.redis.llen(queue_key)
            
            # Update dead letter count
            dlq_key = f"{self.queue_name}:dead_letter"
            self.metrics.dead_letter_messages = await self.redis.llen(dlq_key)
            
            # Calculate error rate
            total_processed = self.metrics.completed_messages + self.metrics.failed_messages
            if total_processed > 0:
                self.metrics.error_rate = (self.metrics.failed_messages / total_processed) * 100
            
            # Calculate throughput (messages per second)
            # This would need historical data for accurate calculation
            # Simplified version here
            if self.metrics.last_activity:
                time_diff = (datetime.utcnow() - self.metrics.last_activity).total_seconds()
                if time_diff > 0:
                    self.metrics.throughput_per_second = 1.0 / time_diff
            
        except Exception as e:
            logger.error(f"❌ Failed to update metrics: {e}")

    async def _ttl_cleaner(self) -> None:
        """Background task for cleaning expired messages"""
        while not self.shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                
                # Clean expired messages from local storage
                expired_messages = []
                for msg_id, message in self.processing_messages.items():
                    if message.expires_at and message.expires_at < current_time:
                        expired_messages.append(msg_id)
                
                for msg_id in expired_messages:
                    await self.acknowledge(msg_id, success=False, error_message="Message expired")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ TTL cleaner error: {e}")
                await asyncio.sleep(600)

    async def _circuit_breaker_monitor(self) -> None:
        """Monitor circuit breaker state"""
        while not self.shutdown_event.is_set():
            try:
                # Reset circuit breaker if enough time has passed
                if self.circuit_breaker_open and self.circuit_breaker_last_failure:
                    time_since_failure = datetime.utcnow() - self.circuit_breaker_last_failure
                    if time_since_failure.total_seconds() > 300:  # 5 minutes
                        self.circuit_breaker_open = False
                        self.circuit_breaker_failures = 0
                        logger.info(f"🔓 Circuit breaker reset for queue {self.queue_name}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Circuit breaker monitor error: {e}")
                await asyncio.sleep(120)

    async def _drain_messages(self) -> None:
        """Drain remaining messages during shutdown"""
        try:
            logger.info(f"🔄 Draining messages for queue {self.queue_name}")
            
            # Wait for processing messages to complete
            timeout = 60  # 1 minute timeout
            start_time = time.time()
            
            while self.processing_messages and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)
            
            # Force acknowledge remaining messages
            if self.processing_messages:
                logger.warning(f"⚠️ Force acknowledging {len(self.processing_messages)} messages")
                for msg_id in list(self.processing_messages.keys()):
                    await self.acknowledge(msg_id, success=False, error_message="System shutdown")
            
        except Exception as e:
            logger.error(f"❌ Failed to drain messages: {e}")

    async def _remove_message_from_storage(self, message_id: str) -> None:
        """Remove message from Redis storage"""
        try:
            # This is a simplified implementation
            # In practice, you'd need to track message locations more precisely
            pass
            
        except Exception as e:
            logger.error(f"❌ Failed to remove message from storage: {e}")

    async def _clear_redis_queue(self, queue_key: str) -> None:
        """Clear Redis queue"""
        try:
            await self.redis.delete(queue_key)
            
        except Exception as e:
            logger.error(f"❌ Failed to clear Redis queue: {e}")

    def _get_queue_key(self, message: Optional[QueueMessage] = None) -> str:
        """Get Redis key for queue"""
        if self.config.processing_mode == ProcessingMode.PRIORITY:
            return f"{self.queue_name}:priority"
        else:
            return self.queue_name


class QueueProcessorManager:
    """
    Manager for multiple queue processors
    
    Features:
    - Multiple queue management
    - Global metrics aggregation
    - Cross-queue load balancing
    - Centralized monitoring
    """
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.processors: Dict[str, QueueProcessor] = {}
        self.global_metrics: Dict[str, Any] = {}
        self.is_running = False

    async def start(self) -> bool:
        """Start queue processor manager"""
        try:
            logger.info("🚀 Starting queue processor manager")
            
            self.is_running = True
            
            logger.info("✅ Queue processor manager started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start queue processor manager: {e}")
            return False

    async def stop(self) -> None:
        """Stop all queue processors"""
        try:
            logger.info("🛑 Stopping queue processor manager")
            
            # Stop all processors
            for processor in self.processors.values():
                await processor.stop()
            
            self.is_running = False
            
            logger.info("✅ Queue processor manager stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping queue processor manager: {e}")

    async def create_processor(self, config: QueueConfig) -> bool:
        """Create a new queue processor"""
        try:
            if config.queue_name in self.processors:
                logger.warning(f"⚠️ Queue processor already exists: {config.queue_name}")
                return False
            
            processor = QueueProcessor(config, self.redis_url)
            success = await processor.start()
            
            if success:
                self.processors[config.queue_name] = processor
                logger.info(f"✅ Created queue processor: {config.queue_name}")
                return True
            else:
                logger.error(f"❌ Failed to start queue processor: {config.queue_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create queue processor: {e}")
            return False

    async def get_processor(self, queue_name: str) -> Optional[QueueProcessor]:
        """Get queue processor by name"""
        return self.processors.get(queue_name)

    async def get_global_status(self) -> Dict[str, Any]:
        """
Get global status of all processors"""
        try:
            total_processors = len(self.processors)
            active_processors = sum(1 for p in self.processors.values() if p.status == QueueStatus.ACTIVE)
            
            total_pending = sum(p.metrics.pending_messages for p in self.processors.values())
            total_processing = sum(p.metrics.processing_messages for p in self.processors.values())
            total_completed = sum(p.metrics.completed_messages for p in self.processors.values())
            total_failed = sum(p.metrics.failed_messages for p in self.processors.values())
            
            processor_status = {}
            for name, processor in self.processors.items():
                processor_status[name] = await processor.get_queue_info()
            
            return {
                "manager_status": "running" if self.is_running else "stopped",
                "total_processors": total_processors,
                "active_processors": active_processors,
                "global_metrics": {
                    "total_pending_messages": total_pending,
                    "total_processing_messages": total_processing,
                    "total_completed_messages": total_completed,
                    "total_failed_messages": total_failed,
                    "overall_error_rate": (total_failed / (total_completed + total_failed) * 100) if (total_completed + total_failed) > 0 else 0
                },
                "processors": processor_status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get global status: {e}")
            return {"error": str(e)}
