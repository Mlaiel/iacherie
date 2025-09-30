"""
Audit Trail Manager
Enterprise audit logging and trail management for ML systems

Features:
- Comprehensive audit logging
- Event correlation and analysis
- Compliance audit trails
- Real-time audit monitoring
- Audit data retention and archival
- Forensic analysis capabilities

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from datetime import datetime, timedelta
import uuid


class AuditEventType(Enum):
    """Types of audit events"""
    MODEL_ACCESS = "model_access"
    DATA_ACCESS = "data_access" 
    MODEL_UPDATE = "model_update"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    COMPLIANCE_CHECK = "compliance_check"
    USER_ACTION = "user_action"
    SYSTEM_ACTION = "system_action"
    DEPLOYMENT = "deployment"
    INFERENCE = "inference"


class AuditSeverity(Enum):
    """Audit event severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class AuditEvent:
    """Individual audit event"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: Optional[str]
    resource_id: str
    resource_type: str
    action: str
    outcome: str  # success, failure, partial
    details: Dict[str, Any]
    metadata: Dict[str, Any]
    checksum: str


@dataclass
class AuditQuery:
    """Audit trail query parameters"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    severity: Optional[AuditSeverity] = None
    outcome: Optional[str] = None
    limit: int = 1000


@dataclass
class AuditReport:
    """Audit report structure"""
    report_id: str
    generated_at: datetime
    query_params: AuditQuery
    total_events: int
    events: List[AuditEvent]
    summary: Dict[str, Any]
    anomalies: List[Dict[str, Any]]


class AuditTrailManager:
    """
    Enterprise Audit Trail Manager
    Comprehensive audit logging and management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_events: List[AuditEvent] = []
        self.audit_configs: Dict[str, Dict[str, Any]] = {}
        self.retention_policies: Dict[str, int] = {}  # days
        self.alert_rules: List[Dict[str, Any]] = []
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default audit configurations"""
        self.retention_policies = {
            "critical": 2555,     # 7 years
            "high": 1095,         # 3 years
            "medium": 365,        # 1 year
            "low": 90,            # 3 months
            "informational": 30   # 1 month
        }
        
        # Default alert rules
        self.alert_rules = [
            {
                "rule_id": "failed_access_attempts",
                "condition": "failed_logins >= 5 in 5 minutes",
                "severity": "high",
                "action": "alert_security_team"
            },
            {
                "rule_id": "suspicious_ip_access",
                "condition": "access from new IP with critical resource",
                "severity": "medium",
                "action": "log_and_monitor"
            }
        ]
    
    async def configure_audit_trail(
        self,
        resource_id: str,
        config: Dict[str, Any]
    ) -> bool:
        """Configure audit trail for a resource"""
        try:
            default_config = {
                "enabled": True,
                "event_types": [e.value for e in AuditEventType],
                "minimum_severity": AuditSeverity.INFORMATIONAL.value,
                "real_time_alerts": True,
                "data_integrity_checks": True,
                "retention_days": 365
            }
            
            # Merge with provided config
            final_config = {**default_config, **config}
            self.audit_configs[resource_id] = final_config
            
            self.logger.info(f"Audit trail configured for resource {resource_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure audit trail for {resource_id}: {str(e)}")
            return False
    
    async def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        resource_id: str,
        resource_type: str,
        action: str,
        outcome: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an audit event"""
        try:
            # Check if auditing is enabled for this resource
            config = self.audit_configs.get(resource_id, {})
            if not config.get("enabled", True):
                return ""
            
            # Check if event type is configured to be logged
            if event_type.value not in config.get("event_types", []):
                return ""
            
            # Check minimum severity
            min_severity = config.get("minimum_severity", "informational")
            severity_levels = {
                "informational": 0,
                "low": 1,
                "medium": 2, 
                "high": 3,
                "critical": 4
            }
            
            if severity_levels.get(severity.value, 0) < severity_levels.get(min_severity, 0):
                return ""
            
            # Create audit event
            event_id = str(uuid.uuid4())
            timestamp = datetime.now()
            
            event_details = details or {}
            event_metadata = metadata or {}
            
            # Add system metadata
            event_metadata.update({
                "logged_at": timestamp.isoformat(),
                "audit_version": "1.0",
                "system_id": "ainflue_mlops"
            })
            
            # Calculate checksum for integrity
            checksum_data = f"{event_id}{timestamp.isoformat()}{event_type.value}{resource_id}{action}{outcome}"
            checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
            
            audit_event = AuditEvent(
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                session_id=session_id,
                source_ip=source_ip,
                resource_id=resource_id,
                resource_type=resource_type,
                action=action,
                outcome=outcome,
                details=event_details,
                metadata=event_metadata,
                checksum=checksum
            )
            
            # Store the event
            self.audit_events.append(audit_event)
            
            # Check for real-time alerts
            if config.get("real_time_alerts", False):
                await self._check_alert_rules(audit_event)
            
            # Verify data integrity if enabled
            if config.get("data_integrity_checks", False):
                await self._verify_event_integrity(audit_event)
            
            # Clean up old events based on retention policy
            await self._cleanup_old_events()
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {str(e)}")
            return ""
    
    async def query_audit_trail(
        self,
        query: AuditQuery
    ) -> List[AuditEvent]:
        """Query audit trail with specified criteria"""
        try:
            filtered_events = self.audit_events.copy()
            
            # Apply time filters
            if query.start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= query.start_time]
            if query.end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= query.end_time]
            
            # Apply event type filter
            if query.event_types:
                filtered_events = [e for e in filtered_events if e.event_type in query.event_types]
            
            # Apply user filter
            if query.user_id:
                filtered_events = [e for e in filtered_events if e.user_id == query.user_id]
            
            # Apply resource filter
            if query.resource_id:
                filtered_events = [e for e in filtered_events if e.resource_id == query.resource_id]
            
            # Apply severity filter
            if query.severity:
                filtered_events = [e for e in filtered_events if e.severity == query.severity]
            
            # Apply outcome filter
            if query.outcome:
                filtered_events = [e for e in filtered_events if e.outcome == query.outcome]
            
            # Apply limit
            if query.limit:
                filtered_events = filtered_events[:query.limit]
            
            return filtered_events
            
        except Exception as e:
            self.logger.error(f"Audit trail query failed: {str(e)}")
            return []
    
    async def generate_audit_report(
        self,
        query: AuditQuery,
        include_analysis: bool = True
    ) -> AuditReport:
        """Generate comprehensive audit report"""
        try:
            report_id = str(uuid.uuid4())
            events = await self.query_audit_trail(query)
            
            # Generate summary
            summary = self._generate_report_summary(events)
            
            # Detect anomalies if analysis is requested
            anomalies = []
            if include_analysis:
                anomalies = await self._detect_anomalies(events)
            
            report = AuditReport(
                report_id=report_id,
                generated_at=datetime.now(),
                query_params=query,
                total_events=len(events),
                events=events,
                summary=summary,
                anomalies=anomalies
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Audit report generation failed: {str(e)}")
            raise
    
    async def verify_audit_integrity(
        self,
        event_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Verify audit trail integrity"""
        try:
            # Select events to verify
            events_to_verify = self.audit_events
            if event_ids:
                events_to_verify = [e for e in self.audit_events if e.event_id in event_ids]
            
            verification_result = {
                "total_events_checked": len(events_to_verify),
                "integrity_violations": [],
                "verification_timestamp": datetime.now().isoformat(),
                "overall_integrity": True
            }
            
            for event in events_to_verify:
                # Recalculate checksum
                checksum_data = f"{event.event_id}{event.timestamp.isoformat()}{event.event_type.value}{event.resource_id}{event.action}{event.outcome}"
                expected_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
                
                if event.checksum != expected_checksum:
                    verification_result["integrity_violations"].append({
                        "event_id": event.event_id,
                        "issue": "checksum_mismatch",
                        "expected_checksum": expected_checksum,
                        "actual_checksum": event.checksum
                    })
                    verification_result["overall_integrity"] = False
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Audit integrity verification failed: {str(e)}")
            raise
    
    async def export_audit_data(
        self,
        query: AuditQuery,
        format: str = "json"
    ) -> str:
        """Export audit data in specified format"""
        try:
            events = await self.query_audit_trail(query)
            
            if format.lower() == "json":
                return json.dumps([asdict(event) for event in events], default=str, indent=2)
            elif format.lower() == "csv":
                return self._export_to_csv(events)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            self.logger.error(f"Audit data export failed: {str(e)}")
            raise
    
    async def get_audit_statistics(
        self,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get audit trail statistics"""
        try:
            end_time = datetime.now()
            start_time = end_time - time_period
            
            query = AuditQuery(start_time=start_time, end_time=end_time)
            events = await self.query_audit_trail(query)
            
            stats = {
                "time_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "total_events": len(events),
                "events_by_type": {},
                "events_by_severity": {},
                "events_by_outcome": {},
                "unique_users": len(set(e.user_id for e in events if e.user_id)),
                "unique_resources": len(set(e.resource_id for e in events)),
                "top_users": self._get_top_users(events),
                "top_resources": self._get_top_resources(events),
                "failure_rate": self._calculate_failure_rate(events)
            }
            
            # Events by type
            for event in events:
                event_type = event.event_type.value
                stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
            
            # Events by severity
            for event in events:
                severity = event.severity.value
                stats["events_by_severity"][severity] = stats["events_by_severity"].get(severity, 0) + 1
            
            # Events by outcome
            for event in events:
                outcome = event.outcome
                stats["events_by_outcome"][outcome] = stats["events_by_outcome"].get(outcome, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get audit statistics: {str(e)}")
            raise
    
    # Private methods
    
    def _generate_report_summary(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate summary for audit report"""
        if not events:
            return {"total_events": 0}
        
        summary = {
            "total_events": len(events),
            "time_range": {
                "start": min(e.timestamp for e in events).isoformat(),
                "end": max(e.timestamp for e in events).isoformat()
            },
            "event_types": {},
            "severity_distribution": {},
            "outcome_distribution": {},
            "unique_users": len(set(e.user_id for e in events if e.user_id)),
            "unique_resources": len(set(e.resource_id for e in events))
        }
        
        for event in events:
            # Count event types
            event_type = event.event_type.value
            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
            
            # Count severity levels
            severity = event.severity.value
            summary["severity_distribution"][severity] = summary["severity_distribution"].get(severity, 0) + 1
            
            # Count outcomes
            outcome = event.outcome
            summary["outcome_distribution"][outcome] = summary["outcome_distribution"].get(outcome, 0) + 1
        
        return summary
    
    async def _detect_anomalies(self, events: List[AuditEvent]) -> List[Dict[str, Any]]:
        """Detect anomalies in audit events"""
        anomalies = []
        
        try:
            # Detect unusual access patterns
            user_access_counts = {}
            for event in events:
                if event.user_id and event.event_type == AuditEventType.MODEL_ACCESS:
                    user_access_counts[event.user_id] = user_access_counts.get(event.user_id, 0) + 1
            
            # Find users with unusually high access
            if user_access_counts:
                avg_access = sum(user_access_counts.values()) / len(user_access_counts)
                threshold = avg_access * 3  # 3x average
                
                for user_id, count in user_access_counts.items():
                    if count > threshold:
                        anomalies.append({
                            "type": "unusual_access_pattern",
                            "description": f"User {user_id} has {count} accesses (avg: {avg_access:.1f})",
                            "severity": "medium",
                            "user_id": user_id,
                            "access_count": count
                        })
            
            # Detect failed login attempts
            failed_logins = [e for e in events if e.action == "login" and e.outcome == "failure"]
            failed_by_user = {}
            for event in failed_logins:
                if event.user_id:
                    failed_by_user[event.user_id] = failed_by_user.get(event.user_id, 0) + 1
            
            for user_id, count in failed_by_user.items():
                if count > 5:  # More than 5 failed attempts
                    anomalies.append({
                        "type": "multiple_failed_logins",
                        "description": f"User {user_id} has {count} failed login attempts",
                        "severity": "high",
                        "user_id": user_id,
                        "failed_attempts": count
                    })
            
            # Detect off-hours access
            for event in events:
                if event.timestamp.hour < 6 or event.timestamp.hour > 22:  # Outside business hours
                    if event.event_type in [AuditEventType.MODEL_ACCESS, AuditEventType.DATA_ACCESS]:
                        anomalies.append({
                            "type": "off_hours_access",
                            "description": f"Access to {event.resource_id} at {event.timestamp.strftime('%H:%M')}",
                            "severity": "low",
                            "event_id": event.event_id,
                            "timestamp": event.timestamp.isoformat()
                        })
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
        
        return anomalies
    
    async def _check_alert_rules(self, event: AuditEvent):
        """Check if event triggers any alert rules"""
        try:
            for rule in self.alert_rules:
                if await self._evaluate_alert_rule(rule, event):
                    await self._trigger_alert(rule, event)
                    
        except Exception as e:
            self.logger.error(f"Alert rule checking failed: {str(e)}")
    
    async def _evaluate_alert_rule(self, rule: Dict[str, Any], event: AuditEvent) -> bool:
        """Evaluate if an alert rule is triggered"""
        # Simplified rule evaluation - in production would use a proper rule engine
        rule_id = rule["rule_id"]
        
        if rule_id == "failed_access_attempts":
            # Check for failed logins in last 5 minutes
            if event.action == "login" and event.outcome == "failure":
                recent_time = datetime.now() - timedelta(minutes=5)
                recent_failures = [
                    e for e in self.audit_events
                    if (e.timestamp >= recent_time and 
                        e.action == "login" and 
                        e.outcome == "failure" and
                        e.user_id == event.user_id)
                ]
                return len(recent_failures) >= 5
        
        elif rule_id == "suspicious_ip_access":
            # Check for access from new IP to critical resource
            if event.severity == AuditSeverity.CRITICAL and event.source_ip:
                previous_ips = set(
                    e.source_ip for e in self.audit_events
                    if e.user_id == event.user_id and e.source_ip
                )
                return event.source_ip not in previous_ips
        
        return False
    
    async def _trigger_alert(self, rule: Dict[str, Any], event: AuditEvent):
        """Trigger alert based on rule"""
        alert_data = {
            "alert_id": str(uuid.uuid4()),
            "rule_id": rule["rule_id"],
            "triggered_at": datetime.now().isoformat(),
            "event_id": event.event_id,
            "severity": rule["severity"],
            "action": rule["action"],
            "description": f"Alert rule {rule['rule_id']} triggered by event {event.event_id}"
        }
        
        # Log the alert as an audit event
        await self.log_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            severity=AuditSeverity(rule["severity"]),
            resource_id="audit_system",
            resource_type="security",
            action="alert_triggered",
            outcome="success",
            details=alert_data
        )
        
        self.logger.warning(f"Security alert triggered: {alert_data}")
    
    async def _verify_event_integrity(self, event: AuditEvent) -> bool:
        """Verify integrity of a single event"""
        checksum_data = f"{event.event_id}{event.timestamp.isoformat()}{event.event_type.value}{event.resource_id}{event.action}{event.outcome}"
        expected_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()
        return event.checksum == expected_checksum
    
    async def _cleanup_old_events(self):
        """Clean up events based on retention policies"""
        try:
            current_time = datetime.now()
            events_to_keep = []
            
            for event in self.audit_events:
                retention_days = self.retention_policies.get(event.severity.value, 365)
                retention_cutoff = current_time - timedelta(days=retention_days)
                
                if event.timestamp >= retention_cutoff:
                    events_to_keep.append(event)
            
            # Update the events list
            removed_count = len(self.audit_events) - len(events_to_keep)
            self.audit_events = events_to_keep
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old audit events")
                
        except Exception as e:
            self.logger.error(f"Audit cleanup failed: {str(e)}")
    
    def _export_to_csv(self, events: List[AuditEvent]) -> str:
        """Export events to CSV format"""
        if not events:
            return "No events to export"
        
        csv_lines = []
        
        # Header
        header = [
            "event_id", "timestamp", "event_type", "severity", "user_id",
            "session_id", "source_ip", "resource_id", "resource_type",
            "action", "outcome", "details", "checksum"
        ]
        csv_lines.append(",".join(header))
        
        # Data rows
        for event in events:
            row = [
                event.event_id,
                event.timestamp.isoformat(),
                event.event_type.value,
                event.severity.value,
                event.user_id or "",
                event.session_id or "",
                event.source_ip or "",
                event.resource_id,
                event.resource_type,
                event.action,
                event.outcome,
                json.dumps(event.details).replace('"', '""'),  # Escape quotes
                event.checksum
            ]
            csv_lines.append(",".join(f'"{field}"' for field in row))
        
        return "\n".join(csv_lines)
    
    def _get_top_users(self, events: List[AuditEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by activity"""
        user_counts = {}
        for event in events:
            if event.user_id:
                user_counts[event.user_id] = user_counts.get(event.user_id, 0) + 1
        
        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"user_id": user_id, "event_count": count} for user_id, count in sorted_users[:limit]]
    
    def _get_top_resources(self, events: List[AuditEvent], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top resources by access"""
        resource_counts = {}
        for event in events:
            resource_counts[event.resource_id] = resource_counts.get(event.resource_id, 0) + 1
        
        sorted_resources = sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"resource_id": resource_id, "access_count": count} for resource_id, count in sorted_resources[:limit]]
    
    def _calculate_failure_rate(self, events: List[AuditEvent]) -> float:
        """Calculate failure rate from events"""
        if not events:
            return 0.0
        
        failed_events = [e for e in events if e.outcome == "failure"]
        return len(failed_events) / len(events) * 100


# Global instance
audit_trail_manager = AuditTrailManager()