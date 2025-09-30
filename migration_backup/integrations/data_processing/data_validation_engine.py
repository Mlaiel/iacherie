"""Data Validation Engine - Comprehensive Data Quality Assurance
==============================================================

Multi-dimensional data validation and cleansing with schema validation,
business rule enforcement, anomaly detection, and automated data quality scoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import re
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import statistics
from decimal import Decimal
import dateutil.parser

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
    np = None
    stats = None

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import redis.asyncio as redis


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRuleType(Enum):
    """Types of validation rules."""
    SCHEMA = "schema"
    DATA_TYPE = "data_type"
    RANGE = "range"
    FORMAT = "format"
    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    BUSINESS_RULE = "business_rule"
    ANOMALY = "anomaly"
    CUSTOM = "custom"


class DataQualityDimension(Enum):
    """Data quality dimensions."""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"


@dataclass
class ValidationRule:
    """Data validation rule configuration."""
    id: str
    name: str
    rule_type: ValidationRuleType
    field_name: Optional[str] = None
    condition: Optional[str] = None  # Python expression or SQL-like condition
    expected_value: Optional[Any] = None
    min_value: Optional[Union[int, float, datetime]] = None
    max_value: Optional[Union[int, float, datetime]] = None
    pattern: Optional[str] = None  # Regex pattern
    schema: Optional[Dict[str, Any]] = None  # JSON schema
    severity: ValidationSeverity = ValidationSeverity.ERROR
    enabled: bool = True
    error_message: Optional[str] = None
    custom_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    """Data validation issue."""
    id: str
    rule_id: str
    field_name: Optional[str]
    severity: ValidationSeverity
    message: str
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    row_identifier: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of data validation."""
    dataset_id: str
    validation_id: str
    timestamp: datetime
    total_records: int
    passed_records: int
    failed_records: int
    issues: List[ValidationIssue]
    quality_score: float
    dimension_scores: Dict[DataQualityDimension, float]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataProfile:
    """Statistical profile of a dataset."""
    field_name: str
    data_type: str
    total_count: int
    null_count: int
    unique_count: int
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_deviation: Optional[float] = None
    percentiles: Dict[int, Any] = field(default_factory=dict)
    most_common_values: List[tuple[Any, int]] = field(default_factory=list)
    pattern_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetectionConfig:
    """Configuration for anomaly detection."""
    method: str  # 'statistical', 'isolation_forest', 'z_score', 'iqr'
    threshold: float = 2.0
    sensitivity: float = 0.95
    enabled: bool = True
    fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


Base = declarative_base()


class ValidationResultModel(Base):
    """Validation result database model."""
    __tablename__ = 'validation_results'
    
    id = sa.Column(sa.String(36), primary_key=True)
    dataset_id = sa.Column(sa.String(100), nullable=False)
    validation_id = sa.Column(sa.String(36), nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    total_records = sa.Column(sa.Integer, nullable=False)
    passed_records = sa.Column(sa.Integer, nullable=False)
    failed_records = sa.Column(sa.Integer, nullable=False)
    quality_score = sa.Column(sa.Float, nullable=False)
    dimension_scores = sa.Column(sa.Text)
    execution_time = sa.Column(sa.Float)
    issues_summary = sa.Column(sa.Text)
    meta_data = sa.Column(sa.Text)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class ValidationIssueModel(Base):
    """Validation issue database model."""
    __tablename__ = 'validation_issues'
    
    id = sa.Column(sa.String(36), primary_key=True)
    validation_result_id = sa.Column(sa.String(36), nullable=False)
    rule_id = sa.Column(sa.String(36), nullable=False)
    field_name = sa.Column(sa.String(100))
    severity = sa.Column(sa.String(20), nullable=False)
    message = sa.Column(sa.Text, nullable=False)
    actual_value = sa.Column(sa.Text)
    expected_value = sa.Column(sa.Text)
    row_identifier = sa.Column(sa.String(100))
    timestamp = sa.Column(sa.DateTime, nullable=False)
    meta_data = sa.Column(sa.Text)


class DataValidationEngine:
    """Comprehensive data validation and quality assurance engine."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup for caching validation results
        self.redis_url = redis_url
        self.redis_client = None
        
        # Validation rules and configurations
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.rule_sets: Dict[str, List[str]] = {}  # Named sets of rule IDs
        self.anomaly_configs: Dict[str, AnomalyDetectionConfig] = {}
        
        # Custom validation functions
        self.custom_validators: Dict[str, Callable] = {}
        self.data_cleaners: Dict[str, Callable] = {}
        
        # Performance metrics
        self.validation_metrics = {
            'total_validations': 0,
            'total_records_validated': 0,
            'average_quality_score': 0.0,
            'average_execution_time': 0.0,
            'common_issues': defaultdict(int)
        }
        
        # Setup built-in validators and cleaners
        self._setup_built_in_functions()
    
    async def initialize(self):
        """Initialize the validation engine."""
        # Initialize database if configured
        if self.engine:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        self.logger.info("Data validation engine initialized")
    
    def _setup_built_in_functions(self):
        """Setup built-in validation functions and data cleaners."""
        # Built-in validators
        self.custom_validators.update({
            'email_validator': self._validate_email,
            'phone_validator': self._validate_phone,
            'url_validator': self._validate_url,
            'credit_card_validator': self._validate_credit_card,
            'ip_address_validator': self._validate_ip_address,
            'date_validator': self._validate_date,
            'numeric_validator': self._validate_numeric,
            'text_length_validator': self._validate_text_length,
            'enum_validator': self._validate_enum,
            'json_validator': self._validate_json
        })
        
        # Built-in data cleaners
        self.data_cleaners.update({
            'trim_whitespace': self._clean_trim_whitespace,
            'normalize_case': self._clean_normalize_case,
            'remove_special_chars': self._clean_remove_special_chars,
            'standardize_phone': self._clean_standardize_phone,
            'standardize_email': self._clean_standardize_email,
            'parse_date': self._clean_parse_date,
            'normalize_numeric': self._clean_normalize_numeric,
            'remove_duplicates': self._clean_remove_duplicates
        })
    
    def add_validation_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.validation_rules[rule.id] = rule
        self.logger.info(f"Added validation rule: {rule.name}")
    
    def add_rule_set(self, name: str, rule_ids: List[str]):
        """Add a named set of validation rules."""
        self.rule_sets[name] = rule_ids
        self.logger.info(f"Added rule set '{name}' with {len(rule_ids)} rules")
    
    def register_custom_validator(self, name: str, validator: Callable):
        """Register a custom validation function."""
        self.custom_validators[name] = validator
        self.logger.info(f"Registered custom validator: {name}")
    
    def register_data_cleaner(self, name: str, cleaner: Callable):
        """Register a custom data cleaning function."""
        self.data_cleaners[name] = cleaner
        self.logger.info(f"Registered data cleaner: {name}")
    
    async def validate_data(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
        rule_set: Optional[str] = None,
        rule_ids: Optional[List[str]] = None,
        dataset_id: str = "unknown"
    ) -> ValidationResult:
        """Validate data against specified rules."""
        start_time = datetime.utcnow()
        validation_id = str(uuid.uuid4())
        
        # Determine which rules to apply
        rules_to_apply = []
        if rule_set and rule_set in self.rule_sets:
            rules_to_apply = [self.validation_rules[rid] for rid in self.rule_sets[rule_set]]
        elif rule_ids:
            rules_to_apply = [self.validation_rules[rid] for rid in rule_ids if rid in self.validation_rules]
        else:
            rules_to_apply = list(self.validation_rules.values())
        
        # Filter enabled rules
        rules_to_apply = [rule for rule in rules_to_apply if rule.enabled]
        
        # Convert data to standard format
        records = self._normalize_data_format(data)
        total_records = len(records)
        
        # Initialize validation state
        issues: List[ValidationIssue] = []
        passed_records = 0
        failed_records = 0
        record_issues: Dict[int, List[ValidationIssue]] = {}
        
        # Validate each record
        for idx, record in enumerate(records):
            record_passed = True
            
            for rule in rules_to_apply:
                try:
                    rule_issues = await self._apply_validation_rule(rule, record, str(idx))
                    if rule_issues:
                        issues.extend(rule_issues)
                        if idx not in record_issues:
                            record_issues[idx] = []
                        record_issues[idx].extend(rule_issues)
                        
                        # Check if any critical/error issues
                        if any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                               for issue in rule_issues):
                            record_passed = False
                            
                except Exception as e:
                    self.logger.error(f"Error applying rule {rule.id}: {e}")
                    issue = ValidationIssue(
                        id=str(uuid.uuid4()),
                        rule_id=rule.id,
                        field_name=rule.field_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"Rule execution error: {str(e)}",
                        row_identifier=str(idx)
                    )
                    issues.append(issue)
                    record_passed = False
            
            if record_passed:
                passed_records += 1
            else:
                failed_records += 1
        
        # Calculate quality scores
        quality_score = (passed_records / total_records * 100) if total_records > 0 else 0
        dimension_scores = await self._calculate_dimension_scores(records, issues)
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Create validation result
        result = ValidationResult(
            dataset_id=dataset_id,
            validation_id=validation_id,
            timestamp=start_time,
            total_records=total_records,
            passed_records=passed_records,
            failed_records=failed_records,
            issues=issues,
            quality_score=quality_score,
            dimension_scores=dimension_scores,
            execution_time=execution_time
        )
        
        # Store result if database available
        if self.async_session:
            await self._store_validation_result(result)
        
        # Update metrics
        await self._update_metrics(result)
        
        self.logger.info(f"Validation completed: {quality_score:.2f}% quality score, "
                        f"{len(issues)} issues found in {execution_time:.2f}s")
        
        return result
    
    async def _apply_validation_rule(
        self, 
        rule: ValidationRule, 
        record: Dict[str, Any], 
        row_id: str
    ) -> List[ValidationIssue]:
        """Apply a single validation rule to a record."""
        issues = []
        
        try:
            if rule.rule_type == ValidationRuleType.SCHEMA:
                issues.extend(await self._validate_schema(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.DATA_TYPE:
                issues.extend(await self._validate_data_type(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.RANGE:
                issues.extend(await self._validate_range(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.FORMAT:
                issues.extend(await self._validate_format(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.UNIQUENESS:
                issues.extend(await self._validate_uniqueness(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.COMPLETENESS:
                issues.extend(await self._validate_completeness(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.CONSISTENCY:
                issues.extend(await self._validate_consistency(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.BUSINESS_RULE:
                issues.extend(await self._validate_business_rule(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.ANOMALY:
                issues.extend(await self._validate_anomaly(rule, record, row_id))
            elif rule.rule_type == ValidationRuleType.CUSTOM:
                issues.extend(await self._validate_custom(rule, record, row_id))
                
        except Exception as e:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=ValidationSeverity.ERROR,
                message=f"Rule validation error: {str(e)}",
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_schema(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate record against JSON schema."""
        issues = []
        
        if not JSONSCHEMA_AVAILABLE or not rule.schema:
            return issues
        
        try:
            validate(record, rule.schema)
        except ValidationError as e:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=e.path[0] if e.path else None,
                severity=rule.severity,
                message=rule.error_message or f"Schema validation failed: {e.message}",
                actual_value=e.instance if hasattr(e, 'instance') else None,
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_data_type(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate field data type."""
        issues = []
        
        if not rule.field_name or rule.field_name not in record:
            return issues
        
        value = record[rule.field_name]
        expected_type = rule.expected_value
        
        if expected_type and not isinstance(value, expected_type):
            # Try type conversion
            try:
                if expected_type == int:
                    int(value)
                elif expected_type == float:
                    float(value)
                elif expected_type == str:
                    str(value)
                elif expected_type == bool:
                    bool(value)
                else:
                    raise ValueError(f"Cannot convert to {expected_type}")
            except (ValueError, TypeError):
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or f"Invalid data type. Expected {expected_type.__name__}, got {type(value).__name__}",
                    actual_value=value,
                    expected_value=expected_type.__name__,
                    row_identifier=row_id
                )
                issues.append(issue)
        
        return issues
    
    async def _validate_range(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate field value range."""
        issues = []
        
        if not rule.field_name or rule.field_name not in record:
            return issues
        
        value = record[rule.field_name]
        
        if value is None:
            return issues
        
        try:
            if rule.min_value is not None and value < rule.min_value:
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or f"Value {value} is below minimum {rule.min_value}",
                    actual_value=value,
                    expected_value=f">= {rule.min_value}",
                    row_identifier=row_id
                )
                issues.append(issue)
            
            if rule.max_value is not None and value > rule.max_value:
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or f"Value {value} is above maximum {rule.max_value}",
                    actual_value=value,
                    expected_value=f"<= {rule.max_value}",
                    row_identifier=row_id
                )
                issues.append(issue)
                
        except TypeError:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=rule.severity,
                message=rule.error_message or f"Cannot compare value {value} with range bounds",
                actual_value=value,
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_format(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate field format using regex pattern."""
        issues = []
        
        if not rule.field_name or rule.field_name not in record or not rule.pattern:
            return issues
        
        value = record[rule.field_name]
        
        if value is None:
            return issues
        
        try:
            if not re.match(rule.pattern, str(value)):
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or f"Value '{value}' does not match required pattern",
                    actual_value=value,
                    expected_value=rule.pattern,
                    row_identifier=row_id
                )
                issues.append(issue)
        except re.error as e:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=ValidationSeverity.ERROR,
                message=f"Invalid regex pattern: {e}",
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_uniqueness(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate field uniqueness (placeholder for batch validation)."""
        # Uniqueness validation would require batch processing
        # This is a placeholder that would be implemented in batch validation
        return []
    
    async def _validate_completeness(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate field completeness (not null/empty)."""
        issues = []
        
        if not rule.field_name:
            return issues
        
        value = record.get(rule.field_name)
        
        if value is None or (isinstance(value, str) and value.strip() == ""):
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=rule.severity,
                message=rule.error_message or f"Field '{rule.field_name}' is required but missing or empty",
                actual_value=value,
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_consistency(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate field consistency (cross-field validation)."""
        issues = []
        
        if not rule.condition:
            return issues
        
        try:
            # Evaluate condition expression
            result = eval(rule.condition, {"__builtins__": {}}, {"record": record, "data": record})
            
            if not result:
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or f"Consistency check failed: {rule.condition}",
                    row_identifier=row_id
                )
                issues.append(issue)
                
        except Exception as e:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=ValidationSeverity.ERROR,
                message=f"Error evaluating consistency condition: {e}",
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_business_rule(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate business rule."""
        issues = []
        
        if not rule.condition:
            return issues
        
        try:
            # Enhanced context for business rules
            context = {
                "record": record,
                "data": record,
                "datetime": datetime,
                "timedelta": timedelta,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum
            }
            
            result = eval(rule.condition, {"__builtins__": {}}, context)
            
            if not result:
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or f"Business rule violation: {rule.condition}",
                    row_identifier=row_id
                )
                issues.append(issue)
                
        except Exception as e:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=ValidationSeverity.ERROR,
                message=f"Error evaluating business rule: {e}",
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    async def _validate_anomaly(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate for anomalies (requires batch processing)."""
        # Anomaly detection would require batch processing and statistical analysis
        # This is a placeholder for future implementation
        return []
    
    async def _validate_custom(self, rule: ValidationRule, record: Dict[str, Any], row_id: str) -> List[ValidationIssue]:
        """Validate using custom function."""
        issues = []
        
        if not rule.custom_function:
            return issues
        
        try:
            result = await rule.custom_function(record, rule, row_id)
            if isinstance(result, ValidationIssue):
                issues.append(result)
            elif isinstance(result, list):
                issues.extend(result)
            elif not result:  # False or None indicates validation failure
                issue = ValidationIssue(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    field_name=rule.field_name,
                    severity=rule.severity,
                    message=rule.error_message or "Custom validation failed",
                    row_identifier=row_id
                )
                issues.append(issue)
        except Exception as e:
            issue = ValidationIssue(
                id=str(uuid.uuid4()),
                rule_id=rule.id,
                field_name=rule.field_name,
                severity=ValidationSeverity.ERROR,
                message=f"Custom validation error: {e}",
                row_identifier=row_id
            )
            issues.append(issue)
        
        return issues
    
    def _normalize_data_format(self, data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]) -> List[Dict[str, Any]]:
        """Normalize data to list of dictionaries."""
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        elif PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
            return data.to_dict('records')
        else:
            raise ValueError(f"Unsupported data format: {type(data)}")
    
    async def _calculate_dimension_scores(
        self, 
        records: List[Dict[str, Any]], 
        issues: List[ValidationIssue]
    ) -> Dict[DataQualityDimension, float]:
        """Calculate data quality dimension scores."""
        scores = {}
        total_records = len(records)
        
        if total_records == 0:
            return {dim: 0.0 for dim in DataQualityDimension}
        
        # Group issues by type to calculate dimension scores
        issue_counts = {dim: 0 for dim in DataQualityDimension}
        
        for issue in issues:
            # Map issue types to quality dimensions
            if "completeness" in issue.message.lower() or "required" in issue.message.lower():
                issue_counts[DataQualityDimension.COMPLETENESS] += 1
            elif "consistency" in issue.message.lower() or "cross-field" in issue.message.lower():
                issue_counts[DataQualityDimension.CONSISTENCY] += 1
            elif "format" in issue.message.lower() or "pattern" in issue.message.lower():
                issue_counts[DataQualityDimension.VALIDITY] += 1
            elif "unique" in issue.message.lower():
                issue_counts[DataQualityDimension.UNIQUENESS] += 1
            elif "range" in issue.message.lower() or "type" in issue.message.lower():
                issue_counts[DataQualityDimension.ACCURACY] += 1
            else:
                issue_counts[DataQualityDimension.ACCURACY] += 1  # Default
        
        # Calculate scores (100 - percentage of records with issues)
        for dimension in DataQualityDimension:
            affected_records = min(issue_counts[dimension], total_records)
            scores[dimension] = max(0.0, (total_records - affected_records) / total_records * 100)
        
        return scores
    
    async def _store_validation_result(self, result: ValidationResult):
        """Store validation result to database."""
        try:
            async with self.async_session() as session:
                # Store validation result
                db_result = ValidationResultModel(
                    id=str(uuid.uuid4()),
                    dataset_id=result.dataset_id,
                    validation_id=result.validation_id,
                    timestamp=result.timestamp,
                    total_records=result.total_records,
                    passed_records=result.passed_records,
                    failed_records=result.failed_records,
                    quality_score=result.quality_score,
                    dimension_scores=json.dumps({k.value: v for k, v in result.dimension_scores.items()}),
                    execution_time=result.execution_time,
                    issues_summary=json.dumps({
                        'total_issues': len(result.issues),
                        'by_severity': {
                            severity.value: len([i for i in result.issues if i.severity == severity])
                            for severity in ValidationSeverity
                        }
                    }),
                    metadata=json.dumps(result.metadata)
                )
                session.add(db_result)
                
                # Store individual issues
                for issue in result.issues:
                    db_issue = ValidationIssueModel(
                        id=issue.id,
                        validation_result_id=result.validation_id,
                        rule_id=issue.rule_id,
                        field_name=issue.field_name,
                        severity=issue.severity.value,
                        message=issue.message,
                        actual_value=json.dumps(issue.actual_value) if issue.actual_value is not None else None,
                        expected_value=json.dumps(issue.expected_value) if issue.expected_value is not None else None,
                        row_identifier=issue.row_identifier,
                        timestamp=issue.timestamp,
                        metadata=json.dumps(issue.metadata)
                    )
                    session.add(db_issue)
                
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing validation result: {e}")
    
    async def _update_metrics(self, result: ValidationResult):
        """Update validation metrics."""
        self.validation_metrics['total_validations'] += 1
        self.validation_metrics['total_records_validated'] += result.total_records
        
        # Update average quality score
        total_validations = self.validation_metrics['total_validations']
        current_avg = self.validation_metrics['average_quality_score']
        self.validation_metrics['average_quality_score'] = (
            (current_avg * (total_validations - 1) + result.quality_score) / total_validations
        )
        
        # Update average execution time
        current_avg_time = self.validation_metrics['average_execution_time']
        self.validation_metrics['average_execution_time'] = (
            (current_avg_time * (total_validations - 1) + result.execution_time) / total_validations
        )
        
        # Update common issues
        for issue in result.issues:
            self.validation_metrics['common_issues'][issue.rule_id] += 1
    
    # Built-in validator functions
    async def _validate_email(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate email format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        email = record[rule.field_name]
        if not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    async def _validate_phone(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate phone number format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        phone = record[rule.field_name]
        if not isinstance(phone, str):
            return False
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Check for valid phone number lengths
        return len(digits) >= 10 and len(digits) <= 15
    
    async def _validate_url(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate URL format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        url = record[rule.field_name]
        if not isinstance(url, str):
            return False
        
        url_pattern = r'^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w\/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return re.match(url_pattern, url) is not None
    
    async def _validate_credit_card(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate credit card number using Luhn algorithm."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        card_number = record[rule.field_name]
        if not isinstance(card_number, str):
            return False
        
        # Remove spaces and dashes
        card_number = re.sub(r'[\s-]', '', card_number)
        
        # Check if all digits
        if not card_number.isdigit():
            return False
        
        # Luhn algorithm
        def luhn_check(card_num):
            total = 0
            reverse_digits = card_num[::-1]
            
            for i, digit in enumerate(reverse_digits):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                    if n > 9:
                        n = (n // 10) + (n % 10)
                total += n
            
            return total % 10 == 0
        
        return luhn_check(card_number)
    
    async def _validate_ip_address(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate IP address format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        ip = record[rule.field_name]
        if not isinstance(ip, str):
            return False
        
        # IPv4 pattern
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        return re.match(ipv4_pattern, ip) is not None
    
    async def _validate_date(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate date format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        date_value = record[rule.field_name]
        if isinstance(date_value, datetime):
            return True
        
        if not isinstance(date_value, str):
            return False
        
        try:
            dateutil.parser.parse(date_value)
            return True
        except (ValueError, TypeError):
            return False
    
    async def _validate_numeric(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate numeric format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        value = record[rule.field_name]
        
        if isinstance(value, (int, float, Decimal)):
            return True
        
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        
        return False
    
    async def _validate_text_length(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate text length."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        value = record[rule.field_name]
        if not isinstance(value, str):
            return False
        
        min_length = rule.metadata.get('min_length', 0)
        max_length = rule.metadata.get('max_length', float('inf'))
        
        return min_length <= len(value) <= max_length
    
    async def _validate_enum(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate enum values."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        value = record[rule.field_name]
        allowed_values = rule.metadata.get('allowed_values', [])
        
        return value in allowed_values
    
    async def _validate_json(self, record: Dict[str, Any], rule: ValidationRule, row_id: str) -> bool:
        """Validate JSON format."""
        if not rule.field_name or rule.field_name not in record:
            return True
        
        value = record[rule.field_name]
        if not isinstance(value, str):
            return False
        
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
    
    # Built-in cleaner functions
    def _clean_trim_whitespace(self, value: Any) -> Any:
        """Trim whitespace from string values."""
        return value.strip() if isinstance(value, str) else value
    
    def _clean_normalize_case(self, value: Any, case: str = 'lower') -> Any:
        """Normalize string case."""
        if not isinstance(value, str):
            return value
        
        if case == 'lower':
            return value.lower()
        elif case == 'upper':
            return value.upper()
        elif case == 'title':
            return value.title()
        
        return value
    
    def _clean_remove_special_chars(self, value: Any, keep_chars: str = '') -> Any:
        """Remove special characters from string."""
        if not isinstance(value, str):
            return value
        
        pattern = f'[^a-zA-Z0-9\\s{re.escape(keep_chars)}]'
        return re.sub(pattern, '', value)
    
    def _clean_standardize_phone(self, value: Any) -> Any:
        """Standardize phone number format."""
        if not isinstance(value, str):
            return value
        
        digits = re.sub(r'\D', '', value)
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return value
    
    def _clean_standardize_email(self, value: Any) -> Any:
        """Standardize email format."""
        if not isinstance(value, str):
            return value
        
        return value.lower().strip()
    
    def _clean_parse_date(self, value: Any, target_format: str = '%Y-%m-%d') -> Any:
        """Parse and standardize date format."""
        if isinstance(value, datetime):
            return value.strftime(target_format)
        
        if not isinstance(value, str):
            return value
        
        try:
            parsed_date = dateutil.parser.parse(value)
            return parsed_date.strftime(target_format)
        except (ValueError, TypeError):
            return value
    
    def _clean_normalize_numeric(self, value: Any) -> Any:
        """Normalize numeric values."""
        if isinstance(value, (int, float)):
            return value
        
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,£€¥]', '', value.strip())
            try:
                return float(cleaned)
            except ValueError:
                return value
        
        return value
    
    def _clean_remove_duplicates(self, values: List[Any]) -> List[Any]:
        """Remove duplicate values from list."""
        seen = set()
        result = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation performance metrics."""
        return self.validation_metrics.copy()
    
    async def profile_data(self, data: List[Dict[str, Any]]) -> Dict[str, DataProfile]:
        """Generate statistical profile of dataset."""
        if not data:
            return {}
        
        profiles = {}
        
        # Get all field names
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        for field_name in all_fields:
            values = [record.get(field_name) for record in data]
            non_null_values = [v for v in values if v is not None]
            
            profile = DataProfile(
                field_name=field_name,
                data_type=self._infer_data_type(non_null_values),
                total_count=len(values),
                null_count=len(values) - len(non_null_values),
                unique_count=len(set(non_null_values))
            )
            
            # Calculate statistics for numeric fields
            if profile.data_type in ['int', 'float'] and non_null_values:
                numeric_values = [float(v) for v in non_null_values if isinstance(v, (int, float))]
                if numeric_values:
                    profile.min_value = min(numeric_values)
                    profile.max_value = max(numeric_values)
                    profile.mean_value = statistics.mean(numeric_values)
                    profile.median_value = statistics.median(numeric_values)
                    if len(numeric_values) > 1:
                        profile.std_deviation = statistics.stdev(numeric_values)
                    
                    # Calculate percentiles
                    if PANDAS_AVAILABLE:
                        profile.percentiles = {
                            p: np.percentile(numeric_values, p)
                            for p in [25, 50, 75, 90, 95, 99]
                        }
            
            # Most common values
            from collections import Counter
            value_counts = Counter(non_null_values)
            profile.most_common_values = value_counts.most_common(10)
            
            # Pattern analysis for strings
            if profile.data_type == 'str' and non_null_values:
                string_values = [str(v) for v in non_null_values]
                profile.pattern_analysis = {
                    'avg_length': statistics.mean(len(s) for s in string_values),
                    'min_length': min(len(s) for s in string_values),
                    'max_length': max(len(s) for s in string_values),
                    'contains_digits': sum(1 for s in string_values if any(c.isdigit() for c in s)),
                    'contains_special_chars': sum(1 for s in string_values if not s.isalnum())
                }
            
            profiles[field_name] = profile
        
        return profiles
    
    def _infer_data_type(self, values: List[Any]) -> str:
        """Infer data type from values."""
        if not values:
            return 'unknown'
        
        type_counts = {}
        for value in values:
            value_type = type(value).__name__
            type_counts[value_type] = type_counts.get(value_type, 0) + 1
        
        # Return the most common type
        return max(type_counts, key=type_counts.get)


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize validation engine
        engine = DataValidationEngine(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await engine.initialize()
        
        # Define validation rules
        email_rule = ValidationRule(
            id="email_format",
            name="Email Format Validation",
            rule_type=ValidationRuleType.CUSTOM,
            field_name="email",
            custom_function=engine._validate_email,
            severity=ValidationSeverity.ERROR,
            error_message="Invalid email format"
        )
        
        age_range_rule = ValidationRule(
            id="age_range",
            name="Age Range Validation",
            rule_type=ValidationRuleType.RANGE,
            field_name="age",
            min_value=0,
            max_value=120,
            severity=ValidationSeverity.WARNING
        )
        
        required_name_rule = ValidationRule(
            id="required_name",
            name="Required Name Field",
            rule_type=ValidationRuleType.COMPLETENESS,
            field_name="name",
            severity=ValidationSeverity.ERROR
        )
        
        # Add rules to engine
        engine.add_validation_rule(email_rule)
        engine.add_validation_rule(age_range_rule)
        engine.add_validation_rule(required_name_rule)
        
        # Create rule set
        engine.add_rule_set("user_validation", ["email_format", "age_range", "required_name"])
        
        # Test data
        test_data = [
            {"name": "John Doe", "email": "john@example.com", "age": 30},
            {"name": "", "email": "invalid-email", "age": 150},
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25}
        ]
        
        # Validate data
        result = await engine.validate_data(test_data, rule_set="user_validation")
        
        print(f"Validation completed:")
        print(f"Quality score: {result.quality_score:.2f}%")
        print(f"Total records: {result.total_records}")
        print(f"Passed: {result.passed_records}")
        print(f"Failed: {result.failed_records}")
        print(f"Issues found: {len(result.issues)}")
        
        for issue in result.issues:
            print(f"- {issue.severity.value}: {issue.message}")
        
        # Generate data profile
        profiles = await engine.profile_data(test_data)
        for field_name, profile in profiles.items():
            print(f"\nProfile for {field_name}:")
            print(f"  Data type: {profile.data_type}")
            print(f"  Total count: {profile.total_count}")
            print(f"  Null count: {profile.null_count}")
            print(f"  Unique count: {profile.unique_count}")
    
    asyncio.run(main())