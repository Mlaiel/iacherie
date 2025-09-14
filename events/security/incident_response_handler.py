"""Incident Response Handler for Events Security

Automated security incident response and management for Ainflue platform.
Handles security incidents with escalation, containment, and recovery procedures.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class IncidentType(Enum):
    """Types of security incidents"""
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE_INFECTION = "malware_infection"
    DDoS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"
    SYSTEM_COMPROMISE = "system_compromise"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SERVICE_DISRUPTION = "service_disruption"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident response status"""
    NEW = "new"
    ASSIGNED = "assigned"
    INVESTIGATING = "investigating"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    LESSONS_LEARNED = "lessons_learned"
    CLOSED = "closed"


class ResponseAction(Enum):
    """Automated response actions"""
    ISOLATE_SYSTEM = "isolate_system"
    BLOCK_IP = "block_ip"
    DISABLE_USER = "disable_user"
    QUARANTINE_FILE = "quarantine_file"
    BACKUP_DATA = "backup_data"
    RESET_CREDENTIALS = "reset_credentials"
    NOTIFY_TEAM = "notify_team"
    ESCALATE_MANAGEMENT = "escalate_management"
    CONTACT_AUTHORITIES = "contact_authorities"
    ACTIVATE_BCP = "activate_bcp"


@dataclass
class SecurityIncident:
    """Represents a security incident"""
    incident_id: str
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    title: str
    description: str
    detected_at: datetime
    reported_by: str
    assigned_to: Optional[str] = None
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    response_actions: List[str] = field(default_factory=list)
    impact_assessment: str = ""
    lessons_learned: str = ""
    closed_at: Optional[datetime] = None
    
    def add_timeline_entry(self, action -> None: str, description -> None: str, user -> None: str = "system") -> None:
        """Add entry to incident timeline"""
        self.timeline.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'description': description,
            'user': user
        })


@dataclass
class ResponsePlan:
    """Incident response plan configuration"""
    plan_id: str
    incident_types: List[IncidentType]
    severity_levels: List[IncidentSeverity]
    automated_actions: List[ResponseAction]
    escalation_rules: Dict[str, Any]
    notification_rules: Dict[str, Any]
    containment_procedures: List[str]
    recovery_procedures: List[str]
    enabled: bool = True


@dataclass
class IncidentReport:
    """Comprehensive incident response report"""
    report_id: str
    incident_id: str
    generated_at: datetime
    incident_summary: str
    impact_analysis: str
    response_timeline: List[Dict[str, Any]]
    actions_taken: List[str]
    lessons_learned: str
    recommendations: List[str]
    compliance_implications: List[str]


class IncidentResponseHandler:
    """
    Automated security incident response handler for Ainflue platform.
    Manages complete incident lifecycle with automated and manual responses.
    """
    
    def __init__(self) -> None:
        self.enabled = True
        self.incidents = []  # In-memory storage for demo
        self.response_plans = self._initialize_response_plans()
        self.notification_handlers = {}  # channel -> handler function
        self.escalation_chains = self._initialize_escalation_chains()
        self.automation_enabled = True
        self.max_incident_history = 1000
        self.sla_thresholds = self._initialize_sla_thresholds()
        logger.info("IncidentResponseHandler initialized")
    
    async def handle_security_incident(self,
                                     incident_type: IncidentType,
                                     severity: IncidentSeverity,
                                     title: str,
                                     description: str,
                                     evidence: Dict[str, Any] = None,
                                     affected_systems: List[str] = None,
                                     affected_users: List[str] = None,
                                     reported_by: str = "system") -> SecurityIncident:
        """
        Handle a new security incident with automated response.
        
        Args:
            incident_type: Type of security incident
            severity: Severity level of the incident
            title: Short title describing the incident
            description: Detailed description of the incident
            evidence: Evidence data related to the incident
            affected_systems: List of affected system components
            affected_users: List of affected user accounts
            reported_by: Who reported the incident
            
        Returns:
            SecurityIncident object with tracking information
        """
        if not self.enabled:
            return self._create_disabled_incident(title, description)
        
        try:
            # Create incident
            incident = SecurityIncident(
                incident_id=f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{len(self.incidents) + 1:04d}",
                incident_type=incident_type,
                severity=severity,
                status=IncidentStatus.NEW,
                title=title,
                description=description,
                detected_at=datetime.utcnow(),
                reported_by=reported_by,
                affected_systems=affected_systems or [],
                affected_users=affected_users or [],
                evidence=evidence or {}
            )
            
            # Add initial timeline entry
            incident.add_timeline_entry(
                "incident_created",
                f"Incident created: {title}",
                reported_by
            )
            
            # Store incident
            self.incidents.append(incident)
            self._maintain_incident_history()
            
            # Perform automated response
            await self._execute_automated_response(incident)
            
            # Assign incident based on severity and type
            await self._auto_assign_incident(incident)
            
            # Send notifications
            await self._send_incident_notifications(incident)
            
            # Check for escalation
            await self._check_escalation_triggers(incident)
            
            logger.info(f"Security incident created: {incident.incident_id} - {title}")
            return incident
            
        except Exception as e:
            logger.error(f"Error handling security incident: {str(e)}")
            return self._create_error_incident(title, description, str(e))
    
    async def _execute_automated_response(self, incident -> None: SecurityIncident) -> None:
        """Execute automated response actions for incident"""
        
        if not self.automation_enabled:
            return
        
        # Find applicable response plans
        applicable_plans = [
            plan for plan in self.response_plans.values()
            if (incident.incident_type in plan.incident_types and
                incident.severity in plan.severity_levels and
                plan.enabled)
        ]
        
        # Execute automated actions from all applicable plans
        for plan in applicable_plans:
            for action in plan.automated_actions:
                success = await self._execute_response_action(action, incident)
                if success:
                    incident.response_actions.append(action.value)
                    incident.add_timeline_entry(
                        "automated_action",
                        f"Executed automated action: {action.value}",
                        "system"
                    )
        
        if incident.response_actions:
            incident.status = IncidentStatus.CONTAINING
            incident.add_timeline_entry(
                "status_change",
                "Status changed to CONTAINING after automated response",
                "system"
            )
    
    async def _execute_response_action(self, action: ResponseAction, incident: SecurityIncident) -> bool:
        """Execute a specific response action"""
        
        try:
            if action == ResponseAction.ISOLATE_SYSTEM:
                return await self._isolate_affected_systems(incident)
            
            elif action == ResponseAction.BLOCK_IP:
                return await self._block_malicious_ips(incident)
            
            elif action == ResponseAction.DISABLE_USER:
                return await self._disable_affected_users(incident)
            
            elif action == ResponseAction.QUARANTINE_FILE:
                return await self._quarantine_malicious_files(incident)
            
            elif action == ResponseAction.BACKUP_DATA:
                return await self._backup_critical_data(incident)
            
            elif action == ResponseAction.RESET_CREDENTIALS:
                return await self._reset_compromised_credentials(incident)
            
            elif action == ResponseAction.NOTIFY_TEAM:
                return await self._notify_incident_response_team(incident)
            
            elif action == ResponseAction.ESCALATE_MANAGEMENT:
                return await self._escalate_to_management(incident)
            
            elif action == ResponseAction.CONTACT_AUTHORITIES:
                return await self._contact_law_enforcement(incident)
            
            elif action == ResponseAction.ACTIVATE_BCP:
                return await self._activate_business_continuity_plan(incident)
            
        except Exception as e:
            logger.error(f"Error executing response action {action}: {str(e)}")
        
        return False
    
    async def _isolate_affected_systems(self, incident: SecurityIncident) -> bool:
        """Isolate affected systems to prevent spread"""
        
        if not incident.affected_systems:
            return False
        
        try:
            for system in incident.affected_systems:
                # In a real implementation, this would call system isolation APIs
                logger.warning(f"ISOLATING SYSTEM: {system} for incident {incident.incident_id}")
                
                # Update incident evidence
                if 'isolated_systems' not in incident.evidence:
                    incident.evidence['isolated_systems'] = []
                incident.evidence['isolated_systems'].append({
                    'system': system,
                    'isolated_at': datetime.utcnow().isoformat(),
                    'method': 'automated_response'
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to isolate systems: {str(e)}")
            return False
    
    async def _block_malicious_ips(self, incident: SecurityIncident) -> bool:
        """Block malicious IP addresses"""
        
        malicious_ips = incident.evidence.get('malicious_ips', [])
        if not malicious_ips:
            # Extract IPs from evidence
            source_ip = incident.evidence.get('source_ip')
            if source_ip:
                malicious_ips = [source_ip]
        
        if not malicious_ips:
            return False
        
        try:
            for ip in malicious_ips:
                # In a real implementation, this would call firewall/WAF APIs
                logger.warning(f"BLOCKING IP: {ip} for incident {incident.incident_id}")
            
            incident.evidence['blocked_ips'] = malicious_ips
            incident.evidence['blocked_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to block IPs: {str(e)}")
            return False
    
    async def _disable_affected_users(self, incident: SecurityIncident) -> bool:
        """Disable affected user accounts"""
        
        if not incident.affected_users:
            return False
        
        try:
            for user_id in incident.affected_users:
                # In a real implementation, this would call user management APIs
                logger.warning(f"DISABLING USER: {user_id} for incident {incident.incident_id}")
            
            incident.evidence['disabled_users'] = incident.affected_users
            incident.evidence['disabled_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable users: {str(e)}")
            return False
    
    async def _quarantine_malicious_files(self, incident: SecurityIncident) -> bool:
        """Quarantine malicious files"""
        
        malicious_files = incident.evidence.get('malicious_files', [])
        if not malicious_files:
            return False
        
        try:
            for file_path in malicious_files:
                # In a real implementation, this would move files to quarantine
                logger.warning(f"QUARANTINING FILE: {file_path} for incident {incident.incident_id}")
            
            incident.evidence['quarantined_files'] = malicious_files
            incident.evidence['quarantined_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to quarantine files: {str(e)}")
            return False
    
    async def _backup_critical_data(self, incident: SecurityIncident) -> bool:
        """Backup critical data before potential loss"""
        
        try:
            # In a real implementation, this would trigger backup systems
            logger.info(f"BACKING UP CRITICAL DATA for incident {incident.incident_id}")
            
            incident.evidence['backup_initiated'] = True
            incident.evidence['backup_at'] = datetime.utcnow().isoformat()
            incident.evidence['backup_id'] = f"backup_{incident.incident_id}_{datetime.utcnow().timestamp()}"
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup data: {str(e)}")
            return False
    
    async def _reset_compromised_credentials(self, incident: SecurityIncident) -> bool:
        """Reset compromised user credentials"""
        
        if not incident.affected_users:
            return False
        
        try:
            for user_id in incident.affected_users:
                # In a real implementation, this would force password reset
                logger.warning(f"RESETTING CREDENTIALS: {user_id} for incident {incident.incident_id}")
            
            incident.evidence['credentials_reset'] = incident.affected_users
            incident.evidence['reset_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset credentials: {str(e)}")
            return False
    
    async def _notify_incident_response_team(self, incident: SecurityIncident) -> bool:
        """Notify incident response team"""
        
        try:
            # In a real implementation, this would send notifications via multiple channels
            message = (f"SECURITY INCIDENT ALERT\n"
                      f"ID: {incident.incident_id}\n"
                      f"Type: {incident.incident_type.value}\n"
                      f"Severity: {incident.severity.value}\n"
                      f"Title: {incident.title}\n"
                      f"Description: {incident.description}")
            
            logger.critical(f"INCIDENT TEAM NOTIFICATION: {message}")
            
            # Send to configured notification channels
            for channel, handler in self.notification_handlers.items():
                try:
                    await handler(incident, message)
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel}: {str(e)}")
            
            incident.evidence['team_notified'] = True
            incident.evidence['notified_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify team: {str(e)}")
            return False
    
    async def _escalate_to_management(self, incident: SecurityIncident) -> bool:
        """Escalate incident to management"""
        
        try:
            # In a real implementation, this would escalate via management channels
            logger.critical(f"MANAGEMENT ESCALATION: Incident {incident.incident_id} - {incident.title}")
            
            incident.evidence['escalated_to_management'] = True
            incident.evidence['escalated_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to escalate to management: {str(e)}")
            return False
    
    async def _contact_law_enforcement(self, incident: SecurityIncident) -> bool:
        """Contact law enforcement for serious incidents"""
        
        try:
            # In a real implementation, this would follow legal procedures
            logger.critical(f"LAW ENFORCEMENT CONTACT: Incident {incident.incident_id} - Criminal activity suspected")
            
            incident.evidence['law_enforcement_contacted'] = True
            incident.evidence['contact_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to contact law enforcement: {str(e)}")
            return False
    
    async def _activate_business_continuity_plan(self, incident: SecurityIncident) -> bool:
        """Activate business continuity plan"""
        
        try:
            # In a real implementation, this would trigger BCP procedures
            logger.critical(f"BUSINESS CONTINUITY ACTIVATION: Incident {incident.incident_id}")
            
            incident.evidence['bcp_activated'] = True
            incident.evidence['bcp_activated_at'] = datetime.utcnow().isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate BCP: {str(e)}")
            return False
    
    async def _auto_assign_incident(self, incident -> None: SecurityIncident) -> None:
        """Automatically assign incident based on type and severity"""
        
        # Assignment logic based on incident characteristics
        assignment_rules = {
            (IncidentType.DATA_BREACH, IncidentSeverity.CRITICAL): "senior_security_analyst",
            (IncidentType.MALWARE_INFECTION, IncidentSeverity.HIGH): "malware_specialist",
            (IncidentType.DDoS_ATTACK, IncidentSeverity.HIGH): "network_security_team",
            (IncidentType.COMPLIANCE_VIOLATION, IncidentSeverity.MEDIUM): "compliance_officer"
        }
        
        assignee = assignment_rules.get((incident.incident_type, incident.severity), "security_analyst")
        
        incident.assigned_to = assignee
        incident.status = IncidentStatus.ASSIGNED
        incident.add_timeline_entry(
            "assignment",
            f"Incident auto-assigned to {assignee}",
            "system"
        )
    
    async def _send_incident_notifications(self, incident -> None: SecurityIncident) -> None:
        """Send incident notifications based on severity and type"""
        
        # Determine notification recipients based on severity
        if incident.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
            recipients = ["security_team", "management", "on_call_engineer"]
        elif incident.severity == IncidentSeverity.MEDIUM:
            recipients = ["security_team", "assigned_analyst"]
        else:
            recipients = ["assigned_analyst"]
        
        for recipient in recipients:
            try:
                await self._send_notification(recipient, incident)
            except Exception as e:
                logger.error(f"Failed to notify {recipient}: {str(e)}")
    
    async def _send_notification(self, recipient -> None: str, incident -> None: SecurityIncident) -> None:
        """Send notification to specific recipient"""
        
        # In a real implementation, this would use various notification channels
        logger.info(f"NOTIFICATION to {recipient}: Incident {incident.incident_id} - {incident.title}")
    
    async def _check_escalation_triggers(self, incident -> None: SecurityIncident) -> None:
        """Check if incident meets escalation criteria"""
        
        escalation_triggers = self.escalation_chains.get(incident.incident_type.value, {})
        
        # Time-based escalation
        if incident.severity == IncidentSeverity.CRITICAL:
            # Critical incidents escalate immediately
            await self._escalate_incident(incident, "severity_critical")
        
        # Impact-based escalation
        if len(incident.affected_systems) > 5:
            await self._escalate_incident(incident, "widespread_impact")
        
        if len(incident.affected_users) > 100:
            await self._escalate_incident(incident, "mass_user_impact")
    
    async def _escalate_incident(self, incident -> None: SecurityIncident, reason -> None: str) -> None:
        """Escalate incident to higher level"""
        
        logger.warning(f"ESCALATING INCIDENT {incident.incident_id}: {reason}")
        
        incident.add_timeline_entry(
            "escalation",
            f"Incident escalated: {reason}",
            "system"
        )
        
        # Execute escalation actions
        await self._execute_response_action(ResponseAction.ESCALATE_MANAGEMENT, incident)
    
    def update_incident_status(self, 
                             incident_id: str, 
                             new_status: IncidentStatus,
                             user: str = "system",
                             notes: str = "") -> bool:
        """Update incident status"""
        
        incident = self.get_incident_by_id(incident_id)
        if not incident:
            return False
        
        old_status = incident.status
        incident.status = new_status
        
        # Close incident if status is CLOSED
        if new_status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.utcnow()
        
        # Add timeline entry
        description = f"Status changed from {old_status.value} to {new_status.value}"
        if notes:
            description += f" - Notes: {notes}"
        
        incident.add_timeline_entry(
            "status_update",
            description,
            user
        )
        
        logger.info(f"Incident {incident_id} status updated to {new_status.value}")
        return True
    
    def add_incident_evidence(self,
                            incident_id: str,
                            evidence_type: str,
                            evidence_data: Any,
                            user: str = "system") -> bool:
        """Add evidence to an incident"""
        
        incident = self.get_incident_by_id(incident_id)
        if not incident:
            return False
        
        incident.evidence[evidence_type] = evidence_data
        incident.add_timeline_entry(
            "evidence_added",
            f"Evidence added: {evidence_type}",
            user
        )
        
        return True
    
    def get_incident_by_id(self, incident_id: str) -> Optional[SecurityIncident]:
        """Get incident by ID"""
        
        for incident in self.incidents:
            if incident.incident_id == incident_id:
                return incident
        
        return None
    
    def get_incidents_by_status(self, status: IncidentStatus) -> List[SecurityIncident]:
        """Get incidents by status"""
        
        return [incident for incident in self.incidents if incident.status == status]
    
    def get_open_incidents(self) -> List[SecurityIncident]:
        """Get all open incidents"""
        
        return [
            incident for incident in self.incidents
            if incident.status != IncidentStatus.CLOSED
        ]
    
    def generate_incident_report(self, incident_id: str) -> Optional[IncidentReport]:
        """Generate comprehensive incident report"""
        
        incident = self.get_incident_by_id(incident_id)
        if not incident:
            return None
        
        try:
            # Generate incident summary
            summary = (f"Security incident {incident.incident_id} of type {incident.incident_type.value} "
                      f"with {incident.severity.value} severity was detected on {incident.detected_at}. "
                      f"Current status: {incident.status.value}.")
            
            # Analyze impact
            impact_analysis = self._analyze_incident_impact(incident)
            
            # Generate recommendations
            recommendations = self._generate_incident_recommendations(incident)
            
            # Check compliance implications
            compliance_implications = self._assess_compliance_implications(incident)
            
            report = IncidentReport(
                report_id=f"RPT-{incident.incident_id}",
                incident_id=incident.incident_id,
                generated_at=datetime.utcnow(),
                incident_summary=summary,
                impact_analysis=impact_analysis,
                response_timeline=incident.timeline,
                actions_taken=incident.response_actions,
                lessons_learned=incident.lessons_learned,
                recommendations=recommendations,
                compliance_implications=compliance_implications
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating incident report: {str(e)}")
            return None
    
    def _analyze_incident_impact(self, incident: SecurityIncident) -> str:
        """Analyze incident impact"""
        
        impact_factors = []
        
        if incident.affected_systems:
            impact_factors.append(f"{len(incident.affected_systems)} systems affected")
        
        if incident.affected_users:
            impact_factors.append(f"{len(incident.affected_users)} users affected")
        
        if incident.severity == IncidentSeverity.CRITICAL:
            impact_factors.append("Critical business operations impacted")
        
        if incident.incident_type == IncidentType.DATA_BREACH:
            impact_factors.append("Potential data confidentiality breach")
        
        return "; ".join(impact_factors) if impact_factors else "Impact assessment pending"
    
    def _generate_incident_recommendations(self, incident: SecurityIncident) -> List[str]:
        """Generate recommendations based on incident"""
        
        recommendations = []
        
        if incident.incident_type == IncidentType.UNAUTHORIZED_ACCESS:
            recommendations.extend([
                "Review and strengthen access controls",
                "Implement additional authentication factors",
                "Conduct access audit for affected systems"
            ])
        
        elif incident.incident_type == IncidentType.MALWARE_INFECTION:
            recommendations.extend([
                "Update antivirus definitions",
                "Enhance email security filtering",
                "Conduct security awareness training"
            ])
        
        elif incident.incident_type == IncidentType.DATA_BREACH:
            recommendations.extend([
                "Implement data loss prevention tools",
                "Encrypt sensitive data at rest and in transit",
                "Review data access permissions"
            ])
        
        # Generic recommendations
        recommendations.extend([
            "Update incident response procedures based on lessons learned",
            "Conduct security assessment of affected systems",
            "Review and update security monitoring"
        ])
        
        return recommendations
    
    def _assess_compliance_implications(self, incident: SecurityIncident) -> List[str]:
        """Assess compliance implications"""
        
        implications = []
        
        if incident.incident_type == IncidentType.DATA_BREACH:
            implications.extend([
                "GDPR breach notification may be required within 72 hours",
                "CCPA notification to affected California residents",
                "Consider credit monitoring for affected users"
            ])
        
        if incident.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
            implications.append("Regulatory reporting may be required")
        
        if 'pii_exposed' in incident.evidence:
            implications.append("Personal data breach - privacy impact assessment needed")
        
        return implications
    
    def _initialize_response_plans(self) -> Dict[str, ResponsePlan]:
        """Initialize automated response plans"""
        
        plans = [
            ResponsePlan(
                plan_id="data_breach_response",
                incident_types=[IncidentType.DATA_BREACH],
                severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
                automated_actions=[
                    ResponseAction.ISOLATE_SYSTEM,
                    ResponseAction.BACKUP_DATA,
                    ResponseAction.NOTIFY_TEAM,
                    ResponseAction.ESCALATE_MANAGEMENT
                ],
                escalation_rules={'immediate': True},
                notification_rules={'management': True, 'legal': True},
                containment_procedures=['Isolate affected systems', 'Preserve evidence'],
                recovery_procedures=['Restore from clean backup', 'Verify system integrity']
            ),
            ResponsePlan(
                plan_id="malware_response",
                incident_types=[IncidentType.MALWARE_INFECTION],
                severity_levels=[IncidentSeverity.MEDIUM, IncidentSeverity.HIGH],
                automated_actions=[
                    ResponseAction.ISOLATE_SYSTEM,
                    ResponseAction.QUARANTINE_FILE,
                    ResponseAction.NOTIFY_TEAM
                ],
                escalation_rules={'time_threshold': 30},
                notification_rules={'security_team': True},
                containment_procedures=['Quarantine infected systems', 'Update AV signatures'],
                recovery_procedures=['Clean infected systems', 'Restore from backup']
            ),
            ResponsePlan(
                plan_id="ddos_response",
                incident_types=[IncidentType.DDoS_ATTACK],
                severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
                automated_actions=[
                    ResponseAction.BLOCK_IP,
                    ResponseAction.ACTIVATE_BCP,
                    ResponseAction.NOTIFY_TEAM
                ],
                escalation_rules={'traffic_threshold': 10000},
                notification_rules={'network_team': True, 'management': True},
                containment_procedures=['Enable DDoS protection', 'Block attack sources'],
                recovery_procedures=['Monitor traffic normalization', 'Restore full service']
            )
        ]
        
        return {plan.plan_id: plan for plan in plans}
    
    def _initialize_escalation_chains(self) -> Dict[str, Any]:
        """Initialize escalation chains"""
        
        return {
            'data_breach': {
                'level_1': 'security_analyst',
                'level_2': 'security_manager',
                'level_3': 'ciso',
                'level_4': 'ceo'
            },
            'unauthorized_access': {
                'level_1': 'security_analyst',
                'level_2': 'security_manager'
            },
            'compliance_violation': {
                'level_1': 'compliance_officer',
                'level_2': 'legal_counsel',
                'level_3': 'ciso'
            }
        }
    
    def _initialize_sla_thresholds(self) -> Dict[str, timedelta]:
        """Initialize SLA thresholds for incident response"""
        
        return {
            'critical_response_time': timedelta(minutes=15),
            'high_response_time': timedelta(hours=1),
            'medium_response_time': timedelta(hours=4),
            'low_response_time': timedelta(hours=24),
            'critical_resolution_time': timedelta(hours=4),
            'high_resolution_time': timedelta(hours=24),
            'medium_resolution_time': timedelta(days=3),
            'low_resolution_time': timedelta(days=7)
        }
    
    def _maintain_incident_history(self) -> None:
        """Maintain incident history size"""
        
        if len(self.incidents) > self.max_incident_history:
            # Keep only the most recent incidents
            self.incidents = sorted(self.incidents, key=lambda x: x.detected_at)[-self.max_incident_history:]
    
    def _create_disabled_incident(self, title: str, description: str) -> SecurityIncident:
        """Create incident when handler is disabled"""
        
        return SecurityIncident(
            incident_id="DISABLED",
            incident_type=IncidentType.SYSTEM_COMPROMISE,
            severity=IncidentSeverity.LOW,
            status=IncidentStatus.NEW,
            title=title,
            description=f"Handler disabled: {description}",
            detected_at=datetime.utcnow(),
            reported_by="system"
        )
    
    def _create_error_incident(self, title: str, description: str, error: str) -> SecurityIncident:
        """Create incident when handling fails"""
        
        return SecurityIncident(
            incident_id="ERROR",
            incident_type=IncidentType.SYSTEM_COMPROMISE,
            severity=IncidentSeverity.MEDIUM,
            status=IncidentStatus.NEW,
            title=f"Error: {title}",
            description=f"Handler error: {error}. Original: {description}",
            detected_at=datetime.utcnow(),
            reported_by="system"
        )
    
    def register_notification_handler(self, channel -> None: str, handler -> None: Callable) -> None:
        """Register notification handler for specific channel"""
        
        self.notification_handlers[channel] = handler
        logger.info(f"Notification handler registered for channel: {channel}")
    
    def get_incident_statistics(self) -> Dict[str, Any]:
        """Get incident response statistics"""
        
        if not self.incidents:
            return {
                'total_incidents': 0,
                'by_type': {},
                'by_severity': {},
                'by_status': {},
                'avg_response_time': 0.0,
                'sla_compliance': 0.0
            }
        
        # Count by various dimensions
        by_type = {}
        by_severity = {}
        by_status = {}
        
        for incident in self.incidents:
            # By type
            incident_type = incident.incident_type.value
            by_type[incident_type] = by_type.get(incident_type, 0) + 1
            
            # By severity
            severity = incident.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # By status
            status = incident.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        # Calculate average response time
        response_times = []
        for incident in self.incidents:
            if incident.timeline:
                first_response = next((entry for entry in incident.timeline 
                                     if entry['action'] in ['assignment', 'automated_action']), None)
                if first_response:
                    response_time = datetime.fromisoformat(first_response['timestamp']) - incident.detected_at
                    response_times.append(response_time.total_seconds())
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return {
            'total_incidents': len(self.incidents),
            'by_type': by_type,
            'by_severity': by_severity,
            'by_status': by_status,
            'avg_response_time': avg_response_time,
            'open_incidents': len(self.get_open_incidents()),
            'automation_enabled': self.automation_enabled
        }
    
    def enable_handler(self) -> None:
        """Enable incident response handler"""
        self.enabled = True
        logger.info("Incident response handler enabled")
    
    def disable_handler(self) -> None:
        """Disable incident response handler"""
        self.enabled = False
        logger.info("Incident response handler disabled")
    
    def enable_automation(self) -> None:
        """Enable automated response actions"""
        self.automation_enabled = True
        logger.info("Automated incident response enabled")
    
    def disable_automation(self) -> None:
        """Disable automated response actions"""
        self.automation_enabled = False
        logger.info("Automated incident response disabled")


# Export for module use
__all__ = ['IncidentResponseHandler', 'SecurityIncident', 'IncidentReport', 'IncidentType', 'IncidentSeverity', 'IncidentStatus']