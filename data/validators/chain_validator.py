"""
Chain Validator - Validation chain orchestrator for IA Influencer Agent Platform
================================================================================

Advanced validation chain system for orchestrating multiple validators
in sequence or parallel for comprehensive content and data validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class ChainExecutionMode(Enum):
    """Chain execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"


class ChainStepType(Enum):
    """Types of validation chain steps."""
    VALIDATOR = "validator"
    TRANSFORMER = "transformer"
    FILTER = "filter"
    AGGREGATOR = "aggregator"
    CONDITION = "condition"
    BRANCH = "branch"


class ChainStatus(Enum):
    """Chain execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


@dataclass
class ValidationStep:
    """Individual validation step in a chain."""
    step_id: str
    step_type: ChainStepType
    validator_name: str
    
    # Configuration
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: bool = True
    timeout: Optional[int] = None
    retry_count: int = 0
    
    # Conditions
    skip_condition: Optional[Callable[[Any], bool]] = None
    error_condition: Optional[Callable[[Any, Exception], bool]] = None
    
    # Execution metadata
    execution_order: int = 0
    dependencies: List[str] = field(default_factory=list)
    
    # Results
    status: ChainStatus = ChainStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class ValidationPipeline:
    """Validation pipeline configuration."""
    pipeline_id: str
    name: str
    description: str
    
    # Pipeline configuration
    steps: List[ValidationStep] = field(default_factory=list)
    execution_mode: ChainExecutionMode = ChainExecutionMode.SEQUENTIAL
    
    # Pipeline settings
    stop_on_error: bool = True
    max_parallel_steps: int = 4
    timeout: Optional[int] = None
    
    # Pipeline metadata
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)


@dataclass
class ChainResult:
    """Chain execution result."""
    chain_id: str
    pipeline_id: str
    success: bool
    status: ChainStatus
    
    # Execution results
    step_results: Dict[str, Any] = field(default_factory=dict)
    failed_steps: List[str] = field(default_factory=list)
    skipped_steps: List[str] = field(default_factory=list)
    
    # Aggregated results
    overall_score: float = 0.0
    validation_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    total_execution_time: float = 0.0
    step_execution_times: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    execution_start: float = field(default_factory=time.time)
    execution_end: Optional[float] = None
    error_summary: List[str] = field(default_factory=list)


class ValidationChain:
    """
    Validation chain execution engine.
    
    Manages the execution of validation pipelines with support for
    sequential, parallel, and conditional execution patterns.
    """
    
    def __init__(self, registry=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize validation chain.
        
        Args:
            registry: Validator registry instance
            config: Chain configuration
        """
        self.registry = registry
        self.config = config or {}
        
        # Execution state
        self.active_chains: Dict[str, ChainResult] = {}
        self.pipeline_cache: Dict[str, ValidationPipeline] = {}
        
        # Built-in pipelines
        self._init_builtin_pipelines()
        
        logger.info("ValidationChain initialized")
    
    async def execute_pipeline(
        self,
        pipeline: Union[ValidationPipeline, str],
        data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> ChainResult:
        """
        Execute validation pipeline.
        
        Args:
            pipeline: Pipeline object or pipeline ID
            data: Data to validate
            context: Execution context
            
        Returns:
            Chain execution result
        """
        chain_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Resolve pipeline
            if isinstance(pipeline, str):
                pipeline = await self._get_pipeline(pipeline)
            
            # Initialize chain result
            result = ChainResult(
                chain_id=chain_id,
                pipeline_id=pipeline.pipeline_id,
                success=False,
                status=ChainStatus.RUNNING,
                execution_start=start_time
            )
            
            self.active_chains[chain_id] = result
            
            # Execute based on mode
            if pipeline.execution_mode == ChainExecutionMode.SEQUENTIAL:
                await self._execute_sequential(pipeline, data, result, context)
            elif pipeline.execution_mode == ChainExecutionMode.PARALLEL:
                await self._execute_parallel(pipeline, data, result, context)
            elif pipeline.execution_mode == ChainExecutionMode.CONDITIONAL:
                await self._execute_conditional(pipeline, data, result, context)
            elif pipeline.execution_mode == ChainExecutionMode.PIPELINE:
                await self._execute_pipeline_mode(pipeline, data, result, context)
            
            # Finalize result
            result.execution_end = time.time()
            result.total_execution_time = result.execution_end - start_time
            result.status = ChainStatus.COMPLETED if result.success else ChainStatus.FAILED
            
            # Generate summary
            result.validation_summary = await self._generate_summary(result)
            result.overall_score = await self._calculate_overall_score(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            
            # Create error result
            error_result = ChainResult(
                chain_id=chain_id,
                pipeline_id=pipeline.pipeline_id if hasattr(pipeline, 'pipeline_id') else "unknown",
                success=False,
                status=ChainStatus.FAILED,
                execution_start=start_time,
                execution_end=time.time(),
                error_summary=[str(e)]
            )
            
            return error_result
        
        finally:
            # Cleanup
            if chain_id in self.active_chains:
                del self.active_chains[chain_id]
    
    async def execute_steps(
        self,
        steps: List[Dict[str, Any]],
        data: Any,
        execution_mode: ChainExecutionMode = ChainExecutionMode.SEQUENTIAL
    ) -> ChainResult:
        """
        Execute validation steps directly.
        
        Args:
            steps: List of step configurations
            data: Data to validate
            execution_mode: Execution mode
            
        Returns:
            Chain execution result
        """
        # Create temporary pipeline
        pipeline = ValidationPipeline(
            pipeline_id=f"temp_{int(time.time())}",
            name="Temporary Pipeline",
            description="Dynamically created pipeline",
            execution_mode=execution_mode
        )
        
        # Convert step configurations to ValidationStep objects
        for i, step_config in enumerate(steps):
            step = ValidationStep(
                step_id=step_config.get("step_id", f"step_{i}"),
                step_type=ChainStepType(step_config.get("step_type", "validator")),
                validator_name=step_config["validator_name"],
                parameters=step_config.get("parameters", {}),
                required=step_config.get("required", True),
                timeout=step_config.get("timeout"),
                execution_order=i
            )
            pipeline.steps.append(step)
        
        return await self.execute_pipeline(pipeline, data)
    
    async def create_pipeline(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        execution_mode: ChainExecutionMode = ChainExecutionMode.SEQUENTIAL,
        **kwargs
    ) -> str:
        """
        Create new validation pipeline.
        
        Args:
            name: Pipeline name
            steps: List of step configurations
            execution_mode: Execution mode
            **kwargs: Additional pipeline options
            
        Returns:
            Pipeline ID
        """
        pipeline_id = f"pipeline_{int(time.time())}_{hash(name)}"
        
        pipeline = ValidationPipeline(
            pipeline_id=pipeline_id,
            name=name,
            description=kwargs.get("description", ""),
            execution_mode=execution_mode,
            stop_on_error=kwargs.get("stop_on_error", True),
            max_parallel_steps=kwargs.get("max_parallel_steps", 4),
            timeout=kwargs.get("timeout"),
            tags=kwargs.get("tags", [])
        )
        
        # Convert step configurations
        for i, step_config in enumerate(steps):
            step = ValidationStep(
                step_id=step_config.get("step_id", f"step_{i}"),
                step_type=ChainStepType(step_config.get("step_type", "validator")),
                validator_name=step_config["validator_name"],
                parameters=step_config.get("parameters", {}),
                required=step_config.get("required", True),
                timeout=step_config.get("timeout"),
                execution_order=i,
                dependencies=step_config.get("dependencies", [])
            )
            pipeline.steps.append(step)
        
        # Cache pipeline
        self.pipeline_cache[pipeline_id] = pipeline
        
        logger.info(f"Created pipeline: {name} (ID: {pipeline_id})")
        return pipeline_id
    
    async def get_pipeline_status(self, chain_id: str) -> Optional[ChainResult]:
        """
        Get status of running chain.
        
        Args:
            chain_id: Chain ID
            
        Returns:
            Chain result or None
        """
        return self.active_chains.get(chain_id)
    
    async def cancel_chain(self, chain_id: str) -> bool:
        """
        Cancel running chain.
        
        Args:
            chain_id: Chain ID
            
        Returns:
            Success status
        """
        if chain_id in self.active_chains:
            self.active_chains[chain_id].status = ChainStatus.CANCELLED
            return True
        return False
    
    async def _execute_sequential(
        self,
        pipeline: ValidationPipeline,
        data: Any,
        result: ChainResult,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Execute pipeline steps sequentially."""
        current_data = data
        
        try:
            # Sort steps by execution order
            sorted_steps = sorted(pipeline.steps, key=lambda s: s.execution_order)
            
            for step in sorted_steps:
                # Check if chain was cancelled
                if result.status == ChainStatus.CANCELLED:
                    break
                
                # Check skip condition
                if step.skip_condition and step.skip_condition(current_data):
                    result.skipped_steps.append(step.step_id)
                    continue
                
                # Execute step
                step_result = await self._execute_step(step, current_data, context)
                result.step_results[step.step_id] = step_result
                result.step_execution_times[step.step_id] = step.execution_time
                
                # Handle step failure
                if step.status == ChainStatus.FAILED:
                    result.failed_steps.append(step.step_id)
                    if step.error:
                        result.error_summary.append(f"Step {step.step_id}: {step.error}")
                    
                    if step.required and pipeline.stop_on_error:
                        logger.warning(f"Pipeline stopped due to failed required step: {step.step_id}")
                        break
                
                # Update data for next step if step provides processed data
                if hasattr(step_result, 'processed_data'):
                    current_data = step_result.processed_data
            
            # Determine overall success
            result.success = len(result.failed_steps) == 0 or not any(
                step.required for step in pipeline.steps 
                if step.step_id in result.failed_steps
            )
            
        except Exception as e:
            logger.error(f"Sequential execution failed: {str(e)}")
            result.error_summary.append(str(e))
            result.success = False
    
    async def _execute_parallel(
        self,
        pipeline: ValidationPipeline,
        data: Any,
        result: ChainResult,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Execute pipeline steps in parallel."""
        try:
            # Group steps that can run in parallel
            parallel_groups = self._group_parallel_steps(pipeline.steps)
            
            for group in parallel_groups:
                # Check if chain was cancelled
                if result.status == ChainStatus.CANCELLED:
                    break
                
                # Execute group in parallel
                semaphore = asyncio.Semaphore(pipeline.max_parallel_steps)
                
                async def execute_step_with_semaphore(step):
                    async with semaphore:
                        return await self._execute_step(step, data, context)
                
                # Filter steps based on skip conditions
                executable_steps = [
                    step for step in group
                    if not (step.skip_condition and step.skip_condition(data))
                ]
                
                # Execute steps
                step_tasks = [
                    execute_step_with_semaphore(step)
                    for step in executable_steps
                ]
                
                step_results = await asyncio.gather(*step_tasks, return_exceptions=True)
                
                # Process results
                for step, step_result in zip(executable_steps, step_results):
                    if isinstance(step_result, Exception):
                        step.status = ChainStatus.FAILED
                        step.error = str(step_result)
                        result.failed_steps.append(step.step_id)
                        result.error_summary.append(f"Step {step.step_id}: {step.error}")
                    else:
                        result.step_results[step.step_id] = step_result
                    
                    result.step_execution_times[step.step_id] = step.execution_time
                
                # Check if we should stop on error
                if result.failed_steps and pipeline.stop_on_error:
                    failed_required = any(
                        step.required for step in executable_steps
                        if step.step_id in result.failed_steps
                    )
                    if failed_required:
                        break
            
            # Determine overall success
            result.success = len(result.failed_steps) == 0 or not any(
                step.required for step in pipeline.steps 
                if step.step_id in result.failed_steps
            )
            
        except Exception as e:
            logger.error(f"Parallel execution failed: {str(e)}")
            result.error_summary.append(str(e))
            result.success = False
    
    async def _execute_conditional(
        self,
        pipeline: ValidationPipeline,
        data: Any,
        result: ChainResult,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Execute pipeline with conditional logic."""
        try:
            current_data = data
            executed_steps = set()
            
            # Continue until no more steps can be executed
            while True:
                steps_executed_this_round = 0
                
                for step in pipeline.steps:
                    # Skip already executed steps
                    if step.step_id in executed_steps:
                        continue
                    
                    # Check dependencies
                    if not self._check_dependencies(step, executed_steps, result):
                        continue
                    
                    # Check skip condition
                    if step.skip_condition and step.skip_condition(current_data):
                        result.skipped_steps.append(step.step_id)
                        executed_steps.add(step.step_id)
                        continue
                    
                    # Execute step
                    step_result = await self._execute_step(step, current_data, context)
                    result.step_results[step.step_id] = step_result
                    result.step_execution_times[step.step_id] = step.execution_time
                    executed_steps.add(step.step_id)
                    steps_executed_this_round += 1
                    
                    # Handle step failure
                    if step.status == ChainStatus.FAILED:
                        result.failed_steps.append(step.step_id)
                        if step.error:
                            result.error_summary.append(f"Step {step.step_id}: {step.error}")
                        
                        if step.required and pipeline.stop_on_error:
                            break
                    
                    # Update data for next steps
                    if hasattr(step_result, 'processed_data'):
                        current_data = step_result.processed_data
                
                # Break if no steps were executed this round
                if steps_executed_this_round == 0:
                    break
                
                # Break if chain was cancelled or stopped on error
                if result.status == ChainStatus.CANCELLED:
                    break
            
            # Determine overall success
            result.success = len(result.failed_steps) == 0 or not any(
                step.required for step in pipeline.steps 
                if step.step_id in result.failed_steps
            )
            
        except Exception as e:
            logger.error(f"Conditional execution failed: {str(e)}")
            result.error_summary.append(str(e))
            result.success = False
    
    async def _execute_pipeline_mode(
        self,
        pipeline: ValidationPipeline,
        data: Any,
        result: ChainResult,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Execute pipeline in pipeline mode (data flows through steps)."""
        try:
            current_data = data
            
            # Sort steps by execution order
            sorted_steps = sorted(pipeline.steps, key=lambda s: s.execution_order)
            
            for step in sorted_steps:
                # Check if chain was cancelled
                if result.status == ChainStatus.CANCELLED:
                    break
                
                # Check skip condition
                if step.skip_condition and step.skip_condition(current_data):
                    result.skipped_steps.append(step.step_id)
                    continue
                
                # Execute step with current data
                step_result = await self._execute_step(step, current_data, context)
                result.step_results[step.step_id] = step_result
                result.step_execution_times[step.step_id] = step.execution_time
                
                # Handle step failure
                if step.status == ChainStatus.FAILED:
                    result.failed_steps.append(step.step_id)
                    if step.error:
                        result.error_summary.append(f"Step {step.step_id}: {step.error}")
                    
                    if step.required and pipeline.stop_on_error:
                        break
                
                # Transform data for next step
                current_data = await self._transform_data(step, step_result, current_data)
            
            # Determine overall success
            result.success = len(result.failed_steps) == 0 or not any(
                step.required for step in pipeline.steps 
                if step.step_id in result.failed_steps
            )
            
        except Exception as e:
            logger.error(f"Pipeline mode execution failed: {str(e)}")
            result.error_summary.append(str(e))
            result.success = False
    
    async def _execute_step(
        self,
        step: ValidationStep,
        data: Any,
        context: Optional[Dict[str, Any]]
    ) -> Any:
        """Execute individual validation step."""
        step.start_time = time.time()
        step.status = ChainStatus.RUNNING
        
        try:
            # Get validator from registry
            if self.registry:
                validator = await self.registry.get_validator(step.validator_name)
            else:
                raise ValueError(f"No registry available for validator: {step.validator_name}")
            
            # Prepare parameters
            params = {**step.parameters}
            if context:
                params.update(context)
            
            # Execute validation with timeout
            if step.timeout:
                step_result = await asyncio.wait_for(
                    validator.validate_async(data, **params) if hasattr(validator, 'validate_async')
                    else asyncio.get_event_loop().run_in_executor(None, validator.validate, data, **params),
                    timeout=step.timeout
                )
            else:
                if hasattr(validator, 'validate_async'):
                    step_result = await validator.validate_async(data, **params)
                else:
                    step_result = validator.validate(data, **params)
            
            step.result = step_result
            step.status = ChainStatus.COMPLETED
            
            return step_result
            
        except asyncio.TimeoutError:
            error_msg = f"Step timeout after {step.timeout} seconds"
            step.error = error_msg
            step.status = ChainStatus.FAILED
            logger.warning(f"Step {step.step_id} timed out")
            raise Exception(error_msg)
            
        except Exception as e:
            step.error = str(e)
            step.status = ChainStatus.FAILED
            logger.error(f"Step {step.step_id} failed: {str(e)}")
            raise
            
        finally:
            step.end_time = time.time()
            step.execution_time = step.end_time - (step.start_time or 0)
    
    async def _transform_data(self, step: ValidationStep, step_result: Any, original_data: Any) -> Any:
        """Transform data based on step result."""
        try:
            # Check if step result has processed data
            if hasattr(step_result, 'processed_data'):
                return step_result.processed_data
            
            # Check if step is a transformer
            if step.step_type == ChainStepType.TRANSFORMER:
                # Apply transformation logic
                if hasattr(step_result, 'transform'):
                    return step_result.transform(original_data)
            
            # Default: return original data
            return original_data
            
        except Exception as e:
            logger.warning(f"Data transformation failed for step {step.step_id}: {str(e)}")
            return original_data
    
    def _group_parallel_steps(self, steps: List[ValidationStep]) -> List[List[ValidationStep]]:
        """Group steps that can be executed in parallel."""
        groups = []
        remaining_steps = steps.copy()
        
        while remaining_steps:
            current_group = []
            steps_to_remove = []
            
            for step in remaining_steps:
                # Check if step has dependencies that haven't been processed
                if not step.dependencies:
                    current_group.append(step)
                    steps_to_remove.append(step)
                else:
                    # Check if all dependencies are in previous groups
                    processed_steps = {s.step_id for group in groups for s in group}
                    if all(dep in processed_steps for dep in step.dependencies):
                        current_group.append(step)
                        steps_to_remove.append(step)
            
            # Remove processed steps
            for step in steps_to_remove:
                remaining_steps.remove(step)
            
            # Add group if not empty
            if current_group:
                groups.append(current_group)
            else:
                # Break infinite loop if no progress
                break
        
        return groups
    
    def _check_dependencies(
        self,
        step: ValidationStep,
        executed_steps: set,
        result: ChainResult
    ) -> bool:
        """Check if step dependencies are satisfied."""
        if not step.dependencies:
            return True
        
        for dependency in step.dependencies:
            if dependency not in executed_steps:
                return False
            
            # Check if dependency step failed and is required
            if dependency in result.failed_steps:
                dependency_step = next(
                    (s for s in result.step_results.keys() if s == dependency),
                    None
                )
                if dependency_step and dependency in result.failed_steps:
                    return False
        
        return True
    
    async def _get_pipeline(self, pipeline_id: str) -> ValidationPipeline:
        """Get pipeline by ID."""
        if pipeline_id in self.pipeline_cache:
            return self.pipeline_cache[pipeline_id]
        
        # Try to load from built-in pipelines
        if pipeline_id in self.builtin_pipelines:
            return self.builtin_pipelines[pipeline_id]
        
        raise ValueError(f"Pipeline not found: {pipeline_id}")
    
    async def _generate_summary(self, result: ChainResult) -> Dict[str, Any]:
        """Generate validation summary."""
        try:
            total_steps = len(result.step_results) + len(result.failed_steps) + len(result.skipped_steps)
            successful_steps = len(result.step_results) - len(result.failed_steps)
            
            return {
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "failed_steps": len(result.failed_steps),
                "skipped_steps": len(result.skipped_steps),
                "success_rate": successful_steps / total_steps if total_steps > 0 else 0,
                "avg_execution_time": sum(result.step_execution_times.values()) / len(result.step_execution_times) if result.step_execution_times else 0,
                "errors": result.error_summary
            }
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return {}
    
    async def _calculate_overall_score(self, result: ChainResult) -> float:
        """Calculate overall validation score."""
        try:
            if not result.step_results:
                return 0.0
            
            scores = []
            
            for step_id, step_result in result.step_results.items():
                # Extract score from step result
                if hasattr(step_result, 'overall_score'):
                    scores.append(step_result.overall_score)
                elif hasattr(step_result, 'score'):
                    scores.append(step_result.score)
                elif hasattr(step_result, 'is_valid') and step_result.is_valid:
                    scores.append(100.0)
                else:
                    scores.append(0.0)
            
            # Calculate weighted average
            if scores:
                return sum(scores) / len(scores)
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"Score calculation failed: {str(e)}")
            return 0.0
    
    def _init_builtin_pipelines(self) -> None:
        """Initialize built-in validation pipelines."""
        self.builtin_pipelines = {}
        
        # Content validation pipeline
        content_pipeline = ValidationPipeline(
            pipeline_id="content_validation",
            name="Content Validation Pipeline",
            description="Comprehensive content validation for creator uploads",
            execution_mode=ChainExecutionMode.SEQUENTIAL
        )
        
        content_pipeline.steps = [
            ValidationStep(
                step_id="file_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="file",
                parameters={"check_integrity": True},
                execution_order=0
            ),
            ValidationStep(
                step_id="security_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="security",
                parameters={"scan_malware": True},
                execution_order=1
            ),
            ValidationStep(
                step_id="content_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="content",
                parameters={"validation_level": "standard"},
                execution_order=2
            ),
            ValidationStep(
                step_id="quality_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="quality",
                parameters={"min_score": 70},
                execution_order=3,
                required=False
            )
        ]
        
        self.builtin_pipelines["content_validation"] = content_pipeline
        
        # Creator onboarding pipeline
        onboarding_pipeline = ValidationPipeline(
            pipeline_id="creator_onboarding",
            name="Creator Onboarding Pipeline", 
            description="Validation pipeline for new creator registration",
            execution_mode=ChainExecutionMode.CONDITIONAL
        )
        
        onboarding_pipeline.steps = [
            ValidationStep(
                step_id="schema_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="schema",
                parameters={"schema_type": "creator_profile"},
                execution_order=0
            ),
            ValidationStep(
                step_id="business_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="business",
                parameters={"check_eligibility": True},
                execution_order=1
            ),
            ValidationStep(
                step_id="compliance_validation",
                step_type=ChainStepType.VALIDATOR,
                validator_name="compliance",
                parameters={"check_legal_requirements": True},
                execution_order=2
            )
        ]
        
        self.builtin_pipelines["creator_onboarding"] = onboarding_pipeline
        
        # Performance monitoring pipeline
        performance_pipeline = ValidationPipeline(
            pipeline_id="performance_monitoring",
            name="Performance Monitoring Pipeline",
            description="Continuous performance validation and monitoring",
            execution_mode=ChainExecutionMode.PARALLEL
        )
        
        performance_pipeline.steps = [
            ValidationStep(
                step_id="system_performance",
                step_type=ChainStepType.VALIDATOR,
                validator_name="performance",
                parameters={"operation_type": "system_monitoring"},
                execution_order=0,
                required=False
            ),
            ValidationStep(
                step_id="content_performance",
                step_type=ChainStepType.VALIDATOR,
                validator_name="performance",
                parameters={"operation_type": "content_processing"},
                execution_order=0,
                required=False
            )
        ]
        
        self.builtin_pipelines["performance_monitoring"] = performance_pipeline


class ChainValidator:
    """
    Main chain validator for the IA Influencer Agent Platform.
    
    Provides unified interface for executing validation chains and pipelines
    with support for complex validation workflows.
    """
    
    def __init__(self, registry=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize chain validator.
        
        Args:
            registry: Validator registry instance
            config: Validation configuration
        """
        self.config = config or {}
        self.chain = ValidationChain(registry, config)
        
        logger.info("ChainValidator initialized")
    
    async def validate_async(self, data: Any, **options) -> ChainResult:
        """
        Async validation interface.
        
        Args:
            data: Data to validate
            **options: Validation options
            
        Returns:
            Chain validation result
        """
        # Extract pipeline configuration
        pipeline_id = options.get("pipeline_id")
        steps = options.get("steps")
        execution_mode = ChainExecutionMode(options.get("execution_mode", "sequential"))
        
        if pipeline_id:
            # Execute existing pipeline
            return await self.chain.execute_pipeline(pipeline_id, data)
        elif steps:
            # Execute custom steps
            return await self.chain.execute_steps(steps, data, execution_mode)
        else:
            # Execute default content validation pipeline
            return await self.chain.execute_pipeline("content_validation", data)
    
    def validate(self, data: Any, **options) -> ChainResult:
        """
        Sync validation interface.
        
        Args:
            data: Data to validate
            **options: Validation options
            
        Returns:
            Chain validation result
        """
        # Run async validation in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.validate_async(data, **options))
            return result
        finally:
            loop.close()
    
    async def create_pipeline(
        self,
        name: str,
        steps: List[Dict[str, Any]],
        **kwargs
    ) -> str:
        """Create new validation pipeline."""
        return await self.chain.create_pipeline(name, steps, **kwargs)
    
    def get_builtin_pipelines(self) -> List[str]:
        """Get list of built-in pipelines."""
        return list(self.chain.builtin_pipelines.keys())
    
    async def get_pipeline_info(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get pipeline information."""
        try:
            pipeline = await self.chain._get_pipeline(pipeline_id)
            return {
                "pipeline_id": pipeline.pipeline_id,
                "name": pipeline.name,
                "description": pipeline.description,
                "execution_mode": pipeline.execution_mode.value,
                "steps": len(pipeline.steps),
                "version": pipeline.version,
                "tags": pipeline.tags
            }
        except Exception:
            return None
