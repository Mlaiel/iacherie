"""Business Rule Validation Engine for Crawler System
==================================================

Enterprise-grade business rule validation system for the IA Influencer Agent Platform
providing comprehensive business logic enforcement and compliance validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use, reproduction, or distribution strictly prohibited

Features:
- Dynamic business rule definition and execution
- Complex conditional logic support
- Multi-field validation rules
- Industry-specific compliance checks
- Monetization and licensing validation
- Creator profile validation
"""

import re
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from ..utils.exceptions import ValidationException

logger = logging.getLogger(__name__)


class RuleSeverity(Enum):
    """
Business rule severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    BLOCKING = "blocking"


class RuleCategory(Enum):
    """Business rule categories"""

    CREATOR_PROFILE = "creator_profile"
    CONTENT_LICENSING = "content_licensing"
    MONETIZATION = "monetization"
    PLATFORM_COMPLIANCE = "platform_compliance"
    QUALITY_STANDARDS = "quality_standards"
    SECURITY_COMPLIANCE = "security_compliance"
    DATA_PROTECTION = "data_protection"
    WORKFLOW = "workflow"
    BUSINESS_LOGIC = "business_logic"


@dataclass
class BusinessRuleViolation:
    """Business rule violation details"""
    rule_name: str
    severity: RuleSeverity
    category: RuleCategory
    message: str
    field_path: Optional[str] = None
    current_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    suggestion: Optional[str] = None
    violation_code: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BusinessRuleResult:
    """
Business rule validation result"""
    is_valid: bool
    violations: List[BusinessRuleViolation] = field(default_factory=list)
    warnings: List[BusinessRuleViolation] = field(default_factory=list)
    passed_rules: List[str] = field(default_factory=list)
    failed_rules: List[str] = field(default_factory=list)
    validation_time_ms: float = 0.0
    total_rules_executed: int = 0
    validated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def has_critical_violations(self) -> bool:
        """
Check if there are critical or blocking violations"""
        return any(v.severity in [RuleSeverity.CRITICAL, RuleSeverity.BLOCKING] 
                  for v in self.violations)
    
    @property
    def violation_count_by_severity(self) -> Dict[str, int]:
        """
Count violations by severity"""
        counts = {}
        for violation in self.violations:
            severity = violation.severity.value
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    @property
    def success_rate(self) -> float:
        """
Calculate rule success rate"""
        if self.total_rules_executed == 0:
            return 0.0
        return len(self.passed_rules) / self.total_rules_executed


class BusinessRule:
    """
Individual business rule definition"""
    
    def __init__(
        self,
        name: str,
        category: RuleCategory,
        severity: RuleSeverity,
        description: str,
        validator_function: Callable[[Dict[str, Any]], bool],
        error_message: str,
        suggestion: Optional[str] = None,
        violation_code: Optional[str] = None,
        conditions: Optional[List[Callable[[Dict[str, Any]], bool]]] = None,
        priority: int = 0,
        enabled: bool = True
    ):
        self.name = name
        self.category = category
        self.severity = severity
        self.description = description
        self.validator_function = validator_function
        self.error_message = error_message
        self.suggestion = suggestion
        self.violation_code = violation_code or name.upper().replace(' ', '_')
        self.conditions = conditions or []
        self.priority = priority
        self.enabled = enabled
        self.execution_count = 0
        self.success_count = 0
        self.last_executed = None
    
    def should_execute(self, data: Dict[str, Any]) -> bool:
        """
Check if rule should be executed based on conditions"""
        if not self.enabled:
            return False
        
        if not self.conditions:
            return True
        
        return all(condition(data) for condition in self.conditions)
    
    def execute(self, data: Dict[str, Any]) -> Optional[BusinessRuleViolation]:
        """
Execute the business rule"""
        self.execution_count += 1
        self.last_executed = datetime.utcnow()
        
        try:
            if self.validator_function(data):
                self.success_count += 1
                return None
            else:
                return BusinessRuleViolation(
                    rule_name=self.name,
                    severity=self.severity,
                    category=self.category,
                    message=self.error_message,
                    suggestion=self.suggestion,
                    violation_code=self.violation_code
                )
        except Exception as e:
            logger.error(f"Business rule '{self.name}' execution failed: {str(e)}")
            return BusinessRuleViolation(
                rule_name=self.name,
                severity=RuleSeverity.ERROR,
                category=self.category,
                message=f"Rule execution failed: {str(e)}",
                violation_code="RULE_EXECUTION_ERROR"
            )
    
    @property
    def success_rate(self) -> float:
        """Calculate rule success rate"""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count


class BusinessRuleValidator:
    """
    Enterprise-grade business rule validation engine for crawler systems.
    
    Provides comprehensive business logic validation including:
    - Creator profile validation
    - Content licensing compliance
    - Monetization rule enforcement
    - Platform-specific requirements
    - Quality standards validation
    - Security and data protection compliance
    """
    
    def __init__(self):
        self.rules = {}
        self.rule_groups = {}
        self.global_conditions = []
        
        # Performance tracking
        self.validation_stats = {
            'total_validations': 0,
            'total_violations': 0,
            'avg_processing_time': 0.0
        }
        
        # Load predefined business rules
        self._load_predefined_rules()
        
        logger.info("BusinessRuleValidator initialized")
    
    def validate(
        self,
        data: Dict[str, Any],
        rule_categories: Optional[List[RuleCategory]] = None,
        rule_names: Optional[List[str]] = None,
        stop_on_critical: bool = True
    ) -> BusinessRuleResult:
        """
        Validate data against business rules.
        
        Args:
            data: Data to validate
            rule_categories: Optional list of rule categories to execute
            rule_names: Optional list of specific rule names to execute
            stop_on_critical: Stop validation on first critical violation
            
        Returns:
            BusinessRuleResult: Comprehensive validation result
        """
        start_time = datetime.utcnow()
        
        result = BusinessRuleResult(is_valid=True)
        
        # Determine which rules to execute
        rules_to_execute = self._select_rules(rule_categories, rule_names)
        
        # Sort rules by priority (higher priority first)
        rules_to_execute.sort(key=lambda rule: rule.priority, reverse=True)
        
        result.total_rules_executed = len(rules_to_execute)
        
        for rule in rules_to_execute:
            if not rule.should_execute(data):
                continue
            
            violation = rule.execute(data)
            
            if violation:
                if violation.severity in [RuleSeverity.WARNING, RuleSeverity.INFO]:
                    result.warnings.append(violation)
                else:
                    result.violations.append(violation)
                    result.failed_rules.append(rule.name)
                    result.is_valid = False
                    
                    # Stop on critical violation if requested
                    if stop_on_critical and violation.severity in [RuleSeverity.CRITICAL, RuleSeverity.BLOCKING]:
                        break
            else:
                result.passed_rules.append(rule.name)
        
        # Record processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.validation_time_ms = processing_time
        
        # Update statistics
        self._update_statistics(result, processing_time)
        
        logger.debug(f"Business rule validation completed in {processing_time:.2f}ms")
        return result
    
    def add_rule(self, rule: BusinessRule) -> None:
        """Add a business rule to the validator"""
        self.rules[rule.name] = rule
        logger.debug(f"Added business rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove a business rule from the validator"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.debug(f"Removed business rule: {rule_name}")
    
    def enable_rule(self, rule_name: str) -> None:
        """Enable a specific rule"""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = True
    
    def disable_rule(self, rule_name: str) -> None:
        """
Disable a specific rule"""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = False
    
    def add_rule_group(self, group_name: str, rule_names: List[str]) -> None:
        """
Add a group of related rules"""
        self.rule_groups[group_name] = rule_names
        logger.debug(f"Added rule group '{group_name}' with {len(rule_names)} rules")
    
    def validate_creator_profile(self, profile_data: Dict[str, Any]) -> BusinessRuleResult:
        """Validate creator profile data"""
        return self.validate(
            profile_data,
            rule_categories=[RuleCategory.CREATOR_PROFILE]
        )
    
    def validate_content_licensing(self, content_data: Dict[str, Any]) -> BusinessRuleResult:
        """
Validate content licensing data"""
        return self.validate(
            content_data,
            rule_categories=[RuleCategory.CONTENT_LICENSING]
        )
    
    def validate_monetization(self, monetization_data: Dict[str, Any]) -> BusinessRuleResult:
        """
Validate monetization data"""
        return self.validate(
            monetization_data,
            rule_categories=[RuleCategory.MONETIZATION]
        )
    
    def validate_platform_compliance(
        self, 
        content_data: Dict[str, Any], 
        platform: str
    ) -> BusinessRuleResult:
        """
Validate platform-specific compliance"""
        # Add platform context to data
        validation_data = {**content_data, '_platform': platform}
        return self.validate(
            validation_data,
            rule_categories=[RuleCategory.PLATFORM_COMPLIANCE]
        )
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """
Get rule execution statistics"""
        rule_stats = {}
        for name, rule in self.rules.items():
            rule_stats[name] = {
                'execution_count': rule.execution_count,
                'success_count': rule.success_count,
                'success_rate': rule.success_rate,
                'last_executed': rule.last_executed.isoformat() if rule.last_executed else None,
                'enabled': rule.enabled,
                'category': rule.category.value,
                'severity': rule.severity.value
            }
        
        return {
            'global_stats': self.validation_stats,
            'rule_stats': rule_stats
        }
    
    # Helper methods
    
    def _select_rules(
        self, 
        rule_categories: Optional[List[RuleCategory]] = None,
        rule_names: Optional[List[str]] = None
    ) -> List[BusinessRule]:
        """
Select rules to execute based on criteria"""
        
        if rule_names:
            # Execute specific named rules
            return [self.rules[name] for name in rule_names if name in self.rules]
        
        if rule_categories:
            # Execute rules from specific categories
            return [
                rule for rule in self.rules.values()
                if rule.category in rule_categories and rule.enabled
            ]
        
        # Execute all enabled rules
        return [rule for rule in self.rules.values() if rule.enabled]
    
    def _update_statistics(self, result: BusinessRuleResult, processing_time: float) -> None:
        """
Update global validation statistics"""
        self.validation_stats['total_validations'] += 1
        self.validation_stats['total_violations'] += len(result.violations)
        
        # Update average processing time
        current_avg = self.validation_stats['avg_processing_time']
        total_validations = self.validation_stats['total_validations']
        self.validation_stats['avg_processing_time'] = (
            (current_avg * (total_validations - 1) + processing_time) / total_validations
        )
    
    def _load_predefined_rules(self) -> None:
        """
Load predefined business rules"""
        
        # Creator Profile Rules
        self._load_creator_profile_rules()
        
        # Content Licensing Rules
        self._load_content_licensing_rules()
        
        # Monetization Rules
        self._load_monetization_rules()
        
        # Platform Compliance Rules
        self._load_platform_compliance_rules()
        
        # Quality Standards Rules
        self._load_quality_standards_rules()
        
        # Security Compliance Rules
        self._load_security_compliance_rules()
        
        # Data Protection Rules
        self._load_data_protection_rules()
    
    def _load_creator_profile_rules(self) -> None:
        """
Load creator profile validation rules"""
        
        # Profile completeness rule
        self.add_rule(BusinessRule(
            name="creator_profile_completeness",
            category=RuleCategory.CREATOR_PROFILE,
            severity=RuleSeverity.WARNING,
            description="Creator profile must have essential information",
            validator_function=lambda data: (
                data.get('username') and
                data.get('email') and
                data.get('bio') and
                len(data.get('bio', '')) >= 50
            ),
            error_message="Creator profile is incomplete",
            suggestion="Complete username, email, and bio (minimum 50 characters)"
        ))
        
        # Age verification rule
        self.add_rule(BusinessRule(
            name="creator_age_verification",
            category=RuleCategory.CREATOR_PROFILE,
            severity=RuleSeverity.CRITICAL,
            description="Creator must be 18 or older for monetization",
            validator_function=lambda data: data.get('age', 0) >= 18,
            error_message="Creator must be 18 or older for monetization features",
            suggestion="Verify age or restrict access to monetization features",
            conditions=[lambda data: data.get('monetization_enabled', False)]
        ))
        
        # Contact information rule
        self.add_rule(BusinessRule(
            name="creator_contact_verification",
            category=RuleCategory.CREATOR_PROFILE,
            severity=RuleSeverity.ERROR,
            description="Creator must have verified contact information",
            validator_function=lambda data: (
                data.get('email_verified', False) and
                data.get('phone_verified', False)
            ),
            error_message="Email and phone verification required",
            suggestion="Complete email and phone verification process",
            conditions=[lambda data: data.get('verification_level') == 'premium']
        ))
        
        # Social media presence rule
        self.add_rule(BusinessRule(
            name="creator_social_presence",
            category=RuleCategory.CREATOR_PROFILE,
            severity=RuleSeverity.INFO,
            description="Creator should have active social media presence",
            validator_function=lambda data: (
                len(data.get('social_accounts', [])) >= 2 and
                data.get('total_followers', 0) >= 100
            ),
            error_message="Limited social media presence detected",
            suggestion="Connect more social accounts and build follower base"
        ))
    
    def _load_content_licensing_rules(self) -> None:
        """Load content licensing validation rules"""
        
        # Content ownership rule
        self.add_rule(BusinessRule(
            name="content_ownership_verification",
            category=RuleCategory.CONTENT_LICENSING,
            severity=RuleSeverity.CRITICAL,
            description="Content must have clear ownership documentation",
            validator_function=lambda data: (
                data.get('ownership_verified', False) and
                data.get('copyright_holder') and
                data.get('creation_date')
            ),
            error_message="Content ownership not properly documented",
            suggestion="Provide ownership verification and copyright information"
        ))
        
        # License compatibility rule
        self.add_rule(BusinessRule(
            name="license_compatibility_check",
            category=RuleCategory.CONTENT_LICENSING,
            severity=RuleSeverity.ERROR,
            description="Content license must be compatible with platform usage",
            validator_function=lambda data: self._check_license_compatibility(data),
            error_message="Content license incompatible with intended usage",
            suggestion="Update license terms or modify usage rights"
        ))
        
        # Commercial usage rights rule
        self.add_rule(BusinessRule(
            name="commercial_usage_rights",
            category=RuleCategory.CONTENT_LICENSING,
            severity=RuleSeverity.ERROR,
            description="Commercial usage requires appropriate licensing",
            validator_function=lambda data: (
                not data.get('commercial_usage', False) or
                data.get('commercial_license', False)
            ),
            error_message="Commercial usage requires commercial license",
            suggestion="Upgrade to commercial license or disable commercial usage"
        ))
        
        # Attribution requirements rule
        self.add_rule(BusinessRule(
            name="attribution_requirements",
            category=RuleCategory.CONTENT_LICENSING,
            severity=RuleSeverity.WARNING,
            description="Content should have proper attribution information",
            validator_function=lambda data: (
                data.get('attribution_text') or
                not data.get('requires_attribution', True)
            ),
            error_message="Missing attribution information",
            suggestion="Provide proper attribution text for content usage"
        ))
    
    def _load_monetization_rules(self) -> None:
        """Load monetization validation rules"""
        
        # Revenue threshold rule
        self.add_rule(BusinessRule(
            name="minimum_revenue_threshold",
            category=RuleCategory.MONETIZATION,
            severity=RuleSeverity.WARNING,
            description="Content should meet minimum revenue potential",
            validator_function=lambda data: data.get('projected_revenue', 0) >= 10.0,
            error_message="Content below minimum revenue threshold",
            suggestion="Optimize content for better monetization potential"
        ))
        
        # Payment information rule
        self.add_rule(BusinessRule(
            name="payment_information_complete",
            category=RuleCategory.MONETIZATION,
            severity=RuleSeverity.CRITICAL,
            description="Complete payment information required for monetization",
            validator_function=lambda data: (
                data.get('payment_method') and
                data.get('tax_information_verified', False) and
                data.get('bank_account_verified', False)
            ),
            error_message="Incomplete payment information",
            suggestion="Complete payment setup including tax and banking details",
            conditions=[lambda data: data.get('monetization_enabled', False)]
        ))
        
        # Revenue sharing rule
        self.add_rule(BusinessRule(
            name="revenue_sharing_agreement",
            category=RuleCategory.MONETIZATION,
            severity=RuleSeverity.ERROR,
            description="Revenue sharing terms must be agreed upon",
            validator_function=lambda data: data.get('revenue_sharing_agreed', False),
            error_message="Revenue sharing agreement not signed",
            suggestion="Review and sign revenue sharing agreement",
            conditions=[lambda data: data.get('has_collaborators', False)]
        ))
        
        # Geographic restrictions rule
        self.add_rule(BusinessRule(
            name="geographic_monetization_restrictions",
            category=RuleCategory.MONETIZATION,
            severity=RuleSeverity.WARNING,
            description="Check geographic restrictions for monetization",
            validator_function=lambda data: self._check_geographic_restrictions(data),
            error_message="Geographic restrictions may limit monetization",
            suggestion="Review geographic limitations and adjust strategy"
        ))
    
    def _load_platform_compliance_rules(self) -> None:
        """Load platform compliance validation rules"""
        
        # Content length rule
        self.add_rule(BusinessRule(
            name="platform_content_length",
            category=RuleCategory.PLATFORM_COMPLIANCE,
            severity=RuleSeverity.ERROR,
            description="Content must meet platform length requirements",
            validator_function=lambda data: self._check_platform_content_length(data),
            error_message="Content length violates platform requirements",
            suggestion="Adjust content length to meet platform specifications"
        ))
        
        # Content format rule
        self.add_rule(BusinessRule(
            name="platform_content_format",
            category=RuleCategory.PLATFORM_COMPLIANCE,
            severity=RuleSeverity.ERROR,
            description="Content format must be supported by platform",
            validator_function=lambda data: self._check_platform_content_format(data),
            error_message="Content format not supported by target platform",
            suggestion="Convert content to supported format"
        ))
        
        # Community guidelines rule
        self.add_rule(BusinessRule(
            name="community_guidelines_compliance",
            category=RuleCategory.PLATFORM_COMPLIANCE,
            severity=RuleSeverity.CRITICAL,
            description="Content must comply with platform community guidelines",
            validator_function=lambda data: self._check_community_guidelines(data),
            error_message="Content violates platform community guidelines",
            suggestion="Review and modify content to comply with guidelines"
        ))
        
        # API rate limits rule
        self.add_rule(BusinessRule(
            name="api_rate_limits_compliance",
            category=RuleCategory.PLATFORM_COMPLIANCE,
            severity=RuleSeverity.WARNING,
            description="API usage must respect platform rate limits",
            validator_function=lambda data: self._check_api_rate_limits(data),
            error_message="API usage approaching or exceeding rate limits",
            suggestion="Implement rate limiting and optimize API calls"
        ))
    
    def _load_quality_standards_rules(self) -> None:
        """Load quality standards validation rules"""
        
        # Content quality score rule
        self.add_rule(BusinessRule(
            name="minimum_content_quality",
            category=RuleCategory.QUALITY_STANDARDS,
            severity=RuleSeverity.WARNING,
            description="Content must meet minimum quality standards",
            validator_function=lambda data: data.get('quality_score', 0) >= 0.7,
            error_message="Content quality below acceptable standards",
            suggestion="Improve content quality through editing and optimization"
        ))
        
        # Metadata completeness rule
        self.add_rule(BusinessRule(
            name="metadata_completeness",
            category=RuleCategory.QUALITY_STANDARDS,
            severity=RuleSeverity.INFO,
            description="Content should have complete metadata",
            validator_function=lambda data: (
                data.get('title') and
                data.get('description') and
                data.get('tags') and
                len(data.get('tags', [])) >= 3
            ),
            error_message="Incomplete content metadata",
            suggestion="Add title, description, and relevant tags"
        ))
        
        # SEO optimization rule
        self.add_rule(BusinessRule(
            name="seo_optimization",
            category=RuleCategory.QUALITY_STANDARDS,
            severity=RuleSeverity.INFO,
            description="Content should be optimized for search engines",
            validator_function=lambda data: data.get('seo_score', 0) >= 0.6,
            error_message="Content needs SEO optimization",
            suggestion="Optimize keywords, meta descriptions, and structure for SEO"
        ))
    
    def _load_security_compliance_rules(self) -> None:
        """Load security compliance validation rules"""
        
        # Malware scan rule
        self.add_rule(BusinessRule(
            name="malware_scan_clear",
            category=RuleCategory.SECURITY_COMPLIANCE,
            severity=RuleSeverity.BLOCKING,
            description="Content must pass malware scanning",
            validator_function=lambda data: data.get('malware_scan_result') == 'clean',
            error_message="Content failed malware scan",
            suggestion="Remove malicious content and rescan"
        ))
        
        # Sensitive information rule
        self.add_rule(BusinessRule(
            name="no_sensitive_information",
            category=RuleCategory.SECURITY_COMPLIANCE,
            severity=RuleSeverity.CRITICAL,
            description="Content must not contain sensitive information",
            validator_function=lambda data: not self._contains_sensitive_info(data),
            error_message="Content contains potential sensitive information",
            suggestion="Remove or redact sensitive information"
        ))
        
        # Encryption requirements rule
        self.add_rule(BusinessRule(
            name="encryption_requirements",
            category=RuleCategory.SECURITY_COMPLIANCE,
            severity=RuleSeverity.ERROR,
            description="Sensitive content must be encrypted",
            validator_function=lambda data: (
                not data.get('contains_pii', False) or
                data.get('encrypted', False)
            ),
            error_message="Sensitive content requires encryption",
            suggestion="Enable encryption for content containing PII"
        ))
    
    def _load_data_protection_rules(self) -> None:
        """Load data protection validation rules"""
        
        # GDPR compliance rule
        self.add_rule(BusinessRule(
            name="gdpr_compliance",
            category=RuleCategory.DATA_PROTECTION,
            severity=RuleSeverity.CRITICAL,
            description="Data processing must comply with GDPR",
            validator_function=lambda data: self._check_gdpr_compliance(data),
            error_message="Data processing violates GDPR requirements",
            suggestion="Ensure proper consent and data protection measures"
        ))
        
        # Data retention rule
        self.add_rule(BusinessRule(
            name="data_retention_policy",
            category=RuleCategory.DATA_PROTECTION,
            severity=RuleSeverity.WARNING,
            description="Data must comply with retention policies",
            validator_function=lambda data: self._check_data_retention(data),
            error_message="Data exceeds retention policy limits",
            suggestion="Review and apply data retention policies"
        ))
        
        # Consent verification rule
        self.add_rule(BusinessRule(
            name="user_consent_verification",
            category=RuleCategory.DATA_PROTECTION,
            severity=RuleSeverity.ERROR,
            description="User consent required for data processing",
            validator_function=lambda data: (
                not data.get('requires_consent', True) or
                data.get('consent_obtained', False)
            ),
            error_message="Missing user consent for data processing",
            suggestion="Obtain explicit user consent before processing data"
        ))
    
    # Helper validation functions
    
    def _check_license_compatibility(self, data: Dict[str, Any]) -> bool:
        """Check license compatibility with intended usage"""
        license_type = data.get('license_type', '').lower()
        commercial_usage = data.get('commercial_usage', False)
        modification_allowed = data.get('modification_allowed', False)
        
        # Creative Commons license compatibility
        if 'cc-by-nc' in license_type and commercial_usage:
            return False
        if 'cc-by-nd' in license_type and modification_allowed:
            return False
        
        return True
    
    def _check_geographic_restrictions(self, data: Dict[str, Any]) -> bool:
        """
Check geographic restrictions for monetization"""
        user_country = data.get('user_country', '').upper()
        restricted_countries = data.get('monetization_restricted_countries', [])
        
        return user_country not in [country.upper() for country in restricted_countries]
    
    def _check_platform_content_length(self, data: Dict[str, Any]) -> bool:
        """
Check platform-specific content length requirements"""
        platform = data.get('_platform', '').lower()
        content = data.get('content', '')
        content_length = len(content)
        
        platform_limits = {
            'twitter': 280,
            'instagram': 2200,
            'tiktok': 150,
            'youtube': 5000,
            'linkedin': 3000
        }
        
        limit = platform_limits.get(platform)
        if limit:
            return content_length <= limit
        
        return True
    
    def _check_platform_content_format(self, data: Dict[str, Any]) -> bool:
        """
Check platform-specific content format requirements"""
        platform = data.get('_platform', '').lower()
        content_type = data.get('content_type', '').lower()
        
        platform_formats = {
            'twitter': ['text', 'image', 'video'],
            'instagram': ['image', 'video', 'story'],
            'tiktok': ['video'],
            'youtube': ['video'],
            'linkedin': ['text', 'image', 'video', 'document']
        }
        
        supported_formats = platform_formats.get(platform, [])
        if supported_formats:
            return content_type in supported_formats
        
        return True
    
    def _check_community_guidelines(self, data: Dict[str, Any]) -> bool:
        """
Check community guidelines compliance"""
        content = data.get('content', '').lower()
        
        # Check for prohibited content patterns
        prohibited_patterns = [
            r'\b(hate|violence|harassment)\b',
            r'\b(spam|scam|fraud)\b',
            r'\b(adult|explicit|nsfw)\b',
            r'\b(drug|illegal|weapon)\b'
        ]
        
        for pattern in prohibited_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True
    
    def _check_api_rate_limits(self, data: Dict[str, Any]) -> bool:
        """
Check API rate limits compliance"""
        current_requests = data.get('api_requests_per_hour', 0)
        rate_limit = data.get('api_rate_limit', 1000)
        
        return current_requests < rate_limit * 0.8  # 80% threshold
    
    def _contains_sensitive_info(self, data: Dict[str, Any]) -> bool:
        """
Check if content contains sensitive information"""
        content = str(data.get('content', ''))
        
        # Patterns for sensitive information
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
            r'\b(?:password|pwd|secret|key):\s*\S+\b'  # Passwords/keys
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _check_gdpr_compliance(self, data: Dict[str, Any]) -> bool:
        """
Check GDPR compliance"""
        if not data.get('processes_eu_data', False):
            return True  # GDPR doesn't apply
        
        required_elements = [
            'privacy_policy_accepted',
            'data_processing_consent',
            'right_to_deletion_implemented',
            'data_portability_supported'
        ]
        
        return all(data.get(element, False) for element in required_elements)
    
    def _check_data_retention(self, data: Dict[str, Any]) -> bool:
        """
Check data retention policy compliance"""
        creation_date = data.get('created_at')
        retention_period_days = data.get('retention_period_days', 365)
        
        if not creation_date:
            return True  # No creation date, can't check retention
        
        if isinstance(creation_date, str):
            try:
                creation_date = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
            except ValueError:
                return True  # Invalid date format, skip check
        
        age_days = (datetime.utcnow() - creation_date).days
        return age_days <= retention_period_days
