"""
Base Analytics Events Module

Ultra-advanced base classes and core functionality for analytics events system.
Provides foundational infrastructure for all analytics event handlers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
⚠️  WARNING: This code and concept are proprietary to Fahed Mlaiel.
    Any unauthorized use, copying, or distribution without explicit written 
    permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
import aioredis
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, validator
import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for processing queue"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class EventStatus(Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class EventCategory(Enum):
    """Analytics event categories"""
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    CONTENT = "content"
    USER_BEHAVIOR = "user_behavior"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    PLATFORM = "platform"
    REAL_TIME = "real_time"
    PREDICTION = "prediction"
    BUSINESS_INTELLIGENCE = "business_intelligence"


@dataclass
class EventMetadata:
    """Metadata for analytics events"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "ia_influencer_agent"
    version: str = "1.0.0"
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    platform: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AnalyticsEvent(BaseModel):
    """Base analytics event model with validation"""
    
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(..., description="Type of analytics event")
    category: EventCategory = Field(..., description="Event category")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    status: EventStatus = Field(default=EventStatus.PENDING)
    retry_count: int = Field(default=0, ge=0, le=5)
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_duration: Optional[float] = None
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('timestamp', pre=True)
    def validate_timestamp(cls, v):
        """Validate and normalize timestamp"""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        elif isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v
        return datetime.now(timezone.utc)
    
    @validator('data')
    def validate_data(cls, v):
        """Validate event data"""
        if not isinstance(v, dict):
            raise ValueError("Event data must be a dictionary")
        return v
    
    def add_tag(self, tag: str) -> None:
        """Add tag to event metadata"""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
    
    def set_custom_attribute(self, key: str, value: Any) -> None:
        """Set custom attribute in metadata"""
        self.metadata.custom_attributes[key] = value
    
    def mark_processing(self) -> None:
        """Mark event as processing"""
        self.status = EventStatus.PROCESSING
        self.processed_at = datetime.now(timezone.utc)
    
    def mark_completed(self, duration: float = None) -> None:
        """Mark event as completed"""
        self.status = EventStatus.COMPLETED
        if duration:
            self.processing_duration = duration
    
    def mark_failed(self, error: str) -> None:
        """Mark event as failed"""
        self.status = EventStatus.FAILED
        self.error_message = error
        self.retry_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        data = self.dict()
        data['timestamp'] = self.timestamp.isoformat()
        if self.processed_at:
            data['processed_at'] = self.processed_at.isoformat()
        return data


class BaseAnalyticsEventHandler(ABC):
    """Abstract base class for analytics event handlers"""
    
    def __init__(self, 
                 name: str,
                 db_session: Optional[AsyncSession] = None,
                 redis_client: Optional[aioredis.Redis] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize base analytics event handler
        
        Args:
            name: Handler name
            db_session: Database session
            redis_client: Redis client for caching
            config: Handler configuration
        """
        self.name = name
        self.db_session = db_session
        self.redis_client = redis_client
        self.config = config or {}
        self.metrics = {
            'events_processed': 0,
            'events_failed': 0,
            'total_processing_time': 0.0,
            'avg_processing_time': 0.0,
            'last_processed': None
        }
        self.is_active = True
        self._event_queue = asyncio.Queue()
        self._processors = []
    
    @abstractmethod
    async def process_event(self, event: AnalyticsEvent) -> Dict[str, Any]:
        """
        Process analytics event (must be implemented by subclasses)
        
        Args:
            event: Analytics event to process
            
        Returns:
            Processing result
        """
        pass
    
    @abstractmethod
    async def validate_event(self, event: AnalyticsEvent) -> bool:
        """
        Validate analytics event (must be implemented by subclasses)
        
        Args:
            event: Analytics event to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    async def handle_event(self, event: AnalyticsEvent) -> Dict[str, Any]:
        """
        Main event handling method with error handling and metrics
        
        Args:
            event: Analytics event to handle
            
        Returns:
            Handling result
        """
        start_time = time.time()
        
        try:
            # Validate event
            if not await self.validate_event(event):
                raise ValueError(f"Event validation failed for {event.event_id}")
            
            # Mark as processing
            event.mark_processing()
            
            # Process event
            result = await self.process_event(event)
            
            # Mark as completed
            processing_time = time.time() - start_time
            event.mark_completed(processing_time)
            
            # Update metrics
            await self._update_metrics(processing_time, success=True)
            
            # Cache result if Redis is available
            if self.redis_client:
                await self._cache_result(event.event_id, result)
            
            logger.info(f"Event {event.event_id} processed successfully by {self.name}")
            
            return {
                'status': 'success',
                'event_id': event.event_id,
                'processing_time': processing_time,
                'result': result
            }
            
        except Exception as e:
            # Mark as failed
            event.mark_failed(str(e))
            
            # Update metrics
            await self._update_metrics(time.time() - start_time, success=False)
            
            logger.error(f"Error processing event {event.event_id} in {self.name}: {str(e)}")
            
            return {
                'status': 'error',
                'event_id': event.event_id,
                'error': str(e),
                'retry_count': event.retry_count
            }
    
    async def batch_process_events(self, events: List[AnalyticsEvent]) -> List[Dict[str, Any]]:
        """
        Process multiple events in batch
        
        Args:
            events: List of analytics events
            
        Returns:
            List of processing results
        """
        tasks = [self.handle_event(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'error',
                    'event_id': events[i].event_id,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def start_background_processing(self, max_workers: int = 5) -> None:
        """Start background event processing"""
        for i in range(max_workers):
            processor = asyncio.create_task(self._background_processor(f"worker-{i}"))
            self._processors.append(processor)
        
        logger.info(f"Started {max_workers} background processors for {self.name}")
    
    async def stop_background_processing(self) -> None:
        """Stop background event processing"""
        self.is_active = False
        
        # Cancel all processors
        for processor in self._processors:
            processor.cancel()
        
        # Wait for processors to finish
        await asyncio.gather(*self._processors, return_exceptions=True)
        
        logger.info(f"Stopped background processing for {self.name}")
    
    async def enqueue_event(self, event: AnalyticsEvent) -> None:
        """Add event to processing queue"""
        await self._event_queue.put(event)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get handler metrics"""
        return {
            'handler_name': self.name,
            'is_active': self.is_active,
            'queue_size': self._event_queue.qsize(),
            'active_processors': len([p for p in self._processors if not p.done()]),
            **self.metrics
        }
    
    async def _background_processor(self, worker_id: str) -> None:
        """Background event processor"""
        logger.info(f"Background processor {worker_id} started for {self.name}")
        
        while self.is_active:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Process event
                await self.handle_event(event)
                
                # Mark task as done
                self._event_queue.task_done()
                
            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in background processor {worker_id}: {str(e)}")
        
        logger.info(f"Background processor {worker_id} stopped for {self.name}")
    
    async def _update_metrics(self, processing_time: float, success: bool) -> None:
        """Update handler metrics"""
        if success:
            self.metrics['events_processed'] += 1
        else:
            self.metrics['events_failed'] += 1
        
        self.metrics['total_processing_time'] += processing_time
        
        total_events = self.metrics['events_processed'] + self.metrics['events_failed']
        if total_events > 0:
            self.metrics['avg_processing_time'] = self.metrics['total_processing_time'] / total_events
        
        self.metrics['last_processed'] = datetime.now(timezone.utc).isoformat()
    
    async def _cache_result(self, event_id: str, result: Dict[str, Any]) -> None:
        """Cache processing result"""
        try:
            cache_key = f"analytics_result:{self.name}:{event_id}"
            cache_value = json.dumps(result, default=str)
            await self.redis_client.setex(cache_key, 3600, cache_value)  # 1 hour TTL
        except Exception as e:
            logger.warning(f"Failed to cache result for {event_id}: {str(e)}")


class EventProcessor:
    """High-level event processor that coordinates multiple handlers"""
    
    def __init__(self):
        """Initialize event processor"""
        self.handlers: Dict[str, BaseAnalyticsEventHandler] = {}
        self.routes: Dict[EventCategory, List[str]] = {}
        self.middleware: List[Callable] = []
        self.metrics = {
            'total_events': 0,
            'events_by_category': {},
            'events_by_handler': {},
            'total_processing_time': 0.0
        }
    
    def register_handler(self, 
                        handler: BaseAnalyticsEventHandler,
                        categories: List[EventCategory]) -> None:
        """
        Register event handler for specific categories
        
        Args:
            handler: Analytics event handler
            categories: List of event categories to handle
        """
        self.handlers[handler.name] = handler
        
        for category in categories:
            if category not in self.routes:
                self.routes[category] = []
            self.routes[category].append(handler.name)
        
        logger.info(f"Registered handler {handler.name} for categories: {categories}")
    
    def add_middleware(self, middleware_func: Callable) -> None:
        """Add middleware function to processing pipeline"""
        self.middleware.append(middleware_func)
        logger.info(f"Added middleware: {middleware_func.__name__}")
    
    async def process_event(self, event: AnalyticsEvent) -> List[Dict[str, Any]]:
        """
        Process event through appropriate handlers
        
        Args:
            event: Analytics event to process
            
        Returns:
            List of processing results from all handlers
        """
        start_time = time.time()
        
        try:
            # Apply middleware
            for middleware in self.middleware:
                event = await middleware(event)
                if event is None:
                    return [{'status': 'filtered', 'reason': 'middleware'}]
            
            # Get handlers for event category
            handler_names = self.routes.get(event.category, [])
            if not handler_names:
                logger.warning(f"No handlers registered for category: {event.category}")
                return [{'status': 'no_handlers', 'category': event.category.value}]
            
            # Process event with all handlers
            results = []
            for handler_name in handler_names:
                handler = self.handlers[handler_name]
                result = await handler.handle_event(event)
                results.append(result)
            
            # Update metrics
            processing_time = time.time() - start_time
            await self._update_processor_metrics(event, processing_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in event processor: {str(e)}")
            return [{'status': 'error', 'error': str(e)}]
    
    async def batch_process_events(self, events: List[AnalyticsEvent]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process multiple events in batch
        
        Args:
            events: List of analytics events
            
        Returns:
            Dictionary mapping event IDs to processing results
        """
        tasks = [self.process_event(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        batch_results = {}
        for i, result in enumerate(results):
            event_id = events[i].event_id
            if isinstance(result, Exception):
                batch_results[event_id] = [{'status': 'error', 'error': str(result)}]
            else:
                batch_results[event_id] = result
        
        return batch_results
    
    async def get_processor_metrics(self) -> Dict[str, Any]:
        """Get processor metrics"""
        handler_metrics = {}
        for name, handler in self.handlers.items():
            handler_metrics[name] = await handler.get_metrics()
        
        return {
            'processor_metrics': self.metrics,
            'handler_metrics': handler_metrics,
            'registered_handlers': list(self.handlers.keys()),
            'route_mappings': {cat.value: handlers for cat, handlers in self.routes.items()}
        }
    
    async def _update_processor_metrics(self, event: AnalyticsEvent, processing_time: float) -> None:
        """Update processor metrics"""
        self.metrics['total_events'] += 1
        self.metrics['total_processing_time'] += processing_time
        
        # Update category metrics
        category = event.category.value
        if category not in self.metrics['events_by_category']:
            self.metrics['events_by_category'][category] = 0
        self.metrics['events_by_category'][category] += 1
        
        # Update handler metrics
        handler_names = self.routes.get(event.category, [])
        for handler_name in handler_names:
            if handler_name not in self.metrics['events_by_handler']:
                self.metrics['events_by_handler'][handler_name] = 0
            self.metrics['events_by_handler'][handler_name] += 1


# Factory functions for common event types
def create_engagement_event(user_id: str, content_id: str, 
                          engagement_type: str, platform: str,
                          additional_data: Dict[str, Any] = None) -> AnalyticsEvent:
    """Create engagement analytics event"""
    data = {
        'user_id': user_id,
        'content_id': content_id,
        'engagement_type': engagement_type,
        'platform': platform
    }
    if additional_data:
        data.update(additional_data)
    
    return AnalyticsEvent(
        event_type='engagement',
        category=EventCategory.ENGAGEMENT,
        data=data
    )


def create_revenue_event(user_id: str, amount: float, currency: str,
                        transaction_type: str, platform: str,
                        additional_data: Dict[str, Any] = None) -> AnalyticsEvent:
    """Create revenue analytics event"""
    data = {
        'user_id': user_id,
        'amount': amount,
        'currency': currency,
        'transaction_type': transaction_type,
        'platform': platform
    }
    if additional_data:
        data.update(additional_data)
    
    return AnalyticsEvent(
        event_type='revenue',
        category=EventCategory.REVENUE,
        data=data
    )


def create_content_event(content_id: str, creator_id: str, 
                        content_type: str, platform: str,
                        additional_data: Dict[str, Any] = None) -> AnalyticsEvent:
    """Create content analytics event"""
    data = {
        'content_id': content_id,
        'creator_id': creator_id,
        'content_type': content_type,
        'platform': platform
    }
    if additional_data:
        data.update(additional_data)
    
    return AnalyticsEvent(
        event_type='content',
        category=EventCategory.CONTENT,
        data=data
    )


def create_protection_event(content_id: str, violation_type: str,
                          detected_platform: str, confidence_score: float,
                          additional_data: Dict[str, Any] = None) -> AnalyticsEvent:
    """Create protection analytics event"""
    data = {
        'content_id': content_id,
        'violation_type': violation_type,
        'detected_platform': detected_platform,
        'confidence_score': confidence_score
    }
    if additional_data:
        data.update(additional_data)
    
    return AnalyticsEvent(
        event_type='protection',
        category=EventCategory.PROTECTION,
        data=data,
        priority=EventPriority.HIGH
    )


# Global event processor instance
global_event_processor = EventProcessor()
