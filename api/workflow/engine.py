"""
Enterprise workflow engine with event-driven architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import uuid
import logging
from collections import defaultdict, deque

from ..core.events import EventBus, Event
from ..core.exceptions import WorkflowEngineException
from ..models.workflow import WorkflowDefinition, WorkflowInstance
from ..services.notification.manager import NotificationManager
from ..utils.state_machine import StateMachine
from ..utils.metrics import MetricsCollector


class WorkflowEventType(Enum):
    """Workflow event types for enterprise orchestration."""
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    STAGE_STARTED = "stage.started"
    STAGE_COMPLETED = "stage.completed"
    STAGE_FAILED = "stage.failed"
    CONDITION_MET = "condition.met"
    CONDITION_FAILED = "condition.failed"
    TIMEOUT_REACHED = "timeout.reached"
    RETRY_INITIATED = "retry.initiated"
    ESCALATION_TRIGGERED = "escalation.triggered"


class WorkflowState(Enum):
    """Enterprise workflow states."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    ESCALATED = "escalated"


class WorkflowPriority(Enum):
    """Workflow execution priorities."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class WorkflowCondition:
    """Workflow execution condition."""
    name: str
    condition_type: str
    expression: str
    timeout_seconds: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context."""
        # Placeholder for condition evaluation logic
        return True


@dataclass  
class WorkflowStage:
    """Enhanced workflow stage definition."""
    id: str
    name: str
    stage_type: str
    handler: str
    conditions: List[WorkflowCondition] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    compensation_handler: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parallel_execution: bool = False
    critical_path: bool = False


@dataclass
class WorkflowTemplate:
    """Enterprise workflow template."""
    id: str
    name: str
    version: str
    description: str
    stages: List[WorkflowStage]
    global_conditions: List[WorkflowCondition] = field(default_factory=list)
    global_timeout_seconds: Optional[int] = None
    error_handling_strategy: str = "fail_fast"  # fail_fast, continue_on_error, compensate
    notification_rules: List[Dict] = field(default_factory=list)
    sla_requirements: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class WorkflowExecutionContext:
    """Runtime execution context for workflows."""
    
    def __init__(self, workflow_id: str, template: WorkflowTemplate, input_data: Dict):
        self.workflow_id = workflow_id
        self.template = template
        self.input_data = input_data
        self.runtime_data = {}
        self.stage_results = {}
        self.variables = {}
        self.execution_path = []
        self.error_log = []
        self.metrics = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_variable(self, key: str, value: Any) -> None:
        """Set runtime variable."""
        self.variables[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get runtime variable."""



        return self.variables.get(key, default)
    
    def set_stage_result(self, stage_id: str, result: Dict) -> None:
        """Set result for completed stage."""
        self.stage_results[stage_id] = {
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
            "duration": result.get("duration", 0)
        }
        self.updated_at = datetime.utcnow()
    
    def add_error(self, stage_id: str, error: str, error_type: str = "execution") -> None:
        """Add error to execution log."""
        self.error_log.append({
            "stage_id": stage_id,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def record_metric(self, metric_name: str, value: float, stage_id: Optional[str] = None) -> None:
        """Record execution metric."""
        key = f"{stage_id}.{metric_name}" if stage_id else metric_name
        self.metrics[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def to_dict(self) -> Dict:
        """Convert context to dictionary."""



        return {
            "workflow_id": self.workflow_id,
            "template_id": self.template.id,
            "input_data": self.input_data,
            "runtime_data": self.runtime_data,
            "stage_results": self.stage_results,
            "variables": self.variables,
            "execution_path": self.execution_path,
            "error_log": self.error_log,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class WorkflowStageHandler:
    """Base class for workflow stage handlers."""
    
    def __init__(self, stage_type: str):
        self.stage_type = stage_type
        self.logger = logging.getLogger(f"workflow.handler.{stage_type}")
    
    async def execute(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """Execute workflow stage."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Executing stage {stage.id} of type {stage.stage_type}")
            
            # Pre-execution validation
            await self._validate_stage_execution(stage, context)
            
            # Execute stage logic
            result = await self._execute_stage_logic(stage, context)
            
            # Post-execution processing
            await self._post_execution_processing(stage, context, result)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "duration": duration,
                "stage_id": stage.id,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Stage {stage.id} failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "duration": duration,
                "stage_id": stage.id,
                "failed_at": datetime.utcnow().isoformat()
            }
    
    async def _validate_stage_execution(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> None:
        """Validate stage can be executed."""
        # Check dependencies
        for dep_id in stage.dependencies:
            if dep_id not in context.stage_results:
                raise WorkflowEngineException(f"Dependency {dep_id} not satisfied for stage {stage.id}")
            
            dep_result = context.stage_results[dep_id]
            if not dep_result.get("result", {}).get("success", False):
                raise WorkflowEngineException(f"Dependency {dep_id} failed for stage {stage.id}")
        
        # Check conditions
        for condition in stage.conditions:
            if not condition.evaluate(context.to_dict()):
                raise WorkflowEngineException(f"Condition {condition.name} not met for stage {stage.id}")
    
    async def _execute_stage_logic(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """Execute the actual stage logic - to be overridden by subclasses."""
        # Default implementation for base stage handler
        self.logger.info(f"Executing base stage logic for {stage.id} of type {stage.stage_type}")
        
        # Simulate basic stage execution
        result = {
            "stage_id": stage.id,
            "stage_type": stage.stage_type,
            "handler": stage.handler,
            "status": "completed",
            "message": f"Base stage handler executed for {stage.stage_type}",
            "metadata": stage.metadata,
            "execution_time": datetime.utcnow().isoformat()
        }
        
        # Update context with basic execution data
        context.set_variable(f"{stage.id}_result", result)
        
        return result
    
    async def _post_execution_processing(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext,
        result: Dict[str, Any]
    ) -> None:
        """Post-execution processing."""
        # Record stage completion in execution path
        context.execution_path.append({
            "stage_id": stage.id,
            "completed_at": datetime.utcnow().isoformat(),
            "result_summary": {k: v for k, v in result.items() if k in ["success", "duration"]}
        })


class ContentAnalysisStageHandler(WorkflowStageHandler):
    """Handler for content analysis workflow stages."""
    
    def __init__(self):
        super().__init__("content_analysis")
    
    async def _execute_stage_logic(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """Execute content analysis logic."""
        content_item = context.input_data.get("content_item")
        if not content_item:
            raise WorkflowEngineException("No content item provided for analysis")
        
        analysis_type = stage.metadata.get("analysis_type", "comprehensive")
        
        # Placeholder for actual analysis logic
        analysis_result = {
            "analysis_type": analysis_type,
            "content_category": "entertainment",
            "quality_score": 0.85,
            "engagement_prediction": 0.78,
            "monetization_score": 0.72,
            "target_audience": ["18-34", "music_lovers"],
            "recommended_platforms": ["youtube", "instagram", "tiktok"],
            "seo_keywords": ["music", "entertainment", "viral"],
            "estimated_processing_time": 120
        }
        
        # Update context with analysis results
        context.set_variable("content_analysis", analysis_result)
        
        return analysis_result


class ContentProtectionStageHandler(WorkflowStageHandler):
    """Handler for content protection workflow stages."""
    
    def __init__(self):
        super().__init__("content_protection")
    
    async def _execute_stage_logic(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """Execute content protection logic."""
        content_item = context.input_data.get("content_item")
        analysis_result = context.get_variable("content_analysis", {})
        
        protection_level = stage.metadata.get("protection_level", "standard")
        
        # Placeholder for actual protection logic
        protection_result = {
            "protection_level": protection_level,
            "fingerprints_generated": 5,
            "monitoring_platforms": 8,
            "protection_score": 0.92,
            "estimated_monthly_scans": 10000,
            "protection_policies": ["copyright", "trademark", "brand"],
            "monitoring_frequency": "hourly",
            "alert_thresholds": {
                "similarity": 0.85,
                "confidence": 0.80
            }
        }
        
        # Update context
        context.set_variable("content_protection", protection_result)
        
        return protection_result


class DistributionStageHandler(WorkflowStageHandler):
    """Handler for content distribution workflow stages."""
    
    def __init__(self):
        super().__init__("distribution")
    
    async def _execute_stage_logic(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """Execute content distribution logic."""
        content_item = context.input_data.get("content_item")
        analysis_result = context.get_variable("content_analysis", {})
        
        target_platforms = stage.metadata.get("target_platforms", [])
        if not target_platforms:
            target_platforms = analysis_result.get("recommended_platforms", [])
        
        # Placeholder for actual distribution logic
        distribution_result = {
            "target_platforms": target_platforms,
            "scheduled_publications": len(target_platforms),
            "optimization_applied": True,
            "estimated_reach": 50000,
            "publishing_schedule": {
                platform: f"2025-08-12T{18 + i}:00:00Z" 
                for i, platform in enumerate(target_platforms)
            },
            "seo_optimizations": ["keywords", "descriptions", "tags"],
            "cross_promotion_setup": True
        }
        
        # Update context
        context.set_variable("content_distribution", distribution_result)
        
        return distribution_result


class MonitoringStageHandler(WorkflowStageHandler):
    """Handler for monitoring setup workflow stages."""
    
    def __init__(self):
        super().__init__("monitoring")
    
    async def _execute_stage_logic(
        self, 
        stage: WorkflowStage, 
        context: WorkflowExecutionContext
    ) -> Dict[str, Any]:
        """Execute monitoring setup logic."""
        protection_result = context.get_variable("content_protection", {})
        distribution_result = context.get_variable("content_distribution", {})
        
        monitoring_scope = stage.metadata.get("monitoring_scope", "comprehensive")
        
        # Placeholder for actual monitoring setup logic
        monitoring_result = {
            "monitoring_scope": monitoring_scope,
            "active_monitors": 12,
            "platforms_monitored": protection_result.get("monitoring_platforms", 8),
            "alert_channels": ["email", "slack", "dashboard"],
            "dashboard_url": f"/dashboard/monitoring/{context.workflow_id}",
            "reporting_frequency": "daily",
            "metrics_tracked": [
                "content_views", "engagement_rate", "protection_violations",
                "revenue_tracking", "audience_growth", "platform_performance"
            ],
            "sla_targets": {
                "uptime": 99.9,
                "alert_response_time": 300,  # 5 minutes
                "reporting_accuracy": 95.0
            }
        }
        
        # Update context
        context.set_variable("monitoring_setup", monitoring_result)
        
        return monitoring_result


class EnterpriseWorkflowEngine:
    """Enterprise-grade workflow engine with advanced features."""
    
    def __init__(self):
        self.logger = logging.getLogger("workflow.engine")
        self.event_bus = EventBus()
        self.notification_manager = NotificationManager()
        self.metrics = MetricsCollector()
        
        # Workflow state management
        self.workflow_instances = {}
        self.templates = {}
        self.execution_queue = deque()
        
        # Stage handlers registry
        self.stage_handlers = {
            "content_analysis": ContentAnalysisStageHandler(),
            "content_protection": ContentProtectionStageHandler(),
            "distribution": DistributionStageHandler(),
            "monitoring": MonitoringStageHandler()
        }
        
        # Configuration
        self.max_concurrent_workflows = 20
        self.default_timeout_seconds = 3600  # 1 hour
        self.cleanup_completed_after_hours = 24
        
        # Initialize event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up event handlers for workflow events."""
        self.event_bus.subscribe(WorkflowEventType.WORKFLOW_FAILED, self._handle_workflow_failure)
        self.event_bus.subscribe(WorkflowEventType.TIMEOUT_REACHED, self._handle_timeout)
        self.event_bus.subscribe(WorkflowEventType.ESCALATION_TRIGGERED, self._handle_escalation)
    
    async def register_template(self, template: WorkflowTemplate) -> str:
        """Register a workflow template."""
        template_id = template.id
        self.templates[template_id] = template
        
        self.logger.info(f"Registered workflow template {template_id}")
        
        return template_id
    
    async def create_content_processing_workflow(
        self,
        content_item: Dict,
        user_id: str,
        processing_options: Optional[Dict] = None
    ) -> str:
        """Create a comprehensive content processing workflow."""
        processing_options = processing_options or {}
        
        # Define workflow stages based on content type and options
        stages = []
        
        # Content Analysis Stage
        stages.append(WorkflowStage(
            id="content_analysis",
            name="Content Analysis",
            stage_type="content_analysis",
            handler="content_analysis",
            metadata={
                "analysis_type": processing_options.get("analysis_type", "comprehensive"),
                "include_ai_insights": processing_options.get("ai_insights", True)
            },
            timeout_seconds=300,
            critical_path=True
        ))
        
        # Content Protection Stage
        if processing_options.get("enable_protection", True):
            stages.append(WorkflowStage(
                id="content_protection",
                name="Content Protection Setup",
                stage_type="content_protection", 
                handler="content_protection",
                dependencies=["content_analysis"],
                metadata={
                    "protection_level": processing_options.get("protection_level", "standard"),
                    "monitoring_platforms": processing_options.get("monitoring_platforms", [])
                },
                timeout_seconds=180,
                critical_path=True
            ))
        
        # Distribution Stage
        if processing_options.get("auto_distribute", False):
            stages.append(WorkflowStage(
                id="distribution",
                name="Content Distribution",
                stage_type="distribution",
                handler="distribution", 
                dependencies=["content_analysis"],
                metadata={
                    "target_platforms": processing_options.get("target_platforms", []),
                    "schedule_optimization": processing_options.get("schedule_optimization", True)
                },
                timeout_seconds=600,
                critical_path=False
            ))
        
        # Monitoring Setup Stage
        stages.append(WorkflowStage(
            id="monitoring_setup",
            name="Monitoring Setup",
            stage_type="monitoring",
            handler="monitoring",
            dependencies=["content_analysis"],
            metadata={
                "monitoring_scope": processing_options.get("monitoring_scope", "comprehensive"),
                "alert_preferences": processing_options.get("alert_preferences", {})
            },
            timeout_seconds=120,
            critical_path=False
        ))
        
        # Create workflow template
        template = WorkflowTemplate(
            id=f"content_processing_{uuid.uuid4().hex[:8]}",
            name="Content Processing Workflow",
            version="1.0",
            description="Comprehensive content processing including analysis, protection, and distribution",
            stages=stages,
            global_timeout_seconds=processing_options.get("max_processing_time", 1800),  # 30 minutes
            error_handling_strategy=processing_options.get("error_strategy", "compensate"),
            notification_rules=[
                {
                    "event": "workflow_completed",
                    "channels": ["email", "dashboard"],
                    "recipients": [user_id]
                },
                {
                    "event": "workflow_failed", 
                    "channels": ["email", "slack"],
                    "recipients": [user_id]
                }
            ],
            sla_requirements={
                "max_duration_minutes": 30,
                "success_rate_threshold": 95.0
            },
            tags=["content_processing", "automated", content_item.get("content_type", "unknown")]
        )
        
        # Register template and start workflow
        await self.register_template(template)
        
        workflow_id = await self.start_workflow(
            template_id=template.id,
            input_data={"content_item": content_item, "user_id": user_id},
            priority=WorkflowPriority.HIGH
        )
        
        return workflow_id
    
    async def start_workflow(
        self,
        template_id: str,
        input_data: Dict,
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        scheduled_start: Optional[datetime] = None
    ) -> str:
        """Start a new workflow instance."""
        if template_id not in self.templates:
            raise WorkflowEngineException(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        workflow_id = f"wf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create execution context
        context = WorkflowExecutionContext(workflow_id, template, input_data)
        
        # Create workflow instance
        instance = {
            "id": workflow_id,
            "template_id": template_id,
            "context": context,
            "state": WorkflowState.READY,
            "priority": priority,
            "scheduled_start": scheduled_start,
            "current_stage_index": 0,
            "parallel_stages": set(),
            "completed_stages": set(),
            "failed_stages": set(),
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "last_heartbeat": datetime.utcnow()
        }
        
        self.workflow_instances[workflow_id] = instance
        
        # Queue for execution
        await self._queue_workflow_for_execution(workflow_id, priority, scheduled_start)
        
        # Emit workflow created event
        await self.event_bus.emit(Event(
            type=WorkflowEventType.WORKFLOW_STARTED.value,
            data={
                "workflow_id": workflow_id,
                "template_id": template_id,
                "priority": priority.value,
                "created_at": instance["created_at"].isoformat()
            }
        ))
        
        self.logger.info(f"Started workflow {workflow_id} from template {template_id}")
        
        return workflow_id
    
    async def _queue_workflow_for_execution(
        self,
        workflow_id: str,
        priority: WorkflowPriority,
        scheduled_start: Optional[datetime] = None
    ):
        """Queue workflow for execution."""
        queue_item = {
            "workflow_id": workflow_id,
            "priority": priority.value,
            "scheduled_start": scheduled_start or datetime.utcnow(),
            "queued_at": datetime.utcnow()
        }
        
        # Insert in priority order
        inserted = False
        for i, item in enumerate(self.execution_queue):
            if priority.value > item["priority"]:
                self.execution_queue.insert(i, queue_item)
                inserted = True
                break
        
        if not inserted:
            self.execution_queue.append(queue_item)
    
    async def execute_workflows(self):
        """Main workflow execution loop."""
        while True:
            try:
                # Check for workflows ready to execute
                current_time = datetime.utcnow()
                ready_workflows = []
                
                # Get ready workflows from queue
                while (self.execution_queue and 
                       len(ready_workflows) < self.max_concurrent_workflows):
                    
                    queue_item = self.execution_queue[0]
                    
                    # Check if scheduled time has arrived
                    if queue_item["scheduled_start"] <= current_time:
                        ready_workflows.append(self.execution_queue.popleft())
                    else:
                        break
                
                # Execute ready workflows
                tasks = []
                for queue_item in ready_workflows:
                    workflow_id = queue_item["workflow_id"]
                    if workflow_id in self.workflow_instances:
                        tasks.append(self._execute_workflow_instance(workflow_id))
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Clean up completed workflows
                await self._cleanup_completed_workflows()
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in workflow execution loop: {str(e)}")
                await asyncio.sleep(5)  # Back off on error
    
    async def _execute_workflow_instance(self, workflow_id: str):
        """Execute a single workflow instance."""
        instance = self.workflow_instances.get(workflow_id)
        if not instance:
            self.logger.error(f"Workflow instance {workflow_id} not found")
            return
        
        try:
            instance["state"] = WorkflowState.RUNNING
            instance["started_at"] = datetime.utcnow()
            
            context = instance["context"]
            template = context.template
            
            self.logger.info(f"Executing workflow {workflow_id}")
            
            # Execute stages
            for stage in template.stages:
                # Check if stage should be executed
                if stage.id in instance["completed_stages"]:
                    continue
                
                # Check dependencies
                dependencies_met = all(
                    dep_id in instance["completed_stages"]
                    for dep_id in stage.dependencies
                )
                
                if not dependencies_met:
                    continue
                
                # Execute stage
                stage_result = await self._execute_workflow_stage(workflow_id, stage)
                
                if stage_result["success"]:
                    instance["completed_stages"].add(stage.id)
                    context.set_stage_result(stage.id, stage_result)
                    
                    # Emit stage completed event
                    await self.event_bus.emit(Event(
                        type=WorkflowEventType.STAGE_COMPLETED.value,
                        data={
                            "workflow_id": workflow_id,
                            "stage_id": stage.id,
                            "result": stage_result
                        }
                    ))
                else:
                    instance["failed_stages"].add(stage.id)
                    context.add_error(stage.id, stage_result.get("error", "Unknown error"))
                    
                    # Handle stage failure based on error strategy
                    if template.error_handling_strategy == "fail_fast":
                        raise WorkflowEngineException(f"Stage {stage.id} failed: {stage_result.get('error')}")
                    
                    # Emit stage failed event
                    await self.event_bus.emit(Event(
                        type=WorkflowEventType.STAGE_FAILED.value,
                        data={
                            "workflow_id": workflow_id,
                            "stage_id": stage.id,
                            "error": stage_result.get("error")
                        }
                    ))
            
            # Check if workflow is complete
            required_stages = {stage.id for stage in template.stages if stage.critical_path}
            completed_required_stages = required_stages.intersection(instance["completed_stages"])
            
            if len(completed_required_stages) == len(required_stages):
                # Workflow completed successfully
                instance["state"] = WorkflowState.COMPLETED
                instance["completed_at"] = datetime.utcnow()
                
                # Emit workflow completed event
                await self.event_bus.emit(Event(
                    type=WorkflowEventType.WORKFLOW_COMPLETED.value,
                    data={
                        "workflow_id": workflow_id,
                        "completed_at": instance["completed_at"].isoformat(),
                        "duration": (instance["completed_at"] - instance["started_at"]).total_seconds(),
                        "stages_completed": len(instance["completed_stages"]),
                        "stages_failed": len(instance["failed_stages"])
                    }
                ))
                
                self.logger.info(f"Workflow {workflow_id} completed successfully")
            else:
                # Workflow failed
                instance["state"] = WorkflowState.FAILED
                instance["completed_at"] = datetime.utcnow()
                
                await self.event_bus.emit(Event(
                    type=WorkflowEventType.WORKFLOW_FAILED.value,
                    data={
                        "workflow_id": workflow_id,
                        "failed_at": instance["completed_at"].isoformat(),
                        "stages_completed": len(instance["completed_stages"]),
                        "stages_failed": len(instance["failed_stages"]),
                        "errors": context.error_log
                    }
                ))
                
                self.logger.error(f"Workflow {workflow_id} failed")
            
        except Exception as e:
            instance["state"] = WorkflowState.FAILED
            instance["completed_at"] = datetime.utcnow()
            
            self.logger.error(f"Workflow {workflow_id} failed with exception: {str(e)}")
            
            await self.event_bus.emit(Event(
                type=WorkflowEventType.WORKFLOW_FAILED.value,
                data={
                    "workflow_id": workflow_id,
                    "error": str(e),
                    "failed_at": instance["completed_at"].isoformat()
                }
            ))
    
    async def _execute_workflow_stage(self, workflow_id: str, stage: WorkflowStage) -> Dict:
        """Execute a single workflow stage."""
        instance = self.workflow_instances[workflow_id]
        context = instance["context"]
        
        handler = self.stage_handlers.get(stage.stage_type)
        if not handler:
            return {
                "success": False,
                "error": f"No handler found for stage type {stage.stage_type}",
                "stage_id": stage.id
            }
        
        self.logger.info(f"Executing stage {stage.id} for workflow {workflow_id}")
        
        # Execute stage with timeout
        try:
            timeout = stage.timeout_seconds or self.default_timeout_seconds
            result = await asyncio.wait_for(
                handler.execute(stage, context),
                timeout=timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Stage {stage.id} timed out after {timeout} seconds",
                "stage_id": stage.id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stage_id": stage.id
            }
    
    async def _cleanup_completed_workflows(self):
        """Clean up old completed workflows."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_completed_after_hours)
        
        workflows_to_remove = []
        for workflow_id, instance in self.workflow_instances.items():
            if (instance["state"] in [WorkflowState.COMPLETED, WorkflowState.FAILED] and
                instance.get("completed_at", datetime.utcnow()) < cutoff_time):
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.workflow_instances[workflow_id]
            self.logger.info(f"Cleaned up workflow {workflow_id}")
    
    async def _handle_workflow_failure(self, event: Event):
        """Handle workflow failure events."""
        workflow_id = event.data.get("workflow_id")
        error = event.data.get("error", "Unknown error")
        
        # Send notification
        await self.notification_manager.send_notification(
            type="workflow_failure",
            data={
                "workflow_id": workflow_id,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _handle_timeout(self, event: Event):
        """Handle workflow timeout events."""
        workflow_id = event.data.get("workflow_id")
        
        if workflow_id in self.workflow_instances:
            instance = self.workflow_instances[workflow_id]
            instance["state"] = WorkflowState.TIMEOUT
            
            self.logger.warning(f"Workflow {workflow_id} timed out")
    
    async def _handle_escalation(self, event: Event):
        """Handle workflow escalation events."""
        workflow_id = event.data.get("workflow_id")
        
        # Implement escalation logic
        self.logger.warning(f"Workflow {workflow_id} escalated")
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get comprehensive workflow status."""
        instance = self.workflow_instances.get(workflow_id)
        if not instance:
            return None
        
        context = instance["context"]
        template = context.template
        
        return {
            "id": workflow_id,
            "template_id": instance["template_id"],
            "state": instance["state"].value,
            "priority": instance["priority"].value,
            "created_at": instance["created_at"].isoformat(),
            "started_at": instance["started_at"].isoformat() if instance["started_at"] else None,
            "completed_at": instance["completed_at"].isoformat() if instance["completed_at"] else None,
            "current_stage_index": instance["current_stage_index"],
            "total_stages": len(template.stages),
            "completed_stages": len(instance["completed_stages"]),
            "failed_stages": len(instance["failed_stages"]),
            "progress_percentage": (len(instance["completed_stages"]) / len(template.stages)) * 100,
            "execution_path": context.execution_path,
            "error_log": context.error_log,
            "metrics": context.metrics,
            "estimated_completion": self._estimate_completion_time(workflow_id),
            "resource_utilization": self._get_resource_utilization(workflow_id)
        }
    
    def _estimate_completion_time(self, workflow_id: str) -> Optional[str]:
        """Estimate workflow completion time."""
        instance = self.workflow_instances.get(workflow_id)
        if not instance or instance["state"] not in [WorkflowState.RUNNING, WorkflowState.WAITING]:
            return None
        
        # Simple estimation based on average stage duration
        remaining_stages = len(instance["context"].template.stages) - len(instance["completed_stages"])
        avg_stage_duration = 120  # 2 minutes average
        
        estimated_completion = datetime.utcnow() + timedelta(seconds=remaining_stages * avg_stage_duration)
        return estimated_completion.isoformat()
    
    def _get_resource_utilization(self, workflow_id: str) -> Dict:
        """Get current resource utilization for workflow."""



        return {
            "cpu_usage": 0.15,
            "memory_usage": 0.08,
            "storage_usage": 0.05,
            "network_usage": 0.03
        }
    
    def get_active_workflows(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get list of active workflows."""
        workflows = []
        
        for workflow_id, instance in self.workflow_instances.items():
            if user_id:
                workflow_user_id = instance["context"].input_data.get("user_id")
                if workflow_user_id != user_id:
                    continue
            
            if instance["state"] in [WorkflowState.RUNNING, WorkflowState.WAITING]:
                workflows.append(self.get_workflow_status(workflow_id))
        
        return workflows
    
    def get_workflow_metrics(self, template_id: Optional[str] = None) -> Dict:
        """Get workflow execution metrics."""
        total_workflows = len(self.workflow_instances)
        completed = sum(1 for w in self.workflow_instances.values() if w["state"] == WorkflowState.COMPLETED)
        failed = sum(1 for w in self.workflow_instances.values() if w["state"] == WorkflowState.FAILED)
        running = sum(1 for w in self.workflow_instances.values() if w["state"] == WorkflowState.RUNNING)
        
        return {
            "total_workflows": total_workflows,
            "completed": completed,
            "failed": failed,
            "running": running,
            "success_rate": (completed / total_workflows * 100) if total_workflows > 0 else 0,
            "average_execution_time": self._calculate_average_execution_time(),
            "queue_length": len(self.execution_queue)
        }
    
    def _calculate_average_execution_time(self) -> float:
        """Calculate average workflow execution time."""
        completed_workflows = [
            w for w in self.workflow_instances.values() 
            if w["state"] == WorkflowState.COMPLETED and w["started_at"] and w["completed_at"]
        ]
        
        if not completed_workflows:
            return 0.0
        
        total_duration = sum(
            (w["completed_at"] - w["started_at"]).total_seconds()
            for w in completed_workflows
        )
        
        return total_duration / len(completed_workflows)
