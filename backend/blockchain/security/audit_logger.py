"""Security Audit Logger - IA-Influencer-Agent Platform

Security audit logging system for comprehensive tracking of all
security-related events and compliance monitoring.

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EventSeverity(Enum):
    """Security event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventCategory(Enum):
    """Security event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CRYPTOGRAPHIC = "cryptographic"
    NETWORK = "network"
    DATA_ACCESS = "data_access"
    SYSTEM = "system"
    COMPLIANCE = "compliance"


@dataclass
class AuditEvent:
    """Security audit event"""
    event_id: str
    timestamp: datetime
    category: EventCategory
    severity: EventSeverity
    event_type: str
    description: str
    user_id: Optional[str]
    source_ip: Optional[str]
    resource: Optional[str]
    outcome: str  # "success", "failure", "pending"
    metadata: Dict[str, Any]


class SecurityAuditLogger:
    """Security Audit Logging System"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.audit_events: List[AuditEvent] = []
        self.event_filters: Dict[str, Any] = {}
        
        # Retention settings
        self.max_events = config.get("max_events", 100000)
        self.retention_days = config.get("retention_days", 365)
    
    async def log_event(
        self,
        category: EventCategory,
        severity: EventSeverity,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        resource: Optional[str] = None,
        outcome: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Log security audit event"""
        try:
            import uuid
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                category=category,
                severity=severity,
                event_type=event_type,
                description=description,
                user_id=user_id,
                source_ip=source_ip,
                resource=resource,
                outcome=outcome,
                metadata=metadata or {}
            )
            
            self.audit_events.append(event)
            
            # Log to system logger based on severity
            if severity == EventSeverity.CRITICAL:
                self.logger.critical(f"SECURITY: {description}")
            elif severity == EventSeverity.HIGH:
                self.logger.error(f"SECURITY: {description}")
            elif severity == EventSeverity.MEDIUM:
                self.logger.warning(f"SECURITY: {description}")
            else:
                self.logger.info(f"SECURITY: {description}")
            
            # Maintain event limit
            if len(self.audit_events) > self.max_events:
                self.audit_events = self.audit_events[-self.max_events:]
            
            return event
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            raise
    
    async def query_events(
        self,
        category: Optional[EventCategory] = None,
        severity: Optional[EventSeverity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Query audit events with filters"""
        filtered_events = []
        
        for event in self.audit_events:
            if category and event.category != category:
                continue
            if severity and event.severity != severity:
                continue
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if user_id and event.user_id != user_id:
                continue
            
            filtered_events.append(event)
            
            if len(filtered_events) >= limit:
                break
        
        return filtered_events
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics from audit logs"""
        total_events = len(self.audit_events)
        
        # Count by severity
        severity_counts = {}
        category_counts = {}
        failure_count = 0
        
        for event in self.audit_events:
            severity = event.severity.value
            category = event.category.value
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            
            if event.outcome == "failure":
                failure_count += 1
        
        return {
            "total_events": total_events,
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "failure_rate": (failure_count / max(total_events, 1)) * 100,
            "retention_days": self.retention_days
        }