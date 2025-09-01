"""Workflow Orchestrator - Advanced Multi-Step Notification Workflow Management

Advanced workflow orchestration engine for IA Influencer Agent notification system.
Manages complex multi-step notification workflows, conditional logic, business rules,
automated follow-ups, escalation procedures, and comprehensive workflow analytics.

Key Features:
- Multi-step workflow automation with conditional branching
- Business rule-driven workflow execution and decision making
- Automated follow-up sequences with intelligent timing
- Escalation procedures for critical notifications
- Workflow analytics and performance monitoring
- Dynamic workflow adaptation based on user responses

Workflow Types:
- Content Protection Workflows: Copyright detection → DMCA → Follow-up → Resolution
- Collaboration Workflows: Match → Invitation → Follow-up → Partnership Setup
- Monetization Workflows: Opportunity → Evaluation → Proposal → Revenue Tracking
- SEO Workflows: Analysis → Recommendations → Implementation → Performance Monitoring
- Distribution Workflows: Upload → Processing → Distribution → Performance Tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

LEGAL NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission from the author is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing and usage rights.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

from .notification_models import NotificationRequest, NotificationResponse, NotificationMetrics
from .notification_service import NotificationService
from .config import NotificationConfig
from .constants import WORKFLOW_TEMPLATES, BUSINESS_RULES, ESCALATION_RULES

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """
Workflow execution status."""

    PENDING = "pending"                # Waiting to start
    RUNNING = "running"                # Currently executing
    PAUSED = "paused"                  # Temporarily paused
    WAITING = "waiting"                # Waiting for user response
    COMPLETED = "completed"            # Successfully completed
    FAILED = "failed"                  # Failed with error
    CANCELLED = "cancelled"            # Manually cancelled
    EXPIRED = "expired"                # Expired due to timeout


class WorkflowStepType(Enum):
    """Types of workflow steps."""

    NOTIFICATION = "notification"      # Send notification
    WAIT = "wait"                     # Wait for specified time
    CONDITION = "condition"           # Conditional branching
    ACTION = "action"                 # Execute custom action
    ESCALATION = "escalation"         # Escalate to higher priority
    FOLLOW_UP = "follow_up"           # Send follow-up notification
    COMPLETION = "completion"         # Mark workflow complete


class WorkflowTrigger(Enum):
    """Workflow trigger types."""

    IMMEDIATE = "immediate"            # Execute immediately
    SCHEDULED = "scheduled"            # Execute at specific time
    CONDITIONAL = "conditional"        # Execute when condition met
    USER_ACTION = "user_action"        # Execute on user action
    EXTERNAL_EVENT = "external_event"  # Execute on external trigger


@dataclass
class WorkflowStep:
    """Individual workflow step definition."""
    id: str
    name: str
    type: WorkflowStepType
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    timeout: Optional[int] = None      # Timeout in seconds
    retry_config: Optional[Dict[str, Any]] = None
    on_success: Optional[str] = None   # Next step on success
    on_failure: Optional[str] = None   # Next step on failure
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """
Complete workflow definition."""
    id: str
    name: str
    description: str
    version: str
    category: str
    steps: Dict[str, WorkflowStep]
    entry_point: str                   # First step ID
    triggers: List[WorkflowTrigger]
    business_rules: Dict[str, Any]
    escalation_rules: Dict[str, Any]
    timeout: Optional[int] = None      # Overall workflow timeout
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """
Workflow execution instance."""
    id: str
    workflow_id: str
    user_id: str
    status: WorkflowStatus
    current_step: Optional[str]
    context: Dict[str, Any]
    step_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowMetrics:
    """
Workflow performance metrics."""
    workflow_id: str
    total_executions: int
    successful_completions: int
    failed_executions: int
    average_completion_time: float
    average_step_count: float
    user_response_rate: float
    escalation_rate: float
    completion_rate: float
    performance_score: float


class WorkflowOrchestrator:
    """
    Advanced notification workflow orchestration engine.
    
    Manages complex multi-step workflows with conditional logic,
    business rule integration, and comprehensive performance monitoring.
    """
    
    def __init__(
        self,
        notification_service: NotificationService,
        config: NotificationConfig
    ):
        """
Initialize workflow orchestrator."""
        self.notification_service = notification_service
        self.config = config
        self.business_rules = BUSINESS_RULES
        self.escalation_rules = ESCALATION_RULES
        
        # Workflow definitions
        self._workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self._load_workflow_templates()
        
        # Active workflow executions
        self._active_executions: Dict[str, WorkflowExecution] = {}
        
        # Workflow metrics
        self._workflow_metrics: Dict[str, WorkflowMetrics] = defaultdict(
            lambda: WorkflowMetrics(
                workflow_id="",
                total_executions=0,
                successful_completions=0,
                failed_executions=0,
                average_completion_time=0.0,
                average_step_count=0.0,
                user_response_rate=0.0,
                escalation_rate=0.0,
                completion_rate=0.0,
                performance_score=0.0
            )
        )
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
        # Performance statistics
        self.orchestrator_stats = {
            "total_workflows_executed": 0,
            "active_workflows": 0,
            "average_completion_time": 0.0,
            "success_rate": 0.0,
            "escalation_rate": 0.0
        }
        
        # Start background monitoring
        self._start_background_monitoring()
        
        logger.info("Workflow orchestrator initialized successfully")
    
    async def start_workflow(
        self,
        workflow_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        trigger: WorkflowTrigger = WorkflowTrigger.IMMEDIATE
    ) -> str:
        """
        Start a new workflow execution.
        
        Args:
            workflow_id: ID of the workflow definition to execute
            user_id: Target user ID
            context: Initial workflow context
            trigger: Workflow trigger type
            
        Returns:
            Execution ID of the started workflow
        """
        try:
            # Validate workflow exists
            if workflow_id not in self._workflow_definitions:
                raise ValueError(f"Workflow '{workflow_id}' not found")
            
            workflow_def = self._workflow_definitions[workflow_id]
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                user_id=user_id,
                status=WorkflowStatus.PENDING,
                current_step=None,
                context=context or {},
                metadata={
                    "trigger": trigger.value,
                    "workflow_name": workflow_def.name,
                    "workflow_version": workflow_def.version
                }
            )
            
            # Store execution
            self._active_executions[execution_id] = execution
            
            # Update metrics
            self._workflow_metrics[workflow_id].total_executions += 1
            self.orchestrator_stats["total_workflows_executed"] += 1
            self.orchestrator_stats["active_workflows"] += 1
            
            logger.info(
                f"Started workflow '{workflow_id}' for user '{user_id}' "
                f"(execution: {execution_id})"
            )
            
            # Execute workflow
            if trigger == WorkflowTrigger.IMMEDIATE:
                asyncio.create_task(self._execute_workflow(execution_id))
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow '{workflow_id}': {e}")
            raise
    
    async def _execute_workflow(self, execution_id: str):
        """Execute workflow steps."""
        try:
            execution = self._active_executions.get(execution_id)
            if not execution:
                logger.error(f"Execution '{execution_id}' not found")
                return
            
            workflow_def = self._workflow_definitions[execution.workflow_id]
            execution.status = WorkflowStatus.RUNNING
            execution.current_step = workflow_def.entry_point
            execution.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Executing workflow '{execution.workflow_id}' (execution: {execution_id})")
            
            # Execute steps
            while execution.status == WorkflowStatus.RUNNING and execution.current_step:
                step_id = execution.current_step
                step = workflow_def.steps.get(step_id)
                
                if not step:
                    logger.error(f"Step '{step_id}' not found in workflow")
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = f"Step '{step_id}' not found"
                    break
                
                # Execute step
                step_result = await self._execute_step(execution, step)
                
                # Process step result
                if step_result["success"]:
                    execution.current_step = step_result.get("next_step")
                    
                    if not execution.current_step:
                        # Workflow completed
                        execution.status = WorkflowStatus.COMPLETED
                        execution.completed_at = datetime.now(timezone.utc)
                        logger.info(f"Workflow '{execution.workflow_id}' completed successfully")
                        
                else:
                    # Step failed
                    if step_result.get("retryable", False) and self._should_retry_step(execution, step):
                        logger.warning(f"Retrying step '{step_id}' in workflow '{execution.workflow_id}'")
                        await asyncio.sleep(step_result.get("retry_delay", 60))
                        continue
                    else:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = step_result.get("error", "Step execution failed")
                        logger.error(f"Workflow '{execution.workflow_id}' failed at step '{step_id}'")
                        break
                
                # Check for workflow timeout
                if self._is_workflow_expired(execution, workflow_def):
                    execution.status = WorkflowStatus.EXPIRED
                    execution.error_message = "Workflow execution timeout"
                    logger.warning(f"Workflow '{execution.workflow_id}' expired")
                    break
            
            # Update final metrics
            await self._update_workflow_metrics(execution)
            
            # Cleanup completed workflow
            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.EXPIRED]:
                self.orchestrator_stats["active_workflows"] -= 1
                
                # Keep for a while for monitoring, then cleanup
                asyncio.create_task(self._cleanup_execution(execution_id, delay=3600))
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            if execution_id in self._active_executions:
                execution = self._active_executions[execution_id]
                execution.status = WorkflowStatus.FAILED
                execution.error_message = str(e)
                execution.updated_at = datetime.now(timezone.utc)
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute individual workflow step."""
        try:
            step_start_time = datetime.now(timezone.utc)
            
            logger.debug(f"Executing step '{step.id}' in workflow '{execution.workflow_id}'")
            
            # Check step dependencies
            if not await self._check_step_dependencies(execution, step):
                return {
                    "success": False,
                    "error": "Step dependencies not met",
                    "retryable": True,
                    "retry_delay": 300  # 5 minutes
                }
            
            # Check step conditions
            if not await self._evaluate_step_conditions(execution, step):
                # Skip step, move to next
                next_step = step.on_success or self._get_next_sequential_step(execution, step)
                return {
                    "success": True,
                    "next_step": next_step,
                    "skipped": True
                }
            
            # Execute step based on type
            result = await self._execute_step_by_type(execution, step)
            
            # Record step execution
            step_record = {
                "step_id": step.id,
                "step_name": step.name,
                "step_type": step.type.value,
                "started_at": step_start_time,
                "completed_at": datetime.now(timezone.utc),
                "success": result["success"],
                "result": result
            }
            execution.step_history.append(step_record)
            execution.updated_at = datetime.now(timezone.utc)
            
            return result
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": False
            }
    
    async def _execute_step_by_type(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute step based on its type."""
        try:
            if step.type == WorkflowStepType.NOTIFICATION:
                return await self._execute_notification_step(execution, step)
                
            elif step.type == WorkflowStepType.WAIT:
                return await self._execute_wait_step(execution, step)
                
            elif step.type == WorkflowStepType.CONDITION:
                return await self._execute_condition_step(execution, step)
                
            elif step.type == WorkflowStepType.ACTION:
                return await self._execute_action_step(execution, step)
                
            elif step.type == WorkflowStepType.ESCALATION:
                return await self._execute_escalation_step(execution, step)
                
            elif step.type == WorkflowStepType.FOLLOW_UP:
                return await self._execute_follow_up_step(execution, step)
                
            elif step.type == WorkflowStepType.COMPLETION:
                return await self._execute_completion_step(execution, step)
                
            else:
                return {
                    "success": False,
                    "error": f"Unknown step type: {step.type}",
                    "retryable": False
                }
                
        except Exception as e:
            logger.error(f"Step type execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": True
            }
    
    async def _execute_notification_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute notification step."""
        try:
            config = step.config
            
            # Build notification request
            notification_request = NotificationRequest(
                type=config.get("notification_type", "workflow_step"),
                recipient_id=execution.user_id,
                content=self._build_notification_content(config, execution.context),
                priority=config.get("priority", "medium"),
                channels=config.get("channels", ["email"]),
                metadata={
                    "workflow_id": execution.workflow_id,
                    "execution_id": execution.id,
                    "step_id": step.id,
                    **config.get("metadata", {})
                }
            )
            
            # Send notification
            response = await self.notification_service.send_notification(notification_request)
            
            if response.success:
                # Determine next step
                next_step = step.on_success or self._get_next_sequential_step(execution, step)
                
                # Store notification response in context
                execution.context[f"notification_{step.id}"] = {
                    "notification_id": response.notification_id,
                    "sent_at": response.sent_at.isoformat(),
                    "channels": response.delivery_status
                }
                
                return {
                    "success": True,
                    "next_step": next_step,
                    "notification_id": response.notification_id
                }
            else:
                return {
                    "success": False,
                    "error": response.error_message,
                    "retryable": True,
                    "retry_delay": 120
                }
                
        except Exception as e:
            logger.error(f"Notification step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": True
            }
    
    async def _execute_wait_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute wait step."""
        try:
            config = step.config
            wait_duration = config.get("duration", 300)  # Default 5 minutes
            wait_type = config.get("type", "fixed")
            
            if wait_type == "fixed":
                await asyncio.sleep(wait_duration)
                
            elif wait_type == "until_time":
                target_time = datetime.fromisoformat(config["target_time"])
                wait_seconds = (target_time - datetime.now(timezone.utc)).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                    
            elif wait_type == "user_response":
                # Set execution to waiting status
                execution.status = WorkflowStatus.WAITING
                execution.metadata["waiting_for"] = config.get("response_type", "any")
                execution.metadata["wait_timeout"] = datetime.now(timezone.utc) + timedelta(seconds=wait_duration)
                
                # This will be resumed by external trigger
                return {
                    "success": True,
                    "waiting": True,
                    "timeout": wait_duration
                }
            
            next_step = step.on_success or self._get_next_sequential_step(execution, step)
            
            return {
                "success": True,
                "next_step": next_step
            }
            
        except Exception as e:
            logger.error(f"Wait step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": False
            }
    
    async def _execute_condition_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute conditional step."""
        try:
            config = step.config
            conditions = config.get("conditions", [])
            
            # Evaluate conditions
            for condition in conditions:
                if await self._evaluate_condition(execution, condition):
                    next_step = condition.get("next_step", step.on_success)
                    return {
                        "success": True,
                        "next_step": next_step,
                        "condition_met": condition.get("name", "unnamed")
                    }
            
            # No conditions met, use failure path
            next_step = step.on_failure or self._get_next_sequential_step(execution, step)
            
            return {
                "success": True,
                "next_step": next_step,
                "condition_met": None
            }
            
        except Exception as e:
            logger.error(f"Condition step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": False
            }
    
    async def _execute_action_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute custom action step."""
        try:
            config = step.config
            action_type = config.get("action_type")
            
            if action_type == "update_context":
                # Update execution context
                updates = config.get("context_updates", {})
                execution.context.update(updates)
                
            elif action_type == "api_call":
                # Make external API call
                result = await self._make_api_call(config)
                execution.context[f"action_{step.id}"] = result
                
            elif action_type == "data_processing":
                # Process data
                result = await self._process_workflow_data(execution, config)
                execution.context[f"processed_data_{step.id}"] = result
                
            elif action_type == "business_logic":
                # Execute business logic
                result = await self._execute_business_logic(execution, config)
                execution.context[f"business_result_{step.id}"] = result
            
            next_step = step.on_success or self._get_next_sequential_step(execution, step)
            
            return {
                "success": True,
                "next_step": next_step,
                "action_type": action_type
            }
            
        except Exception as e:
            logger.error(f"Action step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": True
            }
    
    async def _execute_escalation_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute escalation step."""
        try:
            config = step.config
            escalation_type = config.get("escalation_type", "priority")
            
            if escalation_type == "priority":
                # Escalate priority and resend
                escalated_request = self._create_escalated_notification(execution, config)
                response = await self.notification_service.send_notification(escalated_request)
                
                execution.context["escalated"] = True
                execution.context["escalation_level"] = config.get("escalation_level", 1)
                
            elif escalation_type == "supervisor":
                # Notify supervisor or admin
                supervisor_notification = self._create_supervisor_notification(execution, config)
                await self.notification_service.send_notification(supervisor_notification)
                
            elif escalation_type == "external":
                # Trigger external escalation
                await self._trigger_external_escalation(execution, config)
            
            # Update metrics
            self._workflow_metrics[execution.workflow_id].escalation_rate += 1
            
            next_step = step.on_success or self._get_next_sequential_step(execution, step)
            
            return {
                "success": True,
                "next_step": next_step,
                "escalation_type": escalation_type
            }
            
        except Exception as e:
            logger.error(f"Escalation step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": True
            }
    
    async def _execute_follow_up_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute follow-up step."""
        try:
            config = step.config
            follow_up_type = config.get("follow_up_type", "reminder")
            
            # Build follow-up notification
            follow_up_request = self._create_follow_up_notification(execution, config)
            response = await self.notification_service.send_notification(follow_up_request)
            
            if response.success:
                # Update follow-up tracking
                execution.context.setdefault("follow_ups", []).append({
                    "type": follow_up_type,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "notification_id": response.notification_id
                })
                
                next_step = step.on_success or self._get_next_sequential_step(execution, step)
                
                return {
                    "success": True,
                    "next_step": next_step,
                    "follow_up_type": follow_up_type
                }
            else:
                return {
                    "success": False,
                    "error": response.error_message,
                    "retryable": True
                }
                
        except Exception as e:
            logger.error(f"Follow-up step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": True
            }
    
    async def _execute_completion_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Dict[str, Any]:
        """Execute workflow completion step."""
        try:
            config = step.config
            
            # Execute completion actions
            if config.get("send_completion_notification", False):
                completion_request = self._create_completion_notification(execution, config)
                await self.notification_service.send_notification(completion_request)
            
            if config.get("update_user_status", False):
                await self._update_user_workflow_status(execution, config)
            
            if config.get("trigger_next_workflow", False):
                next_workflow_id = config.get("next_workflow_id")
                if next_workflow_id:
                    await self.start_workflow(
                        next_workflow_id,
                        execution.user_id,
                        execution.context
                    )
            
            # Mark as completed
            execution.context["completion_details"] = {
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "completion_type": config.get("completion_type", "success"),
                "final_status": config.get("final_status", "completed")
            }
            
            return {
                "success": True,
                "next_step": None,  # End workflow
                "completion_type": config.get("completion_type", "success")
            }
            
        except Exception as e:
            logger.error(f"Completion step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "retryable": False
            }
    
    def _build_notification_content(self, config: Dict[str, Any], context: Dict[str, Any]):
        """Build notification content from step configuration and context."""
        # This would be implemented to create NotificationContent object
        # For now, return a mock implementation
        from .notification_models import NotificationContent
        
        return NotificationContent(
            title=config.get("title", "Workflow Notification"),
            message=self._render_template(config.get("message", ""), context),
            template_id=config.get("template_id"),
            variables=context.copy(),
            metadata=config.get("metadata", {})
        )
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render message template with context variables."""
        try:
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in template:
                    template = template.replace(placeholder, str(value))
            return template
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return template
    
    async def _check_step_dependencies(self, execution: WorkflowExecution, step: WorkflowStep) -> bool:
        """Check if step dependencies are satisfied."""
        try:
            for dep_step_id in step.dependencies:
                # Check if dependency step completed successfully
                completed_steps = [
                    s["step_id"] for s in execution.step_history 
                    if s.get("success", False)
                ]
                if dep_step_id not in completed_steps:
                    return False
            return True
        except Exception:
            return False
    
    async def _evaluate_step_conditions(self, execution: WorkflowExecution, step: WorkflowStep) -> bool:
        """Evaluate step execution conditions."""
        try:
            for condition in step.conditions:
                if not await self._evaluate_condition(execution, condition):
                    return False
            return True
        except Exception:
            return False
    
    async def _evaluate_condition(self, execution: WorkflowExecution, condition: Dict[str, Any]) -> bool:
        """
Evaluate a single condition."""
        try:
            condition_type = condition.get("type", "context")
            
            if condition_type == "context":
                # Evaluate context-based condition
                field = condition.get("field")
                operator = condition.get("operator", "equals")
                value = condition.get("value")
                
                context_value = execution.context.get(field)
                
                if operator == "equals":
                    return context_value == value
                elif operator == "not_equals":
                    return context_value != value
                elif operator == "greater_than":
                    return float(context_value or 0) > float(value)
                elif operator == "less_than":
                    return float(context_value or 0) < float(value)
                elif operator == "contains":
                    return value in str(context_value or "")
                elif operator == "exists":
                    return field in execution.context
                
            elif condition_type == "time":
                # Evaluate time-based condition
                return self._evaluate_time_condition(condition)
                
            elif condition_type == "business_rule":
                # Evaluate business rule
                return await self._evaluate_business_rule_condition(execution, condition)
            
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False
    
    def _evaluate_time_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate time-based condition."""
        try:
            time_type = condition.get("time_type", "business_hours")
            current_time = datetime.now(timezone.utc)
            
            if time_type == "business_hours":
                return current_time.weekday() < 5 and 9 <= current_time.hour < 17
            elif time_type == "after_time":
                target_time = datetime.fromisoformat(condition["target_time"])
                return current_time >= target_time
            elif time_type == "before_time":
                target_time = datetime.fromisoformat(condition["target_time"])
                return current_time <= target_time
            
            return True
        except Exception:
            return False
    
    async def _evaluate_business_rule_condition(self, execution: WorkflowExecution, condition: Dict[str, Any]) -> bool:
        """Evaluate business rule condition."""
        try:
            rule_name = condition.get("rule_name")
            rule_config = self.business_rules.get(rule_name, {})
            
            # This would implement specific business rule evaluation logic
            # For now, return a basic implementation
            return rule_config.get("default_result", True)
            
        except Exception:
            return False
    
    def _should_retry_step(self, execution: WorkflowExecution, step: WorkflowStep) -> bool:
        """Determine if step should be retried."""
        if not step.retry_config:
            return False
        
        max_retries = step.retry_config.get("max_retries", 3)
        retry_count = execution.context.get(f"retry_count_{step.id}", 0)
        
        return retry_count < max_retries
    
    def _is_workflow_expired(self, execution: WorkflowExecution, workflow_def: WorkflowDefinition) -> bool:
        """Check if workflow has exceeded timeout."""
        if not workflow_def.timeout:
            return False
        
        elapsed_time = (datetime.now(timezone.utc) - execution.created_at).total_seconds()
        return elapsed_time > workflow_def.timeout
    
    def _get_next_sequential_step(self, execution: WorkflowExecution, current_step: WorkflowStep) -> Optional[str]:
        """
Get next sequential step if no explicit next step defined."""
        # This would implement logic to find the next step
        # For now, return None to end workflow
        return None
    
    def _create_escalated_notification(self, execution: WorkflowExecution, config: Dict[str, Any]):
        """
Create escalated notification request."""
        from .notification_models import NotificationRequest, NotificationContent
        
        return NotificationRequest(
            type="escalated_notification",
            recipient_id=execution.user_id,
            content=NotificationContent(
                title="[URGENT] " + config.get("title", "Escalated Notification"),
                message=config.get("escalation_message", "This is an escalated notification."),
                metadata={"escalated": True}
            ),
            priority="urgent",
            channels=config.get("escalation_channels", ["email", "sms"])
        )
    
    def _create_supervisor_notification(self, execution: WorkflowExecution, config: Dict[str, Any]):
        """Create supervisor notification request."""
        from .notification_models import NotificationRequest, NotificationContent
        
        supervisor_id = config.get("supervisor_id", "admin")
        
        return NotificationRequest(
            type="supervisor_alert",
            recipient_id=supervisor_id,
            content=NotificationContent(
                title=f"Workflow Escalation: {execution.workflow_id}",
                message=f"Workflow {execution.workflow_id} for user {execution.user_id} requires attention.",
                metadata={
                    "original_user": execution.user_id,
                    "workflow_id": execution.workflow_id,
                    "execution_id": execution.id
                }
            ),
            priority="high",
            channels=["email"]
        )
    
    async def _trigger_external_escalation(self, execution: WorkflowExecution, config: Dict[str, Any]):
        """Trigger external escalation process."""
        # This would integrate with external systems
        logger.info(f"External escalation triggered for workflow {execution.workflow_id}")
    
    def _create_follow_up_notification(self, execution: WorkflowExecution, config: Dict[str, Any]):
        """Create follow-up notification request."""
        from .notification_models import NotificationRequest, NotificationContent
        
        return NotificationRequest(
            type="follow_up",
            recipient_id=execution.user_id,
            content=NotificationContent(
                title=config.get("title", "Follow-up"),
                message=self._render_template(
                    config.get("message", "This is a follow-up message."),
                    execution.context
                ),
                metadata={"follow_up": True}
            ),
            priority=config.get("priority", "medium"),
            channels=config.get("channels", ["email"])
        )
    
    def _create_completion_notification(self, execution: WorkflowExecution, config: Dict[str, Any]):
        """Create workflow completion notification."""
        from .notification_models import NotificationRequest, NotificationContent
        
        return NotificationRequest(
            type="workflow_completion",
            recipient_id=execution.user_id,
            content=NotificationContent(
                title=config.get("title", "Workflow Completed"),
                message=self._render_template(
                    config.get("message", "Your workflow has been completed successfully."),
                    execution.context
                ),
                metadata={"completion": True}
            ),
            priority="low",
            channels=config.get("channels", ["email"])
        )
    
    async def _update_user_workflow_status(self, execution: WorkflowExecution, config: Dict[str, Any]):
        """Update user's workflow status."""
        # This would update user status in database
        logger.info(f"Updated workflow status for user {execution.user_id}")
    
    async def _make_api_call(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Make external API call."""
        # This would implement API call logic
        return {"api_call_result": "success"}
    
    async def _process_workflow_data(self, execution: WorkflowExecution, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process workflow data."""
        # This would implement data processing logic
        return {"processing_result": "completed"}
    
    async def _execute_business_logic(self, execution: WorkflowExecution, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute business logic."""
        # This would implement business logic
        return {"business_logic_result": "executed"}
    
    async def _update_workflow_metrics(self, execution: WorkflowExecution):
        """Update workflow performance metrics."""
        try:
            metrics = self._workflow_metrics[execution.workflow_id]
            
            if execution.status == WorkflowStatus.COMPLETED:
                metrics.successful_completions += 1
                completion_time = (execution.completed_at - execution.created_at).total_seconds()
                
                # Update average completion time
                total_time = (
                    metrics.average_completion_time * (metrics.successful_completions - 1) + 
                    completion_time
                )
                metrics.average_completion_time = total_time / metrics.successful_completions
                
                # Update step count
                step_count = len(execution.step_history)
                total_steps = (
                    metrics.average_step_count * (metrics.successful_completions - 1) + 
                    step_count
                )
                metrics.average_step_count = total_steps / metrics.successful_completions
                
            elif execution.status == WorkflowStatus.FAILED:
                metrics.failed_executions += 1
            
            # Update completion rate
            metrics.completion_rate = (
                metrics.successful_completions / metrics.total_executions
            ) if metrics.total_executions > 0 else 0.0
            
            # Update performance score (composite metric)
            metrics.performance_score = (
                metrics.completion_rate * 0.4 +
                (1 - metrics.escalation_rate / metrics.total_executions) * 0.3 +
                metrics.user_response_rate * 0.3
            ) if metrics.total_executions > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Workflow metrics update failed: {e}")
    
    async def _cleanup_execution(self, execution_id: str, delay: int = 3600):
        """Cleanup completed workflow execution after delay."""
        await asyncio.sleep(delay)
        
        if execution_id in self._active_executions:
            del self._active_executions[execution_id]
            logger.debug(f"Cleaned up workflow execution {execution_id}")
    
    def _start_background_monitoring(self):
        """Start background monitoring tasks."""
        try:
            # Monitor workflow timeouts
            timeout_task = asyncio.create_task(self._monitor_workflow_timeouts())
            self._background_tasks.append(timeout_task)
            
            # Monitor waiting workflows
            waiting_task = asyncio.create_task(self._monitor_waiting_workflows())
            self._background_tasks.append(waiting_task)
            
            # Performance monitoring
            perf_task = asyncio.create_task(self._monitor_performance())
            self._background_tasks.append(perf_task)
            
            logger.info("Background monitoring tasks started")
            
        except Exception as e:
            logger.error(f"Failed to start background monitoring: {e}")
    
    async def _monitor_workflow_timeouts(self):
        """Monitor and handle workflow timeouts."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for execution_id, execution in list(self._active_executions.items()):
                    if execution.status == WorkflowStatus.RUNNING:
                        workflow_def = self._workflow_definitions.get(execution.workflow_id)
                        
                        if workflow_def and self._is_workflow_expired(execution, workflow_def):
                            execution.status = WorkflowStatus.EXPIRED
                            execution.error_message = "Workflow timeout"
                            execution.updated_at = current_time
                            
                            logger.warning(f"Workflow {execution.workflow_id} expired (execution: {execution_id})")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Workflow timeout monitoring failed: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_waiting_workflows(self):
        """Monitor workflows waiting for user response."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                for execution_id, execution in list(self._active_executions.items()):
                    if execution.status == WorkflowStatus.WAITING:
                        wait_timeout = execution.metadata.get("wait_timeout")
                        
                        if wait_timeout:
                            timeout_time = datetime.fromisoformat(wait_timeout) if isinstance(wait_timeout, str) else wait_timeout
                            
                            if current_time >= timeout_time:
                                # Resume workflow or timeout
                                execution.status = WorkflowStatus.RUNNING
                                execution.context["wait_timeout_occurred"] = True
                                
                                # Continue execution
                                asyncio.create_task(self._execute_workflow(execution_id))
                                
                                logger.info(f"Resumed waiting workflow {execution.workflow_id} due to timeout")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Waiting workflow monitoring failed: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_performance(self):
        """Monitor workflow performance and update statistics."""
        while True:
            try:
                # Update orchestrator statistics
                active_count = len([
                    e for e in self._active_executions.values()
                    if e.status in [WorkflowStatus.RUNNING, WorkflowStatus.WAITING]
                ])
                
                self.orchestrator_stats["active_workflows"] = active_count
                
                # Calculate success rate
                total_completed = sum(
                    metrics.successful_completions + metrics.failed_executions
                    for metrics in self._workflow_metrics.values()
                )
                
                total_successful = sum(
                    metrics.successful_completions
                    for metrics in self._workflow_metrics.values()
                )
                
                if total_completed > 0:
                    self.orchestrator_stats["success_rate"] = total_successful / total_completed
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                logger.error(f"Performance monitoring failed: {e}")
                await asyncio.sleep(300)
    
    def _load_workflow_templates(self):
        """Load workflow templates from configuration."""
        try:
            # Load predefined workflow templates
            templates = WORKFLOW_TEMPLATES
            
            for template_id, template_data in templates.items():
                workflow_def = self._parse_workflow_template(template_id, template_data)
                self._workflow_definitions[template_id] = workflow_def
            
            logger.info(f"Loaded {len(self._workflow_definitions)} workflow definitions")
            
        except Exception as e:
            logger.error(f"Failed to load workflow templates: {e}")
    
    def _parse_workflow_template(self, template_id: str, template_data: Dict[str, Any]) -> WorkflowDefinition:
        """Parse workflow template into WorkflowDefinition."""
        try:
            # Parse steps
            steps = {}
            for step_data in template_data.get("steps", []):
                step = WorkflowStep(
                    id=step_data["id"],
                    name=step_data["name"],
                    type=WorkflowStepType(step_data["type"]),
                    config=step_data.get("config", {}),
                    dependencies=step_data.get("dependencies", []),
                    conditions=step_data.get("conditions", []),
                    timeout=step_data.get("timeout"),
                    retry_config=step_data.get("retry_config"),
                    on_success=step_data.get("on_success"),
                    on_failure=step_data.get("on_failure"),
                    metadata=step_data.get("metadata", {})
                )
                steps[step.id] = step
            
            # Parse triggers
            triggers = [
                WorkflowTrigger(trigger) 
                for trigger in template_data.get("triggers", ["immediate"])
            ]
            
            return WorkflowDefinition(
                id=template_id,
                name=template_data["name"],
                description=template_data.get("description", ""),
                version=template_data.get("version", "1.0"),
                category=template_data.get("category", "general"),
                steps=steps,
                entry_point=template_data["entry_point"],
                triggers=triggers,
                business_rules=template_data.get("business_rules", {}),
                escalation_rules=template_data.get("escalation_rules", {}),
                timeout=template_data.get("timeout"),
                metadata=template_data.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to parse workflow template {template_id}: {e}")
            raise
    
    # Public API methods
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause workflow execution."""
        try:
            execution = self._active_executions.get(execution_id)
            if execution and execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.PAUSED
                execution.updated_at = datetime.now(timezone.utc)
                logger.info(f"Paused workflow execution {execution_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to pause workflow {execution_id}: {e}")
            return False
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume paused workflow execution."""
        try:
            execution = self._active_executions.get(execution_id)
            if execution and execution.status == WorkflowStatus.PAUSED:
                execution.status = WorkflowStatus.RUNNING
                execution.updated_at = datetime.now(timezone.utc)
                
                # Continue execution
                asyncio.create_task(self._execute_workflow(execution_id))
                
                logger.info(f"Resumed workflow execution {execution_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resume workflow {execution_id}: {e}")
            return False
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel workflow execution."""
        try:
            execution = self._active_executions.get(execution_id)
            if execution and execution.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED, WorkflowStatus.WAITING]:
                execution.status = WorkflowStatus.CANCELLED
                execution.updated_at = datetime.now(timezone.utc)
                self.orchestrator_stats["active_workflows"] -= 1
                
                logger.info(f"Cancelled workflow execution {execution_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel workflow {execution_id}: {e}")
            return False
    
    async def trigger_waiting_workflow(self, execution_id: str, response_data: Dict[str, Any]) -> bool:
        """Trigger waiting workflow with user response."""
        try:
            execution = self._active_executions.get(execution_id)
            if execution and execution.status == WorkflowStatus.WAITING:
                # Add response data to context
                execution.context["user_response"] = response_data
                execution.context["response_received_at"] = datetime.now(timezone.utc).isoformat()
                
                # Resume workflow
                execution.status = WorkflowStatus.RUNNING
                execution.updated_at = datetime.now(timezone.utc)
                
                # Continue execution
                asyncio.create_task(self._execute_workflow(execution_id))
                
                logger.info(f"Triggered waiting workflow {execution_id} with user response")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to trigger waiting workflow {execution_id}: {e}")
            return False
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status."""
        return self._active_executions.get(execution_id)
    
    def get_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """
Get workflow performance metrics."""
        return self._workflow_metrics.get(workflow_id)
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
Get orchestrator performance statistics."""
        return self.orchestrator_stats.copy()
    
    def list_active_workflows(self) -> List[WorkflowExecution]:
        """
List all active workflow executions."""
        return list(self._active_executions.values())
    
    def list_workflow_definitions(self) -> List[WorkflowDefinition]:
        """
List all available workflow definitions."""
        return list(self._workflow_definitions.values())
    
    async def shutdown(self):
        """
Shutdown workflow orchestrator."""
        try:
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
            
            # Wait for background tasks to complete
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            logger.info("Workflow orchestrator shut down successfully")
            
        except Exception as e:
            logger.error(f"Workflow orchestrator shutdown failed: {e}")
