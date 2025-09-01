"""Workflow Engine

Advanced workflow management system for orchestrating complex multi-agent processes
in the IA Influencer platform with support for parallel execution, conditional logic,
and error recovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """
Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepStatus(Enum):
    """Individual step status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


class StepType(Enum):
    """Types of workflow steps"""

    TASK = "task"                    # Execute a task on an agent
    CONDITION = "condition"          # Conditional logic
    PARALLEL = "parallel"            # Execute multiple steps in parallel
    SEQUENCE = "sequence"            # Execute steps in sequence
    LOOP = "loop"                   # Loop execution
    DELAY = "delay"                 # Wait/delay step
    DECISION = "decision"           # Decision point with multiple paths
    MERGE = "merge"                 # Merge results from parallel branches
    TRIGGER = "trigger"             # Trigger external event
    WEBHOOK = "webhook"             # Call external webhook


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    step_type: StepType = StepType.TASK
    agent_id: Optional[str] = None
    task_type: Optional[str] = None
    task_context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Step IDs
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[int] = None
    parallel_steps: List["WorkflowStep"] = field(default_factory=list)
    next_steps: Dict[str, str] = field(default_factory=dict)  # condition -> step_id
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime data
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate step execution duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_completed(self) -> bool:
        """
Check if step is completed"""
        return self.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]
    
    @property
    def is_failed(self) -> bool:
        """
Check if step failed"""
        return self.status == StepStatus.FAILED


@dataclass
class WorkflowDefinition:
    """
Workflow definition and configuration"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    global_context: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_entry_steps(self) -> List[WorkflowStep]:
        """
Get steps with no dependencies (entry points)"""
        dependency_ids = set()
        for step in self.steps:
            dependency_ids.update(step.dependencies)
        
        return [step for step in self.steps if step.step_id not in dependency_ids]
    
    def get_dependent_steps(self, step_id: str) -> List[WorkflowStep]:
        """
Get steps that depend on the given step"""
        return [step for step in self.steps if step_id in step.dependencies]


@dataclass
class WorkflowExecution:
    """
Runtime workflow execution instance"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    workflow_definition: Optional[WorkflowDefinition] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)  # step_id -> result
    active_steps: Set[str] = field(default_factory=set)
    completed_steps: Set[str] = field(default_factory=set)
    failed_steps: Set[str] = field(default_factory=set)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    # Error handling
    errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    
    # Metadata
    triggered_by: Optional[str] = None
    execution_priority: int = 0
    tags: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Calculate total execution duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def progress_percentage(self) -> float:
        """
Calculate progress percentage"""
        if not self.workflow_definition:
            return 0.0
        
        total_steps = len(self.workflow_definition.steps)
        if total_steps == 0:
            return 100.0
        
        return (len(self.completed_steps) / total_steps) * 100
    
    @property
    def is_completed(self) -> bool:
        """
Check if workflow is completed"""
        return self.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]


class WorkflowEngine:
    """
    Advanced workflow engine for multi-agent orchestration
    
    Features:
    - Sequential and parallel execution
    - Conditional logic and decision points
    - Error handling and retry policies
    - Dynamic workflow modification
    - Performance monitoring
    - Event-driven triggers
    - Resource management
    """
    
    def __init__(self, communication_hub, agent_registry):
        self.communication_hub = communication_hub
        self.agent_registry = agent_registry
        
        # Workflow storage
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []
        
        # Event system
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.workflow_triggers: Dict[str, List[str]] = {}  # trigger -> workflow_ids
        
        # Configuration
        self.max_concurrent_executions = 100
        self.execution_timeout_hours = 24
        self.cleanup_interval_hours = 6
        
        # Monitoring
        self.execution_stats: Dict[str, int] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "cancelled_executions": 0
        }
        
        # Background tasks
        self._shutdown_event = asyncio.Event()
        self._background_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> None:
        """Initialize the workflow engine"""
        try:
            # Start background tasks
            self._background_tasks.extend([
                asyncio.create_task(self._execution_monitor()),
                asyncio.create_task(self._cleanup_completed_executions()),
                asyncio.create_task(self._trigger_processor())
            ])
            
            logger.info("Workflow Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow engine: {str(e)}")
            raise
    
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a workflow definition"""
        try:
            # Validate workflow
            if not self._validate_workflow(workflow):
                logger.error(f"Invalid workflow definition: {workflow.workflow_id}")
                return False
            
            # Store workflow
            self.workflow_definitions[workflow.workflow_id] = workflow
            
            # Register triggers
            for trigger in workflow.triggers:
                trigger_name = trigger.get("name", "")
                if trigger_name:
                    if trigger_name not in self.workflow_triggers:
                        self.workflow_triggers[trigger_name] = []
                    self.workflow_triggers[trigger_name].append(workflow.workflow_id)
            
            logger.info(f"Workflow {workflow.name} registered with ID {workflow.workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register workflow: {str(e)}")
            return False
    
    async def execute_workflow(self, workflow_id: str, context: Dict[str, Any] = None, 
                              triggered_by: str = None) -> str:
        """Execute a workflow"""
        try:
            # Get workflow definition
            workflow_def = self.workflow_definitions.get(workflow_id)
            if not workflow_def:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Check execution limits
            if len(self.active_executions) >= self.max_concurrent_executions:
                raise RuntimeError("Maximum concurrent executions reached")
            
            # Create execution instance
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                workflow_definition=workflow_def,
                context=context or {},
                triggered_by=triggered_by,
                started_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            # Merge global context
            execution.context.update(workflow_def.global_context)
            
            # Store execution
            self.active_executions[execution.execution_id] = execution
            
            # Start execution
            execution.status = WorkflowStatus.RUNNING
            asyncio.create_task(self._execute_workflow_async(execution))
            
            # Update statistics
            self.execution_stats["total_executions"] += 1
            
            # Trigger event
            await self._trigger_event("workflow_started", {
                "execution_id": execution.execution_id,
                "workflow_id": workflow_id,
                "triggered_by": triggered_by
            })
            
            logger.info(f"Started workflow execution {execution.execution_id}")
            return execution.execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {str(e)}")
            raise
    
    async def _execute_workflow_async(self, execution: WorkflowExecution) -> None:
        """Asynchronous workflow execution"""
        try:
            workflow_def = execution.workflow_definition
            
            # Execute entry steps
            entry_steps = workflow_def.get_entry_steps()
            await self._execute_steps_parallel(execution, entry_steps)
            
            # Continue execution until all steps completed
            while not self._is_workflow_complete(execution):
                # Find ready steps (dependencies satisfied)
                ready_steps = self._get_ready_steps(execution)
                
                if not ready_steps:
                    # Check for deadlock
                    if execution.active_steps:
                        logger.warning(f"Workflow {execution.execution_id} appears to be deadlocked")
                        await asyncio.sleep(5)  # Wait a bit and check again
                        continue
                    else:
                        # No more steps to execute
                        break
                
                # Execute ready steps
                await self._execute_steps_parallel(execution, ready_steps)
                
                # Brief pause to prevent tight loop
                await asyncio.sleep(0.1)
            
            # Complete workflow
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            
            # Update statistics
            self.execution_stats["successful_executions"] += 1
            
            # Trigger completion event
            await self._trigger_event("workflow_completed", {
                "execution_id": execution.execution_id,
                "duration": execution.duration.total_seconds() if execution.duration else 0,
                "steps_completed": len(execution.completed_steps)
            })
            
            logger.info(f"Workflow execution {execution.execution_id} completed successfully")
            
        except Exception as e:
            # Handle workflow failure
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.errors.append({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "step_id": None
            })
            
            # Update statistics
            self.execution_stats["failed_executions"] += 1
            
            # Trigger failure event
            await self._trigger_event("workflow_failed", {
                "execution_id": execution.execution_id,
                "error": str(e)
            })
            
            logger.error(f"Workflow execution {execution.execution_id} failed: {str(e)}")
        
        finally:
            # Move to history
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
                self.execution_history.append(execution)
    
    async def _execute_steps_parallel(self, execution: WorkflowExecution, steps: List[WorkflowStep]) -> None:
        """Execute multiple steps in parallel"""
        if not steps:
            return
        
        # Create tasks for parallel execution
        tasks = []
        for step in steps:
            if step.step_id not in execution.active_steps and step.step_id not in execution.completed_steps:
                task = asyncio.create_task(self._execute_step(execution, step))
                tasks.append(task)
                execution.active_steps.add(step.step_id)
        
        # Wait for all tasks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Step execution error: {str(result)}")
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep) -> None:
        """Execute a single workflow step"""
        try:
            step.status = StepStatus.RUNNING
            step.started_at = datetime.utcnow()
            execution.last_activity = step.started_at
            
            logger.debug(f"Executing step {step.name} ({step.step_id})")
            
            # Execute based on step type
            if step.step_type == StepType.TASK:
                result = await self._execute_task_step(execution, step)
            elif step.step_type == StepType.CONDITION:
                result = await self._execute_condition_step(execution, step)
            elif step.step_type == StepType.PARALLEL:
                result = await self._execute_parallel_step(execution, step)
            elif step.step_type == StepType.SEQUENCE:
                result = await self._execute_sequence_step(execution, step)
            elif step.step_type == StepType.DELAY:
                result = await self._execute_delay_step(execution, step)
            elif step.step_type == StepType.DECISION:
                result = await self._execute_decision_step(execution, step)
            else:
                raise ValueError(f"Unsupported step type: {step.step_type}")
            
            # Store result
            step.result = result
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            execution.step_results[step.step_id] = result
            execution.completed_steps.add(step.step_id)
            execution.active_steps.discard(step.step_id)
            
            logger.debug(f"Step {step.name} completed successfully")
            
        except Exception as e:
            # Handle step failure
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            
            execution.failed_steps.add(step.step_id)
            execution.active_steps.discard(step.step_id)
            execution.errors.append({
                "step_id": step.step_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Check retry policy
            if await self._should_retry_step(execution, step):
                step.retry_count += 1
                step.status = StepStatus.RETRY
                # Re-queue for execution
                asyncio.create_task(self._retry_step_after_delay(execution, step))
            else:
                # Check if failure should fail entire workflow
                if not execution.workflow_definition.error_handling.get("continue_on_error", False):
                    raise
            
            logger.error(f"Step {step.name} failed: {str(e)}")
    
    async def _execute_task_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a task step on an agent"""
        if not step.agent_id or not step.task_type:
            raise ValueError("Task step requires agent_id and task_type")
        
        # Get agent
        agent = self.agent_registry.agents.get(step.agent_id)
        if not agent:
            raise ValueError(f"Agent {step.agent_id} not found")
        
        # Check if agent can handle task
        if not await agent.can_handle_task(step.task_type, step.task_context):
            raise ValueError(f"Agent {step.agent_id} cannot handle task {step.task_type}")
        
        # Create task
        from .base_agent import AgentTask, AgentPriority
        
        task = AgentTask(
            task_type=step.task_type,
            context=step.task_context,
            timeout_seconds=step.timeout_seconds,
            priority=AgentPriority.MEDIUM
        )
        
        # Execute task
        result = await agent.execute_task(task)
        return result
    
    async def _get_ready_steps(self, execution: WorkflowExecution) -> List[WorkflowStep]:
        """Get steps that are ready to execute (dependencies satisfied)"""
        ready_steps = []
        
        for step in execution.workflow_definition.steps:
            if (step.step_id not in execution.completed_steps and 
                step.step_id not in execution.active_steps and
                step.step_id not in execution.failed_steps):
                
                # Check if all dependencies are satisfied
                dependencies_satisfied = all(
                    dep_id in execution.completed_steps 
                    for dep_id in step.dependencies
                )
                
                # Check conditions
                conditions_satisfied = await self._evaluate_step_conditions(execution, step)
                
                if dependencies_satisfied and conditions_satisfied:
                    ready_steps.append(step)
        
        return ready_steps
    
    async def _is_workflow_complete(self, execution: WorkflowExecution) -> bool:
        """
Check if workflow execution is complete"""
        workflow_def = execution.workflow_definition
        
        # All steps completed or failed
        total_steps = len(workflow_def.steps)
        processed_steps = len(execution.completed_steps) + len(execution.failed_steps)
        
        return processed_steps >= total_steps and not execution.active_steps
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
Get status of workflow execution"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            # Check history
            for hist_execution in self.execution_history:
                if hist_execution.execution_id == execution_id:
                    execution = hist_execution
                    break
        
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "progress_percentage": execution.progress_percentage,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "duration": execution.duration.total_seconds() if execution.duration else None,
            "completed_steps": len(execution.completed_steps),
            "failed_steps": len(execution.failed_steps),
            "active_steps": len(execution.active_steps),
            "errors": execution.errors
        }
    
    async def can_handle_workflow(self, workflow_definition: WorkflowDefinition) -> bool:
        """Check if all required agents and capabilities are available"""
        for step in workflow_definition.steps:
            if step.step_type == StepType.TASK:
                if not step.agent_id:
                    return False
                
                agent = self.agent_registry.agents.get(step.agent_id)
                if not agent:
                    return False
                
                if not await agent.can_handle_task(step.task_type, step.task_context):
                    return False
        
        return True
    
    # Additional helper methods for validation, monitoring, and step execution would be implemented here
