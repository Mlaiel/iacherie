"""🚀 Dead Letter Queue System - IA Influencer Agent Platform
=============================================================
Module: events/dead_letter_queue.py
Author: Fahed Mlaiel (mlaiel@live.de)
=============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 DEAD LETTER QUEUE SYSTEM
Advanced failed event handling and recovery system
- Intelligent retry mechanisms with exponential backoff
- Event classification and automatic recovery
- Monitoring and alerting for failed events
- Manual intervention and reprocessing capabilities
- Performance optimization for high-volume scenarios
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict

from .core.base_event import BaseEvent
from .core.event_priority import EventPriority
from .core.event_status import EventStatus
from .core.exceptions import EventProcessingError

logger = logging.getLogger(__name__)


class FailureReason(Enum):
    """Categorized failure reasons"""
    HANDLER_ERROR = "handler_error"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    SERIALIZATION_ERROR = "serialization_error"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies for failed events"""
    RETRY = "retry"
    MANUAL_INTERVENTION = "manual_intervention"
    SKIP = "skip"
    TRANSFORM_AND_RETRY = "transform_and_retry"
    ROUTE_TO_ALTERNATIVE = "route_to_alternative"


@dataclass
class FailedEvent:
    """Failed event container with metadata"""
    event: BaseEvent
    failure_reason: FailureReason
    error_message: str
    failure_timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    original_handler_id: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other) -> None:
        """For priority queue ordering (earliest retry first)"""
        if self.next_retry_at is None:
            return False
        if other.next_retry_at is None:
            return True
        return self.next_retry_at < other.next_retry_at
    
    def should_retry(self) -> bool:
        """Check if event should be retried"""
        if self.recovery_strategy != RecoveryStrategy.RETRY:
            return False
        if self.retry_count >= self.max_retries:
            return False
        if self.next_retry_at and datetime.utcnow() < self.next_retry_at:
            return False
        return True
    
    def calculate_next_retry(self, base_delay: float = 1.0) -> datetime:
        """Calculate next retry time with exponential backoff"""
        delay = base_delay * (2 ** self.retry_count)
        # Add jitter to prevent thundering herd
        import random
        jitter = random.uniform(0.1, 0.3) * delay
        return datetime.utcnow() + timedelta(seconds=delay + jitter)


@dataclass
class DLQStatistics:
    """Dead letter queue statistics"""
    total_failed_events: int = 0
    events_by_reason: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    events_by_strategy: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    successful_retries: int = 0
    failed_retries: int = 0
    events_requiring_manual_intervention: int = 0
    oldest_event_age: Optional[float] = None
    average_retry_count: float = 0.0


class DeadLetterQueue:
    """Advanced dead letter queue for failed events"""
    
    def __init__(self,
                 max_queue_size -> None: int = 10000,
                 default_max_retries -> None: int = 3,
                 base_retry_delay -> None: float = 1.0,
                 enable_auto_recovery -> None: bool = True,
                 recovery_interval -> None: int = 60) -> None:
        """Initialize dead letter queue
        
        Args:
            max_queue_size: Maximum number of events to store
            default_max_retries: Default retry attempts
            base_retry_delay: Base delay between retries in seconds
            enable_auto_recovery: Enable automatic recovery processing
            recovery_interval: Recovery processing interval in seconds
        """
        self.max_queue_size = max_queue_size
        self.default_max_retries = default_max_retries
        self.base_retry_delay = base_retry_delay
        self.enable_auto_recovery = enable_auto_recovery
        self.recovery_interval = recovery_interval
        
        # Storage
        self.failed_events: Dict[str, FailedEvent] = {}
        self.retry_queue: List[FailedEvent] = []  # Priority queue
        self.manual_intervention_queue: List[FailedEvent] = []
        
        # Event handlers for retry
        self.retry_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.statistics = DLQStatistics()
        
        # Processing control
        self._running = False
        self._recovery_task: Optional[asyncio.Task] = None
        
        # Monitoring callbacks
        self.on_event_failed: Optional[Callable] = None
        self.on_retry_successful: Optional[Callable] = None
        self.on_retry_failed: Optional[Callable] = None
        self.on_manual_intervention_required: Optional[Callable] = None
        
        logger.info("Dead letter queue initialized")
    
    async def start(self) -> None:
        """Start the dead letter queue processing"""
        if self._running:
            logger.warning("Dead letter queue already running")
            return
        
        self._running = True
        
        if self.enable_auto_recovery:
            self._recovery_task = asyncio.create_task(self._recovery_loop())
        
        logger.info("Dead letter queue started")
    
    async def stop(self) -> None:
        """Stop the dead letter queue processing"""
        self._running = False
        
        if self._recovery_task:
            try:
                await asyncio.wait_for(self._recovery_task, timeout=5.0)
            except asyncio.TimeoutError:
                self._recovery_task.cancel()
        
        logger.info("Dead letter queue stopped")
    
    def add_failed_event(self,
                        event: BaseEvent,
                        error: Exception,
                        handler_id: Optional[str] = None,
                        failure_reason: Optional[FailureReason] = None,
                        max_retries: Optional[int] = None) -> str:
        """Add a failed event to the dead letter queue
        
        Args:
            event: Failed event
            error: Exception that caused the failure
            handler_id: ID of the handler that failed
            failure_reason: Categorized failure reason
            max_retries: Override max retries for this event
            
        Returns:
            Failed event ID
        """
        if len(self.failed_events) >= self.max_queue_size:
            logger.error("Dead letter queue is full, dropping oldest event")
            self._remove_oldest_event()
        
        # Classify failure reason if not provided
        if failure_reason is None:
            failure_reason = self._classify_failure(error)
        
        # Determine recovery strategy
        recovery_strategy = self._determine_recovery_strategy(failure_reason, error)
        
        # Create failed event
        failed_event = FailedEvent(
            event=event,
            failure_reason=failure_reason,
            error_message=str(error),
            failure_timestamp=datetime.utcnow(),
            max_retries=max_retries or self.default_max_retries,
            recovery_strategy=recovery_strategy,
            original_handler_id=handler_id
        )
        
        # Set next retry time if applicable
        if recovery_strategy == RecoveryStrategy.RETRY:
            failed_event.next_retry_at = failed_event.calculate_next_retry(self.base_retry_delay)
            heapq.heappush(self.retry_queue, failed_event)
        elif recovery_strategy == RecoveryStrategy.MANUAL_INTERVENTION:
            self.manual_intervention_queue.append(failed_event)
            self.statistics.events_requiring_manual_intervention += 1
        
        # Store failed event
        self.failed_events[event.event_id] = failed_event
        
        # Update statistics
        self._update_statistics(failed_event)
        
        # Trigger callback
        if self.on_event_failed:
            try:
                # Schedule callback execution for async functions
                if asyncio.iscoroutinefunction(self.on_event_failed):
                    asyncio.create_task(self.on_event_failed(failed_event))
                else:
                    self.on_event_failed(failed_event)
            except Exception as e:
                logger.error(f"Error in failed event callback: {e}")
        
        logger.warning(f"Event added to DLQ: {event.event_id} - {failure_reason.value}")
        return event.event_id
    
    async def retry_event(self, event_id: str, handler: Optional[Callable] = None) -> bool:
        """Manually retry a failed event
        
        Args:
            event_id: Event ID to retry
            handler: Optional handler override
            
        Returns:
            True if retry was successful
        """
        failed_event = self.failed_events.get(event_id)
        if not failed_event:
            logger.error(f"Failed event not found: {event_id}")
            return False
        
        # Use provided handler or lookup retry handler
        retry_handler = handler or self.retry_handlers.get(
            failed_event.original_handler_id or "default"
        )
        
        if not retry_handler:
            logger.error(f"No retry handler available for event: {event_id}")
            return False
        
        # Attempt retry
        success = await self._attempt_retry(failed_event, retry_handler)
        
        if success:
            # Remove from DLQ on success
            self._remove_failed_event(event_id)
            self.statistics.successful_retries += 1
            
            if self.on_retry_successful:
                try:
                    # Schedule callback execution for async functions
                    if asyncio.iscoroutinefunction(self.on_retry_successful):
                        asyncio.create_task(self.on_retry_successful(failed_event))
                    else:
                        self.on_retry_successful(failed_event)
                except Exception as e:
                    logger.error(f"Error in retry success callback: {e}")
        else:
            # Update retry count and schedule next retry
            failed_event.retry_count += 1
            self.statistics.failed_retries += 1
            
            if failed_event.should_retry():
                failed_event.next_retry_at = failed_event.calculate_next_retry(self.base_retry_delay)
                heapq.heappush(self.retry_queue, failed_event)
            else:
                # Move to manual intervention
                failed_event.recovery_strategy = RecoveryStrategy.MANUAL_INTERVENTION
                self.manual_intervention_queue.append(failed_event)
                self.statistics.events_requiring_manual_intervention += 1
            
            if self.on_retry_failed:
                try:
                    # Schedule callback execution for async functions
                    if asyncio.iscoroutinefunction(self.on_retry_failed):
                        asyncio.create_task(self.on_retry_failed(failed_event))
                    else:
                        self.on_retry_failed(failed_event)
                except Exception as e:
                    logger.error(f"Error in retry failed callback: {e}")
        
        return success
    
    def register_retry_handler(self, handler_id: str, handler: Callable) -> None:
        """Register a retry handler
        
        Args:
            handler_id: Handler identifier
            handler: Retry handler function
        """
        self.retry_handlers[handler_id] = handler
        logger.info(f"Retry handler registered: {handler_id}")
    
    def get_failed_event(self, event_id: str) -> Optional[FailedEvent]:
        """Get a failed event by ID
        
        Args:
            event_id: Event ID
            
        Returns:
            Failed event or None
        """
        return self.failed_events.get(event_id)
    
    def get_events_by_reason(self, reason: FailureReason) -> List[FailedEvent]:
        """Get events by failure reason
        
        Args:
            reason: Failure reason
            
        Returns:
            List of failed events
        """
        return [
            failed_event for failed_event in self.failed_events.values()
            if failed_event.failure_reason == reason
        ]
    
    def get_events_requiring_intervention(self) -> List[FailedEvent]:
        """Get events requiring manual intervention
        
        Returns:
            List of failed events needing manual intervention
        """
        return self.manual_intervention_queue.copy()
    
    def mark_for_manual_intervention(self, event_id: str, reason: str = "") -> bool:
        """Mark an event for manual intervention
        
        Args:
            event_id: Event ID
            reason: Reason for manual intervention
            
        Returns:
            True if marked successfully
        """
        failed_event = self.failed_events.get(event_id)
        if not failed_event:
            return False
        
        failed_event.recovery_strategy = RecoveryStrategy.MANUAL_INTERVENTION
        failed_event.metadata["intervention_reason"] = reason
        
        # Remove from retry queue if present
        self.retry_queue = [fe for fe in self.retry_queue if fe.event.event_id != event_id]
        heapq.heapify(self.retry_queue)
        
        # Add to manual intervention queue
        if failed_event not in self.manual_intervention_queue:
            self.manual_intervention_queue.append(failed_event)
            self.statistics.events_requiring_manual_intervention += 1
        
        if self.on_manual_intervention_required:
            try:
                asyncio.create_task(self.on_manual_intervention_required(failed_event))
            except Exception as e:
                logger.error(f"Error in manual intervention callback: {e}")
        
        logger.info(f"Event marked for manual intervention: {event_id}")
        return True
    
    def remove_event(self, event_id: str) -> bool:
        """Remove an event from the dead letter queue
        
        Args:
            event_id: Event ID to remove
            
        Returns:
            True if removed successfully
        """
        return self._remove_failed_event(event_id)
    
    async def _recovery_loop(self) -> None:
        """Main recovery processing loop"""
        logger.info("Dead letter queue recovery loop started")
        
        while self._running:
            try:
                await self._process_retry_queue()
                await asyncio.sleep(self.recovery_interval)
            except Exception as e:
                logger.error(f"Error in recovery loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _process_retry_queue(self) -> None:
        """Process events ready for retry"""
        current_time = datetime.utcnow()
        processed_count = 0
        
        while self.retry_queue and processed_count < 100:  # Process up to 100 per cycle
            # Peek at next event
            if self.retry_queue[0].next_retry_at and self.retry_queue[0].next_retry_at > current_time:
                break  # Not ready yet
            
            # Get next event to retry
            failed_event = heapq.heappop(self.retry_queue)
            
            # Find retry handler
            handler = self.retry_handlers.get(
                failed_event.original_handler_id or "default"
            )
            
            if handler:
                await self.retry_event(failed_event.event.event_id, handler)
            else:
                logger.warning(f"No retry handler for event: {failed_event.event.event_id}")
                # Move to manual intervention
                self.mark_for_manual_intervention(
                    failed_event.event.event_id,
                    "No retry handler available"
                )
            
            processed_count += 1
        
        if processed_count > 0:
            logger.info(f"Processed {processed_count} retry events")
    
    async def _attempt_retry(self, failed_event: FailedEvent, handler: Callable) -> bool:
        """Attempt to retry a failed event
        
        Args:
            failed_event: Failed event to retry
            handler: Handler to use for retry
            
        Returns:
            True if retry was successful
        """
        try:
            # Call the retry handler
            if asyncio.iscoroutinefunction(handler):
                await handler(failed_event.event)
            else:
                await asyncio.get_event_loop().run_in_executor(None, handler, failed_event.event)
            
            logger.info(f"Event retry successful: {failed_event.event.event_id}")
            return True
            
        except Exception as e:
            logger.warning(f"Event retry failed: {failed_event.event.event_id} - {e}")
            failed_event.error_message = str(e)
            return False
    
    def _classify_failure(self, error: Exception) -> FailureReason:
        """Classify failure reason based on exception type"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        if "timeout" in error_message:
            return FailureReason.TIMEOUT
        elif "validation" in error_message:
            return FailureReason.VALIDATION_ERROR
        elif "network" in error_message or "connection" in error_message:
            return FailureReason.NETWORK_ERROR
        elif "resource" in error_message or "unavailable" in error_message:
            return FailureReason.RESOURCE_UNAVAILABLE
        elif "business" in error_message or "rule" in error_message:
            return FailureReason.BUSINESS_RULE_VIOLATION
        elif "serialization" in error_message or "json" in error_message:
            return FailureReason.SERIALIZATION_ERROR
        elif error_type in ["ValueError", "TypeError", "AttributeError"]:
            return FailureReason.HANDLER_ERROR
        else:
            return FailureReason.UNKNOWN
    
    def _determine_recovery_strategy(self, reason: FailureReason, error: Exception) -> RecoveryStrategy:
        """Determine recovery strategy based on failure reason"""
        if reason in [FailureReason.TIMEOUT, FailureReason.NETWORK_ERROR, FailureReason.RESOURCE_UNAVAILABLE]:
            return RecoveryStrategy.RETRY
        elif reason in [FailureReason.VALIDATION_ERROR, FailureReason.BUSINESS_RULE_VIOLATION]:
            return RecoveryStrategy.MANUAL_INTERVENTION
        elif reason == FailureReason.SERIALIZATION_ERROR:
            return RecoveryStrategy.TRANSFORM_AND_RETRY
        else:
            return RecoveryStrategy.RETRY
    
    def _update_statistics(self, failed_event: FailedEvent) -> None:
        """Update DLQ statistics"""
        self.statistics.total_failed_events += 1
        self.statistics.events_by_reason[failed_event.failure_reason.value] += 1
        self.statistics.events_by_strategy[failed_event.recovery_strategy.value] += 1
        
        # Update oldest event age
        if self.failed_events:
            oldest_timestamp = min(fe.failure_timestamp for fe in self.failed_events.values())
            self.statistics.oldest_event_age = (datetime.utcnow() - oldest_timestamp).total_seconds()
        
        # Update average retry count
        total_retries = sum(fe.retry_count for fe in self.failed_events.values())
        self.statistics.average_retry_count = total_retries / len(self.failed_events)
    
    def _remove_failed_event(self, event_id: str) -> bool:
        """Remove a failed event from all queues"""
        if event_id not in self.failed_events:
            return False
        
        failed_event = self.failed_events[event_id]
        
        # Remove from main storage
        del self.failed_events[event_id]
        
        # Remove from retry queue
        self.retry_queue = [fe for fe in self.retry_queue if fe.event.event_id != event_id]
        heapq.heapify(self.retry_queue)
        
        # Remove from manual intervention queue
        self.manual_intervention_queue = [
            fe for fe in self.manual_intervention_queue if fe.event.event_id != event_id
        ]
        
        logger.info(f"Failed event removed: {event_id}")
        return True
    
    def _remove_oldest_event(self) -> None:
        """Remove oldest failed event to make space"""
        if not self.failed_events:
            return
        
        oldest_event_id = min(
            self.failed_events.keys(),
            key=lambda eid: self.failed_events[eid].failure_timestamp
        )
        
        self._remove_failed_event(oldest_event_id)
        logger.warning(f"Removed oldest failed event to make space: {oldest_event_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive DLQ statistics"""
        return {
            "queue_status": {
                "total_failed_events": len(self.failed_events),
                "retry_queue_size": len(self.retry_queue),
                "manual_intervention_queue_size": len(self.manual_intervention_queue),
                "max_queue_size": self.max_queue_size,
                "queue_utilization": len(self.failed_events) / self.max_queue_size
            },
            "failure_statistics": {
                "total_failed_events": self.statistics.total_failed_events,
                "events_by_reason": dict(self.statistics.events_by_reason),
                "events_by_strategy": dict(self.statistics.events_by_strategy),
                "successful_retries": self.statistics.successful_retries,
                "failed_retries": self.statistics.failed_retries,
                "events_requiring_manual_intervention": self.statistics.events_requiring_manual_intervention,
                "oldest_event_age": self.statistics.oldest_event_age,
                "average_retry_count": self.statistics.average_retry_count
            },
            "configuration": {
                "max_queue_size": self.max_queue_size,
                "default_max_retries": self.default_max_retries,
                "base_retry_delay": self.base_retry_delay,
                "enable_auto_recovery": self.enable_auto_recovery,
                "recovery_interval": self.recovery_interval
            }
        }


# Global DLQ instance
_global_dlq: Optional[DeadLetterQueue] = None


def get_global_dlq() -> DeadLetterQueue:
    """Get or create global dead letter queue instance"""
    global _global_dlq
    if _global_dlq is None:
        _global_dlq = DeadLetterQueue()
    return _global_dlq


async def add_failed_event(event: BaseEvent, error: Exception, **kwargs) -> str:
    """Convenience function to add failed event to global DLQ"""
    dlq = get_global_dlq()
    return dlq.add_failed_event(event, error, **kwargs)


def register_retry_handler(handler_id: str, handler: Callable) -> None:
    """Convenience function to register retry handler globally"""
    dlq = get_global_dlq()
    dlq.register_retry_handler(handler_id, handler)