"""
Compliance Incident Handler for PagerDuty - IA Chérie Platform
Regulatory compliance and audit incident management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

logger = logging.getLogger(__name__)


class ComplianceFramework(Enum):
    """Compliance frameworks for Creator Economy"""
    GDPR = "gdpr"                    # General Data Protection Regulation
    CCPA = "ccpa"                    # California Consumer Privacy Act
    COPPA = "coppa"                  # Children's Online Privacy Protection
    SOX = "sox"                      # Sarbanes-Oxley Act
    PCI_DSS = "pci_dss"             # Payment Card Industry Data Security
    HIPAA = "hipaa"                  # Health Insurance Portability (if health content)
    FTC_GUIDELINES = "ftc"           # Federal Trade Commission Guidelines
    EU_COPYRIGHT = "eu_copyright"    # EU Copyright Directive
    DMCA = "dmca"                    # Digital Millennium Copyright Act
    CAN_SPAM = "can_spam"           # Controlling Assault of Non-Solicited Pornography
    FERPA = "ferpa"                  # Family Educational Rights and Privacy


class IncidentSeverity(Enum):
    """Compliance incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"
    AUDIT_PENDING = "audit_pending"


class DataType(Enum):
    """Types of data for compliance"""
    PERSONAL_DATA = "personal_data"
    PAYMENT_DATA = "payment_data"
    CONTENT_DATA = "content_data"
    BEHAVIORAL_DATA = "behavioral_data"
    BIOMETRIC_DATA = "biometric_data"
    HEALTH_DATA = "health_data"
    MINOR_DATA = "minor_data"
    FINANCIAL_DATA = "financial_data"


@dataclass
class ComplianceRequirement:
    """Compliance requirement definition"""
    requirement_id: str
    framework: ComplianceFramework
    title: str
    description: str
    data_types: List[DataType]
    severity_level: IncidentSeverity
    max_response_time_hours: int
    notification_required: bool
    documentation_required: bool
    external_reporting_required: bool
    retention_period_days: int
    automated_checks_available: bool
    remediation_steps: List[str]
    legal_implications: str
    business_impact: str


@dataclass
class ComplianceIncident:
    """Compliance incident"""
    incident_id: str
    framework: ComplianceFramework
    requirement_id: str
    incident_type: str
    severity: IncidentSeverity
    title: str
    description: str
    affected_data_types: List[DataType]
    affected_users_count: int
    affected_creators_count: int
    detection_method: str
    detection_timestamp: datetime
    reported_timestamp: datetime
    status: ComplianceStatus
    assigned_compliance_officer: Optional[str]
    legal_team_notified: bool
    external_authorities_notified: bool
    remediation_actions: List[Dict[str, Any]]
    evidence_collected: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
    estimated_resolution_time: Optional[datetime]
    actual_resolution_time: Optional[datetime]
    business_impact_assessment: Dict[str, Any]
    pagerduty_incident_id: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class AuditEntry:
    """Audit trail entry"""
    entry_id: str
    incident_id: str
    timestamp: datetime
    actor: str
    action: str
    details: Dict[str, Any]
    evidence_reference: Optional[str]
    compliance_status_change: Optional[ComplianceStatus]


@dataclass
class ComplianceAlert:
    """Compliance alert for monitoring"""
    alert_id: str
    alert_type: str
    framework: ComplianceFramework
    severity: IncidentSeverity
    message: str
    details: Dict[str, Any]
    automated_detection: bool
    requires_immediate_action: bool
    escalation_required: bool
    created_at: datetime
    resolved_at: Optional[datetime]


class ComplianceIncidentHandler:
    """
    Compliance incident management for Creator Economy platform
    Handles regulatory compliance, audit trails, and legal requirements
    """
    
    def __init__(self, pagerduty_client=None):
        """Initialize compliance incident handler"""
        self.pagerduty_client = pagerduty_client
        self.compliance_requirements = {}
        self.active_incidents = {}
        self.audit_trail = {}
        self.compliance_alerts = {}
        self.compliance_officers = {}
        
        # Initialize compliance requirements
        self._initialize_compliance_requirements()
        
        # Configuration
        self.config = {
            "auto_notification_enabled": True,
            "audit_retention_days": 2555,  # 7 years
            "evidence_retention_days": 2555,
            "max_incident_response_time": {
                "critical": 1,    # 1 hour
                "high": 4,        # 4 hours
                "medium": 24,     # 24 hours
                "low": 72         # 72 hours
            },
            "compliance_officers": {
                "gdpr": "gdpr-officer@iacherie.com",
                "ccpa": "privacy-officer@iacherie.com",
                "pci_dss": "security-officer@iacherie.com",
                "legal": "legal@iacherie.com"
            }
        }
        
        logger.info("Compliance Incident Handler initialized")
    
    def _initialize_compliance_requirements(self):
        """Initialize Creator Economy compliance requirements"""
        
        # GDPR Requirements
        self.compliance_requirements["gdpr_data_breach"] = ComplianceRequirement(
            requirement_id="gdpr_data_breach",
            framework=ComplianceFramework.GDPR,
            title="GDPR Data Breach Notification",
            description="Personal data breach affecting EU residents",
            data_types=[DataType.PERSONAL_DATA, DataType.BEHAVIORAL_DATA],
            severity_level=IncidentSeverity.CRITICAL,
            max_response_time_hours=72,
            notification_required=True,
            documentation_required=True,
            external_reporting_required=True,
            retention_period_days=2555,  # 7 years
            automated_checks_available=True,
            remediation_steps=[
                "Contain the breach immediately",
                "Assess scope of affected data",
                "Notify supervisory authority within 72 hours",
                "Notify affected individuals if high risk",
                "Document all remediation actions"
            ],
            legal_implications="Fines up to €20 million or 4% of annual turnover",
            business_impact="Severe reputation damage, regulatory fines, user trust loss"
        )
        
        self.compliance_requirements["gdpr_consent"] = ComplianceRequirement(
            requirement_id="gdpr_consent",
            framework=ComplianceFramework.GDPR,
            title="GDPR Consent Management",
            description="Invalid or missing consent for data processing",
            data_types=[DataType.PERSONAL_DATA, DataType.BEHAVIORAL_DATA],
            severity_level=IncidentSeverity.HIGH,
            max_response_time_hours=24,
            notification_required=False,
            documentation_required=True,
            external_reporting_required=False,
            retention_period_days=1825,  # 5 years
            automated_checks_available=True,
            remediation_steps=[
                "Stop processing personal data without valid consent",
                "Review consent mechanisms",
                "Update privacy policies if needed",
                "Implement proper consent management"
            ],
            legal_implications="Administrative fines and corrective measures",
            business_impact="Data processing limitations, user experience impact"
        )
        
        # CCPA Requirements
        self.compliance_requirements["ccpa_privacy_rights"] = ComplianceRequirement(
            requirement_id="ccpa_privacy_rights",
            framework=ComplianceFramework.CCPA,
            title="CCPA Privacy Rights Violation",
            description="Violation of California consumer privacy rights",
            data_types=[DataType.PERSONAL_DATA, DataType.BEHAVIORAL_DATA],
            severity_level=IncidentSeverity.HIGH,
            max_response_time_hours=45,  # CCPA response time
            notification_required=True,
            documentation_required=True,
            external_reporting_required=True,
            retention_period_days=1825,
            automated_checks_available=True,
            remediation_steps=[
                "Honor consumer privacy requests immediately",
                "Verify identity of requestor",
                "Provide required disclosures",
                "Update data handling processes"
            ],
            legal_implications="Fines up to $7,500 per intentional violation",
            business_impact="Legal liability, operational disruption"
        )
        
        # PCI DSS Requirements
        self.compliance_requirements["pci_dss_breach"] = ComplianceRequirement(
            requirement_id="pci_dss_breach",
            framework=ComplianceFramework.PCI_DSS,
            title="PCI DSS Security Incident",
            description="Payment card data security incident",
            data_types=[DataType.PAYMENT_DATA],
            severity_level=IncidentSeverity.CRITICAL,
            max_response_time_hours=24,
            notification_required=True,
            documentation_required=True,
            external_reporting_required=True,
            retention_period_days=2555,
            automated_checks_available=True,
            remediation_steps=[
                "Isolate affected payment systems",
                "Notify payment card brands",
                "Conduct forensic investigation",
                "Implement additional security controls",
                "Submit compliance report"
            ],
            legal_implications="Loss of payment processing privileges, fines",
            business_impact="Revenue loss, increased processing costs"
        )
        
        # COPPA Requirements  
        self.compliance_requirements["coppa_minor_data"] = ComplianceRequirement(
            requirement_id="coppa_minor_data",
            framework=ComplianceFramework.COPPA,
            title="COPPA Minor Data Protection",
            description="Unauthorized collection of children's data",
            data_types=[DataType.MINOR_DATA, DataType.PERSONAL_DATA],
            severity_level=IncidentSeverity.CRITICAL,
            max_response_time_hours=24,
            notification_required=True,
            documentation_required=True,
            external_reporting_required=True,
            retention_period_days=2555,
            automated_checks_available=True,
            remediation_steps=[
                "Stop collecting data from minors immediately",
                "Delete existing minor data without consent",
                "Implement age verification mechanisms",
                "Update privacy policies",
                "Train content moderation team"
            ],
            legal_implications="FTC fines up to $43,792 per violation",
            business_impact="Platform restrictions, content creator limitations"
        )
        
        # Content Compliance
        self.compliance_requirements["dmca_copyright"] = ComplianceRequirement(
            requirement_id="dmca_copyright",
            framework=ComplianceFramework.DMCA,
            title="DMCA Copyright Violation",
            description="Copyright infringement in creator content",
            data_types=[DataType.CONTENT_DATA],
            severity_level=IncidentSeverity.MEDIUM,
            max_response_time_hours=24,
            notification_required=True,
            documentation_required=True,
            external_reporting_required=False,
            retention_period_days=1095,  # 3 years
            automated_checks_available=True,
            remediation_steps=[
                "Remove infringing content immediately",
                "Notify content creator",
                "Document takedown notice",
                "Implement repeat infringer policy",
                "Update content filtering systems"
            ],
            legal_implications="Loss of safe harbor protection, liability for damages",
            business_impact="Content removal, creator dissatisfaction"
        )
    
    async def detect_compliance_incident(self, incident_data: Dict[str, Any]) -> Optional[ComplianceIncident]:
        """Detect and classify compliance incident"""
        try:
            # Analyze incident data for compliance implications
            compliance_issues = await self._analyze_compliance_implications(incident_data)
            
            if not compliance_issues:
                return None
            
            # Create compliance incident for most severe issue
            primary_issue = max(compliance_issues, key=lambda x: x["severity_score"])
            
            incident = ComplianceIncident(
                incident_id=str(uuid.uuid4()),
                framework=ComplianceFramework(primary_issue["framework"]),
                requirement_id=primary_issue["requirement_id"],
                incident_type=primary_issue["incident_type"],
                severity=IncidentSeverity(primary_issue["severity"]),
                title=primary_issue["title"],
                description=primary_issue["description"],
                affected_data_types=[DataType(dt) for dt in primary_issue["data_types"]],
                affected_users_count=incident_data.get("affected_users", 0),
                affected_creators_count=incident_data.get("affected_creators", 0),
                detection_method="automated_analysis",
                detection_timestamp=datetime.utcnow(),
                reported_timestamp=datetime.utcnow(),
                status=ComplianceStatus.UNDER_REVIEW,
                assigned_compliance_officer=None,
                legal_team_notified=False,
                external_authorities_notified=False,
                remediation_actions=[],
                evidence_collected=[],
                audit_trail=[],
                estimated_resolution_time=None,
                actual_resolution_time=None,
                business_impact_assessment={},
                pagerduty_incident_id=None,
                metadata=incident_data
            )
            
            # Store incident
            self.active_incidents[incident.incident_id] = incident
            
            # Start incident response workflow
            await self._initiate_incident_response(incident)
            
            logger.warning(f"Compliance incident detected: {incident.incident_id}")
            return incident
            
        except Exception as e:
            logger.error(f"Compliance incident detection failed: {e}")
            return None
    
    async def _analyze_compliance_implications(self, incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze incident for compliance implications"""
        compliance_issues = []
        
        try:
            # Check for data breach indicators
            if incident_data.get("data_breach", False):
                # Determine affected data types
                data_types = incident_data.get("data_types", [])
                user_count = incident_data.get("affected_users", 0)
                
                # GDPR implications
                if "personal_data" in data_types and user_count > 0:
                    compliance_issues.append({
                        "framework": "gdpr",
                        "requirement_id": "gdpr_data_breach",
                        "incident_type": "data_breach",
                        "severity": "critical",
                        "severity_score": 10,
                        "title": "GDPR Data Breach Detected",
                        "description": f"Personal data breach affecting {user_count} users",
                        "data_types": data_types
                    })
                
                # CCPA implications
                if user_count > 0 and incident_data.get("california_residents", 0) > 0:
                    compliance_issues.append({
                        "framework": "ccpa",
                        "requirement_id": "ccpa_privacy_rights", 
                        "incident_type": "privacy_violation",
                        "severity": "high",
                        "severity_score": 8,
                        "title": "CCPA Privacy Rights Incident",
                        "description": f"Privacy incident affecting {incident_data['california_residents']} CA residents",
                        "data_types": data_types
                    })
                
                # PCI DSS implications
                if "payment_data" in data_types:
                    compliance_issues.append({
                        "framework": "pci_dss",
                        "requirement_id": "pci_dss_breach",
                        "incident_type": "payment_security_incident",
                        "severity": "critical",
                        "severity_score": 10,
                        "title": "PCI DSS Security Incident",
                        "description": "Payment card data security breach",
                        "data_types": ["payment_data"]
                    })
            
            # Check for minor data collection
            if incident_data.get("minor_data_collection", False):
                compliance_issues.append({
                    "framework": "coppa",
                    "requirement_id": "coppa_minor_data",
                    "incident_type": "minor_data_violation",
                    "severity": "critical",
                    "severity_score": 9,
                    "title": "COPPA Minor Data Violation",
                    "description": "Unauthorized collection of children's data",
                    "data_types": ["minor_data", "personal_data"]
                })
            
            # Check for copyright violations
            if incident_data.get("copyright_violation", False):
                compliance_issues.append({
                    "framework": "dmca",
                    "requirement_id": "dmca_copyright",
                    "incident_type": "copyright_infringement",
                    "severity": "medium",
                    "severity_score": 5,
                    "title": "DMCA Copyright Violation",
                    "description": "Copyright infringement in creator content",
                    "data_types": ["content_data"]
                })
            
            # Check for consent issues
            if incident_data.get("consent_violation", False):
                compliance_issues.append({
                    "framework": "gdpr",
                    "requirement_id": "gdpr_consent",
                    "incident_type": "consent_violation",
                    "severity": "high",
                    "severity_score": 7,
                    "title": "GDPR Consent Violation",
                    "description": "Invalid or missing consent for data processing",
                    "data_types": ["personal_data", "behavioral_data"]
                })
            
            return compliance_issues
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {e}")
            return []
    
    async def _initiate_incident_response(self, incident: ComplianceIncident):
        """Initiate compliance incident response workflow"""
        try:
            # Create audit entry
            await self._create_audit_entry(
                incident.incident_id,
                "system",
                "incident_created",
                {"incident_data": asdict(incident)}
            )
            
            # Assign compliance officer
            await self._assign_compliance_officer(incident)
            
            # Determine immediate actions required
            requirement = self.compliance_requirements.get(incident.requirement_id)
            if requirement:
                # Check if immediate notification required
                if requirement.notification_required:
                    await self._notify_compliance_team(incident, requirement)
                
                # Check if external reporting required
                if requirement.external_reporting_required:
                    await self._prepare_external_reporting(incident, requirement)
                
                # Start evidence collection
                await self._start_evidence_collection(incident)
                
                # Create PagerDuty incident
                if self.pagerduty_client:
                    await self._create_pagerduty_incident(incident, requirement)
            
            # Set estimated resolution time
            await self._calculate_resolution_timeline(incident)
            
            logger.info(f"Incident response initiated for {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"Incident response initiation failed: {e}")
    
    async def _assign_compliance_officer(self, incident: ComplianceIncident):
        """Assign appropriate compliance officer"""
        try:
            framework_officers = {
                ComplianceFramework.GDPR: "gdpr-officer@iacherie.com",
                ComplianceFramework.CCPA: "privacy-officer@iacherie.com", 
                ComplianceFramework.PCI_DSS: "security-officer@iacherie.com",
                ComplianceFramework.COPPA: "privacy-officer@iacherie.com",
                ComplianceFramework.DMCA: "legal@iacherie.com"
            }
            
            officer = framework_officers.get(incident.framework, "compliance@iacherie.com")
            incident.assigned_compliance_officer = officer
            
            await self._create_audit_entry(
                incident.incident_id,
                "system",
                "officer_assigned",
                {"officer": officer, "framework": incident.framework.value}
            )
            
        except Exception as e:
            logger.error(f"Officer assignment failed: {e}")
    
    async def _notify_compliance_team(self, incident: ComplianceIncident, 
                                    requirement: ComplianceRequirement):
        """Notify compliance team of incident"""
        try:
            notification_data = {
                "incident_id": incident.incident_id,
                "framework": incident.framework.value,
                "severity": incident.severity.value,
                "title": incident.title,
                "description": incident.description,
                "affected_users": incident.affected_users_count,
                "max_response_time": requirement.max_response_time_hours,
                "legal_implications": requirement.legal_implications,
                "business_impact": requirement.business_impact
            }
            
            # In real implementation, send email/Slack notifications
            logger.info(f"Compliance team notified for incident {incident.incident_id}")
            
            await self._create_audit_entry(
                incident.incident_id,
                "system",
                "team_notified",
                notification_data
            )
            
        except Exception as e:
            logger.error(f"Compliance team notification failed: {e}")
    
    async def _prepare_external_reporting(self, incident: ComplianceIncident,
                                        requirement: ComplianceRequirement):
        """Prepare for external authority reporting"""
        try:
            reporting_template = {
                "incident_id": incident.incident_id,
                "framework": incident.framework.value,
                "notification_deadline": incident.detection_timestamp + timedelta(
                    hours=requirement.max_response_time_hours
                ),
                "authority_contacts": self._get_regulatory_contacts(incident.framework),
                "required_information": self._get_required_reporting_info(incident.framework),
                "documentation_checklist": requirement.remediation_steps
            }
            
            # Store reporting template
            incident.metadata["external_reporting"] = reporting_template
            
            await self._create_audit_entry(
                incident.incident_id,
                "system",
                "external_reporting_prepared",
                reporting_template
            )
            
        except Exception as e:
            logger.error(f"External reporting preparation failed: {e}")
    
    def _get_regulatory_contacts(self, framework: ComplianceFramework) -> Dict[str, str]:
        """Get regulatory authority contacts"""
        contacts = {
            ComplianceFramework.GDPR: {
                "authority": "Data Protection Authority",
                "contact": "dpa@eu-authority.eu",
                "deadline": "72 hours"
            },
            ComplianceFramework.CCPA: {
                "authority": "California Attorney General",
                "contact": "privacy@oag.ca.gov", 
                "deadline": "Upon discovery"
            },
            ComplianceFramework.PCI_DSS: {
                "authority": "Payment Card Brands",
                "contact": "incident-response@brands.com",
                "deadline": "24 hours"
            },
            ComplianceFramework.COPPA: {
                "authority": "Federal Trade Commission",
                "contact": "coppa@ftc.gov",
                "deadline": "Upon discovery"
            }
        }
        return contacts.get(framework, {})
    
    def _get_required_reporting_info(self, framework: ComplianceFramework) -> List[str]:
        """Get required information for regulatory reporting"""
        info_requirements = {
            ComplianceFramework.GDPR: [
                "Nature of the breach",
                "Categories and number of data subjects affected",
                "Categories and number of records affected", 
                "Name and contact details of DPO",
                "Description of likely consequences",
                "Measures taken or proposed to address breach"
            ],
            ComplianceFramework.CCPA: [
                "Estimated number of consumers affected",
                "Type of personal information involved",
                "Brief description of incident",
                "Date incident was discovered",
                "Whether notice to consumers is required"
            ],
            ComplianceFramework.PCI_DSS: [
                "Detailed incident description",
                "Timeline of events",
                "Systems and data affected",
                "Remediation actions taken",
                "Forensic investigation results"
            ]
        }
        return info_requirements.get(framework, [])
    
    async def _start_evidence_collection(self, incident: ComplianceIncident):
        """Start automated evidence collection"""
        try:
            evidence_items = []
            
            # System logs
            evidence_items.append({
                "type": "system_logs",
                "description": "System access and activity logs",
                "collection_method": "automated",
                "retention_period": "7_years",
                "location": "/logs/security/",
                "collected_at": datetime.utcnow().isoformat()
            })
            
            # Database audit trails
            evidence_items.append({
                "type": "database_audit",
                "description": "Database access and modification logs",
                "collection_method": "automated",
                "retention_period": "7_years", 
                "location": "/audit/database/",
                "collected_at": datetime.utcnow().isoformat()
            })
            
            # User activity logs
            evidence_items.append({
                "type": "user_activity",
                "description": "Affected user activity patterns",
                "collection_method": "automated",
                "retention_period": "7_years",
                "location": "/logs/users/",
                "collected_at": datetime.utcnow().isoformat()
            })
            
            # Network traffic (if applicable)
            if incident.severity == IncidentSeverity.CRITICAL:
                evidence_items.append({
                    "type": "network_traffic",
                    "description": "Network traffic analysis",
                    "collection_method": "automated",
                    "retention_period": "7_years",
                    "location": "/forensics/network/",
                    "collected_at": datetime.utcnow().isoformat()
                })
            
            incident.evidence_collected = evidence_items
            
            await self._create_audit_entry(
                incident.incident_id,
                "system",
                "evidence_collection_started",
                {"evidence_items": len(evidence_items)}
            )
            
        except Exception as e:
            logger.error(f"Evidence collection failed: {e}")
    
    async def _create_pagerduty_incident(self, incident: ComplianceIncident,
                                       requirement: ComplianceRequirement):
        """Create PagerDuty incident for compliance issue"""
        try:
            if not self.pagerduty_client:
                return
            
            incident_details = {
                "summary": f"Compliance Incident: {incident.framework.value.upper()} - {incident.title}",
                "source": f"compliance/{incident.framework.value}",
                "severity": incident.severity.value,
                "component": "compliance",
                "group": "legal-compliance",
                "class": "regulatory_compliance",
                "custom_details": {
                    "framework": incident.framework.value,
                    "requirement_id": incident.requirement_id,
                    "affected_users": incident.affected_users_count,
                    "affected_creators": incident.affected_creators_count,
                    "max_response_time": requirement.max_response_time_hours,
                    "external_reporting_required": requirement.external_reporting_required,
                    "legal_implications": requirement.legal_implications,
                    "business_impact": requirement.business_impact,
                    "compliance_officer": incident.assigned_compliance_officer
                }
            }
            
            pagerduty_incident_id = await self.pagerduty_client.trigger_incident(
                incident_details,
                dedup_key=f"compliance-{incident.framework.value}-{incident.incident_id}"
            )
            
            if pagerduty_incident_id:
                incident.pagerduty_incident_id = pagerduty_incident_id
                
                await self._create_audit_entry(
                    incident.incident_id,
                    "system",
                    "pagerduty_incident_created",
                    {"pagerduty_id": pagerduty_incident_id}
                )
                
                logger.info(f"PagerDuty incident {pagerduty_incident_id} created for compliance incident")
            
        except Exception as e:
            logger.error(f"PagerDuty compliance incident creation failed: {e}")
    
    async def _calculate_resolution_timeline(self, incident: ComplianceIncident):
        """Calculate estimated resolution timeline"""
        try:
            requirement = self.compliance_requirements.get(incident.requirement_id)
            if not requirement:
                return
            
            # Base timeline on severity and framework requirements
            base_hours = requirement.max_response_time_hours
            
            # Adjust for complexity
            complexity_factors = {
                "data_types_count": len(incident.affected_data_types) * 0.1,
                "user_count_factor": min(incident.affected_users_count / 1000, 1.0),
                "external_reporting": 0.5 if requirement.external_reporting_required else 0.0
            }
            
            complexity_multiplier = 1.0 + sum(complexity_factors.values())
            estimated_hours = base_hours * complexity_multiplier
            
            incident.estimated_resolution_time = (
                incident.detection_timestamp + timedelta(hours=estimated_hours)
            )
            
            await self._create_audit_entry(
                incident.incident_id,
                "system",
                "resolution_timeline_calculated",
                {
                    "estimated_hours": estimated_hours,
                    "estimated_resolution": incident.estimated_resolution_time.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Resolution timeline calculation failed: {e}")
    
    async def _create_audit_entry(self, incident_id: str, actor: str, 
                                action: str, details: Dict[str, Any],
                                evidence_reference: Optional[str] = None):
        """Create audit trail entry"""
        try:
            entry = AuditEntry(
                entry_id=str(uuid.uuid4()),
                incident_id=incident_id,
                timestamp=datetime.utcnow(),
                actor=actor,
                action=action,
                details=details,
                evidence_reference=evidence_reference,
                compliance_status_change=None
            )
            
            if incident_id not in self.audit_trail:
                self.audit_trail[incident_id] = []
            
            self.audit_trail[incident_id].append(entry)
            
        except Exception as e:
            logger.error(f"Audit entry creation failed: {e}")
    
    async def update_incident_status(self, incident_id: str, 
                                   new_status: ComplianceStatus,
                                   actor: str, notes: str = "") -> bool:
        """Update compliance incident status"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                logger.error(f"Incident {incident_id} not found")
                return False
            
            old_status = incident.status
            incident.status = new_status
            
            # Mark as resolved if applicable
            if new_status == ComplianceStatus.COMPLIANT:
                incident.actual_resolution_time = datetime.utcnow()
            
            # Create audit entry
            await self._create_audit_entry(
                incident_id,
                actor,
                "status_updated",
                {
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "notes": notes
                },
                compliance_status_change=new_status
            )
            
            # Update PagerDuty incident if resolved
            if (new_status == ComplianceStatus.COMPLIANT and 
                incident.pagerduty_incident_id and 
                self.pagerduty_client):
                
                await self.pagerduty_client.resolve_incident(
                    incident.pagerduty_incident_id,
                    resolver=actor,
                    resolution_details=f"Compliance incident resolved: {notes}"
                )
            
            logger.info(f"Incident {incident_id} status updated to {new_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Incident status update failed: {e}")
            return False
    
    async def add_remediation_action(self, incident_id: str, action: Dict[str, Any],
                                   actor: str) -> bool:
        """Add remediation action to incident"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return False
            
            remediation_action = {
                "action_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "actor": actor,
                "action_type": action.get("type", "manual"),
                "description": action.get("description", ""),
                "status": action.get("status", "planned"),
                "evidence": action.get("evidence", []),
                "effectiveness": action.get("effectiveness", "unknown")
            }
            
            incident.remediation_actions.append(remediation_action)
            
            await self._create_audit_entry(
                incident_id,
                actor,
                "remediation_action_added",
                remediation_action
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Adding remediation action failed: {e}")
            return False
    
    async def generate_compliance_report(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Generate comprehensive compliance report"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return None
            
            requirement = self.compliance_requirements.get(incident.requirement_id)
            audit_entries = self.audit_trail.get(incident_id, [])
            
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.utcnow().isoformat(),
                "incident_summary": {
                    "incident_id": incident.incident_id,
                    "framework": incident.framework.value,
                    "severity": incident.severity.value,
                    "title": incident.title,
                    "description": incident.description,
                    "status": incident.status.value,
                    "detection_time": incident.detection_timestamp.isoformat(),
                    "resolution_time": incident.actual_resolution_time.isoformat() if incident.actual_resolution_time else None
                },
                "compliance_details": {
                    "requirement_id": incident.requirement_id,
                    "legal_implications": requirement.legal_implications if requirement else "Unknown",
                    "business_impact": requirement.business_impact if requirement else "Unknown",
                    "external_reporting_required": requirement.external_reporting_required if requirement else False
                },
                "affected_scope": {
                    "users_count": incident.affected_users_count,
                    "creators_count": incident.affected_creators_count,
                    "data_types": [dt.value for dt in incident.affected_data_types]
                },
                "response_timeline": {
                    "detection_to_response": self._calculate_response_time(incident),
                    "estimated_resolution": incident.estimated_resolution_time.isoformat() if incident.estimated_resolution_time else None,
                    "actual_resolution": incident.actual_resolution_time.isoformat() if incident.actual_resolution_time else None
                },
                "remediation_actions": incident.remediation_actions,
                "evidence_collected": incident.evidence_collected,
                "audit_trail": [asdict(entry) for entry in audit_entries],
                "compliance_assessment": {
                    "current_status": incident.status.value,
                    "regulatory_obligations_met": incident.status == ComplianceStatus.COMPLIANT,
                    "outstanding_actions": self._get_outstanding_actions(incident)
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            return None
    
    def _calculate_response_time(self, incident: ComplianceIncident) -> float:
        """Calculate response time in hours"""
        if incident.reported_timestamp and incident.detection_timestamp:
            delta = incident.reported_timestamp - incident.detection_timestamp
            return delta.total_seconds() / 3600
        return 0.0
    
    def _get_outstanding_actions(self, incident: ComplianceIncident) -> List[str]:
        """Get outstanding remediation actions"""
        outstanding = []
        
        for action in incident.remediation_actions:
            if action.get("status") != "completed":
                outstanding.append(action.get("description", "Unknown action"))
        
        return outstanding
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard metrics"""
        try:
            dashboard = {
                "summary": {
                    "total_incidents": len(self.active_incidents),
                    "critical_incidents": 0,
                    "high_incidents": 0,
                    "open_incidents": 0,
                    "overdue_incidents": 0
                },
                "by_framework": {},
                "by_status": {},
                "resolution_metrics": {
                    "average_resolution_time": 0.0,
                    "sla_compliance_rate": 0.0
                },
                "recent_incidents": []
            }
            
            current_time = datetime.utcnow()
            resolution_times = []
            sla_compliant = 0
            total_resolved = 0
            
            for incident in self.active_incidents.values():
                # Count by severity
                if incident.severity == IncidentSeverity.CRITICAL:
                    dashboard["summary"]["critical_incidents"] += 1
                elif incident.severity == IncidentSeverity.HIGH:
                    dashboard["summary"]["high_incidents"] += 1
                
                # Count by status
                if incident.status not in [ComplianceStatus.COMPLIANT]:
                    dashboard["summary"]["open_incidents"] += 1
                
                # Count by framework
                framework_key = incident.framework.value
                dashboard["by_framework"][framework_key] = dashboard["by_framework"].get(framework_key, 0) + 1
                
                # Count by status
                status_key = incident.status.value
                dashboard["by_status"][status_key] = dashboard["by_status"].get(status_key, 0) + 1
                
                # Check if overdue
                if (incident.estimated_resolution_time and 
                    current_time > incident.estimated_resolution_time and
                    incident.status != ComplianceStatus.COMPLIANT):
                    dashboard["summary"]["overdue_incidents"] += 1
                
                # Calculate resolution metrics
                if incident.actual_resolution_time:
                    resolution_time = (incident.actual_resolution_time - incident.detection_timestamp).total_seconds() / 3600
                    resolution_times.append(resolution_time)
                    total_resolved += 1
                    
                    # Check SLA compliance
                    requirement = self.compliance_requirements.get(incident.requirement_id)
                    if requirement and resolution_time <= requirement.max_response_time_hours:
                        sla_compliant += 1
                
                # Add to recent incidents (last 10)
                if len(dashboard["recent_incidents"]) < 10:
                    dashboard["recent_incidents"].append({
                        "incident_id": incident.incident_id,
                        "framework": incident.framework.value,
                        "severity": incident.severity.value,
                        "title": incident.title,
                        "status": incident.status.value,
                        "created_at": incident.detection_timestamp.isoformat()
                    })
            
            # Calculate averages
            if resolution_times:
                dashboard["resolution_metrics"]["average_resolution_time"] = sum(resolution_times) / len(resolution_times)
            
            if total_resolved > 0:
                dashboard["resolution_metrics"]["sla_compliance_rate"] = (sla_compliant / total_resolved) * 100
            
            # Sort recent incidents by creation time
            dashboard["recent_incidents"].sort(key=lambda x: x["created_at"], reverse=True)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Compliance dashboard generation failed: {e}")
            return {}


# Global compliance incident handler instance
_compliance_incident_handler = None


def get_compliance_incident_handler(pagerduty_client=None) -> ComplianceIncidentHandler:
    """Get compliance incident handler instance"""
    global _compliance_incident_handler
    if _compliance_incident_handler is None:
        _compliance_incident_handler = ComplianceIncidentHandler(pagerduty_client)
    return _compliance_incident_handler


def create_compliance_incident_handler(pagerduty_client=None) -> ComplianceIncidentHandler:
    """Create new compliance incident handler instance"""
    return ComplianceIncidentHandler(pagerduty_client)


# Export main classes and functions
__all__ = [
    'ComplianceIncidentHandler',
    'ComplianceIncident',
    'ComplianceRequirement',
    'AuditEntry',
    'ComplianceAlert',
    'ComplianceFramework',
    'IncidentSeverity',
    'ComplianceStatus',
    'DataType',
    'get_compliance_incident_handler',
    'create_compliance_incident_handler'
]