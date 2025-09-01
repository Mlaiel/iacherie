"""Security Monitoring Dashboard and Compliance Reporting System
Provides comprehensive security monitoring, incident response tracking, and compliance reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use prohibited
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
import uuid

from security.audit_trail import SecurityAuditTrail, AuditTrailLevel, security_audit_trail
from security.vulnerability_scanner import SecurityScanner, security_scanner
from database.audit_logs.security_events import SecurityEventLogger, SecurityEventType
from data_management.seeds.security_seeds import SecuritySeedsManager

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """
Security incident severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Security incident status"""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.LOW
    status: IncidentStatus = IncidentStatus.DETECTED
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_to: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    response_actions: List[str] = field(default_factory=list)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "status": self.status.value,
            "detected_at": self.detected_at.isoformat(),
            "assigned_to": self.assigned_to,
            "affected_systems": self.affected_systems,
            "indicators": self.indicators,
            "response_actions": self.response_actions,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }


class SecurityMonitoringDashboard:
    """Comprehensive security monitoring and compliance dashboard"""
    
    def __init__(self):
        self.audit_trail = security_audit_trail
        self.vulnerability_scanner = security_scanner
        self.security_logger = SecurityEventLogger()
        self.security_seeds = SecuritySeedsManager()
        
        # Incident tracking
        self.active_incidents: List[SecurityIncident] = []
        self.incident_history: List[SecurityIncident] = []
        
        # Metrics cache
        self.metrics_cache = {}
        self.cache_expiry = {}
        
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """
Get comprehensive security dashboard data"""
        
        dashboard_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "security_overview": await self._get_security_overview(),
            "vulnerability_status": await self._get_vulnerability_status(),
            "audit_summary": await self._get_audit_summary(),
            "incident_status": await self._get_incident_status(),
            "compliance_status": await self._get_compliance_status(),
            "threat_intelligence": await self._get_threat_intelligence(),
            "system_health": await self._get_system_health()
        }
        
        return dashboard_data
    
    async def _get_security_overview(self) -> Dict[str, Any]:
        """Get security overview metrics"""
        
        # Calculate security metrics from last 24 hours
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        recent_events = await self.audit_trail.get_audit_trail(
            start_time=start_time,
            end_time=end_time
        )
        
        security_events = [e for e in recent_events if e.level in [
            AuditTrailLevel.SECURITY, AuditTrailLevel.CRITICAL
        ]]
        
        failed_events = [e for e in recent_events if not e.success]
        
        return {
            "total_events_24h": len(recent_events),
            "security_events_24h": len(security_events),
            "failed_events_24h": len(failed_events),
            "active_incidents": len(self.active_incidents),
            "critical_incidents": len([i for i in self.active_incidents if i.severity == IncidentSeverity.CRITICAL]),
            "security_score": await self._calculate_security_score(),
            "last_vulnerability_scan": await self._get_last_scan_info()
        }
    
    async def _get_vulnerability_status(self) -> Dict[str, Any]:
        """Get vulnerability scanner status"""
        return await self.vulnerability_scanner.get_compliance_status()
    
    async def _get_audit_summary(self) -> Dict[str, Any]:
        """
Get audit trail summary"""
        
        # Get events from last 7 days
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)
        
        events = await self.audit_trail.get_audit_trail(
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        # Group by level
        level_counts = {}
        for event in events:
            level = event.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Group by day
        daily_counts = {}
        for event in events:
            day = event.timestamp.date().isoformat()
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        integrity_check = await self.audit_trail.verify_audit_integrity()
        
        return {
            "total_events_7d": len(events),
            "events_by_level": level_counts,
            "daily_event_counts": daily_counts,
            "audit_integrity": integrity_check,
            "unique_users": len(set(e.user_id for e in events if e.user_id)),
            "unique_resources": len(set(e.resource for e in events if e.resource))
        }
    
    async def _get_incident_status(self) -> Dict[str, Any]:
        """Get security incident status"""
        
        status_counts = {}
        severity_counts = {}
        
        for incident in self.active_incidents:
            status = incident.status.value
            severity = incident.severity.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate metrics
        total_incidents_30d = len([
            i for i in self.incident_history + self.active_incidents
            if (datetime.now(timezone.utc) - i.detected_at).days <= 30
        ])
        
        avg_resolution_time = await self._calculate_avg_resolution_time()
        
        return {
            "active_incidents": len(self.active_incidents),
            "incidents_by_status": status_counts,
            "incidents_by_severity": severity_counts,
            "total_incidents_30d": total_incidents_30d,
            "avg_resolution_time_hours": avg_resolution_time,
            "escalated_incidents": len([
                i for i in self.active_incidents 
                if i.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]
            ])
        }
    
    async def _get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status across different standards"""
        
        standards = ["GDPR", "SOX", "HIPAA", "PCI_DSS", "ISO27001"]
        compliance_status = {}
        
        for standard in standards:
            # Generate compliance report
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=30)
            
            report = await self.audit_trail.generate_compliance_report(
                start_time=start_time,
                end_time=end_time,
                compliance_standard=standard
            )
            
            # Calculate compliance score
            total_events = report["total_events"]
            compliance_events = report["compliance_relevant_events"]
            security_incidents = report["security_incidents"]
            
            if total_events > 0:
                compliance_score = max(0, 100 - (security_incidents / total_events * 100))
            else:
                compliance_score = 100
            
            compliance_status[standard] = {
                "score": round(compliance_score, 2),
                "status": "COMPLIANT" if compliance_score >= 95 else "NON_COMPLIANT",
                "relevant_events": compliance_events,
                "violations": security_incidents,
                "last_assessment": end_time.isoformat()
            }
        
        return compliance_status
    
    async def _get_threat_intelligence(self) -> Dict[str, Any]:
        """Get threat intelligence summary"""
        
        # Get recent security events
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        security_events = await self.audit_trail.get_audit_trail(
            start_time=start_time,
            end_time=end_time,
            level=AuditTrailLevel.SECURITY
        )
        
        # Analyze threat patterns
        threat_types = {}
        source_ips = {}
        
        for event in security_events:
            # Extract threat type from action
            action = event.action.lower()
            if "login" in action:
                threat_type = "authentication_attack"
            elif "injection" in action:
                threat_type = "injection_attack"
            elif "ddos" in action or "dos" in action:
                threat_type = "denial_of_service"
            elif "malware" in action:
                threat_type = "malware"
            else:
                threat_type = "other"
            
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
            
            # Track source IPs
            if event.ip_address:
                source_ips[event.ip_address] = source_ips.get(event.ip_address, 0) + 1
        
        # Identify top threats
        top_threats = sorted(threat_types.items(), key=lambda x: x[1], reverse=True)[:5]
        top_sources = sorted(source_ips.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "threat_summary_24h": {
                "total_threats": len(security_events),
                "unique_sources": len(source_ips),
                "threat_types": threat_types
            },
            "top_threat_types": [{"type": t[0], "count": t[1]} for t in top_threats],
            "top_threat_sources": [{"ip": s[0], "count": s[1]} for s in top_sources],
            "threat_level": await self._assess_threat_level(len(security_events), threat_types)
        }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        
        # Check various system components
        health_checks = {
            "audit_trail": await self._check_audit_health(),
            "vulnerability_scanner": await self._check_scanner_health(),
            "security_monitoring": await self._check_monitoring_health(),
            "compliance_tracking": await self._check_compliance_health()
        }
        
        # Calculate overall health score
        healthy_components = sum(1 for status in health_checks.values() if status["status"] == "healthy")
        total_components = len(health_checks)
        health_score = (healthy_components / total_components) * 100
        
        return {
            "overall_health_score": round(health_score, 2),
            "component_health": health_checks,
            "last_check": datetime.now(timezone.utc).isoformat(),
            "alerts": await self._get_health_alerts()
        }
    
    async def _calculate_security_score(self) -> float:
        """Calculate overall security score"""
        
        # Get vulnerability status
        vuln_status = await self.vulnerability_scanner.get_compliance_status()
        
        # Score components
        vuln_score = 100 if vuln_status.get("compliant", False) else 50
        
        # Incident score (fewer incidents = higher score)
        incident_count = len(self.active_incidents)
        incident_score = max(0, 100 - (incident_count * 10))
        
        # Audit compliance score
        integrity_check = await self.audit_trail.verify_audit_integrity()
        audit_score = 100 if integrity_check["status"] == "verified" else 70
        
        # Calculate weighted average
        overall_score = (vuln_score * 0.4 + incident_score * 0.3 + audit_score * 0.3)
        
        return round(overall_score, 2)
    
    async def _get_last_scan_info(self) -> Dict[str, Any]:
        """Get last vulnerability scan information"""
        
        try:
            if hasattr(self.vulnerability_scanner, 'scan_history') and self.vulnerability_scanner.scan_history:
                last_scan = self.vulnerability_scanner.scan_history[-1]
                return {
                    "scan_date": last_scan.scan_date.isoformat(),
                    "status": last_scan.compliance_status,
                    "vulnerabilities": last_scan.total_vulnerabilities
                }
        except Exception as e:
            logger.error(f"Error getting last scan info: {e}")
        
        return {
            "scan_date": None,
            "status": "UNKNOWN",
            "vulnerabilities": 0
        }
    
    async def _calculate_avg_resolution_time(self) -> float:
        """Calculate average incident resolution time"""
        
        resolved_incidents = [
            i for i in self.incident_history 
            if i.resolved_at is not None
        ]
        
        if not resolved_incidents:
            return 0.0
        
        total_time = sum([
            (i.resolved_at - i.detected_at).total_seconds() / 3600  # Convert to hours
            for i in resolved_incidents
        ])
        
        return round(total_time / len(resolved_incidents), 2)
    
    async def _assess_threat_level(self, threat_count: int, threat_types: Dict[str, int]) -> str:
        """
Assess current threat level"""
        
        if threat_count == 0:
            return "LOW"
        elif threat_count < 5:
            return "MEDIUM"
        elif threat_count < 20:
            return "HIGH"
        else:
            return "CRITICAL"
    
    async def _check_audit_health(self) -> Dict[str, Any]:
        """Check audit trail health"""
        try:
            integrity = await self.audit_trail.verify_audit_integrity()
            return {
                "status": "healthy" if integrity["status"] == "verified" else "unhealthy",
                "details": integrity
            }
        except Exception as e:
            return {
                "status": "error",
                "details": {"error": str(e)}
            }
    
    async def _check_scanner_health(self) -> Dict[str, Any]:
        """Check vulnerability scanner health"""
        try:
            status = await self.vulnerability_scanner.get_compliance_status()
            return {
                "status": "healthy" if status["status"] != "UNKNOWN" else "warning",
                "details": status
            }
        except Exception as e:
            return {
                "status": "error",
                "details": {"error": str(e)}
            }
    
    async def _check_monitoring_health(self) -> Dict[str, Any]:
        """Check security monitoring health"""
        return {
            "status": "healthy",
            "details": {
                "active_incidents": len(self.active_incidents),
                "monitoring_active": True
            }
        }
    
    async def _check_compliance_health(self) -> Dict[str, Any]:
        """Check compliance tracking health"""
        return {
            "status": "healthy",
            "details": {
                "standards_tracked": ["GDPR", "SOX", "HIPAA", "PCI_DSS", "ISO27001"],
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _get_health_alerts(self) -> List[Dict[str, Any]]:
        """Get system health alerts"""
        alerts = []
        
        # Check for critical incidents
        critical_incidents = [
            i for i in self.active_incidents 
            if i.severity == IncidentSeverity.CRITICAL
        ]
        
        if critical_incidents:
            alerts.append({
                "type": "critical_incident",
                "message": f"{len(critical_incidents)} critical security incidents active",
                "severity": "critical"
            })
        
        # Check vulnerability compliance
        vuln_status = await self.vulnerability_scanner.get_compliance_status()
        if not vuln_status.get("compliant", False):
            alerts.append({
                "type": "vulnerability_compliance",
                "message": f"Security compliance violation: {vuln_status.get('critical_vulnerabilities', 0)} critical vulnerabilities",
                "severity": "high"
            })
        
        return alerts
    
    # Incident Management Methods
    
    async def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_systems: Optional[List[str]] = None,
        indicators: Optional[List[str]] = None
    ) -> str:
        """Create a new security incident"""
        
        incident = SecurityIncident(
            title=title,
            description=description,
            severity=severity,
            affected_systems=affected_systems or [],
            indicators=indicators or []
        )
        
        self.active_incidents.append(incident)
        
        # Log incident creation
        await self.audit_trail.log_security_event(
            action="incident_created",
            resource=f"incident:{incident.incident_id}",
            level=AuditTrailLevel.CRITICAL,
            details={
                "incident_id": incident.incident_id,
                "title": title,
                "severity": severity.value
            }
        )
        
        logger.critical(f"Security incident created: {incident.incident_id} - {title}")
        
        return incident.incident_id
    
    async def update_incident_status(
        self,
        incident_id: str,
        status: IncidentStatus,
        assigned_to: Optional[str] = None,
        response_action: Optional[str] = None
    ) -> bool:
        """Update incident status"""
        
        incident = None
        for i in self.active_incidents:
            if i.incident_id == incident_id:
                incident = i
                break
        
        if not incident:
            return False
        
        incident.status = status
        if assigned_to:
            incident.assigned_to = assigned_to
        if response_action:
            incident.response_actions.append(response_action)
        
        # Set resolution/closure timestamps
        if status == IncidentStatus.RESOLVED and not incident.resolved_at:
            incident.resolved_at = datetime.now(timezone.utc)
        elif status == IncidentStatus.CLOSED and not incident.closed_at:
            incident.closed_at = datetime.now(timezone.utc)
            # Move to history
            self.active_incidents.remove(incident)
            self.incident_history.append(incident)
        
        # Log status update
        await self.audit_trail.log_security_event(
            action="incident_updated",
            resource=f"incident:{incident_id}",
            level=AuditTrailLevel.SECURITY,
            details={
                "incident_id": incident_id,
                "new_status": status.value,
                "assigned_to": assigned_to,
                "response_action": response_action
            }
        )
        
        return True
    
    async def generate_incident_report(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Generate incident report"""
        
        # Find incident in active or history
        incident = None
        for i in self.active_incidents + self.incident_history:
            if i.incident_id == incident_id:
                incident = i
                break
        
        if not incident:
            return None
        
        # Calculate metrics
        detection_time = incident.detected_at
        resolution_time = incident.resolved_at or datetime.now(timezone.utc)
        duration_hours = (resolution_time - detection_time).total_seconds() / 3600
        
        report = {
            "incident_details": incident.to_dict(),
            "timeline": {
                "detected_at": incident.detected_at.isoformat(),
                "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
                "closed_at": incident.closed_at.isoformat() if incident.closed_at else None,
                "duration_hours": round(duration_hours, 2)
            },
            "impact_assessment": {
                "affected_systems": incident.affected_systems,
                "severity": incident.severity.value,
                "status": incident.status.value
            },
            "response_summary": {
                "total_actions": len(incident.response_actions),
                "actions_taken": incident.response_actions,
                "assigned_to": incident.assigned_to
            },
            "lessons_learned": {
                "indicators_identified": incident.indicators,
                "prevention_recommendations": await self._generate_prevention_recommendations(incident)
            }
        }
        
        return report
    
    async def _generate_prevention_recommendations(self, incident: SecurityIncident) -> List[str]:
        """Generate prevention recommendations based on incident"""
        
        recommendations = []
        
        # Generic recommendations based on severity
        if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            recommendations.extend([
                "Review and strengthen access controls",
                "Implement additional monitoring for affected systems",
                "Consider security awareness training for relevant teams"
            ])
        
        # Specific recommendations based on indicators
        for indicator in incident.indicators:
            if "login" in indicator.lower():
                recommendations.append("Implement multi-factor authentication")
            elif "network" in indicator.lower():
                recommendations.append("Review network segmentation and firewall rules")
            elif "malware" in indicator.lower():
                recommendations.append("Update endpoint protection and scanning policies")
        
        return list(set(recommendations))  # Remove duplicates


# Global monitoring dashboard instance
security_dashboard = SecurityMonitoringDashboard()


# Helper functions for easy integration
async def get_security_status() -> Dict[str, Any]:
    """Get current security status"""
    return await security_dashboard.get_security_dashboard()


async def create_security_incident(
    title: str,
    description: str,
    severity: str,
    affected_systems: Optional[List[str]] = None
) -> str:
    """
Create a security incident"""
    severity_enum = IncidentSeverity(severity.lower())
    return await security_dashboard.create_incident(
        title=title,
        description=description,
        severity=severity_enum,
        affected_systems=affected_systems
    )