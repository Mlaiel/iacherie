"""Comprehensive validation system for workflow components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, Any, List, Optional, Set, Callable, Union
from dataclasses import dataclass
from enum import Enum
import re
import json
from datetime import datetime, timedelta
import logging

from .exceptions import (
    WorkflowException,
    PipelineException,
    SchedulingException,
    StateException,
    WorkflowErrorCode
)


class ValidationLevel(Enum):
    """
Validation severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationType(Enum):
    """Types of validation checks."""

    STRUCTURE = "structure"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    level: ValidationLevel
    validation_type: ValidationType
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    suggestion: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class ValidationReport:
    """
Comprehensive validation report."""
    valid: bool
    results: List[ValidationResult]
    errors: List[ValidationResult]
    warnings: List[ValidationResult]
    info: List[ValidationResult]
    timestamp: datetime
    
    def __post_init__(self):
        self.errors = [r for r in self.results if r.level == ValidationLevel.ERROR or r.level == ValidationLevel.CRITICAL]
        self.warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        self.info = [r for r in self.results if r.level == ValidationLevel.INFO]
    
    def has_errors(self) -> bool:
        """
Check if report contains errors."""
        return len(self.errors) > 0
    
    def has_critical_errors(self) -> bool:
        """
Check if report contains critical errors."""
        return any(r.level == ValidationLevel.CRITICAL for r in self.errors)
    
    def get_error_summary(self) -> str:
        """
Get summary of errors."""
        if not self.errors:
            return "No errors found"
        
        return f"Found {len(self.errors)} error(s): " + "; ".join(r.message for r in self.errors)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "valid": self.valid,
            "timestamp": self.timestamp.isoformat(),
            "summary": {
                "total_checks": len(self.results),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "info": len(self.info)
            },
            "results": [
                {
                    "valid": r.valid,
                    "level": r.level.value,
                    "type": r.validation_type.value,
                    "message": r.message,
                    "field": r.field,
                    "value": str(r.value) if r.value is not None else None,
                    "suggestion": r.suggestion,
                    "error_code": r.error_code
                }
                for r in self.results
            ]
        }


class WorkflowValidator:
    """Comprehensive validator for workflow components."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("workflow.validator")
        
        # Validation rules
        self.custom_validators: Dict[str, Callable] = {}
        self.validation_rules: Dict[str, List[Callable]] = {}
        
        # Configuration limits
        self.max_pipeline_steps = self.config.get("max_pipeline_steps", 100)
        self.max_dependencies_per_step = self.config.get("max_dependencies_per_step", 10)
        self.max_workflow_duration = self.config.get("max_workflow_duration", 86400)  # 24 hours
        self.max_parallel_steps = self.config.get("max_parallel_steps", 20)
        
        # Setup default validation rules
        self._setup_default_rules()
    
    def validate_workflow_config(self, config: Dict[str, Any]) -> ValidationReport:
        """Validate complete workflow configuration."""
        results = []
        results.extend(self._validate_basic_structure(config, "workflow"))
        results.extend(self._validate_workflow_settings(config))
        results.extend(self._validate_resource_limits(config))
        results.extend(self._validate_security_settings(config))
        
        return self._create_report(results)
    
    def validate_pipeline_definition(self, pipeline_def: Dict[str, Any]) -> ValidationReport:
        """Validate pipeline definition."""
        results = []
        results.extend(self._validate_basic_structure(pipeline_def, "pipeline"))
        results.extend(self._validate_pipeline_steps(pipeline_def))
        results.extend(self._validate_step_dependencies(pipeline_def))
        results.extend(self._validate_pipeline_flow(pipeline_def))
        
        return self._create_report(results)
    
    def validate_schedule_expression(self, cron_expr: str) -> ValidationResult:
        """Validate cron schedule expression."""
        try:
            # Basic cron validation
            parts = cron_expr.split()
            
            if len(parts) != 5:
                return ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.CONFIGURATION,
                    message=f"Invalid cron expression format: {cron_expr}. Expected 5 parts (minute hour day month weekday)",
                    field="cron_expression",
                    value=cron_expr,
                    suggestion="Use format: 'minute hour day month weekday' (e.g., '0 9 * * MON')"
                )
            
            # Validate each part
            ranges = {
                0: (0, 59),    # minute
                1: (0, 23),    # hour
                2: (1, 31),    # day
                3: (1, 12),    # month
                4: (0, 7),     # weekday (0 and 7 are Sunday)
            }
            
            for i, part in enumerate(parts):
                if part == '*':
                    continue
                
                if '/' in part:
                    # Handle step values (e.g., "*/5")
                    base, step = part.split('/')
                    if base != '*':
                        if not self._validate_cron_value(base, ranges[i]):
                            return ValidationResult(
                                valid=False,
                                level=ValidationLevel.ERROR,
                                validation_type=ValidationType.CONFIGURATION,
                                message=f"Invalid cron value in position {i + 1}: {base}",
                                field="cron_expression",
                                value=cron_expr
                            )
                    
                    try:
                        step_val = int(step)
                        if step_val <= 0:
                            return ValidationResult(
                                valid=False,
                                level=ValidationLevel.ERROR,
                                validation_type=ValidationType.CONFIGURATION,
                                message=f"Invalid step value in cron expression: {step}",
                                field="cron_expression",
                                value=cron_expr
                            )
                    except ValueError:
                        return ValidationResult(
                            valid=False,
                            level=ValidationLevel.ERROR,
                            validation_type=ValidationType.CONFIGURATION,
                            message=f"Invalid step value in cron expression: {step}",
                            field="cron_expression",
                            value=cron_expr
                        )
                
                elif ',' in part:
                    # Handle lists (e.g., "1,3,5")
                    values = part.split(',')
                    for value in values:
                        if not self._validate_cron_value(value, ranges[i]):
                            return ValidationResult(
                                valid=False,
                                level=ValidationLevel.ERROR,
                                validation_type=ValidationType.CONFIGURATION,
                                message=f"Invalid cron value in position {i + 1}: {value}",
                                field="cron_expression",
                                value=cron_expr
                            )
                
                elif '-' in part:
                    # Handle ranges (e.g., "1-5")
                    start, end = part.split('-')
                    if not (self._validate_cron_value(start, ranges[i]) and 
                            self._validate_cron_value(end, ranges[i])):
                        return ValidationResult(
                            valid=False,
                            level=ValidationLevel.ERROR,
                            validation_type=ValidationType.CONFIGURATION,
                            message=f"Invalid cron range in position {i + 1}: {part}",
                            field="cron_expression",
                            value=cron_expr
                        )
                
                else:
                    # Handle single values
                    if not self._validate_cron_value(part, ranges[i]):
                        return ValidationResult(
                            valid=False,
                            level=ValidationLevel.ERROR,
                            validation_type=ValidationType.CONFIGURATION,
                            message=f"Invalid cron value in position {i + 1}: {part}",
                            field="cron_expression",
                            value=cron_expr
                        )
            
            return ValidationResult(
                valid=True,
                level=ValidationLevel.INFO,
                validation_type=ValidationType.CONFIGURATION,
                message="Valid cron expression",
                field="cron_expression",
                value=cron_expr
            )
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.CONFIGURATION,
                message=f"Error validating cron expression: {str(e)}",
                field="cron_expression",
                value=cron_expr
            )
    
    def validate_automation_rule(self, rule: Dict[str, Any]) -> ValidationReport:
        """Validate automation rule definition."""
        results = []
        results.extend(self._validate_basic_structure(rule, "automation_rule"))
        results.extend(self._validate_automation_triggers(rule))
        results.extend(self._validate_automation_actions(rule))
        results.extend(self._validate_automation_conditions(rule))
        
        return self._create_report(results)
    
    def validate_state_definition(self, state_def: Dict[str, Any]) -> ValidationReport:
        """Validate workflow state definition."""
        results = []
        results.extend(self._validate_basic_structure(state_def, "state"))
        results.extend(self._validate_state_transitions(state_def))
        results.extend(self._validate_state_data(state_def))
        
        return self._create_report(results)
    
    def validate_resource_requirements(self, requirements: Dict[str, Any]) -> ValidationReport:
        """Validate resource requirements."""
        results = []
        results.extend(self._validate_resource_values(requirements))
        results.extend(self._validate_resource_limits(requirements))
        results.extend(self._validate_resource_availability(requirements))
        
        return self._create_report(results)
    
    def add_custom_validator(self, name: str, validator_func: Callable) -> None:
        """
Add custom validation function."""
        self.custom_validators[name] = validator_func
        self.logger.debug(f"Added custom validator: {name}")
    
    def add_validation_rule(self, target_type: str, rule_func: Callable) -> None:
        """Add validation rule for specific target type."""
        if target_type not in self.validation_rules:
            self.validation_rules[target_type] = []
        
        self.validation_rules[target_type].append(rule_func)
        self.logger.debug(f"Added validation rule for {target_type}")
    
    def _setup_default_rules(self):
        """Setup default validation rules."""
        # Pipeline validation rules
        self.add_validation_rule("pipeline", self._check_pipeline_complexity)
        self.add_validation_rule("pipeline", self._check_circular_dependencies)
        self.add_validation_rule("pipeline", self._check_resource_usage)
        
        # Workflow validation rules
        self.add_validation_rule("workflow", self._check_workflow_timeout)
        self.add_validation_rule("workflow", self._check_parallel_limits)
        
        # Automation validation rules
        self.add_validation_rule("automation", self._check_trigger_conflicts)
        self.add_validation_rule("automation", self._check_action_permissions)
    
    def _validate_basic_structure(self, data: Dict[str, Any], data_type: str) -> List[ValidationResult]:
        """Validate basic structure requirements."""
        results = []
        
        # Check required fields based on type
        required_fields = self._get_required_fields(data_type)
        
        for field in required_fields:
            if field not in data:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Missing required field: {field}",
                    field=field,
                    error_code=f"MISSING_FIELD_{field.upper()}"
                ))
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Required field cannot be empty: {field}",
                    field=field,
                    value=data[field]
                ))
        
        # Check field types
        field_types = self._get_field_types(data_type)
        
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.STRUCTURE,
                        message=f"Invalid type for field {field}. Expected {expected_type.__name__}, got {type(data[field]).__name__}",
                        field=field,
                        value=data[field]
                    ))
        
        return results
    
    def _validate_workflow_settings(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate workflow-specific settings."""
        results = []
        
        # Validate timeout settings
        if "timeout" in config:
            timeout = config["timeout"]
            if isinstance(timeout, (int, float)):
                if timeout <= 0:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.CONFIGURATION,
                        message="Workflow timeout must be positive",
                        field="timeout",
                        value=timeout
                    ))
                elif timeout > self.max_workflow_duration:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.WARNING,
                        validation_type=ValidationType.PERFORMANCE,
                        message=f"Workflow timeout ({timeout}) exceeds recommended maximum ({self.max_workflow_duration})",
                        field="timeout",
                        value=timeout,
                        suggestion=f"Consider reducing timeout to {self.max_workflow_duration} seconds or less"
                    ))
        
        # Validate parallel execution settings
        if "max_parallel_steps" in config:
            parallel_steps = config["max_parallel_steps"]
            if isinstance(parallel_steps, int):
                if parallel_steps <= 0:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.CONFIGURATION,
                        message="max_parallel_steps must be positive",
                        field="max_parallel_steps",
                        value=parallel_steps
                    ))
                elif parallel_steps > self.max_parallel_steps:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.WARNING,
                        validation_type=ValidationType.PERFORMANCE,
                        message=f"High parallel step count may impact performance: {parallel_steps}",
                        field="max_parallel_steps",
                        value=parallel_steps,
                        suggestion=f"Consider reducing to {self.max_parallel_steps} or less"
                    ))
        
        return results
    
    def _validate_pipeline_steps(self, pipeline_def: Dict[str, Any]) -> List[ValidationResult]:
        """Validate pipeline step definitions."""
        results = []
        
        if "steps" not in pipeline_def:
            return results
        
        steps = pipeline_def["steps"]
        
        if not isinstance(steps, (list, dict)):
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="Pipeline steps must be a list or dictionary",
                field="steps",
                value=type(steps).__name__
            ))
            return results
        
        # Convert to consistent format for validation
        if isinstance(steps, dict):
            steps_list = [{"name": name, **step_def} for name, step_def in steps.items()]
        else:
            steps_list = steps
        
        if len(steps_list) > self.max_pipeline_steps:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.PERFORMANCE,
                message=f"Too many pipeline steps: {len(steps_list)} (max: {self.max_pipeline_steps})",
                field="steps",
                value=len(steps_list)
            ))
        
        step_names = set()
        
        for i, step in enumerate(steps_list):
            step_results = self._validate_single_step(step, i)
            results.extend(step_results)
            
            # Check for duplicate step names
            step_name = step.get("name", f"step_{i}")
            if step_name in step_names:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Duplicate step name: {step_name}",
                    field=f"steps[{i}].name",
                    value=step_name
                ))
            else:
                step_names.add(step_name)
        
        return results
    
    def _validate_single_step(self, step: Dict[str, Any], step_index: int) -> List[ValidationResult]:
        """Validate individual pipeline step."""
        results = []
        
        # Required step fields
        required_fields = ["name", "handler"]
        for field in required_fields:
            if field not in step:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Missing required field in step {step_index}: {field}",
                    field=f"steps[{step_index}].{field}"
                ))
        
        # Validate dependencies
        if "dependencies" in step:
            dependencies = step["dependencies"]
            if not isinstance(dependencies, list):
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Step dependencies must be a list in step {step_index}",
                    field=f"steps[{step_index}].dependencies",
                    value=type(dependencies).__name__
                ))
            elif len(dependencies) > self.max_dependencies_per_step:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.WARNING,
                    validation_type=ValidationType.PERFORMANCE,
                    message=f"Too many dependencies in step {step_index}: {len(dependencies)}",
                    field=f"steps[{step_index}].dependencies",
                    value=len(dependencies),
                    suggestion=f"Consider reducing dependencies to {self.max_dependencies_per_step} or less"
                ))
        
        # Validate retry policy
        if "retry_policy" in step:
            retry_results = self._validate_retry_policy(step["retry_policy"], step_index)
            results.extend(retry_results)
        
        return results
    
    def _validate_step_dependencies(self, pipeline_def: Dict[str, Any]) -> List[ValidationResult]:
        """Validate step dependency relationships."""
        results = []
        
        if "steps" not in pipeline_def:
            return results
        
        steps = pipeline_def["steps"]
        
        # Build step name mapping
        if isinstance(steps, dict):
            step_names = set(steps.keys())
            step_deps = {name: step.get("dependencies", []) for name, step in steps.items()}
        else:
            step_names = {step.get("name", f"step_{i}") for i, step in enumerate(steps)}
            step_deps = {
                step.get("name", f"step_{i}"): step.get("dependencies", [])
                for i, step in enumerate(steps)
            }
        
        # Check for invalid dependency references
        for step_name, dependencies in step_deps.items():
            for dep in dependencies:
                if dep not in step_names:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.DEPENDENCY,
                        message=f"Step '{step_name}' depends on non-existent step: {dep}",
                        field=f"steps.{step_name}.dependencies",
                        value=dep
                    ))
        
        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies(step_deps)
        for cycle in circular_deps:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.DEPENDENCY,
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
                field="steps",
                value=cycle
            ))
        
        return results
    
    def _validate_pipeline_flow(self, pipeline_def: Dict[str, Any]) -> List[ValidationResult]:
        """Validate overall pipeline flow and logic."""
        results = []
        
        # Check for isolated steps (no dependencies and no dependents)
        if "steps" in pipeline_def:
            steps = pipeline_def["steps"]
            
            if isinstance(steps, dict):
                all_dependencies = set()
                for step_def in steps.values():
                    all_dependencies.update(step_def.get("dependencies", []))
                
                for step_name in steps.keys():
                    has_dependencies = bool(steps[step_name].get("dependencies"))
                    has_dependents = step_name in all_dependencies
                    
                    if not has_dependencies and not has_dependents:
                        results.append(ValidationResult(
                            valid=True,
                            level=ValidationLevel.INFO,
                            validation_type=ValidationType.STRUCTURE,
                            message=f"Step '{step_name}' appears to be isolated (no dependencies or dependents)",
                            field=f"steps.{step_name}",
                            suggestion="Verify this step is correctly integrated into the pipeline flow"
                        ))
        
        return results
    
    def _validate_automation_triggers(self, rule: Dict[str, Any]) -> List[ValidationResult]:
        """Validate automation trigger configuration."""
        results = []
        
        if "triggers" not in rule:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="Automation rule must have triggers",
                field="triggers"
            ))
            return results
        
        triggers = rule["triggers"]
        if not isinstance(triggers, list):
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="Triggers must be a list",
                field="triggers",
                value=type(triggers).__name__
            ))
            return results
        
        if not triggers:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="At least one trigger must be defined",
                field="triggers"
            ))
        
        for i, trigger in enumerate(triggers):
            if "type" not in trigger:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Trigger {i} missing type",
                    field=f"triggers[{i}].type"
                ))
            
            trigger_type = trigger.get("type")
            if trigger_type == "schedule" and "schedule" in trigger:
                cron_result = self.validate_schedule_expression(trigger["schedule"])
                if not cron_result.valid:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.CONFIGURATION,
                        message=f"Invalid schedule in trigger {i}: {cron_result.message}",
                        field=f"triggers[{i}].schedule",
                        value=trigger["schedule"]
                    ))
        
        return results
    
    def _validate_automation_actions(self, rule: Dict[str, Any]) -> List[ValidationResult]:
        """Validate automation action configuration."""
        results = []
        
        if "actions" not in rule:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="Automation rule must have actions",
                field="actions"
            ))
            return results
        
        actions = rule["actions"]
        if not isinstance(actions, list):
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="Actions must be a list",
                field="actions",
                value=type(actions).__name__
            ))
            return results
        
        if not actions:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="At least one action must be defined",
                field="actions"
            ))
        
        for i, action in enumerate(actions):
            if "type" not in action:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message=f"Action {i} missing type",
                    field=f"actions[{i}].type"
                ))
        
        return results
    
    def _validate_automation_conditions(self, rule: Dict[str, Any]) -> List[ValidationResult]:
        """Validate automation condition logic."""
        results = []
        
        if "conditions" in rule:
            conditions = rule["conditions"]
            
            if not isinstance(conditions, list):
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message="Conditions must be a list",
                    field="conditions",
                    value=type(conditions).__name__
                ))
                return results
            
            for i, condition in enumerate(conditions):
                if not isinstance(condition, dict):
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.STRUCTURE,
                        message=f"Condition {i} must be a dictionary",
                        field=f"conditions[{i}]",
                        value=type(condition).__name__
                    ))
                    continue
                
                if "field" not in condition:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.STRUCTURE,
                        message=f"Condition {i} missing field",
                        field=f"conditions[{i}].field"
                    ))
                
                if "operator" not in condition:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.STRUCTURE,
                        message=f"Condition {i} missing operator",
                        field=f"conditions[{i}].operator"
                    ))
        
        return results
    
    def _validate_state_transitions(self, state_def: Dict[str, Any]) -> List[ValidationResult]:
        """Validate state transition definitions."""
        results = []
        
        if "transitions" in state_def:
            transitions = state_def["transitions"]
            
            if not isinstance(transitions, list):
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message="State transitions must be a list",
                    field="transitions",
                    value=type(transitions).__name__
                ))
                return results
            
            for i, transition in enumerate(transitions):
                required_fields = ["from", "to", "trigger"]
                for field in required_fields:
                    if field not in transition:
                        results.append(ValidationResult(
                            valid=False,
                            level=ValidationLevel.ERROR,
                            validation_type=ValidationType.STRUCTURE,
                            message=f"Transition {i} missing required field: {field}",
                            field=f"transitions[{i}].{field}"
                        ))
        
        return results
    
    def _validate_state_data(self, state_def: Dict[str, Any]) -> List[ValidationResult]:
        """Validate state data structure."""
        results = []
        
        if "initial_state" not in state_def:
            results.append(ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=ValidationType.STRUCTURE,
                message="State definition must have initial_state",
                field="initial_state"
            ))
        
        if "states" in state_def:
            states = state_def["states"]
            if not isinstance(states, list):
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.STRUCTURE,
                    message="States must be a list",
                    field="states",
                    value=type(states).__name__
                ))
        
        return results
    
    def _validate_resource_values(self, requirements: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resource requirement values."""
        results = []
        
        for resource_type, value in requirements.items():
            if isinstance(value, (int, float)):
                if value < 0:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.RESOURCE,
                        message=f"Resource requirement cannot be negative: {resource_type} = {value}",
                        field=resource_type,
                        value=value
                    ))
            elif not isinstance(value, str):
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.RESOURCE,
                    message=f"Invalid resource requirement type: {resource_type}",
                    field=resource_type,
                    value=value
                ))
        
        return results
    
    def _validate_resource_limits(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resource limit configurations."""
        results = []
        
        # Check memory limits
        if "memory" in config:
            memory = config["memory"]
            if isinstance(memory, str):
                # Parse memory string (e.g., "1GB", "512MB")
                if not re.match(r'^\d+(\.\d+)?[KMGT]?B?$', memory.upper()):
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.RESOURCE,
                        message=f"Invalid memory format: {memory}",
                        field="memory",
                        value=memory,
                        suggestion="Use format like '1GB', '512MB', '2048KB'"
                    ))
        
        # Check CPU limits
        if "cpu" in config:
            cpu = config["cpu"]
            if isinstance(cpu, (int, float)):
                if cpu <= 0:
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.RESOURCE,
                        message=f"CPU limit must be positive: {cpu}",
                        field="cpu",
                        value=cpu
                    ))
                elif cpu > 16:  # Reasonable upper limit
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.WARNING,
                        validation_type=ValidationType.RESOURCE,
                        message=f"High CPU limit may not be sustainable: {cpu}",
                        field="cpu",
                        value=cpu,
                        suggestion="Consider reducing CPU limit to 16 or less"
                    ))
        
        return results
    
    def _validate_resource_availability(self, requirements: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resource availability (placeholder for actual resource checks)."""
        results = []
        
        # This would typically check against actual system resources
        # For now, just validate the structure
        
        if "storage" in requirements:
            storage = requirements["storage"]
            if isinstance(storage, str):
                if not re.match(r'^\d+(\.\d+)?[KMGT]?B?$', storage.upper()):
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.RESOURCE,
                        message=f"Invalid storage format: {storage}",
                        field="storage",
                        value=storage
                    ))
        
        return results
    
    def _validate_retry_policy(self, retry_policy: Dict[str, Any], step_index: int) -> List[ValidationResult]:
        """Validate retry policy configuration."""
        results = []
        
        if "max_retries" in retry_policy:
            max_retries = retry_policy["max_retries"]
            if not isinstance(max_retries, int) or max_retries < 0:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.CONFIGURATION,
                    message=f"Invalid max_retries in step {step_index}: {max_retries}",
                    field=f"steps[{step_index}].retry_policy.max_retries",
                    value=max_retries
                ))
            elif max_retries > 10:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.WARNING,
                    validation_type=ValidationType.PERFORMANCE,
                    message=f"High retry count in step {step_index}: {max_retries}",
                    field=f"steps[{step_index}].retry_policy.max_retries",
                    value=max_retries,
                    suggestion="Consider reducing max_retries to 10 or less"
                ))
        
        if "delay" in retry_policy:
            delay = retry_policy["delay"]
            if not isinstance(delay, (int, float)) or delay < 0:
                results.append(ValidationResult(
                    valid=False,
                    level=ValidationLevel.ERROR,
                    validation_type=ValidationType.CONFIGURATION,
                    message=f"Invalid retry delay in step {step_index}: {delay}",
                    field=f"steps[{step_index}].retry_policy.delay",
                    value=delay
                ))
        
        return results
    
    def _validate_security_settings(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate security-related settings."""
        results = []
        
        if "security" in config:
            security = config["security"]
            
            if "allowed_actions" in security:
                allowed_actions = security["allowed_actions"]
                if not isinstance(allowed_actions, list):
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.SECURITY,
                        message="allowed_actions must be a list",
                        field="security.allowed_actions",
                        value=type(allowed_actions).__name__
                    ))
            
            if "permissions" in security:
                permissions = security["permissions"]
                if not isinstance(permissions, dict):
                    results.append(ValidationResult(
                        valid=False,
                        level=ValidationLevel.ERROR,
                        validation_type=ValidationType.SECURITY,
                        message="permissions must be a dictionary",
                        field="security.permissions",
                        value=type(permissions).__name__
                    ))
        
        return results
    
    def _create_report(self, results: List[ValidationResult]) -> ValidationReport:
        """Create validation report from results."""
        valid = not any(r.level in [ValidationLevel.ERROR, ValidationLevel.CRITICAL] for r in results)
        
        return ValidationReport(
            valid=valid,
            results=results,
            timestamp=datetime.utcnow()
        )
    
    def _get_required_fields(self, data_type: str) -> List[str]:
        """
Get required fields for data type."""
        field_requirements = {
            "workflow": ["name", "steps"],
            "pipeline": ["steps"],
            "automation_rule": ["name", "triggers", "actions"],
            "state": ["initial_state", "states"]
        }
        
        return field_requirements.get(data_type, [])
    
    def _get_field_types(self, data_type: str) -> Dict[str, type]:
        """Get expected field types for data type."""
        type_requirements = {
            "workflow": {
                "name": str,
                "steps": (list, dict),
                "timeout": (int, float),
                "max_parallel_steps": int
            },
            "pipeline": {
                "steps": (list, dict),
                "name": str
            },
            "automation_rule": {
                "name": str,
                "triggers": list,
                "actions": list,
                "conditions": list
            },
            "state": {
                "initial_state": str,
                "states": list,
                "transitions": list
            }
        }
        
        return type_requirements.get(data_type, {})
    
    def _validate_cron_value(self, value: str, range_tuple: tuple) -> bool:
        """Validate individual cron value against range."""
        try:
            if value == '*':
                return True
            
            # Handle special weekday names
            if range_tuple == (0, 7):  # weekday
                weekday_names = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
                if value.upper() in weekday_names:
                    return True
            
            # Handle numeric values
            num_value = int(value)
            return range_tuple[0] <= num_value <= range_tuple[1]
            
        except ValueError:
            return False
    
    def _find_circular_dependencies(self, step_deps: Dict[str, List[str]]) -> List[List[str]]:
        """
Find circular dependencies in step definitions."""
        def dfs(node, path, visited):
            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                return [path[cycle_start:] + [node]]
            
            if node in visited:
                return []
            
            visited.add(node)
            path.append(node)
            
            cycles = []
            for dep in step_deps.get(node, []):
                cycles.extend(dfs(dep, path[:], visited))
            
            return cycles
        
        all_cycles = []
        visited = set()
        
        for step_name in step_deps:
            if step_name not in visited:
                cycles = dfs(step_name, [], visited)
                all_cycles.extend(cycles)
        
        return all_cycles
    
    # Default validation rule implementations
    def _check_pipeline_complexity(self, pipeline_def: Dict[str, Any]) -> List[ValidationResult]:
        """
Check pipeline complexity metrics."""
        results = []
        
        if "steps" in pipeline_def:
            steps = pipeline_def["steps"]
            step_count = len(steps) if isinstance(steps, (list, dict)) else 0
            
            if step_count > 50:
                results.append(ValidationResult(
                    valid=True,
                    level=ValidationLevel.WARNING,
                    validation_type=ValidationType.PERFORMANCE,
                    message=f"High pipeline complexity: {step_count} steps",
                    field="steps",
                    value=step_count,
                    suggestion="Consider breaking down into smaller pipelines"
                ))
        
        return results
    
    def _check_circular_dependencies(self, pipeline_def: Dict[str, Any]) -> List[ValidationResult]:
        """Check for circular dependencies in pipeline."""
        return []  # Already handled in _validate_step_dependencies
    
    def _check_resource_usage(self, pipeline_def: Dict[str, Any]) -> List[ValidationResult]:
        """
Check resource usage patterns."""
        results = []
        
        # This would analyze resource requirements across pipeline steps
        # Placeholder for actual resource analysis
        
        return results
    
    def _check_workflow_timeout(self, workflow_def: Dict[str, Any]) -> List[ValidationResult]:
        """
Check workflow timeout configuration."""
        return []  # Already handled in _validate_workflow_settings
    
    def _check_parallel_limits(self, workflow_def: Dict[str, Any]) -> List[ValidationResult]:
        """
Check parallel execution limits."""
        return []  # Already handled in _validate_workflow_settings
    
    def _check_trigger_conflicts(self, automation_def: Dict[str, Any]) -> List[ValidationResult]:
        """
Check for automation trigger conflicts."""
        results = []
        
        # This would check for conflicting automation triggers
        # Placeholder for actual conflict detection
        
        return results
    
    def _check_action_permissions(self, automation_def: Dict[str, Any]) -> List[ValidationResult]:
        """
Check automation action permissions."""
        results = []
        
        # This would validate that automation actions have proper permissions
        # Placeholder for actual permission checks
        
        return results
