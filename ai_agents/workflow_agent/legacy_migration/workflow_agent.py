"""
IA-Influencer Agent - Advanced Workflow Agent

Enterprise-grade workflow orchestration agent for multi-format content creators.
Handles complex business processes, automation workflows, and intelligent task management.

Key Features:
- Multi-step workflow orchestration
- AI-powered workflow optimization
- Real-time workflow monitoring
- Dynamic workflow adaptation
- Enterprise workflow templates
- Automated task scheduling

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 - All Rights Reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import traceback

from ..base import BaseAgent
from .workflow_orchestrator import WorkflowOrchestrator, OrchestrationStrategy
from .workflow_engine import WorkflowEngine, ExecutionMode, OptimizationStrategy
from .workflow_templates import WorkflowTemplateManager, TemplateCategory, TemplateType
from .workflow_scheduler import WorkflowScheduler, ScheduleType, Priority
from .workflow_monitor import WorkflowMonitor, AlertSeverity


class WorkflowAgent(BaseAgent):
    """
    Advanced workflow orchestration agent for multi-format content creators.
    
    This agent provides comprehensive workflow management capabilities including
    orchestration, execution, templating, scheduling, and monitoring.
    """

    def __init__(self):
        """Initialize the workflow agent."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        self.orchestrator = WorkflowOrchestrator()
        self.engine = WorkflowEngine(max_workers=100)
        self.template_manager = WorkflowTemplateManager()
        self.scheduler = WorkflowScheduler(max_concurrent_executions=50)
        self.monitor = WorkflowMonitor(retention_days=30)
        
        # Workflow registry
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_instances: Dict[str, Dict[str, Any]] = {}
        
        # Integration components
        self.agent_integrations = {}
        
        # Statistics
        self.agent_stats = {
            'total_workflows_managed': 0,
            'active_workflows': 0,
            'templates_created': 0,
            'schedules_managed': 0,
            'monitoring_alerts': 0
        }

    async def initialize(self):
        """Initialize the workflow agent and all components."""
        try:
            self.logger.info("Initializing Workflow Agent...")
            
            # Start monitoring system
            await self.monitor.start_monitoring()
            
            # Start scheduler
            await self.scheduler.start_scheduler()
            
            # Load built-in workflows
            await self._load_builtin_workflows()
            
            # Initialize agent integrations
            await self._initialize_agent_integrations()
            
            self.logger.info("Workflow Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing Workflow Agent: {str(e)}")
            raise

    async def create_workflow(
        self,
        name: str,
        description: str,
        workflow_definition: Dict[str, Any],
        category: str = "general",
        created_by: str = "system",
        **kwargs
    ) -> str:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            workflow_definition: Complete workflow definition
            category: Workflow category
            created_by: Creator identifier
            **kwargs: Additional workflow parameters
            
        Returns:
            str: Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Create workflow record
            workflow = {
                'id': workflow_id,
                'name': name,
                'description': description,
                'definition': workflow_definition,
                'category': category,
                'created_by': created_by,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version': '1.0.0',
                'status': 'active',
                'execution_count': 0,
                'success_rate': 0.0,
                'metadata': kwargs.get('metadata', {})
            }
            
            # Store workflow
            self.workflows[workflow_id] = workflow
            
            # Register with monitoring
            await self.monitor.register_workflow(workflow_id)
            
            # Update statistics
            self.agent_stats['total_workflows_managed'] += 1
            self.agent_stats['active_workflows'] += 1
            
            self.logger.info(f"Created workflow: {name} ({workflow_id})")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            raise

    async def execute_workflow(
        self,
        workflow_id: str,
        execution_context: Dict[str, Any],
        execution_mode: ExecutionMode = ExecutionMode.ASYNCHRONOUS,
        orchestration_strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    ) -> Dict[str, Any]:
        """
        Execute a workflow with specified parameters.
        
        Args:
            workflow_id: ID of workflow to execute
            execution_context: Execution context and parameters
            execution_mode: Execution mode to use
            orchestration_strategy: Orchestration strategy
            
        Returns:
            Dict containing execution results
        """
        try:
            # Get workflow definition
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Create execution instance
            instance_id = str(uuid.uuid4())
            execution_start = datetime.now()
            
            # Prepare execution context
            full_context = {
                **execution_context,
                'workflow_id': workflow_id,
                'instance_id': instance_id,
                'execution_start': execution_start
            }
            
            # Execute using orchestrator and engine
            orchestration_result = await self.orchestrator.orchestrate_workflow(
                workflow['definition'],
                full_context,
                orchestration_strategy
            )
            
            if orchestration_result['success']:
                # Execute with engine
                execution_result = await self.engine.execute_workflow(
                    workflow['definition'],
                    full_context,
                    execution_mode,
                    OptimizationStrategy.BALANCED
                )
                
                # Record execution metrics
                await self._record_execution_metrics(
                    workflow_id, instance_id, execution_result
                )
                
                # Update workflow statistics
                await self._update_workflow_stats(workflow_id, execution_result)
                
                return {
                    'success': execution_result['success'],
                    'instance_id': instance_id,
                    'workflow_id': workflow_id,
                    'results': execution_result.get('results', {}),
                    'metrics': execution_result.get('metrics', {}),
                    'orchestration': orchestration_result
                }
            else:
                return {
                    'success': False,
                    'error': orchestration_result.get('error', 'Orchestration failed'),
                    'workflow_id': workflow_id,
                    'instance_id': instance_id
                }
                
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            await self.monitor.record_execution(workflow_id, {
                'success': False,
                'error': str(e),
                'duration': 0.0
            })
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow_id
            }

    async def create_workflow_from_template(
        self,
        template_id: str,
        name: str,
        customizations: Dict[str, Any] = None,
        created_by: str = "user"
    ) -> str:
        """
        Create a workflow from a template.
        
        Args:
            template_id: Template ID to use
            name: Name for new workflow
            customizations: Template customizations
            created_by: Creator identifier
            
        Returns:
            str: Workflow ID
        """
        try:
            # Get template
            template = await self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Customize template
            customization_result = await self.template_manager.customize_template(
                template_id, customizations or {}
            )
            
            # Create workflow from customized template
            workflow_id = await self.create_workflow(
                name=name,
                description=f"Workflow created from template: {template.metadata.name}",
                workflow_definition=customization_result['workflow_definition'],
                category=template.metadata.category.value,
                created_by=created_by,
                metadata={
                    'template_id': template_id,
                    'template_version': template.metadata.version,
                    'customizations': customizations or {}
                }
            )
            
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow from template: {str(e)}")
            raise

    async def schedule_workflow(
        self,
        workflow_id: str,
        schedule_config: Dict[str, Any],
        created_by: str = "user"
    ) -> str:
        """
        Schedule a workflow for execution.
        
        Args:
            workflow_id: ID of workflow to schedule
            schedule_config: Schedule configuration
            created_by: User creating the schedule
            
        Returns:
            str: Schedule ID
        """
        try:
            # Validate workflow exists
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            # Create schedule
            schedule_id = await self.scheduler.create_schedule(
                name=schedule_config.get('name', f"Schedule for {workflow_id}"),
                workflow_id=workflow_id,
                schedule_type=ScheduleType(schedule_config.get('type', 'one_time')),
                conditions=schedule_config.get('conditions', []),
                created_by=created_by,
                priority=Priority(schedule_config.get('priority', 'medium')),
                timezone=schedule_config.get('timezone', 'UTC'),
                **schedule_config
            )
            
            # Update statistics
            self.agent_stats['schedules_managed'] += 1
            
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling workflow: {str(e)}")
            raise

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        try:
            # Get workflow info
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return {'error': 'Workflow not found'}
            
            # Get health status
            health_status = await self.monitor.get_workflow_health(workflow_id)
            
            # Get performance report
            performance_report = await self.monitor.get_performance_report(workflow_id, 24)
            
            # Get active schedules
            schedules = await self.scheduler.list_schedules()
            workflow_schedules = [s for s in schedules if s['workflow_id'] == workflow_id]
            
            return {
                'workflow': {
                    'id': workflow['id'],
                    'name': workflow['name'],
                    'description': workflow['description'],
                    'category': workflow['category'],
                    'status': workflow['status'],
                    'created_at': workflow['created_at'].isoformat(),
                    'execution_count': workflow['execution_count'],
                    'success_rate': workflow['success_rate']
                },
                'health': health_status,
                'performance': {
                    'total_executions': performance_report.total_executions,
                    'success_rate': 1 - performance_report.error_rate,
                    'average_duration': performance_report.average_duration,
                    'throughput': performance_report.throughput
                },
                'schedules': len(workflow_schedules),
                'monitoring': {
                    'alerts_active': health_status.get('active_alerts', 0),
                    'last_execution': health_status.get('last_execution')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {str(e)}")
            return {'error': str(e)}

    async def list_workflows(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List workflows with optional filtering."""
        try:
            workflows = []
            
            for workflow in self.workflows.values():
                # Apply filters
                if category and workflow['category'] != category:
                    continue
                if status and workflow['status'] != status:
                    continue
                if created_by and workflow['created_by'] != created_by:
                    continue
                
                # Get basic status info
                workflows.append({
                    'id': workflow['id'],
                    'name': workflow['name'],
                    'description': workflow['description'],
                    'category': workflow['category'],
                    'status': workflow['status'],
                    'created_by': workflow['created_by'],
                    'created_at': workflow['created_at'].isoformat(),
                    'execution_count': workflow['execution_count'],
                    'success_rate': workflow['success_rate']
                })
            
            # Sort by creation date (newest first)
            workflows.sort(key=lambda w: w['created_at'], reverse=True)
            
            return workflows
            
        except Exception as e:
            self.logger.error(f"Error listing workflows: {str(e)}")
            return []

    async def search_templates(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search workflow templates."""
        try:
            return await self.template_manager.search_templates(
                category=TemplateCategory(query.get('category')) if query.get('category') else None,
                template_type=TemplateType(query.get('type')) if query.get('type') else None,
                tags=query.get('tags'),
                complexity_level=query.get('complexity_level'),
                query=query.get('search_text')
            )
            
        except Exception as e:
            self.logger.error(f"Error searching templates: {str(e)}")
            return []

    async def get_template_recommendations(
        self,
        user_id: str,
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get template recommendations for user."""
        try:
            return await self.template_manager.get_template_recommendations(
                user_id, user_profile
            )
            
        except Exception as e:
            self.logger.error(f"Error getting recommendations: {str(e)}")
            return []

    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Get comprehensive agent statistics."""
        try:
            # Get component statistics
            orchestrator_stats = await self.orchestrator.get_execution_stats()
            engine_stats = await self.engine.get_performance_metrics()
            template_stats = await self.template_manager.get_template_analytics()
            scheduler_stats = await self.scheduler.get_scheduler_stats()
            monitor_stats = await self.monitor.get_monitoring_stats()
            
            return {
                'agent_stats': self.agent_stats.copy(),
                'orchestrator': orchestrator_stats,
                'engine': engine_stats,
                'templates': template_stats,
                'scheduler': scheduler_stats,
                'monitor': monitor_stats,
                'component_health': {
                    'orchestrator': 'healthy',
                    'engine': 'healthy',
                    'templates': 'healthy',
                    'scheduler': 'healthy' if scheduler_stats.get('scheduler_running') else 'stopped',
                    'monitor': 'healthy' if monitor_stats.get('monitoring_active') else 'stopped'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting agent statistics: {str(e)}")
            return {'error': str(e)}

    async def _load_builtin_workflows(self):
        """Load built-in workflows."""
        try:
            # Content creation workflow
            content_workflow = {
                'name': 'Content Creation Pipeline',
                'description': 'Complete content creation and publishing pipeline',
                'workflow_definition': {
                    'id': 'content_creation_pipeline',
                    'nodes': [
                        {
                            'id': 'content_generation',
                            'name': 'Generate Content',
                            'task_type': 'content_agent',
                            'executor': 'generate_content'
                        },
                        {
                            'id': 'content_optimization',
                            'name': 'Optimize Content',
                            'task_type': 'seo_agent',
                            'executor': 'optimize_content',
                            'dependencies': ['content_generation']
                        },
                        {
                            'id': 'content_publishing',
                            'name': 'Publish Content',
                            'task_type': 'distribution_agent',
                            'executor': 'publish_content',
                            'dependencies': ['content_optimization']
                        }
                    ],
                    'edges': [
                        {'from': 'content_generation', 'to': 'content_optimization'},
                        {'from': 'content_optimization', 'to': 'content_publishing'}
                    ]
                },
                'category': 'content_creation'
            }
            
            await self.create_workflow(**content_workflow)
            
            # Music protection workflow
            music_protection_workflow = {
                'name': 'Music Protection Pipeline',
                'description': 'Complete music content protection and monitoring',
                'workflow_definition': {
                    'id': 'music_protection_pipeline',
                    'nodes': [
                        {
                            'id': 'audio_fingerprinting',
                            'name': 'Generate Audio Fingerprint',
                            'task_type': 'fingerprinting_agent',
                            'executor': 'generate_audio_fingerprint'
                        },
                        {
                            'id': 'protection_registration',
                            'name': 'Register Protection',
                            'task_type': 'protection_agent',
                            'executor': 'register_protection',
                            'dependencies': ['audio_fingerprinting']
                        },
                        {
                            'id': 'monitoring_setup',
                            'name': 'Setup Monitoring',
                            'task_type': 'crawling_agent',
                            'executor': 'setup_monitoring',
                            'dependencies': ['protection_registration']
                        }
                    ],
                    'edges': [
                        {'from': 'audio_fingerprinting', 'to': 'protection_registration'},
                        {'from': 'protection_registration', 'to': 'monitoring_setup'}
                    ]
                },
                'category': 'content_protection'
            }
            
            await self.create_workflow(**music_protection_workflow)
            
        except Exception as e:
            self.logger.error(f"Error loading builtin workflows: {str(e)}")

    async def _initialize_agent_integrations(self):
        """Initialize integrations with other agents."""
        try:
            # Placeholder for agent integrations
            # In a real implementation, this would set up connections to other agents
            self.agent_integrations = {
                'spotify_agent': True,
                'content_agent': True,
                'protection_agent': True,
                'seo_agent': True,
                'distribution_agent': True
            }
            
        except Exception as e:
            self.logger.error(f"Error initializing agent integrations: {str(e)}")

    async def _record_execution_metrics(
        self,
        workflow_id: str,
        instance_id: str,
        execution_result: Dict[str, Any]
    ):
        """Record execution metrics."""
        try:
            execution_data = {
                'instance_id': instance_id,
                'success': execution_result.get('success', False),
                'duration': execution_result.get('metrics', {}).get('duration', 0.0),
                'nodes_executed': execution_result.get('nodes_executed', 0),
                'resource_usage': execution_result.get('metrics', {}).get('resource_utilization', {}),
                'error': execution_result.get('error') if not execution_result.get('success') else None
            }
            
            await self.monitor.record_execution(workflow_id, execution_data)
            
        except Exception as e:
            self.logger.error(f"Error recording execution metrics: {str(e)}")

    async def _update_workflow_stats(
        self,
        workflow_id: str,
        execution_result: Dict[str, Any]
    ):
        """Update workflow statistics."""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return
            
            # Update execution count
            workflow['execution_count'] += 1
            
            # Update success rate
            if execution_result.get('success', False):
                # Simple moving average for success rate
                current_success_rate = workflow['success_rate']
                execution_count = workflow['execution_count']
                
                # Weight recent executions more heavily
                if execution_count == 1:
                    workflow['success_rate'] = 1.0
                else:
                    alpha = 0.1  # Smoothing factor
                    workflow['success_rate'] = (1 - alpha) * current_success_rate + alpha * 1.0
            else:
                current_success_rate = workflow['success_rate']
                execution_count = workflow['execution_count']
                
                if execution_count == 1:
                    workflow['success_rate'] = 0.0
                else:
                    alpha = 0.1
                    workflow['success_rate'] = (1 - alpha) * current_success_rate + alpha * 0.0
            
            workflow['updated_at'] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error updating workflow stats: {str(e)}")

    async def shutdown(self):
        """Shutdown the workflow agent gracefully."""
        try:
            self.logger.info("Shutting down Workflow Agent...")
            
            # Stop monitoring
            await self.monitor.stop_monitoring()
            
            # Stop scheduler
            await self.scheduler.stop_scheduler()
            
            # Shutdown engine
            await self.engine.shutdown()
            
            self.logger.info("Workflow Agent shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

    # Additional utility methods
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow (stop scheduling and execution)."""
        try:
            if workflow_id in self.workflows:
                self.workflows[workflow_id]['status'] = 'paused'
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error pausing workflow: {str(e)}")
            return False

    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        try:
            if workflow_id in self.workflows:
                self.workflows[workflow_id]['status'] = 'active'
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error resuming workflow: {str(e)}")
            return False

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        try:
            if workflow_id in self.workflows:
                # Update statistics
                self.agent_stats['active_workflows'] -= 1
                
                # Remove workflow
                del self.workflows[workflow_id]
                
                # Cancel any schedules
                schedules = await self.scheduler.list_schedules()
                for schedule in schedules:
                    if schedule['workflow_id'] == workflow_id:
                        await self.scheduler.delete_schedule(schedule['id'])
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting workflow: {str(e)}")
            return False

    async def update_workflow(
        self,
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update workflow properties."""
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                return False
            
            # Update allowed fields
            allowed_updates = ['name', 'description', 'category', 'metadata']
            for field in allowed_updates:
                if field in updates:
                    workflow[field] = updates[field]
            
            workflow['updated_at'] = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating workflow: {str(e)}")
            return False
    WAITING = "waiting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowPriority(Enum):
    """Workflow execution priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


@dataclass
class WorkflowTask:
    """Individual workflow task definition."""
    id: str
    name: str
    function: Callable
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    timeout: int = 300
    status: TaskStatus = TaskStatus.WAITING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None


@dataclass
class WorkflowDefinition:
    """Complete workflow definition structure."""
    id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    max_parallel_tasks: int = 5
    timeout: int = 3600
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution state and tracking."""
    id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    task_results: Dict[str, Any] = field(default_factory=dict)
    error_log: List[str] = field(default_factory=list)
    progress: float = 0.0
    current_task: Optional[str] = None


class WorkflowAgent(BaseAgent):
    """
    Advanced Workflow Agent for enterprise workflow orchestration.
    
    Provides comprehensive workflow management capabilities including:
    - Dynamic workflow creation and execution
    - AI-powered workflow optimization
    - Real-time monitoring and analytics
    - Intelligent error handling and recovery
    - Scalable parallel execution
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Workflow Agent with enterprise configuration."""
        super().__init__(config)
        
        # Core configuration
        self.max_concurrent_workflows = config.get('max_concurrent_workflows', 50)
        self.max_parallel_tasks = config.get('max_parallel_tasks', 10)
        self.default_timeout = config.get('default_timeout', 3600)
        self.retry_attempts = config.get('retry_attempts', 3)
        
        # Workflow storage and tracking
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}
        
        # Execution engine
        self.executor = ThreadPoolExecutor(max_workers=self.max_parallel_tasks)
        self.task_queue: asyncio.Queue = asyncio.Queue()
        
        # Monitoring and analytics
        self.workflow_stats: Dict[str, Any] = {
            'total_executed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'peak_concurrent_workflows': 0
        }
        
        # AI optimization engine
        self.optimization_enabled = config.get('optimization_enabled', True)
        self.learning_rate = config.get('learning_rate', 0.01)
        
        self.logger.info("Workflow Agent initialized with enterprise configuration")
    
    async def create_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]],
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        **kwargs
    ) -> str:
        """
        Create a new workflow definition.
        
        Args:
            name: Workflow name
            description: Workflow description
            tasks: List of task definitions
            priority: Execution priority
            **kwargs: Additional workflow parameters
            
        Returns:
            str: Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Convert task definitions to WorkflowTask objects
            workflow_tasks = []
            for task_def in tasks:
                task = WorkflowTask(
                    id=task_def.get('id', str(uuid.uuid4())),
                    name=task_def['name'],
                    function=task_def['function'],
                    dependencies=task_def.get('dependencies', []),
                    parameters=task_def.get('parameters', {}),
                    retry_count=task_def.get('retry_count', self.retry_attempts),
                    timeout=task_def.get('timeout', 300)
                )
                workflow_tasks.append(task)
            
            # Create workflow definition
            workflow = WorkflowDefinition(
                id=workflow_id,
                name=name,
                description=description,
                tasks=workflow_tasks,
                priority=priority,
                max_parallel_tasks=kwargs.get('max_parallel_tasks', self.max_parallel_tasks),
                timeout=kwargs.get('timeout', self.default_timeout),
                retry_policy=kwargs.get('retry_policy', {}),
                metadata=kwargs.get('metadata', {})
            )
            
            # Validate workflow
            await self._validate_workflow(workflow)
            
            # Store workflow
            self.workflows[workflow_id] = workflow
            
            self.logger.info(f"Created workflow: {name} ({workflow_id})")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {str(e)}")
            raise
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = False
    ) -> Union[str, Tuple[str, Any]]:
        """
        Execute a workflow asynchronously or synchronously.
        
        Args:
            workflow_id: Workflow ID to execute
            input_data: Input data for workflow execution
            wait_for_completion: Whether to wait for completion
            
        Returns:
            Union[str, Tuple[str, Any]]: Execution ID or (execution_id, result)
        """
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            # Check concurrent workflow limit
            if len(self.running_workflows) >= self.max_concurrent_workflows:
                raise RuntimeError("Maximum concurrent workflows limit reached")
            
            # Create execution instance
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                start_time=datetime.now()
            )
            self.executions[execution_id] = execution
            
            # Start workflow execution
            workflow_task = asyncio.create_task(
                self._execute_workflow_internal(workflow_id, execution_id, input_data)
            )
            self.running_workflows[execution_id] = workflow_task
            
            self.logger.info(f"Started workflow execution: {execution_id}")
            
            if wait_for_completion:
                result = await workflow_task
                return execution_id, result
            else:
                return execution_id
                
        except Exception as e:
            self.logger.error(f"Failed to execute workflow: {str(e)}")
            raise
    
    async def _execute_workflow_internal(
        self,
        workflow_id: str,
        execution_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Internal workflow execution engine."""
        workflow = self.workflows[workflow_id]
        execution = self.executions[execution_id]
        
        try:
            execution.status = WorkflowStatus.RUNNING
            
            # Build task dependency graph
            task_graph = self._build_dependency_graph(workflow.tasks)
            
            # Execute tasks in topological order
            completed_tasks = set()
            task_results = {}
            
            while len(completed_tasks) < len(workflow.tasks):
                # Find executable tasks (dependencies completed)
                executable_tasks = []
                for task in workflow.tasks:
                    if (task.id not in completed_tasks and 
                        all(dep in completed_tasks for dep in task.dependencies)):
                        executable_tasks.append(task)
                
                if not executable_tasks:
                    raise RuntimeError("Circular dependency or deadlock detected")
                
                # Execute tasks in parallel (limited by max_parallel_tasks)
                semaphore = asyncio.Semaphore(workflow.max_parallel_tasks)
                task_futures = []
                
                for task in executable_tasks[:workflow.max_parallel_tasks]:
                    future = asyncio.create_task(
                        self._execute_task(task, task_results, semaphore, input_data)
                    )
                    task_futures.append((task, future))
                
                # Wait for task completion
                for task, future in task_futures:
                    try:
                        result = await future
                        task_results[task.id] = result
                        completed_tasks.add(task.id)
                        execution.progress = len(completed_tasks) / len(workflow.tasks) * 100
                        
                    except Exception as e:
                        self.logger.error(f"Task {task.name} failed: {str(e)}")
                        if task.retry_count > 0:
                            # Implement retry logic
                            task.retry_count -= 1
                            task.status = TaskStatus.RETRYING
                            continue
                        else:
                            execution.status = WorkflowStatus.FAILED
                            execution.error_log.append(f"Task {task.name} failed: {str(e)}")
                            raise
            
            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            execution.task_results = task_results
            
            # Update statistics
            await self._update_workflow_stats(workflow_id, execution)
            
            # AI optimization learning
            if self.optimization_enabled:
                await self._learn_from_execution(workflow_id, execution)
            
            self.logger.info(f"Workflow execution completed: {execution_id}")
            return task_results
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.now()
            execution.error_log.append(str(e))
            self.logger.error(f"Workflow execution failed: {execution_id} - {str(e)}")
            raise
        
        finally:
            # Clean up running workflow tracking
            if execution_id in self.running_workflows:
                del self.running_workflows[execution_id]
    
    async def _execute_task(
        self,
        task: WorkflowTask,
        context: Dict[str, Any],
        semaphore: asyncio.Semaphore,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute an individual workflow task."""
        async with semaphore:
            try:
                task.status = TaskStatus.RUNNING
                task.start_time = datetime.now()
                
                # Prepare task parameters
                task_params = {**task.parameters}
                if input_data:
                    task_params.update(input_data)
                
                # Add context from previous tasks
                task_params['context'] = context
                
                # Execute task function
                if asyncio.iscoroutinefunction(task.function):
                    result = await asyncio.wait_for(
                        task.function(**task_params),
                        timeout=task.timeout
                    )
                else:
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(self.executor, task.function, **task_params),
                        timeout=task.timeout
                    )
                
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.end_time = datetime.now()
                task.execution_time = (task.end_time - task.start_time).total_seconds()
                
                self.logger.debug(f"Task completed: {task.name}")
                return result
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.end_time = datetime.now()
                self.logger.error(f"Task failed: {task.name} - {str(e)}")
                raise
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed workflow execution status."""
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")
        
        execution = self.executions[execution_id]
        workflow = self.workflows[execution.workflow_id]
        
        # Get task statuses
        task_statuses = []
        for task in workflow.tasks:
            task_status = {
                'id': task.id,
                'name': task.name,
                'status': task.status.value,
                'start_time': task.start_time.isoformat() if task.start_time else None,
                'end_time': task.end_time.isoformat() if task.end_time else None,
                'execution_time': task.execution_time,
                'error': task.error
            }
            task_statuses.append(task_status)
        
        return {
            'execution_id': execution_id,
            'workflow_id': execution.workflow_id,
            'workflow_name': workflow.name,
            'status': execution.status.value,
            'progress': execution.progress,
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'execution_time': execution.execution_time,
            'current_task': execution.current_task,
            'task_statuses': task_statuses,
            'error_log': execution.error_log
        }
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        try:
            if execution_id in self.running_workflows:
                workflow_task = self.running_workflows[execution_id]
                workflow_task.cancel()
                
                # Update execution status
                if execution_id in self.executions:
                    execution = self.executions[execution_id]
                    execution.status = WorkflowStatus.CANCELLED
                    execution.end_time = datetime.now()
                
                self.logger.info(f"Workflow execution cancelled: {execution_id}")
                return True
            else:
                self.logger.warning(f"Workflow execution not running: {execution_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow: {str(e)}")
            return False
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a running workflow execution."""
        # Implementation for workflow pausing
        # This would require more complex state management
        self.logger.info(f"Workflow pause requested: {execution_id}")
        return True
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow execution."""
        # Implementation for workflow resuming
        self.logger.info(f"Workflow resume requested: {execution_id}")
        return True
    
    def _build_dependency_graph(self, tasks: List[WorkflowTask]) -> Dict[str, List[str]]:
        """Build task dependency graph for execution planning."""
        graph = {}
        for task in tasks:
            graph[task.id] = task.dependencies.copy()
        return graph
    
    async def _validate_workflow(self, workflow: WorkflowDefinition):
        """Validate workflow definition for consistency and correctness."""
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = next((t for t in workflow.tasks if t.id == task_id), None)
            if task:
                for dep in task.dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        for task in workflow.tasks:
            if task.id not in visited:
                if has_cycle(task.id):
                    raise ValueError("Circular dependency detected in workflow")
        
        # Validate task dependencies exist
        task_ids = {task.id for task in workflow.tasks}
        for task in workflow.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    raise ValueError(f"Invalid dependency: {dep} not found in workflow tasks")
    
    async def _update_workflow_stats(self, workflow_id: str, execution: WorkflowExecution):
        """Update workflow execution statistics for monitoring."""
        self.workflow_stats['total_executed'] += 1
        
        if execution.status == WorkflowStatus.COMPLETED:
            self.workflow_stats['successful_executions'] += 1
        elif execution.status == WorkflowStatus.FAILED:
            self.workflow_stats['failed_executions'] += 1
        
        if execution.execution_time:
            current_avg = self.workflow_stats['average_execution_time']
            total = self.workflow_stats['total_executed']
            self.workflow_stats['average_execution_time'] = (
                (current_avg * (total - 1) + execution.execution_time) / total
            )
        
        # Update peak concurrent workflows
        current_concurrent = len(self.running_workflows)
        if current_concurrent > self.workflow_stats['peak_concurrent_workflows']:
            self.workflow_stats['peak_concurrent_workflows'] = current_concurrent
    
    async def _learn_from_execution(self, workflow_id: str, execution: WorkflowExecution):
        """AI-powered learning from workflow execution for optimization."""
        if execution.status == WorkflowStatus.COMPLETED and execution.execution_time:
            workflow = self.workflows[workflow_id]
            
            # Simple learning algorithm - adjust task timeouts based on actual execution times
            for task in workflow.tasks:
                if task.execution_time and task.execution_time > task.timeout * 0.8:
                    # Increase timeout by 20% if task took more than 80% of allowed time
                    new_timeout = int(task.timeout * 1.2)
                    task.timeout = min(new_timeout, 3600)  # Cap at 1 hour
                elif task.execution_time and task.execution_time < task.timeout * 0.3:
                    # Decrease timeout by 10% if task took less than 30% of allowed time
                    new_timeout = int(task.timeout * 0.9)
                    task.timeout = max(new_timeout, 30)  # Minimum 30 seconds
    
    async def get_workflow_analytics(self) -> Dict[str, Any]:
        """Get comprehensive workflow analytics and statistics."""
        active_workflows = len(self.running_workflows)
        total_workflows = len(self.workflows)
        
        # Calculate success rate
        success_rate = 0.0
        if self.workflow_stats['total_executed'] > 0:
            success_rate = (self.workflow_stats['successful_executions'] / 
                          self.workflow_stats['total_executed']) * 100
        
        return {
            'total_workflows_defined': total_workflows,
            'active_executions': active_workflows,
            'execution_statistics': self.workflow_stats,
            'success_rate_percentage': round(success_rate, 2),
            'system_health': {
                'executor_threads': self.executor._threads,
                'max_concurrent_workflows': self.max_concurrent_workflows,
                'current_concurrent_workflows': active_workflows
            }
        }
    
    async def cleanup_completed_executions(self, older_than_hours: int = 24):
        """Clean up old completed workflow executions to free memory."""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        executions_to_remove = []
        for execution_id, execution in self.executions.items():
            if (execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED] and
                execution.end_time and execution.end_time < cutoff_time):
                executions_to_remove.append(execution_id)
        
        for execution_id in executions_to_remove:
            del self.executions[execution_id]
        
        self.logger.info(f"Cleaned up {len(executions_to_remove)} old workflow executions")
        return len(executions_to_remove)

    async def export_workflow_definition(self, workflow_id: str) -> Dict[str, Any]:
        """Export workflow definition for backup or sharing."""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        
        # Convert to serializable format
        return {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'priority': workflow.priority.value,
            'max_parallel_tasks': workflow.max_parallel_tasks,
            'timeout': workflow.timeout,
            'retry_policy': workflow.retry_policy,
            'metadata': workflow.metadata,
            'tasks': [
                {
                    'id': task.id,
                    'name': task.name,
                    'dependencies': task.dependencies,
                    'parameters': task.parameters,
                    'retry_count': task.retry_count,
                    'timeout': task.timeout
                }
                for task in workflow.tasks
            ]
        }
    
    async def import_workflow_definition(self, workflow_data: Dict[str, Any]) -> str:
        """Import workflow definition from exported data."""
        # This would require function resolution mechanism
        # For now, just store the structure
        workflow_id = workflow_data['id']
        self.logger.info(f"Importing workflow definition: {workflow_id}")
        return workflow_id
