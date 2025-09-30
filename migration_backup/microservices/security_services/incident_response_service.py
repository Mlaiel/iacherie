#!/usr/bin/env python3
"""
🚨 Incident Response Service - Enterprise Security
Service de réponse aux incidents de sécurité pour microservices Ainflue

© Fahed Mlaiel 2024-2025 - Propriété intellectuelle stricte
Architecture microservices enterprise - Niveau production
🛡️ Security Expert Implementation
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib
import uuid

# Configuration logging enterprise
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Niveaux de sévérité incidents"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IncidentStatus(Enum):
    """Statuts incidents"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentType(Enum):
    """Types incidents"""
    MALWARE = "malware"
    DATA_BREACH = "data_breach"
    DDOS = "ddos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_COMPROMISE = "system_compromise"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"
    RANSOMWARE = "ransomware"
    FRAUD = "fraud"
    OTHER = "other"

class ResponseAction(Enum):
    """Actions de réponse"""
    ISOLATE_SYSTEM = "isolate_system"
    BLOCK_IP = "block_ip"
    DISABLE_ACCOUNT = "disable_account"
    COLLECT_EVIDENCE = "collect_evidence"
    NOTIFY_STAKEHOLDERS = "notify_stakeholders"
    PATCH_VULNERABILITY = "patch_vulnerability"
    RESET_CREDENTIALS = "reset_credentials"
    BACKUP_RESTORE = "backup_restore"

@dataclass
class SecurityIncident:
    """Incident de sécurité"""
    incident_id: str
    title: str
    description: str
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    reporter: str
    assigned_to: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    affected_systems: List[str] = None
    indicators: List[str] = None
    timeline: List[Dict[str, Any]] = None
    evidence: List[Dict[str, Any]] = None
    lessons_learned: str = ""
    
    def __post_init__(self):
        if self.affected_systems is None:
            self.affected_systems = []
        if self.indicators is None:
            self.indicators = []
        if self.timeline is None:
            self.timeline = []
        if self.evidence is None:
            self.evidence = []

@dataclass
class ResponsePlaybook:
    """Playbook de réponse"""
    playbook_id: str
    name: str
    description: str
    incident_types: List[IncidentType]
    severity_levels: List[IncidentSeverity]
    steps: List[Dict[str, Any]]
    automated_actions: List[ResponseAction]
    escalation_rules: Dict[str, Any]
    created_at: datetime
    
    def __post_init__(self):
        if not self.steps:
            self.steps = []
        if not self.automated_actions:
            self.automated_actions = []

@dataclass
class NotificationChannel:
    """Canal de notification"""
    channel_id: str
    name: str
    type: str  # email, slack, sms, webhook
    endpoint: str
    severity_filter: List[IncidentSeverity]
    enabled: bool = True

@dataclass
class EvidenceItem:
    """Élément de preuve"""
    evidence_id: str
    incident_id: str
    type: str  # log, file, screenshot, network_capture
    source: str
    collected_at: datetime
    collector: str
    integrity_hash: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class IncidentResponseService:
    """Service de réponse aux incidents Enterprise"""
    
    def __init__(self):
        self.service_name = "incident-response-service"
        self.version = "1.0.0"
        
        # Incidents actifs
        self.incidents: Dict[str, SecurityIncident] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}
        
        # Evidence et forensics
        self.evidence_store: Dict[str, EvidenceItem] = {}
        
        # Configuration
        self.auto_response_enabled = True
        self.escalation_timeout = 1800  # 30 minutes
        self.evidence_retention_days = 365
        
        # Métriques
        self.metrics = {
            'total_incidents': 0,
            'open_incidents': 0,
            'resolved_incidents': 0,
            'critical_incidents': 0,
            'avg_response_time': 0.0,
            'avg_resolution_time': 0.0,
            'automated_responses': 0,
            'evidence_collected': 0,
            'notifications_sent': 0
        }
        
        # Équipe de réponse
        self.response_team = {
            'incident_commander': 'security-lead@ainflue.com',
            'security_analysts': ['analyst1@ainflue.com', 'analyst2@ainflue.com'],
            'forensics_experts': ['forensics@ainflue.com'],
            'legal_counsel': ['legal@ainflue.com'],
            'communications': ['comms@ainflue.com']
        }
        
        logger.info(f"🚨 {self.service_name} v{self.version} - Initialisation")
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialisation du service"""
        try:
            logger.info("🚀 Initialisation Incident Response Service...")
            
            if config is None:
                config = {}
            
            # Configuration
            self.auto_response_enabled = config.get('auto_response', True)
            self.escalation_timeout = config.get('escalation_timeout', 1800)
            
            # Chargement playbooks par défaut
            await self._load_default_playbooks()
            
            # Configuration notifications
            await self._setup_notification_channels()
            
            # Démarrage monitoring
            asyncio.create_task(self._monitoring_loop())
            
            # Tâches de maintenance
            asyncio.create_task(self._maintenance_loop())
            
            logger.info("✅ Incident Response Service initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            return False
    
    async def _load_default_playbooks(self):
        """Chargement playbooks par défaut"""
        try:
            # Playbook Malware
            malware_playbook = ResponsePlaybook(
                playbook_id="pb-malware-001",
                name="Malware Response",
                description="Response procedures for malware incidents",
                incident_types=[IncidentType.MALWARE],
                severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
                steps=[
                    {
                        'step': 1,
                        'action': 'Isolate affected systems',
                        'description': 'Immediately isolate infected systems from network',
                        'automated': True,
                        'timeout': 300
                    },
                    {
                        'step': 2,
                        'action': 'Collect evidence',
                        'description': 'Preserve memory dumps and disk images',
                        'automated': False,
                        'timeout': 3600
                    },
                    {
                        'step': 3,
                        'action': 'Notify stakeholders',
                        'description': 'Alert security team and management',
                        'automated': True,
                        'timeout': 600
                    }
                ],
                automated_actions=[
                    ResponseAction.ISOLATE_SYSTEM,
                    ResponseAction.COLLECT_EVIDENCE,
                    ResponseAction.NOTIFY_STAKEHOLDERS
                ],
                escalation_rules={
                    'timeout': 1800,
                    'escalate_to': 'incident_commander'
                },
                created_at=datetime.now()
            )
            
            # Playbook Data Breach
            breach_playbook = ResponsePlaybook(
                playbook_id="pb-breach-001",
                name="Data Breach Response",
                description="Response procedures for data breach incidents",
                incident_types=[IncidentType.DATA_BREACH],
                severity_levels=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH],
                steps=[
                    {
                        'step': 1,
                        'action': 'Assess scope',
                        'description': 'Determine what data was accessed/stolen',
                        'automated': False,
                        'timeout': 1800
                    },
                    {
                        'step': 2,
                        'action': 'Contain breach',
                        'description': 'Close attack vector and secure systems',
                        'automated': True,
                        'timeout': 900
                    },
                    {
                        'step': 3,
                        'action': 'Legal notification',
                        'description': 'Notify legal team for compliance requirements',
                        'automated': True,
                        'timeout': 3600
                    }
                ],
                automated_actions=[
                    ResponseAction.BLOCK_IP,
                    ResponseAction.DISABLE_ACCOUNT,
                    ResponseAction.NOTIFY_STAKEHOLDERS
                ],
                escalation_rules={
                    'timeout': 900,
                    'escalate_to': 'incident_commander'
                },
                created_at=datetime.now()
            )
            
            # Playbook DDoS
            ddos_playbook = ResponsePlaybook(
                playbook_id="pb-ddos-001",
                name="DDoS Response",
                description="Response procedures for DDoS attacks",
                incident_types=[IncidentType.DDOS],
                severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.MEDIUM],
                steps=[
                    {
                        'step': 1,
                        'action': 'Enable DDoS protection',
                        'description': 'Activate CDN and DDoS mitigation',
                        'automated': True,
                        'timeout': 300
                    },
                    {
                        'step': 2,
                        'action': 'Block attacking IPs',
                        'description': 'Implement IP blocking rules',
                        'automated': True,
                        'timeout': 600
                    },
                    {
                        'step': 3,
                        'action': 'Monitor impact',
                        'description': 'Assess service availability and performance',
                        'automated': False,
                        'timeout': 1800
                    }
                ],
                automated_actions=[
                    ResponseAction.BLOCK_IP,
                    ResponseAction.NOTIFY_STAKEHOLDERS
                ],
                escalation_rules={
                    'timeout': 1800,
                    'escalate_to': 'incident_commander'
                },
                created_at=datetime.now()
            )
            
            # Enregistrement playbooks
            self.playbooks.update({
                pb.playbook_id: pb for pb in [
                    malware_playbook, breach_playbook, ddos_playbook
                ]
            })
            
            logger.info(f"✅ {len(self.playbooks)} playbooks chargés")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement playbooks: {e}")
            raise
    
    async def _setup_notification_channels(self):
        """Configuration canaux de notification"""
        try:
            # Canal email critique
            email_critical = NotificationChannel(
                channel_id="email-critical",
                name="Critical Email Alerts",
                type="email",
                endpoint="security-alerts@ainflue.com",
                severity_filter=[IncidentSeverity.CRITICAL]
            )
            
            # Canal Slack général
            slack_general = NotificationChannel(
                channel_id="slack-security",
                name="Security Slack Channel",
                type="slack",
                endpoint="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
                severity_filter=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH, IncidentSeverity.MEDIUM]
            )
            
            # Webhook pour SIEM
            siem_webhook = NotificationChannel(
                channel_id="siem-webhook",
                name="SIEM Integration",
                type="webhook",
                endpoint="https://siem.ainflue.com/api/incidents",
                severity_filter=[IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]
            )
            
            self.notification_channels.update({
                ch.channel_id: ch for ch in [
                    email_critical, slack_general, siem_webhook
                ]
            })
            
            logger.info(f"✅ {len(self.notification_channels)} canaux de notification configurés")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration notifications: {e}")
            raise
    
    async def create_incident(self, 
                            title: str,
                            description: str,
                            incident_type: IncidentType,
                            severity: IncidentSeverity,
                            reporter: str,
                            affected_systems: List[str] = None,
                            indicators: List[str] = None) -> str:
        """Création d'un incident"""
        try:
            incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            incident = SecurityIncident(
                incident_id=incident_id,
                title=title,
                description=description,
                incident_type=incident_type,
                severity=severity,
                status=IncidentStatus.OPEN,
                reporter=reporter,
                assigned_to=self._assign_incident(severity),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                affected_systems=affected_systems or [],
                indicators=indicators or []
            )
            
            # Ajout timeline initial
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'incident_created',
                'description': f"Incident créé par {reporter}",
                'user': reporter
            })
            
            self.incidents[incident_id] = incident
            
            # Mise à jour métriques
            self.metrics['total_incidents'] += 1
            self.metrics['open_incidents'] += 1
            if severity == IncidentSeverity.CRITICAL:
                self.metrics['critical_incidents'] += 1
            
            # Notifications immédiates
            await self._send_notifications(incident)
            
            # Démarrage réponse automatique si activée
            if self.auto_response_enabled:
                asyncio.create_task(self._execute_automated_response(incident_id))
            
            logger.info(f"🚨 Incident créé: {incident_id} - {severity.value}")
            return incident_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création incident: {e}")
            raise
    
    def _assign_incident(self, severity: IncidentSeverity) -> str:
        """Attribution automatique incident"""
        if severity == IncidentSeverity.CRITICAL:
            return self.response_team['incident_commander']
        elif severity == IncidentSeverity.HIGH:
            return self.response_team['security_analysts'][0]
        else:
            return self.response_team['security_analysts'][1]
    
    async def _send_notifications(self, incident: SecurityIncident):
        """Envoi notifications"""
        try:
            for channel_id, channel in self.notification_channels.items():
                if not channel.enabled:
                    continue
                
                if incident.severity not in channel.severity_filter:
                    continue
                
                await self._send_notification_to_channel(incident, channel)
                self.metrics['notifications_sent'] += 1
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi notifications: {e}")
    
    async def _send_notification_to_channel(self, incident: SecurityIncident, channel: NotificationChannel):
        """Envoi notification vers un canal"""
        try:
            message = self._format_notification_message(incident, channel.type)
            
            if channel.type == "email":
                await self._send_email_notification(channel.endpoint, message)
            elif channel.type == "slack":
                await self._send_slack_notification(channel.endpoint, message)
            elif channel.type == "webhook":
                await self._send_webhook_notification(channel.endpoint, message)
            
            logger.info(f"📧 Notification envoyée: {channel.name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur notification {channel.name}: {e}")
    
    def _format_notification_message(self, incident: SecurityIncident, channel_type: str) -> Dict[str, Any]:
        """Formatage message notification"""
        base_message = {
            'incident_id': incident.incident_id,
            'title': incident.title,
            'severity': incident.severity.value,
            'type': incident.incident_type.value,
            'status': incident.status.value,
            'created_at': incident.created_at.isoformat(),
            'affected_systems': incident.affected_systems
        }
        
        if channel_type == "slack":
            return {
                'text': f"🚨 Security Incident: {incident.title}",
                'attachments': [{
                    'color': self._get_severity_color(incident.severity),
                    'fields': [
                        {'title': 'Incident ID', 'value': incident.incident_id, 'short': True},
                        {'title': 'Severity', 'value': incident.severity.value.upper(), 'short': True},
                        {'title': 'Type', 'value': incident.incident_type.value, 'short': True},
                        {'title': 'Status', 'value': incident.status.value, 'short': True}
                    ]
                }]
            }
        
        return base_message
    
    def _get_severity_color(self, severity: IncidentSeverity) -> str:
        """Couleur selon sévérité"""
        colors = {
            IncidentSeverity.CRITICAL: "#ff0000",
            IncidentSeverity.HIGH: "#ff8000",
            IncidentSeverity.MEDIUM: "#ffff00",
            IncidentSeverity.LOW: "#00ff00"
        }
        return colors.get(severity, "#808080")
    
    async def _send_email_notification(self, endpoint: str, message: Dict[str, Any]):
        """Envoi notification email"""
        try:
            # En production, utiliser service email (SMTP, SendGrid, etc.)
            logger.info(f"📧 Email envoyé à {endpoint}: {message}")
            
        except Exception as e:
            logger.error(f"❌ Erreur email: {e}")
    
    async def _send_slack_notification(self, webhook_url: str, message: Dict[str, Any]):
        """Envoi notification Slack"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        logger.info("✅ Notification Slack envoyée")
                    else:
                        logger.warning(f"⚠️ Erreur Slack: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Erreur Slack: {e}")
    
    async def _send_webhook_notification(self, endpoint: str, message: Dict[str, Any]):
        """Envoi notification webhook"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=message) as response:
                    if response.status in [200, 201, 202]:
                        logger.info("✅ Webhook envoyé")
                    else:
                        logger.warning(f"⚠️ Erreur webhook: {response.status}")
                        
        except Exception as e:
            logger.error(f"❌ Erreur webhook: {e}")
    
    async def _execute_automated_response(self, incident_id: str):
        """Exécution réponse automatique"""
        try:
            incident = self.incidents[incident_id]
            
            # Recherche playbook approprié
            playbook = self._find_matching_playbook(incident)
            
            if not playbook:
                logger.info(f"📋 Aucun playbook trouvé pour {incident_id}")
                return
            
            logger.info(f"🤖 Exécution réponse automatique: {playbook.name}")
            
            # Exécution actions automatisées
            for action in playbook.automated_actions:
                try:
                    success = await self._execute_response_action(incident, action)
                    
                    # Mise à jour timeline
                    incident.timeline.append({
                        'timestamp': datetime.now().isoformat(),
                        'action': f'automated_{action.value}',
                        'description': f"Action automatique: {action.value}",
                        'success': success,
                        'user': 'system'
                    })
                    
                    if success:
                        self.metrics['automated_responses'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Erreur action {action.value}: {e}")
            
            # Mise à jour statut
            incident.status = IncidentStatus.INVESTIGATING
            incident.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Erreur réponse automatique {incident_id}: {e}")
    
    def _find_matching_playbook(self, incident: SecurityIncident) -> Optional[ResponsePlaybook]:
        """Recherche playbook correspondant"""
        for playbook in self.playbooks.values():
            if (incident.incident_type in playbook.incident_types and
                incident.severity in playbook.severity_levels):
                return playbook
        return None
    
    async def _execute_response_action(self, incident: SecurityIncident, action: ResponseAction) -> bool:
        """Exécution action de réponse"""
        try:
            if action == ResponseAction.ISOLATE_SYSTEM:
                return await self._isolate_systems(incident.affected_systems)
            
            elif action == ResponseAction.BLOCK_IP:
                return await self._block_malicious_ips(incident.indicators)
            
            elif action == ResponseAction.DISABLE_ACCOUNT:
                return await self._disable_compromised_accounts(incident.indicators)
            
            elif action == ResponseAction.COLLECT_EVIDENCE:
                return await self._collect_evidence(incident)
            
            elif action == ResponseAction.NOTIFY_STAKEHOLDERS:
                await self._notify_additional_stakeholders(incident)
                return True
            
            elif action == ResponseAction.RESET_CREDENTIALS:
                return await self._reset_credentials(incident.affected_systems)
            
            else:
                logger.warning(f"⚠️ Action non implémentée: {action.value}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur exécution action {action.value}: {e}")
            return False
    
    async def _isolate_systems(self, systems: List[str]) -> bool:
        """Isolation de systèmes"""
        try:
            for system in systems:
                # En production, intégrer avec orchestrateur réseau
                logger.info(f"🔒 Isolation système: {system}")
                
                # Simulation isolation réseau
                # await network_orchestrator.isolate_system(system)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur isolation: {e}")
            return False
    
    async def _block_malicious_ips(self, indicators: List[str]) -> bool:
        """Blocage IPs malveillantes"""
        try:
            ips_to_block = [
                indicator for indicator in indicators
                if self._is_ip_address(indicator)
            ]
            
            for ip in ips_to_block:
                # En production, intégrer avec firewall
                logger.info(f"🚫 Blocage IP: {ip}")
                
                # Simulation blocage firewall
                # await firewall_service.block_ip(ip)
            
            return len(ips_to_block) > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur blocage IPs: {e}")
            return False
    
    def _is_ip_address(self, indicator: str) -> bool:
        """Vérification si indicateur est une IP"""
        import re
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(ip_pattern, indicator))
    
    async def _disable_compromised_accounts(self, indicators: List[str]) -> bool:
        """Désactivation comptes compromis"""
        try:
            accounts_to_disable = [
                indicator for indicator in indicators
                if '@' in indicator or 'user:' in indicator
            ]
            
            for account in accounts_to_disable:
                # En production, intégrer avec IAM
                logger.info(f"🔐 Désactivation compte: {account}")
                
                # Simulation désactivation compte
                # await iam_service.disable_account(account)
            
            return len(accounts_to_disable) > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur désactivation comptes: {e}")
            return False
    
    async def _collect_evidence(self, incident: SecurityIncident) -> bool:
        """Collecte de preuves"""
        try:
            evidence_items = []
            
            # Collecte logs système
            for system in incident.affected_systems:
                evidence_id = f"LOG-{system}-{int(time.time())}"
                
                evidence = EvidenceItem(
                    evidence_id=evidence_id,
                    incident_id=incident.incident_id,
                    type="log",
                    source=system,
                    collected_at=datetime.now(),
                    collector="automated-collector",
                    integrity_hash=hashlib.sha256(f"{evidence_id}{datetime.now()}".encode()).hexdigest(),
                    metadata={
                        'collection_method': 'automated',
                        'system_type': 'linux',
                        'log_types': ['auth', 'syslog', 'access']
                    }
                )
                
                evidence_items.append(evidence)
                self.evidence_store[evidence_id] = evidence
            
            incident.evidence.extend([{
                'evidence_id': ev.evidence_id,
                'type': ev.type,
                'collected_at': ev.collected_at.isoformat()
            } for ev in evidence_items])
            
            self.metrics['evidence_collected'] += len(evidence_items)
            
            logger.info(f"🕵️ {len(evidence_items)} preuves collectées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte preuves: {e}")
            return False
    
    async def _notify_additional_stakeholders(self, incident: SecurityIncident):
        """Notification stakeholders additionnels"""
        try:
            # Notifications selon type et sévérité
            if incident.incident_type == IncidentType.DATA_BREACH:
                # Notifier équipe légale
                logger.info("⚖️ Notification équipe légale")
                
            if incident.severity == IncidentSeverity.CRITICAL:
                # Notifier direction
                logger.info("👔 Notification direction")
                
            if incident.incident_type in [IncidentType.MALWARE, IncidentType.RANSOMWARE]:
                # Notifier experts forensics
                logger.info("🔬 Notification experts forensics")
                
        except Exception as e:
            logger.error(f"❌ Erreur notification stakeholders: {e}")
    
    async def _reset_credentials(self, systems: List[str]) -> bool:
        """Reset des credentials"""
        try:
            for system in systems:
                # En production, intégrer avec gestionnaire de mots de passe
                logger.info(f"🔑 Reset credentials: {system}")
                
                # Simulation reset
                # await credential_manager.reset_system_credentials(system)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur reset credentials: {e}")
            return False
    
    async def update_incident_status(self, incident_id: str, status: IncidentStatus, notes: str = "", user: str = "system"):
        """Mise à jour statut incident"""
        try:
            if incident_id not in self.incidents:
                raise ValueError(f"Incident {incident_id} non trouvé")
            
            incident = self.incidents[incident_id]
            old_status = incident.status
            
            incident.status = status
            incident.updated_at = datetime.now()
            
            # Ajout timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'status_update',
                'description': f"Statut changé de {old_status.value} à {status.value}",
                'notes': notes,
                'user': user
            })
            
            # Si résolu, marquer temps de résolution
            if status == IncidentStatus.RESOLVED:
                incident.resolved_at = datetime.now()
                
                # Calcul temps de résolution
                resolution_time = (incident.resolved_at - incident.created_at).total_seconds()
                
                # Mise à jour métriques
                self.metrics['resolved_incidents'] += 1
                self.metrics['open_incidents'] -= 1
                
                # Mise à jour temps de résolution moyen
                if self.metrics['resolved_incidents'] > 0:
                    current_avg = self.metrics['avg_resolution_time']
                    new_avg = ((current_avg * (self.metrics['resolved_incidents'] - 1)) + resolution_time) / self.metrics['resolved_incidents']
                    self.metrics['avg_resolution_time'] = new_avg
            
            logger.info(f"📝 Incident {incident_id} statut: {status.value}")
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour statut: {e}")
            raise
    
    async def add_evidence(self, 
                          incident_id: str,
                          evidence_type: str,
                          source: str,
                          collector: str,
                          data: bytes,
                          metadata: Dict[str, Any] = None) -> str:
        """Ajout de preuve"""
        try:
            if incident_id not in self.incidents:
                raise ValueError(f"Incident {incident_id} non trouvé")
            
            evidence_id = f"EVD-{incident_id}-{int(time.time())}"
            
            # Calcul hash intégrité
            integrity_hash = hashlib.sha256(data).hexdigest()
            
            evidence = EvidenceItem(
                evidence_id=evidence_id,
                incident_id=incident_id,
                type=evidence_type,
                source=source,
                collected_at=datetime.now(),
                collector=collector,
                integrity_hash=integrity_hash,
                metadata=metadata or {}
            )
            
            self.evidence_store[evidence_id] = evidence
            
            # Mise à jour incident
            incident = self.incidents[incident_id]
            incident.evidence.append({
                'evidence_id': evidence_id,
                'type': evidence_type,
                'collected_at': evidence.collected_at.isoformat(),
                'collector': collector
            })
            
            # Timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'evidence_added',
                'description': f"Preuve ajoutée: {evidence_type} de {source}",
                'user': collector
            })
            
            self.metrics['evidence_collected'] += 1
            
            logger.info(f"🕵️ Preuve ajoutée: {evidence_id}")
            return evidence_id
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout preuve: {e}")
            raise
    
    async def _monitoring_loop(self):
        """Boucle de monitoring"""
        while True:
            try:
                await asyncio.sleep(60)
                
                # Vérification escalation
                await self._check_escalation_timeouts()
                
                # Mise à jour métriques
                await self._update_metrics()
                
            except Exception as e:
                logger.error(f"❌ Erreur monitoring: {e}")
    
    async def _check_escalation_timeouts(self):
        """Vérification timeouts escalation"""
        try:
            current_time = datetime.now()
            
            for incident in self.incidents.values():
                if incident.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
                    # Vérifier si escalation nécessaire
                    time_since_creation = (current_time - incident.created_at).total_seconds()
                    
                    if (time_since_creation > self.escalation_timeout and
                        incident.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]):
                        
                        await self._escalate_incident(incident)
                        
        except Exception as e:
            logger.error(f"❌ Erreur vérification escalation: {e}")
    
    async def _escalate_incident(self, incident: SecurityIncident):
        """Escalation incident"""
        try:
            # Réassignation à incident commander
            old_assigned = incident.assigned_to
            incident.assigned_to = self.response_team['incident_commander']
            incident.updated_at = datetime.now()
            
            # Timeline
            incident.timeline.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'escalated',
                'description': f"Incident escaladé de {old_assigned} à {incident.assigned_to}",
                'reason': 'timeout',
                'user': 'system'
            })
            
            # Notification urgente
            await self._send_escalation_notification(incident)
            
            logger.warning(f"⚠️ Incident escaladé: {incident.incident_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur escalation: {e}")
    
    async def _send_escalation_notification(self, incident: SecurityIncident):
        """Notification escalation"""
        try:
            # Notification urgente à tous les canaux critiques
            for channel in self.notification_channels.values():
                if IncidentSeverity.CRITICAL in channel.severity_filter:
                    escalation_message = self._format_escalation_message(incident, channel.type)
                    await self._send_notification_to_channel(incident, channel)
                    
        except Exception as e:
            logger.error(f"❌ Erreur notification escalation: {e}")
    
    def _format_escalation_message(self, incident: SecurityIncident, channel_type: str) -> Dict[str, Any]:
        """Formatage message escalation"""
        message = self._format_notification_message(incident, channel_type)
        
        if channel_type == "slack":
            message['text'] = f"🚨 ESCALATION: {incident.title}"
            message['attachments'][0]['color'] = "#ff0000"
            message['attachments'][0]['fields'].append({
                'title': 'Status',
                'value': 'ESCALATED - IMMEDIATE ATTENTION REQUIRED',
                'short': False
            })
        
        return message
    
    async def _update_metrics(self):
        """Mise à jour métriques"""
        try:
            # Comptage incidents ouverts
            open_count = len([
                i for i in self.incidents.values()
                if i.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
            ])
            
            self.metrics['open_incidents'] = open_count
            
            # Calcul temps de réponse moyen
            response_times = []
            for incident in self.incidents.values():
                if len(incident.timeline) > 1:
                    first_response = incident.timeline[1]['timestamp']
                    created = incident.created_at
                    response_time = (datetime.fromisoformat(first_response) - created).total_seconds()
                    response_times.append(response_time)
            
            if response_times:
                self.metrics['avg_response_time'] = sum(response_times) / len(response_times)
                
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métriques: {e}")
    
    async def _maintenance_loop(self):
        """Boucle de maintenance"""
        while True:
            try:
                await asyncio.sleep(3600)  # 1 heure
                
                # Nettoyage anciennes preuves
                await self._cleanup_old_evidence()
                
                # Archivage incidents anciens
                await self._archive_old_incidents()
                
            except Exception as e:
                logger.error(f"❌ Erreur maintenance: {e}")
    
    async def _cleanup_old_evidence(self):
        """Nettoyage anciennes preuves"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.evidence_retention_days)
            
            old_evidence = []
            for evidence_id, evidence in self.evidence_store.items():
                if evidence.collected_at < cutoff_date:
                    old_evidence.append(evidence_id)
            
            for evidence_id in old_evidence:
                del self.evidence_store[evidence_id]
            
            if old_evidence:
                logger.info(f"🧹 {len(old_evidence)} preuves anciennes supprimées")
                
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage preuves: {e}")
    
    async def _archive_old_incidents(self):
        """Archivage anciens incidents"""
        try:
            cutoff_date = datetime.now() - timedelta(days=90)
            
            old_incidents = []
            for incident_id, incident in self.incidents.items():
                if (incident.status == IncidentStatus.CLOSED and
                    incident.resolved_at and
                    incident.resolved_at < cutoff_date):
                    old_incidents.append(incident_id)
            
            # En production, archiver vers base de données
            for incident_id in old_incidents:
                # await archive_service.archive_incident(self.incidents[incident_id])
                del self.incidents[incident_id]
            
            if old_incidents:
                logger.info(f"📦 {len(old_incidents)} incidents archivés")
                
        except Exception as e:
            logger.error(f"❌ Erreur archivage: {e}")
    
    async def get_incident_report(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Rapport détaillé incident"""
        try:
            if incident_id not in self.incidents:
                return None
            
            incident = self.incidents[incident_id]
            
            # Compilation données
            report = {
                'incident_info': asdict(incident),
                'timeline': incident.timeline,
                'evidence_summary': {
                    'total_items': len(incident.evidence),
                    'types': list(set(ev['type'] for ev in incident.evidence)),
                    'collectors': list(set(ev['collector'] for ev in incident.evidence))
                },
                'playbook_executed': None,
                'metrics': {
                    'creation_time': incident.created_at.isoformat(),
                    'resolution_time': incident.resolved_at.isoformat() if incident.resolved_at else None,
                    'duration_hours': (
                        (incident.resolved_at - incident.created_at).total_seconds() / 3600
                        if incident.resolved_at else None
                    )
                }
            }
            
            # Recherche playbook utilisé
            playbook = self._find_matching_playbook(incident)
            if playbook:
                report['playbook_executed'] = {
                    'playbook_id': playbook.playbook_id,
                    'name': playbook.name,
                    'automated_actions': [action.value for action in playbook.automated_actions]
                }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur rapport incident: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check"""
        try:
            return {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': self.metrics,
                'components': {
                    'playbooks_loaded': len(self.playbooks) > 0,
                    'notification_channels': len(self.notification_channels) > 0,
                    'automated_response': self.auto_response_enabled,
                    'evidence_storage': True
                },
                'resource_usage': {
                    'active_incidents': self.metrics['open_incidents'],
                    'total_incidents': len(self.incidents),
                    'evidence_items': len(self.evidence_store),
                    'playbooks': len(self.playbooks)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
            return {
                'service': self.service_name,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Statut détaillé service"""
        try:
            return {
                'service_info': {
                    'name': self.service_name,
                    'version': self.version,
                    'status': 'running'
                },
                'configuration': {
                    'auto_response_enabled': self.auto_response_enabled,
                    'escalation_timeout': self.escalation_timeout,
                    'evidence_retention_days': self.evidence_retention_days
                },
                'performance_metrics': self.metrics,
                'incident_overview': {
                    'total_incidents': len(self.incidents),
                    'open_incidents': self.metrics['open_incidents'],
                    'by_severity': self._get_incidents_by_severity(),
                    'by_type': self._get_incidents_by_type(),
                    'by_status': self._get_incidents_by_status()
                },
                'response_capabilities': {
                    'playbooks_available': len(self.playbooks),
                    'notification_channels': len(self.notification_channels),
                    'automated_actions': len(ResponseAction),
                    'response_team_size': sum(len(v) if isinstance(v, list) else 1 for v in self.response_team.values())
                },
                'health': await self.health_check()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statut service: {e}")
            return {'error': str(e)}
    
    def _get_incidents_by_severity(self) -> Dict[str, int]:
        """Répartition incidents par sévérité"""
        severity_counts = {}
        for incident in self.incidents.values():
            severity = incident.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts
    
    def _get_incidents_by_type(self) -> Dict[str, int]:
        """Répartition incidents par type"""
        type_counts = {}
        for incident in self.incidents.values():
            incident_type = incident.incident_type.value
            type_counts[incident_type] = type_counts.get(incident_type, 0) + 1
        return type_counts
    
    def _get_incidents_by_status(self) -> Dict[str, int]:
        """Répartition incidents par statut"""
        status_counts = {}
        for incident in self.incidents.values():
            status = incident.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

# Instance globale
incident_response_service = IncidentResponseService()

async def main():
    """Test du service"""
    try:
        print("🚨 Test Incident Response Service")
        
        success = await incident_response_service.initialize()
        if not success:
            print("❌ Échec initialisation")
            return
        
        # Test création incident critique
        incident_id = await incident_response_service.create_incident(
            title="Ransomware détecté sur serveur production",
            description="Chiffrement détecté sur srv-prod-01, activité suspecte confirmée",
            incident_type=IncidentType.RANSOMWARE,
            severity=IncidentSeverity.CRITICAL,
            reporter="security-analyst@ainflue.com",
            affected_systems=["srv-prod-01", "db-prod-02"],
            indicators=["192.168.1.100", "malware.exe", "user:admin"]
        )
        
        print(f"🚨 Incident créé: {incident_id}")
        
        # Attendre réponse automatique
        await asyncio.sleep(3)
        
        # Mise à jour statut
        await incident_response_service.update_incident_status(
            incident_id,
            IncidentStatus.CONTAINING,
            "Systèmes isolés, analyse forensique en cours",
            "incident-commander@ainflue.com"
        )
        
        # Ajout preuve
        evidence_id = await incident_response_service.add_evidence(
            incident_id,
            "memory_dump",
            "srv-prod-01",
            "forensics-expert@ainflue.com",
            b"fake_memory_dump_data",
            {"dump_type": "full", "acquisition_tool": "volatility"}
        )
        
        print(f"🕵️ Preuve ajoutée: {evidence_id}")
        
        # Rapport incident
        report = await incident_response_service.get_incident_report(incident_id)
        if report:
            print(f"📊 Rapport incident: {report}")
        
        # Statut service
        status = await incident_response_service.get_service_status()
        print(f"📊 Statut service: {status}")
        
        print("✅ Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())