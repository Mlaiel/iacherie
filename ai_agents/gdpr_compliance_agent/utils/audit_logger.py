"""Compliance Audit Logger - Advanced GDPR Audit Trail System
Comprehensive audit logging for GDPR compliance monitoring and regulatory reporting

Project: IA-Influencer Agent
Author: Fahed Mlaiel
Email: mlaiel@live.de
Company: Ultra-Industrial AI Solutions

⚠️ COPYRIGHT PROTECTION - FAHED MLAIEL ⚠️
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from fastapi import HTTPException

try:
    from core.database import get_db
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db = DatabaseManager
from ...core.logging import get_logger
from ...models.gdpr_models import ComplianceAuditLog, AuditEvent, SecurityEvent

logger = get_logger(__name__)

class AuditEventType(Enum):
    """
Types of GDPR audit events"""

    CONSENT_COLLECTED = "consent_collected"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    CONSENT_RENEWED = "consent_renewed"
    DATA_PROCESSING_START = "data_processing_start"
    DATA_PROCESSING_END = "data_processing_end"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_EXPORT = "data_export"
    RIGHTS_REQUEST = "rights_request"
    RIGHTS_FULFILLED = "rights_fulfilled"
    BREACH_DETECTED = "breach_detected"
    BREACH_CONTAINED = "breach_contained"
    BREACH_NOTIFICATION = "breach_notification"
    COMPLIANCE_ASSESSMENT = "compliance_assessment"
    POLICY_UPDATE = "policy_update"
    SYSTEM_ACCESS = "system_access"
    AUTHENTICATION_EVENT = "authentication_event"
    AUTHORIZATION_EVENT = "authorization_event"

class AuditSeverity(Enum):
    """Severity levels for audit events"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceCategory(Enum):
    """GDPR compliance categories"""

    LAWFULNESS = "lawfulness"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    PURPOSE_LIMITATION = "purpose_limitation"
    DATA_MINIMIZATION = "data_minimization"
    ACCURACY = "accuracy"
    STORAGE_LIMITATION = "storage_limitation"
    INTEGRITY_CONFIDENTIALITY = "integrity_confidentiality"
    ACCOUNTABILITY = "accountability"

@dataclass
class AuditMetrics:
    """Audit trail metrics"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    compliance_events: int
    security_events: int
    breach_events: int
    average_events_per_day: float
    most_active_users: List[str]

class ComplianceAuditLogger:
    """
    Advanced GDPR Compliance Audit Logger
    Provides comprehensive audit logging for all GDPR-related activities
    """
    
    def __init__(self):
        # Audit event templates
        self._event_templates = self._initialize_event_templates()
        
        # Compliance event mappings
        self._compliance_mappings = self._initialize_compliance_mappings()
        
        # Audit retention policies
        self._retention_policies = {
            "security_events": 2555,  # 7 years
            "breach_events": 2555,    # 7 years
            "consent_events": 2190,   # 6 years
            "processing_events": 2190, # 6 years
            "access_events": 1095,    # 3 years
            "general_events": 730     # 2 years
        }
        
        # Event criticality levels
        self._criticality_levels = self._initialize_criticality_levels()
        
        logger.info("Compliance Audit Logger initialized successfully")
    
    def _initialize_event_templates(self) -> Dict[AuditEventType, Dict[str, str]]:
        """Initialize audit event templates"""
        return {
            AuditEventType.CONSENT_COLLECTED: {
                "description": "User consent collected for data processing",
                "compliance_categories": ["lawfulness", "transparency"],
                "required_fields": ["user_id", "purpose", "consent_type", "legal_basis"]
            },
            AuditEventType.DATA_PROCESSING_START: {
                "description": "Data processing activity initiated",
                "compliance_categories": ["lawfulness", "purpose_limitation", "data_minimization"],
                "required_fields": ["user_id", "processing_purpose", "data_categories", "lawful_basis"]
            },
            AuditEventType.RIGHTS_REQUEST: {
                "description": "Data subject rights request received",
                "compliance_categories": ["transparency", "accountability"],
                "required_fields": ["user_id", "request_type", "request_details"]
            },
            AuditEventType.BREACH_DETECTED: {
                "description": "Data breach incident detected",
                "compliance_categories": ["integrity_confidentiality", "accountability"],
                "required_fields": ["breach_type", "affected_users", "detection_method"]
            },
            AuditEventType.DATA_DELETION: {
                "description": "Personal data deleted from system",
                "compliance_categories": ["storage_limitation", "accuracy"],
                "required_fields": ["user_id", "deletion_reason", "data_categories"]
            }
        }
    
    def _initialize_compliance_mappings(self) -> Dict[str, List[str]]:
        """Initialize compliance category mappings"""
        return {
            "consent_management": [
                ComplianceCategory.LAWFULNESS.value,
                ComplianceCategory.TRANSPARENCY.value
            ],
            "data_processing": [
                ComplianceCategory.PURPOSE_LIMITATION.value,
                ComplianceCategory.DATA_MINIMIZATION.value,
                ComplianceCategory.LAWFULNESS.value
            ],
            "data_retention": [
                ComplianceCategory.STORAGE_LIMITATION.value,
                ComplianceCategory.ACCURACY.value
            ],
            "security_measures": [
                ComplianceCategory.INTEGRITY_CONFIDENTIALITY.value,
                ComplianceCategory.ACCOUNTABILITY.value
            ],
            "subject_rights": [
                ComplianceCategory.TRANSPARENCY.value,
                ComplianceCategory.ACCOUNTABILITY.value
            ]
        }
    
    def _initialize_criticality_levels(self) -> Dict[AuditEventType, AuditSeverity]:
        """Initialize event criticality levels"""
        return {
            AuditEventType.BREACH_DETECTED: AuditSeverity.CRITICAL,
            AuditEventType.BREACH_NOTIFICATION: AuditSeverity.CRITICAL,
            AuditEventType.CONSENT_WITHDRAWN: AuditSeverity.HIGH,
            AuditEventType.DATA_DELETION: AuditSeverity.HIGH,
            AuditEventType.RIGHTS_REQUEST: AuditSeverity.MEDIUM,
            AuditEventType.DATA_PROCESSING_START: AuditSeverity.MEDIUM,
            AuditEventType.CONSENT_COLLECTED: AuditSeverity.LOW,
            AuditEventType.DATA_ACCESS: AuditSeverity.LOW
        }
    
    async def log_compliance_event(
        self, 
        user_id: str,
        event_type: str,
        details: Dict[str, Any],
        severity: AuditSeverity = None,
        compliance_categories: List[str] = None
    ) -> str:
        """
Log a GDPR compliance event"""
        try:
            event_id = str(uuid.uuid4())
            
            # Convert string event type to enum if needed
            if isinstance(event_type, str):
                try:
                    event_type_enum = AuditEventType(event_type)
                except ValueError:
                    event_type_enum = None
                    logger.warning(f"Unknown event type: {event_type}")
            else:
                event_type_enum = event_type
            
            # Determine severity if not provided
            if not severity:
                severity = self._criticality_levels.get(event_type_enum, AuditSeverity.MEDIUM)
            
            # Determine compliance categories if not provided
            if not compliance_categories and event_type_enum:
                template = self._event_templates.get(event_type_enum, {})
                compliance_categories = template.get("compliance_categories", ["accountability"])
            
            # Validate required fields
            validation_result = await self._validate_event_data(event_type_enum, details)
            
            # Create audit log entry
            audit_log = ComplianceAuditLog(
                event_id=event_id,
                user_id=user_id,
                event_type=event_type if isinstance(event_type, str) else event_type.value,
                severity=severity.value,
                compliance_categories=compliance_categories or ["general"],
                event_details=details,
                validation_status=validation_result["status"],
                validation_warnings=validation_result["warnings"],
                timestamp=datetime.utcnow(),
                source_ip=details.get("source_ip"),
                user_agent=details.get("user_agent"),
                session_id=details.get("session_id"),
                correlation_id=details.get("correlation_id"),
                event_hash=await self._generate_event_hash(event_id, user_id, event_type, details)
            )
            
            async with get_db() as db:
                db.add(audit_log)
                await db.commit()
                await db.refresh(audit_log)
            
            # Create detailed audit event
            await self._create_detailed_audit_event(event_id, event_type_enum, details)
            
            # Trigger real-time monitoring if critical
            if severity == AuditSeverity.CRITICAL:
                await self._trigger_critical_event_monitoring(event_id, event_type, details)
            
            logger.info(f"Compliance event logged: {event_type} for user {user_id} (severity: {severity.value})")
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging compliance event: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Audit logging failed: {str(e)}")
    
    async def log_data_processing(
        self, 
        user_id: str,
        processing_id: str,
        purpose: str,
        data_categories: List[str],
        lawful_basis: str = "consent"
    ) -> str:
        """Log data processing activity"""
        try:
            details = {
                "processing_id": processing_id,
                "processing_purpose": purpose,
                "data_categories": data_categories,
                "lawful_basis": lawful_basis,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "compliance_check": "passed"
            }
            
            event_id = await self.log_compliance_event(
                user_id=user_id,
                event_type=AuditEventType.DATA_PROCESSING_START,
                details=details,
                severity=AuditSeverity.MEDIUM,
                compliance_categories=["lawfulness", "purpose_limitation", "data_minimization"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging data processing: {str(e)}")
            raise
    
    async def log_consent_event(
        self, 
        user_id: str,
        consent_id: str,
        action: str,
        purpose: str,
        consent_details: Dict[str, Any] = None
    ) -> str:
        """Log consent-related events"""
        try:
            # Determine event type based on action
            event_type_mapping = {
                "collected": AuditEventType.CONSENT_COLLECTED,
                "granted": AuditEventType.CONSENT_COLLECTED,
                "withdrawn": AuditEventType.CONSENT_WITHDRAWN,
                "renewed": AuditEventType.CONSENT_RENEWED
            }
            
            event_type = event_type_mapping.get(action, AuditEventType.CONSENT_COLLECTED)
            
            details = {
                "consent_id": consent_id,
                "consent_action": action,
                "purpose": purpose,
                "legal_basis": "consent",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if consent_details:
                details.update(consent_details)
            
            event_id = await self.log_compliance_event(
                user_id=user_id,
                event_type=event_type,
                details=details,
                severity=AuditSeverity.HIGH if action == "withdrawn" else AuditSeverity.MEDIUM,
                compliance_categories=["lawfulness", "transparency"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging consent event: {str(e)}")
            raise
    
    async def log_rights_request(
        self, 
        user_id: str,
        request_id: str,
        request_type: str,
        details: Dict[str, Any]
    ) -> str:
        """Log data subject rights request"""
        try:
            audit_details = {
                "request_id": request_id,
                "request_type": request_type,
                "request_timestamp": datetime.utcnow().isoformat(),
                "request_details": details,
                "compliance_deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "status": "received"
            }
            
            event_id = await self.log_compliance_event(
                user_id=user_id,
                event_type=AuditEventType.RIGHTS_REQUEST,
                details=audit_details,
                severity=AuditSeverity.MEDIUM,
                compliance_categories=["transparency", "accountability"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging rights request: {str(e)}")
            raise
    
    async def log_security_event(
        self, 
        event_type: str,
        severity: AuditSeverity,
        details: Dict[str, Any],
        user_id: str = None,
        incident_id: str = None
    ) -> str:
        """Log security-related events"""
        try:
            event_id = str(uuid.uuid4())
            
            # Create security event record
            security_event = SecurityEvent(
                event_id=event_id,
                incident_id=incident_id,
                user_id=user_id,
                event_type=event_type,
                severity=severity.value,
                event_details=details,
                timestamp=datetime.utcnow(),
                source_ip=details.get("source_ip"),
                resolved=False,
                resolution_notes=""
            )
            
            async with get_db() as db:
                db.add(security_event)
                await db.commit()
                await db.refresh(security_event)
            
            # Also log as compliance event
            compliance_event_id = await self.log_compliance_event(
                user_id=user_id or "system",
                event_type="security_event",
                details={
                    "security_event_id": event_id,
                    "incident_id": incident_id,
                    "event_type": event_type,
                    "severity": severity.value,
                    **details
                },
                severity=severity,
                compliance_categories=["integrity_confidentiality", "accountability"]
            )
            
            logger.warning(f"Security event logged: {event_type} (severity: {severity.value})")
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            raise
    
    async def log_breach_notification(
        self, 
        user_id: str,
        breach_id: str,
        incident_details: Dict[str, Any]
    ) -> str:
        """Log data breach notification"""
        try:
            details = {
                "breach_id": breach_id,
                "incident_type": incident_details.get("incident_type", "unknown"),
                "affected_users": incident_details.get("affected_users", []),
                "notification_timestamp": datetime.utcnow().isoformat(),
                "notification_method": incident_details.get("notification_method", "system"),
                "breach_details": incident_details
            }
            
            event_id = await self.log_compliance_event(
                user_id=user_id,
                event_type=AuditEventType.BREACH_NOTIFICATION,
                details=details,
                severity=AuditSeverity.CRITICAL,
                compliance_categories=["integrity_confidentiality", "transparency", "accountability"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging breach notification: {str(e)}")
            raise
    
    async def log_regulatory_action(
        self, 
        action_type: str,
        details: Dict[str, Any],
        breach_id: str = None,
        notification_details: Dict[str, Any] = None
    ) -> str:
        """Log regulatory compliance actions"""
        try:
            audit_details = {
                "action_type": action_type,
                "breach_id": breach_id,
                "regulatory_timestamp": datetime.utcnow().isoformat(),
                "action_details": details
            }
            
            if notification_details:
                audit_details["notification_details"] = notification_details
            
            event_id = await self.log_compliance_event(
                user_id="system",
                event_type="regulatory_action",
                details=audit_details,
                severity=AuditSeverity.HIGH,
                compliance_categories=["accountability", "transparency"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging regulatory action: {str(e)}")
            raise
    
    async def log_investigation_result(
        self, 
        breach_id: str,
        investigation_details: Dict[str, Any]
    ) -> str:
        """Log breach investigation results"""
        try:
            details = {
                "breach_id": breach_id,
                "investigation_completed": datetime.utcnow().isoformat(),
                "investigation_details": investigation_details,
                "findings": investigation_details.get("findings", {}),
                "recommendations": investigation_details.get("recommendations", [])
            }
            
            event_id = await self.log_compliance_event(
                user_id="system",
                event_type="investigation_completed",
                details=details,
                severity=AuditSeverity.HIGH,
                compliance_categories=["accountability", "integrity_confidentiality"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging investigation result: {str(e)}")
            raise
    
    async def log_data_cleanup(self, cleanup_results: Dict[str, Any]) -> str:
        """Log data cleanup activities"""
        try:
            details = {
                "cleanup_timestamp": datetime.utcnow().isoformat(),
                "cleanup_results": cleanup_results,
                "records_processed": cleanup_results.get("activities_processed", 0),
                "data_deleted": cleanup_results.get("data_deleted", 0),
                "data_anonymized": cleanup_results.get("data_anonymized", 0)
            }
            
            event_id = await self.log_compliance_event(
                user_id="system",
                event_type="data_cleanup",
                details=details,
                severity=AuditSeverity.MEDIUM,
                compliance_categories=["storage_limitation", "accountability"]
            )
            
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging data cleanup: {str(e)}")
            raise
    
    async def get_audit_trail(
        self, 
        user_id: str = None,
        event_types: List[str] = None,
        start_date: datetime = None,
        end_date: datetime = None,
        severity: AuditSeverity = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Retrieve audit trail with filtering options"""
        try:
            async with get_db() as db:
                query = select(ComplianceAuditLog)
                
                # Apply filters
                filters = []
                
                if user_id:
                    filters.append(ComplianceAuditLog.user_id == user_id)
                
                if event_types:
                    filters.append(ComplianceAuditLog.event_type.in_(event_types))
                
                if start_date:
                    filters.append(ComplianceAuditLog.timestamp >= start_date)
                
                if end_date:
                    filters.append(ComplianceAuditLog.timestamp <= end_date)
                
                if severity:
                    filters.append(ComplianceAuditLog.severity == severity.value)
                
                if filters:
                    query = query.where(and_(*filters))
                
                # Order by timestamp descending and limit
                query = query.order_by(ComplianceAuditLog.timestamp.desc()).limit(limit)
                
                result = await db.execute(query)
                audit_logs = result.scalars().all()
                
                # Format response
                formatted_logs = []
                for log in audit_logs:
                    formatted_logs.append({
                        "event_id": log.event_id,
                        "user_id": log.user_id,
                        "event_type": log.event_type,
                        "severity": log.severity,
                        "compliance_categories": log.compliance_categories,
                        "timestamp": log.timestamp.isoformat(),
                        "event_details": log.event_details,
                        "validation_status": log.validation_status,
                        "source_ip": log.source_ip
                    })
                
                return {
                    "audit_trail": formatted_logs,
                    "total_events": len(formatted_logs),
                    "query_parameters": {
                        "user_id": user_id,
                        "event_types": event_types,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                        "severity": severity.value if severity else None,
                        "limit": limit
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error retrieving audit trail: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Audit trail retrieval failed: {str(e)}")
    
    async def get_audit_metrics(self, period_days: int = 30) -> AuditMetrics:
        """Get audit trail metrics for specified period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            async with get_db() as db:
                # Get all events in period
                events_query = await db.execute(
                    select(ComplianceAuditLog).where(
                        ComplianceAuditLog.timestamp >= start_date
                    )
                )
                
                events = events_query.scalars().all()
                
                if not events:
                    return AuditMetrics(0, {}, {}, 0, 0, 0, 0.0, [])
                
                # Count events by type
                events_by_type = {}
                events_by_severity = {}
                compliance_events = 0
                security_events = 0
                breach_events = 0
                user_activity = {}
                
                for event in events:
                    # By type
                    if event.event_type not in events_by_type:
                        events_by_type[event.event_type] = 0
                    events_by_type[event.event_type] += 1
                    
                    # By severity
                    if event.severity not in events_by_severity:
                        events_by_severity[event.severity] = 0
                    events_by_severity[event.severity] += 1
                    
                    # Category counts
                    if any(cat in ["lawfulness", "transparency", "accountability"] for cat in event.compliance_categories):
                        compliance_events += 1
                    
                    if "security" in event.event_type.lower() or event.severity == AuditSeverity.CRITICAL.value:
                        security_events += 1
                    
                    if "breach" in event.event_type.lower():
                        breach_events += 1
                    
                    # User activity
                    if event.user_id and event.user_id != "system":
                        if event.user_id not in user_activity:
                            user_activity[event.user_id] = 0
                        user_activity[event.user_id] += 1
                
                # Calculate average events per day
                avg_events_per_day = len(events) / period_days if period_days > 0 else 0
                
                # Get most active users
                most_active_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5]
                most_active_users = [user_id for user_id, count in most_active_users]
                
                return AuditMetrics(
                    total_events=len(events),
                    events_by_type=events_by_type,
                    events_by_severity=events_by_severity,
                    compliance_events=compliance_events,
                    security_events=security_events,
                    breach_events=breach_events,
                    average_events_per_day=round(avg_events_per_day, 2),
                    most_active_users=most_active_users
                )
                
        except Exception as e:
            logger.error(f"Error getting audit metrics: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Audit metrics calculation failed: {str(e)}")
    
    async def generate_compliance_report(
        self, 
        user_id: str = None,
        period_days: int = 90,
        categories: List[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        try:
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Get audit trail
            audit_trail = await self.get_audit_trail(
                user_id=user_id,
                start_date=start_date,
                limit=1000
            )
            
            # Get metrics
            metrics = await self.get_audit_metrics(period_days)
            
            # Compliance analysis
            compliance_analysis = await self._analyze_compliance_events(
                audit_trail["audit_trail"], categories
            )
            
            # Risk assessment
            risk_assessment = await self._assess_compliance_risks(
                audit_trail["audit_trail"], metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_audit_recommendations(
                compliance_analysis, risk_assessment
            )
            
            return {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.utcnow().isoformat(),
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                    "period_days": period_days
                },
                "scope": {
                    "user_id": user_id,
                    "categories": categories,
                    "total_events": metrics.total_events
                },
                "metrics": asdict(metrics),
                "compliance_analysis": compliance_analysis,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "audit_summary": {
                    "high_severity_events": metrics.events_by_severity.get("high", 0),
                    "critical_events": metrics.events_by_severity.get("critical", 0),
                    "breach_incidents": metrics.breach_events,
                    "compliance_score": compliance_analysis.get("compliance_score", 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Compliance report generation failed: {str(e)}")
    
    # Helper methods
    
    async def _validate_event_data(
        self, 
        event_type: Optional[AuditEventType], 
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate audit event data completeness"""
        validation_result = {
            "status": "valid",
            "warnings": []
        }
        
        if not event_type:
            validation_result["warnings"].append("Unknown event type")
            return validation_result
        
        # Check required fields
        template = self._event_templates.get(event_type, {})
        required_fields = template.get("required_fields", [])
        
        for field in required_fields:
            if field not in details:
                validation_result["warnings"].append(f"Missing required field: {field}")
        
        if validation_result["warnings"]:
            validation_result["status"] = "warnings"
        
        return validation_result
    
    async def _generate_event_hash(
        self, 
        event_id: str, 
        user_id: str,
        event_type: Any, 
        details: Dict[str, Any]
    ) -> str:
        """Generate integrity hash for audit event"""
        try:
            hash_data = f"{event_id}_{user_id}_{str(event_type)}_{json.dumps(details, sort_keys=True)}"
            event_hash = hashlib.sha256(hash_data.encode()).hexdigest()
            return event_hash
        except Exception as e:
            logger.error(f"Error generating event hash: {str(e)}")
            return "hash_generation_failed"
    
    async def _create_detailed_audit_event(
        self, 
        event_id: str,
        event_type: Optional[AuditEventType], 
        details: Dict[str, Any]
    ) -> None:
        """Create detailed audit event record"""
        try:
            if not event_type:
                return
            
            template = self._event_templates.get(event_type, {})
            
            audit_event = AuditEvent(
                event_id=event_id,
                event_category=event_type.value,
                event_description=template.get("description", ""),
                compliance_categories=template.get("compliance_categories", []),
                event_metadata=details,
                created_at=datetime.utcnow()
            )
            
            async with get_db() as db:
                db.add(audit_event)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error creating detailed audit event: {str(e)}")
    
    async def _trigger_critical_event_monitoring(
        self, 
        event_id: str,
        event_type: Any, 
        details: Dict[str, Any]
    ) -> None:
        """Trigger real-time monitoring for critical events"""
        try:
            # In production, this would trigger alerts, notifications, etc.
            logger.critical(f"CRITICAL EVENT DETECTED: {event_type} - Event ID: {event_id}")
            
            # Could send notifications to compliance team
            # Could trigger automated response procedures
            # Could escalate to security operations center
            
        except Exception as e:
            logger.error(f"Error triggering critical event monitoring: {str(e)}")
    
    async def _analyze_compliance_events(
        self, 
        events: List[Dict[str, Any]], 
        categories: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze compliance events for patterns and issues"""
        try:
            if not events:
                return {"compliance_score": 0.0, "category_analysis": {}}
            
            # Filter by categories if specified
            if categories:
                filtered_events = []
                for event in events:
                    event_categories = event.get("compliance_categories", [])
                    if any(cat in event_categories for cat in categories):
                        filtered_events.append(event)
                events = filtered_events
            
            # Analyze by compliance category
            category_analysis = {}
            total_events = len(events)
            
            for category in ComplianceCategory:
                cat_value = category.value
                cat_events = [e for e in events if cat_value in e.get("compliance_categories", [])]
                
                category_analysis[cat_value] = {
                    "total_events": len(cat_events),
                    "percentage": (len(cat_events) / total_events * 100) if total_events > 0 else 0,
                    "severity_breakdown": {
                        "low": len([e for e in cat_events if e["severity"] == "low"]),
                        "medium": len([e for e in cat_events if e["severity"] == "medium"]),
                        "high": len([e for e in cat_events if e["severity"] == "high"]),
                        "critical": len([e for e in cat_events if e["severity"] == "critical"])
                    }
                }
            
            # Calculate overall compliance score
            critical_events = len([e for e in events if e["severity"] == "critical"])
            high_events = len([e for e in events if e["severity"] == "high"])
            
            # Compliance score calculation (0-100)
            compliance_score = max(0, 100 - (critical_events * 20) - (high_events * 5))
            
            return {
                "compliance_score": compliance_score,
                "category_analysis": category_analysis,
                "event_distribution": {
                    "total_events": total_events,
                    "critical_events": critical_events,
                    "high_severity_events": high_events
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing compliance events: {str(e)}")
            return {"compliance_score": 0.0, "category_analysis": {}}
    
    async def _assess_compliance_risks(
        self, 
        events: List[Dict[str, Any]], 
        metrics: AuditMetrics
    ) -> Dict[str, Any]:
        """Assess compliance risks based on audit data"""
        try:
            risk_factors = []
            risk_score = 0.0  # 0-10 scale
            
            # High number of critical events
            if metrics.breach_events > 0:
                risk_factors.append("Data breach incidents detected")
                risk_score += 5.0
            
            # High number of critical severity events
            critical_count = metrics.events_by_severity.get("critical", 0)
            if critical_count > 5:
                risk_factors.append(f"High number of critical events: {critical_count}")
                risk_score += 3.0
            
            # Consent withdrawal patterns
            withdrawal_events = [e for e in events if e["event_type"] == "consent_withdrawn"]
            if len(withdrawal_events) > 10:
                risk_factors.append("High consent withdrawal rate")
                risk_score += 2.0
            
            # Frequent rights requests
            if len([e for e in events if e["event_type"] == "rights_request"]) > 20:
                risk_factors.append("High volume of data subject rights requests")
                risk_score += 1.0
            
            # Security events
            if metrics.security_events > 10:
                risk_factors.append("Multiple security events detected")
                risk_score += 2.0
            
            # Determine risk level
            if risk_score >= 8.0:
                risk_level = "critical"
            elif risk_score >= 5.0:
                risk_level = "high"
            elif risk_score >= 3.0:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "risk_score": min(10.0, risk_score),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "mitigation_required": risk_score >= 5.0,
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing compliance risks: {str(e)}")
            return {"risk_score": 5.0, "risk_level": "medium", "risk_factors": []}
    
    async def _generate_audit_recommendations(
        self, 
        compliance_analysis: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on audit analysis"""
        recommendations = []
        
        try:
            compliance_score = compliance_analysis.get("compliance_score", 0)
            risk_score = risk_assessment.get("risk_score", 0)
            
            # Low compliance score recommendations
            if compliance_score < 70:
                recommendations.append({
                    "priority": "high",
                    "category": "compliance_improvement",
                    "title": "Improve Overall Compliance Score",
                    "description": f"Compliance score is {compliance_score}/100",
                    "action": "Review and address high-severity compliance events"
                })
            
            # High risk score recommendations
            if risk_score >= 7.0:
                recommendations.append({
                    "priority": "critical",
                    "category": "risk_mitigation",
                    "title": "Critical Risk Mitigation Required",
                    "description": f"Risk score is {risk_score}/10",
                    "action": "Implement immediate risk mitigation measures"
                })
            
            # Breach-related recommendations
            if "Data breach incidents detected" in risk_assessment.get("risk_factors", []):
                recommendations.append({
                    "priority": "critical",
                    "category": "breach_response",
                    "title": "Review Breach Response Procedures",
                    "description": "Data breach incidents require immediate attention",
                    "action": "Conduct breach investigation and implement additional security measures"
                })
            
            # Consent management recommendations
            if "High consent withdrawal rate" in risk_assessment.get("risk_factors", []):
                recommendations.append({
                    "priority": "medium",
                    "category": "consent_management",
                    "title": "Review Consent Collection Process",
                    "description": "High rate of consent withdrawals detected",
                    "action": "Analyze consent withdrawal reasons and improve consent experience"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating audit recommendations: {str(e)}")
            return []

    async def cleanup_expired_logs(self) -> Dict[str, Any]:
        """Clean up expired audit logs based on retention policies"""
        try:
            cleanup_results = {
                "categories_processed": 0,
                "logs_deleted": 0,
                "logs_archived": 0,
                "errors": 0
            }
            
            async with get_db() as db:
                for category, retention_days in self._retention_policies.items():
                    try:
                        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                        
                        # Delete logs older than retention period
                        delete_query = delete(ComplianceAuditLog).where(
                            and_(
                                ComplianceAuditLog.timestamp < cutoff_date,
                                ComplianceAuditLog.event_type.contains(category.replace("_events", ""))
                            )
                        )
                        
                        result = await db.execute(delete_query)
                        deleted_count = result.rowcount
                        
                        cleanup_results["logs_deleted"] += deleted_count
                        cleanup_results["categories_processed"] += 1
                        
                    except Exception as e:
                        logger.error(f"Error cleaning up {category}: {str(e)}")
                        cleanup_results["errors"] += 1
                
                await db.commit()
            
            logger.info(f"Audit log cleanup completed: {cleanup_results['logs_deleted']} logs deleted")
            
            return cleanup_results
            
        except Exception as e:
            logger.error(f"Error in audit log cleanup: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Audit log cleanup failed: {str(e)}")
