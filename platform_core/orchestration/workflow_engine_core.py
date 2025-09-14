"""
Workflow Engine Core module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Workflow Engine Core - Enterprise Component
Complex business workflow automation and management system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive workflow automation capabilities including:
- Complex business workflow automation
- Multi-step process coordination
- State management and persistence
- Error handling and recovery mechanisms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from abc import ABC, abstractmethod
import pickle
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    WAITING = "waiting"


class WorkflowExecutionStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ConditionalOperator(Enum):
    """Conditional operators for task execution"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    EXISTS = "exists"


@dataclass
class TaskCondition:
    """Condition for conditional task execution"""
    variable: str
    operator: ConditionalOperator
    value: Any
    description: Optional[str] = None


@dataclass
class TaskRetryPolicy:
    """Retry policy for task execution"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_backoff: bool = True
    retry_on_exceptions: List[str] = field(default_factory=lambda: ["Exception"])


@dataclass
class TaskDefinition:
    """Task definition for workflow"""
    task_id: str
    name: str
    task_type: str  # python_function, http_request, shell_command, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: List[TaskCondition] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_policy: Optional[TaskRetryPolicy] = None
    on_success: Optional[str] = None  # next task or action
    on_failure: Optional[str] = None  # failure handling
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str
    tasks: List[TaskDefinition]
    global_variables: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    max_parallel_tasks: int = 10
    error_handling: str = "fail_fast"  # fail_fast, continue, retry
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskExecution:
    """Task execution state"""
    task_id: str
    execution_id: str
    status: TaskStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    attempt_count: int = 0
    output_variables: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)


@dataclass
class WorkflowExecution:
    """Workflow execution state"""
    execution_id: str
    workflow_id: str
    status: WorkflowExecutionStatus
    variables: Dict[str, Any] = field(default_factory=dict)
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_tasks: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskExecutor(ABC):
    """Abstract base class for task executors"""
    
    @abstractmethod
    async def execute(self, task: TaskDefinition, context: Dict[str, Any]) -> Any:
        """Execute a task with given context"""
        pass


class PythonFunctionExecutor(TaskExecutor):
    """Executor for Python function tasks"""
    
    def __init__(self) -> None:
        self.functions: Dict[str, Callable] = {}
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a function for execution"""
        self.functions[name] = func
    
    async def execute(self, task: TaskDefinition, context: Dict[str, Any]) -> Any:
        """Execute a Python function task"""
        function_name = task.parameters.get("function")
        if not function_name or function_name not in self.functions:
            raise ValueError(f"Function {function_name} not found")
        
        func = self.functions[function_name]
        args = task.parameters.get("args", [])
        kwargs = task.parameters.get("kwargs", {})
        
        # Replace placeholders with context variables
        args = self._resolve_variables(args, context)
        kwargs = self._resolve_variables(kwargs, context)
        
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    def _resolve_variables(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Resolve variables in nested structures"""
        if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return context.get(var_name)
        elif isinstance(obj, dict):
            return {k: self._resolve_variables(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_variables(item, context) for item in obj]
        else:
            return obj


class HttpRequestExecutor(TaskExecutor):
    """Executor for HTTP request tasks"""
    
    def __init__(self) -> None:
        self._session: Optional[object] = None  # aiohttp.ClientSession
    
    async def execute(self, task: TaskDefinition, context: Dict[str, Any]) -> Any:
        """Execute an HTTP request task"""
        try:
            # Import aiohttp dynamically
            try:
                import aiohttp
            except ImportError:
                raise Exception("aiohttp is required for HTTP request tasks")
            
            if not self._session:
                self._session = aiohttp.ClientSession()
            
            method = task.parameters.get("method", "GET").upper()
            url = task.parameters.get("url")
            headers = task.parameters.get("headers", {})
            data = task.parameters.get("data")
            json_data = task.parameters.get("json")
            
            # Resolve variables
            url = self._resolve_variables(url, context)
            headers = self._resolve_variables(headers, context)
            data = self._resolve_variables(data, context)
            json_data = self._resolve_variables(json_data, context)
            
            async with self._session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data
            ) as response:
                result = {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "text": await response.text()
                }
                
                try:
                    result["json"] = await response.json()
                except:
                    pass
                
                return result
                
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            raise
    
    def _resolve_variables(self, obj: Any, context: Dict[str, Any]) -> Any:
        """Resolve variables in nested structures"""
        if isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return context.get(var_name)
        elif isinstance(obj, dict):
            return {k: self._resolve_variables(v, context) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._resolve_variables(item, context) for item in obj]
        else:
            return obj


class WorkflowEngineCore:
    """
    Enterprise Workflow Engine Core
    
    Provides comprehensive workflow automation capabilities including complex
    business process coordination, state management, error handling, and
    recovery mechanisms with enterprise-grade reliability.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.executors: Dict[str, TaskExecutor] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._cleanup_interval = self.config.get('cleanup_interval', 3600)
        self._max_concurrent_workflows = self.config.get('max_concurrent_workflows', 100)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Initialize default executors
        self._initialize_default_executors()
        
        logger.info("Workflow Engine Core initialized")
    
    def _initialize_default_executors(self) -> None:
        """Initialize default task executors"""
        self.executors["python_function"] = PythonFunctionExecutor()
        self.executors["http_request"] = HttpRequestExecutor()
    
    async def start(self) -> None:
        """Start the workflow engine"""
        try:
            logger.info("Starting Workflow Engine Core...")
            
            # Start background tasks
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            # Initialize core workflows
            await self._initialize_core_workflows()
            
            logger.info("Workflow Engine Core started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Workflow Engine Core: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the workflow engine"""
        try:
            logger.info("Stopping Workflow Engine Core...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel all running workflows
            for execution_id in list(self.executions.keys()):
                await self.cancel_workflow(execution_id)
            
            # Cancel cleanup task
            if self._cleanup_task:
                self._cleanup_task.cancel()
            
            # Cancel all running tasks
            for task in self.running_tasks.values():
                task.cancel()
            
            logger.info("Workflow Engine Core stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Workflow Engine Core: {e}")
    
    # Workflow Management
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a new workflow definition"""
        try:
            # Validate workflow
            if not workflow.workflow_id or not workflow.tasks:
                raise ValueError("Workflow ID and tasks are required")
            
            # Validate task dependencies
            task_ids = {task.task_id for task in workflow.tasks}
            for task in workflow.tasks:
                for dep in task.dependencies:
                    if dep not in task_ids:
                        raise ValueError(f"Task {task.task_id} has invalid dependency: {dep}")
            
            # Check for circular dependencies
            if self._has_circular_dependencies(workflow.tasks):
                raise ValueError("Workflow contains circular dependencies")
            
            # Register workflow
            self.workflows[workflow.workflow_id] = workflow
            
            logger.info(f"Workflow {workflow.workflow_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register workflow {workflow.workflow_id}: {e}")
            return False
    
    async def execute_workflow(self, workflow_id: str, input_variables: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute a workflow and return execution ID"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if len(self.executions) >= self._max_concurrent_workflows:
                raise RuntimeError("Maximum concurrent workflows limit reached")
            
            workflow = self.workflows[workflow_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution state
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowExecutionStatus.CREATED,
                variables={**workflow.global_variables, **(input_variables or {})},
                start_time=datetime.utcnow()
            )
            
            # Initialize task executions
            for task in workflow.tasks:
                task_execution = TaskExecution(
                    task_id=task.task_id,
                    execution_id=execution_id,
                    status=TaskStatus.PENDING
                )
                execution.task_executions[task.task_id] = task_execution
            
            self.executions[execution_id] = execution
            
            # Start workflow execution
            task = asyncio.create_task(self._execute_workflow(execution_id))
            self.running_tasks[execution_id] = task
            
            logger.info(f"Workflow {workflow_id} execution started with ID: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            return None
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.executions.get(execution_id)
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow"""
        try:
            if execution_id not in self.executions:
                logger.warning(f"Execution {execution_id} not found")
                return False
            
            execution = self.executions[execution_id]
            if execution.status not in [WorkflowExecutionStatus.RUNNING, WorkflowExecutionStatus.CREATED]:
                logger.warning(f"Execution {execution_id} cannot be cancelled in status: {execution.status}")
                return False
            
            # Cancel the execution task
            if execution_id in self.running_tasks:
                task = self.running_tasks[execution_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.running_tasks[execution_id]
            
            # Update execution status
            execution.status = WorkflowExecutionStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            
            logger.info(f"Workflow execution {execution_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {execution_id}: {e}")
            return False
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a running workflow"""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            if execution.status == WorkflowExecutionStatus.RUNNING:
                execution.status = WorkflowExecutionStatus.PAUSED
                logger.info(f"Workflow execution {execution_id} paused")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause workflow {execution_id}: {e}")
            return False
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            if execution_id not in self.executions:
                return False
            
            execution = self.executions[execution_id]
            if execution.status == WorkflowExecutionStatus.PAUSED:
                execution.status = WorkflowExecutionStatus.RUNNING
                logger.info(f"Workflow execution {execution_id} resumed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resume workflow {execution_id}: {e}")
            return False
    
    # Task Executor Management
    def register_executor(self, task_type: str, executor: TaskExecutor) -> None:
        """Register a custom task executor"""
        self.executors[task_type] = executor
        logger.info(f"Task executor for type '{task_type}' registered")
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a function for Python function tasks"""
        if "python_function" in self.executors:
            executor = self.executors["python_function"]
            if isinstance(executor, PythonFunctionExecutor):
                executor.register_function(name, func)
                logger.info(f"Function '{name}' registered")
    
    # Internal Methods
    async def _initialize_core_workflows(self) -> None:
        """Initialize core platform workflows"""
        try:
            # Creator Content Processing Workflow
            creator_workflow = WorkflowDefinition(
                workflow_id="creator_content_processing_v2",
                name="Advanced Creator Content Processing",
                description="Enhanced content processing workflow with error handling",
                version="2.0.0",
                tasks=[
                    TaskDefinition(
                        task_id="validate_input",
                        name="Validate Input Content",
                        task_type="python_function",
                        parameters={
                            "function": "validate_content",
                            "args": ["${content_data}"]
                        },
                        timeout=30
                    ),
                    TaskDefinition(
                        task_id="upload_content",
                        name="Upload Content",
                        task_type="http_request",
                        parameters={
                            "method": "POST",
                            "url": "http://content-service/upload",
                            "json": {"content": "${content_data}"}
                        },
                        dependencies=["validate_input"],
                        timeout=300,
                        retry_policy=TaskRetryPolicy(max_attempts=3)
                    ),
                    TaskDefinition(
                        task_id="apply_ai_protection",
                        name="Apply AI Protection",
                        task_type="http_request",
                        parameters={
                            "method": "POST",
                            "url": "http://ai-protection-service/protect",
                            "json": {"content_id": "${upload_result.content_id}"}
                        },
                        dependencies=["upload_content"],
                        timeout=600
                    ),
                    TaskDefinition(
                        task_id="enhance_seo",
                        name="Enhance SEO",
                        task_type="http_request",
                        parameters={
                            "method": "POST",
                            "url": "http://seo-service/enhance",
                            "json": {"content_id": "${upload_result.content_id}"}
                        },
                        dependencies=["apply_ai_protection"],
                        timeout=300
                    ),
                    TaskDefinition(
                        task_id="distribute_content",
                        name="Distribute Content",
                        task_type="python_function",
                        parameters={
                            "function": "distribute_content",
                            "kwargs": {
                                "content_id": "${upload_result.content_id}",
                                "channels": ["${distribution_channels}"]
                            }
                        },
                        dependencies=["enhance_seo"],
                        timeout=600
                    )
                ],
                global_variables={
                    "distribution_channels": ["web", "mobile", "social"]
                },
                timeout=3600
            )
            
            await self.register_workflow(creator_workflow)
            
            # Platform Health Check Workflow
            health_workflow = WorkflowDefinition(
                workflow_id="platform_health_monitoring",
                name="Platform Health Monitoring",
                description="Comprehensive platform health verification",
                version="1.0.0",
                tasks=[
                    TaskDefinition(
                        task_id="check_database",
                        name="Check Database Health",
                        task_type="http_request",
                        parameters={
                            "method": "GET",
                            "url": "http://database-service/health"
                        },
                        timeout=30
                    ),
                    TaskDefinition(
                        task_id="check_cache",
                        name="Check Cache Health",
                        task_type="http_request",
                        parameters={
                            "method": "GET",
                            "url": "http://cache-service/health"
                        },
                        timeout=30
                    ),
                    TaskDefinition(
                        task_id="aggregate_health",
                        name="Aggregate Health Results",
                        task_type="python_function",
                        parameters={
                            "function": "aggregate_health_results",
                            "kwargs": {
                                "database_health": "${check_database.json}",
                                "cache_health": "${check_cache.json}"
                            }
                        },
                        dependencies=["check_database", "check_cache"],
                        timeout=10
                    )
                ],
                timeout=120
            )
            
            await self.register_workflow(health_workflow)
            
            logger.info("Core workflows initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize core workflows: {e}")
    
    async def _execute_workflow(self, execution_id: str) -> None:
        """Execute a complete workflow"""
        try:
            execution = self.executions[execution_id]
            workflow = self.workflows[execution.workflow_id]
            
            execution.status = WorkflowExecutionStatus.RUNNING
            
            # Create task dependency graph
            task_graph = {task.task_id: task for task in workflow.tasks}
            remaining_tasks = set(task_graph.keys())
            
            while remaining_tasks and execution.status == WorkflowExecutionStatus.RUNNING:
                # Find tasks ready to execute
                ready_tasks = []
                for task_id in remaining_tasks:
                    task = task_graph[task_id]
                    if all(dep in execution.completed_tasks for dep in task.dependencies):
                        # Check conditions
                        if self._evaluate_conditions(task.conditions, execution.variables):
                            ready_tasks.append(task)
                
                if not ready_tasks:
                    if remaining_tasks:
                        # Check if we're waiting for paused execution
                        if execution.status == WorkflowExecutionStatus.PAUSED:
                            await asyncio.sleep(1)
                            continue
                        else:
                            execution.status = WorkflowExecutionStatus.FAILED
                            execution.error_message = "No tasks ready to execute - possible deadlock"
                            break
                    else:
                        break
                
                # Execute ready tasks (limit parallel execution)
                batch_size = min(len(ready_tasks), workflow.max_parallel_tasks)
                tasks_to_execute = ready_tasks[:batch_size]
                
                # Execute tasks in parallel
                task_futures = []
                for task in tasks_to_execute:
                    future = asyncio.create_task(self._execute_task(execution_id, task))
                    task_futures.append((task, future))
                
                # Wait for all tasks in batch to complete
                for task, future in task_futures:
                    try:
                        await future
                        remaining_tasks.discard(task.task_id)
                        execution.completed_tasks.append(task.task_id)
                    except Exception as e:
                        logger.error(f"Task {task.task_id} failed: {e}")
                        execution.failed_tasks.append(task.task_id)
                        
                        if workflow.error_handling == "fail_fast":
                            execution.status = WorkflowExecutionStatus.FAILED
                            execution.error_message = f"Task {task.task_id} failed: {e}"
                            break
                        elif workflow.error_handling == "continue":
                            remaining_tasks.discard(task.task_id)
                
                # Check for pause
                if execution.status == WorkflowExecutionStatus.PAUSED:
                    continue
                
                # Check for failure
                if execution.status == WorkflowExecutionStatus.FAILED:
                    break
            
            # Update final status
            if execution.status == WorkflowExecutionStatus.RUNNING:
                if remaining_tasks:
                    execution.status = WorkflowExecutionStatus.FAILED
                    execution.error_message = "Not all tasks completed"
                else:
                    execution.status = WorkflowExecutionStatus.COMPLETED
            
            execution.end_time = datetime.utcnow()
            
            # Cleanup task reference
            self.running_tasks.pop(execution_id, None)
            
            logger.info(f"Workflow execution {execution_id} completed with status: {execution.status}")
            
        except asyncio.CancelledError:
            execution.status = WorkflowExecutionStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            raise
        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed: {e}")
            execution.status = WorkflowExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = datetime.utcnow()
    
    async def _execute_task(self, execution_id: str, task: TaskDefinition) -> None:
        """Execute a single task"""
        try:
            execution = self.executions[execution_id]
            task_execution = execution.task_executions[task.task_id]
            
            task_execution.status = TaskStatus.RUNNING
            task_execution.start_time = datetime.utcnow()
            
            # Get task executor
            executor = self.executors.get(task.task_type)
            if not executor:
                raise ValueError(f"No executor found for task type: {task.task_type}")
            
            # Execute with retry logic
            retry_policy = task.retry_policy or TaskRetryPolicy()
            last_error = None
            
            for attempt in range(retry_policy.max_attempts):
                try:
                    task_execution.attempt_count = attempt + 1
                    
                    # Execute task with timeout
                    if task.timeout:
                        result = await asyncio.wait_for(
                            executor.execute(task, execution.variables),
                            timeout=task.timeout
                        )
                    else:
                        result = await executor.execute(task, execution.variables)
                    
                    # Update execution state
                    task_execution.result = result
                    task_execution.status = TaskStatus.COMPLETED
                    task_execution.end_time = datetime.utcnow()
                    
                    # Update workflow variables with task result
                    if isinstance(result, dict):
                        for key, value in result.items():
                            execution.variables[f"{task.task_id}.{key}"] = value
                    else:
                        execution.variables[f"{task.task_id}_result"] = result
                    
                    logger.info(f"Task {task.task_id} completed successfully (attempt {attempt + 1})")
                    return
                    
                except asyncio.TimeoutError:
                    last_error = f"Task timeout after {task.timeout} seconds"
                    if attempt < retry_policy.max_attempts - 1:
                        delay = min(
                            retry_policy.initial_delay * (2 ** attempt) if retry_policy.exponential_backoff else retry_policy.initial_delay,
                            retry_policy.max_delay
                        )
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    last_error = str(e)
                    if attempt < retry_policy.max_attempts - 1:
                        delay = min(
                            retry_policy.initial_delay * (2 ** attempt) if retry_policy.exponential_backoff else retry_policy.initial_delay,
                            retry_policy.max_delay
                        )
                        await asyncio.sleep(delay)
                    
                    logger.warning(f"Task {task.task_id} failed on attempt {attempt + 1}: {e}")
            
            # All retries exhausted
            task_execution.status = TaskStatus.FAILED
            task_execution.error = last_error
            task_execution.end_time = datetime.utcnow()
            
            logger.error(f"Task {task.task_id} failed after {retry_policy.max_attempts} attempts: {last_error}")
            raise Exception(last_error)
            
        except Exception as e:
            task_execution.status = TaskStatus.FAILED
            task_execution.error = str(e)
            task_execution.end_time = datetime.utcnow()
            raise
    
    def _evaluate_conditions(self, conditions: List[TaskCondition], variables: Dict[str, Any]) -> bool:
        """Evaluate task conditions"""
        if not conditions:
            return True
        
        for condition in conditions:
            variable_value = variables.get(condition.variable)
            
            if condition.operator == ConditionalOperator.EQUALS:
                if variable_value != condition.value:
                    return False
            elif condition.operator == ConditionalOperator.NOT_EQUALS:
                if variable_value == condition.value:
                    return False
            elif condition.operator == ConditionalOperator.GREATER_THAN:
                if not (variable_value and variable_value > condition.value):
                    return False
            elif condition.operator == ConditionalOperator.LESS_THAN:
                if not (variable_value and variable_value < condition.value):
                    return False
            elif condition.operator == ConditionalOperator.CONTAINS:
                if not (variable_value and condition.value in variable_value):
                    return False
            elif condition.operator == ConditionalOperator.EXISTS:
                if condition.variable not in variables:
                    return False
        
        return True
    
    def _has_circular_dependencies(self, tasks: List[TaskDefinition]) -> bool:
        """Check for circular dependencies in task graph"""
        task_deps = {task.task_id: set(task.dependencies) for task in tasks}
        
        def has_cycle(node, visited, rec_stack) -> None:
            visited.add(node)
            rec_stack.add(node)
            
            for dep in task_deps.get(node, set()):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for task_id in task_deps:
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    return True
        
        return False
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop for old executions"""
        while not self._shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=24)
                
                # Find old completed executions
                to_remove = []
                for execution_id, execution in self.executions.items():
                    if (execution.status in [WorkflowExecutionStatus.COMPLETED, WorkflowExecutionStatus.FAILED, WorkflowExecutionStatus.CANCELLED]
                        and execution.end_time 
                        and execution.end_time < cutoff_time):
                        to_remove.append(execution_id)
                
                # Remove old executions
                for execution_id in to_remove:
                    del self.executions[execution_id]
                    logger.info(f"Cleaned up old execution: {execution_id}")
                
                # Wait for next cleanup
                await asyncio.sleep(self._cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(300)
    
    # Context Manager Support
    async def __aenter__(self) -> None:
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()


# Factory function
def create_workflow_engine(config: Optional[Dict[str, Any]] = None) -> WorkflowEngineCore:
    """Factory function to create a Workflow Engine Core"""
    return WorkflowEngineCore(config)


# Example usage functions
async def validate_content(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Example content validation function"""
    if not content_data or "content" not in content_data:
        raise ValueError("Invalid content data")
    return {"valid": True, "content_size": len(str(content_data["content"]))}


async def distribute_content(content_id: str, channels: List[str]) -> Dict[str, Any]:
    """Example content distribution function"""
    # Simulate distribution
    await asyncio.sleep(0.1)
    return {
        "distributed": True,
        "content_id": content_id,
        "channels": channels,
        "distribution_time": datetime.utcnow().isoformat()
    }


def aggregate_health_results(database_health: Dict[str, Any], cache_health: Dict[str, Any]) -> Dict[str, Any]:
    """Example health aggregation function"""
    overall_health = "healthy"
    if database_health.get("status") != "healthy" or cache_health.get("status") != "healthy":
        overall_health = "unhealthy"
    
    return {
        "overall_status": overall_health,
        "database": database_health,
        "cache": cache_health,
        "timestamp": datetime.utcnow().isoformat()
    }


# Example usage
async def main() -> None:
    """Example usage of Workflow Engine Core"""
    async with create_workflow_engine() as engine:
        # Register custom functions
        engine.register_function("validate_content", validate_content)
        engine.register_function("distribute_content", distribute_content)
        engine.register_function("aggregate_health_results", aggregate_health_results)
        
        # Execute creator content processing workflow
        execution_id = await engine.execute_workflow(
            "creator_content_processing_v2",
            {
                "content_data": {
                    "content": "Sample content for processing",
                    "type": "text",
                    "author": "test_creator"
                }
            }
        )
        
        if execution_id:
            # Monitor execution
            while True:
                execution = await engine.get_workflow_status(execution_id)
                if execution and execution.status in [
                    WorkflowExecutionStatus.COMPLETED,
                    WorkflowExecutionStatus.FAILED,
                    WorkflowExecutionStatus.CANCELLED
                ]:
                    print(f"Workflow completed with status: {execution.status}")
                    if execution.status == WorkflowExecutionStatus.COMPLETED:
                        print(f"Final variables: {execution.variables}")
                    elif execution.error_message:
                        print(f"Error: {execution.error_message}")
                    break
                
                await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())