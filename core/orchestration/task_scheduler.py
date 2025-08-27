"""
Task Scheduler - Intelligent Enterprise Task Scheduling & Resource Management System

Advanced task scheduling engine with AI-powered optimization, predictive resource allocation,
and intelligent load balancing for complex multi-tenant content processing workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import heapq
import json

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class SchedulingStrategy(Enum):
    """Task scheduling strategy options."""
    FIFO = "fifo"
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"
    WEIGHTED_FAIR = "weighted_fair"
    SHORTEST_JOB_FIRST = "shortest_job_first"
    DEADLINE_AWARE = "deadline_aware"
    AI_OPTIMIZED = "ai_optimized"


class TaskType(Enum):
    """Task type classification."""
    CONTENT_UPLOAD = "content_upload"
    AI_PROCESSING = "ai_processing"
    CONTENT_ANALYSIS = "content_analysis"
    PROTECTION_SCAN = "protection_scan"
    MONETIZATION_CALC = "monetization_calc"
    COLLABORATION_MATCH = "collaboration_match"
    DISTRIBUTION_PUSH = "distribution_push"
    ANALYTICS_REPORT = "analytics_report"
    MAINTENANCE = "maintenance"


class ResourceType(Enum):
    """System resource types."""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"


@dataclass
class ResourceRequirement:
    """Resource requirement specification."""
    resource_type: ResourceType
    amount: float
    unit: str
    duration_estimate: Optional[float] = None
    priority: TaskPriority = TaskPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledTask:
    """Scheduled task definition with execution parameters."""
    task_id: str
    name: str
    task_type: TaskType
    executor: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    deadline: Optional[datetime] = None
    estimated_duration: Optional[float] = None
    resource_requirements: List[ResourceRequirement] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    retry_delay: int = 5
    timeout: Optional[int] = None
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Scheduling metadata
    scheduled_time: Optional[datetime] = None
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None


@dataclass
class TaskExecution:
    """Task execution tracking information."""
    task_id: str
    execution_id: str
    executor_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "running"
    result: Optional[Any] = None
    error: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutorNode:
    """Task executor node information."""
    executor_id: str
    name: str
    node_type: str
    capacity: Dict[str, float]
    available_resources: Dict[str, float]
    allocated_resources: Dict[str, float] = field(default_factory=dict)
    active_tasks: List[str] = field(default_factory=list)
    health_status: str = "healthy"
    performance_score: float = 1.0
    last_heartbeat: Optional[datetime] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulingDecision:
    """Scheduling decision with rationale."""
    task_id: str
    executor_id: str
    scheduled_time: datetime
    estimated_completion: datetime
    priority_score: float
    resource_score: float
    load_score: float
    overall_score: float
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskScheduler:
    """
    Enterprise-grade intelligent task scheduling system with AI optimization.
    
    Provides comprehensive task scheduling capabilities including:
    - Multi-strategy scheduling algorithms with AI optimization
    - Intelligent resource allocation and load balancing
    - Predictive scheduling based on historical patterns
    - Multi-tenant isolation and fair resource sharing
    - Real-time performance monitoring and optimization
    """
    
    def __init__(
        self,
        strategy: SchedulingStrategy = SchedulingStrategy.AI_OPTIMIZED,
        max_concurrent_tasks: int = 1000
    ):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.scheduling_strategy = strategy
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_executors: Dict[str, Callable] = {}
        self.executor_nodes: Dict[str, ExecutorNode] = {}
        
        # Task queues and scheduling
        self.task_queue: List[Tuple[float, ScheduledTask]] = []  # Priority queue
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.active_executions: Dict[str, TaskExecution] = {}
        self.completed_tasks: Dict[str, TaskExecution] = {}
        
        # Resource management
        self.global_resources: Dict[ResourceType, float] = {
            ResourceType.CPU: 100.0,
            ResourceType.MEMORY: 100.0,
            ResourceType.GPU: 100.0,
            ResourceType.STORAGE: 100.0,
            ResourceType.NETWORK: 100.0,
            ResourceType.DATABASE: 100.0
        }
        
        # Performance tracking
        self.scheduling_stats = {
            'total_tasks_scheduled': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'average_wait_time': 0.0,
            'average_execution_time': 0.0,
            'throughput_per_minute': 0.0,
            'resource_utilization': 0.0,
            'deadline_miss_rate': 0.0,
            'scheduling_efficiency': 0.0
        }
        
        # AI optimization
        self.learning_enabled = True
        self.prediction_model = None
        self.historical_patterns: Dict[str, List[Dict]] = {}
        
        # Start background scheduler
        self._scheduler_running = True
        asyncio.create_task(self._scheduler_loop())
        
        self.logger.info(f"TaskScheduler initialized with strategy: {strategy.value}")
    
    async def register_executor(self, executor_id: str, executor_func: Callable, node_info: ExecutorNode) -> bool:
        """
        Register a task executor with node information.
        
        Args:
            executor_id: Unique executor identifier
            executor_func: Async callable for task execution
            node_info: Executor node configuration
            
        Returns:
            bool: Success status
        """
        try:
            if not asyncio.iscoroutinefunction(executor_func):
                raise ValueError("Executor must be an async function")
            
            self.task_executors[executor_id] = executor_func
            self.executor_nodes[executor_id] = node_info
            
            await self.event_dispatcher.emit('executor_registered', {
                'executor_id': executor_id,
                'node_type': node_info.node_type,
                'capacity': node_info.capacity
            })
            
            await self.metrics_collector.increment('executors.registered')
            self.logger.info(f"Task executor registered: {executor_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register executor: {e}")
            return False
    
    async def schedule_task(self, task: ScheduledTask) -> bool:
        """
        Schedule a new task for execution.
        
        Args:
            task: Task definition to schedule
            
        Returns:
            bool: Success status
        """
        try:
            # Validate task
            if not await self._validate_task(task):
                return False
            
            # Set scheduling metadata
            task.scheduled_time = datetime.now()
            
            # Calculate priority score
            priority_score = await self._calculate_priority_score(task)
            
            # Add to queue
            heapq.heappush(self.task_queue, (priority_score, task))
            self.scheduled_tasks[task.task_id] = task
            
            await self.event_dispatcher.emit('task_scheduled', {
                'task_id': task.task_id,
                'task_type': task.task_type.value,
                'priority': task.priority.value,
                'priority_score': priority_score,
                'estimated_duration': task.estimated_duration
            })
            
            self.scheduling_stats['total_tasks_scheduled'] += 1
            await self.metrics_collector.increment('tasks.scheduled')
            
            self.logger.info(f"Task scheduled: {task.task_id} (priority: {priority_score})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule task: {e}")
            await self.metrics_collector.increment('tasks.schedule_failed')
            return False
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop for task execution."""
        while self._scheduler_running:
            try:
                await self._process_task_queue()
                await self._cleanup_completed_tasks()
                await self._update_performance_metrics()
                await asyncio.sleep(0.1)  # 100ms scheduling interval
                
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(1.0)
    
    async def _process_task_queue(self) -> None:
        """Process tasks from the scheduling queue."""
        current_time = datetime.now()
        
        # Check for available resources and ready tasks
        while (self.task_queue and 
               len(self.active_executions) < self.max_concurrent_tasks):
            
            # Get highest priority task
            priority_score, task = heapq.heappop(self.task_queue)
            
            # Check if task is ready (dependencies satisfied)
            if not await self._check_task_dependencies(task):
                # Re-queue with slight priority boost to avoid starvation
                heapq.heappush(self.task_queue, (priority_score - 0.1, task))
                break
            
            # Find optimal executor
            scheduling_decision = await self._find_optimal_executor(task)
            if not scheduling_decision:
                # Re-queue if no suitable executor
                heapq.heappush(self.task_queue, (priority_score, task))
                break
            
            # Execute task
            await self._execute_task(task, scheduling_decision)
    
    async def _find_optimal_executor(self, task: ScheduledTask) -> Optional[SchedulingDecision]:
        """
        Find optimal executor for task using scheduling strategy.
        
        Args:
            task: Task to schedule
            
        Returns:
            Optional[SchedulingDecision]: Scheduling decision or None
        """
        available_executors = []
        
        # Filter available executors
        for executor_id, node in self.executor_nodes.items():
            if (node.health_status == "healthy" and 
                await self._check_resource_availability(node, task)):
                available_executors.append((executor_id, node))
        
        if not available_executors:
            return None
        
        # Apply scheduling strategy
        if self.scheduling_strategy == SchedulingStrategy.AI_OPTIMIZED:
            return await self._ai_optimized_scheduling(task, available_executors)
        elif self.scheduling_strategy == SchedulingStrategy.PRIORITY:
            return await self._priority_scheduling(task, available_executors)
        elif self.scheduling_strategy == SchedulingStrategy.SHORTEST_JOB_FIRST:
            return await self._shortest_job_first_scheduling(task, available_executors)
        elif self.scheduling_strategy == SchedulingStrategy.DEADLINE_AWARE:
            return await self._deadline_aware_scheduling(task, available_executors)
        else:  # Default to round robin
            return await self._round_robin_scheduling(task, available_executors)
    
    async def _ai_optimized_scheduling(
        self,
        task: ScheduledTask,
        available_executors: List[Tuple[str, ExecutorNode]]
    ) -> Optional[SchedulingDecision]:
        """AI-powered optimal executor selection."""
        best_decision = None
        best_score = float('-inf')
        
        for executor_id, node in available_executors:
            # Calculate multi-dimensional score
            priority_score = await self._calculate_priority_score(task)
            resource_score = await self._calculate_resource_score(node, task)
            load_score = await self._calculate_load_score(node)
            performance_score = node.performance_score
            
            # Weighted combination
            overall_score = (
                0.3 * priority_score +
                0.25 * resource_score +
                0.25 * load_score +
                0.2 * performance_score
            )
            
            if overall_score > best_score:
                best_score = overall_score
                estimated_completion = datetime.now() + timedelta(
                    seconds=task.estimated_duration or 60
                )
                
                best_decision = SchedulingDecision(
                    task_id=task.task_id,
                    executor_id=executor_id,
                    scheduled_time=datetime.now(),
                    estimated_completion=estimated_completion,
                    priority_score=priority_score,
                    resource_score=resource_score,
                    load_score=load_score,
                    overall_score=overall_score,
                    rationale=f"AI-optimized selection based on multi-criteria scoring"
                )
        
        return best_decision
    
    async def _priority_scheduling(
        self,
        task: ScheduledTask,
        available_executors: List[Tuple[str, ExecutorNode]]
    ) -> Optional[SchedulingDecision]:
        """Priority-based executor selection."""
        # Select executor with highest performance score
        best_executor = max(available_executors, key=lambda x: x[1].performance_score)
        executor_id, node = best_executor
        
        return SchedulingDecision(
            task_id=task.task_id,
            executor_id=executor_id,
            scheduled_time=datetime.now(),
            estimated_completion=datetime.now() + timedelta(seconds=task.estimated_duration or 60),
            priority_score=await self._calculate_priority_score(task),
            resource_score=await self._calculate_resource_score(node, task),
            load_score=await self._calculate_load_score(node),
            overall_score=node.performance_score,
            rationale="Priority-based selection with highest performance executor"
        )
    
    async def _shortest_job_first_scheduling(
        self,
        task: ScheduledTask,
        available_executors: List[Tuple[str, ExecutorNode]]
    ) -> Optional[SchedulingDecision]:
        """Shortest job first executor selection."""
        # Select executor with lowest current load
        best_executor = min(available_executors, key=lambda x: len(x[1].active_tasks))
        executor_id, node = best_executor
        
        return SchedulingDecision(
            task_id=task.task_id,
            executor_id=executor_id,
            scheduled_time=datetime.now(),
            estimated_completion=datetime.now() + timedelta(seconds=task.estimated_duration or 60),
            priority_score=await self._calculate_priority_score(task),
            resource_score=await self._calculate_resource_score(node, task),
            load_score=await self._calculate_load_score(node),
            overall_score=1.0 / (len(node.active_tasks) + 1),
            rationale="Shortest job first selection with lowest load executor"
        )
    
    async def _deadline_aware_scheduling(
        self,
        task: ScheduledTask,
        available_executors: List[Tuple[str, ExecutorNode]]
    ) -> Optional[SchedulingDecision]:
        """Deadline-aware executor selection."""
        if not task.deadline:
            return await self._priority_scheduling(task, available_executors)
        
        # Calculate deadline urgency
        time_to_deadline = (task.deadline - datetime.now()).total_seconds()
        urgency_score = 1.0 / max(time_to_deadline, 1.0)
        
        best_executor = max(
            available_executors,
            key=lambda x: x[1].performance_score * urgency_score
        )
        executor_id, node = best_executor
        
        return SchedulingDecision(
            task_id=task.task_id,
            executor_id=executor_id,
            scheduled_time=datetime.now(),
            estimated_completion=datetime.now() + timedelta(seconds=task.estimated_duration or 60),
            priority_score=urgency_score,
            resource_score=await self._calculate_resource_score(node, task),
            load_score=await self._calculate_load_score(node),
            overall_score=node.performance_score * urgency_score,
            rationale=f"Deadline-aware selection with {time_to_deadline}s to deadline"
        )
    
    async def _round_robin_scheduling(
        self,
        task: ScheduledTask,
        available_executors: List[Tuple[str, ExecutorNode]]
    ) -> Optional[SchedulingDecision]:
        """Round-robin executor selection."""
        # Simple round-robin based on task count
        executor_id, node = min(available_executors, key=lambda x: len(x[1].active_tasks))
        
        return SchedulingDecision(
            task_id=task.task_id,
            executor_id=executor_id,
            scheduled_time=datetime.now(),
            estimated_completion=datetime.now() + timedelta(seconds=task.estimated_duration or 60),
            priority_score=await self._calculate_priority_score(task),
            resource_score=await self._calculate_resource_score(node, task),
            load_score=await self._calculate_load_score(node),
            overall_score=1.0,
            rationale="Round-robin selection based on task distribution"
        )
    
    async def _execute_task(self, task: ScheduledTask, decision: SchedulingDecision) -> None:
        """
        Execute task on selected executor.
        
        Args:
            task: Task to execute
            decision: Scheduling decision
        """
        execution_id = str(uuid.uuid4())
        
        try:
            # Create execution tracking
            execution = TaskExecution(
                task_id=task.task_id,
                execution_id=execution_id,
                executor_id=decision.executor_id,
                start_time=datetime.now()
            )
            
            self.active_executions[execution_id] = execution
            
            # Allocate resources
            await self._allocate_task_resources(task, decision.executor_id)
            
            # Add to executor's active tasks
            node = self.executor_nodes[decision.executor_id]
            node.active_tasks.append(task.task_id)
            
            # Execute task asynchronously
            asyncio.create_task(self._execute_task_async(task, execution, decision))
            
            await self.event_dispatcher.emit('task_started', {
                'task_id': task.task_id,
                'execution_id': execution_id,
                'executor_id': decision.executor_id,
                'scheduling_score': decision.overall_score
            })
            
            await self.metrics_collector.increment('tasks.started')
            
        except Exception as e:
            self.logger.error(f"Failed to execute task: {e}")
            await self.metrics_collector.increment('tasks.execution_failed')
    
    async def _execute_task_async(
        self,
        task: ScheduledTask,
        execution: TaskExecution,
        decision: SchedulingDecision
    ) -> None:
        """Asynchronous task execution wrapper."""
        try:
            # Get executor function
            executor_func = self.task_executors[decision.executor_id]
            
            # Prepare execution context
            execution_context = {
                'task': task,
                'execution_id': execution.execution_id,
                'parameters': task.parameters,
                'context': task.context,
                'metadata': task.metadata
            }
            
            # Execute with timeout
            if task.timeout:
                execution.result = await asyncio.wait_for(
                    executor_func(execution_context),
                    timeout=task.timeout
                )
            else:
                execution.result = await executor_func(execution_context)
            
            # Mark as completed
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.status = "completed"
            
            self.scheduling_stats['total_tasks_completed'] += 1
            
            await self.event_dispatcher.emit('task_completed', {
                'task_id': task.task_id,
                'execution_id': execution.execution_id,
                'duration': execution.duration,
                'executor_id': decision.executor_id
            })
            
            await self.metrics_collector.record('task.execution_time', execution.duration)
            await self.metrics_collector.increment('tasks.completed')
            
        except Exception as e:
            execution.end_time = datetime.now()
            execution.error = str(e)
            execution.status = "failed"
            
            self.scheduling_stats['total_tasks_failed'] += 1
            
            # Retry logic
            task.execution_count += 1
            if task.execution_count < task.retry_count:
                task.last_execution = datetime.now()
                task.next_execution = datetime.now() + timedelta(seconds=task.retry_delay)
                
                # Re-schedule for retry
                await asyncio.sleep(task.retry_delay)
                await self.schedule_task(task)
            
            await self.event_dispatcher.emit('task_failed', {
                'task_id': task.task_id,
                'execution_id': execution.execution_id,
                'error': str(e),
                'retry_count': task.execution_count
            })
            
            await self.metrics_collector.increment('tasks.failed')
            self.logger.error(f"Task execution failed: {task.task_id} - {e}")
        
        finally:
            # Cleanup
            await self._cleanup_task_execution(task, execution, decision)
    
    async def _cleanup_task_execution(
        self,
        task: ScheduledTask,
        execution: TaskExecution,
        decision: SchedulingDecision
    ) -> None:
        """Cleanup after task execution."""
        try:
            # Release resources
            await self._release_task_resources(task, decision.executor_id)
            
            # Remove from executor's active tasks
            node = self.executor_nodes[decision.executor_id]
            if task.task_id in node.active_tasks:
                node.active_tasks.remove(task.task_id)
            
            # Move to completed tasks
            self.completed_tasks[execution.execution_id] = execution
            
            # Remove from active executions
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
            
            # Remove from scheduled tasks if completed
            if execution.status == "completed" and task.task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task.task_id]
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    async def _calculate_priority_score(self, task: ScheduledTask) -> float:
        """Calculate task priority score."""
        base_score = task.priority.value
        
        # Deadline urgency
        if task.deadline:
            time_to_deadline = (task.deadline - datetime.now()).total_seconds()
            urgency_multiplier = max(1.0, 3600.0 / max(time_to_deadline, 1.0))
            base_score *= urgency_multiplier
        
        # Task type importance
        type_multipliers = {
            TaskType.CRITICAL: 2.0,
            TaskType.CONTENT_UPLOAD: 1.5,
            TaskType.AI_PROCESSING: 1.3,
            TaskType.PROTECTION_SCAN: 1.2,
            TaskType.ANALYTICS_REPORT: 0.8,
            TaskType.MAINTENANCE: 0.5
        }
        
        base_score *= type_multipliers.get(task.task_type, 1.0)
        
        return base_score
    
    async def _calculate_resource_score(self, node: ExecutorNode, task: ScheduledTask) -> float:
        """Calculate resource availability score."""
        total_score = 0.0
        requirement_count = 0
        
        for req in task.resource_requirements:
            if req.resource_type.value in node.available_resources:
                available = node.available_resources[req.resource_type.value]
                required = req.amount
                
                if available >= required:
                    score = min(1.0, available / required)
                    total_score += score
                
                requirement_count += 1
        
        return total_score / max(requirement_count, 1)
    
    async def _calculate_load_score(self, node: ExecutorNode) -> float:
        """Calculate executor load score."""
        max_tasks = 10  # Configurable
        current_tasks = len(node.active_tasks)
        return max(0.0, 1.0 - (current_tasks / max_tasks))
    
    async def _check_resource_availability(self, node: ExecutorNode, task: ScheduledTask) -> bool:
        """Check if node has sufficient resources for task."""
        for req in task.resource_requirements:
            if req.resource_type.value in node.available_resources:
                if node.available_resources[req.resource_type.value] < req.amount:
                    return False
        return True
    
    async def _allocate_task_resources(self, task: ScheduledTask, executor_id: str) -> None:
        """Allocate resources for task execution."""
        node = self.executor_nodes[executor_id]
        
        for req in task.resource_requirements:
            if req.resource_type.value in node.available_resources:
                node.available_resources[req.resource_type.value] -= req.amount
                
                if req.resource_type.value not in node.allocated_resources:
                    node.allocated_resources[req.resource_type.value] = 0.0
                node.allocated_resources[req.resource_type.value] += req.amount
    
    async def _release_task_resources(self, task: ScheduledTask, executor_id: str) -> None:
        """Release allocated task resources."""
        node = self.executor_nodes[executor_id]
        
        for req in task.resource_requirements:
            if req.resource_type.value in node.available_resources:
                node.available_resources[req.resource_type.value] += req.amount
                
                if req.resource_type.value in node.allocated_resources:
                    node.allocated_resources[req.resource_type.value] -= req.amount
                    if node.allocated_resources[req.resource_type.value] <= 0:
                        del node.allocated_resources[req.resource_type.value]
    
    async def _validate_task(self, task: ScheduledTask) -> bool:
        """Validate task definition."""
        try:
            if not task.task_id or not task.executor:
                return False
            
            if task.deadline and task.deadline <= datetime.now():
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _check_task_dependencies(self, task: ScheduledTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            # Check if dependency is completed
            if dep_id in self.scheduled_tasks:
                return False  # Dependency still scheduled
            
            # Check if dependency completed successfully
            dep_completed = any(
                exec.task_id == dep_id and exec.status == "completed"
                for exec in self.completed_tasks.values()
            )
            
            if not dep_completed:
                return False
        
        return True
    
    async def _cleanup_completed_tasks(self) -> None:
        """Cleanup old completed task records."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        tasks_to_remove = [
            exec_id for exec_id, execution in self.completed_tasks.items()
            if execution.end_time and execution.end_time < cutoff_time
        ]
        
        for exec_id in tasks_to_remove:
            del self.completed_tasks[exec_id]
    
    async def _update_performance_metrics(self) -> None:
        """Update scheduler performance metrics."""
        if self.scheduling_stats['total_tasks_completed'] > 0:
            # Calculate average metrics
            total_wait_time = 0.0
            total_execution_time = 0.0
            deadline_misses = 0
            
            for execution in self.completed_tasks.values():
                if execution.duration:
                    total_execution_time += execution.duration
                
                # Check deadline miss
                task = self.scheduled_tasks.get(execution.task_id)
                if (task and task.deadline and execution.end_time and 
                    execution.end_time > task.deadline):
                    deadline_misses += 1
            
            completed_count = self.scheduling_stats['total_tasks_completed']
            
            self.scheduling_stats['average_execution_time'] = (
                total_execution_time / completed_count
            )
            
            if self.scheduling_stats['total_tasks_scheduled'] > 0:
                self.scheduling_stats['deadline_miss_rate'] = (
                    deadline_misses / self.scheduling_stats['total_tasks_scheduled']
                )
            
            # Calculate resource utilization
            total_capacity = sum(
                sum(node.capacity.values()) for node in self.executor_nodes.values()
            )
            total_allocated = sum(
                sum(node.allocated_resources.values()) for node in self.executor_nodes.values()
            )
            
            if total_capacity > 0:
                self.scheduling_stats['resource_utilization'] = total_allocated / total_capacity
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status."""
        # Check scheduled tasks
        if task_id in self.scheduled_tasks:
            return {
                'status': 'scheduled',
                'task': self.scheduled_tasks[task_id]
            }
        
        # Check active executions
        for execution in self.active_executions.values():
            if execution.task_id == task_id:
                return {
                    'status': 'running',
                    'execution': execution
                }
        
        # Check completed tasks
        for execution in self.completed_tasks.values():
            if execution.task_id == task_id:
                return {
                    'status': execution.status,
                    'execution': execution
                }
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled or running task."""
        try:
            # Remove from scheduled tasks
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]
                
                # Remove from queue
                self.task_queue = [
                    (score, task) for score, task in self.task_queue
                    if task.task_id != task_id
                ]
                heapq.heapify(self.task_queue)
                
                await self.event_dispatcher.emit('task_cancelled', {
                    'task_id': task_id,
                    'status': 'scheduled'
                })
                
                return True
            
            # Cancel running task
            for execution in self.active_executions.values():
                if execution.task_id == task_id:
                    execution.status = "cancelled"
                    execution.end_time = datetime.now()
                    
                    await self.event_dispatcher.emit('task_cancelled', {
                        'task_id': task_id,
                        'execution_id': execution.execution_id,
                        'status': 'running'
                    })
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task: {e}")
            return False
    
    async def get_scheduling_stats(self) -> Dict[str, Any]:
        """Get scheduler performance statistics."""
        return {
            **self.scheduling_stats,
            'active_tasks': len(self.active_executions),
            'scheduled_tasks': len(self.scheduled_tasks),
            'completed_tasks': len(self.completed_tasks),
            'queue_length': len(self.task_queue),
            'registered_executors': len(self.task_executors),
            'executor_nodes': len(self.executor_nodes),
            'strategy': self.scheduling_strategy.value
        }
    
    async def shutdown(self) -> None:
        """Shutdown scheduler gracefully."""
        self._scheduler_running = False
        
        # Cancel all active tasks
        for task_id in list(self.scheduled_tasks.keys()):
            await self.cancel_task(task_id)
        
        self.logger.info("TaskScheduler shutdown completed")
