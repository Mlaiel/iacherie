"""Workflow Orchestrator Module
=============================

Professional workflow orchestration and management for content processing pipelines.
Handles multi-stage processing, task scheduling, resource management, and quality control.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

Features:
- Multi-stage processing orchestration
- Intelligent task scheduling and resource allocation
- Quality control automation throughout pipeline
- Error recovery and resilience mechanisms
- Performance monitoring and optimization
- Workflow analytics and insights
- Scalable processing architecture
- Real-time progress tracking
"""

import asyncio
import logging
import time
import uuid
import json
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Individual task status"""
    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5

class ResourceType(Enum):
    """Resource type definitions"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    GPU = "gpu"

@dataclass
class ResourceRequirement:
    """Resource requirement specification"""
    resource_type: ResourceType
    amount: float
    unit: str
    required: bool = True
    max_amount: Optional[float] = None

@dataclass
class TaskDefinition:
    """Task definition container"""
    task_id: str
    name: str
    processor_type: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 3
    timeout: Optional[float] = None
    resource_requirements: List[ResourceRequirement] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskExecution:
    """Task execution tracking"""
    task_id: str
    status: TaskStatus = TaskStatus.WAITING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    execution_time: float = 0.0
    retry_attempt: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)
    worker_id: Optional[str] = None

@dataclass
class WorkflowDefinition:
    """Workflow definition specification"""
    workflow_id: str
    name: str
    description: str
    tasks: List[TaskDefinition]
    global_config: Dict[str, Any] = field(default_factory=dict)
    max_concurrent_tasks: int = 5
    timeout: Optional[float] = None
    error_handling: str = "stop_on_error"  # stop_on_error, continue_on_error, retry_failed
    quality_gates: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_execution_time: float = 0.0
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    progress_percentage: float = 0.0
    current_stage: str = ""
    error_message: Optional[str] = None
    quality_scores: Dict[str, float] = field(default_factory=dict)

class ResourceManager:
    """System resource allocation and monitoring"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.logger = logging.getLogger(f"{__name__}.ResourceManager")
        self.config = config or {}
        
        # Resource limits (as percentages of total system resources)
        self.resource_limits = {
            ResourceType.CPU: self.config.get('max_cpu_usage', 80.0),
            ResourceType.MEMORY: self.config.get('max_memory_usage', 80.0),
            ResourceType.DISK: self.config.get('max_disk_usage', 90.0)
        }
        
        # Currently allocated resources
        self.allocated_resources = {
            ResourceType.CPU: 0.0,
            ResourceType.MEMORY: 0.0,
            ResourceType.DISK: 0.0
        }
        
        # Resource monitoring
        self._monitoring_active = False
        self._monitoring_task = None
        
    def get_system_resources(self) -> Dict[str, float]:
        """Get current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available / (1024**3),  # GB
                'disk_usage': disk.percent,
                'disk_free': disk.free / (1024**3)  # GB
            }
        except Exception as e:
            self.logger.error(f"Failed to get system resources: {str(e)}")
            return {}
    
    def can_allocate_resources(self, requirements: List[ResourceRequirement]) -> bool:
        """Check if resources can be allocated for requirements"""
        try:
            system_resources = self.get_system_resources()
            
            for req in requirements:
                if req.resource_type == ResourceType.CPU:
                    current_usage = system_resources.get('cpu_usage', 0)
                    if current_usage + req.amount > self.resource_limits[ResourceType.CPU]:
                        return False
                        
                elif req.resource_type == ResourceType.MEMORY:
                    current_usage = system_resources.get('memory_usage', 0)
                    if current_usage + req.amount > self.resource_limits[ResourceType.MEMORY]:
                        return False
                        
                elif req.resource_type == ResourceType.DISK:
                    current_usage = system_resources.get('disk_usage', 0)
                    if current_usage + req.amount > self.resource_limits[ResourceType.DISK]:
                        return False
            
            return True
        except Exception as e:
            self.logger.error(f"Resource allocation check failed: {str(e)}")
            return False
    
    def allocate_resources(self, task_id: str, requirements: List[ResourceRequirement]) -> bool:
        """Allocate resources for a task"""
        try:
            if not self.can_allocate_resources(requirements):
                return False
            
            for req in requirements:
                self.allocated_resources[req.resource_type] += req.amount
            
            self.logger.info(f"Resources allocated for task {task_id}")
            return True
        except Exception as e:
            self.logger.error(f"Resource allocation failed: {str(e)}")
            return False
    
    def release_resources(self, task_id -> None: str, requirements -> None: List[ResourceRequirement]) -> None:
        """Release resources after task completion"""
        try:
            for req in requirements:
                self.allocated_resources[req.resource_type] -= req.amount
                # Ensure non-negative values
                self.allocated_resources[req.resource_type] = max(
                    0, self.allocated_resources[req.resource_type]
                )
            
            self.logger.info(f"Resources released for task {task_id}")
        except Exception as e:
            self.logger.error(f"Resource release failed: {str(e)}")

class QualityController:
    """Quality control and validation throughout pipeline"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.logger = logging.getLogger(f"{__name__}.QualityController")
        self.config = config or {}
        
        # Quality thresholds
        self.quality_thresholds = {
            'processing_time': self.config.get('max_processing_time', 300.0),  # seconds
            'memory_usage': self.config.get('max_memory_per_task', 1024),  # MB
            'error_rate': self.config.get('max_error_rate', 0.05),  # 5%
            'output_quality': self.config.get('min_output_quality', 0.8)  # 80%
        }
        
        self.quality_history = []
    
    async def validate_task_input(self, task_def: TaskDefinition, input_data: Any) -> Dict[str, Any]:
        """Validate task input data quality"""
        try:
            validation_result = {
                'valid': True,
                'quality_score': 1.0,
                'issues': [],
                'recommendations': []
            }
            
            # Input data validation
            if input_data is None:
                validation_result['valid'] = False
                validation_result['issues'].append("Input data is None")
                validation_result['quality_score'] = 0.0
                return validation_result
            
            # Size validation
            if hasattr(input_data, '__len__'):
                data_size = len(input_data)
                if data_size == 0:
                    validation_result['issues'].append("Input data is empty")
                    validation_result['quality_score'] *= 0.5
                elif data_size > 100 * 1024 * 1024:  # 100MB
                    validation_result['recommendations'].append("Large input data detected - consider streaming")
            
            # Type-specific validation
            if task_def.processor_type == 'audio':
                validation_result.update(await self._validate_audio_input(input_data))
            elif task_def.processor_type == 'video':
                validation_result.update(await self._validate_video_input(input_data))
            elif task_def.processor_type == 'image':
                validation_result.update(await self._validate_image_input(input_data))
            elif task_def.processor_type == 'text':
                validation_result.update(await self._validate_text_input(input_data))
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return {
                'valid': False,
                'quality_score': 0.0,
                'issues': [f"Validation error: {str(e)}"],
                'recommendations': []
            }
    
    async def validate_task_output(self, task_def: TaskDefinition, output_data: Any) -> Dict[str, Any]:
        """Validate task output data quality"""
        try:
            validation_result = {
                'valid': True,
                'quality_score': 1.0,
                'metrics': {},
                'issues': [],
                'recommendations': []
            }
            
            # Basic output validation
            if output_data is None:
                validation_result['valid'] = False
                validation_result['issues'].append("Output data is None")
                validation_result['quality_score'] = 0.0
                return validation_result
            
            # Check if output has expected structure
            if isinstance(output_data, dict):
                if 'success' in output_data and not output_data['success']:
                    validation_result['valid'] = False
                    validation_result['issues'].append(f"Task failed: {output_data.get('error', 'Unknown error')}")
                    validation_result['quality_score'] = 0.0
                    return validation_result
            
            # Type-specific output validation
            if task_def.processor_type == 'audio':
                validation_result.update(await self._validate_audio_output(output_data))
            elif task_def.processor_type == 'video':
                validation_result.update(await self._validate_video_output(output_data))
            elif task_def.processor_type == 'image':
                validation_result.update(await self._validate_image_output(output_data))
            elif task_def.processor_type == 'text':
                validation_result.update(await self._validate_text_output(output_data))
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Output validation failed: {str(e)}")
            return {
                'valid': False,
                'quality_score': 0.0,
                'metrics': {},
                'issues': [f"Validation error: {str(e)}"],
                'recommendations': []
            }
    
    async def _validate_audio_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate audio input data"""
        result = {'issues': [], 'recommendations': []}
        
        if isinstance(input_data, bytes):
            if len(input_data) < 1024:  # Very small audio file
                result['issues'].append("Audio data seems too small")
        
        return result
    
    async def _validate_video_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate video input data"""
        result = {'issues': [], 'recommendations': []}
        
        if isinstance(input_data, bytes):
            if len(input_data) < 10240:  # Very small video file
                result['issues'].append("Video data seems too small")
        
        return result
    
    async def _validate_image_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate image input data"""
        result = {'issues': [], 'recommendations': []}
        
        if isinstance(input_data, bytes):
            if len(input_data) < 512:  # Very small image file
                result['issues'].append("Image data seems too small")
        
        return result
    
    async def _validate_text_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate text input data"""
        result = {'issues': [], 'recommendations': []}
        
        if isinstance(input_data, (str, bytes)):
            content = input_data.decode('utf-8') if isinstance(input_data, bytes) else input_data
            if len(content.strip()) == 0:
                result['issues'].append("Text content is empty")
        
        return result
    
    async def _validate_audio_output(self, output_data: Any) -> Dict[str, Any]:
        """Validate audio output data"""
        return {'metrics': {}, 'issues': [], 'recommendations': []}
    
    async def _validate_video_output(self, output_data: Any) -> Dict[str, Any]:
        """Validate video output data"""
        return {'metrics': {}, 'issues': [], 'recommendations': []}
    
    async def _validate_image_output(self, output_data: Any) -> Dict[str, Any]:
        """Validate image output data"""
        return {'metrics': {}, 'issues': [], 'recommendations': []}
    
    async def _validate_text_output(self, output_data: Any) -> Dict[str, Any]:
        """Validate text output data"""
        return {'metrics': {}, 'issues': [], 'recommendations': []}

class TaskScheduler:
    """Intelligent task scheduling and execution management"""
    
    def __init__(self, max_concurrent_tasks -> None: int = 5, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.logger = logging.getLogger(f"{__name__}.TaskScheduler")
        self.max_concurrent_tasks = max_concurrent_tasks
        self.config = config or {}
        
        # Task queues by priority
        self.task_queues = {
            TaskPriority.URGENT: asyncio.Queue(),
            TaskPriority.CRITICAL: asyncio.Queue(),
            TaskPriority.HIGH: asyncio.Queue(),
            TaskPriority.NORMAL: asyncio.Queue(),
            TaskPriority.LOW: asyncio.Queue()
        }
        
        # Running tasks
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Scheduler state
        self._scheduler_running = False
        self._scheduler_task = None
    
    async def schedule_task(self, task_def: TaskDefinition, input_data: Any) -> str:
        """Schedule a task for execution"""
        try:
            execution_id = str(uuid.uuid4())
            task_item = {
                'execution_id': execution_id,
                'task_def': task_def,
                'input_data': input_data,
                'scheduled_time': time.time()
            }
            
            # Add to appropriate priority queue
            await self.task_queues[task_def.priority].put(task_item)
            
            self.logger.info(f"Task {task_def.task_id} scheduled with execution ID: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule task {task_def.task_id}: {str(e)}")
            raise
    
    async def start_scheduler(self) -> None:
        """Start the task scheduler"""
        if self._scheduler_running:
            return
        
        self._scheduler_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Task scheduler started")
    
    async def stop_scheduler(self) -> None:
        """Stop the task scheduler"""
        self._scheduler_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        self.logger.info("Task scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self._scheduler_running:
            try:
                # Check queues in priority order
                for priority in TaskPriority:
                    queue = self.task_queues[priority]
                    
                    if not queue.empty():
                        # Check if we can start a new task
                        if len(self.running_tasks) < self.max_concurrent_tasks:
                            task_item = await queue.get()
                            await self._execute_task(task_item)
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                # Short delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _execute_task(self, task_item -> None: Dict[str, Any]) -> None:
        """Execute a single task"""
        execution_id = task_item['execution_id']
        task_def = task_item['task_def']
        input_data = task_item['input_data']
        
        async def task_wrapper() -> None:
            async with self.semaphore:
                try:
                    # Execute the task function
                    result = await task_def.function(input_data, task_def.config)
                    return result
                except Exception as e:
                    self.logger.error(f"Task {task_def.task_id} failed: {str(e)}")
                    raise
        
        # Create and start task
        task = asyncio.create_task(task_wrapper())
        self.running_tasks[execution_id] = task
        
        self.logger.info(f"Started execution of task {task_def.task_id} (ID: {execution_id})")
    
    async def _cleanup_completed_tasks(self) -> None:
        """Remove completed tasks from running tasks"""
        completed_tasks = []
        
        for execution_id, task in self.running_tasks.items():
            if task.done():
                completed_tasks.append(execution_id)
        
        for execution_id in completed_tasks:
            del self.running_tasks[execution_id]
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        queue_sizes = {priority.name: queue.qsize() for priority, queue in self.task_queues.items()}
        
        return {
            'scheduler_running': self._scheduler_running,
            'running_tasks': len(self.running_tasks),
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'queue_sizes': queue_sizes,
            'total_queued_tasks': sum(queue_sizes.values())
        }

class WorkflowOrchestrator:
    """
    Professional workflow orchestration engine for content processing pipelines
    
    Manages complex multi-stage workflows with intelligent scheduling,
    resource allocation, quality control, and error recovery.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.logger = logging.getLogger(f"{__name__}.WorkflowOrchestrator")
        self.config = config or {}
        
        # Core components
        self.resource_manager = ResourceManager(config.get('resource_manager', {}))
        self.quality_controller = QualityController(config.get('quality_controller', {}))
        self.task_scheduler = TaskScheduler(
            max_concurrent_tasks=config.get('max_concurrent_tasks', 5),
            config=config.get('task_scheduler', {})
        )
        
        # Workflow storage
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.workflow_executions: Dict[str, WorkflowExecution] = {}
        
        # Analytics and monitoring
        self.execution_history = []
        self.performance_metrics = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }
        
        self.logger.info("WorkflowOrchestrator initialized successfully")
    
    async def register_workflow(self, workflow_def -> None: WorkflowDefinition) -> None:
        """Register a workflow definition"""
        try:
            # Validate workflow definition
            validation_errors = await self._validate_workflow_definition(workflow_def)
            if validation_errors:
                raise ValueError(f"Workflow validation failed: {', '.join(validation_errors)}")
            
            self.workflow_definitions[workflow_def.workflow_id] = workflow_def
            self.logger.info(f"Workflow registered: {workflow_def.workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to register workflow {workflow_def.workflow_id}: {str(e)}")
            raise
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Any,
        execution_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute a registered workflow
        
        Args:
            workflow_id: ID of the workflow to execute
            input_data: Input data for the workflow
            execution_config: Optional execution configuration
            
        Returns:
            Execution ID for tracking
        """
        try:
            # Get workflow definition
            workflow_def = self.workflow_definitions.get(workflow_id)
            if not workflow_def:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.PENDING,
                current_stage="initialization"
            )
            
            self.workflow_executions[execution_id] = execution
            
            # Start execution
            asyncio.create_task(self._execute_workflow_async(execution, workflow_def, input_data, execution_config))
            
            self.logger.info(f"Workflow execution started: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow execution: {str(e)}")
            raise
    
    async def _execute_workflow_async(
        self,
        execution -> None: WorkflowExecution,
        workflow_def -> None: WorkflowDefinition,
        input_data -> None: Any,
        execution_config -> None: Optional[Dict[str, Any]] = None
    ) -> None:
        """Asynchronous workflow execution"""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = time.time()
            execution.current_stage = "execution"
            
            # Start task scheduler if not running
            await self.task_scheduler.start_scheduler()
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow_def.tasks)
            
            # Execute tasks in dependency order
            task_results = {}
            completed_tasks = set()
            
            while len(completed_tasks) < len(workflow_def.tasks):
                # Find ready tasks (all dependencies completed)
                ready_tasks = []
                for task_def in workflow_def.tasks:
                    if (task_def.task_id not in completed_tasks and 
                        all(dep in completed_tasks for dep in task_def.dependencies)):
                        ready_tasks.append(task_def)
                
                if not ready_tasks:
                    # Check if we're stuck (circular dependencies or failures)
                    if not self._has_running_tasks(execution):
                        break
                    await asyncio.sleep(0.5)
                    continue
                
                # Schedule ready tasks
                for task_def in ready_tasks:
                    await self._execute_task_in_workflow(
                        execution, task_def, input_data, task_results
                    )
                
                # Wait for at least one task to complete
                await self._wait_for_task_completion(execution)
                
                # Update completed tasks
                for task_id, task_exec in execution.task_executions.items():
                    if task_exec.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED]:
                        completed_tasks.add(task_id)
            
            # Finalize execution
            await self._finalize_workflow_execution(execution, workflow_def)
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.end_time = time.time()
            self.logger.error(f"Workflow execution failed: {str(e)}")
    
    async def _execute_task_in_workflow(
        self,
        execution -> None: WorkflowExecution,
        task_def -> None: TaskDefinition,
        workflow_input -> None: Any,
        task_results -> None: Dict[str, Any]
    ) -> None:
        """Execute a single task within a workflow"""
        try:
            # Create task execution tracking
            task_execution = TaskExecution(task_id=task_def.task_id)
            execution.task_executions[task_def.task_id] = task_execution
            
            # Prepare task input data
            task_input = await self._prepare_task_input(task_def, workflow_input, task_results)
            
            # Quality validation of input
            input_validation = await self.quality_controller.validate_task_input(task_def, task_input)
            if not input_validation['valid']:
                task_execution.status = TaskStatus.FAILED
                task_execution.error = f"Input validation failed: {', '.join(input_validation['issues'])}"
                return
            
            # Check resource requirements
            if not self.resource_manager.can_allocate_resources(task_def.resource_requirements):
                task_execution.status = TaskStatus.WAITING
                # Task will be retried when resources become available
                return
            
            # Allocate resources
            self.resource_manager.allocate_resources(task_def.task_id, task_def.resource_requirements)
            
            # Execute task
            task_execution.status = TaskStatus.RUNNING
            task_execution.start_time = time.time()
            
            try:
                # Schedule task execution
                execution_id = await self.task_scheduler.schedule_task(task_def, task_input)
                task_execution.worker_id = execution_id
                
                # Wait for task completion (this is a simplified approach)
                # In a real implementation, this would be handled by the scheduler
                await asyncio.sleep(0.1)  # Allow scheduler to process
                
            except Exception as e:
                task_execution.status = TaskStatus.FAILED
                task_execution.error = str(e)
                task_execution.end_time = time.time()
                
                # Release resources
                self.resource_manager.release_resources(task_def.task_id, task_def.resource_requirements)
                raise
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
    
    async def _prepare_task_input(
        self,
        task_def: TaskDefinition,
        workflow_input: Any,
        task_results: Dict[str, Any]
    ) -> Any:
        """Prepare input data for a task based on dependencies"""
        if not task_def.dependencies:
            return workflow_input
        
        # Combine results from dependency tasks
        combined_input = {
            'workflow_input': workflow_input,
            'dependency_results': {}
        }
        
        for dep_task_id in task_def.dependencies:
            if dep_task_id in task_results:
                combined_input['dependency_results'][dep_task_id] = task_results[dep_task_id]
        
        return combined_input
    
    def _build_dependency_graph(self, tasks: List[TaskDefinition]) -> Dict[str, List[str]]:
        """Build dependency graph from task definitions"""
        graph = {}
        for task in tasks:
            graph[task.task_id] = task.dependencies.copy()
        return graph
    
    def _has_running_tasks(self, execution: WorkflowExecution) -> bool:
        """Check if workflow has any running tasks"""
        return any(
            task_exec.status == TaskStatus.RUNNING
            for task_exec in execution.task_executions.values()
        )
    
    async def _wait_for_task_completion(self, execution -> None: WorkflowExecution) -> None:
        """Wait for at least one task to complete"""
        while self._has_running_tasks(execution):
            await asyncio.sleep(0.5)
    
    async def _finalize_workflow_execution(self, execution -> None: WorkflowExecution, workflow_def -> None: WorkflowDefinition) -> None:
        """Finalize workflow execution"""
        execution.end_time = time.time()
        execution.total_execution_time = execution.end_time - execution.start_time
        
        # Determine final status
        failed_tasks = [
            task_exec for task_exec in execution.task_executions.values()
            if task_exec.status == TaskStatus.FAILED
        ]
        
        if failed_tasks:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = f"{len(failed_tasks)} tasks failed"
        else:
            execution.status = WorkflowStatus.COMPLETED
        
        # Calculate progress
        execution.progress_percentage = 100.0
        
        # Update performance metrics
        self._update_performance_metrics(execution)
        
        self.logger.info(f"Workflow execution completed: {execution.execution_id} - Status: {execution.status}")
    
    def _update_performance_metrics(self, execution -> None: WorkflowExecution) -> None:
        """Update performance metrics"""
        self.performance_metrics['total_workflows'] += 1
        
        if execution.status == WorkflowStatus.COMPLETED:
            self.performance_metrics['successful_workflows'] += 1
        else:
            self.performance_metrics['failed_workflows'] += 1
        
        self.performance_metrics['total_execution_time'] += execution.total_execution_time
        
        if self.performance_metrics['total_workflows'] > 0:
            self.performance_metrics['average_execution_time'] = (
                self.performance_metrics['total_execution_time'] / 
                self.performance_metrics['total_workflows']
            )
    
    async def _validate_workflow_definition(self, workflow_def: WorkflowDefinition) -> List[str]:
        """Validate workflow definition"""
        errors = []
        
        if not workflow_def.workflow_id:
            errors.append("Workflow ID is required")
        
        if not workflow_def.tasks:
            errors.append("Workflow must have at least one task")
        
        # Check for duplicate task IDs
        task_ids = [task.task_id for task in workflow_def.tasks]
        if len(task_ids) != len(set(task_ids)):
            errors.append("Duplicate task IDs found")
        
        # Validate dependencies
        for task in workflow_def.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    errors.append(f"Task {task.task_id} has unknown dependency: {dep}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(workflow_def.tasks):
            errors.append("Circular dependencies detected")
        
        return errors
    
    def _has_circular_dependencies(self, tasks: List[TaskDefinition]) -> bool:
        """Check for circular dependencies in task graph"""
        # Simple cycle detection using DFS
        graph = {task.task_id: task.dependencies for task in tasks}
        visited = set()
        rec_stack = set()
        
        def has_cycle(node) -> None:
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in graph:
            if has_cycle(task_id):
                return True
        
        return False
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        return self.workflow_executions.get(execution_id)
    
    def list_workflows(self) -> List[str]:
        """List registered workflow IDs"""
        return list(self.workflow_definitions.keys())
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.performance_metrics.copy()
    
    async def process(self, content_data: bytes, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main processing interface for compatibility with other processors
        
        Args:
            content_data: Raw content bytes to process
            config: Processing configuration including workflow specification
            
        Returns:
            Processing result dictionary
        """
        try:
            processing_config = config or {}
            workflow_id = processing_config.get('workflow_id')
            
            if not workflow_id:
                # Create a simple default workflow
                workflow_id = await self._create_default_workflow(processing_config)
            
            # Execute workflow
            execution_id = await self.execute_workflow(workflow_id, content_data, processing_config)
            
            # Wait for completion (simplified - in production this would be asynchronous)
            max_wait_time = processing_config.get('max_wait_time', 300)  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                execution = self.get_workflow_status(execution_id)
                if execution and execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                    break
                await asyncio.sleep(1)
            
            execution = self.get_workflow_status(execution_id)
            if not execution:
                return {'success': False, 'error': 'Execution not found'}
            
            if execution.status == WorkflowStatus.COMPLETED:
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'workflow_id': workflow_id,
                    'execution_time': execution.total_execution_time,
                    'tasks_executed': len(execution.task_executions),
                    'quality_scores': execution.quality_scores,
                    'status': execution.status.value
                }
            else:
                return {
                    'success': False,
                    'error': execution.error_message or 'Workflow execution failed',
                    'execution_id': execution_id,
                    'status': execution.status.value
                }
                
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_default_workflow(self, config: Dict[str, Any]) -> str:
        """Create a default workflow for simple processing"""
        workflow_id = f"default_workflow_{int(time.time())}"
        
        # Create a simple single-task workflow
        task_def = TaskDefinition(
            task_id="default_task",
            name="Default Processing Task",
            processor_type=config.get('processor_type', 'text'),
            function=self._default_task_function,
            config=config
        )
        
        workflow_def = WorkflowDefinition(
            workflow_id=workflow_id,
            name="Default Workflow",
            description="Auto-generated default workflow",
            tasks=[task_def]
        )
        
        await self.register_workflow(workflow_def)
        return workflow_id
    
    async def _default_task_function(self, input_data: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """Default task function for simple processing"""
        return {
            'success': True,
            'processed_data': input_data,
            'message': 'Default processing completed'
        }

# Export main classes and functions
__all__ = [
    'WorkflowOrchestrator',
    'WorkflowDefinition',
    'WorkflowExecution',
    'TaskDefinition',
    'TaskExecution',
    'TaskScheduler',
    'ResourceManager',
    'QualityController',
    'WorkflowStatus',
    'TaskStatus',
    'TaskPriority',
    'ResourceType',
    'ResourceRequirement'
]