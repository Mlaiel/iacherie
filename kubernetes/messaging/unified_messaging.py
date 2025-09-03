"""
IA Influencer Agent - Unified Messaging Interface
Enterprise messaging system with multiple backend support

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
import uuid
import sys
import os

from messaging_config import MessagingConfig, MessagingBackend

logger = logging.getLogger(__name__)


class MessagePriority(int, Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 3
    HIGH = 5
    CRITICAL = 10


class MessageStatus(str, Enum):
    """Message status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


@dataclass
class Message:
    """Unified message structure"""
    id: str
    queue_name: str
    data: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    created_at: datetime = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0
    status: MessageStatus = MessageStatus.PENDING
    error_message: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.headers is None:
            self.headers = {}
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Enum):
                data[key] = value.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        # Convert ISO strings back to datetime objects
        for field in ['created_at', 'scheduled_at', 'expires_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert enum values
        if 'priority' in data:
            data['priority'] = MessagePriority(data['priority'])
        if 'status' in data:
            data['status'] = MessageStatus(data['status'])
            
        return cls(**data)


@dataclass
class QueueStats:
    """Queue statistics"""
    queue_name: str
    pending_messages: int = 0
    processing_messages: int = 0
    completed_messages: int = 0
    failed_messages: int = 0
    dead_letter_messages: int = 0
    consumer_count: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class MessageBackend(ABC):
    """Abstract base class for message backends"""
    
    def __init__(self, config: MessagingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the backend"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the backend"""
        pass
    
    @abstractmethod
    async def publish(self, message: Message) -> str:
        """Publish a message"""
        pass
    
    @abstractmethod
    async def consume(self, queue_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Consume a message"""
        pass
    
    @abstractmethod
    async def ack(self, message: Message) -> None:
        """Acknowledge message processing"""
        pass
    
    @abstractmethod
    async def nack(self, message: Message, requeue: bool = True) -> None:
        """Negative acknowledge message"""
        pass
    
    @abstractmethod
    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Get queue statistics"""
        pass
    
    @abstractmethod
    async def purge_queue(self, queue_name: str) -> int:
        """Purge all messages from queue"""
        pass


class UnifiedMessagingSystem:
    """Unified messaging system that can use multiple backends"""
    
    def __init__(self, config: Optional[MessagingConfig] = None):
        self.config = config or MessagingConfig.from_env()
        self.backends: Dict[MessagingBackend, MessageBackend] = {}
        self.primary_backend: Optional[MessageBackend] = None
        self.dead_letter_queues: Dict[str, str] = {}
        self.retry_handlers: Dict[str, Callable] = {}
        self.consumers: Dict[str, List[asyncio.Task]] = {}
        self.is_running = False
        
        # Statistics
        self.stats: Dict[str, QueueStats] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
    async def initialize(self) -> None:
        """Initialize the messaging system"""
        try:
            # Initialize backends based on configuration
            if self.config.primary_backend == MessagingBackend.REDIS:
                sys.path.append(os.path.dirname(__file__))
                from backends.redis_backend import RedisBackend
                self.primary_backend = RedisBackend(self.config)
                await self.primary_backend.connect()
                self.backends[MessagingBackend.REDIS] = self.primary_backend
            
            # Add additional backends as needed
            if self.config.enable_rabbitmq:
                try:
                    from backends.rabbitmq_backend import RabbitMQBackend
                    rabbitmq_backend = RabbitMQBackend(self.config)
                    await rabbitmq_backend.connect()
                    self.backends[MessagingBackend.RABBITMQ] = rabbitmq_backend
                except ImportError:
                    logger.warning("RabbitMQ backend not available")
            
            if self.config.enable_kafka:
                try:
                    from backends.kafka_backend import KafkaBackend
                    kafka_backend = KafkaBackend(self.config)
                    await kafka_backend.connect()
                    self.backends[MessagingBackend.KAFKA] = kafka_backend
                except ImportError:
                    logger.warning("Kafka backend not available")
            
            self.is_running = True
            logger.info("Unified messaging system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize messaging system: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown the messaging system"""
        self.is_running = False
        
        # Stop all consumers
        for queue_name, tasks in self.consumers.items():
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Disconnect from all backends
        for backend in self.backends.values():
            try:
                await backend.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting backend: {e}")
        
        logger.info("Messaging system shutdown complete")
    
    async def publish(self, queue_name: str, data: Dict[str, Any], 
                     priority: MessagePriority = MessagePriority.NORMAL,
                     delay: Optional[float] = None,
                     correlation_id: Optional[str] = None,
                     reply_to: Optional[str] = None,
                     headers: Optional[Dict[str, str]] = None) -> str:
        """Publish a message to a queue"""
        
        if not self.primary_backend:
            raise RuntimeError("Messaging system not initialized")
        
        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            queue_name=queue_name,
            data=data,
            priority=priority,
            scheduled_at=datetime.utcnow() + timedelta(seconds=delay) if delay else None,
            correlation_id=correlation_id,
            reply_to=reply_to,
            headers=headers or {},
            max_retries=self.config.max_retries
        )
        
        # Publish to primary backend
        try:
            message_id = await self.primary_backend.publish(message)
            logger.debug(f"Published message {message_id} to queue {queue_name}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish message to {queue_name}: {e}")
            raise
    
    async def consume(self, queue_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Consume a message from a queue"""
        if not self.primary_backend:
            raise RuntimeError("Messaging system not initialized")
        
        try:
            message = await self.primary_backend.consume(queue_name, timeout)
            if message:
                logger.debug(f"Consumed message {message.id} from queue {queue_name}")
            return message
        except Exception as e:
            logger.error(f"Failed to consume from {queue_name}: {e}")
            raise
    
    async def ack(self, message: Message, success: bool = True, error: Optional[str] = None) -> None:
        """Acknowledge message processing"""
        if not self.primary_backend:
            raise RuntimeError("Messaging system not initialized")
        
        try:
            if success:
                await self.primary_backend.ack(message)
                message.status = MessageStatus.COMPLETED
                logger.debug(f"Acknowledged message {message.id}")
            else:
                # Handle retry logic
                if message.retry_count < message.max_retries:
                    await self._retry_message(message, error)
                else:
                    await self._send_to_dead_letter(message, error)
                
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message.id}: {e}")
            raise
    
    async def _retry_message(self, message: Message, error: Optional[str] = None) -> None:
        """Retry a failed message"""
        message.retry_count += 1
        message.status = MessageStatus.RETRYING
        message.error_message = error
        
        # Calculate retry delay with exponential backoff
        retry_delay = message.retry_delay * (self.config.retry_backoff_factor ** (message.retry_count - 1))
        
        # Republish with delay
        await self.publish(
            queue_name=message.queue_name,
            data=message.data,
            priority=message.priority,
            delay=retry_delay,
            correlation_id=message.correlation_id,
            reply_to=message.reply_to,
            headers=message.headers
        )
        
        # Acknowledge the original message
        await self.primary_backend.ack(message)
        
        logger.info(f"Scheduled retry {message.retry_count} for message {message.id} with delay {retry_delay}s")
    
    async def _send_to_dead_letter(self, message: Message, error: Optional[str] = None) -> None:
        """Send message to dead letter queue"""
        dlq_name = f"{message.queue_name}.dlq"
        message.status = MessageStatus.DEAD_LETTER
        message.error_message = error
        
        dlq_data = message.to_dict()
        dlq_data['original_queue'] = message.queue_name
        dlq_data['dlq_timestamp'] = datetime.utcnow().isoformat()
        
        await self.publish(
            queue_name=dlq_name,
            data=dlq_data,
            priority=MessagePriority.HIGH
        )
        
        # Acknowledge the original message
        await self.primary_backend.ack(message)
        
        logger.warning(f"Sent message {message.id} to dead letter queue after {message.retry_count} failures")
    
    async def register_consumer(self, queue_name: str, handler: Callable[[Message], None], 
                              concurrency: int = 1) -> None:
        """Register a message consumer"""
        self.message_handlers[queue_name] = handler
        
        # Start consumer tasks
        tasks = []
        for i in range(concurrency):
            task = asyncio.create_task(
                self._consumer_loop(queue_name, handler, f"consumer-{i}")
            )
            tasks.append(task)
        
        self.consumers[queue_name] = tasks
        logger.info(f"Registered {concurrency} consumers for queue {queue_name}")
    
    async def _consumer_loop(self, queue_name: str, handler: Callable, consumer_id: str) -> None:
        """Consumer loop for processing messages"""
        logger.info(f"Starting consumer {consumer_id} for queue {queue_name}")
        
        while self.is_running:
            try:
                # Consume message
                message = await self.consume(queue_name, timeout=1.0)
                if not message:
                    continue
                
                # Process message
                try:
                    await handler(message)
                    await self.ack(message, success=True)
                except Exception as e:
                    logger.error(f"Handler failed for message {message.id}: {e}")
                    await self.ack(message, success=False, error=str(e))
                
            except Exception as e:
                logger.error(f"Consumer {consumer_id} error: {e}")
                await asyncio.sleep(1)  # Backoff on error
        
        logger.info(f"Consumer {consumer_id} for queue {queue_name} stopped")
    
    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Get statistics for a queue"""
        if not self.primary_backend:
            raise RuntimeError("Messaging system not initialized")
        
        return await self.primary_backend.get_queue_stats(queue_name)
    
    async def get_all_stats(self) -> Dict[str, QueueStats]:
        """Get statistics for all queues"""
        stats = {}
        for queue_name in self.consumers.keys():
            stats[queue_name] = await self.get_queue_stats(queue_name)
        return stats