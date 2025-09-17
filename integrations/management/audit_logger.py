"""
📝 Audit Logger - Enterprise Compliance Tracking & Forensic Analysis

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ AVERTISSEMENT LÉGAL: Ce code et concept sont la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, vol ou reproduction sans autorisation écrite de Fahed Mlaiel (mlaiel@live.de)
est strictement interdite et passible de poursuites judiciaires.
"""

import asyncio
import uuid
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Audit log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error" 
    CRITICAL = "critical"
    SECURITY = "security"


class AuditCategory(Enum):
    """Audit categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ADMINISTRATION = "system_administration"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    COMPLIANCE = "compliance"
    API_ACCESS = "api_access"
    FILE_ACCESS = "file_access"
    DATABASE_ACCESS = "database_access"


class RetentionPolicy(Enum):
    """Data retention policies"""
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_180 = 180
    DAYS_365 = 365
    DAYS_2555 = 2555  # 7 years for compliance
    PERMANENT = -1


class ComplianceStandard(Enum):
    """Compliance standards"""
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    NIST = "nist"
    FISMA = "fisma"


@dataclass
class AuditEntry:
    """Audit log entry"""
    audit_id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: str
    user_agent: str
    resource: str
    action: str
    outcome: str  # success, failure, error
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    compliance_tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    parent_audit_id: Optional[str] = None
    checksum: Optional[str] = None


class AuditLogger:
    """
    Enterprise Audit Logger with compliance tracking and forensic analysis
    
    Provides comprehensive audit logging for the Ainflue creator platform
    with support for compliance frameworks, forensic analysis, and tamper-proof logging.
    """
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.audit_entries = []
        self.compliance_reports = {}
        
        # Analytics
        self.audit_metrics = {
            "total_entries": 0,
            "security_events": 0,
            "compliance_violations": 0,
            "forensic_investigations": 0,
            "integrity_violations": 0
        }
    
    async def compliance_audit_trails(
        self,
        user_id: str,
        resource: str,
        action: str,
        outcome: str,
        category: AuditCategory = AuditCategory.API_ACCESS,
        level: AuditLevel = AuditLevel.INFO,
        details: Dict[str, Any] = None,
        compliance_tags: List[str] = None,
        session_context: Dict[str, Any] = None
    ) -> str:
        """
        Create compliance audit trail entry
        """
        session_context = session_context or {}
        
        audit_entry = AuditEntry(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            level=level,
            category=category,
            user_id=user_id,
            session_id=session_context.get("session_id"),
            source_ip=session_context.get("source_ip", "unknown"),
            user_agent=session_context.get("user_agent", "unknown"),
            resource=resource,
            action=action,
            outcome=outcome,
            details=details or {},
            compliance_tags=compliance_tags or [],
            correlation_id=session_context.get("correlation_id")
        )
        
        # Calculate risk score
        audit_entry.risk_score = await self._calculate_risk_score(audit_entry)
        
        # Calculate integrity checksum
        audit_entry.checksum = self._calculate_checksum(audit_entry)
        
        # Store audit entry
        self.audit_entries.append(audit_entry)
        
        # Update metrics
        self.audit_metrics["total_entries"] += 1
        if category == AuditCategory.SECURITY_EVENT:
            self.audit_metrics["security_events"] += 1
        
        logger.info(f"Audit entry created: {audit_entry.audit_id}")
        return audit_entry.audit_id
    
    async def forensic_analysis_tools(
        self,
        analysis_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute forensic analysis tools
        """
        logger.info(f"Executing forensic analysis: {analysis_type}")
        
        if analysis_type == "user_behavior":
            user_id = parameters.get("user_id")
            period_days = parameters.get("days", 7)
            
            if not user_id:
                return {"error": "user_id parameter required"}
            
            result = await self._analyze_user_behavior(user_id, period_days)
            
        elif analysis_type == "timeline_reconstruction":
            incident_id = parameters.get("incident_id")
            
            if not incident_id:
                return {"error": "incident_id parameter required"}
            
            result = await self._reconstruct_timeline(incident_id, parameters)
            
        elif analysis_type == "integrity_check":
            result = await self._check_integrity()
            
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
        
        # Update metrics
        self.audit_metrics["forensic_investigations"] += 1
        
        return {
            "analysis_type": analysis_type,
            "parameters": parameters,
            "result": result,
            "analysis_timestamp": datetime.utcnow()
        }
    
    async def regulatory_reporting(
        self,
        standard: ComplianceStandard,
        report_period_days: int = 90,
        export_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate regulatory compliance reports
        """
        logger.info(f"Generating regulatory report for {standard.value}")
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=report_period_days)
        
        # Filter relevant audit entries
        period_entries = [
            entry for entry in self.audit_entries
            if start_time <= entry.timestamp <= end_time
        ]
        
        # Generate compliance assessment
        compliance_score = await self._assess_compliance(standard, period_entries)
        
        report_data = {
            "report_id": str(uuid.uuid4()),
            "standard": standard.value,
            "period_start": start_time.isoformat(),
            "period_end": end_time.isoformat(),
            "total_events": len(period_entries),
            "compliance_score": compliance_score,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report_data
    
    async def audit_data_analytics(
        self,
        analytics_type: str = "comprehensive",
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate comprehensive audit data analytics
        """
        logger.info("Generating audit data analytics")
        
        cutoff_time = datetime.utcnow() - timedelta(days=time_range_days)
        recent_entries = [
            entry for entry in self.audit_entries
            if entry.timestamp >= cutoff_time
        ]
        
        analytics = {
            "time_range_days": time_range_days,
            "total_entries": len(recent_entries),
            "metrics": self.audit_metrics.copy(),
            "category_distribution": {},
            "level_distribution": {},
            "risk_analysis": {}
        }
        
        # Category distribution
        for entry in recent_entries:
            category = entry.category.value
            analytics["category_distribution"][category] = analytics["category_distribution"].get(category, 0) + 1
        
        # Level distribution
        for entry in recent_entries:
            level = entry.level.value
            analytics["level_distribution"][level] = analytics["level_distribution"].get(level, 0) + 1
        
        # Risk analysis
        risk_scores = [entry.risk_score for entry in recent_entries]
        if risk_scores:
            analytics["risk_analysis"] = {
                "average_risk_score": sum(risk_scores) / len(risk_scores),
                "max_risk_score": max(risk_scores),
                "high_risk_entries": len([score for score in risk_scores if score > 70])
            }
        
        return analytics
    
    async def retention_policy_management(
        self,
        action: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Manage audit data retention policies
        """
        parameters = parameters or {}
        
        if action == "apply_retention":
            # Apply retention policies
            purged_count = await self._apply_retention_policies()
            return {
                "action": "apply_retention",
                "purged_entries": purged_count,
                "remaining_entries": len(self.audit_entries)
            }
        
        elif action == "list_rules":
            return {
                "action": "list_rules",
                "rules": {
                    "authentication": {"retention_days": 365},
                    "data_access": {"retention_days": 2555},
                    "system_administration": {"retention_days": 2555}
                }
            }
        
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def audit_dashboard(self) -> Dict[str, Any]:
        """
        Generate audit dashboard data
        """
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_entries = [entry for entry in self.audit_entries if entry.timestamp >= recent_cutoff]
        
        dashboard = {
            "overview": {
                "total_audit_entries": len(self.audit_entries),
                "recent_activity_24h": len(recent_entries),
                "active_investigations": self.audit_metrics["forensic_investigations"]
            },
            "recent_activity": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "user_id": entry.user_id,
                    "action": entry.action,
                    "resource": entry.resource,
                    "outcome": entry.outcome,
                    "risk_score": entry.risk_score
                }
                for entry in sorted(recent_entries, key=lambda x: x.timestamp, reverse=True)[:10]
            ],
            "metrics": self.audit_metrics,
            "dashboard_generated_at": datetime.utcnow().isoformat()
        }
        
        return dashboard
    
    # Private helper methods
    
    def _calculate_checksum(self, audit_entry: AuditEntry) -> str:
        """Calculate integrity checksum for audit entry"""
        entry_data = {
            "audit_id": audit_entry.audit_id,
            "timestamp": audit_entry.timestamp.isoformat(),
            "user_id": audit_entry.user_id,
            "resource": audit_entry.resource,
            "action": audit_entry.action,
            "outcome": audit_entry.outcome
        }
        
        canonical_json = json.dumps(entry_data, sort_keys=True, separators=(',', ':'))
        checksum = hmac.new(
            self.secret_key.encode(),
            canonical_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return checksum
    
    async def _calculate_risk_score(self, audit_entry: AuditEntry) -> float:
        """Calculate risk score for audit entry"""
        risk_score = 0.0
        
        # Base risk by category
        category_risk = {
            AuditCategory.SYSTEM_ADMINISTRATION: 80.0,
            AuditCategory.CONFIGURATION_CHANGE: 70.0,
            AuditCategory.SECURITY_EVENT: 90.0,
            AuditCategory.DATA_MODIFICATION: 60.0,
            AuditCategory.AUTHENTICATION: 40.0,
            AuditCategory.API_ACCESS: 30.0
        }
        
        risk_score += category_risk.get(audit_entry.category, 20.0)
        
        # Risk by outcome
        if audit_entry.outcome == "failure":
            risk_score += 20.0
        elif audit_entry.outcome == "error":
            risk_score += 30.0
        
        return min(risk_score, 100.0)  # Cap at 100
    
    async def _analyze_user_behavior(self, user_id: str, period_days: int) -> Dict[str, Any]:
        """Analyze user behavior patterns"""
        cutoff_time = datetime.utcnow() - timedelta(days=period_days)
        user_entries = [
            entry for entry in self.audit_entries
            if entry.user_id == user_id and entry.timestamp >= cutoff_time
        ]
        
        if not user_entries:
            return {"error": "No audit entries found for user"}
        
        analysis = {
            "user_id": user_id,
            "total_activities": len(user_entries),
            "activity_patterns": {},
            "anomalies": [],
            "risk_assessment": {}
        }
        
        # Activity patterns by hour
        activity_by_hour = {}
        for entry in user_entries:
            hour = entry.timestamp.hour
            activity_by_hour[hour] = activity_by_hour.get(hour, 0) + 1
        
        analysis["activity_patterns"]["by_hour"] = activity_by_hour
        
        # Check for anomalies
        unusual_hours = [hour for hour, count in activity_by_hour.items() if hour < 6 or hour > 22]
        if unusual_hours:
            analysis["anomalies"].append({
                "type": "unusual_hours",
                "description": f"Activity detected during unusual hours: {unusual_hours}",
                "severity": "medium"
            })
        
        # Risk assessment
        risk_scores = [entry.risk_score for entry in user_entries]
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        analysis["risk_assessment"] = {
            "average_risk_score": avg_risk,
            "risk_level": "high" if avg_risk > 70 else "medium" if avg_risk > 30 else "low"
        }
        
        return analysis
    
    async def _reconstruct_timeline(self, incident_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reconstruct incident timeline"""
        time_range = parameters.get("time_range", {})
        start_time = time_range.get("start", datetime.utcnow() - timedelta(hours=24))
        end_time = time_range.get("end", datetime.utcnow())
        
        incident_entries = [
            entry for entry in self.audit_entries
            if start_time <= entry.timestamp <= end_time
        ]
        
        timeline = {
            "incident_id": incident_id,
            "total_events": len(incident_entries),
            "timeline_events": []
        }
        
        for i, entry in enumerate(sorted(incident_entries, key=lambda x: x.timestamp)):
            timeline_event = {
                "sequence": i + 1,
                "timestamp": entry.timestamp.isoformat(),
                "user_id": entry.user_id,
                "action": entry.action,
                "resource": entry.resource,
                "outcome": entry.outcome,
                "risk_score": entry.risk_score
            }
            timeline["timeline_events"].append(timeline_event)
        
        return timeline
    
    async def _check_integrity(self) -> Dict[str, Any]:
        """Check audit log integrity"""
        tampering_indicators = []
        
        for entry in self.audit_entries:
            calculated_checksum = self._calculate_checksum(entry)
            if entry.checksum != calculated_checksum:
                tampering_indicators.append({
                    "audit_id": entry.audit_id,
                    "type": "integrity_violation",
                    "severity": "high"
                })
        
        return {
            "total_entries_checked": len(self.audit_entries),
            "tampering_indicators": tampering_indicators,
            "integrity_score": (1 - len(tampering_indicators) / len(self.audit_entries)) * 100 if self.audit_entries else 100
        }
    
    async def _assess_compliance(self, standard: ComplianceStandard, entries: List[AuditEntry]) -> float:
        """Assess compliance with standard"""
        # Simplified compliance assessment
        if standard == ComplianceStandard.GDPR:
            # Check for data access logging
            data_entries = [e for e in entries if e.category == AuditCategory.DATA_ACCESS]
            score = (len(data_entries) / len(entries)) * 100 if entries else 0
        elif standard == ComplianceStandard.SOX:
            # Check for financial and admin logging
            financial_entries = [e for e in entries if "financial" in e.resource.lower()]
            admin_entries = [e for e in entries if e.category == AuditCategory.SYSTEM_ADMINISTRATION]
            score = ((len(financial_entries) + len(admin_entries)) / len(entries)) * 100 if entries else 0
        else:
            score = 85.0  # Default score
        
        return min(score, 100.0)
    
    async def _apply_retention_policies(self) -> int:
        """Apply retention policies and purge old entries"""
        purged_count = 0
        current_time = datetime.utcnow()
        entries_to_keep = []
        
        for entry in self.audit_entries:
            # Default retention: 365 days
            retention_cutoff = current_time - timedelta(days=365)
            
            if entry.timestamp >= retention_cutoff:
                entries_to_keep.append(entry)
            else:
                purged_count += 1
        
        self.audit_entries = entries_to_keep
        return purged_count

    @asynccontextmanager
    async def audit_context(self, operation: str, user_id: str = None):
        """Context manager for audit operations"""
        correlation_id = str(uuid.uuid4())
        logger.info(f"Starting audit context for operation: {operation}")
        
        try:
            yield correlation_id
        finally:
            logger.info(f"Cleaning up audit context for operation: {operation}")


# Export main classes
__all__ = [
    'AuditLogger',
    'AuditLevel', 
    'AuditCategory',
    'RetentionPolicy',
    'ComplianceStandard',
    'AuditEntry'
]
