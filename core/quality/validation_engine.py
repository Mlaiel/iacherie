"""Validation Engine - Enterprise Quality Validation System

Comprehensive validation engine with advanced rule processing, compliance checking,
and automated quality assurance for multi-format content validation.

Business Logic:
Content submission → Validation rules engine → Quality assessment →
Compliance verification → Security checks → Validation report

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
import time
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
import re
import hashlib
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ValidationRuleType(Enum):
    """Types of validation rules"""    REQUIRED_FIELD = "required_field"
    FORMAT_VALIDATION = "format_validation"
    RANGE_VALIDATION = "range_validation"
    PATTERN_VALIDATION = "pattern_validation"
    CUSTOM_VALIDATION = "custom_validation"
    BUSINESS_RULE = "business_rule"
    SECURITY_RULE = "security_rule"
    COMPLIANCE_RULE = "compliance_rule"


class ValidationSeverity(Enum):
    """Validation result severity levels"""    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Validation execution status"""    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ValidationRule:
    """Individual validation rule definition"""    id: str
    name: str
    description: str
    rule_type: ValidationRuleType
    severity: ValidationSeverity
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Rule configuration
    field_path: Optional[str] = None  # For field validations
    pattern: Optional[str] = None  # For pattern validations
    min_value: Optional[Union[int, float]] = None  # For range validations
    max_value: Optional[Union[int, float]] = None  # For range validations
    allowed_values: Optional[List[Any]] = None  # For enum validations
    custom_validator: Optional[Callable] = None  # For custom validations
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rule_type': self.rule_type.value,
            'severity': self.severity.value,
            'enabled': self.enabled,
            'tags': self.tags,
            'metadata': self.metadata,
            'field_path': self.field_path,
            'pattern': self.pattern,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'allowed_values': self.allowed_values
        }


@dataclass
class ValidationIssue:
    """Individual validation issue"""    rule_id: str
    rule_name: str
    severity: ValidationSeverity
    message: str
    field_path: Optional[str] = None
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'severity': self.severity.value,
            'message': self.message,
            'field_path': self.field_path,
            'actual_value': self.actual_value,
            'expected_value': self.expected_value,
            'suggestions': self.suggestions,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ValidationResult:
    """Comprehensive validation result"""    validation_id: str
    target_type: str
    target_id: str
    status: ValidationStatus
    overall_score: float  # 0-100
    start_time: datetime
    end_time: Optional[datetime] = None
    processing_time_ms: Optional[float] = None
    
    # Results breakdown
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    skipped_rules: int = 0
    error_rules: int = 0
    
    # Issues and recommendations
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_issue(self, issue: ValidationIssue):
        """Add a validation issue"""        self.issues.append(issue)
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues filtered by severity"""        return [issue for issue in self.issues if issue.severity == severity]
    
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues"""        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)
    
    def has_blocking_issues(self) -> bool:
        """Check if there are blocking issues (critical or error)"""        return any(
            issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
            for issue in self.issues
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'validation_id': self.validation_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'status': self.status.value,
            'overall_score': self.overall_score,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'processing_time_ms': self.processing_time_ms,
            'total_rules': self.total_rules,
            'passed_rules': self.passed_rules,
            'failed_rules': self.failed_rules,
            'skipped_rules': self.skipped_rules,
            'error_rules': self.error_rules,
            'issues': [issue.to_dict() for issue in self.issues],
            'recommendations': self.recommendations,
            'metadata': self.metadata
        }


class BaseValidator(ABC):
    """Abstract base class for validators"""    
    @abstractmethod
    def validate(self, data: Any, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute validation and return issues"""        pass
    
    @abstractmethod
    def get_rules(self) -> List[ValidationRule]:
        """Get validation rules"""        pass


class FieldValidator(BaseValidator):
    """Field-level validation"""    
    def __init__(self, rules: List[ValidationRule]):
        self.rules = {rule.id: rule for rule in rules if rule.enabled}
    
    def validate(self, data: Any, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate data against field rules"""        issues = []
        
        for rule in self.rules.values():
            try:
                if rule.rule_type == ValidationRuleType.REQUIRED_FIELD:
                    issues.extend(self._validate_required_field(data, rule))
                elif rule.rule_type == ValidationRuleType.FORMAT_VALIDATION:
                    issues.extend(self._validate_format(data, rule))
                elif rule.rule_type == ValidationRuleType.RANGE_VALIDATION:
                    issues.extend(self._validate_range(data, rule))
                elif rule.rule_type == ValidationRuleType.PATTERN_VALIDATION:
                    issues.extend(self._validate_pattern(data, rule))
                elif rule.rule_type == ValidationRuleType.CUSTOM_VALIDATION:
                    issues.extend(self._validate_custom(data, rule, context))
                    
            except Exception as e:
                logger.error(f"Error validating rule {rule.id}: {e}")
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation error: {str(e)}",
                    metadata={'error_type': 'validation_exception'}
                ))
        
        return issues
    
    def _validate_required_field(self, data: Any, rule: ValidationRule) -> List[ValidationIssue]:
        """Validate required field presence"""        issues = []
        
        if not rule.field_path:
            return issues
        
        value = self._get_nested_value(data, rule.field_path)
        
        if value is None or (isinstance(value, str) and not value.strip()):
            issues.append(ValidationIssue(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Required field '{rule.field_path}' is missing or empty",
                field_path=rule.field_path,
                actual_value=value,
                suggestions=[f"Provide a value for '{rule.field_path}'"]
            ))
        
        return issues
    
    def _validate_format(self, data: Any, rule: ValidationRule) -> List[ValidationIssue]:
        """Validate field format"""        issues = []
        
        if not rule.field_path:
            return issues
        
        value = self._get_nested_value(data, rule.field_path)
        
        if value is None:
            return issues  # Skip format validation for null values
        
        # Email format validation
        if 'email' in rule.tags:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Invalid email format: {value}",
                    field_path=rule.field_path,
                    actual_value=value,
                    suggestions=["Use valid email format (e.g., user@example.com)"]
                ))
        
        # URL format validation
        elif 'url' in rule.tags:
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, str(value)):
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Invalid URL format: {value}",
                    field_path=rule.field_path,
                    actual_value=value,
                    suggestions=["Use valid URL format (e.g., https://example.com)"]
                ))
        
        return issues
    
    def _validate_range(self, data: Any, rule: ValidationRule) -> List[ValidationIssue]:
        """Validate value range"""        issues = []
        
        if not rule.field_path:
            return issues
        
        value = self._get_nested_value(data, rule.field_path)
        
        if value is None:
            return issues
        
        try:
            numeric_value = float(value)
            
            if rule.min_value is not None and numeric_value < rule.min_value:
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Value {numeric_value} is below minimum {rule.min_value}",
                    field_path=rule.field_path,
                    actual_value=numeric_value,
                    expected_value=f">= {rule.min_value}",
                    suggestions=[f"Use value >= {rule.min_value}"]
                ))
            
            if rule.max_value is not None and numeric_value > rule.max_value:
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Value {numeric_value} exceeds maximum {rule.max_value}",
                    field_path=rule.field_path,
                    actual_value=numeric_value,
                    expected_value=f"<= {rule.max_value}",
                    suggestions=[f"Use value <= {rule.max_value}"]
                ))
                
        except (ValueError, TypeError):
            issues.append(ValidationIssue(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=ValidationSeverity.ERROR,
                message=f"Cannot convert '{value}' to numeric value for range validation",
                field_path=rule.field_path,
                actual_value=value,
                suggestions=["Provide a valid numeric value"]
            ))
        
        return issues
    
    def _validate_pattern(self, data: Any, rule: ValidationRule) -> List[ValidationIssue]:
        """Validate against regex pattern"""        issues = []
        
        if not rule.field_path or not rule.pattern:
            return issues
        
        value = self._get_nested_value(data, rule.field_path)
        
        if value is None:
            return issues
        
        try:
            if not re.match(rule.pattern, str(value)):
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=f"Value '{value}' does not match required pattern",
                    field_path=rule.field_path,
                    actual_value=value,
                    expected_value=f"Pattern: {rule.pattern}",
                    suggestions=["Adjust value to match the required pattern"]
                ))
        except re.error as e:
            issues.append(ValidationIssue(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=ValidationSeverity.ERROR,
                message=f"Invalid regex pattern: {e}",
                field_path=rule.field_path,
                metadata={'pattern_error': str(e)}
            ))
        
        return issues
    
    def _validate_custom(self, data: Any, rule: ValidationRule, 
                        context: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute custom validation function"""        issues = []
        
        if not rule.custom_validator:
            return issues
        
        try:
            result = rule.custom_validator(data, rule, context)
            if isinstance(result, list):
                issues.extend(result)
            elif isinstance(result, ValidationIssue):
                issues.append(result)
            elif isinstance(result, bool) and not result:
                issues.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message="Custom validation failed",
                    suggestions=["Review custom validation requirements"]
                ))
        except Exception as e:
            issues.append(ValidationIssue(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=ValidationSeverity.ERROR,
                message=f"Custom validation error: {str(e)}",
                metadata={'custom_validator_error': str(e)}
            ))
        
        return issues
    
    def _get_nested_value(self, data: Any, field_path: str) -> Any:
        """Get nested field value using dot notation"""        if not isinstance(data, dict):
            return None
        
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def get_rules(self) -> List[ValidationRule]:
        """Get all validation rules"""        return list(self.rules.values())


class BusinessRuleValidator(BaseValidator):
    """Business logic validation"""    
    def __init__(self):
        self.rules = self._initialize_business_rules()
    
    def _initialize_business_rules(self) -> Dict[str, ValidationRule]:
        """Initialize standard business rules"""        rules = [
            ValidationRule(
                id="content_monetization_ready",
                name="Content Monetization Readiness",
                description="Validates content is ready for monetization",
                rule_type=ValidationRuleType.BUSINESS_RULE,
                severity=ValidationSeverity.WARNING,
                tags=["monetization", "business"],
                custom_validator=self._validate_monetization_readiness
            ),
            ValidationRule(
                id="platform_compliance",
                name="Platform Compliance Check",
                description="Validates content meets platform requirements",
                rule_type=ValidationRuleType.BUSINESS_RULE,
                severity=ValidationSeverity.ERROR,
                tags=["compliance", "platform"],
                custom_validator=self._validate_platform_compliance
            ),
            ValidationRule(
                id="content_quality_threshold",
                name="Content Quality Threshold",
                description="Validates content meets minimum quality standards",
                rule_type=ValidationRuleType.BUSINESS_RULE,
                severity=ValidationSeverity.ERROR,
                tags=["quality", "threshold"],
                custom_validator=self._validate_quality_threshold
            )
        ]
        
        return {rule.id: rule for rule in rules}
    
    def validate(self, data: Any, context: Dict[str, Any]) -> List[ValidationIssue]:
        """Execute business rule validation"""        issues = []
        
        for rule in self.rules.values():
            if rule.enabled and rule.custom_validator:
                try:
                    result = rule.custom_validator(data, rule, context)
                    if isinstance(result, list):
                        issues.extend(result)
                    elif isinstance(result, ValidationIssue):
                        issues.append(result)
                except Exception as e:
                    logger.error(f"Business rule validation error for {rule.id}: {e}")
                    issues.append(ValidationIssue(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=ValidationSeverity.ERROR,
                        message=f"Business rule validation error: {str(e)}"
                    ))
        
        return issues
    
    def _validate_monetization_readiness(self, data: Any, rule: ValidationRule, 
                                       context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate monetization readiness"""        issues = []
        
        # Check if quality score meets monetization threshold
        quality_score = context.get('quality_score', 0)
        if quality_score < 60:
            issues.append(ValidationIssue(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Quality score {quality_score} below monetization threshold (60)",
                suggestions=["Improve content quality to meet monetization requirements"]
            ))
        
        return issues
    
    def _validate_platform_compliance(self, data: Any, rule: ValidationRule,
                                    context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate platform compliance"""        issues = []
        
        # Example platform compliance checks
        platforms = context.get('target_platforms', [])
        
        for platform in platforms:
            if platform == 'youtube':
                # YouTube specific validation
                if isinstance(data, dict):
                    title = data.get('title', '')
                    if len(title) > 100:
                        issues.append(ValidationIssue(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            message=f"Title too long for YouTube: {len(title)} characters (max: 100)",
                            suggestions=["Shorten title to meet YouTube requirements"]
                        ))
            
            elif platform == 'instagram':
                # Instagram specific validation
                if isinstance(data, dict):
                    description = data.get('description', '')
                    if len(description) > 2200:
                        issues.append(ValidationIssue(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            message=f"Description too long for Instagram: {len(description)} characters (max: 2200)",
                            suggestions=["Shorten description to meet Instagram requirements"]
                        ))
        
        return issues
    
    def _validate_quality_threshold(self, data: Any, rule: ValidationRule,
                                  context: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate quality threshold"""        issues = []
        
        overall_score = context.get('overall_score', 0)
        if overall_score < 70:
            issues.append(ValidationIssue(
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                message=f"Overall quality score {overall_score} below threshold (70)",
                suggestions=["Improve content quality before publishing"]
            ))
        
        return issues
    
    def get_rules(self) -> List[ValidationRule]:
        """Get business validation rules"""        return list(self.rules.values())


class ValidationEngine:
    """Enterprise validation engine with comprehensive rule processing"""    
    def __init__(self):
        self.field_validator = FieldValidator([])
        self.business_validator = BusinessRuleValidator()
        self.custom_validators: Dict[str, BaseValidator] = {}
        
        # Initialize with standard field validation rules
        self._initialize_standard_field_rules()
    
    def _initialize_standard_field_rules(self):
        """Initialize standard field validation rules"""        standard_rules = [
            ValidationRule(
                id="title_required",
                name="Title Required",
                description="Content must have a title",
                rule_type=ValidationRuleType.REQUIRED_FIELD,
                severity=ValidationSeverity.ERROR,
                field_path="title"
            ),
            ValidationRule(
                id="title_length",
                name="Title Length Validation",
                description="Title must be between 5 and 200 characters",
                rule_type=ValidationRuleType.RANGE_VALIDATION,
                severity=ValidationSeverity.WARNING,
                field_path="title",
                min_value=5,
                max_value=200
            ),
            ValidationRule(
                id="description_required",
                name="Description Required",
                description="Content must have a description",
                rule_type=ValidationRuleType.REQUIRED_FIELD,
                severity=ValidationSeverity.WARNING,
                field_path="description"
            ),
            ValidationRule(
                id="tags_format",
                name="Tags Format Validation",
                description="Tags must be provided as an array",
                rule_type=ValidationRuleType.FORMAT_VALIDATION,
                severity=ValidationSeverity.INFO,
                field_path="tags",
                tags=["array"]
            )
        ]
        
        self.field_validator = FieldValidator(standard_rules)
    
    def add_custom_validator(self, name: str, validator: BaseValidator):
        """Add a custom validator"""        self.custom_validators[name] = validator
        logger.info(f"Added custom validator: {name}")
    
    def validate(self, data: Any, target_type: str = "content",
                target_id: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Execute comprehensive validation"""        start_time = datetime.now(timezone.utc)
        validation_id = self._generate_validation_id(data, target_type, target_id)
        
        if target_id is None:
            target_id = str(hash(str(data)))
        
        if context is None:
            context = {}
        
        # Initialize result
        result = ValidationResult(
            validation_id=validation_id,
            target_type=target_type,
            target_id=target_id,
            status=ValidationStatus.RUNNING,
            overall_score=0.0,
            start_time=start_time
        )
        
        try:
            all_issues = []
            total_rules = 0
            
            # Field validation
            field_issues = self.field_validator.validate(data, context)
            all_issues.extend(field_issues)
            total_rules += len(self.field_validator.get_rules())
            
            # Business rule validation
            business_issues = self.business_validator.validate(data, context)
            all_issues.extend(business_issues)
            total_rules += len(self.business_validator.get_rules())
            
            # Custom validators
            for validator_name, validator in self.custom_validators.items():
                try:
                    custom_issues = validator.validate(data, context)
                    all_issues.extend(custom_issues)
                    total_rules += len(validator.get_rules())
                except Exception as e:
                    logger.error(f"Error in custom validator {validator_name}: {e}")
                    all_issues.append(ValidationIssue(
                        rule_id=f"custom_{validator_name}",
                        rule_name=f"Custom Validator: {validator_name}",
                        severity=ValidationSeverity.ERROR,
                        message=f"Custom validator error: {str(e)}"
                    ))
            
            # Add issues to result
            for issue in all_issues:
                result.add_issue(issue)
            
            # Calculate statistics
            result.total_rules = total_rules
            result.failed_rules = len(all_issues)
            result.passed_rules = total_rules - result.failed_rules
            
            # Calculate overall score
            result.overall_score = self._calculate_overall_score(result)
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
            # Determine final status
            if result.has_critical_issues():
                result.status = ValidationStatus.FAILED
            elif result.has_blocking_issues():
                result.status = ValidationStatus.FAILED
            else:
                result.status = ValidationStatus.PASSED
                
        except Exception as e:
            logger.error(f"Validation engine error: {e}")
            result.status = ValidationStatus.ERROR
            result.add_issue(ValidationIssue(
                rule_id="system_error",
                rule_name="System Validation Error",
                severity=ValidationSeverity.CRITICAL,
                message=f"Validation system error: {str(e)}"
            ))
        
        # Finalize result
        result.end_time = datetime.now(timezone.utc)
        result.processing_time_ms = (result.end_time - result.start_time).total_seconds() * 1000
        
        return result
    
    def _generate_validation_id(self, data: Any, target_type: str, 
                               target_id: Optional[str]) -> str:
        """Generate unique validation ID"""        content_hash = hashlib.md5(str(data).encode()).hexdigest()[:8]
        timestamp = int(time.time())
        return f"val_{target_type}_{timestamp}_{content_hash}"
    
    def _calculate_overall_score(self, result: ValidationResult) -> float:
        """Calculate overall validation score"""        if result.total_rules == 0:
            return 100.0
        
        # Base score
        base_score = 100.0
        
        # Deduct points for issues
        for issue in result.issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                base_score -= 25
            elif issue.severity == ValidationSeverity.ERROR:
                base_score -= 15
            elif issue.severity == ValidationSeverity.WARNING:
                base_score -= 10
            elif issue.severity == ValidationSeverity.INFO:
                base_score -= 5
        
        return max(0.0, base_score)
    
    def _generate_recommendations(self, result: ValidationResult) -> List[str]:
        """Generate validation recommendations"""        recommendations = []
        
        # Critical issues
        critical_issues = result.get_issues_by_severity(ValidationSeverity.CRITICAL)
        if critical_issues:
            recommendations.append("Address all critical issues immediately before proceeding")
        
        # Error issues
        error_issues = result.get_issues_by_severity(ValidationSeverity.ERROR)
        if error_issues:
            recommendations.append("Resolve error-level issues to improve validation score")
        
        # Warning issues
        warning_issues = result.get_issues_by_severity(ValidationSeverity.WARNING)
        if warning_issues:
            recommendations.append("Consider addressing warning issues for better quality")
        
        # Score-based recommendations
        if result.overall_score < 50:
            recommendations.append("Overall validation score is low - comprehensive review needed")
        elif result.overall_score < 70:
            recommendations.append("Consider improving content to achieve higher validation score")
        elif result.overall_score >= 90:
            recommendations.append("Excellent validation score - content is ready for publication")
        
        return recommendations
    
    async def validate_async(self, data: Any, target_type: str = "content",
                           target_id: Optional[str] = None,
                           context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Execute validation asynchronously"""        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.validate, data, target_type, target_id, context
        )
    
    def batch_validate(self, items: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate multiple items in batch"""        results = []
        
        for item in items:
            data = item.get('data')
            target_type = item.get('target_type', 'content')
            target_id = item.get('target_id')
            context = item.get('context')
            
            result = self.validate(data, target_type, target_id, context)
            results.append(result)
        
        return results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Get summary statistics for multiple validation results"""        if not results:
            return {}
        
        total_results = len(results)
        passed_results = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed_results = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        error_results = sum(1 for r in results if r.status == ValidationStatus.ERROR)
        
        avg_score = sum(r.overall_score for r in results) / total_results
        avg_processing_time = sum(r.processing_time_ms or 0 for r in results) / total_results
        
        return {
            'total_validations': total_results,
            'passed_validations': passed_results,
            'failed_validations': failed_results,
            'error_validations': error_results,
            'pass_rate_percent': (passed_results / total_results) * 100,
            'average_score': avg_score,
            'average_processing_time_ms': avg_processing_time,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
