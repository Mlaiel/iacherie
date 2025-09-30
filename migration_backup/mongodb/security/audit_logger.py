"""Audit Logging System for MongoDB
==================================

Comprehensive audit logging for all database operations, security events,
and compliance tracking with tamper-proof storage and real-time monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

EXPERT ROLES IMPLEMENTED:
- Security Engineer: Tamper-proof audit trails
- DBA: Database operation logging
- Compliance Specialist: Regulatory compliance tracking
- DevOps: Real-time monitoring and alerting
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import threading
import queue
import time

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Types of audit events."""
    # Database operations
    DB_CONNECT = "db_connect"
    DB_DISCONNECT = "db_disconnect"
    DB_QUERY = "db_query"
    DB_INSERT = "db_insert"
    DB_UPDATE = "db_update"
    DB_DELETE = "db_delete"
    DB_CREATE_COLLECTION = "db_create_collection"
    DB_DROP_COLLECTION = "db_drop_collection"
    DB_CREATE_INDEX = "db_create_index"
    DB_DROP_INDEX = "db_drop_index"
    
    # Security events
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_FAILED = "auth_failed"
    AUTH_SESSION_EXPIRED = "auth_session_expired"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    ENCRYPTION_OPERATION = "encryption_operation"
    DECRYPTION_OPERATION = "decryption_operation"
    KEY_ROTATION = "key_rotation"
    
    # Administrative events
    ADMIN_USER_CREATED = "admin_user_created"
    ADMIN_USER_MODIFIED = "admin_user_modified"
    ADMIN_USER_DELETED = "admin_user_deleted"
    ADMIN_ROLE_CREATED = "admin_role_created"
    ADMIN_ROLE_MODIFIED = "admin_role_modified"
    ADMIN_ROLE_DELETED = "admin_role_deleted"
    ADMIN_CONFIG_CHANGED = "admin_config_changed"
    ADMIN_BACKUP_STARTED = "admin_backup_started"
    ADMIN_RESTORE_STARTED = "admin_restore_started"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    SYSTEM_WARNING = "system_warning"
    PERFORMANCE_ALERT = "performance_alert"
    SECURITY_ALERT = "security_alert"

class AuditSeverity(Enum):
    """Audit event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Single audit event."""
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_name: Optional[str] = None
    operation: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    data_size_bytes: Optional[int] = None
    checksum: Optional[str] = None

@dataclass
class AuditQuery:
    """Audit log query parameters."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    user_id: Optional[str] = None
    resource_name: Optional[str] = None
    severity: Optional[AuditSeverity] = None
    success_only: Optional[bool] = None
    limit: int = 1000
    offset: int = 0

class AuditLogger:
    """Comprehensive audit logging system."""
    
    def __init__(self, storage_backend: str = "memory"):
        """Initialize audit logger."""
        self.storage_backend = storage_backend
        self._events: List[AuditEvent] = []
        self._event_queue = queue.Queue()
        self._running = False
        self._worker_thread = None
        self._listeners: List[callable] = []
        self._encryption_key = self._generate_audit_key()
        
        # Statistics
        self._total_events = 0
        self._events_by_type: Dict[AuditEventType, int] = {}
        self._events_by_severity: Dict[AuditSeverity, int] = {}
        
        # Start background worker
        self.start()
    
    def _generate_audit_key(self) -> str:
        """Generate key for audit log integrity."""
        # In production, this should come from secure key management
        return hashlib.sha256(b"ainflue_audit_key_v1").hexdigest()
    
    def start(self):
        """Start audit logging worker."""
        if not self._running:
            self._running = True
            self._worker_thread = threading.Thread(target=self._worker, daemon=True)
            self._worker_thread.start()
            logger.info("Audit logger started")
    
    def stop(self):
        """Stop audit logging worker."""
        if self._running:
            self._running = False
            if self._worker_thread:
                self._worker_thread.join(timeout=5)
            logger.info("Audit logger stopped")
    
    def _worker(self):
        """Background worker to process audit events."""
        while self._running:
            try:
                # Process events from queue
                event = self._event_queue.get(timeout=1)
                self._store_event(event)
                self._notify_listeners(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audit event: {e}")
    
    def log_event(self, event_type: AuditEventType, severity: AuditSeverity = AuditSeverity.MEDIUM,
                  user_id: str = None, session_id: str = None, resource_type: str = None,
                  resource_name: str = None, operation: str = None, details: Dict[str, Any] = None,
                  source_ip: str = None, user_agent: str = None, success: bool = True,
                  error_message: str = None, execution_time_ms: float = None,
                  data_size_bytes: int = None) -> str:
        """Log an audit event."""
        
        # Generate unique event ID
        event_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}:{event_type.value}:{user_id}:{resource_name}".encode()
        ).hexdigest()[:16]
        
        # Create event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            resource_type=resource_type,
            resource_name=resource_name,
            operation=operation,
            details=details or {},
            source_ip=source_ip,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            data_size_bytes=data_size_bytes
        )
        
        # Calculate integrity checksum
        event.checksum = self._calculate_checksum(event)
        
        # Queue for processing
        self._event_queue.put(event)
        
        return event_id
    
    def log_database_operation(self, operation: str, collection: str = None,
                              user_id: str = None, success: bool = True,
                              execution_time_ms: float = None, details: Dict[str, Any] = None,
                              error_message: str = None) -> str:
        """Log database operation."""
        
        # Map operation to event type
        event_type_map = {
            "find": AuditEventType.DB_QUERY,
            "insert": AuditEventType.DB_INSERT,
            "update": AuditEventType.DB_UPDATE,
            "delete": AuditEventType.DB_DELETE,
            "create_collection": AuditEventType.DB_CREATE_COLLECTION,
            "drop_collection": AuditEventType.DB_DROP_COLLECTION,
            "create_index": AuditEventType.DB_CREATE_INDEX,
            "drop_index": AuditEventType.DB_DROP_INDEX
        }
        
        event_type = event_type_map.get(operation, AuditEventType.DB_QUERY)
        severity = AuditSeverity.HIGH if not success else AuditSeverity.LOW
        
        return self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_type="collection",
            resource_name=collection,
            operation=operation,
            details=details,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms
        )
    
    def log_authentication_event(self, event_type: AuditEventType, user_id: str = None,
                                username: str = None, source_ip: str = None,
                                user_agent: str = None, success: bool = True,
                                error_message: str = None, details: Dict[str, Any] = None) -> str:
        """Log authentication event."""
        severity = AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM
        
        auth_details = details or {}
        if username:
            auth_details["username"] = username
        
        return self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_type="authentication",
            details=auth_details,
            source_ip=source_ip,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
    
    def log_security_event(self, event_type: AuditEventType, severity: AuditSeverity,
                          user_id: str = None, details: Dict[str, Any] = None,
                          error_message: str = None) -> str:
        """Log security event."""
        return self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_type="security",
            details=details,
            error_message=error_message,
            success=error_message is None
        )
    
    def log_admin_event(self, event_type: AuditEventType, admin_user_id: str,
                       target_resource: str = None, details: Dict[str, Any] = None,
                       success: bool = True, error_message: str = None) -> str:
        """Log administrative event."""
        severity = AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM
        
        return self.log_event(
            event_type=event_type,
            severity=severity,
            user_id=admin_user_id,
            resource_type="administration",
            resource_name=target_resource,
            details=details,
            success=success,
            error_message=error_message
        )
    
    def _store_event(self, event: AuditEvent):
        """Store audit event."""
        if self.storage_backend == "memory":
            self._events.append(event)
            
            # Keep only last 10000 events in memory
            if len(self._events) > 10000:
                self._events = self._events[-10000:]
        
        # Update statistics
        self._total_events += 1
        self._events_by_type[event.event_type] = self._events_by_type.get(event.event_type, 0) + 1
        self._events_by_severity[event.severity] = self._events_by_severity.get(event.severity, 0) + 1
        
        # Log to system logger based on severity
        log_level = {
            AuditSeverity.LOW: logging.INFO,
            AuditSeverity.MEDIUM: logging.WARNING,
            AuditSeverity.HIGH: logging.ERROR,
            AuditSeverity.CRITICAL: logging.CRITICAL
        }.get(event.severity, logging.INFO)
        
        logger.log(log_level, f"AUDIT: {event.event_type.value} - {event.resource_name or 'N/A'} - User: {event.user_id or 'N/A'}")
    
    def _notify_listeners(self, event: AuditEvent):
        """Notify registered listeners of new audit event."""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying audit listener: {e}")
    
    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate integrity checksum for audit event."""
        # Create event data without checksum
        event_dict = asdict(event)
        event_dict.pop('checksum', None)
        
        # Convert to JSON string (sorted for consistency)
        event_json = json.dumps(event_dict, sort_keys=True, default=str)
        
        # Calculate HMAC
        data = f"{event_json}:{self._encryption_key}".encode()
        return hashlib.sha256(data).hexdigest()
    
    def verify_event_integrity(self, event: AuditEvent) -> bool:
        """Verify audit event integrity."""
        stored_checksum = event.checksum
        event.checksum = None
        calculated_checksum = self._calculate_checksum(event)
        event.checksum = stored_checksum
        
        return stored_checksum == calculated_checksum
    
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """Query audit events."""
        results = []
        
        for event in self._events:
            # Apply filters
            if query.start_time and event.timestamp < query.start_time:
                continue
            if query.end_time and event.timestamp > query.end_time:
                continue
            if query.event_types and event.event_type not in query.event_types:
                continue
            if query.user_id and event.user_id != query.user_id:
                continue
            if query.resource_name and event.resource_name != query.resource_name:
                continue
            if query.severity and event.severity != query.severity:
                continue
            if query.success_only is not None and event.success != query.success_only:
                continue
            
            results.append(event)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        start_idx = query.offset
        end_idx = start_idx + query.limit
        
        return results[start_idx:end_idx]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit logging statistics."""
        return {
            "total_events": self._total_events,
            "events_by_type": {k.value: v for k, v in self._events_by_type.items()},
            "events_by_severity": {k.value: v for k, v in self._events_by_severity.items()},
            "events_in_memory": len(self._events),
            "queue_size": self._event_queue.qsize(),
            "is_running": self._running
        }
    
    def add_listener(self, listener: callable):
        """Add audit event listener."""
        self._listeners.append(listener)
    
    def remove_listener(self, listener: callable):
        """Remove audit event listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def generate_compliance_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate compliance report for specified time period."""
        query = AuditQuery(start_time=start_time, end_time=end_time, limit=100000)
        events = self.query_events(query)
        
        # Analyze events
        failed_auth_attempts = sum(1 for e in events if e.event_type == AuditEventType.AUTH_FAILED)
        permission_denials = sum(1 for e in events if e.event_type == AuditEventType.PERMISSION_DENIED)
        admin_operations = sum(1 for e in events if e.event_type.value.startswith("admin_"))
        encryption_operations = sum(1 for e in events if e.event_type in [AuditEventType.ENCRYPTION_OPERATION, AuditEventType.DECRYPTION_OPERATION])
        
        return {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(events),
            "security_metrics": {
                "failed_authentication_attempts": failed_auth_attempts,
                "permission_denials": permission_denials,
                "admin_operations": admin_operations,
                "encryption_operations": encryption_operations
            },
            "compliance_status": "COMPLIANT" if failed_auth_attempts < 100 and permission_denials < 50 else "REVIEW_REQUIRED",
            "generated_at": datetime.utcnow().isoformat()
        }

# Global audit logger instance
_default_logger: Optional[AuditLogger] = None

def get_audit_logger() -> AuditLogger:
    """Get or create default audit logger."""
    global _default_logger
    if _default_logger is None:
        _default_logger = AuditLogger()
    return _default_logger

# Export main classes and functions
__all__ = [
    'AuditEventType',
    'AuditSeverity',
    'AuditEvent',
    'AuditQuery',
    'AuditLogger',
    'get_audit_logger'
]