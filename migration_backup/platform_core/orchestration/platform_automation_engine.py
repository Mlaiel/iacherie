#!/usr/bin/env python3
"""
Platform Automation Engine - Enterprise Core Component
Automated operations and maintenance system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive platform automation capabilities including:
- Automated operations and maintenance
- Self-service provisioning
- Automated scaling and optimization
- Routine task automation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import yaml
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomationTrigger(Enum):
    """Automation trigger types"""
    SCHEDULE = "schedule"
    EVENT = "event"
    METRIC = "metric"
    MANUAL = "manual"
    THRESHOLD = "threshold"
    WEBHOOK = "webhook"
    API = "api"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    PAUSED = "paused"


class ActionType(Enum):
    """Automation action types"""
    SCALE_SERVICE = "scale_service"
    RESTART_SERVICE = "restart_service"
    DEPLOY_UPDATE = "deploy_update"
    BACKUP_DATA = "backup_data"
    CLEANUP_RESOURCES = "cleanup_resources"
    SEND_NOTIFICATION = "send_notification"
    RUN_SCRIPT = "run_script"
    EXECUTE_QUERY = "execute_query"
    UPDATE_CONFIG = "update_config"
    HEALTH_CHECK = "health_check"


class ConditionOperator(Enum):
    """Condition operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    REGEX_MATCH = "regex_match"


@dataclass
class AutomationCondition:
    """Condition for automation execution"""
    field: str
    operator: ConditionOperator
    value: Any
    description: Optional[str] = None


@dataclass
class AutomationAction:
    """Action to be executed"""
    action_id: str
    action_type: ActionType
    name: str
    description: str
    parameters: Dict[str, Any]
    conditions: List[AutomationCondition] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay: int = 60
    dependencies: List[str] = field(default_factory=list)


@dataclass
class AutomationWorkflow:
    """Automation workflow definition"""
    workflow_id: str
    name: str
    description: str
    trigger: AutomationTrigger
    trigger_config: Dict[str, Any]
    actions: List[AutomationAction]
    enabled: bool = True
    parallel_execution: bool = False
    max_executions: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution tracking"""
    execution_id: str
    workflow_id: str
    status: TaskStatus
    triggered_by: str
    trigger_data: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_action_index: int = 0
    executed_actions: List[str] = field(default_factory=list)
    failed_actions: List[str] = field(default_factory=list)
    execution_logs: List[str] = field(default_factory=list)
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class ScheduledTask:
    """Scheduled automation task"""
    task_id: str
    workflow_id: str
    schedule: str  # Cron-like expression
    next_run: datetime
    last_run: Optional[datetime] = None
    enabled: bool = True
    timezone: str = "UTC"
    metadata: Dict[str, Any] = field(default_factory=dict)


class PlatformAutomationEngine:
    """
    Enterprise Platform Automation Engine
    
    Manages comprehensive automation capabilities including workflow orchestration,
    scheduled tasks, event-driven automation, and self-service operations.
    """
    
    def __init__(self):
        self.workflows: Dict[str, AutomationWorkflow] = {}
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []
        
        # Task queues
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.priority_queue: asyncio.Queue = asyncio.Queue()
        
        # Worker tasks
        self.worker_tasks: List[asyncio.Task] = []
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "workflow_started": [],
            "workflow_completed": [],
            "workflow_failed": [],
            "action_executed": [],
            "schedule_triggered": [],
            "automation_error": []
        }
        
        # Metrics and monitoring
        self.execution_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.max_concurrent_executions = 10
        self.max_execution_history = 10000
        self.default_timeout = timedelta(minutes=30)
        self.auto_cleanup_enabled = True
        self.worker_count = 5
        
        # Action executors
        self.action_executors: Dict[ActionType, Callable] = {
            ActionType.SCALE_SERVICE: self._execute_scale_service,
            ActionType.RESTART_SERVICE: self._execute_restart_service,
            ActionType.DEPLOY_UPDATE: self._execute_deploy_update,
            ActionType.BACKUP_DATA: self._execute_backup_data,
            ActionType.CLEANUP_RESOURCES: self._execute_cleanup_resources,
            ActionType.SEND_NOTIFICATION: self._execute_send_notification,
            ActionType.RUN_SCRIPT: self._execute_run_script,
            ActionType.EXECUTE_QUERY: self._execute_query,
            ActionType.UPDATE_CONFIG: self._execute_update_config,
            ActionType.HEALTH_CHECK: self._execute_health_check
        }
        
        # Initialize engine state
        self._engine_started = False
        
        logger.info("Platform Automation Engine initialized")
    
    async def start_engine(self):
        """Start the automation engine if not already started"""
        if not self._engine_started:
            await self._start_engine()
            self._engine_started = True
    
    async def create_workflow(self, workflow: AutomationWorkflow) -> bool:
        """Create automation workflow"""
        try:
            # Validate workflow
            if not await self._validate_workflow(workflow):
                logger.error(f"Workflow validation failed: {workflow.workflow_id}")
                return False
            
            self.workflows[workflow.workflow_id] = workflow
            
            # Set up triggers
            await self._setup_workflow_triggers(workflow)
            
            logger.info(f"Automation workflow created: {workflow.workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create workflow {workflow.workflow_id}: {e}")
            return False
    
    async def execute_workflow(
        self,
        workflow_id: str,
        triggered_by: str = "manual",
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute automation workflow"""
        # Ensure engine is started
        await self.start_engine()
        
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if not workflow.enabled:
            raise ValueError(f"Workflow is disabled: {workflow_id}")
        
        # Check execution limits
        active_count = len([
            e for e in self.active_executions.values()
            if e.workflow_id == workflow_id
        ])
        
        if active_count >= workflow.max_executions:
            raise ValueError(f"Maximum concurrent executions reached for workflow: {workflow_id}")
        
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=TaskStatus.PENDING,
            triggered_by=triggered_by,
            trigger_data=trigger_data or {},
            started_at=datetime.utcnow()
        )
        
        self.active_executions[execution_id] = execution
        
        # Queue for execution
        await self.task_queue.put(execution_id)
        
        await self._trigger_event("workflow_started", execution_id)
        logger.info(f"Workflow execution queued: {execution_id}")
        
        return execution_id
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                return False
            
            execution.status = TaskStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            execution.execution_logs.append("Execution cancelled by user")
            
            logger.info(f"Workflow execution cancelled: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel execution {execution_id}: {e}")
            return False
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause workflow execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution or execution.status != TaskStatus.RUNNING:
                return False
            
            execution.status = TaskStatus.PAUSED
            execution.execution_logs.append("Execution paused")
            
            logger.info(f"Workflow execution paused: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause execution {execution_id}: {e}")
            return False
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume paused workflow execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution or execution.status != TaskStatus.PAUSED:
                return False
            
            execution.status = TaskStatus.RUNNING
            execution.execution_logs.append("Execution resumed")
            
            # Re-queue for execution
            await self.task_queue.put(execution_id)
            
            logger.info(f"Workflow execution resumed: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume execution {execution_id}: {e}")
            return False
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        # Check active executions
        execution = self.active_executions.get(execution_id)
        if execution:
            return self._format_execution_status(execution)
        
        # Check history
        for historical_execution in self.execution_history:
            if historical_execution.execution_id == execution_id:
                return self._format_execution_status(historical_execution)
        
        return None
    
    async def list_workflows(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """List automation workflows"""
        workflows = []
        
        for workflow in self.workflows.values():
            if enabled_only and not workflow.enabled:
                continue
            
            # Get execution statistics
            total_executions = len([
                e for e in self.execution_history
                if e.workflow_id == workflow.workflow_id
            ])
            
            successful_executions = len([
                e for e in self.execution_history
                if e.workflow_id == workflow.workflow_id and e.status == TaskStatus.COMPLETED
            ])
            
            workflows.append({
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "trigger": workflow.trigger.value,
                "enabled": workflow.enabled,
                "action_count": len(workflow.actions),
                "total_executions": total_executions,
                "success_rate": (successful_executions / max(total_executions, 1)) * 100,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat()
            })
        
        return workflows
    
    async def get_automation_metrics(self) -> Dict[str, Any]:
        """Get automation metrics"""
        total_workflows = len(self.workflows)
        enabled_workflows = len([w for w in self.workflows.values() if w.enabled])
        active_executions = len(self.active_executions)
        
        # Calculate success rates
        total_executions = len(self.execution_history)
        successful_executions = len([e for e in self.execution_history if e.status == TaskStatus.COMPLETED])
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_executions = len([
            e for e in self.execution_history
            if e.started_at > recent_cutoff
        ])
        
        # Average execution time
        completed_executions = [e for e in self.execution_history if e.status == TaskStatus.COMPLETED and e.completed_at]
        avg_execution_time = 0.0
        if completed_executions:
            total_time = sum(
                (e.completed_at - e.started_at).total_seconds()
                for e in completed_executions
            )
            avg_execution_time = total_time / len(completed_executions)
        
        return {
            "workflows": {
                "total": total_workflows,
                "enabled": enabled_workflows,
                "disabled": total_workflows - enabled_workflows
            },
            "executions": {
                "active": active_executions,
                "total_historical": total_executions,
                "successful": successful_executions,
                "success_rate": (successful_executions / max(total_executions, 1)) * 100,
                "recent_24h": recent_executions
            },
            "performance": {
                "average_execution_time_seconds": avg_execution_time,
                "queue_depth": self.task_queue.qsize(),
                "worker_count": len(self.worker_tasks)
            },
            "scheduled_tasks": {
                "total": len(self.scheduled_tasks),
                "enabled": len([t for t in self.scheduled_tasks.values() if t.enabled])
            }
        }
    
    async def create_scheduled_task(
        self,
        workflow_id: str,
        schedule: str,
        timezone: str = "UTC"
    ) -> str:
        """Create scheduled task"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        task_id = str(uuid.uuid4())
        
        # Calculate next run time
        next_run = self._calculate_next_run(schedule, timezone)
        
        scheduled_task = ScheduledTask(
            task_id=task_id,
            workflow_id=workflow_id,
            schedule=schedule,
            next_run=next_run,
            timezone=timezone
        )
        
        self.scheduled_tasks[task_id] = scheduled_task
        
        logger.info(f"Scheduled task created: {task_id} for workflow {workflow_id}")
        return task_id
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow configuration"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)
            
            workflow.updated_at = datetime.utcnow()
            
            # Re-validate workflow
            if not await self._validate_workflow(workflow):
                logger.error(f"Updated workflow validation failed: {workflow_id}")
                return False
            
            logger.info(f"Workflow updated: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            return False
    
    async def delete_workflow(self, workflow_id: str, force: bool = False) -> bool:
        """Delete workflow"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Check for active executions
            active_count = len([
                e for e in self.active_executions.values()
                if e.workflow_id == workflow_id
            ])
            
            if active_count > 0 and not force:
                logger.error(f"Cannot delete workflow with active executions: {workflow_id}")
                return False
            
            # Cancel active executions if force delete
            if force:
                for execution in list(self.active_executions.values()):
                    if execution.workflow_id == workflow_id:
                        await self.cancel_execution(execution.execution_id)
            
            # Remove workflow and related scheduled tasks
            del self.workflows[workflow_id]
            
            tasks_to_remove = [
                task_id for task_id, task in self.scheduled_tasks.items()
                if task.workflow_id == workflow_id
            ]
            
            for task_id in tasks_to_remove:
                del self.scheduled_tasks[task_id]
            
            logger.info(f"Workflow deleted: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False
    
    # Private methods
    
    async def _start_engine(self):
        """Start automation engine"""
        # Start worker tasks
        for i in range(self.worker_count):
            worker_task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.worker_tasks.append(worker_task)
        
        # Start scheduler
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info(f"Automation engine started with {self.worker_count} workers")
    
    async def _worker_loop(self, worker_name: str):
        """Worker loop for executing workflows"""
        while True:
            try:
                # Get next execution from queue
                execution_id = await self.task_queue.get()
                
                execution = self.active_executions.get(execution_id)
                if not execution:
                    continue
                
                if execution.status == TaskStatus.CANCELLED:
                    continue
                
                logger.info(f"{worker_name} executing workflow: {execution_id}")
                
                # Execute workflow
                await self._execute_workflow_actions(execution)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
    
    async def _scheduler_loop(self):
        """Scheduler loop for handling scheduled tasks"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                for task in list(self.scheduled_tasks.values()):
                    if not task.enabled:
                        continue
                    
                    if current_time >= task.next_run:
                        # Execute scheduled workflow
                        try:
                            execution_id = await self.execute_workflow(
                                task.workflow_id,
                                triggered_by="scheduler",
                                trigger_data={"task_id": task.task_id, "scheduled_time": current_time.isoformat()}
                            )
                            
                            task.last_run = current_time
                            task.next_run = self._calculate_next_run(task.schedule, task.timezone)
                            
                            await self._trigger_event("schedule_triggered", f"{task.task_id}:{execution_id}")
                            
                            logger.info(f"Scheduled task executed: {task.task_id} -> {execution_id}")
                            
                        except Exception as e:
                            logger.error(f"Failed to execute scheduled task {task.task_id}: {e}")
                
                # Sleep for a minute before checking again
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(60)
    
    async def _execute_workflow_actions(self, execution: WorkflowExecution):
        """Execute all actions in a workflow"""
        try:
            execution.status = TaskStatus.RUNNING
            workflow = self.workflows[execution.workflow_id]
            
            execution.execution_logs.append(f"Starting workflow execution: {workflow.name}")
            
            if workflow.parallel_execution:
                # Execute actions in parallel
                await self._execute_actions_parallel(execution, workflow)
            else:
                # Execute actions sequentially
                await self._execute_actions_sequential(execution, workflow)
            
            if execution.status == TaskStatus.RUNNING:
                execution.status = TaskStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                execution.execution_logs.append("Workflow execution completed successfully")
                
                await self._trigger_event("workflow_completed", execution.execution_id)
            
        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error_message = str(e)
            execution.execution_logs.append(f"Workflow execution failed: {e}")
            
            await self._trigger_event("workflow_failed", execution.execution_id)
            logger.error(f"Workflow execution failed {execution.execution_id}: {e}")
        
        finally:
            # Move to history
            if execution.execution_id in self.active_executions:
                self.execution_history.append(self.active_executions[execution.execution_id])
                del self.active_executions[execution.execution_id]
                
                # Maintain history size limit
                if len(self.execution_history) > self.max_execution_history:
                    self.execution_history = self.execution_history[-self.max_execution_history:]
    
    async def _execute_actions_sequential(self, execution: WorkflowExecution, workflow: AutomationWorkflow):
        """Execute actions sequentially"""
        for i, action in enumerate(workflow.actions):
            if execution.status in [TaskStatus.CANCELLED, TaskStatus.PAUSED]:
                break
            
            execution.current_action_index = i
            
            # Check dependencies
            if not await self._check_action_dependencies(action, execution):
                execution.execution_logs.append(f"Action dependencies not met: {action.name}")
                continue
            
            # Check conditions
            if not await self._check_action_conditions(action, execution):
                execution.execution_logs.append(f"Action conditions not met: {action.name}")
                continue
            
            # Execute action
            success = await self._execute_single_action(action, execution)
            
            if success:
                execution.executed_actions.append(action.action_id)
                await self._trigger_event("action_executed", f"{execution.execution_id}:{action.action_id}")
            else:
                execution.failed_actions.append(action.action_id)
                
                # Stop on failure unless configured otherwise
                if not workflow.metadata.get("continue_on_failure", False):
                    execution.status = TaskStatus.FAILED
                    break
    
    async def _execute_actions_parallel(self, execution: WorkflowExecution, workflow: AutomationWorkflow):
        """Execute actions in parallel"""
        tasks = []
        
        for action in workflow.actions:
            if execution.status in [TaskStatus.CANCELLED, TaskStatus.PAUSED]:
                break
            
            task = asyncio.create_task(self._execute_action_with_dependencies(action, execution))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            action = workflow.actions[i]
            
            if isinstance(result, Exception):
                execution.failed_actions.append(action.action_id)
                execution.execution_logs.append(f"Action failed: {action.name} - {result}")
            elif result:
                execution.executed_actions.append(action.action_id)
                await self._trigger_event("action_executed", f"{execution.execution_id}:{action.action_id}")
            else:
                execution.failed_actions.append(action.action_id)
    
    async def _execute_action_with_dependencies(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute action with dependency checking"""
        # Wait for dependencies
        while True:
            if await self._check_action_dependencies(action, execution):
                break
            await asyncio.sleep(1)
        
        # Check conditions
        if not await self._check_action_conditions(action, execution):
            return False
        
        return await self._execute_single_action(action, execution)
    
    async def _execute_single_action(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute a single action"""
        try:
            execution.execution_logs.append(f"Executing action: {action.name}")
            
            # Get action executor
            executor = self.action_executors.get(action.action_type)
            if not executor:
                execution.execution_logs.append(f"No executor found for action type: {action.action_type.value}")
                return False
            
            # Execute with timeout
            result = await asyncio.wait_for(
                executor(action, execution),
                timeout=action.timeout_seconds
            )
            
            if result:
                execution.execution_logs.append(f"Action completed successfully: {action.name}")
            else:
                execution.execution_logs.append(f"Action failed: {action.name}")
            
            return result
            
        except asyncio.TimeoutError:
            execution.execution_logs.append(f"Action timed out: {action.name}")
            return False
        except Exception as e:
            execution.execution_logs.append(f"Action error: {action.name} - {e}")
            return False
    
    async def _check_action_dependencies(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Check if action dependencies are satisfied"""
        for dependency in action.dependencies:
            if dependency not in execution.executed_actions:
                return False
        return True
    
    async def _check_action_conditions(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Check if action conditions are met"""
        for condition in action.conditions:
            if not await self._evaluate_condition(condition, execution):
                return False
        return True
    
    async def _evaluate_condition(self, condition: AutomationCondition, execution: WorkflowExecution) -> bool:
        """Evaluate a condition"""
        try:
            # Get field value from execution context
            field_value = self._get_field_value(condition.field, execution)
            
            if condition.operator == ConditionOperator.EQUALS:
                return field_value == condition.value
            elif condition.operator == ConditionOperator.NOT_EQUALS:
                return field_value != condition.value
            elif condition.operator == ConditionOperator.GREATER_THAN:
                return float(field_value) > float(condition.value)
            elif condition.operator == ConditionOperator.LESS_THAN:
                return float(field_value) < float(condition.value)
            elif condition.operator == ConditionOperator.GREATER_EQUAL:
                return float(field_value) >= float(condition.value)
            elif condition.operator == ConditionOperator.LESS_EQUAL:
                return float(field_value) <= float(condition.value)
            elif condition.operator == ConditionOperator.CONTAINS:
                return str(condition.value) in str(field_value)
            elif condition.operator == ConditionOperator.REGEX_MATCH:
                return bool(re.match(str(condition.value), str(field_value)))
            
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    def _get_field_value(self, field: str, execution: WorkflowExecution) -> Any:
        """Get field value from execution context"""
        # Simple field resolution
        if field.startswith("trigger_data."):
            field_path = field[13:]  # Remove "trigger_data."
            return execution.trigger_data.get(field_path)
        elif field.startswith("result_data."):
            field_path = field[12:]  # Remove "result_data."
            return execution.result_data.get(field_path)
        elif field == "execution_id":
            return execution.execution_id
        elif field == "workflow_id":
            return execution.workflow_id
        elif field == "triggered_by":
            return execution.triggered_by
        
        return None
    
    async def _validate_workflow(self, workflow: AutomationWorkflow) -> bool:
        """Validate workflow configuration"""
        if not workflow.workflow_id or not workflow.name:
            return False
        
        if not workflow.actions:
            return False
        
        # Validate actions
        for action in workflow.actions:
            if action.action_type not in self.action_executors:
                logger.error(f"Unknown action type: {action.action_type}")
                return False
        
        return True
    
    async def _setup_workflow_triggers(self, workflow: AutomationWorkflow):
        """Set up workflow triggers"""
        if workflow.trigger == AutomationTrigger.SCHEDULE:
            # Create scheduled task
            schedule = workflow.trigger_config.get("schedule", "0 0 * * *")  # Daily default
            timezone = workflow.trigger_config.get("timezone", "UTC")
            await self.create_scheduled_task(workflow.workflow_id, schedule, timezone)
    
    def _calculate_next_run(self, schedule: str, timezone: str) -> datetime:
        """Calculate next run time from cron expression"""
        # Simplified cron parsing - in production would use croniter or similar
        # For now, just schedule 1 hour from now
        return datetime.utcnow() + timedelta(hours=1)
    
    def _format_execution_status(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Format execution status for API response"""
        workflow = self.workflows.get(execution.workflow_id)
        
        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "workflow_name": workflow.name if workflow else "Unknown",
            "status": execution.status.value,
            "triggered_by": execution.triggered_by,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "current_action_index": execution.current_action_index,
            "total_actions": len(workflow.actions) if workflow else 0,
            "executed_actions": len(execution.executed_actions),
            "failed_actions": len(execution.failed_actions),
            "recent_logs": execution.execution_logs[-5:],  # Last 5 log entries
            "error_message": execution.error_message
        }
    
    # Action Executors
    
    async def _execute_scale_service(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute service scaling action"""
        service_name = action.parameters.get("service_name")
        target_replicas = action.parameters.get("target_replicas", 1)
        
        execution.execution_logs.append(f"Scaling service {service_name} to {target_replicas} replicas")
        
        # Simulate scaling
        await asyncio.sleep(2)
        
        execution.result_data[f"scaled_{service_name}"] = target_replicas
        return True
    
    async def _execute_restart_service(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute service restart action"""
        service_name = action.parameters.get("service_name")
        
        execution.execution_logs.append(f"Restarting service: {service_name}")
        
        # Simulate restart
        await asyncio.sleep(3)
        
        execution.result_data[f"restarted_{service_name}"] = True
        return True
    
    async def _execute_deploy_update(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute deployment update action"""
        service_name = action.parameters.get("service_name")
        version = action.parameters.get("version")
        
        execution.execution_logs.append(f"Deploying {service_name} version {version}")
        
        # Simulate deployment
        await asyncio.sleep(5)
        
        execution.result_data[f"deployed_{service_name}"] = version
        return True
    
    async def _execute_backup_data(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute data backup action"""
        data_source = action.parameters.get("data_source")
        backup_location = action.parameters.get("backup_location")
        
        execution.execution_logs.append(f"Backing up {data_source} to {backup_location}")
        
        # Simulate backup
        await asyncio.sleep(4)
        
        backup_id = str(uuid.uuid4())
        execution.result_data[f"backup_{data_source}"] = backup_id
        return True
    
    async def _execute_cleanup_resources(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute resource cleanup action"""
        resource_type = action.parameters.get("resource_type")
        criteria = action.parameters.get("criteria", {})
        
        execution.execution_logs.append(f"Cleaning up {resource_type} resources")
        
        # Simulate cleanup
        await asyncio.sleep(2)
        
        cleaned_count = 5  # Simulated
        execution.result_data[f"cleaned_{resource_type}"] = cleaned_count
        return True
    
    async def _execute_send_notification(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute notification sending action"""
        recipient = action.parameters.get("recipient")
        message = action.parameters.get("message")
        channel = action.parameters.get("channel", "email")
        
        execution.execution_logs.append(f"Sending {channel} notification to {recipient}")
        
        # Simulate notification
        await asyncio.sleep(1)
        
        execution.result_data["notification_sent"] = True
        return True
    
    async def _execute_run_script(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute script running action"""
        script_path = action.parameters.get("script_path")
        arguments = action.parameters.get("arguments", [])
        
        execution.execution_logs.append(f"Running script: {script_path}")
        
        # Simulate script execution
        await asyncio.sleep(3)
        
        execution.result_data["script_exit_code"] = 0
        return True
    
    async def _execute_query(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute database query action"""
        query = action.parameters.get("query")
        database = action.parameters.get("database")
        
        execution.execution_logs.append(f"Executing query on {database}")
        
        # Simulate query execution
        await asyncio.sleep(1)
        
        execution.result_data["query_results"] = {"rows_affected": 10}
        return True
    
    async def _execute_update_config(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute configuration update action"""
        config_path = action.parameters.get("config_path")
        updates = action.parameters.get("updates", {})
        
        execution.execution_logs.append(f"Updating configuration: {config_path}")
        
        # Simulate config update
        await asyncio.sleep(1)
        
        execution.result_data["config_updated"] = True
        return True
    
    async def _execute_health_check(self, action: AutomationAction, execution: WorkflowExecution) -> bool:
        """Execute health check action"""
        target = action.parameters.get("target")
        
        execution.execution_logs.append(f"Performing health check on: {target}")
        
        # Simulate health check
        await asyncio.sleep(1)
        
        execution.result_data[f"health_check_{target}"] = "healthy"
        return True
    
    async def _trigger_event(self, event_type: str, event_data: str):
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
platform_automation_engine = PlatformAutomationEngine()


# Convenience functions
async def create_simple_workflow(
    name: str,
    description: str,
    actions: List[AutomationAction],
    trigger: AutomationTrigger = AutomationTrigger.MANUAL
) -> str:
    """Create a simple automation workflow"""
    workflow_id = str(uuid.uuid4())
    
    workflow = AutomationWorkflow(
        workflow_id=workflow_id,
        name=name,
        description=description,
        trigger=trigger,
        trigger_config={},
        actions=actions
    )
    
    await platform_automation_engine.create_workflow(workflow)
    return workflow_id


async def create_scaling_action(service_name: str, target_replicas: int) -> AutomationAction:
    """Create service scaling action"""
    return AutomationAction(
        action_id=str(uuid.uuid4()),
        action_type=ActionType.SCALE_SERVICE,
        name=f"Scale {service_name}",
        description=f"Scale {service_name} to {target_replicas} replicas",
        parameters={
            "service_name": service_name,
            "target_replicas": target_replicas
        }
    )


async def execute_workflow_by_name(workflow_name: str) -> Optional[str]:
    """Execute workflow by name"""
    for workflow in platform_automation_engine.workflows.values():
        if workflow.name == workflow_name:
            return await platform_automation_engine.execute_workflow(workflow.workflow_id)
    return None


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create a simple scaling workflow
        scaling_action = await create_scaling_action("api-service", 5)
        
        workflow_id = await create_simple_workflow(
            "Auto Scale API Service",
            "Automatically scale API service based on load",
            [scaling_action]
        )
        
        print(f"Created workflow: {workflow_id}")
        
        # Execute the workflow
        execution_id = await platform_automation_engine.execute_workflow(workflow_id)
        print(f"Workflow execution started: {execution_id}")
        
        # Wait for completion
        while True:
            status = await platform_automation_engine.get_execution_status(execution_id)
            if status:
                print(f"Status: {status['status']}")
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    break
            await asyncio.sleep(1)
        
        # Get final status
        final_status = await platform_automation_engine.get_execution_status(execution_id)
        print(f"Final result: {final_status}")
        
        # Get metrics
        metrics = await platform_automation_engine.get_automation_metrics()
        print(f"Automation metrics: {metrics}")
    
    asyncio.run(main())