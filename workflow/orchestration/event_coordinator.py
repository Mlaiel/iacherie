"""
🔥 EVENT COORDINATOR - ENTERPRISE EVENT-DRIVEN ARCHITECTURE
Ultra-fast event processing and coordination for Creator Economy
Performance Target: < 10ms event processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY CODE - TOUS DROITS RÉSERVÉS
Commercial use forbidden without written authorization
Reverse engineering strictly prohibited
"""

import asyncio
import json
import time
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
from uuid import uuid4
from weakref import WeakSet

import logging
from pydantic import BaseModel, Field


class EventType(Enum):
    """Creator Economy event types for comprehensive workflow coordination."""
    # Content lifecycle events
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_PROCESSED = "content_processed"
    CONTENT_APPROVED = "content_approved"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_MONETIZED = "content_monetized"
    
    # Creator workflow events
    CREATOR_REGISTERED = "creator_registered"
    CREATOR_VERIFIED = "creator_verified"
    CREATOR_COLLABORATION_REQUEST = "creator_collaboration_request"
    CREATOR_PAYOUT_PROCESSED = "creator_payout_processed"
    
    # System events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    SYSTEM_HEALTH_CHECK = "system_health_check"
    
    # Real-time events
    USER_ENGAGEMENT = "user_engagement"
    REVENUE_GENERATED = "revenue_generated"
    ANALYTICS_UPDATE = "analytics_update"
    
    # Error handling events
    ERROR_OCCURRED = "error_occurred"
    RETRY_TRIGGERED = "retry_triggered"
    RECOVERY_COMPLETED = "recovery_completed"


class EventPriority(Enum):
    """Event priority levels for Creator Economy optimization."""
    CRITICAL = 1       # Revenue-impacting events
    HIGH = 2          # Creator experience events
    NORMAL = 3        # Standard workflow events
    LOW = 4           # Analytics and monitoring
    BACKGROUND = 5    # System maintenance


@dataclass
class WorkflowEvent:
    """Enterprise event with Creator Economy metadata and performance tracking."""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = EventType.WORKFLOW_STARTED
    priority: EventPriority = EventPriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Creator Economy context
    creator_id: Optional[str] = None
    content_type: Optional[str] = None  # music, photo, blog, video
    workflow_stage: Optional[str] = None
    revenue_impact: bool = False
    
    # Temporal data
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Processing data
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Performance tracking
    processing_start: Optional[float] = None
    processing_end: Optional[float] = None
    handler_count: int = 0
    
    def __post_init__(self):
        """Post-initialization optimization for Creator Economy."""
        # Set expiration for non-critical events
        if self.expires_at is None and self.priority in [EventPriority.LOW, EventPriority.BACKGROUND]:
            self.expires_at = self.timestamp + timedelta(hours=1)
        
        # Revenue events are always critical
        if self.revenue_impact:
            self.priority = EventPriority.CRITICAL
    
    @property
    def processing_time(self) -> Optional[float]:
        """Calculate event processing time in milliseconds."""
        if self.processing_start and self.processing_end:
            return (self.processing_end - self.processing_start) * 1000
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if event has expired."""
        return self.expires_at is not None and datetime.now() > self.expires_at


class EventHandler:
    """Enterprise event handler with performance optimization."""
    
    def __init__(
        self,
        handler_id: str,
        handler_func: Callable,
        event_types: Set[EventType],
        priority: EventPriority = EventPriority.NORMAL,
        async_execution: bool = True,
        max_concurrent: int = 10
    ):
        self.handler_id = handler_id
        self.handler_func = handler_func
        self.event_types = event_types
        self.priority = priority
        self.async_execution = async_execution
        self.max_concurrent = max_concurrent
        
        # Performance metrics
        self.events_processed = 0
        self.total_processing_time = 0.0
        self.errors_count = 0
        self.current_concurrent = 0
        
        # Threading control
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._lock = threading.Lock()
    
    async def handle_event(self, event: WorkflowEvent) -> Any:
        """Handle event with comprehensive error handling and metrics."""
        async with self._semaphore:  # Concurrency control
            start_time = time.perf_counter()
            self.current_concurrent += 1
            
            try:
                # Execute handler function
                if self.async_execution and asyncio.iscoroutinefunction(self.handler_func):
                    result = await self.handler_func(event)
                else:
                    result = self.handler_func(event)
                
                # Update metrics
                processing_time = time.perf_counter() - start_time
                with self._lock:
                    self.events_processed += 1
                    self.total_processing_time += processing_time
                
                return result
                
            except Exception as e:
                with self._lock:
                    self.errors_count += 1
                logging.error(f"Event handler {self.handler_id} failed: {e}")
                raise
            
            finally:
                self.current_concurrent -= 1
    
    @property
    def average_processing_time(self) -> float:
        """Get average processing time in milliseconds."""
        with self._lock:
            if self.events_processed > 0:
                return (self.total_processing_time / self.events_processed) * 1000
            return 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive handler metrics."""
        with self._lock:
            return {
                'handler_id': self.handler_id,
                'events_processed': self.events_processed,
                'average_processing_time_ms': self.average_processing_time,
                'errors_count': self.errors_count,
                'current_concurrent': self.current_concurrent,
                'max_concurrent': self.max_concurrent
            }


class EventRouter:
    """High-performance event routing with Creator Economy optimization."""
    
    def __init__(self):
        self.routes = defaultdict(list)  # event_type -> [handlers]
        self.handler_registry = {}  # handler_id -> handler
        self.routing_metrics = {
            'routes_executed': 0,
            'total_routing_time': 0.0,
            'route_cache_hits': 0,
            'route_cache_misses': 0
        }
        
        # Performance optimization caches
        self._route_cache = {}  # event_type -> [handlers] (cached)
        self._creator_routes = defaultdict(list)  # creator-specific routes
        self._lock = threading.Lock()
    
    async def register_handler(self, handler: EventHandler):
        """Register event handler with route optimization."""
        start_time = time.perf_counter()
        
        with self._lock:
            self.handler_registry[handler.handler_id] = handler
            
            # Register for each event type
            for event_type in handler.event_types:
                self.routes[event_type].append(handler)
                # Sort by priority for optimal routing
                self.routes[event_type].sort(key=lambda h: h.priority.value)
            
            # Clear route cache for affected event types
            for event_type in handler.event_types:
                self._route_cache.pop(event_type, None)
        
        routing_time = time.perf_counter() - start_time
        logging.info(f"Handler {handler.handler_id} registered in {routing_time:.3f}s")
    
    async def unregister_handler(self, handler_id: str):
        """Unregister event handler with cleanup."""
        with self._lock:
            if handler_id not in self.handler_registry:
                return False
            
            handler = self.handler_registry[handler_id]
            
            # Remove from routes
            for event_type in handler.event_types:
                if event_type in self.routes:
                    self.routes[event_type] = [
                        h for h in self.routes[event_type] 
                        if h.handler_id != handler_id
                    ]
            
            # Clean up
            del self.handler_registry[handler_id]
            self._route_cache.clear()  # Full cache clear for simplicity
        
        return True
    
    async def route_event(self, event: WorkflowEvent) -> List[EventHandler]:
        """Ultra-fast event routing with caching optimization."""
        start_time = time.perf_counter()
        
        # Check cache first
        cache_key = (event.event_type, event.creator_id, event.content_type)
        
        with self._lock:
            if cache_key in self._route_cache:
                handlers = self._route_cache[cache_key]
                self.routing_metrics['route_cache_hits'] += 1
            else:
                # Build handler list
                handlers = []
                
                # Get base handlers for event type
                base_handlers = self.routes.get(event.event_type, [])
                handlers.extend(base_handlers)
                
                # Add creator-specific handlers
                if event.creator_id:
                    creator_handlers = self._creator_routes.get(event.creator_id, [])
                    handlers.extend(creator_handlers)
                
                # Filter by content type if applicable
                if event.content_type:
                    handlers = [
                        h for h in handlers 
                        if not hasattr(h, 'content_types') or 
                        event.content_type in getattr(h, 'content_types', set())
                    ]
                
                # Cache the result
                self._route_cache[cache_key] = handlers
                self.routing_metrics['route_cache_misses'] += 1
            
            # Update metrics
            routing_time = time.perf_counter() - start_time
            self.routing_metrics['routes_executed'] += 1
            self.routing_metrics['total_routing_time'] += routing_time
        
        return handlers
    
    async def register_creator_specific_handler(self, creator_id: str, handler: EventHandler):
        """Register handler specific to a creator for personalized workflows."""
        with self._lock:
            self._creator_routes[creator_id].append(handler)
            self.handler_registry[handler.handler_id] = handler
        
        logging.info(f"Creator-specific handler registered for {creator_id}")
    
    def get_routing_metrics(self) -> Dict[str, Any]:
        """Get comprehensive routing performance metrics."""
        with self._lock:
            metrics = self.routing_metrics.copy()
            if metrics['routes_executed'] > 0:
                metrics['average_routing_time_ms'] = (
                    metrics['total_routing_time'] / metrics['routes_executed']
                ) * 1000
            
            cache_total = metrics['route_cache_hits'] + metrics['route_cache_misses']
            if cache_total > 0:
                metrics['cache_hit_ratio'] = metrics['route_cache_hits'] / cache_total
            
            return metrics


class EnterpriseEventBus:
    """Ultra-high performance event bus optimized for Creator Economy."""
    
    def __init__(self, max_queue_size: int = 10000):
        self.max_queue_size = max_queue_size
        self.event_queue = asyncio.Queue(maxsize=max_queue_size)
        self.dead_letter_queue = deque(maxlen=1000)
        
        # Performance metrics
        self.events_published = 0
        self.events_processed = 0
        self.events_failed = 0
        self.total_processing_time = 0.0
        
        # Event history for replay functionality
        self.event_history = deque(maxlen=5000)
        self.event_subscriptions = defaultdict(set)
        
        # Processing control
        self.is_running = False
        self._processing_task = None
        self._lock = threading.Lock()
    
    async def start(self):
        """Start the enterprise event bus processing."""
        if self.is_running:
            return
        
        self.is_running = True
        self._processing_task = asyncio.create_task(self._process_events())
        logging.info("🚀 Enterprise Event Bus started")
    
    async def stop(self):
        """Graceful shutdown of event bus."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        logging.info("🛑 Enterprise Event Bus stopped")
    
    async def publish_event(self, event: WorkflowEvent) -> bool:
        """Ultra-fast event publishing with overflow protection."""
        # Check for expired events
        if event.is_expired:
            logging.warning(f"Dropping expired event {event.event_id}")
            return False
        
        try:
            # Non-blocking queue put with immediate feedback
            self.event_queue.put_nowait(event)
            
            with self._lock:
                self.events_published += 1
            
            # Add to history for replay
            self.event_history.append(event)
            
            return True
            
        except asyncio.QueueFull:
            # Move to dead letter queue
            self.dead_letter_queue.append({
                'event': event,
                'reason': 'queue_full',
                'timestamp': datetime.now()
            })
            logging.warning(f"Event queue full, moved to dead letter: {event.event_id}")
            return False
    
    async def _process_events(self):
        """Main event processing loop with performance optimization."""
        while self.is_running:
            try:
                # Get event with timeout for responsiveness
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=0.1
                )
                
                # Process event with timing
                start_time = time.perf_counter()
                event.processing_start = start_time
                
                try:
                    await self._handle_single_event(event)
                    
                    event.processing_end = time.perf_counter()
                    processing_time = event.processing_end - start_time
                    
                    with self._lock:
                        self.events_processed += 1
                        self.total_processing_time += processing_time
                    
                    # Performance alert for slow events
                    if processing_time > 0.01:  # 10ms threshold
                        logging.warning(
                            f"Slow event processing: {event.event_id} took {processing_time*1000:.1f}ms"
                        )
                
                except Exception as e:
                    with self._lock:
                        self.events_failed += 1
                    
                    # Retry logic
                    if event.retry_count < event.max_retries:
                        event.retry_count += 1
                        await self.publish_event(event)
                        logging.info(f"Retrying event {event.event_id} (attempt {event.retry_count})")
                    else:
                        # Move to dead letter queue
                        self.dead_letter_queue.append({
                            'event': event,
                            'reason': f'max_retries_exceeded: {str(e)}',
                            'timestamp': datetime.now()
                        })
                        logging.error(f"Event {event.event_id} failed after max retries: {e}")
                
            except asyncio.TimeoutError:
                # No events to process, continue loop
                continue
            except Exception as e:
                logging.error(f"Event bus processing error: {e}")
                await asyncio.sleep(0.1)  # Brief pause on error
    
    async def _handle_single_event(self, event: WorkflowEvent):
        """Handle single event with Creator Economy optimization."""
        # Notify subscribers
        subscribers = self.event_subscriptions.get(event.event_type, set())
        
        if subscribers:
            # Execute all subscribers concurrently for performance
            tasks = [
                subscriber(event) for subscriber in subscribers
                if asyncio.iscoroutinefunction(subscriber)
            ]
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        event.handler_count = len(subscribers)
    
    async def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to events with automatic cleanup."""
        self.event_subscriptions[event_type].add(handler)
        logging.info(f"Handler subscribed to {event_type}")
    
    async def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from events."""
        self.event_subscriptions[event_type].discard(handler)
    
    async def replay_events(
        self, 
        event_type: Optional[EventType] = None,
        since: Optional[datetime] = None,
        creator_id: Optional[str] = None
    ) -> List[WorkflowEvent]:
        """Replay events for recovery or analysis."""
        filtered_events = []
        
        for event in self.event_history:
            # Apply filters
            if event_type and event.event_type != event_type:
                continue
            if since and event.timestamp < since:
                continue
            if creator_id and event.creator_id != creator_id:
                continue
            
            filtered_events.append(event)
        
        return filtered_events
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive event bus metrics."""
        with self._lock:
            queue_size = self.event_queue.qsize()
            avg_processing_time = (
                self.total_processing_time / max(1, self.events_processed)
            ) * 1000  # Convert to ms
            
            return {
                'events_published': self.events_published,
                'events_processed': self.events_processed,
                'events_failed': self.events_failed,
                'current_queue_size': queue_size,
                'dead_letter_count': len(self.dead_letter_queue),
                'average_processing_time_ms': avg_processing_time,
                'processing_rate': self.events_processed / max(1, self.total_processing_time),
                'failure_rate': self.events_failed / max(1, self.events_published)
            }


class EventCoordinator:
    """
    🔥 ENTERPRISE EVENT COORDINATOR - CREATOR ECONOMY OPTIMIZED
    Ultra-high performance event coordination with <10ms processing
    """
    
    def __init__(self, max_queue_size: int = 10000):
        self.event_bus = EnterpriseEventBus(max_queue_size)
        self.event_router = EventRouter()
        self.handler_registry = {}
        
        # Creator Economy optimization
        self.creator_event_patterns = {}
        self.content_type_handlers = defaultdict(list)
        self.revenue_event_handlers = []
        
        # Performance monitoring
        self.coordination_metrics = {
            'events_coordinated': 0,
            'total_coordination_time': 0.0,
            'routing_optimizations': 0,
            'dead_letter_recoveries': 0
        }
        
        # Real-time monitoring
        self.real_time_monitors = set()
        self._monitoring_task = None
    
    async def start(self):
        """Start the enterprise event coordinator."""
        await self.event_bus.start()
        self._monitoring_task = asyncio.create_task(self._real_time_monitoring())
        logging.info("🚀 Enterprise Event Coordinator started - Creator Economy optimized")
    
    async def stop(self):
        """Graceful shutdown of event coordinator."""
        await self.event_bus.stop()
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logging.info("🛑 Enterprise Event Coordinator stopped")
    
    async def coordinate_workflow_events(
        self, 
        event: WorkflowEvent,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Coordinate workflow events with Creator Economy optimization.
        Performance Target: < 10ms event processing
        """
        start_time = time.perf_counter()
        
        # Set correlation ID for event chain tracking
        if correlation_id:
            event.correlation_id = correlation_id
        
        # Creator Economy specific optimizations
        await self._optimize_event_for_creator_economy(event)
        
        # Route event to appropriate handlers
        handlers = await self.event_router.route_event(event)
        
        # Execute handlers concurrently for performance
        if handlers:
            tasks = [
                handler.handle_event(event) for handler in handlers
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log any handler errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"Handler {handlers[i].handler_id} failed: {result}")
        
        # Publish to event bus for subscribers
        await self.event_bus.publish_event(event)
        
        # Performance tracking
        coordination_time = time.perf_counter() - start_time
        self.coordination_metrics['events_coordinated'] += 1
        self.coordination_metrics['total_coordination_time'] += coordination_time
        
        if coordination_time > 0.01:  # 10ms threshold
            logging.warning(f"Event coordination exceeded 10ms: {coordination_time*1000:.1f}ms")
        
        return event.event_id
    
    async def _optimize_event_for_creator_economy(self, event: WorkflowEvent):
        """Apply Creator Economy specific optimizations to events."""
        # Revenue events get highest priority
        if event.revenue_impact:
            event.priority = EventPriority.CRITICAL
        
        # Content type specific optimizations
        if event.content_type == "music" and event.event_type == EventType.CONTENT_UPLOADED:
            # Music uploads need faster processing for time-sensitive releases
            event.priority = min(event.priority, EventPriority.HIGH)
        
        # Creator pattern recognition
        if event.creator_id in self.creator_event_patterns:
            pattern = self.creator_event_patterns[event.creator_id]
            if pattern.get('premium_processing'):
                event.priority = min(event.priority, EventPriority.HIGH)
    
    async def route_events_efficiently(self, events: List[WorkflowEvent]) -> Dict[str, List[str]]:
        """Batch event routing for high-throughput scenarios."""
        routing_results = {}
        
        # Group events by type for batch processing
        events_by_type = defaultdict(list)
        for event in events:
            events_by_type[event.event_type].append(event)
        
        # Process each group
        for event_type, event_group in events_by_type.items():
            event_ids = []
            for event in event_group:
                event_id = await self.coordinate_workflow_events(event)
                event_ids.append(event_id)
            routing_results[event_type.value] = event_ids
        
        return routing_results
    
    async def manage_event_subscriptions(
        self, 
        handler_id: str,
        event_types: List[EventType],
        handler_func: Callable,
        creator_specific: bool = False,
        creator_id: Optional[str] = None
    ) -> bool:
        """Manage event subscriptions with Creator Economy optimization."""
        try:
            # Create handler
            handler = EventHandler(
                handler_id=handler_id,
                handler_func=handler_func,
                event_types=set(event_types)
            )
            
            # Register with router
            if creator_specific and creator_id:
                await self.event_router.register_creator_specific_handler(creator_id, handler)
            else:
                await self.event_router.register_handler(handler)
            
            # Subscribe to event bus
            for event_type in event_types:
                await self.event_bus.subscribe(event_type, handler_func)
            
            self.handler_registry[handler_id] = handler
            return True
            
        except Exception as e:
            logging.error(f"Failed to manage subscription for {handler_id}: {e}")
            return False
    
    async def implement_event_replay(
        self,
        replay_config: Dict[str, Any]
    ) -> List[WorkflowEvent]:
        """Implement intelligent event replay for recovery scenarios."""
        events = await self.event_bus.replay_events(
            event_type=replay_config.get('event_type'),
            since=replay_config.get('since'),
            creator_id=replay_config.get('creator_id')
        )
        
        # Re-process events
        for event in events:
            event.retry_count = 0  # Reset retry count
            await self.coordinate_workflow_events(event)
        
        return events
    
    async def handle_event_ordering(
        self, 
        events: List[WorkflowEvent],
        ordering_strategy: str = "timestamp"
    ) -> List[WorkflowEvent]:
        """Handle event ordering for workflow consistency."""
        if ordering_strategy == "timestamp":
            return sorted(events, key=lambda e: e.timestamp)
        elif ordering_strategy == "priority":
            return sorted(events, key=lambda e: (e.priority.value, e.timestamp))
        elif ordering_strategy == "creator_workflow":
            # Group by creator and workflow stage
            return sorted(events, key=lambda e: (e.creator_id, e.workflow_stage, e.timestamp))
        
        return events
    
    async def event_dead_letter_handling(self) -> Dict[str, Any]:
        """Handle dead letter events with recovery strategies."""
        dead_letters = list(self.event_bus.dead_letter_queue)
        recovery_stats = {
            'total_dead_letters': len(dead_letters),
            'recovered_events': 0,
            'unrecoverable_events': 0
        }
        
        for dead_letter in dead_letters:
            event = dead_letter['event']
            reason = dead_letter['reason']
            
            # Attempt recovery based on reason
            if reason == 'queue_full':
                # Retry with higher priority
                event.priority = EventPriority.CRITICAL
                success = await self.event_bus.publish_event(event)
                if success:
                    recovery_stats['recovered_events'] += 1
                    self.coordination_metrics['dead_letter_recoveries'] += 1
                else:
                    recovery_stats['unrecoverable_events'] += 1
            else:
                recovery_stats['unrecoverable_events'] += 1
        
        return recovery_stats
    
    async def real_time_event_monitoring(self) -> Dict[str, Any]:
        """Real-time event monitoring with Creator Economy insights."""
        bus_metrics = self.event_bus.get_performance_metrics()
        routing_metrics = self.event_router.get_routing_metrics()
        
        # Calculate coordination performance
        avg_coordination_time = 0.0
        if self.coordination_metrics['events_coordinated'] > 0:
            avg_coordination_time = (
                self.coordination_metrics['total_coordination_time'] / 
                self.coordination_metrics['events_coordinated']
            ) * 1000  # Convert to ms
        
        return {
            'event_bus_metrics': bus_metrics,
            'routing_metrics': routing_metrics,
            'coordination_metrics': {
                **self.coordination_metrics,
                'average_coordination_time_ms': avg_coordination_time
            },
            'active_handlers': len(self.handler_registry),
            'creator_patterns': len(self.creator_event_patterns)
        }
    
    async def _real_time_monitoring(self):
        """Background task for real-time monitoring and optimization."""
        while True:
            try:
                metrics = await self.real_time_event_monitoring()
                
                # Performance alerts
                if metrics['coordination_metrics']['average_coordination_time_ms'] > 10:
                    logging.warning("Event coordination performance degraded")
                
                if metrics['event_bus_metrics']['current_queue_size'] > 1000:
                    logging.warning("High event queue size detected")
                
                # Optimization opportunities
                if metrics['routing_metrics'].get('cache_hit_ratio', 0) < 0.8:
                    logging.info("Route cache optimization opportunity detected")
                    self.coordination_metrics['routing_optimizations'] += 1
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logging.error(f"Monitoring task error: {e}")
                await asyncio.sleep(60)  # Longer delay on error


# Enterprise factory function
async def create_enterprise_event_coordinator(
    max_queue_size: int = 10000,
    creator_patterns: Optional[Dict[str, Dict]] = None
) -> EventCoordinator:
    """Factory function for enterprise event coordinator with Creator Economy optimization."""
    coordinator = EventCoordinator(max_queue_size)
    
    if creator_patterns:
        coordinator.creator_event_patterns.update(creator_patterns)
    
    await coordinator.start()
    return coordinator