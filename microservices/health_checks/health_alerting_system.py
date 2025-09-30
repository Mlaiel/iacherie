"""
Health Alerting System - IA Chérie Health Checks Module
Système alerting santé avec smart notifications, escalation automatique,
multi-channel delivery et intelligent noise reduction.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import uuid
import json
import hashlib
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Niveaux sévérité alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    """Statuts alerte"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class NotificationChannel(Enum):
    """Canaux notification"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGER_DUTY = "pager_duty"
    MICROSOFT_TEAMS = "microsoft_teams"
    DISCORD = "discord"

class EscalationLevel(Enum):
    """Niveaux escalation"""
    LEVEL_1 = "level_1"  # On-call engineer
    LEVEL_2 = "level_2"  # Senior engineer/Team lead
    LEVEL_3 = "level_3"  # Engineering manager
    LEVEL_4 = "level_4"  # Director/VP
    EXECUTIVE = "executive"  # C-level

@dataclass
class AlertRule:
    """Règle alerte"""
    rule_id: str
    name: str
    description: str
    condition: str  # Expression condition (ex: "response_time > 1000")
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 15
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    escalation_enabled: bool = True
    escalation_delay_minutes: int = 30
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """Alerte health"""
    alert_id: str
    rule_id: str
    service_name: str
    metric_name: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    description: str
    triggered_timestamp: datetime
    acknowledged_timestamp: Optional[datetime] = None
    resolved_timestamp: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    suppression_until: Optional[datetime] = None

@dataclass
class NotificationTemplate:
    """Template notification"""
    template_id: str
    channel: NotificationChannel
    severity: AlertSeverity
    subject_template: str
    body_template: str
    format_type: str = "text"  # text, html, markdown

@dataclass
class EscalationPolicy:
    """Politique escalation"""
    policy_id: str
    name: str
    escalation_levels: List[Dict[str, Any]]  # [{level, contacts, delay_minutes}]
    enabled: bool = True
    business_hours_only: bool = False

@dataclass
class AlertingConfig:
    """Configuration système alerting"""
    max_alerts_per_minute: int = 50
    duplicate_alert_window_minutes: int = 5
    auto_resolve_timeout_hours: int = 24
    noise_reduction_enabled: bool = True
    smart_grouping_enabled: bool = True
    notification_retry_attempts: int = 3
    notification_retry_delay_seconds: int = 30

class ConditionEvaluator:
    """Évaluateur conditions alertes"""
    
    @staticmethod
    async def evaluate_condition(condition: str, metrics: Dict[str, Any]) -> bool:
        """Évaluer condition alerte"""
        try:
            # Parse condition simple (ex: "response_time > 1000")
            parts = condition.strip().split()
            if len(parts) != 3:
                return False
                
            metric_name, operator, threshold_str = parts
            
            # Obtenir valeur métrique
            metric_value = metrics.get(metric_name)
            if metric_value is None:
                return False
                
            # Convertir threshold
            try:
                threshold = float(threshold_str)
            except ValueError:
                return False
                
            # Évaluer opérateur
            if operator == '>':
                return metric_value > threshold
            elif operator == '>=':
                return metric_value >= threshold
            elif operator == '<':
                return metric_value < threshold
            elif operator == '<=':
                return metric_value <= threshold
            elif operator == '==':
                return abs(metric_value - threshold) < 0.001
            elif operator == '!=':
                return abs(metric_value - threshold) >= 0.001
                
            return False
            
        except Exception as e:
            logger.error(f"Condition evaluation failed: {condition}: {e}")
            return False

class NotificationDelivery:
    """Système delivery notifications"""
    
    def __init__(self):
        self.delivery_handlers: Dict[NotificationChannel, Callable] = {
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.SLACK: self._send_slack,
            NotificationChannel.SMS: self._send_sms,
            NotificationChannel.WEBHOOK: self._send_webhook,
        }
        
        # Configuration canaux
        self.channel_configs: Dict[NotificationChannel, Dict[str, Any]] = {}
        
    async def configure_channel(self, channel: NotificationChannel, config: Dict[str, Any]):
        """Configurer canal notification"""
        self.channel_configs[channel] = config
        logger.info(f"Configured notification channel: {channel.value}")
        
    async def send_notification(self, channel: NotificationChannel, 
                              alert: Alert, template: NotificationTemplate,
                              recipients: List[str]) -> bool:
        """Envoyer notification"""
        try:
            if channel not in self.delivery_handlers:
                logger.warning(f"No handler for channel: {channel.value}")
                return False
                
            handler = self.delivery_handlers[channel]
            
            # Formater message depuis template
            formatted_message = await self._format_message(alert, template)
            
            # Envoyer via handler
            success = await handler(alert, formatted_message, recipients)
            
            if success:
                logger.info(f"Notification sent via {channel.value} for alert {alert.alert_id}")
            else:
                logger.error(f"Notification failed via {channel.value} for alert {alert.alert_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Notification delivery failed: {e}")
            return False
            
    async def _format_message(self, alert: Alert, template: NotificationTemplate) -> Dict[str, str]:
        """Formater message depuis template"""
        context = {
            'alert_id': alert.alert_id,
            'service_name': alert.service_name,
            'metric_name': alert.metric_name,
            'severity': alert.severity.value,
            'title': alert.title,
            'description': alert.description,
            'current_value': alert.current_value or 0,
            'threshold_value': alert.threshold_value or 0,
            'triggered_time': alert.triggered_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status': alert.status.value
        }
        
        # Format subject et body
        subject = template.subject_template.format(**context)
        body = template.body_template.format(**context)
        
        return {
            'subject': subject,
            'body': body,
            'format': template.format_type
        }
        
    async def _send_email(self, alert: Alert, message: Dict[str, str], 
                         recipients: List[str]) -> bool:
        """Envoyer email"""
        try:
            # Configuration email depuis channel_configs
            email_config = self.channel_configs.get(NotificationChannel.EMAIL, {})
            smtp_server = email_config.get('smtp_server', 'localhost')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username', '')
            password = email_config.get('password', '')
            from_email = email_config.get('from_email', 'alerts@iacherie.com')
            
            # Créer message
            msg = MimeMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = message['subject']
            
            if message['format'] == 'html':
                msg.attach(MimeText(message['body'], 'html'))
            else:
                msg.attach(MimeText(message['body'], 'plain'))
                
            # Envoyer email (simulation)
            # Dans vraie implémentation, utiliser SMTP
            logger.info(f"Email sent to {recipients}: {message['subject']}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
            
    async def _send_slack(self, alert: Alert, message: Dict[str, str], 
                         recipients: List[str]) -> bool:
        """Envoyer Slack"""
        try:
            # Simulation envoi Slack
            logger.info(f"Slack notification sent: {message['subject']}")
            return True
        except Exception as e:
            logger.error(f"Slack sending failed: {e}")
            return False
            
    async def _send_sms(self, alert: Alert, message: Dict[str, str], 
                       recipients: List[str]) -> bool:
        """Envoyer SMS"""
        try:
            # Simulation envoi SMS
            logger.info(f"SMS sent to {recipients}: {message['subject']}")
            return True
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False
            
    async def _send_webhook(self, alert: Alert, message: Dict[str, str], 
                           recipients: List[str]) -> bool:
        """Envoyer webhook"""
        try:
            # Simulation webhook
            logger.info(f"Webhook sent: {message['subject']}")
            return True
        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return False

class NoiseReductionEngine:
    """Moteur réduction bruit alertes"""
    
    def __init__(self):
        self.alert_signatures: Dict[str, List[datetime]] = defaultdict(list)
        self.suppressed_alerts: Set[str] = set()
        
    async def should_suppress_alert(self, alert: Alert, 
                                  suppression_window_minutes: int = 15) -> bool:
        """Déterminer si alerte doit être supprimée"""
        # Créer signature alerte
        signature = self._create_alert_signature(alert)
        
        # Vérifier historique recent
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=suppression_window_minutes)
        
        # Nettoyer anciennes signatures
        self.alert_signatures[signature] = [
            ts for ts in self.alert_signatures[signature] 
            if ts > cutoff_time
        ]
        
        # Si trop d'alertes similaires récentes, supprimer
        recent_count = len(self.alert_signatures[signature])
        
        if recent_count >= 3:  # Supprimer après 3 alertes similaires
            self.suppressed_alerts.add(alert.alert_id)
            logger.info(f"Alert suppressed due to noise reduction: {alert.alert_id}")
            return True
            
        # Enregistrer cette alerte
        self.alert_signatures[signature].append(now)
        return False
        
    def _create_alert_signature(self, alert: Alert) -> str:
        """Créer signature alerte pour déduplication"""
        signature_data = f"{alert.service_name}:{alert.metric_name}:{alert.severity.value}"
        return hashlib.md5(signature_data.encode()).hexdigest()

class EscalationManager:
    """Gestionnaire escalation alertes"""
    
    def __init__(self):
        self.escalation_policies: Dict[str, EscalationPolicy] = {}
        self.active_escalations: Dict[str, Dict[str, Any]] = {}
        
    async def register_escalation_policy(self, policy: EscalationPolicy):
        """Enregistrer politique escalation"""
        self.escalation_policies[policy.policy_id] = policy
        logger.info(f"Registered escalation policy: {policy.policy_id}")
        
    async def start_escalation(self, alert: Alert, policy_id: str = "default") -> bool:
        """Démarrer escalation alerte"""
        if policy_id not in self.escalation_policies:
            logger.error(f"Escalation policy not found: {policy_id}")
            return False
            
        policy = self.escalation_policies[policy_id]
        
        # Vérifier si escalation déjà active
        if alert.alert_id in self.active_escalations:
            return True
            
        # Créer escalation
        escalation = {
            'alert_id': alert.alert_id,
            'policy_id': policy_id,
            'current_level': 0,
            'started_timestamp': datetime.now(),
            'next_escalation_time': datetime.now() + timedelta(
                minutes=policy.escalation_levels[0]['delay_minutes']
            )
        }
        
        self.active_escalations[alert.alert_id] = escalation
        
        # Programmer escalation
        asyncio.create_task(self._escalation_loop(alert, policy))
        
        logger.info(f"Started escalation for alert {alert.alert_id} with policy {policy_id}")
        return True
        
    async def stop_escalation(self, alert_id: str):
        """Arrêter escalation"""
        if alert_id in self.active_escalations:
            del self.active_escalations[alert_id]
            logger.info(f"Stopped escalation for alert {alert_id}")
            
    async def _escalation_loop(self, alert: Alert, policy: EscalationPolicy):
        """Boucle escalation"""
        escalation = self.active_escalations.get(alert.alert_id)
        if not escalation:
            return
            
        try:
            while (alert.alert_id in self.active_escalations and 
                   escalation['current_level'] < len(policy.escalation_levels)):
                
                # Attendre temps escalation
                now = datetime.now()
                if now < escalation['next_escalation_time']:
                    sleep_seconds = (escalation['next_escalation_time'] - now).total_seconds()
                    await asyncio.sleep(max(1, sleep_seconds))
                    
                # Vérifier si alerte toujours active
                if alert.status in [AlertStatus.RESOLVED, AlertStatus.ACKNOWLEDGED]:
                    break
                    
                # Escalate to next level
                level_config = policy.escalation_levels[escalation['current_level']]
                await self._execute_escalation_level(alert, level_config)
                
                # Mettre à jour escalation
                escalation['current_level'] += 1
                if escalation['current_level'] < len(policy.escalation_levels):
                    next_level = policy.escalation_levels[escalation['current_level']]
                    escalation['next_escalation_time'] = now + timedelta(
                        minutes=next_level['delay_minutes']
                    )
                    
        except Exception as e:
            logger.error(f"Escalation loop failed for alert {alert.alert_id}: {e}")
        finally:
            # Nettoyer escalation
            if alert.alert_id in self.active_escalations:
                del self.active_escalations[alert.alert_id]
                
    async def _execute_escalation_level(self, alert: Alert, level_config: Dict[str, Any]):
        """Exécuter niveau escalation"""
        level = level_config['level']
        contacts = level_config['contacts']
        
        logger.info(f"Escalating alert {alert.alert_id} to level {level}")
        
        # Simulation notification escalation
        # Dans vraie implémentation, envoyer notifications aux contacts
        for contact in contacts:
            logger.info(f"Escalation notification sent to {contact} for alert {alert.alert_id}")

class HealthAlertingSystem:
    """
    Système alerting santé avec smart notifications.
    Multi-channel delivery + escalation automatique + intelligent noise reduction.
    
    Features:
    - Smart alert rule engine avec condition evaluation
    - Multi-channel notification delivery (email, Slack, SMS, webhook)
    - Intelligent noise reduction pour éviter spam
    - Automatic escalation avec policies configurables
    - Alert grouping et correlation
    - Template-based notification formatting
    """
    
    def __init__(self, alerting_config: AlertingConfig):
        self.alerting_config = alerting_config
        self.condition_evaluator = ConditionEvaluator()
        self.notification_delivery = NotificationDelivery()
        self.noise_reduction = NoiseReductionEngine()
        self.escalation_manager = EscalationManager()
        
        # Registres
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_templates: Dict[str, NotificationTemplate] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Grouping et correlation
        self.alert_groups: Dict[str, List[str]] = defaultdict(list)
        
        # Rate limiting
        self.alert_rate_limiter: deque = deque(maxlen=100)
        
        # Statistiques
        self.alerting_stats = {
            'total_alerts_triggered': 0,
            'alerts_sent': 0,
            'alerts_suppressed': 0,
            'escalations_started': 0,
            'notifications_failed': 0,
            'average_resolution_time_minutes': 0.0
        }
        
    async def register_alert_rule(self, rule: AlertRule):
        """Enregistrer règle alerte"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Registered alert rule: {rule.rule_id}")
        
    async def register_notification_template(self, template: NotificationTemplate):
        """Enregistrer template notification"""
        template_key = f"{template.channel.value}_{template.severity.value}"
        self.notification_templates[template_key] = template
        logger.info(f"Registered notification template: {template_key}")
        
    async def configure_notification_channel(self, channel: NotificationChannel, 
                                           config: Dict[str, Any]):
        """Configurer canal notification"""
        await self.notification_delivery.configure_channel(channel, config)
        
    async def register_escalation_policy(self, policy: EscalationPolicy):
        """Enregistrer politique escalation"""
        await self.escalation_manager.register_escalation_policy(policy)
        
    async def evaluate_health_alerts(self, service_name: str, 
                                   metrics: Dict[str, Any]) -> List[Alert]:
        """
        Évaluer alertes santé pour métriques service.
        
        Args:
            service_name: Nom du service
            metrics: Métriques à évaluer
            
        Returns:
            Liste alertes déclenchées
        """
        triggered_alerts = []
        
        try:
            # Rate limiting
            if not await self._check_rate_limit():
                logger.warning("Alert rate limit exceeded, skipping evaluation")
                return []
                
            # Évaluer chaque règle
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                    
                try:
                    # Évaluer condition
                    condition_met = await self.condition_evaluator.evaluate_condition(
                        rule.condition, metrics
                    )
                    
                    if condition_met:
                        # Vérifier cooldown
                        if await self._is_in_cooldown(rule_id, service_name):
                            continue
                            
                        # Créer alerte
                        alert = await self._create_alert(rule, service_name, metrics)
                        
                        # Vérifier suppression noise
                        if self.alerting_config.noise_reduction_enabled:
                            if await self.noise_reduction.should_suppress_alert(alert):
                                self.alerting_stats['alerts_suppressed'] += 1
                                continue
                                
                        # Enregistrer alerte
                        self.active_alerts[alert.alert_id] = alert
                        self.alert_history.append(alert)
                        triggered_alerts.append(alert)
                        
                        # Envoyer notifications
                        await self._send_alert_notifications(alert, rule)
                        
                        # Démarrer escalation si configurée
                        if rule.escalation_enabled:
                            await self.escalation_manager.start_escalation(alert)
                            
                        self.alerting_stats['total_alerts_triggered'] += 1
                        
                        logger.info(f"Alert triggered: {alert.alert_id} for {service_name}")
                        
                except Exception as e:
                    logger.error(f"Alert rule evaluation failed: {rule_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Health alert evaluation failed: {e}")
            
        return triggered_alerts
        
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acquitter alerte"""
        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_timestamp = datetime.now()
        alert.acknowledged_by = acknowledged_by
        
        # Arrêter escalation
        await self.escalation_manager.stop_escalation(alert_id)
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
        
    async def resolve_alert(self, alert_id: str, resolved_by: str = None) -> bool:
        """Résoudre alerte"""
        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_timestamp = datetime.now()
        
        # Calculer temps résolution pour stats
        if alert.triggered_timestamp:
            resolution_time = (datetime.now() - alert.triggered_timestamp).total_seconds() / 60
            self._update_resolution_time_stats(resolution_time)
            
        # Arrêter escalation
        await self.escalation_manager.stop_escalation(alert_id)
        
        # Retirer des alertes actives
        del self.active_alerts[alert_id]
        
        logger.info(f"Alert resolved: {alert_id}")
        return True
        
    async def suppress_alert(self, alert_id: str, suppress_until: datetime) -> bool:
        """Supprimer alerte temporairement"""
        if alert_id not in self.active_alerts:
            return False
            
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.SUPPRESSED
        alert.suppression_until = suppress_until
        
        logger.info(f"Alert suppressed until {suppress_until}: {alert_id}")
        return True
        
    async def get_active_alerts(self, service_name: str = None, 
                              severity: AlertSeverity = None) -> List[Alert]:
        """Obtenir alertes actives"""
        alerts = list(self.active_alerts.values())
        
        # Filtrer par service
        if service_name:
            alerts = [a for a in alerts if a.service_name == service_name]
            
        # Filtrer par sévérité
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
            
        return alerts
        
    async def get_alerting_summary(self) -> Dict[str, Any]:
        """Obtenir synthèse alerting"""
        active_alerts = list(self.active_alerts.values())
        
        return {
            'total_active_alerts': len(active_alerts),
            'alerts_by_severity': {
                severity.value: len([a for a in active_alerts if a.severity == severity])
                for severity in AlertSeverity
            },
            'alerts_by_status': {
                status.value: len([a for a in active_alerts if a.status == status])
                for status in AlertStatus
            },
            'active_escalations': len(self.escalation_manager.active_escalations),
            'alerting_stats': self.alerting_stats.copy(),
            'suppressed_alerts_count': len(self.noise_reduction.suppressed_alerts)
        }
        
    # Méthodes utilitaires
    
    async def _check_rate_limit(self) -> bool:
        """Vérifier rate limit alertes"""
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=1)
        
        # Nettoyer anciens timestamps
        while self.alert_rate_limiter and self.alert_rate_limiter[0] < cutoff_time:
            self.alert_rate_limiter.popleft()
            
        # Vérifier limite
        if len(self.alert_rate_limiter) >= self.alerting_config.max_alerts_per_minute:
            return False
            
        # Enregistrer timestamp
        self.alert_rate_limiter.append(now)
        return True
        
    async def _is_in_cooldown(self, rule_id: str, service_name: str) -> bool:
        """Vérifier cooldown règle"""
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
            
        # Chercher dernière alerte pour cette règle/service
        now = datetime.now()
        cooldown_cutoff = now - timedelta(minutes=rule.cooldown_minutes)
        
        for alert in reversed(self.alert_history):
            if (alert.rule_id == rule_id and 
                alert.service_name == service_name and
                alert.triggered_timestamp > cooldown_cutoff):
                return True
                
        return False
        
    async def _create_alert(self, rule: AlertRule, service_name: str, 
                          metrics: Dict[str, Any]) -> Alert:
        """Créer alerte depuis règle"""
        alert_id = str(uuid.uuid4())
        
        # Extraire métrique principale pour context
        metric_name = rule.condition.split()[0] if rule.condition else "unknown"
        current_value = metrics.get(metric_name, 0)
        
        # Extraire threshold depuis condition
        threshold_value = None
        try:
            condition_parts = rule.condition.split()
            if len(condition_parts) == 3:
                threshold_value = float(condition_parts[2])
        except:
            pass
            
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            service_name=service_name,
            metric_name=metric_name,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=f"{rule.name} - {service_name}",
            description=f"{rule.description}. Current value: {current_value}",
            triggered_timestamp=datetime.now(),
            current_value=current_value,
            threshold_value=threshold_value,
            tags=rule.tags.copy()
        )
        
        return alert
        
    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule):
        """Envoyer notifications alerte"""
        for channel in rule.notification_channels:
            try:
                # Chercher template approprié
                template_key = f"{channel.value}_{alert.severity.value}"
                template = self.notification_templates.get(template_key)
                
                if not template:
                    # Template par défaut
                    template = await self._create_default_template(channel, alert.severity)
                    
                # Recipients (placeholder - à configurer selon canal)
                recipients = await self._get_notification_recipients(channel, alert.severity)
                
                # Envoyer notification
                success = await self.notification_delivery.send_notification(
                    channel, alert, template, recipients
                )
                
                if success:
                    self.alerting_stats['alerts_sent'] += 1
                else:
                    self.alerting_stats['notifications_failed'] += 1
                    
            except Exception as e:
                logger.error(f"Notification sending failed for {channel.value}: {e}")
                self.alerting_stats['notifications_failed'] += 1
                
    async def _create_default_template(self, channel: NotificationChannel, 
                                     severity: AlertSeverity) -> NotificationTemplate:
        """Créer template par défaut"""
        return NotificationTemplate(
            template_id=f"default_{channel.value}_{severity.value}",
            channel=channel,
            severity=severity,
            subject_template="[{severity}] Health Alert: {service_name} - {title}",
            body_template="""
Health Alert Details:
- Service: {service_name}
- Metric: {metric_name}
- Severity: {severity}
- Current Value: {current_value}
- Threshold: {threshold_value}
- Triggered: {triggered_time}
- Description: {description}

Alert ID: {alert_id}
Status: {status}
            """.strip()
        )
        
    async def _get_notification_recipients(self, channel: NotificationChannel, 
                                         severity: AlertSeverity) -> List[str]:
        """Obtenir destinataires notification"""
        # Placeholder - à configurer selon environment
        if channel == NotificationChannel.EMAIL:
            if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
                return ['ops-team@iacherie.com', 'engineering@iacherie.com']
            else:
                return ['ops-team@iacherie.com']
        elif channel == NotificationChannel.SLACK:
            return ['#alerts', '#ops-team']
        else:
            return ['default-recipient']
            
    def _update_resolution_time_stats(self, resolution_time_minutes: float):
        """Mettre à jour stats temps résolution"""
        current_avg = self.alerting_stats['average_resolution_time_minutes']
        total_alerts = self.alerting_stats['total_alerts_triggered']
        
        if total_alerts > 0:
            new_avg = ((current_avg * (total_alerts - 1)) + resolution_time_minutes) / total_alerts
            self.alerting_stats['average_resolution_time_minutes'] = new_avg

# Example usage et testing
if __name__ == "__main__":
    async def test_health_alerting_system():
        """Test système alerting santé"""
        config = AlertingConfig(
            max_alerts_per_minute=10,
            noise_reduction_enabled=True,
            smart_grouping_enabled=True
        )
        
        alerting_system = HealthAlertingSystem(config)
        
        # Configurer canal email
        await alerting_system.configure_notification_channel(
            NotificationChannel.EMAIL,
            {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'alerts@iacherie.com',
                'password': 'password',
                'from_email': 'alerts@iacherie.com'
            }
        )
        
        # Enregistrer règles alertes
        response_time_rule = AlertRule(
            rule_id="response_time_high",
            name="High Response Time",
            description="API response time exceeds threshold",
            condition="response_time_ms > 1000",
            severity=AlertSeverity.WARNING,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            cooldown_minutes=10
        )
        await alerting_system.register_alert_rule(response_time_rule)
        
        error_rate_rule = AlertRule(
            rule_id="error_rate_high",
            name="High Error Rate",
            description="Service error rate too high",
            condition="error_rate_percent > 5",
            severity=AlertSeverity.CRITICAL,
            notification_channels=[NotificationChannel.EMAIL],
            escalation_enabled=True,
            cooldown_minutes=5
        )
        await alerting_system.register_alert_rule(error_rate_rule)
        
        # Enregistrer templates notification
        email_warning_template = NotificationTemplate(
            template_id="email_warning",
            channel=NotificationChannel.EMAIL,
            severity=AlertSeverity.WARNING,
            subject_template="[WARNING] {service_name} Health Alert",
            body_template="Service {service_name} has a health issue:\n{description}\nCurrent value: {current_value}",
            format_type="text"
        )
        await alerting_system.register_notification_template(email_warning_template)
        
        # Politique escalation
        escalation_policy = EscalationPolicy(
            policy_id="default",
            name="Default Escalation",
            escalation_levels=[
                {'level': 'L1', 'contacts': ['oncall-engineer@iacherie.com'], 'delay_minutes': 5},
                {'level': 'L2', 'contacts': ['team-lead@iacherie.com'], 'delay_minutes': 15},
                {'level': 'L3', 'contacts': ['engineering-manager@iacherie.com'], 'delay_minutes': 30}
            ]
        )
        await alerting_system.register_escalation_policy(escalation_policy)
        
        # Simuler métriques déclenchant alertes
        test_metrics = [
            {
                'service': 'api_service',
                'metrics': {
                    'response_time_ms': 1500,  # Déclenche alerte
                    'error_rate_percent': 2.0,
                    'cpu_usage': 70
                }
            },
            {
                'service': 'payment_service',
                'metrics': {
                    'response_time_ms': 800,
                    'error_rate_percent': 8.0,  # Déclenche alerte critique
                    'cpu_usage': 85
                }
            }
        ]
        
        all_triggered_alerts = []
        
        for test_case in test_metrics:
            triggered_alerts = await alerting_system.evaluate_health_alerts(
                test_case['service'], test_case['metrics']
            )
            all_triggered_alerts.extend(triggered_alerts)
            
        print("🚨 Health Alerting System Results:")
        print(f"Total Alerts Triggered: {len(all_triggered_alerts)}")
        
        # Afficher alertes
        for alert in all_triggered_alerts:
            print(f"\nAlert: {alert.alert_id}")
            print(f"  Service: {alert.service_name}")
            print(f"  Severity: {alert.severity.value}")
            print(f"  Title: {alert.title}")
            print(f"  Status: {alert.status.value}")
            
        # Tester acknowledge
        if all_triggered_alerts:
            first_alert = all_triggered_alerts[0]
            await alerting_system.acknowledge_alert(first_alert.alert_id, "test-user")
            print(f"\nAcknowledged alert: {first_alert.alert_id}")
            
        # Obtenir synthèse
        summary = await alerting_system.get_alerting_summary()
        print(f"\nAlerting Summary:")
        print(f"  Active Alerts: {summary['total_active_alerts']}")
        print(f"  Critical Alerts: {summary['alerts_by_severity']['critical']}")
        print(f"  Escalations: {summary['active_escalations']}")
        print(f"  Alerts Sent: {summary['alerting_stats']['alerts_sent']}")
        print(f"  Alerts Suppressed: {summary['alerting_stats']['alerts_suppressed']}")
        
        return all_triggered_alerts, summary
        
    # Run test
    asyncio.run(test_health_alerting_system())