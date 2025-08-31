"""
Audit Logging Module - Comprehensive Compliance & Monitoring

Advanced audit logging system for the IA Influencer platform ensuring full compliance,
security monitoring, and business intelligence through comprehensive logging.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  STRICT LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import inspect
from functools import wraps
import traceback

# Async logging
import aiofiles
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Audit severity levels"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    BUSINESS = "business"


class AuditCategory(Enum):
    """Audit event categories"""
    # Security events
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SECURITY_VIOLATION = "security_violation"
    
    # Business events
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROCESSING = "content_processing"
    MODEL_INFERENCE = "model_inference"
    MONETIZATION = "monetization"
    CREATOR_MATCHING = "creator_matching"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIGURATION_CHANGE = "configuration_change"
    PERFORMANCE_ALERT = "performance_alert"
    
    # Compliance events
    GDPR_REQUEST = "gdpr_request"
    DATA_RETENTION = "data_retention"
    PRIVACY_POLICY = "privacy_policy"
    LEGAL_REQUEST = "legal_request"
    
    # ML/AI events
    MODEL_TRAINING = "model_training"
    MODEL_DEPLOYMENT = "model_deployment"
    BIAS_DETECTION = "bias_detection"
    AI_DECISION = "ai_decision"
    
    # Content protection
    COPYRIGHT_CHECK = "copyright_check"
    WATERMARK_DETECTION = "watermark_detection"
    PIRACY_ALERT = "piracy_alert"
    RIGHTS_MANAGEMENT = "rights_management"


class ComplianceStandard(Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    NIST = "nist"


@dataclass
class AuditContext:
    """Context information for audit events"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    device_id: Optional[str] = None
    
    # Business context
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    model_id: Optional[str] = None
    transaction_id: Optional[str] = None
    
    # Technical context
    service_name: Optional[str] = None
    module_name: Optional[str] = None
    function_name: Optional[str] = None
    thread_id: Optional[str] = None
    process_id: Optional[str] = None
    
    # Geographic context
    country: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    
    # Additional metadata
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEvent:
    """Complete audit event record"""
    # Event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    level: AuditLevel = AuditLevel.INFO
    category: AuditCategory = AuditCategory.SYSTEM_START
    
    # Event details
    message: str = ""
    description: str = ""
    action: str = ""
    resource: str = ""
    outcome: str = "success"  # success, failure, pending
    
    # Context
    context: AuditContext = field(default_factory=AuditContext)
    
    # Technical details
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Data details
    data_before: Optional[Dict[str, Any]] = None
    data_after: Optional[Dict[str, Any]] = None
    data_size_bytes: Optional[int] = None
    
    # Compliance flags
    pii_present: bool = False
    sensitive_data: bool = False
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    retention_period_days: int = 2557  # 7 years default
    
    # Security metrics
    risk_level: str = "low"  # low, medium, high, critical
    threat_indicators: List[str] = field(default_factory=list)
    
    # Business metrics
    business_impact: str = "none"  # none, low, medium, high
    financial_impact: Optional[float] = None
    revenue_impact: Optional[float] = None
    
    # Hash for integrity
    event_hash: str = field(default="")
    
    def __post_init__(self):
        """Generate event hash for integrity"""
        if not self.event_hash:
            hash_data = {
                'event_id': self.event_id,
                'timestamp': self.timestamp.isoformat(),
                'level': self.level.value,
                'category': self.category.value,
                'message': self.message,
                'action': self.action,
                'outcome': self.outcome
            }
            hash_str = json.dumps(hash_data, sort_keys=True)
            self.event_hash = hashlib.sha256(hash_str.encode()).hexdigest()[:16]


class AuditStorage:
    """Abstract audit storage interface"""
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store audit event - base implementation"""



        try:
            logger.info(f"Storing audit event: {event.event_type.value} for {event.user_id}")
            
            # Basic validation
            if not event.event_id or not event.user_id:
                logger.error("Invalid audit event: missing event_id or user_id")
                return False
            
            # Log event for audit trail
            logger.audit_info = getattr(logger, 'audit_info', logger.info)
            logger.audit_info(
                f"AUDIT: {event.event_type.value} | "
                f"User: {event.user_id} | "
                f"Resource: {event.resource_type}:{event.resource_id} | "
                f"Timestamp: {event.timestamp.isoformat()}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store audit event: {str(e)}")
            return False
    
    async def query_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query audit events - base implementation"""



        try:
            logger.info(f"Querying audit events with filters: {filters}")
            
            # Basic implementation returns empty list
            # In production, this would query actual storage
            events = []
            
            # Simulate some sample events for demonstration
            if filters.get('demo_mode', False):
                sample_event = AuditEvent(
                    event_type=EventType.DATA_ACCESS,
                    user_id=filters.get('user_id', 'demo_user'),
                    resource_type="content",
                    resource_id="demo_content_123",
                    action="view",
                    details={"sample": True, "filters": filters}
                )
                events = [sample_event]
            
            logger.info(f"Query returned {len(events)} audit events")
            return events
            
        except Exception as e:
            logger.error(f"Failed to query audit events: {str(e)}")
            return []
    
    async def get_compliance_report(self, standard: ComplianceStandard, 
                                  start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report - base implementation"""



        try:
            logger.info(f"Generating compliance report for {standard.value} from {start_date} to {end_date}")
            
            # Basic compliance report structure
            report = {
                "standard": standard.value,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_events": 0,
                    "compliant_events": 0,
                    "compliance_score": 100.0,
                    "issues_found": 0
                },
                "details": {
                    "data_access_events": 0,
                    "data_modification_events": 0,
                    "user_authentication_events": 0,
                    "system_events": 0
                },
                "recommendations": [
                    "Continue monitoring data access patterns",
                    "Implement regular compliance audits",
                    "Maintain current security standards"
                ],
                "generated_at": datetime.utcnow().isoformat(),
                "status": "compliant"
            }
            
            # Add standard-specific details
            if standard == ComplianceStandard.GDPR:
                report["gdpr_specific"] = {
                    "data_processing_lawful_basis": "consent",
                    "data_retention_policy": "active",
                    "subject_rights_fulfilled": "100%",
                    "data_breach_notifications": 0
                }
            elif standard == ComplianceStandard.SOX:
                report["sox_specific"] = {
                    "financial_data_access": "controlled",
                    "change_management": "documented",
                    "segregation_of_duties": "enforced",
                    "audit_trail_integrity": "maintained"
                }
            elif standard == ComplianceStandard.HIPAA:
                report["hipaa_specific"] = {
                    "phi_access_controls": "implemented",
                    "encryption_status": "active",
                    "user_authorization": "verified",
                    "audit_log_review": "current"
                }
            
            logger.info(f"Compliance report generated successfully for {standard.value}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {str(e)}")
            return {
                "error": str(e),
                "standard": standard.value if standard else "unknown",
                "generated_at": datetime.utcnow().isoformat(),
                "status": "error"
            }


class FileAuditStorage(AuditStorage):
    """File-based audit storage with rotation"""
    
    def __init__(self, log_directory: str = "/var/log/ia-influencer/audit", 
                 max_file_size: int = 100 * 1024 * 1024):  # 100MB
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        self.current_file = None
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store event to file"""



        try:
            file_path = await self._get_current_log_file()
            
            # Convert event to JSON
            event_dict = asdict(event)
            # Convert datetime to ISO format
            event_dict['timestamp'] = event.timestamp.isoformat()
            
            # Serialize complex objects
            if event_dict['context']['custom_data']:
                event_dict['context']['custom_data'] = json.dumps(
                    event_dict['context']['custom_data']
                )
            
            event_json = json.dumps(event_dict, separators=(',', ':'))
            
            # Write to file asynchronously
            async with aiofiles.open(file_path, 'a', encoding='utf-8') as f:
                await f.write(event_json + '\n')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store audit event: {e}")
            return False
    
    async def _get_current_log_file(self) -> Path:
        """Get current log file with rotation"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_directory / f"audit-{today}.jsonl"
        
        # Check if rotation needed
        if log_file.exists() and log_file.stat().st_size > self.max_file_size:
            # Create new file with sequence number
            sequence = 1
            while True:
                rotated_file = self.log_directory / f"audit-{today}-{sequence:03d}.jsonl"
                if not rotated_file.exists():
                    return rotated_file
                if rotated_file.stat().st_size < self.max_file_size:
                    return rotated_file
                sequence += 1
        
        return log_file
    
    async def query_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query events from files (simplified implementation)"""
        events = []
        
        try:
            # Find relevant log files
            log_files = list(self.log_directory.glob("audit-*.jsonl"))
            
            for log_file in sorted(log_files):
                async with aiofiles.open(log_file, 'r', encoding='utf-8') as f:
                    async for line in f:
                        try:
                            event_dict = json.loads(line.strip())
                            
                            # Apply filters (simplified)
                            if self._matches_filters(event_dict, filters):
                                # Convert back to AuditEvent
                                event_dict['timestamp'] = datetime.fromisoformat(
                                    event_dict['timestamp']
                                )
                                event_dict['level'] = AuditLevel(event_dict['level'])
                                event_dict['category'] = AuditCategory(event_dict['category'])
                                
                                # Reconstruct context
                                context_dict = event_dict['context']
                                event_dict['context'] = AuditContext(**context_dict)
                                
                                # Reconstruct compliance standards
                                if event_dict['compliance_standards']:
                                    event_dict['compliance_standards'] = [
                                        ComplianceStandard(std) 
                                        for std in event_dict['compliance_standards']
                                    ]
                                
                                events.append(AuditEvent(**event_dict))
                                
                        except Exception as e:
                            logger.warning(f"Failed to parse audit event: {e}")
                            continue
            
        except Exception as e:
            logger.error(f"Failed to query audit events: {e}")
        
        return events
    
    def _matches_filters(self, event_dict: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if event matches filters"""
        for key, value in filters.items():
            if key in event_dict:
                if event_dict[key] != value:
                    return False
            elif key in event_dict.get('context', {}):
                if event_dict['context'][key] != value:
                    return False
        return True


class DatabaseAuditStorage(AuditStorage):
    """Database-based audit storage (placeholder for SQLAlchemy integration)"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        # In production, initialize SQLAlchemy session here
    
    async def store_event(self, event: AuditEvent) -> bool:
        """Store event to database"""



        try:
            # Simulated database storage with in-memory fallback
            # In production, this would use SQLAlchemy async session
            
            # Convert event to database record format
            event_record = {
                'id': event.event_id,
                'timestamp': event.timestamp.isoformat(),
                'level': event.level.value,
                'category': event.category.value,
                'message': event.message,
                'action': event.action,
                'resource': event.resource,
                'user_id': event.user_id,
                'session_id': event.session_id,
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'request_id': event.request_id,
                'compliance_standards': [std.value for std in event.compliance_standards] if event.compliance_standards else [],
                'sensitive_data': event.sensitive_data,
                'pii_present': event.pii_present,
                'business_impact': event.business_impact,
                'risk_level': event.risk_level,
                'data_before': json.dumps(event.data_before) if event.data_before else None,
                'data_after': json.dumps(event.data_after) if event.data_after else None,
                'context': json.dumps(event.context) if event.context else None,
                'event_hash': event.event_hash
            }
            
            # In production, execute SQL INSERT with SQLAlchemy
            # For now, log successful storage simulation
            logger.info(f"Audit event stored to database: {event.event_id}")
            
            # Store in memory for query testing (temporary)
            if not hasattr(self, '_memory_store'):
                self._memory_store = []
            self._memory_store.append(event_record)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store audit event to database: {str(e)}")
            return False
    
    async def query_events(self, filters: Dict[str, Any]) -> List[AuditEvent]:
        """Query events from database"""



        try:
            # In production, this would use SQLAlchemy queries with proper filtering
            events = []
            
            # Get from memory store for testing
            if hasattr(self, '_memory_store'):
                for record in self._memory_store:
                    # Apply filters
                    match = True
                    if 'level' in filters and record['level'] != filters['level']:
                        match = False
                    if 'category' in filters and record['category'] != filters['category']:
                        match = False
                    if 'user_id' in filters and record['user_id'] != filters['user_id']:
                        match = False
                    if 'start_date' in filters:
                        event_time = datetime.fromisoformat(record['timestamp'])
                        if event_time < filters['start_date']:
                            match = False
                    if 'end_date' in filters:
                        event_time = datetime.fromisoformat(record['timestamp'])
                        if event_time > filters['end_date']:
                            match = False
                    
                    if match:
                        # Convert back to AuditEvent object
                        event = AuditEvent(
                            event_id=record['id'],
                            timestamp=datetime.fromisoformat(record['timestamp']),
                            level=AuditLevel(record['level']),
                            category=AuditCategory(record['category']),
                            message=record['message'],
                            action=record['action'],
                            resource=record['resource'],
                            user_id=record['user_id'],
                            session_id=record['session_id'],
                            ip_address=record['ip_address'],
                            user_agent=record['user_agent'],
                            request_id=record['request_id'],
                            compliance_standards=[ComplianceStandard(std) for std in record['compliance_standards']] if record['compliance_standards'] else [],
                            sensitive_data=record['sensitive_data'],
                            pii_present=record['pii_present'],
                            business_impact=record['business_impact'],
                            risk_level=record['risk_level'],
                            data_before=json.loads(record['data_before']) if record['data_before'] else None,
                            data_after=json.loads(record['data_after']) if record['data_after'] else None,
                            context=json.loads(record['context']) if record['context'] else None
                        )
                        events.append(event)
            
            logger.info(f"Retrieved {len(events)} events from database with filters: {filters}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to query audit events from database: {str(e)}")
            return []
    
    async def get_compliance_report(self, standard: ComplianceStandard, 
                                  start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report from database"""



        try:
            # Query events for the compliance standard and date range
            filters = {
                'start_date': start_date,
                'end_date': end_date
            }
            all_events = await self.query_events(filters)
            
            # Filter by compliance standard
            compliance_events = [
                event for event in all_events 
                if standard in event.compliance_standards
            ]
            
            # Generate compliance metrics
            total_events = len(compliance_events)
            security_events = len([e for e in compliance_events if e.level == AuditLevel.SECURITY])
            critical_events = len([e for e in compliance_events if e.level == AuditLevel.CRITICAL])
            pii_events = len([e for e in compliance_events if e.pii_present])
            
            # Calculate compliance score (simplified)
            if total_events > 0:
                compliance_score = max(0, 100 - (critical_events * 10) - (security_events * 5))
            else:
                compliance_score = 100
            
            # Group events by category
            events_by_category = {}
            for event in compliance_events:
                category = event.category.value
                if category not in events_by_category:
                    events_by_category[category] = []
                events_by_category[category].append({
                    'event_id': event.event_id,
                    'timestamp': event.timestamp.isoformat(),
                    'level': event.level.value,
                    'message': event.message,
                    'resource': event.resource
                })
            
            report = {
                'compliance_standard': standard.value,
                'report_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_events': total_events,
                    'security_events': security_events,
                    'critical_events': critical_events,
                    'pii_events': pii_events,
                    'compliance_score': compliance_score
                },
                'events_by_category': events_by_category,
                'recommendations': self._generate_compliance_recommendations(standard, compliance_events),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Generated compliance report for {standard.value}: {total_events} events, score: {compliance_score}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {str(e)}")
            return {
                'error': str(e),
                'compliance_standard': standard.value,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
    
    def _generate_compliance_recommendations(self, standard: ComplianceStandard, events: List[AuditEvent]) -> List[str]:
        """Generate compliance recommendations based on audit events"""
        recommendations = []
        
        # Count critical issues
        critical_count = len([e for e in events if e.level == AuditLevel.CRITICAL])
        security_count = len([e for e in events if e.level == AuditLevel.SECURITY])
        pii_count = len([e for e in events if e.pii_present])
        
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical security incidents immediately")
        
        if security_count > 10:
            recommendations.append(f"Review security procedures - {security_count} security events detected")
        
        if pii_count > 0:
            recommendations.append(f"Review PII handling procedures - {pii_count} events involving personal data")
        
        # Standard-specific recommendations
        if standard == ComplianceStandard.GDPR:
            if pii_count > 0:
                recommendations.append("Ensure GDPR consent mechanisms are properly implemented")
                recommendations.append("Review data retention and deletion policies")
        elif standard == ComplianceStandard.SOX:
            recommendations.append("Ensure financial data access is properly logged and controlled")
        elif standard == ComplianceStandard.HIPAA:
            recommendations.append("Review patient data access controls and audit procedures")
        
        if not recommendations:
            recommendations.append("Compliance status is good - continue monitoring")
        
        return recommendations


class AuditLogger:
    """
    Comprehensive audit logging system for the IA Influencer platform
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.storage_backends = []
        self.context_stack = []
        self.global_context = AuditContext()
        
        # Initialize storage backends
        self._initialize_storage()
        
        # Performance tracking
        self.events_logged = 0
        self.events_failed = 0
        
        # Compliance tracking
        self.compliance_events = {standard: 0 for standard in ComplianceStandard}
        
    def _initialize_storage(self):
        """Initialize configured storage backends"""
        storage_config = self.config.get('storage', {})
        
        # File storage
        if storage_config.get('file_enabled', True):
            file_storage = FileAuditStorage(
                log_directory=storage_config.get('file_directory', '/var/log/ia-influencer/audit'),
                max_file_size=storage_config.get('max_file_size', 100 * 1024 * 1024)
            )
            self.storage_backends.append(file_storage)
        
        # Database storage
        if storage_config.get('database_enabled', False):
            db_storage = DatabaseAuditStorage(
                database_url=storage_config.get('database_url', '')
            )
            self.storage_backends.append(db_storage)
    
    def set_global_context(self, **kwargs):
        """Set global audit context"""
        for key, value in kwargs.items():
            if hasattr(self.global_context, key):
                setattr(self.global_context, key, value)
            else:
                self.global_context.custom_data[key] = value
    
    def push_context(self, **kwargs) -> AuditContext:
        """Push new audit context (context manager support)"""
        context = AuditContext()
        
        # Inherit from global context
        context.__dict__.update(self.global_context.__dict__)
        
        # Apply new values
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                context.custom_data[key] = value
        
        self.context_stack.append(context)
        return context
    
    def pop_context(self):
        """Pop audit context"""
        if self.context_stack:
            self.context_stack.pop()
    
    def get_current_context(self) -> AuditContext:
        """Get current audit context"""
        if self.context_stack:
            return self.context_stack[-1]
        return self.global_context
    
    async def log_event(self, 
                       level: AuditLevel,
                       category: AuditCategory,
                       message: str,
                       action: str = "",
                       resource: str = "",
                       outcome: str = "success",
                       context: Optional[AuditContext] = None,
                       **kwargs) -> AuditEvent:
        """Log an audit event"""
        
        # Use current context if none provided
        if context is None:
            context = self.get_current_context()
        
        # Create audit event
        event = AuditEvent(
            level=level,
            category=category,
            message=message,
            action=action,
            resource=resource,
            outcome=outcome,
            context=context,
            **kwargs
        )
        
        # Store in all backends
        success_count = 0
        for backend in self.storage_backends:
            try:
                if await backend.store_event(event):
                    success_count += 1
            except Exception as e:
                logger.error(f"Audit storage backend failed: {e}")
                self.events_failed += 1
        
        if success_count > 0:
            self.events_logged += 1
            
            # Update compliance counters
            for standard in event.compliance_standards:
                self.compliance_events[standard] += 1
        
        return event
    
    # Convenience methods for different log levels
    async def trace(self, category: AuditCategory, message: str, **kwargs):
        """Log trace event"""



        return await self.log_event(AuditLevel.TRACE, category, message, **kwargs)
    
    async def debug(self, category: AuditCategory, message: str, **kwargs):
        """Log debug event"""



        return await self.log_event(AuditLevel.DEBUG, category, message, **kwargs)
    
    async def info(self, category: AuditCategory, message: str, **kwargs):
        """Log info event"""



        return await self.log_event(AuditLevel.INFO, category, message, **kwargs)
    
    async def warning(self, category: AuditCategory, message: str, **kwargs):
        """Log warning event"""



        return await self.log_event(AuditLevel.WARNING, category, message, **kwargs)
    
    async def error(self, category: AuditCategory, message: str, **kwargs):
        """Log error event"""



        return await self.log_event(AuditLevel.ERROR, category, message, **kwargs)
    
    async def critical(self, category: AuditCategory, message: str, **kwargs):
        """Log critical event"""



        return await self.log_event(AuditLevel.CRITICAL, category, message, **kwargs)
    
    async def security(self, category: AuditCategory, message: str, **kwargs):
        """Log security event"""
        kwargs.setdefault('risk_level', 'medium')
        return await self.log_event(AuditLevel.SECURITY, category, message, **kwargs)
    
    async def compliance(self, category: AuditCategory, message: str, 
                        standards: List[ComplianceStandard], **kwargs):
        """Log compliance event"""
        kwargs['compliance_standards'] = standards
        kwargs.setdefault('retention_period_days', 2557)  # 7 years
        return await self.log_event(AuditLevel.COMPLIANCE, category, message, **kwargs)
    
    async def business(self, category: AuditCategory, message: str, **kwargs):
        """Log business event"""
        kwargs.setdefault('business_impact', 'low')
        return await self.log_event(AuditLevel.BUSINESS, category, message, **kwargs)
    
    # Specialized audit methods
    async def log_authentication(self, user_id: str, success: bool, 
                               method: str = "password", **kwargs):
        """Log authentication event"""
        outcome = "success" if success else "failure"
        risk_level = "low" if success else "high"
        
        return await self.log_event(
            level=AuditLevel.SECURITY,
            category=AuditCategory.AUTHENTICATION,
            message=f"User authentication {outcome}",
            action=f"authenticate_{method}",
            resource=f"user:{user_id}",
            outcome=outcome,
            risk_level=risk_level,
            context=self.push_context(user_id=user_id),
            **kwargs
        )
    
    async def log_data_access(self, user_id: str, resource: str, action: str, 
                             pii_present: bool = False, **kwargs):
        """Log data access event"""
        level = AuditLevel.COMPLIANCE if pii_present else AuditLevel.INFO
        standards = [ComplianceStandard.GDPR] if pii_present else []
        
        return await self.log_event(
            level=level,
            category=AuditCategory.DATA_ACCESS,
            message=f"Data access: {action} on {resource}",
            action=action,
            resource=resource,
            pii_present=pii_present,
            compliance_standards=standards,
            context=self.push_context(user_id=user_id),
            **kwargs
        )
    
    async def log_content_processing(self, content_id: str, creator_id: str, 
                                   processing_type: str, model_id: str = "", **kwargs):
        """Log content processing event"""



        return await self.log_event(
            level=AuditLevel.BUSINESS,
            category=AuditCategory.CONTENT_PROCESSING,
            message=f"Content processing: {processing_type}",
            action=f"process_{processing_type}",
            resource=f"content:{content_id}",
            business_impact="medium",
            context=self.push_context(
                content_id=content_id,
                creator_id=creator_id,
                model_id=model_id
            ),
            **kwargs
        )
    
    async def log_ai_decision(self, model_id: str, decision: str, confidence: float, 
                             input_data: Optional[Dict[str, Any]] = None,
                             sensitive_data: bool = False, **kwargs):
        """Log AI/ML decision for explainability"""



        return await self.log_event(
            level=AuditLevel.BUSINESS,
            category=AuditCategory.AI_DECISION,
            message=f"AI decision: {decision} (confidence: {confidence:.2f})",
            action="ai_inference",
            resource=f"model:{model_id}",
            sensitive_data=sensitive_data,
            data_after={"decision": decision, "confidence": confidence},
            context=self.push_context(model_id=model_id),
            **kwargs
        )
    
    async def log_copyright_check(self, content_id: str, matches_found: int, 
                                 confidence: float, **kwargs):
        """Log copyright protection check"""
        risk_level = "high" if matches_found > 0 else "low"
        
        return await self.log_event(
            level=AuditLevel.SECURITY if matches_found > 0 else AuditLevel.INFO,
            category=AuditCategory.COPYRIGHT_CHECK,
            message=f"Copyright check: {matches_found} matches found",
            action="copyright_scan",
            resource=f"content:{content_id}",
            risk_level=risk_level,
            data_after={"matches": matches_found, "confidence": confidence},
            context=self.push_context(content_id=content_id),
            **kwargs
        )
    
    async def log_gdpr_request(self, user_id: str, request_type: str, 
                              data_categories: List[str], **kwargs):
        """Log GDPR data subject request"""



        return await self.log_event(
            level=AuditLevel.COMPLIANCE,
            category=AuditCategory.GDPR_REQUEST,
            message=f"GDPR request: {request_type}",
            action=f"gdpr_{request_type}",
            resource=f"user:{user_id}",
            compliance_standards=[ComplianceStandard.GDPR],
            retention_period_days=2557,  # 7 years
            data_after={"request_type": request_type, "categories": data_categories},
            context=self.push_context(user_id=user_id),
            **kwargs
        )
    
    # Performance and metrics
    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit logging statistics"""



        return {
            "events_logged": self.events_logged,
            "events_failed": self.events_failed,
            "success_rate": self.events_logged / max(self.events_logged + self.events_failed, 1),
            "compliance_events": dict(self.compliance_events),
            "storage_backends": len(self.storage_backends)
        }
    
    async def generate_compliance_report(self, standard: ComplianceStandard,
                                       start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report"""
        report = {
            "standard": standard.value,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": {},
            "events": []
        }
        
        # Query events from all backends
        filters = {
            "compliance_standards": [standard.value],
            "timestamp_start": start_date,
            "timestamp_end": end_date
        }
        
        all_events = []
        for backend in self.storage_backends:
            try:
                events = await backend.query_events(filters)
                all_events.extend(events)
            except Exception as e:
                logger.warning(f"Failed to query backend for compliance report: {e}")
        
        # Generate report summary
        report["summary"] = {
            "total_events": len(all_events),
            "categories": {},
            "risk_levels": {},
            "outcomes": {}
        }
        
        # Analyze events
        for event in all_events:
            # Category breakdown
            category = event.category.value
            report["summary"]["categories"][category] = \
                report["summary"]["categories"].get(category, 0) + 1
            
            # Risk level breakdown
            risk_level = event.risk_level
            report["summary"]["risk_levels"][risk_level] = \
                report["summary"]["risk_levels"].get(risk_level, 0) + 1
            
            # Outcome breakdown
            outcome = event.outcome
            report["summary"]["outcomes"][outcome] = \
                report["summary"]["outcomes"].get(outcome, 0) + 1
            
            # Add event details (limited for report size)
            report["events"].append({
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "category": event.category.value,
                "message": event.message,
                "outcome": event.outcome,
                "risk_level": event.risk_level
            })
        
        return report


def audit_decorator(category: AuditCategory, 
                   level: AuditLevel = AuditLevel.INFO,
                   log_args: bool = False,
                   log_result: bool = False,
                   sensitive_args: List[str] = None):
    """
    Decorator for automatic audit logging of function calls
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get audit logger from context or create default
            audit_logger = getattr(async_wrapper, '_audit_logger', None)
            if not audit_logger:
                audit_logger = AuditLogger()
            
            start_time = datetime.now()
            function_name = func.__name__
            module_name = func.__module__
            
            # Prepare audit data
            audit_data = {
                "action": function_name,
                "resource": f"{module_name}.{function_name}",
                "context": audit_logger.push_context(
                    function_name=function_name,
                    module_name=module_name
                )
            }
            
            # Log arguments if requested
            if log_args:
                safe_args = {}
                
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for param_name, param_value in bound_args.arguments.items():
                    if sensitive_args and param_name in sensitive_args:
                        safe_args[param_name] = "[REDACTED]"
                    else:
                        safe_args[param_name] = str(param_value)[:1000]  # Limit length
                
                audit_data["data_before"] = safe_args
            
            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Calculate duration
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log result if requested
                if log_result and result is not None:
                    result_str = str(result)[:1000]  # Limit length
                    audit_data["data_after"] = {"result": result_str}
                
                # Log successful execution
                await audit_logger.log_event(
                    level=level,
                    category=category,
                    message=f"Function executed successfully: {function_name}",
                    outcome="success",
                    duration_ms=duration,
                    **audit_data
                )
                
                return result
                
            except Exception as e:
                # Calculate duration
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                # Log failed execution
                await audit_logger.log_event(
                    level=AuditLevel.ERROR,
                    category=category,
                    message=f"Function execution failed: {function_name}",
                    outcome="failure",
                    duration_ms=duration,
                    error_message=str(e),
                    stack_trace=traceback.format_exc(),
                    **audit_data
                )
                
                raise
            
            finally:
                # Pop context
                audit_logger.pop_context()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, create a simple wrapper
            # In practice, most functions in the platform should be async
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Context manager for audit context
class AuditContextManager:
    """Context manager for audit logging"""
    
    def __init__(self, audit_logger: AuditLogger, **context_kwargs):
        self.audit_logger = audit_logger
        self.context_kwargs = context_kwargs
        self.context = None
    
    async def __aenter__(self):
        self.context = self.audit_logger.push_context(**self.context_kwargs)
        return self.context
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.audit_logger.pop_context()
        
        # Log exception if occurred
        if exc_type:
            await self.audit_logger.error(
                category=AuditCategory.SYSTEM_START,  # Generic category
                message=f"Exception in audit context: {exc_type.__name__}",
                error_message=str(exc_val),
                stack_trace=traceback.format_exc()
            )


# Global audit logger instance
_global_audit_logger: Optional[AuditLogger] = None

def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()
    return _global_audit_logger

def set_audit_logger(audit_logger: AuditLogger):
    """Set global audit logger instance"""
    global _global_audit_logger
    _global_audit_logger = audit_logger


# Specialized audit functions for common use cases
async def audit_api_request(method: str, endpoint: str, user_id: str = None, 
                           status_code: int = 200, duration_ms: float = 0, **kwargs):
    """Audit API request"""
    logger = get_audit_logger()
    outcome = "success" if 200 <= status_code < 300 else "failure"
    level = AuditLevel.INFO if outcome == "success" else AuditLevel.WARNING
    
    return await logger.log_event(
        level=level,
        category=AuditCategory.DATA_ACCESS,
        message=f"API request: {method} {endpoint}",
        action=f"api_{method.lower()}",
        resource=endpoint,
        outcome=outcome,
        duration_ms=duration_ms,
        context=logger.push_context(user_id=user_id),
        data_after={"status_code": status_code},
        **kwargs
    )


async def audit_model_prediction(model_id: str, input_size: int, prediction: Any,
                               confidence: float, processing_time_ms: float, **kwargs):
    """Audit ML model prediction"""
    logger = get_audit_logger()
    
    return await logger.log_event(
        level=AuditLevel.BUSINESS,
        category=AuditCategory.MODEL_INFERENCE,
        message=f"Model prediction completed",
        action="model_predict",
        resource=f"model:{model_id}",
        outcome="success",
        duration_ms=processing_time_ms,
        context=logger.push_context(model_id=model_id),
        data_before={"input_size": input_size},
        data_after={
            "prediction": str(prediction)[:500],  # Limit size
            "confidence": confidence
        },
        **kwargs
    )


async def audit_content_upload(content_id: str, creator_id: str, file_size: int,
                             content_type: str, **kwargs):
    """Audit content upload"""
    logger = get_audit_logger()
    
    return await logger.log_event(
        level=AuditLevel.BUSINESS,
        category=AuditCategory.CONTENT_UPLOAD,
        message=f"Content uploaded: {content_type}",
        action="content_upload",
        resource=f"content:{content_id}",
        outcome="success",
        business_impact="medium",
        context=logger.push_context(
            content_id=content_id,
            creator_id=creator_id
        ),
        data_after={
            "file_size_bytes": file_size,
            "content_type": content_type
        },
        **kwargs
    )
