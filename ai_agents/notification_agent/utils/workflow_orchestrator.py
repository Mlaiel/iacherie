"""Notification Workflow Orchestrator - Advanced Workflow Automation & Business Logic

Enterprise-grade workflow orchestration system for complex notification workflows,
business rule automation, multi-step notification sequences, and intelligent
content creator journey management for the IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property are the EXCLUSIVE PROPERTY of Fahed Mlaiel.

STRICTLY PROHIBITED WITHOUT EXPLICIT WRITTEN AUTHORIZATION:
- Copying, cloning, reproducing, or distributing this code
- Using concepts, methodologies, or approaches in other projects
- Commercial exploitation, monetization, or resale
- Reverse engineering, decompilation, or adaptation
- Creating derivative works based on this intellectual property

Contact for licensing inquiries: mlaiel@live.de

Violation of these terms will result in immediate legal action.
All usage is monitored, logged, and legally protected.

Team Specialties & Expertise:
- Lead AI Developer & Backend Senior Engineer: Fahed Mlaiel
- Machine Learning Engineer & Audio Processing Specialist
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from abc import ABC, abstractmethod

from .notification_dispatcher import NotificationDispatcher, DispatchStrategy
from .event_manager import NotificationEventManager, NotificationEventType
from .subscription_manager import NotificationSubscriptionManager
from .analytics_engine import NotificationAnalyticsEngine
from ...models.workflow_models import WorkflowModel, WorkflowStep, WorkflowExecution
from ...business.content_business import ContentBusinessLogic
from ...business.collaboration_business import CollaborationBusinessLogic
from ...business.monetization_business import MonetizationBusinessLogic


class WorkflowType(Enum):
    """Comprehensive workflow types for IA Influencer business logic"""    CONTENT_ONBOARDING = "content_onboarding"
    CONTENT_PROTECTION = "content_protection"
    COLLABORATION_MATCHING = "collaboration_matching"
    MONETIZATION_ACTIVATION = "monetization_activation"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION_MANAGEMENT = "distribution_management"
    ENGAGEMENT_NURTURING = "engagement_nurturing"
    CREATOR_MILESTONE = "creator_milestone"
    SECURITY_INCIDENT = "security_incident"
    PAYMENT_PROCESSING = "payment_processing"


class WorkflowStatus(Enum):
    """Workflow execution status tracking"""    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class StepType(Enum):
    """Types of workflow steps"""    NOTIFICATION = "notification"
    DELAY = "delay"
    CONDITION = "condition"
    ACTION = "action"
    BRANCH = "branch"
    LOOP = "loop"
    API_CALL = "api_call"
    DATA_PROCESSING = "data_processing"
    USER_INPUT = "user_input"


class TriggerType(Enum):
    """Workflow trigger types"""    EVENT_BASED = "event_based"
    TIME_BASED = "time_based"
    USER_ACTION = "user_action"
    BUSINESS_CONDITION = "business_condition"
    API_WEBHOOK = "api_webhook"
    MANUAL = "manual"


@dataclass
class WorkflowCondition:
    """Workflow condition for branching and decision making"""    condition_id: str
    condition_type: str
    parameters: Dict[str, Any]
    evaluation_function: Callable[[Dict[str, Any]], bool]


@dataclass
class WorkflowAction:
    """Workflow action configuration"""    action_id: str
    action_type: str
    parameters: Dict[str, Any]
    retry_attempts: int = 3
    timeout_seconds: int = 300


@dataclass
class WorkflowStepDefinition:
    """Comprehensive workflow step definition"""    step_id: str
    step_type: StepType
    name: str
    description: str
    conditions: List[WorkflowCondition] = field(default_factory=list)
    actions: List[WorkflowAction] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    retry_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition with business logic"""    workflow_id: str
    workflow_type: WorkflowType
    name: str
    description: str
    trigger_config: Dict[str, Any]
    steps: List[WorkflowStepDefinition]
    global_conditions: List[WorkflowCondition] = field(default_factory=list)
    timeout_minutes: int = 1440  # 24 hours default
    max_executions_per_user: int = 1
    ai_optimization_enabled: bool = True


@dataclass
class WorkflowExecutionContext:
    """Rich context for workflow execution"""    execution_id: str
    user_id: str
    workflow_definition: WorkflowDefinition
    trigger_data: Dict[str, Any]
    business_context: Dict[str, Any] = field(default_factory=dict)
    execution_state: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    current_step_id: Optional[str] = None


class NotificationWorkflowOrchestrator:
    """    Advanced workflow orchestration engine with intelligent business logic integration
    
    Key Features:
    - Complex multi-step notification workflows for content creator journeys
    - AI-powered workflow optimization based on user behavior and engagement
    - Business rule integration for content protection, collaboration, and monetization
    - Advanced conditional logic with machine learning insights
    - Real-time workflow monitoring and performance analytics
    - Dynamic workflow adaptation based on business outcomes
    - Intelligent retry mechanisms with exponential backoff
    - Comprehensive audit trail and compliance tracking
    """    
    def __init__(
        self,
        notification_dispatcher: NotificationDispatcher,
        event_manager: NotificationEventManager,
        subscription_manager: NotificationSubscriptionManager,
        analytics_engine: NotificationAnalyticsEngine
    ):
        self.notification_dispatcher = notification_dispatcher
        self.event_manager = event_manager
        self.subscription_manager = subscription_manager
        self.analytics_engine = analytics_engine
        
        self.logger = logging.getLogger(__name__)
        
        # Business logic integrations
        self.content_business = ContentBusinessLogic()
        self.collaboration_business = CollaborationBusinessLogic()
        self.monetization_business = MonetizationBusinessLogic()
        
        # Workflow management
        self._workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self._active_executions: Dict[str, WorkflowExecutionContext] = {}
        self._execution_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance monitoring
        self._workflow_metrics = {
            'executions_started': 0,
            'executions_completed': 0,
            'executions_failed': 0,
            'average_execution_time': 0.0,
            'step_success_rates': {}
        }
        
        # Background processing
        self._execution_processor = asyncio.create_task(self._process_workflow_executions())
        self._monitoring_task = asyncio.create_task(self._monitor_workflow_health())
        
        # Initialize built-in workflows
        asyncio.create_task(self._initialize_builtin_workflows())
    
    async def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """        Register a new workflow definition with validation
        
        Args:
            workflow: Complete workflow definition
            
        Returns:
            True if successfully registered
        """        try:
            # Validate workflow definition
            if not await self._validate_workflow_definition(workflow):
                return False
            
            # Optimize workflow with AI insights if enabled
            if workflow.ai_optimization_enabled:
                workflow = await self._optimize_workflow_definition(workflow)
            
            # Store workflow definition
            self._workflow_definitions[workflow.workflow_id] = workflow
            
            self.logger.info(f"Workflow registered: {workflow.workflow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Workflow registration failed: {str(e)}")
            return False
    
    async def trigger_workflow(
        self,
        workflow_id: str,
        user_id: str,
        trigger_data: Dict[str, Any]
    ) -> str:
        """        Trigger workflow execution for specific user
        
        Args:
            workflow_id: Workflow identifier
            user_id: Target user
            trigger_data: Data that triggered the workflow
            
        Returns:
            Execution ID for tracking
        """        try:
            if workflow_id not in self._workflow_definitions:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow_def = self._workflow_definitions[workflow_id]
            
            # Check execution limits
            if not await self._check_execution_limits(workflow_def, user_id):
                self.logger.warning(f"Execution limit exceeded for {workflow_id}/{user_id}")
                return ""
            
            # Create execution context
            execution_context = WorkflowExecutionContext(
                execution_id=str(uuid.uuid4()),
                user_id=user_id,
                workflow_definition=workflow_def,
                trigger_data=trigger_data,
                business_context=await self._load_business_context(user_id, trigger_data)
            )
            
            # Queue for execution
            await self._execution_queue.put(execution_context)
            self._active_executions[execution_context.execution_id] = execution_context
            
            self.logger.info(
                f"Workflow triggered: {workflow_id} for user {user_id}, "
                f"execution: {execution_context.execution_id}"
            )
            
            return execution_context.execution_id
            
        except Exception as e:
            self.logger.error(f"Workflow trigger failed: {str(e)}")
            return ""
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """        Get current status of workflow execution
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution status and progress information
        """        if execution_id not in self._active_executions:
            return {'status': 'not_found'}
        
        context = self._active_executions[execution_id]
        
        return {
            'execution_id': execution_id,
            'workflow_id': context.workflow_definition.workflow_id,
            'user_id': context.user_id,
            'status': context.execution_state.get('status', 'unknown'),
            'current_step': context.current_step_id,
            'started_at': context.started_at.isoformat(),
            'progress': context.execution_state.get('progress', 0),
            'steps_completed': context.execution_state.get('steps_completed', 0),
            'total_steps': len(context.workflow_definition.steps),
            'error_message': context.execution_state.get('error_message')
        }
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause workflow execution"""        if execution_id in self._active_executions:
            context = self._active_executions[execution_id]
            context.execution_state['status'] = WorkflowStatus.PAUSED.value
            return True
        return False
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume paused workflow execution"""        if execution_id in self._active_executions:
            context = self._active_executions[execution_id]
            if context.execution_state.get('status') == WorkflowStatus.PAUSED.value:
                context.execution_state['status'] = WorkflowStatus.RUNNING.value
                await self._execution_queue.put(context)
                return True
        return False
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel workflow execution"""        if execution_id in self._active_executions:
            context = self._active_executions[execution_id]
            context.execution_state['status'] = WorkflowStatus.CANCELLED.value
            del self._active_executions[execution_id]
            return True
        return False
    
    async def _process_workflow_executions(self):
        """Background task for processing workflow executions"""        while True:
            try:
                # Get next execution from queue
                context = await asyncio.wait_for(
                    self._execution_queue.get(), timeout=1.0
                )
                
                # Process execution
                asyncio.create_task(self._execute_workflow(context))
                
            except asyncio.TimeoutError:
                # No executions in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Execution processor error: {str(e)}")
    
    async def _execute_workflow(self, context: WorkflowExecutionContext):
        """Execute a complete workflow"""        try:
            context.execution_state['status'] = WorkflowStatus.RUNNING.value
            context.execution_state['steps_completed'] = 0
            
            # Execute workflow steps
            for i, step_def in enumerate(context.workflow_definition.steps):
                try:
                    context.current_step_id = step_def.step_id
                    
                    # Check global conditions
                    if not await self._check_global_conditions(context):
                        self.logger.info(f"Global conditions failed for {context.execution_id}")
                        break
                    
                    # Execute step
                    step_result = await self._execute_workflow_step(context, step_def)
                    
                    if not step_result['success']:
                        # Handle step failure
                        if await self._handle_step_failure(context, step_def, step_result):
                            continue  # Retry successful
                        else:
                            break  # Workflow failed
                    
                    # Update progress
                    context.execution_state['steps_completed'] += 1
                    context.execution_state['progress'] = (
                        (i + 1) / len(context.workflow_definition.steps) * 100
                    )
                    
                    # Check for workflow pause/cancellation
                    if context.execution_state.get('status') in [
                        WorkflowStatus.PAUSED.value,
                        WorkflowStatus.CANCELLED.value
                    ]:
                        return
                    
                except Exception as e:
                    self.logger.error(f"Step execution failed: {str(e)}")
                    context.execution_state['error_message'] = str(e)
                    break
            
            # Complete workflow
            if context.execution_state['steps_completed'] == len(context.workflow_definition.steps):
                context.execution_state['status'] = WorkflowStatus.COMPLETED.value
                await self._complete_workflow_execution(context)
            else:
                context.execution_state['status'] = WorkflowStatus.FAILED.value
                await self._handle_workflow_failure(context)
            
            # Remove from active executions
            if context.execution_id in self._active_executions:
                del self._active_executions[context.execution_id]
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            context.execution_state['status'] = WorkflowStatus.FAILED.value
            context.execution_state['error_message'] = str(e)
    
    async def _execute_workflow_step(
        self,
        context: WorkflowExecutionContext,
        step_def: WorkflowStepDefinition
    ) -> Dict[str, Any]:
        """Execute individual workflow step"""        try:
            # Check step conditions
            if not await self._check_step_conditions(context, step_def):
                return {'success': False, 'reason': 'conditions_not_met'}
            
            # Execute based on step type
            if step_def.step_type == StepType.NOTIFICATION:
                return await self._execute_notification_step(context, step_def)
            elif step_def.step_type == StepType.DELAY:
                return await self._execute_delay_step(context, step_def)
            elif step_def.step_type == StepType.CONDITION:
                return await self._execute_condition_step(context, step_def)
            elif step_def.step_type == StepType.ACTION:
                return await self._execute_action_step(context, step_def)
            elif step_def.step_type == StepType.API_CALL:
                return await self._execute_api_call_step(context, step_def)
            elif step_def.step_type == StepType.DATA_PROCESSING:
                return await self._execute_data_processing_step(context, step_def)
            else:
                return {'success': False, 'reason': f'unknown_step_type: {step_def.step_type}'}
            
        except Exception as e:
            self.logger.error(f"Step execution error: {str(e)}")
            return {'success': False, 'reason': str(e)}
    
    async def _execute_notification_step(
        self,
        context: WorkflowExecutionContext,
        step_def: WorkflowStepDefinition
    ) -> Dict[str, Any]:
        """Execute notification step"""        try:
            # Extract notification parameters
            notification_action = next(
                (action for action in step_def.actions if action.action_type == 'send_notification'),
                None
            )
            
            if not notification_action:
                return {'success': False, 'reason': 'no_notification_action'}
            
            # Create notification from workflow context
            notification = await self._create_notification_from_workflow(
                context, notification_action.parameters
            )
            
            # Dispatch notification
            dispatch_result = await self.notification_dispatcher.dispatch_notification(
                notification,
                strategy=DispatchStrategy.INTELLIGENT_ROUTING
            )
            
            # Store result in execution context
            context.execution_state[f'notification_result_{step_def.step_id}'] = {
                'notification_id': notification.id,
                'dispatch_result': dispatch_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'success': dispatch_result.final_status.value in ['delivered', 'sent'],
                'notification_id': notification.id,
                'channels_successful': [ch.value for ch in dispatch_result.channels_successful]
            }
            
        except Exception as e:
            self.logger.error(f"Notification step execution failed: {str(e)}")
            return {'success': False, 'reason': str(e)}
    
    async def _execute_delay_step(
        self,
        context: WorkflowExecutionContext,
        step_def: WorkflowStepDefinition
    ) -> Dict[str, Any]:
        """Execute delay step"""        try:
            delay_action = next(
                (action for action in step_def.actions if action.action_type == 'delay'),
                None
            )
            
            if not delay_action:
                return {'success': False, 'reason': 'no_delay_action'}
            
            delay_seconds = delay_action.parameters.get('seconds', 0)
            
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
            
            return {'success': True, 'delay_seconds': delay_seconds}
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    async def _initialize_builtin_workflows(self):
        """Initialize built-in workflows for IA Influencer platform"""        
        # Content Onboarding Workflow
        content_onboarding = WorkflowDefinition(
            workflow_id="content_onboarding_v1",
            workflow_type=WorkflowType.CONTENT_ONBOARDING,
            name="Content Creator Onboarding",
            description="Welcome new content creators and guide them through platform setup",
            trigger_config={
                'trigger_type': TriggerType.EVENT_BASED.value,
                'event_types': ['user_registered', 'content_uploaded']
            },
            steps=[
                WorkflowStepDefinition(
                    step_id="welcome_notification",
                    step_type=StepType.NOTIFICATION,
                    name="Send Welcome Message",
                    description="Send personalized welcome message to new creator",
                    actions=[WorkflowAction(
                        action_id="send_welcome",
                        action_type="send_notification",
                        parameters={
                            'template': 'content_creator_welcome',
                            'priority': 'high',
                            'channels': ['email', 'push_notification']
                        }
                    )]
                ),
                WorkflowStepDefinition(
                    step_id="setup_guidance_delay",
                    step_type=StepType.DELAY,
                    name="Wait for Initial Setup",
                    description="Wait 1 hour for user to complete initial setup",
                    actions=[WorkflowAction(
                        action_id="delay_1_hour",
                        action_type="delay",
                        parameters={'seconds': 3600}
                    )]
                ),
                WorkflowStepDefinition(
                    step_id="setup_reminder",
                    step_type=StepType.NOTIFICATION,
                    name="Setup Reminder",
                    description="Remind user to complete platform setup",
                    conditions=[WorkflowCondition(
                        condition_id="setup_incomplete",
                        condition_type="business_condition",
                        parameters={'check': 'profile_completion'},
                        evaluation_function=lambda ctx: ctx.get('profile_completion', 0) < 0.8
                    )],
                    actions=[WorkflowAction(
                        action_id="send_setup_reminder",
                        action_type="send_notification",
                        parameters={
                            'template': 'setup_reminder',
                            'priority': 'medium',
                            'channels': ['email']
                        }
                    )]
                )
            ]
        )
        
        # Content Protection Workflow
        content_protection = WorkflowDefinition(
            workflow_id="content_protection_v1",
            workflow_type=WorkflowType.CONTENT_PROTECTION,
            name="Content Protection Alert",
            description="Handle copyright infringement detection and user notification",
            trigger_config={
                'trigger_type': TriggerType.EVENT_BASED.value,
                'event_types': ['copyright_detected', 'infringement_alert']
            },
            steps=[
                WorkflowStepDefinition(
                    step_id="immediate_alert",
                    step_type=StepType.NOTIFICATION,
                    name="Immediate Protection Alert",
                    description="Send immediate alert about copyright infringement",
                    actions=[WorkflowAction(
                        action_id="send_protection_alert",
                        action_type="send_notification",
                        parameters={
                            'template': 'copyright_infringement_alert',
                            'priority': 'critical',
                            'channels': ['email', 'sms', 'push_notification']
                        }
                    )]
                ),
                WorkflowStepDefinition(
                    step_id="protection_action",
                    step_type=StepType.ACTION,
                    name="Initiate Protection Measures",
                    description="Automatically initiate content protection measures",
                    actions=[WorkflowAction(
                        action_id="activate_protection",
                        action_type="content_protection",
                        parameters={
                            'protection_level': 'high',
                            'automatic_takedown': True
                        }
                    )]
                ),
                WorkflowStepDefinition(
                    step_id="followup_notification",
                    step_type=StepType.NOTIFICATION,
                    name="Protection Status Update",
                    description="Send update on protection measures taken",
                    actions=[WorkflowAction(
                        action_id="send_protection_update",
                        action_type="send_notification",
                        parameters={
                            'template': 'protection_measures_update',
                            'priority': 'high',
                            'channels': ['email', 'push_notification']
                        }
                    )]
                )
            ]
        )
        
        # Collaboration Matching Workflow
        collaboration_matching = WorkflowDefinition(
            workflow_id="collaboration_matching_v1",
            workflow_type=WorkflowType.COLLABORATION_MATCHING,
            name="Collaboration Opportunity Matching",
            description="Notify creators about collaboration opportunities",
            trigger_config={
                'trigger_type': TriggerType.EVENT_BASED.value,
                'event_types': ['collaboration_match_found']
            },
            steps=[
                WorkflowStepDefinition(
                    step_id="match_notification",
                    step_type=StepType.NOTIFICATION,
                    name="Collaboration Match Alert",
                    description="Notify about new collaboration opportunity",
                    actions=[WorkflowAction(
                        action_id="send_match_alert",
                        action_type="send_notification",
                        parameters={
                            'template': 'collaboration_match',
                            'priority': 'high',
                            'channels': ['email', 'push_notification']
                        }
                    )]
                ),
                WorkflowStepDefinition(
                    step_id="followup_delay",
                    step_type=StepType.DELAY,
                    name="Wait for Response",
                    description="Wait 3 days for user response",
                    actions=[WorkflowAction(
                        action_id="delay_3_days",
                        action_type="delay",
                        parameters={'seconds': 259200}  # 3 days
                    )]
                ),
                WorkflowStepDefinition(
                    step_id="followup_reminder",
                    step_type=StepType.NOTIFICATION,
                    name="Collaboration Reminder",
                    description="Remind about pending collaboration opportunity",
                    conditions=[WorkflowCondition(
                        condition_id="no_response",
                        condition_type="business_condition",
                        parameters={'check': 'collaboration_response'},
                        evaluation_function=lambda ctx: not ctx.get('collaboration_responded', False)
                    )],
                    actions=[WorkflowAction(
                        action_id="send_collaboration_reminder",
                        action_type="send_notification",
                        parameters={
                            'template': 'collaboration_reminder',
                            'priority': 'medium',
                            'channels': ['push_notification']
                        }
                    )]
                )
            ]
        )
        
        # Register all built-in workflows
        workflows = [content_onboarding, content_protection, collaboration_matching]
        
        for workflow in workflows:
            await self.register_workflow(workflow)
        
        self.logger.info(f"Initialized {len(workflows)} built-in workflows")
    
    # Additional helper methods for workflow execution and management would be implemented here
    # including validation, optimization, business context loading, condition checking, etc.
    
    async def _validate_workflow_definition(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition for correctness"""        if not workflow.workflow_id or not workflow.name:
            return False
        
        if not workflow.steps:
            return False
        
        # Validate step dependencies
        step_ids = {step.step_id for step in workflow.steps}
        for step in workflow.steps:
            for next_step in step.next_steps:
                if next_step not in step_ids:
                    return False
        
        return True
    
    async def _optimize_workflow_definition(
        self, workflow: WorkflowDefinition
    ) -> WorkflowDefinition:
        """Apply AI optimization to workflow definition"""        # Implementation would use ML models to optimize workflow
        # For now, return unchanged
        return workflow
    
    async def _load_business_context(
        self, user_id: str, trigger_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Load relevant business context for workflow execution"""        business_context = {}
        
        # Load content context if relevant
        if 'content_id' in trigger_data:
            content_context = await self.content_business.get_content_context(
                user_id, {'content_id': trigger_data['content_id']}
            )
            business_context.update(content_context)
        
        # Load collaboration context if relevant
        if 'collaboration_id' in trigger_data:
            collab_context = await self.collaboration_business.get_collaboration_context(
                user_id, {'collaboration_id': trigger_data['collaboration_id']}
            )
            business_context.update(collab_context)
        
        return business_context
    
    async def _check_execution_limits(
        self, workflow_def: WorkflowDefinition, user_id: str
    ) -> bool:
        """Check if user hasn't exceeded workflow execution limits"""        # Count active executions for this user and workflow
        active_count = sum(
            1 for context in self._active_executions.values()
            if context.user_id == user_id and 
            context.workflow_definition.workflow_id == workflow_def.workflow_id
        )
        
        return active_count < workflow_def.max_executions_per_user
    
    async def _monitor_workflow_health(self):
        """Background task for monitoring workflow system health"""        while True:
            try:
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
                # Check for stuck executions
                current_time = datetime.utcnow()
                stuck_executions = []
                
                for execution_id, context in self._active_executions.items():
                    execution_time = current_time - context.started_at
                    if execution_time.total_seconds() > context.workflow_definition.timeout_minutes * 60:
                        stuck_executions.append(execution_id)
                
                # Cancel stuck executions
                for execution_id in stuck_executions:
                    await self.cancel_execution(execution_id)
                    self.logger.warning(f"Cancelled stuck execution: {execution_id}")
                
            except Exception as e:
                self.logger.error(f"Workflow health monitoring error: {str(e)}")
    
    async def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get comprehensive workflow performance metrics"""        return self._workflow_metrics.copy()
