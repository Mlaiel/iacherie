"""
Monitoring Models - Protection System
====================================

Monitoring-specific data models for the protection system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from .base_models import AuditableModel

class MonitoringStatus(Enum):
    """Monitoring status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class MonitoringSession(AuditableModel):
    """Monitoring session model"""
    session_name: str = ""
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    monitoring_targets: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: float = 0.0

@dataclass
class MonitoringMetrics(AuditableModel):
    """Monitoring metrics model"""
    session_id: str = ""
    metric_name: str = ""
    metric_value: float = 0.0
    metric_unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "tags": self.tags,
            "recorded_at": self.recorded_at.isoformat(),
            "created_at": self.created_at.isoformat()
        }

# Export all models
__all__ = [
    "MonitoringStatus",
    "MonitoringSession",
    "MonitoringMetrics"
]
