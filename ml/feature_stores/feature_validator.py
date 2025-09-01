"""Feature Validator - Comprehensive feature validation and quality assurance

Provides validation, quality checks, and monitoring for features in the
centralized feature store.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import re

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRule(Enum):
    """Built-in validation rules"""
    NOT_NULL = "not_null"
    RANGE_CHECK = "range_check"
    TYPE_CHECK = "type_check"
    REGEX_MATCH = "regex_match"
    UNIQUENESS = "uniqueness"
    COMPLETENESS = "completeness"
    FRESHNESS = "freshness"
    CONSISTENCY = "consistency"


@dataclass
class ValidationResult:
    """Feature validation result"""
    feature_name: str
    rule_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QualityMetrics:
    """Feature quality metrics"""
    completeness: float = 0.0
    uniqueness: float = 0.0
    validity: float = 0.0
    consistency: float = 0.0
    freshness: float = 0.0
    overall_score: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.now)


class FeatureValidator:
    """Advanced feature validation and quality assurance"""
    
    def __init__(self):
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self.validation_history: List[ValidationResult] = []
        self.quality_thresholds = {
            "completeness": 0.95,
            "uniqueness": 0.99,
            "validity": 0.98,
            "consistency": 0.97,
            "freshness": 0.90,
            "overall": 0.95
        }
        
        # Initialize built-in validation rules
        self._initialize_builtin_rules()
        
        logger.info("Feature validator initialized")
    
    
    async def validate_feature(self, feature_name: str, data: Any, 
                               rules: List[str] = None) -> List[ValidationResult]:
        """Validate feature data against specified rules"""
        try:
            results = []
            
            # Use all rules if none specified
            if rules is None:
                rules = list(self.validation_rules.get(feature_name, {}).keys())
            
            for rule_name in rules:
                if feature_name in self.validation_rules and rule_name in self.validation_rules[feature_name]:
                    rule_config = self.validation_rules[feature_name][rule_name]
                    result = await self._apply_validation_rule(feature_name, data, rule_name, rule_config)
                    results.append(result)
                elif rule_name in self.custom_validators:
                    result = await self._apply_custom_validator(feature_name, data, rule_name)
                    results.append(result)
                else:
                    logger.warning(f"Validation rule not found: {rule_name}")
            
            # Store results in history
            self.validation_history.extend(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Feature validation failed: {e}")
            return []
    
    
    async def calculate_quality_metrics(self, feature_name: str, data: Any) -> QualityMetrics:
        """Calculate comprehensive quality metrics for feature data"""
        try:
            metrics = QualityMetrics()
            
            if data is None:
                return metrics
            
            # Convert data to list if needed
            if not isinstance(data, list):
                data = [data]
            
            total_count = len(data)
            if total_count == 0:
                return metrics
            
            # Completeness (non-null values)
            non_null_count = sum(1 for item in data if item is not None)
            metrics.completeness = non_null_count / total_count
            
            # Uniqueness (for applicable data types)
            try:
                unique_count = len(set(str(item) for item in data if item is not None))
                metrics.uniqueness = unique_count / non_null_count if non_null_count > 0 else 0
            except:
                metrics.uniqueness = 1.0  # Default for non-hashable types
            
            # Validity (basic type/format checks)
            valid_count = await self._count_valid_values(data)
            metrics.validity = valid_count / total_count
            
            # Consistency (variance from expected patterns)
            metrics.consistency = await self._calculate_consistency(data)
            
            # Freshness (time-based, simplified)
            metrics.freshness = 1.0  # Assume fresh data for now
            
            # Overall score (weighted average)
            weights = {
                "completeness": 0.25,
                "uniqueness": 0.15,
                "validity": 0.25,
                "consistency": 0.20,
                "freshness": 0.15
            }
            
            metrics.overall_score = (
                metrics.completeness * weights["completeness"] +
                metrics.uniqueness * weights["uniqueness"] +
                metrics.validity * weights["validity"] +
                metrics.consistency * weights["consistency"] +
                metrics.freshness * weights["freshness"]
            )
            
            logger.debug(f"Quality metrics calculated for {feature_name}: {metrics.overall_score:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Quality metrics calculation failed: {e}")
            return QualityMetrics()
    
    
    async def add_validation_rule(self, feature_name: str, rule_name: str, 
                                  rule_config: Dict[str, Any]) -> bool:
        """Add a validation rule for a feature"""
        try:
            if feature_name not in self.validation_rules:
                self.validation_rules[feature_name] = {}
            
            self.validation_rules[feature_name][rule_name] = rule_config
            
            logger.info(f"Validation rule added: {feature_name}.{rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Validation rule addition failed: {e}")
            return False
    
    
    async def add_custom_validator(self, rule_name: str, validator_func: Callable) -> bool:
        """Add a custom validation function"""
        try:
            self.custom_validators[rule_name] = validator_func
            
            logger.info(f"Custom validator added: {rule_name}")
            return True
            
        except Exception as e:
            logger.error(f"Custom validator addition failed: {e}")
            return False
    
    
    async def get_validation_report(self, feature_name: str = None, 
                                    days_back: int = 7) -> Dict[str, Any]:
        """Generate a validation report"""
        try:
            cutoff_date = datetime.now() - datetime.timedelta(days=days_back)
            
            # Filter results
            if feature_name:
                results = [r for r in self.validation_history 
                          if r.feature_name == feature_name and r.timestamp >= cutoff_date]
            else:
                results = [r for r in self.validation_history if r.timestamp >= cutoff_date]
            
            if not results:
                return {"message": "No validation results found"}
            
            # Aggregate statistics
            total_validations = len(results)
            passed_validations = sum(1 for r in results if r.passed)
            
            severity_counts = {}
            for severity in ValidationSeverity:
                severity_counts[severity.value] = sum(1 for r in results 
                                                     if r.severity == severity and not r.passed)
            
            # Feature-wise breakdown
            feature_breakdown = {}
            for result in results:
                feature = result.feature_name
                if feature not in feature_breakdown:
                    feature_breakdown[feature] = {"total": 0, "passed": 0, "failed": 0}
                
                feature_breakdown[feature]["total"] += 1
                if result.passed:
                    feature_breakdown[feature]["passed"] += 1
                else:
                    feature_breakdown[feature]["failed"] += 1
            
            return {
                "summary": {
                    "total_validations": total_validations,
                    "passed_validations": passed_validations,
                    "failed_validations": total_validations - passed_validations,
                    "success_rate": passed_validations / total_validations if total_validations > 0 else 0
                },
                "severity_breakdown": severity_counts,
                "feature_breakdown": feature_breakdown,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Validation report generation failed: {e}")
            return {"error": str(e)}
    
    
    async def check_quality_thresholds(self, metrics: QualityMetrics) -> List[str]:
        """Check if quality metrics meet defined thresholds"""
        violations = []
        
        try:
            if metrics.completeness < self.quality_thresholds["completeness"]:
                violations.append(f"Completeness below threshold: {metrics.completeness:.3f} < {self.quality_thresholds['completeness']}")
            
            if metrics.uniqueness < self.quality_thresholds["uniqueness"]:
                violations.append(f"Uniqueness below threshold: {metrics.uniqueness:.3f} < {self.quality_thresholds['uniqueness']}")
            
            if metrics.validity < self.quality_thresholds["validity"]:
                violations.append(f"Validity below threshold: {metrics.validity:.3f} < {self.quality_thresholds['validity']}")
            
            if metrics.consistency < self.quality_thresholds["consistency"]:
                violations.append(f"Consistency below threshold: {metrics.consistency:.3f} < {self.quality_thresholds['consistency']}")
            
            if metrics.freshness < self.quality_thresholds["freshness"]:
                violations.append(f"Freshness below threshold: {metrics.freshness:.3f} < {self.quality_thresholds['freshness']}")
            
            if metrics.overall_score < self.quality_thresholds["overall"]:
                violations.append(f"Overall quality below threshold: {metrics.overall_score:.3f} < {self.quality_thresholds['overall']}")
            
        except Exception as e:
            logger.error(f"Quality threshold check failed: {e}")
            violations.append(f"Threshold check error: {e}")
        
        return violations
    
    
    def _initialize_builtin_rules(self):
        """Initialize built-in validation rules"""
        self.builtin_rules = {
            ValidationRule.NOT_NULL: self._validate_not_null,
            ValidationRule.RANGE_CHECK: self._validate_range,
            ValidationRule.TYPE_CHECK: self._validate_type,
            ValidationRule.REGEX_MATCH: self._validate_regex,
            ValidationRule.UNIQUENESS: self._validate_uniqueness,
            ValidationRule.COMPLETENESS: self._validate_completeness
        }
    
    
    async def _apply_validation_rule(self, feature_name: str, data: Any, 
                                     rule_name: str, rule_config: Dict[str, Any]) -> ValidationResult:
        """Apply a specific validation rule"""
        try:
            rule_type = ValidationRule(rule_config.get("type", rule_name))
            
            if rule_type in self.builtin_rules:
                passed, message, details = await self.builtin_rules[rule_type](data, rule_config)
            else:
                passed, message, details = False, f"Unknown rule type: {rule_type}", {}
            
            severity = ValidationSeverity(rule_config.get("severity", "error"))
            
            return ValidationResult(
                feature_name=feature_name,
                rule_name=rule_name,
                passed=passed,
                severity=severity,
                message=message,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Validation rule application failed: {e}")
            return ValidationResult(
                feature_name=feature_name,
                rule_name=rule_name,
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Validation error: {e}"
            )
    
    
    async def _apply_custom_validator(self, feature_name: str, data: Any, 
                                      rule_name: str) -> ValidationResult:
        """Apply a custom validation function"""
        try:
            validator_func = self.custom_validators[rule_name]
            result = await validator_func(data) if asyncio.iscoroutinefunction(validator_func) else validator_func(data)
            
            if isinstance(result, bool):
                passed = result
                message = "Custom validation passed" if result else "Custom validation failed"
                details = {}
            elif isinstance(result, tuple) and len(result) >= 2:
                passed, message = result[:2]
                details = result[2] if len(result) > 2 else {}
            else:
                passed = bool(result)
                message = str(result)
                details = {}
            
            return ValidationResult(
                feature_name=feature_name,
                rule_name=rule_name,
                passed=passed,
                severity=ValidationSeverity.WARNING,
                message=message,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Custom validator application failed: {e}")
            return ValidationResult(
                feature_name=feature_name,
                rule_name=rule_name,
                passed=False,
                severity=ValidationSeverity.ERROR,
                message=f"Custom validation error: {e}"
            )
    
    
    async def _validate_not_null(self, data: Any, config: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """Validate that data is not null"""
        if isinstance(data, list):
            null_count = sum(1 for item in data if item is None)
            total_count = len(data)
            null_rate = null_count / total_count if total_count > 0 else 0
            
            threshold = config.get("null_threshold", 0.0)
            passed = null_rate <= threshold
            
            return passed, f"Null rate: {null_rate:.3f} (threshold: {threshold})", {
                "null_count": null_count,
                "total_count": total_count,
                "null_rate": null_rate
            }
        else:
            passed = data is not None
            return passed, "Not null check", {"is_null": data is None}
    
    
    async def _validate_range(self, data: Any, config: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """Validate that numeric data is within range"""
        try:
            min_val = config.get("min")
            max_val = config.get("max")
            
            if isinstance(data, list):
                numeric_data = [item for item in data if isinstance(item, (int, float))]
                
                if not numeric_data:
                    return False, "No numeric data found", {}
                
                violations = []
                if min_val is not None:
                    violations.extend([item for item in numeric_data if item < min_val])
                if max_val is not None:
                    violations.extend([item for item in numeric_data if item > max_val])
                
                passed = len(violations) == 0
                return passed, f"Range check (min: {min_val}, max: {max_val})", {
                    "violations": len(violations),
                    "total_checked": len(numeric_data)
                }
            else:
                if not isinstance(data, (int, float)):
                    return False, "Data is not numeric", {"data_type": type(data).__name__}
                
                passed = True
                if min_val is not None and data < min_val:
                    passed = False
                if max_val is not None and data > max_val:
                    passed = False
                
                return passed, f"Range check: {data} (min: {min_val}, max: {max_val})", {
                    "value": data,
                    "min": min_val,
                    "max": max_val
                }
                
        except Exception as e:
            return False, f"Range validation error: {e}", {}
    
    
    async def _validate_type(self, data: Any, config: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """Validate data type"""
        expected_type = config.get("expected_type")
        
        if expected_type is None:
            return False, "No expected type specified", {}
        
        try:
            if isinstance(data, list):
                type_counts = {}
                for item in data:
                    item_type = type(item).__name__
                    type_counts[item_type] = type_counts.get(item_type, 0) + 1
                
                # Check if majority matches expected type
                expected_count = type_counts.get(expected_type, 0)
                total_count = len(data)
                type_rate = expected_count / total_count if total_count > 0 else 0
                
                threshold = config.get("type_threshold", 0.95)
                passed = type_rate >= threshold
                
                return passed, f"Type consistency: {type_rate:.3f} (threshold: {threshold})", {
                    "type_counts": type_counts,
                    "expected_type": expected_type,
                    "type_rate": type_rate
                }
            else:
                actual_type = type(data).__name__
                passed = actual_type == expected_type
                
                return passed, f"Type check: {actual_type} (expected: {expected_type})", {
                    "actual_type": actual_type,
                    "expected_type": expected_type
                }
                
        except Exception as e:
            return False, f"Type validation error: {e}", {}
    
    
    async def _validate_regex(self, data: Any, config: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """Validate data against regex pattern"""
        pattern = config.get("pattern")
        
        if pattern is None:
            return False, "No regex pattern specified", {}
        
        try:
            regex = re.compile(pattern)
            
            if isinstance(data, list):
                matches = sum(1 for item in data if isinstance(item, str) and regex.match(item))
                string_items = sum(1 for item in data if isinstance(item, str))
                
                if string_items == 0:
                    return False, "No string data found", {}
                
                match_rate = matches / string_items
                threshold = config.get("match_threshold", 1.0)
                passed = match_rate >= threshold
                
                return passed, f"Regex match rate: {match_rate:.3f} (threshold: {threshold})", {
                    "matches": matches,
                    "string_items": string_items,
                    "match_rate": match_rate,
                    "pattern": pattern
                }
            else:
                if not isinstance(data, str):
                    return False, "Data is not a string", {"data_type": type(data).__name__}
                
                passed = bool(regex.match(data))
                return passed, f"Regex match: {pattern}", {
                    "value": data,
                    "pattern": pattern,
                    "matched": passed
                }
                
        except Exception as e:
            return False, f"Regex validation error: {e}", {}
    
    
    async def _validate_uniqueness(self, data: Any, config: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """Validate data uniqueness"""
        if not isinstance(data, list):
            return True, "Single value is unique", {}
        
        try:
            unique_count = len(set(str(item) for item in data if item is not None))
            total_count = len([item for item in data if item is not None])
            
            if total_count == 0:
                return True, "No data to check uniqueness", {}
            
            uniqueness_rate = unique_count / total_count
            threshold = config.get("uniqueness_threshold", 0.95)
            passed = uniqueness_rate >= threshold
            
            return passed, f"Uniqueness rate: {uniqueness_rate:.3f} (threshold: {threshold})", {
                "unique_count": unique_count,
                "total_count": total_count,
                "uniqueness_rate": uniqueness_rate
            }
            
        except Exception as e:
            return False, f"Uniqueness validation error: {e}", {}
    
    
    async def _validate_completeness(self, data: Any, config: Dict[str, Any]) -> Tuple[bool, str, Dict]:
        """Validate data completeness"""
        if not isinstance(data, list):
            passed = data is not None
            return passed, "Completeness check", {"is_complete": passed}
        
        try:
            non_null_count = sum(1 for item in data if item is not None)
            total_count = len(data)
            
            if total_count == 0:
                return False, "No data provided", {}
            
            completeness_rate = non_null_count / total_count
            threshold = config.get("completeness_threshold", 0.95)
            passed = completeness_rate >= threshold
            
            return passed, f"Completeness rate: {completeness_rate:.3f} (threshold: {threshold})", {
                "non_null_count": non_null_count,
                "total_count": total_count,
                "completeness_rate": completeness_rate
            }
            
        except Exception as e:
            return False, f"Completeness validation error: {e}", {}
    
    
    async def _count_valid_values(self, data: List[Any]) -> int:
        """Count valid values in data (simplified implementation)"""
        try:
            valid_count = 0
            for item in data:
                if item is not None:
                    # Basic validity checks
                    if isinstance(item, str) and len(item.strip()) > 0:
                        valid_count += 1
                    elif isinstance(item, (int, float)) and not (isinstance(item, float) and (item != item)):  # NaN check
                        valid_count += 1
                    elif isinstance(item, bool):
                        valid_count += 1
                    elif hasattr(item, '__len__') and len(item) > 0:
                        valid_count += 1
            
            return valid_count
            
        except Exception as e:
            logger.error(f"Valid value counting failed: {e}")
            return 0
    
    
    async def _calculate_consistency(self, data: List[Any]) -> float:
        """Calculate data consistency score (simplified implementation)"""
        try:
            if not data:
                return 0.0
            
            # For numeric data, calculate coefficient of variation
            numeric_data = [item for item in data if isinstance(item, (int, float))]
            if len(numeric_data) > 1:
                mean_val = statistics.mean(numeric_data)
                if mean_val != 0:
                    std_dev = statistics.stdev(numeric_data)
                    cv = std_dev / abs(mean_val)
                    # Convert to consistency score (lower CV = higher consistency)
                    return max(0.0, 1.0 - min(cv, 1.0))
            
            # For other data types, check format consistency
            if isinstance(data[0], str):
                # Simple pattern consistency check
                length_consistency = 1.0 - (statistics.stdev([len(str(item)) for item in data if item is not None]) / statistics.mean([len(str(item)) for item in data if item is not None])) if len(data) > 1 else 1.0
                return max(0.0, min(1.0, length_consistency))
            
            return 1.0  # Default consistency for other types
            
        except Exception as e:
            logger.error(f"Consistency calculation failed: {e}")
            return 0.0