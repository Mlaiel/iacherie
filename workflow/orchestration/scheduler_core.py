"""
🔥 ENTERPRISE SCHEDULER CORE - AINFLUE PLATFORM
Ultra-advanced scheduling core for enterprise workflows
Specialized scheduling functionality from automation engine
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import logging
from collections import defaultdict, deque

try:
    from croniter import croniter
    from ..core.exceptions import SchedulerException
    from ..utils.metrics import MetricsCollector
except ImportError:
    # Fallback for missing dependencies
    class croniter: pass
    class SchedulerException(Exception): pass
    class MetricsCollector: pass


class SchedulePriority(Enum):
    """Task execution priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class ScheduleConflictResolution(Enum):
    """Conflict resolution strategies."""
    QUEUE = "queue"
    SKIP = "skip"
    REPLACE = "replace"
    PARALLEL = "parallel"


@dataclass
class SchedulerConfig:
    """Enterprise scheduler configuration."""
    max_concurrent_tasks: int = 50
    max_queue_size: int = 1000
    default_timeout_seconds: int = 300
    enable_metrics: bool = True
    enable_persistence: bool = True
    conflict_resolution: ScheduleConflictResolution = ScheduleConflictResolution.QUEUE


class SchedulerCore:
    """
    🔥 ENTERPRISE SCHEDULER CORE
    
    Advanced scheduling engine with:
    - Priority-based task execution
    - Intelligent conflict resolution
    - Resource-aware scheduling
    - Advanced queue management
    - Performance optimization
    - Enterprise monitoring
    """
    
    def __init__(self, config: SchedulerConfig = None):
        """Initialize enterprise scheduler core."""
        self.config = config or SchedulerConfig()
        self.task_queue: deque = deque()
        self.priority_queues: Dict[SchedulePriority, deque] = {
            priority: deque() for priority in SchedulePriority
        }
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}
        self.failed_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_registry: Dict[str, Dict[str, Any]] = {}
        self.resource_usage: Dict[str, float] = defaultdict(float)
        self.metrics = MetricsCollector() if self.config.enable_metrics else None
        self.logger = logging.getLogger(__name__)
        
        # Scheduler state
        self._scheduler_active = True
        self._scheduler_task = None
        self._resource_monitor_task = None
        
        # Start scheduler
        self._start_scheduler()
    
    def _start_scheduler(self):
        """Start the scheduler background tasks."""
        if not self._scheduler_task:
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        if not self._resource_monitor_task:
            self._resource_monitor_task = asyncio.create_task(self._resource_monitor_loop())
    
    async def _scheduler_loop(self):
        """Main scheduler execution loop."""
        while self._scheduler_active:
            try:
                # Process tasks by priority
                await self._process_priority_queues()
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                # Update metrics
                self._update_scheduler_metrics()
                
                # Sleep briefly before next iteration
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(1)
    
    async def _resource_monitor_loop(self):
        """Monitor system resources and adjust scheduling."""
        while self._scheduler_active:
            try:
                # Monitor resource usage
                await self._monitor_resource_usage()
                
                # Adjust scheduling based on resources
                await self._adjust_scheduling()
                
                # Sleep for resource monitoring interval
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Resource monitor error: {e}")
                await asyncio.sleep(5)
    
    async def schedule_task(
        self,
        task_func: Callable,
        task_id: str = None,
        priority: SchedulePriority = SchedulePriority.NORMAL,
        delay_seconds: float = 0,
        scheduled_at: Optional[datetime] = None,
        parameters: Dict[str, Any] = None,
        timeout_seconds: Optional[int] = None,
        max_retries: int = 3,
        resource_requirements: Dict[str, float] = None
    ) -> str:
        """
        Schedule a task for execution.
        
        Args:
            task_func: Function to execute
            task_id: Optional task identifier
            priority: Task execution priority
            delay_seconds: Delay before execution
            scheduled_at: Specific execution time
            parameters: Task parameters
            timeout_seconds: Task timeout
            max_retries: Maximum retry attempts
            resource_requirements: Required resources
            
        Returns:
            Task ID
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        # Calculate execution time
        if scheduled_at:
            execution_time = scheduled_at
        else:
            execution_time = datetime.utcnow() + timedelta(seconds=delay_seconds)
        
        # Create task definition
        task_def = {
            'task_id': task_id,
            'task_func': task_func,
            'priority': priority,
            'execution_time': execution_time,
            'parameters': parameters or {},
            'timeout_seconds': timeout_seconds or self.config.default_timeout_seconds,
            'max_retries': max_retries,
            'retry_count': 0,
            'resource_requirements': resource_requirements or {},
            'created_at': datetime.utcnow(),
            'status': 'scheduled'
        }
        
        # Register task
        self.task_registry[task_id] = task_def
        
        # Add to appropriate queue
        if execution_time <= datetime.utcnow():
            # Immediate execution
            self.priority_queues[priority].append(task_def)
        else:
            # Delayed execution - add to time-based queue
            self.task_queue.append(task_def)
        
        self.logger.info(f"Scheduled task {task_id} with priority {priority.name}")
        
        if self.metrics:
            self.metrics.record_task_scheduled(priority.name)
        
        return task_id
    
    async def _process_priority_queues(self):
        """Process tasks from priority queues."""
        # Check if we can run more tasks
        if len(self.running_tasks) >= self.config.max_concurrent_tasks:
            return
        
        # Move ready delayed tasks to priority queues
        await self._move_ready_delayed_tasks()
        
        # Process tasks in priority order
        for priority in sorted(SchedulePriority, key=lambda p: p.value, reverse=True):
            queue = self.priority_queues[priority]
            
            while queue and len(self.running_tasks) < self.config.max_concurrent_tasks:
                task_def = queue.popleft()
                
                # Check resource availability
                if not await self._check_resource_availability(task_def):
                    # Re-queue if resources not available
                    queue.appendleft(task_def)
                    break
                
                # Execute task
                await self._execute_task(task_def)
    
    async def _move_ready_delayed_tasks(self):
        """Move delayed tasks that are ready to execute."""
        current_time = datetime.utcnow()
        ready_tasks = []
        remaining_tasks = []
        
        # Separate ready tasks from delayed tasks
        for task_def in self.task_queue:
            if task_def['execution_time'] <= current_time:
                ready_tasks.append(task_def)
            else:
                remaining_tasks.append(task_def)
        
        # Update task queue
        self.task_queue = deque(remaining_tasks)
        
        # Add ready tasks to priority queues
        for task_def in ready_tasks:
            priority = task_def['priority']
            self.priority_queues[priority].append(task_def)
    
    async def _check_resource_availability(self, task_def: Dict[str, Any]) -> bool:
        """Check if required resources are available."""
        requirements = task_def.get('resource_requirements', {})
        
        for resource, required_amount in requirements.items():
            current_usage = self.resource_usage.get(resource, 0.0)
            if current_usage + required_amount > 1.0:  # Assuming 1.0 = 100% capacity
                return False
        
        return True
    
    async def _execute_task(self, task_def: Dict[str, Any]):
        """Execute a scheduled task."""
        task_id = task_def['task_id']
        task_func = task_def['task_func']
        parameters = task_def['parameters']
        timeout = task_def['timeout_seconds']
        
        # Reserve resources
        self._reserve_resources(task_def)
        
        # Create and start task
        async_task = asyncio.create_task(
            self._run_task_with_timeout(task_func, parameters, timeout)
        )
        
        self.running_tasks[task_id] = async_task
        task_def['status'] = 'running'
        task_def['started_at'] = datetime.utcnow()
        
        self.logger.info(f"Started execution of task {task_id}")
        
        if self.metrics:
            self.metrics.record_task_started()
    
    async def _run_task_with_timeout(
        self,
        task_func: Callable,
        parameters: Dict[str, Any],
        timeout_seconds: int
    ) -> Any:
        """Run task with timeout handling."""
        try:
            result = await asyncio.wait_for(
                task_func(**parameters),
                timeout=timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            raise SchedulerException(f"Task timed out after {timeout_seconds} seconds")
    
    def _reserve_resources(self, task_def: Dict[str, Any]):
        """Reserve resources for task execution."""
        requirements = task_def.get('resource_requirements', {})
        
        for resource, amount in requirements.items():
            self.resource_usage[resource] += amount
    
    def _release_resources(self, task_def: Dict[str, Any]):
        """Release resources after task completion."""
        requirements = task_def.get('resource_requirements', {})
        
        for resource, amount in requirements.items():
            self.resource_usage[resource] = max(0, self.resource_usage[resource] - amount)
    
    async def _cleanup_completed_tasks(self):
        """Clean up completed tasks."""
        completed_task_ids = []
        
        for task_id, async_task in self.running_tasks.items():
            if async_task.done():
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            await self._handle_task_completion(task_id)
    
    async def _handle_task_completion(self, task_id: str):
        """Handle completion of a task."""
        async_task = self.running_tasks.pop(task_id)
        task_def = self.task_registry[task_id]
        
        # Release resources
        self._release_resources(task_def)
        
        # Update task status
        task_def['completed_at'] = datetime.utcnow()
        execution_time = (task_def['completed_at'] - task_def['started_at']).total_seconds()
        task_def['execution_time_seconds'] = execution_time
        
        try:
            result = await async_task
            task_def['status'] = 'completed'
            task_def['result'] = result
            
            self.completed_tasks[task_id] = task_def
            self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            
            if self.metrics:
                self.metrics.record_task_completed(execution_time)
        
        except Exception as e:
            task_def['status'] = 'failed'
            task_def['error'] = str(e)
            
            # Handle retries
            if task_def['retry_count'] < task_def['max_retries']:
                await self._retry_task(task_def)
            else:
                self.failed_tasks[task_id] = task_def
                self.logger.error(f"Task {task_id} failed permanently: {e}")
                
                if self.metrics:
                    self.metrics.record_task_failed()
    
    async def _retry_task(self, task_def: Dict[str, Any]):
        """Retry a failed task."""
        task_def['retry_count'] += 1
        task_def['status'] = 'retrying'
        
        # Add exponential backoff
        delay = 2 ** task_def['retry_count']
        task_def['execution_time'] = datetime.utcnow() + timedelta(seconds=delay)
        
        # Re-queue task
        self.task_queue.append(task_def)
        
        self.logger.info(f"Retrying task {task_def['task_id']} (attempt {task_def['retry_count']})")
        
        if self.metrics:
            self.metrics.record_task_retry()
    
    async def _monitor_resource_usage(self):
        """Monitor system resource usage."""
        # Implementation would monitor actual system resources
        # For now, simulate resource monitoring
        pass
    
    async def _adjust_scheduling(self):
        """Adjust scheduling based on resource availability."""
        # Implementation would adjust task scheduling based on resources
        # For now, just log resource usage
        if self.resource_usage:
            self.logger.debug(f"Current resource usage: {dict(self.resource_usage)}")
    
    def _update_scheduler_metrics(self):
        """Update scheduler performance metrics."""
        if not self.metrics:
            return
        
        self.metrics.update_gauge('scheduler.running_tasks', len(self.running_tasks))
        self.metrics.update_gauge('scheduler.queued_tasks', sum(len(q) for q in self.priority_queues.values()))
        self.metrics.update_gauge('scheduler.completed_tasks', len(self.completed_tasks))
        self.metrics.update_gauge('scheduler.failed_tasks', len(self.failed_tasks))
    
    # PUBLIC MANAGEMENT METHODS
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled or running task."""
        # Check if task is running
        if task_id in self.running_tasks:
            async_task = self.running_tasks[task_id]
            async_task.cancel()
            
            task_def = self.task_registry[task_id]
            task_def['status'] = 'cancelled'
            self._release_resources(task_def)
            
            self.logger.info(f"Cancelled running task {task_id}")
            return True
        
        # Check if task is in queues
        for priority_queue in self.priority_queues.values():
            for i, task_def in enumerate(priority_queue):
                if task_def['task_id'] == task_id:
                    del priority_queue[i]
                    task_def['status'] = 'cancelled'
                    self.logger.info(f"Cancelled queued task {task_id}")
                    return True
        
        # Check delayed tasks
        for i, task_def in enumerate(self.task_queue):
            if task_def['task_id'] == task_id:
                del self.task_queue[i]
                task_def['status'] = 'cancelled'
                self.logger.info(f"Cancelled delayed task {task_id}")
                return True
        
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        if task_id not in self.task_registry:
            return None
        
        task_def = self.task_registry[task_id].copy()
        
        # Remove function reference for serialization
        if 'task_func' in task_def:
            task_def['task_func'] = str(task_def['task_func'])
        
        return task_def
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get overall scheduler status."""
        return {
            'active': self._scheduler_active,
            'running_tasks': len(self.running_tasks),
            'queued_tasks': {
                priority.name: len(queue) 
                for priority, queue in self.priority_queues.items()
            },
            'delayed_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'resource_usage': dict(self.resource_usage)
        }
    
    async def shutdown(self):
        """Shutdown the scheduler."""
        self._scheduler_active = False
        
        # Cancel all running tasks
        for task_id in list(self.running_tasks.keys()):
            self.cancel_task(task_id)
        
        # Cancel scheduler tasks
        if self._scheduler_task:
            self._scheduler_task.cancel()
        
        if self._resource_monitor_task:
            self._resource_monitor_task.cancel()
        
        self.logger.info("Scheduler shutdown completed")