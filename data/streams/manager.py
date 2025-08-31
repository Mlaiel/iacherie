"""Core Data Stream Manager for IA Influencer Agent Platform
========================================================

Enterprise-grade stream management for real-time content processing,
protection monitoring, and revenue tracking across multiple platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import json
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from pydantic import BaseModel, Field

from ...core.database import get_async_session
from ...core.cache import get_redis_client
from ...core.config import get_settings
from ...utils.logging import get_logger
from ...models.content import ContentModel
from ...models.stream import StreamModel

logger = get_logger(__name__)
settings = get_settings()


class StreamType(str, Enum):
    """Stream type enumeration for different content categories"""    AUDIO = "audio"
    VIDEO = "video" 
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"
    PROTECTION = "protection"
    REVENUE = "revenue"
    ANALYTICS = "analytics"


class StreamStatus(str, Enum):
    """Stream processing status enumeration"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StreamEvent:
    """Data stream event structure"""    id: str
    stream_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    content_id: Optional[str] = None


class StreamMetrics(BaseModel):
    """Stream performance metrics"""    total_events: int = Field(default=0, description="Total events processed")
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    avg_processing_time: float = Field(default=0.0, description="Average processing time in seconds")
    error_count: int = Field(default=0, description="Total error count")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    throughput_per_second: float = Field(default=0.0, description="Events per second")


class DataStreamManager:
    """    Enterprise-grade data stream manager for real-time content processing
    
    Handles multi-format content streams, protection monitoring, revenue tracking,
    and cross-platform data synchronization with high availability.
    """    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_handlers: Dict[StreamType, List[Callable]] = {}
        self.metrics: Dict[str, StreamMetrics] = {}
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize stream manager with Redis connection and handlers"""        try:
            self.redis = await get_redis_client()
            await self._register_default_handlers()
            logger.info("DataStreamManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DataStreamManager: {e}")
            raise
            
    async def _register_default_handlers(self) -> None:
        """Register default stream handlers for each content type"""        handlers = {
            StreamType.AUDIO: [self._handle_audio_stream],
            StreamType.VIDEO: [self._handle_video_stream],
            StreamType.IMAGE: [self._handle_image_stream],
            StreamType.TEXT: [self._handle_text_stream],
            StreamType.METADATA: [self._handle_metadata_stream],
            StreamType.PROTECTION: [self._handle_protection_stream],
            StreamType.REVENUE: [self._handle_revenue_stream],
            StreamType.ANALYTICS: [self._handle_analytics_stream],
        }
        self.stream_handlers = handlers
        
    async def create_stream(
        self,
        stream_type: StreamType,
        user_id: str,
        content_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Create new data stream for content processing
        
        Args:
            stream_type: Type of stream to create
            user_id: User identifier
            content_id: Optional content identifier
            metadata: Optional stream metadata
            
        Returns:
            Stream identifier
        """        try:
            stream_id = str(uuid4())
            
            stream_config = {
                "id": stream_id,
                "type": stream_type.value,
                "user_id": user_id,
                "content_id": content_id,
                "status": StreamStatus.PENDING.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {},
                "event_count": 0,
            }
            
            # Store stream configuration in Redis
            await self.redis.hset(
                f"stream:{stream_id}",
                mapping={
                    "config": json.dumps(stream_config),
                    "status": StreamStatus.PENDING.value,
                }
            )
            
            # Initialize stream metrics
            self.metrics[stream_id] = StreamMetrics()
            self.active_streams[stream_id] = stream_config
            
            # Set stream TTL (24 hours)
            await self.redis.expire(f"stream:{stream_id}", 86400)
            
            logger.info(f"Created stream {stream_id} for user {user_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to create stream: {e}")
            raise
            
    async def push_event(
        self,
        stream_id: str,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """        Push event to data stream
        
        Args:
            stream_id: Stream identifier
            event_type: Type of event
            data: Event data
            metadata: Optional event metadata
            
        Returns:
            Success status
        """        try:
            if stream_id not in self.active_streams:
                logger.warning(f"Stream {stream_id} not found")
                return False
                
            event = StreamEvent(
                id=str(uuid4()),
                stream_id=stream_id,
                event_type=event_type,
                timestamp=datetime.now(timezone.utc),
                data=data,
                metadata=metadata,
                user_id=self.active_streams[stream_id].get("user_id"),
                content_id=self.active_streams[stream_id].get("content_id")
            )
            
            # Push to Redis stream
            await self.redis.xadd(
                f"events:{stream_id}",
                fields={
                    "event_id": event.id,
                    "event_type": event.event_type,
                    "data": json.dumps(event.data),
                    "metadata": json.dumps(event.metadata or {}),
                    "timestamp": event.timestamp.isoformat(),
                }
            )
            
            # Update stream metrics
            self._update_metrics(stream_id, True)
            
            # Trigger event handlers
            stream_type = StreamType(self.active_streams[stream_id]["type"])
            await self._trigger_handlers(stream_type, event)
            
            logger.debug(f"Pushed event {event.id} to stream {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push event to stream {stream_id}: {e}")
            self._update_metrics(stream_id, False)
            return False
            
    async def get_stream_events(
        self,
        stream_id: str,
        start: str = "0",
        count: int = 100
    ) -> List[StreamEvent]:
        """        Retrieve events from stream
        
        Args:
            stream_id: Stream identifier
            start: Start position (Redis stream ID)
            count: Maximum number of events to retrieve
            
        Returns:
            List of stream events
        """        try:
            events = []
            stream_data = await self.redis.xrange(
                f"events:{stream_id}",
                min=start,
                max="+",
                count=count
            )
            
            for event_id, fields in stream_data:
                event = StreamEvent(
                    id=fields[b"event_id"].decode(),
                    stream_id=stream_id,
                    event_type=fields[b"event_type"].decode(),
                    timestamp=datetime.fromisoformat(fields[b"timestamp"].decode()),
                    data=json.loads(fields[b"data"].decode()),
                    metadata=json.loads(fields[b"metadata"].decode())
                )
                events.append(event)
                
            return events
            
        except Exception as e:
            logger.error(f"Failed to get stream events: {e}")
            return []
            
    async def close_stream(self, stream_id: str) -> bool:
        """        Close and cleanup data stream
        
        Args:
            stream_id: Stream identifier
            
        Returns:
            Success status
        """        try:
            if stream_id in self.active_streams:
                # Update stream status
                await self.redis.hset(
                    f"stream:{stream_id}",
                    "status",
                    StreamStatus.COMPLETED.value
                )
                
                # Remove from active streams
                del self.active_streams[stream_id]
                
                # Archive metrics
                if stream_id in self.metrics:
                    await self._archive_metrics(stream_id)
                    del self.metrics[stream_id]
                    
                logger.info(f"Closed stream {stream_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to close stream {stream_id}: {e}")
            return False
            
    async def register_handler(
        self,
        stream_type: StreamType,
        handler: Callable[[StreamEvent], None]
    ) -> None:
        """Register custom event handler for stream type"""        if stream_type not in self.stream_handlers:
            self.stream_handlers[stream_type] = []
        self.stream_handlers[stream_type].append(handler)
        
    async def get_stream_metrics(self, stream_id: str) -> Optional[StreamMetrics]:
        """Get performance metrics for stream"""        return self.metrics.get(stream_id)
        
    async def list_active_streams(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active streams, optionally filtered by user"""        streams = []
        for stream_id, config in self.active_streams.items():
            if user_id is None or config.get("user_id") == user_id:
                streams.append({
                    "stream_id": stream_id,
                    "type": config["type"],
                    "status": config["status"],
                    "created_at": config["created_at"],
                    "event_count": config.get("event_count", 0),
                    "metrics": self.metrics.get(stream_id)
                })
        return streams
        
    def _update_metrics(self, stream_id: str, success: bool) -> None:
        """Update stream performance metrics"""        if stream_id not in self.metrics:
            self.metrics[stream_id] = StreamMetrics()
            
        metrics = self.metrics[stream_id]
        metrics.total_events += 1
        metrics.last_activity = datetime.now(timezone.utc)
        
        if not success:
            metrics.error_count += 1
            
        # Calculate success rate
        metrics.success_rate = ((metrics.total_events - metrics.error_count) / 
                              metrics.total_events * 100) if metrics.total_events > 0 else 0
                              
    async def _trigger_handlers(self, stream_type: StreamType, event: StreamEvent) -> None:
        """Trigger registered handlers for stream type"""        handlers = self.stream_handlers.get(stream_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Handler error for {stream_type}: {e}")
                
    async def _archive_metrics(self, stream_id: str) -> None:
        """Archive stream metrics to database"""        try:
            metrics = self.metrics.get(stream_id)
            if metrics:
                # Store metrics in database for historical analysis
                await self.redis.hset(
                    f"metrics_archive:{stream_id}",
                    mapping=metrics.dict()
                )
        except Exception as e:
            logger.error(f"Failed to archive metrics: {e}")
            
    # Default stream handlers
    async def _handle_audio_stream(self, event: StreamEvent) -> None:
        """Handle audio stream events"""        logger.debug(f"Processing audio event: {event.event_type}")
        
    async def _handle_video_stream(self, event: StreamEvent) -> None:
        """Handle video stream events"""        logger.debug(f"Processing video event: {event.event_type}")
        
    async def _handle_image_stream(self, event: StreamEvent) -> None:
        """Handle image stream events"""        logger.debug(f"Processing image event: {event.event_type}")
        
    async def _handle_text_stream(self, event: StreamEvent) -> None:
        """Handle text stream events"""        logger.debug(f"Processing text event: {event.event_type}")
        
    async def _handle_metadata_stream(self, event: StreamEvent) -> None:
        """Handle metadata stream events"""        logger.debug(f"Processing metadata event: {event.event_type}")
        
    async def _handle_protection_stream(self, event: StreamEvent) -> None:
        """Handle protection monitoring events"""        logger.debug(f"Processing protection event: {event.event_type}")
        
    async def _handle_revenue_stream(self, event: StreamEvent) -> None:
        """Handle revenue tracking events"""        logger.debug(f"Processing revenue event: {event.event_type}")
        
    async def _handle_analytics_stream(self, event: StreamEvent) -> None:
        """Handle analytics events"""        logger.debug(f"Processing analytics event: {event.event_type}")
        
    async def shutdown(self) -> None:
        """Gracefully shutdown stream manager"""        try:
            self._shutdown_event.set()
            
            # Close all active streams
            for stream_id in list(self.active_streams.keys()):
                await self.close_stream(stream_id)
                
            if self.redis:
                await self.redis.close()
                
            logger.info("DataStreamManager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
