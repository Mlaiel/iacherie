"""Message Queue Template for iacherie Platform
Enterprise-grade asynchronous message processing and task management

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
import json
import pickle
from typing import Dict, Any, Optional, List, Callable, Union, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from abc import ABC, abstractmethod

from pydantic import BaseModel, validator, Field
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from celery import Celery
from celery.result import AsyncResult
import aiokafka
from kombu import Queue, Exchange

from core.config import get_settings
from core.database import get_db_session, Base
from core.monitoring import get_monitoring_client
from utils.exceptions import QueueException, TaskException
from monitoring.queue_metrics import QueueMetrics

logger = logging.getLogger(__name__)
settings = get_settings()

T = TypeVar('T')


class QueueType(str, Enum):
    """Types of message queues"""
    REDIS = "redis"
    CELERY = "celery"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    MEMORY = "memory"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    """Message types for processing"""
    CONTENT_PROCESSING = "content.processing"
    AI_ANALYSIS = "ai.analysis"
    NOTIFICATION = "notification"
    EMAIL = "email"
    WEBHOOK_DELIVERY = "webhook.delivery"
    DATA_SYNC = "data.sync"
    ANALYTICS = "analytics"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    MONETIZATION = "monetization"


@dataclass
class QueueConfig:
    """Configuration for message queue"""
    queue_type: QueueType = QueueType.REDIS
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    kafka_bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    rabbitmq_url: str = "amqp://guest@localhost:5672//"
    default_queue_name: str = "iacherie_tasks"
    max_retries: int = 3
    retry_delay_seconds: int = 60
    task_timeout_seconds: int = 300
    result_expires_seconds: int = 3600
    enable_monitoring: bool = True
    prefetch_count: int = 10


class QueueMessage(BaseModel):
    """Message model for queue processing"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType = Field(..., description="Type of message")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    payload: Dict[str, Any] = Field(..., description="Message payload")
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None)
    reply_to: Optional[str] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    max_retries: int = Field(default=3)
    retry_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('payload')
    def validate_payload(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Payload must be a dictionary')
        return v


class TaskResult(BaseModel):
    """Task execution result"""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Task status")
    result: Optional[Any] = Field(default=None, description="Task result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    processing_time_ms: Optional[float] = Field(default=None)
    retry_count: int = Field(default=0)
    worker_id: Optional[str] = Field(default=None)


class QueueTask(Base):
    """Database model for task tracking"""
    __tablename__ = "queue_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(String(255), nullable=False, unique=True, index=True)
    message_type = Column(String(100), nullable=False, index=True)
    priority = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    queue_name = Column(String(255), nullable=False, index=True)
    worker_id = Column(String(255), nullable=True)
    payload = Column(JSONB, nullable=False)
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)


class BaseMessageQueue(ABC, Generic[T]):
    """Abstract base class for message queues"""

    def __init__(self, config: QueueConfig):
        self.config = config
        self.metrics = QueueMetrics()
        self.task_handlers: Dict[MessageType, Callable] = {}
        self.is_running = False

    @abstractmethod
    async def initialize(self):
        """Initialize the message queue"""
        pass

    @abstractmethod
    async def publish(
        self,
        message: QueueMessage,
        queue_name: Optional[str] = None,
        delay_seconds: Optional[int] = None
    ) -> str:
        """Publish message to queue"""
        pass

    @abstractmethod
    async def consume(
        self,
        queue_name: Optional[str] = None,
        batch_size: int = 1
    ) -> List[QueueMessage]:
        """Consume messages from queue"""
        pass

    @abstractmethod
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task execution result"""
        pass

    @abstractmethod
    async def close(self):
        """Close queue connection"""
        pass

    def register_task_handler(self, message_type: MessageType, handler: Callable):
        """Register a task handler for specific message type"""
        self.task_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def process_message(self, message: QueueMessage) -> TaskResult:
        """Process a message with registered handler"""
        start_time = datetime.utcnow()
        task_result = TaskResult(
            task_id=message.message_id,
            status=TaskStatus.PROCESSING,
            started_at=start_time,
            retry_count=message.retry_count
        )

        try:
            # Find handler for message type
            handler = self.task_handlers.get(message.message_type)
            if not handler:
                raise TaskException(f"No handler registered for message type: {message.message_type}")

            # Execute handler
            result = await handler(message)
            
            # Update task result
            task_result.status = TaskStatus.COMPLETED
            task_result.result = result
            task_result.completed_at = datetime.utcnow()
            task_result.processing_time_ms = (
                task_result.completed_at - start_time
            ).total_seconds() * 1000

            await self.metrics.increment_tasks_completed(message.message_type.value)
            logger.debug(f"Task {message.message_id} completed successfully")

        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.completed_at = datetime.utcnow()
            task_result.processing_time_ms = (
                task_result.completed_at - start_time
            ).total_seconds() * 1000

            await self.metrics.increment_tasks_failed(message.message_type.value)
            logger.error(f"Task {message.message_id} failed: {e}")

        return task_result

    async def start_worker(self, queue_name: Optional[str] = None):
        """Start worker to process messages"""
        self.is_running = True
        worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Starting worker {worker_id} for queue {queue_name or self.config.default_queue_name}")

        while self.is_running:
            try:
                # Consume messages
                messages = await self.consume(queue_name, self.config.prefetch_count)
                
                if not messages:
                    await asyncio.sleep(1)
                    continue

                # Process messages concurrently
                tasks = []
                for message in messages:
                    task = asyncio.create_task(self._process_with_tracking(message, worker_id))
                    tasks.append(task)

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)

    async def _process_with_tracking(self, message: QueueMessage, worker_id: str):
        """Process message with database tracking"""
        async with get_db_session() as session:
            try:
                # Update task status in database
                task = QueueTask(
                    task_id=message.message_id,
                    message_type=message.message_type.value,
                    priority=message.priority.value,
                    status=TaskStatus.PROCESSING.value,
                    queue_name=self.config.default_queue_name,
                    worker_id=worker_id,
                    payload=message.payload,
                    retry_count=message.retry_count,
                    max_retries=message.max_retries,
                    started_at=datetime.utcnow()
                )
                session.add(task)
                await session.commit()

                # Process message
                result = await self.process_message(message)

                # Update task with result
                task.status = result.status.value
                task.result = result.result if isinstance(result.result, dict) else {"data": result.result}
                task.error_message = result.error
                task.processing_time_ms = result.processing_time_ms
                task.completed_at = result.completed_at
                await session.commit()

            except Exception as e:
                logger.error(f"Failed to track task {message.message_id}: {e}")
                try:
                    task.status = TaskStatus.FAILED.value
                    task.error_message = str(e)
                    task.completed_at = datetime.utcnow()
                    await session.commit()
                except:
                    pass

    def stop_worker(self):
        """Stop the worker"""
        self.is_running = False
        logger.info("Worker stop requested")


class RedisMessageQueue(BaseMessageQueue):
    """Redis-based message queue implementation"""

    def __init__(self, config: QueueConfig):
        super().__init__(config)
        self.redis: Optional[aioredis.Redis] = None

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=False  # For binary data support
            )
            logger.info("Redis message queue initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis queue: {e}")
            raise QueueException(f"Redis initialization failed: {e}")

    async def publish(
        self,
        message: QueueMessage,
        queue_name: Optional[str] = None,
        delay_seconds: Optional[int] = None
    ) -> str:
        """Publish message to Redis queue"""
        try:
            queue_key = queue_name or self.config.default_queue_name
            
            # Serialize message
            message_data = message.dict()
            serialized_message = json.dumps(message_data, default=str)

            if delay_seconds:
                # Use Redis sorted set for delayed messages
                score = (datetime.utcnow() + timedelta(seconds=delay_seconds)).timestamp()
                await self.redis.zadd(f"{queue_key}:delayed", {serialized_message: score})
            else:
                # Add to regular queue
                await self.redis.lpush(queue_key, serialized_message)

            await self.metrics.increment_messages_published(message.message_type.value)
            logger.debug(f"Published message {message.message_id} to queue {queue_key}")
            
            return message.message_id

        except Exception as e:
            logger.error(f"Failed to publish message to Redis: {e}")
            raise QueueException(f"Message publishing failed: {e}")

    async def consume(
        self,
        queue_name: Optional[str] = None,
        batch_size: int = 1
    ) -> List[QueueMessage]:
        """Consume messages from Redis queue"""
        try:
            queue_key = queue_name or self.config.default_queue_name
            messages = []

            # Process delayed messages first
            await self._process_delayed_messages(queue_key)

            # Consume from regular queue
            for _ in range(batch_size):
                message_data = await self.redis.brpop(queue_key, timeout=1)
                if not message_data:
                    break

                try:
                    serialized_message = message_data[1].decode('utf-8')
                    message_dict = json.loads(serialized_message)
                    message = QueueMessage(**message_dict)
                    messages.append(message)
                    
                    await self.metrics.increment_messages_consumed(message.message_type.value)
                    
                except Exception as e:
                    logger.error(f"Failed to deserialize message: {e}")

            return messages

        except Exception as e:
            logger.error(f"Failed to consume messages from Redis: {e}")
            return []

    async def _process_delayed_messages(self, queue_key: str):
        """Move delayed messages that are ready to the main queue"""
        try:
            now = datetime.utcnow().timestamp()
            
            # Get messages ready for processing
            ready_messages = await self.redis.zrangebyscore(
                f"{queue_key}:delayed", 0, now, withscores=False
            )

            if ready_messages:
                # Move to main queue
                for message in ready_messages:
                    await self.redis.lpush(queue_key, message)
                
                # Remove from delayed queue
                await self.redis.zremrangebyscore(f"{queue_key}:delayed", 0, now)

        except Exception as e:
            logger.error(f"Failed to process delayed messages: {e}")

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result from Redis"""
        try:
            result_key = f"task_result:{task_id}"
            result_data = await self.redis.get(result_key)
            
            if result_data:
                result_dict = json.loads(result_data.decode('utf-8'))
                return TaskResult(**result_dict)
            
            return None

        except Exception as e:
            logger.error(f"Failed to get task result: {e}")
            return None

    async def set_task_result(self, task_result: TaskResult):
        """Store task result in Redis"""
        try:
            result_key = f"task_result:{task_result.task_id}"
            result_data = json.dumps(task_result.dict(), default=str)
            
            await self.redis.setex(
                result_key,
                self.config.result_expires_seconds,
                result_data
            )

        except Exception as e:
            logger.error(f"Failed to store task result: {e}")

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()


class CeleryMessageQueue(BaseMessageQueue):
    """Celery-based message queue implementation"""

    def __init__(self, config: QueueConfig):
        super().__init__(config)
        self.celery_app = None
        self._initialize_celery()

    def _initialize_celery(self):
        """Initialize Celery application"""
        self.celery_app = Celery(
            'iacherie_tasks',
            broker=self.config.celery_broker_url,
            backend=self.config.celery_result_backend
        )

        # Configure Celery
        self.celery_app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_track_started=True,
            task_time_limit=self.config.task_timeout_seconds,
            task_soft_time_limit=self.config.task_timeout_seconds - 30,
            result_expires=self.config.result_expires_seconds,
            worker_prefetch_multiplier=self.config.prefetch_count,
        )

        # Define default queue
        self.celery_app.conf.task_routes = {
            '*': {'queue': self.config.default_queue_name}
        }

    async def initialize(self):
        """Initialize Celery queue"""
        logger.info("Celery message queue initialized")

    @celery_app.task(bind=True, max_retries=3)
    def _process_celery_task(self, message_data):
        """Celery task wrapper for message processing"""
        try:
            message = QueueMessage(**message_data)
            
            # This would need to be adapted for sync Celery context
            # In practice, you'd have separate Celery tasks for each message type
            return {"status": "completed", "message_id": message.message_id}
            
        except Exception as e:
            logger.error(f"Celery task failed: {e}")
            raise

    async def publish(
        self,
        message: QueueMessage,
        queue_name: Optional[str] = None,
        delay_seconds: Optional[int] = None
    ) -> str:
        """Publish message to Celery"""
        try:
            message_data = message.dict()
            
            task_options = {}
            if queue_name:
                task_options['queue'] = queue_name
            if delay_seconds:
                task_options['countdown'] = delay_seconds

            # Send task to Celery
            result = self._process_celery_task.apply_async(
                args=[message_data],
                **task_options
            )

            await self.metrics.increment_messages_published(message.message_type.value)
            logger.debug(f"Published message {message.message_id} to Celery")
            
            return result.id

        except Exception as e:
            logger.error(f"Failed to publish message to Celery: {e}")
            raise QueueException(f"Message publishing failed: {e}")

    async def consume(
        self,
        queue_name: Optional[str] = None,
        batch_size: int = 1
    ) -> List[QueueMessage]:
        """Celery handles consumption automatically via workers"""
        # This method is not used with Celery as it handles consumption internally
        return []

    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result from Celery"""
        try:
            async_result = AsyncResult(task_id, app=self.celery_app)
            
            if async_result.ready():
                if async_result.successful():
                    return TaskResult(
                        task_id=task_id,
                        status=TaskStatus.COMPLETED,
                        result=async_result.result,
                        completed_at=datetime.utcnow()
                    )
                else:
                    return TaskResult(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        error=str(async_result.info),
                        completed_at=datetime.utcnow()
                    )
            else:
                return TaskResult(
                    task_id=task_id,
                    status=TaskStatus.PROCESSING if async_result.state == 'STARTED' else TaskStatus.PENDING
                )

        except Exception as e:
            logger.error(f"Failed to get Celery task result: {e}")
            return None

    async def close(self):
        """Close Celery connection"""
        if self.celery_app:
            self.celery_app.close()


class QueueManager:
    """Manager for message queues with multiple backends"""

    def __init__(self, config: QueueConfig):
        self.config = config
        self.queues: Dict[QueueType, BaseMessageQueue] = {}
        self.default_queue: Optional[BaseMessageQueue] = None

    async def initialize(self):
        """Initialize queue manager and backends"""
        try:
            # Initialize Redis queue
            redis_queue = RedisMessageQueue(self.config)
            await redis_queue.initialize()
            self.queues[QueueType.REDIS] = redis_queue
            
            # Initialize Celery queue
            celery_queue = CeleryMessageQueue(self.config)
            await celery_queue.initialize()
            self.queues[QueueType.CELERY] = celery_queue

            # Set default queue
            self.default_queue = self.queues[self.config.queue_type]

            logger.info(f"Queue manager initialized with {len(self.queues)} backends")

        except Exception as e:
            logger.error(f"Failed to initialize queue manager: {e}")
            raise

    async def publish(
        self,
        message: QueueMessage,
        queue_type: Optional[QueueType] = None,
        queue_name: Optional[str] = None,
        delay_seconds: Optional[int] = None
    ) -> str:
        """Publish message to specified queue"""
        try:
            target_queue = self.queues.get(queue_type or self.config.queue_type)
            if not target_queue:
                target_queue = self.default_queue

            if not target_queue:
                raise QueueException("No queue available for publishing")

            return await target_queue.publish(message, queue_name, delay_seconds)

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

    def get_queue(self, queue_type: QueueType) -> Optional[BaseMessageQueue]:
        """Get queue instance for specific type"""
        return self.queues.get(queue_type)

    async def start_worker(
        self,
        queue_type: Optional[QueueType] = None,
        queue_name: Optional[str] = None
    ):
        """Start worker for specified queue"""
        target_queue = self.queues.get(queue_type or self.config.queue_type)
        if target_queue:
            await target_queue.start_worker(queue_name)

    async def close_all(self):
        """Close all queue connections"""
        for queue in self.queues.values():
            try:
                await queue.close()
            except Exception as e:
                logger.error(f"Error closing queue: {e}")


# Global queue manager
queue_manager = QueueManager(QueueConfig())

async def get_queue_manager() -> QueueManager:
    """Dependency to get queue manager"""
    return queue_manager


# Example task handlers
async def process_content_task(message: QueueMessage) -> Dict[str, Any]:
    """Example content processing task"""
    content_id = message.payload.get('content_id')
    action = message.payload.get('action')
    
    logger.info(f"Processing content {content_id} with action {action}")
    
    # Simulate processing
    await asyncio.sleep(2)
    
    return {
        "content_id": content_id,
        "action": action,
        "processed_at": datetime.utcnow().isoformat(),
        "status": "completed"
    }


async def send_notification_task(message: QueueMessage) -> Dict[str, Any]:
    """Example notification sending task"""
    recipient = message.payload.get('recipient')
    notification_type = message.payload.get('type')
    content = message.payload.get('content')
    
    logger.info(f"Sending {notification_type} notification to {recipient}")
    
    # Simulate sending
    await asyncio.sleep(1)
    
    return {
        "recipient": recipient,
        "type": notification_type,
        "sent_at": datetime.utcnow().isoformat(),
        "status": "sent"
    }


# Setup example handlers
async def setup_task_handlers():
    """Setup task handlers for different message types"""
    redis_queue = queue_manager.get_queue(QueueType.REDIS)
    if redis_queue:
        redis_queue.register_task_handler(MessageType.CONTENT_PROCESSING, process_content_task)
        redis_queue.register_task_handler(MessageType.NOTIFICATION, send_notification_task)


# Example usage
async def example_queue_usage():
    """Example of how to use the message queue system"""
    await queue_manager.initialize()
    await setup_task_handlers()
    
    # Publish a content processing task
    content_message = QueueMessage(
        message_type=MessageType.CONTENT_PROCESSING,
        priority=TaskPriority.HIGH,
        payload={
            "content_id": "content_123",
            "action": "process_video",
            "user_id": "user_456"
        },
        correlation_id="req_789"
    )
    
    task_id = await queue_manager.publish(content_message)
    logger.info(f"Published content processing task: {task_id}")
    
    # Publish a notification task with delay
    notification_message = QueueMessage(
        message_type=MessageType.NOTIFICATION,
        priority=TaskPriority.NORMAL,
        payload={
            "recipient": "user@example.com",
            "type": "email",
            "content": "Your content has been processed successfully"
        }
    )
    
    delayed_task_id = await queue_manager.publish(
        notification_message,
        delay_seconds=300  # Send after 5 minutes
    )
    logger.info(f"Published delayed notification task: {delayed_task_id}")


if __name__ == "__main__":
    async def main():
        await example_queue_usage()
        
        # Start worker (this would normally run in a separate process)
        await queue_manager.start_worker()

    asyncio.run(main())