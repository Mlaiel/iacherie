#!/usr/bin/env python3
"""
Security Incident Response - Enterprise Automated Security Response System
Advanced incident detection, classification, and automated response orchestration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import secrets
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Niveaux de sévérité incidents"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IncidentCategory(Enum):
    """Catégories d'incidents sécurité"""
    MALWARE = "malware"
    PHISHING = "phishing"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DDOS = "ddos"
    INSIDER_THREAT = "insider_threat"
    VULNERABILITY = "vulnerability"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_COMPROMISE = "system_compromise"
    CREATOR_ACCOUNT_ABUSE = "creator_account_abuse"

class IncidentStatus(Enum):
    """États d'incidents"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ResponseAction(Enum):
    """Actions de réponse automatisées"""
    ISOLATE_SYSTEM = "isolate_system"
    BLOCK_IP = "block_ip"
    DISABLE_ACCOUNT = "disable_account"
    QUARANTINE_FILE = "quarantine_file"
    RESET_PASSWORD = "reset_password"
    ENABLE_MFA = "enable_mfa"
    NOTIFY_TEAM = "notify_team"
    ESCALATE = "escalate"
    CREATE_TICKET = "create_ticket"
    COLLECT_EVIDENCE = "collect_evidence"

@dataclass
class SecurityIncident:
    """Incident de sécurité"""
    incident_id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    affected_assets: List[str]
    source_ip: Optional[str]
    user_id: Optional[str]
    detection_time: datetime
    evidence: Dict[str, Any]
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    assigned_to: Optional[str] = None
    containment_actions: List[str] = field(default_factory=list)
    resolution_notes: Optional[str] = None
    lessons_learned: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'incident_id': self.incident_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'affected_assets': self.affected_assets,
            'source_ip': self.source_ip,
            'user_id': self.user_id,
            'detection_time': self.detection_time.isoformat(),
            'evidence': self.evidence,
            'timeline': self.timeline,
            'assigned_to': self.assigned_to,
            'containment_actions': self.containment_actions,
            'resolution_notes': self.resolution_notes,
            'lessons_learned': self.lessons_learned
        }

@dataclass
class ResponsePlaybook:
    """Playbook de réponse d'incident"""
    playbook_id: str
    name: str
    description: str
    incident_categories: List[IncidentCategory]
    severity_threshold: IncidentSeverity
    automated_actions: List[ResponseAction]
    manual_steps: List[str]
    escalation_criteria: Dict[str, Any]
    enabled: bool = True
    
    def matches_incident(self, incident: SecurityIncident) -> bool:
        """Vérification correspondance incident"""
        if not self.enabled:
            return False
        
        # Vérification catégorie
        if self.incident_categories and incident.category not in self.incident_categories:
            return False
        
        # Vérification seuil sévérité
        severity_levels = {
            IncidentSeverity.INFO: 1,
            IncidentSeverity.LOW: 2,
            IncidentSeverity.MEDIUM: 3,
            IncidentSeverity.HIGH: 4,
            IncidentSeverity.CRITICAL: 5
        }
        
        if severity_levels.get(incident.severity, 0) < severity_levels.get(self.severity_threshold, 0):
            return False
        
        return True

@dataclass
class ResponseActionResult:
    """Résultat action de réponse"""
    action: ResponseAction
    success: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    evidence_collected: Dict[str, Any] = field(default_factory=dict)

class SecurityIncidentResponseEngine:
    """Moteur principal de réponse aux incidents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialisation moteur réponse incidents"""
        self.config = config or {}
        
        # Base de données incidents
        self.incidents: Dict[str, SecurityIncident] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.response_handlers: Dict[ResponseAction, Callable] = {}
        
        # Configuration
        self.auto_response_enabled = self.config.get('auto_response_enabled', True)
        self.escalation_timeout = self.config.get('escalation_timeout', 3600)  # 1 heure
        self.notification_channels = self.config.get('notification_channels', [])
        
        # Métriques
        self.response_metrics = defaultdict(int)
        
        # Initialisation playbooks par défaut
        self._initialize_default_playbooks()
        self._register_response_handlers()
        
        logger.info("Security Incident Response Engine initialized successfully")
    
    def _initialize_default_playbooks(self):
        """Initialisation playbooks de réponse par défaut"""
        
        # Playbook malware
        self.add_playbook(ResponsePlaybook(
            playbook_id="malware_response",
            name="Malware Incident Response",
            description="Automated response to malware detection",
            incident_categories=[IncidentCategory.MALWARE],
            severity_threshold=IncidentSeverity.MEDIUM,
            automated_actions=[
                ResponseAction.ISOLATE_SYSTEM,
                ResponseAction.QUARANTINE_FILE,
                ResponseAction.COLLECT_EVIDENCE,
                ResponseAction.NOTIFY_TEAM
            ],
            manual_steps=[
                "Perform forensic analysis",
                "Identify malware family",
                "Check for lateral movement",
                "Update antivirus signatures"
            ],
            escalation_criteria={'time_to_containment': 1800}  # 30 minutes
        ))
        
        # Playbook violation accès
        self.add_playbook(ResponsePlaybook(
            playbook_id="unauthorized_access_response",
            name="Unauthorized Access Response",
            description="Response to unauthorized access attempts",
            incident_categories=[IncidentCategory.UNAUTHORIZED_ACCESS],
            severity_threshold=IncidentSeverity.HIGH,
            automated_actions=[
                ResponseAction.DISABLE_ACCOUNT,
                ResponseAction.BLOCK_IP,
                ResponseAction.RESET_PASSWORD,
                ResponseAction.ENABLE_MFA,
                ResponseAction.NOTIFY_TEAM
            ],
            manual_steps=[
                "Review access logs",
                "Verify user identity",
                "Check for compromised credentials",
                "Assess data exposure"
            ],
            escalation_criteria={'failed_containment': True}
        ))
        
        # Playbook fuite données
        self.add_playbook(ResponsePlaybook(
            playbook_id="data_breach_response",
            name="Data Breach Response",
            description="Critical response to data breach incidents",
            incident_categories=[IncidentCategory.DATA_BREACH],
            severity_threshold=IncidentSeverity.CRITICAL,
            automated_actions=[
                ResponseAction.ISOLATE_SYSTEM,
                ResponseAction.COLLECT_EVIDENCE,
                ResponseAction.NOTIFY_TEAM,
                ResponseAction.ESCALATE,
                ResponseAction.CREATE_TICKET
            ],
            manual_steps=[
                "Assess scope of breach",
                "Identify affected data",
                "Notify legal team",
                "Prepare regulatory notifications",
                "Coordinate external communications"
            ],
            escalation_criteria={'immediate': True}
        ))
        
        # Playbook spécifique créateurs Ainflue
        self.add_playbook(ResponsePlaybook(
            playbook_id="creator_account_abuse_response",
            name="Creator Account Abuse Response",
            description="Response to creator account compromise or abuse",
            incident_categories=[IncidentCategory.CREATOR_ACCOUNT_ABUSE],
            severity_threshold=IncidentSeverity.MEDIUM,
            automated_actions=[
                ResponseAction.DISABLE_ACCOUNT,
                ResponseAction.RESET_PASSWORD,
                ResponseAction.ENABLE_MFA,
                ResponseAction.COLLECT_EVIDENCE,
                ResponseAction.NOTIFY_TEAM
            ],
            manual_steps=[
                "Review creator content modifications",
                "Check revenue/payment tampering",
                "Verify creator identity",
                "Assess follower/engagement manipulation",
                "Coordinate with creator support team"
            ],
            escalation_criteria={'revenue_impact': True, 'content_violation': True}
        ))
        
        logger.info(f"Initialized {len(self.playbooks)} default response playbooks")
    
    def _register_response_handlers(self):
        """Enregistrement handlers actions de réponse"""
        self.response_handlers = {
            ResponseAction.ISOLATE_SYSTEM: self._isolate_system,
            ResponseAction.BLOCK_IP: self._block_ip,
            ResponseAction.DISABLE_ACCOUNT: self._disable_account,
            ResponseAction.QUARANTINE_FILE: self._quarantine_file,
            ResponseAction.RESET_PASSWORD: self._reset_password,
            ResponseAction.ENABLE_MFA: self._enable_mfa,
            ResponseAction.NOTIFY_TEAM: self._notify_team,
            ResponseAction.ESCALATE: self._escalate_incident,
            ResponseAction.CREATE_TICKET: self._create_ticket,
            ResponseAction.COLLECT_EVIDENCE: self._collect_evidence
        }
    
    def add_playbook(self, playbook: ResponsePlaybook):
        """Ajout playbook de réponse"""
        self.playbooks[playbook.playbook_id] = playbook
        logger.debug(f"Added response playbook: {playbook.name}")
    
    async def create_incident(
        self,
        title: str,
        description: str,
        category: IncidentCategory,
        severity: IncidentSeverity,
        affected_assets: List[str],
        evidence: Dict[str, Any],
        source_ip: str = None,
        user_id: str = None
    ) -> str:
        """Création nouvel incident de sécurité"""
        try:
            incident_id = str(uuid.uuid4())
            
            incident = SecurityIncident(
                incident_id=incident_id,
                title=title,
                description=description,
                category=category,
                severity=severity,
                status=IncidentStatus.NEW,
                affected_assets=affected_assets,
                source_ip=source_ip,
                user_id=user_id,
                detection_time=datetime.utcnow(),
                evidence=evidence
            )
            
            # Ajout événement timeline
            incident.timeline.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'Incident Created',
                'details': f'Incident {incident_id} created with severity {severity.value}',
                'actor': 'system'
            })
            
            self.incidents[incident_id] = incident
            
            # Déclenchement réponse automatique si activée
            if self.auto_response_enabled:
                await self._trigger_automated_response(incident)
            
            self.response_metrics['incidents_created'] += 1
            
            logger.info(f"Created security incident: {incident_id} - {title}")
            return incident_id
            
        except Exception as e:
            logger.error(f"Error creating incident: {str(e)}")
            raise
    
    async def _trigger_automated_response(self, incident: SecurityIncident):
        """Déclenchement réponse automatisée"""
        try:
            # Recherche playbooks applicables
            applicable_playbooks = [
                playbook for playbook in self.playbooks.values()
                if playbook.matches_incident(incident)
            ]
            
            if not applicable_playbooks:
                logger.info(f"No applicable playbooks found for incident {incident.incident_id}")
                return
            
            # Tri par priorité (plus restrictif = plus prioritaire)
            applicable_playbooks.sort(
                key=lambda p: len(p.incident_categories) + len(p.automated_actions),
                reverse=True
            )
            
            # Exécution du playbook le plus prioritaire
            selected_playbook = applicable_playbooks[0]
            
            logger.info(f"Executing playbook {selected_playbook.name} for incident {incident.incident_id}")
            
            # Mise à jour statut
            await self._update_incident_status(incident.incident_id, IncidentStatus.ACKNOWLEDGED)
            
            # Exécution actions automatisées
            for action in selected_playbook.automated_actions:
                try:
                    result = await self._execute_response_action(incident, action)
                    
                    # Enregistrement action dans timeline
                    incident.timeline.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'event': f'Automated Action: {action.value}',
                        'details': result.message,
                        'success': result.success,
                        'actor': 'automated_response'
                    })
                    
                    if result.success:
                        incident.containment_actions.append(action.value)
                        self.response_metrics[f'action_{action.value}_success'] += 1
                    else:
                        self.response_metrics[f'action_{action.value}_failed'] += 1
                        logger.error(f"Failed to execute action {action.value}: {result.message}")
                    
                except Exception as e:
                    logger.error(f"Error executing action {action.value}: {str(e)}")
                    incident.timeline.append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'event': f'Action Failed: {action.value}',
                        'details': str(e),
                        'success': False,
                        'actor': 'automated_response'
                    })
            
            # Vérification critères escalation
            if self._should_escalate(incident, selected_playbook):
                await self._escalate_incident(incident)
            
            # Transition vers investigation si containment réussi
            if incident.containment_actions:
                await self._update_incident_status(incident.incident_id, IncidentStatus.CONTAINMENT)
            
        except Exception as e:
            logger.error(f"Error in automated response: {str(e)}")
    
    async def _execute_response_action(
        self,
        incident: SecurityIncident,
        action: ResponseAction
    ) -> ResponseActionResult:
        """Exécution action de réponse spécifique"""
        try:
            if action not in self.response_handlers:
                return ResponseActionResult(
                    action=action,
                    success=False,
                    message=f"No handler registered for action: {action.value}"
                )
            
            handler = self.response_handlers[action]
            return await handler(incident)
            
        except Exception as e:
            logger.error(f"Error executing response action {action.value}: {str(e)}")
            return ResponseActionResult(
                action=action,
                success=False,
                message=str(e)
            )
    
    # Handlers spécifiques pour actions de réponse
    
    async def _isolate_system(self, incident: SecurityIncident) -> ResponseActionResult:
        """Isolation système compromis"""
        try:
            # Simulation isolation réseau
            # Dans une implémentation réelle, intégrer avec infrastructure réseau
            
            isolated_systems = []
            for asset in incident.affected_assets:
                if self._is_system_asset(asset):
                    # Simulation commande isolation
                    logger.info(f"Isolating system: {asset}")
                    isolated_systems.append(asset)
            
            return ResponseActionResult(
                action=ResponseAction.ISOLATE_SYSTEM,
                success=True,
                message=f"Successfully isolated {len(isolated_systems)} systems",
                evidence_collected={'isolated_systems': isolated_systems}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.ISOLATE_SYSTEM,
                success=False,
                message=str(e)
            )
    
    async def _block_ip(self, incident: SecurityIncident) -> ResponseActionResult:
        """Blocage adresse IP malveillante"""
        try:
            if not incident.source_ip:
                return ResponseActionResult(
                    action=ResponseAction.BLOCK_IP,
                    success=False,
                    message="No source IP available for blocking"
                )
            
            # Simulation ajout règle firewall
            logger.info(f"Blocking IP: {incident.source_ip}")
            
            return ResponseActionResult(
                action=ResponseAction.BLOCK_IP,
                success=True,
                message=f"Successfully blocked IP: {incident.source_ip}",
                evidence_collected={'blocked_ip': incident.source_ip}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.BLOCK_IP,
                success=False,
                message=str(e)
            )
    
    async def _disable_account(self, incident: SecurityIncident) -> ResponseActionResult:
        """Désactivation compte utilisateur"""
        try:
            if not incident.user_id:
                return ResponseActionResult(
                    action=ResponseAction.DISABLE_ACCOUNT,
                    success=False,
                    message="No user ID available for account disable"
                )
            
            # Simulation désactivation compte
            logger.info(f"Disabling account: {incident.user_id}")
            
            return ResponseActionResult(
                action=ResponseAction.DISABLE_ACCOUNT,
                success=True,
                message=f"Successfully disabled account: {incident.user_id}",
                evidence_collected={'disabled_account': incident.user_id}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.DISABLE_ACCOUNT,
                success=False,
                message=str(e)
            )
    
    async def _quarantine_file(self, incident: SecurityIncident) -> ResponseActionResult:
        """Mise en quarantaine fichier malveillant"""
        try:
            quarantined_files = []
            
            # Recherche fichiers dans evidence
            file_paths = incident.evidence.get('file_paths', [])
            file_hashes = incident.evidence.get('file_hashes', [])
            
            for file_path in file_paths:
                logger.info(f"Quarantining file: {file_path}")
                quarantined_files.append(file_path)
            
            return ResponseActionResult(
                action=ResponseAction.QUARANTINE_FILE,
                success=True,
                message=f"Successfully quarantined {len(quarantined_files)} files",
                evidence_collected={'quarantined_files': quarantined_files}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.QUARANTINE_FILE,
                success=False,
                message=str(e)
            )
    
    async def _reset_password(self, incident: SecurityIncident) -> ResponseActionResult:
        """Réinitialisation mot de passe utilisateur"""
        try:
            if not incident.user_id:
                return ResponseActionResult(
                    action=ResponseAction.RESET_PASSWORD,
                    success=False,
                    message="No user ID available for password reset"
                )
            
            # Simulation réinitialisation mot de passe
            new_password = secrets.token_urlsafe(16)
            logger.info(f"Resetting password for user: {incident.user_id}")
            
            return ResponseActionResult(
                action=ResponseAction.RESET_PASSWORD,
                success=True,
                message=f"Successfully reset password for user: {incident.user_id}",
                evidence_collected={'password_reset_user': incident.user_id}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.RESET_PASSWORD,
                success=False,
                message=str(e)
            )
    
    async def _enable_mfa(self, incident: SecurityIncident) -> ResponseActionResult:
        """Activation authentification multi-facteurs"""
        try:
            if not incident.user_id:
                return ResponseActionResult(
                    action=ResponseAction.ENABLE_MFA,
                    success=False,
                    message="No user ID available for MFA enable"
                )
            
            # Simulation activation MFA
            logger.info(f"Enabling MFA for user: {incident.user_id}")
            
            return ResponseActionResult(
                action=ResponseAction.ENABLE_MFA,
                success=True,
                message=f"Successfully enabled MFA for user: {incident.user_id}",
                evidence_collected={'mfa_enabled_user': incident.user_id}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.ENABLE_MFA,
                success=False,
                message=str(e)
            )
    
    async def _notify_team(self, incident: SecurityIncident) -> ResponseActionResult:
        """Notification équipe sécurité"""
        try:
            # Simulation envoi notifications
            notified_channels = []
            
            for channel in self.notification_channels:
                logger.info(f"Sending notification to {channel} for incident {incident.incident_id}")
                notified_channels.append(channel)
            
            return ResponseActionResult(
                action=ResponseAction.NOTIFY_TEAM,
                success=True,
                message=f"Successfully notified {len(notified_channels)} channels",
                evidence_collected={'notified_channels': notified_channels}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.NOTIFY_TEAM,
                success=False,
                message=str(e)
            )
    
    async def _escalate_incident(self, incident: SecurityIncident) -> ResponseActionResult:
        """Escalation incident"""
        try:
            # Mise à jour statut et assignation
            incident.assigned_to = "security_manager"
            
            logger.info(f"Escalating incident {incident.incident_id} to security manager")
            
            return ResponseActionResult(
                action=ResponseAction.ESCALATE,
                success=True,
                message=f"Successfully escalated incident to security manager",
                evidence_collected={'escalated_to': 'security_manager'}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.ESCALATE,
                success=False,
                message=str(e)
            )
    
    async def _create_ticket(self, incident: SecurityIncident) -> ResponseActionResult:
        """Création ticket support"""
        try:
            ticket_id = f"SEC-{str(uuid.uuid4())[:8].upper()}"
            
            logger.info(f"Creating support ticket {ticket_id} for incident {incident.incident_id}")
            
            return ResponseActionResult(
                action=ResponseAction.CREATE_TICKET,
                success=True,
                message=f"Successfully created ticket: {ticket_id}",
                evidence_collected={'ticket_id': ticket_id}
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.CREATE_TICKET,
                success=False,
                message=str(e)
            )
    
    async def _collect_evidence(self, incident: SecurityIncident) -> ResponseActionResult:
        """Collection evidence supplémentaire"""
        try:
            evidence_collected = {
                'collection_timestamp': datetime.utcnow().isoformat(),
                'incident_id': incident.incident_id,
                'system_logs': f"logs_{incident.incident_id}.zip",
                'network_captures': f"pcap_{incident.incident_id}.pcap",
                'memory_dumps': f"memory_{incident.incident_id}.dmp"
            }
            
            logger.info(f"Collecting evidence for incident {incident.incident_id}")
            
            return ResponseActionResult(
                action=ResponseAction.COLLECT_EVIDENCE,
                success=True,
                message="Successfully collected forensic evidence",
                evidence_collected=evidence_collected
            )
            
        except Exception as e:
            return ResponseActionResult(
                action=ResponseAction.COLLECT_EVIDENCE,
                success=False,
                message=str(e)
            )
    
    # Méthodes utilitaires
    
    def _is_system_asset(self, asset: str) -> bool:
        """Vérification si asset est un système"""
        system_indicators = ['server', 'host', 'vm', 'container', '.local', '.internal']
        return any(indicator in asset.lower() for indicator in system_indicators)
    
    def _should_escalate(self, incident: SecurityIncident, playbook: ResponsePlaybook) -> bool:
        """Vérification critères escalation"""
        criteria = playbook.escalation_criteria
        
        # Escalation immédiate
        if criteria.get('immediate'):
            return True
        
        # Escalation si containment échoué
        if criteria.get('failed_containment') and not incident.containment_actions:
            return True
        
        # Escalation basée temps
        time_threshold = criteria.get('time_to_containment')
        if time_threshold:
            elapsed = (datetime.utcnow() - incident.detection_time).total_seconds()
            if elapsed > time_threshold and not incident.containment_actions:
                return True
        
        # Escalation spécifique créateurs
        if criteria.get('revenue_impact') and incident.category == IncidentCategory.CREATOR_ACCOUNT_ABUSE:
            return True
        
        return False
    
    async def _update_incident_status(self, incident_id: str, new_status: IncidentStatus):
        """Mise à jour statut incident"""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            old_status = incident.status
            incident.status = new_status
            
            # Ajout timeline
            incident.timeline.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'Status Update',
                'details': f'Status changed from {old_status.value} to {new_status.value}',
                'actor': 'system'
            })
            
            logger.info(f"Updated incident {incident_id} status: {old_status.value} -> {new_status.value}")
    
    # API publique
    
    async def get_incident(self, incident_id: str) -> Dict[str, Any]:
        """Récupération incident par ID"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        return self.incidents[incident_id].to_dict()
    
    async def update_incident(
        self,
        incident_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Mise à jour incident"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            
            # Application mises à jour
            for field, value in updates.items():
                if hasattr(incident, field):
                    old_value = getattr(incident, field)
                    setattr(incident, field, value)
                    
                    # Timeline pour changements importants
                    if field in ['status', 'severity', 'assigned_to']:
                        incident.timeline.append({
                            'timestamp': datetime.utcnow().isoformat(),
                            'event': f'Updated {field}',
                            'details': f'{field} changed from {old_value} to {value}',
                            'actor': 'manual'
                        })
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating incident: {str(e)}")
            return False
    
    async def close_incident(
        self,
        incident_id: str,
        resolution_notes: str,
        lessons_learned: str = None
    ) -> bool:
        """Clôture incident"""
        try:
            if incident_id not in self.incidents:
                return False
            
            incident = self.incidents[incident_id]
            incident.status = IncidentStatus.CLOSED
            incident.resolution_notes = resolution_notes
            incident.lessons_learned = lessons_learned
            
            # Timeline clôture
            incident.timeline.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'Incident Closed',
                'details': resolution_notes,
                'actor': 'analyst'
            })
            
            self.response_metrics['incidents_closed'] += 1
            
            logger.info(f"Closed incident {incident_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing incident: {str(e)}")
            return False
    
    async def get_response_metrics(self) -> Dict[str, Any]:
        """Métriques système de réponse"""
        try:
            total_incidents = len(self.incidents)
            
            # Statistiques par statut
            status_counts = defaultdict(int)
            severity_counts = defaultdict(int)
            category_counts = defaultdict(int)
            
            # Temps de réponse moyens
            response_times = []
            resolution_times = []
            
            for incident in self.incidents.values():
                status_counts[incident.status.value] += 1
                severity_counts[incident.severity.value] += 1
                category_counts[incident.category.value] += 1
                
                # Calcul temps de réponse (première action)
                if incident.timeline:
                    first_response = next(
                        (event for event in incident.timeline 
                         if 'Automated Action' in event.get('event', '')), 
                        None
                    )
                    if first_response:
                        response_time = (
                            datetime.fromisoformat(first_response['timestamp']) - 
                            incident.detection_time
                        ).total_seconds()
                        response_times.append(response_time)
                
                # Calcul temps résolution
                if incident.status == IncidentStatus.CLOSED:
                    close_event = next(
                        (event for event in incident.timeline 
                         if event.get('event') == 'Incident Closed'), 
                        None
                    )
                    if close_event:
                        resolution_time = (
                            datetime.fromisoformat(close_event['timestamp']) - 
                            incident.detection_time
                        ).total_seconds()
                        resolution_times.append(resolution_time)
            
            metrics = {
                'total_incidents': total_incidents,
                'incidents_by_status': dict(status_counts),
                'incidents_by_severity': dict(severity_counts),
                'incidents_by_category': dict(category_counts),
                'average_response_time': sum(response_times) / len(response_times) if response_times else 0,
                'average_resolution_time': sum(resolution_times) / len(resolution_times) if resolution_times else 0,
                'automated_actions_executed': sum(
                    count for key, count in self.response_metrics.items() 
                    if 'action_' in key and '_success' in key
                ),
                'playbook_metrics': {
                    'total_playbooks': len(self.playbooks),
                    'enabled_playbooks': len([p for p in self.playbooks.values() if p.enabled])
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting response metrics: {str(e)}")
            raise

# Factory function
def create_security_incident_response_engine(config: Dict[str, Any] = None) -> SecurityIncidentResponseEngine:
    """Factory pour création moteur réponse incidents"""
    return SecurityIncidentResponseEngine(config)

# Export classes principales
__all__ = [
    'SecurityIncidentResponseEngine',
    'SecurityIncident',
    'ResponsePlaybook',
    'ResponseActionResult',
    'IncidentSeverity',
    'IncidentCategory',
    'IncidentStatus',
    'ResponseAction',
    'create_security_incident_response_engine'
]