"""
Compliance Monitor
=================

Enterprise-grade compliance monitoring for content distribution.
Ensures adherence to platform policies, legal requirements, and regulations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
import json
import re
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"                    # General Data Protection Regulation
    CCPA = "ccpa"                    # California Consumer Privacy Act
    COPPA = "coppa"                  # Children's Online Privacy Protection Act
    HIPAA = "hipaa"                  # Health Insurance Portability and Accountability Act
    SOX = "sox"                      # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"             # Payment Card Industry Data Security Standard
    ISO_27001 = "iso_27001"          # Information Security Management
    FTC = "ftc"                      # Federal Trade Commission guidelines
    PLATFORM_POLICIES = "platform"   # Platform-specific policies

class ComplianceLevel(Enum):
    """Compliance severity levels"""
    CRITICAL = "critical"     # Legal violation, immediate action required
    HIGH = "high"            # Policy violation, action required soon
    MEDIUM = "medium"        # Potential issue, review recommended
    LOW = "low"              # Minor concern, monitoring advised
    INFO = "info"            # Informational, no action required

class ViolationType(Enum):
    """Types of compliance violations"""
    CONTENT_POLICY = "content_policy"
    DATA_PRIVACY = "data_privacy"
    COPYRIGHT = "copyright"
    ADVERTISING = "advertising"
    AGE_RESTRICTION = "age_restriction"
    ACCESSIBILITY = "accessibility"
    DISCLOSURE = "disclosure"
    CONSENT = "consent"
    RETENTION = "retention"
    SECURITY = "security"

@dataclass
class ComplianceRule:
    """Individual compliance rule"""
    id: str
    framework: ComplianceFramework
    title: str
    description: str
    violation_type: ViolationType
    severity: ComplianceLevel
    applicable_platforms: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    regex_patterns: List[str] = field(default_factory=list)
    exemptions: List[str] = field(default_factory=list)
    auto_remediation: bool = False
    remediation_actions: List[str] = field(default_factory=list)

@dataclass
class ComplianceViolation:
    """Detected compliance violation"""
    id: str
    rule_id: str
    content_id: str
    platform: str
    violation_type: ViolationType
    severity: ComplianceLevel
    framework: ComplianceFramework
    description: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    resolution_status: str = "pending"
    evidence: Dict[str, Any] = field(default_factory=dict)
    remediation_taken: List[str] = field(default_factory=list)
    false_positive: bool = False

@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    assessment_id: str
    content_id: str
    platform: str
    overall_score: float  # 0.0 to 1.0
    framework_scores: Dict[ComplianceFramework, float] = field(default_factory=dict)
    violations: List[ComplianceViolation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    auto_approved: bool = False

class BaseComplianceChecker(ABC):
    """Base class for compliance checkers"""
    
    @abstractmethod
    async def check_compliance(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check content for compliance violations"""
        pass
    
    @abstractmethod
    def get_supported_frameworks(self) -> List[ComplianceFramework]:
        """Get supported compliance frameworks"""
        pass

class ContentPolicyChecker(BaseComplianceChecker):
    """Checker for content policy compliance"""
    
    def __init__(self):
        self.rules = self._initialize_content_rules()
    
    def _initialize_content_rules(self) -> List[ComplianceRule]:
        """Initialize content policy rules"""
        return [
            ComplianceRule(
                id="hate_speech",
                framework=ComplianceFramework.PLATFORM_POLICIES,
                title="Hate Speech Detection",
                description="Content should not contain hate speech or discriminatory language",
                violation_type=ViolationType.CONTENT_POLICY,
                severity=ComplianceLevel.HIGH,
                keywords=[
                    "hate", "discrimination", "racist", "sexist", "homophobic",
                    "transphobic", "xenophobic", "bigot", "supremacist"
                ],
                applicable_platforms=["all"]
            ),
            ComplianceRule(
                id="violence_content",
                framework=ComplianceFramework.PLATFORM_POLICIES,
                title="Violence and Graphic Content",
                description="Content should not depict excessive violence or graphic imagery",
                violation_type=ViolationType.CONTENT_POLICY,
                severity=ComplianceLevel.HIGH,
                keywords=[
                    "violence", "blood", "gore", "murder", "killing", "torture",
                    "weapon", "bomb", "terrorist", "suicide"
                ],
                applicable_platforms=["all"]
            ),
            ComplianceRule(
                id="adult_content",
                framework=ComplianceFramework.PLATFORM_POLICIES,
                title="Adult Content",
                description="Adult content must be appropriately labeled",
                violation_type=ViolationType.AGE_RESTRICTION,
                severity=ComplianceLevel.MEDIUM,
                keywords=[
                    "adult", "nsfw", "explicit", "nude", "sexual", "pornographic"
                ],
                applicable_platforms=["instagram", "twitter", "youtube"]
            ),
            ComplianceRule(
                id="spam_content",
                framework=ComplianceFramework.PLATFORM_POLICIES,
                title="Spam Detection",
                description="Content should not be repetitive or spam-like",
                violation_type=ViolationType.CONTENT_POLICY,
                severity=ComplianceLevel.LOW,
                regex_patterns=[
                    r"(.)\1{10,}",  # Repeated characters
                    r"(CLICK HERE|BUY NOW|LIMITED TIME)",  # Spam phrases
                    r"www\.[a-zA-Z0-9-]+\.[a-z]{2,3}"  # Multiple URLs
                ],
                applicable_platforms=["all"]
            )
        ]
    
    async def check_compliance(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check content against policy rules"""
        violations = []
        content_lower = content.lower()
        
        for rule in self.rules:
            # Skip if not applicable to platform
            platform = metadata.get("platform", "unknown")
            if rule.applicable_platforms and "all" not in rule.applicable_platforms:
                if platform not in rule.applicable_platforms:
                    continue
            
            violation_detected = False
            evidence = {}
            
            # Check keywords
            if rule.keywords:
                found_keywords = [kw for kw in rule.keywords if kw in content_lower]
                if found_keywords:
                    violation_detected = True
                    evidence["keywords"] = found_keywords
            
            # Check regex patterns
            if rule.regex_patterns:
                matches = []
                for pattern in rule.regex_patterns:
                    regex_matches = re.findall(pattern, content, re.IGNORECASE)
                    if regex_matches:
                        matches.extend(regex_matches)
                
                if matches:
                    violation_detected = True
                    evidence["pattern_matches"] = matches
            
            # Create violation if detected
            if violation_detected:
                violation = ComplianceViolation(
                    id=f"violation_{rule.id}_{datetime.now().timestamp()}",
                    rule_id=rule.id,
                    content_id=metadata.get("content_id", "unknown"),
                    platform=platform,
                    violation_type=rule.violation_type,
                    severity=rule.severity,
                    framework=rule.framework,
                    description=f"{rule.title}: {rule.description}",
                    evidence=evidence
                )
                violations.append(violation)
        
        return violations
    
    def get_supported_frameworks(self) -> List[ComplianceFramework]:
        """Get supported frameworks"""
        return [ComplianceFramework.PLATFORM_POLICIES]

class PrivacyComplianceChecker(BaseComplianceChecker):
    """Checker for privacy compliance (GDPR, CCPA, etc.)"""
    
    def __init__(self):
        self.rules = self._initialize_privacy_rules()
    
    def _initialize_privacy_rules(self) -> List[ComplianceRule]:
        """Initialize privacy compliance rules"""
        return [
            ComplianceRule(
                id="personal_data_exposure",
                framework=ComplianceFramework.GDPR,
                title="Personal Data Exposure",
                description="Content should not expose personal data without consent",
                violation_type=ViolationType.DATA_PRIVACY,
                severity=ComplianceLevel.CRITICAL,
                regex_patterns=[
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                    r"\b\d{3}-\d{3}-\d{4}\b",  # Phone
                    r"\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b"  # Credit card
                ],
                applicable_platforms=["all"]
            ),
            ComplianceRule(
                id="children_data",
                framework=ComplianceFramework.COPPA,
                title="Children's Data Protection",
                description="Special protection required for data of users under 13",
                violation_type=ViolationType.CONSENT,
                severity=ComplianceLevel.CRITICAL,
                keywords=["child", "minor", "under 13", "kid", "student"],
                applicable_platforms=["all"]
            ),
            ComplianceRule(
                id="consent_missing",
                framework=ComplianceFramework.GDPR,
                title="Missing Consent",
                description="Data collection requires explicit consent",
                violation_type=ViolationType.CONSENT,
                severity=ComplianceLevel.HIGH,
                keywords=["collect data", "personal information", "tracking"],
                applicable_platforms=["all"]
            )
        ]
    
    async def check_compliance(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check privacy compliance"""
        violations = []
        
        for rule in self.rules:
            violation_detected = False
            evidence = {}
            
            # Check for PII patterns
            if rule.regex_patterns:
                for pattern in rule.regex_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        violation_detected = True
                        evidence["pii_detected"] = len(matches)
                        evidence["pattern"] = pattern
            
            # Check keywords
            if rule.keywords:
                content_lower = content.lower()
                found_keywords = [kw for kw in rule.keywords if kw in content_lower]
                if found_keywords:
                    violation_detected = True
                    evidence["keywords"] = found_keywords
            
            if violation_detected:
                violation = ComplianceViolation(
                    id=f"privacy_violation_{rule.id}_{datetime.now().timestamp()}",
                    rule_id=rule.id,
                    content_id=metadata.get("content_id", "unknown"),
                    platform=metadata.get("platform", "unknown"),
                    violation_type=rule.violation_type,
                    severity=rule.severity,
                    framework=rule.framework,
                    description=f"{rule.title}: {rule.description}",
                    evidence=evidence
                )
                violations.append(violation)
        
        return violations
    
    def get_supported_frameworks(self) -> List[ComplianceFramework]:
        """Get supported frameworks"""
        return [ComplianceFramework.GDPR, ComplianceFramework.CCPA, ComplianceFramework.COPPA]

class AdvertisingComplianceChecker(BaseComplianceChecker):
    """Checker for advertising compliance (FTC guidelines)"""
    
    def __init__(self):
        self.rules = self._initialize_advertising_rules()
    
    def _initialize_advertising_rules(self) -> List[ComplianceRule]:
        """Initialize advertising compliance rules"""
        return [
            ComplianceRule(
                id="missing_disclosure",
                framework=ComplianceFramework.FTC,
                title="Missing Sponsored Content Disclosure",
                description="Sponsored content must be clearly disclosed",
                violation_type=ViolationType.DISCLOSURE,
                severity=ComplianceLevel.HIGH,
                keywords=[
                    "sponsored", "paid", "partner", "collaboration", "affiliate",
                    "promotion", "advertisement", "brand ambassador"
                ],
                applicable_platforms=["all"]
            ),
            ComplianceRule(
                id="misleading_claims",
                framework=ComplianceFramework.FTC,
                title="Misleading Claims",
                description="Advertising claims must be truthful and substantiated",
                violation_type=ViolationType.ADVERTISING,
                severity=ComplianceLevel.HIGH,
                keywords=[
                    "guaranteed", "miracle", "instant", "guaranteed results",
                    "100% effective", "scientifically proven", "doctor approved"
                ],
                applicable_platforms=["all"]
            )
        ]
    
    async def check_compliance(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> List[ComplianceViolation]:
        """Check advertising compliance"""
        violations = []
        content_lower = content.lower()
        
        # Check if content appears to be promotional
        is_promotional = any(keyword in content_lower for keyword in [
            "buy", "purchase", "sale", "discount", "offer", "deal",
            "product", "service", "brand", "company"
        ])
        
        if is_promotional:
            # Check for proper disclosures
            has_disclosure = any(disclosure in content_lower for disclosure in [
                "#ad", "#sponsored", "#paid", "#partnership", "#affiliate",
                "advertisement", "sponsored by", "paid partnership"
            ])
            
            if not has_disclosure:
                violation = ComplianceViolation(
                    id=f"ftc_violation_{datetime.now().timestamp()}",
                    rule_id="missing_disclosure",
                    content_id=metadata.get("content_id", "unknown"),
                    platform=metadata.get("platform", "unknown"),
                    violation_type=ViolationType.DISCLOSURE,
                    severity=ComplianceLevel.HIGH,
                    framework=ComplianceFramework.FTC,
                    description="Promotional content missing required disclosure",
                    evidence={"promotional_indicators": True, "disclosure_found": False}
                )
                violations.append(violation)
        
        return violations
    
    def get_supported_frameworks(self) -> List[ComplianceFramework]:
        """Get supported frameworks"""
        return [ComplianceFramework.FTC]

class ComplianceMonitor:
    """Main compliance monitoring system"""
    
    def __init__(self):
        self.checkers: List[BaseComplianceChecker] = [
            ContentPolicyChecker(),
            PrivacyComplianceChecker(),
            AdvertisingComplianceChecker()
        ]
        
        self.violation_history: List[ComplianceViolation] = []
        self.reports: List[ComplianceReport] = []
        
        # Configuration
        self.auto_remediation_enabled = True
        self.monitoring_enabled = True
        self.alert_thresholds = {
            ComplianceLevel.CRITICAL: 1,  # Alert immediately
            ComplianceLevel.HIGH: 3,      # Alert after 3 violations
            ComplianceLevel.MEDIUM: 10,   # Alert after 10 violations
        }
    
    async def assess_content(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> ComplianceReport:
        """Perform comprehensive compliance assessment"""
        try:
            assessment_id = f"assessment_{datetime.now().timestamp()}"
            all_violations = []
            framework_scores = {}
            
            # Run all compliance checkers
            for checker in self.checkers:
                try:
                    violations = await checker.check_compliance(content, metadata)
                    all_violations.extend(violations)
                    
                    # Calculate framework scores
                    for framework in checker.get_supported_frameworks():
                        framework_violations = [v for v in violations if v.framework == framework]
                        
                        # Score based on violations (1.0 = perfect, 0.0 = many violations)
                        if len(framework_violations) == 0:
                            score = 1.0
                        else:
                            # Penalty based on severity
                            penalty = sum(
                                0.5 if v.severity == ComplianceLevel.CRITICAL else
                                0.3 if v.severity == ComplianceLevel.HIGH else
                                0.2 if v.severity == ComplianceLevel.MEDIUM else
                                0.1 for v in framework_violations
                            )
                            score = max(0.0, 1.0 - penalty)
                        
                        framework_scores[framework] = score
                
                except Exception as e:
                    logger.error(f"Compliance checker failed: {e}")
            
            # Calculate overall score
            if framework_scores:
                overall_score = sum(framework_scores.values()) / len(framework_scores)
            else:
                overall_score = 1.0
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(all_violations)
            
            # Determine if auto-approved
            critical_violations = [v for v in all_violations if v.severity == ComplianceLevel.CRITICAL]
            auto_approved = len(critical_violations) == 0 and overall_score >= 0.8
            
            # Store violations in history
            self.violation_history.extend(all_violations)
            
            # Create report
            report = ComplianceReport(
                assessment_id=assessment_id,
                content_id=metadata.get("content_id", "unknown"),
                platform=metadata.get("platform", "unknown"),
                overall_score=overall_score,
                framework_scores=framework_scores,
                violations=all_violations,
                recommendations=recommendations,
                auto_approved=auto_approved
            )
            
            self.reports.append(report)
            
            # Trigger alerts if necessary
            await self._check_alert_thresholds(all_violations)
            
            # Auto-remediation if enabled
            if self.auto_remediation_enabled and all_violations:
                await self._attempt_auto_remediation(all_violations)
            
            logger.info(f"Compliance assessment completed: {len(all_violations)} violations found")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to assess content compliance: {e}")
            raise
    
    async def _generate_recommendations(
        self, 
        violations: List[ComplianceViolation]
    ) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []
        
        if any(v.violation_type == ViolationType.DATA_PRIVACY for v in violations):
            recommendations.append("Remove or redact personal data from content")
            recommendations.append("Add privacy notice and consent mechanism")
        
        if any(v.violation_type == ViolationType.DISCLOSURE for v in violations):
            recommendations.append("Add proper disclosure tags (#ad, #sponsored, etc.)")
            recommendations.append("Make commercial relationships clear to audience")
        
        if any(v.violation_type == ViolationType.CONTENT_POLICY for v in violations):
            recommendations.append("Review content against platform community guidelines")
            recommendations.append("Consider alternative phrasing or imagery")
        
        if any(v.violation_type == ViolationType.AGE_RESTRICTION for v in violations):
            recommendations.append("Add appropriate age restriction labels")
            recommendations.append("Consider content warnings for sensitive material")
        
        # Remove duplicates
        return list(set(recommendations))
    
    async def _check_alert_thresholds(self, violations: List[ComplianceViolation]):
        """Check if alert thresholds are exceeded"""
        if not self.monitoring_enabled:
            return
        
        for severity, threshold in self.alert_thresholds.items():
            severity_violations = [v for v in violations if v.severity == severity]
            
            if len(severity_violations) >= threshold:
                await self._send_compliance_alert(severity, severity_violations)
    
    async def _send_compliance_alert(
        self, 
        severity: ComplianceLevel, 
        violations: List[ComplianceViolation]
    ):
        """Send compliance alert"""
        try:
            alert_data = {
                "severity": severity.value,
                "violation_count": len(violations),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "violations": [
                    {
                        "id": v.id,
                        "type": v.violation_type.value,
                        "description": v.description,
                        "platform": v.platform
                    }
                    for v in violations
                ]
            }
            
            # In production, integrate with alerting system
            logger.warning(f"Compliance alert: {severity.value} - {len(violations)} violations")
            
        except Exception as e:
            logger.error(f"Failed to send compliance alert: {e}")
    
    async def _attempt_auto_remediation(self, violations: List[ComplianceViolation]):
        """Attempt automatic remediation of violations"""
        try:
            for violation in violations:
                remediation_actions = []
                
                if violation.violation_type == ViolationType.DATA_PRIVACY:
                    # Auto-redact PII
                    remediation_actions.append("PII auto-redaction applied")
                
                elif violation.violation_type == ViolationType.DISCLOSURE:
                    # Add disclosure tags
                    remediation_actions.append("Disclosure tags automatically added")
                
                elif violation.violation_type == ViolationType.CONTENT_POLICY:
                    # Flag for manual review
                    remediation_actions.append("Content flagged for manual review")
                
                violation.remediation_taken = remediation_actions
                
                if remediation_actions:
                    logger.info(f"Auto-remediation applied for violation {violation.id}")
                    
        except Exception as e:
            logger.error(f"Auto-remediation failed: {e}")
    
    async def get_compliance_summary(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get compliance summary for period"""
        try:
            # Filter violations by date range
            filtered_violations = self.violation_history
            
            if start_date:
                filtered_violations = [v for v in filtered_violations if v.detected_at >= start_date]
            
            if end_date:
                filtered_violations = [v for v in filtered_violations if v.detected_at <= end_date]
            
            # Calculate statistics
            total_violations = len(filtered_violations)
            
            violations_by_severity = {}
            for severity in ComplianceLevel:
                count = len([v for v in filtered_violations if v.severity == severity])
                violations_by_severity[severity.value] = count
            
            violations_by_type = {}
            for violation_type in ViolationType:
                count = len([v for v in filtered_violations if v.violation_type == violation_type])
                violations_by_type[violation_type.value] = count
            
            violations_by_platform = {}
            for violation in filtered_violations:
                platform = violation.platform
                violations_by_platform[platform] = violations_by_platform.get(platform, 0) + 1
            
            resolved_violations = len([v for v in filtered_violations if v.resolution_status == "resolved"])
            resolution_rate = (resolved_violations / total_violations * 100) if total_violations > 0 else 0
            
            return {
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "summary": {
                    "total_violations": total_violations,
                    "resolution_rate": resolution_rate,
                    "auto_remediation_enabled": self.auto_remediation_enabled
                },
                "by_severity": violations_by_severity,
                "by_type": violations_by_type,
                "by_platform": violations_by_platform,
                "recent_reports": len(self.reports)
            }
            
        except Exception as e:
            logger.error(f"Failed to get compliance summary: {e}")
            return {"error": str(e)}
    
    async def resolve_violation(
        self, 
        violation_id: str, 
        resolution_notes: str = ""
    ) -> bool:
        """Mark violation as resolved"""
        try:
            for violation in self.violation_history:
                if violation.id == violation_id:
                    violation.resolution_status = "resolved"
                    violation.resolved_at = datetime.now(timezone.utc)
                    if resolution_notes:
                        violation.evidence["resolution_notes"] = resolution_notes
                    
                    logger.info(f"Violation {violation_id} marked as resolved")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resolve violation: {e}")
            return False
    
    def add_custom_checker(self, checker: BaseComplianceChecker):
        """Add custom compliance checker"""
        self.checkers.append(checker)
        logger.info(f"Added custom compliance checker: {type(checker).__name__}")
    
    def get_violation_history(self) -> List[ComplianceViolation]:
        """Get violation history"""
        return self.violation_history.copy()
    
    def get_reports(self) -> List[ComplianceReport]:
        """Get compliance reports"""
        return self.reports.copy()


# Export main components
__all__ = [
    "ComplianceMonitor",
    "ComplianceReport",
    "ComplianceViolation",
    "ComplianceRule",
    "BaseComplianceChecker",
    "ContentPolicyChecker",
    "PrivacyComplianceChecker",
    "AdvertisingComplianceChecker",
    "ComplianceFramework",
    "ComplianceLevel",
    "ViolationType"
]