"""Workflow Engine Database Components

Enterprise workflow orchestration system with AI-powered automation, process
optimization, and intelligent task management for multi-format content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import asyncio
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


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


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"
    RETRY = "retry"


class TriggerType(Enum):
    """Workflow trigger types"""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONTENT_UPLOAD = "content_upload"
    PERFORMANCE_THRESHOLD = "performance_threshold"
    USER_ACTION = "user_action"
    EXTERNAL_API = "external_api"
    COLLABORATION_REQUEST = "collaboration_request"


class TaskType(Enum):
    """Task execution types"""

    CONTENT_PROCESSING = "content_processing"
    AI_ANALYSIS = "ai_analysis"
    PUBLISHING = "publishing"
    NOTIFICATION = "notification"
    APPROVAL_REQUEST = "approval_request"
    DATA_SYNC = "data_sync"
    REPORT_GENERATION = "report_generation"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    CUSTOM_SCRIPT = "custom_script"


@dataclass
class WorkflowContext:
    """Workflow execution context"""
    workflow_id: str
    user_id: str
    creator_type: str
    input_data: Dict[str, Any]
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    started_at: datetime
    current_task: Optional[str] = None


class Workflow(Base):
    """
    Database model for workflow definitions
    """
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_name = Column(String(200), nullable=False)
    workflow_description = Column(Text)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_type = Column(String(50), nullable=False)
    
    # Workflow configuration
    workflow_definition = Column(JSON, nullable=False)  # Tasks, dependencies, conditions
    trigger_configuration = Column(JSON, nullable=False)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    
    # Execution settings
    max_execution_time = Column(Integer, default=3600)  # seconds
    retry_policy = Column(JSON)
    error_handling = Column(JSON)
    notification_settings = Column(JSON)
    
    # Status and lifecycle
    status = Column(String(20), default="draft", nullable=False)
    version = Column(String(20), default="1.0.0")
    is_template = Column(Boolean, default=False)
    template_category = Column(String(100))
    
    # Execution statistics
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    average_execution_time = Column(Integer, default=0)  # seconds
    last_execution_at = Column(DateTime(timezone=True))
    
    # Optimization data
    performance_score = Column(Numeric(5, 2), default=0.0)
    optimization_suggestions = Column(JSON)
    cost_per_execution = Column(Numeric(10, 4), default=0.0)
    
    # Metadata
    tags = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_workflow_user_status', 'user_id', 'status'),
        Index('idx_workflow_creator_type', 'creator_type'),
        Index('idx_workflow_template', 'is_template', 'template_category'),
        Index('idx_workflow_tags', 'tags'),
    )


class WorkflowExecution(Base):
    """
    Database model for workflow execution instances
    """
    __tablename__ = "workflow_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    execution_name = Column(String(200))
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Trigger information
    trigger_type = Column(String(50), nullable=False)
    trigger_data = Column(JSON)
    triggered_by_user_id = Column(UUID(as_uuid=True))
    
    # Execution context
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON)
    execution_variables = Column(JSON)
    context_metadata = Column(JSON)
    
    # Execution status
    status = Column(String(20), default="pending", nullable=False)
    current_task_id = Column(UUID(as_uuid=True))
    completed_tasks = Column(ARRAY(UUID))
    failed_tasks = Column(ARRAY(UUID))
    
    # Timing information
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_duration = Column(Integer)  # seconds
    
    # Error and debugging
    error_message = Column(Text)
    error_details = Column(JSON)
    debug_logs = Column(JSON)
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    total_processing_time = Column(Integer, default=0)  # milliseconds
    memory_usage_mb = Column(Integer)
    cpu_usage_percentage = Column(Numeric(5, 2))
    
    # Approval and manual intervention
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    manual_interventions = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_workflow_exec_workflow', 'workflow_id'),
        Index('idx_workflow_exec_user_status', 'user_id', 'status'),
        Index('idx_workflow_exec_trigger', 'trigger_type'),
        Index('idx_workflow_exec_scheduled', 'scheduled_at'),
        Index('idx_workflow_exec_started', 'started_at'),
    )


class WorkflowTask(Base):
    """
    Database model for individual workflow tasks
    """
    __tablename__ = "workflow_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_execution_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workflow_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Task definition
    task_name = Column(String(200), nullable=False)
    task_type = Column(String(50), nullable=False)
    task_definition = Column(JSON, nullable=False)
    task_order = Column(Integer, nullable=False)
    
    # Dependencies and conditions
    depends_on_tasks = Column(ARRAY(UUID))
    conditional_execution = Column(JSON)
    parallel_group = Column(String(50))
    
    # Execution details
    status = Column(String(20), default="pending", nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    task_variables = Column(JSON)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_duration = Column(Integer)  # milliseconds
    
    # Error handling
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Task-specific metadata
    processor_id = Column(String(100))  # Which service/worker processed this
    resource_usage = Column(JSON)
    external_references = Column(JSON)  # API calls, file references, etc.
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    progress_details = Column(JSON)
    estimated_completion = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_workflow_task_execution', 'workflow_execution_id'),
        Index('idx_workflow_task_status', 'status'),
        Index('idx_workflow_task_type', 'task_type'),
        Index('idx_workflow_task_order', 'task_order'),
        Index('idx_workflow_task_started', 'started_at'),
    )


class WorkflowTemplate(Base):
    """
    Database model for reusable workflow templates
    """
    __tablename__ = "workflow_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(200), nullable=False)
    template_description = Column(Text)
    template_category = Column(String(100), nullable=False)
    
    # Template definition
    template_definition = Column(JSON, nullable=False)
    parameter_schema = Column(JSON)
    customization_options = Column(JSON)
    
    # Usage and popularity
    usage_count = Column(Integer, default=0)
    popularity_score = Column(Numeric(5, 2), default=0.0)
    success_rate = Column(Numeric(5, 4), default=1.0)
    
    # Creator information
    created_by_user_id = Column(UUID(as_uuid=True))
    is_official = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Content type compatibility
    supported_content_types = Column(ARRAY(String))
    supported_creator_types = Column(ARRAY(String))
    platform_compatibility = Column(JSON)
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    changelog = Column(JSON)
    migration_scripts = Column(JSON)
    
    # Metadata
    tags = Column(ARRAY(String))
    icon_url = Column(String(500))
    documentation_url = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_workflow_template_category', 'template_category'),
        Index('idx_workflow_template_public', 'is_public'),
        Index('idx_workflow_template_popularity', 'popularity_score'),
        Index('idx_workflow_template_content_type', 'supported_content_types'),
    )


class ProcessOrchestrator:
    """
    Enterprise process orchestration with parallel execution and dependency management
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.running_executions: Dict[str, WorkflowContext] = {}
        self.task_processors: Dict[TaskType, Callable] = {}
        self.max_concurrent_executions = 50
        self.default_timeout = timedelta(hours=1)
    
    async def register_task_processor(
        self,
        task_type: TaskType,
        processor: Callable
    ):
        """
Register task processor for specific task type"""
        self.task_processors[task_type] = processor
        logger.info(f"Registered task processor for {task_type.value}")
    
    async def execute_workflow(
        self,
        workflow_id: str,
        user_id: str,
        input_data: Dict[str, Any],
        trigger_type: TriggerType = TriggerType.MANUAL,
        trigger_data: Optional[Dict[str, Any]] = None,
        execution_name: Optional[str] = None
    ) -> str:
        """
        Execute workflow with full orchestration
        
        Args:
            workflow_id: Workflow to execute
            user_id: User executing workflow
            input_data: Input data for workflow
            trigger_type: How workflow was triggered
            trigger_data: Additional trigger information
            execution_name: Optional execution name
            
        Returns:
            Execution ID
        """
        # Get workflow definition
        workflow = self.db_session.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.is_active == True
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if workflow.status not in ["active", "draft"]:
            raise ValueError(f"Workflow not executable: {workflow.status}")
        
        # Check concurrent execution limits
        active_executions = self.db_session.query(WorkflowExecution).filter(
            WorkflowExecution.user_id == user_id,
            WorkflowExecution.status.in_(["running", "pending"])
        ).count()
        
        if active_executions >= self.max_concurrent_executions:
            raise ValueError("Maximum concurrent executions reached")
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_record = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            execution_name=execution_name,
            user_id=user_id,
            trigger_type=trigger_type.value,
            trigger_data=trigger_data,
            triggered_by_user_id=user_id,
            input_data=input_data,
            execution_variables={},
            context_metadata={
                'workflow_version': workflow.version,
                'creator_type': workflow.creator_type
            },
            status="running",
            started_at=datetime.now(timezone.utc)
        )
        
        self.db_session.add(execution_record)
        self.db_session.commit()
        
        # Create workflow context
        context = WorkflowContext(
            workflow_id=workflow_id,
            user_id=user_id,
            creator_type=workflow.creator_type,
            input_data=input_data,
            variables={},
            metadata=trigger_data or {},
            started_at=datetime.now(timezone.utc)
        )
        
        self.running_executions[execution_id] = context
        
        # Start execution asynchronously
        asyncio.create_task(self._execute_workflow_tasks(execution_id, workflow))
        
        logger.info(f"Started workflow execution: {execution_id} for workflow: {workflow_id}")
        return execution_id
    
    async def _execute_workflow_tasks(
        self,
        execution_id: str,
        workflow: Workflow
    ):
        """Execute all tasks in workflow with dependency management"""
        try:
            context = self.running_executions[execution_id]
            workflow_definition = workflow.workflow_definition
            tasks_definition = workflow_definition.get('tasks', [])
            
            # Create task records
            task_records = {}
            for i, task_def in enumerate(tasks_definition):
                task_id = str(uuid.uuid4())
                task_record = WorkflowTask(
                    id=task_id,
                    workflow_execution_id=execution_id,
                    workflow_id=workflow.id,
                    task_name=task_def['name'],
                    task_type=task_def['type'],
                    task_definition=task_def,
                    task_order=i,
                    depends_on_tasks=task_def.get('depends_on', []),
                    conditional_execution=task_def.get('conditions'),
                    parallel_group=task_def.get('parallel_group'),
                    input_data=task_def.get('input', {}),
                    max_retries=task_def.get('max_retries', 3)
                )
                
                self.db_session.add(task_record)
                task_records[task_def['name']] = task_record
            
            self.db_session.commit()
            
            # Execute tasks with dependency resolution
            completed_tasks = set()
            failed_tasks = set()
            
            while len(completed_tasks) + len(failed_tasks) < len(tasks_definition):
                # Find tasks ready to execute
                ready_tasks = []
                for task_name, task_record in task_records.items():
                    if (task_record.status == "pending" and
                        all(dep in completed_tasks for dep in task_record.depends_on_tasks or [])):
                        ready_tasks.append(task_record)
                
                if not ready_tasks:
                    # Check if we're deadlocked
                    pending_tasks = [t for t in task_records.values() if t.status == "pending"]
                    if pending_tasks:
                        logger.error(f"Workflow deadlock detected in execution {execution_id}")
                        break
                    else:
                        break
                
                # Execute ready tasks (potentially in parallel)
                execution_futures = []
                for task_record in ready_tasks:
                    future = asyncio.create_task(
                        self._execute_single_task(execution_id, task_record, context)
                    )
                    execution_futures.append((task_record, future))
                
                # Wait for task completions
                for task_record, future in execution_futures:
                    try:
                        success = await future
                        if success:
                            completed_tasks.add(task_record.task_name)
                            task_record.status = "completed"
                        else:
                            failed_tasks.add(task_record.task_name)
                            task_record.status = "failed"
                    except Exception as e:
                        logger.error(f"Task execution error: {str(e)}")
                        failed_tasks.add(task_record.task_name)
                        task_record.status = "failed"
                        task_record.error_message = str(e)
                
                self.db_session.commit()
                
                # Check if critical tasks failed
                if any(task_records[name].task_definition.get('critical', False) 
                       for name in failed_tasks):
                    logger.error(f"Critical task failed in execution {execution_id}")
                    break
            
            # Update execution status
            execution_record = self.db_session.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()
            
            if execution_record:
                execution_record.completed_at = datetime.now(timezone.utc)
                execution_record.execution_duration = int(
                    (execution_record.completed_at - execution_record.started_at).total_seconds()
                )
                execution_record.tasks_completed = len(completed_tasks)
                execution_record.tasks_failed = len(failed_tasks)
                
                if failed_tasks:
                    execution_record.status = "failed"
                else:
                    execution_record.status = "completed"
                
                self.db_session.commit()
            
            # Update workflow statistics
            workflow.total_executions += 1
            if not failed_tasks:
                workflow.successful_executions += 1
            else:
                workflow.failed_executions += 1
            
            workflow.last_execution_at = datetime.now(timezone.utc)
            self.db_session.commit()
            
            # Cleanup
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
            
            logger.info(f"Completed workflow execution: {execution_id}")
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {execution_id} - {str(e)}")
            
            # Update execution as failed
            execution_record = self.db_session.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()
            
            if execution_record:
                execution_record.status = "failed"
                execution_record.error_message = str(e)
                execution_record.completed_at = datetime.now(timezone.utc)
                self.db_session.commit()
            
            # Cleanup
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
    
    async def _execute_single_task(
        self,
        execution_id: str,
        task_record: WorkflowTask,
        context: WorkflowContext
    ) -> bool:
        """Execute single workflow task"""
        try:
            task_type = TaskType(task_record.task_type)
            
            # Check if we have a processor for this task type
            if task_type not in self.task_processors:
                logger.error(f"No processor registered for task type: {task_type.value}")
                return False
            
            # Update task status
            task_record.status = "running"
            task_record.started_at = datetime.now(timezone.utc)
            self.db_session.commit()
            
            # Execute task
            processor = self.task_processors[task_type]
            result = await processor(task_record, context)
            
            # Update task with results
            task_record.completed_at = datetime.now(timezone.utc)
            task_record.execution_duration = int(
                (task_record.completed_at - task_record.started_at).total_seconds() * 1000
            )
            
            if result.get('success', False):
                task_record.output_data = result.get('output', {})
                task_record.progress_percentage = 100
                return True
            else:
                task_record.error_message = result.get('error', 'Unknown error')
                task_record.error_details = result.get('error_details', {})
                return False
                
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
            task_record.error_message = str(e)
            task_record.completed_at = datetime.now(timezone.utc)
            return False
        finally:
            self.db_session.commit()


class WorkflowEngine:
    """
    Enterprise workflow engine with template management and optimization
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.orchestrator = ProcessOrchestrator(db_session)
    
    async def create_workflow(
        self,
        workflow_name: str,
        user_id: str,
        creator_type: str,
        workflow_definition: Dict[str, Any],
        trigger_config: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create new workflow definition
        
        Args:
            workflow_name: Name of workflow
            user_id: Creator user ID
            creator_type: Type of creator
            workflow_definition: Workflow tasks and structure
            trigger_config: Trigger configuration
            metadata: Additional metadata
            
        Returns:
            Workflow ID
        """
        workflow = Workflow(
            workflow_name=workflow_name,
            workflow_description=metadata.get('description', ''),
            user_id=user_id,
            creator_type=creator_type,
            workflow_definition=workflow_definition,
            trigger_configuration=trigger_config,
            input_schema=metadata.get('input_schema'),
            output_schema=metadata.get('output_schema'),
            max_execution_time=metadata.get('max_execution_time', 3600),
            retry_policy=metadata.get('retry_policy', {}),
            error_handling=metadata.get('error_handling', {}),
            notification_settings=metadata.get('notification_settings', {}),
            tags=metadata.get('tags', [])
        )
        
        self.db_session.add(workflow)
        self.db_session.commit()
        
        logger.info(f"Created workflow: {workflow.id} - {workflow_name}")
        return str(workflow.id)
    
    async def create_workflow_from_template(
        self,
        template_id: str,
        user_id: str,
        workflow_name: str,
        parameters: Dict[str, Any]
    ) -> str:
        """
        Create workflow from template with customization
        
        Args:
            template_id: Template to use
            user_id: User creating workflow
            workflow_name: Name for new workflow
            parameters: Template parameters
            
        Returns:
            Workflow ID
        """
        template = self.db_session.query(WorkflowTemplate).filter(
            WorkflowTemplate.id == template_id,
            WorkflowTemplate.is_active == True
        ).first()
        
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Customize template with parameters
        workflow_definition = self._customize_template(
            template.template_definition,
            parameters
        )
        
        # Create workflow
        workflow_id = await self.create_workflow(
            workflow_name=workflow_name,
            user_id=user_id,
            creator_type=parameters.get('creator_type', 'generic'),
            workflow_definition=workflow_definition,
            trigger_config=parameters.get('trigger_config', {'type': 'manual'}),
            metadata={
                'template_id': template_id,
                'template_version': template.version,
                'customization_parameters': parameters
            }
        )
        
        # Update template usage
        template.usage_count += 1
        self.db_session.commit()
        
        return workflow_id
    
    async def get_workflow_templates(
        self,
        creator_type: Optional[str] = None,
        category: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available workflow templates with filtering
        
        Args:
            creator_type: Filter by creator type
            category: Filter by template category
            content_type: Filter by content type support
            
        Returns:
            List of template information
        """
        query = self.db_session.query(WorkflowTemplate).filter(
            WorkflowTemplate.is_active == True,
            WorkflowTemplate.is_public == True
        )
        
        if creator_type:
            query = query.filter(
                WorkflowTemplate.supported_creator_types.contains([creator_type])
            )
        
        if category:
            query = query.filter(WorkflowTemplate.template_category == category)
        
        if content_type:
            query = query.filter(
                WorkflowTemplate.supported_content_types.contains([content_type])
            )
        
        templates = query.order_by(WorkflowTemplate.popularity_score.desc()).all()
        
        return [
            {
                'template_id': str(template.id),
                'name': template.template_name,
                'description': template.template_description,
                'category': template.template_category,
                'popularity_score': float(template.popularity_score),
                'success_rate': float(template.success_rate),
                'usage_count': template.usage_count,
                'supported_content_types': template.supported_content_types,
                'supported_creator_types': template.supported_creator_types,
                'parameter_schema': template.parameter_schema,
                'tags': template.tags,
                'icon_url': template.icon_url
            }
            for template in templates
        ]
    
    async def get_workflow_execution_status(
        self,
        execution_id: str
    ) -> Dict[str, Any]:
        """
Get detailed execution status and progress"""
        execution = self.db_session.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).first()
        
        if not execution:
            return {'error': 'Execution not found'}
        
        # Get task details
        tasks = self.db_session.query(WorkflowTask).filter(
            WorkflowTask.workflow_execution_id == execution_id
        ).order_by(WorkflowTask.task_order).all()
        
        task_details = []
        for task in tasks:
            task_info = {
                'task_id': str(task.id),
                'task_name': task.task_name,
                'task_type': task.task_type,
                'status': task.status,
                'progress_percentage': task.progress_percentage,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'execution_duration': task.execution_duration,
                'error_message': task.error_message
            }
            task_details.append(task_info)
        
        return {
            'execution_id': str(execution.id),
            'workflow_id': str(execution.workflow_id),
            'status': execution.status,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'execution_duration': execution.execution_duration,
            'tasks_completed': execution.tasks_completed,
            'tasks_failed': execution.tasks_failed,
            'error_message': execution.error_message,
            'tasks': task_details,
            'progress_percentage': self._calculate_execution_progress(tasks)
        }
    
    def _customize_template(
        self,
        template_definition: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Apply parameters to template definition"""
        # This would implement template parameter substitution
        # For now, return basic customization
        definition = template_definition.copy()
        
        # Replace parameter placeholders
        definition_str = json.dumps(definition)
        for key, value in parameters.items():
            placeholder = f"{{{{ {key} }}}}"
            definition_str = definition_str.replace(placeholder, str(value))
        
        return json.loads(definition_str)
    
    def _calculate_execution_progress(self, tasks: List[WorkflowTask]) -> int:
        """Calculate overall execution progress percentage"""
        if not tasks:
            return 0
        
        total_progress = sum(task.progress_percentage or 0 for task in tasks)
        return int(total_progress / len(tasks))
