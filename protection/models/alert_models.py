"""
Alert Models - Protection System
===============================

Core alert data models for the protection system.
Defines alert structures, rules, and configurations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field

# Optional pydantic with fallback
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class BaseModel:
    """BaseModel: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
    def Field(*args, **kwargs) -> None: return None

import uuid

class AlertPriority(Enum):
    """Alert priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(Enum):
    """Alert status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    SUPPRESSED = "suppressed"

class AlertType(Enum):
    """Alert type enumeration"""
    SECURITY_THREAT = "security_threat"
    PERFORMANCE_ISSUE = "performance_issue"
    SYSTEM_ERROR = "system_error"
    COMPLIANCE_VIOLATION = "compliance_violation"
    DATA_BREACH = "data_breach"
    ANOMALY_DETECTION = "anomaly_detection"

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    alert_type: AlertType = AlertType.SYSTEM_ERROR
    conditions: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

@dataclass
class AlertEvent:
    """Individual alert event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.OPEN
    alert_type: AlertType = AlertType.SYSTEM_ERROR
    source: str = ""
    affected_resources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    assigned_to: Optional[str] = None

@dataclass
class AlertNotification:
    """Alert notification configuration"""
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    channel: str = "email"
    recipients: List[str] = field(default_factory=list)
    template: str = ""
    sent_at: Optional[datetime] = None
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class AlertConfiguration:
    """Global alert system configuration"""
    max_alerts_per_minute: int = 100
    alert_retention_days: int = 30
    notification_batch_size: int = 50
    escalation_timeout_minutes: int = 60
    auto_resolve_timeout_hours: int = 24
    enable_correlation: bool = True
    enable_suppression: bool = True
    default_severity: AlertSeverity = AlertSeverity.MEDIUM

@dataclass
class AlertResponse:
    """Alert response tracking"""
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    responder: str = ""
    action_taken: str = ""
    response_time_seconds: float = 0.0
    resolution_notes: str = ""
    effectiveness_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AlertEscalation:
    """Alert escalation configuration"""
    escalation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    escalation_levels: List[Dict[str, Any]] = field(default_factory=list)
    current_level: int = 0
    max_level: int = 3
    escalation_interval_minutes: int = 30
    auto_escalate: bool = True

@dataclass
class AlertMetrics:
    """Alert system metrics"""
    total_alerts: int = 0
    open_alerts: int = 0
    critical_alerts: int = 0
    average_resolution_time_minutes: float = 0.0
    false_positive_rate: float = 0.0
    system_availability: float = 100.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AlertAudit:
    """Alert audit trail"""
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    action: str = ""
    user: str = ""
    old_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class ThreatIntelligenceAlert:
    """Threat intelligence based alert"""
    threat_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    threat_type: str = ""
    ioc_type: str = ""  # Indicator of Compromise
    ioc_value: str = ""
    threat_level: AlertSeverity = AlertSeverity.MEDIUM
    confidence_score: float = 0.0
    threat_source: str = ""
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: Optional[datetime] = None
    related_campaigns: List[str] = field(default_factory=list)

@dataclass
class AlertWorkflow:
    """Alert workflow definition"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    workflow_steps: List[Dict[str, Any]] = field(default_factory=list)
    approval_required: bool = False
    auto_execute: bool = False
    timeout_minutes: int = 60
    created_by: str = ""
    version: str = "1.0"

@dataclass
class AlertCorrelation:
    """Alert correlation configuration"""
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_rules: List[Dict[str, Any]] = field(default_factory=list)
    time_window_minutes: int = 15
    correlation_threshold: int = 3
    enabled: bool = True
    last_correlation: Optional[datetime] = None

@dataclass
class AlertEnrichment:
    """Alert enrichment data"""
    enrichment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    enrichment_source: str = ""
    enrichment_data: Dict[str, Any] = field(default_factory=dict)
    confidence_level: float = 0.0
    enriched_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AlertSuppression:
    """Alert suppression rules"""
    suppression_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str = ""
    suppression_criteria: Dict[str, Any] = field(default_factory=dict)
    suppression_duration_minutes: int = 60
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class AlertTemplate:
    """Alert notification template"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_name: str = ""
    template_type: str = "email"
    subject_template: str = ""
    body_template: str = ""
    variables: List[str] = field(default_factory=list)
    created_by: str = ""
    version: str = "1.0"

@dataclass
class AlertBatch:
    """Alert batch processing"""
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    batch_type: str = ""
    alert_ids: List[str] = field(default_factory=list)
    batch_status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    processing_result: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertForensics:
    """Alert forensics data"""
    forensics_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    evidence_collected: List[Dict[str, Any]] = field(default_factory=list)
    forensics_analyst: str = ""
    analysis_status: str = "pending"
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AlertCompliance:
    """Alert compliance tracking"""
    compliance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    compliance_framework: str = ""
    compliance_requirements: List[str] = field(default_factory=list)
    compliance_status: str = "pending"
    compliance_notes: str = ""
    reviewed_by: str = ""
    reviewed_at: Optional[datetime] = None

# Additional classes for compatibility
@dataclass
class Alert:
    """Main alert class (alias for AlertEvent)"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    priority: AlertPriority = AlertPriority.NORMAL
    status: AlertStatus = AlertStatus.OPEN
    alert_type: AlertType = AlertType.SYSTEM_ERROR
    source: str = ""
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertHistory:
    """Alert history tracking"""
    history_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    action: str = ""
    old_status: Optional[AlertStatus] = None
    new_status: Optional[AlertStatus] = None
    user: str = ""
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

# Export all models
__all__ = [
    "AlertPriority",
    "AlertSeverity",
    "AlertStatus", 
    "AlertType",
    "Alert",
    "AlertHistory",
    "AlertRule",
    "AlertEvent",
    "AlertNotification",
    "AlertConfiguration",
    "AlertResponse",
    "AlertEscalation",
    "AlertMetrics",
    "AlertAudit",
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
