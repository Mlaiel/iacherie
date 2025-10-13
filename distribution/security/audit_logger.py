"""
Audit Logger Module
==================

Enterprise-grade audit logging system for comprehensive security monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2024 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import aiofiles
import hashlib
import hmac
from cryptography.fernet import Fernet

class AuditEventType(Enum):
    """Types of audit events"""
    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    
    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_ESCALATION = "permission_escalation"
    ROLE_CHANGE = "role_change"
    
    # Data access events
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"
    
    # API events
    API_CALL = "api_call"
    API_ERROR = "api_error"
    API_RATE_LIMIT_HIT = "api_rate_limit_hit"
    
    # Security events
    SECURITY_VIOLATION = "security_violation"
    THREAT_DETECTED = "threat_detected"
    VULNERABILITY_FOUND = "vulnerability_found"
    ENCRYPTION_KEY_ROTATION = "encryption_key_rotation"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    CONFIGURATION_CHANGE = "configuration_change"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    # Distribution events
    CONTENT_DISTRIBUTED = "content_distributed"
    VIRAL_PREDICTION = "viral_prediction"
    COLLABORATION_MATCHED = "collaboration_matched"
    CRISIS_DETECTED = "crisis_detected"
    PLATFORM_ERROR = "platform_error"

class AuditSeverity(Enum):
    """Audit event severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    outcome: str = "unknown"  # success, failure, partial
    details: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    source_system: str = "distribution"
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure timestamp has timezone info
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['severity'] = self.severity.value
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

@dataclass
class AuditLogConfig:
    """Audit logging configuration"""
    log_file_path: str = "logs/audit.log"
    encrypted_log_path: str = "logs/audit_encrypted.log"
    max_file_size_mb: int = 100
    max_backup_files: int = 10
    encryption_enabled: bool = True
    compression_enabled: bool = True
    remote_logging_enabled: bool = True
    remote_endpoint: Optional[str] = None
    integrity_check_enabled: bool = True
    real_time_alerts_enabled: bool = True
    alert_webhook_url: Optional[str] = None

class AuditLogger:
    """Enterprise audit logging system"""
    
    def __init__(self, config: AuditLogConfig):
        self.config = config
        self.logger = logging.getLogger("audit")
        self._setup_logger()
        self._encryption_key = None
        self._log_queue = asyncio.Queue()
        self._is_running = False
        self._log_processor_task = None
        
        # Initialize encryption if enabled
        if config.encryption_enabled:
            self._setup_encryption()
    
    def _setup_logger(self):
        """Setup audit logger configuration"""
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S UTC'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.config.log_file_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def _setup_encryption(self):
        """Setup encryption for audit logs"""
        try:
            # In production, this would use a proper key management system
            self._encryption_key = Fernet.generate_key()
            self._cipher = Fernet(self._encryption_key)
        except Exception as e:
            logging.error(f"Failed to setup encryption: {e}")
            self.config.encryption_enabled = False
    
    async def start(self):
        """Start the audit logging system"""
        if self._is_running:
            return
        
        self._is_running = True
        self._log_processor_task = asyncio.create_task(self._process_log_queue())
        
        # Log system start
        await self.log_event(AuditEvent(
            event_type=AuditEventType.SYSTEM_START,
            severity=AuditSeverity.INFO,
            details={"component": "audit_logger"}
        ))
    
    async def stop(self):
        """Stop the audit logging system"""
        if not self._is_running:
            return
        
        # Log system stop
        await self.log_event(AuditEvent(
            event_type=AuditEventType.SYSTEM_STOP,
            severity=AuditSeverity.INFO,
            details={"component": "audit_logger"}
        ))
        
        self._is_running = False
        if self._log_processor_task:
            await self._log_processor_task
    
    async def log_event(self, event: AuditEvent):
        """Log an audit event"""
        try:
            # Add to queue for processing
            await self._log_queue.put(event)
            
            # Immediate critical event handling
            if event.severity == AuditSeverity.CRITICAL:
                await self._handle_critical_event(event)
                
        except Exception as e:
            logging.error(f"Failed to log audit event: {e}")
    
    async def _process_log_queue(self):
        """Process audit log queue"""
        while self._is_running:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(self._log_queue.get(), timeout=1.0)
                await self._write_log_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logging.error(f"Error processing audit log: {e}")
    
    async def _write_log_event(self, event: AuditEvent):
        """Write audit event to storage"""
        try:
            # Standard logging
            self.logger.info(event.to_json())
            
            # Encrypted logging if enabled
            if self.config.encryption_enabled:
                await self._write_encrypted_log(event)
            
            # Remote logging if enabled
            if self.config.remote_logging_enabled and self.config.remote_endpoint:
                await self._send_remote_log(event)
            
            # Real-time alerts if enabled
            if self.config.real_time_alerts_enabled:
                await self._check_alert_conditions(event)
                
        except Exception as e:
            logging.error(f"Failed to write audit log: {e}")
    
    async def _write_encrypted_log(self, event: AuditEvent):
        """Write encrypted audit log"""
        try:
            if not self._cipher:
                return
            
            encrypted_data = self._cipher.encrypt(event.to_json().encode())
            
            async with aiofiles.open(self.config.encrypted_log_path, 'ab') as f:
                await f.write(encrypted_data + b'\n')
                
        except Exception as e:
            logging.error(f"Failed to write encrypted log: {e}")
    
    async def _send_remote_log(self, event: AuditEvent):
        """Send audit log to remote endpoint"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.remote_endpoint,
                    json=event.to_dict(),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        logging.warning(f"Remote logging failed: {response.status}")
                        
        except Exception as e:
            logging.error(f"Failed to send remote log: {e}")
    
    async def _check_alert_conditions(self, event: AuditEvent):
        """Check if event requires immediate alert"""
        alert_conditions = [
            event.severity == AuditSeverity.CRITICAL,
            event.event_type == AuditEventType.SECURITY_VIOLATION,
            event.event_type == AuditEventType.THREAT_DETECTED,
            event.outcome == "failure" and event.severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]
        ]
        
        if any(alert_conditions):
            await self._send_alert(event)
    
    async def _send_alert(self, event: AuditEvent):
        """Send immediate alert for critical events"""
        try:
            if not self.config.alert_webhook_url:
                return
            
            import aiohttp
            
            alert_data = {
                "alert_type": "audit_security_event",
                "severity": event.severity.value,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "details": event.details,
                "user_id": event.user_id,
                "ip_address": event.ip_address
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.alert_webhook_url,
                    json=alert_data
                ) as response:
                    if response.status == 200:
                        logging.info(f"Alert sent for event: {event.event_type.value}")
                    else:
                        logging.error(f"Failed to send alert: {response.status}")
                        
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")
    
    async def _handle_critical_event(self, event: AuditEvent):
        """Handle critical events immediately"""
        try:
            # Immediate response for critical events
            if event.event_type == AuditEventType.SECURITY_VIOLATION:
                # Could trigger automatic security responses
                logging.critical(f"SECURITY VIOLATION: {event.details}")
            
            elif event.event_type == AuditEventType.THREAT_DETECTED:
                # Could trigger threat response procedures
                logging.critical(f"THREAT DETECTED: {event.details}")
            
            # Could integrate with incident response systems
            
        except Exception as e:
            logging.error(f"Failed to handle critical event: {e}")
    
    async def search_events(
        self,
        start_time: datetime,
        end_time: datetime,
        event_types: Optional[List[AuditEventType]] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None
    ) -> List[AuditEvent]:
        """Search audit events (simplified implementation)"""
        # In production, this would query a proper database or search system
        events = []
        
        try:
            # This is a simplified file-based search
            # Production would use database queries or log search systems
            async with aiofiles.open(self.config.log_file_path, 'r') as f:
                async for line in f:
                    try:
                        event_data = json.loads(line.split(' | ')[-1])
                        event_time = datetime.fromisoformat(event_data['timestamp'])
                        
                        # Apply filters
                        if start_time <= event_time <= end_time:
                            if event_types and event_data['event_type'] not in [et.value for et in event_types]:
                                continue
                            if severity and event_data['severity'] != severity.value:
                                continue
                            if user_id and event_data.get('user_id') != user_id:
                                continue
                            
                            # Convert back to AuditEvent object
                            event = AuditEvent(
                                event_type=AuditEventType(event_data['event_type']),
                                severity=AuditSeverity(event_data['severity']),
                                timestamp=event_time,
                                user_id=event_data.get('user_id'),
                                session_id=event_data.get('session_id'),
                                ip_address=event_data.get('ip_address'),
                                user_agent=event_data.get('user_agent'),
                                resource=event_data.get('resource'),
                                action=event_data.get('action'),
                                outcome=event_data.get('outcome', 'unknown'),
                                details=event_data.get('details', {}),
                                request_id=event_data.get('request_id'),
                                source_system=event_data.get('source_system', 'distribution')
                            )
                            events.append(event)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        
        except Exception as e:
            logging.error(f"Failed to search audit events: {e}")
        
        return events
    
    def generate_integrity_hash(self, event: AuditEvent) -> str:
        """Generate integrity hash for audit event"""
        event_data = event.to_json()
        return hmac.new(
            self._encryption_key or b'default_key',
            event_data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def verify_log_integrity(self) -> bool:
        """Verify audit log integrity"""
        try:
            # This would implement comprehensive integrity checking
            # For now, return True as placeholder
            return True
        except Exception as e:
            logging.error(f"Failed to verify log integrity: {e}")
            return False

# Convenience functions for common audit events
async def log_authentication_event(
    logger: AuditLogger,
    event_type: AuditEventType,
    user_id: str,
    ip_address: str,
    success: bool,
    details: Optional[Dict] = None
):
    """Log authentication event"""
    await logger.log_event(AuditEvent(
        event_type=event_type,
        severity=AuditSeverity.INFO if success else AuditSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address,
        outcome="success" if success else "failure",
        details=details or {}
    ))

async def log_api_call(
    logger: AuditLogger,
    user_id: str,
    endpoint: str,
    method: str,
    status_code: int,
    ip_address: str,
    details: Optional[Dict] = None
):
    """Log API call"""
    severity = AuditSeverity.INFO if status_code < 400 else AuditSeverity.MEDIUM
    if status_code >= 500:
        severity = AuditSeverity.HIGH
    
    await logger.log_event(AuditEvent(
        event_type=AuditEventType.API_CALL,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        resource=endpoint,
        action=method,
        outcome="success" if status_code < 400 else "failure",
        details={"status_code": status_code, **(details or {})}
    ))

async def log_security_violation(
    logger: AuditLogger,
    user_id: Optional[str],
    violation_type: str,
    ip_address: str,
    details: Dict
):
    """Log security violation"""
    await logger.log_event(AuditEvent(
        event_type=AuditEventType.SECURITY_VIOLATION,
        severity=AuditSeverity.CRITICAL,
        user_id=user_id,
        ip_address=ip_address,
        outcome="failure",
        details={"violation_type": violation_type, **details}
    ))

async def log_distribution_event(
    logger: AuditLogger,
    user_id: str,
    content_id: str,
    platforms: List[str],
    success: bool,
    details: Optional[Dict] = None
):
    """Log content distribution event"""
    await logger.log_event(AuditEvent(
        event_type=AuditEventType.CONTENT_DISTRIBUTED,
        severity=AuditSeverity.INFO,
        user_id=user_id,
        resource=content_id,
        action="distribute",
        outcome="success" if success else "failure",
        details={"platforms": platforms, **(details or {})}
    ))

# Export classes and functions
__all__ = [
    "AuditEventType",
    "AuditSeverity",
    "AuditEvent",
    "AuditLogConfig",
    "AuditLogger",
    "log_authentication_event",
    "log_api_call",
    "log_security_violation", 
    "log_distribution_event"
]