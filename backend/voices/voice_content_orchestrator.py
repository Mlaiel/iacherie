"""Voice Content Business Logic Orchestrator

Central orchestration system for voice content business logic, workflow management,
and enterprise-level voice processing coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from concurrent.futures import ThreadPoolExecutor
import uuid

try:
    from .creator_voice_intelligence import (
        CreatorVoiceIntelligenceEngine, 
        CreatorType, 
        VoiceContentType,
        CreatorVoiceProfile,
        VoiceAnalysisResult
    )
except ImportError:
    from creator_voice_intelligence import (
        CreatorVoiceIntelligenceEngine, 
        CreatorType, 
        VoiceContentType,
        CreatorVoiceProfile,
        VoiceAnalysisResult
    )

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Voice content workflow stages"""
    CONTENT_INGESTION = "content_ingestion"
    INTELLIGENCE_ANALYSIS = "intelligence_analysis"
    PROTECTION_PROCESSING = "protection_processing"
    MONETIZATION_OPTIMIZATION = "monetization_optimization"
    COLLABORATION_MATCHING = "collaboration_matching"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION_PREPARATION = "distribution_preparation"
    PERFORMANCE_TRACKING = "performance_tracking"


class ProcessingStatus(Enum):
    """Processing status for workflow stages"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY_NEEDED = "retry_needed"


class BusinessLogicTier(Enum):
    """Business logic processing tiers"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


@dataclass
class WorkflowTask:
    """Individual workflow task definition"""
    task_id: str
    stage: WorkflowStage
    task_type: str
    input_data: Dict[str, Any]
    processing_tier: BusinessLogicTier
    priority: int = 5  # 1-10, 10 being highest
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    created_at: datetime = field(default_factory=datetime.now)
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class VoiceContentWorkflow:
    """Complete voice content processing workflow"""
    workflow_id: str
    creator_id: str
    content_id: str
    creator_type: CreatorType
    content_type: VoiceContentType
    business_tier: BusinessLogicTier
    workflow_config: Dict[str, Any]
    tasks: List[WorkflowTask] = field(default_factory=list)
    workflow_status: ProcessingStatus = ProcessingStatus.PENDING
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    total_processing_time: Optional[float] = None
    business_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OrchestrationMetrics:
    """Orchestration performance and business metrics"""
    total_workflows_processed: int = 0
    successful_workflows: int = 0
    failed_workflows: int = 0
    average_processing_time: float = 0.0
    tier_performance: Dict[BusinessLogicTier, Dict[str, Any]] = field(default_factory=dict)
    stage_performance: Dict[WorkflowStage, Dict[str, Any]] = field(default_factory=dict)
    business_impact_metrics: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


class VoiceContentOrchestrator:
    """Voice Content Business Logic Orchestrator"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.intelligence_engine = CreatorVoiceIntelligenceEngine()
        self.executor = ThreadPoolExecutor(max_workers=self.config.get("max_workers", 10))
        
        # Workflow management
        self.active_workflows: Dict[str, VoiceContentWorkflow] = {}
        self.workflow_history: List[VoiceContentWorkflow] = []
        self.task_registry: Dict[str, Callable] = {}
        
        # Performance tracking
        self.metrics = OrchestrationMetrics()
        self.performance_history: List[Dict[str, Any]] = []
        
        # Business logic configuration
        self.tier_configurations = self._initialize_tier_configurations()
        self.stage_processors = self._initialize_stage_processors()
        
        # Workflow templates
        self.workflow_templates = self._initialize_workflow_templates()
        
        # Initialize task registry
        self._register_workflow_tasks()
        
    def _initialize_tier_configurations(self) -> Dict[BusinessLogicTier, Dict[str, Any]]:
        """Initialize business tier configurations"""
        return {
            BusinessLogicTier.BASIC: {
                "features": ["basic_analysis", "standard_protection", "basic_seo"],
                "processing_priority": 3,
                "resource_allocation": 0.25,
                "advanced_features": False,
                "collaboration_features": False,
                "premium_distribution": False
            },
            BusinessLogicTier.PROFESSIONAL: {
                "features": ["advanced_analysis", "enhanced_protection", "professional_seo", "basic_collaboration"],
                "processing_priority": 6,
                "resource_allocation": 0.5,
                "advanced_features": True,
                "collaboration_features": True,
                "premium_distribution": False
            },
            BusinessLogicTier.ENTERPRISE: {
                "features": ["ai_intelligence", "enterprise_protection", "advanced_seo", "full_collaboration", "analytics"],
                "processing_priority": 8,
                "resource_allocation": 0.75,
                "advanced_features": True,
                "collaboration_features": True,
                "premium_distribution": True
            },
            BusinessLogicTier.PREMIUM: {
                "features": ["full_ai_suite", "maximum_protection", "premium_seo", "enterprise_collaboration", "real_time_analytics"],
                "processing_priority": 10,
                "resource_allocation": 1.0,
                "advanced_features": True,
                "collaboration_features": True,
                "premium_distribution": True
            }
        }
    
    def _initialize_stage_processors(self) -> Dict[WorkflowStage, Dict[str, Any]]:
        """Initialize stage processing configurations"""
        return {
            WorkflowStage.CONTENT_INGESTION: {
                "processor": "content_processor",
                "dependencies": [],
                "timeout": 60,
                "retry_enabled": True
            },
            WorkflowStage.INTELLIGENCE_ANALYSIS: {
                "processor": "intelligence_processor",
                "dependencies": [WorkflowStage.CONTENT_INGESTION],
                "timeout": 300,
                "retry_enabled": True
            },
            WorkflowStage.PROTECTION_PROCESSING: {
                "processor": "protection_processor",
                "dependencies": [WorkflowStage.INTELLIGENCE_ANALYSIS],
                "timeout": 180,
                "retry_enabled": True
            },
            WorkflowStage.MONETIZATION_OPTIMIZATION: {
                "processor": "monetization_processor",
                "dependencies": [WorkflowStage.INTELLIGENCE_ANALYSIS],
                "timeout": 120,
                "retry_enabled": True
            },
            WorkflowStage.COLLABORATION_MATCHING: {
                "processor": "collaboration_processor",
                "dependencies": [WorkflowStage.INTELLIGENCE_ANALYSIS],
                "timeout": 240,
                "retry_enabled": True
            },
            WorkflowStage.SEO_OPTIMIZATION: {
                "processor": "seo_processor",
                "dependencies": [WorkflowStage.INTELLIGENCE_ANALYSIS],
                "timeout": 150,
                "retry_enabled": True
            },
            WorkflowStage.DISTRIBUTION_PREPARATION: {
                "processor": "distribution_processor",
                "dependencies": [WorkflowStage.PROTECTION_PROCESSING, WorkflowStage.SEO_OPTIMIZATION],
                "timeout": 120,
                "retry_enabled": True
            },
            WorkflowStage.PERFORMANCE_TRACKING: {
                "processor": "tracking_processor",
                "dependencies": [WorkflowStage.DISTRIBUTION_PREPARATION],
                "timeout": 60,
                "retry_enabled": False
            }
        }
    
    def _initialize_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize workflow templates for different scenarios"""
        return {
            "standard_voice_processing": {
                "stages": [
                    WorkflowStage.CONTENT_INGESTION,
                    WorkflowStage.INTELLIGENCE_ANALYSIS,
                    WorkflowStage.PROTECTION_PROCESSING,
                    WorkflowStage.SEO_OPTIMIZATION,
                    WorkflowStage.DISTRIBUTION_PREPARATION,
                    WorkflowStage.PERFORMANCE_TRACKING
                ],
                "parallel_stages": [
                    [WorkflowStage.PROTECTION_PROCESSING, WorkflowStage.MONETIZATION_OPTIMIZATION, WorkflowStage.SEO_OPTIMIZATION]
                ]
            },
            "collaboration_workflow": {
                "stages": [
                    WorkflowStage.CONTENT_INGESTION,
                    WorkflowStage.INTELLIGENCE_ANALYSIS,
                    WorkflowStage.COLLABORATION_MATCHING,
                    WorkflowStage.PROTECTION_PROCESSING,
                    WorkflowStage.SEO_OPTIMIZATION,
                    WorkflowStage.DISTRIBUTION_PREPARATION,
                    WorkflowStage.PERFORMANCE_TRACKING
                ],
                "parallel_stages": [
                    [WorkflowStage.PROTECTION_PROCESSING, WorkflowStage.SEO_OPTIMIZATION]
                ]
            },
            "premium_enterprise_workflow": {
                "stages": [
                    WorkflowStage.CONTENT_INGESTION,
                    WorkflowStage.INTELLIGENCE_ANALYSIS,
                    WorkflowStage.PROTECTION_PROCESSING,
                    WorkflowStage.MONETIZATION_OPTIMIZATION,
                    WorkflowStage.COLLABORATION_MATCHING,
                    WorkflowStage.SEO_OPTIMIZATION,
                    WorkflowStage.DISTRIBUTION_PREPARATION,
                    WorkflowStage.PERFORMANCE_TRACKING
                ],
                "parallel_stages": [
                    [WorkflowStage.PROTECTION_PROCESSING, WorkflowStage.MONETIZATION_OPTIMIZATION, WorkflowStage.COLLABORATION_MATCHING, WorkflowStage.SEO_OPTIMIZATION]
                ]
            }
        }
    
    def _register_workflow_tasks(self):
        """Register workflow task processors"""
        self.task_registry = {
            "content_processor": self._process_content_ingestion,
            "intelligence_processor": self._process_intelligence_analysis,
            "protection_processor": self._process_protection,
            "monetization_processor": self._process_monetization,
            "collaboration_processor": self._process_collaboration,
            "seo_processor": self._process_seo,
            "distribution_processor": self._process_distribution,
            "tracking_processor": self._process_performance_tracking
        }
    
    async def create_voice_content_workflow(
        self,
        creator_id: str,
        content_data: Union[bytes, str],
        creator_type: CreatorType,
        content_type: VoiceContentType,
        business_tier: BusinessLogicTier = BusinessLogicTier.PROFESSIONAL,
        workflow_template: str = "standard_voice_processing",
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create and initiate voice content processing workflow"""
        
        try:
            # Generate unique workflow ID
            workflow_id = f"workflow_{uuid.uuid4().hex[:12]}"
            content_id = f"content_{uuid.uuid4().hex[:8]}"
            
            self.logger.info(f"Creating workflow {workflow_id} for creator {creator_id}")
            
            # Get workflow template
            template = self.workflow_templates.get(workflow_template, self.workflow_templates["standard_voice_processing"])
            
            # Get tier configuration
            tier_config = self.tier_configurations[business_tier]
            
            # Create workflow configuration
            workflow_config = {
                "template": workflow_template,
                "tier_config": tier_config,
                "custom_config": custom_config or {},
                "content_data": content_data,
                "processing_options": {
                    "priority": tier_config["processing_priority"],
                    "resource_allocation": tier_config["resource_allocation"],
                    "features": tier_config["features"]
                }
            }
            
            # Create workflow instance
            workflow = VoiceContentWorkflow(
                workflow_id=workflow_id,
                creator_id=creator_id,
                content_id=content_id,
                creator_type=creator_type,
                content_type=content_type,
                business_tier=business_tier,
                workflow_config=workflow_config
            )
            
            # Generate workflow tasks
            workflow.tasks = await self._generate_workflow_tasks(workflow, template)
            
            # Store workflow
            self.active_workflows[workflow_id] = workflow
            
            # Start workflow processing
            asyncio.create_task(self._execute_workflow(workflow_id))
            
            self.logger.info(f"Workflow {workflow_id} created and initiated")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {str(e)}")
            raise
    
    async def _generate_workflow_tasks(
        self,
        workflow: VoiceContentWorkflow,
        template: Dict[str, Any]
    ) -> List[WorkflowTask]:
        """Generate workflow tasks based on template and configuration"""
        
        tasks = []
        tier_config = workflow.workflow_config["tier_config"]
        
        for stage in template["stages"]:
            # Check if stage is enabled for this tier
            stage_processor_config = self.stage_processors[stage]
            
            # Skip stages not available for this tier
            if not self._is_stage_enabled_for_tier(stage, tier_config):
                continue
            
            # Create task
            task = WorkflowTask(
                task_id=f"{workflow.workflow_id}_{stage.value}_{uuid.uuid4().hex[:8]}",
                stage=stage,
                task_type=stage_processor_config["processor"],
                input_data={
                    "workflow_id": workflow.workflow_id,
                    "creator_id": workflow.creator_id,
                    "content_id": workflow.content_id,
                    "creator_type": workflow.creator_type.value,
                    "content_type": workflow.content_type.value,
                    "content_data": workflow.workflow_config.get("content_data"),
                    "tier_config": tier_config,
                    "stage_config": stage_processor_config
                },
                processing_tier=workflow.business_tier,
                priority=tier_config["processing_priority"],
                dependencies=[dep.value for dep in stage_processor_config["dependencies"]],
                timeout_seconds=stage_processor_config["timeout"]
            )
            
            tasks.append(task)
        
        return tasks
    
    def _is_stage_enabled_for_tier(self, stage: WorkflowStage, tier_config: Dict[str, Any]) -> bool:
        """Check if a stage is enabled for the given tier"""
        stage_features = {
            WorkflowStage.CONTENT_INGESTION: True,  # Always enabled
            WorkflowStage.INTELLIGENCE_ANALYSIS: "advanced_analysis" in tier_config["features"] or "ai_intelligence" in tier_config["features"],
            WorkflowStage.PROTECTION_PROCESSING: True,  # Always enabled with different levels
            WorkflowStage.MONETIZATION_OPTIMIZATION: tier_config["advanced_features"],
            WorkflowStage.COLLABORATION_MATCHING: tier_config["collaboration_features"],
            WorkflowStage.SEO_OPTIMIZATION: True,  # Always enabled with different levels
            WorkflowStage.DISTRIBUTION_PREPARATION: True,  # Always enabled
            WorkflowStage.PERFORMANCE_TRACKING: tier_config["advanced_features"]
        }
        
        return stage_features.get(stage, True)
    
    async def _execute_workflow(self, workflow_id: str):
        """Execute workflow with proper orchestration"""
        
        try:
            workflow = self.active_workflows[workflow_id]
            workflow.workflow_status = ProcessingStatus.IN_PROGRESS
            workflow.start_time = datetime.now()
            
            self.logger.info(f"Starting workflow execution: {workflow_id}")
            
            # Execute tasks based on dependencies
            completed_tasks = set()
            failed_tasks = set()
            
            while len(completed_tasks) + len(failed_tasks) < len(workflow.tasks):
                # Find tasks ready to execute
                ready_tasks = [
                    task for task in workflow.tasks
                    if (task.status == ProcessingStatus.PENDING and
                        all(dep in completed_tasks or dep in [t.stage.value for t in workflow.tasks if t.status == ProcessingStatus.COMPLETED] 
                            for dep in task.dependencies))
                ]
                
                if not ready_tasks:
                    # Check if we're stuck due to failed dependencies
                    remaining_tasks = [t for t in workflow.tasks if t.status == ProcessingStatus.PENDING]
                    if remaining_tasks:
                        self.logger.warning(f"Workflow {workflow_id} stuck - failed dependencies")
                        for task in remaining_tasks:
                            task.status = ProcessingStatus.SKIPPED
                            task.error_message = "Skipped due to failed dependencies"
                    break
                
                # Execute ready tasks
                task_futures = []
                for task in ready_tasks:
                    future = asyncio.create_task(self._execute_task(task))
                    task_futures.append((task, future))
                
                # Wait for task completion
                for task, future in task_futures:
                    try:
                        result = await future
                        task.result = result
                        task.status = ProcessingStatus.COMPLETED
                        completed_tasks.add(task.stage.value)
                        self.logger.info(f"Task completed: {task.task_id}")
                    except Exception as e:
                        task.status = ProcessingStatus.FAILED
                        task.error_message = str(e)
                        failed_tasks.add(task.stage.value)
                        self.logger.error(f"Task failed: {task.task_id} - {str(e)}")
            
            # Finalize workflow
            workflow.completion_time = datetime.now()
            workflow.total_processing_time = (workflow.completion_time - workflow.start_time).total_seconds()
            
            if failed_tasks:
                workflow.workflow_status = ProcessingStatus.FAILED
            else:
                workflow.workflow_status = ProcessingStatus.COMPLETED
            
            # Calculate business metrics
            workflow.business_metrics = await self._calculate_workflow_metrics(workflow)
            
            # Update orchestration metrics
            await self._update_orchestration_metrics(workflow)
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"Workflow {workflow_id} completed with status: {workflow.workflow_status.value}")
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id].workflow_status = ProcessingStatus.FAILED
    
    async def _execute_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute individual workflow task"""
        
        try:
            task.status = ProcessingStatus.IN_PROGRESS
            self.logger.info(f"Executing task: {task.task_id}")
            
            # Get task processor
            processor = self.task_registry.get(task.task_type)
            if not processor:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Execute task with timeout
            result = await asyncio.wait_for(
                processor(task),
                timeout=task.timeout_seconds
            )
            
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Task {task.task_id} timed out after {task.timeout_seconds} seconds")
        except Exception as e:
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = ProcessingStatus.RETRY_NEEDED
                self.logger.warning(f"Task {task.task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
                return await self._execute_task(task)
            else:
                raise
    
    # Task processors
    async def _process_content_ingestion(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process content ingestion stage"""
        self.logger.info(f"Processing content ingestion for task {task.task_id}")
        
        # Simulate content processing
        await asyncio.sleep(1)
        
        return {
            "stage": "content_ingestion",
            "status": "completed",
            "content_processed": True,
            "content_size": len(str(task.input_data.get("content_data", ""))),
            "processing_time": 1.0
        }
    
    async def _process_intelligence_analysis(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process intelligence analysis stage"""
        self.logger.info(f"Processing intelligence analysis for task {task.task_id}")
        
        # Use intelligence engine for analysis
        analysis_result = await self.intelligence_engine.analyze_creator_voice_content(
            creator_id=task.input_data["creator_id"],
            content_data=task.input_data.get("content_data", b""),
            content_type=VoiceContentType(task.input_data["content_type"]),
            creator_type=CreatorType(task.input_data["creator_type"])
        )
        
        return {
            "stage": "intelligence_analysis",
            "status": "completed",
            "analysis_result": {
                "quality_scores": analysis_result.quality_scores,
                "commercial_potential": analysis_result.commercial_potential,
                "improvement_suggestions": analysis_result.improvement_suggestions
            },
            "processing_time": 2.0
        }
    
    async def _process_protection(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process voice protection stage"""
        self.logger.info(f"Processing protection for task {task.task_id}")
        
        tier_config = task.input_data["tier_config"]
        protection_level = "basic"
        
        if "enhanced_protection" in tier_config["features"]:
            protection_level = "enhanced"
        elif "enterprise_protection" in tier_config["features"]:
            protection_level = "enterprise"
        elif "maximum_protection" in tier_config["features"]:
            protection_level = "maximum"
        
        await asyncio.sleep(1.5)
        
        return {
            "stage": "protection_processing",
            "status": "completed",
            "protection_level": protection_level,
            "protection_applied": True,
            "fingerprint_generated": True,
            "processing_time": 1.5
        }
    
    async def _process_monetization(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process monetization optimization stage"""
        self.logger.info(f"Processing monetization for task {task.task_id}")
        
        await asyncio.sleep(1.2)
        
        return {
            "stage": "monetization_optimization",
            "status": "completed",
            "monetization_strategies": ["premium_content", "licensing", "coaching"],
            "revenue_potential": 0.78,
            "optimization_applied": True,
            "processing_time": 1.2
        }
    
    async def _process_collaboration(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process collaboration matching stage"""
        self.logger.info(f"Processing collaboration for task {task.task_id}")
        
        await asyncio.sleep(2.0)
        
        return {
            "stage": "collaboration_matching",
            "status": "completed",
            "potential_collaborators": 5,
            "collaboration_suggestions": ["duet", "podcast_guest", "harmony_feature"],
            "matching_score": 0.82,
            "processing_time": 2.0
        }
    
    async def _process_seo(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process SEO optimization stage"""
        self.logger.info(f"Processing SEO for task {task.task_id}")
        
        await asyncio.sleep(1.3)
        
        return {
            "stage": "seo_optimization",
            "status": "completed",
            "keywords_optimized": 15,
            "seo_score": 0.75,
            "optimization_applied": True,
            "processing_time": 1.3
        }
    
    async def _process_distribution(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process distribution preparation stage"""
        self.logger.info(f"Processing distribution for task {task.task_id}")
        
        await asyncio.sleep(1.0)
        
        return {
            "stage": "distribution_preparation",
            "status": "completed",
            "platforms_prepared": ["spotify", "apple_music", "youtube", "podcast_platforms"],
            "distribution_ready": True,
            "processing_time": 1.0
        }
    
    async def _process_performance_tracking(self, task: WorkflowTask) -> Dict[str, Any]:
        """Process performance tracking setup stage"""
        self.logger.info(f"Processing performance tracking for task {task.task_id}")
        
        await asyncio.sleep(0.5)
        
        return {
            "stage": "performance_tracking",
            "status": "completed",
            "tracking_enabled": True,
            "metrics_configured": ["engagement", "revenue", "reach", "quality"],
            "processing_time": 0.5
        }
    
    async def _calculate_workflow_metrics(self, workflow: VoiceContentWorkflow) -> Dict[str, Any]:
        """Calculate business metrics for completed workflow"""
        
        completed_tasks = [t for t in workflow.tasks if t.status == ProcessingStatus.COMPLETED]
        failed_tasks = [t for t in workflow.tasks if t.status == ProcessingStatus.FAILED]
        
        success_rate = len(completed_tasks) / len(workflow.tasks) if workflow.tasks else 0
        
        # Extract results from tasks
        intelligence_result = next((t.result for t in completed_tasks if t.stage == WorkflowStage.INTELLIGENCE_ANALYSIS), {})
        protection_result = next((t.result for t in completed_tasks if t.stage == WorkflowStage.PROTECTION_PROCESSING), {})
        monetization_result = next((t.result for t in completed_tasks if t.stage == WorkflowStage.MONETIZATION_OPTIMIZATION), {})
        
        return {
            "workflow_success_rate": success_rate,
            "total_processing_time": workflow.total_processing_time,
            "completed_stages": len(completed_tasks),
            "failed_stages": len(failed_tasks),
            "business_impact": {
                "quality_improvement": intelligence_result.get("analysis_result", {}).get("commercial_potential", 0),
                "protection_applied": protection_result.get("protection_applied", False),
                "monetization_potential": monetization_result.get("revenue_potential", 0),
                "tier_value_delivered": workflow.business_tier.value
            },
            "performance_metrics": {
                "efficiency_score": min(1.0, 300 / (workflow.total_processing_time or 300)),  # Target 5 minutes
                "quality_score": intelligence_result.get("analysis_result", {}).get("commercial_potential", 0.5),
                "feature_utilization": len(completed_tasks) / len(workflow.tasks)
            }
        }
    
    async def _update_orchestration_metrics(self, workflow: VoiceContentWorkflow):
        """Update overall orchestration metrics"""
        
        self.metrics.total_workflows_processed += 1
        
        if workflow.workflow_status == ProcessingStatus.COMPLETED:
            self.metrics.successful_workflows += 1
        else:
            self.metrics.failed_workflows += 1
        
        # Update average processing time
        if workflow.total_processing_time:
            total_time = (self.metrics.average_processing_time * (self.metrics.total_workflows_processed - 1) + 
                         workflow.total_processing_time) / self.metrics.total_workflows_processed
            self.metrics.average_processing_time = total_time
        
        # Update tier performance
        if workflow.business_tier not in self.metrics.tier_performance:
            self.metrics.tier_performance[workflow.business_tier] = {
                "total_workflows": 0,
                "successful_workflows": 0,
                "average_processing_time": 0.0,
                "success_rate": 0.0
            }
        
        tier_metrics = self.metrics.tier_performance[workflow.business_tier]
        tier_metrics["total_workflows"] += 1
        if workflow.workflow_status == ProcessingStatus.COMPLETED:
            tier_metrics["successful_workflows"] += 1
        tier_metrics["success_rate"] = tier_metrics["successful_workflows"] / tier_metrics["total_workflows"]
        
        self.metrics.last_updated = datetime.now()
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": workflow.workflow_status.value,
                "progress": self._calculate_workflow_progress(workflow),
                "current_stage": self._get_current_stage(workflow),
                "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
                "estimated_completion": self._estimate_completion_time(workflow)
            }
        
        # Check completed workflows
        for workflow in self.workflow_history:
            if workflow.workflow_id == workflow_id:
                return {
                    "workflow_id": workflow_id,
                    "status": workflow.workflow_status.value,
                    "progress": 100.0,
                    "completion_time": workflow.completion_time.isoformat() if workflow.completion_time else None,
                    "total_processing_time": workflow.total_processing_time,
                    "business_metrics": workflow.business_metrics
                }
        
        return None
    
    def _calculate_workflow_progress(self, workflow: VoiceContentWorkflow) -> float:
        """Calculate workflow progress percentage"""
        if not workflow.tasks:
            return 0.0
        
        completed_tasks = len([t for t in workflow.tasks if t.status == ProcessingStatus.COMPLETED])
        return (completed_tasks / len(workflow.tasks)) * 100.0
    
    def _get_current_stage(self, workflow: VoiceContentWorkflow) -> Optional[str]:
        """Get current processing stage"""
        in_progress_tasks = [t for t in workflow.tasks if t.status == ProcessingStatus.IN_PROGRESS]
        if in_progress_tasks:
            return in_progress_tasks[0].stage.value
        
        pending_tasks = [t for t in workflow.tasks if t.status == ProcessingStatus.PENDING]
        if pending_tasks:
            return f"waiting_for_{pending_tasks[0].stage.value}"
        
        return "finalizing"
    
    def _estimate_completion_time(self, workflow: VoiceContentWorkflow) -> Optional[str]:
        """Estimate workflow completion time"""
        if not workflow.start_time:
            return None
        
        progress = self._calculate_workflow_progress(workflow) / 100.0
        if progress == 0:
            return None
        
        elapsed_time = (datetime.now() - workflow.start_time).total_seconds()
        estimated_total_time = elapsed_time / progress
        estimated_completion = workflow.start_time + timedelta(seconds=estimated_total_time)
        
        return estimated_completion.isoformat()
    
    async def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestration performance metrics"""
        
        return {
            "overall_metrics": {
                "total_workflows": self.metrics.total_workflows_processed,
                "success_rate": self.metrics.successful_workflows / max(1, self.metrics.total_workflows_processed),
                "average_processing_time": self.metrics.average_processing_time,
                "active_workflows": len(self.active_workflows)
            },
            "tier_performance": {tier.value: metrics for tier, metrics in self.metrics.tier_performance.items()},
            "stage_performance": {stage.value: metrics for stage, metrics in self.metrics.stage_performance.items()},
            "business_impact": self.metrics.business_impact_metrics,
            "last_updated": self.metrics.last_updated.isoformat()
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.workflow_status = ProcessingStatus.FAILED
            workflow.completion_time = datetime.now()
            
            # Cancel pending tasks
            for task in workflow.tasks:
                if task.status == ProcessingStatus.PENDING:
                    task.status = ProcessingStatus.SKIPPED
                    task.error_message = "Workflow cancelled by user"
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            self.logger.info(f"Workflow {workflow_id} cancelled")
            return True
        
        return False