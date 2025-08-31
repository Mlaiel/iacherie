"""Data Schema Validation Engine for Crawler System
===============================================

Industrial-grade schema validation system for the IA Influencer Agent Platform
providing comprehensive data structure validation and integrity checking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use, reproduction, or distribution strictly prohibited

Features:
- Multi-format schema validation (JSON, XML, Pydantic)
- Custom validation rules and constraints
- Business object validation
- Data type validation and coercion
- Cross-field validation
"""
import json
import re
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
import logging

try:
    from pydantic import BaseModel, ValidationError, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    import jsonschema
    from jsonschema import validate, ValidationError as JsonSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class SchemaType(Enum):
    """Schema validation types"""    JSON_SCHEMA = "json_schema"
    PYDANTIC = "pydantic"
    CUSTOM = "custom"
    BUSINESS_OBJECT = "business_object"
    DATABASE_SCHEMA = "database_schema"


class ValidationSeverity(Enum):
    """Validation issue severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SchemaValidationIssue:
    """Individual schema validation issue"""    severity: ValidationSeverity
    code: str
    message: str
    field_path: str
    expected_type: Optional[str] = None
    actual_value: Optional[Any] = None
    rule_name: Optional[str] = None
    suggestion: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchemaValidationResult:
    """Comprehensive schema validation result"""    is_valid: bool
    schema_type: SchemaType
    issues: List[SchemaValidationIssue] = field(default_factory=list)
    validated_data: Optional[Any] = None
    coerced_data: Optional[Any] = None
    validation_time_ms: float = 0.0
    schema_name: Optional[str] = None
    validation_rules_count: int = 0
    fields_validated: int = 0
    fields_passed: int = 0
    fields_failed: int = 0
    validated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors"""        return any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                  for issue in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings"""        return any(issue.severity == ValidationSeverity.WARNING for issue in self.issues)
    
    @property
    def error_count(self) -> int:
        """Count of error-level issues"""        return len([i for i in self.issues if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]])
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level issues"""        return len([i for i in self.issues if i.severity == ValidationSeverity.WARNING])
    
    @property
    def success_rate(self) -> float:
        """Calculate field validation success rate"""        if self.fields_validated == 0:
            return 0.0
        return self.fields_passed / self.fields_validated


class CustomValidationRule:
    """Custom validation rule definition"""    
    def __init__(
        self,
        name: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        severity: ValidationSeverity = ValidationSeverity.ERROR,
        field_path: str = "",
        suggestion: Optional[str] = None
    ):
        self.name = name
        self.validator_func = validator_func
        self.error_message = error_message
        self.severity = severity
        self.field_path = field_path
        self.suggestion = suggestion
    
    def validate(self, value: Any) -> Optional[SchemaValidationIssue]:
        """Execute validation rule"""        try:
            if not self.validator_func(value):
                return SchemaValidationIssue(
                    severity=self.severity,
                    code=f"CUSTOM_RULE_{self.name.upper()}",
                    message=self.error_message,
                    field_path=self.field_path,
                    actual_value=value,
                    rule_name=self.name,
                    suggestion=self.suggestion
                )
        except Exception as e:
            return SchemaValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="VALIDATION_RULE_ERROR",
                message=f"Validation rule '{self.name}' failed with error: {str(e)}",
                field_path=self.field_path,
                actual_value=value,
                rule_name=self.name
            )
        return None


class SchemaValidator:
    """    Enterprise-grade schema validation engine for crawler data validation.
    
    Supports multiple validation types:
    - JSON Schema validation
    - Pydantic model validation
    - Custom business rule validation
    - Cross-field validation
    - Data type coercion
    """    
    def __init__(self):
        self.custom_rules = {}
        self.business_schemas = {}
        self.type_coercers = self._initialize_type_coercers()
        self.format_validators = self._initialize_format_validators()
        
        logger.info("SchemaValidator initialized")
    
    def validate_json_schema(
        self,
        data: Any,
        schema: Dict[str, Any],
        schema_name: Optional[str] = None
    ) -> SchemaValidationResult:
        """        Validate data against JSON Schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema definition
            schema_name: Optional schema name for reporting
            
        Returns:
            SchemaValidationResult: Validation result
        """        start_time = datetime.utcnow()
        
        if not JSONSCHEMA_AVAILABLE:
            raise ValidationException("jsonschema library not available")
        
        result = SchemaValidationResult(
            is_valid=True,
            schema_type=SchemaType.JSON_SCHEMA,
            schema_name=schema_name
        )
        
        try:
            # Perform JSON Schema validation
            jsonschema.validate(instance=data, schema=schema)
            result.validated_data = data
            result.fields_validated = self._count_schema_fields(schema)
            result.fields_passed = result.fields_validated
            
        except JsonSchemaValidationError as e:
            result.is_valid = False
            
            # Parse validation error
            issue = self._parse_jsonschema_error(e)
            result.issues.append(issue)
            result.fields_failed = 1
            result.fields_validated = 1
            
        except Exception as e:
            result.is_valid = False
            result.issues.append(SchemaValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SCHEMA_VALIDATION_ERROR",
                message=f"Schema validation failed: {str(e)}",
                field_path="root"
            ))
        
        # Record validation time
        validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.validation_time_ms = validation_time
        
        logger.debug(f"JSON Schema validation completed in {validation_time:.2f}ms")
        return result
    
    def validate_pydantic_model(
        self,
        data: Dict[str, Any],
        model_class: Type[BaseModel],
        schema_name: Optional[str] = None
    ) -> SchemaValidationResult:
        """        Validate data against Pydantic model.
        
        Args:
            data: Data to validate
            model_class: Pydantic model class
            schema_name: Optional schema name for reporting
            
        Returns:
            SchemaValidationResult: Validation result
        """        start_time = datetime.utcnow()
        
        if not PYDANTIC_AVAILABLE:
            raise ValidationException("pydantic library not available")
        
        result = SchemaValidationResult(
            is_valid=True,
            schema_type=SchemaType.PYDANTIC,
            schema_name=schema_name or model_class.__name__
        )
        
        try:
            # Create and validate Pydantic model instance
            validated_model = model_class(**data)
            result.validated_data = validated_model.dict()
            result.fields_validated = len(model_class.__fields__)
            result.fields_passed = result.fields_validated
            
        except ValidationError as e:
            result.is_valid = False
            
            # Parse Pydantic validation errors
            for error in e.errors():
                issue = self._parse_pydantic_error(error)
                result.issues.append(issue)
            
            result.fields_failed = len(e.errors())
            result.fields_validated = len(model_class.__fields__)
            
        except Exception as e:
            result.is_valid = False
            result.issues.append(SchemaValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="PYDANTIC_VALIDATION_ERROR",
                message=f"Pydantic validation failed: {str(e)}",
                field_path="root"
            ))
        
        # Record validation time
        validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.validation_time_ms = validation_time
        
        logger.debug(f"Pydantic validation completed in {validation_time:.2f}ms")
        return result
    
    def validate_custom_rules(
        self,
        data: Any,
        rules: List[CustomValidationRule],
        schema_name: Optional[str] = None
    ) -> SchemaValidationResult:
        """        Validate data against custom validation rules.
        
        Args:
            data: Data to validate
            rules: List of custom validation rules
            schema_name: Optional schema name for reporting
            
        Returns:
            SchemaValidationResult: Validation result
        """        start_time = datetime.utcnow()
        
        result = SchemaValidationResult(
            is_valid=True,
            schema_type=SchemaType.CUSTOM,
            schema_name=schema_name,
            validation_rules_count=len(rules)
        )
        
        fields_validated = set()
        fields_passed = set()
        
        for rule in rules:
            # Extract field value if field path is specified
            if rule.field_path:
                try:
                    field_value = self._extract_field_value(data, rule.field_path)
                    fields_validated.add(rule.field_path)
                except KeyError:
                    result.issues.append(SchemaValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="FIELD_NOT_FOUND",
                        message=f"Field '{rule.field_path}' not found in data",
                        field_path=rule.field_path,
                        rule_name=rule.name
                    ))
                    continue
            else:
                field_value = data
                fields_validated.add("root")
            
            # Execute validation rule
            issue = rule.validate(field_value)
            if issue:
                result.issues.append(issue)
                result.is_valid = False
            else:
                fields_passed.add(rule.field_path or "root")
        
        result.fields_validated = len(fields_validated)
        result.fields_passed = len(fields_passed)
        result.fields_failed = result.fields_validated - result.fields_passed
        
        # Record validation time
        validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.validation_time_ms = validation_time
        
        logger.debug(f"Custom rules validation completed in {validation_time:.2f}ms")
        return result
    
    def validate_business_object(
        self,
        data: Dict[str, Any],
        object_type: str,
        schema_name: Optional[str] = None
    ) -> SchemaValidationResult:
        """        Validate business object according to predefined schemas.
        
        Args:
            data: Data to validate
            object_type: Type of business object
            schema_name: Optional schema name for reporting
            
        Returns:
            SchemaValidationResult: Validation result
        """        start_time = datetime.utcnow()
        
        if object_type not in self.business_schemas:
            raise ValidationException(f"Unknown business object type: {object_type}")
        
        schema_config = self.business_schemas[object_type]
        
        result = SchemaValidationResult(
            is_valid=True,
            schema_type=SchemaType.BUSINESS_OBJECT,
            schema_name=schema_name or object_type
        )
        
        # Validate required fields
        required_fields = schema_config.get('required_fields', [])
        for field in required_fields:
            if field not in data or data[field] is None:
                result.issues.append(SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="REQUIRED_FIELD_MISSING",
                    message=f"Required field '{field}' is missing or null",
                    field_path=field,
                    expected_type="any"
                ))
                result.is_valid = False
        
        # Validate field types
        field_types = schema_config.get('field_types', {})
        for field, expected_type in field_types.items():
            if field in data:
                if not self._validate_field_type(data[field], expected_type):
                    result.issues.append(SchemaValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="TYPE_MISMATCH",
                        message=f"Field '{field}' has invalid type",
                        field_path=field,
                        expected_type=expected_type,
                        actual_value=data[field]
                    ))
                    result.is_valid = False
        
        # Validate field constraints
        constraints = schema_config.get('constraints', {})
        for field, constraint_list in constraints.items():
            if field in data:
                for constraint in constraint_list:
                    issue = self._validate_constraint(data[field], constraint, field)
                    if issue:
                        result.issues.append(issue)
                        if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                            result.is_valid = False
        
        # Validate cross-field rules
        cross_field_rules = schema_config.get('cross_field_rules', [])
        for rule in cross_field_rules:
            issue = self._validate_cross_field_rule(data, rule)
            if issue:
                result.issues.append(issue)
                if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                    result.is_valid = False
        
        # Calculate field statistics
        all_fields = set(required_fields + list(field_types.keys()) + list(constraints.keys()))
        result.fields_validated = len(all_fields)
        result.fields_failed = len([i for i in result.issues if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]])
        result.fields_passed = result.fields_validated - result.fields_failed
        
        # Record validation time
        validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.validation_time_ms = validation_time
        
        logger.debug(f"Business object validation completed in {validation_time:.2f}ms")
        return result
    
    def validate_with_coercion(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any],
        coercion_rules: Optional[Dict[str, str]] = None
    ) -> SchemaValidationResult:
        """        Validate data with automatic type coercion.
        
        Args:
            data: Data to validate
            schema: Schema definition
            coercion_rules: Optional type coercion rules
            
        Returns:
            SchemaValidationResult: Validation result with coerced data
        """        start_time = datetime.utcnow()
        
        result = SchemaValidationResult(
            is_valid=True,
            schema_type=SchemaType.CUSTOM,
            schema_name="coercion_validation"
        )
        
        coerced_data = {}
        coercion_rules = coercion_rules or {}
        
        for field, value in data.items():
            if field in schema:
                expected_type = schema[field].get('type', 'string')
                coercion_type = coercion_rules.get(field, expected_type)
                
                # Attempt type coercion
                coerced_value, coercion_issue = self._coerce_value(value, coercion_type, field)
                
                if coercion_issue:
                    result.issues.append(coercion_issue)
                    if coercion_issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                        result.is_valid = False
                    coerced_data[field] = value  # Keep original value
                else:
                    coerced_data[field] = coerced_value
            else:
                coerced_data[field] = value
        
        result.validated_data = data
        result.coerced_data = coerced_data
        
        # Record validation time
        validation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.validation_time_ms = validation_time
        
        logger.debug(f"Coercion validation completed in {validation_time:.2f}ms")
        return result
    
    def add_custom_rule(self, rule: CustomValidationRule) -> None:
        """Add a custom validation rule"""        self.custom_rules[rule.name] = rule
        logger.debug(f"Added custom validation rule: {rule.name}")
    
    def add_business_schema(self, object_type: str, schema_config: Dict[str, Any]) -> None:
        """Add a business object schema"""        self.business_schemas[object_type] = schema_config
        logger.debug(f"Added business object schema: {object_type}")
    
    def validate_format(self, value: str, format_name: str) -> bool:
        """Validate string value against named format"""        if format_name in self.format_validators:
            return self.format_validators[format_name](value)
        return True
    
    # Helper methods
    
    def _parse_jsonschema_error(self, error: JsonSchemaValidationError) -> SchemaValidationIssue:
        """Parse JSON Schema validation error"""        field_path = ".".join(str(x) for x in error.absolute_path) or "root"
        
        return SchemaValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="JSON_SCHEMA_ERROR",
            message=error.message,
            field_path=field_path,
            actual_value=error.instance if hasattr(error, 'instance') else None
        )
    
    def _parse_pydantic_error(self, error: Dict[str, Any]) -> SchemaValidationIssue:
        """Parse Pydantic validation error"""        field_path = ".".join(str(x) for x in error.get('loc', []))
        error_type = error.get('type', 'validation_error')
        message = error.get('msg', 'Validation failed')
        
        return SchemaValidationIssue(
            severity=ValidationSeverity.ERROR,
            code=f"PYDANTIC_{error_type.upper()}",
            message=message,
            field_path=field_path,
            actual_value=error.get('input')
        )
    
    def _count_schema_fields(self, schema: Dict[str, Any]) -> int:
        """Count fields in JSON schema"""        count = 0
        if 'properties' in schema:
            count += len(schema['properties'])
            for prop_schema in schema['properties'].values():
                if isinstance(prop_schema, dict) and 'properties' in prop_schema:
                    count += self._count_schema_fields(prop_schema)
        return count
    
    def _extract_field_value(self, data: Any, field_path: str) -> Any:
        """Extract field value using dot notation path"""        keys = field_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value[key]
            elif isinstance(value, list) and key.isdigit():
                value = value[int(key)]
            else:
                raise KeyError(f"Cannot access field '{key}' in {type(value)}")
        
        return value
    
    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validate field type"""        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float, Decimal),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        if expected_type in type_mapping:
            expected_class = type_mapping[expected_type]
            return isinstance(value, expected_class)
        
        return True  # Unknown type, pass validation
    
    def _validate_constraint(self, value: Any, constraint: Dict[str, Any], field_path: str) -> Optional[SchemaValidationIssue]:
        """Validate field constraint"""        constraint_type = constraint.get('type')
        
        if constraint_type == 'min_length' and isinstance(value, str):
            min_length = constraint.get('value', 0)
            if len(value) < min_length:
                return SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MIN_LENGTH_VIOLATION",
                    message=f"Field '{field_path}' length ({len(value)}) is below minimum ({min_length})",
                    field_path=field_path,
                    actual_value=value
                )
        
        elif constraint_type == 'max_length' and isinstance(value, str):
            max_length = constraint.get('value', float('inf'))
            if len(value) > max_length:
                return SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MAX_LENGTH_VIOLATION",
                    message=f"Field '{field_path}' length ({len(value)}) exceeds maximum ({max_length})",
                    field_path=field_path,
                    actual_value=value
                )
        
        elif constraint_type == 'pattern' and isinstance(value, str):
            pattern = constraint.get('value', '')
            if not re.match(pattern, value):
                return SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="PATTERN_MISMATCH",
                    message=f"Field '{field_path}' doesn't match required pattern",
                    field_path=field_path,
                    actual_value=value
                )
        
        elif constraint_type == 'range' and isinstance(value, (int, float)):
            min_val = constraint.get('min', float('-inf'))
            max_val = constraint.get('max', float('inf'))
            if not (min_val <= value <= max_val):
                return SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="RANGE_VIOLATION",
                    message=f"Field '{field_path}' value ({value}) is outside allowed range ({min_val}-{max_val})",
                    field_path=field_path,
                    actual_value=value
                )
        
        elif constraint_type == 'enum':
            allowed_values = constraint.get('values', [])
            if value not in allowed_values:
                return SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="ENUM_VIOLATION",
                    message=f"Field '{field_path}' value must be one of: {allowed_values}",
                    field_path=field_path,
                    actual_value=value
                )
        
        return None
    
    def _validate_cross_field_rule(self, data: Dict[str, Any], rule: Dict[str, Any]) -> Optional[SchemaValidationIssue]:
        """Validate cross-field business rule"""        rule_type = rule.get('type')
        
        if rule_type == 'date_range':
            start_field = rule.get('start_field')
            end_field = rule.get('end_field')
            
            if start_field in data and end_field in data:
                start_date = data[start_field]
                end_date = data[end_field]
                
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                if start_date >= end_date:
                    return SchemaValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="INVALID_DATE_RANGE",
                        message=f"End date must be after start date",
                        field_path=f"{start_field},{end_field}"
                    )
        
        elif rule_type == 'conditional_required':
            condition_field = rule.get('condition_field')
            condition_value = rule.get('condition_value')
            required_field = rule.get('required_field')
            
            if condition_field in data and data[condition_field] == condition_value:
                if required_field not in data or data[required_field] is None:
                    return SchemaValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="CONDITIONAL_REQUIRED_MISSING",
                        message=f"Field '{required_field}' is required when '{condition_field}' is '{condition_value}'",
                        field_path=required_field
                    )
        
        elif rule_type == 'mutual_exclusion':
            fields = rule.get('fields', [])
            present_fields = [f for f in fields if f in data and data[f] is not None]
            
            if len(present_fields) > 1:
                return SchemaValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MUTUAL_EXCLUSION_VIOLATION",
                    message=f"Only one of these fields can be present: {fields}",
                    field_path=",".join(present_fields)
                )
        
        return None
    
    def _coerce_value(self, value: Any, target_type: str, field_path: str) -> Tuple[Any, Optional[SchemaValidationIssue]]:
        """Attempt to coerce value to target type"""        if target_type in self.type_coercers:
            try:
                coerced_value = self.type_coercers[target_type](value)
                return coerced_value, None
            except (ValueError, TypeError) as e:
                return value, SchemaValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="TYPE_COERCION_FAILED",
                    message=f"Could not coerce '{field_path}' to {target_type}: {str(e)}",
                    field_path=field_path,
                    actual_value=value,
                    suggestion=f"Provide value in correct {target_type} format"
                )
        
        return value, None
    
    def _initialize_type_coercers(self) -> Dict[str, Callable]:
        """Initialize type coercion functions"""        def coerce_to_int(value):
            if isinstance(value, str):
                value = value.strip()
                if value.replace('-', '').replace('+', '').isdigit():
                    return int(value)
            elif isinstance(value, float):
                return int(value)
            return int(value)
        
        def coerce_to_float(value):
            if isinstance(value, str):
                value = value.strip()
                return float(value)
            return float(value)
        
        def coerce_to_bool(value):
            if isinstance(value, str):
                value = value.lower().strip()
                if value in ('true', '1', 'yes', 'on'):
                    return True
                elif value in ('false', '0', 'no', 'off'):
                    return False
            elif isinstance(value, (int, float)):
                return bool(value)
            return bool(value)
        
        def coerce_to_datetime(value):
            if isinstance(value, str):
                # Try common datetime formats
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%Y-%m-%d',
                    '%d/%m/%Y',
                    '%m/%d/%Y'
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                # Try ISO format
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, (int, float)):
                return datetime.fromtimestamp(value)
            return datetime(value)
        
        return {
            'integer': coerce_to_int,
            'number': coerce_to_float,
            'boolean': coerce_to_bool,
            'datetime': coerce_to_datetime,
            'string': str,
            'array': lambda x: x if isinstance(x, list) else [x],
            'object': lambda x: x if isinstance(x, dict) else {'value': x}
        }
    
    def _initialize_format_validators(self) -> Dict[str, Callable[[str], bool]]:
        """Initialize format validation functions"""        def validate_email(value: str) -> bool:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, value) is not None
        
        def validate_url(value: str) -> bool:
            pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
            return re.match(pattern, value) is not None
        
        def validate_uuid(value: str) -> bool:
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
            return re.match(pattern, value.lower()) is not None
        
        def validate_phone(value: str) -> bool:
            # Simple phone validation
            pattern = r'^\+?[1-9]\d{1,14}$'
            cleaned = re.sub(r'[^\d+]', '', value)
            return re.match(pattern, cleaned) is not None
        
        def validate_credit_card(value: str) -> bool:
            # Luhn algorithm for credit card validation
            cleaned = re.sub(r'\D', '', value)
            if len(cleaned) < 13 or len(cleaned) > 19:
                return False
            
            # Luhn algorithm
            checksum = 0
            reverse_digits = cleaned[::-1]
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                checksum += n
            
            return checksum % 10 == 0
        
        def validate_ip_address(value: str) -> bool:
            # IPv4 validation
            parts = value.split('.')
            if len(parts) != 4:
                return False
            try:
                return all(0 <= int(part) <= 255 for part in parts)
            except ValueError:
                return False
        
        return {
            'email': validate_email,
            'url': validate_url,
            'uuid': validate_uuid,
            'phone': validate_phone,
            'credit_card': validate_credit_card,
            'ip_address': validate_ip_address,
            'alphanumeric': lambda x: x.isalnum(),
            'numeric': lambda x: x.isdigit(),
            'alpha': lambda x: x.isalpha()
        }


# Predefined business object schemas
BUSINESS_SCHEMAS = {
    'user_profile': {
        'required_fields': ['username', 'email'],
        'field_types': {
            'username': 'string',
            'email': 'string',
            'age': 'integer',
            'is_verified': 'boolean',
            'created_at': 'string'
        },
        'constraints': {
            'username': [
                {'type': 'min_length', 'value': 3},
                {'type': 'max_length', 'value': 50},
                {'type': 'pattern', 'value': r'^[a-zA-Z0-9_]+$'}
            ],
            'email': [
                {'type': 'pattern', 'value': r'^[^@]+@[^@]+\.[^@]+$'}
            ],
            'age': [
                {'type': 'range', 'min': 13, 'max': 120}
            ]
        },
        'cross_field_rules': []
    },
    
    'content_item': {
        'required_fields': ['title', 'content_type', 'status'],
        'field_types': {
            'title': 'string',
            'description': 'string',
            'content_type': 'string',
            'status': 'string',
            'created_at': 'string',
            'published_at': 'string',
            'view_count': 'integer',
            'is_featured': 'boolean'
        },
        'constraints': {
            'title': [
                {'type': 'min_length', 'value': 5},
                {'type': 'max_length', 'value': 200}
            ],
            'content_type': [
                {'type': 'enum', 'values': ['text', 'image', 'video', 'audio', 'document']}
            ],
            'status': [
                {'type': 'enum', 'values': ['draft', 'published', 'archived', 'deleted']}
            ],
            'view_count': [
                {'type': 'range', 'min': 0}
            ]
        },
        'cross_field_rules': [
            {
                'type': 'conditional_required',
                'condition_field': 'status',
                'condition_value': 'published',
                'required_field': 'published_at'
            }
        ]
    },
    
    'social_media_post': {
        'required_fields': ['platform', 'content', 'author_id'],
        'field_types': {
            'platform': 'string',
            'content': 'string',
            'author_id': 'string',
            'hashtags': 'array',
            'mentions': 'array',
            'likes_count': 'integer',
            'shares_count': 'integer',
            'posted_at': 'string'
        },
        'constraints': {
            'platform': [
                {'type': 'enum', 'values': ['twitter', 'instagram', 'facebook', 'linkedin', 'tiktok']}
            ],
            'content': [
                {'type': 'min_length', 'value': 1},
                {'type': 'max_length', 'value': 2200}
            ],
            'likes_count': [
                {'type': 'range', 'min': 0}
            ],
            'shares_count': [
                {'type': 'range', 'min': 0}
            ]
        },
        'cross_field_rules': []
    },
    
    'monetization_data': {
        'required_fields': ['content_id', 'revenue_amount', 'currency'],
        'field_types': {
            'content_id': 'string',
            'revenue_amount': 'number',
            'currency': 'string',
            'payment_date': 'string',
            'platform': 'string',
            'revenue_type': 'string'
        },
        'constraints': {
            'revenue_amount': [
                {'type': 'range', 'min': 0}
            ],
            'currency': [
                {'type': 'enum', 'values': ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']}
            ],
            'revenue_type': [
                {'type': 'enum', 'values': ['ad_revenue', 'subscription', 'donation', 'merchandise', 'licensing']}
            ]
        },
        'cross_field_rules': []
    }
}
