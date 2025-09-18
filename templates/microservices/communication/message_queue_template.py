"""
Message Queue Template for Enterprise Microservices
==================================================

Production-ready message queue implementation with:
- Redis Streams integration
- Dead letter queue handling
- Message persistence and retry logic
- Consumer group management
- Monitoring and metrics
- Circuit breaker patterns

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Message Queue Expert
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as redis
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge

from ..base_microservice import BaseMicroservice
from ..circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class QueueMessage:
    """Queue message structure"""
    id: str
    type: str
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    created_at: datetime = None
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    correlation_id: Optional[str] = None
    timeout: Optional[int] = 30
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class MessageQueueConfig(BaseModel):
    """Message queue configuration"""
    redis_url: str = Field(..., description="Redis connection URL")
    stream_name: str = Field(..., description="Redis stream name")
    consumer_group: str = Field(..., description="Consumer group name")
    consumer_name: str = Field(..., description="Consumer name")
    batch_size: int = Field(default=10, description="Message batch size")
    block_timeout: int = Field(default=1000, description="Block timeout in ms")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: int = Field(default=5, description="Retry delay in seconds")
    dead_letter_queue: str = Field(default="dlq", description="Dead letter queue name")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")


class MessageQueueTemplate(BaseMicroservice):
    """
    Enterprise Message Queue Template
    
    Provides comprehensive message queue functionality with:
    - High-throughput message processing
    - Dead letter queue handling
    - Consumer group management
    - Circuit breaker protection
    - Prometheus metrics integration
    - Message persistence and durability
    """
    
    def __init__(self, config: MessageQueueConfig):
        super().__init__()
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=redis.RedisError
        )
        
        # Message handlers registry
        self.message_handlers: Dict[str, Callable] = {}
        self.middleware_stack: List[Callable] = []
        
        # Metrics
        if config.monitoring_enabled:
            self._setup_metrics()
    
    def _setup_metrics(self):
        """Setup Prometheus metrics"""
        self.messages_produced = Counter(
            'message_queue_messages_produced_total',
            'Total messages produced',
            ['queue_name', 'message_type', 'priority']
        )
        
        self.messages_consumed = Counter(
            'message_queue_messages_consumed_total',
            'Total messages consumed',
            ['queue_name', 'message_type', 'status']
        )
        
        self.message_processing_time = Histogram(
            'message_queue_processing_duration_seconds',
            'Message processing duration',
            ['queue_name', 'message_type']
        )
        
        self.queue_size = Gauge(
            'message_queue_size',
            'Current queue size',
            ['queue_name']
        )
        
        self.dead_letter_queue_size = Gauge(
            'message_queue_dlq_size',
            'Dead letter queue size',
            ['queue_name']
        )
    
    async def start(self):
        """Start message queue service"""
        await super().start()
        
        # Initialize Redis connection
        self.redis_client = redis.from_url(
            self.config.redis_url,
            decode_responses=True,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={}
        )
        
        # Create consumer group if not exists
        try:
            await self.redis_client.xgroup_create(
                self.config.stream_name,
                self.config.consumer_group,
                id='0',
                mkstream=True
            )
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        
        logger.info(f"Message queue started - Stream: {self.config.stream_name}")
    
    async def stop(self):
        """Stop message queue service"""
        if self.redis_client:
            await self.redis_client.close()
        await super().stop()
        logger.info("Message queue stopped")
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to processing pipeline"""
        self.middleware_stack.append(middleware)
    
    @CircuitBreaker.circuit_breaker
    async def produce_message(
        self,
        message_type: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> str:
        """
        Produce message to queue
        
        Args:
            message_type: Type of message
            payload: Message payload
            priority: Message priority
            correlation_id: Correlation ID for tracing
            timeout: Message timeout
            
        Returns:
            Message ID
        """
        message = QueueMessage(
            id=f"msg_{int(time.time() * 1000)}_{hash(json.dumps(payload)) % 10000}",
            type=message_type,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id,
            timeout=timeout or self.config.max_retries * self.config.retry_delay
        )
        
        # Serialize message
        message_data = {
            'id': message.id,
            'type': message.type,
            'payload': json.dumps(message.payload),
            'priority': message.priority.value,
            'created_at': message.created_at.isoformat(),
            'correlation_id': message.correlation_id,
            'timeout': message.timeout,
            'retry_count': message.retry_count,
            'max_retries': message.max_retries
        }
        
        # Add to stream with priority-based ID
        priority_prefix = f"{10 - message.priority.value:02d}"
        stream_id = f"{priority_prefix}-{int(time.time() * 1000)}-{hash(message.id) % 1000}"
        
        result = await self.redis_client.xadd(
            self.config.stream_name,
            message_data,
            id=stream_id
        )
        
        # Update metrics
        if self.config.monitoring_enabled:
            self.messages_produced.labels(
                queue_name=self.config.stream_name,
                message_type=message_type,
                priority=priority.name.lower()
            ).inc()
        
        logger.debug(f"Produced message: {message.id} -> {result}")
        return message.id
    
    async def consume_messages(self, count: int = None) -> List[QueueMessage]:
        """
        Consume messages from queue
        
        Args:
            count: Number of messages to consume
            
        Returns:
            List of consumed messages
        """
        batch_size = count or self.config.batch_size
        
        try:
            # Read from stream
            messages = await self.redis_client.xreadgroup(
                self.config.consumer_group,
                self.config.consumer_name,
                {self.config.stream_name: '>'},
                count=batch_size,
                block=self.config.block_timeout
            )
            
            processed_messages = []
            
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    try:
                        # Deserialize message
                        message = QueueMessage(
                            id=fields['id'],
                            type=fields['type'],
                            payload=json.loads(fields['payload']),
                            priority=MessagePriority(int(fields['priority'])),
                            created_at=datetime.fromisoformat(fields['created_at']),
                            correlation_id=fields.get('correlation_id'),
                            timeout=int(fields.get('timeout', 30)),
                            retry_count=int(fields.get('retry_count', 0)),
                            max_retries=int(fields.get('max_retries', 3))
                        )
                        
                        processed_messages.append(message)
                        
                        # Acknowledge message
                        await self.redis_client.xack(
                            self.config.stream_name,
                            self.config.consumer_group,
                            msg_id
                        )
                        
                    except Exception as e:
                        logger.error(f"Error processing message {msg_id}: {e}")
                        continue
            
            return processed_messages
            
        except redis.RedisError as e:
            logger.error(f"Redis error consuming messages: {e}")
            return []
    
    async def process_message(self, message: QueueMessage) -> bool:
        """
        Process individual message
        
        Args:
            message: Message to process
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            # Apply middleware
            for middleware in self.middleware_stack:
                message = await middleware(message)
                if message is None:
                    return True  # Message filtered out
            
            # Get handler
            handler = self.message_handlers.get(message.type)
            if not handler:
                logger.warning(f"No handler for message type: {message.type}")
                return False
            
            # Process message
            result = await handler(message)
            
            # Update metrics
            if self.config.monitoring_enabled:
                processing_time = time.time() - start_time
                self.message_processing_time.labels(
                    queue_name=self.config.stream_name,
                    message_type=message.type
                ).observe(processing_time)
                
                self.messages_consumed.labels(
                    queue_name=self.config.stream_name,
                    message_type=message.type,
                    status='success'
                ).inc()
            
            logger.debug(f"Successfully processed message: {message.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            
            # Update metrics
            if self.config.monitoring_enabled:
                self.messages_consumed.labels(
                    queue_name=self.config.stream_name,
                    message_type=message.type,
                    status='error'
                ).inc()
            
            # Handle retry logic
            await self._handle_message_retry(message, str(e))
            return False
    
    async def _handle_message_retry(self, message: QueueMessage, error: str):
        """Handle message retry logic"""
        message.retry_count += 1
        
        if message.retry_count <= message.max_retries:
            # Retry after delay
            await asyncio.sleep(self.config.retry_delay * message.retry_count)
            
            # Re-queue message
            await self.produce_message(
                message.type,
                {**message.payload, '_retry_count': message.retry_count, '_error': error},
                message.priority,
                message.correlation_id
            )
            
            logger.info(f"Retrying message {message.id} (attempt {message.retry_count})")
        else:
            # Move to dead letter queue
            await self._move_to_dead_letter_queue(message, error)
    
    async def _move_to_dead_letter_queue(self, message: QueueMessage, error: str):
        """Move message to dead letter queue"""
        dlq_data = {
            'original_message': json.dumps(message.__dict__, default=str),
            'error': error,
            'failed_at': datetime.utcnow().isoformat(),
            'retry_count': message.retry_count
        }
        
        await self.redis_client.xadd(
            f"{self.config.stream_name}:{self.config.dead_letter_queue}",
            dlq_data
        )
        
        logger.warning(f"Moved message {message.id} to dead letter queue")
    
    async def get_queue_info(self) -> Dict[str, Any]:
        """Get queue information and metrics"""
        try:
            # Stream info
            stream_info = await self.redis_client.xinfo_stream(self.config.stream_name)
            
            # Consumer group info
            groups_info = await self.redis_client.xinfo_groups(self.config.stream_name)
            
            # Dead letter queue size
            dlq_size = await self.redis_client.xlen(
                f"{self.config.stream_name}:{self.config.dead_letter_queue}"
            )
            
            return {
                'stream_name': self.config.stream_name,
                'length': stream_info['length'],
                'consumer_groups': len(groups_info),
                'dead_letter_queue_size': dlq_size,
                'last_generated_id': stream_info['last-generated-id'],
                'first_entry': stream_info.get('first-entry'),
                'last_entry': stream_info.get('last-entry')
            }
            
        except redis.RedisError as e:
            logger.error(f"Error getting queue info: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for message queue"""
        try:
            # Test Redis connection
            await self.redis_client.ping()
            
            # Get queue metrics
            queue_info = await self.get_queue_info()
            
            return {
                'status': 'healthy',
                'redis_connected': True,
                'queue_info': queue_info,
                'circuit_breaker_state': self.circuit_breaker.state.name
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'redis_connected': False,
                'error': str(e),
                'circuit_breaker_state': self.circuit_breaker.state.name
            }


# Example usage and message handlers
async def example_content_processing_handler(message: QueueMessage) -> bool:
    """Example handler for content processing messages"""
    logger.info(f"Processing content: {message.payload.get('content_id')}")
    
    # Simulate processing
    await asyncio.sleep(0.1)
    
    # Process based on content type
    content_type = message.payload.get('content_type')
    if content_type == 'video':
        # Process video content
        logger.info("Processing video content")
    elif content_type == 'audio':
        # Process audio content
        logger.info("Processing audio content")
    elif content_type == 'image':
        # Process image content
        logger.info("Processing image content")
    
    return True


async def example_creator_notification_handler(message: QueueMessage) -> bool:
    """Example handler for creator notifications"""
    logger.info(f"Sending notification to creator: {message.payload.get('creator_id')}")
    
    notification_type = message.payload.get('type')
    if notification_type == 'collaboration_request':
        # Handle collaboration request
        logger.info("Handling collaboration request notification")
    elif notification_type == 'revenue_update':
        # Handle revenue update
        logger.info("Handling revenue update notification")
    
    return True


# Example middleware
async def authentication_middleware(message: QueueMessage) -> Optional[QueueMessage]:
    """Authentication middleware"""
    if 'user_id' not in message.payload:
        logger.warning(f"Message {message.id} missing user_id")
        return None
    
    # Validate user authentication
    user_id = message.payload['user_id']
    # Implement authentication logic here
    
    return message


async def rate_limiting_middleware(message: QueueMessage) -> Optional[QueueMessage]:
    """Rate limiting middleware"""
    # Implement rate limiting logic here
    return message