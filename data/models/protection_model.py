"""Protection Data Model
====================

Professional content protection data model for monitoring and enforcement.
Comprehensive protection tracking with alerts, violations, and enforcement actions.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()


class ProtectionType(Enum):
    """
Protection type enumeration"""

    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PRIVACY = "privacy"
    DEFAMATION = "defamation"
    UNAUTHORIZED_USE = "unauthorized_use"
    PIRACY = "piracy"
    DEEPFAKE = "deepfake"
    IMPERSONATION = "impersonation"
    CONTENT_THEFT = "content_theft"
    REVENUE_THEFT = "revenue_theft"


class ViolationType(Enum):
    """Violation type enumeration"""

    EXACT_MATCH = "exact_match"
    PARTIAL_MATCH = "partial_match"
    DERIVATIVE_WORK = "derivative_work"
    UNAUTHORIZED_MONETIZATION = "unauthorized_monetization"
    FALSE_ATTRIBUTION = "false_attribution"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    PRIVACY_VIOLATION = "privacy_violation"


class SeverityLevel(Enum):
    """Severity level enumeration"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ProtectionStatus(Enum):
    """Protection status enumeration"""

    MONITORING = "monitoring"
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    TAKEDOWN_REQUESTED = "takedown_requested"
    TAKEDOWN_SUCCESSFUL = "takedown_successful"
    TAKEDOWN_FAILED = "takedown_failed"
    LEGAL_ACTION = "legal_action"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    ESCALATED = "escalated"


class EnforcementAction(Enum):
    """Enforcement action enumeration"""

    DMCA_TAKEDOWN = "dmca_takedown"
    CEASE_DESIST = "cease_desist"
    PLATFORM_REPORT = "platform_report"
    LEGAL_NOTICE = "legal_notice"
    COURT_FILING = "court_filing"
    REVENUE_CLAIM = "revenue_claim"
    CHANNEL_STRIKE = "channel_strike"
    ACCOUNT_SUSPENSION = "account_suspension"
    CONTENT_REMOVAL = "content_removal"
    MONETIZATION_DISABLE = "monetization_disable"


class ProtectionModel(Base):
    """
    Professional protection data model for IA Influencer Agent platform.
    
    Comprehensive content protection with violation detection, enforcement
    actions, legal compliance, and automated monitoring systems.
    """
    
    __tablename__ = "protection"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String(36), ForeignKey("content.id"), index=True)
    fingerprint_id = Column(String(36), ForeignKey("fingerprints.id"), index=True)
    
    # Protection basic information
    protection_type = Column(String(30), nullable=False)  # ProtectionType
    violation_type = Column(String(40))  # ViolationType if violation detected
    severity_level = Column(String(20), default=SeverityLevel.MEDIUM.value)
    status = Column(String(30), default=ProtectionStatus.MONITORING.value)
    
    # Detection information
    detected_url = Column(String(1000))  # URL where violation was found
    detected_platform = Column(String(50))  # Platform hosting violation
    detected_at = Column(DateTime)  # When violation was detected
    detection_method = Column(String(50))  # auto, manual, reported
    detection_confidence = Column(Float, default=0.0)  # 0-100%
    similarity_score = Column(Float)  # Similarity to original content
    
    # Violator information
    violator_username = Column(String(100))
    violator_profile_url = Column(String(500))
    violator_account_id = Column(String(100))
    violator_email = Column(String(255))
    violator_ip_address = Column(String(45))  # IPv6 compatible
    violator_location = Column(String(100))
    repeat_offender = Column(Boolean, default=False)
    violation_history = Column(JSON)  # Previous violations by this user
    
    # Violation details
    violation_description = Column(Text)
    infringing_content_title = Column(String(500))
    infringing_content_description = Column(Text)
    infringing_content_duration = Column(Float)  # seconds
    infringing_content_size = Column(Integer)  # bytes
    content_modifications = Column(JSON)  # How content was modified
    
    # Evidence and documentation
    evidence_urls = Column(JSON)  # Screenshots, videos, etc.
    evidence_files = Column(JSON)  # Stored evidence files
    evidence_hash = Column(String(64))  # Hash of evidence package
    legal_documents = Column(JSON)  # Legal notices, responses
    correspondence = Column(JSON)  # Communication history
    
    # Financial impact
    estimated_revenue_loss = Column(DECIMAL(12, 4))  # Estimated lost revenue
    actual_revenue_loss = Column(DECIMAL(12, 4))  # Confirmed lost revenue
    recovery_amount = Column(DECIMAL(12, 4))  # Amount recovered
    legal_costs = Column(DECIMAL(10, 4))  # Legal expenses
    enforcement_costs = Column(DECIMAL(10, 4))  # Enforcement costs
    
    # Enforcement actions
    enforcement_actions_taken = Column(ARRAY(String))  # List of actions
    dmca_notice_sent = Column(Boolean, default=False)
    dmca_notice_date = Column(Date)
    dmca_response_received = Column(Boolean, default=False)
    dmca_response_date = Column(Date)
    dmca_counter_notice = Column(Boolean, default=False)
    
    # Legal information
    jurisdiction = Column(String(10))  # Legal jurisdiction
    applicable_laws = Column(ARRAY(String))  # Relevant laws
    legal_representative = Column(String(200))  # Lawyer/firm handling case
    court_case_number = Column(String(100))
    legal_status = Column(String(50))  # pending, active, settled, won, lost
    settlement_amount = Column(DECIMAL(12, 4))
    
    # Platform-specific data
    platform_report_id = Column(String(100))  # Platform's report ID
    platform_case_id = Column(String(100))  # Platform's case ID
    platform_response = Column(JSON)  # Platform's response
    content_removed = Column(Boolean, default=False)
    content_removed_date = Column(Date)
    account_penalized = Column(Boolean, default=False)
    penalty_details = Column(JSON)  # Details of platform penalties
    
    # Monitoring and tracking
    monitoring_enabled = Column(Boolean, default=True)
    monitoring_frequency = Column(String(20), default="daily")  # hourly, daily, weekly
    last_monitored_at = Column(DateTime)
    next_monitoring_at = Column(DateTime)
    monitoring_keywords = Column(ARRAY(String))  # Keywords to monitor
    monitoring_platforms = Column(ARRAY(String))  # Platforms to monitor
    
    # Automated actions
    auto_takedown_enabled = Column(Boolean, default=False)
    auto_takedown_threshold = Column(Float, default=95.0)  # Similarity threshold
    auto_notice_enabled = Column(Boolean, default=False)
    auto_escalation_enabled = Column(Boolean, default=False)
    escalation_threshold = Column(Integer, default=3)  # Number of violations
    
    # Analytics and metrics
    detection_accuracy = Column(Float)  # True positive rate
    false_positive_rate = Column(Float)
    response_time = Column(Float)  # Hours to first action
    resolution_time = Column(Float)  # Hours to resolution
    success_rate = Column(Float)  # % of successful enforcements
    
    # Geographic and territorial
    violation_country = Column(String(2))  # ISO country code
    violation_region = Column(String(100))
    territorial_rights = Column(JSON)  # Rights by territory
    geo_blocking_enabled = Column(Boolean, default=False)
    blocked_countries = Column(ARRAY(String))
    
    # Third-party services
    detection_service = Column(String(50))  # Service used for detection
    enforcement_service = Column(String(50))  # Service used for enforcement
    legal_service = Column(String(50))  # Legal service provider
    monitoring_service = Column(String(50))  # Monitoring service
    service_costs = Column(JSON)  # Costs by service
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)  # Overall risk score 0-100
    reputational_risk = Column(Float)  # Risk to reputation
    financial_risk = Column(Float)  # Financial exposure
    legal_risk = Column(Float)  # Legal complications risk
    mitigation_strategies = Column(JSON)  # Risk mitigation plans
    
    # Collaboration and sharing
    shared_with_partners = Column(Boolean, default=False)
    partner_notifications = Column(JSON)  # Notifications to partners
    industry_alerts = Column(Boolean, default=False)  # Share with industry
    law_enforcement_notified = Column(Boolean, default=False)
    
    # Quality and validation
    human_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(36))  # User ID who reviewed
    reviewed_at = Column(DateTime)
    review_notes = Column(Text)
    quality_score = Column(Float, default=100.0)  # Detection quality
    
    # Metadata and context
    metadata = Column(JSON)  # Flexible metadata storage
    tags = Column(ARRAY(String))  # Protection tags
    categories = Column(ARRAY(String))  # Violation categories
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_detected_at = Column(DateTime)  # First detection of this violation
    last_seen_at = Column(DateTime)  # Last time violation was observed
    resolved_at = Column(DateTime)  # When issue was resolved
    
    # Soft delete
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="protection_records")
    content = relationship("ContentModel", back_populates="protection_records")
    fingerprint = relationship("FingerprintModel", back_populates="protection_alerts")
    
    def __repr__(self):
        return f"<ProtectionModel(id='{self.id}', type='{self.protection_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'fingerprint_id': self.fingerprint_id,
            'protection_type': self.protection_type,
            'violation_type': self.violation_type,
            'severity_level': self.severity_level,
            'status': self.status,
            'detected_url': self.detected_url,
            'detected_platform': self.detected_platform,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'detection_method': self.detection_method,
            'detection_confidence': self.detection_confidence,
            'similarity_score': self.similarity_score,
            'violator_username': self.violator_username,
            'violator_profile_url': self.violator_profile_url,
            'repeat_offender': self.repeat_offender,
            'violation_description': self.violation_description,
            'infringing_content_title': self.infringing_content_title,
            'evidence_urls': self.evidence_urls,
            'estimated_revenue_loss': float(self.estimated_revenue_loss) if self.estimated_revenue_loss else None,
            'actual_revenue_loss': float(self.actual_revenue_loss) if self.actual_revenue_loss else None,
            'recovery_amount': float(self.recovery_amount) if self.recovery_amount else None,
            'enforcement_actions_taken': self.enforcement_actions_taken,
            'dmca_notice_sent': self.dmca_notice_sent,
            'dmca_notice_date': self.dmca_notice_date.isoformat() if self.dmca_notice_date else None,
            'content_removed': self.content_removed,
            'content_removed_date': self.content_removed_date.isoformat() if self.content_removed_date else None,
            'monitoring_enabled': self.monitoring_enabled,
            'auto_takedown_enabled': self.auto_takedown_enabled,
            'risk_score': self.risk_score,
            'human_reviewed': self.human_reviewed,
            'quality_score': self.quality_score,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'is_deleted': self.is_deleted
        }
    
    @property
    def is_copyright_violation(self) -> bool:
        """
Check if violation is copyright-related"""
        return self.protection_type == ProtectionType.COPYRIGHT.value
    
    @property
    def is_high_severity(self) -> bool:
        """
Check if violation is high severity"""
        return self.severity_level in [SeverityLevel.HIGH.value, SeverityLevel.CRITICAL.value, SeverityLevel.EMERGENCY.value]
    
    @property
    def is_resolved(self) -> bool:
        """
Check if protection issue is resolved"""
        return self.status == ProtectionStatus.RESOLVED.value
    
    @property
    def is_under_investigation(self) -> bool:
        """
Check if violation is under investigation"""
        return self.status in [ProtectionStatus.INVESTIGATING.value, ProtectionStatus.CONFIRMED.value]
    
    @property
    def is_takedown_in_progress(self) -> bool:
        """
Check if takedown is in progress"""
        return self.status == ProtectionStatus.TAKEDOWN_REQUESTED.value
    
    @property
    def has_evidence(self) -> bool:
        """
Check if evidence has been collected"""
        return bool(self.evidence_urls or self.evidence_files)
    
    @property
    def severity_color(self) -> str:
        """
Get color code for severity level"""
        colors = {
            SeverityLevel.LOW.value: "#28a745",      # Green
            SeverityLevel.MEDIUM.value: "#ffc107",   # Yellow
            SeverityLevel.HIGH.value: "#fd7e14",     # Orange
            SeverityLevel.CRITICAL.value: "#dc3545", # Red
            SeverityLevel.EMERGENCY.value: "#6f42c1" # Purple
        }
        return colors.get(self.severity_level, "#6c757d")  # Default gray
    
    @property
    def time_to_detection(self) -> Optional[float]:
        """Calculate time from creation to detection in hours"""
        if self.detected_at and self.created_at:
            delta = self.detected_at - self.created_at
            return delta.total_seconds() / 3600
        return None
    
    @property
    def time_to_resolution(self) -> Optional[float]:
        """
Calculate time from detection to resolution in hours"""
        if self.resolved_at and self.detected_at:
            delta = self.resolved_at - self.detected_at
            return delta.total_seconds() / 3600
        return None
    
    @property
    def financial_impact_formatted(self) -> str:
        """
Get formatted financial impact"""
        if self.estimated_revenue_loss:
            return f"€{self.estimated_revenue_loss:,.2f}"
        return "€0.00"
    
    @property
    def confidence_level(self) -> str:
        """Get confidence level category"""
        if not self.detection_confidence:
            return "Unknown"
        
        confidence = self.detection_confidence
        if confidence >= 95:
            return "Very High"
        elif confidence >= 85:
            return "High"
        elif confidence >= 70:
            return "Medium"
        elif confidence >= 50:
            return "Low"
        else:
            return "Very Low"
    
    def detect_violation(self, url: str, platform: str, confidence: float, similarity: float):
        """Record violation detection"""
        self.detected_url = url
        self.detected_platform = platform
        self.detected_at = datetime.utcnow()
        self.detection_confidence = confidence
        self.similarity_score = similarity
        self.status = ProtectionStatus.DETECTED.value
        self.first_detected_at = self.first_detected_at or self.detected_at
        self.last_seen_at = self.detected_at
        
        # Determine violation type based on similarity
        if similarity >= 98:
            self.violation_type = ViolationType.EXACT_MATCH.value
        elif similarity >= 85:
            self.violation_type = ViolationType.PARTIAL_MATCH.value
        else:
            self.violation_type = ViolationType.DERIVATIVE_WORK.value
        
        # Set severity based on confidence and similarity
        if confidence >= 95 and similarity >= 90:
            self.severity_level = SeverityLevel.HIGH.value
        elif confidence >= 80 and similarity >= 75:
            self.severity_level = SeverityLevel.MEDIUM.value
        else:
            self.severity_level = SeverityLevel.LOW.value
        
        self.updated_at = datetime.utcnow()
    
    def add_evidence(self, evidence_type: str, evidence_data: Dict[str, Any]):
        """
Add evidence to the case"""
        if not self.evidence_urls:
            self.evidence_urls = []
        if not self.evidence_files:
            self.evidence_files = []
        
        evidence_entry = {
            'type': evidence_type,
            'data': evidence_data,
            'timestamp': datetime.utcnow().isoformat(),
            'hash': None  # Would calculate hash of evidence
        }
        
        if evidence_type in ['screenshot', 'video', 'document']:
            self.evidence_files.append(evidence_entry)
        else:
            self.evidence_urls.append(evidence_entry)
        
        self.updated_at = datetime.utcnow()
    
    def send_dmca_notice(self, notice_details: Dict[str, Any]):
        """
Record DMCA notice sending"""
        self.dmca_notice_sent = True
        self.dmca_notice_date = date.today()
        self.status = ProtectionStatus.TAKEDOWN_REQUESTED.value
        
        # Add to enforcement actions
        if not self.enforcement_actions_taken:
            self.enforcement_actions_taken = []
        self.enforcement_actions_taken.append(EnforcementAction.DMCA_TAKEDOWN.value)
        
        # Store notice details
        if not self.legal_documents:
            self.legal_documents = []
        
        self.legal_documents.append({
            'type': 'dmca_notice',
            'details': notice_details,
            'sent_date': date.today().isoformat()
        })
        
        self.updated_at = datetime.utcnow()
    
    def record_dmca_response(self, response_type: str, response_data: Dict[str, Any]):
        """
Record response to DMCA notice"""
        self.dmca_response_received = True
        self.dmca_response_date = date.today()
        
        if response_type == 'counter_notice':
            self.dmca_counter_notice = True
            self.status = ProtectionStatus.ESCALATED.value
        elif response_type == 'compliance':
            self.content_removed = True
            self.content_removed_date = date.today()
            self.status = ProtectionStatus.TAKEDOWN_SUCCESSFUL.value
        elif response_type == 'rejection':
            self.status = ProtectionStatus.TAKEDOWN_FAILED.value
        
        # Store response details
        if not self.legal_documents:
            self.legal_documents = []
        
        self.legal_documents.append({
            'type': f'dmca_response_{response_type}',
            'details': response_data,
            'received_date': date.today().isoformat()
        })
        
        self.updated_at = datetime.utcnow()
    
    def escalate_to_legal(self, legal_representative: str, jurisdiction: str):
        """
Escalate case to legal action"""
        self.status = ProtectionStatus.LEGAL_ACTION.value
        self.legal_representative = legal_representative
        self.jurisdiction = jurisdiction
        self.legal_status = "pending"
        
        # Add to enforcement actions
        if not self.enforcement_actions_taken:
            self.enforcement_actions_taken = []
        self.enforcement_actions_taken.append(EnforcementAction.LEGAL_NOTICE.value)
        
        self.updated_at = datetime.utcnow()
    
    def resolve_case(self, resolution_type: str, recovery_amount: Decimal = None, notes: str = None):
        """Resolve protection case"""
        self.status = ProtectionStatus.RESOLVED.value
        self.resolved_at = datetime.utcnow()
        
        if recovery_amount:
            self.recovery_amount = recovery_amount
        
        if notes:
            if not self.review_notes:
                self.review_notes = notes
            else:
                self.review_notes += f"\nResolution: {notes}"
        
        # Calculate success metrics
        if self.detected_at:
            self.resolution_time = (self.resolved_at - self.detected_at).total_seconds() / 3600
        
        self.updated_at = datetime.utcnow()
    
    def dismiss_case(self, reason: str):
        """Dismiss protection case"""
        self.status = ProtectionStatus.DISMISSED.value
        self.resolved_at = datetime.utcnow()
        
        if not self.review_notes:
            self.review_notes = f"Dismissed: {reason}"
        else:
            self.review_notes += f"\nDismissed: {reason}"
        
        self.updated_at = datetime.utcnow()
    
    def calculate_financial_impact(self, content_revenue_rate: Decimal = None):
        """Calculate estimated financial impact"""
        if not content_revenue_rate:
            return
        
        # Simple calculation based on view estimates
        estimated_views = 1000  # Would be calculated based on platform and content
        daily_loss = content_revenue_rate * estimated_views
        
        # Estimate based on how long violation has been active
        if self.detected_at:
            days_active = (datetime.utcnow() - self.detected_at).days
            self.estimated_revenue_loss = daily_loss * max(1, days_active)
        
        self.updated_at = datetime.utcnow()
    
    def update_risk_assessment(self):
        """
Update risk scores"""
        # Calculate risk based on various factors
        base_risk = 0
        
        # Severity contributes to risk
        severity_weights = {
            SeverityLevel.LOW.value: 10,
            SeverityLevel.MEDIUM.value: 25,
            SeverityLevel.HIGH.value: 50,
            SeverityLevel.CRITICAL.value: 75,
            SeverityLevel.EMERGENCY.value: 90
        }
        base_risk += severity_weights.get(self.severity_level, 25)
        
        # Repeat offender increases risk
        if self.repeat_offender:
            base_risk += 20
        
        # Platform influence on risk
        high_reach_platforms = ['youtube', 'instagram', 'tiktok', 'facebook']
        if self.detected_platform and self.detected_platform.lower() in high_reach_platforms:
            base_risk += 15
        
        # Financial impact increases risk
        if self.estimated_revenue_loss and self.estimated_revenue_loss > 1000:
            base_risk += 20
        
        self.risk_score = min(100, base_risk)
        
        # Set component risks
        self.reputational_risk = min(100, base_risk * 0.8)
        self.financial_risk = min(100, base_risk * 1.2) if self.estimated_revenue_loss else base_risk * 0.5
        self.legal_risk = min(100, base_risk * 0.6) if self.dmca_counter_notice else base_risk * 0.3
        
        self.updated_at = datetime.utcnow()
    
    def set_monitoring_schedule(self, frequency: str, keywords: List[str] = None, platforms: List[str] = None):
        """
Configure monitoring settings"""
        self.monitoring_frequency = frequency
        self.monitoring_keywords = keywords or []
        self.monitoring_platforms = platforms or []
        
        # Calculate next monitoring time
        from datetime import timedelta
        
        if frequency == "hourly":
            delta = timedelta(hours=1)
        elif frequency == "daily":
            delta = timedelta(days=1)
        elif frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(days=1)  # Default to daily
        
        self.next_monitoring_at = datetime.utcnow() + delta
        self.updated_at = datetime.utcnow()
    
    def mark_as_repeat_offender(self, violation_count: int):
        """Mark violator as repeat offender"""
        self.repeat_offender = True
        
        if not self.violation_history:
            self.violation_history = []
        
        self.violation_history.append({
            'violation_id': self.id,
            'violation_date': self.detected_at.isoformat() if self.detected_at else None,
            'violation_type': self.violation_type,
            'platform': self.detected_platform,
            'count': violation_count
        })
        
        # Increase severity for repeat offenders
        if self.severity_level == SeverityLevel.LOW.value:
            self.severity_level = SeverityLevel.MEDIUM.value
        elif self.severity_level == SeverityLevel.MEDIUM.value:
            self.severity_level = SeverityLevel.HIGH.value
        
        self.updated_at = datetime.utcnow()
    
    def enable_auto_enforcement(self, threshold: float = 95.0):
        """
Enable automatic enforcement"""
        self.auto_takedown_enabled = True
        self.auto_takedown_threshold = threshold
        self.auto_notice_enabled = True
        self.updated_at = datetime.utcnow()
    
    def human_review(self, reviewer_id: str, decision: str, notes: str = None):
        """
Record human review of case"""
        self.human_reviewed = True
        self.reviewed_by = reviewer_id
        self.reviewed_at = datetime.utcnow()
        
        if notes:
            self.review_notes = notes
        
        # Update status based on review decision
        if decision == "confirm":
            if self.status == ProtectionStatus.DETECTED.value:
                self.status = ProtectionStatus.CONFIRMED.value
        elif decision == "dismiss":
            self.dismiss_case("Human review - false positive")
        elif decision == "escalate":
            self.status = ProtectionStatus.ESCALATED.value
        
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """Soft delete protection record"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.monitoring_enabled = False
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """
Restore soft-deleted protection record"""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.utcnow()
