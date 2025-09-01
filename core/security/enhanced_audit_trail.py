"""Enhanced Audit Trail System
============================

Complete audit trail implementation for user actions, admin operations,
data access, and security events with real-time monitoring and compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

from config.security.production_security import AuditTrailConfig, get_security_config


logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    PASSWORD_CHANGE = "auth.password.change"
    MFA_ENABLE = "auth.mfa.enable"
    MFA_DISABLE = "auth.mfa.disable"
    
    # Admin actions
    USER_CREATE = "admin.user.create"
    USER_DELETE = "admin.user.delete"
    USER_ROLE_CHANGE = "admin.user.role.change"
    SYSTEM_CONFIG_CHANGE = "admin.config.change"
    SECURITY_SETTING_CHANGE = "admin.security.change"
    
    # Data access
    DATA_VIEW = "data.view"
    DATA_EXPORT = "data.export"
    DATA_DELETE = "data.delete"
    DATA_MODIFY = "data.modify"
    
    # API operations
    API_CALL = "api.call"
    API_KEY_CREATE = "api.key.create"
    API_KEY_REVOKE = "api.key.revoke"
    
    # Security events
    SECURITY_VIOLATION = "security.violation"
    INTRUSION_ATTEMPT = "security.intrusion"
    SUSPICIOUS_ACTIVITY = "security.suspicious"
    
    # Business operations
    CONTENT_UPLOAD = "business.content.upload"
    CONTENT_DELETE = "business.content.delete"
    PAYMENT_PROCESS = "business.payment.process"
    REVENUE_GENERATE = "business.revenue.generate"


class AuditEventSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Individual audit event"""
    event_id: str
    event_type: AuditEventType
    severity: AuditEventSeverity
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    outcome: str = "unknown"  # success, failure, unknown
    risk_score: int = 0  # 0-100
    
    # Compliance and legal
    data_classification: Optional[str] = None
    retention_period: Optional[int] = None  # Days
    legal_hold: bool = False
    
    # Integrity and verification
    event_hash: Optional[str] = None
    previous_event_hash: Optional[str] = None
    
    def __post_init__(self):
        """Generate event hash for integrity"""
        if not self.event_hash:
            self.event_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate hash for event integrity"""
        # Create deterministic hash of core event data
        hash_data = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "outcome": self.outcome
        }
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class AuditQuery:
    """Audit query parameters"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    user_id: Optional[str] = None
    event_types: Optional[List[AuditEventType]] = None
    severity_min: Optional[AuditEventSeverity] = None
    resource: Optional[str] = None
    outcome: Optional[str] = None
    limit: int = 100
    offset: int = 0


class EnhancedAuditTrail:
    """Enhanced audit trail system"""
    
    def __init__(self, config: Optional[AuditTrailConfig] = None):
        self.config = config or get_security_config().audit_trail
        self.events: List[AuditEvent] = []  # In-memory storage (use DB in production)
        self.previous_event_hash: Optional[str] = None
        self.suspicious_patterns: Dict[str, Any] = {}
        
    def _calculate_risk_score(self, event: AuditEvent) -> int:
        """Calculate risk score for event"""
        base_scores = {
            AuditEventType.LOGIN_FAILURE: 30,
            AuditEventType.PASSWORD_CHANGE: 20,
            AuditEventType.USER_DELETE: 80,
            AuditEventType.SECURITY_SETTING_CHANGE: 70,
            AuditEventType.DATA_EXPORT: 40,
            AuditEventType.DATA_DELETE: 60,
            AuditEventType.INTRUSION_ATTEMPT: 90,
            AuditEventType.SUSPICIOUS_ACTIVITY: 50
        }
        
        base_score = base_scores.get(event.event_type, 10)
        
        # Adjust based on user patterns
        if event.user_id:
            user_events = [e for e in self.events[-100:] if e.user_id == event.user_id]
            if len(user_events) > 50:  # High activity
                base_score += 10
        
        # Adjust based on IP address
        if event.ip_address:
            ip_events = [e for e in self.events[-50:] if e.ip_address == event.ip_address]
            failed_logins = [e for e in ip_events if e.event_type == AuditEventType.LOGIN_FAILURE]
            if len(failed_logins) > 5:
                base_score += 30
        
        return min(base_score, 100)
    
    def _determine_severity(self, event_type: AuditEventType, risk_score: int) -> AuditEventSeverity:
        """Determine event severity"""
        critical_events = {
            AuditEventType.USER_DELETE,
            AuditEventType.SECURITY_SETTING_CHANGE,
            AuditEventType.INTRUSION_ATTEMPT
        }
        
        if event_type in critical_events or risk_score >= 80:
            return AuditEventSeverity.CRITICAL
        elif risk_score >= 60:
            return AuditEventSeverity.HIGH
        elif risk_score >= 30:
            return AuditEventSeverity.MEDIUM
        else:
            return AuditEventSeverity.LOW
    
    def _determine_retention_period(self, event_type: AuditEventType) -> int:
        """Determine retention period based on event type and compliance"""
        base_retention = self.config.retention_years * 365
        
        # Extended retention for critical events
        critical_events = {
            AuditEventType.USER_DELETE,
            AuditEventType.SECURITY_SETTING_CHANGE,
            AuditEventType.DATA_DELETE,
            AuditEventType.INTRUSION_ATTEMPT
        }
        
        if event_type in critical_events:
            return base_retention + (2 * 365)  # Extra 2 years
        
        return base_retention
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        action: str = "",
        details: Optional[Dict[str, Any]] = None,
        outcome: str = "success"
    ) -> AuditEvent:
        """Log an audit event"""
        
        # Generate unique event ID
        event_id = str(uuid.uuid4())
        
        # Create event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=AuditEventSeverity.LOW,  # Will be recalculated
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            details=details or {},
            outcome=outcome,
            previous_event_hash=self.previous_event_hash
        )
        
        # Calculate risk score and severity
        event.risk_score = self._calculate_risk_score(event)
        event.severity = self._determine_severity(event_type, event.risk_score)
        
        # Set retention period
        event.retention_period = self._determine_retention_period(event_type)
        
        # Update hash chain
        event.event_hash = event._calculate_hash()
        self.previous_event_hash = event.event_hash
        
        # Store event
        self.events.append(event)
        
        # Real-time monitoring
        if self.config.real_time_monitoring:
            await self._real_time_analysis(event)
        
        # Log to system logger
        logger.info(
            f"AUDIT [{event.severity.value.upper()}]: {event.event_type.value} - "
            f"User: {user_id}, Action: {action}, Outcome: {outcome}"
        )
        
        return event
    
    async def _real_time_analysis(self, event: AuditEvent):
        """Perform real-time analysis of audit event"""
        
        # Check for suspicious patterns
        if self.config.suspicious_pattern_detection:
            await self._detect_suspicious_patterns(event)
        
        # Alert on high-severity events
        if event.severity in [AuditEventSeverity.HIGH, AuditEventSeverity.CRITICAL]:
            await self._send_security_alert(event)
    
    async def _detect_suspicious_patterns(self, event: AuditEvent):
        """Detect suspicious activity patterns"""
        current_time = datetime.utcnow()
        
        # Pattern 1: Multiple failed logins
        if event.event_type == AuditEventType.LOGIN_FAILURE and event.ip_address:
            recent_failures = [
                e for e in self.events[-50:]
                if e.event_type == AuditEventType.LOGIN_FAILURE
                and e.ip_address == event.ip_address
                and (current_time - e.timestamp) < timedelta(minutes=15)
            ]
            
            if len(recent_failures) >= 5:
                await self.log_event(
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    ip_address=event.ip_address,
                    action="Multiple failed login attempts detected",
                    details={"failed_attempts": len(recent_failures), "timeframe": "15_minutes"}
                )
        
        # Pattern 2: Unusual data access
        if event.event_type == AuditEventType.DATA_VIEW and event.user_id:
            recent_views = [
                e for e in self.events[-100:]
                if e.event_type == AuditEventType.DATA_VIEW
                and e.user_id == event.user_id
                and (current_time - e.timestamp) < timedelta(hours=1)
            ]
            
            if len(recent_views) >= 50:  # Unusual high volume
                await self.log_event(
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    user_id=event.user_id,
                    action="Unusual high-volume data access detected",
                    details={"access_count": len(recent_views), "timeframe": "1_hour"}
                )
        
        # Pattern 3: Off-hours admin activity
        if (event.event_type.value.startswith("admin.") and 
            event.timestamp.hour < 6 or event.timestamp.hour > 22):
            await self.log_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                user_id=event.user_id,
                action="Off-hours administrative activity detected",
                details={"original_event": event.event_type.value, "hour": event.timestamp.hour}
            )
    
    async def _send_security_alert(self, event: AuditEvent):
        """Send security alert for high-severity events"""
        alert_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "action": event.action,
            "timestamp": event.timestamp.isoformat(),
            "risk_score": event.risk_score
        }
        
        # Log alert
        logger.warning(f"SECURITY ALERT: {event.event_type.value} - Risk Score: {event.risk_score}")
        
        # Send to monitoring systems (placeholder)
        # In production, integrate with SIEM, Slack, email, etc.
    
    async def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """Query audit events"""
        filtered_events = self.events
        
        # Apply filters
        if query.start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= query.start_time]
        
        if query.end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= query.end_time]
        
        if query.user_id:
            filtered_events = [e for e in filtered_events if e.user_id == query.user_id]
        
        if query.event_types:
            filtered_events = [e for e in filtered_events if e.event_type in query.event_types]
        
        if query.severity_min:
            severity_order = [AuditEventSeverity.LOW, AuditEventSeverity.MEDIUM, 
                            AuditEventSeverity.HIGH, AuditEventSeverity.CRITICAL]
            min_index = severity_order.index(query.severity_min)
            filtered_events = [
                e for e in filtered_events 
                if severity_order.index(e.severity) >= min_index
            ]
        
        if query.resource:
            filtered_events = [e for e in filtered_events if e.resource == query.resource]
        
        if query.outcome:
            filtered_events = [e for e in filtered_events if e.outcome == query.outcome]
        
        # Apply pagination
        start_index = query.offset
        end_index = start_index + query.limit
        
        return filtered_events[start_index:end_index]
    
    async def get_user_audit_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get audit summary for specific user"""
        start_time = datetime.utcnow() - timedelta(days=days)
        
        user_events = [
            e for e in self.events 
            if e.user_id == user_id and e.timestamp >= start_time
        ]
        
        # Count by event type
        event_counts = {}
        for event in user_events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Count by outcome
        outcome_counts = {}
        for event in user_events:
            outcome = event.outcome
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
        
        # Risk analysis
        risk_scores = [e.risk_score for e in user_events]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_events": len(user_events),
            "event_counts": event_counts,
            "outcome_counts": outcome_counts,
            "average_risk_score": round(avg_risk_score, 2),
            "high_risk_events": len([e for e in user_events if e.risk_score >= 70]),
            "last_activity": user_events[-1].timestamp.isoformat() if user_events else None
        }
    
    async def get_security_incidents(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get security incidents from audit log"""
        start_time = datetime.utcnow() - timedelta(days=days)
        
        security_events = [
            e for e in self.events
            if e.timestamp >= start_time and (
                e.event_type in [
                    AuditEventType.INTRUSION_ATTEMPT,
                    AuditEventType.SUSPICIOUS_ACTIVITY,
                    AuditEventType.SECURITY_VIOLATION
                ] or e.severity == AuditEventSeverity.CRITICAL
            )
        ]
        
        incidents = []
        for event in security_events:
            incidents.append({
                "incident_id": event.event_id,
                "type": event.event_type.value,
                "severity": event.severity.value,
                "timestamp": event.timestamp.isoformat(),
                "user_id": event.user_id,
                "ip_address": event.ip_address,
                "description": event.action,
                "risk_score": event.risk_score,
                "details": event.details
            })
        
        return sorted(incidents, key=lambda x: x["timestamp"], reverse=True)
    
    async def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify audit log integrity using hash chain"""
        total_events = len(self.events)
        verified_events = 0
        broken_chains = []
        
        previous_hash = None
        for i, event in enumerate(self.events):
            # Verify event hash
            expected_hash = event._calculate_hash()
            if event.event_hash != expected_hash:
                broken_chains.append({
                    "event_id": event.event_id,
                    "position": i,
                    "issue": "Hash mismatch"
                })
                continue
            
            # Verify chain
            if i > 0 and event.previous_event_hash != previous_hash:
                broken_chains.append({
                    "event_id": event.event_id,
                    "position": i,
                    "issue": "Chain break"
                })
                continue
            
            verified_events += 1
            previous_hash = event.event_hash
        
        integrity_score = (verified_events / total_events * 100) if total_events > 0 else 100
        
        return {
            "total_events": total_events,
            "verified_events": verified_events,
            "integrity_score": round(integrity_score, 2),
            "broken_chains": len(broken_chains),
            "issues": broken_chains[:10]  # First 10 issues
        }
    
    async def export_audit_log(
        self,
        query: AuditQuery,
        format: str = "json"
    ) -> Union[str, bytes]:
        """Export audit log data"""
        events = await self.query_events(query)
        
        if format == "json":
            return json.dumps([event.to_dict() for event in events], indent=2)
        elif format == "csv":
            # CSV export implementation
            import csv
            from io import StringIO
            
            output = StringIO()
            if events:
                fieldnames = list(events[0].to_dict().keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for event in events:
                    writer.writerow(event.to_dict())
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Global audit trail instance
_audit_trail_instance: Optional[EnhancedAuditTrail] = None

def get_audit_trail() -> EnhancedAuditTrail:
    """Get global audit trail instance"""
    global _audit_trail_instance
    if _audit_trail_instance is None:
        _audit_trail_instance = EnhancedAuditTrail()
    return _audit_trail_instance


async def log_audit_event(
    event_type: str,
    user_id: Optional[str] = None,
    action: str = "",
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Log audit event (main entry point)"""
    audit_trail = get_audit_trail()
    
    # Convert string to enum
    try:
        event_type_enum = AuditEventType(event_type)
    except ValueError:
        # Handle custom event types
        event_type_enum = AuditEventType.API_CALL
        kwargs["original_event_type"] = event_type
    
    event = await audit_trail.log_event(
        event_type=event_type_enum,
        user_id=user_id,
        action=action,
        details=details,
        **kwargs
    )
    
    return event.to_dict()


if __name__ == "__main__":
    async def main():
        # Test audit trail
        audit_trail = EnhancedAuditTrail()
        
        # Log some test events
        await audit_trail.log_event(
            AuditEventType.LOGIN_SUCCESS,
            user_id="user123",
            ip_address="192.168.1.100",
            action="User logged in successfully"
        )
        
        await audit_trail.log_event(
            AuditEventType.DATA_VIEW,
            user_id="user123",
            resource="customer_data",
            action="Viewed customer list"
        )
        
        # Query events
        query = AuditQuery(user_id="user123")
        events = await audit_trail.query_events(query)
        print(f"Found {len(events)} events for user123")
        
        # Get user summary
        summary = await audit_trail.get_user_audit_summary("user123")
        print(f"User summary: {summary}")
        
        # Verify integrity
        integrity = await audit_trail.verify_audit_integrity()
        print(f"Audit integrity: {integrity['integrity_score']}%")
    
    asyncio.run(main())