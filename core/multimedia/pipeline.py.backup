"""Multimedia Pipeline - Enterprise Processing Pipeline Engine

Advanced pipeline system for orchestrating multimedia processing workflows.
Provides flexible, configurable processing chains with error handling and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
import traceback

from .registry import MultimediaRegistry, MultimediaComponent
from ..events.dispatcher import EventDispatcher
from ..monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class PipelineStepType(Enum):
    """Pipeline step types"""
    PROCESSOR = "processor"
    VALIDATOR = "validator"
    TRANSFORMER = "transformer"
    ANALYZER = "analyzer"
    ENHANCER = "enhancer"
    CONVERTER = "converter"
    FILTER = "filter"
    AGGREGATOR = "aggregator"
    ROUTER = "router"
    CONDITIONAL = "conditional"


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ExecutionMode(Enum):
    """Pipeline execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    DYNAMIC = "dynamic"


@dataclass
class PipelineStep:
    """Pipeline step definition"""
    step_id: str
    name: str
    description: str
    step_type: PipelineStepType
    component_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    required: bool = True
    parallel_group: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    error_handling: str = "fail"  # fail, skip, retry, fallback
    fallback_step: Optional[str] = None
    enabled: bool = True


@dataclass
class PipelineDefinition:
    """Complete pipeline definition"""
    pipeline_id: str
    name: str
    description: str
    version: str
    steps: List[PipelineStep]
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    max_parallel_steps: int = 5
    global_timeout: int = 3600
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    error_handling_strategy: str = "fail_fast"
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    enabled: bool = True


@dataclass
class PipelineContext:
    """Pipeline execution context"""
    execution_id: str
    pipeline_id: str
    user_id: str
    input_data: Dict[str, Any]
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: PipelineStatus = PipelineStatus.PENDING
    current_step: Optional[str] = None
    progress: float = 0.0
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class StepExecutionResult:
    """Step execution result"""
    step_id: str
    status: PipelineStatus
    output_data: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    error_details: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class MultimediaPipeline:
    """Enterprise multimedia processing pipeline"""
    
    def __init__(
        self, 
        config: Dict[str, Any],
        registry: Optional[MultimediaRegistry] = None,
        event_dispatcher: Optional[EventDispatcher] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.config = config
        self.registry = registry or MultimediaRegistry(config.get("registry", {}))
        self.event_dispatcher = event_dispatcher or EventDispatcher()
        self.metrics = metrics_collector or MetricsCollector()
        
        # Pipeline storage
        self.pipeline_definitions: Dict[str, PipelineDefinition] = {}
        self.active_executions: Dict[str, PipelineContext] = {}
        
        # Configuration
        self.max_concurrent_executions = config.get("max_concurrent_executions", 50)
        self.default_timeout = config.get("default_timeout", 3600)
        self.enable_step_caching = config.get("enable_step_caching", True)
        self.enable_parallel_execution = config.get("enable_parallel_execution", True)
        
        # Performance tracking
        self.pipeline_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "pipeline_usage": {},
            "step_performance": {}
        }
        
        self._setup_event_handlers()
        
    async def initialize(self):
        """Initialize pipeline engine"""
        try:
            await self.registry.initialize()
            await self._load_default_pipelines()
            
            logger.info("Multimedia pipeline engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline engine: {e}")
            raise
            
    async def register_pipeline(self, pipeline_def: PipelineDefinition) -> bool:
        """Register new pipeline definition"""
        try:
            # Validate pipeline
            validation_result = await self._validate_pipeline(pipeline_def)
            if not validation_result["valid"]:
                logger.error(f"Pipeline validation failed: {validation_result['errors']}")
                return False
                
            # Store pipeline
            self.pipeline_definitions[pipeline_def.pipeline_id] = pipeline_def
            
            # Initialize pipeline usage stats
            self.pipeline_stats["pipeline_usage"][pipeline_def.pipeline_id] = {
                "executions": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0
            }
            
            logger.info(f"Pipeline registered: {pipeline_def.pipeline_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register pipeline: {e}")
            return False
            
    async def execute_pipeline(
        self, 
        pipeline_id: str,
        input_data: Dict[str, Any],
        user_id: str,
        parameters: Dict[str, Any] = None,
        execution_options: Dict[str, Any] = None
    ) -> PipelineContext:
        """Execute pipeline"""
        execution_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get pipeline definition
            pipeline_def = self.pipeline_definitions.get(pipeline_id)
            if not pipeline_def or not pipeline_def.enabled:
                raise ValueError(f"Pipeline not found or disabled: {pipeline_id}")
                
            # Create execution context
            context = PipelineContext(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                user_id=user_id,
                input_data=input_data,
                parameters=parameters or {},
                metadata=execution_options or {}
            )
            
            # Store active execution
            self.active_executions[execution_id] = context
            
            # Start execution
            context.status = PipelineStatus.RUNNING
            context.started_at = start_time
            
            # Fire start event
            await self.event_dispatcher.emit("pipeline_started", {
                "execution_id": execution_id,
                "pipeline_id": pipeline_id,
                "user_id": user_id
            })
            
            # Execute pipeline steps
            await self._execute_pipeline_steps(pipeline_def, context)
            
            # Complete execution
            context.status = PipelineStatus.COMPLETED
            context.completed_at = datetime.now(timezone.utc)
            context.progress = 100.0
            
            # Fire completion event
            await self.event_dispatcher.emit("pipeline_completed", {
                "execution_id": execution_id,
                "pipeline_id": pipeline_id,
                "user_id": user_id,
                "execution_time": (context.completed_at - context.started_at).total_seconds()
            })
            
            # Update statistics
            execution_time = (context.completed_at - context.started_at).total_seconds()
            await self._update_pipeline_stats(pipeline_id, execution_time, True)
            
            logger.info(f"Pipeline executed successfully: {execution_id}")
            return context
            
        except Exception as e:
            # Handle execution failure
            context = self.active_executions.get(execution_id)
            if context:
                context.status = PipelineStatus.FAILED
                context.completed_at = datetime.now(timezone.utc)
                context.error_details = {
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
            # Fire failure event
            await self.event_dispatcher.emit("pipeline_failed", {
                "execution_id": execution_id,
                "pipeline_id": pipeline_id,
                "user_id": user_id,
                "error": str(e)
            })
            
            # Update statistics
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            await self._update_pipeline_stats(pipeline_id, execution_time, False)
            
            logger.error(f"Pipeline execution failed: {execution_id} - {e}")
            
            if not context:
                context = PipelineContext(
                    execution_id=execution_id,
                    pipeline_id=pipeline_id,
                    user_id=user_id,
                    input_data=input_data,
                    status=PipelineStatus.FAILED,
                    error_details={"error": str(e)}
                )
                
            return context
            
        finally:
            # Cleanup
            if execution_id in self.active_executions:
                # Keep execution for a while for status queries
                pass
                
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline execution status"""
        context = self.active_executions.get(execution_id)
        if not context:
            return None
            
        return {
            "execution_id": execution_id,
            "pipeline_id": context.pipeline_id,
            "status": context.status.value,
            "progress": context.progress,
            "current_step": context.current_step,
            "started_at": context.started_at.isoformat() if context.started_at else None,
            "completed_at": context.completed_at.isoformat() if context.completed_at else None,
            "error_details": context.error_details,
            "step_results": context.step_results
        }
        
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel pipeline execution"""
        try:
            context = self.active_executions.get(execution_id)
            if not context or context.status not in [PipelineStatus.PENDING, PipelineStatus.RUNNING]:
                return False
                
            context.status = PipelineStatus.CANCELLED
            context.completed_at = datetime.now(timezone.utc)
            
            # Fire cancellation event
            await self.event_dispatcher.emit("pipeline_cancelled", {
                "execution_id": execution_id,
                "pipeline_id": context.pipeline_id,
                "user_id": context.user_id
            })
            
            logger.info(f"Pipeline execution cancelled: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel execution {execution_id}: {e}")
            return False
            
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause pipeline execution"""
        try:
            context = self.active_executions.get(execution_id)
            if not context or context.status != PipelineStatus.RUNNING:
                return False
                
            context.status = PipelineStatus.PAUSED
            
            # Fire pause event
            await self.event_dispatcher.emit("pipeline_paused", {
                "execution_id": execution_id,
                "pipeline_id": context.pipeline_id,
                "user_id": context.user_id
            })
            
            logger.info(f"Pipeline execution paused: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause execution {execution_id}: {e}")
            return False
            
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume paused pipeline execution"""
        try:
            context = self.active_executions.get(execution_id)
            if not context or context.status != PipelineStatus.PAUSED:
                return False
                
            context.status = PipelineStatus.RUNNING
            
            # Fire resume event
            await self.event_dispatcher.emit("pipeline_resumed", {
                "execution_id": execution_id,
                "pipeline_id": context.pipeline_id,
                "user_id": context.user_id
            })
            
            logger.info(f"Pipeline execution resumed: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume execution {execution_id}: {e}")
            return False
            
    def list_pipelines(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """List available pipelines"""
        pipelines = []
        
        for pipeline_id, pipeline_def in self.pipeline_definitions.items():
            if enabled_only and not pipeline_def.enabled:
                continue
                
            pipelines.append({
                "pipeline_id": pipeline_id,
                "name": pipeline_def.name,
                "description": pipeline_def.description,
                "version": pipeline_def.version,
                "steps_count": len(pipeline_def.steps),
                "execution_mode": pipeline_def.execution_mode.value,
                "enabled": pipeline_def.enabled,
                "created_at": pipeline_def.created_at.isoformat()
            })
            
        return pipelines
        
    async def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            **self.pipeline_stats,
            "active_executions": len(self.active_executions),
            "registered_pipelines": len(self.pipeline_definitions),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    async def health_check(self) -> Dict[str, Any]:
        """Pipeline engine health check"""
        try:
            # Check registry health
            registry_health = await self.registry.health_check()
            
            # Check active executions
            running_executions = len([
                ctx for ctx in self.active_executions.values()
                if ctx.status == PipelineStatus.RUNNING
            ])
            
            # Check pipeline definitions
            enabled_pipelines = len([
                p for p in self.pipeline_definitions.values()
                if p.enabled
            ])
            
            status = "healthy"
            if registry_health.get("status") != "healthy":
                status = "degraded"
                
            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "registry_health": registry_health,
                "running_executions": running_executions,
                "enabled_pipelines": enabled_pipelines,
                "pipeline_stats": self.pipeline_stats
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    # Private methods
    
    async def _execute_pipeline_steps(self, pipeline_def: PipelineDefinition, context: PipelineContext):
        """Execute pipeline steps"""
        try:
            if pipeline_def.execution_mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential_steps(pipeline_def, context)
            elif pipeline_def.execution_mode == ExecutionMode.PARALLEL:
                await self._execute_parallel_steps(pipeline_def, context)
            elif pipeline_def.execution_mode == ExecutionMode.CONDITIONAL:
                await self._execute_conditional_steps(pipeline_def, context)
            elif pipeline_def.execution_mode == ExecutionMode.DYNAMIC:
                await self._execute_dynamic_steps(pipeline_def, context)
            else:
                raise ValueError(f"Unsupported execution mode: {pipeline_def.execution_mode}")
                
        except Exception as e:
            logger.error(f"Pipeline step execution failed: {e}")
            raise
            
    async def _execute_sequential_steps(self, pipeline_def: PipelineDefinition, context: PipelineContext):
        """Execute steps sequentially"""
        total_steps = len(pipeline_def.steps)
        
        for i, step in enumerate(pipeline_def.steps):
            if not step.enabled:
                continue
                
            if context.status == PipelineStatus.CANCELLED:
                break
                
            while context.status == PipelineStatus.PAUSED:
                await asyncio.sleep(1)
                
            # Update progress
            context.current_step = step.step_id
            context.progress = (i / total_steps) * 100
            
            # Execute step
            step_result = await self._execute_step(step, context)
            context.step_results[step.step_id] = step_result
            
            # Handle step result
            if step_result.status == PipelineStatus.FAILED:
                if step.error_handling == "fail":
                    raise RuntimeError(f"Step failed: {step.step_id} - {step_result.error_details}")
                elif step.error_handling == "skip":
                    logger.warning(f"Step skipped due to error: {step.step_id}")
                    continue
                elif step.error_handling == "fallback" and step.fallback_step:
                    # Execute fallback step
                    fallback_step = next((s for s in pipeline_def.steps if s.step_id == step.fallback_step), None)
                    if fallback_step:
                        step_result = await self._execute_step(fallback_step, context)
                        context.step_results[f"{step.step_id}_fallback"] = step_result
                        
    async def _execute_parallel_steps(self, pipeline_def: PipelineDefinition, context: PipelineContext):
        """Execute steps in parallel where possible"""
        # Group steps by dependencies
        step_groups = self._group_steps_by_dependencies(pipeline_def.steps)
        
        for group in step_groups:
            if context.status == PipelineStatus.CANCELLED:
                break
                
            # Execute group in parallel
            tasks = []
            for step in group:
                if step.enabled:
                    task = asyncio.create_task(self._execute_step(step, context))
                    tasks.append((step.step_id, task))
                    
            # Wait for all tasks in group
            for step_id, task in tasks:
                try:
                    step_result = await task
                    context.step_results[step_id] = step_result
                except Exception as e:
                    context.step_results[step_id] = StepExecutionResult(
                        step_id=step_id,
                        status=PipelineStatus.FAILED,
                        error_details=str(e)
                    )
                    
    async def _execute_conditional_steps(self, pipeline_def: PipelineDefinition, context: PipelineContext):
        """Execute steps based on conditions"""
        for step in pipeline_def.steps:
            if not step.enabled:
                continue
                
            # Check conditions
            if step.conditions and not self._evaluate_conditions(step.conditions, context):
                context.step_results[step.step_id] = StepExecutionResult(
                    step_id=step.step_id,
                    status=PipelineStatus.SKIPPED
                )
                continue
                
            # Execute step
            step_result = await self._execute_step(step, context)
            context.step_results[step.step_id] = step_result
            
    async def _execute_dynamic_steps(self, pipeline_def: PipelineDefinition, context: PipelineContext):
        """Execute steps dynamically based on runtime conditions"""
        # This is a simplified implementation
        # In practice, this would involve more complex routing logic
        await self._execute_sequential_steps(pipeline_def, context)
        
    async def _execute_step(self, step: PipelineStep, context: PipelineContext) -> StepExecutionResult:
        """Execute individual pipeline step"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get component from registry
            component = await self.registry.get_component(step.component_id)
            if not component:
                raise ValueError(f"Component not found: {step.component_id}")
                
            # Prepare input data
            input_data = self._prepare_step_input(step, context)
            
            # Merge parameters
            step_parameters = {**step.parameters}
            step_parameters.update(context.parameters.get(step.step_id, {}))
            
            # Fire step start event
            await self.event_dispatcher.emit("step_started", {
                "execution_id": context.execution_id,
                "step_id": step.step_id,
                "component_id": step.component_id
            })
            
            # Execute component
            output_data = await asyncio.wait_for(
                component.process(input_data, step_parameters),
                timeout=step.timeout_seconds
            )
            
            # Process output
            processed_output = self._process_step_output(step, output_data, context)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Fire step completion event
            await self.event_dispatcher.emit("step_completed", {
                "execution_id": context.execution_id,
                "step_id": step.step_id,
                "processing_time": processing_time
            })
            
            return StepExecutionResult(
                step_id=step.step_id,
                status=PipelineStatus.COMPLETED,
                output_data=processed_output,
                processing_time=processing_time,
                started_at=start_time,
                completed_at=datetime.now(timezone.utc)
            )
            
        except asyncio.TimeoutError:
            error_msg = f"Step timeout: {step.step_id}"
            logger.error(error_msg)
            
            await self.event_dispatcher.emit("step_failed", {
                "execution_id": context.execution_id,
                "step_id": step.step_id,
                "error": error_msg
            })
            
            return StepExecutionResult(
                step_id=step.step_id,
                status=PipelineStatus.FAILED,
                error_details=error_msg,
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                started_at=start_time,
                completed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Step execution failed: {step.step_id} - {error_msg}")
            
            await self.event_dispatcher.emit("step_failed", {
                "execution_id": context.execution_id,
                "step_id": step.step_id,
                "error": error_msg
            })
            
            return StepExecutionResult(
                step_id=step.step_id,
                status=PipelineStatus.FAILED,
                error_details=error_msg,
                processing_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                started_at=start_time,
                completed_at=datetime.now(timezone.utc)
            )
            
    def _prepare_step_input(self, step: PipelineStep, context: PipelineContext) -> Dict[str, Any]:
        """Prepare input data for step execution"""
        input_data = {}
        
        # Map inputs from context
        for target_key, source_key in step.input_mapping.items():
            if source_key.startswith("input."):
                # From initial input
                key_path = source_key[6:]  # Remove "input."
                input_data[target_key] = self._get_nested_value(context.input_data, key_path)
            elif source_key.startswith("step."):
                # From step result
                parts = source_key.split(".", 2)
                if len(parts) >= 3:
                    step_id = parts[1]
                    result_key = parts[2]
                    if step_id in context.step_results:
                        step_result = context.step_results[step_id]
                        input_data[target_key] = self._get_nested_value(step_result.output_data, result_key)
            elif source_key.startswith("shared."):
                # From shared state
                key_path = source_key[7:]  # Remove "shared."
                input_data[target_key] = self._get_nested_value(context.shared_state, key_path)
                
        # If no input mapping, use context input data
        if not input_data and not step.input_mapping:
            input_data = context.input_data
            
        return input_data
        
    def _process_step_output(self, step: PipelineStep, output_data: Dict[str, Any], context: PipelineContext) -> Dict[str, Any]:
        """Process step output and update context"""
        processed_output = output_data
        
        # Apply output mapping
        if step.output_mapping:
            mapped_output = {}
            for source_key, target_key in step.output_mapping.items():
                if source_key in output_data:
                    if target_key.startswith("shared."):
                        # Store in shared state
                        key_path = target_key[7:]  # Remove "shared."
                        self._set_nested_value(context.shared_state, key_path, output_data[source_key])
                    else:
                        mapped_output[target_key] = output_data[source_key]
                        
            processed_output = mapped_output
            
        return processed_output
        
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = key_path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
                
        return current
        
    def _set_nested_value(self, data: Dict[str, Any], key_path: str, value: Any):
        """Set nested value in dictionary using dot notation"""
        keys = key_path.split(".")
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    def _group_steps_by_dependencies(self, steps: List[PipelineStep]) -> List[List[PipelineStep]]:
        """Group steps by their dependencies for parallel execution"""
        groups = []
        remaining_steps = steps.copy()
        completed_steps = set()
        
        while remaining_steps:
            current_group = []
            
            for step in remaining_steps[:]:
                # Check if all dependencies are completed
                if all(dep in completed_steps for dep in step.dependencies):
                    current_group.append(step)
                    remaining_steps.remove(step)
                    
            if not current_group and remaining_steps:
                # Handle circular dependencies by taking first step
                current_group.append(remaining_steps.pop(0))
                
            groups.append(current_group)
            completed_steps.update(step.step_id for step in current_group)
            
        return groups
        
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: PipelineContext) -> bool:
        """Evaluate step conditions"""
        # This is a simplified implementation
        # In practice, you would implement a more sophisticated condition evaluator
        
        for condition_type, condition_value in conditions.items():
            if condition_type == "step_status":
                step_id = condition_value.get("step_id")
                expected_status = condition_value.get("status")
                
                if step_id in context.step_results:
                    actual_status = context.step_results[step_id].status
                    if actual_status.value != expected_status:
                        return False
                else:
                    return False
                    
            elif condition_type == "output_exists":
                step_id = condition_value.get("step_id")
                output_key = condition_value.get("key")
                
                if step_id in context.step_results:
                    output_data = context.step_results[step_id].output_data
                    if output_key not in output_data:
                        return False
                else:
                    return False
                    
        return True
        
    async def _validate_pipeline(self, pipeline_def: PipelineDefinition) -> Dict[str, Any]:
        """Validate pipeline definition"""
        errors = []
        
        # Basic validation
        if not pipeline_def.pipeline_id:
            errors.append("Pipeline ID is required")
            
        if not pipeline_def.name:
            errors.append("Pipeline name is required")
            
        if not pipeline_def.steps:
            errors.append("Pipeline must have at least one step")
            
        # Validate steps
        step_ids = set()
        for step in pipeline_def.steps:
            if not step.step_id:
                errors.append("Step ID is required")
            elif step.step_id in step_ids:
                errors.append(f"Duplicate step ID: {step.step_id}")
            else:
                step_ids.add(step.step_id)
                
            if not step.component_id:
                errors.append(f"Component ID required for step: {step.step_id}")
                
            # Check if component exists
            component = await self.registry.get_component(step.component_id)
            if not component:
                errors.append(f"Component not found: {step.component_id}")
                
        # Validate dependencies
        for step in pipeline_def.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    errors.append(f"Invalid dependency {dep} for step {step.step_id}")
                    
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
        
    async def _load_default_pipelines(self):
        """Load default pipeline definitions"""
        # This would typically load from configuration files or database
        # For now, we'll create some basic default pipelines
        
        default_pipelines = [
            PipelineDefinition(
                pipeline_id="basic_multimedia_processing",
                name="Basic Multimedia Processing",
                description="Basic multimedia file processing pipeline",
                version="1.0.0",
                steps=[
                    PipelineStep(
                        step_id="validate",
                        name="Validate Input",
                        description="Validate input file",
                        step_type=PipelineStepType.VALIDATOR,
                        component_id="multimedia_validator"
                    ),
                    PipelineStep(
                        step_id="analyze",
                        name="Analyze Content",
                        description="Analyze multimedia content",
                        step_type=PipelineStepType.ANALYZER,
                        component_id="multimedia_analyzer"
                    ),
                    PipelineStep(
                        step_id="enhance",
                        name="Enhance Quality",
                        description="Enhance content quality",
                        step_type=PipelineStepType.ENHANCER,
                        component_id="multimedia_enhancer"
                    )
                ]
            )
        ]
        
        for pipeline_def in default_pipelines:
            await self.register_pipeline(pipeline_def)
            
    def _setup_event_handlers(self):
        """Setup event handlers"""
        self.event_dispatcher.subscribe("pipeline_started", self._handle_pipeline_started)
        self.event_dispatcher.subscribe("pipeline_completed", self._handle_pipeline_completed)
        self.event_dispatcher.subscribe("pipeline_failed", self._handle_pipeline_failed)
        self.event_dispatcher.subscribe("step_started", self._handle_step_started)
        self.event_dispatcher.subscribe("step_completed", self._handle_step_completed)
        self.event_dispatcher.subscribe("step_failed", self._handle_step_failed)
        
    async def _update_pipeline_stats(self, pipeline_id: str, execution_time: float, success: bool):
        """Update pipeline statistics"""
        self.pipeline_stats["total_executions"] += 1
        
        if success:
            self.pipeline_stats["successful_executions"] += 1
        else:
            self.pipeline_stats["failed_executions"] += 1
            
        # Update average execution time
        total_time = (
            self.pipeline_stats["average_execution_time"] * (self.pipeline_stats["total_executions"] - 1) +
            execution_time
        )
        self.pipeline_stats["average_execution_time"] = total_time / self.pipeline_stats["total_executions"]
        
        # Update pipeline-specific stats
        if pipeline_id not in self.pipeline_stats["pipeline_usage"]:
            self.pipeline_stats["pipeline_usage"][pipeline_id] = {
                "executions": 0,
                "successful_executions": 0,
                "total_time": 0.0,
                "avg_execution_time": 0.0,
                "success_rate": 0.0
            }
            
        pipeline_stats = self.pipeline_stats["pipeline_usage"][pipeline_id]
        pipeline_stats["executions"] += 1
        pipeline_stats["total_time"] += execution_time
        pipeline_stats["avg_execution_time"] = pipeline_stats["total_time"] / pipeline_stats["executions"]
        
        if success:
            pipeline_stats["successful_executions"] += 1
            
        pipeline_stats["success_rate"] = pipeline_stats["successful_executions"] / pipeline_stats["executions"]
        
    # Event handlers
    
    async def _handle_pipeline_started(self, event_data: Dict[str, Any]):
        """Handle pipeline started event"""
        logger.info(f"Pipeline started: {event_data['execution_id']}")
        
    async def _handle_pipeline_completed(self, event_data: Dict[str, Any]):
        """Handle pipeline completed event"""
        logger.info(f"Pipeline completed: {event_data['execution_id']}")
        
    async def _handle_pipeline_failed(self, event_data: Dict[str, Any]):
        """Handle pipeline failed event"""
        logger.error(f"Pipeline failed: {event_data['execution_id']} - {event_data.get('error')}")
        
    async def _handle_step_started(self, event_data: Dict[str, Any]):
        """Handle step started event"""
        logger.debug(f"Step started: {event_data['step_id']}")
        
    async def _handle_step_completed(self, event_data: Dict[str, Any]):
        """Handle step completed event"""
        logger.debug(f"Step completed: {event_data['step_id']}")
        
    async def _handle_step_failed(self, event_data: Dict[str, Any]):
        """Handle step failed event"""
        logger.warning(f"Step failed: {event_data['step_id']} - {event_data.get('error')}")
