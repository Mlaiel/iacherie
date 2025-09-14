"""
Message Queue Service module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
📬 MESSAGE QUEUE SERVICE
========================

Asynchronous message queue management service for microservices communication.
Handles reliable message delivery, routing, and processing across the platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.

🎖️ MULTI-EXPERT IMPLEMENTATION:
- Lead Dev IA: AI-powered message routing and intelligent queue management
- Backend Senior: Enterprise message queue infrastructure with high availability
- ML Engineer: ML models for message priority optimization and delivery prediction
- DBA: Optimized message storage and persistence strategies
- Security: Secure message encryption and authenticated communication
- Microservices: Service-to-service communication and event distribution
- Audio Engineer: Audio processing message queues and media delivery
- DevOps: Queue monitoring, performance optimization, and automated scaling
- AI Prompt Engineer: Intelligent message processing and content routing
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from collections import defaultdict, deque
import uuid
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor
import statistics
import pickle
import zlib
import heapq
import threading
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BULK = 4

class MessageStatus(Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"
    RETRYING = "retrying"

class QueueType(Enum):
    """Queue type classification"""
    FIFO = "fifo"
    PRIORITY = "priority"
    DELAY = "delay"
    TOPIC = "topic"
    FANOUT = "fanout"
    DIRECT = "direct"
    DEAD_LETTER = "dead_letter"

class DeliveryMode(Enum):
    """Message delivery modes"""
    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    EXACTLY_ONCE = "exactly_once"

@dataclass
class Message:
    """Message data structure"""
    id: str
    queue_name: str
    payload: Dict[str, Any]
    priority: MessagePriority
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    headers: Dict[str, str] = None
    routing_key: str = ""
    correlation_id: str = ""
    reply_to: str = ""
    content_type: str = "application/json"
    delivery_mode: DeliveryMode = DeliveryMode.AT_LEAST_ONCE
    
    def __post_init__(self) -> None:
        if self.headers is None:
            self.headers = {}

@dataclass
class QueueConfig:
    """Queue configuration"""
    name: str
    queue_type: QueueType
    max_size: int = 10000
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    message_ttl: int = 3600  # seconds
    dead_letter_queue: Optional[str] = None
    auto_acknowledge: bool = False
    persistent: bool = True
    priority_levels: int = 5
    rate_limit: Optional[int] = None  # messages per second
    
@dataclass
class ConsumerConfig:
    """Consumer configuration"""
    id: str
    queue_names: List[str]
    handler: Callable
    prefetch_count: int = 10
    auto_acknowledge: bool = False
    exclusive: bool = False
    durable: bool = True

@dataclass
class QueueMetrics:
    """Queue performance metrics"""
    queue_name: str
    message_count: int
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int
    average_processing_time: float
    throughput_per_second: float
    consumer_count: int
    last_updated: datetime

class MessageQueueService:
    """
    📬 Advanced Message Queue Service
    
    Multi-Expert Implementation:
    - Lead Dev IA: AI-powered routing and intelligent queue optimization
    - Backend Senior: Scalable queue infrastructure with high availability
    - ML Engineer: ML models for message priority and delivery optimization
    - DBA: Optimized message persistence and query strategies
    - Security: Encrypted messaging and secure authentication
    - Microservices: Inter-service communication and event distribution
    - Audio Engineer: Media processing queues and audio delivery
    - DevOps: Queue monitoring, scaling, and performance optimization
    - AI Prompt Engineer: Intelligent message content processing
    """
    
    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        """Initialize message queue service"""
        self.redis_url = redis_url
        self.redis_client = None
        self.executor = ThreadPoolExecutor(max_workers=50)
        
        # Queue management
        self.queues: Dict[str, QueueConfig] = {}
        self.consumers: Dict[str, ConsumerConfig] = {}
        self.active_consumers: Dict[str, asyncio.Task] = {}
        
        # Message storage and tracking
        self.message_store: Dict[str, Message] = {}
        self.priority_queues: Dict[str, List] = defaultdict(list)  # Heap-based priority queues
        self.delayed_messages: List[Tuple[datetime, str]] = []  # Heap for delayed messages
        
        # Dead letter queues
        self.dead_letter_queues: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Metrics and monitoring
        self.queue_metrics: Dict[str, QueueMetrics] = {}
        self.message_metrics: Dict[str, Dict] = defaultdict(dict)
        
        # Rate limiting
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # AI/ML components
        self.priority_optimizer = None
        self.routing_optimizer = None
        
        # Performance tracking
        self.service_metrics = {
            'messages_published': 0,
            'messages_consumed': 0,
            'messages_failed': 0,
            'average_latency': 0.0,
            'queue_count': 0,
            'consumer_count': 0
        }
        
        # Threading locks
        self.queue_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        logger.info("Message Queue Service initialized")
    
    async def initialize(self) -> None:
        """Initialize Redis connection and queue infrastructure"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Load existing queues and consumers
            await self._load_queue_configurations()
            
            # Start background tasks
            asyncio.create_task(self._process_delayed_messages())
            asyncio.create_task(self._monitor_queue_health())
            asyncio.create_task(self._update_metrics())
            asyncio.create_task(self._cleanup_expired_messages())
            
            logger.info("Message Queue Service initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Message Queue Service: {e}")
            raise
    
    async def create_queue(self, config: QueueConfig) -> bool:
        """Create a new message queue with specified configuration"""
        try:
            # Validate configuration
            if config.name in self.queues:
                raise ValueError(f"Queue {config.name} already exists")
            
            # Store queue configuration
            self.queues[config.name] = config
            
            # Initialize queue structures
            if config.queue_type == QueueType.PRIORITY:
                self.priority_queues[config.name] = []
            
            # Create dead letter queue if specified
            if config.dead_letter_queue:
                if config.dead_letter_queue not in self.queues:
                    dlq_config = QueueConfig(
                        name=config.dead_letter_queue,
                        queue_type=QueueType.FIFO,
                        max_size=config.max_size,
                        persistent=True
                    )
                    await self.create_queue(dlq_config)
            
            # Initialize metrics
            self.queue_metrics[config.name] = QueueMetrics(
                queue_name=config.name,
                message_count=0,
                pending_count=0,
                processing_count=0,
                completed_count=0,
                failed_count=0,
                average_processing_time=0.0,
                throughput_per_second=0.0,
                consumer_count=0,
                last_updated=datetime.now()
            )
            
            # Persist configuration to Redis
            await self._save_queue_config_to_redis(config)
            
            # Update service metrics
            self.service_metrics['queue_count'] += 1
            
            logger.info(f"Created queue: {config.name} (type: {config.queue_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create queue {config.name}: {e}")
            return False
    
    async def publish_message(self, queue_name: str, payload: Dict[str, Any],
                            priority: MessagePriority = MessagePriority.NORMAL,
                            delay_seconds: int = 0,
                            headers: Optional[Dict[str, str]] = None,
                            correlation_id: str = "",
                            reply_to: str = "") -> str:
        """Publish a message to the specified queue"""
        try:
            start_time = time.time()
            
            # Validate queue exists
            if queue_name not in self.queues:
                raise ValueError(f"Queue {queue_name} does not exist")
            
            queue_config = self.queues[queue_name]
            
            # Check rate limiting
            if queue_config.rate_limit and not await self._check_rate_limit(queue_name, queue_config.rate_limit):
                raise ValueError(f"Rate limit exceeded for queue {queue_name}")
            
            # Check queue capacity
            current_size = await self._get_queue_size(queue_name)
            if current_size >= queue_config.max_size:
                raise ValueError(f"Queue {queue_name} is full")
            
            # Create message
            message_id = str(uuid.uuid4())
            scheduled_at = datetime.now() + timedelta(seconds=delay_seconds) if delay_seconds > 0 else None
            expires_at = datetime.now() + timedelta(seconds=queue_config.message_ttl)
            
            message = Message(
                id=message_id,
                queue_name=queue_name,
                payload=payload,
                priority=priority,
                created_at=datetime.now(),
                scheduled_at=scheduled_at,
                expires_at=expires_at,
                max_retries=queue_config.max_retries,
                headers=headers or {},
                correlation_id=correlation_id,
                reply_to=reply_to
            )
            
            # Store message
            self.message_store[message_id] = message
            
            # Add to appropriate queue structure
            if delay_seconds > 0:
                # Add to delayed messages heap
                heapq.heappush(self.delayed_messages, (scheduled_at, message_id))
            else:
                await self._enqueue_message(message)
            
            # Persist to Redis if configured
            if queue_config.persistent:
                await self._save_message_to_redis(message)
            
            # Update metrics
            self.service_metrics['messages_published'] += 1
            self.queue_metrics[queue_name].message_count += 1
            self.queue_metrics[queue_name].pending_count += 1
            
            # Trigger AI optimization
            asyncio.create_task(self._optimize_queue_priority(queue_name))
            
            processing_time = time.time() - start_time
            self.service_metrics['average_latency'] = (
                self.service_metrics['average_latency'] * 0.9 + processing_time * 0.1
            )
            
            logger.debug(f"Published message {message_id} to queue {queue_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message to queue {queue_name}: {e}")
            raise
    
    async def _enqueue_message(self, message -> None: Message) -> None:
        """Add message to the appropriate queue structure"""
        try:
            queue_config = self.queues[message.queue_name]
            
            if queue_config.queue_type == QueueType.PRIORITY:
                # Use priority queue (min-heap, so negate priority for max-heap behavior)
                priority_score = -message.priority.value
                heapq.heappush(self.priority_queues[message.queue_name], (priority_score, time.time(), message.id))
                
            elif queue_config.queue_type == QueueType.FIFO:
                # Use Redis list for FIFO
                if self.redis_client:
                    await self.redis_client.lpush(f"queue:{message.queue_name}:fifo", message.id)
                    
            elif queue_config.queue_type == QueueType.TOPIC:
                # Route based on routing key
                await self._route_topic_message(message)
                
            elif queue_config.queue_type == QueueType.FANOUT:
                # Broadcast to all bound consumers
                await self._fanout_message(message)
                
            else:
                # Default to FIFO
                if self.redis_client:
                    await self.redis_client.lpush(f"queue:{message.queue_name}:default", message.id)
            
        except Exception as e:
            logger.error(f"Failed to enqueue message {message.id}: {e}")
            raise
    
    async def register_consumer(self, config: ConsumerConfig) -> bool:
        """Register a message consumer"""
        try:
            # Validate configuration
            if config.id in self.consumers:
                raise ValueError(f"Consumer {config.id} already exists")
            
            # Validate queues exist
            for queue_name in config.queue_names:
                if queue_name not in self.queues:
                    raise ValueError(f"Queue {queue_name} does not exist")
            
            # Store consumer configuration
            self.consumers[config.id] = config
            
            # Start consumer task
            consumer_task = asyncio.create_task(self._run_consumer(config))
            self.active_consumers[config.id] = consumer_task
            
            # Update metrics
            self.service_metrics['consumer_count'] += 1
            for queue_name in config.queue_names:
                self.queue_metrics[queue_name].consumer_count += 1
            
            logger.info(f"Registered consumer: {config.id} for queues: {config.queue_names}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register consumer {config.id}: {e}")
            return False
    
    async def _run_consumer(self, config -> None: ConsumerConfig) -> None:
        """Run consumer to process messages from assigned queues"""
        try:
            logger.info(f"Starting consumer {config.id}")
            
            while True:
                try:
                    # Process messages from each assigned queue
                    for queue_name in config.queue_names:
                        await self._process_queue_messages(config, queue_name)
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.1)
                    
                except asyncio.CancelledError:
                    logger.info(f"Consumer {config.id} cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in consumer {config.id}: {e}")
                    await asyncio.sleep(1)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"Fatal error in consumer {config.id}: {e}")
        finally:
            logger.info(f"Consumer {config.id} stopped")
    
    async def _process_queue_messages(self, config -> None: ConsumerConfig, queue_name -> None: str) -> None:
        """Process messages from a specific queue"""
        try:
            queue_config = self.queues[queue_name]
            messages_processed = 0
            
            async with self.queue_locks[queue_name]:
                # Get messages up to prefetch count
                while messages_processed < config.prefetch_count:
                    message_id = await self._dequeue_message(queue_name)
                    if not message_id:
                        break
                    
                    if message_id not in self.message_store:
                        logger.warning(f"Message {message_id} not found in store")
                        continue
                    
                    message = self.message_store[message_id]
                    
                    # Check if message has expired
                    if message.expires_at and datetime.now() > message.expires_at:
                        await self._handle_expired_message(message)
                        continue
                    
                    # Process message
                    await self._process_single_message(config, message)
                    messages_processed += 1
                    
        except Exception as e:
            logger.error(f"Failed to process messages from queue {queue_name}: {e}")
    
    async def _dequeue_message(self, queue_name: str) -> Optional[str]:
        """Dequeue the next message from the specified queue"""
        try:
            queue_config = self.queues[queue_name]
            
            if queue_config.queue_type == QueueType.PRIORITY:
                # Get from priority queue
                if self.priority_queues[queue_name]:
                    _, _, message_id = heapq.heappop(self.priority_queues[queue_name])
                    return message_id
                    
            elif queue_config.queue_type == QueueType.FIFO:
                # Get from Redis list
                if self.redis_client:
                    result = await self.redis_client.rpop(f"queue:{queue_name}:fifo")
                    return result.decode() if result else None
                    
            else:
                # Default dequeue
                if self.redis_client:
                    result = await self.redis_client.rpop(f"queue:{queue_name}:default")
                    return result.decode() if result else None
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue message from {queue_name}: {e}")
            return None
    
    async def _process_single_message(self, config -> None: ConsumerConfig, message -> None: Message) -> None:
        """Process a single message with the consumer handler"""
        try:
            start_time = time.time()
            
            # Update message status
            message.status = MessageStatus.PROCESSING
            self.queue_metrics[message.queue_name].processing_count += 1
            self.queue_metrics[message.queue_name].pending_count -= 1
            
            try:
                # Call consumer handler
                if asyncio.iscoroutinefunction(config.handler):
                    result = await config.handler(message)
                else:
                    result = await asyncio.get_event_loop().run_in_executor(
                        self.executor, config.handler, message
                    )
                
                # Handle successful processing
                await self._handle_message_success(message, result)
                
                # Update metrics
                processing_time = time.time() - start_time
                metrics = self.queue_metrics[message.queue_name]
                metrics.processing_count -= 1
                metrics.completed_count += 1
                metrics.average_processing_time = (
                    metrics.average_processing_time * 0.9 + processing_time * 0.1
                )
                
                self.service_metrics['messages_consumed'] += 1
                
            except Exception as handler_error:
                # Handle processing failure
                await self._handle_message_failure(message, handler_error)
                
        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {e}")
            await self._handle_message_failure(message, e)
    
    async def _handle_message_success(self, message -> None: Message, result -> None: Any) -> None:
        """Handle successful message processing"""
        try:
            message.status = MessageStatus.COMPLETED
            
            # Send reply if reply_to is specified
            if message.reply_to and result is not None:
                reply_payload = {
                    "correlation_id": message.correlation_id,
                    "result": result,
                    "original_message_id": message.id
                }
                await self.publish_message(message.reply_to, reply_payload)
            
            # Clean up message if not persistent
            queue_config = self.queues[message.queue_name]
            if not queue_config.persistent:
                del self.message_store[message.id]
            
            logger.debug(f"Message {message.id} processed successfully")
            
        except Exception as e:
            logger.error(f"Failed to handle message success for {message.id}: {e}")
    
    async def _handle_message_failure(self, message -> None: Message, error -> None: Exception) -> None:
        """Handle message processing failure with retry logic"""
        try:
            message.retry_count += 1
            queue_config = self.queues[message.queue_name]
            
            # Update metrics
            self.queue_metrics[message.queue_name].processing_count -= 1
            self.queue_metrics[message.queue_name].failed_count += 1
            self.service_metrics['messages_failed'] += 1
            
            if message.retry_count <= message.max_retries:
                # Retry the message
                message.status = MessageStatus.RETRYING
                
                # Add delay before retry
                retry_delay = queue_config.retry_delay * (2 ** (message.retry_count - 1))  # Exponential backoff
                retry_time = datetime.now() + timedelta(seconds=retry_delay)
                
                # Add to delayed messages for retry
                heapq.heappush(self.delayed_messages, (retry_time, message.id))
                
                logger.warning(f"Retrying message {message.id} (attempt {message.retry_count})")
                
            else:
                # Send to dead letter queue
                await self._send_to_dead_letter_queue(message, error)
                
        except Exception as e:
            logger.error(f"Failed to handle message failure for {message.id}: {e}")
    
    async def _send_to_dead_letter_queue(self, message -> None: Message, error -> None: Exception) -> None:
        """Send failed message to dead letter queue"""
        try:
            message.status = MessageStatus.DEAD_LETTER
            queue_config = self.queues[message.queue_name]
            
            if queue_config.dead_letter_queue:
                # Create dead letter message with error info
                dlq_payload = {
                    "original_message": asdict(message),
                    "error": str(error),
                    "failed_at": datetime.now().isoformat(),
                    "retry_count": message.retry_count
                }
                
                await self.publish_message(
                    queue_config.dead_letter_queue,
                    dlq_payload,
                    priority=MessagePriority.LOW
                )
            else:
                # Add to internal dead letter queue
                self.dead_letter_queues[message.queue_name].append({
                    "message": message,
                    "error": str(error),
                    "failed_at": datetime.now()
                })
            
            logger.error(f"Message {message.id} sent to dead letter queue: {error}")
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id} to dead letter queue: {e}")
    
    async def _process_delayed_messages(self) -> None:
        """Background task to process delayed messages"""
        while True:
            try:
                await asyncio.sleep(1)  # Check every second
                
                current_time = datetime.now()
                
                # Process all ready delayed messages
                while (self.delayed_messages and 
                       self.delayed_messages[0][0] <= current_time):
                    
                    _, message_id = heapq.heappop(self.delayed_messages)
                    
                    if message_id in self.message_store:
                        message = self.message_store[message_id]
                        
                        # Check if message is still valid
                        if message.expires_at and current_time > message.expires_at:
                            await self._handle_expired_message(message)
                        else:
                            # Enqueue the message
                            message.status = MessageStatus.PENDING
                            await self._enqueue_message(message)
                
            except Exception as e:
                logger.error(f"Error processing delayed messages: {e}")
                await asyncio.sleep(5)
    
    async def _handle_expired_message(self, message -> None: Message) -> None:
        """Handle expired message"""
        try:
            message.status = MessageStatus.FAILED
            logger.warning(f"Message {message.id} expired")
            
            # Update metrics
            self.queue_metrics[message.queue_name].failed_count += 1
            
            # Remove from store
            if message.id in self.message_store:
                del self.message_store[message.id]
                
        except Exception as e:
            logger.error(f"Failed to handle expired message {message.id}: {e}")
    
    async def _check_rate_limit(self, queue_name: str, limit: int) -> bool:
        """Check if message can be published based on rate limit"""
        try:
            current_time = time.time()
            rate_limiter = self.rate_limiters[queue_name]
            
            # Remove old entries (older than 1 second)
            while rate_limiter and rate_limiter[0] < current_time - 1.0:
                rate_limiter.popleft()
            
            # Check if under limit
            if len(rate_limiter) >= limit:
                return False
            
            # Add current timestamp
            rate_limiter.append(current_time)
            return True
            
        except Exception as e:
            logger.error(f"Failed to check rate limit for queue {queue_name}: {e}")
            return True  # Allow on error
    
    async def _get_queue_size(self, queue_name: str) -> int:
        """Get current size of a queue"""
        try:
            queue_config = self.queues[queue_name]
            
            if queue_config.queue_type == QueueType.PRIORITY:
                return len(self.priority_queues[queue_name])
            elif self.redis_client:
                if queue_config.queue_type == QueueType.FIFO:
                    return await self.redis_client.llen(f"queue:{queue_name}:fifo")
                else:
                    return await self.redis_client.llen(f"queue:{queue_name}:default")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to get queue size for {queue_name}: {e}")
            return 0
    
    async def get_queue_metrics(self, queue_name: Optional[str] = None) -> Dict[str, Any]:
        """Get queue performance metrics"""
        try:
            if queue_name:
                # Metrics for specific queue
                if queue_name not in self.queue_metrics:
                    return {"error": f"Queue {queue_name} not found"}
                
                metrics = self.queue_metrics[queue_name]
                
                # Calculate additional metrics
                current_size = await self._get_queue_size(queue_name)
                
                return {
                    "queue_name": queue_name,
                    "current_size": current_size,
                    "message_count": metrics.message_count,
                    "pending_count": metrics.pending_count,
                    "processing_count": metrics.processing_count,
                    "completed_count": metrics.completed_count,
                    "failed_count": metrics.failed_count,
                    "average_processing_time": metrics.average_processing_time,
                    "throughput_per_second": metrics.throughput_per_second,
                    "consumer_count": metrics.consumer_count,
                    "success_rate": (metrics.completed_count / max(metrics.message_count, 1)) * 100,
                    "last_updated": metrics.last_updated.isoformat()
                }
            else:
                # Overall metrics
                total_messages = sum(m.message_count for m in self.queue_metrics.values())
                total_completed = sum(m.completed_count for m in self.queue_metrics.values())
                total_failed = sum(m.failed_count for m in self.queue_metrics.values())
                
                return {
                    "service_metrics": self.service_metrics,
                    "total_queues": len(self.queues),
                    "total_consumers": len(self.consumers),
                    "total_messages": total_messages,
                    "overall_success_rate": (total_completed / max(total_messages, 1)) * 100,
                    "queue_summaries": [
                        {
                            "name": name,
                            "size": await self._get_queue_size(name),
                            "pending": metrics.pending_count,
                            "consumers": metrics.consumer_count
                        }
                        for name, metrics in self.queue_metrics.items()
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get queue metrics: {e}")
            return {"error": str(e)}
    
    async def purge_queue(self, queue_name: str) -> bool:
        """Purge all messages from a queue"""
        try:
            if queue_name not in self.queues:
                raise ValueError(f"Queue {queue_name} does not exist")
            
            queue_config = self.queues[queue_name]
            
            # Clear queue structures
            if queue_config.queue_type == QueueType.PRIORITY:
                self.priority_queues[queue_name].clear()
            elif self.redis_client:
                if queue_config.queue_type == QueueType.FIFO:
                    await self.redis_client.delete(f"queue:{queue_name}:fifo")
                else:
                    await self.redis_client.delete(f"queue:{queue_name}:default")
            
            # Remove messages from store
            messages_to_remove = [
                msg_id for msg_id, msg in self.message_store.items()
                if msg.queue_name == queue_name and msg.status == MessageStatus.PENDING
            ]
            
            for msg_id in messages_to_remove:
                del self.message_store[msg_id]
            
            # Reset metrics
            metrics = self.queue_metrics[queue_name]
            metrics.pending_count = 0
            metrics.message_count = 0
            
            logger.info(f"Purged queue {queue_name}: removed {len(messages_to_remove)} messages")
            return True
            
        except Exception as e:
            logger.error(f"Failed to purge queue {queue_name}: {e}")
            return False
    
    async def delete_queue(self, queue_name: str, force: bool = False) -> bool:
        """Delete a queue and all its messages"""
        try:
            if queue_name not in self.queues:
                raise ValueError(f"Queue {queue_name} does not exist")
            
            # Check if queue has active consumers
            active_consumers = [
                consumer_id for consumer_id, config in self.consumers.items()
                if queue_name in config.queue_names
            ]
            
            if active_consumers and not force:
                raise ValueError(f"Queue {queue_name} has active consumers: {active_consumers}")
            
            # Stop consumers using this queue
            for consumer_id in active_consumers:
                await self.unregister_consumer(consumer_id)
            
            # Purge messages
            await self.purge_queue(queue_name)
            
            # Remove queue configuration
            del self.queues[queue_name]
            del self.queue_metrics[queue_name]
            
            # Clean up Redis data
            if self.redis_client:
                await self.redis_client.delete(f"queue_config:{queue_name}")
                await self.redis_client.delete(f"queue:{queue_name}:fifo")
                await self.redis_client.delete(f"queue:{queue_name}:default")
            
            # Update service metrics
            self.service_metrics['queue_count'] -= 1
            
            logger.info(f"Deleted queue: {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete queue {queue_name}: {e}")
            return False
    
    async def unregister_consumer(self, consumer_id: str) -> bool:
        """Unregister a message consumer"""
        try:
            if consumer_id not in self.consumers:
                raise ValueError(f"Consumer {consumer_id} does not exist")
            
            # Stop consumer task
            if consumer_id in self.active_consumers:
                task = self.active_consumers[consumer_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.active_consumers[consumer_id]
            
            # Update metrics
            config = self.consumers[consumer_id]
            for queue_name in config.queue_names:
                if queue_name in self.queue_metrics:
                    self.queue_metrics[queue_name].consumer_count -= 1
            
            # Remove consumer configuration
            del self.consumers[consumer_id]
            self.service_metrics['consumer_count'] -= 1
            
            logger.info(f"Unregistered consumer: {consumer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister consumer {consumer_id}: {e}")
            return False
    
    async def _route_topic_message(self, message -> None: Message) -> None:
        """Route message based on topic routing patterns"""
        try:
            # Placeholder for topic routing logic
            # In production, this would implement pattern matching for routing keys
            routing_key = message.routing_key or message.headers.get("routing_key", "")
            
            # For now, just add to default queue
            if self.redis_client:
                await self.redis_client.lpush(f"queue:{message.queue_name}:topic", message.id)
                
        except Exception as e:
            logger.error(f"Failed to route topic message {message.id}: {e}")
    
    async def _fanout_message(self, message -> None: Message) -> None:
        """Broadcast message to all bound consumers"""
        try:
            # Placeholder for fanout logic
            # In production, this would broadcast to all bound consumers
            
            # For now, just add to default queue
            if self.redis_client:
                await self.redis_client.lpush(f"queue:{message.queue_name}:fanout", message.id)
                
        except Exception as e:
            logger.error(f"Failed to fanout message {message.id}: {e}")
    
    async def _optimize_queue_priority(self, queue_name -> None: str) -> None:
        """AI-powered queue priority optimization"""
        try:
            # Placeholder for AI optimization
            # In production, this would use ML models to optimize message priority
            # based on historical processing patterns and business rules
            
            queue_config = self.queues[queue_name]
            if queue_config.queue_type == QueueType.PRIORITY:
                # Analyze current queue state and optimize priority assignments
                pass
                
        except Exception as e:
            logger.error(f"Failed to optimize queue priority for {queue_name}: {e}")
    
    async def _monitor_queue_health(self) -> None:
        """Background task to monitor queue health and performance"""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                for queue_name, metrics in self.queue_metrics.items():
                    # Check for potential issues
                    current_size = await self._get_queue_size(queue_name)
                    
                    # Alert on queue growing too large
                    if current_size > self.queues[queue_name].max_size * 0.8:
                        logger.warning(f"Queue {queue_name} is {(current_size / self.queues[queue_name].max_size) * 100:.1f}% full")
                    
                    # Alert on high failure rate
                    if metrics.message_count > 100:  # Only check if we have enough data
                        failure_rate = (metrics.failed_count / metrics.message_count) * 100
                        if failure_rate > 10:  # 10% failure rate threshold
                            logger.warning(f"Queue {queue_name} has high failure rate: {failure_rate:.1f}%")
                    
                    # Alert on slow processing
                    if metrics.average_processing_time > 30:  # 30 seconds threshold
                        logger.warning(f"Queue {queue_name} has slow processing: {metrics.average_processing_time:.1f}s average")
                
            except Exception as e:
                logger.error(f"Error monitoring queue health: {e}")
                await asyncio.sleep(60)
    
    async def _update_metrics(self) -> None:
        """Background task to update queue metrics"""
        while True:
            try:
                await asyncio.sleep(10)  # Update every 10 seconds
                
                for queue_name, metrics in self.queue_metrics.items():
                    # Update throughput calculation
                    current_time = datetime.now()
                    time_diff = (current_time - metrics.last_updated).total_seconds()
                    
                    if time_diff >= 10:  # Update every 10 seconds
                        # Calculate throughput (messages per second)
                        completed_in_period = metrics.completed_count  # This would need to track period-specific completions
                        metrics.throughput_per_second = completed_in_period / time_diff if time_diff > 0 else 0
                        metrics.last_updated = current_time
                
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_expired_messages(self) -> None:
        """Background task to clean up expired messages"""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                
                current_time = datetime.now()
                expired_messages = []
                
                # Find expired messages
                for message_id, message in self.message_store.items():
                    if (message.expires_at and current_time > message.expires_at and
                        message.status in [MessageStatus.PENDING, MessageStatus.PROCESSING]):
                        expired_messages.append(message_id)
                
                # Remove expired messages
                for message_id in expired_messages:
                    if message_id in self.message_store:
                        message = self.message_store[message_id]
                        await self._handle_expired_message(message)
                
                if expired_messages:
                    logger.info(f"Cleaned up {len(expired_messages)} expired messages")
                
            except Exception as e:
                logger.error(f"Error cleaning up expired messages: {e}")
                await asyncio.sleep(120)
    
    async def _save_queue_config_to_redis(self, config -> None: QueueConfig) -> None:
        """Save queue configuration to Redis"""
        try:
            if self.redis_client:
                config_data = {
                    'name': config.name,
                    'queue_type': config.queue_type.value,
                    'max_size': config.max_size,
                    'max_retries': config.max_retries,
                    'retry_delay': config.retry_delay,
                    'message_ttl': config.message_ttl,
                    'dead_letter_queue': config.dead_letter_queue or '',
                    'auto_acknowledge': config.auto_acknowledge,
                    'persistent': config.persistent,
                    'priority_levels': config.priority_levels,
                    'rate_limit': config.rate_limit or 0
                }
                await self.redis_client.hset(f"queue_config:{config.name}", mapping=config_data)
                
        except Exception as e:
            logger.error(f"Failed to save queue config to Redis: {e}")
    
    async def _save_message_to_redis(self, message -> None: Message) -> None:
        """Save message to Redis for persistence"""
        try:
            if self.redis_client:
                message_data = {
                    'id': message.id,
                    'queue_name': message.queue_name,
                    'payload': json.dumps(message.payload),
                    'priority': message.priority.value,
                    'created_at': message.created_at.isoformat(),
                    'scheduled_at': message.scheduled_at.isoformat() if message.scheduled_at else '',
                    'expires_at': message.expires_at.isoformat() if message.expires_at else '',
                    'retry_count': message.retry_count,
                    'max_retries': message.max_retries,
                    'status': message.status.value,
                    'headers': json.dumps(message.headers),
                    'routing_key': message.routing_key,
                    'correlation_id': message.correlation_id,
                    'reply_to': message.reply_to,
                    'content_type': message.content_type,
                    'delivery_mode': message.delivery_mode.value
                }
                
                await self.redis_client.hset(f"message:{message.id}", mapping=message_data)
                
                # Set TTL
                ttl = int((message.expires_at - datetime.now()).total_seconds()) if message.expires_at else 3600
                await self.redis_client.expire(f"message:{message.id}", ttl)
                
        except Exception as e:
            logger.error(f"Failed to save message to Redis: {e}")
    
    async def _load_queue_configurations(self) -> None:
        """Load existing queue configurations from Redis"""
        try:
            if self.redis_client:
                # Load queue configurations
                config_keys = await self.redis_client.keys("queue_config:*")
                for key in config_keys:
                    config_data = await self.redis_client.hgetall(key)
                    if config_data:
                        # Reconstruct queue config
                        # Implementation details would depend on Redis data format
                        pass
                        
        except Exception as e:
            logger.error(f"Failed to load queue configurations: {e}")
    
    async def _initialize_ai_models(self) -> None:
        """Initialize AI models for queue optimization"""
        try:
            # Placeholder for AI model initialization
            # In production, this would load actual ML models for:
            # - Message priority optimization
            # - Routing optimization
            # - Capacity planning
            
            self.priority_optimizer = "priority_optimization_model"
            self.routing_optimizer = "routing_optimization_model"
            
            logger.info("AI models initialized for message queue optimization")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    async def shutdown(self) -> None:
        """Graceful shutdown of message queue service"""
        try:
            # Stop all consumers
            for consumer_id in list(self.consumers.keys()):
                await self.unregister_consumer(consumer_id)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info("Message Queue Service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Example usage and testing
async def main() -> None:
    """Example usage of Message Queue Service"""
    service = MessageQueueService()
    await service.initialize()
    
    try:
        # Create queues
        high_priority_queue = QueueConfig(
            name="high_priority_tasks",
            queue_type=QueueType.PRIORITY,
            max_size=1000,
            max_retries=3,
            retry_delay=5,
            message_ttl=3600
        )
        
        notification_queue = QueueConfig(
            name="notifications",
            queue_type=QueueType.FIFO,
            max_size=5000,
            max_retries=2,
            retry_delay=10,
            message_ttl=7200
        )
        
        await service.create_queue(high_priority_queue)
        await service.create_queue(notification_queue)
        print("Created queues")
        
        # Define message handlers
        async def process_high_priority_task(message -> None: Message) -> None:
            print(f"Processing high priority task: {message.payload}")
            await asyncio.sleep(0.1)  # Simulate processing
            return {"status": "completed", "processed_at": datetime.now().isoformat()}
        
        async def process_notification(message -> None: Message) -> None:
            print(f"Sending notification: {message.payload}")
            await asyncio.sleep(0.05)  # Simulate sending
            return {"status": "sent"}
        
        # Register consumers
        high_priority_consumer = ConsumerConfig(
            id="high_priority_worker",
            queue_names=["high_priority_tasks"],
            handler=process_high_priority_task,
            prefetch_count=5
        )
        
        notification_consumer = ConsumerConfig(
            id="notification_worker",
            queue_names=["notifications"],
            handler=process_notification,
            prefetch_count=10
        )
        
        await service.register_consumer(high_priority_consumer)
        await service.register_consumer(notification_consumer)
        print("Registered consumers")
        
        # Publish messages
        for i in range(10):
            # High priority tasks
            await service.publish_message(
                "high_priority_tasks",
                {"task_id": f"task_{i}", "data": f"important_data_{i}"},
                priority=MessagePriority.HIGH if i % 2 == 0 else MessagePriority.NORMAL
            )
            
            # Notifications
            await service.publish_message(
                "notifications",
                {"user_id": f"user_{i}", "message": f"Hello user {i}!"},
                priority=MessagePriority.NORMAL
            )
        
        print("Published messages")
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get metrics
        metrics = await service.get_queue_metrics()
        print(f"Service metrics: {metrics}")
        
        # Get specific queue metrics
        high_priority_metrics = await service.get_queue_metrics("high_priority_tasks")
        print(f"High priority queue metrics: {high_priority_metrics}")
        
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())