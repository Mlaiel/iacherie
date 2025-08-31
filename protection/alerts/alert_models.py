"""Content Protection Alert Models - IA Influencer Agent Enterprise System
Created by: Fahed Mlaiel (mlaiel@live.de)

WARNING: This code is proprietary and confidential. Any unauthorized use, reproduction, 
or distribution is strictly prohibited without explicit written permission from Fahed Mlaiel.
Legal action will be taken against any violation of intellectual property rights.
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Ultra-advanced enterprise-grade alert system models for AI-powered content protection,
multi-format fingerprinting, automated DMCA enforcement, and revenue protection.
Business Logic: Content creators → AI protection → threat detection → automated response → monetization
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
import uuid


class AlertSeverity(Enum):
    """Alert severity levels for content protection incidents."""    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """Alert status tracking states."""    
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


class AlertCategory(Enum):
    """Content protection alert categories."""    
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_DISTRIBUTION = "unauthorized_distribution"
    CONTENT_THEFT = "content_theft"
    PLAGIARISM = "plagiarism"
    DEEPFAKE_DETECTION = "deepfake_detection"
    WATERMARK_REMOVAL = "watermark_removal"
    METADATA_TAMPERING = "metadata_tampering"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_ANOMALY = "system_anomaly"


class EscalationLevel(Enum):
    """Alert escalation levels."""    
    LEVEL_0 = "automated_response"
    LEVEL_1 = "support_team"
    LEVEL_2 = "senior_support"
    LEVEL_3 = "legal_team"
    LEVEL_4 = "executive_team"


@dataclass
class AlertMetadata:
    """Metadata container for alert additional information."""    
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None
    device_fingerprint: Optional[str] = None
    session_id: Optional[str] = None
    request_headers: Optional[Dict[str, str]] = None
    ai_confidence_score: Optional[float] = None
    risk_indicators: List[str] = field(default_factory=list)
    evidence_urls: List[str] = field(default_factory=list)
    related_alerts: List[str] = field(default_factory=list)


class AlertEvidenceModel(BaseModel):
    """Evidence model for content protection alerts."""    
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str = Field(..., description="Type of evidence collected")
    content_hash: str = Field(..., description="Content hash for verification")
    file_path: Optional[str] = Field(None, description="Path to evidence file")
    url: Optional[str] = Field(None, description="URL where evidence was found")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    collector_agent: str = Field(..., description="Agent that collected evidence")
    verification_status: str = Field(default="pending", description="Evidence verification status")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('evidence_type')
    def validate_evidence_type(cls, v):
        valid_types = [
            'screenshot', 'video_frame', 'audio_sample', 'document',
            'metadata_dump', 'network_trace', 'system_log', 'user_action'
        ]
        if v not in valid_types:
            raise ValueError(f"Evidence type must be one of: {valid_types}")
        return v


class AlertActionModel(BaseModel):
    """Action model for alert responses and escalations."""    
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str = Field(..., description="Type of action taken")
    actor: str = Field(..., description="Who performed the action")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field(..., description="Action description")
    result: Optional[str] = Field(None, description="Action result")
    next_steps: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentProtectionAlert(BaseModel):
    """Main alert model for content protection incidents."""    
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Detailed alert description")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    status: AlertStatus = Field(default=AlertStatus.ACTIVE)
    category: AlertCategory = Field(..., description="Alert category")
    
    # Timing
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = Field(None)
    
    # Content identification
    content_id: str = Field(..., description="Protected content identifier")
    content_owner: str = Field(..., description="Content owner identifier")
    content_type: str = Field(..., description="Type of protected content")
    
    # Detection details
    detection_method: str = Field(..., description="How the threat was detected")
    ai_model_version: str = Field(..., description="AI model version used")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    
    # Location and source
    source_platform: Optional[str] = Field(None, description="Platform where threat detected")
    source_url: Optional[str] = Field(None, description="URL of the threat")
    threat_actor: Optional[str] = Field(None, description="Identified threat actor")
    
    # Evidence and metadata
    evidence: List[AlertEvidenceModel] = Field(default_factory=list)
    metadata: AlertMetadata = Field(default_factory=AlertMetadata)
    
    # Response tracking
    actions_taken: List[AlertActionModel] = Field(default_factory=list)
    assigned_to: Optional[str] = Field(None, description="Alert assignee")
    escalation_level: EscalationLevel = Field(default=EscalationLevel.LEVEL_0)
    
    # Business impact
    potential_loss: Optional[float] = Field(None, description="Estimated financial impact")
    affected_users: int = Field(default=0, description="Number of affected users")
    business_priority: str = Field(default="normal", description="Business priority level")
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v
    
    def add_evidence(self, evidence: AlertEvidenceModel) -> None:
        """Add evidence to the alert."""        self.evidence.append(evidence)
        self.updated_at = datetime.now(timezone.utc)
    
    def add_action(self, action: AlertActionModel) -> None:
        """Add action to the alert."""        self.actions_taken.append(action)
        self.updated_at = datetime.now(timezone.utc)
    
    def escalate(self, new_level: EscalationLevel, reason: str, actor: str) -> None:
        """Escalate alert to higher level."""        self.escalation_level = new_level
        escalation_action = AlertActionModel(
            action_type="escalation",
            actor=actor,
            description=f"Escalated to {new_level.value}: {reason}"
        )
        self.add_action(escalation_action)
        self.status = AlertStatus.ESCALATED
    
    def resolve(self, resolution: str, actor: str) -> None:
        """Mark alert as resolved."""        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.now(timezone.utc)
        resolution_action = AlertActionModel(
            action_type="resolution",
            actor=actor,
            description=f"Alert resolved: {resolution}"
        )
        self.add_action(resolution_action)


class NotificationPreferences(BaseModel):
    """User notification preferences for alerts."""    
    user_id: str = Field(..., description="User identifier")
    email_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=False)
    push_enabled: bool = Field(default=True)
    webhook_enabled: bool = Field(default=False)
    
    # Severity filters
    min_severity: AlertSeverity = Field(default=AlertSeverity.MEDIUM)
    categories: List[AlertCategory] = Field(default_factory=list)
    
    # Timing preferences
    quiet_hours_start: Optional[str] = Field(None, description="HH:MM format")
    quiet_hours_end: Optional[str] = Field(None, description="HH:MM format")
    timezone: str = Field(default="UTC")
    
    # Contact details
    email_address: Optional[str] = Field(None)
    phone_number: Optional[str] = Field(None)
    webhook_url: Optional[str] = Field(None)


class AlertDashboardMetrics(BaseModel):
    """Dashboard metrics for alert monitoring."""    
    total_alerts: int = Field(default=0)
    active_alerts: int = Field(default=0)
    critical_alerts: int = Field(default=0)
    resolved_today: int = Field(default=0)
    avg_resolution_time: float = Field(default=0.0)
    false_positive_rate: float = Field(default=0.0)
    
    # Category breakdown
    alerts_by_category: Dict[str, int] = Field(default_factory=dict)
    alerts_by_severity: Dict[str, int] = Field(default_factory=dict)
    alerts_by_status: Dict[str, int] = Field(default_factory=dict)
    
    # Time series data
    hourly_counts: List[int] = Field(default_factory=list)
    daily_counts: List[int] = Field(default_factory=list)
    
    # Performance metrics
    detection_accuracy: float = Field(default=0.0)
    response_time_p95: float = Field(default=0.0)
    escalation_rate: float = Field(default=0.0)
    
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MLClassificationResult(BaseModel):
    """ML classification result for content analysis."""    
    classification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_hash: str = Field(..., description="Content identifier hash")
    model_name: str = Field(..., description="ML model used")
    model_version: str = Field(..., description="Model version")
    
    # Classification results
    predicted_class: str = Field(..., description="Predicted threat class")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    probability_distribution: Dict[str, float] = Field(default_factory=dict)
    
    # Feature analysis
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    anomaly_score: Optional[float] = Field(None)
    risk_factors: List[str] = Field(default_factory=list)
    
    # Processing details
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Validation
    human_verified: bool = Field(default=False)
    feedback_score: Optional[float] = Field(None)
    validation_notes: Optional[str] = Field(None)


# Alert rule models for dynamic alert configuration
class AlertRuleCondition(BaseModel):
    """Individual condition for alert rules."""    
    field: str = Field(..., description="Field to evaluate")
    operator: str = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")
    logical_operator: str = Field(default="AND", description="AND/OR with next condition")


class AlertRule(BaseModel):
    """Dynamic alert rule configuration."""    
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    enabled: bool = Field(default=True)
    
    # Rule conditions
    conditions: List[AlertRuleCondition] = Field(..., min_items=1)
    severity: AlertSeverity = Field(..., description="Alert severity when triggered")
    category: AlertCategory = Field(..., description="Alert category")
    
    # Actions
    auto_escalate: bool = Field(default=False)
    auto_resolve: bool = Field(default=False)
    notification_targets: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: str = Field(..., description="Rule creator")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Advanced Enterprise Alert Models

class ThreatIntelligenceAlert(BaseModel):
    """Advanced threat intelligence alert for content protection"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = Field(..., description="Associated alert ID")
    threat_type: str = Field(..., description="Type of threat detected")
    threat_source: str = Field(..., description="Source of threat intelligence")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence level")
    ioc_indicators: List[Dict[str, Any]] = Field(default_factory=list, description="Indicators of compromise")
    attribution: Optional[Dict[str, Any]] = Field(None, description="Threat attribution data")
    mitigation_recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertWorkflow(BaseModel):
    """Enterprise alert workflow management"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    trigger_conditions: List[Dict[str, Any]] = Field(..., description="Conditions to trigger workflow")
    workflow_steps: List[Dict[str, Any]] = Field(..., description="Automated workflow steps")
    approval_required: bool = Field(default=False, description="Whether approval is required")
    approvers: List[str] = Field(default_factory=list, description="List of authorized approvers")
    sla_minutes: Optional[int] = Field(None, description="SLA in minutes")
    success_criteria: Dict[str, Any] = Field(default_factory=dict)
    failure_handling: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertCorrelation(BaseModel):
    """Advanced alert correlation for enterprise threat detection"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    primary_alert_id: str = Field(..., description="Primary alert ID")
    correlated_alert_ids: List[str] = Field(..., description="Correlated alert IDs")
    correlation_type: str = Field(..., description="Type of correlation")
    correlation_score: float = Field(..., ge=0.0, le=1.0, description="Correlation strength")
    time_window_minutes: int = Field(..., description="Time window for correlation")
    root_cause_analysis: Optional[Dict[str, Any]] = Field(None)
    threat_pattern: Optional[str] = Field(None, description="Identified threat pattern")
    recommended_actions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertEnrichment(BaseModel):
    """Alert enrichment with external data sources"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = Field(..., description="Associated alert ID")
    enrichment_source: str = Field(..., description="Source of enrichment data")
    enrichment_data: Dict[str, Any] = Field(..., description="Enriched data")
    confidence_level: float = Field(..., ge=0.0, le=1.0)
    geolocation_data: Optional[Dict[str, Any]] = Field(None)
    reputation_data: Optional[Dict[str, Any]] = Field(None)
    historical_context: Optional[Dict[str, Any]] = Field(None)
    risk_assessment: Optional[Dict[str, Any]] = Field(None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertSuppression(BaseModel):
    """Advanced alert suppression for noise reduction"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Suppression rule name")
    description: Optional[str] = Field(None)
    suppression_type: str = Field(..., description="Type of suppression")
    criteria: Dict[str, Any] = Field(..., description="Suppression criteria")
    duration_minutes: Optional[int] = Field(None, description="Suppression duration")
    max_suppressed_alerts: Optional[int] = Field(None)
    whitelist_patterns: List[str] = Field(default_factory=list)
    blacklist_patterns: List[str] = Field(default_factory=list)
    enabled: bool = Field(default=True)
    created_by: str = Field(..., description="Creator of suppression rule")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertTemplate(BaseModel):
    """Enterprise alert template for standardized responses"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Template name")
    category: AlertCategory = Field(..., description="Alert category")
    severity: AlertSeverity = Field(..., description="Default severity")
    template_content: Dict[str, Any] = Field(..., description="Template content structure")
    notification_channels: List[str] = Field(default_factory=list)
    escalation_policy: Optional[str] = Field(None)
    auto_actions: List[Dict[str, Any]] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    version: str = Field(default="1.0")
    created_by: str = Field(..., description="Template creator")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertBatch(BaseModel):
    """Batch processing for high-volume alert scenarios"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    batch_name: str = Field(..., description="Batch processing name")
    alert_ids: List[str] = Field(..., description="List of alert IDs in batch")
    batch_type: str = Field(..., description="Type of batch operation")
    processing_status: str = Field(default="pending")
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    created_by: str = Field(..., description="Batch creator")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertForensics(BaseModel):
    """Advanced forensic data for enterprise investigations"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = Field(..., description="Associated alert ID")
    evidence_chain: List[Dict[str, Any]] = Field(..., description="Chain of evidence")
    digital_fingerprints: List[str] = Field(default_factory=list)
    network_artifacts: Dict[str, Any] = Field(default_factory=dict)
    file_hashes: Dict[str, str] = Field(default_factory=dict)
    timeline_events: List[Dict[str, Any]] = Field(default_factory=list)
    witness_accounts: List[Dict[str, Any]] = Field(default_factory=list)
    legal_holds: List[str] = Field(default_factory=list)
    chain_of_custody: List[Dict[str, Any]] = Field(default_factory=list)
    investigation_notes: str = Field(default="")
    created_by: str = Field(..., description="Forensic investigator")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlertCompliance(BaseModel):
    """Compliance and regulatory tracking for alerts"""    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = Field(..., description="Associated alert ID")
    compliance_frameworks: List[str] = Field(..., description="Applicable compliance frameworks")
    regulatory_requirements: List[str] = Field(default_factory=list)
    compliance_status: str = Field(default="pending")
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    retention_period_days: int = Field(default=2555)  # 7 years default
    legal_obligations: List[str] = Field(default_factory=list)
    privacy_implications: Dict[str, Any] = Field(default_factory=dict)
    data_classification: str = Field(default="confidential")
    breach_notification_required: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Export all models
__all__ = [
    "ContentProtectionAlert",
    "AlertSeverity", 
    "AlertStatus",
    "AlertCategory",
    "EscalationLevel",
    "AlertEvidenceModel",
    "AlertActionModel", 
    "AlertMetadata",
    "NotificationPreferences",
    "AlertDashboardMetrics",
    "MLClassificationResult",
    "AlertRule",
    "AlertRuleCondition",
    "ThreatIntelligenceAlert",
    "AlertWorkflow",
    "AlertCorrelation", 
    "AlertEnrichment",
    "AlertSuppression",
    "AlertTemplate",
    "AlertBatch",
    "AlertForensics",
    "AlertCompliance"
]
    last_triggered: Optional[datetime] = Field(None)
    trigger_count: int = Field(default=0)
