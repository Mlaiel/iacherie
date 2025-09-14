"""
import asyncio
from datetime import datetime

🔍 Advanced Validation Engine with Custom Rules
Enterprise-grade validation system for Ainflue Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Callable, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import re
import datetime
from abc import ABC, abstractmethod


class ValidationSeverity(str, Enum):
    """Validation severity levels"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


class ValidationRule(BaseModel):
    """Base validation rule structure"""
    name: str = Field(..., description="Rule name identifier")
    description: str = Field(..., description="Human-readable rule description")
    severity: ValidationSeverity = Field(default=ValidationSeverity.ERROR)
    enabled: bool = Field(default=True)
    rule_type: str = Field(..., description="Type of validation rule")


class ValidationResult(BaseModel):
    """Validation result container"""
    field_name: str = Field(..., description="Field being validated")
    rule_name: str = Field(..., description="Rule that was applied")
    is_valid: bool = Field(..., description="Whether validation passed")
    severity: ValidationSeverity = Field(..., description="Validation severity")
    message: str = Field(..., description="Validation message")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for the issue")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class ValidationContext(BaseModel):
    """Validation execution context"""
    entity_type: str = Field(..., description="Type of entity being validated")
    entity_id: Optional[str] = Field(None, description="Entity identifier")
    validation_timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationRuleEngine(ABC):
    """Abstract base for validation rule engines"""
    
    @abstractmethod
    async def validate(self, value: Any, context: ValidationContext) -> List[ValidationResult]:
        """Execute validation rules on value"""
        pass


class ContentValidationRules(ValidationRuleEngine):
    """Content-specific validation rules"""
    
    def __init__(self) -> None:
        self.rules = {
            "content_length": self._validate_content_length,
            "content_format": self._validate_content_format,
            "content_safety": self._validate_content_safety,
            "metadata_completeness": self._validate_metadata_completeness,
        }
    
    async def validate(self, value: Any, context: ValidationContext) -> List[ValidationResult]:
        """Validate content according to business rules"""
        results = []
        
        for rule_name, rule_func in self.rules.items():
            try:
                result = await rule_func(value, context)
                if result:
                    results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    field_name="content",
                    rule_name=rule_name,
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation rule error: {str(e)}",
                    context={"exception": str(e)}
                ))
        
        return results
    
    async def _validate_content_length(self, content: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate content length constraints"""
        content_type = content.get("type", "")
        content_size = content.get("size", 0)
        
        max_sizes = {
            "text": 50000,  # 50KB
            "image": 10 * 1024 * 1024,  # 10MB
            "audio": 100 * 1024 * 1024,  # 100MB
            "video": 500 * 1024 * 1024,  # 500MB
        }
        
        max_size = max_sizes.get(content_type, 1024 * 1024)  # Default 1MB
        
        if content_size > max_size:
            return ValidationResult(
                field_name="content.size",
                rule_name="content_length",
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Content size {content_size} exceeds maximum {max_size} for type {content_type}",
                suggested_fix=f"Reduce content size to under {max_size} bytes"
            )
        return None
    
    async def _validate_content_format(self, content: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate content format compliance"""
        content_type = content.get("type", "")
        file_extension = content.get("filename", "").lower().split(".")[-1]
        
        allowed_formats = {
            "text": ["txt", "md", "html", "pdf"],
            "image": ["jpg", "jpeg", "png", "gif", "svg", "webp"],
            "audio": ["mp3", "wav", "flac", "aac", "ogg"],
            "video": ["mp4", "avi", "mov", "wmv", "webm"],
        }
        
        if content_type in allowed_formats:
            if file_extension not in allowed_formats[content_type]:
                return ValidationResult(
                    field_name="content.format",
                    rule_name="content_format",
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"File extension '{file_extension}' not allowed for content type '{content_type}'",
                    suggested_fix=f"Use one of: {', '.join(allowed_formats[content_type])}"
                )
        return None
    
    async def _validate_content_safety(self, content: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate content safety and compliance"""
        # Implement AI-based content safety validation
        safety_score = content.get("safety_score", 1.0)
        
        if safety_score < 0.8:
            return ValidationResult(
                field_name="content.safety",
                rule_name="content_safety",
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Content safety score {safety_score} below required threshold 0.8",
                suggested_fix="Review and modify content to meet safety guidelines"
            )
        return None
    
    async def _validate_metadata_completeness(self, content: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate metadata completeness"""
        required_fields = ["title", "description", "tags", "category"]
        metadata = content.get("metadata", {})
        
        missing_fields = [field for field in required_fields if not metadata.get(field)]
        
        if missing_fields:
            return ValidationResult(
                field_name="content.metadata",
                rule_name="metadata_completeness",
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message=f"Missing required metadata fields: {', '.join(missing_fields)}",
                suggested_fix=f"Add the following fields: {', '.join(missing_fields)}"
            )
        return None


class UserValidationRules(ValidationRuleEngine):
    """User-specific validation rules"""
    
    def __init__(self) -> None:
        self.rules = {
            "email_format": self._validate_email_format,
            "password_strength": self._validate_password_strength,
            "profile_completeness": self._validate_profile_completeness,
            "creator_verification": self._validate_creator_verification,
        }
    
    async def validate(self, value: Any, context: ValidationContext) -> List[ValidationResult]:
        """Validate user data according to business rules"""
        results = []
        
        for rule_name, rule_func in self.rules.items():
            try:
                result = await rule_func(value, context)
                if result:
                    results.append(result)
            except Exception as e:
                results.append(ValidationResult(
                    field_name="user",
                    rule_name=rule_name,
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation rule error: {str(e)}",
                    context={"exception": str(e)}
                ))
        
        return results
    
    async def _validate_email_format(self, user: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate email format"""
        email = user.get("email", "")
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return ValidationResult(
                field_name="user.email",
                rule_name="email_format",
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Invalid email format: {email}",
                suggested_fix="Provide a valid email address (e.g., user@domain.com)"
            )
        return None
    
    async def _validate_password_strength(self, user: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate password strength"""
        password = user.get("password", "")
        
        if len(password) < 8:
            return ValidationResult(
                field_name="user.password",
                rule_name="password_strength",
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message="Password must be at least 8 characters long",
                suggested_fix="Use a password with at least 8 characters"
            )
        
        # Check for complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            return ValidationResult(
                field_name="user.password",
                rule_name="password_strength",
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message="Password should contain uppercase, lowercase, digit, and special character",
                suggested_fix="Use a password with mixed case, numbers, and special characters"
            )
        return None
    
    async def _validate_profile_completeness(self, user: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate profile completeness"""
        required_fields = ["username", "email", "first_name", "last_name"]
        profile = user.get("profile", {})
        
        missing_fields = [field for field in required_fields if not user.get(field) and not profile.get(field)]
        
        if missing_fields:
            return ValidationResult(
                field_name="user.profile",
                rule_name="profile_completeness",
                is_valid=False,
                severity=ValidationSeverity.INFO,
                message=f"Profile incomplete. Missing: {', '.join(missing_fields)}",
                suggested_fix=f"Complete profile by adding: {', '.join(missing_fields)}"
            )
        return None
    
    async def _validate_creator_verification(self, user: Dict[str, Any], context: ValidationContext) -> Optional[ValidationResult]:
        """Validate creator verification status"""
        is_creator = user.get("is_creator", False)
        verification_status = user.get("verification_status", "pending")
        
        if is_creator and verification_status not in ["verified", "pending"]:
            return ValidationResult(
                field_name="user.verification_status",
                rule_name="creator_verification",
                is_valid=False,
                severity=ValidationSeverity.WARNING,
                message=f"Creator verification status '{verification_status}' is invalid",
                suggested_fix="Complete creator verification process"
            )
        return None


class AdvancedValidationEngine:
    """Advanced validation engine with custom rules and context awareness"""
    
    def __init__(self) -> None:
        self.rule_engines: Dict[str, ValidationRuleEngine] = {
            "content": ContentValidationRules(),
            "user": UserValidationRules(),
        }
        self.global_rules: List[ValidationRule] = []
        self.validation_history: List[Dict[str, Any]] = []
    
    async def validate_entity(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        context: Optional[ValidationContext] = None
    ) -> List[ValidationResult]:
        """Validate an entity using appropriate rule engine"""
        
        if context is None:
            context = ValidationContext(entity_type=entity_type)
        
        results = []
        
        # Get appropriate rule engine
        rule_engine = self.rule_engines.get(entity_type)
        if rule_engine:
            engine_results = await rule_engine.validate(entity_data, context)
            results.extend(engine_results)
        
        # Apply global rules
        global_results = await self._apply_global_rules(entity_data, context)
        results.extend(global_results)
        
        # Store validation history
        self._store_validation_history(entity_type, entity_data, results, context)
        
        return results
    
    async def _apply_global_rules(
        self,
        entity_data: Dict[str, Any],
        context: ValidationContext
    ) -> List[ValidationResult]:
        """Apply global validation rules"""
        results = []
        
        # Example global rule: Check for profanity
        text_fields = self._extract_text_fields(entity_data)
        for field_name, text_value in text_fields.items():
            if await self._contains_profanity(text_value):
                results.append(ValidationResult(
                    field_name=field_name,
                    rule_name="global_profanity_check",
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Inappropriate content detected in {field_name}",
                    suggested_fix="Remove inappropriate language and content"
                ))
        
        return results
    
    def _extract_text_fields(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """Extract all text fields from nested data structure"""
        text_fields = {}
        
        for key, value in data.items():
            field_name = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, str):
                text_fields[field_name] = value
            elif isinstance(value, dict):
                nested_fields = self._extract_text_fields(value, field_name)
                text_fields.update(nested_fields)
        
        return text_fields
    
    async def _contains_profanity(self, text: str) -> bool:
        """Check if text contains profanity (placeholder implementation)"""
        # This would integrate with a real profanity detection service
        profanity_words = ["spam", "fake", "scam"]  # Simplified example
        text_lower = text.lower()
        return any(word in text_lower for word in profanity_words)
    
    def _store_validation_history(
        self,
        entity_type -> None: str,
        entity_data -> None: Dict[str, Any],
        results -> None: List[ValidationResult],
        context -> None: ValidationContext
    ) -> None:
        """Store validation history for analytics and improvement"""
        history_entry = {
            "timestamp": datetime.datetime.utcnow(),
            "entity_type": entity_type,
            "entity_id": context.entity_id,
            "total_rules_applied": len(results),
            "failed_validations": len([r for r in results if not r.is_valid]),
            "severity_distribution": {
                "critical": len([r for r in results if r.severity == ValidationSeverity.CRITICAL]),
                "error": len([r for r in results if r.severity == ValidationSeverity.ERROR]),
                "warning": len([r for r in results if r.severity == ValidationSeverity.WARNING]),
                "info": len([r for r in results if r.severity == ValidationSeverity.INFO]),
            }
        }
        
        self.validation_history.append(history_entry)
    
    def add_custom_rule_engine(self, entity_type -> None: str, rule_engine -> None: ValidationRuleEngine) -> None:
        """Add custom rule engine for specific entity type"""
        self.rule_engines[entity_type] = rule_engine
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics and insights"""
        if not self.validation_history:
            return {"message": "No validation history available"}
        
        total_validations = len(self.validation_history)
        total_failures = sum(entry["failed_validations"] for entry in self.validation_history)
        
        return {
            "total_validations": total_validations,
            "total_failures": total_failures,
            "failure_rate": total_failures / max(sum(entry["total_rules_applied"] for entry in self.validation_history), 1),
            "entity_type_distribution": self._get_entity_type_distribution(),
            "severity_trends": self._get_severity_trends(),
        }
    
    def _get_entity_type_distribution(self) -> Dict[str, int]:
        """Get distribution of validations by entity type"""
        distribution = {}
        for entry in self.validation_history:
            entity_type = entry["entity_type"]
            distribution[entity_type] = distribution.get(entity_type, 0) + 1
        return distribution
    
    def _get_severity_trends(self) -> Dict[str, List[int]]:
        """Get trends of validation severities over time"""
        trends = {
            "critical": [],
            "error": [],
            "warning": [],
            "info": []
        }
        
        for entry in self.validation_history:
            severity_dist = entry["severity_distribution"]
            for severity, count in severity_dist.items():
                trends[severity].append(count)
        
        return trends


# Export classes for external use
__all__ = [
    'ValidationSeverity',
    'ValidationRule', 
    'ValidationResult',
    'ValidationContext',
    'ValidationRuleEngine',
    'ContentValidationRules',
    'UserValidationRules',
    'AdvancedValidationEngine'
]