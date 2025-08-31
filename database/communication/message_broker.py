"""
Message Broker Database Management

Enterprise message broker system for real-time communication, asynchronous task processing,
and cross-platform message routing for multi-format creator collaboration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import uuid
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import logging
from contextlib import asynccontextmanager

Base = declarative_base()
logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class MessageStatus(Enum):
    """Message processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRY = "retry"
    EXPIRED = "expired"


class QueueType(Enum):
    """Message queue types"""
    REAL_TIME = "real_time"
    BACKGROUND = "background"
    DELAYED = "delayed"
    PRIORITY = "priority"
    DEAD_LETTER = "dead_letter"
    BROADCAST = "broadcast"


@dataclass
class MessageHeader:
    """Message header information"""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]
    channel: str
    priority: MessagePriority
    timestamp: datetime
    ttl: Optional[int]
    retry_count: int
    correlation_id: Optional[str]
    reply_to: Optional[str]


@dataclass
class MessagePayload:
    """Message payload structure"""
    content_type: str
    data: Dict[str, Any]
    attachments: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    encryption_key: Optional[str]
    compression: Optional[str]


class MessageQueue(Base):
    """Message queue persistence model"""
    __tablename__ = "message_queues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_name = Column(String(255), nullable=False, index=True)
    queue_type = Column(String(50), nullable=False)
    priority_level = Column(Integer, default=0)
    max_size = Column(Integer, default=10000)
    ttl_seconds = Column(Integer, default=3600)
    dlq_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    config = Column(JSON)
    stats = Column(JSON)

    __table_args__ = (
        Index('idx_queue_name_type', 'queue_name', 'queue_type'),
    )


class QueuedMessage(Base):
    """Queued message persistence model"""
    __tablename__ = "queued_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(255), nullable=False, unique=True, index=True)
    queue_name = Column(String(255), nullable=False, index=True)
    sender_id = Column(String(255), nullable=False, index=True)
    recipient_id = Column(String(255), index=True)
    channel = Column(String(255), nullable=False)
    priority = Column(String(50), nullable=False)
    status = Column(String(50), default=MessageStatus.QUEUED.value)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Message content
    content_type = Column(String(100))
    payload = Column(JSON)
    headers = Column(JSON)
    attachments = Column(JSON)
    
    # Timing
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    scheduled_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Processing
    worker_id = Column(String(255))
    error_message = Column(Text)
    correlation_id = Column(String(255), index=True)
    reply_to = Column(String(255))
    
    # Metrics
    processing_time_ms = Column(Integer)
    size_bytes = Column(Integer)

    __table_args__ = (
        Index('idx_message_status_priority', 'status', 'priority'),
        Index('idx_message_scheduled', 'scheduled_at'),
        Index('idx_message_expires', 'expires_at'),
    )


class MessageBrokerMetrics(Base):
    """Message broker metrics and statistics"""
    __tablename__ = "message_broker_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    queue_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False)
    metric_value = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    labels = Column(JSON)
    
    __table_args__ = (
        Index('idx_metrics_queue_type_time', 'queue_name', 'metric_type', 'timestamp'),
    )


class MessageBroker:
    """Enterprise message broker with Redis and PostgreSQL persistence"""
    
    def __init__(self, redis_client: redis.Redis, db_session: Session):
        self.redis = redis_client
        self.db = db_session
        self.queues: Dict[str, Dict[str, Any]] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
        
    async def initialize(self):
        """Initialize message broker"""



        try:
            # Load queue configurations from database
            await self._load_queue_configs()
            
            # Start background workers
            await self._start_workers()
            
            self.running = True
            logger.info("Message broker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize message broker: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Stop workers
        for task in self.worker_tasks:
            task.cancel()
        
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        logger.info("Message broker shutdown completed")
    
    async def create_queue(
        self,
        queue_name: str,
        queue_type: QueueType = QueueType.REAL_TIME,
        max_size: int = 10000,
        ttl_seconds: int = 3600,
        dlq_enabled: bool = True,
        config: Optional[Dict[str, Any]] = None
    ) -> MessageQueue:
        """Create new message queue"""



        try:
            # Check if queue exists
            existing = self.db.query(MessageQueue).filter(
                MessageQueue.queue_name == queue_name
            ).first()
            
            if existing:
                logger.info(f"Queue {queue_name} already exists")
                return existing
            
            # Create queue
            queue = MessageQueue(
                queue_name=queue_name,
                queue_type=queue_type.value,
                max_size=max_size,
                ttl_seconds=ttl_seconds,
                dlq_enabled=dlq_enabled,
                config=config or {},
                stats={
                    "total_messages": 0,
                    "processed_messages": 0,
                    "failed_messages": 0,
                    "average_processing_time": 0
                }
            )
            
            self.db.add(queue)
            self.db.commit()
            
            # Initialize Redis structures
            await self._initialize_queue_redis(queue_name, queue_type)
            
            self.queues[queue_name] = {
                "type": queue_type,
                "config": config or {},
                "stats": queue.stats
            }
            
            logger.info(f"Created queue: {queue_name}")
            return queue
            
        except Exception as e:
            logger.error(f"Failed to create queue {queue_name}: {e}")
            self.db.rollback()
            raise
    
    async def publish_message(
        self,
        queue_name: str,
        payload: MessagePayload,
        header: MessageHeader,
        delay_seconds: Optional[int] = None
    ) -> str:
        """Publish message to queue"""



        try:
            # Validate queue exists
            if queue_name not in self.queues:
                raise ValueError(f"Queue {queue_name} does not exist")
            
            # Create message record
            message = QueuedMessage(
                message_id=header.message_id,
                queue_name=queue_name,
                sender_id=header.sender_id,
                recipient_id=header.recipient_id,
                channel=header.channel,
                priority=header.priority.value,
                content_type=payload.content_type,
                payload=payload.data,
                headers=asdict(header),
                attachments=payload.attachments,
                scheduled_at=datetime.now(timezone.utc) + timedelta(seconds=delay_seconds or 0),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=header.ttl) if header.ttl else None,
                correlation_id=header.correlation_id,
                reply_to=header.reply_to,
                size_bytes=len(json.dumps(payload.data))
            )
            
            self.db.add(message)
            self.db.commit()
            
            # Add to Redis queue
            if delay_seconds:
                await self._schedule_message(queue_name, header.message_id, delay_seconds)
            else:
                await self._enqueue_message(queue_name, header.message_id, header.priority)
            
            # Update metrics
            await self._update_queue_metrics(queue_name, "messages_published", 1)
            
            logger.debug(f"Published message {header.message_id} to {queue_name}")
            return header.message_id
            
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            self.db.rollback()
            raise
    
    async def consume_message(
        self,
        queue_name: str,
        timeout: Optional[int] = None
    ) -> Optional[QueuedMessage]:
        """Consume message from queue"""



        try:
            # Get message from Redis
            message_id = await self._dequeue_message(queue_name, timeout)
            if not message_id:
                return None
            
            # Get full message from database
            message = self.db.query(QueuedMessage).filter(
                QueuedMessage.message_id == message_id,
                QueuedMessage.status == MessageStatus.QUEUED.value
            ).first()
            
            if not message:
                logger.warning(f"Message {message_id} not found in database")
                return None
            
            # Mark as processing
            message.status = MessageStatus.PROCESSING.value
            message.processed_at = datetime.now(timezone.utc)
            self.db.commit()
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to consume message from {queue_name}: {e}")
            return None
    
    async def acknowledge_message(self, message_id: str, success: bool = True):
        """Acknowledge message processing"""



        try:
            message = self.db.query(QueuedMessage).filter(
                QueuedMessage.message_id == message_id
            ).first()
            
            if not message:
                logger.warning(f"Message {message_id} not found for acknowledgment")
                return
            
            if success:
                message.status = MessageStatus.DELIVERED.value
                await self._update_queue_metrics(message.queue_name, "messages_processed", 1)
            else:
                await self._handle_failed_message(message)
            
            # Calculate processing time
            if message.processed_at:
                processing_time = (datetime.now(timezone.utc) - message.processed_at).total_seconds() * 1000
                message.processing_time_ms = int(processing_time)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
            self.db.rollback()
    
    async def subscribe(self, channel: str, callback: Callable):
        """Subscribe to message channel"""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(callback)
        
        # Subscribe to Redis pub/sub
        await self.redis.subscribe(f"channel:{channel}")
        logger.info(f"Subscribed to channel: {channel}")
    
    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to channel subscribers"""



        try:
            # Publish to Redis
            await self.redis.publish(f"channel:{channel}", json.dumps(message))
            
            # Call local subscribers
            if channel in self.subscribers:
                for callback in self.subscribers[channel]:
                    try:
                        await callback(message)
                    except Exception as e:
                        logger.error(f"Subscriber callback failed: {e}")
            
            await self._update_queue_metrics(f"broadcast:{channel}", "messages_broadcast", 1)
            
        except Exception as e:
            logger.error(f"Failed to broadcast to {channel}: {e}")
    
    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get queue statistics"""



        try:
            # Get from database
            queue = self.db.query(MessageQueue).filter(
                MessageQueue.queue_name == queue_name
            ).first()
            
            if not queue:
                return {}
            
            # Get current counts from Redis
            pending_count = await self.redis.llen(f"queue:{queue_name}")
            processing_count = await self.redis.scard(f"processing:{queue_name}")
            
            # Get recent metrics
            recent_metrics = self.db.query(MessageBrokerMetrics).filter(
                MessageBrokerMetrics.queue_name == queue_name,
                MessageBrokerMetrics.timestamp >= datetime.now(timezone.utc) - timedelta(hours=1)
            ).all()
            
            return {
                "queue_name": queue_name,
                "queue_type": queue.queue_type,
                "pending_messages": pending_count,
                "processing_messages": processing_count,
                "total_processed": queue.stats.get("processed_messages", 0),
                "total_failed": queue.stats.get("failed_messages", 0),
                "average_processing_time": queue.stats.get("average_processing_time", 0),
                "recent_metrics": [
                    {
                        "type": m.metric_type,
                        "value": m.metric_value,
                        "timestamp": m.timestamp.isoformat()
                    } for m in recent_metrics
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    # Private methods
    
    async def _load_queue_configs(self):
        """Load queue configurations from database"""
        queues = self.db.query(MessageQueue).all()
        for queue in queues:
            self.queues[queue.queue_name] = {
                "type": QueueType(queue.queue_type),
                "config": queue.config,
                "stats": queue.stats
            }
    
    async def _start_workers(self):
        """Start background worker tasks"""
        # Message processor worker
        self.worker_tasks.append(
            asyncio.create_task(self._message_processor_worker())
        )
        
        # Delayed message scheduler
        self.worker_tasks.append(
            asyncio.create_task(self._delayed_scheduler_worker())
        )
        
        # Dead letter queue processor
        self.worker_tasks.append(
            asyncio.create_task(self._dlq_processor_worker())
        )
        
        # Metrics collector
        self.worker_tasks.append(
            asyncio.create_task(self._metrics_collector_worker())
        )
    
    async def _initialize_queue_redis(self, queue_name: str, queue_type: QueueType):
        """Initialize Redis structures for queue"""
        # Initialize queue lists
        await self.redis.delete(f"queue:{queue_name}")
        await self.redis.delete(f"priority:{queue_name}")
        await self.redis.delete(f"processing:{queue_name}")
        await self.redis.delete(f"delayed:{queue_name}")
    
    async def _enqueue_message(self, queue_name: str, message_id: str, priority: MessagePriority):
        """Add message to Redis queue"""
        if priority in [MessagePriority.HIGH, MessagePriority.URGENT, MessagePriority.CRITICAL]:
            await self.redis.lpush(f"priority:{queue_name}", message_id)
        else:
            await self.redis.lpush(f"queue:{queue_name}", message_id)
    
    async def _dequeue_message(self, queue_name: str, timeout: Optional[int] = None) -> Optional[str]:
        """Remove message from Redis queue"""
        # Try priority queue first
        message_id = await self.redis.rpop(f"priority:{queue_name}")
        if message_id:
            await self.redis.sadd(f"processing:{queue_name}", message_id)
            return message_id.decode() if isinstance(message_id, bytes) else message_id
        
        # Try regular queue
        if timeout:
            result = await self.redis.brpop(f"queue:{queue_name}", timeout=timeout)
            if result:
                message_id = result[1]
                await self.redis.sadd(f"processing:{queue_name}", message_id)
                return message_id.decode() if isinstance(message_id, bytes) else message_id
        else:
            message_id = await self.redis.rpop(f"queue:{queue_name}")
            if message_id:
                await self.redis.sadd(f"processing:{queue_name}", message_id)
                return message_id.decode() if isinstance(message_id, bytes) else message_id
        
        return None
    
    async def _schedule_message(self, queue_name: str, message_id: str, delay_seconds: int):
        """Schedule message for delayed delivery"""
        score = datetime.now(timezone.utc).timestamp() + delay_seconds
        await self.redis.zadd(f"delayed:{queue_name}", {message_id: score})
    
    async def _handle_failed_message(self, message: QueuedMessage):
        """Handle failed message processing"""
        message.retry_count += 1
        
        if message.retry_count <= message.max_retries:
            # Retry with exponential backoff
            delay = min(300, 2 ** message.retry_count)  # Max 5 minutes
            message.status = MessageStatus.RETRY.value
            await self._schedule_message(message.queue_name, message.message_id, delay)
        else:
            # Move to dead letter queue
            message.status = MessageStatus.FAILED.value
            if self.queues[message.queue_name].get("dlq_enabled", True):
                await self.redis.lpush(f"dlq:{message.queue_name}", message.message_id)
        
        await self._update_queue_metrics(message.queue_name, "messages_failed", 1)
    
    async def _update_queue_metrics(self, queue_name: str, metric_type: str, value: float):
        """Update queue metrics"""
        metric = MessageBrokerMetrics(
            queue_name=queue_name,
            metric_type=metric_type,
            metric_value=value,
            labels={"queue": queue_name}
        )
        
        self.db.add(metric)
        self.db.commit()
    
    async def _message_processor_worker(self):
        """Background worker for processing messages"""
        while self.running:
            try:
                await asyncio.sleep(1)
                # Process scheduled messages and other background tasks
                
            except Exception as e:
                logger.error(f"Message processor worker error: {e}")
                await asyncio.sleep(5)
    
    async def _delayed_scheduler_worker(self):
        """Background worker for delayed message scheduling"""
        while self.running:
            try:
                await asyncio.sleep(10)
                # Process delayed messages
                
            except Exception as e:
                logger.error(f"Delayed scheduler worker error: {e}")
                await asyncio.sleep(5)
    
    async def _dlq_processor_worker(self):
        """Background worker for dead letter queue processing"""
        while self.running:
            try:
                await asyncio.sleep(60)
                # Process dead letter queues
                
            except Exception as e:
                logger.error(f"DLQ processor worker error: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_collector_worker(self):
        """Background worker for collecting metrics"""
        while self.running:
            try:
                await asyncio.sleep(30)
                # Collect and update metrics
                
            except Exception as e:
                logger.error(f"Metrics collector worker error: {e}")
                await asyncio.sleep(10)


@asynccontextmanager
async def get_message_broker(redis_client: redis.Redis, db_session: Session):
    """Context manager for message broker"""
    broker = MessageBroker(redis_client, db_session)
    try:
        await broker.initialize()
        yield broker
    finally:
        await broker.shutdown()
