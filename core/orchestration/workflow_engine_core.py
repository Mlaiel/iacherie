"""Ainflue Core Workflow Engine - Enterprise Business Process Automation
====================================================================

Advanced workflow engine providing business process orchestration, state machines,
task automation, conditional logic, parallel processing, and workflow monitoring
for the Ainflue platform orchestration core.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class TaskType(str, Enum):
    """Task types"""
    HUMAN = "human"
    AUTOMATED = "automated"
    API_CALL = "api_call"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    WAIT = "wait"
    WEBHOOK = "webhook"
    EMAIL = "email"
    NOTIFICATION = "notification"

class TriggerType(str, Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    API = "api"
    WEBHOOK = "webhook"

@dataclass
class TaskCondition:
    """Task execution condition"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, contains
    value: Any
    logic: str = "and"  # and, or

@dataclass
class TaskConfig:
    """Task configuration"""
    task_id: str
    name: str
    task_type: TaskType
    handler: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    conditions: List[TaskCondition] = field(default_factory=list)
    timeout: int = 300  # 5 minutes
    retries: int = 3
    retry_delay: int = 60  # 1 minute
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskInstance:
    """Running task instance"""
    instance_id: str
    task_id: str
    workflow_instance_id: str
    status: TaskStatus
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    assigned_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str
    tasks: List[TaskConfig]
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowInstance:
    """Running workflow instance"""
    instance_id: str
    workflow_id: str
    status: WorkflowStatus
    variables: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    task_instances: Dict[str, TaskInstance] = field(default_factory=dict)
    current_tasks: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    started_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowMetrics:
    """Workflow engine metrics"""
    workflows_created: int = 0
    instances_started: int = 0
    instances_completed: int = 0
    instances_failed: int = 0
    tasks_executed: int = 0
    tasks_failed: int = 0
    avg_execution_time: float = 0.0
    active_instances: int = 0
    pending_tasks: int = 0
    uptime_seconds: int = 0
    last_health_check: float = field(default_factory=time.time)

class WorkflowEngineCore:
    """Enterprise workflow engine core management system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize workflow engine core"""
        self.level = level
        self.metrics = WorkflowMetrics()
        self.start_time = time.time()
        
        # Workflow management
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.workflow_instances: Dict[str, WorkflowInstance] = {}
        self.task_handlers: Dict[str, Callable] = {}
        
        # Execution queues
        self.task_queue: List[Tuple[str, str]] = []  # (instance_id, task_id)
        self.retry_queue: List[Dict[str, Any]] = []
        self.scheduled_tasks: List[Dict[str, Any]] = []
        
        # Event system
        self.event_listeners: Dict[str, List[Callable]] = {}
        self.workflow_events: List[Dict[str, Any]] = []
        
        # Background processing
        self._execution_tasks: List[asyncio.Task] = []
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("⚙️ Workflow Engine Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize workflow engine"""
        try:
            logger.info("🚀 Initializing workflow engine core")
            
            # Register default task handlers
            self._register_default_handlers()
            
            # Create sample workflows
            await self._create_sample_workflows()
            
            logger.info("✅ Workflow engine core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow engine initialization failed: {str(e)}")
            return False
    
    def _register_default_handlers(self) -> None:
        """Register default task handlers"""
        self.task_handlers = {
            "log": self._handle_log_task,
            "delay": self._handle_delay_task,
            "http_request": self._handle_http_request_task,
            "email": self._handle_email_task,
            "condition": self._handle_condition_task,
            "transformation": self._handle_transformation_task,
            "notification": self._handle_notification_task
        }
    
    async def _create_sample_workflows(self) -> None:
        """Create sample workflow definitions"""
        # Content approval workflow
        content_approval_tasks = [
            TaskConfig(
                task_id="submit_content",
                name="Submit Content for Review",
                task_type=TaskType.HUMAN,
                inputs={"content_id": "", "creator_id": ""},
                outputs={"status": "submitted"}
            ),
            TaskConfig(
                task_id="review_content",
                name="Review Content",
                task_type=TaskType.HUMAN,
                dependencies=["submit_content"],
                inputs={"content_id": "", "reviewer_id": ""},
                outputs={"approved": "boolean", "feedback": "string"}
            ),
            TaskConfig(
                task_id="publish_content",
                name="Publish Content",
                task_type=TaskType.AUTOMATED,
                handler="publish_content",
                dependencies=["review_content"],
                conditions=[
                    TaskCondition(field="approved", operator="eq", value=True)
                ]
            ),
            TaskConfig(
                task_id="notify_rejection",
                name="Notify Content Rejection",
                task_type=TaskType.NOTIFICATION,
                handler="notification",
                dependencies=["review_content"],
                conditions=[
                    TaskCondition(field="approved", operator="eq", value=False)
                ]
            )
        ]
        
        content_approval_workflow = WorkflowDefinition(
            workflow_id="content_approval",
            name="Content Approval Process",
            description="Workflow for content review and approval",
            version="1.0",
            tasks=content_approval_tasks,
            triggers=[
                {"type": "event", "event": "content_submitted"},
                {"type": "api", "endpoint": "/workflows/content-approval/start"}
            ]
        )
        
        # Creator onboarding workflow
        onboarding_tasks = [
            TaskConfig(
                task_id="collect_profile",
                name="Collect Profile Information",
                task_type=TaskType.HUMAN,
                outputs={"profile_complete": "boolean"}
            ),
            TaskConfig(
                task_id="verify_identity",
                name="Verify Identity",
                task_type=TaskType.AUTOMATED,
                handler="verify_identity",
                dependencies=["collect_profile"],
                timeout=600
            ),
            TaskConfig(
                task_id="setup_payment",
                name="Setup Payment Method",
                task_type=TaskType.HUMAN,
                dependencies=["verify_identity"],
                outputs={"payment_setup": "boolean"}
            ),
            TaskConfig(
                task_id="welcome_email",
                name="Send Welcome Email",
                task_type=TaskType.EMAIL,
                handler="email",
                dependencies=["setup_payment"]
            ),
            TaskConfig(
                task_id="activate_account",
                name="Activate Account",
                task_type=TaskType.AUTOMATED,
                handler="activate_account",
                dependencies=["welcome_email"]
            )
        ]
        
        onboarding_workflow = WorkflowDefinition(
            workflow_id="creator_onboarding",
            name="Creator Onboarding Process",
            description="Complete onboarding flow for new creators",
            version="1.0",
            tasks=onboarding_tasks,
            triggers=[
                {"type": "event", "event": "creator_registered"}
            ]
        )
        
        # Store workflows
        self.workflow_definitions["content_approval"] = content_approval_workflow
        self.workflow_definitions["creator_onboarding"] = onboarding_workflow
        self.metrics.workflows_created += 2
    
    async def start(self) -> bool:
        """Start workflow engine"""
        try:
            if not hasattr(self, '_initialized'):
                await self.initialize()
                self._initialized = True
            
            # Start execution workers
            num_workers = 3
            for i in range(num_workers):
                task = asyncio.create_task(self._execution_worker(f"worker_{i}"))
                self._execution_tasks.append(task)
            
            # Start health monitoring
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            
            # Start scheduler
            scheduler_task = asyncio.create_task(self._scheduler_loop())
            self._execution_tasks.append(scheduler_task)
            
            logger.info("🚀 Workflow engine core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow engine start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop workflow engine"""
        try:
            logger.info("🛑 Stopping workflow engine core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel all tasks
            all_tasks = self._execution_tasks + [self._health_monitor_task]
            for task in all_tasks:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("✅ Workflow engine core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow engine stop failed: {str(e)}")
            return False
    
    async def create_workflow(self, definition: WorkflowDefinition) -> bool:
        """Create new workflow definition"""
        try:
            self.workflow_definitions[definition.workflow_id] = definition
            self.metrics.workflows_created += 1
            
            logger.info(f"📋 Created workflow '{definition.workflow_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Workflow creation failed: {str(e)}")
            return False
    
    async def start_workflow(self, workflow_id: str, inputs: Optional[Dict[str, Any]] = None, 
                           started_by: str = "") -> Optional[str]:
        """Start workflow instance"""
        try:
            if workflow_id not in self.workflow_definitions:
                logger.error(f"Workflow '{workflow_id}' not found")
                return None
            
            definition = self.workflow_definitions[workflow_id]
            instance_id = str(uuid.uuid4())
            
            # Create workflow instance
            instance = WorkflowInstance(
                instance_id=instance_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING,
                variables=definition.variables.copy(),
                context=inputs or {},
                started_by=started_by
            )
            
            # Merge inputs into variables
            if inputs:
                instance.variables.update(inputs)
            
            # Find initial tasks (no dependencies)
            initial_tasks = [
                task for task in definition.tasks
                if not task.dependencies
            ]
            
            # Create task instances for initial tasks
            for task in initial_tasks:
                task_instance = TaskInstance(
                    instance_id=str(uuid.uuid4()),
                    task_id=task.task_id,
                    workflow_instance_id=instance_id,
                    status=TaskStatus.PENDING,
                    inputs=self._resolve_task_inputs(task, instance)
                )
                
                instance.task_instances[task.task_id] = task_instance
                instance.current_tasks.append(task.task_id)
                
                # Add to execution queue
                self.task_queue.append((instance_id, task.task_id))
            
            self.workflow_instances[instance_id] = instance
            self.metrics.instances_started += 1
            self.metrics.active_instances += 1
            
            # Emit workflow started event
            await self._emit_event("workflow_started", {
                "instance_id": instance_id,
                "workflow_id": workflow_id,
                "started_by": started_by
            })
            
            logger.info(f"🚀 Started workflow instance '{instance_id}' for workflow '{workflow_id}'")
            return instance_id
            
        except Exception as e:
            logger.error(f"Workflow start failed: {str(e)}")
            return None
    
    def _resolve_task_inputs(self, task: TaskConfig, instance: WorkflowInstance) -> Dict[str, Any]:
        """Resolve task inputs from workflow variables and context"""
        resolved_inputs = {}
        
        for input_name, input_value in task.inputs.items():
            if isinstance(input_value, str) and input_value.startswith("${"):
                # Variable reference
                var_name = input_value[2:-1]  # Remove ${ and }
                if var_name in instance.variables:
                    resolved_inputs[input_name] = instance.variables[var_name]
                elif var_name in instance.context:
                    resolved_inputs[input_name] = instance.context[var_name]
                else:
                    resolved_inputs[input_name] = input_value
            else:
                resolved_inputs[input_name] = input_value
        
        return resolved_inputs
    
    async def _execution_worker(self, worker_id -> None: str) -> None:
        """Background task execution worker"""
        logger.info(f"Worker {worker_id} started")
        
        while not self._shutdown_event.is_set():
            try:
                if self.task_queue:
                    instance_id, task_id = self.task_queue.pop(0)
                    await self._execute_task(instance_id, task_id)
                else:
                    await asyncio.sleep(1)  # Wait for tasks
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                await asyncio.sleep(5)
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _execute_task(self, instance_id -> None: str, task_id -> None: str) -> None:
        """Execute a single task"""
        try:
            instance = self.workflow_instances.get(instance_id)
            if not instance:
                return
            
            task_instance = instance.task_instances.get(task_id)
            if not task_instance:
                return
            
            definition = self.workflow_definitions.get(instance.workflow_id)
            if not definition:
                return
            
            task_config = next((t for t in definition.tasks if t.task_id == task_id), None)
            if not task_config:
                return
            
            # Check conditions
            if not self._check_task_conditions(task_config, instance):
                task_instance.status = TaskStatus.SKIPPED
                await self._complete_task(instance_id, task_id)
                return
            
            # Update status
            task_instance.status = TaskStatus.RUNNING
            task_instance.started_at = datetime.utcnow()
            
            logger.info(f"🔄 Executing task '{task_id}' in instance '{instance_id}'")
            
            # Execute task based on type
            try:
                if task_config.task_type == TaskType.AUTOMATED:
                    await self._execute_automated_task(task_config, task_instance, instance)
                elif task_config.task_type == TaskType.HUMAN:
                    await self._execute_human_task(task_config, task_instance, instance)
                elif task_config.task_type == TaskType.WAIT:
                    await self._execute_wait_task(task_config, task_instance, instance)
                else:
                    # Use handler if available
                    if task_config.handler and task_config.handler in self.task_handlers:
                        handler = self.task_handlers[task_config.handler]
                        result = await handler(task_config, task_instance, instance)
                        task_instance.outputs.update(result or {})
                    
                    task_instance.status = TaskStatus.COMPLETED
                
                task_instance.completed_at = datetime.utcnow()
                self.metrics.tasks_executed += 1
                
                # Update workflow variables with task outputs
                if task_config.outputs:
                    for output_name, variable_name in task_config.outputs.items():
                        if output_name in task_instance.outputs:
                            instance.variables[variable_name] = task_instance.outputs[output_name]
                
                await self._complete_task(instance_id, task_id)
                
            except Exception as e:
                # Task failed
                task_instance.status = TaskStatus.FAILED
                task_instance.error_message = str(e)
                task_instance.completed_at = datetime.utcnow()
                self.metrics.tasks_failed += 1
                
                # Retry logic
                if task_instance.retry_count < task_config.retries:
                    task_instance.retry_count += 1
                    task_instance.status = TaskStatus.RETRYING
                    
                    # Schedule retry
                    retry_at = time.time() + task_config.retry_delay
                    self.retry_queue.append({
                        "instance_id": instance_id,
                        "task_id": task_id,
                        "retry_at": retry_at
                    })
                    
                    logger.info(f"🔄 Scheduled retry {task_instance.retry_count} for task '{task_id}'")
                else:
                    # Mark task as failed
                    instance.failed_tasks.append(task_id)
                    await self._handle_task_failure(instance_id, task_id)
                
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
    
    def _check_task_conditions(self, task_config: TaskConfig, instance: WorkflowInstance) -> bool:
        """Check if task conditions are met"""
        if not task_config.conditions:
            return True
        
        for condition in task_config.conditions:
            field_value = instance.variables.get(condition.field)
            
            # Evaluate condition
            condition_met = False
            if condition.operator == "eq":
                condition_met = field_value == condition.value
            elif condition.operator == "ne":
                condition_met = field_value != condition.value
            elif condition.operator == "gt":
                condition_met = field_value > condition.value
            elif condition.operator == "lt":
                condition_met = field_value < condition.value
            elif condition.operator == "gte":
                condition_met = field_value >= condition.value
            elif condition.operator == "lte":
                condition_met = field_value <= condition.value
            elif condition.operator == "contains":
                condition_met = condition.value in str(field_value)
            
            # Handle logic (simplified - only AND for now)
            if condition.logic == "and" and not condition_met:
                return False
        
        return True
    
    async def _execute_automated_task(self, task_config -> None: TaskConfig, task_instance -> None: TaskInstance, instance -> None: WorkflowInstance) -> None:
        """Execute automated task"""
        # Simulate automated task execution
        await asyncio.sleep(0.1)
        
        task_instance.outputs = {
            "execution_time": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        task_instance.status = TaskStatus.COMPLETED
    
    async def _execute_human_task(self, task_config -> None: TaskConfig, task_instance -> None: TaskInstance, instance -> None: WorkflowInstance) -> None:
        """Execute human task (mark as pending user action)"""
        task_instance.status = TaskStatus.PENDING
        # Human tasks require manual completion via API
    
    async def _execute_wait_task(self, task_config -> None: TaskConfig, task_instance -> None: TaskInstance, instance -> None: WorkflowInstance) -> None:
        """Execute wait task"""
        wait_seconds = task_config.inputs.get("seconds", 1)
        await asyncio.sleep(wait_seconds)
        
        task_instance.outputs = {"waited_seconds": wait_seconds}
        task_instance.status = TaskStatus.COMPLETED
    
    async def _complete_task(self, instance_id -> None: str, task_id -> None: str) -> None:
        """Complete task and trigger next tasks"""
        instance = self.workflow_instances.get(instance_id)
        if not instance:
            return
        
        definition = self.workflow_definitions.get(instance.workflow_id)
        if not definition:
            return
        
        # Remove from current tasks
        if task_id in instance.current_tasks:
            instance.current_tasks.remove(task_id)
        
        # Add to completed tasks
        if task_id not in instance.completed_tasks:
            instance.completed_tasks.append(task_id)
        
        # Find next tasks
        next_tasks = [
            task for task in definition.tasks
            if task_id in task.dependencies and 
            task.task_id not in instance.completed_tasks and
            task.task_id not in instance.failed_tasks and
            all(dep in instance.completed_tasks for dep in task.dependencies)
        ]
        
        # Start next tasks
        for task in next_tasks:
            task_instance = TaskInstance(
                instance_id=str(uuid.uuid4()),
                task_id=task.task_id,
                workflow_instance_id=instance_id,
                status=TaskStatus.PENDING,
                inputs=self._resolve_task_inputs(task, instance)
            )
            
            instance.task_instances[task.task_id] = task_instance
            instance.current_tasks.append(task.task_id)
            self.task_queue.append((instance_id, task.task_id))
        
        # Check if workflow is complete
        if not instance.current_tasks and not any(
            task.task_id not in instance.completed_tasks + instance.failed_tasks
            for task in definition.tasks
        ):
            await self._complete_workflow(instance_id)
    
    async def _complete_workflow(self, instance_id -> None: str) -> None:
        """Complete workflow instance"""
        instance = self.workflow_instances.get(instance_id)
        if not instance:
            return
        
        if instance.failed_tasks:
            instance.status = WorkflowStatus.FAILED
            self.metrics.instances_failed += 1
        else:
            instance.status = WorkflowStatus.COMPLETED
            self.metrics.instances_completed += 1
        
        instance.completed_at = datetime.utcnow()
        self.metrics.active_instances -= 1
        
        # Calculate execution time
        if instance.started_at:
            execution_time = (instance.completed_at - instance.started_at).total_seconds()
            total_instances = self.metrics.instances_completed + self.metrics.instances_failed
            self.metrics.avg_execution_time = (
                (self.metrics.avg_execution_time * (total_instances - 1) + execution_time) /
                total_instances
            )
        
        # Emit workflow completed event
        await self._emit_event("workflow_completed", {
            "instance_id": instance_id,
            "status": instance.status.value,
            "execution_time": execution_time if instance.started_at else 0
        })
        
        logger.info(f"✅ Workflow instance '{instance_id}' {instance.status.value}")
    
    async def _handle_task_failure(self, instance_id -> None: str, task_id -> None: str) -> None:
        """Handle task failure"""
        instance = self.workflow_instances.get(instance_id)
        if not instance:
            return
        
        # Remove from current tasks
        if task_id in instance.current_tasks:
            instance.current_tasks.remove(task_id)
        
        # Check if there are any remaining tasks that can run
        definition = self.workflow_definitions.get(instance.workflow_id)
        if definition:
            runnable_tasks = [
                task for task in definition.tasks
                if (task.task_id not in instance.completed_tasks and 
                    task.task_id not in instance.failed_tasks and
                    all(dep in instance.completed_tasks for dep in task.dependencies))
            ]
            
            if not runnable_tasks:
                # No more tasks can run, workflow failed
                await self._complete_workflow(instance_id)
    
    # Task handlers
    async def _handle_log_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle log task"""
        message = task_instance.inputs.get("message", "Log message")
        logger.info(f"📝 Workflow log: {message}")
        return {"logged": True, "message": message}
    
    async def _handle_delay_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle delay task"""
        seconds = task_instance.inputs.get("seconds", 1)
        await asyncio.sleep(seconds)
        return {"delayed_seconds": seconds}
    
    async def _handle_http_request_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle HTTP request task"""
        # Simulate HTTP request
        url = task_instance.inputs.get("url", "")
        method = task_instance.inputs.get("method", "GET")
        
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            "status_code": 200,
            "response": {"success": True},
            "url": url,
            "method": method
        }
    
    async def _handle_email_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle email task"""
        to_email = task_instance.inputs.get("to", "")
        subject = task_instance.inputs.get("subject", "")
        
        # Simulate email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"📧 Email sent to {to_email}: {subject}")
        return {"email_sent": True, "to": to_email}
    
    async def _handle_condition_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle conditional task"""
        condition = task_instance.inputs.get("condition", True)
        return {"condition_result": bool(condition)}
    
    async def _handle_transformation_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle data transformation task"""
        data = task_instance.inputs.get("data", {})
        transform_rule = task_instance.inputs.get("transform", "")
        
        # Simple transformation (in real implementation, this would be more sophisticated)
        transformed_data = data.copy()
        if transform_rule == "uppercase":
            for key, value in transformed_data.items():
                if isinstance(value, str):
                    transformed_data[key] = value.upper()
        
        return {"transformed_data": transformed_data}
    
    async def _handle_notification_task(self, task_config: TaskConfig, task_instance: TaskInstance, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle notification task"""
        message = task_instance.inputs.get("message", "")
        recipient = task_instance.inputs.get("recipient", "")
        
        logger.info(f"🔔 Notification to {recipient}: {message}")
        return {"notification_sent": True, "recipient": recipient}
    
    async def _scheduler_loop(self) -> None:
        """Process scheduled tasks and retries"""
        while not self._shutdown_event.is_set():
            try:
                current_time = time.time()
                
                # Process retries
                retry_ready = [
                    retry for retry in self.retry_queue
                    if current_time >= retry["retry_at"]
                ]
                
                for retry in retry_ready:
                    self.task_queue.append((retry["instance_id"], retry["task_id"]))
                    self.retry_queue.remove(retry)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _emit_event(self, event_type -> None: str, data -> None: Dict[str, Any]) -> None:
        """Emit workflow event"""
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow(),
            "event_id": str(uuid.uuid4())
        }
        
        self.workflow_events.append(event)
        
        # Call event listeners
        listeners = self.event_listeners.get(event_type, [])
        for listener in listeners:
            try:
                await listener(event)
            except Exception as e:
                logger.error(f"Event listener error: {str(e)}")
    
    async def complete_human_task(self, instance_id: str, task_id: str, outputs: Dict[str, Any]) -> bool:
        """Complete human task with outputs"""
        try:
            instance = self.workflow_instances.get(instance_id)
            if not instance:
                return False
            
            task_instance = instance.task_instances.get(task_id)
            if not task_instance or task_instance.status != TaskStatus.PENDING:
                return False
            
            task_instance.outputs.update(outputs)
            task_instance.status = TaskStatus.COMPLETED
            task_instance.completed_at = datetime.utcnow()
            
            await self._complete_task(instance_id, task_id)
            
            logger.info(f"✅ Human task '{task_id}' completed in instance '{instance_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Human task completion failed: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Perform workflow engine health check"""
        try:
            # Check if execution workers are responsive
            if len(self.task_queue) > 1000:  # Too many pending tasks
                logger.warning("Workflow engine task queue is too large")
                return False
            
            # Check for stuck instances
            stuck_instances = 0
            for instance in self.workflow_instances.values():
                if (instance.status == WorkflowStatus.RUNNING and 
                    (datetime.utcnow() - instance.started_at).total_seconds() > 3600):  # 1 hour
                    stuck_instances += 1
            
            if stuck_instances > 10:
                logger.warning("Too many stuck workflow instances")
                return False
            
            self.metrics.last_health_check = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Workflow engine health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                self.metrics.pending_tasks = len(self.task_queue)
                self.metrics.uptime_seconds = int(time.time() - self.start_time)
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Workflow health monitor error: {str(e)}")
                await asyncio.sleep(600)
    
    def get_workflow_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow instance status"""
        instance = self.workflow_instances.get(instance_id)
        if not instance:
            return None
        
        return {
            "instance_id": instance_id,
            "workflow_id": instance.workflow_id,
            "status": instance.status.value,
            "started_at": instance.started_at.isoformat(),
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "current_tasks": instance.current_tasks,
            "completed_tasks": instance.completed_tasks,
            "failed_tasks": instance.failed_tasks,
            "variables": instance.variables
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get workflow engine metrics"""
        return {
            "workflows_created": self.metrics.workflows_created,
            "instances_started": self.metrics.instances_started,
            "instances_completed": self.metrics.instances_completed,
            "instances_failed": self.metrics.instances_failed,
            "success_rate": (
                self.metrics.instances_completed / 
                max(self.metrics.instances_started, 1) * 100
            ),
            "tasks_executed": self.metrics.tasks_executed,
            "tasks_failed": self.metrics.tasks_failed,
            "task_success_rate": (
                (self.metrics.tasks_executed - self.metrics.tasks_failed) /
                max(self.metrics.tasks_executed, 1) * 100
            ),
            "avg_execution_time_seconds": self.metrics.avg_execution_time,
            "active_instances": self.metrics.active_instances,
            "pending_tasks": len(self.task_queue),
            "retry_queue_size": len(self.retry_queue),
            "uptime_seconds": int(time.time() - self.start_time)
        }

# Module exports
__all__ = [
    "WorkflowEngineCore", "WorkflowDefinition", "WorkflowInstance", "TaskConfig",
    "TaskInstance", "WorkflowStatus", "TaskStatus", "TaskType", "TriggerType",
    "TaskCondition", "WorkflowMetrics"
]