"""Enterprise Structured Logging System

Advanced logging infrastructure with structured logs, audit trails, and security logging
for comprehensive observability in the IA Influencer content protection platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DevOps + Security

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, copying, or implementation without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""

import json
import logging
import logging.handlers
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from collections import deque, defaultdict
import hashlib


class LogLevel(Enum):
    """
Enhanced log levels for different contexts."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"
    AUDIT = "AUDIT"
    BUSINESS = "BUSINESS"
    PERFORMANCE = "PERFORMANCE"


class EventCategory(Enum):
    """Event categories for structured logging."""

    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    SECURITY_EVENT = "security_event"
    BUSINESS_EVENT = "business_event"
    PERFORMANCE_EVENT = "performance_event"
    ERROR_EVENT = "error_event"
    AUDIT_EVENT = "audit_event"
    CONTENT_EVENT = "content_event"
    AI_EVENT = "ai_event"
    PROTECTION_EVENT = "protection_event"


@dataclass
class StructuredLogEntry:
    """Structured log entry with rich metadata."""
    timestamp: datetime
    level: LogLevel
    category: EventCategory
    message: str
    service_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Dict[str, Any] = None
    tags: List[str] = None

    def to_dict(self) -> Dict:
        """
Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        data['category'] = self.category.value
        data['tags'] = self.tags or []
        data['metadata'] = self.metadata or {}
        return data

    def to_json(self) -> str:
        """
Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class StructuredLogger:
    """
Enhanced structured logger with multiple output formats."""
    
    def __init__(self, service_name: str, log_directory: str = "/var/log/ia-influencer"):
        self.service_name = service_name
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers for different purposes
        self._setup_loggers()
        
        # In-memory log buffer for real-time monitoring
        self.log_buffer = deque(maxlen=1000)
        self._lock = threading.Lock()
        
        # Performance metrics
        self.log_metrics = defaultdict(int)
        
    def _setup_loggers(self):
        """Set up different loggers for various log types."""
        
        # Main application logger
        self.app_logger = self._create_logger(
            name=f"{self.service_name}_app",
            filename=self.log_directory / "application.log",
            level=logging.INFO
        )
        
        # Error logger
        self.error_logger = self._create_logger(
            name=f"{self.service_name}_error",
            filename=self.log_directory / "errors.log",
            level=logging.ERROR
        )
        
        # Performance logger
        self.perf_logger = self._create_logger(
            name=f"{self.service_name}_performance",
            filename=self.log_directory / "performance.log",
            level=logging.INFO
        )
        
        # Business events logger
        self.business_logger = self._create_logger(
            name=f"{self.service_name}_business",
            filename=self.log_directory / "business_events.log",
            level=logging.INFO
        )
    
    def _create_logger(self, name: str, filename: Path, level: int) -> logging.Logger:
        """Create a logger with rotating file handler."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Rotating file handler (10MB per file, keep 5 files)
        handler = logging.handlers.RotatingFileHandler(
            filename=filename,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # JSON formatter for structured logs
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def log(self, 
            level: LogLevel, 
            category: EventCategory, 
            message: str,
            user_id: Optional[str] = None,
            session_id: Optional[str] = None,
            request_id: Optional[str] = None,
            correlation_id: Optional[str] = None,
            source_ip: Optional[str] = None,
            user_agent: Optional[str] = None,
            endpoint: Optional[str] = None,
            method: Optional[str] = None,
            status_code: Optional[int] = None,
            response_time_ms: Optional[float] = None,
            error_code: Optional[str] = None,
            exception: Optional[Exception] = None,
            metadata: Optional[Dict] = None,
            tags: Optional[List[str]] = None):
        """
Log a structured entry."""
        
        # Create structured log entry
        entry = StructuredLogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            category=category,
            message=message,
            service_name=self.service_name,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            correlation_id=correlation_id,
            source_ip=source_ip,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error_code=error_code,
            stack_trace=traceback.format_exc() if exception else None,
            metadata=metadata or {},
            tags=tags or []
        )
        
        # Add to buffer for real-time monitoring
        with self._lock:
            self.log_buffer.append(entry)
            self.log_metrics[level.value] += 1
            self.log_metrics[category.value] += 1
        
        # Route to appropriate logger
        json_message = entry.to_json()
        
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.error_logger.error(json_message)
        elif category == EventCategory.PERFORMANCE_EVENT:
            self.perf_logger.info(json_message)
        elif category == EventCategory.BUSINESS_EVENT:
            self.business_logger.info(json_message)
        else:
            self.app_logger.info(json_message)
    
    def debug(self, message: str, **kwargs):
        """
Log debug message."""
        self.log(LogLevel.DEBUG, EventCategory.SYSTEM_EVENT, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """
Log info message."""
        self.log(LogLevel.INFO, EventCategory.SYSTEM_EVENT, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """
Log warning message."""
        self.log(LogLevel.WARNING, EventCategory.SYSTEM_EVENT, message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """
Log error message."""
        self.log(LogLevel.ERROR, EventCategory.ERROR_EVENT, message, exception=exception, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """
Log critical message."""
        self.log(LogLevel.CRITICAL, EventCategory.ERROR_EVENT, message, exception=exception, **kwargs)
    
    def log_user_action(self, action: str, user_id: str, details: Optional[Dict] = None, **kwargs):
        """
Log user action."""
        self.log(
            LogLevel.INFO, 
            EventCategory.USER_ACTION, 
            f"User action: {action}",
            user_id=user_id,
            metadata={"action": action, "details": details or {}},
            **kwargs
        )
    
    def log_business_event(self, event: str, value: Optional[float] = None, metadata: Optional[Dict] = None, **kwargs):
        """Log business event."""
        message = f"Business event: {event}"
        if value is not None:
            message += f" (value: {value})"
        
        self.log(
            LogLevel.BUSINESS,
            EventCategory.BUSINESS_EVENT,
            message,
            metadata={"event": event, "value": value, **(metadata or {})},
            **kwargs
        )
    
    def log_performance_event(self, operation: str, duration_ms: float, success: bool = True, **kwargs):
        """Log performance event."""
        self.log(
            LogLevel.PERFORMANCE,
            EventCategory.PERFORMANCE_EVENT,
            f"Performance: {operation} took {duration_ms:.2f}ms ({'success' if success else 'failed'})",
            response_time_ms=duration_ms,
            metadata={"operation": operation, "duration_ms": duration_ms, "success": success},
            **kwargs
        )
    
    def log_content_event(self, event_type: str, content_id: str, user_id: str, metadata: Optional[Dict] = None, **kwargs):
        """Log content-related event."""
        self.log(
            LogLevel.INFO,
            EventCategory.CONTENT_EVENT,
            f"Content event: {event_type} for content {content_id}",
            user_id=user_id,
            metadata={"event_type": event_type, "content_id": content_id, **(metadata or {})},
            tags=["content", event_type],
            **kwargs
        )
    
    def log_ai_event(self, model_name: str, operation: str, duration_ms: float, success: bool = True, **kwargs):
        """Log AI processing event."""
        self.log(
            LogLevel.INFO,
            EventCategory.AI_EVENT,
            f"AI {operation}: {model_name} ({'success' if success else 'failed'}) in {duration_ms:.2f}ms",
            response_time_ms=duration_ms,
            metadata={"model": model_name, "operation": operation, "duration_ms": duration_ms, "success": success},
            tags=["ai", model_name, operation],
            **kwargs
        )
    
    def log_protection_event(self, event_type: str, content_id: str, result: str, confidence: Optional[float] = None, **kwargs):
        """Log content protection event."""
        message = f"Protection {event_type}: {result} for content {content_id}"
        if confidence:
            message += f" (confidence: {confidence:.2f})"
        
        self.log(
            LogLevel.INFO,
            EventCategory.PROTECTION_EVENT,
            message,
            metadata={
                "event_type": event_type,
                "content_id": content_id,
                "result": result,
                "confidence": confidence
            },
            tags=["protection", event_type],
            **kwargs
        )
    
    def get_recent_logs(self, count: int = 100) -> List[Dict]:
        """Get recent log entries."""
        with self._lock:
            recent_logs = list(self.log_buffer)[-count:]
            return [log.to_dict() for log in recent_logs]
    
    def get_log_metrics(self) -> Dict:
        """
Get logging metrics."""
        with self._lock:
            return {
                "total_logs": sum(self.log_metrics.values()),
                "by_level": {k: v for k, v in self.log_metrics.items() if k in LogLevel.__members__},
                "by_category": {k: v for k, v in self.log_metrics.items() if k in EventCategory.__members__},
                "buffer_size": len(self.log_buffer),
                "service_name": self.service_name
            }


class AuditLogger:
    """Specialized logger for audit trails and compliance."""
    
    def __init__(self, service_name: str, log_directory: str = "/var/log/ia-influencer/audit"):
        self.service_name = service_name
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Audit-specific logger with enhanced security
        self.audit_logger = self._setup_audit_logger()
        
        # Audit trail buffer
        self.audit_buffer = deque(maxlen=10000)
        self._lock = threading.Lock()
        
    def _setup_audit_logger(self) -> logging.Logger:
        """Set up audit logger with security features."""
        logger = logging.getLogger(f"{self.service_name}_audit")
        logger.setLevel(logging.INFO)
        
        if logger.handlers:
            return logger
        
        # Daily rotating file handler for audit logs
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_directory / "audit.log",
            when="D",  # Daily rotation
            interval=1,
            backupCount=365,  # Keep 1 year of audit logs
            encoding='utf-8'
        )
        
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_audit_event(self,
                       event_type: str,
                       user_id: Optional[str] = None,
                       resource_id: Optional[str] = None,
                       action: Optional[str] = None,
                       result: Optional[str] = None,
                       source_ip: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       session_id: Optional[str] = None,
                       metadata: Optional[Dict] = None):
        """Log audit event with comprehensive tracking."""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "user_id": user_id,
            "resource_id": resource_id,
            "action": action,
            "result": result,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "session_id": session_id,
            "metadata": metadata or {},
            "audit_id": self._generate_audit_id()
        }
        
        with self._lock:
            self.audit_buffer.append(audit_entry)
        
        # Log to file
        audit_message = json.dumps(audit_entry, ensure_ascii=False)
        self.audit_logger.info(audit_message)
    
    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        timestamp = datetime.utcnow().isoformat()
        service = self.service_name
        content = f"{timestamp}_{service}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def log_user_authentication(self, user_id: str, action: str, success: bool, source_ip: str, **kwargs):
        """Log authentication events."""
        self.log_audit_event(
            event_type="authentication",
            user_id=user_id,
            action=action,
            result="success" if success else "failure",
            source_ip=source_ip,
            **kwargs
        )
    
    def log_data_access(self, user_id: str, resource_type: str, resource_id: str, action: str, **kwargs):
        """Log data access events."""
        self.log_audit_event(
            event_type="data_access",
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            metadata={"resource_type": resource_type},
            **kwargs
        )
    
    def log_data_modification(self, user_id: str, resource_type: str, resource_id: str, changes: Dict, **kwargs):
        """Log data modification events."""
        self.log_audit_event(
            event_type="data_modification",
            user_id=user_id,
            resource_id=resource_id,
            action="modify",
            metadata={"resource_type": resource_type, "changes": changes},
            **kwargs
        )
    
    def log_permission_change(self, admin_user_id: str, target_user_id: str, permission: str, action: str, **kwargs):
        """Log permission changes."""
        self.log_audit_event(
            event_type="permission_change",
            user_id=admin_user_id,
            resource_id=target_user_id,
            action=action,
            metadata={"permission": permission, "target_user": target_user_id},
            **kwargs
        )
    
    def get_audit_trail(self, user_id: Optional[str] = None, event_type: Optional[str] = None, hours: int = 24) -> List[Dict]:
        """Get audit trail with optional filtering."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            filtered_entries = []
            
            for entry in self.audit_buffer:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time < cutoff_time:
                    continue
                    
                if user_id and entry.get("user_id") != user_id:
                    continue
                    
                if event_type and entry.get("event_type") != event_type:
                    continue
                
                filtered_entries.append(entry)
        
        return sorted(filtered_entries, key=lambda x: x["timestamp"], reverse=True)


class SecurityLogger:
    """Specialized logger for security events and threat detection."""
    
    def __init__(self, service_name: str, log_directory: str = "/var/log/ia-influencer/security"):
        self.service_name = service_name
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Security-specific logger
        self.security_logger = self._setup_security_logger()
        
        # Security events buffer
        self.security_buffer = deque(maxlen=5000)
        self._lock = threading.Lock()
        
        # Threat detection counters
        self.threat_counters = defaultdict(int)
        
    def _setup_security_logger(self) -> logging.Logger:
        """Set up security logger with enhanced monitoring."""
        logger = logging.getLogger(f"{self.service_name}_security")
        logger.setLevel(logging.WARNING)
        
        if logger.handlers:
            return logger
        
        # Security logs with hourly rotation
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_directory / "security.log",
            when="H",  # Hourly rotation
            interval=1,
            backupCount=24 * 7,  # Keep 1 week of hourly logs
            encoding='utf-8'
        )
        
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_security_event(self,
                          threat_type: str,
                          severity: str,
                          description: str,
                          source_ip: Optional[str] = None,
                          user_id: Optional[str] = None,
                          user_agent: Optional[str] = None,
                          request_details: Optional[Dict] = None,
                          action_taken: Optional[str] = None):
        """Log security event."""
        
        security_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "threat_type": threat_type,
            "severity": severity,
            "description": description,
            "source_ip": source_ip,
            "user_id": user_id,
            "user_agent": user_agent,
            "request_details": request_details or {},
            "action_taken": action_taken,
            "security_id": self._generate_security_id()
        }
        
        with self._lock:
            self.security_buffer.append(security_entry)
            self.threat_counters[threat_type] += 1
        
        # Log to file
        security_message = json.dumps(security_entry, ensure_ascii=False)
        self.security_logger.warning(security_message)
    
    def _generate_security_id(self) -> str:
        """Generate unique security event ID."""
        timestamp = datetime.utcnow().isoformat()
        content = f"security_{timestamp}_{self.service_name}"
        return hashlib.sha256(content.encode()).hexdigest()[:20]
    
    def log_failed_authentication(self, attempted_user: str, source_ip: str, failure_reason: str, **kwargs):
        """Log failed authentication attempts."""
        self.log_security_event(
            threat_type="authentication_failure",
            severity="medium",
            description=f"Failed authentication attempt for user: {attempted_user}",
            source_ip=source_ip,
            user_id=attempted_user,
            request_details={"failure_reason": failure_reason},
            **kwargs
        )
    
    def log_suspicious_activity(self, activity_type: str, source_ip: str, description: str, **kwargs):
        """Log suspicious activity."""
        self.log_security_event(
            threat_type="suspicious_activity",
            severity="high",
            description=description,
            source_ip=source_ip,
            request_details={"activity_type": activity_type},
            **kwargs
        )
    
    def log_rate_limit_exceeded(self, source_ip: str, endpoint: str, request_count: int, **kwargs):
        """Log rate limiting violations."""
        self.log_security_event(
            threat_type="rate_limit_violation",
            severity="low",
            description=f"Rate limit exceeded for endpoint {endpoint}",
            source_ip=source_ip,
            request_details={"endpoint": endpoint, "request_count": request_count},
            action_taken="requests_throttled",
            **kwargs
        )
    
    def log_data_breach_attempt(self, attack_type: str, source_ip: str, target_resource: str, **kwargs):
        """Log potential data breach attempts."""
        self.log_security_event(
            threat_type="data_breach_attempt",
            severity="critical",
            description=f"Potential data breach attempt: {attack_type}",
            source_ip=source_ip,
            request_details={"attack_type": attack_type, "target_resource": target_resource},
            action_taken="access_blocked",
            **kwargs
        )
    
    def get_threat_summary(self, hours: int = 24) -> Dict:
        """Get summary of security threats."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            recent_threats = [
                entry for entry in self.security_buffer
                if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
            ]
        
        # Count threats by type and severity
        threat_by_type = defaultdict(int)
        threat_by_severity = defaultdict(int)
        unique_ips = set()
        
        for threat in recent_threats:
            threat_by_type[threat["threat_type"]] += 1
            threat_by_severity[threat["severity"]] += 1
            if threat.get("source_ip"):
                unique_ips.add(threat["source_ip"])
        
        return {
            "period_hours": hours,
            "total_threats": len(recent_threats),
            "unique_source_ips": len(unique_ips),
            "threats_by_type": dict(threat_by_type),
            "threats_by_severity": dict(threat_by_severity),
            "top_threat_ips": self._get_top_threat_ips(recent_threats),
            "recent_critical_threats": [
                threat for threat in recent_threats[-10:]
                if threat["severity"] == "critical"
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _get_top_threat_ips(self, threats: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top threat source IPs."""
        ip_counts = defaultdict(int)
        
        for threat in threats:
            if threat.get("source_ip"):
                ip_counts[threat["source_ip"]] += 1
        
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [{"ip": ip, "threat_count": count} for ip, count in top_ips]
