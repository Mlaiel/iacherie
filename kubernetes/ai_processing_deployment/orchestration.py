"""Advanced AI Processing Orchestration Engine
==========================================

Enterprise-grade orchestration system for coordinating complex AI processing workflows,
managing distributed tasks, and ensuring reliable execution across multiple nodes.

Features:
- Distributed workflow orchestration and execution
- Advanced task scheduling and load balancing
- Fault tolerance and automatic recovery mechanisms
- Real-time workflow monitoring and health checks
- Dynamic resource allocation and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Set, Tuple
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import PriorityQueue
import threading
import weakref

import redis.asyncio as aioredis
from celery import Celery
from celery.result import AsyncResult
from kubernetes import client as k8s_client
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, start_http_server

from .core import ProcessingConfig, AIModelType, ProcessingRequest, ProcessingResult
from .configuration import CompleteAIProcessingConfig, Environment
from .monitoring import MetricsCollector, HealthMonitor
from .model_management import ModelManager

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """
Task execution status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class WorkflowStatus(Enum):
    """
Workflow execution status."""

    CREATED = "created"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResourceType(Enum):
    """Types of computational resources."""

    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"


@dataclass
class TaskDefinition:
    """Definition of a processing task."""
    task_id: str
    task_type: str
    task_name: str
    priority: TaskPriority = TaskPriority.NORMAL
    
    # Execution parameters
    processing_request: ProcessingRequest = None
    model_type: AIModelType = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Resource requirements
    cpu_cores: float = 1.0
    memory_mb: int = 1024
    gpu_required: bool = False
    gpu_memory_mb: int = 0
    estimated_duration_seconds: int = 60
    
    # Dependencies and constraints
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    max_retries: int = 3
    retry_delay_seconds: int = 5
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """Task execution instance with runtime information."""
    execution_id: str
    task_definition: TaskDefinition
    status: TaskStatus = TaskStatus.PENDING
    
    # Execution tracking
    worker_id: Optional[str] = None
    node_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and errors
    result: Optional[ProcessingResult] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Performance metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_usage_percent: float = 0.0
    processing_time_seconds: float = 0.0
    
    # Progress tracking
    progress_percent: float = 0.0
    current_step: str = ""
    estimated_remaining_seconds: int = 0


@dataclass
class WorkflowDefinition:
    """Definition of a processing workflow."""
    workflow_id: str
    workflow_name: str
    description: str = ""
    
    # Tasks and dependencies
    tasks: List[TaskDefinition] = field(default_factory=list)
    task_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    # Execution parameters
    parallel_execution: bool = True
    max_concurrent_tasks: int = 10
    workflow_timeout_seconds: int = 3600
    
    # Retry and error handling
    retry_failed_tasks: bool = True
    continue_on_task_failure: bool = False
    rollback_on_failure: bool = False
    
    # Scheduling
    schedule_expression: Optional[str] = None  # Cron expression
    scheduled_execution_times: List[datetime] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    version: str = "1.0.0"
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution instance with runtime information."""
    execution_id: str
    workflow_definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.CREATED
    
    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    
    # Task executions
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    
    # Progress and metrics
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    progress_percent: float = 0.0
    
    # Resource usage
    total_cpu_time_seconds: float = 0.0
    total_memory_usage_mb: float = 0.0
    total_gpu_time_seconds: float = 0.0


@dataclass
class NodeCapacity:
    """
Computational node capacity information."""
    node_id: str
    node_name: str
    
    # Resource capacity
    total_cpu_cores: float
    total_memory_mb: int
    total_gpu_count: int
    total_gpu_memory_mb: int
    total_storage_gb: int
    
    # Current usage
    used_cpu_cores: float = 0.0
    used_memory_mb: int = 0
    used_gpu_count: int = 0
    used_gpu_memory_mb: int = 0
    used_storage_gb: int = 0
    
    # Status
    is_available: bool = True
    is_healthy: bool = True
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    
    # Capabilities
    supported_model_types: List[AIModelType] = field(default_factory=list)
    node_labels: Dict[str, str] = field(default_factory=dict)


class TaskScheduler:
    """
    Advanced task scheduler with priority-based scheduling,
    resource optimization, and load balancing.
    """
    
    def __init__(self, config: CompleteAIProcessingConfig):
        """
Initialize task scheduler."""
        self.config = config
        self.task_queue = PriorityQueue()
        self.running_tasks: Dict[str, TaskExecution] = {}
        self.completed_tasks: Dict[str, TaskExecution] = {}
        self.failed_tasks: Dict[str, TaskExecution] = {}
        self.node_capacities: Dict[str, NodeCapacity] = {}
        self.worker_pool = ThreadPoolExecutor(max_workers=config.processing.max_workers)
        self.scheduler_lock = threading.Lock()
        self.is_running = False
        
        # Metrics
        self.tasks_scheduled = Counter('ai_tasks_scheduled_total', 'Total tasks scheduled')
        self.tasks_completed = Counter('ai_tasks_completed_total', 'Total tasks completed')
        self.tasks_failed = Counter('ai_tasks_failed_total', 'Total tasks failed')
        self.scheduling_duration = Histogram('ai_scheduling_duration_seconds', 'Task scheduling duration')
        self.queue_size = Gauge('ai_task_queue_size', 'Current task queue size')
        
    def add_node(self, node_capacity: NodeCapacity):
        """
Add computational node to scheduler."""
        with self.scheduler_lock:
            self.node_capacities[node_capacity.node_id] = node_capacity
            logger.info(f"Added node to scheduler: {node_capacity.node_name}")
    
    def remove_node(self, node_id: str):
        """Remove computational node from scheduler."""
        with self.scheduler_lock:
            if node_id in self.node_capacities:
                # Move running tasks to other nodes
                self._reschedule_node_tasks(node_id)
                del self.node_capacities[node_id]
                logger.info(f"Removed node from scheduler: {node_id}")
    
    def _reschedule_node_tasks(self, node_id: str):
        """Reschedule tasks from unavailable node."""
        tasks_to_reschedule = []
        
        for task_id, execution in self.running_tasks.items():
            if execution.node_id == node_id:
                tasks_to_reschedule.append(execution)
        
        for execution in tasks_to_reschedule:
            # Mark as failed and reschedule
            execution.status = TaskStatus.FAILED
            execution.error_message = f"Node {node_id} became unavailable"
            self.schedule_task(execution.task_definition)
            
            logger.warning(f"Rescheduled task {execution.task_definition.task_id} from unavailable node")
    
    def schedule_task(self, task_definition: TaskDefinition) -> str:
        """Schedule task for execution."""
        with self.scheduling_duration.time():
            execution_id = str(uuid.uuid4())
            
            # Create task execution
            execution = TaskExecution(
                execution_id=execution_id,
                task_definition=task_definition,
                status=TaskStatus.QUEUED
            )
            
            # Add to priority queue
            priority = task_definition.priority.value
            self.task_queue.put((-priority, time.time(), execution))
            
            self.tasks_scheduled.inc()
            self.queue_size.set(self.task_queue.qsize())
            
            logger.info(f"Scheduled task: {task_definition.task_name} with priority {task_definition.priority.name}")
            return execution_id
    
    def find_best_node(self, task_definition: TaskDefinition) -> Optional[NodeCapacity]:
        """Find the best node for task execution based on resources and constraints."""
        best_node = None
        best_score = -1
        
        for node_id, node in self.node_capacities.items():
            if not node.is_available or not node.is_healthy:
                continue
            
            # Check resource requirements
            if not self._node_has_sufficient_resources(node, task_definition):
                continue
            
            # Check model type support
            if (task_definition.model_type and 
                task_definition.model_type not in node.supported_model_types):
                continue
            
            # Calculate node score based on resource utilization and performance
            score = self._calculate_node_score(node, task_definition)
            
            if score > best_score:
                best_score = score
                best_node = node
        
        return best_node
    
    def _node_has_sufficient_resources(self, node: NodeCapacity, task: TaskDefinition) -> bool:
        """
Check if node has sufficient resources for task."""
        # CPU check
        if (node.used_cpu_cores + task.cpu_cores) > node.total_cpu_cores:
            return False
        
        # Memory check
        if (node.used_memory_mb + task.memory_mb) > node.total_memory_mb:
            return False
        
        # GPU check
        if task.gpu_required:
            if node.used_gpu_count >= node.total_gpu_count:
                return False
            if (node.used_gpu_memory_mb + task.gpu_memory_mb) > node.total_gpu_memory_mb:
                return False
        
        return True
    
    def _calculate_node_score(self, node: NodeCapacity, task: TaskDefinition) -> float:
        """
Calculate node score for task assignment."""
        # Resource utilization score (prefer less utilized nodes)
        cpu_utilization = node.used_cpu_cores / node.total_cpu_cores
        memory_utilization = node.used_memory_mb / node.total_memory_mb
        
        # Base score (lower utilization = higher score)
        utilization_score = 1.0 - (cpu_utilization + memory_utilization) / 2.0
        
        # GPU preference score
        gpu_score = 1.0
        if task.gpu_required and node.total_gpu_count > 0:
            gpu_utilization = node.used_gpu_count / node.total_gpu_count
            gpu_score = 1.0 - gpu_utilization
        
        # Node health score
        health_score = 1.0 if node.is_healthy else 0.0
        
        # Combine scores
        total_score = (utilization_score * 0.5 + gpu_score * 0.3 + health_score * 0.2)
        
        return total_score
    
    async def start_scheduler(self):
        """
Start the task scheduler."""
        self.is_running = True
        logger.info("Task scheduler started")
        
        # Start scheduler loop
        scheduler_task = asyncio.create_task(self._scheduler_loop())
        return scheduler_task
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                # Check for new tasks to schedule
                if not self.task_queue.empty():
                    _, _, execution = self.task_queue.get_nowait()
                    
                    # Find best node for execution
                    best_node = self.find_best_node(execution.task_definition)
                    
                    if best_node:
                        # Assign task to node
                        await self._assign_task_to_node(execution, best_node)
                    else:
                        # No suitable node available, put back in queue
                        priority = execution.task_definition.priority.value
                        self.task_queue.put((-priority, time.time(), execution))
                
                # Update queue size metric
                self.queue_size.set(self.task_queue.qsize())
                
                # Update node heartbeats
                await self._update_node_heartbeats()
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                await asyncio.sleep(1)  # Schedule every second
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5)
    
    async def _assign_task_to_node(self, execution: TaskExecution, node: NodeCapacity):
        """Assign task execution to specific node."""
        try:
            # Update execution info
            execution.node_id = node.node_id
            execution.status = TaskStatus.RUNNING
            execution.started_at = datetime.utcnow()
            
            # Reserve node resources
            self._reserve_node_resources(node, execution.task_definition)
            
            # Add to running tasks
            self.running_tasks[execution.execution_id] = execution
            
            # Submit task for execution
            future = self.worker_pool.submit(self._execute_task, execution)
            
            logger.info(f"Assigned task {execution.task_definition.task_name} to node {node.node_name}")
            
        except Exception as e:
            logger.error(f"Failed to assign task to node: {e}")
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
    
    def _reserve_node_resources(self, node: NodeCapacity, task: TaskDefinition):
        """Reserve node resources for task execution."""
        node.used_cpu_cores += task.cpu_cores
        node.used_memory_mb += task.memory_mb
        
        if task.gpu_required:
            node.used_gpu_count += 1
            node.used_gpu_memory_mb += task.gpu_memory_mb
    
    def _release_node_resources(self, node: NodeCapacity, task: TaskDefinition):
        """
Release node resources after task completion."""
        node.used_cpu_cores = max(0, node.used_cpu_cores - task.cpu_cores)
        node.used_memory_mb = max(0, node.used_memory_mb - task.memory_mb)
        
        if task.gpu_required:
            node.used_gpu_count = max(0, node.used_gpu_count - 1)
            node.used_gpu_memory_mb = max(0, node.used_gpu_memory_mb - task.gpu_memory_mb)
    
    def _execute_task(self, execution: TaskExecution) -> TaskExecution:
        """
Execute task and return updated execution info."""
        try:
            start_time = time.time()
            
            # Update progress
            execution.progress_percent = 10.0
            execution.current_step = "Initializing"
            
            # Simulate task execution
            # In real implementation, this would call the actual processing functions
            if execution.task_definition.processing_request:
                # Process the request
                execution.current_step = "Processing"
                execution.progress_percent = 50.0
                
                # Simulate processing time
                time.sleep(min(execution.task_definition.estimated_duration_seconds, 10))
                
                # Create result
                execution.result = ProcessingResult(
                    request_id=execution.task_definition.processing_request.request_id,
                    success=True,
                    processing_time=time.time() - start_time,
                    results={"processed": True, "execution_id": execution.execution_id}
                )
            
            # Complete task
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.progress_percent = 100.0
            execution.current_step = "Completed"
            execution.processing_time_seconds = time.time() - start_time
            
            self.tasks_completed.inc()
            logger.info(f"Task completed successfully: {execution.task_definition.task_name}")
            
        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            self.tasks_failed.inc()
            logger.error(f"Task execution failed: {execution.task_definition.task_name} - {e}")
        
        finally:
            # Release node resources
            if execution.node_id and execution.node_id in self.node_capacities:
                node = self.node_capacities[execution.node_id]
                self._release_node_resources(node, execution.task_definition)
            
            # Move from running to completed/failed
            if execution.execution_id in self.running_tasks:
                del self.running_tasks[execution.execution_id]
            
            if execution.status == TaskStatus.COMPLETED:
                self.completed_tasks[execution.execution_id] = execution
            else:
                self.failed_tasks[execution.execution_id] = execution
        
        return execution
    
    async def _update_node_heartbeats(self):
        """Update node heartbeat information."""
        current_time = datetime.utcnow()
        heartbeat_timeout = timedelta(minutes=5)
        
        for node_id, node in self.node_capacities.items():
            if current_time - node.last_heartbeat > heartbeat_timeout:
                if node.is_available:
                    node.is_available = False
                    node.is_healthy = False
                    logger.warning(f"Node {node.node_name} heartbeat timeout")
    
    def _cleanup_completed_tasks(self):
        """Clean up old completed and failed tasks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean completed tasks
        completed_to_remove = []
        for execution_id, execution in self.completed_tasks.items():
            if execution.completed_at and execution.completed_at < cutoff_time:
                completed_to_remove.append(execution_id)
        
        for execution_id in completed_to_remove:
            del self.completed_tasks[execution_id]
        
        # Clean failed tasks
        failed_to_remove = []
        for execution_id, execution in self.failed_tasks.items():
            if execution.completed_at and execution.completed_at < cutoff_time:
                failed_to_remove.append(execution_id)
        
        for execution_id in failed_to_remove:
            del self.failed_tasks[execution_id]
    
    def get_task_status(self, execution_id: str) -> Optional[TaskExecution]:
        """
Get current task execution status."""
        # Check running tasks
        if execution_id in self.running_tasks:
            return self.running_tasks[execution_id]
        
        # Check completed tasks
        if execution_id in self.completed_tasks:
            return self.completed_tasks[execution_id]
        
        # Check failed tasks
        if execution_id in self.failed_tasks:
            return self.failed_tasks[execution_id]
        
        return None
    
    def cancel_task(self, execution_id: str) -> bool:
        """
Cancel task execution."""
        if execution_id in self.running_tasks:
            execution = self.running_tasks[execution_id]
            execution.status = TaskStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            
            # Release resources
            if execution.node_id and execution.node_id in self.node_capacities:
                node = self.node_capacities[execution.node_id]
                self._release_node_resources(node, execution.task_definition)
            
            # Move to failed tasks
            del self.running_tasks[execution_id]
            self.failed_tasks[execution_id] = execution
            
            logger.info(f"Cancelled task: {execution.task_definition.task_name}")
            return True
        
        return False
    
    async def stop_scheduler(self):
        """Stop the task scheduler."""
        self.is_running = False
        
        # Cancel all running tasks
        for execution_id in list(self.running_tasks.keys()):
            self.cancel_task(execution_id)
        
        # Shutdown worker pool
        self.worker_pool.shutdown(wait=True)
        
        logger.info("Task scheduler stopped")


class WorkflowOrchestrator:
    """
    Advanced workflow orchestrator for managing complex multi-task workflows
    with dependency resolution, parallel execution, and fault tolerance.
    """
    
    def __init__(self, config: CompleteAIProcessingConfig, task_scheduler: TaskScheduler):
        """
Initialize workflow orchestrator."""
        self.config = config
        self.task_scheduler = task_scheduler
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.running_workflows: Dict[str, WorkflowExecution] = {}
        self.completed_workflows: Dict[str, WorkflowExecution] = {}
        self.workflow_lock = asyncio.Lock()
        
        # Metrics
        self.workflows_started = Counter('ai_workflows_started_total', 'Total workflows started')
        self.workflows_completed = Counter('ai_workflows_completed_total', 'Total workflows completed')
        self.workflows_failed = Counter('ai_workflows_failed_total', 'Total workflows failed')
        
    def register_workflow(self, workflow_definition: WorkflowDefinition):
        """
Register workflow definition."""
        self.workflows[workflow_definition.workflow_id] = workflow_definition
        logger.info(f"Registered workflow: {workflow_definition.workflow_name}")
    
    async def start_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> str:
        """Start workflow execution."""
        async with self.workflow_lock:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow_definition = self.workflows[workflow_id]
            execution_id = str(uuid.uuid4())
            
            # Create workflow execution
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_definition=workflow_definition,
                status=WorkflowStatus.SCHEDULED,
                total_tasks=len(workflow_definition.tasks)
            )
            
            # Apply parameters to tasks
            if parameters:
                self._apply_parameters_to_tasks(execution, parameters)
            
            self.running_workflows[execution_id] = execution
            self.workflows_started.inc()
            
            # Start workflow execution task
            asyncio.create_task(self._execute_workflow(execution))
            
            logger.info(f"Started workflow: {workflow_definition.workflow_name}")
            return execution_id
    
    def _apply_parameters_to_tasks(self, execution: WorkflowExecution, parameters: Dict[str, Any]):
        """Apply runtime parameters to workflow tasks."""
        for task in execution.workflow_definition.tasks:
            # Update task parameters with workflow parameters
            task.parameters.update(parameters)
    
    async def _execute_workflow(self, execution: WorkflowExecution):
        """
Execute workflow with dependency resolution and parallel execution."""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.started_at = datetime.utcnow()
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(execution.workflow_definition)
            
            # Execute tasks in dependency order
            await self._execute_tasks_with_dependencies(execution, dependency_graph)
            
            # Complete workflow
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.progress_percent = 100.0
            
            self.workflows_completed.inc()
            logger.info(f"Workflow completed: {execution.workflow_definition.workflow_name}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            
            self.workflows_failed.inc()
            logger.error(f"Workflow failed: {execution.workflow_definition.workflow_name} - {e}")
        
        finally:
            # Move to completed workflows
            async with self.workflow_lock:
                if execution.execution_id in self.running_workflows:
                    del self.running_workflows[execution.execution_id]
                self.completed_workflows[execution.execution_id] = execution
    
    def _build_dependency_graph(self, workflow: WorkflowDefinition) -> Dict[str, Set[str]]:
        """Build task dependency graph."""
        graph = {}
        
        # Initialize graph with all tasks
        for task in workflow.tasks:
            graph[task.task_id] = set()
        
        # Add dependencies
        for task_id, dependencies in workflow.task_dependencies.items():
            if task_id in graph:
                graph[task_id].update(dependencies)
        
        return graph
    
    async def _execute_tasks_with_dependencies(self, execution: WorkflowExecution, 
                                             dependency_graph: Dict[str, Set[str]]):
        """
Execute tasks respecting dependencies and parallel execution limits."""
        completed_tasks = set()
        running_tasks = {}
        task_dict = {task.task_id: task for task in execution.workflow_definition.tasks}
        
        max_concurrent = execution.workflow_definition.max_concurrent_tasks
        
        while len(completed_tasks) < len(task_dict):
            # Find tasks ready to execute
            ready_tasks = []
            for task_id, dependencies in dependency_graph.items():
                if (task_id not in completed_tasks and 
                    task_id not in running_tasks and
                    dependencies.issubset(completed_tasks)):
                    ready_tasks.append(task_id)
            
            # Start ready tasks (up to concurrency limit)
            available_slots = max_concurrent - len(running_tasks)
            for task_id in ready_tasks[:available_slots]:
                task_def = task_dict[task_id]
                
                # Schedule task
                execution_id = self.task_scheduler.schedule_task(task_def)
                running_tasks[task_id] = execution_id
                
                logger.info(f"Started task in workflow: {task_def.task_name}")
            
            # Check for completed tasks
            completed_in_this_iteration = []
            for task_id, task_execution_id in running_tasks.items():
                task_execution = self.task_scheduler.get_task_status(task_execution_id)
                if task_execution and task_execution.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    completed_in_this_iteration.append(task_id)
                    
                    # Store task execution in workflow
                    execution.task_executions[task_id] = task_execution
                    
                    if task_execution.status == TaskStatus.COMPLETED:
                        completed_tasks.add(task_id)
                        execution.completed_tasks += 1
                    else:
                        execution.failed_tasks += 1
                        
                        # Handle task failure
                        if not execution.workflow_definition.continue_on_task_failure:
                            raise Exception(f"Task failed: {task_id} - {task_execution.error_message}")
            
            # Remove completed tasks from running tasks
            for task_id in completed_in_this_iteration:
                del running_tasks[task_id]
            
            # Update workflow progress
            execution.progress_percent = (execution.completed_tasks / execution.total_tasks) * 100.0
            
            # Wait before next iteration
            await asyncio.sleep(1)
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status."""
        if execution_id in self.running_workflows:
            return self.running_workflows[execution_id]
        
        if execution_id in self.completed_workflows:
            return self.completed_workflows[execution_id]
        
        return None
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """
Pause workflow execution."""
        async with self.workflow_lock:
            if execution_id in self.running_workflows:
                execution = self.running_workflows[execution_id]
                execution.status = WorkflowStatus.PAUSED
                execution.paused_at = datetime.utcnow()
                
                # Cancel running tasks
                for task_id, task_execution in execution.task_executions.items():
                    if task_execution.status == TaskStatus.RUNNING:
                        self.task_scheduler.cancel_task(task_execution.execution_id)
                
                logger.info(f"Paused workflow: {execution.workflow_definition.workflow_name}")
                return True
        
        return False
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume paused workflow execution."""
        async with self.workflow_lock:
            if execution_id in self.running_workflows:
                execution = self.running_workflows[execution_id]
                if execution.status == WorkflowStatus.PAUSED:
                    execution.status = WorkflowStatus.RUNNING
                    execution.paused_at = None
                    
                    # Restart workflow execution
                    asyncio.create_task(self._execute_workflow(execution))
                    
                    logger.info(f"Resumed workflow: {execution.workflow_definition.workflow_name}")
                    return True
        
        return False
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel workflow execution."""
        async with self.workflow_lock:
            if execution_id in self.running_workflows:
                execution = self.running_workflows[execution_id]
                execution.status = WorkflowStatus.CANCELLED
                execution.completed_at = datetime.utcnow()
                
                # Cancel all running tasks
                for task_id, task_execution in execution.task_executions.items():
                    if task_execution.status == TaskStatus.RUNNING:
                        self.task_scheduler.cancel_task(task_execution.execution_id)
                
                # Move to completed workflows
                del self.running_workflows[execution_id]
                self.completed_workflows[execution_id] = execution
                
                logger.info(f"Cancelled workflow: {execution.workflow_definition.workflow_name}")
                return True
        
        return False


class DistributedOrchestrator:
    """
    Distributed orchestration system for coordinating AI processing
    across multiple nodes and clusters with fault tolerance.
    """
    
    def __init__(self, config: CompleteAIProcessingConfig):
        """
Initialize distributed orchestrator."""
        self.config = config
        self.node_id = str(uuid.uuid4())
        self.task_scheduler = TaskScheduler(config)
        self.workflow_orchestrator = WorkflowOrchestrator(config, self.task_scheduler)
        self.redis_client: Optional[aioredis.Redis] = None
        self.celery_app: Optional[Celery] = None
        self.health_monitor = HealthMonitor(config)
        self.metrics_collector = MetricsCollector(config)
        self.is_leader = False
        self.leader_election_lock = asyncio.Lock()
        
        # Node registry
        self.active_nodes: Dict[str, Dict[str, Any]] = {}
        self.node_heartbeat_interval = 30  # seconds
        
    async def initialize(self):
        """
Initialize distributed orchestrator."""
        try:
            # Initialize Redis client
            await self._initialize_redis()
            
            # Initialize Celery
            await self._initialize_celery()
            
            # Register this node
            await self._register_node()
            
            # Start health monitor
            await self.health_monitor.start()
            
            # Start metrics collector
            await self.metrics_collector.start()
            
            # Start task scheduler
            await self.task_scheduler.start_scheduler()
            
            # Start leader election
            asyncio.create_task(self._leader_election_loop())
            
            # Start node heartbeat
            asyncio.create_task(self._heartbeat_loop())
            
            # Start node discovery
            asyncio.create_task(self._node_discovery_loop())
            
            logger.info(f"Distributed orchestrator initialized with node ID: {self.node_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed orchestrator: {e}")
            raise
    
    async def _initialize_redis(self):
        """Initialize Redis client for coordination."""
        if self.config.redis:
            self.redis_client = aioredis.Redis(
                host=self.config.redis.host,
                port=self.config.redis.port,
                db=self.config.redis.database,
                password=self.config.redis.password if self.config.redis.password else None
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis client initialized for distributed coordination")
    
    async def _initialize_celery(self):
        """Initialize Celery for distributed task execution."""
        if self.redis_client:
            redis_url = f"redis://{self.config.redis.host}:{self.config.redis.port}/{self.config.redis.database}"
            
            self.celery_app = Celery(
                'ai_processing',
                broker=redis_url,
                backend=redis_url
            )
            
            # Configure Celery
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                worker_prefetch_multiplier=1,
                task_acks_late=True,
                worker_max_tasks_per_child=1000
            )
            
            logger.info("Celery initialized for distributed task execution")
    
    async def _register_node(self):
        """Register this node in the distributed system."""
        if not self.redis_client:
            return
        
        node_info = {
            'node_id': self.node_id,
            'node_name': f"ai-processing-{self.node_id[:8]}",
            'status': 'active',
            'capabilities': {
                'max_workers': self.config.processing.max_workers,
                'gpu_enabled': self.config.processing.gpu_enabled,
                'supported_models': [model_type.value for model_type in AIModelType]
            },
            'registered_at': datetime.utcnow().isoformat(),
            'last_heartbeat': datetime.utcnow().isoformat()
        }
        
        await self.redis_client.hset(
            'ai_processing_nodes',
            self.node_id,
            json.dumps(node_info)
        )
        
        logger.info(f"Registered node in distributed system: {node_info['node_name']}")
    
    async def _leader_election_loop(self):
        """Leader election loop using Redis."""
        while True:
            try:
                async with self.leader_election_lock:
                    # Try to become leader
                    leader_key = "ai_processing_leader"
                    leader_ttl = 60  # seconds
                    
                    result = await self.redis_client.set(
                        leader_key, self.node_id, nx=True, ex=leader_ttl
                    )
                    
                    if result:
                        if not self.is_leader:
                            self.is_leader = True
                            logger.info(f"Node {self.node_id} became leader")
                            await self._on_become_leader()
                    else:
                        # Check if we're still the leader
                        current_leader = await self.redis_client.get(leader_key)
                        if current_leader != self.node_id.encode():
                            if self.is_leader:
                                self.is_leader = False
                                logger.info(f"Node {self.node_id} lost leadership")
                                await self._on_lose_leadership()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in leader election: {e}")
                await asyncio.sleep(10)
    
    async def _on_become_leader(self):
        """Actions to take when becoming leader."""
        # Leader is responsible for workflow scheduling and cluster coordination
        logger.info("Taking leadership responsibilities")
    
    async def _on_lose_leadership(self):
        """Actions to take when losing leadership."""
        # Stop leader-specific tasks
        logger.info("Relinquishing leadership responsibilities")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to indicate node health."""
        while True:
            try:
                if self.redis_client:
                    heartbeat_data = {
                        'node_id': self.node_id,
                        'timestamp': datetime.utcnow().isoformat(),
                        'status': 'healthy',
                        'running_tasks': len(self.task_scheduler.running_tasks),
                        'queued_tasks': self.task_scheduler.task_queue.qsize(),
                        'is_leader': self.is_leader
                    }
                    
                    await self.redis_client.hset(
                        'ai_processing_heartbeats',
                        self.node_id,
                        json.dumps(heartbeat_data)
                    )
                
                await asyncio.sleep(self.node_heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(self.node_heartbeat_interval)
    
    async def _node_discovery_loop(self):
        """Discover and monitor other nodes in the cluster."""
        while True:
            try:
                if self.redis_client:
                    # Get all registered nodes
                    nodes_data = await self.redis_client.hgetall('ai_processing_nodes')
                    
                    current_nodes = {}
                    for node_id, node_data in nodes_data.items():
                        node_id = node_id.decode('utf-8')
                        node_info = json.loads(node_data.decode('utf-8'))
                        current_nodes[node_id] = node_info
                    
                    # Update active nodes
                    self.active_nodes = current_nodes
                    
                    # Update task scheduler with node information
                    await self._update_scheduler_nodes()
                
                await asyncio.sleep(60)  # Discovery every minute
                
            except Exception as e:
                logger.error(f"Error in node discovery: {e}")
                await asyncio.sleep(60)
    
    async def _update_scheduler_nodes(self):
        """Update task scheduler with current node information."""
        current_time = datetime.utcnow()
        
        for node_id, node_info in self.active_nodes.items():
            # Check node health based on heartbeat
            heartbeat_data = await self.redis_client.hget('ai_processing_heartbeats', node_id)
            
            if heartbeat_data:
                heartbeat_info = json.loads(heartbeat_data.decode('utf-8'))
                heartbeat_time = datetime.fromisoformat(heartbeat_info['timestamp'])
                
                is_healthy = (current_time - heartbeat_time).total_seconds() < 120  # 2 minutes
                
                # Create or update node capacity
                node_capacity = NodeCapacity(
                    node_id=node_id,
                    node_name=node_info.get('node_name', f"node-{node_id[:8]}"),
                    total_cpu_cores=node_info['capabilities']['max_workers'],
                    total_memory_mb=8192,  # Default value
                    total_gpu_count=1 if node_info['capabilities']['gpu_enabled'] else 0,
                    total_gpu_memory_mb=8192 if node_info['capabilities']['gpu_enabled'] else 0,
                    total_storage_gb=100,  # Default value
                    is_available=is_healthy,
                    is_healthy=is_healthy,
                    last_heartbeat=heartbeat_time,
                    supported_model_types=[AIModelType(mt) for mt in node_info['capabilities']['supported_models']]
                )
                
                self.task_scheduler.add_node(node_capacity)
    
    async def submit_processing_request(self, request: ProcessingRequest) -> str:
        """Submit processing request for distributed execution."""
        # Create task definition
        task_definition = TaskDefinition(
            task_id=str(uuid.uuid4()),
            task_type="ai_processing",
            task_name=f"process_{request.content_type}",
            processing_request=request,
            model_type=request.model_type,
            parameters={'request_id': request.request_id}
        )
        
        # Schedule task
        execution_id = self.task_scheduler.schedule_task(task_definition)
        
        logger.info(f"Submitted processing request for distributed execution: {request.request_id}")
        return execution_id
    
    async def submit_workflow(self, workflow_definition: WorkflowDefinition) -> str:
        """Submit workflow for distributed execution."""
        # Register workflow
        self.workflow_orchestrator.register_workflow(workflow_definition)
        
        # Start workflow execution
        execution_id = await self.workflow_orchestrator.start_workflow(workflow_definition.workflow_id)
        
        logger.info(f"Submitted workflow for distributed execution: {workflow_definition.workflow_name}")
        return execution_id
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status."""
        total_nodes = len(self.active_nodes)
        healthy_nodes = sum(1 for node in self.active_nodes.values() 
                          if node.get('status') == 'active')
        
        total_running_tasks = sum(len(self.task_scheduler.running_tasks) 
                                for _ in self.active_nodes)
        total_queued_tasks = self.task_scheduler.task_queue.qsize()
        
        return {
            'cluster_id': 'ai-processing-cluster',
            'leader_node': await self._get_current_leader(),
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'total_running_tasks': total_running_tasks,
            'total_queued_tasks': total_queued_tasks,
            'active_workflows': len(self.workflow_orchestrator.running_workflows),
            'cluster_health': 'healthy' if healthy_nodes > 0 else 'unhealthy'
        }
    
    async def _get_current_leader(self) -> Optional[str]:
        """
Get current cluster leader."""
        if self.redis_client:
            leader = await self.redis_client.get("ai_processing_leader")
            return leader.decode('utf-8') if leader else None
        return None
    
    async def shutdown(self):
        """Shutdown distributed orchestrator."""
        try:
            # Stop task scheduler
            await self.task_scheduler.stop_scheduler()
            
            # Stop health monitor
            await self.health_monitor.stop()
            
            # Stop metrics collector
            await self.metrics_collector.stop()
            
            # Unregister node
            if self.redis_client:
                await self.redis_client.hdel('ai_processing_nodes', self.node_id)
                await self.redis_client.hdel('ai_processing_heartbeats', self.node_id)
                await self.redis_client.close()
            
            logger.info("Distributed orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during distributed orchestrator shutdown: {e}")


# Factory functions for easy setup
async def create_distributed_orchestrator(config: CompleteAIProcessingConfig) -> DistributedOrchestrator:
    """Create and initialize distributed orchestrator."""
    orchestrator = DistributedOrchestrator(config)
    await orchestrator.initialize()
    return orchestrator


def create_simple_workflow(name: str, tasks: List[TaskDefinition], 
                         dependencies: Dict[str, List[str]] = None) -> WorkflowDefinition:
    """
Create simple workflow definition."""
    workflow_id = str(uuid.uuid4())
    
    return WorkflowDefinition(
        workflow_id=workflow_id,
        workflow_name=name,
        tasks=tasks,
        task_dependencies=dependencies or {},
        parallel_execution=True,
        max_concurrent_tasks=5
    )


def create_processing_task(content_path: str, model_type: AIModelType, 
                         priority: TaskPriority = TaskPriority.NORMAL) -> TaskDefinition:
    """
Create processing task definition."""
    task_id = str(uuid.uuid4())
    
    processing_request = ProcessingRequest(
        request_id=str(uuid.uuid4()),
        content_type=model_type.value,
        content_path=content_path,
        model_type=model_type
    )
    
    return TaskDefinition(
        task_id=task_id,
        task_type="ai_processing",
        task_name=f"process_{model_type.value}",
        priority=priority,
        processing_request=processing_request,
        model_type=model_type
    )
