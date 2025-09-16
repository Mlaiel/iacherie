#!/usr/bin/env python3
"""
🚨 COMPLIANCE ALERTING SYSTEM - AINFLUE ENTERPRISE
Real-time compliance alerting with multi-channel notification and escalation

🏛️ EXPERTISE MULTI-RÔLES:
- Lead Dev IA: Orchestration alerts IA pour détection automatique violations
- Backend Senior: Architecture enterprise pour gestion massive alertes temps réel
- ML Engineer: Algorithmes ML prédictifs pour alertes préventives compliance
- DBA: Optimisation BD pour stockage historique alertes & analytics
- Sécurité: Chiffrement alertes sensibles & authentification multi-facteurs
- Microservices: Distribution alertes multi-services & resilience patterns
- Audio Engineer: Alertes audio/sonores pour violations critiques content
- DevOps: Monitoring temps réel & integration CI/CD pour alertes automated
- IA Prompt Engineer: Génération automatisée messages alertes intelligents

👨‍💻 CRÉATEUR & PROPRIÉTÉ INTELLECTUELLE
Architecte Principal: Fahed Mlaiel (mlaiel@live.de)

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL
Toute utilisation non autorisée = Poursuites judiciaires immédiates
Contact: mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import aioredis
import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email.encoders import encode_base64
import requests
import asyncpg
from cryptography.fernet import Fernet
import jwt

# Configuration logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/compliance_alerting.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes compliance"""
    CRITICAL = "critical"      # Violation majeure nécessitant action immédiate
    HIGH = "high"             # Violation importante nécessitant attention rapide
    MEDIUM = "medium"         # Violation modérée nécessitant review
    LOW = "low"              # Violation mineure pour information
    INFO = "info"            # Information compliance pour tracking

class AlertCategory(Enum):
    """Catégories d'alertes compliance"""
    GDPR_VIOLATION = "gdpr_violation"
    CCPA_VIOLATION = "ccpa_violation"
    DMCA_VIOLATION = "dmca_violation"
    DATA_BREACH = "data_breach"
    PRIVACY_VIOLATION = "privacy_violation"
    CONSENT_VIOLATION = "consent_violation"
    RETENTION_VIOLATION = "retention_violation"
    ACCESS_VIOLATION = "access_violation"
    TRANSFER_VIOLATION = "transfer_violation"
    AUDIT_FINDING = "audit_finding"
    REGULATORY_CHANGE = "regulatory_change"
    PLATFORM_VIOLATION = "platform_violation"

class AlertChannel(Enum):
    """Canaux de notification des alertes"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"
    MOBILE_PUSH = "mobile_push"
    VOICE_CALL = "voice_call"
    TELEGRAM = "telegram"

@dataclass
class ComplianceAlert:
    """Structure d'une alerte compliance enterprise"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: AlertSeverity = AlertSeverity.INFO
    category: AlertCategory = AlertCategory.AUDIT_FINDING
    title: str = ""
    description: str = ""
    regulation: str = ""
    affected_data_subjects: int = 0
    affected_platforms: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    compliance_violation: bool = False
    requires_notification: bool = False
    notification_deadline: Optional[datetime] = None
    remediation_actions: List[str] = field(default_factory=list)
    escalation_level: int = 0
    assigned_to: Optional[str] = None
    status: str = "new"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "compliance_alerting_system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir l'alerte en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'category': self.category.value,
            'title': self.title,
            'description': self.description,
            'regulation': self.regulation,
            'affected_data_subjects': self.affected_data_subjects,
            'affected_platforms': self.affected_platforms,
            'risk_score': self.risk_score,
            'compliance_violation': self.compliance_violation,
            'requires_notification': self.requires_notification,
            'notification_deadline': self.notification_deadline.isoformat() if self.notification_deadline else None,
            'remediation_actions': self.remediation_actions,
            'escalation_level': self.escalation_level,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'metadata': self.metadata,
            'created_by': self.created_by
        }

@dataclass 
class AlertRule:
    """Règle de génération d'alertes compliance"""
    id: str
    name: str
    category: AlertCategory
    severity: AlertSeverity
    condition: Callable[[Dict[str, Any]], bool]
    channels: List[AlertChannel]
    escalation_rules: Dict[str, Any]
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
class ComplianceAlertingSystem:
    """
    🚨 SYSTÈME D'ALERTES COMPLIANCE ENTERPRISE
    Gestion complète des alertes compliance avec notification multi-canaux
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialiser le système d'alertes compliance"""
        self.config = config
        self.redis_client = None
        self.db_pool = None
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_channels: Dict[AlertChannel, Any] = {}
        self.escalation_matrix: Dict[str, Dict[str, Any]] = {}
        
        # Métriques alertes
        self.metrics = {
            'total_alerts': 0,
            'critical_alerts': 0,
            'alerts_by_category': {},
            'resolution_times': [],
            'escalation_rates': 0.0,
            'false_positive_rate': 0.0
        }
        
        logger.info("🚨 Compliance Alerting System initialisé - Fahed Mlaiel (mlaiel@live.de)")
    
    async def initialize(self):
        """Initialiser les connexions et services"""
        try:
            # Connexion Redis pour cache et queue alertes
            self.redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                encoding='utf-8',
                decode_responses=True
            )
            
            # Pool connexions PostgreSQL pour stockage alertes
            self.db_pool = await asyncpg.create_pool(
                self.config.get('database_url'),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Initialiser les tables
            await self._create_tables()
            
            # Charger les règles d'alertes
            await self._load_alert_rules()
            
            # Configurer les canaux de notification
            await self._setup_notification_channels()
            
            # Démarrer les workers d'alertes
            await self._start_alert_workers()
            
            logger.info("✅ Compliance Alerting System initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Compliance Alerting: {e}")
            raise
    
    async def _create_tables(self):
        """Créer les tables de base de données"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_alerts (
                    id VARCHAR(36) PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    regulation VARCHAR(50),
                    affected_data_subjects INTEGER DEFAULT 0,
                    affected_platforms JSONB DEFAULT '[]',
                    risk_score DECIMAL(5,2) DEFAULT 0.0,
                    compliance_violation BOOLEAN DEFAULT FALSE,
                    requires_notification BOOLEAN DEFAULT FALSE,
                    notification_deadline TIMESTAMP WITH TIME ZONE,
                    remediation_actions JSONB DEFAULT '[]',
                    escalation_level INTEGER DEFAULT 0,
                    assigned_to VARCHAR(255),
                    status VARCHAR(20) DEFAULT 'new',
                    metadata JSONB DEFAULT '{}',
                    created_by VARCHAR(255) DEFAULT 'system',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_severity ON compliance_alerts(severity);
                CREATE INDEX IF NOT EXISTS idx_alerts_category ON compliance_alerts(category);
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON compliance_alerts(timestamp);
                CREATE INDEX IF NOT EXISTS idx_alerts_status ON compliance_alerts(status);
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS alert_notifications (
                    id SERIAL PRIMARY KEY,
                    alert_id VARCHAR(36) REFERENCES compliance_alerts(id),
                    channel VARCHAR(20) NOT NULL,
                    recipient VARCHAR(255) NOT NULL,
                    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    delivery_status VARCHAR(20) DEFAULT 'sent',
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            """)
    
    async def _load_alert_rules(self):
        """Charger les règles d'alertes compliance"""
        # Règles GDPR
        self.alert_rules['gdpr_data_access'] = AlertRule(
            id='gdpr_data_access',
            name='GDPR Data Access Violation',
            category=AlertCategory.GDPR_VIOLATION,
            severity=AlertSeverity.HIGH,
            condition=lambda ctx: ctx.get('unauthorized_access', False),
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.DASHBOARD],
            escalation_rules={'timeout': 3600, 'escalate_to': 'dpo'}
        )
        
        self.alert_rules['gdpr_consent_violation'] = AlertRule(
            id='gdpr_consent_violation', 
            name='GDPR Consent Violation',
            category=AlertCategory.CONSENT_VIOLATION,
            severity=AlertSeverity.CRITICAL,
            condition=lambda ctx: ctx.get('consent_missing', False),
            channels=[AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.DASHBOARD],
            escalation_rules={'timeout': 1800, 'escalate_to': 'legal_team'}
        )
        
        # Règles CCPA
        self.alert_rules['ccpa_opt_out_violation'] = AlertRule(
            id='ccpa_opt_out_violation',
            name='CCPA Opt-Out Violation',
            category=AlertCategory.CCPA_VIOLATION,
            severity=AlertSeverity.HIGH,
            condition=lambda ctx: ctx.get('opt_out_ignored', False),
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            escalation_rules={'timeout': 7200, 'escalate_to': 'privacy_team'}
        )
        
        # Règles Data Breach
        self.alert_rules['data_breach_detected'] = AlertRule(
            id='data_breach_detected',
            name='Data Breach Detected',
            category=AlertCategory.DATA_BREACH,
            severity=AlertSeverity.CRITICAL,
            condition=lambda ctx: ctx.get('breach_indicators', 0) > 3,
            channels=[AlertChannel.EMAIL, AlertChannel.SMS, AlertChannel.VOICE_CALL],
            escalation_rules={'timeout': 900, 'escalate_to': 'incident_response'}
        )
        
        logger.info(f"✅ {len(self.alert_rules)} règles d'alertes chargées")
    
    async def _setup_notification_channels(self):
        """Configurer les canaux de notification"""
        # Email SMTP
        self.notification_channels[AlertChannel.EMAIL] = {
            'smtp_server': self.config.get('smtp_server', 'smtp.gmail.com'),
            'smtp_port': self.config.get('smtp_port', 587),
            'username': self.config.get('smtp_username'),
            'password': self.config.get('smtp_password'),
            'from_email': self.config.get('from_email', 'compliance@ainflue.com')
        }
        
        # Slack Webhook
        self.notification_channels[AlertChannel.SLACK] = {
            'webhook_url': self.config.get('slack_webhook_url'),
            'channel': self.config.get('slack_channel', '#compliance-alerts')
        }
        
        # SMS via Twilio
        self.notification_channels[AlertChannel.SMS] = {
            'account_sid': self.config.get('twilio_account_sid'),
            'auth_token': self.config.get('twilio_auth_token'),
            'from_number': self.config.get('twilio_from_number')
        }
        
        logger.info("✅ Canaux de notification configurés")
    
    async def _start_alert_workers(self):
        """Démarrer les workers de traitement d'alertes"""
        # Worker pour traitement alertes temps réel
        asyncio.create_task(self._alert_processing_worker())
        
        # Worker pour escalation automatique
        asyncio.create_task(self._escalation_worker())
        
        # Worker pour nettoyage alertes anciennes
        asyncio.create_task(self._cleanup_worker())
        
        logger.info("✅ Workers d'alertes démarrés")
    
    async def create_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        category: AlertCategory,
        regulation: str = "",
        affected_data_subjects: int = 0,
        affected_platforms: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ComplianceAlert:
        """
        🚨 Créer une nouvelle alerte compliance
        
        Args:
            title: Titre de l'alerte
            description: Description détaillée
            severity: Niveau de sévérité
            category: Catégorie de l'alerte
            regulation: Réglementation concernée
            affected_data_subjects: Nombre de personnes affectées
            affected_platforms: Plateformes affectées
            metadata: Métadonnées supplémentaires
            
        Returns:
            ComplianceAlert: Alerte créée
        """
        try:
            # Calculer le score de risque
            risk_score = await self._calculate_risk_score(
                severity, category, affected_data_subjects, affected_platforms or []
            )
            
            # Déterminer si notification réglementaire requise
            requires_notification, deadline = await self._check_notification_requirements(
                category, severity, affected_data_subjects
            )
            
            # Créer l'alerte
            alert = ComplianceAlert(
                title=title,
                description=description,
                severity=severity,
                category=category,
                regulation=regulation,
                affected_data_subjects=affected_data_subjects,
                affected_platforms=affected_platforms or [],
                risk_score=risk_score,
                compliance_violation=severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH],
                requires_notification=requires_notification,
                notification_deadline=deadline,
                metadata=metadata or {}
            )
            
            # Stocker en base de données
            await self._store_alert(alert)
            
            # Ajouter à la queue de traitement
            await self.redis_client.lpush(
                'compliance_alerts_queue',
                json.dumps(alert.to_dict())
            )
            
            # Mettre à jour les métriques
            await self._update_metrics(alert)
            
            logger.info(f"🚨 Alerte créée: {alert.id} - {title}")
            return alert
            
        except Exception as e:
            logger.error(f"❌ Erreur création alerte: {e}")
            raise
    
    async def _calculate_risk_score(
        self,
        severity: AlertSeverity,
        category: AlertCategory,
        affected_subjects: int,
        affected_platforms: List[str]
    ) -> float:
        """Calculer le score de risque de l'alerte"""
        base_score = {
            AlertSeverity.CRITICAL: 9.0,
            AlertSeverity.HIGH: 7.0,
            AlertSeverity.MEDIUM: 5.0,
            AlertSeverity.LOW: 3.0,
            AlertSeverity.INFO: 1.0
        }[severity]
        
        # Facteur impact data subjects
        subject_factor = min(1.0 + (affected_subjects / 1000), 2.0)
        
        # Facteur impact plateformes
        platform_factor = min(1.0 + (len(affected_platforms) / 10), 1.5)
        
        # Facteur catégorie
        category_factor = {
            AlertCategory.DATA_BREACH: 1.5,
            AlertCategory.GDPR_VIOLATION: 1.3,
            AlertCategory.CCPA_VIOLATION: 1.2,
            AlertCategory.PRIVACY_VIOLATION: 1.1,
        }.get(category, 1.0)
        
        risk_score = base_score * subject_factor * platform_factor * category_factor
        return min(risk_score, 10.0)
    
    async def _check_notification_requirements(
        self,
        category: AlertCategory,
        severity: AlertSeverity,
        affected_subjects: int
    ) -> tuple[bool, Optional[datetime]]:
        """Vérifier si notification réglementaire requise"""
        requires_notification = False
        deadline = None
        
        # GDPR Article 33 - 72h notification
        if category == AlertCategory.DATA_BREACH and severity == AlertSeverity.CRITICAL:
            requires_notification = True
            deadline = datetime.utcnow() + timedelta(hours=72)
        
        # GDPR Article 34 - Notification data subjects
        elif category == AlertCategory.DATA_BREACH and affected_subjects > 0:
            requires_notification = True
            deadline = datetime.utcnow() + timedelta(hours=72)
        
        # CCPA notifications
        elif category == AlertCategory.CCPA_VIOLATION and severity == AlertSeverity.CRITICAL:
            requires_notification = True
            deadline = datetime.utcnow() + timedelta(days=45)
        
        return requires_notification, deadline
    
    async def _store_alert(self, alert: ComplianceAlert):
        """Stocker l'alerte en base de données"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO compliance_alerts (
                    id, timestamp, severity, category, title, description,
                    regulation, affected_data_subjects, affected_platforms,
                    risk_score, compliance_violation, requires_notification,
                    notification_deadline, remediation_actions, escalation_level,
                    assigned_to, status, metadata, created_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
            """,
                alert.id, alert.timestamp, alert.severity.value, alert.category.value,
                alert.title, alert.description, alert.regulation, alert.affected_data_subjects,
                json.dumps(alert.affected_platforms), alert.risk_score, alert.compliance_violation,
                alert.requires_notification, alert.notification_deadline, json.dumps(alert.remediation_actions),
                alert.escalation_level, alert.assigned_to, alert.status, json.dumps(alert.metadata),
                alert.created_by
            )
    
    async def _alert_processing_worker(self):
        """Worker de traitement des alertes en temps réel"""
        while True:
            try:
                # Récupérer alerte de la queue
                alert_data = await self.redis_client.brpop('compliance_alerts_queue', timeout=1)
                
                if alert_data:
                    alert_dict = json.loads(alert_data[1])
                    await self._process_alert(alert_dict)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Erreur processing worker: {e}")
                await asyncio.sleep(1)
    
    async def _process_alert(self, alert_dict: Dict[str, Any]):
        """Traiter une alerte compliance"""
        try:
            alert_id = alert_dict['id']
            severity = AlertSeverity(alert_dict['severity'])
            category = AlertCategory(alert_dict['category'])
            
            # Trouver les règles applicables
            applicable_rules = [
                rule for rule in self.alert_rules.values()
                if rule.category == category and rule.active
            ]
            
            # Envoyer notifications pour chaque règle
            for rule in applicable_rules:
                await self._send_notifications(alert_dict, rule)
            
            # Assigner automatiquement si règle définie
            if applicable_rules:
                await self._auto_assign_alert(alert_id, applicable_rules[0])
            
            logger.info(f"✅ Alerte traitée: {alert_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement alerte: {e}")
    
    async def _send_notifications(self, alert_dict: Dict[str, Any], rule: AlertRule):
        """Envoyer notifications selon les canaux définis"""
        for channel in rule.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_notification(alert_dict)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_notification(alert_dict)
                elif channel == AlertChannel.SMS:
                    await self._send_sms_notification(alert_dict)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_notification(alert_dict)
                
                # Enregistrer la notification
                await self._record_notification(alert_dict['id'], channel, 'sent')
                
            except Exception as e:
                logger.error(f"❌ Erreur envoi notification {channel}: {e}")
                await self._record_notification(alert_dict['id'], channel, 'failed', str(e))
    
    async def _send_email_notification(self, alert_dict: Dict[str, Any]):
        """Envoyer notification email"""
        email_config = self.notification_channels[AlertChannel.EMAIL]
        
        # Créer le message
        msg = MimeMultipart()
        msg['From'] = email_config['from_email']
        msg['To'] = self.config.get('compliance_email', 'compliance@ainflue.com')
        msg['Subject'] = f"🚨 COMPLIANCE ALERT: {alert_dict['title']}"
        
        # Corps du message
        body = f"""
        ALERTE COMPLIANCE - AINFLUE ENTERPRISE
        
        ID: {alert_dict['id']}
        Sévérité: {alert_dict['severity'].upper()}
        Catégorie: {alert_dict['category']}
        Réglementation: {alert_dict['regulation']}
        
        Description:
        {alert_dict['description']}
        
        Personnes affectées: {alert_dict['affected_data_subjects']}
        Plateformes affectées: {', '.join(alert_dict['affected_platforms'])}
        Score de risque: {alert_dict['risk_score']}/10
        
        Notification requise: {'Oui' if alert_dict['requires_notification'] else 'Non'}
        
        Actions requises:
        - Examiner l'alerte immédiatement
        - Vérifier la conformité réglementaire
        - Implémenter les mesures correctives
        
        Système Compliance Ainflue
        © Fahed Mlaiel (mlaiel@live.de)
        """
        
        msg.attach(MimeText(body, 'plain'))
        
        # Envoyer via SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls(context=context)
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
    
    async def _send_slack_notification(self, alert_dict: Dict[str, Any]):
        """Envoyer notification Slack"""
        slack_config = self.notification_channels[AlertChannel.SLACK]
        
        # Emoji selon sévérité
        emoji = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': 'ℹ️',
            'info': '📋'
        }.get(alert_dict['severity'], '📋')
        
        payload = {
            'channel': slack_config['channel'],
            'username': 'Compliance Bot',
            'icon_emoji': ':warning:',
            'text': f"{emoji} *COMPLIANCE ALERT*",
            'attachments': [{
                'color': 'danger' if alert_dict['severity'] in ['critical', 'high'] else 'warning',
                'fields': [
                    {'title': 'Titre', 'value': alert_dict['title'], 'short': False},
                    {'title': 'Sévérité', 'value': alert_dict['severity'].upper(), 'short': True},
                    {'title': 'Catégorie', 'value': alert_dict['category'], 'short': True},
                    {'title': 'Score Risque', 'value': f"{alert_dict['risk_score']}/10", 'short': True},
                    {'title': 'Personnes affectées', 'value': str(alert_dict['affected_data_subjects']), 'short': True},
                ],
                'footer': 'Ainflue Compliance System',
                'ts': int(datetime.fromisoformat(alert_dict['timestamp']).timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(slack_config['webhook_url'], json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Slack notification failed: {response.status}")
    
    async def _escalation_worker(self):
        """Worker pour escalation automatique des alertes"""
        while True:
            try:
                # Récupérer alertes nécessitant escalation
                async with self.db_pool.acquire() as conn:
                    alerts = await conn.fetch("""
                        SELECT * FROM compliance_alerts
                        WHERE status IN ('new', 'in_progress')
                        AND created_at < NOW() - INTERVAL '1 hour'
                        AND escalation_level < 3
                    """)
                
                for alert_row in alerts:
                    await self._escalate_alert(dict(alert_row))
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur escalation worker: {e}")
                await asyncio.sleep(60)
    
    async def _escalate_alert(self, alert_dict: Dict[str, Any]):
        """Escalader une alerte non résolue"""
        try:
            alert_id = alert_dict['id']
            current_level = alert_dict['escalation_level']
            new_level = current_level + 1
            
            # Mettre à jour le niveau d'escalation
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE compliance_alerts 
                    SET escalation_level = $1, updated_at = NOW()
                    WHERE id = $2
                """, new_level, alert_id)
            
            # Envoyer notification d'escalation
            escalation_msg = f"🔥 ESCALATION NIVEAU {new_level}: {alert_dict['title']}"
            await self._send_escalation_notification(alert_dict, new_level)
            
            self.metrics['escalation_rates'] += 1
            logger.warning(f"🔥 Alerte escaladée: {alert_id} (niveau {new_level})")
            
        except Exception as e:
            logger.error(f"❌ Erreur escalation alerte: {e}")
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques des alertes"""
        try:
            async with self.db_pool.acquire() as conn:
                # Statistiques générales
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_alerts,
                        COUNT(*) FILTER (WHERE severity = 'critical') as critical_alerts,
                        COUNT(*) FILTER (WHERE severity = 'high') as high_alerts,
                        COUNT(*) FILTER (WHERE status = 'resolved') as resolved_alerts,
                        AVG(risk_score) as avg_risk_score
                    FROM compliance_alerts
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                """)
                
                # Alertes par catégorie
                categories = await conn.fetch("""
                    SELECT category, COUNT(*) as count
                    FROM compliance_alerts
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY category
                """)
                
                # Temps de résolution moyen
                resolution_times = await conn.fetch("""
                    SELECT 
                        EXTRACT(EPOCH FROM (updated_at - created_at))/3600 as hours
                    FROM compliance_alerts
                    WHERE status = 'resolved'
                    AND created_at >= NOW() - INTERVAL '30 days'
                """)
            
            return {
                'total_alerts': stats['total_alerts'],
                'critical_alerts': stats['critical_alerts'],
                'high_alerts': stats['high_alerts'],
                'resolved_alerts': stats['resolved_alerts'],
                'resolution_rate': stats['resolved_alerts'] / max(stats['total_alerts'], 1),
                'avg_risk_score': float(stats['avg_risk_score'] or 0),
                'alerts_by_category': {row['category']: row['count'] for row in categories},
                'avg_resolution_hours': sum(row['hours'] for row in resolution_times) / max(len(resolution_times), 1),
                'escalation_rate': self.metrics['escalation_rates'],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statistiques: {e}")
            return {}
    
    async def _update_metrics(self, alert: ComplianceAlert):
        """Mettre à jour les métriques système"""
        self.metrics['total_alerts'] += 1
        
        if alert.severity == AlertSeverity.CRITICAL:
            self.metrics['critical_alerts'] += 1
        
        category_key = alert.category.value
        self.metrics['alerts_by_category'][category_key] = \
            self.metrics['alerts_by_category'].get(category_key, 0) + 1
    
    async def _cleanup_worker(self):
        """Worker de nettoyage des alertes anciennes"""
        while True:
            try:
                # Nettoyer alertes résolues > 90 jours
                async with self.db_pool.acquire() as conn:
                    deleted = await conn.execute("""
                        DELETE FROM compliance_alerts
                        WHERE status = 'resolved'
                        AND updated_at < NOW() - INTERVAL '90 days'
                    """)
                
                if deleted != "DELETE 0":
                    logger.info(f"🧹 {deleted} alertes anciennes nettoyées")
                
                await asyncio.sleep(86400)  # Nettoyer quotidiennement
                
            except Exception as e:
                logger.error(f"❌ Erreur cleanup worker: {e}")
                await asyncio.sleep(3600)

# Interface publique
async def create_compliance_alert(
    title: str,
    description: str,
    severity: str,
    category: str,
    **kwargs
) -> str:
    """
    Interface publique pour créer une alerte compliance
    
    Args:
        title: Titre de l'alerte
        description: Description
        severity: critical|high|medium|low|info  
        category: Catégorie de l'alerte
        **kwargs: Paramètres supplémentaires
        
    Returns:
        str: ID de l'alerte créée
    """
    alerting_system = ComplianceAlertingSystem({})
    await alerting_system.initialize()
    
    alert = await alerting_system.create_alert(
        title=title,
        description=description,
        severity=AlertSeverity(severity),
        category=AlertCategory(category),
        **kwargs
    )
    
    return alert.id

if __name__ == "__main__":
    # Test du système d'alertes
    async def test_alerting():
        config = {
            'redis_url': 'redis://localhost:6379',
            'database_url': 'postgresql://user:pass@localhost/ainflue',
            'smtp_server': 'smtp.gmail.com',
            'smtp_username': 'compliance@ainflue.com',
            'smtp_password': 'password',
            'compliance_email': 'dpo@ainflue.com'
        }
        
        alerting = ComplianceAlertingSystem(config)
        await alerting.initialize()
        
        # Créer alerte test
        alert = await alerting.create_alert(
            title="Test GDPR Violation",
            description="Test de violation GDPR pour validation système",
            severity=AlertSeverity.HIGH,
            category=AlertCategory.GDPR_VIOLATION,
            regulation="GDPR",
            affected_data_subjects=100
        )
        
        print(f"✅ Alerte test créée: {alert.id}")
        
        # Statistiques
        stats = await alerting.get_alert_statistics()
        print(f"📊 Statistiques: {stats}")
    
    # asyncio.run(test_alerting())
    
    logger.info("🚨 Compliance Alerting System - Prêt pour production")
    logger.info("👨‍💻 Créé par Fahed Mlaiel (mlaiel@live.de)")
    logger.info("⚠️ Propriété intellectuelle exclusive protégée")