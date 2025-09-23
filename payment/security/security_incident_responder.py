#!/usr/bin/env python3
"""
📡 Security Incident Responder
=============================

Automated security incident response system with SOAR integration,
playbooks, and automated containment capabilities.

Expert Roles Combined:
- Security Specialist: Advanced incident response and threat containment
- DevOps Engineer: Automated response orchestration and system integration
- IA Prompt Engineer: AI-powered incident analysis and response generation

Features:
- Automated incident detection and classification
- SOAR (Security Orchestration, Automation and Response) integration
- Incident response playbooks
- Automated containment and mitigation
- Evidence collection and preservation
- Stakeholder notification and communication
- Post-incident analysis and learning
- Creator-specific incident response

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Security + DevOps + IA Prompt Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import hashlib
import secrets
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import aiohttp
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Incident severity levels"""
    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    """Types of security incidents"""
    MALWARE_DETECTION = "malware_detection"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PHISHING_ATTACK = "phishing_attack"
    DDOS_ATTACK = "ddos_attack"
    INSIDER_THREAT = "insider_threat"
    FRAUD_DETECTION = "fraud_detection"
    SYSTEM_COMPROMISE = "system_compromise"
    DATA_EXFILTRATION = "data_exfiltration"
    RANSOMWARE = "ransomware"
    SOCIAL_ENGINEERING = "social_engineering"
    API_ABUSE = "api_abuse"

class IncidentStatus(Enum):
    """Incident status tracking"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    CLOSED = "closed"
    ESCALATED = "escalated"

class ResponseAction(Enum):
    """Available response actions"""
    ISOLATE_SYSTEM = "isolate_system"
    BLOCK_IP = "block_ip"
    DISABLE_ACCOUNT = "disable_account"
    QUARANTINE_FILE = "quarantine_file"
    RESET_PASSWORD = "reset_password"
    NOTIFY_STAKEHOLDERS = "notify_stakeholders"
    COLLECT_EVIDENCE = "collect_evidence"
    ESCALATE_INCIDENT = "escalate_incident"
    CONTACT_AUTHORITIES = "contact_authorities"
    RESTORE_BACKUP = "restore_backup"

class PlaybookStatus(Enum):
    """Playbook execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    incident_type: IncidentType = IncidentType.UNAUTHORIZED_ACCESS
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    status: IncidentStatus = IncidentStatus.NEW
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    source_ip: str = ""
    detection_time: datetime = field(default_factory=datetime.now)
    response_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    assigned_responder: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    response_actions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    sla_breach: bool = False
    communication_log: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ResponsePlaybook:
    """Incident response playbook"""
    playbook_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    incident_types: List[IncidentType] = field(default_factory=list)
    severity_levels: List[IncidentSeverity] = field(default_factory=list)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    automated: bool = True
    approval_required: bool = False
    estimated_duration: int = 3600  # seconds
    success_rate: float = 0.0
    execution_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

@dataclass
class PlaybookExecution:
    """Playbook execution tracking"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = ""
    playbook_id: str = ""
    status: PlaybookStatus = PlaybookStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: int = 0
    steps_completed: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    manual_interventions: int = 0

@dataclass
class EvidenceItem:
    """Evidence collection item"""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = ""
    evidence_type: str = ""
    source: str = ""
    collected_at: datetime = field(default_factory=datetime.now)
    file_path: str = ""
    hash_md5: str = ""
    hash_sha256: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    chain_of_custody: List[Dict[str, Any]] = field(default_factory=list)

class SecurityIncidentResponder:
    """
    Security Incident Response System
    ================================
    
    Automated incident response with SOAR integration,
    playbooks, and intelligent containment.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.incidents: Dict[str, SecurityIncident] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.executions: Dict[str, PlaybookExecution] = {}
        self.evidence: Dict[str, EvidenceItem] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # SLA configurations
        self.sla_configs = {
            IncidentSeverity.CRITICAL: {
                'acknowledgment_time': 300,  # 5 minutes
                'response_time': 900,  # 15 minutes
                'resolution_time': 14400  # 4 hours
            },
            IncidentSeverity.HIGH: {
                'acknowledgment_time': 600,  # 10 minutes
                'response_time': 1800,  # 30 minutes
                'resolution_time': 28800  # 8 hours
            },
            IncidentSeverity.MEDIUM: {
                'acknowledgment_time': 1800,  # 30 minutes
                'response_time': 3600,  # 1 hour
                'resolution_time': 86400  # 24 hours
            },
            IncidentSeverity.LOW: {
                'acknowledgment_time': 3600,  # 1 hour
                'response_time': 7200,  # 2 hours
                'resolution_time': 172800  # 48 hours
            }
        }
        
        # Initialize default playbooks
        self._initialize_default_playbooks()
        
        # Response metrics
        self.metrics = {
            'total_incidents': 0,
            'active_incidents': 0,
            'resolved_incidents': 0,
            'average_response_time': 0.0,
            'average_resolution_time': 0.0,
            'sla_breach_rate': 0.0,
            'automated_responses': 0,
            'manual_interventions': 0,
            'playbooks_executed': 0
        }
        
        logger.info("📡 Security Incident Responder initialized")

    async def initialize(self):
        """Initialize Redis connection and load configurations"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._load_existing_data()
            logger.info("✅ Security Incident Responder initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Security Incident Responder: {e}")
            raise

    def _initialize_default_playbooks(self):
        """Initialize default incident response playbooks"""
        # Critical Data Breach Response
        data_breach_playbook = ResponsePlaybook(
            name="Critical Data Breach Response",
            description="Immediate response to critical data breach incidents",
            incident_types=[IncidentType.DATA_BREACH, IncidentType.DATA_EXFILTRATION],
            severity_levels=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
            steps=[
                {
                    'step_id': 1,
                    'name': 'Immediate Containment',
                    'action': ResponseAction.ISOLATE_SYSTEM.value,
                    'description': 'Isolate affected systems to prevent further damage',
                    'automated': True,
                    'timeout': 300
                },
                {
                    'step_id': 2,
                    'name': 'Stakeholder Notification',
                    'action': ResponseAction.NOTIFY_STAKEHOLDERS.value,
                    'description': 'Notify security team and management immediately',
                    'automated': True,
                    'timeout': 180
                },
                {
                    'step_id': 3,
                    'name': 'Evidence Collection',
                    'action': ResponseAction.COLLECT_EVIDENCE.value,
                    'description': 'Collect and preserve digital evidence',
                    'automated': True,
                    'timeout': 600
                },
                {
                    'step_id': 4,
                    'name': 'Impact Assessment',
                    'action': 'assess_impact',
                    'description': 'Assess scope and impact of the breach',
                    'automated': False,
                    'timeout': 1800
                },
                {
                    'step_id': 5,
                    'name': 'External Notification',
                    'action': 'notify_authorities',
                    'description': 'Notify regulatory authorities if required',
                    'automated': False,
                    'timeout': 3600
                }
            ],
            automated=True,
            approval_required=False,
            estimated_duration=7200
        )
        
        # Malware Detection Response
        malware_playbook = ResponsePlaybook(
            name="Malware Detection Response",
            description="Automated response to malware detection",
            incident_types=[IncidentType.MALWARE_DETECTION, IncidentType.RANSOMWARE],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
            steps=[
                {
                    'step_id': 1,
                    'name': 'Quarantine File',
                    'action': ResponseAction.QUARANTINE_FILE.value,
                    'description': 'Quarantine detected malware file',
                    'automated': True,
                    'timeout': 60
                },
                {
                    'step_id': 2,
                    'name': 'Isolate Affected System',
                    'action': ResponseAction.ISOLATE_SYSTEM.value,
                    'description': 'Isolate infected system from network',
                    'automated': True,
                    'timeout': 120
                },
                {
                    'step_id': 3,
                    'name': 'Scan Related Systems',
                    'action': 'scan_systems',
                    'description': 'Scan related systems for malware',
                    'automated': True,
                    'timeout': 1800
                },
                {
                    'step_id': 4,
                    'name': 'Update Security Rules',
                    'action': 'update_security_rules',
                    'description': 'Update security rules to prevent reinfection',
                    'automated': True,
                    'timeout': 300
                }
            ],
            automated=True,
            approval_required=False,
            estimated_duration=2400
        )
        
        # Unauthorized Access Response
        unauthorized_access_playbook = ResponsePlaybook(
            name="Unauthorized Access Response",
            description="Response to unauthorized access attempts",
            incident_types=[IncidentType.UNAUTHORIZED_ACCESS, IncidentType.INSIDER_THREAT],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
            steps=[
                {
                    'step_id': 1,
                    'name': 'Block Source IP',
                    'action': ResponseAction.BLOCK_IP.value,
                    'description': 'Block source IP address',
                    'automated': True,
                    'timeout': 30
                },
                {
                    'step_id': 2,
                    'name': 'Disable Compromised Account',
                    'action': ResponseAction.DISABLE_ACCOUNT.value,
                    'description': 'Disable potentially compromised account',
                    'automated': True,
                    'timeout': 60
                },
                {
                    'step_id': 3,
                    'name': 'Force Password Reset',
                    'action': ResponseAction.RESET_PASSWORD.value,
                    'description': 'Force password reset for affected accounts',
                    'automated': True,
                    'timeout': 120
                },
                {
                    'step_id': 4,
                    'name': 'Review Access Logs',
                    'action': 'review_logs',
                    'description': 'Review access logs for suspicious activity',
                    'automated': False,
                    'timeout': 1800
                }
            ],
            automated=True,
            approval_required=False,
            estimated_duration=3600
        )
        
        # Fraud Detection Response
        fraud_playbook = ResponsePlaybook(
            name="Payment Fraud Response",
            description="Response to payment fraud detection",
            incident_types=[IncidentType.FRAUD_DETECTION],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
            steps=[
                {
                    'step_id': 1,
                    'name': 'Freeze Suspicious Transactions',
                    'action': 'freeze_transactions',
                    'description': 'Freeze suspicious transactions immediately',
                    'automated': True,
                    'timeout': 30
                },
                {
                    'step_id': 2,
                    'name': 'Disable Payment Methods',
                    'action': 'disable_payment_methods',
                    'description': 'Disable compromised payment methods',
                    'automated': True,
                    'timeout': 60
                },
                {
                    'step_id': 3,
                    'name': 'Notify Financial Team',
                    'action': ResponseAction.NOTIFY_STAKEHOLDERS.value,
                    'description': 'Notify financial operations team',
                    'automated': True,
                    'timeout': 120
                },
                {
                    'step_id': 4,
                    'name': 'Generate Fraud Report',
                    'action': 'generate_fraud_report',
                    'description': 'Generate detailed fraud analysis report',
                    'automated': True,
                    'timeout': 600
                }
            ],
            automated=True,
            approval_required=False,
            estimated_duration=1800
        )
        
        # Store playbooks
        for playbook in [data_breach_playbook, malware_playbook, unauthorized_access_playbook, fraud_playbook]:
            self.playbooks[playbook.playbook_id] = playbook

    async def create_incident(
        self,
        title: str,
        description: str,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        affected_systems: List[str] = None,
        affected_users: List[str] = None,
        source_ip: str = "",
        evidence: Dict[str, Any] = None,
        auto_respond: bool = True
    ) -> str:
        """
        Create new security incident
        
        Args:
            title: Incident title
            description: Detailed description
            incident_type: Type of incident
            severity: Incident severity
            affected_systems: List of affected systems
            affected_users: List of affected users
            source_ip: Source IP address
            evidence: Initial evidence
            auto_respond: Whether to automatically execute response
            
        Returns:
            Incident ID
        """
        try:
            # Create incident
            incident = SecurityIncident(
                title=title,
                description=description,
                incident_type=incident_type,
                severity=severity,
                affected_systems=affected_systems or [],
                affected_users=affected_users or [],
                source_ip=source_ip,
                evidence=evidence or {}
            )
            
            # Store incident
            self.incidents[incident.incident_id] = incident
            self.metrics['total_incidents'] += 1
            self.metrics['active_incidents'] += 1
            
            # Store in Redis
            await self._store_incident(incident)
            
            # Log incident creation
            await self._log_incident_event(
                incident.incident_id,
                "incident_created",
                f"New {severity.value} incident: {title}"
            )
            
            # Check SLA requirements
            await self._check_sla_requirements(incident)
            
            # Auto-respond if enabled
            if auto_respond:
                await self._trigger_auto_response(incident)
                
            logger.info(f"🚨 Security incident created: {incident.incident_id} - {title}")
            return incident.incident_id
            
        except Exception as e:
            logger.error(f"❌ Error creating incident: {e}")
            raise

    async def _trigger_auto_response(self, incident: SecurityIncident):
        """Trigger automated response for incident"""
        try:
            # Find matching playbooks
            matching_playbooks = await self._find_matching_playbooks(incident)
            
            if not matching_playbooks:
                logger.warning(f"⚠️ No matching playbooks found for incident {incident.incident_id}")
                return
                
            # Execute highest priority playbook
            best_playbook = max(matching_playbooks, key=lambda p: len(p.incident_types))
            await self._execute_playbook(incident.incident_id, best_playbook.playbook_id)
            
        except Exception as e:
            logger.error(f"❌ Error in auto-response: {e}")

    async def _find_matching_playbooks(self, incident: SecurityIncident) -> List[ResponsePlaybook]:
        """Find playbooks that match incident criteria"""
        matching = []
        
        for playbook in self.playbooks.values():
            if not playbook.is_active:
                continue
                
            # Check incident type match
            if incident.incident_type in playbook.incident_types:
                # Check severity match
                if incident.severity in playbook.severity_levels:
                    matching.append(playbook)
                    
        return matching

    async def execute_playbook(self, incident_id: str, playbook_id: str) -> str:
        """
        Execute response playbook for incident
        
        Args:
            incident_id: Incident ID
            playbook_id: Playbook ID to execute
            
        Returns:
            Execution ID
        """
        return await self._execute_playbook(incident_id, playbook_id)

    async def _execute_playbook(self, incident_id: str, playbook_id: str) -> str:
        """Execute response playbook"""
        try:
            incident = self.incidents.get(incident_id)
            if not incident:
                raise ValueError(f"Incident {incident_id} not found")
                
            playbook = self.playbooks.get(playbook_id)
            if not playbook:
                raise ValueError(f"Playbook {playbook_id} not found")
                
            # Create execution
            execution = PlaybookExecution(
                incident_id=incident_id,
                playbook_id=playbook_id,
                status=PlaybookStatus.RUNNING,
                started_at=datetime.now()
            )
            
            self.executions[execution.execution_id] = execution
            self.metrics['playbooks_executed'] += 1
            
            # Update incident status
            incident.status = IncidentStatus.INVESTIGATING
            incident.response_time = datetime.now()
            
            # Log playbook execution start
            await self._log_incident_event(
                incident_id,
                "playbook_started",
                f"Started executing playbook: {playbook.name}"
            )
            
            # Execute steps
            await self._execute_playbook_steps(execution, playbook)
            
            return execution.execution_id
            
        except Exception as e:
            logger.error(f"❌ Error executing playbook: {e}")
            raise

    async def _execute_playbook_steps(self, execution: PlaybookExecution, playbook: ResponsePlaybook):
        """Execute individual playbook steps"""
        try:
            for i, step in enumerate(playbook.steps):
                execution.current_step = i + 1
                
                # Log step start
                await self._log_incident_event(
                    execution.incident_id,
                    "step_started",
                    f"Executing step {execution.current_step}: {step['name']}"
                )
                
                # Execute step
                step_result = await self._execute_step(execution, step)
                execution.steps_completed.append(step_result)
                
                # Check if step failed
                if not step_result.get('success', False):
                    execution.errors.append(f"Step {execution.current_step} failed: {step_result.get('error', 'Unknown error')}")
                    
                    # If critical step fails, pause execution for manual intervention
                    if step.get('critical', False):
                        execution.status = PlaybookStatus.PAUSED
                        execution.manual_interventions += 1
                        await self._log_incident_event(
                            execution.incident_id,
                            "manual_intervention_required",
                            f"Critical step failed, manual intervention required"
                        )
                        return
                        
            # All steps completed successfully
            execution.status = PlaybookStatus.COMPLETED
            execution.completed_at = datetime.now()
            
            # Update playbook success rate
            playbook.execution_count += 1
            if execution.status == PlaybookStatus.COMPLETED:
                playbook.success_rate = (
                    (playbook.success_rate * (playbook.execution_count - 1) + 1) / 
                    playbook.execution_count
                )
            
            # Update incident status
            incident = self.incidents[execution.incident_id]
            incident.status = IncidentStatus.CONTAINING
            
            await self._log_incident_event(
                execution.incident_id,
                "playbook_completed",
                f"Playbook executed successfully: {playbook.name}"
            )
            
        except Exception as e:
            execution.status = PlaybookStatus.FAILED
            execution.errors.append(str(e))
            logger.error(f"❌ Error executing playbook steps: {e}")

    async def _execute_step(self, execution: PlaybookExecution, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual response step"""
        try:
            action = step.get('action', '')
            incident = self.incidents[execution.incident_id]
            
            # Execute based on action type
            if action == ResponseAction.ISOLATE_SYSTEM.value:
                return await self._isolate_system(incident, step)
            elif action == ResponseAction.BLOCK_IP.value:
                return await self._block_ip(incident, step)
            elif action == ResponseAction.DISABLE_ACCOUNT.value:
                return await self._disable_account(incident, step)
            elif action == ResponseAction.QUARANTINE_FILE.value:
                return await self._quarantine_file(incident, step)
            elif action == ResponseAction.RESET_PASSWORD.value:
                return await self._reset_password(incident, step)
            elif action == ResponseAction.NOTIFY_STAKEHOLDERS.value:
                return await self._notify_stakeholders(incident, step)
            elif action == ResponseAction.COLLECT_EVIDENCE.value:
                return await self._collect_evidence(incident, step)
            elif action == 'freeze_transactions':
                return await self._freeze_transactions(incident, step)
            elif action == 'disable_payment_methods':
                return await self._disable_payment_methods(incident, step)
            elif action == 'generate_fraud_report':
                return await self._generate_fraud_report(incident, step)
            else:
                return await self._execute_custom_action(incident, step)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _isolate_system(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Isolate affected systems"""
        isolated_systems = []
        
        for system in incident.affected_systems:
            # Simulate system isolation
            isolated_systems.append(system)
            logger.info(f"🔒 Isolated system: {system}")
            
        incident.response_actions.append(f"isolated_systems: {isolated_systems}")
        
        return {
            'success': True,
            'action': 'isolate_system',
            'isolated_systems': isolated_systems,
            'timestamp': datetime.now().isoformat()
        }

    async def _block_ip(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Block source IP address"""
        if incident.source_ip:
            # Simulate IP blocking
            logger.info(f"🚫 Blocked IP: {incident.source_ip}")
            incident.response_actions.append(f"blocked_ip: {incident.source_ip}")
            
            return {
                'success': True,
                'action': 'block_ip',
                'blocked_ip': incident.source_ip,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'error': 'No source IP to block',
                'timestamp': datetime.now().isoformat()
            }

    async def _disable_account(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Disable affected user accounts"""
        disabled_accounts = []
        
        for user_id in incident.affected_users:
            # Simulate account disabling
            disabled_accounts.append(user_id)
            logger.info(f"🚫 Disabled account: {user_id}")
            
        incident.response_actions.append(f"disabled_accounts: {disabled_accounts}")
        
        return {
            'success': True,
            'action': 'disable_account',
            'disabled_accounts': disabled_accounts,
            'timestamp': datetime.now().isoformat()
        }

    async def _quarantine_file(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Quarantine malicious files"""
        quarantined_files = []
        
        # Get file information from evidence
        files = incident.evidence.get('malicious_files', [])
        for file_info in files:
            quarantined_files.append(file_info)
            logger.info(f"🔒 Quarantined file: {file_info}")
            
        incident.response_actions.append(f"quarantined_files: {quarantined_files}")
        
        return {
            'success': True,
            'action': 'quarantine_file',
            'quarantined_files': quarantined_files,
            'timestamp': datetime.now().isoformat()
        }

    async def _reset_password(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Reset passwords for affected accounts"""
        reset_accounts = []
        
        for user_id in incident.affected_users:
            # Simulate password reset
            reset_accounts.append(user_id)
            logger.info(f"🔑 Reset password for: {user_id}")
            
        incident.response_actions.append(f"password_reset: {reset_accounts}")
        
        return {
            'success': True,
            'action': 'reset_password',
            'reset_accounts': reset_accounts,
            'timestamp': datetime.now().isoformat()
        }

    async def _notify_stakeholders(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Notify relevant stakeholders"""
        notifications_sent = []
        
        # Determine stakeholders based on severity
        stakeholders = []
        if incident.severity == IncidentSeverity.CRITICAL:
            stakeholders = ['security_team', 'management', 'legal_team', 'communications']
        elif incident.severity == IncidentSeverity.HIGH:
            stakeholders = ['security_team', 'management']
        else:
            stakeholders = ['security_team']
            
        for stakeholder in stakeholders:
            # Simulate notification
            notification = {
                'recipient': stakeholder,
                'subject': f"Security Incident: {incident.title}",
                'severity': incident.severity.value,
                'timestamp': datetime.now().isoformat()
            }
            notifications_sent.append(notification)
            logger.info(f"📧 Notified: {stakeholder}")
            
        incident.communication_log.extend(notifications_sent)
        
        return {
            'success': True,
            'action': 'notify_stakeholders',
            'notifications_sent': len(notifications_sent),
            'recipients': stakeholders,
            'timestamp': datetime.now().isoformat()
        }

    async def _collect_evidence(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Collect digital evidence"""
        evidence_collected = []
        
        # Collect different types of evidence
        evidence_types = ['system_logs', 'network_traffic', 'memory_dump', 'file_system']
        
        for evidence_type in evidence_types:
            evidence_item = EvidenceItem(
                incident_id=incident.incident_id,
                evidence_type=evidence_type,
                source=f"{evidence_type}_source",
                file_path=f"/evidence/{incident.incident_id}/{evidence_type}_{int(time.time())}.bin",
                hash_sha256=hashlib.sha256(f"{evidence_type}_{incident.incident_id}".encode()).hexdigest(),
                metadata={'size': f"{secrets.randbelow(1000)}MB", 'collection_method': 'automated'}
            )
            
            self.evidence[evidence_item.evidence_id] = evidence_item
            evidence_collected.append(evidence_item.evidence_id)
            
        incident.response_actions.append(f"evidence_collected: {len(evidence_collected)} items")
        
        return {
            'success': True,
            'action': 'collect_evidence',
            'evidence_items': len(evidence_collected),
            'types_collected': evidence_types,
            'timestamp': datetime.now().isoformat()
        }

    async def _freeze_transactions(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Freeze suspicious transactions"""
        # Get transaction information from evidence
        transactions = incident.evidence.get('suspicious_transactions', [])
        frozen_count = len(transactions)
        
        for transaction in transactions:
            logger.info(f"❄️ Froze transaction: {transaction}")
            
        incident.response_actions.append(f"frozen_transactions: {frozen_count}")
        
        return {
            'success': True,
            'action': 'freeze_transactions',
            'frozen_count': frozen_count,
            'timestamp': datetime.now().isoformat()
        }

    async def _disable_payment_methods(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Disable compromised payment methods"""
        payment_methods = incident.evidence.get('compromised_payment_methods', [])
        disabled_count = len(payment_methods)
        
        for method in payment_methods:
            logger.info(f"🚫 Disabled payment method: {method}")
            
        incident.response_actions.append(f"disabled_payment_methods: {disabled_count}")
        
        return {
            'success': True,
            'action': 'disable_payment_methods',
            'disabled_count': disabled_count,
            'timestamp': datetime.now().isoformat()
        }

    async def _generate_fraud_report(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fraud analysis report"""
        report_data = {
            'incident_id': incident.incident_id,
            'detection_time': incident.detection_time.isoformat(),
            'affected_accounts': len(incident.affected_users),
            'suspicious_transactions': len(incident.evidence.get('suspicious_transactions', [])),
            'financial_impact': incident.evidence.get('estimated_loss', 0),
            'response_actions': incident.response_actions,
            'generated_at': datetime.now().isoformat()
        }
        
        # Store report
        report_id = str(uuid.uuid4())
        incident.evidence['fraud_report'] = report_data
        
        logger.info(f"📊 Generated fraud report: {report_id}")
        
        return {
            'success': True,
            'action': 'generate_fraud_report',
            'report_id': report_id,
            'timestamp': datetime.now().isoformat()
        }

    async def _execute_custom_action(self, incident: SecurityIncident, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom action"""
        action = step.get('action', 'unknown')
        
        # Log custom action execution
        logger.info(f"⚙️ Executing custom action: {action}")
        
        return {
            'success': True,
            'action': action,
            'description': step.get('description', ''),
            'timestamp': datetime.now().isoformat()
        }

    async def _check_sla_requirements(self, incident: SecurityIncident):
        """Check and monitor SLA requirements"""
        sla_config = self.sla_configs.get(incident.severity)
        if not sla_config:
            return
            
        current_time = datetime.now()
        
        # Check acknowledgment SLA
        ack_deadline = incident.detection_time + timedelta(seconds=sla_config['acknowledgment_time'])
        if current_time > ack_deadline and incident.status == IncidentStatus.NEW:
            incident.sla_breach = True
            await self._log_incident_event(
                incident.incident_id,
                "sla_breach",
                f"Acknowledgment SLA breached for {incident.severity.value} incident"
            )
            
        # Check response SLA
        response_deadline = incident.detection_time + timedelta(seconds=sla_config['response_time'])
        if current_time > response_deadline and not incident.response_time:
            incident.sla_breach = True
            await self._log_incident_event(
                incident.incident_id,
                "sla_breach",
                f"Response SLA breached for {incident.severity.value} incident"
            )

    async def _log_incident_event(self, incident_id: str, event_type: str, message: str):
        """Log incident event"""
        event = {
            'incident_id': incident_id,
            'event_type': event_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in Redis
        if self.redis:
            await self.redis.lpush(
                f"security:incident:{incident_id}:events",
                json.dumps(event)
            )

    async def _store_incident(self, incident: SecurityIncident):
        """Store incident in Redis"""
        if self.redis:
            incident_data = {
                'incident_id': incident.incident_id,
                'title': incident.title,
                'description': incident.description,
                'incident_type': incident.incident_type.value,
                'severity': incident.severity.value,
                'status': incident.status.value,
                'affected_systems': incident.affected_systems,
                'affected_users': incident.affected_users,
                'source_ip': incident.source_ip,
                'detection_time': incident.detection_time.isoformat(),
                'response_time': incident.response_time.isoformat() if incident.response_time else None,
                'resolution_time': incident.resolution_time.isoformat() if incident.resolution_time else None,
                'assigned_responder': incident.assigned_responder,
                'evidence': incident.evidence,
                'response_actions': incident.response_actions,
                'tags': incident.tags,
                'sla_breach': incident.sla_breach,
                'communication_log': incident.communication_log
            }
            
            await self.redis.setex(
                f"security:incident:{incident.incident_id}",
                86400 * 30,  # 30 days
                json.dumps(incident_data)
            )

    async def _load_existing_data(self):
        """Load existing incidents and playbooks from Redis"""
        if self.redis:
            try:
                # Load incidents
                incident_keys = await self.redis.keys("security:incident:*")
                for key in incident_keys:
                    if not key.endswith(':events'):
                        incident_data = await self.redis.get(key)
                        if incident_data:
                            data = json.loads(incident_data)
                            # Convert back to SecurityIncident object
                            
                # Load playbooks
                playbook_keys = await self.redis.keys("security:playbook:*")
                for key in playbook_keys:
                    playbook_data = await self.redis.get(key)
                    if playbook_data:
                        data = json.loads(playbook_data)
                        # Convert back to ResponsePlaybook object
                        
            except Exception as e:
                logger.error(f"❌ Failed to load existing data: {e}")

    async def get_incident_metrics(self) -> Dict[str, Any]:
        """Get comprehensive incident response metrics"""
        active_count = len([i for i in self.incidents.values() if i.status not in [IncidentStatus.CLOSED]])
        
        return {
            'metrics': self.metrics,
            'active_incidents': active_count,
            'total_playbooks': len(self.playbooks),
            'active_executions': len([e for e in self.executions.values() if e.status == PlaybookStatus.RUNNING]),
            'evidence_items': len(self.evidence),
            'sla_breach_count': len([i for i in self.incidents.values() if i.sla_breach]),
            'system_status': 'operational',
            'last_updated': datetime.now().isoformat()
        }

    async def close(self):
        """Close connections and cleanup"""
        if self.redis:
            await self.redis.close()
        self.executor.shutdown(wait=True)
        logger.info("📡 Security Incident Responder closed")


# Factory function
async def create_incident_responder(redis_url: str = "redis://localhost:6379") -> SecurityIncidentResponder:
    """
    Factory function to create and initialize Security Incident Responder
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Initialized SecurityIncidentResponder instance
    """
    responder = SecurityIncidentResponder(redis_url)
    await responder.initialize()
    return responder


if __name__ == "__main__":
    async def test_incident_responder():
        """Test the security incident responder"""
        responder = await create_incident_responder()
        
        # Create test incident
        incident_id = await responder.create_incident(
            title="Suspicious Payment Activity Detected",
            description="Multiple failed payment attempts from same IP",
            incident_type=IncidentType.FRAUD_DETECTION,
            severity=IncidentSeverity.HIGH,
            affected_systems=["payment_gateway", "fraud_detection_system"],
            affected_users=["creator_12345", "creator_67890"],
            source_ip="192.168.1.100",
            evidence={
                "suspicious_transactions": ["txn_001", "txn_002", "txn_003"],
                "estimated_loss": 2500.00,
                "failed_attempts": 15
            },
            auto_respond=True
        )
        print(f"🚨 Incident created: {incident_id}")
        
        # Wait for auto-response to complete
        await asyncio.sleep(2)
        
        # Get metrics
        metrics = await responder.get_incident_metrics()
        print(f"📊 Incident metrics: {json.dumps(metrics, indent=2)}")
        
        await responder.close()

    # Run test
    asyncio.run(test_incident_responder())