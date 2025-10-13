# -*- coding: utf-8 -*-
"""
iaCherie Platform - Enterprise Security Audit Logger
Comprehensive security event logging and audit trail system
Author: iaCherie Team
Version: 2.0.0
Date: 2024
"""

import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
import uuid
import os

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class AuditEventType(Enum):
    """Types of audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_VIOLATION = "security_violation"
    ADMIN_ACTION = "admin_action"
    API_CALL = "api_call"
    SYSTEM_EVENT = "system_event"
    ERROR = "error"
    WARNING = "warning"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditStatus(Enum):
    """Audit event status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    ERROR = "error"

@dataclass
class AuditEvent:
    """Audit event structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: AuditEventType = AuditEventType.SYSTEM_EVENT
    severity: AuditSeverity = AuditSeverity.LOW
    status: AuditStatus = AuditStatus.SUCCESS
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: int = 0
    compliance_tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate hash for integrity verification"""
        self.hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate SHA-256 hash of event data"""
        try:
            # Create a copy without the hash field
            data = asdict(self)
            data.pop('hash', None)  # Remove hash if it exists
            
            # Sort keys for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(sorted_data.encode()).hexdigest()
        except Exception:
            return ""

@dataclass
class AuditFilter:
    """Filter criteria for audit queries"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[List[AuditEventType]] = None
    severities: Optional[List[AuditSeverity]] = None
    user_ids: Optional[List[str]] = None
    resources: Optional[List[str]] = None
    status: Optional[AuditStatus] = None
    correlation_id: Optional[str] = None
    min_risk_score: Optional[int] = None
    compliance_tags: Optional[List[str]] = None

class AuditLogger:
    """Enterprise Security Audit Logger"""
    
    def __init__(self, storage_path: str = "/tmp/iacherie_audit_logs"):
        """Initialize audit logger"""
        self.events: List[AuditEvent] = []
        self.storage_path = storage_path
        self.max_memory_events = 10000
        self.auto_flush_threshold = 1000
        self._lock = threading.RLock()
        self._event_counter = 0
        
        # Risk scoring weights
        self.risk_weights = {
            AuditEventType.AUTHENTICATION: 5,
            AuditEventType.AUTHORIZATION: 7,
            AuditEventType.SECURITY_VIOLATION: 10,
            AuditEventType.ADMIN_ACTION: 8,
            AuditEventType.DATA_ACCESS: 6,
            AuditEventType.CONFIGURATION_CHANGE: 9,
            AuditEventType.API_CALL: 3,
            AuditEventType.SYSTEM_EVENT: 2,
            AuditEventType.ERROR: 4,
            AuditEventType.WARNING: 2
        }
        
        # Compliance mappings
        self.compliance_mappings = {
            "gdpr": [AuditEventType.DATA_ACCESS, AuditEventType.CONFIGURATION_CHANGE],
            "hipaa": [AuditEventType.DATA_ACCESS, AuditEventType.AUTHENTICATION],
            "pci_dss": [AuditEventType.AUTHENTICATION, AuditEventType.DATA_ACCESS, AuditEventType.ADMIN_ACTION],
            "sox": [AuditEventType.CONFIGURATION_CHANGE, AuditEventType.ADMIN_ACTION],
            "iso27001": [AuditEventType.SECURITY_VIOLATION, AuditEventType.AUTHENTICATION, AuditEventType.AUTHORIZATION]
        }
        
        # Initialize storage
        self._ensure_storage_directory()
        
        logger.info("🔍 Audit Logger initialized successfully")
    
    def _ensure_storage_directory(self):
        """Ensure audit log storage directory exists"""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            logger.info(f"📁 Audit storage directory: {self.storage_path}")
        except Exception as e:
            logger.error(f"❌ Error creating audit storage directory: {str(e)}")
    
    def log_event(self, event_type: AuditEventType, description: str, 
                  user_id: Optional[str] = None, resource: Optional[str] = None,
                  action: Optional[str] = None, status: AuditStatus = AuditStatus.SUCCESS,
                  details: Optional[Dict[str, Any]] = None, 
                  correlation_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  source_ip: Optional[str] = None,
                  user_agent: Optional[str] = None) -> str:
        """Log an audit event"""
        try:
            with self._lock:
                # Create audit event
                event = AuditEvent(
                    event_type=event_type,
                    description=description,
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    status=status,
                    details=details or {},
                    correlation_id=correlation_id,
                    session_id=session_id,
                    source_ip=source_ip,
                    user_agent=user_agent
                )
                
                # Calculate risk score and severity
                event.risk_score = self._calculate_risk_score(event)
                event.severity = self._determine_severity(event)
                
                # Add compliance tags
                event.compliance_tags = self._get_compliance_tags(event)
                
                # Regenerate hash after all fields are set
                event.hash = event._generate_hash()
                
                # Store event
                self.events.append(event)
                self._event_counter += 1
                
                # Auto-flush if threshold reached
                if len(self.events) >= self.auto_flush_threshold:
                    self._flush_to_storage()
                
                # Log based on severity
                if event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                    logger.warning(f"⚠️ {event.severity.value.upper()} audit event: {description}")
                else:
                    logger.info(f"📝 Audit: {event_type.value} - {description}")
                
                return event.id
                
        except Exception as e:
            logger.error(f"❌ Error logging audit event: {str(e)}")
            return ""
    
    def _calculate_risk_score(self, event: AuditEvent) -> int:
        """Calculate risk score for event"""
        try:
            base_score = self.risk_weights.get(event.event_type, 1)
            
            # Adjust based on status
            if event.status == AuditStatus.FAILURE:
                base_score += 3
            elif event.status == AuditStatus.ERROR:
                base_score += 2
            
            # Adjust based on details
            if event.details:
                if event.details.get("privileged_operation"):
                    base_score += 2
                if event.details.get("external_access"):
                    base_score += 2
                if event.details.get("sensitive_data"):
                    base_score += 3
                if event.details.get("admin_rights"):
                    base_score += 2
            
            return min(base_score, 10)  # Cap at 10
            
        except Exception:
            return 1
    
    def _determine_severity(self, event: AuditEvent) -> AuditSeverity:
        """Determine event severity based on risk score"""
        if event.risk_score >= 8:
            return AuditSeverity.CRITICAL
        elif event.risk_score >= 6:
            return AuditSeverity.HIGH
        elif event.risk_score >= 3:
            return AuditSeverity.MEDIUM
        else:
            return AuditSeverity.LOW
    
    def _get_compliance_tags(self, event: AuditEvent) -> List[str]:
        """Get compliance tags for event type"""
        tags = []
        for compliance, event_types in self.compliance_mappings.items():
            if event.event_type in event_types:
                tags.append(compliance)
        return tags
    
    def log_authentication(self, user_id: str, success: bool, method: str = "password",
                          source_ip: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> str:
        """Log authentication event"""
        status = AuditStatus.SUCCESS if success else AuditStatus.FAILURE
        description = f"User authentication {'successful' if success else 'failed'} using {method}"
        
        auth_details = {
            "method": method,
            "success": success,
            **(details or {})
        }
        
        return self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            description=description,
            user_id=user_id,
            status=status,
            details=auth_details,
            source_ip=source_ip
        )
    
    def log_authorization(self, user_id: str, resource: str, action: str, granted: bool,
                         policy_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> str:
        """Log authorization event"""
        status = AuditStatus.SUCCESS if granted else AuditStatus.FAILURE
        description = f"Access {'granted' if granted else 'denied'} to {resource}:{action}"
        
        auth_details = {
            "granted": granted,
            "policy_id": policy_id,
            **(details or {})
        }
        
        return self.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            description=description,
            user_id=user_id,
            resource=resource,
            action=action,
            status=status,
            details=auth_details
        )
    
    def _flush_to_storage(self):
        """Flush events to persistent storage"""
        try:
            if not self.events:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_log_{timestamp}_{self._event_counter}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            # Prepare events for JSON serialization
            events_data = []
            for event in self.events:
                event_dict = asdict(event)
                # Convert datetime to ISO string
                event_dict['timestamp'] = event.timestamp.isoformat()
                events_data.append(event_dict)
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(events_data, f, indent=2)
            
            logger.info(f"💾 Flushed {len(self.events)} audit events to {filename}")
            
            # Clear memory events (keep recent ones)
            if len(self.events) > self.max_memory_events:
                self.events = self.events[-1000:]  # Keep last 1000
            
        except Exception as e:
            logger.error(f"❌ Error flushing audit events to storage: {str(e)}")
    
    def query_events(self, filter_criteria: AuditFilter, limit: int = 1000) -> List[AuditEvent]:
        """Query audit events with filtering"""
        try:
            with self._lock:
                filtered_events = self.events.copy()
                
                # Apply filters
                if filter_criteria.start_time:
                    filtered_events = [e for e in filtered_events if e.timestamp >= filter_criteria.start_time]
                
                if filter_criteria.end_time:
                    filtered_events = [e for e in filtered_events if e.timestamp <= filter_criteria.end_time]
                
                if filter_criteria.event_types:
                    filtered_events = [e for e in filtered_events if e.event_type in filter_criteria.event_types]
                
                if filter_criteria.severities:
                    filtered_events = [e for e in filtered_events if e.severity in filter_criteria.severities]
                
                if filter_criteria.user_ids:
                    filtered_events = [e for e in filtered_events if e.user_id in filter_criteria.user_ids]
                
                # Sort by timestamp (newest first) and limit
                filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
                return filtered_events[:limit]
                
        except Exception as e:
            logger.error(f"❌ Error querying audit events: {str(e)}")
            return []

# Create global instance
audit_logger = AuditLogger()

# Export main classes and instance
__all__ = [
    'AuditLogger',
    'AuditEvent',
    'AuditFilter',
    'AuditEventType',
    'AuditSeverity',
    'AuditStatus',
    'audit_logger'
]