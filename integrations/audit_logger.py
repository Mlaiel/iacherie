"""Audit Logger - Integration Audit and Compliance System
========================================================

Comprehensive audit logging system for integration activities, compliance tracking,
and security monitoring. Provides detailed audit trails for all integration operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import gzip
import pickle
from collections import defaultdict

import aiofiles
import aioredis
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Audit event categories."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    API_REQUEST = "api_request"
    API_RESPONSE = "api_response"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    ERROR = "error"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    WEBHOOK = "webhook"
    OAUTH_FLOW = "oauth_flow"
    PAYMENT_TRANSACTION = "payment_transaction"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"

class AuditSeverity(Enum):
    """Audit event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    CCPA = "ccpa"

@dataclass
class AuditEvent:
    """Individual audit event record."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_type: AuditEventType = AuditEventType.SYSTEM_EVENT
    severity: AuditSeverity = AuditSeverity.LOW
    
    # Event context
    integration_name: Optional[str] = None
    service_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Event details
    action: str = ""
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    outcome: str = "success"  # success, failure, error
    
    # Request/Response data
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Security context
    auth_method: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    risk_score: int = 0  # 0-100
    
    # Performance metrics
    duration_ms: Optional[float] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    
    # Compliance metadata
    compliance_frameworks: List[ComplianceFramework] = field(default_factory=list)
    data_classification: Optional[str] = None
    retention_period: Optional[timedelta] = None
    
    # Additional metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None

@dataclass
class AuditConfiguration:
    """Audit system configuration."""
    enabled: bool = True
    log_level: str = "INFO"
    
    # Storage configuration
    storage_backend: str = "file"  # file, redis, database
    storage_path: str = "/home/runner/work/Ainflue/Ainflue/logs/audit"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_files: int = 100
    compression_enabled: bool = True
    
    # Redis configuration
    redis_url: Optional[str] = None
    redis_key_prefix: str = "audit:"
    redis_ttl: int = 90 * 24 * 3600  # 90 days
    
    # Real-time monitoring
    real_time_alerts: bool = True
    alert_severity_threshold: AuditSeverity = AuditSeverity.HIGH
    webhook_urls: List[str] = field(default_factory=list)
    
    # Compliance settings
    gdpr_mode: bool = True
    data_anonymization: bool = True
    automatic_deletion: bool = True
    
    # Performance settings
    async_logging: bool = True
    batch_size: int = 100
    flush_interval: int = 30  # seconds
    
    # Security settings
    encryption_enabled: bool = True
    integrity_checks: bool = True
    digital_signatures: bool = False

class AuditLogger:
    """Comprehensive audit logging system."""
    
    def __init__(self, config: Optional[AuditConfiguration] = None):
        self.config = config or AuditConfiguration()
        
        # Initialize storage
        self.storage_backend = None
        self.redis_client = None
        self.encryption_key = None
        
        # Event buffers for async processing
        self.event_buffer: List[AuditEvent] = []
        self.buffer_lock = asyncio.Lock()
        
        # Real-time processors
        self.alert_processors: List[callable] = []
        self.compliance_processors: List[callable] = []
        
        # Statistics tracking
        self.stats = defaultdict(int)
        self.performance_metrics = defaultdict(list)
        
        # Background tasks
        self.flush_task = None
        self.cleanup_task = None
        
        logger.info("Audit Logger initialized")

    async def initialize(self) -> None:
        """Initialize audit logging system."""
        try:
            # Setup encryption if enabled
            if self.config.encryption_enabled:
                self.encryption_key = Fernet.generate_key()
                
            # Initialize storage backend
            await self._initialize_storage()
            
            # Setup background tasks
            if self.config.async_logging:
                self.flush_task = asyncio.create_task(self._flush_buffer_periodically())
                self.cleanup_task = asyncio.create_task(self._cleanup_old_logs())
                
            # Setup compliance processors
            await self._setup_compliance_processors()
            
            logger.info("Audit Logger initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize audit logger: {e}")
            raise

    async def _initialize_storage(self) -> None:
        """Initialize storage backend."""
        if self.config.storage_backend == "redis":
            if self.config.redis_url:
                self.redis_client = await aioredis.from_url(self.config.redis_url)
                await self.redis_client.ping()
                logger.info("Redis storage backend initialized")
            else:
                logger.warning("Redis URL not configured, falling back to file storage")
                self.config.storage_backend = "file"
                
        if self.config.storage_backend == "file":
            storage_path = Path(self.config.storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"File storage backend initialized at {storage_path}")

    async def log_event(self, event: AuditEvent) -> None:
        """Log an audit event."""
        try:
            # Enhance event with system context
            await self._enhance_event(event)
            
            # Validate event
            await self._validate_event(event)
            
            # Apply compliance rules
            await self._apply_compliance_rules(event)
            
            # Process security context
            await self._process_security_context(event)
            
            # Store event
            if self.config.async_logging:
                await self._buffer_event(event)
            else:
                await self._store_event(event)
                
            # Real-time processing
            await self._process_real_time_alerts(event)
            
            # Update statistics
            self._update_statistics(event)
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Fallback logging to ensure audit trails are preserved
            await self._fallback_log(event, str(e))

    async def _enhance_event(self, event: AuditEvent) -> None:
        """Enhance event with additional context."""
        # Add correlation ID if not present
        if not event.correlation_id:
            event.correlation_id = str(uuid.uuid4())
            
        # Add trace ID for distributed tracing
        if not event.trace_id:
            event.trace_id = str(uuid.uuid4())
            
        # Calculate risk score based on event characteristics
        event.risk_score = await self._calculate_risk_score(event)
        
        # Add compliance framework tags
        if not event.compliance_frameworks:
            event.compliance_frameworks = await self._determine_compliance_frameworks(event)

    async def _validate_event(self, event: AuditEvent) -> None:
        """Validate audit event data."""
        # Required fields validation
        if not event.action:
            raise ValueError("Event action is required")
            
        # Severity validation
        if event.severity not in AuditSeverity:
            event.severity = AuditSeverity.LOW
            
        # Risk score validation
        if not 0 <= event.risk_score <= 100:
            event.risk_score = max(0, min(100, event.risk_score))
            
        # PII detection and masking
        if self.config.data_anonymization:
            await self._mask_sensitive_data(event)

    async def _apply_compliance_rules(self, event: AuditEvent) -> None:
        """Apply compliance-specific rules."""
        for framework in event.compliance_frameworks:
            if framework == ComplianceFramework.GDPR:
                await self._apply_gdpr_rules(event)
            elif framework == ComplianceFramework.SOC2:
                await self._apply_soc2_rules(event)
            elif framework == ComplianceFramework.PCI_DSS:
                await self._apply_pci_rules(event)

    async def _apply_gdpr_rules(self, event: AuditEvent) -> None:
        """Apply GDPR compliance rules."""
        # Set retention period
        if not event.retention_period:
            event.retention_period = timedelta(days=1095)  # 3 years
            
        # Data classification
        if not event.data_classification:
            event.data_classification = "personal_data"
            
        # Add GDPR tags
        if "gdpr_compliant" not in event.tags:
            event.tags.append("gdpr_compliant")

    async def _apply_soc2_rules(self, event: AuditEvent) -> None:
        """Apply SOC2 compliance rules."""
        # Ensure security events are marked appropriately
        if event.event_type in [AuditEventType.AUTHENTICATION, AuditEventType.AUTHORIZATION]:
            if "soc2_security" not in event.tags:
                event.tags.append("soc2_security")

    async def _apply_pci_rules(self, event: AuditEvent) -> None:
        """Apply PCI DSS compliance rules."""
        # Payment-related events require special handling
        if event.event_type == AuditEventType.PAYMENT_TRANSACTION:
            if "pci_compliant" not in event.tags:
                event.tags.append("pci_compliant")
                
            # Mask payment card data
            if event.request_data:
                await self._mask_payment_data(event.request_data)
            if event.response_data:
                await self._mask_payment_data(event.response_data)

    async def _mask_sensitive_data(self, event: AuditEvent) -> None:
        """Mask sensitive data in event."""
        sensitive_patterns = [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # IP address
        ]
        
        # Mask in request/response data
        for data_field in ['request_data', 'response_data']:
            data = getattr(event, data_field)
            if data:
                setattr(event, data_field, await self._mask_data_patterns(data, sensitive_patterns))

    async def _mask_data_patterns(self, data: Any, patterns: List[str]) -> Any:
        """Mask sensitive patterns in data."""
        import re
        
        if isinstance(data, str):
            for pattern in patterns:
                data = re.sub(pattern, '[MASKED]', data)
            return data
        elif isinstance(data, dict):
            return {k: await self._mask_data_patterns(v, patterns) for k, v in data.items()}
        elif isinstance(data, list):
            return [await self._mask_data_patterns(item, patterns) for item in data]
        return data

    async def _mask_payment_data(self, data: Dict[str, Any]) -> None:
        """Mask payment-related sensitive data."""
        payment_fields = ['card_number', 'cvv', 'account_number', 'routing_number']
        
        for field in payment_fields:
            if field in data:
                if isinstance(data[field], str) and len(data[field]) > 4:
                    # Keep only last 4 digits
                    data[field] = '*' * (len(data[field]) - 4) + data[field][-4:]

    async def _calculate_risk_score(self, event: AuditEvent) -> int:
        """Calculate risk score for event."""
        score = 0
        
        # Base score by event type
        risk_weights = {
            AuditEventType.SECURITY_EVENT: 40,
            AuditEventType.AUTHENTICATION: 30,
            AuditEventType.AUTHORIZATION: 25,
            AuditEventType.DATA_MODIFICATION: 20,
            AuditEventType.PAYMENT_TRANSACTION: 35,
            AuditEventType.ERROR: 15,
            AuditEventType.API_REQUEST: 5
        }
        
        score += risk_weights.get(event.event_type, 10)
        
        # Severity multiplier
        severity_multipliers = {
            AuditSeverity.CRITICAL: 2.0,
            AuditSeverity.HIGH: 1.5,
            AuditSeverity.MEDIUM: 1.0,
            AuditSeverity.LOW: 0.5
        }
        
        score = int(score * severity_multipliers.get(event.severity, 1.0))
        
        # Failure outcome increases risk
        if event.outcome in ['failure', 'error']:
            score += 20
            
        # Multiple failed attempts (detected via correlation)
        # This would require session tracking
        
        return min(100, max(0, score))

    async def _determine_compliance_frameworks(self, event: AuditEvent) -> List[ComplianceFramework]:
        """Determine applicable compliance frameworks."""
        frameworks = []
        
        # Always apply GDPR for personal data
        if self.config.gdpr_mode:
            frameworks.append(ComplianceFramework.GDPR)
            
        # SOC2 for security events
        if event.event_type in [
            AuditEventType.AUTHENTICATION,
            AuditEventType.AUTHORIZATION,
            AuditEventType.SECURITY_EVENT
        ]:
            frameworks.append(ComplianceFramework.SOC2)
            
        # PCI DSS for payment events
        if event.event_type == AuditEventType.PAYMENT_TRANSACTION:
            frameworks.append(ComplianceFramework.PCI_DSS)
            
        return frameworks

    async def _buffer_event(self, event: AuditEvent) -> None:
        """Add event to buffer for async processing."""
        async with self.buffer_lock:
            self.event_buffer.append(event)
            
            # Flush buffer if it's full
            if len(self.event_buffer) >= self.config.batch_size:
                await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Flush event buffer to storage."""
        async with self.buffer_lock:
            if not self.event_buffer:
                return
                
            events_to_process = self.event_buffer.copy()
            self.event_buffer.clear()
            
        # Process events outside of lock
        for event in events_to_process:
            try:
                await self._store_event(event)
            except Exception as e:
                logger.error(f"Failed to store event {event.event_id}: {e}")

    async def _flush_buffer_periodically(self) -> None:
        """Periodically flush buffer."""
        while True:
            try:
                await asyncio.sleep(self.config.flush_interval)
                await self._flush_buffer()
            except asyncio.CancelledError:
                # Final flush before shutdown
                await self._flush_buffer()
                break
            except Exception as e:
                logger.error(f"Error in periodic buffer flush: {e}")

    async def _store_event(self, event: AuditEvent) -> None:
        """Store event to configured backend."""
        if self.config.storage_backend == "redis":
            await self._store_to_redis(event)
        else:
            await self._store_to_file(event)

    async def _store_to_redis(self, event: AuditEvent) -> None:
        """Store event to Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
            
        # Serialize event
        event_data = self._serialize_event(event)
        
        # Store with TTL
        key = f"{self.config.redis_key_prefix}{event.event_id}"
        await self.redis_client.setex(key, self.config.redis_ttl, event_data)
        
        # Add to time-based index
        timestamp_key = f"{self.config.redis_key_prefix}by_time:{event.timestamp.strftime('%Y-%m-%d-%H')}"
        await self.redis_client.lpush(timestamp_key, event.event_id)
        await self.redis_client.expire(timestamp_key, self.config.redis_ttl)
        
        # Add to type-based index
        type_key = f"{self.config.redis_key_prefix}by_type:{event.event_type.value}"
        await self.redis_client.lpush(type_key, event.event_id)
        await self.redis_client.expire(type_key, self.config.redis_ttl)

    async def _store_to_file(self, event: AuditEvent) -> None:
        """Store event to file."""
        # Determine file path
        date_str = event.timestamp.strftime('%Y-%m-%d')
        file_path = Path(self.config.storage_path) / f"audit_{date_str}.jsonl"
        
        # Serialize event
        event_data = self._serialize_event(event)
        
        # Append to file
        async with aiofiles.open(file_path, mode='a') as f:
            await f.write(event_data + '\n')
            
        # Check file rotation
        await self._check_file_rotation(file_path)

    def _serialize_event(self, event: AuditEvent) -> str:
        """Serialize event to JSON."""
        # Convert to dictionary
        event_dict = asdict(event)
        
        # Handle datetime serialization
        event_dict['timestamp'] = event.timestamp.isoformat()
        if event.retention_period:
            event_dict['retention_period'] = event.retention_period.total_seconds()
            
        # Handle enum serialization
        event_dict['event_type'] = event.event_type.value
        event_dict['severity'] = event.severity.value
        event_dict['compliance_frameworks'] = [f.value for f in event.compliance_frameworks]
        
        # Encrypt if enabled
        data = json.dumps(event_dict)
        if self.config.encryption_enabled and self.encryption_key:
            cipher_suite = Fernet(self.encryption_key)
            data = cipher_suite.encrypt(data.encode()).decode()
            
        return data

    async def _check_file_rotation(self, file_path: Path) -> None:
        """Check if file needs rotation."""
        try:
            file_size = file_path.stat().st_size
            if file_size > self.config.max_file_size:
                await self._rotate_file(file_path)
        except Exception as e:
            logger.error(f"Error checking file rotation: {e}")

    async def _rotate_file(self, file_path: Path) -> None:
        """Rotate log file."""
        try:
            # Compress current file
            if self.config.compression_enabled:
                compressed_path = file_path.with_suffix('.gz')
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                file_path.unlink()
                
            # Clean up old files
            await self._cleanup_old_files()
            
        except Exception as e:
            logger.error(f"Error rotating file: {e}")

    async def _cleanup_old_files(self) -> None:
        """Clean up old audit files."""
        storage_path = Path(self.config.storage_path)
        
        # Get all audit files
        audit_files = list(storage_path.glob("audit_*.jsonl*"))
        audit_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove excess files
        if len(audit_files) > self.config.max_files:
            for file_path in audit_files[self.config.max_files:]:
                file_path.unlink()

    async def _cleanup_old_logs(self) -> None:
        """Periodically clean up old logs."""
        while True:
            try:
                await asyncio.sleep(24 * 3600)  # Daily cleanup
                await self._cleanup_old_files()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in log cleanup: {e}")

    async def _process_real_time_alerts(self, event: AuditEvent) -> None:
        """Process real-time alerts."""
        if not self.config.real_time_alerts:
            return
            
        # Check if event meets alert threshold
        severity_levels = {
            AuditSeverity.LOW: 1,
            AuditSeverity.MEDIUM: 2,
            AuditSeverity.HIGH: 3,
            AuditSeverity.CRITICAL: 4
        }
        
        if severity_levels[event.severity] < severity_levels[self.config.alert_severity_threshold]:
            return
            
        # Process alert
        await self._send_alert(event)

    async def _send_alert(self, event: AuditEvent) -> None:
        """Send alert for high-severity events."""
        alert_data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "action": event.action,
            "outcome": event.outcome,
            "risk_score": event.risk_score,
            "integration_name": event.integration_name,
            "user_id": event.user_id
        }
        
        # Send to configured webhooks
        for webhook_url in self.config.webhook_urls:
            try:
                # This would typically use an HTTP client
                logger.info(f"Sending alert to {webhook_url}: {alert_data}")
            except Exception as e:
                logger.error(f"Failed to send alert to {webhook_url}: {e}")

    def _update_statistics(self, event: AuditEvent) -> None:
        """Update audit statistics."""
        self.stats['total_events'] += 1
        self.stats[f'events_by_type_{event.event_type.value}'] += 1
        self.stats[f'events_by_severity_{event.severity.value}'] += 1
        
        if event.outcome in ['failure', 'error']:
            self.stats['failed_events'] += 1
            
        if event.duration_ms:
            self.performance_metrics['durations'].append(event.duration_ms)

    async def _fallback_log(self, event: AuditEvent, error: str) -> None:
        """Fallback logging when main logging fails."""
        try:
            fallback_path = Path(self.config.storage_path) / "fallback.log"
            fallback_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "error": error,
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "action": event.action
            }
            
            async with aiofiles.open(fallback_path, mode='a') as f:
                await f.write(json.dumps(fallback_entry) + '\n')
                
        except Exception as e:
            logger.critical(f"Fallback logging failed: {e}")

    async def query_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        integration_name: Optional[str] = None,
        outcome: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Query audit events with filters."""
        # This is a simplified implementation
        # In a production system, you'd implement efficient indexing and querying
        events = []
        
        try:
            if self.config.storage_backend == "redis":
                events = await self._query_redis_events(
                    start_time, end_time, event_type, user_id, 
                    integration_name, outcome, min_risk_score, limit
                )
            else:
                events = await self._query_file_events(
                    start_time, end_time, event_type, user_id,
                    integration_name, outcome, min_risk_score, limit
                )
                
        except Exception as e:
            logger.error(f"Error querying events: {e}")
            
        return events

    async def _query_redis_events(self, *args) -> List[AuditEvent]:
        """Query events from Redis (simplified implementation)."""
        # This would implement Redis-based querying with indexes
        return []

    async def _query_file_events(self, *args) -> List[AuditEvent]:
        """Query events from files (simplified implementation)."""
        # This would implement file-based querying
        return []

    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit system statistics."""
        stats = dict(self.stats)
        
        # Calculate additional metrics
        if self.performance_metrics['durations']:
            durations = self.performance_metrics['durations']
            stats['avg_duration_ms'] = sum(durations) / len(durations)
            stats['max_duration_ms'] = max(durations)
            stats['min_duration_ms'] = min(durations)
            
        stats['buffer_size'] = len(self.event_buffer)
        stats['config'] = asdict(self.config)
        
        return stats

    async def health_check(self) -> Dict[str, Any]:
        """Perform audit system health check."""
        health = {
            "status": "healthy",
            "storage_backend": self.config.storage_backend,
            "events_logged": self.stats.get('total_events', 0),
            "buffer_size": len(self.event_buffer),
            "issues": []
        }
        
        # Check storage connectivity
        try:
            if self.config.storage_backend == "redis" and self.redis_client:
                await self.redis_client.ping()
            elif self.config.storage_backend == "file":
                storage_path = Path(self.config.storage_path)
                if not storage_path.exists():
                    health["issues"].append("Storage directory does not exist")
                    health["status"] = "degraded"
        except Exception as e:
            health["issues"].append(f"Storage connectivity issue: {e}")
            health["status"] = "unhealthy"
            
        return health

    async def shutdown(self) -> None:
        """Shutdown audit logger gracefully."""
        logger.info("Shutting down audit logger...")
        
        # Cancel background tasks
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
                
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Final buffer flush
        await self._flush_buffer()
        
        # Close connections
        if self.redis_client:
            await self.redis_client.close()
            
        logger.info("Audit logger shutdown completed")

    def __repr__(self) -> str:
        return f"AuditLogger(backend={self.config.storage_backend}, events={self.stats.get('total_events', 0)})"


# Convenience functions for common audit events
async def log_authentication_event(
    user_id: str,
    auth_method: str,
    outcome: str,
    ip_address: Optional[str] = None,
    integration_name: Optional[str] = None,
    **kwargs
) -> None:
    """Log authentication event."""
    event = AuditEvent(
        event_type=AuditEventType.AUTHENTICATION,
        action="user_authentication",
        user_id=user_id,
        auth_method=auth_method,
        outcome=outcome,
        ip_address=ip_address,
        integration_name=integration_name,
        severity=AuditSeverity.HIGH if outcome != "success" else AuditSeverity.MEDIUM,
        **kwargs
    )
    
    await audit_logger.log_event(event)

async def log_api_request(
    integration_name: str,
    action: str,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None,
    outcome: str = "success",
    **kwargs
) -> None:
    """Log API request event."""
    event = AuditEvent(
        event_type=AuditEventType.API_REQUEST,
        integration_name=integration_name,
        action=action,
        request_data=request_data,
        response_data=response_data,
        duration_ms=duration_ms,
        outcome=outcome,
        severity=AuditSeverity.LOW,
        **kwargs
    )
    
    await audit_logger.log_event(event)

async def log_security_event(
    action: str,
    severity: AuditSeverity,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> None:
    """Log security event."""
    event = AuditEvent(
        event_type=AuditEventType.SECURITY_EVENT,
        action=action,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        error_details=details,
        **kwargs
    )
    
    await audit_logger.log_event(event)


# Global audit logger instance
audit_logger = AuditLogger()

# Export main classes and functions
__all__ = [
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditSeverity",
    "ComplianceFramework",
    "AuditConfiguration",
    "audit_logger",
    "log_authentication_event",
    "log_api_request",
    "log_security_event"
]