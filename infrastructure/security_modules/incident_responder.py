"""Infrastructure Security Incident Response - Enterprise Incident Management
=========================================================================

Advanced security incident response system for automated threat detection,
incident coordination, forensic analysis, and business continuity management.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Security Specialist + DevOps + Incident Response Expert
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL SECURITY WARNING ⚠️
This incident response system contains advanced security algorithms and enterprise
threat response frameworks belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED ACCESS OR MODIFICATION IS STRICTLY PROHIBITED.
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import hashlib
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "critical"  # System down, data breach
    HIGH = "high"         # Significant impact, security threat
    MEDIUM = "medium"     # Moderate impact, performance degradation
    LOW = "low"           # Minor issue, informational
    INFO = "info"         # Monitoring alert, no immediate action

class IncidentStatus(Enum):
    """Incident status tracking"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"

class IncidentCategory(Enum):
    """Incident categories"""
    SECURITY_BREACH = "security_breach"
    DATA_BREACH = "data_breach"
    SYSTEM_OUTAGE = "system_outage"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    NETWORK_ISSUE = "network_issue"
    AUTHENTICATION_FAILURE = "authentication_failure"
    COMPLIANCE_VIOLATION = "compliance_violation"
    MALWARE_DETECTION = "malware_detection"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

@dataclass
class IncidentResponse:
    """Incident response definition"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    status: IncidentStatus = IncidentStatus.NEW
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    escalation_level: int = 0
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    containment_actions: List[Dict[str, Any]] = field(default_factory=list)
    recovery_actions: List[Dict[str, Any]] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    compliance_requirements: List[str] = field(default_factory=list)
    communication_log: List[Dict[str, Any]] = field(default_factory=list)

class SecurityIncidentResponder:
    """Enterprise security incident response system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.incidents: Dict[str, IncidentResponse] = {}
        self.response_playbooks: Dict[str, Dict[str, Any]] = {}
        self.escalation_matrix: Dict[str, List[str]] = {}
        self.notification_channels: Dict[str, Any] = {}
        self.automated_responses: Dict[str, Callable] = {}
        self.forensic_tools: Dict[str, Any] = {}
        self.compliance_frameworks = ["GDPR", "PCI-DSS", "SOC2", "ISO27001", "CCPA"]
        self.logger = logging.getLogger(__name__)
        
        # SLA targets by severity
        self.sla_targets = {
            IncidentSeverity.CRITICAL: {"response_time": 15, "resolution_time": 240},  # 15min, 4h
            IncidentSeverity.HIGH: {"response_time": 60, "resolution_time": 720},      # 1h, 12h
            IncidentSeverity.MEDIUM: {"response_time": 240, "resolution_time": 1440},   # 4h, 24h
            IncidentSeverity.LOW: {"response_time": 480, "resolution_time": 2880},      # 8h, 48h
            IncidentSeverity.INFO: {"response_time": 1440, "resolution_time": 4320}     # 24h, 72h
        }
    
    async def initialize(self) -> bool:
        """Initialize incident response system"""
        try:
            await self._setup_response_playbooks()
            await self._configure_escalation_matrix()
            await self._setup_notification_channels()
            await self._initialize_automated_responses()
            await self._setup_forensic_tools()
            self.logger.info("Security incident response system initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize incident response system: {e}")
            return False
    
    async def create_incident(self, incident_data: Dict[str, Any]) -> str:
        """Create new security incident"""
        try:
            # Generate unique incident ID
            incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create incident object
            incident = IncidentResponse(
                incident_id=incident_id,
                title=incident_data.get("title", "Unknown Incident"),
                description=incident_data.get("description", ""),
                severity=IncidentSeverity(incident_data.get("severity", "medium")),
                category=IncidentCategory(incident_data.get("category", "infrastructure_failure")),
                affected_systems=incident_data.get("affected_systems", []),
                affected_users=incident_data.get("affected_users", []),
                compliance_requirements=incident_data.get("compliance_requirements", [])
            )
            
            # Store incident
            self.incidents[incident_id] = incident
            
            # Add initial timeline entry
            await self._add_timeline_entry(incident_id, "incident_created", {
                "description": "Incident created and logged",
                "severity": incident.severity.value,
                "category": incident.category.value
            })
            
            # Trigger immediate response
            await self._trigger_immediate_response(incident)
            
            # Send initial notifications
            await self._send_incident_notifications(incident, "created")
            
            self.logger.info(f"Security incident created: {incident_id}")
            return incident_id
        
        except Exception as e:
            self.logger.error(f"Failed to create incident: {e}")
            return None
    
    async def update_incident_status(self, incident_id: str, new_status: IncidentStatus, 
                                  update_notes: Optional[str] = None) -> bool:
        """Update incident status"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            old_status = incident.status
            incident.status = new_status
            incident.updated_at = datetime.utcnow()
            
            # Add timeline entry
            await self._add_timeline_entry(incident_id, "status_changed", {
                "old_status": old_status.value,
                "new_status": new_status.value,
                "notes": update_notes or "Status updated"
            })
            
            # Trigger status-specific actions
            await self._handle_status_change(incident, old_status, new_status)
            
            # Send notifications
            await self._send_incident_notifications(incident, "status_updated")
            
            self.logger.info(f"Incident {incident_id} status updated: {old_status.value} -> {new_status.value}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to update incident status: {e}")
            return False
    
    async def escalate_incident(self, incident_id: str, escalation_reason: str) -> bool:
        """Escalate incident to higher level"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            incident.escalation_level += 1
            incident.status = IncidentStatus.ESCALATED
            incident.updated_at = datetime.utcnow()
            
            # Add timeline entry
            await self._add_timeline_entry(incident_id, "escalated", {
                "escalation_level": incident.escalation_level,
                "reason": escalation_reason
            })
            
            # Get escalation contacts
            escalation_contacts = self.escalation_matrix.get(
                f"level_{incident.escalation_level}", 
                self.escalation_matrix.get("default", [])
            )
            
            # Send escalation notifications
            await self._send_escalation_notifications(incident, escalation_contacts, escalation_reason)
            
            # Auto-assign to escalation team
            if escalation_contacts:
                incident.assigned_to = escalation_contacts[0]
            
            self.logger.warning(f"Incident {incident_id} escalated to level {incident.escalation_level}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to escalate incident: {e}")
            return False
    
    async def add_evidence(self, incident_id: str, evidence_data: Dict[str, Any]) -> bool:
        """Add forensic evidence to incident"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            
            # Create evidence entry
            evidence_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "type": evidence_data.get("type", "unknown"),
                "description": evidence_data.get("description", ""),
                "source": evidence_data.get("source", ""),
                "hash": self._calculate_evidence_hash(evidence_data),
                "chain_of_custody": [
                    {
                        "action": "collected",
                        "timestamp": datetime.utcnow().isoformat(),
                        "user": evidence_data.get("collected_by", "system")
                    }
                ]
            }
            
            incident.evidence.append(evidence_entry)
            incident.updated_at = datetime.utcnow()
            
            # Add timeline entry
            await self._add_timeline_entry(incident_id, "evidence_added", {
                "evidence_id": evidence_entry["id"],
                "evidence_type": evidence_entry["type"],
                "description": evidence_entry["description"]
            })
            
            self.logger.info(f"Evidence added to incident {incident_id}: {evidence_entry['id']}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to add evidence: {e}")
            return False
    
    async def execute_containment_action(self, incident_id: str, action_data: Dict[str, Any]) -> bool:
        """Execute containment action"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            
            # Create containment action
            action = {
                "id": str(uuid.uuid4()),
                "type": action_data.get("type", "manual"),
                "description": action_data.get("description", ""),
                "executed_at": datetime.utcnow().isoformat(),
                "executed_by": action_data.get("executed_by", "system"),
                "status": "pending",
                "result": None
            }
            
            # Execute action based on type
            if action["type"] == "isolate_system":
                result = await self._isolate_system(action_data.get("system_id"))
            elif action["type"] == "block_ip":
                result = await self._block_ip_address(action_data.get("ip_address"))
            elif action["type"] == "disable_user":
                result = await self._disable_user_account(action_data.get("user_id"))
            elif action["type"] == "quarantine_file":
                result = await self._quarantine_file(action_data.get("file_path"))
            elif action["type"] == "network_segment":
                result = await self._network_segmentation(action_data.get("segment_config"))
            else:
                result = {"success": False, "message": "Unknown action type"}
            
            # Update action with result
            action["status"] = "completed" if result.get("success") else "failed"
            action["result"] = result
            
            incident.containment_actions.append(action)
            incident.updated_at = datetime.utcnow()
            
            # Add timeline entry
            await self._add_timeline_entry(incident_id, "containment_action", {
                "action_id": action["id"],
                "action_type": action["type"],
                "status": action["status"],
                "result": result.get("message", "")
            })
            
            self.logger.info(f"Containment action executed for incident {incident_id}: {action['type']}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to execute containment action: {e}")
            return False
    
    async def generate_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Generate comprehensive incident report"""
        try:
            if incident_id not in self.incidents:
                return {"error": "Incident not found"}
            
            incident = self.incidents[incident_id]
            
            # Calculate metrics
            response_time = self._calculate_response_time(incident)
            resolution_time = self._calculate_resolution_time(incident)
            sla_compliance = self._check_sla_compliance(incident, response_time, resolution_time)
            
            report = {
                "incident_summary": {
                    "incident_id": incident.incident_id,
                    "title": incident.title,
                    "description": incident.description,
                    "severity": incident.severity.value,
                    "category": incident.category.value,
                    "status": incident.status.value,
                    "created_at": incident.created_at.isoformat(),
                    "updated_at": incident.updated_at.isoformat(),
                    "escalation_level": incident.escalation_level
                },
                "affected_resources": {
                    "systems": incident.affected_systems,
                    "users": incident.affected_users,
                    "system_count": len(incident.affected_systems),
                    "user_count": len(incident.affected_users)
                },
                "timeline": incident.timeline,
                "evidence": {
                    "evidence_items": len(incident.evidence),
                    "evidence_list": incident.evidence
                },
                "response_actions": {
                    "containment_actions": len(incident.containment_actions),
                    "recovery_actions": len(incident.recovery_actions),
                    "containment_details": incident.containment_actions,
                    "recovery_details": incident.recovery_actions
                },
                "metrics": {
                    "response_time_minutes": response_time,
                    "resolution_time_minutes": resolution_time,
                    "sla_compliance": sla_compliance,
                    "escalation_level": incident.escalation_level
                },
                "compliance": {
                    "requirements": incident.compliance_requirements,
                    "breach_notifications": self._get_breach_notifications_required(incident)
                },
                "lessons_learned": incident.lessons_learned,
                "communication_log": incident.communication_log,
                "generated_at": datetime.utcnow().isoformat(),
                "generated_by": "security_incident_responder"
            }
            
            return report
        
        except Exception as e:
            self.logger.error(f"Failed to generate incident report: {e}")
            return {"error": str(e)}
    
    async def _trigger_immediate_response(self, incident: IncidentResponse):
        """Trigger immediate automated response based on incident"""
        try:
            # Get response playbook
            playbook = self.response_playbooks.get(incident.category.value, {})
            
            # Execute immediate actions
            immediate_actions = playbook.get("immediate_actions", [])
            for action in immediate_actions:
                if incident.severity.value in action.get("severity_levels", []):
                    await self._execute_automated_action(incident, action)
            
            # Auto-assign based on severity and category
            await self._auto_assign_incident(incident)
            
            # Check for compliance requirements
            await self._check_compliance_requirements(incident)
        
        except Exception as e:
            self.logger.error(f"Failed to trigger immediate response: {e}")
    
    async def _execute_automated_action(self, incident: IncidentResponse, action: Dict[str, Any]):
        """Execute automated response action"""
        try:
            action_type = action.get("type")
            
            if action_type == "auto_containment":
                await self._auto_containment(incident, action)
            elif action_type == "evidence_collection":
                await self._auto_evidence_collection(incident, action)
            elif action_type == "notification":
                await self._auto_notification(incident, action)
            elif action_type == "system_isolation":
                await self._auto_system_isolation(incident, action)
            
        except Exception as e:
            self.logger.error(f"Failed to execute automated action: {e}")
    
    async def _auto_containment(self, incident: IncidentResponse, action: Dict[str, Any]):
        """Execute automated containment"""
        if incident.category == IncidentCategory.SECURITY_BREACH:
            # Auto-isolate affected systems
            for system in incident.affected_systems:
                await self.execute_containment_action(incident.incident_id, {
                    "type": "isolate_system",
                    "system_id": system,
                    "description": f"Auto-isolation due to security breach",
                    "executed_by": "auto_response_system"
                })
    
    async def _auto_evidence_collection(self, incident: IncidentResponse, action: Dict[str, Any]):
        """Execute automated evidence collection"""
        # Collect system logs
        for system in incident.affected_systems:
            await self.add_evidence(incident.incident_id, {
                "type": "system_logs",
                "description": f"Automated log collection from {system}",
                "source": system,
                "collected_by": "auto_response_system"
            })
    
    async def _isolate_system(self, system_id: str) -> Dict[str, Any]:
        """Isolate system from network"""
        # Implementation would integrate with network management systems
        return {"success": True, "message": f"System {system_id} isolated successfully"}
    
    async def _block_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """Block IP address at firewall level"""
        # Implementation would integrate with firewall management
        return {"success": True, "message": f"IP {ip_address} blocked successfully"}
    
    async def _disable_user_account(self, user_id: str) -> Dict[str, Any]:
        """Disable user account"""
        # Implementation would integrate with identity management systems
        return {"success": True, "message": f"User {user_id} account disabled successfully"}
    
    async def _quarantine_file(self, file_path: str) -> Dict[str, Any]:
        """Quarantine suspicious file"""
        # Implementation would integrate with endpoint protection
        return {"success": True, "message": f"File {file_path} quarantined successfully"}
    
    async def _network_segmentation(self, segment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Implement network segmentation"""
        # Implementation would integrate with SDN controllers
        return {"success": True, "message": "Network segmentation applied successfully"}
    
    async def _add_timeline_entry(self, incident_id: str, event_type: str, event_data: Dict[str, Any]):
        """Add entry to incident timeline"""
        if incident_id in self.incidents:
            timeline_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "data": event_data
            }
            self.incidents[incident_id].timeline.append(timeline_entry)
    
    def _calculate_evidence_hash(self, evidence_data: Dict[str, Any]) -> str:
        """Calculate hash for evidence integrity"""
        evidence_json = json.dumps(evidence_data, sort_keys=True)
        return hashlib.sha256(evidence_json.encode()).hexdigest()
    
    def _calculate_response_time(self, incident: IncidentResponse) -> Optional[int]:
        """Calculate incident response time in minutes"""
        investigating_event = next(
            (event for event in incident.timeline if event["event_type"] == "status_changed" 
             and event["data"].get("new_status") == "investigating"), None
        )
        
        if investigating_event:
            investigating_time = datetime.fromisoformat(investigating_event["timestamp"])
            response_time = (investigating_time - incident.created_at).total_seconds() / 60
            return int(response_time)
        
        return None
    
    def _calculate_resolution_time(self, incident: IncidentResponse) -> Optional[int]:
        """Calculate incident resolution time in minutes"""
        if incident.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
            resolution_time = (incident.updated_at - incident.created_at).total_seconds() / 60
            return int(resolution_time)
        
        return None
    
    def _check_sla_compliance(self, incident: IncidentResponse, response_time: Optional[int], 
                            resolution_time: Optional[int]) -> Dict[str, Any]:
        """Check SLA compliance for incident"""
        sla_target = self.sla_targets.get(incident.severity)
        if not sla_target:
            return {"response": "unknown", "resolution": "unknown"}
        
        compliance = {}
        
        if response_time is not None:
            compliance["response"] = "met" if response_time <= sla_target["response_time"] else "breached"
        else:
            compliance["response"] = "pending"
        
        if resolution_time is not None:
            compliance["resolution"] = "met" if resolution_time <= sla_target["resolution_time"] else "breached"
        else:
            compliance["resolution"] = "pending"
        
        return compliance
    
    def _get_breach_notifications_required(self, incident: IncidentResponse) -> List[str]:
        """Get required breach notifications based on incident"""
        notifications = []
        
        if incident.category in [IncidentCategory.DATA_BREACH, IncidentCategory.SECURITY_BREACH]:
            if "GDPR" in incident.compliance_requirements:
                notifications.append("GDPR_72_HOUR_NOTIFICATION")
            if "CCPA" in incident.compliance_requirements:
                notifications.append("CCPA_NOTIFICATION")
            if "PCI-DSS" in incident.compliance_requirements:
                notifications.append("PCI_INCIDENT_NOTIFICATION")
        
        return notifications
    
    async def _setup_response_playbooks(self):
        """Setup incident response playbooks"""
        self.response_playbooks = {
            "security_breach": {
                "immediate_actions": [
                    {
                        "type": "auto_containment",
                        "severity_levels": ["critical", "high"],
                        "description": "Immediate system isolation"
                    },
                    {
                        "type": "evidence_collection",
                        "severity_levels": ["critical", "high", "medium"],
                        "description": "Automated evidence collection"
                    }
                ]
            },
            "data_breach": {
                "immediate_actions": [
                    {
                        "type": "auto_containment",
                        "severity_levels": ["critical", "high"],
                        "description": "Data access restriction"
                    },
                    {
                        "type": "notification",
                        "severity_levels": ["critical", "high"],
                        "description": "Compliance notification"
                    }
                ]
            }
        }
    
    async def _configure_escalation_matrix(self):
        """Configure escalation matrix"""
        self.escalation_matrix = {
            "level_1": ["security_team_lead", "infrastructure_manager"],
            "level_2": ["security_director", "it_director"],
            "level_3": ["ciso", "cto"],
            "level_4": ["ceo", "legal_counsel"],
            "default": ["security_team_lead"]
        }
    
    async def _setup_notification_channels(self):
        """Setup notification channels"""
        self.notification_channels = {
            "email": {
                "enabled": True,
                "smtp_server": self.config.get("smtp_server", "localhost"),
                "smtp_port": self.config.get("smtp_port", 587)
            },
            "slack": {
                "enabled": self.config.get("slack_enabled", False),
                "webhook_url": self.config.get("slack_webhook_url")
            },
            "sms": {
                "enabled": self.config.get("sms_enabled", False),
                "provider": self.config.get("sms_provider")
            }
        }
    
    async def _send_incident_notifications(self, incident: IncidentResponse, event_type: str):
        """Send incident notifications"""
        try:
            # Email notification
            if self.notification_channels["email"]["enabled"]:
                await self._send_email_notification(incident, event_type)
            
            # Slack notification
            if self.notification_channels["slack"]["enabled"]:
                await self._send_slack_notification(incident, event_type)
            
        except Exception as e:
            self.logger.error(f"Failed to send notifications: {e}")
    
    async def _send_email_notification(self, incident: IncidentResponse, event_type: str):
        """Send email notification"""
        # Email notification implementation
        pass
    
    async def _send_slack_notification(self, incident: IncidentResponse, event_type: str):
        """Send Slack notification"""
        # Slack notification implementation
        pass
    
    async def _send_escalation_notifications(self, incident: IncidentResponse, 
                                          contacts: List[str], reason: str):
        """Send escalation notifications"""
        # Escalation notification implementation
        pass
    
    async def _initialize_automated_responses(self):
        """Initialize automated response handlers"""
        # Setup automated response handlers
        pass
    
    async def _setup_forensic_tools(self):
        """Setup forensic analysis tools"""
        # Setup forensic tools integration
        pass
    
    async def _auto_assign_incident(self, incident: IncidentResponse):
        """Auto-assign incident based on rules"""
        # Auto-assignment logic
        pass
    
    async def _check_compliance_requirements(self, incident: IncidentResponse):
        """Check compliance requirements for incident"""
        # Compliance checking logic
        pass
    
    async def _handle_status_change(self, incident: IncidentResponse, 
                                  old_status: IncidentStatus, new_status: IncidentStatus):
        """Handle incident status change"""
        # Status change handling logic
        pass
    
    async def _auto_notification(self, incident: IncidentResponse, action: Dict[str, Any]):
        """Execute automated notification"""
        # Auto notification logic
        pass
    
    async def _auto_system_isolation(self, incident: IncidentResponse, action: Dict[str, Any]):
        """Execute automated system isolation"""
        # Auto system isolation logic
        pass

# Factory function for easy instantiation
def create_security_incident_responder(config: Optional[Dict[str, Any]] = None) -> SecurityIncidentResponder:
    """Create and configure security incident responder"""
    return SecurityIncidentResponder(config)

# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize incident responder
        responder = create_security_incident_responder({
            "smtp_server": "smtp.company.com",
            "slack_enabled": True,
            "slack_webhook_url": "https://hooks.slack.com/webhook"
        })
        
        await responder.initialize()
        
        # Create example incident
        incident_id = await responder.create_incident({
            "title": "Suspicious Network Activity Detected",
            "description": "Unusual network traffic patterns detected from internal IP",
            "severity": "high",
            "category": "security_breach",
            "affected_systems": ["web-server-01", "database-01"],
            "compliance_requirements": ["GDPR", "SOC2"]
        })
        
        if incident_id:
            print(f"Incident created: {incident_id}")
            
            # Add evidence
            await responder.add_evidence(incident_id, {
                "type": "network_logs",
                "description": "Network traffic logs showing suspicious activity",
                "source": "firewall-01",
                "collected_by": "security_analyst"
            })
            
            # Execute containment
            await responder.execute_containment_action(incident_id, {
                "type": "block_ip",
                "ip_address": "192.168.1.100",
                "description": "Block suspicious IP address",
                "executed_by": "security_analyst"
            })
            
            # Update status
            await responder.update_incident_status(
                incident_id, 
                IncidentStatus.INVESTIGATING,
                "Investigation started by security team"
            )
            
            # Generate report
            report = await responder.generate_incident_report(incident_id)
            print(f"Incident report: {json.dumps(report, indent=2)}")
    
    asyncio.run(main())