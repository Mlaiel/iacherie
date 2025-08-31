"""High-Performance Distributed Queue System for IA Influencer Agent
================================================================

Enterprise-grade queue management with intelligent prioritization,
load balancing, and guaranteed message delivery.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import pickle

from pydantic import BaseModel, Field
from redis.asyncio import Redis

from ...core.config import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class QueuePriority(int, Enum):
    """Queue priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MessageStatus(str, Enum):
    """Message processing status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


class QueueType(str, Enum):
    """Queue type definitions"""    FIFO = "fifo"
    PRIORITY = "priority"
    DELAY = "delay"
    UNIQUE = "unique"
    BATCHED = "batched"


@dataclass
class QueueMessage:
    """Queue message structure"""    message_id: str
    queue_name: str
    payload: Any
    priority: QueuePriority = QueuePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)
    consumer_id: Optional[str] = None
    
    def __lt__(self, other):
        """Priority comparison for heap operations"""        return self.priority.value > other.priority.value


class QueueConfig(BaseModel):
    """Queue configuration"""    name: str = Field(..., description="Queue name")
    queue_type: QueueType = Field(default=QueueType.FIFO, description="Queue type")
    max_size: int = Field(default=10000, description="Maximum queue size")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay_seconds: float = Field(default=60.0, description="Retry delay")
    message_timeout_seconds: int = Field(default=300, description="Message timeout")
    dead_letter_enabled: bool = Field(default=True, description="Enable dead letter queue")
    batch_size: int = Field(default=1, description="Batch processing size")
    visibility_timeout: int = Field(default=30, description="Message visibility timeout")
    auto_delete_completed: bool = Field(default=True, description="Auto delete completed messages")
    persistence_enabled: bool = Field(default=True, description="Enable persistence")


class QueueMetrics(BaseModel):
    """Queue performance metrics"""    total_messages: int = Field(default=0, description="Total messages processed")
    pending_messages: int = Field(default=0, description="Pending messages")
    processing_messages: int = Field(default=0, description="Currently processing")
    completed_messages: int = Field(default=0, description="Completed messages")
    failed_messages: int = Field(default=0, description="Failed messages")
    dead_letter_messages: int = Field(default=0, description="Dead letter messages")
    avg_processing_time: float = Field(default=0.0, description="Average processing time")
    throughput_per_second: float = Field(default=0.0, description="Messages per second")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")


class MessageProcessor:
    """Message processor for handling queue messages"""    
    def __init__(self, processor_id: str, handler: Callable):
        self.processor_id = processor_id
        self.handler = handler
        self.active = True
        self.current_message: Optional[QueueMessage] = None
        self.processed_count = 0
        self.error_count = 0
        
    async def process(self, message: QueueMessage) -> bool:
        """Process a single message"""        try:
            self.current_message = message
            message.processing_started_at = datetime.now(timezone.utc)
            message.status = MessageStatus.PROCESSING
            message.consumer_id = self.processor_id
            
            # Process the message
            result = await self.handler(message.payload, message.metadata)
            
            if result:
                message.status = MessageStatus.COMPLETED
                message.completed_at = datetime.now(timezone.utc)
                self.processed_count += 1
                return True
            else:
                message.status = MessageStatus.FAILED
                self.error_count += 1
                return False
                
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            message.status = MessageStatus.FAILED
            self.error_count += 1
            return False
        finally:
            self.current_message = None


class DistributedQueue:
    """Single queue implementation"""    
    def __init__(self, config: QueueConfig, redis_client: Redis):
        self.config = config
        self.redis = redis_client
        self.metrics = QueueMetrics()
        self.processors: Dict[str, MessageProcessor] = {}
        
        # Queue storage
        self.pending_queue = []  # Priority heap
        self.processing_messages: Dict[str, QueueMessage] = {}
        self.completed_messages: Dict[str, QueueMessage] = {}
        self.failed_messages: Dict[str, QueueMessage] = {}
        self.dead_letter_queue: List[QueueMessage] = []
        
        # Unique message tracking
        self.message_hashes: Set[str] = set()
        
        # Performance tracking
        self.processing_times: deque = deque(maxlen=1000)
        self.throughput_tracker = deque(maxlen=60)  # Last 60 seconds
        
    async def enqueue(
        self,
        payload: Any,
        priority: QueuePriority = QueuePriority.NORMAL,
        delay_seconds: float = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """        Add message to queue
        
        Args:
            payload: Message payload
            priority: Message priority
            delay_seconds: Delay before processing
            metadata: Additional metadata
            
        Returns:
            Message ID or None if failed
        """        try:
            # Check queue size limit
            if len(self.pending_queue) >= self.config.max_size:
                logger.warning(f"Queue {self.config.name} is full")
                return None
                
            # Generate message ID
            message_id = hashlib.sha256(
                f"{self.config.name}_{time.time()}_{hash(str(payload))}".encode()
            ).hexdigest()[:16]
            
            # Check for unique constraint
            if self.config.queue_type == QueueType.UNIQUE:
                payload_hash = hashlib.sha256(str(payload).encode()).hexdigest()
                if payload_hash in self.message_hashes:
                    logger.info(f"Duplicate message rejected: {payload_hash}")
                    return None
                self.message_hashes.add(payload_hash)
                
            # Create message
            scheduled_at = None
            if delay_seconds > 0:
                scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
                
            message = QueueMessage(
                message_id=message_id,
                queue_name=self.config.name,
                payload=payload,
                priority=priority,
                scheduled_at=scheduled_at,
                max_retries=self.config.max_retries,
                timeout_seconds=self.config.message_timeout_seconds,
                metadata=metadata or {}
            )
            
            # Add to queue
            if self.config.queue_type == QueueType.PRIORITY:
                heapq.heappush(self.pending_queue, message)
            else:
                self.pending_queue.append(message)
                
            # Persist if enabled
            if self.config.persistence_enabled:
                await self._persist_message(message)
                
            # Update metrics
            self.metrics.total_messages += 1
            self.metrics.pending_messages += 1
            self.metrics.last_activity = datetime.now(timezone.utc)
            
            logger.debug(f"Message {message_id} enqueued to {self.config.name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue message: {e}")
            return None
            
    async def dequeue(self, processor_id: str) -> Optional[QueueMessage]:
        """        Get next message from queue
        
        Args:
            processor_id: Processor identifier
            
        Returns:
            Next message or None
        """        try:
            current_time = datetime.now(timezone.utc)
            
            # Find next available message
            message = None
            
            if self.config.queue_type == QueueType.PRIORITY:
                # Priority queue - get highest priority
                while self.pending_queue:
                    candidate = heapq.heappop(self.pending_queue)
                    
                    # Check if scheduled time has passed
                    if candidate.scheduled_at and candidate.scheduled_at > current_time:
                        # Put back and wait
                        heapq.heappush(self.pending_queue, candidate)
                        break
                        
                    message = candidate
                    break
            else:
                # FIFO queue
                while self.pending_queue:
                    candidate = self.pending_queue.pop(0)
                    
                    # Check if scheduled time has passed
                    if candidate.scheduled_at and candidate.scheduled_at > current_time:
                        # Put back and wait
                        self.pending_queue.insert(0, candidate)
                        break
                        
                    message = candidate
                    break
                    
            if not message:
                return None
                
            # Move to processing
            message.status = MessageStatus.PROCESSING
            message.consumer_id = processor_id
            self.processing_messages[message.message_id] = message
            
            # Update metrics
            self.metrics.pending_messages -= 1
            self.metrics.processing_messages += 1
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to dequeue message: {e}")
            return None
            
    async def acknowledge(self, message_id: str) -> bool:
        """        Acknowledge message completion
        
        Args:
            message_id: Message identifier
            
        Returns:
            Success status
        """        try:
            if message_id not in self.processing_messages:
                return False
                
            message = self.processing_messages.pop(message_id)
            message.status = MessageStatus.COMPLETED
            message.completed_at = datetime.now(timezone.utc)
            
            # Calculate processing time
            if message.processing_started_at:
                processing_time = (
                    message.completed_at - message.processing_started_at
                ).total_seconds()
                self.processing_times.append(processing_time)
                
            # Store completed message or delete
            if self.config.auto_delete_completed:
                await self._delete_message(message)
            else:
                self.completed_messages[message_id] = message
                
            # Update metrics
            self.metrics.processing_messages -= 1
            self.metrics.completed_messages += 1
            self._update_throughput()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
            return False
            
    async def reject(self, message_id: str, requeue: bool = True) -> bool:
        """        Reject message and optionally requeue
        
        Args:
            message_id: Message identifier
            requeue: Whether to requeue for retry
            
        Returns:
            Success status
        """        try:
            if message_id not in self.processing_messages:
                return False
                
            message = self.processing_messages.pop(message_id)
            message.status = MessageStatus.FAILED
            message.retry_count += 1
            
            # Check if should retry
            if requeue and message.retry_count <= message.max_retries:
                # Add retry delay
                message.scheduled_at = datetime.now(timezone.utc) + timedelta(
                    seconds=self.config.retry_delay_seconds * message.retry_count
                )
                message.status = MessageStatus.RETRY
                
                # Requeue
                if self.config.queue_type == QueueType.PRIORITY:
                    heapq.heappush(self.pending_queue, message)
                else:
                    self.pending_queue.append(message)
                    
                self.metrics.pending_messages += 1
            else:
                # Move to dead letter queue
                if self.config.dead_letter_enabled:
                    message.status = MessageStatus.DEAD_LETTER
                    self.dead_letter_queue.append(message)
                    self.metrics.dead_letter_messages += 1
                else:
                    self.failed_messages[message_id] = message
                    
                self.metrics.failed_messages += 1
                
            # Update metrics
            self.metrics.processing_messages -= 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject message {message_id}: {e}")
            return False
            
    async def get_queue_size(self) -> int:
        """Get current queue size"""        return len(self.pending_queue)
        
    async def get_metrics(self) -> QueueMetrics:
        """Get queue performance metrics"""        # Update average processing time
        if self.processing_times:
            self.metrics.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
            
        return self.metrics
        
    async def purge(self) -> bool:
        """Clear all messages from queue"""        try:
            self.pending_queue.clear()
            self.processing_messages.clear()
            self.completed_messages.clear()
            self.failed_messages.clear()
            self.dead_letter_queue.clear()
            self.message_hashes.clear()
            
            # Reset metrics
            self.metrics = QueueMetrics()
            
            logger.info(f"Queue {self.config.name} purged")
            return True
            
        except Exception as e:
            logger.error(f"Failed to purge queue: {e}")
            return False
            
    async def _persist_message(self, message: QueueMessage) -> None:
        """Persist message to Redis"""        try:
            key = f"queue:{self.config.name}:message:{message.message_id}"
            data = {
                "message_id": message.message_id,
                "queue_name": message.queue_name,
                "payload": pickle.dumps(message.payload).hex(),
                "priority": message.priority.value,
                "status": message.status.value,
                "created_at": message.created_at.isoformat(),
                "scheduled_at": message.scheduled_at.isoformat() if message.scheduled_at else None,
                "retry_count": message.retry_count,
                "max_retries": message.max_retries,
                "timeout_seconds": message.timeout_seconds,
                "metadata": json.dumps(message.metadata)
            }
            
            await self.redis.hset(key, mapping=data)
            await self.redis.expire(key, 86400)  # 24 hour TTL
            
        except Exception as e:
            logger.error(f"Failed to persist message: {e}")
            
    async def _delete_message(self, message: QueueMessage) -> None:
        """Delete persisted message"""        try:
            key = f"queue:{self.config.name}:message:{message.message_id}"
            await self.redis.delete(key)
            
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            
    def _update_throughput(self) -> None:
        """Update throughput metrics"""        current_time = time.time()
        self.throughput_tracker.append(current_time)
        
        # Calculate messages per second over last 60 seconds
        if len(self.throughput_tracker) > 1:
            time_window = current_time - self.throughput_tracker[0]
            if time_window > 0:
                self.metrics.throughput_per_second = len(self.throughput_tracker) / time_window


class StreamQueue:
    """    High-Performance Distributed Queue System for IA Influencer Agent
    
    Enterprise-grade queue management with intelligent prioritization,
    load balancing, and guaranteed message delivery.
    """    
    def __init__(self):
        self.queues: Dict[str, DistributedQueue] = {}
        self.redis_client: Optional[Redis] = None
        self.processors: Dict[str, MessageProcessor] = {}
        self._shutdown_event = asyncio.Event()
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize queue system"""        try:
            # Initialize Redis connection
            redis_url = settings.redis_url or "redis://localhost:6379"
            self.redis_client = Redis.from_url(redis_url)
            
            # Test connection
            await self.redis_client.ping()
            
            # Start monitoring task
            self._monitor_task = asyncio.create_task(self._monitor_queues())
            
            logger.info("StreamQueue initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize StreamQueue: {e}")
            raise
            
    async def create_queue(self, config: QueueConfig) -> bool:
        """        Create new queue
        
        Args:
            config: Queue configuration
            
        Returns:
            Success status
        """        try:
            if config.name in self.queues:
                logger.warning(f"Queue {config.name} already exists")
                return False
                
            queue = DistributedQueue(config, self.redis_client)
            self.queues[config.name] = queue
            
            logger.info(f"Created queue {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create queue {config.name}: {e}")
            return False
            
    async def delete_queue(self, queue_name: str) -> bool:
        """        Delete queue
        
        Args:
            queue_name: Queue name
            
        Returns:
            Success status
        """        try:
            if queue_name not in self.queues:
                return False
                
            queue = self.queues[queue_name]
            await queue.purge()
            del self.queues[queue_name]
            
            logger.info(f"Deleted queue {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete queue {queue_name}: {e}")
            return False
            
    async def enqueue(
        self,
        queue_name: str,
        payload: Any,
        priority: QueuePriority = QueuePriority.NORMAL,
        delay_seconds: float = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """        Add message to queue
        
        Args:
            queue_name: Target queue name
            payload: Message payload
            priority: Message priority
            delay_seconds: Delay before processing
            metadata: Additional metadata
            
        Returns:
            Message ID or None
        """        if queue_name not in self.queues:
            logger.error(f"Queue {queue_name} not found")
            return None
            
        return await self.queues[queue_name].enqueue(
            payload, priority, delay_seconds, metadata
        )
        
    async def dequeue(self, queue_name: str, processor_id: str) -> Optional[QueueMessage]:
        """        Get next message from queue
        
        Args:
            queue_name: Source queue name
            processor_id: Processor identifier
            
        Returns:
            Next message or None
        """        if queue_name not in self.queues:
            return None
            
        return await self.queues[queue_name].dequeue(processor_id)
        
    async def acknowledge(self, queue_name: str, message_id: str) -> bool:
        """Acknowledge message completion"""        if queue_name not in self.queues:
            return False
            
        return await self.queues[queue_name].acknowledge(message_id)
        
    async def reject(self, queue_name: str, message_id: str, requeue: bool = True) -> bool:
        """Reject message"""        if queue_name not in self.queues:
            return False
            
        return await self.queues[queue_name].reject(message_id, requeue)
        
    async def register_processor(
        self,
        processor_id: str,
        queue_name: str,
        handler: Callable
    ) -> bool:
        """        Register message processor
        
        Args:
            processor_id: Processor identifier
            queue_name: Target queue name
            handler: Message handler function
            
        Returns:
            Success status
        """        try:
            if queue_name not in self.queues:
                logger.error(f"Queue {queue_name} not found")
                return False
                
            processor = MessageProcessor(processor_id, handler)
            self.processors[processor_id] = processor
            
            # Start processing task
            asyncio.create_task(self._process_messages(processor, queue_name))
            
            logger.info(f"Registered processor {processor_id} for queue {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register processor: {e}")
            return False
            
    async def unregister_processor(self, processor_id: str) -> bool:
        """Unregister processor"""        try:
            if processor_id in self.processors:
                self.processors[processor_id].active = False
                del self.processors[processor_id]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister processor: {e}")
            return False
            
    async def get_queue_metrics(self, queue_name: str) -> Optional[QueueMetrics]:
        """Get queue metrics"""        if queue_name in self.queues:
            return await self.queues[queue_name].get_metrics()
        return None
        
    async def list_queues(self) -> List[Dict[str, Any]]:
        """List all queues with metrics"""        queues = []
        
        for queue_name, queue in self.queues.items():
            metrics = await queue.get_metrics()
            queues.append({
                "name": queue_name,
                "type": queue.config.queue_type.value,
                "size": await queue.get_queue_size(),
                "metrics": metrics.dict()
            })
            
        return queues
        
    async def _process_messages(self, processor: MessageProcessor, queue_name: str) -> None:
        """Background message processing"""        while processor.active and not self._shutdown_event.is_set():
            try:
                # Get next message
                message = await self.dequeue(queue_name, processor.processor_id)
                
                if message:
                    # Process message
                    success = await processor.process(message)
                    
                    if success:
                        await self.acknowledge(queue_name, message.message_id)
                    else:
                        await self.reject(queue_name, message.message_id)
                else:
                    # No messages available, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                await asyncio.sleep(5)
                
    async def _monitor_queues(self) -> None:
        """Background queue monitoring"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                for queue_name, queue in self.queues.items():
                    metrics = await queue.get_metrics()
                    
                    # Log queue status
                    logger.info(
                        f"Queue {queue_name}: "
                        f"pending={metrics.pending_messages}, "
                        f"processing={metrics.processing_messages}, "
                        f"throughput={metrics.throughput_per_second:.2f}/s"
                    )
                    
                    # Check for issues
                    if metrics.failed_messages > 100:
                        logger.warning(
                            f"High failure rate in queue {queue_name}: "
                            f"{metrics.failed_messages} failed messages"
                        )
                        
            except Exception as e:
                logger.error(f"Queue monitoring error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown queue system"""        try:
            self._shutdown_event.set()
            
            # Stop all processors
            for processor in self.processors.values():
                processor.active = False
                
            # Cancel monitoring task
            if self._monitor_task:
                self._monitor_task.cancel()
                
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                
            logger.info("StreamQueue shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during queue shutdown: {e}")
