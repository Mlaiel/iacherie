"""
Workflow Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Workflow Engine - Utils Module - Enterprise Implementation

© 2025 Fahed Mlaiel. All rights reserved.
This software and associated documentation files are proprietary and confidential.
Unauthorized copying, distribution, or modification is strictly prohibited.
Licensed under Enterprise Commercial License.

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Developer & AI Architect - Workflow orchestration and business process automation
Backend Senior Engineer - Enterprise workflow management and state machines
ML Engineer - AI-powered workflow optimization and decision making
DevOps Engineer - Workflow infrastructure automation and monitoring

⚠️ STRICT WARNING: Any attempt to steal, copy, or use this concept, idea, or code
without written personal authorization from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"

class StepType(Enum):
    """Workflow step types"""
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    LOOP = "loop"
    WAIT = "wait"
    HUMAN_TASK = "human_task"
    API_CALL = "api_call"
    DATA_PROCESSING = "data_processing"

class ConditionOperator(Enum):
    """Condition operators for decision steps"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    EXISTS = "exists"
    MATCHES_REGEX = "matches_regex"

class TriggerType(Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    API = "api"
    FILE_UPLOAD = "file_upload"
    DATA_CHANGE = "data_change"

@dataclass
class WorkflowVariable:
    """Workflow variable definition"""
    name: str
    value: Any
    data_type: str = "string"
    is_input: bool = False
    is_output: bool = False
    description: str = ""

@dataclass
class Condition:
    """Condition for decision steps"""
    field: str
    operator: ConditionOperator
    value: Any
    next_step_id: Optional[str] = None

@dataclass
class WorkflowStep:
    """Individual workflow step"""
    id: str
    name: str
    step_type: StepType
    description: str = ""
    function_name: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Condition] = field(default_factory=list)
    next_step_id: Optional[str] = None
    error_step_id: Optional[str] = None
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    is_optional: bool = False
    parallel_steps: List[str] = field(default_factory=list)
    wait_condition: Optional[str] = None

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    id: str
    name: str
    version: str
    description: str
    steps: List[WorkflowStep]
    variables: List[WorkflowVariable] = field(default_factory=list)
    trigger_type: TriggerType = TriggerType.MANUAL
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    start_step_id: str = ""
    timeout_minutes: int = 60
    max_concurrent_instances: int = 1
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"

@dataclass
class WorkflowInstance:
    """Workflow execution instance"""
    instance_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    step_history: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    triggered_by: str = "system"
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StepExecution:
    """Individual step execution record"""
    step_id: str
    instance_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class WorkflowEngine:
    """
    Enterprise workflow engine for business process automation,
    decision workflows, and multi-step task orchestration
    """
    
    def __init__(self) -> None:
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.step_functions: Dict[str, Callable] = {}
        self.triggers: Dict[str, Callable] = {}
        self.config_path = Path("./config/workflows")
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Engine state
        self.is_running = False
        self.engine_task: Optional[asyncio.Task] = None
        self.max_concurrent_instances = 50
        
        # Register built-in step functions
        self._register_builtin_functions()
        
        logger.info("WorkflowEngine initialized")
    
    async def initialize_engine(self) -> bool:
        """Initialize workflow engine"""
        try:
            logger.info("Initializing workflow engine...")
            
            # Load existing workflows
            await self._load_workflow_definitions()
            
            # Start engine
            await self.start_engine()
            
            logger.info("Workflow engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow engine: {e}")
            return False
    
    async def register_step_function(self, name: str, function: Callable) -> bool:
        """Register a step execution function"""
        try:
            logger.info(f"Registering step function: {name}")
            
            if not callable(function):
                raise ValueError(f"Function {name} is not callable")
            
            self.step_functions[name] = function
            logger.info(f"Step function {name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register step function {name}: {e}")
            return False
    
    async def create_workflow(self, definition: WorkflowDefinition) -> bool:
        """Create a new workflow definition"""
        try:
            logger.info(f"Creating workflow: {definition.name}")
            
            # Validate workflow definition
            if not self._validate_workflow_definition(definition):
                logger.error(f"Invalid workflow definition: {definition.name}")
                return False
            
            # Check for naming conflicts
            if definition.id in self.workflows:
                logger.error(f"Workflow {definition.id} already exists")
                return False
            
            # Set start step if not specified
            if not definition.start_step_id and definition.steps:
                definition.start_step_id = definition.steps[0].id
            
            # Store workflow definition
            self.workflows[definition.id] = definition
            
            # Save configuration
            await self._save_workflow_config(definition)
            
            logger.info(f"Workflow {definition.name} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create workflow {definition.name}: {e}")
            return False
    
    async def start_workflow(self, workflow_id: str, input_variables: Optional[Dict[str, Any]] = None, triggered_by: str = "system") -> str:
        """Start a new workflow instance"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow_def = self.workflows[workflow_id]
            
            # Check concurrent instance limit
            active_instances = len([
                inst for inst in self.instances.values()
                if inst.workflow_id == workflow_id and inst.status in [WorkflowStatus.RUNNING, WorkflowStatus.ACTIVE]
            ])
            
            if active_instances >= workflow_def.max_concurrent_instances:
                raise Exception(f"Maximum concurrent instances ({workflow_def.max_concurrent_instances}) reached for workflow {workflow_id}")
            
            # Create instance
            instance_id = f"{workflow_id}_{uuid.uuid4().hex[:8]}"
            
            # Initialize variables
            instance_variables = {}
            for var in workflow_def.variables:
                instance_variables[var.name] = var.value
            
            # Override with input variables
            if input_variables:
                instance_variables.update(input_variables)
            
            # Create workflow instance
            instance = WorkflowInstance(
                instance_id=instance_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING,
                current_step_id=workflow_def.start_step_id,
                start_time=datetime.now(timezone.utc),
                variables=instance_variables,
                triggered_by=triggered_by
            )
            
            self.instances[instance_id] = instance
            
            logger.info(f"Started workflow instance: {instance_id} (workflow: {workflow_def.name})")
            
            # Start execution
            asyncio.create_task(self._execute_workflow_instance(instance))
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_id}: {e}")
            raise
    
    async def pause_workflow(self, instance_id: str) -> bool:
        """Pause a running workflow instance"""
        try:
            if instance_id not in self.instances:
                raise ValueError(f"Workflow instance {instance_id} not found")
            
            instance = self.instances[instance_id]
            
            if instance.status != WorkflowStatus.RUNNING:
                logger.warning(f"Workflow instance {instance_id} is not running")
                return False
            
            instance.status = WorkflowStatus.PAUSED
            logger.info(f"Workflow instance {instance_id} paused")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause workflow {instance_id}: {e}")
            return False
    
    async def resume_workflow(self, instance_id: str) -> bool:
        """Resume a paused workflow instance"""
        try:
            if instance_id not in self.instances:
                raise ValueError(f"Workflow instance {instance_id} not found")
            
            instance = self.instances[instance_id]
            
            if instance.status != WorkflowStatus.PAUSED:
                logger.warning(f"Workflow instance {instance_id} is not paused")
                return False
            
            instance.status = WorkflowStatus.RUNNING
            logger.info(f"Workflow instance {instance_id} resumed")
            
            # Continue execution
            asyncio.create_task(self._execute_workflow_instance(instance))
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume workflow {instance_id}: {e}")
            return False
    
    async def cancel_workflow(self, instance_id: str) -> bool:
        """Cancel a workflow instance"""
        try:
            if instance_id not in self.instances:
                raise ValueError(f"Workflow instance {instance_id} not found")
            
            instance = self.instances[instance_id]
            
            if instance.status in [WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED]:
                logger.warning(f"Workflow instance {instance_id} is already completed or cancelled")
                return False
            
            instance.status = WorkflowStatus.CANCELLED
            instance.end_time = datetime.now(timezone.utc)
            
            logger.info(f"Workflow instance {instance_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {instance_id}: {e}")
            return False
    
    async def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """Get status information for a workflow instance"""
        try:
            if instance_id not in self.instances:
                return {'error': 'Workflow instance not found'}
            
            instance = self.instances[instance_id]
            workflow_def = self.workflows.get(instance.workflow_id)
            
            duration = None
            if instance.end_time:
                duration = (instance.end_time - instance.start_time).total_seconds()
            else:
                duration = (datetime.now(timezone.utc) - instance.start_time).total_seconds()
            
            current_step = None
            if instance.current_step_id and workflow_def:
                current_step = next(
                    (step for step in workflow_def.steps if step.id == instance.current_step_id),
                    None
                )
            
            return {
                'instance_id': instance_id,
                'workflow_id': instance.workflow_id,
                'workflow_name': workflow_def.name if workflow_def else 'Unknown',
                'status': instance.status.value,
                'current_step': {
                    'id': instance.current_step_id,
                    'name': current_step.name if current_step else None,
                    'type': current_step.step_type.value if current_step else None
                } if current_step else None,
                'start_time': instance.start_time.isoformat(),
                'end_time': instance.end_time.isoformat() if instance.end_time else None,
                'duration_seconds': round(duration, 2),
                'steps_completed': len(instance.step_history),
                'variables': instance.variables,
                'error_message': instance.error_message,
                'triggered_by': instance.triggered_by,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status for {instance_id}: {e}")
            return {'error': str(e)}
    
    async def get_engine_metrics(self) -> Dict[str, Any]:
        """Get comprehensive workflow engine metrics"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Calculate metrics
            total_workflows = len(self.workflows)
            total_instances = len(self.instances)
            
            # Instance status counts
            status_counts = {}
            for status in WorkflowStatus:
                status_counts[status.value] = len([
                    inst for inst in self.instances.values()
                    if inst.status == status
                ])
            
            # Recent execution metrics
            time_window = timedelta(hours=24)
            recent_instances = [
                inst for inst in self.instances.values()
                if current_time - inst.start_time <= time_window
            ]
            
            completed_recent = len([
                inst for inst in recent_instances
                if inst.status == WorkflowStatus.COMPLETED
            ])
            
            failed_recent = len([
                inst for inst in recent_instances
                if inst.status == WorkflowStatus.FAILED
            ])
            
            success_rate = (completed_recent / len(recent_instances) * 100) if recent_instances else 0
            
            # Average execution time
            completed_instances = [
                inst for inst in recent_instances
                if inst.status == WorkflowStatus.COMPLETED and inst.end_time
            ]
            
            avg_execution_time = 0
            if completed_instances:
                execution_times = [
                    (inst.end_time - inst.start_time).total_seconds()
                    for inst in completed_instances
                ]
                avg_execution_time = sum(execution_times) / len(execution_times)
            
            return {
                'engine_status': 'running' if self.is_running else 'stopped',
                'total_workflows': total_workflows,
                'total_instances': total_instances,
                'max_concurrent_instances': self.max_concurrent_instances,
                'instance_status_counts': status_counts,
                'recent_metrics': {
                    'total_executions': len(recent_instances),
                    'completed_executions': completed_recent,
                    'failed_executions': failed_recent,
                    'success_rate': round(success_rate, 2),
                    'average_execution_time': round(avg_execution_time, 2)
                },
                'registered_functions': len(self.step_functions),
                'registered_triggers': len(self.triggers),
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get engine metrics: {e}")
            return {'error': str(e)}
    
    async def start_engine(self) -> bool:
        """Start the workflow engine"""
        try:
            if self.is_running:
                logger.warning("Workflow engine is already running")
                return True
            
            logger.info("Starting workflow engine...")
            self.is_running = True
            
            # Start engine loop
            self.engine_task = asyncio.create_task(self._engine_loop())
            
            logger.info("Workflow engine started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start workflow engine: {e}")
            return False
    
    async def stop_engine(self) -> bool:
        """Stop the workflow engine"""
        try:
            logger.info("Stopping workflow engine...")
            
            self.is_running = False
            
            # Cancel engine loop
            if self.engine_task:
                self.engine_task.cancel()
                try:
                    await self.engine_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Workflow engine stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop workflow engine: {e}")
            return False
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    async def _engine_loop(self) -> None:
        """Main engine loop for monitoring workflows"""
        logger.info("Workflow engine loop started")
        
        while self.is_running:
            try:
                # Check for timed out workflows
                current_time = datetime.now(timezone.utc)
                
                for instance in list(self.instances.values()):
                    if instance.status == WorkflowStatus.RUNNING:
                        workflow_def = self.workflows.get(instance.workflow_id)
                        if workflow_def:
                            timeout_duration = timedelta(minutes=workflow_def.timeout_minutes)
                            if current_time - instance.start_time > timeout_duration:
                                logger.warning(f"Workflow instance {instance.instance_id} timed out")
                                instance.status = WorkflowStatus.FAILED
                                instance.error_message = "Workflow timed out"
                                instance.end_time = current_time
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in workflow engine loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _execute_workflow_instance(self, instance -> None: WorkflowInstance) -> None:
        """Execute a workflow instance"""
        try:
            logger.info(f"Executing workflow instance: {instance.instance_id}")
            
            workflow_def = self.workflows[instance.workflow_id]
            
            while (instance.status == WorkflowStatus.RUNNING and 
                   instance.current_step_id):
                
                # Find current step
                current_step = next(
                    (step for step in workflow_def.steps if step.id == instance.current_step_id),
                    None
                )
                
                if not current_step:
                    raise Exception(f"Step {instance.current_step_id} not found in workflow")
                
                # Execute step
                step_result = await self._execute_workflow_step(instance, current_step)
                
                # Record step execution
                instance.step_history.append({
                    'step_id': current_step.id,
                    'step_name': current_step.name,
                    'executed_at': datetime.now(timezone.utc).isoformat(),
                    'result': step_result,
                    'status': 'completed' if step_result.get('success') else 'failed'
                })
                
                if not step_result.get('success'):
                    # Step failed
                    if current_step.error_step_id:
                        instance.current_step_id = current_step.error_step_id
                    else:
                        instance.status = WorkflowStatus.FAILED
                        instance.error_message = step_result.get('error', 'Step execution failed')
                        break
                else:
                    # Step succeeded, determine next step
                    next_step_id = self._determine_next_step(current_step, step_result, instance)
                    
                    if next_step_id:
                        instance.current_step_id = next_step_id
                    else:
                        # Workflow completed
                        instance.status = WorkflowStatus.COMPLETED
                        instance.current_step_id = None
                        break
            
            # Set end time
            if instance.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                instance.end_time = datetime.now(timezone.utc)
            
            logger.info(f"Workflow instance execution completed: {instance.instance_id} (status: {instance.status.value})")
            
        except Exception as e:
            logger.error(f"Workflow instance execution failed: {instance.instance_id} - {e}")
            instance.status = WorkflowStatus.FAILED
            instance.error_message = str(e)
            instance.end_time = datetime.now(timezone.utc)
    
    async def _execute_workflow_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            logger.debug(f"Executing step: {step.name} (type: {step.step_type.value})")
            
            if step.step_type == StepType.TASK:
                return await self._execute_task_step(instance, step)
            elif step.step_type == StepType.DECISION:
                return await self._execute_decision_step(instance, step)
            elif step.step_type == StepType.WAIT:
                return await self._execute_wait_step(instance, step)
            elif step.step_type == StepType.PARALLEL:
                return await self._execute_parallel_step(instance, step)
            else:
                return await self._execute_generic_step(instance, step)
                
        except Exception as e:
            logger.error(f"Step execution failed: {step.name} - {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_task_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a task step"""
        try:
            if not step.function_name:
                raise ValueError("Task step requires function_name")
            
            step_function = self.step_functions.get(step.function_name)
            if not step_function:
                raise ValueError(f"Step function {step.function_name} not found")
            
            # Prepare parameters
            parameters = {**step.parameters}
            parameters['workflow_variables'] = instance.variables
            parameters['instance_id'] = instance.instance_id
            
            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    step_function(**parameters),
                    timeout=step.timeout_seconds
                )
                
                # Update instance variables if result contains variables
                if isinstance(result, dict) and 'variables' in result:
                    instance.variables.update(result['variables'])
                
                return {'success': True, 'result': result}
                
            except asyncio.TimeoutError:
                raise Exception(f"Step timed out after {step.timeout_seconds} seconds")
                
        except Exception as e:
            logger.error(f"Task step execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_decision_step(self, instance: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a decision step"""
        try:
            # Evaluate conditions
            for condition in step.conditions:
                if self._evaluate_condition(condition, instance.variables):
                    return {
                        'success': True,
                        'next_step_id': condition.next_step_id,
                        'condition_matched': condition.field
                    }
            
            # No condition matched, use default next step
            return {'success': True, 'next_step_id': step.next_step_id}
            
        except Exception as e:
            logger.error(f"Decision step execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _evaluate_condition(self, condition: Condition, variables: Dict[str, Any]) -> bool:
        """Evaluate a condition against workflow variables"""
        try:
            field_value = variables.get(condition.field)
            
            if condition.operator == ConditionOperator.EQUALS:
                return field_value == condition.value
            elif condition.operator == ConditionOperator.NOT_EQUALS:
                return field_value != condition.value
            elif condition.operator == ConditionOperator.GREATER_THAN:
                return field_value > condition.value
            elif condition.operator == ConditionOperator.LESS_THAN:
                return field_value < condition.value
            elif condition.operator == ConditionOperator.CONTAINS:
                return condition.value in str(field_value)
            elif condition.operator == ConditionOperator.EXISTS:
                return condition.field in variables
            else:
                logger.warning(f"Unsupported condition operator: {condition.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _determine_next_step(self, current_step: WorkflowStep, step_result: Dict[str, Any], instance: WorkflowInstance) -> Optional[str]:
        """Determine the next step based on current step and result"""
        # Check if step result specifies next step
        if 'next_step_id' in step_result:
            return step_result['next_step_id']
        
        # Use default next step
        return current_step.next_step_id
    
    def _validate_workflow_definition(self, definition: WorkflowDefinition) -> bool:
        """Validate workflow definition"""
        if not definition.id or not definition.name:
            return False
        if not definition.steps:
            return False
        
        # Validate step references
        step_ids = {step.id for step in definition.steps}
        for step in definition.steps:
            if step.next_step_id and step.next_step_id not in step_ids:
                logger.error(f"Invalid next_step_id reference: {step.next_step_id}")
                return False
            if step.error_step_id and step.error_step_id not in step_ids:
                logger.error(f"Invalid error_step_id reference: {step.error_step_id}")
                return False
        
        return True
    
    def _register_builtin_functions(self) -> None:
        """Register built-in step functions"""
        self.step_functions.update({
            'log_message': self._step_log_message,
            'set_variable': self._step_set_variable,
            'http_request': self._step_http_request,
            'delay': self._step_delay,
            'send_email': self._step_send_email
        })
    
    # Built-in step functions
    async def _step_log_message(self, message: str, level: str = "info", **kwargs) -> Dict[str, Any]:
        """Built-in log message step"""
        logger.log(getattr(logging, level.upper(), logging.INFO), message)
        return {'success': True, 'message_logged': message}
    
    async def _step_set_variable(self, variable_name: str, variable_value: Any, **kwargs) -> Dict[str, Any]:
        """Built-in set variable step"""
        return {
            'success': True,
            'variables': {variable_name: variable_value}
        }
    
    async def _step_http_request(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Built-in HTTP request step"""
        await asyncio.sleep(0.5)  # Simulate HTTP request
        return {'success': True, 'status_code': 200, 'response': 'Mock response'}
    
    async def _step_delay(self, seconds: int = 1, **kwargs) -> Dict[str, Any]:
        """Built-in delay step"""
        await asyncio.sleep(seconds)
        return {'success': True, 'delayed_seconds': seconds}
    
    async def _step_send_email(self, to: str, subject: str, body: str, **kwargs) -> Dict[str, Any]:
        """Built-in send email step"""
        await asyncio.sleep(1)  # Simulate email sending
        return {'success': True, 'email_sent': True, 'recipient': to}

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def example_workflow_engine() -> None:
    """Example usage of WorkflowEngine"""
    try:
        # Initialize engine
        engine = WorkflowEngine()
        await engine.initialize_engine()
        
        # Register custom step function
        async def process_content(**kwargs) -> None:
            content_id = kwargs.get('content_id')
            await asyncio.sleep(2)  # Simulate processing
            return {
                'success': True,
                'variables': {
                    'processed_content_id': content_id,
                    'processing_complete': True,
                    'quality_score': 92.5
                }
            }
        
        await engine.register_step_function('process_content', process_content)
        
        # Create workflow steps
        start_step = WorkflowStep(
            id="start",
            name="Start Processing",
            step_type=StepType.TASK,
            function_name="log_message",
            parameters={"message": "Starting content processing workflow"},
            next_step_id="process"
        )
        
        process_step = WorkflowStep(
            id="process",
            name="Process Content",
            step_type=StepType.TASK,
            function_name="process_content",
            parameters={"content_id": "content_123"},
            next_step_id="decision"
        )
        
        decision_step = WorkflowStep(
            id="decision",
            name="Quality Check",
            step_type=StepType.DECISION,
            conditions=[
                Condition(
                    field="quality_score",
                    operator=ConditionOperator.GREATER_THAN,
                    value=90.0,
                    next_step_id="approve"
                )
            ],
            next_step_id="reject"
        )
        
        approve_step = WorkflowStep(
            id="approve",
            name="Approve Content",
            step_type=StepType.TASK,
            function_name="log_message",
            parameters={"message": "Content approved - high quality"},
            next_step_id=None
        )
        
        reject_step = WorkflowStep(
            id="reject",
            name="Reject Content",
            step_type=StepType.TASK,
            function_name="log_message",
            parameters={"message": "Content rejected - low quality"},
            next_step_id=None
        )
        
        # Create workflow definition
        workflow_def = WorkflowDefinition(
            id="content_processing_workflow",
            name="Content Processing Workflow",
            version="1.0",
            description="Automated content processing and quality check",
            steps=[start_step, process_step, decision_step, approve_step, reject_step],
            variables=[
                WorkflowVariable(name="content_id", value="", is_input=True),
                WorkflowVariable(name="quality_score", value=0.0, is_output=True)
            ],
            start_step_id="start",
            timeout_minutes=30
        )
        
        # Create workflow
        await engine.create_workflow(workflow_def)
        
        # Start workflow instance
        instance_id = await engine.start_workflow(
            "content_processing_workflow",
            input_variables={"content_id": "test_content_456"},
            triggered_by="api_user"
        )
        
        # Wait for execution
        await asyncio.sleep(5)
        
        # Get workflow status
        status = await engine.get_workflow_status(instance_id)
        logger.info(f"Workflow status: {json.dumps(status, indent=2)}")
        
        # Get engine metrics
        metrics = await engine.get_engine_metrics()
        logger.info(f"Engine metrics: {json.dumps(metrics, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Example workflow engine failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(example_workflow_engine())