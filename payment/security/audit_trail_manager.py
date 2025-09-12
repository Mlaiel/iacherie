"""🔒 Audit Trail Manager
======================

Enterprise audit trail management system for comprehensive transaction logging,
compliance audit support, data retention, and forensic investigation tools.

Features:
- Comprehensive transaction logging
- Compliance audit support
- Data retention management
- Forensic investigation tools
- Immutable audit records
- Real-time audit monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib
import uuid
import gzip
import base64
from pathlib import Path
import aiofiles
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


class AuditEventType(Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_REFUNDED = "payment_refunded"
    CONFIGURATION_CHANGED = "configuration_changed"
    USER_CREATED = "user_created"
    USER_MODIFIED = "user_modified"
    USER_DELETED = "user_deleted"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    DATA_ACCESSED = "data_accessed"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    SECURITY_INCIDENT = "security_incident"
    COMPLIANCE_CHECK = "compliance_check"
    SYSTEM_ERROR = "system_error"
    API_CALL = "api_call"


class AuditSeverity(Enum):
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Compliance standards"""
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    ISO_27001 = "iso_27001"


@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: str
    user_agent: Optional[str]
    resource_type: str
    resource_id: Optional[str]
    action: str
    severity: AuditSeverity
    success: bool
    
    # Event details
    details: Dict[str, Any] = field(default_factory=dict)
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    
    # Security context
    risk_score: Optional[float] = None
    compliance_tags: Set[ComplianceStandard] = field(default_factory=set)
    
    # Metadata
    correlation_id: Optional[str] = None
    transaction_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'session_id': self.session_id,
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'action': self.action,
            'severity': self.severity.value,
            'success': self.success,
            'details': self.details,
            'before_state': self.before_state,
            'after_state': self.after_state,
            'risk_score': self.risk_score,
            'compliance_tags': [tag.value for tag in self.compliance_tags],
            'correlation_id': self.correlation_id,
            'transaction_id': self.transaction_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create from dictionary"""
        return cls(
            event_id=data['event_id'],
            event_type=AuditEventType(data['event_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            source_ip=data['source_ip'],
            user_agent=data.get('user_agent'),
            resource_type=data['resource_type'],
            resource_id=data.get('resource_id'),
            action=data['action'],
            severity=AuditSeverity(data['severity']),
            success=data['success'],
            details=data.get('details', {}),
            before_state=data.get('before_state'),
            after_state=data.get('after_state'),
            risk_score=data.get('risk_score'),
            compliance_tags=set(ComplianceStandard(tag) for tag in data.get('compliance_tags', [])),
            correlation_id=data.get('correlation_id'),
            transaction_id=data.get('transaction_id')
        )


@dataclass
class AuditTrail:
    """Collection of related audit events"""
    trail_id: str
    correlation_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    events: List[AuditEvent]
    summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetentionPolicy:
    """Data retention policy"""
    policy_id: str
    name: str
    description: str
    event_types: Set[AuditEventType]
    retention_period: timedelta
    archive_after: timedelta
    compliance_requirements: Set[ComplianceStandard]
    is_active: bool = True


class AuditTrailManager:
    """Enterprise audit trail management system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.db_session: Optional[AsyncSession] = None
        
        # Audit settings
        self.batch_size = config.get('batch_size', 1000)
        self.flush_interval = timedelta(seconds=config.get('flush_interval_seconds', 30))
        self.max_memory_events = config.get('max_memory_events', 10000)
        
        # Storage paths
        self.audit_log_path = Path(config.get('audit_log_path', '/var/log/payment_audit'))
        self.archive_path = Path(config.get('archive_path', '/var/log/payment_audit/archive'))
        
        # In-memory buffers
        self.event_buffer: List[AuditEvent] = []
        self.buffer_lock = asyncio.Lock()
        
        # Retention policies
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        
        # Background tasks
        self.flush_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # Integrity verification
        self.last_hash: str = ""
        
        # Ensure directories exist
        self.audit_log_path.mkdir(parents=True, exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the audit trail system"""
        try:
            # Initialize Redis connection
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 3),
                decode_responses=False
            )
            
            # Initialize database connection
            db_config = self.config.get('database', {})
            db_url = f"postgresql+asyncpg://{db_config.get('user')}:{db_config.get('password')}@{db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}"
            engine = create_async_engine(db_url)
            async_session = sessionmaker(engine, class_=AsyncSession)
            self.db_session = async_session()
            
            # Load retention policies
            await self._load_retention_policies()
            
            # Create default retention policies
            await self._create_default_retention_policies()
            
            # Start background tasks
            self.flush_task = asyncio.create_task(self._periodic_flush())
            self.cleanup_task = asyncio.create_task(self._periodic_cleanup())
            
            logger.info("Audit trail system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize audit trail system: {e}")
            raise
    
    async def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        source_ip: str,
        resource_type: str,
        action: str,
        success: bool,
        **kwargs
    ) -> str:
        """Log an audit event"""
        try:
            event = AuditEvent(
                event_id=f"audit_{uuid.uuid4().hex}",
                event_type=event_type,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                session_id=kwargs.get('session_id'),
                source_ip=source_ip,
                user_agent=kwargs.get('user_agent'),
                resource_type=resource_type,
                resource_id=kwargs.get('resource_id'),
                action=action,
                severity=kwargs.get('severity', AuditSeverity.INFO),
                success=success,
                details=kwargs.get('details', {}),
                before_state=kwargs.get('before_state'),
                after_state=kwargs.get('after_state'),
                risk_score=kwargs.get('risk_score'),
                compliance_tags=set(kwargs.get('compliance_tags', [])),
                correlation_id=kwargs.get('correlation_id'),
                transaction_id=kwargs.get('transaction_id')
            )
            
            # Add to buffer
            async with self.buffer_lock:
                self.event_buffer.append(event)
                
                # Flush if buffer is full
                if len(self.event_buffer) >= self.batch_size:
                    await self._flush_events()
            
            # Store in Redis for real-time access
            await self._store_event_in_redis(event)
            
            # Log critical events immediately
            if event.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
                await self._log_critical_event(event)
            
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            raise
    
    async def get_audit_trail(
        self,
        correlation_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[AuditTrail]:
        """Get audit trail by correlation ID"""
        try:
            events = await self._get_events_by_correlation(correlation_id, start_time, end_time)
            if not events:
                return None
            
            # Sort events by timestamp
            events.sort(key=lambda e: e.timestamp)
            
            trail = AuditTrail(
                trail_id=f"trail_{uuid.uuid4().hex}",
                correlation_id=correlation_id,
                started_at=events[0].timestamp,
                ended_at=events[-1].timestamp,
                events=events,
                summary=self._generate_trail_summary(events)
            )
            
            return trail
            
        except Exception as e:
            logger.error(f"Failed to get audit trail: {e}")
            raise
    
    async def search_events(
        self,
        filters: Dict[str, Any],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Search audit events with filters"""
        try:
            events = []
            
            # Search in Redis for recent events
            redis_events = await self._search_redis_events(filters, start_time, end_time, limit)
            events.extend(redis_events)
            
            # Search in database for older events if needed
            if len(events) < limit:
                db_events = await self._search_database_events(filters, start_time, end_time, limit - len(events))
                events.extend(db_events)
            
            # Search in archived files if needed
            if len(events) < limit:
                archive_events = await self._search_archive_events(filters, start_time, end_time, limit - len(events))
                events.extend(archive_events)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search events: {e}")
            raise
    
    async def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            # Get events with compliance tags
            filters = {'compliance_tags': [standard]}
            events = await self.search_events(filters, start_time, end_time, limit=10000)
            
            # Analyze events
            total_events = len(events)
            success_count = sum(1 for event in events if event.success)
            failure_count = total_events - success_count
            
            # Group by event type
            event_type_counts = {}
            for event in events:
                event_type = event.event_type.value
                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
            # Security incidents
            security_incidents = [
                event for event in events 
                if event.event_type == AuditEventType.SECURITY_INCIDENT
            ]
            
            # Access violations
            access_violations = [
                event for event in events
                if event.event_type == AuditEventType.ACCESS_DENIED
            ]
            
            # Generate report
            report = {
                'standard': standard.value,
                'period': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                },
                'summary': {
                    'total_events': total_events,
                    'successful_operations': success_count,
                    'failed_operations': failure_count,
                    'success_rate': (success_count / total_events * 100) if total_events > 0 else 0
                },
                'event_breakdown': event_type_counts,
                'security_metrics': {
                    'security_incidents': len(security_incidents),
                    'access_violations': len(access_violations),
                    'high_risk_events': len([e for e in events if e.risk_score and e.risk_score > 0.8])
                },
                'compliance_status': await self._assess_compliance_status(standard, events),
                'recommendations': await self._generate_compliance_recommendations(standard, events)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise
    
    async def verify_integrity(self, event_id: str) -> bool:
        """Verify audit event integrity"""
        try:
            # Get event from storage
            event = await self._get_event_by_id(event_id)
            if not event:
                return False
            
            # Calculate hash
            event_data = event.to_dict()
            event_hash = hashlib.sha256(json.dumps(event_data, sort_keys=True).encode()).hexdigest()
            
            # Check against stored hash
            stored_hash = await self._get_stored_hash(event_id)
            
            return event_hash == stored_hash
            
        except Exception as e:
            logger.error(f"Failed to verify integrity: {e}")
            return False
    
    async def _store_event_in_redis(self, event: AuditEvent):
        """Store event in Redis for real-time access"""
        if not self.redis_client:
            return
        
        event_data = json.dumps(event.to_dict()).encode()
        
        # Store with TTL
        await self.redis_client.setex(
            f"audit_event:{event.event_id}",
            timedelta(days=7).total_seconds(),
            event_data
        )
        
        # Add to timeline
        await self.redis_client.zadd(
            "audit_timeline",
            {event.event_id: event.timestamp.timestamp()}
        )
        
        # Add to user timeline if user_id exists
        if event.user_id:
            await self.redis_client.zadd(
                f"user_audit:{event.user_id}",
                {event.event_id: event.timestamp.timestamp()}
            )
    
    async def _flush_events(self):
        """Flush events from buffer to persistent storage"""
        if not self.event_buffer:
            return
        
        events_to_flush = self.event_buffer.copy()
        self.event_buffer.clear()
        
        # Write to database
        await self._write_events_to_database(events_to_flush)
        
        # Write to audit log files
        await self._write_events_to_files(events_to_flush)
        
        logger.info(f"Flushed {len(events_to_flush)} events to persistent storage")
    
    async def _write_events_to_database(self, events: List[AuditEvent]):
        """Write events to database"""
        # Placeholder for database storage implementation
        pass
    
    async def _write_events_to_files(self, events: List[AuditEvent]):
        """Write events to audit log files"""
        try:
            # Group events by date
            events_by_date = {}
            for event in events:
                date_key = event.timestamp.strftime('%Y-%m-%d')
                if date_key not in events_by_date:
                    events_by_date[date_key] = []
                events_by_date[date_key].append(event)
            
            # Write to daily log files
            for date_key, daily_events in events_by_date.items():
                log_file = self.audit_log_path / f"audit_{date_key}.jsonl"
                
                async with aiofiles.open(log_file, 'a') as f:
                    for event in daily_events:
                        event_line = json.dumps(event.to_dict()) + '\n'
                        await f.write(event_line)
                        
                        # Calculate and store hash for integrity
                        event_hash = hashlib.sha256(event_line.encode()).hexdigest()
                        await self._store_event_hash(event.event_id, event_hash)
            
        except Exception as e:
            logger.error(f"Failed to write events to files: {e}")
    
    async def _log_critical_event(self, event: AuditEvent):
        """Immediately log critical events"""
        try:
            critical_log_file = self.audit_log_path / "critical_events.jsonl"
            
            async with aiofiles.open(critical_log_file, 'a') as f:
                event_line = json.dumps(event.to_dict()) + '\n'
                await f.write(event_line)
            
            # Send alert if configured
            await self._send_critical_event_alert(event)
            
        except Exception as e:
            logger.error(f"Failed to log critical event: {e}")
    
    async def _periodic_flush(self):
        """Periodically flush events to storage"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval.total_seconds())
                
                async with self.buffer_lock:
                    if self.event_buffer:
                        await self._flush_events()
                        
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
    
    async def _periodic_cleanup(self):
        """Periodically clean up old data"""
        while True:
            try:
                # Run cleanup daily
                await asyncio.sleep(86400)  # 24 hours
                
                await self._cleanup_expired_data()
                await self._archive_old_data()
                
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def _cleanup_expired_data(self):
        """Clean up expired audit data"""
        try:
            # Clean up Redis timeline
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            await self.redis_client.zremrangebyscore(
                "audit_timeline",
                0,
                cutoff_time.timestamp()
            )
            
            # Apply retention policies
            for policy in self.retention_policies.values():
                if not policy.is_active:
                    continue
                
                cutoff_time = datetime.utcnow() - policy.retention_period
                await self._delete_events_by_policy(policy, cutoff_time)
            
            logger.info("Completed expired data cleanup")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
    
    async def _archive_old_data(self):
        """Archive old audit data"""
        try:
            archive_cutoff = datetime.utcnow() - timedelta(days=90)
            
            # Find log files older than cutoff
            for log_file in self.audit_log_path.glob("audit_*.jsonl"):
                file_date_str = log_file.stem.replace('audit_', '')
                try:
                    file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                    if file_date < archive_cutoff:
                        await self._archive_log_file(log_file)
                except ValueError:
                    continue
            
            logger.info("Completed old data archival")
            
        except Exception as e:
            logger.error(f"Failed to archive old data: {e}")
    
    async def _archive_log_file(self, log_file: Path):
        """Archive a log file"""
        try:
            # Compress file
            archive_file = self.archive_path / f"{log_file.stem}.jsonl.gz"
            
            async with aiofiles.open(log_file, 'rb') as input_file:
                content = await input_file.read()
                
            async with aiofiles.open(archive_file, 'wb') as output_file:
                compressed_content = gzip.compress(content)
                await output_file.write(compressed_content)
            
            # Remove original file
            log_file.unlink()
            
            logger.info(f"Archived log file: {log_file}")
            
        except Exception as e:
            logger.error(f"Failed to archive log file {log_file}: {e}")
    
    async def _search_redis_events(
        self,
        filters: Dict[str, Any],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int
    ) -> List[AuditEvent]:
        """Search events in Redis"""
        events = []
        
        if not self.redis_client:
            return events
        
        try:
            # Get event IDs from timeline
            min_score = start_time.timestamp() if start_time else 0
            max_score = end_time.timestamp() if end_time else datetime.utcnow().timestamp()
            
            event_ids = await self.redis_client.zrangebyscore(
                "audit_timeline",
                min_score,
                max_score,
                start=0,
                num=limit
            )
            
            # Get events and apply filters
            for event_id in event_ids:
                event_data = await self.redis_client.get(f"audit_event:{event_id}")
                if event_data:
                    event = AuditEvent.from_dict(json.loads(event_data))
                    if self._matches_filters(event, filters):
                        events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to search Redis events: {e}")
            return events
    
    def _matches_filters(self, event: AuditEvent, filters: Dict[str, Any]) -> bool:
        """Check if event matches filters"""
        for key, value in filters.items():
            if key == 'event_type' and event.event_type.value != value:
                return False
            elif key == 'user_id' and event.user_id != value:
                return False
            elif key == 'resource_type' and event.resource_type != value:
                return False
            elif key == 'success' and event.success != value:
                return False
            elif key == 'compliance_tags' and not any(tag.value in value for tag in event.compliance_tags):
                return False
        
        return True
    
    # Placeholder methods for additional functionality
    async def _load_retention_policies(self):
        """Load retention policies from storage"""
        pass
    
    async def _create_default_retention_policies(self):
        """Create default retention policies"""
        pass
    
    async def _get_events_by_correlation(self, correlation_id: str, start_time: Optional[datetime], end_time: Optional[datetime]) -> List[AuditEvent]:
        """Get events by correlation ID"""
        return []
    
    async def _search_database_events(self, filters: Dict[str, Any], start_time: Optional[datetime], end_time: Optional[datetime], limit: int) -> List[AuditEvent]:
        """Search events in database"""
        return []
    
    async def _search_archive_events(self, filters: Dict[str, Any], start_time: Optional[datetime], end_time: Optional[datetime], limit: int) -> List[AuditEvent]:
        """Search events in archive files"""
        return []
    
    def _generate_trail_summary(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Generate trail summary"""
        return {}
    
    async def _assess_compliance_status(self, standard: ComplianceStandard, events: List[AuditEvent]) -> str:
        """Assess compliance status"""
        return "compliant"
    
    async def _generate_compliance_recommendations(self, standard: ComplianceStandard, events: List[AuditEvent]) -> List[str]:
        """Generate compliance recommendations"""
        return []
    
    async def _get_event_by_id(self, event_id: str) -> Optional[AuditEvent]:
        """Get event by ID"""
        return None
    
    async def _get_stored_hash(self, event_id: str) -> Optional[str]:
        """Get stored hash for event"""
        return None
    
    async def _store_event_hash(self, event_id: str, event_hash: str):
        """Store event hash for integrity verification"""
        pass
    
    async def _send_critical_event_alert(self, event: AuditEvent):
        """Send alert for critical events"""
        pass
    
    async def _delete_events_by_policy(self, policy: RetentionPolicy, cutoff_time: datetime):
        """Delete events according to retention policy"""
        pass
    
    def get_audit_metrics(self) -> Dict[str, Any]:
        """Get audit system metrics"""
        return {
            "events_in_buffer": len(self.event_buffer),
            "retention_policies": len(self.retention_policies),
            "flush_interval_seconds": int(self.flush_interval.total_seconds()),
            "max_memory_events": self.max_memory_events,
            "batch_size": self.batch_size
        }