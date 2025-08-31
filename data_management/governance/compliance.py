"""
Compliance Management System

Advanced compliance monitoring and enforcement for regulatory standards
including GDPR, CCPA, DMCA and industry-specific regulations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
License: Proprietary - Unauthorized use prohibited

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json
import hashlib

from ...core.base import BaseManager
from ...core.exceptions import ComplianceError, ValidationError
from ...core.database import DatabaseManager
from ...core.cache import CacheManager
from ...ai.models import PersonalDataDetector, ContentClassifier


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    DMCA = "dmca"
    COPPA = "coppa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class ComplianceStatus(Enum):
    """Compliance assessment status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceIssue:
    """Compliance issue record"""
    issue_id: str
    framework: ComplianceFramework
    content_id: str
    issue_type: str
    description: str
    risk_level: RiskLevel
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceReport:
    """Compliance assessment report"""
    report_id: str
    content_id: str
    framework: ComplianceFramework
    status: ComplianceStatus
    score: float  # 0-100 compliance score
    issues: List[ComplianceIssue]
    recommendations: List[str]
    assessed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseComplianceChecker(ABC):
    """Base class for compliance framework checkers"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def assess_compliance(
        self,
        content_id: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> ComplianceReport:
        """Assess compliance for given content - base implementation"""



        try:
            self.logger.info(f"Assessing compliance for content: {content_id}")
            
            # Base implementation with generic compliance assessment
            # Subclasses should override with specific framework logic
            compliance_status = ComplianceStatus.COMPLIANT
            violations = []
            recommendations = []
            
            # Basic checks
            if not content_id:
                violations.append("Content ID is required")
                compliance_status = ComplianceStatus.NON_COMPLIANT
            
            if not content_type:
                violations.append("Content type is required")
                compliance_status = ComplianceStatus.NON_COMPLIANT
            
            # Create compliance report
            report = ComplianceReport(
                content_id=content_id,
                framework=self.framework,
                assessment_date=datetime.utcnow(),
                status=compliance_status,
                violations=violations,
                recommendations=recommendations,
                metadata=metadata
            )
            
            self.logger.info(f"Compliance assessment completed for {content_id}: {compliance_status}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error assessing compliance: {str(e)}")
            # Return non-compliant report on error
            return ComplianceReport(
                content_id=content_id,
                framework=self.framework,
                assessment_date=datetime.utcnow(),
                status=ComplianceStatus.NON_COMPLIANT,
                violations=[f"Assessment error: {str(e)}"],
                recommendations=["Review content and retry assessment"],
                metadata=metadata
            )
    
    def get_requirements(self) -> List[str]:
        """Get list of compliance requirements - base implementation"""



        try:
            # Base implementation with generic requirements
            # Subclasses should override with specific framework requirements
            return [
                "Content must have valid identification",
                "Content type must be specified",
                "Metadata must be provided",
                "Content must follow platform guidelines",
                "Data protection measures must be in place"
            ]
        except Exception as e:
            self.logger.error(f"Error getting requirements: {str(e)}")
            return []
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get information about the compliance framework - base implementation"""



        try:
            # Base implementation with generic framework info
            # Subclasses should override with specific framework information
            return {
                "name": self.framework,
                "version": "1.0",
                "description": "Base compliance framework implementation",
                "requirements_count": len(self.get_requirements()),
                "last_updated": datetime.utcnow().isoformat(),
                "scope": "General content compliance",
                "jurisdiction": "International"
            }
        except Exception as e:
            self.logger.error(f"Error getting framework info: {str(e)}")
            return {
                "name": self.framework,
                "error": str(e)
            }


class GDPRCompliance(BaseComplianceChecker):
    """
    GDPR Compliance Checker
    
    Implements General Data Protection Regulation compliance checking
    for personal data processing and protection.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.framework = ComplianceFramework.GDPR
        
        # Initialize PII detector
        self.pii_detector = PersonalDataDetector(config)
        
        # GDPR requirements mapping
        self.requirements = {
            "lawful_basis": "Processing must have lawful basis",
            "consent": "Explicit consent for data processing",
            "data_minimization": "Only collect necessary data",
            "purpose_limitation": "Data used only for stated purpose",
            "accuracy": "Data must be accurate and up-to-date",
            "storage_limitation": "Data retained only as long as necessary",
            "integrity_confidentiality": "Data must be secure",
            "accountability": "Controller must demonstrate compliance"
        }
    
    async def assess_compliance(
        self,
        content_id: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> ComplianceReport:
        """
        Assess GDPR compliance for content
        
        Args:
            content_id: ID of content to assess
            content_type: Type of content (audio, video, image, text)
            metadata: Content metadata including processing info
            
        Returns:
            ComplianceReport: Detailed compliance assessment
        """
        issues = []
        score = 100.0
        
        try:
            # Check for personal data
            pii_issues = await self._check_personal_data(content_id, metadata)
            issues.extend(pii_issues)
            
            # Check consent requirements
            consent_issues = await self._check_consent(content_id, metadata)
            issues.extend(consent_issues)
            
            # Check data minimization
            minimization_issues = await self._check_data_minimization(metadata)
            issues.extend(minimization_issues)
            
            # Check purpose limitation
            purpose_issues = await self._check_purpose_limitation(metadata)
            issues.extend(purpose_issues)
            
            # Check retention limits
            retention_issues = await self._check_retention_limits(metadata)
            issues.extend(retention_issues)
            
            # Check security measures
            security_issues = await self._check_security_measures(metadata)
            issues.extend(security_issues)
            
            # Calculate compliance score
            score = self._calculate_gdpr_score(issues)
            
            # Determine overall status
            status = self._determine_status(score, issues)
            
            # Generate recommendations
            recommendations = self._generate_gdpr_recommendations(issues)
            
            return ComplianceReport(
                report_id=f"gdpr_{content_id}_{datetime.utcnow().timestamp()}",
                content_id=content_id,
                framework=self.framework,
                status=status,
                score=score,
                issues=issues,
                recommendations=recommendations,
                assessed_at=datetime.utcnow(),
                metadata={
                    "content_type": content_type,
                    "assessment_version": "1.0",
                    "pii_detected": any("personal_data" in issue.issue_type for issue in issues)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing GDPR compliance for {content_id}: {e}")
            raise ComplianceError(f"GDPR assessment failed: {e}")
    
    async def _check_personal_data(self, content_id: str, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check for personal data and processing compliance"""
        issues = []
        
        # Detect PII in content
        pii_results = await self.pii_detector.detect_pii(metadata.get("content", ""))
        
        if pii_results.get("contains_pii", False):
            # Check if processing has lawful basis
            if not metadata.get("processing", {}).get("lawful_basis"):
                issues.append(ComplianceIssue(
                    issue_id=f"gdpr_lawful_basis_{content_id}",
                    framework=self.framework,
                    content_id=content_id,
                    issue_type="personal_data_lawful_basis",
                    description="Personal data detected without documented lawful basis",
                    risk_level=RiskLevel.HIGH,
                    detected_at=datetime.utcnow(),
                    metadata={"pii_types": pii_results.get("pii_types", [])}
                ))
            
            # Check data controller information
            if not metadata.get("controller", {}).get("contact_info"):
                issues.append(ComplianceIssue(
                    issue_id=f"gdpr_controller_{content_id}",
                    framework=self.framework,
                    content_id=content_id,
                    issue_type="personal_data_controller",
                    description="Data controller information not specified",
                    risk_level=RiskLevel.MEDIUM,
                    detected_at=datetime.utcnow()
                ))
        
        return issues
    
    async def _check_consent(self, content_id: str, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check consent requirements"""
        issues = []
        processing = metadata.get("processing", {})
        
        # If processing relies on consent
        if processing.get("lawful_basis") == "consent":
            # Check consent record
            consent = metadata.get("consent", {})
            
            if not consent.get("obtained_at"):
                issues.append(ComplianceIssue(
                    issue_id=f"gdpr_consent_missing_{content_id}",
                    framework=self.framework,
                    content_id=content_id,
                    issue_type="consent_missing",
                    description="Consent required but not recorded",
                    risk_level=RiskLevel.HIGH,
                    detected_at=datetime.utcnow()
                ))
            
            # Check consent specificity
            if not consent.get("purposes"):
                issues.append(ComplianceIssue(
                    issue_id=f"gdpr_consent_vague_{content_id}",
                    framework=self.framework,
                    content_id=content_id,
                    issue_type="consent_vague",
                    description="Consent not specific about purposes",
                    risk_level=RiskLevel.MEDIUM,
                    detected_at=datetime.utcnow()
                ))
            
            # Check consent withdrawal mechanism
            if not consent.get("withdrawal_mechanism"):
                issues.append(ComplianceIssue(
                    issue_id=f"gdpr_consent_withdrawal_{content_id}",
                    framework=self.framework,
                    content_id=content_id,
                    issue_type="consent_withdrawal",
                    description="No mechanism for consent withdrawal",
                    risk_level=RiskLevel.MEDIUM,
                    detected_at=datetime.utcnow()
                ))
        
        return issues
    
    async def _check_data_minimization(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check data minimization principle"""
        issues = []
        
        # Check if data collection is justified
        collected_fields = metadata.get("collected_fields", [])
        necessary_fields = metadata.get("necessary_fields", [])
        
        if len(collected_fields) > len(necessary_fields):
            unnecessary_fields = set(collected_fields) - set(necessary_fields)
            issues.append(ComplianceIssue(
                issue_id=f"gdpr_minimization_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="data_minimization",
                description=f"Unnecessary data fields collected: {list(unnecessary_fields)}",
                risk_level=RiskLevel.MEDIUM,
                detected_at=datetime.utcnow(),
                metadata={"unnecessary_fields": list(unnecessary_fields)}
            ))
        
        return issues
    
    async def _check_purpose_limitation(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check purpose limitation principle"""
        issues = []
        
        stated_purposes = metadata.get("processing", {}).get("purposes", [])
        actual_usage = metadata.get("usage", {}).get("purposes", [])
        
        # Check if actual usage exceeds stated purposes
        if actual_usage and not all(purpose in stated_purposes for purpose in actual_usage):
            unauthorized_purposes = set(actual_usage) - set(stated_purposes)
            issues.append(ComplianceIssue(
                issue_id=f"gdpr_purpose_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="purpose_limitation",
                description=f"Data used for unauthorized purposes: {list(unauthorized_purposes)}",
                risk_level=RiskLevel.HIGH,
                detected_at=datetime.utcnow(),
                metadata={"unauthorized_purposes": list(unauthorized_purposes)}
            ))
        
        return issues
    
    async def _check_retention_limits(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check data retention limits"""
        issues = []
        
        retention_policy = metadata.get("retention", {})
        created_at = metadata.get("created_at")
        
        if created_at and retention_policy.get("max_days"):
            created_date = datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at
            max_retention = timedelta(days=retention_policy["max_days"])
            
            if datetime.utcnow() - created_date > max_retention:
                issues.append(ComplianceIssue(
                    issue_id=f"gdpr_retention_{metadata.get('content_id')}",
                    framework=self.framework,
                    content_id=metadata.get("content_id", "unknown"),
                    issue_type="retention_exceeded",
                    description="Data retained beyond specified retention period",
                    risk_level=RiskLevel.HIGH,
                    detected_at=datetime.utcnow(),
                    metadata={
                        "retention_days": retention_policy["max_days"],
                        "age_days": (datetime.utcnow() - created_date).days
                    }
                ))
        
        return issues
    
    async def _check_security_measures(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check security measures implementation"""
        issues = []
        
        security = metadata.get("security", {})
        
        # Check encryption
        if not security.get("encrypted", False):
            issues.append(ComplianceIssue(
                issue_id=f"gdpr_encryption_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="security_encryption",
                description="Personal data not encrypted",
                risk_level=RiskLevel.HIGH,
                detected_at=datetime.utcnow()
            ))
        
        # Check access controls
        if not security.get("access_controls"):
            issues.append(ComplianceIssue(
                issue_id=f"gdpr_access_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="security_access",
                description="Access controls not implemented",
                risk_level=RiskLevel.MEDIUM,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    def _calculate_gdpr_score(self, issues: List[ComplianceIssue]) -> float:
        """Calculate GDPR compliance score"""
        if not issues:
            return 100.0
        
        # Deduct points based on risk level
        score = 100.0
        risk_penalties = {
            RiskLevel.LOW: 5.0,
            RiskLevel.MEDIUM: 15.0,
            RiskLevel.HIGH: 30.0,
            RiskLevel.CRITICAL: 50.0
        }
        
        for issue in issues:
            score -= risk_penalties.get(issue.risk_level, 10.0)
        
        return max(0.0, score)
    
    def _determine_status(self, score: float, issues: List[ComplianceIssue]) -> ComplianceStatus:
        """Determine overall compliance status"""
        critical_issues = [i for i in issues if i.risk_level == RiskLevel.CRITICAL]
        high_issues = [i for i in issues if i.risk_level == RiskLevel.HIGH]
        
        if critical_issues:
            return ComplianceStatus.NON_COMPLIANT
        elif high_issues or score < 70:
            return ComplianceStatus.REQUIRES_ACTION
        elif score < 90:
            return ComplianceStatus.PENDING_REVIEW
        else:
            return ComplianceStatus.COMPLIANT
    
    def _generate_gdpr_recommendations(self, issues: List[ComplianceIssue]) -> List[str]:
        """Generate GDPR compliance recommendations"""
        recommendations = []
        
        issue_types = {issue.issue_type for issue in issues}
        
        if "personal_data_lawful_basis" in issue_types:
            recommendations.append("Document lawful basis for personal data processing")
        
        if "consent_missing" in issue_types:
            recommendations.append("Implement consent collection mechanism")
        
        if "data_minimization" in issue_types:
            recommendations.append("Review data collection to minimize unnecessary fields")
        
        if "purpose_limitation" in issue_types:
            recommendations.append("Ensure data usage aligns with stated purposes")
        
        if "retention_exceeded" in issue_types:
            recommendations.append("Implement automated data retention policies")
        
        if "security_encryption" in issue_types:
            recommendations.append("Implement encryption for personal data")
        
        return recommendations
    
    def get_requirements(self) -> List[str]:
        """Get GDPR requirements"""



        return list(self.requirements.values())
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get GDPR framework information"""



        return {
            "name": "General Data Protection Regulation",
            "jurisdiction": "European Union",
            "effective_date": "2018-05-25",
            "max_fine": "4% of annual revenue or €20M",
            "key_principles": list(self.requirements.keys()),
            "data_subject_rights": [
                "right_to_information",
                "right_of_access",
                "right_to_rectification", 
                "right_to_erasure",
                "right_to_restrict_processing",
                "right_to_data_portability",
                "right_to_object",
                "rights_automated_decision_making"
            ]
        }


class CCPACompliance(BaseComplianceChecker):
    """
    CCPA Compliance Checker
    
    Implements California Consumer Privacy Act compliance checking
    for consumer rights and business obligations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.framework = ComplianceFramework.CCPA
    
    async def assess_compliance(
        self,
        content_id: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> ComplianceReport:
        """Assess CCPA compliance for content"""
        issues = []
        score = 100.0
        
        try:
            # Check consumer rights implementation
            rights_issues = await self._check_consumer_rights(content_id, metadata)
            issues.extend(rights_issues)
            
            # Check data disclosure requirements
            disclosure_issues = await self._check_disclosure_requirements(metadata)
            issues.extend(disclosure_issues)
            
            # Check opt-out mechanisms
            optout_issues = await self._check_optout_mechanisms(metadata)
            issues.extend(optout_issues)
            
            # Calculate score and status
            score = self._calculate_ccpa_score(issues)
            status = self._determine_status(score, issues)
            recommendations = self._generate_ccpa_recommendations(issues)
            
            return ComplianceReport(
                report_id=f"ccpa_{content_id}_{datetime.utcnow().timestamp()}",
                content_id=content_id,
                framework=self.framework,
                status=status,
                score=score,
                issues=issues,
                recommendations=recommendations,
                assessed_at=datetime.utcnow(),
                metadata={"content_type": content_type}
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing CCPA compliance for {content_id}: {e}")
            raise ComplianceError(f"CCPA assessment failed: {e}")
    
    async def _check_consumer_rights(self, content_id: str, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check consumer rights implementation"""
        issues = []
        
        consumer_rights = metadata.get("consumer_rights", {})
        
        # Check right to know implementation
        if not consumer_rights.get("right_to_know_implemented"):
            issues.append(ComplianceIssue(
                issue_id=f"ccpa_right_to_know_{content_id}",
                framework=self.framework,
                content_id=content_id,
                issue_type="consumer_right_to_know",
                description="Right to know not implemented",
                risk_level=RiskLevel.HIGH,
                detected_at=datetime.utcnow()
            ))
        
        # Check right to delete implementation
        if not consumer_rights.get("right_to_delete_implemented"):
            issues.append(ComplianceIssue(
                issue_id=f"ccpa_right_to_delete_{content_id}",
                framework=self.framework,
                content_id=content_id,
                issue_type="consumer_right_to_delete",
                description="Right to delete not implemented",
                risk_level=RiskLevel.HIGH,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    async def _check_disclosure_requirements(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check data disclosure requirements"""
        issues = []
        
        disclosure = metadata.get("disclosure", {})
        
        if not disclosure.get("categories_collected"):
            issues.append(ComplianceIssue(
                issue_id=f"ccpa_disclosure_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="disclosure_categories",
                description="Categories of personal information not disclosed",
                risk_level=RiskLevel.MEDIUM,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    async def _check_optout_mechanisms(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check opt-out mechanisms"""
        issues = []
        
        optout = metadata.get("optout", {})
        
        if not optout.get("do_not_sell_link"):
            issues.append(ComplianceIssue(
                issue_id=f"ccpa_optout_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="optout_mechanism",
                description="Do Not Sell link not provided",
                risk_level=RiskLevel.MEDIUM,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    def _calculate_ccpa_score(self, issues: List[ComplianceIssue]) -> float:
        """Calculate CCPA compliance score"""
        if not issues:
            return 100.0
        
        score = 100.0
        for issue in issues:
            if issue.risk_level == RiskLevel.HIGH:
                score -= 25.0
            elif issue.risk_level == RiskLevel.MEDIUM:
                score -= 15.0
            else:
                score -= 5.0
        
        return max(0.0, score)
    
    def _generate_ccpa_recommendations(self, issues: List[ComplianceIssue]) -> List[str]:
        """Generate CCPA recommendations"""
        recommendations = []
        
        issue_types = {issue.issue_type for issue in issues}
        
        if "consumer_right_to_know" in issue_types:
            recommendations.append("Implement consumer right to know mechanisms")
        
        if "consumer_right_to_delete" in issue_types:
            recommendations.append("Implement consumer right to delete mechanisms")
        
        if "disclosure_categories" in issue_types:
            recommendations.append("Provide clear disclosure of data categories collected")
        
        return recommendations
    
    def get_requirements(self) -> List[str]:
        """Get CCPA requirements"""



        return [
            "Consumer right to know",
            "Consumer right to delete",
            "Consumer right to opt-out",
            "Disclosure requirements",
            "Non-discrimination provisions"
        ]
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get CCPA framework information"""



        return {
            "name": "California Consumer Privacy Act",
            "jurisdiction": "California, USA",
            "effective_date": "2020-01-01",
            "max_fine": "$7,500 per violation",
            "consumer_rights": [
                "right_to_know",
                "right_to_delete",
                "right_to_opt_out",
                "right_to_non_discrimination"
            ]
        }


class DMCACompliance(BaseComplianceChecker):
    """
    DMCA Compliance Checker
    
    Implements Digital Millennium Copyright Act compliance checking
    for copyright protection and safe harbor provisions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.framework = ComplianceFramework.DMCA
    
    async def assess_compliance(
        self,
        content_id: str,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> ComplianceReport:
        """Assess DMCA compliance for content"""
        issues = []
        score = 100.0
        
        try:
            # Check copyright ownership
            copyright_issues = await self._check_copyright_ownership(content_id, metadata)
            issues.extend(copyright_issues)
            
            # Check takedown procedures
            takedown_issues = await self._check_takedown_procedures(metadata)
            issues.extend(takedown_issues)
            
            # Check safe harbor compliance
            safeharbor_issues = await self._check_safe_harbor(metadata)
            issues.extend(safeharbor_issues)
            
            score = self._calculate_dmca_score(issues)
            status = self._determine_status(score, issues)
            recommendations = self._generate_dmca_recommendations(issues)
            
            return ComplianceReport(
                report_id=f"dmca_{content_id}_{datetime.utcnow().timestamp()}",
                content_id=content_id,
                framework=self.framework,
                status=status,
                score=score,
                issues=issues,
                recommendations=recommendations,
                assessed_at=datetime.utcnow(),
                metadata={"content_type": content_type}
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing DMCA compliance for {content_id}: {e}")
            raise ComplianceError(f"DMCA assessment failed: {e}")
    
    async def _check_copyright_ownership(self, content_id: str, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check copyright ownership documentation"""
        issues = []
        
        copyright_info = metadata.get("copyright", {})
        
        if not copyright_info.get("owner"):
            issues.append(ComplianceIssue(
                issue_id=f"dmca_owner_{content_id}",
                framework=self.framework,
                content_id=content_id,
                issue_type="copyright_ownership",
                description="Copyright owner not specified",
                risk_level=RiskLevel.HIGH,
                detected_at=datetime.utcnow()
            ))
        
        if not copyright_info.get("registration_number"):
            issues.append(ComplianceIssue(
                issue_id=f"dmca_registration_{content_id}",
                framework=self.framework,
                content_id=content_id,
                issue_type="copyright_registration",
                description="Copyright registration not provided",
                risk_level=RiskLevel.MEDIUM,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    async def _check_takedown_procedures(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check DMCA takedown procedures"""
        issues = []
        
        takedown = metadata.get("takedown", {})
        
        if not takedown.get("agent_contact"):
            issues.append(ComplianceIssue(
                issue_id=f"dmca_agent_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="takedown_agent",
                description="DMCA agent contact not provided",
                risk_level=RiskLevel.HIGH,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    async def _check_safe_harbor(self, metadata: Dict[str, Any]) -> List[ComplianceIssue]:
        """Check safe harbor compliance"""
        issues = []
        
        safe_harbor = metadata.get("safe_harbor", {})
        
        if not safe_harbor.get("policy_implemented"):
            issues.append(ComplianceIssue(
                issue_id=f"dmca_policy_{metadata.get('content_id')}",
                framework=self.framework,
                content_id=metadata.get("content_id", "unknown"),
                issue_type="safe_harbor_policy",
                description="Safe harbor policy not implemented",
                risk_level=RiskLevel.MEDIUM,
                detected_at=datetime.utcnow()
            ))
        
        return issues
    
    def _calculate_dmca_score(self, issues: List[ComplianceIssue]) -> float:
        """Calculate DMCA compliance score"""
        if not issues:
            return 100.0
        
        score = 100.0
        for issue in issues:
            if issue.risk_level == RiskLevel.HIGH:
                score -= 30.0
            elif issue.risk_level == RiskLevel.MEDIUM:
                score -= 20.0
            else:
                score -= 10.0
        
        return max(0.0, score)
    
    def _generate_dmca_recommendations(self, issues: List[ComplianceIssue]) -> List[str]:
        """Generate DMCA recommendations"""
        recommendations = []
        
        issue_types = {issue.issue_type for issue in issues}
        
        if "copyright_ownership" in issue_types:
            recommendations.append("Document copyright ownership clearly")
        
        if "takedown_agent" in issue_types:
            recommendations.append("Designate and register DMCA agent")
        
        if "safe_harbor_policy" in issue_types:
            recommendations.append("Implement safe harbor policies")
        
        return recommendations
    
    def get_requirements(self) -> List[str]:
        """Get DMCA requirements"""



        return [
            "Copyright ownership documentation",
            "DMCA takedown procedures",
            "Safe harbor compliance",
            "Designated agent registration"
        ]
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get DMCA framework information"""



        return {
            "name": "Digital Millennium Copyright Act",
            "jurisdiction": "United States",
            "effective_date": "1998-10-28",
            "key_provisions": [
                "safe_harbor_provisions",
                "takedown_procedures",
                "counter_notification_procedures"
            ]
        }


class ComplianceManager(BaseManager):
    """
    Central compliance management system
    
    Orchestrates compliance checking across multiple regulatory frameworks
    and provides unified compliance reporting and monitoring.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the compliance manager"""
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize compliance checkers
        self.checkers = {
            ComplianceFramework.GDPR: GDPRCompliance(config),
            ComplianceFramework.CCPA: CCPACompliance(config),
            ComplianceFramework.DMCA: DMCACompliance(config)
        }
        
        # Compliance storage
        self.reports: Dict[str, ComplianceReport] = {}
        self.issues: List[ComplianceIssue] = []
        
        # Metrics
        self.metrics = {
            "total_assessments": 0,
            "compliance_rate": 0.0,
            "critical_issues": 0,
            "resolved_issues": 0
        }
    
    async def assess_compliance(
        self,
        content_id: str,
        content_type: str,
        metadata: Dict[str, Any],
        frameworks: Optional[List[ComplianceFramework]] = None
    ) -> Dict[ComplianceFramework, ComplianceReport]:
        """
        Assess compliance across multiple frameworks
        
        Args:
            content_id: ID of content to assess
            content_type: Type of content
            metadata: Content metadata
            frameworks: Specific frameworks to check (default: all)
            
        Returns:
            Dict mapping frameworks to compliance reports
        """
        if frameworks is None:
            frameworks = list(self.checkers.keys())
        
        reports = {}
        
        try:
            for framework in frameworks:
                if framework in self.checkers:
                    checker = self.checkers[framework]
                    report = await checker.assess_compliance(content_id, content_type, metadata)
                    reports[framework] = report
                    
                    # Store report
                    self.reports[report.report_id] = report
                    
                    # Collect issues
                    self.issues.extend(report.issues)
            
            # Update metrics
            self.metrics["total_assessments"] += 1
            self._update_compliance_metrics()
            
            return reports
            
        except Exception as e:
            self.logger.error(f"Error assessing compliance for {content_id}: {e}")
            raise ComplianceError(f"Compliance assessment failed: {e}")
    
    async def get_compliance_summary(
        self,
        content_id: Optional[str] = None,
        framework: Optional[ComplianceFramework] = None
    ) -> Dict[str, Any]:
        """
        Get compliance summary with optional filtering
        
        Args:
            content_id: Filter by content ID
            framework: Filter by compliance framework
            
        Returns:
            Dict with compliance summary statistics
        """
        filtered_reports = list(self.reports.values())
        
        if content_id:
            filtered_reports = [r for r in filtered_reports if r.content_id == content_id]
        
        if framework:
            filtered_reports = [r for r in filtered_reports if r.framework == framework]
        
        if not filtered_reports:
            return {"total_reports": 0, "average_score": 0.0, "status_breakdown": {}}
        
        # Calculate summary statistics
        total_reports = len(filtered_reports)
        average_score = sum(r.score for r in filtered_reports) / total_reports
        
        status_breakdown = {}
        for status in ComplianceStatus:
            count = len([r for r in filtered_reports if r.status == status])
            status_breakdown[status.value] = count
        
        framework_breakdown = {}
        for fw in ComplianceFramework:
            count = len([r for r in filtered_reports if r.framework == fw])
            if count > 0:
                framework_breakdown[fw.value] = count
        
        return {
            "total_reports": total_reports,
            "average_score": round(average_score, 2),
            "status_breakdown": status_breakdown,
            "framework_breakdown": framework_breakdown,
            "compliance_rate": len([r for r in filtered_reports if r.status == ComplianceStatus.COMPLIANT]) / total_reports * 100
        }
    
    async def get_issues(
        self,
        framework: Optional[ComplianceFramework] = None,
        risk_level: Optional[RiskLevel] = None,
        resolved: Optional[bool] = None
    ) -> List[ComplianceIssue]:
        """
        Get compliance issues with optional filtering
        
        Args:
            framework: Filter by compliance framework
            risk_level: Filter by risk level
            resolved: Filter by resolution status
            
        Returns:
            List of filtered compliance issues
        """
        filtered_issues = self.issues.copy()
        
        if framework:
            filtered_issues = [i for i in filtered_issues if i.framework == framework]
        
        if risk_level:
            filtered_issues = [i for i in filtered_issues if i.risk_level == risk_level]
        
        if resolved is not None:
            if resolved:
                filtered_issues = [i for i in filtered_issues if i.resolved_at is not None]
            else:
                filtered_issues = [i for i in filtered_issues if i.resolved_at is None]
        
        return filtered_issues
    
    async def resolve_issue(
        self,
        issue_id: str,
        resolution_action: Optional[str] = None
    ) -> bool:
        """
        Mark a compliance issue as resolved
        
        Args:
            issue_id: ID of issue to resolve
            resolution_action: Description of resolution action taken
            
        Returns:
            bool: True if issue resolved successfully
        """
        for issue in self.issues:
            if issue.issue_id == issue_id:
                issue.resolved_at = datetime.utcnow()
                issue.resolution_action = resolution_action
                
                self.metrics["resolved_issues"] += 1
                self._update_compliance_metrics()
                
                self.logger.info(f"Resolved compliance issue: {issue_id}")
                return True
        
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get compliance metrics"""



        return {
            **self.metrics,
            "framework_coverage": len(self.checkers),
            "issue_breakdown": {
                risk_level.value: len([
                    i for i in self.issues 
                    if i.risk_level == risk_level and i.resolved_at is None
                ])
                for risk_level in RiskLevel
            }
        }
    
    def _update_compliance_metrics(self) -> None:
        """Update compliance metrics"""
        total_reports = len(self.reports)
        if total_reports > 0:
            compliant_reports = len([
                r for r in self.reports.values() 
                if r.status == ComplianceStatus.COMPLIANT
            ])
            self.metrics["compliance_rate"] = (compliant_reports / total_reports) * 100
        
        self.metrics["critical_issues"] = len([
            i for i in self.issues 
            if i.risk_level == RiskLevel.CRITICAL and i.resolved_at is None
        ])
