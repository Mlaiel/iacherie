"""Business Validation - IA Influencer Agent Platform
==================================================

Consolidated business logic validation for content, users, monetization,
and collaboration processes across the platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationType(Enum):
    """Types of business validation."""
    CONTENT_VALIDATION = "content_validation"
    USER_VALIDATION = "user_validation"
    MONETIZATION_VALIDATION = "monetization_validation"
    COLLABORATION_VALIDATION = "collaboration_validation"
    COMPLIANCE_VALIDATION = "compliance_validation"
    DATA_VALIDATION = "data_validation"


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationRule:
    """Validation rule definition."""
    rule_id: str
    name: str
    validation_type: ValidationType
    severity: ValidationSeverity
    validator_func: str
    error_message: str
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationError:
    """Validation error details."""
    rule_id: str
    field: str
    message: str
    severity: ValidationSeverity
    value: Any = None
    expected: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation process."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    validation_time: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BusinessValidator:
    """
    Consolidated business validation engine for the IA Influencer platform.
    
    Provides comprehensive validation for content, users, monetization,
    collaboration, and compliance across all business processes.
    """
    
    def __init__(self) -> None:
        """Initialize the business validator."""
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.validators: Dict[str, callable] = {}
        self.logger = logging.getLogger(__name__)
        self._register_default_validators()
        self._load_default_rules()
    
    def _register_default_validators(self) -> None:
        """Register default validation functions."""
        self.validators.update({
            "validate_email": self._validate_email,
            "validate_content_type": self._validate_content_type,
            "validate_file_size": self._validate_file_size,
            "validate_audio_format": self._validate_audio_format,
            "validate_video_format": self._validate_video_format,
            "validate_image_format": self._validate_image_format,
            "validate_creator_type": self._validate_creator_type,
            "validate_audience_size": self._validate_audience_size,
            "validate_revenue_amount": self._validate_revenue_amount,
            "validate_collaboration_terms": self._validate_collaboration_terms,
            "validate_compliance_requirements": self._validate_compliance_requirements,
            "validate_pricing_data": self._validate_pricing_data,
            "validate_payment_method": self._validate_payment_method,
            "validate_content_metadata": self._validate_content_metadata
        })
    
    def _load_default_rules(self) -> None:
        """Load default validation rules."""
        default_rules = [
            # Content validation rules
            ValidationRule(
                rule_id="email_format",
                name="Email Format Validation",
                validation_type=ValidationType.USER_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_email",
                error_message="Invalid email format"
            ),
            ValidationRule(
                rule_id="content_type_check",
                name="Content Type Validation",
                validation_type=ValidationType.CONTENT_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_content_type",
                error_message="Invalid content type"
            ),
            ValidationRule(
                rule_id="file_size_limit",
                name="File Size Validation",
                validation_type=ValidationType.CONTENT_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_file_size",
                error_message="File size exceeds allowed limit"
            ),
            ValidationRule(
                rule_id="audio_format_check",
                name="Audio Format Validation",
                validation_type=ValidationType.CONTENT_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_audio_format",
                error_message="Invalid audio format"
            ),
            ValidationRule(
                rule_id="creator_type_validation",
                name="Creator Type Validation",
                validation_type=ValidationType.USER_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_creator_type",
                error_message="Invalid creator type"
            ),
            ValidationRule(
                rule_id="audience_size_check",
                name="Audience Size Validation",
                validation_type=ValidationType.MONETIZATION_VALIDATION,
                severity=ValidationSeverity.WARNING,
                validator_func="validate_audience_size",
                error_message="Insufficient audience size for monetization"
            ),
            ValidationRule(
                rule_id="revenue_amount_validation",
                name="Revenue Amount Validation",
                validation_type=ValidationType.MONETIZATION_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_revenue_amount",
                error_message="Invalid revenue amount"
            ),
            ValidationRule(
                rule_id="collaboration_terms_check",
                name="Collaboration Terms Validation",
                validation_type=ValidationType.COLLABORATION_VALIDATION,
                severity=ValidationSeverity.ERROR,
                validator_func="validate_collaboration_terms",
                error_message="Invalid collaboration terms"
            ),
            ValidationRule(
                rule_id="compliance_requirements",
                name="Compliance Requirements Validation",
                validation_type=ValidationType.COMPLIANCE_VALIDATION,
                severity=ValidationSeverity.CRITICAL,
                validator_func="validate_compliance_requirements",
                error_message="Compliance requirements not met"
            )
        ]
        
        for rule in default_rules:
            self.add_validation_rule(rule)
    
    def add_validation_rule(self, rule: ValidationRule) -> str:
        """Add a validation rule."""
        try:
            self.validation_rules[rule.rule_id] = rule
            self.logger.info(f"Added validation rule: {rule.name} ({rule.rule_id})")
            return rule.rule_id
        except Exception as e:
            self.logger.error(f"Failed to add validation rule {rule.rule_id}: {str(e)}")
            raise
    
    def register_validator(self, name: str, validator_func: callable) -> None:
        """Register a custom validator function."""
        try:
            self.validators[name] = validator_func
            self.logger.info(f"Registered validator: {name}")
        except Exception as e:
            self.logger.error(f"Failed to register validator {name}: {str(e)}")
            raise
    
    async def validate_content(self, content_data: Dict[str, Any]) -> ValidationResult:
        """Validate content data."""
        try:
            errors = []
            warnings = []
            
            # Apply content validation rules
            for rule in self.validation_rules.values():
                if rule.validation_type == ValidationType.CONTENT_VALIDATION and rule.is_active:
                    validation_error = await self._apply_validation_rule(rule, content_data)
                    if validation_error:
                        if validation_error.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
                            errors.append(validation_error)
                        else:
                            warnings.append(validation_error)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata={"validation_type": "content", "rules_applied": len(self.validation_rules)}
            )
            
        except Exception as e:
            self.logger.error(f"Error validating content: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    rule_id="system_error",
                    field="system",
                    message=f"Validation system error: {str(e)}",
                    severity=ValidationSeverity.CRITICAL
                )]
            )
    
    async def validate_user(self, user_data: Dict[str, Any]) -> ValidationResult:
        """Validate user data."""
        try:
            errors = []
            warnings = []
            
            # Apply user validation rules
            for rule in self.validation_rules.values():
                if rule.validation_type == ValidationType.USER_VALIDATION and rule.is_active:
                    validation_error = await self._apply_validation_rule(rule, user_data)
                    if validation_error:
                        if validation_error.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
                            errors.append(validation_error)
                        else:
                            warnings.append(validation_error)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata={"validation_type": "user", "rules_applied": len(self.validation_rules)}
            )
            
        except Exception as e:
            self.logger.error(f"Error validating user: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    rule_id="system_error",
                    field="system",
                    message=f"Validation system error: {str(e)}",
                    severity=ValidationSeverity.CRITICAL
                )]
            )
    
    async def validate_monetization(self, monetization_data: Dict[str, Any]) -> ValidationResult:
        """Validate monetization data."""
        try:
            errors = []
            warnings = []
            
            # Apply monetization validation rules
            for rule in self.validation_rules.values():
                if rule.validation_type == ValidationType.MONETIZATION_VALIDATION and rule.is_active:
                    validation_error = await self._apply_validation_rule(rule, monetization_data)
                    if validation_error:
                        if validation_error.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
                            errors.append(validation_error)
                        else:
                            warnings.append(validation_error)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata={"validation_type": "monetization", "rules_applied": len(self.validation_rules)}
            )
            
        except Exception as e:
            self.logger.error(f"Error validating monetization: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    rule_id="system_error",
                    field="system",
                    message=f"Validation system error: {str(e)}",
                    severity=ValidationSeverity.CRITICAL
                )]
            )
    
    async def validate_collaboration(self, collaboration_data: Dict[str, Any]) -> ValidationResult:
        """Validate collaboration data."""
        try:
            errors = []
            warnings = []
            
            # Apply collaboration validation rules
            for rule in self.validation_rules.values():
                if rule.validation_type == ValidationType.COLLABORATION_VALIDATION and rule.is_active:
                    validation_error = await self._apply_validation_rule(rule, collaboration_data)
                    if validation_error:
                        if validation_error.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
                            errors.append(validation_error)
                        else:
                            warnings.append(validation_error)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata={"validation_type": "collaboration", "rules_applied": len(self.validation_rules)}
            )
            
        except Exception as e:
            self.logger.error(f"Error validating collaboration: {str(e)}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    rule_id="system_error",
                    field="system",
                    message=f"Validation system error: {str(e)}",
                    severity=ValidationSeverity.CRITICAL
                )]
            )
    
    async def _apply_validation_rule(self, rule: ValidationRule, data: Dict[str, Any]) -> Optional[ValidationError]:
        """Apply a validation rule to data."""
        try:
            if rule.validator_func not in self.validators:
                return ValidationError(
                    rule_id=rule.rule_id,
                    field="validator",
                    message=f"Validator {rule.validator_func} not found",
                    severity=ValidationSeverity.ERROR
                )
            
            validator = self.validators[rule.validator_func]
            is_valid, error_details = await validator(data)
            
            if not is_valid:
                return ValidationError(
                    rule_id=rule.rule_id,
                    field=error_details.get("field", "unknown"),
                    message=rule.error_message,
                    severity=rule.severity,
                    value=error_details.get("value"),
                    expected=error_details.get("expected"),
                    metadata=error_details.get("metadata", {})
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error applying validation rule {rule.rule_id}: {str(e)}")
            return ValidationError(
                rule_id=rule.rule_id,
                field="system",
                message=f"Rule application error: {str(e)}",
                severity=ValidationSeverity.ERROR
            )
    
    # Default validation functions
    async def _validate_email(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate email format."""
        email = data.get("email", "")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not email or not re.match(email_pattern, email):
            return False, {"field": "email", "value": email, "expected": "valid email format"}
        
        return True, {}
    
    async def _validate_content_type(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate content type."""
        content_type = data.get("content_type", "")
        valid_types = ["audio", "video", "image", "text"]
        
        if content_type not in valid_types:
            return False, {"field": "content_type", "value": content_type, "expected": valid_types}
        
        return True, {}
    
    async def _validate_file_size(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate file size."""
        file_size = data.get("file_size", 0)
        content_type = data.get("content_type", "")
        
        # Size limits in bytes
        size_limits = {
            "audio": 100 * 1024 * 1024,  # 100MB
            "video": 500 * 1024 * 1024,  # 500MB
            "image": 10 * 1024 * 1024,   # 10MB
            "text": 1 * 1024 * 1024      # 1MB
        }
        
        max_size = size_limits.get(content_type, 10 * 1024 * 1024)
        
        if file_size > max_size:
            return False, {
                "field": "file_size",
                "value": file_size,
                "expected": f"<= {max_size} bytes",
                "metadata": {"content_type": content_type}
            }
        
        return True, {}
    
    async def _validate_audio_format(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate audio format."""
        if data.get("content_type") != "audio":
            return True, {}
        
        audio_format = data.get("audio_format", "")
        valid_formats = ["mp3", "wav", "flac", "aac", "ogg"]
        
        if audio_format not in valid_formats:
            return False, {"field": "audio_format", "value": audio_format, "expected": valid_formats}
        
        return True, {}
    
    async def _validate_video_format(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate video format."""
        if data.get("content_type") != "video":
            return True, {}
        
        video_format = data.get("video_format", "")
        valid_formats = ["mp4", "avi", "mov", "mkv", "webm"]
        
        if video_format not in valid_formats:
            return False, {"field": "video_format", "value": video_format, "expected": valid_formats}
        
        return True, {}
    
    async def _validate_image_format(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate image format."""
        if data.get("content_type") != "image":
            return True, {}
        
        image_format = data.get("image_format", "")
        valid_formats = ["jpg", "jpeg", "png", "gif", "webp"]
        
        if image_format not in valid_formats:
            return False, {"field": "image_format", "value": image_format, "expected": valid_formats}
        
        return True, {}
    
    async def _validate_creator_type(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate creator type."""
        creator_type = data.get("creator_type", "")
        valid_types = ["musician", "podcaster", "video_creator", "artist", "influencer"]
        
        if creator_type not in valid_types:
            return False, {"field": "creator_type", "value": creator_type, "expected": valid_types}
        
        return True, {}
    
    async def _validate_audience_size(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate audience size."""
        audience_size = data.get("audience_size", 0)
        
        if not isinstance(audience_size, int) or audience_size < 0:
            return False, {"field": "audience_size", "value": audience_size, "expected": "non-negative integer"}
        
        # Warning for small audience (not an error)
        if audience_size < 1000:
            return False, {
                "field": "audience_size",
                "value": audience_size,
                "expected": ">= 1000 for optimal monetization",
                "metadata": {"severity": "warning"}
            }
        
        return True, {}
    
    async def _validate_revenue_amount(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate revenue amount."""
        try:
            amount = data.get("amount", 0)
            
            if isinstance(amount, str):
                amount = Decimal(amount)
            elif isinstance(amount, (int, float)):
                amount = Decimal(str(amount))
            
            if amount < 0:
                return False, {"field": "amount", "value": str(amount), "expected": ">= 0"}
            
            # Check for reasonable upper limit
            if amount > Decimal("1000000"):
                return False, {
                    "field": "amount",
                    "value": str(amount),
                    "expected": "<= 1,000,000",
                    "metadata": {"reason": "exceeds reasonable limit"}
                }
            
            return True, {}
            
        except (InvalidOperation, ValueError) as e:
            return False, {"field": "amount", "value": data.get("amount"), "expected": "valid decimal number"}
    
    async def _validate_collaboration_terms(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate collaboration terms."""
        terms = data.get("collaboration_terms", {})
        
        if not isinstance(terms, dict):
            return False, {"field": "collaboration_terms", "value": type(terms).__name__, "expected": "dictionary"}
        
        required_fields = ["revenue_share", "duration", "responsibilities"]
        
        for field in required_fields:
            if field not in terms:
                return False, {
                    "field": f"collaboration_terms.{field}",
                    "value": None,
                    "expected": f"required field: {field}"
                }
        
        # Validate revenue share
        revenue_share = terms.get("revenue_share", {})
        if isinstance(revenue_share, dict):
            total_share = sum(revenue_share.values())
            if abs(total_share - 100) > 0.01:  # Allow small floating point errors
                return False, {
                    "field": "collaboration_terms.revenue_share",
                    "value": total_share,
                    "expected": "total shares must equal 100%"
                }
        
        return True, {}
    
    async def _validate_compliance_requirements(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate compliance requirements."""
        # Check for required compliance fields
        required_compliance = ["terms_accepted", "privacy_policy_accepted", "age_verification"]
        
        for field in required_compliance:
            if not data.get(field, False):
                return False, {
                    "field": field,
                    "value": data.get(field),
                    "expected": "must be accepted/verified"
                }
        
        return True, {}
    
    async def _validate_pricing_data(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate pricing data."""
        pricing = data.get("pricing", {})
        
        if not isinstance(pricing, dict):
            return False, {"field": "pricing", "value": type(pricing).__name__, "expected": "dictionary"}
        
        # Validate price ranges
        for price_type, price_value in pricing.items():
            try:
                price = Decimal(str(price_value))
                if price < 0:
                    return False, {
                        "field": f"pricing.{price_type}",
                        "value": str(price),
                        "expected": ">= 0"
                    }
            except (InvalidOperation, ValueError):
                return False, {
                    "field": f"pricing.{price_type}",
                    "value": price_value,
                    "expected": "valid decimal number"
                }
        
        return True, {}
    
    async def _validate_payment_method(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate payment method."""
        payment_method = data.get("payment_method", {})
        
        if not isinstance(payment_method, dict):
            return False, {"field": "payment_method", "value": type(payment_method).__name__, "expected": "dictionary"}
        
        method_type = payment_method.get("type", "")
        valid_types = ["credit_card", "bank_transfer", "paypal", "crypto", "stripe"]
        
        if method_type not in valid_types:
            return False, {
                "field": "payment_method.type",
                "value": method_type,
                "expected": valid_types
            }
        
        return True, {}
    
    async def _validate_content_metadata(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate content metadata."""
        metadata = data.get("metadata", {})
        
        if not isinstance(metadata, dict):
            return False, {"field": "metadata", "value": type(metadata).__name__, "expected": "dictionary"}
        
        # Check for required metadata fields
        content_type = data.get("content_type", "")
        if content_type == "audio":
            required_fields = ["duration", "bitrate", "sample_rate"]
            for field in required_fields:
                if field not in metadata:
                    return False, {
                        "field": f"metadata.{field}",
                        "value": None,
                        "expected": f"required for audio content: {field}"
                    }
        
        return True, {}
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation rules and statistics."""
        try:
            return {
                "total_rules": len(self.validation_rules),
                "active_rules": len([r for r in self.validation_rules.values() if r.is_active]),
                "rules_by_type": {
                    vtype.value: len([r for r in self.validation_rules.values() if r.validation_type == vtype])
                    for vtype in ValidationType
                },
                "rules_by_severity": {
                    severity.value: len([r for r in self.validation_rules.values() if r.severity == severity])
                    for severity in ValidationSeverity
                },
                "registered_validators": len(self.validators)
            }
        except Exception as e:
            self.logger.error(f"Error getting validation summary: {str(e)}")
            return {}