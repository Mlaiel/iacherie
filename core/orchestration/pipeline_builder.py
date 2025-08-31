"""Pipeline Builder - Enterprise Pipeline Construction System

Advanced pipeline building engine for creating complex, intelligent content processing
pipelines with AI-powered optimization and dynamic workflow generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union, Set, Type
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from backend.core.orchestration.workflow_engine import (
    WorkflowDefinition, TaskDefinition, ExecutionMode
)


class PipelineType(Enum):
    """Pipeline type classifications."""
    CONTENT_PROCESSING = "content_processing"
    PROTECTION_WORKFLOW = "protection_workflow"
    MONETIZATION_PIPELINE = "monetization_pipeline"
    COLLABORATION_MATCHING = "collaboration_matching"
    DISTRIBUTION_PIPELINE = "distribution_pipeline"
    ANALYTICS_PIPELINE = "analytics_pipeline"
    SEO_OPTIMIZATION = "seo_optimization"
    RIGHTS_MANAGEMENT = "rights_management"


class StageType(Enum):
    """Pipeline stage types."""
    INPUT_VALIDATION = "input_validation"
    PRE_PROCESSING = "pre_processing"
    AI_PROCESSING = "ai_processing"
    PROTECTION_SCAN = "protection_scan"
    QUALITY_CHECK = "quality_check"
    OPTIMIZATION = "optimization"
    POST_PROCESSING = "post_processing"
    OUTPUT_DELIVERY = "output_delivery"
    NOTIFICATION = "notification"


@dataclass
class PipelineStage:
    """Individual pipeline stage definition."""
    stage_id: str
    name: str
    stage_type: StageType
    handler_class: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    parallel_capable: bool = False
    critical: bool = True
    timeout: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineTemplate:
    """Reusable pipeline template definition."""
    template_id: str
    name: str
    description: str
    pipeline_type: PipelineType
    stages: List[PipelineStage]
    default_config: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineBuilder:
    """
    Enterprise Pipeline Builder for constructing intelligent content processing pipelines.
    
    Features:
    - Template-based pipeline generation
    - Dynamic stage configuration
    - AI-powered optimization
    - Dependency resolution
    - Performance profiling
    """
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the pipeline builder."""
        self.logger = logger or logging.getLogger(__name__)
        self.templates: Dict[str, PipelineTemplate] = {}
        self.stage_handlers: Dict[str, Type] = {}
        self.optimization_rules: Dict[str, Callable] = {}
        self._initialize_default_templates()
        self._register_optimization_rules()

    def _initialize_default_templates(self):
        """Initialize default pipeline templates for common workflows."""
        # Content Processing Pipeline Template
        content_stages = [
            PipelineStage(
                stage_id="input_validation",
                name="Content Input Validation",
                stage_type=StageType.INPUT_VALIDATION,
                handler_class="backend.core.validation.ContentValidator",
                timeout=30
            ),
            PipelineStage(
                stage_id="format_detection",
                name="Format Detection & Analysis",
                stage_type=StageType.PRE_PROCESSING,
                handler_class="backend.core.processors.FormatDetector",
                dependencies=["input_validation"],
                timeout=60
            ),
            PipelineStage(
                stage_id="ai_fingerprinting",
                name="AI Fingerprinting Generation",
                stage_type=StageType.AI_PROCESSING,
                handler_class="backend.core.protection.FingerprintEngine",
                dependencies=["format_detection"],
                timeout=300
            ),
            PipelineStage(
                stage_id="protection_scan",
                name="Content Protection Scan",
                stage_type=StageType.PROTECTION_SCAN,
                handler_class="backend.core.protection.ProtectionScanner",
                dependencies=["ai_fingerprinting"],
                parallel_capable=True,
                timeout=180
            ),
            PipelineStage(
                stage_id="seo_optimization",
                name="SEO Metadata Optimization",
                stage_type=StageType.OPTIMIZATION,
                handler_class="backend.core.seo.MetadataOptimizer",
                dependencies=["protection_scan"],
                timeout=120
            ),
            PipelineStage(
                stage_id="distribution_prep",
                name="Distribution Preparation",
                stage_type=StageType.POST_PROCESSING,
                handler_class="backend.core.distribution.DistributionPreprocessor",
                dependencies=["seo_optimization"],
                timeout=90
            )
        ]
        
        content_template = PipelineTemplate(
            template_id="content_processing_v1",
            name="Content Processing Pipeline",
            description="Complete content processing with protection and optimization",
            pipeline_type=PipelineType.CONTENT_PROCESSING,
            stages=content_stages
        )
        
        self.templates["content_processing"] = content_template

        # Protection Workflow Template
        protection_stages = [
            PipelineStage(
                stage_id="fingerprint_generation",
                name="Multi-Modal Fingerprint Generation",
                stage_type=StageType.AI_PROCESSING,
                handler_class="backend.core.protection.MultiFingerprintEngine",
                timeout=600
            ),
            PipelineStage(
                stage_id="database_indexing",
                name="Vector Database Indexing",
                stage_type=StageType.POST_PROCESSING,
                handler_class="backend.core.storage.VectorIndexer",
                dependencies=["fingerprint_generation"],
                timeout=120
            ),
            PipelineStage(
                stage_id="monitoring_setup",
                name="Surveillance Monitoring Setup",
                stage_type=StageType.POST_PROCESSING,
                handler_class="backend.core.monitoring.SurveillanceManager",
                dependencies=["database_indexing"],
                timeout=60
            ),
            PipelineStage(
                stage_id="rights_registration",
                name="Digital Rights Registration",
                stage_type=StageType.POST_PROCESSING,
                handler_class="backend.core.rights.RightsRegistrar",
                dependencies=["monitoring_setup"],
                timeout=300
            )
        ]
        
        protection_template = PipelineTemplate(
            template_id="protection_workflow_v1",
            name="Content Protection Workflow",
            description="Comprehensive content protection and rights management",
            pipeline_type=PipelineType.PROTECTION_WORKFLOW,
            stages=protection_stages
        )
        
        self.templates["protection_workflow"] = protection_template

        # Monetization Pipeline Template
        monetization_stages = [
            PipelineStage(
                stage_id="revenue_analysis",
                name="Revenue Potential Analysis",
                stage_type=StageType.AI_PROCESSING,
                handler_class="backend.core.monetization.RevenueAnalyzer",
                timeout=120
            ),
            PipelineStage(
                stage_id="platform_optimization",
                name="Platform-Specific Optimization",
                stage_type=StageType.OPTIMIZATION,
                handler_class="backend.core.monetization.PlatformOptimizer",
                dependencies=["revenue_analysis"],
                parallel_capable=True,
                timeout=180
            ),
            PipelineStage(
                stage_id="distribution_strategy",
                name="Distribution Strategy Generation",
                stage_type=StageType.AI_PROCESSING,
                handler_class="backend.core.distribution.StrategyEngine",
                dependencies=["platform_optimization"],
                timeout=90
            ),
            PipelineStage(
                stage_id="monetization_setup",
                name="Monetization Channel Setup",
                stage_type=StageType.POST_PROCESSING,
                handler_class="backend.core.monetization.ChannelManager",
                dependencies=["distribution_strategy"],
                timeout=300
            )
        ]
        
        monetization_template = PipelineTemplate(
            template_id="monetization_pipeline_v1",
            name="Monetization Pipeline",
            description="Automated monetization setup and optimization",
            pipeline_type=PipelineType.MONETIZATION_PIPELINE,
            stages=monetization_stages
        )
        
        self.templates["monetization_pipeline"] = monetization_template

    def _register_optimization_rules(self):
        """Register optimization rules for pipeline efficiency."""
        self.optimization_rules = {
            "parallel_execution": self._optimize_parallel_execution,
            "resource_allocation": self._optimize_resource_allocation,
            "dependency_minimization": self._optimize_dependencies,
            "timeout_optimization": self._optimize_timeouts,
            "stage_merging": self._optimize_stage_merging
        }

    def create_pipeline(
        self,
        pipeline_name: str,
        template_id: str,
        custom_config: Optional[Dict[str, Any]] = None,
        optimization_enabled: bool = True
    ) -> WorkflowDefinition:
        """
        Create a new pipeline from template with optional customization.
        
        Args:
            pipeline_name: Name for the new pipeline
            template_id: Template identifier to use
            custom_config: Custom configuration overrides
            optimization_enabled: Whether to apply optimization rules
            
        Returns:
            WorkflowDefinition: Complete workflow definition
        """
        try:
            if template_id not in self.templates:
                raise ValueError(f"Template '{template_id}' not found")
            
            template = self.templates[template_id]
            workflow_id = str(uuid.uuid4())
            
            # Convert pipeline stages to workflow tasks
            tasks = []
            for stage in template.stages:
                task = self._convert_stage_to_task(stage, custom_config)
                tasks.append(task)
            
            # Create workflow definition
            workflow = WorkflowDefinition(
                workflow_id=workflow_id,
                name=pipeline_name,
                description=f"Pipeline: {template.description}",
                tasks=tasks,
                execution_mode=ExecutionMode.HYBRID,
                timeout=self._calculate_total_timeout(template.stages),
                max_retries=3,
                retry_delay=15,
                rollback_enabled=True,
                metadata={
                    "template_id": template_id,
                    "pipeline_type": template.pipeline_type.value,
                    "created_at": datetime.utcnow().isoformat(),
                    "optimization_applied": optimization_enabled
                }
            )
            
            # Apply optimization if enabled
            if optimization_enabled:
                workflow = self._optimize_workflow(workflow)
            
            self.logger.info(f"Created pipeline '{pipeline_name}' from template '{template_id}'")
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to create pipeline: {str(e)}")
            raise

    def _convert_stage_to_task(
        self,
        stage: PipelineStage,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> TaskDefinition:
        """Convert pipeline stage to workflow task definition."""
        # Merge custom configuration with stage configuration
        final_config = {**stage.configuration}
        if custom_config and stage.stage_id in custom_config:
            final_config.update(custom_config[stage.stage_id])
        
        return TaskDefinition(
            task_id=stage.stage_id,
            name=stage.name,
            handler=stage.handler_class,
            parameters=final_config,
            dependencies=stage.dependencies,
            timeout=stage.timeout,
            retry_count=stage.retry_policy.get("max_retries", 3),
            retry_delay=stage.retry_policy.get("delay", 5),
            required=stage.critical,
            conditions=stage.conditions,
            metadata={
                "stage_type": stage.stage_type.value,
                "parallel_capable": stage.parallel_capable,
                **stage.metadata
            }
        )

    def _calculate_total_timeout(self, stages: List[PipelineStage]) -> int:
        """Calculate total pipeline timeout based on stage timeouts."""
        total_timeout = 0
        for stage in stages:
            if stage.timeout:
                total_timeout += stage.timeout
            else:
                total_timeout += 300  # Default 5 minutes per stage
        
        # Add 20% buffer for overhead
        return int(total_timeout * 1.2)

    def _optimize_workflow(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Apply optimization rules to workflow definition."""
        try:
            for rule_name, rule_func in self.optimization_rules.items():
                workflow = rule_func(workflow)
                self.logger.debug(f"Applied optimization rule: {rule_name}")
            
            return workflow
            
        except Exception as e:
            self.logger.warning(f"Workflow optimization failed: {str(e)}")
            return workflow

    def _optimize_parallel_execution(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize workflow for parallel execution where possible."""
        # Identify tasks that can run in parallel
        parallel_groups = self._identify_parallel_groups(workflow.tasks)
        
        # Update execution mode based on parallelization opportunities
        if len(parallel_groups) > 1:
            workflow.execution_mode = ExecutionMode.HYBRID
        
        return workflow

    def _optimize_resource_allocation(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize resource allocation based on task requirements."""
        for task in workflow.tasks:
            # Add resource hints based on task type
            if "ai_processing" in task.metadata.get("stage_type", ""):
                task.metadata["resource_requirements"] = {
                    "cpu_intensive": True,
                    "memory_mb": 2048,
                    "gpu_preferred": True
                }
            elif "fingerprinting" in task.handler.lower():
                task.metadata["resource_requirements"] = {
                    "cpu_intensive": True,
                    "memory_mb": 4096,
                    "io_intensive": True
                }
        
        return workflow

    def _optimize_dependencies(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Minimize and optimize task dependencies."""
        # Remove redundant dependencies
        for task in workflow.tasks:
            task.dependencies = list(set(task.dependencies))  # Remove duplicates
        
        return workflow

    def _optimize_timeouts(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize timeout values based on task complexity."""
        for task in workflow.tasks:
            if not task.timeout:
                # Set intelligent defaults based on task type
                if "ai_processing" in task.metadata.get("stage_type", ""):
                    task.timeout = 600  # 10 minutes for AI processing
                elif "validation" in task.metadata.get("stage_type", ""):
                    task.timeout = 60   # 1 minute for validation
                else:
                    task.timeout = 300  # 5 minutes default
        
        return workflow

    def _optimize_stage_merging(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Merge compatible stages for efficiency."""
        # This is a placeholder for more sophisticated stage merging logic
        # In practice, this would analyze stage compatibility and merge them
        return workflow

    def _identify_parallel_groups(self, tasks: List[TaskDefinition]) -> List[List[str]]:
        """Identify groups of tasks that can run in parallel."""
        parallel_groups = []
        processed_tasks = set()
        
        for task in tasks:
            if task.task_id in processed_tasks:
                continue
                
            # Find tasks with no dependencies or same dependencies
            group = [task.task_id]
            for other_task in tasks:
                if (other_task.task_id != task.task_id and 
                    other_task.task_id not in processed_tasks and
                    set(other_task.dependencies) == set(task.dependencies)):
                    group.append(other_task.task_id)
            
            if len(group) > 1:
                parallel_groups.append(group)
            
            processed_tasks.update(group)
        
        return parallel_groups

    def register_template(self, template: PipelineTemplate):
        """Register a new pipeline template."""
        self.templates[template.template_id] = template
        self.logger.info(f"Registered pipeline template: {template.template_id}")

    def get_template(self, template_id: str) -> Optional[PipelineTemplate]:
        """Retrieve a pipeline template by ID."""
        return self.templates.get(template_id)

    def list_templates(self) -> List[str]:
        """List all available pipeline template IDs."""
        return list(self.templates.keys())

    def validate_pipeline(self, workflow: WorkflowDefinition) -> Dict[str, List[str]]:
        """Validate pipeline definition and return any issues."""
        issues = {
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check for circular dependencies
        if self._has_circular_dependencies(workflow.tasks):
            issues["errors"].append("Circular dependencies detected in workflow")
        
        # Check for orphaned tasks
        orphaned = self._find_orphaned_tasks(workflow.tasks)
        if orphaned:
            issues["warnings"].extend([f"Orphaned task: {task_id}" for task_id in orphaned])
        
        # Check for performance recommendations
        long_running_tasks = [
            task.task_id for task in workflow.tasks 
            if task.timeout and task.timeout > 600
        ]
        if long_running_tasks:
            issues["recommendations"].append(
                f"Consider breaking down long-running tasks: {', '.join(long_running_tasks)}"
            )
        
        return issues

    def _has_circular_dependencies(self, tasks: List[TaskDefinition]) -> bool:
        """Check for circular dependencies in task definitions."""
        task_deps = {task.task_id: set(task.dependencies) for task in tasks}
        
        def has_cycle(task_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)
            
            for dep in task_deps.get(task_id, set()):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(task_id)
            return False
        
        visited = set()
        for task in tasks:
            if task.task_id not in visited:
                if has_cycle(task.task_id, visited, set()):
                    return True
        
        return False

    def _find_orphaned_tasks(self, tasks: List[TaskDefinition]) -> List[str]:
        """Find tasks with dependencies that don't exist."""
        task_ids = {task.task_id for task in tasks}
        orphaned = []
        
        for task in tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    orphaned.append(task.task_id)
                    break
        
        return orphaned

    async def build_dynamic_pipeline(
        self,
        content_type: str,
        requirements: Dict[str, Any],
        optimization_level: str = "balanced"
    ) -> WorkflowDefinition:
        """
        Build a dynamic pipeline based on content type and specific requirements.
        
        Args:
            content_type: Type of content (audio, video, image, text)
            requirements: Specific processing requirements
            optimization_level: Performance optimization level (fast, balanced, quality)
            
        Returns:
            WorkflowDefinition: Dynamically generated workflow
        """
        try:
            # Select appropriate base template
            base_template = self._select_base_template(content_type, requirements)
            
            # Customize stages based on requirements
            customized_stages = self._customize_stages(
                base_template.stages, 
                content_type, 
                requirements,
                optimization_level
            )
            
            # Generate workflow
            workflow_id = str(uuid.uuid4())
            workflow_name = f"Dynamic {content_type.title()} Pipeline"
            
            tasks = [
                self._convert_stage_to_task(stage, requirements.get("stage_config", {}))
                for stage in customized_stages
            ]
            
            workflow = WorkflowDefinition(
                workflow_id=workflow_id,
                name=workflow_name,
                description=f"Dynamically generated {content_type} processing pipeline",
                tasks=tasks,
                execution_mode=self._determine_execution_mode(optimization_level),
                timeout=self._calculate_total_timeout(customized_stages),
                max_retries=requirements.get("max_retries", 3),
                retry_delay=requirements.get("retry_delay", 15),
                rollback_enabled=requirements.get("rollback_enabled", True),
                metadata={
                    "content_type": content_type,
                    "optimization_level": optimization_level,
                    "dynamic_generation": True,
                    "generated_at": datetime.utcnow().isoformat(),
                    "requirements": requirements
                }
            )
            
            # Apply optimization
            workflow = self._optimize_workflow(workflow)
            
            self.logger.info(
                f"Built dynamic {content_type} pipeline with {len(tasks)} stages"
            )
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to build dynamic pipeline: {str(e)}")
            raise

    def _select_base_template(
        self, 
        content_type: str, 
        requirements: Dict[str, Any]
    ) -> PipelineTemplate:
        """Select the most appropriate base template."""
        # Priority mapping for different content types and requirements
        if requirements.get("protection_required", False):
            return self.templates["protection_workflow"]
        elif requirements.get("monetization_focus", False):
            return self.templates["monetization_pipeline"]
        else:
            return self.templates["content_processing"]

    def _customize_stages(
        self,
        base_stages: List[PipelineStage],
        content_type: str,
        requirements: Dict[str, Any],
        optimization_level: str
    ) -> List[PipelineStage]:
        """Customize pipeline stages based on specific requirements."""
        customized_stages = []
        
        for stage in base_stages:
            # Clone the stage
            custom_stage = PipelineStage(
                stage_id=stage.stage_id,
                name=stage.name,
                stage_type=stage.stage_type,
                handler_class=self._customize_handler(stage.handler_class, content_type),
                configuration={**stage.configuration},
                dependencies=stage.dependencies.copy(),
                parallel_capable=stage.parallel_capable,
                critical=stage.critical,
                timeout=stage.timeout,
                retry_policy=stage.retry_policy.copy(),
                conditions=stage.conditions.copy(),
                metadata={**stage.metadata}
            )
            
            # Apply content-type specific customizations
            self._apply_content_customizations(custom_stage, content_type, requirements)
            
            # Apply optimization level adjustments
            self._apply_optimization_adjustments(custom_stage, optimization_level)
            
            customized_stages.append(custom_stage)
        
        return customized_stages

    def _customize_handler(self, base_handler: str, content_type: str) -> str:
        """Customize handler class based on content type."""
        handler_mapping = {
            "audio": {
                "FingerprintEngine": "AudioFingerprintEngine",
                "FormatDetector": "AudioFormatDetector"
            },
            "video": {
                "FingerprintEngine": "VideoFingerprintEngine", 
                "FormatDetector": "VideoFormatDetector"
            },
            "image": {
                "FingerprintEngine": "ImageFingerprintEngine",
                "FormatDetector": "ImageFormatDetector"
            },
            "text": {
                "FingerprintEngine": "TextFingerprintEngine",
                "FormatDetector": "TextFormatDetector"
            }
        }
        
        # Extract class name from full path
        class_name = base_handler.split('.')[-1]
        
        # Apply content-specific mapping if available
        if content_type in handler_mapping and class_name in handler_mapping[content_type]:
            specialized_class = handler_mapping[content_type][class_name]
            return base_handler.replace(class_name, specialized_class)
        
        return base_handler

    def _apply_content_customizations(
        self,
        stage: PipelineStage,
        content_type: str,
        requirements: Dict[str, Any]
    ):
        """Apply content-type specific customizations to stage."""
        # Content-specific configuration
        content_configs = {
            "audio": {
                "sample_rate": requirements.get("sample_rate", 44100),
                "channels": requirements.get("channels", 2),
                "format_priority": ["wav", "flac", "mp3"]
            },
            "video": {
                "resolution": requirements.get("resolution", "1080p"),
                "fps": requirements.get("fps", 30),
                "codec_priority": ["h264", "h265", "vp9"]
            },
            "image": {
                "max_resolution": requirements.get("max_resolution", "4k"),
                "format_priority": ["png", "jpg", "webp"]
            },
            "text": {
                "language": requirements.get("language", "auto"),
                "encoding": requirements.get("encoding", "utf-8")
            }
        }
        
        if content_type in content_configs:
            stage.configuration.update(content_configs[content_type])

    def _apply_optimization_adjustments(
        self,
        stage: PipelineStage,
        optimization_level: str
    ):
        """Apply optimization level adjustments to stage."""
        optimization_configs = {
            "fast": {
                "quality_level": "low",
                "parallel_processing": True,
                "timeout_multiplier": 0.7
            },
            "balanced": {
                "quality_level": "medium",
                "parallel_processing": True,
                "timeout_multiplier": 1.0
            },
            "quality": {
                "quality_level": "high",
                "parallel_processing": False,
                "timeout_multiplier": 1.5
            }
        }
        
        if optimization_level in optimization_configs:
            config = optimization_configs[optimization_level]
            stage.configuration.update(config)
            
            # Adjust timeout based on optimization level
            if stage.timeout:
                stage.timeout = int(stage.timeout * config["timeout_multiplier"])

    def _determine_execution_mode(self, optimization_level: str) -> ExecutionMode:
        """Determine execution mode based on optimization level."""
        mode_mapping = {
            "fast": ExecutionMode.PARALLEL,
            "balanced": ExecutionMode.HYBRID,
            "quality": ExecutionMode.SEQUENTIAL
        }
        return mode_mapping.get(optimization_level, ExecutionMode.HYBRID)

    def export_pipeline(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """Export pipeline definition to JSON-serializable format."""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "execution_mode": workflow.execution_mode.value,
            "timeout": workflow.timeout,
            "max_retries": workflow.max_retries,
            "retry_delay": workflow.retry_delay,
            "rollback_enabled": workflow.rollback_enabled,
            "metadata": workflow.metadata,
            "conditions": workflow.conditions,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "name": task.name,
                    "handler": task.handler,
                    "parameters": task.parameters,
                    "dependencies": task.dependencies,
                    "timeout": task.timeout,
                    "retry_count": task.retry_count,
                    "retry_delay": task.retry_delay,
                    "required": task.required,
                    "conditions": task.conditions,
                    "metadata": task.metadata
                }
                for task in workflow.tasks
            ]
        }

    def import_pipeline(self, pipeline_data: Dict[str, Any]) -> WorkflowDefinition:
        """Import pipeline definition from JSON format."""
        tasks = []
        for task_data in pipeline_data["tasks"]:
            task = TaskDefinition(
                task_id=task_data["task_id"],
                name=task_data["name"],
                handler=task_data["handler"],
                parameters=task_data.get("parameters", {}),
                dependencies=task_data.get("dependencies", []),
                timeout=task_data.get("timeout"),
                retry_count=task_data.get("retry_count", 3),
                retry_delay=task_data.get("retry_delay", 5),
                required=task_data.get("required", True),
                conditions=task_data.get("conditions", {}),
                metadata=task_data.get("metadata", {})
            )
            tasks.append(task)
        
        workflow = WorkflowDefinition(
            workflow_id=pipeline_data["workflow_id"],
            name=pipeline_data["name"],
            description=pipeline_data["description"],
            tasks=tasks,
            execution_mode=ExecutionMode(pipeline_data["execution_mode"]),
            timeout=pipeline_data.get("timeout"),
            max_retries=pipeline_data.get("max_retries", 3),
            retry_delay=pipeline_data.get("retry_delay", 10),
            rollback_enabled=pipeline_data.get("rollback_enabled", True),
            metadata=pipeline_data.get("metadata", {}),
            conditions=pipeline_data.get("conditions", {})
        )
        
        return workflow
