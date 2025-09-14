"""
Task Scheduler module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Task Scheduler - Utils Module - Enterprise Implementation

© 2025 Fahed Mlaiel. All rights reserved.
This software and associated documentation files are proprietary and confidential.
Unauthorized copying, distribution, or modification is strictly prohibited.
Licensed under Enterprise Commercial License.

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Developer & AI Architect - Task scheduling and workflow automation
Backend Senior Engineer - Enterprise task management and job queuing
DevOps Engineer - Infrastructure automation and scheduling optimization
IA Prompt Engineer - AI-powered task prioritization and execution

⚠️ STRICT WARNING: Any attempt to steal, copy, or use this concept, idea, or code
without written personal authorization from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import cron_descriptor
from croniter import croniter
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    SKIPPED = "skipped"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class ScheduleType(Enum):
    """Schedule types for tasks"""
    ONCE = "once"
    RECURRING = "recurring"
    CRON = "cron"
    INTERVAL = "interval"
    EVENT_DRIVEN = "event_driven"

class TaskType(Enum):
    """Task categories"""
    DATA_PROCESSING = "data_processing"
    CONTENT_ANALYSIS = "content_analysis"
    AI_TRAINING = "ai_training"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    NOTIFICATION = "notification"
    MONITORING = "monitoring"
    SYNC = "sync"

@dataclass
class TaskDefinition:
    """Task definition and configuration"""
    id: str
    name: str
    description: str
    task_type: TaskType
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: int = 3600
    max_retries: int = 3
    retry_delay_seconds: int = 60
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"

@dataclass
class Schedule:
    """Task schedule configuration"""
    schedule_type: ScheduleType
    expression: str  # Cron expression or interval
    timezone: str = "UTC"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_instances: int = 1
    catchup: bool = False
    enabled: bool = True

@dataclass
class TaskExecution:
    """Task execution instance"""
    execution_id: str
    task_id: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScheduledTask:
    """Scheduled task with definition and schedule"""
    task_definition: TaskDefinition
    schedule: Schedule
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    is_active: bool = True

class TaskScheduler:
    """
    Enterprise task scheduler with cron-based scheduling,
    dependency management, and priority-based execution
    """
    
    def __init__(self) -> None:
        self.tasks: Dict[str, ScheduledTask] = {}
        self.executions: Dict[str, TaskExecution] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_functions: Dict[str, Callable] = {}
        self.config_path = Path("./config/task_scheduler")
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Scheduler state
        self.is_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.max_concurrent_tasks = 10
        
        # Register built-in task functions
        self._register_builtin_functions()
        
        logger.info("TaskScheduler initialized")
    
    async def initialize_scheduler(self) -> bool:
        """Initialize task scheduler"""
        try:
            logger.info("Initializing task scheduler...")
            
            # Load existing tasks
            await self._load_scheduled_tasks()
            
            # Start scheduler loop
            await self.start_scheduler()
            
            logger.info("Task scheduler initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize task scheduler: {e}")
            return False
    
    async def register_task_function(self, name: str, function: Callable) -> bool:
        """Register a task execution function"""
        try:
            logger.info(f"Registering task function: {name}")
            
            if not callable(function):
                raise ValueError(f"Function {name} is not callable")
            
            self.task_functions[name] = function
            logger.info(f"Task function {name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register task function {name}: {e}")
            return False
    
    async def schedule_task(self, task_definition: TaskDefinition, schedule: Schedule) -> bool:
        """Schedule a new task"""
        try:
            logger.info(f"Scheduling task: {task_definition.name}")
            
            # Validate task definition
            if not self._validate_task_definition(task_definition):
                logger.error(f"Invalid task definition: {task_definition.name}")
                return False
            
            # Validate schedule
            if not self._validate_schedule(schedule):
                logger.error(f"Invalid schedule for task: {task_definition.name}")
                return False
            
            # Check if function exists
            if task_definition.function_name not in self.task_functions:
                logger.error(f"Task function {task_definition.function_name} not found")
                return False
            
            # Calculate next execution time
            next_execution = self._calculate_next_execution(schedule)
            
            # Create scheduled task
            scheduled_task = ScheduledTask(
                task_definition=task_definition,
                schedule=schedule,
                next_execution=next_execution
            )
            
            # Store scheduled task
            self.tasks[task_definition.id] = scheduled_task
            
            # Save configuration
            await self._save_task_config(scheduled_task)
            
            logger.info(f"Task {task_definition.name} scheduled successfully. Next execution: {next_execution}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule task {task_definition.name}: {e}")
            return False
    
    async def execute_task_now(self, task_id: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Execute a task immediately"""
        try:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            scheduled_task = self.tasks[task_id]
            task_def = scheduled_task.task_definition
            
            # Override parameters if provided
            exec_parameters = {**task_def.parameters}
            if parameters:
                exec_parameters.update(parameters)
            
            # Create execution instance
            execution_id = f"{task_id}_{uuid.uuid4().hex[:8]}"
            execution = TaskExecution(
                execution_id=execution_id,
                task_id=task_id,
                status=TaskStatus.PENDING,
                start_time=datetime.now(timezone.utc)
            )
            
            self.executions[execution_id] = execution
            
            logger.info(f"Executing task immediately: {task_def.name} (execution: {execution_id})")
            
            # Execute task
            asyncio.create_task(self._execute_task(scheduled_task, execution, exec_parameters))
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute task {task_id}: {e}")
            raise
    
    async def start_scheduler(self) -> bool:
        """Start the task scheduler"""
        try:
            if self.is_running:
                logger.warning("Scheduler is already running")
                return True
            
            logger.info("Starting task scheduler...")
            self.is_running = True
            
            # Start scheduler loop
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            logger.info("Task scheduler started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            return False
    
    async def stop_scheduler(self) -> bool:
        """Stop the task scheduler"""
        try:
            logger.info("Stopping task scheduler...")
            
            self.is_running = False
            
            # Cancel scheduler loop
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            
            # Cancel running tasks
            for task_id, task in self.running_tasks.items():
                logger.info(f"Cancelling running task: {task_id}")
                task.cancel()
            
            # Wait for all tasks to complete
            if self.running_tasks:
                await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
            
            logger.info("Task scheduler stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status information for a task"""
        try:
            if task_id not in self.tasks:
                return {'error': 'Task not found'}
            
            scheduled_task = self.tasks[task_id]
            task_def = scheduled_task.task_definition
            
            # Get recent executions
            recent_executions = [
                exec for exec in self.executions.values()
                if exec.task_id == task_id and
                datetime.now(timezone.utc) - exec.start_time <= timedelta(hours=24)
            ]
            
            return {
                'task_id': task_id,
                'name': task_def.name,
                'description': task_def.description,
                'type': task_def.task_type.value,
                'priority': task_def.priority.value,
                'is_active': scheduled_task.is_active,
                'schedule_type': scheduled_task.schedule.schedule_type.value,
                'last_execution': scheduled_task.last_execution.isoformat() if scheduled_task.last_execution else None,
                'next_execution': scheduled_task.next_execution.isoformat() if scheduled_task.next_execution else None,
                'execution_count': scheduled_task.execution_count,
                'success_count': scheduled_task.success_count,
                'failure_count': scheduled_task.failure_count,
                'success_rate': (scheduled_task.success_count / scheduled_task.execution_count * 100) if scheduled_task.execution_count > 0 else 0,
                'recent_executions': len(recent_executions),
                'is_running': task_id in self.running_tasks,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get task status for {task_id}: {e}")
            return {'error': str(e)}
    
    async def get_scheduler_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scheduler metrics"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Calculate metrics
            total_tasks = len(self.tasks)
            active_tasks = len([t for t in self.tasks.values() if t.is_active])
            running_tasks = len(self.running_tasks)
            
            # Recent execution metrics
            time_window = timedelta(hours=24)
            recent_executions = [
                exec for exec in self.executions.values()
                if current_time - exec.start_time <= time_window
            ]
            
            successful_executions = len([e for e in recent_executions if e.status == TaskStatus.COMPLETED])
            failed_executions = len([e for e in recent_executions if e.status == TaskStatus.FAILED])
            
            success_rate = (successful_executions / len(recent_executions) * 100) if recent_executions else 0
            
            # Upcoming tasks
            upcoming_tasks = []
            for task_id, scheduled_task in self.tasks.items():
                if scheduled_task.is_active and scheduled_task.next_execution:
                    if scheduled_task.next_execution <= current_time + timedelta(hours=1):
                        upcoming_tasks.append({
                            'task_id': task_id,
                            'name': scheduled_task.task_definition.name,
                            'next_execution': scheduled_task.next_execution.isoformat()
                        })
            
            return {
                'scheduler_status': 'running' if self.is_running else 'stopped',
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'inactive_tasks': total_tasks - active_tasks,
                'running_tasks': running_tasks,
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'recent_metrics': {
                    'total_executions': len(recent_executions),
                    'successful_executions': successful_executions,
                    'failed_executions': failed_executions,
                    'success_rate': round(success_rate, 2)
                },
                'upcoming_tasks': upcoming_tasks[:10],  # Next 10 tasks
                'registered_functions': len(self.task_functions),
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get scheduler metrics: {e}")
            return {'error': str(e)}
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Check for due tasks
                due_tasks = []
                for task_id, scheduled_task in self.tasks.items():
                    if (scheduled_task.is_active and 
                        scheduled_task.next_execution and 
                        scheduled_task.next_execution <= current_time):
                        due_tasks.append((task_id, scheduled_task))
                
                # Sort by priority
                due_tasks.sort(key=lambda x: x[1].task_definition.priority.value, reverse=True)
                
                # Execute due tasks (respecting concurrency limit)
                for task_id, scheduled_task in due_tasks:
                    if len(self.running_tasks) >= self.max_concurrent_tasks:
                        logger.warning("Maximum concurrent tasks reached, skipping task execution")
                        break
                    
                    if task_id not in self.running_tasks:
                        await self._schedule_task_execution(task_id, scheduled_task)
                
                # Clean up completed tasks
                completed_tasks = []
                for task_id, task in self.running_tasks.items():
                    if task.done():
                        completed_tasks.append(task_id)
                
                for task_id in completed_tasks:
                    del self.running_tasks[task_id]
                
                # Sleep for scheduling interval
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _schedule_task_execution(self, task_id -> None: str, scheduled_task -> None: ScheduledTask) -> None:
        """Schedule a task for execution"""
        try:
            # Create execution instance
            execution_id = f"{task_id}_{uuid.uuid4().hex[:8]}"
            execution = TaskExecution(
                execution_id=execution_id,
                task_id=task_id,
                status=TaskStatus.PENDING,
                start_time=datetime.now(timezone.utc)
            )
            
            self.executions[execution_id] = execution
            
            # Create task for execution
            task = asyncio.create_task(
                self._execute_task(scheduled_task, execution, scheduled_task.task_definition.parameters)
            )
            
            self.running_tasks[task_id] = task
            
            # Calculate next execution time
            scheduled_task.next_execution = self._calculate_next_execution(scheduled_task.schedule)
            
            logger.info(f"Scheduled task execution: {scheduled_task.task_definition.name} (execution: {execution_id})")
            
        except Exception as e:
            logger.error(f"Failed to schedule task execution for {task_id}: {e}")
    
    async def _execute_task(self, scheduled_task -> None: ScheduledTask, execution -> None: TaskExecution, parameters -> None: Dict[str, Any]) -> None:
        """Execute a task"""
        task_def = scheduled_task.task_definition
        
        try:
            logger.info(f"Executing task: {task_def.name} (execution: {execution.execution_id})")
            
            # Update execution status
            execution.status = TaskStatus.RUNNING
            execution.start_time = datetime.now(timezone.utc)
            
            # Get task function
            task_function = self.task_functions.get(task_def.function_name)
            if not task_function:
                raise ValueError(f"Task function {task_def.function_name} not found")
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    task_function(**parameters),
                    timeout=task_def.timeout_seconds
                )
                
                # Task completed successfully
                execution.status = TaskStatus.COMPLETED
                execution.result = result
                execution.end_time = datetime.now(timezone.utc)
                execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
                
                # Update scheduled task metrics
                scheduled_task.execution_count += 1
                scheduled_task.success_count += 1
                scheduled_task.last_execution = execution.end_time
                
                logger.info(f"Task completed successfully: {task_def.name} (duration: {execution.duration_seconds:.2f}s)")
                
            except asyncio.TimeoutError:
                raise Exception(f"Task timed out after {task_def.timeout_seconds} seconds")
            
        except Exception as e:
            logger.error(f"Task execution failed: {task_def.name} - {e}")
            
            # Handle failure
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.now(timezone.utc)
            execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
            
            # Update scheduled task metrics
            scheduled_task.execution_count += 1
            scheduled_task.failure_count += 1
            scheduled_task.last_execution = execution.end_time
            
            # Handle retries
            if execution.retry_count < task_def.max_retries:
                execution.retry_count += 1
                execution.status = TaskStatus.RETRYING
                
                logger.info(f"Retrying task: {task_def.name} (attempt {execution.retry_count}/{task_def.max_retries})")
                
                # Schedule retry
                await asyncio.sleep(task_def.retry_delay_seconds)
                await self._execute_task(scheduled_task, execution, parameters)
    
    def _calculate_next_execution(self, schedule: Schedule) -> Optional[datetime]:
        """Calculate next execution time based on schedule"""
        try:
            current_time = datetime.now(timezone.utc)
            
            if schedule.schedule_type == ScheduleType.ONCE:
                # One-time execution
                if schedule.start_date and schedule.start_date > current_time:
                    return schedule.start_date
                else:
                    return None
            
            elif schedule.schedule_type == ScheduleType.CRON:
                # Cron-based schedule
                cron = croniter(schedule.expression, current_time)
                next_time = cron.get_next(datetime)
                
                # Check end date
                if schedule.end_date and next_time > schedule.end_date:
                    return None
                
                return next_time
            
            elif schedule.schedule_type == ScheduleType.INTERVAL:
                # Interval-based schedule
                interval_seconds = int(schedule.expression)
                next_time = current_time + timedelta(seconds=interval_seconds)
                
                # Check end date
                if schedule.end_date and next_time > schedule.end_date:
                    return None
                
                return next_time
            
            else:
                logger.warning(f"Unsupported schedule type: {schedule.schedule_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to calculate next execution time: {e}")
            return None
    
    def _validate_task_definition(self, task_def: TaskDefinition) -> bool:
        """Validate task definition"""
        if not task_def.id or not task_def.name:
            return False
        if not task_def.function_name:
            return False
        if task_def.timeout_seconds <= 0:
            return False
        if task_def.max_retries < 0:
            return False
        return True
    
    def _validate_schedule(self, schedule: Schedule) -> bool:
        """Validate schedule configuration"""
        if schedule.schedule_type == ScheduleType.CRON:
            try:
                croniter(schedule.expression)
                return True
            except:
                return False
        elif schedule.schedule_type == ScheduleType.INTERVAL:
            try:
                int(schedule.expression)
                return True
            except:
                return False
        return True
    
    def _register_builtin_functions(self) -> None:
        """Register built-in task functions"""
        self.task_functions.update({
            'system_health_check': self._task_system_health_check,
            'cleanup_logs': self._task_cleanup_logs,
            'backup_data': self._task_backup_data,
            'send_notification': self._task_send_notification,
            'sync_external_data': self._task_sync_external_data
        })
    
    # Built-in task functions
    async def _task_system_health_check(self, **kwargs) -> Dict[str, Any]:
        """Built-in system health check task"""
        await asyncio.sleep(2)  # Simulate health check
        return {'status': 'healthy', 'checks_passed': 5, 'checks_failed': 0}
    
    async def _task_cleanup_logs(self, days_to_keep: int = 30, **kwargs) -> Dict[str, Any]:
        """Built-in log cleanup task"""
        await asyncio.sleep(5)  # Simulate cleanup
        return {'logs_cleaned': 150, 'space_freed_mb': 2048}
    
    async def _task_backup_data(self, backup_type: str = "incremental", **kwargs) -> Dict[str, Any]:
        """Built-in data backup task"""
        await asyncio.sleep(10)  # Simulate backup
        return {'backup_type': backup_type, 'files_backed_up': 1000, 'backup_size_mb': 5120}
    
    async def _task_send_notification(self, message: str, recipients: List[str], **kwargs) -> Dict[str, Any]:
        """Built-in notification task"""
        await asyncio.sleep(1)  # Simulate notification
        return {'message_sent': True, 'recipients_count': len(recipients)}
    
    async def _task_sync_external_data(self, source: str, **kwargs) -> Dict[str, Any]:
        """Built-in external data sync task"""
        await asyncio.sleep(8)  # Simulate sync
        return {'source': source, 'records_synced': 500, 'sync_time_seconds': 8}

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def example_task_scheduling() -> None:
    """Example usage of TaskScheduler"""
    try:
        # Initialize scheduler
        scheduler = TaskScheduler()
        await scheduler.initialize_scheduler()
        
        # Register custom task function
        async def custom_content_analysis(**kwargs) -> None:
            content_id = kwargs.get('content_id')
            await asyncio.sleep(3)  # Simulate processing
            return {'content_id': content_id, 'analysis_complete': True, 'score': 85.5}
        
        await scheduler.register_task_function('content_analysis', custom_content_analysis)
        
        # Create task definitions
        health_check_task = TaskDefinition(
            id="health_check_daily",
            name="Daily Health Check",
            description="Perform daily system health check",
            task_type=TaskType.MONITORING,
            function_name="system_health_check",
            priority=TaskPriority.HIGH
        )
        
        content_analysis_task = TaskDefinition(
            id="content_analysis_hourly",
            name="Hourly Content Analysis",
            description="Analyze new content uploads",
            task_type=TaskType.CONTENT_ANALYSIS,
            function_name="content_analysis",
            parameters={"content_id": "latest"},
            priority=TaskPriority.NORMAL
        )
        
        # Create schedules
        daily_schedule = Schedule(
            schedule_type=ScheduleType.CRON,
            expression="0 2 * * *",  # Daily at 2 AM
            timezone="UTC"
        )
        
        hourly_schedule = Schedule(
            schedule_type=ScheduleType.CRON,
            expression="0 * * * *",  # Every hour
            timezone="UTC"
        )
        
        # Schedule tasks
        await scheduler.schedule_task(health_check_task, daily_schedule)
        await scheduler.schedule_task(content_analysis_task, hourly_schedule)
        
        # Execute task immediately
        execution_id = await scheduler.execute_task_now("health_check_daily")
        logger.info(f"Immediate execution started: {execution_id}")
        
        # Wait a moment for execution
        await asyncio.sleep(3)
        
        # Get task status
        status = await scheduler.get_task_status("health_check_daily")
        logger.info(f"Task status: {json.dumps(status, indent=2)}")
        
        # Get scheduler metrics
        metrics = await scheduler.get_scheduler_metrics()
        logger.info(f"Scheduler metrics: {json.dumps(metrics, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Example task scheduling failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(example_task_scheduling())