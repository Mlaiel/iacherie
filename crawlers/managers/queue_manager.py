"""Queue Management Manager
=======================

Advanced queue management system for crawler operations with priority handling,
load balancing, retry logic, and distributed processing capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import json
import logging
import time
import uuid
import pickle
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import heapq
import threading
from collections import defaultdict, deque
import weakref

from ..config.queue_config import QueueConfig
from ..utils.serialization import TaskSerializer
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...monitoring.metrics_collector import MetricsCollector


class TaskPriority(Enum):
    """
Task priority levels for queue management."""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """
Task execution status."""

    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class QueueType(Enum):
    """Queue type enumeration."""

    PRIORITY = "priority"
    FIFO = "fifo"
    LIFO = "lifo"
    DELAY = "delay"
    SCHEDULED = "scheduled"
    ROUND_ROBIN = "round_robin"


@dataclass
class CrawlerTask:
    """Crawler task definition."""
    task_id: str
    task_type: str
    url: str
    priority: TaskPriority
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    callback: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 30
    delay: int = 0
    scheduled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueueMetrics:
    """
Queue performance metrics."""
    queue_name: str
    total_tasks: int = 0
    pending_tasks: int = 0
    processing_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    average_wait_time: float = 0.0
    throughput_per_minute: float = 0.0
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkerMetrics:
    """
Worker performance metrics."""
    worker_id: str
    tasks_processed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_task_time: float = 0.0
    last_active: datetime = field(default_factory=datetime.utcnow)
    status: str = "idle"


class TaskQueue:
    """
    Advanced task queue implementation with priority and scheduling support.
    """
    
    def __init__(self, name: str, queue_type: QueueType = QueueType.PRIORITY):
        """
Initialize task queue."""
        self.name = name
        self.queue_type = queue_type
        self.logger = get_logger(f"Queue-{name}")
        
        # Queue storage
        self._priority_queue: List[Tuple[int, float, CrawlerTask]] = []
        self._fifo_queue: deque = deque()
        self._scheduled_tasks: Dict[str, CrawlerTask] = {}
        self._processing_tasks: Dict[str, CrawlerTask] = {}
        
        # Queue state
        self._lock = asyncio.Lock()
        self._task_counter = 0
        self._paused = False
        
        # Metrics
        self.metrics = QueueMetrics(queue_name=name)
        self._processing_times: deque = deque(maxlen=1000)
        self._wait_times: deque = deque(maxlen=1000)
        
    async def put(self, task: CrawlerTask) -> bool:
        """Add task to queue."""
        async with self._lock:
            try:
                if self._paused:
                    self.logger.warning(f"Queue {self.name} is paused, rejecting task: {task.task_id}")
                    return False
                    
                # Handle scheduled tasks
                if task.scheduled_at and task.scheduled_at > datetime.utcnow():
                    self._scheduled_tasks[task.task_id] = task
                    task.status = TaskStatus.QUEUED
                    self.logger.info(f"Task {task.task_id} scheduled for {task.scheduled_at}")
                    return True
                    
                # Add to appropriate queue
                if self.queue_type == QueueType.PRIORITY:
                    priority = task.priority.value
                    timestamp = time.time()
                    heapq.heappush(self._priority_queue, (priority, timestamp, task))
                    
                elif self.queue_type in [QueueType.FIFO, QueueType.ROUND_ROBIN]:
                    self._fifo_queue.append(task)
                    
                elif self.queue_type == QueueType.LIFO:
                    self._fifo_queue.appendleft(task)
                    
                task.status = TaskStatus.QUEUED
                self.metrics.total_tasks += 1
                self.metrics.pending_tasks += 1
                
                self.logger.debug(f"Task {task.task_id} added to queue {self.name}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to add task to queue: {e}")
                return False
                
    async def get(self, timeout: Optional[float] = None) -> Optional[CrawlerTask]:
        """Get next task from queue."""
        start_time = time.time()
        
        while True:
            async with self._lock:
                if self._paused:
                    await asyncio.sleep(0.1)
                    continue
                    
                # Check scheduled tasks first
                await self._process_scheduled_tasks()
                
                # Get next task based on queue type
                task = None
                
                if self.queue_type == QueueType.PRIORITY and self._priority_queue:
                    _, _, task = heapq.heappop(self._priority_queue)
                    
                elif self.queue_type in [QueueType.FIFO, QueueType.ROUND_ROBIN] and self._fifo_queue:
                    task = self._fifo_queue.popleft()
                    
                elif self.queue_type == QueueType.LIFO and self._fifo_queue:
                    task = self._fifo_queue.pop()
                    
                if task:
                    # Move to processing
                    task.status = TaskStatus.PROCESSING
                    task.started_at = datetime.utcnow()
                    self._processing_tasks[task.task_id] = task
                    
                    # Update metrics
                    self.metrics.pending_tasks -= 1
                    self.metrics.processing_tasks += 1
                    
                    wait_time = time.time() - start_time
                    self._wait_times.append(wait_time)
                    
                    return task
                    
                # Check timeout
                if timeout and (time.time() - start_time) >= timeout:
                    return None
                    
            # Wait before next attempt
            await asyncio.sleep(0.01)
            
    async def _process_scheduled_tasks(self):
        """
Move scheduled tasks to main queue if ready."""
        current_time = datetime.utcnow()
        ready_tasks = []
        
        for task_id, task in self._scheduled_tasks.items():
            if task.scheduled_at and task.scheduled_at <= current_time:
                ready_tasks.append(task_id)
                
        for task_id in ready_tasks:
            task = self._scheduled_tasks.pop(task_id)
            
            # Add to main queue
            if self.queue_type == QueueType.PRIORITY:
                priority = task.priority.value
                timestamp = time.time()
                heapq.heappush(self._priority_queue, (priority, timestamp, task))
            else:
                self._fifo_queue.append(task)
                
            self.metrics.pending_tasks += 1
            
    async def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
Mark task as completed."""
        async with self._lock:
            if task_id not in self._processing_tasks:
                return False
                
            task = self._processing_tasks.pop(task_id)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            
            # Update metrics
            self.metrics.processing_tasks -= 1
            self.metrics.completed_tasks += 1
            
            # Calculate processing time
            if task.started_at:
                processing_time = (task.completed_at - task.started_at).total_seconds()
                self._processing_times.append(processing_time)
                
            self.logger.debug(f"Task {task_id} completed successfully")
            return True
            
    async def fail_task(self, task_id: str, error: str, retry: bool = True) -> bool:
        """Mark task as failed and optionally retry."""
        async with self._lock:
            if task_id not in self._processing_tasks:
                return False
                
            task = self._processing_tasks.pop(task_id)
            task.error_message = error
            
            # Check if should retry
            if retry and task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                
                # Re-queue with delay
                delay = min(task.retry_count * 2, 60)  # Exponential backoff
                task.scheduled_at = datetime.utcnow() + timedelta(seconds=delay)
                self._scheduled_tasks[task.task_id] = task
                
                self.logger.info(f"Task {task_id} retry {task.retry_count}/{task.max_retries} scheduled in {delay}s")
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                self.metrics.failed_tasks += 1
                
                self.logger.warning(f"Task {task_id} failed permanently: {error}")
                
            self.metrics.processing_tasks -= 1
            return True
            
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        async with self._lock:
            # Check processing tasks
            if task_id in self._processing_tasks:
                task = self._processing_tasks.pop(task_id)
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                self.metrics.processing_tasks -= 1
                return True
                
            # Check scheduled tasks
            if task_id in self._scheduled_tasks:
                task = self._scheduled_tasks.pop(task_id)
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                return True
                
            # Check queued tasks
            for i, (_, _, task) in enumerate(self._priority_queue):
                if task.task_id == task_id:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.utcnow()
                    self._priority_queue.pop(i)
                    heapq.heapify(self._priority_queue)
                    self.metrics.pending_tasks -= 1
                    return True
                    
            return False
            
    async def pause(self):
        """
Pause queue processing."""
        self._paused = True
        self.logger.info(f"Queue {self.name} paused")
        
    async def resume(self):
        """Resume queue processing."""
        self._paused = False
        self.logger.info(f"Queue {self.name} resumed")
        
    async def clear(self):
        """Clear all tasks from queue."""
        async with self._lock:
            self._priority_queue.clear()
            self._fifo_queue.clear()
            self._scheduled_tasks.clear()
            
            # Cancel processing tasks
            for task in self._processing_tasks.values():
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                
            self._processing_tasks.clear()
            
            # Reset metrics
            self.metrics.pending_tasks = 0
            self.metrics.processing_tasks = 0
            
            self.logger.info(f"Queue {self.name} cleared")
            
    def get_size(self) -> int:
        """Get current queue size."""
        return (len(self._priority_queue) + len(self._fifo_queue) + 
                len(self._scheduled_tasks) + len(self._processing_tasks))
                
    def get_metrics(self) -> QueueMetrics:
        """
Get queue metrics."""
        # Update average times
        if self._processing_times:
            self.metrics.average_processing_time = sum(self._processing_times) / len(self._processing_times)
            
        if self._wait_times:
            self.metrics.average_wait_time = sum(self._wait_times) / len(self._wait_times)
            
        # Calculate throughput
        if self.metrics.completed_tasks > 0:
            time_diff = (datetime.utcnow() - self.metrics.last_updated).total_seconds()
            if time_diff > 0:
                self.metrics.throughput_per_minute = (self.metrics.completed_tasks / time_diff) * 60
                
        # Calculate error rate
        total_processed = self.metrics.completed_tasks + self.metrics.failed_tasks
        if total_processed > 0:
            self.metrics.error_rate = self.metrics.failed_tasks / total_processed
            
        self.metrics.last_updated = datetime.utcnow()
        return self.metrics


class QueueManager:
    """
    Advanced queue management system for crawler operations.
    
    Provides multiple queues, load balancing, worker management,
    and distributed processing capabilities.
    """
    
    def __init__(self, config: Optional[QueueConfig] = None):
        """
Initialize queue manager."""
        self.config = config or QueueConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        
        # Queue storage
        self.queues: Dict[str, TaskQueue] = {}
        self.workers: Dict[str, WorkerMetrics] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        
        # Redis connection for distributed queues
        self.redis_client: Optional[redis.Redis] = None
        if self.config.ENABLE_REDIS:
            self._initialize_redis()
            
        # Load balancing
        self.round_robin_index = 0
        self.queue_weights: Dict[str, float] = {}
        
        # Monitoring
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
        # Statistics
        self.global_stats = {
            'total_tasks_processed': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'active_workers': 0,
            'queue_count': 0,
            'average_response_time': 0.0
        }
        
    def _initialize_redis(self):
        """
Initialize Redis connection for distributed queues."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.REDIS_HOST,
                port=self.config.REDIS_PORT,
                db=self.config.REDIS_DB,
                password=self.config.REDIS_PASSWORD,
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established for distributed queues")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
            self.config.ENABLE_REDIS = False
            
    async def start(self):
        """Start queue manager."""
        try:
            # Create default queues
            await self.create_queue("default", QueueType.PRIORITY)
            await self.create_queue("high_priority", QueueType.PRIORITY)
            await self.create_queue("background", QueueType.FIFO)
            await self.create_queue("scheduled", QueueType.SCHEDULED)
            
            # Start monitoring
            if self.config.ENABLE_MONITORING:
                self.monitoring_active = True
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
                
            self.logger.info("Queue manager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start queue manager: {e}")
            raise
            
    async def create_queue(self, name: str, queue_type: QueueType = QueueType.PRIORITY) -> bool:
        """Create a new queue."""
        try:
            if name in self.queues:
                self.logger.warning(f"Queue {name} already exists")
                return False
                
            queue = TaskQueue(name, queue_type)
            self.queues[name] = queue
            self.queue_weights[name] = 1.0
            
            self.global_stats['queue_count'] = len(self.queues)
            
            self.logger.info(f"Queue {name} created with type {queue_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create queue {name}: {e}")
            return False
            
    async def submit_task(self, task: CrawlerTask, queue_name: str = "default") -> bool:
        """Submit task to specified queue."""
        try:
            if queue_name not in self.queues:
                self.logger.error(f"Queue {queue_name} does not exist")
                return False
                
            queue = self.queues[queue_name]
            success = await queue.put(task)
            
            if success:
                self.global_stats['total_tasks_processed'] += 1
                
                # Store in Redis if enabled
                if self.redis_client:
                    await self._store_task_in_redis(task, queue_name)
                    
                self.logger.debug(f"Task {task.task_id} submitted to queue {queue_name}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {e}")
            return False
            
    async def _store_task_in_redis(self, task: CrawlerTask, queue_name: str):
        """Store task in Redis for distributed processing."""
        try:
            task_data = {
                'task': asdict(task),
                'queue_name': queue_name,
                'submitted_at': datetime.utcnow().isoformat()
            }
            
            serialized_task = json.dumps(task_data, default=str)
            
            # Store in Redis list
            redis_key = f"queue:{queue_name}"
            self.redis_client.lpush(redis_key, serialized_task)
            
            # Set TTL
            self.redis_client.expire(redis_key, self.config.TASK_TTL)
            
        except Exception as e:
            self.logger.error(f"Failed to store task in Redis: {e}")
            
    async def get_task(self, queue_name: str = None, worker_id: str = None, timeout: float = 5.0) -> Optional[CrawlerTask]:
        """Get next task from queue(s)."""
        try:
            # Register worker if provided
            if worker_id:
                await self.register_worker(worker_id)
                
            # Get from specific queue
            if queue_name:
                if queue_name not in self.queues:
                    return None
                    
                queue = self.queues[queue_name]
                task = await queue.get(timeout)
                
                if task and worker_id:
                    self._update_worker_metrics(worker_id, 'task_assigned')
                    
                return task
                
            # Load balance across all queues
            return await self._get_balanced_task(worker_id, timeout)
            
        except Exception as e:
            self.logger.error(f"Failed to get task: {e}")
            return None
            
    async def _get_balanced_task(self, worker_id: Optional[str], timeout: float) -> Optional[CrawlerTask]:
        """Get task using load balancing algorithm."""
        if not self.queues:
            return None
            
        # Try round-robin with weights
        queue_names = list(self.queues.keys())
        attempts = len(queue_names)
        
        for _ in range(attempts):
            # Select queue based on round-robin
            queue_name = queue_names[self.round_robin_index % len(queue_names)]
            self.round_robin_index += 1
            
            # Check queue weight
            weight = self.queue_weights.get(queue_name, 1.0)
            if weight <= 0:
                continue
                
            queue = self.queues[queue_name]
            task = await queue.get(timeout / attempts)
            
            if task:
                if worker_id:
                    self._update_worker_metrics(worker_id, 'task_assigned')
                return task
                
        return None
        
    async def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None, queue_name: str = "default") -> bool:
        """Mark task as completed."""
        try:
            if queue_name not in self.queues:
                return False
                
            queue = self.queues[queue_name]
            success = await queue.complete_task(task_id, result)
            
            if success:
                self.global_stats['total_tasks_completed'] += 1
                
                # Execute callback if registered
                if task_id in self.task_callbacks:
                    callback = self.task_callbacks.pop(task_id)
                    try:
                        await callback(task_id, result, None)
                    except Exception as e:
                        self.logger.error(f"Task callback error: {e}")
                        
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to complete task: {e}")
            return False
            
    async def fail_task(self, task_id: str, error: str, queue_name: str = "default", retry: bool = True) -> bool:
        """Mark task as failed."""
        try:
            if queue_name not in self.queues:
                return False
                
            queue = self.queues[queue_name]
            success = await queue.fail_task(task_id, error, retry)
            
            if success:
                if not retry:
                    self.global_stats['total_tasks_failed'] += 1
                    
                # Execute callback if registered
                if task_id in self.task_callbacks:
                    callback = self.task_callbacks.pop(task_id)
                    try:
                        await callback(task_id, None, error)
                    except Exception as e:
                        self.logger.error(f"Task callback error: {e}")
                        
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to fail task: {e}")
            return False
            
    async def register_worker(self, worker_id: str) -> bool:
        """Register a worker."""
        try:
            if worker_id not in self.workers:
                self.workers[worker_id] = WorkerMetrics(worker_id=worker_id)
                self.global_stats['active_workers'] = len(self.workers)
                self.logger.info(f"Worker {worker_id} registered")
                
            # Update last active
            self.workers[worker_id].last_active = datetime.utcnow()
            self.workers[worker_id].status = "active"
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register worker: {e}")
            return False
            
    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker."""
        try:
            if worker_id in self.workers:
                self.workers.pop(worker_id)
                self.global_stats['active_workers'] = len(self.workers)
                self.logger.info(f"Worker {worker_id} unregistered")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to unregister worker: {e}")
            return False
            
    def _update_worker_metrics(self, worker_id: str, event: str):
        """Update worker metrics."""
        if worker_id not in self.workers:
            return
            
        worker = self.workers[worker_id]
        worker.last_active = datetime.utcnow()
        
        if event == 'task_assigned':
            worker.tasks_processed += 1
            worker.status = "processing"
        elif event == 'task_completed':
            worker.tasks_completed += 1
            worker.status = "idle"
        elif event == 'task_failed':
            worker.tasks_failed += 1
            worker.status = "idle"
            
    async def set_queue_weight(self, queue_name: str, weight: float) -> bool:
        """Set queue weight for load balancing."""
        try:
            if queue_name not in self.queues:
                return False
                
            self.queue_weights[queue_name] = max(0.0, weight)
            self.logger.info(f"Queue {queue_name} weight set to {weight}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set queue weight: {e}")
            return False
            
    async def pause_queue(self, queue_name: str) -> bool:
        """Pause a queue."""
        if queue_name not in self.queues:
            return False
            
        await self.queues[queue_name].pause()
        return True
        
    async def resume_queue(self, queue_name: str) -> bool:
        """
Resume a queue."""
        if queue_name not in self.queues:
            return False
            
        await self.queues[queue_name].resume()
        return True
        
    async def clear_queue(self, queue_name: str) -> bool:
        """
Clear a queue."""
        if queue_name not in self.queues:
            return False
            
        await self.queues[queue_name].clear()
        return True
        
    async def get_queue_metrics(self, queue_name: str) -> Optional[QueueMetrics]:
        """
Get metrics for a specific queue."""
        if queue_name not in self.queues:
            return None
            
        return self.queues[queue_name].get_metrics()
        
    async def get_all_queue_metrics(self) -> Dict[str, QueueMetrics]:
        """
Get metrics for all queues."""
        metrics = {}
        for name, queue in self.queues.items():
            metrics[name] = queue.get_metrics()
        return metrics
        
    async def get_worker_metrics(self, worker_id: str) -> Optional[WorkerMetrics]:
        """
Get metrics for a specific worker."""
        return self.workers.get(worker_id)
        
    async def get_all_worker_metrics(self) -> Dict[str, WorkerMetrics]:
        """
Get metrics for all workers."""
        return self.workers.copy()
        
    async def get_global_stats(self) -> Dict[str, Any]:
        """
Get global queue manager statistics."""
        return self.global_stats.copy()
        
    async def _monitoring_loop(self):
        """
Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Update global statistics
                await self._update_global_stats()
                
                # Clean up inactive workers
                await self._cleanup_inactive_workers()
                
                # Send metrics to collector
                if self.config.ENABLE_METRICS_COLLECTION:
                    await self._collect_and_send_metrics()
                    
                await asyncio.sleep(self.config.MONITORING_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(1)
                
    async def _update_global_stats(self):
        """Update global statistics."""
        total_processing_time = 0.0
        total_processed = 0
        
        for queue in self.queues.values():
            metrics = queue.get_metrics()
            if metrics.completed_tasks > 0:
                total_processing_time += metrics.average_processing_time * metrics.completed_tasks
                total_processed += metrics.completed_tasks
                
        if total_processed > 0:
            self.global_stats['average_response_time'] = total_processing_time / total_processed
            
    async def _cleanup_inactive_workers(self):
        """
Clean up inactive workers."""
        current_time = datetime.utcnow()
        inactive_threshold = timedelta(seconds=self.config.WORKER_TIMEOUT)
        
        inactive_workers = []
        for worker_id, worker in self.workers.items():
            if current_time - worker.last_active > inactive_threshold:
                inactive_workers.append(worker_id)
                
        for worker_id in inactive_workers:
            await self.unregister_worker(worker_id)
            self.logger.info(f"Cleaned up inactive worker: {worker_id}")
            
    async def _collect_and_send_metrics(self):
        """Collect and send metrics to monitoring system."""
        try:
            # Collect queue metrics
            queue_metrics = await self.get_all_queue_metrics()
            worker_metrics = await self.get_all_worker_metrics()
            global_stats = await self.get_global_stats()
            
            # Send to metrics collector
            metrics_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'queue_metrics': {name: asdict(metrics) for name, metrics in queue_metrics.items()},
                'worker_metrics': {worker_id: asdict(metrics) for worker_id, metrics in worker_metrics.items()},
                'global_stats': global_stats
            }
            
            await self.metrics_collector.send_metrics('queue_manager', metrics_data)
            
        except Exception as e:
            self.logger.error(f"Failed to collect and send metrics: {e}")
            
    async def shutdown(self):
        """Shutdown queue manager."""
        try:
            # Stop monitoring
            if self.monitoring_task:
                self.monitoring_active = False
                self.monitoring_task.cancel()
                
            # Clear all queues
            for queue_name in list(self.queues.keys()):
                await self.clear_queue(queue_name)
                
            # Unregister all workers
            for worker_id in list(self.workers.keys()):
                await self.unregister_worker(worker_id)
                
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
                
            self.logger.info("Queue manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Factory function
def create_queue_manager(config: Optional[QueueConfig] = None) -> QueueManager:
    """Create and return a queue manager instance."""
    return QueueManager(config)


# Utility functions
async def submit_batch_tasks(manager: QueueManager, tasks: List[CrawlerTask], queue_name: str = "default") -> Dict[str, bool]:
    """Submit multiple tasks in batch."""
    results = {}
    
    for task in tasks:
        success = await manager.submit_task(task, queue_name)
        results[task.task_id] = success
        
    return results


async def create_crawler_task(task_type: str, url: str, priority: TaskPriority = TaskPriority.NORMAL, **kwargs) -> CrawlerTask:
    """
Create a crawler task with generated ID."""
    task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
    
    return CrawlerTask(
        task_id=task_id,
        task_type=task_type,
        url=url,
        priority=priority,
        **kwargs
    )
