"""Platform Automation Module

Advanced automation workflows for platform operations and content management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import logging
import json
import uuid
from abc import ABC, abstractmethod

from .base import PlatformBase, ContentMetadata, AnalyticsData
from .distributor import PlatformDistributor, DistributionStrategy
from .aggregator import PlatformAggregator
from .monitor import PlatformMonitor, MonitorSeverity
from .scheduler import PlatformScheduler, ScheduleConfig, ScheduleType, TaskPriority

logger = logging.getLogger(__name__)


class AutomationTrigger(Enum):
    """Types of automation triggers"""    TIME_BASED = "time_based"
    METRIC_THRESHOLD = "metric_threshold"
    PLATFORM_STATUS = "platform_status"
    CONTENT_PERFORMANCE = "content_performance"
    USER_ACTION = "user_action"
    EXTERNAL_EVENT = "external_event"
    CONDITIONAL = "conditional"


class AutomationAction(Enum):
    """Types of automation actions"""    DISTRIBUTE_CONTENT = "distribute_content"
    SEND_NOTIFICATION = "send_notification"
    UPDATE_SETTINGS = "update_settings"
    TRIGGER_BACKUP = "trigger_backup"
    SCALE_RESOURCES = "scale_resources"
    EXECUTE_FUNCTION = "execute_function"
    SEND_ALERT = "send_alert"
    PAUSE_OPERATIONS = "pause_operations"


class WorkflowStatus(Enum):
    """Workflow execution status"""    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AutomationCondition:
    """Condition for automation trigger"""    condition_type: str
    parameter: str
    operator: str  # eq, gt, lt, gte, lte, contains, regex
    value: Any
    platform_id: Optional[str] = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context"""        try:
            # Get value from context
            if self.platform_id:
                platform_context = context.get('platforms', {}).get(self.platform_id, {})
                actual_value = platform_context.get(self.parameter)
            else:
                actual_value = context.get(self.parameter)
            
            if actual_value is None:
                return False
            
            # Apply operator
            if self.operator == 'eq':
                return actual_value == self.value
            elif self.operator == 'gt':
                return actual_value > self.value
            elif self.operator == 'lt':
                return actual_value < self.value
            elif self.operator == 'gte':
                return actual_value >= self.value
            elif self.operator == 'lte':
                return actual_value <= self.value
            elif self.operator == 'contains':
                return str(self.value).lower() in str(actual_value).lower()
            elif self.operator == 'regex':
                import re
                return bool(re.search(str(self.value), str(actual_value)))
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False


@dataclass
class AutomationRule:
    """Automation rule definition"""    rule_id: str
    name: str
    description: str
    trigger: AutomationTrigger
    conditions: List[AutomationCondition]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Execution tracking
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None
    
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if rule should execute based on conditions"""        if not self.enabled:
            return False
        
        if not self.conditions:
            return True  # No conditions = always execute
        
        # All conditions must be true (AND logic)
        return all(condition.evaluate(context) for condition in self.conditions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'trigger': self.trigger.value,
            'conditions': [
                {
                    'condition_type': c.condition_type,
                    'parameter': c.parameter,
                    'operator': c.operator,
                    'value': c.value,
                    'platform_id': c.platform_id
                }
                for c in self.conditions
            ],
            'actions': self.actions,
            'enabled': self.enabled,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'execution_count': self.execution_count,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'last_result': self.last_result
        }


@dataclass
class WorkflowStep:
    """Single step in automation workflow"""    step_id: str
    name: str
    action_type: AutomationAction
    parameters: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout_seconds: int = 300
    
    # Execution tracking
    status: WorkflowStatus = WorkflowStatus.INACTIVE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AutomationWorkflow:
    """Complex automation workflow"""    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    trigger_rules: List[str]  # Rule IDs that can trigger this workflow
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Execution tracking
    status: WorkflowStatus = WorkflowStatus.INACTIVE
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_count: int = 0
    
    def get_next_steps(self) -> List[WorkflowStep]:
        """Get steps ready for execution"""        ready_steps = []
        completed_step_ids = {
            step.step_id for step in self.steps 
            if step.status == WorkflowStatus.COMPLETED
        }
        
        for step in self.steps:
            if step.status == WorkflowStatus.INACTIVE:
                # Check if dependencies are satisfied
                if all(dep_id in completed_step_ids for dep_id in step.depends_on):
                    ready_steps.append(step)
        
        return ready_steps
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""        return all(step.status == WorkflowStatus.COMPLETED for step in self.steps)
    
    def has_failed(self) -> bool:
        """Check if workflow has failed"""        return any(step.status == WorkflowStatus.FAILED for step in self.steps)


class AutomationEngine:
    """Core automation engine for platform operations"""    
    def __init__(self):
        """Initialize automation engine"""        self.rules: Dict[str, AutomationRule] = {}
        self.workflows: Dict[str, AutomationWorkflow] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}
        self.context_providers: List[Callable[[], Dict[str, Any]]] = []
        self.action_handlers: Dict[AutomationAction, Callable] = {}
        self.engine_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Dependencies
        self.distributor: Optional[PlatformDistributor] = None
        self.aggregator: Optional[PlatformAggregator] = None
        self.monitor: Optional[PlatformMonitor] = None
        self.scheduler: Optional[PlatformScheduler] = None
        
        self._setup_default_handlers()
    
    def set_dependencies(
        self,
        distributor: PlatformDistributor = None,
        aggregator: PlatformAggregator = None,
        monitor: PlatformMonitor = None,
        scheduler: PlatformScheduler = None
    ):
        """Set system dependencies"""        self.distributor = distributor
        self.aggregator = aggregator
        self.monitor = monitor
        self.scheduler = scheduler
    
    def _setup_default_handlers(self):
        """Setup default action handlers"""        self.action_handlers.update({
            AutomationAction.DISTRIBUTE_CONTENT: self._handle_distribute_content,
            AutomationAction.SEND_NOTIFICATION: self._handle_send_notification,
            AutomationAction.UPDATE_SETTINGS: self._handle_update_settings,
            AutomationAction.TRIGGER_BACKUP: self._handle_trigger_backup,
            AutomationAction.SCALE_RESOURCES: self._handle_scale_resources,
            AutomationAction.EXECUTE_FUNCTION: self._handle_execute_function,
            AutomationAction.SEND_ALERT: self._handle_send_alert,
            AutomationAction.PAUSE_OPERATIONS: self._handle_pause_operations
        })
    
    def add_rule(
        self,
        name: str,
        description: str,
        trigger: AutomationTrigger,
        conditions: List[AutomationCondition],
        actions: List[Dict[str, Any]],
        priority: int = 1
    ) -> str:
        """Add automation rule"""        rule_id = str(uuid.uuid4())
        
        rule = AutomationRule(
            rule_id=rule_id,
            name=name,
            description=description,
            trigger=trigger,
            conditions=conditions,
            actions=actions,
            priority=priority
        )
        
        self.rules[rule_id] = rule
        logger.info(f"Added automation rule: {name} ({rule_id})")
        
        return rule_id
    
    def add_workflow(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep],
        trigger_rules: List[str] = None
    ) -> str:
        """Add automation workflow"""        workflow_id = str(uuid.uuid4())
        
        workflow = AutomationWorkflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=steps,
            trigger_rules=trigger_rules or []
        )
        
        self.workflows[workflow_id] = workflow
        logger.info(f"Added automation workflow: {name} ({workflow_id})")
        
        return workflow_id
    
    def add_context_provider(self, provider: Callable[[], Dict[str, Any]]):
        """Add context provider function"""        self.context_providers.append(provider)
    
    def register_action_handler(self, action: AutomationAction, handler: Callable):
        """Register custom action handler"""        self.action_handlers[action] = handler
    
    async def get_automation_context(self) -> Dict[str, Any]:
        """Gather context from all providers"""        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'platforms': {},
            'system': {}
        }
        
        # Call all context providers
        for provider in self.context_providers:
            try:
                provider_context = provider()
                if isinstance(provider_context, dict):
                    context.update(provider_context)
            except Exception as e:
                logger.error(f"Error getting context from provider: {e}")
        
        # Add system metrics if available
        if self.monitor:
            try:
                system_overview = await self.monitor.get_system_overview()
                context['system'].update(system_overview)
            except Exception as e:
                logger.error(f"Error getting system overview: {e}")
        
        return context
    
    async def evaluate_rules(self, trigger_type: AutomationTrigger = None) -> List[AutomationRule]:
        """Evaluate rules and return those that should execute"""        context = await self.get_automation_context()
        triggered_rules = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if trigger_type and rule.trigger != trigger_type:
                continue
            
            if rule.should_execute(context):
                triggered_rules.append(rule)
        
        # Sort by priority
        triggered_rules.sort(key=lambda r: r.priority, reverse=True)
        return triggered_rules
    
    async def execute_rule(self, rule: AutomationRule) -> Dict[str, Any]:
        """Execute automation rule"""        rule.execution_count += 1
        rule.last_execution = datetime.utcnow()
        
        results = []
        
        try:
            for action_config in rule.actions:
                action_type = AutomationAction(action_config['type'])
                parameters = action_config.get('parameters', {})
                
                handler = self.action_handlers.get(action_type)
                if not handler:
                    raise Exception(f"No handler for action type: {action_type}")
                
                result = await handler(parameters)
                results.append({
                    'action_type': action_type.value,
                    'success': True,
                    'result': result
                })
            
            rule.last_result = {
                'success': True,
                'actions_executed': len(results),
                'results': results
            }
            
            logger.info(f"Successfully executed rule: {rule.name}")
            return rule.last_result
            
        except Exception as e:
            error_msg = str(e)
            rule.last_result = {
                'success': False,
                'error': error_msg,
                'actions_executed': len(results)
            }
            
            logger.error(f"Rule execution failed: {rule.name} - {error_msg}")
            return rule.last_result
    
    async def execute_workflow(self, workflow: AutomationWorkflow) -> Dict[str, Any]:
        """Execute automation workflow"""        workflow.status = WorkflowStatus.ACTIVE
        workflow.started_at = datetime.utcnow()
        workflow.execution_count += 1
        
        try:
            while not workflow.is_complete() and not workflow.has_failed():
                next_steps = workflow.get_next_steps()
                
                if not next_steps:
                    # No more steps ready, check if we're stuck
                    if not any(step.status == WorkflowStatus.ACTIVE for step in workflow.steps):
                        break  # Workflow is stuck
                    
                    # Wait for running steps
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready steps in parallel
                step_tasks = []
                for step in next_steps:
                    step.status = WorkflowStatus.ACTIVE
                    step.started_at = datetime.utcnow()
                    workflow.current_step = step.step_id
                    
                    task = asyncio.create_task(self._execute_workflow_step(step))
                    step_tasks.append((step, task))
                
                # Wait for steps to complete
                for step, task in step_tasks:
                    try:
                        result = await task
                        step.status = WorkflowStatus.COMPLETED
                        step.completed_at = datetime.utcnow()
                        step.result = result
                    except Exception as e:
                        step.status = WorkflowStatus.FAILED
                        step.completed_at = datetime.utcnow()
                        step.error = str(e)
                        logger.error(f"Workflow step failed: {step.name} - {e}")
            
            # Determine final status
            if workflow.is_complete():
                workflow.status = WorkflowStatus.COMPLETED
            elif workflow.has_failed():
                workflow.status = WorkflowStatus.FAILED
            else:
                workflow.status = WorkflowStatus.PAUSED  # Stuck or paused
            
            workflow.completed_at = datetime.utcnow()
            
            return {
                'workflow_id': workflow.workflow_id,
                'status': workflow.status.value,
                'completed_steps': len([s for s in workflow.steps if s.status == WorkflowStatus.COMPLETED]),
                'total_steps': len(workflow.steps),
                'execution_time': (workflow.completed_at - workflow.started_at).total_seconds()
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            logger.error(f"Workflow execution failed: {workflow.name} - {e}")
            
            return {
                'workflow_id': workflow.workflow_id,
                'status': workflow.status.value,
                'error': str(e)
            }
    
    async def _execute_workflow_step(self, step: WorkflowStep) -> Any:
        """Execute single workflow step"""        handler = self.action_handlers.get(step.action_type)
        if not handler:
            raise Exception(f"No handler for action type: {step.action_type}")
        
        return await handler(step.parameters)
    
    # Default action handlers
    async def _handle_distribute_content(self, parameters: Dict[str, Any]) -> Any:
        """Handle content distribution action"""        if not self.distributor:
            raise Exception("Content distributor not available")
        
        # Extract parameters
        content_path = parameters.get('content_path')
        metadata = parameters.get('metadata')
        platform_targets = parameters.get('platform_targets', [])
        strategy = parameters.get('strategy', DistributionStrategy.SMART_ROUTING)
        
        if not content_path or not metadata:
            raise Exception("Missing required parameters: content_path, metadata")
        
        # Convert metadata if needed
        if isinstance(metadata, dict):
            metadata = ContentMetadata(**metadata)
        
        # Convert targets format
        targets = [{'platform_id': pid, 'priority': 1} for pid in platform_targets]
        
        result = await self.distributor.distribute_content(
            task_id=f"automation_{uuid.uuid4()}",
            content_path=content_path,
            metadata=metadata,
            platform_targets=targets,
            strategy=strategy
        )
        
        return result
    
    async def _handle_send_notification(self, parameters: Dict[str, Any]) -> Any:
        """Handle send notification action"""        message = parameters.get('message', 'Automation notification')
        recipients = parameters.get('recipients', [])
        
        # This would integrate with notification system
        logger.info(f"Notification sent: {message} to {len(recipients)} recipients")
        
        return {'message': message, 'recipients_count': len(recipients)}
    
    async def _handle_update_settings(self, parameters: Dict[str, Any]) -> Any:
        """Handle update settings action"""        settings = parameters.get('settings', {})
        platform_id = parameters.get('platform_id')
        
        # This would update platform or system settings
        logger.info(f"Settings updated for {platform_id}: {settings}")
        
        return {'platform_id': platform_id, 'updated_settings': settings}
    
    async def _handle_trigger_backup(self, parameters: Dict[str, Any]) -> Any:
        """Handle trigger backup action"""        backup_type = parameters.get('backup_type', 'full')
        platforms = parameters.get('platforms', [])
        
        # This would trigger backup process
        logger.info(f"Backup triggered: {backup_type} for {len(platforms)} platforms")
        
        return {'backup_type': backup_type, 'platforms_count': len(platforms)}
    
    async def _handle_scale_resources(self, parameters: Dict[str, Any]) -> Any:
        """Handle scale resources action"""        scale_direction = parameters.get('direction', 'up')  # up/down
        resource_type = parameters.get('resource_type', 'compute')
        
        # This would scale system resources
        logger.info(f"Resource scaling: {scale_direction} for {resource_type}")
        
        return {'direction': scale_direction, 'resource_type': resource_type}
    
    async def _handle_execute_function(self, parameters: Dict[str, Any]) -> Any:
        """Handle execute function action"""        function_name = parameters.get('function_name')
        function_args = parameters.get('args', [])
        function_kwargs = parameters.get('kwargs', {})
        
        if not function_name:
            raise Exception("Function name required")
        
        # This would execute a registered function
        logger.info(f"Function executed: {function_name}")
        
        return {'function_name': function_name, 'executed': True}
    
    async def _handle_send_alert(self, parameters: Dict[str, Any]) -> Any:
        """Handle send alert action"""        alert_type = parameters.get('alert_type', 'info')
        message = parameters.get('message', 'Automation alert')
        
        if self.monitor:
            # Send through monitor system
            pass
        
        logger.warning(f"Alert sent: {alert_type} - {message}")
        
        return {'alert_type': alert_type, 'message': message}
    
    async def _handle_pause_operations(self, parameters: Dict[str, Any]) -> Any:
        """Handle pause operations action"""        platform_ids = parameters.get('platform_ids', [])
        duration_minutes = parameters.get('duration_minutes', 30)
        
        # This would pause platform operations
        logger.info(f"Operations paused for {len(platform_ids)} platforms for {duration_minutes} minutes")
        
        return {'paused_platforms': len(platform_ids), 'duration_minutes': duration_minutes}
    
    async def start(self):
        """Start automation engine"""        if self.engine_active:
            logger.warning("Automation engine already active")
            return
        
        self.engine_active = True
        self.monitor_task = asyncio.create_task(self._automation_loop())
        logger.info("Automation engine started")
    
    async def stop(self):
        """Stop automation engine"""        if not self.engine_active:
            return
        
        self.engine_active = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        # Cancel running workflows
        for workflow_task in self.running_workflows.values():
            workflow_task.cancel()
        
        self.running_workflows.clear()
        logger.info("Automation engine stopped")
    
    async def _automation_loop(self):
        """Main automation monitoring loop"""        try:
            while self.engine_active:
                try:
                    # Evaluate time-based triggers
                    triggered_rules = await self.evaluate_rules(AutomationTrigger.TIME_BASED)
                    
                    # Execute triggered rules
                    for rule in triggered_rules:
                        try:
                            await self.execute_rule(rule)
                        except Exception as e:
                            logger.error(f"Error executing rule {rule.name}: {e}")
                    
                    # Check for triggered workflows
                    for rule in triggered_rules:
                        for workflow_id in self.workflows:
                            workflow = self.workflows[workflow_id]
                            if (rule.rule_id in workflow.trigger_rules and 
                                workflow.status == WorkflowStatus.INACTIVE and
                                workflow_id not in self.running_workflows):
                                
                                # Start workflow
                                workflow_task = asyncio.create_task(
                                    self.execute_workflow(workflow)
                                )
                                self.running_workflows[workflow_id] = workflow_task
                    
                    # Clean up completed workflows
                    completed_workflows = [
                        wf_id for wf_id, task in self.running_workflows.items()
                        if task.done()
                    ]
                    
                    for wf_id in completed_workflows:
                        del self.running_workflows[wf_id]
                    
                except Exception as e:
                    logger.error(f"Automation loop error: {e}")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            logger.info("Automation loop cancelled")
        except Exception as e:
            logger.error(f"Automation loop fatal error: {e}")
            self.engine_active = False
    
    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation engine statistics"""        return {
            'engine_active': self.engine_active,
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
            'total_workflows': len(self.workflows),
            'active_workflows': len(self.running_workflows),
            'context_providers': len(self.context_providers),
            'action_handlers': len(self.action_handlers),
            'rules_executed': sum(r.execution_count for r in self.rules.values()),
            'workflows_executed': sum(w.execution_count for w in self.workflows.values())
        }


# Global automation engine instance
_global_engine: Optional[AutomationEngine] = None


def get_automation_engine() -> AutomationEngine:
    """Get global automation engine instance"""    global _global_engine
    
    if _global_engine is None:
        _global_engine = AutomationEngine()
    
    return _global_engine


async def start_automation():
    """Start global automation engine"""    engine = get_automation_engine()
    await engine.start()


async def stop_automation():
    """Stop global automation engine"""    global _global_engine
    
    if _global_engine:
        await _global_engine.stop()
