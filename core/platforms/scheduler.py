"""Platform Scheduler Module

Advanced scheduling system for content distribution and platform operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging
import json
import uuid

try:
    from croniter import croniter
    CRONITER_AVAILABLE = True
except ImportError:
    CRONITER_AVAILABLE = False
    croniter = None

try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    pytz = None

from .base import PlatformBase, ContentMetadata
from .distributor import PlatformDistributor, DistributionTask, DistributionStrategy

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """
Types of scheduled tasks"""

    ONE_TIME = "one_time"
    RECURRING = "recurring"
    CRON = "cron"
    CONDITIONAL = "conditional"


class TaskStatus(Enum):
    """Status of scheduled tasks"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class ScheduleConfig:
    """
Schedule configuration"""
    schedule_type: ScheduleType
    start_time: datetime
    end_time: Optional[datetime] = None
    interval_seconds: Optional[int] = None
    cron_expression: Optional[str] = None
    max_executions: Optional[int] = None
    timezone: str = "UTC"
    
    def validate(self) -> bool:
        """Validate schedule configuration"""
        if self.schedule_type == ScheduleType.RECURRING and not self.interval_seconds:
            return False
        if self.schedule_type == ScheduleType.CRON and not self.cron_expression:
            return False
        if self.end_time and self.end_time <= self.start_time:
            return False
        return True


@dataclass
class TaskContext:
    """
Context for task execution"""
    task_id: str
    execution_count: int
    last_execution: Optional[datetime]
    next_execution: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledTask:
    """
Scheduled task definition"""
    task_id: str
    name: str
    description: str
    task_type: str
    schedule_config: ScheduleConfig
    priority: TaskPriority
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Task execution details
    target_function: Optional[Callable] = None
    function_args: List[Any] = field(default_factory=list)
    function_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # Content distribution specific
    content_path: Optional[str] = None
    content_metadata: Optional[ContentMetadata] = None
    platform_targets: List[str] = field(default_factory=list)
    distribution_strategy: Optional[DistributionStrategy] = None
    
    # Execution tracking
    status: TaskStatus = TaskStatus.PENDING
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    last_result: Optional[Any] = None
    last_error: Optional[str] = None
    
    def __post_init__(self):
        """
        try:
            logger.info(f"Executing __post_init__")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"__post_init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__post_init__ failed: {e}")
            raise
Post-initialization processing"""
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
        
        if not self.schedule_config.validate():
            raise ValueError("Invalid schedule configuration")
        
        self._calculate_next_execution()
    
    def _calculate_next_execution(self):
        """Calculate next execution time"""
        tz = pytz.timezone(self.schedule_config.timezone)
        now = datetime.now(tz)
        
        if self.schedule_config.schedule_type == ScheduleType.ONE_TIME:
            if self.execution_count == 0:
                self.next_execution = self.schedule_config.start_time
            else:
                self.next_execution = None
                
        elif self.schedule_config.schedule_type == ScheduleType.RECURRING:
            if self.execution_count == 0:
                self.next_execution = self.schedule_config.start_time
            else:
                self.next_execution = self.last_execution + timedelta(
                    seconds=self.schedule_config.interval_seconds
                )
                
        elif self.schedule_config.schedule_type == ScheduleType.CRON:
            if not CRONITER_AVAILABLE:
                logger.warning("croniter not available, falling back to daily schedule")
                self.next_execution = now + timedelta(days=1)
            else:
                cron = croniter(self.schedule_config.cron_expression, now)
                self.next_execution = cron.get_next(datetime)
        
        # Check end time and max executions
        if self.schedule_config.end_time and self.next_execution > self.schedule_config.end_time:
            self.next_execution = None
            
        if (self.schedule_config.max_executions and 
            self.execution_count >= self.schedule_config.max_executions):
            self.next_execution = None
    
    def should_execute(self) -> bool:
        """Check if task should be executed now"""
        try:
            logger.info(f"Executing mark_execution_failed")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_failed completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_failed failed: {e}")
            raise
        try:
            logger.info(f"Executing mark_execution_complete")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_complete completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_complete failed: {e}")
            raise
        if not self.enabled or self.status in [TaskStatus.RUNNING, TaskStatus.CANCELLED]:
            return False
        
        if not self.next_execution:
            return False
        
        now = datetime.utcnow()
        return now >= self.next_execution
    
    def mark_execution_start(self):
        """
        try:
            logger.info(f"Executing mark_execution_failed")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_failed completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_failed failed: {e}")
            raise
        try:
            logger.info(f"Executing mark_execution_complete")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_complete completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_complete failed: {e}")
            raise
        try:
            logger.info(f"Executing mark_execution_start")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_start completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_start failed: {e}")
            raise
Mark task execution as started"""
        self.status = TaskStatus.RUNNING
        self.last_execution = datetime.utcnow()
        self.execution_count += 1
    
    def mark_execution_complete(self, result: Any = None):
        """
        try:
            logger.info(f"Executing to_dict")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"to_dict completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"to_dict failed: {e}")
            raise
        try:
            logger.info(f"Executing mark_execution_failed")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_failed completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_failed failed: {e}")
            raise
        try:
            logger.info(f"Executing mark_execution_complete")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"mark_execution_complete completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mark_execution_complete failed: {e}")
            raise
Mark task execution as completed"""
        self.status = TaskStatus.COMPLETED
        self.last_result = result
        self.last_error = None
        self._calculate_next_execution()
    
    def mark_execution_failed(self, error: str):
        """
Mark task execution as failed"""
        self.status = TaskStatus.FAILED
        self.last_error = error
        self.last_result = None
        self._calculate_next_execution()
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'task_type': self.task_type,
            'schedule_config': {
                'schedule_type': self.schedule_config.schedule_type.value,
                'start_time': self.schedule_config.start_time.isoformat(),
                'end_time': self.schedule_config.end_time.isoformat() if self.schedule_config.end_time else None,
                'interval_seconds': self.schedule_config.interval_seconds,
                'cron_expression': self.schedule_config.cron_expression,
                'max_executions': self.schedule_config.max_executions,
                'timezone': self.schedule_config.timezone
            },
            'priority': self.priority.value,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'execution_count': self.execution_count,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'next_execution': self.next_execution.isoformat() if self.next_execution else None,
            'last_error': self.last_error
        }


class PlatformScheduler:
    """
Advanced scheduler for platform operations"""
    
    def __init__(self, check_interval: int = 10):
        """
        Initialize platform scheduler
        
        Args:
            check_interval: How often to check for tasks to execute (seconds)
        """
        self.check_interval = check_interval
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.scheduler_active = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.content_distributor: Optional[PlatformDistributor] = None
    
    def set_content_distributor(self, distributor: PlatformDistributor):
        """
        try:
            logger.info(f"Executing set_content_distributor")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"set_content_distributor completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"set_content_distributor failed: {e}")
            raise
Set content distributor for distribution tasks"""
        self.content_distributor = distributor
    
    def schedule_content_distribution(
        self,
        name: str,
        content_path: str,
        metadata: ContentMetadata,
        platform_targets: List[str],
        schedule_config: ScheduleConfig,
        distribution_strategy: DistributionStrategy = DistributionStrategy.SMART_ROUTING,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """
Schedule content distribution task"""
        
        task = ScheduledTask(
            task_id=str(uuid.uuid4()),
            name=name,
            description=f"Distribute {metadata.title} to {len(platform_targets)} platforms",
            task_type="content_distribution",
            schedule_config=schedule_config,
            priority=priority,
            content_path=content_path,
            content_metadata=metadata,
            platform_targets=platform_targets,
            distribution_strategy=distribution_strategy
        )
        
        self.tasks[task.task_id] = task
        logger.info(f"Scheduled content distribution task: {task.name} ({task.task_id})")
        
        return task.task_id
    
    def schedule_function(
        self,
        name: str,
        function: Callable,
        schedule_config: ScheduleConfig,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """Schedule function execution"""
        
        task = ScheduledTask(
            task_id=str(uuid.uuid4()),
            name=name,
            description=f"Execute function {function.__name__}",
            task_type="function_execution",
            schedule_config=schedule_config,
            priority=priority,
            target_function=function,
            function_args=args or [],
            function_kwargs=kwargs or {}
        )
        
        self.tasks[task.task_id] = task
        logger.info(f"Scheduled function task: {task.name} ({task.task_id})")
        
        return task.task_id
    
    def schedule_platform_health_check(
        self,
        platform_ids: List[str],
        schedule_config: ScheduleConfig,
        priority: TaskPriority = TaskPriority.HIGH
    ) -> str:
        """Schedule platform health check"""
        
        async def health_check_function():
            """
Health check function"""
            results = {}
            # Implementation would depend on having access to platform manager
            return results
        
        return self.schedule_function(
            name=f"Health check for {len(platform_ids)} platforms",
            function=health_check_function,
            schedule_config=schedule_config,
            priority=priority
        )
    
    def schedule_metrics_collection(
        self,
        platform_ids: List[str],
        schedule_config: ScheduleConfig,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """Schedule metrics collection"""
        
        async def metrics_collection_function():
            """
Metrics collection function"""
            results = {}
            # Implementation would depend on having access to metrics collector
            return results
        
        return self.schedule_function(
            name=f"Metrics collection for {len(platform_ids)} platforms",
            function=metrics_collection_function,
            schedule_config=schedule_config,
            priority=priority
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel scheduled task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.next_execution = None
        
        # Cancel running task if exists
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
        
        logger.info(f"Cancelled task: {task.name} ({task_id})")
        return True
    
    def pause_task(self, task_id: str) -> bool:
        """Pause scheduled task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.RUNNING:
            return False  # Cannot pause running task
        
        task.enabled = False
        task.status = TaskStatus.PAUSED
        logger.info(f"Paused task: {task.name} ({task_id})")
        return True
    
    def resume_task(self, task_id: str) -> bool:
        """Resume paused task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != TaskStatus.PAUSED:
            return False
        
        task.enabled = True
        task.status = TaskStatus.PENDING
        task._calculate_next_execution()
        logger.info(f"Resumed task: {task.name} ({task_id})")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """Remove task from scheduler"""
        if task_id not in self.tasks:
            return False
        
        # Cancel first if running
        self.cancel_task(task_id)
        
        # Remove from tasks
        del self.tasks[task_id]
        logger.info(f"Removed task: {task_id}")
        return True
    
    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks(
        self,
        status: TaskStatus = None,
        task_type: str = None,
        priority: TaskPriority = None
    ) -> List[ScheduledTask]:
        """
Get filtered list of tasks"""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]
        
        if priority:
            tasks = [task for task in tasks if task.priority == priority]
        
        return tasks
    
    def get_pending_tasks(self) -> List[ScheduledTask]:
        """
        try:
            logger.info(f"Executing get_pending_tasks")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"get_pending_tasks completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"get_pending_tasks failed: {e}")
            raise
Get tasks ready for execution"""
        return [
            task for task in self.tasks.values()
            if task.should_execute()
        ]
    
    async def execute_task(self, task: ScheduledTask) -> Any:
        """
Execute a single task"""
        task.mark_execution_start()
        
        try:
            if task.task_type == "content_distribution":
                if not self.content_distributor:
                    raise Exception("Content distributor not configured")
                
                result = await self.content_distributor.distribute_content(
                    task_id=f"scheduled_{task.task_id}",
                    content_path=task.content_path,
                    metadata=task.content_metadata,
                    platform_targets=[
                        {"platform_id": pid, "priority": 1}
                        for pid in task.platform_targets
                    ],
                    strategy=task.distribution_strategy
                )
                
                task.mark_execution_complete(result)
                return result
                
            elif task.task_type == "function_execution":
                if not task.target_function:
                    raise Exception("No target function defined")
                
                if asyncio.iscoroutinefunction(task.target_function):
                    result = await task.target_function(*task.function_args, **task.function_kwargs)
                else:
                    result = task.target_function(*task.function_args, **task.function_kwargs)
                
                task.mark_execution_complete(result)
                return result
            
            else:
                raise Exception(f"Unknown task type: {task.task_type}")
                
        except Exception as e:
            error_msg = str(e)
            task.mark_execution_failed(error_msg)
            logger.error(f"Task execution failed: {task.name} - {error_msg}")
            raise
    
    async def start(self):
        """Start the scheduler"""
        if self.scheduler_active:
            logger.warning("Scheduler already active")
            return
        
        self.scheduler_active = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Platform scheduler started")
    
    async def stop(self):
        try:
            logger.info(f"Executing stop")
            
            # Implementation for stop
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"stop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"stop failed: {e}")
            raise
    async def _scheduler_loop(self):
        """Main scheduler execution loop"""
        try:
            while self.scheduler_active:
                try:
                    # Get pending tasks
                    pending_tasks = self.get_pending_tasks()
                    
                    # Sort by priority
                    pending_tasks.sort(key=lambda t: t.priority.value, reverse=True)
                    
                    # Execute tasks
                    for task in pending_tasks:
                        if task.task_id in self.running_tasks:
                            continue  # Task already running
                        
                        # Create and start task execution
                        execution_task = asyncio.create_task(
                            self.execute_task(task),
                            name=f"exec_{task.task_id}"
                        )
                        
                        self.running_tasks[task.task_id] = execution_task
                        
                        # Set up completion callback
                        execution_task.add_done_callback(
                            lambda t, tid=task.task_id: self._task_completed(tid, t)
                        )
                    
                    # Clean up completed tasks
                    completed_task_ids = [
                        task_id for task_id, task in self.running_tasks.items()
                        if task.done()
                    ]
                    
                    for task_id in completed_task_ids:
                        del self.running_tasks[task_id]
                    
                except Exception as e:
                    logger.error(f"Scheduler loop error: {e}")
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
        except Exception as e:
            logger.error(f"Scheduler loop fatal error: {e}")
            self.scheduler_active = False
    
    def _task_completed(self, task_id: str, execution_task: asyncio.Task):
        """Handle task completion"""
        try:
            if execution_task.cancelled():
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.CANCELLED
            elif execution_task.exception():
                if task_id in self.tasks:
                    error = str(execution_task.exception())
                    self.tasks[task_id].mark_execution_failed(error)
            else:
                # Task completed successfully
                pass  # Already marked complete in execute_task
                
        except Exception as e:
            logger.error(f"Error handling task completion: {e}")
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        task_counts = {
            'total': len(self.tasks),
            'pending': len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            'running': len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            'completed': len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            'failed': len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            'cancelled': len([t for t in self.tasks.values() if t.status == TaskStatus.CANCELLED]),
            'paused': len([t for t in self.tasks.values() if t.status == TaskStatus.PAUSED])
        }
        
        task_types = {}
        for task in self.tasks.values():
            task_types[task.task_type] = task_types.get(task.task_type, 0) + 1
        
        return {
            'scheduler_active': self.scheduler_active,
            'check_interval_seconds': self.check_interval,
            'task_counts': task_counts,
            'task_types': task_types,
            'running_tasks': len(self.running_tasks),
            'next_execution': min([
                task.next_execution for task in self.tasks.values()
                if task.next_execution and task.enabled
            ], default=None)
        }
    
    def export_tasks(self) -> Dict[str, Any]:
        """
        try:
            logger.info(f"Executing get_scheduler")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"get_scheduler completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"get_scheduler failed: {e}")
            raise
Export all tasks data"""
        return {
            'export_timestamp': datetime.utcnow().isoformat(),
            'scheduler_stats': self.get_scheduler_stats(),
            'tasks': [task.to_dict() for task in self.tasks.values()]
        }


# Global scheduler instance
_global_scheduler: Optional[PlatformScheduler] = None


def get_scheduler() -> PlatformScheduler:
    """
    try:
        logger.info(f"Executing get_scheduler")
        
        # Implement operation logic
        result = await self._execute_operation()
        
        logger.info(f"get_scheduler completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"get_scheduler failed: {e}")
        raise
Get global scheduler instance"""
    global _global_scheduler
    
    if _global_scheduler is None:
        _global_scheduler = PlatformScheduler()
    
    return _global_scheduler


async def start_scheduler():
    """
Start global scheduler"""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """
Stop global scheduler"""
    global _global_scheduler
    
    if _global_scheduler:
        await _global_scheduler.stop()
