"""🔍 Advanced Audit Trail System - Ultra-Professional DRM Compliance Logging
========================================================================

Comprehensive audit logging and compliance tracking system for digital rights
management with advanced forensics and regulatory compliance features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing and usage rights.

🎯 PROJECT TEAM SPECIALTIES:
- Lead AI Developer & Solution Architect: Advanced AI/ML systems and intelligent automation
- Backend Senior Engineer: Enterprise-grade backend architecture and microservices  
- ML Engineer: Machine learning models and predictive analytics
- Database Administrator: High-performance data management and optimization
- Security Engineer: Advanced cybersecurity and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Professional audio processing and analysis
- DevOps Engineer: Advanced deployment and infrastructure automation
- IA Prompt Engineer: Advanced AI prompt engineering and optimization
"""

import asyncio
import logging
import json
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from cryptography.fernet import Fernet
import gzip
import base64

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """
Types of auditable events."""

    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    LICENSE_ISSUED = "license_issued"
    LICENSE_VALIDATED = "license_validated"
    LICENSE_EXPIRED = "license_expired"
    LICENSE_REVOKED = "license_revoked"
    CONTENT_ENCRYPTED = "content_encrypted"
    CONTENT_DECRYPTED = "content_decrypted"
    POLICY_CREATED = "policy_created"
    POLICY_UPDATED = "policy_updated"
    POLICY_DELETED = "policy_deleted"
    VIOLATION_DETECTED = "violation_detected"
    REVENUE_CALCULATED = "revenue_calculated"
    PAYMENT_PROCESSED = "payment_processed"
    USER_AUTHENTICATED = "user_authenticated"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    CONTENT_UPLOADED = "content_uploaded"
    CONTENT_DOWNLOADED = "content_downloaded"
    WATERMARK_APPLIED = "watermark_applied"
    FINGERPRINT_GENERATED = "fingerprint_generated"
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"

class EventSeverity(str, Enum):
    """Event severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class EventCategory(str, Enum):
    """Event categories for compliance."""

    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS = "business"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"
    OPERATIONAL = "operational"

class ComplianceStandard(str, Enum):
    """Compliance standards."""

    GDPR = "gdpr"
    CCPA = "ccpa"
    DMCA = "dmca"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"

@dataclass
class AuditEvent:
    """Comprehensive audit event record."""
    event_id: str
    event_type: EventType
    severity: EventSeverity
    category: EventCategory
    timestamp: datetime
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    license_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source_system: str = "drm_system"
    event_data: Dict[str, Any] = field(default_factory=dict)
    compliance_tags: Set[ComplianceStandard] = field(default_factory=set)
    retention_until: Optional[datetime] = None
    encrypted: bool = False
    checksum: Optional[str] = None
    signature: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceReport:
    """Compliance report for regulatory requirements."""
    report_id: str
    standard: ComplianceStandard
    report_type: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    events_included: int
    summary: Dict[str, Any]
    details: List[Dict[str, Any]]
    recommendations: List[str]
    compliance_status: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class AuditTrail:
    """
Advanced audit trail and compliance logging system."""
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize audit trail system."""
        self.config = config
        self.events: List[AuditEvent] = []
        self.retention_policy = config.get("retention_policy", {})
        self.encryption_enabled = config.get("encryption_enabled", True)
        self.signing_enabled = config.get("signing_enabled", True)
        self.compression_enabled = config.get("compression_enabled", True)
        self.max_events_in_memory = config.get("max_events_in_memory", 10000)
        
        # Initialize encryption
        if self.encryption_enabled:
            self.encryption_key = self._generate_encryption_key()
            self.cipher = Fernet(self.encryption_key)
        
        # Initialize event processors
        self.event_processors = {}
        self.compliance_rules = {}
        
    async def initialize(self) -> bool:
        """Initialize audit trail system."""
        try:
            # Load compliance rules
            await self._load_compliance_rules()
            
            # Initialize event processors
            await self._initialize_event_processors()
            
            # Start cleanup task
            asyncio.create_task(self._periodic_cleanup())
            
            logger.info("Audit trail system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize audit trail system: {e}")
            return False
    
    async def _load_compliance_rules(self) -> None:
        """Load compliance rules for different standards."""
        # GDPR compliance rules
        self.compliance_rules[ComplianceStandard.GDPR] = {
            "retention_period": timedelta(days=2555),  # 7 years
            "required_events": {
                EventType.USER_AUTHENTICATED,
                EventType.ACCESS_GRANTED,
                EventType.ACCESS_DENIED,
                EventType.CONTENT_DOWNLOADED
            },
            "data_fields": ["user_id", "timestamp", "ip_address", "event_data"]
        }
        
        # DMCA compliance rules
        self.compliance_rules[ComplianceStandard.DMCA] = {
            "retention_period": timedelta(days=1095),  # 3 years
            "required_events": {
                EventType.VIOLATION_DETECTED,
                EventType.CONTENT_UPLOADED,
                EventType.LICENSE_ISSUED
            },
            "data_fields": ["content_id", "license_id", "timestamp", "event_data"]
        }
        
        # SOX compliance rules
        self.compliance_rules[ComplianceStandard.SOX] = {
            "retention_period": timedelta(days=2555),  # 7 years
            "required_events": {
                EventType.REVENUE_CALCULATED,
                EventType.PAYMENT_PROCESSED,
                EventType.LICENSE_ISSUED
            },
            "data_fields": ["user_id", "content_id", "timestamp", "event_data"]
        }
    
    async def _initialize_event_processors(self) -> None:
        """Initialize event processors for different event types."""
        self.event_processors = {
            EventType.SECURITY_ALERT: self._process_security_alert,
            EventType.VIOLATION_DETECTED: self._process_violation,
            EventType.SYSTEM_ERROR: self._process_system_error,
            EventType.ACCESS_DENIED: self._process_access_denied
        }
    
    async def log_event(
        self,
        event_type: EventType,
        severity: EventSeverity = EventSeverity.MEDIUM,
        category: EventCategory = EventCategory.OPERATIONAL,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        license_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        compliance_tags: Optional[Set[ComplianceStandard]] = None
    ) -> str:
        """
Log an audit event."""
        try:
            # Generate event ID
            event_id = str(uuid.uuid4())
            
            # Create event
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                severity=severity,
                category=category,
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                content_id=content_id,
                license_id=license_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                event_data=event_data or {},
                compliance_tags=compliance_tags or set()
            )
            
            # Set retention period based on compliance requirements
            await self._set_retention_period(event)
            
            # Encrypt sensitive data if required
            if self.encryption_enabled and self._requires_encryption(event):
                await self._encrypt_event(event)
            
            # Calculate checksum
            event.checksum = self._calculate_checksum(event)
            
            # Add digital signature
            if self.signing_enabled:
                event.signature = await self._sign_event(event)
            
            # Store event
            await self._store_event(event)
            
            # Process event if required
            if event_type in self.event_processors:
                await self.event_processors[event_type](event)
            
            logger.debug(f"Audit event logged: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            raise
    
    async def _set_retention_period(self, event: AuditEvent) -> None:
        """Set retention period based on compliance requirements."""
        max_retention = None
        
        for standard in event.compliance_tags:
            if standard in self.compliance_rules:
                retention = self.compliance_rules[standard]["retention_period"]
                if max_retention is None or retention > max_retention:
                    max_retention = retention
        
        if max_retention:
            event.retention_until = event.timestamp + max_retention
        else:
            # Default retention period
            default_retention = timedelta(days=self.retention_policy.get("default_days", 365))
            event.retention_until = event.timestamp + default_retention
    
    def _requires_encryption(self, event: AuditEvent) -> bool:
        """Determine if event requires encryption."""
        sensitive_events = {
            EventType.USER_AUTHENTICATED,
            EventType.PAYMENT_PROCESSED,
            EventType.SECURITY_ALERT,
            EventType.VIOLATION_DETECTED
        }
        
        return event.event_type in sensitive_events or event.severity in {
            EventSeverity.HIGH, EventSeverity.CRITICAL, EventSeverity.EMERGENCY
        }
    
    async def _encrypt_event(self, event: AuditEvent) -> None:
        """
Encrypt sensitive event data."""
        try:
            if self.encryption_enabled and hasattr(self, 'cipher'):
                # Encrypt event data
                if event.event_data:
                    serialized_data = json.dumps(event.event_data)
                    encrypted_data = self.cipher.encrypt(serialized_data.encode())
                    event.event_data = {"encrypted": base64.b64encode(encrypted_data).decode()}
                    event.encrypted = True
                
        except Exception as e:
            logger.error(f"Error encrypting event data: {e}")
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate SHA-256 checksum for event integrity."""
        try:
            # Create deterministic representation
            event_dict = asdict(event)
            event_dict.pop('checksum', None)  # Remove checksum field
            event_dict.pop('signature', None)  # Remove signature field
            
            # Convert to JSON string with sorted keys
            event_json = json.dumps(event_dict, sort_keys=True, default=str)
            
            # Calculate checksum
            return hashlib.sha256(event_json.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""
    
    async def _sign_event(self, event: AuditEvent) -> str:
        """Create digital signature for event."""
        try:
            # For simplicity, using HMAC-like signature
            # In production, use proper digital signatures
            signing_key = self.config.get("signing_key", "default_signing_key")
            signature_data = f"{event.event_id}{event.timestamp.isoformat()}{event.checksum}"
            signature = hashlib.sha256(f"{signing_key}{signature_data}".encode()).hexdigest()
            return signature
            
        except Exception as e:
            logger.error(f"Error signing event: {e}")
            return ""
    
    async def _store_event(self, event: AuditEvent) -> None:
        """Store event in appropriate storage."""
        try:
            # Add to in-memory storage
            self.events.append(event)
            
            # Manage memory usage
            if len(self.events) > self.max_events_in_memory:
                # Archive oldest events
                await self._archive_events(self.events[:1000])
                self.events = self.events[1000:]
            
            # Persist to permanent storage
            await self._persist_event(event)
            
        except Exception as e:
            logger.error(f"Error storing event: {e}")
    
    async def _persist_event(self, event: AuditEvent) -> None:
        """Persist event to permanent storage."""
        try:
            # This would integrate with database or file storage
            # For now, log to file
            log_entry = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "timestamp": event.timestamp.isoformat(),
                "user_id": event.user_id,
                "content_id": event.content_id,
                "event_data": event.event_data,
                "checksum": event.checksum,
                "signature": event.signature
            }
            
            # Compress if enabled
            if self.compression_enabled:
                log_entry = self._compress_data(log_entry)
            
            logger.info(f"Audit event persisted: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Error persisting event: {e}")
    
    def _compress_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress event data."""
        try:
            json_data = json.dumps(data)
            compressed = gzip.compress(json_data.encode())
            encoded = base64.b64encode(compressed).decode()
            return {"compressed": True, "data": encoded}
            
        except Exception as e:
            logger.error(f"Error compressing data: {e}")
            return data
    
    async def _archive_events(self, events: List[AuditEvent]) -> None:
        """Archive events to long-term storage."""
        try:
            # This would integrate with archival storage
            logger.info(f"Archiving {len(events)} events")
            
        except Exception as e:
            logger.error(f"Error archiving events: {e}")
    
    async def _process_security_alert(self, event: AuditEvent) -> None:
        """Process security alert events."""
        try:
            # Send immediate notifications for critical security events
            if event.severity in {EventSeverity.CRITICAL, EventSeverity.EMERGENCY}:
                await self._send_security_notification(event)
            
            # Update security metrics
            await self._update_security_metrics(event)
            
        except Exception as e:
            logger.error(f"Error processing security alert: {e}")
    
    async def _process_violation(self, event: AuditEvent) -> None:
        """Process violation detection events."""
        try:
            # Log violation details
            violation_data = event.event_data.get("violation_details", {})
            logger.warning(f"Policy violation detected: {violation_data}")
            
            # Update violation statistics
            await self._update_violation_metrics(event)
            
        except Exception as e:
            logger.error(f"Error processing violation: {e}")
    
    async def _process_system_error(self, event: AuditEvent) -> None:
        """Process system error events."""
        try:
            # Alert on critical system errors
            if event.severity in {EventSeverity.HIGH, EventSeverity.CRITICAL}:
                await self._send_error_notification(event)
            
        except Exception as e:
            logger.error(f"Error processing system error: {e}")
    
    async def _process_access_denied(self, event: AuditEvent) -> None:
        """Process access denied events."""
        try:
            # Track failed access attempts
            user_id = event.user_id
            if user_id:
                await self._track_failed_access(user_id, event)
            
        except Exception as e:
            logger.error(f"Error processing access denied: {e}")
    
    async def search_events(
        self,
        event_types: Optional[List[EventType]] = None,
        severities: Optional[List[EventSeverity]] = None,
        categories: Optional[List[EventCategory]] = None,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Search audit events with filters."""
        try:
            filtered_events = self.events
            
            if event_types:
                filtered_events = [e for e in filtered_events if e.event_type in event_types]
            
            if severities:
                filtered_events = [e for e in filtered_events if e.severity in severities]
            
            if categories:
                filtered_events = [e for e in filtered_events if e.category in categories]
            
            if user_id:
                filtered_events = [e for e in filtered_events if e.user_id == user_id]
            
            if content_id:
                filtered_events = [e for e in filtered_events if e.content_id == content_id]
            
            if start_date:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
            
            if end_date:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
            
            # Sort by timestamp (newest first)
            filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return filtered_events[:limit]
            
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    async def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        start_date: datetime,
        end_date: datetime
    ) -> ComplianceReport:
        """Generate compliance report for specific standard."""
        try:
            report_id = str(uuid.uuid4())
            
            # Get compliance rules
            rules = self.compliance_rules.get(standard, {})
            required_events = rules.get("required_events", set())
            
            # Search relevant events
            events = await self.search_events(
                event_types=list(required_events),
                start_date=start_date,
                end_date=end_date
            )
            
            # Generate summary
            summary = await self._generate_compliance_summary(events, standard)
            
            # Generate details
            details = await self._generate_compliance_details(events, standard)
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(events, standard)
            
            # Determine compliance status
            compliance_status = await self._determine_compliance_status(events, standard)
            
            report = ComplianceReport(
                report_id=report_id,
                standard=standard,
                report_type="audit_compliance",
                period_start=start_date,
                period_end=end_date,
                generated_at=datetime.now(timezone.utc),
                events_included=len(events),
                summary=summary,
                details=details,
                recommendations=recommendations,
                compliance_status=compliance_status
            )
            
            logger.info(f"Compliance report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    async def _generate_compliance_summary(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard
    ) -> Dict[str, Any]:
        """Generate compliance summary."""
        summary = {
            "total_events": len(events),
            "events_by_type": {},
            "events_by_severity": {},
            "violations_detected": 0,
            "security_incidents": 0
        }
        
        for event in events:
            # Count by type
            event_type = event.event_type.value
            summary["events_by_type"][event_type] = summary["events_by_type"].get(event_type, 0) + 1
            
            # Count by severity
            severity = event.severity.value
            summary["events_by_severity"][severity] = summary["events_by_severity"].get(severity, 0) + 1
            
            # Count violations
            if event.event_type == EventType.VIOLATION_DETECTED:
                summary["violations_detected"] += 1
            
            # Count security incidents
            if event.category == EventCategory.SECURITY and event.severity in {
                EventSeverity.HIGH, EventSeverity.CRITICAL, EventSeverity.EMERGENCY
            }:
                summary["security_incidents"] += 1
        
        return summary
    
    async def _generate_compliance_details(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard
    ) -> List[Dict[str, Any]]:
        """Generate detailed compliance information."""
        details = []
        
        for event in events:
            detail = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "severity": event.severity.value,
                "user_id": event.user_id,
                "content_id": event.content_id,
                "compliance_relevant": standard in event.compliance_tags
            }
            details.append(detail)
        
        return details
    
    async def _generate_compliance_recommendations(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard
    ) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        # Analyze events for compliance gaps
        high_severity_events = [e for e in events if e.severity in {
            EventSeverity.HIGH, EventSeverity.CRITICAL, EventSeverity.EMERGENCY
        }]
        
        if len(high_severity_events) > 10:
            recommendations.append("Consider implementing additional security monitoring")
        
        violations = [e for e in events if e.event_type == EventType.VIOLATION_DETECTED]
        if len(violations) > 5:
            recommendations.append("Review and strengthen content protection policies")
        
        access_denied_events = [e for e in events if e.event_type == EventType.ACCESS_DENIED]
        if len(access_denied_events) > 20:
            recommendations.append("Analyze access patterns to improve user experience")
        
        return recommendations
    
    async def _determine_compliance_status(
        self,
        events: List[AuditEvent],
        standard: ComplianceStandard
    ) -> str:
        """Determine overall compliance status."""
        # Simple compliance scoring
        total_events = len(events)
        violation_events = len([e for e in events if e.event_type == EventType.VIOLATION_DETECTED])
        critical_events = len([e for e in events if e.severity == EventSeverity.CRITICAL])
        
        if critical_events > 0:
            return "NON_COMPLIANT"
        elif violation_events > total_events * 0.05:  # More than 5% violations
            return "PARTIALLY_COMPLIANT"
        else:
            return "COMPLIANT"
    
    async def _periodic_cleanup(self) -> None:
        """Periodically clean up expired events."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                current_time = datetime.now(timezone.utc)
                expired_events = [
                    e for e in self.events
                    if e.retention_until and e.retention_until < current_time
                ]
                
                if expired_events:
                    # Archive before deletion
                    await self._archive_events(expired_events)
                    
                    # Remove from memory
                    self.events = [
                        e for e in self.events
                        if not (e.retention_until and e.retention_until < current_time)
                    ]
                    
                    logger.info(f"Cleaned up {len(expired_events)} expired events")
                
            except Exception as e:
                logger.error(f"Error during periodic cleanup: {e}")
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for sensitive data."""
        return Fernet.generate_key()
    
    async def _send_security_notification(self, event: AuditEvent) -> None:
        """
Send security notification for critical events."""
        # This would integrate with notification system
        logger.critical(f"Security alert: {event.event_type.value} - {event.event_data}")
    
    async def _send_error_notification(self, event: AuditEvent) -> None:
        """Send error notification."""
        # This would integrate with notification system
        logger.error(f"System error: {event.event_type.value} - {event.event_data}")
    
    async def _update_security_metrics(self, event: AuditEvent) -> None:
        """Update security metrics."""
        try:
            # Initialize security metrics if not exists
            if not hasattr(self, 'security_metrics'):
                self.security_metrics = {
                    'access_attempts': {'total': 0, 'successful': 0, 'failed': 0},
                    'privilege_escalations': 0,
                    'suspicious_activities': 0,
                    'data_access_events': 0,
                    'authentication_events': {'logins': 0, 'logouts': 0, 'failed_logins': 0},
                    'authorization_failures': 0,
                    'security_violations': 0,
                    'encryption_events': 0,
                    'audit_integrity_checks': 0,
                    'last_updated': datetime.now().isoformat()
                }
            
            # Update metrics based on event type
            event_type = event.event_type.value
            
            if event_type in ['USER_LOGIN', 'API_ACCESS', 'SYSTEM_ACCESS']:
                self.security_metrics['access_attempts']['total'] += 1
                if event.result == 'SUCCESS':
                    self.security_metrics['access_attempts']['successful'] += 1
                else:
                    self.security_metrics['access_attempts']['failed'] += 1
            
            elif event_type == 'USER_LOGIN':
                if event.result == 'SUCCESS':
                    self.security_metrics['authentication_events']['logins'] += 1
                else:
                    self.security_metrics['authentication_events']['failed_logins'] += 1
            
            elif event_type == 'USER_LOGOUT':
                self.security_metrics['authentication_events']['logouts'] += 1
            
            elif event_type == 'PRIVILEGE_ESCALATION':
                self.security_metrics['privilege_escalations'] += 1
            
            elif event_type == 'SUSPICIOUS_ACTIVITY':
                self.security_metrics['suspicious_activities'] += 1
            
            elif event_type in ['DATA_ACCESS', 'FILE_ACCESS', 'DATABASE_ACCESS']:
                self.security_metrics['data_access_events'] += 1
            
            elif event_type == 'AUTHORIZATION_FAILURE':
                self.security_metrics['authorization_failures'] += 1
            
            elif event_type == 'SECURITY_VIOLATION':
                self.security_metrics['security_violations'] += 1
            
            elif event_type in ['ENCRYPT', 'DECRYPT', 'KEY_ROTATION']:
                self.security_metrics['encryption_events'] += 1
            
            elif event_type == 'AUDIT_INTEGRITY_CHECK':
                self.security_metrics['audit_integrity_checks'] += 1
            
            # Update timestamp
            self.security_metrics['last_updated'] = datetime.now().isoformat()
            
            # Store metrics persistently if configured
            await self._persist_security_metrics()
            
            logger.debug(f"Updated security metrics for event type: {event_type}")
            
        except Exception as e:
            logger.error(f"Error updating security metrics: {str(e)}")
    
    async def _update_violation_metrics(self, event: AuditEvent) -> None:
        """Update violation metrics."""
        try:
            # Initialize violation metrics if not exists
            if not hasattr(self, 'violation_metrics'):
                self.violation_metrics = {
                    'copyright_violations': 0,
                    'license_violations': 0,
                    'access_violations': 0,
                    'data_policy_violations': 0,
                    'terms_violations': 0,
                    'privacy_violations': 0,
                    'security_violations': 0,
                    'compliance_violations': 0,
                    'severity_breakdown': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                    'user_violations': {},  # user_id -> violation_count
                    'violation_trends': [],  # Time series data
                    'last_updated': datetime.now().isoformat()
                }
            
            # Determine violation type from event data
            violation_type = self._classify_violation(event)
            
            if violation_type in self.violation_metrics:
                self.violation_metrics[violation_type] += 1
            
            # Update severity breakdown
            severity = event.event_data.get('severity', 'medium')
            if severity in self.violation_metrics['severity_breakdown']:
                self.violation_metrics['severity_breakdown'][severity] += 1
            
            # Track per-user violations
            user_id = event.user_id
            if user_id:
                if user_id not in self.violation_metrics['user_violations']:
                    self.violation_metrics['user_violations'][user_id] = 0
                self.violation_metrics['user_violations'][user_id] += 1
            
            # Add to trend data
            trend_entry = {
                'timestamp': event.timestamp.isoformat(),
                'violation_type': violation_type,
                'severity': severity,
                'user_id': user_id
            }
            self.violation_metrics['violation_trends'].append(trend_entry)
            
            # Keep only last 1000 trend entries to prevent memory issues
            if len(self.violation_metrics['violation_trends']) > 1000:
                self.violation_metrics['violation_trends'] = self.violation_metrics['violation_trends'][-1000:]
            
            # Update timestamp
            self.violation_metrics['last_updated'] = datetime.now().isoformat()
            
            # Store metrics persistently
            await self._persist_violation_metrics()
            
            logger.info(f"Updated violation metrics: {violation_type} (severity: {severity})")
            
        except Exception as e:
            logger.error(f"Error updating violation metrics: {str(e)}")
    
    async def _track_failed_access(self, user_id: str, event: AuditEvent) -> None:
        """Track failed access attempts for user."""
        try:
            # Initialize failed access tracking
            if not hasattr(self, 'failed_access_tracking'):
                self.failed_access_tracking = {}
            
            current_time = datetime.now()
            
            # Initialize user tracking if not exists
            if user_id not in self.failed_access_tracking:
                self.failed_access_tracking[user_id] = {
                    'failed_attempts': 0,
                    'first_failure': current_time.isoformat(),
                    'last_failure': current_time.isoformat(),
                    'failure_details': [],
                    'blocked': False,
                    'block_until': None
                }
            
            user_tracking = self.failed_access_tracking[user_id]
            
            # Update failure count and details
            user_tracking['failed_attempts'] += 1
            user_tracking['last_failure'] = current_time.isoformat()
            
            failure_detail = {
                'timestamp': current_time.isoformat(),
                'event_type': event.event_type.value,
                'ip_address': event.event_data.get('ip_address', 'unknown'),
                'user_agent': event.event_data.get('user_agent', 'unknown'),
                'reason': event.event_data.get('failure_reason', 'unknown')
            }
            user_tracking['failure_details'].append(failure_detail)
            
            # Keep only last 20 failure details
            if len(user_tracking['failure_details']) > 20:
                user_tracking['failure_details'] = user_tracking['failure_details'][-20:]
            
            # Check if user should be blocked (configurable thresholds)
            block_threshold = 5  # 5 failed attempts
            block_duration_minutes = 30
            
            if user_tracking['failed_attempts'] >= block_threshold and not user_tracking['blocked']:
                user_tracking['blocked'] = True
                block_until = current_time + timedelta(minutes=block_duration_minutes)
                user_tracking['block_until'] = block_until.isoformat()
                
                # Log security alert
                logger.warning(f"User {user_id} blocked due to {user_tracking['failed_attempts']} failed access attempts")
                
                # Create security alert
                await self._create_security_alert(user_id, 'EXCESSIVE_FAILED_ACCESS', {
                    'failed_attempts': user_tracking['failed_attempts'],
                    'block_duration_minutes': block_duration_minutes,
                    'first_failure': user_tracking['first_failure'],
                    'last_failure': user_tracking['last_failure']
                })
            
            # Clean up old tracking data (older than 24 hours)
            cutoff_time = current_time - timedelta(hours=24)
            for uid, tracking in list(self.failed_access_tracking.items()):
                first_failure = datetime.fromisoformat(tracking['first_failure'])
                if first_failure < cutoff_time and tracking['failed_attempts'] < block_threshold:
                    del self.failed_access_tracking[uid]
            
            logger.debug(f"Tracked failed access for user {user_id}: {user_tracking['failed_attempts']} attempts")
            
        except Exception as e:
            logger.error(f"Error tracking failed access for user {user_id}: {str(e)}")
    
    def _classify_violation(self, event: AuditEvent) -> str:
        """Classify violation type based on event data"""
        event_type = event.event_type.value
        event_data = event.event_data
        
        # Map event types to violation categories
        if 'copyright' in event_type.lower() or 'infringement' in event_type.lower():
            return 'copyright_violations'
        elif 'license' in event_type.lower():
            return 'license_violations'
        elif 'access' in event_type.lower() and event.result != 'SUCCESS':
            return 'access_violations'
        elif 'privacy' in event_type.lower() or 'gdpr' in event_type.lower():
            return 'privacy_violations'
        elif 'security' in event_type.lower():
            return 'security_violations'
        elif 'compliance' in event_type.lower():
            return 'compliance_violations'
        elif 'policy' in event_type.lower():
            return 'data_policy_violations'
        else:
            return 'terms_violations'
    
    async def _persist_security_metrics(self):
        """
Persist security metrics to storage"""
        try:
            if hasattr(self, 'storage_client'):
                await self.storage_client.store_metrics('security', self.security_metrics)
        except Exception as e:
            logger.debug(f"Failed to persist security metrics: {str(e)}")
    
    async def _persist_violation_metrics(self):
        """Persist violation metrics to storage"""
        try:
            if hasattr(self, 'storage_client'):
                await self.storage_client.store_metrics('violations', self.violation_metrics)
        except Exception as e:
            logger.debug(f"Failed to persist violation metrics: {str(e)}")
    
    async def _create_security_alert(self, user_id: str, alert_type: str, alert_data: dict):
        """Create security alert for excessive failed access"""
        try:
            if hasattr(self, 'alert_client'):
                await self.alert_client.create_alert({
                    'type': alert_type,
                    'severity': 'HIGH',
                    'user_id': user_id,
                    'data': alert_data,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.debug(f"Failed to create security alert: {str(e)}")
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics."""
        try:
            total_events = len(self.events)
            
            stats = {
                "total_events": total_events,
                "events_by_type": {},
                "events_by_severity": {},
                "events_by_category": {},
                "encrypted_events": 0,
                "signed_events": 0
            }
            
            for event in self.events:
                # Count by type
                event_type = event.event_type.value
                stats["events_by_type"][event_type] = stats["events_by_type"].get(event_type, 0) + 1
                
                # Count by severity
                severity = event.severity.value
                stats["events_by_severity"][severity] = stats["events_by_severity"].get(severity, 0) + 1
                
                # Count by category
                category = event.category.value
                stats["events_by_category"][category] = stats["events_by_category"].get(category, 0) + 1
                
                # Count encrypted/signed events
                if event.encrypted:
                    stats["encrypted_events"] += 1
                if event.signature:
                    stats["signed_events"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting audit statistics: {e}")
            return {}
    
    async def verify_event_integrity(self, event_id: str) -> bool:
        """Verify integrity of an audit event."""
        try:
            event = next((e for e in self.events if e.event_id == event_id), None)
            if not event:
                return False
            
            # Verify checksum
            calculated_checksum = self._calculate_checksum(event)
            if calculated_checksum != event.checksum:
                logger.warning(f"Checksum mismatch for event {event_id}")
                return False
            
            # Verify signature if present
            if event.signature and self.signing_enabled:
                expected_signature = await self._sign_event(event)
                if expected_signature != event.signature:
                    logger.warning(f"Signature verification failed for event {event_id}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying event integrity: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup audit trail resources."""
        try:
            # Archive remaining events
            if self.events:
                await self._archive_events(self.events)
            
            logger.info("Audit trail cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during audit trail cleanup: {e}")
