"""🚀 Event Validator System - IA Influencer Agent Platform
===========================================================
Module: events/event_validator.py
Author: Fahed Mlaiel (mlaiel@live.de)
===========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 EVENT VALIDATION FRAMEWORK
Comprehensive event validation and business rule enforcement
- Schema validation with JSON Schema
- Business rule validation
- Data integrity checks
- Cross-field validation
- Performance optimized validation
"""

import re
import logging
from typing import Dict, List, Optional, Any, Callable, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import jsonschema
from decimal import Decimal

from .core.base_event import BaseEvent
from .core.exceptions import EventValidationError
from .event_registry import get_global_registry

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Validation result container"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add validation error"""
        self.valid = False
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        """Add validation warning"""
        self.warnings.append(message)
    
    def add_info(self, message: str) -> None:
        """Add validation info"""
        self.info.append(message)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result"""
        if not other.valid:
            self.valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)


@dataclass
class ValidationRule:
    """Custom validation rule definition"""
    rule_id: str
    name: str
    description: str
    validator_func: Callable[[BaseEvent], ValidationResult]
    event_patterns: List[str] = field(default_factory=list)
    severity: ValidationSeverity = ValidationSeverity.ERROR
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def applies_to_event(self, event: BaseEvent) -> bool:
        """Check if rule applies to event"""
        if not self.active:
            return False
        
        if not self.event_patterns:
            return True  # Applies to all events
        
        for pattern in self.event_patterns:
            if pattern == "*" or pattern == event.event_type:
                return True
            if pattern.endswith("*") and event.event_type.startswith(pattern[:-1]):
                return True
        
        return False


class EventValidator:
    """Comprehensive event validation system"""
    
    def __init__(self,
                 enable_schema_validation: bool = True,
                 enable_business_rules: bool = True,
                 strict_mode: bool = False):
        """Initialize event validator
        
        Args:
            enable_schema_validation: Enable JSON schema validation
            enable_business_rules: Enable business rule validation
            strict_mode: Fail validation on warnings
        """
        self.enable_schema_validation = enable_schema_validation
        self.enable_business_rules = enable_business_rules
        self.strict_mode = strict_mode
        
        # Validation rules
        self.custom_rules: Dict[str, ValidationRule] = {}
        
        # Validation statistics
        self.validation_count = 0
        self.validation_failures = 0
        self.rule_execution_count: Dict[str, int] = {}
        
        # Initialize built-in rules
        self._register_builtin_rules()
        
        logger.info("Event validator initialized")
    
    def validate(self, event: BaseEvent) -> ValidationResult:
        """Validate an event comprehensively
        
        Args:
            event: Event to validate
            
        Returns:
            Validation result
        """
        self.validation_count += 1
        result = ValidationResult(valid=True)
        
        try:
            # Basic structure validation
            structure_result = self._validate_basic_structure(event)
            result.merge(structure_result)
            
            # Schema validation
            if self.enable_schema_validation:
                schema_result = self._validate_schema(event)
                result.merge(schema_result)
            
            # Business rules validation
            if self.enable_business_rules:
                rules_result = self._validate_business_rules(event)
                result.merge(rules_result)
            
            # Custom rules validation
            custom_result = self._validate_custom_rules(event)
            result.merge(custom_result)
            
            # Strict mode check
            if self.strict_mode and result.warnings:
                result.valid = False
                result.errors.extend([f"Warning treated as error: {w}" for w in result.warnings])
            
            if not result.valid:
                self.validation_failures += 1
                logger.warning(f"Event validation failed: {event.event_id}")
                for error in result.errors:
                    logger.warning(f"  - {error}")
            
            return result
            
        except Exception as e:
            logger.error(f"Validation error for event {event.event_id}: {e}")
            result.valid = False
            result.add_error(f"Validation system error: {str(e)}")
            self.validation_failures += 1
            return result
    
    def register_rule(self, rule: ValidationRule) -> bool:
        """Register a custom validation rule
        
        Args:
            rule: Validation rule to register
            
        Returns:
            True if registration successful
        """
        if rule.rule_id in self.custom_rules:
            logger.warning(f"Rule already exists: {rule.rule_id}")
            return False
        
        self.custom_rules[rule.rule_id] = rule
        self.rule_execution_count[rule.rule_id] = 0
        
        logger.info(f"Validation rule registered: {rule.rule_id}")
        return True
    
    def unregister_rule(self, rule_id: str) -> bool:
        """Unregister a custom validation rule
        
        Args:
            rule_id: Rule ID to remove
            
        Returns:
            True if removal successful
        """
        if rule_id not in self.custom_rules:
            logger.warning(f"Rule not found: {rule_id}")
            return False
        
        del self.custom_rules[rule_id]
        self.rule_execution_count.pop(rule_id, None)
        
        logger.info(f"Validation rule unregistered: {rule_id}")
        return True
    
    def _validate_basic_structure(self, event: BaseEvent) -> ValidationResult:
        """Validate basic event structure"""
        result = ValidationResult(valid=True)
        
        # Check required fields
        if not event.event_type:
            result.add_error("Event type is required")
        
        if not event.event_id:
            result.add_error("Event ID is required")
        
        if not event.timestamp:
            result.add_error("Event timestamp is required")
        
        # Validate event type format
        if event.event_type and not re.match(r'^[a-z][a-z0-9_.]*[a-z0-9]$', event.event_type):
            result.add_error("Event type must follow naming convention: lowercase, dots, underscores")
        
        # Validate timestamp
        if event.timestamp and event.timestamp > datetime.utcnow() + timedelta(minutes=5):
            result.add_warning("Event timestamp is in the future")
        
        if event.timestamp and event.timestamp < datetime.utcnow() - timedelta(days=30):
            result.add_warning("Event timestamp is very old")
        
        # Validate data types
        if event.data is not None and not isinstance(event.data, dict):
            result.add_error("Event data must be a dictionary")
        
        if event.metadata is not None and not isinstance(event.metadata, dict):
            result.add_error("Event metadata must be a dictionary")
        
        return result
    
    def _validate_schema(self, event: BaseEvent) -> ValidationResult:
        """Validate event against registered schema"""
        result = ValidationResult(valid=True)
        
        # Get event schema from registry
        registry = get_global_registry()
        schema = registry.get_event_schema(event.event_type)
        
        if not schema:
            result.add_warning(f"No schema found for event type: {event.event_type}")
            return result
        
        # Validate against schema
        try:
            if event.data:
                jsonschema.validate(event.data, schema.schema)
            
            # Check required fields
            if event.data:
                for field in schema.required_fields:
                    if field not in event.data:
                        result.add_error(f"Required field missing: {field}")
            
            # Check deprecated schema
            if schema.deprecated:
                result.add_warning(f"Event type is deprecated: {event.event_type}")
                if schema.replacement_event:
                    result.add_info(f"Use {schema.replacement_event} instead")
            
        except jsonschema.ValidationError as e:
            result.add_error(f"Schema validation failed: {e.message}")
        except Exception as e:
            result.add_error(f"Schema validation error: {str(e)}")
        
        return result
    
    def _validate_business_rules(self, event: BaseEvent) -> ValidationResult:
        """Validate business rules"""
        result = ValidationResult(valid=True)
        
        # User-related validations
        if event.event_type.startswith("user."):
            user_result = self._validate_user_events(event)
            result.merge(user_result)
        
        # Content-related validations
        elif event.event_type.startswith("content."):
            content_result = self._validate_content_events(event)
            result.merge(content_result)
        
        # Revenue-related validations
        elif event.event_type.startswith("revenue."):
            revenue_result = self._validate_revenue_events(event)
            result.merge(revenue_result)
        
        # AI-related validations
        elif event.event_type.startswith("ai."):
            ai_result = self._validate_ai_events(event)
            result.merge(ai_result)
        
        # Security-related validations
        elif event.event_type.startswith("security."):
            security_result = self._validate_security_events(event)
            result.merge(security_result)
        
        return result
    
    def _validate_user_events(self, event: BaseEvent) -> ValidationResult:
        """Validate user-related events"""
        result = ValidationResult(valid=True)
        
        if not event.data:
            return result
        
        # User ID validation
        if "user_id" in event.data:
            user_id = event.data["user_id"]
            if not isinstance(user_id, str) or not user_id.strip():
                result.add_error("User ID must be a non-empty string")
            elif len(user_id) < 3:
                result.add_error("User ID must be at least 3 characters")
        
        # Email validation
        if "email" in event.data:
            email = event.data["email"]
            if not isinstance(email, str):
                result.add_error("Email must be a string")
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                result.add_error("Invalid email format")
        
        # Username validation
        if "username" in event.data:
            username = event.data["username"]
            if not isinstance(username, str):
                result.add_error("Username must be a string")
            elif not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):
                result.add_error("Username must be 3-30 alphanumeric characters or underscores")
        
        return result
    
    def _validate_content_events(self, event: BaseEvent) -> ValidationResult:
        """Validate content-related events"""
        result = ValidationResult(valid=True)
        
        if not event.data:
            return result
        
        # Content ID validation
        if "content_id" in event.data:
            content_id = event.data["content_id"]
            if not isinstance(content_id, str) or not content_id.strip():
                result.add_error("Content ID must be a non-empty string")
        
        # File size validation
        if "file_size" in event.data:
            file_size = event.data["file_size"]
            if not isinstance(file_size, int) or file_size < 0:
                result.add_error("File size must be a non-negative integer")
            elif file_size > 5 * 1024 * 1024 * 1024:  # 5GB
                result.add_warning("File size is very large (>5GB)")
        
        # Duration validation
        if "duration" in event.data:
            duration = event.data["duration"]
            if duration is not None:
                if not isinstance(duration, (int, float)) or duration < 0:
                    result.add_error("Duration must be a non-negative number")
                elif duration > 86400:  # 24 hours
                    result.add_warning("Content duration is very long (>24 hours)")
        
        return result
    
    def _validate_revenue_events(self, event: BaseEvent) -> ValidationResult:
        """Validate revenue-related events"""
        result = ValidationResult(valid=True)
        
        if not event.data:
            return result
        
        # Amount validation
        amount_fields = ["amount", "revenue_amount"]
        for field in amount_fields:
            if field in event.data:
                amount_str = event.data[field]
                try:
                    amount = Decimal(amount_str)
                    if amount < 0:
                        result.add_error(f"{field} cannot be negative")
                    elif amount > Decimal('1000000'):
                        result.add_warning(f"{field} is very large (>$1M)")
                except (ValueError, TypeError):
                    result.add_error(f"{field} must be a valid decimal number")
        
        # Currency validation
        if "currency" in event.data:
            currency = event.data["currency"]
            if not isinstance(currency, str) or len(currency) != 3:
                result.add_error("Currency must be a 3-character ISO code")
            elif not currency.isupper():
                result.add_error("Currency code must be uppercase")
        
        return result
    
    def _validate_ai_events(self, event: BaseEvent) -> ValidationResult:
        """Validate AI-related events"""
        result = ValidationResult(valid=True)
        
        if not event.data:
            return result
        
        # Confidence score validation
        if "confidence_score" in event.data:
            confidence = event.data["confidence_score"]
            if not isinstance(confidence, (int, float)):
                result.add_error("Confidence score must be a number")
            elif not 0 <= confidence <= 1:
                result.add_error("Confidence score must be between 0 and 1")
        
        # AI model validation
        if "ai_model" in event.data:
            ai_model = event.data["ai_model"]
            if not isinstance(ai_model, str) or not ai_model.strip():
                result.add_error("AI model must be a non-empty string")
        
        # Processing time validation
        if "processing_time" in event.data:
            processing_time = event.data["processing_time"]
            if not isinstance(processing_time, (int, float)) or processing_time < 0:
                result.add_error("Processing time must be a non-negative number")
            elif processing_time > 3600:  # 1 hour
                result.add_warning("Processing time is very long (>1 hour)")
        
        return result
    
    def _validate_security_events(self, event: BaseEvent) -> ValidationResult:
        """Validate security-related events"""
        result = ValidationResult(valid=True)
        
        if not event.data:
            return result
        
        # Severity validation
        if "severity" in event.data:
            severity = event.data["severity"]
            valid_severities = ["low", "medium", "high", "critical"]
            if severity not in valid_severities:
                result.add_error(f"Severity must be one of: {valid_severities}")
        
        # IP address validation
        if "source_ip" in event.data:
            source_ip = event.data["source_ip"]
            if source_ip and not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', source_ip):
                result.add_error("Invalid IP address format")
        
        return result
    
    def _validate_custom_rules(self, event: BaseEvent) -> ValidationResult:
        """Validate custom rules"""
        result = ValidationResult(valid=True)
        
        for rule in self.custom_rules.values():
            if rule.applies_to_event(event):
                try:
                    rule_result = rule.validator_func(event)
                    result.merge(rule_result)
                    self.rule_execution_count[rule.rule_id] += 1
                except Exception as e:
                    logger.error(f"Custom rule {rule.rule_id} failed: {e}")
                    if rule.severity == ValidationSeverity.CRITICAL:
                        result.add_error(f"Critical rule {rule.rule_id} failed: {str(e)}")
                    else:
                        result.add_warning(f"Rule {rule.rule_id} failed: {str(e)}")
        
        return result
    
    def _register_builtin_rules(self) -> None:
        """Register built-in validation rules"""
        
        # Event ID uniqueness rule (placeholder)
        def validate_event_id_format(event: BaseEvent) -> ValidationResult:
            result = ValidationResult(valid=True)
            if event.event_id and not re.match(r'^[a-zA-Z0-9\-_]{8,}$', event.event_id):
                result.add_warning("Event ID should be at least 8 alphanumeric characters")
            return result
        
        self.register_rule(ValidationRule(
            rule_id="event_id_format",
            name="Event ID Format",
            description="Validate event ID format",
            validator_func=validate_event_id_format,
            severity=ValidationSeverity.WARNING
        ))
        
        # Rate limiting rule (placeholder)
        def validate_rate_limit(event: BaseEvent) -> ValidationResult:
            result = ValidationResult(valid=True)
            # Placeholder for rate limiting logic
            return result
        
        self.register_rule(ValidationRule(
            rule_id="rate_limit",
            name="Rate Limiting",
            description="Check event rate limits",
            validator_func=validate_rate_limit,
            severity=ValidationSeverity.ERROR
        ))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        success_rate = (self.validation_count - self.validation_failures) / max(self.validation_count, 1)
        
        return {
            "validation_count": self.validation_count,
            "validation_failures": self.validation_failures,
            "success_rate": success_rate,
            "custom_rules_count": len(self.custom_rules),
            "rule_execution_counts": dict(self.rule_execution_count),
            "settings": {
                "schema_validation": self.enable_schema_validation,
                "business_rules": self.enable_business_rules,
                "strict_mode": self.strict_mode
            }
        }


# Global validator instance
_global_validator: Optional[EventValidator] = None


def get_global_validator() -> EventValidator:
    """Get or create global event validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = EventValidator()
    return _global_validator


def validate_event(event: BaseEvent) -> ValidationResult:
    """Convenience function to validate event globally"""
    validator = get_global_validator()
    return validator.validate(event)


def register_validation_rule(rule: ValidationRule) -> bool:
    """Convenience function to register validation rule globally"""
    validator = get_global_validator()
    return validator.register_rule(rule)