"""Audit Trail Generator - SOC 2 Compliance & Enterprise Audit Logging

Enterprise-grade audit trail generation system with comprehensive logging,
immutable audit records, and automated compliance reporting for ML operations.

Author: Fahed Mlaiel (mlaiel@live.de)  
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

🛡️ SECURITY EXPERT IMPLEMENTATION:
- SOC 2 Type II compliance with automated controls
- Immutable audit trails with cryptographic integrity
- Real-time security event monitoring and alerting
- Comprehensive access logging and user activity tracking
- Automated compliance reporting and evidence collection
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class AuditEventType(Enum):
    """Types of audit events for comprehensive logging."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    MODEL_TRAINING = "model_training"
    MODEL_DEPLOYMENT = "model_deployment"
    CONFIG_CHANGE = "config_change"
    PERMISSION_CHANGE = "permission_change"
    DATA_EXPORT = "data_export"
    SYSTEM_ERROR = "system_error"
    SECURITY_INCIDENT = "security_incident"
    COMPLIANCE_CHECK = "compliance_check"
    BACKUP_OPERATION = "backup_operation"

class AuditSeverity(Enum):
    """Audit event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ComplianceFramework(Enum):
    """Compliance frameworks for audit requirements."""
    SOC2_TYPE2 = "soc2_type2"
    ISO27001 = "iso27001"
    GDPR_AUDIT = "gdpr_audit"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"

@dataclass
class AuditEvent:
    """Immutable audit event record."""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: str
    session_id: str
    source_ip: str
    user_agent: str
    resource_accessed: str
    action_performed: str
    outcome: str  # "success", "failure", "error"
    details: Dict[str, Any]
    risk_score: float
    compliance_tags: List[str]
    checksum: str  # For integrity verification

@dataclass
class ComplianceControl:
    """SOC 2 compliance control definition."""
    control_id: str
    control_name: str
    framework: ComplianceFramework
    description: str
    automated: bool
    frequency: str  # "continuous", "daily", "weekly", "monthly"
    evidence_requirements: List[str]
    last_check: Optional[datetime]
    status: str  # "compliant", "non_compliant", "needs_review"

class AuditTrailGenerator:
    """Enterprise audit trail generation system for ML operations.
    
    Features:
    - Immutable audit logs with cryptographic integrity
    - SOC 2 Type II compliance controls
    - Real-time security monitoring
    - Automated compliance reporting
    - Evidence collection and retention
    - Anomaly detection in audit logs
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize audit trail generator.
        
        Args:
            config: Configuration including storage, encryption, compliance settings
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Audit configuration
        self.storage_path = Path(self.config.get('storage_path', './audit_logs'))
        self.encryption_enabled = self.config.get('encryption_enabled', True)
        self.real_time_monitoring = self.config.get('real_time_monitoring', True)
        self.retention_days = self.config.get('retention_days', 2555)  # 7 years default
        self.compliance_frameworks = self.config.get('compliance_frameworks', [
            ComplianceFramework.SOC2_TYPE2, ComplianceFramework.ISO27001
        ])
        
        # Initialize storage and encryption
        self._initialize_storage()
        self._initialize_encryption()
        self._initialize_compliance_controls()
        
        # Audit trail state
        self.audit_events: List[AuditEvent] = []
        self.compliance_controls: Dict[str, ComplianceControl] = {}
        self.security_incidents: List[Dict[str, Any]] = []
        
        self.logger.info("🛡️ Audit Trail Generator initialized successfully")
    
    def _initialize_storage(self) -> None:
        """Initialize audit storage infrastructure."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite database for audit logs
        self.db_path = self.storage_path / "audit_trail.db"
        self._create_audit_tables()
        
        # Create directories for audit files
        (self.storage_path / "daily_logs").mkdir(exist_ok=True)
        (self.storage_path / "compliance_reports").mkdir(exist_ok=True)
        (self.storage_path / "evidence").mkdir(exist_ok=True)
    
    def _create_audit_tables(self) -> None:
        """Create SQLite tables for audit storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Audit events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT,
                source_ip TEXT,
                user_agent TEXT,
                resource_accessed TEXT,
                action_performed TEXT,
                outcome TEXT,
                details TEXT,
                risk_score REAL,
                compliance_tags TEXT,
                checksum TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Compliance controls table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_controls (
                control_id TEXT PRIMARY KEY,
                control_name TEXT NOT NULL,
                framework TEXT NOT NULL,
                description TEXT,
                automated BOOLEAN,
                frequency TEXT,
                evidence_requirements TEXT,
                last_check TEXT,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security incidents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_incidents (
                incident_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                affected_resources TEXT,
                response_actions TEXT,
                status TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_encryption(self) -> None:
        """Initialize encryption for sensitive audit data."""
        if not self.encryption_enabled:
            self.cipher_suite = None
            return
        
        # Generate or load encryption key
        key_file = self.storage_path / ".audit_key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            password = os.urandom(32)
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Store key securely (in production, use HSM or key vault)
            with open(key_file, 'wb') as f:
                f.write(key)
            key_file.chmod(0o600)  # Restrict access
        
        self.cipher_suite = Fernet(key)
        self.logger.info("🔐 Audit encryption initialized")
    
    def _initialize_compliance_controls(self) -> None:
        """Initialize SOC 2 and other compliance controls."""
        soc2_controls = [
            ComplianceControl(
                control_id="CC6.1",
                control_name="Logical Access Controls",
                framework=ComplianceFramework.SOC2_TYPE2,
                description="Controls to restrict logical access to the system",
                automated=True,
                frequency="continuous",
                evidence_requirements=["access_logs", "user_provisioning", "privilege_reviews"],
                last_check=None,
                status="compliant"
            ),
            ComplianceControl(
                control_id="CC6.2",
                control_name="Authentication Controls",
                framework=ComplianceFramework.SOC2_TYPE2,
                description="Controls for user authentication and identity verification",
                automated=True,
                frequency="continuous",
                evidence_requirements=["login_logs", "mfa_usage", "password_policies"],
                last_check=None,
                status="compliant"
            ),
            ComplianceControl(
                control_id="CC6.3",
                control_name="Authorization Controls",
                framework=ComplianceFramework.SOC2_TYPE2,
                description="Controls for user authorization and access management",
                automated=True,
                frequency="daily",
                evidence_requirements=["permission_changes", "role_assignments", "access_reviews"],
                last_check=None,
                status="compliant"
            ),
            ComplianceControl(
                control_id="CC7.1",
                control_name="System Monitoring",
                framework=ComplianceFramework.SOC2_TYPE2,
                description="Controls for system activity monitoring and logging",
                automated=True,
                frequency="continuous",
                evidence_requirements=["system_logs", "monitoring_alerts", "incident_responses"],
                last_check=None,
                status="compliant"
            ),
            ComplianceControl(
                control_id="CC7.2",
                control_name="Data Processing Controls",
                framework=ComplianceFramework.SOC2_TYPE2,
                description="Controls for data processing integrity and security",
                automated=True,
                frequency="continuous",
                evidence_requirements=["data_access_logs", "processing_logs", "error_handling"],
                last_check=None,
                status="compliant"
            )
        ]
        
        self.compliance_controls = {ctrl.control_id: ctrl for ctrl in soc2_controls}
        self.logger.info(f"📋 Initialized {len(soc2_controls)} compliance controls")
    
    async def log_audit_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        action: str,
        resource: str,
        outcome: str,
        details: Dict[str, Any],
        session_id: str = None,
        source_ip: str = None,
        user_agent: str = None
    ) -> AuditEvent:
        """Log an audit event with full traceability.
        
        Args:
            event_type: Type of audit event
            user_id: User performing the action
            action: Action being performed
            resource: Resource being accessed
            outcome: Result of the action
            details: Additional event details
            session_id: User session identifier
            source_ip: Source IP address
            user_agent: User agent string
            
        Returns:
            AuditEvent: Created audit event
        """
        event_id = self._generate_event_id()
        timestamp = datetime.utcnow()
        
        # Calculate risk score
        risk_score = await self._calculate_risk_score(event_type, action, outcome, details)
        
        # Determine severity
        severity = self._determine_severity(event_type, outcome, risk_score)
        
        # Generate compliance tags
        compliance_tags = self._generate_compliance_tags(event_type, action, resource)
        
        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id or "unknown",
            source_ip=source_ip or "unknown",
            user_agent=user_agent or "unknown",
            resource_accessed=resource,
            action_performed=action,
            outcome=outcome,
            details=details,
            risk_score=risk_score,
            compliance_tags=compliance_tags,
            checksum=""  # Will be set after serialization
        )
        
        # Generate integrity checksum
        event.checksum = self._generate_checksum(event)
        
        # Store event
        await self._store_audit_event(event)
        
        # Add to in-memory collection
        self.audit_events.append(event)
        
        # Real-time monitoring
        if self.real_time_monitoring:
            await self._process_real_time_monitoring(event)
        
        self.logger.info(f"📊 Audit event logged: {event_id} ({event_type.value})")
        return event
    
    async def _calculate_risk_score(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str,
        details: Dict[str, Any]
    ) -> float:
        """Calculate risk score for audit event (0-1 scale)."""
        base_risk = {
            AuditEventType.USER_LOGIN: 0.2,
            AuditEventType.USER_LOGOUT: 0.1,
            AuditEventType.DATA_ACCESS: 0.5,
            AuditEventType.MODEL_TRAINING: 0.4,
            AuditEventType.MODEL_DEPLOYMENT: 0.7,
            AuditEventType.CONFIG_CHANGE: 0.8,
            AuditEventType.PERMISSION_CHANGE: 0.9,
            AuditEventType.DATA_EXPORT: 0.8,
            AuditEventType.SYSTEM_ERROR: 0.6,
            AuditEventType.SECURITY_INCIDENT: 1.0,
            AuditEventType.COMPLIANCE_CHECK: 0.3,
            AuditEventType.BACKUP_OPERATION: 0.2
        }
        
        risk_score = base_risk.get(event_type, 0.5)
        
        # Outcome modifiers
        if outcome == "failure":
            risk_score *= 1.5
        elif outcome == "error":
            risk_score *= 1.3
        
        # Action modifiers
        high_risk_actions = ["delete", "export", "modify_permissions", "deploy_production"]
        if any(action_keyword in action.lower() for action_keyword in high_risk_actions):
            risk_score *= 1.4
        
        # Context modifiers
        if details.get("admin_action", False):
            risk_score *= 1.2
        
        if details.get("sensitive_data", False):
            risk_score *= 1.3
        
        if details.get("external_access", False):
            risk_score *= 1.5
        
        return min(risk_score, 1.0)
    
    def _determine_severity(
        self,
        event_type: AuditEventType,
        outcome: str,
        risk_score: float
    ) -> AuditSeverity:
        """Determine audit event severity."""
        if event_type == AuditEventType.SECURITY_INCIDENT or risk_score >= 0.9:
            return AuditSeverity.CRITICAL
        elif outcome == "failure" or risk_score >= 0.7:
            return AuditSeverity.ERROR
        elif outcome == "error" or risk_score >= 0.5:
            return AuditSeverity.WARNING
        else:
            return AuditSeverity.INFO
    
    def _generate_compliance_tags(
        self,
        event_type: AuditEventType,
        action: str,
        resource: str
    ) -> List[str]:
        """Generate compliance framework tags for the event."""
        tags = []
        
        # SOC 2 Type II tags
        if event_type in [AuditEventType.USER_LOGIN, AuditEventType.USER_LOGOUT]:
            tags.extend(["CC6.1", "CC6.2"])  # Access and Authentication controls
        
        if event_type in [AuditEventType.PERMISSION_CHANGE, AuditEventType.CONFIG_CHANGE]:
            tags.extend(["CC6.3", "CC6.1"])  # Authorization controls
        
        if event_type in [AuditEventType.DATA_ACCESS, AuditEventType.DATA_EXPORT]:
            tags.extend(["CC7.2", "CC6.1"])  # Data processing and access controls
        
        if event_type == AuditEventType.SYSTEM_ERROR:
            tags.extend(["CC7.1"])  # System monitoring
        
        # ISO 27001 tags
        if "security" in action.lower() or "incident" in action.lower():
            tags.append("ISO27001-A.16")  # Information security incident management
        
        if "backup" in action.lower():
            tags.append("ISO27001-A.12.3")  # Information backup
        
        # GDPR tags
        if "personal_data" in resource.lower() or "pii" in resource.lower():
            tags.append("GDPR-Art.30")  # Records of processing activities
        
        return tags
    
    def _generate_checksum(self, event: AuditEvent) -> str:
        """Generate integrity checksum for audit event."""
        # Create deterministic string representation
        event_data = {
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type.value,
            'user_id': event.user_id,
            'action': event.action_performed,
            'resource': event.resource_accessed,
            'outcome': event.outcome,
            'details': json.dumps(event.details, sort_keys=True)
        }
        
        event_string = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(event_string.encode()).hexdigest()
    
    async def _store_audit_event(self, event -> None: AuditEvent) -> None:
        """Store audit event in persistent storage."""
        # Store in SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_events (
                event_id, timestamp, event_type, severity, user_id, session_id,
                source_ip, user_agent, resource_accessed, action_performed,
                outcome, details, risk_score, compliance_tags, checksum
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.event_id,
            event.timestamp.isoformat(),
            event.event_type.value,
            event.severity.value,
            event.user_id,
            event.session_id,
            event.source_ip,
            event.user_agent,
            event.resource_accessed,
            event.action_performed,
            event.outcome,
            json.dumps(event.details),
            event.risk_score,
            json.dumps(event.compliance_tags),
            event.checksum
        ))
        
        conn.commit()
        conn.close()
        
        # Store encrypted daily log file
        if self.encryption_enabled:
            await self._store_encrypted_log(event)
    
    async def _store_encrypted_log(self, event -> None: AuditEvent) -> None:
        """Store encrypted audit log for long-term retention."""
        date_str = event.timestamp.strftime('%Y-%m-%d')
        log_file = self.storage_path / "daily_logs" / f"audit_{date_str}.log"
        
        # Prepare log entry
        log_entry = {
            'timestamp': event.timestamp.isoformat(),
            'event': asdict(event),
            'version': '1.0'
        }
        
        log_line = json.dumps(log_entry) + '\n'
        
        # Encrypt if enabled
        if self.cipher_suite:
            log_line = self.cipher_suite.encrypt(log_line.encode()).decode()
        
        # Append to daily log file
        with open(log_file, 'a') as f:
            f.write(log_line)
    
    async def _process_real_time_monitoring(self, event -> None: AuditEvent) -> None:
        """Process real-time monitoring for security incidents."""
        # Check for security incidents
        if event.severity in [AuditSeverity.CRITICAL, AuditSeverity.ERROR]:
            await self._handle_security_incident(event)
        
        # Check for compliance violations
        if event.outcome == "failure" and event.risk_score > 0.7:
            await self._handle_compliance_violation(event)
        
        # Anomaly detection
        await self._detect_anomalies(event)
    
    async def _handle_security_incident(self, event -> None: AuditEvent) -> None:
        """Handle potential security incident."""
        incident_id = f"SI_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(event.event_id) % 10000:04d}"
        
        incident = {
            'incident_id': incident_id,
            'timestamp': event.timestamp.isoformat(),
            'trigger_event': event.event_id,
            'incident_type': 'audit_anomaly',
            'severity': event.severity.value,
            'description': f"High-risk audit event detected: {event.action_performed}",
            'affected_resources': [event.resource_accessed],
            'response_actions': ['investigate', 'monitor', 'alert_security_team'],
            'status': 'open'
        }
        
        self.security_incidents.append(incident)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_incidents (
                incident_id, timestamp, incident_type, severity, description,
                affected_resources, response_actions, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident['incident_id'],
            incident['timestamp'],
            incident['incident_type'],
            incident['severity'],
            incident['description'],
            json.dumps(incident['affected_resources']),
            json.dumps(incident['response_actions']),
            incident['status']
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.warning(f"🚨 Security incident created: {incident_id}")
    
    async def _handle_compliance_violation(self, event -> None: AuditEvent) -> None:
        """Handle potential compliance violation."""
        for tag in event.compliance_tags:
            if tag in self.compliance_controls:
                control = self.compliance_controls[tag]
                control.status = "needs_review"
                control.last_check = datetime.utcnow()
                
                self.logger.warning(f"⚠️ Compliance control {tag} requires review due to event {event.event_id}")
    
    async def _detect_anomalies(self, event -> None: AuditEvent) -> None:
        """Detect anomalies in audit patterns."""
        # Simple anomaly detection based on recent events
        recent_events = [
            e for e in self.audit_events[-100:]  # Last 100 events
            if e.user_id == event.user_id and e.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        # Check for unusual activity patterns
        if len(recent_events) > 50:  # Too many events in short time
            await self._create_anomaly_alert("high_activity_volume", event, recent_events)
        
        # Check for privilege escalation
        admin_actions = [e for e in recent_events if e.details.get("admin_action", False)]
        if len(admin_actions) > 5:
            await self._create_anomaly_alert("potential_privilege_escalation", event, admin_actions)
    
    async def _create_anomaly_alert(self, anomaly_type -> None: str, event -> None: AuditEvent, related_events -> None: List[AuditEvent]) -> None:
        """Create anomaly alert for investigation."""
        alert = {
            'alert_id': f"AA_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(event.event_id) % 1000:03d}",
            'timestamp': datetime.utcnow().isoformat(),
            'anomaly_type': anomaly_type,
            'trigger_event': event.event_id,
            'user_id': event.user_id,
            'related_events': [e.event_id for e in related_events],
            'risk_score': max(e.risk_score for e in related_events + [event]),
            'requires_investigation': True
        }
        
        self.logger.warning(f"🔍 Anomaly detected: {alert['alert_id']} ({anomaly_type})")
    
    async def generate_compliance_report(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report.
        
        Args:
            framework: Compliance framework to report on
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dict: Compliance report with evidence and controls
        """
        # Filter events by date range and compliance tags
        relevant_events = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_events 
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        for row in rows:
            event_dict = dict(zip(columns, row))
            compliance_tags = json.loads(event_dict['compliance_tags'])
            
            # Check if event is relevant to framework
            framework_relevant = False
            if framework == ComplianceFramework.SOC2_TYPE2:
                framework_relevant = any(tag.startswith('CC') for tag in compliance_tags)
            elif framework == ComplianceFramework.ISO27001:
                framework_relevant = any(tag.startswith('ISO27001') for tag in compliance_tags)
            elif framework == ComplianceFramework.GDPR_AUDIT:
                framework_relevant = any(tag.startswith('GDPR') for tag in compliance_tags)
            
            if framework_relevant:
                relevant_events.append(event_dict)
        
        conn.close()
        
        # Generate report sections
        report = {
            'report_metadata': {
                'framework': framework.value,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'generated_at': datetime.utcnow().isoformat(),
                'total_events': len(relevant_events)
            },
            'control_effectiveness': await self._assess_control_effectiveness(framework, relevant_events),
            'audit_coverage': await self._assess_audit_coverage(relevant_events),
            'incident_summary': await self._summarize_incidents(start_date, end_date),
            'compliance_gaps': await self._identify_compliance_gaps(framework, relevant_events),
            'evidence_collection': await self._collect_compliance_evidence(framework, relevant_events),
            'recommendations': await self._generate_compliance_recommendations(framework, relevant_events)
        }
        
        # Store report
        report_file = self.storage_path / "compliance_reports" / f"{framework.value}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"📊 Compliance report generated: {report_file}")
        return report
    
    async def _assess_control_effectiveness(
        self,
        framework: ComplianceFramework,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess effectiveness of compliance controls."""
        control_assessment = {}
        
        # Get framework-specific controls
        framework_controls = [
            ctrl for ctrl in self.compliance_controls.values()
            if ctrl.framework == framework
        ]
        
        for control in framework_controls:
            # Count relevant events
            control_events = [
                e for e in events
                if control.control_id in json.loads(e['compliance_tags'])
            ]
            
            # Calculate effectiveness metrics
            total_events = len(control_events)
            successful_events = len([e for e in control_events if e['outcome'] == 'success'])
            failed_events = len([e for e in control_events if e['outcome'] == 'failure'])
            
            effectiveness_score = successful_events / total_events if total_events > 0 else 1.0
            
            control_assessment[control.control_id] = {
                'control_name': control.control_name,
                'total_events': total_events,
                'successful_events': successful_events,
                'failed_events': failed_events,
                'effectiveness_score': effectiveness_score,
                'status': control.status,
                'last_check': control.last_check.isoformat() if control.last_check else None,
                'evidence_count': len([e for e in control_events if e['severity'] != 'info'])
            }
        
        return control_assessment
    
    async def _assess_audit_coverage(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess audit log coverage and completeness."""
        # Analyze event distribution
        event_types = {}
        hourly_distribution = {}
        user_coverage = set()
        
        for event in events:
            # Event type distribution
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Hourly distribution
            timestamp = datetime.fromisoformat(event['timestamp'])
            hour_key = timestamp.strftime('%Y-%m-%d-%H')
            hourly_distribution[hour_key] = hourly_distribution.get(hour_key, 0) + 1
            
            # User coverage
            user_coverage.add(event['user_id'])
        
        # Calculate coverage metrics
        total_hours = len(hourly_distribution)
        avg_events_per_hour = sum(hourly_distribution.values()) / total_hours if total_hours > 0 else 0
        
        return {
            'total_events': len(events),
            'unique_event_types': len(event_types),
            'event_type_distribution': event_types,
            'unique_users': len(user_coverage),
            'time_coverage_hours': total_hours,
            'average_events_per_hour': avg_events_per_hour,
            'coverage_gaps': [hour for hour, count in hourly_distribution.items() if count < 5]
        }
    
    async def _summarize_incidents(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Summarize security incidents in the period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM security_incidents 
            WHERE timestamp BETWEEN ? AND ?
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        incidents = cursor.fetchall()
        conn.close()
        
        # Categorize incidents
        incident_summary = {
            'total_incidents': len(incidents),
            'by_severity': {},
            'by_type': {},
            'open_incidents': 0,
            'resolved_incidents': 0
        }
        
        for incident in incidents:
            severity = incident[3]  # severity column
            incident_type = incident[2]  # incident_type column
            status = incident[7]  # status column
            
            incident_summary['by_severity'][severity] = incident_summary['by_severity'].get(severity, 0) + 1
            incident_summary['by_type'][incident_type] = incident_summary['by_type'].get(incident_type, 0) + 1
            
            if status == 'open':
                incident_summary['open_incidents'] += 1
            else:
                incident_summary['resolved_incidents'] += 1
        
        return incident_summary
    
    async def _identify_compliance_gaps(
        self,
        framework: ComplianceFramework,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify compliance gaps and issues."""
        gaps = []
        
        # Check for missing audit coverage
        required_event_types = [
            AuditEventType.USER_LOGIN,
            AuditEventType.DATA_ACCESS,
            AuditEventType.PERMISSION_CHANGE,
            AuditEventType.CONFIG_CHANGE
        ]
        
        covered_types = set(event['event_type'] for event in events)
        
        for required_type in required_event_types:
            if required_type.value not in covered_types:
                gaps.append({
                    'gap_type': 'missing_audit_coverage',
                    'description': f"No audit events found for {required_type.value}",
                    'severity': 'medium',
                    'recommendation': f"Ensure {required_type.value} events are properly logged"
                })
        
        # Check for high failure rates
        failure_events = [e for e in events if e['outcome'] == 'failure']
        if len(failure_events) > len(events) * 0.1:  # More than 10% failures
            gaps.append({
                'gap_type': 'high_failure_rate',
                'description': f"High failure rate detected: {len(failure_events)}/{len(events)} events",
                'severity': 'high',
                'recommendation': "Investigate root causes of system failures"
            })
        
        return gaps
    
    async def _collect_compliance_evidence(
        self,
        framework: ComplianceFramework,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Collect evidence for compliance audits."""
        evidence = {
            'audit_logs_count': len(events),
            'log_integrity_verified': await self._verify_log_integrity(events),
            'access_control_events': len([e for e in events if e['event_type'] in [
                'user_login', 'permission_change', 'config_change'
            ]]),
            'data_processing_events': len([e for e in events if e['event_type'] in [
                'data_access', 'model_training', 'data_export'
            ]]),
            'system_monitoring_events': len([e for e in events if e['event_type'] in [
                'system_error', 'security_incident', 'compliance_check'
            ]]),
            'evidence_files': []
        }
        
        # Create evidence files
        evidence_dir = self.storage_path / "evidence"
        
        # Access control evidence
        access_events = [e for e in events if e['event_type'] in ['user_login', 'permission_change']]
        if access_events:
            access_file = evidence_dir / f"access_control_{framework.value}.json"
            with open(access_file, 'w') as f:
                json.dump(access_events, f, indent=2, default=str)
            evidence['evidence_files'].append(str(access_file))
        
        # Data processing evidence
        data_events = [e for e in events if e['event_type'] in ['data_access', 'data_export']]
        if data_events:
            data_file = evidence_dir / f"data_processing_{framework.value}.json"
            with open(data_file, 'w') as f:
                json.dump(data_events, f, indent=2, default=str)
            evidence['evidence_files'].append(str(data_file))
        
        return evidence
    
    async def _verify_log_integrity(self, events: List[Dict[str, Any]]) -> bool:
        """Verify integrity of audit logs using checksums."""
        for event in events:
            # Reconstruct checksum
            event_data = {
                'event_id': event['event_id'],
                'timestamp': event['timestamp'],
                'event_type': event['event_type'],
                'user_id': event['user_id'],
                'action': event['action_performed'],
                'resource': event['resource_accessed'],
                'outcome': event['outcome'],
                'details': event['details']
            }
            
            expected_checksum = hashlib.sha256(
                json.dumps(event_data, sort_keys=True).encode()
            ).hexdigest()
            
            if event['checksum'] != expected_checksum:
                self.logger.error(f"Integrity violation detected for event {event['event_id']}")
                return False
        
        return True
    
    async def _generate_compliance_recommendations(
        self,
        framework: ComplianceFramework,
        events: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []
        
        # Analyze audit patterns
        failure_rate = len([e for e in events if e['outcome'] == 'failure']) / len(events) if events else 0
        
        if failure_rate > 0.05:  # More than 5% failures
            recommendations.append("Investigate and reduce system failure rate")
            recommendations.append("Implement additional error handling and recovery mechanisms")
        
        # Check monitoring coverage
        monitoring_events = len([e for e in events if e['event_type'] == 'system_error'])
        if monitoring_events < len(events) * 0.1:
            recommendations.append("Increase system monitoring and error detection coverage")
        
        # Check access control patterns
        access_events = len([e for e in events if e['event_type'] in ['user_login', 'permission_change']])
        if access_events < len(events) * 0.3:
            recommendations.append("Enhance access control monitoring and logging")
        
        if not recommendations:
            recommendations.append("Audit patterns appear compliant with framework requirements")
            recommendations.append("Continue regular monitoring and periodic reviews")
        
        return recommendations
    
    def _generate_event_id(self) -> str:
        """Generate unique audit event ID."""
        return f"AE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.utcnow()) % 100000:05d}"
    
    async def get_audit_metrics(self) -> Dict[str, Any]:
        """Get current audit trail metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic counts
        cursor.execute("SELECT COUNT(*) FROM audit_events")
        total_events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM security_incidents WHERE status = 'open'")
        open_incidents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM compliance_controls WHERE status = 'compliant'")
        compliant_controls = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM compliance_controls")
        total_controls = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_audit_events': total_events,
            'open_security_incidents': open_incidents,
            'compliant_controls': compliant_controls,
            'total_controls': total_controls,
            'compliance_rate': compliant_controls / total_controls if total_controls > 0 else 0,
            'storage_path': str(self.storage_path),
            'encryption_enabled': self.encryption_enabled,
            'frameworks_monitored': [f.value for f in self.compliance_frameworks]
        }


# Example usage and testing
async def main() -> None:
    """Test audit trail generator functionality."""
    # Initialize audit trail generator
    config = {
        'storage_path': './test_audit_logs',
        'encryption_enabled': True,
        'real_time_monitoring': True,
        'compliance_frameworks': [ComplianceFramework.SOC2_TYPE2]
    }
    
    generator = AuditTrailGenerator(config)
    
    # Log various audit events
    events = [
        {
            'event_type': AuditEventType.USER_LOGIN,
            'user_id': 'creator_123',
            'action': 'login',
            'resource': 'ml_platform',
            'outcome': 'success',
            'details': {'method': 'sso', 'location': 'Germany'},
            'source_ip': '192.168.1.100'
        },
        {
            'event_type': AuditEventType.MODEL_TRAINING,
            'user_id': 'creator_123',
            'action': 'start_training',
            'resource': 'audio_classifier_v2',
            'outcome': 'success',
            'details': {'dataset_size': 10000, 'training_time': 3600},
            'source_ip': '192.168.1.100'
        },
        {
            'event_type': AuditEventType.DATA_EXPORT,
            'user_id': 'creator_456',
            'action': 'export_user_data',
            'resource': 'user_profile_data',
            'outcome': 'success',
            'details': {'export_format': 'json', 'records_count': 500, 'sensitive_data': True},
            'source_ip': '10.0.0.50'
        }
    ]
    
    logged_events = []
    for event_config in events:
        event = await generator.log_audit_event(**event_config)
        logged_events.append(event)
        print(f"Logged event: {event.event_id} (risk: {event.risk_score:.2f})")
    
    # Generate compliance report
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    
    report = await generator.generate_compliance_report(
        framework=ComplianceFramework.SOC2_TYPE2,
        start_date=start_date,
        end_date=end_date
    )
    
    print("\nSOC 2 Compliance Report:")
    print(f"Total events: {report['report_metadata']['total_events']}")
    print(f"Control effectiveness: {len(report['control_effectiveness'])} controls assessed")
    print(f"Evidence files: {len(report['evidence_collection']['evidence_files'])}")
    
    # Get audit metrics
    metrics = await generator.get_audit_metrics()
    print(f"\nAudit Metrics: {json.dumps(metrics, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())