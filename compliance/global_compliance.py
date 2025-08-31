"""
Global Legal Compliance Manager
Unified framework coordinating GDPR, CCPA, DMCA, PIPEDA, LGPD, and PDPA compliance

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Import existing compliance managers
try:
    from kubernetes.compliance.gdpr_compliance import GDPRComplianceManager
    from api.protection.dmca_compliance import EnterpriseDMCACompliance
except ImportError:
    # Fallback if modules not available
    GDPRComplianceManager = None
    EnterpriseDMCACompliance = None


class ComplianceRegulation(str, Enum):
    """Supported compliance regulations"""
    GDPR = "gdpr"              # General Data Protection Regulation (EU)
    CCPA = "ccpa"              # California Consumer Privacy Act (US)
    DMCA = "dmca"              # Digital Millennium Copyright Act (US)
    PIPEDA = "pipeda"          # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"              # Lei Geral de Proteção de Dados (Brazil)
    PDPA = "pdpa"              # Personal Data Protection Act (Singapore)


class ComplianceStatus(str, Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    EXEMPTED = "exempted"


class DataSubjectRight(str, Enum):
    """Universal data subject rights across regulations"""
    ACCESS = "access"                    # Right to access personal data
    RECTIFICATION = "rectification"      # Right to correct inaccurate data
    ERASURE = "erasure"                  # Right to delete personal data
    PORTABILITY = "portability"          # Right to data portability
    RESTRICTION = "restriction"          # Right to restrict processing
    OBJECTION = "objection"              # Right to object to processing
    OPT_OUT = "opt_out"                  # Right to opt-out (CCPA specific)
    KNOWLEDGE = "knowledge"              # Right to know (CCPA specific)


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement definition"""
    regulation: ComplianceRegulation
    requirement_id: str
    title: str
    description: str
    mandatory: bool = True
    jurisdiction: str = ""
    penalty_amount: Optional[float] = None
    implementation_deadline: Optional[datetime] = None
    verification_method: str = ""
    responsible_party: str = ""


@dataclass
class UserComplianceProfile:
    """User's global compliance profile"""
    user_id: int
    jurisdiction: str
    applicable_regulations: List[ComplianceRegulation] = field(default_factory=list)
    consent_status: Dict[str, Dict[str, bool]] = field(default_factory=dict)
    data_subject_requests: List[Dict[str, Any]] = field(default_factory=list)
    compliance_scores: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    risk_level: str = "low"


@dataclass
class GlobalComplianceReport:
    """Comprehensive global compliance report"""
    report_id: str
    generated_at: datetime
    reporting_period: str
    overall_compliance_score: float
    regulation_scores: Dict[str, float] = field(default_factory=dict)
    compliance_gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    total_users: int = 0
    compliant_users: int = 0
    outstanding_requests: int = 0
    violations_detected: int = 0
    enforcement_actions: int = 0


class ComplianceEngine(ABC):
    """Abstract base class for compliance engines"""
    
    @abstractmethod
    async def check_compliance(self, user_id: int) -> Dict[str, Any]:
        """Check compliance status for a user"""
        pass
    
    @abstractmethod
    async def process_data_subject_request(
        self, user_id: int, request_type: DataSubjectRight, details: Dict[str, Any]
    ) -> str:
        """Process data subject request"""
        pass
    
    @abstractmethod
    async def generate_compliance_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        pass


class GlobalComplianceManager:
    """
    Global Legal Compliance Manager
    
    Unified framework for managing compliance across multiple jurisdictions
    and regulations including GDPR, CCPA, DMCA, PIPEDA, LGPD, and PDPA.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("compliance.global")
        
        # Initialize compliance engines
        self.compliance_engines: Dict[ComplianceRegulation, ComplianceEngine] = {}
        self._initialize_engines()
        
        # Jurisdiction mapping
        self.jurisdiction_regulations = {
            "EU": [ComplianceRegulation.GDPR],
            "US": [ComplianceRegulation.CCPA, ComplianceRegulation.DMCA],
            "CA": [ComplianceRegulation.PIPEDA],
            "BR": [ComplianceRegulation.LGPD],
            "SG": [ComplianceRegulation.PDPA],
            "GLOBAL": [
                ComplianceRegulation.GDPR,
                ComplianceRegulation.CCPA,
                ComplianceRegulation.DMCA,
                ComplianceRegulation.PIPEDA,
                ComplianceRegulation.LGPD,
                ComplianceRegulation.PDPA
            ]
        }
        
        # Compliance requirements matrix
        self.compliance_requirements = self._initialize_compliance_requirements()
        
        self.logger.info("Global Compliance Manager initialized successfully")
    
    def _initialize_engines(self):
        """Initialize individual compliance engines"""
        try:
            # GDPR compliance engine
            if GDPRComplianceManager:
                self.compliance_engines[ComplianceRegulation.GDPR] = GDPRComplianceManager()
            
            # DMCA compliance engine
            if EnterpriseDMCACompliance:
                self.compliance_engines[ComplianceRegulation.DMCA] = EnterpriseDMCACompliance()
            
            # Import and initialize other compliance engines
            from .ccpa_compliance import CCPAComplianceManager
            from .pipeda_compliance import PIPEDAComplianceManager
            from .lgpd_compliance import LGPDComplianceManager
            from .pdpa_compliance import PDPAComplianceManager
            
            self.compliance_engines[ComplianceRegulation.CCPA] = CCPAComplianceManager()
            self.compliance_engines[ComplianceRegulation.PIPEDA] = PIPEDAComplianceManager()
            self.compliance_engines[ComplianceRegulation.LGPD] = LGPDComplianceManager()
            self.compliance_engines[ComplianceRegulation.PDPA] = PDPAComplianceManager()
            
            self.logger.info(f"Initialized {len(self.compliance_engines)} compliance engines")
            
        except ImportError as e:
            self.logger.warning(f"Some compliance engines not available: {e}")
    
    def _initialize_compliance_requirements(self) -> List[ComplianceRequirement]:
        """Initialize compliance requirements matrix"""
        requirements = [
            # GDPR Requirements
            ComplianceRequirement(
                regulation=ComplianceRegulation.GDPR,
                requirement_id="gdpr_001",
                title="Consent Management",
                description="Obtain explicit consent for data processing",
                jurisdiction="EU",
                penalty_amount=20000000.0,  # €20M or 4% of annual revenue
                verification_method="consent_audit"
            ),
            ComplianceRequirement(
                regulation=ComplianceRegulation.GDPR,
                requirement_id="gdpr_002",
                title="Right to Erasure",
                description="Implement right to be forgotten",
                jurisdiction="EU",
                penalty_amount=20000000.0,
                verification_method="erasure_audit"
            ),
            
            # CCPA Requirements
            ComplianceRequirement(
                regulation=ComplianceRegulation.CCPA,
                requirement_id="ccpa_001",
                title="Right to Know",
                description="Provide information about personal data collection",
                jurisdiction="CA-US",
                penalty_amount=7500.0,  # $7,500 per violation
                verification_method="disclosure_audit"
            ),
            ComplianceRequirement(
                regulation=ComplianceRegulation.CCPA,
                requirement_id="ccpa_002",
                title="Right to Delete",
                description="Allow consumers to delete personal information",
                jurisdiction="CA-US",
                penalty_amount=7500.0,
                verification_method="deletion_audit"
            ),
            
            # DMCA Requirements
            ComplianceRequirement(
                regulation=ComplianceRegulation.DMCA,
                requirement_id="dmca_001",
                title="Safe Harbor Compliance",
                description="Implement DMCA safe harbor provisions",
                jurisdiction="US",
                verification_method="takedown_audit"
            ),
            
            # PIPEDA Requirements
            ComplianceRequirement(
                regulation=ComplianceRegulation.PIPEDA,
                requirement_id="pipeda_001",
                title="Consent Requirement",
                description="Obtain meaningful consent for data collection",
                jurisdiction="CA",
                verification_method="consent_review"
            ),
            
            # LGPD Requirements
            ComplianceRequirement(
                regulation=ComplianceRegulation.LGPD,
                requirement_id="lgpd_001",
                title="Data Protection Officer",
                description="Appoint Data Protection Officer",
                jurisdiction="BR",
                penalty_amount=50000000.0,  # R$50M
                verification_method="dpo_audit"
            ),
            
            # PDPA Requirements
            ComplianceRequirement(
                regulation=ComplianceRegulation.PDPA,
                requirement_id="pdpa_001",
                title="Data Protection Notification",
                description="Notify individuals about data collection",
                jurisdiction="SG",
                penalty_amount=1000000.0,  # S$1M
                verification_method="notification_audit"
            )
        ]
        
        return requirements
    
    async def determine_applicable_regulations(
        self, user_jurisdiction: str, business_operations: List[str] = None
    ) -> List[ComplianceRegulation]:
        """
        Determine which regulations apply to a user based on jurisdiction and operations
        
        Args:
            user_jurisdiction: User's jurisdiction (ISO country code)
            business_operations: List of jurisdictions where business operates
            
        Returns:
            List of applicable regulations
        """
        try:
            applicable_regulations = set()
            
            # Add regulations based on user jurisdiction
            if user_jurisdiction in self.jurisdiction_regulations:
                applicable_regulations.update(self.jurisdiction_regulations[user_jurisdiction])
            
            # Add EU regulations if user is in EU
            eu_countries = [
                "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
                "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
                "PL", "PT", "RO", "SK", "SI", "ES", "SE"
            ]
            if user_jurisdiction in eu_countries:
                applicable_regulations.add(ComplianceRegulation.GDPR)
            
            # Add US state-specific regulations
            if user_jurisdiction == "US":
                applicable_regulations.add(ComplianceRegulation.CCPA)
                applicable_regulations.add(ComplianceRegulation.DMCA)
            
            # Add regulations based on business operations
            if business_operations:
                for jurisdiction in business_operations:
                    if jurisdiction in self.jurisdiction_regulations:
                        applicable_regulations.update(
                            self.jurisdiction_regulations[jurisdiction]
                        )
            
            # Always include DMCA for content platforms
            applicable_regulations.add(ComplianceRegulation.DMCA)
            
            self.logger.info(
                f"Determined applicable regulations for {user_jurisdiction}: "
                f"{list(applicable_regulations)}"
            )
            
            return list(applicable_regulations)
            
        except Exception as e:
            self.logger.error(f"Error determining applicable regulations: {e}")
            # Return default minimal compliance set
            return [ComplianceRegulation.GDPR, ComplianceRegulation.DMCA]
    
    async def create_user_compliance_profile(
        self, user_id: int, user_jurisdiction: str
    ) -> UserComplianceProfile:
        """Create comprehensive compliance profile for user"""
        try:
            # Determine applicable regulations
            applicable_regulations = await self.determine_applicable_regulations(
                user_jurisdiction
            )
            
            # Initialize consent status for each regulation
            consent_status = {}
            for regulation in applicable_regulations:
                consent_status[regulation.value] = {
                    "essential": False,
                    "analytics": False,
                    "marketing": False,
                    "personalization": False
                }
            
            # Create profile
            profile = UserComplianceProfile(
                user_id=user_id,
                jurisdiction=user_jurisdiction,
                applicable_regulations=applicable_regulations,
                consent_status=consent_status,
                compliance_scores={reg.value: 0.0 for reg in applicable_regulations},
                risk_level="medium"  # Default to medium until assessment
            )
            
            self.logger.info(f"Created compliance profile for user {user_id}")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error creating compliance profile: {e}")
            raise
    
    async def check_global_compliance(self, user_id: int) -> Dict[str, Any]:
        """
        Perform comprehensive compliance check across all applicable regulations
        
        Args:
            user_id: User ID to check compliance for
            
        Returns:
            Global compliance status and scores
        """
        try:
            compliance_results = {
                "user_id": user_id,
                "overall_status": ComplianceStatus.COMPLIANT,
                "overall_score": 100.0,
                "regulation_results": {},
                "gaps": [],
                "recommendations": [],
                "last_checked": datetime.utcnow()
            }
            
            total_score = 0.0
            regulation_count = 0
            
            # Check compliance for each applicable regulation
            for regulation, engine in self.compliance_engines.items():
                try:
                    if hasattr(engine, 'check_compliance'):
                        result = await engine.check_compliance(user_id)
                        compliance_results["regulation_results"][regulation.value] = result
                        
                        # Extract score (assuming engines return score in result)
                        score = result.get("compliance_score", 0.0)
                        total_score += score
                        regulation_count += 1
                        
                        # Check for gaps
                        if score < 80.0:
                            compliance_results["gaps"].append(
                                f"{regulation.value.upper()} compliance below threshold: {score:.1f}%"
                            )
                    
                except Exception as e:
                    self.logger.error(f"Error checking {regulation.value} compliance: {e}")
                    compliance_results["regulation_results"][regulation.value] = {
                        "error": str(e),
                        "compliance_score": 0.0
                    }
                    compliance_results["gaps"].append(
                        f"{regulation.value.upper()} compliance check failed"
                    )
            
            # Calculate overall score
            if regulation_count > 0:
                compliance_results["overall_score"] = total_score / regulation_count
            
            # Determine overall status
            overall_score = compliance_results["overall_score"]
            if overall_score >= 90.0:
                compliance_results["overall_status"] = ComplianceStatus.COMPLIANT
            elif overall_score >= 70.0:
                compliance_results["overall_status"] = ComplianceStatus.PARTIAL_COMPLIANCE
            else:
                compliance_results["overall_status"] = ComplianceStatus.NON_COMPLIANT
            
            # Generate recommendations
            if compliance_results["gaps"]:
                compliance_results["recommendations"] = [
                    "Review and update consent management processes",
                    "Implement missing data subject request handlers",
                    "Update privacy policies for applicable jurisdictions",
                    "Conduct compliance training for staff"
                ]
            
            self.logger.info(
                f"Global compliance check completed for user {user_id}: "
                f"{overall_score:.1f}% ({compliance_results['overall_status']})"
            )
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Global compliance check failed: {e}")
            raise
    
    async def process_universal_data_subject_request(
        self,
        user_id: int,
        request_type: DataSubjectRight,
        jurisdiction: str,
        details: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Process data subject request across all applicable regulations
        
        Args:
            user_id: User making the request
            request_type: Type of request
            jurisdiction: User's jurisdiction
            details: Additional request details
            
        Returns:
            Dictionary mapping regulation to request ID
        """
        try:
            request_ids = {}
            details = details or {}
            
            # Determine applicable regulations
            applicable_regulations = await self.determine_applicable_regulations(jurisdiction)
            
            # Process request for each applicable regulation
            for regulation in applicable_regulations:
                engine = self.compliance_engines.get(regulation)
                if engine and hasattr(engine, 'process_data_subject_request'):
                    try:
                        request_id = await engine.process_data_subject_request(
                            user_id, request_type, details
                        )
                        request_ids[regulation.value] = request_id
                        
                    except Exception as e:
                        self.logger.error(
                            f"Error processing {request_type.value} request "
                            f"for {regulation.value}: {e}"
                        )
                        request_ids[regulation.value] = f"ERROR: {str(e)}"
            
            self.logger.info(
                f"Processed {request_type.value} request for user {user_id} "
                f"across {len(request_ids)} regulations"
            )
            
            return request_ids
            
        except Exception as e:
            self.logger.error(f"Universal data subject request processing failed: {e}")
            raise
    
    async def generate_global_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        jurisdictions: List[str] = None
    ) -> GlobalComplianceReport:
        """
        Generate comprehensive global compliance report
        
        Args:
            start_date: Report period start date
            end_date: Report period end date
            jurisdictions: Specific jurisdictions to include
            
        Returns:
            Global compliance report
        """
        try:
            report_id = f"global_compliance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            self.logger.info(f"Generating global compliance report: {report_id}")
            
            regulation_scores = {}
            all_gaps = []
            all_recommendations = []
            total_enforcement_actions = 0
            
            # Generate reports for each regulation
            for regulation, engine in self.compliance_engines.items():
                if hasattr(engine, 'generate_compliance_report'):
                    try:
                        reg_report = await engine.generate_compliance_report(
                            start_date, end_date
                        )
                        
                        # Extract metrics from regulation-specific report
                        if isinstance(reg_report, dict):
                            score = reg_report.get("compliance_rate", 0.0) * 100
                            regulation_scores[regulation.value] = score
                            
                            # Extract enforcement actions
                            enforcement = reg_report.get("enforcement_actions", 0)
                            if isinstance(enforcement, (int, float)):
                                total_enforcement_actions += enforcement
                        
                    except Exception as e:
                        self.logger.error(
                            f"Error generating {regulation.value} report: {e}"
                        )
                        regulation_scores[regulation.value] = 0.0
            
            # Calculate overall compliance score
            overall_score = (
                sum(regulation_scores.values()) / len(regulation_scores)
                if regulation_scores else 0.0
            )
            
            # Identify gaps and recommendations
            for regulation, score in regulation_scores.items():
                if score < 80.0:
                    all_gaps.append(
                        f"{regulation.upper()} compliance below 80%: {score:.1f}%"
                    )
                    all_recommendations.append(
                        f"Improve {regulation.upper()} compliance processes"
                    )
            
            # Create comprehensive report
            report = GlobalComplianceReport(
                report_id=report_id,
                generated_at=datetime.utcnow(),
                reporting_period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                overall_compliance_score=overall_score,
                regulation_scores=regulation_scores,
                compliance_gaps=all_gaps[:10],  # Limit to top 10 gaps
                recommendations=list(set(all_recommendations))[:10],  # Unique top 10
                enforcement_actions=total_enforcement_actions
            )
            
            self.logger.info(
                f"Global compliance report generated: {report_id} "
                f"(Overall score: {overall_score:.1f}%)"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Global compliance report generation failed: {e}")
            raise
    
    async def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time compliance dashboard data"""
        try:
            dashboard_data = {
                "timestamp": datetime.utcnow(),
                "regulations_monitored": len(self.compliance_engines),
                "overall_health": "healthy",
                "regulation_status": {},
                "recent_alerts": [],
                "compliance_trends": {},
                "jurisdiction_coverage": list(self.jurisdiction_regulations.keys())
            }
            
            # Get status for each regulation
            for regulation in self.compliance_engines.keys():
                dashboard_data["regulation_status"][regulation.value] = {
                    "status": "operational",
                    "last_check": datetime.utcnow(),
                    "active_requests": 0,
                    "compliance_score": 85.0  # Placeholder
                }
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}
    
    def get_supported_regulations(self) -> List[str]:
        """Get list of supported compliance regulations"""
        return [reg.value for reg in ComplianceRegulation]
    
    def get_jurisdiction_regulations(self, jurisdiction: str) -> List[str]:
        """Get applicable regulations for a jurisdiction"""
        regulations = self.jurisdiction_regulations.get(jurisdiction, [])
        return [reg.value for reg in regulations]


# Export for use in other modules
__all__ = [
    "GlobalComplianceManager",
    "ComplianceRegulation", 
    "ComplianceStatus",
    "DataSubjectRight",
    "UserComplianceProfile",
    "GlobalComplianceReport"
]