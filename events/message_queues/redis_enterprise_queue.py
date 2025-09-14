"""Redis Enterprise Queue Module

High-performance Redis queue implementation with clustering and persistence
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Redis Enterprise Queue architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from ..core.exceptions import MessageQueueError
from ..core.redis import RedisManager
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels for Redis Enterprise Queue"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class RedisQueueConfig(Enum):
    """Redis queue configuration constants"""
    MAX_RETRY_COUNT = 5
    DEFAULT_TTL = 3600  # 1 hour
    BATCH_SIZE = 100
    COMPRESSION_THRESHOLD = 1024  # 1KB


@dataclass
class QueueMessage:
    """Message structure for Redis Enterprise Queue"""
    id: str = field(default_factory=lambda: str(uuid4()))
    queue_name: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    business_context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for Redis storage"""
        return {
            "id": self.id,
            "queue_name": self.queue_name,
            "payload": self.payload,
            "priority": self.priority.value,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "business_context": self.business_context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueMessage':
        """Create message from dictionary"""
        return cls(
            id=data["id"],
            queue_name=data["queue_name"],
            payload=data["payload"],
            priority=MessagePriority(data["priority"]),
            max_retries=data["max_retries"],
            retry_count=data["retry_count"],
            created_at=datetime.fromisoformat(data["created_at"]),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data["scheduled_at"] else None,
            business_context=data["business_context"]
        )


class AinflueBusiness:
    """Ainflue Business Logic Constants for Redis Queues"""
    
    # Content processing queues
    CONTENT_UPLOAD_QUEUE = "ainflue:queue:content:upload"
    CONTENT_VALIDATION_QUEUE = "ainflue:queue:content:validation"
    CONTENT_AI_ANALYSIS_QUEUE = "ainflue:queue:content:ai-analysis"
    
    # User interaction queues
    USER_REGISTRATION_QUEUE = "ainflue:queue:user:registration"
    USER_PROFILE_UPDATE_QUEUE = "ainflue:queue:user:profile-update"
    USER_AUTHENTICATION_QUEUE = "ainflue:queue:user:authentication"
    
    # Collaboration queues
    COLLABORATION_MATCHING_QUEUE = "ainflue:queue:collaboration:matching"
    COLLABORATION_NOTIFICATION_QUEUE = "ainflue:queue:collaboration:notification"
    COLLABORATION_WORKFLOW_QUEUE = "ainflue:queue:collaboration:workflow"
    
    # Revenue processing queues
    REVENUE_CALCULATION_QUEUE = "ainflue:queue:revenue:calculation"
    PAYMENT_PROCESSING_QUEUE = "ainflue:queue:payment:processing"
    COMMISSION_DISTRIBUTION_QUEUE = "ainflue:queue:commission:distribution"
    
    # SEO optimization queues
    SEO_ANALYSIS_QUEUE = "ainflue:queue:seo:analysis"
    SEO_METADATA_QUEUE = "ainflue:queue:seo:metadata"
    SEO_INDEXING_QUEUE = "ainflue:queue:seo:indexing"
    
    # Distribution queues
    PLATFORM_PUBLISHING_QUEUE = "ainflue:queue:platform:publishing"
    SOCIAL_MEDIA_SYNC_QUEUE = "ainflue:queue:social:sync"
    CONTENT_DISTRIBUTION_QUEUE = "ainflue:queue:content:distribution"


class RedisEnterpriseQueue:
    """
    Redis Enterprise Queue with clustering and persistence
    Optimized for Ainflue business logic with high performance requirements
    """
    
    def __init__(self, 
                 redis_cluster -> None: RedisManager,
                 queue_name -> None: str,
                 encryption_manager -> None: Optional[EncryptionManager] = None,
                 metrics_collector -> None: Optional[MetricsCollector] = None) -> None:
        self.redis = redis_cluster
        self.queue_name = queue_name
        self.encryption = encryption_manager
        self.metrics = metrics_collector
        
        # Redis keys
        self.pending_key = f"{queue_name}:pending"
        self.processing_key = f"{queue_name}:processing"
        self.scheduled_key = f"{queue_name}:scheduled"
        self.dlq_key = f"{queue_name}:dlq"
        self.stats_key = f"{queue_name}:stats"
        
        # Performance optimization
        self._compression_enabled = True
        self._batch_processing = True
        
        logger.info(f"Initialized Redis Enterprise Queue: {queue_name}")
    
    async def enqueue_content_upload(self, 
                                   creator_id: str,
                                   content_data: Dict[str, Any],
                                   priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Enqueue content upload with business context"""
        
        message = QueueMessage(
            queue_name=self.queue_name,
            payload={
                "event_type": "content_upload",
                "creator_id": creator_id,
                "content_data": content_data,
                "business_context": {
                    "workflow_stage": "upload",
                    "requires_ai_analysis": True,
                    "requires_protection": True,
                    "requires_seo_optimization": True
                }
            },
            priority=priority,
            max_retries=5
        )
        
        return await self._enqueue_with_priority(message)
    
    async def enqueue_collaboration_match(self,
                                        requester_id: str,
                                        criteria: Dict[str, Any],
                                        urgency: str = "normal") -> str:
        """Enqueue collaboration matching request"""
        
        priority = MessagePriority.HIGH if urgency == "urgent" else MessagePriority.NORMAL
        
        message = QueueMessage(
            queue_name=self.queue_name,
            payload={
                "event_type": "collaboration_match",
                "requester_id": requester_id,
                "matching_criteria": criteria,
                "business_context": {
                    "workflow_stage": "collaboration",
                    "requires_ml_matching": True,
                    "requires_notification": True
                }
            },
            priority=priority,
            max_retries=3
        )
        
        return await self._enqueue_with_priority(message)
    
    async def enqueue_revenue_calculation(self,
                                        period: str,
                                        creator_ids: List[str],
                                        calculation_type: str = "standard") -> str:
        """Enqueue revenue calculation request"""
        
        priority = MessagePriority.HIGH if calculation_type == "urgent" else MessagePriority.NORMAL
        
        message = QueueMessage(
            queue_name=self.queue_name,
            payload={
                "event_type": "revenue_calculation",
                "period": period,
                "creator_ids": creator_ids,
                "calculation_type": calculation_type,
                "business_context": {
                    "workflow_stage": "revenue",
                    "requires_payment_processing": True,
                    "requires_commission_calculation": True
                }
            },
            priority=priority,
            max_retries=5
        )
        
        return await self._enqueue_with_priority(message)
    
    async def _enqueue_with_priority(self, message: QueueMessage) -> str:
        """Enqueue message with priority handling"""
        try:
            # Serialize message
            message_data = self._serialize_message(message)
            
            # Encrypt if encryption is enabled
            if self.encryption:
                message_data = await self._encrypt_message(message_data)
            
            # Store message data
            await self._store_message_data(message.id, message_data)
            
            # Add to priority queue (sorted set with priority as score)
            score = message.priority.value
            if message.scheduled_at:
                # For scheduled messages, use timestamp as score
                score = message.scheduled_at.timestamp()
                await self._add_to_scheduled_queue(message.id, score)
            else:
                await self._add_to_pending_queue(message.id, score)
            
            # Update metrics
            if self.metrics:
                await self._update_metrics("enqueued", message)
            
            logger.debug(f"Enqueued message {message.id} with priority {message.priority.name}")
            return message.id
            
        except Exception as e:
            logger.error(f"Error enqueuing message: {str(e)}")
            raise MessageQueueError(f"Failed to enqueue message: {str(e)}")
    
    async def dequeue_message(self) -> Optional[QueueMessage]:
        """Dequeue highest priority message"""
        try:
            # First, process any scheduled messages that are ready
            await self._process_scheduled_messages()
            
            # Get highest priority message from pending queue
            result = await self._get_from_pending_queue()
            if not result:
                return None
            
            message_id, priority = result
            
            # Get message data
            message_data = await self._get_message_data(message_id)
            if not message_data:
                logger.warning(f"Message data not found for ID: {message_id}")
                return None
            
            # Decrypt if needed
            if self.encryption:
                message_data = await self._decrypt_message(message_data)
            
            # Deserialize message
            message = self._deserialize_message(message_data)
            
            # Move to processing queue
            await self._move_to_processing(message_id)
            
            # Update metrics
            if self.metrics:
                await self._update_metrics("dequeued", message)
            
            logger.debug(f"Dequeued message {message_id} with priority {priority}")
            return message
            
        except Exception as e:
            logger.error(f"Error dequeuing message: {str(e)}")
            raise MessageQueueError(f"Failed to dequeue message: {str(e)}")
    
    async def ack_message(self, message_id: str) -> bool:
        """Acknowledge successful message processing"""
        try:
            # Remove from processing queue
            await self._remove_from_processing(message_id)
            
            # Clean up message data
            await self._cleanup_message_data(message_id)
            
            # Update metrics
            if self.metrics:
                await self._update_metrics("acknowledged", None)
            
            logger.debug(f"Acknowledged message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging message {message_id}: {str(e)}")
            return False
    
    async def nack_message(self, message_id: str, reason: str = "") -> bool:
        """Negative acknowledge - retry or move to DLQ"""
        try:
            # Get message data
            message_data = await self._get_message_data(message_id)
            if not message_data:
                return False
            
            # Decrypt if needed
            if self.encryption:
                message_data = await self._decrypt_message(message_data)
            
            # Deserialize message
            message = self._deserialize_message(message_data)
            
            # Remove from processing queue
            await self._remove_from_processing(message_id)
            
            # Check retry count
            if message.retry_count >= message.max_retries:
                # Move to dead letter queue
                await self._move_to_dlq(message_id, reason)
                logger.warning(f"Message {message_id} moved to DLQ after {message.retry_count} retries")
            else:
                # Increment retry count and re-queue
                message.retry_count += 1
                await self._store_message_data(message_id, self._serialize_message(message))
                
                # Re-queue with lower priority (higher number)
                new_priority = min(message.priority.value + 1, 3)
                await self._add_to_pending_queue(message_id, new_priority)
                
                logger.info(f"Message {message_id} re-queued for retry {message.retry_count}")
            
            # Update metrics
            if self.metrics:
                await self._update_metrics("negative_acknowledged", message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error negative acknowledging message {message_id}: {str(e)}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics"""
        try:
            stats = {
                "queue_name": self.queue_name,
                "pending_count": await self._get_queue_length(self.pending_key),
                "processing_count": await self._get_queue_length(self.processing_key),
                "scheduled_count": await self._get_queue_length(self.scheduled_key),
                "dlq_count": await self._get_queue_length(self.dlq_key),
                "total_processed": await self._get_total_processed(),
                "error_rate": await self._get_error_rate(),
                "avg_processing_time": await self._get_avg_processing_time(),
                "throughput_per_minute": await self._get_throughput(),
                "memory_usage": await self._get_memory_usage()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {str(e)}")
            return {"error": str(e)}
    
    # Helper methods
    
    def _serialize_message(self, message: QueueMessage) -> str:
        """Serialize message to JSON string"""
        return json.dumps(message.to_dict())
    
    def _deserialize_message(self, data: str) -> QueueMessage:
        """Deserialize message from JSON string"""
        return QueueMessage.from_dict(json.loads(data))
    
    async def _encrypt_message(self, data: str) -> str:
        """Encrypt message data"""
        # Placeholder for encryption
        return data
    
    async def _decrypt_message(self, data: str) -> str:
        """Decrypt message data"""
        # Placeholder for decryption
        return data
    
    async def _store_message_data(self, message_id -> None: str, data -> None: str) -> None:
        """Store message data in Redis"""
        key = f"message:{message_id}"
        # Set with TTL for automatic cleanup
        await self._redis_set(key, data, ex=RedisQueueConfig.DEFAULT_TTL.value)
    
    async def _get_message_data(self, message_id: str) -> Optional[str]:
        """Get message data from Redis"""
        key = f"message:{message_id}"
        return await self._redis_get(key)
    
    async def _cleanup_message_data(self, message_id -> None: str) -> None:
        """Clean up message data"""
        key = f"message:{message_id}"
        await self._redis_delete(key)
    
    async def _add_to_pending_queue(self, message_id -> None: str, priority -> None: float) -> None:
        """Add message to pending queue with priority"""
        await self._redis_zadd(self.pending_key, {message_id: priority})
    
    async def _add_to_scheduled_queue(self, message_id -> None: str, timestamp -> None: float) -> None:
        """Add message to scheduled queue"""
        await self._redis_zadd(self.scheduled_key, {message_id: timestamp})
    
    async def _get_from_pending_queue(self) -> Optional[tuple]:
        """Get highest priority message from pending queue"""
        result = await self._redis_zpopmin(self.pending_key)
        if result:
            return result[0]  # (message_id, priority)
        return None
    
    async def _move_to_processing(self, message_id -> None: str) -> None:
        """Move message to processing queue"""
        timestamp = time.time()
        await self._redis_zadd(self.processing_key, {message_id: timestamp})
    
    async def _remove_from_processing(self, message_id -> None: str) -> None:
        """Remove message from processing queue"""
        await self._redis_zrem(self.processing_key, message_id)
    
    async def _move_to_dlq(self, message_id -> None: str, reason -> None: str = "") -> None:
        """Move message to dead letter queue"""
        timestamp = time.time()
        dlq_data = {
            "message_id": message_id,
            "reason": reason,
            "timestamp": timestamp
        }
        await self._redis_zadd(self.dlq_key, {json.dumps(dlq_data): timestamp})
    
    async def _process_scheduled_messages(self) -> None:
        """Move ready scheduled messages to pending queue"""
        current_time = time.time()
        
        # Get messages ready for processing
        ready_messages = await self._redis_zrangebyscore(
            self.scheduled_key, 0, current_time
        )
        
        if ready_messages:
            for message_id in ready_messages:
                # Get message to determine priority
                message_data = await self._get_message_data(message_id)
                if message_data:
                    message = self._deserialize_message(message_data)
                    
                    # Move to pending queue
                    await self._add_to_pending_queue(message_id, message.priority.value)
                    await self._redis_zrem(self.scheduled_key, message_id)
    
    async def _get_queue_length(self, key: str) -> int:
        """Get queue length"""
        return await self._redis_zcard(key)
    
    async def _get_total_processed(self) -> int:
        """Get total processed messages count"""
        stats_data = await self._redis_hget(self.stats_key, "total_processed")
        return int(stats_data) if stats_data else 0
    
    async def _get_error_rate(self) -> float:
        """Get error rate percentage"""
        total = await self._get_total_processed()
        errors = await self._redis_hget(self.stats_key, "total_errors")
        errors = int(errors) if errors else 0
        
        if total == 0:
            return 0.0
        return (errors / total) * 100
    
    async def _get_avg_processing_time(self) -> float:
        """Get average processing time in seconds"""
        avg_time = await self._redis_hget(self.stats_key, "avg_processing_time")
        return float(avg_time) if avg_time else 0.0
    
    async def _get_throughput(self) -> float:
        """Get throughput per minute"""
        throughput = await self._redis_hget(self.stats_key, "throughput_per_minute")
        return float(throughput) if throughput else 0.0
    
    async def _get_memory_usage(self) -> int:
        """Get approximate memory usage in bytes"""
        return await self._redis_memory_usage(self.queue_name)
    
    async def _update_metrics(self, action -> None: str, message -> None: Optional[QueueMessage]) -> None:
        """Update queue metrics"""
        if not self.metrics:
            return
        
        timestamp = time.time()
        
        # Update action counters
        await self._redis_hincrby(self.stats_key, f"total_{action}", 1)
        
        # Update throughput
        current_minute = int(timestamp / 60)
        throughput_key = f"{self.stats_key}:throughput:{current_minute}"
        await self._redis_incr(throughput_key)
        await self._redis_expire(throughput_key, 3600)  # Expire after 1 hour
    
    # Redis operation wrappers (placeholder implementations)
    
    async def _redis_set(self, key -> None: str, value -> None: str, ex -> None: int = None) -> None:
        """Redis SET operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis SET: {key}")
    
    async def _redis_get(self, key: str) -> Optional[str]:
        """Redis GET operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis GET: {key}")
        return None
    
    async def _redis_delete(self, key -> None: str) -> None:
        """Redis DELETE operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis DELETE: {key}")
    
    async def _redis_zadd(self, key -> None: str, mapping -> None: Dict[str, float]) -> None:
        """Redis ZADD operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis ZADD: {key}")
    
    async def _redis_zpopmin(self, key -> None: str) -> None:
        """Redis ZPOPMIN operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis ZPOPMIN: {key}")
        return None
    
    async def _redis_zrem(self, key -> None: str, member -> None: str) -> None:
        """Redis ZREM operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis ZREM: {key}")
    
    async def _redis_zrangebyscore(self, key -> None: str, min_score -> None: float, max_score -> None: float) -> None:
        """Redis ZRANGEBYSCORE operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis ZRANGEBYSCORE: {key}")
        return []
    
    async def _redis_zcard(self, key: str) -> int:
        """Redis ZCARD operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis ZCARD: {key}")
        return 0
    
    async def _redis_hget(self, key: str, field: str) -> Optional[str]:
        """Redis HGET operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis HGET: {key} {field}")
        return None
    
    async def _redis_hincrby(self, key -> None: str, field -> None: str, increment -> None: int) -> None:
        """Redis HINCRBY operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis HINCRBY: {key} {field}")
    
    async def _redis_incr(self, key -> None: str) -> None:
        """Redis INCR operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis INCR: {key}")
    
    async def _redis_expire(self, key -> None: str, seconds -> None: int) -> None:
        """Redis EXPIRE operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis EXPIRE: {key}")
    
    async def _redis_memory_usage(self, pattern: str) -> int:
        """Redis MEMORY USAGE operation"""
        # Placeholder - would use actual Redis client
        logger.debug(f"Redis MEMORY USAGE: {pattern}")
        return 0


# Export for public API
__all__ = [
    "RedisEnterpriseQueue",
    "QueueMessage", 
    "MessagePriority",
    "RedisQueueConfig",
    "AinflueBusiness"
]