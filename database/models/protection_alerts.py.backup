"""Protection Alerts Database Model

Enterprise-grade SQLAlchemy model for content protection alerts and violation detection.
Manages real-time monitoring, threat detection, and automated response systems.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class AlertType(Enum):
    """Alert type enumeration"""
    COPYRIGHT_VIOLATION = "copyright_violation"
    UNAUTHORIZED_USE = "unauthorized_use"
    COMMERCIAL_INFRINGEMENT = "commercial_infringement"
    PIRACY_DETECTED = "piracy_detected"
    FAKE_CONTENT = "fake_content"
    DEEPFAKE_DETECTED = "deepfake_detected"
    WATERMARK_REMOVAL = "watermark_removal"
    CONTENT_THEFT = "content_theft"
    LICENSING_VIOLATION = "licensing_violation"
    REVENUE_LOSS = "revenue_loss"


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert processing status"""
    PENDING = "pending"
    INVESTIGATING = "investigating"
    VERIFIED = "verified"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    ESCALATED = "escalated"
    AUTOMATED_ACTION = "automated_action"


class DetectionMethod(Enum):
    """Detection method enumeration"""
    AI_FINGERPRINT = "ai_fingerprint"
    WEB_CRAWLER = "web_crawler"
    USER_REPORT = "user_report"
    PLATFORM_API = "platform_api"
    AUTOMATED_SCAN = "automated_scan"
    PARTNER_NOTIFICATION = "partner_notification"
    BLOCKCHAIN_VERIFICATION = "blockchain_verification"


class Platform(Enum):
    """Platform enumeration"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    REDDIT = "reddit"
    UNKNOWN = "unknown"
    OTHER = "other"


class ActionType(Enum):
    """Automated action types"""
    DMCA_TAKEDOWN = "dmca_takedown"
    CONTENT_BLOCKING = "content_blocking"
    MONETIZATION_CLAIM = "monetization_claim"
    WATERMARK_ENFORCEMENT = "watermark_enforcement"
    LEGAL_NOTICE = "legal_notice"
    ACCOUNT_FLAGGING = "account_flagging"
    REVENUE_RECOVERY = "revenue_recovery"
    LICENSING_ENFORCEMENT = "licensing_enforcement"


class ProtectionAlert(Base):
    """
    Enterprise Protection Alert Model
    
    Comprehensive alert system for content protection violations, unauthorized usage,
    and copyright infringement detection with automated response capabilities.
    """
    __tablename__ = "protection_alerts"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Alert classification
    alert_type = Column(SQLEnum(AlertType), nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.PENDING, index=True)
    detection_method = Column(SQLEnum(DetectionMethod), nullable=False)
    
    # Detection details
    detected_url = Column(Text, nullable=False)
    platform = Column(SQLEnum(Platform), nullable=True, index=True)
    platform_content_id = Column(String(255), nullable=True)
    detected_title = Column(String(500), nullable=True)
    detected_description = Column(Text, nullable=True)
    
    # Similarity and matching
    similarity_score = Column(Float, nullable=False, index=True)
    confidence_level = Column(Float, nullable=False)
    match_percentage = Column(Float, nullable=True)
    false_positive_probability = Column(Float, default=0.0)
    
    # Evidence and proof
    evidence_screenshots = Column(ARRAY(Text), nullable=True)
    evidence_metadata = Column(JSON, nullable=True)
    technical_evidence = Column(JSON, nullable=True)
    fingerprint_comparison = Column(JSON, nullable=True)
    
    # Violation details
    violation_details = Column(JSON, nullable=True)
    infringing_party = Column(JSON, nullable=True)
    estimated_reach = Column(Integer, nullable=True)
    estimated_revenue_loss = Column(Float, default=0.0)
    
    # Geographic and temporal data
    detection_location = Column(String(100), nullable=True)
    detection_timezone = Column(String(50), nullable=True)
    content_publication_date = Column(DateTime(timezone=True), nullable=True)
    first_detection_date = Column(DateTime(timezone=True), nullable=True)
    
    # Response and actions
    automated_actions = Column(JSON, nullable=True)
    manual_actions = Column(JSON, nullable=True)
    response_time = Column(Float, nullable=True)  # Response time in seconds
    resolution_time = Column(Float, nullable=True)  # Resolution time in hours
    
    # Legal and compliance
    dmca_request_sent = Column(Boolean, default=False)
    dmca_request_id = Column(String(255), nullable=True)
    legal_action_required = Column(Boolean, default=False)
    legal_notes = Column(Text, nullable=True)
    
    # Communication and notifications
    user_notified = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime(timezone=True), nullable=True)
    notification_method = Column(String(50), nullable=True)
    escalation_level = Column(Integer, default=0)
    
    # Platform response tracking
    platform_response = Column(JSON, nullable=True)
    platform_action_taken = Column(String(255), nullable=True)
    content_removed = Column(Boolean, default=False)
    content_removed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Revenue and monetization impact
    revenue_impact = Column(Float, default=0.0)
    monetization_status = Column(String(50), nullable=True)
    revenue_recovery_amount = Column(Float, default=0.0)
    recovery_success = Column(Boolean, default=False)
    
    # Analytics and tracking
    view_count_at_detection = Column(Integer, default=0)
    engagement_metrics = Column(JSON, nullable=True)
    trend_analysis = Column(JSON, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    
    # Machine learning features
    ml_prediction_confidence = Column(Float, nullable=True)
    ml_model_version = Column(String(50), nullable=True)
    feature_vector = Column(JSON, nullable=True)
    clustering_group = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    requires_human_review = Column(Boolean, default=True)
    is_recurring_violation = Column(Boolean, default=False)
    
    # Priority and workflow
    priority_score = Column(Float, default=0.0)
    assigned_to = Column(String(255), nullable=True)
    workflow_stage = Column(String(100), default="detection")
    next_action_due = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    fingerprint = relationship("ContentFingerprint", back_populates="protection_alerts")
    audit_logs = relationship("AuditLog", back_populates="protection_alert", cascade="all, delete-orphan")
    
    # Advanced indexes for performance
    __table_args__ = (
        Index('idx_alerts_fingerprint_status', 'fingerprint_id', 'status'),
        Index('idx_alerts_user_severity', 'user_id', 'severity'),
        Index('idx_alerts_platform_type', 'platform', 'alert_type'),
        Index('idx_alerts_similarity_confidence', 'similarity_score', 'confidence_level'),
        Index('idx_alerts_created_status', 'created_at', 'status'),
        Index('idx_alerts_priority_workflow', 'priority_score', 'workflow_stage'),
        Index('idx_alerts_revenue_impact', 'revenue_impact', 'recovery_success'),
        Index('idx_alerts_detection_method', 'detection_method', 'created_at'),
        Index('idx_alerts_human_review', 'requires_human_review', 'priority_score'),
    )
    
    def __repr__(self):
        return f"<ProtectionAlert(id={self.id}, type={self.alert_type.value}, severity={self.severity.value}, status={self.status.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "fingerprint_id": str(self.fingerprint_id),
            "user_id": str(self.user_id),
            "alert_type": self.alert_type.value if self.alert_type else None,
            "severity": self.severity.value if self.severity else None,
            "status": self.status.value if self.status else None,
            "detection_method": self.detection_method.value if self.detection_method else None,
            "detected_url": self.detected_url,
            "platform": self.platform.value if self.platform else None,
            "platform_content_id": self.platform_content_id,
            "detected_title": self.detected_title,
            "detected_description": self.detected_description,
            "similarity_score": self.similarity_score,
            "confidence_level": self.confidence_level,
            "match_percentage": self.match_percentage,
            "false_positive_probability": self.false_positive_probability,
            "evidence_screenshots": self.evidence_screenshots,
            "evidence_metadata": self.evidence_metadata,
            "technical_evidence": self.technical_evidence,
            "fingerprint_comparison": self.fingerprint_comparison,
            "violation_details": self.violation_details,
            "infringing_party": self.infringing_party,
            "estimated_reach": self.estimated_reach,
            "estimated_revenue_loss": self.estimated_revenue_loss,
            "detection_location": self.detection_location,
            "detection_timezone": self.detection_timezone,
            "content_publication_date": self.content_publication_date.isoformat() if self.content_publication_date else None,
            "first_detection_date": self.first_detection_date.isoformat() if self.first_detection_date else None,
            "automated_actions": self.automated_actions,
            "manual_actions": self.manual_actions,
            "response_time": self.response_time,
            "resolution_time": self.resolution_time,
            "dmca_request_sent": self.dmca_request_sent,
            "dmca_request_id": self.dmca_request_id,
            "legal_action_required": self.legal_action_required,
            "legal_notes": self.legal_notes,
            "user_notified": self.user_notified,
            "notification_sent_at": self.notification_sent_at.isoformat() if self.notification_sent_at else None,
            "notification_method": self.notification_method,
            "escalation_level": self.escalation_level,
            "platform_response": self.platform_response,
            "platform_action_taken": self.platform_action_taken,
            "content_removed": self.content_removed,
            "content_removed_at": self.content_removed_at.isoformat() if self.content_removed_at else None,
            "revenue_impact": self.revenue_impact,
            "monetization_status": self.monetization_status,
            "revenue_recovery_amount": self.revenue_recovery_amount,
            "recovery_success": self.recovery_success,
            "view_count_at_detection": self.view_count_at_detection,
            "engagement_metrics": self.engagement_metrics,
            "trend_analysis": self.trend_analysis,
            "risk_assessment": self.risk_assessment,
            "ml_prediction_confidence": self.ml_prediction_confidence,
            "ml_model_version": self.ml_model_version,
            "feature_vector": self.feature_vector,
            "clustering_group": self.clustering_group,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "requires_human_review": self.requires_human_review,
            "is_recurring_violation": self.is_recurring_violation,
            "priority_score": self.priority_score,
            "assigned_to": self.assigned_to,
            "workflow_stage": self.workflow_stage,
            "next_action_due": self.next_action_due.isoformat() if self.next_action_due else None
        }
    
    def calculate_priority_score(self) -> float:
        """Calculate dynamic priority score based on multiple factors"""
        base_score = 0.0
        
        # Severity weight
        severity_weights = {
            AlertSeverity.CRITICAL: 10.0,
            AlertSeverity.HIGH: 7.5,
            AlertSeverity.MEDIUM: 5.0,
            AlertSeverity.LOW: 2.5,
            AlertSeverity.INFO: 1.0
        }
        base_score += severity_weights.get(self.severity, 1.0)
        
        # Similarity score weight
        base_score += (self.similarity_score or 0.0) * 5.0
        
        # Revenue impact weight
        if self.estimated_revenue_loss:
            base_score += min(self.estimated_revenue_loss / 100.0, 5.0)
        
        # Reach impact weight
        if self.estimated_reach:
            base_score += min(self.estimated_reach / 1000.0, 3.0)
        
        # Confidence weight
        base_score += (self.confidence_level or 0.0) * 2.0
        
        return min(base_score, 100.0)  # Cap at 100
    
    def should_escalate(self) -> bool:
        """Determine if alert should be escalated"""
        if self.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            return True
        
        if self.similarity_score and self.similarity_score > 0.9:
            return True
        
        if self.estimated_revenue_loss and self.estimated_revenue_loss > 1000.0:
            return True
        
        if self.is_recurring_violation:
            return True
        
        return False
    
    @classmethod
    def create_from_detection(cls, detection_data: Dict[str, Any], fingerprint_id: str, user_id: str) -> 'ProtectionAlert':
        """Create ProtectionAlert from detection engine output"""
        return cls(
            fingerprint_id=fingerprint_id,
            user_id=user_id,
            alert_type=AlertType(detection_data.get('alert_type', 'copyright_violation')),
            severity=AlertSeverity(detection_data.get('severity', 'medium')),
            detection_method=DetectionMethod(detection_data.get('detection_method', 'ai_fingerprint')),
            detected_url=detection_data.get('detected_url'),
            platform=Platform(detection_data.get('platform', 'unknown')),
            platform_content_id=detection_data.get('platform_content_id'),
            detected_title=detection_data.get('detected_title'),
            detected_description=detection_data.get('detected_description'),
            similarity_score=detection_data.get('similarity_score', 0.0),
            confidence_level=detection_data.get('confidence_level', 0.0),
            match_percentage=detection_data.get('match_percentage'),
            evidence_screenshots=detection_data.get('evidence_screenshots', []),
            evidence_metadata=detection_data.get('evidence_metadata', {}),
            technical_evidence=detection_data.get('technical_evidence', {}),
            violation_details=detection_data.get('violation_details', {}),
            estimated_reach=detection_data.get('estimated_reach'),
            estimated_revenue_loss=detection_data.get('estimated_revenue_loss', 0.0),
            detection_location=detection_data.get('detection_location'),
            first_detection_date=datetime.now(timezone.utc)
        )
