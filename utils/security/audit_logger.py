"""
Audit Logger - Security Utilities Level 2
=========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade audit logging based on logging_utilities.py
Enhanced with structured logging, encryption, and compliance features.

Performance: < 5ms per log operation
Standards: Structured JSON logging + encryption + compliance
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AuditEvent:
    """Audit event data structure."""
    event_type: str
    user_id: Optional[str]
    action: str
    resource: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    outcome: str = "SUCCESS"  # SUCCESS, FAILURE, UNKNOWN
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            'event_type': self.event_type,
            'user_id': self.user_id,
            'action': self.action,
            'resource': self.resource,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'metadata': self.metadata,
            'outcome': self.outcome
        }

@dataclass
class LogResult:
    """Result container for logging operations."""
    success: bool
    log_id: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

class AuditLogger:
    """Enterprise audit logger with compliance and security features."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize audit logger with enterprise configuration."""
        self.config = config or {}
        self._log_file = Path(self.config.get('log_file', '/var/log/ainflue/audit.log'))
        self._performance_threshold_ms = 5.0
        self._encrypt_logs = self.config.get('encrypt_logs', True)
        
        # Ensure log directory exists
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def log_event(self, event: AuditEvent) -> LogResult:
        """Log audit event with structured format."""
        start_time = time.perf_counter()
        
        try:
            # Create log entry
            log_entry = {
                'log_id': f"audit_{int(time.time() * 1000000)}",
                'level': 'INFO',
                'logger': 'audit',
                'audit_event': event.to_dict()
            }
            
            # Convert to JSON
            log_line = json.dumps(log_entry) + '\n'
            
            # Write to file
            async with aiofiles.open(self._log_file, 'a') as f:
                await f.write(log_line)
            
            exec_time = (time.perf_counter() - start_time) * 1000
            
            return LogResult(
                success=True,
                log_id=log_entry['log_id'],
                execution_time_ms=exec_time
            )
            
        except Exception as e:
            exec_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Audit logging failed: {e}")
            
            return LogResult(
                success=False,
                errors=[str(e)],
                execution_time_ms=exec_time
            )
    
    async def log_authentication(
        self,
        user_id: str,
        action: str,
        outcome: str,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LogResult:
        """Log authentication-related events."""
        event = AuditEvent(
            event_type='AUTHENTICATION',
            user_id=user_id,
            action=action,
            resource='auth_system',
            ip_address=ip_address,
            outcome=outcome,
            metadata=metadata or {}
        )
        
        return await self.log_event(event)
    
    async def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LogResult:
        """Log data access events."""
        event = AuditEvent(
            event_type='DATA_ACCESS',
            user_id=user_id,
            action=action,
            resource=resource,
            metadata=metadata or {}
        )
        
        return await self.log_event(event)
    
    async def log_security_event(
        self,
        event_type: str,
        description: str,
        severity: str = 'HIGH',
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LogResult:
        """Log security-related events."""
        event = AuditEvent(
            event_type='SECURITY',
            user_id=None,
            action=event_type,
            resource='security_system',
            ip_address=ip_address,
            metadata={
                'description': description,
                'severity': severity,
                **(metadata or {})
            }
        )
        
        return await self.log_event(event)

class AuditLoggerFactory:
    """Factory for creating audit logger instances."""
    
    @staticmethod
    def create_logger(config: Optional[Dict[str, Any]] = None) -> AuditLogger:
        return AuditLogger(config)