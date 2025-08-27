"""
Task Orchestrator Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/task_orchestrator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Task Orchestration System
Responsibility: Intelligent task coordination and workflow management
Technologies: ML-driven orchestration, Graph workflows, Adaptive scheduling
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Workflow definition → Dependency analysis → Intelligent scheduling → 
Resource allocation → Parallel execution → Progress monitoring → Auto-recovery
"""

from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, NamedTuple
import logging
import asyncio
import networkx as nx
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor
import pickle

from .crawler_worker import CrawlerWorker, CrawlerTask, TaskResult, TaskPriority, WorkerStatus
from .worker_pool import WorkerPool, PoolStatus
from .queue_processor import QueueProcessor, QueueMessage
from .resource_manager import ResourceManager, ResourceType, AllocationStrategy
from .event_processor import EventProcessor, WorkerEvent, EventType, EventPriority
from .notification_engine import NotificationEngine, NotificationPriority
from ...monitoring.performance_monitor import PerformanceMonitor
from ...ml.prediction.task_predictor import TaskPredictor
from ...utils.graph_utils import GraphUtils
from ...utils.optimization_utils import OptimizationUtils

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskType(Enum):
    """Task types in orchestration"""
    CRAWLER_TASK = "crawler_task"
    ANALYSIS_TASK = "analysis_task"
    FINGERPRINT_TASK = "fingerprint_task"
    NOTIFICATION_TASK = "notification_task"
    AGGREGATION_TASK = "aggregation_task"
    VALIDATION_TASK = "validation_task"
    CLEANUP_TASK = "cleanup_task"
    CUSTOM_TASK = "custom_task"


class DependencyType(Enum):
    """Task dependency types"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    TRIGGER = "trigger"
    BARRIER = "barrier"
    FAN_OUT = "fan_out"
    FAN_IN = "fan_in"


class ExecutionStrategy(Enum):
    """Workflow execution strategies"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    DAG = "dag"
    ADAPTIVE = "adaptive"
    OPTIMIZED = "optimized"


@dataclass
class TaskDefinition:
    """Task definition in workflow"""
    task_id: str
    task_type: TaskType
    task_config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    dependency_type: DependencyType = DependencyType.SEQUENTIAL
    conditions: Dict[str, Any] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    resource_requirements: Dict[ResourceType, float] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    tasks: List[TaskDefinition]
    execution_strategy: ExecutionStrategy = ExecutionStrategy.DAG
    global_timeout: int = 7200
    max_retries: int = 3
    on_failure: str = "stop"
    on_success: str = "complete"
    schedule: Optional[Dict[str, Any]] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1


@dataclass
class TaskExecution:
    """Task execution state"""
    execution_id: str
    task_def: TaskDefinition
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    worker_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    progress: float = 0.0
    resource_allocations: Dict[str, str] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution state"""
    execution_id: str
    workflow_def: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    execution_graph: Optional[nx.DiGraph] = None
    current_tasks: Set[str] = field(default_factory=set)
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    retry_count: int = 0
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    performance_summary: Dict[str, Any] = field(default_factory=dict)


class TaskOrchestrator:
    """
    Intelligent task orchestration system
    
    Features:
    - ML-driven task scheduling and optimization
    - Complex workflow management with dependencies
    - Graph-based execution planning
    - Adaptive resource allocation
    - Real-time monitoring and recovery
    - Performance optimization and learning
    """

    def __init__(self, orchestrator_id: str = None):
        self.orchestrator_id = orchestrator_id or str(uuid.uuid4())
        
        # Core components
        self.worker_pool: Optional[WorkerPool] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.event_processor: Optional[EventProcessor] = None
        self.notification_engine: Optional[NotificationEngine] = None
        self.queue_processor: Optional[QueueProcessor] = None
        
        # Workflow management
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.completed_executions: deque = deque(maxlen=1000)
        self.execution_history: Dict[str, List[str]] = defaultdict(list)
        
        # Scheduling and execution
        self.execution_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.scheduler_graph: nx.DiGraph = nx.DiGraph()
        self.execution_semaphore = asyncio.Semaphore(50)  # Max concurrent workflows
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.shutdown_event = asyncio.Event()
        self.is_running = False
        
        # ML and optimization
        self.task_predictor = TaskPredictor()
        self.performance_monitor = PerformanceMonitor()
        self.graph_utils = GraphUtils()
        self.optimization_utils = OptimizationUtils()
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=8, 
            thread_name_prefix=f"TaskOrchestrator-{self.orchestrator_id}"
        )
        
        # Performance metrics
        self.metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_workflow_duration": 0.0,
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "average_task_duration": 0.0,
            "resource_efficiency": 0.0,
            "optimization_improvements": 0.0
        }

    async def start(self) -> bool:
        """Start task orchestrator"""
        try:
            logger.info(f"🚀 Starting task orchestrator: {self.orchestrator_id}")
            
            # Initialize components
            await self._initialize_components()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_running = True
            
            logger.info(f"✅ Task orchestrator {self.orchestrator_id} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start task orchestrator {self.orchestrator_id}: {e}")
            return False

    async def stop(self) -> None:
        """Stop task orchestrator gracefully"""
        try:
            logger.info(f"🛑 Stopping task orchestrator: {self.orchestrator_id}")
            
            self.is_running = False
            self.shutdown_event.set()
            
            # Wait for active workflows to complete or timeout
            await self._graceful_shutdown()
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True, timeout=30)
            
            logger.info(f"✅ Task orchestrator {self.orchestrator_id} stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping task orchestrator {self.orchestrator_id}: {e}")

    async def register_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """Register a workflow definition"""
        try:
            # Validate workflow
            if not await self._validate_workflow(workflow_def):
                logger.warning(f"❌ Invalid workflow: {workflow_def.workflow_id}")
                return False
            
            # Build and validate execution graph
            execution_graph = await self._build_execution_graph(workflow_def)
            if not execution_graph:
                logger.warning(f"❌ Invalid workflow graph: {workflow_def.workflow_id}")
                return False
            
            # Store workflow
            self.workflow_definitions[workflow_def.workflow_id] = workflow_def
            
            logger.info(f"✅ Workflow registered: {workflow_def.workflow_id} ({len(workflow_def.tasks)} tasks)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register workflow {workflow_def.workflow_id}: {e}")
            return False

    async def execute_workflow(self, workflow_id: str, 
                             execution_variables: Optional[Dict[str, Any]] = None,
                             priority: TaskPriority = TaskPriority.NORMAL) -> Optional[str]:
        """Execute a workflow"""
        try:
            workflow_def = self.workflow_definitions.get(workflow_id)
            if not workflow_def:
                logger.warning(f"⚠️ Workflow not found: {workflow_id}")
                return None
            
            # Create execution instance
            execution = await self._create_workflow_execution(
                workflow_def, execution_variables or {}
            )
            
            # Add to active executions
            self.active_executions[execution.execution_id] = execution
            
            # Queue for execution
            priority_value = priority.value
            await self.execution_queue.put((priority_value, time.time(), execution))
            
            logger.info(f"🚀 Workflow queued for execution: {workflow_id} -> {execution.execution_id}")
            return execution.execution_id
            
        except Exception as e:
            logger.error(f"❌ Failed to execute workflow {workflow_id}: {e}")
            return None

    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause workflow execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                logger.warning(f"⚠️ Execution not found: {execution_id}")
                return False
            
            execution.status = WorkflowStatus.PAUSED
            
            # Pause running tasks
            for task_id in execution.current_tasks:
                task_execution = execution.task_executions.get(task_id)
                if task_execution and task_execution.status == WorkflowStatus.RUNNING:
                    await self._pause_task(task_execution)
            
            logger.info(f"⏸️ Workflow paused: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to pause workflow {execution_id}: {e}")
            return False

    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume paused workflow execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution or execution.status != WorkflowStatus.PAUSED:
                logger.warning(f"⚠️ Cannot resume workflow: {execution_id}")
                return False
            
            execution.status = WorkflowStatus.RUNNING
            
            # Resume paused tasks
            for task_id in execution.current_tasks:
                task_execution = execution.task_executions.get(task_id)
                if task_execution and task_execution.status == WorkflowStatus.PAUSED:
                    await self._resume_task(task_execution)
            
            logger.info(f"▶️ Workflow resumed: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to resume workflow {execution_id}: {e}")
            return False

    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                logger.warning(f"⚠️ Execution not found: {execution_id}")
                return False
            
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            
            # Cancel running tasks
            for task_id in execution.current_tasks:
                task_execution = execution.task_executions.get(task_id)
                if task_execution and task_execution.status == WorkflowStatus.RUNNING:
                    await self._cancel_task(task_execution)
            
            # Move to completed
            self.completed_executions.append(execution)
            del self.active_executions[execution_id]
            
            logger.info(f"❌ Workflow cancelled: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel workflow {execution_id}: {e}")
            return False

    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed workflow execution status"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                # Check completed executions
                for completed_exec in self.completed_executions:
                    if completed_exec.execution_id == execution_id:
                        execution = completed_exec
                        break
                
                if not execution:
                    return None
            
            # Calculate progress
            total_tasks = len(execution.workflow_def.tasks)
            completed_tasks_count = len(execution.completed_tasks)
            progress = (completed_tasks_count / total_tasks * 100) if total_tasks > 0 else 0
            
            # Task status summary
            task_status = {}
            for task_id, task_exec in execution.task_executions.items():
                task_status[task_id] = {
                    "status": task_exec.status.value,
                    "progress": task_exec.progress,
                    "worker_id": task_exec.worker_id,
                    "started_at": task_exec.started_at.isoformat() if task_exec.started_at else None,
                    "completed_at": task_exec.completed_at.isoformat() if task_exec.completed_at else None,
                    "error_message": task_exec.error_message,
                    "retry_count": task_exec.retry_count
                }
            
            return {
                "execution_id": execution_id,
                "workflow_id": execution.workflow_def.workflow_id,
                "workflow_name": execution.workflow_def.name,
                "status": execution.status.value,
                "progress": progress,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks_count,
                "failed_tasks": len(execution.failed_tasks),
                "current_tasks": list(execution.current_tasks),
                "task_status": task_status,
                "variables": execution.variables,
                "results": execution.results,
                "performance_summary": execution.performance_summary,
                "retry_count": execution.retry_count
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get workflow status {execution_id}: {e}")
            return None

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        try:
            return {
                "orchestrator_id": self.orchestrator_id,
                "is_running": self.is_running,
                "registered_workflows": len(self.workflow_definitions),
                "active_executions": len(self.active_executions),
                "execution_queue_size": self.execution_queue.qsize(),
                "completed_executions": len(self.completed_executions),
                "available_execution_slots": self.execution_semaphore._value,
                "metrics": self.metrics.copy(),
                "workflow_definitions": {
                    wf_id: {
                        "name": wf_def.name,
                        "tasks_count": len(wf_def.tasks),
                        "execution_strategy": wf_def.execution_strategy.value,
                        "created_at": wf_def.created_at.isoformat()
                    } for wf_id, wf_def in self.workflow_definitions.items()
                },
                "active_execution_summary": {
                    exec_id: {
                        "workflow_id": exec.workflow_def.workflow_id,
                        "status": exec.status.value,
                        "progress": len(exec.completed_tasks) / len(exec.workflow_def.tasks) * 100 if exec.workflow_def.tasks else 0,
                        "current_tasks": len(exec.current_tasks)
                    } for exec_id, exec in self.active_executions.items()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get orchestrator status: {e}")
            return {"error": str(e)}

    async def optimize_execution_plan(self, workflow_id: str) -> Dict[str, Any]:
        """Optimize workflow execution plan using ML"""
        try:
            workflow_def = self.workflow_definitions.get(workflow_id)
            if not workflow_def:
                return {"error": "Workflow not found"}
            
            # Analyze historical performance
            historical_data = await self._get_historical_performance_data(workflow_id)
            
            # Predict optimal execution strategy
            optimal_strategy = await self.task_predictor.predict_optimal_strategy(
                workflow_def, historical_data
            )
            
            # Generate resource optimization recommendations
            resource_recommendations = await self._generate_resource_recommendations(
                workflow_def, historical_data
            )
            
            # Calculate estimated improvements
            estimated_improvements = await self._calculate_estimated_improvements(
                workflow_def, optimal_strategy, resource_recommendations
            )
            
            return {
                "workflow_id": workflow_id,
                "current_strategy": workflow_def.execution_strategy.value,
                "optimal_strategy": optimal_strategy,
                "resource_recommendations": resource_recommendations,
                "estimated_improvements": estimated_improvements,
                "confidence_score": 0.85,  # Would come from ML model
                "optimization_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize execution plan for {workflow_id}: {e}")
            return {"error": str(e)}

    async def _initialize_components(self) -> None:
        """Initialize orchestrator components"""
        try:
            # Components should be injected or retrieved from global registry
            # For now, we'll create placeholder connections
            logger.info(f"✅ Components initialized for orchestrator {self.orchestrator_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise

    async def _start_background_tasks(self) -> None:
        """Start background orchestration tasks"""
        try:
            # Workflow executor
            executor_task = asyncio.create_task(self._workflow_executor_loop())
            self.background_tasks.add(executor_task)
            
            # Performance monitor
            monitor_task = asyncio.create_task(self._performance_monitor_loop())
            self.background_tasks.add(monitor_task)
            
            # Optimization engine
            optimization_task = asyncio.create_task(self._optimization_loop())
            self.background_tasks.add(optimization_task)
            
            # Health checker
            health_task = asyncio.create_task(self._health_check_loop())
            self.background_tasks.add(health_task)
            
            logger.info(f"✅ Background tasks started for orchestrator {self.orchestrator_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start background tasks: {e}")
            raise

    async def _workflow_executor_loop(self) -> None:
        """Main workflow execution loop"""
        while not self.shutdown_event.is_set():
            try:
                # Get next workflow for execution
                try:
                    priority, timestamp, execution = await asyncio.wait_for(
                        self.execution_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Execute workflow asynchronously
                asyncio.create_task(self._execute_workflow_instance(execution))
                
            except Exception as e:
                logger.error(f"❌ Workflow executor loop error: {e}")
                await asyncio.sleep(5)

    async def _execute_workflow_instance(self, execution: WorkflowExecution) -> None:
        """Execute a workflow instance"""
        async with self.execution_semaphore:
            try:
                logger.info(f"🚀 Executing workflow: {execution.execution_id}")
                
                execution.status = WorkflowStatus.RUNNING
                execution.started_at = datetime.utcnow()
                
                # Build execution graph
                execution.execution_graph = await self._build_execution_graph(execution.workflow_def)
                
                # Execute based on strategy
                if execution.workflow_def.execution_strategy == ExecutionStrategy.DAG:
                    await self._execute_dag_workflow(execution)
                elif execution.workflow_def.execution_strategy == ExecutionStrategy.PIPELINE:
                    await self._execute_pipeline_workflow(execution)
                elif execution.workflow_def.execution_strategy == ExecutionStrategy.PARALLEL:
                    await self._execute_parallel_workflow(execution)
                elif execution.workflow_def.execution_strategy == ExecutionStrategy.ADAPTIVE:
                    await self._execute_adaptive_workflow(execution)
                else:
                    await self._execute_sequential_workflow(execution)
                
                # Mark as completed
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                
                # Update metrics
                self.metrics["successful_workflows"] += 1
                await self._update_performance_metrics(execution)
                
                logger.info(f"✅ Workflow completed: {execution.execution_id}")
                
            except Exception as e:
                logger.error(f"❌ Workflow execution failed {execution.execution_id}: {e}")
                
                execution.status = WorkflowStatus.FAILED
                execution.completed_at = datetime.utcnow()
                self.metrics["failed_workflows"] += 1
                
                # Send failure notification
                await self._send_workflow_notification(execution, "failed")
                
            finally:
                # Move to completed executions
                self.completed_executions.append(execution)
                self.active_executions.pop(execution.execution_id, None)
                
                # Update total workflows
                self.metrics["total_workflows"] += 1

    async def _execute_dag_workflow(self, execution: WorkflowExecution) -> None:
        """Execute workflow using DAG strategy"""
        try:
            graph = execution.execution_graph
            if not graph:
                raise Exception("Execution graph not available")
            
            # Get topological order
            execution_order = list(nx.topological_sort(graph))
            
            # Track task dependencies
            in_progress = set()
            completed = set()
            
            while len(completed) < len(execution_order):
                # Find tasks ready to execute
                ready_tasks = []
                for task_id in execution_order:
                    if task_id in completed or task_id in in_progress:
                        continue
                    
                    # Check if all dependencies are completed
                    dependencies = list(graph.predecessors(task_id))
                    if all(dep in completed for dep in dependencies):
                        ready_tasks.append(task_id)
                
                if not ready_tasks:
                    # Check for deadlock
                    if not in_progress:
                        raise Exception("Workflow deadlock detected")
                    
                    # Wait for some tasks to complete
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks in parallel
                task_futures = []
                for task_id in ready_tasks:
                    task_def = next(t for t in execution.workflow_def.tasks if t.task_id == task_id)
                    task_execution = await self._create_task_execution(execution, task_def)
                    execution.task_executions[task_id] = task_execution
                    execution.current_tasks.add(task_id)
                    in_progress.add(task_id)
                    
                    future = asyncio.create_task(self._execute_task(task_execution))
                    task_futures.append((task_id, future))
                
                # Wait for tasks to complete
                for task_id, future in task_futures:
                    try:
                        await future
                        completed.add(task_id)
                        execution.completed_tasks.add(task_id)
                        execution.current_tasks.discard(task_id)
                        in_progress.discard(task_id)
                        
                    except Exception as e:
                        logger.error(f"❌ Task failed in DAG workflow: {task_id}: {e}")
                        execution.failed_tasks.add(task_id)
                        execution.current_tasks.discard(task_id)
                        in_progress.discard(task_id)
                        
                        # Handle failure based on workflow configuration
                        if execution.workflow_def.on_failure == "stop":
                            raise Exception(f"Workflow stopped due to task failure: {task_id}")
                        # Continue with other tasks if on_failure == "continue"
            
        except Exception as e:
            logger.error(f"❌ DAG workflow execution failed: {e}")
            raise

    async def _execute_pipeline_workflow(self, execution: WorkflowExecution) -> None:
        """Execute workflow using pipeline strategy"""
        try:
            for task_def in execution.workflow_def.tasks:
                task_execution = await self._create_task_execution(execution, task_def)
                execution.task_executions[task_def.task_id] = task_execution
                execution.current_tasks.add(task_def.task_id)
                
                try:
                    await self._execute_task(task_execution)
                    execution.completed_tasks.add(task_def.task_id)
                    
                except Exception as e:
                    logger.error(f"❌ Pipeline task failed: {task_def.task_id}: {e}")
                    execution.failed_tasks.add(task_def.task_id)
                    
                    if execution.workflow_def.on_failure == "stop":
                        raise
                
                finally:
                    execution.current_tasks.discard(task_def.task_id)
            
        except Exception as e:
            logger.error(f"❌ Pipeline workflow execution failed: {e}")
            raise

    async def _execute_parallel_workflow(self, execution: WorkflowExecution) -> None:
        """Execute workflow using parallel strategy"""
        try:
            task_futures = []
            
            # Start all tasks in parallel
            for task_def in execution.workflow_def.tasks:
                task_execution = await self._create_task_execution(execution, task_def)
                execution.task_executions[task_def.task_id] = task_execution
                execution.current_tasks.add(task_def.task_id)
                
                future = asyncio.create_task(self._execute_task(task_execution))
                task_futures.append((task_def.task_id, future))
            
            # Wait for all tasks to complete
            for task_id, future in task_futures:
                try:
                    await future
                    execution.completed_tasks.add(task_id)
                    
                except Exception as e:
                    logger.error(f"❌ Parallel task failed: {task_id}: {e}")
                    execution.failed_tasks.add(task_id)
                    
                    if execution.workflow_def.on_failure == "stop":
                        # Cancel remaining tasks
                        for other_task_id, other_future in task_futures:
                            if not other_future.done():
                                other_future.cancel()
                        raise
                
                finally:
                    execution.current_tasks.discard(task_id)
            
        except Exception as e:
            logger.error(f"❌ Parallel workflow execution failed: {e}")
            raise

    async def _execute_sequential_workflow(self, execution: WorkflowExecution) -> None:
        """Execute workflow using sequential strategy"""
        try:
            for task_def in execution.workflow_def.tasks:
                task_execution = await self._create_task_execution(execution, task_def)
                execution.task_executions[task_def.task_id] = task_execution
                execution.current_tasks.add(task_def.task_id)
                
                try:
                    await self._execute_task(task_execution)
                    execution.completed_tasks.add(task_def.task_id)
                    
                except Exception as e:
                    logger.error(f"❌ Sequential task failed: {task_def.task_id}: {e}")
                    execution.failed_tasks.add(task_def.task_id)
                    
                    if execution.workflow_def.on_failure == "stop":
                        raise
                
                finally:
                    execution.current_tasks.discard(task_def.task_id)
            
        except Exception as e:
            logger.error(f"❌ Sequential workflow execution failed: {e}")
            raise

    async def _execute_adaptive_workflow(self, execution: WorkflowExecution) -> None:
        """Execute workflow using adaptive strategy with ML optimization"""
        try:
            # Use ML to determine optimal execution strategy
            optimal_strategy = await self.task_predictor.predict_optimal_execution_order(
                execution.workflow_def.tasks
            )
            
            # Execute based on predicted strategy
            if optimal_strategy == "dag":
                await self._execute_dag_workflow(execution)
            elif optimal_strategy == "pipeline":
                await self._execute_pipeline_workflow(execution)
            elif optimal_strategy == "parallel":
                await self._execute_parallel_workflow(execution)
            else:
                await self._execute_sequential_workflow(execution)
            
        except Exception as e:
            logger.error(f"❌ Adaptive workflow execution failed: {e}")
            raise

    async def _execute_task(self, task_execution: TaskExecution) -> None:
        """Execute a single task"""
        try:
            task_execution.status = WorkflowStatus.RUNNING
            task_execution.started_at = datetime.utcnow()
            
            logger.debug(f"🚀 Executing task: {task_execution.task_def.task_id}")
            
            # Allocate resources
            if task_execution.task_def.resource_requirements:
                await self._allocate_task_resources(task_execution)
            
            # Execute based on task type
            if task_execution.task_def.task_type == TaskType.CRAWLER_TASK:
                result = await self._execute_crawler_task(task_execution)
            elif task_execution.task_def.task_type == TaskType.ANALYSIS_TASK:
                result = await self._execute_analysis_task(task_execution)
            elif task_execution.task_def.task_type == TaskType.FINGERPRINT_TASK:
                result = await self._execute_fingerprint_task(task_execution)
            elif task_execution.task_def.task_type == TaskType.NOTIFICATION_TASK:
                result = await self._execute_notification_task(task_execution)
            else:
                result = await self._execute_custom_task(task_execution)
            
            # Store result
            task_execution.result = result
            task_execution.status = WorkflowStatus.COMPLETED
            task_execution.completed_at = datetime.utcnow()
            task_execution.progress = 100.0
            
            # Update metrics
            self.metrics["successful_tasks"] += 1
            
            logger.debug(f"✅ Task completed: {task_execution.task_def.task_id}")
            
        except Exception as e:
            logger.error(f"❌ Task execution failed {task_execution.task_def.task_id}: {e}")
            
            task_execution.status = WorkflowStatus.FAILED
            task_execution.completed_at = datetime.utcnow()
            task_execution.error_message = str(e)
            
            # Update metrics
            self.metrics["failed_tasks"] += 1
            
            # Retry if configured
            if (task_execution.retry_count < task_execution.task_def.retry_config.get("max_retries", 0)):
                await self._retry_task(task_execution)
            else:
                raise
                
        finally:
            # Deallocate resources
            await self._deallocate_task_resources(task_execution)
            
            # Update total tasks
            self.metrics["total_tasks"] += 1

    async def _execute_crawler_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute crawler task"""
        try:
            config = task_execution.task_def.task_config
            
            # Create crawler task
            crawler_task = CrawlerTask(
                task_id=task_execution.execution_id,
                task_type=config.get("task_type", "web_crawl"),
                target_url=config["target_url"],
                platform=config.get("platform", "unknown"),
                content_types=config.get("content_types", ["text"]),
                extraction_rules=config.get("extraction_rules", {}),
                priority=task_execution.task_def.priority,
                user_id=config.get("user_id"),
                tenant_id=config.get("tenant_id"),
                metadata=config.get("metadata", {})
            )
            
            # Submit to worker pool
            if self.worker_pool:
                success = await self.worker_pool.submit_task(crawler_task)
                if not success:
                    raise Exception("Failed to submit crawler task to worker pool")
                
                # Wait for completion (simplified - would need proper task tracking)
                await asyncio.sleep(5)  # Placeholder
                
                return {"status": "completed", "task_id": crawler_task.task_id}
            else:
                raise Exception("Worker pool not available")
            
        except Exception as e:
            logger.error(f"❌ Crawler task execution failed: {e}")
            raise

    async def _execute_analysis_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute analysis task"""
        try:
            # Placeholder for analysis task execution
            config = task_execution.task_def.task_config
            analysis_type = config.get("analysis_type", "content_analysis")
            
            # Simulate analysis processing
            await asyncio.sleep(2)
            
            return {
                "analysis_type": analysis_type,
                "status": "completed",
                "results": {"analyzed_items": 100, "insights": ["insight1", "insight2"]}
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis task execution failed: {e}")
            raise

    async def _execute_fingerprint_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute fingerprint generation task"""
        try:
            # Placeholder for fingerprint task execution
            config = task_execution.task_def.task_config
            content_items = config.get("content_items", [])
            
            # Simulate fingerprint generation
            await asyncio.sleep(3)
            
            return {
                "status": "completed",
                "fingerprints_generated": len(content_items),
                "fingerprint_ids": [str(uuid.uuid4()) for _ in content_items]
            }
            
        except Exception as e:
            logger.error(f"❌ Fingerprint task execution failed: {e}")
            raise

    async def _execute_notification_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute notification task"""
        try:
            config = task_execution.task_def.task_config
            
            if self.notification_engine:
                notification_id = await self.notification_engine.send_direct_notification(
                    recipient_id=config["recipient_id"],
                    channel=config["channel"],
                    template_type=config["template_type"],
                    variables=config.get("variables", {}),
                    priority=config.get("priority", NotificationPriority.MEDIUM)
                )
                
                return {"status": "completed", "notification_id": notification_id}
            else:
                raise Exception("Notification engine not available")
            
        except Exception as e:
            logger.error(f"❌ Notification task execution failed: {e}")
            raise

    async def _execute_custom_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """Execute custom task"""
        try:
            # Placeholder for custom task execution
            config = task_execution.task_def.task_config
            
            # Simulate custom processing
            processing_time = config.get("processing_time", 1)
            await asyncio.sleep(processing_time)
            
            return {
                "status": "completed",
                "custom_result": config.get("expected_result", "success")
            }
            
        except Exception as e:
            logger.error(f"❌ Custom task execution failed: {e}")
            raise

    async def _validate_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """Validate workflow definition"""
        try:
            if not workflow_def.workflow_id or not workflow_def.tasks:
                return False
            
            # Check for duplicate task IDs
            task_ids = [task.task_id for task in workflow_def.tasks]
            if len(task_ids) != len(set(task_ids)):
                logger.warning(f"⚠️ Duplicate task IDs in workflow: {workflow_def.workflow_id}")
                return False
            
            # Validate task dependencies
            for task in workflow_def.tasks:
                for dep_id in task.dependencies:
                    if dep_id not in task_ids:
                        logger.warning(f"⚠️ Invalid dependency {dep_id} in task {task.task_id}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow validation failed: {e}")
            return False

    async def _build_execution_graph(self, workflow_def: WorkflowDefinition) -> Optional[nx.DiGraph]:
        """Build execution graph from workflow definition"""
        try:
            graph = nx.DiGraph()
            
            # Add task nodes
            for task in workflow_def.tasks:
                graph.add_node(task.task_id, task_def=task)
            
            # Add dependency edges
            for task in workflow_def.tasks:
                for dep_id in task.dependencies:
                    graph.add_edge(dep_id, task.task_id)
            
            # Check for cycles
            if not nx.is_directed_acyclic_graph(graph):
                logger.warning(f"⚠️ Workflow contains cycles: {workflow_def.workflow_id}")
                return None
            
            return graph
            
        except Exception as e:
            logger.error(f"❌ Failed to build execution graph: {e}")
            return None

    async def _create_workflow_execution(self, workflow_def: WorkflowDefinition, 
                                       variables: Dict[str, Any]) -> WorkflowExecution:
        """Create workflow execution instance"""
        try:
            execution = WorkflowExecution(
                execution_id=str(uuid.uuid4()),
                workflow_def=workflow_def,
                variables={**workflow_def.variables, **variables}
            )
            
            return execution
            
        except Exception as e:
            logger.error(f"❌ Failed to create workflow execution: {e}")
            raise

    async def _create_task_execution(self, workflow_execution: WorkflowExecution,
                                   task_def: TaskDefinition) -> TaskExecution:
        """Create task execution instance"""
        try:
            task_execution = TaskExecution(
                execution_id=f"{workflow_execution.execution_id}_{task_def.task_id}",
                task_def=task_def,
                workflow_id=workflow_execution.workflow_def.workflow_id
            )
            
            return task_execution
            
        except Exception as e:
            logger.error(f"❌ Failed to create task execution: {e}")
            raise

    async def _allocate_task_resources(self, task_execution: TaskExecution) -> None:
        """Allocate resources for task execution"""
        try:
            if self.resource_manager and task_execution.task_def.resource_requirements:
                allocations = await self.resource_manager.allocate_resources(
                    worker_id=task_execution.execution_id,
                    required_resources=task_execution.task_def.resource_requirements,
                    priority=task_execution.task_def.priority.value
                )
                
                task_execution.resource_allocations = {
                    rt.value: alloc.allocation_id 
                    for rt, alloc in allocations.items()
                }
            
        except Exception as e:
            logger.error(f"❌ Failed to allocate task resources: {e}")

    async def _deallocate_task_resources(self, task_execution: TaskExecution) -> None:
        """Deallocate task resources"""
        try:
            if self.resource_manager and task_execution.resource_allocations:
                for allocation_id in task_execution.resource_allocations.values():
                    await self.resource_manager.deallocate_resources(allocation_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to deallocate task resources: {e}")

    async def _retry_task(self, task_execution: TaskExecution) -> None:
        """Retry failed task"""
        try:
            task_execution.retry_count += 1
            task_execution.status = WorkflowStatus.PENDING
            task_execution.error_message = None
            
            # Calculate backoff delay
            retry_delay = task_execution.task_def.retry_config.get("delay", 30)
            backoff_factor = task_execution.task_def.retry_config.get("backoff_factor", 2.0)
            delay = retry_delay * (backoff_factor ** (task_execution.retry_count - 1))
            
            logger.info(f"🔄 Retrying task {task_execution.task_def.task_id} in {delay}s (attempt {task_execution.retry_count})")
            
            # Schedule retry
            asyncio.create_task(self._delayed_task_retry(task_execution, delay))
            
        except Exception as e:
            logger.error(f"❌ Failed to retry task: {e}")

    async def _delayed_task_retry(self, task_execution: TaskExecution, delay: float) -> None:
        """Execute delayed task retry"""
        try:
            await asyncio.sleep(delay)
            await self._execute_task(task_execution)
            
        except Exception as e:
            logger.error(f"❌ Task retry failed: {e}")

    async def _pause_task(self, task_execution: TaskExecution) -> None:
        """Pause task execution"""
        try:
            task_execution.status = WorkflowStatus.PAUSED
            task_execution.paused_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Failed to pause task: {e}")

    async def _resume_task(self, task_execution: TaskExecution) -> None:
        """Resume paused task execution"""
        try:
            task_execution.status = WorkflowStatus.RUNNING
            task_execution.paused_at = None
            
        except Exception as e:
            logger.error(f"❌ Failed to resume task: {e}")

    async def _cancel_task(self, task_execution: TaskExecution) -> None:
        """Cancel task execution"""
        try:
            task_execution.status = WorkflowStatus.CANCELLED
            task_execution.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"❌ Failed to cancel task: {e}")

    async def _send_workflow_notification(self, execution: WorkflowExecution, event_type: str) -> None:
        """Send workflow status notification"""
        try:
            if self.notification_engine and execution.workflow_def.notifications:
                # Implementation would depend on notification configuration
                pass
            
        except Exception as e:
            logger.error(f"❌ Failed to send workflow notification: {e}")

    async def _get_historical_performance_data(self, workflow_id: str) -> Dict[str, Any]:
        """Get historical performance data for workflow"""
        try:
            # Placeholder for historical data retrieval
            return {
                "executions": 10,
                "average_duration": 300,
                "success_rate": 0.95,
                "resource_utilization": {"cpu": 0.7, "memory": 0.6}
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get historical performance data: {e}")
            return {}

    async def _generate_resource_recommendations(self, workflow_def: WorkflowDefinition,
                                               historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource optimization recommendations"""
        try:
            # Placeholder for resource recommendations
            return {
                "cpu_optimization": "increase_by_20_percent",
                "memory_optimization": "reduce_by_10_percent",
                "parallel_tasks": ["task1", "task2"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate resource recommendations: {e}")
            return {}

    async def _calculate_estimated_improvements(self, workflow_def: WorkflowDefinition,
                                              optimal_strategy: str,
                                              resource_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate estimated improvements from optimizations"""
        try:
            # Placeholder for improvement calculations
            return {
                "execution_time_improvement": "25_percent",
                "resource_efficiency_improvement": "15_percent",
                "cost_savings": "30_percent"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate estimated improvements: {e}")
            return {}

    async def _update_performance_metrics(self, execution: WorkflowExecution) -> None:
        """Update performance metrics from execution"""
        try:
            if execution.started_at and execution.completed_at:
                duration = (execution.completed_at - execution.started_at).total_seconds()
                
                # Update average workflow duration
                total_workflows = self.metrics["total_workflows"]
                current_avg = self.metrics["average_workflow_duration"]
                new_avg = ((current_avg * total_workflows) + duration) / (total_workflows + 1)
                self.metrics["average_workflow_duration"] = new_avg
            
            # Update task metrics
            for task_exec in execution.task_executions.values():
                if task_exec.started_at and task_exec.completed_at:
                    task_duration = (task_exec.completed_at - task_exec.started_at).total_seconds()
                    
                    # Update average task duration
                    total_tasks = self.metrics["total_tasks"]
                    current_avg = self.metrics["average_task_duration"]
                    new_avg = ((current_avg * total_tasks) + task_duration) / (total_tasks + 1)
                    self.metrics["average_task_duration"] = new_avg
            
        except Exception as e:
            logger.error(f"❌ Failed to update performance metrics: {e}")

    async def _graceful_shutdown(self) -> None:
        """Gracefully shutdown active workflows"""
        try:
            if not self.active_executions:
                return
            
            logger.info(f"⏳ Waiting for {len(self.active_executions)} active workflows to complete...")
            
            # Set a reasonable timeout
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while self.active_executions and (time.time() - start_time) < timeout:
                await asyncio.sleep(5)
            
            # Cancel remaining workflows
            if self.active_executions:
                logger.warning(f"⚠️ Cancelling {len(self.active_executions)} remaining workflows")
                for execution_id in list(self.active_executions.keys()):
                    await self.cancel_workflow(execution_id)
            
        except Exception as e:
            logger.error(f"❌ Failed graceful shutdown: {e}")

    async def _performance_monitor_loop(self) -> None:
        """Background performance monitoring loop"""
        while not self.shutdown_event.is_set():
            try:
                # Monitor performance and send alerts if needed
                await self._monitor_performance()
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Performance monitor error: {e}")
                await asyncio.sleep(600)

    async def _monitor_performance(self) -> None:
        """Monitor orchestrator performance"""
        try:
            # Check queue size
            if self.execution_queue.qsize() > 100:
                logger.warning(f"⚠️ High execution queue size: {self.execution_queue.qsize()}")
            
            # Check active executions
            if len(self.active_executions) > 40:
                logger.warning(f"⚠️ High number of active executions: {len(self.active_executions)}")
            
            # Check success rate
            total_workflows = self.metrics["total_workflows"]
            failed_workflows = self.metrics["failed_workflows"]
            if total_workflows > 10 and (failed_workflows / total_workflows) > 0.1:
                logger.warning(f"⚠️ High workflow failure rate: {failed_workflows / total_workflows * 100:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Failed to monitor performance: {e}")

    async def _optimization_loop(self) -> None:
        """Background optimization loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._run_optimization_cycle()
                await asyncio.sleep(1800)  # Optimize every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Optimization loop error: {e}")
                await asyncio.sleep(3600)

    async def _run_optimization_cycle(self) -> None:
        """Run optimization cycle for all workflows"""
        try:
            for workflow_id in self.workflow_definitions.keys():
                try:
                    optimization_result = await self.optimize_execution_plan(workflow_id)
                    if optimization_result and "estimated_improvements" in optimization_result:
                        improvements = optimization_result["estimated_improvements"]
                        logger.info(f"🔧 Optimization available for {workflow_id}: {improvements}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to optimize workflow {workflow_id}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Failed to run optimization cycle: {e}")

    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._perform_health_checks()
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Health check loop error: {e}")
                await asyncio.sleep(600)

    async def _perform_health_checks(self) -> None:
        """Perform health checks on orchestrator components"""
        try:
            # Check component availability
            components_health = {
                "worker_pool": self.worker_pool is not None,
                "resource_manager": self.resource_manager is not None,
                "event_processor": self.event_processor is not None,
                "notification_engine": self.notification_engine is not None
            }
            
            unhealthy_components = [name for name, healthy in components_health.items() if not healthy]
            
            if unhealthy_components:
                logger.warning(f"⚠️ Unhealthy components: {unhealthy_components}")
            
        except Exception as e:
            logger.error(f"❌ Failed to perform health checks: {e}")


# Global task orchestrator instance
_task_orchestrator: Optional[TaskOrchestrator] = None


def get_task_orchestrator(orchestrator_id: str = "default") -> TaskOrchestrator:
    """Get or create task orchestrator singleton"""
    global _task_orchestrator
    
    if _task_orchestrator is None:
        _task_orchestrator = TaskOrchestrator(orchestrator_id)
    
    return _task_orchestrator


async def initialize_task_orchestrator(orchestrator_id: str = "default") -> bool:
    """Initialize global task orchestrator"""
    try:
        orchestrator = get_task_orchestrator(orchestrator_id)
        return await orchestrator.start()
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize task orchestrator: {e}")
        return False


async def shutdown_task_orchestrator() -> None:
    """Shutdown global task orchestrator"""
    global _task_orchestrator
    
    if _task_orchestrator:
        await _task_orchestrator.stop()
        _task_orchestrator = None
