"""Protection and Security Schemas

Comprehensive Pydantic schemas for content protection, threat detection,
and security monitoring in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class AlertSeverityEnum(str, Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class AlertStatusEnum(str, Enum):
    """Alert processing status"""    PENDING = "pending"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    ESCALATED = "escalated"


class ThreatTypeEnum(str, Enum):
    """Types of detected threats"""    UNAUTHORIZED_USE = "unauthorized_use"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    CONTENT_THEFT = "content_theft"
    DEEP_FAKE = "deep_fake"
    IMPERSONATION = "impersonation"
    PLAGIARISM = "plagiarism"
    REVENUE_THEFT = "revenue_theft"
    BRAND_MISUSE = "brand_misuse"
    SPAM_CONTENT = "spam_content"


class PlatformEnum(str, Enum):
    """Supported platforms for monitoring"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    WEBSITE = "website"
    OTHER = "other"


class ActionTypeEnum(str, Enum):
    """Actions that can be taken on threats"""    TAKEDOWN_REQUEST = "takedown_request"
    DMCA_NOTICE = "dmca_notice"
    COPYRIGHT_CLAIM = "copyright_claim"
    LEGAL_ACTION = "legal_action"
    CONTENT_BLOCKING = "content_blocking"
    ACCOUNT_REPORTING = "account_reporting"
    MONETIZATION_CLAIM = "monetization_claim"
    CEASE_DESIST = "cease_desist"
    MANUAL_REVIEW = "manual_review"
    AUTOMATED_REMOVAL = "automated_removal"


class EvidenceTypeEnum(str, Enum):
    """Types of evidence collected"""    SCREENSHOT = "screenshot"
    VIDEO_RECORDING = "video_recording"
    METADATA_CAPTURE = "metadata_capture"
    HTML_SOURCE = "html_source"
    API_RESPONSE = "api_response"
    NETWORK_TRACE = "network_trace"
    TIMESTAMP_PROOF = "timestamp_proof"
    HASH_COMPARISON = "hash_comparison"


class ProtectionLevelEnum(str, Enum):
    """Protection monitoring levels"""    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ThreatIntelligenceSchema(BaseModel):
    """Schema for threat intelligence data"""    threat_id: str = Field(..., description="Unique threat identifier")
    threat_type: ThreatTypeEnum = Field(..., description="Type of threat detected")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Threat confidence score")
    risk_level: AlertSeverityEnum = Field(..., description="Risk level assessment")
    geographic_location: Optional[str] = Field(None, description="Geographic location of threat")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    referrer_url: Optional[HttpUrl] = Field(None, description="Referrer URL")
    attack_patterns: Optional[List[str]] = Field(None, description="Identified attack patterns")
    indicators_of_compromise: Optional[List[str]] = Field(None, description="IOCs detected")
    mitigation_suggestions: Optional[List[str]] = Field(None, description="Suggested mitigations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "threat_id": "THR-2024-001234",
                "threat_type": "unauthorized_use",
                "confidence_score": 0.89,
                "risk_level": "high",
                "geographic_location": "Unknown",
                "attack_patterns": ["content_scraping", "metadata_manipulation"]
            }
        }


class EvidenceCollectionSchema(BaseModel):
    """Schema for evidence collection"""    evidence_id: str = Field(..., description="Unique evidence identifier")
    evidence_type: EvidenceTypeEnum = Field(..., description="Type of evidence")
    file_path: Optional[str] = Field(None, description="Path to evidence file")
    file_size: Optional[PositiveInt] = Field(None, description="Evidence file size")
    file_hash: Optional[str] = Field(None, description="Evidence file hash")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Evidence metadata")
    collection_timestamp: datetime = Field(..., description="When evidence was collected")
    collection_method: str = Field(..., description="Method used to collect evidence")
    authenticity_verified: bool = Field(False, description="Whether authenticity is verified")
    legal_admissibility: bool = Field(False, description="Whether legally admissible")
    retention_period: Optional[int] = Field(None, description="Retention period in days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence_id": "EVD-2024-001234",
                "evidence_type": "screenshot",
                "file_size": 1048576,
                "file_hash": "sha256:a1b2c3...",
                "collection_method": "automated_crawler",
                "authenticity_verified": True
            }
        }


class ProtectionAlertBaseSchema(BaseModel):
    """Base schema for protection alerts"""    fingerprint_id: PositiveInt = Field(..., description="Associated content fingerprint ID")
    detected_url: HttpUrl = Field(..., description="URL where violation was detected")
    platform: PlatformEnum = Field(..., description="Platform where violation occurred")
    threat_type: ThreatTypeEnum = Field(..., description="Type of threat detected")
    severity: AlertSeverityEnum = Field(..., description="Alert severity level")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Content similarity score")
    
    # Detection details
    detection_method: str = Field(..., description="Method used for detection")
    detection_timestamp: datetime = Field(..., description="When violation was detected")
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")
    
    # Content details
    infringing_title: Optional[str] = Field(None, description="Title of infringing content")
    infringing_description: Optional[str] = Field(None, description="Description of infringing content")
    infringing_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata of infringing content")
    
    # Infringer details
    infringer_username: Optional[str] = Field(None, description="Username of infringer")
    infringer_profile_url: Optional[HttpUrl] = Field(None, description="Profile URL of infringer")
    infringer_email: Optional[str] = Field(None, description="Email of infringer if available")
    infringer_history: Optional[List[str]] = Field(None, description="Previous infringement history")
    
    # Technical details
    page_html: Optional[str] = Field(None, description="HTML source of infringing page")
    response_headers: Optional[Dict[str, str]] = Field(None, description="HTTP response headers")
    network_info: Optional[Dict[str, Any]] = Field(None, description="Network information")
    
    @field_validator('similarity_score')
    @classmethod
    def validate_similarity_score(cls, v):
        """Validate similarity score is within acceptable range"""        if v < 0.5:
            raise ValueError("Similarity score must be at least 0.5 for valid alerts")
        return v


class ProtectionAlertCreateSchema(ProtectionAlertBaseSchema):
    """Schema for creating protection alerts"""    user_id: PositiveInt = Field(..., description="User ID who owns the content")
    auto_action_enabled: bool = Field(False, description="Enable automatic actions")
    notification_enabled: bool = Field(True, description="Enable notifications")
    priority_level: int = Field(5, ge=1, le=10, description="Priority level (1-10)")
    
    # Evidence collection
    collect_evidence: bool = Field(True, description="Whether to collect evidence")
    evidence_types: Optional[List[EvidenceTypeEnum]] = Field(None, description="Types of evidence to collect")
    
    # Threat intelligence
    threat_intelligence: Optional[ThreatIntelligenceSchema] = Field(None, description="Threat intelligence data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "fingerprint_id": 456,
                "detected_url": "https://youtube.com/watch?v=stolen_content",
                "platform": "youtube",
                "threat_type": "unauthorized_use",
                "severity": "high",
                "similarity_score": 0.95,
                "detection_method": "ai_fingerprint_matching",
                "auto_action_enabled": True
            }
        }


class ProtectionAlertUpdateSchema(BaseModel):
    """Schema for updating protection alerts"""    status: Optional[AlertStatusEnum] = Field(None, description="Updated alert status")
    severity: Optional[AlertSeverityEnum] = Field(None, description="Updated severity")
    assigned_to: Optional[PositiveInt] = Field(None, description="User ID of assignee")
    notes: Optional[str] = Field(None, description="Investigation notes")
    false_positive_reason: Optional[str] = Field(None, description="Reason if false positive")
    resolution_notes: Optional[str] = Field(None, description="Resolution details")
    evidence_verified: Optional[bool] = Field(None, description="Whether evidence is verified")
    legal_action_required: Optional[bool] = Field(None, description="Whether legal action needed")
    priority_level: Optional[int] = Field(None, ge=1, le=10, description="Updated priority")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "confirmed",
                "assigned_to": 789,
                "notes": "Verified as unauthorized use of copyrighted material",
                "evidence_verified": True,
                "legal_action_required": False
            }
        }


class ProtectionActionSchema(BaseModel):
    """Schema for protection actions taken"""    action_id: str = Field(..., description="Unique action identifier")
    action_type: ActionTypeEnum = Field(..., description="Type of action taken")
    platform: PlatformEnum = Field(..., description="Platform where action was taken")
    action_timestamp: datetime = Field(..., description="When action was executed")
    status: str = Field(..., description="Status of the action")
    response_received: bool = Field(False, description="Whether response was received")
    response_details: Optional[Dict[str, Any]] = Field(None, description="Response details")
    success_rate: Optional[float] = Field(None, description="Success rate of action type")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    follow_up_required: bool = Field(False, description="Whether follow-up is required")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_id": "ACT-2024-001234",
                "action_type": "dmca_notice",
                "platform": "youtube",
                "status": "submitted",
                "response_received": False,
                "follow_up_required": True
            }
        }


class ProtectionAlertResponseSchema(ProtectionAlertBaseSchema):
    """Schema for protection alert responses"""    id: PositiveInt = Field(..., description="Unique alert ID")
    user_id: PositiveInt = Field(..., description="Owner user ID")
    alert_reference: str = Field(..., description="Human-readable alert reference")
    
    # Status and processing
    status: AlertStatusEnum = Field(..., description="Current alert status")
    assigned_to: Optional[PositiveInt] = Field(None, description="Assigned user ID")
    investigation_progress: float = Field(0.0, ge=0.0, le=1.0, description="Investigation progress")
    
    # Evidence and intelligence
    evidence_collected: List[EvidenceCollectionSchema] = Field([], description="Collected evidence")
    threat_intelligence: Optional[ThreatIntelligenceSchema] = Field(None, description="Threat intelligence")
    
    # Actions taken
    actions_taken: List[ProtectionActionSchema] = Field([], description="Actions taken")
    auto_actions_enabled: bool = Field(False, description="Automatic actions enabled")
    
    # Financial impact
    estimated_revenue_loss: Optional[Decimal] = Field(None, description="Estimated revenue loss")
    recovery_amount: Optional[Decimal] = Field(None, description="Amount recovered")
    legal_costs: Optional[Decimal] = Field(None, description="Legal costs incurred")
    
    # Timestamps and tracking
    created_at: datetime = Field(..., description="Alert creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    # Performance metrics
    response_time_hours: Optional[float] = Field(None, description="Response time in hours")
    resolution_time_hours: Optional[float] = Field(None, description="Resolution time in hours")
    accuracy_score: Optional[float] = Field(None, description="Alert accuracy score")
    
    # Notes and communication
    investigation_notes: Optional[str] = Field(None, description="Investigation notes")
    communication_log: Optional[List[Dict]] = Field(None, description="Communication history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "user_id": 123,
                "alert_reference": "ALT-2024-001234",
                "status": "investigating",
                "fingerprint_id": 456,
                "platform": "youtube",
                "similarity_score": 0.95,
                "estimated_revenue_loss": "150.00",
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class ProtectionDashboardSchema(BaseModel):
    """Schema for protection dashboard metrics"""    total_alerts: int = Field(..., description="Total number of alerts")
    active_alerts: int = Field(..., description="Number of active alerts")
    resolved_alerts: int = Field(..., description="Number of resolved alerts")
    false_positives: int = Field(..., description="Number of false positives")
    
    # Severity breakdown
    alerts_by_severity: Dict[str, int] = Field(..., description="Alerts grouped by severity")
    alerts_by_platform: Dict[str, int] = Field(..., description="Alerts grouped by platform")
    alerts_by_threat_type: Dict[str, int] = Field(..., description="Alerts grouped by threat type")
    
    # Performance metrics
    average_response_time: float = Field(..., description="Average response time in hours")
    average_resolution_time: float = Field(..., description="Average resolution time in hours")
    accuracy_rate: float = Field(..., description="Overall accuracy rate")
    false_positive_rate: float = Field(..., description="False positive rate")
    
    # Financial impact
    total_revenue_protected: Decimal = Field(..., description="Total revenue protected")
    estimated_losses_prevented: Decimal = Field(..., description="Estimated losses prevented")
    recovery_success_rate: float = Field(..., description="Recovery success rate")
    
    # Trend data
    alerts_trend: List[Dict] = Field(..., description="Alert trends over time")
    threat_evolution: List[Dict] = Field(..., description="Threat pattern evolution")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_alerts": 1250,
                "active_alerts": 45,
                "resolved_alerts": 1150,
                "false_positives": 55,
                "average_response_time": 2.5,
                "total_revenue_protected": "125000.00",
                "accuracy_rate": 0.94
            }
        }


class ThreatDetectionConfigSchema(BaseModel):
    """Schema for threat detection configuration"""    user_id: PositiveInt = Field(..., description="User ID")
    protection_level: ProtectionLevelEnum = Field(..., description="Protection level")
    
    # Detection settings
    similarity_threshold: float = Field(0.8, ge=0.5, le=1.0, description="Similarity detection threshold")
    auto_action_threshold: float = Field(0.95, ge=0.8, le=1.0, description="Auto-action threshold")
    monitoring_frequency: int = Field(24, ge=1, le=168, description="Monitoring frequency in hours")
    
    # Platform settings
    enabled_platforms: List[PlatformEnum] = Field(..., description="Platforms to monitor")
    platform_priorities: Dict[str, int] = Field(..., description="Platform priority levels")
    
    # Alert settings
    notification_email: bool = Field(True, description="Enable email notifications")
    notification_sms: bool = Field(False, description="Enable SMS notifications")
    notification_webhook: Optional[HttpUrl] = Field(None, description="Webhook URL for notifications")
    
    # Action settings
    auto_dmca_enabled: bool = Field(False, description="Enable automatic DMCA notices")
    auto_takedown_enabled: bool = Field(False, description="Enable automatic takedown requests")
    legal_escalation_enabled: bool = Field(False, description="Enable legal escalation")
    
    # Evidence collection
    collect_screenshots: bool = Field(True, description="Collect screenshot evidence")
    collect_metadata: bool = Field(True, description="Collect metadata evidence")
    collect_source_code: bool = Field(False, description="Collect HTML source evidence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "protection_level": "enhanced",
                "similarity_threshold": 0.85,
                "enabled_platforms": ["youtube", "instagram", "tiktok"],
                "notification_email": True,
                "auto_dmca_enabled": True
            }
        }


class SecurityAuditSchema(BaseModel):
    """Schema for security audit logs"""    audit_id: str = Field(..., description="Unique audit identifier")
    user_id: PositiveInt = Field(..., description="User ID")
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource affected")
    timestamp: datetime = Field(..., description="Audit timestamp")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    success: bool = Field(..., description="Whether action was successful")
    risk_level: AlertSeverityEnum = Field(..., description="Risk level of action")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "AUD-2024-001234",
                "user_id": 123,
                "action": "protection_alert_created",
                "resource": "alert_12345",
                "success": True,
                "risk_level": "low"
            }
        }


# Export schemas
__all__ = [
    # Enums
    "AlertSeverityEnum",
    "AlertStatusEnum",
    "ThreatTypeEnum",
    "PlatformEnum",
    "ActionTypeEnum",
    "EvidenceTypeEnum",
    "ProtectionLevelEnum",
    
    # Complex schemas
    "ThreatIntelligenceSchema",
    "EvidenceCollectionSchema",
    "ProtectionActionSchema",
    
    # Main alert schemas
    "ProtectionAlertBaseSchema",
    "ProtectionAlertCreateSchema",
    "ProtectionAlertUpdateSchema",
    "ProtectionAlertResponseSchema",
    
    # Dashboard and configuration
    "ProtectionDashboardSchema",
    "ThreatDetectionConfigSchema",
    "SecurityAuditSchema"
]
