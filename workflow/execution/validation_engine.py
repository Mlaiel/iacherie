"""
🔥 ENTERPRISE VALIDATION ENGINE - AINFLUE PLATFORM
Ultra-advanced validation and exception handling system
Consolidates: validators.py + exceptions.py
"""

from typing import Dict, Any, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from datetime import datetime, timedelta
import logging
import asyncio
import uuid


class WorkflowErrorCode(Enum):
    """Standardized workflow error codes."""
    # General workflow errors (1000-1099)
    WORKFLOW_INITIALIZATION_FAILED = "WF1000"
    WORKFLOW_EXECUTION_FAILED = "WF1001"
    WORKFLOW_TIMEOUT = "WF1002"
    WORKFLOW_CANCELLED = "WF1003"
    WORKFLOW_NOT_FOUND = "WF1004"
    WORKFLOW_INVALID_STATE = "WF1005"
    
    # Pipeline errors (1100-1199)
    PIPELINE_CREATION_FAILED = "WF1100"
    PIPELINE_STEP_FAILED = "WF1101"
    PIPELINE_DEPENDENCY_ERROR = "WF1102"
    PIPELINE_DEADLOCK = "WF1103"
    PIPELINE_RESOURCE_EXHAUSTED = "WF1104"
    PIPELINE_VALIDATION_ERROR = "WF1105"
    
    # Scheduling errors (1200-1299)
    SCHEDULE_INVALID_CRON = "WF1200"
    SCHEDULE_TASK_NOT_FOUND = "WF1201"
    SCHEDULE_EXECUTION_FAILED = "WF1202"
    SCHEDULE_CONFLICT = "WF1203"
    SCHEDULE_RESOURCE_BUSY = "WF1204"
    
    # State management errors (1300-1399)
    STATE_CORRUPTION = "WF1300"
    STATE_LOCK_TIMEOUT = "WF1301"
    STATE_SERIALIZATION_ERROR = "WF1302"
    STATE_PERSISTENCE_FAILED = "WF1303"
    STATE_RECOVERY_FAILED = "WF1304"
    
    # Automation errors (1400-1499)
    AUTOMATION_TRIGGER_FAILED = "WF1400"
    AUTOMATION_ACTION_FAILED = "WF1401"
    AUTOMATION_CONDITION_ERROR = "WF1402"
    AUTOMATION_RULE_CONFLICT = "WF1403"
    
    # Validation errors (1500-1599)
    VALIDATION_SCHEMA_ERROR = "WF1500"
    VALIDATION_TYPE_ERROR = "WF1501"
    VALIDATION_CONSTRAINT_ERROR = "WF1502"
    VALIDATION_DEPENDENCY_ERROR = "WF1503"
    VALIDATION_SECURITY_ERROR = "WF1504"
    
    # Integration errors (1600-1699)
    INTEGRATION_CONNECTION_FAILED = "WF1600"
    INTEGRATION_AUTH_FAILED = "WF1601"
    INTEGRATION_API_ERROR = "WF1602"
    INTEGRATION_TIMEOUT = "WF1603"
    INTEGRATION_DATA_ERROR = "WF1604"


class ValidationLevel(Enum):
    """Validation severity levels."""
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
    DATA_INTEGRITY = "data_integrity"
    BUSINESS_RULES = "business_rules"


# EXCEPTION CLASSES

class WorkflowException(Exception):
    """Base exception for workflow-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = WorkflowErrorCode.WORKFLOW_EXECUTION_FAILED,
        details: Dict[str, Any] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            'error_code': self.error_code.value,
            'message': str(self),
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'cause': str(self.cause) if self.cause else None
        }


class PipelineException(WorkflowException):
    """Exception for pipeline-related errors."""
    
    def __init__(self, message: str, error_code: WorkflowErrorCode = WorkflowErrorCode.PIPELINE_STEP_FAILED, **kwargs):
        super().__init__(message, error_code, **kwargs)


class SchedulingException(WorkflowException):
    """Exception for scheduling-related errors."""
    
    def __init__(self, message: str, error_code: WorkflowErrorCode = WorkflowErrorCode.SCHEDULE_EXECUTION_FAILED, **kwargs):
        super().__init__(message, error_code, **kwargs)


class StateException(WorkflowException):
    """Exception for state management errors."""
    
    def __init__(self, message: str, error_code: WorkflowErrorCode = WorkflowErrorCode.STATE_CORRUPTION, **kwargs):
        super().__init__(message, error_code, **kwargs)


class ValidationException(WorkflowException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, error_code: WorkflowErrorCode = WorkflowErrorCode.VALIDATION_SCHEMA_ERROR, **kwargs):
        super().__init__(message, error_code, **kwargs)


class IntegrationException(WorkflowException):
    """Exception for integration errors."""
    
    def __init__(self, message: str, error_code: WorkflowErrorCode = WorkflowErrorCode.INTEGRATION_CONNECTION_FAILED, **kwargs):
        super().__init__(message, error_code, **kwargs)


# VALIDATION SYSTEM

@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    level: ValidationLevel
    validation_type: ValidationType
    message: str
    field: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationRule:
    """Validation rule definition."""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    validation_type: ValidationType = ValidationType.STRUCTURE
    level: ValidationLevel = ValidationLevel.ERROR
    validator_func: Callable = None
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationContext:
    """Context for validation operations."""
    target_object: Any = None
    validation_scope: str = "full"
    strict_mode: bool = False
    custom_rules: List[ValidationRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidationEngine:
    """
    🔥 ENTERPRISE VALIDATION ENGINE
    
    Ultra-advanced validation system with:
    - Comprehensive rule-based validation
    - Multi-level validation (info, warning, error, critical)
    - Custom validation rules
    - Schema validation
    - Business rule validation
    - Security validation
    - Performance validation
    - Dependency validation
    """
    
    def __init__(self):
        """Initialize enterprise validation engine."""
        self.validation_rules: Dict[ValidationType, List[ValidationRule]] = {
            validation_type: [] for validation_type in ValidationType
        }
        self.validation_cache: Dict[str, ValidationResult] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize built-in rules
        self._initialize_builtin_rules()
    
    def _initialize_builtin_rules(self):
        """Initialize built-in validation rules."""
        # Structure validation rules
        self.add_validation_rule(ValidationRule(
            name="required_fields",
            description="Check for required fields presence",
            validation_type=ValidationType.STRUCTURE,
            level=ValidationLevel.ERROR,
            validator_func=self._validate_required_fields
        ))
        
        self.add_validation_rule(ValidationRule(
            name="data_types",
            description="Validate data types",
            validation_type=ValidationType.STRUCTURE,
            level=ValidationLevel.ERROR,
            validator_func=self._validate_data_types
        ))
        
        # Configuration validation rules
        self.add_validation_rule(ValidationRule(
            name="config_schema",
            description="Validate configuration schema",
            validation_type=ValidationType.CONFIGURATION,
            level=ValidationLevel.ERROR,
            validator_func=self._validate_configuration_schema
        ))
        
        # Security validation rules
        self.add_validation_rule(ValidationRule(
            name="security_constraints",
            description="Check security constraints",
            validation_type=ValidationType.SECURITY,
            level=ValidationLevel.CRITICAL,
            validator_func=self._validate_security_constraints
        ))
        
        # Performance validation rules
        self.add_validation_rule(ValidationRule(
            name="performance_limits",
            description="Check performance limits",
            validation_type=ValidationType.PERFORMANCE,
            level=ValidationLevel.WARNING,
            validator_func=self._validate_performance_limits
        ))
        
        # Dependency validation rules
        self.add_validation_rule(ValidationRule(
            name="dependency_graph",
            description="Validate dependency relationships",
            validation_type=ValidationType.DEPENDENCY,
            level=ValidationLevel.ERROR,
            validator_func=self._validate_dependencies
        ))
    
    def add_validation_rule(self, rule: ValidationRule):
        """Add a validation rule to the engine."""
        self.validation_rules[rule.validation_type].append(rule)
        self.logger.debug(f"Added validation rule: {rule.name}")
    
    def remove_validation_rule(self, rule_id: str) -> bool:
        """Remove a validation rule by ID."""
        for validation_type, rules in self.validation_rules.items():
            for i, rule in enumerate(rules):
                if rule.rule_id == rule_id:
                    del rules[i]
                    self.logger.debug(f"Removed validation rule: {rule.name}")
                    return True
        return False
    
    async def validate(
        self,
        target: Any,
        context: Optional[ValidationContext] = None,
        validation_types: Optional[List[ValidationType]] = None
    ) -> List[ValidationResult]:
        """
        Perform comprehensive validation on target object.
        
        Args:
            target: Object to validate
            context: Validation context
            validation_types: Specific validation types to run
            
        Returns:
            List of validation results
        """
        if context is None:
            context = ValidationContext(target_object=target)
        
        if validation_types is None:
            validation_types = list(ValidationType)
        
        results = []
        
        # Run validation for each type
        for validation_type in validation_types:
            type_results = await self._validate_type(target, context, validation_type)
            results.extend(type_results)
        
        # Run custom rules if provided
        if context.custom_rules:
            for rule in context.custom_rules:
                if rule.enabled:
                    result = await self._execute_validation_rule(target, context, rule)
                    if result:
                        results.append(result)
        
        # Sort results by severity
        results.sort(key=lambda x: self._get_severity_weight(x.level), reverse=True)
        
        return results
    
    async def _validate_type(
        self,
        target: Any,
        context: ValidationContext,
        validation_type: ValidationType
    ) -> List[ValidationResult]:
        """Validate using rules of specific type."""
        results = []
        rules = self.validation_rules.get(validation_type, [])
        
        for rule in rules:
            if rule.enabled:
                result = await self._execute_validation_rule(target, context, rule)
                if result:
                    results.append(result)
        
        return results
    
    async def _execute_validation_rule(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Execute a single validation rule."""
        try:
            if asyncio.iscoroutinefunction(rule.validator_func):
                return await rule.validator_func(target, context, rule)
            else:
                return rule.validator_func(target, context, rule)
        except Exception as e:
            self.logger.error(f"Validation rule {rule.name} failed: {e}")
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                validation_type=rule.validation_type,
                message=f"Validation rule execution failed: {str(e)}",
                details={'rule_name': rule.name, 'error': str(e)}
            )
    
    def _get_severity_weight(self, level: ValidationLevel) -> int:
        """Get numeric weight for severity level."""
        weights = {
            ValidationLevel.CRITICAL: 4,
            ValidationLevel.ERROR: 3,
            ValidationLevel.WARNING: 2,
            ValidationLevel.INFO: 1
        }
        return weights.get(level, 0)
    
    # BUILT-IN VALIDATION FUNCTIONS
    
    def _validate_required_fields(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate required fields are present."""
        required_fields = rule.parameters.get('required_fields', [])
        
        if not required_fields:
            return None
        
        missing_fields = []
        
        if isinstance(target, dict):
            for field in required_fields:
                if field not in target or target[field] is None:
                    missing_fields.append(field)
        elif hasattr(target, '__dict__'):
            for field in required_fields:
                if not hasattr(target, field) or getattr(target, field) is None:
                    missing_fields.append(field)
        
        if missing_fields:
            return ValidationResult(
                valid=False,
                level=rule.level,
                validation_type=rule.validation_type,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                details={'missing_fields': missing_fields},
                suggestions=[f"Provide value for field: {field}" for field in missing_fields]
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            validation_type=rule.validation_type,
            message="All required fields are present"
        )
    
    def _validate_data_types(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate data types."""
        type_constraints = rule.parameters.get('type_constraints', {})
        
        if not type_constraints:
            return None
        
        type_errors = []
        
        if isinstance(target, dict):
            for field, expected_type in type_constraints.items():
                if field in target:
                    value = target[field]
                    if value is not None and not isinstance(value, expected_type):
                        type_errors.append(f"{field}: expected {expected_type.__name__}, got {type(value).__name__}")
        
        if type_errors:
            return ValidationResult(
                valid=False,
                level=rule.level,
                validation_type=rule.validation_type,
                message=f"Type validation errors: {'; '.join(type_errors)}",
                details={'type_errors': type_errors}
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            validation_type=rule.validation_type,
            message="Data types are valid"
        )
    
    def _validate_configuration_schema(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate configuration schema."""
        schema = rule.parameters.get('schema', {})
        
        if not schema:
            return ValidationResult(
                valid=True,
                level=ValidationLevel.INFO,
                validation_type=rule.validation_type,
                message="No schema defined for validation"
            )
        
        # Basic schema validation
        errors = []
        
        if isinstance(target, dict) and isinstance(schema, dict):
            for key, constraints in schema.items():
                if key in target:
                    value = target[key]
                    
                    # Check type constraint
                    if 'type' in constraints:
                        expected_type = constraints['type']
                        if not isinstance(value, expected_type):
                            errors.append(f"{key}: expected {expected_type.__name__}")
                    
                    # Check value constraints
                    if 'min' in constraints and isinstance(value, (int, float)):
                        if value < constraints['min']:
                            errors.append(f"{key}: value {value} below minimum {constraints['min']}")
                    
                    if 'max' in constraints and isinstance(value, (int, float)):
                        if value > constraints['max']:
                            errors.append(f"{key}: value {value} above maximum {constraints['max']}")
                    
                    if 'pattern' in constraints and isinstance(value, str):
                        pattern = constraints['pattern']
                        if not re.match(pattern, value):
                            errors.append(f"{key}: value does not match pattern {pattern}")
        
        if errors:
            return ValidationResult(
                valid=False,
                level=rule.level,
                validation_type=rule.validation_type,
                message=f"Schema validation errors: {'; '.join(errors)}",
                details={'schema_errors': errors}
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            validation_type=rule.validation_type,
            message="Configuration schema is valid"
        )
    
    def _validate_security_constraints(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate security constraints."""
        security_issues = []
        
        if isinstance(target, dict):
            # Check for sensitive data in plain text
            sensitive_fields = ['password', 'secret', 'token', 'key', 'credential']
            for field, value in target.items():
                if any(sensitive in field.lower() for sensitive in sensitive_fields):
                    if isinstance(value, str) and len(value) > 0:
                        # Check if value looks like plain text (simple heuristic)
                        if not (value.startswith('$') or len(value) > 32):
                            security_issues.append(f"Potential plain text sensitive data in field: {field}")
            
            # Check for SQL injection patterns
            if 'query' in target or 'sql' in target:
                query_field = target.get('query') or target.get('sql', '')
                if isinstance(query_field, str):
                    dangerous_patterns = ['DROP TABLE', 'DELETE FROM', '; --', 'UNION SELECT']
                    for pattern in dangerous_patterns:
                        if pattern.upper() in query_field.upper():
                            security_issues.append(f"Potential SQL injection pattern detected: {pattern}")
        
        if security_issues:
            return ValidationResult(
                valid=False,
                level=rule.level,
                validation_type=rule.validation_type,
                message=f"Security validation failed: {'; '.join(security_issues)}",
                details={'security_issues': security_issues},
                suggestions=[
                    "Encrypt sensitive data",
                    "Use parameterized queries",
                    "Implement input sanitization"
                ]
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            validation_type=rule.validation_type,
            message="Security constraints are satisfied"
        )
    
    def _validate_performance_limits(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate performance limits."""
        performance_issues = []
        limits = rule.parameters.get('limits', {})
        
        if isinstance(target, dict):
            # Check timeout values
            timeout_fields = ['timeout', 'timeout_seconds', 'execution_timeout']
            for field in timeout_fields:
                if field in target:
                    timeout_value = target[field]
                    if isinstance(timeout_value, (int, float)):
                        max_timeout = limits.get('max_timeout', 300)
                        if timeout_value > max_timeout:
                            performance_issues.append(f"Timeout value {timeout_value}s exceeds limit {max_timeout}s")
            
            # Check batch sizes
            batch_fields = ['batch_size', 'chunk_size', 'page_size']
            for field in batch_fields:
                if field in target:
                    batch_value = target[field]
                    if isinstance(batch_value, int):
                        max_batch = limits.get('max_batch_size', 1000)
                        if batch_value > max_batch:
                            performance_issues.append(f"Batch size {batch_value} exceeds limit {max_batch}")
            
            # Check concurrency limits
            concurrency_fields = ['max_concurrent', 'parallel_workers', 'thread_count']
            for field in concurrency_fields:
                if field in target:
                    concurrency_value = target[field]
                    if isinstance(concurrency_value, int):
                        max_concurrency = limits.get('max_concurrency', 50)
                        if concurrency_value > max_concurrency:
                            performance_issues.append(f"Concurrency {concurrency_value} exceeds limit {max_concurrency}")
        
        if performance_issues:
            return ValidationResult(
                valid=False,
                level=rule.level,
                validation_type=rule.validation_type,
                message=f"Performance validation issues: {'; '.join(performance_issues)}",
                details={'performance_issues': performance_issues},
                suggestions=[
                    "Reduce timeout values",
                    "Use smaller batch sizes",
                    "Limit concurrency"
                ]
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            validation_type=rule.validation_type,
            message="Performance limits are within acceptable ranges"
        )
    
    def _validate_dependencies(
        self,
        target: Any,
        context: ValidationContext,
        rule: ValidationRule
    ) -> Optional[ValidationResult]:
        """Validate dependency relationships."""
        dependency_issues = []
        
        if isinstance(target, dict) and 'dependencies' in target:
            dependencies = target['dependencies']
            
            if isinstance(dependencies, list):
                # Check for circular dependencies (simple check)
                dependency_graph = {}
                for dep in dependencies:
                    if isinstance(dep, dict) and 'from' in dep and 'to' in dep:
                        from_node = dep['from']
                        to_node = dep['to']
                        
                        if from_node not in dependency_graph:
                            dependency_graph[from_node] = []
                        dependency_graph[from_node].append(to_node)
                
                # Simple cycle detection
                visited = set()
                rec_stack = set()
                
                def has_cycle(node):
                    if node in rec_stack:
                        return True
                    if node in visited:
                        return False
                    
                    visited.add(node)
                    rec_stack.add(node)
                    
                    for neighbor in dependency_graph.get(node, []):
                        if has_cycle(neighbor):
                            return True
                    
                    rec_stack.remove(node)
                    return False
                
                for node in dependency_graph:
                    if has_cycle(node):
                        dependency_issues.append(f"Circular dependency detected involving: {node}")
                        break
        
        if dependency_issues:
            return ValidationResult(
                valid=False,
                level=rule.level,
                validation_type=rule.validation_type,
                message=f"Dependency validation failed: {'; '.join(dependency_issues)}",
                details={'dependency_issues': dependency_issues},
                suggestions=["Remove circular dependencies", "Restructure dependency graph"]
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            validation_type=rule.validation_type,
            message="Dependencies are valid"
        )
    
    # VALIDATION UTILITIES
    
    def validate_workflow_definition(self, workflow_def: Dict[str, Any]) -> List[ValidationResult]:
        """Validate workflow definition."""
        context = ValidationContext(
            target_object=workflow_def,
            validation_scope="workflow_definition",
            strict_mode=True
        )
        
        # Add workflow-specific rules
        workflow_rules = [
            ValidationRule(
                name="workflow_required_fields",
                validation_type=ValidationType.STRUCTURE,
                level=ValidationLevel.ERROR,
                validator_func=self._validate_required_fields,
                parameters={'required_fields': ['workflow_id', 'steps']}
            )
        ]
        
        context.custom_rules = workflow_rules
        
        return asyncio.run(self.validate(workflow_def, context))
    
    def validate_pipeline_configuration(self, pipeline_config: Dict[str, Any]) -> List[ValidationResult]:
        """Validate pipeline configuration."""
        context = ValidationContext(
            target_object=pipeline_config,
            validation_scope="pipeline_configuration"
        )
        
        pipeline_rules = [
            ValidationRule(
                name="pipeline_performance_limits",
                validation_type=ValidationType.PERFORMANCE,
                level=ValidationLevel.WARNING,
                validator_func=self._validate_performance_limits,
                parameters={
                    'limits': {
                        'max_timeout': 600,
                        'max_batch_size': 500,
                        'max_concurrency': 20
                    }
                }
            )
        ]
        
        context.custom_rules = pipeline_rules
        
        return asyncio.run(self.validate(pipeline_config, context))
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get validation summary statistics."""
        summary = {
            'total_checks': len(results),
            'passed': 0,
            'failed': 0,
            'by_level': {level.value: 0 for level in ValidationLevel},
            'by_type': {vtype.value: 0 for vtype in ValidationType},
            'critical_issues': 0,
            'overall_status': 'unknown'
        }
        
        for result in results:
            if result.valid:
                summary['passed'] += 1
            else:
                summary['failed'] += 1
            
            summary['by_level'][result.level.value] += 1
            summary['by_type'][result.validation_type.value] += 1
            
            if result.level == ValidationLevel.CRITICAL:
                summary['critical_issues'] += 1
        
        # Determine overall status
        if summary['critical_issues'] > 0:
            summary['overall_status'] = 'critical'
        elif summary['failed'] > 0:
            summary['overall_status'] = 'failed'
        else:
            summary['overall_status'] = 'passed'
        
        return summary


# ========== CONSOLIDATED WORKFLOW EXCEPTIONS ==========
# Integrated from: exceptions.py

from enum import Enum

class WorkflowErrorCode(Enum):
    """🔥 STANDARDIZED WORKFLOW ERROR CODES - ENTERPRISE GRADE"""
    # General workflow errors (1000-1099)
    WORKFLOW_INITIALIZATION_FAILED = "WF1000"
    WORKFLOW_EXECUTION_FAILED = "WF1001"
    WORKFLOW_TIMEOUT = "WF1002"
    WORKFLOW_CANCELLED = "WF1003"
    WORKFLOW_NOT_FOUND = "WF1004"
    WORKFLOW_INVALID_STATE = "WF1005"
    
    # Pipeline errors (1100-1199)
    PIPELINE_CREATION_FAILED = "WF1100"
    PIPELINE_STEP_FAILED = "WF1101"
    PIPELINE_DEPENDENCY_ERROR = "WF1102"
    PIPELINE_DEADLOCK = "WF1103"
    PIPELINE_RESOURCE_EXHAUSTED = "WF1104"
    PIPELINE_VALIDATION_ERROR = "WF1105"
    
    # Validation errors (1500-1599)
    VALIDATION_FAILED = "WF1500"
    VALIDATION_RULE_ERROR = "WF1501"
    VALIDATION_SCHEMA_ERROR = "WF1502"
    VALIDATION_SECURITY_ERROR = "WF1503"
    VALIDATION_PERFORMANCE_ERROR = "WF1504"


class WorkflowException(Exception):
    """🔥 BASE WORKFLOW EXCEPTION - ENTERPRISE EXCEPTION HANDLING"""
    
    def __init__(
        self,
        message: str,
        error_code: WorkflowErrorCode = WorkflowErrorCode.WORKFLOW_EXECUTION_FAILED,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            'error_code': self.error_code.value,
            'message': self.message,
            'details': self.details,
            'context': self.context,
            'recovery_suggestions': self.recovery_suggestions,
            'timestamp': self.timestamp.isoformat(),
            'exception_type': self.__class__.__name__
        }


class PipelineException(WorkflowException):
    """🔥 PIPELINE-SPECIFIC EXCEPTION - ENTERPRISE PIPELINE ERROR HANDLING"""
    
    def __init__(
        self,
        message: str,
        pipeline_id: Optional[str] = None,
        step_id: Optional[str] = None,
        error_code: WorkflowErrorCode = WorkflowErrorCode.PIPELINE_STEP_FAILED,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.pipeline_id = pipeline_id
        self.step_id = step_id


class ValidationException(WorkflowException):
    """🔥 VALIDATION-SPECIFIC EXCEPTION - ENTERPRISE VALIDATION ERROR HANDLING"""
    
    def __init__(
        self,
        message: str,
        validation_type: Optional[str] = None,
        validation_level: Optional[str] = None,
        validation_failures: Optional[List[Dict[str, Any]]] = None,
        error_code: WorkflowErrorCode = WorkflowErrorCode.VALIDATION_FAILED,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.validation_type = validation_type
        self.validation_level = validation_level
        self.validation_failures = validation_failures or []


class StepExecutionException(PipelineException):
    """🔥 STEP EXECUTION EXCEPTION - ENTERPRISE STEP ERROR HANDLING"""
    
    def __init__(
        self,
        message: str,
        step_name: Optional[str] = None,
        execution_duration: Optional[float] = None,
        retry_count: int = 0,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.step_name = step_name
        self.execution_duration = execution_duration
        self.retry_count = retry_count


class SecurityException(WorkflowException):
    """🔥 SECURITY EXCEPTION - ENTERPRISE SECURITY ERROR HANDLING"""
    
    def __init__(
        self,
        message: str,
        security_violation_type: Optional[str] = None,
        threat_level: str = "medium",
        error_code: WorkflowErrorCode = WorkflowErrorCode.VALIDATION_SECURITY_ERROR,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.security_violation_type = security_violation_type
        self.threat_level = threat_level


class PerformanceException(WorkflowException):
    """🔥 PERFORMANCE EXCEPTION - ENTERPRISE PERFORMANCE ERROR HANDLING"""
    
    def __init__(
        self,
        message: str,
        performance_metric: Optional[str] = None,
        threshold_exceeded: Optional[float] = None,
        actual_value: Optional[float] = None,
        error_code: WorkflowErrorCode = WorkflowErrorCode.VALIDATION_PERFORMANCE_ERROR,
        **kwargs
    ):
        super().__init__(message, error_code, **kwargs)
        self.performance_metric = performance_metric
        self.threshold_exceeded = threshold_exceeded
        self.actual_value = actual_value


# ========== EXCEPTION HANDLING UTILITIES ==========

class ExceptionHandler:
    """🔥 ENTERPRISE EXCEPTION HANDLER - COMPREHENSIVE ERROR MANAGEMENT"""
    
    def __init__(self):
        self.exception_history = []
        self.recovery_strategies = {}
        self.notification_callbacks = []
        
        self.logger = logging.getLogger(f"{__name__}.ExceptionHandler")
    
    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        auto_recovery: bool = True
    ) -> Dict[str, Any]:
        """Handle workflow exceptions with enterprise-grade error management."""
        
        error_info = {
            'exception_id': uuid.uuid4().hex[:8],
            'timestamp': datetime.now(),
            'exception_type': exception.__class__.__name__,
            'message': str(exception),
            'context': context or {},
            'handled': False,
            'recovery_attempted': False,
            'recovery_successful': False
        }
        
        # Log exception
        self.logger.error(f"Exception occurred: {exception}")
        
        # Handle specific exception types
        if isinstance(exception, WorkflowException):
            error_info.update({
                'error_code': exception.error_code.value,
                'details': exception.details,
                'recovery_suggestions': exception.recovery_suggestions
            })
            
            # Attempt automatic recovery if enabled
            if auto_recovery and exception.error_code in self.recovery_strategies:
                recovery_result = self._attempt_recovery(exception)
                error_info.update({
                    'recovery_attempted': True,
                    'recovery_successful': recovery_result.get('success', False),
                    'recovery_details': recovery_result
                })
        
        # Store in history
        self.exception_history.append(error_info)
        
        # Notify callbacks
        for callback in self.notification_callbacks:
            try:
                callback(error_info)
            except Exception as callback_error:
                self.logger.error(f"Exception notification callback failed: {callback_error}")
        
        error_info['handled'] = True
        return error_info
    
    def _attempt_recovery(self, exception: WorkflowException) -> Dict[str, Any]:
        """Attempt automatic recovery from workflow exception."""
        
        recovery_strategy = self.recovery_strategies.get(exception.error_code)
        if not recovery_strategy:
            return {'success': False, 'reason': 'No recovery strategy available'}
        
        try:
            recovery_result = recovery_strategy(exception)
            return {'success': True, 'result': recovery_result}
        except Exception as recovery_error:
            return {'success': False, 'reason': str(recovery_error)}
    
    def register_recovery_strategy(
        self,
        error_code: WorkflowErrorCode,
        recovery_function: Callable[[WorkflowException], Any]
    ):
        """Register recovery strategy for specific error code."""
        self.recovery_strategies[error_code] = recovery_function
    
    def add_notification_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add notification callback for exception events."""
        self.notification_callbacks.append(callback)
    
    def get_exception_statistics(self) -> Dict[str, Any]:
        """Get exception statistics and patterns."""
        
        if not self.exception_history:
            return {'total_exceptions': 0}
        
        # Calculate statistics
        total_exceptions = len(self.exception_history)
        exception_types = {}
        error_codes = {}
        recovery_success_rate = 0
        
        for error_info in self.exception_history:
            # Count by type
            exc_type = error_info['exception_type']
            exception_types[exc_type] = exception_types.get(exc_type, 0) + 1
            
            # Count by error code
            if 'error_code' in error_info:
                error_code = error_info['error_code']
                error_codes[error_code] = error_codes.get(error_code, 0) + 1
            
            # Recovery statistics
            if error_info.get('recovery_attempted') and error_info.get('recovery_successful'):
                recovery_success_rate += 1
        
        recovery_attempts = sum(1 for e in self.exception_history if e.get('recovery_attempted'))
        recovery_success_rate = (recovery_success_rate / recovery_attempts * 100) if recovery_attempts > 0 else 0
        
        return {
            'total_exceptions': total_exceptions,
            'exception_types': exception_types,
            'error_codes': error_codes,
            'recovery_attempts': recovery_attempts,
            'recovery_success_rate': f"{recovery_success_rate:.1f}%",
            'most_common_exception': max(exception_types, key=exception_types.get) if exception_types else None,
            'most_common_error_code': max(error_codes, key=error_codes.get) if error_codes else None
        }