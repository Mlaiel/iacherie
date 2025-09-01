"""Validation Chain Engine for Crawler System
==========================================

Advanced validation pipeline and chain management system for the IA Influencer Agent Platform
providing orchestrated validation workflows and comprehensive validation management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use, reproduction, or distribution strictly prohibited

Features:
- Sequential and parallel validation chains
- Conditional validation workflows
- Validation result aggregation
- Error handling and recovery
- Performance optimization
"""

import asyncio
import time
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .content_validator import ContentValidator, ValidationResult as ContentValidationResult
from .schema_validator import SchemaValidator, SchemaValidationResult
from .quality_validator import DataQualityValidator, QualityProfile
from .business_validator import BusinessRuleValidator, BusinessRuleResult
from .performance_validator import PerformanceValidator, PerformanceProfile
from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ValidationMode(Enum):
    """
Validation execution modes"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    FAIL_FAST = "fail_fast"
    CONTINUE_ON_ERROR = "continue_on_error"


class ValidationPriority(Enum):
    """Validation priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


@dataclass
class ValidationStep:
    """Individual validation step in a chain"""
    name: str
    validator_class: Type
    validator_config: Dict[str, Any] = field(default_factory=dict)
    priority: ValidationPriority = ValidationPriority.MEDIUM
    enabled: bool = True
    conditions: List[Callable[[Dict[str, Any]], bool]] = field(default_factory=list)
    timeout_seconds: Optional[float] = None
    retry_count: int = 0
    retry_delay: float = 1.0
    
    # Execution tracking
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time: float = 0.0
    last_executed: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """
Calculate step success rate"""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count
    
    def should_execute(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
Check if step should be executed based on conditions"""
        if not self.enabled:
            return False
        
        if not self.conditions:
            return True
        
        try:
            return all(condition({**data, **context}) for condition in self.conditions)
        except Exception as e:
            logger.warning(f"Condition check failed for step '{self.name}': {str(e)}")
            return False


@dataclass
class ValidationChainResult:
    """Comprehensive validation chain result"""
    is_valid: bool
    overall_score: float
    chain_name: str
    executed_steps: List[str] = field(default_factory=list)
    skipped_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    step_results: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    total_steps: int = 0
    successful_steps: int = 0
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """
Calculate chain success rate"""
        if self.total_steps == 0:
            return 0.0
        return self.successful_steps / self.total_steps
    
    @property
    def has_critical_failures(self) -> bool:
        """
Check if chain has critical failures"""
        return len(self.critical_failures) > 0
    
    @property
    def completion_rate(self) -> float:
        """
Calculate completion rate (executed vs total)"""
        if self.total_steps == 0:
            return 0.0
        return len(self.executed_steps) / self.total_steps


class ValidationChain:
    """
    Validation chain orchestrator for complex validation workflows.
    
    Manages sequential and parallel execution of multiple validation steps
    with comprehensive error handling, performance tracking, and result aggregation.
    """
    
    def __init__(
        self,
        name: str,
        mode: ValidationMode = ValidationMode.SEQUENTIAL,
        max_workers: int = 4,
        global_timeout_seconds: Optional[float] = None
    ):
        self.name = name
        self.mode = mode
        self.max_workers = max_workers
        self.global_timeout_seconds = global_timeout_seconds
        
        self.steps = []
        self.validators = {}
        self.execution_history = []
        self.max_history_size = 100
        
        # Performance tracking
        self.chain_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'avg_execution_time': 0.0,
            'last_executed': None
        }
        
        logger.info(f"ValidationChain '{name}' initialized with mode: {mode.value}")
    
    def add_step(self, step: ValidationStep) -> None:
        """Add a validation step to the chain"""
        self.steps.append(step)
        
        # Initialize validator if not exists
        if step.validator_class not in self.validators:
            self.validators[step.validator_class] = step.validator_class(**step.validator_config)
        
        logger.debug(f"Added validation step '{step.name}' to chain '{self.name}'")
    
    def remove_step(self, step_name: str) -> None:
        """Remove a validation step from the chain"""
        self.steps = [step for step in self.steps if step.name != step_name]
        logger.debug(f"Removed validation step '{step_name}' from chain '{self.name}'")
    
    def enable_step(self, step_name: str) -> None:
        """Enable a specific validation step"""
        for step in self.steps:
            if step.name == step_name:
                step.enabled = True
                break
    
    def disable_step(self, step_name: str) -> None:
        """
Disable a specific validation step"""
        for step in self.steps:
            if step.name == step_name:
                step.enabled = False
                break
    
    def execute(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        stop_on_critical: bool = True
    ) -> ValidationChainResult:
        """
        Execute the validation chain.
        
        Args:
            data: Data to validate
            context: Additional context for validation
            stop_on_critical: Stop execution on critical failures
            
        Returns:
            ValidationChainResult: Comprehensive chain execution result
        """
        start_time = time.time()
        context = context or {}
        
        result = ValidationChainResult(
            is_valid=True,
            overall_score=1.0,
            chain_name=self.name,
            total_steps=len([s for s in self.steps if s.enabled])
        )
        
        try:
            if self.mode == ValidationMode.SEQUENTIAL:
                result = self._execute_sequential(data, context, result, stop_on_critical)
            elif self.mode == ValidationMode.PARALLEL:
                result = self._execute_parallel(data, context, result, stop_on_critical)
            elif self.mode == ValidationMode.CONDITIONAL:
                result = self._execute_conditional(data, context, result, stop_on_critical)
            elif self.mode == ValidationMode.FAIL_FAST:
                result = self._execute_fail_fast(data, context, result)
            elif self.mode == ValidationMode.CONTINUE_ON_ERROR:
                result = self._execute_continue_on_error(data, context, result)
            
            # Aggregate results and calculate scores
            self._aggregate_results(result)
            
        except Exception as e:
            logger.error(f"Validation chain '{self.name}' execution failed: {str(e)}")
            result.is_valid = False
            result.critical_failures.append(f"Chain execution error: {str(e)}")
        
        # Record execution time
        execution_time = (time.time() - start_time) * 1000
        result.execution_time_ms = execution_time
        
        # Update chain statistics
        self._update_chain_stats(result, execution_time)
        
        # Store in history
        self._store_execution_history(result)
        
        logger.info(f"Validation chain '{self.name}' completed in {execution_time:.2f}ms")
        return result
    
    async def execute_async(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        stop_on_critical: bool = True
    ) -> ValidationChainResult:
        """
        Execute the validation chain asynchronously.
        
        Args:
            data: Data to validate
            context: Additional context for validation
            stop_on_critical: Stop execution on critical failures
            
        Returns:
            ValidationChainResult: Comprehensive chain execution result
        """
        start_time = time.time()
        context = context or {}
        
        result = ValidationChainResult(
            is_valid=True,
            overall_score=1.0,
            chain_name=self.name,
            total_steps=len([s for s in self.steps if s.enabled])
        )
        
        try:
            if self.mode in [ValidationMode.PARALLEL, ValidationMode.CONTINUE_ON_ERROR]:
                result = await self._execute_async_parallel(data, context, result, stop_on_critical)
            else:
                # For other modes, fall back to sync execution in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    self.execute, 
                    data, 
                    context, 
                    stop_on_critical
                )
        
        except Exception as e:
            logger.error(f"Async validation chain '{self.name}' execution failed: {str(e)}")
            result.is_valid = False
            result.critical_failures.append(f"Async chain execution error: {str(e)}")
        
        return result
    
    def get_chain_statistics(self) -> Dict[str, Any]:
        """Get detailed chain execution statistics"""
        step_stats = {}
        for step in self.steps:
            step_stats[step.name] = {
                'execution_count': step.execution_count,
                'success_count': step.success_count,
                'failure_count': step.failure_count,
                'success_rate': step.success_rate,
                'avg_execution_time': step.avg_execution_time,
                'priority': step.priority.value,
                'enabled': step.enabled,
                'last_executed': step.last_executed.isoformat() if step.last_executed else None
            }
        
        return {
            'chain_name': self.name,
            'mode': self.mode.value,
            'total_steps': len(self.steps),
            'enabled_steps': len([s for s in self.steps if s.enabled]),
            'chain_stats': self.chain_stats,
            'step_stats': step_stats,
            'recent_executions': len(self.execution_history)
        }
    
    # Execution mode implementations
    
    def _execute_sequential(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        result: ValidationChainResult,
        stop_on_critical: bool
    ) -> ValidationChainResult:
        """
Execute steps sequentially"""
        
        for step in self._get_enabled_steps_by_priority():
            if not step.should_execute(data, context):
                result.skipped_steps.append(step.name)
                continue
            
            step_result = self._execute_step(step, data, context)
            result.step_results[step.name] = step_result
            result.executed_steps.append(step.name)
            
            if self._is_step_successful(step_result):
                result.successful_steps += 1
            else:
                result.failed_steps.append(step.name)
                result.is_valid = False
                
                if self._is_critical_failure(step_result) or step.priority == ValidationPriority.CRITICAL:
                    result.critical_failures.append(step.name)
                    if stop_on_critical:
                        break
        
        return result
    
    def _execute_parallel(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        result: ValidationChainResult,
        stop_on_critical: bool
    ) -> ValidationChainResult:
        """
Execute steps in parallel"""
        
        enabled_steps = [s for s in self.steps if s.enabled and s.should_execute(data, context)]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all step executions
            future_to_step = {
                executor.submit(self._execute_step, step, data, context): step
                for step in enabled_steps
            }
            
            # Collect results
            for future in as_completed(future_to_step):
                step = future_to_step[future]
                
                try:
                    step_result = future.result()
                    result.step_results[step.name] = step_result
                    result.executed_steps.append(step.name)
                    
                    if self._is_step_successful(step_result):
                        result.successful_steps += 1
                    else:
                        result.failed_steps.append(step.name)
                        result.is_valid = False
                        
                        if self._is_critical_failure(step_result) or step.priority == ValidationPriority.CRITICAL:
                            result.critical_failures.append(step.name)
                            if stop_on_critical:
                                # Cancel remaining futures
                                for remaining_future in future_to_step:
                                    if not remaining_future.done():
                                        remaining_future.cancel()
                                break
                
                except Exception as e:
                    logger.error(f"Step '{step.name}' execution failed: {str(e)}")
                    result.failed_steps.append(step.name)
                    result.critical_failures.append(step.name)
                    result.is_valid = False
        
        return result
    
    def _execute_conditional(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        result: ValidationChainResult,
        stop_on_critical: bool
    ) -> ValidationChainResult:
        """Execute steps based on conditions and dependencies"""
        
        executed_steps = set()
        
        for step in self._get_enabled_steps_by_priority():
            # Check if step should execute based on previous results
            if not step.should_execute(data, {**context, 'executed_steps': executed_steps}):
                result.skipped_steps.append(step.name)
                continue
            
            step_result = self._execute_step(step, data, context)
            result.step_results[step.name] = step_result
            result.executed_steps.append(step.name)
            executed_steps.add(step.name)
            
            if self._is_step_successful(step_result):
                result.successful_steps += 1
                # Add successful step to context for next steps
                context[f'step_{step.name}_result'] = step_result
            else:
                result.failed_steps.append(step.name)
                result.is_valid = False
                
                if self._is_critical_failure(step_result) or step.priority == ValidationPriority.CRITICAL:
                    result.critical_failures.append(step.name)
                    if stop_on_critical:
                        break
        
        return result
    
    def _execute_fail_fast(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        result: ValidationChainResult
    ) -> ValidationChainResult:
        """
Execute steps and stop on first failure"""
        
        for step in self._get_enabled_steps_by_priority():
            if not step.should_execute(data, context):
                result.skipped_steps.append(step.name)
                continue
            
            step_result = self._execute_step(step, data, context)
            result.step_results[step.name] = step_result
            result.executed_steps.append(step.name)
            
            if self._is_step_successful(step_result):
                result.successful_steps += 1
            else:
                result.failed_steps.append(step.name)
                result.is_valid = False
                break  # Stop on first failure
        
        return result
    
    def _execute_continue_on_error(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        result: ValidationChainResult
    ) -> ValidationChainResult:
        """
Execute all steps regardless of failures"""
        
        for step in self._get_enabled_steps_by_priority():
            if not step.should_execute(data, context):
                result.skipped_steps.append(step.name)
                continue
            
            try:
                step_result = self._execute_step(step, data, context)
                result.step_results[step.name] = step_result
                result.executed_steps.append(step.name)
                
                if self._is_step_successful(step_result):
                    result.successful_steps += 1
                else:
                    result.failed_steps.append(step.name)
                    result.is_valid = False
                    
                    if self._is_critical_failure(step_result) or step.priority == ValidationPriority.CRITICAL:
                        result.critical_failures.append(step.name)
            
            except Exception as e:
                logger.error(f"Step '{step.name}' execution failed: {str(e)}")
                result.failed_steps.append(step.name)
                result.critical_failures.append(step.name)
                result.is_valid = False
        
        return result
    
    async def _execute_async_parallel(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any],
        result: ValidationChainResult,
        stop_on_critical: bool
    ) -> ValidationChainResult:
        """Execute steps asynchronously in parallel"""
        
        enabled_steps = [s for s in self.steps if s.enabled and s.should_execute(data, context)]
        
        # Create async tasks for each step
        tasks = []
        for step in enabled_steps:
            task = asyncio.create_task(self._execute_step_async(step, data, context))
            tasks.append((task, step))
        
        # Wait for all tasks to complete
        for task, step in tasks:
            try:
                step_result = await task
                result.step_results[step.name] = step_result
                result.executed_steps.append(step.name)
                
                if self._is_step_successful(step_result):
                    result.successful_steps += 1
                else:
                    result.failed_steps.append(step.name)
                    result.is_valid = False
                    
                    if self._is_critical_failure(step_result) or step.priority == ValidationPriority.CRITICAL:
                        result.critical_failures.append(step.name)
                        if stop_on_critical:
                            # Cancel remaining tasks
                            for remaining_task, _ in tasks:
                                if not remaining_task.done():
                                    remaining_task.cancel()
                            break
            
            except Exception as e:
                logger.error(f"Async step '{step.name}' execution failed: {str(e)}")
                result.failed_steps.append(step.name)
                result.critical_failures.append(step.name)
                result.is_valid = False
        
        return result
    
    # Helper methods
    
    def _get_enabled_steps_by_priority(self) -> List[ValidationStep]:
        """Get enabled steps sorted by priority"""
        enabled_steps = [step for step in self.steps if step.enabled]
        priority_order = {
            ValidationPriority.CRITICAL: 0,
            ValidationPriority.HIGH: 1,
            ValidationPriority.MEDIUM: 2,
            ValidationPriority.LOW: 3,
            ValidationPriority.OPTIONAL: 4
        }
        return sorted(enabled_steps, key=lambda s: priority_order.get(s.priority, 999))
    
    def _execute_step(self, step: ValidationStep, data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
Execute a single validation step with retry logic"""
        step_start_time = time.time()
        step.execution_count += 1
        step.last_executed = datetime.utcnow()
        
        for attempt in range(step.retry_count + 1):
            try:
                # Get validator instance
                validator = self.validators[step.validator_class]
                
                # Execute validation based on validator type
                if isinstance(validator, ContentValidator):
                    result = self._execute_content_validation(validator, data, step)
                elif isinstance(validator, SchemaValidator):
                    result = self._execute_schema_validation(validator, data, step)
                elif isinstance(validator, DataQualityValidator):
                    result = self._execute_quality_validation(validator, data, step)
                elif isinstance(validator, BusinessRuleValidator):
                    result = self._execute_business_validation(validator, data, step)
                elif isinstance(validator, PerformanceValidator):
                    result = self._execute_performance_validation(validator, data, step)
                else:
                    # Generic validation call
                    if hasattr(validator, 'validate'):
                        result = validator.validate(data)
                    else:
                        raise ValidationException(f"Validator {step.validator_class.__name__} has no validate method")
                
                # Update step statistics
                execution_time = (time.time() - step_start_time) * 1000
                step.avg_execution_time = (
                    (step.avg_execution_time * (step.execution_count - 1) + execution_time) 
                    / step.execution_count
                )
                step.success_count += 1
                
                return result
            
            except Exception as e:
                if attempt < step.retry_count:
                    logger.warning(f"Step '{step.name}' attempt {attempt + 1} failed, retrying: {str(e)}")
                    time.sleep(step.retry_delay)
                else:
                    step.failure_count += 1
                    logger.error(f"Step '{step.name}' failed after {step.retry_count + 1} attempts: {str(e)}")
                    raise
    
    async def _execute_step_async(self, step: ValidationStep, data: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Execute a validation step asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._execute_step, step, data, context)
    
    def _execute_content_validation(self, validator: ContentValidator, data: Dict[str, Any], step: ValidationStep) -> Any:
        """
Execute content validation"""
        content = data.get('content', '')
        content_type = data.get('content_type', 'text')
        metadata = data.get('metadata')
        platform_target = data.get('platform_target')
        
        from .content_validator import ContentType
        content_type_enum = getattr(ContentType, content_type.upper(), ContentType.TEXT)
        
        return validator.validate_content(
            content=content,
            content_type=content_type_enum,
            metadata=metadata,
            platform_target=platform_target
        )
    
    def _execute_schema_validation(self, validator: SchemaValidator, data: Dict[str, Any], step: ValidationStep) -> Any:
        """
Execute schema validation"""
        validation_type = step.validator_config.get('validation_type', 'custom')
        
        if validation_type == 'json_schema':
            schema = step.validator_config.get('schema', {})
            return validator.validate_json_schema(data, schema)
        elif validation_type == 'business_object':
            object_type = step.validator_config.get('object_type', 'generic')
            return validator.validate_business_object(data, object_type)
        else:
            # Custom rules validation
            rules = step.validator_config.get('rules', [])
            return validator.validate_custom_rules(data, rules)
    
    def _execute_quality_validation(self, validator: DataQualityValidator, data: Dict[str, Any], step: ValidationStep) -> Any:
        """
Execute quality validation"""
        content_type = step.validator_config.get('content_type', 'unknown')
        return validator.assess_quality(data, content_type)
    
    def _execute_business_validation(self, validator: BusinessRuleValidator, data: Dict[str, Any], step: ValidationStep) -> Any:
        """
Execute business rule validation"""
        rule_categories = step.validator_config.get('rule_categories')
        rule_names = step.validator_config.get('rule_names')
        stop_on_critical = step.validator_config.get('stop_on_critical', True)
        
        return validator.validate(
            data=data,
            rule_categories=rule_categories,
            rule_names=rule_names,
            stop_on_critical=stop_on_critical
        )
    
    def _execute_performance_validation(self, validator: PerformanceValidator, data: Dict[str, Any], step: ValidationStep) -> Any:
        """
Execute performance validation"""
        operation_name = step.validator_config.get('operation_name', step.name)
        
        # Create a simple operation function for performance testing
        def test_operation():
            return data  # Simple data processing operation
        
        return validator.validate_performance(test_operation, operation_name)
    
    def _is_step_successful(self, step_result: Any) -> bool:
        """
Check if step execution was successful"""
        if hasattr(step_result, 'is_valid'):
            return step_result.is_valid
        elif hasattr(step_result, 'overall_score'):
            return step_result.overall_score >= 0.7
        elif hasattr(step_result, 'success_rate'):
            return step_result.success_rate >= 0.8
        else:
            return step_result is not None
    
    def _is_critical_failure(self, step_result: Any) -> bool:
        """
Check if step result indicates critical failure"""
        if hasattr(step_result, 'has_critical_violations'):
            return step_result.has_critical_violations
        elif hasattr(step_result, 'critical_issues'):
            return len(step_result.critical_issues) > 0
        elif hasattr(step_result, 'overall_score'):
            return step_result.overall_score < 0.3
        else:
            return False
    
    def _aggregate_results(self, result: ValidationChainResult) -> None:
        """
Aggregate validation results and calculate overall scores"""
        
        # Calculate overall score
        scores = []
        weights = []
        
        for step_name, step_result in result.step_results.items():
            step = next((s for s in self.steps if s.name == step_name), None)
            if not step:
                continue
            
            # Extract score from step result
            score = 0.0
            if hasattr(step_result, 'overall_score'):
                score = step_result.overall_score
            elif hasattr(step_result, 'quality_score'):
                score = step_result.quality_score
            elif hasattr(step_result, 'success_rate'):
                score = step_result.success_rate
            elif hasattr(step_result, 'is_valid'):
                score = 1.0 if step_result.is_valid else 0.0
            
            scores.append(score)
            
            # Weight by priority
            priority_weights = {
                ValidationPriority.CRITICAL: 2.0,
                ValidationPriority.HIGH: 1.5,
                ValidationPriority.MEDIUM: 1.0,
                ValidationPriority.LOW: 0.8,
                ValidationPriority.OPTIONAL: 0.5
            }
            weights.append(priority_weights.get(step.priority, 1.0))
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            result.overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Collect warnings and recommendations
        for step_result in result.step_results.values():
            if hasattr(step_result, 'warnings'):
                result.warnings.extend(step_result.warnings)
            if hasattr(step_result, 'recommendations'):
                result.recommendations.extend(step_result.recommendations)
            if hasattr(step_result, 'improvement_suggestions'):
                result.recommendations.extend(step_result.improvement_suggestions)
    
    def _update_chain_stats(self, result: ValidationChainResult, execution_time: float) -> None:
        """
Update chain execution statistics"""
        self.chain_stats['total_executions'] += 1
        
        if result.is_valid:
            self.chain_stats['successful_executions'] += 1
        
        # Update average execution time
        current_avg = self.chain_stats['avg_execution_time']
        total_executions = self.chain_stats['total_executions']
        self.chain_stats['avg_execution_time'] = (
            (current_avg * (total_executions - 1) + execution_time) / total_executions
        )
        
        self.chain_stats['last_executed'] = datetime.utcnow().isoformat()
    
    def _store_execution_history(self, result: ValidationChainResult) -> None:
        """
Store execution result in history"""
        self.execution_history.append(result)
        
        # Limit history size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size:]


# Predefined validation chains

def create_content_validation_chain() -> ValidationChain:
    """
Create a comprehensive content validation chain"""
    chain = ValidationChain(
        name="content_validation_chain",
        mode=ValidationMode.SEQUENTIAL
    )
    
    # Add content validation step
    chain.add_step(ValidationStep(
        name="content_validation",
        validator_class=ContentValidator,
        priority=ValidationPriority.HIGH
    ))
    
    # Add quality assessment step
    chain.add_step(ValidationStep(
        name="quality_assessment",
        validator_class=DataQualityValidator,
        priority=ValidationPriority.MEDIUM
    ))
    
    # Add business rules validation
    chain.add_step(ValidationStep(
        name="business_rules",
        validator_class=BusinessRuleValidator,
        priority=ValidationPriority.HIGH
    ))
    
    return chain


def create_performance_validation_chain() -> ValidationChain:
    """Create a performance-focused validation chain"""
    chain = ValidationChain(
        name="performance_validation_chain",
        mode=ValidationMode.PARALLEL,
        max_workers=2
    )
    
    # Add performance validation step
    chain.add_step(ValidationStep(
        name="performance_validation",
        validator_class=PerformanceValidator,
        priority=ValidationPriority.CRITICAL
    ))
    
    # Add quality assessment with performance focus
    chain.add_step(ValidationStep(
        name="quality_performance_check",
        validator_class=DataQualityValidator,
        priority=ValidationPriority.MEDIUM
    ))
    
    return chain


def create_comprehensive_validation_chain() -> ValidationChain:
    """Create a comprehensive validation chain with all validators"""
    chain = ValidationChain(
        name="comprehensive_validation_chain",
        mode=ValidationMode.CONDITIONAL
    )
    
    # Critical validations first
    chain.add_step(ValidationStep(
        name="schema_validation",
        validator_class=SchemaValidator,
        priority=ValidationPriority.CRITICAL,
        validator_config={'validation_type': 'business_object', 'object_type': 'content_item'}
    ))
    
    chain.add_step(ValidationStep(
        name="content_security",
        validator_class=ContentValidator,
        priority=ValidationPriority.CRITICAL
    ))
    
    # High priority validations
    chain.add_step(ValidationStep(
        name="business_compliance",
        validator_class=BusinessRuleValidator,
        priority=ValidationPriority.HIGH,
        validator_config={'rule_categories': ['security_compliance', 'data_protection']}
    ))
    
    # Medium priority validations
    chain.add_step(ValidationStep(
        name="quality_assessment",
        validator_class=DataQualityValidator,
        priority=ValidationPriority.MEDIUM
    ))
    
    chain.add_step(ValidationStep(
        name="content_quality",
        validator_class=ContentValidator,
        priority=ValidationPriority.MEDIUM
    ))
    
    # Optional performance check
    chain.add_step(ValidationStep(
        name="performance_check",
        validator_class=PerformanceValidator,
        priority=ValidationPriority.OPTIONAL
    ))
    
    return chain
