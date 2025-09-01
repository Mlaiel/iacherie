"""Task Scheduler - Enterprise Task Scheduling & Execution Management

Advanced task scheduling system providing sophisticated task management, dependency
resolution, priority handling, and execution coordination for the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This task scheduling system is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization.

🎯 BUSINESS LOGIC:
Task Creation → Scheduling → Dependency Resolution → Resource Allocation → Execution → Monitoring
"""
import asyncio
import uuid
import heapq
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import json
import threading
from croniter import croniter
import pytz

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Task scheduling types"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    PERIODIC = "periodic"
    CRON = "cron"
    INTERVAL = "interval"
    EVENT_DRIVEN = "event_driven"
    DEPENDENCY_BASED = "dependency_based"


class TaskPriority(Enum):
    """Task execution priority levels"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Task execution status"""
    SCHEDULED = "scheduled"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class TaskType(Enum):
    """Types of tasks in the system"""
    CONTENT_ANALYSIS = "content_analysis"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    PROTECTION_SCAN = "protection_scan"
    REVENUE_SYNC = "revenue_sync"
    PLATFORM_UPDATE = "platform_update"
    DATA_CLEANUP = "data_cleanup"
    NOTIFICATION_SEND = "notification_send"
    SYSTEM_MAINTENANCE = "system_maintenance"


@dataclass
class TaskDependency:
    """Task dependency definition"""
    task_id: str
    dependency_type: str = "completion"  # completion, success, failure
    timeout_seconds: int = 3600


@dataclass
class TaskSchedule:
    """Task scheduling configuration"""
    schedule_type: ScheduleType
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    interval_seconds: Optional[int] = None
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    max_executions: Optional[int] = None
    execution_count: int = 0


@dataclass
class TaskConfiguration:
    """Complete task configuration"""
    task_id: str
    name: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    schedule: TaskSchedule
    dependencies: List[TaskDependency] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    retry_count: int = 3
    retry_delay_seconds: int = 60
    enabled: bool = True
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """Task execution state and tracking"""
    execution_id: str
    task_id: str
    configuration: TaskConfiguration
    status: TaskStatus
    scheduled_time: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_details: List[str] = field(default_factory=list)
    retry_count: int = 0
    next_retry_time: Optional[datetime] = None


@dataclass
class ScheduledTask:
    """Task in the scheduler queue"""
    execution_time: datetime
    priority: int
    task_id: str
    execution_id: str
    
    def __lt__(self, other):
        if self.execution_time == other.execution_time:
            return self.priority < other.priority
        return self.execution_time < other.execution_time


class TaskScheduler:
    """Enterprise task scheduling and execution management system"""
    
    def __init__(self, max_concurrent_tasks: int = 20):
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Task registry
        self.task_configurations: Dict[str, TaskConfiguration] = {}
        self.scheduled_tasks: List[ScheduledTask] = []
        self.active_executions: Dict[str, TaskExecution] = {}
        self.completed_executions: Dict[str, TaskExecution] = {}
        
        # Dependency tracking
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.waiting_tasks: Dict[str, List[str]] = defaultdict(list)
        
        # Scheduling engine
        self.scheduler_active = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.execution_lock = threading.Lock()
        
        # Event handling
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.task_listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # Performance tracking
        self.execution_metrics: Dict[str, List[float]] = defaultdict(list)
        self.schedule_accuracy: Dict[str, float] = {}
        
        # Initialize standard tasks
        self._initialize_standard_tasks()
        
        # Start scheduler
        self.start_scheduler()
        
        logger.info("TaskScheduler initialized successfully")
    
    def _initialize_standard_tasks(self):
        """Initialize standard business task configurations"""
        # Content Analysis Task
        content_analysis_task = TaskConfiguration(
            task_id="content_analysis_periodic",
            name="Periodic Content Analysis",
            description="Analyze newly uploaded content for optimization opportunities",
            task_type=TaskType.CONTENT_ANALYSIS,
            priority=TaskPriority.HIGH,
            schedule=TaskSchedule(
                schedule_type=ScheduleType.INTERVAL,
                interval_seconds=1800,  # Every 30 minutes
                timezone="UTC"
            ),
            timeout_seconds=1200,
            retry_count=2,
            enabled=True
        )
        
        # Fingerprint Generation Task
        fingerprint_task = TaskConfiguration(
            task_id="fingerprint_generation_batch",
            name="Batch Fingerprint Generation",
            description="Generate fingerprints for content protection",
            task_type=TaskType.FINGERPRINT_GENERATION,
            priority=TaskPriority.NORMAL,
            schedule=TaskSchedule(
                schedule_type=ScheduleType.CRON,
                cron_expression="0 2 * * *",  # Daily at 2 AM
                timezone="UTC"
            ),
            dependencies=[
                TaskDependency(task_id="content_analysis_periodic", dependency_type="success")
            ],
            timeout_seconds=3600,
            retry_count=3,
            enabled=True
        )
        
        # Protection Scan Task
        protection_scan_task = TaskConfiguration(
            task_id="protection_scan_continuous",
            name="Continuous Protection Scanning",
            description="Continuously scan for content violations",
            task_type=TaskType.PROTECTION_SCAN,
            priority=TaskPriority.URGENT,
            schedule=TaskSchedule(
                schedule_type=ScheduleType.INTERVAL,
                interval_seconds=300,  # Every 5 minutes
                timezone="UTC"
            ),
            timeout_seconds=600,
            retry_count=5,
            enabled=True
        )
        
        # Revenue Sync Task
        revenue_sync_task = TaskConfiguration(
            task_id="revenue_sync_daily",
            name="Daily Revenue Synchronization",
            description="Synchronize revenue data from all platforms",
            task_type=TaskType.REVENUE_SYNC,
            priority=TaskPriority.HIGH,
            schedule=TaskSchedule(
                schedule_type=ScheduleType.CRON,
                cron_expression="0 6 * * *",  # Daily at 6 AM
                timezone="UTC"
            ),
            timeout_seconds=1800,
            retry_count=3,
            enabled=True
        )
        
        # System Maintenance Task
        maintenance_task = TaskConfiguration(
            task_id="system_maintenance_weekly",
            name="Weekly System Maintenance",
            description="Perform weekly system maintenance and cleanup",
            task_type=TaskType.SYSTEM_MAINTENANCE,
            priority=TaskPriority.LOW,
            schedule=TaskSchedule(
                schedule_type=ScheduleType.CRON,
                cron_expression="0 1 * * 0",  # Weekly on Sunday at 1 AM
                timezone="UTC"
            ),
            timeout_seconds=7200,
            retry_count=1,
            enabled=True
        )
        
        # Register standard tasks
        self.register_task(content_analysis_task)
        self.register_task(fingerprint_task)
        self.register_task(protection_scan_task)
        self.register_task(revenue_sync_task)
        self.register_task(maintenance_task)
    
    def register_task(self, configuration: TaskConfiguration) -> bool:
        """Register a new task configuration"""
        try:
            # Validate configuration
            if not self._validate_task_configuration(configuration):
                return False
            
            # Register task
            self.task_configurations[configuration.task_id] = configuration
            
            # Build dependency graph
            self._update_dependency_graph(configuration)
            
            # Schedule initial execution if enabled
            if configuration.enabled:
                self._schedule_next_execution(configuration)
            
            logger.info(f"Task registered: {configuration.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Task registration failed: {e}")
            return False
    
    def _validate_task_configuration(self, config: TaskConfiguration) -> bool:
        """Validate task configuration"""
        try:
            # Required fields validation
            if not all([config.task_id, config.name, config.task_type]):
                logger.error("Missing required task configuration fields")
                return False
            
            # Schedule validation
            if not self._validate_schedule(config.schedule):
                logger.error("Invalid task schedule configuration")
                return False
            
            # Dependency validation
            for dep in config.dependencies:
                if dep.task_id == config.task_id:
                    logger.error("Task cannot depend on itself")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Task configuration validation error: {e}")
            return False
    
    def _validate_schedule(self, schedule: TaskSchedule) -> bool:
        """Validate task schedule configuration"""
        try:
            if schedule.schedule_type == ScheduleType.CRON:
                if not schedule.cron_expression:
                    return False
                # Validate cron expression
                try:
                    croniter(schedule.cron_expression)
                except ValueError:
                    return False
            
            elif schedule.schedule_type == ScheduleType.INTERVAL:
                if not schedule.interval_seconds or schedule.interval_seconds <= 0:
                    return False
            
            elif schedule.schedule_type == ScheduleType.DELAYED:
                if not schedule.start_time:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schedule validation error: {e}")
            return False
    
    def _update_dependency_graph(self, config: TaskConfiguration):
        """Update dependency graph for task"""
        for dep in config.dependencies:
            self.dependency_graph[dep.task_id].add(config.task_id)
    
    def _schedule_next_execution(self, config: TaskConfiguration):
        """Schedule next execution for a task"""
        try:
            next_time = self._calculate_next_execution_time(config)
            if next_time:
                execution_id = str(uuid.uuid4())
                
                scheduled_task = ScheduledTask(
                    execution_time=next_time,
                    priority=config.priority.value,
                    task_id=config.task_id,
                    execution_id=execution_id
                )
                
                with self.execution_lock:
                    heapq.heappush(self.scheduled_tasks, scheduled_task)
                
                logger.debug(f"Task {config.task_id} scheduled for {next_time}")
                
        except Exception as e:
            logger.error(f"Task scheduling failed: {e}")
    
    def _calculate_next_execution_time(self, config: TaskConfiguration) -> Optional[datetime]:
        """Calculate next execution time for a task"""
        try:
            now = datetime.now(pytz.timezone(config.schedule.timezone))
            
            if config.schedule.schedule_type == ScheduleType.IMMEDIATE:
                return now
            
            elif config.schedule.schedule_type == ScheduleType.DELAYED:
                return config.schedule.start_time
            
            elif config.schedule.schedule_type == ScheduleType.INTERVAL:
                if config.schedule.execution_count == 0:
                    return now + timedelta(seconds=config.schedule.interval_seconds)
                else:
                    return now + timedelta(seconds=config.schedule.interval_seconds)
            
            elif config.schedule.schedule_type == ScheduleType.CRON:
                cron = croniter(config.schedule.cron_expression, now)
                return cron.get_next(datetime)
            
            elif config.schedule.schedule_type == ScheduleType.PERIODIC:
                if config.schedule.interval_seconds:
                    return now + timedelta(seconds=config.schedule.interval_seconds)
            
            # Check max executions
            if (config.schedule.max_executions and 
                config.schedule.execution_count >= config.schedule.max_executions):
                return None
            
            # Check end time
            if config.schedule.end_time and now >= config.schedule.end_time:
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"Next execution time calculation failed: {e}")
            return None
    
    def start_scheduler(self):
        """Start the task scheduler"""
        if not self.scheduler_active:
            self.scheduler_active = True
            self.scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True
            )
            self.scheduler_thread.start()
            logger.info("Task scheduler started")
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.scheduler_active = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Task scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.scheduler_active:
            try:
                self._process_scheduled_tasks()
                self._check_dependency_resolutions()
                self._handle_retry_tasks()
                threading.Event().wait(1)  # Check every second
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
    
    def _process_scheduled_tasks(self):
        """Process tasks that are ready for execution"""
        now = datetime.now(timezone.utc)
        
        with self.execution_lock:
            ready_tasks = []
            
            while (self.scheduled_tasks and 
                   self.scheduled_tasks[0].execution_time <= now):
                ready_tasks.append(heapq.heappop(self.scheduled_tasks))
            
            # Execute ready tasks
            for scheduled_task in ready_tasks:
                if len(self.active_executions) < self.max_concurrent_tasks:
                    asyncio.create_task(self._execute_task(scheduled_task))
                else:
                    # Re-schedule for later if at capacity
                    scheduled_task.execution_time = now + timedelta(seconds=30)
                    heapq.heappush(self.scheduled_tasks, scheduled_task)
    
    def _check_dependency_resolutions(self):
        """Check if any waiting tasks can now be executed"""
        resolved_tasks = []
        
        for task_id, waiting_list in self.waiting_tasks.items():
            if self._are_dependencies_satisfied(task_id):
                resolved_tasks.extend(waiting_list)
                self.waiting_tasks[task_id] = []
        
        # Schedule resolved tasks
        for execution_id in resolved_tasks:
            self._schedule_dependency_resolved_task(execution_id)
    
    def _are_dependencies_satisfied(self, task_id: str) -> bool:
        """Check if all dependencies for a task are satisfied"""
        try:
            config = self.task_configurations.get(task_id)
            if not config:
                return False
            
            for dep in config.dependencies:
                # Check if dependency task has completed successfully
                if not self._is_dependency_satisfied(dep):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            return False
    
    def _is_dependency_satisfied(self, dependency: TaskDependency) -> bool:
        """Check if a specific dependency is satisfied"""
        # Look for recent successful execution of dependency task
        for execution in self.completed_executions.values():
            if (execution.task_id == dependency.task_id and
                execution.status == TaskStatus.COMPLETED and
                execution.completed_at and
                (datetime.now(timezone.utc) - execution.completed_at).total_seconds() <= dependency.timeout_seconds):
                return True
        
        return False
    
    def _schedule_dependency_resolved_task(self, execution_id: str):
        """Schedule a task whose dependencies are now resolved"""
        # This would integrate with the actual task execution
        logger.info(f"Dependencies resolved for task execution {execution_id}")
    
    def _handle_retry_tasks(self):
        """Handle tasks that need to be retried"""
        now = datetime.now(timezone.utc)
        
        retry_tasks = []
        for execution in list(self.active_executions.values()):
            if (execution.status == TaskStatus.RETRYING and
                execution.next_retry_time and
                execution.next_retry_time <= now):
                retry_tasks.append(execution)
        
        for execution in retry_tasks:
            asyncio.create_task(self._retry_task_execution(execution))
    
    async def _execute_task(self, scheduled_task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            config = self.task_configurations.get(scheduled_task.task_id)
            if not config:
                logger.error(f"Task configuration not found: {scheduled_task.task_id}")
                return
            
            # Create execution instance
            execution = TaskExecution(
                execution_id=scheduled_task.execution_id,
                task_id=scheduled_task.task_id,
                configuration=config,
                status=TaskStatus.PENDING,
                scheduled_time=scheduled_task.execution_time
            )
            
            # Check dependencies
            if not self._are_dependencies_satisfied(scheduled_task.task_id):
                self.waiting_tasks[scheduled_task.task_id].append(scheduled_task.execution_id)
                logger.info(f"Task {scheduled_task.task_id} waiting for dependencies")
                return
            
            # Start execution
            self.active_executions[scheduled_task.execution_id] = execution
            
            execution.status = TaskStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            
            # Emit task started event
            await self._emit_task_event("task_started", execution)
            
            # Execute task with timeout
            try:
                result = await asyncio.wait_for(
                    self._execute_task_logic(execution),
                    timeout=config.timeout_seconds
                )
                
                execution.result_data = result
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.now(timezone.utc)
                
                # Update execution count
                config.schedule.execution_count += 1
                
                # Schedule next execution if recurring
                if self._is_recurring_task(config):
                    self._schedule_next_execution(config)
                
                await self._complete_task_execution(execution)
                
            except asyncio.TimeoutError:
                execution.status = TaskStatus.FAILED
                execution.error_details.append("Task execution timeout")
                await self._handle_task_failure(execution)
                
            except Exception as e:
                execution.status = TaskStatus.FAILED
                execution.error_details.append(str(e))
                await self._handle_task_failure(execution)
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
    
    async def _execute_task_logic(self, execution: TaskExecution) -> Dict[str, Any]:
        """Execute the actual task business logic"""
        # Simulate task processing based on task type
        processing_time = {
            TaskType.CONTENT_ANALYSIS: 30,
            TaskType.FINGERPRINT_GENERATION: 60,
            TaskType.PROTECTION_SCAN: 15,
            TaskType.REVENUE_SYNC: 45,
            TaskType.PLATFORM_UPDATE: 20,
            TaskType.DATA_CLEANUP: 120,
            TaskType.NOTIFICATION_SEND: 5,
            TaskType.SYSTEM_MAINTENANCE: 300
        }.get(execution.configuration.task_type, 30)
        
        await asyncio.sleep(processing_time)
        
        return {
            "task_type": execution.configuration.task_type.value,
            "execution_id": execution.execution_id,
            "processing_time": processing_time,
            "parameters": execution.configuration.parameters,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "result": "success"
        }
    
    def _is_recurring_task(self, config: TaskConfiguration) -> bool:
        """Check if task is recurring"""
        return config.schedule.schedule_type in [
            ScheduleType.INTERVAL,
            ScheduleType.CRON,
            ScheduleType.PERIODIC
        ]
    
    async def _complete_task_execution(self, execution: TaskExecution):
        """Complete task execution and cleanup"""
        try:
            # Calculate execution time
            if execution.started_at:
                execution.execution_time = (
                    execution.completed_at - execution.started_at
                ).total_seconds()
            
            # Move to completed executions
            self.completed_executions[execution.execution_id] = execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Emit completion event
            await self._emit_task_event("task_completed", execution)
            
            # Update metrics
            self.execution_metrics[execution.task_id].append(execution.execution_time)
            
            logger.info(f"Task {execution.execution_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task completion failed: {e}")
    
    async def _handle_task_failure(self, execution: TaskExecution):
        """Handle task execution failure"""
        try:
            # Check for retry
            if execution.retry_count < execution.configuration.retry_count:
                execution.retry_count += 1
                execution.status = TaskStatus.RETRYING
                execution.next_retry_time = datetime.now(timezone.utc) + timedelta(
                    seconds=execution.configuration.retry_delay_seconds * execution.retry_count
                )
                
                logger.info(f"Task {execution.execution_id} scheduled for retry {execution.retry_count}")
                return
            
            # Task failed permanently
            execution.completed_at = datetime.now(timezone.utc)
            
            # Move to completed executions
            self.completed_executions[execution.execution_id] = execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Emit failure event
            await self._emit_task_event("task_failed", execution)
            
            logger.error(f"Task {execution.execution_id} failed permanently")
            
        except Exception as e:
            logger.error(f"Task failure handling failed: {e}")
    
    async def _retry_task_execution(self, execution: TaskExecution):
        """Retry failed task execution"""
        try:
            execution.status = TaskStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            execution.next_retry_time = None
            
            # Clear previous errors for retry
            execution.error_details = []
            
            logger.info(f"Retrying task {execution.execution_id} (attempt {execution.retry_count})")
            
            # Execute task logic
            try:
                result = await asyncio.wait_for(
                    self._execute_task_logic(execution),
                    timeout=execution.configuration.timeout_seconds
                )
                
                execution.result_data = result
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.now(timezone.utc)
                
                await self._complete_task_execution(execution)
                
            except Exception as e:
                execution.status = TaskStatus.FAILED
                execution.error_details.append(f"Retry failed: {str(e)}")
                await self._handle_task_failure(execution)
                
        except Exception as e:
            logger.error(f"Task retry failed: {e}")
    
    async def _emit_task_event(self, event_type: str, execution: TaskExecution):
        """Emit task events to registered handlers"""
        try:
            event_data = {
                "event_type": event_type,
                "execution_id": execution.execution_id,
                "task_id": execution.task_id,
                "status": execution.status.value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Call registered event handlers
            for handler in self.event_handlers.get(event_type, []):
                try:
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Event handler failed: {e}")
            
            # Call task-specific listeners
            for listener in self.task_listeners.get(execution.task_id, []):
                try:
                    await listener(event_data)
                except Exception as e:
                    logger.error(f"Task listener failed: {e}")
                    
        except Exception as e:
            logger.error(f"Event emission failed: {e}")
    
    def schedule_task(
        self,
        task_id: str,
        schedule_time: Optional[datetime] = None,
        parameters: Dict[str, Any] = None
    ) -> str:
        """Schedule a one-time task execution"""
        try:
            if task_id not in self.task_configurations:
                raise ValueError(f"Task '{task_id}' not found")
            
            config = self.task_configurations[task_id]
            execution_id = str(uuid.uuid4())
            
            # Update parameters if provided
            if parameters:
                config.parameters.update(parameters)
            
            # Create scheduled task
            scheduled_task = ScheduledTask(
                execution_time=schedule_time or datetime.now(timezone.utc),
                priority=config.priority.value,
                task_id=task_id,
                execution_id=execution_id
            )
            
            with self.execution_lock:
                heapq.heappush(self.scheduled_tasks, scheduled_task)
            
            logger.info(f"Task {task_id} scheduled for execution")
            return execution_id
            
        except Exception as e:
            logger.error(f"Task scheduling failed: {e}")
            raise
    
    def cancel_task(self, execution_id: str) -> bool:
        """Cancel a scheduled or running task"""
        try:
            # Check if task is active
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                execution.status = TaskStatus.CANCELLED
                execution.completed_at = datetime.now(timezone.utc)
                
                # Move to completed
                self.completed_executions[execution_id] = execution
                del self.active_executions[execution_id]
                
                logger.info(f"Task {execution_id} cancelled")
                return True
            
            # Check if task is scheduled
            with self.execution_lock:
                for i, scheduled_task in enumerate(self.scheduled_tasks):
                    if scheduled_task.execution_id == execution_id:
                        del self.scheduled_tasks[i]
                        heapq.heapify(self.scheduled_tasks)
                        logger.info(f"Scheduled task {execution_id} cancelled")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Task cancellation failed: {e}")
            return False
    
    def get_task_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get task execution status"""
        execution = (self.active_executions.get(execution_id) or 
                    self.completed_executions.get(execution_id))
        
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "task_id": execution.task_id,
            "status": execution.status.value,
            "scheduled_time": execution.scheduled_time.isoformat(),
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "execution_time": execution.execution_time,
            "retry_count": execution.retry_count,
            "error_details": execution.error_details,
            "result_data": execution.result_data
        }
    
    def get_scheduler_metrics(self) -> Dict[str, Any]:
        """Get scheduler performance metrics"""
        active_count = len(self.active_executions)
        scheduled_count = len(self.scheduled_tasks)
        completed_count = len(self.completed_executions)
        
        return {
            "active_tasks": active_count,
            "scheduled_tasks": scheduled_count,
            "completed_tasks": completed_count,
            "total_processed": completed_count,
            "execution_metrics": dict(self.execution_metrics),
            "task_utilization": (active_count / self.max_concurrent_tasks) * 100,
            "registered_tasks": len(self.task_configurations)
        }
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for task events"""
        self.event_handlers[event_type].append(handler)
    
    def register_task_listener(self, task_id: str, listener: Callable):
        """Register listener for specific task"""
        self.task_listeners[task_id].append(listener)
    
    def enable_task(self, task_id: str) -> bool:
        """Enable a task for scheduling"""
        try:
            if task_id in self.task_configurations:
                config = self.task_configurations[task_id]
                config.enabled = True
                self._schedule_next_execution(config)
                logger.info(f"Task {task_id} enabled")
                return True
            return False
        except Exception as e:
            logger.error(f"Task enable failed: {e}")
            return False
    
    def disable_task(self, task_id: str) -> bool:
        """Disable a task from scheduling"""
        try:
            if task_id in self.task_configurations:
                self.task_configurations[task_id].enabled = False
                
                # Remove scheduled instances
                with self.execution_lock:
                    self.scheduled_tasks = [
                        task for task in self.scheduled_tasks 
                        if task.task_id != task_id
                    ]
                    heapq.heapify(self.scheduled_tasks)
                
                logger.info(f"Task {task_id} disabled")
                return True
            return False
        except Exception as e:
            logger.error(f"Task disable failed: {e}")
            return False
    
    def shutdown(self):
        """Shutdown task scheduler and cleanup"""
        try:
            self.stop_scheduler()
            
            # Cancel all active tasks
            for execution_id in list(self.active_executions.keys()):
                self.cancel_task(execution_id)
            
            logger.info("TaskScheduler shutdown completed")
            
        except Exception as e:
            logger.error(f"TaskScheduler shutdown failed: {e}")
