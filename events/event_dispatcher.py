"""🚀 Event Dispatcher System - IA Influencer Agent Platform
============================================================
Module: events/event_dispatcher.py
Author: Fahed Mlaiel (mlaiel@live.de)
============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INTELLIGENT EVENT DISPATCHER
Advanced event routing and distribution system
- Smart routing based on content and context
- Load balancing across handlers
- Circuit breaker for fault tolerance
- Priority-based dispatching
- Real-time monitoring and metrics
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict, deque

from .core.base_event import BaseEvent
from .core.event_priority import EventPriority
from .core.event_status import EventStatus
from .core.exceptions import EventProcessingError, EventStreamingError

logger = logging.getLogger(__name__)


class DispatchMode(Enum):
    """Event dispatch modes"""
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"
    PRIORITY_BASED = "priority_based"
    CONTENT_AWARE = "content_aware"
    GEOGRAPHIC = "geographic"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class HandlerStats:
    """Handler performance statistics"""
    handler_id: str
    total_processed: int = 0
    total_failed: int = 0
    avg_processing_time: float = 0.0
    last_processed: Optional[datetime] = None
    current_load: int = 0
    circuit_state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_processed == 0:
            return 1.0
        return (self.total_processed - self.total_failed) / self.total_processed
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate"""
        return 1.0 - self.success_rate


@dataclass
class DispatchRule:
    """Event dispatch routing rule"""
    rule_id: str
    event_patterns: List[str]
    handler_ids: List[str]
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def matches_event(self, event: BaseEvent) -> bool:
        """Check if rule matches event"""
        # Pattern matching
        for pattern in self.event_patterns:
            if pattern == "*" or pattern == event.event_type:
                return True
            if pattern.endswith("*") and event.event_type.startswith(pattern[:-1]):
                return True
        
        # Condition matching
        if self.conditions and event.data:
            for key, expected_value in self.conditions.items():
                if key not in event.data or event.data[key] != expected_value:
                    return False
        
        return False


@dataclass
class QueuedEvent:
    """Queued event for priority processing"""
    event: BaseEvent
    priority: int
    queued_at: datetime = field(default_factory=datetime.utcnow)
    attempts: int = 0
    
    def __lt__(self, other) -> None:
        """For priority queue ordering"""
        return self.priority > other.priority  # Higher priority first


class EventDispatcher:
    """Intelligent event dispatcher with advanced routing"""
    
    def __init__(self,
                 mode -> None: DispatchMode = DispatchMode.LOAD_BALANCED,
                 max_queue_size -> None: int = 10000,
                 max_retries -> None: int = 3,
                 circuit_failure_threshold -> None: int = 5,
                 circuit_timeout -> None: int = 60) -> None:
        """Initialize event dispatcher
        
        Args:
            mode: Dispatch mode strategy
            max_queue_size: Maximum queue size
            max_retries: Maximum retry attempts
            circuit_failure_threshold: Failures before circuit opens
            circuit_timeout: Circuit breaker timeout in seconds
        """
        self.mode = mode
        self.max_queue_size = max_queue_size
        self.max_retries = max_retries
        self.circuit_failure_threshold = circuit_failure_threshold
        self.circuit_timeout = circuit_timeout
        
        # Handler management
        self.handlers: Dict[str, Callable] = {}
        self.handler_stats: Dict[str, HandlerStats] = {}
        self.dispatch_rules: List[DispatchRule] = []
        
        # Queue management
        self.event_queue: List[QueuedEvent] = []  # Priority queue
        self.processing_events: Set[str] = set()
        
        # Round-robin state
        self.round_robin_index: Dict[str, int] = defaultdict(int)
        
        # Performance tracking
        self.total_dispatched = 0
        self.total_failed = 0
        self.start_time = datetime.utcnow()
        
        # Processing control
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        
        logger.info(f"Event dispatcher initialized - Mode: {mode.value}")
    
    async def start(self) -> None:
        """Start the event dispatcher"""
        if self._running:
            logger.warning("Event dispatcher already running")
            return
        
        self._running = True
        self._processor_task = asyncio.create_task(self._process_queue())
        
        logger.info("Event dispatcher started")
    
    async def stop(self) -> None:
        """Stop the event dispatcher"""
        self._running = False
        
        if self._processor_task:
            try:
                await asyncio.wait_for(self._processor_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._processor_task.cancel()
        
        logger.info("Event dispatcher stopped")
    
    def register_handler(self,
                        handler_id: str,
                        handler: Callable,
                        event_patterns: List[str],
                        conditions: Optional[Dict[str, Any]] = None,
                        priority: int = 0) -> str:
        """Register an event handler
        
        Args:
            handler_id: Unique handler identifier
            handler: Handler function
            event_patterns: Event patterns to handle
            conditions: Optional matching conditions
            priority: Handler priority
            
        Returns:
            Rule ID for the registration
        """
        if handler_id in self.handlers:
            logger.warning(f"Handler already registered: {handler_id}")
            return ""
        
        # Register handler
        self.handlers[handler_id] = handler
        self.handler_stats[handler_id] = HandlerStats(handler_id=handler_id)
        
        # Create dispatch rule
        rule = DispatchRule(
            rule_id=f"rule-{handler_id}",
            event_patterns=event_patterns,
            handler_ids=[handler_id],
            conditions=conditions or {},
            priority=priority
        )
        
        self.dispatch_rules.append(rule)
        self.dispatch_rules.sort(key=lambda r: r.priority, reverse=True)
        
        logger.info(f"Handler registered: {handler_id} for patterns: {event_patterns}")
        return rule.rule_id
    
    def unregister_handler(self, handler_id: str) -> bool:
        """Unregister an event handler
        
        Args:
            handler_id: Handler to remove
            
        Returns:
            True if handler was removed
        """
        if handler_id not in self.handlers:
            logger.warning(f"Handler not found: {handler_id}")
            return False
        
        # Remove handler
        del self.handlers[handler_id]
        del self.handler_stats[handler_id]
        
        # Remove from rules
        self.dispatch_rules = [
            rule for rule in self.dispatch_rules
            if handler_id not in rule.handler_ids
        ]
        
        logger.info(f"Handler unregistered: {handler_id}")
        return True
    
    async def dispatch(self, event: BaseEvent, priority: Optional[int] = None) -> bool:
        """Dispatch an event for processing
        
        Args:
            event: Event to dispatch
            priority: Optional priority override
            
        Returns:
            True if event was queued successfully
        """
        if len(self.event_queue) >= self.max_queue_size:
            logger.error("Event queue full, dropping event")
            return False
        
        # Determine priority
        event_priority = priority or self._calculate_priority(event)
        
        # Create queued event
        queued_event = QueuedEvent(
            event=event,
            priority=event_priority
        )
        
        # Add to priority queue
        heapq.heappush(self.event_queue, queued_event)
        
        logger.debug(f"Event queued: {event.event_id} (priority: {event_priority})")
        return True
    
    async def _process_queue(self) -> None:
        """Main queue processing loop"""
        logger.info("Event queue processing started")
        
        while self._running:
            try:
                if not self.event_queue:
                    await asyncio.sleep(0.1)
                    continue
                
                # Get highest priority event
                queued_event = heapq.heappop(self.event_queue)
                
                # Skip if already processing
                if queued_event.event.event_id in self.processing_events:
                    continue
                
                # Process event
                await self._process_event(queued_event)
                
            except Exception as e:
                logger.error(f"Error in queue processing: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_event(self, queued_event: QueuedEvent) -> None:
        """Process a single event"""
        event = queued_event.event
        self.processing_events.add(event.event_id)
        
        try:
            # Find matching handlers
            matching_handlers = self._find_matching_handlers(event)
            
            if not matching_handlers:
                logger.warning(f"No handlers found for event: {event.event_type}")
                return
            
            # Select handler based on dispatch mode
            selected_handler = self._select_handler(matching_handlers, event)
            
            if not selected_handler:
                logger.error(f"No available handler for event: {event.event_id}")
                return
            
            # Execute handler
            await self._execute_handler(event, selected_handler)
            
        except Exception as e:
            logger.error(f"Event processing failed: {event.event_id} - {e}")
            
            # Retry logic
            if queued_event.attempts < self.max_retries:
                queued_event.attempts += 1
                heapq.heappush(self.event_queue, queued_event)
                logger.info(f"Event requeued for retry: {event.event_id}")
            else:
                logger.error(f"Event failed after max retries: {event.event_id}")
                self.total_failed += 1
        
        finally:
            self.processing_events.discard(event.event_id)
    
    def _find_matching_handlers(self, event: BaseEvent) -> List[str]:
        """Find handlers that match the event"""
        matching_handlers = []
        
        for rule in self.dispatch_rules:
            if rule.active and rule.matches_event(event):
                matching_handlers.extend(rule.handler_ids)
        
        # Remove duplicates and filter available handlers
        matching_handlers = list(set(matching_handlers))
        matching_handlers = [
            h for h in matching_handlers 
            if h in self.handlers and self._is_handler_available(h)
        ]
        
        return matching_handlers
    
    def _select_handler(self, handlers: List[str], event: BaseEvent) -> Optional[str]:
        """Select best handler based on dispatch mode"""
        if not handlers:
            return None
        
        if self.mode == DispatchMode.ROUND_ROBIN:
            return self._select_round_robin(handlers, event.event_type)
        
        elif self.mode == DispatchMode.LOAD_BALANCED:
            return self._select_load_balanced(handlers)
        
        elif self.mode == DispatchMode.PRIORITY_BASED:
            return self._select_priority_based(handlers, event)
        
        elif self.mode == DispatchMode.CONTENT_AWARE:
            return self._select_content_aware(handlers, event)
        
        else:
            # Default to first available
            return handlers[0]
    
    def _select_round_robin(self, handlers: List[str], event_type: str) -> str:
        """Round-robin selection"""
        index = self.round_robin_index[event_type] % len(handlers)
        self.round_robin_index[event_type] += 1
        return handlers[index]
    
    def _select_load_balanced(self, handlers: List[str]) -> str:
        """Load-balanced selection (least loaded handler)"""
        return min(handlers, key=lambda h: self.handler_stats[h].current_load)
    
    def _select_priority_based(self, handlers: List[str], event: BaseEvent) -> str:
        """Priority-based selection"""
        # For now, use load balancing
        # Could be enhanced with handler priority metadata
        return self._select_load_balanced(handlers)
    
    def _select_content_aware(self, handlers: List[str], event: BaseEvent) -> str:
        """Content-aware selection"""
        # For now, use load balancing
        # Could be enhanced with content analysis
        return self._select_load_balanced(handlers)
    
    def _is_handler_available(self, handler_id: str) -> bool:
        """Check if handler is available"""
        stats = self.handler_stats.get(handler_id)
        if not stats:
            return False
        
        # Check circuit breaker
        if stats.circuit_state == CircuitState.OPEN:
            # Check if timeout period has passed
            if stats.last_failure:
                timeout_passed = (
                    datetime.utcnow() - stats.last_failure
                ).total_seconds() > self.circuit_timeout
                
                if timeout_passed:
                    stats.circuit_state = CircuitState.HALF_OPEN
                    stats.failure_count = 0
                    return True
                else:
                    return False
        
        return True
    
    async def _execute_handler(self, event: BaseEvent, handler_id: str) -> None:
        """Execute event handler"""
        handler = self.handlers[handler_id]
        stats = self.handler_stats[handler_id]
        
        start_time = time.time()
        stats.current_load += 1
        
        try:
            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                await asyncio.get_event_loop().run_in_executor(None, handler, event)
            
            # Update success stats
            processing_time = time.time() - start_time
            stats.total_processed += 1
            stats.last_processed = datetime.utcnow()
            
            # Update average processing time
            total = stats.total_processed
            current_avg = stats.avg_processing_time
            stats.avg_processing_time = (
                (current_avg * (total - 1) + processing_time) / total
            )
            
            # Reset circuit breaker on success
            if stats.circuit_state == CircuitState.HALF_OPEN:
                stats.circuit_state = CircuitState.CLOSED
                stats.failure_count = 0
            
            self.total_dispatched += 1
            
            logger.debug(f"Event processed successfully: {event.event_id} by {handler_id}")
            
        except Exception as e:
            # Update failure stats
            stats.total_failed += 1
            stats.failure_count += 1
            stats.last_failure = datetime.utcnow()
            
            # Check circuit breaker
            if stats.failure_count >= self.circuit_failure_threshold:
                stats.circuit_state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened for handler: {handler_id}")
            
            logger.error(f"Handler execution failed: {handler_id} - {e}")
            raise
        
        finally:
            stats.current_load -= 1
    
    def _calculate_priority(self, event: BaseEvent) -> int:
        """Calculate event priority"""
        # Base priority from event
        base_priority = 0
        if hasattr(event, 'priority'):
            base_priority = event.priority.value
        
        # Adjust based on event type
        if event.event_type.startswith("system."):
            base_priority += 100
        elif event.event_type.startswith("security."):
            base_priority += 90
        elif event.event_type.startswith("user."):
            base_priority += 50
        
        return base_priority
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dispatcher statistics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        handler_stats = {
            handler_id: {
                "total_processed": stats.total_processed,
                "total_failed": stats.total_failed,
                "success_rate": stats.success_rate,
                "avg_processing_time": stats.avg_processing_time,
                "current_load": stats.current_load,
                "circuit_state": stats.circuit_state.value,
                "last_processed": stats.last_processed.isoformat() if stats.last_processed else None
            }
            for handler_id, stats in self.handler_stats.items()
        }
        
        return {
            "mode": self.mode.value,
            "running": self._running,
            "uptime_seconds": uptime,
            "queue_size": len(self.event_queue),
            "processing_count": len(self.processing_events),
            "registered_handlers": len(self.handlers),
            "dispatch_rules": len(self.dispatch_rules),
            "total_dispatched": self.total_dispatched,
            "total_failed": self.total_failed,
            "success_rate": self.total_dispatched / max(self.total_dispatched + self.total_failed, 1),
            "events_per_second": self.total_dispatched / max(uptime, 1),
            "handler_statistics": handler_stats
        }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status information"""
        if not self.event_queue:
            return {
                "queue_size": 0,
                "priority_distribution": {},
                "oldest_event_age": 0
            }
        
        # Priority distribution
        priority_dist = defaultdict(int)
        oldest_time = None
        
        for queued_event in self.event_queue:
            priority_dist[queued_event.priority] += 1
            
            if oldest_time is None or queued_event.queued_at < oldest_time:
                oldest_time = queued_event.queued_at
        
        oldest_age = 0
        if oldest_time:
            oldest_age = (datetime.utcnow() - oldest_time).total_seconds()
        
        return {
            "queue_size": len(self.event_queue),
            "priority_distribution": dict(priority_dist),
            "oldest_event_age": oldest_age,
            "max_queue_size": self.max_queue_size,
            "queue_utilization": len(self.event_queue) / self.max_queue_size
        }


# Global dispatcher instance
_global_dispatcher: Optional[EventDispatcher] = None


def get_global_dispatcher() -> EventDispatcher:
    """Get or create global event dispatcher instance"""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = EventDispatcher()
    return _global_dispatcher


async def dispatch_event(event: BaseEvent, priority: Optional[int] = None) -> bool:
    """Convenience function to dispatch event globally"""
    dispatcher = get_global_dispatcher()
    return await dispatcher.dispatch(event, priority)


def register_handler(handler_id: str,
                    handler: Callable,
                    event_patterns: List[str],
                    **kwargs) -> str:
    """Convenience function to register handler globally"""
    dispatcher = get_global_dispatcher()
    return dispatcher.register_handler(handler_id, handler, event_patterns, **kwargs)