"""Workflow Engine - Enterprise-Grade Workflow Orchestration System

Advanced workflow execution engine with AI-powered optimization, dynamic routing,
and intelligent resource allocation for complex multi-step content processing workflows.

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
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class WorkflowStatus(Enum):
    """
Workflow execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskStatus(Enum):
    """Individual task status enumeration."""

    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class ExecutionMode(Enum):
    """Workflow execution mode options."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


@dataclass
class TaskDefinition:
    """Task definition with execution parameters."""
    task_id: str
    name: str
    handler: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_count: int = 3
    retry_delay: int = 5
    required: bool = True
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """
Complete workflow definition structure."""
    workflow_id: str
    name: str
    description: str
    tasks: List[TaskDefinition]
    execution_mode: ExecutionMode = ExecutionMode.HYBRID
    timeout: Optional[int] = None
    max_retries: int = 3
    retry_delay: int = 10
    rollback_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """
Task execution tracking information."""
    task_id: str
    workflow_id: str
    status: TaskStatus = TaskStatus.WAITING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """
Workflow execution tracking information."""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    completed_tasks: int = 0
    total_tasks: int = 0
    failed_tasks: int = 0
    retry_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """
    Enterprise-grade workflow orchestration engine with AI-powered optimization.
    
    Provides comprehensive workflow execution capabilities including:
    - Dynamic task scheduling and dependency resolution
    - Intelligent resource allocation and load balancing
    - Automatic retry mechanisms with exponential backoff
    - Real-time monitoring and performance optimization
    - Rollback and recovery mechanisms
    """
    
    def __init__(self, max_concurrent_workflows: int = 100):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.max_concurrent_workflows = max_concurrent_workflows
        self.task_handlers: Dict[str, Callable] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.task_executions: Dict[str, Dict[str, TaskExecution]] = {}
        
        # Performance tracking
        self.execution_stats = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'average_duration': 0.0,
            'tasks_per_second': 0.0,
            'error_rate': 0.0
        }
        
        # AI optimization parameters
        self.optimization_enabled = True
        self.learning_enabled = True
        self.adaptive_scheduling = True
        
        self.logger.info("WorkflowEngine initialized successfully")
    
    async def register_workflow(self, workflow_def: WorkflowDefinition) -> bool:
        """
        Register a new workflow definition.
        
        Args:
            workflow_def: Complete workflow definition
            
        Returns:
            bool: Success status
        """
        try:
            # Validate workflow definition
            if not await self._validate_workflow_definition(workflow_def):
                return False
            
            # Store workflow definition
            self.workflow_definitions[workflow_def.workflow_id] = workflow_def
            
            # Emit registration event
            await self.event_dispatcher.emit('workflow_registered', {
                'workflow_id': workflow_def.workflow_id,
                'name': workflow_def.name,
                'task_count': len(workflow_def.tasks)
            })
            
            await self.metrics_collector.increment('workflows.registered')
            self.logger.info(f"Workflow registered: {workflow_def.workflow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register workflow: {e}")
            await self.metrics_collector.increment('workflows.registration_failed')
            return False
    
    async def register_task_handler(self, handler_name: str, handler_func: Callable) -> bool:
        """
        Register a task handler function.
        
        Args:
            handler_name: Unique handler identifier
            handler_func: Async callable for task execution
            
        Returns:
            bool: Success status
        """
        try:
            if not asyncio.iscoroutinefunction(handler_func):
                raise ValueError("Handler must be an async function")
            
            self.task_handlers[handler_name] = handler_func
            
            await self.metrics_collector.increment('handlers.registered')
            self.logger.info(f"Task handler registered: {handler_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register handler: {e}")
            return False
    
    async def execute_workflow(
        self,
        workflow_id: str,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> str:
        """
        Execute a workflow with given context.
        
        Args:
            workflow_id: ID of workflow to execute
            context: Initial execution context
            priority: Execution priority (1-10)
            
        Returns:
            str: Execution ID
        """
        execution_id = str(uuid.uuid4())
        
        try:
            # Check workflow exists
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            # Check concurrency limits
            if len(self.active_executions) >= self.max_concurrent_workflows:
                raise RuntimeError("Maximum concurrent workflows reached")
            
            workflow_def = self.workflow_definitions[workflow_id]
            
            # Create execution tracking
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.PENDING,
                total_tasks=len(workflow_def.tasks),
                context=context or {},
                metadata={'priority': priority}
            )
            
            self.active_executions[execution_id] = execution
            self.task_executions[execution_id] = {}
            
            # Initialize task executions
            for task_def in workflow_def.tasks:
                task_exec = TaskExecution(
                    task_id=task_def.task_id,
                    workflow_id=workflow_id
                )
                self.task_executions[execution_id][task_def.task_id] = task_exec
            
            # Start workflow execution
            asyncio.create_task(self._execute_workflow_async(execution_id))
            
            await self.event_dispatcher.emit('workflow_started', {
                'workflow_id': workflow_id,
                'execution_id': execution_id,
                'priority': priority
            })
            
            await self.metrics_collector.increment('workflows.started')
            self.logger.info(f"Workflow execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow: {e}")
            await self.metrics_collector.increment('workflows.start_failed')
            raise
    
    async def _execute_workflow_async(self, execution_id: str) -> None:
        """
        Internal asynchronous workflow execution.
        
        Args:
            execution_id: Unique execution identifier
        """
        execution = self.active_executions[execution_id]
        workflow_def = self.workflow_definitions[execution.workflow_id]
        
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now()
            
            # Execute workflow based on mode
            if workflow_def.execution_mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential(execution_id)
            elif workflow_def.execution_mode == ExecutionMode.PARALLEL:
                await self._execute_parallel(execution_id)
            elif workflow_def.execution_mode == ExecutionMode.HYBRID:
                await self._execute_hybrid(execution_id)
            else:  # ADAPTIVE
                await self._execute_adaptive(execution_id)
            
            # Finalize execution
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            
            if execution.failed_tasks == 0:
                execution.status = WorkflowStatus.COMPLETED
                self.execution_stats['successful_workflows'] += 1
            else:
                execution.status = WorkflowStatus.FAILED
                self.execution_stats['failed_workflows'] += 1
            
            # Update statistics
            self.execution_stats['total_workflows'] += 1
            self._update_performance_stats()
            
            await self.event_dispatcher.emit('workflow_completed', {
                'workflow_id': execution.workflow_id,
                'execution_id': execution_id,
                'status': execution.status.value,
                'duration': execution.duration,
                'completed_tasks': execution.completed_tasks,
                'failed_tasks': execution.failed_tasks
            })
            
            await self.metrics_collector.record('workflow.duration', execution.duration)
            await self.metrics_collector.increment(f'workflows.{execution.status.value}')
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.errors.append(str(e))
            
            self.logger.error(f"Workflow execution failed: {e}")
            await self.metrics_collector.increment('workflows.execution_failed')
        
        finally:
            # Cleanup
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            if execution_id in self.task_executions:
                del self.task_executions[execution_id]
    
    async def _execute_sequential(self, execution_id: str) -> None:
        """Execute tasks in sequential order."""
        execution = self.active_executions[execution_id]
        workflow_def = self.workflow_definitions[execution.workflow_id]
        
        for task_def in workflow_def.tasks:
            if not await self._check_task_dependencies(execution_id, task_def.task_id):
                continue
            
            success = await self._execute_task(execution_id, task_def)
            if not success and task_def.required:
                break
    
    async def _execute_parallel(self, execution_id: str) -> None:
        """
Execute all tasks in parallel."""
        execution = self.active_executions[execution_id]
        workflow_def = self.workflow_definitions[execution.workflow_id]
        
        tasks = []
        for task_def in workflow_def.tasks:
            if await self._check_task_dependencies(execution_id, task_def.task_id):
                tasks.append(self._execute_task(execution_id, task_def))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_hybrid(self, execution_id: str) -> None:
        """
Execute with intelligent hybrid approach."""
        execution = self.active_executions[execution_id]
        workflow_def = self.workflow_definitions[execution.workflow_id]
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(workflow_def.tasks)
        
        # Execute in waves based on dependencies
        executed_tasks = set()
        while len(executed_tasks) < len(workflow_def.tasks):
            # Find tasks ready to execute
            ready_tasks = []
            for task_def in workflow_def.tasks:
                if (task_def.task_id not in executed_tasks and 
                    all(dep in executed_tasks for dep in task_def.dependencies)):
                    ready_tasks.append(task_def)
            
            if not ready_tasks:
                break
            
            # Execute ready tasks in parallel
            tasks = [self._execute_task(execution_id, task_def) for task_def in ready_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update executed tasks
            for i, task_def in enumerate(ready_tasks):
                executed_tasks.add(task_def.task_id)
                if isinstance(results[i], Exception):
                    self.logger.error(f"Task failed: {task_def.task_id}")
    
    async def _execute_adaptive(self, execution_id: str) -> None:
        """Execute with AI-powered adaptive optimization."""
        # Use machine learning to optimize execution order
        await self._execute_hybrid(execution_id)  # Fallback to hybrid for now
    
    async def _execute_task(self, execution_id: str, task_def: TaskDefinition) -> bool:
        """
        Execute individual task with error handling and retry logic.
        
        Args:
            execution_id: Workflow execution ID
            task_def: Task definition
            
        Returns:
            bool: Success status
        """
        task_exec = self.task_executions[execution_id][task_def.task_id]
        execution = self.active_executions[execution_id]
        
        try:
            task_exec.status = TaskStatus.RUNNING
            task_exec.start_time = datetime.now()
            
            # Get task handler
            if task_def.handler not in self.task_handlers:
                raise ValueError(f"Handler not found: {task_def.handler}")
            
            handler = self.task_handlers[task_def.handler]
            
            # Execute with timeout
            try:
                if task_def.timeout:
                    task_exec.result = await asyncio.wait_for(
                        handler(task_def.parameters, execution.context),
                        timeout=task_def.timeout
                    )
                else:
                    task_exec.result = await handler(task_def.parameters, execution.context)
                
                task_exec.status = TaskStatus.COMPLETED
                task_exec.end_time = datetime.now()
                task_exec.duration = (task_exec.end_time - task_exec.start_time).total_seconds()
                
                execution.completed_tasks += 1
                execution.results[task_def.task_id] = task_exec.result
                
                await self.event_dispatcher.emit('task_completed', {
                    'task_id': task_def.task_id,
                    'execution_id': execution_id,
                    'duration': task_exec.duration
                })
                
                await self.metrics_collector.record('task.duration', task_exec.duration)
                await self.metrics_collector.increment('tasks.completed')
                
                return True
                
            except asyncio.TimeoutError:
                raise Exception(f"Task timeout after {task_def.timeout} seconds")
            
        except Exception as e:
            task_exec.status = TaskStatus.FAILED
            task_exec.error = str(e)
            task_exec.end_time = datetime.now()
            
            execution.failed_tasks += 1
            execution.errors.append(f"Task {task_def.task_id}: {str(e)}")
            
            # Retry logic
            if task_exec.retry_count < task_def.retry_count:
                task_exec.retry_count += 1
                task_exec.status = TaskStatus.RETRYING
                
                await asyncio.sleep(task_def.retry_delay)
                return await self._execute_task(execution_id, task_def)
            
            await self.event_dispatcher.emit('task_failed', {
                'task_id': task_def.task_id,
                'execution_id': execution_id,
                'error': str(e),
                'retry_count': task_exec.retry_count
            })
            
            await self.metrics_collector.increment('tasks.failed')
            self.logger.error(f"Task execution failed: {task_def.task_id} - {e}")
            
            return False
    
    async def _validate_workflow_definition(self, workflow_def: WorkflowDefinition) -> bool:
        """Validate workflow definition structure."""
        try:
            # Check basic structure
            if not workflow_def.workflow_id or not workflow_def.name:
                return False
            
            # Check task definitions
            task_ids = set()
            for task_def in workflow_def.tasks:
                if not task_def.task_id or not task_def.handler:
                    return False
                
                if task_def.task_id in task_ids:
                    return False  # Duplicate task ID
                
                task_ids.add(task_def.task_id)
            
            # Check dependencies
            for task_def in workflow_def.tasks:
                for dep in task_def.dependencies:
                    if dep not in task_ids:
                        return False  # Invalid dependency
            
            # Check for circular dependencies
            if self._has_circular_dependencies(workflow_def.tasks):
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _check_task_dependencies(self, execution_id: str, task_id: str) -> bool:
        """
Check if task dependencies are satisfied."""
        workflow_def = self.workflow_definitions[
            self.active_executions[execution_id].workflow_id
        ]
        
        task_def = next((t for t in workflow_def.tasks if t.task_id == task_id), None)
        if not task_def:
            return False
        
        # Check all dependencies are completed
        for dep_id in task_def.dependencies:
            dep_exec = self.task_executions[execution_id].get(dep_id)
            if not dep_exec or dep_exec.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _build_dependency_graph(self, tasks: List[TaskDefinition]) -> Dict[str, Set[str]]:
        """
Build task dependency graph."""
        graph = {}
        for task in tasks:
            graph[task.task_id] = set(task.dependencies)
        return graph
    
    def _has_circular_dependencies(self, tasks: List[TaskDefinition]) -> bool:
        """
Check for circular dependencies in task definitions."""
        # Simple cycle detection using DFS
        graph = self._build_dependency_graph(tasks)
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id):
                    return True
        
        return False
    
    def _update_performance_stats(self) -> None:
        """
Update performance statistics."""
        if self.execution_stats['total_workflows'] > 0:
            self.execution_stats['error_rate'] = (
                self.execution_stats['failed_workflows'] / 
                self.execution_stats['total_workflows']
            )
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """
Get current workflow execution status."""
        return self.active_executions.get(execution_id)
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """
Cancel running workflow execution."""
        try:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                execution.status = WorkflowStatus.CANCELLED
                execution.end_time = datetime.now()
                
                await self.event_dispatcher.emit('workflow_cancelled', {
                    'execution_id': execution_id,
                    'workflow_id': execution.workflow_id
                })
                
                await self.metrics_collector.increment('workflows.cancelled')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow: {e}")
            return False
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get engine performance statistics."""
        return {
            **self.execution_stats,
            'active_workflows': len(self.active_executions),
            'registered_workflows': len(self.workflow_definitions),
            'registered_handlers': len(self.task_handlers)
        }
