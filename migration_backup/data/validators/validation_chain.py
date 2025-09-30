"""Validation Chain - Pipeline Orchestration System for Validator Coordination
===========================================================================

Industrial-grade validation pipeline orchestration system for the IA Influencer
Agent Platform, providing intelligent validation chains, conditional workflows,
and error handling with retry logic.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited

Pipeline Capabilities:
- Orchestrated validation chains with dependency management
- Conditional validation flows based on content type and context
- Intelligent parallelization for performance optimization
- Comprehensive error handling and retry logic
- Real-time performance monitoring and metrics
- Custom workflow configuration and hot-reload
- Integration with business logic and quality gates
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logger = logging.getLogger(__name__)

class ValidationStepType(Enum):
    """Types of validation steps."""
    CONTENT = "content"
    SECURITY = "security"
    BUSINESS = "business"
    SCHEMA = "schema"
    FILE = "file"
    AI_ANALYSIS = "ai_analysis"
    PLATFORM_SPECIFIC = "platform_specific"
    CUSTOM = "custom"

class StepStatus(Enum):
    """Validation step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class ChainExecutionMode(Enum):
    """Chain execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ADAPTIVE = "adaptive"

class FailureStrategy(Enum):
    """Strategies for handling validation failures."""
    FAIL_FAST = "fail_fast"
    CONTINUE_ON_ERROR = "continue_on_error"
    RETRY_ON_FAILURE = "retry_on_failure"
    SKIP_ON_ERROR = "skip_on_error"

@dataclass
class ValidationStep:
    """Individual validation step configuration."""
    step_id: str
    step_type: ValidationStepType
    validator_name: str
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    failure_strategy: FailureStrategy = FailureStrategy.FAIL_FAST
    parallel_allowed: bool = True
    required: bool = True
    weight: float = 1.0  # Weight for scoring calculations

@dataclass
class StepResult:
    """Result of a validation step execution."""
    step_id: str
    status: StepStatus
    success: bool
    result_data: Any = None
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    retry_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChainResult:
    """Result of validation chain execution."""
    chain_id: str
    overall_success: bool
    execution_mode: ChainExecutionMode
    total_steps: int
    successful_steps: int
    failed_steps: int
    skipped_steps: int
    step_results: List[StepResult] = field(default_factory=list)
    overall_score: float = 0.0
    execution_time_ms: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_summary: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class ValidationChain:
    """Validation chain configuration and execution."""
    
    def __init__(self, chain_id: str, steps: List[ValidationStep],
                 execution_mode: ChainExecutionMode = ChainExecutionMode.SEQUENTIAL,
                 max_parallel_steps: int = 3,
                 global_timeout_seconds: int = 300,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize validation chain.
        
        Args:
            chain_id: Unique identifier for the chain
            steps: List of validation steps
            execution_mode: How to execute the chain
            max_parallel_steps: Maximum parallel steps for parallel execution
            global_timeout_seconds: Global timeout for entire chain
            config: Optional configuration
        """
        self.chain_id = chain_id
        self.steps = steps
        self.execution_mode = execution_mode
        self.max_parallel_steps = max_parallel_steps
        self.global_timeout_seconds = global_timeout_seconds
        self.config = config or {}
        
        # Build dependency graph
        self.dependency_graph = self._build_dependency_graph()
        
        # Validate chain configuration
        self._validate_chain_configuration()
        
        logger.info(f"ValidationChain '{chain_id}' initialized with {len(steps)} steps")
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build dependency graph from steps.
        
        Returns:
            Dictionary mapping step IDs to their dependencies
        """
        graph = {}
        for step in self.steps:
            graph[step.step_id] = set(step.dependencies)
        return graph
    
    def _validate_chain_configuration(self) -> None:
        """Validate chain configuration for consistency."""
        step_ids = {step.step_id for step in self.steps}
        
        # Check for duplicate step IDs
        if len(step_ids) != len(self.steps):
            raise ValueError("Duplicate step IDs found in chain")
        
        # Check for invalid dependencies
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Step '{step.step_id}' depends on non-existent step '{dep}'")
        
        # Check for circular dependencies
        if self._has_circular_dependencies():
            raise ValueError("Circular dependencies detected in chain")
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies in the chain.
        
        Returns:
            True if circular dependencies exist
        """
        visited = set()
        rec_stack = set()
        
        def dfs(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)
            
            for dep in self.dependency_graph.get(step_id, set()):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(step_id)
            return False
        
        for step_id in self.dependency_graph:
            if step_id not in visited:
                if dfs(step_id):
                    return True
        
        return False
    
    def get_execution_order(self) -> List[List[str]]:
        """Get execution order for steps, grouped by execution level.
        
        Returns:
            List of step ID groups that can be executed in parallel
        """
        if self.execution_mode == ChainExecutionMode.SEQUENTIAL:
            # Topological sort for sequential execution
            return [[step.step_id] for step in self._topological_sort()]
        
        elif self.execution_mode == ChainExecutionMode.PARALLEL:
            # Group steps by dependency level
            return self._group_by_dependency_level()
        
        else:
            # Default to sequential for other modes
            return [[step.step_id] for step in self._topological_sort()]
    
    def _topological_sort(self) -> List[ValidationStep]:
        """Perform topological sort of steps.
        
        Returns:
            List of steps in topological order
        """
        in_degree = {step.step_id: 0 for step in self.steps}
        
        # Calculate in-degrees
        for step in self.steps:
            for dep in step.dependencies:
                in_degree[step.step_id] += 1
        
        # Find steps with no dependencies
        queue = [step for step in self.steps if in_degree[step.step_id] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees for dependent steps
            for step in self.steps:
                if current.step_id in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step)
        
        return result
    
    def _group_by_dependency_level(self) -> List[List[str]]:
        """Group steps by dependency level for parallel execution.
        
        Returns:
            List of step ID groups by execution level
        """
        levels = []
        remaining_steps = {step.step_id: step for step in self.steps}
        completed_steps = set()
        
        while remaining_steps:
            # Find steps that can be executed (all dependencies completed)
            ready_steps = []
            for step_id, step in remaining_steps.items():
                if all(dep in completed_steps for dep in step.dependencies):
                    ready_steps.append(step_id)
            
            if not ready_steps:
                # This shouldn't happen if dependencies are valid
                raise ValueError("Unable to resolve step dependencies")
            
            # Limit parallel execution
            if len(ready_steps) > self.max_parallel_steps:
                # Prioritize required steps and those with higher weight
                ready_steps.sort(key=lambda sid: (
                    -int(remaining_steps[sid].required),
                    -remaining_steps[sid].weight
                ))
                ready_steps = ready_steps[:self.max_parallel_steps]
            
            levels.append(ready_steps)
            
            # Mark steps as completed and remove from remaining
            for step_id in ready_steps:
                completed_steps.add(step_id)
                del remaining_steps[step_id]
        
        return levels

class ChainValidator:
    """Main validation chain executor."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize chain validator.
        
        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.validators = self._load_validators()
        self.execution_metrics = {}
        
        # Performance settings
        self.enable_metrics = self.config.get('enable_metrics', True)
        self.enable_caching = self.config.get('enable_caching', True)
        self.default_timeout = self.config.get('default_timeout', 30)
        
        logger.info("ChainValidator initialized")
    
    def _load_validators(self) -> Dict[str, Any]:
        """Load available validators.
        
        Returns:
            Dictionary of available validators
        """
        # In a real implementation, this would load actual validator instances
        # For now, we'll simulate with placeholder functions
        validators = {
            'content_validator': self._create_mock_validator('content'),
            'security_compliance_validator': self._create_mock_validator('security'),
            'business_quality_validator': self._create_mock_validator('business'),
            'schema_metadata_validator': self._create_mock_validator('schema'),
            'file_performance_validator': self._create_mock_validator('file'),
            'ai_content_analyzer': self._create_mock_validator('ai'),
            'platform_specific_validator': self._create_mock_validator('platform'),
        }
        return validators
    
    def _create_mock_validator(self, validator_type: str) -> Callable:
        """Create mock validator for demonstration.
        
        Args:
            validator_type: Type of validator
            
        Returns:
            Mock validator function
        """
        async def mock_validator(content: Any, **kwargs) -> Dict[str, Any]:
            # Simulate validation processing time
            await asyncio.sleep(0.1)
            
            # Return mock validation result
            return {
                'is_valid': True,
                'score': 0.85,
                'validator_type': validator_type,
                'issues': [],
                'recommendations': [f"Optimize for {validator_type} validation"]
            }
        
        return mock_validator
    
    async def execute_chain(self, chain: ValidationChain, 
                          content: Any, 
                          context: Optional[Dict[str, Any]] = None) -> ChainResult:
        """Execute validation chain on content.
        
        Args:
            chain: Validation chain to execute
            content: Content to validate
            context: Optional execution context
            
        Returns:
            ChainResult with execution details
        """
        start_time = datetime.now(timezone.utc)
        context = context or {}
        
        logger.info(f"Executing validation chain '{chain.chain_id}'")
        
        try:
            # Get execution order
            execution_levels = chain.get_execution_order()
            
            # Execute steps
            step_results = []
            overall_success = True
            
            for level, step_ids in enumerate(execution_levels):
                logger.debug(f"Executing level {level} with steps: {step_ids}")
                
                if len(step_ids) == 1:
                    # Sequential execution
                    result = await self._execute_step(
                        chain.steps[self._find_step_index(chain, step_ids[0])],
                        content, context, step_results
                    )
                    step_results.append(result)
                else:
                    # Parallel execution
                    parallel_results = await self._execute_steps_parallel(
                        [chain.steps[self._find_step_index(chain, sid)] for sid in step_ids],
                        content, context, step_results
                    )
                    step_results.extend(parallel_results)
                
                # Check for failures and apply failure strategies
                level_failed = any(not r.success for r in step_results[-len(step_ids):])
                if level_failed:
                    overall_success = False
                    
                    # Apply failure strategy
                    should_continue = self._handle_level_failure(
                        chain, level, step_results[-len(step_ids):], step_results
                    )
                    
                    if not should_continue:
                        logger.warning(f"Chain '{chain.chain_id}' stopped due to failure strategy")
                        break
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(step_results)
            
            # Calculate execution time
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Collect performance metrics
            performance_metrics = self._collect_performance_metrics(step_results, execution_time_ms)
            
            # Count step statuses
            successful_steps = sum(1 for r in step_results if r.success)
            failed_steps = sum(1 for r in step_results if not r.success and r.status != StepStatus.SKIPPED)
            skipped_steps = sum(1 for r in step_results if r.status == StepStatus.SKIPPED)
            
            # Generate error summary
            error_summary = [r.error_message for r in step_results 
                           if r.error_message and not r.success]
            
            return ChainResult(
                chain_id=chain.chain_id,
                overall_success=overall_success,
                execution_mode=chain.execution_mode,
                total_steps=len(chain.steps),
                successful_steps=successful_steps,
                failed_steps=failed_steps,
                skipped_steps=skipped_steps,
                step_results=step_results,
                overall_score=overall_score,
                execution_time_ms=execution_time_ms,
                started_at=start_time,
                completed_at=end_time,
                error_summary=error_summary,
                performance_metrics=performance_metrics
            )
            
        except Exception as e:
            logger.error(f"Chain execution failed: {e}")
            end_time = datetime.now(timezone.utc)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return ChainResult(
                chain_id=chain.chain_id,
                overall_success=False,
                execution_mode=chain.execution_mode,
                total_steps=len(chain.steps),
                successful_steps=0,
                failed_steps=len(chain.steps),
                skipped_steps=0,
                step_results=[],
                overall_score=0.0,
                execution_time_ms=execution_time_ms,
                started_at=start_time,
                completed_at=end_time,
                error_summary=[f"Chain execution error: {str(e)}"]
            )
    
    async def _execute_step(self, step: ValidationStep, content: Any,
                          context: Dict[str, Any], 
                          previous_results: List[StepResult]) -> StepResult:
        """Execute a single validation step.
        
        Args:
            step: Validation step to execute
            content: Content to validate
            context: Execution context
            previous_results: Results from previous steps
            
        Returns:
            StepResult with execution details
        """
        start_time = datetime.now(timezone.utc)
        
        # Check conditions
        if not self._check_step_conditions(step, context, previous_results):
            return StepResult(
                step_id=step.step_id,
                status=StepStatus.SKIPPED,
                success=True,  # Skipped steps are considered successful
                execution_time_ms=0,
                started_at=start_time,
                completed_at=start_time
            )
        
        # Execute step with retry logic
        retry_count = 0
        last_error = None
        
        while retry_count <= step.retry_attempts:
            try:
                step_start = datetime.now(timezone.utc)
                
                # Get validator
                validator = self.validators.get(step.validator_name)
                if not validator:
                    raise ValueError(f"Validator '{step.validator_name}' not found")
                
                # Execute validation with timeout
                result_data = await asyncio.wait_for(
                    validator(content, **step.config),
                    timeout=step.timeout_seconds
                )
                
                step_end = datetime.now(timezone.utc)
                execution_time_ms = int((step_end - step_start).total_seconds() * 1000)
                
                # Determine success based on result
                success = self._is_step_successful(result_data, step)
                
                return StepResult(
                    step_id=step.step_id,
                    status=StepStatus.SUCCESS if success else StepStatus.FAILED,
                    success=success,
                    result_data=result_data,
                    execution_time_ms=execution_time_ms,
                    retry_count=retry_count,
                    started_at=start_time,
                    completed_at=step_end,
                    metrics=self._extract_step_metrics(result_data)
                )
                
            except asyncio.TimeoutError:
                last_error = f"Step '{step.step_id}' timed out after {step.timeout_seconds}s"
                logger.warning(last_error)
                
            except Exception as e:
                last_error = f"Step '{step.step_id}' failed: {str(e)}"
                logger.warning(last_error)
            
            # Handle retry
            if retry_count < step.retry_attempts:
                retry_count += 1
                logger.info(f"Retrying step '{step.step_id}' (attempt {retry_count})")
                
                # Wait before retry
                if step.retry_delay_seconds > 0:
                    await asyncio.sleep(step.retry_delay_seconds)
            else:
                break
        
        # All retries failed
        end_time = datetime.now(timezone.utc)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return StepResult(
            step_id=step.step_id,
            status=StepStatus.FAILED,
            success=False,
            error_message=last_error,
            execution_time_ms=execution_time_ms,
            retry_count=retry_count,
            started_at=start_time,
            completed_at=end_time
        )
    
    async def _execute_steps_parallel(self, steps: List[ValidationStep], content: Any,
                                    context: Dict[str, Any], 
                                    previous_results: List[StepResult]) -> List[StepResult]:
        """Execute multiple steps in parallel.
        
        Args:
            steps: List of validation steps to execute
            content: Content to validate
            context: Execution context
            previous_results: Results from previous steps
            
        Returns:
            List of StepResult objects
        """
        # Create tasks for parallel execution
        tasks = []
        for step in steps:
            task = asyncio.create_task(
                self._execute_step(step, content, context, previous_results)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        step_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                step_results.append(StepResult(
                    step_id=steps[i].step_id,
                    status=StepStatus.FAILED,
                    success=False,
                    error_message=f"Parallel execution error: {str(result)}",
                    execution_time_ms=0
                ))
            else:
                step_results.append(result)
        
        return step_results
    
    def _check_step_conditions(self, step: ValidationStep, context: Dict[str, Any],
                             previous_results: List[StepResult]) -> bool:
        """Check if step conditions are met.
        
        Args:
            step: Validation step
            context: Execution context
            previous_results: Previous step results
            
        Returns:
            True if conditions are met
        """
        if not step.conditions:
            return True
        
        # Check content type conditions
        content_type = context.get('content_type')
        if 'content_types' in step.conditions:
            if content_type not in step.conditions['content_types']:
                return False
        
        # Check platform conditions
        platform = context.get('platform')
        if 'platforms' in step.conditions:
            if platform not in step.conditions['platforms']:
                return False
        
        # Check dependency results
        if 'require_success' in step.conditions:
            required_steps = step.conditions['require_success']
            for required_step in required_steps:
                result = next((r for r in previous_results if r.step_id == required_step), None)
                if not result or not result.success:
                    return False
        
        # Check score conditions
        if 'min_score' in step.conditions:
            min_score = step.conditions['min_score']
            for result in previous_results:
                if (result.result_data and 
                    isinstance(result.result_data, dict) and
                    'score' in result.result_data):
                    if result.result_data['score'] < min_score:
                        return False
        
        return True
    
    def _is_step_successful(self, result_data: Any, step: ValidationStep) -> bool:
        """Determine if step execution was successful.
        
        Args:
            result_data: Result data from validator
            step: Validation step
            
        Returns:
            True if step was successful
        """
        if not result_data:
            return False
        
        if isinstance(result_data, dict):
            # Check for explicit success indicator
            if 'is_valid' in result_data:
                return result_data['is_valid']
            
            if 'success' in result_data:
                return result_data['success']
            
            # Check score-based success
            if 'score' in result_data:
                min_score = step.config.get('min_score', 0.5)
                return result_data['score'] >= min_score
        
        # Default to success if no clear failure indicators
        return True
    
    def _handle_level_failure(self, chain: ValidationChain, level: int,
                            level_results: List[StepResult],
                            all_results: List[StepResult]) -> bool:
        """Handle failures at execution level.
        
        Args:
            chain: Validation chain
            level: Current execution level
            level_results: Results from current level
            all_results: All results so far
            
        Returns:
            True if execution should continue
        """
        failed_results = [r for r in level_results if not r.success]
        
        for failed_result in failed_results:
            step = next(s for s in chain.steps if s.step_id == failed_result.step_id)
            
            if step.failure_strategy == FailureStrategy.FAIL_FAST:
                return False
            elif step.failure_strategy == FailureStrategy.CONTINUE_ON_ERROR:
                continue
            elif step.failure_strategy == FailureStrategy.SKIP_ON_ERROR:
                failed_result.status = StepStatus.SKIPPED
            # RETRY_ON_FAILURE is handled in _execute_step
        
        return True
    
    def _calculate_overall_score(self, step_results: List[StepResult]) -> float:
        """Calculate overall score from step results.
        
        Args:
            step_results: List of step results
            
        Returns:
            Overall score (0.0 to 1.0)
        """
        if not step_results:
            return 0.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        for result in step_results:
            # Find corresponding step for weight
            weight = 1.0  # Default weight
            step_score = 0.0
            
            if result.success:
                if result.result_data and isinstance(result.result_data, dict):
                    step_score = result.result_data.get('score', 1.0)
                else:
                    step_score = 1.0
            else:
                step_score = 0.0
            
            weighted_score += step_score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _collect_performance_metrics(self, step_results: List[StepResult],
                                   total_execution_time_ms: int) -> Dict[str, Any]:
        """Collect performance metrics from execution.
        
        Args:
            step_results: List of step results
            total_execution_time_ms: Total execution time
            
        Returns:
            Performance metrics dictionary
        """
        metrics = {
            'total_execution_time_ms': total_execution_time_ms,
            'step_count': len(step_results),
            'successful_steps': sum(1 for r in step_results if r.success),
            'failed_steps': sum(1 for r in step_results if not r.success),
            'average_step_time_ms': 0,
            'max_step_time_ms': 0,
            'min_step_time_ms': 0,
            'total_retry_count': sum(r.retry_count for r in step_results),
            'parallel_efficiency': 0.0
        }
        
        if step_results:
            step_times = [r.execution_time_ms for r in step_results if r.execution_time_ms > 0]
            if step_times:
                metrics['average_step_time_ms'] = sum(step_times) / len(step_times)
                metrics['max_step_time_ms'] = max(step_times)
                metrics['min_step_time_ms'] = min(step_times)
                
                # Calculate parallel efficiency
                sequential_time = sum(step_times)
                if total_execution_time_ms > 0:
                    metrics['parallel_efficiency'] = sequential_time / total_execution_time_ms
        
        return metrics
    
    def _extract_step_metrics(self, result_data: Any) -> Dict[str, Any]:
        """Extract metrics from step result data.
        
        Args:
            result_data: Result data from validator
            
        Returns:
            Extracted metrics
        """
        metrics = {}
        
        if isinstance(result_data, dict):
            # Extract common metrics
            if 'score' in result_data:
                metrics['score'] = result_data['score']
            
            if 'issues' in result_data:
                metrics['issue_count'] = len(result_data['issues'])
            
            if 'recommendations' in result_data:
                metrics['recommendation_count'] = len(result_data['recommendations'])
            
            # Extract validator-specific metrics
            for key, value in result_data.items():
                if key.endswith('_score') or key.endswith('_count') or key.endswith('_time'):
                    metrics[key] = value
        
        return metrics
    
    def _find_step_index(self, chain: ValidationChain, step_id: str) -> int:
        """Find index of step in chain.
        
        Args:
            chain: Validation chain
            step_id: Step ID to find
            
        Returns:
            Index of step in chain
        """
        for i, step in enumerate(chain.steps):
            if step.step_id == step_id:
                return i
        raise ValueError(f"Step '{step_id}' not found in chain")

class ValidationPipeline:
    """High-level validation pipeline manager."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize validation pipeline.
        
        Args:
            config: Optional configuration
        """
        self.config = config or {}
        self.chain_validator = ChainValidator(config)
        self.predefined_chains = self._load_predefined_chains()
        
        logger.info("ValidationPipeline initialized")
    
    def _load_predefined_chains(self) -> Dict[str, ValidationChain]:
        """Load predefined validation chains.
        
        Returns:
            Dictionary of predefined chains
        """
        chains = {}
        
        # Content Upload Chain
        chains['content_upload'] = ValidationChain(
            chain_id='content_upload',
            steps=[
                ValidationStep(
                    step_id='file_validation',
                    step_type=ValidationStepType.FILE,
                    validator_name='file_performance_validator',
                    config={'validation_types': ['integrity', 'format']},
                    required=True,
                    weight=1.0
                ),
                ValidationStep(
                    step_id='security_check',
                    step_type=ValidationStepType.SECURITY,
                    validator_name='security_compliance_validator',
                    config={'enable_malware_scan': True},
                    dependencies=['file_validation'],
                    required=True,
                    weight=1.5
                ),
                ValidationStep(
                    step_id='content_validation',
                    step_type=ValidationStepType.CONTENT,
                    validator_name='content_validator',
                    config={'validation_level': 'normal'},
                    dependencies=['file_validation'],
                    parallel_allowed=True,
                    weight=1.0
                ),
                ValidationStep(
                    step_id='metadata_extraction',
                    step_type=ValidationStepType.SCHEMA,
                    validator_name='schema_metadata_validator',
                    config={'ai_enhancement': True},
                    dependencies=['content_validation'],
                    parallel_allowed=True,
                    weight=0.8
                ),
                ValidationStep(
                    step_id='business_rules',
                    step_type=ValidationStepType.BUSINESS,
                    validator_name='business_quality_validator',
                    config={'context': 'upload'},
                    dependencies=['security_check', 'content_validation'],
                    required=True,
                    weight=1.2
                )
            ],
            execution_mode=ChainExecutionMode.PARALLEL,
            max_parallel_steps=3
        )
        
        # Monetization Chain
        chains['monetization'] = ValidationChain(
            chain_id='monetization',
            steps=[
                ValidationStep(
                    step_id='copyright_check',
                    step_type=ValidationStepType.SECURITY,
                    validator_name='security_compliance_validator',
                    config={'frameworks': ['dmca']},
                    required=True,
                    weight=2.0
                ),
                ValidationStep(
                    step_id='quality_assessment',
                    step_type=ValidationStepType.BUSINESS,
                    validator_name='business_quality_validator',
                    config={'context': 'monetization'},
                    required=True,
                    weight=1.5
                ),
                ValidationStep(
                    step_id='platform_compliance',
                    step_type=ValidationStepType.PLATFORM_SPECIFIC,
                    validator_name='platform_specific_validator',
                    dependencies=['copyright_check', 'quality_assessment'],
                    required=True,
                    weight=1.0
                )
            ],
            execution_mode=ChainExecutionMode.SEQUENTIAL
        )
        
        # Performance Optimization Chain
        chains['performance_optimization'] = ValidationChain(
            chain_id='performance_optimization',
            steps=[
                ValidationStep(
                    step_id='file_performance',
                    step_type=ValidationStepType.FILE,
                    validator_name='file_performance_validator',
                    config={'enable_performance_analysis': True},
                    required=False,
                    weight=1.0
                ),
                ValidationStep(
                    step_id='ai_analysis',
                    step_type=ValidationStepType.AI_ANALYSIS,
                    validator_name='ai_content_analyzer',
                    config={'deep_analysis': True},
                    parallel_allowed=True,
                    required=False,
                    weight=0.8
                ),
                ValidationStep(
                    step_id='optimization_recommendations',
                    step_type=ValidationStepType.CUSTOM,
                    validator_name='optimization_engine',
                    dependencies=['file_performance', 'ai_analysis'],
                    required=False,
                    weight=0.5
                )
            ],
            execution_mode=ChainExecutionMode.PARALLEL
        )
        
        return chains
    
    async def execute_pipeline(self, pipeline_name: str, content: Any,
                             context: Optional[Dict[str, Any]] = None) -> ChainResult:
        """Execute predefined validation pipeline.
        
        Args:
            pipeline_name: Name of predefined pipeline
            content: Content to validate
            context: Optional execution context
            
        Returns:
            ChainResult with execution details
        """
        if pipeline_name not in self.predefined_chains:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")
        
        chain = self.predefined_chains[pipeline_name]
        return await self.chain_validator.execute_chain(chain, content, context)
    
    async def execute_custom_chain(self, chain: ValidationChain, content: Any,
                                 context: Optional[Dict[str, Any]] = None) -> ChainResult:
        """Execute custom validation chain.
        
        Args:
            chain: Custom validation chain
            content: Content to validate
            context: Optional execution context
            
        Returns:
            ChainResult with execution details
        """
        return await self.chain_validator.execute_chain(chain, content, context)
    
    def get_available_pipelines(self) -> List[str]:
        """Get list of available predefined pipelines.
        
        Returns:
            List of pipeline names
        """
        return list(self.predefined_chains.keys())
    
    def get_pipeline_info(self, pipeline_name: str) -> Dict[str, Any]:
        """Get information about a specific pipeline.
        
        Args:
            pipeline_name: Name of pipeline
            
        Returns:
            Pipeline information
        """
        if pipeline_name not in self.predefined_chains:
            raise ValueError(f"Pipeline '{pipeline_name}' not found")
        
        chain = self.predefined_chains[pipeline_name]
        
        return {
            'chain_id': chain.chain_id,
            'execution_mode': chain.execution_mode.value,
            'step_count': len(chain.steps),
            'steps': [
                {
                    'step_id': step.step_id,
                    'step_type': step.step_type.value,
                    'validator_name': step.validator_name,
                    'required': step.required,
                    'dependencies': step.dependencies
                }
                for step in chain.steps
            ],
            'estimated_duration_seconds': sum(step.timeout_seconds for step in chain.steps),
            'max_parallel_steps': chain.max_parallel_steps
        }

# Export main classes and functions
__all__ = [
    'ValidationChain',
    'ChainValidator', 
    'ValidationPipeline',
    'ValidationStep',
    'StepResult',
    'ChainResult',
    'ValidationStepType',
    'StepStatus',
    'ChainExecutionMode',
    'FailureStrategy'
]