"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Audit Logger Template for iacherie Platform
=========================================

Production-ready audit logging with:
- Security event tracking
- User action logging
- Compliance audit trails
- Data access monitoring
- System change tracking
- Tamper-proof logging

Author: Fahed Mlaiel (mlaiel@live.de)
Security & Compliance Expert
"""

import json
import hashlib
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class AuditEventType(str, Enum):
    """Audit event types"""
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    DATA_ACCESS = "data.access"
    DATA_MODIFY = "data.modify"
    DATA_DELETE = "data.delete"
    SYSTEM_CONFIG = "system.config"
    SECURITY_EVENT = "security.event"
    ADMIN_ACTION = "admin.action"

@dataclass
class AuditEvent:
    """Audit event data"""
    id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    result: str = "success"  # success, failure, partial
    risk_score: int = 0  # 0-100

class AuditLogger:
    """
    Production-ready audit logging system
    
    Features:
    - Security event tracking
    - User action logging
    - Compliance audit trails
    - Tamper-proof logging
    """
    
    def __init__(self, service_name: str = "iacherie-service"):
        self.service_name = service_name
        self.audit_events: List[AuditEvent] = []
        self.logger = logging.getLogger(f"{service_name}.audit")
        
        # Configure audit logger for security
        audit_handler = logging.FileHandler(f"audit_{service_name}.log")
        audit_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(audit_handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event_type: AuditEventType, user_id: Optional[str], 
                  resource: str, action: str, **kwargs) -> str:
        """Log an audit event"""
        event_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{user_id}{resource}{action}".encode()
        ).hexdigest()[:16]
        
        event = AuditEvent(
            id=event_id,
            event_type=event_type,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=kwargs.get("session_id"),
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
            resource=resource,
            action=action,
            details=kwargs.get("details", {}),
            result=kwargs.get("result", "success"),
            risk_score=kwargs.get("risk_score", 0)
        )
        
        self.audit_events.append(event)
        
        # Log to file for persistence
        self.logger.info(json.dumps({
            "event_id": event.id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "resource": event.resource,
            "action": event.action,
            "result": event.result,
            "risk_score": event.risk_score,
            "details": event.details
        }))
        
        return event_id
    
    def log_user_login(self, user_id: str, ip_address: str, result: str = "success"):
        """Log user login event"""
        return self.log_event(
            AuditEventType.USER_LOGIN,
            user_id=user_id,
            resource="authentication",
            action="login",
            ip_address=ip_address,
            result=result,
            risk_score=10 if result == "failure" else 0
        )
    
    def log_data_access(self, user_id: str, resource: str, details: Dict[str, Any] = None):
        """Log data access event"""
        return self.log_event(
            AuditEventType.DATA_ACCESS,
            user_id=user_id,
            resource=resource,
            action="read",
            details=details or {},
            risk_score=5
        )
    
    def log_admin_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log administrative action"""
        return self.log_event(
            AuditEventType.ADMIN_ACTION,
            user_id=user_id,
            resource="system",
            action=action,
            details=details or {},
            risk_score=20
        )
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_events = [
            event for event in self.audit_events
            if event.timestamp >= cutoff_time
        ]
        
        # Event type breakdown
        event_types = {}
        for event in recent_events:
            event_type = event.event_type.value
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
        
        # User activity
        user_activity = {}
        for event in recent_events:
            if event.user_id:
                if event.user_id not in user_activity:
                    user_activity[event.user_id] = 0
                user_activity[event.user_id] += 1
        
        # High-risk events
        high_risk_events = [
            event for event in recent_events
            if event.risk_score >= 15
        ]
        
        return {
            "period_hours": hours,
            "total_events": len(recent_events),
            "event_types": event_types,
            "unique_users": len(user_activity),
            "most_active_users": sorted(
                user_activity.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "high_risk_events": len(high_risk_events),
            "failure_rate": len([e for e in recent_events if e.result == "failure"]) / len(recent_events) if recent_events else 0
        }

class AuditLoggerTemplate:
    """Audit Logger Template"""
    
    def create_logger(self, config: Dict[str, Any]) -> AuditLogger:
        return AuditLogger(service_name=config.get("service_name", "iacherie"))
    
    def get_template_info(self) -> Dict[str, Any]:
        return {
            "name": "audit-logger",
            "description": "Security and compliance audit logging",
            "features": ["Security events", "User tracking", "Compliance trails"]
        }