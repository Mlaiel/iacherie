"""Automated Data Breach Notification System

Implements automated breach detection, notification to authorities,
and data subject notifications in compliance with GDPR and other regulations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class BreachType(Enum):
    """Types of data breaches"""
    CONFIDENTIALITY_BREACH = "confidentiality_breach"  # Unauthorized disclosure
    INTEGRITY_BREACH = "integrity_breach"  # Unauthorized alteration
    AVAILABILITY_BREACH = "availability_breach"  # Loss of access/availability
    COMBINED_BREACH = "combined_breach"  # Multiple types


class BreachSeverity(Enum):
    """Severity levels of data breaches"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


class BreachStatus(Enum):
    """Status of breach handling"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    CONTAINED = "contained"
    AUTHORITIES_NOTIFIED = "authorities_notified"
    SUBJECTS_NOTIFIED = "subjects_notified"
    RESOLVED = "resolved"
    CLOSED = "closed"


class NotificationRequirement(Enum):
    """Notification requirements based on regulation"""
    GDPR_AUTHORITY = "gdpr_authority"  # 72 hours to supervisory authority
    GDPR_SUBJECT = "gdpr_subject"  # Without undue delay if high risk
    CCPA_AUTHORITY = "ccpa_authority"  # Varies by state
    BREACH_NOTIFICATION_LAWS = "breach_notification_laws"  # US state laws
    REGULATORY_SPECIFIC = "regulatory_specific"  # Sector-specific regulations


@dataclass
class BreachImpact:
    """Assessment of breach impact"""
    affected_individuals: int = 0
    data_categories: List[str] = field(default_factory=list)
    sensitive_data_involved: bool = False
    financial_data_involved: bool = False
    health_data_involved: bool = False
    risk_to_rights_freedoms: str = "low"  # low, medium, high
    potential_consequences: List[str] = field(default_factory=list)
    likelihood_of_harm: str = "unlikely"  # unlikely, possible, likely, certain
    mitigation_measures: List[str] = field(default_factory=list)


@dataclass
class NotificationRecord:
    """Record of breach notification sent"""
    notification_id: str
    notification_type: NotificationRequirement
    recipient: str
    recipient_type: str  # authority, individual, regulator
    sent_at: datetime
    delivery_confirmed: bool = False
    confirmation_date: Optional[datetime] = None
    method: str = "email"  # email, postal, phone, portal
    content_hash: Optional[str] = None
    regulatory_reference: Optional[str] = None


@dataclass
class DataBreach:
    """Data breach incident record"""
    breach_id: str
    title: str
    description: str
    breach_type: BreachType
    severity: BreachSeverity
    status: BreachStatus = BreachStatus.DETECTED
    detected_at: datetime = field(default_factory=datetime.utcnow)
    discovered_by: str = ""
    discovery_method: str = ""
    incident_start: Optional[datetime] = None
    incident_end: Optional[datetime] = None
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    impact_assessment: BreachImpact = field(default_factory=BreachImpact)
    notification_requirements: List[NotificationRequirement] = field(default_factory=list)
    notifications_sent: List[NotificationRecord] = field(default_factory=list)
    investigation_notes: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    regulatory_jurisdiction: List[str] = field(default_factory=list)
    external_notifications_required: bool = True
    data_subject_notifications_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class BreachNotificationManager:
    """
    Automated Data Breach Notification System
    
    Handles breach detection, assessment, containment, and automated
    notifications to authorities and data subjects per regulatory requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage for breaches
        self.breaches: Dict[str, DataBreach] = {}
        self.notification_queue: List[NotificationRecord] = []
        
        # Configuration
        self.notification_templates = self._load_notification_templates()
        self.authority_contacts = self._load_authority_contacts()
        self.notification_deadlines = self._load_notification_deadlines()
        
        # Audit trail
        self.audit_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "total_breaches": 0,
            "active_breaches": 0,
            "notifications_sent": 0,
            "compliance_rate": 100.0,
            "average_detection_time": 0.0,
            "average_notification_time": 0.0,
            "overdue_notifications": 0
        }
    
    def _load_notification_templates(self) -> Dict[str, str]:
        """Load breach notification templates"""
        return {
            "gdpr_authority": """
PERSONAL DATA BREACH NOTIFICATION
(Article 33 GDPR)

To: {authority_name}
From: {controller_name}
Date: {notification_date}

1. NATURE OF THE BREACH
Breach Type: {breach_type}
Categories of Data: {data_categories}
Number of Affected Individuals: {affected_count}

2. CONTACT DETAILS
Data Protection Officer: {dpo_contact}
Organization Contact: {org_contact}

3. LIKELY CONSEQUENCES
{consequences_description}

4. MEASURES TAKEN
Containment Measures: {containment_measures}
Mitigation Measures: {mitigation_measures}

5. ASSESSMENT
Risk to Rights and Freedoms: {risk_assessment}
Data Subject Notification Required: {subject_notification_required}

Reference ID: {breach_id}
            """,
            "data_subject": """
IMPORTANT SECURITY NOTICE - DATA BREACH NOTIFICATION

Dear {subject_name},

We are writing to inform you of a security incident that may have affected your personal information.

WHAT HAPPENED:
{incident_description}

INFORMATION INVOLVED:
{affected_data_types}

WHAT WE ARE DOING:
{remediation_actions}

WHAT YOU CAN DO:
{recommended_actions}

CONTACT INFORMATION:
If you have questions, please contact us at {contact_info}

We sincerely apologize for this incident and any inconvenience it may cause.

{organization_name}
Date: {notification_date}
            """,
            "regulatory": """
DATA BREACH NOTIFICATION

Regulatory Authority: {authority_name}
Incident Reference: {breach_id}
Date of Notification: {notification_date}

INCIDENT SUMMARY:
{incident_summary}

AFFECTED DATA:
{data_summary}

COMPLIANCE ACTIONS:
{compliance_actions}

Contact: {contact_information}
            """
        }
    
    def _load_authority_contacts(self) -> Dict[str, Dict[str, Any]]:
        """Load regulatory authority contact information"""
        return {
            "gdpr_de": {
                "name": "Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI)",
                "email": "poststelle@bfdi.bund.de",
                "notification_portal": "https://www.bfdi.bund.de/meldeportal",
                "jurisdiction": "Germany",
                "deadline_hours": 72
            },
            "gdpr_fr": {
                "name": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
                "email": "notifications@cnil.fr",
                "notification_portal": "https://notifications.cnil.fr",
                "jurisdiction": "France",
                "deadline_hours": 72
            },
            "gdpr_eu": {
                "name": "European Data Protection Board",
                "email": "edpb@edpb.europa.eu",
                "notification_portal": "https://edpb.europa.eu/breach-notification",
                "jurisdiction": "EU",
                "deadline_hours": 72
            },
            "ccpa_ca": {
                "name": "California Attorney General",
                "email": "privacy@doj.ca.gov",
                "notification_portal": "https://oag.ca.gov/privacy/databreach",
                "jurisdiction": "California",
                "deadline_hours": 72
            }
        }
    
    def _load_notification_deadlines(self) -> Dict[NotificationRequirement, int]:
        """Load notification deadlines in hours"""
        return {
            NotificationRequirement.GDPR_AUTHORITY: 72,
            NotificationRequirement.GDPR_SUBJECT: 72,  # Without undue delay
            NotificationRequirement.CCPA_AUTHORITY: 72,
            NotificationRequirement.BREACH_NOTIFICATION_LAWS: 72,
            NotificationRequirement.REGULATORY_SPECIFIC: 24
        }
    
    async def report_breach(
        self,
        title: str,
        description: str,
        breach_type: BreachType,
        discovered_by: str,
        discovery_method: str = "automated",
        incident_start: Optional[datetime] = None,
        affected_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Report a new data breach
        
        Args:
            title: Brief title of the breach
            description: Detailed description
            breach_type: Type of breach
            discovered_by: Who discovered the breach
            discovery_method: How the breach was discovered
            incident_start: When the incident started
            affected_data: Information about affected data
            **kwargs: Additional parameters
            
        Returns:
            str: Breach ID
        """
        try:
            breach_id = str(uuid.uuid4())
            
            # Assess initial severity
            severity = await self._assess_initial_severity(breach_type, affected_data or {})
            
            # Create breach record
            breach = DataBreach(
                breach_id=breach_id,
                title=title,
                description=description,
                breach_type=breach_type,
                severity=severity,
                discovered_by=discovered_by,
                discovery_method=discovery_method,
                incident_start=incident_start,
                regulatory_jurisdiction=kwargs.get("jurisdiction", ["eu"]),
                metadata=kwargs.get("metadata", {})
            )
            
            self.breaches[breach_id] = breach
            
            # Log breach detection
            await self._log_audit_event({
                "event_type": "breach_detected",
                "breach_id": breach_id,
                "title": title,
                "breach_type": breach_type.value,
                "severity": severity.value,
                "discovered_by": discovered_by,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Initiate automated response
            await self._initiate_breach_response(breach)
            
            # Update metrics
            self._update_metrics()
            
            self.logger.critical(f"Data breach reported: {breach_id} ({title})")
            return breach_id
            
        except Exception as e:
            self.logger.error(f"Error reporting data breach: {e}")
            raise
    
    async def _initiate_breach_response(self, breach: DataBreach):
        """Initiate automated breach response"""
        try:
            # Start investigation
            breach.status = BreachStatus.INVESTIGATING
            
            # Perform detailed impact assessment
            await self._perform_impact_assessment(breach)
            
            # Determine notification requirements
            await self._determine_notification_requirements(breach)
            
            # Initiate containment if not already done
            await self._initiate_containment(breach)
            
            # Start notification timeline
            await self._start_notification_timeline(breach)
            
        except Exception as e:
            self.logger.error(f"Error initiating breach response: {e}")
    
    async def _perform_impact_assessment(self, breach: DataBreach):
        """Perform detailed impact assessment"""
        try:
            # Assess number of affected individuals
            affected_count = await self._count_affected_individuals(breach)
            
            # Identify data categories involved
            data_categories = await self._identify_data_categories(breach)
            
            # Assess sensitivity of data
            sensitive_assessment = await self._assess_data_sensitivity(data_categories)
            
            # Evaluate risk to rights and freedoms
            risk_assessment = await self._assess_risk_to_rights_freedoms(
                affected_count, data_categories, sensitive_assessment
            )
            
            # Update impact assessment
            breach.impact_assessment = BreachImpact(
                affected_individuals=affected_count,
                data_categories=data_categories,
                sensitive_data_involved=sensitive_assessment["sensitive"],
                financial_data_involved=sensitive_assessment["financial"],
                health_data_involved=sensitive_assessment["health"],
                risk_to_rights_freedoms=risk_assessment["level"],
                potential_consequences=risk_assessment["consequences"],
                likelihood_of_harm=risk_assessment["likelihood"],
                mitigation_measures=[]
            )
            
            # Update severity based on assessment
            breach.severity = await self._calculate_final_severity(breach.impact_assessment)
            
            await self._log_audit_event({
                "event_type": "impact_assessment_completed",
                "breach_id": breach.breach_id,
                "affected_count": affected_count,
                "severity": breach.severity.value,
                "risk_level": risk_assessment["level"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error performing impact assessment: {e}")
    
    async def _determine_notification_requirements(self, breach: DataBreach):
        """Determine which notifications are required"""
        try:
            requirements = []
            
            # GDPR requirements (if EU jurisdiction)
            if any(j in ["eu", "de", "fr", "it", "es"] for j in breach.regulatory_jurisdiction):
                requirements.append(NotificationRequirement.GDPR_AUTHORITY)
                
                # Data subject notification required if high risk
                if breach.impact_assessment.risk_to_rights_freedoms in ["medium", "high"]:
                    requirements.append(NotificationRequirement.GDPR_SUBJECT)
                    breach.data_subject_notifications_required = True
            
            # CCPA requirements (if California)
            if "ca" in breach.regulatory_jurisdiction:
                requirements.append(NotificationRequirement.CCPA_AUTHORITY)
            
            # Other breach notification laws
            if "us" in breach.regulatory_jurisdiction:
                requirements.append(NotificationRequirement.BREACH_NOTIFICATION_LAWS)
            
            breach.notification_requirements = requirements
            
            await self._log_audit_event({
                "event_type": "notification_requirements_determined",
                "breach_id": breach.breach_id,
                "requirements": [req.value for req in requirements],
                "data_subject_notification": breach.data_subject_notifications_required,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error determining notification requirements: {e}")
    
    async def _start_notification_timeline(self, breach: DataBreach):
        """Start automated notification timeline"""
        try:
            current_time = datetime.utcnow()
            
            for requirement in breach.notification_requirements:
                deadline_hours = self.notification_deadlines.get(requirement, 72)
                notification_deadline = current_time + timedelta(hours=deadline_hours)
                
                # Schedule notification
                await self._schedule_notification(breach, requirement, notification_deadline)
            
        except Exception as e:
            self.logger.error(f"Error starting notification timeline: {e}")
    
    async def _schedule_notification(
        self,
        breach: DataBreach,
        requirement: NotificationRequirement,
        deadline: datetime
    ):
        """Schedule a specific notification"""
        try:
            if requirement == NotificationRequirement.GDPR_AUTHORITY:
                await self._send_authority_notification(breach, "gdpr")
            elif requirement == NotificationRequirement.CCPA_AUTHORITY:
                await self._send_authority_notification(breach, "ccpa")
            elif requirement == NotificationRequirement.GDPR_SUBJECT:
                await self._send_data_subject_notifications(breach)
            
        except Exception as e:
            self.logger.error(f"Error scheduling notification: {e}")
    
    async def _send_authority_notification(self, breach: DataBreach, regulation: str):
        """Send notification to regulatory authority"""
        try:
            # Determine appropriate authority
            authority_key = self._get_authority_key(breach.regulatory_jurisdiction, regulation)
            authority_info = self.authority_contacts.get(authority_key)
            
            if not authority_info:
                self.logger.warning(f"No authority contact found for {authority_key}")
                return
            
            # Prepare notification content
            template = self.notification_templates["gdpr_authority" if regulation == "gdpr" else "regulatory"]
            
            notification_content = template.format(
                authority_name=authority_info["name"],
                controller_name=self.config.get("organization_name", "Organization"),
                notification_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                breach_type=breach.breach_type.value,
                data_categories=", ".join(breach.impact_assessment.data_categories),
                affected_count=breach.impact_assessment.affected_individuals,
                dpo_contact=self.config.get("dpo_contact", "dpo@company.com"),
                org_contact=self.config.get("org_contact", "contact@company.com"),
                consequences_description="; ".join(breach.impact_assessment.potential_consequences),
                containment_measures="; ".join(breach.remediation_actions),
                mitigation_measures="; ".join(breach.impact_assessment.mitigation_measures),
                risk_assessment=breach.impact_assessment.risk_to_rights_freedoms,
                subject_notification_required=breach.data_subject_notifications_required,
                breach_id=breach.breach_id
            )
            
            # Send notification
            notification_record = await self._send_notification(
                recipient=authority_info["email"],
                recipient_type="authority",
                content=notification_content,
                method="email",
                notification_type=NotificationRequirement.GDPR_AUTHORITY if regulation == "gdpr" else NotificationRequirement.CCPA_AUTHORITY
            )
            
            breach.notifications_sent.append(notification_record)
            
            # Update status
            if breach.status == BreachStatus.CONTAINED:
                breach.status = BreachStatus.AUTHORITIES_NOTIFIED
            
            await self._log_audit_event({
                "event_type": "authority_notification_sent",
                "breach_id": breach.breach_id,
                "authority": authority_info["name"],
                "notification_id": notification_record.notification_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error sending authority notification: {e}")
    
    async def _send_data_subject_notifications(self, breach: DataBreach):
        """Send notifications to affected data subjects"""
        try:
            if not breach.data_subject_notifications_required:
                return
            
            # Get list of affected individuals
            affected_individuals = await self._get_affected_individuals(breach)
            
            template = self.notification_templates["data_subject"]
            
            notifications_sent = 0
            for individual in affected_individuals:
                try:
                    # Personalize notification
                    notification_content = template.format(
                        subject_name=individual.get("name", "Valued Customer"),
                        incident_description=breach.description,
                        affected_data_types=", ".join(breach.impact_assessment.data_categories),
                        remediation_actions="; ".join(breach.remediation_actions),
                        recommended_actions="; ".join(self._get_recommended_actions(breach)),
                        contact_info=self.config.get("contact_info", "privacy@company.com"),
                        organization_name=self.config.get("organization_name", "Organization"),
                        notification_date=datetime.utcnow().strftime("%Y-%m-%d")
                    )
                    
                    # Send notification
                    notification_record = await self._send_notification(
                        recipient=individual["email"],
                        recipient_type="individual",
                        content=notification_content,
                        method="email",
                        notification_type=NotificationRequirement.GDPR_SUBJECT
                    )
                    
                    breach.notifications_sent.append(notification_record)
                    notifications_sent += 1
                    
                except Exception as e:
                    self.logger.error(f"Error sending notification to {individual.get('email')}: {e}")
            
            # Update status
            if notifications_sent > 0:
                breach.status = BreachStatus.SUBJECTS_NOTIFIED
            
            await self._log_audit_event({
                "event_type": "data_subject_notifications_sent",
                "breach_id": breach.breach_id,
                "notifications_count": notifications_sent,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error sending data subject notifications: {e}")
    
    async def _send_notification(
        self,
        recipient: str,
        recipient_type: str,
        content: str,
        method: str,
        notification_type: NotificationRequirement
    ) -> NotificationRecord:
        """Send a single notification"""
        notification_id = str(uuid.uuid4())
        
        # Implementation would use actual email/notification service
        # For now, simulate sending
        
        notification_record = NotificationRecord(
            notification_id=notification_id,
            notification_type=notification_type,
            recipient=recipient,
            recipient_type=recipient_type,
            sent_at=datetime.utcnow(),
            method=method,
            content_hash=str(hash(content))
        )
        
        # Add to queue for delivery tracking
        self.notification_queue.append(notification_record)
        
        self.logger.info(f"Breach notification sent: {notification_id} to {recipient}")
        return notification_record
    
    async def update_breach_status(
        self,
        breach_id: str,
        status: BreachStatus,
        notes: Optional[str] = None,
        remediation_actions: Optional[List[str]] = None
    ) -> bool:
        """Update breach status and add investigation notes"""
        try:
            breach = self.breaches.get(breach_id)
            if not breach:
                return False
            
            old_status = breach.status
            breach.status = status
            
            if notes:
                breach.investigation_notes.append(f"{datetime.utcnow().isoformat()}: {notes}")
            
            if remediation_actions:
                breach.remediation_actions.extend(remediation_actions)
            
            # Set timestamps for specific status changes
            if status == BreachStatus.CONTAINED:
                breach.contained_at = datetime.utcnow()
            elif status == BreachStatus.RESOLVED:
                breach.resolved_at = datetime.utcnow()
            
            await self._log_audit_event({
                "event_type": "breach_status_updated",
                "breach_id": breach_id,
                "old_status": old_status.value,
                "new_status": status.value,
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating breach status: {e}")
            return False
    
    async def get_breach_status(self, breach_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive breach status"""
        breach = self.breaches.get(breach_id)
        if not breach:
            return None
        
        # Calculate notification compliance
        required_notifications = len(breach.notification_requirements)
        sent_notifications = len(breach.notifications_sent)
        
        # Check if notifications are overdue
        overdue_notifications = []
        current_time = datetime.utcnow()
        
        for requirement in breach.notification_requirements:
            deadline_hours = self.notification_deadlines.get(requirement, 72)
            deadline = breach.detected_at + timedelta(hours=deadline_hours)
            
            if current_time > deadline:
                # Check if notification was sent
                sent = any(n.notification_type == requirement for n in breach.notifications_sent)
                if not sent:
                    overdue_notifications.append({
                        "requirement": requirement.value,
                        "deadline": deadline.isoformat(),
                        "hours_overdue": (current_time - deadline).total_seconds() / 3600
                    })
        
        return {
            "breach_id": breach_id,
            "title": breach.title,
            "status": breach.status.value,
            "severity": breach.severity.value,
            "breach_type": breach.breach_type.value,
            "detected_at": breach.detected_at.isoformat(),
            "contained_at": breach.contained_at.isoformat() if breach.contained_at else None,
            "resolved_at": breach.resolved_at.isoformat() if breach.resolved_at else None,
            "affected_individuals": breach.impact_assessment.affected_individuals,
            "data_categories": breach.impact_assessment.data_categories,
            "risk_level": breach.impact_assessment.risk_to_rights_freedoms,
            "notification_compliance": {
                "required": required_notifications,
                "sent": sent_notifications,
                "compliance_rate": (sent_notifications / required_notifications * 100) if required_notifications > 0 else 100,
                "overdue": overdue_notifications
            },
            "hours_since_detection": (current_time - breach.detected_at).total_seconds() / 3600
        }
    
    async def generate_breach_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive breach report"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter breaches by date range
            filtered_breaches = [
                breach for breach in self.breaches.values()
                if start_date <= breach.detected_at <= end_date
            ]
            
            # Calculate metrics
            total_breaches = len(filtered_breaches)
            total_affected = sum(b.impact_assessment.affected_individuals for b in filtered_breaches)
            
            # Notification compliance
            total_required_notifications = sum(len(b.notification_requirements) for b in filtered_breaches)
            total_sent_notifications = sum(len(b.notifications_sent) for b in filtered_breaches)
            
            # Response times
            resolved_breaches = [b for b in filtered_breaches if b.resolved_at]
            avg_resolution_time = 0.0
            if resolved_breaches:
                resolution_times = [
                    (b.resolved_at - b.detected_at).total_seconds() / 3600
                    for b in resolved_breaches
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_breaches": total_breaches,
                    "total_affected_individuals": total_affected,
                    "resolved_breaches": len(resolved_breaches),
                    "notification_compliance_rate": (total_sent_notifications / total_required_notifications * 100) if total_required_notifications > 0 else 100,
                    "average_resolution_time_hours": avg_resolution_time
                },
                "by_severity": {
                    severity.value: len([b for b in filtered_breaches if b.severity == severity])
                    for severity in BreachSeverity
                },
                "by_type": {
                    breach_type.value: len([b for b in filtered_breaches if b.breach_type == breach_type])
                    for breach_type in BreachType
                },
                "by_status": {
                    status.value: len([b for b in filtered_breaches if b.status == status])
                    for status in BreachStatus
                },
                "overdue_notifications": self._get_overdue_notifications(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating breach report: {e}")
            return {"error": str(e)}
    
    # Helper methods (simplified implementations)
    
    async def _assess_initial_severity(self, breach_type: BreachType, affected_data: Dict[str, Any]) -> BreachSeverity:
        """Assess initial severity based on breach type and data"""
        # Simplified assessment logic
        if "sensitive" in affected_data or "financial" in affected_data:
            return BreachSeverity.HIGH
        elif breach_type == BreachType.CONFIDENTIALITY_BREACH:
            return BreachSeverity.MEDIUM
        else:
            return BreachSeverity.LOW
    
    async def _count_affected_individuals(self, breach: DataBreach) -> int:
        """Count number of affected individuals"""
        # Implementation would query actual systems
        return 1000  # Simplified
    
    async def _identify_data_categories(self, breach: DataBreach) -> List[str]:
        """Identify categories of data involved"""
        # Implementation would analyze affected systems
        return ["email_addresses", "names", "phone_numbers"]
    
    async def _assess_data_sensitivity(self, data_categories: List[str]) -> Dict[str, bool]:
        """Assess sensitivity of involved data"""
        sensitive_categories = {"ssn", "passport", "health_records", "financial_data"}
        financial_categories = {"credit_card", "bank_account", "payment_info"}
        health_categories = {"medical_records", "health_data", "prescription_data"}
        
        return {
            "sensitive": any(cat in sensitive_categories for cat in data_categories),
            "financial": any(cat in financial_categories for cat in data_categories),
            "health": any(cat in health_categories for cat in data_categories)
        }
    
    async def _assess_risk_to_rights_freedoms(
        self,
        affected_count: int,
        data_categories: List[str],
        sensitivity: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Assess risk to rights and freedoms of data subjects"""
        if sensitivity["health"] or sensitivity["financial"]:
            level = "high"
            likelihood = "likely"
        elif affected_count > 1000:
            level = "medium"
            likelihood = "possible"
        else:
            level = "low"
            likelihood = "unlikely"
        
        return {
            "level": level,
            "likelihood": likelihood,
            "consequences": ["Identity theft", "Financial fraud", "Discrimination"]
        }
    
    async def _calculate_final_severity(self, impact: BreachImpact) -> BreachSeverity:
        """Calculate final severity based on impact assessment"""
        if impact.risk_to_rights_freedoms == "high":
            return BreachSeverity.CRITICAL
        elif impact.risk_to_rights_freedoms == "medium":
            return BreachSeverity.HIGH
        else:
            return BreachSeverity.MEDIUM
    
    def _get_authority_key(self, jurisdictions: List[str], regulation: str) -> str:
        """Get authority key based on jurisdiction"""
        for jurisdiction in jurisdictions:
            key = f"{regulation}_{jurisdiction}"
            if key in self.authority_contacts:
                return key
        return f"{regulation}_eu"  # Default
    
    async def _get_affected_individuals(self, breach: DataBreach) -> List[Dict[str, Any]]:
        """Get list of affected individuals"""
        # Implementation would query affected user data
        return [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"}
        ]
    
    def _get_recommended_actions(self, breach: DataBreach) -> List[str]:
        """Get recommended actions for data subjects"""
        actions = ["Monitor your accounts for unusual activity"]
        
        if breach.impact_assessment.financial_data_involved:
            actions.append("Consider placing a fraud alert on your credit reports")
        
        if breach.impact_assessment.sensitive_data_involved:
            actions.append("Be cautious of phishing attempts")
        
        return actions
    
    def _get_overdue_notifications(self) -> List[Dict[str, Any]]:
        """Get list of overdue notifications"""
        overdue = []
        current_time = datetime.utcnow()
        
        for breach in self.breaches.values():
            if breach.status in [BreachStatus.DETECTED, BreachStatus.INVESTIGATING, BreachStatus.CONFIRMED]:
                for requirement in breach.notification_requirements:
                    deadline_hours = self.notification_deadlines.get(requirement, 72)
                    deadline = breach.detected_at + timedelta(hours=deadline_hours)
                    
                    if current_time > deadline:
                        sent = any(n.notification_type == requirement for n in breach.notifications_sent)
                        if not sent:
                            overdue.append({
                                "breach_id": breach.breach_id,
                                "title": breach.title,
                                "requirement": requirement.value,
                                "deadline": deadline.isoformat(),
                                "hours_overdue": (current_time - deadline).total_seconds() / 3600
                            })
        
        return overdue
    
    async def _initiate_containment(self, breach: DataBreach):
        """Initiate breach containment measures"""
        # Implementation would execute containment procedures
        breach.status = BreachStatus.CONTAINED
        breach.contained_at = datetime.utcnow()
    
    async def _log_audit_event(self, event: Dict[str, Any]):
        """Log audit event"""
        event["id"] = str(uuid.uuid4())
        event["logged_at"] = datetime.utcnow().isoformat()
        self.audit_log.append(event)
    
    def _update_metrics(self):
        """Update breach metrics"""
        total = len(self.breaches)
        active = len([b for b in self.breaches.values() if b.status not in [BreachStatus.RESOLVED, BreachStatus.CLOSED]])
        notifications = sum(len(b.notifications_sent) for b in self.breaches.values())
        
        self.metrics.update({
            "total_breaches": total,
            "active_breaches": active,
            "notifications_sent": notifications,
            "overdue_notifications": len(self._get_overdue_notifications())
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get breach notification metrics"""
        return self.metrics.copy()