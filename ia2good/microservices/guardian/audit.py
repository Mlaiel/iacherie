"""
Guardian Audit Logging System
Track all important actions for security and compliance
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json

class AuditAction(str, Enum):
    """Audit action types"""
    # User actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"
    USER_BANNED = "user.banned"
    USER_UNBANNED = "user.unbanned"
    USER_ROLE_CHANGED = "user.role_changed"
    
    # Mission actions
    MISSION_CREATED = "mission.created"
    MISSION_UPDATED = "mission.updated"
    MISSION_DELETED = "mission.deleted"
    MISSION_REGISTERED = "mission.registered"
    
    # Content moderation
    CONTENT_MODERATED = "content.moderated"
    CONTENT_BLOCKED = "content.blocked"
    CONTENT_FLAGGED = "content.flagged"
    
    # File actions
    FILE_UPLOADED = "file.uploaded"
    FILE_DELETED = "file.deleted"
    FILE_DOWNLOADED = "file.downloaded"
    
    # Stream actions
    STREAM_CREATED = "stream.created"
    STREAM_STARTED = "stream.started"
    STREAM_ENDED = "stream.ended"
    
    # Room actions
    ROOM_CREATED = "room.created"
    ROOM_JOINED = "room.joined"
    ROOM_LEFT = "room.left"
    ROOM_CLOSED = "room.closed"
    
    # Chat actions
    MESSAGE_SENT = "message.sent"
    MESSAGE_DELETED = "message.deleted"
    MESSAGE_EDITED = "message.edited"
    
    # Security
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    PERMISSION_DENIED = "security.permission_denied"
    SUSPICIOUS_ACTIVITY = "security.suspicious_activity"

class AuditLevel(str, Enum):
    """Audit log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditLog(BaseModel):
    """Audit log entry"""
    log_id: str
    timestamp: datetime
    action: AuditAction
    level: AuditLevel
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    success: bool = True
    error_message: Optional[str] = None

class AuditLogger:
    """Audit logging system"""
    
    def __init__(self, max_logs: int = 10000):
        self.logs: list[AuditLog] = []
        self.max_logs = max_logs
    
    def log(
        self,
        action: AuditAction,
        level: AuditLevel = AuditLevel.INFO,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log an audit event"""
        import uuid
        
        log_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            action=action,
            level=level,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            success=success,
            error_message=error_message
        )
        
        self.logs.append(log_entry)
        
        # Trim old logs if exceeding max
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Print to console (in production, send to proper logging system)
        print(f"[AUDIT] {log_entry.timestamp.isoformat()} | {log_entry.action} | "
              f"User: {username or 'anonymous'} | Success: {success}")
    
    def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        level: Optional[AuditLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> list[AuditLog]:
        """Query audit logs"""
        filtered_logs = self.logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.user_id == user_id]
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.action == action]
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp <= end_time]
        
        # Return most recent first
        return list(reversed(filtered_logs[-limit:]))
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> list[AuditLog]:
        """Get recent activity for a user"""
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_security_events(self, limit: int = 100) -> list[AuditLog]:
        """Get security-related events"""
        security_actions = [
            AuditAction.RATE_LIMIT_EXCEEDED,
            AuditAction.PERMISSION_DENIED,
            AuditAction.SUSPICIOUS_ACTIVITY,
            AuditAction.USER_BANNED,
            AuditAction.CONTENT_BLOCKED
        ]
        
        security_logs = [
            log for log in self.logs
            if log.action in security_actions or log.level in [AuditLevel.WARNING, AuditLevel.ERROR, AuditLevel.CRITICAL]
        ]
        
        return list(reversed(security_logs[-limit:]))
    
    def export_logs(self, filename: str):
        """Export logs to JSON file"""
        with open(filename, 'w') as f:
            json.dump([log.dict() for log in self.logs], f, indent=2, default=str)
    
    def clear_old_logs(self, days: int = 30):
        """Clear logs older than specified days"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.logs = [log for log in self.logs if log.timestamp >= cutoff]

# Singleton instance
_audit_logger_instance = None

def get_audit_logger() -> AuditLogger:
    """Get or create audit logger instance"""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        _audit_logger_instance = AuditLogger()
    return _audit_logger_instance

def audit_log(
    action: AuditAction,
    **kwargs
):
    """Convenience function for logging"""
    logger = get_audit_logger()
    logger.log(action, **kwargs)
