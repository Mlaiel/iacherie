"""
Challenge Validator - Enterprise Challenge Validation and Compliance Engine

This module provides comprehensive validation and compliance checking for challenges,
ensuring quality standards, business rule compliance, and platform safety across
all challenge types and participant interactions.

Features:
- Multi-layer validation with configurable rule engines
- Real-time compliance monitoring and enforcement
- Advanced content safety and quality assessment
- Business rule validation and constraint checking
- Integration with AI-powered content analysis
- Professional audit trails and compliance reporting
- Automated challenge approval workflows
- Risk assessment and mitigation recommendations

Business Logic Integration:
- Challenge creation → Validation engine → Compliance approval → Activation
- Participant submission → Content validation → Quality assessment → Scoring
- Business rule compliance → Risk evaluation → Automated enforcement

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, distribution, or theft of this code or concept
without explicit written permission from Fahed Mlaiel is strictly prohibited
and will result in immediate legal action.

Contact: mlaiel@live.de for authorized usage inquiries.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class ValidationCategory(Enum):
    """Validation category classification"""
    CONTENT_SAFETY = "content_safety"
    BUSINESS_RULES = "business_rules"
    TECHNICAL_COMPLIANCE = "technical_compliance"
    QUALITY_STANDARDS = "quality_standards"
    LEGAL_COMPLIANCE = "legal_compliance"
    PLATFORM_POLICIES = "platform_policies"
    PARTICIPANT_ELIGIBILITY = "participant_eligibility"
    FINANCIAL_COMPLIANCE = "financial_compliance"


class ValidationStatus(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"
    PENDING_REVIEW = "pending_review"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


@dataclass
class ValidationRule:
    """Individual validation rule specification"""
    rule_id: str
    name: str
    description: str
    category: ValidationCategory
    severity: ValidationSeverity
    is_active: bool = True
    auto_fix_enabled: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationIssue:
    """Validation issue details"""
    rule_id: str
    rule_name: str
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    field_path: Optional[str] = None
    current_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    auto_fix_suggestion: Optional[str] = None
    manual_review_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationConfiguration:
    """Validation engine configuration"""
    config_id: str
    name: str
    description: str
    
    # Rules configuration
    rules: List[ValidationRule] = field(default_factory=list)
    rule_sets: Dict[str, List[str]] = field(default_factory=dict)  # Named rule collections
    
    # Processing configuration
    stop_on_critical: bool = True
    stop_on_blocking: bool = True
    parallel_validation: bool = True
    
    # AI integration
    ai_validation_enabled: bool = False
    ai_confidence_threshold: float = 0.8
    ai_model_version: str = "v1.0"
    
    # Compliance settings
    strict_mode: bool = False
    auto_fix_enabled: bool = False
    manual_review_threshold: int = 3  # Number of errors triggering manual review
    
    # Audit and reporting
    audit_trail_enabled: bool = True
    detailed_reporting: bool = True
    
    # Metadata
    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Comprehensive validation result"""
    validation_id: str
    target_type: str  # challenge, submission, participant, etc.
    target_id: str
    validation_timestamp: datetime
    
    # Overall result
    status: ValidationStatus
    overall_score: float  # 0-100 compliance score
    is_compliant: bool
    
    # Issues breakdown
    issues: List[ValidationIssue] = field(default_factory=list)
    critical_issues_count: int = 0
    blocking_issues_count: int = 0
    error_issues_count: int = 0
    warning_issues_count: int = 0
    
    # Category analysis
    category_results: Dict[ValidationCategory, Dict[str, Any]] = field(default_factory=dict)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    auto_fix_suggestions: List[str] = field(default_factory=list)
    manual_review_items: List[str] = field(default_factory=list)
    
    # Processing metadata
    validation_duration_ms: float = 0.0
    rules_processed: int = 0
    ai_validation_used: bool = False
    ai_confidence_score: Optional[float] = None
    
    # Audit trail
    validator_version: str = ""
    configuration_used: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidationRuleEngine(ABC):
    """Abstract base class for validation rule engines"""
    
    @abstractmethod
    async def validate(
        self,
        data: Any,
        rule: ValidationRule,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Execute validation rule and return issues"""
        pass
    
    @abstractmethod
    def get_supported_categories(self) -> List[ValidationCategory]:
        """Get list of supported validation categories"""
        pass


class ContentSafetyValidator(ValidationRuleEngine):
    """Content safety and moderation validation"""
    
    def __init__(self):
        self.prohibited_keywords = [
            "spam", "scam", "fraud", "hate", "violence", "illegal",
            "copyright violation", "plagiarism", "fake", "misleading"
        ]
        self.content_filters = {
            'profanity': True,
            'hate_speech': True,
            'violence': True,
            'adult_content': True,
            'copyright_violation': True
        }
    
    async def validate(
        self,
        data: Any,
        rule: ValidationRule,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Validate content safety"""
        issues = []
        
        try:
            if rule.rule_id == "content_profanity_check":
                issues.extend(await self._check_profanity(data, rule))
            elif rule.rule_id == "content_safety_scan":
                issues.extend(await self._scan_content_safety(data, rule))
            elif rule.rule_id == "copyright_compliance":
                issues.extend(await self._check_copyright_compliance(data, rule))
            elif rule.rule_id == "content_quality_standards":
                issues.extend(await self._check_quality_standards(data, rule))
            
        except Exception as e:
            logger.error(f"Error in content safety validation: {e}")
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=ValidationSeverity.ERROR,
                message=f"Content safety validation error: {str(e)}"
            ))
        
        return issues
    
    async def _check_profanity(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check for profanity in content"""
        issues = []
        
        # Extract text content for analysis
        text_content = self._extract_text_content(data)
        
        for text in text_content:
            # Simple profanity detection (in production, use advanced ML models)
            for keyword in self.prohibited_keywords:
                if keyword.lower() in text.lower():
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        message=f"Potentially inappropriate content detected: {keyword}",
                        current_value=text,
                        auto_fix_suggestion="Remove or replace inappropriate content",
                        manual_review_required=True
                    ))
        
        return issues
    
    async def _scan_content_safety(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Comprehensive content safety scanning"""
        issues = []
        
        # Simulate AI-powered content safety analysis
        content_data = data.get('content_data', {}) if isinstance(data, dict) else {}
        
        # Check for various safety concerns
        safety_score = await self._calculate_safety_score(content_data)
        
        if safety_score < rule.parameters.get('min_safety_score', 80.0):
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                message=f"Content safety score ({safety_score:.1f}) below threshold",
                current_value=safety_score,
                expected_value=rule.parameters.get('min_safety_score', 80.0),
                manual_review_required=safety_score < 60.0
            ))
        
        return issues
    
    async def _check_copyright_compliance(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check copyright compliance"""
        issues = []
        
        # Simulate copyright detection
        content_data = data.get('content_data', {}) if isinstance(data, dict) else {}
        media_files = content_data.get('media_files', [])
        
        for media_file in media_files:
            # Simulate copyright detection analysis
            copyright_risk = await self._assess_copyright_risk(media_file)
            
            if copyright_risk > rule.parameters.get('max_copyright_risk', 0.3):
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    message=f"Potential copyright violation detected in media file",
                    field_path=f"media_files.{media_file}",
                    manual_review_required=True
                ))
        
        return issues
    
    async def _check_quality_standards(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check content quality standards"""
        issues = []
        
        content_data = data.get('content_data', {}) if isinstance(data, dict) else {}
        
        # Check description quality
        description = content_data.get('description', '')
        if len(description) < rule.parameters.get('min_description_length', 50):
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=ValidationSeverity.WARNING,
                message="Description too short for quality standards",
                field_path="content_data.description",
                current_value=len(description),
                expected_value=rule.parameters.get('min_description_length', 50),
                auto_fix_suggestion="Provide more detailed description"
            ))
        
        # Check for required metadata
        required_fields = rule.parameters.get('required_metadata_fields', [])
        for field in required_fields:
            if field not in content_data:
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=ValidationSeverity.ERROR,
                    message=f"Required metadata field missing: {field}",
                    field_path=f"content_data.{field}",
                    auto_fix_suggestion=f"Add required field: {field}"
                ))
        
        return issues
    
    def _extract_text_content(self, data: Any) -> List[str]:
        """Extract text content for analysis"""
        text_content = []
        
        if isinstance(data, dict):
            # Extract from common text fields
            text_fields = ['title', 'description', 'tags', 'content', 'text']
            for field in text_fields:
                if field in data and isinstance(data[field], str):
                    text_content.append(data[field])
                elif field in data and isinstance(data[field], list):
                    text_content.extend([str(item) for item in data[field]])
            
            # Recursively extract from nested structures
            content_data = data.get('content_data', {})
            if isinstance(content_data, dict):
                for value in content_data.values():
                    if isinstance(value, str):
                        text_content.append(value)
        
        return text_content
    
    async def _calculate_safety_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate content safety score"""
        # Simulate AI-powered safety scoring
        base_score = 85.0
        
        # Deduct points for risk factors
        risk_factors = content_data.get('risk_factors', [])
        base_score -= len(risk_factors) * 10
        
        # Adjust for content type
        content_type = content_data.get('content_type', 'text')
        if content_type in ['video', 'audio']:
            base_score -= 5  # Higher risk for multimedia
        
        return max(0.0, min(100.0, base_score))
    
    async def _assess_copyright_risk(self, media_file: str) -> float:
        """Assess copyright violation risk"""
        # Simulate copyright risk assessment
        # In production, integrate with copyright detection services
        return 0.1  # Low risk by default
    
    def get_supported_categories(self) -> List[ValidationCategory]:
        """Get supported validation categories"""
        return [
            ValidationCategory.CONTENT_SAFETY,
            ValidationCategory.QUALITY_STANDARDS,
            ValidationCategory.LEGAL_COMPLIANCE
        ]


class BusinessRulesValidator(ValidationRuleEngine):
    """Business rules and constraints validation"""
    
    async def validate(
        self,
        data: Any,
        rule: ValidationRule,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Validate business rules"""
        issues = []
        
        try:
            if rule.rule_id == "challenge_duration_limits":
                issues.extend(await self._check_duration_limits(data, rule))
            elif rule.rule_id == "reward_value_limits":
                issues.extend(await self._check_reward_limits(data, rule))
            elif rule.rule_id == "participant_eligibility":
                issues.extend(await self._check_participant_eligibility(data, rule, context))
            elif rule.rule_id == "business_compliance":
                issues.extend(await self._check_business_compliance(data, rule))
            
        except Exception as e:
            logger.error(f"Error in business rules validation: {e}")
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=ValidationSeverity.ERROR,
                message=f"Business rules validation error: {str(e)}"
            ))
        
        return issues
    
    async def _check_duration_limits(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check challenge duration limits"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            try:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                duration_days = (end_date - start_date).days
                
                min_duration = rule.parameters.get('min_duration_days', 1)
                max_duration = rule.parameters.get('max_duration_days', 365)
                
                if duration_days < min_duration:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        message=f"Challenge duration ({duration_days} days) below minimum ({min_duration} days)",
                        field_path="duration",
                        current_value=duration_days,
                        expected_value=f"≥ {min_duration}",
                        auto_fix_suggestion=f"Extend challenge duration to at least {min_duration} days"
                    ))
                
                if duration_days > max_duration:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        message=f"Challenge duration ({duration_days} days) exceeds maximum ({max_duration} days)",
                        field_path="duration",
                        current_value=duration_days,
                        expected_value=f"≤ {max_duration}",
                        auto_fix_suggestion=f"Reduce challenge duration to maximum {max_duration} days"
                    ))
                    
            except Exception as e:
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=ValidationSeverity.ERROR,
                    message=f"Error parsing challenge dates: {str(e)}"
                ))
        
        return issues
    
    async def _check_reward_limits(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check reward value limits"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        rewards = data.get('rewards', [])
        if not isinstance(rewards, list):
            return issues
        
        max_monetary_reward = rule.parameters.get('max_monetary_reward', 10000.0)
        min_monetary_reward = rule.parameters.get('min_monetary_reward', 0.0)
        
        for i, reward in enumerate(rewards):
            if isinstance(reward, dict):
                monetary_prize = reward.get('monetary_prize', 0.0)
                
                if monetary_prize > max_monetary_reward:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        message=f"Reward value ({monetary_prize}) exceeds maximum ({max_monetary_reward})",
                        field_path=f"rewards[{i}].monetary_prize",
                        current_value=monetary_prize,
                        expected_value=f"≤ {max_monetary_reward}",
                        auto_fix_suggestion=f"Reduce reward to maximum {max_monetary_reward}"
                    ))
                
                if monetary_prize < min_monetary_reward and monetary_prize > 0:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=ValidationSeverity.WARNING,
                        message=f"Reward value ({monetary_prize}) below recommended minimum ({min_monetary_reward})",
                        field_path=f"rewards[{i}].monetary_prize",
                        current_value=monetary_prize,
                        expected_value=f"≥ {min_monetary_reward}",
                        auto_fix_suggestion=f"Consider increasing reward to at least {min_monetary_reward}"
                    ))
        
        return issues
    
    async def _check_participant_eligibility(
        self,
        data: Any,
        rule: ValidationRule,
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationIssue]:
        """Check participant eligibility requirements"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        eligibility_requirements = data.get('eligibility_requirements', {})
        
        # Check minimum age requirement
        min_age = eligibility_requirements.get('min_age')
        if min_age is not None:
            max_allowed_min_age = rule.parameters.get('max_min_age', 18)
            if min_age > max_allowed_min_age:
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    message=f"Minimum age requirement ({min_age}) too restrictive",
                    field_path="eligibility_requirements.min_age",
                    current_value=min_age,
                    expected_value=f"≤ {max_allowed_min_age}",
                    manual_review_required=True
                ))
        
        # Check geographic restrictions
        restricted_countries = eligibility_requirements.get('restricted_countries', [])
        if len(restricted_countries) > rule.parameters.get('max_restricted_countries', 10):
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=ValidationSeverity.WARNING,
                message=f"Too many geographic restrictions ({len(restricted_countries)} countries)",
                field_path="eligibility_requirements.restricted_countries",
                current_value=len(restricted_countries),
                expected_value=f"≤ {rule.parameters.get('max_restricted_countries', 10)}",
                auto_fix_suggestion="Review and reduce geographic restrictions"
            ))
        
        return issues
    
    async def _check_business_compliance(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check general business compliance"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        # Check required business fields
        required_fields = rule.parameters.get('required_business_fields', [])
        for field in required_fields:
            if field not in data or not data[field]:
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    message=f"Required business field missing: {field}",
                    field_path=field,
                    auto_fix_suggestion=f"Provide value for required field: {field}"
                ))
        
        # Check challenge type restrictions
        challenge_type = data.get('challenge_type')
        allowed_types = rule.parameters.get('allowed_challenge_types', [])
        if allowed_types and challenge_type not in allowed_types:
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                message=f"Challenge type '{challenge_type}' not allowed",
                field_path="challenge_type",
                current_value=challenge_type,
                expected_value=f"One of: {', '.join(allowed_types)}",
                auto_fix_suggestion=f"Change to allowed challenge type"
            ))
        
        return issues
    
    def get_supported_categories(self) -> List[ValidationCategory]:
        """Get supported validation categories"""
        return [
            ValidationCategory.BUSINESS_RULES,
            ValidationCategory.PARTICIPANT_ELIGIBILITY,
            ValidationCategory.FINANCIAL_COMPLIANCE
        ]


class TechnicalComplianceValidator(ValidationRuleEngine):
    """Technical compliance and platform requirements validation"""
    
    async def validate(
        self,
        data: Any,
        rule: ValidationRule,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationIssue]:
        """Validate technical compliance"""
        issues = []
        
        try:
            if rule.rule_id == "data_format_validation":
                issues.extend(await self._validate_data_format(data, rule))
            elif rule.rule_id == "api_limits_compliance":
                issues.extend(await self._check_api_limits(data, rule))
            elif rule.rule_id == "platform_integration":
                issues.extend(await self._check_platform_integration(data, rule))
            elif rule.rule_id == "security_requirements":
                issues.extend(await self._check_security_requirements(data, rule))
            
        except Exception as e:
            logger.error(f"Error in technical compliance validation: {e}")
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=ValidationSeverity.ERROR,
                message=f"Technical compliance validation error: {str(e)}"
            ))
        
        return issues
    
    async def _validate_data_format(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Validate data format and structure"""
        issues = []
        
        # Check required fields
        required_fields = rule.parameters.get('required_fields', [])
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        message=f"Required field missing: {field}",
                        field_path=field,
                        auto_fix_suggestion=f"Add required field: {field}"
                    ))
        
        # Check data types
        field_types = rule.parameters.get('field_types', {})
        if isinstance(data, dict):
            for field, expected_type in field_types.items():
                if field in data:
                    actual_type = type(data[field]).__name__
                    if actual_type != expected_type:
                        issues.append(ValidationIssue(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=ValidationSeverity.ERROR,
                            message=f"Invalid data type for field '{field}': expected {expected_type}, got {actual_type}",
                            field_path=field,
                            current_value=actual_type,
                            expected_value=expected_type,
                            auto_fix_suggestion=f"Convert field '{field}' to {expected_type}"
                        ))
        
        return issues
    
    async def _check_api_limits(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check API limits and constraints"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        # Check payload size limits
        max_payload_size = rule.parameters.get('max_payload_size_mb', 10)
        payload_size = len(json.dumps(data).encode('utf-8')) / (1024 * 1024)  # Size in MB
        
        if payload_size > max_payload_size:
            issues.append(ValidationIssue(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                message=f"Payload size ({payload_size:.2f}MB) exceeds limit ({max_payload_size}MB)",
                current_value=f"{payload_size:.2f}MB",
                expected_value=f"≤ {max_payload_size}MB",
                auto_fix_suggestion="Reduce payload size or use file uploads for large content"
            ))
        
        # Check array size limits
        max_array_size = rule.parameters.get('max_array_size', 1000)
        for key, value in data.items():
            if isinstance(value, list) and len(value) > max_array_size:
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=ValidationSeverity.WARNING,
                    message=f"Array '{key}' size ({len(value)}) exceeds recommended limit ({max_array_size})",
                    field_path=key,
                    current_value=len(value),
                    expected_value=f"≤ {max_array_size}",
                    auto_fix_suggestion=f"Consider pagination or reducing array size for '{key}'"
                ))
        
        return issues
    
    async def _check_platform_integration(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check platform integration requirements"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        # Check supported platforms
        target_platforms = data.get('target_platforms', [])
        supported_platforms = rule.parameters.get('supported_platforms', [])
        
        for platform in target_platforms:
            if platform not in supported_platforms:
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=ValidationSeverity.ERROR,
                    message=f"Unsupported platform: {platform}",
                    field_path="target_platforms",
                    current_value=platform,
                    expected_value=f"One of: {', '.join(supported_platforms)}",
                    auto_fix_suggestion=f"Use supported platform instead of '{platform}'"
                ))
        
        return issues
    
    async def _check_security_requirements(
        self,
        data: Any,
        rule: ValidationRule
    ) -> List[ValidationIssue]:
        """Check security requirements"""
        issues = []
        
        if not isinstance(data, dict):
            return issues
        
        # Check for sensitive data patterns
        sensitive_patterns = rule.parameters.get('sensitive_patterns', [])
        data_string = json.dumps(data, default=str)
        
        for pattern_name, pattern_regex in sensitive_patterns.items():
            if re.search(pattern_regex, data_string, re.IGNORECASE):
                issues.append(ValidationIssue(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Potential sensitive data detected: {pattern_name}",
                    auto_fix_suggestion=f"Remove or mask sensitive data: {pattern_name}",
                    manual_review_required=True
                ))
        
        return issues
    
    def get_supported_categories(self) -> List[ValidationCategory]:
        """Get supported validation categories"""
        return [
            ValidationCategory.TECHNICAL_COMPLIANCE,
            ValidationCategory.PLATFORM_POLICIES
        ]


class ChallengeValidator:
    """
    Enterprise-grade challenge validation and compliance engine
    
    Provides comprehensive validation across multiple dimensions including
    content safety, business rules, technical compliance, and quality standards.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize challenge validator with configuration"""
        self.config = config or {}
        
        # Core storage
        self._validation_configurations: Dict[str, ValidationConfiguration] = {}
        self._validation_history: Dict[str, List[ValidationResult]] = {}
        
        # Rule engines
        self._rule_engines: Dict[ValidationCategory, ValidationRuleEngine] = {
            ValidationCategory.CONTENT_SAFETY: ContentSafetyValidator(),
            ValidationCategory.BUSINESS_RULES: BusinessRulesValidator(),
            ValidationCategory.TECHNICAL_COMPLIANCE: TechnicalComplianceValidator(),
            ValidationCategory.QUALITY_STANDARDS: ContentSafetyValidator(),  # Reuse for quality
            ValidationCategory.LEGAL_COMPLIANCE: ContentSafetyValidator(),  # Reuse for legal
            ValidationCategory.PLATFORM_POLICIES: TechnicalComplianceValidator()  # Reuse for platform
        }
        
        # Performance tracking
        self._validation_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.default_config_id = self.config.get('default_config_id', 'default')
        self.max_validation_time_seconds = self.config.get('max_validation_time_seconds', 30)
        self.enable_caching = self.config.get('enable_caching', True)
        
        # Initialize default configuration
        self._initialize_default_configuration()
        
        logger.info("Challenge Validator initialized successfully")
    
    async def validate(
        self,
        data: Any,
        target_type: str = "challenge",
        target_id: Optional[str] = None,
        config_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Execute comprehensive validation"""
        try:
            start_time = datetime.now(timezone.utc)
            validation_id = self._generate_validation_id(data, target_type, target_id)
            
            if target_id is None:
                target_id = str(hash(str(data)))
            
            if context is None:
                context = {}
            
            # Get configuration
            config_id = config_id or self.default_config_id
            if config_id not in self._validation_configurations:
                raise ValueError(f"Validation configuration {config_id} not found")
            
            configuration = self._validation_configurations[config_id]
            
            # Initialize result
            result = ValidationResult(
                validation_id=validation_id,
                target_type=target_type,
                target_id=target_id,
                validation_timestamp=start_time,
                status=ValidationStatus.PASSED,
                overall_score=100.0,
                is_compliant=True,
                validator_version="1.0",
                configuration_used=config_id
            )
            
            # Execute validation rules
            all_issues = []
            rules_processed = 0
            
            # Process rules by category
            for category in ValidationCategory:
                if category in self._rule_engines:
                    category_rules = [r for r in configuration.rules if r.category == category and r.is_active]
                    
                    if category_rules:
                        category_issues = await self._validate_category(
                            data, category, category_rules, context
                        )
                        all_issues.extend(category_issues)
                        rules_processed += len(category_rules)
            
            # Process all issues
            for issue in all_issues:
                result.issues.append(issue)
                
                # Count by severity
                if issue.severity == ValidationSeverity.CRITICAL:
                    result.critical_issues_count += 1
                elif issue.severity == ValidationSeverity.BLOCKING:
                    result.blocking_issues_count += 1
                elif issue.severity == ValidationSeverity.ERROR:
                    result.error_issues_count += 1
                elif issue.severity == ValidationSeverity.WARNING:
                    result.warning_issues_count += 1
            
            # Calculate overall score and compliance
            result.overall_score = self._calculate_overall_score(result)
            result.is_compliant = self._determine_compliance(result, configuration)
            
            # Determine final status
            if result.critical_issues_count > 0 or result.blocking_issues_count > 0:
                result.status = ValidationStatus.FAILED
            elif result.error_issues_count > configuration.manual_review_threshold:
                result.status = ValidationStatus.REQUIRES_MANUAL_REVIEW
            elif result.error_issues_count > 0:
                result.status = ValidationStatus.CONDITIONAL
            else:
                result.status = ValidationStatus.PASSED
            
            # Generate recommendations
            result.recommendations = await self._generate_recommendations(result)
            result.auto_fix_suggestions = [
                issue.auto_fix_suggestion for issue in result.issues 
                if issue.auto_fix_suggestion
            ]
            result.manual_review_items = [
                issue.message for issue in result.issues 
                if issue.manual_review_required
            ]
            
            # Calculate processing metrics
            result.validation_duration_ms = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            result.rules_processed = rules_processed
            
            # Store result
            await self._store_validation_result(result)
            
            logger.info(f"Validation completed for {target_type} {target_id}: {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"Error in validation: {e}")
            raise
    
    async def create_validation_configuration(
        self,
        config: ValidationConfiguration
    ) -> bool:
        """Create new validation configuration"""
        try:
            if config.config_id in self._validation_configurations:
                logger.warning(f"Configuration {config.config_id} already exists")
                return False
            
            # Validate configuration
            if not config.rules:
                logger.error("Configuration must have at least one rule")
                return False
            
            # Store configuration
            self._validation_configurations[config.config_id] = config
            self._validation_metrics[config.config_id] = {
                'created_at': datetime.now(timezone.utc),
                'total_validations': 0,
                'passed_validations': 0,
                'failed_validations': 0
            }
            
            logger.info(f"Validation configuration {config.config_id} created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating validation configuration: {e}")
            return False
    
    async def get_validation_statistics(
        self,
        config_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get validation statistics and analytics"""
        try:
            if config_id not in self._validation_history:
                return {}
            
            validation_history = self._validation_history[config_id]
            
            # Filter by time range if specified
            if time_range:
                start_time, end_time = time_range
                validation_history = [
                    result for result in validation_history
                    if start_time <= result.validation_timestamp <= end_time
                ]
            
            if not validation_history:
                return {'message': 'No validation data available'}
            
            # Calculate statistics
            total_validations = len(validation_history)
            passed_validations = sum(1 for r in validation_history if r.status == ValidationStatus.PASSED)
            failed_validations = sum(1 for r in validation_history if r.status == ValidationStatus.FAILED)
            
            # Issue statistics
            total_issues = sum(len(r.issues) for r in validation_history)
            critical_issues = sum(r.critical_issues_count for r in validation_history)
            
            # Performance statistics
            avg_validation_time = sum(r.validation_duration_ms for r in validation_history) / total_validations
            avg_compliance_score = sum(r.overall_score for r in validation_history) / total_validations
            
            return {
                'summary': {
                    'total_validations': total_validations,
                    'passed_validations': passed_validations,
                    'failed_validations': failed_validations,
                    'pass_rate': (passed_validations / total_validations) * 100,
                    'total_issues_found': total_issues,
                    'critical_issues_found': critical_issues
                },
                'performance': {
                    'average_validation_time_ms': avg_validation_time,
                    'average_compliance_score': avg_compliance_score
                },
                'trends': await self._calculate_validation_trends(validation_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting validation statistics: {e}")
            return {}
    
    # Helper methods
    
    def _initialize_default_configuration(self) -> None:
        """Initialize default validation configuration"""
        try:
            default_rules = [
                ValidationRule(
                    rule_id="content_profanity_check",
                    name="Content Profanity Check",
                    description="Check for inappropriate language and content",
                    category=ValidationCategory.CONTENT_SAFETY,
                    severity=ValidationSeverity.ERROR
                ),
                ValidationRule(
                    rule_id="challenge_duration_limits",
                    name="Challenge Duration Limits",
                    description="Validate challenge duration is within acceptable limits",
                    category=ValidationCategory.BUSINESS_RULES,
                    severity=ValidationSeverity.ERROR,
                    parameters={
                        'min_duration_days': 1,
                        'max_duration_days': 365
                    }
                ),
                ValidationRule(
                    rule_id="data_format_validation",
                    name="Data Format Validation",
                    description="Validate data structure and format",
                    category=ValidationCategory.TECHNICAL_COMPLIANCE,
                    severity=ValidationSeverity.ERROR,
                    parameters={
                        'required_fields': ['title', 'description', 'challenge_type']
                    }
                ),
                ValidationRule(
                    rule_id="reward_value_limits",
                    name="Reward Value Limits",
                    description="Validate reward values are within acceptable limits",
                    category=ValidationCategory.BUSINESS_RULES,
                    severity=ValidationSeverity.WARNING,
                    parameters={
                        'max_monetary_reward': 10000.0,
                        'min_monetary_reward': 0.0
                    }
                )
            ]
            
            default_config = ValidationConfiguration(
                config_id=self.default_config_id,
                name="Default Challenge Validation",
                description="Standard validation configuration for challenges",
                rules=default_rules,
                stop_on_critical=True,
                stop_on_blocking=True,
                ai_validation_enabled=False,
                strict_mode=False,
                auto_fix_enabled=True
            )
            
            self._validation_configurations[self.default_config_id] = default_config
            self._validation_metrics[self.default_config_id] = {
                'created_at': datetime.now(timezone.utc),
                'total_validations': 0,
                'passed_validations': 0,
                'failed_validations': 0
            }
            
        except Exception as e:
            logger.error(f"Error initializing default configuration: {e}")
    
    async def _validate_category(
        self,
        data: Any,
        category: ValidationCategory,
        rules: List[ValidationRule],
        context: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate specific category rules"""
        try:
            engine = self._rule_engines.get(category)
            if not engine:
                logger.warning(f"No validation engine for category {category}")
                return []
            
            all_issues = []
            
            for rule in rules:
                try:
                    issues = await engine.validate(data, rule, context)
                    all_issues.extend(issues)
                except Exception as e:
                    logger.error(f"Error validating rule {rule.rule_id}: {e}")
                    all_issues.append(ValidationIssue(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=ValidationSeverity.ERROR,
                        message=f"Rule validation error: {str(e)}"
                    ))
            
            return all_issues
            
        except Exception as e:
            logger.error(f"Error validating category {category}: {e}")
            return []
    
    def _generate_validation_id(
        self,
        data: Any,
        target_type: str,
        target_id: Optional[str]
    ) -> str:
        """Generate unique validation ID"""
        timestamp = int(datetime.now(timezone.utc).timestamp())
        data_hash = hash(str(data))
        return f"validation_{target_type}_{target_id or 'unknown'}_{timestamp}_{abs(data_hash)}"
    
    def _calculate_overall_score(self, result: ValidationResult) -> float:
        """Calculate overall compliance score"""
        try:
            if not result.issues:
                return 100.0
            
            # Weighted scoring based on severity
            severity_weights = {
                ValidationSeverity.CRITICAL: -50.0,
                ValidationSeverity.BLOCKING: -40.0,
                ValidationSeverity.ERROR: -20.0,
                ValidationSeverity.WARNING: -5.0,
                ValidationSeverity.INFO: -1.0
            }
            
            total_deduction = 0.0
            for issue in result.issues:
                total_deduction += severity_weights.get(issue.severity, -10.0)
            
            score = max(0.0, 100.0 + total_deduction)
            return min(100.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    def _determine_compliance(
        self,
        result: ValidationResult,
        configuration: ValidationConfiguration
    ) -> bool:
        """Determine if validation result is compliant"""
        try:
            # Not compliant if critical or blocking issues
            if result.critical_issues_count > 0 or result.blocking_issues_count > 0:
                return False
            
            # In strict mode, any error is non-compliant
            if configuration.strict_mode and result.error_issues_count > 0:
                return False
            
            # Check overall score threshold
            min_score_threshold = 70.0  # Configurable threshold
            if result.overall_score < min_score_threshold:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error determining compliance: {e}")
            return False
    
    async def _generate_recommendations(
        self,
        result: ValidationResult
    ) -> List[str]:
        """Generate recommendations based on validation result"""
        recommendations = []
        
        try:
            # Critical issue recommendations
            if result.critical_issues_count > 0:
                recommendations.append("Address critical issues immediately before proceeding")
            
            # Category-specific recommendations
            category_issues = {}
            for issue in result.issues:
                if issue.category not in category_issues:
                    category_issues[issue.category] = 0
                category_issues[issue.category] += 1
            
            for category, count in category_issues.items():
                if count >= 3:
                    if category == ValidationCategory.CONTENT_SAFETY:
                        recommendations.append("Review content safety guidelines and policies")
                    elif category == ValidationCategory.BUSINESS_RULES:
                        recommendations.append("Verify compliance with business rules and constraints")
                    elif category == ValidationCategory.TECHNICAL_COMPLIANCE:
                        recommendations.append("Check technical requirements and API specifications")
            
            # Score-based recommendations
            if result.overall_score < 50:
                recommendations.append("Consider redesigning challenge to meet quality standards")
            elif result.overall_score < 80:
                recommendations.append("Make improvements to increase compliance score")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _store_validation_result(self, result: ValidationResult) -> None:
        """Store validation result for analytics"""
        try:
            config_id = result.configuration_used
            
            if config_id not in self._validation_history:
                self._validation_history[config_id] = []
            
            self._validation_history[config_id].append(result)
            
            # Update metrics
            if config_id in self._validation_metrics:
                metrics = self._validation_metrics[config_id]
                metrics['total_validations'] += 1
                
                if result.status == ValidationStatus.PASSED:
                    metrics['passed_validations'] += 1
                elif result.status == ValidationStatus.FAILED:
                    metrics['failed_validations'] += 1
            
            # Limit history size
            max_history = self.config.get('max_history_size', 10000)
            if len(self._validation_history[config_id]) > max_history:
                self._validation_history[config_id] = self._validation_history[config_id][-max_history:]
            
        except Exception as e:
            logger.error(f"Error storing validation result: {e}")
    
    async def _calculate_validation_trends(
        self,
        validation_history: List[ValidationResult]
    ) -> Dict[str, Any]:
        """Calculate validation trends over time"""
        try:
            if len(validation_history) < 2:
                return {'message': 'Insufficient data for trend analysis'}
            
            # Group by day
            daily_stats = {}
            for result in validation_history:
                day = result.validation_timestamp.date()
                if day not in daily_stats:
                    daily_stats[day] = {
                        'total': 0,
                        'passed': 0,
                        'failed': 0,
                        'avg_score': 0.0,
                        'scores': []
                    }
                
                stats = daily_stats[day]
                stats['total'] += 1
                stats['scores'].append(result.overall_score)
                
                if result.status == ValidationStatus.PASSED:
                    stats['passed'] += 1
                elif result.status == ValidationStatus.FAILED:
                    stats['failed'] += 1
            
            # Calculate daily averages
            trend_data = []
            for day in sorted(daily_stats.keys()):
                stats = daily_stats[day]
                avg_score = sum(stats['scores']) / len(stats['scores'])
                pass_rate = (stats['passed'] / stats['total']) * 100
                
                trend_data.append({
                    'date': day.isoformat(),
                    'total_validations': stats['total'],
                    'pass_rate': pass_rate,
                    'average_score': avg_score
                })
            
            return {
                'daily_trends': trend_data,
                'total_days': len(daily_stats)
            }
            
        except Exception as e:
            logger.error(f"Error calculating validation trends: {e}")
            return {}