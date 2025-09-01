"""Compliance Checker Module - Automated compliance verification and monitoring.

Ensures content and protection strategies comply with regulations, platform policies,
and industry standards across different jurisdictions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from ...core.config import settings
from ...core.cache import cache_manager
from ...utils.logging import get_logger

logger = get_logger(__name__)


class ComplianceType(str, Enum):
    """
Types of compliance requirements."""

    LEGAL = "legal"
    PLATFORM = "platform"
    INDUSTRY = "industry"
    REGIONAL = "regional"
    INTERNATIONAL = "international"


class ComplianceStatus(str, Enum):
    """Compliance status levels."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    UNKNOWN = "unknown"


class ComplianceArea(str, Enum):
    """Areas of compliance."""

    COPYRIGHT = "copyright"
    PRIVACY = "privacy"
    DATA_PROTECTION = "data_protection"
    CONTENT_POLICY = "content_policy"
    ACCESSIBILITY = "accessibility"
    TAXATION = "taxation"
    LICENSING = "licensing"
    ADVERTISING = "advertising"


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement."""
    requirement_id: str
    name: str
    description: str
    compliance_type: ComplianceType
    compliance_area: ComplianceArea
    jurisdiction: str
    mandatory: bool
    deadline: Optional[datetime]
    verification_method: str
    documentation_required: List[str]
    applicable_content_types: List[str]
    applicable_platforms: List[str]
    penalty_for_non_compliance: str
    reference_url: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class ComplianceCheck:
    """
Result of compliance verification."""
    check_id: str
    requirement_id: str
    content_id: Optional[str]
    status: ComplianceStatus
    compliance_score: float
    issues_found: List[str]
    recommendations: List[str]
    evidence_collected: Dict[str, Any]
    verification_details: Dict[str, Any]
    next_check_date: datetime
    checked_at: datetime
    checked_by: str


@dataclass
class ComplianceReport:
    """
Comprehensive compliance assessment report."""
    report_id: str
    user_id: str
    scope: str
    total_requirements: int
    compliant_count: int
    non_compliant_count: int
    partially_compliant_count: int
    overall_compliance_score: float
    compliance_checks: List[ComplianceCheck]
    critical_issues: List[str]
    upcoming_deadlines: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime
    valid_until: datetime


class ComplianceChecker:
    """
    Automated compliance checker for content protection.
    
    Provides comprehensive compliance verification including:
    - Legal and regulatory compliance
    - Platform-specific policy compliance
    - Industry standards adherence
    - Regional and international requirements
    - Automated monitoring and alerts
    """
    def __init__(self):
        self.compliance_rules = self._load_compliance_rules()
        self.jurisdiction_map = self._load_jurisdiction_map()
        self.cache_ttl = 3600  # 1 hour cache
        
    async def check_content_compliance(
        self,
        user_id: str,
        content_id: str,
        jurisdiction: str,
        target_platforms: List[str]
    ) -> ComplianceReport:
        """
        Perform comprehensive compliance check for content.
        
        Args:
            user_id: Creator user ID
            content_id: Content to check
            jurisdiction: Legal jurisdiction
            target_platforms: Target distribution platforms
            
        Returns:
            ComplianceReport with detailed assessment
        """
        try:
            logger.info(f"Starting compliance check for content {content_id}")
            
            # Get content metadata
            content_metadata = await self._get_content_metadata(user_id, content_id)
            
            # Identify applicable requirements
            applicable_requirements = await self._identify_applicable_requirements(
                content_metadata, jurisdiction, target_platforms
            )
            
            # Perform compliance checks
            compliance_checks = []
            for requirement in applicable_requirements:
                check_result = await self._perform_compliance_check(
                    requirement, content_metadata, user_id
                )
                compliance_checks.append(check_result)
            
            # Calculate overall compliance metrics
            compliance_metrics = await self._calculate_compliance_metrics(compliance_checks)
            
            # Identify critical issues
            critical_issues = await self._identify_critical_issues(
                compliance_checks, applicable_requirements
            )
            
            # Check upcoming deadlines
            upcoming_deadlines = await self._check_upcoming_deadlines(
                applicable_requirements
            )
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                compliance_checks, critical_issues
            )
            
            # Create compliance report
            report = ComplianceReport(
                report_id=f"compliance_{content_id}_{int(datetime.utcnow().timestamp())}",
                user_id=user_id,
                scope=f"content_{content_id}",
                total_requirements=len(applicable_requirements),
                compliant_count=compliance_metrics["compliant"],
                non_compliant_count=compliance_metrics["non_compliant"],
                partially_compliant_count=compliance_metrics["partially_compliant"],
                overall_compliance_score=compliance_metrics["overall_score"],
                compliance_checks=compliance_checks,
                critical_issues=critical_issues,
                upcoming_deadlines=upcoming_deadlines,
                recommendations=recommendations,
                generated_at=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=30)
            )
            
            # Cache the report
            await self._cache_compliance_report(user_id, content_id, report)
            
            logger.info(f"Compliance check completed. Score: {compliance_metrics['overall_score']:.2f}")
            return report
            
        except Exception as e:
            logger.error(f"Error in compliance check: {str(e)}")
            raise
    
    async def check_platform_compliance(
        self,
        user_id: str,
        platform: str,
        content_portfolio: List[str]
    ) -> Dict[str, Any]:
        """
        Check compliance with specific platform policies.
        
        Args:
            user_id: Creator user ID
            platform: Platform to check against
            content_portfolio: List of content IDs
            
        Returns:
            Platform compliance assessment
        """
        try:
            logger.info(f"Checking {platform} compliance for user {user_id}")
            
            # Get platform-specific requirements
            platform_requirements = await self._get_platform_requirements(platform)
            
            # Check each content item
            content_compliance = {}
            for content_id in content_portfolio:
                content_metadata = await self._get_content_metadata(user_id, content_id)
                
                content_checks = []
                for requirement in platform_requirements:
                    if await self._is_requirement_applicable(requirement, content_metadata):
                        check_result = await self._perform_platform_compliance_check(
                            requirement, content_metadata, platform
                        )
                        content_checks.append(check_result)
                
                content_compliance[content_id] = {
                    "checks": content_checks,
                    "compliance_score": await self._calculate_content_compliance_score(content_checks),
                    "issues": [check.issues_found for check in content_checks if check.issues_found],
                    "status": await self._determine_content_compliance_status(content_checks)
                }
            
            # Calculate overall platform compliance
            overall_score = await self._calculate_overall_platform_compliance(content_compliance)
            
            # Identify platform-specific issues
            platform_issues = await self._identify_platform_issues(content_compliance)
            
            # Generate platform recommendations
            platform_recommendations = await self._generate_platform_recommendations(
                platform, content_compliance, platform_issues
            )
            
            assessment = {
                "user_id": user_id,
                "platform": platform,
                "assessment_date": datetime.utcnow().isoformat(),
                "content_count": len(content_portfolio),
                "overall_compliance_score": overall_score,
                "content_compliance": content_compliance,
                "platform_issues": platform_issues,
                "recommendations": platform_recommendations,
                "next_review_date": (datetime.utcnow() + timedelta(days=14)).isoformat()
            }
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error checking platform compliance: {str(e)}")
            return {}
    
    async def monitor_regulatory_changes(
        self,
        user_id: str,
        jurisdictions: List[str],
        monitoring_config: Dict[str, Any]
    ) -> str:
        """
        Set up monitoring for regulatory changes.
        
        Args:
            user_id: Creator user ID
            jurisdictions: Jurisdictions to monitor
            monitoring_config: Monitoring configuration
            
        Returns:
            Monitoring session ID
        """
        try:
            logger.info(f"Setting up regulatory monitoring for user {user_id}")
            
            # Create monitoring session
            session_id = f"reg_monitor_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Configure monitoring for each jurisdiction
            jurisdiction_monitors = {}
            for jurisdiction in jurisdictions:
                monitor_config = await self._setup_jurisdiction_monitoring(
                    jurisdiction, monitoring_config
                )
                jurisdiction_monitors[jurisdiction] = monitor_config
            
            # Set up change detection
            change_detection_config = await self._setup_change_detection(
                jurisdictions, monitoring_config
            )
            
            # Configure notifications
            notification_config = await self._setup_compliance_notifications(
                user_id, monitoring_config
            )
            
            # Store monitoring session
            monitoring_session = {
                "session_id": session_id,
                "user_id": user_id,
                "jurisdictions": jurisdictions,
                "jurisdiction_monitors": jurisdiction_monitors,
                "change_detection": change_detection_config,
                "notifications": notification_config,
                "created_at": datetime.utcnow(),
                "status": "active"
            }
            
            await self._store_monitoring_session(session_id, monitoring_session)
            
            logger.info(f"Regulatory monitoring started with session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error setting up regulatory monitoring: {str(e)}")
            raise
    
    async def generate_compliance_documentation(
        self,
        user_id: str,
        compliance_report: ComplianceReport,
        document_type: str
    ) -> Dict[str, Any]:
        """
        Generate compliance documentation.
        
        Args:
            user_id: Creator user ID
            compliance_report: Compliance assessment report
            document_type: Type of document to generate
            
        Returns:
            Generated compliance documentation
        """
        try:
            logger.info(f"Generating {document_type} documentation for user {user_id}")
            
            # Select document template based on type
            template = await self._get_document_template(document_type)
            
            # Extract relevant data from compliance report
            document_data = await self._extract_document_data(
                compliance_report, document_type
            )
            
            # Generate document content
            document_content = await self._generate_document_content(
                template, document_data
            )
            
            # Add legal disclaimers and signatures
            finalized_content = await self._finalize_document_content(
                document_content, document_type, user_id
            )
            
            # Generate metadata
            document_metadata = {
                "document_id": f"doc_{document_type}_{user_id}_{int(datetime.utcnow().timestamp())}",
                "user_id": user_id,
                "document_type": document_type,
                "compliance_report_id": compliance_report.report_id,
                "generated_at": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "format": "pdf",
                "language": "en",
                "legal_status": "draft"
            }
            
            documentation = {
                "metadata": document_metadata,
                "content": finalized_content,
                "attachments": await self._generate_document_attachments(
                    compliance_report, document_type
                ),
                "verification": await self._generate_document_verification(
                    finalized_content, document_metadata
                )
            }
            
            # Store documentation
            await self._store_compliance_documentation(user_id, documentation)
            
            return documentation
            
        except Exception as e:
            logger.error(f"Error generating compliance documentation: {str(e)}")
            return {}
    
    # Private helper methods
    
    def _load_compliance_rules(self) -> Dict[str, List[ComplianceRequirement]]:
        """Load compliance rules and requirements."""
        # This would typically load from a database or configuration files
        rules = {
            "copyright": [
                ComplianceRequirement(
                    requirement_id="copyright_registration",
                    name="Copyright Registration",
                    description="Content must be properly registered for copyright protection",
                    compliance_type=ComplianceType.LEGAL,
                    compliance_area=ComplianceArea.COPYRIGHT,
                    jurisdiction="international",
                    mandatory=True,
                    deadline=None,
                    verification_method="document_check",
                    documentation_required=["registration_certificate", "creation_proof"],
                    applicable_content_types=["music", "video", "writing", "photography"],
                    applicable_platforms=["all"],
                    penalty_for_non_compliance="Limited legal protection",
                    reference_url="https://copyright.gov/registration/",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            ],
            "gdpr": [
                ComplianceRequirement(
                    requirement_id="gdpr_consent",
                    name="GDPR Data Processing Consent",
                    description="Explicit consent required for processing personal data",
                    compliance_type=ComplianceType.REGIONAL,
                    compliance_area=ComplianceArea.DATA_PROTECTION,
                    jurisdiction="EU",
                    mandatory=True,
                    deadline=None,
                    verification_method="consent_audit",
                    documentation_required=["consent_records", "privacy_policy"],
                    applicable_content_types=["all"],
                    applicable_platforms=["all"],
                    penalty_for_non_compliance="Up to 4% of annual revenue",
                    reference_url="https://gdpr.eu/",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            ]
        }
        return rules
    
    def _load_jurisdiction_map(self) -> Dict[str, Dict[str, Any]]:
        """Load jurisdiction-specific compliance mappings."""
        return {
            "EU": {
                "regulations": ["gdpr", "copyright_directive", "digital_services_act"],
                "data_protection_authority": "EDPB",
                "copyright_office": "EUIPO"
            },
            "US": {
                "regulations": ["dmca", "ccpa", "coppa"],
                "data_protection_authority": "FTC",
                "copyright_office": "USCO"
            },
            "DE": {
                "regulations": ["gdpr", "tmg", "urheberrechtsgesetz"],
                "data_protection_authority": "BfDI",
                "copyright_office": "DPMA"
            }
        }
    
    async def _identify_applicable_requirements(
        self,
        content_metadata: Dict[str, Any],
        jurisdiction: str,
        target_platforms: List[str]
    ) -> List[ComplianceRequirement]:
        """Identify compliance requirements applicable to content."""
        try:
            applicable_requirements = []
            
            content_type = content_metadata.get("type", "unknown")
            contains_personal_data = content_metadata.get("contains_personal_data", False)
            
            # Check all compliance rule categories
            for category, requirements in self.compliance_rules.items():
                for requirement in requirements:
                    # Check jurisdiction applicability
                    if (requirement.jurisdiction == "international" or 
                        requirement.jurisdiction == jurisdiction):
                        
                        # Check content type applicability
                        if ("all" in requirement.applicable_content_types or
                            content_type in requirement.applicable_content_types):
                            
                            # Check platform applicability
                            if ("all" in requirement.applicable_platforms or
                                any(platform in requirement.applicable_platforms 
                                    for platform in target_platforms)):
                                
                                # Special checks for data protection
                                if (requirement.compliance_area == ComplianceArea.DATA_PROTECTION and
                                    not contains_personal_data):
                                    continue
                                
                                applicable_requirements.append(requirement)
            
            return applicable_requirements
            
        except Exception as e:
            logger.error(f"Error identifying applicable requirements: {str(e)}")
            return []
    
    async def _perform_compliance_check(
        self,
        requirement: ComplianceRequirement,
        content_metadata: Dict[str, Any],
        user_id: str
    ) -> ComplianceCheck:
        """Perform individual compliance check."""
        try:
            check_id = f"check_{requirement.requirement_id}_{int(datetime.utcnow().timestamp())}"
            
            # Perform verification based on method
            verification_result = await self._perform_verification(
                requirement, content_metadata, user_id
            )
            
            # Determine compliance status
            status = await self._determine_compliance_status(
                verification_result, requirement
            )
            
            # Calculate compliance score
            compliance_score = await self._calculate_compliance_score(
                verification_result, requirement
            )
            
            # Identify issues
            issues_found = await self._identify_compliance_issues(
                verification_result, requirement
            )
            
            # Generate recommendations
            recommendations = await self._generate_check_recommendations(
                issues_found, requirement
            )
            
            check = ComplianceCheck(
                check_id=check_id,
                requirement_id=requirement.requirement_id,
                content_id=content_metadata.get("id"),
                status=status,
                compliance_score=compliance_score,
                issues_found=issues_found,
                recommendations=recommendations,
                evidence_collected=verification_result.get("evidence", {}),
                verification_details=verification_result,
                next_check_date=datetime.utcnow() + timedelta(days=90),
                checked_at=datetime.utcnow(),
                checked_by="automated_system"
            )
            
            return check
            
        except Exception as e:
            logger.error(f"Error performing compliance check: {str(e)}")
            # Return failed check
            return ComplianceCheck(
                check_id=f"failed_{int(datetime.utcnow().timestamp())}",
                requirement_id=requirement.requirement_id,
                content_id=content_metadata.get("id"),
                status=ComplianceStatus.UNKNOWN,
                compliance_score=0.0,
                issues_found=["Check failed due to system error"],
                recommendations=["Retry compliance check manually"],
                evidence_collected={},
                verification_details={"error": str(e)},
                next_check_date=datetime.utcnow() + timedelta(days=1),
                checked_at=datetime.utcnow(),
                checked_by="automated_system"
            )
    
    # Additional helper methods (simplified implementations)
    
    async def _get_content_metadata(self, user_id: str, content_id: str) -> Dict[str, Any]:
        """Get content metadata for compliance checking."""
        return {
            "id": content_id,
            "type": "video",
            "title": "Sample Content",
            "contains_personal_data": False,
            "copyright_registered": False,
            "privacy_policy_accepted": True
        }
    
    async def _calculate_compliance_metrics(self, checks: List[ComplianceCheck]) -> Dict[str, Any]:
        """Calculate overall compliance metrics."""
        if not checks:
            return {"compliant": 0, "non_compliant": 0, "partially_compliant": 0, "overall_score": 0.0}
        
        compliant = len([c for c in checks if c.status == ComplianceStatus.COMPLIANT])
        non_compliant = len([c for c in checks if c.status == ComplianceStatus.NON_COMPLIANT])
        partially_compliant = len([c for c in checks if c.status == ComplianceStatus.PARTIALLY_COMPLIANT])
        
        total_score = sum(c.compliance_score for c in checks)
        overall_score = total_score / len(checks) if checks else 0.0
        
        return {
            "compliant": compliant,
            "non_compliant": non_compliant,
            "partially_compliant": partially_compliant,
            "overall_score": overall_score
        }
    
    async def _identify_critical_issues(self, checks: List[ComplianceCheck], requirements: List[ComplianceRequirement]) -> List[str]:
        """Identify critical compliance issues."""
        critical_issues = []
        
        for check in checks:
            if check.status == ComplianceStatus.NON_COMPLIANT:
                requirement = next((r for r in requirements if r.requirement_id == check.requirement_id), None)
                if requirement and requirement.mandatory:
                    critical_issues.extend(check.issues_found)
        
        return critical_issues
    
    async def _check_upcoming_deadlines(self, requirements: List[ComplianceRequirement]) -> List[Dict[str, Any]]:
        """
Check for upcoming compliance deadlines."""
        upcoming = []
        now = datetime.utcnow()
        
        for requirement in requirements:
            if requirement.deadline and requirement.deadline > now:
                days_until = (requirement.deadline - now).days
                if days_until <= 30:  # Within 30 days
                    upcoming.append({
                        "requirement_id": requirement.requirement_id,
                        "name": requirement.name,
                        "deadline": requirement.deadline.isoformat(),
                        "days_remaining": days_until,
                        "mandatory": requirement.mandatory
                    })
        
        return upcoming
    
    async def _generate_compliance_recommendations(self, checks: List[ComplianceCheck], critical_issues: List[str]) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = set()
        
        for check in checks:
            if check.status != ComplianceStatus.COMPLIANT:
                recommendations.update(check.recommendations)
        
        if critical_issues:
            recommendations.add("Address critical compliance issues immediately")
        
        return list(recommendations)
    
    async def _cache_compliance_report(self, user_id: str, content_id: str, report: ComplianceReport):
        """Cache compliance report."""
        try:
            cache_key = f"compliance_report:{user_id}:{content_id}"
            await cache_manager.set(cache_key, report.__dict__, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Failed to cache compliance report: {str(e)}")
    
    # Simplified implementations for remaining methods
    async def _get_platform_requirements(self, platform: str) -> List[ComplianceRequirement]:
        return []
    
    async def _is_requirement_applicable(self, requirement: ComplianceRequirement, content_metadata: Dict) -> bool:
        return True
    
    async def _perform_platform_compliance_check(self, requirement: ComplianceRequirement, content_metadata: Dict, platform: str) -> ComplianceCheck:
        return ComplianceCheck(
            check_id="platform_check",
            requirement_id=requirement.requirement_id,
            content_id=content_metadata.get("id"),
            status=ComplianceStatus.COMPLIANT,
            compliance_score=1.0,
            issues_found=[],
            recommendations=[],
            evidence_collected={},
            verification_details={},
            next_check_date=datetime.utcnow() + timedelta(days=30),
            checked_at=datetime.utcnow(),
            checked_by="automated_system"
        )
    
    async def _calculate_content_compliance_score(self, checks: List[ComplianceCheck]) -> float:
        if not checks:
            return 0.0
        return sum(c.compliance_score for c in checks) / len(checks)
    
    async def _determine_content_compliance_status(self, checks: List[ComplianceCheck]) -> str:
        if not checks:
            return "unknown"
        
        if all(c.status == ComplianceStatus.COMPLIANT for c in checks):
            return "compliant"
        elif any(c.status == ComplianceStatus.NON_COMPLIANT for c in checks):
            return "non_compliant"
        else:
            return "partially_compliant"
    
    async def _calculate_overall_platform_compliance(self, content_compliance: Dict) -> float:
        if not content_compliance:
            return 0.0
        
        scores = [item["compliance_score"] for item in content_compliance.values()]
        return sum(scores) / len(scores)
    
    async def _identify_platform_issues(self, content_compliance: Dict) -> List[str]:
        issues = []
        for content_id, compliance_data in content_compliance.items():
            issues.extend([issue for issue_list in compliance_data["issues"] for issue in issue_list])
        return list(set(issues))
    
    async def _generate_platform_recommendations(self, platform: str, content_compliance: Dict, issues: List[str]) -> List[str]:
        recommendations = []
        if issues:
            recommendations.append(f"Address platform-specific issues for {platform}")
        return recommendations
    
    # Additional simplified methods
    async def _setup_jurisdiction_monitoring(self, jurisdiction: str, config: Dict) -> Dict:
        return {"jurisdiction": jurisdiction, "monitoring_enabled": True}
    
    async def _setup_change_detection(self, jurisdictions: List[str], config: Dict) -> Dict:
        return {"detection_method": "rss_feed", "check_frequency": "daily"}
    
    async def _setup_compliance_notifications(self, user_id: str, config: Dict) -> Dict:
        return {"email_enabled": True, "urgency_threshold": "high"}
    
    async def _store_monitoring_session(self, session_id: str, session: Dict):
        logger.info(f"Stored monitoring session {session_id}")
    
    async def _get_document_template(self, document_type: str) -> str:
        return f"Template for {document_type}"
    
    async def _extract_document_data(self, report: ComplianceReport, document_type: str) -> Dict:
        return {"report_data": report.__dict__}
    
    async def _generate_document_content(self, template: str, data: Dict) -> str:
        return f"Generated content based on {template}"
    
    async def _finalize_document_content(self, content: str, document_type: str, user_id: str) -> str:
        return content + f"\n\nGenerated for user {user_id}"
    
    async def _generate_document_attachments(self, report: ComplianceReport, document_type: str) -> List[Dict]:
        return []
    
    async def _generate_document_verification(self, content: str, metadata: Dict) -> Dict:
        return {"hash": "content_hash", "signature": "digital_signature"}
    
    async def _store_compliance_documentation(self, user_id: str, documentation: Dict):
        logger.info(f"Stored compliance documentation for user {user_id}")
    
    async def _perform_verification(self, requirement: ComplianceRequirement, content_metadata: Dict, user_id: str) -> Dict:
        return {"verified": True, "evidence": {"method": requirement.verification_method}}
    
    async def _determine_compliance_status(self, verification_result: Dict, requirement: ComplianceRequirement) -> ComplianceStatus:
        if verification_result.get("verified", False):
            return ComplianceStatus.COMPLIANT
        else:
            return ComplianceStatus.NON_COMPLIANT
    
    async def _calculate_compliance_score(self, verification_result: Dict, requirement: ComplianceRequirement) -> float:
        return 1.0 if verification_result.get("verified", False) else 0.0
    
    async def _identify_compliance_issues(self, verification_result: Dict, requirement: ComplianceRequirement) -> List[str]:
        if not verification_result.get("verified", False):
            return [f"Failed to verify {requirement.name}"]
        return []
    
    async def _generate_check_recommendations(self, issues: List[str], requirement: ComplianceRequirement) -> List[str]:
        if issues:
            return [f"Complete {requirement.name} requirements"]
        return []
