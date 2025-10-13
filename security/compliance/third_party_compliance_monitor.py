"""
🛡️ Third-Party Compliance Monitor - IA Chérie Creator Economy

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

ENTERPRISE FEATURES:
- Vendor compliance assessment automation
- Third-party certification monitoring
- SLA compliance tracking
- Security posture evaluation
- Risk-based vendor scoring
- Contract compliance validation
- Audit trail management
- Multi-jurisdiction compliance
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import uuid
from contextlib import asynccontextmanager
import aiohttp
import asyncpg
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VendorRiskLevel(Enum):
    """Third-party vendor risk levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

class ComplianceStatus(Enum):
    """Vendor compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial_compliance"
    PENDING_REVIEW = "pending_review"
    SUSPENDED = "suspended"

class CertificationType(Enum):
    """Third-party certification types"""
    SOC2_TYPE_II = "soc2_type_ii"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    GDPR_CERTIFIED = "gdpr_certified"
    HIPAA = "hipaa"
    FedRAMP = "fedramp"
    CCPA_COMPLIANT = "ccpa_compliant"

@dataclass
class VendorProfile:
    """Third-party vendor profile"""
    vendor_id: str
    name: str
    category: str
    risk_level: VendorRiskLevel
    compliance_status: ComplianceStatus
    certifications: List[CertificationType]
    contract_start: datetime
    contract_end: datetime
    last_assessment: Optional[datetime]
    next_assessment: datetime
    sla_requirements: Dict[str, Any]
    data_processing: bool
    creator_data_access: bool
    financial_data_access: bool
    geographic_presence: List[str]
    contact_info: Dict[str, str]
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

@dataclass
class ComplianceAssessment:
    """Vendor compliance assessment"""
    assessment_id: str
    vendor_id: str
    assessment_type: str
    score: float
    risk_factors: List[str]
    compliance_gaps: List[str]
    remediation_actions: List[str]
    assessor: str
    assessment_date: datetime
    next_review_date: datetime
    evidence_documents: List[str]
    automated_checks: Dict[str, bool]
    manual_validation: Dict[str, str]

@dataclass
class SLAMonitoring:
    """SLA monitoring and compliance tracking"""
    monitoring_id: str
    vendor_id: str
    sla_metric: str
    target_value: float
    actual_value: float
    measurement_period: str
    compliance_percentage: float
    violations_count: int
    last_violation: Optional[datetime]
    penalty_applied: bool
    escalation_triggered: bool
    monitoring_date: datetime

class ThirdPartyComplianceMonitor:
    """
    🛡️ Third-Party Compliance Monitor - Enterprise Vendor Management
    
    COMPREHENSIVE FEATURES:
    - Automated vendor compliance assessments
    - Real-time SLA monitoring and violation detection
    - Certification tracking and renewal management
    - Risk-based vendor scoring and categorization
    - Contract compliance validation
    - Multi-jurisdiction regulatory compliance
    - Audit trail and evidence management
    - Creator economy specific controls
    """

    def __init__(self, db_connection_string: str, encryption_key: Optional[str] = None):
        """Initialize third-party compliance monitor"""
        self.db_connection_string = db_connection_string
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key.encode() if isinstance(self.encryption_key, str) 
                                 else self.encryption_key)
        self.vendor_profiles: Dict[str, VendorProfile] = {}
        self.assessment_cache: Dict[str, ComplianceAssessment] = {}
        self.sla_monitoring: Dict[str, SLAMonitoring] = {}
        self.compliance_rules = self._initialize_compliance_rules()
        self.risk_matrix = self._initialize_risk_matrix()
        
        logger.info("Third-Party Compliance Monitor initialized successfully")

    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data"""
        password = b"iacherie_third_party_compliance_2025"
        salt = b"iacherie_vendor_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def _initialize_compliance_rules(self) -> Dict[str, Any]:
        """Initialize compliance rules for vendor assessment"""
        return {
            "creator_data_handling": {
                "required_certifications": [CertificationType.SOC2_TYPE_II, CertificationType.ISO27001],
                "data_residency_requirements": True,
                "encryption_requirements": {"at_rest": True, "in_transit": True},
                "access_controls": {"mfa_required": True, "rbac_implemented": True},
                "audit_logging": {"enabled": True, "retention_period": "7_years"}
            },
            "financial_data_processing": {
                "required_certifications": [CertificationType.PCI_DSS, CertificationType.SOC2_TYPE_II],
                "compliance_frameworks": ["PCI-DSS", "SOX"],
                "segregation_of_duties": True,
                "transaction_monitoring": True,
                "fraud_detection": True
            },
            "privacy_compliance": {
                "gdpr_compliance": True,
                "ccpa_compliance": True,
                "data_subject_rights": True,
                "privacy_by_design": True,
                "consent_management": True,
                "breach_notification": {"sla": "72_hours"}
            },
            "sla_requirements": {
                "availability": {"target": 99.9, "measurement": "monthly"},
                "response_time": {"target": 500, "unit": "milliseconds"},
                "data_recovery": {"rpo": "4_hours", "rto": "8_hours"},
                "security_incidents": {"notification": "1_hour", "resolution": "24_hours"}
            }
        }

    def _initialize_risk_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Initialize risk assessment matrix"""
        return {
            "data_sensitivity": {
                "creator_personal_data": {"risk_score": 9, "weight": 0.3},
                "financial_transactions": {"risk_score": 10, "weight": 0.25},
                "content_metadata": {"risk_score": 6, "weight": 0.2},
                "analytics_data": {"risk_score": 4, "weight": 0.15},
                "public_content": {"risk_score": 2, "weight": 0.1}
            },
            "access_level": {
                "full_database_access": {"risk_score": 10, "weight": 0.4},
                "api_access_only": {"risk_score": 6, "weight": 0.3},
                "read_only_access": {"risk_score": 3, "weight": 0.2},
                "no_data_access": {"risk_score": 1, "weight": 0.1}
            },
            "geographic_risk": {
                "high_risk_jurisdictions": {"risk_score": 8, "weight": 0.3},
                "medium_risk_jurisdictions": {"risk_score": 5, "weight": 0.3},
                "low_risk_jurisdictions": {"risk_score": 2, "weight": 0.4}
            },
            "business_criticality": {
                "mission_critical": {"risk_score": 10, "weight": 0.5},
                "business_important": {"risk_score": 7, "weight": 0.3},
                "supporting_service": {"risk_score": 4, "weight": 0.2}
            }
        }

    async def register_vendor(self, vendor_profile: VendorProfile) -> str:
        """Register new third-party vendor"""
        try:
            vendor_id = str(uuid.uuid4())
            vendor_profile.vendor_id = vendor_id
            
            # Encrypt sensitive information
            encrypted_contact = self._encrypt_data(json.dumps(vendor_profile.contact_info))
            
            # Calculate initial risk score
            risk_score = await self._calculate_vendor_risk_score(vendor_profile)
            
            # Store vendor profile
            self.vendor_profiles[vendor_id] = vendor_profile
            
            # Schedule initial assessment
            await self._schedule_initial_assessment(vendor_id)
            
            # Log vendor registration
            await self._log_vendor_activity(
                vendor_id,
                "vendor_registered",
                {"risk_score": risk_score, "certifications": [cert.value for cert in vendor_profile.certifications]}
            )
            
            logger.info(f"Vendor registered successfully: {vendor_profile.name} (ID: {vendor_id})")
            return vendor_id
            
        except Exception as e:
            logger.error(f"Error registering vendor: {str(e)}")
            raise

    async def conduct_compliance_assessment(self, vendor_id: str, assessment_type: str = "comprehensive") -> ComplianceAssessment:
        """Conduct comprehensive compliance assessment"""
        try:
            vendor = self.vendor_profiles.get(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor not found: {vendor_id}")
            
            assessment_id = str(uuid.uuid4())
            assessment_date = datetime.utcnow()
            
            # Perform automated checks
            automated_checks = await self._perform_automated_checks(vendor)
            
            # Calculate compliance score
            compliance_score = await self._calculate_compliance_score(vendor, automated_checks)
            
            # Identify risk factors
            risk_factors = await self._identify_risk_factors(vendor, automated_checks)
            
            # Identify compliance gaps
            compliance_gaps = await self._identify_compliance_gaps(vendor, automated_checks)
            
            # Generate remediation actions
            remediation_actions = await self._generate_remediation_actions(compliance_gaps)
            
            # Create assessment
            assessment = ComplianceAssessment(
                assessment_id=assessment_id,
                vendor_id=vendor_id,
                assessment_type=assessment_type,
                score=compliance_score,
                risk_factors=risk_factors,
                compliance_gaps=compliance_gaps,
                remediation_actions=remediation_actions,
                assessor="automated_system",
                assessment_date=assessment_date,
                next_review_date=assessment_date + timedelta(days=90),
                evidence_documents=[],
                automated_checks=automated_checks,
                manual_validation={}
            )
            
            # Store assessment
            self.assessment_cache[assessment_id] = assessment
            
            # Update vendor compliance status
            await self._update_vendor_compliance_status(vendor_id, assessment)
            
            logger.info(f"Compliance assessment completed for vendor {vendor_id}: Score {compliance_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error conducting compliance assessment: {str(e)}")
            raise

    async def monitor_sla_compliance(self, vendor_id: str, metrics: Dict[str, float]) -> SLAMonitoring:
        """Monitor SLA compliance and detect violations"""
        try:
            vendor = self.vendor_profiles.get(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor not found: {vendor_id}")
            
            monitoring_results = []
            
            for metric_name, actual_value in metrics.items():
                if metric_name in vendor.sla_requirements:
                    target_value = vendor.sla_requirements[metric_name].get("target", 0)
                    
                    # Calculate compliance percentage
                    if metric_name == "availability":
                        compliance_percentage = min(100, (actual_value / target_value) * 100)
                    elif metric_name == "response_time":
                        compliance_percentage = max(0, 100 - ((actual_value - target_value) / target_value) * 100)
                    else:
                        compliance_percentage = min(100, (actual_value / target_value) * 100)
                    
                    # Check for violations
                    violations_count = 1 if compliance_percentage < 95 else 0
                    last_violation = datetime.utcnow() if violations_count > 0 else None
                    
                    # Determine if penalty should be applied
                    penalty_applied = compliance_percentage < 90
                    escalation_triggered = compliance_percentage < 85
                    
                    monitoring = SLAMonitoring(
                        monitoring_id=str(uuid.uuid4()),
                        vendor_id=vendor_id,
                        sla_metric=metric_name,
                        target_value=target_value,
                        actual_value=actual_value,
                        measurement_period="monthly",
                        compliance_percentage=compliance_percentage,
                        violations_count=violations_count,
                        last_violation=last_violation,
                        penalty_applied=penalty_applied,
                        escalation_triggered=escalation_triggered,
                        monitoring_date=datetime.utcnow()
                    )
                    
                    monitoring_results.append(monitoring)
                    self.sla_monitoring[monitoring.monitoring_id] = monitoring
                    
                    # Trigger alerts if necessary
                    if escalation_triggered:
                        await self._trigger_sla_escalation(vendor_id, metric_name, compliance_percentage)
            
            logger.info(f"SLA monitoring completed for vendor {vendor_id}: {len(monitoring_results)} metrics evaluated")
            return monitoring_results[0] if monitoring_results else None
            
        except Exception as e:
            logger.error(f"Error monitoring SLA compliance: {str(e)}")
            raise

    async def track_certifications(self, vendor_id: str) -> Dict[str, Any]:
        """Track vendor certifications and renewal dates"""
        try:
            vendor = self.vendor_profiles.get(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor not found: {vendor_id}")
            
            certification_status = {}
            expiring_certifications = []
            
            for certification in vendor.certifications:
                # Mock certification expiry tracking (in real implementation, integrate with certification bodies)
                expiry_date = datetime.utcnow() + timedelta(days=365)  # Example: 1 year validity
                days_until_expiry = (expiry_date - datetime.utcnow()).days
                
                status = {
                    "certification": certification.value,
                    "status": "valid" if days_until_expiry > 30 else "expiring_soon",
                    "expiry_date": expiry_date.isoformat(),
                    "days_until_expiry": days_until_expiry,
                    "renewal_required": days_until_expiry <= 60
                }
                
                certification_status[certification.value] = status
                
                if days_until_expiry <= 60:
                    expiring_certifications.append(certification.value)
            
            # Check for missing required certifications
            required_certs = self._get_required_certifications(vendor)
            missing_certifications = [cert for cert in required_certs if cert not in vendor.certifications]
            
            result = {
                "vendor_id": vendor_id,
                "certification_status": certification_status,
                "expiring_certifications": expiring_certifications,
                "missing_certifications": [cert.value for cert in missing_certifications],
                "overall_certification_compliance": len(missing_certifications) == 0 and len(expiring_certifications) == 0
            }
            
            logger.info(f"Certification tracking completed for vendor {vendor_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking certifications: {str(e)}")
            raise

    async def validate_contract_compliance(self, vendor_id: str) -> Dict[str, Any]:
        """Validate vendor contract compliance"""
        try:
            vendor = self.vendor_profiles.get(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor not found: {vendor_id}")
            
            compliance_checks = {
                "contract_validity": {
                    "valid": datetime.utcnow() < vendor.contract_end,
                    "days_remaining": (vendor.contract_end - datetime.utcnow()).days,
                    "renewal_required": (vendor.contract_end - datetime.utcnow()).days <= 90
                },
                "data_processing_agreement": {
                    "required": vendor.data_processing,
                    "in_place": True,  # Mock - integrate with contract management system
                    "compliant": True
                },
                "security_requirements": {
                    "encryption_mandatory": True,
                    "access_controls_defined": True,
                    "incident_response_plan": True,
                    "audit_rights_reserved": True
                },
                "liability_coverage": {
                    "adequate_insurance": True,  # Mock - integrate with insurance verification
                    "liability_limits": "sufficient",
                    "cyber_insurance": True
                },
                "termination_clauses": {
                    "data_return_procedures": True,
                    "notification_period": "30_days",
                    "penalty_clauses": True
                }
            }
            
            # Calculate overall contract compliance score
            compliance_items = []
            for category, checks in compliance_checks.items():
                if isinstance(checks, dict):
                    category_compliance = all(
                        value is True or value == "sufficient" or isinstance(value, (int, str))
                        for value in checks.values()
                    )
                    compliance_items.append(category_compliance)
            
            overall_compliance = sum(compliance_items) / len(compliance_items) * 100 if compliance_items else 0
            
            result = {
                "vendor_id": vendor_id,
                "contract_compliance_checks": compliance_checks,
                "overall_compliance_score": overall_compliance,
                "compliance_status": "compliant" if overall_compliance >= 95 else "non_compliant",
                "review_date": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Contract compliance validation completed for vendor {vendor_id}: {overall_compliance:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error validating contract compliance: {str(e)}")
            raise

    async def generate_vendor_risk_report(self, vendor_id: str) -> Dict[str, Any]:
        """Generate comprehensive vendor risk report"""
        try:
            vendor = self.vendor_profiles.get(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor not found: {vendor_id}")
            
            # Get latest assessment
            latest_assessment = await self._get_latest_assessment(vendor_id)
            
            # Get SLA compliance data
            sla_compliance = await self._get_sla_compliance_summary(vendor_id)
            
            # Get certification status
            certification_status = await self.track_certifications(vendor_id)
            
            # Get contract compliance
            contract_compliance = await self.validate_contract_compliance(vendor_id)
            
            # Calculate overall risk score
            overall_risk_score = await self._calculate_vendor_risk_score(vendor)
            
            # Generate risk recommendations
            risk_recommendations = await self._generate_risk_recommendations(vendor, latest_assessment)
            
            report = {
                "vendor_id": vendor_id,
                "vendor_name": vendor.name,
                "report_date": datetime.utcnow().isoformat(),
                "risk_assessment": {
                    "overall_risk_level": vendor.risk_level.value,
                    "risk_score": overall_risk_score,
                    "risk_factors": latest_assessment.risk_factors if latest_assessment else [],
                    "risk_recommendations": risk_recommendations
                },
                "compliance_summary": {
                    "compliance_status": vendor.compliance_status.value,
                    "compliance_score": latest_assessment.score if latest_assessment else 0,
                    "compliance_gaps": latest_assessment.compliance_gaps if latest_assessment else []
                },
                "sla_performance": sla_compliance,
                "certification_status": certification_status,
                "contract_compliance": contract_compliance,
                "next_review_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
                "action_items": await self._generate_action_items(vendor, latest_assessment)
            }
            
            logger.info(f"Vendor risk report generated for {vendor_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating vendor risk report: {str(e)}")
            raise

    # Helper methods
    async def _perform_automated_checks(self, vendor: VendorProfile) -> Dict[str, bool]:
        """Perform automated compliance checks"""
        checks = {
            "has_required_certifications": len(vendor.certifications) >= 2,
            "contract_current": datetime.utcnow() < vendor.contract_end,
            "recent_assessment": vendor.last_assessment and 
                               (datetime.utcnow() - vendor.last_assessment).days <= 90,
            "data_processing_controls": vendor.data_processing,
            "geographic_compliance": len(vendor.geographic_presence) > 0,
            "contact_information_complete": bool(vendor.contact_info),
            "risk_level_appropriate": vendor.risk_level in [VendorRiskLevel.LOW, VendorRiskLevel.MEDIUM]
        }
        return checks

    async def _calculate_compliance_score(self, vendor: VendorProfile, automated_checks: Dict[str, bool]) -> float:
        """Calculate compliance score based on various factors"""
        base_score = sum(automated_checks.values()) / len(automated_checks) * 100
        
        # Certification bonus
        cert_bonus = len(vendor.certifications) * 5
        
        # Risk level adjustment
        risk_adjustment = {
            VendorRiskLevel.MINIMAL: 10,
            VendorRiskLevel.LOW: 5,
            VendorRiskLevel.MEDIUM: 0,
            VendorRiskLevel.HIGH: -10,
            VendorRiskLevel.CRITICAL: -20
        }.get(vendor.risk_level, 0)
        
        final_score = min(100, base_score + cert_bonus + risk_adjustment)
        return round(final_score, 2)

    async def _calculate_vendor_risk_score(self, vendor: VendorProfile) -> float:
        """Calculate comprehensive vendor risk score"""
        risk_score = 0
        total_weight = 0
        
        # Data sensitivity risk
        if vendor.creator_data_access:
            risk_score += 9 * 0.3
            total_weight += 0.3
        if vendor.financial_data_access:
            risk_score += 10 * 0.25
            total_weight += 0.25
        
        # Certification risk (inverse)
        cert_risk = max(0, 5 - len(vendor.certifications)) * 2
        risk_score += cert_risk * 0.2
        total_weight += 0.2
        
        # Geographic risk
        high_risk_jurisdictions = ["CN", "RU", "IR", "KP"]  # Example
        geo_risk = any(country in high_risk_jurisdictions for country in vendor.geographic_presence)
        if geo_risk:
            risk_score += 8 * 0.25
        else:
            risk_score += 2 * 0.25
        total_weight += 0.25
        
        final_score = risk_score / total_weight if total_weight > 0 else 5
        return round(final_score, 2)

    async def _identify_risk_factors(self, vendor: VendorProfile, automated_checks: Dict[str, bool]) -> List[str]:
        """Identify vendor risk factors"""
        risk_factors = []
        
        if vendor.creator_data_access:
            risk_factors.append("Access to creator personal data")
        if vendor.financial_data_access:
            risk_factors.append("Access to financial transaction data")
        if not automated_checks.get("has_required_certifications", True):
            risk_factors.append("Missing required security certifications")
        if vendor.risk_level in [VendorRiskLevel.HIGH, VendorRiskLevel.CRITICAL]:
            risk_factors.append("High inherent risk classification")
        if not automated_checks.get("recent_assessment", True):
            risk_factors.append("Overdue compliance assessment")
        
        return risk_factors

    async def _identify_compliance_gaps(self, vendor: VendorProfile, automated_checks: Dict[str, bool]) -> List[str]:
        """Identify compliance gaps"""
        gaps = []
        
        for check_name, passed in automated_checks.items():
            if not passed:
                gap_descriptions = {
                    "has_required_certifications": "Missing required security certifications",
                    "contract_current": "Contract expired or expiring soon",
                    "recent_assessment": "Compliance assessment overdue",
                    "data_processing_controls": "Data processing controls not implemented",
                    "geographic_compliance": "Geographic presence not documented",
                    "contact_information_complete": "Incomplete contact information",
                    "risk_level_appropriate": "Risk level requires review"
                }
                if check_name in gap_descriptions:
                    gaps.append(gap_descriptions[check_name])
        
        return gaps

    async def _generate_remediation_actions(self, compliance_gaps: List[str]) -> List[str]:
        """Generate remediation actions for compliance gaps"""
        actions = []
        
        gap_to_action = {
            "Missing required security certifications": "Obtain SOC 2 Type II and ISO 27001 certifications",
            "Contract expired or expiring soon": "Renew contract with updated security terms",
            "Compliance assessment overdue": "Schedule comprehensive compliance assessment",
            "Data processing controls not implemented": "Implement data processing agreement and controls",
            "Geographic presence not documented": "Document and validate geographic presence",
            "Incomplete contact information": "Update emergency contact information",
            "Risk level requires review": "Conduct risk level reassessment"
        }
        
        for gap in compliance_gaps:
            if gap in gap_to_action:
                actions.append(gap_to_action[gap])
        
        return actions

    def _get_required_certifications(self, vendor: VendorProfile) -> List[CertificationType]:
        """Get required certifications based on vendor profile"""
        required = []
        
        if vendor.creator_data_access or vendor.data_processing:
            required.extend([CertificationType.SOC2_TYPE_II, CertificationType.ISO27001])
        
        if vendor.financial_data_access:
            required.append(CertificationType.PCI_DSS)
        
        # Remove duplicates
        return list(set(required))

    async def _get_latest_assessment(self, vendor_id: str) -> Optional[ComplianceAssessment]:
        """Get latest compliance assessment for vendor"""
        vendor_assessments = [
            assessment for assessment in self.assessment_cache.values()
            if assessment.vendor_id == vendor_id
        ]
        
        if not vendor_assessments:
            return None
        
        return max(vendor_assessments, key=lambda x: x.assessment_date)

    async def _get_sla_compliance_summary(self, vendor_id: str) -> Dict[str, Any]:
        """Get SLA compliance summary for vendor"""
        vendor_sla_data = [
            sla for sla in self.sla_monitoring.values()
            if sla.vendor_id == vendor_id
        ]
        
        if not vendor_sla_data:
            return {"overall_compliance": 100, "violations": 0, "metrics": {}}
        
        total_compliance = sum(sla.compliance_percentage for sla in vendor_sla_data)
        average_compliance = total_compliance / len(vendor_sla_data)
        total_violations = sum(sla.violations_count for sla in vendor_sla_data)
        
        return {
            "overall_compliance": round(average_compliance, 2),
            "violations": total_violations,
            "metrics": {sla.sla_metric: sla.compliance_percentage for sla in vendor_sla_data}
        }

    async def _schedule_initial_assessment(self, vendor_id: str):
        """Schedule initial compliance assessment"""
        # In a real implementation, this would integrate with a scheduling system
        logger.info(f"Initial assessment scheduled for vendor {vendor_id}")

    async def _update_vendor_compliance_status(self, vendor_id: str, assessment: ComplianceAssessment):
        """Update vendor compliance status based on assessment"""
        vendor = self.vendor_profiles[vendor_id]
        
        if assessment.score >= 95:
            vendor.compliance_status = ComplianceStatus.COMPLIANT
        elif assessment.score >= 80:
            vendor.compliance_status = ComplianceStatus.PARTIAL
        elif assessment.score >= 60:
            vendor.compliance_status = ComplianceStatus.PENDING_REVIEW
        else:
            vendor.compliance_status = ComplianceStatus.NON_COMPLIANT
        
        vendor.last_assessment = assessment.assessment_date
        vendor.updated_at = datetime.utcnow()

    async def _trigger_sla_escalation(self, vendor_id: str, metric_name: str, compliance_percentage: float):
        """Trigger SLA escalation for violations"""
        logger.warning(f"SLA escalation triggered for vendor {vendor_id}: {metric_name} at {compliance_percentage:.1f}%")
        # In a real implementation, this would send alerts to stakeholders

    async def _generate_risk_recommendations(self, vendor: VendorProfile, assessment: Optional[ComplianceAssessment]) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if vendor.risk_level in [VendorRiskLevel.HIGH, VendorRiskLevel.CRITICAL]:
            recommendations.append("Implement enhanced monitoring and controls")
            recommendations.append("Require additional security certifications")
        
        if vendor.creator_data_access:
            recommendations.append("Implement data minimization and access controls")
            recommendations.append("Regular privacy impact assessments")
        
        if assessment and assessment.score < 90:
            recommendations.append("Address compliance gaps immediately")
            recommendations.append("Increase assessment frequency")
        
        return recommendations

    async def _generate_action_items(self, vendor: VendorProfile, assessment: Optional[ComplianceAssessment]) -> List[str]:
        """Generate action items for vendor management"""
        actions = []
        
        # Contract-related actions
        if (vendor.contract_end - datetime.utcnow()).days <= 90:
            actions.append("Initiate contract renewal process")
        
        # Assessment-related actions
        if not vendor.last_assessment or (datetime.utcnow() - vendor.last_assessment).days > 90:
            actions.append("Schedule compliance assessment")
        
        # Certification-related actions
        required_certs = self._get_required_certifications(vendor)
        missing_certs = [cert for cert in required_certs if cert not in vendor.certifications]
        if missing_certs:
            actions.append(f"Obtain missing certifications: {', '.join([cert.value for cert in missing_certs])}")
        
        return actions

    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    async def _log_vendor_activity(self, vendor_id: str, activity_type: str, details: Dict[str, Any]):
        """Log vendor-related activities for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "vendor_id": vendor_id,
            "activity_type": activity_type,
            "details": details,
            "system": "third_party_compliance_monitor"
        }
        
        # In a real implementation, this would write to a secure audit log
        logger.info(f"Vendor activity logged: {json.dumps(log_entry)}")

# Creator Economy specific extensions
class CreatorVendorManager(ThirdPartyComplianceMonitor):
    """Extended third-party compliance for creator economy specific needs"""
    
    def __init__(self, db_connection_string: str, encryption_key: Optional[str] = None):
        super().__init__(db_connection_string, encryption_key)
        self.creator_specific_rules = self._initialize_creator_rules()
    
    def _initialize_creator_rules(self) -> Dict[str, Any]:
        """Initialize creator economy specific compliance rules"""
        return {
            "content_moderation_vendors": {
                "ai_bias_testing": True,
                "content_appeal_process": True,
                "creator_rights_protection": True,
                "transparency_reporting": True
            },
            "payment_processors": {
                "creator_payout_protection": True,
                "multi_currency_support": True,
                "fee_transparency": True,
                "dispute_resolution": True
            },
            "analytics_providers": {
                "creator_consent_required": True,
                "data_anonymization": True,
                "opt_out_mechanisms": True,
                "audience_privacy_protection": True
            }
        }
    
    async def assess_creator_impact(self, vendor_id: str) -> Dict[str, Any]:
        """Assess vendor impact on creator experience and rights"""
        vendor = self.vendor_profiles.get(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor not found: {vendor_id}")
        
        impact_assessment = {
            "creator_data_exposure": vendor.creator_data_access,
            "content_processing": vendor.category in ["content_moderation", "analytics", "ai_processing"],
            "revenue_impact": vendor.category in ["payment_processing", "advertising", "monetization"],
            "creator_control": {
                "data_portability": True,  # Mock assessment
                "consent_granularity": True,
                "opt_out_available": True
            },
            "transparency_score": 85,  # Mock score
            "creator_feedback_rating": 4.2  # Mock rating
        }
        
        return impact_assessment

# Example usage and testing
async def main():
    """Example usage of Third-Party Compliance Monitor"""
    
    # Initialize monitor
    monitor = ThirdPartyComplianceMonitor("postgresql://localhost/compliance")
    
    # Create example vendor profile
    vendor_profile = VendorProfile(
        vendor_id="",  # Will be generated
        name="CreatorAnalytics Pro",
        category="analytics_provider",
        risk_level=VendorRiskLevel.MEDIUM,
        compliance_status=ComplianceStatus.PENDING_REVIEW,
        certifications=[CertificationType.SOC2_TYPE_II, CertificationType.ISO27001],
        contract_start=datetime.utcnow(),
        contract_end=datetime.utcnow() + timedelta(days=365),
        last_assessment=None,
        next_assessment=datetime.utcnow() + timedelta(days=30),
        sla_requirements={
            "availability": {"target": 99.9},
            "response_time": {"target": 500}
        },
        data_processing=True,
        creator_data_access=True,
        financial_data_access=False,
        geographic_presence=["US", "EU", "CA"],
        contact_info={
            "primary_contact": "security@creatoranalytics.com",
            "emergency_contact": "+1-555-0123"
        }
    )
    
    try:
        # Register vendor
        vendor_id = await monitor.register_vendor(vendor_profile)
        print(f"Vendor registered: {vendor_id}")
        
        # Conduct compliance assessment
        assessment = await monitor.conduct_compliance_assessment(vendor_id)
        print(f"Assessment completed with score: {assessment.score}")
        
        # Monitor SLA compliance
        sla_metrics = {"availability": 99.8, "response_time": 450}
        sla_monitoring = await monitor.monitor_sla_compliance(vendor_id, sla_metrics)
        print(f"SLA monitoring completed: {sla_monitoring.compliance_percentage}% compliance")
        
        # Track certifications
        cert_status = await monitor.track_certifications(vendor_id)
        print(f"Certification tracking: {cert_status['overall_certification_compliance']}")
        
        # Generate risk report
        risk_report = await monitor.generate_vendor_risk_report(vendor_id)
        print(f"Risk report generated: Overall risk level {risk_report['risk_assessment']['overall_risk_level']}")
        
    except Exception as e:
        print(f"Error in example usage: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())