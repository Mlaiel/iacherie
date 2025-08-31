"""Stream Scheduler for IA Influencer Agent Platform
================================================

Intelligent scheduling system for stream processing tasks with priority
management, resource optimization, and automated load balancing.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import heapq
from uuid import uuid4
import json

from pydantic import BaseModel, Field

from ...core.config import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TaskPriority(int, Enum):
    """Task priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class TaskStatus(str, Enum):
    """Task execution status"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class SchedulingStrategy(str, Enum):
    """Task scheduling strategies"""    FIFO = "fifo"  # First In, First Out
    PRIORITY = "priority"  # Priority-based
    ROUND_ROBIN = "round_robin"  # Round-robin
    WEIGHTED = "weighted"  # Weighted scheduling
    ADAPTIVE = "adaptive"  # Adaptive scheduling


@dataclass
class ScheduledTask:
    """Scheduled task definition"""    id: str
    name: str
    function: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    result: Optional[Any] = None
    
    def __lt__(self, other):
        """For heap comparison - higher priority first"""        if self.priority != other.priority:
            return self.priority.value > other.priority.value
        return self.scheduled_at < other.scheduled_at


class WorkerConfig(BaseModel):
    """Worker configuration"""    worker_id: str = Field(description="Worker identifier")
    max_concurrent_tasks: int = Field(default=5, description="Maximum concurrent tasks")
    specialized_types: List[str] = Field(default_factory=list, description="Task types this worker handles")
    resources: Dict[str, Any] = Field(default_factory=dict, description="Worker resources")
    enabled: bool = Field(default=True, description="Worker enabled status")


class SchedulerStats(BaseModel):
    """Scheduler performance statistics"""    total_tasks: int = Field(default=0, description="Total tasks scheduled")
    completed_tasks: int = Field(default=0, description="Successfully completed tasks")
    failed_tasks: int = Field(default=0, description="Failed tasks")
    pending_tasks: int = Field(default=0, description="Pending tasks")
    running_tasks: int = Field(default=0, description="Currently running tasks")
    avg_execution_time: float = Field(default=0.0, description="Average execution time")
    avg_wait_time: float = Field(default=0.0, description="Average wait time")
    throughput_per_minute: float = Field(default=0.0, description="Tasks per minute")
    worker_utilization: float = Field(default=0.0, description="Worker utilization percentage")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StreamScheduler:
    """    Intelligent scheduling system for stream processing tasks with priority
    management, resource optimization, and automated load balancing.
    """    
    def __init__(self, strategy: SchedulingStrategy = SchedulingStrategy.PRIORITY):
        self.strategy = strategy
        self.task_queue: List[ScheduledTask] = []
        self.active_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.workers: Dict[str, WorkerConfig] = {}
        self.worker_tasks: Dict[str, Set[str]] = {}
        self.stats = SchedulerStats()
        self.task_callbacks: Dict[str, List[Callable]] = {}
        self._shutdown_event = asyncio.Event()
        self._queue_lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize stream scheduler"""        try:
            # Initialize default worker
            await self.add_worker(WorkerConfig(
                worker_id="default_worker",
                max_concurrent_tasks=10
            ))
            
            # Start scheduler tasks
            asyncio.create_task(self._scheduler_loop())
            asyncio.create_task(self._stats_updater())
            asyncio.create_task(self._cleanup_task())
            
            logger.info(f"StreamScheduler initialized with {self.strategy} strategy")
            
        except Exception as e:
            logger.error(f"Failed to initialize StreamScheduler: {e}")
            raise
            
    async def schedule_task(
        self,
        name: str,
        function: Callable,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: float = 0,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        timeout_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """        Schedule task for execution
        
        Args:
            name: Task name
            function: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority
            delay_seconds: Delay before execution
            scheduled_at: Specific schedule time
            max_retries: Maximum retry attempts
            timeout_seconds: Task timeout
            metadata: Additional metadata
            
        Returns:
            Task identifier
        """        try:
            task_id = str(uuid4())
            
            if scheduled_at is None:
                scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=delay_seconds)
                
            task = ScheduledTask(
                id=task_id,
                name=name,
                function=function,
                args=args,
                kwargs=kwargs or {},
                priority=priority,
                scheduled_at=scheduled_at,
                max_retries=max_retries,
                timeout_seconds=timeout_seconds,
                metadata=metadata or {}
            )
            
            async with self._queue_lock:
                if self.strategy == SchedulingStrategy.PRIORITY:
                    heapq.heappush(self.task_queue, task)
                else:
                    self.task_queue.append(task)
                    
            self.stats.total_tasks += 1
            self.stats.pending_tasks += 1
            
            logger.debug(f"Scheduled task {task_id}: {name}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to schedule task {name}: {e}")
            raise
            
    async def schedule_recurring_task(
        self,
        name: str,
        function: Callable,
        interval_seconds: float,
        args: tuple = (),
        kwargs: Optional[dict] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_occurrences: Optional[int] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """        Schedule recurring task
        
        Args:
            name: Task name
            function: Function to execute
            interval_seconds: Interval between executions
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Task priority
            max_occurrences: Maximum number of executions
            end_time: End time for recurring schedule
            
        Returns:
            Recurring task identifier
        """        try:
            recurring_id = str(uuid4())
            
            async def recurring_wrapper():
                occurrence_count = 0
                while not self._shutdown_event.is_set():
                    # Check termination conditions
                    if max_occurrences and occurrence_count >= max_occurrences:
                        break
                    if end_time and datetime.now(timezone.utc) >= end_time:
                        break
                        
                    # Schedule next occurrence
                    await self.schedule_task(
                        name=f"{name}_occurrence_{occurrence_count}",
                        function=function,
                        args=args,
                        kwargs=kwargs,
                        priority=priority,
                        metadata={"recurring_id": recurring_id, "occurrence": occurrence_count}
                    )
                    
                    occurrence_count += 1
                    await asyncio.sleep(interval_seconds)
                    
            # Start recurring task
            asyncio.create_task(recurring_wrapper())
            
            logger.info(f"Scheduled recurring task {recurring_id}: {name}")
            return recurring_id
            
        except Exception as e:
            logger.error(f"Failed to schedule recurring task {name}: {e}")
            raise
            
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel scheduled or running task"""        try:
            # Check active tasks
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                del self.active_tasks[task_id]
                
                # Update stats
                self.stats.running_tasks -= 1
                
                logger.info(f"Cancelled active task {task_id}")
                return True
                
            # Check pending tasks
            async with self._queue_lock:
                for i, task in enumerate(self.task_queue):
                    if task.id == task_id:
                        task.status = TaskStatus.CANCELLED
                        self.task_queue.pop(i)
                        
                        # Rebuild heap if using priority
                        if self.strategy == SchedulingStrategy.PRIORITY:
                            heapq.heapify(self.task_queue)
                            
                        # Update stats
                        self.stats.pending_tasks -= 1
                        
                        logger.info(f"Cancelled pending task {task_id}")
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
            
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and details"""        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        # Check completed tasks
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        # Check pending tasks
        else:
            task = None
            for t in self.task_queue:
                if t.id == task_id:
                    task = t
                    break
                    
        if not task:
            return None
            
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.value,
            "scheduled_at": task.scheduled_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "retry_count": task.retry_count,
            "error_message": task.error_message,
            "metadata": task.metadata
        }
        
    async def add_worker(self, config: WorkerConfig) -> bool:
        """Add worker to scheduler"""        try:
            self.workers[config.worker_id] = config
            self.worker_tasks[config.worker_id] = set()
            
            logger.info(f"Added worker {config.worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add worker: {e}")
            return False
            
    async def remove_worker(self, worker_id: str) -> bool:
        """Remove worker from scheduler"""        try:
            if worker_id in self.workers:
                del self.workers[worker_id]
                
            if worker_id in self.worker_tasks:
                # Cancel tasks assigned to this worker
                for task_id in list(self.worker_tasks[worker_id]):
                    await self.cancel_task(task_id)
                del self.worker_tasks[worker_id]
                
            logger.info(f"Removed worker {worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove worker {worker_id}: {e}")
            return False
            
    async def register_callback(
        self,
        event_type: str,
        callback: Callable[[ScheduledTask], None]
    ) -> None:
        """Register callback for task events"""        if event_type not in self.task_callbacks:
            self.task_callbacks[event_type] = []
        self.task_callbacks[event_type].append(callback)
        
    async def get_scheduler_stats(self) -> SchedulerStats:
        """Get scheduler performance statistics"""        # Update real-time stats
        self.stats.pending_tasks = len(self.task_queue)
        self.stats.running_tasks = len(self.active_tasks)
        
        # Calculate worker utilization
        total_capacity = sum(worker.max_concurrent_tasks for worker in self.workers.values())
        if total_capacity > 0:
            self.stats.worker_utilization = (self.stats.running_tasks / total_capacity) * 100
            
        self.stats.last_updated = datetime.now(timezone.utc)
        return self.stats
        
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(0.1)  # Check every 100ms
                
                # Get next task based on strategy
                task = await self._get_next_task()
                if not task:
                    continue
                    
                # Find available worker
                worker_id = await self._find_available_worker(task)
                if not worker_id:
                    # No worker available, put task back
                    async with self._queue_lock:
                        if self.strategy == SchedulingStrategy.PRIORITY:
                            heapq.heappush(self.task_queue, task)
                        else:
                            self.task_queue.insert(0, task)
                    continue
                    
                # Execute task
                await self._execute_task(task, worker_id)
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                
    async def _get_next_task(self) -> Optional[ScheduledTask]:
        """Get next task to execute based on strategy"""        async with self._queue_lock:
            if not self.task_queue:
                return None
                
            current_time = datetime.now(timezone.utc)
            
            if self.strategy == SchedulingStrategy.PRIORITY:
                # Check if highest priority task is ready
                if self.task_queue[0].scheduled_at <= current_time:
                    return heapq.heappop(self.task_queue)
            elif self.strategy == SchedulingStrategy.FIFO:
                # First in, first out
                for i, task in enumerate(self.task_queue):
                    if task.scheduled_at <= current_time:
                        return self.task_queue.pop(i)
            else:
                # Default to priority
                if self.task_queue[0].scheduled_at <= current_time:
                    return heapq.heappop(self.task_queue)
                    
            return None
            
    async def _find_available_worker(self, task: ScheduledTask) -> Optional[str]:
        """Find available worker for task"""        for worker_id, worker in self.workers.items():
            if not worker.enabled:
                continue
                
            # Check worker capacity
            current_tasks = len(self.worker_tasks.get(worker_id, set()))
            if current_tasks >= worker.max_concurrent_tasks:
                continue
                
            # Check task type specialization
            task_type = task.metadata.get("type")
            if worker.specialized_types and task_type not in worker.specialized_types:
                continue
                
            return worker_id
            
        return None
        
    async def _execute_task(self, task: ScheduledTask, worker_id: str) -> None:
        """Execute task on worker"""        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            
            # Track task
            self.active_tasks[task.id] = task
            self.worker_tasks[worker_id].add(task.id)
            
            # Update stats
            self.stats.pending_tasks -= 1
            self.stats.running_tasks += 1
            
            # Notify callbacks
            await self._notify_callbacks("task_started", task)
            
            # Execute task function
            asyncio.create_task(self._run_task(task, worker_id))
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.id}: {e}")
            await self._handle_task_failure(task, worker_id, str(e))
            
    async def _run_task(self, task: ScheduledTask, worker_id: str) -> None:
        """Run task function with timeout and error handling"""        try:
            # Execute with timeout if specified
            if task.timeout_seconds:
                result = await asyncio.wait_for(
                    self._call_task_function(task),
                    timeout=task.timeout_seconds
                )
            else:
                result = await self._call_task_function(task)
                
            # Task completed successfully
            await self._handle_task_completion(task, worker_id, result)
            
        except asyncio.TimeoutError:
            await self._handle_task_failure(task, worker_id, "Task timeout exceeded")
        except Exception as e:
            await self._handle_task_failure(task, worker_id, str(e))
            
    async def _call_task_function(self, task: ScheduledTask) -> Any:
        """Call task function with proper async handling"""        if asyncio.iscoroutinefunction(task.function):
            return await task.function(*task.args, **task.kwargs)
        else:
            return task.function(*task.args, **task.kwargs)
            
    async def _handle_task_completion(
        self,
        task: ScheduledTask,
        worker_id: str,
        result: Any
    ) -> None:
        """Handle successful task completion"""        try:
            # Update task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.result = result
            
            # Move to completed tasks
            self.completed_tasks[task.id] = task
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
                
            # Remove from worker
            if worker_id in self.worker_tasks:
                self.worker_tasks[worker_id].discard(task.id)
                
            # Update stats
            self.stats.running_tasks -= 1
            self.stats.completed_tasks += 1
            
            # Update execution time
            if task.started_at:
                execution_time = (task.completed_at - task.started_at).total_seconds()
                current_avg = self.stats.avg_execution_time
                total_completed = self.stats.completed_tasks
                self.stats.avg_execution_time = (
                    (current_avg * (total_completed - 1) + execution_time) / total_completed
                )
                
            # Notify callbacks
            await self._notify_callbacks("task_completed", task)
            
            logger.debug(f"Task {task.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error handling task completion: {e}")
            
    async def _handle_task_failure(
        self,
        task: ScheduledTask,
        worker_id: str,
        error_message: str
    ) -> None:
        """Handle task failure with retry logic"""        try:
            task.error_message = error_message
            task.retry_count += 1
            
            # Check if we should retry
            if task.retry_count <= task.max_retries:
                task.status = TaskStatus.RETRY
                
                # Schedule retry with delay
                retry_delay = task.retry_delay * (2 ** (task.retry_count - 1))  # Exponential backoff
                task.scheduled_at = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
                
                # Put back in queue
                async with self._queue_lock:
                    if self.strategy == SchedulingStrategy.PRIORITY:
                        heapq.heappush(self.task_queue, task)
                    else:
                        self.task_queue.append(task)
                        
                self.stats.pending_tasks += 1
                
                logger.warning(f"Task {task.id} failed, retry {task.retry_count}/{task.max_retries} scheduled")
            else:
                # Max retries exceeded
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)
                
                # Move to completed tasks
                self.completed_tasks[task.id] = task
                
                # Update stats
                self.stats.failed_tasks += 1
                
                logger.error(f"Task {task.id} failed permanently: {error_message}")
                
            # Cleanup
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
                
            if worker_id in self.worker_tasks:
                self.worker_tasks[worker_id].discard(task.id)
                
            self.stats.running_tasks -= 1
            
            # Notify callbacks
            await self._notify_callbacks("task_failed", task)
            
        except Exception as e:
            logger.error(f"Error handling task failure: {e}")
            
    async def _notify_callbacks(self, event_type: str, task: ScheduledTask) -> None:
        """Notify registered callbacks"""        callbacks = self.task_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(task)
                else:
                    callback(task)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")
                
    async def _stats_updater(self) -> None:
        """Background stats update task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Calculate throughput
                current_time = datetime.now(timezone.utc)
                one_minute_ago = current_time - timedelta(minutes=1)
                
                recent_completions = sum(
                    1 for task in self.completed_tasks.values()
                    if task.completed_at and task.completed_at >= one_minute_ago
                )
                
                self.stats.throughput_per_minute = recent_completions
                
            except Exception as e:
                logger.error(f"Stats updater error: {e}")
                
    async def _cleanup_task(self) -> None:
        """Background cleanup task"""        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Remove old completed tasks (keep last 1000)
                if len(self.completed_tasks) > 1000:
                    sorted_tasks = sorted(
                        self.completed_tasks.items(),
                        key=lambda x: x[1].completed_at or datetime.min.replace(tzinfo=timezone.utc),
                        reverse=True
                    )
                    
                    # Keep only last 1000
                    self.completed_tasks = dict(sorted_tasks[:1000])
                    
                logger.debug("Completed task cleanup")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown scheduler"""        try:
            self._shutdown_event.set()
            
            # Cancel all pending tasks
            async with self._queue_lock:
                for task in self.task_queue:
                    task.status = TaskStatus.CANCELLED
                self.task_queue.clear()
                
            # Wait for active tasks to complete (with timeout)
            timeout = 30  # 30 seconds timeout
            start_time = datetime.now(timezone.utc)
            
            while self.active_tasks and (datetime.now(timezone.utc) - start_time).total_seconds() < timeout:
                await asyncio.sleep(1)
                
            logger.info("StreamScheduler shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")
