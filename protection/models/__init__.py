"""
Protection Models Package
========================

Central models package for the protection system.
Contains all data models used across protection modules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .alert_models import *
from .base_models import *
from .security_models import *
from .monitoring_models import *

__all__ = [
    # Alert models
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
    "AlertCompliance",
    
    # Base models
    "BaseModel",
    "TimestampedModel",
    "AuditableModel",
    
    # Security models
    "SecurityEvent",
    "ThreatIndicator",
    "VulnerabilityReport",
    
    # Monitoring models
    "MonitoringSession",
    "MonitoringMetrics"
]
