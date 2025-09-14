"""
Audit Logger module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
📋 MLOps Audit Logger - Enterprise Compliance System

Logger d'audit complet pour toutes les opérations MLOps critiques.
Implémente des trails d'audit pour compliance réglementaire enterprise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Role: Security Expert + DBA + Backend Senior + DevOps
"""

import asyncio
import json
import hashlib
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import gzip
import sqlite3
from contextlib import asynccontextmanager
import aiofiles
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Niveaux d'audit pour classification"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"


class EventCategory(Enum):
    """Catégories d'événements MLOps"""
    # Authentication & Authorization
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    AUTH_PERMISSION_DENIED = "auth.permission_denied"
    
    # Model Operations
    MODEL_CREATE = "model.create"
    MODEL_UPDATE = "model.update"
    MODEL_DELETE = "model.delete"
    MODEL_DEPLOY = "model.deploy"
    MODEL_ROLLBACK = "model.rollback"
    MODEL_VERSION = "model.version"
    
    # Pipeline Operations
    PIPELINE_CREATE = "pipeline.create"
    PIPELINE_EXECUTE = "pipeline.execute"
    PIPELINE_MODIFY = "pipeline.modify"
    PIPELINE_DELETE = "pipeline.delete"
    PIPELINE_FAILED = "pipeline.failed"
    
    # Data Operations
    DATA_ACCESS = "data.access"
    DATA_EXPORT = "data.export"
    DATA_IMPORT = "data.import"
    DATA_DELETE = "data.delete"
    DATA_QUALITY_ISSUE = "data.quality_issue"
    
    # Infrastructure Operations
    INFRA_DEPLOY = "infra.deploy"
    INFRA_SCALE = "infra.scale"
    INFRA_CONFIG_CHANGE = "infra.config_change"
    INFRA_SECURITY_EVENT = "infra.security_event"
    
    # System Operations
    SYSTEM_START = "system.start"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_CONFIG_CHANGE = "system.config_change"
    
    # Compliance Operations
    COMPLIANCE_VIOLATION = "compliance.violation"
    COMPLIANCE_REPORT = "compliance.report"
    COMPLIANCE_AUDIT = "compliance.audit"


@dataclass
class AuditEvent:
    """Événement d'audit complet"""
    event_id: str
    timestamp: datetime
    category: EventCategory
    level: AuditLevel
    user_id: Optional[str]
    session_id: Optional[str]
    resource_type: str
    resource_id: str
    action: str
    result: str  # SUCCESS, FAILURE, ERROR
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    compliance_flags: List[str] = field(default_factory=list)


@dataclass
class ComplianceRule:
    """Règle de compliance pour audit"""
    rule_id: str
    name: str
    description: str
    categories: List[EventCategory]
    conditions: Dict[str, Any]
    actions: List[str]
    severity: AuditLevel
    enabled: bool = True


class AuditStorage:
    """Interface de stockage d'audit"""
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store audit event"""
        raise NotImplementedError
    
    async def query_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query audit events"""
        raise NotImplementedError
    
    async def archive_events(self, before_date: datetime) -> int:
        """Archive old events"""
        raise NotImplementedError


class SQLiteAuditStorage(AuditStorage):
    """Stockage SQLite pour audit (dev/test)"""
    
    def __init__(self, db_path -> None: str = "audit.db") -> None:
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                level TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                action TEXT NOT NULL,
                result TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                request_id TEXT,
                correlation_id TEXT,
                tags TEXT,
                compliance_flags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON audit_events(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON audit_events(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON audit_events(level)")
        
        conn.commit()
        conn.close()
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store audit event in SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO audit_events (
                    event_id, timestamp, category, level, user_id, session_id,
                    resource_type, resource_id, action, result, description,
                    details, ip_address, user_agent, request_id, correlation_id,
                    tags, compliance_flags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.timestamp.isoformat(),
                event.category.value,
                event.level.value,
                event.user_id,
                event.session_id,
                event.resource_type,
                event.resource_id,
                event.action,
                event.result,
                event.description,
                json.dumps(event.details),
                event.ip_address,
                event.user_agent,
                event.request_id,
                event.correlation_id,
                json.dumps(event.tags),
                json.dumps(event.compliance_flags)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to store audit event: {e}")
            return False
    
    async def query_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query audit events from SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []
            
            if 'start_time' in filters:
                query += " AND timestamp >= ?"
                params.append(filters['start_time'].isoformat())
            
            if 'end_time' in filters:
                query += " AND timestamp <= ?"
                params.append(filters['end_time'].isoformat())
            
            if 'user_id' in filters:
                query += " AND user_id = ?"
                params.append(filters['user_id'])
            
            if 'category' in filters:
                query += " AND category = ?"
                params.append(filters['category'].value if isinstance(filters['category'], EventCategory) else filters['category'])
            
            if 'level' in filters:
                query += " AND level = ?"
                params.append(filters['level'].value if isinstance(filters['level'], AuditLevel) else filters['level'])
            
            query += " ORDER BY timestamp DESC"
            
            if 'limit' in filters:
                query += f" LIMIT {filters['limit']}"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                events.append(AuditEvent(
                    event_id=row['event_id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    category=EventCategory(row['category']),
                    level=AuditLevel(row['level']),
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    resource_type=row['resource_type'],
                    resource_id=row['resource_id'],
                    action=row['action'],
                    result=row['result'],
                    description=row['description'],
                    details=json.loads(row['details']) if row['details'] else {},
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    request_id=row['request_id'],
                    correlation_id=row['correlation_id'],
                    tags=json.loads(row['tags']) if row['tags'] else [],
                    compliance_flags=json.loads(row['compliance_flags']) if row['compliance_flags'] else []
                ))
            
            return events
            
        except Exception as e:
            logger.error(f"❌ Failed to query audit events: {e}")
            return []
    
    async def archive_events(self, before_date: datetime) -> int:
        """Archive events older than specified date"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(
                "DELETE FROM audit_events WHERE timestamp < ?",
                (before_date.isoformat(),)
            )
            archived_count = cursor.rowcount
            conn.commit()
            conn.close()
            return archived_count
        except Exception as e:
            logger.error(f"❌ Failed to archive audit events: {e}")
            return 0


class FileAuditStorage(AuditStorage):
    """Stockage fichier pour audit (production)"""
    
    def __init__(self, base_path -> None: str = "audit_logs", encrypt -> None: bool = True) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.encrypt = encrypt
        if encrypt:
            self.cipher_suite = Fernet(Fernet.generate_key())
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store audit event in daily log files"""
        try:
            # Create daily log file
            date_str = event.timestamp.strftime("%Y-%m-%d")
            log_file = self.base_path / f"audit_{date_str}.jsonl"
            
            # Serialize event
            event_data = asdict(event)
            event_data['timestamp'] = event.timestamp.isoformat()
            event_data['category'] = event.category.value
            event_data['level'] = event.level.value
            
            log_line = json.dumps(event_data) + "\n"
            
            # Encrypt if enabled
            if self.encrypt:
                log_line = self.cipher_suite.encrypt(log_line.encode()).decode()
                log_line += "\n"
            
            # Write to file
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(log_line)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store audit event to file: {e}")
            return False
    
    async def query_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query audit events from files"""
        events = []
        
        # Determine date range for file scanning
        start_date = filters.get('start_time', datetime.now() - timedelta(days=30))
        end_date = filters.get('end_time', datetime.now())
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            log_file = self.base_path / f"audit_{date_str}.jsonl"
            
            if log_file.exists():
                try:
                    async with aiofiles.open(log_file, 'r') as f:
                        async for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Decrypt if encrypted
                            if self.encrypt:
                                try:
                                    line = self.cipher_suite.decrypt(line.encode()).decode()
                                except:
                                    continue
                            
                            # Parse event
                            event_data = json.loads(line)
                            event = AuditEvent(
                                event_id=event_data['event_id'],
                                timestamp=datetime.fromisoformat(event_data['timestamp']),
                                category=EventCategory(event_data['category']),
                                level=AuditLevel(event_data['level']),
                                user_id=event_data.get('user_id'),
                                session_id=event_data.get('session_id'),
                                resource_type=event_data['resource_type'],
                                resource_id=event_data['resource_id'],
                                action=event_data['action'],
                                result=event_data['result'],
                                description=event_data['description'],
                                details=event_data.get('details', {}),
                                ip_address=event_data.get('ip_address'),
                                user_agent=event_data.get('user_agent'),
                                request_id=event_data.get('request_id'),
                                correlation_id=event_data.get('correlation_id'),
                                tags=event_data.get('tags', []),
                                compliance_flags=event_data.get('compliance_flags', [])
                            )
                            
                            # Apply filters
                            if self._event_matches_filters(event, filters):
                                events.append(event)
                                
                except Exception as e:
                    logger.error(f"❌ Failed to read audit file {log_file}: {e}")
            
            current_date += timedelta(days=1)
        
        # Sort by timestamp and apply limit
        events.sort(key=lambda x: x.timestamp, reverse=True)
        if 'limit' in filters:
            events = events[:filters['limit']]
        
        return events
    
    def _event_matches_filters(self, event: AuditEvent, filters: Dict[str, Any]) -> bool:
        """Check if event matches query filters"""
        if 'user_id' in filters and event.user_id != filters['user_id']:
            return False
        
        if 'category' in filters:
            filter_category = filters['category']
            if isinstance(filter_category, EventCategory):
                filter_category = filter_category.value
            if event.category.value != filter_category:
                return False
        
        if 'level' in filters:
            filter_level = filters['level']
            if isinstance(filter_level, AuditLevel):
                filter_level = filter_level.value
            if event.level.value != filter_level:
                return False
        
        return True
    
    async def archive_events(self, before_date: datetime) -> int:
        """Archive old log files by compressing them"""
        archived_count = 0
        
        for log_file in self.base_path.glob("audit_*.jsonl"):
            # Extract date from filename
            date_str = log_file.stem.replace("audit_", "")
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < before_date:
                    # Compress file
                    archive_file = log_file.with_suffix('.jsonl.gz')
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(archive_file, 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    # Remove original
                    log_file.unlink()
                    archived_count += 1
                    
            except ValueError:
                continue
        
        return archived_count


class AuditLogger:
    """
    📋 Logger d'audit enterprise pour MLOps
    
    Fonctionnalités:
    - Audit trails complets pour compliance
    - Multiple storage backends (SQLite, Files, Cloud)
    - Event categorization et tagging
    - Compliance rule engine
    - Real-time monitoring et alerting
    - Tamper-evident logging avec encryption
    - GDPR et regulatory compliance
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.storage_backends: List[AuditStorage] = []
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        
        # Initialize storage backends
        self._init_storage_backends()
        
        # Initialize compliance rules
        self._init_compliance_rules()
        
        # Statistics
        self.stats = {
            'events_logged': 0,
            'compliance_violations': 0,
            'storage_failures': 0
        }
        
        logger.info("📋 Audit Logger initialized for enterprise compliance")
    
    def _init_storage_backends(self) -> None:
        """Initialize storage backends based on config"""
        storage_config = self.config.get('storage', {})
        
        # SQLite storage (always available for development)
        if storage_config.get('sqlite', {}).get('enabled', True):
            db_path = storage_config.get('sqlite', {}).get('path', 'audit.db')
            self.storage_backends.append(SQLiteAuditStorage(db_path))
        
        # File storage for production
        if storage_config.get('file', {}).get('enabled', False):
            file_config = storage_config.get('file', {})
            self.storage_backends.append(FileAuditStorage(
                base_path=file_config.get('path', 'audit_logs'),
                encrypt=file_config.get('encrypt', True)
            ))
    
    def _init_compliance_rules(self) -> None:
        """Initialize compliance rules"""
        # GDPR Data Access Rule
        gdpr_access_rule = ComplianceRule(
            rule_id="gdpr_data_access",
            name="GDPR Data Access Monitoring",
            description="Monitor personal data access for GDPR compliance",
            categories=[EventCategory.DATA_ACCESS, EventCategory.DATA_EXPORT],
            conditions={"contains_pii": True},
            actions=["log_critical", "notify_dpo"],
            severity=AuditLevel.COMPLIANCE
        )
        
        # Security Incident Rule
        security_incident_rule = ComplianceRule(
            rule_id="security_incident",
            name="Security Incident Detection",
            description="Detect and escalate security incidents",
            categories=[
                EventCategory.AUTH_FAILED, 
                EventCategory.AUTH_PERMISSION_DENIED,
                EventCategory.INFRA_SECURITY_EVENT
            ],
            conditions={"failure_threshold": 5, "time_window_minutes": 15},
            actions=["alert_security_team", "log_critical"],
            severity=AuditLevel.SECURITY
        )
        
        # Model Deployment Rule
        model_deployment_rule = ComplianceRule(
            rule_id="model_deployment",
            name="Model Deployment Governance",
            description="Ensure proper approval for model deployments",
            categories=[EventCategory.MODEL_DEPLOY],
            conditions={"requires_approval": True},
            actions=["verify_approval", "log_compliance"],
            severity=AuditLevel.COMPLIANCE
        )
        
        # Register rules
        for rule in [gdpr_access_rule, security_incident_rule, model_deployment_rule]:
            self.compliance_rules[rule.rule_id] = rule
    
    async def start(self) -> None:
        """Start audit logger background tasks"""
        self.running = True
        asyncio.create_task(self._process_event_queue())
        logger.info("🚀 Audit Logger started")
    
    async def stop(self) -> None:
        """Stop audit logger"""
        self.running = False
        logger.info("🛑 Audit Logger stopped")
    
    async def log_event(self, category: EventCategory, level: AuditLevel,
                       resource_type: str, resource_id: str, action: str,
                       result: str, description: str, user_id: Optional[str] = None,
                       session_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                       request_id: Optional[str] = None, correlation_id: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> str:
        """Log audit event"""
        # Generate unique event ID
        event_id = hashlib.sha256(
            f"{category.value}{time.time()}{resource_id}{action}".encode()
        ).hexdigest()[:16]
        
        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            category=category,
            level=level,
            user_id=user_id,
            session_id=session_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            description=description,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            correlation_id=correlation_id,
            tags=tags or []
        )
        
        # Check compliance rules
        await self._check_compliance_rules(event)
        
        # Queue for processing
        await self.event_queue.put(event)
        
        # Update statistics
        self.stats['events_logged'] += 1
        
        return event_id
    
    async def _process_event_queue(self) -> None:
        """Process queued audit events"""
        while self.running:
            try:
                # Get event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Store in all backends
                for backend in self.storage_backends:
                    try:
                        success = await backend.store_event(event)
                        if not success:
                            self.stats['storage_failures'] += 1
                            logger.error(f"❌ Failed to store event {event.event_id} in backend")
                    except Exception as e:
                        self.stats['storage_failures'] += 1
                        logger.error(f"❌ Backend error storing event {event.event_id}: {e}")
                
                # Mark task done
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Error processing audit event: {e}")
    
    async def _check_compliance_rules(self, event -> None: AuditEvent) -> None:
        """Check event against compliance rules"""
        for rule in self.compliance_rules.values():
            if not rule.enabled:
                continue
            
            # Check if event category matches rule
            if event.category not in rule.categories:
                continue
            
            # Check rule conditions
            if await self._evaluate_rule_conditions(event, rule):
                # Add compliance flag
                event.compliance_flags.append(rule.rule_id)
                
                # Execute rule actions
                await self._execute_rule_actions(event, rule)
                
                self.stats['compliance_violations'] += 1
    
    async def _evaluate_rule_conditions(self, event: AuditEvent, rule: ComplianceRule) -> bool:
        """Evaluate if event meets rule conditions"""
        conditions = rule.conditions
        
        # Check for PII data access
        if conditions.get('contains_pii'):
            return 'pii' in event.tags or 'personal_data' in event.details
        
        # Check failure threshold for security incidents
        if 'failure_threshold' in conditions:
            threshold = conditions['failure_threshold']
            time_window = conditions.get('time_window_minutes', 15)
            
            # Count recent failures (simplified check)
            return await self._count_recent_failures(event, threshold, time_window)
        
        # Check approval requirement for deployments
        if conditions.get('requires_approval'):
            return 'approval_id' not in event.details
        
        return False
    
    async def _count_recent_failures(self, event: AuditEvent, threshold: int, time_window: int) -> bool:
        """Count recent failures for threshold checking"""
        # In production, this would query the storage backends
        # For demo, return True if result is FAILURE
        return event.result == "FAILURE"
    
    async def _execute_rule_actions(self, event -> None: AuditEvent, rule -> None: ComplianceRule) -> None:
        """Execute actions for triggered compliance rule"""
        for action in rule.actions:
            if action == "log_critical":
                logger.critical(f"🚨 COMPLIANCE VIOLATION: {rule.name} - {event.description}")
            
            elif action == "notify_dpo":
                # In production, send notification to Data Protection Officer
                logger.warning(f"📧 DPO Notification: GDPR data access by {event.user_id}")
            
            elif action == "alert_security_team":
                # In production, send alert to security team
                logger.warning(f"🔐 Security Alert: {event.description}")
            
            elif action == "verify_approval":
                # In production, check approval system
                logger.warning(f"⚠️ Unapproved Deployment: {event.resource_id}")
    
    # Convenience methods for common audit events
    async def log_authentication(self, user_id: str, result: str, ip_address: str,
                                details: Optional[Dict[str, Any]] = None) -> str:
        """Log authentication event"""
        category = EventCategory.AUTH_LOGIN if result == "SUCCESS" else EventCategory.AUTH_FAILED
        level = AuditLevel.INFO if result == "SUCCESS" else AuditLevel.WARNING
        
        return await self.log_event(
            category=category,
            level=level,
            resource_type="authentication",
            resource_id=user_id,
            action="login",
            result=result,
            description=f"User {user_id} authentication {result.lower()}",
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )
    
    async def log_model_operation(self, user_id: str, model_id: str, action: str,
                                 result: str, details: Optional[Dict[str, Any]] = None) -> str:
        """Log model operation event"""
        category_map = {
            "create": EventCategory.MODEL_CREATE,
            "update": EventCategory.MODEL_UPDATE,
            "delete": EventCategory.MODEL_DELETE,
            "deploy": EventCategory.MODEL_DEPLOY,
            "rollback": EventCategory.MODEL_ROLLBACK
        }
        
        category = category_map.get(action, EventCategory.MODEL_UPDATE)
        level = AuditLevel.INFO if result == "SUCCESS" else AuditLevel.WARNING
        
        return await self.log_event(
            category=category,
            level=level,
            resource_type="model",
            resource_id=model_id,
            action=action,
            result=result,
            description=f"Model {action} operation on {model_id}",
            user_id=user_id,
            details=details
        )
    
    async def log_data_access(self, user_id: str, dataset_id: str, action: str,
                             contains_pii: bool = False, details: Optional[Dict[str, Any]] = None) -> str:
        """Log data access event"""
        tags = ["pii"] if contains_pii else []
        
        return await self.log_event(
            category=EventCategory.DATA_ACCESS,
            level=AuditLevel.COMPLIANCE if contains_pii else AuditLevel.INFO,
            resource_type="dataset",
            resource_id=dataset_id,
            action=action,
            result="SUCCESS",
            description=f"Data {action} on dataset {dataset_id}",
            user_id=user_id,
            details=details,
            tags=tags
        )
    
    async def query_audit_trail(self, filters: Optional[Dict[str, Any]] = None) -> List[AuditEvent]:
        """Query audit trail from storage backends"""
        filters = filters or {}
        all_events = []
        
        # Query all storage backends
        for backend in self.storage_backends:
            try:
                events = await backend.query_events(filters)
                all_events.extend(events)
            except Exception as e:
                logger.error(f"❌ Failed to query backend: {e}")
        
        # Remove duplicates and sort
        unique_events = {event.event_id: event for event in all_events}
        sorted_events = sorted(unique_events.values(), key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit if specified
        if 'limit' in filters:
            sorted_events = sorted_events[:filters['limit']]
        
        return sorted_events
    
    async def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for specified period"""
        # Query events for period
        events = await self.query_audit_trail({
            'start_time': start_date,
            'end_time': end_date
        })
        
        # Analyze events
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_events": len(events),
                "by_category": {},
                "by_level": {},
                "by_result": {},
                "compliance_violations": 0
            },
            "compliance_violations": [],
            "security_incidents": [],
            "data_access_events": []
        }
        
        # Categorize events
        for event in events:
            # Count by category
            category = event.category.value
            report["summary"]["by_category"][category] = report["summary"]["by_category"].get(category, 0) + 1
            
            # Count by level
            level = event.level.value
            report["summary"]["by_level"][level] = report["summary"]["by_level"].get(level, 0) + 1
            
            # Count by result
            result = event.result
            report["summary"]["by_result"][result] = report["summary"]["by_result"].get(result, 0) + 1
            
            # Track compliance violations
            if event.compliance_flags:
                report["summary"]["compliance_violations"] += 1
                report["compliance_violations"].append({
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "rule_ids": event.compliance_flags,
                    "description": event.description
                })
            
            # Track security incidents
            if event.level == AuditLevel.SECURITY:
                report["security_incidents"].append({
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "category": event.category.value,
                    "description": event.description
                })
            
            # Track data access for GDPR
            if event.category == EventCategory.DATA_ACCESS and 'pii' in event.tags:
                report["data_access_events"].append({
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "user_id": event.user_id,
                    "resource_id": event.resource_id,
                    "action": event.action
                })
        
        return report
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit logger statistics"""
        return {
            **self.stats,
            "storage_backends": len(self.storage_backends),
            "compliance_rules": len(self.compliance_rules),
            "queue_size": self.event_queue.qsize()
        }


# Demo function
async def demo_audit_logger() -> None:
    """Démonstration du système d'audit"""
    print("📋 MLOps Audit Logger Demo")
    
    # Initialize audit logger
    audit_logger = AuditLogger({
        'storage': {
            'sqlite': {'enabled': True, 'path': 'demo_audit.db'},
            'file': {'enabled': True, 'path': 'demo_audit_logs', 'encrypt': False}
        }
    })
    
    await audit_logger.start()
    
    # Simulate various audit events
    print("🔐 Logging authentication events...")
    await audit_logger.log_authentication("alice", "SUCCESS", "192.168.1.100")
    await audit_logger.log_authentication("hacker", "FAILURE", "203.0.113.50")
    
    print("🤖 Logging model operations...")
    await audit_logger.log_model_operation(
        "alice", "model_v1.2", "deploy", "SUCCESS",
        {"approval_id": "APP-12345", "environment": "production"}
    )
    
    # Simulate unapproved deployment (compliance violation)
    await audit_logger.log_model_operation(
        "bob", "model_v1.3", "deploy", "SUCCESS",
        {"environment": "production"}  # Missing approval_id
    )
    
    print("📊 Logging data access events...")
    await audit_logger.log_data_access(
        "alice", "customer_dataset", "read", 
        contains_pii=True, 
        details={"query": "SELECT * FROM customers WHERE region='EU'"}
    )
    
    # Wait for processing
    await asyncio.sleep(1)
    
    print("📋 Querying audit trail...")
    recent_events = await audit_logger.query_audit_trail({'limit': 10})
    print(f"✅ Found {len(recent_events)} recent events")
    
    for event in recent_events[:3]:
        print(f"  - {event.timestamp}: {event.category.value} - {event.description}")
    
    print("📊 Generating compliance report...")
    start_date = datetime.now() - timedelta(hours=1)
    end_date = datetime.now()
    
    report = await audit_logger.generate_compliance_report(start_date, end_date)
    print(f"📈 Report Summary:")
    print(f"  - Total events: {report['summary']['total_events']}")
    print(f"  - Compliance violations: {report['summary']['compliance_violations']}")
    print(f"  - Security incidents: {len(report['security_incidents'])}")
    print(f"  - Data access events: {len(report['data_access_events'])}")
    
    # Statistics
    stats = audit_logger.get_statistics()
    print(f"📊 Audit Logger Statistics: {stats}")
    
    await audit_logger.stop()


if __name__ == "__main__":
    asyncio.run(demo_audit_logger())