"""
AI Agents Compliance System

Advanced compliance management system for AI agents with regulatory framework support.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - AI Content Protection & Collaboration Platform
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited
and will result in legal action. This includes but is not limited to:
- Copying any part of this code
- Using the concept or architecture
- Creating derivative works
- Commercial use without explicit written permission

For licensing inquiries, contact: mlaiel@live.de
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from pydantic import BaseModel, validator
import json
import hashlib
import re
from pathlib import Path
import uuid
from collections import defaultdict, deque

# Configure logging
logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Regulatory frameworks for compliance checking"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    PDPA = "pdpa"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"
    FTC = "ftc"


class ComplianceLevel(IntEnum):
    """Compliance requirement levels"""
    MINIMAL = 1
    BASIC = 2
    STANDARD = 3
    ENHANCED = 4
    MAXIMUM = 5


class ViolationType(Enum):
    """Types of compliance violations"""
    DATA_PRIVACY = "data_privacy"
    CONSENT_MISSING = "consent_missing"
    RETENTION_VIOLATION = "retention_violation"
    ACCESS_UNAUTHORIZED = "access_unauthorized"
    AUDIT_TRAIL_MISSING = "audit_trail_missing"
    ENCRYPTION_VIOLATION = "encryption_violation"
    CROSS_BORDER_TRANSFER = "cross_border_transfer"
    ANONYMIZATION_FAILURE = "anonymization_failure"
    RIGHT_TO_FORGET = "right_to_forget"
    DATA_MINIMIZATION = "data_minimization"


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"


@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    title: str
    description: str
    requirement_level: ComplianceLevel
    automated_check: bool = True
    remediation_steps: List[str] = field(default_factory=list)
    applicable_data_types: Set[str] = field(default_factory=set)
    jurisdiction: Optional[str] = None
    effective_date: Optional[datetime] = None
    version: str = "1.0"
    tags: Set[str] = field(default_factory=set)


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    rule_id: str
    violation_type: ViolationType
    severity: ComplianceLevel
    description: str
    detected_at: datetime
    resource_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    remediation_required: bool = True
    remediation_deadline: Optional[datetime] = None
    status: ComplianceStatus = ComplianceStatus.UNDER_REVIEW
    assigned_to: Optional[str] = None


@dataclass
class RegulatoryFramework:
    """Regulatory framework configuration"""
    framework_id: str
    name: str
    jurisdiction: str
    version: str
    effective_date: datetime
    rules: List[ComplianceRule] = field(default_factory=list)
    mandatory_controls: Set[str] = field(default_factory=set)
    reporting_requirements: Dict[str, Any] = field(default_factory=dict)
    penalties: Dict[str, str] = field(default_factory=dict)


@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""
    assessment_id: str
    framework: ComplianceFramework
    assessed_at: datetime
    overall_status: ComplianceStatus
    compliance_score: float
    total_rules: int
    compliant_rules: int
    violations: List[ComplianceViolation] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_assessment_due: Optional[datetime] = None


class ComplianceChecker:
    """
    Advanced AI agents compliance management system
    
    Provides comprehensive compliance checking, monitoring, and reporting
    for multiple regulatory frameworks with automated violation detection
    and remediation guidance.
    """
    
    def __init__(self, 
                 frameworks: List[ComplianceFramework] = None,
                 jurisdiction: str = "EU",
                 auto_remediation: bool = False):
        """
        Initialize compliance checker
        
        Args:
            frameworks: List of regulatory frameworks to check against
            jurisdiction: Legal jurisdiction for compliance
            auto_remediation: Whether to automatically attempt remediation
        """
        self.frameworks = frameworks or [ComplianceFramework.GDPR]
        self.jurisdiction = jurisdiction
        self.auto_remediation = auto_remediation
        
        # Internal state
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.monitoring_active = False
        
        # Performance tracking
        self.checks_performed = 0
        self.violations_detected = 0
        self.violations_remediated = 0
        
        # Initialize default rules
        self._load_default_rules()
        
        logger.info(f"Compliance checker initialized for frameworks: {[f.value for f in self.frameworks]}")
    
    def _load_default_rules(self):
        """Load default compliance rules for supported frameworks"""
        
        # GDPR Rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="GDPR_001",
                framework=ComplianceFramework.GDPR,
                title="Data Processing Lawful Basis",
                description="All personal data processing must have a lawful basis",
                requirement_level=ComplianceLevel.MAXIMUM,
                remediation_steps=[
                    "Identify lawful basis for processing",
                    "Document basis in privacy policy",
                    "Obtain consent if required"
                ],
                applicable_data_types={"personal_data", "sensitive_data"}
            ),
            ComplianceRule(
                rule_id="GDPR_002",
                framework=ComplianceFramework.GDPR,
                title="Data Subject Consent",
                description="Valid consent must be obtained for data processing",
                requirement_level=ComplianceLevel.MAXIMUM,
                remediation_steps=[
                    "Implement consent collection mechanism",
                    "Provide clear consent options",
                    "Enable consent withdrawal"
                ],
                applicable_data_types={"personal_data"}
            ),
            ComplianceRule(
                rule_id="GDPR_003",
                framework=ComplianceFramework.GDPR,
                title="Right to be Forgotten",
                description="Data subjects can request deletion of their data",
                requirement_level=ComplianceLevel.ENHANCED,
                remediation_steps=[
                    "Implement data deletion mechanism",
                    "Provide deletion request interface",
                    "Verify complete data removal"
                ],
                applicable_data_types={"personal_data", "user_data"}
            )
        ]
        
        # CCPA Rules
        ccpa_rules = [
            ComplianceRule(
                rule_id="CCPA_001",
                framework=ComplianceFramework.CCPA,
                title="Consumer Right to Know",
                description="Consumers have right to know what personal information is collected",
                requirement_level=ComplianceLevel.ENHANCED,
                jurisdiction="California",
                remediation_steps=[
                    "Provide transparent privacy policy",
                    "List all data collection practices",
                    "Enable data access requests"
                ],
                applicable_data_types={"personal_information"}
            )
        ]
        
        # Load all rules
        all_rules = gdpr_rules + ccpa_rules
        for rule in all_rules:
            self.rules[rule.rule_id] = rule
    
    async def check_compliance(self, 
                              resource_id: str,
                              data_context: Dict[str, Any],
                              framework: Optional[ComplianceFramework] = None) -> ComplianceAssessment:
        """
        Perform comprehensive compliance check
        
        Args:
            resource_id: ID of resource being checked
            data_context: Context about the data/resource
            framework: Specific framework to check (or all if None)
            
        Returns:
            ComplianceAssessment with results
        """
        try:
            assessment_id = str(uuid.uuid4())
            target_frameworks = [framework] if framework else self.frameworks
            
            all_violations = []
            total_rules = 0
            compliant_rules = 0
            
            for fw in target_frameworks:
                # Get applicable rules for framework
                fw_rules = [rule for rule in self.rules.values() if rule.framework == fw]
                total_rules += len(fw_rules)
                
                # Check each rule
                for rule in fw_rules:
                    violation = await self._check_rule(rule, resource_id, data_context)
                    if violation:
                        all_violations.append(violation)
                        self.violations[violation.violation_id] = violation
                    else:
                        compliant_rules += 1
            
            # Calculate compliance score
            compliance_score = (compliant_rules / total_rules) * 100 if total_rules > 0 else 100
            
            # Determine overall status
            overall_status = self._determine_overall_status(compliance_score, all_violations)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_violations)
            
            # Create assessment
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                framework=framework or self.frameworks[0],
                assessed_at=datetime.utcnow(),
                overall_status=overall_status,
                compliance_score=compliance_score,
                total_rules=total_rules,
                compliant_rules=compliant_rules,
                violations=all_violations,
                recommendations=recommendations,
                next_assessment_due=datetime.utcnow() + timedelta(days=30)
            )
            
            self.assessments[assessment_id] = assessment
            self.checks_performed += 1
            self.violations_detected += len(all_violations)
            
            logger.info(f"Compliance check completed for {resource_id}: {compliance_score:.1f}% compliant")
            
            # Auto-remediation if enabled
            if self.auto_remediation and all_violations:
                await self._attempt_auto_remediation(all_violations)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error performing compliance check: {e}")
            raise
    
    async def _check_rule(self, 
                         rule: ComplianceRule,
                         resource_id: str, 
                         data_context: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check a specific compliance rule"""
        try:
            # Rule-specific checks
            if rule.rule_id == "GDPR_001":
                return await self._check_lawful_basis(rule, resource_id, data_context)
            elif rule.rule_id == "GDPR_002":
                return await self._check_consent(rule, resource_id, data_context)
            elif rule.rule_id == "GDPR_003":
                return await self._check_deletion_capability(rule, resource_id, data_context)
            elif rule.rule_id == "CCPA_001":
                return await self._check_transparency(rule, resource_id, data_context)
            
            # Generic checks for unknown rules
            return await self._generic_rule_check(rule, resource_id, data_context)
            
        except Exception as e:
            logger.error(f"Error checking rule {rule.rule_id}: {e}")
            return None
    
    async def _check_lawful_basis(self, 
                                 rule: ComplianceRule,
                                 resource_id: str,
                                 data_context: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check GDPR lawful basis requirement"""
        lawful_basis = data_context.get("lawful_basis")
        
        if not lawful_basis or lawful_basis not in [
            "consent", "contract", "legal_obligation", 
            "vital_interests", "public_task", "legitimate_interests"
        ]:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                violation_type=ViolationType.DATA_PRIVACY,
                severity=ComplianceLevel.MAXIMUM,
                description="No valid lawful basis identified for data processing",
                detected_at=datetime.utcnow(),
                resource_id=resource_id,
                context={"missing_basis": True, "data_types": data_context.get("data_types", [])},
                remediation_deadline=datetime.utcnow() + timedelta(days=7)
            )
        
        return None
    
    async def _check_consent(self,
                            rule: ComplianceRule,
                            resource_id: str,
                            data_context: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check GDPR consent requirements"""
        consent_status = data_context.get("consent_status")
        lawful_basis = data_context.get("lawful_basis")
        
        if lawful_basis == "consent" and consent_status != "valid":
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                violation_type=ViolationType.CONSENT_MISSING,
                severity=ComplianceLevel.MAXIMUM,
                description="Valid consent required but not obtained",
                detected_at=datetime.utcnow(),
                resource_id=resource_id,
                context={"consent_status": consent_status},
                remediation_deadline=datetime.utcnow() + timedelta(days=3)
            )
        
        return None
    
    async def _check_deletion_capability(self,
                                        rule: ComplianceRule,
                                        resource_id: str,
                                        data_context: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check right to be forgotten capability"""
        deletion_capability = data_context.get("deletion_capability", False)
        
        if not deletion_capability:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                violation_type=ViolationType.RIGHT_TO_FORGET,
                severity=ComplianceLevel.ENHANCED,
                description="No data deletion capability implemented",
                detected_at=datetime.utcnow(),
                resource_id=resource_id,
                context={"deletion_available": False},
                remediation_deadline=datetime.utcnow() + timedelta(days=14)
            )
        
        return None
    
    async def _check_transparency(self,
                                 rule: ComplianceRule,
                                 resource_id: str,
                                 data_context: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check CCPA transparency requirements"""
        privacy_policy = data_context.get("privacy_policy_available", False)
        data_collection_disclosed = data_context.get("data_collection_disclosed", False)
        
        if not privacy_policy or not data_collection_disclosed:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                violation_type=ViolationType.DATA_PRIVACY,
                severity=ComplianceLevel.ENHANCED,
                description="Insufficient transparency about data collection",
                detected_at=datetime.utcnow(),
                resource_id=resource_id,
                context={
                    "privacy_policy": privacy_policy,
                    "collection_disclosed": data_collection_disclosed
                },
                remediation_deadline=datetime.utcnow() + timedelta(days=10)
            )
        
        return None
    
    async def _generic_rule_check(self,
                                 rule: ComplianceRule,
                                 resource_id: str,
                                 data_context: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Generic compliance rule check"""
        # Simple heuristic-based check
        compliance_indicators = data_context.get("compliance_indicators", {})
        rule_specific_indicator = compliance_indicators.get(rule.rule_id, True)
        
        if not rule_specific_indicator:
            return ComplianceViolation(
                violation_id=str(uuid.uuid4()),
                rule_id=rule.rule_id,
                violation_type=ViolationType.DATA_PRIVACY,
                severity=rule.requirement_level,
                description=f"Generic compliance check failed for rule: {rule.title}",
                detected_at=datetime.utcnow(),
                resource_id=resource_id,
                context={"generic_check": True}
            )
        
        return None
    
    def _determine_overall_status(self, 
                                 compliance_score: float,
                                 violations: List[ComplianceViolation]) -> ComplianceStatus:
        """Determine overall compliance status"""
        if compliance_score == 100:
            return ComplianceStatus.COMPLIANT
        
        critical_violations = [v for v in violations if v.severity >= ComplianceLevel.ENHANCED]
        if critical_violations:
            return ComplianceStatus.CRITICAL if len(critical_violations) > 3 else ComplianceStatus.NON_COMPLIANT
        
        if compliance_score >= 90:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        elif compliance_score >= 70:
            return ComplianceStatus.NEEDS_ATTENTION
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    def _generate_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # Group violations by type
        violation_types = defaultdict(list)
        for violation in violations:
            violation_types[violation.violation_type].append(violation)
        
        # Generate type-specific recommendations
        for violation_type, type_violations in violation_types.items():
            if violation_type == ViolationType.CONSENT_MISSING:
                recommendations.append("Implement comprehensive consent management system")
            elif violation_type == ViolationType.DATA_PRIVACY:
                recommendations.append("Review and update privacy policies and data handling procedures")
            elif violation_type == ViolationType.RIGHT_TO_FORGET:
                recommendations.append("Implement automated data deletion capabilities")
        
        # Priority recommendations for high-severity violations
        high_severity = [v for v in violations if v.severity >= ComplianceLevel.ENHANCED]
        if len(high_severity) > 5:
            recommendations.insert(0, "URGENT: Address high-priority compliance violations immediately")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def _attempt_auto_remediation(self, violations: List[ComplianceViolation]):
        """Attempt automatic remediation of violations"""
        remediated_count = 0
        
        for violation in violations:
            try:
                if await self._remediate_violation(violation):
                    violation.status = ComplianceStatus.COMPLIANT
                    remediated_count += 1
                    logger.info(f"Auto-remediated violation {violation.violation_id}")
                    
            except Exception as e:
                logger.error(f"Failed to remediate violation {violation.violation_id}: {e}")
        
        self.violations_remediated += remediated_count
        logger.info(f"Auto-remediated {remediated_count}/{len(violations)} violations")
    
    async def _remediate_violation(self, violation: ComplianceViolation) -> bool:
        """Attempt to remediate a specific violation"""
        # Placeholder for actual remediation logic
        # In practice, this would implement specific fixes based on violation type
        
        if violation.violation_type == ViolationType.CONSENT_MISSING:
            # Would trigger consent collection flow
            return False  # Cannot auto-remediate consent
        
        elif violation.violation_type == ViolationType.DATA_PRIVACY:
            # Would update privacy settings or policies
            return True  # Can potentially auto-remediate
        
        return False
    
    async def generate_compliance_report(self, 
                                       framework: Optional[ComplianceFramework] = None,
                                       format_type: str = "json") -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            target_frameworks = [framework] if framework else self.frameworks
            
            # Collect assessment data
            relevant_assessments = [
                assessment for assessment in self.assessments.values()
                if assessment.framework in target_frameworks
            ]
            
            # Calculate statistics
            if relevant_assessments:
                avg_compliance_score = sum(a.compliance_score for a in relevant_assessments) / len(relevant_assessments)
                latest_assessment = max(relevant_assessments, key=lambda a: a.assessed_at)
            else:
                avg_compliance_score = 0
                latest_assessment = None
            
            # Collect all violations
            all_violations = []
            for assessment in relevant_assessments:
                all_violations.extend(assessment.violations)
            
            # Group violations by severity and type
            violations_by_severity = defaultdict(int)
            violations_by_type = defaultdict(int)
            
            for violation in all_violations:
                violations_by_severity[violation.severity.name] += 1
                violations_by_type[violation.violation_type.value] += 1
            
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.utcnow().isoformat(),
                "frameworks": [f.value for f in target_frameworks],
                "summary": {
                    "total_assessments": len(relevant_assessments),
                    "average_compliance_score": round(avg_compliance_score, 2),
                    "total_violations": len(all_violations),
                    "checks_performed": self.checks_performed,
                    "violations_remediated": self.violations_remediated
                },
                "latest_assessment": {
                    "assessment_id": latest_assessment.assessment_id if latest_assessment else None,
                    "compliance_score": latest_assessment.compliance_score if latest_assessment else 0,
                    "status": latest_assessment.overall_status.value if latest_assessment else "unknown",
                    "assessed_at": latest_assessment.assessed_at.isoformat() if latest_assessment else None
                } if latest_assessment else None,
                "violations_analysis": {
                    "by_severity": dict(violations_by_severity),
                    "by_type": dict(violations_by_type),
                    "critical_violations": len([v for v in all_violations if v.severity >= ComplianceLevel.ENHANCED]),
                    "overdue_violations": len([v for v in all_violations 
                                             if v.remediation_deadline and v.remediation_deadline < datetime.utcnow()])
                },
                "recommendations": self._generate_report_recommendations(all_violations),
                "next_actions": self._generate_next_actions(all_violations)
            }
            
            logger.info(f"Generated compliance report with {len(all_violations)} violations")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    def _generate_report_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate strategic recommendations for compliance report"""
        recommendations = []
        
        critical_violations = [v for v in violations if v.severity >= ComplianceLevel.ENHANCED]
        overdue_violations = [v for v in violations 
                            if v.remediation_deadline and v.remediation_deadline < datetime.utcnow()]
        
        if overdue_violations:
            recommendations.append(f"URGENT: {len(overdue_violations)} overdue violations require immediate attention")
        
        if critical_violations:
            recommendations.append(f"Address {len(critical_violations)} critical compliance violations")
        
        # Framework-specific recommendations
        gdpr_violations = [v for v in violations if any(r.framework == ComplianceFramework.GDPR 
                                                       for r in self.rules.values() 
                                                       if r.rule_id == v.rule_id)]
        if gdpr_violations:
            recommendations.append("Review GDPR compliance procedures and data handling practices")
        
        return recommendations
    
    def _generate_next_actions(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate specific next actions"""
        actions = []
        
        # Prioritize by deadline and severity
        urgent_violations = sorted(
            [v for v in violations if v.remediation_deadline],
            key=lambda v: (v.remediation_deadline, -v.severity.value)
        )[:5]
        
        for violation in urgent_violations:
            rule = self.rules.get(violation.rule_id)
            if rule and rule.remediation_steps:
                actions.append(f"For {violation.violation_id}: {rule.remediation_steps[0]}")
        
        if len(violations) > 10:
            actions.append("Consider implementing automated compliance monitoring")
        
        return actions
    
    def get_compliance_metrics(self) -> Dict[str, Any]:
        """Get current compliance system metrics"""
        return {
            "checks_performed": self.checks_performed,
            "violations_detected": self.violations_detected,
            "violations_remediated": self.violations_remediated,
            "active_violations": len([v for v in self.violations.values() 
                                    if v.status != ComplianceStatus.COMPLIANT]),
            "frameworks_monitored": len(self.frameworks),
            "rules_loaded": len(self.rules),
            "assessments_completed": len(self.assessments),
            "auto_remediation_enabled": self.auto_remediation,
            "remediation_rate": (self.violations_remediated / max(self.violations_detected, 1)) * 100
        }


# Module initialization
logger.info("AI agents compliance system module loaded successfully")


# Export main classes
__all__ = [
    'ComplianceChecker',
    'ComplianceRule', 
    'ComplianceViolation',
    'RegulatoryFramework',
    'ComplianceAssessment',
    'ComplianceFramework',
    'ComplianceLevel',
    'ComplianceStatus',
    'ViolationType'
]
