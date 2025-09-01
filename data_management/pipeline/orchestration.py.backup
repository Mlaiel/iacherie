"""Pipeline Orchestration Module
Author: Fahed Mlaiel <mlaiel@live.de>

Advanced workflow orchestration systems for complex data pipeline management
with intelligent scheduling, dependency resolution, distributed execution,
and specialized creator content workflows supporting the complete monetization pipeline:

Creator Workflow: Upload → AI Protection → SEO Optimization → Platform Distribution → Monetization Tracking
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue

# Workflow and scheduling
import croniter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor as APSThreadPoolExecutor

# Creator-specific integrations
import requests
from datetime import timezone

from ..core.exceptions import OrchestrationError, DependencyError, SchedulingError
from ..core.metrics import MetricsCollector
from ..core.config import OrchestrationConfig
from ..utils.decorators import monitor_performance, retry_on_failure
from ..utils.state_manager import StateManager


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskStatus(Enum):
    """Individual task status."""
    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class DependencyType(Enum):
    """Dependency relationship types."""
    SEQUENTIAL = "sequential"  # Must complete before next starts
    PARALLEL = "parallel"     # Can run concurrently
    CONDITIONAL = "conditional"  # Depends on condition/result
    TRIGGER = "trigger"       # Triggers next task on completion


class CreatorWorkflowType(Enum):
    """Creator-specific workflow types."""
    CONTENT_UPLOAD = "content_upload"
    PROTECTION_PIPELINE = "protection_pipeline"
    SEO_OPTIMIZATION = "seo_optimization"
    PLATFORM_DISTRIBUTION = "platform_distribution"
    MONETIZATION_TRACKING = "monetization_tracking"
    COLLABORATION_MATCHING = "collaboration_matching"
    BRAND_PARTNERSHIP = "brand_partnership"
    ANALYTICS_REPORTING = "analytics_reporting"


@dataclass
class Task:
    """Workflow task definition."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    function: Optional[Callable] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.SEQUENTIAL
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 1
    status: TaskStatus = TaskStatus.WAITING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorWorkflow:
    """Creator-specific workflow definition with monetization pipeline."""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    creator_type: str = ""  # musician, blogger, photographer, influencer, comedian
    workflow_type: CreatorWorkflowType = CreatorWorkflowType.CONTENT_UPLOAD
    tasks: List[Task] = field(default_factory=list)
    schedule: Optional[str] = None  # Cron expression
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    target_platforms: List[str] = field(default_factory=list)
    monetization_goals: Dict[str, Any] = field(default_factory=dict)
    protection_level: str = "enterprise"
    collaboration_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Complete workflow definition."""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tasks: List[Task] = field(default_factory=list)
    schedule: Optional[str] = None  # Cron expression
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    tags: List[str] = field(default_factory=list)


class WorkflowOrchestrator:
    """
    Advanced workflow orchestration engine with intelligent scheduling,
    dynamic dependency resolution, and distributed execution capabilities.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("workflow_orchestrator")
        
        # Workflow storage and management
        self.workflows: Dict[str, Workflow] = {}
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # Dependency management
        self.dependency_graph = nx.DiGraph()
        self.state_manager = StateManager()
        
        # Execution infrastructure
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_workflows)
        self.task_executor = ThreadPoolExecutor(max_workers=config.max_concurrent_tasks)
        
        # Scheduling
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': APSThreadPoolExecutor(config.scheduler_thread_pool_size)},
            job_defaults={'coalesce': False, 'max_instances': 3}
        )
        
        self._initialize_orchestrator()
    
    def _initialize_orchestrator(self):
        """Initialize orchestrator components."""
        
        self.scheduler.start()
        self.logger.info("Workflow orchestrator initialized")
    
    @monitor_performance
    async def register_workflow(
        self,
        workflow: Workflow,
        auto_schedule: bool = True
    ) -> str:
        """
        Register a workflow for orchestration.
        
        Args:
            workflow: Workflow definition
            auto_schedule: Whether to automatically schedule if cron is provided
            
        Returns:
            Workflow ID
        """
        
        # Validate workflow
        await self._validate_workflow(workflow)
        
        # Build dependency graph
        await self._build_dependency_graph(workflow)
        
        # Store workflow
        self.workflows[workflow.workflow_id] = workflow
        
        # Schedule workflow if cron expression provided
        if workflow.schedule and auto_schedule:
            await self._schedule_workflow(workflow)
        
        self.metrics.increment('workflows_registered')
        self.logger.info(f"Workflow registered: {workflow.workflow_id} - {workflow.name}")
        
        return workflow.workflow_id
    
    async def _validate_workflow(self, workflow: Workflow):
        """Validate workflow definition."""
        
        if not workflow.name:
            raise OrchestrationError("Workflow name is required")
        
        if not workflow.tasks:
            raise OrchestrationError("Workflow must contain at least one task")
        
        # Validate task definitions
        task_ids = {task.task_id for task in workflow.tasks}
        
        for task in workflow.tasks:
            if not task.name:
                raise OrchestrationError(f"Task {task.task_id} must have a name")
            
            if not task.function:
                raise OrchestrationError(f"Task {task.task_id} must have a function")
            
            # Validate dependencies
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise DependencyError(f"Task {task.task_id} depends on non-existent task {dep_id}")
        
        # Check for circular dependencies
        await self._check_circular_dependencies(workflow.tasks)
    
    async def _check_circular_dependencies(self, tasks: List[Task]):
        """Check for circular dependencies in task list."""
        
        temp_graph = nx.DiGraph()
        
        for task in tasks:
            temp_graph.add_node(task.task_id)
            for dep_id in task.dependencies:
                temp_graph.add_edge(dep_id, task.task_id)
        
        if not nx.is_directed_acyclic_graph(temp_graph):
            raise DependencyError("Circular dependency detected in workflow")
    
    async def _build_dependency_graph(self, workflow: Workflow):
        """Build dependency graph for workflow."""
        
        workflow_graph_id = f"workflow_{workflow.workflow_id}"
        
        # Add nodes for all tasks
        for task in workflow.tasks:
            node_id = f"{workflow_graph_id}_{task.task_id}"
            self.dependency_graph.add_node(node_id, task=task)
        
        # Add edges for dependencies
        for task in workflow.tasks:
            task_node_id = f"{workflow_graph_id}_{task.task_id}"
            
            for dep_id in task.dependencies:
                dep_node_id = f"{workflow_graph_id}_{dep_id}"
                self.dependency_graph.add_edge(dep_node_id, task_node_id)
    
    async def _schedule_workflow(self, workflow: Workflow):
        """Schedule workflow using cron expression."""
        
        if not workflow.schedule:
            return
        
        try:
            # Validate cron expression
            croniter.croniter(workflow.schedule)
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self._execute_scheduled_workflow,
                trigger='cron',
                **self._parse_cron_expression(workflow.schedule),
                args=[workflow.workflow_id],
                id=f"workflow_{workflow.workflow_id}",
                name=f"Scheduled execution of {workflow.name}",
                misfire_grace_time=300
            )
            
            workflow.status = WorkflowStatus.SCHEDULED
            self.logger.info(f"Workflow {workflow.workflow_id} scheduled with cron: {workflow.schedule}")
            
        except Exception as e:
            raise SchedulingError(f"Failed to schedule workflow: {e}")
    
    def _parse_cron_expression(self, cron_expr: str) -> Dict[str, Any]:
        """Parse cron expression into scheduler parameters."""
        
        parts = cron_expr.split()
        if len(parts) != 5:
            raise SchedulingError("Invalid cron expression format")
        
        minute, hour, day, month, day_of_week = parts
        
        return {
            'minute': minute,
            'hour': hour,
            'day': day,
            'month': month,
            'day_of_week': day_of_week
        }
    
    async def _execute_scheduled_workflow(self, workflow_id: str):
        """Execute scheduled workflow."""
        
        try:
            await self.execute_workflow(workflow_id)
        except Exception as e:
            self.logger.error(f"Scheduled workflow execution failed: {e}")
    
    @monitor_performance
    async def execute_workflow(
        self,
        workflow_id: str,
        execution_parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute workflow with intelligent task orchestration.
        
        Args:
            workflow_id: Workflow identifier
            execution_parameters: Optional execution parameters
            
        Returns:
            Execution ID
        """
        
        if workflow_id not in self.workflows:
            raise OrchestrationError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = f"exec_{workflow_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create execution context
        execution_context = {
            'execution_id': execution_id,
            'workflow_id': workflow_id,
            'workflow': workflow,
            'parameters': execution_parameters or {},
            'status': WorkflowStatus.RUNNING,
            'started_at': datetime.utcnow(),
            'task_results': {},
            'task_states': {task.task_id: TaskStatus.WAITING for task in workflow.tasks}
        }
        
        self.active_executions[execution_id] = execution_context
        
        try:
            # Update workflow status
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.utcnow()
            
            # Execute workflow
            result = await self._orchestrate_workflow_execution(execution_context)
            
            # Update completion status
            execution_context['status'] = WorkflowStatus.COMPLETED
            execution_context['completed_at'] = datetime.utcnow()
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            
            self.metrics.increment('workflows_completed')
            self.logger.info(f"Workflow {workflow_id} completed successfully")
            
            return execution_id
            
        except Exception as e:
            # Handle execution failure
            execution_context['status'] = WorkflowStatus.FAILED
            execution_context['error_message'] = str(e)
            
            workflow.status = WorkflowStatus.FAILED
            
            self.metrics.increment('workflows_failed')
            self.logger.error(f"Workflow {workflow_id} execution failed: {e}")
            
            # Retry if configured
            if workflow.retry_count < workflow.max_retries:
                workflow.retry_count += 1
                workflow.status = WorkflowStatus.RETRYING
                
                # Schedule retry
                retry_delay = 2 ** workflow.retry_count  # Exponential backoff
                self.scheduler.add_job(
                    func=self._retry_workflow_execution,
                    trigger='date',
                    run_date=datetime.utcnow() + timedelta(seconds=retry_delay),
                    args=[workflow_id, execution_parameters],
                    id=f"retry_{execution_id}",
                    name=f"Retry execution of {workflow.name}"
                )
                
                self.logger.info(f"Workflow {workflow_id} scheduled for retry in {retry_delay} seconds")
            
            raise OrchestrationError(f"Workflow execution failed: {e}")
        
        finally:
            # Move to execution history
            self.execution_history.append(execution_context)
            
            # Cleanup active execution
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _retry_workflow_execution(
        self,
        workflow_id: str,
        execution_parameters: Optional[Dict[str, Any]] = None
    ):
        """Retry failed workflow execution."""
        
        try:
            await self.execute_workflow(workflow_id, execution_parameters)
        except Exception as e:
            self.logger.error(f"Workflow retry failed: {e}")
    
    async def _orchestrate_workflow_execution(self, execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the execution of workflow tasks."""
        
        workflow = execution_context['workflow']
        task_states = execution_context['task_states']
        task_results = execution_context['task_results']
        
        # Initialize execution state
        remaining_tasks = set(task.task_id for task in workflow.tasks)
        running_tasks = set()
        
        while remaining_tasks or running_tasks:
            # Find ready tasks
            ready_tasks = await self._find_ready_tasks(
                workflow.tasks,
                task_states,
                remaining_tasks
            )
            
            # Start ready tasks
            for task in ready_tasks:
                if len(running_tasks) < self.config.max_concurrent_tasks:
                    task_future = asyncio.create_task(
                        self._execute_task(task, execution_context)
                    )
                    running_tasks.add(task.task_id)
                    remaining_tasks.discard(task.task_id)
                    task_states[task.task_id] = TaskStatus.RUNNING
                    
                    # Store future for completion tracking
                    execution_context[f'task_future_{task.task_id}'] = task_future
            
            # Wait for task completions
            if running_tasks:
                completed_tasks = await self._wait_for_task_completions(
                    execution_context,
                    running_tasks
                )
                
                for task_id in completed_tasks:
                    running_tasks.discard(task_id)
            
            # Short sleep to prevent busy waiting
            await asyncio.sleep(0.1)
        
        return task_results
    
    async def _find_ready_tasks(
        self,
        tasks: List[Task],
        task_states: Dict[str, TaskStatus],
        remaining_tasks: Set[str]
    ) -> List[Task]:
        """Find tasks that are ready to execute."""
        
        ready_tasks = []
        
        for task in tasks:
            if task.task_id not in remaining_tasks:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in task.dependencies:
                if task_states.get(dep_id) != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_tasks.append(task)
        
        # Sort by priority (higher priority first)
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        return ready_tasks
    
    @retry_on_failure(max_retries=3)
    async def _execute_task(self, task: Task, execution_context: Dict[str, Any]) -> Any:
        """Execute individual task with monitoring and error handling."""
        
        task.started_at = datetime.utcnow()
        execution_context['task_states'][task.task_id] = TaskStatus.RUNNING
        
        try:
            # Prepare task parameters
            task_params = {
                **task.parameters,
                **execution_context['parameters'],
                'execution_context': execution_context
            }
            
            # Execute task with timeout
            result = await asyncio.wait_for(
                self._run_task_function(task.function, task_params),
                timeout=task.timeout_seconds
            )
            
            # Update task completion
            task.completed_at = datetime.utcnow()
            task.status = TaskStatus.COMPLETED
            task.result = result
            
            execution_context['task_states'][task.task_id] = TaskStatus.COMPLETED
            execution_context['task_results'][task.task_id] = result
            
            self.metrics.increment('tasks_completed')
            self.logger.info(f"Task {task.task_id} completed successfully")
            
            return result
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error_message = f"Task timeout after {task.timeout_seconds} seconds"
            execution_context['task_states'][task.task_id] = TaskStatus.FAILED
            
            self.metrics.increment('tasks_timeout')
            raise OrchestrationError(f"Task {task.task_id} timed out")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            execution_context['task_states'][task.task_id] = TaskStatus.FAILED
            
            self.metrics.increment('tasks_failed')
            self.logger.error(f"Task {task.task_id} failed: {e}")
            
            # Retry if configured
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.WAITING
                execution_context['task_states'][task.task_id] = TaskStatus.WAITING
                
                # Add retry delay
                await asyncio.sleep(2 ** task.retry_count)
                
                return await self._execute_task(task, execution_context)
            
            raise OrchestrationError(f"Task {task.task_id} failed: {e}")
    
    async def _run_task_function(self, function: Callable, parameters: Dict[str, Any]) -> Any:
        """Run task function with proper async handling."""
        
        if asyncio.iscoroutinefunction(function):
            return await function(**parameters)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.task_executor,
                lambda: function(**parameters)
            )
    
    async def _wait_for_task_completions(
        self,
        execution_context: Dict[str, Any],
        running_tasks: Set[str]
    ) -> List[str]:
        """Wait for task completions and return completed task IDs."""
        
        completed_tasks = []
        futures = []
        
        for task_id in running_tasks:
            future_key = f'task_future_{task_id}'
            if future_key in execution_context:
                futures.append((task_id, execution_context[future_key]))
        
        if not futures:
            return completed_tasks
        
        # Wait for at least one task to complete
        done, pending = await asyncio.wait(
            [future for _, future in futures],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task_id, future in futures:
            if future in done:
                completed_tasks.append(task_id)
                # Clean up future reference
                future_key = f'task_future_{task_id}'
                if future_key in execution_context:
                    del execution_context[future_key]
        
        return completed_tasks


class TaskScheduler:
    """
    Intelligent task scheduler with priority-based queuing,
    resource-aware scheduling, and load balancing capabilities.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsCollector("task_scheduler")
        
        # Task queues by priority
        self.priority_queues = {
            1: queue.PriorityQueue(),  # Low priority
            2: queue.PriorityQueue(),  # Normal priority
            3: queue.PriorityQueue(),  # High priority
            4: queue.PriorityQueue(),  # Critical priority
        }
        
        # Resource tracking
        self.resource_usage = {
            'cpu': 0.0,
            'memory': 0.0,
            'disk_io': 0.0,
            'network_io': 0.0
        }
        
        # Worker management
        self.active_workers = {}
        self.worker_pool = ThreadPoolExecutor(max_workers=config.max_concurrent_tasks)
        
        # Scheduling thread
        self.scheduler_thread = threading.Thread(target=self._scheduling_loop, daemon=True)
        self.stop_scheduling = threading.Event()
        
        self._start_scheduler()
    
    def _start_scheduler(self):
        """Start task scheduling."""
        
        self.scheduler_thread.start()
        self.logger.info("Task scheduler started")
    
    def _scheduling_loop(self):
        """Main scheduling loop."""
        
        while not self.stop_scheduling.wait(0.1):
            try:
                # Check resource availability
                if self._can_schedule_more_tasks():
                    # Find next task to schedule
                    task_item = self._get_next_task()
                    
                    if task_item:
                        priority, timestamp, task = task_item
                        self._schedule_task_execution(task)
                
            except Exception as e:
                self.logger.error(f"Scheduling loop error: {e}")
    
    def _can_schedule_more_tasks(self) -> bool:
        """Check if more tasks can be scheduled based on resource constraints."""
        
        # Check concurrent task limit
        if len(self.active_workers) >= self.config.max_concurrent_tasks:
            return False
        
        # Check resource thresholds
        if self.resource_usage['cpu'] > 0.9:
            return False
        
        if self.resource_usage['memory'] > 0.85:
            return False
        
        return True
    
    def _get_next_task(self) -> Optional[tuple]:
        """Get next task from priority queues."""
        
        # Check queues from highest to lowest priority
        for priority in sorted(self.priority_queues.keys(), reverse=True):
            task_queue = self.priority_queues[priority]
            
            if not task_queue.empty():
                try:
                    return task_queue.get_nowait()
                except queue.Empty:
                    continue
        
        return None
    
    def _schedule_task_execution(self, task: Task):
        """Schedule task for execution."""
        
        worker_id = f"worker_{task.task_id}"
        
        future = self.worker_pool.submit(self._execute_task_worker, task)
        
        self.active_workers[worker_id] = {
            'task': task,
            'future': future,
            'started_at': datetime.utcnow()
        }
        
        # Add completion callback
        future.add_done_callback(lambda f: self._handle_task_completion(worker_id, f))
        
        self.metrics.increment('tasks_scheduled')
        self.logger.debug(f"Task {task.task_id} scheduled for execution")
    
    def _execute_task_worker(self, task: Task) -> Any:
        """Execute task in worker thread."""
        
        try:
            # Update resource usage
            self._update_resource_usage(task, 'start')
            
            # Execute task
            if asyncio.iscoroutinefunction(task.function):
                # Run async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(task.function(**task.parameters))
                loop.close()
            else:
                # Run sync function
                result = task.function(**task.parameters)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.utcnow()
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            raise
        
        finally:
            # Update resource usage
            self._update_resource_usage(task, 'end')
    
    def _handle_task_completion(self, worker_id: str, future):
        """Handle task completion and cleanup."""
        
        if worker_id in self.active_workers:
            worker_info = self.active_workers[worker_id]
            task = worker_info['task']
            
            try:
                result = future.result()
                self.metrics.increment('tasks_completed_scheduler')
                self.logger.debug(f"Task {task.task_id} completed in scheduler")
                
            except Exception as e:
                self.metrics.increment('tasks_failed_scheduler')
                self.logger.error(f"Task {task.task_id} failed in scheduler: {e}")
            
            finally:
                # Cleanup worker
                del self.active_workers[worker_id]
    
    def _update_resource_usage(self, task: Task, phase: str):
        """Update resource usage tracking."""
        
        resource_requirements = task.resource_requirements
        
        if phase == 'start':
            # Add resource usage
            for resource, amount in resource_requirements.items():
                if resource in self.resource_usage:
                    self.resource_usage[resource] += amount
        
        elif phase == 'end':
            # Remove resource usage
            for resource, amount in resource_requirements.items():
                if resource in self.resource_usage:
                    self.resource_usage[resource] = max(0, self.resource_usage[resource] - amount)
    
    async def submit_task(self, task: Task) -> str:
        """Submit task for scheduling."""
        
        priority = task.priority
        timestamp = datetime.utcnow().timestamp()
        
        # Add to appropriate priority queue
        self.priority_queues[priority].put((priority, timestamp, task))
        
        self.metrics.increment('tasks_submitted')
        self.logger.debug(f"Task {task.task_id} submitted to scheduler")
        
        return task.task_id


class DependencyResolver:
    """
    Advanced dependency resolution system with intelligent conflict resolution
    and dynamic dependency management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependency_cache = {}
        
    async def resolve_dependencies(
        self,
        tasks: List[Task],
        context: Dict[str, Any] = None
    ) -> List[List[Task]]:
        """
        Resolve task dependencies and return execution batches.
        
        Args:
            tasks: List of tasks to resolve
            context: Optional execution context
            
        Returns:
            List of task batches for parallel execution
        """
        
        # Build dependency graph
        graph = nx.DiGraph()
        
        for task in tasks:
            graph.add_node(task.task_id, task=task)
        
        for task in tasks:
            for dep_id in task.dependencies:
                graph.add_edge(dep_id, task.task_id)
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(graph):
            raise DependencyError("Circular dependency detected")
        
        # Topological sort to get execution order
        execution_order = list(nx.topological_sort(graph))
        
        # Group tasks into batches for parallel execution
        batches = self._create_execution_batches(graph, execution_order, tasks)
        
        return batches
    
    def _create_execution_batches(
        self,
        graph: nx.DiGraph,
        execution_order: List[str],
        tasks: List[Task]
    ) -> List[List[Task]]:
        """Create batches of tasks that can be executed in parallel."""
        
        task_map = {task.task_id: task for task in tasks}
        batches = []
        remaining_tasks = set(execution_order)
        
        while remaining_tasks:
            batch = []
            
            # Find tasks with no unresolved dependencies
            for task_id in list(remaining_tasks):
                predecessors = set(graph.predecessors(task_id))
                
                if not predecessors.intersection(remaining_tasks):
                    batch.append(task_map[task_id])
                    remaining_tasks.remove(task_id)
            
            if batch:
                batches.append(batch)
            else:
                # This shouldn't happen with a valid DAG
                raise DependencyError("Unable to resolve dependencies")
        
        return batches


class ExecutionPlanner:
    """
    Intelligent execution planning system with optimization strategies,
    resource allocation, and performance prediction.
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.historical_data = []
        
    async def create_execution_plan(
        self,
        workflow: Workflow,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create optimized execution plan for workflow.
        
        Args:
            workflow: Workflow to plan
            constraints: Optional execution constraints
            
        Returns:
            Detailed execution plan
        """
        
        constraints = constraints or {}
        
        # Analyze workflow complexity
        complexity_analysis = await self._analyze_workflow_complexity(workflow)
        
        # Estimate resource requirements
        resource_estimate = await self._estimate_resource_requirements(workflow)
        
        # Create execution strategy
        execution_strategy = await self._create_execution_strategy(
            workflow,
            complexity_analysis,
            resource_estimate,
            constraints
        )
        
        # Generate execution timeline
        timeline = await self._generate_execution_timeline(workflow, execution_strategy)
        
        execution_plan = {
            'workflow_id': workflow.workflow_id,
            'plan_created_at': datetime.utcnow().isoformat(),
            'complexity_analysis': complexity_analysis,
            'resource_estimate': resource_estimate,
            'execution_strategy': execution_strategy,
            'timeline': timeline,
            'estimated_duration_minutes': timeline['total_duration_minutes'],
            'recommended_resources': self._recommend_resources(resource_estimate)
        }
        
        return execution_plan
    
    async def _analyze_workflow_complexity(self, workflow: Workflow) -> Dict[str, Any]:
        """Analyze workflow complexity metrics."""
        
        task_count = len(workflow.tasks)
        dependency_count = sum(len(task.dependencies) for task in workflow.tasks)
        
        # Calculate complexity score
        complexity_score = (
            task_count * 1.0 +
            dependency_count * 0.5 +
            len([t for t in workflow.tasks if t.dependency_type == DependencyType.CONDITIONAL]) * 2.0
        )
        
        return {
            'task_count': task_count,
            'dependency_count': dependency_count,
            'complexity_score': complexity_score,
            'complexity_level': self._classify_complexity(complexity_score),
            'parallel_opportunities': self._count_parallel_opportunities(workflow.tasks),
            'critical_path_length': self._calculate_critical_path_length(workflow.tasks)
        }
    
    def _classify_complexity(self, score: float) -> str:
        """Classify workflow complexity level."""
        
        if score < 10:
            return 'simple'
        elif score < 50:
            return 'moderate'
        elif score < 100:
            return 'complex'
        else:
            return 'very_complex'
    
    async def _estimate_resource_requirements(self, workflow: Workflow) -> Dict[str, Any]:
        """Estimate resource requirements for workflow execution."""
        
        total_cpu = sum(
            task.resource_requirements.get('cpu', 1.0) 
            for task in workflow.tasks
        )
        
        total_memory = sum(
            task.resource_requirements.get('memory', 512) 
            for task in workflow.tasks
        )
        
        peak_cpu = max(
            task.resource_requirements.get('cpu', 1.0) 
            for task in workflow.tasks
        )
        
        peak_memory = max(
            task.resource_requirements.get('memory', 512) 
            for task in workflow.tasks
        )
        
        return {
            'total_cpu_hours': total_cpu,
            'total_memory_mb': total_memory,
            'peak_cpu_cores': peak_cpu,
            'peak_memory_mb': peak_memory,
            'estimated_cost_usd': self._estimate_execution_cost(total_cpu, total_memory),
            'storage_requirements_gb': sum(
                task.resource_requirements.get('storage', 0) 
                for task in workflow.tasks
            )
        }
    
    def _estimate_execution_cost(self, cpu_hours: float, memory_mb: float) -> float:
        """Estimate execution cost based on resource usage."""
        
        # Simple cost estimation (adjust based on actual cloud pricing)
        cpu_cost_per_hour = 0.05
        memory_cost_per_gb_hour = 0.01
        
        memory_gb_hours = memory_mb / 1024
        
        return (cpu_hours * cpu_cost_per_hour) + (memory_gb_hours * memory_cost_per_gb_hour)
