"""Crawl Scheduler Implementation
=============================

Advanced scheduling system for managing crawler tasks with intelligent prioritization.
Implements dynamic scheduling, workload balancing, and resource optimization.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import heapq
import uuid
from collections import defaultdict, deque
import cron_descriptor
from croniter import croniter


class TaskStatus(Enum):
    """Task execution status"""    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    SCHEDULED = "scheduled"


class TaskPriority(Enum):
    """Task priority levels"""    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class ScheduleType(Enum):
    """Schedule type definitions"""    ONCE = "once"
    INTERVAL = "interval" 
    CRON = "cron"
    CONDITION = "condition"
    MANUAL = "manual"


@dataclass
class TaskConfiguration:
    """Configuration for scheduled tasks"""    task_id: str
    name: str
    platform: str
    crawler_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    schedule_type: ScheduleType = ScheduleType.ONCE
    schedule_expression: Optional[str] = None  # Cron or interval expression
    retry_count: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 3600  # seconds
    max_parallel_instances: int = 1
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    condition_callback: Optional[Callable] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True


@dataclass
class TaskExecution:
    """Task execution instance"""    execution_id: str
    task_id: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_attempt: int = 0
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


@dataclass
class SchedulerMetrics:
    """Scheduler performance metrics"""    total_tasks_scheduled: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_cancelled: int = 0
    average_execution_time: float = 0.0
    queue_length: int = 0
    active_executions: int = 0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class PriorityQueue:
    """Priority queue for task scheduling"""    
    def __init__(self):
        self._queue = []
        self._index = 0
    
    def push(self, item, priority: float):
        """Add item with priority (lower values = higher priority)"""        heapq.heappush(self._queue, (priority, self._index, item))
        self._index += 1
    
    def pop(self):
        """Get highest priority item"""        if self._queue:
            return heapq.heappop(self._queue)[2]
        return None
    
    def peek(self):
        """Look at highest priority item without removing"""        if self._queue:
            return self._queue[0][2]
        return None
    
    def size(self):
        """Get queue size"""        return len(self._queue)
    
    def clear(self):
        """Clear the queue"""        self._queue.clear()
        self._index = 0


class CrawlScheduler:
    """    Advanced crawling scheduler with intelligent task management and resource optimization.
    
    Features:
    - Dynamic task prioritization
    - Cron-based scheduling
    - Interval-based scheduling
    - Condition-based scheduling
    - Dependency management
    - Resource allocation
    - Workload balancing
    - Retry mechanisms
    - Performance monitoring
    - Task history and analytics
    """    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.logger = logging.getLogger(__name__)
        
        # Core scheduler state
        self.max_concurrent_tasks = max_concurrent_tasks
        self.is_running = False
        self._shutdown_event = asyncio.Event()
        
        # Task management
        self.task_configurations: Dict[str, TaskConfiguration] = {}
        self.task_queue = PriorityQueue()
        self.active_executions: Dict[str, TaskExecution] = {}
        self.execution_history: List[TaskExecution] = []
        
        # Scheduling
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        self.cron_schedules: Dict[str, croniter] = {}
        
        # Resource management
        self.resource_limits = {
            'cpu_percent': 80.0,
            'memory_mb': 1024,
            'network_mb_per_sec': 10,
            'concurrent_crawlers': max_concurrent_tasks
        }
        self.current_resource_usage = {
            'cpu_percent': 0.0,
            'memory_mb': 0,
            'network_mb_per_sec': 0,
            'concurrent_crawlers': 0
        }
        
        # Dependencies
        self.dependency_graph: Dict[str, List[str]] = {}
        self.completed_tasks: set = set()
        
        # Metrics and monitoring
        self.metrics = SchedulerMetrics()
        self.performance_history: deque = deque(maxlen=1000)
        
        # Callbacks
        self.task_callbacks: Dict[str, List[Callable]] = {
            'on_task_start': [],
            'on_task_complete': [],
            'on_task_fail': [],
            'on_task_retry': []
        }
        
        # Background tasks
        self._scheduler_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the scheduler"""        try:
            if self.is_running:
                self.logger.warning("Scheduler is already running")
                return
            
            self.is_running = True
            self._shutdown_event.clear()
            
            # Start background tasks
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            
            self.logger.info("Crawl scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the scheduler gracefully"""        try:
            if not self.is_running:
                return
            
            self.logger.info("Stopping crawl scheduler...")
            
            # Signal shutdown
            self.is_running = False
            self._shutdown_event.set()
            
            # Cancel all scheduled tasks
            for task_id, task in self.scheduled_tasks.items():
                if not task.done():
                    task.cancel()
                    self.logger.debug(f"Cancelled scheduled task: {task_id}")
            
            # Wait for active executions to complete (with timeout)
            if self.active_executions:
                self.logger.info(f"Waiting for {len(self.active_executions)} active tasks to complete...")
                
                # Give tasks 30 seconds to complete gracefully
                await asyncio.sleep(30)
                
                # Force cancel remaining tasks
                for execution_id, execution in self.active_executions.items():
                    execution.status = TaskStatus.CANCELLED
                    execution.end_time = datetime.utcnow()
                    self.logger.warning(f"Force cancelled task execution: {execution_id}")
            
            # Cancel background tasks
            if self._scheduler_task and not self._scheduler_task.done():
                self._scheduler_task.cancel()
            
            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
            
            self.logger.info("Crawl scheduler stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {str(e)}")
    
    def schedule_task(self, task_config: TaskConfiguration) -> str:
        """        Schedule a new task.
        
        Args:
            task_config: Task configuration
            
        Returns:
            Task ID
        """        try:
            # Validate task configuration
            if not self._validate_task_config(task_config):
                raise ValueError("Invalid task configuration")
            
            # Store task configuration
            self.task_configurations[task_config.task_id] = task_config
            
            # Handle different schedule types
            if task_config.schedule_type == ScheduleType.ONCE:
                self._schedule_immediate_task(task_config)
            
            elif task_config.schedule_type == ScheduleType.INTERVAL:
                self._schedule_interval_task(task_config)
            
            elif task_config.schedule_type == ScheduleType.CRON:
                self._schedule_cron_task(task_config)
            
            elif task_config.schedule_type == ScheduleType.CONDITION:
                self._schedule_conditional_task(task_config)
            
            elif task_config.schedule_type == ScheduleType.MANUAL:
                # Manual tasks are stored but not scheduled
                pass
            
            # Update dependencies
            if task_config.dependencies:
                self.dependency_graph[task_config.task_id] = task_config.dependencies
            
            self.logger.info(f"Scheduled task: {task_config.name} ({task_config.task_id})")
            
            return task_config.task_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling task {task_config.name}: {str(e)}")
            raise
    
    def unschedule_task(self, task_id: str) -> bool:
        """        Unschedule a task.
        
        Args:
            task_id: Task ID to unschedule
            
        Returns:
            Success status
        """        try:
            # Remove from configurations
            if task_id in self.task_configurations:
                del self.task_configurations[task_id]
            
            # Cancel scheduled task
            if task_id in self.scheduled_tasks:
                task = self.scheduled_tasks[task_id]
                if not task.done():
                    task.cancel()
                del self.scheduled_tasks[task_id]
            
            # Remove from cron schedules
            if task_id in self.cron_schedules:
                del self.cron_schedules[task_id]
            
            # Remove from dependency graph
            if task_id in self.dependency_graph:
                del self.dependency_graph[task_id]
            
            # Remove dependencies on this task
            for other_task_id, deps in self.dependency_graph.items():
                if task_id in deps:
                    deps.remove(task_id)
            
            self.logger.info(f"Unscheduled task: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unscheduling task {task_id}: {str(e)}")
            return False
    
    async def execute_task_now(self, task_id: str) -> str:
        """        Execute a task immediately.
        
        Args:
            task_id: Task ID to execute
            
        Returns:
            Execution ID
        """        try:
            if task_id not in self.task_configurations:
                raise ValueError(f"Task {task_id} not found")
            
            task_config = self.task_configurations[task_id]
            
            # Check if we can execute (resource limits, dependencies)
            if not await self._can_execute_task(task_config):
                raise RuntimeError("Cannot execute task due to resource or dependency constraints")
            
            # Create execution
            execution_id = str(uuid.uuid4())
            execution = TaskExecution(
                execution_id=execution_id,
                task_id=task_id,
                status=TaskStatus.PENDING,
                start_time=datetime.utcnow()
            )
            
            # Add to active executions
            self.active_executions[execution_id] = execution
            
            # Execute task asynchronously
            asyncio.create_task(self._execute_task(execution, task_config))
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {str(e)}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """        Get task status and information.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """        try:
            if task_id not in self.task_configurations:
                return {'error': 'Task not found'}
            
            task_config = self.task_configurations[task_id]
            
            # Get recent executions
            recent_executions = [
                {
                    'execution_id': ex.execution_id,
                    'status': ex.status.value,
                    'start_time': ex.start_time.isoformat() if ex.start_time else None,
                    'end_time': ex.end_time.isoformat() if ex.end_time else None,
                    'duration': ex.duration,
                    'error': ex.error,
                    'retry_attempt': ex.retry_attempt
                }
                for ex in self.execution_history
                if ex.task_id == task_id
            ][-10:]  # Last 10 executions
            
            # Get active executions
            active_executions = [
                {
                    'execution_id': ex.execution_id,
                    'status': ex.status.value,
                    'start_time': ex.start_time.isoformat() if ex.start_time else None,
                    'duration': (datetime.utcnow() - ex.start_time).total_seconds() if ex.start_time else None
                }
                for ex in self.active_executions.values()
                if ex.task_id == task_id
            ]
            
            # Calculate next run time
            next_run_time = None
            if task_config.schedule_type == ScheduleType.CRON and task_id in self.cron_schedules:
                next_run_time = self.cron_schedules[task_id].get_next(datetime).isoformat()
            
            return {
                'task_id': task_id,
                'name': task_config.name,
                'platform': task_config.platform,
                'enabled': task_config.enabled,
                'schedule_type': task_config.schedule_type.value,
                'schedule_expression': task_config.schedule_expression,
                'priority': task_config.priority.value,
                'next_run_time': next_run_time,
                'active_executions': active_executions,
                'recent_executions': recent_executions,
                'total_executions': len([ex for ex in self.execution_history if ex.task_id == task_id]),
                'success_rate': self._calculate_success_rate(task_id)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting task status for {task_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get overall scheduler status and metrics"""        try:
            # Update metrics
            self._update_metrics()
            
            return {
                'is_running': self.is_running,
                'total_tasks': len(self.task_configurations),
                'active_tasks': len([t for t in self.task_configurations.values() if t.enabled]),
                'queue_length': self.task_queue.size(),
                'active_executions': len(self.active_executions),
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'resource_usage': self.current_resource_usage.copy(),
                'resource_limits': self.resource_limits.copy(),
                'metrics': {
                    'total_tasks_scheduled': self.metrics.total_tasks_scheduled,
                    'tasks_completed': self.metrics.tasks_completed,
                    'tasks_failed': self.metrics.tasks_failed,
                    'tasks_cancelled': self.metrics.tasks_cancelled,
                    'average_execution_time': self.metrics.average_execution_time,
                    'success_rate': self._calculate_overall_success_rate()
                },
                'scheduled_tasks': list(self.scheduled_tasks.keys()),
                'dependencies_pending': len([
                    task_id for task_id, deps in self.dependency_graph.items()
                    if not all(dep in self.completed_tasks for dep in deps)
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting scheduler status: {str(e)}")
            return {'error': str(e)}
    
    def add_task_callback(self, event: str, callback: Callable):
        """        Add callback for task events.
        
        Args:
            event: Event type (on_task_start, on_task_complete, on_task_fail, on_task_retry)
            callback: Callback function
        """        if event in self.task_callbacks:
            self.task_callbacks[event].append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event}")
    
    def remove_task_callback(self, event: str, callback: Callable):
        """Remove callback for task events"""        if event in self.task_callbacks and callback in self.task_callbacks[event]:
            self.task_callbacks[event].remove(callback)
    
    def update_resource_limits(self, limits: Dict[str, Union[int, float]]):
        """Update resource limits"""        try:
            for key, value in limits.items():
                if key in self.resource_limits:
                    self.resource_limits[key] = value
                    self.logger.info(f"Updated resource limit {key}: {value}")
                else:
                    self.logger.warning(f"Unknown resource limit: {key}")
                    
        except Exception as e:
            self.logger.error(f"Error updating resource limits: {str(e)}")
    
    def get_task_analytics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get task execution analytics"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # Filter executions within time range
            relevant_executions = [
                ex for ex in self.execution_history
                if ex.start_time and ex.start_time >= cutoff_time
            ]
            
            if not relevant_executions:
                return {'message': 'No executions in specified time range'}
            
            # Calculate analytics
            total_executions = len(relevant_executions)
            successful_executions = len([ex for ex in relevant_executions if ex.status == TaskStatus.COMPLETED])
            failed_executions = len([ex for ex in relevant_executions if ex.status == TaskStatus.FAILED])
            
            # Calculate durations
            durations = [ex.duration for ex in relevant_executions if ex.duration]
            avg_duration = sum(durations) / len(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            
            # Platform analytics
            platform_stats = defaultdict(lambda: {'total': 0, 'successful': 0, 'failed': 0})
            for ex in relevant_executions:
                if ex.task_id in self.task_configurations:
                    platform = self.task_configurations[ex.task_id].platform
                    platform_stats[platform]['total'] += 1
                    if ex.status == TaskStatus.COMPLETED:
                        platform_stats[platform]['successful'] += 1
                    elif ex.status == TaskStatus.FAILED:
                        platform_stats[platform]['failed'] += 1
            
            # Priority analytics
            priority_stats = defaultdict(lambda: {'total': 0, 'successful': 0, 'failed': 0})
            for ex in relevant_executions:
                if ex.task_id in self.task_configurations:
                    priority = self.task_configurations[ex.task_id].priority.name
                    priority_stats[priority]['total'] += 1
                    if ex.status == TaskStatus.COMPLETED:
                        priority_stats[priority]['successful'] += 1
                    elif ex.status == TaskStatus.FAILED:
                        priority_stats[priority]['failed'] += 1
            
            return {
                'time_range_hours': time_range_hours,
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'success_rate': (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                'duration_stats': {
                    'average': avg_duration,
                    'minimum': min_duration,
                    'maximum': max_duration
                },
                'platform_stats': dict(platform_stats),
                'priority_stats': dict(priority_stats),
                'hourly_distribution': self._get_hourly_distribution(relevant_executions)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting task analytics: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    def _validate_task_config(self, task_config: TaskConfiguration) -> bool:
        """Validate task configuration"""        try:
            # Basic validation
            if not task_config.task_id or not task_config.name:
                return False
            
            # Schedule validation
            if task_config.schedule_type == ScheduleType.CRON:
                if not task_config.schedule_expression:
                    return False
                try:
                    croniter(task_config.schedule_expression)
                except:
                    return False
            
            elif task_config.schedule_type == ScheduleType.INTERVAL:
                if not task_config.schedule_expression:
                    return False
                try:
                    int(task_config.schedule_expression)  # Should be seconds
                except:
                    return False
            
            elif task_config.schedule_type == ScheduleType.CONDITION:
                if not task_config.condition_callback:
                    return False
            
            # Dependency validation
            for dep in task_config.dependencies:
                if dep not in self.task_configurations:
                    self.logger.warning(f"Dependency {dep} not found for task {task_config.task_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating task config: {str(e)}")
            return False
    
    def _schedule_immediate_task(self, task_config: TaskConfiguration):
        """Schedule task for immediate execution"""        priority = self._calculate_task_priority(task_config)
        self.task_queue.push(task_config.task_id, priority)
    
    def _schedule_interval_task(self, task_config: TaskConfiguration):
        """Schedule interval-based task"""        try:
            interval_seconds = int(task_config.schedule_expression)
            
            async def interval_scheduler():
                while task_config.enabled and self.is_running:
                    try:
                        await asyncio.sleep(interval_seconds)
                        if task_config.enabled and await self._can_execute_task(task_config):
                            priority = self._calculate_task_priority(task_config)
                            self.task_queue.push(task_config.task_id, priority)
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        self.logger.error(f"Error in interval scheduler for {task_config.task_id}: {str(e)}")
            
            self.scheduled_tasks[task_config.task_id] = asyncio.create_task(interval_scheduler())
            
        except Exception as e:
            self.logger.error(f"Error scheduling interval task {task_config.task_id}: {str(e)}")
    
    def _schedule_cron_task(self, task_config: TaskConfiguration):
        """Schedule cron-based task"""        try:
            cron = croniter(task_config.schedule_expression, datetime.utcnow())
            self.cron_schedules[task_config.task_id] = cron
            
            async def cron_scheduler():
                while task_config.enabled and self.is_running:
                    try:
                        # Calculate time until next execution
                        next_run = cron.get_next(datetime)
                        wait_seconds = (next_run - datetime.utcnow()).total_seconds()
                        
                        if wait_seconds > 0:
                            await asyncio.sleep(wait_seconds)
                        
                        if task_config.enabled and await self._can_execute_task(task_config):
                            priority = self._calculate_task_priority(task_config)
                            self.task_queue.push(task_config.task_id, priority)
                            
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        self.logger.error(f"Error in cron scheduler for {task_config.task_id}: {str(e)}")
            
            self.scheduled_tasks[task_config.task_id] = asyncio.create_task(cron_scheduler())
            
        except Exception as e:
            self.logger.error(f"Error scheduling cron task {task_config.task_id}: {str(e)}")
    
    def _schedule_conditional_task(self, task_config: TaskConfiguration):
        """Schedule condition-based task"""        try:
            async def condition_scheduler():
                while task_config.enabled and self.is_running:
                    try:
                        # Check condition every minute
                        await asyncio.sleep(60)
                        
                        if (task_config.enabled and 
                            task_config.condition_callback and 
                            await task_config.condition_callback() and
                            await self._can_execute_task(task_config)):
                            
                            priority = self._calculate_task_priority(task_config)
                            self.task_queue.push(task_config.task_id, priority)
                            
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        self.logger.error(f"Error in condition scheduler for {task_config.task_id}: {str(e)}")
            
            self.scheduled_tasks[task_config.task_id] = asyncio.create_task(condition_scheduler())
            
        except Exception as e:
            self.logger.error(f"Error scheduling conditional task {task_config.task_id}: {str(e)}")
    
    def _calculate_task_priority(self, task_config: TaskConfiguration) -> float:
        """Calculate numeric priority for task (lower = higher priority)"""        base_priority = 6 - task_config.priority.value  # Invert so lower is better
        
        # Adjust based on various factors
        priority_adjustment = 0
        
        # Age-based priority boost
        age_hours = (datetime.utcnow() - task_config.created_at).total_seconds() / 3600
        priority_adjustment -= min(age_hours * 0.01, 1.0)  # Max 1.0 boost
        
        # Failure-based priority boost
        recent_failures = len([
            ex for ex in self.execution_history[-10:]
            if ex.task_id == task_config.task_id and ex.status == TaskStatus.FAILED
        ])
        priority_adjustment += recent_failures * 0.5  # Penalty for failures
        
        return base_priority + priority_adjustment
    
    async def _can_execute_task(self, task_config: TaskConfiguration) -> bool:
        """Check if task can be executed based on constraints"""        try:
            # Check if scheduler is running
            if not self.is_running:
                return False
            
            # Check if task is enabled
            if not task_config.enabled:
                return False
            
            # Check concurrent instances limit
            current_instances = len([
                ex for ex in self.active_executions.values()
                if ex.task_id == task_config.task_id and ex.status == TaskStatus.RUNNING
            ])
            
            if current_instances >= task_config.max_parallel_instances:
                return False
            
            # Check resource limits
            if not self._check_resource_availability(task_config):
                return False
            
            # Check dependencies
            if task_config.dependencies:
                if not all(dep in self.completed_tasks for dep in task_config.dependencies):
                    return False
            
            # Check global concurrent limit
            if len(self.active_executions) >= self.max_concurrent_tasks:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking task execution constraints: {str(e)}")
            return False
    
    def _check_resource_availability(self, task_config: TaskConfiguration) -> bool:
        """Check if resources are available for task execution"""        try:
            required_resources = task_config.resource_requirements
            
            for resource, required_amount in required_resources.items():
                if resource in self.resource_limits:
                    current_usage = self.current_resource_usage.get(resource, 0)
                    limit = self.resource_limits[resource]
                    
                    if current_usage + required_amount > limit:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking resource availability: {str(e)}")
            return False
    
    async def _execute_task(self, execution: TaskExecution, task_config: TaskConfiguration):
        """Execute a single task"""        try:
            execution.status = TaskStatus.RUNNING
            execution.start_time = datetime.utcnow()
            
            # Call task start callbacks
            for callback in self.task_callbacks['on_task_start']:
                try:
                    await callback(execution, task_config)
                except Exception as e:
                    self.logger.error(f"Error in task start callback: {str(e)}")
            
            # Update resource usage
            self._update_resource_usage(task_config.resource_requirements, increment=True)
            
            # Simulate task execution (replace with actual crawler execution)
            await self._run_crawler_task(execution, task_config)
            
            # Mark as completed
            execution.status = TaskStatus.COMPLETED
            execution.end_time = datetime.utcnow()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            
            # Mark task as completed for dependency resolution
            self.completed_tasks.add(task_config.task_id)
            
            # Update metrics
            self.metrics.tasks_completed += 1
            
            # Call completion callbacks
            for callback in self.task_callbacks['on_task_complete']:
                try:
                    await callback(execution, task_config)
                except Exception as e:
                    self.logger.error(f"Error in task complete callback: {str(e)}")
            
            self.logger.info(f"Task completed: {task_config.name} ({execution.execution_id})")
            
        except Exception as e:
            # Handle task failure
            execution.status = TaskStatus.FAILED
            execution.end_time = datetime.utcnow()
            execution.error = str(e)
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            
            # Update metrics
            self.metrics.tasks_failed += 1
            
            # Check if we should retry
            if execution.retry_attempt < task_config.retry_count:
                execution.status = TaskStatus.RETRYING
                execution.retry_attempt += 1
                
                # Schedule retry
                await asyncio.sleep(task_config.retry_delay)
                asyncio.create_task(self._execute_task(execution, task_config))
                
                # Call retry callbacks
                for callback in self.task_callbacks['on_task_retry']:
                    try:
                        await callback(execution, task_config)
                    except Exception as e:
                        self.logger.error(f"Error in task retry callback: {str(e)}")
                
                self.logger.warning(f"Retrying task: {task_config.name} (attempt {execution.retry_attempt})")
            else:
                # Call failure callbacks
                for callback in self.task_callbacks['on_task_fail']:
                    try:
                        await callback(execution, task_config)
                    except Exception as e:
                        self.logger.error(f"Error in task fail callback: {str(e)}")
                
                self.logger.error(f"Task failed: {task_config.name} ({execution.execution_id}) - {str(e)}")
        
        finally:
            # Update resource usage
            self._update_resource_usage(task_config.resource_requirements, increment=False)
            
            # Move from active to history
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            self.execution_history.append(execution)
            
            # Keep history limited
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-800:]  # Keep 800 most recent
    
    async def _run_crawler_task(self, execution: TaskExecution, task_config: TaskConfiguration):
        """Execute the actual crawler task"""        try:
            # This would integrate with the actual crawler implementations
            # For now, simulate with a delay
            
            execution.logs.append(f"Starting {task_config.crawler_type} crawler for {task_config.platform}")
            
            # Simulate different task durations based on platform
            base_duration = {
                'youtube': 30,
                'twitter': 20,
                'facebook': 25,
                'instagram': 15,
                'tiktok': 10,
                'spotify': 5
            }.get(task_config.platform.lower(), 10)
            
            # Add some randomness
            import random
            duration = base_duration + random.randint(-5, 15)
            
            execution.logs.append(f"Estimated duration: {duration} seconds")
            
            # Simulate task execution with progress updates
            for i in range(duration):
                if execution.status != TaskStatus.RUNNING:
                    break
                
                await asyncio.sleep(1)
                
                # Add some progress logs
                if i % 10 == 0:
                    execution.logs.append(f"Progress: {i}/{duration} seconds")
            
            # Simulate results
            execution.result = {
                'items_found': random.randint(10, 100),
                'matches_detected': random.randint(0, 10),
                'pages_crawled': random.randint(5, 50),
                'execution_time': duration
            }
            
            execution.logs.append(f"Completed successfully: {execution.result}")
            
        except Exception as e:
            execution.logs.append(f"Error during execution: {str(e)}")
            raise
    
    def _update_resource_usage(self, resource_requirements: Dict[str, Any], increment: bool):
        """Update current resource usage"""        try:
            multiplier = 1 if increment else -1
            
            for resource, amount in resource_requirements.items():
                if resource in self.current_resource_usage:
                    self.current_resource_usage[resource] += amount * multiplier
                    self.current_resource_usage[resource] = max(0, self.current_resource_usage[resource])
            
            # Update concurrent crawlers count
            if increment:
                self.current_resource_usage['concurrent_crawlers'] += 1
            else:
                self.current_resource_usage['concurrent_crawlers'] = max(
                    0, self.current_resource_usage['concurrent_crawlers'] - 1
                )
                
        except Exception as e:
            self.logger.error(f"Error updating resource usage: {str(e)}")
    
    async def _scheduler_loop(self):
        """Main scheduler loop for processing queued tasks"""        try:
            while self.is_running:
                try:
                    # Process queued tasks
                    while self.task_queue.size() > 0 and len(self.active_executions) < self.max_concurrent_tasks:
                        task_id = self.task_queue.pop()
                        
                        if task_id in self.task_configurations:
                            task_config = self.task_configurations[task_id]
                            
                            if await self._can_execute_task(task_config):
                                execution_id = str(uuid.uuid4())
                                execution = TaskExecution(
                                    execution_id=execution_id,
                                    task_id=task_id,
                                    status=TaskStatus.PENDING
                                )
                                
                                self.active_executions[execution_id] = execution
                                
                                # Execute task asynchronously
                                asyncio.create_task(self._execute_task(execution, task_config))
                                
                                # Update metrics
                                self.metrics.total_tasks_scheduled += 1
                    
                    await asyncio.sleep(1)  # Check every second
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in scheduler loop: {str(e)}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            self.logger.error(f"Fatal error in scheduler loop: {str(e)}")
    
    async def _monitor_loop(self):
        """Monitor loop for metrics and health checks"""        try:
            while self.is_running:
                try:
                    # Update metrics
                    self._update_metrics()
                    
                    # Check for stuck tasks
                    current_time = datetime.utcnow()
                    for execution in list(self.active_executions.values()):
                        if (execution.start_time and 
                            (current_time - execution.start_time).total_seconds() > 
                            self.task_configurations.get(execution.task_id, TaskConfiguration("", "", "", "")).timeout):
                            
                            # Cancel stuck task
                            execution.status = TaskStatus.FAILED
                            execution.error = "Task timeout"
                            execution.end_time = current_time
                            
                            self.logger.warning(f"Task timed out: {execution.execution_id}")
                    
                    await asyncio.sleep(60)  # Monitor every minute
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in monitor loop: {str(e)}")
                    await asyncio.sleep(30)
                    
        except Exception as e:
            self.logger.error(f"Fatal error in monitor loop: {str(e)}")
    
    def _update_metrics(self):
        """Update scheduler metrics"""        try:
            self.metrics.queue_length = self.task_queue.size()
            self.metrics.active_executions = len(self.active_executions)
            self.metrics.resource_utilization = self.current_resource_usage.copy()
            self.metrics.last_updated = datetime.utcnow()
            
            # Calculate average execution time
            recent_executions = [
                ex for ex in self.execution_history[-100:]
                if ex.duration is not None
            ]
            
            if recent_executions:
                total_duration = sum(ex.duration for ex in recent_executions)
                self.metrics.average_execution_time = total_duration / len(recent_executions)
                
        except Exception as e:
            self.logger.error(f"Error updating metrics: {str(e)}")
    
    def _calculate_success_rate(self, task_id: str) -> float:
        """Calculate success rate for a specific task"""        try:
            task_executions = [ex for ex in self.execution_history if ex.task_id == task_id]
            
            if not task_executions:
                return 0.0
            
            successful = len([ex for ex in task_executions if ex.status == TaskStatus.COMPLETED])
            return (successful / len(task_executions)) * 100
            
        except Exception as e:
            self.logger.error(f"Error calculating success rate: {str(e)}")
            return 0.0
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate"""        try:
            if not self.execution_history:
                return 0.0
            
            successful = len([ex for ex in self.execution_history if ex.status == TaskStatus.COMPLETED])
            return (successful / len(self.execution_history)) * 100
            
        except Exception as e:
            self.logger.error(f"Error calculating overall success rate: {str(e)}")
            return 0.0
    
    def _get_hourly_distribution(self, executions: List[TaskExecution]) -> Dict[int, int]:
        """Get hourly distribution of executions"""        try:
            hourly_dist = defaultdict(int)
            
            for execution in executions:
                if execution.start_time:
                    hour = execution.start_time.hour
                    hourly_dist[hour] += 1
            
            return dict(hourly_dist)
            
        except Exception as e:
            self.logger.error(f"Error getting hourly distribution: {str(e)}")
            return {}
