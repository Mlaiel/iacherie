"""
Configuration Validation Schema
==============================

Enterprise-grade configuration validation with comprehensive schema definitions,
type checking, and business rule validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationRuleType(Enum):
    """Types of validation rules."""
    TYPE_CHECK = "type_check"
    RANGE_CHECK = "range_check"
    PATTERN_CHECK = "pattern_check"
    CUSTOM_CHECK = "custom_check"
    DEPENDENCY_CHECK = "dependency_check"
    BUSINESS_RULE = "business_rule"

@dataclass
class ValidationRule:
    """Configuration validation rule."""
    name: str
    rule_type: ValidationRuleType
    validator: Callable[[Any], bool]
    message: str
    level: ValidationLevel = ValidationLevel.ERROR
    required: bool = True
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    critical: List[str] = field(default_factory=list)

class ValidationSchema:
    """
    Enterprise configuration validation schema.
    
    Provides comprehensive validation including:
    - Type validation
    - Range validation
    - Pattern validation
    - Custom business rules
    - Dependency validation
    - Performance constraint validation
    """
    
    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}
        self._setup_default_rules()
        
    def _setup_default_rules(self) -> None:
        """Setup default validation rules for IA Chérie configuration."""
        
        # Performance configuration validation
        self.add_performance_rules()
        
        # Security configuration validation
        self.add_security_rules()
        
        # Database configuration validation
        self.add_database_rules()
        
        # Creator economy configuration validation
        self.add_creator_economy_rules()
        
    def add_performance_rules(self) -> None:
        """Add performance configuration validation rules."""
        
        # Performance targets validation
        self.add_rule(
            "performance.cache_operations_p95",
            ValidationRule(
                name="cache_p95_threshold",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, (int, float)) and 0 < x <= 10,
                message="Cache P95 latency must be between 0 and 10ms",
                level=ValidationLevel.ERROR
            )
        )
        
        self.add_rule(
            "performance.database_operations_p95",
            ValidationRule(
                name="database_p95_threshold",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, (int, float)) and 0 < x <= 100,
                message="Database P95 latency must be between 0 and 100ms",
                level=ValidationLevel.WARNING
            )
        )
        
        # Memory configuration validation
        self.add_rule(
            "memory.max_heap_size_mb",
            ValidationRule(
                name="heap_size_limit",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, int) and 256 <= x <= 8192,
                message="Heap size must be between 256MB and 8GB",
                level=ValidationLevel.ERROR
            )
        )
        
        # CPU configuration validation
        self.add_rule(
            "cpu.max_worker_threads",
            ValidationRule(
                name="thread_count_limit",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, int) and 1 <= x <= 64,
                message="Worker threads must be between 1 and 64",
                level=ValidationLevel.WARNING
            )
        )
        
    def add_security_rules(self) -> None:
        """Add security configuration validation rules."""
        
        # Encryption algorithm validation
        self.add_rule(
            "security.encryption.symmetric_algorithm",
            ValidationRule(
                name="symmetric_algorithm_check",
                rule_type=ValidationRuleType.PATTERN_CHECK,
                validator=lambda x: x in ["AES-256-GCM", "AES-256-CBC", "ChaCha20-Poly1305"],
                message="Symmetric algorithm must be AES-256-GCM, AES-256-CBC, or ChaCha20-Poly1305",
                level=ValidationLevel.CRITICAL
            )
        )
        
        # Key rotation validation
        self.add_rule(
            "security.encryption.key_rotation_days",
            ValidationRule(
                name="key_rotation_period",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, int) and 30 <= x <= 365,
                message="Key rotation period must be between 30 and 365 days",
                level=ValidationLevel.ERROR
            )
        )
        
        # Password policy validation
        self.add_rule(
            "security.authentication.password_min_length",
            ValidationRule(
                name="password_min_length",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, int) and x >= 8,
                message="Minimum password length must be at least 8 characters",
                level=ValidationLevel.CRITICAL
            )
        )
        
        # JWT algorithm validation
        self.add_rule(
            "security.authentication.jwt_algorithm",
            ValidationRule(
                name="jwt_algorithm_check",
                rule_type=ValidationRuleType.PATTERN_CHECK,
                validator=lambda x: x in ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"],
                message="JWT algorithm must be a supported secure algorithm",
                level=ValidationLevel.ERROR
            )
        )
        
    def add_database_rules(self) -> None:
        """Add database configuration validation rules."""
        
        # Connection pool validation
        self.add_rule(
            "database.pool_size",
            ValidationRule(
                name="pool_size_limit",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, int) and 1 <= x <= 100,
                message="Database pool size must be between 1 and 100",
                level=ValidationLevel.ERROR
            )
        )
        
        # Timeout validation
        self.add_rule(
            "database.pool_timeout",
            ValidationRule(
                name="pool_timeout_limit",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, (int, float)) and 1 <= x <= 300,
                message="Pool timeout must be between 1 and 300 seconds",
                level=ValidationLevel.WARNING
            )
        )
        
    def add_creator_economy_rules(self) -> None:
        """Add creator economy configuration validation rules."""
        
        # File size limits
        self.add_rule(
            "file_management.max_file_size_mb",
            ValidationRule(
                name="file_size_limit",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, (int, float)) and 1 <= x <= 1000,
                message="Max file size must be between 1MB and 1GB",
                level=ValidationLevel.ERROR
            )
        )
        
        # Rate limiting validation
        self.add_rule(
            "rate_limiting.default_rpm",
            ValidationRule(
                name="rate_limit_check",
                rule_type=ValidationRuleType.RANGE_CHECK,
                validator=lambda x: isinstance(x, int) and 1 <= x <= 10000,
                message="Rate limit must be between 1 and 10,000 requests per minute",
                level=ValidationLevel.WARNING
            )
        )
        
    def add_rule(self, config_path: str, rule: ValidationRule) -> None:
        """
        Add validation rule for configuration path.
        
        Args:
            config_path: Dot-notation path to configuration value
            rule: Validation rule to add
        """
        if config_path not in self.rules:
            self.rules[config_path] = []
        self.rules[config_path].append(rule)
        
    def remove_rule(self, config_path: str, rule_name: str) -> bool:
        """
        Remove validation rule.
        
        Args:
            config_path: Configuration path
            rule_name: Name of rule to remove
            
        Returns:
            bool: True if rule was removed, False if not found
        """
        if config_path in self.rules:
            for i, rule in enumerate(self.rules[config_path]):
                if rule.name == rule_name:
                    del self.rules[config_path][i]
                    return True
        return False
        
    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            ValidationResult: Validation results
        """
        result = ValidationResult(is_valid=True)
        
        for config_path, rules in self.rules.items():
            value = self._get_nested_value(config, config_path)
            
            for rule in rules:
                validation_result = self._validate_rule(config_path, value, rule, config)
                self._merge_validation_results(result, validation_result)
                
        # Overall validation status
        result.is_valid = len(result.critical) == 0 and len(result.errors) == 0
        
        return result
        
    def _get_nested_value(self, config: Dict[str, Any], path: str) -> Any:
        """Get nested configuration value using dot notation."""
        keys = path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return None
            
    def _validate_rule(self, config_path: str, value: Any, rule: ValidationRule, 
                      full_config: Dict[str, Any]) -> ValidationResult:
        """Validate single rule."""
        result = ValidationResult(is_valid=True)
        
        # Check if value exists when required
        if rule.required and value is None:
            message = f"{config_path}: Required configuration is missing"
            self._add_message(result, message, ValidationLevel.ERROR)
            return result
            
        # Skip validation if value is None and not required
        if value is None and not rule.required:
            return result
            
        # Check dependencies
        if rule.dependencies:
            for dep in rule.dependencies:
                dep_value = self._get_nested_value(full_config, dep)
                if dep_value is None:
                    message = f"{config_path}: Dependency {dep} is missing"
                    self._add_message(result, message, ValidationLevel.ERROR)
                    return result
                    
        # Run validator
        try:
            is_valid = rule.validator(value)
            if not is_valid:
                self._add_message(result, f"{config_path}: {rule.message}", rule.level)
        except Exception as e:
            message = f"{config_path}: Validation error - {str(e)}"
            self._add_message(result, message, ValidationLevel.ERROR)
            
        return result
        
    def _add_message(self, result: ValidationResult, message: str, level: ValidationLevel) -> None:
        """Add validation message to result."""
        if level == ValidationLevel.CRITICAL:
            result.critical.append(message)
        elif level == ValidationLevel.ERROR:
            result.errors.append(message)
        elif level == ValidationLevel.WARNING:
            result.warnings.append(message)
        elif level == ValidationLevel.INFO:
            result.info.append(message)
            
    def _merge_validation_results(self, target: ValidationResult, source: ValidationResult) -> None:
        """Merge validation results."""
        target.critical.extend(source.critical)
        target.errors.extend(source.errors)
        target.warnings.extend(source.warnings)
        target.info.extend(source.info)
        
    def add_custom_validator(self, config_path: str, name: str, 
                           validator: Callable[[Any], bool], message: str,
                           level: ValidationLevel = ValidationLevel.ERROR) -> None:
        """
        Add custom validation rule.
        
        Args:
            config_path: Configuration path to validate
            name: Validator name
            validator: Validation function
            message: Error message
            level: Validation level
        """
        rule = ValidationRule(
            name=name,
            rule_type=ValidationRuleType.CUSTOM_CHECK,
            validator=validator,
            message=message,
            level=level
        )
        self.add_rule(config_path, rule)
        
    def validate_business_rules(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate business-specific rules."""
        result = ValidationResult(is_valid=True)
        
        # Creator economy business rules
        self._validate_creator_economy_business_rules(config, result)
        
        # Performance business rules
        self._validate_performance_business_rules(config, result)
        
        # Security business rules
        self._validate_security_business_rules(config, result)
        
        result.is_valid = len(result.critical) == 0 and len(result.errors) == 0
        return result
        
    def _validate_creator_economy_business_rules(self, config: Dict[str, Any], 
                                               result: ValidationResult) -> None:
        """Validate creator economy business rules."""
        # Rule: File size limits should be reasonable for creator content
        max_file_size = self._get_nested_value(config, "file_management.max_file_size_mb")
        if max_file_size and max_file_size > 500:
            self._add_message(
                result,
                "File size limit exceeds recommended 500MB for creator content",
                ValidationLevel.WARNING
            )
            
    def _validate_performance_business_rules(self, config: Dict[str, Any], 
                                           result: ValidationResult) -> None:
        """Validate performance business rules."""
        # Rule: Cache P95 should be lower than database P95
        cache_p95 = self._get_nested_value(config, "performance.cache_operations_p95")
        db_p95 = self._get_nested_value(config, "performance.database_operations_p95")
        
        if cache_p95 and db_p95 and cache_p95 >= db_p95:
            self._add_message(
                result,
                "Cache P95 latency should be lower than database P95 latency",
                ValidationLevel.WARNING
            )
            
    def _validate_security_business_rules(self, config: Dict[str, Any], 
                                        result: ValidationResult) -> None:
        """Validate security business rules."""
        # Rule: Production must have stronger security settings
        env = self._get_nested_value(config, "environment")
        if env == "production":
            # Check for production-specific security requirements
            mfa_required = self._get_nested_value(config, "security.authentication.require_mfa")
            if not mfa_required:
                self._add_message(
                    result,
                    "Production environment must require MFA authentication",
                    ValidationLevel.CRITICAL
                )