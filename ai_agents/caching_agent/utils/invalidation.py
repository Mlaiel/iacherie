"""Cache Invalidation Engine - Intelligent Cache Invalidation System

Advanced cache invalidation providing smart invalidation strategies,
event-driven triggers, and automated cleanup mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable, Pattern
from enum import Enum
import re
import json
import time
import uuid

logger = logging.getLogger(__name__)

class InvalidationTrigger(Enum):
    """
Types of invalidation triggers"""

    TTL_EXPIRED = "ttl_expired"
    MANUAL_REQUEST = "manual_request"
    TAG_BASED = "tag_based"
    PATTERN_BASED = "pattern_based"
    EVENT_DRIVEN = "event_driven"
    DEPENDENCY_CHANGED = "dependency_changed"
    CONTENT_UPDATED = "content_updated"
    USER_LOGOUT = "user_logout"
    SECURITY_BREACH = "security_breach"
    CACHE_COHERENCE = "cache_coherence"

class InvalidationPriority(Enum):
    """Priority levels for invalidation operations"""

    IMMEDIATE = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class InvalidationEvent:
    """
Invalidation event with comprehensive metadata"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger: InvalidationTrigger = InvalidationTrigger.MANUAL_REQUEST
    priority: InvalidationPriority = InvalidationPriority.NORMAL
    keys: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    affected_entries: int = 0

@dataclass
class InvalidationRule:
    """Configurable invalidation rule"""
    rule_id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    target_patterns: List[str] = field(default_factory=list)
    target_tags: List[str] = field(default_factory=list)
    priority: InvalidationPriority = InvalidationPriority.NORMAL
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = None
    execution_count: int = 0

class InvalidationStrategy(ABC):
    """
Abstract base class for invalidation strategies"""
    
    @abstractmethod
    async def should_invalidate(
        self, 
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """
Determine if invalidation should proceed"""
        pass
    
    @abstractmethod
    async def get_invalidation_candidates(
        self,
        event: InvalidationEvent,
        try:
                    # Request validation
                    if not event:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_invalidation_candidates_request(event)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
                    # Request validation
                    if not event:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_post_invalidation_actions_request(event)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler post_invalidation_actions failed: {e}")
                    return {"status": "error", "message": str(e)}
    async def post_invalidation_actions(
        self,
        event: InvalidationEvent,
        invalidated_keys: List[str]
    ):
        """
Actions to perform after invalidation"""
        pass

class TTLInvalidationStrategy(InvalidationStrategy):
    """
Time-To-Live based invalidation strategy"""
    
    async def should_invalidate(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """
Always proceed with TTL invalidation"""
        return True
    
    async def get_invalidation_candidates(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> List[str]:
        """
Find expired cache entries"""
        candidates = []
        current_time = datetime.utcnow()
        
        for key, entry in cache_entries.items():
            if hasattr(entry, 'ttl') and entry.ttl:
                expiry_time = entry.created_at + timedelta(seconds=entry.ttl)
                if current_time >= expiry_time:
                    candidates.append(key)
        
        return candidates
    
    async def post_invalidation_actions(
        self,
        event: InvalidationEvent,
        invalidated_keys: List[str]
    ):
        """
Log TTL-based invalidations"""
        if invalidated_keys:
            logger.info(f"TTL invalidation completed: {len(invalidated_keys)} entries expired")

class TagBasedInvalidation(InvalidationStrategy):
    """Tag-based cache invalidation strategy"""
    
    def __init__(self):
        self.tag_dependencies: Dict[str, Set[str]] = {}  # tag -> set of keys
        self.key_tags: Dict[str, Set[str]] = {}  # key -> set of tags
    
    def register_key_tags(self, key: str, tags: Set[str]):
        """
Register tags for a cache key"""
        self.key_tags[key] = tags
        
        for tag in tags:
            if tag not in self.tag_dependencies:
                self.tag_dependencies[tag] = set()
            self.tag_dependencies[tag].add(key)
    
    def unregister_key(self, key: str):
        """
Remove key from tag tracking"""
        if key in self.key_tags:
            for tag in self.key_tags[key]:
                if tag in self.tag_dependencies:
                    self.tag_dependencies[tag].discard(key)
            del self.key_tags[key]
    
    async def should_invalidate(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """
Proceed if we have tags to invalidate"""
        return bool(event.tags)
    
    async def get_invalidation_candidates(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> List[str]:
        """
Find cache entries matching specified tags"""
        candidates = set()
        
        for tag in event.tags:
            if tag in self.tag_dependencies:
                candidates.update(self.tag_dependencies[tag])
        
        # Filter to ensure keys still exist in cache
        return [key for key in candidates if key in cache_entries]
    
    async def post_invalidation_actions(
        self,
        event: InvalidationEvent,
        invalidated_keys: List[str]
    ):
        """
Clean up tag tracking for invalidated keys"""
        for key in invalidated_keys:
            self.unregister_key(key)
        
        logger.info(f"Tag-based invalidation completed: {len(invalidated_keys)} entries for tags {event.tags}")

class TimeBasedInvalidation(InvalidationStrategy):
    """Time-based invalidation with advanced scheduling"""
    
    def __init__(self):
        self.scheduled_invalidations: Dict[str, datetime] = {}
        self.recurring_schedules: Dict[str, Dict[str, Any]] = {}
    
    def schedule_invalidation(self, key: str, scheduled_time: datetime):
        """
Schedule a key for future invalidation"""
        self.scheduled_invalidations[key] = scheduled_time
    
    def schedule_recurring_invalidation(
        self,
        pattern: str,
        interval_seconds: int,
        start_time: Optional[datetime] = None
    ):
        """
Schedule recurring invalidation for key pattern"""
        schedule_id = f"recurring_{pattern}_{int(time.time())}"
        self.recurring_schedules[schedule_id] = {
            'pattern': pattern,
            'interval': interval_seconds,
            'start_time': start_time or datetime.utcnow(),
            'last_run': None
        }
    
    async def should_invalidate(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """Check if it's time for scheduled invalidations"""
        current_time = datetime.utcnow()
        
        # Check for due scheduled invalidations
        for key, scheduled_time in list(self.scheduled_invalidations.items()):
            if current_time >= scheduled_time:
                return True
        
        # Check recurring schedules
        for schedule_id, schedule in self.recurring_schedules.items():
            last_run = schedule.get('last_run', schedule['start_time'])
            next_run = last_run + timedelta(seconds=schedule['interval'])
            
            if current_time >= next_run:
                return True
        
        return False
    
    async def get_invalidation_candidates(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> List[str]:
        """
Get keys due for time-based invalidation"""
        candidates = []
        current_time = datetime.utcnow()
        
        # Process scheduled invalidations
        for key, scheduled_time in list(self.scheduled_invalidations.items()):
            if current_time >= scheduled_time and key in cache_entries:
                candidates.append(key)
                del self.scheduled_invalidations[key]
        
        # Process recurring schedules
        for schedule_id, schedule in self.recurring_schedules.items():
            last_run = schedule.get('last_run', schedule['start_time'])
            next_run = last_run + timedelta(seconds=schedule['interval'])
            
            if current_time >= next_run:
                pattern = schedule['pattern']
                regex = re.compile(pattern)
                
                for key in cache_entries.keys():
                    if regex.match(key):
                        candidates.append(key)
                
                # Update last run time
                schedule['last_run'] = current_time
        
        return candidates
    
    async def post_invalidation_actions(
        self,
        event: InvalidationEvent,
        invalidated_keys: List[str]
    ):
        """
Log time-based invalidations"""
        logger.info(f"Time-based invalidation completed: {len(invalidated_keys)} entries")

class EventDrivenInvalidation(InvalidationStrategy):
    """Event-driven invalidation based on application events"""
    
    def __init__(self):
        self.event_handlers: Dict[str, Callable] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}  # key -> dependent keys
        
    def register_event_handler(self, event_type: str, handler: Callable):
        """
Register handler for specific event type"""
        self.event_handlers[event_type] = handler
    
    def register_dependency(self, key: str, dependent_keys: Set[str]):
        """
Register cache dependencies"""
        self.dependency_graph[key] = dependent_keys
    
    async def should_invalidate(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> bool:
        """
Check if event should trigger invalidation"""
        event_type = event.metadata.get('event_type')
        return event_type in self.event_handlers
    
    async def get_invalidation_candidates(
        self,
        event: InvalidationEvent,
        cache_entries: Dict[str, Any]
    ) -> List[str]:
        """
Get candidates based on event and dependencies"""
        candidates = set()
        event_type = event.metadata.get('event_type')
        
        if event_type in self.event_handlers:
            handler = self.event_handlers[event_type]
            handler_candidates = await handler(event, cache_entries)
            candidates.update(handler_candidates)
        
        # Add dependent keys
        for key in list(candidates):
            if key in self.dependency_graph:
                candidates.update(self.dependency_graph[key])
        
        return [key for key in candidates if key in cache_entries]
    
    async def post_invalidation_actions(
        self,
        event: InvalidationEvent,
        invalidated_keys: List[str]
    ):
        """
Clean up dependencies for invalidated keys"""
        for key in invalidated_keys:
            if key in self.dependency_graph:
                del self.dependency_graph[key]
        
        logger.info(f"Event-driven invalidation completed: {len(invalidated_keys)} entries")

class InvalidationEngine:
    """
    Advanced cache invalidation engine orchestrating multiple strategies
    and providing comprehensive invalidation capabilities.
    """
    
    def __init__(self):
        self.strategies: Dict[InvalidationTrigger, InvalidationStrategy] = {
            InvalidationTrigger.TTL_EXPIRED: TTLInvalidationStrategy(),
            InvalidationTrigger.TAG_BASED: TagBasedInvalidation(),
            InvalidationTrigger.EVENT_DRIVEN: EventDrivenInvalidation()
        }
        
        self.rules: Dict[str, InvalidationRule] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.metrics = {
            'total_events': 0,
        try:
            logger.info(f"Executing shutdown")
            
            # Implementation for shutdown
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"shutdown completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"shutdown failed: {e}")
            raise
    async def initialize(self):
        """
Initialize invalidation engine"""
        self.processing_task = asyncio.create_task(self._process_invalidation_queue())
        logger.info("InvalidationEngine initialized")
    
    async def shutdown(self):
        """Graceful shutdown"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("InvalidationEngine shut down")
    
    def add_rule(self, rule: InvalidationRule):
        """Add invalidation rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added invalidation rule: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove invalidation rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed invalidation rule: {rule_id}")
    
    async def invalidate(
        self,
        trigger: InvalidationTrigger,
        keys: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        priority: InvalidationPriority = InvalidationPriority.NORMAL,
        **metadata
    ) -> InvalidationEvent:
        """Queue invalidation event"""
        event = InvalidationEvent(
            trigger=trigger,
            priority=priority,
            keys=keys or [],
            patterns=patterns or [],
            tags=tags or [],
            metadata=metadata
        )
        
        await self.event_queue.put(event)
        self.metrics['total_events'] += 1
        
        return event
    
    async def schedule_invalidation(self, key: str, delay_seconds: int):
        """
Schedule key for future invalidation"""
        scheduled_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        strategy = self.strategies.get(InvalidationTrigger.TTL_EXPIRED)
        if isinstance(strategy, TimeBasedInvalidation):
            strategy.schedule_invalidation(key, scheduled_time)
    
    async def cancel_invalidation(self, key: str):
        """
Cancel scheduled invalidation for key"""
        strategy = self.strategies.get(InvalidationTrigger.TTL_EXPIRED)
        if isinstance(strategy, TimeBasedInvalidation):
            strategy.scheduled_invalidations.pop(key, None)
    
    def register_cache_access_callback(self, callback: Callable):
        """
Register callback for cache access monitoring"""
        self.cache_access_callback = callback
    
    async def _process_invalidation_queue(self):
        """
Process invalidation events from queue"""
        while True:
            try:
                event = await self.event_queue.get()
                await self._process_invalidation_event(event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing invalidation event: {e}")
                await asyncio.sleep(1)
    
    async def _process_invalidation_event(self, event: InvalidationEvent):
        """Process single invalidation event"""
        start_time = time.time()
        
        try:
            # Get cache entries (would be provided by caching manager)
            cache_entries = {}
            if self.cache_access_callback:
                cache_entries = await self.cache_access_callback()
            
            # Get appropriate strategy
            strategy = self.strategies.get(event.trigger)
            if not strategy:
                logger.warning(f"No strategy found for trigger: {event.trigger}")
                return
            
            # Check if invalidation should proceed
            if not await strategy.should_invalidate(event, cache_entries):
                return
            
            # Get invalidation candidates
            candidates = await strategy.get_invalidation_candidates(event, cache_entries)
            
            # Add explicitly specified keys and pattern matches
            candidates.extend(event.keys)
            
            # Process patterns
            for pattern in event.patterns:
                regex = re.compile(pattern)
                pattern_matches = [key for key in cache_entries.keys() if regex.match(key)]
                candidates.extend(pattern_matches)
            
            # Remove duplicates
            candidates = list(set(candidates))
            
            # Perform actual invalidation (would be handled by caching manager)
            invalidated_keys = []
            if self.cache_access_callback:
                invalidated_keys = await self._perform_invalidation(candidates)
            
            # Post-invalidation actions
            await strategy.post_invalidation_actions(event, invalidated_keys)
            
            # Update event and metrics
            event.executed_at = datetime.utcnow()
            event.success = True
            event.affected_entries = len(invalidated_keys)
            
            self.metrics['successful_invalidations'] += 1
            self.metrics['keys_invalidated'] += len(invalidated_keys)
            
            processing_time = time.time() - start_time
            self._update_average_processing_time(processing_time)
            
        except Exception as e:
            event.error_message = str(e)
            event.success = False
            self.metrics['failed_invalidations'] += 1
            logger.error(f"Invalidation event failed: {e}")
    
    async def _perform_invalidation(self, keys: List[str]) -> List[str]:
        """Perform actual cache invalidation"""
        # This would integrate with the caching manager
        # For now, just return the keys as if they were invalidated
        return keys
    
    def _update_average_processing_time(self, processing_time: float):
        """
Update average processing time metric"""
        current_avg = self.metrics['average_processing_time']
        total_events = self.metrics['successful_invalidations'] + self.metrics['failed_invalidations']
        
        if total_events > 0:
            self.metrics['average_processing_time'] = (
                current_avg * (total_events - 1) + processing_time
            ) / total_events
    
    def get_metrics(self) -> Dict[str, Any]:
        """
Get invalidation engine metrics"""
        return self.metrics.copy()
    
    def get_queue_size(self) -> int:
        """
Get current invalidation queue size"""
        return self.event_queue.qsize()
