"""Task Management and Scheduling for Copyright Enforcement
Professional task orchestration, job queuing, and workflow management
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod
import heapq
from collections import defaultdict
import traceback

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    PAUSED = "paused"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class TaskType(Enum):
    """Types of enforcement tasks"""
    CONTENT_ANALYSIS = "content_analysis"
    PLATFORM_MONITORING = "platform_monitoring"
    EVIDENCE_COLLECTION = "evidence_collection"
    TAKEDOWN_REQUEST = "takedown_request"
    DMCA_SUBMISSION = "dmca_submission"
    ESCALATION_PROCESSING = "escalation_processing"
    REPORT_GENERATION = "report_generation"
    NOTIFICATION_DELIVERY = "notification_delivery"
    LEGAL_DOCUMENT_GENERATION = "legal_document_generation"
    PAYMENT_PROCESSING = "payment_processing"
    COMPLIANCE_CHECK = "compliance_check"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    HEALTH_CHECK = "health_check"
    CLEANUP = "cleanup"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    STARTED = "started"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: Optional[datetime] = None


@dataclass
class TaskConfig:
    """Task configuration"""
    max_retries: int = 3
    retry_delay: float = 5.0
    timeout: Optional[float] = None
    depends_on: List[str] = field(default_factory=list)
    retry_backoff: float = 2.0
    max_retry_delay: float = 300.0
    failure_threshold: float = 0.8
    
    # Resource requirements
    memory_limit_mb: Optional[int] = None
    cpu_limit: Optional[float] = None
    
    # Scheduling
    schedule_after: Optional[datetime] = None
    schedule_before: Optional[datetime] = None
    
    # Notifications
    notify_on_completion: bool = False
    notify_on_failure: bool = True
    notification_channels: List[str] = field(default_factory=list)


class Task:
    """Individual task in the enforcement system"""
    
    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        config: Optional[TaskConfig] = None
    ):
        self.id = task_id
        self.type = task_type
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.config = config or TaskConfig()
        
        # State tracking
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.last_retry_at: Optional[datetime] = None
        
        # Execution tracking
        self.retry_count = 0
        self.execution_time: Optional[float] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.traceback: Optional[str] = None
        
        # Metadata
        self.metadata: Dict[str, Any] = {}
        self.tags: Set[str] = set()
        
        # Dependencies
        self.dependencies: Set[str] = set(self.config.depends_on)
        self.dependents: Set[str] = set()
        
        # Progress tracking
        self.progress_percentage: float = 0.0
        self.progress_message: str = ""
    
    def __lt__(self, other):
        """Compare tasks for priority queue"""
        if not isinstance(other, Task):
            return NotImplemented
        
        # Higher priority value = higher priority
        # If same priority, use creation time (FIFO)
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        return self.created_at < other.created_at
    
    def can_execute(self, completed_tasks: Set[str]) -> bool:
        """Check if task can be executed based on dependencies"""
        return self.dependencies.issubset(completed_tasks)
    
    def add_dependency(self, task_id: str):
        """Add task dependency"""
        self.dependencies.add(task_id)
    
    def add_dependent(self, task_id: str):
        """Add dependent task"""
        self.dependents.add(task_id)
    
    def add_tag(self, tag: str):
        """Add tag to task"""
        self.tags.add(tag)
    
    def update_progress(self, percentage: float, message: str = ""):
        """Update task progress"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        self.progress_message = message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'status': self.status.value,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retry_count': self.retry_count,
            'execution_time': self.execution_time,
            'progress_percentage': self.progress_percentage,
            'progress_message': self.progress_message,
            'metadata': self.metadata,
            'tags': list(self.tags),
            'dependencies': list(self.dependencies),
            'dependents': list(self.dependents),
            'error': self.error
        }


class TaskQueue:
    """Priority-based task queue"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self._queue: List[Task] = []
        self._task_map: Dict[str, Task] = {}
        self._lock = asyncio.Lock()
        
    async def put(self, task: Task):
        """Add task to queue"""
        async with self._lock:
            if task.id in self._task_map:
                raise ValueError(f"Task {task.id} already exists in queue")
            
            heapq.heappush(self._queue, task)
            self._task_map[task.id] = task
            task.status = TaskStatus.QUEUED
            
            logger.debug(f"Task {task.id} added to queue {self.name}")
    
    async def get(self) -> Optional[Task]:
        """Get highest priority task from queue"""
        async with self._lock:
            while self._queue:
                task = heapq.heappop(self._queue)
                
                # Check if task is still valid
                if task.id in self._task_map and task.status == TaskStatus.QUEUED:
                    del self._task_map[task.id]
                    return task
                
                # Remove invalid tasks
                self._task_map.pop(task.id, None)
            
            return None
    
    async def remove(self, task_id: str) -> bool:
        """Remove task from queue"""
        async with self._lock:
            task = self._task_map.get(task_id)
            if not task:
                return False
            
            # Mark as cancelled
            task.status = TaskStatus.CANCELLED
            del self._task_map[task_id]
            
            # Note: Task remains in heap but will be filtered out in get()
            logger.debug(f"Task {task_id} removed from queue {self.name}")
            return True
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        async with self._lock:
            return self._task_map.get(task_id)
    
    async def size(self) -> int:
        """Get queue size"""
        async with self._lock:
            return len(self._task_map)
    
    async def is_empty(self) -> bool:
        """Check if queue is empty"""
        return await self.size() == 0
    
    async def clear(self):
        """Clear all tasks from queue"""
        async with self._lock:
            self._queue.clear()
            self._task_map.clear()
            logger.info(f"Queue {self.name} cleared")


class WorkflowStep:
    """Single step in a workflow"""
    
    def __init__(
        self,
        step_id: str,
        task_type: TaskType,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        depends_on: List[str] = None,
        condition: Optional[Callable] = None,
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None
    ):
        self.id = step_id
        self.task_type = task_type
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.depends_on = depends_on or []
        self.condition = condition
        self.on_success = on_success
        self.on_failure = on_failure
        
        # State
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    def should_execute(self, workflow_context: Dict[str, Any]) -> bool:
        """Check if step should be executed based on condition"""
        if not self.condition:
            return True
        
        try:
            return self.condition(workflow_context)
        except Exception as e:
            logger.error(f"Error evaluating condition for step {self.id}: {e}")
            return False


class Workflow:
    """Workflow definition and execution"""
    
    def __init__(self, workflow_id: str, name: str, description: str = ""):
        self.id = workflow_id
        self.name = name
        self.description = description
        self.steps: Dict[str, WorkflowStep] = {}
        self.step_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Execution state
        self.status = WorkflowStatus.CREATED
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        # Context and results
        self.context: Dict[str, Any] = {}
        self.step_results: Dict[str, Any] = {}
        self.failed_steps: Set[str] = set()
        
        # Configuration
        self.max_parallel_steps = 5
        self.failure_tolerance = 0.8  # 80% success rate required
        self.timeout: Optional[float] = None
    
    def add_step(self, step: WorkflowStep):
        """Add step to workflow"""
        self.steps[step.id] = step
        
        # Build dependency graph
        for dependency in step.depends_on:
            self.step_dependencies[step.id].add(dependency)
    
    def get_executable_steps(self, completed_steps: Set[str]) -> List[WorkflowStep]:
        """Get steps that can be executed now"""
        executable = []
        
        for step_id, step in self.steps.items():
            if (step.status == TaskStatus.PENDING and
                self.step_dependencies[step_id].issubset(completed_steps) and
                step.should_execute(self.context)):
                executable.append(step)
        
        return executable
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        pending_steps = [s for s in self.steps.values() if s.status == TaskStatus.PENDING]
        return len(pending_steps) == 0
    
    def calculate_success_rate(self) -> float:
        """Calculate workflow success rate"""
        if not self.steps:
            return 1.0
        
        completed_steps = [s for s in self.steps.values() if s.status == TaskStatus.COMPLETED]
        return len(completed_steps) / len(self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'steps': {step_id: {
                'id': step.id,
                'task_type': step.task_type.value,
                'status': step.status.value,
                'depends_on': step.depends_on,
                'started_at': step.started_at.isoformat() if step.started_at else None,
                'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                'error': step.error
            } for step_id, step in self.steps.items()},
            'context': self.context,
            'success_rate': self.calculate_success_rate(),
            'failed_steps': list(self.failed_steps)
        }


class TaskExecutor:
    """Task execution engine"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.worker_semaphore = asyncio.Semaphore(max_workers)
        self._shutdown = False
        
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a single task"""
        task_result = TaskResult(
            task_id=task.id,
            status=TaskStatus.RUNNING
        )
        
        async with self.worker_semaphore:
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                
                start_time = asyncio.get_event_loop().time()
                
                # Execute task with timeout
                if task.config.timeout:
                    result = await asyncio.wait_for(
                        task.func(*task.args, **task.kwargs),
                        timeout=task.config.timeout
                    )
                else:
                    result = await task.func(*task.args, **task.kwargs)
                
                end_time = asyncio.get_event_loop().time()
                execution_time = end_time - start_time
                
                # Success
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.execution_time = execution_time
                task.result = result
                
                task_result.status = TaskStatus.COMPLETED
                task_result.result = result
                task_result.execution_time = execution_time
                task_result.completed_at = task.completed_at
                
                logger.info(f"Task {task.id} completed successfully in {execution_time:.2f}s")
                
            except asyncio.TimeoutError:
                error_msg = f"Task {task.id} timed out after {task.config.timeout}s"
                task.status = TaskStatus.FAILED
                task.error = error_msg
                task_result.status = TaskStatus.FAILED
                task_result.error = error_msg
                logger.error(error_msg)
                
            except Exception as e:
                error_msg = str(e)
                task.status = TaskStatus.FAILED
                task.error = error_msg
                task.traceback = traceback.format_exc()
                task_result.status = TaskStatus.FAILED
                task_result.error = error_msg
                logger.error(f"Task {task.id} failed: {error_msg}")
        
        # Store result
        self.task_results[task.id] = task_result
        
        return task_result
    
    async def execute_with_retry(self, task: Task) -> TaskResult:
        """Execute task with retry logic"""
        last_result = None
        
        for attempt in range(task.config.max_retries + 1):
            if self._shutdown:
                break
            
            if attempt > 0:
                # Calculate retry delay with exponential backoff
                delay = min(
                    task.config.retry_delay * (task.config.retry_backoff ** (attempt - 1)),
                    task.config.max_retry_delay
                )
                
                logger.info(f"Retrying task {task.id} (attempt {attempt + 1}) after {delay}s")
                await asyncio.sleep(delay)
                
                task.status = TaskStatus.RETRYING
                task.retry_count = attempt
                task.last_retry_at = datetime.utcnow()
            
            last_result = await self.execute_task(task)
            
            if last_result.status == TaskStatus.COMPLETED:
                break
        
        return last_result
    
    async def shutdown(self):
        """Shutdown executor"""
        self._shutdown = True
        
        # Cancel running tasks
        for task_id, task_coroutine in self.running_tasks.items():
            task_coroutine.cancel()
            logger.info(f"Cancelled running task {task_id}")
        
        # Wait for tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        self.running_tasks.clear()
        logger.info("Task executor shutdown complete")


class WorkflowEngine:
    """Workflow execution engine"""
    
    def __init__(self, task_executor: TaskExecutor):
        self.task_executor = task_executor
        self.running_workflows: Dict[str, Workflow] = {}
        self.workflow_results: Dict[str, Dict[str, Any]] = {}
    
    async def execute_workflow(self, workflow: Workflow) -> Dict[str, Any]:
        """Execute a complete workflow"""
        try:
            workflow.status = WorkflowStatus.STARTED
            workflow.started_at = datetime.utcnow()
            self.running_workflows[workflow.id] = workflow
            
            logger.info(f"Starting workflow {workflow.id}: {workflow.name}")
            
            completed_steps: Set[str] = set()
            running_tasks: Dict[str, asyncio.Task] = {}
            
            while not workflow.is_complete() and not self.task_executor._shutdown:
                # Get executable steps
                executable_steps = workflow.get_executable_steps(completed_steps)
                
                # Start new tasks (respect parallel limit)
                available_slots = workflow.max_parallel_steps - len(running_tasks)
                for step in executable_steps[:available_slots]:
                    step.status = TaskStatus.RUNNING
                    step.started_at = datetime.utcnow()
                    
                    # Create task from step
                    task = Task(
                        task_id=f"{workflow.id}_{step.id}",
                        task_type=step.task_type,
                        func=step.func,
                        args=step.args,
                        kwargs=step.kwargs
                    )
                    
                    # Execute task
                    task_coroutine = asyncio.create_task(
                        self.task_executor.execute_with_retry(task)
                    )
                    running_tasks[step.id] = task_coroutine
                
                # Wait for any task to complete
                if running_tasks:
                    done, pending = await asyncio.wait(
                        running_tasks.values(),
                        return_when=asyncio.FIRST_COMPLETED,
                        timeout=1.0  # Check for new tasks every second
                    )
                    
                    # Process completed tasks
                    for completed_task in done:
                        step_id = None
                        for sid, task_coro in running_tasks.items():
                            if task_coro == completed_task:
                                step_id = sid
                                break
                        
                        if step_id:
                            step = workflow.steps[step_id]
                            try:
                                result = await completed_task
                                
                                if result.status == TaskStatus.COMPLETED:
                                    step.status = TaskStatus.COMPLETED
                                    step.result = result.result
                                    step.completed_at = datetime.utcnow()
                                    completed_steps.add(step_id)
                                    workflow.step_results[step_id] = result.result
                                    
                                    # Execute success callback
                                    if step.on_success:
                                        try:
                                            await step.on_success(workflow.context, result.result)
                                        except Exception as e:
                                            logger.error(f"Success callback failed for step {step_id}: {e}")
                                    
                                    logger.info(f"Workflow {workflow.id} step {step_id} completed")
                                    
                                else:
                                    step.status = TaskStatus.FAILED
                                    step.error = result.error
                                    step.completed_at = datetime.utcnow()
                                    workflow.failed_steps.add(step_id)
                                    
                                    # Execute failure callback
                                    if step.on_failure:
                                        try:
                                            await step.on_failure(workflow.context, result.error)
                                        except Exception as e:
                                            logger.error(f"Failure callback failed for step {step_id}: {e}")
                                    
                                    logger.error(f"Workflow {workflow.id} step {step_id} failed: {result.error}")
                                
                            except Exception as e:
                                step.status = TaskStatus.FAILED
                                step.error = str(e)
                                step.completed_at = datetime.utcnow()
                                workflow.failed_steps.add(step_id)
                                logger.error(f"Workflow {workflow.id} step {step_id} failed: {e}")
                            
                            # Remove from running tasks
                            del running_tasks[step_id]
                
                # Check failure tolerance
                if workflow.calculate_success_rate() < workflow.failure_tolerance:
                    workflow.status = WorkflowStatus.FAILED
                    logger.error(f"Workflow {workflow.id} failed: success rate below tolerance")
                    break
                
                # Small delay to prevent busy waiting
                if not executable_steps and running_tasks:
                    await asyncio.sleep(0.1)
            
            # Determine final status
            if workflow.is_complete():
                if len(workflow.failed_steps) == 0:
                    workflow.status = WorkflowStatus.COMPLETED
                else:
                    success_rate = workflow.calculate_success_rate()
                    if success_rate >= workflow.failure_tolerance:
                        workflow.status = WorkflowStatus.COMPLETED
                    else:
                        workflow.status = WorkflowStatus.FAILED
            
            workflow.completed_at = datetime.utcnow()
            
            # Generate workflow result
            result = {
                'workflow_id': workflow.id,
                'status': workflow.status.value,
                'success_rate': workflow.calculate_success_rate(),
                'total_steps': len(workflow.steps),
                'completed_steps': len([s for s in workflow.steps.values() if s.status == TaskStatus.COMPLETED]),
                'failed_steps': len(workflow.failed_steps),
                'execution_time': (workflow.completed_at - workflow.started_at).total_seconds(),
                'step_results': workflow.step_results,
                'context': workflow.context
            }
            
            self.workflow_results[workflow.id] = result
            
            logger.info(f"Workflow {workflow.id} completed with status {workflow.status.value}")
            
            return result
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            logger.error(f"Workflow {workflow.id} execution failed: {e}")
            
            return {
                'workflow_id': workflow.id,
                'status': WorkflowStatus.FAILED.value,
                'error': str(e),
                'execution_time': (workflow.completed_at - workflow.started_at).total_seconds() if workflow.started_at else 0
            }
        
        finally:
            # Cleanup
            self.running_workflows.pop(workflow.id, None)


class TaskScheduler:
    """Task scheduling and queue management"""
    
    def __init__(self, task_executor: TaskExecutor, max_queues: int = 10):
        self.task_executor = task_executor
        self.queues: Dict[str, TaskQueue] = {}
        self.max_queues = max_queues
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        self._shutdown = False
        
        # Default queue
        self.default_queue = TaskQueue("default")
        self.queues["default"] = self.default_queue
        
        # Worker task
        self.worker_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the task scheduler"""
        if self.worker_task:
            return
        
        self.worker_task = asyncio.create_task(self._worker_loop())
        logger.info("Task scheduler started")
    
    async def stop(self):
        """Stop the task scheduler"""
        self._shutdown = True
        
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
            self.worker_task = None
        
        # Cancel scheduled tasks
        for task_id, scheduled_task in self.scheduled_tasks.items():
            scheduled_task.cancel()
            logger.info(f"Cancelled scheduled task {task_id}")
        
        await self.task_executor.shutdown()
        
        logger.info("Task scheduler stopped")
    
    async def _worker_loop(self):
        """Main worker loop"""
        while not self._shutdown:
            try:
                # Process all queues
                for queue_name, queue in self.queues.items():
                    if await queue.is_empty():
                        continue
                    
                    # Get task from queue
                    task = await queue.get()
                    if not task:
                        continue
                    
                    # Check dependencies
                    completed_task_ids = set(
                        task_id for task_id, result in self.task_executor.task_results.items()
                        if result.status == TaskStatus.COMPLETED
                    )
                    
                    if not task.can_execute(completed_task_ids):
                        # Re-queue task
                        await queue.put(task)
                        continue
                    
                    # Execute task
                    execution_task = asyncio.create_task(
                        self.task_executor.execute_with_retry(task)
                    )
                    self.scheduled_tasks[task.id] = execution_task
                    
                    logger.debug(f"Started execution of task {task.id} from queue {queue_name}")
                
                # Clean up completed tasks
                completed_task_ids = []
                for task_id, scheduled_task in self.scheduled_tasks.items():
                    if scheduled_task.done():
                        completed_task_ids.append(task_id)
                
                for task_id in completed_task_ids:
                    del self.scheduled_tasks[task_id]
                
                # Wait before next iteration
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(1.0)
    
    async def submit_task(
        self,
        task_type: TaskType,
        func: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        queue_name: str = "default",
        config: Optional[TaskConfig] = None,
        task_id: Optional[str] = None
    ) -> str:
        """Submit task for execution"""
        if not task_id:
            task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            config=config or TaskConfig()
        )
        
        # Get or create queue
        queue = await self.get_or_create_queue(queue_name)
        
        # Add task to queue
        await queue.put(task)
        
        logger.info(f"Task {task_id} submitted to queue {queue_name}")
        
        return task_id
    
    async def get_or_create_queue(self, queue_name: str) -> TaskQueue:
        """Get existing queue or create new one"""
        if queue_name not in self.queues:
            if len(self.queues) >= self.max_queues:
                raise ValueError(f"Maximum number of queues ({self.max_queues}) reached")
            
            self.queues[queue_name] = TaskQueue(queue_name)
            logger.info(f"Created new queue: {queue_name}")
        
        return self.queues[queue_name]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        # Check if task is scheduled
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].cancel()
            del self.scheduled_tasks[task_id]
            logger.info(f"Cancelled running task {task_id}")
            return True
        
        # Check all queues
        for queue in self.queues.values():
            if await queue.remove(task_id):
                logger.info(f"Cancelled queued task {task_id}")
                return True
        
        return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        # Check task results
        if task_id in self.task_executor.task_results:
            result = self.task_executor.task_results[task_id]
            return {
                'task_id': task_id,
                'status': result.status.value,
                'result': result.result,
                'error': result.error,
                'execution_time': result.execution_time,
                'retry_count': result.retry_count,
                'completed_at': result.completed_at.isoformat() if result.completed_at else None
            }
        
        # Check running tasks
        if task_id in self.scheduled_tasks:
            return {
                'task_id': task_id,
                'status': TaskStatus.RUNNING.value
            }
        
        # Check queues
        for queue_name, queue in self.queues.items():
            task = await queue.get_task(task_id)
            if task:
                return {
                    'task_id': task_id,
                    'status': task.status.value,
                    'queue': queue_name,
                    'priority': task.priority.value,
                    'created_at': task.created_at.isoformat(),
                    'progress_percentage': task.progress_percentage,
                    'progress_message': task.progress_message
                }
        
        return None
    
    async def get_queue_status(self, queue_name: str = None) -> Dict[str, Any]:
        """Get queue status"""
        if queue_name:
            queue = self.queues.get(queue_name)
            if not queue:
                return {}
            
            return {
                'name': queue.name,
                'size': await queue.size(),
                'is_empty': await queue.is_empty()
            }
        
        # All queues
        status = {
            'total_queues': len(self.queues),
            'running_tasks': len(self.scheduled_tasks),
            'queues': {}
        }
        
        for name, queue in self.queues.items():
            status['queues'][name] = {
                'name': name,
                'size': await queue.size(),
                'is_empty': await queue.is_empty()
            }
        
        return status


# Global instances
task_executor = TaskExecutor()
task_scheduler = TaskScheduler(task_executor)
workflow_engine = WorkflowEngine(task_executor)


async def get_task_scheduler() -> TaskScheduler:
    """Get the global task scheduler instance"""
    return task_scheduler


async def get_workflow_engine() -> WorkflowEngine:
    """Get the global workflow engine instance"""
    return workflow_engine


__all__ = [
    'Task',
    'TaskQueue',
    'TaskExecutor',
    'TaskScheduler',
    'Workflow',
    'WorkflowStep',
    'WorkflowEngine',
    'TaskStatus',
    'TaskPriority',
    'TaskType',
    'TaskConfig',
    'TaskResult',
    'WorkflowStatus',
    'get_task_scheduler',
    'get_workflow_engine'
]
