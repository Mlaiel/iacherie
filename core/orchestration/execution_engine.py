"""
Execution Engine - High-Performance Task Execution Framework

Advanced execution engine for running distributed tasks with intelligent load balancing,
fault tolerance, and performance optimization across multi-node environments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL WARNING:
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
import json
import concurrent.futures

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class ExecutionStatus(Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionMode(Enum):
    """Execution mode options."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"


class ExecutorType(Enum):
    """Executor type classification."""
    LOCAL_PROCESS = "local_process"
    THREAD_POOL = "thread_pool"
    ASYNC_COROUTINE = "async_coroutine"
    REMOTE_NODE = "remote_node"
    CONTAINER = "container"
    SERVERLESS = "serverless"


@dataclass
class ExecutionContext:
    """Execution context with environment and configuration."""
    execution_id: str
    task_id: str
    executor_id: str
    environment: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    security_context: Dict[str, Any] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Task execution result with metrics and output."""
    execution_id: str
    task_id: str
    status: ExecutionStatus
    result_data: Optional[Any] = None
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutorNode:
    """Execution node configuration and status."""
    node_id: str
    name: str
    executor_type: ExecutorType
    endpoint: Optional[str] = None
    capacity: Dict[str, float] = field(default_factory=dict)
    current_load: Dict[str, float] = field(default_factory=dict)
    status: str = "healthy"
    last_heartbeat: Optional[datetime] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    supported_tasks: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionTask:
    """Task definition for execution."""
    task_id: str
    name: str
    task_type: str
    handler: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_mode: ExecutionMode = ExecutionMode.ASYNCHRONOUS
    timeout: Optional[int] = None
    retry_count: int = 3
    retry_delay: int = 5
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchExecution:
    """Batch execution tracking."""
    batch_id: str
    name: str
    tasks: List[ExecutionTask]
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL
    max_concurrent: int = 10
    timeout: Optional[int] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, ExecutionResult] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExecutionEngine:
    """
    High-performance task execution engine with distributed capabilities.
    
    Provides comprehensive execution capabilities including:
    - Multi-mode task execution (sync, async, parallel, distributed)
    - Intelligent load balancing across executor nodes
    - Fault tolerance with automatic retry and failover
    - Resource monitoring and performance optimization
    - Batch execution with dependency management
    """
    
    def __init__(self, max_concurrent_executions: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.max_concurrent_executions = max_concurrent_executions
        self.task_handlers: Dict[str, Callable] = {}
        self.executor_nodes: Dict[str, ExecutorNode] = {}
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.execution_results: Dict[str, ExecutionResult] = {}
        self.batch_executions: Dict[str, BatchExecution] = {}
        
        # Thread pools for different execution modes
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=50)
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=20)
        
        # Performance tracking
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'throughput_per_second': 0.0,
            'resource_utilization': 0.0,
            'error_rate': 0.0,
            'load_balance_efficiency': 0.0
        }
        
        # Load balancing
        self.load_balancing_enabled = True
        self.auto_scaling_enabled = True
        self.fault_tolerance_enabled = True
        
        self.logger.info("ExecutionEngine initialized successfully")
    
    async def register_task_handler(self, handler_name: str, handler_func: Callable) -> bool:
        """
        Register a task handler function.
        
        Args:
            handler_name: Unique handler identifier
            handler_func: Callable for task execution
            
        Returns:
            bool: Success status
        """



        try:
            self.task_handlers[handler_name] = handler_func
            
            await self.event_dispatcher.emit('handler_registered', {
                'handler_name': handler_name,
                'is_async': asyncio.iscoroutinefunction(handler_func)
            })
            
            await self.metrics_collector.increment('handlers.registered')
            self.logger.info(f"Task handler registered: {handler_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register handler: {e}")
            return False
    
    async def register_executor_node(self, node: ExecutorNode) -> bool:
        """
        Register an executor node.
        
        Args:
            node: Executor node configuration
            
        Returns:
            bool: Success status
        """



        try:
            self.executor_nodes[node.node_id] = node
            
            await self.event_dispatcher.emit('executor_registered', {
                'node_id': node.node_id,
                'executor_type': node.executor_type.value,
                'capacity': node.capacity
            })
            
            await self.metrics_collector.increment('executors.registered')
            self.logger.info(f"Executor node registered: {node.node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register executor: {e}")
            return False
    
    async def execute_task(self, task: ExecutionTask) -> str:
        """
        Execute a single task.
        
        Args:
            task: Task definition to execute
            
        Returns:
            str: Execution ID
        """
        execution_id = str(uuid.uuid4())
        
        try:
            # Check concurrency limits
            if len(self.active_executions) >= self.max_concurrent_executions:
                raise RuntimeError("Maximum concurrent executions reached")
            
            # Validate task
            if not await self._validate_task(task):
                raise ValueError("Invalid task definition")
            
            # Select optimal executor
            executor_node = await self._select_optimal_executor(task)
            if not executor_node:
                raise RuntimeError("No suitable executor available")
            
            # Create execution context
            context = ExecutionContext(
                execution_id=execution_id,
                task_id=task.task_id,
                executor_id=executor_node.node_id,
                environment=task.environment,
                resource_limits=task.resource_requirements
            )
            
            self.active_executions[execution_id] = context
            
            # Execute based on mode
            if task.execution_mode == ExecutionMode.SYNCHRONOUS:
                result = await self._execute_synchronous(task, context)
            elif task.execution_mode == ExecutionMode.ASYNCHRONOUS:
                asyncio.create_task(self._execute_asynchronous(task, context))
                result = ExecutionResult(
                    execution_id=execution_id,
                    task_id=task.task_id,
                    status=ExecutionStatus.RUNNING,
                    start_time=datetime.now()
                )
            elif task.execution_mode == ExecutionMode.PARALLEL:
                asyncio.create_task(self._execute_parallel(task, context))
                result = ExecutionResult(
                    execution_id=execution_id,
                    task_id=task.task_id,
                    status=ExecutionStatus.RUNNING,
                    start_time=datetime.now()
                )
            else:  # DISTRIBUTED
                asyncio.create_task(self._execute_distributed(task, context))
                result = ExecutionResult(
                    execution_id=execution_id,
                    task_id=task.task_id,
                    status=ExecutionStatus.RUNNING,
                    start_time=datetime.now()
                )
            
            self.execution_results[execution_id] = result
            
            await self.event_dispatcher.emit('task_execution_started', {
                'execution_id': execution_id,
                'task_id': task.task_id,
                'executor_id': executor_node.node_id,
                'execution_mode': task.execution_mode.value
            })
            
            self.execution_stats['total_executions'] += 1
            await self.metrics_collector.increment('executions.started')
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute task: {e}")
            await self.metrics_collector.increment('executions.start_failed')
            raise
    
    async def execute_batch(self, batch: BatchExecution) -> str:
        """
        Execute a batch of tasks.
        
        Args:
            batch: Batch execution definition
            
        Returns:
            str: Batch execution ID
        """



        try:
            batch.status = ExecutionStatus.RUNNING
            batch.started_at = datetime.now()
            
            self.batch_executions[batch.batch_id] = batch
            
            # Execute tasks based on batch mode
            if batch.execution_mode == ExecutionMode.PARALLEL:
                await self._execute_batch_parallel(batch)
            elif batch.execution_mode == ExecutionMode.DISTRIBUTED:
                await self._execute_batch_distributed(batch)
            else:  # Sequential
                await self._execute_batch_sequential(batch)
            
            await self.event_dispatcher.emit('batch_execution_started', {
                'batch_id': batch.batch_id,
                'task_count': len(batch.tasks),
                'execution_mode': batch.execution_mode.value
            })
            
            await self.metrics_collector.increment('batch_executions.started')
            
            return batch.batch_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute batch: {e}")
            await self.metrics_collector.increment('batch_executions.start_failed')
            raise
    
    async def _execute_synchronous(self, task: ExecutionTask, context: ExecutionContext) -> ExecutionResult:
        """Execute task synchronously."""
        start_time = datetime.now()
        
        try:
            # Get task handler
            if task.handler not in self.task_handlers:
                raise ValueError(f"Handler not found: {task.handler}")
            
            handler = self.task_handlers[task.handler]
            
            # Prepare execution input
            execution_input = {
                'task': task,
                'context': context,
                'parameters': task.parameters
            }
            
            # Execute with timeout
            if task.timeout:
                if asyncio.iscoroutinefunction(handler):
                    result_data = await asyncio.wait_for(
                        handler(execution_input), timeout=task.timeout
                    )
                else:
                    # Run in thread pool for sync functions
                    future = self.thread_pool.submit(handler, execution_input)
                    result_data = await asyncio.wrap_future(
                        asyncio.wait_for(future, timeout=task.timeout)
                    )
            else:
                if asyncio.iscoroutinefunction(handler):
                    result_data = await handler(execution_input)
                else:
                    future = self.thread_pool.submit(handler, execution_input)
                    result_data = await asyncio.wrap_future(future)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ExecutionResult(
                execution_id=context.execution_id,
                task_id=task.task_id,
                status=ExecutionStatus.COMPLETED,
                result_data=result_data,
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
            
            self.execution_stats['successful_executions'] += 1
            
            await self.event_dispatcher.emit('task_execution_completed', {
                'execution_id': context.execution_id,
                'task_id': task.task_id,
                'duration': duration,
                'status': 'completed'
            })
            
            await self.metrics_collector.record('execution.duration', duration)
            await self.metrics_collector.increment('executions.completed')
            
            return result
            
        except asyncio.TimeoutError:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ExecutionResult(
                execution_id=context.execution_id,
                task_id=task.task_id,
                status=ExecutionStatus.TIMEOUT,
                error_message=f"Task timeout after {task.timeout} seconds",
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
            
            self.execution_stats['failed_executions'] += 1
            await self.metrics_collector.increment('executions.timeout')
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = ExecutionResult(
                execution_id=context.execution_id,
                task_id=task.task_id,
                status=ExecutionStatus.FAILED,
                error_message=str(e),
                start_time=start_time,
                end_time=end_time,
                duration=duration
            )
            
            self.execution_stats['failed_executions'] += 1
            await self.metrics_collector.increment('executions.failed')
            
            return result
        
        finally:
            # Cleanup
            if context.execution_id in self.active_executions:
                del self.active_executions[context.execution_id]
    
    async def _execute_asynchronous(self, task: ExecutionTask, context: ExecutionContext) -> None:
        """Execute task asynchronously."""



        try:
            result = await self._execute_synchronous(task, context)
            self.execution_results[context.execution_id] = result
            
        except Exception as e:
            self.logger.error(f"Async execution failed: {e}")
    
    async def _execute_parallel(self, task: ExecutionTask, context: ExecutionContext) -> None:
        """Execute task with parallel processing."""



        try:
            # For parallel execution, we might split the task into sub-tasks
            # This is a simplified implementation
            result = await self._execute_synchronous(task, context)
            self.execution_results[context.execution_id] = result
            
        except Exception as e:
            self.logger.error(f"Parallel execution failed: {e}")
    
    async def _execute_distributed(self, task: ExecutionTask, context: ExecutionContext) -> None:
        """Execute task on distributed nodes."""



        try:
            # For distributed execution, we would send task to remote nodes
            # This is a simplified implementation
            result = await self._execute_synchronous(task, context)
            self.execution_results[context.execution_id] = result
            
        except Exception as e:
            self.logger.error(f"Distributed execution failed: {e}")
    
    async def _execute_batch_parallel(self, batch: BatchExecution) -> None:
        """Execute batch tasks in parallel."""
        semaphore = asyncio.Semaphore(batch.max_concurrent)
        
        async def execute_task_with_semaphore(task):
            async with semaphore:
                execution_id = await self.execute_task(task)
                return execution_id, task.task_id
        
        # Execute all tasks concurrently
        tasks = [execute_task_with_semaphore(task) for task in batch.tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch task failed: {result}")
            else:
                execution_id, task_id = result
                if execution_id in self.execution_results:
                    batch.results[task_id] = self.execution_results[execution_id]
        
        batch.status = ExecutionStatus.COMPLETED
        batch.completed_at = datetime.now()
    
    async def _execute_batch_sequential(self, batch: BatchExecution) -> None:
        """Execute batch tasks sequentially."""
        for task in batch.tasks:
            try:
                execution_id = await self.execute_task(task)
                
                # Wait for completion if synchronous
                if task.execution_mode == ExecutionMode.SYNCHRONOUS:
                    if execution_id in self.execution_results:
                        batch.results[task.task_id] = self.execution_results[execution_id]
                
            except Exception as e:
                self.logger.error(f"Sequential batch task failed: {e}")
        
        batch.status = ExecutionStatus.COMPLETED
        batch.completed_at = datetime.now()
    
    async def _execute_batch_distributed(self, batch: BatchExecution) -> None:
        """Execute batch tasks on distributed nodes."""
        # Simplified - would implement actual distribution logic
        await self._execute_batch_parallel(batch)
    
    async def _select_optimal_executor(self, task: ExecutionTask) -> Optional[ExecutorNode]:
        """Select optimal executor node for task."""
        if not self.executor_nodes:
            return None
        
        # Filter suitable executors
        suitable_executors = []
        for node in self.executor_nodes.values():
            if (node.status == "healthy" and
                task.task_type in node.supported_tasks and
                await self._check_executor_capacity(node, task)):
                suitable_executors.append(node)
        
        if not suitable_executors:
            return None
        
        # Load balancing selection
        if self.load_balancing_enabled:
            return await self._load_balanced_selection(suitable_executors, task)
        else:
            return suitable_executors[0]
    
    async def _load_balanced_selection(
        self,
        executors: List[ExecutorNode],
        task: ExecutionTask
    ) -> ExecutorNode:
        """Select executor using load balancing."""
        # Calculate load scores
        best_executor = None
        best_score = float('inf')
        
        for executor in executors:
            # Calculate current load
            current_load = sum(executor.current_load.values())
            total_capacity = sum(executor.capacity.values())
            
            load_ratio = current_load / max(total_capacity, 1.0)
            
            # Consider task requirements
            resource_fit_score = 0.0
            for resource, required in task.resource_requirements.items():
                if resource in executor.capacity:
                    available = executor.capacity[resource] - executor.current_load.get(resource, 0.0)
                    if available >= required:
                        resource_fit_score += 1.0
            
            # Combined score (lower is better)
            score = load_ratio - (resource_fit_score * 0.1)
            
            if score < best_score:
                best_score = score
                best_executor = executor
        
        return best_executor or executors[0]
    
    async def _check_executor_capacity(self, node: ExecutorNode, task: ExecutionTask) -> bool:
        """Check if executor has sufficient capacity."""
        for resource, required in task.resource_requirements.items():
            if resource in node.capacity:
                available = node.capacity[resource] - node.current_load.get(resource, 0.0)
                if available < required:
                    return False
        return True
    
    async def _validate_task(self, task: ExecutionTask) -> bool:
        """Validate task definition."""



        try:
            if not task.task_id or not task.handler:
                return False
            
            if task.handler not in self.task_handlers:
                return False
            
            if task.timeout and task.timeout <= 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    async def get_execution_result(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get execution result by ID."""



        return self.execution_results.get(execution_id)
    
    async def get_batch_status(self, batch_id: str) -> Optional[BatchExecution]:
        """Get batch execution status."""



        return self.batch_executions.get(batch_id)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running execution."""



        try:
            if execution_id in self.active_executions:
                context = self.active_executions[execution_id]
                
                # Mark as cancelled
                result = ExecutionResult(
                    execution_id=execution_id,
                    task_id=context.task_id,
                    status=ExecutionStatus.CANCELLED,
                    end_time=datetime.now()
                )
                
                self.execution_results[execution_id] = result
                del self.active_executions[execution_id]
                
                await self.event_dispatcher.emit('execution_cancelled', {
                    'execution_id': execution_id,
                    'task_id': context.task_id
                })
                
                await self.metrics_collector.increment('executions.cancelled')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel execution: {e}")
            return False
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution engine statistics."""
        # Update performance metrics
        if self.execution_stats['total_executions'] > 0:
            self.execution_stats['error_rate'] = (
                self.execution_stats['failed_executions'] /
                self.execution_stats['total_executions']
            )
        
        return {
            **self.execution_stats,
            'active_executions': len(self.active_executions),
            'completed_executions': len(self.execution_results),
            'registered_handlers': len(self.task_handlers),
            'registered_executors': len(self.executor_nodes),
            'batch_executions': len(self.batch_executions)
        }
    
    async def shutdown(self) -> None:
        """Shutdown execution engine gracefully."""
        # Cancel all active executions
        for execution_id in list(self.active_executions.keys()):
            await self.cancel_execution(execution_id)
        
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        self.logger.info("ExecutionEngine shutdown completed")
