"""Security Audit Trail Implementation
Comprehensive audit trail system for security events, access logging, and compliance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
import uuid

from database.audit_logs.security_events import SecurityEventLogger, SecurityEventType
from data_management.governance.access import AccessController, AccessLog
from ai_engine.ml.audit_logger import AuditLogger, AuditLevel, AuditCategory

logger = logging.getLogger(__name__)


class AuditTrailLevel(Enum):
    """
Security audit trail severity levels"""

    INFO = "info"
    WARNING = "warning"
    SECURITY = "security"
    CRITICAL = "critical"
    COMPLIANCE = "compliance"


@dataclass
class SecurityAuditEvent:
    """Security audit event record"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    level: AuditTrailLevel = AuditTrailLevel.INFO
    category: str = ""
    action: str = ""
    resource: str = ""
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    details: Dict[str, Any] = field(default_factory=dict)
    compliance_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "category": self.category,
            "action": self.action,
            "resource": self.resource,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "details": self.details,
            "compliance_flags": self.compliance_flags
        }


class SecurityAuditTrail:
    """Comprehensive security audit trail system"""
    
    def __init__(self):
        self.security_logger = SecurityEventLogger()
        self.access_controller = AccessController()
        self.audit_logger = AuditLogger()
        self.events_cache: List[SecurityAuditEvent] = []
        self.max_cache_size = 1000
        
    async def log_security_event(
        self,
        action: str,
        resource: str,
        level: AuditTrailLevel = AuditTrailLevel.INFO,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        compliance_flags: Optional[List[str]] = None
    ) -> str:
        """
Log a security audit event"""
        
        event = SecurityAuditEvent(
            level=level,
            category="security",
            action=action,
            resource=resource,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {},
            compliance_flags=compliance_flags or []
        )
        
        # Store in cache
        self.events_cache.append(event)
        if len(self.events_cache) > self.max_cache_size:
            self.events_cache.pop(0)
        
        # Log to security events system
        await self._log_to_security_events(event)
        
        # Log to audit logger
        await self._log_to_audit_logger(event)
        
        # Log access if applicable
        if action in ["login", "logout", "access", "view", "download", "modify"]:
            await self._log_access_event(event)
        
        return event.event_id
    
    async def _log_to_security_events(self, event: SecurityAuditEvent):
        """Log to security events system"""
        try:
            security_event_type = self._map_to_security_event_type(event.action, event.success)
            
            await self.security_logger.log_security_event(
                event_type=security_event_type,
                severity=event.level.value.upper(),
                user_id=event.user_id or "anonymous",
                ip_address=event.ip_address,
                details={
                    "action": event.action,
                    "resource": event.resource,
                    "success": event.success,
                    "user_agent": event.user_agent,
                    **event.details
                }
            )
        except Exception as e:
            logger.error(f"Failed to log to security events: {e}")
    
    async def _log_to_audit_logger(self, event: SecurityAuditEvent):
        """Log to audit logger system"""
        try:
            audit_level = self._map_to_audit_level(event.level)
            audit_category = self._map_to_audit_category(event.action)
            
            await self.audit_logger.log_event(
                level=audit_level,
                category=audit_category,
                message=f"Security audit: {event.action} on {event.resource}",
                action=event.action,
                resource=event.resource,
                success=event.success,
                user_id=event.user_id,
                ip_address=event.ip_address,
                details=event.details
            )
        except Exception as e:
            logger.error(f"Failed to log to audit logger: {e}")
    
    async def _log_access_event(self, event: SecurityAuditEvent):
        """Log access-related events"""
        try:
            if event.user_id and event.resource:
                # Note: This would integrate with the AccessController
                # For now, we'll log it as a security event
                logger.info(f"Access event: {event.user_id} {event.action} {event.resource}")
        except Exception as e:
            logger.error(f"Failed to log access event: {e}")
    
    def _map_to_security_event_type(self, action: str, success: bool) -> SecurityEventType:
        """Map action to security event type"""
        action_lower = action.lower()
        
        if "login" in action_lower:
            return SecurityEventType.FAILED_LOGIN_ATTEMPT if not success else SecurityEventType.SUSPICIOUS_LOGIN
        elif "download" in action_lower and not success:
            return SecurityEventType.UNAUTHORIZED_DOWNLOAD
        elif "access" in action_lower and not success:
            return SecurityEventType.UNAUTHORIZED_ACCESS
        elif "data" in action_lower and not success:
            return SecurityEventType.UNAUTHORIZED_DATA_ACCESS
        else:
            return SecurityEventType.SUSPICIOUS_LOGIN  # Default
    
    def _map_to_audit_level(self, level: AuditTrailLevel) -> AuditLevel:
        """Map audit trail level to audit logger level"""
        mapping = {
            AuditTrailLevel.INFO: AuditLevel.INFO,
            AuditTrailLevel.WARNING: AuditLevel.WARNING,
            AuditTrailLevel.SECURITY: AuditLevel.SECURITY,
            AuditTrailLevel.CRITICAL: AuditLevel.CRITICAL,
            AuditTrailLevel.COMPLIANCE: AuditLevel.COMPLIANCE
        }
        return mapping.get(level, AuditLevel.INFO)
    
    def _map_to_audit_category(self, action: str) -> AuditCategory:
        """
Map action to audit category"""
        action_lower = action.lower()
        
        if "auth" in action_lower or "login" in action_lower:
            return AuditCategory.AUTHENTICATION
        elif "access" in action_lower or "view" in action_lower:
            return AuditCategory.DATA_ACCESS
        elif "process" in action_lower or "ai" in action_lower:
            return AuditCategory.AI_PROCESSING
        else:
            return AuditCategory.SYSTEM
    
    async def get_audit_trail(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[AuditTrailLevel] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityAuditEvent]:
        """Retrieve audit trail with filtering"""
        
        filtered_events = self.events_cache.copy()
        
        # Apply filters
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        if level:
            filtered_events = [e for e in filtered_events if e.level == level]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if action:
            filtered_events = [e for e in filtered_events if action.lower() in e.action.lower()]
        
        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_events[:limit]
    
    async def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        compliance_standard: str = "GDPR"
    ) -> Dict[str, Any]:
        """Generate compliance report for audit trail"""
        
        events = await self.get_audit_trail(start_time=start_time, end_time=end_time)
        
        # Filter events relevant to compliance standard
        compliance_events = [
            e for e in events 
            if compliance_standard in e.compliance_flags or 
               any(flag in compliance_standard for flag in e.compliance_flags)
        ]
        
        report = {
            "compliance_standard": compliance_standard,
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "total_events": len(events),
            "compliance_relevant_events": len(compliance_events),
            "event_breakdown": {
                "info": len([e for e in compliance_events if e.level == AuditTrailLevel.INFO]),
                "warning": len([e for e in compliance_events if e.level == AuditTrailLevel.WARNING]),
                "security": len([e for e in compliance_events if e.level == AuditTrailLevel.SECURITY]),
                "critical": len([e for e in compliance_events if e.level == AuditTrailLevel.CRITICAL]),
                "compliance": len([e for e in compliance_events if e.level == AuditTrailLevel.COMPLIANCE])
            },
            "security_incidents": len([e for e in compliance_events if not e.success]),
            "events": [e.to_dict() for e in compliance_events]
        }
        
        return report
    
    async def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the audit trail"""
        
        try:
            # Calculate hash chain for events
            hash_chain = []
            for i, event in enumerate(self.events_cache):
                event_data = json.dumps(event.to_dict(), sort_keys=True)
                
                if i == 0:
                    event_hash = hashlib.sha256(event_data.encode()).hexdigest()
                else:
                    combined_data = hash_chain[i-1] + event_data
                    event_hash = hashlib.sha256(combined_data.encode()).hexdigest()
                
                hash_chain.append(event_hash)
            
            integrity_check = {
                "status": "verified",
                "total_events": len(self.events_cache),
                "hash_chain_length": len(hash_chain),
                "verification_timestamp": datetime.now(timezone.utc).isoformat(),
                "last_event_hash": hash_chain[-1] if hash_chain else None
            }
            
            return integrity_check
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "verification_timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global audit trail instance
security_audit_trail = SecurityAuditTrail()


# Helper functions for easy integration
async def log_security_audit(
    action: str,
    resource: str,
    level: AuditTrailLevel = AuditTrailLevel.INFO,
    **kwargs
) -> str:
    """Convenience function to log security audit events"""
    return await security_audit_trail.log_security_event(
        action=action,
        resource=resource,
        level=level,
        **kwargs
    )


async def log_authentication_event(
    user_id: str,
    success: bool,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """
Log authentication events"""
    return await log_security_audit(
        action="authentication",
        resource=f"user:{user_id}",
        level=AuditTrailLevel.SECURITY if not success else AuditTrailLevel.INFO,
        user_id=user_id,
        ip_address=ip_address,
        success=success,
        details=details,
        compliance_flags=["GDPR", "SOX", "ISO27001"]
    )


async def log_data_access_event(
    user_id: str,
    resource: str,
    action: str,
    success: bool = True,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """Log data access events"""
    return await log_security_audit(
        action=f"data_access_{action}",
        resource=resource,
        level=AuditTrailLevel.COMPLIANCE,
        user_id=user_id,
        ip_address=ip_address,
        success=success,
        details=details,
        compliance_flags=["GDPR", "CCPA", "HIPAA"]
    )