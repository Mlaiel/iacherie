"""MongoDB Event Processor
=======================

Advanced event processing system for MongoDB synchronization events
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from queue import Queue, PriorityQueue
import json
import time

from . import SyncEvent, SyncConfiguration, SyncStatus

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Event processing priorities."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0

class ProcessingStrategy(Enum):
    """Event processing strategies."""
    FIFO = "first_in_first_out"
    PRIORITY = "priority_based"
    BATCH = "batch_processing"
    REAL_TIME = "real_time"

@dataclass
class ProcessingRule:
    """Event processing rule."""
    rule_id: str
    name: str
    condition: Dict[str, Any]
    action: str
    priority: EventPriority
    enabled: bool = True

@dataclass
class ProcessingMetrics:
    """Event processing metrics."""
    total_events: int
    processed_events: int
    failed_events: int
    average_processing_time_ms: float
    events_per_second: float
    last_processed: Optional[datetime]

class EventProcessor:
    """Enterprise-grade MongoDB event processing system."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize event processor."""
        self.config = config or {}
        self.processing_rules: List[ProcessingRule] = []
        self.event_handlers: Dict[str, Callable] = {}
        self.processing_strategy = ProcessingStrategy.PRIORITY
        
        # Processing queues
        self.priority_queue = PriorityQueue(maxsize=50000)
        self.fifo_queue = Queue(maxsize=50000)
        self.batch_queue = Queue(maxsize=10000)
        self.dead_letter_queue = Queue(maxsize=1000)
        
        # Processing threads
        self.processing_threads = []
        self.batch_processing_thread = None
        self.metrics_thread = None
        self.shutdown_event = threading.Event()
        
        # Metrics
        self.metrics = ProcessingMetrics(
            total_events=0,
            processed_events=0,
            failed_events=0,
            average_processing_time_ms=0.0,
            events_per_second=0.0,
            last_processed=None
        )
        
        # Configuration
        self.max_processing_threads = self.config.get('max_threads', 10)
        self.batch_size = self.config.get('batch_size', 100)
        self.batch_timeout_seconds = self.config.get('batch_timeout', 5)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay_seconds = self.config.get('retry_delay', 1)
        
        # Initialize default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default processing rules."""
        # High priority for critical operations
        critical_rule = ProcessingRule(
            rule_id="critical_ops",
            name="Critical Operations",
            condition={"operation_type": {"$in": ["insert", "delete"]}},
            action="process_immediately",
            priority=EventPriority.CRITICAL
        )
        
        # Normal priority for updates
        update_rule = ProcessingRule(
            rule_id="update_ops",
            name="Update Operations",
            condition={"operation_type": "update"},
            action="process_normal",
            priority=EventPriority.NORMAL
        )
        
        # Low priority for metadata changes
        metadata_rule = ProcessingRule(
            rule_id="metadata_ops",
            name="Metadata Operations",
            condition={"collection": {"$regex": ".*metadata.*"}},
            action="process_batch",
            priority=EventPriority.LOW
        )
        
        self.processing_rules.extend([critical_rule, update_rule, metadata_rule])
    
    def add_processing_rule(self, rule -> None: ProcessingRule) -> None:
        """Add a new processing rule."""
        self.processing_rules.append(rule)
        logger.info(f"Added processing rule: {rule.name}")
    
    def register_handler(self, event_type -> None: str, handler -> None: Callable) -> None:
        """Register an event handler for a specific event type."""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
    
    def process_event(self, event: SyncEvent) -> bool:
        """Process a single synchronization event."""
        try:
            self.metrics.total_events += 1
            
            # Determine processing priority
            priority = self._determine_priority(event)
            
            # Apply processing rules
            action = self._apply_processing_rules(event)
            
            # Route to appropriate queue
            if self.processing_strategy == ProcessingStrategy.PRIORITY:
                self._queue_for_priority_processing(event, priority)
            elif self.processing_strategy == ProcessingStrategy.FIFO:
                self._queue_for_fifo_processing(event)
            elif self.processing_strategy == ProcessingStrategy.BATCH:
                self._queue_for_batch_processing(event)
            else:  # REAL_TIME
                return self._process_event_immediately(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            self._send_to_dead_letter_queue(event, str(e))
            return False
    
    def _determine_priority(self, event: SyncEvent) -> EventPriority:
        """Determine processing priority for an event."""
        # Critical operations
        if event.operation_type in ['delete', 'drop']:
            return EventPriority.CRITICAL
        
        # High priority for inserts and important collections
        if (event.operation_type == 'insert' or 
            'user' in event.collection.lower() or
            'payment' in event.collection.lower()):
            return EventPriority.HIGH
        
        # Normal priority for updates
        if event.operation_type == 'update':
            return EventPriority.NORMAL
        
        # Low priority for everything else
        return EventPriority.LOW
    
    def _apply_processing_rules(self, event: SyncEvent) -> str:
        """Apply processing rules to determine action."""
        event_dict = asdict(event)
        
        for rule in self.processing_rules:
            if not rule.enabled:
                continue
            
            if self._matches_condition(event_dict, rule.condition):
                logger.debug(f"Event {event.event_id} matched rule: {rule.name}")
                return rule.action
        
        return "process_normal"  # Default action
    
    def _matches_condition(self, event_dict: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Check if event matches a rule condition."""
        for field, criteria in condition.items():
            if field not in event_dict:
                return False
            
            value = event_dict[field]
            
            if isinstance(criteria, dict):
                # MongoDB-style operators
                for op, op_value in criteria.items():
                    if op == "$in":
                        if value not in op_value:
                            return False
                    elif op == "$regex":
                        import re
                        if not re.search(op_value, str(value)):
                            return False
                    elif op == "$eq":
                        if value != op_value:
                            return False
                    elif op == "$ne":
                        if value == op_value:
                            return False
            else:
                # Direct equality
                if value != criteria:
                    return False
        
        return True
    
    def _queue_for_priority_processing(self, event -> None: SyncEvent, priority -> None: EventPriority) -> None:
        """Queue event for priority-based processing."""
        try:
            priority_item = (priority.value, time.time(), event)
            self.priority_queue.put(priority_item, timeout=1)
        except:
            logger.warning(f"Priority queue full, sending event {event.event_id} to dead letter queue")
            self._send_to_dead_letter_queue(event, "Priority queue full")
    
    def _queue_for_fifo_processing(self, event -> None: SyncEvent) -> None:
        """Queue event for FIFO processing."""
        try:
            self.fifo_queue.put(event, timeout=1)
        except:
            logger.warning(f"FIFO queue full, sending event {event.event_id} to dead letter queue")
            self._send_to_dead_letter_queue(event, "FIFO queue full")
    
    def _queue_for_batch_processing(self, event -> None: SyncEvent) -> None:
        """Queue event for batch processing."""
        try:
            self.batch_queue.put(event, timeout=1)
        except:
            logger.warning(f"Batch queue full, sending event {event.event_id} to dead letter queue")
            self._send_to_dead_letter_queue(event, "Batch queue full")
    
    def _process_event_immediately(self, event: SyncEvent) -> bool:
        """Process event immediately."""
        start_time = time.time()
        
        try:
            # Get appropriate handler
            handler = self.event_handlers.get(
                event.operation_type,
                self.event_handlers.get('default', self._default_handler)
            )
            
            # Process the event
            result = handler(event)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            self._update_processing_metrics(processing_time, True)
            
            event.status = 'processed'
            logger.debug(f"Processed event {event.event_id} in {processing_time:.2f}ms")
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._update_processing_metrics(processing_time, False)
            
            event.status = 'error'
            event.error_message = str(e)
            
            logger.error(f"Failed to process event {event.event_id}: {e}")
            return False
    
    def _default_handler(self, event: SyncEvent) -> bool:
        """Default event handler."""
        logger.info(f"Processing event: {event.operation_type} on {event.collection}")
        return True
    
    def start_processing_threads(self, num_threads -> None: Optional[int] = None) -> None:
        """Start background processing threads."""
        if num_threads is None:
            num_threads = self.max_processing_threads
        
        # Start priority processing threads
        for i in range(num_threads):
            thread = threading.Thread(
                target=self._priority_processor,
                args=(f"priority_{i}",),
                daemon=True
            )
            thread.start()
            self.processing_threads.append(thread)
        
        # Start FIFO processing thread
        fifo_thread = threading.Thread(
            target=self._fifo_processor,
            args=("fifo_processor",),
            daemon=True
        )
        fifo_thread.start()
        self.processing_threads.append(fifo_thread)
        
        # Start batch processing thread
        self.batch_processing_thread = threading.Thread(
            target=self._batch_processor,
            args=("batch_processor",),
            daemon=True
        )
        self.batch_processing_thread.start()
        
        # Start metrics thread
        self.metrics_thread = threading.Thread(
            target=self._metrics_collector,
            args=("metrics_collector",),
            daemon=True
        )
        self.metrics_thread.start()
        
        logger.info(f"Started {num_threads + 2} processing threads")
    
    def _priority_processor(self, processor_name -> None: str) -> None:
        """Process events from priority queue."""
        logger.info(f"Priority processor started: {processor_name}")
        
        while not self.shutdown_event.is_set():
            try:
                # Get event from priority queue
                priority, timestamp, event = self.priority_queue.get(timeout=1)
                
                # Process the event
                self._process_event_immediately(event)
                
                # Mark task as done
                self.priority_queue.task_done()
                
            except:
                # Timeout or shutdown
                continue
        
        logger.info(f"Priority processor stopped: {processor_name}")
    
    def _fifo_processor(self, processor_name -> None: str) -> None:
        """Process events from FIFO queue."""
        logger.info(f"FIFO processor started: {processor_name}")
        
        while not self.shutdown_event.is_set():
            try:
                # Get event from FIFO queue
                event = self.fifo_queue.get(timeout=1)
                
                # Process the event
                self._process_event_immediately(event)
                
                # Mark task as done
                self.fifo_queue.task_done()
                
            except:
                # Timeout or shutdown
                continue
        
        logger.info(f"FIFO processor stopped: {processor_name}")
    
    def _batch_processor(self, processor_name -> None: str) -> None:
        """Process events in batches."""
        logger.info(f"Batch processor started: {processor_name}")
        
        batch = []
        last_batch_time = time.time()
        
        while not self.shutdown_event.is_set():
            try:
                # Get event from batch queue
                event = self.batch_queue.get(timeout=0.1)
                batch.append(event)
                
                # Process batch if it's full or timeout reached
                current_time = time.time()
                if (len(batch) >= self.batch_size or 
                    current_time - last_batch_time >= self.batch_timeout_seconds):
                    
                    self._process_event_batch(batch)
                    batch = []
                    last_batch_time = current_time
                
            except:
                # Timeout - check if we should process partial batch
                if batch and time.time() - last_batch_time >= self.batch_timeout_seconds:
                    self._process_event_batch(batch)
                    batch = []
                    last_batch_time = time.time()
        
        # Process remaining events
        if batch:
            self._process_event_batch(batch)
        
        logger.info(f"Batch processor stopped: {processor_name}")
    
    def _process_event_batch(self, events -> None: List[SyncEvent]) -> None:
        """Process a batch of events."""
        logger.info(f"Processing batch of {len(events)} events")
        
        start_time = time.time()
        successful = 0
        
        try:
            # Group events by operation type for efficient processing
            grouped_events = {}
            for event in events:
                op_type = event.operation_type
                if op_type not in grouped_events:
                    grouped_events[op_type] = []
                grouped_events[op_type].append(event)
            
            # Process each group
            for op_type, group_events in grouped_events.items():
                handler = self.event_handlers.get(
                    f"batch_{op_type}",
                    self.event_handlers.get('batch_default', self._default_batch_handler)
                )
                
                try:
                    result = handler(group_events)
                    if result:
                        successful += len(group_events)
                        for event in group_events:
                            event.status = 'processed'
                except Exception as e:
                    logger.error(f"Batch processing failed for {op_type}: {e}")
                    for event in group_events:
                        event.status = 'error'
                        event.error_message = str(e)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            avg_time_per_event = processing_time / len(events) if events else 0
            
            for _ in range(successful):
                self._update_processing_metrics(avg_time_per_event, True)
            
            for _ in range(len(events) - successful):
                self._update_processing_metrics(avg_time_per_event, False)
            
            logger.info(f"Batch processed: {successful}/{len(events)} successful in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            for event in events:
                event.status = 'error'
                event.error_message = str(e)
    
    def _default_batch_handler(self, events: List[SyncEvent]) -> bool:
        """Default batch event handler."""
        logger.info(f"Processing batch of {len(events)} events")
        return True
    
    def _metrics_collector(self, collector_name -> None: str) -> None:
        """Collect and update processing metrics."""
        logger.info(f"Metrics collector started: {collector_name}")
        
        last_processed_count = 0
        last_update_time = time.time()
        
        while not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                time_diff = current_time - last_update_time
                
                if time_diff >= 60:  # Update every minute
                    processed_diff = self.metrics.processed_events - last_processed_count
                    self.metrics.events_per_second = processed_diff / time_diff
                    
                    last_processed_count = self.metrics.processed_events
                    last_update_time = current_time
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                time.sleep(10)
        
        logger.info(f"Metrics collector stopped: {collector_name}")
    
    def _update_processing_metrics(self, processing_time_ms -> None: float, success -> None: bool) -> None:
        """Update processing metrics."""
        if success:
            self.metrics.processed_events += 1
            self.metrics.last_processed = datetime.now()
        else:
            self.metrics.failed_events += 1
        
        # Update average processing time
        total_successful = self.metrics.processed_events
        if total_successful > 0:
            current_avg = self.metrics.average_processing_time_ms
            self.metrics.average_processing_time_ms = (
                (current_avg * (total_successful - 1) + processing_time_ms) / total_successful
            )
    
    def _send_to_dead_letter_queue(self, event -> None: SyncEvent, reason -> None: str) -> None:
        """Send event to dead letter queue."""
        try:
            event.status = 'dead_letter'
            event.error_message = reason
            self.dead_letter_queue.put((event, reason), timeout=1)
            logger.warning(f"Event {event.event_id} sent to dead letter queue: {reason}")
        except:
            logger.error(f"Dead letter queue full, event {event.event_id} lost")
    
    def get_processing_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics."""
        return self.metrics
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get status of all processing queues."""
        return {
            'priority_queue_size': self.priority_queue.qsize(),
            'fifo_queue_size': self.fifo_queue.qsize(),
            'batch_queue_size': self.batch_queue.qsize(),
            'dead_letter_queue_size': self.dead_letter_queue.qsize(),
            'processing_threads': len(self.processing_threads),
            'processing_strategy': self.processing_strategy.value
        }
    
    def get_dead_letter_events(self, limit: int = 100) -> List[Tuple[SyncEvent, str]]:
        """Get events from dead letter queue."""
        events = []
        temp_events = []
        
        # Extract events up to limit
        for _ in range(min(limit, self.dead_letter_queue.qsize())):
            try:
                event_data = self.dead_letter_queue.get_nowait()
                events.append(event_data)
                temp_events.append(event_data)
            except:
                break
        
        # Put events back in queue
        for event_data in temp_events:
            try:
                self.dead_letter_queue.put_nowait(event_data)
            except:
                break
        
        return events
    
    def retry_dead_letter_event(self, event_id: str) -> bool:
        """Retry processing a dead letter event."""
        # Find and remove event from dead letter queue
        temp_events = []
        target_event = None
        
        while not self.dead_letter_queue.empty():
            try:
                event_data = self.dead_letter_queue.get_nowait()
                if event_data[0].event_id == event_id:
                    target_event = event_data[0]
                else:
                    temp_events.append(event_data)
            except:
                break
        
        # Put other events back
        for event_data in temp_events:
            try:
                self.dead_letter_queue.put_nowait(event_data)
            except:
                break
        
        # Retry target event
        if target_event:
            target_event.status = 'retry'
            target_event.error_message = None
            return self.process_event(target_event)
        
        return False
    
    def shutdown(self) -> None:
        """Shutdown event processor."""
        logger.info("Shutting down event processor")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for processing threads
        for thread in self.processing_threads:
            thread.join(timeout=5)
        
        if self.batch_processing_thread:
            self.batch_processing_thread.join(timeout=5)
        
        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)
        
        logger.info("Event processor shutdown complete")

# Export the main class
__all__ = ['EventProcessor', 'ProcessingRule', 'ProcessingMetrics', 'EventPriority']