"""Compliance Checker - Enterprise Compliance Validation System

Ultra-advanced compliance checking system for platform requirements, legal standards,
AI content regulations, and content protection compliance across multiple jurisdictions
and platforms for the IA-Influencer platform.

Business Logic:
Content submission → AI compliance checks → Platform validation → Legal checks →
Copyright compliance → Data privacy validation → Regulatory compliance → 
Protection compliance → Violation detection → Compliance reporting

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violators will face immediate legal action under German and international law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import re
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class ComplianceCategory(Enum):
    """
Categories of compliance requirements"""

    PLATFORM_POLICY = "platform_policy"
    LEGAL_REGULATORY = "legal_regulatory"
    DATA_PRIVACY = "data_privacy"
    CONTENT_SAFETY = "content_safety"
    COPYRIGHT = "copyright"
    ACCESSIBILITY = "accessibility"
    ADVERTISING = "advertising"
    USER_PROTECTION = "user_protection"


class ComplianceSeverity(Enum):
    """Compliance violation severity levels"""

    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


class Platform(Enum):
    """Supported platforms for compliance checking"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    GENERIC = "generic"


class Jurisdiction(Enum):
    """Legal jurisdictions"""

    EU = "eu"  # European Union
    US = "us"  # United States
    DE = "de"  # Germany
    FR = "fr"  # France
    UK = "uk"  # United Kingdom
    CA = "ca"  # Canada
    GLOBAL = "global"


@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    id: str
    name: str
    description: str
    category: ComplianceCategory
    severity: ComplianceSeverity
    platforms: List[Platform]
    jurisdictions: List[Jurisdiction]
    enabled: bool = True
    
    # Rule configuration
    patterns: List[str] = field(default_factory=list)  # Regex patterns
    keywords: List[str] = field(default_factory=list)  # Flagged keywords
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    required_fields: List[str] = field(default_factory=list)
    prohibited_content: List[str] = field(default_factory=list)
    
    # Metadata
    source: str = ""  # Source of the rule (e.g., platform policy)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    
    def applies_to_platform(self, platform: Platform) -> bool:
        """Check if rule applies to specific platform"""
        return Platform.GENERIC in self.platforms or platform in self.platforms
    
    def applies_to_jurisdiction(self, jurisdiction: Jurisdiction) -> bool:
        """
Check if rule applies to specific jurisdiction"""
        return Jurisdiction.GLOBAL in self.jurisdictions or jurisdiction in self.jurisdictions


@dataclass
class ComplianceViolation:
    """
Individual compliance violation"""
    rule_id: str
    rule_name: str
    category: ComplianceCategory
    severity: ComplianceSeverity
    message: str
    
    # Violation details
    field: Optional[str] = None
    detected_content: Optional[str] = None
    position: Optional[int] = None  # Character position in content
    platforms_affected: List[Platform] = field(default_factory=list)
    jurisdictions_affected: List[Jurisdiction] = field(default_factory=list)
    
    # Remediation
    suggestions: List[str] = field(default_factory=list)
    required_action: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'field': self.field,
            'detected_content': self.detected_content,
            'position': self.position,
            'platforms_affected': [p.value for p in self.platforms_affected],
            'jurisdictions_affected': [j.value for j in self.jurisdictions_affected],
            'suggestions': self.suggestions,
            'required_action': self.required_action,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence
        }


@dataclass
class ComplianceReport:
    """
Comprehensive compliance assessment report"""
    content_id: str
    overall_compliance_score: float  # 0-100
    is_compliant: bool
    
    # Violation breakdown
    total_violations: int = 0
    critical_violations: int = 0
    violation_violations: int = 0
    warning_violations: int = 0
    
    # Platform compliance
    platform_compliance: Dict[Platform, bool] = field(default_factory=dict)
    jurisdiction_compliance: Dict[Jurisdiction, bool] = field(default_factory=dict)
    
    # Violations and recommendations
    violations: List[ComplianceViolation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    required_actions: List[str] = field(default_factory=list)
    
    # Analysis metadata
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
    platforms_checked: List[Platform] = field(default_factory=list)
    jurisdictions_checked: List[Jurisdiction] = field(default_factory=list)
    
    def add_violation(self, violation: ComplianceViolation):
        """
Add a compliance violation"""
        self.violations.append(violation)
        self.total_violations += 1
        
        if violation.severity == ComplianceSeverity.CRITICAL:
            self.critical_violations += 1
        elif violation.severity == ComplianceSeverity.VIOLATION:
            self.violation_violations += 1
        elif violation.severity == ComplianceSeverity.WARNING:
            self.warning_violations += 1
    
    def get_violations_by_category(self, category: ComplianceCategory) -> List[ComplianceViolation]:
        """
Get violations by category"""
        return [v for v in self.violations if v.category == category]
    
    def get_critical_violations(self) -> List[ComplianceViolation]:
        """
Get critical violations"""
        return [v for v in self.violations if v.severity == ComplianceSeverity.CRITICAL]
    
    def has_blocking_violations(self) -> bool:
        """
Check if there are blocking violations"""
        return self.critical_violations > 0 or self.violation_violations > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'overall_compliance_score': self.overall_compliance_score,
            'is_compliant': self.is_compliant,
            'violation_counts': {
                'total': self.total_violations,
                'critical': self.critical_violations,
                'violations': self.violation_violations,
                'warnings': self.warning_violations
            },
            'platform_compliance': {p.value: compliant for p, compliant in self.platform_compliance.items()},
            'jurisdiction_compliance': {j.value: compliant for j, compliant in self.jurisdiction_compliance.items()},
            'violations': [v.to_dict() for v in self.violations],
            'recommendations': self.recommendations,
            'required_actions': self.required_actions,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'processing_time_ms': self.processing_time_ms,
            'platforms_checked': [p.value for p in self.platforms_checked],
            'jurisdictions_checked': [j.value for j in self.jurisdictions_checked]
        }


class PlatformPolicyChecker:
    """
Platform-specific policy compliance checker"""
    
    def __init__(self):
        self.platform_rules = self._initialize_platform_rules()
    
    def _initialize_platform_rules(self) -> Dict[Platform, List[ComplianceRule]]:
        """
Initialize platform-specific compliance rules"""
        rules = {
            Platform.YOUTUBE: [
                ComplianceRule(
                    id="youtube_title_length",
                    name="YouTube Title Length",
                    description="YouTube title must be 100 characters or less",
                    category=ComplianceCategory.PLATFORM_POLICY,
                    severity=ComplianceSeverity.VIOLATION,
                    platforms=[Platform.YOUTUBE],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    max_length=100,
                    source="YouTube Community Guidelines"
                ),
                ComplianceRule(
                    id="youtube_description_length",
                    name="YouTube Description Length",
                    description="YouTube description must be 5000 characters or less",
                    category=ComplianceCategory.PLATFORM_POLICY,
                    severity=ComplianceSeverity.WARNING,
                    platforms=[Platform.YOUTUBE],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    max_length=5000,
                    source="YouTube Community Guidelines"
                ),
                ComplianceRule(
                    id="youtube_prohibited_content",
                    name="YouTube Prohibited Content",
                    description="Content that violates YouTube community guidelines",
                    category=ComplianceCategory.CONTENT_SAFETY,
                    severity=ComplianceSeverity.CRITICAL,
                    platforms=[Platform.YOUTUBE],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    keywords=["hate speech", "violence", "harassment", "spam"],
                    source="YouTube Community Guidelines"
                )
            ],
            Platform.INSTAGRAM: [
                ComplianceRule(
                    id="instagram_caption_length",
                    name="Instagram Caption Length",
                    description="Instagram caption must be 2200 characters or less",
                    category=ComplianceCategory.PLATFORM_POLICY,
                    severity=ComplianceSeverity.VIOLATION,
                    platforms=[Platform.INSTAGRAM],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    max_length=2200,
                    source="Instagram Community Guidelines"
                ),
                ComplianceRule(
                    id="instagram_hashtag_limit",
                    name="Instagram Hashtag Limit",
                    description="Instagram posts should have 30 hashtags or less",
                    category=ComplianceCategory.PLATFORM_POLICY,
                    severity=ComplianceSeverity.WARNING,
                    platforms=[Platform.INSTAGRAM],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    patterns=[r"#\w+"],
                    source="Instagram Best Practices"
                )
            ],
            Platform.TIKTOK: [
                ComplianceRule(
                    id="tiktok_caption_length",
                    name="TikTok Caption Length",
                    description="TikTok caption must be 150 characters or less",
                    category=ComplianceCategory.PLATFORM_POLICY,
                    severity=ComplianceSeverity.VIOLATION,
                    platforms=[Platform.TIKTOK],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    max_length=150,
                    source="TikTok Community Guidelines"
                )
            ],
            Platform.LINKEDIN: [
                ComplianceRule(
                    id="linkedin_post_length",
                    name="LinkedIn Post Length",
                    description="LinkedIn post should be 3000 characters or less",
                    category=ComplianceCategory.PLATFORM_POLICY,
                    severity=ComplianceSeverity.WARNING,
                    platforms=[Platform.LINKEDIN],
                    jurisdictions=[Jurisdiction.GLOBAL],
                    max_length=3000,
                    source="LinkedIn Best Practices"
                )
            ]
        }
        
        return rules
    
    def check_platform_compliance(self, content_data: Dict[str, Any], 
                                 platform: Platform) -> List[ComplianceViolation]:
        """Check compliance for specific platform"""
        violations = []
        
        if platform not in self.platform_rules:
            return violations
        
        rules = self.platform_rules[platform]
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            # Check length constraints
            if rule.max_length:
                violations.extend(self._check_length_constraint(content_data, rule))
            
            # Check prohibited keywords
            if rule.keywords:
                violations.extend(self._check_prohibited_keywords(content_data, rule))
            
            # Check patterns
            if rule.patterns:
                violations.extend(self._check_patterns(content_data, rule))
        
        return violations
    
    def _check_length_constraint(self, content_data: Dict[str, Any], 
                               rule: ComplianceRule) -> List[ComplianceViolation]:
        """
Check length constraints"""
        violations = []
        
        # Determine which field to check based on rule
        field_mapping = {
            'title': ['title', 'name'],
            'description': ['description', 'caption', 'content'],
            'caption': ['caption', 'description']
        }
        
        target_field = None
        content_to_check = ""
        
        # Find the relevant field
        for field_type, possible_fields in field_mapping.items():
            if field_type in rule.id.lower():
                for field in possible_fields:
                    if field in content_data and content_data[field]:
                        target_field = field
                        content_to_check = str(content_data[field])
                        break
                break
        
        # If no specific field mapping, check main content
        if not target_field and 'content' in content_data:
            target_field = 'content'
            content_to_check = str(content_data['content'])
        
        # Check length
        if content_to_check and len(content_to_check) > rule.max_length:
            violations.append(ComplianceViolation(
                rule_id=rule.id,
                rule_name=rule.name,
                category=rule.category,
                severity=rule.severity,
                message=f"{rule.name}: {len(content_to_check)} characters exceeds limit of {rule.max_length}",
                field=target_field,
                detected_content=content_to_check[:100] + "..." if len(content_to_check) > 100 else content_to_check,
                platforms_affected=rule.platforms,
                jurisdictions_affected=rule.jurisdictions,
                suggestions=[f"Reduce {target_field} length to {rule.max_length} characters or less"]
            ))
        
        return violations
    
    def _check_prohibited_keywords(self, content_data: Dict[str, Any],
                                  rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check for prohibited keywords"""
        violations = []
        
        # Check all text fields
        text_fields = ['title', 'description', 'content', 'caption', 'tags']
        
        for field in text_fields:
            if field in content_data and content_data[field]:
                content = str(content_data[field]).lower()
                
                for keyword in rule.keywords:
                    if keyword.lower() in content:
                        position = content.find(keyword.lower())
                        violations.append(ComplianceViolation(
                            rule_id=rule.id,
                            rule_name=rule.name,
                            category=rule.category,
                            severity=rule.severity,
                            message=f"Prohibited content detected: '{keyword}'",
                            field=field,
                            detected_content=keyword,
                            position=position,
                            platforms_affected=rule.platforms,
                            jurisdictions_affected=rule.jurisdictions,
                            suggestions=[f"Remove or replace '{keyword}' to comply with platform guidelines"],
                            confidence=0.8  # Keyword matching has some uncertainty
                        ))
        
        return violations
    
    def _check_patterns(self, content_data: Dict[str, Any],
                       rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check regex patterns"""
        violations = []
        
        # Special handling for hashtag counting
        if "hashtag" in rule.id.lower():
            return self._check_hashtag_limit(content_data, rule)
        
        # General pattern checking
        text_fields = ['title', 'description', 'content', 'caption']
        
        for field in text_fields:
            if field in content_data and content_data[field]:
                content = str(content_data[field])
                
                for pattern in rule.patterns:
                    try:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            violations.append(ComplianceViolation(
                                rule_id=rule.id,
                                rule_name=rule.name,
                                category=rule.category,
                                severity=rule.severity,
                                message=f"Pattern violation detected: {len(matches)} instances found",
                                field=field,
                                detected_content=str(matches[:3]),  # Show first 3 matches
                                platforms_affected=rule.platforms,
                                jurisdictions_affected=rule.jurisdictions,
                                suggestions=["Review and modify content to comply with platform guidelines"]
                            ))
                    except re.error as e:
                        logger.error(f"Invalid regex pattern in rule {rule.id}: {e}")
        
        return violations
    
    def _check_hashtag_limit(self, content_data: Dict[str, Any],
                           rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check hashtag limits for social media platforms"""
        violations = []
        
        text_fields = ['description', 'content', 'caption', 'tags']
        
        for field in text_fields:
            if field in content_data and content_data[field]:
                content = str(content_data[field])
                hashtags = re.findall(r'#\w+', content)
                
                # Instagram has a 30 hashtag limit
                if len(hashtags) > 30:
                    violations.append(ComplianceViolation(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        message=f"Too many hashtags: {len(hashtags)} found (limit: 30)",
                        field=field,
                        detected_content=f"{len(hashtags)} hashtags",
                        platforms_affected=rule.platforms,
                        jurisdictions_affected=rule.jurisdictions,
                        suggestions=["Reduce number of hashtags to 30 or fewer"]
                    ))
        
        return violations


class LegalComplianceChecker:
    """Legal and regulatory compliance checker"""
    
    def __init__(self):
        self.legal_rules = self._initialize_legal_rules()
    
    def _initialize_legal_rules(self) -> List[ComplianceRule]:
        """
Initialize legal compliance rules"""
        return [
            ComplianceRule(
                id="gdpr_data_collection",
                name="GDPR Data Collection Notice",
                description="Content must include appropriate data collection notices",
                category=ComplianceCategory.DATA_PRIVACY,
                severity=ComplianceSeverity.VIOLATION,
                platforms=[Platform.GENERIC],
                jurisdictions=[Jurisdiction.EU, Jurisdiction.DE],
                keywords=["collect data", "personal information", "cookies"],
                source="GDPR Article 13"
            ),
            ComplianceRule(
                id="coppa_child_protection",
                name="COPPA Child Protection",
                description="Content must comply with child protection regulations",
                category=ComplianceCategory.USER_PROTECTION,
                severity=ComplianceSeverity.CRITICAL,
                platforms=[Platform.GENERIC],
                jurisdictions=[Jurisdiction.US],
                keywords=["children", "kids", "under 13"],
                source="COPPA"
            ),
            ComplianceRule(
                id="accessibility_compliance",
                name="Accessibility Compliance",
                description="Content should be accessible to users with disabilities",
                category=ComplianceCategory.ACCESSIBILITY,
                severity=ComplianceSeverity.WARNING,
                platforms=[Platform.GENERIC],
                jurisdictions=[Jurisdiction.GLOBAL],
                required_fields=["alt_text", "captions"],
                source="WCAG 2.1"
            ),
            ComplianceRule(
                id="copyright_attribution",
                name="Copyright Attribution",
                description="Proper attribution required for copyrighted content",
                category=ComplianceCategory.COPYRIGHT,
                severity=ComplianceSeverity.CRITICAL,
                platforms=[Platform.GENERIC],
                jurisdictions=[Jurisdiction.GLOBAL],
                keywords=["copyright", "(c)", "all rights reserved"],
                source="Copyright Law"
            )
        ]
    
    def check_legal_compliance(self, content_data: Dict[str, Any],
                             jurisdiction: Jurisdiction) -> List[ComplianceViolation]:
        """Check legal compliance for specific jurisdiction"""
        violations = []
        
        for rule in self.legal_rules:
            if not rule.enabled or not rule.applies_to_jurisdiction(jurisdiction):
                continue
            
            # Check required fields
            if rule.required_fields:
                violations.extend(self._check_required_fields(content_data, rule))
            
            # Check keywords for compliance indicators
            if rule.keywords:
                violations.extend(self._check_compliance_keywords(content_data, rule))
        
        return violations
    
    def _check_required_fields(self, content_data: Dict[str, Any],
                              rule: ComplianceRule) -> List[ComplianceViolation]:
        """
Check for required compliance fields"""
        violations = []
        
        for required_field in rule.required_fields:
            if required_field not in content_data or not content_data[required_field]:
                violations.append(ComplianceViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    message=f"Missing required field for compliance: {required_field}",
                    field=required_field,
                    platforms_affected=[Platform.GENERIC],
                    jurisdictions_affected=rule.jurisdictions,
                    suggestions=[f"Add {required_field} to ensure compliance with {rule.source}"],
                    required_action=f"Add {required_field}"
                ))
        
        return violations
    
    def _check_compliance_keywords(self, content_data: Dict[str, Any],
                                  rule: ComplianceRule) -> List[ComplianceViolation]:
        """Check for compliance-related keywords"""
        violations = []
        
        # For certain rules, missing keywords indicate compliance issues
        text_fields = ['title', 'description', 'content', 'caption']
        found_keywords = []
        
        for field in text_fields:
            if field in content_data and content_data[field]:
                content = str(content_data[field]).lower()
                
                for keyword in rule.keywords:
                    if keyword.lower() in content:
                        found_keywords.append(keyword)
        
        # Rules that require presence of compliance indicators
        if rule.id in ["gdpr_data_collection"] and not found_keywords:
            # If collecting data but no GDPR notice
            data_collection_indicators = ["email", "subscribe", "newsletter", "contact"]
            has_data_collection = any(
                indicator in str(content_data.get('content', '')).lower()
                for indicator in data_collection_indicators
            )
            
            if has_data_collection:
                violations.append(ComplianceViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    message="Data collection detected but no GDPR compliance notice found",
                    platforms_affected=[Platform.GENERIC],
                    jurisdictions_affected=rule.jurisdictions,
                    suggestions=["Add GDPR-compliant data collection notice"],
                    required_action="Add GDPR notice"
                ))
        
        return violations


class ComplianceChecker:
    """Enterprise compliance checking system"""
    
    def __init__(self):
        self.platform_checker = PlatformPolicyChecker()
        self.legal_checker = LegalComplianceChecker()
    
    def check_compliance(self, content_data: Dict[str, Any],
                        platforms: List[Platform] = None,
                        jurisdictions: List[Jurisdiction] = None,
                        content_id: str = "unknown") -> ComplianceReport:
        """Perform comprehensive compliance check"""
        start_time = datetime.now(timezone.utc)
        
        # Set defaults
        if platforms is None:
            platforms = [Platform.GENERIC]
        if jurisdictions is None:
            jurisdictions = [Jurisdiction.GLOBAL]
        
        # Initialize report
        report = ComplianceReport(
            content_id=content_id,
            overall_compliance_score=0.0,
            is_compliant=True,
            platforms_checked=platforms,
            jurisdictions_checked=jurisdictions
        )
        
        try:
            # Platform compliance checks
            for platform in platforms:
                platform_violations = self.platform_checker.check_platform_compliance(
                    content_data, platform
                )
                
                for violation in platform_violations:
                    report.add_violation(violation)
                
                # Track platform compliance
                report.platform_compliance[platform] = len(platform_violations) == 0
            
            # Legal compliance checks
            for jurisdiction in jurisdictions:
                legal_violations = self.legal_checker.check_legal_compliance(
                    content_data, jurisdiction
                )
                
                for violation in legal_violations:
                    report.add_violation(violation)
                
                # Track jurisdiction compliance
                report.jurisdiction_compliance[jurisdiction] = len(legal_violations) == 0
            
            # Calculate compliance score
            report.overall_compliance_score = self._calculate_compliance_score(report)
            
            # Determine overall compliance
            report.is_compliant = not report.has_blocking_violations()
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report)
            
            # Generate required actions
            report.required_actions = self._generate_required_actions(report)
            
        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            report.add_violation(ComplianceViolation(
                rule_id="system_error",
                rule_name="Compliance System Error",
                category=ComplianceCategory.PLATFORM_POLICY,
                severity=ComplianceSeverity.CRITICAL,
                message=f"Compliance check failed: {str(e)}"
            ))
        
        # Finalize report
        end_time = datetime.now(timezone.utc)
        report.processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return report
    
    def _calculate_compliance_score(self, report: ComplianceReport) -> float:
        """Calculate overall compliance score"""
        base_score = 100.0
        
        # Deduct points for violations
        for violation in report.violations:
            if violation.severity == ComplianceSeverity.CRITICAL:
                base_score -= 25
            elif violation.severity == ComplianceSeverity.VIOLATION:
                base_score -= 15
            elif violation.severity == ComplianceSeverity.WARNING:
                base_score -= 5
            elif violation.severity == ComplianceSeverity.INFO:
                base_score -= 1
        
        return max(0.0, base_score)
    
    def _generate_recommendations(self, report: ComplianceReport) -> List[str]:
        """
Generate compliance recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if report.overall_compliance_score < 50:
            recommendations.append("Compliance score is critically low - immediate action required")
        elif report.overall_compliance_score < 70:
            recommendations.append("Compliance needs improvement - address key violations")
        elif report.overall_compliance_score < 90:
            recommendations.append("Good compliance - optimize remaining issues")
        else:
            recommendations.append("Excellent compliance - maintain current standards")
        
        # Category-specific recommendations
        categories = {}
        for violation in report.violations:
            if violation.category not in categories:
                categories[violation.category] = 0
            categories[violation.category] += 1
        
        for category, count in categories.items():
            if category == ComplianceCategory.PLATFORM_POLICY:
                recommendations.append(f"Review platform policies ({count} violations)")
            elif category == ComplianceCategory.DATA_PRIVACY:
                recommendations.append(f"Improve data privacy compliance ({count} violations)")
            elif category == ComplianceCategory.CONTENT_SAFETY:
                recommendations.append(f"Address content safety concerns ({count} violations)")
        
        # Critical violation recommendations
        critical_violations = report.get_critical_violations()
        if critical_violations:
            recommendations.append("Address all critical violations before publishing")
        
        return recommendations
    
    def _generate_required_actions(self, report: ComplianceReport) -> List[str]:
        """Generate required compliance actions"""
        actions = set()
        
        for violation in report.violations:
            if violation.required_action:
                actions.add(violation.required_action)
            
            # Add suggestions as potential actions
            for suggestion in violation.suggestions:
                if any(keyword in suggestion.lower() for keyword in ['add', 'remove', 'modify', 'update']):
                    actions.add(suggestion)
        
        return list(actions)
    
    def get_platform_requirements(self, platform: Platform) -> Dict[str, Any]:
        """
Get compliance requirements for specific platform"""
        if platform in self.platform_checker.platform_rules:
            rules = self.platform_checker.platform_rules[platform]
            return {
                'platform': platform.value,
                'total_rules': len(rules),
                'rules': [
                    {
                        'id': rule.id,
                        'name': rule.name,
                        'description': rule.description,
                        'category': rule.category.value,
                        'severity': rule.severity.value,
                        'source': rule.source
                    }
                    for rule in rules
                ]
            }
        return {'platform': platform.value, 'total_rules': 0, 'rules': []}
    
    def get_jurisdiction_requirements(self, jurisdiction: Jurisdiction) -> Dict[str, Any]:
        """
Get compliance requirements for specific jurisdiction"""
        applicable_rules = [
            rule for rule in self.legal_checker.legal_rules
            if rule.applies_to_jurisdiction(jurisdiction)
        ]
        
        return {
            'jurisdiction': jurisdiction.value,
            'total_rules': len(applicable_rules),
            'rules': [
                {
                    'id': rule.id,
                    'name': rule.name,
                    'description': rule.description,
                    'category': rule.category.value,
                    'severity': rule.severity.value,
                    'source': rule.source
                }
                for rule in applicable_rules
            ]
        }
    
    def batch_check_compliance(self, content_items: List[Dict[str, Any]],
                              platforms: List[Platform] = None,
                              jurisdictions: List[Jurisdiction] = None) -> List[ComplianceReport]:
        """
Check compliance for multiple content items"""
        reports = []
        
        for i, content_data in enumerate(content_items):
            content_id = content_data.get('id', f'content_{i}')
            report = self.check_compliance(content_data, platforms, jurisdictions, content_id)
            reports.append(report)
        
        return reports
    
    def get_compliance_summary(self, reports: List[ComplianceReport]) -> Dict[str, Any]:
        """
Get summary statistics for multiple compliance reports"""
        if not reports:
            return {}
        
        total_reports = len(reports)
        compliant_reports = sum(1 for r in reports if r.is_compliant)
        avg_score = sum(r.overall_compliance_score for r in reports) / total_reports
        
        # Violation statistics
        total_violations = sum(r.total_violations for r in reports)
        critical_violations = sum(r.critical_violations for r in reports)
        
        # Category breakdown
        category_violations = {}
        for report in reports:
            for violation in report.violations:
                category = violation.category.value
                category_violations[category] = category_violations.get(category, 0) + 1
        
        return {
            'total_reports': total_reports,
            'compliant_reports': compliant_reports,
            'compliance_rate_percent': (compliant_reports / total_reports) * 100,
            'average_compliance_score': avg_score,
            'total_violations': total_violations,
            'critical_violations': critical_violations,
            'violations_by_category': category_violations,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
