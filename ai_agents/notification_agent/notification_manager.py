"""
Advanced Notification Manager - Comprehensive Notification Orchestration System

This module provides sophisticated notification management capabilities for the IA Influencer Agent platform,
handling complex notification workflows, scheduling, templating, and delivery orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import heapq
from collections import defaultdict

from ...models.notification_models import (
    NotificationModel, NotificationStatus, NotificationPriority,
    NotificationChannel, NotificationTemplate, AlertModel,
    NotificationRule, NotificationSchedule
)
from ...business.notification_business import NotificationBusinessLogic
from ...security.notification_security import NotificationSecurityManager
from ...database.notification_repository import NotificationRepository
from ...monitoring.notification_monitoring import NotificationMonitoringService


class NotificationScheduleType(Enum):
    """Types of notification scheduling"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    RECURRING = "recurring"
    CONDITIONAL = "conditional"
    BATCH_OPTIMIZED = "batch_optimized"


class NotificationWorkflowStatus(Enum):
    """Notification workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NotificationWorkflow:
    """Advanced notification workflow configuration"""
    id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    notification_sequence: List[Dict[str, Any]]
    scheduling_rules: Dict[str, Any]
    success_criteria: Dict[str, Any]
    failure_handling: Dict[str, Any]
    status: NotificationWorkflowStatus = NotificationWorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationAlert:
    """Advanced alert configuration for critical notifications"""
    id: str
    alert_type: str
    severity_level: int
    conditions: Dict[str, Any]
    escalation_rules: List[Dict[str, Any]]
    notification_config: Dict[str, Any]
    auto_resolution: bool = False
    cooldown_period: int = 300  # 5 minutes default


class NotificationManager:
    """
    Advanced notification management system for comprehensive notification orchestration
    
    Features:
    - Intelligent notification scheduling and workflow management
    - Advanced templating with AI-driven personalization
    - Multi-channel delivery optimization and analytics
    - Workflow orchestration with conditional logic
    - Alert management and escalation handling
    - Performance monitoring and optimization
    - Business logic integration for content creators
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.business_logic = NotificationBusinessLogic(config.get('business_config', {}))
        self.security_manager = NotificationSecurityManager(config.get('security_config', {}))
        self.repository = NotificationRepository(config.get('database_config', {}))
        self.monitoring = NotificationMonitoringService(config.get('monitoring_config', {}))
        
        # Workflow management
        self.active_workflows: Dict[str, NotificationWorkflow] = {}
        self.workflow_queue = asyncio.PriorityQueue()
        self.workflow_executor = ThreadPoolExecutor(max_workers=10)
        
        # Scheduling system
        self.scheduler = self._initialize_scheduler()
        self.scheduled_notifications = {}
        self.recurring_schedules = {}
        
        # Alert management
        self.active_alerts: Dict[str, NotificationAlert] = {}
        self.alert_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Template management
        self.template_cache = {}
        self.template_performance = {}
        
        # Performance tracking
        self.performance_metrics = {
            'workflows_executed': 0,
            'alerts_triggered': 0,
            'templates_rendered': 0,
            'average_processing_time': 0.0,
            'success_rate': 0.0
        }
        
    def _initialize_scheduler(self):
        """Initialize advanced scheduling system"""
        from ...infrastructure.notification_scheduler import NotificationScheduler
        return NotificationScheduler(self.config.get('scheduler_config', {}))
        
    async def start_manager(self):
        """Start notification manager with all processing components"""
        try:
            self.logger.info("Starting NotificationManager with advanced capabilities")
            
            # Start core processing tasks
            self.processing_tasks = [
                asyncio.create_task(self._process_workflow_queue()),
                asyncio.create_task(self._monitor_scheduled_notifications()),
                asyncio.create_task(self._process_recurring_schedules()),
                asyncio.create_task(self._monitor_active_alerts()),
                asyncio.create_task(self._optimize_template_performance()),
                asyncio.create_task(self._generate_management_reports())
            ]
            
            # Initialize repository
            await self.repository.initialize()
            
            # Load active workflows
            await self._load_active_workflows()
            
            # Start monitoring
            await self.monitoring.start_monitoring()
            
            self.logger.info("NotificationManager started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start NotificationManager: {str(e)}")
            return False
            
    async def stop_manager(self):
        """Gracefully stop notification manager"""
        try:
            self.logger.info("Stopping NotificationManager")
            
            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()
                
            # Complete active workflows
            await self._complete_active_workflows()
            
            # Stop monitoring
            await self.monitoring.stop_monitoring()
            
            # Close repository
            await self.repository.close()
            
            self.logger.info("NotificationManager stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping NotificationManager: {str(e)}")
            return False
            
    async def create_workflow(
        self,
        workflow_config: Dict[str, Any]
    ) -> str:
        """Create and register a new notification workflow"""
        try:
            # Validate workflow configuration
            if not await self._validate_workflow_config(workflow_config):
                raise ValueError("Invalid workflow configuration")
                
            # Generate workflow ID
            workflow_id = str(uuid.uuid4())
            
            # Create workflow instance
            workflow = NotificationWorkflow(
                id=workflow_id,
                name=workflow_config['name'],
                description=workflow_config.get('description', ''),
                trigger_conditions=workflow_config['trigger_conditions'],
                notification_sequence=workflow_config['notification_sequence'],
                scheduling_rules=workflow_config.get('scheduling_rules', {}),
                success_criteria=workflow_config.get('success_criteria', {}),
                failure_handling=workflow_config.get('failure_handling', {})
            )
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow
            await self.repository.store_workflow(workflow)
            
            # Queue for processing if immediately triggered
            if workflow.trigger_conditions.get('immediate', False):
                await self.workflow_queue.put((1, workflow))
                
            self.logger.info(f"Workflow created successfully: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {str(e)}")
            raise
            
    async def trigger_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Trigger execution of a specific workflow"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                self.logger.error(f"Workflow not found: {workflow_id}")
                return False
                
            # Check trigger conditions
            if not await self._check_trigger_conditions(workflow, context):
                self.logger.info(f"Trigger conditions not met for workflow: {workflow_id}")
                return False
                
            # Add context to workflow
            workflow_with_context = workflow
            workflow_with_context.context = context
            
            # Calculate priority
            priority = await self._calculate_workflow_priority(workflow, context)
            
            # Queue for execution
            await self.workflow_queue.put((priority, workflow_with_context))
            
            self.logger.info(f"Workflow triggered: {workflow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger workflow {workflow_id}: {str(e)}")
            return False
            
    async def schedule_notification(
        self,
        notification_config: Dict[str, Any],
        schedule_type: NotificationScheduleType,
        schedule_params: Dict[str, Any]
    ) -> str:
        """Schedule a notification with advanced scheduling options"""
        try:
            # Generate schedule ID
            schedule_id = str(uuid.uuid4())
            
            # Validate notification and schedule configuration
            if not await self._validate_notification_config(notification_config):
                raise ValueError("Invalid notification configuration")
                
            if not await self._validate_schedule_params(schedule_type, schedule_params):
                raise ValueError("Invalid schedule parameters")
                
            # Create schedule entry
            schedule_entry = {
                'id': schedule_id,
                'notification_config': notification_config,
                'schedule_type': schedule_type,
                'schedule_params': schedule_params,
                'created_at': datetime.utcnow(),
                'status': 'active'
            }
            
            # Handle different schedule types
            if schedule_type == NotificationScheduleType.IMMEDIATE:
                # Process immediately
                await self._process_immediate_notification(notification_config)
                
            elif schedule_type == NotificationScheduleType.DELAYED:
                # Schedule for later execution
                execution_time = datetime.utcnow() + timedelta(
                    seconds=schedule_params.get('delay_seconds', 0)
                )
                self.scheduled_notifications[schedule_id] = {
                    **schedule_entry,
                    'execution_time': execution_time
                }
                
            elif schedule_type == NotificationScheduleType.RECURRING:
                # Set up recurring schedule
                self.recurring_schedules[schedule_id] = schedule_entry
                await self._schedule_next_occurrence(schedule_id)
                
            elif schedule_type == NotificationScheduleType.CONDITIONAL:
                # Set up condition monitoring
                await self._setup_conditional_monitoring(schedule_id, schedule_entry)
                
            elif schedule_type == NotificationScheduleType.BATCH_OPTIMIZED:
                # Add to batch optimization queue
                await self._add_to_batch_queue(schedule_entry)
                
            # Store in repository
            await self.repository.store_schedule(schedule_entry)
            
            self.logger.info(f"Notification scheduled: {schedule_id} ({schedule_type.value})")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule notification: {str(e)}")
            raise
            
    async def create_alert(
        self,
        alert_config: Dict[str, Any]
    ) -> str:
        """Create and register a new alert configuration"""
        try:
            # Generate alert ID
            alert_id = str(uuid.uuid4())
            
            # Validate alert configuration
            if not await self._validate_alert_config(alert_config):
                raise ValueError("Invalid alert configuration")
                
            # Create alert instance
            alert = NotificationAlert(
                id=alert_id,
                alert_type=alert_config['alert_type'],
                severity_level=alert_config['severity_level'],
                conditions=alert_config['conditions'],
                escalation_rules=alert_config.get('escalation_rules', []),
                notification_config=alert_config['notification_config'],
                auto_resolution=alert_config.get('auto_resolution', False),
                cooldown_period=alert_config.get('cooldown_period', 300)
            )
            
            # Register alert
            self.active_alerts[alert_id] = alert
            await self.repository.store_alert(alert)
            
            # Set up monitoring for alert conditions
            await self._setup_alert_monitoring(alert)
            
            self.logger.info(f"Alert created successfully: {alert_id}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {str(e)}")
            raise
            
    async def trigger_alert(
        self,
        alert_id: str,
        trigger_data: Dict[str, Any]
    ) -> bool:
        """Trigger a specific alert with context data"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                self.logger.error(f"Alert not found: {alert_id}")
                return False
                
            # Check cooldown period
            if await self._is_alert_in_cooldown(alert_id):
                self.logger.info(f"Alert in cooldown period: {alert_id}")
                return False
                
            # Validate trigger conditions
            if not await self._validate_alert_trigger(alert, trigger_data):
                self.logger.info(f"Alert trigger conditions not met: {alert_id}")
                return False
                
            # Create alert notification
            alert_notification = await self._create_alert_notification(alert, trigger_data)
            
            # Send immediate notification
            await self._send_alert_notification(alert_notification)
            
            # Handle escalation if configured
            if alert.escalation_rules:
                await self._setup_alert_escalation(alert, trigger_data)
                
            # Record alert in history
            self.alert_history[alert_id].append({
                'triggered_at': datetime.utcnow(),
                'trigger_data': trigger_data,
                'status': 'triggered'
            })
            
            # Update metrics
            self.performance_metrics['alerts_triggered'] += 1
            
            self.logger.info(f"Alert triggered successfully: {alert_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert {alert_id}: {str(e)}")
            return False
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow execution status"""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return {"error": "Workflow not found"}
                
            # Get execution history
            execution_history = await self.repository.get_workflow_history(workflow_id)
            
            # Get performance metrics
            metrics = await self.monitoring.get_workflow_metrics(workflow_id)
            
            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "execution_history": execution_history,
                "metrics": metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            return {"error": str(e)}
            
    async def get_alert_status(self, alert_id: str) -> Dict[str, Any]:
        """Get comprehensive alert status and history"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return {"error": "Alert not found"}
                
            # Get alert history
            history = self.alert_history.get(alert_id, [])
            
            # Get current status
            is_in_cooldown = await self._is_alert_in_cooldown(alert_id)
            
            return {
                "alert_id": alert_id,
                "alert_type": alert.alert_type,
                "severity_level": alert.severity_level,
                "is_in_cooldown": is_in_cooldown,
                "trigger_history": history,
                "total_triggers": len(history)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get alert status: {str(e)}")
            return {"error": str(e)}
            
    async def _process_workflow_queue(self):
        """Process workflow execution queue"""
        while True:
            try:
                priority, workflow = await self.workflow_queue.get()
                await self._execute_workflow(workflow)
                self.workflow_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing workflow queue: {str(e)}")
                await asyncio.sleep(1)
                
    async def _execute_workflow(self, workflow: NotificationWorkflow):
        """Execute a notification workflow"""
        try:
            # Update workflow status
            workflow.status = NotificationWorkflowStatus.RUNNING
            workflow.updated_at = datetime.utcnow()
            
            start_time = datetime.utcnow()
            
            # Execute notification sequence
            for i, step in enumerate(workflow.notification_sequence):
                try:
                    # Apply step-specific context
                    step_context = await self._apply_step_context(step, workflow.context)
                    
                    # Execute notification step
                    step_result = await self._execute_notification_step(step, step_context)
                    
                    # Check success criteria
                    if not await self._check_step_success(step, step_result):
                        # Handle step failure
                        await self._handle_step_failure(workflow, i, step_result)
                        
                        # Check if workflow should continue
                        if not step.get('continue_on_failure', False):
                            workflow.status = NotificationWorkflowStatus.FAILED
                            break
                            
                    # Add delay between steps if configured
                    step_delay = step.get('delay_seconds', 0)
                    if step_delay > 0:
                        await asyncio.sleep(step_delay)
                        
                except Exception as e:
                    self.logger.error(f"Workflow step {i} failed: {str(e)}")
                    await self._handle_step_failure(workflow, i, {"error": str(e)})
                    
                    if not step.get('continue_on_failure', False):
                        workflow.status = NotificationWorkflowStatus.FAILED
                        break
                        
            # Update final status
            if workflow.status == NotificationWorkflowStatus.RUNNING:
                workflow.status = NotificationWorkflowStatus.COMPLETED
                
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update metrics
            self.performance_metrics['workflows_executed'] += 1
            self._update_average_processing_time(execution_time)
            
            # Store workflow results
            await self.repository.store_workflow_execution(workflow, execution_time)
            
            self.logger.info(f"Workflow executed: {workflow.id} ({workflow.status.value})")
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {workflow.id}: {str(e)}")
            workflow.status = NotificationWorkflowStatus.FAILED
            
    async def _monitor_scheduled_notifications(self):
        """Monitor and execute scheduled notifications"""
        while True:
            try:
                current_time = datetime.utcnow()
                ready_notifications = []
                
                # Find notifications ready for execution
                for schedule_id, schedule in list(self.scheduled_notifications.items()):
                    if schedule['execution_time'] <= current_time:
                        ready_notifications.append(schedule_id)
                        
                # Execute ready notifications
                for schedule_id in ready_notifications:
                    schedule = self.scheduled_notifications.pop(schedule_id)
                    await self._process_scheduled_notification(schedule)
                    
                # Sleep for 1 second before next check
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error monitoring scheduled notifications: {str(e)}")
                await asyncio.sleep(1)
                
    async def _process_recurring_schedules(self):
        """Process recurring notification schedules"""
        while True:
            try:
                # Check each recurring schedule
                for schedule_id, schedule in list(self.recurring_schedules.items()):
                    if await self._should_execute_recurring(schedule):
                        await self._execute_recurring_notification(schedule)
                        await self._schedule_next_occurrence(schedule_id)
                        
                # Sleep for 60 seconds before next check
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing recurring schedules: {str(e)}")
                await asyncio.sleep(60)
                
    async def _monitor_active_alerts(self):
        """Monitor active alerts and their conditions"""
        while True:
            try:
                # Check conditions for each active alert
                for alert_id, alert in list(self.active_alerts.items()):
                    if await self._check_alert_conditions(alert):
                        # Trigger alert if conditions are met
                        await self.trigger_alert(alert_id, {
                            'condition_check': True,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        
                # Sleep for alert monitoring interval
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error monitoring alerts: {str(e)}")
                await asyncio.sleep(30)
                
    async def _optimize_template_performance(self):
        """Optimize template performance based on usage analytics"""
        while True:
            try:
                # Analyze template performance
                performance_data = await self._analyze_template_performance()
                
                # Optimize low-performing templates
                for template_id, performance in performance_data.items():
                    if performance['effectiveness'] < 0.7:  # Below 70% effectiveness
                        await self._optimize_template(template_id, performance)
                        
                # Sleep for 1 hour before next optimization
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error optimizing templates: {str(e)}")
                await asyncio.sleep(3600)
                
    async def _generate_management_reports(self):
        """Generate comprehensive management reports"""
        while True:
            try:
                # Generate daily management report
                report = await self._compile_management_report()
                
                # Send report to administrators
                await self._send_management_report(report)
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error generating management reports: {str(e)}")
                await asyncio.sleep(86400)
                
    # Validation methods
    async def _validate_workflow_config(self, config: Dict[str, Any]) -> bool:
        """Validate workflow configuration"""
        required_fields = ['name', 'trigger_conditions', 'notification_sequence']
        return all(field in config for field in required_fields)
        
    async def _validate_notification_config(self, config: Dict[str, Any]) -> bool:
        """Validate notification configuration"""
        required_fields = ['type', 'content', 'target']
        return all(field in config for field in required_fields)
        
    async def _validate_schedule_params(self, schedule_type: NotificationScheduleType, params: Dict[str, Any]) -> bool:
        """Validate schedule parameters based on type"""
        if schedule_type == NotificationScheduleType.DELAYED:
            return 'delay_seconds' in params
        elif schedule_type == NotificationScheduleType.RECURRING:
            return 'interval' in params
        elif schedule_type == NotificationScheduleType.CONDITIONAL:
            return 'conditions' in params
        return True
        
    async def _validate_alert_config(self, config: Dict[str, Any]) -> bool:
        """Validate alert configuration"""
        required_fields = ['alert_type', 'severity_level', 'conditions', 'notification_config']
        return all(field in config for field in required_fields)
        
    # Utility methods
    def _update_average_processing_time(self, new_time: float):
        """Update average processing time metric"""
        current_avg = self.performance_metrics['average_processing_time']
        total_executed = self.performance_metrics['workflows_executed']
        
        if total_executed == 1:
            self.performance_metrics['average_processing_time'] = new_time
        else:
            # Calculate new average
            self.performance_metrics['average_processing_time'] = (
                (current_avg * (total_executed - 1) + new_time) / total_executed
            )
    - Multi-tier alert and escalation systems
    - Real-time notification analytics and optimization
    - Business logic integration for content creators
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components initialization
        self._initialize_core_components()
        
        # Repository for persistent storage
        self.repository = NotificationRepository(config.get('database_config', {}))
        
        # Business logic integration
        self.business_logic = NotificationBusinessLogic(config.get('business_config', {}))
        
        # Security manager
        self.security_manager = NotificationSecurityManager(config.get('security_config', {}))
        
        # Monitoring service
        self.monitoring = NotificationMonitoringService(config.get('monitoring_config', {}))
        
        # Workflow management
        self.workflows: Dict[str, NotificationWorkflow] = {}
        self.active_workflows: Set[str] = set()
        
        # Scheduling system
        self.scheduled_notifications = []  # Priority queue
        self.recurring_schedules: Dict[str, Dict[str, Any]] = {}
        
        # Alert management
        self.active_alerts: Dict[str, NotificationAlert] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.performance_stats = {
            'workflows_executed': 0,
            'notifications_scheduled': 0,
            'alerts_triggered': 0,
            'average_processing_time': 0.0,
            'success_rate': 0.0
        }
        
    def _initialize_core_components(self):
        """Initialize core notification management components"""
        self.template_engine = self._initialize_template_engine()
        self.scheduler = self._initialize_scheduler()
        self.workflow_engine = self._initialize_workflow_engine()
        self.alert_processor = self._initialize_alert_processor()
        
    def _initialize_template_engine(self):
        """Initialize advanced template engine with AI capabilities"""
        from ...ai.templating.notification_template_engine import NotificationTemplateEngine
        return NotificationTemplateEngine(self.config.get('template_config', {}))
        
    def _initialize_scheduler(self):
        """Initialize intelligent notification scheduler"""
        from ...infrastructure.scheduling.notification_scheduler import NotificationScheduler
        return NotificationScheduler(self.config.get('scheduler_config', {}))
        
    def _initialize_workflow_engine(self):
        """Initialize workflow execution engine"""
        from ...infrastructure.workflow.notification_workflow_engine import NotificationWorkflowEngine
        return NotificationWorkflowEngine(self.config.get('workflow_config', {}))
        
    def _initialize_alert_processor(self):
        """Initialize alert processing system"""
        from ...infrastructure.alerting.notification_alert_processor import NotificationAlertProcessor
        return NotificationAlertProcessor(self.config.get('alert_config', {}))
        
    async def start_manager(self):
        """Start the notification manager with all processing services"""
        try:
            self.logger.info("Starting NotificationManager with advanced orchestration")
            
            # Start core services
            await self.repository.initialize()
            await self.monitoring.start_monitoring()
            
            # Start processing tasks
            self.processing_tasks = [
                asyncio.create_task(self._process_scheduled_notifications()),
                asyncio.create_task(self._execute_workflows()),
                asyncio.create_task(self._monitor_alerts()),
                asyncio.create_task(self._optimize_performance()),
                asyncio.create_task(self._cleanup_expired_data())
            ]
            
            # Load existing workflows and schedules
            await self._load_persistent_data()
            
            self.logger.info("NotificationManager started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start NotificationManager: {str(e)}")
            return False
            
    async def stop_manager(self):
        """Gracefully stop the notification manager"""
        try:
            self.logger.info("Stopping NotificationManager")
            
            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()
                
            # Save persistent data
            await self._save_persistent_data()
            
            # Stop monitoring
            await self.monitoring.stop_monitoring()
            
            self.logger.info("NotificationManager stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping NotificationManager: {str(e)}")
            return False
            
    async def create_notification_workflow(
        self,
        name: str,
        description: str,
        trigger_conditions: Dict[str, Any],
        notification_sequence: List[Dict[str, Any]],
        scheduling_rules: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create advanced notification workflow with intelligent orchestration
        
        Args:
            name: Workflow name
            description: Workflow description
            trigger_conditions: Conditions that trigger the workflow
            notification_sequence: Sequence of notifications to send
            scheduling_rules: Advanced scheduling configuration
            
        Returns:
            workflow_id: Unique workflow identifier
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Validate workflow configuration
            if not await self._validate_workflow_config(
                trigger_conditions, notification_sequence
            ):
                raise ValueError("Invalid workflow configuration")
                
            # Create workflow instance
            workflow = NotificationWorkflow(
                id=workflow_id,
                name=name,
                description=description,
                trigger_conditions=trigger_conditions,
                notification_sequence=notification_sequence,
                scheduling_rules=scheduling_rules or {},
                success_criteria=self._generate_success_criteria(notification_sequence),
                failure_handling=self._generate_failure_handling()
            )
            
            # Store workflow
            self.workflows[workflow_id] = workflow
            await self.repository.save_workflow(workflow)
            
            # Register with workflow engine
            await self.workflow_engine.register_workflow(workflow)
            
            self.logger.info(f"Notification workflow created: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to create notification workflow: {str(e)}")
            raise
            
    async def trigger_workflow(
        self,
        workflow_id: str,
        trigger_data: Dict[str, Any],
        context_override: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Trigger execution of a notification workflow
        
        Args:
            workflow_id: ID of workflow to trigger
            trigger_data: Data that triggered the workflow
            context_override: Optional context override
            
        Returns:
            success: Whether workflow was successfully triggered
        """
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_id}")
                
            # Validate trigger conditions
            if not await self._validate_trigger_conditions(
                workflow.trigger_conditions, trigger_data
            ):
                self.logger.info(f"Trigger conditions not met for workflow: {workflow_id}")
                return False
                
            # Security validation
            if not await self.security_manager.validate_workflow_trigger(
                workflow_id, trigger_data
            ):
                raise ValueError("Security validation failed for workflow trigger")
                
            # Queue workflow for execution
            execution_context = {
                'workflow_id': workflow_id,
                'trigger_data': trigger_data,
                'context_override': context_override or {},
                'triggered_at': datetime.utcnow().isoformat()
            }
            
            # Add to active workflows
            self.active_workflows.add(workflow_id)
            workflow.status = NotificationWorkflowStatus.RUNNING
            
            # Execute workflow
            success = await self.workflow_engine.execute_workflow(
                workflow, execution_context
            )
            
            # Update statistics
            self.performance_stats['workflows_executed'] += 1
            
            # Monitor workflow execution
            await self.monitoring.record_workflow_execution(workflow_id, success)
            
            self.logger.info(f"Workflow triggered successfully: {workflow_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to trigger workflow {workflow_id}: {str(e)}")
            return False
            
    async def schedule_notification(
        self,
        notification_config: Dict[str, Any],
        schedule_type: NotificationScheduleType,
        schedule_params: Dict[str, Any]
    ) -> str:
        """
        Schedule notification with intelligent timing optimization
        
        Args:
            notification_config: Notification configuration
            schedule_type: Type of scheduling
            schedule_params: Scheduling parameters
            
        Returns:
            schedule_id: Unique schedule identifier
        """
        try:
            schedule_id = str(uuid.uuid4())
            
            # Validate notification configuration
            if not await self._validate_notification_config(notification_config):
                raise ValueError("Invalid notification configuration")
                
            # Calculate optimal scheduling
            optimal_schedule = await self.scheduler.optimize_schedule(
                schedule_type, schedule_params, notification_config
            )
            
            # Create schedule entry
            schedule_entry = {
                'id': schedule_id,
                'notification_config': notification_config,
                'schedule_type': schedule_type.value,
                'schedule_params': schedule_params,
                'optimal_schedule': optimal_schedule,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Add to scheduling queue based on type
            if schedule_type == NotificationScheduleType.IMMEDIATE:
                # High priority for immediate notifications
                heapq.heappush(self.scheduled_notifications, (0, schedule_entry))
            elif schedule_type == NotificationScheduleType.DELAYED:
                # Schedule based on delay time
                delay_time = schedule_params.get('delay_minutes', 0)
                priority = delay_time
                heapq.heappush(self.scheduled_notifications, (priority, schedule_entry))
            elif schedule_type == NotificationScheduleType.RECURRING:
                # Add to recurring schedules
                self.recurring_schedules[schedule_id] = schedule_entry
            else:
                # Default priority
                heapq.heappush(self.scheduled_notifications, (100, schedule_entry))
                
            # Save to repository
            await self.repository.save_schedule(schedule_entry)
            
            self.logger.info(f"Notification scheduled: {schedule_id} ({schedule_type.value})")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule notification: {str(e)}")
            raise
            
    # Additional helper methods for comprehensive functionality
    async def _load_active_workflows(self):
        """Load active workflows from repository"""
        try:
            stored_workflows = await self.repository.get_active_workflows()
            for workflow_data in stored_workflows:
                workflow = NotificationWorkflow(**workflow_data)
                self.active_workflows[workflow.id] = workflow
                
            self.logger.info(f"Loaded {len(stored_workflows)} active workflows")
            
        except Exception as e:
            self.logger.error(f"Failed to load active workflows: {str(e)}")
            
    async def _complete_active_workflows(self):
        """Complete any remaining active workflows during shutdown"""
        try:
            for workflow_id, workflow in list(self.active_workflows.items()):
                if workflow.status == NotificationWorkflowStatus.RUNNING:
                    workflow.status = NotificationWorkflowStatus.CANCELLED
                    await self.repository.update_workflow_status(workflow_id, workflow.status)
                    
        except Exception as e:
            self.logger.error(f"Error completing active workflows: {str(e)}")
            
    async def _check_trigger_conditions(self, workflow: NotificationWorkflow, context: Dict[str, Any]) -> bool:
        """Check if workflow trigger conditions are met"""
        try:
            conditions = workflow.trigger_conditions
            
            # Check each condition
            for condition_type, condition_value in conditions.items():
                if condition_type == "user_action":
                    if context.get("action") != condition_value:
                        return False
                elif condition_type == "content_type":
                    if context.get("content_type") != condition_value:
                        return False
                elif condition_type == "priority_level":
                    if context.get("priority", 0) < condition_value:
                        return False
                elif condition_type == "time_window":
                    current_hour = datetime.utcnow().hour
                    if not (condition_value["start"] <= current_hour <= condition_value["end"]):
                        return False
                        
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking trigger conditions: {str(e)}")
            return False
            
    async def _calculate_workflow_priority(self, workflow: NotificationWorkflow, context: Dict[str, Any]) -> int:
        """Calculate workflow execution priority"""
        try:
            base_priority = 5  # Default medium priority
            
            # Adjust based on notification type
            if "urgent" in workflow.name.lower():
                base_priority = 1
            elif "high" in workflow.name.lower():
                base_priority = 2
            elif "low" in workflow.name.lower():
                base_priority = 8
                
            # Adjust based on context
            if context.get("user_tier") == "premium":
                base_priority -= 1
            if context.get("business_critical", False):
                base_priority = 1
                
            return max(1, min(10, base_priority))
            
        except Exception as e:
            self.logger.error(f"Error calculating workflow priority: {str(e)}")
            return 5
            
    async def _process_immediate_notification(self, notification_config: Dict[str, Any]):
        """Process immediate notification"""
        try:
            # Create notification context
            context = NotificationContext(
                user_id=notification_config["target"]["user_id"],
                content_type=notification_config["type"],
                metadata=notification_config.get("metadata", {})
            )
            
            # Send notification through agent
            from .notification_agent import NotificationAgent, NotificationType
            agent = NotificationAgent(self.config)
            
            notification_type = NotificationType(notification_config["type"])
            await agent.send_notification(notification_type, context)
            
        except Exception as e:
            self.logger.error(f"Failed to process immediate notification: {str(e)}")
            
    async def _schedule_next_occurrence(self, schedule_id: str):
        """Schedule next occurrence for recurring notifications"""
        try:
            schedule = self.recurring_schedules.get(schedule_id)
            if not schedule:
                return
                
            schedule_params = schedule["schedule_params"]
            interval = schedule_params.get("interval", "daily")
            
            # Calculate next execution time
            if interval == "hourly":
                next_time = datetime.utcnow() + timedelta(hours=1)
            elif interval == "daily":
                next_time = datetime.utcnow() + timedelta(days=1)
            elif interval == "weekly":
                next_time = datetime.utcnow() + timedelta(weeks=1)
            elif interval == "monthly":
                next_time = datetime.utcnow() + timedelta(days=30)
            else:
                # Custom interval in minutes
                minutes = schedule_params.get("interval_minutes", 60)
                next_time = datetime.utcnow() + timedelta(minutes=minutes)
                
            # Add to scheduled notifications
            schedule_entry = schedule.copy()
            schedule_entry["execution_time"] = next_time
            self.scheduled_notifications[f"{schedule_id}_{next_time.timestamp()}"] = schedule_entry
            
        except Exception as e:
            self.logger.error(f"Failed to schedule next occurrence: {str(e)}")
            
    async def _setup_conditional_monitoring(self, schedule_id: str, schedule_entry: Dict[str, Any]):
        """Set up monitoring for conditional notifications"""
        try:
            conditions = schedule_entry["schedule_params"]["conditions"]
            
            # Register condition monitoring
            for condition in conditions:
                await self.monitoring.register_condition_monitor(
                    schedule_id, condition["type"], condition["parameters"]
                )
                
        except Exception as e:
            self.logger.error(f"Failed to setup conditional monitoring: {str(e)}")
            
    async def _add_to_batch_queue(self, schedule_entry: Dict[str, Any]):
        """Add notification to batch optimization queue"""
        try:
            # Add to batch processing queue
            batch_key = self._calculate_batch_key(schedule_entry)
            
            if batch_key not in self.batch_queues:
                self.batch_queues[batch_key] = []
                
            self.batch_queues[batch_key].append(schedule_entry)
            
            # Schedule batch processing if queue is full
            if len(self.batch_queues[batch_key]) >= 10:  # Batch size threshold
                await self._process_batch_queue(batch_key)
                
        except Exception as e:
            self.logger.error(f"Failed to add to batch queue: {str(e)}")
            
    def _calculate_batch_key(self, schedule_entry: Dict[str, Any]) -> str:
        """Calculate batch key for grouping similar notifications"""
        notification_config = schedule_entry["notification_config"]
        return f"{notification_config['type']}_{notification_config.get('template', 'default')}"
        
    async def _setup_alert_monitoring(self, alert: NotificationAlert):
        """Set up monitoring for alert conditions"""
        try:
            for condition in alert.conditions:
                await self.monitoring.register_alert_condition(
                    alert.id, condition["metric"], condition["threshold"]
                )
                
        except Exception as e:
            self.logger.error(f"Failed to setup alert monitoring: {str(e)}")
            
    async def _is_alert_in_cooldown(self, alert_id: str) -> bool:
        """Check if alert is in cooldown period"""
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                return False
                
            history = self.alert_history.get(alert_id, [])
            if not history:
                return False
                
            last_trigger = history[-1]["triggered_at"]
            if isinstance(last_trigger, str):
                last_trigger = datetime.fromisoformat(last_trigger)
                
            cooldown_end = last_trigger + timedelta(seconds=alert.cooldown_period)
            return datetime.utcnow() < cooldown_end
            
        except Exception as e:
            self.logger.error(f"Error checking alert cooldown: {str(e)}")
            return False
            
    async def _validate_alert_trigger(self, alert: NotificationAlert, trigger_data: Dict[str, Any]) -> bool:
        """Validate alert trigger conditions"""
        try:
            for condition in alert.conditions:
                metric_name = condition["metric"]
                threshold = condition["threshold"]
                operator = condition.get("operator", ">=")
                
                actual_value = trigger_data.get(metric_name)
                if actual_value is None:
                    return False
                    
                if operator == ">=" and actual_value < threshold:
                    return False
                elif operator == "<=" and actual_value > threshold:
                    return False
                elif operator == "==" and actual_value != threshold:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating alert trigger: {str(e)}")
            return False
            
    async def _create_alert_notification(self, alert: NotificationAlert, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification for triggered alert"""
        try:
            return {
                "type": "alert",
                "alert_id": alert.id,
                "alert_type": alert.alert_type,
                "severity_level": alert.severity_level,
                "trigger_data": trigger_data,
                "timestamp": datetime.utcnow().isoformat(),
                **alert.notification_config
            }
            
        except Exception as e:
            self.logger.error(f"Error creating alert notification: {str(e)}")
            return {}
            
    async def _send_alert_notification(self, alert_notification: Dict[str, Any]):
        """Send alert notification"""
        try:
            # Use notification agent to send alert
            from .notification_agent import NotificationAgent, NotificationType
            agent = NotificationAgent(self.config)
            
            context = NotificationContext(
                user_id=alert_notification.get("target_user", "admin"),
                content_type="alert",
                metadata=alert_notification
            )
            
            await agent.send_notification(
                NotificationType.SECURITY_ALERT, 
                context, 
                priority=NotificationPriority.HIGH
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send alert notification: {str(e)}")
            
    async def _setup_alert_escalation(self, alert: NotificationAlert, trigger_data: Dict[str, Any]):
        """Set up alert escalation if configured"""
        try:
            for escalation in alert.escalation_rules:
                # Schedule escalation after delay
                delay = escalation.get("delay_minutes", 15)
                escalation_time = datetime.utcnow() + timedelta(minutes=delay)
                
                escalation_entry = {
                    "alert_id": alert.id,
                    "escalation_level": escalation["level"],
                    "trigger_data": trigger_data,
                    "escalation_config": escalation,
                    "execution_time": escalation_time
                }
                
                # Add to escalation queue
                schedule_id = f"escalation_{alert.id}_{escalation['level']}"
                self.scheduled_notifications[schedule_id] = escalation_entry
                
        except Exception as e:
            self.logger.error(f"Failed to setup alert escalation: {str(e)}")
            
    async def _apply_step_context(self, step: Dict[str, Any], workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply workflow context to notification step"""
        try:
            step_context = step.copy()
            
            # Replace context variables
            for key, value in step_context.items():
                if isinstance(value, str) and value.startswith("${"):
                    # Extract variable name
                    var_name = value[2:-1]  # Remove ${ and }
                    if var_name in workflow_context:
                        step_context[key] = workflow_context[var_name]
                        
            return step_context
            
        except Exception as e:
            self.logger.error(f"Error applying step context: {str(e)}")
            return step
            
    async def _execute_notification_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual notification step"""
        try:
            # Create notification configuration
            notification_config = {
                "type": step["notification_type"],
                "content": step["content"],
                "target": step["target"],
                "metadata": context
            }
            
            # Process notification
            await self._process_immediate_notification(notification_config)
            
            return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
            
        except Exception as e:
            self.logger.error(f"Failed to execute notification step: {str(e)}")
            return {"status": "failed", "error": str(e)}
            
    async def _check_step_success(self, step: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Check if notification step was successful"""
        return result.get("status") == "success"
        
    async def _handle_step_failure(self, workflow: NotificationWorkflow, step_index: int, result: Dict[str, Any]):
        """Handle notification step failure"""
        try:
            failure_config = workflow.failure_handling
            
            # Log failure
            self.logger.error(f"Workflow {workflow.id} step {step_index} failed: {result}")
            
            # Send failure notification if configured
            if failure_config.get("notify_on_failure", False):
                failure_notification = {
                    "type": "workflow_failure",
                    "workflow_id": workflow.id,
                    "step_index": step_index,
                    "failure_reason": result,
                    "target": {"user_id": failure_config.get("notification_target", "admin")}
                }
                await self._process_immediate_notification(failure_notification)
                
        except Exception as e:
            self.logger.error(f"Error handling step failure: {str(e)}")
            
    async def _process_scheduled_notification(self, schedule: Dict[str, Any]):
        """Process a scheduled notification"""
        try:
            await self._process_immediate_notification(schedule["notification_config"])
            
            # Update schedule status
            schedule["status"] = "completed"
            schedule["executed_at"] = datetime.utcnow().isoformat()
            
            # Save execution record
            await self.repository.save_execution_record(schedule)
            
        except Exception as e:
            self.logger.error(f"Failed to process scheduled notification: {str(e)}")
            
    async def _should_execute_recurring(self, schedule: Dict[str, Any]) -> bool:
        """Check if recurring notification should be executed"""
        try:
            last_execution = schedule.get("last_executed")
            if not last_execution:
                return True
                
            if isinstance(last_execution, str):
                last_execution = datetime.fromisoformat(last_execution)
                
            interval = schedule["schedule_params"]["interval"]
            
            if interval == "hourly":
                return (datetime.utcnow() - last_execution).total_seconds() >= 3600
            elif interval == "daily":
                return (datetime.utcnow() - last_execution).days >= 1
            elif interval == "weekly":
                return (datetime.utcnow() - last_execution).days >= 7
            elif interval == "monthly":
                return (datetime.utcnow() - last_execution).days >= 30
            else:
                # Custom interval
                minutes = schedule["schedule_params"].get("interval_minutes", 60)
                return (datetime.utcnow() - last_execution).total_seconds() >= (minutes * 60)
                
        except Exception as e:
            self.logger.error(f"Error checking recurring execution: {str(e)}")
            return False
            
    async def _execute_recurring_notification(self, schedule: Dict[str, Any]):
        """Execute recurring notification"""
        try:
            await self._process_immediate_notification(schedule["notification_config"])
            
            # Update last execution time
            schedule["last_executed"] = datetime.utcnow().isoformat()
            
            # Save updated schedule
            await self.repository.update_schedule(schedule)
            
        except Exception as e:
            self.logger.error(f"Failed to execute recurring notification: {str(e)}")
            
    async def _check_alert_conditions(self, alert: NotificationAlert) -> bool:
        """Check if alert conditions are met"""
        try:
            # Get current metrics
            current_metrics = await self.monitoring.get_current_metrics()
            
            # Check each condition
            for condition in alert.conditions:
                metric_name = condition["metric"]
                threshold = condition["threshold"]
                operator = condition.get("operator", ">=")
                
                current_value = current_metrics.get(metric_name, 0)
                
                if operator == ">=" and current_value >= threshold:
                    return True
                elif operator == "<=" and current_value <= threshold:
                    return True
                elif operator == "==" and current_value == threshold:
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking alert conditions: {str(e)}")
            return False
            
    async def _analyze_template_performance(self) -> Dict[str, Dict[str, float]]:
        """Analyze template performance metrics"""
        try:
            performance_data = {}
            
            for template_id, metrics in self.template_performance.items():
                if metrics["total_sent"] > 0:
                    effectiveness = metrics["total_delivered"] / metrics["total_sent"]
                    engagement = metrics.get("total_engaged", 0) / metrics["total_sent"]
                    
                    performance_data[template_id] = {
                        "effectiveness": effectiveness,
                        "engagement": engagement,
                        "total_sent": metrics["total_sent"]
                    }
                    
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing template performance: {str(e)}")
            return {}
            
    async def _optimize_template(self, template_id: str, performance: Dict[str, float]):
        """Optimize underperforming template"""
        try:
            # Get template content
            template = await self.repository.get_template(template_id)
            if not template:
                return
                
            # Apply AI-driven optimization
            optimized_template = await self._apply_ai_template_optimization(template, performance)
            
            # Save optimized template
            await self.repository.save_template(optimized_template)
            
            self.logger.info(f"Template optimized: {template_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to optimize template {template_id}: {str(e)}")
            
    async def _apply_ai_template_optimization(self, template: Dict[str, Any], performance: Dict[str, float]) -> Dict[str, Any]:
        """Apply AI-driven template optimization"""
        # This would integrate with AI optimization service
        # For now, return template with optimization metadata
        optimized_template = template.copy()
        optimized_template["optimization_applied"] = True
        optimized_template["optimization_timestamp"] = datetime.utcnow().isoformat()
        optimized_template["previous_performance"] = performance
        
        return optimized_template
        
    async def _compile_management_report(self) -> Dict[str, Any]:
        """Compile comprehensive management report"""
        try:
            return {
                "report_date": datetime.utcnow().isoformat(),
                "performance_metrics": self.performance_metrics,
                "workflow_statistics": {
                    "total_workflows": len(self.active_workflows),
                    "completed_workflows": sum(1 for w in self.active_workflows.values() 
                                             if w.status == NotificationWorkflowStatus.COMPLETED),
                    "failed_workflows": sum(1 for w in self.active_workflows.values() 
                                          if w.status == NotificationWorkflowStatus.FAILED)
                },
                "alert_statistics": {
                    "total_alerts": len(self.active_alerts),
                    "triggered_alerts": sum(len(history) for history in self.alert_history.values())
                },
                "template_performance": await self._analyze_template_performance(),
                "system_health": await self.monitoring.get_system_health_metrics()
            }
            
        except Exception as e:
            self.logger.error(f"Error compiling management report: {str(e)}")
            return {}
            
    async def _send_management_report(self, report: Dict[str, Any]):
        """Send management report to administrators"""
        try:
            # Create management report notification
            report_notification = {
                "type": "management_report",
                "content": {
                    "title": f"Notification System Management Report - {datetime.utcnow().strftime('%Y-%m-%d')}",
                    "report_data": report
                },
                "target": {"user_id": "system_admin"}
            }
            
            await self._process_immediate_notification(report_notification)
            
        except Exception as e:
            self.logger.error(f"Failed to send management report: {str(e)}")


class AlertDispatcher:
    """
    Advanced alert dispatching system for immediate critical notifications
    Handles high-priority alerts with escalation and failover capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.alert_channels = self._initialize_alert_channels()
        self.escalation_manager = self._initialize_escalation_manager()
        
    def _initialize_alert_channels(self):
        """Initialize alert-specific delivery channels"""
        from ...integrations.alert_channels import AlertChannelManager
        return AlertChannelManager(self.config.get('alert_channels', {}))
        
    def _initialize_escalation_manager(self):
        """Initialize alert escalation management"""
        from ...business.alert_escalation import AlertEscalationManager
        return AlertEscalationManager(self.config.get('escalation_config', {}))
        
    async def dispatch_critical_alert(
        self,
        alert_data: Dict[str, Any],
        escalation_level: int = 1
    ) -> bool:
        """Dispatch critical alert with immediate delivery"""
        try:
            # Determine alert channels based on severity
            channels = await self._determine_alert_channels(alert_data, escalation_level)
            
            # Dispatch to all channels simultaneously
            dispatch_tasks = []
            for channel in channels:
                task = asyncio.create_task(
                    self.alert_channels.send_alert(channel, alert_data)
                )
                dispatch_tasks.append(task)
                
            # Wait for at least one successful delivery
            results = await asyncio.gather(*dispatch_tasks, return_exceptions=True)
            
            # Check if any delivery was successful
            success = any(
                result is True for result in results 
                if not isinstance(result, Exception)
            )
            
            # Handle escalation if all deliveries failed
            if not success and escalation_level < 3:
                await self.escalation_manager.escalate_alert(alert_data, escalation_level + 1)
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to dispatch critical alert: {str(e)}")
            return False
            
    async def _determine_alert_channels(
        self,
        alert_data: Dict[str, Any],
        escalation_level: int
    ) -> List[str]:
        """Determine appropriate channels for alert delivery"""
        base_channels = ["email", "sms"]
        
        severity = alert_data.get("severity_level", 3)
        
        if severity >= 8 or escalation_level >= 2:
            base_channels.extend(["phone_call", "slack", "teams"])
            
        if escalation_level >= 3:
            base_channels.append("emergency_contact")
            
        return base_channels
            
            # Update statistics
            self.performance_stats['notifications_scheduled'] += 1
            
            self.logger.info(f"Notification scheduled: {schedule_id}")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule notification: {str(e)}")
            raise
            
    async def create_alert_configuration(
        self,
        alert_type: str,
        severity_level: int,
        conditions: Dict[str, Any],
        escalation_rules: List[Dict[str, Any]],
        notification_config: Dict[str, Any]
    ) -> str:
        """
        Create advanced alert configuration with escalation
        
        Args:
            alert_type: Type of alert (e.g., 'content_protection', 'security_breach')
            severity_level: Alert severity (1-5, 5 being most critical)
            conditions: Conditions that trigger the alert
            escalation_rules: Rules for alert escalation
            notification_config: Notification configuration for alert
            
        Returns:
            alert_id: Unique alert identifier
        """
        try:
            alert_id = str(uuid.uuid4())
            
            # Validate alert configuration
            if not await self._validate_alert_config(
                alert_type, conditions, escalation_rules
            ):
                raise ValueError("Invalid alert configuration")
                
            # Create alert instance
            alert = NotificationAlert(
                id=alert_id,
                alert_type=alert_type,
                severity_level=severity_level,
                conditions=conditions,
                escalation_rules=escalation_rules,
                notification_config=notification_config
            )
            
            # Store alert configuration
            self.active_alerts[alert_id] = alert
            await self.repository.save_alert_config(alert)
            
            # Register with alert processor
            await self.alert_processor.register_alert(alert)
            
            self.logger.info(f"Alert configuration created: {alert_id}")
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Failed to create alert configuration: {str(e)}")
            raise
            
    async def trigger_alert(
        self,
        alert_id: str,
        alert_data: Dict[str, Any],
        severity_override: Optional[int] = None
    ) -> bool:
        """
        Trigger alert with escalation handling
        
        Args:
            alert_id: ID of alert to trigger
            alert_data: Data that triggered the alert
            severity_override: Optional severity level override
            
        Returns:
            success: Whether alert was successfully triggered
        """
        try:
            alert = self.active_alerts.get(alert_id)
            if not alert:
                raise ValueError(f"Alert configuration not found: {alert_id}")
                
            # Check cooldown period
            if not await self._check_alert_cooldown(alert_id):
                self.logger.info(f"Alert {alert_id} in cooldown period, skipping")
                return False
                
            # Validate trigger conditions
            if not await self._validate_alert_conditions(alert.conditions, alert_data):
                self.logger.info(f"Alert conditions not met: {alert_id}")
                return False
                
            # Determine effective severity
            effective_severity = severity_override or alert.severity_level
            
            # Process alert through escalation chain
            success = await self.alert_processor.process_alert(
                alert, alert_data, effective_severity
            )
            
            # Record alert in history
            alert_record = {
                'alert_id': alert_id,
                'triggered_at': datetime.utcnow().isoformat(),
                'alert_data': alert_data,
                'severity': effective_severity,
                'success': success
            }
            self.alert_history.append(alert_record)
            
            # Update statistics
            self.performance_stats['alerts_triggered'] += 1
            
            # Monitor alert
            await self.monitoring.record_alert_trigger(alert_id, success)
            
            self.logger.info(f"Alert triggered: {alert_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert {alert_id}: {str(e)}")
            return False
            
    async def get_notification_templates(
        self,
        template_type: Optional[str] = None,
        channel: Optional[NotificationChannel] = None
    ) -> List[Dict[str, Any]]:
        """Get available notification templates with filtering"""
        try:
            templates = await self.template_engine.get_templates(
                template_type=template_type,
                channel=channel
            )
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to get notification templates: {str(e)}")
            return []
            
    async def create_custom_template(
        self,
        template_name: str,
        template_type: str,
        channels: List[NotificationChannel],
        template_content: Dict[str, Any],
        personalization_rules: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create custom notification template with AI personalization
        
        Args:
            template_name: Name of the template
            template_type: Type of template (e.g., 'content_upload', 'collaboration_match')
            channels: Supported channels for this template
            template_content: Template content structure
            personalization_rules: AI personalization rules
            
        Returns:
            template_id: Unique template identifier
        """
        try:
            template_id = await self.template_engine.create_template(
                name=template_name,
                template_type=template_type,
                channels=channels,
                content=template_content,
                personalization_rules=personalization_rules or {}
            )
            
            self.logger.info(f"Custom template created: {template_id}")
            return template_id
            
        except Exception as e:
            self.logger.error(f"Failed to create custom template: {str(e)}")
            raise
            
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow execution status"""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return {"error": "Workflow not found"}
                
            # Get execution history
            execution_history = await self.repository.get_workflow_execution_history(workflow_id)
            
            # Get performance metrics
            metrics = await self.monitoring.get_workflow_metrics(workflow_id)
            
            return {
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "execution_history": execution_history,
                "metrics": metrics,
                "is_active": workflow_id in self.active_workflows
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            return {"error": str(e)}
            
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get comprehensive system analytics and performance metrics"""
        try:
            analytics = {
                "performance_stats": self.performance_stats.copy(),
                "workflow_analytics": await self._get_workflow_analytics(),
                "scheduling_analytics": await self._get_scheduling_analytics(),
                "alert_analytics": await self._get_alert_analytics(),
                "template_analytics": await self._get_template_analytics(),
                "channel_performance": await self._get_channel_performance()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get system analytics: {str(e)}")
            return {}
            
    async def _process_scheduled_notifications(self):
        """Process scheduled notifications based on priority and timing"""
        while True:
            try:
                if self.scheduled_notifications:
                    # Get highest priority notification
                    priority, schedule_entry = heapq.heappop(self.scheduled_notifications)
                    
                    # Check if it's time to send
                    if await self._is_send_time(schedule_entry):
                        await self._execute_scheduled_notification(schedule_entry)
                    else:
                        # Put back in queue if not ready
                        heapq.heappush(self.scheduled_notifications, (priority, schedule_entry))
                        
                # Check recurring schedules
                await self._process_recurring_schedules()
                
                # Sleep before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error processing scheduled notifications: {str(e)}")
                await asyncio.sleep(60)
                
    async def _execute_workflows(self):
        """Execute active workflows"""
        while True:
            try:
                # Process workflows that need attention
                workflows_to_process = list(self.active_workflows)
                
                for workflow_id in workflows_to_process:
                    try:
                        workflow = self.workflows.get(workflow_id)
                        if workflow and workflow.status == NotificationWorkflowStatus.RUNNING:
                            # Check workflow progress and handle completion
                            await self._check_workflow_progress(workflow)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing workflow {workflow_id}: {str(e)}")
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in workflow execution loop: {str(e)}")
                await asyncio.sleep(30)
                
    async def _monitor_alerts(self):
        """Monitor and process active alerts"""
        while True:
            try:
                # Check for alert conditions
                for alert_id, alert in self.active_alerts.items():
                    try:
                        # Check if alert should be triggered
                        should_trigger = await self.alert_processor.should_trigger_alert(alert)
                        
                        if should_trigger:
                            await self.trigger_alert(alert_id, {})
                            
                    except Exception as e:
                        self.logger.error(f"Error monitoring alert {alert_id}: {str(e)}")
                        
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in alert monitoring loop: {str(e)}")
                await asyncio.sleep(30)
                
    async def _optimize_performance(self):
        """Continuously optimize system performance"""
        while True:
            try:
                # Analyze performance metrics
                await self._analyze_performance_metrics()
                
                # Optimize scheduling
                await self._optimize_scheduling_algorithms()
                
                # Optimize templates
                await self._optimize_template_performance()
                
                # Sleep for optimization interval
                await asyncio.sleep(3600)  # Optimize every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in performance optimization: {str(e)}")
                await asyncio.sleep(3600)
                
    async def _cleanup_expired_data(self):
        """Clean up expired workflows, schedules, and alerts"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Clean up completed workflows older than 30 days
                expired_workflows = [
                    wid for wid, workflow in self.workflows.items()
                    if workflow.status == NotificationWorkflowStatus.COMPLETED
                    and (current_time - workflow.updated_at).days > 30
                ]
                
                for workflow_id in expired_workflows:
                    del self.workflows[workflow_id]
                    await self.repository.delete_workflow(workflow_id)
                    
                # Clean up old alert history
                cutoff_date = current_time - timedelta(days=90)
                self.alert_history = [
                    record for record in self.alert_history
                    if datetime.fromisoformat(record['triggered_at']) > cutoff_date
                ]
                
                if expired_workflows or len(self.alert_history) > 1000:
                    self.logger.info(f"Cleaned up {len(expired_workflows)} workflows and alert history")
                    
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup process: {str(e)}")
                await asyncio.sleep(86400)
                
    async def _validate_workflow_config(
        self,
        trigger_conditions: Dict[str, Any],
        notification_sequence: List[Dict[str, Any]]
    ) -> bool:
        """Validate workflow configuration"""
        try:
            # Validate trigger conditions
            if not trigger_conditions:
                return False
                
            # Validate notification sequence
            if not notification_sequence or len(notification_sequence) == 0:
                return False
                
            # Validate each notification in sequence
            for notification in notification_sequence:
                if not await self._validate_notification_config(notification):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Workflow validation failed: {str(e)}")
            return False
            
    async def _validate_notification_config(self, notification_config: Dict[str, Any]) -> bool:
        """Validate individual notification configuration"""
        try:
            required_fields = ['type', 'content', 'channels']
            
            for field in required_fields:
                if field not in notification_config:
                    return False
                    
            # Validate channels
            channels = notification_config.get('channels', [])
            valid_channels = [ch.value for ch in NotificationChannel]
            
            for channel in channels:
                if channel not in valid_channels:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Notification config validation failed: {str(e)}")
            return False
            
    async def _validate_alert_config(
        self,
        alert_type: str,
        conditions: Dict[str, Any],
        escalation_rules: List[Dict[str, Any]]
    ) -> bool:
        """Validate alert configuration"""
        try:
            # Validate alert type
            valid_alert_types = [
                'content_protection', 'security_breach', 'system_error',
                'performance_degradation', 'collaboration_opportunity'
            ]
            
            if alert_type not in valid_alert_types:
                return False
                
            # Validate conditions
            if not conditions:
                return False
                
            # Validate escalation rules
            for rule in escalation_rules:
                if 'level' not in rule or 'action' not in rule:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Alert config validation failed: {str(e)}")
            return False
            
    def _generate_success_criteria(self, notification_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate success criteria for workflow"""
        return {
            'minimum_delivery_rate': 0.8,
            'maximum_failure_rate': 0.2,
            'required_channels': len(set([
                ch for notif in notification_sequence 
                for ch in notif.get('channels', [])
            ])),
            'completion_timeout': 3600  # 1 hour
        }
        
    def _generate_failure_handling(self) -> Dict[str, Any]:
        """Generate failure handling configuration"""
        return {
            'retry_attempts': 3,
            'retry_delay': 300,  # 5 minutes
            'fallback_channels': ['email'],
            'escalation_enabled': True,
            'notification_on_failure': True
        }


class AlertDispatcher:
    """
    Advanced alert dispatching system with intelligent routing and escalation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.escalation_chains: Dict[str, List[Dict[str, Any]]] = {}
        self.dispatch_history: List[Dict[str, Any]] = []
        
    async def dispatch_alert(
        self,
        alert: NotificationAlert,
        alert_data: Dict[str, Any],
        escalation_level: int = 1
    ) -> bool:
        """
        Dispatch alert through appropriate channels with escalation support
        
        Args:
            alert: Alert configuration
            alert_data: Alert data
            escalation_level: Current escalation level
            
        Returns:
            success: Whether alert was successfully dispatched
        """
        try:
            # Get escalation chain for this alert
            escalation_chain = self._get_escalation_chain(alert, escalation_level)
            
            dispatch_results = []
            
            # Dispatch through escalation chain
            for escalation_step in escalation_chain:
                result = await self._execute_escalation_step(
                    alert, alert_data, escalation_step
                )
                dispatch_results.append(result)
                
                # If successful, stop escalation
                if result.get('success'):
                    break
                    
            # Record dispatch
            dispatch_record = {
                'alert_id': alert.id,
                'dispatched_at': datetime.utcnow().isoformat(),
                'escalation_level': escalation_level,
                'results': dispatch_results,
                'success': any(r.get('success') for r in dispatch_results)
            }
            self.dispatch_history.append(dispatch_record)
            
            return dispatch_record['success']
            
        except Exception as e:
            self.logger.error(f"Alert dispatch failed: {str(e)}")
            return False
            
    def _get_escalation_chain(
        self,
        alert: NotificationAlert,
        escalation_level: int
    ) -> List[Dict[str, Any]]:
        """Get escalation chain for alert based on severity and level"""
        try:
            # Filter escalation rules by level
            applicable_rules = [
                rule for rule in alert.escalation_rules
                if rule.get('level', 1) <= escalation_level
            ]
            
            # Sort by priority
            return sorted(applicable_rules, key=lambda x: x.get('priority', 100))
            
        except Exception as e:
            self.logger.error(f"Failed to get escalation chain: {str(e)}")
            return []
            
    async def _execute_escalation_step(
        self,
        alert: NotificationAlert,
        alert_data: Dict[str, Any],
        escalation_step: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual escalation step"""
        try:
            action_type = escalation_step.get('action')
            
            if action_type == 'notification':
                return await self._send_escalation_notification(
                    alert, alert_data, escalation_step
                )
            elif action_type == 'webhook':
                return await self._trigger_escalation_webhook(
                    alert, alert_data, escalation_step
                )
            elif action_type == 'sms':
                return await self._send_escalation_sms(
                    alert, alert_data, escalation_step
                )
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def _send_escalation_notification(
        self,
        alert: NotificationAlert,
        alert_data: Dict[str, Any],
        escalation_step: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification as part of escalation"""
        # Implementation would integrate with notification system
        return {'success': True, 'method': 'notification'}
        
    async def _trigger_escalation_webhook(
        self,
        alert: NotificationAlert,
        alert_data: Dict[str, Any],
        escalation_step: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger webhook as part of escalation"""
        # Implementation would make HTTP request to webhook URL
        return {'success': True, 'method': 'webhook'}
        
    async def _send_escalation_sms(
        self,
        alert: NotificationAlert,
        alert_data: Dict[str, Any],
        escalation_step: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send SMS as part of escalation"""
        # Implementation would integrate with SMS service
        return {'success': True, 'method': 'sms'}
