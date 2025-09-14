"""Compliance Management - IA Influencer Agent Platform
===================================================

Consolidated compliance management for regulatory requirements, legal compliance,
data protection, content policies, and industry standards.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import re

logger = logging.getLogger(__name__)


class ComplianceType(Enum):
    """Types of compliance requirements."""
    DATA_PROTECTION = "data_protection"
    COPYRIGHT = "copyright"
    CONTENT_POLICY = "content_policy"
    FINANCIAL_REGULATION = "financial_regulation"
    PRIVACY_LAW = "privacy_law"
    INDUSTRY_STANDARD = "industry_standard"
    PLATFORM_POLICY = "platform_policy"
    ACCESSIBILITY = "accessibility"


class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    UNDER_REVIEW = "under_review"
    REQUIRES_ACTION = "requires_action"


class ComplianceSeverity(Enum):
    """Compliance violation severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ComplianceRule:
    """Compliance rule definition."""
    rule_id: str
    name: str
    compliance_type: ComplianceType
    description: str
    requirements: List[str]
    severity: ComplianceSeverity
    is_mandatory: bool = True
    check_frequency: str = "daily"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceViolation:
    """Compliance violation record."""
    violation_id: str
    rule_id: str
    entity_id: str
    entity_type: str
    description: str
    severity: ComplianceSeverity
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    status: str = "open"
    remediation_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceAudit:
    """Compliance audit record."""
    audit_id: str
    audit_type: ComplianceType
    scope: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "in_progress"
    findings: List[ComplianceViolation] = field(default_factory=list)
    score: Optional[float] = None
    recommendations: List[str] = field(default_factory=list)
    auditor: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplianceManager:
    """
    Consolidated compliance management system for the IA Influencer platform.
    
    Manages regulatory compliance, legal requirements, data protection,
    content policies, and industry standards across all platform operations.
    """
    
    def __init__(self) -> None:
        """Initialize the compliance manager."""
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.violations: Dict[str, ComplianceViolation] = {}
        self.audits: Dict[str, ComplianceAudit] = {}
        self.compliance_scores: Dict[ComplianceType, float] = {}
        self.logger = logging.getLogger(__name__)
        self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Load default compliance rules."""
        default_rules = [
            # GDPR/Data Protection Rules
            ComplianceRule(
                rule_id="gdpr_consent",
                name="GDPR Consent Management",
                compliance_type=ComplianceType.DATA_PROTECTION,
                description="Users must provide explicit consent for data processing",
                requirements=[
                    "Explicit consent collection",
                    "Consent withdrawal mechanism",
                    "Consent records maintenance"
                ],
                severity=ComplianceSeverity.CRITICAL
            ),
            ComplianceRule(
                rule_id="data_retention",
                name="Data Retention Policy",
                compliance_type=ComplianceType.DATA_PROTECTION,
                description="Personal data retention limits and deletion",
                requirements=[
                    "Data retention periods defined",
                    "Automatic deletion processes",
                    "Data minimization practices"
                ],
                severity=ComplianceSeverity.HIGH
            ),
            
            # Copyright Rules
            ComplianceRule(
                rule_id="copyright_protection",
                name="Copyright Protection",
                compliance_type=ComplianceType.COPYRIGHT,
                description="Content must not infringe on copyrights",
                requirements=[
                    "Copyright verification",
                    "DMCA compliance",
                    "Content fingerprinting"
                ],
                severity=ComplianceSeverity.CRITICAL
            ),
            
            # Content Policy Rules
            ComplianceRule(
                rule_id="content_moderation",
                name="Content Moderation Policy",
                compliance_type=ComplianceType.CONTENT_POLICY,
                description="Content must comply with platform policies",
                requirements=[
                    "Automated content scanning",
                    "Manual review processes",
                    "Appeal mechanisms"
                ],
                severity=ComplianceSeverity.HIGH
            ),
            
            # Financial Regulation Rules
            ComplianceRule(
                rule_id="payment_compliance",
                name="Payment Processing Compliance",
                compliance_type=ComplianceType.FINANCIAL_REGULATION,
                description="Payment processing must comply with financial regulations",
                requirements=[
                    "PCI DSS compliance",
                    "AML checks",
                    "Transaction monitoring"
                ],
                severity=ComplianceSeverity.CRITICAL
            ),
            
            # Privacy Law Rules
            ComplianceRule(
                rule_id="privacy_by_design",
                name="Privacy by Design",
                compliance_type=ComplianceType.PRIVACY_LAW,
                description="Privacy considerations in system design",
                requirements=[
                    "Data protection impact assessments",
                    "Privacy-preserving technologies",
                    "Default privacy settings"
                ],
                severity=ComplianceSeverity.HIGH
            ),
            
            # Accessibility Rules
            ComplianceRule(
                rule_id="accessibility_standards",
                name="Accessibility Standards",
                compliance_type=ComplianceType.ACCESSIBILITY,
                description="Platform must be accessible to users with disabilities",
                requirements=[
                    "WCAG 2.1 AA compliance",
                    "Screen reader compatibility",
                    "Keyboard navigation support"
                ],
                severity=ComplianceSeverity.MEDIUM
            )
        ]
        
        for rule in default_rules:
            self.add_compliance_rule(rule)
    
    def add_compliance_rule(self, rule: ComplianceRule) -> str:
        """Add a compliance rule."""
        try:
            self.compliance_rules[rule.rule_id] = rule
            self.logger.info(f"Added compliance rule: {rule.name} ({rule.rule_id})")
            return rule.rule_id
        except Exception as e:
            self.logger.error(f"Failed to add compliance rule {rule.rule_id}: {str(e)}")
            raise
    
    async def check_compliance(self, entity_id: str, entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance for a specific entity."""
        try:
            violations = []
            compliance_status = ComplianceStatus.COMPLIANT
            
            for rule in self.compliance_rules.values():
                violation = await self._check_rule_compliance(rule, entity_id, entity_type, entity_data)
                if violation:
                    violations.append(violation)
                    if violation.severity in [ComplianceSeverity.CRITICAL, ComplianceSeverity.HIGH]:
                        compliance_status = ComplianceStatus.NON_COMPLIANT
                    elif compliance_status == ComplianceStatus.COMPLIANT:
                        compliance_status = ComplianceStatus.PARTIAL_COMPLIANCE
            
            # Store violations
            for violation in violations:
                self.violations[violation.violation_id] = violation
            
            return {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "compliance_status": compliance_status.value,
                "violations_count": len(violations),
                "critical_violations": len([v for v in violations if v.severity == ComplianceSeverity.CRITICAL]),
                "violations": [
                    {
                        "violation_id": v.violation_id,
                        "rule_id": v.rule_id,
                        "description": v.description,
                        "severity": v.severity.value
                    } for v in violations
                ],
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking compliance for {entity_id}: {str(e)}")
            return {
                "entity_id": entity_id,
                "compliance_status": "error",
                "error": str(e)
            }
    
    async def _check_rule_compliance(self, rule: ComplianceRule, entity_id: str, entity_type: str, entity_data: Dict[str, Any]) -> Optional[ComplianceViolation]:
        """Check compliance for a specific rule."""
        try:
            violation_description = None
            
            # Rule-specific compliance checks
            if rule.rule_id == "gdpr_consent":
                if not entity_data.get("consent_given", False):
                    violation_description = "GDPR consent not obtained"
                elif not entity_data.get("consent_timestamp"):
                    violation_description = "GDPR consent timestamp missing"
            
            elif rule.rule_id == "data_retention":
                retention_date = entity_data.get("created_at")
                if retention_date:
                    # Check if data is older than 7 years (example retention period)
                    if isinstance(retention_date, str):
                        retention_date = datetime.fromisoformat(retention_date.replace('Z', '+00:00'))
                    elif isinstance(retention_date, datetime):
                        pass
                    else:
                        retention_date = datetime.utcnow()
                    
                    if datetime.utcnow() - retention_date > timedelta(days=2555):  # ~7 years
                        violation_description = "Data exceeds retention period"
            
            elif rule.rule_id == "copyright_protection":
                if entity_type == "content":
                    if not entity_data.get("copyright_verified", False):
                        violation_description = "Copyright verification missing"
                    elif entity_data.get("dmca_claimed", False):
                        violation_description = "DMCA claim against content"
            
            elif rule.rule_id == "content_moderation":
                if entity_type == "content":
                    if not entity_data.get("moderation_status"):
                        violation_description = "Content moderation status missing"
                    elif entity_data.get("moderation_status") == "rejected":
                        violation_description = "Content rejected by moderation"
            
            elif rule.rule_id == "payment_compliance":
                if entity_type == "payment":
                    if not entity_data.get("pci_compliant", False):
                        violation_description = "Payment not PCI compliant"
                    elif entity_data.get("amount", 0) > 10000 and not entity_data.get("aml_checked", False):
                        violation_description = "Large payment without AML check"
            
            elif rule.rule_id == "privacy_by_design":
                if not entity_data.get("privacy_assessment_completed", False):
                    violation_description = "Privacy impact assessment missing"
            
            elif rule.rule_id == "accessibility_standards":
                if entity_type == "content" and entity_data.get("content_type") in ["video", "image"]:
                    if not entity_data.get("alt_text") and not entity_data.get("captions"):
                        violation_description = "Accessibility features missing"
            
            # Create violation if found
            if violation_description:
                violation = ComplianceViolation(
                    violation_id=str(uuid.uuid4()),
                    rule_id=rule.rule_id,
                    entity_id=entity_id,
                    entity_type=entity_type,
                    description=violation_description,
                    severity=rule.severity,
                    metadata={"rule_name": rule.name}
                )
                return violation
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking rule compliance {rule.rule_id}: {str(e)}")
            return None
    
    async def start_compliance_audit(self, audit_type: ComplianceType, scope: str) -> str:
        """Start a compliance audit."""
        try:
            audit = ComplianceAudit(
                audit_id=str(uuid.uuid4()),
                audit_type=audit_type,
                scope=scope
            )
            
            self.audits[audit.audit_id] = audit
            
            # Start audit process asynchronously
            asyncio.create_task(self._run_compliance_audit(audit.audit_id))
            
            self.logger.info(f"Started compliance audit: {audit_type.value} ({audit.audit_id})")
            return audit.audit_id
            
        except Exception as e:
            self.logger.error(f"Error starting compliance audit: {str(e)}")
            raise
    
    async def _run_compliance_audit(self, audit_id: str) -> None:
        """Run a compliance audit."""
        try:
            audit = self.audits[audit_id]
            
            # Get relevant rules for audit type
            relevant_rules = [rule for rule in self.compliance_rules.values() 
                            if rule.compliance_type == audit.audit_type]
            
            # Simulate audit process
            total_checks = len(relevant_rules) * 10  # Assume 10 entities per rule
            compliant_checks = 0
            
            for rule in relevant_rules:
                # Simulate checking multiple entities
                for i in range(10):
                    entity_id = f"entity_{i}"
                    entity_data = self._generate_sample_entity_data(audit.audit_type)
                    
                    violation = await self._check_rule_compliance(rule, entity_id, "audit_entity", entity_data)
                    if violation:
                        audit.findings.append(violation)
                    else:
                        compliant_checks += 1
            
            # Calculate compliance score
            audit.score = (compliant_checks / total_checks) * 100 if total_checks > 0 else 100
            
            # Generate recommendations
            audit.recommendations = self._generate_audit_recommendations(audit)
            
            # Complete audit
            audit.status = "completed"
            audit.completed_at = datetime.utcnow()
            
            self.logger.info(f"Completed compliance audit: {audit_id} (Score: {audit.score:.1f}%)")
            
        except Exception as e:
            audit.status = "failed"
            self.logger.error(f"Error running compliance audit {audit_id}: {str(e)}")
    
    def _generate_sample_entity_data(self, audit_type: ComplianceType) -> Dict[str, Any]:
        """Generate sample entity data for audit testing."""
        import random
        
        base_data = {
            "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 1000)),
            "updated_at": datetime.utcnow()
        }
        
        if audit_type == ComplianceType.DATA_PROTECTION:
            base_data.update({
                "consent_given": random.choice([True, False]),
                "consent_timestamp": datetime.utcnow().isoformat(),
                "privacy_assessment_completed": random.choice([True, False])
            })
        elif audit_type == ComplianceType.COPYRIGHT:
            base_data.update({
                "copyright_verified": random.choice([True, False]),
                "dmca_claimed": random.choice([True, False])
            })
        elif audit_type == ComplianceType.CONTENT_POLICY:
            base_data.update({
                "moderation_status": random.choice(["approved", "rejected", "pending"]),
                "content_type": random.choice(["audio", "video", "image"])
            })
        elif audit_type == ComplianceType.FINANCIAL_REGULATION:
            base_data.update({
                "pci_compliant": random.choice([True, False]),
                "amount": random.randint(10, 15000),
                "aml_checked": random.choice([True, False])
            })
        
        return base_data
    
    def _generate_audit_recommendations(self, audit: ComplianceAudit) -> List[str]:
        """Generate recommendations based on audit findings."""
        recommendations = []
        
        critical_findings = [f for f in audit.findings if f.severity == ComplianceSeverity.CRITICAL]
        high_findings = [f for f in audit.findings if f.severity == ComplianceSeverity.HIGH]
        
        if critical_findings:
            recommendations.append(f"Immediately address {len(critical_findings)} critical compliance violations")
        
        if high_findings:
            recommendations.append(f"Prioritize resolution of {len(high_findings)} high-severity violations")
        
        if audit.score < 90:
            recommendations.append("Implement additional compliance monitoring and controls")
        
        if audit.score < 70:
            recommendations.append("Consider comprehensive compliance program review")
        
        # Type-specific recommendations
        if audit.audit_type == ComplianceType.DATA_PROTECTION:
            recommendations.append("Enhance data protection training for staff")
            recommendations.append("Review and update privacy policies")
        elif audit.audit_type == ComplianceType.COPYRIGHT:
            recommendations.append("Strengthen copyright verification processes")
            recommendations.append("Implement automated copyright detection")
        
        return recommendations
    
    async def resolve_violation(self, violation_id: str, resolution_notes: str) -> bool:
        """Resolve a compliance violation."""
        try:
            if violation_id not in self.violations:
                return False
            
            violation = self.violations[violation_id]
            violation.status = "resolved"
            violation.resolved_at = datetime.utcnow()
            violation.metadata["resolution_notes"] = resolution_notes
            
            self.logger.info(f"Resolved compliance violation: {violation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resolving violation {violation_id}: {str(e)}")
            return False
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive compliance dashboard."""
        try:
            # Calculate overall compliance scores
            for compliance_type in ComplianceType:
                relevant_violations = [v for v in self.violations.values() 
                                     if self.compliance_rules.get(v.rule_id, {}).compliance_type == compliance_type]
                relevant_rules = [r for r in self.compliance_rules.values() if r.compliance_type == compliance_type]
                
                if relevant_rules:
                    # Simple scoring: 100% - (violations * penalty)
                    penalty_per_violation = {
                        ComplianceSeverity.CRITICAL: 25,
                        ComplianceSeverity.HIGH: 15,
                        ComplianceSeverity.MEDIUM: 10,
                        ComplianceSeverity.LOW: 5
                    }
                    
                    total_penalty = sum(penalty_per_violation.get(v.severity, 5) for v in relevant_violations)
                    score = max(0, 100 - total_penalty)
                    self.compliance_scores[compliance_type] = score
            
            overall_score = sum(self.compliance_scores.values()) / len(self.compliance_scores) if self.compliance_scores else 100
            
            open_violations = [v for v in self.violations.values() if v.status == "open"]
            critical_violations = [v for v in open_violations if v.severity == ComplianceSeverity.CRITICAL]
            
            return {
                "overall_compliance_score": round(overall_score, 1),
                "compliance_status": "compliant" if overall_score >= 90 else "non_compliant" if overall_score < 70 else "partial_compliance",
                "total_violations": len(self.violations),
                "open_violations": len(open_violations),
                "critical_violations": len(critical_violations),
                "resolved_violations": len([v for v in self.violations.values() if v.status == "resolved"]),
                "compliance_scores_by_type": {ct.value: self.compliance_scores.get(ct, 100) for ct in ComplianceType},
                "recent_audits": len([a for a in self.audits.values() if a.started_at >= datetime.utcnow() - timedelta(days=30)]),
                "total_rules": len(self.compliance_rules),
                "mandatory_rules": len([r for r in self.compliance_rules.values() if r.is_mandatory]),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting compliance dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def generate_compliance_report(self, compliance_type: Optional[ComplianceType] = None) -> Dict[str, Any]:
        """Generate a comprehensive compliance report."""
        try:
            if compliance_type:
                violations = [v for v in self.violations.values() 
                            if self.compliance_rules.get(v.rule_id, {}).compliance_type == compliance_type]
                rules = [r for r in self.compliance_rules.values() if r.compliance_type == compliance_type]
                audits = [a for a in self.audits.values() if a.audit_type == compliance_type]
            else:
                violations = list(self.violations.values())
                rules = list(self.compliance_rules.values())
                audits = list(self.audits.values())
            
            return {
                "report_type": f"{compliance_type.value if compliance_type else 'overall'}_compliance_report",
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_rules": len(rules),
                    "total_violations": len(violations),
                    "open_violations": len([v for v in violations if v.status == "open"]),
                    "resolved_violations": len([v for v in violations if v.status == "resolved"]),
                    "critical_violations": len([v for v in violations if v.severity == ComplianceSeverity.CRITICAL]),
                    "completed_audits": len([a for a in audits if a.status == "completed"])
                },
                "violations_by_severity": {
                    severity.value: len([v for v in violations if v.severity == severity])
                    for severity in ComplianceSeverity
                },
                "recent_violations": [
                    {
                        "violation_id": v.violation_id,
                        "rule_id": v.rule_id,
                        "description": v.description,
                        "severity": v.severity.value,
                        "detected_at": v.detected_at.isoformat(),
                        "status": v.status
                    } for v in sorted(violations, key=lambda x: x.detected_at, reverse=True)[:10]
                ],
                "audit_summary": [
                    {
                        "audit_id": a.audit_id,
                        "audit_type": a.audit_type.value,
                        "score": a.score,
                        "status": a.status,
                        "findings_count": len(a.findings)
                    } for a in sorted(audits, key=lambda x: x.started_at, reverse=True)[:5]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            return {"error": str(e)}
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get summary of compliance management system."""
        try:
            return {
                "total_rules": len(self.compliance_rules),
                "total_violations": len(self.violations),
                "total_audits": len(self.audits),
                "compliance_types": [ct.value for ct in ComplianceType],
                "severity_levels": [cs.value for cs in ComplianceSeverity],
                "rules_by_type": {
                    ct.value: len([r for r in self.compliance_rules.values() if r.compliance_type == ct])
                    for ct in ComplianceType
                },
                "violations_by_status": {
                    "open": len([v for v in self.violations.values() if v.status == "open"]),
                    "resolved": len([v for v in self.violations.values() if v.status == "resolved"])
                },
                "audits_by_status": {
                    "completed": len([a for a in self.audits.values() if a.status == "completed"]),
                    "in_progress": len([a for a in self.audits.values() if a.status == "in_progress"]),
                    "failed": len([a for a in self.audits.values() if a.status == "failed"])
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting compliance summary: {str(e)}")
            return {}