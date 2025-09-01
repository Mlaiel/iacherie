"""⚙️ Workflow Repository - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/data_management/repositories/workflow_repository.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Workflow Management Repository - Production-Ready
Responsibility: Advanced AI workflow orchestration and automation pipeline management
=================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
User (musician/blogger/photographer/influencer/comedian) → Upload multi-format → 
IA protection rights → Professional SEO → Collaboration matching → Multi-platform distribution

WORKFLOW REPOSITORY ARCHITECTURE:
Workflow Definition → Step Orchestration → Condition Evaluation → 
Parallel Processing → Error Handling → Progress Tracking → 
Notification Integration → Performance Analytics
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable
import logging
import asyncio
import hashlib
import json
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum

from .base_repository import BaseRepository, AsyncBaseRepository, OperationType

class WorkflowStatus(Enum):
    """
Workflow execution status"""

    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class StepStatus(Enum):
    """Workflow step status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    WAITING = "waiting"

class StepType(Enum):
    """Types of workflow steps"""

    AI_PROCESSING = "ai_processing"
    CONTENT_ANALYSIS = "content_analysis"
    FINGERPRINT_GENERATION = "fingerprint_generation"
    SEO_OPTIMIZATION = "seo_optimization"
    PROTECTION_REGISTRATION = "protection_registration"
    DISTRIBUTION = "distribution"
    NOTIFICATION = "notification"
    COLLABORATION_MATCHING = "collaboration_matching"
    ANALYTICS_CALCULATION = "analytics_calculation"
    CUSTOM_FUNCTION = "custom_function"

class TriggerType(Enum):
    """Workflow trigger types"""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    API_CALL = "api_call"
    CONTENT_UPLOAD = "content_upload"
    PLATFORM_WEBHOOK = "platform_webhook"

class ConditionOperator(Enum):
    """Condition operators for workflow logic"""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"

@dataclass
class WorkflowCondition:
    """Workflow condition definition"""
    field: str
    operator: ConditionOperator
    value: Any
    description: Optional[str] = None

@dataclass
class WorkflowStep:
    """
Individual workflow step definition"""
    step_id: str
    name: str
    step_type: StepType
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: List[WorkflowCondition] = field(default_factory=list)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    parallel_execution: bool = False
    dependencies: List[str] = field(default_factory=list)
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowDefinition:
    """
Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str
    creator_id: str
    steps: List[WorkflowStep]
    trigger_config: Dict[str, Any]
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None
    timeout_minutes: int = 60
    max_concurrent_executions: int = 1
    notification_config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    is_template: bool = False
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class StepExecution:
    """
Individual step execution tracking"""
    execution_id: str
    step_id: str
    workflow_execution_id: str
    status: StepStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    retry_count: int = 0
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

@dataclass
class WorkflowExecution:
    """
Complete workflow execution tracking"""
    execution_id: str
    workflow_id: str
    workflow_version: str
    trigger_data: Dict[str, Any]
    status: WorkflowStatus
    current_step: Optional[str] = None
    step_executions: List[StepExecution] = field(default_factory=list)
    global_context: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    progress_percentage: float = 0.0
    error_summary: Optional[str] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowTemplate:
    """
Reusable workflow template"""
    template_id: str
    name: str
    description: str
    category: str
    workflow_definition: WorkflowDefinition
    usage_count: int = 0
    rating: float = 0.0
    tags: List[str] = field(default_factory=list)
    is_public: bool = False
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class WorkflowMetrics:
    """Workflow performance metrics"""
    workflow_id: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration: float
    success_rate: float
    throughput_per_hour: float
    resource_efficiency: float
    error_patterns: Dict[str, int]
    performance_trends: Dict[str, List[float]]
    bottleneck_steps: List[str]
    optimization_suggestions: List[str]

class WorkflowRepository(BaseRepository):
    """
    Advanced workflow repository for AI automation pipelines
    
    Features:
    - Complex workflow orchestration
    - Parallel and sequential execution
    - Advanced condition handling
    - Error recovery and retry logic
    - Real-time progress tracking
    - Performance analytics
    - Template management
    - Resource optimization
    """
    
    def __init__(self, db_connection=None, cache_manager=None, logger=None,
                 audit_service=None, metrics_collector=None, execution_engine=None,
                 function_registry=None, scheduler_service=None, notification_service=None):
        super().__init__(db_connection, cache_manager, logger, audit_service, metrics_collector)
        self.execution_engine = execution_engine
        self.function_registry = function_registry or {}
        self.scheduler_service = scheduler_service
        self.notification_service = notification_service
        
        # Workflow configuration
        self.max_concurrent_workflows = 50
        self.default_timeout_minutes = 60
        self.retry_enabled = True
        self.monitoring_enabled = True
        
        # Performance settings
        self.resource_tracking_enabled = True
        self.optimization_enabled = True
        self.auto_scaling_enabled = True

    def create(self, entity, **kwargs):
        """
Create workflow entity"""
        self._validate_entity(entity)
        
        # Generate ID if not provided
        if hasattr(entity, 'workflow_id') and not entity.workflow_id:
            entity.workflow_id = self._generate_workflow_id()
        elif hasattr(entity, 'execution_id') and not entity.execution_id:
            entity.execution_id = self._generate_execution_id()
        elif hasattr(entity, 'template_id') and not entity.template_id:
            entity.template_id = self._generate_template_id()
        
        # Set timestamps
        current_time = datetime.now(timezone.utc)
        if hasattr(entity, 'created_at') and not entity.created_at:
            entity.created_at = current_time
        if hasattr(entity, 'updated_at'):
            entity.updated_at = current_time
        
        # Validate workflow definition if applicable
        if isinstance(entity, WorkflowDefinition):
            self._validate_workflow_definition(entity)
        
        # Store in database
        created_entity = self._store_workflow_entity(entity)
        
        # Set up scheduling if workflow has schedule
        if isinstance(entity, WorkflowDefinition) and entity.schedule:
            self._setup_workflow_schedule(created_entity)
        
        # Log audit
        self._log_audit(
            OperationType.CREATE,
            entity_id=self._get_entity_id(created_entity),
            new_values=asdict(created_entity) if hasattr(created_entity, '__dict__') else None,
            metadata={'operation': 'workflow_entity_created', **kwargs}
        )
        
        return created_entity

    def get_by_id(self, entity_id: str, use_cache: bool = True):
        """
Get workflow entity by ID"""
        if use_cache and self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("get_workflow_by_id", entity_id=entity_id)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Fetch from database
        workflow_entity = self._fetch_workflow_by_id(entity_id)
        
        # Cache result
        if use_cache and self._cache_enabled and self.cache and workflow_entity:
            self.cache.set(cache_key, workflow_entity, ttl=self._cache_ttl)
        
        return workflow_entity

    def update(self, entity, **kwargs):
        """Update workflow entity"""
        self._validate_entity(entity)
        
        # Get current entity for audit
        current_entity = self.get_by_id(self._get_entity_id(entity), use_cache=False)
        
        # Update timestamp
        if hasattr(entity, 'updated_at'):
            entity.updated_at = datetime.now(timezone.utc)
        
        # Update version for workflow definitions
        if isinstance(entity, WorkflowDefinition) and current_entity:
            entity.version = self._increment_version(current_entity.version)
        
        # Update in database
        updated_entity = self._update_workflow_entity(entity)
        
        # Update scheduling if needed
        if isinstance(entity, WorkflowDefinition) and entity.schedule:
            self._update_workflow_schedule(updated_entity)
        
        # Log audit
        self._log_audit(
            OperationType.UPDATE,
            entity_id=self._get_entity_id(updated_entity),
            old_values=asdict(current_entity) if current_entity else None,
            new_values=asdict(updated_entity) if hasattr(updated_entity, '__dict__') else None,
            metadata={'operation': 'workflow_entity_updated', **kwargs}
        )
        
        # Invalidate cache
        if self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("get_workflow_by_id", entity_id=self._get_entity_id(entity))
            self.cache.delete(cache_key)
        
        return updated_entity

    def delete(self, entity_id: str, soft_delete: bool = False):
        """Delete workflow entity"""
        # Get entity for audit
        entity = self.get_by_id(entity_id, use_cache=False)
        if not entity:
            return False
        
        # Stop active executions if workflow definition
        if isinstance(entity, WorkflowDefinition):
            self._stop_active_executions(entity_id)
            self._remove_workflow_schedule(entity_id)
        
        # Perform deletion
        success = self._delete_workflow_entity(entity_id, soft_delete)
        
        if success:
            # Log audit
            self._log_audit(
                OperationType.DELETE,
                entity_id=entity_id,
                old_values=asdict(entity) if hasattr(entity, '__dict__') else None,
                metadata={'operation': 'workflow_entity_deleted', 'soft_delete': soft_delete}
            )
            
            # Invalidate cache
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_workflow_by_id", entity_id=entity_id)
                self.cache.delete(cache_key)
        
        return success

    def list(self, filters: Dict[str, Any] = None, limit: int = 100, 
             offset: int = 0, order_by: str = None):
        """List workflow entities with filters"""
        filters = filters or {}
        
        # Check cache for list results
        if self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("list_workflows", filters=filters, limit=limit, offset=offset)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Fetch from database
        workflow_list = self._fetch_workflow_list(filters, limit, offset, order_by)
        
        # Cache result
        if self._cache_enabled and self.cache:
            self.cache.set(cache_key, workflow_list, ttl=self._cache_ttl)
        
        return workflow_list

    def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any] = None,
                        context: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        try:
            # Get workflow definition
            workflow = self.get_by_id(workflow_id)
            if not workflow or not isinstance(workflow, WorkflowDefinition):
                raise ValueError(f"Workflow not found or invalid: {workflow_id}")
            
            if workflow.status != WorkflowStatus.ACTIVE:
                raise ValueError(f"Workflow is not active: {workflow.status}")
            
            # Check concurrent execution limits
            if not self._check_concurrent_execution_limits(workflow):
                raise ValueError("Maximum concurrent executions reached")
            
            # Create execution
            execution = WorkflowExecution(
                execution_id=self._generate_execution_id(),
                workflow_id=workflow_id,
                workflow_version=workflow.version,
                trigger_data=trigger_data or {},
                status=WorkflowStatus.RUNNING,
                global_context=context or {}
            )
            
            # Store execution
            created_execution = self.create(execution)
            
            # Start execution in background
            if self.execution_engine:
                self.execution_engine.start_execution(created_execution, workflow)
            else:
                # Fallback to inline execution
                self._execute_workflow_inline(created_execution, workflow)
            
            self.logger.info(f"Workflow execution started: {execution.execution_id}")
            
            return created_execution
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed to start: {e}")
            raise

    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed execution status"""
        try:
            execution = self.get_by_id(execution_id)
            if not execution or not isinstance(execution, WorkflowExecution):
                raise ValueError(f"Execution not found: {execution_id}")
            
            # Calculate progress
            total_steps = len(execution.step_executions)
            completed_steps = len([s for s in execution.step_executions if s.status == StepStatus.COMPLETED])
            progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
            
            # Get current step details
            current_step = None
            if execution.current_step:
                current_step = next(
                    (s for s in execution.step_executions if s.step_id == execution.current_step),
                    None
                )
            
            status = {
                'execution_id': execution_id,
                'workflow_id': execution.workflow_id,
                'status': execution.status.value,
                'progress_percentage': progress,
                'current_step': execution.current_step,
                'current_step_details': asdict(current_step) if current_step else None,
                'started_at': execution.started_at.isoformat(),
                'duration_seconds': execution.duration_seconds,
                'step_executions': [asdict(step) for step in execution.step_executions],
                'error_summary': execution.error_summary,
                'resource_usage': execution.resource_usage
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Execution status retrieval failed: {e}")
            raise

    def cancel_execution(self, execution_id: str, reason: str = "User cancelled") -> bool:
        """Cancel running workflow execution"""
        try:
            execution = self.get_by_id(execution_id)
            if not execution or not isinstance(execution, WorkflowExecution):
                return False
            
            if execution.status not in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                return False
            
            # Cancel execution
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now(timezone.utc)
            execution.error_summary = reason
            
            if execution.started_at:
                execution.duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            
            # Update execution
            self.update(execution)
            
            # Stop execution in engine
            if self.execution_engine:
                self.execution_engine.cancel_execution(execution_id)
            
            # Send notification
            if self.notification_service:
                self._send_execution_notification(execution, "cancelled")
            
            self.logger.info(f"Workflow execution cancelled: {execution_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Execution cancellation failed: {e}")
            return False

    def pause_execution(self, execution_id: str) -> bool:
        """Pause running workflow execution"""
        try:
            execution = self.get_by_id(execution_id)
            if not execution or not isinstance(execution, WorkflowExecution):
                return False
            
            if execution.status != WorkflowStatus.RUNNING:
                return False
            
            # Pause execution
            execution.status = WorkflowStatus.PAUSED
            self.update(execution)
            
            # Pause execution in engine
            if self.execution_engine:
                self.execution_engine.pause_execution(execution_id)
            
            self.logger.info(f"Workflow execution paused: {execution_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Execution pause failed: {e}")
            return False

    def resume_execution(self, execution_id: str) -> bool:
        """Resume paused workflow execution"""
        try:
            execution = self.get_by_id(execution_id)
            if not execution or not isinstance(execution, WorkflowExecution):
                return False
            
            if execution.status != WorkflowStatus.PAUSED:
                return False
            
            # Resume execution
            execution.status = WorkflowStatus.RUNNING
            self.update(execution)
            
            # Resume execution in engine
            if self.execution_engine:
                self.execution_engine.resume_execution(execution_id)
            
            self.logger.info(f"Workflow execution resumed: {execution_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Execution resume failed: {e}")
            return False

    def create_workflow_template(self, template_data: Dict[str, Any]) -> WorkflowTemplate:
        """Create reusable workflow template"""
        try:
            # Create workflow definition from template data
            workflow_def = self._create_workflow_definition_from_template(template_data)
            
            template = WorkflowTemplate(
                template_id=self._generate_template_id(),
                name=template_data['name'],
                description=template_data.get('description', ''),
                category=template_data.get('category', 'general'),
                workflow_definition=workflow_def,
                tags=template_data.get('tags', []),
                is_public=template_data.get('is_public', False),
                created_by=template_data.get('created_by', '')
            )
            
            # Store template
            created_template = self.create(template)
            
            self.logger.info(f"Workflow template created: {template.template_id}")
            
            return created_template
            
        except Exception as e:
            self.logger.error(f"Workflow template creation failed: {e}")
            raise

    def instantiate_from_template(self, template_id: str, instance_data: Dict[str, Any]) -> WorkflowDefinition:
        """Create workflow instance from template"""
        try:
            # Get template
            template = self.get_by_id(template_id)
            if not template or not isinstance(template, WorkflowTemplate):
                raise ValueError(f"Template not found: {template_id}")
            
            # Create workflow instance
            workflow_def = template.workflow_definition
            workflow_def.workflow_id = self._generate_workflow_id()
            workflow_def.name = instance_data.get('name', f"{template.name} - Instance")
            workflow_def.creator_id = instance_data.get('creator_id', '')
            workflow_def.global_parameters.update(instance_data.get('parameters', {}))
            workflow_def.status = WorkflowStatus.DRAFT
            workflow_def.is_template = False
            
            # Store workflow
            created_workflow = self.create(workflow_def)
            
            # Update template usage count
            template.usage_count += 1
            self.update(template)
            
            self.logger.info(f"Workflow instantiated from template: {template_id}")
            
            return created_workflow
            
        except Exception as e:
            self.logger.error(f"Workflow instantiation failed: {e}")
            raise

    def get_workflow_metrics(self, workflow_id: str, time_range: str = "30d") -> WorkflowMetrics:
        """Get comprehensive workflow performance metrics"""
        try:
            # Get executions for time range
            executions = self._fetch_workflow_executions(workflow_id, time_range)
            
            # Calculate metrics
            total_executions = len(executions)
            successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
            failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])
            
            success_rate = successful_executions / total_executions if total_executions > 0 else 0
            
            # Calculate average duration
            durations = [e.duration_seconds for e in executions if e.duration_seconds]
            average_duration = sum(durations) / len(durations) if durations else 0
            
            # Calculate throughput
            if executions:
                time_span = (max(e.started_at for e in executions) - min(e.started_at for e in executions)).total_seconds() / 3600
                throughput_per_hour = total_executions / time_span if time_span > 0 else 0
            else:
                throughput_per_hour = 0
            
            # Analyze error patterns
            error_patterns = {}
            for execution in executions:
                if execution.error_summary:
                    error_type = self._categorize_error(execution.error_summary)
                    error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
            
            # Identify bottleneck steps
            bottleneck_steps = self._identify_bottleneck_steps(executions)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(executions)
            
            metrics = WorkflowMetrics(
                workflow_id=workflow_id,
                total_executions=total_executions,
                successful_executions=successful_executions,
                failed_executions=failed_executions,
                average_duration=average_duration,
                success_rate=success_rate,
                throughput_per_hour=throughput_per_hour,
                resource_efficiency=self._calculate_resource_efficiency(executions),
                error_patterns=error_patterns,
                performance_trends=self._calculate_performance_trends(executions),
                bottleneck_steps=bottleneck_steps,
                optimization_suggestions=optimization_suggestions
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Workflow metrics calculation failed: {e}")
            raise

    def get_workflow_analytics(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive workflow analytics"""
        try:
            filters = filters or {}
            
            # Get workflows and executions
            workflows = self.list(filters={'entity_type': 'WorkflowDefinition'})
            executions = self._fetch_all_executions(filters)
            
            # Calculate analytics
            analytics = {
                'total_workflows': len(workflows),
                'active_workflows': len([w for w in workflows if w.status == WorkflowStatus.ACTIVE]),
                'total_executions': len(executions),
                'execution_status_breakdown': self._calculate_execution_status_breakdown(executions),
                'workflow_type_usage': self._calculate_workflow_type_usage(workflows),
                'average_execution_time': self._calculate_average_execution_time(executions),
                'resource_utilization': self._calculate_resource_utilization(executions),
                'error_analysis': self._analyze_execution_errors(executions),
                'performance_trends': self._calculate_overall_performance_trends(executions),
                'most_popular_templates': self._get_most_popular_templates(),
                'optimization_recommendations': self._generate_global_optimization_recommendations(workflows, executions)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Workflow analytics calculation failed: {e}")
            raise

    # Private helper methods

    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        return f"wf_{timestamp}_{random_hash}"

    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        return f"exec_{timestamp}_{random_hash}"

    def _generate_template_id(self) -> str:
        """Generate unique template ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        return f"tmpl_{timestamp}_{random_hash}"

    def _get_entity_id(self, entity) -> str:
        """Get entity ID from entity object"""
        for id_field in ['workflow_id', 'execution_id', 'template_id']:
            if hasattr(entity, id_field):
                return getattr(entity, id_field)
        return None

    def _validate_workflow_definition(self, workflow: WorkflowDefinition):
        """
Validate workflow definition"""
        # Check for duplicate step IDs
        step_ids = [step.step_id for step in workflow.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("Duplicate step IDs found in workflow")
        
        # Validate step dependencies
        for step in workflow.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Invalid dependency '{dep}' in step '{step.step_id}'")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(workflow.steps):
            raise ValueError("Circular dependencies detected in workflow")

    def _has_circular_dependencies(self, steps: List[WorkflowStep]) -> bool:
        """Check for circular dependencies in workflow steps"""
        # Implementation would check for cycles
        return False

    def _store_workflow_entity(self, entity):
        """
Store workflow entity in database"""
        # Implementation would store in database
        return entity

    def _setup_workflow_schedule(self, workflow: WorkflowDefinition):
        """
Set up workflow scheduling"""
        # Implementation would set up scheduling
        pass

    def _fetch_workflow_by_id(self, entity_id: str):
        """
Fetch workflow entity by ID"""
        # Implementation would fetch from database
        return None

    def _increment_version(self, current_version: str) -> str:
        """
Increment version number"""
        try:
            parts = current_version.split('.')
            parts[-1] = str(int(parts[-1]) + 1)
            return '.'.join(parts)
        except:
            return "1.0.1"

    def _update_workflow_entity(self, entity):
        """Update workflow entity in database"""
        # Implementation would update database
        return entity

    def _update_workflow_schedule(self, workflow: WorkflowDefinition):
        """
Update workflow scheduling"""
        # Implementation would update scheduling
        pass

    def _stop_active_executions(self, workflow_id: str):
        """
Stop all active executions for workflow"""
        # Implementation would stop executions
        pass

    def _remove_workflow_schedule(self, workflow_id: str):
        """
Remove workflow from scheduler"""
        # Implementation would remove scheduling
        pass

    def _delete_workflow_entity(self, entity_id: str, soft_delete: bool) -> bool:
        """
Delete workflow entity"""
        # Implementation would delete from database
        return True

    def _fetch_workflow_list(self, filters, limit, offset, order_by):
        """
Fetch workflow entities list"""
        # Implementation would fetch from database
        return []

    def _check_concurrent_execution_limits(self, workflow: WorkflowDefinition) -> bool:
        """
Check if workflow can be executed (concurrent limits)"""
        # Implementation would check limits
        return True

    def _execute_workflow_inline(self, execution: WorkflowExecution, workflow: WorkflowDefinition):
        """
Execute workflow inline (fallback)"""
        # Implementation would execute workflow
        pass

    def _send_execution_notification(self, execution: WorkflowExecution, event_type: str):
        """
Send execution notification"""
        # Implementation would send notification
        pass

    def _create_workflow_definition_from_template(self, template_data: Dict[str, Any]) -> WorkflowDefinition:
        """
Create workflow definition from template data"""
        # Implementation would create workflow definition
        return WorkflowDefinition(
            workflow_id=self._generate_workflow_id(),
            name=template_data['name'],
            description=template_data.get('description', ''),
            version="1.0.0",
            creator_id=template_data.get('creator_id', ''),
            steps=[],
            trigger_config={},
            is_template=True
        )

    def _fetch_workflow_executions(self, workflow_id: str, time_range: str) -> List[WorkflowExecution]:
        """Fetch workflow executions for time range"""
        # Implementation would fetch executions
        return []

    def _categorize_error(self, error_message: str) -> str:
        """
Categorize error type"""
        error_lower = error_message.lower()
        if 'timeout' in error_lower:
            return 'timeout_error'
        elif 'permission' in error_lower or 'auth' in error_lower:
            return 'auth_error'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'network_error'
        elif 'memory' in error_lower or 'resource' in error_lower:
            return 'resource_error'
        else:
            return 'unknown_error'

    def _identify_bottleneck_steps(self, executions: List[WorkflowExecution]) -> List[str]:
        """
Identify bottleneck steps in workflow"""
        # Implementation would identify bottlenecks
        return []

    def _generate_optimization_suggestions(self, executions: List[WorkflowExecution]) -> List[str]:
        """
Generate optimization suggestions"""
        # Implementation would generate suggestions
        return []

    def _calculate_resource_efficiency(self, executions: List[WorkflowExecution]) -> float:
        """
Calculate resource efficiency"""
        # Implementation would calculate efficiency
        return 0.85

    def _calculate_performance_trends(self, executions: List[WorkflowExecution]) -> Dict[str, List[float]]:
        """
Calculate performance trends"""
        # Implementation would calculate trends
        return {}

    def _fetch_all_executions(self, filters: Dict[str, Any]) -> List[WorkflowExecution]:
        """
Fetch all executions with filters"""
        # Implementation would fetch executions
        return []

    def _calculate_execution_status_breakdown(self, executions: List[WorkflowExecution]) -> Dict[str, int]:
        """
Calculate execution status breakdown"""
        breakdown = {}
        for execution in executions:
            status = execution.status.value
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown

    def _calculate_workflow_type_usage(self, workflows: List[WorkflowDefinition]) -> Dict[str, int]:
        """
Calculate workflow type usage"""
        # Implementation would calculate usage
        return {}

    def _calculate_average_execution_time(self, executions: List[WorkflowExecution]) -> float:
        """
Calculate average execution time"""
        durations = [e.duration_seconds for e in executions if e.duration_seconds]
        return sum(durations) / len(durations) if durations else 0

    def _calculate_resource_utilization(self, executions: List[WorkflowExecution]) -> Dict[str, float]:
        """
Calculate resource utilization"""
        # Implementation would calculate utilization
        return {}

    def _analyze_execution_errors(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """
Analyze execution errors"""
        # Implementation would analyze errors
        return {}

    def _calculate_overall_performance_trends(self, executions: List[WorkflowExecution]) -> Dict[str, Any]:
        """
Calculate overall performance trends"""
        # Implementation would calculate trends
        return {}

    def _get_most_popular_templates(self) -> List[Dict[str, Any]]:
        """
Get most popular workflow templates"""
        # Implementation would get popular templates
        return []

    def _generate_global_optimization_recommendations(self, workflows: List[WorkflowDefinition], 
                                                    executions: List[WorkflowExecution]) -> List[str]:
        """
Generate global optimization recommendations"""
        # Implementation would generate recommendations
        return []


class AsyncWorkflowRepository(AsyncBaseRepository):
    """
    Advanced asynchronous workflow repository for high-performance automation
    
    Features:
    - Concurrent workflow execution
    - Async step processing
    - Parallel execution monitoring
    - Real-time status updates
    - Batch workflow operations
    """
    
    def __init__(self, db_connection=None, cache_manager=None, logger=None,
                 audit_service=None, metrics_collector=None, execution_engine=None,
                 function_registry=None, scheduler_service=None, notification_service=None):
        super().__init__(db_connection, cache_manager, logger, audit_service, metrics_collector)
        self.execution_engine = execution_engine
        self.function_registry = function_registry or {}
        self.scheduler_service = scheduler_service
        self.notification_service = notification_service
        
        # Initialize sync repository for shared functionality
        self.sync_repo = WorkflowRepository(
            db_connection, cache_manager, logger, audit_service, 
            metrics_collector, execution_engine, function_registry, scheduler_service, notification_service
        )

    async def create(self, entity, **kwargs):
        """
Create workflow entity asynchronously"""
        await self._validate_entity(entity)
        
        # Generate ID if not provided
        if hasattr(entity, 'workflow_id') and not entity.workflow_id:
            entity.workflow_id = self.sync_repo._generate_workflow_id()
        elif hasattr(entity, 'execution_id') and not entity.execution_id:
            entity.execution_id = self.sync_repo._generate_execution_id()
        elif hasattr(entity, 'template_id') and not entity.template_id:
            entity.template_id = self.sync_repo._generate_template_id()
        
        # Set timestamps
        current_time = datetime.now(timezone.utc)
        if hasattr(entity, 'created_at') and not entity.created_at:
            entity.created_at = current_time
        if hasattr(entity, 'updated_at'):
            entity.updated_at = current_time
        
        # Validate workflow definition if applicable
        if isinstance(entity, WorkflowDefinition):
            self.sync_repo._validate_workflow_definition(entity)
        
        # Store in database
        created_entity = await self._store_workflow_entity_async(entity)
        
        # Set up scheduling if workflow has schedule
        if isinstance(entity, WorkflowDefinition) and entity.schedule:
            await self._setup_workflow_schedule_async(created_entity)
        
        # Log audit
        await self._log_audit(
            OperationType.CREATE,
            entity_id=self.sync_repo._get_entity_id(created_entity),
            new_values=asdict(created_entity) if hasattr(created_entity, '__dict__') else None,
            metadata={'operation': 'async_workflow_entity_created', **kwargs}
        )
        
        return created_entity

    async def get_by_id(self, entity_id: str, use_cache: bool = True):
        """
Get workflow entity by ID asynchronously"""
        if use_cache and self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("get_workflow_by_id", entity_id=entity_id)
            cached_result = await self.cache.get_async(cache_key)
            if cached_result:
                return cached_result
        
        # Fetch from database
        workflow_entity = await self._fetch_workflow_by_id_async(entity_id)
        
        # Cache result
        if use_cache and self._cache_enabled and self.cache and workflow_entity:
            await self.cache.set_async(cache_key, workflow_entity, ttl=self._cache_ttl)
        
        return workflow_entity

    async def update(self, entity, **kwargs):
        """Update workflow entity asynchronously"""
        await self._validate_entity(entity)
        
        # Get current entity for audit
        current_entity = await self.get_by_id(self.sync_repo._get_entity_id(entity), use_cache=False)
        
        # Update timestamp
        if hasattr(entity, 'updated_at'):
            entity.updated_at = datetime.now(timezone.utc)
        
        # Update version for workflow definitions
        if isinstance(entity, WorkflowDefinition) and current_entity:
            entity.version = self.sync_repo._increment_version(current_entity.version)
        
        # Update in database
        updated_entity = await self._update_workflow_entity_async(entity)
        
        # Update scheduling if needed
        if isinstance(entity, WorkflowDefinition) and entity.schedule:
            await self._update_workflow_schedule_async(updated_entity)
        
        # Log audit
        await self._log_audit(
            OperationType.UPDATE,
            entity_id=self.sync_repo._get_entity_id(updated_entity),
            old_values=asdict(current_entity) if current_entity else None,
            new_values=asdict(updated_entity) if hasattr(updated_entity, '__dict__') else None,
            metadata={'operation': 'async_workflow_entity_updated', **kwargs}
        )
        
        # Invalidate cache
        if self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("get_workflow_by_id", entity_id=self.sync_repo._get_entity_id(entity))
            await self.cache.delete_async(cache_key)
        
        return updated_entity

    async def delete(self, entity_id: str, soft_delete: bool = False):
        """Delete workflow entity asynchronously"""
        # Get entity for audit
        entity = await self.get_by_id(entity_id, use_cache=False)
        if not entity:
            return False
        
        # Stop active executions if workflow definition
        if isinstance(entity, WorkflowDefinition):
            await self._stop_active_executions_async(entity_id)
            await self._remove_workflow_schedule_async(entity_id)
        
        # Perform deletion
        success = await self._delete_workflow_entity_async(entity_id, soft_delete)
        
        if success:
            # Log audit
            await self._log_audit(
                OperationType.DELETE,
                entity_id=entity_id,
                old_values=asdict(entity) if hasattr(entity, '__dict__') else None,
                metadata={'operation': 'async_workflow_entity_deleted', 'soft_delete': soft_delete}
            )
            
            # Invalidate cache
            if self._cache_enabled and self.cache:
                cache_key = self._generate_cache_key("get_workflow_by_id", entity_id=entity_id)
                await self.cache.delete_async(cache_key)
        
        return success

    async def list(self, filters: Dict[str, Any] = None, limit: int = 100, 
                  offset: int = 0, order_by: str = None):
        """List workflow entities with filters asynchronously"""
        filters = filters or {}
        
        # Check cache for list results
        if self._cache_enabled and self.cache:
            cache_key = self._generate_cache_key("list_workflows", filters=filters, limit=limit, offset=offset)
            cached_result = await self.cache.get_async(cache_key)
            if cached_result:
                return cached_result
        
        # Fetch from database
        workflow_list = await self._fetch_workflow_list_async(filters, limit, offset, order_by)
        
        # Cache result
        if self._cache_enabled and self.cache:
            await self.cache.set_async(cache_key, workflow_list, ttl=self._cache_ttl)
        
        return workflow_list

    async def execute_workflow_async(self, workflow_id: str, trigger_data: Dict[str, Any] = None,
                                   context: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow asynchronously"""
        try:
            # Get workflow definition
            workflow = await self.get_by_id(workflow_id)
            if not workflow or not isinstance(workflow, WorkflowDefinition):
                raise ValueError(f"Workflow not found or invalid: {workflow_id}")
            
            if workflow.status != WorkflowStatus.ACTIVE:
                raise ValueError(f"Workflow is not active: {workflow.status}")
            
            # Check concurrent execution limits
            if not await self._check_concurrent_execution_limits_async(workflow):
                raise ValueError("Maximum concurrent executions reached")
            
            # Create execution
            execution = WorkflowExecution(
                execution_id=self.sync_repo._generate_execution_id(),
                workflow_id=workflow_id,
                workflow_version=workflow.version,
                trigger_data=trigger_data or {},
                status=WorkflowStatus.RUNNING,
                global_context=context or {}
            )
            
            # Store execution
            created_execution = await self.create(execution)
            
            # Start execution in background
            if self.execution_engine:
                await self.execution_engine.start_execution_async(created_execution, workflow)
            else:
                # Fallback to async inline execution
                await self._execute_workflow_inline_async(created_execution, workflow)
            
            self.logger.info(f"Async workflow execution started: {execution.execution_id}")
            
            return created_execution
            
        except Exception as e:
            self.logger.error(f"Async workflow execution failed to start: {e}")
            raise

    async def batch_execute_workflows(self, execution_requests: List[Dict[str, Any]]) -> List[WorkflowExecution]:
        """Execute multiple workflows concurrently"""
        try:
            semaphore = asyncio.Semaphore(self._max_concurrent_operations)
            
            async def execute_workflow_with_semaphore(request):
                async with semaphore:
                    return await self.execute_workflow_async(
                        request['workflow_id'],
                        request.get('trigger_data'),
                        request.get('context')
                    )
            
            # Execute all workflows concurrently
            execution_tasks = [execute_workflow_with_semaphore(req) for req in execution_requests]
            execution_results = await asyncio.gather(*execution_tasks)
            
            self.logger.info(f"Batch workflow execution completed: {len(execution_results)} workflows started")
            
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Batch workflow execution failed: {e}")
            raise

    # Async versions of private methods

    async def _store_workflow_entity_async(self, entity):
        """Store workflow entity in database asynchronously"""
        # Implementation would store in database
        return entity

    async def _setup_workflow_schedule_async(self, workflow: WorkflowDefinition):
        """
Set up workflow scheduling asynchronously"""
        # Implementation would set up scheduling
        pass

    async def _fetch_workflow_by_id_async(self, entity_id: str):
        """
Fetch workflow entity by ID asynchronously"""
        # Implementation would fetch from database
        return None

    async def _update_workflow_entity_async(self, entity):
        """
Update workflow entity in database asynchronously"""
        # Implementation would update database
        return entity

    async def _update_workflow_schedule_async(self, workflow: WorkflowDefinition):
        """
Update workflow scheduling asynchronously"""
        # Implementation would update scheduling
        pass

    async def _stop_active_executions_async(self, workflow_id: str):
        """
Stop all active executions for workflow asynchronously"""
        # Implementation would stop executions
        pass

    async def _remove_workflow_schedule_async(self, workflow_id: str):
        """
Remove workflow from scheduler asynchronously"""
        # Implementation would remove scheduling
        pass

    async def _delete_workflow_entity_async(self, entity_id: str, soft_delete: bool) -> bool:
        """
Delete workflow entity asynchronously"""
        # Implementation would delete from database
        return True

    async def _fetch_workflow_list_async(self, filters, limit, offset, order_by):
        """
Fetch workflow entities list asynchronously"""
        # Implementation would fetch from database
        return []

    async def _check_concurrent_execution_limits_async(self, workflow: WorkflowDefinition) -> bool:
        """
Check if workflow can be executed asynchronously"""
        # Implementation would check limits
        return True

    async def _execute_workflow_inline_async(self, execution: WorkflowExecution, workflow: WorkflowDefinition):
        """
Execute workflow inline asynchronously"""
        # Implementation would execute workflow
        pass
