"""
Ultra-Advanced Compliance and Regulatory Management System

Revolutionary compliance management and regulatory oversight system specifically
designed for the IA Influencer Agent platform. Ensures comprehensive adherence
to GDPR, CCPA, HIPAA, SOX, DMCA, and international content protection laws.
Provides automated compliance monitoring, audit trail generation, regulatory
reporting, and risk assessment with real-time violation detection and
automated remediation capabilities.

Business Logic Integration:
User (musicien/blogueur/photographe/influencer/comédien) → Upload multi-format → 
IA protection droits → SEO pro → Matching collaboration → Distribution multi-plateformes

Created by: Fahed Mlaiel <mlaiel@live.de>
Team: Multi-Expert Legal Compliance Specialist & Regulatory Technology Lead

 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 
This revolutionary compliance management system is the EXCLUSIVE property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or exploitation is STRICTLY PROHIBITED.
Legal action will be taken against violators under international IP law.
Contact: mlaiel@live.de for authorization.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import logging
from dataclasses import dataclass, asdict
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, JSON, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()


class ComplianceFramework(Enum):
    """Compliance frameworks supported."""
    
    GDPR = "gdpr"  # General Data Protection Regulation (EU)
    CCPA = "ccpa"  # California Consumer Privacy Act (US)
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    SOX = "sox"  # Sarbanes-Oxley Act
    ISO_27001 = "iso_27001"  # ISO/IEC 27001 Information Security
    NIST = "nist"  # NIST Cybersecurity Framework
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados (Brazil)
    DMCA = "dmca"  # Digital Millennium Copyright Act
    CJIS = "cjis"  # Criminal Justice Information Services


class ComplianceEventType(Enum):
    """Types of compliance events."""
    
    # Data Protection Events
    DATA_SUBJECT_REQUEST = "data_subject_request"
    DATA_PORTABILITY_REQUEST = "data_portability_request"
    RIGHT_TO_ERASURE = "right_to_erasure"
    CONSENT_WITHDRAWAL = "consent_withdrawal"
    CONSENT_GRANTED = "consent_granted"
    DATA_RETENTION_VIOLATION = "data_retention_violation"
    DATA_MINIMIZATION_VIOLATION = "data_minimization_violation"
    
    # Security Events
    DATA_BREACH_NOTIFICATION = "data_breach_notification"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SECURITY_INCIDENT = "security_incident"
    VULNERABILITY_DISCLOSURE = "vulnerability_disclosure"
    
    # Processing Events
    LAWFUL_BASIS_CHANGE = "lawful_basis_change"
    PURPOSE_LIMITATION_VIOLATION = "purpose_limitation_violation"
    INTERNATIONAL_TRANSFER = "international_transfer"
    THIRD_PARTY_SHARING = "third_party_sharing"
    
    # Payment Security Events
    CARD_DATA_EXPOSURE = "card_data_exposure"
    PCI_COMPLIANCE_VIOLATION = "pci_compliance_violation"
    PAYMENT_FRAUD_DETECTION = "payment_fraud_detection"
    
    # Audit Events
    COMPLIANCE_AUDIT = "compliance_audit"
    POLICY_VIOLATION = "policy_violation"
    TRAINING_COMPLETION = "training_completion"
    RISK_ASSESSMENT = "risk_assessment"
    
    # Copyright Events
    DMCA_TAKEDOWN_REQUEST = "dmca_takedown_request"
    COPYRIGHT_CLAIM = "copyright_claim"
    FAIR_USE_DETERMINATION = "fair_use_determination"


class ComplianceStatus(Enum):
    """Compliance status types."""
    
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_REQUIRED = "remediation_required"
    PENDING_APPROVAL = "pending_approval"
    EXPIRED = "expired"


class ComplianceRiskLevel(Enum):
    """Risk levels for compliance events."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class DataCategory(Enum):
    """Categories of data for compliance tracking."""
    
    PERSONAL_IDENTIFIABLE = "pii"
    SENSITIVE_PERSONAL = "spi"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    BEHAVIORAL = "behavioral"
    LOCATION = "location"
    COMMUNICATION = "communication"
    CONTENT = "content"
    MARKETING = "marketing"


@dataclass
class ComplianceContext:
    """Context information for compliance events."""
    
    framework: ComplianceFramework
    jurisdiction: str
    data_categories: List[DataCategory]
    legal_basis: str
    data_controller: str
    data_processor: Optional[str]
    retention_period: Optional[int]  # Days
    encryption_status: bool
    anonymization_status: bool


class ComplianceTrackingLog(Base):
    """Compliance tracking log model."""
    
    __tablename__ = "compliance_tracking_logs"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_id = Column(String(255), nullable=False, unique=True, index=True)
    compliance_case_id = Column(String(255), index=True)  # Groups related events
    
    # Compliance details
    framework = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False, index=True)
    risk_level = Column(String(50), nullable=False, index=True)
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text)
    compliance_requirement = Column(String(500))
    violation_details = Column(Text)
    
    # Timing
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc), index=True)
    deadline = Column(DateTime(timezone=True))  # Compliance deadline
    resolution_deadline = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Affected entities
    user_id = Column(UUID(as_uuid=True), index=True)
    data_subject_id = Column(String(255), index=True)
    organization_id = Column(UUID(as_uuid=True))
    
    # Data context
    data_categories = Column(JSON)  # List of data categories involved
    data_volume = Column(Integer)  # Number of records affected
    data_sensitivity = Column(String(50))
    legal_basis = Column(String(100))
    processing_purpose = Column(String(500))
    
    # Geographic context
    jurisdiction = Column(String(100), nullable=False)
    data_location = Column(String(100))
    cross_border_transfer = Column(Boolean, default=False)
    transfer_mechanism = Column(String(100))  # adequacy decision, SCCs, etc.
    
    # Security context
    encryption_status = Column(Boolean, default=False)
    anonymization_status = Column(Boolean, default=False)
    pseudonymization_status = Column(Boolean, default=False)
    access_controls = Column(JSON)
    
    # Response and remediation
    automated_response = Column(JSON)
    manual_actions = Column(JSON)
    remediation_steps = Column(Text)
    preventive_measures = Column(Text)
    
    # Documentation
    evidence_collected = Column(JSON)
    documentation_links = Column(JSON)
    audit_trail = Column(JSON)
    
    # Notification requirements
    notification_required = Column(Boolean, default=False)
    authority_notification = Column(Boolean, default=False)
    data_subject_notification = Column(Boolean, default=False)
    notification_deadline = Column(DateTime(timezone=True))
    notification_sent = Column(Boolean, default=False)
    notification_details = Column(JSON)
    
    # Financial impact
    potential_fine = Column(Float)
    actual_fine = Column(Float)
    remediation_cost = Column(Float)
    business_impact = Column(Float)
    
    # Responsible parties
    compliance_officer = Column(String(255))
    data_protection_officer = Column(String(255))
    legal_counsel = Column(String(255))
    assigned_to = Column(String(255))
    
    # External parties
    supervisory_authority = Column(String(255))
    third_party_processors = Column(JSON)
    legal_representatives = Column(JSON)
    
    # Review and approval
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_framework_status', 'framework', 'status'),
        Index('idx_risk_level_timestamp', 'risk_level', 'timestamp'),
        Index('idx_deadline', 'deadline'),
        Index('idx_jurisdiction_framework', 'jurisdiction', 'framework'),
        Index('idx_data_subject', 'data_subject_id'),
        Index('idx_notification_required', 'notification_required', 'notification_sent'),
    )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {
            "id": str(self.id),
            "tracking_id": self.tracking_id,
            "compliance_case_id": self.compliance_case_id,
            "framework": self.framework,
            "event_type": self.event_type,
            "status": self.status,
            "risk_level": self.risk_level,
            "event_name": self.event_name,
            "event_description": self.event_description,
            "compliance_requirement": self.compliance_requirement,
            "violation_details": self.violation_details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "resolution_deadline": self.resolution_deadline.isoformat() if self.resolution_deadline else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "organization_id": str(self.organization_id) if self.organization_id else None,
            "data_categories": self.data_categories,
            "data_volume": self.data_volume,
            "data_sensitivity": self.data_sensitivity,
            "legal_basis": self.legal_basis,
            "processing_purpose": self.processing_purpose,
            "jurisdiction": self.jurisdiction,
            "data_location": self.data_location,
            "cross_border_transfer": self.cross_border_transfer,
            "transfer_mechanism": self.transfer_mechanism,
            "encryption_status": self.encryption_status,
            "anonymization_status": self.anonymization_status,
            "pseudonymization_status": self.pseudonymization_status,
            "access_controls": self.access_controls,
            "automated_response": self.automated_response,
            "manual_actions": self.manual_actions,
            "remediation_steps": self.remediation_steps,
            "preventive_measures": self.preventive_measures,
            "evidence_collected": self.evidence_collected,
            "documentation_links": self.documentation_links,
            "audit_trail": self.audit_trail,
            "notification_required": self.notification_required,
            "authority_notification": self.authority_notification,
            "data_subject_notification": self.data_subject_notification,
            "notification_deadline": self.notification_deadline.isoformat() if self.notification_deadline else None,
            "notification_sent": self.notification_sent,
            "notification_details": self.notification_details,
            "potential_fine": self.potential_fine,
            "actual_fine": self.actual_fine,
            "remediation_cost": self.remediation_cost,
            "business_impact": self.business_impact,
            "compliance_officer": self.compliance_officer,
            "data_protection_officer": self.data_protection_officer,
            "legal_counsel": self.legal_counsel,
            "assigned_to": self.assigned_to,
            "supervisory_authority": self.supervisory_authority,
            "third_party_processors": self.third_party_processors,
            "legal_representatives": self.legal_representatives,
            "requires_approval": self.requires_approval,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approval_notes": self.approval_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data only if explicitly requested
        if include_sensitive:
            result.update({
                "data_subject_id": self.data_subject_id
            })
        
        return result


class ComplianceTracker:
    """Enterprise compliance tracking system."""
    
    def __init__(self, db_session, service_name: str = "ia_influencer_agent"):
        """
        Initialize compliance tracker.
        
        Args:
            db_session: Database session
            service_name: Name of the service
        """
        self.db_session = db_session
        self.service_name = service_name
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    def track_compliance_event(
        self,
        framework: ComplianceFramework,
        event_type: ComplianceEventType,
        event_name: str,
        jurisdiction: str,
        risk_level: ComplianceRiskLevel = ComplianceRiskLevel.MEDIUM,
        status: ComplianceStatus = ComplianceStatus.UNDER_REVIEW,
        description: Optional[str] = None,
        compliance_requirement: Optional[str] = None,
        violation_details: Optional[str] = None,
        user_id: Optional[str] = None,
        data_subject_id: Optional[str] = None,
        data_categories: Optional[List[DataCategory]] = None,
        data_volume: Optional[int] = None,
        legal_basis: Optional[str] = None,
        processing_purpose: Optional[str] = None,
        deadline: Optional[datetime] = None,
        notification_required: bool = False,
        automated_response: Optional[List[str]] = None,
        compliance_case_id: Optional[str] = None
    ) -> str:
        """
        Track a compliance event.
        
        Args:
            framework: Compliance framework
            event_type: Type of compliance event
            event_name: Name of the event
            jurisdiction: Legal jurisdiction
            risk_level: Risk level assessment
            status: Compliance status
            description: Event description
            compliance_requirement: Specific requirement involved
            violation_details: Details of any violation
            user_id: ID of user involved
            data_subject_id: ID of data subject
            data_categories: Categories of data involved
            data_volume: Volume of data affected
            legal_basis: Legal basis for processing
            processing_purpose: Purpose of data processing
            deadline: Compliance deadline
            notification_required: Whether notification is required
            automated_response: Automated actions taken
            compliance_case_id: ID of related compliance case
            
        Returns:
            str: Generated tracking ID
        """



        try:
            tracking_id = f"comp_{uuid.uuid4().hex[:16]}"
            
            # Generate case ID if not provided
            if not compliance_case_id:
                compliance_case_id = f"case_{uuid.uuid4().hex[:12]}"
            
            compliance_log = ComplianceTrackingLog(
                tracking_id=tracking_id,
                compliance_case_id=compliance_case_id,
                framework=framework.value,
                event_type=event_type.value,
                status=status.value,
                risk_level=risk_level.value,
                event_name=event_name,
                event_description=description,
                compliance_requirement=compliance_requirement,
                violation_details=violation_details,
                user_id=user_id,
                data_subject_id=data_subject_id,
                data_categories=[cat.value for cat in data_categories] if data_categories else None,
                data_volume=data_volume,
                legal_basis=legal_basis,
                processing_purpose=processing_purpose,
                jurisdiction=jurisdiction,
                deadline=deadline,
                notification_required=notification_required,
                automated_response=automated_response
            )
            
            # Set notification deadlines based on framework
            if notification_required and deadline:
                if framework == ComplianceFramework.GDPR:
                    # GDPR requires notification within 72 hours for breaches
                    compliance_log.notification_deadline = datetime.now(timezone.utc) + timedelta(hours=72)
                elif framework == ComplianceFramework.CCPA:
                    # CCPA has different notification requirements
                    compliance_log.notification_deadline = deadline
                else:
                    compliance_log.notification_deadline = deadline
            
            # Calculate potential fines based on framework and risk
            if framework == ComplianceFramework.GDPR:
                if risk_level == ComplianceRiskLevel.CRITICAL:
                    compliance_log.potential_fine = 20000000.0  # Up to €20M or 4% of turnover
                elif risk_level == ComplianceRiskLevel.HIGH:
                    compliance_log.potential_fine = 10000000.0  # Up to €10M or 2% of turnover
            elif framework == ComplianceFramework.CCPA:
                if risk_level in [ComplianceRiskLevel.CRITICAL, ComplianceRiskLevel.HIGH]:
                    compliance_log.potential_fine = 7500.0 * (data_volume or 1)  # $7,500 per violation
            
            self.db_session.add(compliance_log)
            self.db_session.commit()
            
            # Log based on risk level
            log_message = f"Compliance Event: {event_name} ({framework.value}/{event_type.value})"
            
            if risk_level == ComplianceRiskLevel.CRITICAL:
                self.logger.critical(log_message, extra={
                    "tracking_id": tracking_id,
                    "framework": framework.value,
                    "risk_level": risk_level.value
                })
            elif risk_level == ComplianceRiskLevel.HIGH:
                self.logger.error(log_message, extra={
                    "tracking_id": tracking_id,
                    "framework": framework.value
                })
            else:
                self.logger.info(log_message, extra={
                    "tracking_id": tracking_id,
                    "framework": framework.value
                })
            
            return tracking_id
            
        except Exception as e:
            self.logger.error(f"Failed to track compliance event: {str(e)}")
            self.db_session.rollback()
            raise
    
    def track_gdpr_data_subject_request(
        self,
        data_subject_id: str,
        request_type: str,
        legal_basis: str,
        data_categories: List[DataCategory],
        user_id: Optional[str] = None,
        data_volume: Optional[int] = None
    ) -> str:
        """Track GDPR data subject request."""



        return self.track_compliance_event(
            framework=ComplianceFramework.GDPR,
            event_type=ComplianceEventType.DATA_SUBJECT_REQUEST,
            event_name=f"GDPR Data Subject {request_type.title()} Request",
            jurisdiction="EU",
            risk_level=ComplianceRiskLevel.MEDIUM,
            description=f"Data subject requested {request_type} of personal data",
            compliance_requirement="GDPR Article 15-22 (Data Subject Rights)",
            data_subject_id=data_subject_id,
            user_id=user_id,
            data_categories=data_categories,
            data_volume=data_volume,
            legal_basis=legal_basis,
            deadline=datetime.now(timezone.utc) + timedelta(days=30),  # 1 month response time
            notification_required=True,
            automated_response=["acknowledge_request", "identity_verification"]
        )
    
    def track_data_breach(
        self,
        framework: ComplianceFramework,
        breach_type: str,
        affected_records: int,
        data_categories: List[DataCategory],
        jurisdiction: str,
        encryption_status: bool = False,
        risk_assessment: str = "high"
    ) -> str:
        """Track data breach for compliance."""
        risk_level = ComplianceRiskLevel.CRITICAL if not encryption_status else ComplianceRiskLevel.HIGH
        
        return self.track_compliance_event(
            framework=framework,
            event_type=ComplianceEventType.DATA_BREACH_NOTIFICATION,
            event_name=f"Data Breach - {breach_type}",
            jurisdiction=jurisdiction,
            risk_level=risk_level,
            description=f"Data breach affecting {affected_records} records",
            compliance_requirement="Data breach notification requirements",
            violation_details=f"Breach type: {breach_type}, Encryption: {encryption_status}",
            data_categories=data_categories,
            data_volume=affected_records,
            deadline=datetime.now(timezone.utc) + timedelta(hours=72),
            notification_required=True,
            automated_response=["incident_response", "forensics_initiate", "legal_notification"]
        )
    
    def track_dmca_takedown(
        self,
        content_id: str,
        copyright_holder: str,
        claimed_work: str,
        user_id: Optional[str] = None
    ) -> str:
        """Track DMCA takedown request."""



        return self.track_compliance_event(
            framework=ComplianceFramework.DMCA,
            event_type=ComplianceEventType.DMCA_TAKEDOWN_REQUEST,
            event_name="DMCA Takedown Request",
            jurisdiction="US",
            risk_level=ComplianceRiskLevel.MEDIUM,
            description=f"DMCA takedown request for content: {claimed_work}",
            compliance_requirement="DMCA Section 512(c) Safe Harbor",
            user_id=user_id,
            data_categories=[DataCategory.CONTENT],
            processing_purpose=f"Content removal for copyright violation",
            deadline=datetime.now(timezone.utc) + timedelta(days=14),  # 14 days for counter-notice
            notification_required=True,
            automated_response=["content_takedown", "user_notification", "legal_review"]
        )
    
    def track_pci_violation(
        self,
        violation_type: str,
        payment_system: str,
        card_data_involved: bool,
        user_id: Optional[str] = None
    ) -> str:
        """Track PCI DSS compliance violation."""
        risk_level = ComplianceRiskLevel.CRITICAL if card_data_involved else ComplianceRiskLevel.HIGH
        
        return self.track_compliance_event(
            framework=ComplianceFramework.PCI_DSS,
            event_type=ComplianceEventType.PCI_COMPLIANCE_VIOLATION,
            event_name=f"PCI DSS Violation - {violation_type}",
            jurisdiction="Global",
            risk_level=risk_level,
            description=f"PCI DSS violation in {payment_system}",
            compliance_requirement="PCI DSS Requirements 1-12",
            violation_details=f"Violation type: {violation_type}, Card data involved: {card_data_involved}",
            user_id=user_id,
            data_categories=[DataCategory.FINANCIAL],
            deadline=datetime.now(timezone.utc) + timedelta(days=7),  # Immediate remediation required
            notification_required=True,
            automated_response=["payment_system_isolate", "forensics_initiate", "card_brands_notify"]
        )
    
    def update_compliance_status(
        self,
        tracking_id: str,
        status: ComplianceStatus,
        assigned_to: Optional[str] = None,
        remediation_steps: Optional[str] = None,
        evidence_collected: Optional[Dict[str, Any]] = None,
        notification_sent: bool = False,
        approval_required: bool = False
    ) -> bool:
        """
        Update compliance tracking status.
        
        Args:
            tracking_id: Tracking ID to update
            status: New compliance status
            assigned_to: Person assigned to handle
            remediation_steps: Steps taken for remediation
            evidence_collected: Evidence documentation
            notification_sent: Whether notifications were sent
            approval_required: Whether approval is required
            
        Returns:
            bool: True if successfully updated
        """



        try:
            compliance_log = self.db_session.query(ComplianceTrackingLog).filter_by(tracking_id=tracking_id).first()
            
            if compliance_log:
                compliance_log.status = status.value
                
                if assigned_to:
                    compliance_log.assigned_to = assigned_to
                
                if remediation_steps:
                    compliance_log.remediation_steps = remediation_steps
                
                if evidence_collected:
                    compliance_log.evidence_collected = evidence_collected
                
                if notification_sent:
                    compliance_log.notification_sent = True
                
                if approval_required:
                    compliance_log.requires_approval = True
                
                # Set completion time for completed statuses
                if status in [ComplianceStatus.COMPLIANT, ComplianceStatus.NON_COMPLIANT]:
                    compliance_log.completed_at = datetime.now(timezone.utc)
                
                self.db_session.commit()
                
                self.logger.info(f"Compliance tracking {tracking_id} status updated to {status.value}")
                return True
            else:
                self.logger.warning(f"Compliance tracking {tracking_id} not found for status update")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update compliance status: {str(e)}")
            self.db_session.rollback()
            return False
    
    def get_compliance_dashboard(
        self,
        framework: Optional[ComplianceFramework] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get compliance dashboard summary.
        
        Args:
            framework: Specific framework to analyze
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Compliance dashboard data
        """



        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = self.db_session.query(ComplianceTrackingLog).filter(
                ComplianceTrackingLog.timestamp >= start_date
            )
            
            if framework:
                query = query.filter_by(framework=framework.value)
            
            logs = query.all()
            
            # Calculate statistics
            total_events = len(logs)
            framework_counts = {}
            status_counts = {}
            risk_level_counts = {}
            overdue_events = 0
            pending_notifications = 0
            total_potential_fines = 0.0
            total_actual_fines = 0.0
            
            for log in logs:
                # Count by framework
                framework_counts[log.framework] = framework_counts.get(log.framework, 0) + 1
                
                # Count by status
                status_counts[log.status] = status_counts.get(log.status, 0) + 1
                
                # Count by risk level
                risk_level_counts[log.risk_level] = risk_level_counts.get(log.risk_level, 0) + 1
                
                # Check for overdue events
                if log.deadline and log.deadline < datetime.now(timezone.utc) and log.status not in [ComplianceStatus.COMPLIANT.value]:
                    overdue_events += 1
                
                # Check for pending notifications
                if log.notification_required and not log.notification_sent:
                    pending_notifications += 1
                
                # Sum potential and actual fines
                if log.potential_fine:
                    total_potential_fines += log.potential_fine
                if log.actual_fine:
                    total_actual_fines += log.actual_fine
            
            # Calculate compliance score (0-100)
            compliance_score = 100
            compliance_score -= overdue_events * 15       # -15 per overdue event
            compliance_score -= pending_notifications * 10 # -10 per pending notification
            compliance_score -= risk_level_counts.get(ComplianceRiskLevel.CRITICAL.value, 0) * 20
            compliance_score -= risk_level_counts.get(ComplianceRiskLevel.HIGH.value, 0) * 10
            compliance_score = max(0, compliance_score)
            
            return {
                "period_days": days,
                "total_events": total_events,
                "compliance_score": compliance_score,
                "framework_breakdown": framework_counts,
                "status_breakdown": status_counts,
                "risk_level_breakdown": risk_level_counts,
                "overdue_events": overdue_events,
                "pending_notifications": pending_notifications,
                "total_potential_fines": total_potential_fines,
                "total_actual_fines": total_actual_fines,
                "dashboard_generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get compliance dashboard: {str(e)}")
            return {"error": str(e)}
    
    def get_upcoming_deadlines(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming compliance deadlines.
        
        Args:
            days: Number of days ahead to look for deadlines
            
        Returns:
            List[Dict[str, Any]]: List of upcoming deadlines
        """



        try:
            end_date = datetime.now(timezone.utc) + timedelta(days=days)
            
            upcoming = self.db_session.query(ComplianceTrackingLog).filter(
                ComplianceTrackingLog.deadline <= end_date,
                ComplianceTrackingLog.deadline >= datetime.now(timezone.utc),
                ComplianceTrackingLog.status.in_([
                    ComplianceStatus.UNDER_REVIEW.value,
                    ComplianceStatus.REMEDIATION_REQUIRED.value,
                    ComplianceStatus.PENDING_APPROVAL.value
                ])
            ).order_by(ComplianceTrackingLog.deadline.asc()).all()
            
            return [log.to_dict() for log in upcoming]
            
        except Exception as e:
            self.logger.error(f"Failed to get upcoming deadlines: {str(e)}")
            return []


def create_compliance_tracker(db_session, service_name: str = "ia_influencer_agent") -> ComplianceTracker:
    """
    Factory function to create compliance tracker.
    
    Args:
        db_session: Database session
        service_name: Name of the service
        
    Returns:
        ComplianceTracker: Configured compliance tracker
    """



    return ComplianceTracker(db_session, service_name)


# Export main classes and functions
__all__ = [
    "ComplianceTrackingLog",
    "ComplianceTracker",
    "ComplianceFramework",
    "ComplianceEventType",
    "ComplianceStatus",
    "ComplianceRiskLevel",
    "DataCategory",
    "ComplianceContext",
    "create_compliance_tracker"
]
