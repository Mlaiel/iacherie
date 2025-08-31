"""🚀 Billing Alerts System - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/platform_core/billing/billing_alerts.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 SYSTÈME D'ALERTES BILLING INTELLIGENT
Monitoring et alertes automatiques pour la facturation
- Détection anomalies et fraudes en temps réel
- Alertes échéances et impayés automatiques
- Monitoring revenus et seuils critiques
- Notifications multi-canaux et escalation
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

# Configuration
logger = logging.getLogger(__name__)

class AlertType(Enum):
    """Types d'alertes"""    PAYMENT_FAILED = "payment_failed"
    INVOICE_OVERDUE = "invoice_overdue"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    FRAUD_DETECTED = "fraud_detected"
    CHARGEBACK_RECEIVED = "chargeback_received"
    REVENUE_DROP = "revenue_drop"
    HIGH_REFUND_RATE = "high_refund_rate"
    PAYMENT_METHOD_EXPIRED = "payment_method_expired"
    DUNNING_TRIGGER = "dunning_trigger"
    CREDIT_LIMIT_EXCEEDED = "credit_limit_exceeded"

class AlertSeverity(Enum):
    """Niveaux de sévérité"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """États des alertes"""    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"

class NotificationChannel(Enum):
    """Canaux de notification"""    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    PUSH = "push"

@dataclass
class AlertRule:
    """Règle d'alerte"""    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Type et sévérité
    alert_type: AlertType = AlertType.PAYMENT_FAILED
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Conditions de déclenchement
    conditions: Dict[str, Any] = field(default_factory=dict)
    threshold_value: Optional[Decimal] = None
    threshold_period_hours: int = 24
    
    # Configuration des notifications
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    recipients: List[str] = field(default_factory=list)
    
    # Timing et récurrence
    cooldown_minutes: int = 60  # Éviter les spams
    max_alerts_per_day: int = 10
    
    # État
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    trigger_count_today: int = 0

@dataclass
class BillingAlert:
    """Alerte de facturation"""    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    
    # Classification
    alert_type: AlertType = AlertType.PAYMENT_FAILED
    severity: AlertSeverity = AlertSeverity.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    
    # Contenu
    title: str = ""
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Entités concernées
    customer_id: Optional[str] = None
    invoice_id: Optional[str] = None
    subscription_id: Optional[str] = None
    payment_id: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Actions
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'alerte en dictionnaire"""        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "customer_id": self.customer_id,
            "invoice_id": self.invoice_id,
            "subscription_id": self.subscription_id,
            "payment_id": self.payment_id,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_by": self.resolved_by,
            "actions_taken": self.actions_taken
        }

class BillingAlerts:
    """Système d'alertes de facturation"""    
    def __init__(self, database_client: Optional[Any] = None):
        self.database_client = database_client
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, BillingAlert] = {}
        self.handlers: Dict[AlertType, List[Callable]] = {}
        
        # Monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Charger les règles par défaut
        self._load_default_rules()
        
    def _load_default_rules(self):
        """Charge les règles d'alerte par défaut"""        
        # Échec de paiement
        self.add_rule(AlertRule(
            name="Échec de paiement",
            description="Alerte quand un paiement échoue",
            alert_type=AlertType.PAYMENT_FAILED,
            severity=AlertSeverity.HIGH,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            recipients=["billing@company.com", "support@company.com"]
        ))
        
        # Facture en retard
        self.add_rule(AlertRule(
            name="Facture en retard",
            description="Alerte pour les factures impayées depuis plus de 7 jours",
            alert_type=AlertType.INVOICE_OVERDUE,
            severity=AlertSeverity.MEDIUM,
            conditions={"overdue_days": 7},
            notification_channels=[NotificationChannel.EMAIL],
            recipients=["accounts@company.com"]
        ))
        
        # Détection de fraude
        self.add_rule(AlertRule(
            name="Fraude détectée",
            description="Alerte pour activité suspecte",
            alert_type=AlertType.FRAUD_DETECTED,
            severity=AlertSeverity.CRITICAL,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            recipients=["security@company.com", "management@company.com"],
            cooldown_minutes=5  # Plus court pour la sécurité
        ))
        
        # Baisse de revenus
        self.add_rule(AlertRule(
            name="Baisse de revenus significative",
            description="Alerte quand les revenus chutent de plus de 20%",
            alert_type=AlertType.REVENUE_DROP,
            severity=AlertSeverity.HIGH,
            threshold_value=Decimal("20.0"),  # 20%
            threshold_period_hours=24,
            notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
            recipients=["finance@company.com", "ceo@company.com"]
        ))
        
        # Taux de remboursement élevé
        self.add_rule(AlertRule(
            name="Taux de remboursement élevé",
            description="Alerte quand le taux de remboursement dépasse 5%",
            alert_type=AlertType.HIGH_REFUND_RATE,
            severity=AlertSeverity.MEDIUM,
            threshold_value=Decimal("5.0"),  # 5%
            threshold_period_hours=24,
            notification_channels=[NotificationChannel.EMAIL],
            recipients=["quality@company.com", "billing@company.com"]
        ))
        
    async def start_monitoring(self):
        """Démarre le monitoring automatique"""        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoring des alertes de facturation démarré")
        
    async def stop_monitoring(self):
        """Arrête le monitoring"""        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Monitoring des alertes arrêté")
        
    def add_rule(self, rule: AlertRule):
        """Ajoute une règle d'alerte"""        self.rules[rule.rule_id] = rule
        logger.debug(f"Règle d'alerte ajoutée: {rule.name}")
        
    def remove_rule(self, rule_id: str):
        """Supprime une règle d'alerte"""        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.debug(f"Règle d'alerte supprimée: {rule_id}")
            
    async def trigger_alert(self,
                          alert_type: AlertType,
                          title: str,
                          message: str,
                          severity: AlertSeverity = AlertSeverity.MEDIUM,
                          **kwargs) -> Optional[BillingAlert]:
        """Déclenche une alerte"""        
        # Trouver une règle correspondante
        matching_rule = None
        for rule in self.rules.values():
            if rule.alert_type == alert_type and rule.is_active:
                matching_rule = rule
                break
                
        if not matching_rule:
            logger.debug(f"Aucune règle active trouvée pour {alert_type.value}")
            return None
            
        # Vérifier le cooldown
        if (matching_rule.last_triggered and 
            datetime.utcnow() - matching_rule.last_triggered < timedelta(minutes=matching_rule.cooldown_minutes)):
            logger.debug(f"Alerte {alert_type.value} en cooldown")
            return None
            
        # Vérifier le limite quotidienne
        if matching_rule.trigger_count_today >= matching_rule.max_alerts_per_day:
            logger.debug(f"Limite quotidienne atteinte pour {alert_type.value}")
            return None
            
        # Créer l'alerte
        alert = BillingAlert(
            rule_id=matching_rule.rule_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            **kwargs
        )
        
        # Enregistrer l'alerte
        self.alerts[alert.alert_id] = alert
        
        # Mettre à jour la règle
        matching_rule.last_triggered = datetime.utcnow()
        matching_rule.trigger_count_today += 1
        
        # Envoyer les notifications
        await self._send_notifications(alert, matching_rule)
        
        # Exécuter les handlers personnalisés
        if alert_type in self.handlers:
            for handler in self.handlers[alert_type]:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Erreur dans handler pour {alert_type.value}: {e}")
                    
        # Sauvegarder
        if self.database_client:
            await self._save_alert(alert)
            
        logger.info(f"Alerte déclenchée: {title} ({alert.alert_id})")
        return alert
        
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Accuse réception d'une alerte"""        alert = self.alerts.get(alert_id)
        if not alert or alert.status != AlertStatus.ACTIVE:
            return False
            
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        if self.database_client:
            await self._save_alert(alert)
            
        logger.info(f"Alerte accusée réception: {alert_id} par {acknowledged_by}")
        return True
        
    async def resolve_alert(self,
                          alert_id: str,
                          resolved_by: str,
                          actions_taken: Optional[List[str]] = None) -> bool:
        """Résout une alerte"""        alert = self.alerts.get(alert_id)
        if not alert:
            return False
            
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        
        if actions_taken:
            alert.actions_taken.extend(actions_taken)
            
        if self.database_client:
            await self._save_alert(alert)
            
        logger.info(f"Alerte résolue: {alert_id} par {resolved_by}")
        return True
        
    async def get_active_alerts(self, 
                              severity_filter: Optional[AlertSeverity] = None,
                              type_filter: Optional[AlertType] = None) -> List[BillingAlert]:
        """Récupère les alertes actives"""        alerts = []
        
        for alert in self.alerts.values():
            if alert.status != AlertStatus.ACTIVE:
                continue
                
            if severity_filter and alert.severity != severity_filter:
                continue
                
            if type_filter and alert.alert_type != type_filter:
                continue
                
            alerts.append(alert)
            
        # Trier par sévérité puis par date
        severity_order = {
            AlertSeverity.CRITICAL: 4,
            AlertSeverity.HIGH: 3,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.LOW: 1
        }
        
        alerts.sort(key=lambda a: (severity_order[a.severity], a.created_at), reverse=True)
        return alerts
        
    def add_handler(self, alert_type: AlertType, handler: Callable):
        """Ajoute un handler personnalisé pour un type d'alerte"""        if alert_type not in self.handlers:
            self.handlers[alert_type] = []
        self.handlers[alert_type].append(handler)
        
    async def _monitoring_loop(self):
        """Boucle de monitoring automatique"""        while self._running:
            try:
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                await self._check_automated_alerts()
                await self._reset_daily_counters()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans la boucle de monitoring: {e}")
                
    async def _check_automated_alerts(self):
        """Vérifie les conditions d'alerte automatiques"""        
        # Vérifier les factures en retard
        await self._check_overdue_invoices()
        
        # Vérifier les méthodes de paiement expirées
        await self._check_expired_payment_methods()
        
        # Vérifier les anomalies de revenus
        await self._check_revenue_anomalies()
        
        # Vérifier le taux de remboursements
        await self._check_refund_rate()
        
    async def _check_overdue_invoices(self):
        """Vérifie les factures en retard"""        # Dans un vrai système, on interrogerait la base de données
        # pour trouver les factures en retard
        
        # Simulation
        overdue_invoices = []  # Résultats de requête DB
        
        for invoice in overdue_invoices:
            await self.trigger_alert(
                alert_type=AlertType.INVOICE_OVERDUE,
                title=f"Facture en retard: {invoice.get('invoice_number')}",
                message=f"La facture {invoice.get('invoice_number')} est en retard de {invoice.get('days_overdue')} jours",
                severity=AlertSeverity.MEDIUM,
                customer_id=invoice.get('customer_id'),
                invoice_id=invoice.get('invoice_id'),
                details={"days_overdue": invoice.get('days_overdue'), "amount": invoice.get('amount')}
            )
            
    async def _check_expired_payment_methods(self):
        """Vérifie les méthodes de paiement expirées"""        # Check for payment methods expiring in the next 30 days
        try:
            expiry_threshold = datetime.utcnow() + timedelta(days=30)
            # In a real system, this would query the database
            # For now, simulate finding expired payment methods
            expired_methods = []  # Would be filled from database query
            
            for method in expired_methods:
                await self._create_alert(
                    AlertType.PAYMENT_METHOD_EXPIRED,
                    AlertSeverity.MEDIUM,
                    f"Payment method {method['id']} expiring soon",
                    {"payment_method_id": method['id'], "user_id": method['user_id']}
                )
            logger.debug(f"Checked for expired payment methods: {len(expired_methods)} found")
        except Exception as e:
            logger.error(f"Error checking expired payment methods: {e}")
        
    async def _check_revenue_anomalies(self):
        """Vérifie les anomalies de revenus"""        # Compare current revenue with previous period
        try:
            current_date = datetime.utcnow()
            # In a real system, this would query revenue data from database
            current_revenue = Decimal("10000")  # Simulated current revenue
            previous_revenue = Decimal("12000")  # Simulated previous period revenue
            
            revenue_drop_threshold = Decimal("0.20")  # 20% drop threshold
            if previous_revenue > 0:
                drop_percentage = (previous_revenue - current_revenue) / previous_revenue
                
                if drop_percentage > revenue_drop_threshold:
                    await self._create_alert(
                        AlertType.REVENUE_DROP,
                        AlertSeverity.HIGH,
                        f"Revenue dropped by {drop_percentage:.1%} from previous period",
                        {
                            "current_revenue": float(current_revenue),
                            "previous_revenue": float(previous_revenue),
                            "drop_percentage": float(drop_percentage)
                        }
                    )
            logger.debug(f"Revenue anomaly check completed")
        except Exception as e:
            logger.error(f"Error checking revenue anomalies: {e}")
        
    async def _check_refund_rate(self):
        """Vérifie le taux de remboursements"""        # Calculate refund rate for the current period
        try:
            # In a real system, this would query refund data from database
            total_transactions = 1000  # Simulated
            total_refunds = 50  # Simulated
            
            if total_transactions > 0:
                refund_rate = total_refunds / total_transactions
                refund_threshold = 0.05  # 5% threshold
                
                if refund_rate > refund_threshold:
                    await self._create_alert(
                        AlertType.HIGH_REFUND_RATE,
                        AlertSeverity.HIGH,
                        f"Refund rate is {refund_rate:.1%}, above threshold of {refund_threshold:.1%}",
                        {
                            "refund_rate": refund_rate,
                            "total_transactions": total_transactions,
                            "total_refunds": total_refunds,
                            "threshold": refund_threshold
                        }
                    )
            logger.debug(f"Refund rate check completed")
        except Exception as e:
            logger.error(f"Error checking refund rate: {e}")
        
    async def _reset_daily_counters(self):
        """Remet à zéro les compteurs quotidiens"""        now = datetime.utcnow()
        
        for rule in self.rules.values():
            if (rule.last_triggered and 
                rule.last_triggered.date() < now.date()):
                rule.trigger_count_today = 0
                
    async def _send_notifications(self, alert: BillingAlert, rule: AlertRule):
        """Envoie les notifications pour une alerte"""        
        for channel in rule.notification_channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(alert, rule.recipients)
                elif channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(alert)
                elif channel == NotificationChannel.SMS:
                    await self._send_sms_notification(alert, rule.recipients)
                elif channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(alert)
                elif channel == NotificationChannel.IN_APP:
                    await self._send_in_app_notification(alert)
                    
            except Exception as e:
                logger.error(f"Erreur envoi notification {channel.value}: {e}")
                
    async def _send_email_notification(self, alert: BillingAlert, recipients: List[str]):
        """Envoie une notification par email"""        # Implémentation avec service d'email
        logger.info(f"Email envoyé pour alerte {alert.alert_id} à {recipients}")
        
    async def _send_slack_notification(self, alert: BillingAlert):
        """Envoie une notification Slack"""        # Implémentation avec API Slack
        logger.info(f"Notification Slack envoyée pour alerte {alert.alert_id}")
        
    async def _send_sms_notification(self, alert: BillingAlert, recipients: List[str]):
        """Envoie une notification SMS"""        # Implémentation avec service SMS
        logger.info(f"SMS envoyé pour alerte {alert.alert_id}")
        
    async def _send_webhook_notification(self, alert: BillingAlert):
        """Envoie une notification webhook"""        # Implémentation avec requête HTTP
        logger.info(f"Webhook envoyé pour alerte {alert.alert_id}")
        
    async def _send_in_app_notification(self, alert: BillingAlert):
        """Envoie une notification in-app"""        # Implémentation avec système de notifications interne
        logger.info(f"Notification in-app créée pour alerte {alert.alert_id}")
        
    async def _save_alert(self, alert: BillingAlert):
        """Sauvegarde une alerte en base"""        try:
            # In a real system, this would save to database
            # For now, just log the alert data
            alert_data = {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "description": alert.description,
                "status": alert.status.value,
                "created_at": alert.created_at.isoformat(),
                "metadata": alert.metadata
            }
            
            # Simulate database save
            logger.info(f"Alert saved to database: {alert.alert_id}")
            logger.debug(f"Alert data: {json.dumps(alert_data, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error saving alert to database: {e}")
        
    def get_alert_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des alertes"""        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE])
        
        alerts_by_type = {}
        for alert_type in AlertType:
            count = len([a for a in self.alerts.values() if a.alert_type == alert_type])
            alerts_by_type[alert_type.value] = count
            
        alerts_by_severity = {}
        for severity in AlertSeverity:
            count = len([a for a in self.alerts.values() if a.severity == severity])
            alerts_by_severity[severity.value] = count
            
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.is_active]),
            "alerts_by_type": alerts_by_type,
            "alerts_by_severity": alerts_by_severity,
            "monitoring_active": self._running
        }

class AlertManager:
    """Gestionnaire principal des alertes"""    
    def __init__(self, billing_alerts: BillingAlerts):
        self.billing_alerts = billing_alerts
        
    async def process_payment_failure(self, payment_data: Dict[str, Any]):
        """Traite un échec de paiement"""        await self.billing_alerts.trigger_alert(
            alert_type=AlertType.PAYMENT_FAILED,
            title=f"Échec de paiement",
            message=f"Le paiement {payment_data.get('payment_id')} a échoué",
            severity=AlertSeverity.HIGH,
            customer_id=payment_data.get('customer_id'),
            payment_id=payment_data.get('payment_id'),
            details=payment_data
        )
        
    async def process_chargeback(self, chargeback_data: Dict[str, Any]):
        """Traite une contestation"""        await self.billing_alerts.trigger_alert(
            alert_type=AlertType.CHARGEBACK_RECEIVED,
            title=f"Contestation reçue",
            message=f"Contestation sur le paiement {chargeback_data.get('payment_id')}",
            severity=AlertSeverity.CRITICAL,
            customer_id=chargeback_data.get('customer_id'),
            payment_id=chargeback_data.get('payment_id'),
            details=chargeback_data
        )
        
    async def process_fraud_detection(self, fraud_data: Dict[str, Any]):
        """Traite une détection de fraude"""        await self.billing_alerts.trigger_alert(
            alert_type=AlertType.FRAUD_DETECTED,
            title=f"Fraude détectée",
            message=f"Activité suspecte détectée pour le client {fraud_data.get('customer_id')}",
            severity=AlertSeverity.CRITICAL,
            customer_id=fraud_data.get('customer_id'),
            details=fraud_data
        )