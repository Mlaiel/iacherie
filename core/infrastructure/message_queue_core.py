"""Ainflue Core Message Queue - Enterprise Message Queue Management
================================================================

Core message queue management system providing advanced messaging orchestration,
event-driven architecture, pub/sub patterns, task queues, and enterprise-grade
message queue operations for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import redis.asyncio as redis
from celery import Celery

logger = logging.getLogger(__name__)

class QueueType(str, Enum):
    """Message queue types"""
    REDIS = "redis"
    CELERY = "celery"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"

@dataclass
class QueueMessage:
    """Message queue message"""
    id: str
    topic: str
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    delay: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueueConfig:
    """Message queue configuration"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 1
    redis_password: Optional[str] = None
    celery_broker: str = "redis://localhost:6379/2"
    celery_backend: str = "redis://localhost:6379/3"
    default_queue: str = "ainflue_default"
    max_workers: int = 10
    visibility_timeout: int = 300
    message_ttl: int = 86400  # 24 hours

@dataclass
class QueueMetrics:
    """Message queue metrics"""
    messages_sent: int = 0
    messages_received: int = 0
    messages_processed: int = 0
    messages_failed: int = 0
    active_workers: int = 0
    queue_size: int = 0
    avg_processing_time: float = 0.0
    error_count: int = 0
    last_error: Optional[str] = None

class MessageQueueCore:
    """Enterprise message queue core management system"""
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """Initialize message queue core"""
        self.config = config or QueueConfig()
        self.metrics = QueueMetrics()
        
        # Queue connections
        self.redis_client: Optional[redis.Redis] = None
        self.celery_app: Optional[Celery] = None
        
        # Message handlers
        self.handlers: Dict[str, Callable] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.running = False
        
        logger.info("📨 Message Queue Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize message queue system"""
        try:
            logger.info("🔌 Initializing message queue connections...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Initialize Celery
            await self._initialize_celery()
            
            logger.info("✅ Message Queue Core initialization completed")
            return True
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Message Queue Core initialization failed: {e}")
            return False
    
    async def _initialize_redis(self):
        """Initialize Redis connection for message queue"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=False,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            
            logger.info("✅ Redis message queue connection established")
            
        except Exception as e:
            logger.error(f"❌ Redis message queue connection failed: {e}")
            raise
    
    async def _initialize_celery(self):
        """Initialize Celery for distributed task processing"""
        try:
            self.celery_app = Celery(
                'ainflue_tasks',
                broker=self.config.celery_broker,
                backend=self.config.celery_backend
            )
            
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_routes={
                    'ainflue.ai.*': {'queue': 'ai_processing'},
                    'ainflue.media.*': {'queue': 'media_processing'},
                    'ainflue.security.*': {'queue': 'security_processing'},
                },
                worker_max_tasks_per_child=1000,
                task_time_limit=3600,  # 1 hour
                task_soft_time_limit=3000,  # 50 minutes
            )
            
            logger.info("✅ Celery task queue configured")
            
        except Exception as e:
            logger.error(f"❌ Celery initialization failed: {e}")
            # Celery is optional, don't raise
    
    async def publish(self, topic: str, payload: Dict[str, Any], 
                     priority: MessagePriority = MessagePriority.NORMAL,
                     delay: Optional[int] = None) -> str:
        """Publish message to queue"""
        try:
            message_id = f"{topic}_{int(time.time() * 1000)}"
            
            message = QueueMessage(
                id=message_id,
                topic=topic,
                payload=payload,
                priority=priority,
                delay=delay
            )
            
            # Serialize message
            message_data = {
                'id': message.id,
                'topic': message.topic,
                'payload': message.payload,
                'priority': message.priority.value,
                'created_at': message.created_at.isoformat(),
                'retry_count': message.retry_count,
                'max_retries': message.max_retries,
                'status': message.status.value,
                'delay': message.delay,
                'metadata': message.metadata
            }
            
            serialized_message = json.dumps(message_data)
            
            if delay:
                # Delayed message
                await self._schedule_delayed_message(topic, serialized_message, delay)
            else:
                # Immediate message
                await self._enqueue_message(topic, serialized_message, priority)
            
            self.metrics.messages_sent += 1
            logger.debug(f"📤 Message published to topic '{topic}': {message_id}")
            
            return message_id
            
        except Exception as e:
            self.metrics.error_count += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Failed to publish message to topic '{topic}': {e}")
            raise
    
    async def _enqueue_message(self, topic: str, message: str, priority: MessagePriority):
        """Enqueue message with priority"""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
        
        queue_key = f"queue:{topic}"
        priority_score = {
            MessagePriority.LOW: 1,
            MessagePriority.NORMAL: 2,
            MessagePriority.HIGH: 3,
            MessagePriority.CRITICAL: 4
        }.get(priority, 2)
        
        # Add to priority queue (sorted set)
        await self.redis_client.zadd(queue_key, {message: priority_score})
        
        # Update queue size metric
        self.metrics.queue_size = await self.redis_client.zcard(queue_key)
    
    async def _schedule_delayed_message(self, topic: str, message: str, delay: int):
        """Schedule delayed message"""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
        
        delayed_key = f"delayed:{topic}"
        execution_time = time.time() + delay
        
        # Add to delayed queue (sorted set with execution time as score)
        await self.redis_client.zadd(delayed_key, {message: execution_time})
    
    async def subscribe(self, topic: str, handler: Callable[[QueueMessage], Coroutine[Any, Any, None]]):
        """Subscribe to topic with message handler"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        self.subscribers[topic].append(handler)
        logger.info(f"📥 Subscribed to topic '{topic}'")
    
    async def unsubscribe(self, topic: str, handler: Callable):
        """Unsubscribe from topic"""
        if topic in self.subscribers and handler in self.subscribers[topic]:
            self.subscribers[topic].remove(handler)
            
            if not self.subscribers[topic]:
                del self.subscribers[topic]
            
            logger.info(f"📤 Unsubscribed from topic '{topic}'")
    
    async def start_workers(self, num_workers: Optional[int] = None):
        """Start message queue workers"""
        if self.running:
            logger.warning("⚠️ Workers already running")
            return
        
        num_workers = num_workers or self.config.max_workers
        self.running = True
        
        logger.info(f"🚀 Starting {num_workers} message queue workers")
        
        # Start worker tasks
        for i in range(num_workers):
            worker_task = asyncio.create_task(self._worker_loop(f"worker_{i}"))
            self.workers.append(worker_task)
        
        # Start delayed message processor
        delayed_processor = asyncio.create_task(self._delayed_message_processor())
        self.workers.append(delayed_processor)
        
        self.metrics.active_workers = num_workers
    
    async def stop_workers(self):
        """Stop message queue workers"""
        if not self.running:
            return
        
        logger.info("🛑 Stopping message queue workers")
        self.running = False
        
        # Cancel all worker tasks
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        self.metrics.active_workers = 0
        
        logger.info("✅ All workers stopped")
    
    async def _worker_loop(self, worker_id: str):
        """Main worker loop for processing messages"""
        logger.info(f"👷 Worker {worker_id} started")
        
        while self.running:
            try:
                # Process messages from all subscribed topics
                for topic in self.subscribers.keys():
                    message_data = await self._dequeue_message(topic)
                    
                    if message_data:
                        start_time = time.time()
                        
                        # Deserialize message
                        message_dict = json.loads(message_data)
                        message = QueueMessage(**message_dict)
                        
                        # Process message
                        success = await self._process_message(topic, message)
                        
                        # Update metrics
                        processing_time = time.time() - start_time
                        self._update_processing_metrics(processing_time, success)
                        
                        if success:
                            self.metrics.messages_processed += 1
                        else:
                            self.metrics.messages_failed += 1
                
                # Short sleep to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"👷 Worker {worker_id} stopped")
    
    async def _dequeue_message(self, topic: str) -> Optional[str]:
        """Dequeue highest priority message from topic"""
        if not self.redis_client:
            return None
        
        queue_key = f"queue:{topic}"
        
        # Get highest priority message (highest score)
        result = await self.redis_client.zpopmax(queue_key)
        
        if result:
            return result[0][0].decode() if isinstance(result[0][0], bytes) else result[0][0]
        
        return None
    
    async def _process_message(self, topic: str, message: QueueMessage) -> bool:
        """Process message with handlers"""
        try:
            handlers = self.subscribers.get(topic, [])
            
            if not handlers:
                logger.warning(f"⚠️ No handlers for topic '{topic}'")
                return False
            
            # Execute all handlers for the topic
            for handler in handlers:
                await handler(message)
            
            logger.debug(f"✅ Message processed successfully: {message.id}")
            return True
            
        except Exception as e:
            # Handle message retry logic
            if message.retry_count < message.max_retries:
                message.retry_count += 1
                message.status = MessageStatus.RETRYING
                
                # Re-queue with exponential backoff
                delay = 2 ** message.retry_count
                await self._schedule_delayed_message(topic, json.dumps(message.__dict__), delay)
                
                logger.warning(f"⚠️ Message retry {message.retry_count}/{message.max_retries}: {message.id}")
            else:
                message.status = MessageStatus.DEAD_LETTER
                await self._send_to_dead_letter_queue(topic, message)
                
                logger.error(f"❌ Message moved to dead letter queue: {message.id}")
            
            logger.error(f"❌ Message processing failed: {e}")
            return False
    
    async def _delayed_message_processor(self):
        """Process delayed messages"""
        logger.info("⏰ Delayed message processor started")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Check all delayed queues
                for topic in self.subscribers.keys():
                    delayed_key = f"delayed:{topic}"
                    
                    # Get messages ready for processing
                    ready_messages = await self.redis_client.zrangebyscore(
                        delayed_key, 0, current_time, withscores=True
                    )
                    
                    for message_data, score in ready_messages:
                        # Move to regular queue
                        message_str = message_data.decode() if isinstance(message_data, bytes) else message_data
                        message_dict = json.loads(message_str)
                        priority = MessagePriority(message_dict.get('priority', 'normal'))
                        
                        await self._enqueue_message(topic, message_str, priority)
                        
                        # Remove from delayed queue
                        await self.redis_client.zrem(delayed_key, message_data)
                
                await asyncio.sleep(1)  # Check every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Delayed message processor error: {e}")
                await asyncio.sleep(5)
        
        logger.info("⏰ Delayed message processor stopped")
    
    async def _send_to_dead_letter_queue(self, topic: str, message: QueueMessage):
        """Send message to dead letter queue"""
        if not self.redis_client:
            return
        
        dead_letter_key = f"dead_letter:{topic}"
        message_data = json.dumps({
            **message.__dict__,
            'created_at': message.created_at.isoformat()
        })
        
        await self.redis_client.lpush(dead_letter_key, message_data)
    
    def _update_processing_metrics(self, processing_time: float, success: bool):
        """Update processing time metrics"""
        total_processed = self.metrics.messages_processed + self.metrics.messages_failed
        
        if total_processed > 0:
            self.metrics.avg_processing_time = (
                (self.metrics.avg_processing_time * (total_processed - 1) + processing_time)
                / total_processed
            )
    
    async def health_check(self) -> bool:
        """Perform message queue health check"""
        try:
            # Test Redis connection
            if self.redis_client:
                await self.redis_client.ping()
            
            # Test Celery if configured
            if self.celery_app:
                # Check if Celery workers are available
                stats = self.celery_app.control.inspect().stats()
                if not stats:
                    logger.warning("⚠️ No Celery workers available")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Message queue health check failed: {e}")
            return False
    
    def get_metrics(self) -> QueueMetrics:
        """Get queue metrics"""
        return self.metrics

# Global message queue instance
message_queue_core = MessageQueueCore()

# Convenience functions
async def publish_message(topic: str, payload: Dict[str, Any], 
                         priority: MessagePriority = MessagePriority.NORMAL,
                         delay: Optional[int] = None) -> str:
    """Publish message to queue"""
    return await message_queue_core.publish(topic, payload, priority, delay)

async def subscribe_to_topic(topic: str, handler: Callable[[QueueMessage], Coroutine[Any, Any, None]]):
    """Subscribe to topic"""
    await message_queue_core.subscribe(topic, handler)

async def start_queue_workers(num_workers: Optional[int] = None):
    """Start queue workers"""
    await message_queue_core.start_workers(num_workers)

async def stop_queue_workers():
    """Stop queue workers"""
    await message_queue_core.stop_workers()

# Module exports
__all__ = [
    "MessageQueueCore", "QueueMessage", "QueueConfig", "QueueMetrics",
    "QueueType", "MessagePriority", "MessageStatus", "message_queue_core",
    "publish_message", "subscribe_to_topic", "start_queue_workers", "stop_queue_workers"
]