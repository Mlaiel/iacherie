"""Ainflue Core Infrastructure - Message Queue Core
==================================================

Enterprise-grade message queue management providing asynchronous communication,
event-driven processing, task distribution, and reliable message delivery across
microservices architecture for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import threading
import time
from collections import defaultdict, deque

# Setup logger
logger = logging.getLogger(__name__)

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"

class QueueType(str, Enum):
    """Queue types"""
    FIFO = "fifo"
    PRIORITY = "priority"
    DELAY = "delay"
    DEAD_LETTER = "dead_letter"
    BROADCAST = "broadcast"

@dataclass
class Message:
    """Message data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    timeout_seconds: int = 300

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'topic': self.topic,
            'payload': self.payload,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'metadata': self.metadata,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'timeout_seconds': self.timeout_seconds
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        message = cls()
        message.id = data.get('id', message.id)
        message.topic = data.get('topic', '')
        message.payload = data.get('payload', {})
        message.priority = MessagePriority(data.get('priority', MessagePriority.NORMAL.value))
        message.status = MessageStatus(data.get('status', MessageStatus.PENDING.value))
        message.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        message.scheduled_at = datetime.fromisoformat(data['scheduled_at']) if data.get('scheduled_at') else None
        message.attempts = data.get('attempts', 0)
        message.max_attempts = data.get('max_attempts', 3)
        message.metadata = data.get('metadata', {})
        message.correlation_id = data.get('correlation_id')
        message.reply_to = data.get('reply_to')
        message.timeout_seconds = data.get('timeout_seconds', 300)
        return message

@dataclass
class QueueStats:
    """Queue statistics"""
    total_messages: int = 0
    pending_messages: int = 0
    processing_messages: int = 0
    processed_messages: int = 0
    failed_messages: int = 0
    dead_letter_messages: int = 0
    avg_processing_time: float = 0.0
    throughput_per_second: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

class MessageHandler(ABC):
    """Abstract message handler"""
    
    @abstractmethod
    async def handle(self, message: Message) -> bool:
        """Handle message processing"""
        pass
    
    @abstractmethod
    async def on_error(self, message: Message, error: Exception) -> bool:
        """Handle processing errors"""
        pass

class InMemoryQueue:
    """In-memory message queue implementation"""
    
    def __init__(self, name: str, queue_type: QueueType = QueueType.FIFO):
        self.name = name
        self.queue_type = queue_type
        self.messages = deque()
        self.priority_messages = defaultdict(deque)
        self.delayed_messages = []
        self.processing_messages = {}
        self.dead_letter_messages = deque()
        self.stats = QueueStats()
        self.lock = threading.Lock()
        
    def enqueue(self, message: Message) -> bool:
        """Add message to queue"""
        try:
            with self.lock:
                if message.scheduled_at and message.scheduled_at > datetime.utcnow():
                    # Delayed message
                    self.delayed_messages.append(message)
                    self.delayed_messages.sort(key=lambda m: m.scheduled_at)
                elif self.queue_type == QueueType.PRIORITY:
                    self.priority_messages[message.priority].append(message)
                else:
                    self.messages.append(message)
                
                self.stats.total_messages += 1
                self.stats.pending_messages += 1
                return True
        except Exception as e:
            logger.error(f"Failed to enqueue message {message.id}: {str(e)}")
            return False
    
    def dequeue(self) -> Optional[Message]:
        """Get next message from queue"""
        try:
            with self.lock:
                # Check delayed messages first
                self._process_delayed_messages()
                
                message = None
                if self.queue_type == QueueType.PRIORITY:
                    # Process by priority order
                    for priority in [MessagePriority.URGENT, MessagePriority.CRITICAL, 
                                   MessagePriority.HIGH, MessagePriority.NORMAL, MessagePriority.LOW]:
                        if self.priority_messages[priority]:
                            message = self.priority_messages[priority].popleft()
                            break
                elif self.messages:
                    message = self.messages.popleft()
                
                if message:
                    message.status = MessageStatus.PROCESSING
                    message.attempts += 1
                    self.processing_messages[message.id] = message
                    self.stats.pending_messages -= 1
                    self.stats.processing_messages += 1
                
                return message
        except Exception as e:
            logger.error(f"Failed to dequeue message: {str(e)}")
            return None
    
    def _process_delayed_messages(self):
        """Move ready delayed messages to main queue"""
        now = datetime.utcnow()
        ready_messages = []
        
        for message in self.delayed_messages[:]:
            if message.scheduled_at <= now:
                ready_messages.append(message)
                self.delayed_messages.remove(message)
        
        for message in ready_messages:
            if self.queue_type == QueueType.PRIORITY:
                self.priority_messages[message.priority].append(message)
            else:
                self.messages.append(message)
    
    def complete_message(self, message_id: str, success: bool = True) -> bool:
        """Mark message as completed"""
        try:
            with self.lock:
                if message_id in self.processing_messages:
                    message = self.processing_messages.pop(message_id)
                    
                    if success:
                        message.status = MessageStatus.PROCESSED
                        self.stats.processed_messages += 1
                    else:
                        if message.attempts >= message.max_attempts:
                            message.status = MessageStatus.DEAD_LETTER
                            self.dead_letter_messages.append(message)
                            self.stats.dead_letter_messages += 1
                        else:
                            message.status = MessageStatus.RETRY
                            # Re-queue for retry
                            if self.queue_type == QueueType.PRIORITY:
                                self.priority_messages[message.priority].append(message)
                            else:
                                self.messages.append(message)
                            self.stats.pending_messages += 1
                    
                    self.stats.processing_messages -= 1
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to complete message {message_id}: {str(e)}")
            return False
    
    def get_stats(self) -> QueueStats:
        """Get queue statistics"""
        with self.lock:
            return self.stats

class MessageQueueCore:
    """Core message queue management system"""
    
    def __init__(self, level: str = "enterprise"):
        self.level = level
        self.queues: Dict[str, InMemoryQueue] = {}
        self.handlers: Dict[str, List[MessageHandler]] = defaultdict(list)
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.worker_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self.metrics = {
            'total_messages_processed': 0,
            'total_processing_time': 0.0,
            'start_time': datetime.utcnow()
        }
        
        logger.info(f"Message Queue Core initialized - Level: {level}")
    
    async def initialize(self) -> bool:
        """Initialize message queue system"""
        try:
            # Create default queues
            self.create_queue("default", QueueType.FIFO)
            self.create_queue("priority", QueueType.PRIORITY)
            self.create_queue("delayed", QueueType.DELAY)
            self.create_queue("dead_letter", QueueType.DEAD_LETTER)
            
            logger.info("Message Queue Core initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Message Queue Core: {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start message queue processing"""
        try:
            self.is_running = True
            
            # Start workers for each queue
            for queue_name in self.queues.keys():
                if queue_name not in self.worker_tasks:
                    self.worker_tasks[queue_name] = asyncio.create_task(
                        self._queue_worker(queue_name)
                    )
            
            logger.info("Message Queue Core started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Message Queue Core: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop message queue processing"""
        try:
            self.is_running = False
            
            # Cancel all worker tasks
            for task in self.worker_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks.values(), return_exceptions=True)
            
            self.worker_tasks.clear()
            logger.info("Message Queue Core stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Message Queue Core: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check system health"""
        try:
            # Check if queues are responsive
            for queue_name, queue in self.queues.items():
                stats = queue.get_stats()
                if stats.pending_messages > 10000:  # Too many pending messages
                    logger.warning(f"Queue {queue_name} has high pending messages: {stats.pending_messages}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def create_queue(self, name: str, queue_type: QueueType = QueueType.FIFO) -> bool:
        """Create a new queue"""
        try:
            if name not in self.queues:
                self.queues[name] = InMemoryQueue(name, queue_type)
                logger.info(f"Created queue: {name} (type: {queue_type.value})")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to create queue {name}: {str(e)}")
            return False
    
    def delete_queue(self, name: str) -> bool:
        """Delete a queue"""
        try:
            if name in self.queues:
                # Stop worker if running
                if name in self.worker_tasks:
                    self.worker_tasks[name].cancel()
                    del self.worker_tasks[name]
                
                del self.queues[name]
                logger.info(f"Deleted queue: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete queue {name}: {str(e)}")
            return False
    
    async def publish(self, topic: str, payload: Dict[str, Any], 
                     priority: MessagePriority = MessagePriority.NORMAL,
                     delay_seconds: int = 0,
                     queue_name: str = "default") -> str:
        """Publish message to queue"""
        try:
            message = Message(
                topic=topic,
                payload=payload,
                priority=priority,
                scheduled_at=datetime.utcnow() + timedelta(seconds=delay_seconds) if delay_seconds > 0 else None
            )
            
            if queue_name in self.queues:
                success = self.queues[queue_name].enqueue(message)
                if success:
                    logger.debug(f"Published message {message.id} to queue {queue_name}")
                    return message.id
            
            raise Exception(f"Queue {queue_name} not found")
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise
    
    def subscribe(self, topic: str, handler: Callable[[Message], bool]) -> bool:
        """Subscribe to topic messages"""
        try:
            self.subscribers[topic].append(handler)
            logger.info(f"Subscribed handler to topic: {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {topic}: {str(e)}")
            return False
    
    def unsubscribe(self, topic: str, handler: Callable[[Message], bool]) -> bool:
        """Unsubscribe from topic messages"""
        try:
            if topic in self.subscribers and handler in self.subscribers[topic]:
                self.subscribers[topic].remove(handler)
                logger.info(f"Unsubscribed handler from topic: {topic}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic {topic}: {str(e)}")
            return False
    
    async def _queue_worker(self, queue_name: str):
        """Worker process for queue messages"""
        queue = self.queues[queue_name]
        
        while self.is_running:
            try:
                message = queue.dequeue()
                if message:
                    start_time = time.time()
                    success = await self._process_message(message)
                    processing_time = time.time() - start_time
                    
                    queue.complete_message(message.id, success)
                    
                    # Update metrics
                    self.metrics['total_messages_processed'] += 1
                    self.metrics['total_processing_time'] += processing_time
                else:
                    # No messages, sleep briefly
                    await asyncio.sleep(0.1)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue worker error for {queue_name}: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_message(self, message: Message) -> bool:
        """Process individual message"""
        try:
            # Call topic subscribers
            if message.topic in self.subscribers:
                for handler in self.subscribers[message.topic]:
                    try:
                        success = await handler(message) if asyncio.iscoroutinefunction(handler) else handler(message)
                        if not success:
                            return False
                    except Exception as e:
                        logger.error(f"Handler error for message {message.id}: {str(e)}")
                        return False
            
            # Call registered handlers
            if message.topic in self.handlers:
                for handler in self.handlers[message.topic]:
                    try:
                        success = await handler.handle(message)
                        if not success:
                            return False
                    except Exception as e:
                        logger.error(f"Handler error for message {message.id}: {str(e)}")
                        await handler.on_error(message, e)
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {str(e)}")
            return False
    
    def get_queue_stats(self, queue_name: str) -> Optional[QueueStats]:
        """Get statistics for specific queue"""
        if queue_name in self.queues:
            return self.queues[queue_name].get_stats()
        return None
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
        avg_processing_time = (
            self.metrics['total_processing_time'] / self.metrics['total_messages_processed']
            if self.metrics['total_messages_processed'] > 0 else 0
        )
        
        return {
            'level': self.level,
            'uptime_seconds': uptime,
            'total_queues': len(self.queues),
            'total_messages_processed': self.metrics['total_messages_processed'],
            'avg_processing_time_seconds': avg_processing_time,
            'throughput_per_second': self.metrics['total_messages_processed'] / uptime if uptime > 0 else 0,
            'active_workers': len([task for task in self.worker_tasks.values() if not task.done()]),
            'queue_stats': {name: queue.get_stats() for name, queue in self.queues.items()}
        }

# Global instance
message_queue_core = MessageQueueCore()

# Convenience functions
async def publish_message(topic: str, payload: Dict[str, Any], 
                         priority: MessagePriority = MessagePriority.NORMAL,
                         delay_seconds: int = 0) -> str:
    """Publish message to default queue"""
    return await message_queue_core.publish(topic, payload, priority, delay_seconds)

def subscribe_to_topic(topic: str, handler: Callable[[Message], bool]) -> bool:
    """Subscribe to topic messages"""
    return message_queue_core.subscribe(topic, handler)

def get_queue_statistics(queue_name: str = "default") -> Optional[QueueStats]:
    """Get queue statistics"""
    return message_queue_core.get_queue_stats(queue_name)

# Module exports
__all__ = [
    "MessageQueueCore", "Message", "MessageHandler", "MessagePriority", 
    "MessageStatus", "QueueType", "QueueStats", "InMemoryQueue",
    "message_queue_core", "publish_message", "subscribe_to_topic", 
    "get_queue_statistics"
]

logger.info("Message Queue Core module loaded")