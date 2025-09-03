"""
IA Influencer Agent - Redis Message Backend
Redis implementation for the unified messaging system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Simple Redis implementation that works with current dependencies
import redis

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from unified_messaging import MessageBackend, Message, QueueStats, MessageStatus
from messaging_config import MessagingConfig

logger = logging.getLogger(__name__)


class RedisBackend(MessageBackend):
    """Redis implementation of the message backend using redis-py with async wrapper"""
    
    def __init__(self, config: MessagingConfig):
        super().__init__(config)
        self.client: Optional[redis.Redis] = None
        self.consumer_groups: Dict[str, str] = {}
    
    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            # Create Redis connection
            self.client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True
            )
            
            # Test connection
            self.client.ping()
            logger.info("Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("Disconnected from Redis")
    
    async def publish(self, message: Message) -> str:
        """Publish a message to Redis using lists for simplicity"""
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            # Prepare message data
            message_data = message.to_dict()
            serialized_data = json.dumps(message_data)
            
            # Handle delayed messages
            if message.scheduled_at and message.scheduled_at > datetime.utcnow():
                # Store in delayed queue using sorted set
                delay_timestamp = message.scheduled_at.timestamp()
                await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: self.client.zadd(
                        f"{message.queue_name}:delayed",
                        {serialized_data: delay_timestamp}
                    )
                )
                return message.id
            
            # Choose queue based on priority
            queue_key = message.queue_name
            if message.priority.value > 3:  # High priority
                queue_key = f"{message.queue_name}:high"
            
            # Add to list (right push for FIFO)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.lpush(queue_key, serialized_data)
            )
            
            # Limit queue size
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.ltrim(queue_key, 0, self.config.default_queue_maxsize - 1)
            )
            
            return message.id
            
        except Exception as e:
            logger.error(f"Failed to publish message to Redis: {e}")
            raise
    
    async def consume(self, queue_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Consume a message from Redis"""
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            # Process delayed messages first
            await self._process_delayed_messages(queue_name)
            
            # Check high priority queue first
            high_priority_queue = f"{queue_name}:high"
            message = await self._consume_from_queue(high_priority_queue, timeout)
            if message:
                return message
            
            # Then check normal priority queue
            return await self._consume_from_queue(queue_name, timeout)
            
        except Exception as e:
            logger.error(f"Failed to consume from Redis: {e}")
            raise
    
    async def _consume_from_queue(self, queue_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Consume from a specific Redis list"""
        try:
            # Use blocking pop with timeout
            timeout_int = int(timeout) if timeout else 1
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.brpop(queue_name, timeout=timeout_int)
            )
            
            if not result:
                return None
            
            # Parse message
            queue_key, message_data = result
            message_dict = json.loads(message_data)
            message = Message.from_dict(message_dict)
            message.status = MessageStatus.PROCESSING
            
            # Store processing info for acknowledgment
            processing_info = {
                "queue_name": queue_name,
                "started_at": datetime.utcnow().isoformat(),
                "message_data": message_data
            }
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.hset(
                    f"{queue_name}:processing",
                    message.id,
                    json.dumps(processing_info)
                )
            )
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to consume from queue {queue_name}: {e}")
            return None
    
    async def _process_delayed_messages(self, queue_name: str) -> None:
        """Process delayed messages that are ready"""
        try:
            delayed_key = f"{queue_name}:delayed"
            now = time.time()
            
            # Get messages that are ready
            ready_messages = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.zrangebyscore(delayed_key, 0, now, withscores=True)
            )
            
            if not ready_messages:
                return
            
            # Process each ready message
            for message_data, score in ready_messages:
                try:
                    # Parse and republish message
                    message_dict = json.loads(message_data)
                    message = Message.from_dict(message_dict)
                    
                    # Remove from delayed queue
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.zrem(delayed_key, message_data)
                    )
                    
                    # Republish to main queue
                    await self.publish(message)
                    
                except Exception as e:
                    logger.error(f"Failed to process delayed message: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to process delayed messages: {e}")
    
    async def ack(self, message: Message) -> None:
        """Acknowledge message processing"""
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            # Remove processing info
            processing_key = f"{message.queue_name}:processing"
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.hdel(processing_key, message.id)
            )
            
            logger.debug(f"Acknowledged message {message.id}")
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message.id}: {e}")
            raise
    
    async def nack(self, message: Message, requeue: bool = True) -> None:
        """Negative acknowledge message"""
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            if requeue:
                # Republish the message
                await self.publish(message)
            
            # Remove processing info
            processing_key = f"{message.queue_name}:processing"
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.hdel(processing_key, message.id)
            )
            
            logger.debug(f"Negative acknowledged message {message.id}, requeue: {requeue}")
            
        except Exception as e:
            logger.error(f"Failed to nack message {message.id}: {e}")
            raise
    
    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Get queue statistics"""
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            stats = QueueStats(queue_name=queue_name)
            
            # Count messages in main queue
            stats.pending_messages = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.llen(queue_name)
            )
            
            # Count messages in high priority queue
            high_priority_count = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.llen(f"{queue_name}:high")
            )
            stats.pending_messages += high_priority_count
            
            # Count processing messages
            processing_key = f"{queue_name}:processing"
            stats.processing_messages = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.hlen(processing_key)
            )
            
            # Count delayed messages
            delayed_key = f"{queue_name}:delayed"
            delayed_count = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.zcard(delayed_key)
            )
            stats.pending_messages += delayed_count
            
            # Count DLQ messages
            dlq_key = f"{queue_name}.dlq"
            stats.dead_letter_messages = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.llen(dlq_key)
            )
            
            stats.last_updated = datetime.utcnow()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats for {queue_name}: {e}")
            raise
    
    async def purge_queue(self, queue_name: str) -> int:
        """Purge all messages from queue"""
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            deleted_count = 0
            keys_to_delete = [
                queue_name,
                f"{queue_name}:high",
                f"{queue_name}:delayed",
                f"{queue_name}:processing"
            ]
            
            for key in keys_to_delete:
                deleted = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda k=key: self.client.delete(k)
                )
                deleted_count += deleted
            
            logger.info(f"Purged queue {queue_name}, deleted {deleted_count} keys")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to purge queue {queue_name}: {e}")
            raise