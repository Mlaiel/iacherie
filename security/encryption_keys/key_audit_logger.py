#!/usr/bin/env python3
"""
🔐 Key Audit Logger - Enterprise Cryptographic Audit and Compliance Logging System
Production-grade audit logging for Ainflue Creator Economy Platform

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

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import hashlib
import secrets
import base64
import json
import gzip
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import yaml
from pathlib import Path
import threading
import queue
import sqlite3
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    KEY_CREATED = "key_created"
    KEY_ACCESSED = "key_accessed"
    KEY_MODIFIED = "key_modified"
    KEY_DELETED = "key_deleted"
    KEY_ROTATED = "key_rotated"
    KEY_ESCROWED = "key_escrowed"
    KEY_RECOVERED = "key_recovered"
    KEY_DERIVED = "key_derived"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ENCRYPTION_OPERATION = "encryption_operation"
    DECRYPTION_OPERATION = "decryption_operation"
    SIGNATURE_OPERATION = "signature_operation"
    VERIFICATION_OPERATION = "verification_operation"
    POLICY_CHANGE = "policy_change"
    COMPLIANCE_EVENT = "compliance_event"
    SECURITY_INCIDENT = "security_incident"
    SYSTEM_EVENT = "system_event"


class AuditLevel(Enum):
    """Audit logging levels."""
    MINIMAL = "minimal"      # Critical events only
    STANDARD = "standard"    # Standard compliance events
    DETAILED = "detailed"    # Detailed operational events
    COMPREHENSIVE = "comprehensive"  # All events including debug
    FORENSIC = "forensic"    # Maximum detail for investigations


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    CCPA = "ccpa"
    FIPS_140_2 = "fips_140_2"
    COMMON_CRITERIA = "common_criteria"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    NIST_CYBERSECURITY = "nist_cybersecurity"


@dataclass
class AuditEvent:
    """Audit event structure."""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    actor_id: str
    actor_type: str  # user, system, service, etc.
    resource_id: str
    resource_type: str
    operation: str
    result: str  # success, failure, partial
    details: Dict[str, Any]
    risk_level: str  # low, medium, high, critical
    compliance_frameworks: List[ComplianceFramework]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    creator_id: Optional[str] = None
    geographic_location: Optional[str] = None
    integrity_hash: Optional[str] = None


@dataclass
class AuditPolicy:
    """Audit policy configuration."""
    policy_name: str
    event_types: List[AuditEventType]
    audit_level: AuditLevel
    retention_days: int
    encryption_required: bool
    real_time_alerts: bool
    compliance_frameworks: List[ComplianceFramework]
    include_sensitive_data: bool
    geographical_restrictions: List[str]
    export_formats: List[str]  # json, csv, xml, syslog
    storage_locations: List[str]  # local, s3, elasticsearch, etc.


@dataclass
class ComplianceRule:
    """Compliance-specific audit rule."""
    rule_id: str
    framework: ComplianceFramework
    requirement_id: str
    description: str
    mandatory_fields: List[str]
    retention_requirements: Dict[str, int]
    access_restrictions: List[str]
    reporting_frequency: str  # daily, weekly, monthly, quarterly
    alert_conditions: List[str]


@dataclass
class AuditQuery:
    """Audit log query structure."""
    query_id: str
    requester_id: str
    start_date: datetime
    end_date: datetime
    event_types: Optional[List[AuditEventType]] = None
    actor_id: Optional[str] = None
    resource_id: Optional[str] = None
    compliance_framework: Optional[ComplianceFramework] = None
    risk_level: Optional[str] = None
    limit: int = 1000
    offset: int = 0


class KeyAuditLogger:
    """
    🔐 Key Audit Logger - Enterprise Cryptographic Audit System
    
    Provides comprehensive audit logging for Ainflue Creator Economy:
    - Comprehensive cryptographic operation logging
    - Compliance framework support (SOX, PCI-DSS, GDPR, etc.)
    - Real-time security event monitoring and alerting
    - Tamper-evident audit trail with integrity verification
    - Creator-specific audit policies and privacy controls
    - Advanced query and reporting capabilities
    - Multi-format export and integration support
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Key Audit Logger."""
        self.config = self._load_configuration(config_path)
        self.audit_policies: Dict[str, AuditPolicy] = {}
        self.compliance_rules: Dict[ComplianceFramework, List[ComplianceRule]] = {}
        self.event_queue = queue.Queue(maxsize=10000)
        self.logger_thread: Optional[threading.Thread] = None
        self.running = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize storage backends
        self._initialize_storage_backends()
        
        # Initialize compliance rules
        self._initialize_compliance_rules()
        
        # Initialize default policies
        self._initialize_default_policies()
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []

    def _load_configuration(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load audit logger configuration."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f).get('audit_logger_config', {})
        
        # Default configuration
        return {
            "default_audit_level": AuditLevel.STANDARD.value,
            "default_retention_days": 2555,  # 7 years
            "enable_encryption": True,
            "enable_compression": True,
            "enable_real_time_alerts": True,
            "batch_size": 100,
            "flush_interval_seconds": 60,
            "storage_backends": ["sqlite", "filesystem"],
            "compliance_frameworks": ["SOX", "PCI_DSS", "GDPR"],
            "alert_thresholds": {
                "failed_operations_per_minute": 10,
                "high_risk_events_per_hour": 5,
                "critical_events_immediate": 1
            }
        }

    def _initialize_storage_backends(self):
        """Initialize storage backends for audit logs."""
        self.storage_backends = {}
        
        # SQLite backend for structured queries
        if "sqlite" in self.config.get("storage_backends", []):
            db_path = Path("audit_logs.db")
            self.storage_backends["sqlite"] = self._initialize_sqlite_backend(db_path)
        
        # Filesystem backend for long-term storage
        if "filesystem" in self.config.get("storage_backends", []):
            log_dir = Path("audit_logs")
            log_dir.mkdir(exist_ok=True)
            self.storage_backends["filesystem"] = log_dir

    def _initialize_sqlite_backend(self, db_path: Path) -> sqlite3.Connection:
        """Initialize SQLite database for audit logs."""
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                operation TEXT NOT NULL,
                result TEXT NOT NULL,
                details TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                compliance_frameworks TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                tenant_id TEXT,
                creator_id TEXT,
                geographic_location TEXT,
                integrity_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp);
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_actor_id ON audit_events(actor_id);
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource_id ON audit_events(resource_id);
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type);
        """)
        
        conn.commit()
        return conn

    def _initialize_compliance_rules(self):
        """Initialize compliance framework rules."""
        # SOX (Sarbanes-Oxley) rules
        self.compliance_rules[ComplianceFramework.SOX] = [
            ComplianceRule(
                rule_id="SOX_404",
                framework=ComplianceFramework.SOX,
                requirement_id="Section 404",
                description="Internal control over financial reporting",
                mandatory_fields=["timestamp", "actor_id", "operation", "result"],
                retention_requirements={"financial_data": 2555},  # 7 years
                access_restrictions=["auditor", "cfo", "compliance_officer"],
                reporting_frequency="quarterly",
                alert_conditions=["failed_financial_operations", "unauthorized_access"]
            )
        ]
        
        # PCI-DSS rules
        self.compliance_rules[ComplianceFramework.PCI_DSS] = [
            ComplianceRule(
                rule_id="PCI_DSS_10",
                framework=ComplianceFramework.PCI_DSS,
                requirement_id="Requirement 10",
                description="Track and monitor all access to network resources and cardholder data",
                mandatory_fields=["timestamp", "actor_id", "resource_id", "operation", "result", "ip_address"],
                retention_requirements={"payment_data": 365},  # 1 year minimum
                access_restrictions=["qsa", "security_officer"],
                reporting_frequency="daily",
                alert_conditions=["payment_data_access", "failed_card_operations"]
            )
        ]
        
        # GDPR rules
        self.compliance_rules[ComplianceFramework.GDPR] = [
            ComplianceRule(
                rule_id="GDPR_ART_30",
                framework=ComplianceFramework.GDPR,
                requirement_id="Article 30",
                description="Records of processing activities",
                mandatory_fields=["timestamp", "actor_id", "operation", "result", "data_subject_id"],
                retention_requirements={"personal_data": 2190},  # 6 years
                access_restrictions=["dpo", "data_controller"],
                reporting_frequency="monthly",
                alert_conditions=["personal_data_breach", "unauthorized_processing"]
            )
        ]

    def _initialize_default_policies(self):
        """Initialize default audit policies."""
        # Standard enterprise policy
        self.audit_policies["enterprise_standard"] = AuditPolicy(
            policy_name="enterprise_standard",
            event_types=[
                AuditEventType.KEY_CREATED,
                AuditEventType.KEY_ACCESSED,
                AuditEventType.KEY_DELETED,
                AuditEventType.ENCRYPTION_OPERATION,
                AuditEventType.AUTHENTICATION,
                AuditEventType.SECURITY_INCIDENT
            ],
            audit_level=AuditLevel.STANDARD,
            retention_days=2555,  # 7 years
            encryption_required=True,
            real_time_alerts=True,
            compliance_frameworks=[ComplianceFramework.SOX, ComplianceFramework.ISO_27001],
            include_sensitive_data=False,
            geographical_restrictions=[],
            export_formats=["json", "csv"],
            storage_locations=["sqlite", "filesystem"]
        )
        
        # High-security policy for financial data
        self.audit_policies["financial_high_security"] = AuditPolicy(
            policy_name="financial_high_security",
            event_types=list(AuditEventType),  # All events
            audit_level=AuditLevel.COMPREHENSIVE,
            retention_days=2555,  # 7 years
            encryption_required=True,
            real_time_alerts=True,
            compliance_frameworks=[ComplianceFramework.SOX, ComplianceFramework.PCI_DSS],
            include_sensitive_data=False,  # Never include sensitive data
            geographical_restrictions=["US", "EU"],
            export_formats=["json"],
            storage_locations=["sqlite", "filesystem"]
        )
        
        # Creator-focused policy
        self.audit_policies["creator_privacy"] = AuditPolicy(
            policy_name="creator_privacy",
            event_types=[
                AuditEventType.KEY_CREATED,
                AuditEventType.KEY_ACCESSED,
                AuditEventType.ENCRYPTION_OPERATION,
                AuditEventType.AUTHENTICATION
            ],
            audit_level=AuditLevel.DETAILED,
            retention_days=1095,  # 3 years
            encryption_required=True,
            real_time_alerts=False,  # Respect creator privacy
            compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CCPA],
            include_sensitive_data=False,
            geographical_restrictions=[],
            export_formats=["json"],
            storage_locations=["filesystem"]
        )

    async def start_logging(self):
        """Start the audit logging system."""
        if self.running:
            return
        
        self.running = True
        self.logger_thread = threading.Thread(target=self._logging_loop, daemon=True)
        self.logger_thread.start()
        
        self.logger.info("Key Audit Logger started")

    def _logging_loop(self):
        """Main logging loop running in separate thread."""
        batch = []
        last_flush = time.time()
        flush_interval = self.config.get("flush_interval_seconds", 60)
        batch_size = self.config.get("batch_size", 100)
        
        while self.running:
            try:
                # Get event from queue with timeout
                try:
                    event = self.event_queue.get(timeout=1)
                    batch.append(event)
                except queue.Empty:
                    pass
                
                # Flush batch if conditions are met
                current_time = time.time()
                if (len(batch) >= batch_size or 
                    (batch and current_time - last_flush >= flush_interval)):
                    
                    self._flush_batch(batch)
                    batch.clear()
                    last_flush = current_time
                
            except Exception as e:
                self.logger.error(f"Audit logging error: {e}")
                time.sleep(1)
        
        # Flush remaining events on shutdown
        if batch:
            self._flush_batch(batch)

    def _flush_batch(self, events: List[AuditEvent]):
        """Flush a batch of events to storage."""
        try:
            # Store in SQLite
            if "sqlite" in self.storage_backends:
                self._store_events_sqlite(events)
            
            # Store in filesystem
            if "filesystem" in self.storage_backends:
                self._store_events_filesystem(events)
            
            # Check for alerts
            self._check_alert_conditions(events)
            
        except Exception as e:
            self.logger.error(f"Batch flush failed: {e}")

    def _store_events_sqlite(self, events: List[AuditEvent]):
        """Store events in SQLite database."""
        conn = self.storage_backends["sqlite"]
        
        for event in events:
            conn.execute("""
                INSERT INTO audit_events (
                    event_id, event_type, timestamp, actor_id, actor_type,
                    resource_id, resource_type, operation, result, details,
                    risk_level, compliance_frameworks, ip_address, user_agent,
                    session_id, tenant_id, creator_id, geographic_location,
                    integrity_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.event_type.value,
                event.timestamp.isoformat(),
                event.actor_id,
                event.actor_type,
                event.resource_id,
                event.resource_type,
                event.operation,
                event.result,
                json.dumps(event.details),
                event.risk_level,
                json.dumps([cf.value for cf in event.compliance_frameworks]),
                event.ip_address,
                event.user_agent,
                event.session_id,
                event.tenant_id,
                event.creator_id,
                event.geographic_location,
                event.integrity_hash
            ))
        
        conn.commit()

    def _store_events_filesystem(self, events: List[AuditEvent]):
        """Store events in filesystem with rotation."""
        log_dir = self.storage_backends["filesystem"]
        
        # Create daily log file
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = log_dir / f"audit_{today}.jsonl"
        
        # Prepare log entries
        log_entries = []
        for event in events:
            log_entry = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "actor_id": event.actor_id,
                "actor_type": event.actor_type,
                "resource_id": event.resource_id,
                "resource_type": event.resource_type,
                "operation": event.operation,
                "result": event.result,
                "details": event.details,
                "risk_level": event.risk_level,
                "compliance_frameworks": [cf.value for cf in event.compliance_frameworks],
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "session_id": event.session_id,
                "tenant_id": event.tenant_id,
                "creator_id": event.creator_id,
                "geographic_location": event.geographic_location,
                "integrity_hash": event.integrity_hash
            }
            log_entries.append(json.dumps(log_entry))
        
        # Write to file (with optional compression)
        content = "\n".join(log_entries) + "\n"
        
        if self.config.get("enable_compression", True):
            content = gzip.compress(content.encode('utf-8'))
            log_file = log_file.with_suffix('.jsonl.gz')
            mode = 'ab'
        else:
            content = content.encode('utf-8')
            mode = 'ab'
        
        with open(log_file, mode) as f:
            f.write(content)

    def _check_alert_conditions(self, events: List[AuditEvent]):
        """Check for alert conditions in event batch."""
        alert_thresholds = self.config.get("alert_thresholds", {})
        
        # Count events by risk level
        risk_counts = {}
        for event in events:
            risk_counts[event.risk_level] = risk_counts.get(event.risk_level, 0) + 1
        
        # Critical events trigger immediate alerts
        if risk_counts.get("critical", 0) >= alert_thresholds.get("critical_events_immediate", 1):
            self._trigger_alert("critical_events", {
                "count": risk_counts["critical"],
                "events": [e.event_id for e in events if e.risk_level == "critical"]
            })
        
        # High risk events
        if risk_counts.get("high", 0) >= alert_thresholds.get("high_risk_events_per_hour", 5):
            self._trigger_alert("high_risk_events", {
                "count": risk_counts["high"],
                "timeframe": "1_hour"
            })

    def _trigger_alert(self, alert_type: str, alert_data: Dict[str, Any]):
        """Trigger security alert."""
        alert = {
            "alert_id": f"alert_{secrets.token_hex(8)}",
            "alert_type": alert_type,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": "high" if alert_type == "critical_events" else "medium",
            "data": alert_data
        }
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
        
        self.logger.warning(f"Security alert triggered: {alert_type}")

    async def log_event(self,
                       event_type: AuditEventType,
                       actor_id: str,
                       actor_type: str,
                       resource_id: str,
                       resource_type: str,
                       operation: str,
                       result: str,
                       details: Dict[str, Any],
                       risk_level: str = "medium",
                       policy_name: str = "enterprise_standard",
                       **additional_fields) -> str:
        """
        Log an audit event.
        
        Args:
            event_type: Type of audit event
            actor_id: ID of the actor performing the operation
            actor_type: Type of actor (user, system, service)
            resource_id: ID of the resource being accessed
            resource_type: Type of resource
            operation: Operation being performed
            result: Result of the operation (success, failure, partial)
            details: Additional details about the event
            risk_level: Risk level (low, medium, high, critical)
            policy_name: Audit policy to apply
            **additional_fields: Additional fields (ip_address, session_id, etc.)
            
        Returns:
            Event ID
        """
        try:
            # Get audit policy
            policy = self.audit_policies.get(policy_name, self.audit_policies["enterprise_standard"])
            
            # Check if this event type should be logged
            if event_type not in policy.event_types:
                return ""
            
            # Generate event ID
            event_id = f"audit_{event_type.value}_{secrets.token_hex(12)}"
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                actor_id=actor_id,
                actor_type=actor_type,
                resource_id=resource_id,
                resource_type=resource_type,
                operation=operation,
                result=result,
                details=details,
                risk_level=risk_level,
                compliance_frameworks=policy.compliance_frameworks,
                ip_address=additional_fields.get("ip_address"),
                user_agent=additional_fields.get("user_agent"),
                session_id=additional_fields.get("session_id"),
                tenant_id=additional_fields.get("tenant_id"),
                creator_id=additional_fields.get("creator_id"),
                geographic_location=additional_fields.get("geographic_location")
            )
            
            # Calculate integrity hash
            event.integrity_hash = self._calculate_integrity_hash(event)
            
            # Add to queue
            try:
                self.event_queue.put_nowait(event)
            except queue.Full:
                self.logger.warning("Audit event queue full, dropping event")
                return ""
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            return ""

    def _calculate_integrity_hash(self, event: AuditEvent) -> str:
        """Calculate integrity hash for tamper detection."""
        # Create deterministic string representation
        hash_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "actor_id": event.actor_id,
            "resource_id": event.resource_id,
            "operation": event.operation,
            "result": event.result,
            "details": event.details
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    async def query_audit_logs(self, query: AuditQuery) -> List[Dict[str, Any]]:
        """
        Query audit logs with filtering and pagination.
        
        Args:
            query: Audit query parameters
            
        Returns:
            List of matching audit events
        """
        try:
            if "sqlite" not in self.storage_backends:
                raise ValueError("SQLite backend required for queries")
            
            conn = self.storage_backends["sqlite"]
            
            # Build SQL query
            sql_parts = ["SELECT * FROM audit_events WHERE 1=1"]
            params = []
            
            # Date range filter
            sql_parts.append("AND timestamp >= ? AND timestamp <= ?")
            params.extend([query.start_date.isoformat(), query.end_date.isoformat()])
            
            # Optional filters
            if query.event_types:
                placeholders = ",".join(["?"] * len(query.event_types))
                sql_parts.append(f"AND event_type IN ({placeholders})")
                params.extend([et.value for et in query.event_types])
            
            if query.actor_id:
                sql_parts.append("AND actor_id = ?")
                params.append(query.actor_id)
            
            if query.resource_id:
                sql_parts.append("AND resource_id = ?")
                params.append(query.resource_id)
            
            if query.risk_level:
                sql_parts.append("AND risk_level = ?")
                params.append(query.risk_level)
            
            # Compliance framework filter
            if query.compliance_framework:
                sql_parts.append("AND compliance_frameworks LIKE ?")
                params.append(f"%{query.compliance_framework.value}%")
            
            # Order and pagination
            sql_parts.append("ORDER BY timestamp DESC")
            sql_parts.append("LIMIT ? OFFSET ?")
            params.extend([query.limit, query.offset])
            
            sql = " ".join(sql_parts)
            
            # Execute query
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert to dictionaries
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in rows:
                event_dict = dict(zip(columns, row))
                
                # Parse JSON fields
                event_dict["details"] = json.loads(event_dict["details"])
                event_dict["compliance_frameworks"] = json.loads(event_dict["compliance_frameworks"])
                
                results.append(event_dict)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Audit log query failed: {e}")
            raise

    async def generate_compliance_report(self,
                                        framework: ComplianceFramework,
                                        start_date: datetime,
                                        end_date: datetime,
                                        format: str = "json") -> Dict[str, Any]:
        """
        Generate compliance report for specific framework.
        
        Args:
            framework: Compliance framework
            start_date: Report start date
            end_date: Report end date
            format: Output format (json, csv, xml)
            
        Returns:
            Compliance report data
        """
        try:
            # Get compliance rules for framework
            rules = self.compliance_rules.get(framework, [])
            
            # Query events for the timeframe
            query = AuditQuery(
                query_id=f"compliance_{framework.value}_{secrets.token_hex(8)}",
                requester_id="system",
                start_date=start_date,
                end_date=end_date,
                compliance_framework=framework,
                limit=10000  # Large limit for reports
            )
            
            events = await self.query_audit_logs(query)
            
            # Analyze events against compliance rules
            compliance_analysis = {}
            
            for rule in rules:
                rule_analysis = {
                    "rule_id": rule.rule_id,
                    "requirement_id": rule.requirement_id,
                    "description": rule.description,
                    "events_count": 0,
                    "compliant_events": 0,
                    "non_compliant_events": 0,
                    "compliance_percentage": 0.0,
                    "issues": []
                }
                
                # Check events against rule
                for event in events:
                    if self._event_matches_rule(event, rule):
                        rule_analysis["events_count"] += 1
                        
                        if self._event_compliant_with_rule(event, rule):
                            rule_analysis["compliant_events"] += 1
                        else:
                            rule_analysis["non_compliant_events"] += 1
                            rule_analysis["issues"].append({
                                "event_id": event["event_id"],
                                "timestamp": event["timestamp"],
                                "issue": "Missing mandatory fields or policy violation"
                            })
                
                # Calculate compliance percentage
                if rule_analysis["events_count"] > 0:
                    rule_analysis["compliance_percentage"] = (
                        rule_analysis["compliant_events"] / rule_analysis["events_count"] * 100
                    )
                
                compliance_analysis[rule.rule_id] = rule_analysis
            
            # Create comprehensive report
            report = {
                "report_id": f"compliance_report_{framework.value}_{secrets.token_hex(8)}",
                "framework": framework.value,
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "generated_at": datetime.utcnow().isoformat(),
                "total_events": len(events),
                "compliance_rules_analyzed": len(rules),
                "overall_compliance_score": self._calculate_overall_compliance_score(compliance_analysis),
                "rule_analysis": compliance_analysis,
                "summary": {
                    "compliant_rules": len([r for r in compliance_analysis.values() if r["compliance_percentage"] >= 95]),
                    "non_compliant_rules": len([r for r in compliance_analysis.values() if r["compliance_percentage"] < 95]),
                    "total_issues": sum(len(r["issues"]) for r in compliance_analysis.values())
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Compliance report generation failed: {e}")
            raise

    def _event_matches_rule(self, event: Dict[str, Any], rule: ComplianceRule) -> bool:
        """Check if event matches compliance rule scope."""
        # Simple matching - in production would have more sophisticated logic
        return True

    def _event_compliant_with_rule(self, event: Dict[str, Any], rule: ComplianceRule) -> bool:
        """Check if event is compliant with rule requirements."""
        # Check mandatory fields
        for field in rule.mandatory_fields:
            if field not in event or not event[field]:
                return False
        
        return True

    def _calculate_overall_compliance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall compliance score."""
        if not analysis:
            return 0.0
        
        scores = [rule["compliance_percentage"] for rule in analysis.values()]
        return sum(scores) / len(scores)

    async def verify_audit_integrity(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Verify integrity of audit logs in date range.
        
        Args:
            start_date: Start date for verification
            end_date: End date for verification
            
        Returns:
            Integrity verification results
        """
        try:
            query = AuditQuery(
                query_id=f"integrity_check_{secrets.token_hex(8)}",
                requester_id="system",
                start_date=start_date,
                end_date=end_date,
                limit=10000
            )
            
            events = await self.query_audit_logs(query)
            
            verification_results = {
                "verification_id": f"integrity_{secrets.token_hex(8)}",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_events": len(events),
                "verified_events": 0,
                "corrupted_events": 0,
                "missing_hashes": 0,
                "corrupted_event_ids": [],
                "verification_timestamp": datetime.utcnow().isoformat()
            }
            
            for event in events:
                if not event.get("integrity_hash"):
                    verification_results["missing_hashes"] += 1
                    continue
                
                # Reconstruct event for hash verification
                event_data = AuditEvent(
                    event_id=event["event_id"],
                    event_type=AuditEventType(event["event_type"]),
                    timestamp=datetime.fromisoformat(event["timestamp"]),
                    actor_id=event["actor_id"],
                    actor_type=event["actor_type"],
                    resource_id=event["resource_id"],
                    resource_type=event["resource_type"],
                    operation=event["operation"],
                    result=event["result"],
                    details=event["details"],
                    risk_level=event["risk_level"],
                    compliance_frameworks=[]  # Not needed for hash verification
                )
                
                calculated_hash = self._calculate_integrity_hash(event_data)
                
                if calculated_hash == event["integrity_hash"]:
                    verification_results["verified_events"] += 1
                else:
                    verification_results["corrupted_events"] += 1
                    verification_results["corrupted_event_ids"].append(event["event_id"])
            
            verification_results["integrity_percentage"] = (
                verification_results["verified_events"] / max(verification_results["total_events"], 1) * 100
            )
            
            return verification_results
            
        except Exception as e:
            self.logger.error(f"Audit integrity verification failed: {e}")
            raise

    def register_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback function for security alerts."""
        self.alert_callbacks.append(callback)

    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit logging statistics."""
        try:
            if "sqlite" not in self.storage_backends:
                return {"error": "SQLite backend not available"}
            
            conn = self.storage_backends["sqlite"]
            
            # Total events
            cursor = conn.execute("SELECT COUNT(*) FROM audit_events")
            total_events = cursor.fetchone()[0]
            
            # Events by type
            cursor = conn.execute("SELECT event_type, COUNT(*) FROM audit_events GROUP BY event_type")
            events_by_type = dict(cursor.fetchall())
            
            # Events by risk level
            cursor = conn.execute("SELECT risk_level, COUNT(*) FROM audit_events GROUP BY risk_level")
            events_by_risk = dict(cursor.fetchall())
            
            # Recent activity (last 24 hours)
            yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
            cursor = conn.execute("SELECT COUNT(*) FROM audit_events WHERE timestamp >= ?", (yesterday,))
            recent_events = cursor.fetchone()[0]
            
            return {
                "audit_logger_status": "operational",
                "total_events": total_events,
                "events_last_24h": recent_events,
                "events_by_type": events_by_type,
                "events_by_risk_level": events_by_risk,
                "active_policies": len(self.audit_policies),
                "compliance_frameworks": len(self.compliance_rules),
                "queue_size": self.event_queue.qsize(),
                "storage_backends": list(self.storage_backends.keys()),
                "logging_active": self.running,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get audit statistics: {e}")
            raise

    async def cleanup(self):
        """Cleanup audit logger resources."""
        try:
            # Stop logging thread
            self.running = False
            if self.logger_thread and self.logger_thread.is_alive():
                self.logger_thread.join(timeout=10)
            
            # Close database connections
            if "sqlite" in self.storage_backends:
                self.storage_backends["sqlite"].close()
            
            # Clear queues
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("Key Audit Logger cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Audit logger cleanup failed: {e}")


# Creator Economy Integration Functions
async def setup_creator_audit_monitoring(creator_id: str,
                                        creator_type: str,
                                        privacy_level: str,
                                        audit_logger: KeyAuditLogger) -> str:
    """Setup audit monitoring for creator with privacy controls."""
    # Create privacy-aware audit policy
    policy_name = f"creator_{creator_id}_privacy"
    
    if privacy_level == "high":
        event_types = [
            AuditEventType.KEY_CREATED,
            AuditEventType.AUTHENTICATION,
            AuditEventType.SECURITY_INCIDENT
        ]
        audit_level = AuditLevel.MINIMAL
    elif privacy_level == "medium":
        event_types = [
            AuditEventType.KEY_CREATED,
            AuditEventType.KEY_ACCESSED,
            AuditEventType.AUTHENTICATION,
            AuditEventType.ENCRYPTION_OPERATION
        ]
        audit_level = AuditLevel.STANDARD
    else:  # low privacy
        event_types = [
            AuditEventType.KEY_CREATED,
            AuditEventType.KEY_ACCESSED,
            AuditEventType.KEY_MODIFIED,
            AuditEventType.AUTHENTICATION,
            AuditEventType.ENCRYPTION_OPERATION,
            AuditEventType.DECRYPTION_OPERATION
        ]
        audit_level = AuditLevel.DETAILED
    
    creator_policy = AuditPolicy(
        policy_name=policy_name,
        event_types=event_types,
        audit_level=audit_level,
        retention_days=1095,  # 3 years
        encryption_required=True,
        real_time_alerts=privacy_level != "high",
        compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.CCPA],
        include_sensitive_data=False,
        geographical_restrictions=[],
        export_formats=["json"],
        storage_locations=["filesystem"]
    )
    
    audit_logger.audit_policies[policy_name] = creator_policy
    
    return policy_name


# Export main classes and functions
__all__ = [
    "KeyAuditLogger",
    "AuditEventType",
    "AuditLevel",
    "ComplianceFramework",
    "AuditEvent",
    "AuditPolicy",
    "AuditQuery",
    "setup_creator_audit_monitoring"
]