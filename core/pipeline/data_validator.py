"""Data Validator

Ultra-advanced data validation system for ensuring data quality and integrity
across all pipeline stages with AI-powered analysis and automated correction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic: Data Ingestion → Schema Validation → Quality Analysis → Anomaly Detection → Data Enrichment → Compliance Verification
"""

import asyncio
import logging
import time
import re
import hashlib
import json
import uuid
import statistics
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """
Validation types"""

    SCHEMA = "schema"
    FORMAT = "format"
    RANGE = "range"
    PATTERN = "pattern"
    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    INTEGRITY = "integrity"
    BUSINESS_RULE = "business_rule"
    ANOMALY = "anomaly"
    COMPLIANCE = "compliance"
    QUALITY = "quality"


class DataType(Enum):
    """Data types"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    URL = "url"
    JSON = "json"
    ARRAY = "array"
    OBJECT = "object"
    BINARY = "binary"
    UUID = "uuid"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"


class ValidationLevel(Enum):
    """Validation levels"""

    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ULTRA_STRICT = "ultra_strict"


class ValidationStatus(Enum):
    """Validation status"""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class CorrectionAction(Enum):
    """Data correction actions"""

    NONE = "none"
    REMOVE = "remove"
    REPLACE = "replace"
    TRANSFORM = "transform"
    NORMALIZE = "normalize"
    STANDARDIZE = "standardize"
    IMPUTE = "impute"
    SANITIZE = "sanitize"


@dataclass
class ValidationRule:
    """Data validation rule"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str = ""
    validation_type: ValidationType = ValidationType.SCHEMA
    field_name: str = ""
    data_type: DataType = DataType.STRING
    required: bool = True
    nullable: bool = False
    
    # Constraints
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable] = None
    
    # Business rules
    business_conditions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Correction settings
    auto_correct: bool = False
    correction_action: CorrectionAction = CorrectionAction.NONE
    default_value: Any = None
    
    # Metadata
    description: str = ""
    category: str = ""
    priority: int = 1
    enabled: bool = True


@dataclass
class ValidationResult:
    """Validation result"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    field_name: str = ""
    status: ValidationStatus = ValidationStatus.PASSED
    message: str = ""
    
    # Value information
    original_value: Any = None
    corrected_value: Any = None
    correction_applied: bool = False
    
    # Error details
    error_code: str = ""
    error_details: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    row_index: Optional[int] = None
    record_id: Optional[str] = None
    validation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Metrics
    confidence_score: float = 1.0
    impact_level: str = "low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "result_id": self.result_id,
            "rule_id": self.rule_id,
            "field_name": self.field_name,
            "status": self.status.value,
            "message": self.message,
            "original_value": self.original_value,
            "corrected_value": self.corrected_value,
            "correction_applied": self.correction_applied,
            "error_code": self.error_code,
            "error_details": self.error_details,
            "row_index": self.row_index,
            "record_id": self.record_id,
            "validation_timestamp": self.validation_timestamp.isoformat(),
            "confidence_score": self.confidence_score,
            "impact_level": self.impact_level
        }


@dataclass
class DataProfile:
    """Data profiling result"""
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    field_name: str = ""
    data_type: DataType = DataType.STRING
    
    # Statistical information
    total_count: int = 0
    null_count: int = 0
    unique_count: int = 0
    duplicate_count: int = 0
    
    # Numeric statistics (if applicable)
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_deviation: Optional[float] = None
    
    # String statistics (if applicable)
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    
    # Quality metrics
    completeness: float = 0.0  # (total_count - null_count) / total_count
    uniqueness: float = 0.0    # unique_count / total_count
    validity: float = 0.0      # valid_values / total_count
    
    # Pattern analysis
    common_patterns: List[str] = field(default_factory=list)
    anomalous_values: List[Any] = field(default_factory=list)
    
    # Value distribution
    value_frequency: Dict[Any, int] = field(default_factory=dict)
    
    # Profiling metadata
    profiled_at: datetime = field(default_factory=datetime.now)
    sample_size: int = 0


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = ""
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    
    # Summary statistics
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    corrected_records: int = 0
    
    # Validation results
    validation_results: List[ValidationResult] = field(default_factory=list)
    data_profiles: List[DataProfile] = field(default_factory=list)
    
    # Quality metrics
    overall_quality_score: float = 0.0
    field_quality_scores: Dict[str, float] = field(default_factory=dict)
    
    # Error analysis
    error_summary: Dict[str, int] = field(default_factory=dict)
    critical_errors: List[ValidationResult] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Timing
    validation_start: datetime = field(default_factory=datetime.now)
    validation_end: Optional[datetime] = None
    processing_time: float = 0.0
    
    def calculate_quality_score(self) -> float:
        """Calculate overall quality score"""
        if self.total_records == 0:
            return 0.0
        
        # Weight different types of issues
        weights = {
            ValidationStatus.PASSED: 1.0,
            ValidationStatus.WARNING: 0.8,
            ValidationStatus.FAILED: 0.0,
            ValidationStatus.ERROR: 0.0
        }
        
        total_weight = 0.0
        total_count = 0
        
        for result in self.validation_results:
            weight = weights.get(result.status, 0.0)
            total_weight += weight
            total_count += 1
        
        return (total_weight / max(total_count, 1)) * 100


class BaseValidator(ABC):
    """
Abstract base validator"""
    
    @abstractmethod
    async def validate(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """
Validate value against rule"""
        pass
    
    @abstractmethod
    def supports_type(self, data_type: DataType) -> bool:
        """
Check if validator supports data type"""
        pass


class SchemaValidator(BaseValidator):
    """
Schema validation"""
    
    async def validate(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """
Validate schema compliance"""
        result = ValidationResult(
            rule_id=rule.rule_id,
            field_name=rule.field_name,
            original_value=value
        )
        
        try:
            # Check required field
            if rule.required and (value is None or value == ""):
                result.status = ValidationStatus.FAILED
                result.message = f"Required field '{rule.field_name}' is missing"
                result.error_code = "REQUIRED_FIELD_MISSING"
                return result
            
            # Check nullable
            if value is None:
                if rule.nullable:
                    result.status = ValidationStatus.PASSED
                    result.message = "Null value allowed"
                else:
                    result.status = ValidationStatus.FAILED
                    result.message = f"Field '{rule.field_name}' cannot be null"
                    result.error_code = "NULL_NOT_ALLOWED"
                return result
            
            # Type validation
            if not self._validate_type(value, rule.data_type):
                result.status = ValidationStatus.FAILED
                result.message = f"Invalid type for field '{rule.field_name}'. Expected {rule.data_type.value}"
                result.error_code = "INVALID_TYPE"
                
                # Auto-correction attempt
                if rule.auto_correct:
                    corrected_value = self._attempt_type_correction(value, rule.data_type)
                    if corrected_value is not None:
                        result.corrected_value = corrected_value
                        result.correction_applied = True
                        result.status = ValidationStatus.WARNING
                        result.message += " (auto-corrected)"
                
                return result
            
            result.status = ValidationStatus.PASSED
            result.message = "Schema validation passed"
            return result
            
        except Exception as e:
            result.status = ValidationStatus.ERROR
            result.message = f"Schema validation error: {str(e)}"
            result.error_code = "VALIDATION_ERROR"
            return result
    
    def _validate_type(self, value: Any, expected_type: DataType) -> bool:
        """Validate data type"""
        try:
            if expected_type == DataType.STRING:
                return isinstance(value, str)
            elif expected_type == DataType.INTEGER:
                return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
            elif expected_type == DataType.FLOAT:
                return isinstance(value, (int, float)) or self._is_float_string(value)
            elif expected_type == DataType.BOOLEAN:
                return isinstance(value, bool) or value in ["true", "false", "True", "False", "1", "0"]
            elif expected_type == DataType.EMAIL:
                return isinstance(value, str) and self._is_valid_email(value)
            elif expected_type == DataType.URL:
                return isinstance(value, str) and self._is_valid_url(value)
            elif expected_type == DataType.UUID:
                return isinstance(value, str) and self._is_valid_uuid(value)
            elif expected_type == DataType.JSON:
                return self._is_valid_json(value)
            else:
                return True  # Default case
        except:
            return False
    
    def _is_float_string(self, value: str) -> bool:
        """Check if string represents a float"""
        try:
            float(value)
            return True
        except:
            return False
    
    def _is_valid_email(self, value: str) -> bool:
        """
Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    def _is_valid_url(self, value: str) -> bool:
        """
Validate URL format"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, value))
    
    def _is_valid_uuid(self, value: str) -> bool:
        """
Validate UUID format"""
        try:
            uuid.UUID(value)
            return True
        except:
            return False
    
    def _is_valid_json(self, value: Any) -> bool:
        """
Validate JSON format"""
        try:
            if isinstance(value, str):
                json.loads(value)
            return True
        except:
            return False
    
    def _attempt_type_correction(self, value: Any, target_type: DataType) -> Any:
        """
Attempt to correct type"""
        try:
            if target_type == DataType.INTEGER:
                if isinstance(value, str) and value.isdigit():
                    return int(value)
                elif isinstance(value, float):
                    return int(value)
            elif target_type == DataType.FLOAT:
                return float(value)
            elif target_type == DataType.STRING:
                return str(value)
            elif target_type == DataType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ["true", "1", "yes"]
                return bool(value)
        except:
            pass
        return None
    
    def supports_type(self, data_type: DataType) -> bool:
        """Check if validator supports data type"""
        return True


class RangeValidator(BaseValidator):
    """
Range and constraint validation"""
    
    async def validate(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """
Validate range constraints"""
        result = ValidationResult(
            rule_id=rule.rule_id,
            field_name=rule.field_name,
            original_value=value
        )
        
        if value is None and rule.nullable:
            result.status = ValidationStatus.PASSED
            return result
        
        try:
            # Numeric range validation
            if rule.data_type in [DataType.INTEGER, DataType.FLOAT]:
                numeric_value = float(value) if not isinstance(value, (int, float)) else value
                
                if rule.min_value is not None and numeric_value < rule.min_value:
                    result.status = ValidationStatus.FAILED
                    result.message = f"Value {numeric_value} is below minimum {rule.min_value}"
                    result.error_code = "VALUE_BELOW_MINIMUM"
                    
                    if rule.auto_correct and rule.correction_action == CorrectionAction.REPLACE:
                        result.corrected_value = rule.min_value
                        result.correction_applied = True
                        result.status = ValidationStatus.WARNING
                    
                    return result
                
                if rule.max_value is not None and numeric_value > rule.max_value:
                    result.status = ValidationStatus.FAILED
                    result.message = f"Value {numeric_value} is above maximum {rule.max_value}"
                    result.error_code = "VALUE_ABOVE_MAXIMUM"
                    
                    if rule.auto_correct and rule.correction_action == CorrectionAction.REPLACE:
                        result.corrected_value = rule.max_value
                        result.correction_applied = True
                        result.status = ValidationStatus.WARNING
                    
                    return result
            
            # String length validation
            elif rule.data_type == DataType.STRING:
                string_value = str(value)
                
                if rule.min_length is not None and len(string_value) < rule.min_length:
                    result.status = ValidationStatus.FAILED
                    result.message = f"String length {len(string_value)} is below minimum {rule.min_length}"
                    result.error_code = "STRING_TOO_SHORT"
                    return result
                
                if rule.max_length is not None and len(string_value) > rule.max_length:
                    result.status = ValidationStatus.FAILED
                    result.message = f"String length {len(string_value)} is above maximum {rule.max_length}"
                    result.error_code = "STRING_TOO_LONG"
                    
                    if rule.auto_correct and rule.correction_action == CorrectionAction.TRANSFORM:
                        result.corrected_value = string_value[:rule.max_length]
                        result.correction_applied = True
                        result.status = ValidationStatus.WARNING
                    
                    return result
            
            # Allowed values validation
            if rule.allowed_values and value not in rule.allowed_values:
                result.status = ValidationStatus.FAILED
                result.message = f"Value '{value}' not in allowed values: {rule.allowed_values}"
                result.error_code = "VALUE_NOT_ALLOWED"
                
                if rule.auto_correct and rule.default_value is not None:
                    result.corrected_value = rule.default_value
                    result.correction_applied = True
                    result.status = ValidationStatus.WARNING
                
                return result
            
            result.status = ValidationStatus.PASSED
            result.message = "Range validation passed"
            return result
            
        except Exception as e:
            result.status = ValidationStatus.ERROR
            result.message = f"Range validation error: {str(e)}"
            result.error_code = "VALIDATION_ERROR"
            return result
    
    def supports_type(self, data_type: DataType) -> bool:
        """Check if validator supports data type"""
        return data_type in [DataType.INTEGER, DataType.FLOAT, DataType.STRING]


class PatternValidator(BaseValidator):
    """
Pattern and format validation"""
    
    async def validate(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """
Validate pattern matching"""
        result = ValidationResult(
            rule_id=rule.rule_id,
            field_name=rule.field_name,
            original_value=value
        )
        
        if value is None and rule.nullable:
            result.status = ValidationStatus.PASSED
            return result
        
        try:
            string_value = str(value)
            
            if rule.pattern:
                if not re.match(rule.pattern, string_value):
                    result.status = ValidationStatus.FAILED
                    result.message = f"Value '{string_value}' does not match pattern '{rule.pattern}'"
                    result.error_code = "PATTERN_MISMATCH"
                    
                    # Attempt auto-correction for common patterns
                    if rule.auto_correct:
                        corrected_value = self._attempt_pattern_correction(string_value, rule.pattern)
                        if corrected_value:
                            result.corrected_value = corrected_value
                            result.correction_applied = True
                            result.status = ValidationStatus.WARNING
                    
                    return result
            
            result.status = ValidationStatus.PASSED
            result.message = "Pattern validation passed"
            return result
            
        except Exception as e:
            result.status = ValidationStatus.ERROR
            result.message = f"Pattern validation error: {str(e)}"
            result.error_code = "VALIDATION_ERROR"
            return result
    
    def _attempt_pattern_correction(self, value: str, pattern: str) -> Optional[str]:
        """Attempt to correct value to match pattern"""
        # Common pattern corrections
        try:
            # Phone number normalization
            if "phone" in pattern.lower() or r"\d" in pattern:
                # Remove non-digit characters
                digits_only = re.sub(r'\D', '', value)
                if len(digits_only) >= 10:
                    return digits_only
            
            # Email normalization
            if "@" in pattern and "@" in value:
                return value.lower().strip()
            
            # URL normalization
            if "http" in pattern.lower() and not value.startswith(("http://", "https://")):
                return "https://" + value
            
        except:
            pass
        
        return None
    
    def supports_type(self, data_type: DataType) -> bool:
        """Check if validator supports data type"""
        return data_type == DataType.STRING


class AnomalyDetector:
    """
AI-powered anomaly detection"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.AnomalyDetector")
        
        # Statistical thresholds
        self.z_score_threshold = self.config.get("z_score_threshold", 3.0)
        self.iqr_multiplier = self.config.get("iqr_multiplier", 1.5)
        
        # Historical data for learning
        self.field_statistics: Dict[str, Dict[str, Any]] = {}
    
    async def detect_anomalies(self, data: List[Dict[str, Any]], field_name: str) -> List[int]:
        """Detect anomalous values in dataset"""
        values = [record.get(field_name) for record in data if record.get(field_name) is not None]
        
        if not values:
            return []
        
        anomaly_indices = []
        
        # Numeric anomaly detection
        if all(isinstance(v, (int, float)) for v in values):
            anomaly_indices.extend(self._detect_numeric_anomalies(values, data, field_name))
        
        # String anomaly detection
        elif all(isinstance(v, str) for v in values):
            anomaly_indices.extend(self._detect_string_anomalies(values, data, field_name))
        
        return list(set(anomaly_indices))  # Remove duplicates
    
    def _detect_numeric_anomalies(self, values: List[Union[int, float]], data: List[Dict[str, Any]], field_name: str) -> List[int]:
        """
Detect numeric anomalies using statistical methods"""
        anomaly_indices = []
        
        if len(values) < 3:
            return anomaly_indices
        
        # Z-score method
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        if std_val > 0:
            for i, record in enumerate(data):
                value = record.get(field_name)
                if value is not None and isinstance(value, (int, float)):
                    z_score = abs((value - mean_val) / std_val)
                    if z_score > self.z_score_threshold:
                        anomaly_indices.append(i)
        
        # IQR method
        sorted_values = sorted(values)
        n = len(sorted_values)
        q1 = sorted_values[n // 4]
        q3 = sorted_values[3 * n // 4]
        iqr = q3 - q1
        
        if iqr > 0:
            lower_bound = q1 - self.iqr_multiplier * iqr
            upper_bound = q3 + self.iqr_multiplier * iqr
            
            for i, record in enumerate(data):
                value = record.get(field_name)
                if value is not None and isinstance(value, (int, float)):
                    if value < lower_bound or value > upper_bound:
                        anomaly_indices.append(i)
        
        return anomaly_indices
    
    def _detect_string_anomalies(self, values: List[str], data: List[Dict[str, Any]], field_name: str) -> List[int]:
        """
Detect string anomalies using pattern analysis"""
        anomaly_indices = []
        
        # Length-based anomalies
        lengths = [len(v) for v in values]
        if len(lengths) > 2:
            mean_length = statistics.mean(lengths)
            std_length = statistics.stdev(lengths) if len(lengths) > 1 else 0
            
            if std_length > 0:
                for i, record in enumerate(data):
                    value = record.get(field_name)
                    if value is not None and isinstance(value, str):
                        z_score = abs((len(value) - mean_length) / std_length)
                        if z_score > self.z_score_threshold:
                            anomaly_indices.append(i)
        
        # Pattern-based anomalies
        # Find common patterns
        patterns = defaultdict(int)
        for value in values:
            pattern = self._extract_pattern(value)
            patterns[pattern] += 1
        
        # Consider values with rare patterns as anomalies
        rare_threshold = max(1, len(values) * 0.05)  # 5% threshold
        rare_patterns = {p for p, count in patterns.items() if count <= rare_threshold}
        
        for i, record in enumerate(data):
            value = record.get(field_name)
            if value is not None and isinstance(value, str):
                pattern = self._extract_pattern(value)
                if pattern in rare_patterns:
                    anomaly_indices.append(i)
        
        return anomaly_indices
    
    def _extract_pattern(self, value: str) -> str:
        """
Extract pattern from string value"""
        # Replace digits with 'D', letters with 'L', special chars with 'S'
        pattern = ""
        for char in value:
            if char.isdigit():
                pattern += "D"
            elif char.isalpha():
                pattern += "L"
            elif char.isspace():
                pattern += " "
            else:
                pattern += "S"
        return pattern


class DataProfiler:
    """Advanced data profiling system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.DataProfiler")
    
    async def profile_dataset(self, data: List[Dict[str, Any]]) -> List[DataProfile]:
        """Profile entire dataset"""
        if not data:
            return []
        
        profiles = []
        
        # Get all field names
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # Profile each field
        for field_name in all_fields:
            profile = await self.profile_field(data, field_name)
            profiles.append(profile)
        
        return profiles
    
    async def profile_field(self, data: List[Dict[str, Any]], field_name: str) -> DataProfile:
        """
Profile individual field"""
        profile = DataProfile(field_name=field_name)
        
        # Extract values for this field
        values = []
        null_count = 0
        
        for record in data:
            if field_name in record:
                value = record[field_name]
                if value is None or value == "":
                    null_count += 1
                else:
                    values.append(value)
            else:
                null_count += 1
        
        profile.total_count = len(data)
        profile.null_count = null_count
        
        if not values:
            return profile
        
        # Detect data type
        profile.data_type = self._detect_data_type(values)
        
        # Basic statistics
        profile.unique_count = len(set(str(v) for v in values))
        profile.duplicate_count = len(values) - profile.unique_count
        
        # Quality metrics
        profile.completeness = (profile.total_count - profile.null_count) / profile.total_count if profile.total_count > 0 else 0
        profile.uniqueness = profile.unique_count / len(values) if values else 0
        
        # Type-specific profiling
        if profile.data_type in [DataType.INTEGER, DataType.FLOAT]:
            await self._profile_numeric_field(values, profile)
        elif profile.data_type == DataType.STRING:
            await self._profile_string_field(values, profile)
        
        # Value frequency analysis
        value_counts = defaultdict(int)
        for value in values:
            value_counts[value] += 1
        
        # Store top 20 most frequent values
        sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
        profile.value_frequency = dict(sorted_values[:20])
        
        # Validity assessment (simplified)
        profile.validity = self._assess_validity(values, profile.data_type)
        
        profile.sample_size = len(values)
        
        return profile
    
    def _detect_data_type(self, values: List[Any]) -> DataType:
        """Detect most likely data type"""
        if not values:
            return DataType.STRING
        
        # Sample some values for detection
        sample_size = min(100, len(values))
        sample_values = values[:sample_size]
        
        # Check for different types
        numeric_count = 0
        integer_count = 0
        float_count = 0
        boolean_count = 0
        email_count = 0
        url_count = 0
        date_count = 0
        
        for value in sample_values:
            str_value = str(value)
            
            # Numeric checks
            try:
                float_val = float(str_value)
                numeric_count += 1
                if float_val.is_integer():
                    integer_count += 1
                else:
                    float_count += 1
            except:
                pass
            
            # Boolean check
            if str_value.lower() in ["true", "false", "yes", "no", "1", "0"]:
                boolean_count += 1
            
            # Email check
            if "@" in str_value and "." in str_value:
                email_count += 1
            
            # URL check
            if str_value.startswith(("http://", "https://", "www.")):
                url_count += 1
            
            # Date check (simplified)
            if re.search(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', str_value):
                date_count += 1
        
        # Determine type based on majority
        threshold = sample_size * 0.8  # 80% threshold
        
        if integer_count >= threshold:
            return DataType.INTEGER
        elif numeric_count >= threshold:
            return DataType.FLOAT
        elif boolean_count >= threshold:
            return DataType.BOOLEAN
        elif email_count >= threshold:
            return DataType.EMAIL
        elif url_count >= threshold:
            return DataType.URL
        elif date_count >= threshold:
            return DataType.DATE
        else:
            return DataType.STRING
    
    async def _profile_numeric_field(self, values: List[Any], profile: DataProfile):
        """Profile numeric field"""
        try:
            numeric_values = [float(v) for v in values if self._is_numeric(v)]
            
            if numeric_values:
                profile.min_value = min(numeric_values)
                profile.max_value = max(numeric_values)
                profile.mean_value = statistics.mean(numeric_values)
                profile.median_value = statistics.median(numeric_values)
                profile.std_deviation = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
        except Exception as e:
            self.logger.warning(f"Error profiling numeric field: {e}")
    
    async def _profile_string_field(self, values: List[Any], profile: DataProfile):
        """Profile string field"""
        try:
            string_values = [str(v) for v in values]
            lengths = [len(s) for s in string_values]
            
            if lengths:
                profile.min_length = min(lengths)
                profile.max_length = max(lengths)
                profile.avg_length = statistics.mean(lengths)
            
            # Pattern analysis
            patterns = defaultdict(int)
            for value in string_values[:100]:  # Sample for performance
                pattern = self._extract_pattern(value)
                patterns[pattern] += 1
            
            # Store top 10 patterns
            sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
            profile.common_patterns = [pattern for pattern, count in sorted_patterns[:10]]
            
        except Exception as e:
            self.logger.warning(f"Error profiling string field: {e}")
    
    def _is_numeric(self, value: Any) -> bool:
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except:
            return False
    
    def _assess_validity(self, values: List[Any], data_type: DataType) -> float:
        """
Assess data validity based on type"""
        if not values:
            return 0.0
        
        valid_count = 0
        
        for value in values:
            if self._is_valid_for_type(value, data_type):
                valid_count += 1
        
        return valid_count / len(values)
    
    def _is_valid_for_type(self, value: Any, data_type: DataType) -> bool:
        """
Check if value is valid for data type"""
        try:
            str_value = str(value)
            
            if data_type == DataType.INTEGER:
                int(str_value)
                return True
            elif data_type == DataType.FLOAT:
                float(str_value)
                return True
            elif data_type == DataType.EMAIL:
                return "@" in str_value and "." in str_value
            elif data_type == DataType.URL:
                return str_value.startswith(("http://", "https://"))
            else:
                return True  # Default to valid for strings
        except:
            return False
    
    def _extract_pattern(self, value: str) -> str:
        """Extract pattern from string (same as in AnomalyDetector)"""
        pattern = ""
        for char in value:
            if char.isdigit():
                pattern += "D"
            elif char.isalpha():
                pattern += "L"
            elif char.isspace():
                pattern += " "
            else:
                pattern += "S"
        return pattern


class DataValidator:
    """
    Ultra-advanced data validation system for ensuring data quality and integrity
    across all pipeline stages with AI-powered analysis and automated correction.
    
    Features:
    - Comprehensive schema validation
    - Multi-type data validation (format, range, pattern, business rules)
    - AI-powered anomaly detection
    - Automated data profiling and analysis
    - Intelligent data correction and transformation
    - Real-time validation with configurable levels
    - Comprehensive reporting and analytics
    - Compliance and regulatory validation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Core components
        self.validators: Dict[ValidationType, BaseValidator] = {}
        self.anomaly_detector = AnomalyDetector(self.config.get("anomaly_detection", {}))
        self.profiler = DataProfiler(self.config.get("profiling", {}))
        
        # Validation rules
        self.validation_rules: Dict[str, List[ValidationRule]] = {}
        self.global_rules: List[ValidationRule] = []
        
        # Validation history
        self.validation_history: List[ValidationReport] = []
        
        # Initialize default validators
        self._initialize_validators()
        
        self.logger.info("Data Validator initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "validation_level": "standard",
            "auto_correction": True,
            "anomaly_detection": {
                "enabled": True,
                "z_score_threshold": 3.0,
                "iqr_multiplier": 1.5
            },
            "profiling": {
                "enabled": True,
                "sample_size": 1000
            },
            "reporting": {
                "detailed_reports": True,
                "include_recommendations": True
            },
            "performance": {
                "batch_size": 1000,
                "parallel_validation": True,
                "max_workers": 4
            }
        }
    
    def _initialize_validators(self):
        """Initialize built-in validators"""
        self.validators[ValidationType.SCHEMA] = SchemaValidator()
        self.validators[ValidationType.RANGE] = RangeValidator()
        self.validators[ValidationType.PATTERN] = PatternValidator()
    
    def register_validator(self, validation_type: ValidationType, validator: BaseValidator):
        """
Register custom validator"""
        self.validators[validation_type] = validator
        self.logger.info(f"Registered validator for type: {validation_type.value}")
    
    def add_validation_rule(self, dataset_name: str, rule: ValidationRule):
        """Add validation rule for dataset"""
        if dataset_name not in self.validation_rules:
            self.validation_rules[dataset_name] = []
        
        self.validation_rules[dataset_name].append(rule)
        self.logger.info(f"Added validation rule '{rule.rule_name}' for dataset '{dataset_name}'")
    
    def add_global_rule(self, rule: ValidationRule):
        """Add global validation rule"""
        self.global_rules.append(rule)
        self.logger.info(f"Added global validation rule: {rule.rule_name}")
    
    async def validate_dataset(
        self,
        data: List[Dict[str, Any]],
        dataset_name: str = "unknown",
        validation_level: Optional[ValidationLevel] = None
    ) -> ValidationReport:
        """Validate entire dataset"""
        start_time = datetime.now()
        
        report = ValidationReport(
            dataset_name=dataset_name,
            validation_level=validation_level or ValidationLevel(self.config["validation_level"]),
            validation_start=start_time,
            total_records=len(data)
        )
        
        try:
            # Get validation rules
            dataset_rules = self.validation_rules.get(dataset_name, [])
            all_rules = self.global_rules + dataset_rules
            
            if not all_rules:
                self.logger.warning(f"No validation rules found for dataset: {dataset_name}")
                return report
            
            # Data profiling
            if self.config["profiling"]["enabled"]:
                self.logger.info("Starting data profiling...")
                report.data_profiles = await self.profiler.profile_dataset(data)
            
            # Validation execution
            validation_results = []
            
            if self.config["performance"]["parallel_validation"]:
                validation_results = await self._validate_parallel(data, all_rules)
            else:
                validation_results = await self._validate_sequential(data, all_rules)
            
            report.validation_results = validation_results
            
            # Anomaly detection
            if self.config["anomaly_detection"]["enabled"]:
                await self._detect_and_report_anomalies(data, report)
            
            # Calculate metrics
            self._calculate_report_metrics(report)
            
            # Generate recommendations
            if self.config["reporting"]["include_recommendations"]:
                report.recommendations = self._generate_recommendations(report)
            
            # Finalize report
            report.validation_end = datetime.now()
            report.processing_time = (report.validation_end - report.validation_start).total_seconds()
            report.overall_quality_score = report.calculate_quality_score()
            
            # Store in history
            self.validation_history.append(report)
            
            self.logger.info(f"Dataset validation completed. Quality score: {report.overall_quality_score:.2f}")
            return report
            
        except Exception as e:
            self.logger.error(f"Dataset validation failed: {e}")
            report.validation_end = datetime.now()
            report.processing_time = (report.validation_end - report.validation_start).total_seconds()
            raise
    
    async def _validate_parallel(self, data: List[Dict[str, Any]], rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate data in parallel"""
        batch_size = self.config["performance"]["batch_size"]
        max_workers = self.config["performance"]["max_workers"]
        
        # Create batches
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        
        # Create validation tasks
        tasks = []
        for batch_idx, batch in enumerate(batches):
            task = asyncio.create_task(
                self._validate_batch(batch, rules, batch_idx * batch_size)
            )
            tasks.append(task)
            
            # Limit concurrent tasks
            if len(tasks) >= max_workers:
                completed_results = await asyncio.gather(*tasks)
                tasks = []
                
                # Collect results
                for batch_results in completed_results:
                    tasks.extend(batch_results)
        
        # Process remaining tasks
        if tasks:
            completed_results = await asyncio.gather(*tasks)
            all_results = []
            for batch_results in completed_results:
                all_results.extend(batch_results)
        else:
            all_results = []
        
        return all_results
    
    async def _validate_sequential(self, data: List[Dict[str, Any]], rules: List[ValidationRule]) -> List[ValidationResult]:
        """Validate data sequentially"""
        all_results = []
        
        for record_idx, record in enumerate(data):
            record_results = await self._validate_record(record, rules, record_idx)
            all_results.extend(record_results)
        
        return all_results
    
    async def _validate_batch(self, batch: List[Dict[str, Any]], rules: List[ValidationRule], start_idx: int) -> List[ValidationResult]:
        """
Validate a batch of records"""
        batch_results = []
        
        for record_idx, record in enumerate(batch):
            record_results = await self._validate_record(record, rules, start_idx + record_idx)
            batch_results.extend(record_results)
        
        return batch_results
    
    async def _validate_record(self, record: Dict[str, Any], rules: List[ValidationRule], record_idx: int) -> List[ValidationResult]:
        """
Validate single record against all rules"""
        results = []
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            value = record.get(rule.field_name)
            
            # Get appropriate validator
            validator = self.validators.get(rule.validation_type)
            if not validator:
                self.logger.warning(f"No validator found for type: {rule.validation_type.value}")
                continue
            
            # Validate
            result = await validator.validate(value, rule)
            result.row_index = record_idx
            result.record_id = record.get("id", str(record_idx))
            
            results.append(result)
        
        return results
    
    async def _detect_and_report_anomalies(self, data: List[Dict[str, Any]], report: ValidationReport):
        """Detect anomalies and add to report"""
        if not data:
            return
        
        # Get all fields
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # Detect anomalies for each field
        for field_name in all_fields:
            try:
                anomaly_indices = await self.anomaly_detector.detect_anomalies(data, field_name)
                
                # Create validation results for anomalies
                for idx in anomaly_indices:
                    if idx < len(data):
                        result = ValidationResult(
                            rule_id="anomaly_detection",
                            field_name=field_name,
                            status=ValidationStatus.WARNING,
                            message=f"Anomalous value detected in field '{field_name}'",
                            original_value=data[idx].get(field_name),
                            row_index=idx,
                            record_id=data[idx].get("id", str(idx)),
                            error_code="ANOMALY_DETECTED",
                            confidence_score=0.8,
                            impact_level="medium"
                        )
                        report.validation_results.append(result)
                        
            except Exception as e:
                self.logger.warning(f"Anomaly detection failed for field '{field_name}': {e}")
    
    def _calculate_report_metrics(self, report: ValidationReport):
        """Calculate report metrics"""
        if not report.validation_results:
            return
        
        # Count results by status
        status_counts = defaultdict(int)
        error_counts = defaultdict(int)
        field_results = defaultdict(list)
        
        for result in report.validation_results:
            status_counts[result.status] += 1
            
            if result.error_code:
                error_counts[result.error_code] += 1
            
            field_results[result.field_name].append(result)
            
            # Track critical errors
            if result.status == ValidationStatus.FAILED and result.impact_level == "high":
                report.critical_errors.append(result)
        
        # Update report statistics
        report.valid_records = status_counts[ValidationStatus.PASSED]
        report.invalid_records = status_counts[ValidationStatus.FAILED]
        report.corrected_records = sum(1 for r in report.validation_results if r.correction_applied)
        
        # Calculate field quality scores
        for field_name, results in field_results.items():
            if results:
                passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
                total = len(results)
                report.field_quality_scores[field_name] = (passed / total) * 100
        
        # Error summary
        report.error_summary = dict(error_counts)
    
    def _generate_recommendations(self, report: ValidationReport) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Quality-based recommendations
        if report.overall_quality_score < 80:
            recommendations.append("Overall data quality is below acceptable threshold (80%)")
        
        if report.critical_errors:
            recommendations.append(f"Address {len(report.critical_errors)} critical data quality issues")
        
        # Field-specific recommendations
        for field_name, quality_score in report.field_quality_scores.items():
            if quality_score < 90:
                recommendations.append(f"Improve data quality for field '{field_name}' (current: {quality_score:.1f}%)")
        
        # Error pattern recommendations
        common_errors = sorted(report.error_summary.items(), key=lambda x: x[1], reverse=True)
        if common_errors:
            top_error = common_errors[0]
            recommendations.append(f"Most common error: {top_error[0]} ({top_error[1]} occurrences)")
        
        # Profiling-based recommendations
        for profile in report.data_profiles:
            if profile.completeness < 0.95:
                recommendations.append(f"Improve completeness for field '{profile.field_name}' (current: {profile.completeness:.1%})")
            
            if profile.uniqueness < 0.8 and profile.data_type != DataType.BOOLEAN:
                recommendations.append(f"Review uniqueness of field '{profile.field_name}' (current: {profile.uniqueness:.1%})")
        
        return recommendations
    
    def get_validation_history(self) -> List[ValidationReport]:
        """Get validation history"""
        return self.validation_history.copy()
    
    def get_field_statistics(self, dataset_name: str) -> Dict[str, Any]:
        """
Get field statistics for dataset"""
        dataset_reports = [r for r in self.validation_history if r.dataset_name == dataset_name]
        
        if not dataset_reports:
            return {}
        
        latest_report = max(dataset_reports, key=lambda r: r.validation_start)
        
        field_stats = {}
        for profile in latest_report.data_profiles:
            field_stats[profile.field_name] = {
                "data_type": profile.data_type.value,
                "completeness": profile.completeness,
                "uniqueness": profile.uniqueness,
                "validity": profile.validity,
                "quality_score": latest_report.field_quality_scores.get(profile.field_name, 0)
            }
        
        return field_stats
    
    async def validate_single_record(
        self,
        record: Dict[str, Any],
        dataset_name: str = "unknown"
    ) -> List[ValidationResult]:
        """Validate single record"""
        dataset_rules = self.validation_rules.get(dataset_name, [])
        all_rules = self.global_rules + dataset_rules
        
        return await self._validate_record(record, all_rules, 0)
    
    def create_validation_rule(
        self,
        field_name: str,
        validation_type: ValidationType,
        data_type: DataType,
        **kwargs
    ) -> ValidationRule:
        """
Helper to create validation rule"""
        return ValidationRule(
            rule_name=kwargs.get("rule_name", f"{field_name}_{validation_type.value}"),
            validation_type=validation_type,
            field_name=field_name,
            data_type=data_type,
            required=kwargs.get("required", True),
            nullable=kwargs.get("nullable", False),
            min_value=kwargs.get("min_value"),
            max_value=kwargs.get("max_value"),
            min_length=kwargs.get("min_length"),
            max_length=kwargs.get("max_length"),
            pattern=kwargs.get("pattern"),
            allowed_values=kwargs.get("allowed_values"),
            auto_correct=kwargs.get("auto_correct", False),
            correction_action=kwargs.get("correction_action", CorrectionAction.NONE),
            default_value=kwargs.get("default_value"),
            description=kwargs.get("description", ""),
            category=kwargs.get("category", ""),
            priority=kwargs.get("priority", 1)
        )
    
    async def auto_generate_rules(self, data: List[Dict[str, Any]], dataset_name: str) -> List[ValidationRule]:
        """Auto-generate validation rules based on data analysis"""
        if not data:
            return []
        
        # Profile the data first
        profiles = await self.profiler.profile_dataset(data)
        
        rules = []
        
        for profile in profiles:
            # Basic schema rule
            schema_rule = self.create_validation_rule(
                field_name=profile.field_name,
                validation_type=ValidationType.SCHEMA,
                data_type=profile.data_type,
                rule_name=f"{profile.field_name}_schema",
                required=profile.completeness > 0.95,
                nullable=profile.completeness < 1.0
            )
            rules.append(schema_rule)
            
            # Range rules for numeric fields
            if profile.data_type in [DataType.INTEGER, DataType.FLOAT] and profile.min_value is not None:
                range_rule = self.create_validation_rule(
                    field_name=profile.field_name,
                    validation_type=ValidationType.RANGE,
                    data_type=profile.data_type,
                    rule_name=f"{profile.field_name}_range",
                    min_value=profile.min_value,
                    max_value=profile.max_value
                )
                rules.append(range_rule)
            
            # Length rules for string fields
            if profile.data_type == DataType.STRING and profile.min_length is not None:
                length_rule = self.create_validation_rule(
                    field_name=profile.field_name,
                    validation_type=ValidationType.RANGE,
                    data_type=profile.data_type,
                    rule_name=f"{profile.field_name}_length",
                    min_length=profile.min_length,
                    max_length=profile.max_length
                )
                rules.append(length_rule)
        
        # Add rules to dataset
        for rule in rules:
            self.add_validation_rule(dataset_name, rule)
        
        self.logger.info(f"Auto-generated {len(rules)} validation rules for dataset '{dataset_name}'")
        return rules
