"""IA Influencer Agent - Enterprise Audit Logger
Comprehensive audit logging system for compliance and security

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, text
from fastapi import Request, HTTPException
from contextvars import ContextVar

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.audit import AuditLog, SecurityEvent, ComplianceLog
from backend.core.security import hash_sensitive_data, encrypt_audit_data
from backend.utils.encryption import generate_audit_signature
from backend.core.logging import get_logger

logger = get_logger(__name__)


class AuditLevel(str, Enum):
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class AuditCategory(str, Enum):
    """Audit event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_OPERATION = "system_operation"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    CONTENT_PROTECTION = "content_protection"
    FINANCIAL = "financial"
    USER_ACTIVITY = "user_activity"
    API_ACCESS = "api_access"
    ADMIN_ACTION = "admin_action"


class ComplianceFramework(str, Enum):
    """Compliance frameworks for audit mapping"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    DMCA = "dmca"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"


@dataclass
class AuditContext:
    """Audit context information"""
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    transaction_id: Optional[str] = None
    correlation_id: Optional[str] = None


@dataclass
class SecurityContext:
    """Security event context"""
    threat_level: str
    attack_type: Optional[str] = None
    source_ip: Optional[str] = None
    target_resource: Optional[str] = None
    attack_signature: Optional[str] = None
    mitigation_action: Optional[str] = None


@dataclass
class ComplianceContext:
    """Compliance audit context"""
    framework: ComplianceFramework
    regulation_section: str
    control_objective: str
    assessment_result: str
    remediation_required: bool = False


# Context variables for request-scoped audit context
audit_context: ContextVar[Optional[AuditContext]] = ContextVar('audit_context', default=None)
request_correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class AuditLogger:
    """Enterprise-grade audit logging system"""
    
    def __init__(self):
        self.logger = logger
        self.encryption_enabled = settings.AUDIT_ENCRYPTION_ENABLED
        self.retention_days = settings.AUDIT_RETENTION_DAYS
        self.tamper_protection = settings.AUDIT_TAMPER_PROTECTION
        self.real_time_alerts = settings.AUDIT_REAL_TIME_ALERTS
        
        # Compliance mapping for audit events
        self.compliance_mapping = {
            "user_data_access": [ComplianceFramework.GDPR, ComplianceFramework.CCPA],
            "financial_transaction": [ComplianceFramework.PCI_DSS, ComplianceFramework.SOX],
            "content_upload": [ComplianceFramework.DMCA],
            "security_incident": [ComplianceFramework.ISO27001],
            "data_breach": [ComplianceFramework.GDPR, ComplianceFramework.CCPA, ComplianceFramework.ISO27001]
        }
    
    async def log_audit_event(
        self,
        event_type: str,
        category: AuditCategory,
        level: AuditLevel,
        message: str,
        details: Dict[str, Any],
        user_id: Optional[int] = None,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log comprehensive audit event with full context"""
        try:
            # Get or create audit context
            audit_ctx = context or audit_context.get() or AuditContext()
            correlation_id = request_correlation_id.get() or self._generate_correlation_id()
            
            # Generate event ID
            event_id = self._generate_event_id(event_type, correlation_id)
            
            # Prepare audit data
            audit_data = {
                "event_id": event_id,
                "event_type": event_type,
                "category": category.value,
                "level": level.value,
                "message": message,
                "details": details,
                "user_id": user_id or audit_ctx.user_id,
                "session_id": audit_ctx.session_id,
                "ip_address": audit_ctx.ip_address,
                "user_agent": audit_ctx.user_agent,
                "request_id": audit_ctx.request_id,
                "correlation_id": correlation_id,
                "resource_id": resource_id,
                "resource_type": resource_type,
                "timestamp": datetime.utcnow(),
                "server_timestamp": datetime.utcnow(),
                "timezone": "UTC"
            }
            
            # Add security context if available
            if hasattr(details, 'security_context'):
                audit_data.update(details.pop('security_context', {}))
            
            # Encrypt sensitive data if enabled
            if self.encryption_enabled:
                audit_data = await self._encrypt_audit_data(audit_data)
            
            # Generate tamper protection signature
            if self.tamper_protection:
                audit_data["integrity_hash"] = await self._generate_integrity_hash(audit_data)
            
            # Store audit log
            async with get_db_session() as session:
                audit_log = AuditLog(
                    event_id=event_id,
                    event_type=event_type,
                    category=category.value,
                    level=level.value,
                    message=message,
                    details=json.dumps(audit_data["details"]),
                    user_id=audit_data["user_id"],
                    session_id=audit_data["session_id"],
                    ip_address=audit_data["ip_address"],
                    user_agent=audit_data["user_agent"],
                    request_id=audit_data["request_id"],
                    correlation_id=correlation_id,
                    resource_id=resource_id,
                    resource_type=resource_type,
                    timestamp=audit_data["timestamp"],
                    integrity_hash=audit_data.get("integrity_hash"),
                    encrypted=self.encryption_enabled
                )
                
                session.add(audit_log)
                await session.commit()
            
            # Check compliance requirements
            await self._process_compliance_requirements(event_type, audit_data)
            
            # Send real-time alerts if configured
            if self.real_time_alerts and level in [AuditLevel.ERROR, AuditLevel.CRITICAL, AuditLevel.SECURITY]:
                await self._send_real_time_alert(audit_data)
            
            self.logger.debug(f"Audit event logged: {event_id}")
            return event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {str(e)}")
            # Ensure audit failures are logged to system logs
            self.logger.critical(f"AUDIT FAILURE: {event_type} - {message}")
            raise
    
    async def log_security_event(
        self,
        event_type: str,
        threat_level: str,
        message: str,
        security_context: SecurityContext,
        details: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """Log security-specific events with enhanced context"""
        try:
            event_id = await self.log_audit_event(
                event_type=event_type,
                category=AuditCategory.SECURITY,
                level=AuditLevel.SECURITY,
                message=message,
                details={
                    **details,
                    "threat_level": threat_level,
                    "attack_type": security_context.attack_type,
                    "source_ip": security_context.source_ip,
                    "target_resource": security_context.target_resource,
                    "attack_signature": security_context.attack_signature,
                    "mitigation_action": security_context.mitigation_action
                },
                user_id=user_id
            )
            
            # Store additional security event data
            async with get_db_session() as session:
                security_event = SecurityEvent(
                    event_id=event_id,
                    threat_level=threat_level,
                    attack_type=security_context.attack_type,
                    source_ip=security_context.source_ip,
                    target_resource=security_context.target_resource,
                    attack_signature=security_context.attack_signature,
                    mitigation_action=security_context.mitigation_action,
                    timestamp=datetime.utcnow(),
                    resolved=False
                )
                
                session.add(security_event)
                await session.commit()
            
            # Trigger security incident response if critical
            if threat_level in ["high", "critical"]:
                await self._trigger_security_incident_response(event_id, security_context)
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")
            raise
    
    async def log_compliance_event(
        self,
        event_type: str,
        framework: ComplianceFramework,
        regulation_section: str,
        control_objective: str,
        assessment_result: str,
        details: Dict[str, Any],
        remediation_required: bool = False,
        user_id: Optional[int] = None
    ) -> str:
        """Log compliance-specific events for regulatory audit trails"""
        try:
            event_id = await self.log_audit_event(
                event_type=event_type,
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.WARNING if remediation_required else AuditLevel.INFO,
                message=f"Compliance assessment: {framework.value} - {regulation_section}",
                details={
                    **details,
                    "framework": framework.value,
                    "regulation_section": regulation_section,
                    "control_objective": control_objective,
                    "assessment_result": assessment_result,
                    "remediation_required": remediation_required
                },
                user_id=user_id
            )
            
            # Store compliance-specific data
            async with get_db_session() as session:
                compliance_log = ComplianceLog(
                    event_id=event_id,
                    framework=framework.value,
                    regulation_section=regulation_section,
                    control_objective=control_objective,
                    assessment_result=assessment_result,
                    remediation_required=remediation_required,
                    assessment_date=datetime.utcnow(),
                    next_assessment_date=datetime.utcnow() + timedelta(days=90),
                    assessor_id="system"
                )
                
                session.add(compliance_log)
                await session.commit()
            
            # Schedule remediation if required
            if remediation_required:
                await self._schedule_compliance_remediation(event_id, framework, regulation_section)
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Failed to log compliance event: {str(e)}")
            raise
    
    async def log_data_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        access_type: str,
        success: bool,
        details: Dict[str, Any] = None
    ) -> str:
        """Log data access events for privacy compliance"""
        try:
            return await self.log_audit_event(
                event_type="data_access",
                category=AuditCategory.DATA_ACCESS,
                level=AuditLevel.INFO if success else AuditLevel.WARNING,
                message=f"Data access: {access_type} on {resource_type}",
                details={
                    "access_type": access_type,
                    "success": success,
                    "query_time": datetime.utcnow().isoformat(),
                    **(details or {})
                },
                user_id=user_id,
                resource_id=resource_id,
                resource_type=resource_type
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log data access: {str(e)}")
            raise
    
    async def log_financial_transaction(
        self,
        user_id: int,
        transaction_id: str,
        transaction_type: str,
        amount: float,
        currency: str,
        success: bool,
        details: Dict[str, Any] = None
    ) -> str:
        """Log financial transactions for audit and compliance"""
        try:
            return await self.log_audit_event(
                event_type="financial_transaction",
                category=AuditCategory.FINANCIAL,
                level=AuditLevel.INFO if success else AuditLevel.ERROR,
                message=f"Financial transaction: {transaction_type}",
                details={
                    "transaction_type": transaction_type,
                    "amount": amount,
                    "currency": currency,
                    "success": success,
                    "transaction_time": datetime.utcnow().isoformat(),
                    **(details or {})
                },
                user_id=user_id,
                resource_id=transaction_id,
                resource_type="financial_transaction"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log financial transaction: {str(e)}")
            raise
    
    async def generate_audit_report(
        self,
        start_date: datetime,
        end_date: datetime,
        category_filter: Optional[AuditCategory] = None,
        user_filter: Optional[int] = None,
        compliance_framework: Optional[ComplianceFramework] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report for specified period"""
        try:
            async with get_db_session() as session:
                # Build query with filters
                query = select(AuditLog).where(
                    AuditLog.timestamp >= start_date,
                    AuditLog.timestamp <= end_date
                )
                
                if category_filter:
                    query = query.where(AuditLog.category == category_filter.value)
                
                if user_filter:
                    query = query.where(AuditLog.user_id == user_filter)
                
                result = await session.execute(query)
                audit_logs = result.scalars().all()
                
                # Generate report statistics
                report = {
                    "report_period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    },
                    "filters": {
                        "category": category_filter.value if category_filter else None,
                        "user_id": user_filter,
                        "compliance_framework": compliance_framework.value if compliance_framework else None
                    },
                    "statistics": {
                        "total_events": len(audit_logs),
                        "events_by_category": {},
                        "events_by_level": {},
                        "events_by_hour": {},
                        "unique_users": set(),
                        "unique_resources": set()
                    },
                    "compliance_events": [],
                    "security_events": [],
                    "high_risk_events": [],
                    "data_integrity": {
                        "verified_events": 0,
                        "integrity_failures": 0
                    }
                }
                
                # Process audit logs
                for log in audit_logs:
                    # Category statistics
                    category = log.category
                    report["statistics"]["events_by_category"][category] = \
                        report["statistics"]["events_by_category"].get(category, 0) + 1
                    
                    # Level statistics
                    level = log.level
                    report["statistics"]["events_by_level"][level] = \
                        report["statistics"]["events_by_level"].get(level, 0) + 1
                    
                    # Hourly statistics
                    hour = log.timestamp.strftime("%Y-%m-%d %H:00")
                    report["statistics"]["events_by_hour"][hour] = \
                        report["statistics"]["events_by_hour"].get(hour, 0) + 1
                    
                    # Unique users and resources
                    if log.user_id:
                        report["statistics"]["unique_users"].add(log.user_id)
                    if log.resource_id:
                        report["statistics"]["unique_resources"].add(log.resource_id)
                    
                    # Check data integrity
                    if log.integrity_hash:
                        is_valid = await self._verify_integrity_hash(log)
                        if is_valid:
                            report["data_integrity"]["verified_events"] += 1
                        else:
                            report["data_integrity"]["integrity_failures"] += 1
                    
                    # Categorize special events
                    if log.category == AuditCategory.COMPLIANCE.value:
                        report["compliance_events"].append({
                            "event_id": log.event_id,
                            "timestamp": log.timestamp.isoformat(),
                            "message": log.message
                        })
                    
                    if log.category == AuditCategory.SECURITY.value:
                        report["security_events"].append({
                            "event_id": log.event_id,
                            "timestamp": log.timestamp.isoformat(),
                            "level": log.level,
                            "message": log.message
                        })
                    
                    if log.level in [AuditLevel.ERROR.value, AuditLevel.CRITICAL.value]:
                        report["high_risk_events"].append({
                            "event_id": log.event_id,
                            "timestamp": log.timestamp.isoformat(),
                            "category": log.category,
                            "level": log.level,
                            "message": log.message
                        })
                
                # Convert sets to counts
                report["statistics"]["unique_users"] = len(report["statistics"]["unique_users"])
                report["statistics"]["unique_resources"] = len(report["statistics"]["unique_resources"])
                
                # Add compliance framework specific events if requested
                if compliance_framework:
                    compliance_events = await self._get_compliance_framework_events(
                        session, start_date, end_date, compliance_framework
                    )
                    report["compliance_framework_events"] = compliance_events
                
                self.logger.info(f"Audit report generated: {len(audit_logs)} events")
                return report
                
        except Exception as e:
            self.logger.error(f"Failed to generate audit report: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate audit report")
    
    def set_audit_context(self, context: AuditContext) -> None:
        """Set audit context for current request"""
        audit_context.set(context)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracking"""
        request_correlation_id.set(correlation_id)
    
    async def _encrypt_audit_data(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive audit data"""
        try:
            sensitive_fields = ["user_agent", "ip_address", "details"]
            encrypted_data = audit_data.copy()
            
            for field in sensitive_fields:
                if field in encrypted_data and encrypted_data[field]:
                    encrypted_data[field] = await encrypt_audit_data(str(encrypted_data[field]))
            
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt audit data: {str(e)}")
            return audit_data
    
    async def _generate_integrity_hash(self, audit_data: Dict[str, Any]) -> str:
        """Generate tamper-proof integrity hash for audit data"""
        try:
            # Create consistent string representation
            hash_data = {
                "event_id": audit_data["event_id"],
                "timestamp": audit_data["timestamp"].isoformat(),
                "event_type": audit_data["event_type"],
                "message": audit_data["message"],
                "user_id": audit_data["user_id"]
            }
            
            hash_string = json.dumps(hash_data, sort_keys=True)
            return hashlib.sha256(hash_string.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to generate integrity hash: {str(e)}")
            return ""
    
    async def _verify_integrity_hash(self, audit_log: AuditLog) -> bool:
        """Verify integrity hash of audit log entry"""
        try:
            if not audit_log.integrity_hash:
                return True  # No hash to verify
            
            # Recreate hash with current data
            hash_data = {
                "event_id": audit_log.event_id,
                "timestamp": audit_log.timestamp.isoformat(),
                "event_type": audit_log.event_type,
                "message": audit_log.message,
                "user_id": audit_log.user_id
            }
            
            hash_string = json.dumps(hash_data, sort_keys=True)
            calculated_hash = hashlib.sha256(hash_string.encode()).hexdigest()
            
            return calculated_hash == audit_log.integrity_hash
            
        except Exception as e:
            self.logger.error(f"Failed to verify integrity hash: {str(e)}")
            return False
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for request tracking"""
        timestamp = str(int(datetime.utcnow().timestamp() * 1000))
        random_part = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"COR-{timestamp}-{random_part}"
    
    def _generate_event_id(self, event_type: str, correlation_id: str) -> str:
        """Generate unique event ID"""
        timestamp = str(int(datetime.utcnow().timestamp() * 1000))
        hash_part = hashlib.md5(f"{event_type}-{correlation_id}-{timestamp}".encode()).hexdigest()[:8]
        return f"AUD-{timestamp}-{hash_part}"
    
    async def _process_compliance_requirements(self, event_type: str, audit_data: Dict[str, Any]) -> None:
        """Process compliance requirements for audit event"""
        try:
            # Check if event type requires compliance logging
            compliance_frameworks = self.compliance_mapping.get(event_type, [])
            
            for framework in compliance_frameworks:
                await self._create_compliance_record(framework, event_type, audit_data)
            
        except Exception as e:
            self.logger.error(f"Failed to process compliance requirements: {str(e)}")
    
    async def _send_real_time_alert(self, audit_data: Dict[str, Any]) -> None:
        """Send real-time alert for critical audit events"""
        try:
            # Implementation would integrate with alerting system
            # (email, Slack, PagerDuty, etc.)
            self.logger.warning(f"REAL-TIME ALERT: {audit_data['event_type']} - {audit_data['message']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send real-time alert: {str(e)}")


# Export for use in other modules
__all__ = ["AuditLogger", "AuditLevel", "AuditCategory", "AuditContext", "SecurityContext", "ComplianceContext"]
